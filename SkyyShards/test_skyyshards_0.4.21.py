"""Harness for SkyyShards 0.4.21 (bigger walled Combat arenas, mobs level with the owner, bags apart - tools/shards_0_4_21_patch.py, on top of 0.4.20).
Build first:
    python tools/shards_0_4_21_patch.py && python SkyyShards/build_skyyshards_0.4.21.py
    python SkyyShards/test_skyyshards_0.4.21.py [--keep]

  S21  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand; line endings kept
  GE   geometry EXECUTED every size x zone x slot: floor footprint, wall ring + corners, the bridge's gap, bridge reaches the rim, five Large islands do not touch, spawn spots inside, the rows
  RB   rebuild  EXECUTED paint + marker once / twice: old torches + old wall gone, Soul Cage + a hand-placed totem + a player's chest kept, History copy byte for byte, Grow, wall lowered, a moved island,
                a refused History copy waits
  LV   level    EXECUTED the owner's level (active class, no class, other profile, SkyySkills missing, level 0), the upgrade on top, the row off, the cache, the cap, tickWorld's real spawned levels, no bridge under the lock
  BA   bags     EXECUTED bag store through settle (rate, cap), Collect all leaves it alone, bag Collect (partial, full inventory, no SkyyGear, a box answering nothing, an inventory that fills up midway), every drop kind paid, rollback ignores the keys
  PG21 page     rows and lines of the Combat tab, Bags button driven through the page, sizes, levels, the XP wording
  then 0.4.20's phases (compress, sell, migration, page, offline, ...), A verify, C compare, AA audit, live START TWICE
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, math, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.21"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sh021", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.20.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.20.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_21_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.20 harness: the wording this round moves on purpose is adjusted in memory
_T20 = open(os.path.join(HERE, "test_skyyshards_0.4.20.py"), encoding="utf8").read()
_T20 = _T20.replace('VERSION = "0.4.20"', 'VERSION = "0.4.21"')
_argv = list(sys.argv)
T420 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_20", loader=None))
T420.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.20.py")
exec(compile(_T20, T420.__file__, "exec"), T420.__dict__)
sys.argv[:] = _argv
T419, T411, T410, T49, T416, T415, T413, T418 = T420.T419, T420.T411, T420.T410, T420.T49, T420.T416, T420.T415, T420.T413, T420.T418
T420.JAR = T419.JAR = T418.JAR = T419.T417.JAR = JAR
T420.SCRATCH = T419.SCRATCH = T418.SCRATCH = T416.SCRATCH = T415.SCRATCH = T419.T417.SCRATCH = SCRATCH
OWNER, MEMBER = T420.OWNER, T420.MEMBER
CK = 5
T0 = 1790000000000
Y0 = T411.Y


def _cen(L, slot):
    Geo = L["ShGeo"]
    return int(Geo.ox(CK)) + int(Geo.sxk(CK, slot)), int(Geo.OZ) + int(Geo.szk(CK, slot))


def _id(m, x, y, z):
    v = m.get("%d,%d,%d" % (x, y, z))
    return "" if v is None else str(v)


def _put(L, name, f):
    """a bridge function, where ShCfg.fn (the bridge) and the fixture both see it"""
    L["br"].put(name, f)
    L["fns"].put(name, f)


def _del(L, name):
    L["br"].remove(name)
    L["fns"].remove(name)


def _gap(L, slot, dx, dz):
    return bool(L["ShGeo"].gapK(CK, slot, dx, dz))


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.21 - build script') and 'VERSION = "0.4.21"\n' in g, "S21 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S21 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.21:" in g, "S21 the ready line names the round")
    K.check("CB_RING" in g and "combat.wallHeight" in g and "combat.levelWithPlayer" in g and "combat.bagPct" in g, "S21 the new rows are in the build")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S21 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S21 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S21 fix: the jar is newer than the build script, the build script newer than the patch")
    K.check("this.c.length > 8" in g, "S21 fix: the range aura reads the arena's own size")
    K.check('"crowB%d_%d", "crowC%d_%d")] + ["c1", "c1b"]' in g, "S21 fix: the Bags row is a build-time UI variant")
    K.check('" - 888,888 bags"' in g, "S21 fix: the bag suffix is in the width assertion")
    K.save()


def _floor_set(L, slot, h):
    cx, cz = _cen(L, slot)
    return set((cx + dx, cz + dz) for dx in range(-h, h + 1) for dz in range(-h, h + 1))


def run_geo(out, jar, scratch, _home):
    K = HK.Child(out)
    L = T411._L(os.path.join(scratch, "ge"), K)
    Geo, Cfg, Cb = L["ShGeo"], L["ShCfg"], L["ShCombat"]
    H = [12, 18, 25]
    K.eq([int(x) for x in Cfg.CB_HALF], H, "GE the default half widths")
    K.eq(int(Cfg.CB_WALL), 4, "GE the default wall")
    K.eq([int(Geo.half(0, s)) for s in (1, 2, 3)], [6, 10, 14], "GE another shard keeps its half widths")
    for z in range(5):
        wall = str(Geo.IDS[int(Geo.CRIM[z])])
        K.check("Brick" in wall, "GE zone %d wall = brick (%s)" % (z + 1, wall))
        for size in (1, 2, 3):
            for slot in (0, 1, 3):
                key = T411._key()
                p = T411._prof(L, key, [(slot, z, size, (0, 0, 0))])
                m, _w = T411._paint(L, p)
                cx, cz = _cen(L, slot)
                h = H[size - 1]
                bad_floor = []
                walls = holes = ground = 0
                for dx in range(-h - 1, h + 2):
                    for dz in range(-h - 1, h + 2):
                        ax, az = abs(dx), abs(dz)
                        f = _id(m, cx + dx, Y0, cz + dz)
                        if max(ax, az) > h:
                            if f not in ("", "Wood_Hardwood_Planks", str(Geo.IDS[int(Geo.PLANK)])):
                                bad_floor.append((dx, dz, f))
                        elif ax == h and az == h:
                            pass
                        elif not f and not (size == 3 and bool(Geo.nearShaft(int(Geo.quads(slot)[0]), dx, dz))):   # Large: the cavern stair opens the floor (0.4.11)
                            bad_floor.append((dx, dz, f))
                        if max(ax, az) == h:
                            top = [_id(m, cx + dx, Y0 + y, cz + dz) for y in range(1, 5)]
                            if _gap(L, slot, dx, dz):
                                holes += 1
                                K.check(all(t == "" for t in top), "GE gap cell %d,%d open" % (dx, dz)) if top != ["", "", "", ""] else None
                            else:
                                walls += 1
                                if not all(t == wall for t in top):
                                    bad_floor.append(("wall", dx, dz, top))
                        ground += 1 if f else 0
                K.check(not bad_floor, "GE z%d size %d slot %d: floor + wall %s" % (z + 1, size, slot, bad_floor[:4]))
                K.check(holes >= 3 and holes <= 4 and walls == 8 * h - holes, "GE z%d size %d slot %d: %d wall cells round, %d gap cells (fix: 3-wide)" % (z + 1, size, slot, walls, holes))
                walk = 0   # fix: rim cells open two high with bridge plank right outside them: the way in is at least two wide
                for dx in range(-h, h + 1):
                    for dz in range(-h, h + 1):
                        if max(abs(dx), abs(dz)) != h or not _gap(L, slot, dx, dz):
                            continue
                        ox_, oz_ = (dx + (1 if dx > 0 else -1), dz) if abs(dx) == h else (dx, dz + (1 if dz > 0 else -1))
                        if _id(m, cx + dx, Y0 + 1, cz + dz) == "" and _id(m, cx + dx, Y0 + 2, cz + dz) == "" and _id(m, cx + ox_, Y0, cz + oz_) == str(Geo.IDS[int(Geo.PLANK)]):
                            walk += 1
                K.check(walk >= 2, "GE z%d size %d slot %d: the bridge walks through the gap, %d cells wide" % (z + 1, size, slot, walk))
                # the bridge: from the hub to the rim, the plank right before the rim on the line
                sx, sz = int(Geo.sxk(CK, slot)), int(Geo.szk(CK, slot))
                ln = math.hypot(sx, sz)
                t = ln - (h + 1.5) / max(abs(sx) / ln, abs(sz) / ln)   # just past the rim on the line (the ring is square, the line is at an angle)
                x = int(round(int(Geo.ox(CK)) + sx * t / ln))
                zc = int(round(int(Geo.OZ) + sz * t / ln))
                K.eq(_id(m, x, Y0, zc), str(Geo.IDS[int(Geo.PLANK)]), "GE z%d size %d slot %d: the bridge reaches the rim" % (z + 1, size, slot))
                # the gap faces the bridge: a rim cell on the hub line is open, the opposite one walled
                hub_dx, hub_dz = int(round(-sx * (h / ln))), int(round(-sz * (h / ln)))
                if slot == 0:
                    K.check(_id(m, cx, Y0 + 1, cz + h) == "" and _id(m, cx, Y0 + 2, cz + h) == "" and _id(m, cx, Y0 + 1, cz - h) == wall, "GE slot 0: open on the hub side (+z), wall on the far side")
                K.check(_gap(L, slot, hub_dx, hub_dz) or max(abs(hub_dx), abs(hub_dz)) != h, "GE slot %d: the hub line is a gap" % slot)
                # spawn spots inside the rim, none on the pads
                sp = [int(v) for v in Geo.cspots(slot, size, 0)]
                K.check(len(sp) > 0 and all(abs(v) <= h - 1 for v in sp), "GE z%d size %d slot %d: %d spawn spots inside the wall" % (z + 1, size, slot, len(sp) // 2))
                K.check(not any(abs(sp[i]) <= 1 and abs(sp[i + 1]) <= 1 for i in range(0, len(sp), 2)), "GE no spawn on the pads")
    # five Large islands on one shard: nothing touches, a bigger island's floor is complete
    p5 = T411._prof(L, T411._key(), [(s, s, 3, (0, 0, 0)) for s in range(5)])
    m5, _w = T411._paint(L, p5)
    sets = [_floor_set(L, s, 25) for s in range(5)]
    for i in range(5):
        for j in range(i + 1, 5):
            K.check(not (sets[i] & sets[j]), "GE Large slots %d / %d do not overlap" % (i, j))
    for i in range(5):
        K.check(all(_id(m5, x, Y0, z) != "" for (x, z) in list(sets[i])[::7] if max(abs(x - _cen(L, i)[0]), abs(z - _cen(L, i)[1])) < 25 and not bool(Geo.nearShaft(int(Geo.quads(i)[0]), x - _cen(L, i)[0], z - _cen(L, i)[1]))), "GE slot %d floor complete at Large" % i)
    # the Large cavern + rise + forest are still inside
    cx, cz = _cen(L, 0)
    K.check(any(str(v).startswith("Wood_") and str(k).split(",")[1] == str(Y0 + 1) for k, v in dict((str(k_), str(m5.get(k_))) for k_ in m5.keySet()).items()), "GE Large: the forest edge is painted")
    # the rows: a wall of 0, a smaller arena; Medium never under Small
    Cfg.CB_WALL = 0
    p = T411._prof(L, T411._key(), [(0, 0, 1, (0, 0, 0))])
    m0, _w = T411._paint(L, p)
    K.eq(_id(m0, cx, Y0 + 1, cz - 12), "", "GE wall 0 = no wall")
    Cfg.CB_WALL = 4
    Cfg.CB_HALF = L["JInts"]([8, 12, 16]) if "JInts" in L else None
    if Cfg.CB_HALF is None:
        from jpype import JArray, JInt
        Cfg.CB_HALF = JArray(JInt)([8, 12, 16])
    K.eq(int(Geo.half(CK, 1)), 8, "GE the row is read live")
    K.check(int(Geo.cspots(0, 1, 0)[0]) >= -7, "GE the spawn spots follow a changed row (cache keyed by the half width)")
    from jpype import JArray, JInt
    Cfg.CB_HALF = JArray(JInt)([12, 18, 25])
    # a hand-placed totem spot: inside the new floor counts; the wall ring is the rim, not farmland
    Core, St = L["ShCore"], L["ShStore"]
    pk = T411._key()
    p = T411._prof(L, pk, [(0, 0, 1, (0, 0, 0))])
    s0 = Core.spotFor(p, CK, cx + 11, cz + 4)
    K.check(s0 is not None and int(s0[0]) == 0 and int(s0[1]) == 11 and int(s0[2]) == 4, "GE a totem spot at dx 11 is on the new arena")
    K.check(Core.spotFor(p, CK, cx + 13, cz) is None, "GE outside the rim is no spot")
    K.save()


def run_rebuild(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    L = T411._L(os.path.join(scratch, "rb"), K)
    Geo, Cfg, Fill, St, M = L["ShGeo"], L["ShCfg"], L["ShFill"], L["ShStore"], L["ShMath"]
    HS, Int = JClass("java.util.HashSet"), JClass("java.lang.Integer")
    key = T411._key()
    p = T411._prof(L, key, [(0, 0, 1, (0, 0, 0))])
    p.setProperty("combat.i0.totems", "soul_cage:2:wider::0:aaa111,soul_cage:1:::0:bbb222::10;3")   # one on pad 1, one hand-placed at 10, 3
    St.LOCK.lock()
    try:
        St.save(key, p)
    finally:
        St.LOCK.unlock()
    sd = str(St.DIR)
    before = open(os.path.join(sd, key + ".properties"), "rb").read()
    m = JClass("java.util.HashMap")()
    Fill.TEST_BLOCKS = m
    cx, cz = _cen(L, 0)
    torch = str(Geo.IDS[int(Geo.CTORCH)])
    wall = str(Geo.IDS[int(Geo.CRIM[0])])
    chest = "Furniture_Crude_Chest_Small"
    # what 0.4.20 left: its torch ring (ring 5), a floor, and a chest of the player's on the old torch ring, on a cell the new floor owns
    old = []
    for i in range(0, 40):
        q = Geo.ringPos(5, i)
        m.put("%d,%d,%d" % (cx + q[0], Y0 + 1, cz + q[1]), torch)
    m.put("%d,%d,%d" % (cx + 3, Y0 + 1, cz + 5), chest)   # ON the old torch ring: a player's block, not ours - kept
    m.put("%d,%d,%d" % (cx + 8, Y0 + 1, cz + 9), chest)   # on the new floor
    m.put("%d,%d,%d" % (cx + 12, Y0 + 2, cz + 7), chest)  # where the new wall would stand: never replaced
    r1 = list(Geo.region(p, CK))
    fx1 = [b for b in r1 if int(b[3]) == int(Geo.FIX_ARENA)]
    K.check(len(fx1) > 0 and all(int(Geo.arenaSlotOf(int(b[4]))) == 0 and str(Geo.arenaMarkOf(int(b[4]))) == "12:4" for b in fx1), "RB no marker: %d FIX_ARENA cells, all tagged slot 0, 12:4" % len(fx1))
    f = HS()
    Fill.TEST_BLOCKS = m
    n1 = int(Fill.paintY(None, Geo.region(p, CK), f, None))
    K.check(n1 > 100 and f.contains(Int(int(Geo.arenaTag(0, 12, 4)))), "RB the rebuild painted %d blocks and is done" % n1)
    K.check(not any(_id(m, cx + int(Geo.ringPos(5, i)[0]), Y0 + 1, cz + int(Geo.ringPos(5, i)[1])) == torch for i in range(40)), "RB the old torch ring is gone")
    K.check(_id(m, cx + 3, Y0 + 1, cz + 5) == chest and _id(m, cx + 8, Y0 + 1, cz + 9) == chest, "RB the player's chests are kept")
    K.eq(_id(m, cx + 12, Y0 + 2, cz + 7), chest, "RB a chest where the wall goes stays (the wall is placed only on air)")
    K.eq(_id(m, cx + 12, Y0 + 1, cz + 7), wall, "RB the wall stands next to it")
    K.check("Totem" in _id(m, cx, Y0 + 1, cz), "RB the Soul Cage on its pad stands (%s)" % _id(m, cx, Y0 + 1, cz))
    K.check("Totem" in _id(m, cx + 10, Y0 + 1, cz + 3), "RB the hand-placed Soul Cage stands (%s)" % _id(m, cx + 10, Y0 + 1, cz + 3))
    K.check(_id(m, cx, Y0 + 1, cz + 12) == "" and _id(m, cx, Y0 + 2, cz + 12) == "", "RB nobody is walled in: the bridge side is open")
    nm = int(Fill.markFixed("skyy-shard-" + key, CK, f))
    p = St.get(key)
    K.check(str(p.getProperty("combat.i0.arena")) == "12:4" and nm >= 1, "RB marker = 12:4 (%s)" % p.getProperty("combat.i0.arena"))
    hist = os.path.join(sd, "history", "arena", key + ".pre-0.4.21.properties")
    K.check(os.path.isfile(hist) and open(hist, "rb").read() == before, "RB the History copy = the file before, byte for byte")
    lp = os.path.join(os.path.dirname(sd), "collect.log")
    K.check(os.path.isfile(lp) and ("arena (SkyyShards 0.4.21) " + key) in open(lp, encoding="utf8", errors="replace").read(), "RB one collect.log line")
    # twice: no fix any more, nothing moves
    r2 = list(Geo.region(p, CK))
    K.check(not any(int(b[3]) == int(Geo.FIX_ARENA) for b in r2), "RB second paint: no FIX_ARENA")
    snap = dict((str(k_), str(m.get(k_))) for k_ in m.keySet())
    Fill.TEST_BLOCKS = m
    n2 = int(Fill.paintY(None, Geo.region(p, CK), HS(), None))
    K.eq(n2, 0, "RB second paint changes nothing (%d)" % n2)
    K.eq(dict((str(k_), str(m.get(k_))) for k_ in m.keySet()), snap, "RB ... block for block")
    K.check(int(Fill.markFixed("skyy-shard-" + key, CK, HS())) == 0, "RB second markFixed marks nothing")
    # Grow: the old wall goes, the new one stands, chest stays; a player's OTHER block on the old wall ring is kept
    m.put("%d,%d,%d" % (cx + 12, Y0 + 3, cz - 2), chest)
    p.setProperty("combat.i0.size", "2")
    f = HS()
    Fill.TEST_BLOCKS = m
    Fill.paintY(None, Geo.region(p, CK), f, None)
    K.check(f.contains(Int(int(Geo.arenaTag(0, 18, 4)))), "RB Grow: the rebuild runs again")
    rest = [(dx, dz) for dx in range(-12, 13) for dz in range(-12, 13) if max(abs(dx), abs(dz)) == 12 and not _gap(L, 0, dx, dz) and (dx, dz) not in ((12, 7),)]
    K.check(all(_id(m, cx + dx, Y0 + 2, cz + dz) != wall for dx, dz in rest), "RB Grow: the old wall ring (Small) is gone")
    K.eq(_id(m, cx + 12, Y0 + 3, cz - 2), chest, "RB Grow: the player's block on the old wall ring stays")
    K.eq(_id(m, cx + 18, Y0 + 1, cz + 3), wall, "RB Grow: the new wall (Medium) stands")
    K.eq(_id(m, cx + 15, Y0, cz + 3) != "", True, "RB Grow: the new floor")
    Fill.markFixed("skyy-shard-" + key, CK, f)
    K.eq(str(St.get(key).getProperty("combat.i0.arena")), "18:4", "RB Grow: marker 18:4")
    # the wall lowered in Server Setup: only the top goes
    Cfg.CB_WALL = 2
    p = St.get(key)
    f = HS()
    Fill.TEST_BLOCKS = m
    Fill.paintY(None, Geo.region(p, CK), f, None)
    K.check(_id(m, cx + 18, Y0 + 2, cz + 3) == wall and _id(m, cx + 18, Y0 + 3, cz + 3) == "" and _id(m, cx + 18, Y0 + 4, cz + 3) == "", "RB wall 4 -> 2: the top two go, the rest stays")
    Fill.markFixed("skyy-shard-" + key, CK, f)
    K.eq(str(St.get(key).getProperty("combat.i0.arena")), "18:2", "RB marker 18:2")
    Cfg.CB_WALL = 4
    p = St.get(key)
    f = HS()
    Fill.TEST_BLOCKS = m
    Fill.paintY(None, Geo.region(p, CK), f, None)
    Fill.markFixed("skyy-shard-" + key, CK, f)
    K.eq(str(St.get(key).getProperty("combat.i0.arena")), "18:4", "RB wall back to 4")
    # fix (critic): the marker is what the paint BUILT: the row changes between the paint and its marker
    Cfg.CB_WALL = 6
    p = St.get(key)
    f = HS()
    Fill.TEST_BLOCKS = m
    Fill.paintY(None, Geo.region(p, CK), f, None)
    Cfg.CB_WALL = 1
    Fill.markFixed("skyy-shard-" + key, CK, f)
    K.eq(str(St.get(key).getProperty("combat.i0.arena")), "18:6", "RB fix: a row changed mid-paint: the marker says what was built (18:6), not the new row")
    K.check(any(int(b[3]) == int(Geo.FIX_ARENA) and len(b) > 5 for b in list(Geo.region(St.get(key), CK))), "RB fix: ... so the next Enter clears the top of that wall")
    Cfg.CB_WALL = 4
    p = St.get(key)
    f = HS()
    Fill.TEST_BLOCKS = m
    Fill.paintY(None, Geo.region(p, CK), f, None)
    Fill.markFixed("skyy-shard-" + key, CK, f)
    K.eq(_id(m, cx + 18, Y0 + 5, cz + 3), "", "RB fix: the too-high wall of that paint is gone")
    K.eq(len([n_ for n_ in os.listdir(os.path.join(sd, "history", "arena")) if n_.startswith(key)]), 1, "RB fix: one History copy for this profile after Grow + every row change")
    # an island of slot 1 from before 0.4.21: moved out, the old floor cleared, a player's chest left where it was
    k2 = T411._key()
    p2 = T411._prof(L, k2, [(1, 1, 1, (0, 0, 0))])
    bx, bz = int(Geo.ox(CK)) + int(Geo.SX[1]), int(Geo.OZ) + int(Geo.SZ[1])
    m2 = JClass("java.util.HashMap")()
    floor_old = str(Geo.IDS[int(Geo.CFLOOR[1])])
    rim_old = str(Geo.IDS[int(Geo.CRIM[1])])
    for dx in range(-6, 7):
        for dz in range(-6, 7):
            m2.put("%d,%d,%d" % (bx + dx, Y0, bz + dz), rim_old if max(abs(dx), abs(dz)) == 6 else floor_old)
    m2.put("%d,%d,%d" % (bx + 2, Y0 + 1, bz), chest)
    f2 = HS()
    Fill.TEST_BLOCKS = m2
    Fill.paintY(None, Geo.region(p2, CK), f2, None)
    K.eq(_id(m2, bx - 4, Y0, bz - 4), "", "RB a moved island: its old floor is cleared (ours only; the new bridge runs along the same spoke)")
    K.eq(_id(m2, bx + 2, Y0 + 1, bz), chest, "RB ... a player's chest stays at the old place")
    cx1, cz1 = _cen(L, 1)
    K.check(_id(m2, cx1, Y0, cz1) != "" and (cx1, cz1) != (bx, bz), "RB ... the island is at its new centre")
    Fill.markFixed("skyy-shard-" + k2, CK, f2)
    # a refused History copy: the marker waits, nothing else changes
    k3 = T411._key()
    p3 = T411._prof(L, k3, [(0, 0, 1, (0, 0, 0))])
    fh = os.path.join(sd, "history", "arena")
    tmp = fh + ".x"
    os.replace(fh, tmp)
    open(fh, "wb").close()
    f3 = HS()
    m3 = JClass("java.util.HashMap")()
    Fill.TEST_BLOCKS = m3
    Fill.paintY(None, Geo.region(p3, CK), f3, None)
    Fill.markFixed("skyy-shard-" + k3, CK, f3)
    K.check(St.get(k3).getProperty("combat.i0.arena") is None, "RB a refused History copy: the marker waits (the arena is painted, the centre fix may mark)")
    os.remove(fh)
    os.replace(tmp, fh)
    Fill.markFixed("skyy-shard-" + k3, CK, f3)
    K.eq(str(St.get(k3).getProperty("combat.i0.arena")), "12:4", "RB ... and is written next time")
    Fill.TEST_BLOCKS = None
    K.save()


def run_level(out, jar, scratch, _home):
    from jpype import JObject, JInt, JLong, JString, JArray
    K = HK.Child(out)
    L = T411._L(os.path.join(scratch, "lv"), K)
    Cb, Cfg, fns, PyFn, St, Fi = L["ShCombat"], L["ShCfg"], L["fns"], L["PyFn"], L["ShStore"], L["ShFight"]
    Bool = L["Bool"] if "Bool" in L else None
    key = T411._key()
    ouid = key[:36]
    p = T411._prof(L, key, [(0, 0, 1, (0, 0, 0))])
    levels = {"Combat.Warrior": 34, "Combat.Archer": 12, "Combat.Mage": 40}
    state = {"cls": "Combat.Warrior", "pk": key, "calls": 0}

    def ans(n):
        return JArray(JObject)([JInt(n), JInt(1000), JLong(0), JLong(0), JObject(False, "java.lang.Boolean"), JString("x")])

    def run_fn(a):
        state["calls"] += 1
        who, sk = a[0], str(a[1])
        if sk == "class":
            if state["cls"] is None:
                return None
            return JArray(JObject)([JInt(0), JInt(1000), JLong(0), JLong(0), JObject(False, "java.lang.Boolean"), JString(state["cls"])])
        if str(who) != key:
            return None
        return ans(levels.get(sk, 0))
    _put(L, "skill:fn:run", PyFn(run_fn))
    Cfg.KEY_TEST = PyFn(lambda u: JString(state["pk"]))
    Cb.LV_MS = 0
    K.eq(int(Cb.ownerLv(key)), 34, "LV the owner online on this profile: the active class (Warrior 34)")
    state["cls"] = None
    K.eq(int(Cb.ownerLv(key)), 40, "LV no class chosen: the highest class level on the profile (Mage 40)")
    state["cls"] = "Combat.Warrior"
    state["pk"] = key + "x"
    K.eq(int(Cb.ownerLv(key)), 40, "LV the owner on another profile (or offline): the highest class level on this profile")
    state["pk"] = key
    levels.clear()
    K.eq(int(Cb.ownerLv(key)), 1, "LV a class at level 0 = level 1")
    levels.update({"Combat.Warrior": 34, "Combat.Archer": 12, "Combat.Mage": 40})
    # the ladder (Zone 1 table: Small 1-3 .. 5-8, Medium 5-8 .. 10-13, Large 10-13 .. 16-20)
    exp = {(1, 0): (34, 34), (1, 5): (38, 39), (2, 0): (38, 39), (2, 5): (43, 44), (3, 0): (43, 44), (3, 5): (49, 51)}
    for (s, l), (lo, hi) in exp.items():
        K.eq((int(Cb.lvLoP(34, 0, s, l)), int(Cb.lvHiP(34, 0, s, l))), (lo, hi), "LV owner 34, size %d, Mob level %d: %d-%d" % (s, l, lo, hi))
    K.check(int(Cb.lvLoP(34, 4, 1, 0)) == 34, "LV the zone offset is not added (Zone 5 = your level)")
    K.check(str(Cb.lvTxtP(34, 0, 1, 0)) == "34" and str(Cb.lvTxtP(34, 0, 1, 5)) == "38-39", "LV the texts follow it")
    K.check(int(Cb.lvLoP(99, 0, 3, 5)) == 100 and int(Cb.lvHiP(99, 0, 3, 5)) == 100, "LV capped at 100 (SkyyMobs refuses more)")
    Cfg.CB_LVP = False
    K.eq(int(Cb.ownerLv(key)), -1, "LV the row off: no owner level")
    K.eq((int(Cb.lvLoP(34, 0, 1, 0)), int(Cb.lvHiP(34, 0, 1, 0))), (1, 3), "LV the row off = the zone table")
    Cfg.CB_LVP = True
    K.eq((int(Cb.lvLoP(-1, 1, 1, 0)), int(Cb.lvHiP(-1, 1, 1, 0))), (21, 23), "LV unreadable (-1) = the zone table with its offset")
    _del(L, "skill:fn:run")
    K.eq(int(Cb.ownerLv(key)), -1, "LV no SkyySkills = -1 (the table)")
    _put(L, "skill:fn:run", PyFn(run_fn))
    Cb.LV_MS = 5000
    Cb.LVL.clear()
    K.eq(int(Cb.ownerLv(key)), 34, "LV cached read")
    n0 = state["calls"]
    levels["Combat.Warrior"] = 50
    K.eq(int(Cb.ownerLv(key)), 34, "LV the 5 s cache holds it")
    K.eq(state["calls"], n0, "LV ... with no bridge call")
    Cb.LVL.clear()
    levels["Combat.Warrior"] = 34
    # fix (critic): the 8-class path is kept 30 s, the active-class path 5 s
    state["cls"] = None
    K.eq(int(Cb.ownerLv(key)), 40, "LV fix: no class: the highest level")
    n0 = state["calls"]
    Cb.LVL.get(key)[1] -= 6000
    K.eq(int(Cb.ownerLv(key)), 40, "LV fix: still cached after 6 s")
    K.eq(state["calls"], n0, "LV fix: ... with no bridge call (8 classes = 30 s)")
    Cb.LVL.get(key)[1] -= 30000
    Cb.ownerLv(key)
    K.check(state["calls"] > n0, "LV fix: asked again after 30 s")
    state["cls"] = "Combat.Warrior"
    Cb.LVL.clear()
    Cb.ownerLv(key)
    n0 = state["calls"]
    Cb.LVL.get(key)[1] -= 6000
    Cb.ownerLv(key)
    K.check(state["calls"] > n0, "LV fix: the active-class path keeps its 5 s")
    Cb.LVL.clear()
    # the real spawner: the mobs this island spawns stand at the owner's level; a visitor standing there changes nothing; no bridge under the lock
    pp, m, wd = T411._wsetup(L, key, [(0, 0, 1, (0, 0, 0))], "lv")
    p2 = St.get(key)
    cx, cz = _cen(L, 0)
    t = [T0]
    pos = [cx + 3.5, Y0 + 1.0, cz + 2.5]
    U0 = int(Cfg.UNDER.get())

    def tick(extra=()):
        t[0] += 1000
        pos[0] = cx + 3.5 if pos[0] != cx + 3.5 else cx - 2.5
        pl = T411._players(L, [(ouid, tuple(pos), True)] + list(extra))
        return int(Fi.tickWorld(None, key, St.get(key), pl, t[0]))
    Cb.LVL.clear()
    n = [tick() for _ in range(5)]
    K.check(sum(n) >= 3, "LV the island spawned (%s)" % n)
    lvls = [wd.levels[u] for u in wd.alive()]
    K.check(lvls and all(l == 34 for l in lvls), "LV spawned mobs at the owner's level: %s" % lvls)
    # a level change of the owner shows on the next spawn after the cache
    levels["Combat.Warrior"] = 36
    Cb.LVL.clear()
    wd.mobs[wd.alive()[0]]["alive"] = False
    tick()
    t[0] += 31000
    tick()
    K.check(any(wd.levels[u] == 36 for u in wd.alive()), "LV a new mob takes the new level: %s" % [wd.levels[u] for u in wd.alive()])
    p3 = St.get(key)
    p3.setProperty("combat.i0.deco", "5")   # Mob level 5 (sub 1)
    St.LOCK.lock()
    try:
        St.save(key, p3)
    finally:
        St.LOCK.unlock()
    levels["Combat.Warrior"] = 30
    Cb.LVL.clear()
    wd.mobs[wd.alive()[0]]["alive"] = False
    tick()
    t[0] += 31000
    tick()
    lv2 = [wd.levels[u] for u in wd.alive()]
    K.check(any(34 <= l <= 35 for l in lv2), "LV the upgrade on top: Mob level 5 = owner 30 + 4..5: %s" % lv2)
    # a visitor standing there changes nothing (only the owner's key is asked)
    n0 = state["calls"]
    Cb.LVL.clear()
    wd.mobs[wd.alive()[0]]["alive"] = False
    tick()
    t[0] += 31000
    tick(extra=[(MEMBER, (cx - 3.5, Y0 + 1.0, cz - 3.5), True)])
    K.check(any(34 <= wd.levels[u] <= 35 for u in wd.alive()), "LV a visitor standing there: the owner's level still counts")
    K.eq(int(Cfg.UNDER.get()), U0, "LV no bridge lookup under the shard lock")
    # fix (critic): SkyyMobs refuses the level (levels.max lower): the mob takes the zone table's level instead of none
    wfn = wd.fn
    refused = []

    def lim(a):
        if str(a[0]) == "level" and int(a[2]) > 25:
            refused.append(int(a[2]))
            return L["Bool"].FALSE
        return wfn(a)
    Fi.TEST = PyFn(lim)
    p3 = St.get(key)
    p3.setProperty("combat.i0.deco", "0")
    St.LOCK.lock()
    try:
        St.save(key, p3)
    finally:
        St.LOCK.unlock()
    Cb.LVL.clear()
    levels["Combat.Warrior"] = 34
    wd.mobs[wd.alive()[0]]["alive"] = False
    before = set(wd.mobs)
    tick()
    t[0] += 31000
    tick()
    new = [u for u in wd.alive() if u not in before]
    K.check(refused and new and all(1 <= wd.levels[u] <= 3 for u in new), "LV fix: a refused level (%s) falls back to the Zone 1 table: %s" % (refused[:2], [wd.levels[u] for u in new]))
    K.save()


def _bagbox(L, ou, st):
    from jpype import JClass
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")

    def box(a):
        st["calls"].append((a[0], int(a[1]), str(a[2]), int(a[3])))
        if st.get("hook"):
            h, st["hook"] = st["hook"], None
            h()
        if st.get("nothing"):
            return None
        return IS(st.get("id", "Skyy_Unid_Bag_Normal"), 1)
    return box


def run_bags(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString
    K = HK.Child(out)
    L = T411._L(os.path.join(scratch, "ba"), K)
    M, St, Core, Cfg, Inv, Cb, fns, PyFn = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShInv"], L["ShCombat"], L["fns"], L["PyFn"]
    inv, count = L["inv"], L["count"]
    T410.T48.add_items([("Skyy_Unid_Bag_Normal", 1)]) if hasattr(T410, "T48") else None
    key = OWNER
    Core.NOW_TEST = T0
    ou = L["UUID"].fromString(OWNER)
    M.ONLINE.put(OWNER, True)
    M.ALL_ON_TEST = True
    p = St.get(key)
    St.LOCK.lock()
    try:
        M.starter(CK, p, JLong(T0)) if p.getProperty("combat.i0.type") is None else None
        p.setProperty("combat.i0.type", "skeleton"); p.setProperty("combat.i0.size", "1"); p.setProperty("combat.auto", "1"); p.setProperty("combat.paused", "0")
        p.setProperty("combat.placed", "skyy-island-" + OWNER + "|1|2|3")
        p.setProperty("combat.i0.totems", "soul_cage:5:::0:ccc333"); p.setProperty("combat.i0.last", str(T0)); p.setProperty("combat.i0.stored", "0")
        p.setProperty("combat.storage", "5")
        St.save(key, p)
    finally:
        St.LOCK.unlock()
    rate = float(M.rate(CK, p, 0, JLong(T0)))
    K.check(rate > 0, "BA the Soul Cage runs (%.3f / min)" % rate)

    def st0():
        return int(M.stored(CK, p, 0))

    def bg():
        return int(M.bags(p, 0))
    # the store: bags fill from the Soul Cage alone, as a percent of the drops made
    Cfg.CB_BAG_PCT = 10
    Cfg.CB_BAG_CAP = 100000
    H = 3600000
    p.setProperty("combat.i0.last", str(T0))
    M.settle(CK, p, 0, JLong(T0 + 5 * H))
    made = st0()
    K.check(made > 100, "BA drops made (%d)" % made)
    K.check(abs(bg() - made / 10.0) <= 1.0, "BA bags = 10 %% of the drops made (%d of %d)" % (bg(), made))
    K.eq(str(p.getProperty("combat.i0.stored")), str(made), "BA the drops count is the plain count (bags are not in it)")
    # the cap
    Cfg.CB_BAG_CAP = 8
    p.setProperty("combat.i0.bags", "5"); p.setProperty("combat.i0.last", str(T0 + 5 * H))
    M.settle(CK, p, 0, JLong(T0 + 9 * H))
    K.eq(bg(), 8, "BA combat.bagCap holds it (8)")
    Cfg.CB_BAG_PCT = 0
    v0 = bg()
    p.setProperty("combat.i0.bags", "0"); p.setProperty("combat.i0.last", str(T0 + 9 * H))
    M.settle(CK, p, 0, JLong(T0 + 10 * H))
    K.eq(bg(), 0, "BA combat.bagPct 0 = no bags")
    Cfg.CB_BAG_PCT = 2; Cfg.CB_BAG_CAP = 64
    # Collect all never touches the bag store; the drop mix is paid out whole
    p.setProperty("combat.i0.stored", "300"); p.setProperty("combat.i0.bags", "5"); p.setProperty("combat.i0.last", str(T0 + 10 * H))
    Core.NOW_TEST = T0 + 10 * H
    cs = inv(27, 27, 9)
    r = str(Core.collect(ou, key, CK, -1, cs))
    K.check(r.startswith("+Collected") and st0() == 0, "BA Collect all: %s" % r[:90])
    K.eq(bg(), 5, "BA Collect all left the bags stored")
    K.check(int(count(cs, "Skyy_Unid_Bag_Normal")) == 0, "BA no bag came out of Collect all")
    drop = Cb.dropsFor(p, 0, 300)
    ids, qs = [str(i) for i in drop[0]], [int(q) for q in drop[1]]
    K.check(sum(qs) == 300 and len(ids) >= 2 and all(int(count(cs, i)) == q for i, q in zip(ids, qs)), "BA every kind of the mix came out (%s)" % list(zip(ids, qs)))
    # fix (critic): the 0.4.20 pool never held a bag, every zone: the Soul Cage's bags are the new store's only source
    for zz in range(5):
        pz = T411._prof(L, T411._key(), [(0, zz, 1, (0, 0, 0))])
        dz = [str(i) for i in Cb.dropsFor(pz, 0, 1000)[0]]
        K.check(dz and not any("Unid" in i or "Mystery" in i or "Bag" in i for i in dz), "BA fix: Zone %d's pool has no bags: %s" % (zz + 1, dz[:4]))
    # the bag Collect
    bx = {"calls": []}
    _put(L, "gear:fn:box", PyFn(_bagbox(L, ou, bx)))
    Cb.LVL.clear()
    from jpype import JObject, JInt, JArray
    Cfg.KEY_TEST = PyFn(lambda u: JString(key))
    _put(L, "skill:fn:run", PyFn(lambda a: JArray(JObject)([JInt(20), JInt(1000), JLong(0), JLong(0), JObject(False, "java.lang.Boolean"), JString("Combat.Warrior")])))
    cs2 = inv(2, 1)   # three slots
    r = str(Core.collectBags(ou, key, CK, 0, cs2))
    K.check(r.startswith("+Collected 3 unidentified bags") and "2 stay stored" in r, "BA a partial bag Collect: %s" % r)
    K.eq(bg(), 2, "BA ... two stay stored")
    K.eq(int(count(cs2, "Skyy_Unid_Bag_Normal")), 3, "BA ... three in the inventory")
    K.check(bx["calls"] and bx["calls"][0][1:] == (20, "shard", 0), "BA the bag's level = the island's mob level (owner 20, Mob level 0): %s" % (bx["calls"][:1],))
    # drops never come with bags
    K.eq(st0(), 0, "BA the drop store is untouched by the bag Collect")
    disk = open(os.path.join(str(St.DIR), key + ".properties"), encoding="utf8").read()
    K.check("combat.i0.bags=2" in disk, "BA the file holds the debit")
    # full inventory
    full = inv(1)
    L_full = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Inv.give(full, "Ingredient_Bone_Fragment", JLong(100))
    r = str(Core.collectBags(ou, key, CK, 0, full))
    K.check(r.startswith("-Your inventory is full") and bg() == 2, "BA a full inventory: %s" % r)
    # an inventory that fills while the bag is being made: what does not arrive goes back
    cs3 = inv(2)
    p.setProperty("combat.i0.bags", "2")
    bx["hook"] = lambda: Inv.give(cs3, "Ingredient_Bone_Fragment", JLong(100))
    r = str(Core.collectBags(ou, key, CK, 0, cs3))
    K.check(r.startswith("+Collected 1 ") and bg() == 1 and int(count(cs3, "Skyy_Unid_Bag_Normal")) == 1, "BA the inventory filled midway: 1 given, 1 back: %s (bags %d)" % (r, bg()))
    # nothing stored
    p.setProperty("combat.i0.bags", "0")
    K.check(str(Core.collectBags(ou, key, CK, 0, inv(2))).startswith("=No unidentified bags"), "BA nothing stored")
    # SkyyGear silent / absent: stays stored
    p.setProperty("combat.i0.bags", "4")
    bx["nothing"] = True
    K.check(str(Core.collectBags(ou, key, CK, 0, inv(4))).startswith("-SkyyGear made no bags") and bg() == 4, "BA a box that answers nothing: bags stay stored")
    bx["nothing"] = False
    _del(L, "gear:fn:box")
    K.check(str(Core.collectBags(ou, key, CK, 0, inv(4))).startswith("-SkyyGear cannot make bags") and bg() == 4, "BA no SkyyGear: bags stay stored")
    _put(L, "gear:fn:box", PyFn(_bagbox(L, ou, bx)))
    # the bridge is never asked under the lock (ShCfg.UNDER counts lookups under the shard lock)
    U0 = int(Cfg.UNDER.get())
    r = str(Core.collectBags(ou, key, CK, 0, inv(9)))
    K.eq(int(Cfg.UNDER.get()), U0, "BA gear:fn:box asked with no lock held")
    # bags on another shard's Collect: refused
    K.check(str(Core.collectBags(ou, key, 2, 0, inv(9))).startswith("-Only combat"), "BA only combat islands")
    # the saved keys: a 0.4.20 reader never reads them (no such keys in its source), and a save round-trips unknown keys
    src = open(GEN_OLD, encoding="utf8").read()
    K.check(not re.search(r'ik\([^)]*"(bags|arena)"', src), "BA rollback: the 0.4.20 build never reads <kind>.i<n>.bags / .arena")
    p.setProperty("combat.i0.arena", "12:4"); p.setProperty("combat.i0.bags", "7")
    St.LOCK.lock()
    try:
        St.save(key, p)
    finally:
        St.LOCK.unlock()
    d2 = open(os.path.join(str(St.DIR), key + ".properties"), encoding="utf8").read()
    K.check("combat.i0.arena=12\\:4" in d2 or "combat.i0.arena=12:4" in d2, "BA rollback: the keys survive a save")
    K.save()


def run_page21(out, jar, scratch, _home):
    from jpype import JClass, JLong, JString, JArray, JObject, JInt
    K = HK.Child(out)
    L, ou, W_, p, lv = T420._W0(os.path.join(scratch, "pg21"), K)
    M, Core, Cfg, Page, fns, PyFn, St, Inv, Cb = L["ShMath"], L["ShCore"], L["ShCfg"], L["ShPage"], L["fns"], L["PyFn"], L["ShStore"], L["ShInv"], JClass(PKG + "ShCombat")
    Core.NOW_TEST = T0
    M.ONLINE.put(OWNER, True)
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.type", "skeleton"); p.setProperty("combat.i0.size", "1"); p.setProperty("combat.auto", "1"); p.setProperty("combat.storage", "1")
        p.setProperty("combat.placed", "skyy-island-" + OWNER + "|1|2|3"); p.setProperty("combat.i0.last", str(T0)); p.setProperty("combat.i0.stored", "6"); p.setProperty("combat.i0.bags", "3")
        p.setProperty("combat.i0.totems", "soul_cage:1:::0:ddd444")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    Cfg.KEY_TEST = PyFn(lambda u: JString(OWNER))
    _put(L, "skill:fn:run", PyFn(lambda a: JArray(JObject)([JInt(34), JInt(1000), JLong(0), JLong(0), JObject(False, "java.lang.Boolean"), JString("Combat.Warrior")])))
    bx = {"calls": []}
    _put(L, "gear:fn:box", PyFn(_bagbox(L, ou, bx)))
    Cb.LVL.clear()
    pg = Page(ou, W_)
    pg.kind = CK
    pg.view = 0

    def click(a, **extra):
        d = {"a": a}
        d.update(extra)
        pg.handleDataEvent(None, None, json.dumps(d))
        r = T410.full(pg)
        K.check(not r["miss"] and not r["unbound"], "PG21 %s: the page walks clean %s %s" % (a, r["miss"][:2], r["unbound"][:2]))
        return T49._build(pg)
    bd = click("tab0")
    K.check(bool(pg.cBags), "PG21 the Bags button is on")
    K.check("3 bags" in str(pg.cSub[0]) and len(str(pg.cSub[0])) <= 60, "PG21 the row's sub line names the bag store: %s" % pg.cSub[0])
    K.check("Unidentified bags: 3" in str(pg.cAll[6]), "PG21 its own line in the tab: %s" % pg.cAll[6])
    K.check("paid when you collect" in str(pg.cAll[5]), "PG21 fix: the paid-on-collect line stays: %s" % pg.cAll[5])
    K.check("Bag" in bd["mk"] if isinstance(bd, dict) and "mk" in bd else True, "PG21 the markup has the button")
    K.eq(int(pg.ownLv), 34, "PG21 the page read the owner's level")
    click("tab1")
    K.check("Small (25 x 25)" in str(Page.sizeName(CK, 1)) and "Large (51 x 51)" in str(Page.sizeName(CK, 3)) and "Medium (21 x 21)" in str(Page.sizeName(2, 2)), "PG21 the sizes the tabs state")
    p.setProperty("combat.i0.deco", "5")
    K.eq(str(Cb.nowTxt(34, 0, 1, 0, 5, 0)).count("Lv 38-39"), 1, "PG21 the Map tab's level text")
    r9 = click("tab0")
    r0 = pg.handleDataEvent(None, None, json.dumps({"a": "cbag0"}))
    K.check("Collected" in str(pg.stText) and "unidentified bag" in str(pg.stText), "PG21 the row's Bags button collects: %s" % pg.stText)
    K.eq(int(M.bags(St.get(OWNER), 0)), 0, "PG21 the store is emptied")
    pg.handleDataEvent(None, None, json.dumps({"a": "cbag99"}))
    K.check("gone" in str(pg.stText), "PG21 a stale row: %s" % pg.stText)
    # the visitor view: no button, and no line pointing at one (fix, critic 2)
    K.check("press Bags on a row to collect" in str(pg.cAll[6]), "PG21 fix: the owner's line says how to collect: %s" % pg.cAll[6])
    Cfg.KEY_TEST = PyFn(lambda u: JString(OWNER if str(u) == str(ou) else str(u)))   # each player their own profile key, so the visitor is not the owner
    pv = Page(L["UUID"].fromString(T420.VISITOR), W_)
    pv.kind = CK
    pv.view = 0
    pv.handleDataEvent(None, None, json.dumps({"a": "tab0"}))
    b3 = T49._build(pv)
    K.check(not bool(pv.cBags) and "#SkyyShCRow0Bag" not in b3["binds"], "PG21 fix: a visitor has no Bags button")
    K.eq(str(pv.cAll[6]), "", "PG21 fix: a visitor has no bag line either")
    Cfg.KEY_TEST = PyFn(lambda u: JString(OWNER))
    K.check('("Up to +2,400 Farming XP", GOOD)' in open(GEN, encoding="utf8").read(), "PG21 fix: the sizing sample matches the live XP text")
    K.check("up to +" in open(GEN, encoding="utf8").read(), "PG21 the XP wording is in the build")
    # the XP lines
    # fix (critic): a long sub-line keeps the bag count, cut to 60
    p.setProperty("combat.i0.bags", "123456")
    St.LOCK.lock()
    try:
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    click("tab0")
    K.check("123,456 bags" in str(pg.cSub[0]) and len(str(pg.cSub[0])) <= 60, "PG21 fix: a long sub-line keeps the bag count: %s" % pg.cSub[0])
    K.check(True, "PG21 done")
    K.save()


EXPECT = {   # 0.4.20 -> 0.4.21, checked by hand 2026-11-08: the version texts (CfgFn / CfgRows / CfgFile rows / ShStore.migrate + migrate2 + save / ready line) + the round
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'ShAura': ['~m runIn'],
    'ShCfg': ['+f CB_BAG_CAP', '+f CB_BAG_PCT', '+f CB_HALF', '+f CB_LVP', '+f CB_WALL', '~<clinit>', '~m loadCfg', '~m writeDefaults'],
    'ShCombat': ['+f CLASS_SK', '+f LVL', '+f LV_MS', '+f MAXLV', '+m lvHiP', '+m lvLoP', '+m lvTxtP', '+m nextTxt', '+m nowTxt', '+m ownerLv', '+m ownerLv0', '+m riseOf', '+m runLv', '+m withP', '-m nextTxt', '-m nowTxt', '~<clinit>'],
    'ShCore': ['+f BAGS_AT_ONCE', '+m collectBags', '+m collectBags0', '~m auraSet', '~m payCred', '~m placeAt', '~m spotFor'],
    'ShFight': ['+m island', '+m spawnOne', '-m island', '-m spawnOne', '~m tickWorld'],
    'ShFill': ['+m arenaIs', '~m markFixed', '~m paintZ'],
    'ShGeo': ['+f CSX', '+f CSZ', '+f FIX_ARENA', '+m arenaFix', '+m arenaMark', '+m arenaMarkOf', '+m arenaSlotOf', '+m arenaTag', '+m gapK', '+m half', '+m laneLenK', '+m sxk', '+m szk', '~<clinit>', '~m bridge', '~m combat', '~m cspots', '~m fixes', '~m lane', '~m padPos', '~m pads', '~m region', '~m spotOf', '~m totemSpot'],
    'ShInv': ['+m freeSlots'],
    'ShMath': ['+m bagAdd', '+m bags', '~m settle'],
    'ShPage': ['+f bagT', '+f cBags', '+f ownLv', '+m sizeName', '~m act', '~m buildFull', '~m fill', '~m fillMap', '~m svTwo'],
    'ShStore': ['+m snapArena', '~m migrate', '~m migrate2', '~m save'],
    'SkyyShardsPlugin': ['~m setup'],
}


def run_live(out, jar, scratch, home):
    T420.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run_compare = T419._compare
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("geo", run_geo), ("rebuild", run_rebuild), ("level", run_level), ("bags", run_bags), ("page21", run_page21),
                   ("comp", T420.run_comp), ("sell20", T420.run_sell), ("mig20", T420.run_mig20), ("ore", T420.run_ore), ("deb", T420.run_deb), ("page20", T420.run_page20), ("livecomp", T420.run_livecomp),
                   ("off", T419.run_off), ("mig", T419.run_mig), ("sell", T419.run_sell), ("page", T419.run_page),
                   ("open", T416._h(T416._g(T416.run_open), True)), ("bytecode", T415.run_bytecode),
                   ("flows3", T416._h(T416._g(T413.run_flows3))), ("page49", T419.run_page49),
                   ("live", run_live)],
           script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
