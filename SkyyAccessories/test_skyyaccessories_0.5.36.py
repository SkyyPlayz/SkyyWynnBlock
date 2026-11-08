"""Harness for SkyyAccessories 0.5.36 (Void Charms -> Craft counts and opens Enchanted items; tools/accessories_0_5_36_patch.py). Build first:
    python tools/accessories_0_5_36_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.36.py
    python SkyyAccessories/test_skyyaccessories_0.5.36.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; 0.5.35's patch still regenerates 0.5.35; no new system / command / class; line endings
                 kept; the jar: no entry added / removed, the only changed non-class entry = manifest.json
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.5.35 -> 0.5.36 (AccCraft + the version texts)
  OP    EXECUTED with the real AccCraft.lineRow / row / craft on real engine containers and a stand-in SkyySacks that copies takeOpen's documented
                 rules (0.8.32 changelog item 2): loose only, Enchanted only, loose + Enchanted (Skyy's 30 + 12 Enchanted Lead = 1230/64), inventory +
                 Void + Enchanted, short on one of several inputs (nothing taken), a Void that fails on the second input (the first packed back),
                 no room for the result (refund), takeOpen absent (old take path), a paused Void, a cost naming the Enchanted item too, an id
                 without a pair, a Bench row + a stat accessory row, bags.craftOpen off (the row counts, the click moves nothing), the journal
  LIVE  start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyAccessories (start 2 changes nothing)
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the opening against the LIVE SkyySacks (its own harness covers takeOpen); the real page render.
Scratch: tools/dev/scratch/acc036/h (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "acc036", "h")]
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq
_chd0 = HK.Child


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T534 = _mod(os.path.join(HERE, "test_skyyaccessories_0.5.34.py"), "test_skyyaccessories_0_5_34")
T22 = _mod(os.path.join(HERE, "test_skyyaccessories_0.5.22.py"), "test_skyyaccessories_0_5_22")
HK.run_compare = _cmp0          # back to the plain compare: 0.5.36 changes only manifest.json outside the classes
HK.Child = _chd0
HK.Child.eq = _eq00

VERSION, OLD = "0.5.36", "0.5.35"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyaccessories_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "accessories_0_5_36_patch.py")
PKG = "com.skyy.accessories."
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T534.LIVE_DIR
EXPECT = {
    "AccCraft": ["+f OBASE", "+f OENCH", "+m encAdd", "+m encOf", "+m haveOf", "+m opens", "+m takeVoid", "+m voidHave", "-m takeVoid", "~<clinit>", "~m craft", "~m lineRow", "~m row", "~m voidCopy"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyAccessoriesPlugin": ["~m setup"],          # the version texts
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
FC = ["Skyy_Charm_Furnace_T%d" % t for t in range(1, 6)] + ["Skyy_Charm_Furnace_Eternal"]
COPPER, IRON, THOR, LEAD = "Ingredient_Bar_Copper", "Ingredient_Bar_Iron", "Ingredient_Bar_Thorium", "Ingredient_Bar_Lead_SkyWynn"
E_COP, E_IRON, E_LEAD = "Skyy_Ench_Copper", "Skyy_Ench_Iron", "Skyy_Ench_Lead"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyAccessories 0.5.36 - build script') and g.count('VERSION = "0.5.36"') == 1, "S header + VERSION")
    K.check("KNOWN EDGE, bags.craftOpen OFF" in g, "S the bags.craftOpen edge is written in the script notes")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.eq(g.count('vcall("sacks:fn:count", u, id, -1L)'), 1, "S the Void count of an id is read in one place (voidHave)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(ROOT, "tools", "accessories_0_5_35_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn ^ on), [], "S the jar adds / removes no entry")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


def sacks(W, C):
    """the stand-in SkyySacks: takeOpen = the documented rules of 0.8.32 (loose first, the fewest Enchanted opened, change loose, all or nothing;
    put of a takeOpen'd id packs the opened ones back once nothing of it is owed; commit clears the ledger)"""
    from jpype import JImplements, JOverride, JObject, JClass
    V = {"n": {}, "owe": {}, "opn": {}, "paused": set(), "fail": set(), "calls": [], "noopen": False}

    def L(v):
        return JObject(int(v), "java.lang.Long")

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, mode):
            self.mode = mode

        @JOverride
        def apply(self, a):
            if self.mode == "all":
                m = JClass("java.util.HashMap")()
                for k, v in V["n"].items():
                    if v > 0:
                        m.put(k, L(v))
                return m
            iid = str(a[1])
            if self.mode == "count":
                return L(-1 if iid in V["paused"] else V["n"].get(iid, 0))
            n = int(a[2])
            V["calls"].append((self.mode, iid, n))
            e = C.encOf(iid)
            e = None if e is None else str(e)
            if self.mode == "take":
                t = min(n, V["n"].get(iid, 0))
                V["n"][iid] = V["n"].get(iid, 0) - t
                V["owe"][iid] = V["owe"].get(iid, 0) + t
                return L(t)
            if self.mode == "takeOpen":
                loose, held = V["n"].get(iid, 0), V["n"].get(e, 0) if e and not V["noopen"] else 0          # noopen = bags.craftOpen off: loose only
                if iid in V["fail"] or loose + 100 * held < n:
                    return L(0)
                m = 0 if loose >= n else (n - loose + 99) // 100
                if m:
                    V["n"][e] = held - m
                V["n"][iid] = loose + 100 * m - n
                V["owe"][iid] = V["owe"].get(iid, 0) + n
                V["opn"][iid] = V["opn"].get(iid, 0) + m
                return L(n)
            if self.mode == "put":
                t = min(n, V["owe"].get(iid, 0))
                V["owe"][iid] = V["owe"].get(iid, 0) - t
                V["n"][iid] = V["n"].get(iid, 0) + t
                if t > 0 and V["owe"][iid] == 0 and V["opn"].get(iid, 0) > 0:
                    b = V["opn"].pop(iid)
                    V["n"][e] = V["n"].get(e, 0) + b
                    V["n"][iid] -= 100 * b
                return L(t)
            if self.mode == "commit":
                t = min(n, V["owe"].get(iid, 0))
                V["owe"][iid] = V["owe"].get(iid, 0) - t
                if V["owe"][iid] == 0:
                    V["opn"].pop(iid, None)
                return L(t)
            return L(0)
    fns = dict((m, Fn(m)) for m in ("count", "take", "takeOpen", "put", "commit", "all"))
    for m, f in fns.items():
        W.bridge.put("sacks:fn:" + m, f)
    V["fns"] = fns
    return V


def run_op(out, jar, scratch, _home):
    K = HK.Child(out)
    T22.JAR = jar
    M = T22.m18()
    W = M.World(os.path.join(scratch, "op"))
    C, D, A = W.Craft, W.Defs, W.Acc
    from jpype import JClass
    ids = M.setup_recipes(W)
    ids["wb"] = W.recipe("Skyy_Accessory_Workbench_T1", [("Bench_WorkBench", 1), ("Ingredient_Bar_Copper", 4)], tab="SkyyAccessoryBag")          # 0.5.21: the bag's own category
    ids["spd"] = W.recipe("Skyy_Talisman_Speed_Common", M.SPEED_IN, tab="SkyyAccessoryBag")
    for iid in FC:
        W.item(iid, 1, 900)
    for m_ in (THOR, LEAD, "Ingredient_Bar_Iron", "Ingredient_Bar_Cobalt", "Ingredient_Bar_Chromium_SkyWynn", "Ingredient_Bar_Adamantite", "Ingredient_Bar_Slag_SkyWynn",
               "Ingredient_Bar_Mithril", "Ingredient_Bar_Titanium_SkyWynn", "Ingredient_Bar_Lumen_SkyWynn", E_COP, E_IRON, E_LEAD, "Skyy_Ench_Charcoal", "Skyy_Test_NoPair"):
        W.item(m_, 100, 0)
    W.item("Junk_One", 1, 0)
    V = sacks(W, C)
    FN = V["fns"]

    def fresh(put=(), void=None, name="P", tier=0, fill=None):
        V["n"].clear()
        V["owe"].clear()
        V["opn"].clear()
        V["paused"].clear()
        V["fail"].clear()
        V["noopen"] = False
        del V["calls"][:]
        V["n"].update(void or {})
        inv = W.inv(fill=fill, put=put)
        p, pr, U = W.player(inv, name)
        k = str(U)
        if tier:
            A.putK(U, k, 0, FC[tier - 1])
        return inv, p, pr, U, k

    def row(p, U, k, shown, sub=2):
        for e in C.rowsFor(U, k, p, sub):
            ri = [str(x) for x in C.lineRow(U, k, p, e)]
            if ri[0] == shown:
                return ri
        return None

    def craft(pr, p, U, k, rid):
        return str(C.craft(pr, None, None, p, U, k, rid))

    def state():
        return dict((a, b) for a, b in V["n"].items() if b), dict((a, b) for a, b in V["owe"].items() if b), dict((a, b) for a, b in V["opn"].items() if b)

    def rid(t):
        return FC[t - 1] + "_Recipe_SkyyCharm"

    def mqs(*ids_):
        a = W.JArray(W.MQ)(len(ids_))
        for i, x in enumerate(ids_):
            a[i] = W.mq(x, None, 1)
        return a

    # the table + small helpers
    import skyyench as SE
    K.eq(str(C.encOf(LEAD)), E_LEAD, "T encOf(Lead Ingot) = Enchanted Lead (the pair in Skyy's report)")
    K.eq(str(C.encOf("Ingredient_Life_Essence")), "Ingredient_Life_Essence_Concentrated", "T the vanilla Greater Essence of Life pair")
    K.check(C.encOf(E_LEAD) is None and C.encOf("Skyy_Test_NoPair") is None and C.encOf(None) is None, "T an Enchanted item or an unknown id has no pair")
    K.eq(len(C.OBASE), len(C.OENCH), "T the two pair arrays line up")
    K.check(len(C.OBASE) > 100 and all(str(e).startswith(SE.PREFIX) or str(e) == "Ingredient_Life_Essence_Concentrated" for e in C.OENCH), "T %d pairs, Enchanted ids only" % len(C.OBASE))
    K.eq([int(C.encAdd(30, 12)), int(C.encAdd(5, 0)), int(C.encAdd(5, -1)), int(C.encAdd(0x7fffffffffffff00, 92233720368547))], [1230, 5, 5, 0x7fffffffffffffff], "T encAdd: + 100 each, never negative, never overflows")
    K.check(bool(C.opens(LEAD, mqs(LEAD, THOR))) and not bool(C.opens(LEAD, mqs(LEAD, E_LEAD))) and not bool(C.opens("Skyy_Test_NoPair", mqs("Skyy_Test_NoPair"))), "T opens: yes / the cost also names the Enchanted item = no / no pair = no")

    # O1 Skyy's case: Furnace Charm II, 64 Thorium in the inventory, the Void holds 30 Lead + 13 -> 12 Enchanted Lead as reported
    inv, p, pr, U, k = fresh([("s", 0, THOR, 64)], {LEAD: 30, E_LEAD: 12}, "Skyy", tier=1)
    ri = row(p, U, k, FC[1])
    K.check(ri is not None and "1230/64" in ri[4] and ri[2].endswith("CAN UPGRADE") and "64/64" in ri[4], "O1 Skyy's row: Lead Ingot 1230/64, CAN UPGRADE: %s" % ri)
    r = craft(pr, p, U, k, rid(2))
    K.eq(r, "upgraded to Furnace Charm II in your Void Charms - your Furnace Charm I was used for it", "O1 the upgrade goes through")
    K.eq(state(), ({LEAD: 66, E_LEAD: 11}, {}, {}), "O1 30 loose + ONE opened (11 left), the change 66 back in the Void, the ledger settled")
    K.eq(V["calls"], [("takeOpen", LEAD, 64), ("commit", LEAD, 64)], "O1 paid through takeOpen, then committed")
    K.check(W.bag(U)[0] == FC[1] and W.count(inv, THOR) == 0, "O1 the bag holds T2 and the Thorium is gone")

    # O2 loose only: nothing opened
    inv, p, pr, U, k = fresh([], {COPPER: 32, IRON: 500}, "Loose")
    ri = row(p, U, k, FC[0])
    K.check("32/32" in ri[4] and "500/32" in ri[4] and ri[2].endswith("CAN CRAFT"), "O2 loose only: 32/32 and the true total 500/32: %s" % ri[4])
    r = craft(pr, p, U, k, rid(1))
    K.check(r.startswith("crafted Furnace Charm I"), "O2 crafted: " + r)
    K.eq(state(), ({IRON: 468}, {}, {}), "O2 exact loose amounts used, nothing opened")

    # O3 Enchanted only
    inv, p, pr, U, k = fresh([], {E_COP: 1, E_IRON: 2}, "Ench")
    ri = row(p, U, k, FC[0])
    K.check("100/32" in ri[4] and "200/32" in ri[4] and ri[2].endswith("CAN CRAFT"), "O3 Enchanted only: 100/32, 200/32: %s" % ri[4])
    K.check(craft(pr, p, U, k, rid(1)).startswith("crafted"), "O3 crafted")
    K.eq(state(), ({COPPER: 68, E_IRON: 1, IRON: 68}, {}, {}), "O3 one Enchanted of each opened, the change 68 stays loose")

    # O4 inventory + loose + Enchanted
    inv, p, pr, U, k = fresh([("s", 0, THOR, 64), ("s", 1, LEAD, 10)], {LEAD: 4, E_LEAD: 1}, "Mix", tier=1)
    ri = row(p, U, k, FC[1])
    K.check("114/64" in ri[4], "O4 10 inventory + 4 loose + 1 Enchanted = 114/64: %s" % ri[4])
    K.check(craft(pr, p, U, k, rid(2)).startswith("upgraded"), "O4 upgraded")
    K.eq((W.count(inv, LEAD), state()), (0, ({LEAD: 50}, {}, {})), "O4 inventory paid first, then takeOpen 54: change 50 loose, the Enchanted item used")

    # O5 short on one of two inputs: nothing taken
    inv, p, pr, U, k = fresh([("s", 0, IRON, 10)], {E_COP: 5, IRON: 21}, "Short")
    s0, st0, b0 = W.slots(inv), state(), W.bag(U)
    ri = row(p, U, k, FC[0])
    K.check("500/32" in ri[4] and "31/" in ri[4] and ri[2].endswith("NEEDS MATERIALS"), "O5 row: Copper 500/32, Iron 31/32, NEEDS MATERIALS: %s" % ri[4])
    r = craft(pr, p, U, k, rid(1))
    K.check(r == "not enough materials for Furnace Charm I - nothing was used" and W.slots(inv) == s0 and state() == st0 and W.bag(U) == b0 and V["calls"] == [], "O5 the click takes nothing: " + r)

    # O6 the Void fails on the second input: the first is packed back, the inventory restored
    inv, p, pr, U, k = fresh([("s", 0, IRON, 5)], {E_COP: 3, E_IRON: 1}, "Fail")
    V["fail"].add(IRON)
    s0, st0, b0 = W.slots(inv), state(), W.bag(U)
    r = craft(pr, p, U, k, rid(1))
    K.check(r.startswith("the Void gave 0 of 27") and r.endswith("nothing was used"), "O6 refused: " + r)
    K.eq((W.slots(inv) == s0, state(), W.bag(U) == b0), (True, st0, True), "O6 everything back: the Enchanted Copper packed back, inventory iron restored, nothing owed")
    K.eq(V["calls"], [("takeOpen", COPPER, 32), ("takeOpen", IRON, 27), ("put", COPPER, 32)], "O6 first takeOpen refunded with sacks:fn:put; the failed one owes nothing")

    # O7 no room for the result: a refund after a successful takeOpen
    D.AUTO = False
    inv, p, pr, U, k = fresh([], {E_COP: 1, E_IRON: 1, COPPER: 3}, "Full", fill="Junk_One")
    s0, st0 = W.slots(inv), state()
    r = craft(pr, p, U, k, rid(1))
    K.eq(r, "no room for Furnace Charm I in your inventory - nothing was used", "O7 full inventory refuses")
    K.eq((W.slots(inv) == s0, state()), (True, st0), "O7 the refund packed the Enchanted items back (loose 3 Copper too), nothing owed, no dupe")
    K.check(("commit", COPPER, 32) not in V["calls"] and ("put", COPPER, 32) in V["calls"] and ("put", IRON, 32) in V["calls"], "O7 both refunded, neither committed")
    D.AUTO = True

    # O8 SkyySacks without takeOpen: the old count + the old take
    W.bridge.remove("sacks:fn:takeOpen")
    K.check(not bool(C.opens(LEAD, mqs(LEAD))), "O8 no takeOpen key: opens = no")
    inv, p, pr, U, k = fresh([("s", 0, THOR, 64)], {LEAD: 30, E_LEAD: 12}, "Old", tier=1)
    s0, st0 = W.slots(inv), state()
    ri = row(p, U, k, FC[1])
    K.check("30/64" in ri[4] and ri[2].endswith("NEEDS MATERIALS"), "O8 the row counts loose only: %s" % ri[4])
    r = craft(pr, p, U, k, rid(2))
    K.check(r.startswith("not enough materials") and W.slots(inv) == s0 and state() == st0, "O8 refused, nothing moved: " + r)
    inv, p, pr, U, k = fresh([("s", 0, THOR, 64)], {LEAD: 90}, "Old2", tier=1)
    ri = row(p, U, k, FC[1])
    K.check("64/64" in ri[4] and "90/" not in ri[4], "O8 enough loose: the old need/need cap: %s" % ri[4])
    K.check(craft(pr, p, U, k, rid(2)).startswith("upgraded"), "O8 upgraded")
    K.eq((V["calls"], state()), ([("take", LEAD, 64), ("commit", LEAD, 64)], ({LEAD: 26}, {}, {})), "O8 paid through the plain sacks:fn:take")
    W.bridge.put("sacks:fn:takeOpen", FN["takeOpen"])

    # O9 a paused Void; the Enchanted bag alone not readable
    inv, p, pr, U, k = fresh([("s", 0, THOR, 64), ("s", 1, LEAD, 7)], {LEAD: 30, E_LEAD: 12}, "Paused", tier=1)
    V["paused"].add(LEAD)
    ri = row(p, U, k, FC[1])
    K.check("7/64" in ri[4] and ri[2].endswith("NEEDS MATERIALS"), "O9 paused: only the inventory counts: %s" % ri[4])
    s0, st0 = W.slots(inv), state()
    r = craft(pr, p, U, k, rid(2))
    K.check(r.startswith("not enough materials") and W.slots(inv) == s0 and state() == st0 and V["calls"] == [], "O9 refused, nothing moved: " + r)
    V["paused"].clear()
    V["paused"].add(E_LEAD)
    ri = row(p, U, k, FC[1])
    K.check("37/64" in ri[4], "O9 the Enchanted item's count not readable: loose + inventory only: %s" % ri[4])

    # O10 a custom cost naming both the base and its Enchanted item; a custom cost with no pair
    Props = JClass("java.util.Properties")
    pp = Props()
    pp.setProperty("furnace.cost.T1", COPPER + ":32," + E_COP + ":1")
    D.fcLoad(pp)
    inv, p, pr, U, k = fresh([], {COPPER: 40, E_COP: 2}, "Both")
    ri = row(p, U, k, FC[0])
    K.check("32/32" in ri[4] and "1/1" in ri[4] and ri[2].endswith("CAN CRAFT"), "O10 base + its Enchanted item in one cost: old counting: %s" % ri[4])
    K.check(craft(pr, p, U, k, rid(1)).startswith("crafted"), "O10 crafted")
    K.eq((sorted(c for c in V["calls"] if c[0] != "commit"), state()), ([("take", COPPER, 32), ("take", E_COP, 1)], ({COPPER: 8, E_COP: 1}, {}, {})), "O10 both by the plain take, nothing opened")
    inv, p, pr, U, k = fresh([], {COPPER: 30, E_COP: 1}, "Both2")
    ri = row(p, U, k, FC[0])
    K.check("30/32" in ri[4] and ri[2].endswith("NEEDS MATERIALS"), "O10 ... its Enchanted item is not counted for the base: %s" % ri[4])
    pp = Props()
    pp.setProperty("furnace.cost.T1", "Skyy_Test_NoPair:2")
    D.fcLoad(pp)
    inv, p, pr, U, k = fresh([], {"Skyy_Test_NoPair": 500}, "NoPair")
    ri = row(p, U, k, FC[0])
    K.check("2/2" in ri[4] and "500" not in ri[4], "O10 an id with no pair keeps the need/need cap: %s" % ri[4])
    K.check(craft(pr, p, U, k, rid(1)).startswith("crafted"), "O10 crafted")
    K.eq(V["calls"][0], ("take", "Skyy_Test_NoPair", 2), "O10 ... by the plain take")
    D.fcLoad(Props())

    # O11 the cap of the text, a Bench row and a stat accessory row, the older row()
    inv, p, pr, U, k = fresh([("s", 0, THOR, 64)], {LEAD: 0, E_LEAD: 120}, "Many", tier=1)
    ri = row(p, U, k, FC[1])
    K.check("9999+/64" in ri[4], "O11 over 9999: 9999+/64: %s" % ri[4])
    inv, p, pr, U, k = fresh([("s", 0, "Bench_WorkBench", 1)], {E_COP: 1}, "Bench")
    ri = row(p, U, k, "Skyy_Accessory_Workbench_T1", int(C.subOf("Skyy_Accessory_Workbench_T1")))
    K.check(ri is not None and "100/4" in ri[4] and ri[2].endswith("CAN CRAFT"), "O11 a Bench row counts Enchanted Copper: %s" % ri)
    K.check(craft(pr, p, U, k, ids["wb"]).startswith("crafted"), "O11 Bench accessory crafted")
    K.eq(state(), ({COPPER: 96}, {}, {}), "O11 one Enchanted opened, the change 96 loose")
    inv, p, pr, U, k = fresh([("s", 0, "Ingredient_Crystal_Cyan", 2), ("s", 1, "Ingredient_Feathers_Light", 3)], {E_COP: 1}, "Stat")
    sub = int(C.subOf("Skyy_Talisman_Speed_Common"))
    ri = row(p, U, k, "Skyy_Talisman_Speed_Common", sub)
    K.check(ri is not None and "100/2" in ri[4] and ri[2].endswith("CAN CRAFT"), "O11 a stat accessory row (sub tab %d): %s" % (sub, ri))
    K.check(craft(pr, p, U, k, ids["spd"]).startswith("crafted"), "O11 stat accessory crafted")
    K.eq(state(), ({COPPER: 98}, {}, {}), "O11 ... the same way")
    inv, p, pr, U, k = fresh([], {E_COP: 1}, "OldRow")
    rr = C.row(U, k, p, W.rmap.get(ids["wb"]))
    K.check("100/4" in str(rr[4]), "O11 the older row() agrees: %s" % rr[4])

    # O12 Server Setup bags.craftOpen OFF (no bridge key reports it): the row counts Enchanted items, the click is refused, nothing moves
    inv, p, pr, U, k = fresh([("s", 0, THOR, 64)], {LEAD: 30, E_LEAD: 12}, "Off", tier=1)
    V["noopen"] = True
    s0, st0, b0 = W.slots(inv), state(), W.bag(U)
    ri = row(p, U, k, FC[1])
    K.check("1230/64" in ri[4] and ri[2].endswith("CAN UPGRADE"), "O12 craftOpen off: the row still counts Enchanted (known edge): %s" % ri)
    r = craft(pr, p, U, k, rid(2))
    K.check(r.startswith("the Void gave 0 of 64") and r.endswith("nothing was used"), "O12 the click is refused: " + r)
    K.eq((W.slots(inv) == s0, state(), W.bag(U) == b0, V["calls"]), (True, st0, True, [("takeOpen", LEAD, 64)]), "O12 nothing moved: the Thorium back, the Enchanted Lead not opened, the charm kept, nothing owed")
    inv, p, pr, U, k = fresh([], {COPPER: 32, E_IRON: 1}, "Off2")
    V["noopen"] = True
    s0, st0 = W.slots(inv), state()
    r = craft(pr, p, U, k, rid(1))
    K.check(r.startswith("the Void gave 0 of 32") and r.endswith("nothing was used"), "O12 two inputs, the second needs opening: refused: " + r)
    K.eq((W.slots(inv) == s0, state(), V["calls"]), (True, st0, [("takeOpen", COPPER, 32), ("takeOpen", IRON, 32), ("put", COPPER, 32)]), "O12 ... the loose Copper already taken is put back")

    jr = open(W.LOGF, encoding="utf8").read() if os.path.exists(W.LOGF) else ""
    K.check(jr.count("ROLLBACK") == 4 and "LOST" not in jr, "O the journal: the four rollbacks (O6, O7, O12 twice), nothing lost")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("op", run_op), ("live", T534.run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyAccessories"))
