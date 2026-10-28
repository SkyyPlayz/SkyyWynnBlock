"""Harness for SkyyGear 0.3.49 (HOTFIX capfix: a tier-up that gives change no longer throws for a player without a backpack -
tools/gear_0_3_49_patch.py header; phase Z below). Everything else = the 0.3.48 harness (round uprows: every tier-up requirement its own row + Enchanted items pay tier-ups + Smithing weapon families /
class toggle + sectioned tool tooltips - tools/gear_0_3_48_patch.py header).
Build first:
    python tools/gear_0_3_49_patch.py && python SkyyGear/build_skyygear_0.3.49.py
    python SkyyGear/test_skyygear_0.3.49.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.48 jar is the compare base):
  Z  capfix   (engine phase, last) Skyy's click: the lifelong Iron Watering Can -> its next tier through LifePage.tierUp with NO backpack
              (the engine's EmptyItemContainer, capacity 0), costs split over loose inventory items, Enchanted items in the inventory (change
              given back) and the Pocket Dimension (sacks:fn:take / commit), an empty source; success = every cost taken exactly once
              (loose + 100 x Enchanted conserved, the bags' take = the commit), no throw; no room for the change = refused, nothing moved;
              roomWhy / giveChange / activeCopy on capacity-0 sections; the engine's SimpleItemContainer(0) message = the one in Skyy's log
  S  static   the patch re-runs to identical bytes, line endings kept, no new class / command / system; the jar's non-class files = 0.3.48's
              (only manifest.json differs)
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.48 -> 0.3.49 (EXPECT below)
  E  engine   (the 0.2.11 harness's bare server boot: vanilla pack + THIS jar) on real UICommandBuilders, every command list WALKED IN ORDER
              like the client (SkyyShards 0.4.10 phase O): every selector a Set / Append names exists when its command runs, every event
              binding's element exists at the end -
              W1 GearReq.draw: 12 rows = 12 labels (no merged label), more than max = the scroll list; 3 rows = a plain group
              W2 the Upgrade (tools) page, FULL build (Skyy's multitool: Mining / Foraging levels, two collections, the Furnace Charm, every
                 material): one 18 px label a requirement, none merged, green / red
              W3 the Anvil Upgrade card (every requirement + material its own 26 px row; > 3 = scroll list), W4 the Smithing set page (a
                 tier-up row per piece, the full-set total one a line), W5 the /upgrade list row, W6 Smithing > Weapons / Combat armor with the
                 My class / All classes toggle (both states; full builds), the family keys (Wands vs Soul Orbs + Cages, Staffs vs Bo Staffs)
              P  Enchanted items pay: payPlan (Skyy's case: 14 Enchanted Sticks, 0 loose, Stick 150 -> 2 opened, 50 back), haveE, a REAL
                 GearUp.upgrade of a farming armor piece (Skyy's Carrot case: 17 loose + 21 Enchanted; the change case; the bag case through
                 sacks:fn:count / take / commit; a full inventory = refused, nothing moved), the full-set button (17 loose + 21 Enchanted cover
                 the summed cost; loose + 100 x Enchanted is conserved exactly)
              T  the sectioned tooltip of a lifelong-style tool (STATS first, one Fortune line, UPGRADES, ABILITIES, no "^" marker left, plain()
                 without the titles)
  D  live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: every one-time update does nothing, load() twice
              leaves config.properties byte-identical (no saved-data change in this round)
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): how the client draws the new rows / scroll lists and the tooltip segments; SkyySacks' bag sweep filing the
change into the Pocket Dimension.
Scratch: tools/dev/scratch/capfix/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.49"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "capfix", "harness")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.48.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_49_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.48.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
ADDED = []
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"], "GearCfg": ["~m defaultsText"], "SkyyGearPlugin": ["~m setup"],          # the version
    "GearUp": ["~m roomWhy"],          # capfix: no copy of a capacity-0 section
    "GearArmor": ["~m activeCopy"],          # capfix: never a 0-capacity copy
}
U = "00000000-0000-0000-0000-000000000349"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.49 - build script') and g.count('VERSION = "0.3.49"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 0), "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(n for n in nb - na if not n.endswith(".class")), sorted(na - nb)), ([], []), "S no file added or removed")
    chg = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(chg, ["manifest.json"], "S the only non-class change is manifest.json")
    K.check("cs[i].getCapacity() <= 0) continue;" in g and "new @SIC@(cap > 0 ? cap : (short) 1)" in g and g.count("new @SIC@(") == 2, "S capfix: both dynamic SimpleItemContainer copies are guarded")
    K.save()


# ---------------------------------------------------------------------------------------------------------- the client's view of a command list
IDRX = re.compile(r"#([A-Za-z0-9]+)\s*\{")
SELRX = re.compile(r"#([A-Za-z0-9]+)")


def walk(cmds, have=()):
    """the commands IN ORDER, as the client runs them (SkyyShards 0.4.10 phase O): every element a selector names must exist at that moment"""
    have = set(have)
    miss, types, nap, sets = [], set(), 0, {}
    for i, c in enumerate(cmds):
        t = str(c.type)
        types.add(t)
        sel = str(c.selector) if c.selector is not None else ""
        for n in SELRX.findall(sel):
            if n not in have:
                miss.append((i, t, sel))
        if "Append" in t or "Insert" in t:
            nap += 1
            have.update(IDRX.findall(str(c.text) if c.text is not None else ""))
        elif t == "Remove":
            for n in SELRX.findall(sel)[-1:]:
                have.discard(n)
        elif t == "Clear":
            miss.append((i, t, sel + " (Clear: not modelled)"))
        if t == "Set" and sel.endswith(".Text"):
            try:
                sets[sel[1:-5]] = str(c.data.get("0")) if hasattr(c, "data") and c.data is not None else None
            except Exception:
                sets[sel[1:-5]] = None
    return have, miss, types, nap, sets


def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JString, JShort, JImplements, JOverride, JObject, JArray, JLong, JByte
    K = HK.Child(out)
    h211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
    t = open(h211, encoding="utf-8").read()
    t = t[:t.index("def run_engine(out):")]
    esc = os.path.join(scratch, "eng")
    os.makedirs(esc, exist_ok=True)
    argv0 = sys.argv
    sys.argv = [h211, "--jar", jar, "--dir", esc]
    H = {"__name__": "skyygear_h211_lib", "__file__": h211, "__builtins__": __builtins__}
    exec(compile(t, h211 + " (engine boot, library)", "exec"), H)
    sys.argv = argv0
    H.update({"JAR": jar, "SCRATCH": esc, "VERSION": VERSION})
    H["_jvm"]([B.SERVER_JAR, B.JAVASSIST, jar], verify=True, big=True)

    class KC(object):
        def __init__(self, k):
            self.k = k
            self.notes = k.notes

        def check(self, c, w):
            return self.k.check(c, "E boot: " + w)
    E = H["engine_boot"](KC(K))
    us, jf = E["us"], E["jf"]
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Data, Req, Up, LL, Smith, View, Tool, Hub = (P("GearCfg"), P("Gear"), P("GearData"), P("GearReq"), P("GearUp"), P("GearLL"),
                                                              P("GearSmith"), P("GearView"), P("GearTool"), P("GearHubOpen"))
    Props, AL, HM = JClass("java.util.Properties"), JClass("java.util.ArrayList"), JClass("java.util.HashMap")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UUID = JClass("java.util.UUID")
    u = UUID.fromString(U)
    sysp = JClass("java.lang.System").getProperties()
    br = sysp.get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        sysp.put("skyy.bridge", br)
    fresh = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(JClass("java.io.StringReader")(fresh))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    apply()

    @JImplements("java.util.function.Function")
    class PyFn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, a):
            return self.f(a)
    LV = {"Mining": 26, "Foraging": 32, "Farming": 40}
    br.put("skill:fn:level", PyFn(lambda a: JObject(JInt(LV.get(str(a[1]), 0)), "java.lang.Integer")))
    COLL = {"pickaxe": "1|Ore_Iron|Iron Ore|3|100|365", "hatchet": "0|Wood_Maple_Trunk|Maple Log|2|70|156"}
    br.put("coll:fn:tierup", PyFn(lambda a: JString(COLL.get(str(a[1]).split(":")[0], "1|X|X|1|1|1"))))
    BAG = {}
    TOOK = []

    def bag_count(a):
        return JObject(JLong(BAG.get(str(a[1]), 0)), "java.lang.Long")

    def bag_take(a):
        i, n = str(a[1]), int(a[2])
        g = min(n, BAG.get(i, 0))
        BAG[i] = BAG.get(i, 0) - g
        TOOK.append((i, g))
        return JObject(JLong(g), "java.lang.Long")

    def bag_put(a):
        i, n = str(a[1]), int(a[2])
        BAG[i] = BAG.get(i, 0) + n
        return JObject(JLong(n), "java.lang.Long")
    br.put("sacks:fn:count", PyFn(bag_count))
    br.put("sacks:fn:take", PyFn(bag_take))
    br.put("sacks:fn:put", PyFn(bag_put))
    br.put("sacks:fn:commit", PyFn(lambda a: JObject(JLong(int(a[2])), "java.lang.Long")))

    def fld(cls, name):
        k = cls.class_
        while k is not None:
            try:
                f = k.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(name)
    pr = us.allocateInstance(PR.class_)
    fld(PR, "uuid").set(pr, u)
    fld(PR, "username").set(pr, JString("Tester"))

    def page(name):
        C = P(name)
        pg = us.allocateInstance(C.class_)
        k = C.class_
        done = False
        while k is not None and not done:
            for f in k.getDeclaredFields():
                if f.getType() == PR.class_:
                    f.setAccessible(True)
                    f.set(pg, pr)
                    done = True
            k = k.getSuperclass()
        return pg

    def full(pg, what, bad):
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        return walked(b, ev, (), what, bad)

    def walked(b, ev, have, what, bad):
        hv, miss, types, nap, sets = walk(b.getCommands(), have)
        unb = [str(e.selector) for e in ev.getEvents() if any(n not in hv for n in SELRX.findall(str(e.selector)))]
        if miss or unb:
            bad.append((what, miss[:3], unb[:3]))
        return hv, [str(c.text) for c in b.getCommands() if c.text is not None], b

    def texts(b):
        import json as _j
        out_ = {}
        for c in b.getCommands():
            if str(c.type) == "Set" and str(c.selector).endswith(".Text"):
                v = str(c.data) if c.data is not None else ""
                try:
                    o_ = _j.loads(v)
                    if isinstance(o_, dict):
                        o_ = o_.get("0", list(o_.values())[0] if o_ else "")
                    v = o_ if isinstance(o_, str) else str(o_)
                except Exception:
                    pass
                out_[str(c.selector)[1:-5]] = v
        return out_
    bad = []

    def rows(*rs):
        a = AL()
        for t_, s_ in rs:
            Req.add(a, JString(t_), JInt(s_))
        return a
    # ================================================================================== W1 GearReq.draw
    rs12 = rows(*[("Row %d of twelve" % i, i % 2) for i in range(12)])
    b = UCB()
    h = int(Req.draw(b, JString("#SkyyTP"), JString("SkyyTq"), rs12, JInt(18), JInt(14), JInt(5)))
    hv, apps, _b = walked(b, UEB(), ("SkyyTP",), "W1 draw 12", bad)
    K.check(h == 90 and "TopScrolling" in apps[0] and len([x for x in hv if re.match(r"SkyyTqL\d+$", x)]) == 12,
            "W1 12 rows, max 5: a 90 px scroll list holding 12 labels (no merged label): h %d, first %r" % (h, apps[0][:90]))
    b = UCB()
    h3 = int(Req.draw(b, JString("#SkyyTP"), JString("SkyyTr"), rows(("a", 1), ("b", 0), ("c", -1)), JInt(18), JInt(14), JInt(5)))
    hv, apps, _b = walked(b, UEB(), ("SkyyTP",), "W1 draw 3", bad)
    K.check(h3 == 54 and "TopScrolling" not in apps[0] and len([x for x in hv if re.match(r"SkyyTrL\d+$", x)]) == 3, "W1 3 rows = a plain 54 px group, 3 labels")
    # ================================================================================== W2 the Upgrade (tools) page, full build
    # Skyy's screenshot was the multitool (the Multitools pack mod is not in this bare boot): the pickaxe ladder's first step that needs a Furnace
    # Charm (Iron -> Bronze) gives the same kind of list - the skill level, the collection, the charm, every material
    step, best, kk = None, -1, 0
    for k0 in range(len(LL.KIND)):
        starts = [str(LL.KCRUDE[k0])] + (["Tool_Sickle_Harvester_Crude"] if str(LL.KIND[k0]) == "sickle" else [])
        for st0 in starts:
            cur = JString(st0)
            for _i in range(20):
                nx_ = Up.next(cur)
                if nx_ is None:
                    break
                if Gear.item(cur) is not None and Gear.item(nx_) is not None:          # this bare boot lacks some tool items: only loaded ones
                    r_ = AL()
                    Req.levelRow(u, cur, nx_, r_); Req.collRow(u, cur, nx_, r_); Req.costRows(None, u, Up.cost(cur, nx_), r_)
                    sc_ = r_.size() + (10 if int(LL.charmNeed(nx_)) > 0 else 0)
                    if sc_ > best:
                        best, step, kk = sc_, (str(cur), str(nx_)), k0
                cur = nx_
    K.check(step is not None, "W2 a loaded lifelong-tool step (the one with the most requirements, a Furnace Charm step first): %s (kind %d)" % (step, kk))
    reg = Props()
    pk = str(Gear.pkey(u))
    if step:
        reg.setProperty(str(LL.KIND[kk]) + ".id", step[0])
        reg.setProperty(str(LL.KIND[kk]) + ".uid", "harness-uid")
        if "Harvester" in step[0]:
            reg.setProperty("harv", "1")
    LL.REG.put(JString(pk), reg)
    lp = page("LifePage")
    lp.sel = kk
    lp.info = JString("")
    lp.epoch = JString("")
    lp.armK = -1
    hv, apps, lb = full(lp, "W2 LifePage full build", bad)
    tx = texts(lb)
    req = sorted([k for k in tx if re.match(r"SkyyGPReqL\d+$", k)], key=lambda x: int(x[10:]))
    rq = AL()
    to = JString(step[1]) if step else None
    if to is not None:
        Req.levelRow(u, JString(step[0]), to, rq)
        Req.collRow(u, JString(step[0]), to, rq)
        Req.costRows(None, u, Up.cost(JString(step[0]), to), rq)
    want = [str(Req.tx(rq, i)) for i in range(rq.size())]
    got = [tx[k] for k in req]
    K.notes.append("W2 tier row: %s, rows %s" % (step, got))
    K.check(len(req) >= 4 and len(req) >= len(want) and got[:len(want)] == want and not [g_ for g_ in got if ", " in g_ and " : " in g_],
            "W2 the tier row = one label per requirement (%d), the same rows GearReq builds, none merged: %s" % (len(req), got))
    K.check(any("collection" in g_ for g_ in got) and (any("Furnace Charm" in g_ for g_ in got) or (step is None or int(LL.charmNeed(JString(step[1]))) == 0)),
            "W2 the collection (+ the Furnace Charm when the step needs one) are their own rows")
    lab = [a for a in apps if "Label #SkyyGPReqL" in a]
    K.check(lab and all("Height: 18" in a and "FontSize: 14" in a for a in lab), "W2 every requirement label is 18 px / font 14 (the green rows' size)")
    if step:          # a short panel (88 px left): 3 rows show, the rest scroll - still one label each
        lp.reqRoom = 88
        lp.tok = 3
        b, ev = UCB(), UEB()
        lp.tierRow(b, ev, u, None, JString(pk), reg, JInt(kk), JString(step[0]))
        hv2, apps2, _b2 = walked(b, ev, ("SkyyGPanel",), "W2 tierRow (short panel)", bad)
        box = [a_ for a_ in apps2 if "Group #SkyyGPReq " in a_ or "Group #SkyyGPReq{" in a_]
        K.check(box and "TopScrolling" in box[0] and "Height: 54" in box[0] and len([x for x in hv2 if re.match(r"SkyyGPReqL\d+$", x)]) == len(got),
                "W2 a short panel: the %d rows sit in a 54 px scroll list (3 show), one label each: %s" % (len(got), box[:1]))
    okc, badc = str(P("GearDefs").C_OK), str(P("GearDefs").C_BAD)
    K.check(all(((okc in a) if int(Req.st(rq, int(re.search(r"SkyyGPReqL(\d+)", a).group(1)))) > 0 else True) for a in lab[:rq.size()]) and any(badc in a for a in lab),
            "W2 met rows green, missing rows red")
    # ================================================================================== shared inventory helpers
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"
    SECS = (("hotbar", "Hotbar", 9), ("storage", "Storage", 36), ("backpack", "Backpack", 9), ("armor", "Armor", 4), ("utility", "Utility", 4), ("tools", "Tool", 4))

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JByte(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        fld(Cc, "inventory").set(o_, cont)
        return o_

    EIC = JClass("com.hypixel.hytale.server.core.inventory.container.EmptyItemContainer")

    def mkinv(nobp=False):
        inv_ = INV()
        cs_ = {}
        for f_, kind, n_ in SECS:
            cs_[f_] = EIC.INSTANCE if (nobp and f_ == "backpack") else SIC(JShort(n_))
            try:
                fld(INV, f_).set(inv_, comp(kind, cs_[f_]))
            except Exception:
                fld(INV, f_).set(inv_, cs_[f_])
        return inv_, cs_

    def count(cs_, iid):
        n = 0
        for f_, _k, _n in SECS:
            c_ = cs_[f_]
            for i_ in range(int(c_.getCapacity())):
                s_ = c_.getItemStack(JShort(i_))
                if s_ is not None and not s_.isEmpty() and str(s_.getItemId()) == iid:
                    n += int(s_.getQuantity())
        return n

    def put(cs_, sec, slot, iid, q):
        cs_[sec].setItemStackForSlot(JShort(slot), IS(JString(iid), JInt(q)))
    # the farming armor step whose cost has a base with an Enchanted form (Skyy's Lettuce -> Carrot pieces)
    pieces = []
    for crop in ("Lettuce", "Wheat", "Carrot", "Corn"):
        for sl in ("Head", "Chest", "Hands", "Legs"):
            pid = "Armor_Farming_%s_%s" % (crop, sl)
            if Gear.item(JString(pid)) is None:
                continue
            nx = Up.next(JString(pid))
            if nx is None:
                continue
            c = Up.cost(JString(pid), nx)
            if c is None:
                continue
            ids_ = [str(x) for x in c[0]]
            qs_ = [int(x) for x in c[1]]
            en = [(i_, str(Up.enchOf(JString(i_), c[0]))) for i_ in ids_ if Up.enchOf(JString(i_), c[0]) is not None]
            if en:
                pieces.append((pid, str(nx), ids_, qs_, en[0][0], en[0][1]))
    K.check(bool(pieces), "P a farming armor step with an Enchanted-able material exists")
    K.notes.append("P steps: %s" % [(p_[0], p_[1], list(zip(p_[2], p_[3]))) for p_ in pieces[:4]])
    # ================================================================================== P Enchanted items pay
    inv0, cs0 = mkinv()
    put(cs0, "storage", 3, "Skyy_Ench_Stick", 14)
    pp = Up.payPlan(inv0, u, JArray(JString)(["Ingredient_Stick"]), JArray(JInt)([150]))
    K.eq(([str(x) for x in pp[0]], [int(x) for x in pp[1]], [int(x) for x in pp[2]]), (["Ingredient_Stick", "Skyy_Ench_Stick"], [0, 2], [50, 0]),
         "P Skyy's sticks: 14 Enchanted, 0 loose, Stick 150 = 2 Enchanted opened, 50 sticks back")
    K.eq(int(Up.haveE(inv0, u, JString("Ingredient_Stick"), JArray(JString)(["Ingredient_Stick"]))), 1400, "P haveE: 14 Enchanted Sticks count 1,400 sticks")
    K.eq(int(Up.haveE(inv0, u, JString("Ingredient_Stick"), JArray(JString)(["Ingredient_Stick", "Skyy_Ench_Stick"]))), 0,
         "P a cost listing the Enchanted item itself: the base counts loose only (never twice)")
    put(cs0, "storage", 4, "Ingredient_Stick", 60)
    pp = Up.payPlan(inv0, u, JArray(JString)(["Ingredient_Stick"]), JArray(JInt)([150]))
    K.eq(([int(x) for x in pp[1]], [int(x) for x in pp[2]]), ([50, 1, ], [0, 0]), "P 60 loose + Enchanted for 150: 1 opened, 50 loose taken, no change made")
    for case in pieces[:1]:
        pid, nx, ids_, qs_, base, ench = case
        need = qs_[ids_.index(base)]
        others = [(i_, q_) for i_, q_ in zip(ids_, qs_) if i_ != base]

        def setup(loose, ench_n, bag_e=0, full_inv=False):
            inv_, cs_ = mkinv()
            put(cs_, "storage", 0, pid, 1)
            sl_ = 1
            if loose:
                put(cs_, "storage", sl_, base, loose); sl_ += 1
            if ench_n:
                put(cs_, "storage", sl_, ench, ench_n); sl_ += 1
            for i_, q_ in others:
                put(cs_, "storage", sl_, i_, q_); sl_ += 1
            if full_inv:
                for f_ in ("hotbar", "storage", "backpack"):
                    c_ = cs_[f_]
                    for i_ in range(int(c_.getCapacity())):
                        s_ = c_.getItemStack(JShort(i_))
                        if s_ is None or s_.isEmpty():
                            c_.setItemStackForSlot(JShort(i_), IS(JString("Rock_Stone_Cobble"), JInt(1)))
            BAG.clear()
            BAG[ench] = bag_e
            del TOOK[:]
            return inv_, cs_

        def upg(inv_):
            x = P("GearStamp").at(inv_, JInt(1), JInt(0))
            return Up.upgrade(inv_, JInt(1), JInt(0), JString(pid), P("GearForge").fp(x), u, JString("Tester"))
        # Skyy's carrot case (17 loose + 21 Enchanted) for ONE piece
        loose = min(17, need - 1)
        nE = (need - loose + 99) // 100
        inv_, cs_ = setup(loose, 21)
        sh = Up.shortOfU(inv_, u, Up.cost(JString(pid), JString(nx)))
        r = upg(inv_)
        K.check(sh is None and int(r[0]) == 1, "P %s -> %s with %d loose + 21 Enchanted (need %d): upgraded (%s)" % (pid, nx, loose, need, r[1]))
        left = count(cs_, base) + 100 * count(cs_, ench)
        K.eq((count(cs_, ench), left, count(cs_, pid), count(cs_, nx)), (21 - nE, loose + 2100 - need, 0, 1),
             "P the fewest Enchanted opened (%d), loose + 100 x Enchanted conserved, the piece tiered up in place" % nE)
        # the change case: 0 loose, Enchanted only
        inv_, cs_ = setup(0, nE + 1)
        r = upg(inv_)
        K.check(int(r[0]) == 1 and count(cs_, ench) == nE + 1 - ((need + 99) // 100) and count(cs_, base) + 100 * count(cs_, ench) == 100 * (nE + 1) - need,
                "P 0 loose: %d Enchanted opened, the change (%d %s) back in the inventory: %s / %s" % ((need + 99) // 100, ((need + 99) // 100) * 100 - need, base, count(cs_, base), r[1]))
        # the bag case: loose in the inventory, the Enchanted in the bags (sacks:fn:take, then commit)
        inv_, cs_ = setup(loose, 0, bag_e=21)
        r = upg(inv_)
        K.check(int(r[0]) == 1 and (ench, nE) in TOOK and BAG[ench] == 21 - nE, "P Enchanted in the bags: %d taken through sacks:fn:take (%s), %s" % (nE, TOOK, r[1]))
        # a full inventory with change to give: refused, nothing moved
        inv_, cs_ = setup(0, nE + 1, full_inv=True)
        b0 = (count(cs_, ench), count(cs_, pid), count(cs_, base))
        r = upg(inv_)
        K.check(int(r[0]) == 0 and (count(cs_, ench), count(cs_, pid), count(cs_, base)) == b0 and "room" in str(r[1]),
                "P no room for the change: refused before anything moved (%s)" % r[1])
        # not enough: the refusal counts Enchanted too
        inv_, cs_ = setup(0, 0)
        r = upg(inv_)
        K.check(int(r[0]) == 0 and "Enchanted" in str(r[1]), "P short: the refusal names the Enchanted count (%s)" % r[1])
        # W3 the Anvil card on this piece (each requirement + material its own row)
        inv_, cs_ = setup(loose, 21)
        rp = page("ReforgePage")
        b = UCB()
        ev = UEB()
        x = P("GearStamp").at(inv_, JInt(1), JInt(0))
        rp.anUpgrade(b, ev, u, x, inv_)
        hv, apps, _b = walked(b, ev, ("SkyyGActs",), "W3 Anvil card", bad)
        mats = [a for a in hv if re.match(r"SkyyGUMat\d+$", a)]
        rqs = [a for a in hv if re.match(r"SkyyGUReq\d+$", a)]
        K.check(len(mats) == len(ids_) and len(rqs) >= 1 and not [a for a in apps if "more materials" in a],
                "W3 the Anvil card: every material its own row (%d of %d) + the level row(s) %s, no '... and N more'" % (len(mats), len(ids_), rqs))
        K.check(("TopScrolling" in [a for a in apps if "SkyyGUMats" in a][0]) == (len(mats) + len(rqs) > 3), "W3 more than 3 rows = the scroll list")
        # W5 the /upgrade list row of this piece
        upp = page("UpgPage")
        upp.rows = AL()
        upp.rows.add(JArray(JObject)([JObject(JInt(1), "java.lang.Integer"), JObject(JInt(0), "java.lang.Integer"), JString(pid)]))
        upp.tok = 7
        b, ev = UCB(), UEB()
        upp.row(b, ev, u, inv_, JString(pk), reg, JInt(0), upp.rows.get(0))
        hv, apps, _b = walked(b, ev, ("SkyyGUList",), "W5 /upgrade row", bad)
        q = [a for a in hv if re.match(r"SkyyGURow0QL\d+$", a)]
        K.check(len(q) >= len(ids_), "W5 the /upgrade row: one label a requirement (%d)" % len(q))
        # W4 + the full-set button: the farming set page of the next tier, the lower set on the player
        crop = pid.split("_")[2]
        lower = ["Armor_Farming_%s_%s" % (crop, s_) for s_ in ("Head", "Chest", "Hands", "Legs")]
        lower = [i_ for i_ in lower if Gear.item(JString(i_)) is not None and Up.next(JString(i_)) is not None]
        inv_, cs_ = mkinv()
        for i_, l_ in enumerate(lower):
            put(cs_, "storage", i_, l_, 1)
        tot = {}
        for l_ in lower:
            c = Up.cost(JString(l_), Up.next(JString(l_)))
            for i_, q_ in zip([str(x) for x in c[0]], [int(x) for x in c[1]]):
                tot[i_] = tot.get(i_, 0) + q_
        sl_ = 10
        put(cs_, "storage", sl_, base, 17); sl_ += 1
        nEs = max(0, (tot[base] - 17 + 99) // 100) + 1
        put(cs_, "storage", sl_, ench, nEs); sl_ += 1
        for i_, q_ in tot.items():
            if i_ != base:
                put(cs_, "storage", sl_, i_, q_); sl_ += 1
        cat = int(Smith.cat(JString(Up.next(JString(lower[0])))))
        gs = Smith.groups(u, JInt(cat), True)
        grp = None
        for gi in range(gs.size()):
            g_ = gs.get(gi)
            if str(Up.next(JString(lower[0]))) in [str(x) for x in g_[1]]:
                grp = g_
        K.check(grp is not None, "W4 the %s set group is on the Smithing page (cat %d)" % (crop, cat))
        if grp is not None:
            sp = page("SmithPage")
            sp.grp = grp
            sp.hc = HM()
            sp.al = Smith.allowed(u)
            sp.token = 5
            sp.view = 1
            b, ev = UCB(), UEB()
            sp.piecesArea(b, ev, u, inv_)
            hv, apps, _b = walked(b, ev, ("SkyyGMain",), "W4 set page", bad)
            tx = texts(_b)
            cost_rows = sorted([k for k in tx if re.match(r"SkyyGPCostL\d+$", k)])
            prow = [k for k in tx if re.match(r"SkyyGPc\d+WL\d+$", k)]
            K.check(cost_rows and prow and not [tx[k] for k in cost_rows + prow if ", " in tx[k] and "(you have" in tx[k]],
                    "W4 the set page: every piece row + the full-set total one requirement a line: total %s" % [tx[k] for k in cost_rows])
            brow = [tx[k] for k in cost_rows if str(Smith.matName(JString(base))) in tx[k]]
            K.check(brow and "(you have %d)" % (17 + 100 * nEs) in brow[0], "W4 the total counts loose + 100 x Enchanted: %s" % brow)
            sc = Hub.plan(u, inv_, grp, None)
            sh = Req.firstShort(sc[2])
            K.check(sh is None, "W4 Skyy's full-set case: 17 loose + %d Enchanted cover %d %s (short: %s)" % (nEs, tot[base], base, sh))
            b_units = 17 + 100 * nEs
            res = Hub.upSet(inv_, u, pr, sc[1])
            K.check(int(res[0]) == len(lower), "W4 the full set tiered up (%s)" % res[1])
            K.eq(count(cs_, base) + 100 * count(cs_, ench), b_units - tot[base], "W4 loose + 100 x Enchanted after = before - the summed cost (nothing made, nothing lost)")
            # the full SmithPage builds (view 1 on this set, inv null) walk too
            sp2 = page("SmithPage")
            sp2.cat = cat
            sp2.view = 1
            sp2.gkey = grp[0]
            sp2.picked = True
            sp2.info = JString("")
            full(sp2, "W4 SmithPage full build (set view)", bad)
    # ================================================================================== P2 review fix: the change room is counted for ALL change stacks together
    def one_free(cs_):
        n_ = 0
        for f_ in ("hotbar", "storage", "backpack"):
            c_ = cs_[f_]
            for i_ in range(int(c_.getCapacity())):
                s_ = c_.getItemStack(JShort(i_))
                if s_ is None or s_.isEmpty():
                    if n_ == 0:
                        n_ = 1
                        continue
                    c_.setItemStackForSlot(JShort(i_), IS(JString("Rock_Stone_Cobble"), JInt(1)))
    invR, csR = mkinv()
    one_free(csR)
    two = JArray(JString)(["Ingredient_Stick", "Plant_Crop_Carrot_Item"])
    K.check(Up.roomWhy(invR, two, JArray(JInt)([50, 45])) is not None and Up.roomWhy(invR, two, JArray(JInt)([50, 0])) is None,
            "P2 roomWhy: two change stacks + ONE free slot = refused; one change stack = fits (0.3.48 first build said both fit)")
    # Skyy's Iron Harvester -> Bronze, the lifelong tool for real: Enchanted Bronze / Carrot / Sticks only (3 change stacks)
    hv_from, hv_to = "Tool_Sickle_Harvester_Iron", "Tool_Sickle_Harvester_Bronze_SkyWynn"
    if Gear.item(JString(hv_from)) is not None and Gear.item(JString(hv_to)) is not None:
        ks = int(LL.kOf(JString(hv_from)))
        rg = Props()
        rg.setProperty(str(LL.KIND[ks]) + ".id", hv_from)
        rg.setProperty(str(LL.KIND[ks]) + ".uid", "harness-hv")
        rg.setProperty("harv", "1")
        LL.REG.put(JString(pk), rg)
        br.put("acc:smelt:" + U, JString("1|x|x|x|" + pk))
        BDc2, BI2, BS2 = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonInt32"), JClass("org.bson.BsonString")
        dd = BDc2()
        dd.append("ll", BI2(1)); dd.append("lo", BS2(pk)); dd.append("lu", BS2("harness-hv"))
        cst = Up.cost(JString(hv_from), JString(hv_to))
        cids, cqs = [str(x) for x in cst[0]], [int(x) for x in cst[1]]
        K.notes.append("P2 harvester cost: %s" % list(zip(cids, cqs)))

        def hv_setup(room):
            inv_, cs_ = mkinv()
            cs_["storage"].setItemStackForSlot(JShort(0), Data.put(IS(JString(hv_from), JInt(1)), dd, u))
            sl_ = 1
            for i_, q_ in zip(cids, cqs):
                e_ = Up.enchOf(JString(i_), cst[0])
                if e_ is not None:
                    put(cs_, "storage", sl_, str(e_), (q_ + 99) // 100)
                else:
                    put(cs_, "storage", sl_, i_, q_)
                sl_ += 1
            if not room:
                one_free(cs_)
            BAG.clear()
            return inv_, cs_

        def snap(cs_):
            return dict((i_, count(cs_, i_)) for i_ in set(cids + [str(Up.enchOf(JString(i_), cst[0])) for i_ in cids] + [hv_from, hv_to]))
        pp2 = Up.payPlan(hv_setup(True)[0], u, cst[0], cst[1])
        nch = len([c_ for c_ in pp2[2] if int(c_) > 0])
        inv_, cs_ = hv_setup(False)
        b0 = snap(cs_)
        r = Up.upgrade(inv_, JInt(1), JInt(0), JString(hv_from), P("GearForge").fp(cs_["storage"].getItemStack(JShort(0))), u, JString("Tester"))
        K.check(nch >= 2 and int(r[0]) == 0 and snap(cs_) == b0, "P2 the Harvester with %d change stacks + 1 free slot: refused, nothing moved (%s)" % (nch, r[1]))
        inv_, cs_ = hv_setup(True)
        r = Up.upgrade(inv_, JInt(1), JInt(0), JString(hv_from), P("GearForge").fp(cs_["storage"].getItemStack(JShort(0))), u, JString("Tester"))
        a1 = snap(cs_)
        okc = int(r[0]) == 1 and a1[hv_from] == 0 and a1[hv_to] == 1
        for i_, q_ in zip(cids, cqs):
            e_ = Up.enchOf(JString(i_), cst[0])
            if e_ is not None:
                okc = okc and a1[i_] + 100 * a1[str(e_)] == 100 * ((q_ + 99) // 100) - q_
        K.check(okc, "P2 Skyy's Harvester with room: Iron -> Bronze, every Enchanted cost paid with the fewest opened, the change back (%s, %s)" % (r[1], a1))
        LL.REG.put(JString(pk), reg)
    else:
        K.check(False, "P2 the Iron / Bronze Harvesters are loaded")
    # W5 a tall /upgrade row (many rows on the list = the base 70 px height, more requirements than fit = the row grows to them)
    if pieces:
        upp = page("UpgPage")
        upp.rows = AL()
        inv_, cs_ = mkinv()
        put(cs_, "storage", 0, pieces[0][0], 1)
        for _i in range(12):
            upp.rows.add(JArray(JObject)([JObject(JInt(1), "java.lang.Integer"), JObject(JInt(0), "java.lang.Integer"), JString(pieces[0][0])]))
        upp.tok = 8
        b, ev = UCB(), UEB()
        upp.row(b, ev, u, inv_, JString(pk), reg, JInt(0), upp.rows.get(0))
        hv, apps, _b = walked(b, ev, ("SkyyGUList",), "W5 tall /upgrade row", bad)
        nq = len([a_ for a_ in hv if re.match(r"SkyyGURow0QL\d+$", a_)])
        rh = int(P("GearHub").growUp(JInt(12)))
        m_ = re.search(r"Group #SkyyGURow0 \{ Anchor: \(Height: (\d+)\)", apps[0])
        K.notes.append("W5 tall row: %d requirement rows, height %s, list row %d" % (nq, m_.group(1) if m_ else None, rh))
        K.check(m_ is not None and 52 + nq * 18 > rh and int(m_.group(1)) == 52 + nq * 18,
                "W5 the tall row: %d requirement rows, row height %s (list rows %d px)" % (nq, m_.group(1) if m_ else None, rh))
    # ================================================================================== W6 Smithing > Weapons: families + the class toggle
    K.eq([str(Smith.famKey(JString(i_))) for i_ in ("Weapon_Wand_Wood", "Weapon_Wand_SoulOrb", "Weapon_Wand_SoulCage_Copper", "Weapon_Staff_Iron", "Weapon_Staff_Bo_Bamboo", "Weapon_Sword_Iron")],
         ["Weapon_Wand", "Weapon_Wand_Soul", "Weapon_Wand_Soul", "Weapon_Staff", "Weapon_Staff_Bo", "Weapon_Sword"], "W6 the family keys: Wands / Soul Orbs + Cages / Staffs / Bo Staffs apart")
    K.eq([str(Smith.groupName(JString(k_), JInt(2))) for k_ in ("Weapon_Wand", "Weapon_Wand_Soul", "Weapon_Staff_Bo")], ["Wands", "Soul Orbs + Cages", "Bo Staffs"], "W6 their card names")
    for cat in (2, 0):
        for allv in (False, True):
            Smith.setPref(u, JString("gear.smithShowAll"), allv)
            sp = page("SmithPage")
            sp.cat = cat
            sp.view = 0
            sp.picked = True
            sp.info = JString("")
            hv, apps, _b = full(sp, "W6 Smithing cat %d all %s" % (cat, allv), bad)
            if not bool(Smith.shown(JInt(cat))):
                continue
            K.check("SkyyGFltMine" in hv and "SkyyGFltAll" in hv, "W6 cat %d (all %s): the My class / All classes toggle is on the page" % (cat, allv))
            lit = [a for a in apps if "SkyyGFltAll" in a][0]
            K.check(("Primary.png" in lit.split("SkyyGFltAll")[1][:400] or "#2c4a66" in lit.split("SkyyGFltAll")[1][:400]) == allv, "W6 the lit button follows the switch (all %s)" % allv)
    Smith.setPref(u, JString("gear.smithShowAll"), False)
    # ================================================================================== T the sectioned tooltip
    hid = [i_ for i_ in ("Tool_Sickle_Harvester_Iron", "Tool_Hoe_Iron", "Tool_Pickaxe_Iron") if Gear.item(JString(i_)) is not None]
    K.check(bool(hid), "T a tool to show")
    BDc, BI, BA, BS = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonInt32"), JClass("org.bson.BsonArray"), JClass("org.bson.BsonString")
    tid = hid[0] if hid else None
    k_ = int(LL.kOf(JString(tid))) if tid else -1
    for rolled in (True, False):
        if tid is None or k_ < 0:
            break
        d = BDc()
        d.append("ll", BI(1)); d.append("lo", BS(pk)); d.append("lu", BS("harness-uid"))
        d.append("tr", BI(1 if rolled else 0))
        ms = BA()
        ms.add(Data.mod(JString(str(Tool.fortKey(JInt(int(Tool.fam(JString(tid))))))), JInt(11)))
        ms.add(Data.mod(JString(str(Tool.wisKey(JInt(int(Tool.fam(JString(tid))))))), JInt(11)))
        d.append("mods", ms)
        reg.setProperty(str(LL.KIND[k_]) + ".up.fort", "5")
        reg.setProperty(str(LL.KIND[k_]) + ".up.swing", "3")
        txt, col = AL(), AL()
        View.lines(JString(tid), d, u, txt, col)
        tl = [str(x) for x in txt]
        cl = [None if c_ is None else str(c_) for c_ in col]
        K.notes.append("T %s (rolled %s): %s" % (tid, rolled, list(zip(tl, cl))[:40]))
        K.check("STATS" in tl and not [c_ for c_ in cl if c_ and c_.startswith("^")], "T %s: a STATS section, no section marker left in a colour" % tid)
        si = tl.index("STATS") if "STATS" in tl else -1
        fort = [x for x in tl if "Fortune" in x and "Lv " not in x]
        K.check(len(fort) == (1 if rolled else 2) and all(tl.index(x) > si for x in fort),
                "T %s rolled %s: %s Fortune line(s) under STATS (a rolled tool's +11 is inside its total; an unrolled one keeps the row): %s" % (tid, rolled, 1 if rolled else 2, fort))
        K.check(fort and cl[tl.index(fort[0])].startswith("&"), "T %s: the Fortune total is colour coded (name / bold green value / dim rest)" % tid)
        ui = tl.index("UPGRADES") if "UPGRADES" in tl else -1
        ai = tl.index("ABILITIES") if "ABILITIES" in tl else -1
        K.check(si < ui < ai and [x for x in tl[ui:ai] if "Lv 5" in x and "Fortune" in x], "T %s: STATS, then UPGRADES (Fortune Lv 5 + what it gives), then ABILITIES" % tid)
        K.check(all(tl.index(x) > ai for x in tl if x.startswith(("Cuts bushes", "Tills soil", "Lifelong "))), "T %s: what it does sits under ABILITIES" % tid)
        cd_ = [i_ for i_, x in enumerate(tl) if x.startswith("Can't be dropped")]
        K.check(cd_ and cd_[0] > ai and cl[cd_[0]] == str(P("GearDefs").C_GRAY), "T %s: 'Can't be dropped' sits at the bottom, dim (after ABILITIES)" % tid)
        pl = [str(x) for x in View.plain(JString(tid), d, u)]
        K.check(not [x for x in pl if x in ("STATS", "UPGRADES", "ABILITIES")] and not [x for x in pl if "" in x], "T %s: plain() has no section titles / joints" % tid)
    if tid:
        K.eq(str(P("LifePage").effect(JInt(k_), JInt(1), JInt(5))), str(LL.upEffect(JInt(k_), JInt(1), JInt(5))), "T the Tools page's effect text = GearLL.upEffect (one writer)")
    # ================================================================================== Z capfix (0.3.49): Skyy's watering can click, no backpack
    try:
        SIC(JShort(0))
        zmsg = None
    except Exception as e_:
        zmsg = str(e_)
    K.check(zmsg is not None and "Capacity is less than or equal zero! 0 <= 0" in zmsg,
            "Z root cause: the engine's SimpleItemContainer(0) throws Skyy's log message (%s)" % zmsg)
    invE, csE = mkinv(nobp=True)
    K.eq(int(csE["backpack"].getCapacity()), 0, "Z the no-backpack inventory: backpack = EmptyItemContainer, capacity 0")
    zr = "?"
    try:
        zr = Up.roomWhy(invE, JArray(JString)(["Ingredient_Stick", "Plant_Crop_Carrot_Item"]), JArray(JInt)([50, 45]))
        zr = None if zr is None else str(zr)
    except Exception as e_:
        zr = "THREW " + str(e_)
    K.check(zr is None, "Z roomWhy with no backpack: two change stacks fit an empty inventory, no throw (0.3.48 threw here): %s" % zr)
    one_free(csE)
    try:
        zr2 = Up.roomWhy(invE, JArray(JString)(["Ingredient_Stick", "Plant_Crop_Carrot_Item"]), JArray(JInt)([50, 45]))
        zr2 = None if zr2 is None else str(zr2)
    except Exception as e_:
        zr2 = "THREW " + str(e_)
    K.check(zr2 is not None and "room" in zr2, "Z roomWhy with no backpack + ONE free slot, two change stacks: refused by words, no throw: %s" % zr2)
    try:
        ac = P("GearArmor").activeCopy(u, EIC.INSTANCE)
        zac = int(ac.getCapacity())
    except Exception as e_:
        zac = "THREW " + str(e_)
    K.eq(zac, 1, "Z activeCopy of a capacity-0 armor container: a 1-slot empty copy, no throw")
    can_from = "Tool_WaterCan_Iron"
    can_to = str(Up.next(JString(can_from))) if Gear.item(JString(can_from)) is not None and Up.next(JString(can_from)) is not None else None
    K.check(can_to is not None and Gear.item(JString(can_to)) is not None, "Z the Iron Watering Can and its next tier are loaded: %s -> %s" % (can_from, can_to))
    if can_to is not None:
        kc = int(LL.kOf(JString(can_from)))
        K.eq(kc, int(LL.CAN), "Z the can is the lifelong 'can' kind")
        zc = Up.cost(JString(can_from), JString(can_to))
        zids, zqs = [str(x) for x in zc[0]], [int(x) for x in zc[1]]
        zen = dict((i_, str(Up.enchOf(JString(i_), zc[0]))) for i_ in zids if Up.enchOf(JString(i_), zc[0]) is not None)
        K.notes.append("Z can cost (harness defaults; Skyy's server: Bronze Ingot 32, Carrot 355, Stick 150): %s, Enchanted forms %s" % (list(zip(zids, zqs)), zen))
        K.check(len(zen) >= 2, "Z the can step has at least two materials with an Enchanted form (sticks / carrots / bronze)")
        zreg = Props()
        zreg.setProperty("can.id", can_from)
        zreg.setProperty("can.uid", "harness-can")
        br.put("acc:smelt:" + U, JString("1|x|x|x|" + pk))          # the Furnace Charm (as the P2 Harvester case)
        BDz, BIz, BSz = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonInt32"), JClass("org.bson.BsonString")
        zd = BDz()
        zd.append("ll", BIz(1)); zd.append("lo", BSz(pk)); zd.append("lu", BSz("harness-can"))
        enl = sorted(zen.keys())
        e_inv, e_bag = enl[0], enl[1]          # one Enchanted form in the inventory (change back), one in the Pocket Dimension

        def can_setup(room=True, nobp=True, bag_loose=False):
            inv_, cs_ = mkinv(nobp=nobp)
            cs_["hotbar"].setItemStackForSlot(JShort(0), Data.put(IS(JString(can_from), JInt(1)), zd, u))
            sl_ = 1
            BAG.clear()
            del TOOK[:]
            for i_, q_ in zip(zids, zqs):
                if i_ == e_inv:          # 0 loose, Enchanted only, in the inventory: ceil(q / 100) opened, the rest back as change
                    put(cs_, "storage", sl_, zen[i_], (q_ + 99) // 100 + 1); sl_ += 1
                elif i_ == e_bag:          # a few loose in the inventory, the rest as Enchanted in the Pocket Dimension (change too)
                    lo_ = min(17, q_ - 1)
                    put(cs_, "storage", sl_, i_, lo_); sl_ += 1
                    BAG[zen[i_]] = (q_ - lo_ + 99) // 100 + 2
                elif bag_loose:          # loose, all in the Pocket Dimension
                    BAG[i_] = q_ + 5
                else:          # loose, all in the inventory; its Enchanted source (if any) empty
                    put(cs_, "storage", sl_, i_, q_ + 5); sl_ += 1
            if not room:
                for f_ in ("hotbar", "storage", "backpack"):
                    c_ = cs_[f_]
                    for i_ in range(int(c_.getCapacity())):
                        s_ = c_.getItemStack(JShort(i_))
                        if s_ is None or s_.isEmpty():
                            c_.setItemStackForSlot(JShort(i_), IS(JString("Rock_Stone_Cobble"), JInt(1)))
            return inv_, cs_

        def units(cs_, i_):
            e_ = zen.get(i_)
            return count(cs_, i_) + BAG.get(i_, 0) + (100 * (count(cs_, e_) + BAG.get(e_, 0)) if e_ else 0)

        def zsnap(cs_):
            d_ = dict((i_, count(cs_, i_)) for i_ in set(zids + list(zen.values()) + [can_from, can_to]))
            d_["bag"] = dict(BAG)
            return d_

        def click(inv_):
            lp_ = page("LifePage")
            lp_.sel = kc
            lp_.info = JString("")
            lp_.epoch = JString("")
            lp_.armK = -1
            LL.REG.put(JString(pk), zreg)
            try:
                lp_.tierUp(inv_)
                return str(lp_.info)
            except Exception as e_:
                return "THREW " + str(e_)
            finally:
                LL.REG.put(JString(pk), reg)
        for nobp, bl in ((True, False), (True, True), (False, False)):
            tag = "%s, loose %s" % ("no backpack" if nobp else "9-slot backpack", "in the Pocket Dimension" if bl else "in the inventory")
            inv_, cs_ = can_setup(nobp=nobp, bag_loose=bl)
            u0 = dict((i_, units(cs_, i_)) for i_ in zids)
            b0 = dict(BAG)
            info = click(inv_)
            u1 = dict((i_, units(cs_, i_)) for i_ in zids)
            took = {}
            for i_, g_ in TOOK:
                took[i_] = took.get(i_, 0) + g_
            K.check(info.startswith("+") and count(cs_, can_from) == 0 and count(cs_, can_to) == 1,
                    "Z Skyy's click (%s): the can tiers up (%s)" % (tag, info))
            K.eq(dict((i_, u0[i_] - u1[i_]) for i_ in zids), dict(zip(zids, zqs)),
                 "Z (%s) every cost taken exactly once (loose + 100 x Enchanted, inventory + bags, before - after = the cost)" % tag)
            K.check(all(b0.get(i_, 0) - BAG.get(i_, 0) == took.get(i_, 0) for i_ in set(list(b0) + list(took))) and len(TOOK) == len(took),
                    "Z (%s) the bags gave exactly what was taken, one take per id: %s" % (tag, TOOK))
        # no room for the change (no backpack, inventory full): refused, nothing moved, no throw
        inv_, cs_ = can_setup(room=False)
        s0 = zsnap(cs_)
        info = click(inv_)
        K.check(info.startswith("-") and "room" in info and zsnap(cs_) == s0 and not TOOK,
                "Z no backpack + full inventory: refused before anything moved (nothing taken from the inventory or the bags): %s" % info)
        # short of a material: refused, nothing moved
        inv_, cs_ = can_setup()
        BAG[zen[e_bag]] = 0
        s0 = zsnap(cs_)
        info = click(inv_)
        K.check(info.startswith("-") and zsnap(cs_) == s0 and not TOOK, "Z short of %s: refused, nothing moved: %s" % (e_bag, info))
        # giveChange on a no-backpack inventory (the change lands in storage / hotbar; the capacity-0 section is read as 0 slots)
        inv_, cs_ = mkinv(nobp=True)
        try:
            gc_ = Up.giveChange(inv_, JArray(JString)(["Ingredient_Stick"]), JArray(JInt)([50]))
            gz = (str(gc_[0]), count(cs_, "Ingredient_Stick"))
        except Exception as e_:
            gz = ("THREW " + str(e_), -1)
        K.eq(gz, ("", 50), "Z giveChange with no backpack: all 50 sticks in, no throw")
    dist = sorted(set(m_[2] for _w, ms_, _u in bad for m_ in ms_))
    K.check(not bad, "O every selector exists when its command runs + every binding's element at the end: %d bad, missing %s, first %s" % (len(bad), dist[:10], bad[:1]))
    K.save()


# ====================================================================================================== D: start twice on the live copy
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    fc = os.path.join(home, "config.properties")
    c0 = open(fc, "rb").read() if os.path.isfile(fc) else None
    K.check(c0 is not None, "D the live copy has a config.properties")
    Cfg.FILE = JClass("java.nio.file.Paths").get(fc)
    MIG = ["migrate0326", "migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39", "migrateUt28"]
    m0 = "".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    c1 = open(fc, "rb").read()
    Cfg.load()
    K.notes.append("D start 1: one-time updates said %r" % m0[:200])
    K.check(open(fc, "rb").read() == c1, "D start 2 changes nothing")
    K.check(c1 == c0 or m0 != "", "D no saved-data change from this round (the file is byte-identical unless an OLDER one-time update ran: %r)" % m0[:80])
    K.save()


if "--expect-dump" in sys.argv:
    EXPECT = {}
HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("engine", run_engine), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
