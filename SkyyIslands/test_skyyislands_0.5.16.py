"""Harness for SkyyIslands 0.5.16 (a natural hill + cave mouth on island 1, the respawn trip after the death screen; tools/islands_0_5_16_patch.py).
Build first:  python tools/islands_0_5_16_patch.py && python SkyyIslands/build_skyyislands_0.5.16.py

    python SkyyIslands/test_skyyislands_0.5.16.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  A / C / AA  verify (-Xverify:all), class compare 0.5.15 -> 0.5.16 (exactly the planned members + manifest + the layout data), engine-access
        audit
  CAVE  bare Python on the build's s3_layout() (0.5.15 for comparison) + the jar's StarterIsles data:
        WALK  no cave cell touches the void / the sky (only the mouth's meadow); a player walks from the spawn into the copper tunnel (2-high cells, steps of 1; roots / moss are passable, rubble is not)
              and every tunnel cell is reachable; the floor steps DOWN into the hill (y 128 at the mouth -> 127 inside)
        LOOK  the dark opening shows from the spawn's eye (a clear line into the passage); the mouth faces the spawn (north, -z)
        MOUTH the opening is wider than tall (5 x 3), its outline is jagged (no two rows alike at both edges), framed by >= 5 different
              vanilla rock / soil ids, no one id over 60 %; hanging roots under solid rock, cave moss / rubble on solid ground
        HILL  no flat wall: no 3 x 3 patch of exposed faces in one vertical plane anywhere on island 1's hill (0.5.15's box had one);
              uneven tops (>= 4 heights, no 3 x 3 plateau); grass on every top; the hill meets the meadow in 1-block steps except the
              rock face at the mouth; nothing floats
        ORES  still 8 copper ores on island 1, each in the cave's rock next to a cell the player reaches
        KEEP  only island 1's hill area differs from 0.5.15 (islands 2 + 3, the spawn, chest, plot, trees, old wall, bed identical); the
              named places unchanged; the gatherables the hill covered moved onto it (same counts) + the 3 mouth rubbles; the approach
              in front of the mouth is open meadow
        S3    the 0.5.10 design checks on the new layout (the old "copper cave floor at y 128" check replaced by WALK / ORES above)
        DATA  StarterIsles.decode() in the jar = the build's s3_layout() block for block
  RESP  EXECUTED on a stand-in IsleApi (JProxy): config row + file line (islands.respawnDelaySeconds, 1.8 s, 0.5-10, clamps, bad text),
        respawnLater schedules the trip after 1800 ms (later(), no 800 ms left), a new death clears a parked trip; IsleTask mode 5:
        in a world -> mode 4 there (as 0.5.15); online between worlds -> the 1 s retry; offline -> PARKED in IslandStore.RSP_WAIT
        (retry count reset, with its time; IslandStore.owedTrip drops one older than 60 s), also on the retry; the parked trip run
        after a login -> routes on the login world, and when it routes nowhere (kept world, no island, gave up) the login routing
        runs too (IsleApi.loginRoute); bytecode: IslandReady
        runs a parked trip at the next ready (on the first one instead of the login routing; removed first, scheduled with
        IslandCfg.respawnMs, else RouteTask)
  The REAL server phase is NOT RUN here (tools/smoke_test.py covers the ready line) - the cave's look in game is UNVERIFIED.
Exit code 1 on any failure.
"""
import os, sys, json, math, zipfile, importlib.util, shutil, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import soundpass_kit as SK
import serverjar

VERSION = "0.5.16"
PKG = "com.skyy.islands."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-0.5.15.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "isle0516", "h")))

EXPECT = {
    "IslandCfg": ["+f RESPAWN_DELAY", "+m dbl", "+m respawnMs", "~<clinit>", "~m load"],
    "CfgFile": ["~<clinit>"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],                                  # the version string
    "IslandStore": ["+f RSP_WAIT", "+f RSP_TTL", "+m owedTrip", "~<clinit>"],
    "IsleApi": ["+m online", "+m loginRoute"],
    "IsleEng": ["+m online", "+m loginRoute"],
    "IsleLife": ["~m respawnLater", "+m park", "-m respawnRetry", "+m respawnRetry"],
    "IsleTask": ["+f login", "~m run"],
    "IslandReady": ["~m accept"],
    "SkyyIslandsPlugin": ["~m setup"],
    "FillTask": ["~m run"],                                    # the layout's block count
    "StarterIsles": ["~<clinit>", "~m decode", "~m fill", "~m placeOf", "~m publish"],   # the layout data + the places text (cave y 128)
}
ADDED = []


def run_compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the kit's compare; its non-class check replaced: only the manifest changes (Version / Name)"""
    HK._kit_compare(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    d["fails"] = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    na = set(n_ for n_ in za.namelist() if not n_.endswith(".class"))
    nb = set(n_ for n_ in zb.namelist() if not n_.endswith(".class"))
    changed = sorted(n_ for n_ in na & nb if za.read(n_) != zb.read(n_))
    if na != nb or changed != ["manifest.json"]:
        d["fails"].append("C: non-class entries: added %s removed %s changed %s" % (sorted(nb - na), sorted(na - nb), changed))
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    for m_, v_ in ((ma, "0.5.15"), (mb, VERSION)):
        if m_.pop("Version", None) != v_ or m_.pop("Name", None) != v_ + " SkyyIslands":
            d["fails"].append("C: manifest Version / Name are not %s" % v_)
    if ma != mb:
        d["fails"].append("C: manifest changed beyond Version / Name")
    d["ok"] += 1
    json.dump(d, open(out, "w"), indent=1)


HK._kit_compare = HK.run_compare
HK.run_compare = run_compare


def layout_of(v):
    os.environ["S3_ONLY"] = "1"
    sp = importlib.util.spec_from_file_location("build_skyyislands_%s_s3" % v.replace(".", "_"), os.path.join(HERE, "build_skyyislands_%s.py" % v))
    m = importlib.util.module_from_spec(sp)
    try:
        sp.loader.exec_module(m)
    except ImportError as e:
        assert "S3_ONLY" in str(e), e
    finally:
        del os.environ["S3_ONLY"]
    return m


# ================================================================================================ CAVE (bare Python)
PASS = ("Plant_Roots_Cave", "Plant_Moss_Cave_Green", "Plant_Grass")      # Material Empty / grass tufts: walk and look through


def passable(L, p):
    b = L.get(p)
    return b is None or b.startswith(PASS)


def standable(L, p):
    b = L.get(p)
    return b is not None and not b.startswith(("Plant_", "Rubble_", "Wood_Sticks"))


def walk(L, start=(8, 129, 8)):
    """feet cells a 2-high player reaches from the spawn: 1-block steps up (head room for the jump), any drop of 1"""
    seen = {start}
    q = collections.deque([start])
    while q:
        x, y, z = q.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for dy in (0, 1, -1):
                n = (x + dx, y + dy, z + dz)
                if n in seen or not (-25 < n[0] < 45 and -25 < n[2] < 45):
                    continue
                if passable(L, n) and passable(L, (n[0], n[1] + 1, n[2])) and standable(L, (n[0], n[1] - 1, n[2])) \
                        and (dy <= 0 or passable(L, (x, y + 2, z))) and (dy >= 0 or passable(L, (n[0], n[1] + 2, n[2]))):
                    seen.add(n)
                    q.append(n)
    return seen


def los(L, e, t):
    for i in range(1, 600):
        f = i / 600.0
        c = tuple(int(math.floor(e[k] + (t[k] - e[k]) * f)) for k in range(3))
        if not passable(L, c):
            return False, c
    return True, None


def flat_patches(L, cells):
    """3 x 3 patches of exposed faces in one vertical plane, among the solid blocks in `cells` (x, z columns)"""
    faces = set()
    for (x, y, z), b in L.items():
        if (x, z) not in cells or y < 129 or b.startswith(("Plant_", "Rubble_", "Wood_Sticks")):
            continue
        for a, c, k in ((1, 0, "E"), (-1, 0, "W"), (0, 1, "S"), (0, -1, "N")):
            if passable(L, (x + a, y, z + c)) and not L.get((x + a, y, z + c), "").startswith("Plant_Grass"):
                faces.add((k, x, y, z))
    out = []
    for (k, x, y, z) in faces:
        along = (1, 0) if k in ("N", "S") else (0, 1)
        if all((k, x + along[0] * i, y + j, z + along[1] * i) in faces for i in range(3) for j in range(3)):
            out.append((k, x, y, z))
    return sorted(out)


def cave_checks(K, m, old):
    L, tops, isle = m.S3_L, m.S3_TOPS, m.S3_ISLE
    L0 = old.S3_L
    hill = set(c for c, t in tops.items() if isle.get(c) == "island1" and t > 128)
    hill0 = set(c for c, t in old.S3_TOPS.items() if old.S3_ISLE.get(c) == "island1" and t > 128)
    # ---- WALK
    seen = walk(L)
    tunnel = [(x, 128, z) for x in range(12, 19) for z in (15, 16)]
    K.check(all(c in seen for c in tunnel), "WALK a player walks from the spawn into the copper tunnel: %d / %d tunnel cells reached (missing %s)"
            % (sum(1 for c in tunnel if c in seen), len(tunnel), [c for c in tunnel if c not in seen][:4]))
    K.check(all((x, 129, 12) in seen for x in range(10, 14)) and all(standable(L, (x, 127, 15)) and passable(L, (x, 128, 15)) for x in range(12, 19))
            and min(y for (x, y, z) in seen if 11 <= x <= 14 and z == 12) == 129 and min(y for (x, y, z) in seen if 11 <= x <= 14 and z == 14) == 128,
            "WALK the floor steps DOWN into the hill: feet at y 129 in the mouth (z 12), y 128 in the passage (z 14) and the tunnel (3 high)")
    K.check(all(passable(L, (x, y, z)) for x in range(12, 19) for z in (15, 16) for y in (128, 129, 130)),
            "WALK the tunnel is 3 high (y 128-130, a hanging root / cave moss at most) all along x 12-18")
    # ---- LOOK
    ok_, hit = los(L, (8.5, 130.6, 8.5), (12.5, 129.8, 13.8))
    ok0, _h0 = los(L0, (8.5, 130.6, 8.5), (12.5, 130.0, 13.8))
    K.check(ok_, "LOOK the dark opening shows from the spawn's eye (8.5,130.6,8.5 -> into the passage): blocked at %s" % (hit,))
    K.check(all((x, 128, z) in L and (x, 129, z) not in L for x in range(10, 15) for z in range(9, 12) if (x, z) not in ((10, 11), (14, 11)))
            and all(tops[(x, z)] == 128 for x in range(10, 15) for z in range(6, 12)),
            "LOOK the mouth faces the spawn (north, -z; the spawn is at z 8.5): the meadow in front (x 10-14, z 6-11) is open, flat at y 128")
    air = m.s3_cave_air()
    holes = []
    for (x, y, z) in sorted(air):
        for a, b, c in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            n = (x + a, y + b, z + c)
            if n in air or n in L:
                continue
            if c == -1 and z == 12 and n[2] == 11 and 9 <= n[0] <= 15:
                continue                         # the open meadow in front of the mouth
            holes.append((x, y, z, n))
    K.check(not holes, "WALK every cave cell's 6 neighbours are rock, cave or the mouth's meadow - no hole to the void / the sky: %s" % holes[:4])
    # ---- MOUTH
    hole = lambda x, y: passable(L, (x, y, 12)) or L.get((x, y, 12), "").startswith("Rubble_")
    op = sorted((x, y) for x in range(8, 17) for y in range(129, 134)
                if hole(x, y) and any(standable(L, (x, yy, 12)) for yy in range(y + 1, y + 4)))   # under the hill's rock = the opening
    xs, ys = [p[0] for p in op], [p[1] for p in op]
    w, h = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
    rows = dict((y, (min(x for x, yy in op if yy == y), max(x for x, yy in op if yy == y))) for y in set(ys))
    K.check(w == 5 and h == 3 and w > h, "MOUTH the opening at z 12 is wider than tall: %d x %d" % (w, h))
    K.check(len(set(r[0] for r in rows.values())) >= 2 and len(set(r[1] for r in rows.values())) >= 2 and len(set(rows.values())) == len(rows),
            "MOUTH a jagged outline (rows %s): no straight frame line" % sorted(rows.items()))
    ring = collections.Counter()                 # the frame: every block of the face within 1 of the opening (floor included)
    for q in set((x + a, y + b, 12) for (x, y) in op for a in (-1, 0, 1) for b in (-1, 0, 1)):
        if (q[0], q[1]) not in op and standable(L, q):
            ring[L[q]] += 1
    tot = sum(ring.values())
    K.check(len(ring) >= 5 and max(ring.values()) <= 0.6 * tot, "MOUTH framed by a mix (%d ids, %s)" % (len(ring), dict(ring)))
    roots = [k for k, b in L.items() if b == "Plant_Roots_Cave"]
    moss = [k for k, b in L.items() if b == "Plant_Moss_Cave_Green"]
    K.check(len(roots) >= 4 and all(standable(L, (x, y + 1, z)) and not L[(x, y + 1, z)].startswith("Soil_Gravel") for x, y, z in roots),
            "MOUTH hanging roots under solid rock (Support Up): %s" % sorted(roots))
    K.check(len(moss) >= 3 and all(standable(L, (x, y - 1, z)) for x, y, z in moss), "MOUTH cave moss on solid ground (Support Down): %s" % sorted(moss))
    grav = [k for k, b in L.items() if b == "Soil_Gravel" and isle.get((k[0], k[2])) == "island1"]
    K.check(grav and all(standable(L, (x, y - 1, z)) for x, y, z in grav), "MOUTH every gravel block stands on a solid block (%d)" % len(grav))
    mr = [k for k, b in L.items() if b.startswith("Rubble_") and 9 <= k[0] <= 15 and 10 <= k[2] <= 12]
    K.check(len(mr) >= 2, "MOUTH a little rubble at the mouth: %s" % sorted(mr))
    # ---- HILL
    fp0, fp1 = flat_patches(L0, hill0), flat_patches(L, hill)
    K.check(fp0 and not fp1, "HILL no flat wall: 3 x 3 coplanar face patches on the hill - 0.5.15 (the box) %d, 0.5.16 %d %s" % (len(fp0), len(fp1), fp1[:3]))
    th = [tops[c] for c in hill]
    plateau = [c for c in hill if all(tops.get((c[0] + a, c[1] + b)) == tops[c] for a in (0, 1, 2) for b in (0, 1, 2))]
    K.check(len(set(th)) >= 4 and not plateau, "HILL uneven tops: heights %s, 3 x 3 plateaus %s" % (sorted(set(th)), plateau[:3]))
    K.check(all(L.get((x, tops[(x, z)], z)) == "Soil_Grass" for x, z in hill), "HILL grass on every top")
    steep = []
    for (x, z) in hill:
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + a, z + b)
            if isle.get(n) == "island1" and tops.get(n) == 128 and tops[(x, z)] > 129:
                steep.append((x, z, n))
    K.check(all(9 <= x <= 15 and 11 <= z <= 13 for x, z, _n in steep),
            "HILL meets the meadow in 1-block steps except the rock face at the mouth: %s" % sorted(set((x, z) for x, z, _n in steep)))
    K.check(len(hill) >= 100 and max(th) <= 135, "HILL size: %d columns (0.5.15 %d), top y %d" % (len(hill), len(hill0), max(th)))
    isl = set(k for k in L if isle.get((k[0], k[2])) == "island1")
    seen_, todo = set(), [(8, 126, 8)]
    while todo:
        p = todo.pop()
        if p in seen_ or p not in isl:
            continue
        seen_.add(p)
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            todo.append((p[0] + d[0], p[1] + d[1], p[2] + d[2]))
    K.check(not isl - seen_, "HILL nothing floats on island 1 (%s)" % sorted(isl - seen_)[:4])
    # ---- ORES
    cu = sorted(k for k, b in L.items() if b == "Ore_Copper_Stone" and isle.get((k[0], k[2])) == "island1")
    cu0 = sorted(k for k, b in L0.items() if b == "Ore_Copper_Stone" and old.S3_ISLE.get((k[0], k[2])) == "island1")
    cavef = [p for p in seen if 10 <= p[0] <= 18 and 12 <= p[2] <= 17 and p[1] <= 129]       # feet in the cave
    def mineable(c):                             # an open face, within 3.5 blocks of a reachable eye (feet + 1.6)
        for a, b, d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            f = (c[0] + a, c[1] + b, c[2] + d)
            if passable(L, f) and any(math.sqrt((f[0] - p[0]) ** 2 + (f[1] + 0.5 - p[1] - 1.6) ** 2 + (f[2] - p[2]) ** 2) <= 3.5 for p in cavef):
                return True
        return False
    bad = [c for c in cu if not mineable(c)]
    K.check(len(cu) == len(cu0) == 8 and not bad, "ORES still 8 copper ores on island 1, each with an open face in reach from inside the cave (not: %s)" % bad)
    K.eq(cu, sorted(m.S3_CAVE_ORES), "ORES = S3_CAVE_ORES")
    K.check(len(set(cu) & set(cu0)) == 5, "ORES the 5 wall ores kept their cells (%s)" % sorted(set(cu) & set(cu0)))
    # ---- KEEP
    diff = set(k for k in set(L) | set(L0) if L.get(k) != L0.get(k))
    K.check(diff and all(isle.get((x, z)) == "island1" and 5 <= x <= 22 and 8 <= z <= 21 for x, y, z in diff),
            "KEEP only island 1's hill area differs (%d blocks, x %d-%d z %d-%d)" % (len(diff), min(k[0] for k in diff), max(k[0] for k in diff),
                                                                                  min(k[2] for k in diff), max(k[2] for k in diff)))
    keep = [(4, 129, 4), (8, 128, 8), (8, 129, 8), (8, 130, 8)] + [(x, y, z) for x in range(11, 14) for z in range(2, 6) for y in (128, 129)] \
        + list(m.S3_BED_CELLS) + list(m.S3_BED_GROUND) + [(-3, y, z) for z in range(5, 13) for y in range(129, 133)]
    K.check(all(L.get(k) == L0.get(k) for k in keep), "KEEP the chest, the spawn, the starter plot + wheat, the ruins bed, the old wall: identical")
    K.check(all(L.get(k) == b for k, b in L0.items() if isle.get((k[0], k[2])) != "island1")
            and all(L0.get(k) == b for k, b in L.items() if isle.get((k[0], k[2])) != "island1"), "KEEP islands 2 + 3 and the plank stubs identical")
    pl0 = dict(old.S3_PLACES)
    pl0["cave"] = (12.5, 128.0, 15.5, "The copper cave")
    K.eq(m.S3_PLACES, pl0, "KEEP the named places (island:places) unchanged but 'cave', lowered with the floor to y 128")
    K.check(passable(L, (12, 128, 15)) and passable(L, (12, 129, 15)) and standable(L, (12, 127, 15)), "KEEP the 'cave' place stands on the cave floor")
    gath = ("Plant_Bush", "Plant_Bush_Green", "Wood_Sticks", "Rubble_Stone", "Rubble_Stone_Mossy", "Plant_Grass_Lush_Short")
    c0 = collections.Counter(b for k, b in L0.items() if b in gath and old.S3_ISLE.get((k[0], k[2])) == "island1")
    c1 = collections.Counter(b for k, b in L.items() if b in gath and isle.get((k[0], k[2])) == "island1")
    want = c0 + collections.Counter(b for _p, b in m.S3_CAVE_RUBBLE)
    K.eq(dict(c1), dict(want), "KEEP the gatherables on island 1: the same counts (+ the 3 rubbles at the mouth)")
    K.check(not [k for k, b in L.items() if b in gath and (k[0], k[2]) in set(m.S3_CAVE_FRONT) and (k, b) not in m.S3_CAVE_RUBBLE],
            "KEEP no gatherable in front of the mouth (only the rubbles at its sides)")
    K.check(all(L.get((x, tops[(x, z)] + 1, z)) in (None,) + gath or L.get((x, tops[(x, z)] + 1, z), "").startswith("Plant_Moss")
                for (x, z) in hill), "KEEP the hill carries only gatherables on its tops")


class _Wrap(object):
    """T510.design_checks through this: its 'copper cave' check (0.5.10's floor at y 128) is replaced by WALK / ORES"""
    def __init__(self, K):
        self.K, self.skipped = K, []

    def check(self, cond, what):
        if what.startswith("DESIGN the copper cave") or what.startswith("DESIGN island 3: 6 broken pillars, the portal frame"):
            self.skipped.append(what)
            return True
        return self.K.check(cond, "S3 " + what)

    def eq(self, got, want, what):
        return self.check(got == want, "%s: got %r, want %r" % (what, got, want))


def run_cave(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    m = layout_of(VERSION)
    old = layout_of("0.5.15")
    cave_checks(K, m, old)
    # the 0.5.10 design checks (imports the 0.5.10 harness, as 0.5.11's did; Assets.zip = the CACHED copy)
    _spec = importlib.util.spec_from_file_location("test_skyyislands_0_5_10", os.path.join(HERE, "test_skyyislands_0.5.10.py"))
    T510 = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(T510)

    class _ZipShim(object):
        import zipfile as _z

        def ZipFile(self, path, *a, **k):
            if str(path).replace("\\", "/").endswith("game/latest/Assets.zip"):
                path = serverjar.assets_zip()
            return self._z.ZipFile(path, *a, **k)
    T510.zipfile = _ZipShim()
    T510.JAR = jar
    wk = _Wrap(K)
    T510.design_checks(wk, m)
    K.check(len(wk.skipped) == 2, "S3 exactly the old copper-cave floor check (-> WALK / ORES) + island 3's portal frame count (gone since 0.5.13; island 3 "
            "= 0.5.15 in KEEP) replaced: %d" % len(wk.skipped))
    # DATA: the jar's layout
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    S3 = JClass(PKG + "StarterIsles")
    r = list(S3.decode())
    pal = [str(x) for x in S3.PAL]
    got = {}
    for i in range(int(S3.RUNS)):
        p, x, y, z, n = r[i * 5:i * 5 + 5]
        for k in range(n):
            got[(x + k, y, z)] = pal[p]
    K.check(got == m.S3_L and int(S3.BLOCKS) == len(m.S3_L), "DATA StarterIsles.decode() = the build's s3_layout() block for block (%d blocks)" % len(got))
    K.eq(list(S3.CHUNKS), [v for c in m.S3_CHUNKS for v in c], "DATA chunks")
    K.save()


# ================================================================================================ RESP (stand-in engine)
def stand_in(iface, impl):
    """a JImplements stand-in for every abstract method of iface: impl's methods where it has them, else a neutral answer"""
    from jpype import JClass, JImplements, JOverride, JLong, JInt
    neutral = {"boolean": False, "int": JInt(0), "long": JLong(0), "void": None}
    body = {}
    for mm in JClass(iface).class_.getMethods():
        n, rt = str(mm.getName()), str(mm.getReturnType().getName())
        if hasattr(impl, n):
            body[n] = JOverride((lambda f: lambda self, *a: f(*a))(getattr(impl, n)))
        else:
            body[n] = JOverride((lambda v: lambda self, *a: v)(neutral.get(rt)))
    return JImplements(iface)(type("Stand", (object,), body))()


def run_resp(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(PKG + n)
    St, Cfg, Life, Task, Rows = P("IslandStore"), P("IslandCfg"), P("IsleLife"), P("IsleTask"), P("CfgRows")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    shutil.rmtree(os.path.join(scratch, "resp"), ignore_errors=True)
    home = os.path.join(scratch, "resp", "Skyy_SkyyIslands")
    os.makedirs(os.path.join(home, "islands"), exist_ok=True)
    # ---------------------------------------------------------------- CFG
    cf = os.path.join(home, "config.properties")
    Cfg.FILE = Paths.get(cf)
    Cfg.load("")
    txt = open(cf, encoding="utf-8").read()
    K.check("islands.respawnDelaySeconds=1.8" in txt.splitlines() and float(Cfg.RESPAWN_DELAY) == 1.8 and int(Cfg.respawnMs()) == 1800,
            "CFG a fresh config.properties lists islands.respawnDelaySeconds=1.8; default 1.8 s = 1800 ms")
    old = "\n".join(l for l in txt.splitlines() if "respawnDelaySeconds" not in l and "0.5.16" not in l) + "\n"
    open(cf, "w", encoding="utf-8").write(old)
    Cfg.RESPAWN_DELAY = 3.0
    Cfg.load("")
    K.check(float(Cfg.RESPAWN_DELAY) == 1.8 and open(cf, encoding="utf-8").read() == old, "CFG a 0.5.15 file without the line = 1.8 s, not rewritten")
    for typed, want in (("2.5", 2500), ("99", 10000), ("0.1", 500), ("soon", 1800), ("NaN", 1800), (" 0.75 ", 750)):
        open(cf, "w", encoding="utf-8").write(old + "islands.respawnDelaySeconds=%s\n" % typed)
        Cfg.load("")
        K.eq(int(Cfg.respawnMs()), want, "CFG hand edit %r -> %d ms (clamped 0.5-10 s, bad text = 1.8 s)" % (typed, want))
    open(cf, "w", encoding="utf-8").write(txt)
    Cfg.load("")
    Cfg.RESPAWN_DELAY = 0.0
    K.eq(int(Cfg.respawnMs()), 500, "CFG respawnMs clamps a field set below 0.5 s")
    Cfg.RESPAWN_DELAY = 1.8
    rows = SK.kit_rows(Rows)
    r_ = rows.get("islands.respawnDelaySeconds")
    K.check(r_ is not None and tuple(r_[1:9]) == ("Respawn trip delay", "hub", "dec", "1.8", "0.5", "10", "step=0.1", "s") and "live" in r_[9],
            "ROW Server Setup -> Hub -> Respawn trip delay (dec, 1.8, 0.5-10 s, live): %s" % (r_,))
    # ---------------------------------------------------------------- the stand-in engine
    W, DW = "skyy-island-x", "default"
    uA = UUID.fromString("00000000-0000-4000-8000-0000000a0516")
    A = {"where": {}, "online": set(), "later": [], "exec": [], "login": []}
    from jpype import JArray, JObject

    class Api(object):
        def later(self, r, ms):
            A["later"].append((r, int(ms)))
            return True

        def worldOf(self, u):
            w = A["where"].get(str(u))
            return None if w is None else JString(w)

        def online(self, u):
            return str(u) in A["online"]

        def exec(self, wn, r):
            A["exec"].append((str(wn), r))
            return True

        def players(self, wn):
            return JArray(JObject)([JArray(JObject)([UUID.fromString(k), JObject(0.5, "java.lang.Double"), JObject(129.0, "java.lang.Double"),
                                                     JObject(0.5, "java.lang.Double")]) for k, w in A["where"].items() if w == str(wn)])

        def loginRoute(self, u):
            A["login"].append(str(u))
    Life.API = stand_in(PKG + "IsleApi", Api())
    St.DIR = Paths.get(os.path.join(home, "islands"))      # no island files: uA has no island
    St.IO = None
    St.STOPPING = False
    St.SETTINGS.clear()
    St.loadIslandWorlds()

    def clear():
        for k in ("later", "exec", "login"):
            A[k][:] = []
    St.RSP_WAIT.clear()
    Cfg.RESPAWN_HOME = True
    now = lambda: int(JClass("java.lang.System").currentTimeMillis())
    parked = lambda: St.RSP_WAIT.get(uA)
    entry = lambda t, ms: JArray(JObject)([t, JObject(ms, "java.lang.Long")])
    # respawnLater: 1.8 s, through later(); clears a parked trip
    St.RSP_WAIT.put(uA, entry(Task(5, JString(W), uA), now()))
    Life.respawnLater(JString(DW), uA)
    K.check(len(A["later"]) == 1 and A["later"][0][1] == 1800 and int(A["later"][0][0].mode) == 5 and str(A["later"][0][0].wn) == DW
            and not bool(A["later"][0][0].login) and not St.RSP_WAIT.containsKey(uA),
            "RESP respawnLater -> the trip (IsleTask mode 5, the death world, not a login trip) after 1800 ms; a parked trip cleared")
    t5 = A["later"][0][0]
    # in a world -> mode 4 there (0.5.15)
    A["where"][str(uA)] = W
    A["online"].add(str(uA))
    t5.run()
    K.check(len(A["exec"]) == 1 and A["exec"][0][0] == W and int(A["exec"][0][1].mode) == 4 and str(A["exec"][0][1].a) == DW
            and not bool(A["exec"][0][1].login), "RESP mode 5, the player in a world -> mode 4 on that world (a = the death world), as 0.5.15")
    t4 = A["exec"][0][1]
    clear()
    t4.run()                                  # a normal trip that routes nowhere (no island) -> nothing else
    K.check(not A["login"], "RESP a normal trip that routes nowhere -> no login routing (as 0.5.15)")
    # online, between worlds -> the 1 s retry (no park)
    clear()
    del A["where"][str(uA)]
    t5.run()
    K.check(len(A["later"]) == 1 and A["later"][0][1] == 1000 and int(A["later"][0][0].fl) == 1 and not A["exec"] and not St.RSP_WAIT.containsKey(uA),
            "RESP mode 5, online between worlds -> once more in 1 s (fl 1), nothing parked")
    retry = A["later"][0][0]
    # offline -> parked (the trip itself + the time, retry count reset, a login trip)
    clear()
    A["online"].discard(str(uA))
    t0 = now()
    retry.run()
    pk = parked()
    K.check(not A["later"] and not A["exec"] and pk is not None and len(pk) == 2 and pk[0].equals(retry) and int(retry.fl) == 0
            and bool(retry.login) and t0 <= int(pk[1]) <= now(),
            "RESP logged out before the retry -> PARKED in IslandStore.RSP_WAIT as {the trip, the time} (retry count reset, marked a login trip)")
    St.RSP_WAIT.clear()
    t6 = Task(5, JString(DW), uA)
    t6.run()
    K.check(parked() is not None and parked()[0].equals(t6) and not A["later"] and not A["exec"], "RESP logged out before the first trip -> parked (never lost)")
    # expiry: IslandStore.owedTrip (what IslandReady calls)
    K.eq(int(St.RSP_TTL), 60000, "RESP a parked trip lives 60 s")
    St.RSP_WAIT.put(uA, entry(t6, now() - 61000))
    K.check(St.owedTrip(uA, now()) is None and not St.RSP_WAIT.containsKey(uA), "RESP owedTrip: a trip parked 61 s ago -> dropped (the login routing runs as usual)")
    St.RSP_WAIT.put(uA, t6)
    K.check(St.owedTrip(uA, now()) is None and not St.RSP_WAIT.containsKey(uA), "RESP owedTrip: a malformed entry -> dropped")
    St.RSP_WAIT.put(uA, entry(t6, now() - 30000))
    owed = St.owedTrip(uA, now())
    K.check(owed is not None and owed.equals(t6) and not St.RSP_WAIT.containsKey(uA) and St.owedTrip(uA, now()) is None,
            "RESP owedTrip: a trip parked 30 s ago -> returned once, removed")
    # the next login runs it: routes on the login world, as a login trip
    A["online"].add(str(uA))
    A["where"][str(uA)] = "hub"
    owed.run()
    K.check(len(A["exec"]) == 1 and A["exec"][0][0] == "hub" and str(A["exec"][0][1].a) == DW and int(A["exec"][0][1].mode) == 4
            and bool(A["exec"][0][1].login), "RESP the parked trip after the login -> the routing on the world they logged in to (a = the death world)")
    # review fix: a login trip that routes nowhere -> the login routing too
    for dw, why in (("skyy-shard-z", "died in a world that keeps its respawn"), (DW, "no island / bed where they died")):
        clear()
        tl = Task(4, JString("hub"), uA)
        tl.a, tl.login = JString(dw), True
        tl.run()
        K.check(A["login"] == [str(uA)], "RESP a parked trip that routes nowhere (%s) -> the login routing still runs (Start on your island / Hub on login)" % why)
    clear()
    tl = Task(4, JString("other"), uA)        # not in that world: the retry carries the login flag ...
    tl.a, tl.login = JString(DW), True
    tl.run()
    K.check(len(A["later"]) == 1 and bool(A["later"][0][0].login) and int(A["later"][0][0].fl) == 1 and not A["login"],
            "RESP a parked trip's retry carries its login flag (no login routing yet)")
    clear()
    tl.fl = 1                                 # ... and when it gives up -> the login routing
    tl.run()
    K.check(not A["later"] and A["login"] == [str(uA)], "RESP a parked trip that gives up -> the login routing")
    clear()
    del A["where"][str(uA)]
    tl = Task(5, JString(DW), uA)
    tl.fl, tl.login = 1, True
    tl.run()
    K.check(not A["later"] and A["login"] == [str(uA)], "RESP a parked trip still between worlds after its retry -> the login routing")
    # setting off -> nothing parked
    Cfg.RESPAWN_HOME = False
    A["online"].discard(str(uA))
    St.RSP_WAIT.clear()
    Task(5, JString(DW), uA).run()
    K.check(not St.RSP_WAIT.containsKey(uA), "RESP Respawn on your island off -> nothing parked")
    Cfg.RESPAWN_HOME = True
    # ---------------------------------------------------------------- bytecode
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for mm in pool.get(PKG + cn).getDeclaredMethods():
            if str(mm.getName()) == mn:
                IP(PS(bos)).print_(mm)
        return str(bos.toString())
    acc = code("IslandReady", "accept")
    i_seen, i_wait = acc.find("IslandStore.SEEN"), acc.find("IslandStore.owedTrip")
    i_ms, i_route, i_note = acc.find("IslandCfg.respawnMs"), acc.find("RouteTask.schedule"), acc.find("JoinNote.schedule")
    K.check(0 <= i_seen < i_wait < i_ms < i_route < i_note and "SCHEDULED_EXECUTOR" in acc[i_wait:i_route],
            "RESP IslandReady: a parked trip is removed and scheduled (respawnMs) on the player's next ready - on the first ready of a session INSTEAD of the "
            "login routing (also after a quick relog, before the old session's mark is gone); the join notes as before")
    K.check(acc.find("IslandStore.owedTrip") < acc.find("ArrivalTask.schedule"), "RESP IslandReady: the parked trip is looked at before the first-ready return")
    rl = code("IsleLife", "respawnLater")
    K.check("800" not in rl and "IslandCfg.respawnMs" in rl and "IsleApi.later" in rl and "RSP_WAIT" in rl, "RESP respawnLater: no 800 ms left; respawnMs through later()")
    K.check("IsleLife.respawnLater" in code("IsleRespawn", "onComponentRemoved"), "RESP the respawn hook still calls respawnLater")
    Life.API = None
    K.save()


if __name__ == "__main__":
    print("S. real-server phase: NOT RUN in this harness (tools/smoke_test.py) - the cave's look in game UNVERIFIED")
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("cave", run_cave), ("resp", run_resp)], script=__file__)
