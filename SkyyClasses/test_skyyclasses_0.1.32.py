"""Harness for SkyyClasses 0.1.32 (Arcane Breach = a flying crescent of light, 5 s cooldown, 1.4x; class:fn:stacks; the one-time numbers
update; tools/classes_0_1_32_patch.py; round sb01). Build first:
    python tools/classes_0_1_32_patch.py && python SkyyClasses/build_skyyclasses_0.1.32.py
    python SkyyClasses/test_skyyclasses_0.1.32.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/sb01/cls):
  A   verify   every class loads + initialises
  C   compare  0.1.31 -> 0.1.32: exactly the planned members (EXPECT), + AbilStacksFn; every 0.1.31 bridge key still put, one new
  X   exec     on the engine stand-ins of test_skyyclasses_0.1.25.py (its N0 set-up is executed from that file: a map-backed Store /
               CommandBuffer, the REAL EntityStatMap, real Damage objects, the REAL AbilTick + AbilWorld):
               X1 the numbers + every ability's cooldown; X2 THE FLIGHT (the swing animation, a moving crescent: step by step, each enemy
               hit ONCE as it passes, 1.4x, Breach, knockback along the flight, nothing beyond 6.5 blocks / to the side / behind, the end:
               +3 Momentum + one counted use); X3 A WALL stops it (enemies behind it untouched; a 1-high step does not); X4 the level
               scaling (Lv 10 = +18 %); X5 sprint / crouch / air shapes; X6 the caster leaves = the flight ends; X7 class:fn:stacks (the
               Spellblade's Momentum + Rolling / Unstoppable with their seconds, the Monk combo, Blood Frenzy, none, unknown player)
  MIG the one-time update on scratch files (the live test world's config COPY: History first, one Undo line, INFO, runs once, load()
      reads the new numbers; hand-edited kept; marker present; chain 0.1.10 -> 0.1.29 -> 0.1.32; a fresh default file is never rewritten
      and holds every ability's cooldown)
  ST1 / ST2  START TWICE on a scratch COPY of the live Skyy_SkyyClasses folder (setup's order: migrations, load, CfgPub): start 1 writes only
      the update (config.properties + its History version + the change log), start 2 writes nothing; the live folder is only read
  AA  engine-access audit
"""
import os, sys, json, shutil, zipfile, hashlib, textwrap, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import deploy_set as DS

VERSION, OLD = "0.1.32", "0.1.31"
JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.join(TOOLS, "dev", "scratch", "sb01", "cls")
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyClasses")
T25 = os.path.join(HERE, "test_skyyclasses_0.1.25.py")
ADDED = ["AbilStacksFn"]
EXPECT = {
    "Abil": ["+f ANIMS", "+f ARCS", "+f ARC_ANIM", "+f ARC_ANIM_SET", "+f ARC_HITS", "+f ARC_WALLS", "+f FX_ARC", "+f FX_ARC_HIT", "+f FX_ARC_WALL",
             "+f FX_ARC_WING", "+f SOLID", "+f SOLID_FAIL", "+m arcAnim", "+m arcCast", "+m arcClear", "+m arcFly", "+m arcFx", "+m arcHits", "+m arcSolid",
             "~<clinit>", "~m breachCast", "~m runJob5"],
    "AbilNum": ["+f AB_KNOCK", "+f AB_SPEED", "+f AB_WIDTH", "-f AB_ANGLE", "~<clinit>", "~m sync"],
    "AbilCfg": ["~<clinit>", "~m read"],                        # the numbers row default text
    "ClassCfg": ["+f MG32_KEY", "+f MG32_MARK", "+f MG32_MARK_ID", "+f MG32_NEW", "+f MG32_OLD", "+f MG32_WHO", "+f MG32_WHY",
                 "+m migrate0132", "~<clinit>"],
    "CfgRows2": ["~<clinit>"],                                  # the config kit's row table (the numbers row default)
    "AbilDefs": ["~<clinit>"],                                  # the one-line description
    "AbilDoes": ["~m does"],                                    # what it does (class:fn:abilDoes)
    "SkyyClassesPlugin": ["~m setup", "~m shutdown"],           # migrate0132 + class:fn:stacks (and the version text)
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"],          # the version text only
}


def live_text():
    f = os.path.join(LIVE, "config.properties")
    return open(f, "rb").read().decode("latin-1") if os.path.isfile(f) else None


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


# ================================================================================================================== X: exec
def run_exec(out, jar, scratch, _home):
    # the 0.1.25 harness's engine stand-ins (its run_exec from "import jpype" to the X1 section), executed here with our jar; Assets.zip is
    # only READ (its Server/Entity/Stats entries are copied into a scratch zip first)
    stats_zip = os.path.join(scratch, "stats.zip")
    with zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")) as zi, \
            zipfile.ZipFile(stats_zip, "w") as zo:
        for n in zi.namelist():
            if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
                zo.writestr(n, zi.read(n))
    lines = open(T25, encoding="utf8").read().split("\n")
    a = lines.index("def run_exec(out, jar, scratch, _home):") + 1
    b = [i for i, l in enumerate(lines) if l.strip() == "# ---------------- X1 the pure rules"][0]
    ns = {"out": out, "jar": jar, "scratch": scratch, "_home": _home, "HK": HK, "B": B, "PKG": PKG, "ASSETS": stats_zip, "os": os, "sys": sys,
          "json": json, "shutil": shutil, "zipfile": zipfile, "time": time, "__name__": "t25setup"}
    exec(compile(textwrap.dedent("\n".join(lines[a:b])), T25 + " (N0 set-up)", "exec"), ns)
    g = lambda n: ns[n]
    K, C, ck, JClass = g("K"), g("C"), g("ck"), __import__("jpype").JClass
    from jpype import JArray, JDouble, JLong, JString, JObject, JFloat, JImplements, JOverride
    A, AS, AD, AW, Defs, Cfg = g("A"), g("AS"), g("AD"), g("AW"), g("Defs"), g("Cfg")
    AN, AC, ACX = C("AbilNum"), C("AbilCfg"), C("AbilCtx")
    tst, tbuf, world, TBf = g("tst"), g("tbuf"), g("world"), g("TBf")
    player, npc, setclass, put = g("player"), g("npc"), g("setclass"), g("put")
    LEVEL, HANDS, NEARL, br, Fn, Bool = g("LEVEL"), g("HANDS"), g("NEARL"), g("br"), g("Fn"), g("Bool")
    said, unthrottle, MANA, STAM, HP = g("said"), g("unthrottle"), g("MANA"), g("STAM"), g("HP")
    ArrayList, UUID = g("ArrayList"), g("UUID")
    now_ms = lambda: int(time.time() * 1000)
    tick = C("AbilTick")()
    aw = AW.of("abil-test")
    EFX, PUSH, PSEEN, ANIMS = ArrayList(), ArrayList(), ArrayList(), ArrayList()
    A.EFFECTS = EFX
    A.EFFECT = Fn(lambda o: Bool.valueOf(not str(list(o)[1]).startswith("?")))
    A.PUSHES = PUSH
    A.PSEEN = PSEEN
    A.ANIMS = ANIMS
    LOOKV = {"v": [120.5, 65.6, 0.5, 0.0, 0.0, 1.0]}
    A.LOOK = Fn(lambda o: JArray(JDouble)(LOOKV["v"]))
    WALL = {"f": None}
    A.SOLID = Fn(lambda o: Bool.valueOf(bool(WALL["f"] and WALL["f"](float(o[0]), float(o[1]), float(o[2])))))
    NAMES_ = [str(x) for x in Defs.NAMES]
    ID = dict((str(AD.IDS[i]), i) for i in range(len(AD.IDS)))
    BRc = ID["ArcaneBreach"]
    AMt = C("AbilMath")

    def setp(k__, kv):
        AS.set(k__, JArray(JString)(list(kv.keys())), JArray(JString)([None if v is None else str(v) for v in kv.values()]))

    def lv(n):
        return int(AMt.levelStart(n, 4.5, 1.5))

    def uses(k_, id_):
        v_ = AS.load(k_).getProperty("u." + id_)
        return 0 if v_ is None else int(str(v_))

    def amts():
        return [round(float(e[1].getAmount()), 3) for e in TBf.EVENTS]

    def hitrefs():
        return [e[0] for e in TBf.EVENTS]

    def mob(i, x, z, y=64.0):
        return npc(i, x, y, z, hp=200.0)

    def jobs27():
        return [j for j in aw.jobs if int(j.kind) == 27]

    def step(ms_since_cast):
        """one world tick with the crescent's clock at ms_since_cast after its cast"""
        t_ = now_ms()
        for j_ in jobs27():
            j_.start = JLong(t_ - ms_since_cast)
            j_.at = JLong(t_ - 5)
        aw.lastNs = 0
        tick.tick(JFloat(0.05), 0, None, tst, tbuf)

    ci_s = NAMES_.index("Spellblade")
    su, sr, spr, sm, spl, smsc = player(90, 120.5, 64.0, 0.5, "Blade32")
    setclass(su, "Spellblade")
    LEVEL[(str(su), str(Defs.SKILLS[ci_s]))] = 30
    HANDS[90] = "Weapon_Longsword_Crude"
    SK = str(su)

    def sreset():
        AS.clearCd(SK)
        sm.setStatValue(MANA, JFloat(400.0))
        sm.setStatValue(STAM, JFloat(50.0))
        unthrottle()
        said()
        AS.LASTUSE.clear()
        setp(SK, {"u.ArcaneBreach": None})
        for l_ in (EFX, PUSH, PSEEN, ANIMS, TBf.EVENTS):
            l_.clear()
        for mp_ in (AS.MOMS, AS.MOMX, AS.IMBUE, AS.BREACH, AS.MARKD):
            mp_.clear()
        aw.jobs.clear()
        aw.zones.clear()
        aw.nz = 0
        WALL["f"] = None
        LOOKV["v"] = [120.5, 65.6, 0.5, 0.0, 0.0, 1.0]
        ms_ = smsc.getMovementStates()
        ms_.onGround, ms_.crouching, ms_.sprinting = True, False, False

    def fcast(slot, sh):
        unthrottle()
        return str(A.castAt(spr, tst, sr, world, slot, sh, 3))

    # ---------------- X1 the numbers + the cooldowns
    AN.sync()
    ck([float(AN.AB_CD), float(AN.AB_RANGE), float(AN.AB_POWER), float(AN.AB_SPEED), float(AN.AB_WIDTH), float(AN.AB_KNOCK)] == [5.0, 6.5, 1.4, 15.0, 8.0, 2.0],
       "X1: Arcane Breach cooldown 5, flies 6.5 blocks at 15 a second, 8 wide, 1.4x, knock 2")
    ck([int(AD.cdMs(BRc, k_)) for k_ in range(4)] == [5000, 5000, 7000, 5000], "X1: the shapes' cooldowns follow the 5 s row (walk 5, sprint 5, air 7, crouch 5): %s"
       % [int(AD.cdMs(BRc, k_)) for k_ in range(4)])
    pas = [str(AD.IDS[i]) for i in range(len(AD.IDS)) if bool(AD.PASSIVE[i])]
    zero = [str(AD.IDS[i]) for i in range(len(AD.IDS)) if not bool(AD.PASSIVE[i]) and int(AD.cdMs(i, 0)) <= 0]
    ck(not zero and pas == ["GuardianSpirit"], "X1: every ability has its own cooldown (none 0): %s" % zero)
    old_nums = str(AC.AB_NUMS)
    AC.AB_NUMS = "cooldown=9"
    AN.sync()
    ck(int(AD.cdMs(BRc, 0)) == 9000 and float(AN.AB_RANGE) == 6.5, "X1: the cooldown key is read live from Server Setup (9 s), a missing key = its default")
    AC.AB_NUMS = "range=99,width=50,speed=1"
    AN.sync()
    ck([float(AN.AB_RANGE), float(AN.AB_WIDTH), float(AN.AB_SPEED)] == [20.0, 12.0, 5.0], "X1 (fix 4): the arc rows are clamped (range <= 20, width <= 12, speed 5..40)")
    AC.AB_NUMS = "speed=500"
    AN.sync()
    ck(float(AN.AB_SPEED) == 40.0, "X1 (fix 4): speed at most 40")
    AC.AB_NUMS = old_nums
    AN.sync()

    # ---------------- X2 THE FLIGHT
    sreset()
    m1, m2, m3 = mob(901, 120.5, 2.5), mob(902, 123.5, 5.5), mob(903, 120.5, 6.5)
    far, side, back = mob(904, 120.5, 9.5), mob(905, 126.5, 3.0), mob(906, 120.5, -2.0)
    NEARL[:] = [m1, m2, m3, far, side, back]
    A.momAdd(su, 2, now_ms())
    r_ = fcast("1", 0)
    ck(r_.startswith("ok:ArcaneBreach") and " flies=6.5" in r_ and " speed=15" in r_ and " width=8" in r_ and " hit=35" in r_ and " breach=17" in r_,
       "X2: the cast: a crescent 6.5 blocks at 15 a second, 8 wide, 1.4 H (35), Breach 15 + 2 Momentum: %s" % r_)
    ck([str(x) for x in ANIMS] == ["Longsword/SwingLeftCharged"], "X2: the cast plays the longsword's big horizontal slash: %s" % list(ANIMS))
    ck(len(jobs27()) == 1 and amts() == [] and AS.BREACH.get(m1) is None, "X2: a crescent in flight (kind 27), nothing hit yet")
    j = jobs27()[0]
    ck(abs(float(j.y) - 65.1) < 1e-9 and [float(j.dx), float(j.dy), float(j.dz)] == [0.0, 0.0, 1.0], "X2: it starts at chest height and flies where you look")
    step(100)   # 1.5 blocks
    ck(amts() == [35.0] and AS.BREACH.get(m1) is not None and AS.BREACH.get(m2) is None, "X2: 0.1 s: 1.5 blocks - the first enemy (2 blocks) is hit: %s" % amts())
    ck(len(jobs27()) == 1 and abs(float(jobs27()[0].from_) - 1.5) < 0.2, "X2: still flying, 1.5 blocks out")
    n_fx = sum(1 for x in PSEEN if str(x) in ("Sword_Charged_Trail_Blade", "Mace_Signature_Slash"))
    ck(n_fx == 7, "X2: the crescent is drawn every step (7 light points: the centre + 6 wing slashes): %d" % n_fx)
    step(250)   # 3.75 blocks: nobody new, the first enemy is not hit again
    ck(amts() == [35.0], "X2: 0.25 s: nothing new, the first enemy is NOT hit twice: %s" % amts())
    step(400)   # 6.0 blocks: the two at 5 and 6 blocks
    ck(sorted(amts()) == [35.0, 35.0, 35.0] and AS.BREACH.get(m2) is not None and AS.BREACH.get(m3) is not None,
       "X2: 0.4 s: 6 blocks - the one 3 blocks to the side (inside the 8-wide crescent) and the one 6 blocks out: %s" % amts())
    ck(int(A.momN(su, now_ms())) == 2 and uses(SK, "ArcaneBreach") == 0, "X2: no Momentum / use before the flight ends")
    step(500)   # 7.5 -> capped at 6.5: the end
    ck(len(jobs27()) == 0 and sorted(amts()) == [35.0, 35.0, 35.0], "X2: 0.5 s: 6.5 blocks - the flight ends; three hits in all (each enemy ONCE)")
    ck(AS.BREACH.get(far) is None and AS.BREACH.get(side) is None and AS.BREACH.get(back) is None and not [r for r in hitrefs() if r in (far, side, back)],
       "X2: nothing 9 blocks out, 6 blocks to the side or behind you is touched")
    ck(abs(float(A.breachPct(m1, now_ms())) - 17.0) < 1e-9, "X2: Breached = +17 %% damage taken from everyone (15 + 2 Momentum)")
    pu = [[round(float(v), 3) for v in p] for p in PUSH]
    ck(pu == [[0.0, 1.0, 4.0]] * 3, "X2: each one is knocked back 2 blocks along the flight (speed 2 x 2, a little up): %s" % pu)
    ck(int(A.momN(su, now_ms())) == 5 and uses(SK, "ArcaneBreach") == 1, "X2: the end: +3 Momentum, one counted use")
    sd = said()
    ck([x for x in sd if "Arcane Breach: 3 enemies Breached" in x], "X2: the line: %s" % sd)
    ck(str(A.LAST_SB).startswith("breach arc 0 flew=6.5 hit=3 breached=3"), "X2: %s" % A.LAST_SB)
    # aimed up: the crescent follows the look, its climb clamped to 30 degrees
    sreset()
    LOOKV["v"] = [120.5, 65.6, 0.5, 0.0, 0.8, 0.6]
    fcast("1", 0)
    j = jobs27()[0]
    ck(abs(float(j.dy) / (float(j.dz) ** 2 + float(j.dx) ** 2) ** 0.5 - 0.57735) < 1e-4, "X2: aimed steeply up -> it climbs at most 30 degrees")
    step(500)
    sreset()

    # ---------------- X3 A WALL
    sreset()
    w1, w2 = mob(911, 120.5, 2.5), mob(912, 120.5, 5.5)
    NEARL[:] = [w1, w2]
    WALL["f"] = lambda x, y, z: 3.0 <= z < 4.0          # a wall 2.5 blocks ahead (every height)
    fcast("1", 0)
    step(600)   # in one step: the whole 6.5 blocks - the wall cuts it at 2.5
    ck(len(jobs27()) == 0 and amts() == [35.0] and AS.BREACH.get(w1) is not None and AS.BREACH.get(w2) is None,
       "X3: a wall stops the crescent - the enemy before it is hit, the one behind it is not: %s" % amts())
    ck(" wall" in str(A.LAST_SB) and "flew=2.5" in str(A.LAST_SB) and "Impact_Sword_Signature" in [str(x) for x in PSEEN], "X3: %s" % A.LAST_SB)
    sd = said()
    ck([x for x in sd if "(the arc hit a wall)" in x], "X3: the line says so: %s" % sd)
    sreset()
    NEARL[:] = [w1, w2]
    WALL["f"] = lambda x, y, z: 3.0 <= z < 4.0 and y < 65.0      # a 1-high step: the crescent (chest height) passes over it
    fcast("1", 0)
    step(600)
    ck(sorted(amts()) == [35.0, 35.0], "X3: a 1-block step does not stop it (both hit): %s" % amts())
    sreset()
    c1, c2, c3 = mob(913, 120.5, 2.5), mob(914, 123.5, 3.5), mob(915, 117.5, 3.5)
    NEARL[:] = [c1, c2, c3]
    WALL["f"] = lambda x, y, z: 122.0 <= x < 123.0          # a side wall between the centre line and the right wing
    fcast("1", 0)
    step(600)
    ck(sorted(amts()) == [35.0, 35.0] and AS.BREACH.get(c2) is None and AS.BREACH.get(c1) is not None and AS.BREACH.get(c3) is not None,
       "X3 (fix 1): a mob behind a SIDE wall (in the wing's reach) is not hit; the centre one and the open-side one are: %s" % amts())
    sreset()

    # ---------------- X4 the level scaling (1.4x x the ability level multiplier)
    sreset()
    l1 = mob(921, 120.5, 2.5)
    NEARL[:] = [l1]
    setp(SK, {"u.ArcaneBreach": lv(10)})
    r_ = fcast("1", 0)
    step(600)
    ck(amts() == [41.3] and " hit=41.3" in r_, "X4: Lv 10 = +18 %% -> 1.4 x 25 x 1.18 = 41.3 a hit: %s %s" % (amts(), r_))
    setp(SK, {"u.ArcaneBreach": None})
    sreset()

    # ---------------- X5 the other shapes
    sreset()
    s1 = mob(931, 120.5, 2.5)
    NEARL[:] = [s1]
    r_ = fcast("1", 1)
    ck(" flies=6.5" in r_ and " secs=7" in r_ and len(PUSH) == 1, "X5: Breaching Charge (sprint) - a 2-block step, then the crescent, Breach 7 s: %s" % r_)
    step(600)
    ck(amts() == [35.0] and len(PUSH) == 2, "X5: ... its crescent hits + knocks back")
    sreset()
    s4 = mob(932, 119.5, -1.5)
    NEARL[:] = [s1, s4]
    setp(SK, {"p1": "ElementalImbue", "p2": "Sunder", "a1": "ArcaneBreach", "a2": "RiftCleave"})
    r_ = fcast("3", 3)
    setp(SK, {"p1": None, "p2": None, "a1": None, "a2": None})
    for j_ in list(aw.jobs):
        j_.at = JLong(now_ms() - 10)
    aw.lastNs = 0
    tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(" breach=20" in r_ and amts() == [] and AS.BREACH.get(s4) is not None and not jobs27() and not ANIMS,
       "X5: Marked Ground (crouch) is unchanged - no damage, every side (the one behind too), no crescent: %s %s %s %s %s" % (r_, amts(), AS.BREACH.get(s4), len(jobs27()), list(ANIMS)))
    sreset()
    NEARL[:] = [s1, s4]
    smsc.getMovementStates().onGround = False
    r_ = fcast("1", 2)
    smsc.getMovementStates().onGround = True
    for _i in range(3):
        for j_ in list(aw.jobs):
            j_.at = JLong(now_ms() - 10)
        aw.lastNs = 0
        tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(" land" in r_ and str(A.LAST_LAND).startswith("breach:2") and sorted(amts()) == [25.0, 25.0] and not jobs27(),
       "X5: Breach from Above (air) is unchanged - on landing, the 4-block circle, 1.0 H: %s %s" % (A.LAST_LAND, amts()))
    sreset()

    # ---------------- X6 the caster switches profile mid-flight: the crescent stops (nothing hit, nothing counted)
    sreset()
    q1 = mob(941, 120.5, 4.5)
    NEARL[:] = [q1]
    fcast("1", 0)
    jobs27()[0].pkey = "someone-else"
    step(600)
    ck(not jobs27() and amts() == [] and str(A.LAST_SB) == "breach arc gone hit=0", "X6: the caster's profile changed = the crescent ends: %s" % A.LAST_SB)
    sreset()
    q2, q3 = mob(942, 120.5, 2.5), mob(943, 120.5, 5.5)
    NEARL[:] = [q2, q3]
    fcast("1", 0)
    step(100)
    ebu = g("ebu")
    ebu.remove(su)          # the caster logs out (or dies) with one hit dealt
    step(600)
    ebu.put(su, sr)
    ck(not jobs27() and amts() == [35.0] and str(A.LAST_SB) == "breach arc gone hit=1 counted" and int(A.momN(su, now_ms())) == 3 and uses(SK, "ArcaneBreach") == 1,
       "X6 (fix 3): the caster gone mid-flight - the hit already dealt still gives +3 Momentum + the counted use: %s" % A.LAST_SB)
    sreset()
    NEARL[:] = [q2, q3]
    fcast("1", 0)
    step(100)
    jobs27()[0].pkey = "someone-else"
    step(600)
    ck(str(A.LAST_SB) == "breach arc gone hit=1 switched" and int(A.momN(su, now_ms())) == 0, "X6 (fix 3): ... a switched profile gets nothing: %s" % A.LAST_SB)
    sreset()

    # ---------------- X7 class:fn:stacks
    SF = C("AbilStacksFn")
    rows = lambda u_, t_: [str(x) for x in SF.rows(u_, JLong(t_))]
    col = lambda n_: str(Defs.COLORS[NAMES_.index(n_)])
    sreset()
    t0 = now_ms()
    ck(rows(su, t0) == ["Momentum|0|20|0.0|" + col("Spellblade")], "X7: a Spellblade always has its Momentum row (0): %s" % rows(su, t0))
    A.momAdd(su, 9, t0)
    ck(rows(su, t0 + 500) == ["Momentum|9|20|3.5|" + col("Spellblade"), "Rolling|1|1|3.5|#9fe8ee"],
       "X7: 9 Momentum - the next falls off in 3.5 s; Rolling (7+) holds 3.5 s: %s" % rows(su, t0 + 500))
    A.momAdd(su, 6, t0 + 1000)
    ck(rows(su, t0 + 1500) == ["Momentum|15|20|2.5|" + col("Spellblade"), "Unstoppable|1|1|2.5|#ffc800"],
       "X7: 15 - Unstoppable (14+) holds until the 2nd stack falls off (2.5 s): %s" % rows(su, t0 + 1500))
    ck(rows(su, t0 + 4100) == ["Momentum|6|20|0.9|" + col("Spellblade")], "X7: after the first 9 fell off: 6 left, no tier row: %s" % rows(su, t0 + 4100))
    fn = SF()
    got = fn.apply(JArray(JObject)([su]))
    ck(got is not None and len(list(got)) >= 1 and str(list(got)[0]).startswith("Momentum|"), "X7: apply(Object[]{UUID}) -> String[]: %s" % (got and list(got)))
    ck(fn.apply(JArray(JObject)([UUID.randomUUID()])) is None and fn.apply(None) is None and fn.apply(JArray(JObject)([JString("x")])) is None,
       "X7: an unknown player / junk -> null")
    ku, kr, kpr, km, kpl, kmsc = player(91, 140.5, 64.0, 0.5, "Monk32")
    bu, bref, bpr, bm, bpl, bmsc = player(92, 150.5, 64.0, 0.5, "Ber32")
    wu, wr, wpr, wm, wpl, wmsc = player(93, 160.5, 64.0, 0.5, "War32")
    setclass(ku, "Monk")
    setclass(bu, "Berserker")
    setclass(wu, "Warrior")
    ck(rows(ku, t0) == [] and rows(bu, t0) == [] and rows(wu, t0) == [], "X7: a Monk without the aura / a Berserker without the frenzy / a Warrior: no rows")
    AZ = C("AbilZone")
    fz = AZ(8, ku, 140.5, 64.0, 0.5, 5.0, JLong(t0), JLong(t0 + 30000))
    fz.ring = JArray(JLong)([t0] * 5 + [0] * 15)
    fz.ai = int(AD.FFORM)
    fz.pkey = str(Cfg.pkey(ku))
    AS.FLOWS.put(ku, fz)
    ck(rows(ku, t0 + 1000) == ["Combo|5|20|4.0|" + col("Monk")], "X7: Flowing Form running: Combo 5 of 20, the next falls off in 4 s: %s" % rows(ku, t0 + 1000))
    fz.ai = int(AD.HFISTS)
    ck(rows(ku, t0 + 1000)[0].startswith("Hundred Fists|5|20|"), "X7: Hundred Fists names itself")
    fz.ended = True
    ck(rows(ku, t0 + 1000) == [], "X7: the aura ended = no row")
    bz = AZ(17, bu, 150.5, 64.0, 0.5, 1.0, JLong(t0), JLong(t0 + 86400000))
    bz.ring = JArray(JLong)([t0] * 3 + [0] * 22)
    bz.pkey = str(Cfg.pkey(bu))
    AS.FRENZ.put(bu, bz)
    ck(rows(bu, t0 + 1000) == ["Blood Frenzy|3|25|5.0|" + col("Berserker")], "X7: Blood Frenzy on: 3 of 25, 5 s left on the next: %s" % rows(bu, t0 + 1000))
    bz.pkey = "another-profile"
    ck(rows(bu, t0 + 1000) == [], "X7: a zone of another profile is not shown")
    AS.FLOWS.remove(ku)
    AS.FRENZ.remove(bu)
    tt = time.perf_counter()
    for _i in range(2000):
        fn.apply(JArray(JObject)([su]))
    per = (time.perf_counter() - tt) / 2000.0 * 1000.0
    ck(per < 1.0, "X7: cheap enough for a 250 ms poll (%.3f ms a call through jpype)" % per)
    sreset()
    K.save()


# ================================================================================================================== MIG
def run_mig(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Cfg, AC, AN, AD = JClass(PKG + "ClassCfg"), JClass(PKG + "AbilCfg"), JClass(PKG + "AbilNum"), JClass(PKG + "AbilDefs")
    Paths = JClass("java.nio.file.Paths")
    MARK, MID, WHO = str(Cfg.MG32_MARK), str(Cfg.MG32_MARK_ID), str(Cfg.MG32_WHO)
    KEY = "ab.ArcaneBreach.numbers"
    OLDV, NEWV = str(Cfg.MG32_OLD[0]), str(Cfg.MG32_NEW[0])
    K.check([str(x) for x in Cfg.MG32_KEY] == [KEY] and "cooldown=16," in OLDV and "angle=90," in OLDV and "cooldown=5,range=6.5,speed=15,width=8,knock=2,power=1.4," in NEWV
            and "angle" not in NEWV and WHO == "SkyyClasses 0.1.32" and "=" not in MARK and MID in MARK, "MIG: the 0.1.32 table + marker")
    sample = ("# SkyyClasses config\nswitchCost=5000\nab.HuntersNet.numbers=mana=6\n%s=%s\nab.ElementalImbue.numbers=mana=7\n" % (KEY, OLDV))

    def upd(text):
        r = Cfg.mgUpdateT(text, Cfg.MG32_KEY, Cfg.MG32_OLD, Cfg.MG32_NEW, Cfg.MG32_WHY, Cfg.MG32_MARK, Cfg.MG32_MARK_ID, "0.1.32")
        return None if r is None else [str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]]]
    lt = live_text()
    base = lt if (lt is not None and ("\n%s=%s" % (KEY, OLDV)) in lt.replace("\r\n", "\n")) else sample
    for tag, t in (("LF", base.replace("\r\n", "\n")), ("CRLF", base.replace("\r\n", "\n").replace("\n", "\r\n"))):
        r = upd(t)
        nl = "\r\n" if tag == "CRLF" else "\n"
        want = t.replace(nl + KEY + "=" + OLDV + nl, nl + MARK + nl + KEY + "=" + NEWV + nl, 1)
        K.check(r is not None and r[0] == want and want != t, "MIG %s: an untouched row -> the 0.1.32 numbers, the marker right above it, every other byte kept" % tag)
        K.check(r is not None and r[3] == [KEY, OLDV, NEWV] and r[2] == [] and r[1].startswith(KEY + " " + OLDV + " -> " + NEWV), "MIG %s: the change row" % tag)
    t = sample.replace(KEY + "=" + OLDV, KEY + "=" + OLDV.replace("power=1.2", "power=2"))
    r = upd(t)
    K.check(r is not None and r[3] == [] and r[1] == "" and len(r[2]) == 1 and "kept (custom)" in r[2][0] and r[0] == t.replace("\n" + KEY, "\n" + MARK + "\n" + KEY, 1),
            "MIG: a hand-edited row is kept (marker only) and noted: %s" % (r and r[2]))
    t = "\n".join(l for l in sample.split("\n") if not l.startswith(KEY))
    r = upd(t)
    K.check(r is not None and r[0] == MARK + "\n" + t and r[3] == [] and r[2] == [], "MIG: no row (the default = the new numbers): only the marker, on top")
    K.check(upd(MARK + "\n" + sample) is None, "MIG: the marker in a comment line = nothing to do (runs once)")
    K.check(upd(str(Cfg.MG29_MARK) + "\n" + sample) is not None and Cfg.mgUpdateT(MARK + "\n" + sample, Cfg.MG29_KEY, Cfg.MG29_OLD, Cfg.MG29_NEW, Cfg.MG29_WHY,
            Cfg.MG29_MARK, Cfg.MG29_MARK_ID, "0.1.29") is not None, "MIG: the 0.1.29 / 0.1.32 markers never stand for each other")
    mroot = os.path.join(scratch, "mig")

    def setup(name, text=None, copy_live=False):
        home = os.path.join(mroot, name, "Skyy_SkyyClasses")
        os.makedirs(home)
        if copy_live:
            for f_ in ("config.properties", "config-changes.log"):
                if os.path.isfile(os.path.join(LIVE, f_)):
                    shutil.copy(os.path.join(LIVE, f_), os.path.join(home, f_))
            if os.path.isdir(os.path.join(LIVE, "config-history")):
                shutil.copytree(os.path.join(LIVE, "config-history"), os.path.join(home, "config-history"))
        f = os.path.join(home, "config.properties")
        if text is not None:
            open(f, "wb").write(text.encode("latin-1"))
        Cfg.FILE = Paths.get(f)
        return home, f

    def hist(home):
        d = os.path.join(home, "config-history")
        return sorted(x for x in os.listdir(d) if x.endswith(".bak")) if os.path.isdir(d) else []

    def logl(home):
        f = os.path.join(home, "config-changes.log")
        return [l for l in open(f, encoding="utf8").read().split("\n") if l] if os.path.isfile(f) else []

    rd = lambda f: open(f, "rb").read()
    live_ok = lt is not None
    home, f = setup("live", copy_live=True) if live_ok else setup("live", text=sample)
    b0, h0, l0 = rd(f), hist(home), logl(home)
    t0 = b0.decode("latin-1")
    untouched = (KEY + "=" + OLDV) in t0.replace("\r\n", "\n").split("\n")
    Cfg.migrate0110()
    Cfg.migrate0129()
    b1, h1, l1 = rd(f), hist(home), logl(home)
    r = str(Cfg.migrate0132())
    t1 = rd(f).decode("latin-1")
    print("MIG: %s config: %s %s -> %r" % ("the live test world's" if live_ok else "a sample", KEY, "untouched" if untouched else "edited / missing", r[:200]))
    if untouched:
        nl = "\r\n" if "\r\n" in t0 else "\n"
        K.check(t1 == b1.decode("latin-1").replace(nl + KEY + "=" + OLDV + nl, nl + MARK + nl + KEY + "=" + NEWV + nl, 1), "MIG live copy: the row updated + the marker, every other byte kept")
        rows = [l.split("\t") for l in logl(home)[len(l1):]]
        K.check(len(rows) == 1 and rows[0][1:4] == [WHO, "-", "update"] and rows[0][4:8] == [KEY, OLDV, NEWV, "ok"],
                "MIG live copy: one config-changes.log line in the Undo format: %s" % rows)
        K.check(KEY + " " + OLDV + " -> " + NEWV in r and "config-history" in r, "MIG live copy: the INFO line")
    else:
        K.check(MARK in t1, "MIG live copy: marked (%r)" % r[:200])
    K.check(len(hist(home)) == len(h1) + 1 and any(rd(os.path.join(home, "config-history", x)) == b1 for x in hist(home)) and all(x in hist(home) for x in h1),
            "MIG live copy: one new History version with the old bytes; the old versions kept")
    K.check(WHO in open(os.path.join(home, "config-history", "index.log"), encoding="utf8").read(), "MIG: the History index names the update")
    b2, h2, l2 = rd(f), hist(home), logl(home)
    K.check(str(Cfg.migrate0132()) == "" and rd(f) == b2 and hist(home) == h2 and logl(home) == l2, "MIG live copy: the second start changes nothing")
    Cfg.load()
    AN.sync()
    if untouched:
        K.check(str(AC.AB_NUMS) == NEWV and float(AN.AB_CD) == 5.0 and float(AN.AB_RANGE) == 6.5 and float(AN.AB_POWER) == 1.4,
                "MIG live copy: load() reads the 0.1.32 numbers (cooldown 5, range 6.5, power 1.4)")
    # hand-edited: kept, marker only, no change-log line
    home, f = setup("edited", text=sample.replace("cooldown=16", "cooldown=12"))
    bb = rd(f)
    r = str(Cfg.migrate0132())
    K.check(rd(f).decode("latin-1") == bb.decode("latin-1").replace("\n" + KEY, "\n" + MARK + "\n" + KEY, 1) and not logl(home) and "nothing changed" in r
            and "kept (custom)" in r, "MIG edited: kept, marker only, noted")
    Cfg.load()
    AN.sync()
    K.check(float(AN.AB_CD) == 12.0 and float(AN.AB_POWER) == 1.2, "MIG edited: load() keeps the hand-edited numbers (12 s, 1.2x)")
    # a 0.1.9-era CRLF file: the three updates in setup's order
    home, f = setup("chain", text=("kit.Warrior=Weapon_Sword_Crude:1\nkit.Assassin=Weapon_Daggers_Crude:1\npriestHeal.selfPercent=50\n%s=%s\n" % (KEY, OLDV)).replace("\n", "\r\n"))
    Cfg.migrate0110()
    Cfg.migrate0129()
    Cfg.migrate0132()
    tc = rd(f).decode("latin-1")
    K.check(KEY + "=" + NEWV + "\r\n" in tc and "kit.Assassin=Weapon_Daggers_Crude:1,Weapon_Kunai_Crude:1\r\n" in tc and tc.count(MARK) == 1
            and tc.count(str(Cfg.MG29_MARK)) == 1 and tc.count(str(Cfg.MG_MARK)) == 1 and "\n" not in tc.replace("\r\n", ""), "MIG chain: all three updates, CRLF kept")
    K.check(len(hist(home)) == 3 and sorted(l.split("\t")[1] for l in logl(home)).count(WHO) == 1, "MIG chain: three History versions, one 0.1.32 log line")
    # fresh: load() writes the 0.1.32 default (with the marker); the update never rewrites it; every ability's cooldown is in it
    home, f = setup("fresh")
    Cfg.load()
    fb = rd(f)
    ft = fb.decode("latin-1")
    K.check(str(Cfg.migrate0132()) == "" and rd(f) == fb and not hist(home), "MIG fresh: the 0.1.32 default file is never rewritten by the update")
    K.check((MARK + "\n" + KEY + "=" + NEWV) in ft.replace("\r\n", "\n"), "MIG fresh: the default file holds the marker + the new numbers")
    keys = dict(l.split("=", 1) for l in ft.replace("\r\n", "\n").split("\n") if l and not l.startswith("#") and "=" in l)
    miss = []
    for i in range(len(AD.IDS)):
        a = str(AD.IDS[i])
        ok = ("ab.%s.walk.cooldown" % a) in keys or ("ab.%s.cooldown" % a) in keys or ("," + keys.get("ab.%s.numbers" % a, "")).count(",cooldown=") == 1
        if not ok:
            miss.append(a)
    K.check(not miss and len(AD.IDS) == 39, "MIG fresh: every one of the 39 abilities has its own cooldown setting in Server Setup's file: missing %s" % miss)
    K.save()


# ================================================================================================================== ST1 / ST2
def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Pub, AS = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilStore")
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "st", "mods")
    base = os.path.join(home, "Skyy_SkyyClasses")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = tree_hash(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    o = {"m10": str(Cfg.migrate0110()), "m29": str(Cfg.migrate0129()), "m32": str(Cfg.migrate0132()), "load": str(Cfg.load())}
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    Pub.start(Paths.get(home), None)
    Pub.flush()
    Pub.shutdown()
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    if step == "1":
        lt = live_text()
        will = lt is not None and ("ab.ArcaneBreach.numbers=" + str(Cfg.MG32_OLD[0])) in lt.replace("\r\n", "\n").split("\n")
        okset = all(k == "config.properties" or k == "config-changes.log" or k.startswith("config-history/") for k in ch)
        K.check(okset and (not will or ("config.properties" in ch and o["m32"].startswith("config.properties updated to the 0.1.32"))),
                "ST start 1 on a scratch COPY of the live data: only the one-time update is written (%s) %s" % (ch, o["m32"][:120]))
    else:
        K.check(not ch and o["m32"] == "", "ST start 2: nothing written (%s)" % ch)
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyClasses folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


def bridge_keys():
    """every bridge key string the plugin class puts / removes (0.1.31 vs 0.1.32)"""
    sys.path.insert(0, os.path.join(TOOLS, "dev"))
    from cpstrings import read_utf8_constants
    o = {}
    for v, j in (("old", OLD_JAR), ("new", JAR)):
        with zipfile.ZipFile(j) as z:
            o[v] = set(s for s in read_utf8_constants(z.read("com/skyy/classes/SkyyClassesPlugin.class")) if s.startswith(("class:", "classes:", "tree:", "rebirth:")))
    return o


if __name__ == "__main__":
    if "--phase" not in sys.argv:
        k = bridge_keys()
        HK.check(k["old"] <= k["new"] and k["new"] - k["old"] == {"class:fn:stacks"}, "BR: every 0.1.31 bridge key is still there; one new: %s" % sorted(k["new"] - k["old"]))
        print("BR. bridge keys: %d in 0.1.31, + %s" % (len(k["old"]), sorted(k["new"] - k["old"])))
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("mig", run_mig), ("st1", run_st1), ("st2", run_st2)], script=__file__)
