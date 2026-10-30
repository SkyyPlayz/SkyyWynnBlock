"""Harness for SkyyShards 0.4.16 (the Pocket Dimension opens Enchanted items for shard costs - SkyySacks sacks:fn:takeOpen in payInvBags,
Enchanted counted as 100; tools/shards_0_4_16_patch.py, on top of 0.4.15).
Build first:
    python tools/shards_0_4_16_patch.py && python SkyyShards/build_skyyshards_0.4.16.py
    python SkyyShards/test_skyyshards_0.4.16.py [--keep]

  S16  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand / lock region; no
                continue / break inside any ShStore.LOCK region; 0.4.14's static lock audit (no bridge under the lock) still clean; the Enchanted
                pairs baked into ShCore = SkyySacks 0.8.33's VoidCompact pairs (same tools/skyyench.py formula, read from its build script);
                SkyySacks' sacks:fn:takeOpen is {UUID, String, Number} -> Long (its mode 19)
  OP   open     EXECUTED with a SkyySacks stand-in that copies takeOpen's documented rules (loose first, the fewest Enchanted opened, the change
                loose, all or nothing; put packs the opened ones back; commit makes them final):
                Skyy's example (180 Iron, the Pocket 10 Iron + 3 Enchanted Iron -> the 10 loose + 2 opened, 30 Iron + 1 Enchanted left) through payInvBags, needTxt,
                and a Totem Bench craft; the Map tab 'you have N' (green / red) + a whole sub-upgrade paid inventory + Pocket with an Enchanted
                Wheat opened; every refusal (coins, a refused save) leaves inventory AND Pocket exactly as before; Enchanted bag not carried /
                SkyySacks without takeOpen (0.8.31) / no SkyySacks = 0.4.15's behaviour; a cost naming both a base and its Enchanted item never
                opens it; Add booster takes loose essence first, then opens a Greater Essence of Life; a placed totem's Tier up opens one for
                its Life Essence; the page's booster pick; overflow-safe counts; no stand-in call ever made while holding ShStore.LOCK
  every 0.4.15 phase (LB / LK / NL / CB / OW / FX / 414 / RP / D live start twice) on the 0.4.16 jar, with the hold count checked after
                each; the LB / LK controls still run on the 0.4.14 (leaking) jar
  A verify (-Xverify:all), C compare (0.4.15 -> 0.4.16 = EXPECT), AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.16"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shtake", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.15.jar")
LEAK_JAR = os.path.join(HERE, "SkyyShards-0.4.14.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.15.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_16_patch.py")
SACKS = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.33.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_15", os.path.join(HERE, "test_skyyshards_0.4.15.py"))
T415 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T415)
sys.argv[:] = _argv
T414, T413 = T415.T414, T415.T413
T415.JAR = T414.JAR = T413.JAR = JAR
T415.GEN = T414.GEN = T413.GEN = GEN
T415.SCRATCH = T414.SCRATCH = SCRATCH
T415.VERSION = VERSION   # the compare's scratch jar names
T415.OLD_JAR = LEAK_JAR   # LB / LK: the controls stay on the jar that leaked
T412, T411, T410, T49, T48, T46 = T415.T412, T415.T411, T415.T410, T415.T49, T415.T48, T415.T46
OWNER = T415.OWNER
FK = T415.FK
SUP = T415.SUP
_h, _g, _p = T415._h, T415._g, T415._p
GOOD, BAD = T49.GOOD, T49.BAD


def sacks_pairs():
    """SkyySacks 0.8.33's VoidCompact pairs, by the formula its build script uses (checked to be still there)"""
    import skyyench as EN
    s = open(SACKS, encoding="utf8").read()
    f1 = 'CMP_PAIRS = ([(t[2], EN.PREFIX + t[0]) for t in EN.TABLE if t[1] == "I"]\n             + [(t[2], EN.PREFIX + t[0]) for t in EN.TABLE_ALLOYS if t[1] == "I"])'
    f2 = '_RET_BASE = dict((_r[3], _r[2]) for _i, _r in EN.RETIRED_C1)\nCMP_VPAIRS = [(_RET_BASE[_c], _v, _c) for _c, (_v, _cat) in sorted(EN.VANILLA_ENCH.items())]'
    f3 = 'vcm.addField(CtField.make("public static final String[] BASE = " + _jarr([b for b, _e in CMP_PAIRS]) + ";", vcm))'
    ok = f1 in s.replace("\r\n", "\n") and f2 in s.replace("\r\n", "\n") and f3 in s
    cmp_ = [(t[2], EN.PREFIX + t[0]) for t in EN.TABLE if t[1] == "I"] + [(t[2], EN.PREFIX + t[0]) for t in EN.TABLE_ALLOYS if t[1] == "I"]
    rb = dict((_r[3], _r[2]) for _i, _r in EN.RETIRED_C1)
    vp = [(rb[_c], _v) for _c, (_v, _cat) in sorted(EN.VANILLA_ENCH.items())]
    return ok, cmp_ + vp


# ---------------------------------------------------------------------------------------------------------- S16: static
def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.16 - build script') and g.count('VERSION = "0.4.16"\n') == 1, "S16 header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "LOCK.lock()"):
        K.check(g.count(w) == o.count(w), "S16 no new %s (%d)" % (w, g.count(w)))
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.16: Pocket Dimension costs open Enchanted items (SkyySacks takeOpen); 0.4.15: the shard data lock leak fixed" in g,
            "S16 the ready line names the round (and keeps 0.4.15's)")
    gn = g.replace("\r\n", "\n")
    bad = [(ln, h) for ln, r in T415.regions(gn) for h in T415.jump_out(r)]
    K.check(len(T415.regions(gn)) > 60 and not bad, "S16 no continue / break leaves any of the %d lock regions: %s" % (len(T415.regions(gn)), bad[:3]))
    bad1, n1 = T414.lock_audit(gn)
    K.check(n1 > 60 and not bad1, "S16 0.4.14's static lock audit still clean: %d regions, none reaches a bridge: %s" % (n1, bad1[:3]))
    # the new SkyySacks calls are in methods that hold no lock region at all
    for mname in ("public static long[] payInvBags(", "public static long bagOpen(", "public static boolean openOn(", "public void bagLoad("):
        i = gn.index(mname)
        body = gn[i:gn.index('}""")', i)]
        K.check("LOCK.lock()" not in body, "S16 %s holds no lock region" % mname.split("(")[0].split()[-1])
    pay = gn[gn.index("public static long[] payInvBags("):]
    pay = pay[:pay.index('}""")')]
    K.check('op && opens(ids[i], ids) ? "sacks:fn:takeOpen" : "sacks:fn:take"' in pay and pay.count("bagCall(") == 1, "S16 payInvBags: the Pocket part = takeOpen when offered (a cost naming the Enchanted item too = take)")
    ok, pairs = sacks_pairs()
    K.check(ok, "S16 SkyySacks 0.8.33 still builds its VoidCompact pairs with the formula this harness copies")
    s = open(SACKS, encoding="utf8").read()
    K.check('sbr0.put("sacks:fn:takeOpen", new {PKG}.SackFn(19));' in s and
            "return Long.valueOf(@PKG@.SackBridge.takeOpen((java.util.UUID) a19[0], (String) a19[1], ((Number) a19[2]).longValue()));" in s,
            "S16 SkyySacks' sacks:fn:takeOpen = {UUID, String, Number} -> Long (mode 19), as payInvBags calls it")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S16 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S16 line endings kept")
    K.save()


# ---------------------------------------------------------------------------------------------------------- OP: the Pocket opens Enchanted items
def _sacks(L, pairs):
    """a SkyySacks 0.8.33 stand-in: have = the Pocket's loose counts by id (Enchanted ids too); off = ids whose bag is not carried;
    calls = (fn, id, qty); held = a call made while the caller held ShStore.LOCK"""
    from jpype import JClass, JLong
    br, PyFn, LOCK = L["br"], L["PyFn"], L["ShStore"].LOCK
    PAIR = dict(pairs)
    S = {"have": {}, "off": set(), "ledger": {}, "opn": {}, "committed": {}, "paused": False, "calls": [], "held": [], "craftOpen": True}

    def H(id_):
        return 0 if id_ in S["off"] else S["have"].get(id_, 0)

    def rec(name, a):
        if bool(LOCK.isHeldByCurrentThread()):
            S["held"].append(name)
        S["calls"].append((name, str(a[1]) if len(a) > 1 else "", int(a[2]) if len(a) > 2 else 0))

    def count(a):
        rec("count", a)
        return JLong(-1 if S["paused"] else H(str(a[1])))

    def take(a):
        rec("take", a)
        i_, n_ = str(a[1]), int(a[2])
        if S["paused"]:
            return JLong(0)
        m = min(n_, H(i_))
        S["have"][i_] = S["have"].get(i_, 0) - m
        S["ledger"][i_] = S["ledger"].get(i_, 0) + m
        return JLong(m)

    def take_open(a):
        rec("takeOpen", a)
        i_, n_ = str(a[1]), int(a[2])
        if S["paused"] or i_ in S["off"]:
            return JLong(0)
        e = PAIR.get(i_)
        if e is not None and (e in S["off"] or not S["craftOpen"]):
            e = None
        lo, hi = H(i_), (H(e) if e else 0)
        if lo + 100 * hi < n_:
            return JLong(0)
        if n_ <= lo or e is None:
            S["have"][i_] = lo - n_
            m = 0
        else:
            m = -(-(n_ - lo) // 100)
            S["have"][e] = hi - m
            S["have"][i_] = lo + 100 * m - n_
        S["ledger"][i_] = S["ledger"].get(i_, 0) + n_
        if m:
            S["opn"][i_] = S["opn"].get(i_, 0) + m
        return JLong(n_)

    def put(a):
        rec("put", a)
        i_, n_ = str(a[1]), int(a[2])
        m = min(n_, S["ledger"].get(i_, 0))
        S["ledger"][i_] = S["ledger"].get(i_, 0) - m
        S["have"][i_] = S["have"].get(i_, 0) + m
        o = S["opn"].get(i_, 0)
        if m > 0 and o > 0:   # SkyySacks unoweOpen: all once nothing of the id is owed any more, else floor(returned / 100)
            pb = o if S["ledger"][i_] == 0 else min(o, m // 100)
            e = PAIR[i_]
            S["have"][i_] -= 100 * pb
            S["have"][e] = S["have"].get(e, 0) + pb
            S["opn"][i_] = o - pb
        return JLong(m)

    def commit(a):
        rec("commit", a)
        i_, n_ = str(a[1]), int(a[2])
        m = min(n_, S["ledger"].get(i_, 0))
        S["ledger"][i_] = S["ledger"].get(i_, 0) - m
        S["committed"][i_] = S["committed"].get(i_, 0) + m
        if S["ledger"][i_] == 0:
            S["opn"].pop(i_, None)
        return JLong(m)

    def all_(u):
        S["calls"].append(("all", "", 0))
        if bool(LOCK.isHeldByCurrentThread()):
            S["held"].append("all")
        if S["paused"]:
            return None
        m = JClass("java.util.HashMap")()
        for k_, v_ in S["have"].items():
            if v_ > 0 and k_ not in S["off"]:
                m.put(k_, JLong(v_))
        return m
    FNS = (("count", count), ("take", take), ("put", put), ("commit", commit), ("all", all_), ("takeOpen", take_open))

    def install(open_=True):
        for k_, f_ in FNS:
            if k_ != "takeOpen" or open_:
                br.put("sacks:fn:" + k_, PyFn(f_))
        if not open_:
            br.remove("sacks:fn:takeOpen")

    def remove():
        for k_, _f in FNS:
            br.remove("sacks:fn:" + k_)
    install()
    S["install"], S["remove"] = install, remove
    S["owed"] = lambda: sum(S["ledger"].values()) + sum(S["opn"].values())
    return S


def run_open(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString
    K = HK.Child(out)
    L = T414._fx(os.path.join(scratch, "op"), K)
    St, Isl, Core, Cfg, Page, Tot, Cb = (L[n] for n in ("ShStore", "ShIsl", "ShCore", "ShCfg", "ShPage", "ShTotem", "ShCombat"))
    inv, count, ou, W, p, coins = (L[n] for n in ("inv", "count", "ou", "W", "p", "coins"))
    W_ = T414._world
    _ok, pairs = sacks_pairs()
    S = _sacks(L, pairs)
    IRON, EIRON = "Ingredient_Bar_Iron", "Skyy_Ench_Iron"
    WHEAT, EWHEAT = "Plant_Crop_Wheat_Item", "Skyy_Ench_Wheat"
    LIFE, GLIFE, WATER = "Ingredient_Life_Essence", "Ingredient_Life_Essence_Concentrated", "Ingredient_Water_Essence"
    got = list(zip([str(x) for x in Core.OBASE], [str(x) for x in Core.OENCH]))
    K.check(_ok and got == pairs and len(got) > 100, "OP the %d Enchanted pairs in the jar's ShCore = SkyySacks 0.8.33's VoidCompact pairs (BASE / ENCH + VBASE / VENCH)" % len(got))
    K.check(str(Core.encOf(IRON)) == EIRON and str(Core.encOf(LIFE)) == GLIFE and Core.encOf(EIRON) is None and Core.encOf("Rock_Stone") is None,
            "OP fixture: the pairs (Iron -> Enchanted Iron, Life Essence -> Greater Essence of Life; an Enchanted item opens nothing)")

    def calls(name):
        return [c for c in S["calls"] if c[0] == name]

    def collect_log():
        for root, _d, fs in os.walk(os.path.join(scratch, "op")):
            for f_ in fs:
                if f_ == "collect.log":
                    return open(os.path.join(root, f_), encoding="utf-8").read()
        return ""
    # ---- Skyy's example, straight through payInvBags: 180 Iron; the Pocket 10 Iron + 3 Enchanted Iron, the inventory none
    cs = inv(27, 27, 9)
    Page.TEST_INV = cs
    S["have"] = {IRON: 10, EIRON: 3}
    K.check(int(W_(lambda: Core.haveAll(ou, cs, IRON))) == 310 and int(W_(lambda: Core.bagLoose(ou, IRON))) == 10,
            "OP Skyy's example: 10 Iron + 3 Enchanted Iron in the Pocket count as 310 Iron (loose alone: 10)")
    K.check(W_(lambda: Core.needTxt(ou, cs, [IRON], [JLong(180)])) is None, "OP ... needTxt lets a 180 Iron cost through")
    r = str(W_(lambda: Core.needTxt(ou, cs, [IRON], [JLong(311)])))
    K.check(r == "-You need 311 %s (you have 310)." % str(Tot.pretty(IRON)), "OP ... and refuses 311 with the right count: %s" % r)
    kept = JClass("java.util.ArrayList")()
    bag = JClass("long[]")(1)
    del S["calls"][:]
    took = W_(lambda: Core.payInvBags(ou, cs, [IRON], [JLong(180)], kept, bag))
    K.check(took is not None and int(took[0]) == 0 and int(bag[0]) == 180 and calls("takeOpen") == [("takeOpen", IRON, 180)] and not calls("take"),
            "OP ... payInvBags takes the 180 from the Pocket through sacks:fn:takeOpen (one call): %s" % S["calls"])
    K.check(S["have"] == {IRON: 30, EIRON: 1}, "OP ... the 10 loose first, then 2 Enchanted Iron opened (Skyy: 'just cost 2 enchanted iron ingots'), the change loose: 30 Iron + 1 Enchanted left (310 - 180 = 130; nothing lost): %s" % S["have"])
    lost = str(W_(lambda: Core.refundPaid(ou, cs, [IRON], took, bag, kept)))
    K.check(lost == "" and S["have"] == {IRON: 10, EIRON: 3} and S["owed"]() == 0, "OP ... a refund packs them back: the Pocket exactly as before (%s)" % S["have"])
    took = W_(lambda: Core.payInvBags(ou, cs, [IRON], [JLong(180)], kept, bag))
    ct = str(W_(lambda: Core.commitBags(ou, [IRON], bag)))
    K.check(took is not None and ct == " (from bags: 180 %s)" % IRON and S["have"] == {IRON: 30, EIRON: 1} and S["owed"]() == 0 and S["committed"].get(IRON) == 180,
            "OP ... paid + committed: final, nothing left on the refund ledger: %s %s" % (ct, S["have"]))
    # the inventory part first, as before (Enchanted items in the inventory are not opened)
    T48 = T415.T48
    T48.add_items([(IRON, 100), (EIRON, 100)])
    T48._fill(L, cs, [(IRON, 5), (EIRON, 4)])
    S["have"] = {IRON: 10, EIRON: 3}
    K.check(int(W_(lambda: Core.haveAll(ou, cs, IRON))) == 315, "OP the inventory's Iron counts as before; its Enchanted Iron is not counted (Pocket part only)")
    took = W_(lambda: Core.payInvBags(ou, cs, [IRON], [JLong(180)], kept, bag))
    K.check(took is not None and int(took[0]) == 5 and int(bag[0]) == 175 and count(cs, IRON) == 0 and count(cs, EIRON) == 4 and S["have"] == {IRON: 35, EIRON: 1},
            "OP ... 5 from the inventory, 175 from the Pocket (2 opened, 35 back), the inventory's Enchanted Iron untouched: %s" % S["have"])
    W_(lambda: Core.refundPaid(ou, cs, [IRON], took, bag, kept))
    K.check(count(cs, IRON) == 5 and S["have"] == {IRON: 10, EIRON: 3} and S["owed"]() == 0, "OP ... refunded: inventory and Pocket back exactly")
    for c in cs:
        c.clear()
    # not enough even with opening: nothing moves
    S["have"] = {IRON: 10, EIRON: 1}
    took = W_(lambda: Core.payInvBags(ou, cs, [IRON], [JLong(180)], kept, bag))
    K.check(took is None and S["have"] == {IRON: 10, EIRON: 1} and S["owed"]() == 0, "OP 110 for a 180 cost: refused, nothing moved")
    # the Enchanted item's bag not carried: not counted, not opened
    S["have"] = {IRON: 10, EIRON: 3}
    S["off"] = {EIRON}
    K.check(int(W_(lambda: Core.haveAll(ou, cs, IRON))) == 10, "OP the Enchanted Iron's bag not carried: only the loose 10 count")
    S["off"] = set()
    # an overflow-safe count
    S["have"] = {IRON: 5, EIRON: 92233720368547758}
    K.check(int(W_(lambda: Core.haveAll(ou, cs, IRON))) > 10 ** 15, "OP a huge Enchanted count never overflows into a negative 'you have'")
    # a cost naming BOTH Iron and Enchanted Iron: Iron is paid loose only (the Enchanted ones are the cost's own)
    S["have"] = {IRON: 70, EIRON: 2}
    del S["calls"][:]
    r = W_(lambda: Core.needTxt(ou, cs, [IRON, EIRON], [JLong(60), JLong(1)]))
    bag2 = JClass("long[]")(2)
    took = W_(lambda: Core.payInvBags(ou, cs, [IRON, EIRON], [JLong(60), JLong(1)], kept, bag2))
    K.check(r is None and took is not None and calls("take") == [("take", IRON, 60), ("take", EIRON, 1)] and not calls("takeOpen") and S["have"] == {IRON: 10, EIRON: 1},
            "OP a cost naming Iron AND Enchanted Iron: both plain takes, nothing opened: %s" % S["calls"])
    W_(lambda: Core.refundPaid(ou, cs, [IRON, EIRON], took, bag2, kept))
    S["have"] = {IRON: 10, EIRON: 2}
    r = str(W_(lambda: Core.needTxt(ou, cs, [IRON, EIRON], [JLong(60), JLong(1)])))
    K.check(r.startswith("-You need 60 %s (you have 10" % str(Tot.pretty(IRON))), "OP ... and its check counts Iron loose only: %s" % r)
    # SkyySacks 0.8.31 (no takeOpen): 0.4.15's behaviour
    S["install"](False)
    S["have"] = {IRON: 10, EIRON: 3}
    del S["calls"][:]
    K.check(int(W_(lambda: Core.haveAll(ou, cs, IRON))) == 10, "OP SkyySacks without takeOpen: the Enchanted items do not count (as 0.4.15)")
    took = W_(lambda: Core.payInvBags(ou, cs, [IRON], [JLong(180)], kept, bag))
    K.check(took is None and calls("take") == [("take", IRON, 180)] and S["have"] == {IRON: 10, EIRON: 3} and S["owed"]() == 0,
            "OP ... the plain take, short = everything back (as 0.4.15): %s" % S["calls"])
    S["have"] = {IRON: 200}
    took = W_(lambda: Core.payInvBags(ou, cs, [IRON], [JLong(180)], kept, bag))
    K.check(took is not None and S["have"] == {IRON: 20}, "OP ... enough loose: paid by sacks:fn:take")
    W_(lambda: Core.refundPaid(ou, cs, [IRON], took, bag, kept))
    S["install"](True)
    # ---- a Totem Bench craft costing 180 Iron (Skyy's words were about crafting)
    rid = dict((str(x), i) for i, x in enumerate(Cfg.CRAFT_ID))
    ri = rid["Skyy_Totem_Rain"]
    old_rc = str(Cfg.CRAFT[ri])
    Cfg.CRAFT[ri] = "%s:180;100" % IRON
    S["have"] = {IRON: 10, EIRON: 3}
    pb = Page(ou, W)
    pb.kind = FK
    pb.kSel = ri
    W_(lambda: pb.fillBench(OWNER, cs))
    K.check(str(pb.kTx[0]) == "180 %s (you: 310)" % str(Tot.pretty(IRON)) and str(pb.kCol[0]).lower() == GOOD.lower(),
            "OP the Totem Bench Craft tab: '%s' green (the Pocket's Enchanted Iron counted)" % pb.kTx[0])
    coins["fail"] = True
    r = str(W_(lambda: Core.craftAt(ou, OWNER, FK, ri, cs)))
    coins["fail"] = False
    K.check(r.startswith("-") and S["have"] == {IRON: 10, EIRON: 3} and S["owed"]() == 0, "OP ... craft with the coins refused: the Pocket exactly as before: %s / %s" % (r[:70], S["have"]))
    r = str(W_(lambda: Core.craftAt(ou, OWNER, FK, ri, cs)))
    K.check(r.startswith("+Crafted Rain Totem I") and S["have"] == {IRON: 30, EIRON: 1} and S["owed"]() == 0 and "(from bags: 180 %s)" % IRON in collect_log(),
            "OP ... crafted: 2 Enchanted Iron opened, 30 Iron left loose, committed + logged: %s / %s" % (r[:60], S["have"]))
    # FIX (critic: the page's cost lines counted Iron + 100 x Enchanted Iron even for a cost naming Enchanted Iron too)
    Cfg.CRAFT[ri] = "%s:60,%s:1;100" % (IRON, EIRON)
    S["have"] = {IRON: 10, EIRON: 2}
    W_(lambda: pb.fillBench(OWNER, cs))
    K.check(str(pb.kTx[0]) == "60 %s (you: 10)" % str(Tot.pretty(IRON)) and str(pb.kCol[0]).lower() == BAD.lower(),
            "FIX a cost naming Iron AND Enchanted Iron: the Craft tab line counts Iron loose only, red (as payInvBags pays it): '%s'" % pb.kTx[0])
    K.check(int(pb.havIn(cs, IRON, [IRON, EIRON])) == 10 and int(pb.havIn(cs, IRON, [IRON])) == 210 and int(pb.hav(cs, IRON)) == 210,
            "FIX havIn: loose only when the cost names the Enchanted item too, + 100 x Enchanted otherwise (= hav for a one-id cost)")
    del S["calls"][:]
    r = str(W_(lambda: Core.craftAt(ou, OWNER, FK, ri, cs)))
    K.check(r.startswith("-") and S["have"] == {IRON: 10, EIRON: 2} and S["owed"]() == 0 and not calls("takeOpen"),
            "FIX ... and its craft is refused with nothing moved, matching the red line: %s" % r[:70])
    gfx = open(GEN, encoding="utf8").read()
    K.check(len(re.findall(r"[^.a-zA-Z0-9]hav[(]cs, (ids|bi)\[", gfx)) == 0 and gfx.count("havIn(cs, ids[i], ids)") == 7
            and gfx.count("havIn(cs, ids[j], ids)") == 1 and gfx.count("havIn(cs, bi[j], bi)") == 3,
            "FIX every per-id line of a whole cost counts through havIn (11 lines; single-id lookups keep hav)")
    Cfg.CRAFT[ri] = old_rc
    for c in cs:
        c.clear()
    # ---- the Map tab: a sub-upgrade's 'you have N' + paid inventory + Pocket with an Enchanted Wheat opened
    t0 = int(Isl.LAD0[FK])
    tm0 = str(Cb.subMat(FK, 0))
    T413._set(L, p, "farming.i0.amt", None)
    m0 = Isl.mats(FK, t0, tm0, 0, JLong(1))
    ids0, q0 = [str(x) for x in m0[0]], [int(x) for x in m0[1]]
    K.check(ids0[0] == WHEAT and q0[0] == 16, "OP fixture: Crop Amount 1 costs %s" % list(zip(ids0, q0)))
    S["have"] = {WHEAT: 10, EWHEAT: 1}
    for i_, q_ in zip(ids0[1:], q0[1:]):
        S["have"][i_] = q_
    pg = Page(ou, W)
    pg.kind = FK
    pg.view = 0
    SL = dict((str(n), i) for i, n in enumerate(Page.SLOT_NAME))
    tx = lambda n: str(pg.mTx[SL[n]])
    co = lambda n: str(pg.mCol[SL[n]]).lower()
    W_(lambda: pg.act("mn0", None, None))
    del S["calls"][:]
    W_(lambda: pg.fill(OWNER, cs))
    K.check(tx("RU0I") == "16 Wheat (you have 110)" and co("RU0I") == GOOD.lower(), "OP the Map tab: '%s' green (10 Wheat + 1 Enchanted Wheat in the Pocket)" % tx("RU0I"))
    K.check(len(calls("all")) == 1 and not calls("count") and not calls("takeOpen"), "OP ... still ONE bag read per fill (sacks:fn:all; no count / take): %s" % S["calls"][:4])
    S["install"](False)
    W_(lambda: pg.fill(OWNER, cs))
    K.check(tx("RU0I") == "16 Wheat (you have 10)" and co("RU0I") == BAD.lower(), "OP ... SkyySacks without takeOpen: '%s' red (as 0.4.15)" % tx("RU0I"))
    S["install"](True)
    S["off"] = {EWHEAT}
    W_(lambda: pg.fill(OWNER, cs))
    K.check(tx("RU0I") == "16 Wheat (you have 10)", "OP ... the Enchanted Wheat's bag not carried: '%s'" % tx("RU0I"))
    S["off"] = set()
    T48._fill(L, cs, [(WHEAT, 5)])
    snap = dict(S["have"])
    coins["fail"] = True
    r = str(W_(lambda: Core.buySub(ou, OWNER, FK, 0, 0, cs)))
    coins["fail"] = False
    K.check(r.startswith("-The coins could not be taken") and count(cs, WHEAT) == 5 and S["have"] == snap and S["owed"]() == 0,
            "OP the sub-upgrade, coins refused: inventory + Pocket (the Enchanted Wheat packed back) exactly as before: %s" % r[:70])
    St.FAIL_TEST = True
    r = str(W_(lambda: Core.buySub(ou, OWNER, FK, 0, 0, cs)))
    St.FAIL_TEST = False
    K.check(r.startswith("-It could not be saved") and count(cs, WHEAT) == 5 and S["have"] == snap and S["owed"]() == 0, "OP ... a refused save: everything back: %s" % r[:70])
    r = str(W_(lambda: Core.buySub(ou, OWNER, FK, 0, 0, cs)))
    K.check(r.startswith("+") and count(cs, WHEAT) == 0 and S["have"].get(WHEAT) == 99 and S["have"].get(EWHEAT) == 0 and S["owed"]() == 0
            and str(p.getProperty("farming.i0.amt")) == "1" and ("(from bags: 11 %s" % WHEAT) in collect_log(),
            "OP ... bought: 5 from the inventory, 11 from the Pocket (1 Enchanted Wheat opened, 99 back loose), committed: %s / %s" % (r[:50], S["have"]))
    # ---- Add booster: loose essence first, then a Greater Essence of Life opened
    T413._set(L, p, "farming.i0.totems", "harvest_spirit:1:::0:op0001")
    S["have"] = {GLIFE: 1, WATER: 1}
    r = str(W_(lambda: Core.addBooster(ou, OWNER, FK, 0, 0, cs)))
    K.check(r.startswith("+Booster burning") and S["have"] == {GLIFE: 1, WATER: 0}, "OP Add booster: the loose Water Essence first, the Greater Essence of Life stays closed: %s %s" % (r[:40], S["have"]))
    T413._set(L, p, "farming.i0.totems", "harvest_spirit:1:::0:op0001")
    S["have"] = {GLIFE: 1}
    pt = Page(ou, W)
    pt.kind = FK
    W_(lambda: pt.fill(OWNER, cs))
    K.check(int(pt.hav(cs, LIFE)) == 100 and int(pt.hav2(cs, LIFE, False)) == 0 and int(pt.hav(cs, WATER)) == 0, "OP the page counts 1 Greater Essence of Life as 100 Life Essence (loose only: 0)")
    del S["calls"][:]
    r = str(W_(lambda: Core.addBooster(ou, OWNER, FK, 0, 0, cs)))
    K.check(r.startswith("+Booster burning") and S["have"] == {GLIFE: 0, LIFE: 99} and calls("takeOpen") == [("takeOpen", LIFE, 1)] and S["owed"]() == 0,
            "OP ... only a Greater Essence of Life: it opens (1 Life Essence used, 99 back loose): %s %s" % (r[:40], S["have"]))
    S["have"] = {}
    r = str(W_(lambda: Core.addBooster(ou, OWNER, FK, 0, 0, inv(9))))
    K.check(r.startswith("-") and "you have none" in r, "OP ... none at all: refused as before: %s" % r[:60])
    # ---- a placed totem's Tier up: its Life Essence from a Greater Essence of Life
    T413._set(L, p, "farming.i0.totems", "harvest_spirit:1:::0:op0002")
    S["have"] = T414._Inf()
    S["have"][LIFE] = 0
    S["have"][GLIFE] = 1
    del S["calls"][:]
    r = str(W_(lambda: Core.tierUpPlaced0(ou, OWNER, FK, 0, 0, 1, "harvest_spirit", "op0002", cs)))
    lt = [c for c in calls("takeOpen") if c[1] == LIFE]
    K.check(r.startswith("+") and len(lt) == 1 and S["have"].get(GLIFE) == 0 and S["have"].get(LIFE) == 100 - lt[0][2] and S["owed"]() == 0,
            "OP a placed totem's Tier up: its %d Life Essence came from 1 opened Greater Essence of Life (%d back loose): %s" % (lt[0][2] if lt else -1, S["have"].get(LIFE), r[:60]))
    # ---- the lock rules
    K.check(not S["held"] and not L["held"], "OP no SkyySacks (or other bridge) call was made while holding ShStore.LOCK: %s %s" % (S["held"][:4], L["held"][:4]))
    S["remove"]()
    S["have"] = {IRON: 10, EIRON: 3}
    K.check(int(W_(lambda: Core.haveAll(ou, cs, IRON))) == 0 and W_(lambda: Core.payInvBags(ou, cs, [IRON], [JLong(1)], kept, bag)) is None,
            "OP no SkyySacks: inventory only (nothing to take)")
    Page.TEST_INV = None
    K.save()


def run_players48(out, jar, scratch, home):
    """the map migration's collect.log line names the RUNNING version: 0.4.16 now"""
    SUP(("P one collect.log line with the Undo", "P the map migration's collect.log line"), lambda: T48.run_players(out, jar, os.path.join(scratch, "p48"), home))
    d_ = json.load(open(out))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = d_["ok"], d_["fails"], d_["notes"]
    txt = ""
    for root, _d, fs in os.walk(os.path.join(scratch, "p48")):
        for f_ in fs:
            if f_ == "collect.log":
                txt += open(os.path.join(root, f_), encoding="utf8").read()
    K.check("map migration (SkyyShards 0.4.16) 0a0a0a0a-1111-2222-3333-000000000001" in txt and "Undo:" in txt,
            "P the map migration's collect.log line (running version 0.4.16) with the Undo")
    K.save()


EXPECT = {   # 0.4.15 -> 0.4.16, checked by hand 2026-10-30: the version texts (CfgFn / CfgRows, ShStore migrate* log lines, the ready line in
    # SkyyShardsPlugin.setup); the pairs + helpers (ShCore OBASE / OENCH / encOf / inIds / opens / encAdd / openOn / bagLoose / bagOpen / haveIn,
    # bagCount now + 100 x Enchanted); payInvBags (takeOpen); needTxt + tierUpPlaced0 (haveIn); addBooster (loose first); ShPage bagOpen / bagN /
    # hav2 (bagLoad / hav / haveB) + fillTotemPage (the booster pick)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~m header'],
    'ShCore': ['+f OBASE', '+f OENCH', '+m bagLoose', '+m bagOpen', '+m encAdd', '+m encOf', '+m haveIn', '+m inIds', '+m openOn', '+m opens',
               '~<clinit>', '~m addBooster', '~m bagCount', '~m needTxt', '~m payInvBags', '~m tierUpPlaced0'],
    'ShPage': ['+f bagOpen', '+m bagN', '+m hav2', '+m havIn', '~m bagLoad', '~m fill', '~m fillBenchCraft', '~m fillBenchSide', '~m fillBenchTier', '~m fillBenchUp', '~m fillMap', '~m fillTotemPage', '~m hav', '~m haveB', '~m qSlots', '~m reqMats', '~m tierRows'],   # fix (critic): havIn + the 11 cost lines that call it
    'ShStore': ['~m migrate', '~m migrate2', '~m save'],   # save: same source (0.4.16 does not touch ShStore), its constant-pool indexes moved (as 0.4.15)
    'SkyyShardsPlugin': ['~m setup'],
}
HK.run_compare = T415._compare

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("open", _h(_g(run_open), True)),
                   ("bytecode", T415.run_bytecode), ("leak", T415.run_leak),
                   ("nolock", _h(T414.run_nolock, True)), ("commit", _h(T414.run_commit, True)), ("owed", _h(T414.run_owed, True)), ("fixer", _h(T414.run_fixer, True)),
                   ("lock", _h(_g(T413.run_lock))), ("busy", _h(_g(T413.run_busy, T414.SUP_BZ))), ("place", _h(_g(T413.run_place))), ("walk3", _h(_g(T413.run_walk3))),
                   ("flows3", _h(_g(T413.run_flows3))), ("aura", _h(_g(T413.run_aura))),
                   ("bags", _h(_p(T412.run_bags, lock_ok=True))),
                   ("exec48", _h(_p(T49.run_exec48))), ("exec47", _h(_p(T49.run_exec47, T414.SUP_X47))), ("exec46", _h(_p(T49.run_exec46))),
                   ("centre47", _h(_p(T49.run_centre47))), ("config48", _h(_p(T49.run_config48))), ("mig48", _h(_p(T410.run_mig48))),
                   ("players48", _h(_p(run_players48))), ("geo48", _h(_p(T415.run_geo48))), ("replant", _h(T415.run_replant)), ("config49", _h(_p(T49.run_config))),
                   ("mig49", _h(_p(T49.run_mig))), ("exec49", _h(_p(T49.run_exec))), ("page49", _h(_p(T49.run_page))),
                   ("width", _h(_p(T49.run_width))), ("order", _h(_p(T410.run_order))), ("flows", _h(_p(T410.run_flows))),
                   ("zones", _h(_p(T411.run_zones))), ("balance", _h(_p(T411.run_balance))), ("land", _h(_p(T411.run_land))),
                   ("night", _h(_p(T411.run_night))), ("spawn", _h(_p(T411.run_spawn))), ("buy", _h(_p(T411.run_buy))),
                   ("config", _h(_p(T411.run_config))), ("gate", _h(_p(T411.run_gate))), ("order2", _h(_p(T411.run_order2))),
                   ("live", T411.run_live411)],
           script=__file__, live=(T46.LIVE_SH, "mods/Skyy_SkyyShards"))
