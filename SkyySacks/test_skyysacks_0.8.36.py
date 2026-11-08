"""Harness for SkyySacks 0.8.36 (round sk836 - tools/sacks_0_8_36_patch.py: Enchanted metals in the Smithing bag, Sell on the Pocket page, real names on the page;
Skyy 2026-11-08 "enchanted metals should go in the smithing bag too." + "add a sell button in here too,").
Build first:
    python tools/sacks_0_8_36_patch.py && python SkyySacks/build_skyysacks_0.8.36.py

    python SkyySacks/test_skyysacks_0.8.36.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A / C   verify (-Xverify:all) + compare 0.8.35 -> 0.8.36 (only what the patch touches), engine-access audit
  S36     on the 0.8.9 Void stand-ins:
          CAT     homeOf / catOf / sacks:fn:catOf for all 18 moved ids, every other Enchanted row beside its base, Charcoal
          MOVE    held stock in a pool file: read twice (a restart between), an over-space stock, an offline profile, no byte written, level totals unchanged
          COMPACT the compactor (one bag now, over space too), Unpack, sacks:fn:takeOpen, the bag's stored counts
          SELL    every path of SacksPage.sell through onEvent with a fake bazaar:fn:sell: pays (Long, long[]), 0, throws, absent, no price, part, odd answers, amount box, two clicks,
                  a profile change, a paused Void, fish, debit before pay, crafts.log
          NAME    the title, +Took, +Put with a stand-in I18nModule; no translation = the tidied id
          PAGE    render: the Sell button, its binding, the third row with / without Unpack, the price line
  ALL35   the 0.8.35 Furnace-All cases on THIS jar (regression)
  BC36    bytecode: sell debits before it calls the Function
  D       start twice on a scratch COPY of NewBetaTest's Skyy_SkyySacks: no migration, no byte changed
NOT COVERED (UNVERIFIED in game): how the client draws the third row; the real SkyyBazaar 0.2.4 (only its contract, through the fake).
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyench as EN

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_35", os.path.join(HERE, "test_skyysacks_0.8.35.py"))
T35 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T35)
sys.argv = _argv
HK.run_compare = _RC
T089, T30, BETA = T35.T089, T35.T30, T35.BETA

VERSION = "0.8.36"
OLD_VERSION = "0.8.35"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
T30.OLD_JAR = OLD_JAR
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sk836", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {"SkyySacksPlugin": ["~m setup"], "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],
          "SackDefs": ["~m enchCat"],
          "SacksPage": ["+m sell", "+m sellDebit", "+m sellDebit0", "+m sellHint", "+m sellOpen", "+m sellPrice", "~m onEvent", "~m pretty", "~m render", "~m unpack"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
METALS = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Silver", "Gold", "Mithril", "Lead", "Chromium", "Slag", "Titanium",
          "Bronze", "Dusk", "Azurvane", "Cinder", "Lumen", "Electrum"]
METAL_IDS = [EN.PREFIX + m for m in METALS]
LEAD, IRON_E, IRON_B, COB_E = "Skyy_Ench_Lead", "Skyy_Ench_Iron", "Ingredient_Bar_Iron", "Skyy_Ench_Cobblestone"
MAX = 9223372036854775807


def cases36(K, L, scratch):
    from jpype import JClass, JString, JArray, JLong, JImplements, JOverride
    VS, Defs, Pool, Swp, SPage = L["VS"], L["Defs"], L["Pool"], L["Swp"], L["SPage"]
    fresh, write_pool, player, pc, inv_counts, custom_item, drain, restart, coll, nocoll = (L[n] for n in ("fresh", "write_pool", "player", "pc", "inv_counts", "custom_item", "drain", "restart", "coll", "nocoll"))
    UUID, bridge, us, jfield, jp, pref, TPlayers, Bridge = (L[n] for n in ("UUID", "bridge", "us", "jfield", "jp", "pref", "TPlayers", "Bridge"))
    J = lambda n: JClass(PKG + n)
    VC, Fn, Cfg, CLog = J("VoidCompact"), J("SackFn"), J("SackCfg"), J("CraftLog")
    UCBc, UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Long_ = JClass("java.lang.Long")
    cats = [str(c) for c in Defs.CATS]
    MI, SM = cats.index("Mining"), cats.index("Smithing")
    base = os.path.join(scratch, "s36")
    pools = os.path.join(base, "pools")
    U = UUID.fromString("00000000-0000-0000-0000-0000000f0836")
    k = str(U)
    OFF = "00000000-0000-0000-0000-0000000f0837"

    def home(i):
        h = Defs.homeOf(JString(i))
        return None if h is None else str(h)

    def rd(i, key=k):
        return int(Pool.get(JString(key), JString(i)))

    def used(key=k):
        return [int(x) for x in VS.usedAll(JString(key))]

    def mk(vals, key=k):
        drain()
        fresh(base)
        write_pool(pools, key, vals)
        VS.st(key).first = 1

    def fbytes(key=k):
        with open(os.path.join(pools, key + ".properties"), "rb") as f:
            return f.read()

    # ================================================= CAT
    catfn = Fn(13)
    wrong = [i for i in METAL_IDS if home(i) != "Smithing" or str(Defs.catOf(JString(i))) != "Smithing" or str(catfn.apply(JString(i))) != "Smithing"]
    K.check(len(METAL_IDS) == 18 and not wrong, "CAT homeOf, catOf and sacks:fn:catOf: all 18 Enchanted metals answer Smithing (wrong: %s)" % wrong)
    table = list(EN.TABLE) + list(EN.TABLE_ALLOYS)
    off = [(t[0], home(EN.PREFIX + t[0]), home(t[2])) for t in table if t[1] == "I" and home(t[2]) is not None and home(EN.PREFIX + t[0]) != home(t[2])]
    K.check(not off, "CAT every other Enchanted item row sits in its base's bag (%d rows, off: %s)" % (len(table), off))
    rt = dict((t[0], home(EN.PREFIX + t[0])) for t in table if t[1] == "R")
    K.check(rt == {"Rubble": "Mining", "Sand": "Mining", "Crystal": "Mining"}, "CAT the three resource-type rows stay Mining (their bases are Mining items): %s" % rt)
    K.eq([home("Skyy_Ench_Charcoal"), home("Ingredient_Charcoal"), home(COB_E), home("Skyy_Ench_Maple"), home("Skyy_Ench_Bone"), home("Skyy_Ench_HideLight"), home("Skyy_Ench_Nothing"), home(IRON_B)],
         ["Smithing", "Smithing", "Mining", "Foraging", "Combat", "Smithing", None, "Smithing"], "CAT Charcoal + the non-metals unchanged; an unknown Skyy_Ench_ id has no bag; plain bars Smithing")
    for i_ in METAL_IDS + [IRON_B, COB_E, "Ore_Copper"]:
        custom_item(i_, 100)

    # ================================================= MOVE (no migration: the pool is one map; proven on real files)
    stock = {LEAD: 16, IRON_E: 5, COB_E: 4, "Ore_Copper": 50}
    mk(stock)
    coll(U, dict((c_, 0) for c_ in cats))
    b0 = fbytes()
    u0 = used()
    K.check(u0[SM] == 21 and u0[MI] == 54, "MOVE a pool written by 0.8.35 (16 Lead + 5 Iron Enchanted, 4 Enchanted Cobble, 50 ore): Smithing 21, Mining 54: %s" % u0)
    t0 = (int(VS.total(U, JString(k), MI)), int(VS.total(U, JString(k), SM)))
    for s_ in (1, 2):
        restart()
        K.eq(used(), u0, "MOVE start %d: same counts after a restart (once, by construction)" % s_)
        K.eq([rd(LEAD), rd(IRON_E)], [16, 5], "MOVE start %d: every item still held" % s_)
        K.check(fbytes() == b0, "MOVE start %d: not a byte of the pool file written" % s_)
    K.eq((int(VS.total(U, JString(k), MI)), int(VS.total(U, JString(k), SM))), t0, "MOVE bag level totals unchanged (no double count)")
    # the level total without SkyyCollections (own.<Cat>, intake only): reading the move adds nothing
    nocoll()
    own0 = [int(x) for x in VS.st(k).own]
    restart()
    used()
    K.eq([int(x) for x in VS.st(k).own], own0, "MOVE own.<Cat> (no SkyyCollections): unchanged by the move")
    coll(U, dict((c_, 0) for c_ in cats))
    # an offline profile: only its file exists, nobody plays it
    write_pool(pools, OFF, {LEAD: 7})
    off0 = fbytes(OFF)
    restart()
    K.check(used(OFF)[SM] == 7 and used(OFF)[MI] == 0 and fbytes(OFF) == off0, "MOVE an offline profile's file: 7 Lead show in Smithing, the file untouched: %s" % used(OFF))
    # more stock than Smithing's space: held, never trimmed; only new items wait
    lvl_cap = int(VS.capOf(1, 0))
    over = lvl_cap + 500
    mk({LEAD: over, "Ore_Copper": 10})
    coll(U, dict((c_, 0) for c_ in cats))
    cap_sm = int(VS.capsK(U, JString(k)).get(JString("Smithing")))
    K.check(over > cap_sm and used()[SM] == over, "MOVE over space: %d Lead in a Smithing bag of %d" % (over, cap_sm))
    for s_ in (1, 2):
        restart()
        K.eq(rd(LEAD), over, "MOVE over space, start %d: nothing lost or trimmed" % s_)
    pO = player(storage=[(IRON_B, 50)])
    r_ = int(VS.depositInv(pO, U, JString(k), JString(IRON_B), JLong(50)))
    K.check(r_ == -2 and rd(IRON_B) == 0 and inv_counts(pO).get(IRON_B) == 50, "MOVE over space: a new deposit waits (the usual 'category is full'), the bars stay on the player: %d" % r_)
    got = int(SPage.withdrawN(pO, JString(k), JString(LEAD), JLong(100)))
    drain()
    K.check(got == 100 and rd(LEAD) == over - 100 and inv_counts(pO).get(LEAD) == 100, "MOVE over space: withdrawing still works: %d" % got)

    # ================================================= COMPACT / UNPACK / takeOpen keep working in one bag
    Cfg.CMP_ON = True
    mk({IRON_B: 350, IRON_E: 2})
    coll(U, dict((c_, 0) for c_ in cats))
    st_ = VS.st(k)
    st_.extra.setProperty(JString("comp.Smithing"), JString("1"))
    bridge.put(JString("coll:recipes:" + k), JString(IRON_E + EN.RECIPE_SUFFIX))
    pC = player(storage=[])
    made = int(VC.run(U, JString(k), VS.capsK(U, JString(k))))
    drain()
    K.check(made == 3 and rd(IRON_B) == 50 and rd(IRON_E) == 5, "COMPACT Smithing's Auto-compact: 300 bars -> 3 Enchanted, in the same bag: made %d, %s" % (made, pc(k)))
    # compacting when the bag is over space: a same-bag pack only frees room
    big = int(VS.capsK(U, JString(k)).get(JString("Smithing"))) + 300
    mk({IRON_B: big})
    coll(U, dict((c_, 0) for c_ in cats))
    VS.st(k).extra.setProperty(JString("comp.Smithing"), JString("1"))
    bridge.put(JString("coll:recipes:" + k), JString(IRON_E + EN.RECIPE_SUFFIX))
    made = int(VC.run(U, JString(k), VS.capsK(U, JString(k))))
    drain()
    K.check(made == big // 100 and rd(IRON_E) == made, "COMPACT over space: still packs (was: the other bag needed room): %d" % made)
    mk({IRON_E: 2})
    pU = player(storage=[])
    r_ = str(SPage.unpack(pU, JString(k), JString(IRON_E), JLong(1)))
    drain()
    K.check(r_.startswith("+Unpacked") and "to your inventory" in r_ and inv_counts(pU).get(IRON_B) == 100 and rd(IRON_E) == 1, "COMPACT Unpack to inventory from Smithing, and the line says so: %s" % r_)
    mk({IRON_B: 30, IRON_E: 4})
    Bridge.PLAYERS = TPlayers()
    TPlayers.P = player(storage=[])
    r_ = Fn(19).apply(JArray(JClass("java.lang.Object"))([U, JString(IRON_B), Long_(250)]))
    K.check(int(r_) == 250 and rd(IRON_E) == 1 and rd(IRON_B) == 80, "COMPACT sacks:fn:takeOpen (Enchanted opening for costs) from the moved bag: %s %s" % (r_, pc(k)))
    Bridge.PLAYERS = None

    # ================================================= SELL
    def pool_file():
        return str(Pool.DIR.resolve(JString(k + ".properties")).toString())

    def disk(i_):
        """the count of i_ in the pool FILE right now (what a crash would leave)"""
        if not os.path.isfile(pool_file()):
            return None
        for ln_ in open(pool_file(), encoding="latin-1").read().splitlines():
            if ln_.startswith(i_ + "="):
                return int(ln_.split("=", 1)[1])
        return 0

    @JImplements("java.util.function.Function")
    class FakeBz(object):
        def __init__(self):
            self.mode, self.calls, self.seen, self.disk = "pay", [], None, None

        @JOverride
        def apply(self, o):
            a = list(o)
            i_, q_ = str(a[1]), int(a[2])
            self.calls.append((str(a[0]), i_, q_))
            self.seen = rd(i_)
            self.disk = disk(i_)
            m = self.mode
            if m == "pay":
                return Long_(q_ * 7)
            if m == "arr":
                return JArray(JLong)([q_ * 3, q_])
            if m == "zero":
                return Long_(0)
            if m == "zeroarr":
                return JArray(JLong)([0, 0])
            if m == "part":
                return JArray(JLong)([9 * 40, 40])
            if m == "throw":
                raise JClass("java.lang.RuntimeException")("bazaar down")
            if m == "null":
                return None
            if m == "free":
                return JArray(JLong)([5, 0])
            if m == "over":
                return JArray(JLong)([5, q_ + 10])
            raise AssertionError(m)

    fz = FakeBz()
    PR = "bazaar:sell:" + LEAD

    def setup(n=250, fn=True, price=7):
        mk({LEAD: n})
        coll(U, dict((c_, 0) for c_ in cats))
        fz.calls, fz.seen, fz.mode = [], None, "pay"
        bridge.remove("bazaar:fn:sell")
        bridge.remove(PR)
        CLog.PENDING.clear()
        if fn:
            bridge.put("bazaar:fn:sell", fz)
        if price is not None:
            bridge.put(PR, Long_(price))
        sp = us.allocateInstance(SPage.class_)
        jfield(SPage.class_, "playerRef").set(sp, pref(U))
        jfield(SPage.class_, "info").set(sp, JString(""))
        jfield(SPage.class_, "amount").set(sp, JString(""))
        jfield(SPage.class_, "cat").set(sp, JString("Smithing"))
        jfield(SPage.class_, "sel").set(sp, JString(LEAD))
        return sp

    pS = player(storage=[])

    def click(sp, amt):
        sp.onEvent(None, None, pS, JString('{"a":"sell","@Amt":"%s"}' % amt))
        return str(jfield(SPage.class_, "info").get(sp))

    def logs():
        return [str(x) for x in list(CLog.PENDING)]

    # the amount box
    K.eq([int(SPage.parseAmt(JString(""), 100)), int(SPage.parseAmt(JString("30"), 100)), int(SPage.parseAmt(JString("all"), 100)), int(SPage.parseAmt(JString("1,500"), 100)),
          int(SPage.parseAmt(JString("abc"), 100)), int(SPage.parseAmt(JString("0"), 100))], [100, 30, MAX, 1500, -2, -2], "SELL the amount box: empty / 30 / all / 1,500 / abc / 0")
    # review fix: a dot is refused by Sell only (parseAmt would read 1.5 as 15)
    sp = setup(250)
    for bad_ in ("1.5", "0.5", ".", "1.000"):
        t_ = click(sp, bad_)
        K.check(rd(LEAD) == 250 and not fz.calls and t_.startswith("-Type a number"), "SELL amount '%s' refused, nothing sold: %s" % (bad_, t_))
    K.eq(int(SPage.parseAmt(JString("1.5"), 100)), 15, "the shared parseAmt is unchanged for Withdraw / Deposit")
    t_ = click(sp, "1,5")
    K.check(rd(LEAD) == 235 and fz.calls[-1][2] == 15, "SELL a comma is still digit grouping: %s" % t_)
    t_ = click(sp, "1_0")
    K.check(rd(LEAD) == 225 and fz.calls[-1][2] == 10, "SELL an underscore is still digit grouping: %s" % t_)
    # review fix: the file holds the debit BEFORE the coins exist, and whatever comes back at once
    sp = setup(250)
    t_ = click(sp, "100")
    K.eq(fz.disk, 150, "SELL CRASH: the pool FILE already has the debit while the Bazaar pays")
    for mode_, after_ in (("zero", 250), ("throw", 250), ("part", 210)):
        sp = setup(250)
        fz.mode = mode_
        click(sp, "100")
        K.eq(fz.disk, 150, "SELL CRASH '%s': on disk before the pay" % mode_)
        K.eq(disk(LEAD), after_, "SELL CRASH '%s': what came back is in the FILE straight away" % mode_)
        K.eq(rd(LEAD), after_, "SELL CRASH '%s': memory agrees" % mode_)
    # review fix: the file cannot be written = no pay, all back
    sp = setup(250)
    tmp_ = pool_file() + ".tmp"
    if os.path.isfile(tmp_):
        os.remove(tmp_)
    os.makedirs(tmp_)   # a folder in the tmp file's place: the write throws
    t_ = click(sp, "100")
    os.rmdir(tmp_)
    K.check(rd(LEAD) == 250 and not fz.calls and t_.startswith("-The Void could not be saved") and any("VOID-SELL-REFUSED" in x for x in logs()), "SELL the pool cannot be written: no pay, every item back, a log line: %s pool %d" % (t_, rd(LEAD)))
    sp = setup()
    t_ = click(sp, "")
    K.check(rd(LEAD) == 150 and fz.calls == [(k, LEAD, 100)] and t_.startswith("+Sold 100 ") and "700 coins" in t_, "SELL empty = one stack (100): %s" % t_)
    K.eq(fz.seen, 150, "SELL DEBIT FIRST: the pool was already short while the Bazaar was paying")
    K.check(any(("VOID-SELL " + LEAD + " sold 100 of 100 for 700 coins") in x for x in logs()), "SELL crafts.log: VOID-SELL line: %s" % logs())
    t_ = click(sp, "30")
    K.check(rd(LEAD) == 120 and fz.calls[-1][2] == 30 and "210 coins" in t_, "SELL a number = that many: %s" % t_)
    t_ = click(sp, "500")
    K.check(rd(LEAD) == 0 and fz.calls[-1][2] == 120 and "you only had 120" in t_, "SELL more than held = what is held, and says so: %s" % t_)
    t_ = click(sp, "1")
    K.check(rd(LEAD) == 0 and len(fz.calls) == 3 and t_.startswith("-None of it left"), "SELL nothing left: no call: %s" % t_)
    sp = setup(180)
    t_ = click(sp, "all")
    K.check(rd(LEAD) == 0 and fz.calls[-1][2] == 180 and "only had" not in t_, "SELL all = the whole amount: %s" % t_)
    sp = setup(50)
    fz.mode = "arr"
    t_ = click(sp, "all")
    K.check(rd(LEAD) == 0 and "150 coins" in t_, "SELL a long[]{coins, sold} answer: %s" % t_)
    for mode_ in ("zero", "zeroarr", "throw", "null", "free"):
        sp = setup(250)
        fz.mode = mode_
        t_ = click(sp, "100")
        K.check(rd(LEAD) == 250 and len(fz.calls) == 1 and t_.startswith("-The Bazaar would not buy") and fz.seen == 150, "SELL '%s': debited, then every item back: %s pool %d" % (mode_, t_, rd(LEAD)))
        K.check(any("VOID-SELL-REFUSED" in x for x in logs()), "SELL '%s': a crafts.log line" % mode_)
    sp = setup(250)
    fz.mode = "part"
    t_ = click(sp, "100")
    K.check(rd(LEAD) == 210 and "Sold 40" in t_ and "60 stay in the Void" in t_, "SELL part sold: only that part leaves: %s pool %d" % (t_, rd(LEAD)))
    sp = setup(250)
    fz.mode = "over"
    t_ = click(sp, "100")
    K.check(rd(LEAD) == 150, "SELL an answer of more than asked: at most the debit leaves: %s pool %d" % (t_, rd(LEAD)))
    sp = setup(250, fn=False)
    t_ = click(sp, "100")
    K.check(rd(LEAD) == 250 and t_.startswith("-The Bazaar cannot buy"), "SELL no bazaar:fn:sell (Bazaar older than 0.2.4): a message, nothing moves: %s" % t_)
    sp = setup(250, price=None)
    t_ = click(sp, "100")
    K.check(rd(LEAD) == 250 and not fz.calls and "does not buy" in t_, "SELL no price (not a product): a message, no call: %s" % t_)
    sp = setup(250, price=0)
    t_ = click(sp, "100")
    K.check(rd(LEAD) == 250 and not fz.calls and "does not buy" in t_, "SELL a price of 0: a message, no call: %s" % t_)
    sp = setup(250)
    for bad_ in ("abc", "0", "-5"):
        t_ = click(sp, bad_)
        K.check(rd(LEAD) == 250 and not fz.calls and t_.startswith("-Type a number"), "SELL amount '%s' refused: %s" % (bad_, t_))
    # two clicks
    sp = setup(100)
    click(sp, "60")
    t_ = click(sp, "60")
    K.check(rd(LEAD) == 0 and [c[2] for c in fz.calls] == [60, 40] and sum(c[2] for c in fz.calls) == 100, "SELL two clicks: 100 sold in all, never more: %s" % t_)
    # a profile change / a paused Void
    sp = setup(250)
    jfield(SPage.class_, "key").set(sp, JString("other-profile"))
    t_ = click(sp, "10")
    K.check(rd(LEAD) == 250 and not fz.calls and "profile changed" in t_, "SELL a profile change: nothing sold: %s" % t_)
    sp = setup(250)
    Pool.CLOSED = True
    t_ = click(sp, "10")
    Pool.CLOSED = False
    K.check(rd(LEAD) == 250 and not fz.calls and "paused" in t_, "SELL a paused Void (settling / shutting down): nothing sold: %s" % t_)
    # no selection, a fish, an item without a bag
    sp = setup(250)
    jfield(SPage.class_, "sel").set(sp, None)
    t_ = click(sp, "10")
    K.check(not fz.calls and t_.startswith("-Pick an item"), "SELL nothing selected: %s" % t_)
    FISH = "SkyyFishing_Fish_Test36"
    custom_item(FISH, 100)
    sp = setup(10)
    Pool.add(JString(k), JString(FISH), JLong(3))
    bridge.put("bazaar:sell:" + FISH, Long_(5))
    jfield(SPage.class_, "sel").set(sp, JString(FISH))
    t_ = click(sp, "")
    K.check(rd(FISH) == 3 and not fz.calls and "Fishing Bench" in t_, "SELL a whole fish: refused (its weight must not be sold by id): %s" % t_)
    r_ = str(SPage.sell(U, pS, JString(k), JString("Skyy_Sack_Pocket"), JLong(1)))
    K.check(r_.startswith("-") and "cannot be sold" in r_ and not fz.calls, "SELL an item with no bag: %s" % r_)
    # a world change: the page event has no player component - nothing happens
    sp = setup(100)
    sp.onEvent(None, None, None, JString('{"a":"sell","@Amt":"10"}'))
    K.check(rd(LEAD) == 100 and not fz.calls, "SELL no player on this thread (a world change): nothing sold")
    # the sale leaves the inventory alone
    pI = player(storage=[(LEAD, 40)])
    sp = setup(100)
    sp.onEvent(None, None, pI, JString('{"a":"sell","@Amt":"10"}'))
    K.check(rd(LEAD) == 90 and inv_counts(pI).get(LEAD) == 40, "SELL from the pool, not the inventory: pool %d, inventory %s" % (rd(LEAD), inv_counts(pI)))

    # ================================================= NAME + PAGE
    I18N = "com.hypixel.hytale.server.core.modules.i18n.I18nModule"
    ti = jp.makeClass("com.hypixel.hytale.server.core.modules.i18n.SkyyTestI18n36", jp.get(I18N))
    ti.addField(JClass("javassist.CtField").make("public static final java.util.HashMap M = new java.util.HashMap();", ti))
    ti.addMethod(JClass("javassist.CtNewMethod").make("public String getMessage(String l, String k) { return (String) M.get(k); }", ti))
    TI = JClass(ti.toClass(JClass(I18N).class_))

    def texts(b_):
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

    def binds(e_):
        return " ".join(str(x) for x in e_.getEvents()) if hasattr(e_, "getEvents") else str(e_)

    def build(sp, pl):
        b_, e_ = UCBc(), UEBc()
        sp.render(b_, e_, pl, JString(k), U)
        return texts(b_), texts_ev(e_)

    def texts_ev(e_):
        out_ = []
        for c_ in e_.getEvents():
            k_ = c_.getClass()
            while k_ is not None:
                for f_ in k_.getDeclaredFields():
                    if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                        continue
                    f_.setAccessible(True)
                    v_ = f_.get(c_)
                    if v_ is None:
                        continue
                    out_.append(str(v_))
                    try:
                        out_.append(str(v_.getClass().getMethod("toString").invoke(v_)))
                    except Exception:
                        pass
                k_ = k_.getSuperclass()
        return "\n".join(out_)

    Defs.DNAMES.clear()
    K.eq(str(SPage.pretty(JString(LEAD))), "Skyy Ench Lead", "NAME no translation: the tidied id (Skyy's screenshot)")
    for i_, n_ in ((LEAD, "Enchanted Lead Ingot"), ("Skyy_Ench_Maple", "Enchanted Maple Log"), (IRON_B, "Iron Ingot")):
        TI.M.put(JString("server.items.%s.name" % i_), JString(n_))
        TI.M.put(JString("items.%s.name" % i_), JString(n_))
    custom_item("Skyy_Ench_Maple", 100)
    jfield(JClass(I18N).class_, "instance").set(None, us.allocateInstance(TI.class_))
    Defs.DNAMES.clear()
    K.eq([str(SPage.pretty(JString(LEAD))), str(SPage.pretty(JString("Skyy_Ench_Maple"))), str(SPage.pretty(JString("Ingredient_Stick")))],
         ["Enchanted Lead Ingot", "Enchanted Maple Log", "Stick"], "NAME the real names; no translation = the tidied id")
    sp = setup(250)
    pP = player(storage=[])
    tx, ev = build(sp, pP)
    K.check("Enchanted Lead Ingot" in tx and "Skyy Ench Lead" not in tx, "NAME the page title is the real name")
    t_ = click(sp, "1")
    K.check("Enchanted Lead Ingot" in t_ and "Skyy Ench" not in t_, "NAME the sale line: %s" % t_)
    jfield(SPage.class_, "info").set(sp, JString(""))
    sp.onEvent(None, None, pP, JString('{"a":"wd","@Amt":"1"}'))
    t_ = str(jfield(SPage.class_, "info").get(sp))
    drain()
    K.check(t_ == "+Took 1 Enchanted Lead Ingot", "NAME +Took: %s" % t_)
    sp.onEvent(None, None, pP, JString('{"a":"dep","@Amt":"1"}'))
    t_ = str(jfield(SPage.class_, "info").get(sp))
    drain()
    K.check(t_ == "+Put 1 Enchanted Lead Ingot into the Void", "NAME +Put: %s" % t_)
    # the third row
    sp = setup(250)
    jfield(SPage.class_, "info").set(sp, JString(""))
    tx, ev = build(sp, pP)
    K.check("#SkyyVSell" in tx and "#SkyyVUnpack" in tx, "PAGE an Enchanted item: Sell + Unpack on the third row")
    K.check("The Bazaar pays about 7 coins each" in tx, "PAGE the price on the empty result line")
    K.eq(str(jfield(SPage.class_, "info").get(sp)), "", "PAGE the price is not kept as a result (a later build starts empty)")
    K.notes.append("PAGE the Sell event: " + ev[ev.index("SkyyVSell"):][:160].replace(chr(10), " | "))
    K.check("sell" in ev[ev.index("SkyyVSell"):][:200] and "SkyyVAmt" in ev[ev.index("SkyyVSell"):][:200], "PAGE Sell is bound and carries the amount box")
    jfield(SPage.class_, "sel").set(sp, JString("Ore_Copper"))
    Pool.add(JString(k), JString("Ore_Copper"), JLong(5))
    tx2, ev2 = build(sp, pP)
    K.check("#SkyyVSell" in tx2 and "#SkyyVUnpack" not in tx2 and "SkyyVBtnsC" in tx2, "PAGE a plain item: the Sell row, no Unpack")
    jfield(SPage.class_, "sel").set(sp, None)
    tx3, ev3 = build(sp, pP)
    K.check("#SkyyVSell" in tx3 and "SkyyVSell" not in ev3 and "SkyyVBtnsC" in tx3 and "or Sell" in tx3, "PAGE nothing selected: the row stays, Sell has no event (nothing jumps)")
    K.check(tx3[tx3.index("#SkyyVSell"):][:600] != tx[tx.index("#SkyyVSell"):][:600] and "Disabled" in tx3[tx3.index("#SkyyVSell"):][:600], "PAGE nothing selected: Sell uses the kit's disabled look")
    bridge.remove("bazaar:fn:sell")
    jfield(SPage.class_, "sel").set(sp, JString(LEAD))
    tx4, _e = build(sp, pP)
    K.check("The Bazaar pays" not in tx4, "PAGE no bazaar:fn:sell: no price line")
    jfield(JClass(I18N).class_, "instance").set(None, None)
    Defs.DNAMES.clear()


def run_s36(out, jar, scratch, home):
    T089.void_cases = cases36
    T089.run_void(out, jar, scratch, home)


def run_bc36(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(True)
    cp.appendClassPath(JString(jar))
    Mn = JClass("javassist.bytecode.Mnemonic")
    m = cp.get(PKG + "SacksPage").getDeclaredMethod("sell")
    ci = m.getMethodInfo().getCodeAttribute().iterator()
    cpool = m.getMethodInfo().getConstPool()
    seen = []
    while ci.hasNext():
        i = ci.next()
        op = str(Mn.OPCODE[ci.byteAt(i)])
        if op in ("invokestatic", "invokevirtual", "invokeinterface", "invokespecial"):
            idx = ci.u16bitAt(i + 1)
            if op == "invokeinterface":
                seen.append(str(cpool.getInterfaceMethodrefClassName(idx)).split(".")[-1] + "." + str(cpool.getInterfaceMethodrefName(idx)))
            else:
                seen.append(str(cpool.getMethodrefClassName(idx)).split(".")[-1] + "." + str(cpool.getMethodrefName(idx)))
    K.check("SacksPage.sellDebit" in seen and "Function.apply" in seen and seen.index("SacksPage.sellDebit") < seen.index("Function.apply"), "BC36 sell: the debit comes before the Bazaar's Function: %s" % seen[:12])
    K.check("SackPool.saveOk" in seen and seen.index("SacksPage.sellDebit") < seen.index("SackPool.saveOk") < seen.index("Function.apply"), "BC36 sell: the debit is written to disk before the Bazaar's Function")
    K.check("BagMirror.beforeTake" in seen and seen.index("BagMirror.beforeTake") < seen.index("SacksPage.sellDebit"), "BC36 sell: the live-mirror rule before the debit")
    K.save()


if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("s36", run_s36), ("all35", T35.run_all35), ("bc36", run_bc36), ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
