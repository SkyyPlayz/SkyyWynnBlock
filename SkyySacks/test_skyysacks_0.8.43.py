"""Harness for SkyySacks 0.8.43 (round oldmenu10 - tools/sacks_0_8_43_patch.py: the pocket upgrade shop bridge sacks:fn:upView / upAct for
SkyyMenu 0.3.78's in-screen Upgrades view).
Build first:
    python tools/sacks_0_8_43_patch.py && python SkyySacks/build_skyysacks_0.8.43.py

    python SkyySacks/test_skyysacks_0.8.43.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  S       the patch re-generates the script byte for byte; no class / system / command added; the jar entries are the same; changed
          non-class entries = manifest.json only; the two keys registered; the old ops' code is byte-identical
  K43     EXECUTED on the real classes (the 0.8.9 Void fixture): upView off the world thread = null; the lines (h / u / c / k / l / li / r) in
          every box state; upAct: a stale token, a wrong / changed profile, a value the view did not show, a changed rarity / cost / price /
          state / refill choice = '=' and NOTHING moves (pool, inventory, coins, pd file); RACING PRESSES with one token (threads) = exactly
          one runs - coins AND items conserved (the rarity upgrade, Auto-compact, Shard Link); a used token = '='; Pause / Turn on; refill;
          Pick up all / Deposit <pocket> / Deposit every bag conserve every item; bad arguments = null; an unknown op said
  K42 / V41 / P40 / F37 / S36 / ALL35 / BC36   every 0.8.42 harness case EXECUTED on THIS jar (regression: the old ops unchanged)
  D       start twice on a scratch COPY of the live Skyy_SkyySacks: no migration, no byte changed
Exit code 1 on any failure.
"""
import os, sys, re, importlib.util, zipfile, threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_42", os.path.join(HERE, "test_skyysacks_0.8.42.py"))
T42 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T42)
sys.argv = _argv
HK.run_compare = _RC
T41, T40, T37, T36, T35, T30, BETA = T42.T41, T42.T40, T42.T37, T42.T36, T42.T35, T42.T30, T42.BETA

VERSION = "0.8.43"
OLD_VERSION = "0.8.42"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "oldmenu10", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {"SackBridge": ["+f UPBASE", "+f UPSEQ", "+f UPTOK", "+m cmpSt", "+m lnkSt", "+m upAct", "+m upCost", "+m upDeposit", "+m upNum",
                         "+m upTakeAll", "+m upView", "~<clinit>"],
          "SackFn": ["~m apply"], "SkyySacksPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]}   # + the version strings
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, home):
    import subprocess
    K = HK.Child(out)
    gen = os.path.join(HERE, "build_skyysacks_%s.py" % VERSION)
    cp = os.path.join(scratch, "regen.py")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sacks_0_8_43_patch.py"), "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(gen, "rb").read(), "S the patch re-generates the script byte for byte: %s" % p.stderr[-300:])
    g, o = open(gen, encoding="utf8").read(), open(os.path.join(HERE, "build_skyysacks_%s.py" % OLD_VERSION), encoding="utf8").read()
    K.eq([g.count(w) - o.count(w) for w in ("registerSystem(", "registerCommand(", "makeClass(")], [0, 0, 0], "S no class / system / command added")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(set(zn.namelist()) ^ set(zo.namelist())), [], "S the same jar entries (no class added or removed)")
    K.eq(sorted(n for n in zn.namelist() if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.check('sbr0.put("sacks:fn:upView", new {PKG}.SackFn(26));' in g and 'sbr0.put("sacks:fn:upAct", new {PKG}.SackFn(27));' in g
            and "ROLLBACK to 0.8.42: safe alone" in g, "S the two bridge keys + the rollback note")
    for m_ in ("public static String pocketList(", "public static String pocketAct(", "public static Boolean openPocket(", "public static String furnList(",
               "public static String furnAct(", "public static String upgrade(@PLA@ p", "public static String buyAt(java.util.UUID u", "public static String buyAt(@PLA@ p"):
        a_, b_ = g.index(m_), o.index(m_)
        K.eq(g[a_:g.index('"""', a_)], o[b_:o.index('"""', b_)], "S %s... byte-identical (the old op / the page's code path untouched)" % m_[:40])
    K.check(g.count("UPTOK.remove(us, rec)") == 1 and "if (!UPTOK.remove(us, rec)) return old;" in g, "S the token is used up atomically (ConcurrentHashMap.remove(key, record)) exactly once")
    K.save()


def cases43(K, L, scratch):
    from jpype import JClass, JString, JLong, JDouble, JArray, JObject, JImplements, JOverride
    VS, Pool, Defs, Cfg = L["VS"], L["Pool"], L["Defs"], L["Cfg"]
    fresh, write_pool, player, custom_item, drain, inv_counts, pc, coll = (L[n] for n in ("fresh", "write_pool", "player", "custom_item", "drain",
                                                                                         "inv_counts", "pc", "coll"))
    UUID, bridge, TPlayers, Bridge = L["UUID"], L["bridge"], L["TPlayers"], L["Bridge"]
    Fn, VL, VCm, RP = JClass(PKG + "SackFn"), JClass(PKG + "VoidLink"), JClass(PKG + "VoidCompact"), JClass(PKG + "RefillPref")
    Bool = JClass("java.lang.Boolean")

    @JImplements("java.util.function.Function")
    class PF(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    lock = threading.Lock()
    coins = {"bal": 10 ** 9, "takes": 0}

    def c_take(o):
        n = int(list(o)[1])
        with lock:
            if coins["bal"] < n:
                return Bool.FALSE
            coins["bal"] -= n
            coins["takes"] += 1
            return Bool.TRUE

    def c_add(o):
        with lock:
            coins["bal"] += int(list(o)[1])
            return JLong(coins["bal"])
    bridge.put("coins:fn:take", PF(c_take))
    bridge.put("coins:fn:get", PF(lambda o: JLong(coins["bal"])))
    bridge.put("coins:fn:add", PF(c_add))
    bridge.put("coins:fn:curve", PF(lambda o: JDouble(36.8)))
    bridge.put("coins:fn:flush", PF(lambda o: Bool.TRUE))
    view_, act_ = Fn(26), Fn(27)

    def jv(*a):
        return JArray(JObject)([JString(x) if isinstance(x, str) else x for x in a])

    def view(u, cat):
        r = view_.apply(jv(u, cat))
        return None if r is None else str(r)

    def act(op, u, tok, pk, arg=None):
        r = act_.apply(jv(op, u, tok, pk, arg))
        return None if r is None else str(r)

    def parse(v):
        d = {"c": [], "li": []}
        for ln in v.split("\n"):
            f = ln.split("|")
            if f[0] in ("c", "li"):
                d[f[0]].append(f[1:])
            else:
                d[f[0]] = f[1:]
        return d
    U = UUID.fromString("00000000-0000-0000-0000-0000000c0f43")
    k = str(U)
    base = os.path.join(scratch, "void43")
    drain()
    fresh(base)
    cats = [str(c) for c in Defs.CATS]
    up_cost = dict((i_.split(":")[0], int(i_.split(":")[1])) for i_ in str(Cfg.cost(0, 1)).split(","))
    for i_ in list(up_cost) + ["Ore_Copper", "Ore_Iron", "Rubble_Stone"]:
        custom_item(i_, 100)
    lcost = [(x.split(":")[0], int(x.split(":")[1])) for x in str(Cfg.LINK_COST_MINING).split(",")]
    for i_, _q in lcost:
        custom_item(i_, 100)
    K.notes.append("K43 Mining Normal -> Unique cost: %s; Shard Link items: %s" % (up_cost, lcost))
    pool0 = dict((i_, q_ * 3) for i_, q_ in up_cost.items())
    pool0.update({"Ore_Copper": 500})
    write_pool(os.path.join(base, "pools"), k, pool0)
    s = VS.st(k)
    s.first = 1
    coll(U, dict((c_, 0) for c_ in cats))
    p = player(storage=[("Ore_Copper", 50)])

    def rdpd():   # the writer replaces the file atomically - on Windows a read in that instant is refused: wait for the writer, try again
        pdf = os.path.join(base, "pd", k + ".properties")
        for _t in range(50):
            try:
                drain()
                return open(pdf, encoding="latin-1").read() if os.path.isfile(pdf) else ""
            except PermissionError:
                __import__("time").sleep(0.05)
        return open(pdf, encoding="latin-1").read()

    def snap():
        return (pc(k), inv_counts(p), coins["bal"], int(VS.rarOf(k, 0)), rdpd())
    try:
        Bridge.PLAYERS = None
        K.check(view(U, "Mining") is None and act("up", U, "x", k, "0") is None, "K43 off the player's world thread: view / act = null (nothing read, nothing done)")
        Bridge.PLAYERS = TPlayers()
        TPlayers.P = p
        # ---- the view
        v = view(U, "Mining")
        d = parse(v)
        tok, pk = d["h"][1], d["h"][2]
        K.check(d["h"][0] == "ok" and pk == k and d["h"][3] == "Mining" and d["h"][6] == "Normal" and d["h"][10] == str(10 ** 9) and len(tok) > 4,
                "K43 VIEW h: ok, token, profile key, pocket, rarity Normal, coins (%s)" % d["h"])
        K.check(d["u"][0] == "up" and d["u"][1:5] == ["0", "Normal", "1", "Unique"] and d["u"][7] == "1" and "Pay the items" in d["u"][8],
                "K43 VIEW u: up Normal -> Unique, ready (%s)" % d["u"])
        K.eq(sorted((c_[0], int(c_[3])) for c_ in d["c"]), sorted(up_cost.items()), "K43 VIEW c: the cost cells = SackCfg.cost(Mining, Unique)")
        K.check(d["k"][0] == "buy" and d["k"][2] == "1" and d["l"][0] == "need" and "Legendary" in d["l"][4] and d["r"][0] == "0",
                "K43 VIEW k: Auto-compact buy (ready), l: Shard Link needs Legendary, r: refill Hotbar only (%s / %s / %s)" % (d["k"], d["l"], d["r"]))
        v2 = view(U, "Mining")
        tok2 = parse(v2)["h"][1]
        K.check(tok2 != tok, "K43 VIEW every read makes a new token")
        K.check(view(U, "Nope").startswith("off|No such pocket") and act("up", U, tok2, k, "0").startswith("=That click was for an older copy"),
                "K43 VIEW an unknown pocket = off (and kills the token: the next press = older copy)")
        b0 = snap()
        v = parse(view(U, "Mining"))
        tok = v["h"][1]
        r = act("up", U, tok2, k, "0")
        K.check(r.startswith("=That click was for an older copy") and snap() == b0, "K43 UP a stale token: '=', nothing taken (%s)" % r)
        r = act("up", U, tok, k + "-p2", "0")
        K.check(r.startswith("=Your profile changed") and snap() == b0, "K43 UP a wrong profile key: '=', nothing taken (%s)" % r)
        r = act("up", U, tok, k, "1")
        K.check(r.startswith("=That click was for an older copy") and snap() == b0, "K43 UP a rarity the view did not show: '=', nothing taken (%s)" % r)
        old_c = str(Cfg.PD_COST_MINING_UNIQUE)
        Cfg.PD_COST_MINING_UNIQUE = JString(old_c.split(",")[0])
        r = act("up", U, tok, k, "0")
        K.check(r.startswith("=The upgrade cost changed since you looked") and snap() == b0, "K43 UP the cost changed in Server Setup: '=', nothing taken (%s)" % r)
        Cfg.PD_COST_MINING_UNIQUE = JString(old_c)
        bridge.put("profile:fn:key", PF(lambda o: JString(k + "-p2")))
        r = act("up", U, tok, k, "0")
        K.check(r is not None and r.startswith("-The Void is paused") or r.startswith("=Your profile changed"), "K43 UP another profile settled: refused (%s)" % r)
        bridge.remove("profile:fn:key")
        K.check(snap() == b0, "K43 UP ... nothing taken")
        # RACING PRESSES with one token: exactly one runs
        tot0 = dict((i_, b0[0].get(i_, 0) + b0[1].get(i_, 0)) for i_ in up_cost)
        res = []

        def press(op, t_, a_):
            res.append(act(op, U, t_, k, a_))

        def race(op, t_, a_, n=4):
            del res[:]
            bar = threading.Barrier(n)

            def go():
                bar.wait()
                press(op, t_, a_)
            th = [threading.Thread(target=go) for _ in range(n)]
            for x in th:
                x.start()
            for x in th:
                x.join()
            return list(res)
        rs = race("up", tok, "0")
        drain()
        a1 = snap()
        tot1 = dict((i_, a1[0].get(i_, 0) + a1[1].get(i_, 0)) for i_ in up_cost)
        K.check(len([x for x in rs if x and x.startswith("+")]) == 1 and len([x for x in rs if x and x.startswith("=That click was for an older copy")]) == 3,
                "K43 RACE UP 4 presses with one token: exactly one ran, three '=older copy' (%s)" % rs)
        K.check(a1[3] == 1 and all(tot0[i_] - tot1[i_] == q_ for i_, q_ in up_cost.items()) and a1[2] == b0[2],
                "K43 RACE UP the cost paid exactly once (items conserved: %s -> %s), Unique now, no coins" % (tot0, tot1))
        r = act("up", U, tok, k, "0")
        K.check(r.startswith("=That click was for an older copy") and snap()[:4] == a1[:4], "K43 UP the used token again: '=', nothing taken")
        # ---- Auto-compact buy (SkyyCollections published its unlocked recipes - buyAt needs them, 0.8.30 fixer 2)
        bridge.put(JString("coll:recipes:" + k), JString(""))
        v = parse(view(U, "Mining"))
        tok, price = v["h"][1], int(v["k"][1])
        K.check(v["u"][1:5] == ["1", "Unique", "2", "Rare"] and v["k"][0] == "buy", "K43 VIEW after the upgrade: Unique -> Rare, compact buy (%d coins)" % price)
        b0 = snap()
        r = act("cmpbuy", U, tok, k, str(price + 1))
        K.check(r.startswith("=That click was for an older copy") and snap() == b0, "K43 CMP a price the view did not show: '=', nothing taken (%s)" % r)
        oldp = int(Cfg.CMP_COINS_MINING)
        Cfg.CMP_COINS_MINING = oldp * 2
        r = act("cmpbuy", U, tok, k, str(price))
        K.check(r.startswith("=The price is now") and snap() == b0 and not bool(VCm.bought(k, 0)), "K43 CMP the price changed since the view: '=', nothing taken (%s)" % r)
        Cfg.CMP_COINS_MINING = oldp
        rs = race("cmpbuy", tok, str(price))
        drain()
        a1 = snap()
        K.check(len([x for x in rs if x and x.startswith("+")]) == 1 and b0[2] - a1[2] == price and bool(VCm.bought(k, 0)) and "comp.Mining=1" in a1[4],
                "K43 RACE CMP 4 presses: ONE purchase, the coins taken exactly once (%d), the pd line on disk (%s)" % (b0[2] - a1[2], rs))
        tsum = lambda sn: sum(sn[0].values()) + sum(sn[1].values())
        # ---- Auto-compact toggle
        v = parse(view(U, "Mining"))
        tok = v["h"][1]
        K.eq(v["k"][0], "on", "K43 VIEW compact on")
        r = act("cmptog", U, tok, k, "paused")
        K.check(r.startswith("=That click was for an older copy") and not bool(VCm.paused(k, 0)), "K43 CMPTOG a state the view did not show: '=' (%s)" % r)
        VCm.toggle(U, k, 0)   # paused elsewhere (the /pd page) after the view
        r = act("cmptog", U, tok, k, "on")
        K.check(r.startswith("=Auto-compact for Mining changed since you looked") and bool(VCm.paused(k, 0)), "K43 CMPTOG the state changed since the view: '=', nothing toggled (%s)" % r)
        v = parse(view(U, "Mining"))
        r = act("cmptog", U, v["h"][1], k, "paused")
        K.check(r.startswith("+Auto-compact is on again") and not bool(VCm.paused(k, 0)), "K43 CMPTOG Turn on (%s)" % r)
        v = parse(view(U, "Mining"))
        Cfg.CMP_ON = False
        r = act("cmptog", U, v["h"][1], k, "on")
        K.check(r.startswith("-Auto-compact is switched off") and not bool(VCm.paused(k, 0)), "K43 CMPTOG Server Setup pd.compact.on off: refused (%s)" % r)
        Cfg.CMP_ON = True
        v = parse(view(U, "Mining"))
        r = act("cmptog", U, v["h"][1], k, "on")
        K.check(r.startswith("+Auto-compact paused for Mining") and bool(VCm.paused(k, 0)), "K43 CMPTOG Pause = '+' (done; the page's '=' note) (%s)" % r)
        v = parse(view(U, "Mining"))
        act("cmptog", U, v["h"][1], k, "paused")
        # ---- Shard Link buy (Mining at Legendary)
        s.rar[0] = 3
        for i_, q_ in lcost:
            Pool.add(k, i_, q_)
        p.getInventory()
        v = parse(view(U, "Mining"))
        tok, lp = v["h"][1], int(v["l"][1])
        K.check(v["l"][0] == "buy" and v["l"][2] == "1" and sorted((x[0], int(x[3])) for x in v["li"]) == sorted(lcost) and v["u"][0] == "top",
                "K43 VIEW l: Shard Link buy, ready, the item lines; u: top (%s)" % v["l"])
        b0 = snap()
        old_l = str(Cfg.LINK_COST_MINING)
        Cfg.LINK_COST_MINING = JString(old_l.split(",")[0])
        r = act("lnkbuy", U, tok, k, str(lp))
        K.check(r.startswith("=The Shard Link item cost changed") and snap() == b0, "K43 LNK the item cost changed: '=', nothing taken (%s)" % r)
        Cfg.LINK_COST_MINING = JString(old_l)
        ltot0 = dict((i_, b0[0].get(i_, 0) + b0[1].get(i_, 0)) for i_, _q in lcost)
        rs = race("lnkbuy", tok, str(lp))
        drain()
        a1 = snap()
        ltot1 = dict((i_, a1[0].get(i_, 0) + a1[1].get(i_, 0)) for i_, _q in lcost)
        K.check(len([x for x in rs if x and x.startswith("+")]) == 1 and b0[2] - a1[2] == lp and all(ltot0[i_] - ltot1[i_] == q_ for i_, q_ in lcost)
                and "link.Mining=1" in a1[4], "K43 RACE LNK 4 presses: ONE purchase, coins once (%d) + items once, the pd line on disk (%s)" % (lp, rs))
        v = parse(view(U, "Mining"))
        r = act("lnktog", U, v["h"][1], k, "on")
        K.check(r.startswith("+Shard Link paused") and bool(VL.paused(k, 0)), "K43 LNKTOG Pause = '+' (done; the page's '=' note) (%s)" % r)
        r = act("lnktog", U, v["h"][1], k, "paused")
        K.check(r.startswith("=That click was for an older copy") and bool(VL.paused(k, 0)), "K43 LNKTOG the used token: nothing toggled")
        # ---- refill
        v = parse(view(U, "Mining"))
        r = act("refill", U, v["h"][1], k, "full")
        K.check(r.startswith("+Stack refill: Full inventory") and int(RP.choice(U)) == 1, "K43 REFILL full (%s)" % r)
        v = parse(view(U, "Mining"))
        RP.set(U, 2)
        r = act("refill", U, v["h"][1], k, "hotbar")
        K.check(r.startswith("=Your stack refill choice changed") and int(RP.choice(U)) == 2, "K43 REFILL changed elsewhere since the view: '=' (%s)" % r)
        v = parse(view(U, "Mining"))
        K.check(act("refill", U, v["h"][1], k, "sideways").startswith("-Unknown stack refill choice") and int(RP.choice(U)) == 2, "K43 REFILL a bad word: refused")
        # ---- the bulk moves conserve every item
        for op_ in ("takeall", "depcat", "depevery", "takeall"):
            v = parse(view(U, "Mining"))
            b0 = snap()
            r = act(op_, U, v["h"][1], k)
            drain()
            a1 = snap()
            allk = set(b0[0]) | set(b0[1]) | set(a1[0]) | set(a1[1])
            K.check(r is not None and r[:1] in "+-" and all(b0[0].get(i_, 0) + b0[1].get(i_, 0) == a1[0].get(i_, 0) + a1[1].get(i_, 0) for i_ in allk)
                    and a1[2] == b0[2], "K43 BULK %s: every item counted once (pool %d -> %d, inventory %d -> %d) (%s)"
                    % (op_, sum(b0[0].values()), sum(a1[0].values()), sum(b0[1].values()), sum(a1[1].values()), r))
        K.check(sum(snap()[1].values()) > 0, "K43 BULK ... the last Pick up all moved items to the inventory")
        # ---- null-safety / bad arguments
        K.check(act_.apply(None) is None and act_.apply(JString("x")) is None and act_.apply(jv("up")) is None and act_.apply(jv(U, "up")) is None
                and act_.apply(jv("up", U, JLong(3))) is None and view_.apply(None) is None and view_.apply(jv(U)) is None and view_.apply(jv("x", "Mining")) is None,
                "K43 NULL bad arguments (none, not an array, too short, not a UUID, a token that is not text) = null")
        K.check(act("nope", U, "t", k).startswith("-Unknown pocket action") and act("up", U, None, None) .startswith("=That click was for an older copy"),
                "K43 NULL an unknown op said; no token = older copy")
        Pool.BADPOOL.put(JString(k), JLong(int(__import__("time").time() * 1000)))
        vv = view(U, "Mining")
        K.check(vv is not None, "K43 VIEW with the pool unreadable answers (%s)" % (vv or "")[:60])
        Pool.BADPOOL.remove(JString(k))
        K.notes.append("K43 coins taken %d times; last view: %s" % (coins["takes"], view(U, "Mining").replace("\n", " / ")[:600]))
    finally:
        Bridge.PLAYERS = None
        Cfg.CMP_ON = True


def run_k43(out, jar, scratch, home):
    T35.T089.void_cases = cases43
    T35.T089.run_void(out, jar, scratch, home)


if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("static", run_static), ("k43", run_k43), ("k42", T42.run_k42), ("v41", T41.run_v41), ("p40", T40.run_p40), ("f37", T37.run_f37),
            ("s36", T36.run_s36), ("all35", T35.run_all35), ("bc36", T36.run_bc36), ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
