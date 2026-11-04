"""Harness for SkyyShards 0.4.18 (the natural Mining cave + its mouth on the bridge - tools/shards_0_4_18_patch.py, on top of 0.4.17).
Build first:
    python tools/shards_0_4_18_patch.py && python SkyyShards/build_skyyshards_0.4.18.py
    python SkyyShards/test_skyyshards_0.4.18.py [--keep] [--ascii]

  S18  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand / lock region;
                line endings kept
  CB   bridge   every bridge of every kind / slot = 0.4.17's maths (a Python copy of the old bridge(): the same plank cells, in order)
  CV   cave     every Mining slot x size (all 11 islands owned, so every outgoing bridge exists) painted onto a block map: the ore count =
                oreN (every Ore Amount at Small / Medium / Large, never under 16 / 72 / 160 at the rebuild amounts 2 / 1 / 0); every
                bridge's inner end cell (incoming + every island bridged onto it) has 1-3 free above a floor at y 100 and a WALK (BFS, 2 high,
                floor at the bridge's height) reaches the totem pads from it; not a box (wall line, ceiling heights, outer top all vary, the
                corners open ledge), stalactites / pillars / floor pieces present, only vanilla ids; ASCII top-down + side per size (--ascii)
  RB   rebuild  a 0.4.17 box cave (walls, ceiling, opening, ore) + a player's chest inside / in an old wall / on the roof + a hand-placed
                totem: one paint + markFixed -> the box cleared where the new cave has no rock (only our ids), the player's blocks + the
                totem kept, marker .cave=2, the History copy byte-identical to the file before, one collect.log line with the Undo; the
                second region has no FIX_CAVE cell and a second + third paint change NOTHING; a 0.4.7 flat island (no marker) goes 1 -> 2
                in one pass; a refused History copy = no marker + a warning, the next pass marks it
  GX   grow + profile paths: Small -> Medium -> Large in place (no Small / Medium rock or floor piece left in the bigger cave), Decorations
                5 (niches / dropped deco), Irrigation 5 (pools only on the cave floor), a hand-placed totem's cells kept clear, 0.4.8's
                8-argument cave() = the profile-less cave, ROCK over our own ore / not over a player's block
  LV   live     on a scratch COPY of the live Skyy_SkyyShards data: every Mining island painted over its 0.4.17 box, marked .cave=2 once,
                the second pass changes nothing; then 0.4.17's live start twice
  then 0.4.17's open (Pocket costs) + LB bytecode + 0.4.13 flows3 + 0.4.9 page; A verify (-Xverify:all), C compare (0.4.17 -> 0.4.18 =
  EXPECT; every non-class file identical), AA audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.18"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "cave", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.17.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.17.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_18_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
ASCII = "--ascii" in sys.argv
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_17", os.path.join(HERE, "test_skyyshards_0.4.17.py"))
T417 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T417)
sys.argv[:] = _argv
T416, T415, T413, T411, T49 = T417.T416, T417.T415, T417.T413, T417.T411, T417.T49
T48 = T49.T48
T417.JAR = JAR
T416.SCRATCH = T415.SCRATCH = T417.SCRATCH = SCRATCH
OWNER = T416.OWNER
MK = 0                    # the Mining kind
Y = 100
HALF = [6, 10, 14]
MINN = [16, 72, 160]      # the old flat island's node counts (0.4.8: never fewer)
REB_AMT = [2, 1, 0]       # 0.4.8's rebuild Ore Amount per size


# ---------------------------------------------------------------------------------------------------------- S18: static
def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.18 - build script') and g.count('VERSION = "0.4.18"\n') == 1, "S18 header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "LOCK.lock()"):
        K.check(g.count(w) == o.count(w), "S18 no new %r (%d)" % (w, g.count(w)))
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.18: natural Mining caves, the mouth meets the bridge; 0.4.17: rarity colours" in g, "S18 the ready line names the round")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S18 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S18 line endings kept")
    K.save()


# ---------------------------------------------------------------------------------------------------------- helpers
def _setup(scratch, K):
    L = T48._setup(scratch, K)
    from jpype import JClass
    for n in ("ShGeo", "ShFill", "ShIsl", "ShMath", "ShStore", "ShTotem", "ShCfg"):
        L[n] = JClass(PKG + n)
    return L


def _jround(v):
    return math.floor(v + 0.5)


def old_bridge(Geo, kd, slot):
    """0.4.17's bridge() in Python (the plank cells in order)"""
    SX, SZ, SRC = list(Geo.SX), list(Geo.SZ), list(Geo.SRC)
    src = SRC[slot]
    ax0 = 0.0 if src < 0 else float(SX[src])
    az0 = 0.0 if src < 0 else float(SZ[src])
    ln = math.sqrt((float(SX[slot]) - ax0) * (float(SX[slot]) - ax0) + (float(SZ[slot]) - az0) * (float(SZ[slot]) - az0))
    dx = (float(SX[slot]) - ax0) / ln
    dz = (float(SZ[slot]) - az0) / ln
    ox = 1024 * kd
    seen, out = set(), []
    end = ln - 6.0
    s0 = (int(Geo.HUB) - 1) * 2 if src < 0 else 12
    for s in range(s0, int(math.floor(end * 2.0)) + 1):
        t = s / 2.0
        for w in (-1, 0, 1):
            x = int(_jround(float(ox) + ax0 + dx * t - dz * float(w)))
            z = int(_jround(float(int(Geo.OZ)) + az0 + dz * t + dx * float(w)))
            if (x, z) in seen:
                continue
            seen.add((x, z))
            out.append((x, Y, z))
    return out


def _bridge(L, kd, slot):
    from jpype import JClass
    o = JClass("java.util.ArrayList")()
    L["ShGeo"].bridge(o, kd, slot)
    return [(int(b[0]), int(b[1]), int(b[2])) for b in o]


def _mprof(L, slots, size, amt=None, cave="2", deco=0, irr=0):
    """the Mining shard of OWNER with islands on `slots` (ladder order), all at `size`"""
    St, Isl = L["ShStore"], L["ShIsl"]
    p = St.get(OWNER)
    St.LOCK.lock()
    try:
        for k in list(p.stringPropertyNames()):
            if str(k).startswith("mining.i"):
                p.remove(k)
        p.setProperty("mining.auto", "1")
        for s in slots:
            p.setProperty("mining.i%d.type" % s, str(Isl.KEY[int(Isl.LAD0[MK]) + s]))
            p.setProperty("mining.i%d.size" % s, str(size))
            p.setProperty("mining.i%d.amt" % s, str(REB_AMT[size - 1] if amt is None else amt))
            p.setProperty("mining.i%d.deco" % s, str(deco))
            p.setProperty("mining.i%d.irr" % s, str(irr))
            p.setProperty("mining.i%d.totems" % s, "quarry_spirit:1")
            p.setProperty("mining.i%d.centre" % s, "1")
            if cave:
                p.setProperty("mining.i%d.cave" % s, cave)
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    return p


def _ids(L, slot, p=None):
    Isl, Geo = L["ShIsl"], L["ShGeo"]
    t = int(Isl.ty(MK, p, slot)) if p is not None else int(Isl.LAD0[MK]) + slot
    return str(Geo.IDS[int(Isl.HOST[t])]), str(Geo.IDS[int(Isl.RES1[t])]), t


def _ctr(L, slot):
    Geo = L["ShGeo"]
    return int(Geo.ox(MK)) + int(Geo.SX[slot]), int(Geo.OZ) + int(Geo.SZ[slot])


def _paint(L, p, m=None, fx=None):
    from jpype import JClass
    Geo, Fill = L["ShGeo"], L["ShFill"]
    if m is None:
        m = JClass("java.util.HashMap")()
    Fill.TEST_BLOCKS = m
    want = Geo.region(p, MK)
    n = int(Fill.paintY(None, want, fx, None))
    return m, want, n


def _bid(m, x, y, z):
    v = m.get("%d,%d,%d" % (x, y, z))
    return "" if v is None else str(v)


def _walk(m, starts, goal, box, foot_ok):
    """BFS on feet cells (x, z) at y Y+1: floor solid at Y, Y+1 and Y+2 empty (water floor no); box = allowed (x, z) test"""
    seen = set()
    q = [s for s in starts if foot_ok(s)]
    for s in q:
        seen.add(s)
    i = 0
    while i < len(q):
        c = q[i]
        i += 1
        if goal(c):
            return True
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dz)
            if n in seen or not box(n) or not foot_ok(n):
                continue
            seen.add(n)
            q.append(n)
    return False


def _foot(m, totems):
    """a feet cell: a solid floor at y 100 (not water), y 101 free (or a half-block bump / a totem pad), y 102 free"""
    def ok(c):
        x, z = c
        f = _bid(m, x, Y, z)
        if not f and m.get("f:%d,%d,%d" % (x, Y, z)) is None:   # an irrigation pool (1 deep, as since 0.4.8) is walked through
            return False
        a, b = _bid(m, x, Y + 1, z), _bid(m, x, Y + 2, z)
        return (a == "" or a.endswith("_Half") or a in totems) and b == ""
    return ok


def ascii_island(L, m, slot, size, bridge_cells):
    cx, cz = _ctr(L, slot)
    h = HALF[size - 1]
    host, ore, _t = _ids(L, slot)
    bset = set((x, z) for x, _y, z in bridge_cells)
    lines = ["slot %d (%s) size %d - TOP-DOWN at y+2 (# rock, o ore, . cave air, : open rock ledge, = plank walkway, ~ bridge outside, ^ stalagmite, , rubble, _ half bump, T totem, blank open)" % (slot + 1, host, size)]
    for dz in range(-h - 3, h + 4):
        row = ""
        for dx in range(-h - 3, h + 4):
            x, z = cx + dx, cz + dz
            inside = abs(dx) <= h and abs(dz) <= h
            b2, b1, f = _bid(m, x, Y + 2, z), _bid(m, x, Y + 1, z), _bid(m, x, Y, z)
            if b2 == host:
                ch = "#"
            elif b2 == ore:
                ch = "o"
            elif "Totem" in b1:
                ch = "T"
            elif "Stalactite" in b1:
                ch = "^"
            elif b1.startswith("Rubble"):
                ch = ","
            elif b1.endswith("_Half"):
                ch = "_"
            elif b1 == host or b1 == ore:
                ch = "#"
            elif f.startswith("Wood") or f.endswith("Planks") or "Plank" in f:
                ch = "=" if inside else "~"
            elif inside and f:
                roofed = any(_bid(m, x, yy, z) for yy in range(Y + 3, Y + 17))
                ch = "." if roofed else ":"
            elif (x, z) in bset:
                ch = "~"
            else:
                ch = " "
            row += ch
        lines.append("   " + row)
    lines.append("slot %d size %d - SIDE slice through the centre (x across, y up; # rock, o ore, . air inside the outline)" % (slot + 1, size))
    for y in range(Y + 16, Y - 1, -1):
        row = ""
        for dx in range(-h - 1, h + 2):
            b = _bid(m, cx + dx, y, cz)
            row += "#" if b == host else ("o" if b == ore else ("=" if "Plank" in b else ("^" if "Stalactite" in b else (" " if b == "" else "+"))))
        if row.strip() or y <= Y + 2:
            lines.append("%4d %s" % (y, row))
    return "\n".join(lines)


# ---------------------------------------------------------------------------------------------------------- CB: the bridges are 0.4.17's
def run_bridge(out, jar, scratch, _home):
    K = HK.Child(out)
    L = _setup(os.path.join(scratch, "cb"), K)
    Geo = L["ShGeo"]
    bad = []
    n = 0
    for kd in range(6):
        for s in range(int(len(Geo.SX))):
            a, b = _bridge(L, kd, s), old_bridge(Geo, kd, s)
            n += len(a)
            if a != b:
                bad.append((kd, s, len(a), len(b)))
    K.check(not bad and n > 2000, "CB every bridge of 6 kinds x 16 slots = 0.4.17's plank cells, in order (%d cells): %s" % (n, bad[:4]))
    K.save()


# ---------------------------------------------------------------------------------------------------------- CV: every Mining slot x size
def run_cave(out, jar, scratch, _home):
    K = HK.Child(out)
    from jpype import JClass
    L = _setup(os.path.join(scratch, "cv"), K)
    Geo, Isl, Fill = L["ShGeo"], L["ShIsl"], L["ShFill"]
    nis = int(Isl.LADN[MK])
    K.eq(nis, 11, "CV the Mining ladder has 11 islands (slots 1-11)")
    slots = list(range(nis))
    SRC = list(Geo.SRC)
    van = set()
    rep = []
    for size in (1, 2, 3):
        for amt in sorted(set([REB_AMT[size - 1], 5])):
            p = _mprof(L, slots, size, amt)
            m, want, _n = _paint(L, p)
            kinds = set(int(b[3]) for b in want)
            K.check(int(Geo.FIX_CAVE) not in kinds and int(Geo.FIX_ORE) not in kinds, "CV size %d: marked islands list no one-time cell" % size)
            for s in slots:
                cx, cz = _ctr(L, s)
                h = HALF[size - 1]
                host, ore, t = _ids(L, s, p)
                box = lambda c, cx=cx, cz=cz, h=h: abs(c[0] - cx) <= h + 12 and abs(c[1] - cz) <= h + 12
                cells = [(cx + dx, y, cz + dz) for dx in range(-h, h + 1) for dz in range(-h, h + 1) for y in range(Y + 1, Y + 17)]
                ores = [c for c in cells if _bid(m, *c) == ore]
                want_n = int(Isl.oreN(size, amt))
                K.check(len(ores) == want_n and (amt != REB_AMT[size - 1] or want_n >= MINN[size - 1]),
                        "CV slot %d size %d Amount %d: %d ore nodes = oreN %d%s" % (s + 1, size, amt, len(ores), want_n, (" >= the old %d" % MINN[size - 1]) if amt == REB_AMT[size - 1] else ""))
                if amt != REB_AMT[size - 1]:
                    continue
                for c in cells:
                    v = _bid(m, *c)
                    if v:
                        van.add(v)
                tot = set(str(x) for x in L["ShTotem"].BLOCKS)
                foot = _foot(m, tot)
                goal = lambda c, cx=cx, cz=cz: abs(c[0] - cx) <= 2 and abs(c[1] - cz) <= 2
                # the bridge this island hangs on: its inner end cell (the last plank before the centre)
                b_in = _bridge(L, MK, s)
                endc = max(b_in, key=lambda c: -((c[0] - cx) ** 2 + (c[2] - cz) ** 2)) if b_in else None
                ok_end = endc is not None and _bid(m, endc[0], Y + 1, endc[2]) == "" and _bid(m, endc[0], Y + 2, endc[2]) == "" and _bid(m, endc[0], Y + 3, endc[2]) == "" and (_bid(m, endc[0], Y, endc[2]) != "" or m.get("f:%d,%d,%d" % (endc[0], Y, endc[2])) is not None)
                outer = [ (c[0], c[2]) for c in b_in if max(abs(c[0] - cx), abs(c[2] - cz)) > h ]
                K.check(ok_end and _walk(m, [(endc[0], endc[2])] + outer[-3:], goal, box, foot),
                        "CV slot %d size %d: the bridge's end cell %s meets the mouth (free 3 high over the y 100 floor) and a walk reaches the pads" % (s + 1, size, endc and (endc[0] - cx, endc[2] - cz)))
                for j in slots:
                    if SRC[j] != s:
                        continue
                    bj = _bridge(L, MK, j)
                    st = min(bj, key=lambda c: (c[0] - cx) ** 2 + (c[2] - cz) ** 2)
                    K.check(_bid(m, st[0], Y + 1, st[2]) == "" and _bid(m, st[0], Y + 2, st[2]) == "" and _walk(m, [(st[0], st[2])], goal, box, foot),
                            "CV slot %d size %d: the bridge to slot %d leaves through a mouth (its first plank %s free, a walk reaches the pads)" % (s + 1, size, j + 1, (st[0] - cx, st[2] - cz)))
                # not a box
                ceil, wall, top = set(), set(), set()
                for dx in range(-h, h + 1):
                    for dz in range(-h, h + 1):
                        col = [_bid(m, cx + dx, y, cz + dz) for y in range(Y + 1, Y + 17)]
                        rock = [i for i, v in enumerate(col) if v in (host, ore)]
                        if rock:
                            top.add(max(rock))
                        if col[0] == "" and col[1] == "" and rock:
                            ceil.add(min(rock))
                for dz in range(-h + 1, h):
                    for dx in range(-h, 1):
                        if _bid(m, cx + dx, Y + 2, cz + dz) == "":
                            wall.add(dx)
                            break
                corners = [_bid(m, cx + a * h, Y + 4, cz + b * h) for a in (-1, 1) for b in (-1, 1)]
                floor = [_bid(m, cx + dx, Y + 1, cz + dz) for dx in range(-h, h + 1) for dz in range(-h, h + 1)]
                nst = sum(1 for v in floor if "Stalactite" in v)
                nrb = sum(1 for v in floor if v.startswith("Rubble_"))
                nhb = sum(1 for v in floor if v.endswith("_Half"))
                hang = sum(1 for dx in range(-h, h + 1) for dz in range(-h, h + 1) for y in range(Y + 4, Y + 12)
                           if _bid(m, cx + dx, y, cz + dz) in (host, ore) and _bid(m, cx + dx, y - 1, cz + dz) == "" and _bid(m, cx + dx, y + 1, cz + dz) in (host, ore)
                           and _bid(m, cx + dx + 1, y, cz + dz) == "" and _bid(m, cx + dx - 1, y, cz + dz) == "")
                K.check(len(ceil) >= 3 and len(wall) >= 2 and len(top) >= 4 and corners.count("") >= 3 and nst >= 2 and nrb >= 2 and nhb >= 1 and hang >= 1,
                        "CV slot %d size %d natural: ceiling heights %s, wall line %s, outer tops %d, open corners %d, stalagmites %d, rubble %d, bumps %d, hanging rock %d"
                        % (s + 1, size, sorted(ceil), sorted(wall), len(top), corners.count(""), nst, nrb, nhb, hang))
                if size >= 2:
                    pil = sum(1 for dx in range(-h + 3, h - 2) for dz in range(-h + 3, h - 2)
                              if all(_bid(m, cx + dx, y, cz + dz) in (host, ore) for y in range(Y + 1, Y + 5))
                              and sum(1 for a, b in ((2, 0), (-2, 0), (0, 2), (0, -2)) if _bid(m, cx + dx + a, Y + 2, cz + dz + b) == "") >= 3)
                    K.check(pil >= 1, "CV slot %d size %d: a rock pillar stands in the cave (%d columns)" % (s + 1, size, pil))
                if s in (0, 1) or (ASCII and s in (6, 7)):
                    rep.append(ascii_island(L, m, s, size, b_in))
    # vanilla ids only
    Fill.TEST_BLOCKS = None
    import zipfile as _zf
    with _zf.ZipFile(B.ASSETS_ZIP if hasattr(B, "ASSETS_ZIP") else os.path.join(os.environ.get("APPDATA", ""), "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")) as z:
        have = set(n.rsplit("/", 1)[1][:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    ours = set(v for v in van if v.startswith("Skyy_") or v.endswith("_SkyWynn"))   # our totem + the SkyWynn zone metals' ores (island types since 0.4.8)
    typ = set(str(Geo.IDS[int(Isl.RES1[t])]) for t in range(int(Isl.TN)) if int(Isl.TK[t]) == MK)   # the island types' ores (0.4.8, unchanged)
    new = set(str(Geo.IDS[int(a[t])]) for a in (Isl.STAL, Isl.RUBB, Isl.HALFB, Isl.COBB) for t in range(int(Isl.TN)) if int(a[t]) >= 0)
    K.check(len(new) == 24 and new <= have and not (van - have - ours - typ) and all("Totem" in v or v.startswith("Ore_") for v in ours),
            "CV the cave's new pieces are vanilla (%d: %s ...) and every block in the caves is vanilla or one of ours from before: %s" % (len(new), sorted(new)[:4], sorted(van - have - typ)))
    open(os.path.join(SCRATCH, "cave-ascii.txt"), "w").write("\n\n".join(rep))
    K.notes.append("ASCII: %s" % os.path.join(SCRATCH, "cave-ascii.txt"))
    print("\n\n".join(rep))
    K.save()


# ---------------------------------------------------------------------------------------------------------- RB: the one-time rebuild
def old_box(L, m, slot, size, p, every=6):
    """paint 0.4.17's box cave of `slot` at `size` (and its floor) onto the block map m; returns (shell cells, ore cells)"""
    Geo = L["ShGeo"]
    cx, cz = _ctr(L, slot)
    host, ore, t = _ids(L, slot, p)
    h = HALF[size - 1]
    H = int(Isl_caveH(L, size))
    side = int(Geo.facing(slot))
    shell, ores = [], []
    for dx in range(-h, h + 1):
        for dz in range(-h, h + 1):
            m.put("%d,%d,%d" % (cx + dx, Y, cz + dz), host)
            wall = abs(dx) == h or abs(dz) == h
            for y in range(1, H + 2):
                if y <= H and not wall:
                    continue
                if y <= H and bool(Geo.opening(side, dx, dz, y, h)):
                    continue
                c = (cx + dx, Y + y, cz + dz)
                v = ore if (len(shell) % every) == 3 else host
                m.put("%d,%d,%d" % c, v)
                shell.append(c)
                if v == ore:
                    ores.append(c)
    return shell, ores


def Isl_caveH(L, size):
    return int(L["ShIsl"].caveH(size))


def _rock(L, p, slot):
    """the cells the natural cave wants as rock / ore (from the region's ROCK + ORECELL entries)"""
    Geo = L["ShGeo"]
    want = Geo.region(p, MK)
    cx, cz = _ctr(L, slot)
    h = HALF[2]
    return set((int(b[0]), int(b[1]), int(b[2])) for b in want if int(b[3]) in (int(Geo.ROCK), int(Geo.ORECELL)) and abs(int(b[0]) - cx) <= h and abs(int(b[2]) - cz) <= h)


def run_rebuild(out, jar, scratch, _home):
    K = HK.Child(out)
    from jpype import JClass
    L = _setup(os.path.join(scratch, "rb"), K)
    Geo, Isl, Fill, St, Cfg = L["ShGeo"], L["ShIsl"], L["ShFill"], L["ShStore"], L["ShCfg"]
    HS = JClass("java.util.HashSet")
    Int = JClass("java.lang.Integer")
    sd = str(St.DIR.toString())
    for size in (1, 2, 3):
        p = _mprof(L, [0, 1, 6, 7], size, cave="1")
        slot = 1   # the Iron island (bridge at -30 degrees; slots 8 + 9 hang on it - here slot 8 = index 7)
        cx, cz = _ctr(L, slot)
        host, ore, t = _ids(L, slot, p)
        rock = _rock(L, p, slot)
        m = JClass("java.util.HashMap")()
        shell, ores = old_box(L, m, slot, size, p)
        for s2 in (0, 6, 7):
            old_box(L, m, s2, size, p)
        h = HALF[size - 1]
        # a player's chest in an old wall cell the new cave clears, one inside the old chamber where the new cave has rock, one on the roof
        gone = [c for c in shell if c not in rock]
        inr = [(cx + dx, Y + y, cz + dz) for dx in range(-h + 1, h) for dz in range(-h + 1, h) for y in range(1, Isl_caveH(L, size) + 1) if (cx + dx, Y + y, cz + dz) in rock]
        roof = [c for c in rock if c[1] > Y + Isl_caveH(L, size) + 1]
        K.check(gone and inr and (roof or size == 1), "RB size %d: the new cave clears %d old box cells, has rock at %d old chamber cells, %d above the old roof" % (size, len(gone), len(inr), len(roof)))
        chests = [gone[len(gone) // 2], inr[len(inr) // 3]] + ([roof[0]] if roof else [])
        for c in chests:
            m.put("%d,%d,%d" % c, "Furniture_Crude_Chest_Small")
        # a hand-placed totem where the new cave has rock at y+1
        spot = next(((x - cx, z - cz) for x, y, z in sorted(inr) if y == Y + 1 and max(abs(x - cx), abs(z - cz)) >= 3), None)
        K.check(spot is not None, "RB size %d: a hand-placed totem spot inside new rock (%s)" % (size, spot))
        St.LOCK.lock()
        try:
            p.setProperty("mining.i1.totems", "quarry_spirit:1,quarry_spirit:1:::0:::%d;%d" % spot)
            St.save(OWNER, p)
        finally:
            St.LOCK.unlock()
        before = open(os.path.join(sd, OWNER + ".properties"), "rb").read()
        rw = list(Geo.region(p, MK))
        fixc = [b for b in rw if int(b[3]) == int(Geo.FIX_CAVE)]
        K.check(len(fixc) > 0 and all(int(b[4]) in (200, 201, 206, 207) for b in fixc), "RB size %d: %d FIX_CAVE cells (marker 1 -> the box is cleared once)" % (size, len(fixc)))
        fx = HS()
        Fill.TEST_BLOCKS = m
        n1 = int(Fill.paintY(None, Geo.region(p, MK), fx, None))
        K.check(fx.contains(Int(201)) and n1 > 100, "RB size %d: the rebuild painted %d blocks, the island's FIX cells all done" % (size, n1))
        left = [c for c in gone if c not in chests and _bid(m, *c) in (host, ore)]
        K.check(not left, "RB size %d: every old box cell the new cave does not use is cleared (%d left)" % (size, len(left)))
        K.check(all(_bid(m, *c) == "Furniture_Crude_Chest_Small" for c in chests), "RB size %d: the player's %d chests kept (old wall / old chamber / roof)" % (size, len(chests)))
        tsp = (cx + spot[0], Y + 1, cz + spot[1])
        K.check("Totem" in _bid(m, *tsp) and _bid(m, tsp[0], Y + 2, tsp[2]) == "" and _bid(m, tsp[0], Y + 3, tsp[2]) == "", "RB size %d: the hand-placed totem stands, 2 free above (%s)" % (size, _bid(m, *tsp)))
        nm = int(Fill.markFixed("skyy-shard-" + OWNER, MK, fx))
        p = St.get(OWNER)
        K.check(str(p.getProperty("mining.i1.cave")) == "2" and nm >= 1, "RB size %d: marker mining.i1.cave = 2 (%d marked)" % (size, nm))
        hist = os.path.join(sd, "history", "cave", OWNER + ".pre-0.4.18.properties")
        hs = [f for f in os.listdir(os.path.join(sd, "history", "cave")) if f.startswith(OWNER)]
        newest = max((os.path.join(sd, "history", "cave", f) for f in hs), key=os.path.getmtime)
        K.check(open(newest, "rb").read() == before, "RB size %d: the History copy %s = the file before, byte for byte" % (size, os.path.basename(newest)))
        lp = os.path.join(os.path.dirname(sd), "collect.log")
        log = open(lp, encoding="utf8", errors="replace").read() if os.path.isfile(lp) else ""
        K.check("cave2 (SkyyShards 0.4.18) " + OWNER in log and "Undo: stop the server" in log, "RB size %d: one collect.log line with the Undo" % size)
        rw2 = list(Geo.region(p, MK))
        K.check(not any(int(b[3]) in (int(Geo.FIX_CAVE), int(Geo.FIX_ORE)) for b in rw2 if int(b[4] if len(b) > 4 else 0) in (201, 101)), "RB size %d: the second region lists no FIX cell for the island" % size)
        snap0 = dict((str(k_), str(m.get(k_))) for k_ in m.keySet())
        n2 = int(Fill.paintY(None, Geo.region(p, MK), HS(), None))
        snap1 = dict((str(k_), str(m.get(k_))) for k_ in m.keySet())
        if n2:
            dif = sorted(k_ for k_ in set(snap0) | set(snap1) if snap0.get(k_) != snap1.get(k_))
            K.notes.append("DEBUG second paint: %s" % [(k_, snap0.get(k_), snap1.get(k_)) for k_ in dif[:20]])
        n3 = int(Fill.paintY(None, Geo.region(p, MK), HS(), None))
        K.check(n2 == 0 and n3 == 0, "RB size %d: the second and third paint change nothing (%d, %d)" % (size, n2, n3))
        Fill.TEST_BLOCKS = None
    # a 0.4.7 flat island (no marker): 1 -> 2 in one pass
    p = _mprof(L, [0, 1], 1, cave=None)
    m = JClass("java.util.HashMap")()
    cx, cz = _ctr(L, 1)
    flat = [(cx + dx, Y + 1, cz + dz) for dx in range(-5, 6) for dz in range(-5, 6) if dx % 2 == 0 and dz % 2 == 0 and not (abs(dx) <= 2 and abs(dz) <= 2)]
    for c in flat:
        m.put("%d,%d,%d" % c, "Ore_Copper_Stone")
    fx = HS()
    Fill.TEST_BLOCKS = m
    Fill.paintY(None, Geo.region(p, MK), fx, None)
    rock = _rock(L, p, 1)
    left = [c for c in flat if c not in rock and _bid(m, *c) == "Ore_Copper_Stone"]
    Fill.markFixed("skyy-shard-" + OWNER, MK, fx)
    p = St.get(OWNER)
    K.check(fx.contains(Int(101)) and fx.contains(Int(201)) and str(p.getProperty("mining.i1.cave")) == "2" and not left,
            "RB a 0.4.7 flat island: the old nodes cleared and the box fix done in one pass, marker straight to 2 (%s)" % p.getProperty("mining.i1.cave"))
    # 200 done but the 0.4.8 flat-node fix missing (an unloaded node cell): no marker 2
    p = _mprof(L, [0, 1], 1, cave=None)
    fx = HS()
    fx.add(Int(201))
    Fill.markFixed("skyy-shard-" + OWNER, MK, fx)
    K.check(St.get(OWNER).getProperty("mining.i1.cave") is None, "RB the box fix alone never marks an island whose 0.4.8 node fix is not done")
    # a refused History copy: no marker, a warning; then it marks
    p = _mprof(L, [0, 1], 1, cave="1")
    hd = os.path.join(sd, "history", "cave")
    import shutil
    shutil.rmtree(hd)
    open(hd, "w").write("x")   # a FILE where the folder goes: createDirectories throws
    fx = HS()
    fx.add(Int(201))
    Fill.markFixed("skyy-shard-" + OWNER, MK, fx)
    K.check(str(St.get(OWNER).getProperty("mining.i1.cave")) == "1", "RB a refused History copy: no marker (still 1)")
    os.remove(hd)
    Fill.markFixed("skyy-shard-" + OWNER, MK, fx)
    K.check(str(St.get(OWNER).getProperty("mining.i1.cave")) == "2" and os.path.isdir(hd), "RB the next pass copies + marks")
    K.save()


# ---------------------------------------------------------------------------------------------------------- GX: grow + the profile paths
def run_grow(out, jar, scratch, _home):
    K = HK.Child(out)
    from jpype import JClass
    L = _setup(os.path.join(scratch, "gx"), K)
    Geo, Isl, Fill, St = L["ShGeo"], L["ShIsl"], L["ShFill"], L["ShStore"]
    m = JClass("java.util.HashMap")()
    slot = 1
    cx, cz = _ctr(L, slot)
    for size in (1, 2, 3):
        p = _mprof(L, [0, 1, 6, 7], size)
        host, ore, t = _ids(L, slot, p)
        _paint(L, p, m)
        rk = _rock(L, p, slot)
        h = HALF[size - 1]
        extra = [(cx + dx, y, cz + dz) for dx in range(-h, h + 1) for dz in range(-h, h + 1) for y in range(Y + 1, Y + 17)
                 if _bid(m, cx + dx, y, cz + dz) in (host, ore) and (cx + dx, y, cz + dz) not in rk]
        fl = set(str(Geo.IDS[int(a[t])]) for a in (Isl.STAL, Isl.RUBB, Isl.HALFB))
        want = Geo.region(p, MK)
        wf = set((int(b[0]), int(b[1]), int(b[2])) for b in want if int(b[3]) == int(Geo.DECO_K))
        pieces = [(cx + dx, Y + 1, cz + dz) for dx in range(-h, h + 1) for dz in range(-h, h + 1) if _bid(m, cx + dx, Y + 1, cz + dz) in fl and (cx + dx, Y + 1, cz + dz) not in wf]
        K.check(not extra and not pieces, "GX grown to size %d in place: no rock / ore of a smaller cave left (%d) and no stale floor piece (%d)" % (size, len(extra), len(pieces)))
        snap0 = dict((str(k_), str(m.get(k_))) for k_ in m.keySet())
        n2 = int(Fill.paintY(None, Geo.region(p, MK), None, None))
        snap1 = dict((str(k_), str(m.get(k_))) for k_ in m.keySet())
        dif = sorted(k_ for k_ in set(snap0) | set(snap1) if snap0.get(k_) != snap1.get(k_))
        K.check(n2 == 0, "GX size %d: a second paint changes nothing (%d: %s)" % (size, n2, [(k_, snap0.get(k_), snap1.get(k_)) for k_ in dif[:6]]))
    # Decorations 5 + Irrigation 5 on a Large island: each deco on cave air (or a niche), pools only on the cave floor
    p = _mprof(L, [0, 1, 6, 7], 3, deco=15, irr=15)
    m2, want, _n = _paint(L, p)
    deco = [b for b in want if int(b[3]) == int(Geo.DECO_K) and str(Geo.IDS[int(b[4])]) in set(str(Geo.IDS[int(x)]) for x in Geo.DECOALL)]
    K.check(len(deco) >= 20 and all(_bid(m2, int(b[0]), int(b[1]), int(b[2])) == str(Geo.IDS[int(b[4])]) for b in deco),
            "GX Decorations 15: %d decorations all placed (on cave air or in a niche)" % len(deco))
    wat = [b for b in want if int(b[3]) == int(Geo.WATER)]
    K.check(len(wat) >= 8 and all(_bid(m2, int(b[0]), Y + 1, int(b[2])) == "" for b in wat) and all(m2.get("f:%d,%d,%d" % (int(b[0]), Y, int(b[2]))) is not None for b in wat),
            "GX Irrigation 15: %d pool cells, all water with air above (on the cave floor)" % len(wat))
    # the profile-less 8-argument cave (0.4.8's signature) = the cave with no islands bridged on (only its own mouth)
    o8 = JClass("java.util.ArrayList")()
    Geo.cave(o8, MK, slot, 1, int(Isl.LAD0[MK]) + 1, 2, 0, 0)
    o9 = JClass("java.util.ArrayList")()
    Geo.cave(o9, MK, None, slot, 1, int(Isl.LAD0[MK]) + 1, 2, 0, 0)
    K.check([list(b) for b in o8] == [list(b) for b in o9] and len(o8) > 500, "GX 0.4.8's cave() signature = the profile-less cave (%d cells)" % len(o8))
    # ROCK: over our own ore yes, over a player's block no
    p = _mprof(L, [0, 1], 1)
    host, ore, t = _ids(L, slot, p)
    want = Geo.region(p, MK)
    rocks = [b for b in want if int(b[3]) == int(Geo.ROCK) and abs(int(b[0]) - cx) <= 6 and abs(int(b[2]) - cz) <= 6]
    a, b = rocks[0], rocks[1]
    m3 = JClass("java.util.HashMap")()
    m3.put("%d,%d,%d" % (int(a[0]), int(a[1]), int(a[2])), ore)
    m3.put("%d,%d,%d" % (int(b[0]), int(b[1]), int(b[2])), "Furniture_Crude_Chest_Small")
    Fill.TEST_BLOCKS = m3
    Fill.paintY(None, want, None, None)
    K.check(_bid(m3, int(a[0]), int(a[1]), int(a[2])) == host and _bid(m3, int(b[0]), int(b[1]), int(b[2])) == "Furniture_Crude_Chest_Small",
            "GX a ROCK cell turns our stray ore into host rock, never touches a player's chest (%s, %s)" % (_bid(m3, int(a[0]), int(a[1]), int(a[2])), _bid(m3, int(b[0]), int(b[1]), int(b[2]))))
    Fill.TEST_BLOCKS = None
    K.save()


# ---------------------------------------------------------------------------------------------------------- LV: the live data (scratch copy)
def run_livecave(out, jar, scratch, home):
    K = HK.Child(out)
    from jpype import JClass
    L = _setup(os.path.join(scratch, "lvc"), K)
    Geo, Isl, Fill, St = L["ShGeo"], L["ShIsl"], L["ShFill"], L["ShStore"]
    Paths = JClass("java.nio.file.Paths")
    sd = os.path.join(home, "shards")
    St.DIR = Paths.get(sd)
    keys = [f[:-11] for f in os.listdir(sd) if f.endswith(".properties")]
    seen = 0
    for k in keys:
        p = St.get(k)
        if p is None:
            continue
        isl = [s for s in range(16) if bool(L["ShMath"].hasIsland(MK, p, s))]
        if not isl:
            continue
        m = JClass("java.util.HashMap")()
        for s in isl:
            old_box(L, m, s, int(L["ShMath"].size(MK, p, s)), p)
        before = dict((s, str(p.getProperty("mining.i%d.cave" % s))) for s in isl)
        fx = JClass("java.util.HashSet")()
        Fill.TEST_BLOCKS = m
        Fill.paintY(None, Geo.region(p, MK), fx, None)
        Fill.markFixed("skyy-shard-" + k, MK, fx)
        p = St.get(k)
        after = dict((s, str(p.getProperty("mining.i%d.cave" % s))) for s in isl)
        n2 = int(Fill.paintY(None, Geo.region(p, MK), JClass("java.util.HashSet")(), None))
        orec = []
        for s in isl:
            cx, cz = _ctr(L, s)
            sz = int(L["ShMath"].size(MK, p, s))
            h = HALF[sz - 1]
            host, ore, t = _ids(L, s, p)
            orec.append(sum(1 for dx in range(-h, h + 1) for dz in range(-h, h + 1) for y in range(Y + 1, Y + 17) if _bid(m, cx + dx, y, cz + dz) == ore))
        msg = "LV live %s: Mining islands %s cave %s -> %s, ore %s, a second paint changes %d" % (k[:8], [s + 1 for s in isl], before, after, orec, n2)
        K.check(all(v == "2" for v in after.values()) and n2 == 0 and all(o >= MINN[0] for o in orec), msg)
        K.notes.append(msg)
        seen += 1
        Fill.TEST_BLOCKS = None
    K.check(seen >= 1, "LV %d live profile(s) with Mining islands rebuilt" % seen)
    K.save()


def run_live(out, jar, scratch, home):
    T411.run_live411(out, jar, scratch, home)


EXPECT = {   # 0.4.17 -> 0.4.18, checked by hand 2026-11-03: the version texts (CfgFn opExport / CfgRows header, the ShStore migrate* log lines +
    # save's constant-pool indexes, the ready line in SkyyShardsPlugin.setup) + the round (ShGeo cave / bridge / caveFix, ShFill cell kinds +
    # markFixed, ShIsl's piece tables, ShStore.snapCave)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~m header'],
    'ShFill': ['~m cell', '~m markFixed', '~m paintZ'],
    'ShGeo': ['+f FIX_CAVE', '+f ROCK', '+m carve', '+m cave', '+m caveBase', '+m gi', '+m inner', '+m lane', '+m laneLen', '+m mouth', '+m rnd', '+m vn',
              '~<clinit>', '~m bridge', '~m cave', '~m caveFix', '~m island'],
    'ShIsl': ['+f COBB', '+f HALFB', '+f RUBB', '+f STAL', '~<clinit>'],
    'ShStore': ['+m snapCave', '~m migrate', '~m migrate2', '~m save'],
    'SkyyShardsPlugin': ['~m setup'],
}


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """every non-class file identical (manifest.json aside); the classes as EXPECT"""
    with zipfile.ZipFile(jar) as a, zipfile.ZipFile(old_jar) as b:
        na = dict((n, a.read(n)) for n in a.namelist() if not n.endswith(".class"))
        nb = dict((n, b.read(n)) for n in b.namelist() if not n.endswith(".class"))
    ch = sorted(n for n in set(na) | set(nb) if na.get(n) != nb.get(n) and n != "manifest.json")
    assert not ch, "C non-class files differ: %s" % ch[:8]
    print("C. %d non-class files identical" % len(nb))
    T49._ORIG_COMPARE(out, jar, old_jar, pkg, expect, added, removed)


HK.run_compare = _compare

if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("bridge", run_bridge), ("cave", run_cave), ("rebuild", run_rebuild), ("grow", run_grow),
                   ("livecave", run_livecave),
                   ("open", T416._h(T416._g(T416.run_open), True)), ("bytecode", T415.run_bytecode),
                   ("flows3", T416._h(T416._g(T413.run_flows3))), ("page49", T416._h(T416._p(T49.run_page))),
                   ("live", run_live)],
           script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
