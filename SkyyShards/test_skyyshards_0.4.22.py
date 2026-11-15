"""Harness for SkyyShards 0.4.22 (the store grid on every Collect tab, click a cell = collect that kind - tools/shards_0_4_22_patch.py, on top of 0.4.21).
Build first:
    python tools/shards_0_4_22_patch.py && python SkyyShards/build_skyyshards_0.4.22.py
    python SkyyShards/test_skyyshards_0.4.22.py [--keep]

  S22  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand; line endings kept
  GC   combat   EXECUTED the grid = the pool split (two zones merged, sorted), roll, one kind out (exact counts, the rest kept as kinds, the file), the same kind twice
                in one tick, two kinds then Collect all (no dupe, no loss), a full inventory, an inventory with one free slot (per kind + Collect all: inventory + store =
                what was there), the rolled drops count against storage (settle stops at the cap), a bad drops line, the bag cell over two islands (all / a short
                inventory), no bridge asked under the lock, rollback (0.4.21 never reads .drops; a save keeps it)
  GF   farming  EXECUTED the base cell, the Enchanted stock (legacy) and the loose rest apart, the Enchanted-only part of a stored count (legacy holding another item),
                the old item, the bonus finds merged with the stock, collection + XP credit per click = what Collect all pays, a full inventory
  PG22 page     the Collect tab grid: cells, counts, rarity squares, the sort, the bindings name the item, a click collects, a stale click, a visitor sees no buttons,
                the bag cell only with SkyyGear, the page walks clean, the packet size
  then 0.4.21's phases (geo, rebuild, level, bags, page21) and 0.4.20's / older ones, A verify, C compare, AA audit, live START TWICE
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.22"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shard1", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.21.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.21.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_22_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.21 harness (it loads 0.4.20 and older): its version moves to this one in memory
_T21 = open(os.path.join(HERE, "test_skyyshards_0.4.21.py"), encoding="utf8").read()
assert _T21.count('VERSION = "0.4.21"') == 3, "the 0.4.21 harness changed"   # its module line, its 0.4.20 loader, its own static check (not run here)
_T21 = _T21.replace('VERSION = "0.4.21"', 'VERSION = "0.4.22"')
assert _T21.count('"arena (SkyyShards 0.4.21) "') == 1
_T21 = _T21.replace('"arena (SkyyShards 0.4.21) "', '"arena (SkyyShards 0.4.22) "')   # the rebuild's collect.log line names the running version (@VERSION@)
_argv = list(sys.argv)
T421 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_21", loader=None))
T421.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.21.py")
exec(compile(_T21, T421.__file__, "exec"), T421.__dict__)
sys.argv[:] = _argv
T420, T419, T411, T410, T49, T416, T415, T413 = T421.T420, T421.T419, T421.T411, T421.T410, T421.T49, T421.T416, T421.T415, T421.T413
T421.JAR = T420.JAR = T419.JAR = T420.T418.JAR = T419.T417.JAR = JAR
T421.SCRATCH = T420.SCRATCH = T419.SCRATCH = T420.T418.SCRATCH = T416.SCRATCH = T415.SCRATCH = T419.T417.SCRATCH = SCRATCH
OWNER, MEMBER = T420.OWNER, T420.MEMBER
CK, FK = 5, 2
T0 = 1790000000000
H = 3600000
W, E = "Plant_Crop_Wheat_Item", "Skyy_Ench_Wheat"


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.22 - build script') and 'VERSION = "0.4.22"\n' in g, "S22 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S22 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.22:" in g, "S22 the ready line names the round")
    K.check("GRID_JAVA" in g and '"gc:" + this.sgId[gIx]' in g, "S22 the grid's binding names the item")
    K.check("fitFor(" not in g[g.index("public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs, String only)"):g.index("public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {")],
            "S22 collect0 no longer re-mixes a short combat Collect (fitFor)")
    K.check("ItemStack" not in g[g.index("GC_ROW = "):g.index("GRID_JAVA = ")], "S22 the grid cells are ItemIcons (no ItemStack in the cell markup)")
    c0 = g[g.index("public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs, String only)"):]
    c0 = c0[:c0.index('"""')]
    K.check("p.clear()" not in c0[:c0.index("=None of that is stored any more")] and "unroll(p, old, i)" in c0, "S22 fix 2: nothing taken puts back only the rolled keys (no p.clear() of the live profile)")
    bg = g[g.index("public static String collectBagsAll("):]
    bg = bg[:bg.index('"""')]
    K.check('startsWith("-")) break' not in bg, "S22 fix (bags): an island that answers '-' never stops the bag cell's other islands")
    K.check("assert not _G422_BAD" in g, "S22 fix (ids): the build asserts every grid id is a real item")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S22 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S22 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S22 the jar is newer than the build script, the build script newer than the patch")
    K.save()


def _grid(Core, kd, p):
    r = Core.gridOf(kd, p)
    return [(str(i), int(q)) for i, q in zip(r[0], r[1])]


def _gd(Core, kd, p):
    return dict(_grid(Core, kd, p))


def _sum(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, 0) + v
    return dict((k, v) for k, v in out.items() if v)


def _drops(Cb, p, slot, n):   # fix (critic 1): what a roll pays now = the cumulative roll from the island's saved rolled count
    r = Cb.rollFor(p, slot, n)
    return dict((str(i), int(q)) for i, q in zip(r[0], r[1]) if str(i) and int(q) > 0)


def _invd(L, cs, ids):
    return dict((i, int(L["count"](cs, i))) for i in ids if int(L["count"](cs, i)))


def _save(St, key, p):
    St.LOCK.lock()
    try:
        St.save(key, p)
    finally:
        St.LOCK.unlock()


def run_combat(out, jar, scratch, _home):
    from jpype import JLong, JString
    K = HK.Child(out)
    L = T411._L(os.path.join(scratch, "gc"), K)
    M, St, Core, Cfg, Inv, Cb, PyFn = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShInv"], L["ShCombat"], L["PyFn"]
    inv, count = L["inv"], L["count"]
    key = OWNER
    Core.NOW_TEST = T0
    ou = L["UUID"].fromString(OWNER)
    M.ONLINE.put(OWNER, True)
    M.ALL_ON_TEST = True
    Cfg.KEY_TEST = PyFn(lambda u: JString(key))
    p = St.get(key)
    St.LOCK.lock()
    try:
        M.starter(CK, p, JLong(T0)) if p.getProperty("combat.i0.type") is None else None
        for s, ty in ((0, "skeleton"), (1, "zone2")):
            p.setProperty("combat.i%d.type" % s, ty); p.setProperty("combat.i%d.size" % s, "1"); p.setProperty("combat.i%d.last" % s, str(T0))
            p.setProperty("combat.i%d.stored" % s, "0"); p.setProperty("combat.i%d.totems" % s, "soul_cage:1:::0:gc%04d" % s)
        p.setProperty("combat.auto", "1"); p.setProperty("combat.paused", "0"); p.setProperty("combat.storage", "5")
        p.setProperty("combat.placed", "skyy-island-" + OWNER + "|1|2|3")
        St.save(key, p)
    finally:
        St.LOCK.unlock()

    def setc(a, b):
        for s, n in ((0, a), (1, b)):
            p.setProperty("combat.i%d.stored" % s, str(n)); p.setProperty("combat.i%d.last" % s, str(T0)); p.remove("combat.i%d.drops" % s); p.remove("combat.i%d.bags" % s); p.remove("combat.i%d.rolled" % s)
        _save(St, key, p)

    # 1. the grid = exactly what Collect all pays (the split of each island's count, merged), in the sort order
    setc(300, 200)
    want = _sum(_drops(Cb, p, 0, 300), _drops(Cb, p, 1, 200))
    g = _grid(Core, CK, p)
    K.check(len(g) >= 3 and dict(g) == want, "GC the grid = the split of both islands merged (%d kinds)" % len(g))
    K.check(all(int(Core.gridCmp(g[i][0], g[i + 1][0])) < 0 for i in range(len(g) - 1)), "GC the grid is sorted (tier, then name): %s" % [x[0] for x in g][:6])
    tiers = [int(Core.tierOf(x[0])) or 1000 for x in g]
    K.check(tiers == sorted(tiers), "GC tier first, untiered last: %s" % tiers[:10])
    K.eq(int(M.stored(CK, p, 0)), 300, "GC showing the grid rolls nothing")
    # 2. one kind out: exactly its count from both islands, the rest stays as kinds
    d0, d1 = _drops(Cb, p, 0, 300), _drops(Cb, p, 1, 200)
    both = [i for i in d0 if i in d1]
    X = both[0] if both else g[0][0]
    cs = inv(27, 27, 9)
    r = str(Core.collectKind(ou, key, CK, X, cs))
    K.check(r.startswith("+Collected") and "only" not in r, "GC one kind: %s" % r[:120])
    K.eq(int(count(cs, X)), want[X], "GC ... exactly that kind's count came out (%s)" % X)
    K.eq(sum(int(count(cs, i)) for i in want if i != X), 0, "GC ... and nothing else")
    K.check(int(M.stored(CK, p, 0)) == 300 - sum(d0.values()) and int(M.stored(CK, p, 1)) == 200 - sum(d1.values()) and 300 - sum(d0.values()) < len(d0) + 2,
            "GC ... both counts were rolled (the units that make no whole item yet stay in the pool: %d / %d)" % (int(M.stored(CK, p, 0)), int(M.stored(CK, p, 1))))
    K.eq(int(str(p.getProperty("combat.i0.rolled"))), 300, "GC ... the rolled count is saved (300)")
    rest = dict(want)
    rest.pop(X)
    K.eq(_gd(Core, CK, p), rest, "GC ... the grid keeps every other kind, exactly")
    K.eq(int(M.heldN(CK, p, 0)), sum(d0.values()) - d0.get(X, 0), "GC ... island 1's rolled drops keep the rest (%d)" % (sum(d0.values()) - d0.get(X, 0)))
    K.eq(int(M.usedOf(CK, p, 0)), 300 - d0.get(X, 0), "GC ... and still use its storage")
    disk = open(os.path.join(str(St.DIR), key + ".properties"), encoding="utf8").read().replace(chr(92) + ":", ":")
    K.check("combat.i0.drops=" in disk and X + ":" not in [ln for ln in disk.splitlines() if ln.startswith("combat.i0.drops=")][0], "GC ... the file holds the rolled drops without that kind")
    # the same kind again in the same tick: nothing, nothing moves
    r2 = str(Core.collectKind(ou, key, CK, X, cs))
    K.check(r2.startswith("=None of that"), "GC the same kind twice in one tick: %s" % r2)
    K.eq(int(count(cs, X)), want[X], "GC ... no second payout")
    K.eq(_gd(Core, CK, p), rest, "GC ... the store did not move")
    # fix 2 (critic): a click that takes nothing on a pool that DOES roll (new count since): the rolled keys come back exactly, the rest of the profile is untouched
    p.setProperty("combat.i0.stored", str(int(M.stored(CK, p, 0)) + 40)); p.setProperty("zz.marker", "keep")
    _save(St, key, p)
    snap = dict((str(k_), str(p.getProperty(k_))) for k_ in p.stringPropertyNames())
    r2 = str(Core.collectKind(ou, key, CK, "Not_A_Real_Item", cs))
    K.check(r2.startswith("=None of that"), "GC fix 2: an id the shard does not hold: %s" % r2)
    K.eq(dict((str(k_), str(p.getProperty(k_))) for k_ in p.stringPropertyNames()), snap, "GC fix 2: ... stored / drops / rolled put back exactly, every other key kept")
    p.setProperty("combat.i0.stored", str(int(M.stored(CK, p, 0)) - 40)); p.remove("zz.marker")
    _save(St, key, p)
    # a second kind, then Collect all: every kind exactly once
    Y = [i for i in rest][0]
    r3 = str(Core.collectKind(ou, key, CK, Y, cs))
    K.check(r3.startswith("+Collected"), "GC a second kind: %s" % r3[:80])
    r4 = str(Core.collect(ou, key, CK, -1, cs))
    K.check(r4.startswith("+Collected"), "GC then Collect all: %s" % r4[:80])
    K.eq(_invd(L, cs, want), want, "GC no dupe, no loss: the inventory = what the grid showed")
    K.check(p.getProperty("combat.i0.drops") is None and p.getProperty("combat.i1.drops") is None and _gd(Core, CK, p) == {}, "GC the store is empty, no drops line left")
    # fix 1 (critic): the mix does not depend on how often anyone collects: 100 Collects of 3 = one roll of 300 (exactly), and the rarest kind still comes
    setc(0, 0)
    one300 = _drops(Cb, p, 0, 300)
    big = inv(45, 45, 45, 45)
    for _k in range(100):
        p.setProperty("combat.i0.stored", str(int(M.stored(CK, p, 0)) + 3))
        Core.collect(ou, key, CK, 0, big)
    K.eq(_invd(L, big, one300), one300, "GC fix 1: 100 Collects of 3 pay exactly what one roll of 300 pays (%d kinds)" % len(one300))
    K.eq(sum(one300.values()) + int(M.stored(CK, p, 0)), 300, "GC fix 1: ... nothing lost (the rest waits in the pool: %d)" % int(M.stored(CK, p, 0)))
    lr3 = dict((str(i), int(q)) for i, q in zip(*Cb.dropsFor(p, 0, 3)) if int(q) > 0)
    old100 = dict((k_, 100 * v_) for k_, v_ in lr3.items())
    K.check(old100 != one300, "GC fix 1: ... where 100 largest-remainder rolls of 3 (0.4.21's way) would pay a different mix: %s vs %s" % (old100, one300))
    p.setProperty("combat.i0.rolled", "999999"); p.setProperty("combat.i0.stored", "7")   # a saved count that no longer fits (a hand edit / a new pool): starts over, never pays more
    r = Cb.rollFor(p, 0, 7)
    K.check(0 <= sum(int(q) for q in r[1]) <= 7 and all(int(q) >= 0 for q in r[1]), "GC fix 1: a stale rolled count never pays more than the pool (pays %d of 7, C %s)" % (sum(int(q) for q in r[1]), r[2]))
    # 3. a full inventory: nothing moves, nothing lost
    setc(300, 200)
    full = inv(1)
    Inv.give(full, "Rock_Stone_Cobble", JLong(100))
    r = str(Core.collectKind(ou, key, CK, X, full))
    K.check(r.startswith("-Your inventory is full"), "GC a full inventory (one kind): %s" % r)
    K.eq(_gd(Core, CK, p), want, "GC ... the store still holds every kind")
    r = str(Core.collect(ou, key, CK, -1, full))
    K.check(r.startswith("-Your inventory is full"), "GC a full inventory (Collect all): %s" % r)
    K.eq(_gd(Core, CK, p), want, "GC ... still every kind")
    # 4. one free slot: what fits comes out, the rest stays AS THOSE KINDS
    setc(300, 200)
    one = inv(1)
    r = str(Core.collect(ou, key, CK, -1, one))
    got1 = _invd(L, one, want)
    K.check(r.startswith("+Collected") and 0 < sum(got1.values()) <= 100 and "stay in the shard" in r, "GC one free slot, Collect all: %s" % r[:100])
    K.eq(_sum(got1, _gd(Core, CK, p)), want, "GC ... inventory + store = what was there (no dupe, no loss)")
    Z = [i for i in want if i not in got1][0]
    two = inv(1)
    r = str(Core.collectKind(ou, key, CK, Z, two))
    K.eq(int(count(two, Z)), min(want[Z], 100), "GC one free slot, one kind: a stack of it (%s)" % r[:60])
    K.eq(_sum(got1, _invd(L, two, want), _gd(Core, CK, p)), want, "GC ... still nothing lost or doubled")
    disk = open(os.path.join(str(St.DIR), key + ".properties"), encoding="utf8").read().replace(chr(92) + ":", ":")
    K.check(("combat.i0.drops=" + str(p.getProperty("combat.i0.drops"))) in disk, "GC ... the file = memory (the back-out was saved)")
    # 5. the rolled drops use the storage: a full one makes nothing
    setc(0, 0)
    capi = int(M.capOf(CK, p, 0))
    p.setProperty("combat.i0.drops", "Ingredient_Bone_Fragment:%d" % capi)
    p.setProperty("combat.i0.last", str(T0 - 5 * H))
    made = int(M.settle(CK, p, 0, JLong(T0)))
    K.check(made == 0 and int(M.stored(CK, p, 0)) == 0, "GC rolled drops at the cap: the Soul Cage makes nothing (made %d)" % made)
    p.setProperty("combat.i0.drops", "Ingredient_Bone_Fragment:%d" % (capi - 5))
    p.setProperty("combat.i0.last", str(T0 - 5 * H))
    made = int(M.settle(CK, p, 0, JLong(T0)))
    K.check(made == 5 and int(M.usedOf(CK, p, 0)) == capi, "GC ... 5 below the cap: 5 made, then full (made %d)" % made)
    # 6. a bad drops line: the good entries count, the rest is skipped (no error)
    p.setProperty("combat.i0.drops", "Ingredient_Bone_Fragment:5,bad,x:y,:3,Ingredient_Bone_Fragment:-2,Ingredient_Bone_Fragment:1")
    K.eq(int(M.heldN(CK, p, 0)), 6, "GC a bad drops line: only the good entries (6)")
    p.remove("combat.i0.drops")
    # 7. the bag cell: every island's bags
    bx = {"calls": []}
    T421._put(L, "gear:fn:box", PyFn(T421._bagbox(L, ou, bx)))
    from jpype import JObject, JInt, JArray
    T421._put(L, "skill:fn:run", PyFn(lambda a: JArray(JObject)([JInt(20), JInt(1000), JLong(0), JLong(0), JObject(False, "java.lang.Boolean"), JString("Combat.Warrior")])))
    Cb.LVL.clear()
    setc(0, 0)
    p.setProperty("combat.i0.bags", "3"); p.setProperty("combat.i1.bags", "2")
    _save(St, key, p)
    U0 = int(Cfg.UNDER.get())
    cs = inv(27)
    r = str(Core.collectKind(ou, key, CK, "#bags", cs))
    K.check(r.startswith("+Collected 5 unidentified bags") and int(M.bags(p, 0)) == 0 and int(M.bags(p, 1)) == 0, "GC the bag cell takes both islands' bags: %s" % r)
    K.eq(int(count(cs, "Skyy_Unid_Bag_Normal")), 5, "GC ... five bags in the inventory")
    K.eq(int(Cfg.UNDER.get()), U0, "GC ... no bridge asked under the lock")
    p.setProperty("combat.i0.bags", "3"); p.setProperty("combat.i1.bags", "2")
    cs = inv(2)
    r = str(Core.collectKind(ou, key, CK, "#bags", cs))
    K.check(r.startswith("+Collected 2 unidentified bags") and "3 stay stored" in r and int(M.bags(p, 0)) + int(M.bags(p, 1)) == 3, "GC ... a short inventory: 2 out, 3 stay: %s" % r)
    r = str(Core.collectKind(ou, key, CK, "#bags", full))
    K.check(r.startswith("-Your inventory is full"), "GC ... a full inventory: %s" % r)
    K.check(str(Core.collectKind(ou, key, FK, "#bags", inv(9))).startswith("-Only combat"), "GC ... only on the Combat Shard")
    K.check(str(Core.collectKind(ou, key, CK, "", inv(9))).startswith("-Pick an item"), "GC an empty id is refused")
    # 8. rollback: 0.4.21 never reads <kind>.i<n>.drops; a save keeps the key
    K.check(not re.search(r'ik\([^)]*"drops"', open(GEN_OLD, encoding="utf8").read()), "GC rollback: the 0.4.21 build never reads <kind>.i<n>.drops")
    p.setProperty("combat.i1.drops", "Ingredient_Bone_Fragment:9")
    _save(St, key, p)
    K.check("combat.i1.drops=Ingredient_Bone_Fragment\\:9" in open(os.path.join(str(St.DIR), key + ".properties"), encoding="utf8").read(), "GC rollback: the drops line survives a save")
    K.save()


def run_farm(out, jar, scratch, _home):
    from jpype import JLong, JString
    K = HK.Child(out)
    L, ou, W_, p, lv = T420._W0(os.path.join(scratch, "gf"), K)
    M, St, Core, Cfg, Inv, Kind = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShInv"], L["ShKind"]
    M.ONLINE.put(OWNER, True)
    Core.NOW_TEST = T0
    got = T420._kit(L, p, K)
    p.setProperty("farming.auto", "1"); p.setProperty("farming.paused", "0"); p.setProperty("farming.storage", "5")
    C = "Plant_Crop_Carrot_Item"
    BON = str(Kind.BONUS[FK])

    def setst(s, cmp_=0, leg=None, ench=0):
        p.setProperty("farming.i0.stored", str(s)); p.setProperty("farming.i0.last", str(T0)); p.setProperty("farming.compactor", str(cmp_))
        for f in ("xpn", "xpw", "ench", "legacy"):
            p.remove("farming.i0." + f)
        if leg:
            p.setProperty("farming.i0.legacy", leg)
        if ench:
            p.setProperty("farming.i0.ench", str(ench))
        got["coll"].clear(); got["xp"] = 0
        _save(St, OWNER, p)
    # the base cell
    setst(250)
    K.eq(_gd(Core, FK, p), {W: 250}, "GF one island, no Compactor: one Wheat cell")
    cs = L["inv"](45, 45)
    w0 = int(L["count"](cs, W))
    r = str(Core.collectKind(ou, JString(OWNER), FK, W, cs))
    K.check(r.startswith("+Collected 250") and int(L["count"](cs, W)) - w0 == 250 and int(M.stored(FK, p, 0)) == 0, "GF a Wheat click: %s" % r[:90])
    K.eq(got["coll"].get(W, 0), 250, "GF ... the Wheat collection +250 (as Collect all)")
    K.check(got["xp"] > 0, "GF ... and Farming XP (%d)" % got["xp"])
    # the Enchanted stock (legacy) and the loose rest are two cells
    setst(12345, 1)
    M.settle(FK, p, 0, JLong(T0))
    K.eq(_gd(Core, FK, p), {E: 123, W: 45}, "GF with a Compactor: 123 Enchanted + 45 Wheat")
    g = _grid(Core, FK, p)
    K.eq([x[0] for x in g], [W, E], "GF the Enchanted item sits right after its base item")
    cs = L["inv"](45, 45)
    w0, e0 = int(L["count"](cs, W)), int(L["count"](cs, E))
    r = str(Core.collectKind(ou, JString(OWNER), FK, W, cs))
    K.check(int(L["count"](cs, W)) - w0 == 45 and int(L["count"](cs, E)) == e0 and int(M.comp(FK, p, 0)) == 123, "GF a Wheat click leaves the Enchanted stock: %s" % r[:80])
    got["coll"].clear()
    r = str(Core.collectKind(ou, JString(OWNER), FK, E, cs))
    K.check(int(L["count"](cs, E)) - e0 == 123 and int(M.comp(FK, p, 0)) == 0 and p.getProperty("farming.i0.legacy") is None, "GF an Enchanted click: 123 out: %s" % r[:80])
    K.eq(got["coll"].get(W, 0), 12300, "GF ... credited as 12,300 Wheat (the 0.4.20 rule)")
    # the Enchanted part of a stored count (the legacy line holds another item, so nothing compresses): two cells + the old item
    setst(250, 1, leg=C + ":7")
    M.settle(FK, p, 0, JLong(T0))
    K.eq(_gd(Core, FK, p), {E: 2, W: 50, C: 7}, "GF legacy of another item: 2 Enchanted + 50 Wheat + 7 Carrot")
    cs = L["inv"](45, 45)
    w0, e0, c0 = int(L["count"](cs, W)), int(L["count"](cs, E)), int(L["count"](cs, C))
    r = str(Core.collectKind(ou, JString(OWNER), FK, E, cs))
    K.check(int(L["count"](cs, E)) - e0 == 2 and int(L["count"](cs, W)) == w0 and int(M.stored(FK, p, 0)) == 50 and str(p.getProperty("farming.i0.legacy")) == C + ":7",
            "GF an Enchanted click takes only the full hundreds (50 Wheat + the Carrot stay): %s" % r[:80])
    r = str(Core.collectKind(ou, JString(OWNER), FK, C, cs))
    K.check(int(L["count"](cs, C)) - c0 == 7 and p.getProperty("farming.i0.legacy") is None and int(M.stored(FK, p, 0)) == 50, "GF the old item's click: %s" % r[:80])
    r = str(Core.collectKind(ou, JString(OWNER), FK, W, cs))
    K.check(int(L["count"](cs, W)) - w0 == 50 and int(M.stored(FK, p, 0)) == 0, "GF the rest: %s" % r[:80])
    # the bonus finds share their item's cell
    setst(0, 1, leg=E + ":3", ench=5)
    gd = _gd(Core, FK, p)
    K.eq(gd.get(BON, 0) + (gd.get(E, 0) if BON != E else 0), 8 if BON == E else 5, "GF the bonus finds (%s) in the grid: %s" % (BON, gd))
    cs = L["inv"](45, 45)
    b0 = int(L["count"](cs, BON))
    r = str(Core.collectKind(ou, JString(OWNER), FK, BON, cs))
    K.check(int(L["count"](cs, BON)) - b0 == (8 if BON == E else 5) and int(M.ench(FK, p, 0)) == 0, "GF a bonus click: %s" % r[:100])
    # Collect all after clicks = the same credit as one Collect all
    setst(345)
    cs = L["inv"](45, 45)
    Core.collectKind(ou, JString(OWNER), FK, W, cs)
    a1 = dict(got["coll"]); x1 = got["xp"]
    setst(345)
    Core.collect(ou, JString(OWNER), FK, -1, L["inv"](45, 45))
    K.check(dict(got["coll"]) == a1 and got["xp"] == x1, "GF a click credits what Collect all credits (%s / %d XP)" % (a1, x1))
    # a full inventory
    setst(250)
    full = L["inv"](1)
    Inv.give(full, "Rock_Stone_Cobble", JLong(100))
    r = str(Core.collectKind(ou, JString(OWNER), FK, W, full))
    K.check(r.startswith("-Your inventory is full") and int(M.stored(FK, p, 0)) == 250, "GF a full inventory: %s" % r)
    r = str(Core.collectKind(ou, JString(OWNER), FK, "Ore_Copper", L["inv"](9)))
    K.check(r.startswith("=None of that") and int(M.stored(FK, p, 0)) == 250, "GF an item this shard does not hold: %s" % r)
    K.save()


def run_page22(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString, JArray, JObject, JInt
    K = HK.Child(out)
    L, ou, W_, p, lv = T420._W0(os.path.join(scratch, "pg22"), K)
    M, Core, Cfg, Page, PyFn, St, Cb = L["ShMath"], L["ShCore"], L["ShCfg"], L["ShPage"], L["PyFn"], L["ShStore"], JClass(PKG + "ShCombat")
    Core.NOW_TEST = T0
    M.ONLINE.put(OWNER, True)
    Cfg.KEY_TEST = PyFn(lambda u: JString(OWNER))
    T420._kit(L, p, K)
    St.LOCK.lock()
    try:
        p.setProperty("farming.i0.stored", "12345"); p.setProperty("farming.i0.last", str(T0)); p.setProperty("farming.storage", "5")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    pg = Page(ou, W_)
    pg.kind = FK
    pg.view = 0

    def click(a):
        pg.handleDataEvent(None, None, json.dumps({"a": a}))
        r = T410.full(pg)
        K.check(not r["miss"] and not r["unbound"], "PG22 %s: the page walks clean %s %s" % (a, r["miss"][:2], r["unbound"][:2]))
        return T49._build(pg)
    bd = click("tab0")
    K.check(int(pg.sgN) >= 1 and str(pg.sgId[0]) == W and str(pg.sgQty[0]) == "12,345", "PG22 the Wheat cell with its full count: %s %s" % (list(pg.sgId)[:3], list(pg.sgQty)[:3]))
    K.check("#SkyyShGCell0" in bd["datas"] and ('"gc:%s"' % W) in bd["datas"]["#SkyyShGCell0"], "PG22 the cell's binding names the item: %s" % bd["datas"].get("#SkyyShGCell0"))
    K.check("#SkyyShGRow3" in bd["mk"] and "#SkyyShGCell23" in bd["mk"], "PG22 four rows of six cells always show (empty cells fill them)")
    K.check(str(pg.sgBg[0]).endswith("(0.4)") or str(pg.sgBg[0]).endswith("(0.15)"), "PG22 the rarity square: %s" % pg.sgBg[0])
    K.check("Click an item" in str(pg.sgHint), "PG22 the hint: %s" % pg.sgHint)
    K.check(bd["size"] < 1000000, "PG22 the packet stays small (%d bytes)" % bd["size"])
    K.check("ItemStack" not in bd["mk"] and 'ItemId: "' + W + '"' in bd["mk"], "PG22 the cells carry an item id only")
    Page.TEST_INV = L["inv"](45, 45, 45)   # an empty inventory with room for all of it
    w0 = int(L["count"](Page.TEST_INV, W))
    click("gc:" + W)
    K.check("Collected" in str(pg.stText) and int(M.stored(FK, p, 0)) == 0, "PG22 a cell click collects that kind: %s" % pg.stText)
    K.check(int(L["count"](Page.TEST_INV, W)) - w0 == 12345, "PG22 ... all 12,345 into the inventory")
    click("gc:" + W)
    K.check("None of that" in str(pg.stText), "PG22 a stale click (the kind is gone): %s" % pg.stText)
    K.eq(int(pg.sgN), 0, "PG22 the grid is empty now")
    K.check("Nothing is stored" in str(pg.sgHint), "PG22 the empty hint: %s" % pg.sgHint)
    # a co-op member who may not Collect (shard.coopCollect off): cells without bindings, its own hint, a crafted click refused
    St.LOCK.lock()
    try:
        p.setProperty("farming.i0.stored", "40")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    Cfg.COOP_COLLECT = False
    Cfg.KEY_TEST = PyFn(lambda u: JString(OWNER if str(u) == str(ou) else str(u)))   # the member has a profile of their own
    pv = Page(L["UUID"].fromString(MEMBER), W_)
    pv.kind = FK
    pv.view = 0
    pv.handleDataEvent(None, None, json.dumps({"a": "tab0"}))
    b3 = T49._build(pv)
    K.check(not bool(pv.manage) and int(pv.sgN) == 1, "PG22 the co-op view (no Collect) has the grid: %s" % list(pv.sgId))
    K.check(not any(s.startswith("#SkyyShGCell") for s in b3["datas"]) and "#SkyyShGCell0" in b3["mk"], "PG22 ... the cells, no buttons")
    K.check("island owner" in str(pv.sgHint), "PG22 ... and is told who collects: %s" % pv.sgHint)
    pv.handleDataEvent(None, None, json.dumps({"a": "gc:" + W}))
    K.check(int(M.stored(FK, p, 0)) == 40, "PG22 ... a crafted click moves nothing: %s" % pv.stText)
    Cfg.COOP_COLLECT = True
    Cfg.KEY_TEST = PyFn(lambda u: JString(OWNER))
    # the Combat tab: drops sorted, the bag cell only with SkyyGear
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.type", "skeleton"); p.setProperty("combat.i0.size", "1"); p.setProperty("combat.auto", "1"); p.setProperty("combat.storage", "1")
        p.setProperty("combat.placed", "skyy-island-" + OWNER + "|1|2|3"); p.setProperty("combat.i0.last", str(T0)); p.setProperty("combat.i0.stored", "60"); p.setProperty("combat.i0.bags", "3")
        p.remove("combat.i0.drops"); p.remove("combat.i0.ench"); p.remove("combat.i0.legacy")
        p.setProperty("combat.i0.totems", "soul_cage:1:::0:ddd422")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    T421._put(L, "skill:fn:run", PyFn(lambda a: JArray(JObject)([JInt(34), JInt(1000), JLong(0), JLong(0), JObject(False, "java.lang.Boolean"), JString("Combat.Warrior")])))
    Cb.LVL.clear()
    pg.kind = CK
    U0 = int(Cfg.UNDER.get())
    click("tab0")
    K.eq(int(Cfg.UNDER.get()), U0, "PG22 the page asks no bridge under the lock")
    ids = [str(x) for x in pg.sgId]
    K.check("#bags" not in ids, "PG22 no bag cell without SkyyGear (its icon id might not exist): %s" % ids[-2:])
    want = _sum(_drops(Cb, p, 0, int(M.stored(CK, p, 0))), {str(L["ShKind"].BONUS[CK]): int(M.ench(CK, p, 0))})   # the pool split + the rare finds (Collect pays both)
    K.check(sum(want.values()) >= 60 - len(want), "PG22 the Soul Cage's store (%d)" % sum(want.values()))
    K.eq(dict((str(i), int(str(q).replace(",", ""))) for i, q in zip(pg.sgId, pg.sgQty)), want, "PG22 the combat cells = the pool split")
    bx = {"calls": []}
    T421._put(L, "gear:fn:box", PyFn(T421._bagbox(L, ou, bx)))
    bd = click("tab0")
    ids = [str(x) for x in pg.sgId]
    K.check(ids[-1] == "#bags" and str(pg.sgIc[len(ids) - 1]) == "Skyy_Unid_Bag_Normal" and str(pg.sgQty[len(ids) - 1]) == "3", "PG22 the bag cell last, 3 bags: %s" % ids[-2:])
    K.check(('"gc:#bags"') in bd["datas"].get("#SkyyShGCell%d" % (len(ids) - 1), ""), "PG22 ... its binding")
    click("gc:#bags")
    K.check("3 unidentified bags" in str(pg.stText) and int(M.bags(p, 0)) == 0, "PG22 the bag cell collects: %s" % pg.stText)
    one = [i for i in want][0]
    click("gc:" + one)
    K.check("Collected" in str(pg.stText) and one not in [str(x) for x in pg.sgId], "PG22 a combat cell collects its kind: %s" % pg.stText)
    K.check(str(Page.gQtyTxt(JLong(9999999))) == "9,999,999" and str(Page.gQtyTxt(JLong(12345678))) == "12M", "PG22 the count text: full up to 9,999,999")
    K.save()


EXPECT = {   # 0.4.21 -> 0.4.22, checked by hand 2026-11-14: the version texts (CfgFn / CfgRows / ShFill.markFixed's @VERSION@ log line / ShStore.migrate + migrate2 + save / ready line) + the round
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~m header'],
    'ShAdmin': ['~m run'],
    'ShCombat': ['+m cum', '+m rollFor'],
    'ShCore': ['+f BAG_ICON', '+f RARS', '+f RAR_BG', '+f RAR_NONE', '+f RAR_SPEC', '+f TIERS', '+f TIER_SPEC', '+m collect0', '+m collectBagsAll', '+m collectKind', '+m gAdd',
               '+m gridCmp', '+m gridOf', '+m rarBg', '+m rarOf', '+m roll', '+m specMap', '+m tierOf', '+m unroll', '~<clinit>', '~m collect0'],
    'ShFill': ['~m markFixed'],
    'ShMath': ['+m held', '+m heldN', '+m heldSet', '~m usedOf'],
    'ShPage': ['+f sgBg', '+f sgHint', '+f sgIc', '+f sgId', '+f sgN', '+f sgQty', '+m gQtyTxt', '+m gridFill', '~m act', '~m buildFull', '~m fill'],
    'ShStore': ['~m migrate', '~m migrate2', '~m save'],
    'SkyyShardsPlugin': ['~m setup'],
}


def run_live(out, jar, scratch, home):
    T421.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run_compare = T419._compare
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("combat22", run_combat), ("farm22", run_farm), ("page22", run_page22),
                   ("geo", T421.run_geo), ("rebuild", T421.run_rebuild), ("level", T421.run_level), ("bags", T421.run_bags), ("page21", T421.run_page21),
                   ("comp", T420.run_comp), ("sell20", T420.run_sell), ("mig20", T420.run_mig20), ("ore", T420.run_ore), ("deb", T420.run_deb), ("page20", T420.run_page20), ("livecomp", T420.run_livecomp),
                   ("off", T419.run_off), ("mig", T419.run_mig), ("sell", T419.run_sell), ("page", T419.run_page),
                   ("open", T416._h(T416._g(T416.run_open), True)), ("bytecode", T415.run_bytecode),
                   ("flows3", T416._h(T416._g(T413.run_flows3))), ("page49", T419.run_page49),
                   ("live", run_live)],
           script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
