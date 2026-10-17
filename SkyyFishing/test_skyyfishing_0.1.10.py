"""Harness for SkyyFishing 0.1.10 (round fish0110: the Fishing Bench sees the Void's weighed fish + the Accessory Power readers;
tools/fishing_0_1_10_patch.py). Build first: python tools/fishing_0_1_10_patch.py && python SkyyFishing/build_skyyfishing_0.1.10.py

    python SkyyFishing/test_skyyfishing_0.1.10.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  A / C / AA  verify (-Xverify:all), class compare 0.1.9 -> 0.1.10 (exactly the planned members), engine-access audit
  SAME19 / SAME110  the same bench clicks on 0.1.9 and 0.1.10 WITHOUT the new SkyySacks keys (craft, rod, fit, remove, sell, fillet a Rare
      fish (asks first), sell all twice-click, long list, close): info line, the whole inventory, coin payments and every binding
      IDENTICAL (the two changed texts - Sell all's question, the empty state - normalised and named); 0.1.10's real window keeps the
      0.1.9 checks (check_page, assert_proven, fits 1600 x 980, ONE 32 px tab row, rule 7 tiers, no back / pager text).
  VOID  0.1.10 with a stand-in SkyySacks speaking the contract (sacks:fn:fishList / fishTake / fishPut / commit / all) + coins:fn:add /
      flush: a Void-only list (rows "Void - ..."), sell one exactly once (one payment = the row's price, that entry gone, committed, no op
      file), fillet one (Raw Fish storage-first, entry gone), a Rare Void fish asks first, a refused payment = the fish back in the Void,
      no room = nothing taken, mixed inventory + Void list, Sell all (two clicks) sells the Normal fish of both and leaves the Rare,
      CRASH at every step of a sale (before take, after take, before pay, before the coin flush) and of a fillet (before / after take):
      restart (memory lost, files kept) + replay = the fish is in the Void and nothing paid, or gone and paid exactly once; the
      residual window (after the coin flush, before the op delete) is shown and named. Old SkyySacks (no fish keys): the hint counts
      the Void fish (sacks:fn:all) and the list is the inventory's.
  ACC  FishBridge.accx reads skill:bonus:<uuid>["accessories"] fspd / treasure / dd .fishing (fractions -> %), off / bad = 0, negatives
      ignored; FishRig.withAcc + addGear = added before the fish.cap.* caps; questInit publishes skill:bonus:reads:fish = TRUE.
  R / X / Q / ST  the 0.1.7 harness's phases on this jar (reel, exec, quest, live on a scratch COPY of the live Skyy_SkyyFishing)
Not testable without the game (UNVERIFIED): the real SkyySacks side of the contract (not built yet), the client look of the Void rows.
Scratch: tools/dev/scratch/fish0110/h0110 (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, re, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

VERSION = "0.1.10"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "fish0110", "h0110")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyFishing-%s.jar" % VERSION)]
_spec = importlib.util.spec_from_file_location("test_skyyfishing_0_1_9", os.path.join(HERE, "test_skyyfishing_0.1.9.py"))
T19 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T19)
T17, T15, H = T19.T17, T19.T15, T19.H
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyFishing-0.1.9.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.fishing."
EXPECT = {
    "FishBridge": ["+m voidOn", "+m voidList", "+m voidTake", "+m voidPut", "+m voidTaken", "+m coinsFlush", "+m voidOld", "+m accNum", "+m accx", "~m questInit"],
    "FishRig": ["+m withAcc"], "FishCore": ["~m cast"],
    "FishBench": ["+<clinit>", "+f OPSEQ", "+f VOID_SOLD", "+f VOID_FILLETED", "+f REPLAYED", "+f VOID_MAX", "+m entG", "+m entMm", "+m priceG", "+m filletsG",
                  "+m voidFish", "+m opDir", "+m opSave", "+m opNew", "+m opTok", "+m opStage", "+m opDone", "+m backFromVoid", "+m voidSell", "+m voidFillet",
                  "+m recover", "+m sellAllV"],
    "FishPage": ["+f vIds", "+f vEnts", "~c ", "~m build", "~m handleDataEvent"],
    "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "FishCmds": ["~m admin"], "SkyyFishingPlugin": ["~m setup", "~m shutdown"],
    "FishCfg": ["~m applyAll", "~m seed"],
}
ADDED = []
U1S = "00000000-0000-4000-8000-0000000110f9"
NORM = [("=Sell every Normal fish in your inventory and the Void? Click", "=Sell every Normal fish you carry? Click"),
        ("=You have no Normal fish in your inventory or the Void.", "=You carry no Normal fish.")]


def setup(K, jar, scratch, tag):
    import jpype
    from jpype import JClass, JImplements, JOverride
    T19.JAR_NOW[0] = jar
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Defs, Cfg, Store = P("FishDefs"), P("FishCfg"), P("FishStore")
    ids = set(["Rock_Stone"])
    Mod = JClass("java.lang.reflect.Modifier")
    for f in Defs.class_.getDeclaredFields():
        if not Mod.isStatic(f.getModifiers()):
            continue
        f.setAccessible(True)
        v = f.get(None)
        vals = [v] if isinstance(v, str) else (list(v) if v is not None and str(f.getType().getName()) == "[Ljava.lang.String;" else [])
        for x in vals:
            if x is not None and re.match(r"\A[A-Z][A-Za-z]+_[A-Za-z0-9_]+\Z", str(x)):
                ids.add(str(x))
    T15.item_store(sorted(ids))
    mods = os.path.join(scratch, "mods-" + tag)
    os.makedirs(mods, exist_ok=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg.load(Paths.get(mods))
    Store.start(Paths.get(mods))
    return P, mods


def snap_inv(inv):
    from jpype import JClass
    SH = JClass("java.lang.Short")
    o = []
    for s_ in range(int(inv.getCapacity())):
        st = inv.getItemStack(SH(s_).shortValue())
        if st is None or st.isEmpty():
            continue
        m = st.getMetadata()
        o.append([s_, str(st.getItemId()), int(st.getQuantity()), None if m is None else str(m.toJson())])
    return o


def norm(t):
    for a, b in NORM:
        t = t.replace(a, b)
    return t


# ------------------------------------------------------------------------------------------------ SAME: 0.1.9 vs 0.1.10 without the Void keys
def run_same(out, jar_unused, scratch, _home, which):
    import jpype
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    jar = OLD_JAR if which == "0.1.9" else JAR
    P, mods = setup(K, jar, scratch, "same-" + which)
    Defs, Cfg, Rig, Bench, Brg, Pg, Eng = P("FishDefs"), P("FishCfg"), P("FishRig"), P("FishBench"), P("FishBridge"), P("FishPage"), P("FishEng")
    IS, SIC, SH, UUID, Long = (JClass("com.hypixel.hytale.server.core.inventory.ItemStack"),
                               JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"), JClass("java.lang.Short"),
                               JClass("java.util.UUID"), JClass("java.lang.Long"))
    coins = []

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            coins.append(int(o[1]))
            return Long(1000 + sum(coins))
    Brg.bridge().put("coins:fn:add", Coins())
    u = UUID.fromString(U1S)
    W = {"inv": SIC(SH(36).shortValue()), "t": 1000000}
    Eng.API = T19._api(W)
    inv = W["inv"]
    inv.addItemStack(IS("Ingredient_Stick", 6))
    inv.addItemStack(IS("Ingredient_Fibre", 7))
    inv.addItemStack(IS("SkyyFishing_Hook_Barbed_I", 2))
    rar = [int(x) for x in Defs.SP_RAR]
    common = [i for i in range(len(rar)) if rar[i] == 0]
    rare = [i for i in range(len(rar)) if rar[i] >= int(Cfg.FIL_CONFIRM_R)]
    inv.addItemStack(Rig.makeFish(common[0], 2000, 450, "Skyy"))
    inv.addItemStack(Rig.makeFish(common[1 % len(common)], 2600, 500, "Skyy"))
    inv.addItemStack(Rig.makeFish(rare[0], 8000, 1100, "Skyy"))
    FPT = T19.fake_page_class()
    pg = FPT(T19.player_ref(u))
    trace, win = [], []

    def bindings():
        evs = H.events_of(pg.lastEv)
        tok = str(pg.tok)
        return sorted("%s %s" % (s, re.sub(r"\b%s\b" % re.escape(tok), "TOK", " ".join(re.findall(r'\{"a": [^{}]*\}', t)))) for s, t in evs)

    def click(a, i=None, tok=True):
        d = {"a": a}
        if i is not None:
            d["i"] = str(i)
        if tok:
            d["t"] = str(pg.tok)
        pg.handleDataEvent(None, None, json.dumps(d))
        r = norm(str(pg.info))
        trace.append({"click": [a, i], "info": r, "inv": snap_inv(inv), "coins": list(coins), "tab": int(pg.tab), "bind": bindings()})
        return r

    def keep(what):
        win.append((what, H.cmds_of(pg.lastB), H.events_of(pg.lastEv), str(pg.info)))
    pg.rebuild()
    keep("Parts")
    K.check(click("craft", 0).startswith("+Crafted"), "%s SAME: craft the Wooden rod" % which)
    click("tab", 1, tok=False)
    keep("Rig, one rod")
    click("rod", 0)
    pids = [str(x) for x in pg.partIds]
    K.check(click("fit", pids.index("SkyyFishing_Hook_Barbed_I")).startswith("+Fitted"), "%s SAME: fit the hook" % which)
    K.check(click("rm", 1).startswith("+Took off"), "%s SAME: take it off" % which)
    click("tab", 2, tok=False)
    keep("Fillet and Sell, 3 fish")
    K.check(click("sell", 0).startswith("+Sold"), "%s SAME: sell one" % which)
    fsl = [int(x) for x in pg.fishSlots]
    rr = [n_ for n_, sl in enumerate(fsl) if int(Defs.fishIndex(inv.getItemStack(SH(sl).shortValue()).getItemId())) == rare[0]]
    K.check(click("fil", rr[0]).startswith("=Fillet the"), "%s SAME: a Rare fillet asks first" % which)
    K.check(click("fil", rr[0]).startswith("+Filleted"), "%s SAME: the second click fillets" % which)
    keep("Fillet and Sell, 1 fish")
    K.check(click("sellall").startswith("=Sell every"), "%s SAME: Sell all arms first" % which)
    keep("Sell all armed")
    r = click("sellall")
    K.check(r.startswith("+Sold") and len(coins) == 2, "%s SAME: the second click sells: %s %s" % (which, r, coins))
    keep("Fillet and Sell, now empty")
    K.check(click("sellall").startswith("=Sell every"), "%s SAME: armed again (nothing left)" % which)
    click("sellall")
    for n_ in range(14):
        inv.addItemStack(Rig.makeFish(common[0], 1500 + 10 * n_, 400 + n_, "Skyy"))
    pg.rebuild()
    keep("Fillet and Sell, 14 fish")
    click("close", tok=False)
    json.dump(trace, open(os.path.join(scratch, "same-%s.json" % which), "w"), indent=0)
    if which == "0.1.10":
        T19.window_checks(K, [w for w in win if w[0] != "Fillet and Sell, now empty"], [int(x) for x in Pg.RHS])
        emp = [w for w in win if w[0] == "Fillet and Sell, now empty"][0]
        sets = [(s, d) for ty, s, t, d in emp[1] if ty == "Set"]
        K.check(any(s == "#SkyyFbNoFish.Text" and "No whole fish in your inventory or the Void" in str(d) for s, d in sets),
                "0.1.10: the empty state names the inventory and the Void")
        old = json.load(open(os.path.join(scratch, "same-0.1.9.json")))
        K.eq(len(trace), len(old), "SAME: the same clicks as on 0.1.9")
        for a_, b_ in zip(old, trace):
            what = "%s %s" % tuple(a_["click"])
            K.eq(b_["info"], a_["info"], "SAME %s: the info line (Sell all's question normalised)" % what)
            K.check(b_["inv"] == a_["inv"], "SAME %s: the whole inventory = 0.1.9's" % what)
            K.eq(b_["coins"], a_["coins"], "SAME %s: the coin payments" % what)
            K.eq(b_["bind"], a_["bind"], "SAME %s: every binding" % what)
        K.notes.append("SAME: %d clicks identical to 0.1.9 (normalised: %s)" % (len(trace), NORM))
    P("FishStore").stopIO()
    K.save()


def run_same19(out, jar, scratch, home):
    run_same(out, jar, scratch, home, "0.1.9")


def run_same110(out, jar, scratch, home):
    run_same(out, jar, scratch, home, "0.1.10")


# ------------------------------------------------------------------------------------------------ VOID: the contract stand-in
def run_void(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JString
    K = HK.Child(out)
    P, mods = setup(K, JAR, scratch, "void")
    Defs, Cfg, Rig, Bench, Brg, Pg, Eng, Store = (P("FishDefs"), P("FishCfg"), P("FishRig"), P("FishBench"), P("FishBridge"), P("FishPage"),
                                                   P("FishEng"), P("FishStore"))
    IS, SIC, SH, UUID, Long, HM = (JClass("com.hypixel.hytale.server.core.inventory.ItemStack"),
                                   JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"), JClass("java.lang.Short"),
                                   JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.util.HashMap"))
    br = Brg.bridge()
    u = UUID.fromString(U1S)
    key = str(u)
    bench_dir = os.path.join(mods, "Skyy_SkyyFishing", "bench")
    S = {"void": {}, "owed": {}, "commits": [], "coins": [], "persisted": [], "failpay": False, "hook": None, "snaps": {}, "takes": 0,
         "toks": [], "paused": False, "putfail": False, "lockop": False}

    def hook(point):
        h = S["hook"]
        if h and h == point:
            ops = {}
            if os.path.isdir(bench_dir):
                for n_ in sorted(os.listdir(bench_dir)):
                    ops[n_] = open(os.path.join(bench_dir, n_), "rb").read()
            S["snaps"][point] = {"void": json.loads(json.dumps(S["void"])), "persisted": list(S["persisted"]), "ops": ops, "toks": list(S["toks"]),
                                 "inv": snap_inv(W["inv"])}

    @JImplements("java.util.function.Function")
    class FishList(object):
        @JOverride
        def apply(self, o):
            if S["paused"]:
                return None
            return JArray(JString)(list(S["void"].get(str(o[1]), [])))

    @JImplements("java.util.function.Function")
    class FishTake(object):
        @JOverride
        def apply(self, o):
            hook("take-before")
            id_, e, tok = str(o[1]), str(o[2]), str(o[3])
            l = S["void"].get(id_, [])
            if e not in l or tok in S["toks"]:
                return Long(0)
            l.remove(e)
            S["toks"].append(tok)
            S["owed"][id_] = S["owed"].get(id_, 0) + 1
            S["takes"] += 1
            hook("take-after")
            return Long(1)

    @JImplements("java.util.function.Function")
    class FishPut(object):
        @JOverride
        def apply(self, o):
            hook("put-before")
            id_, e, tok = str(o[1]), str(o[2]), str(o[3])
            if S["lockop"] and os.path.isdir(bench_dir):
                for n_ in os.listdir(bench_dir):          # the op file cannot be rewritten any more (stage=done must fail)
                    os.chmod(os.path.join(bench_dir, n_), 0o444)
            if S["putfail"]:
                return Long(0)
            if S["owed"].get(id_, 0) <= 0 or tok not in S["toks"]:
                return Long(0)
            S["owed"][id_] -= 1
            S["toks"].remove(tok)
            S["void"].setdefault(id_, []).append(e)
            hook("put-after")
            return Long(1)

    @JImplements("java.util.function.Function")
    class FishTaken(object):
        @JOverride
        def apply(self, o):
            if S["paused"]:
                return None
            return JClass("java.lang.Boolean")(str(o[1]) in S["toks"])

    @JImplements("java.util.function.Function")
    class Commit(object):
        @JOverride
        def apply(self, o):
            id_, n = str(o[1]), int(o[2])
            t = min(n, S["owed"].get(id_, 0))
            S["owed"][id_] = S["owed"].get(id_, 0) - t
            S["commits"].append((id_, t))
            return Long(t)

    @JImplements("java.util.function.Function")
    class All(object):
        @JOverride
        def apply(self, o):
            m = HM()
            for id_, l in S["void"].items():
                if l:
                    m.put(id_, Long(len(l)))
            return m

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            hook("add-before")
            if S["failpay"]:
                return None
            S["coins"].append(int(o[1]))
            return Long(sum(S["coins"]))

    @JImplements("java.util.function.Function")
    class Flush(object):
        @JOverride
        def apply(self, o):
            hook("flush-before")
            S["persisted"] = list(S["coins"])
            hook("flush-after")
            return JClass("java.lang.Integer")(1)
    KEYS = {"sacks:fn:fishList": FishList(), "sacks:fn:fishTake": FishTake(), "sacks:fn:fishPut": FishPut(), "sacks:fn:fishTaken": FishTaken(), "sacks:fn:commit": Commit(),
            "sacks:fn:all": All(), "coins:fn:add": Coins(), "coins:fn:flush": Flush()}
    for k_, v_ in KEYS.items():
        br.put(k_, v_)
    W = {"inv": SIC(SH(36).shortValue()), "t": 1000000}
    Eng.API = T19._api(W)
    inv = W["inv"]
    rar = [int(x) for x in Defs.SP_RAR]
    FISH = [str(x) for x in Defs.FISH]
    common = [i for i in range(len(rar)) if rar[i] == 0]
    rare = [i for i in range(len(rar)) if rar[i] >= int(Cfg.FIL_CONFIRM_R)]
    FIL = [str(x) for x in Defs.FILLET]

    def ent(g, mm):
        return "%d,%d,Skyy" % (g, mm)
    c0, c1, r0 = FISH[common[0]], FISH[common[1 % len(common)]], FISH[rare[0]]
    S["void"] = {c0: [ent(2000, 450), ent(3100, 520)], c1: [ent(2600, 500)], r0: [ent(8000, 1100)]}
    K.check(bool(Brg.voidOn()), "VOID: the contract keys present = voidOn")
    FPT = T19.fake_page_class()
    pg = FPT(T19.player_ref(u))

    def click(a, i=None, tok=True):
        d = {"a": a}
        if i is not None:
            d["i"] = str(i)
        if tok:
            d["t"] = str(pg.tok)
        pg.handleDataEvent(None, None, json.dumps(d))
        return str(pg.info)

    def ops():
        return sorted(os.listdir(bench_dir)) if os.path.isdir(bench_dir) else []

    def fish_count(id_):
        return sum(int(st[2]) for st in snap_inv(inv) if st[1] == id_)

    def fil_count():
        return sum(int(st[2]) for st in snap_inv(inv) if st[1] in FIL)
    pg.rebuild()
    click("tab", 2, tok=False)
    vi = [str(x) for x in pg.vIds]
    ve = [str(x) for x in pg.vEnts]
    K.eq(len(pg.fishSlots), 0, "VOID: no fish carried")
    K.eq(sorted(zip(vi, ve)), sorted((k_, e) for k_, l in S["void"].items() for e in l), "VOID-ONLY: the list = every weighed Void fish")
    cmds = H.cmds_of(pg.lastB)
    alltext = " ".join(str(d) for ty, s, t, d in cmds if ty == "Set") + " ".join(str(t) for ty, s, t, d in cmds if t)
    K.check(alltext.count("Void - ") == 4, "VOID-ONLY: each Void row says 'Void - ' (%d)" % alltext.count("Void - "))
    K.check("#SkyyFbNoFish" not in alltext, "VOID-ONLY: no empty state while the Void holds fish")
    hint = [str(d) for ty, s, t, d in cmds if ty == "Set" and s == "#SkyyFbHint.Text"]
    K.check(any("Void fish are listed too" in h for h in hint), "VOID: the hint says Void fish are listed: %s" % hint)
    # ---- sell one exactly once
    j = vi.index(c0)
    e0 = ve[j]
    sp0 = common[0]
    price = int(Bench.priceG(sp0, 2000 if e0.startswith("2000") else 3100, jpype.JLong(int(JClass("java.lang.System").currentTimeMillis()))))
    r = click("sell", j)
    K.check(r.startswith("+Sold the") and "from the Void" in r, "VOID SELL: %s" % r)
    K.eq(len(S["coins"]), 1, "VOID SELL: exactly one payment")
    K.check(abs(S["coins"][0] - price) <= max(1, price // 100), "VOID SELL: paid the row's price (%s vs %s)" % (S["coins"], price))
    K.check(e0 not in S["void"][c0] and len(S["void"][c0]) == 1, "VOID SELL: that entry left the Void, the other stays")
    K.eq(S["commits"], [(c0, 1)], "VOID SELL: committed once")
    K.eq(S["persisted"], S["coins"], "VOID SELL: the purse flushed (coins:fn:flush)")
    K.eq(ops(), [], "VOID SELL: no op file left")
    K.eq(len(pg.vIds), 3, "VOID SELL: the list shows the 3 left")
    r = click("sell", 99)
    K.check(r.startswith("-That fish is gone"), "VOID: a row index past the list = gone: %s" % r)
    # stale: the fish left the Void meanwhile
    vi = [str(x) for x in pg.vIds]; ve = [str(x) for x in pg.vEnts]
    jj = vi.index(c1)
    gone = S["void"][c1].pop()
    r = click("sell", jj)
    K.check(r.startswith("-That fish left the Void") and len(S["coins"]) == 1, "VOID STALE: a fish that left the Void is not sold: %s" % r)
    S["void"][c1].append(gone)
    pg.rebuild()
    # ---- fillet a Normal Void fish (storage-first)
    vi = [str(x) for x in pg.vIds]; ve = [str(x) for x in pg.vEnts]
    jf = vi.index(c1)
    nf = int(Bench.filletsG(2600))
    f0 = fil_count()
    r = click("fil", jf)
    K.check(r.startswith("+Filleted") and "from the Void" in r, "VOID FILLET: %s" % r)
    K.eq(fil_count() - f0, nf, "VOID FILLET: %d Raw Fish given" % nf)
    stor_first = [st for st in snap_inv(inv) if st[1] in FIL]
    K.check(stor_first and stor_first[0][0] == 0, "VOID FILLET: the fillets landed in the first storage slot (storage-first) %s" % stor_first)
    K.eq(S["void"].get(c1, []), [], "VOID FILLET: the fish left the Void")
    K.eq(ops(), [], "VOID FILLET: no op file left")
    # ---- a Rare Void fish asks first
    pg.rebuild()
    vi = [str(x) for x in pg.vIds]
    jr = vi.index(r0)
    r = click("fil", jr)
    K.check(r.startswith("=Fillet the") and "from the Void" in r and len(S["void"][r0]) == 1, "VOID RARE: asks first: %s" % r)
    pg.rebuild()
    # ---- refused payment = back in the Void
    S["failpay"] = True
    vi = [str(x) for x in pg.vIds]; ve = [str(x) for x in pg.vEnts]
    before = json.dumps(S["void"], sort_keys=True)
    r = click("sell", vi.index(c0))
    K.check(r.startswith("-The sale did not go through") and "in the Void" in r, "VOID PAYFAIL: %s" % r)
    K.check(json.dumps(S["void"], sort_keys=True) == before and S["owed"].get(c0, 0) == 0, "VOID PAYFAIL: the same fish is back in the Void")
    K.eq(ops(), [], "VOID PAYFAIL: no op file left")
    S["failpay"] = False
    # ---- no room for fillets = nothing taken
    pg.rebuild()
    inv.clear()          # (the earlier fillets would take the new ones on their stack)
    for s_ in range(int(inv.getCapacity())):
        cur = inv.getItemStack(SH(s_).shortValue())
        if cur is None or cur.isEmpty():
            inv.setItemStackForSlot(jpype.JShort(s_), Rig.makeFish(rare[0], 5000 + s_, 900 + s_, "Filler"))
    free = [s_ for s_ in range(int(inv.getCapacity())) if inv.getItemStack(jpype.JShort(s_)) is None or inv.getItemStack(jpype.JShort(s_)).isEmpty()]
    K.check(not free, "VOID FULL: the inventory is full (%d free, %d stacks)" % (len(free), len(snap_inv(inv))))
    S["void"].setdefault(c1, []).append(ent(2400, 480))
    pg.rebuild()
    vi = [str(x) for x in pg.vIds]
    tk = S["takes"]
    r = click("fil", len(pg.fishSlots) + vi.index(c1))
    K.check(r.startswith("-Make room") and S["takes"] == tk and ent(2400, 480) in S["void"][c1], "VOID FULL: no room = nothing taken: %s" % r)
    inv.clear()
    # ---- mixed inventory + Void, Sell all (two clicks)
    inv.addItemStack(Rig.makeFish(common[0], 1800, 430, "Skyy"))
    inv.addItemStack(Rig.makeFish(rare[0], 7000, 1000, "Skyy"))
    pg.rebuild()
    nI, nV = len(pg.fishSlots), len(pg.vIds)
    K.check(nI == 2 and nV == 3, "MIXED: 2 carried + 3 Void rows (%d + %d)" % (nI, nV))
    cmds = H.cmds_of(pg.lastB)
    subs = [str(d) for ty, s, t, d in cmds if ty == "Set" and "Void - " in str(d)]
    K.eq(len(subs), nV, "MIXED: only the Void rows say Void")
    ncoins = len(S["coins"])
    r = click("sellall")
    K.check(r.startswith("=Sell every Normal fish in your inventory and the Void") and len(S["coins"]) == ncoins, "MIXED SELLALL: the first click arms: %s" % r)
    r = click("sellall")
    normal_void = sum(1 for id_, l in S["void"].items() for e in l if rar[FISH.index(id_)] == 0)
    K.check(r.startswith("+Sold 3 Normal fish (2 from the Void)"), "MIXED SELLALL: the second click sells 1 carried + 2 Void Normal fish: %s" % r)
    K.eq(len(S["coins"]) - ncoins, 3, "MIXED SELLALL: 3 payments")
    K.eq(normal_void, 0, "MIXED SELLALL: no Normal fish left in the Void")
    K.check(len(S["void"][r0]) == 1 and fish_count(FISH[rare[0]]) == 1, "MIXED SELLALL: the Rare fish (Void + carried) stay")
    K.eq(ops(), [], "MIXED SELLALL: no op file left")
    # ---- CRASH at each step: the click runs on (as if the step were the last thing done), the snapshot = what the disk held at that moment;
    # then a restart (coins memory = what was flushed; the Void = its file; the op files as they were) + replay
    def restart_from(sn):
        S["void"] = json.loads(json.dumps(sn["void"]))
        S["owed"] = {}
        S["coins"] = list(sn["persisted"])
        S["persisted"] = list(sn["persisted"])
        S["toks"] = list(sn["toks"])
        if os.path.isdir(bench_dir):
            shutil.rmtree(bench_dir)
        os.makedirs(bench_dir, exist_ok=True)
        for n_, b_ in sn["ops"].items():
            open(os.path.join(bench_dir, n_), "wb").write(b_)
        inv.clear()
        for s_, id_, q, md in sn["inv"]:
            st = IS(id_, q) if md is None else IS(id_, q, JClass("org.bson.BsonDocument").parse(md))
            inv.setItemStackForSlot(jpype.JShort(s_), st)
    for op_, point, expect in (("sell", "take-before", "kept"), ("sell", "take-after", "paid"), ("sell", "add-before", "paid"),
                               ("sell", "flush-before", "paid"), ("sell", "flush-after", "window"),
                               ("sellfail", "put-before", "paid"), ("sellfail", "put-after", "kept"),
                               ("fil", "take-before", "kept"), ("fil", "take-after", "paid")):
        inv.clear()
        e = ent(2222, 444)
        S["void"] = {c0: [e]}
        S["owed"], S["coins"], S["persisted"], S["commits"], S["snaps"], S["toks"] = {}, [], [], [], {}, []
        S["hook"] = point
        S["failpay"] = op_ == "sellfail"
        pg.rebuild()
        vi = [str(x) for x in pg.vIds]
        price = int(Bench.priceG(common[0], 2222, jpype.JLong(int(JClass("java.lang.System").currentTimeMillis()))))
        nfil = int(Bench.filletsG(2222))
        r = click("fil" if op_ == "fil" else "sell", vi.index(c0))
        S["hook"] = None
        S["failpay"] = False
        sn = S["snaps"].get(point)
        what = "CRASH %s at %s" % (op_, point)
        if not K.check(sn is not None and (r.startswith("+") or op_ == "sellfail"), "%s: the step was reached (%s)" % (what, r)):
            continue
        K.check(len(sn["ops"]) == 1, "%s: the op file was on disk at that moment (%d)" % (what, len(sn["ops"])))
        if op_ == "sellfail":
            K.check(b"stage=returned" in list(sn["ops"].values())[0], "%s: the op says returned before the put" % what)
        restart_from(sn)
        n_done = int(Bench.recover(inv, u, key))
        in_void = S["void"].get(c0, []).count(e)
        paid = sum(S["coins"])          # every coin this sale ever put on disk (the purse started empty)
        fil = fil_count()
        if op_ in ("sell", "sellfail"):
            got = "kept" if in_void == 1 and paid == 0 else ("paid" if in_void == 0 and paid == price else "dupe" if in_void == 0 and paid == 2 * price else "BAD")
        else:
            got = "kept" if in_void == 1 and fil == 0 else ("paid" if in_void == 0 and fil == nfil else "BAD")
        if expect == "window":
            K.notes.append("%s: RESIDUAL WINDOW - the purse was written, the op file not yet deleted: the replay pays again (%s; documented in the header)" % (what, got))
            K.check(got == "dupe", "%s: exactly the named residual window - one extra payment, nothing else (got %s)" % (what, got))
        else:
            K.eq(got, expect, "%s: after restart + replay the fish is %s exactly once (void %d, paid %d, fillets %d)" % (what, expect, in_void, paid, fil))
        K.eq(ops(), [], "%s: the replay settled the op file (%d)" % (what, n_done))
        K.eq(int(Bench.recover(inv, u, key)), 0, "%s: a second replay does nothing" % what)
    # ---- fishList / fishTaken null (paused): never an empty Void; the op stays
    inv.clear()
    S["void"] = {c0: [ent(2000, 450)]}
    S["paused"] = True
    pg.rebuild()
    hint = [str(d) for ty, s, t, d in H.cmds_of(pg.lastB) if ty == "Set" and s == "#SkyyFbHint.Text"]
    K.check(len(pg.vIds) == 0 and any("The Void is busy" in h for h in hint), "PAUSED: fishList null = not listed + the hint says busy: %s" % hint)
    os.makedirs(bench_dir, exist_ok=True)
    pend = os.path.join(bench_dir, key + ".1-1.op")
    open(pend, "w").write("u=%s\nkey=%s\nid=%s\ne=%s\nop=sell\nn=50\nitem=\ntok=%s.1-1\nt=1\nstage=taken\n" % (key, key, c0, ent(2000, 450), key))
    K.eq(int(Bench.recover(inv, u, key)), 0, "PAUSED: fishTaken null = the op is kept")
    K.check(os.path.exists(pend), "PAUSED: the op file is still there")
    S["paused"] = False
    nc = len(S["coins"])
    K.eq(int(Bench.recover(inv, u, key)), 1, "PAUSED -> ready: fishTaken FALSE (no such token) = nothing left the Void -> deleted")
    K.check(not os.path.exists(pend) and len(S["coins"]) == nc, "PAUSED -> ready: deleted, nothing paid")
    open(pend, "w").write("u=%s\nkey=other\nid=%s\ne=x\nop=sell\nn=50\nitem=\ntok=%s.1-1\nt=1\nstage=taken\n" % (key, c0, key))
    K.eq(int(Bench.recover(inv, u, "other")), 0, "PROFILE: an op of another (not active) profile is not replayed")
    os.remove(pend)
    # ---- the list cap
    S["void"] = {c0: [ent(1000 + i_, 300 + i_) for i_ in range(230)]}
    pg.rebuild()
    hint = [str(d) for ty, s, t, d in H.cmds_of(pg.lastB) if ty == "Set" and s == "#SkyyFbHint.Text"]
    K.check(len(pg.vIds) == int(Bench.VOID_MAX) == 200 and any("30 more wait in the Void" in h for h in hint), "CAP: 200 Void rows + the hint names 30 more: %s" % hint)
    # ---- re-check fix 1: put fails AND the op cannot be closed = the fish is NOT handed over; the replay pays
    inv.clear()
    S["void"] = {c0: [ent(2300, 470)]}
    S["toks"], S["owed"] = [], {}
    pg.rebuild()
    nc = len(S["coins"])
    S["failpay"], S["putfail"], S["lockop"] = True, True, True
    r = click("sell", 0)
    S["failpay"], S["putfail"], S["lockop"] = False, False, False
    left = ops()
    for n_ in left:
        os.chmod(os.path.join(bench_dir, n_), 0o666)
    K.check("still on its way" in r and fish_count(c0) == 0 and len(left) == 1 and b"stage=returned" in open(os.path.join(bench_dir, left[0]), "rb").read(),
            "FIX1: put fails + op not closable = no fish handed over, the op stays returned: %s %s" % (r, left))
    K.eq(int(Bench.recover(inv, u, key)), 1, "FIX1: the replay settles it (token TRUE)")
    K.check(len(S["coins"]) == nc + 1 and fish_count(c0) == 0 and ops() == [], "FIX1: paid exactly once, no fish in hand, no op left")
    # ---- re-check fix 2: an old op is settled BEFORE a new take
    S["void"] = {c0: [ent(2400, 480)]}
    S["toks"] = [key + ".5-5"]
    os.makedirs(bench_dir, exist_ok=True)
    open(os.path.join(bench_dir, key + ".5-5.op"), "w").write("u=%s\nkey=%s\nid=%s\ne=%s\nop=sell\nn=77\nitem=\ntok=%s.5-5\nt=%d\nstage=taken\n"
                                                             % (key, key, c0, ent(9, 9), key, int(JClass("java.lang.System").currentTimeMillis())))
    pg.rebuild()
    S["toks"] = [key + ".5-5"]
    open(os.path.join(bench_dir, key + ".5-5.op"), "w").write("u=%s\nkey=%s\nid=%s\ne=%s\nop=sell\nn=77\nitem=\ntok=%s.5-5\nt=%d\nstage=taken\n"
                                                             % (key, key, c0, ent(9, 9), key, int(JClass("java.lang.System").currentTimeMillis())))
    nc = len(S["coins"])
    S["hook"] = "take-before"
    S["snaps"] = {}
    r = click("sell", 0)
    S["hook"] = None
    sn = S["snaps"].get("take-before")
    K.check(sn is not None and len(sn["ops"]) == 1 and S["coins"][nc] == 77 and r.startswith("+Sold"),
            "FIX2: the old op was paid (77) and deleted before the new take (only the new op on disk at the take): %s %s" % (r, S["coins"][nc:]))
    K.eq(ops(), [], "FIX2: both settled")
    # ---- old SkyySacks: no fish keys
    for k_ in ("sacks:fn:fishList", "sacks:fn:fishTake", "sacks:fn:fishPut", "sacks:fn:fishTaken"):
        br.remove(k_)
    K.check(not bool(Brg.voidOn()), "OLD SACKS: no keys = voidOn false")
    inv.clear()
    S["void"] = {c0: [ent(2000, 450), ent(2100, 460)], r0: [ent(8000, 1100)]}
    inv.addItemStack(Rig.makeFish(common[0], 1800, 430, "Skyy"))
    pg.rebuild()
    cmds = H.cmds_of(pg.lastB)
    hint = [str(d) for ty, s, t, d in cmds if ty == "Set" and s == "#SkyyFbHint.Text"]
    K.check(any("3 whole fish wait in the Void" in h for h in hint), "OLD SACKS: the hint counts the Void fish: %s" % hint)
    K.check(len(pg.vIds) == 0 and len(pg.fishSlots) == 1, "OLD SACKS: only the carried fish are listed")
    r = click("sellall"); r = click("sellall")
    K.check(r.startswith("+Sold 1 Normal fish for"), "OLD SACKS: Sell all sells the carried fish only: %s" % r)
    K.eq(int(Bench.recover(inv, u, key)), 0, "OLD SACKS: no replay without the keys")
    K.notes.append("VOID: sold %d, filleted %d, replayed %d" % (int(Bench.VOID_SOLD), int(Bench.VOID_FILLETED), int(Bench.REPLAYED)))
    Store.stopIO()
    K.save()


# ------------------------------------------------------------------------------------------------ ACC: the Accessory Power readers
def run_acc(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JDouble
    K = HK.Child(out)
    P, mods = setup(K, JAR, scratch, "acc")
    Brg, Rig, Cfg = P("FishBridge"), P("FishRig"), P("FishCfg")
    UUID, HM, CHM, D = JClass("java.util.UUID"), JClass("java.util.HashMap"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.Double")
    u = UUID.fromString(U1S)
    br = Brg.bridge()
    K.eq([float(x) for x in Brg.accx(u)], [0.0, 0.0, 0.0], "ACC OFF: no skill:bonus = nothing added")
    m = HM()
    m.put("fspd.fishing", D(0.08)); m.put("dd.fishing", D(0.02)); m.put("treasure.fishing", D(0.01)); m.put("dd.mining", D(0.5))
    src = CHM()
    src.put("accessories", m)
    src.put("trees", HM())
    br.put("skill:bonus:" + str(u), src)
    a = [round(float(x), 6) for x in Brg.accx(u)]
    K.eq(a, [8.0, 1.0, 2.0], "ACC ON: { speed 8 %, treasure 1 %, double 2 % } from the accessories source")
    m2 = HM(); m2.put("fspd.fishing", D(-0.5)); m2.put("dd.fishing", D(float("nan"))); m2.put("treasure.fishing", "x")
    src.put("accessories", m2)
    K.eq([float(x) for x in Brg.accx(u)], [0.0, 0.0, 0.0], "ACC BAD: negatives / NaN / text ignored")
    other = HM(); other.put("fspd.fishing", D(0.3))
    src.put("accessories", HM()); src.put("trees", other)
    K.eq([float(x) for x in Brg.accx(u)], [0.0, 0.0, 0.0], "ACC: only the 'accessories' source counts")
    g = JArray(JDouble)([5.0, 1.0, 2.0, 3.0, 40.0])
    w = [float(x) for x in Rig.withAcc(g, JArray(JDouble)([8.0, 1.0, 2.0]))]
    K.eq(w, [13.0, 2.0, 4.0, 3.0, 40.0], "ACC: withAcc adds speed / treasure / double to SkyyGear's, wisdom + pull unchanged")
    K.eq([float(x) for x in g], [5.0, 1.0, 2.0, 3.0, 40.0], "ACC: withAcc leaves the gear array alone")
    caps = [float(x) for x in Cfg.CAP]
    capst = [int(x) for x in Cfg.CAP_STAT]
    st = JArray(JDouble)(12)
    Rig.addGear(st, Rig.withAcc(JArray(JDouble)([0.0, 0.0, 0.0, 0.0, 0.0]), JArray(JDouble)([1000.0, 1000.0, 1000.0])))
    for i_, (cp, si) in enumerate(zip(caps, capst)):
        if si in (int(Rig.ST_SPEED), int(Rig.ST_TREASURE), int(Rig.ST_DOUBLE)):
            K.check(float(st[si]) <= cp, "ACC CAP: stat %d stays at its fish.cap row (%s <= %s)" % (si, float(st[si]), cp))
    K.check(float(st[int(Rig.ST_SPEED)]) > 0.0, "ACC CAP: a huge bonus reaches the cap (speed %s)" % float(st[int(Rig.ST_SPEED)]))
    Brg.questInit()
    K.check(br.get("skill:bonus:reads:fish") == JClass("java.lang.Boolean").TRUE, "ACC: questInit publishes skill:bonus:reads:fish = TRUE")
    src_txt = open(os.path.join(HERE, "build_skyyfishing_0.1.10.py"), encoding="utf8").read()
    K.check(src_txt.count("s.gx = @PKG@.FishRig.withAcc(@PKG@.FishBridge.gearx(c.uuid, stack), @PKG@.FishBridge.accx(c.uuid));") == 1
            and src_txt.index("FishRig.withAcc(@PKG@.FishBridge.gearx") < src_txt.index("@PKG@.FishRig.addGear(s.stat, s.gx);"),
            "ACC: the cast adds the Accessory Power to the gear numbers BEFORE addGear's caps")
    K.check('remove("skill:bonus:reads:fish", Boolean.TRUE)' in src_txt, "ACC: shutdown takes the reader flag back")
    P("FishStore").stopIO()
    K.save()


def run_real(out, jar, scratch, home):
    """THE REAL SkyySacks 0.8.17 keys: SkyySacks' own harness REAL phase (it drives THIS jar's bench through its SackFn / SackPool)"""
    sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_17", os.path.join(ROOT, "SkyySacks", "test_skyysacks_0.8.17.py"))
    keep = list(sys.argv)
    sys.argv = [sys.argv[0]]
    try:
        TS = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(TS)
    finally:
        sys.argv = keep
    TS.run_real(out, TS.JAR, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyFishing", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("same19", run_same19), ("same110", run_same110), ("void", run_void), ("real", run_real), ("acc", run_acc), ("reel", T17.run_reel),
                   ("exec", T15.run_exec), ("quest", T15.run_quest), ("live", T15.run_live)], script=__file__, live=(T15.LIVE_DIR, "Skyy_SkyyFishing"))
