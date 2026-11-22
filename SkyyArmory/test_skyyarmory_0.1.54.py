"""Harness for SkyyArmory 0.1.54 (round sig4: Loophole Lance on The Loophole; the 7 base family signatures of 0.1.46 re-checked;
tools/armory_0_1_54_patch.py). Build first:
    python tools/armory_0_1_54_patch.py && python SkyyArmory/build_skyyarmory_0.1.54.py
    python SkyyArmory/test_skyyarmory_0.1.54.py [--keep] [--expect-dump]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S    static   the patch re-runs to identical bytes, line endings kept; no new class / system / command, 12 new methods; the jar vs 0.1.53:
                nothing added or removed, the only changed non-class entry = manifest.json (every item / interaction / lang byte-equal - Loophole
                Lance rides on The Loophole's 0.1.46 staff root); lance() hits through ArmoryTrav.hit (MINE-marked: never charges a meter)
  X    exec     EXECUTED in the JVM: the 4 rows (defaults, clamps, the default file text); lanceItem / lanceAsk / lanceCast (The Loophole only;
                every other staff incl. Doomcaller + The Stormfossil and every other family id = no); lanceBase (Iron 175, x tune.staff, part.tune
                off, not a staff = 0); wallStop on a stand-in TravGrid (open air = 24, a wall, a floor below, max, no grid / no aim = 0); linePick
                (on the line, past the end, behind, too near, the width edge, a wide body, not-ok, the eye-to-centre drop, an unnormalised aim, a
                steep aim, len 0); armory:fn:sig for The Loophole (row-driven line <= 70 at the rows' widest, switches off -> Arcane Overload /
                ready false) and every other id of the 7 families unchanged; nm; lancePending (no double fire); the lance job (one pulse, at
                once, then over); lance() itself with no engine (the wall stop, the counters, no target = 0; no aim = nothing); step / run /
                marker with no engine (quiet); the shared target rule TravMath.who (PvP off = players never hit); the charge numbers (20 quick /
                10 charged hits, unchanged); statusText; SkyyGear 0.3.59 GearSigX.sigOf through the bridge (when its jar is present)
  B/X4x-5x      the 0.1.46 / 0.1.47 / 0.1.48 / 0.1.50 / 0.1.51 harnesses' exec phases on the 0.1.53 jar (baseline) AND on the 0.1.54 jar: no
                check may fail on 0.1.54 that passes on 0.1.53, except the ONE planned change (0.1.46's family answers: The Loophole now
                answers Loophole Lance); X53 = the 0.1.53 exec whole. (0.1.52's exec reads the 0.1.51 jar, no longer on disk - its fist set is
                byte-equal in 0.1.54, phase S.)
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.53 -> 0.1.54: exactly the planned members (EXPECT)
  D    live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration + load): 0.1.54 writes nothing; start 2 = start 1;
                the 4 new keys read their defaults
  AA   audit    the engine-access audit
  sig4fix  S also proves statically: the lance's hits take SkyyGear 0.3.59's charged-shot path (PROJECTILE cause -> launch record ->
                weaponHit2: levels + Damage % incl. The Loophole's utfx dmg-30, no second cut in lanceBase); every sig.*.enabled row is
                live,part,danger; the sig.lance.enabled help names its sig.staff.enabled dependency.
Not executed here (UNVERIFIED until the game): the lance on real mobs (ArmoryTrav.hit through the damage pipeline + SkyyGear's levels and
The Loophole's -30 % trade-off - proven by reading only), the real world grid stopping the bolt, the bolt / impact look in the client.
"""
import os, sys, json, subprocess, zipfile, importlib.util, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sig4", "arm")]
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.54", "0.1.53"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyarmory_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyarmory_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "armory_0_1_54_patch.py")
GEAR_JAR = os.path.join(ROOT, "SkyyGear", "SkyyGear-0.3.59.jar")          # the SET pin
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
LH = "Weapon_Staff_UT_Loophole"
LANCE_KEYS = {"sig.lance.enabled": "true", "sig.lance.range": "24", "sig.lance.damage": "1.5", "sig.lance.width": "1.2"}

_ORIG_COMPARE = HK.run_compare
_argv = list(sys.argv)
OLDH = {}
OLD_EXEC = ("46", "47", "48", "50", "51")          # 0.1.52's exec needs the 0.1.51 jar (gone; its fist set is byte-equal here - S); 0.1.53's runs whole below
for _v in OLD_EXEC + ("53",):
    _s = importlib.util.spec_from_file_location("test_skyyarmory_0_1_%s" % _v, os.path.join(HERE, "test_skyyarmory_0.1.%s.py" % _v))
    _m = importlib.util.module_from_spec(_s)
    _s.loader.exec_module(_m)
    sys.argv[:] = _argv
    _m.JAR = JAR
    _m.SCRATCH = SCRATCH
    OLDH[_v] = _m
HK.run_compare = _ORIG_COMPARE          # the old harnesses swap in their own asset compares; 0.1.54 changes no asset (the kit's manifest-only check)
MIGS = OLDH["53"].MIGS

EXPECT = {
    # the version text (as every Armory round)
    "SkyyArmoryPlugin": ["~m setup", "~m start"], "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults",
                                                                 "+f LANCE_ON", "+f LANCE_R", "+f LANCE_DMG", "+f LANCE_W", "+m applyLance", "~m apply", "~<clinit>"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header", "~<clinit>"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"], "CfgFile": ["~<clinit>"],
    "ArmoryCheck": ["~m packCheck", "~m packOf"],
    # 0.1.54: Loophole Lance
    "Sig4Job": ["+f lance", "+f aim"],
    "ArmorySig4": ["+f LANCE_ID", "+f LANCE_NAME", "+f LANCE_STEP", "+f LANCE_NEAR", "+f LN_CASTS", "+f LN_LINES", "+f LN_HITS", "+f LN_LEN",
                   "+m lanceItem", "+m lanceAsk", "+m lanceCast", "+m lanceBase", "+m wallStop", "+m linePick", "+m lanceText", "+m lanceAnswer",
                   "+m nm", "+m lancePending", "+m lance", "~m answer", "~m miss", "~m step", "~m marker", "~m statusText", "~<clinit>"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


# ---------------------------------------------------------------------------------------------------------------- S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyArmory 0.1.54 - build script') and g.count('VERSION = "0.1.54"') == 1 and 'VERSION = "0.1.53"' not in g, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count("makeClass(") - o.count("makeClass("),
          g.count("\nM(") - o.count("\nM(")), (0, 0, 0, 12), "S no new system / command / class; 12 new methods")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S nothing added, nothing removed")
    nc = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(nc, ["manifest.json"], "S changed non-class = manifest only (every item / interaction / lang byte-identical - no asset for the lance)")
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    K.check(mb["Version"] == VERSION and dict(ma, Version=VERSION, Name=ma["Name"].replace(OLD, VERSION)) == mb, "S manifest: only the Version changed")
    it = json.loads(zb.read([n for n in nb if n.endswith("/%s.json" % LH)][0]).decode("utf-8"))
    K.eq(it["Interactions"].get("Ability1"), "SkyyArmory_Sig_ArcaneOverload", "S The Loophole keeps the 0.1.46 staff root (the lance is decided server side)")
    body = g[g.index("public static int lance(@PKG@.Sig4Job j"):]
    body = body[:body.index('}""")')]
    K.check("@PKG@.ArmoryTrav.hit(buf, rs[k], me, null, amt)" in body and "Monk.hit" not in body and "Rico.add" not in body and "ArmorySig2.cands(" in body,
            "S lance(): hits through ArmoryTrav.hit (MINE-marked, never charges), never adds charge itself, targets through the shared cands() rule")
    K.check(g.count('LANCE_ID = "Weapon_Staff_UT_Loophole"') == 1 and "lanceItem(id) && famOf(id) == 0" in g, "S one id, and only in the staff family")
    # ---- fix round sig4fix
    # F2 (critic: The Loophole's -30 % trade-off): the lance's damage takes the same SkyyGear path as The Loophole's own charged shot.
    # ArmoryTrav.hit = Damage(EntitySource(caster), PROJECTILE) -> SkyyGear 0.3.59 GearHitSys: Projectile family -> the shooter's launch record
    # (the staff) -> GearHit.weaponHit2 (levels + Damage %, which carries the held UT's utfx "dmg-30"); no extra cut in lanceBase (no double cut)
    th = g[g.index("public static boolean hit(@CB@ buf, @REF@ target, @REF@ caster, @REF@ proj, double amount)"):]
    th = th[:th.index('}""")')]
    K.check("@DCS@ cause = @DCS@.PROJECTILE;" in th and "new @DENT@(caster)" in th and "MINE.put(d, Boolean.TRUE)" in th,
            "S F2 ArmoryTrav.hit: PROJECTILE cause through EntitySource(caster), MINE-marked")
    lb = g[g.index("public static double lanceBase(String item)"):]
    lb = lb[:lb.index('}""")')]
    K.check("utfx" not in lb and "dmg" not in lb, "S F2 lanceBase applies no UT cut of its own (SkyyGear's Damage % does it once)")
    gp = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.59.py")
    if os.path.isfile(gp):
        gg = open(gp, encoding="utf8", newline="").read()
        gs = gg[gg.index("boolean proj = @PKG@.GearHit.family(d.getCause()) == 2;"):]
        gs = gs[:gs.index("info = @PKG@.GearHit.weaponHit2(d, u, pr, main, shot, srec, rec, arm, vnpc);") + 10]
        K.check("GearShotTrack.pickFor(u, pa" in gs and "main = nr.main;" in gs and "shot = true;" in gs,
                "S F2 SkyyGear 0.3.59 GearHitSys: a Projectile-family hit through a plain EntitySource takes the shooter's launch record (the staff) into weaponHit2")
        wh = gg[gg.index("public static Object[] weaponHit2(@DMG@ d"):]
        wh = wh[:wh.index('}""")')]
        K.check("family(d.getCause()) <= 0" in wh and "hitAmount((double) a0, t, spell, chg, r1, r2)" in wh and "GearStats.totals(u, main, arm, ok, true)" in wh,
                "S F2 weaponHit2: Projectile family passes; Damage % from the held weapon's totals (incl. utfx dmg) applies")
    else:
        K.check(True, "S F2 SkyyGear 0.3.59 script not on disk - skipped")
    # F3 / engine note: the lance row is flagged like every other sig.*.enabled row and its help names the Staff-signature dependency
    rows = re.findall(r"\('(sig\.[a-z0-9]+\.enabled)', '[^']*', [^,]+, 'bool', 'true', '', '', '', '', '([a-z,]+)'", g)
    K.check(len(rows) >= 15 and all(f == "live,part,danger" for _k, f in rows) and ("sig.lance.enabled", "live,part,danger") in rows,
            "S F3 sig.lance.enabled flagged live,part,danger like all %d sig.*.enabled rows" % len(rows))
    ln = g[g.index("('sig.lance.enabled'"):]
    ln = ln[:ln.index("\n")]
    K.check("Needs the Staff signature on." in ln and "Needs sig.staff.enabled on." in ln, "S F-note sig.lance.enabled help + file comment name the sig.staff.enabled dependency")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- X: executed
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray, JObject, JDouble, JBoolean, JLong, JImplements, JOverride
    K = HK.Child(out)
    cp = [B.SERVER_JAR, B.JAVASSIST, jar] + ([GEAR_JAR] if os.path.isfile(GEAR_JAR) else [])
    HK.jvm(cp, verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, Defs, S2, S4, Job, Fn, TW, TM = (JClass(PKG + n) for n in ("ArmoryCfg", "ArmoryDefs", "ArmorySig2", "ArmorySig4", "Sig4Job", "ArmorySigFn", "TravWorld", "TravMath"))
    UUID = JClass("java.util.UUID")
    Vec = JClass("org.joml.Vector3d")
    D_ = lambda a: JArray(JDouble)([float(x) for x in a])
    B_ = lambda a: JArray(JBoolean)([bool(x) for x in a])
    Cfg.useDefaults()
    # ---- the rows
    K.eq((bool(Cfg.LANCE_ON), float(Cfg.LANCE_R), float(Cfg.LANCE_DMG), float(Cfg.LANCE_W)), (True, 24.0, 1.5, 1.2), "X useDefaults -> applyLance: the 4 defaults")
    dc = str(Cfg.DEF_CFG)
    K.eq([k for k, v in LANCE_KEYS.items() if ("\n%s=%s\n" % (k, v)) not in dc], [], "X the default config.properties text carries the 4 new keys at their defaults")
    Pr = JClass("java.util.Properties")
    pp = Pr()
    for k_, v_ in (("sig.lance.range", "99"), ("sig.lance.damage", "0.01"), ("sig.lance.width", "abc"), ("sig.lance.enabled", "off")):
        pp.setProperty(k_, v_)
    Cfg.applyLance(pp)
    K.eq((bool(Cfg.LANCE_ON), float(Cfg.LANCE_R), float(Cfg.LANCE_DMG), float(Cfg.LANCE_W)), (False, 48.0, 0.1, 1.2),
         "X applyLance clamps like the kit (max / min / bad text = default)")
    Cfg.applyLance(Pr())
    K.eq((bool(Cfg.LANCE_ON), float(Cfg.LANCE_R), float(Cfg.LANCE_DMG), float(Cfg.LANCE_W)), (True, 24.0, 1.5, 1.2), "X a missing key = its default (no migration)")
    Cfg.useDefaults()
    # ---- who
    ids = [str(x) for x in S4.ID]
    others = [i for i in ids if i != LH]
    K.check(LH in ids and int(S4.famOf(JString(LH))) == 0, "X The Loophole is in the staff family (the 0.1.46 root)")
    K.eq([bool(S4.lanceItem(JString(i))) for i in (LH, "Weapon_Staff_Iron", "Weapon_Staff_UT_Doomcaller", "Weapon_Staff_UT_Stormfossil", "")] + [bool(S4.lanceItem(None))],
         [True, False, False, False, False, False], "X lanceItem: The Loophole only")
    K.eq([i for i in others if bool(S4.lanceAsk(JString(i))) or bool(S4.lanceCast(int(S4.famOf(JString(i))), JString(i)))], [],
         "X lanceAsk / lanceCast: no other item of the 7 families (%d ids: 16 staffs, souls, spears, axes, clubs, longswords, great shields)" % len(others))
    K.eq([bool(S4.lanceAsk(JString(i))) for i in ("Weapon_Staff_UT_Doomcaller", "Weapon_Staff_UT_Stormfossil", "Weapon_Wand_UT_SecondOpinion", "Weapon_Bo_UT_Turnstile",
                                                  "Weapon_Sword_UT_Paperweight", "Weapon_Wand_Iron", "Hepta_Axe")],
         [False] * 7, "X lanceAsk: the other Untiered staffs / weapons and non-family ids never")
    K.eq([bool(S4.lanceCast(f, JString(LH))) for f in range(7)], [True] + [False] * 6, "X lanceCast: only the staff root's marker (family 0)")
    Cfg.LANCE_ON = False
    K.eq((bool(S4.lanceAsk(JString(LH))), bool(S4.lanceCast(0, JString(LH)))), (False, False), "X sig.lance.enabled off: The Loophole casts the plain Arcane Overload")
    Cfg.useDefaults()
    # ---- the numbers
    si = int(Defs.staffIndex(JString(LH)))
    K.eq((si, int(Defs.staffIndex(JString("Weapon_Staff_Iron"))), int(Defs.S_CD[si])), (2, 2, 175), "X The Loophole = the Iron staff's index; its charged shot 175 (before levels)")
    K.eq(float(S4.lanceBase(JString(LH))), 175.0, "X lanceBase: the Iron charged shot")
    Cfg.TUNE_S[si] = 150.0
    tuned = float(S4.lanceBase(JString(LH)))
    Cfg.PART_TUNE = False
    untuned = float(S4.lanceBase(JString(LH)))
    Cfg.useDefaults()
    K.eq((tuned, untuned), (262.5, 175.0), "X lanceBase x tune.staff.Iron 150 %; part.tune off = the plain number")
    K.eq([float(S4.lanceBase(JString(i))) for i in ("Weapon_Sword_Iron", "Nope")] + [float(S4.lanceBase(None))], [0.0, 0.0, 0.0], "X lanceBase: not a staff = 0 (refused + charge back)")
    K.eq(round(175.0 * float(Cfg.LANCE_DMG), 4), 262.5, "X each enemy on the line takes 175 x 1.5 = 262.5 before levels (Arcane Overload on one target: 3 x 35 x 2 = 210)")

    # ---- the wall stop on a stand-in grid
    @JImplements(PKG + "TravGrid")
    class Grid(object):
        def __init__(self, solid):
            self.solid = solid

        @JOverride
        def at(self, x, y, z):
            return 1 if self.solid(int(x), int(y), int(z)) else 0
    air = Grid(lambda x, y, z: False)
    wall = Grid(lambda x, y, z: x == 10)
    floor = Grid(lambda x, y, z: y < 64)
    ws = lambda g, d, mx: round(float(S4.wallStop(g, 0.5, 65.62, 0.5, D_(d), mx)), 4)
    K.eq([ws(air, [1, 0, 0], 24.0), ws(wall, [1, 0, 0], 24.0), ws(wall, [-1, 0, 0], 24.0), ws(air, [1, 0, 0], 4.0), ws(air, [1, 0, 0], 3.9),
          ws(floor, [0, -1, 0], 24.0), ws(None, [1, 0, 0], 24.0), round(float(S4.wallStop(air, 0.5, 65.62, 0.5, None, 24.0)), 4), ws(air, [1, 0, 0], 0.0)],
         [24.0, 9.25, 24.0, 4.0, 3.9, 1.5, 0.0, 0.0, 0.0],
         "X wallStop: open air = the reach, a wall 9.5 ahead stops it at 9.25, behind you nothing, the max, a floor 1.62 below stops a downward bolt, no grid / aim / reach = 0")
    # ---- the line pick (eye 0,1.62,0 looking +x; body centres; widths)
    lp = lambda xs, ys, zs, wsd, ok, d, ln, w: [bool(b) for b in S4.linePick(D_(xs), D_(ys), D_(zs), D_(wsd), B_(ok), 0.0, 1.62, 0.0, D_(d), ln, w)]
    K.eq(lp([5, 23.5, 25, -3, 0.2, 10, 10, 10, 10, 12], [1.62, 1.62, 1.62, 1.62, 1.62, 1.62, 1.62, 0.9, 1.62, 1.62], [0, 0, 0, 0, 0, 0.9, 0.95, 0, 0, 2.5],
            [0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 4.0], [1, 1, 1, 1, 1, 1, 1, 1, 0, 1], [1, 0, 0], 24.0, 1.2),
         [True, True, False, False, False, True, False, True, False, True],
         "X linePick: on the line in; 23.5 in; 25 past the end out; behind out; 0.2 too near out; 0.9 aside in (0.3 + 0.6), 0.95 out; a body centre "
         "0.72 below the eye in; not-ok out; a 4-wide body 2.5 aside in")
    K.eq(lp([5, 5], [1.62, 1.62], [0, 0.85], [0.6, 0.6], [1, 1], [2, 0, 0], 24.0, 1.2), [True, True], "X linePick: an unnormalised aim = the same line")
    K.eq(lp([3, 3], [1.62 - 3, 1.62], [0, 0], [0.6, 0.6], [1, 1], [0.7071, -0.7071, 0], 24.0, 1.2), [True, False],
         "X linePick: a 45-degree downward aim hits the body on its line (3 ahead, 3 down), not one 3 ahead at eye height (2.12 off it)")
    K.eq(lp([2.1, 6], [-0.5, 1.62], [0, 0], [0.6, 0.6], [1, 1], [0.7071, -0.7071, 0], 24.0, 1.2), [True, False], "X linePick: the 45-degree line hits what lies on it")
    K.eq((lp([5], [1.62], [0], [0.6], [1], [1, 0, 0], 0.0, 1.2), lp([5], [1.62], [0], [0.6], [1], [0, 0, 0], 24.0, 1.2), lp([5], [1.62], [0], [0.6], [1], [1, 0, 0], 4.0, 1.2)),
         ([False], [False], [False]), "X linePick: len 0 / no aim / stopped by a wall before it = nothing")
    # ---- armory:fn:sig
    f = Fn()

    def ask(i):
        a = JArray(JObject)(1)
        a[0] = JString(i)
        r_ = f.apply(a)
        return None if r_ is None else (str(r_[0]), str(r_[1]), int(r_[2]), str(r_[3]), bool(r_[4]), ["java.lang.String" if isinstance(r_[k], str) else str(r_[k].getClass().getName()) for k in range(5)])
    T5 = ["java.lang.String", "java.lang.String", "java.lang.Integer", "java.lang.String", "java.lang.Boolean"]
    want = ("Loophole Lance", "One piercing bolt flies 24 blocks: 1.5x your charged shot to each.", 20, "quick hit +1~, charged hit +2", True, T5)
    K.eq(ask(LH), want, "X armory:fn:sig: The Loophole = Loophole Lance (plain java.lang types; the spec's tooltip line)")
    names = [str(x) for x in S4.NAMES]
    fami = [int(x) for x in S4.FAMI]
    wrong = [(i, ask(i)[0]) for k, i in enumerate(ids) if i != LH and (ask(i) is None or ask(i)[0] != names[fami[k]])]
    K.eq(wrong, [], "X every other item of the 7 families still answers its family signature (%d)" % len(others))
    K.eq([ask(i)[0] for i in ("Weapon_Staff_Iron", "Weapon_Staff_UT_Doomcaller", "Weapon_Staff_UT_Stormfossil", "Weapon_Wand_UT_SecondOpinion", "Weapon_Bo_UT_Turnstile",
                             "Weapon_Wand_Iron", "Weapon_Bo_Iron")] + [ask("Weapon_Sword_Iron")],
         ["Arcane Overload", "Arcane Overload", "Arcane Overload", "Second Opinion", "Revolving Door", "Ricochet", "Whirling Staff", None],
         "X other staffs keep Arcane Overload; the sig2 / sig3 answers unchanged; not ours = null")
    Cfg.LANCE_R, Cfg.LANCE_DMG = 31.0, 2.25
    live = ask(LH)[1]
    Cfg.LANCE_R, Cfg.LANCE_DMG = 47.75, 4.75
    widest = ask(LH)[1]
    Cfg.useDefaults()
    K.check(live == "One piercing bolt flies 31 blocks: 2.25x your charged shot to each." and len(widest) <= 70,
            "X the line follows the live rows; the widest fits 70 characters (%d: %s)" % (len(widest), widest))
    Cfg.LANCE_ON = False
    off = ask(LH)
    Cfg.useDefaults()
    Cfg.SG4_ST_ON = False
    st_off = ask(LH)
    Cfg.useDefaults()
    K.check(off[0] == "Arcane Overload" and off[4] and st_off[0] == "Loophole Lance" and not st_off[4],
            "X sig.lance.enabled off -> Arcane Overload; the staff signature off -> ready false (SkyyGear shows none): %s / %s" % (off[0], st_off))
    # ---- the job + no double fire
    u, u2 = UUID.randomUUID(), UUID.randomUUID()
    jl = Job(0, u, JString(LH), 175.0, 1.5, 1, JLong(0), D_([1, 0, 0]), JLong(1000))
    jl.lance = True
    jl.aim = D_([1, 0, 0])
    jo = Job(3, u, JString("Weapon_Axe_Iron"), 10.0, 0.8, 3, JLong(250), D_([1, 0, 0]), JLong(1000))
    K.eq([str(S4.nm(jl)), str(S4.nm(jo)), str(S4.nm(Job(0, u, JString("Weapon_Staff_Iron"), 1.0, 2.0, 1, JLong(250), D_([1, 0, 0]), JLong(1)))), str(S4.nm(None))],
         ["Loophole Lance", "Cleave", "Arcane Overload", ""], "X nm: the lance job is named Loophole Lance (miss / timeout lines)")
    K.eq([int(S4.due(jl, JLong(t))) for t in (999, 1000)], [0, 1], "X the lance job pulses at once (gap 0)")
    S4.stepped(jl, JLong(1000))
    K.eq((int(jl.left), int(S4.due(jl, JLong(1000)))), (0, -1), "X ... once, then it is over (one bolt per cast)")
    st = JClass("java.lang.Object")()
    tw = TW.get(st)
    jp = Job(0, u, JString(LH), 175.0, 1.5, 1, JLong(0), D_([1, 0, 0]), JLong(1000))
    jp.lance = True
    tw.sig4.add(jo)
    K.check(not bool(S4.lancePending(tw, u)), "X lancePending: another family's job of the same player = no")
    tw.sig4.add(jp)
    K.eq((bool(S4.lancePending(tw, u)), bool(S4.lancePending(tw, u2)), bool(S4.lancePending(None, u)), bool(S4.lancePending(tw, None))), (True, False, False, False),
         "X lancePending: a queued lance of this player refuses a 2nd cast (no double fire); another player / no world = no")
    jp.left = 0
    K.check(not bool(S4.lancePending(tw, u)), "X ... a fired lance (left 0) no longer blocks")
    # ---- lance() executed with no engine: the wall stop + counters run; no candidates = 0 hits
    ln0, hit0 = int(S4.LN_LINES), int(S4.LN_HITS)
    p = Vec(0.5, 64.0, 0.5)
    jx = Job(0, u, JString(LH), 175.0, 1.5, 1, JLong(0), D_([1, 0, 0]), JLong(1))
    jx.lance = True
    jx.aim = D_([1, 0, 0])
    try:
        g1 = int(S4.lance(jx, None, None, p, False, wall))
        l1 = round(float(S4.LN_LEN), 4)
        g2 = int(S4.lance(jx, None, None, p, False, air))
        l2 = round(float(S4.LN_LEN), 4)
        g3 = int(S4.lance(jx, None, None, p, False, None))
        jx.aim = None
        g4 = int(S4.lance(jx, None, None, p, False, air))
        K.eq((g1, l1, g2, l2, g3, g4, int(S4.LN_LINES) - ln0, int(S4.LN_HITS) - hit0), (0, 9.25, 0, 24.0, 0, 0, 3, 0),
             "X lance() runs with no engine: the wall stops the bolt at 9.25, open air 24, no grid = 0 (nothing hit, no throw); no aim = nothing drawn")
    except Exception as ex:
        K.check(False, "X lance() with no engine threw: %s" % str(ex)[:300])
    # ---- the glue with no engine: quiet
    try:
        S4.marker(None, None, 13005, None, None)
        K.eq(str(S4.LAST_WHY), "no caster", "X marker (staff code) with no engine: quiet")
        tw.sig4.clear()
        jr = Job(0, u, JString(LH), 175.0, 1.5, 1, JLong(0), D_([1, 0, 0]), JLong(5000))
        jr.lance = True
        tw.sig4.add(jr)
        K.check(not bool(tw.idle()), "X TravWorld.idle() sees a queued lance")
        S4.run(tw, None, None, JLong(5000))
        K.eq((int(tw.sig4.size()), str(S4.LAST_WHY), bool(S4.OVER.containsKey(u))), (0, "the caster left this world", False),
             "X run -> step: a due lance whose caster is gone is dropped; it never touches the Arcane Overload watch (OVER)")
        TW.ALL.remove(st)
    except Exception as ex:
        K.check(False, "X the glue edges threw: %s" % str(ex)[:300])
    # ---- the shared target rule (ArmorySig2.cands -> ArmoryTrav.kind -> TravMath.who) + the charge numbers
    K.eq([int(TM.who(a, b, c, d)) for a, b, c, d in ((True, False, True, True), (False, True, True, True), (False, False, False, True), (False, False, True, True),
                                                       (False, False, True, False))],
         [2, 2, 1, 0, 1], "X who: you / an ally never; a player only where PvP is on (+ trav.players) - the lance's target rule")

    def to_full(amt):
        cur, n = 0.0, 0
        while n < 1000:
            v = float(S2.fill(cur, 20.0, amt))
            if v < 0:
                break
            cur, n = v, n + 1
        return n
    K.eq((to_full(float(S4.staffAmt(3001, 1.0))), to_full(float(S4.staffAmt(4001, 1.0))), int(Defs.SIG_MAX)), (20, 10, 20),
         "X the charge (unchanged, The Loophole = every staff): meter 20, 20 quick hits / 10 charged hits (sig.ut 0 in SkyyGear)")
    sx = str(S4.statusText())
    K.check("Loophole Lance on (casts " in sx, "X statusText names the lance: %s" % sx[:300])
    K.notes.append("X status line: %s" % sx)
    # ---- SkyyGear 0.3.59 (the SET pin) reads it
    try:
        br.put("armory:fn:sig", f)
        GX = JClass("com.skyy.gear.GearSigX")
        ga = GX.sigOf(JString(LH))
        gi = GX.sigOf(JString("Weapon_Staff_Iron"))
        K.eq((str(ga[0]), str(ga[1]), int(ga[2]), str(gi[0])), ("Loophole Lance", want[1], 20, "Arcane Overload"),
             "X SkyyGear 0.3.59 GearSigX.sigOf takes Loophole Lance through armory:fn:sig (no Gear change)")
        br.remove("armory:fn:sig")
    except Exception as ex:
        K.notes.append("X SkyyGear GearSigX not run (%s)" % str(ex)[:200])
    K.save()


# ---------------------------------------------------------------------------------------------------------------- B / X4x: the older exec phases
# Each older harness's exec phase runs TWICE: on the 0.1.53 jar (B<v>, the baseline - checks written for an older jar that later rounds
# already changed fail there too) and on the 0.1.54 jar (X<v>). X<v> fails on any check that fails on 0.1.54 but not on 0.1.53, except the ONE
# planned change (0.1.46's family-answer check: The Loophole now answers Loophole Lance).
PLANNED = {"46": [("X armory:fn:sig: every item of the 7 families answers its signature",
                   "('%s', ('Loophole Lance', 'One piercing bolt flies 24 blocks: 1.5x your charged shot to each.'" % LH)]}


def _raw(scratch, tag, v):
    return os.path.join(scratch, "%s%s.raw.json" % (tag, v))


def base_phase(v):
    def f(out, jar, scratch, home):
        raw = _raw(scratch, "base", v)
        try:
            OLDH[v].run_exec(raw, OLD_JAR, scratch, home)
        finally:
            ok = os.path.isfile(raw)
            d = json.load(open(raw)) if ok else {"ok": 0, "fails": []}
            json.dump({"ok": 1 if ok else 0, "fails": [] if ok else ["B%s: the 0.1.53 baseline wrote no result" % v],
                       "notes": ["B%s: the 0.1.%s exec on the 0.1.53 jar: %d ok, %d pre-existing fail(s)%s" % (v, v, d["ok"], len(d["fails"]),
                                 (" (checks later rounds changed: %s)" % [x[:110] for x in d["fails"]]) if d["fails"] else "")]}, open(out, "w"), indent=1)
    return f


def cmp_phase(v):
    def f(out, jar, scratch, home):
        raw = _raw(scratch, "exec", v)
        try:
            OLDH[v].run_exec(raw, jar, scratch, home)
        finally:
            b = json.load(open(_raw(scratch, "base", v))) if os.path.isfile(_raw(scratch, "base", v)) else None
            n = json.load(open(raw)) if os.path.isfile(raw) else None
            if b is None or n is None:
                json.dump({"ok": 0, "fails": ["X%s: no result (baseline %s, new %s)" % (v, b is not None, n is not None)], "notes": []}, open(out, "w"), indent=1)
            else:
                plan = PLANNED.get(v, [])
                hit = [x for x in n["fails"] if x not in b["fails"] and any(x.startswith(pf) and x.count("('Weapon_") == 1 and needle in x for pf, needle in plan)]
                new = [x for x in n["fails"] if x not in b["fails"] and x not in hit]
                notes = ["X%s: the 0.1.%s exec on the 0.1.54 jar: %d ok, %d fail(s) = %d also on 0.1.53 + %d planned (Loophole Lance) + %d new" % (
                    v, v, n["ok"], len(n["fails"]), len([x for x in n["fails"] if x in b["fails"]]), len(hit), len(new))]
                fl = list(new)
                if len(hit) != len(plan):
                    fl.append("X%s: expected exactly %d planned difference(s), got %d" % (v, len(plan), len(hit)))
                json.dump({"ok": n["ok"] + len(hit), "fails": fl, "notes": notes + n.get("notes", [])[:2]}, open(out, "w"), indent=1)
    return f


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
    hashes = [HK.tree_hash(home)]
    for start in (1, 2):
        rs = [str(getattr(Cfg, m)()) for m in MIGS]
        Cfg.load()
        hashes.append(HK.tree_hash(home))
        if start == 1:
            K.notes.append("D start 1 migrations: %s" % [x[:120] for x in rs if x])
    K.check(hashes[1] == hashes[2], "D start 2 changes nothing")
    K.check(hashes[0] == hashes[1], "D start 1 changes nothing either (0.1.54 has no migration; new keys read their defaults)")
    t1 = open(fp, "rb").read()
    K.check(b"0.1.54" not in t1 and (b"\r\n" in b0) == (b"\r\n" in t1), "D 0.1.54 writes nothing of its own; line endings kept")
    K.check(not [k for k in LANCE_KEYS if (k + "=").encode() in b0], "D the live file has none of the new keys")
    K.eq((bool(Cfg.LANCE_ON), float(Cfg.LANCE_R), float(Cfg.LANCE_DMG), float(Cfg.LANCE_W), bool(Cfg.SG4_ST_ON)), (True, 24.0, 1.5, 1.2, True),
         "D after the live load: the lance rows at their defaults, the staff signature on")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec", run_exec)] + [(t + v, (base_phase if t == "base" else cmp_phase)(v)) for v in OLD_EXEC for t in ("base", "exec")]
           + [("exec53", OLDH["53"].run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
