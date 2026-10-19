"""Harness for SkyySacks 0.8.25 (the off-hand refills too - beta bug 11; tools/sacks_0_8_25_patch.py). Build first:
    python tools/sacks_0_8_25_patch.py && python SkyySacks/build_skyysacks_0.8.25.py

    python SkyySacks/test_skyysacks_0.8.25.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.8.24 -> 0.8.25: exactly the planned members (EXPECT)
  OFF   (the 0.8.0 harness's Void stand-ins + an inventory stand-in WITH an off-hand container) the real SweepTask.items tick, twice per case:
        a torch (no Void category) used from the off-hand is topped up from storage; an off-hand torch that RAN OUT is refilled with the
        same item; nothing used = nothing moves; a Void item (cobble) tops up from the Void first (pool pays exactly what the slot gained);
        the Void before the inventory; the hotbar is never a source; refill Off (bags.refill off) = nothing; a stack with metadata and a
        non-stacking item (max 1) are never touched; items are conserved in every case; SEENU holds the off-hand ids; forgetSeen clears it
  AA    engine-access audit
Not testable without the game (UNVERIFIED): the real utility container's filter (a torch / food may sit there; anything it refuses is
simply not added - read back = 0, nothing taken), the client showing the refilled off-hand at once. Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_orig_compare = HK.run_compare
_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_10", os.path.join(HERE, "test_skyysacks_0.8.10.py"))
T0810 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T0810)
T089 = T0810.T089
sys.argv = _argv
HK.run_compare = _orig_compare

VERSION = "0.8.25"
OLD_VERSION = "0.8.24"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "bsc", "sacks25")))
PKG = "com.skyy.sacks."
EXPECT = {
    "SackPool": ["+f SEENU", "~m forgetSeen", "~<clinit>"],
    "SweepTask": ["+m utilCounts", "+m utilIds", "+m offFill", "~m items"],
    "SkyySacksPlugin": ["~m setup"],    # the ready line names 0.8.25
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
TORCH, SHIELD, COB = "Furniture_Crude_Torch", "Weapon_Shield_Wood", "Rock_Stone_Cobble"


def cases25(K, L, scratch):
    from jpype import JClass, JString, JShort
    VS, Defs, Cfg, Pool, Swp = L["VS"], L["Defs"], L["Cfg"], L["Pool"], L["Swp"]
    fresh, write_pool, coll, pc, custom_item, drain = (L[n] for n in ("fresh", "write_pool", "coll", "pc", "custom_item", "drain"))
    UUID, IS, SIC, us, inv_field, PLA = L["UUID"], L["IS"], L["SIC"], L["us"], L["inv_field"], L["PLA"]
    jp, CtF, CtM, CtC, INVN, ICN = L["jp"], L["CtF"], L["CtM"], L["CtC"], L["INVN"], L["ICN"]
    CICN = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
    # an inventory stand-in WITH an off-hand (utility) container
    ti = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyTestInvU", jp.get(INVN))
    for f in ("s", "h", "b", "u"):
        ti.addField(CtF.make("public %s %s;" % (ICN, f), ti))
    ti.addConstructor(CtC.make("public SkyyTestInvU(%s s, %s h, %s b, %s u) { super(); this.s = s; this.h = h; this.b = b; this.u = u; }" % (ICN, ICN, ICN, ICN), ti))
    for m, f in (("getStorage", "s"), ("getHotbar", "h"), ("getBackpack", "b"), ("getUtility", "u")):
        ti.addMethod(CtM.make("public %s %s() { return this.%s; }" % (ICN, m, f), ti))
    for m, order in (("getCombinedBackpackStorageHotbar", "this.b, this.s, this.h"), ("getCombinedStorageHotbarBackpack", "this.s, this.h, this.b")):
        ti.addMethod(CtM.make("public %s %s() { return new %s(new %s[] { %s }); }" % (CICN, m, CICN, ICN, order), ti))
    TInvU = JClass(ti.toClass(JClass(INVN).class_))
    custom_item(TORCH, 25)
    custom_item(SHIELD, 1)
    custom_item(COB, 100)

    def player(storage=(), hotbar=(), backpack=(), off=()):
        conts = [SIC(JShort(36)), SIC(JShort(9)), SIC(JShort(9)), SIC(JShort(4))]
        for cont, its in zip(conts, (storage, hotbar, backpack, off)):
            for (iid, q) in its:
                assert cont.addItemStack(IS(iid, q)).succeeded(), (iid, q)
        p = us.allocateInstance(PLA.class_)
        inv_field.set(p, TInvU(*conts))
        return p

    def cnt(cont):
        out = {}
        for s in range(int(cont.getCapacity())):
            it = cont.getItemStack(JShort(s))
            if it is not None and not it.isEmpty():
                out[str(it.getItemId())] = out.get(str(it.getItemId()), 0) + int(it.getQuantity())
        return out

    def view(p):
        i = p.getInventory()
        return {"storage": cnt(i.getStorage()), "hotbar": cnt(i.getHotbar()), "backpack": cnt(i.getBackpack()), "off": cnt(i.getUtility())}

    def total(v, k=None, ids=(TORCH, COB, SHIELD)):
        t = dict((i, sum(v[c].get(i, 0) for c in v)) for i in ids)
        if k is not None:
            pl = pc(k)
            for i in ids:
                t[i] += pl.get(i, 0)
        return t

    def off0(p):
        it = p.getInventory().getUtility().getItemStack(JShort(0))
        return None if it is None or it.isEmpty() else (str(it.getItemId()), int(it.getQuantity()))

    n = [0]

    def setup(pool=None):
        n[0] += 1
        base = os.path.join(scratch, "off25", "c%d" % n[0])
        pd = fresh(base)
        k = "00000000-0000-0000-0000-0000000025%02d" % n[0]
        U = UUID.fromString(k)
        coll(U, {"Mining": 0, "Foraging": 0, "Farming": 0, "Fishing": 0, "Combat": 0, "Smithing": 0})
        write_pool(pd, k, pool or {})
        return k, U

    def tick(p, k, U):
        r = Swp.items(p, JString(k), U, VS.capsK(U, JString(k)))
        drain()
        return [int(x) for x in r]

    K.check(Defs.homeOf(JString(TORCH)) is None and str(Defs.homeOf(JString(COB))) == "Mining", "OFF a torch has no Void category (only the inventory can refill it); cobble = Mining")
    # ---- 1. torch used from the off-hand -> topped up from storage
    k, U = setup()
    p = player(storage=[(TORCH, 20)], off=[(TORCH, 5)])
    tick(p, k, U)
    v0 = view(p)
    K.check(v0["off"] == {TORCH: 5} and v0["storage"] == {TORCH: 20}, "OFF 1 tick 1 (nothing used yet) moves nothing: %s" % v0)
    ids = Pool.SEENU.get(U)
    K.check(ids is not None and str(ids[0]) == TORCH, "OFF 1 SEENU remembers the off-hand torch")
    p.getInventory().getUtility().setItemStackForSlot(JShort(0), IS(TORCH, 3))       # placed 2 torches from the off-hand
    r = tick(p, k, U)
    v1 = view(p)
    K.check(v1["off"] == {TORCH: 23} and v1["storage"] == {} and r[1] == 20, "OFF 1 the used off-hand torch is topped up from storage (3 + 20 = 23, max 25): %s %s" % (v1, r))
    K.eq(total(v1), {TORCH: 23, COB: 0, SHIELD: 0}, "OFF 1 conserved (23 torches before and after the refill)")
    r = tick(p, k, U)
    K.check(view(p) == v1 and r[1] == 0, "OFF 1 the next tick (the move itself is no 'use') changes nothing: %s" % view(p))
    # ---- 2. the off-hand torch RAN OUT -> refilled with the same item
    k, U = setup()
    p = player(storage=[(TORCH, 10), (COB, 1)], off=[(TORCH, 1)])
    tick(p, k, U)
    p.getInventory().getUtility().removeItemStackFromSlot(JShort(0))                 # the last torch placed
    K.check(off0(p) is None, "OFF 2 the off-hand slot is empty")
    tick(p, k, U)
    v = view(p)
    K.check(off0(p) == (TORCH, 10) and TORCH not in v["storage"], "OFF 2 the empty off-hand slot gets the same item back (10 from storage): %s" % v)
    # ---- 3. nothing used = nothing moves
    k, U = setup()
    p = player(storage=[(TORCH, 10)], off=[(TORCH, 5)])
    tick(p, k, U)
    tick(p, k, U)
    K.eq(view(p)["off"], {TORCH: 5}, "OFF 3 an off-hand stack that was not used is not topped up")
    # ---- 4. a Void item: the Void first, exactly what the slot gained; then the inventory is not needed
    k, U = setup({COB: 500})
    p = player(off=[(COB, 10)])
    tick(p, k, U)
    p.getInventory().getUtility().setItemStackForSlot(JShort(0), IS(COB, 4))
    tick(p, k, U)
    K.check(off0(p) == (COB, 100) and pc(k).get(COB) == 404, "OFF 4 cobble in the off-hand tops up from the Void: 4 -> 100, the pool pays 96 (500 -> 404): %s %s" % (off0(p), pc(k)))
    # ---- 4b. the Void runs short -> the rest from storage (Void first)
    k, U = setup({COB: 6})
    p = player(off=[(COB, 10)], backpack=[(COB, 50)])
    tick(p, k, U)
    b0 = view(p)
    p.getInventory().getUtility().setItemStackForSlot(JShort(0), IS(COB, 4))
    pool0 = pc(k).get(COB, 0)
    t0 = total(view(p), k)
    tick(p, k, U)
    v = view(p)
    K.check(off0(p) is not None and off0(p)[0] == COB and pc(k).get(COB, 0) == 0 and total(v, k) == t0,
            "OFF 4b the Void pays first (all %d), then the backpack; nothing made or lost: %s pool %s (before %s)" % (pool0, v, pc(k), b0))
    # ---- 5. the hotbar is never a source
    k, U = setup()
    p = player(hotbar=[(TORCH, 10)], off=[(TORCH, 5)])
    tick(p, k, U)
    p.getInventory().getUtility().setItemStackForSlot(JShort(0), IS(TORCH, 4))
    tick(p, k, U)
    K.check(view(p)["hotbar"] == {TORCH: 10} and off0(p) == (TORCH, 4), "OFF 5 hotbar torches are never pulled into the off-hand: %s" % view(p))
    # ---- 6. refill Off (Server Setup bags.refill off) = nothing
    k, U = setup()
    p = player(storage=[(TORCH, 10)], off=[(TORCH, 5)])
    tick(p, k, U)
    Cfg.REFILL_ON = False
    p.getInventory().getUtility().setItemStackForSlot(JShort(0), IS(TORCH, 4))
    tick(p, k, U)
    Cfg.REFILL_ON = True
    K.check(off0(p) == (TORCH, 4) and view(p)["storage"] == {TORCH: 10}, "OFF 6 stack refill off = the off-hand is not refilled: %s" % view(p))
    # ---- 7. a stack with metadata / a non-stacking item are never touched
    k, U = setup()
    p = player(storage=[(TORCH, 10), (SHIELD, 1)], off=[(SHIELD, 1)])
    BD, BS = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString")
    md = BD()
    md.put("SkyyTest", BS("named"))
    p.getInventory().getUtility().addItemStack(IS(TORCH, 5, md))
    tick(p, k, U)
    p.getInventory().getUtility().removeItemStackFromSlot(JShort(0))                  # the shield taken off (moved away)
    p.getInventory().getUtility().setItemStackForSlot(JShort(1), IS(TORCH, 3, md))
    tick(p, k, U)
    v = view(p)
    s1 = p.getInventory().getUtility().getItemStack(JShort(1))
    K.check(off0(p) is None and int(s1.getQuantity()) == 3 and v["storage"] == {TORCH: 10, SHIELD: 1},
            "OFF 7 a named (metadata) torch stack and a shield (max stack 1) are left alone: %s" % v)
    # ---- 8. forgetSeen (relog / profile switch) clears SEENU
    Pool.forgetSeen(U)
    K.check(Pool.SEENU.get(U) is None and Pool.SEENQ.get(U) is None, "OFF 8 forgetSeen clears SEENQ and SEENU")


def run_off25(out, jar, scratch, home):
    T089.void_cases = cases25
    T089.run_void(out, jar, scratch, home)


if __name__ == "__main__":
    print("kit:", T089.KIT_NOTE)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, [("off", run_off25)], __file__)
