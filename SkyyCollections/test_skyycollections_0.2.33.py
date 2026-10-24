"""Harness for SkyyCollections 0.2.33 (Harvester / sickle swing harvests count: CollSwing + CollSwingTask; the F-pickup break context claims
pickups only for a BreakBlockEvent with no item in hand; tools/collections_0_2_33_patch.py). Build first:
    python tools/collections_0_2_33_patch.py && python SkyyCollections/build_skyycollections_0.2.33.py
      (SkyyGear/SkyyGear-0.3.29.jar gone? set SKYY_GEAR_0329_JAR to a copy extracted from backups/archive/old-jars-20261022.tar.xz)
    python SkyyCollections/test_skyycollections_0.2.33.py [--jar <SkyyCollections-0.2.33.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  S    static   the patch re-runs to identical bytes; line endings kept; two new classes, no new command / system; CollPickupSys takes the
                three branches in order (F-pickup claim -> F-harvest window -> swing) and the swing branch returns
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.32 -> 0.2.33 (EXPECT below)
  SW   EXECUTED on a fresh registry (CollReg.loadAll on a scratch folder): the crop map built through CollSwing.put from the REAL vanilla
       StageFinal harvest drop lists (Assets.zip); a Harvester swing over wheat + carrot + a berry bush = pickup events fed through
       CollSwing.add (one CollSwingTask queued per burst) -> the task credits every dropped stack ONCE (counts = exactly the stacks);
       the task run again / a second flush = 0; a cancelled stack is not counted; a placed Health plant / rubble / stick pile / mushroom
       handing back its own item counts nothing (alone, before a crop, between crops); a treasure pile (not a Farming produce) nothing;
       creative-free path with pr = null (offline) still counts for the profile; a profile change between pickup and task = nothing;
       every Harvester id of SkyyGear (Tool_Sickle_Harvester_*) is a sickle, a hoe / pickaxe / bare hand is not
  CL   CollSwing.claims: an F pickup (held null, same thread, < 250 ms, task not run) claims; a break WITH an item (a Harvester / a hoe), a
       done context, another thread, 300 ms later do not
  FH   F-harvest still credits once: CollPickupTask (the window branch's task) credits the stack once; a cancelled one nothing
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, subprocess, importlib.util, threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD_VERSION = "0.2.33", "0.2.32"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)
GEN = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyycollections_%s.py" % OLD_VERSION)
PATCH = os.path.join(ROOT, "tools", "collections_0_2_33_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "collharv", "test")))
PKG = "com.skyy.collections."
# CfgFn / CfgRows: the version text; CollTier: the working tree's tools/tier_tags.py (round fish2's uncommitted SkyyFishing rows, not this
# round) - the table every jar copies; CollPickupSys: the three branches; the plugin: the ready line
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CollTier": ["~<clinit>"], "CollPickupSys": ["~m handle"],
          "SkyyCollectionsPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["CollSwing", "CollSwingTask"]
AZ = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
GEAR_GEN = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.44.py")          # read-only: the Harvester ids
T31 = None


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


def t31():
    global T31
    if T31 is None:
        T31 = tmod(os.path.join(HERE, "test_skyycollections_0.2.31.py"), "tco0231")
    return T31


def mkis(i, q):
    """an ItemStack without the Item asset store (the harness has no assets): Unsafe-allocated, itemId + quantity set (the fields the
    credit path reads: getItemId / getQuantity / isEmpty = itemId "Empty")"""
    from jpype import JClass, JInt
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    x = uf.get(None).allocateInstance(IS.class_)
    for n, v in (("itemId", i),):
        f = IS.class_.getDeclaredField(n)
        f.setAccessible(True)
        f.set(x, v)
    f = IS.class_.getDeclaredField("quantity")
    f.setAccessible(True)
    f.setInt(x, JInt(q))
    return x


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.33"') == 1 and '[SkyyCollections] 0.2.33 ready (' in g and '[SkyyCollections] 0.2.32 ready' not in g, "S version + ready line")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count(' = K("') - o.count(' = K("'), 2, "S two new classes")
    h3 = g[g.index('event_system(psy, "CollPickupSys"'):]
    h3 = h3[:h3.index('""")')]
    a, b, c = h3.index("CollSwing.claims(g, Thread.currentThread(), System.nanoTime())) { g.pickups.add(e); return; }"), \
        h3.index("CollPending.USE.get(u)"), h3.index("{ @PKG@.CollSwing.swing(st, r, pr, u, e); return; }")
    K.check(a < b < c and h3.count("CollSwing.swing(") == 1 and h3.index("w.execute(new @PKG@.CollPickupTask(") > c,
            "S CollPickupSys: F-pickup claim -> F-harvest window -> swing (returns) -> the window's CollPickupTask; each pickup takes ONE branch")
    K.check("g.held == null" in g[g.index("public static boolean claims("):g.index("public static boolean claims(") + 300], "S claims needs no item in hand")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _drop_ids(z, path):
    """item ids of a vanilla drop list in container order (BlockHarvestUtils.getDrops emits them in that order)"""
    out = []

    def walk(c):
        if not isinstance(c, dict):
            return
        it = c.get("Item")
        if isinstance(it, dict) and it.get("ItemId"):
            out.append((it["ItemId"], int(it.get("QuantityMax", 1))))
        for x in c.get("Containers") or []:
            walk(x)
    walk(json.loads(z.read(path).decode("utf-8-sig")).get("Container"))
    return out


def run_sw(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    base = os.path.join(scratch, "sw", "Skyy_SkyyCollections")
    os.makedirs(os.path.join(base, "counts"))
    Reg = t31().boot(base)
    Reg.loadAll()
    R = Reg.D
    Sw = JClass(PKG + "CollSwing")
    Task = JClass(PKG + "CollSwingTask")
    St = JClass(PKG + "CollStore")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    IPE = JClass("com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent")
    HM, HS = JClass("java.util.HashMap"), JClass("java.util.HashSet")
    # the crop map from the REAL vanilla StageFinal harvest drop lists (keys() reads the same lists from the block assets in game)
    z = zipfile.ZipFile(AZ)
    crops = {}
    for cname in ("Wheat", "Carrot", "Potato", "Berry"):
        crops[cname] = _drop_ids(z, "Server/Drops/Crop/%s/Drops_Plant_Crop_%s_StageFinal_Harvest.json" % (cname, cname))
    m = HM()
    for cname, lst in crops.items():
        ids = HS()
        for i, _q in lst:
            ids.add(i)
        prod = lst[0][0]
        Sw.put(m, prod, sum(1 for i, _q in lst if i == prod) > 1, ids)
    tre = HS()
    tre.add("Ore_Gold")
    Sw.put(m, "Deco_Treasure", False, tre)          # a StageFinal treasure pile: produce not a Farming collection item
    Sw.KEYS = m
    K.check(Sw.keys() is m or Sw.keys().equals(m), "SW keys() returns the cached crop map")
    K.notes.append("crop drop lists: %s" % crops)
    K.check(crops["Wheat"][0][0] == "Plant_Crop_Wheat_Item" and crops["Carrot"][0][0] == "Plant_Crop_Carrot_Item", "SW the produce leads each vanilla harvest list")

    queued = []

    @JImplements("java.util.concurrent.Executor")
    class Exec(object):
        @JOverride
        def execute(self, r):
            queued.append(r)
    ex = Exec()
    U = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000c0115")
    key = str(U)
    d = St.dataK(key)

    def cnt(item):
        v = d.items.get(item)
        return 0 if v is None else int(v)

    def snap():
        return dict((str(k), int(d.items.get(k))) for k in d.items.keySet())

    def swing(stacks, cancel=(), k=key):
        evs = [IPE(mkis(i, q)) for i, q in stacks]
        first = [bool(Sw.add(U, None, k, e, ex)) for e in evs]
        for ci in cancel:
            evs[ci].setCancelled(True)
        n = len(queued)
        for r in list(queued):
            r.run()
        del queued[:]
        return first, n

    def delta(a, b):
        return dict((x, b.get(x, 0) - a.get(x, 0)) for x in set(a) | set(b) if b.get(x, 0) != a.get(x, 0))
    wheat = [(i, q) for i, q in crops["Wheat"]]
    carrot = [(i, q) for i, q in crops["Carrot"]]
    berry = [(i, q) for i, q in crops["Berry"]]
    # 1. one swing over wheat + carrot + berries: every stack once, one task
    s0 = snap()
    first, nq = swing(wheat + carrot + berry)
    s1 = snap()
    want = {}
    for i, q in wheat + carrot + berry:
        if R.itemColl.get(i) is not None:
            want[i] = want.get(i, 0) + q
    K.check(first[0] and not any(first[1:]) and nq == 1, "SW one burst = one CollSwingTask queued (first pickup only): %s" % first)
    K.eq(delta(s0, s1), want, "SW a Harvester swing over wheat + carrot + a berry bush credits exactly the dropped stacks once")
    K.check(want.get("Plant_Crop_Wheat_Item", 0) >= 1 and want.get("Plant_Crop_Carrot_Item", 0) >= 1 and want.get("Ingredient_Life_Essence", 0) >= 1,
            "SW wheat, carrot and Essence of Life are among the credited stacks: %s" % want)
    K.check(not Sw.PEND.containsKey(U), "SW the burst is gone after its task")
    # the same task again / a flush without a burst: nothing
    s2 = snap()
    Task(U).run()
    K.eq(int(Sw.flush(U)), 0, "SW a second flush credits nothing")
    K.eq(delta(s2, snap()), {}, "SW the task run again credits nothing (never twice)")
    # 2. one wheat crop: exactly its amount
    s2 = snap()
    swing([("Plant_Crop_Wheat_Item", 2), ("Ingredient_Life_Essence", 3)])
    K.eq(delta(s2, snap()), {"Plant_Crop_Wheat_Item": 2, "Ingredient_Life_Essence": 3}, "SW one ripe wheat: 2 wheat + 3 Essence of Life, once")
    # 3. a cancelled stack is not counted
    s2 = snap()
    swing([("Plant_Crop_Wheat_Item", 2), ("Ingredient_Life_Essence", 3)], cancel=(1,))
    K.eq(delta(s2, snap()), {"Plant_Crop_Wheat_Item": 2}, "SW a cancelled pickup (another mod refused it) is not counted")
    # 4. placed non-crop blocks handing back their own item (FarmingUtil.harvest0 harvests any Harvest block): nothing
    junk = [("Plant_Crop_Health1", 1), ("Rubble_Stone", 1), ("Ingredient_Stick", 2), ("Plant_Crop_Mushroom_Cap_Brown", 1), ("Plant_Cactus_Flower", 1),
            ("Plant_Fruit_Windwillow", 1)]
    s2 = snap()
    swing(junk)
    K.eq(delta(s2, snap()), {}, "SW placed Health plant / rubble / stick pile / mushroom / cactus flower / windwillow alone: nothing")
    s2 = snap()
    swing(junk + [("Plant_Crop_Wheat_Item", 1), ("Rubble_Stone", 1), ("Ingredient_Life_Essence", 2), ("Plant_Crop_Mushroom_Cap_Brown", 1),
                  ("Plant_Crop_Carrot_Item", 1)])
    K.eq(delta(s2, snap()), {"Plant_Crop_Wheat_Item": 1, "Ingredient_Life_Essence": 2, "Plant_Crop_Carrot_Item": 1},
         "SW junk before / between crops is skipped; the crops' own stacks count")
    s2 = snap()
    swing([("Deco_Treasure", 1), ("Ore_Gold", 3)])
    K.eq(delta(s2, snap()), {}, "SW a treasure pile (produce not a Farming collection item) counts nothing on a swing")
    # 5. the profile changed between the pickup and the task: nothing (creditOne's profile check)
    s2 = snap()
    swing([("Plant_Crop_Wheat_Item", 2)], k=key + "-p2")
    K.eq(delta(s2, snap()), {}, "SW a burst for another profile key than the active one counts nothing")
    # 6. the held item rule
    ids = sorted(set(re.findall(r"Tool_Sickle_Harvester_[A-Za-z]+(?:_SkyWynn)?", open(GEAR_GEN, encoding="utf8").read())))
    hv = [i for i in ids if not i.endswith("_")]
    K.check(len(hv) >= 4 and all(bool(Sw.isSickle(i)) for i in hv), "SW every SkyyGear Harvester id is a sickle: %s" % hv)
    K.check(not any(bool(Sw.isSickle(i)) for i in (None, "", "Tool_Hoe_Crude", "Tool_Pickaxe_Iron", "Weapon_Sword_Iron")), "SW hoe / pickaxe / sword / bare hand are not")
    # 7. farmCrop
    K.check(bool(Sw.farmCrop(R, "Plant_Crop_Wheat_Item")) and bool(Sw.farmCrop(R, "Plant_Fruit_Berries_Red")) and not bool(Sw.farmCrop(R, "Deco_Treasure"))
            and not bool(Sw.farmCrop(R, "Ore_Copper")) and not bool(Sw.farmCrop(None, "Plant_Crop_Wheat_Item")), "SW farmCrop: Farming produce only")
    # 8. an executor that refuses the task drops the burst (no stale PEND)
    @JImplements("java.util.concurrent.Executor")
    class Refuse(object):
        @JOverride
        def execute(self, r):
            raise RuntimeError("refused")
    K.check(not bool(Sw.add(U, None, key, IPE(mkis("Plant_Crop_Wheat_Item", 1)), Refuse())) and not Sw.PEND.containsKey(U), "SW a refused task leaves no burst behind")
    K.check(int(Sw.CROPS.get()) >= 5 and bool(Sw.SEEN), "SW the diagnostic counted the crops (%d) and logged once" % int(Sw.CROPS.get()))
    K.save()


def run_cl(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Sw = JClass(PKG + "CollSwing")
    G = JClass(PKG + "GatherCtx")
    Thr = JClass("java.lang.Thread")
    Sysj = JClass("java.lang.System")

    def ctx(held, done=False, ago_ns=1000000):
        g = G()
        g.held = held
        g.done = done
        g.thread = Thr.currentThread()
        g.nanos = Sysj.nanoTime() - ago_ns
        return g
    now = lambda: Sysj.nanoTime()
    K.check(bool(Sw.claims(ctx(None), Thr.currentThread(), now())), "CL an F pickup (no item in hand) claims its pickups")
    K.check(not bool(Sw.claims(ctx("Tool_Sickle_Harvester_Crude"), Thr.currentThread(), now())), "CL a Harvester swing's break (one-up crop / bush) does not")
    K.check(not bool(Sw.claims(ctx("Tool_Hoe_Crude"), Thr.currentThread(), now())), "CL a break with any item does not")
    K.check(not bool(Sw.claims(ctx(None, done=True), Thr.currentThread(), now())), "CL a context whose task ran does not")
    K.check(not bool(Sw.claims(ctx(None, ago_ns=300000000), Thr.currentThread(), now())), "CL 300 ms later does not")
    K.check(not bool(Sw.claims(None, Thr.currentThread(), now())), "CL no context does not")
    g = ctx(None)
    res = {}

    def other():
        try:
            res["v"] = bool(Sw.claims(g, Thr.currentThread(), Sysj.nanoTime()))
        except Exception as e:
            res["e"] = repr(e)
    t = threading.Thread(target=other)
    t.start()
    t.join()
    K.check(res.get("v") is False, "CL another thread does not: %s" % res)
    K.save()


def run_fh(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    base = os.path.join(scratch, "fh", "Skyy_SkyyCollections")
    os.makedirs(os.path.join(base, "counts"))
    Reg = t31().boot(base)
    Reg.loadAll()
    St = JClass(PKG + "CollStore")
    PT = JClass(PKG + "CollPickupTask")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    IPE = JClass("com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent")
    U = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000f4a57")
    key = str(U)
    d = St.dataK(key)
    e = IPE(mkis("Plant_Crop_Wheat_Item", 2))
    PT(e, None, U, key).run()
    K.eq(int(d.items.get("Plant_Crop_Wheat_Item")), 2, "FH an F-harvest pickup credits its stack once (CollPickupTask)")
    e2 = IPE(mkis("Plant_Crop_Wheat_Item", 5))
    e2.setCancelled(True)
    PT(e2, None, U, key).run()
    K.eq(int(d.items.get("Plant_Crop_Wheat_Item")), 2, "FH a cancelled F-harvest pickup counts nothing")
    K.eq(int(JClass(PKG + "CollSwing").PEND.size()), 0, "FH the swing burst map is untouched by an F-harvest")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyCollections", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("sw", run_sw), ("cl", run_cl), ("fh", run_fh)], script=__file__)
