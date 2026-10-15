"""Harness for SkyyArmory 0.1.27 (THE STAFF BLINK GOES PAST ENEMIES; tools/armory_0_1_27_patch.py). Build first:
    python tools/armory_0_1_27_patch.py && python SkyyArmory/build_skyyarmory_0.1.27.py

    python SkyyArmory/test_skyyarmory_0.1.27.py [--jar <SkyyArmory-0.1.27.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.26 -> 0.1.27: only TravMath (+ EYE, spotL, moved, scanL) and ArmoryTrav.blink differ (the wand hop, Shadow Step, kunai,
               Levitate, TravTick's trail untouched); non-class: manifest only
  X   exec     TravMath.scanL on a fake block grid (TravGrid = blocks only - an entity can never stop it): aiming at a mob over flat ground
               (a few degrees down) reaches the far block end past the mob (0.1.26's scan: none); the mob is inside the trail capsule;
               level / upward looks = scan to the bit (random grids); a downward look never lands inside a block, never higher than the
               start, never past the max distance; walls / steps / ceilings / unknown blocks still stop it; straight down = no blink;
               blink calls scanL (bytecode), nothing else calls it
  AA  audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, math, random, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.27", "0.1.26"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "armory0127", "armory")))
PKG = "com.skyy.armory."
# the version texts (as 0.1.25's list: ArmoryCheck pack name, ArmoryCfg / CfgRows default file line, CfgFn / CfgRows header, the ready line)
# + the change: TravMath (+ EYE, spotL, moved, scanL) and ArmoryTrav.blink
EXPECT = {"TravMath": ["+f EYE", "+m moved", "+m scanL", "+m spotL"], "ArmoryTrav": ["~m blink"],
          "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "ArmoryCheck": ["~m packCheck", "~m packOf"], "CfgFn": ["~m opExport"],
          "CfgRows": ["~<clinit>", "~m header"], "SkyyArmoryPlugin": ["~m setup"]}
ADDED = []
EYE = 1.6


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    TM = JClass(PKG + "TravMath")
    K.eq(float(TM.EYE), EYE, "X0: TravMath.EYE = the player's eye height (Player.json EyeHeight 1.6)")

    @JImplements(PKG + "TravGrid")
    class Grid:
        def __init__(self, fn): self.fn = fn

        @JOverride
        def at(self, x, y, z): return int(self.fn(int(x), int(y), int(z)))

    def world(walls=(), floor=63, unknown=lambda x, y, z: False, floor_ok=lambda x, z: True):
        def fn(x, y, z):
            if unknown(x, y, z):
                return -1
            if y <= floor and floor_ok(x, z):
                return 1
            for w_ in walls:
                if w_(x, y, z):
                    return 1
            return 0
        return Grid(fn)

    def L(g, s, d, D=16.0, f=0):
        r = TM.scanL(g, s[0], s[1], s[2], d[0], d[1], d[2], D, f)
        return round(float(r[0]), 6), round(float(r[1]), 6)

    def S(g, s, d, D=16.0, f=0):
        return round(float(TM.scan(g, s[0], s[1], s[2], d[0], d[1], d[2], D, f)), 6)

    def land(s, d, t, y):
        n = math.sqrt(sum(c * c for c in d))
        return (s[0] + d[0] / n * t, y, s[2] + d[2] / n * t)

    flat = world()
    st = (0.5, 64.0, 0.5)
    # X1. aiming at a mob 6 blocks ahead on flat ground: from the eye (65.6) to its middle (64.9) = 6.7 degrees down
    mob = (6.5, 64.0, 0.5)
    d1 = (mob[0] - st[0], (mob[1] + 0.9) - (st[1] + EYE), 0.0)
    old1, new1 = S(flat, st, d1), L(flat, st, d1)
    p1 = land(st, d1, new1[0], new1[1])
    K.check(old1 == 0.0, "X1: 0.1.26's feet scan, aiming at the mob 6 blocks ahead = no blink at all (the feet box hits the floor): %s" % old1)
    K.check(new1[0] > 13.0 and new1[1] == 64.0 and p1[0] > mob[0] + 6.0,
            "X1: 0.1.27 scanL carries you PAST the mob to where the crosshair meets the ground (~13.8 along, x %.2f, feet on the floor 64): %s"
            % (p1[0], new1))
    K.check(int(TM.body(flat, p1[0], p1[1], p1[2])) == 0, "X1: the landing body box is free (never inside a block)")
    r = 1.5 / 2.0
    sd = float(TM.segDist(mob[0], mob[1] + 0.9, mob[2], st[0], st[1] + 0.9, st[2], p1[0], p1[1] + 0.9, p1[2]))
    K.check(sd <= r + 0.4, "X1: the mob stands inside the light trail capsule start -> landing (TravTick hits it): %.3f <= %.2f" % (sd, r + 0.4))
    # the same at 12 and 20 blocks (3.4 / 2.1 degrees down): 0.1.26 = none / 1.4 blocks INTO the mob; 0.1.27 = the full 16
    for dist, want_old in ((12.0, 0.0), (20.0, 1.4)):
        dd = (dist, 0.9 - EYE, 0.0)
        o, nw = S(flat, st, dd), L(flat, st, dd)
        K.check(o == want_old and nw == (16.0, 64.0), "X1: a mob %g blocks ahead: 0.1.26 %s, 0.1.27 %s (the full 16, feet on the floor)" % (dist, o, nw))
    # X2. level / upward looks = TravMath.scan to the bit (random grids with walls, ceilings, holes, unknown blocks)
    rnd = random.Random(127)
    same = 0
    for k in range(400):
        cells = {}
        for _ in range(rnd.randint(0, 40)):
            cells[(rnd.randint(-8, 16), rnd.randint(63, 72), rnd.randint(-8, 8))] = rnd.choice((1, 1, 1, -1))
        holes = set((rnd.randint(-4, 16), rnd.randint(-4, 4)) for _ in range(rnd.randint(0, 20)))

        def fn(x, y, z, cells=cells, holes=holes):
            if (x, y, z) in cells:
                return cells[(x, y, z)]
            return 1 if (y <= 63 and (x, z) not in holes) else 0
        g = Grid(fn)
        d = (rnd.uniform(-1, 1), rnd.uniform(0.0, 1.0) if k % 4 else 0.0, rnd.uniform(-1, 1))
        fl = rnd.choice((0, 0, 3, 12))
        o = S(g, st, d, 16.0, fl)
        nw = L(g, st, d, 16.0, fl)
        n = math.sqrt(sum(c * c for c in d))
        want_y = round(st[1] + d[1] / n * o, 6) if o > 0 else st[1]
        if nw[0] == o and abs(nw[1] - want_y) < 1e-6:
            same += 1
        else:
            K.check(False, "X2: level / up look differs from scan: d %s floor %s -> scan %s, scanL %s" % (d, fl, o, nw))
    K.check(same == 400, "X2: 400 random level / upward looks: scanL = scan (distance and feet height) every time: %d" % same)
    # X3. downward looks on random terrain: never inside a block, never above the start, never past the max distance, real move >= 1
    bad = []
    lifted = 0
    for k in range(600):
        cells = {}
        for _ in range(rnd.randint(0, 50)):
            cells[(rnd.randint(-16, 16), rnd.randint(58, 70), rnd.randint(-16, 16))] = rnd.choice((1, 1, 1, 0, -1))
        drop = set((rnd.randint(-16, 16), rnd.randint(-16, 16)) for _ in range(rnd.randint(0, 30)))

        def fn(x, y, z, cells=cells, drop=drop):
            if (x, y, z) in cells:
                return cells[(x, y, z)]
            return 1 if y <= (61 if (x, z) in drop else 63) else 0
        g = Grid(fn)
        d = (rnd.uniform(-1, 1), -rnd.uniform(0.005, 1.5), rnd.uniform(-1, 1))
        D = rnd.choice((3.0, 10.0, 16.0, 21.0))
        fl = rnd.choice((0, 0, 0, 2, 12))
        t, y = L(g, st, d, D, fl)
        if t == 0.0:
            continue
        p = land(st, d, t, y)
        n = math.sqrt(sum(c * c for c in d))
        if y > st[1] + 1e-9 or t > D + 1e-9 or int(TM.body(g, p[0], p[1], p[2])) != 0 or not bool(TM.ground(g, p[0], p[1], p[2], fl)):
            bad.append((d, D, fl, t, y))
        if math.sqrt((p[0] - st[0]) ** 2 + (p[1] - st[1]) ** 2 + (p[2] - st[2]) ** 2) < 1.0 - 1e-6:
            bad.append(("moved < 1", d, t, y))
        if abs(y - (st[1] + d[1] / n * t)) > 1e-6:
            lifted += 1
    K.check(not bad, "X3: 600 random downward looks: every landing body free, on ground when the floor check asks, <= the start height, <= the "
            "max distance, a real move >= 1 block (%d stood on a floor): %s" % (lifted, bad[:3]))
    # X4. what still stops it (the same block rules)
    wall6 = world([lambda x, y, z: x == 6 and 64 <= y <= 66])
    t4, y4 = L(wall6, st, (1.0, -0.05, 0.0))
    p4 = land(st, (1.0, -0.05, 0.0), t4, y4)
    K.check(y4 == 64.0 and 5.0 < p4[0] <= 5.701, "X4: a wall at x 6, looking a little down: stops before it on the floor (x %.3f): %s" % (p4[0], (t4, y4)))
    step = world([lambda x, y, z: x >= 5 and y == 64])
    t5, y5 = L(step, st, (1.0, -0.04, 0.0))
    p5 = land(st, (1.0, -0.04, 0.0), t5, y5)
    K.check(p5[0] <= 4.701 and y5 == 64.0, "X4: a 1-block step up ahead: never climbs above the start height (stops at x %.3f): %s" % (p5[0], (t5, y5)))
    t6 = L(world(unknown=lambda x, y, z: x >= 4), st, (1.0, -0.05, 0.0))
    K.check(land(st, (1.0, -0.05, 0.0), t6[0], t6[1])[0] <= 3.701, "X4: an unloaded section stops it like a wall: %s" % (t6,))
    d7 = (1.0, -1.0, 0.0)
    t7, y7 = L(flat, st, d7)
    K.check(y7 == 64.0 and abs(t7 - 2.25) < 1e-6, "X4: 45 degrees down at the ground: lands where the crosshair meets it (2.25 along, eye ray 2.26): %s" % ((t7, y7),))
    K.eq(L(flat, st, (0.0, -1.0, 0.0)), (0.0, 64.0), "X4: straight down = no blink (it would not move you, costs nothing)")
    K.eq(L(flat, st, (0.01, -1.0, 0.0)), (0.0, 64.0), "X4: almost straight down = no blink")
    cliff = world(floor_ok=lambda x, z: x <= 3)
    dc = (1.0, -0.2, 0.0)
    se = (4.4, 64.0, 0.5)          # just past the cliff edge (the first step is clear of the floor block x 3)
    K.eq(L(cliff, se, dc), (S(cliff, se, dc), round(64.0 - 0.2 / math.sqrt(1.04) * S(cliff, se, dc), 6)), "X4: down off a cliff edge = 0.1.26 (nothing under = no lift)")
    K.check(S(cliff, se, dc) == 16.0, "X4: ... the full 16 into the air (no void protection, Skyy): %s" % S(cliff, se, dc))
    tc, yc = L(cliff, st, dc)
    K.check(tc == 16.0 and yc < 64.0 - 2.0, "X4: 3 blocks back from the edge, looking down past it: walks the floor, then over the edge into the air (0.1.26: none): %s" % ((tc, yc),))
    bridge = world([lambda x, y, z: x >= 2 and y == 60], floor=-999)          # a 1-thick floor at y 60, the player on it at 61
    t8 = L(bridge, (0.5 + 3, 61.0, 0.5), (1.0, -3.0, 0.0))
    K.check(t8[1] == 61.0, "X4: steeply down on a 1-thick bridge: the crosshair ray stops at the bridge, never through it: %s" % (t8,))
    K.eq(L(None, st, (1.0, -0.1, 0.0)), (0.0, 64.0), "X4: no grid = no blink")
    K.eq(L(flat, st, (0.0, 0.0, 0.0)), (0.0, 64.0), "X4: no direction = no blink")
    K.eq(L(flat, st, (1.0, -0.02, 0.0), 0.0), (0.0, 64.0), "X4: max distance 0 = no blink")
    t9 = L(flat, st, (1.0, -0.001, 0.0), 21.0)
    K.check(t9[0] == 21.0 and 63.95 < t9[1] <= 64.0, "X4: blink.distance 20 + Long Blink: the full 21 on a flat floor, never more (feet within the "
            "0.05 floor tolerance, as 0.1.26): %s" % (t9,))
    # X5. the code paths: blink calls scanL; scan is still there for Levitate / the kunai / Shadow Step; nothing else calls scanL
    from jpype import JClass as JC
    CP = JC("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(jar)
    calls = {}
    with zipfile.ZipFile(jar) as z:
        for n in z.namelist():
            if n.endswith(".class") and n.startswith("com/skyy/armory/"):
                cc = CP.get(n[:-6].replace("/", "."))
                for m in cc.getDeclaredMethods():
                    ci =m.getMethodInfo().getCodeAttribute()
                    if ci is None:
                        continue
                    it = ci.iterator()
                    cpl = m.getMethodInfo().getConstPool()
                    while it.hasNext():
                        pos = it.next()
                        op = it.byteAt(pos)
                        if op == 0xb8:
                            idx = it.u16bitAt(pos + 1)
                            if str(cpl.getMethodrefClassName(idx)) == PKG + "TravMath" and str(cpl.getMethodrefName(idx)) in ("scan", "scanL"):
                                calls.setdefault(str(cpl.getMethodrefName(idx)), []).append(str(cc.getSimpleName()) + "." + str(m.getName()))
    K.eq(sorted(calls.get("scanL", [])), ["ArmoryTrav.blink"], "X5: only the staff blink calls scanL")
    K.check("ArmoryTrav.blink" not in calls.get("scan", []) and len(calls.get("scan", [])) == 3,
            "X5: scan stays for the other 3 callers (Levitate room, kunai, Shadow Step), not the blink: %s" % calls.get("scan"))
    K.notes.append("X1: 6-block mob: 0.1.26 %s, 0.1.27 %s; X3 lifted %d of 600" % (old1, new1, lifted))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyArmory", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, [("exec", run_exec)], __file__)
