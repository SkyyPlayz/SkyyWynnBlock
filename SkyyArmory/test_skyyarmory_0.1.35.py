"""Harness for SkyyArmory 0.1.35 (BETA BUGS 5 + 6, the Armory part; tools/armory_0_1_35_patch.py). Build first:
    python tools/armory_0_1_35_patch.py && python SkyyArmory/build_skyyarmory_0.1.35.py

    python SkyyArmory/test_skyyarmory_0.1.35.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.34 -> 0.1.35: exactly the planned members (EXPECT); non-class entries: manifest.json only
  R   repro    BUG 5 ON THE OLD 0.1.34 JAR: the real Monk.edges() driven tick by tick (no engine: every engine read falls back) through the
               4 skip timelines below - the bound does NOT fire on 3 of them (the bug); the same timelines on 0.1.35 (phase X) bound
  X   exec     X1 the rows + loader (defaults, a file without the new lines = defaults); X2 the 4 timelines on 0.1.35 bound, each once, with
               the "(how)" debug line; spikeKind's rule table; no double bound on our own push; the chain still ends without a jump;
               X3 Skyy's skip notes: each bound asks skill:fn:regenblock for a block until just after its landing (a stand-in bridge fn), off
               switches; X4 BUG 6: rayOpen / seesT on a stand-in TravGrid (open, 2-high wall, 1-high wall seen over, floor, unreadable,
               own / enemy block skipped, no grid) + sweep / rise / riseTick really call seesT (bytecode); X5 migrate035's text step on
               synthetic files (0.1 -> 0.3 + marker, hand value kept, no line = marker only, marker = never again, CRLF kept)
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration in setup's order + load): the 1st start changes
               exactly bound.after 0.1 -> 0.3 + the marker line (History copy + change-log line), the 2nd start changes nothing
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): pauseStam (the StaminaRegenDelay stat write - the grapple's own path), the Monk hits' real
world grid (WorldGrid = the blink's), the client's reported vertical speed at a real skip (read the "Bound ... (how)" debug lines).
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.35", "0.1.34"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ac-bugs", "armory")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
EXPECT = {"ArmoryCfg": ["+f M35_KEY", "+f M35_OLD", "+f M35_NEW", "+f M35_MARK", "+f M35_MARK_ID", "+f M35_WHO", "+f M35_LAST",
                        "+f MK_BSPEED", "+f MK_BSPAUSE", "+f MK_BNOMANA", "+f MK_LOS", "+m m35Key", "+m m35Update", "+m m35Log", "+m migrate035",
                        "~<clinit>", "~m apply", "~m load", "~m reloadAll", "~m useDefaults", "~m monkText"],
          "ArmoryCheck": ["~m packCheck", "~m packOf"],          # the version text
          "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"], "CfgFile": ["~<clinit>"],          # the rows + version text
          "Monk": ["+f SPIKES", "+f LOS_MISS", "+f PAUSED", "+f MANA_BLOCKS", "~<clinit>", "+m spikeKind", "+m rayOpen", "+m seesT", "+m losGrid",
                   "+m pauseStam", "+m noManaRegen", "+m rest", "+m nearGround", "~m bound", "~m edges", "~m sweep", "~m rise", "~m riseTick"],
          "MonkState": ["+f prevVy"],
          "SkyyArmoryPlugin": ["~m setup", "~m start"]}          # migrate035 + its line, the version text

DT = 33          # one server tick (ms)


# ---------------------------------------------------------------------------------------------------------------- the skip timelines
# each step = (ground, jumping, client vy); the chain is armed (a Pole-Vault landed before). Real-world shapes of Skyy's "the skip does not fire":
#  T1 land seen, the jump key tapped 200 ms after the landing (a human's "on landing" - outside 0.1.34's 0.1 s window)
#  T2 space HELD through the landing: jumping never drops, the client jumps again right away (no jumping edge)
#  T3 land-and-jump inside one server tick: the server never sees the ground; jumping stays true from the last bound (no edge, no landing)
#  T4 the tap is seen as an edge 40 ms after a seen landing (0.1.34 already bounds - the control)
FALL = [(False, False, -4.0), (False, False, -8.0), (False, False, -12.0)]
TL = {
    "T1": FALL + [(True, False, 0.0)] * 6 + [(False, True, 11.8), (False, True, 10.0)],
    "T2": [(False, True, -4.0), (False, True, -8.0), (False, True, -12.0), (True, True, 0.0), (False, True, 11.8), (False, True, 10.0)],
    "T3": [(False, True, -4.0), (False, True, -8.0), (False, True, -12.0), (False, True, 11.8), (False, True, 10.0)],
    "T4": FALL + [(True, False, 0.0), (False, True, 11.8), (False, True, 10.0)],
}


GRIDS = {}


def grid(JClass, kind="floor"):
    """a stand-in TravGrid (ArmoryTrav.GRID seam): 'floor' = solid at y <= 68 (the timelines land near y 69), 'unknown' = unreadable everywhere"""
    if kind not in GRIDS:
        from jpype import JImplements, JOverride, JInt

        @JImplements(PKG + "TravGrid")
        class G(object):
            @JOverride
            def at(self, x, y, z):
                return JInt(-1 if kind == "unknown" else (1 if int(y) <= 68 else 0))
        GRIDS[kind] = G()
    return GRIDS[kind]


def drive(JClass, steps, t0=1_000_000, y0=70.0, g_kind="floor"):
    """the real Monk.edges() + heldFall() on 0.1.34 / 0.1.35, the tickPlayer bookkeeping copied (ground / land / leave / jEdge / fall), no engine
    (buf / ref / player null: Leap.take pays, jumpForce = 11.8, the pushes do nothing). Returns (bounds, debug lines)."""
    from jpype import JArray, JDouble
    Monk, MS = JClass(PKG + "Monk"), JClass(PKG + "MonkState")
    V3, UUID, AL = JClass("org.joml.Vector3d"), JClass("java.util.UUID"), JClass("java.util.ArrayList")
    u = UUID.fromString("00000000-0000-0000-0035-000000000001")
    s = MS(u, None, None)
    sink = AL()
    Monk.SINK = sink
    Monk.DEBUG.put(u, True)
    s.chain, s.move, s.lastLand, s.boundDone, s.prevGround = True, 0, 0, False, False
    s.leftAt = t0 - 1000
    s.prevJump = steps[0][1]          # T2 / T3: the jump key / state is held since the last bound
    b0 = int(Monk.BOUNDS)
    JClass(PKG + "ArmoryTrav").GRID = grid(JClass, g_kind) if g_kind else None
    y = y0
    now = t0
    for g, jmp, vy in steps:
        now += DT
        Monk.CLOCK = now
        y += vy * DT / 1000.0
        land = g and not s.prevGround
        leave = (not g) and s.prevGround
        jedge = jmp and not s.prevJump
        s.prevGround, s.prevJump = g, jmp
        if leave:
            s.leftAt, s.airTopY, s.fallMax = now, y, 0.0
        if not g:
            s.airTopY = max(s.airTopY, y)
            s.fallMax = max(s.fallMax, s.airTopY - y)
        Monk.edges(s, None, None, None, V3(0.5, y, 0.5), JArray(JDouble)([0.0, vy, 0.0]), g, land, leave, jedge, False, now)
    Monk.CLOCK = 0
    return int(Monk.BOUNDS) - b0, [str(x) for x in sink], s


def setup_jvm(jar, *more):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR] + list(more) + [jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    return JClass


def run_repro(out, jar, scratch, _home):
    K = HK.Child(out)
    JClass = setup_jvm(OLD_JAR)
    K.check(abs(float(JClass(PKG + "ArmoryCfg").MK_BAFTER) - 0.1) < 1e-9, "R: 0.1.34's bound.after is 0.1 s")
    got = {}
    for k in sorted(TL):
        n, lines, _s = drive(JClass, TL[k])
        got[k] = n
        K.notes.append("R %s on 0.1.34: %d bound(s) %s" % (k, n, [l for l in lines if l.startswith("Bound")][:2]))
    K.check(got == {"T1": 0, "T2": 0, "T3": 0, "T4": 1}, "R: REPRO bug 5 on the old jar - the skip does not fire on T1 (tap 200 ms late), T2 (space held), "
            "T3 (land-and-jump inside a tick); only T4 (a jump edge 40 ms after a seen landing) bounds: %s" % got)
    K.save()


def run_exec(out, jar, scratch, _home):
    from jpype import JImplements, JOverride, JInt, JBoolean
    K = HK.Child(out)
    JClass = setup_jvm(jar, B.JAVASSIST)
    Cfg, Monk, Defs = JClass(PKG + "ArmoryCfg"), JClass(PKG + "Monk"), JClass(PKG + "ArmoryDefs")
    Props, SR = JClass("java.util.Properties"), JClass("java.io.StringReader")
    DEF = str(Cfg.DEF_CFG)
    # ---- X1 rows + loader
    want = ["bound.after=0.3", "bound.bySpeed=true", "bound.staminaPause=0.5", "bound.noManaRegen=true", "monk.lineOfSight=true"]
    K.check(all(("\n" + w + "\n") in DEF for w in want) and str(Cfg.M35_MARK) in DEF and "\nbound.after=0.1\n" not in DEF,
            "X1: a fresh config.properties carries the new defaults + the 0.1.35 marker: %s" % [w for w in want if ("\n" + w + "\n") not in DEF])

    def apply(drop=(), **kv):
        p = Props()
        p.load(SR(DEF))
        for k in drop:
            p.remove(k)
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p)

    def cur():
        return [round(float(Cfg.MK_BAFTER), 3), bool(Cfg.MK_BSPEED), round(float(Cfg.MK_BSPAUSE), 3), bool(Cfg.MK_BNOMANA), bool(Cfg.MK_LOS)]
    apply()
    K.eq(cur(), [0.3, True, 0.5, True, True], "X1: the loader reads the defaults")
    apply(drop=["bound.bySpeed", "bound.staminaPause", "bound.noManaRegen", "monk.lineOfSight"])
    K.eq(cur(), [0.3, True, 0.5, True, True], "X1: a live file WITHOUT the 4 new lines = the defaults (no update needed)")
    apply(bound__staminaPause="9", bound__after="2", bound__bySpeed="false", monk__lineOfSight="false")
    K.eq(cur(), [0.4, False, 3.0, True, False], "X1: hand edits clamped (pause 9 -> 3, after 2 -> 0.4), switches read")
    apply()
    mt = str(Cfg.monkText())
    K.check("also from the jump seen by speed" in mt and "Stamina regen pause 0.5 s" in mt and "need a clear line" in mt, "X1: monkText names the new rules: %s" % mt[-260:])

    # ---- X2 the 4 timelines on 0.1.35 (the same driver as R)
    REG = []

    @JImplements("java.util.function.Function")
    class RegenFn(object):
        @JOverride
        def apply(self, o):
            a = list(o)
            REG.append((str(a[0]), int(a[1].longValue())))
            return JBoolean(True)
    br = Defs.bridge()
    br.put("skill:fn:regenblock", RegenFn())
    got, how = {}, {}
    for k in sorted(TL):
        n, lines, s = drive(JClass, TL[k])
        got[k] = n
        how[k] = [l for l in lines if l.startswith("Bound ")]
    K.check(got == {"T1": 1, "T2": 1, "T3": 1, "T4": 1}, "X2: FIX bug 5 - every timeline bounds exactly once on 0.1.35: %s" % got)
    K.check("198 ms after landing" in " ".join(how["T1"]), "X2: T1 (tap 200 ms late) bounds inside the 0.3 s window: %s" % how["T1"])
    K.check("jump seen by speed" in " ".join(how["T2"]) and "after landing" in " ".join(how["T2"]), "X2: T2 (space held) bounds by speed after the seen landing: %s" % how["T2"])
    K.check("jump seen by speed, landing hidden" in " ".join(how["T3"]), "X2: T3 (no landing seen) bounds by speed, landing hidden: %s" % how["T3"])
    K.check(how["T4"] and "after landing" in how["T4"][0] and "speed" not in how["T4"][0], "X2: T4 still bounds by the jump edge (the old way in): %s" % how["T4"])
    # no jump at all after the landing: the chain ends (no bound by the vault landing alone)
    n0, l0, s0 = drive(JClass, FALL + [(True, False, 0.0)] * 12)
    K.check(n0 == 0 and not bool(s0.chain) and any("Bounds ended" in l for l in l0), "X2: no jump within 0.3 s of the landing = no bound and the chain ends: %s" % l0[-1:])
    # our own bound's push next tick + a long rise never re-trigger; a second real jump after the next landing bounds again
    two = TL["T4"] + [(False, True, 9.0), (False, True, 4.0), (False, True, -3.0), (False, True, -9.0), (True, True, 0.0), (False, True, 11.8)]
    n2, l2, _ = drive(JClass, two)
    K.check(n2 == 2, "X2: a chain of 2 skips = 2 bounds (the rise after a bound never counts twice): %s" % [l for l in l2 if l.startswith("Bound")])
    # the pure rule table
    sk = lambda *a: int(Monk.spikeKind(*a))
    rows = [((True, 0, False, False, 11.8, 0.0, 11.8, 40, 300), 1), ((True, 0, False, False, 11.8, 0.0, 11.8, 250, 300), 1),
            ((True, 0, False, False, 11.8, 0.0, 11.8, 250, 100), 0), ((True, 0, True, True, 11.8, -12.0, 11.8, -1, 300, True), 2),
            ((True, 0, True, True, 11.8, -12.0, 11.8, -1, 300, False), 0),
            ((False, 0, True, False, 11.8, -12.0, 11.8, 40, 300), 0), ((True, 2, True, False, 11.8, -12.0, 11.8, 40, 300), 0),
            ((True, 0, False, False, 11.8, 9.0, 11.8, 40, 300), 0), ((True, 0, False, True, 11.8, 0.0, 11.8, 40, 300), 0),
            ((True, 0, False, False, float("nan"), 0.0, 11.8, 40, 300), 0), ((True, 0, False, False, 5.0, 0.0, 11.8, 40, 300), 0),
            ((True, 0, False, False, 6.0, 0.0, 0.0, 40, 300), 1), ((True, 0, False, False, 11.8, 0.0, 11.8, -1, 300), 0)]
    rows = [(a if len(a) == 10 else a + (False,), w) for a, w in rows]
    bad = [(a, w, sk(*a)) for a, w in rows if sk(*a) != w]
    K.check(not bad, "X2: spikeKind's table (seen landing in / out of the window, hidden landing at the ground / NOT at the ground, no chain, a move running, already rising, "
            "bound done, NaN, under half a jump, no jump force = 5.9, no landing at all): %s" % bad)
    Cfg.MK_BSPEED = False
    nf = {k: drive(JClass, TL[k])[0] for k in ("T2", "T3")}
    Cfg.MK_BSPEED = True
    K.check(nf == {"T2": 0, "T3": 0}, "X2: bound.bySpeed off = the old jump-edge rule only: %s" % nf)
    # review: a mid-air knockback / jump pad / grapple pull / Double Jump during a chain's fall, 10 blocks above the floor: never a bound
    KB = [(False, True, -4.0), (False, True, -8.0), (False, True, -12.0), (False, True, 12.0), (False, True, 10.0), (False, True, 6.0)]
    nk, lk, _sk = drive(JClass, KB, y0=80.0)
    nu, _lu, _su = drive(JClass, KB, y0=80.0, g_kind="unknown")
    nn = drive(JClass, KB, y0=80.0, g_kind=None)[0]
    nt3u = drive(JClass, TL["T3"], g_kind="unknown")[0]
    K.check(nk == 0 and nu == 0 and nn == 0, "X2: REVIEW - an upward push in mid-air (10 blocks up, falling at 12 b/s the tick before) = no bound, "
            "with the floor read, unreadable blocks or no grid: %s %s" % ((nk, nu, nn), [l for l in lk if l.startswith("Bound")]))
    K.check(nt3u == 0, "X2: unreadable blocks + a fast fall the tick before = no hidden-landing bound (only a near-stop -5 .. 0.5 counts): %d" % nt3u)
    JClass(PKG + "ArmoryTrav").GRID = grid(JClass, "floor")
    ngr = [bool(JClass(PKG + "Monk").nearGround(None, JClass("org.joml.Vector3d")(0.5, 69.6, 0.5), -12.0)),
           bool(JClass(PKG + "Monk").nearGround(None, JClass("org.joml.Vector3d")(0.5, 72.0, 0.5), -12.0))]
    JClass(PKG + "ArmoryTrav").GRID = grid(JClass, "unknown")
    ngr += [bool(JClass(PKG + "Monk").nearGround(None, JClass("org.joml.Vector3d")(0.5, 72.0, 0.5), -3.0)),
            bool(JClass(PKG + "Monk").nearGround(None, JClass("org.joml.Vector3d")(0.5, 72.0, 0.5), -12.0))]
    JClass(PKG + "ArmoryTrav").GRID = None
    K.eq(ngr, [True, False, True, False], "X2: nearGround - floor 1 block under the feet yes, 3 blocks no; unreadable: a near-stop yes, a fast fall no")

    # ---- X3 Skyy's skip notes: the Mana regen block per bound
    del REG[:]
    t0 = 2_000_000
    n3, _l, s3 = drive(JClass, TL["T4"], t0=t0)
    bt = int(s3.lastBoundAt)
    import math
    vyb = 11.8 * math.sqrt(1.4)
    want = int(round(2000.0 * vyb / float(Monk.grav()))) + 300 + 250
    K.check(n3 == 1 and len(REG) == 1 and REG[0][0] == str(s3.u) and abs(REG[0][1] - bt - want) <= 2,
            "X3: a bound blocks natural Mana regen until just after its landing (flight 2 vy / g + bound.after 0.3 + 0.25 s = %d ms): %s (bound at %d)" % (want, REG, bt))
    Cfg.MK_BNOMANA = False
    del REG[:]
    drive(JClass, TL["T4"])
    Cfg.MK_BNOMANA = True
    K.check(not REG, "X3: bound.noManaRegen off = no block asked")
    br.remove("skill:fn:regenblock")
    n4 = drive(JClass, TL["T4"])[0]
    K.check(n4 == 1, "X3: without SkyySkills (no skill:fn:regenblock) the bound still fires")
    K.check(not bool(Monk.pauseStam(None, None, 0.5)) and not bool(Monk.pauseStam(None, None, 0.0)), "X3: pauseStam never throws (no stats = nothing)")

    # ---- X4 bug 6: the line checks
    TG = JClass(PKG + "TravGrid")

    @JImplements(PKG + "TravGrid")
    class Grid(object):
        def __init__(self, solid, unknown=False):
            self.solid, self.unknown = solid, unknown

        @JOverride
        def at(self, x, y, z):
            if self.unknown:
                return JInt(-1)
            return JInt(1 if (int(x), int(y), int(z)) in self.solid else 0)
    floor = set((x, 63, z) for x in range(-3, 12) for z in range(-3, 4))
    wall2 = floor | {(3, 64, z) for z in range(-3, 4)} | {(3, 65, z) for z in range(-3, 4)}
    wall1 = floor | {(3, 64, z) for z in range(-3, 4)}
    cave = floor | set((x, 62, z) for x in range(-3, 12) for z in range(-3, 4))
    see = lambda g, ty=64.0, tx=6.5, ay=65.0: bool(Monk.seesT(g, 0.5, ay, 0.5, tx, ty, 0.5, 1.8))
    res = {"open": see(Grid(floor)), "wall2": see(Grid(wall2)), "wall1": see(Grid(wall1)), "below": see(Grid(cave), ty=60.0, tx=1.5),
           "unknown": see(Grid(set(), True)), "nogrid": bool(Monk.seesT(None, 0.5, 65.0, 0.5, 6.5, 64.0, 0.5, 1.8)),
           "ownblock": bool(Monk.rayOpen(Grid({(0, 65, 0), (6, 64, 0)}), 0.5, 65.0, 0.5, 6.5, 64.5, 0.5))}
    K.eq(res, {"open": True, "wall2": False, "wall1": True, "below": False, "unknown": True, "nogrid": True, "ownblock": True},
         "X4: FIX bug 6 - open field seen; a 2-high wall blocks; a 1-high wall is seen over (its top); a mob under the floor is not; unreadable "
         "blocks / no grid never cost a hit; your own block and the enemy's block are skipped")
    # the three Monk hits really ask seesT (bytecode: invokestatic Monk.seesT inside sweep / rise / riseTick)
    CP = JClass("javassist.ClassPool")(True)
    CP.appendClassPath(jar)
    cc = CP.get(PKG + "Monk")
    calls = {}
    for m in cc.getDeclaredMethods():
        nm = str(m.getName())
        if nm not in ("sweep", "rise", "riseTick", "edges", "bound"):
            continue
        ca = m.getMethodInfo().getCodeAttribute()
        cp = m.getMethodInfo().getConstPool()
        it = ca.iterator()
        found = set()
        while it.hasNext():
            p = it.next()
            if it.byteAt(p) == 0xb8:
                found.add(str(cp.getMethodrefName(it.u16bitAt(p + 1))))
        calls[nm] = found
    K.check(all("seesT" in calls.get(n, ()) and "losGrid" in calls.get(n, ()) for n in ("sweep", "rise", "riseTick")),
            "X4: the vault kick (sweep), Rising Strike (rise) and the Plunge slam (riseTick) check the line: %s" % {k: sorted(v & {"seesT", "losGrid"}) for k, v in calls.items()})
    K.check("spikeKind" in calls.get("edges", ()) and "rest" in calls.get("bound", ()), "X4: edges asks spikeKind, bound calls rest")
    Cfg.MK_LOS = False
    K.check(Monk.losGrid(None) is None, "X4: monk.lineOfSight off -> no grid = every hit as before")
    Cfg.MK_LOS = True

    # ---- X5 migrate035's text step
    def upd(t):
        r = Cfg.m35Update(t)
        return None if r is None else (str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]])
    src = "# a\nbound.before=0.25\n# w\nbound.after=0.1\nbound.distance=5\n"
    a = upd(src)
    K.check(a is not None and "\nbound.after=0.3\n" in a[0] and str(Cfg.M35_MARK) in a[0] and a[1] == "bound.after 0.1 -> 0.3" and a[3] == ["bound.after", "0.1", "0.3"]
            and a[0].replace(str(Cfg.M35_MARK) + "\n", "").replace("bound.after=0.3", "bound.after=0.1") == src,
            "X5: a line still at 0.1 -> 0.3 + the marker, nothing else changed: %s" % (a and a[1]))
    K.check(upd(a[0]) is None, "X5: the marker = never again")
    h = upd(src.replace("bound.after=0.1", "bound.after=0.2"))
    K.check(h is not None and "bound.after=0.2" in h[0] and h[1] == "" and h[2] and "kept (custom)" in h[2][0], "X5: a hand-set 0.2 is kept + named: %s" % (h and h[2]))
    nl = upd("# x\nbound.distance=5\n")
    K.check(nl is not None and str(Cfg.M35_MARK) in nl[0] and nl[1] == "" and "bound.distance=5" in nl[0], "X5: no bound.after line = the marker only")
    cr = upd(src.replace("\n", "\r\n"))
    K.check(cr is not None and "bound.after=0.3\r\n" in cr[0] and cr[0].count("\r\n") == src.count("\n") + 1 and "\n" not in cr[0].replace("\r\n", ""),
            "X5: CRLF kept (every line, the marker too)")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    f = os.path.join(home, "config.properties")
    before = open(f, "rb").read()
    snaps, msgs = [], []
    for start in (1, 2):
        for m in ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035"):
            r = str(getattr(Cfg, m)())
            if m == "migrate035":
                msgs.append(r)
        Cfg.load()
        snaps.append(open(f, "rb").read())
    K.check(snaps[0] == snaps[1] and msgs[1] == "", "D: the 2nd start changes nothing")
    b, a = before.decode("latin-1"), snaps[0].decode("latin-1")
    eol = "\r\n" if "\r\n" in b else "\n"
    had01 = (eol + "bound.after=0.1" + eol) in b
    exp = b.replace(eol + "bound.after=0.1" + eol, eol + "bound.after=0.3" + eol) if had01 else b
    K.check(a.replace(str(Cfg.M35_MARK) + eol, "") == exp and a.count(str(Cfg.M35_MARK)) == 1,
            "D: the 1st start changed only bound.after (%s) + added the marker: %s" % ("0.1 -> 0.3" if had01 else "no 0.1 line", msgs[0][:160]))
    K.check(abs(float(Cfg.MK_BAFTER) - (0.3 if had01 else float(Cfg.MK_BAFTER))) < 1e-9 and bool(Cfg.MK_BSPEED) and bool(Cfg.MK_LOS), "D: the loader reads 0.3 + the new rows' defaults")
    hist = [os.path.join(dp, fn) for dp, _d, fns in os.walk(home) for fn in fns if fn != "config.properties"]
    held = [p for p in hist if open(p, "rb").read() == before]
    logl = [l for p in hist for l in open(p, "rb").read().decode("latin-1").splitlines() if "SkyyArmory 0.1.35" in l and "bound.after" in l]
    K.check(held and (logl or not had01), "D: a History copy holds the old bytes (%d) and the change log has the bound.after line (%s)" % (len(held), logl[:1]))
    K.notes.append("D: live config %d bytes, bound.after was 0.1: %s; files %s" % (len(before), had01, [os.path.relpath(p, home) for p in hist][:6]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("repro", run_repro), ("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyArmory"))
