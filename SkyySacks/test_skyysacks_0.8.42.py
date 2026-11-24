"""Harness for SkyySacks 0.8.42 (round link1 - tools/sacks_0_8_42_patch.py: Shard Link, the late-game pocket upgrade + sacks:fn:link).
Build first:
    python tools/sacks_0_8_42_patch.py && python SkyySacks/build_skyysacks_0.8.42.py

    python SkyySacks/test_skyysacks_0.8.42.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  S       the patch re-generates the script byte for byte; one class added (VoidLink), no system / command; the only new jar entry is
          VoidLink.class; changed non-class entries = manifest.json only
  K42     EXECUTED on the real classes (the 0.8.9 Void fixture): THE PURCHASE - below Legendary refused, short items / coins refused, a stale
          price refused, a failed pd save / a throw after the coins (refund) / refused coins = nothing taken (pool, inventory, coins, pd line
          on disk); paid from the Void first then the inventory; the pd line on disk; a double click = "already"; Fishing has none; Pause /
          Turn on. THE BRIDGE sacks:fn:link (SackFn 25) - state / room (only linked pockets; another profile / an unsaved sweep = "") / put
          (each id into its own pocket up to the room, the items + the ~lk.<token> marker in ONE pool file write, a repeat = the same answer,
          a full pocket takes 0) / done / ack; crash before the pool save = nothing (done ""), crash after = on disk (done = the answer, also
          after a restart); bad arguments null. The cost ids live in their own pocket. THE PAGE - the Shard Link box in every state
  V41 / P40 / F37 / S36 / ALL35 / BC36   every 0.8.41 harness case EXECUTED on THIS jar (regression)
  D       start twice on a scratch COPY of the live Skyy_SkyySacks (the 0.8.40 harness' live phases): no migration, no byte changed
Exit code 1 on any failure.
"""
import os, sys, re, importlib.util, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_41", os.path.join(HERE, "test_skyysacks_0.8.41.py"))
T41 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T41)
sys.argv = _argv
HK.run_compare = _RC
T40, T37, T36, T35, T30, BETA = T41.T40, T41.T37, T41.T36, T41.T35, T41.T30, T41.BETA

VERSION = "0.8.42"
OLD_VERSION = "0.8.41"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "link1", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {"CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "CfgFile": ["~<clinit>"], "SkyySacksPlugin": ["~m setup"],   # the 13 rows + the version
          "SackCfg": ["+f LINK_COINS_%s" % c.upper() for c in ("Combat", "Farming", "Foraging", "Mining", "Smithing")]
          + ["+f LINK_COST_%s" % c.upper() for c in ("Combat", "Farming", "Foraging", "Mining", "Smithing")]
          + ["+f LINK_LEVEL", "+f LINK_ON", "~<clinit>", "~m pdKeys", "~m pdSig", "~m reload"],
          "SackFn": ["~m apply"], "SacksPage": ["+f lconfirm", "+m linkBox", "~m onEvent", "~m render"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
LINK_CATS = ("Mining", "Foraging", "Farming", "Combat", "Smithing")


def run_static(out, jar, scratch, home):
    import subprocess
    K = HK.Child(out)
    gen = os.path.join(HERE, "build_skyysacks_%s.py" % VERSION)
    cp = os.path.join(scratch, "regen.py")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sacks_0_8_42_patch.py"), "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(gen, "rb").read(), "S the patch re-generates the script byte for byte: %s" % p.stderr[-300:])
    g, o = open(gen, encoding="utf8").read(), open(os.path.join(HERE, "build_skyysacks_%s.py" % OLD_VERSION), encoding="utf8").read()
    K.eq([g.count(w) - o.count(w) for w in ("registerSystem(", "registerCommand(", "makeClass(")], [0, 0, 1], "S one class added (VoidLink), no system / command")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(set(zn.namelist()) - set(zo.namelist())), ["com/skyy/sacks/VoidLink.class"], "S the only new jar entry: VoidLink.class")
    K.eq(sorted(set(zo.namelist()) - set(zn.namelist())), [], "S no jar entry removed")
    K.eq(sorted(n for n in zn.namelist() if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.check('sbr0.put("sacks:fn:link", new {PKG}.SackFn(25));' in g and "ROLLBACK 0.8.42 -> 0.8.41 alone" in g, "S the bridge key + the rollback note")
    K.check(g.count("_pdrow(\"pd.link.") == 4 and "for c in LINK_CATS" in g, "S the Server Setup rows: pd.link.on / level + coins / cost per pocket")
    K.save()


def ucb_text(b_):
    from jpype import JClass
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


def cases42(K, L, scratch):
    from jpype import JClass, JString, JLong, JDouble, JArray, JObject, JImplements, JOverride
    VS, Pool, Defs, Cfg, SPage = L["VS"], L["Pool"], L["Defs"], L["Cfg"], L["SPage"]
    fresh, write_pool, player, custom_item, drain, restart, inv_counts, pc = (L[n] for n in ("fresh", "write_pool", "player", "custom_item", "drain",
                                                                                          "restart", "inv_counts", "pc"))
    UUID, us, jfield, pref, bridge = L["UUID"], L["us"], L["jfield"], L["pref"], L["bridge"]
    VL, Fn, VCm = JClass(PKG + "VoidLink"), JClass(PKG + "SackFn"), JClass(PKG + "VoidCompact")
    Bool = JClass("java.lang.Boolean")

    @JImplements("java.util.function.Function")
    class PF(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    coins = {"bal": 10 ** 9, "mode": "ok"}

    def c_take(o):
        n = int(list(o)[1])
        if coins["mode"] == "refuse" or coins["bal"] < n:
            return Bool.FALSE
        coins["bal"] -= n
        return Bool.TRUE

    def c_add(o):
        coins["bal"] += int(list(o)[1])
        return JLong(coins["bal"])
    bridge.put("coins:fn:take", PF(c_take))
    bridge.put("coins:fn:get", PF(lambda o: JLong(coins["bal"])))
    bridge.put("coins:fn:add", PF(c_add))
    bridge.put("coins:fn:curve", PF(lambda o: JDouble(36.8)))
    bridge.put("coins:fn:flush", PF(lambda o: Bool.TRUE))
    K.eq(str(bridge.get("sacks:fn:link")) if bridge.get("sacks:fn:link") is not None else None, None, "K42 (the fixture publishes no bridge: SackFn 25 is called directly)")
    link = Fn(25)

    def call(*a):
        r = link.apply(JArray(JObject)([JString(x) if isinstance(x, str) else x for x in a]))
        return None if r is None else (bool(r) if isinstance(r, Bool) or str(type(r)).find("Boolean") >= 0 else str(r))
    cost = {}
    for c in LINK_CATS:
        cost[c] = [(x.split(":")[0], int(x.split(":")[1])) for x in str(getattr(Cfg, "LINK_COST_" + c.upper())).split(",")]
    for c, v in cost.items():
        for i_, _q in v:
            custom_item(i_, 100)
    for i_ in ("Ore_Copper", "Ingredient_Bar_Iron", "Wood_Oak_Trunk"):
        custom_item(i_, 100)
    # the cost ids are that pocket's own Enchanted items
    homes = dict((i_, str(Defs.catOf(JString(i_)))) for v in cost.values() for i_, _q in v)
    allh = {}
    for row_ in ("Cobblestone", "Sandstone", "Shale", "Slate", "Basalt", "Gemstone", "Clay", "Copper", "Iron", "Thorium", "Cobalt", "HideLight", "HideMedium",
                 "Charcoal", "Lead", "Bronze", "Dusk", "Ice", "Marble", "Volcanic"):
        custom_item("Skyy_Ench_" + row_, 100)
        allh[row_] = str(Defs.catOf(JString("Skyy_Ench_" + row_)))
    K.notes.append("K42 Enchanted homes: %s" % allh)
    K.check(all(homes[i_] == c for c, v in cost.items() for i_, _q in v), "K42 every Shard Link cost item lives in its own pocket: %s" % homes)
    U = UUID.fromString("00000000-0000-0000-0000-0000000c0f42")
    k = str(U)
    base = os.path.join(scratch, "void42")
    drain()
    fresh(base)
    ECOB, EIR, ETH = [i_ for i_, _q in cost["Mining"]]
    write_pool(os.path.join(base, "pools"), k, {ECOB: 40, EIR: 32, ETH: 16, "Ore_Copper": 100})
    s = VS.st(k)
    s.first = 1
    price = int(VL.price(0))
    K.eq(price, int(VCm.round7(10000 * 36.8)), "K42 the price = pd.link.coins x the coin curve at pd.link.level, rounded like Auto-compact (%d)" % price)
    K.eq((call("state", k), call("room", U, k, "Ore_Copper")), ("", ""), "K42 no link yet: state '' and room ''")

    def snap(p_):
        return (pc(k), inv_counts(p_), coins["bal"], open(os.path.join(base, "pd", k + ".properties"), encoding="latin-1").read() if os.path.isfile(os.path.join(base, "pd", k + ".properties")) else "")
    s.rar[0] = 2
    p = player(storage=[(ECOB, 30)])
    b0 = snap(p)
    r = str(VL.buyAt(p, U, k, 0, -1))
    K.check(r.startswith("-Shard Link needs the Mining pocket at Legendary") and snap(p) == b0, "K42 below Legendary: refused, nothing taken: %s" % r)
    s.rar[0] = 3
    p2 = player(storage=[(ECOB, 10)])
    b0 = snap(p2)
    r = str(VL.buyAt(p2, U, k, 0, -1))
    K.check(r.startswith("-Not enough") and snap(p2) == b0, "K42 short items (50 / 64): refused, nothing taken: %s" % r)
    coins["bal"] = 5
    b0 = snap(p)
    r = str(VL.buyAt(p, U, k, 0, price))
    K.check(r.startswith("-Not enough coins") and snap(p) == b0, "K42 short coins: refused, nothing taken: %s" % r)
    coins["bal"] = 10 ** 9
    b0 = snap(p)
    r = str(VL.buyAt(p, U, k, 0, price + 1))
    K.check(r.startswith("=The price is now") and snap(p) == b0, "K42 a stale page (another price shown): nothing taken: %s" % r)
    VS.CRASHAT, VS.CRASHN, VS.CRASHHITS = "lnksave", 1, 0
    r = str(VL.buyAt(p, U, k, 0, price))
    K.check(r.startswith("-The Void data could not be saved") and snap(p)[:3] == b0[:3] and "link.Mining=1" not in snap(p)[3] and not bool(VL.bought(k, 0)),
            "K42 the pd save fails: nothing taken: %s" % r)
    VS.CRASHAT, VS.CRASHN, VS.CRASHHITS = "lnkbuy", 1, 0
    r = str(VL.buyAt(p, U, k, 0, price))
    drain()
    b1 = snap(p)
    K.check(r.startswith("-Something went wrong - your items are back and your coins were given back") and b1[:3] == b0[:3] and "link.Mining=1" not in b1[3],
            "K42 a throw after the coins: items + coins back, the line removed on disk: %s" % r)
    coins["mode"] = "refuse"
    r = str(VL.buyAt(p, U, k, 0, price))
    K.check(r.startswith("-Coins are busy") and snap(p)[:3] == b0[:3] and not bool(VL.bought(k, 0)), "K42 SkyyCoins refuses: nothing taken: %s" % r)
    coins["mode"] = "ok"
    VS.CRASHAT = None
    r = str(VL.buyAt(p, U, k, 0, price))
    drain()
    a1 = snap(p)
    K.check(r.startswith("+The Mining pocket now has Shard Link"), "K42 the purchase: %s" % r)
    K.eq((a1[0].get(ECOB, 0), a1[1].get(ECOB, 0), a1[0].get(EIR, 0), a1[0].get(ETH, 0), b0[2] - a1[2]), (0, 6, 0, 0, price),
         "K42 ... paid: the Void's 40 first, then 24 from the inventory; Iron + Thorium from the Void; the coins")
    K.check("link.Mining=1" in a1[3], "K42 ... the pd line is on disk")
    pf = open(os.path.join(base, "pools", k + ".properties"), encoding="latin-1").read()
    K.check(not re.search(r"^%s=" % ECOB, pf, re.M) and re.search(r"^Ore_Copper=100$", pf, re.M), "K42 ... the pool debit is on disk (VoidJob 4)")
    r = str(VL.buyAt(p, U, k, 0, price))
    K.check(r == "=Mining already has Shard Link" and snap(p) == a1, "K42 a double click: 'already', nothing taken: %s" % r)
    r = str(VL.buyAt(p, U, k, 3, -1))
    K.check(r.startswith("=No shard fills the Fishing pocket"), "K42 Fishing: no Shard Link: %s" % r)
    K.eq(call("state", k), "Mining", "K42 state = Mining")
    r1 = str(VL.toggle(U, k, 0))
    K.check(r1.startswith("=Shard Link paused") and call("state", k) == "" and call("room", U, k, "Ore_Copper") == "", "K42 Pause: state / room '': %s" % r1)
    r2 = str(VL.toggle(U, k, 0))
    K.check(r2.startswith("+Shard Link is on again") and call("state", k) == "Mining", "K42 Turn on: %s" % r2)
    Cfg.LINK_ON = False
    K.check(call("state", k) == "" and str(VL.buyAt(p, U, k, 1, -1)).startswith("-Shard Link is switched off"), "K42 pd.link.on off: no link anywhere, no purchase")
    Cfg.LINK_ON = True
    # ---- the bridge
    room0 = int(VS.capOf(VS.levelBest(k, 0), VS.rank(k, 0))) - int(VS.usedAll(k)[0])
    K.eq(call("room", U, k, "Ore_Copper,Ingredient_Bar_Iron,Wood_Oak_Trunk,Bad,Id"), "Mining:%d|Ore_Copper=Mining" % room0,
         "K42 room: only the linked pocket (Mining %d); bars (Smithing) / logs (Foraging) not linked are left out" % room0)
    bridge.put("profile:fn:key", PF(lambda o: JString(k + "-p2")))
    K.eq((call("room", U, k, "Ore_Copper"), call("put", U, k, "tA", "Ore_Copper:5")), ("", ""), "K42 another profile active: room '' and put '' (nothing put)")
    bridge.remove("profile:fn:key")
    K.eq(call("done", k, "tA"), "", "K42 ... and no marker")
    Pool.SWEPTQ.put(k, Bool.TRUE)
    K.eq((call("room", U, k, "Ore_Copper"), call("put", U, k, "tB", "Ore_Copper:5")), ("", ""), "K42 an unsaved sweep in the pool: room / put '' (the crash-window rule)")
    Pool.SWEPTQ.remove(k)
    pool0 = pc(k)
    acc = call("put", U, k, "t1", "Ore_Copper:%d,Ingredient_Bar_Iron:5" % (room0 + 50))
    K.eq(acc, "Ore_Copper:%d,Ingredient_Bar_Iron:0" % room0, "K42 put: Mining takes its room, the bar (Smithing, not linked) 0")
    K.eq(pc(k).get("Ore_Copper", 0) - pool0.get("Ore_Copper", 0), room0, "K42 ... the pool got exactly that")
    pf = open(os.path.join(base, "pools", k + ".properties"), encoding="latin-1").read()
    K.check(re.search(r"^Ore_Copper=%d$" % (100 + room0), pf, re.M) and re.search(r"^~lk.t1=\d+\\?\|Ore_Copper\\?:%d,Ingredient_Bar_Iron\\?:0$" % room0, pf, re.M),
            "K42 ... the items AND the marker ~lk.t1 in the pool file (one write)")
    p1 = pc(k)
    K.check(call("put", U, k, "t1", "Ore_Copper:999") == acc and pc(k) == p1, "K42 the same token again: the same answer, nothing added twice")
    K.eq(call("done", k, "t1"), acc, "K42 done t1 = the answer")
    K.check(call("ack", k, "t1") is True and call("done", k, "t1") == "" and call("ack", k, "t1") is False, "K42 ack removes the marker (done '' after; a second ack FALSE)")
    K.eq(call("put", U, k, "t2", "Ore_Copper:5"), "Ore_Copper:0", "K42 a full pocket takes 0")
    call("ack", k, "t2")
    Pool.add(k, "Ore_Copper", -300)
    Pool.saveOk(k)
    p1 = pc(k)
    VS.CRASHAT, VS.CRASHN, VS.CRASHHITS = "lnkput", 1, 0
    K.check(call("put", U, k, "t3", "Ore_Copper:20") is None and pc(k) == p1 and call("done", k, "t3") == "", "K42 a crash before the pool save: null, nothing added, done ''")
    restart()
    VS.st(k).first = 1
    K.check(call("done", k, "t3") == "" and pc(k) == p1, "K42 ... after a restart too (the file never had it)")
    VS.CRASHAT, VS.CRASHN, VS.CRASHHITS = "lnkput2", 1, 0
    K.check(call("put", U, k, "t4", "Ore_Copper:20") is None and call("done", k, "t4") == "Ore_Copper:20", "K42 a crash after the pool save: null, but done = the answer")
    restart()
    VS.st(k).first = 1
    K.check(call("done", k, "t4") == "Ore_Copper:20" and pc(k).get("Ore_Copper", 0) == p1.get("Ore_Copper", 0) + 20, "K42 ... after a restart: on disk, items + marker")
    VS.CRASHAT = None
    # ---- FIX (link1 critics): the change under both locks, the fsync outside the pool monitor, a save that fails / waits = UNSAVED
    K.check(bool(VL.MUTHELD) and not bool(VL.SAVEHELD), "FIX42 the items + marker change ran under the pool monitor AND SAVELOCK; the fsync without the pool monitor")
    src42 = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    K.check("synchronized (@PKG@.SackPool.class) { return put0(u, k, tok, items); }" in src42 and "public static Object put0(" in src42
            and "saveOk" not in src42[src42.index("public static Object put0("):src42.index("public static Object put1(")],
            "FIX42 put0 (under the pool monitor) never saves; fin saves outside it")
    Pool.saveOk(k)
    restart()
    VL.UNSAVED.clear()
    VS.st(k).first = 1
    p5 = pc(k)
    VS.CRASHAT, VS.CRASHN, VS.CRASHHITS = "lnkput1", 1, 0
    K.check(call("put", U, k, "t5", "Ore_Copper:20") is None and pc(k).get("Ore_Copper", 0) == p5.get("Ore_Copper", 0) + 20, "FIX42 the save fails: null, the put stays in memory (UNSAVED)")
    pf = open(os.path.join(base, "pools", k + ".properties"), encoding="latin-1").read()
    K.check("~lk.t5" not in pf and re.search(r"^Ore_Copper=%d$" % p5.get("Ore_Copper", 0), pf, re.M), "FIX42 ... the file has neither the items nor the marker")
    restart()
    VL.UNSAVED.clear()
    VS.st(k).first = 1
    K.check(call("done", k, "t5") == "" and pc(k) == p5, "FIX42 ... a crash now: 'never happened' and the pool as before (nothing doubled)")
    VS.CRASHAT, VS.CRASHN, VS.CRASHHITS = "lnkput1", 1, 0
    K.check(call("put", U, k, "t6", "Ore_Copper:20") is None, "FIX42 the save fails again: null")
    Pool.SWEPTQ.put(k, Bool.TRUE)
    K.check(call("done", k, "t6") is None and call("put", U, k, "t6", "Ore_Copper:20") is None and "~lk.t6" not in open(os.path.join(base, "pools", k + ".properties"), encoding="latin-1").read(),
            "FIX42 ... an unsaved sweep in the pool: done / a repeat put = null (cannot tell), no early save (the crash-window rule)")
    Pool.SWEPTQ.remove(k)
    K.check(call("done", k, "t6") == "Ore_Copper:20" and "~lk.t6" in open(os.path.join(base, "pools", k + ".properties"), encoding="latin-1").read() and VL.UNSAVED.isEmpty(),
            "FIX42 ... done saves it now: the answer, items + marker on disk")
    K.check(call("put", U, k, "t6", "Ore_Copper:20") == "Ore_Copper:20" and call("ack", k, "t6") is True, "FIX42 ... a repeat = the same answer; ack")
    Pool.BADPOOL.put(JString("bad-key-42"), JClass("java.lang.Long")(int(__import__("time").time() * 1000)))
    K.check(call("ack", "bad-key-42", "t9") is None, "FIX42 ack while the pool cannot be read: null (cannot tell), never FALSE")
    Pool.BADPOOL.remove(JString("bad-key-42"))
    K.check(call("put") is None and call("put", U, k, "a|b", "Ore_Copper:1") is None and call("nope", k) is None and link.apply(JString("x")) is None,
            "K42 bad arguments / a token with | / an unknown op: null")
    K.check(int(VL.PUTS.get()) >= 3 and int(VL.REFUSED.get()) >= 1, "K42 the counters: %d puts, %d refused" % (int(VL.PUTS.get()), int(VL.REFUSED.get())))
    # ---- the page: the box in every state
    UCBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def page(cat, confirm=False):
        pg = us.allocateInstance(SPage.class_)
        jfield(SPage.class_, "playerRef").set(pg, pref(U))
        jfield(SPage.class_, "info").set(pg, JString(""))
        jfield(SPage.class_, "amount").set(pg, JString(""))
        pg.cat = cat
        pg.lconfirm = confirm
        b_, e_ = UCBc(), UEBc()
        pg.render(b_, e_, p, k, U)
        return ucb_text(b_)

    def box(t):
        ti = re.search(r'#SkyyVLnkTitle\.Text[^\n]*\n([^\n]*)', t)
        return t
    t = page("Mining")
    K.check("#SkyyVLnk " in t and "Shard Link: On" in t and "#SkyyVLnkTog" in t and "Pause" in t, "K42 page Mining (bought): 'Shard Link: On' + Pause")
    t = page("Fishing")
    K.check("No shard fills the Fishing pocket." in t and "#SkyyVLnkBuy" not in t, "K42 page Fishing: no link")
    t = page("Foraging")
    K.check("Needs this pocket at Legendary first." in t and "#SkyyVLnkBuy" not in t, "K42 page Foraging below Legendary: the late-game note, no Buy")
    VS.st(k).rar[1] = 3   # (the state object of before the restarts above is gone)
    t = page("Foraging")
    K.check(("Shard Link - %s coins" % str(SPage.shortNum(price))) in t and "#SkyyVLnkBuy" in t and re.search(r"Coins [0-9.,kKmMbB?]+ / ", t),
            "K42 page Foraging at Legendary: the price, the have / need lines, Buy")
    K.notes.append("K42 Foraging box: %s" % re.findall(r"Shard Link.{0,200}|Coins.{0,200}", t)[:6])
    t = page("Foraging", confirm=True)
    K.check("#SkyyVLnkYes" not in t or "#SkyyVLnkNo" in t, "K42 page Foraging confirm: Pay with Cancel (only when ready)")
    for i_, q_ in cost["Foraging"]:
        Pool.add(k, i_, q_)
    t = page("Foraging", confirm=True)
    K.check("#SkyyVLnkYes" in t and "#SkyyVLnkNo" in t and "Pay " in t, "K42 page Foraging ready + confirm: Pay / Cancel")
    K.notes.append("K42 Mining price %d coins + %s; room at Legendary Lv %d = %d" % (price, cost["Mining"], int(VS.levelBest(k, 0)), room0))
    # ---- FIX (critic): a purchase undone whose second pd save fails: memory "not bought", kept dirty, the saver writes it
    for i_, q_ in cost["Foraging"]:
        Pool.add(k, i_, q_)
    coins["mode"] = "refuse"
    VS.CRASHAT, VS.CRASHN, VS.CRASHHITS = "lnkunbuy", 1, 0
    r = str(VL.buyAt(p, U, k, 1, -1))
    VS.CRASHAT = None
    coins["mode"] = "ok"
    K.check(r.startswith("-Coins are busy") and not bool(VL.bought(k, 1)) and VS.DIRTY.containsKey(k), "FIX42 the undo's save fails: not bought, kept dirty: %s" % r)
    VS.flushDirty()
    K.check("link.Foraging=1" not in open(os.path.join(base, "pd", k + ".properties"), encoding="latin-1").read(), "FIX42 ... the saver's retry: no link line on disk")


def run_k42(out, jar, scratch, home):
    T35.T089.void_cases = cases42
    T35.T089.run_void(out, jar, scratch, home)


if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ["VoidLink"],
           [("static", run_static), ("k42", run_k42), ("v41", T41.run_v41), ("p40", T40.run_p40), ("f37", T37.run_f37), ("s36", T36.run_s36),
            ("all35", T35.run_all35), ("bc36", T36.run_bc36), ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
