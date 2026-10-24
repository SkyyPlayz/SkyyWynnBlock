"""Harness for SkyyArmory 0.1.47 (round shield1: the Spellblade great shield bash + the 30-block steerable Bulwark Charge;
tools/armory_0_1_47_patch.py). Build first:
    python tools/armory_0_1_47_patch.py && python SkyyArmory/build_skyyarmory_0.1.47.py
    python SkyyArmory/test_skyyarmory_0.1.47.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S   static   the patch re-runs to identical bytes; one new class (ArmoryWishSys) registered once (ordered + the unordered fallback = 2 calls),
               no command; the jar vs 0.1.46: added = the class only; changed non-class = manifest + the 4 bash / slam files (ONLY the knockback
               Force 22 / 30 and the arc 120 / -60) + the lang file (ONLY the 15 great shield descriptions); every great shield item file
               byte-identical; the 9 new rows; the 8 retired rows in CFG_HIDDEN; the build fix for "<version> <mod>" manifest names
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.46 -> 0.1.47: exactly the planned members (EXPECT) + ArmoryWishSys
  X   exec     EXECUTED in the JVM: the 9 defaults + clamps + the retired keys still read; bladeText; rot / turn / side / steer / knock; wallAt /
               ahead on a fake grid (ArmoryTrav.GRID seam: flat, wall, step, drop, void, unknown); charge() end to end on plain numbers (the full
               30 blocks at 11 b/s with a client that follows the sent speeds, the turn toward a look 90 degrees off at <= 120 deg/s, the A / D lean
               from a fresh wish and none from a stale one, a mob knocked ahead + to its side once, a boss hit + the stop, a player hit only, line of
               sight, a wall stall, the blocks reasons 2 / 5 / 6 / 7, the timeout, the lag coast); coolLeft / coolSet (+ the prune); wishOf on a
               REAL engine PlayerInput queue (WishMovement / RelativeMovement); startCharge EXECUTED (refusals: cooldown, wall, drop; then the start:
               the RushState, the cost path, the cooldown); tickCharge + finishCharge EXECUTED with no engine (the NEAR / HAND / GRID seams) to the
               end (full length / the hand check); ArmoryWishSys built ordered / unordered + tick(null) quiet; statusText
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration + load): 0.1.47 writes no row, the new keys read
               their defaults, the old gshield.charge.* lines are kept
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): Rush.tickPlayer -> tickCharge and Rush.dash -> startCharge with a real player; the hits / knock
velocities / stuns on real mobs; the client following the per-tick Velocity Set while you steer; the engine queueing WishMovement and ordering
ArmoryWishSys before ProcessPlayerInput (A / D); the bash arc / knockback feel.
"""
import os, sys, json, subprocess, zipfile, re, hashlib, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shield1fin", "arm")]
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.47", "0.1.46"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyarmory_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyarmory_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "armory_0_1_47_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
GSI = "Server/Item/Interactions/Weapons/GreatShield/SkyyArmory/"
BASH_FILES = [GSI + n + ".json" for n in ("SkyyArmory_GreatShield_Bash_Damage", "SkyyArmory_GreatShield_Slam_Damage",
                                          "SkyyArmory_GreatShield_Bash_Selector", "SkyyArmory_GreatShield_Slam_Selector")]
LANG = "Server/Languages/en-US/server.lang"
RELEASE = GSI + "SkyyArmory_GreatShield_Release.json"          # fix round: + the Guard pose held for the charge
NEWKEYS = ["GSR_DIST", "GSR_SPEED", "GSR_TURN", "GSR_LEAN", "GSR_HIT", "GSR_KNOCK", "GSR_SIDE", "GSR_LEDGE", "GSR_CD"]
RETIRED = ["distance", "speed", "hit", "stagger", "shoveHit", "shove", "shoveReach", "shoveWidth"]
EXPECT = {"ArmoryCfg": ["+f " + k for k in NEWKEYS] + ["+m applyGs47", "~<clinit>", "~m apply", "~m bladeText", "~m load", "~m reloadAll", "~m useDefaults"],          # the rows (the kit inlines the defaults)
          "ArmoryHooks": ["~<clinit>"],          # the read-only fixed.gshield.bash row text (arc 120, knockback 22 / 30)
          "Rush": ["+f COOL", "+f WISH_MS", "+f KNOCK_UP", "+f WALL_AHEAD", "+f LAG_S", "+f SIDE_MIN", "+f COOL_MAX", "+f KNOCKS", "+f LEDGES",
                   "+f COOLED", "+f WISHES", "+f ARENAS", "+f HOPS", "+f HOP_TICKS", "+f STEP_LEAD", "+f SYS_WISH", "+f WISH_ORD", "+m stepAt", "+m rot", "+m turn", "+m side", "+m steer", "+m knock",
                   "+m wallAt", "+m ahead", "+m whyEnd", "+m charge", "+m coolLeft", "+m coolSet", "+m wishOf", "+m wish", "+m quit", "+m finishCharge",
                   "+m tickCharge", "+m startCharge", "~<clinit>", "~m clear", "~m tickPlayer", "~m dash", "~m statusText"],
          "RushState": ["+f wx", "+f wz", "+f wishT", "+f lx", "+f lz", "+f seen", "+f turned", "+f leans", "+f knocked", "+f hop", "+f hops"],
          "ArmoryCheck": ["~m packCheck", "~m packOf"],          # the version text
          "SkyyArmoryPlugin": ["~m setup", "~m start", "~m systems"],          # the version text, the 0.1.47 status line, ArmoryWishSys
          "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"],
          "CfgRows2": ["~<clinit>"],
          "ArmoryQuit": ["~m accept"]}          # fix round: a quitter's running charge goes (Rush.quit)          # the kit: the 9 new rows + the default file + the relabelled texts (+ 8 hidden)
if "--expect-dump" in sys.argv:
    EXPECT = {}
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040",
        "migrateP5")


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


PLANNED = sorted(["manifest.json", LANG, RELEASE] + BASH_FILES)
_ORIG_COMPARE = HK.run_compare


def compare_with_assets(out, jar, old_jar, pkg, expect, added, removed=()):
    _ORIG_COMPARE(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    ed = sorted(n for n in ea | eb if n not in ea or n not in eb or za.read(n) != zb.read(n))
    kept = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    if ed == PLANNED:
        d["ok"] += 1
    else:
        kept.append("C: non-class entries changed = the plan: extra %s, missing %s" % (sorted(set(ed) - set(PLANNED))[:6], sorted(set(PLANNED) - set(ed))[:6]))
    d["fails"] = kept
    d["notes"].append("C: non-class entries changed = manifest + lang + the 4 bash / slam files + the release pose (the kit's manifest-only check replaced)")
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = compare_with_assets


# ---------------------------------------------------------------------------------------------------------------- S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyArmory 0.1.47 - build script') and g.count('VERSION = "0.1.47"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count("makeClass(") - o.count("makeClass(")),
         (2, 0, 1), "S one new class (ArmoryWishSys), registered once (ordered + the unordered fallback = 2 calls), no command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq(sorted(nb - na), ["com/skyy/armory/ArmoryWishSys.class"], "S added = ArmoryWishSys only")
    K.eq(sorted(na - nb), [], "S nothing removed")
    nc = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(nc, PLANNED, "S changed non-class = manifest + lang + the 4 bash / slam files + the release (the pose)")
    ra, rb = json.loads(za.read(RELEASE).decode("utf-8")), json.loads(zb.read(RELEASE).decode("utf-8"))
    rb2 = json.loads(json.dumps(rb))
    pose = rb2["Next"].pop("Next", None)
    K.check(rb2 == ra and pose == {"Type": "Simple", "RunTime": 0.5, "Effects": {"ItemAnimationId": "Guard"}} and rb["Next"]["Type"] == "LaunchProjectile",
            "S FIX2 pose: after the release launches the charge, the Guard pose shows a short 0.5 s (a refused charge never locks the bash long); nothing else in the file changed: %s" % pose)
    _acc = g[g.index("public void accept(Object ev) {\n  java.util.UUID u = null;"):]
    _acc = _acc[:_acc.index("\n}")]
    K.check(_acc.count("try {") == 4 and _acc.index("try { @PKG@.Rush.quit(u); }") < _acc.index("try { @PKG@.ArmoryTrav.forgetLand(u); }")
            < _acc.index("try { @PKG@.ArmorySig4.quit(u); }") and _acc.count("catch (Throwable") == 4,
            "S FIX2 quit: ArmoryQuit runs Rush.quit first, each of the 3 quit calls in its own try (one throw never skips another)")
    K.check( "public static void quit(java.util.UUID u) {\n  if (u != null) PEND.remove(u);" in g,
            "S FIX quit: ArmoryQuit (PlayerDisconnectEvent) drops the quitter's running charge")
    _rows = re.findall(r"^    \('gshield\.rush\.\w+', '([^']*)'", g, re.M)
    K.check(len(_rows) == 9 and all(x.startswith("Bulwark Charge ") and len(x) <= 40 for x in _rows)
            and "+ CFG_GS + CFG_GS47 + CFG_SIG4" in g, "S FIX2 rows: all 9 labels start 'Bulwark Charge' (Server Setup search) + sit next to the other great shield rows: %s" % _rows)
    K.check("A drop is too close ahead - Bulwark Charge stops a few blocks before an edge. Nothing spent." in g
            and "ends the charge a few blocks before the edge" in g, "S FIX ledge wording: the chat line + the row say 'a few blocks before the edge'")
    J = lambda z, n: json.loads(z.read(n).decode("utf-8"))
    bad = []
    for n, path, want in ((BASH_FILES[0], ("DamageEffects", "Knockback", "Force"), (16, 22)), (BASH_FILES[1], ("DamageEffects", "Knockback", "Force"), (24, 30))):
        a, b = J(za, n), J(zb, n)
        va, vb = a, b
        for k in path:
            va, vb = va[k], vb[k]
        b2 = json.loads(json.dumps(b))
        x = b2
        for k in path[:-1]:
            x = x[k]
        x[path[-1]] = va
        if (va, vb) != want or b2 != a:
            bad.append((os.path.basename(n), va, vb))
    for n in BASH_FILES[2:]:
        a, b = J(za, n), J(zb, n)
        b2 = json.loads(json.dumps(b))
        ok = (a["Selector"]["Length"], a["Selector"]["YawStartOffset"], b["Selector"]["Length"], b["Selector"]["YawStartOffset"]) == (90, -45, 120, -60)
        b2["Selector"]["Length"], b2["Selector"]["YawStartOffset"] = a["Selector"]["Length"], a["Selector"]["YawStartOffset"]
        if not ok or b2 != a:
            bad.append((os.path.basename(n), a["Selector"], b["Selector"]))
    K.eq(bad, [], "S bash 16 -> 22 + slam 24 -> 30 knockback, both arcs 90 -> 120 (offset -60); nothing else in those 4 files")
    la = za.read(LANG).decode("utf-8").split("\n")
    lb = zb.read(LANG).decode("utf-8").split("\n")
    dl = sorted(set(la) ^ set(lb))
    gsd = [x for x in lb if x.startswith("items.Weapon_GreatShield_") and ".description = " in x]
    K.check(len(la) == len(lb) and len(dl) == 30 and all(x.startswith("items.Weapon_GreatShield_") and ".description = " in x for x in dl)
            and len(gsd) == 15 and all("(wide, heavy knockback)" in x and "steer with the mouse and A / D" in x for x in gsd),
            "S lang: ONLY the 15 great shield descriptions changed (bash wide + heavy, the steerable charge)")
    K.check(all(x.count('<color is="#ffcc00">') == 3 and x.count('<color is="#7ee08a">') == 3 and x.count("</color>") == 6
                and re.match(r'^items\.Weapon_GreatShield_\w+\.description = T\d+ \w+ - Spellblade\. <color is="#ffcc00">Click:</color> shield bash <color is="#7ee08a">[\d.]+</color>', x)
                for x in gsd), "S FIX colours: Style Guide 15 on all 15 descriptions (3 action spans yellow, bash / slam / guard green; the tier tag stays first)")
    K.notes.append("S lang now: %s" % gsd[1])
    items = [n for n in na if n.startswith("Server/Item/Items/Weapon/GreatShield/")]
    K.check(len(items) == 15 and all(za.read(n) == zb.read(n) for n in items), "S the 15 great shield item files byte-identical (vars / Ability1 untouched)")
    rows = [x for x in g.split("\n") if x.startswith("    ('gshield.rush.")]
    K.eq(len(rows), 9, "S 9 new gshield.rush.* rows in the script")
    K.check(all(("    ('gshield.charge.%s'," % k) in g for k in RETIRED) and g.count("RETIRED 0.1.47 (the steerable charge reads gshield.rush.*)") == 8
            and '["gshield.charge." + _k for _k in %r]' % RETIRED in g, "S the 8 old Bulwark rows kept + retired (CFG_HIDDEN; comment marked)")
    K.check('str(_man.get("Name")).split(" ")[-1] in _sg4own' in g, "S FIX: the installed-mods scan skips our own '<version> <mod>' manifest names")
    m = json.loads(zb.read("manifest.json"))
    K.check(m["Version"] == VERSION and "30-block charge you steer" in m["Description"], "S manifest version + description")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray, JObject, JInt, JDouble, JBoolean, JLong, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, Rush, RS, Trav, Leap, WS = (JClass(PKG + n) for n in ("ArmoryCfg", "Rush", "RushState", "ArmoryTrav", "Leap", "ArmoryWishSys"))
    UUID = JClass("java.util.UUID")
    D_ = lambda a: JArray(JDouble)([float(x) for x in a])
    Cfg.useDefaults()
    # ---- the rows
    dflt = dict(GSR_DIST=30.0, GSR_SPEED=11.0, GSR_TURN=120, GSR_LEAN=45, GSR_HIT=0.9, GSR_KNOCK=24.0, GSR_SIDE=16.0, GSR_LEDGE=4, GSR_CD=6.0)
    K.eq(sorted(dflt), sorted(NEWKEYS), "X the harness knows the 9 fields")
    _bash_h, _bash_v = 22 * 2 / math.sqrt(5), 22 / math.sqrt(5)          # the bash's Force 22 on (0, 1, -2): 19.7 level, 9.8 up
    _ch_h = math.hypot(24.0, 16.0)
    K.check(float(Rush.KNOCK_UP) == 10.0 and float(Rush.KNOCK_UP) >= _bash_v and _ch_h * float(Rush.KNOCK_UP) > 1.4 * _bash_h * _bash_v,
            "X FIX2 knock up 10 >= the bash's 9.8: level x up (airtime) %.0f vs the bash %.0f = clearly further" % (_ch_h * float(Rush.KNOCK_UP), _bash_h * _bash_v))
    got = dict((k, int(getattr(Cfg, k)) if isinstance(v, int) else round(float(getattr(Cfg, k)), 6)) for k, v in dflt.items())
    K.eq(got, dflt, "X useDefaults -> applyGs47: the 9 defaults")
    K.eq((bool(Cfg.GS_ON), float(Cfg.GS_MANA), float(Cfg.GS_STAM), float(Cfg.GS_WIDTH), float(Cfg.GS_KD), float(Cfg.GS_DIST)), (True, 4.0, 5.0, 3.0, 1.0, 8.0),
         "X the kept gshield.charge.* rows (enabled / Mana / Stamina / width / knock-down) + a retired one still read (GS_DIST 8, nothing uses it)")
    Pr = JClass("java.util.Properties")
    pp = Pr()
    for k_, v_ in (("gshield.rush.distance", "999"), ("gshield.rush.speed", "1"), ("gshield.rush.turn", "abc"), ("gshield.rush.lean", "-5"),
                   ("gshield.rush.ledge", "0"), ("gshield.rush.cooldown", "61"), ("gshield.rush.knock", "40")):
        pp.setProperty(k_, v_)
    Cfg.applyGs47(pp)
    K.eq((float(Cfg.GSR_DIST), float(Cfg.GSR_SPEED), int(Cfg.GSR_TURN), int(Cfg.GSR_LEAN), int(Cfg.GSR_LEDGE), float(Cfg.GSR_CD), float(Cfg.GSR_KNOCK), float(Cfg.GSR_HIT)),
         (60.0, 5.0, 120, 0, 1, 60.0, 40.0, 0.9), "X applyGs47 clamps like the kit (max / min / bad text = default; a missing key = its default; ledge never 0)")
    Cfg.useDefaults()
    bt = str(Cfg.bladeText())
    K.check("steerable: up to 30 blocks at 11 a second, turns 120 degrees a second toward your aim, A / D lean 45 degrees" in bt and "cooldown 6 s" in bt
            and "drop over 4 blocks" in bt, "X bladeText names the steerable charge: %s" % bt[bt.find("Bulwark"):][:260])
    # ---- pure geometry
    r = [round(float(x), 6) for x in Rush.rot(1.0, 0.0, math.pi / 2)]
    K.eq(r, [0.0, 1.0], "X rot: (1, 0) by +90 degrees = (0, 1)")
    t1 = [round(float(x), 4) for x in Rush.turn(1.0, 0.0, 0.0, 1.0, math.radians(30))]
    t2 = [round(float(x), 4) for x in Rush.turn(1.0, 0.0, 0.0, -1.0, math.radians(30))]
    t3 = [round(float(x), 4) for x in Rush.turn(1.0, 0.0, 1.0, 0.1, math.radians(30))]
    t4 = [round(float(x), 4) for x in Rush.turn(1.0, 0.0, 0.0, 0.0, 1.0)]
    K.eq((t1, t2, t3, t4), ([0.866, 0.5], [0.866, -0.5], [round(1 / math.sqrt(1.01), 4), round(0.1 / math.sqrt(1.01), 4)], [1.0, 0.0]),
         "X turn: at most the step toward the target (both sides), reaches a close target, a zero target = unchanged")
    sd = [int(Rush.side(1.0, 0.0, wx, wz)) for wx, wz in ((0.0, 1.0), (0.0, -1.0), (1.0, 0.0), (-1.0, 0.0), (1.0, 0.2), (1.0, 1.0), (0.0, 0.0))]
    K.eq(sd, [1, -1, 0, 0, 0, 1, 0], "X side: A / D = the cross side; straight ahead / back / a small drift / none = 0")
    st = lambda look, s, dt, tr, ln: [round(float(x), 4) for x in Rush.steer(1.0, 0.0, None if look is None else D_(look), s, dt, tr, ln)]
    K.eq((st([0, 0, 1], 0.0, 1.0 / 30, 120, 45), st([0, 0, 1], 0.0, 1.0, 120, 45), st([1, 0, 0], 1.0, 1.0, 120, 45), st([1, 0, 0], -1.0, 1.0, 120, 45),
          st([0, 0, 1], 0.0, 1.0, 0, 45), st(None, 0.0, 1.0, 120, 45), st([1, 0, 0], 1.0, 1.0, 120, 0), st([0, -1, 0], 0.0, 1.0, 120, 45)),
         ([round(math.cos(math.radians(4)), 4), round(math.sin(math.radians(4)), 4)], [round(math.cos(math.radians(90)), 4), 1.0],
          [round(math.cos(math.radians(45)), 4), round(math.sin(math.radians(45)), 4)], [round(math.cos(math.radians(45)), 4), round(-math.sin(math.radians(45)), 4)],
          [1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [1.0, 0.0]),
         "X steer: 4 deg a 30 TPS tick toward a look 90 off (120 deg/s), the full 90 in a second; A / D lean +-45 of the aim; turn 0 = straight; no look / "
         "lean 0 / straight down = unchanged")
    kn = [[round(float(x), 4) for x in Rush.knock(1.0, 0.0, 0.0, 0.0, mx, mz, 14.0, 10.0)] for mx, mz in ((1.0, 0.5), (1.0, -0.5), (1.0, 0.0))]
    K.eq(kn, [[14.0, 10.0], [14.0, -10.0], [14.0, -10.0]], "X knock: ahead 14 + aside 10 AWAY from your line (an enemy at +z flies to +z; centre = one side)")

    # ---- the blocks ahead on a fake grid (feet y 64; ground y 63)
    @JImplements(PKG + "TravGrid")
    class Grid:
        def __init__(self, fn): self.fn = fn
        @JOverride
        def at(self, x, y, z): return int(self.fn(int(x), int(y), int(z)))
    flat = Grid(lambda x, y, z: 1 if y <= 63 else 0)
    wall = Grid(lambda x, y, z: 1 if (y <= 63 or x == 10) else 0)
    step = Grid(lambda x, y, z: 1 if (y <= 63 or (x == 10 and y == 64)) else 0)
    drop = Grid(lambda x, y, z: 1 if (y <= 63 and x < 12) or (y <= 55) else 0)
    void = Grid(lambda x, y, z: 1 if (y <= 63 and x < 12) else 0)
    unk = Grid(lambda x, y, z: -1 if x >= 12 else (1 if y <= 63 else 0))
    ah = lambda gr, x, v=11.0, ledge=4: int(Rush.ahead(gr, x, 64.0, 0.5, 1.0, 0.0, v, ledge))
    K.eq((ah(flat, 9.5), ah(wall, 9.5), ah(wall, 8.0), ah(step, 9.5), ah(drop, 10.5), ah(drop, 9.0), ah(drop, 7.0), ah(void, 10.5), ah(unk, 10.5), ah(None, 9.5),
          ah(drop, 10.5, ledge=10), ah(drop, 10.5, ledge=8)),
         (0, 2, 0, 0, 5, 5, 0, 5, 5, 0, 0, 5),
         "X ahead: flat 0; a wall 0.7 ahead = 2 (not yet at 2 blocks); a one-block step is no wall; an 8-deep drop 1 block / lag-far (1 + 11 x 0.25) "
         "ahead = 5, not 5 blocks before; void / unknown = 5; no grid = 0; ledge 10 lets the 8-drop pass, 8 does not")
    K.check(bool(Rush.wallAt(wall, 9.5, 64.0, 0.5, 1.0, 0.0, 0.7)) and not bool(Rush.wallAt(flat, 9.5, 64.0, 0.5, 1.0, 0.0, 0.7))
            and bool(Rush.wallAt(Grid(lambda x, y, z: 1 if (y <= 63 or (x == 10 and z == 0 and y == 65)) else 0), 9.5, 64.0, 0.75, 1.0, 0.0, 0.7)),
            "X wallAt: body height, across the body (a block at the shoulder side counts)")
    sa = lambda gr, x, d=0.7: bool(Rush.stepAt(gr, x, 64.0, 0.5, 1.0, 0.0, d))
    K.eq((sa(step, 9.5), sa(step, 8.0), sa(step, 8.0, 2.35), sa(wall, 9.5), sa(flat, 9.5), sa(None, 9.5)), (True, False, True, False, False, False),
         "X stepAt: a one-block step 0.7 ahead / at the lag lead = hop; a 2-high wall / flat / no grid = no")
    K.eq([str(Rush.whyEnd(i)) for i in (1, 2, 3, 4, 5, 6, 7)],
         ["full length", "a wall", "an enemy that does not move", "too long", "a drop ahead", "a locked arena", "the shield left your hand"], "X whyEnd")

    # ---- charge() end to end on plain numbers
    def new_state(far=30.0, v=11.0, now=1000000):
        s = RS()
        s.kind, s.far, s.v, s.hx, s.hz, s.sx, s.sz, s.h = 5, far, v, 1.0, 0.0, 0.0, 0.0, 16.0
        s.until = now + int(round(far / v * 1600.0)) + 1500
        return s
    Obj = JClass("java.lang.Object")

    def run_charge(s, look=None, lag=0, wish=None, mobs_fn=None, blocks_fn=None, freeze_after=None, ticks=400, now0=1000000):
        px, pz, now = 0.0, 0.0, now0
        queue = [(0.0, 0.0)] * lag
        out, n = None, 0
        acts = []
        while n < ticks:
            if wish is not None:
                s.wx, s.wz, s.wishT = wish[0], wish[1], now - wish[2]
            keys, mobs = (mobs_fn(px, pz) if mobs_fn else ([], []))
            ka = JArray(Obj)(keys)
            ma = JArray(JArray(JDouble))([D_(m) for m in mobs])
            blk = blocks_fn(n) if blocks_fn else 0
            out = [float(x) for x in Rush.charge(s, px, 64.0, pz, 1.0 / 30, JLong(now), None if look is None else D_(look), blk, ka, ma)]
            acts.append(out[3:])
            n += 1
            now += 33
            if int(out[0]) != 0:
                break
            queue.append((out[1], out[2]))
            vx, vz = queue.pop(0)
            if freeze_after is None or n < freeze_after:
                px += vx / 30.0
                pz += vz / 30.0
        return s, out, n, px, pz, acts
    s, o, n, px, pz, _a = run_charge(new_state())
    K.check(int(o[0]) == 1 and abs(float(s.sent) - 30.0) < 1e-6 and abs(px - 30.0) < 0.01 and abs(pz) < 1e-9 and 80 <= n <= 86,
            "X charge: the full 30 blocks at 11 b/s straight on (no look), reason 1 (sent %.3f, seen %.3f, %d ticks)" % (float(s.sent), px, n))
    s, o, n, px, pz, _a = run_charge(new_state(), lag=3)
    K.check(int(o[0]) == 1 and abs(float(s.sent) - 30.0) < 1e-6 and 29.7 - 1e-6 <= px <= 30.0 + 1e-6 and n > 84,
            "X charge: with 3 ticks of lag it coasts until seen there (within the 0.3 tolerance: %.3f, %d ticks)" % (px, n))
    s, o, n, px, pz, _a = run_charge(new_state(), look=[0, 0, 1])
    K.check(int(o[0]) == 1 and pz > 10.0 and abs(float(s.hx)) < 1e-6 and abs(float(s.hz) - 1.0) < 1e-6 and abs(float(s.turned) - 90.0) < 0.5,
            "X charge: looking 90 degrees left it turns at <= 120 deg/s, then runs that way (end %.2f / %.2f, turned %.1f)" % (px, pz, float(s.turned)))
    s, o, n, px, pz, _a = run_charge(new_state(), look=[1, 0, 0], wish=(0.0, 1.0, 0))
    K.check(int(o[0]) == 1 and abs(math.degrees(math.atan2(float(s.hz), float(s.hx))) - 45.0) < 0.5 and int(s.leans) == n,
            "X charge: holding the + side key (fresh wish) leans the charge 45 degrees off the aim (heading %.1f deg, %d lean ticks)"
            % (math.degrees(math.atan2(float(s.hz), float(s.hx))), int(s.leans)))
    s, o, n, px, pz, _a = run_charge(new_state(), look=[1, 0, 0], wish=(0.0, 1.0, 400))
    K.check(abs(float(s.hz)) < 1e-9 and int(s.leans) == 0, "X charge: a stale wish (400 ms > WISH_MS) does nothing")
    mobk = [JString("mob"), JString("boss"), JString("pl"), JString("hid")]

    def mobs_at(px, pz):
        return (mobk, [[6.0, 64.0, 0.4, 0.9, 0.4, 1, 1, 0], [20.0, 64.0, 0.0, 1.5, 0.8, 0, 1, 0], [3.0, 64.0, -0.4, 0.9, 0.3, 1, 1, 1], [8.0, 64.0, 0.0, 0.9, 0.4, 1, 0, 0]])
    s, o, n, px, pz, acts = run_charge(new_state(), mobs_fn=mobs_at)
    seen = {}
    for i, a in enumerate(acts):
        for j in range(4):
            if int(a[3 * j]) != 0:
                seen.setdefault(str(mobk[j]), []).append((i, int(a[3 * j]), round(a[3 * j + 1], 3), round(a[3 * j + 2], 3)))
    K.check([x[1:] for x in seen.get("mob", [])] == [(1, 24.0, 16.0)] and [x[1] for x in seen.get("pl", [])] == [3] and "hid" not in seen
            and [x[1] for x in seen.get("boss", [])] == [3] and int(o[0]) == 3 and int(s.hits) == 3 and int(s.knocked) == 1,
            "X charge: the mob hit ONCE + knocked 24 ahead / 16 to its side (FIX: horizontal 28.8 > the bash 22 x 2 / sqrt 5 = 19.7), the player hit only (never pushed), the hidden one (no line of sight) "
            "never, the boss hit + the charge stops (reason 3): %s, end %d at %.2f" % (seen, int(o[0]), px))
    s, o, n, px, pz, _a = run_charge(new_state(), freeze_after=20)
    K.check(int(o[0]) == 2 and 20 + 6 <= n <= 20 + 10, "X charge: stuck against something (seen not moving) = a wall stall after %d ticks (reason 2)" % n)
    for code in (2, 5, 6, 7):
        s, o, n, px, pz, _a = run_charge(new_state(), blocks_fn=lambda i, c=code: c if i == 10 else 0)
        K.check(int(o[0]) == code and n == 11 and float(o[1]) == 0.0, "X charge: blocks reason %d ends it that tick with speed 0" % code)
    s = new_state()
    s.until = 1000000 - 1
    s2, o, n, px, pz, _a = run_charge(s)
    K.check(int(o[0]) == 4 and n == 1, "X charge: past its time = reason 4")
    o0 = [float(x) for x in Rush.charge(None, 0.0, 0.0, 0.0, 0.03, JLong(1), None, 0, None, None)]
    K.eq(o0[0], 4.0, "X charge(null) = ended (4)")
    # ---- the cooldown
    u = UUID.randomUUID()
    Rush.COOL.clear()
    Rush.coolSet(u, JLong(1000), 6.0)
    K.eq((int(Rush.coolLeft(u, JLong(1000))), int(Rush.coolLeft(u, JLong(6999))), int(Rush.coolLeft(u, JLong(7000))), bool(Rush.COOL.containsKey(u))),
         (6000, 1, 0, False), "X coolLeft: 6 s from the start; ready at 7000 ms and the entry goes")
    Rush.coolSet(u, JLong(1000), 0.0)
    K.check(int(Rush.coolLeft(u, JLong(1000))) == 0 and int(Rush.coolLeft(None, JLong(1))) == 0, "X cooldown 0 = none; no player = ready")
    for i in range(300):
        Rush.COOL.put(UUID.randomUUID(), JLong(500))
    Rush.coolSet(u, JLong(1000), 6.0)
    K.check(int(Rush.COOL.size()) == 1 and int(Rush.coolLeft(u, JLong(1000))) == 6000, "X coolSet prunes the expired entries past COOL_MAX (%d left)" % int(Rush.COOL.size()))
    Rush.COOL.clear()
    # ---- the A / D keys on a REAL engine input queue
    PIn = JClass("com.hypixel.hytale.server.core.modules.entity.player.PlayerInput")
    WM = JClass("com.hypixel.hytale.server.core.modules.entity.player.PlayerInput$WishMovement")
    RM = JClass("com.hypixel.hytale.server.core.modules.entity.player.PlayerInput$RelativeMovement")
    pi = PIn()
    K.check(Rush.wishOf(pi.getMovementUpdateQueue()) is None and Rush.wishOf(None) is None, "X wishOf: an empty queue / none = null")
    pi.queue(RM(5.0, 0.0, 5.0))
    pi.queue(WM(0.1, 0.0, 0.2))
    pi.queue(RM(1.0, 0.0, 1.0))
    pi.queue(WM(-0.3, 0.5, 0.4))
    K.eq([round(float(x), 6) for x in Rush.wishOf(pi.getMovementUpdateQueue())], [-0.3, 0.4], "X wishOf: the LAST WishMovement's x / z (other updates skipped)")
    K.eq(int(pi.getMovementUpdateQueue().size()), 4, "X wishOf reads the queue without taking anything out (the engine still applies it)")
    Rush.PEND.clear()
    Rush.wish(None, None, pi)
    Rush.wish(None, None, None)
    K.eq(int(Rush.WISHES), 0, "X wish: no charge running / no player = quiet, nothing recorded")
    # ---- startCharge EXECUTED with no engine (the ArmoryTrav.GRID seam; grounded / cost unreadable = allowed, the kit's rule)
    Trav.GRID = flat
    u2 = UUID.randomUUID()
    Rush.COOL.put(u2, JLong(int(JClass("java.lang.System").currentTimeMillis()) + 60000))
    nowj = int(JClass("java.lang.System").currentTimeMillis())
    Rush.startCharge(None, None, None, None, u2, JClass("org.joml.Vector3d")(5.5, 64.0, 0.5), 1.0, 0.0, JString("Weapon_GreatShield_Iron"), 16.0, JLong(nowj), 3)
    K.check(not bool(Rush.PEND.containsKey(u2)) and "cooldown" in str(Rush.LAST_WHY) and int(Rush.COOLED) == 1, "X startCharge: on cooldown = refused, nothing spent")
    Rush.COOL.clear()
    Trav.GRID = wall
    Rush.startCharge(None, None, None, None, u2, JClass("org.joml.Vector3d")(9.5, 64.0, 0.5), 1.0, 0.0, JString("Weapon_GreatShield_Iron"), 16.0, JLong(nowj), 3)
    w1 = str(Rush.LAST_WHY)
    Trav.GRID = void
    Rush.startCharge(None, None, None, None, u2, JClass("org.joml.Vector3d")(10.5, 64.0, 0.5), 1.0, 0.0, JString("Weapon_GreatShield_Iron"), 16.0, JLong(nowj), 3)
    w2 = str(Rush.LAST_WHY)
    K.check(not bool(Rush.PEND.containsKey(u2)) and w1.startswith("a wall right in front") and w2.startswith("a drop ahead right in front") and not bool(Rush.COOL.containsKey(u2)),
            "X startCharge: a wall / a drop right in front = refused, no cooldown (%s | %s)" % (w1, w2))
    Trav.GRID = flat
    c0 = int(Rush.CHARGES)
    Rush.startCharge(None, None, None, None, u2, JClass("org.joml.Vector3d")(5.5, 64.0, 0.5), 0.0, 1.0, JString("Weapon_GreatShield_Iron"), 16.0, JLong(nowj), 14)
    s = Rush.PEND.get(u2)
    K.check(s is not None and int(s.kind) == 5 and float(s.far) == 30.0 and float(s.v) == 11.0 and float(s.hz) == 1.0 and float(s.h) == 16.0 and float(s.mom) == 14.0
            and int(s.until) == nowj + int(round(30.0 / 11.0 * 1600.0)) + 1500 and int(Rush.CHARGES) == c0 + 1
            and int(Rush.coolLeft(u2, JLong(nowj))) == 6000 and str(s.item) == "Weapon_GreatShield_Iron",
            "X startCharge: the start (the cost path ran - unreadable stats never block), the RushState (30 blocks at 11, H, Momentum), the 6 s cooldown: %s" % str(Rush.LAST_WHY))
    # ---- tickCharge + finishCharge EXECUTED with no engine (NEAR = nobody, HAND = the shield / a sword)
    @JImplements("java.util.function.Function")
    class Nobody:
        @JOverride
        def apply(self, o): return JClass("java.util.ArrayList")()
    Trav.NEAR = Nobody()
    hand = JClass("java.util.HashMap")()
    hand.put(u2, JString("Weapon_GreatShield_Iron"))
    Leap.HAND = hand
    V3 = JClass("org.joml.Vector3d")
    qz = 0.5
    t_ = nowj
    for i in range(200):
        if not Rush.PEND.containsKey(u2):
            break
        Rush.tickCharge(None, None, u2, s, V3(5.5, 64.0, qz), JLong(t_), 1.0 / 30)
        qz = qz + (float(s.lastAsk) if float(s.sent) <= 30.0 else 0.0)
        t_ += 33
    K.check(not bool(Rush.PEND.containsKey(u2)) and int(s.reason) == 1 and "Bulwark Charge" in str(Rush.LAST_HIT) and "(full length)" in str(Rush.LAST_HIT)
            and int(s.hops) == 0, "X tickCharge -> charge -> finishCharge run to the end with no engine (flat: no hop): %s" % str(Rush.LAST_HIT))
    s4 = new_state(now=nowj)
    s4.item = "Weapon_GreatShield_Iron"
    s4.g = step
    s4.hx, s4.hz = 1.0, 0.0
    Rush.PEND.put(u2, s4)
    qx = 5.5
    for i in range(40):
        if not Rush.PEND.containsKey(u2):
            break
        Rush.tickCharge(None, None, u2, s4, V3(qx, 64.0, 0.5), JLong(nowj + 33 * i), 1.0 / 30)
        qx = qx + float(s4.lastAsk)
        if qx > 9.6:
            break
    K.check(int(s4.hops) == 1 and int(Rush.HOPS) == 1 and int(s4.hop) > 0, "X tickCharge: a one-block step ahead = ONE hop (your jump force), then HOP_TICKS before the next (%d hops at x %.2f)" % (int(s4.hops), qx))
    Rush.PEND.clear()
    s3 = new_state(now=nowj)
    s3.item = "Weapon_GreatShield_Iron"
    s3.g = flat
    Rush.PEND.put(u2, s3)
    hand.put(u2, JString("Weapon_Longsword_Iron"))
    p = JClass("org.joml.Vector3d")(5.5, 64.0, 0.5)
    for i in range(20):
        if not Rush.PEND.containsKey(u2):
            break
        Rush.tickCharge(None, None, u2, s3, p, JLong(nowj + 33 * i), 1.0 / 30)
    K.check(not bool(Rush.PEND.containsKey(u2)) and int(s3.reason) == 7 and int(s3.ticks) == 6, "X tickCharge: the shield left your hand = it stops at the 5-tick check (%d)" % int(s3.ticks))
    # FIX heading: the wall / drop look runs again along the heading AFTER this tick's steering (A / D lean, dt 0.1 = 12 degrees toward a drop at z >= 2)
    Rush.PEND.clear()
    hand.put(u2, JString("Weapon_GreatShield_Iron"))
    edge = Grid(lambda x, y, z: 1 if (y <= 63 and z < 2) else 0)
    K.eq(int(Rush.ahead(edge, 5.5, 64.0, 1.5, 1.0, 0.0, 11.0, 4)), 0, "X FIX heading: the old heading (+x along the edge) sees no drop")
    s5 = new_state(now=nowj)
    s5.item, s5.g = "Weapon_GreatShield_Iron", edge
    s5.wx, s5.wz, s5.wishT = 0.0, 1.0, nowj
    Rush.PEND.put(u2, s5)
    l0 = int(Rush.LEDGES)
    Rush.tickCharge(None, None, u2, s5, V3(5.5, 64.0, 1.5), JLong(nowj), 0.1)
    K.check(not bool(Rush.PEND.containsKey(u2)) and int(s5.reason) == 5 and int(s5.ticks) == 1 and float(s5.hz) > 0.2 and abs(float(s5.sent)) < 1e-9
            and int(Rush.LEDGES) == l0 + 1, "X FIX heading: steered toward the edge = it stops THIS tick (reason 5, nothing sent: %.3f, hz %.3f)" % (float(s5.sent), float(s5.hz)))
    s6 = new_state(now=nowj)
    s6.item, s6.g = "Weapon_GreatShield_Iron", flat
    s6.wx, s6.wz, s6.wishT = 0.0, 1.0, nowj
    Rush.PEND.put(u2, s6)
    Rush.tickCharge(None, None, u2, s6, V3(5.5, 64.0, 1.5), JLong(nowj), 0.1)
    K.check(bool(Rush.PEND.containsKey(u2)) and int(s6.reason) == 0 and float(s6.sent) > 0.5, "X FIX heading: the same steer on flat ground keeps going (sent %.3f)" % float(s6.sent))
    # FIX quit: a player who leaves mid-charge loses it; the cooldown stays
    Rush.COOL.put(u2, JLong(nowj + 6000))
    Rush.quit(u2)
    Rush.quit(None)
    K.check(not bool(Rush.PEND.containsKey(u2)) and bool(Rush.COOL.containsKey(u2)), "X FIX quit: Rush.quit drops the running charge, keeps the cooldown, null = quiet")
    Rush.COOL.clear()
    Trav.NEAR = None
    Leap.HAND = None
    Trav.GRID = None
    # ---- ArmoryWishSys
    WS.PPI = JClass("java.lang.Class").forName("com.hypixel.hytale.server.core.modules.entity.player.PlayerSystems$ProcessPlayerInput")
    w_o, w_u = WS(True), WS(False)
    deps = list(w_o.getDependencies())
    K.check(len(deps) == 1 and bool(w_o.ordered) and int(w_u.getDependencies().size()) == 0 and not bool(w_u.ordered) and not bool(w_o.isParallel(1, 1)),
            "X ArmoryWishSys: ordered = one dependency (BEFORE ProcessPlayerInput: %s), the fallback none" % deps)
    WS.PPI = None
    K.check(not bool(WS(True).ordered), "X ArmoryWishSys: no ProcessPlayerInput class = unordered")
    try:
        Rush.PEND.put(u2, new_state())
        w_o.tick(0.03, 0, None, None, None)
        Rush.PEND.clear()
        w_o.tick(0.03, 0, None, None, None)
        K.check(True, "X ArmoryWishSys.tick with no chunk = quiet (charge running or not)")
    except Exception as ex:
        K.check(False, "X ArmoryWishSys.tick threw: %s" % str(ex)[:200])
    Rush.clear()
    K.check(int(Rush.COOL.size()) == 0 and int(Rush.PEND.size()) == 0, "X Rush.clear empties the cooldowns too")
    stx = str(Rush.statusText())
    K.check("Bulwark Charge (0.1.47):" in stx and "A / D samples 0 (key reader off)" in stx, "X statusText: %s" % stx[stx.find("Bulwark Charge (0.1.47)"):][:200])
    K.save()


# ---------------------------------------------------------------------------------------------------------------- D: live
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    fp = os.path.join(home, "config.properties")
    b0 = open(fp, "rb").read()
    K.check(b"gshield.rush." not in b0, "D the live file has none of the new keys (they read their defaults)")
    old_lines = sorted(x for x in b0.decode("latin-1").splitlines() if x.startswith("gshield.charge."))
    hashes = [tree_hash(home)]
    for start in (1, 2):
        rs = [str(getattr(Cfg, m)()) for m in MIGS]
        Cfg.load()
        hashes.append(tree_hash(home))
        if start == 1:
            K.notes.append("D start 1 migrations: %s" % [x[:120] for x in rs if x])
    K.check(hashes[1] == hashes[2], "D start 2 changes nothing")
    t1 = open(fp, "rb").read()
    K.check(b"gshield.rush." not in t1 and b"0.1.47" not in t1 and (b"\r\n" in b0) == (b"\r\n" in t1), "D 0.1.47 writes no row of its own; line endings kept")
    K.eq(sorted(x for x in t1.decode("latin-1").splitlines() if x.startswith("gshield.charge.")), old_lines, "D the old gshield.charge.* lines are kept as they were")
    K.eq((float(Cfg.GSR_DIST), float(Cfg.GSR_SPEED), int(Cfg.GSR_TURN), float(Cfg.GSR_CD), bool(Cfg.GS_ON)), (30.0, 11.0, 120, 6.0, True), "D the new keys read their defaults")
    K.notes.append("D live gshield lines: %s" % old_lines)
    K.notes.append("D files changed by start 1: %s" % sorted(k for k in set(hashes[0]) | set(hashes[1]) if hashes[0].get(k) != hashes[1].get(k))[:8])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ArmoryWishSys"],
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
