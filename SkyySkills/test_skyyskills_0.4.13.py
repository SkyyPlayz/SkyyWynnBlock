"""SkyySkills 0.4.13 - bare-JVM harness for the combat state on the bridge (tools/skills_0_4_13_patch.py): skill:fn:combat (CombatFn) answers
the ms left in combat - EXACTLY the in-combat test of the 0.4.12 Mana regen (a NoDamageTaken condition of a positive Additive Mana regen
entry fails at the world's clock), recorded by ManaRegen.tick at its own 0.2 s pulse; nothing else changes. Copied forward from
SkyySkills/test_skyyskills_0.4.12.py: every 0.4.12 section still runs, now against the 0.4.13 jar with the SET pin 0.4.12 as the baseline.

    python SkyySkills/test_skyyskills_0.4.13.py [--jar <SkyySkills-0.4.13.jar>] [--old <SkyySkills-0.4.12.jar>] [--dir <scratch>]
                                                [--live <Skyy_SkyySkills folder>] [--keep]

Build first (python tools/skills_0_4_13_patch.py, then python SkyySkills/build_skyyskills_0.4.13.py). The old jar = the SET pin 0.4.12.
Child processes start fresh JVMs (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the jars; TEMP / TMP /
java.io.tmpdir in the scratch folder). The live world is READ ONLY: its Skyy_SkyySkills folder is copied into the scratch folder and only
that copy is ever written.
NEW in 0.4.13:
  W  the combat state on REAL engine conditions (AliveCondition, NoDamageTakenCondition 6 s, a charging stand-in, real RegeneratingValue
     entries, a real DamageDataComponent): 0 before any hit (lastDamageTime = Instant.MIN), 6000 right after a hit, 1 ms steps down to 1 at
     5999 ms, 0 at exactly 6 s (vanilla's >=); a sweep of 6,100 1-ms steps + nanosecond edges + 400 random instants: combatLeft > 0 <=>
     ManaRegen.state == 1 <=> the in-combat refill rate > 0 <=> the NoDamageTaken condition fails, and combatLeft = ceil((6 s - since the
     hit) / 1 ms); charging / dead keep the combat state (the refill stops, combat does not); the Delay asked from the condition = 6 s to the
     nanosecond (cached); WINDOW 0 before, 6000 after; a second entry with another Delay (the larger wins); entries without a NoDamageTaken
     or not Additive never count; a failing accessor = 0 + logged once. skill:fn:combat (the bridge Function, executed): Long 0 before any
     hit and for unknown players, ~6000 right after a hit (a pulse at the hit), counts down pulse by pulse to 0 at 6 s (matching state()
     at every pulse), counts down on the wall clock between pulses (>= 1 while the pulse is fresh, runs out once it is stale), "window" =
     6000, Object[] forms, bad arguments null, java.lang.Long types; an out-of-combat pulse removes the entry
  E  the REAL ManaRegen.tick end to end (stand-ins: Store / CommandBuffer subclasses, an EntityStatMap subclass that records
     addStatValue, the module singletons): a 500-tick script (hits, boosts, full Mana, in-combat 0 %, no Mana pool, no Mana value,
     charging, dead) on the 0.4.12 AND the 0.4.13 jar: the Mana after every tick and every addStatValue call identical up to the
     charging window (ticks 400-429, charging in combat: 0.4.13 adds exactly the in-combat amount, 0.4.12 nothing), the same per-tick
     refill after it (a constant offset); 0.4.13 records the combat state at every pulse (= the expected ms from the world clock), also
     where the refill returns early (full Mana, 0 %, no pool), and drops it without a Mana value
NEW in the 0.4.13 FIX ROUND (cross-check F1 / F2 + Skyy's LOCKED charging line):
  Y  F1 - stamps from another world's clock. Pure: ManaRegen.carried on 30 named cases with exact expected Instants (same stamp -> a
     smaller / bigger clock for all three stamps, a fresh hit in the new world left alone, a hit in the old world after its last pulse
     carried, the windows' overlap, the future guard with / without a record, Instant.MIN / null kept, over 1 hour = MIN and the exact
     1-hour edge, the time dilation of either world, a clock step back, broken records, an overflowing stamp) + 3000 random cases = a
     Python model of the rule. End to end through the REAL ManaRegen.tick on BOTH jars (0.4.12 = the control): a hit in 'default'
     (the live clock 09:12:57.683302876) -> /island (03:13:37.259307512, smaller) -> a hit there -> a bigger clock (15:00) -> a hit
     right after a pulse then a hop (late) -> back to 'default' with a fresh hit -> a stamp 1 hour in the future; real sleeps = the
     loading screens. 0.4.13: every first pulse in the new world = the exact carried stamps (computed from the recorded clock and the
     records' nanoTime), the countdown / skill:fn:combat continue from the last pulse minus the real time in between, combat ends on
     time, Health's NoDamageTaken 15 s turns at the real 15 s, the fresh hit and the late-hit rules hold, the future stamp becomes now;
     0.4.12: stuck "in combat" past 15 s on the smaller clock, out of combat at once on the bigger one, stuck on the future stamp.
     F2: Acro.retainOnline prunes ManaRegen.CMB and CARRY (and CLK) to the online players.
  H  CHARGING: state / rates / amount / stateLine on the real conditions (a real ChargingCondition subclass, inverse and not): charging
     out of combat = state 3, in combat = 4, dead + charging = 2, a non-inverse failing Charging = 2; a sweep of dead x charging x 9
     hit times x 5 boosts x 4 in-combat settings against vanilla's own entry (Condition.allConditionsMet = what
     RegeneratingValue.shouldRegenerate checks): vanilla + SkyySkills = 5 x (1 + MR) out of combat and F x 5 x (1 + MR) in combat,
     charging or not, 0 dead; SkyySkills pays the base only where vanilla does not (never double). The REAL tick on both jars (8
     steps: out / charging out / charging in combat / in combat / dead + charging / dead / out / charging at 0 % and no boosts / charging
     in combat at 0 %): every addStatValue = the exact float, vanilla modelled per pulse; 0.4.12 = 0 while charging (Skyy's report).
     /skills mana EXECUTED (the real ManaCmd.execute: charging out / in combat / dead / out / in combat lines + text()).
  Z  the ENGINE-ACCESS AUDIT with the JVM's own rules: every class / field / method / constructor reference in the 0.4.13 jar looked up
     with MethodHandles.privateLookupIn(its own class) - 0 refused (a control that calls a protected engine member from outside IS refused)
Carried forward (vs 0.4.12):
  A  every class of the 0.4.13 jar AND of the 0.4.12 jar loads and initializes under -Xverify:all
  T  the class table = the proposal's section 5, totals = its Total column; for every level boundary (+-1) and random totals: every slot's
     level / intoLevel / needFor / progress and generalLevel = the 0.4.12 jar's
  G  the guard: class level = max(general, class), the class max, the general list cut to 50, sameAsOthers = the general table
  P  per-slot everywhere (Divinity 67,425 = 28, Mining 15): SkillStore.level, skill:fn:level, skill:fn:xp, skill:<uuid>, skill:fn:overall,
     the pages, the chat lines, a real class level up and a Mining level up
  M  ClassCurve on scratch COPIES of the live data: (1) the live copy (0.4.12 already ran there): a start reads the record, scans nothing,
     tells nobody and writes nothing, twice; (2)-(5) the edited copies as in 0.4.12 (told + paid once, restart, profile:busy, an
     unwritable record, SkyyCoins missing) - counted on the test profiles: Skyy kept playing on 0.4.12, so a FRESH scan of a copy (record
     deleted) may also list a real profile whose class level is higher on the class table; checked to be real profiles that rose, left pending
  R  Mana regen maths (amount, rates / state on real engine conditions, mana.regen.inCombat load + clamps) - the 0.4.12 numbers
  B  skill:fn:manaregen add / remove / get / sources / clear, clamps, java.lang types, the Server Setup action
  C  the loader: the 0.4.13 default file = 0.4.12's but the version line; old files get both 0.4.12 blocks once (LF / CRLF), an admin's
     switch kept, bad / short class lists
  K  the Server Setup rows = 0.4.12's exactly (180, same order, every field); the class curve custom rows; kill / party / heal / grant XP
     = the 0.4.12 jar's
  F  class bytes 0.4.12 vs 0.4.13: + CombatFn only; changed beyond the version string: ManaRegen (+ delayOf / combatLeft / combat /
     combatNow / nsBetween / carried / carry / stateLine, + CMB / NDLY / WINDOW / CFAILED_ONCE / STALE_MS / NDLY_CAP / CARRY /
     KFAILED_ONCE / CARRY_CAP / CARRY_SLACK; tick, state, rates, amount, text), SkyySkillsPlugin (setup / shutdown), ManaCmd (execute) and
     Acro (retainOnline) only; every other class byte-identical or the version string only; manifest Name / Version only; every
     non-class entry byte-identical
  X  the 0.4.12 review fixes still hold (R1 / R3 / R4 / R5 / R9) + 0.4.13 bytecode order: ManaRegen.tick = pulse gate -> the clock + its
     dilation -> carry(...) -> the Mana value / entries -> combat(...) -> IN_COMBAT -> amount(rates(...)) -> addStatValue; carry reads /
     writes the three stamps through carried(); state tells ChargingCondition by eval0; ManaCmd.execute = rates -> stateLine -> text (the
     old "holding a charge" line gone); Acro.retainOnline prunes CLK, CMB and CARRY; setup() puts skill:fn:combat = new CombatFn after
     skill:fn:manaregen, shutdown() removes it
Nothing is deployed. Default scratch folder: tools/dev/scratch/skills0413/harness (deleted at the end unless --keep; --dir must be a folder
INSIDE tools/dev/scratch/). Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, zipfile, random, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION = "0.4.13", "0.4.12"
PKG = "com.skyy.skills."
CLASS_SLOTS = [5, 6, 7, 8, 9, 14, 15]
OTHER_SLOTS = [0, 1, 2, 3, 4, 10, 11, 12, 13]
ARCHERY, WARRIOR, DIVINITY, MINING, ALCHEMY, SMITHING, COOKING, EXPLORATION = 5, 6, 15, 0, 10, 11, 12, 13
HEALTHS = [-1.0, 2.0, 5.0, 7.0, 20.0, 37.0, 100.0, 250.0, 1000.0, 2500.0, 10000.0]
# the 6 rows 0.4.12 added (0.4.13 adds none - its rows must equal 0.4.12's)
NEW_KEYS = ["levels.class", "levels.class.scale", "levels.class.max", "levels.class.sameAsOthers", "mana.regen.inCombat", "mana.regen.show"]
T_SLOTS = [0, 4, 3, 12, 13, 5, 15, 6]          # the slots section T compares (Mining, Acrobatics, legacy Combat, Cooking, Exploration, Archery, Divinity, Swordsmanship)
NDT_NS = 6000000000                            # vanilla's NoDamageTaken Delay (Mana.json: 6 s)
SEC = 1000000000
CARRY_CAP, CARRY_SLACK = 3600 * SEC, SEC       # ManaRegen.CARRY_CAP / CARRY_SLACK (the build's fields; section F checks they exist)
# the live world clocks (resources/Time.json "Now", read 2026-10-02): default and the smallest island; BIG = a world ahead of default
CLK_A = (9 * 3600 + 12 * 60 + 57) * SEC + 683302876
CLK_B = (3 * 3600 + 13 * 60 + 37) * SEC + 259307512
CLK_C = 15 * 3600 * SEC
W0 = 5000000 * SEC                             # a System.nanoTime() base for the pure cases


def f32(x):
    """x rounded to a Java float (struct: IEEE binary32, round half to even like the JVM)"""
    return struct.unpack("f", struct.pack("f", x))[0]


TICK_NS = int(f32(1.0 / 30.0) * 1.0e9)        # the scripts' world-clock step per tick (dt = (float) 1/30 s, as tick_trace moves the clock)


def carried_py(s, wn, now, dil, wall, rec, i):
    """ManaRegen.carried in Python (the model the random sweep compares with): epoch-ns ints, None = null, "MIN" = Instant.MIN; rec =
    [world, clock ns, wall ns, dilation, stamp0, stamp1, stamp2] or None. Returns "keep", "MIN" or the new stamp (ns). Same double
    arithmetic in the same order as the Java (ints < 2^53 convert exactly)."""
    if s is None or now is None or s == "MIN":
        return "keep"
    out = None
    if (wn is not None and rec is not None and len(rec) >= 7 and 0 <= i < 3 and isinstance(rec[0], str) and wn != rec[0]
            and isinstance(rec[1], int) and isinstance(rec[2], int) and isinstance(rec[3], float)):
        rn = rec[1]
        gap = max(0, wall - rec[2])
        od = rec[3] if rec[3] > 0.0 else 1.0
        nd = dil if dil > 0.0 else 1.0
        take = rec[4 + i] is not None and rec[4 + i] != "MIN" and s == rec[4 + i]
        if not take and s > rn:
            fresh = s <= now and float(now - s) <= float(gap) * nd + float(CARRY_SLACK)
            take = (not fresh) and float(s - rn) <= float(gap) * od + float(CARRY_SLACK)
        if take:
            el = float(rn - s) / od + float(gap)
            if el < 0.0:
                el = 0.0
            out = "MIN" if el > float(CARRY_CAP) else now - int(el * nd)
    if out is None and s > now:
        out = now
    return "keep" if out is None else out


def _rec(w, rn, wall, dil, d=None, c=None, q=None):
    return [w, rn, wall, dil, d, c, q]


# section Y pure cases: (name, s, wn, now, dil, wall, rec, i, expected) - expected written by hand from the rule (ns, "keep" or "MIN")
_RA = _rec("default", CLK_A, W0, 1.0, CLK_A - 2 * SEC, CLK_A - 2 * SEC, CLK_A - 2 * SEC)
CARRY_CASES = [
    ("same stamp -> smaller clock (lastDamageTime)", CLK_A - 2 * SEC, "island", CLK_B, 1.0, W0 + SEC // 4, _RA, 0, CLK_B - 2 * SEC - SEC // 4),
    ("same stamp -> bigger clock", CLK_A - 2 * SEC, "big", CLK_C, 1.0, W0 + SEC // 4, _RA, 0, CLK_C - 2 * SEC - SEC // 4),
    ("same stamp -> smaller clock (lastCombatAction)", CLK_A - 2 * SEC, "island", CLK_B, 1.0, W0 + SEC // 4, _RA, 1, CLK_B - 2 * SEC - SEC // 4),
    ("same stamp -> smaller clock (lastChargeTime)", CLK_A - 2 * SEC, "island", CLK_B, 1.0, W0 + SEC // 4, _RA, 2, CLK_B - 2 * SEC - SEC // 4),
    ("a fresh hit in the new world (smaller clock): left alone", CLK_B - SEC // 10, "island", CLK_B, 1.0, W0 + SEC // 4, _RA, 0, "keep"),
    ("a fresh hit in the new world (bigger clock): left alone", CLK_C - SEC // 10, "big", CLK_C, 1.0, W0 + SEC // 4, _RA, 0, "keep"),
    ("a hit in the old world after its last pulse -> smaller clock", CLK_A + SEC // 10, "island", CLK_B, 1.0, W0 + SEC // 4, _RA, 0,
     CLK_B - (SEC // 4 - SEC // 10)),
    ("a hit in the old world after its last pulse -> bigger clock", CLK_A + SEC // 10, "big", CLK_C, 1.0, W0 + SEC // 4, _RA, 0,
     CLK_C - (SEC // 4 - SEC // 10)),
    ("past the late window (2 s after the pulse, gap 0.25 s): not carried, the future guard = now", CLK_A + 2 * SEC, "island", CLK_B, 1.0,
     W0 + SEC // 4, _RA, 0, CLK_B),
    ("late and fresh windows overlap (equal clocks): left alone", CLK_A + SEC // 10, "island2", CLK_A + 3 * SEC // 10, 1.0, W0 + SEC // 4, _RA, 0,
     "keep"),
    ("a future stamp in the same world = now", CLK_A + 3600 * SEC, "default", CLK_A + SEC, 1.0, W0 + SEC, _RA, 0, CLK_A + SEC),
    ("a future stamp, no record = now", CLK_A + 5 * SEC, "island", CLK_A, 1.0, W0, None, 0, CLK_A),
    ("a past stamp, no record: left alone", CLK_B - 5 * SEC, "island", CLK_B, 1.0, W0, None, 0, "keep"),
    ("Instant.MIN (never hit): left alone", "MIN", "island", CLK_B, 1.0, W0 + SEC // 4, _RA, 0, "keep"),
    ("null (no charge yet): left alone", None, "island", CLK_B, 1.0, W0 + SEC // 4, _RA, 2, "keep"),
    ("over 1 hour real since the hit = Instant.MIN", CLK_A - 2 * SEC, "island", CLK_B, 1.0, W0 + 3600 * SEC, _RA, 0, "MIN"),
    ("exactly 1 hour = now - 1 hour", CLK_A, "island", CLK_B, 1.0, W0 + 3600 * SEC, _rec("default", CLK_A, W0, 1.0, CLK_A), 0, CLK_B - 3600 * SEC),
    ("1 hour + 1 ns = Instant.MIN", CLK_A, "island", CLK_B, 1.0, W0 + 3600 * SEC + 1, _rec("default", CLK_A, W0, 1.0, CLK_A), 0, "MIN"),
    ("old world at time dilation 2: 2 s of its clock = 1 s real", CLK_A - 2 * SEC, "island", CLK_B, 1.0, W0 + SEC // 4,
     _rec("default", CLK_A, W0, 2.0, CLK_A - 2 * SEC), 0, CLK_B - SEC - SEC // 4),
    ("new world at time dilation 2: 2.25 s real = 4.5 s of its clock", CLK_A - 2 * SEC, "island", CLK_B, 2.0, W0 + SEC // 4, _RA, 0,
     CLK_B - 4 * SEC - SEC // 2),
    ("the wall clock stepped back (gap < 0 = 0)", CLK_A - 2 * SEC, "island", CLK_B, 1.0, W0 - 5 * SEC, _RA, 0, CLK_B - 2 * SEC),
    ("a record without its wall time: only the future guard", CLK_A - 2 * SEC, "island", CLK_B, 1.0, W0 + SEC // 4,
     _rec("default", CLK_A, None, 1.0, CLK_A - 2 * SEC), 0, CLK_B),
    ("a short record: only the future guard", CLK_A - 2 * SEC, "island", CLK_B, 1.0, W0 + SEC // 4, ["default", CLK_A, W0, 1.0], 0, CLK_B),
    ("no world name now: only the future guard", CLK_A - 2 * SEC, None, CLK_B, 1.0, W0 + SEC // 4, _RA, 0, CLK_B),
    ("no world name in the record: only the future guard", CLK_A - 2 * SEC, "island", CLK_B, 1.0, W0 + SEC // 4,
     _rec(None, CLK_A, W0, 1.0, CLK_A - 2 * SEC), 0, CLK_B),
    ("a stamp index out of range: only the future guard", CLK_A - 2 * SEC, "island", CLK_B, 1.0, W0 + SEC // 4, _RA, 3, CLK_B),
    ("a record dilation of 0 counts as 1", CLK_A - 2 * SEC, "island", CLK_B, 1.0, W0 + SEC // 4, _rec("default", CLK_A, W0, 0.0, CLK_A - 2 * SEC), 0,
     CLK_B - 2 * SEC - SEC // 4),
    ("the same world, the recorded stamp: nothing to do", CLK_A - 2 * SEC, "default", CLK_A + SEC, 1.0, W0 + SEC, _RA, 0, "keep"),
    ("a dilation of 0 now counts as 1", CLK_A - 2 * SEC, "island", CLK_B, 0.0, W0 + SEC // 4, _RA, 0, CLK_B - 2 * SEC - SEC // 4),
]


def random_carry_cases(n, seed=4131):
    """n random [s, wn, now, dil, wall, rec, i] for ManaRegen.carried vs carried_py: the recorded stamp, a stamp after the record's
    clock, one in the new world's window, the future, MIN / null, anything; same / other / no world; gaps from 0 to past 1 hour and a
    step back; dilations 0 / 0.5 / 1 / 2 / 4; sometimes no record"""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        rn = rnd.choice([CLK_A, CLK_B, CLK_C, rnd.randrange(0, 20 * 3600 * SEC)])
        now = rnd.choice([CLK_A, CLK_B, CLK_C, rn + rnd.randrange(-3 * SEC, 3 * SEC), rnd.randrange(0, 20 * 3600 * SEC)])
        gap = rnd.choice([0, rnd.randrange(0, 2 * SEC), rnd.randrange(0, 10 * SEC), 3600 * SEC + rnd.randrange(-3, 4), -rnd.randrange(1, SEC)])
        od, nd = rnd.choice([1.0, 1.0, 2.0, 0.5, 4.0, 0.0]), rnd.choice([1.0, 1.0, 2.0, 0.5, 4.0, 0.0])
        srec = rnd.choice([rn - rnd.randrange(0, 10 * SEC), rn - rnd.randrange(0, 4000 * SEC), rn, "MIN", None])
        kind = rnd.randrange(8)
        if kind in (0, 6, 7) and isinstance(srec, int):
            s = srec
        elif kind == 1:
            s = rn + rnd.randrange(1, 3 * SEC)
        elif kind == 2:
            s = now - rnd.randrange(0, 3 * SEC)
        elif kind == 3:
            s = now + rnd.randrange(1, 7200 * SEC)
        elif kind == 4:
            s = rnd.choice(["MIN", None])
        elif kind == 5:
            s = rnd.randrange(0, 20 * 3600 * SEC)
        else:
            s = rn - rnd.randrange(0, 10 * SEC)                    # "the same" kinds without a recorded stamp: any past stamp
        wrec = rnd.choice(["default", "island", "big"])
        wn = rnd.choice([wrec, wrec, rnd.choice(["default", "island", "big", None])])
        rec = None if rnd.random() < 0.08 else [wrec, rn, W0, od, srec, srec if rnd.random() < 0.5 else None, srec if rnd.random() < 0.5 else None]
        out.append([s, wn, now, nd, W0 + gap, rec, rnd.randrange(3)])
    return out


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills0413", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyySkills-%s.jar" % OLD_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
LIVE = os.path.join(LIVE_DIR, "xp.properties")
KEEP = "--keep" in sys.argv
FAILS, OKS, GUARD_OK = [], [0], [False]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def proposal_table():
    md = open(os.path.join(ROOT, "research", "cloud", "Class-Skill-Curve-Proposal.md"), encoding="utf8").read()
    sec = md[md.index("## 5. Per-level table"):md.index("## 6.")]
    rows = []
    for ln in sec.splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|", ln)
        if m:
            rows.append(tuple(int(x.replace(",", "")) for x in m.groups()))
    return rows


def _jvm_start(cp, verify=True):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
    jpype.startJVM(jvm, *opts, classpath=[B.SERVER_JAR] + list(cp), convertStrings=True)
    return B


# ============================================================================================ child: the javassist stand-ins
def run_mkfake(out_dir):
    """skyytest.FakeHandler (PacketHandler: counts packets, keeps every chat text), FakeWorld (World.execute runs at once), FixedCondition
    (a Condition whose eval0 answers a field), FakeAcc (a ComponentAccessor answering getComponent with one DamageDataComponent and
    getArchetype with one Archetype); 0.4.13: FakeStore / FakeCB / FakeStatMap for the real ManaRegen.tick; fix round: FakeStore also
    answers getExternalData (the world) and the store reads of ManaCmd.execute, FixedCharging (a REAL ChargingCondition subclass - the
    charging stand-in), FakePerms (PermissionsModule saying yes), LookupIn + BadAccess (the access audit and its control)."""
    import jpype
    from jpype import JClass
    import skyybuild as B
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", classpath=[B.JAVASSIST], convertStrings=True)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    h = cp.makeClass("skyytest.FakeHandler")
    h.setSuperclass(cp.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    h.addField(CtField.make("public static volatile int SENT = 0;", h))
    h.addField(CtField.make("public static final java.util.List TEXTS = java.util.Collections.synchronizedList(new java.util.ArrayList());", h))
    h.addMethod(CtNewMethod.make("""public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) {
  SENT = SENT + 1;
  if (p instanceof com.hypixel.hytale.protocol.packets.interface_.ServerMessage) {
    com.hypixel.hytale.protocol.FormattedMessage m = ((com.hypixel.hytale.protocol.packets.interface_.ServerMessage) p).message;
    TEXTS.add(m == null ? "" : String.valueOf(m.rawText));
  }
}""", h))
    h.writeFile(out_dir)
    w = cp.makeClass("skyytest.FakeWorld")
    w.setSuperclass(cp.get("com.hypixel.hytale.server.core.universe.world.World"))
    w.addField(CtField.make("public static volatile int RAN = 0;", w))
    w.addMethod(CtNewMethod.make("public void execute(java.lang.Runnable r) { RAN = RAN + 1; r.run(); }", w))
    w.writeFile(out_dir)
    c = cp.makeClass("skyytest.FixedCondition")
    c.setSuperclass(cp.get("com.hypixel.hytale.server.core.modules.entity.condition.Condition"))
    c.addField(CtField.make("public boolean v;", c))
    c.addConstructor(CtNewConstructor.make("public FixedCondition(boolean v) { super(false); this.v = v; }", c))
    c.addMethod(CtNewMethod.make("public boolean eval0(com.hypixel.hytale.component.ComponentAccessor a, com.hypixel.hytale.component.Ref r, java.time.Instant n) { return this.v; }", c))
    c.writeFile(out_dir)
    a = cp.makeClass("skyytest.FakeAcc")
    a.addInterface(cp.get("com.hypixel.hytale.component.ComponentAccessor"))
    a.addField(CtField.make("public com.hypixel.hytale.component.Component dd;", a))
    a.addField(CtField.make("public com.hypixel.hytale.component.Archetype arch;", a))
    a.addConstructor(CtNewConstructor.make("public FakeAcc() { }", a))
    a.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) { return this.dd; }", a))
    a.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Archetype getArchetype(com.hypixel.hytale.component.Ref r) { return this.arch; }", a))
    a.writeFile(out_dir)
    # 0.4.13 (section E): the REAL ManaRegen.tick needs a Store (its TimeResource) and a CommandBuffer (the EntityStatMap, the
    # DamageDataComponent, the Archetype). Subclasses that answer exactly those; created with Unsafe.allocateInstance (no constructor runs -
    # Store's is package-private). FakeStatMap records addStatValue (the real one needs the stat asset map) - the harness applies the amount.
    st_ = cp.makeClass("skyytest.FakeStore")
    st_.setSuperclass(cp.get("com.hypixel.hytale.component.Store"))
    st_.addField(CtField.make("public com.hypixel.hytale.component.Resource time;", st_))
    # 0.4.13 fix round: the store's world (getExternalData -> an EntityStore -> World.getName, section Y) and the components /
    # archetype the real ManaCmd.execute reads through the store (section H)
    for decl in ("java.lang.Object ext", "com.hypixel.hytale.component.Component stats", "com.hypixel.hytale.component.Component dd",
                 "com.hypixel.hytale.component.ComponentType statsType", "com.hypixel.hytale.component.ComponentType ddType",
                 "com.hypixel.hytale.component.Archetype arch"):
        st_.addField(CtField.make("public %s;" % decl, st_))
    # never run (Unsafe.allocateInstance): javassist wants some constructor, Store's only one is package-private
    st_.addConstructor(CtNewConstructor.make("public FakeStore() { super(null, 0, null, null); }", st_))
    st_.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Resource getResource(com.hypixel.hytale.component.ResourceType t) { return this.time; }", st_))
    st_.addMethod(CtNewMethod.make("public java.lang.Object getExternalData() { return this.ext; }", st_))
    st_.addMethod(CtNewMethod.make("""public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (t == this.statsType) return this.stats;
  if (t == this.ddType) return this.dd;
  return null;
}""", st_))
    st_.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Archetype getArchetype(com.hypixel.hytale.component.Ref r) { return this.arch; }", st_))
    st_.writeFile(out_dir)
    # 0.4.13 fix round: a REAL ChargingCondition (subclass) whose answer is a field - v = the condition passes (eval() == v); inv = the
    # Inverse flag (vanilla Mana.json: Charging, Inverse -> eval0 = "is charging" = !v); a non-inverse one answers eval0 = v
    fc = cp.makeClass("skyytest.FixedCharging")
    fc.setSuperclass(cp.get("com.hypixel.hytale.server.core.modules.entity.condition.ChargingCondition"))
    fc.addField(CtField.make("public boolean v;", fc))
    fc.addConstructor(CtNewConstructor.make("public FixedCharging(boolean v, boolean inv) { super(); this.v = v; this.inverse = inv; }", fc))
    fc.addMethod(CtNewMethod.make("public boolean eval0(com.hypixel.hytale.component.ComponentAccessor a, com.hypixel.hytale.component.Ref r, java.time.Instant n) { return this.inverse ? !this.v : this.v; }", fc))
    fc.writeFile(out_dir)
    # the permissions module for the real ManaCmd.execute (pr.hasPermission -> PermissionsModule.get().hasPermission(uuid, node))
    pm = cp.makeClass("skyytest.FakePerms")
    pm.setSuperclass(cp.get("com.hypixel.hytale.server.core.permissions.PermissionsModule"))
    pm.addConstructor(CtNewConstructor.make("public FakePerms() { super(null); }", pm))   # never run (Unsafe.allocateInstance)
    pm.addMethod(CtNewMethod.make("public boolean hasPermission(java.util.UUID u, String n) { return true; }", pm))
    pm.writeFile(out_dir)
    # section Z: a MethodHandles.Lookup IN a given class (the JVM's own access rules) + the control: a class that is no page calling the
    # page's PROTECTED sendUpdate (javassist compiles it; the JVM refuses it when it runs - the audit must name it)
    lk = cp.makeClass("skyytest.LookupIn")
    lk.addMethod(CtNewMethod.make(
        "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
        "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", lk))
    lk.writeFile(out_dir)
    ba = cp.makeClass("skyytest.BadAccess")
    ba.addMethod(CtNewMethod.make(
        "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
        "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}", ba))
    ba.writeFile(out_dir)
    cb_ = cp.makeClass("skyytest.FakeCB")
    cb_.setSuperclass(cp.get("com.hypixel.hytale.component.CommandBuffer"))
    for decl in ("com.hypixel.hytale.component.Component stats", "com.hypixel.hytale.component.Component dd", "com.hypixel.hytale.component.ComponentType statsType",
                 "com.hypixel.hytale.component.ComponentType ddType", "com.hypixel.hytale.component.Archetype arch"):
        cb_.addField(CtField.make("public %s;" % decl, cb_))
    cb_.addMethod(CtNewMethod.make("""public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (t == this.statsType) return this.stats;
  if (t == this.ddType) return this.dd;
  return null;
}""", cb_))
    cb_.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Archetype getArchetype(com.hypixel.hytale.component.Ref r) { return this.arch; }", cb_))
    cb_.writeFile(out_dir)
    sm_ = cp.makeClass("skyytest.FakeStatMap")
    sm_.setSuperclass(cp.get("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"))
    for decl in ("int calls", "float added", "float last", "int lastIndex"):
        sm_.addField(CtField.make("public %s;" % decl, sm_))
    sm_.addMethod(CtNewMethod.make("""public float addStatValue(int i, float a) {
  this.calls = this.calls + 1;
  this.added = this.added + a;
  this.last = a;
  this.lastIndex = i;
  return a;
}""", sm_))
    sm_.writeFile(out_dir)


def load_all(jar):
    from jpype import JClass
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    loaded, fails = 0, []
    for n in names:
        try:
            Cls.forName(n, True, loader)
            loaded += 1
        except Exception as e:
            fails.append("%s: %s" % (n, e))
    return {"jar": jar, "classes": len(names), "loaded": loaded, "load_fails": fails, "data": {}}


def rows_of(Rows):
    cols = ("KEYS", "LABELS", "CATS", "TYPES", "DEFS", "MINS", "MAXS", "OPTS", "UNITS", "FLAGS", "HELPS")
    arrs = [[str(x) for x in getattr(Rows, c)] for c in cols]
    return {"rows": [list(r) for r in zip(*arrs)]}


def totals_to_test(cum_a, cum_b):
    """every level boundary of both tables, +-1, plus random totals up to past the end of the longer one"""
    xs = set([0, 1])
    for c in (cum_a, cum_b):
        for v in c:
            for d in (-1, 0, 1):
                if v + d >= 0:
                    xs.add(v + d)
    rnd = random.Random(412)
    top = max(cum_a[-1], cum_b[-1]) + 1000000
    for _ in range(1500):
        xs.add(rnd.randrange(0, top))
    return sorted(xs)


def common(jar, extra_cp):
    from jpype import JClass
    _jvm_start([jar] + extra_cp)
    res = load_all(jar)
    Paths, JStr, Arr = JClass("java.nio.file.Paths"), JClass("java.lang.String"), JClass("java.lang.reflect.Array")

    def path(p):
        return Paths.get(p, Arr.newInstance(JStr.class_, 0))
    return res, path


def defaults_part(D, Cfg, Rows, Bx, path, work):
    """numbers both jars must agree on: kill XP at the defaults, grants / gathering paid, rows, the default file"""
    from jpype import JClass, JFloat
    UUID = JClass("java.util.UUID")
    f = os.path.join(work, "xp.properties")
    if os.path.exists(f):
        os.remove(f)
    Cfg.FILE = path(f)
    D["load"] = str(Cfg.load())
    D["defaults"] = open(f, "rb").read().decode("latin-1")
    D["kill"] = [int(Cfg.classXp(ARCHERY, Cfg.combatXp(None, JFloat(h)))) for h in HEALTHS]
    D["base"] = [int(Cfg.combatXp(None, JFloat(h))) for h in HEALTHS]
    D["other"] = dict((str(s), [int(Cfg.classXp(s, x)) for x in (1, 7, 20, 500)]) for s in OTHER_SLOTS)
    u = UUID(0x5117, 99)
    D["paid"] = [int(Bx.paid(u, MINING, 500, True)), int(Bx.paid(u, ALCHEMY, 40, False)), int(Bx.paid(u, SMITHING, 12, False)),
                 int(Bx.paid(u, COOKING, 30, True)), int(Bx.paid(u, EXPLORATION, 25, True)), int(Bx.paid(u, 4, 9, True)),
                 int(Bx.paid(u, ARCHERY, 100, True)), int(Bx.paid(u, DIVINITY, 10, False)), int(Bx.paidX(u, DIVINITY, 10, False, False))]
    D["rows"] = rows_of(Rows)


# ============================================================================================ the Mana regen's engine pieces (both jars)
def regen_env():
    """the REAL engine pieces the Mana regen reads, in a bare JVM: the EntityModule / DamageModule / EntityStatsModule / TimeModule
    singletons (allocated; only their component / resource type field set, so DamageDataComponent / DeathComponent / EntityStatMap
    .getComponentType() and TimeResource.getResourceType() resolve), a NoDamageTakenCondition with Delay 6 s, the charging stand-in,
    vanilla's Mana regen entry (+1 every 0.2 s if Alive, NoDamageTaken 6 s, not Charging) as a real RegeneratingValue, a FakeAcc with a
    real DamageDataComponent, and the tick stand-ins: FakeStore holding a real TimeResource, FakeCB, FakeStatMap holding a real
    EntityStatValue for Mana at index 0 (= DefaultEntityStatTypes.getMana() in a bare JVM)"""
    from jpype import JClass, JFloat, JArray, JInt
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    Mod = JClass("java.lang.reflect.Modifier")

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)
    E = {"U": U, "setf": setf}
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    DM = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule")
    SM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    TM = JClass("com.hypixel.hytale.server.core.modules.time.TimeModule")
    CT, RT = JClass("com.hypixel.hytale.component.ComponentType"), JClass("com.hypixel.hytale.component.ResourceType")
    E["ddType"], E["deathType"], E["statsType"] = U.allocateInstance(CT.class_), U.allocateInstance(CT.class_), U.allocateInstance(CT.class_)
    E["timeType"] = U.allocateInstance(RT.class_)
    E["stubs"] = []
    for cls, want in ((EM, ("damageDataComponentType", E["ddType"])), (DM, ("deathComponentType", E["deathType"])),
                      (SM, ("entityStatMapComponentType", E["statsType"])), (TM, ("timeResourceType", E["timeType"]))):
        inst = U.allocateInstance(cls.class_)
        sf_ = [f for f in cls.class_.getDeclaredFields() if Mod.isStatic(f.getModifiers()) and f.getType() == cls.class_]
        E["stubs"].append(len(sf_))
        for f in sf_:
            f.setAccessible(True)
            f.set(None, inst)
        setf(inst, cls, want[0], want[1])
    E["Arch"] = Arch = JClass("com.hypixel.hytale.component.Archetype")
    E["DDC"] = DDC = JClass("com.hypixel.hytale.server.core.entity.damage.DamageDataComponent")
    E["NDT"] = NDT = JClass("com.hypixel.hytale.server.core.modules.entity.condition.NoDamageTakenCondition")
    Alive = JClass("com.hypixel.hytale.server.core.modules.entity.condition.AliveCondition")
    E["RGN"] = RGN = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating")
    E["RGT"] = RGT = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating$RegenType")
    E["RGV"] = RGV = JClass("com.hypixel.hytale.server.core.modules.entitystats.RegeneratingValue")
    Cond = JClass("com.hypixel.hytale.server.core.modules.entity.condition.Condition")
    E["Instant"], E["Duration"] = Instant, Duration = JClass("java.time.Instant"), JClass("java.time.Duration")
    nctor = NDT.class_.getDeclaredConstructor()
    nctor.setAccessible(True)

    def ndt(duration):
        c = nctor.newInstance()
        setf(c, NDT, "delay", duration)
        return c
    E["ndt"] = ndt
    E["nodmg"] = nodmg = ndt(Duration.ofSeconds(6))
    # vanilla's Charging (Inverse) as a REAL ChargingCondition subclass (0.4.13 fix round: state() tells it by type + eval0):
    # .v = the condition passes = NOT charging; .v = False = the player is charging (eval0 true, the inverse condition fails)
    E["charging"] = charging = JClass("skyytest.FixedCharging")(True, True)
    E["FixedCharging"] = JClass("skyytest.FixedCharging")
    E["CHG"] = JClass("com.hypixel.hytale.server.core.modules.entity.condition.ChargingCondition")
    E["Alive"] = Alive

    def entry(amount, interval, rtype, conds):
        rg = RGN()
        setf(rg, RGN, "amount", JFloat(amount))
        setf(rg, RGN, "interval", JFloat(interval))
        setf(rg, RGN, "regenType", rtype)
        setf(rg, RGN, "conditions", None if conds is None else JArray(Cond)(conds))
        return RGV(rg)
    E["entry"] = entry
    E["vanilla"] = entry(1.0, 0.2, RGT.ADDITIVE, [Alive(False), nodmg, charging])
    E["now"] = Instant.parse("2026-10-02T12:00:00Z")
    E["acc"] = acc = JClass("skyytest.FakeAcc")()
    E["dd"] = dd = DDC()
    acc.dd = dd
    acc.arch = Arch.empty()
    # the tick stand-ins
    TR = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
    ESV = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    E["ESV"], E["ESM"] = ESV, ESM
    E["tr"] = tr = TR(E["now"])
    E["store"] = store = U.allocateInstance(JClass("skyytest.FakeStore").class_)
    store.time = tr
    E["mv"] = mv = U.allocateInstance(ESV.class_)
    for name, val in (("id", "Mana"), ("index", JInt(0)), ("value", JFloat(2.0)), ("min", JFloat(0.0)), ("max", JFloat(30.0)),
                      ("regeneratingValues", JArray(RGV)([E["vanilla"]]))):
        setf(mv, ESV, name, val)
    E["fsm"] = fsm = U.allocateInstance(JClass("skyytest.FakeStatMap").class_)
    setf(fsm, ESM, "values", JArray(ESV)([mv]))
    E["dd2"] = dd2 = DDC()                                         # the tick's own DamageDataComponent (never hit yet)
    E["cb"] = cb = U.allocateInstance(JClass("skyytest.FakeCB").class_)
    cb.stats, cb.dd, cb.statsType, cb.ddType, cb.arch = fsm, dd2, E["statsType"], E["ddType"], Arch.empty()
    return E


def tick_trace(E, Mana, combat):
    """section E: 500 ticks of 1/30 s through the REAL ManaRegen.tick(u, store, cb, ref, dt) on the stand-ins, the world clock (the
    TimeResource) moved like TimeSystem.tick before each one. The script (events before tick t): 30 hit; 90 Mana Regen +20%; 150 hit;
    200 full Mana; 230 Mana 10, in-combat 0 % + no boosts (the refill returns before reading anything); 232 hit; 300 in-combat 50 %, no
    Mana pool (max 0) + hit; 340 no Mana value at all; 360 the value back (Mana 5 / 30) + Mana Regen +20%; 400 charging; 430 dead;
    460 alive; 480 out of combat (the boost part only); 490 hit. Per tick: [t, Mana after, addStatValue calls, pulsed, ns since the last
    hit (-1 never), the combat entry ms (0.4.13; 0 = no entry, None = 0.4.12)]"""
    from jpype import JClass, JFloat, JLong, JArray
    UUID, ChronoUnit = JClass("java.util.UUID"), JClass("java.time.temporal.ChronoUnit")
    Instant, ESV, ESM, RGV = E["Instant"], E["ESV"], E["ESM"], E["RGV"]
    tr, store, cb, fsm, mv, dd2, setf = E["tr"], E["store"], E["cb"], E["fsm"], E["mv"], E["dd2"], E["setf"]
    u = UUID(0xE13, 1)
    Mana.CLK.clear()
    Mana.SRC.clear()
    Mana.IN_COMBAT = 50
    if combat:
        Mana.CMB.clear()
    dd2.setLastDamageTime(Instant.MIN)
    E["charging"].v = True
    cb.arch = E["Arch"].empty()
    setf(mv, ESV, "value", JFloat(2.0))
    setf(mv, ESV, "max", JFloat(30.0))
    dt = JFloat(1.0 / 30.0)
    nanos = JLong(int(float(dt) * 1.0e9))                          # TimeSystem.tick: (long) (dt * 1.0E9f) nanoseconds per tick
    rows, warn0 = [], bool(Mana.FAILED_ONCE)

    def hit():
        dd2.setLastDamageTime(tr.getNow())
    for t in range(500):
        tr.add(nanos, ChronoUnit.NANOS)                            # the world clock first (TimeSystem ticks before the entity systems)
        if t in (30, 150, 232, 300, 490):
            hit()
        if t == 90:
            Mana.put(u, "Test", 20.0)
        if t == 200:
            setf(mv, ESV, "value", JFloat(30.0))
        if t == 230:
            setf(mv, ESV, "value", JFloat(10.0))
            Mana.IN_COMBAT = 0
            Mana.remove(u, "Test")
        if t == 300:
            Mana.IN_COMBAT = 50
            setf(mv, ESV, "max", JFloat(0.0))
            setf(mv, ESV, "value", JFloat(0.0))
        if t == 340:
            setf(mv, ESV, "max", JFloat(30.0))
            setf(mv, ESV, "value", JFloat(5.0))
            setf(fsm, ESM, "values", JArray(ESV)([]))
        if t == 360:
            setf(fsm, ESM, "values", JArray(ESV)([mv]))
            Mana.put(u, "Test", 20.0)
        if t == 400:
            E["charging"].v = False
        if t == 430:
            E["charging"].v = True
            cb.arch = E["Arch"].of(E["deathType"])
        if t == 460:
            cb.arch = E["Arch"].empty()
        c0 = int(fsm.calls)
        ck = Mana.CLK.get(u)
        c_before = float(ck[0]) if ck is not None else 0.0
        Mana.tick(u, store, cb, None, dt)
        added = 0.0
        if int(fsm.calls) != c0:                                   # what the real EntityStatValue.set would do: clamp to [min, max]
            added = float(fsm.last)
            setf(mv, ESV, "value", JFloat(min(float(mv.getMax()), max(0.0, float(mv.get()) + float(fsm.last)))))
        clk = Mana.CLK.get(u)
        last = dd2.getLastDamageTime()
        since = -1 if last.equals(Instant.MIN) else int(last.until(tr.getNow(), ChronoUnit.NANOS))
        ent = None
        if combat:
            e = Mana.CMB.get(u)
            ent = int(e[0]) if e is not None else 0
        # 0.4.13 fix round: + the amount this tick added and the pulse's seconds (the Java float sum of the CLK clock, at most 1)
        rows.append([t, round(float(mv.get()), 6), int(fsm.calls), clk is not None and float(clk[0]) == 0.0, since, ent, added,
                     min(1.0, f32(f32(c_before) + f32(float(dt))))])
    return {"rows": rows, "warn": [warn0, bool(Mana.FAILED_ONCE)], "calls": int(fsm.calls), "index": int(fsm.lastIndex)}


def _ns(i, Instant):
    """an Instant as epoch ns (None for null, "MIN" for Instant.MIN)"""
    if i is None:
        return None
    if i.equals(Instant.MIN):
        return "MIN"
    return int(i.getEpochSecond()) * SEC + int(i.getNano())


def switch_trace(E, Mana, new):
    """section Y end to end (0.4.13 fix F1; BOTH jars - 0.4.12 is the control): the REAL ManaRegen.tick across world switches. Every world
    has its own TimeResource (the live clocks: 'default' CLK_A, the island CLK_B - smaller; 'big' CLK_C - bigger) and its EntityStore ->
    World name (FakeStore.getExternalData); the player's DamageDataComponent travels (the Holder keeps it). dt 1/30 s, the current world's
    clock moved before each tick (TimeSystem first); a hop = the store's world + clock switched and a real sleep (the loading screen).
      A   'default': hit + attack + a released charge at tick 30 (the three stamps), then 2 s
      H1  -> island (smaller clock), 0.25 s asleep; I1 = 15 s of island ticks (Mana's 6 s and Health's 15 s both run out)
      B   island: a hit, 1 s;  H2 -> 'big' (bigger clock), 0.15 s asleep; I2 = 6 s
      L   'big': a hit one tick after a pulse, then -> island at once, 0.1 s asleep (a hit in the old world on its way out); I3 = 2 s
      H4  -> 'default' (its clock ran 30 s meanwhile) with a FRESH hit there 0.1 s before the first pulse; I4 = 1 s
      G   'default': the hit stamp set 1 hour in the FUTURE of the clock (same world); I5 = 1 s
    Per pulse: {step, world, now, before / after = the three stamps around the tick, state (the Mana regen's own test), cmb (0.4.13:
    the skill:fn:combat entry ms, 0 = none), fn (0.4.13: CombatFn.apply right after the pulse), rec (0.4.13: the CARRY record after the
    pulse), h15 (vanilla Health's NoDamageTaken 15 s condition at the pulse)}"""
    import time as _t
    from jpype import JClass, JFloat, JLong
    UUID, ChronoUnit, Duration = JClass("java.util.UUID"), JClass("java.time.temporal.ChronoUnit"), E["Duration"]
    Instant, setf, U, ESV = E["Instant"], E["setf"], E["U"], E["ESV"]
    store, cb, mv = E["store"], E["cb"], E["mv"]
    TR = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
    EST = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    FakeW = JClass("skyytest.FakeWorld")
    dd = E["DDC"]()                                                # the player's DamageDataComponent (travels with the Holder)
    dd_keep, time_keep = cb.dd, store.time
    cb.dd = dd
    fn = JClass(PKG + "CombatFn")() if new else None

    def world(name):
        w = U.allocateInstance(FakeW.class_)
        setf(w, WLD, "name", name)
        es = U.allocateInstance(EST.class_)
        setf(es, EST, "world", w)
        return es

    def inst(ns_):
        return Instant.ofEpochSecond(ns_ // SEC, ns_ % SEC)
    W = {"default": (world("default"), TR(inst(CLK_A))),
         "island": (world("skyy-island-d8ddde89-98b2-4739-983e-a39773d582b6-p4"), TR(inst(CLK_B))),
         "big": (world("skyy-island-b942734e-90b8-4e4b-986c-cd725d975b9e"), TR(inst(CLK_C)))}
    u = UUID(0xF1, 1)
    Mana.CLK.clear()
    Mana.SRC.clear()
    Mana.IN_COMBAT = 50
    if new:
        Mana.CMB.clear()
        Mana.CARRY.clear()
    E["charging"].v = True
    cb.arch = E["Arch"].empty()
    setf(mv, ESV, "value", JFloat(2.0))
    setf(mv, ESV, "max", JFloat(100000.0))
    ndt15 = E["ndt"](Duration.ofSeconds(15))                       # vanilla Health.json's NoDamageTaken 15 s
    cur = {"w": None}
    rows = []
    dt = JFloat(1.0 / 30.0)
    nanos = JLong(int(float(dt) * 1.0e9))

    def go(name):
        es, tr = W[name]
        store.ext = es
        store.time = tr
        cur["w"] = name

    def stamps():
        return [_ns(dd.getLastDamageTime(), Instant), _ns(dd.getLastCombatAction(), Instant), _ns(dd.getLastChargeTime(), Instant)]

    def rec():
        if not new:
            return None
        r = Mana.CARRY.get(u)
        if r is None:
            return None
        return [None if r[0] is None else str(r[0]), _ns(r[1], Instant), int(r[2].longValue()), float(r[3].floatValue()),
                _ns(r[4], Instant), _ns(r[5], Instant), _ns(r[6], Instant)]

    def tick(step):
        tr = W[cur["w"]][1]
        tr.add(nanos, ChronoUnit.NANOS)
        before = stamps()
        Mana.tick(u, store, cb, None, dt)
        c = Mana.CLK.get(u)
        if c is None or float(c[0]) != 0.0:
            return False
        now = tr.getNow()
        e = Mana.CMB.get(u) if new else None
        rows.append({"step": step, "w": cur["w"], "now": _ns(now, Instant), "before": before, "after": stamps(),
                     "state": int(Mana.state(cb, None, now, E["vanilla"].getRegenerating())),
                     "cmb": (int(e[0]) if e is not None else 0) if new else None,
                     "fn": int(fn.apply(u).longValue()) if new else None, "rec": rec(), "h15": bool(ndt15.eval(cb, None, now))})
        return True

    def run(step, n):
        for _ in range(n):
            tick(step)

    def to_pulse(step):
        for _ in range(40):
            if tick(step):
                return True
        return False
    go("default")
    run("A0", 30)
    t0 = W["default"][1].getNow()
    dd.setLastDamageTime(t0)
    dd.setLastCombatAction(t0)
    dd.setLastChargeTime(t0)
    run("A", 60)
    go("island")
    _t.sleep(0.25)
    to_pulse("H1")
    run("I1", 450)
    dd.setLastDamageTime(W["island"][1].getNow())
    run("B", 30)
    go("big")
    _t.sleep(0.15)
    to_pulse("H2")
    run("I2", 180)
    to_pulse("L0")
    tick("L1")                                                     # one tick after the pulse (no pulse)
    late = W["big"][1].getNow()
    dd.setLastDamageTime(late)
    go("island")
    _t.sleep(0.1)
    to_pulse("H3")
    run("I3", 60)
    W["default"][1].add(JLong(30 * SEC), ChronoUnit.NANOS)          # 'default' kept running while the player was away
    go("default")
    _t.sleep(0.05)
    fresh = W["default"][1].getNow().minusMillis(100)
    dd.setLastDamageTime(fresh)
    to_pulse("H4")
    run("I4", 30)
    fut = W["default"][1].getNow().plusSeconds(3600)
    dd.setLastDamageTime(fut)
    to_pulse("G")
    run("I5", 30)
    out = {"rows": rows, "late": _ns(late, Instant), "fresh": _ns(fresh, Instant), "future": _ns(fut, Instant), "t0": _ns(t0, Instant),
           "warn": [bool(Mana.FAILED_ONCE), bool(Mana.KFAILED_ONCE) if new else None]}
    cb.dd, store.time, store.ext = dd_keep, time_keep, None
    return out


def charge_trace(E, Mana, new):
    """section H end to end (Skyy 2026-10-02 LOCKED; BOTH jars - 0.4.12 is the control): Mana while charging through the REAL ManaRegen.tick,
    vanilla's own entry modelled at every pulse with the engine's Condition.allConditionsMet (what RegeneratingValue.shouldRegenerate
    checks). dt 1/30 s, Mana 100 / 100000 (nothing caps), Mana Regen +20 %, in-combat 50 %. Steps (ticks):
      O 0-59 out of combat | C 60-119 charging, out of combat | CI 120-179 hit at 120: charging in combat | I 180-239 in combat |
      D 240-269 dead + charging | DN 270-299 dead | R 300-359 alive, out of combat (the hit at 120 is 6 s old at 300) |
      Z 360-419 no boosts + in-combat 0 %, charging out of combat (0.4.12 returned before reading anything at 0 % + no boosts) |
      ZI 420-479 hit at 420: charging in combat at 0 %
    Per pulse: [step, t, added (the addStatValue amount, 0 = none), secs (the pulse's Java-float seconds), vanilla (allConditionsMet),
    state, rates (5 on 0.4.13, 3 on 0.4.12), since (ns since the last hit, -1 never), charging, dead, Mana Regen %, in-combat %]"""
    from jpype import JClass, JFloat, JLong
    UUID, ChronoUnit = JClass("java.util.UUID"), JClass("java.time.temporal.ChronoUnit")
    Cond = JClass("com.hypixel.hytale.server.core.modules.entity.condition.Condition")
    Instant, setf, ESV, RGV = E["Instant"], E["setf"], E["ESV"], E["RGV"]
    tr, store, cb, fsm, mv, dd2 = E["tr"], E["store"], E["cb"], E["fsm"], E["mv"], E["dd2"]
    from jpype import JArray
    u = UUID(0xC4A, 1)
    Mana.CLK.clear()
    Mana.SRC.clear()
    Mana.IN_COMBAT = 50
    Mana.put(u, "Test", 20.0)
    store.ext = None
    cb.arch = E["Arch"].empty()
    dd2.setLastDamageTime(Instant.MIN)
    E["charging"].v = True
    setf(mv, ESV, "value", JFloat(100.0))
    setf(mv, ESV, "max", JFloat(100000.0))
    rg = E["vanilla"].getRegenerating()
    rv = JArray(RGV)([E["vanilla"]])
    dt = JFloat(1.0 / 30.0)
    nanos = JLong(int(float(dt) * 1.0e9))
    rows = []
    for t in range(480):
        tr.add(nanos, ChronoUnit.NANOS)
        step = ("O" if t < 60 else "C" if t < 120 else "CI" if t < 180 else "I" if t < 240 else "D" if t < 270 else "DN" if t < 300
                else "R" if t < 360 else "Z" if t < 420 else "ZI")
        if t == 60:
            E["charging"].v = False                                # charging
        if t == 120:
            dd2.setLastDamageTime(tr.getNow())
        if t == 180:
            E["charging"].v = True
        if t == 240:
            E["charging"].v = False
            cb.arch = E["Arch"].of(E["deathType"])
        if t == 270:
            E["charging"].v = True
        if t == 300:
            cb.arch = E["Arch"].empty()
        if t == 360:
            Mana.remove(u, "Test")
            Mana.IN_COMBAT = 0
            E["charging"].v = False
        if t == 420:
            dd2.setLastDamageTime(tr.getNow())
        c0 = int(fsm.calls)
        ck = Mana.CLK.get(u)
        c_before = float(ck[0]) if ck is not None else 0.0
        Mana.tick(u, store, cb, None, dt)
        added = 0.0
        if int(fsm.calls) != c0:
            added = float(fsm.last)
            setf(mv, ESV, "value", JFloat(min(float(mv.getMax()), max(0.0, float(mv.get()) + float(fsm.last)))))
        c = Mana.CLK.get(u)
        if c is not None and float(c[0]) == 0.0:
            now = tr.getNow()
            last = dd2.getLastDamageTime()
            since = -1 if last.equals(Instant.MIN) else int(last.until(now, ChronoUnit.NANOS))
            rows.append([step, t, added, min(1.0, f32(f32(c_before) + f32(float(dt)))), bool(Cond.allConditionsMet(cb, None, now, rg)),
                         int(Mana.state(cb, None, now, rg)), [float(x) for x in Mana.rates(cb, None, now, rv)], since,
                         not bool(E["charging"].v), 240 <= t < 300, float(Mana.total(u)), int(Mana.IN_COMBAT)])
        elif added != 0.0:
            rows.append([step, t, added, None, None, None, None, None, None, None, None, None])   # never: a refill off the pulse
    Mana.SRC.clear()
    Mana.IN_COMBAT = 50
    E["charging"].v = True
    cb.arch = E["Arch"].empty()
    return {"rows": rows, "warn": bool(Mana.FAILED_ONCE)}


# ============================================================================================ child: the 0.4.12 jar (baseline numbers)
def run_old(jar, out, fake, xs_file):
    from jpype import JClass, JLong
    res, path = common(jar, [fake])
    if not res["load_fails"]:
        D = res["data"]
        work = os.path.join(SCRATCH, "old")
        os.makedirs(work, exist_ok=True)
        defaults_part(D, JClass(PKG + "SkillCfg"), JClass(PKG + "CfgRows"), JClass(PKG + "BridgeXp"), path, work)
        Defs = JClass(PKG + "SkillDefs")
        Defs.setTable(Defs.DEFAULT_PER)
        Defs.setClassTable(Defs.DEFAULT_CPER, False)
        D["per"] = [int(x) for x in Defs.DEFAULT_PER]
        D["cum"] = [int(x) for x in Defs.CUM]
        D["cper"] = [int(x) for x in Defs.DEFAULT_CPER]
        D["ccum"] = [int(x) for x in Defs.CCUM]
        D["ecum"] = [int(x) for x in Defs.ECUM]
        xs = json.load(open(xs_file))
        D["xs"] = {}
        for s in T_SLOTS:
            D["xs"][str(s)] = [[int(Defs.levelOf(s, JLong(x))), int(Defs.intoLevel(s, JLong(x))), int(Defs.needFor(s, JLong(x))), str(Defs.progress(s, JLong(x)))] for x in xs]
        D["general"] = [int(Defs.generalLevel(JLong(x))) for x in xs]
        ENV, Mana = None, JClass(PKG + "ManaRegen")
        try:
            ENV = regen_env()
            D["E"] = tick_trace(ENV, Mana, False)
        except Exception as e:
            D["E"] = {"error": str(e)}
        # 0.4.13 fix round controls: the same world-switch and charging scripts on the 0.4.12 jar (the faults the fix removes)
        for k, f in (("Ysw", switch_trace), ("Hch", charge_trace)):
            try:
                D[k] = f(ENV, Mana, False)
            except Exception as e:
                D[k] = {"error": str(e)}
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: the 0.4.12 jar
def run_new(jar, out, fake, xs_file):
    from jpype import JClass, JFloat, JLong, JImplements, JOverride, JArray, JObject
    res, path = common(jar, [fake])
    if res["load_fails"]:
        json.dump(res, open(out, "w"), indent=1)
        return
    D = res["data"]
    UUID, CHM, Props = JClass("java.util.UUID"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Properties")
    Cfg, Xp, Store, Defs = JClass(PKG + "SkillCfg"), JClass(PKG + "SkillXp"), JClass(PKG + "SkillStore"), JClass(PKG + "SkillDefs")
    Bx, Rows, Kit, Curve = JClass(PKG + "BridgeXp"), JClass(PKG + "CfgRows"), JClass(PKG + "SkillKit"), JClass(PKG + "ClassCurve")
    Mana, ManaFn, Ovl, Px, Msg = JClass(PKG + "ManaRegen"), JClass(PKG + "ManaRegenFn"), JClass(PKG + "Overall"), JClass(PKG + "PartyXp"), JClass(PKG + "SkillMsg")
    SkillFn, XpFn, OvFn, Top = JClass(PKG + "SkillFn"), JClass(PKG + "SkillXpFn"), JClass(PKG + "OverallFn"), JClass(PKG + "SkillTop")
    SkillsPage, StatsPage, OverallPage = JClass(PKG + "SkillsPage"), JClass(PKG + "StatsPage"), JClass(PKG + "OverallPage")
    Hist, CLog, Mig, HMig, CfgFn = JClass(PKG + "CfgHist"), JClass(PKG + "CfgLog"), JClass(PKG + "ManaMig"), JClass(PKG + "HealMig"), JClass(PKG + "CfgFn")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Universe, Holder = JClass("com.hypixel.hytale.server.core.universe.Universe"), JClass("com.hypixel.hytale.component.Holder")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    FakeH, FakeW, Fixed, FakeAcc = JClass("skyytest.FakeHandler"), JClass("skyytest.FakeWorld"), JClass("skyytest.FixedCondition"), JClass("skyytest.FakeAcc")
    JDouble, JBool, JLongC, JObj, JInt = JClass("java.lang.Double"), JClass("java.lang.Boolean"), JClass("java.lang.Long"), JClass("java.lang.Object"), JClass("java.lang.Integer")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    def getf(obj, cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f.get(obj)

    @JImplements("java.util.function.Function")
    class Const(object):
        def __init__(self, v):
            self.v = v

        @JOverride
        def apply(self, o):
            return self.v

    COINS = []

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, o):
            COINS.append([str(o[0]), int(o[1])])
            return JLongC(1000000 + sum(c[1] for c in COINS))

    ACTIVE = {}

    @JImplements("java.util.function.Function")
    class PKey(object):
        @JOverride
        def apply(self, o):
            k = ACTIVE.get(str(o))
            return k if k is not None else str(o)

    bridge = Store.bridge()
    work = os.path.join(SCRATCH, "new")
    os.makedirs(work, exist_ok=True)
    defaults_part(D, Cfg, Rows, Bx, path, work)
    D["marker_heal"] = str(HMig.MG_MARK)
    D["curve_block"] = str(Cfg.CURVE_DEFAULTS)
    D["mreg_block"] = str(Cfg.MREG_DEFAULTS)

    # ---------------------------------------------------------------- T: the tables
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    T = {"cper": [int(x) for x in Defs.DEFAULT_CPER], "per": [int(x) for x in Defs.DEFAULT_PER], "ccum": [int(x) for x in Defs.CCUM],
         "cum": [int(x) for x in Defs.CUM], "ecum": [int(x) for x in Defs.ECUM], "maxes": [int(Defs.maxOf(s)) for s in range(16)],
         "cmax": int(Defs.CMAX), "max": int(Defs.MAX), "same": bool(Defs.SAME)}
    xs = json.load(open(xs_file))
    T["xs"] = {}
    for s in (MINING, 4, 3, COOKING, EXPLORATION, ARCHERY, DIVINITY, WARRIOR):
        T["xs"][str(s)] = [[int(Defs.levelOf(s, JLong(x))), int(Defs.intoLevel(s, JLong(x))), int(Defs.needFor(s, JLong(x))), str(Defs.progress(s, JLong(x)))] for x in xs]
    T["general"] = [int(Defs.generalLevel(JLong(x))) for x in xs]
    D["T"] = T

    # ---------------------------------------------------------------- G: the guard
    G = {}
    steep = [1000] * 100                                          # level 1 needs 1000 (general 50) ... level 100 = 100,000 total
    Defs.setClassTable(JArray(JLong)(steep), False)
    G["steep"] = [[int(Defs.levelOf(DIVINITY, JLong(x))), int(Defs.generalLevel(JLong(x))), int(Defs.levelIn(Defs.CCUM, JLong(x)))] for x in xs[::7]]
    G["steep_ecum"] = [int(x) for x in Defs.ECUM]
    Defs.setClassTable(JArray(JLong)([int(x) for x in Defs.DEFAULT_CPER][:60]), False)
    G["cut60"] = [int(Defs.maxOf(DIVINITY)), int(Defs.levelOf(DIVINITY, JLong(10 ** 12))), int(Defs.maxOf(MINING)), int(Defs.needFor(DIVINITY, JLong(10 ** 12))),
                  str(Defs.progress(DIVINITY, JLong(10 ** 12)))]
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    Defs.setTable(JArray(JLong)([int(x) for x in Defs.DEFAULT_PER][:50]))
    G["gen50"] = [int(Defs.maxOf(MINING)), int(Defs.maxOf(DIVINITY)), int(Defs.levelOf(DIVINITY, JLong(929090))), int(Defs.levelOf(MINING, JLong(10 ** 12))),
                  int(Defs.levelOf(DIVINITY, JLong(21540)))]
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, True)
    G["same"] = all(int(Defs.levelOf(s, JLong(x))) == int(Defs.generalLevel(JLong(x))) for s in CLASS_SLOTS for x in xs[::5]) and \
        [int(x) for x in Defs.ECUM] == [int(x) for x in Defs.CUM]
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    G["back"] = [int(x) for x in Defs.ECUM] == [int(x) for x in Defs.CCUM]
    D["G"] = G

    # ---------------------------------------------------------------- stand-ins: Universe, world, players
    uni = U.allocateInstance(Universe.class_)
    PLAYERS, WORLDS = CHM(), CHM()
    setf(uni, Universe, "playersByUuid", PLAYERS)
    setf(uni, Universe, "players", PLAYERS.values())
    setf(uni, Universe, "worldsByUuid", WORLDS)
    setf(None, Universe, "instance", uni)
    world = U.allocateInstance(FakeW.class_)
    wuid = UUID(0x3012D, 1)
    WORLDS.put(wuid, world)
    handler = U.allocateInstance(FakeH.class_)
    holder = U.allocateInstance(Holder.class_)
    TEXTS = getf(None, FakeH, "TEXTS")

    def mkpr(u, name):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", u)
        setf(pr, PRef, "username", name)
        setf(pr, PRef, "packetHandler", handler)
        setf(pr, PRef, "worldUuid", wuid)
        setf(pr, PRef, "holder", holder)
        PLAYERS.put(u, pr)
        return pr

    def texts():
        out = [str(t) for t in TEXTS]
        TEXTS.clear()
        return out

    def fresh_store(players_dir):
        Store.DATA.clear()
        Store.DIRTY.clear()
        Store.QUIET.clear()
        Store.OWNER.clear()
        Store.PUBLISHED.clear()
        Store.DIR = path(players_dir)
        for i in range(len(Top.CACHE)):
            Top.CACHE[i] = None
            Top.AT[i] = 0

    def load_cfg(d, text=None):
        f = os.path.join(d, "xp.properties")
        if text is not None:
            os.makedirs(d, exist_ok=True)
            open(f, "wb").write(text)
        Cfg.FILE = path(f)
        return str(Cfg.load())

    def page_texts(pg):
        b, ev = UCB(), UEB()
        err = None
        try:
            pg.build(None, b, ev, None)
        except Exception as e:
            err = str(e)
        return err, [str(c.data) for c in b.getCommands() if c.data is not None]

    def has(lst, sub):
        return any(sub in x for x in lst)

    # ---------------------------------------------------------------- P: per-slot everywhere
    P = {}
    pdir = os.path.join(SCRATCH, "p-players")
    os.makedirs(pdir, exist_ok=True)
    load_cfg(os.path.join(SCRATCH, "p-cfg"), b"multiplier=1.0\n")
    uP = UUID(0x5117, 15)
    keyP = str(uP)
    open(os.path.join(pdir, keyP + ".properties"), "wb").write(
        ("name=Pria\nCombat.Priest=67425\nCombat.Priest.paid=15\nMining=67425\nMining.paid=15\nCombat.Archer=1000\nCombat.Archer.paid=4\n").encode("latin-1"))
    for k in ("u2", "u3"):
        pass
    open(os.path.join(pdir, "aaaaaaaa-0000-0000-0000-000000000001.properties"), "wb").write(b"name=Alex\nCombat.Priest=21540\nCombat.Priest.paid=20\n")
    fresh_store(pdir)
    prP = mkpr(uP, "Pria")
    bridge.put("class:" + keyP, "Priest")
    bridge.put("class:fn:allowed", Const(JBool.TRUE))
    bridge.put("coins:fn:add", Coins())
    P["level"] = [int(Store.level(uP, DIVINITY)), int(Store.level(uP, MINING)), int(Store.level(uP, ARCHERY))]
    sf, xf = SkillFn(), XpFn()
    P["fn_level"] = dict((n, int(sf.apply(JObj[:]([uP, n])))) for n in ("Divinity", "Priest", "Combat", "Mining", "Archery", "div"))
    P["fn_level"]["Overall"] = int(sf.apply(JObj[:]([uP, "Overall"])))
    P["fn_xp"] = [int(xf.apply(JObj[:]([uP, "Divinity"]))), int(xf.apply(JObj[:]([uP, "Mining"])))]
    P["levels"] = str(Store.levelsString(uP))
    ov = OvFn().apply(uP)
    P["overall"] = [int(ov[0]), int(ov[1]), int(ov[2])]
    P["ovmax"] = int(Ovl.maxLevel(uP))
    err, cmds = page_texts(SkillsPage(prP))
    P["skills_page"] = [err, has(cmds, "Divinity  28"), has(cmds, "Mining  15"), has(cmds, "XP to level 29"), has(cmds, "XP to level 16"),
                        has(cmds, "Overall Level ")]
    err, cmds = page_texts(StatsPage(prP, DIVINITY))
    P["stats_page"] = [err, has(cmds, "Divinity - level 28 of 100"), has(cmds, "XP to level 29")]
    err, cmds = page_texts(StatsPage(prP, MINING))
    P["stats_mining"] = [err, has(cmds, "Mining - level 15 of 100"), has(cmds, "XP to level 16")]
    sp = SkillsPage(prP)
    sp.view = DIVINITY
    err, cmds = page_texts(sp)
    P["top_page"] = [err, has(cmds, "Level 28"), has(cmds, "Level 20"), has(cmds, "Your rank #1 of 2 - level 28")]
    err, cmds = page_texts(OverallPage(prP))
    P["overall_page"] = [err, has(cmds, "Level %d of %d" % (P["overall"][0], P["ovmax"])), has(cmds, "Divinity 28 (your class)")]
    texts()
    Msg.PEND.clear()
    Msg.LAST.clear()
    Msg.note(prP, DIVINITY, 100)                      # the first note is due: sent at once
    P["msg"] = texts()
    Msg.note(prP, MINING, 1)                          # inside feedbackMs: pending, read back with take()
    P["msg_take"] = str(Msg.take(uP))
    Px.drop(uP)
    Px.add(uP, DIVINITY, 6, "Skyy")
    P["party"] = str(Px.take(uP))
    # a real level up on the class table: Alex 21,540 Divinity XP = 20 already; Pria to exactly 21,540 from 21,539
    Store.DATA.get(keyP)[DIVINITY] = 21539
    Store.DATA.get(keyP)[16 + DIVINITY] = 19
    COINS[:] = []
    texts()
    Xp.gain3(prP, DIVINITY, 1, False, False)
    P["levelup"] = {"texts": texts(), "coins": list(COINS), "paid": int(Store.DATA.get(keyP)[16 + DIVINITY]), "level": int(Store.level(uP, DIVINITY))}
    Store.DATA.get(keyP)[MINING] = 9924
    Store.DATA.get(keyP)[16 + MINING] = 9
    COINS[:] = []
    Xp.gain3(prP, MINING, 1, False, False)
    P["levelup_mining"] = {"texts": texts(), "coins": list(COINS)}
    D["P"] = P

    # ---------------------------------------------------------------- M: ClassCurve on scratch copies
    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)

    def start(d):
        """the plugin's setup order: ManaMig.run -> HealMig.run -> SkillCfg.load -> ClassCurve.start (+ the kit's history init)"""
        Cfg.FILE = path(os.path.join(d, "xp.properties"))
        fresh_store(os.path.join(d, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        mr = [str(x) for x in Mig.run()]
        hr = str(HMig.run())
        lt = str(Cfg.load())
        cr = str(Curve.start(path(d)))
        return {"mana": mr, "heal": hr, "load": lt, "curve": cr, "ready": bool(Curve.READY), "pending": dict((str(k), str(v)) for k, v in Curve.PENDING.items()),
                "done": dict((str(k), str(v)) for k, v in Curve.DONE.items())}

    M = {}
    bridge.remove("class:fn:allowed")
    lc = os.path.join(SCRATCH, "live-copy")
    s0 = snap(lc)
    r1 = start(lc)
    s1 = snap(lc)
    r2 = start(lc)
    s2 = snap(lc)
    M["live"] = {"r1": r1, "r2": r2, "changed1": sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k)),
                 "changed2": sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k)),
                 "players_same": all(s0[k] == s2.get(k) for k in s0 if k.startswith("players/")),
                 "xp_append": s1["xp.properties"] == s0["xp.properties"] + b"\n" + D["curve_block"].encode("latin-1") + b"\n" + D["mreg_block"].encode("latin-1"),
                 "xp_same": s1["xp.properties"] == s0["xp.properties"] == s2["xp.properties"],
                 "blocks_there": D["curve_block"].encode("latin-1") in s0["xp.properties"].replace(b"\r\n", b"\n")
                 and D["mreg_block"].encode("latin-1") in s0["xp.properties"].replace(b"\r\n", b"\n"),
                 "record": s1.get("class-curve.properties", b"").decode("latin-1"), "n_players": len([k for k in s0 if k.startswith("players/")])}
    # (2) an edited copy: three risen profiles of one player (u2 profile 1 Priest 67,425 = 15 -> 28; profile 2 Archer 522,425 = 20 -> 51,
    # profile 3 Archer 1,000 = 4 -> 5 = the crossbow unlock level) + Skyy's real files
    ed = os.path.join(SCRATCH, "mig-edit")
    shutil.copytree(lc, ed)
    os.remove(os.path.join(ed, "class-curve.properties"))
    u2 = UUID(0xABC, 2)
    k1, k2, k3 = str(u2), str(u2) + "-p2", str(u2) + "-p3"
    open(os.path.join(ed, "players", k1 + ".properties"), "wb").write(b"name=Tester\nCombat.Priest=67425\nCombat.Priest.paid=15\nMining=67425\nMining.paid=15\n")
    open(os.path.join(ed, "players", k2 + ".properties"), "wb").write(b"name=Tester\nCombat.Archer=522425\nCombat.Archer.paid=20\n")
    open(os.path.join(ed, "players", k3 + ".properties"), "wb").write(b"name=Tester\nCombat.Archer=1000\nCombat.Archer.paid=4\n")
    pr2 = mkpr(u2, "Tester")
    bridge.put("profile:fn:key", PKey())
    bridge.put("class:fn:allowed", Const(JBool.TRUE))
    bridge.put("class:" + k1, "Priest")
    ACTIVE[k1] = k1
    e1 = start(ed)
    rec1 = open(os.path.join(ed, "class-curve.properties"), "rb").read().decode("latin-1")
    COINS[:] = []
    texts()
    Curve.tick(pr2, u2)
    t1 = texts()
    c1 = list(COINS)
    paid1 = int(Store.dataK(k1, u2)[16 + DIVINITY])
    disk_before = open(os.path.join(ed, "players", k1 + ".properties"), "rb").read().decode("latin-1")
    Curve.flush()
    disk_after = open(os.path.join(ed, "players", k1 + ".properties"), "rb").read().decode("latin-1")
    rec2 = open(os.path.join(ed, "class-curve.properties"), "rb").read().decode("latin-1")
    COINS[:] = []
    Curve.tick(pr2, u2)
    t2 = texts()
    c2 = list(COINS)
    Xp.gain3(pr2, DIVINITY, 5, False, False)          # a later small award: no level crossed, nothing more paid
    t3 = texts()
    c3 = list(COINS)
    M["edit1"] = {"start": e1, "rec1": rec1, "t1": t1, "c1": c1, "paid1": paid1, "disk_paid_before": "Combat.Priest.paid=28" in disk_before,
                  "disk_paid_after": "Combat.Priest.paid=28" in disk_after, "rec2": rec2, "t2": t2, "c2": c2, "t3": t3, "c3": c3}
    # restart (fresh statics from the file): k1 done; k2 / k3 still pending; k2 becomes active
    e2 = start(ed)
    ACTIVE[str(u2)] = k2
    bridge.put("class:" + str(u2), "Archer")
    COINS[:] = []
    texts()
    Curve.tick(pr2, u2)
    t4 = texts()
    c4 = list(COINS)
    Curve.flush()
    ACTIVE[str(u2)] = k3
    COINS[:] = []
    Curve.tick(pr2, u2)
    t5 = texts()
    c5 = list(COINS)
    Curve.flush()
    e3 = start(ed)
    ACTIVE[str(u2)] = k1
    bridge.put("class:" + str(u2), "Priest")
    COINS[:] = []
    for _ in range(3):
        Curve.tick(pr2, u2)
    t6 = texts()
    c6 = list(COINS)
    sE = snap(ed)
    M["edit2"] = {"start2": e2, "t4": t4, "c4": c4, "t5": t5, "c5": c5, "start3": e3, "t6": t6, "c6": c6,
                  "rec3": sE.get("class-curve.properties", b"").decode("latin-1"),
                  "disk": dict((k, sE["players/" + k + ".properties"].decode("latin-1")) for k in (k1, k2, k3))}
    # (3) profile:busy waits, then delivers
    bz = os.path.join(SCRATCH, "mig-busy")
    shutil.copytree(lc, bz)
    os.remove(os.path.join(bz, "class-curve.properties"))
    u3 = UUID(0xABC, 3)
    open(os.path.join(bz, "players", str(u3) + ".properties"), "wb").write(b"name=Busy\nCombat.Priest=67425\nCombat.Priest.paid=15\n")
    pr3 = mkpr(u3, "Busy")
    bridge.put("class:" + str(u3), "Priest")
    start(bz)
    bridge.put("profile:busy:" + str(u3), JBool.TRUE)
    texts()
    Curve.tick(pr3, u3)
    b1 = [texts(), str(u3) in [str(k) for k in Curve.PENDING.keySet()]]
    bridge.remove("profile:busy:" + str(u3))
    Curve.tick(pr3, u3)
    b2 = [texts(), str(u3) in [str(k) for k in Curve.PENDING.keySet()]]
    M["busy"] = {"while": b1, "after": b2}
    # (4) the record cannot be written (a FOLDER named class-curve.properties): nobody told, the next start scans again
    nw = os.path.join(SCRATCH, "mig-nowrite")
    shutil.copytree(lc, nw)
    os.remove(os.path.join(nw, "class-curve.properties"))
    open(os.path.join(nw, "players", str(u3) + ".properties"), "wb").write(b"name=Busy\nCombat.Priest=67425\nCombat.Priest.paid=15\n")
    os.makedirs(os.path.join(nw, "class-curve.properties.tmp", "x"))
    w1 = start(nw)
    texts()
    Curve.tick(pr3, u3)
    w_t = texts()
    w_rec = os.path.exists(os.path.join(nw, "class-curve.properties"))
    shutil.rmtree(os.path.join(nw, "class-curve.properties.tmp"))
    w2 = start(nw)
    M["nowrite"] = {"w1": w1, "t": w_t, "w2": w2, "rec": w_rec}
    # (5) SkyyCoins missing: the line once, the coins stay owed (paid marker unchanged) for the normal late payout
    nc = os.path.join(SCRATCH, "mig-nocoins")
    shutil.copytree(lc, nc)
    os.remove(os.path.join(nc, "class-curve.properties"))
    open(os.path.join(nc, "players", str(u3) + ".properties"), "wb").write(b"name=Busy\nCombat.Priest=67425\nCombat.Priest.paid=15\n")
    start(nc)
    bridge.remove("coins:fn:add")
    texts()
    Curve.tick(pr3, u3)
    n_t1 = texts()
    n_paid = int(Store.dataK(str(u3), u3)[16 + DIVINITY])
    bridge.put("coins:fn:add", Coins())
    COINS[:] = []
    Curve.tick(pr3, u3)
    n_t2 = texts()
    Xp.gain3(pr3, DIVINITY, 1, False, False)
    n_t3 = texts()
    M["nocoins"] = {"t1": n_t1, "paid": n_paid, "t2": n_t2, "t3": n_t3, "coins": list(COINS), "paid_after": int(Store.dataK(str(u3), u3)[16 + DIVINITY])}
    M["test_keys"] = [k1, k2, k3, str(u3)]
    M["real_keys"] = sorted(fn[:-11] for fn in os.listdir(os.path.join(lc, "players")) if fn.endswith(".properties"))
    D["M"] = M

    # ---------------------------------------------------------------- R: Mana regen maths
    R = {}

    def amt(r, pct, f, secs, cur, mx):
        return round(float(Mana.amount(JArray(JFloat)(r), pct, f, JFloat(secs), JFloat(cur), JFloat(mx))), 5)
    R["amount"] = {
        "out0": amt([5, 5, 0], 0.0, 50, 1.0, 10, 30), "out20": amt([5, 5, 0], 20.0, 50, 1.0, 10, 30), "out20_pulse": amt([5, 5, 0], 20.0, 50, 0.2, 10, 30),
        "in0": amt([5, 0, 5], 0.0, 50, 1.0, 10, 30), "in0_pulse": amt([5, 0, 5], 0.0, 50, 0.2, 10, 30), "in20": amt([5, 0, 5], 20.0, 50, 1.0, 10, 30),
        "in_f0": amt([5, 0, 5], 20.0, 0, 1.0, 10, 30), "out_f0": amt([5, 5, 0], 20.0, 0, 1.0, 10, 30), "in_f100": amt([5, 0, 5], 0.0, 100, 1.0, 10, 30),
        "cap": amt([5, 0, 5], 0.0, 100, 1.0, 29.9, 30), "full": amt([5, 0, 5], 0.0, 50, 1.0, 30, 30), "nomana": amt([5, 0, 5], 50.0, 50, 1.0, 0, 0),
        "charging": amt([5, 0, 0], 50.0, 50, 1.0, 10, 30), "neg": amt([5, 5, 0], -40.0, 50, 1.0, 10, 30), "neg_in": amt([5, 0, 5], -40.0, 50, 1.0, 10, 30),
        "big": amt([5, 5, 0], 5000.0, 50, 1.0, 0, 10000), "nan": amt([5, 5, 0], float("nan"), 50, 1.0, 10, 30), "f150": amt([5, 0, 5], 0.0, 150, 1.0, 10, 30),
        "secs0": amt([5, 0, 5], 0.0, 50, 0.0, 10, 30)}
    tot = 0.0
    for _ in range(30):                                            # 6 s in combat in vanilla's 0.2 s pulses at 50%: 15 Mana
        tot += float(Mana.amount(JArray(JFloat)([5, 0, 5]), 0.0, 50, JFloat(0.2), JFloat(0.0 + tot), JFloat(100.0)))
    R["six_seconds"] = round(tot, 4)
    # the real engine conditions (regen_env: the module singletons so DamageDataComponent / DeathComponent / EntityStatMap / TimeResource
    # types resolve, NoDamageTakenCondition 6 s, the charging stand-in, vanilla's entry, a FakeAcc with a real DamageDataComponent)
    ENV = regen_env()
    R["stubs"] = ENV["stubs"]
    Arch, DDC, NDT, RGN, RGT, RGV = ENV["Arch"], ENV["DDC"], ENV["NDT"], ENV["RGN"], ENV["RGT"], ENV["RGV"]
    Instant, Duration, deathType = ENV["Instant"], ENV["Duration"], ENV["deathType"]
    nodmg, charging, entry, vanilla, now, acc, dd = ENV["nodmg"], ENV["charging"], ENV["entry"], ENV["vanilla"], ENV["now"], ENV["acc"], ENV["dd"]

    def rates(entries, hit_ago_ms, charge_ok=True, dead=False):
        dd.setLastDamageTime(now.minusMillis(hit_ago_ms))
        charging.v = charge_ok
        acc.arch = Arch.of(deathType) if dead else Arch.empty()
        try:
            return [round(float(x), 4) for x in Mana.rates(acc, None, now, JArray(RGV)(entries))]
        except Exception as e:
            return "error: %s" % e
    R["rates"] = {"out": rates([vanilla], 10000), "in": rates([vanilla], 2000), "edge6": rates([vanilla], 6000), "edge5999": rates([vanilla], 5999),
                  "in_charging": rates([vanilla], 2000, charge_ok=False), "out_charging": rates([vanilla], 10000, charge_ok=False),
                  "dead": rates([vanilla], 10000, dead=True), "dead_in": rates([vanilla], 2000, dead=True),
                  "pct_entry": rates([vanilla, entry(1.0, 0.5, RGT.PERCENTAGE, [])], 10000),
                  "zero_entry": rates([vanilla, entry(0.0, 0.2, RGT.ADDITIVE, [])], 10000),
                  "no_conds": rates([entry(2.0, 1.0, RGT.ADDITIVE, None)], 2000),
                  "two": rates([vanilla, entry(1.0, 1.0, RGT.ADDITIVE, [nodmg])], 2000)}

    def state(hit_ago_ms, charge_ok=True):
        dd.setLastDamageTime(now.minusMillis(hit_ago_ms))
        charging.v = charge_ok
        acc.arch = Arch.empty()
        return int(Mana.state(acc, None, now, vanilla.getRegenerating()))
    R["rates"]["state"] = [state(10000), state(2000), state(2000, False), state(10000, False)]
    # mana.regen.inCombat in the loader
    R["cfg"] = {}
    for name, line, in (("default", None), ("150", b"mana.regen.inCombat=150\n"), ("neg", b"mana.regen.inCombat=-5\n"),
                        ("abc", b"mana.regen.inCombat=abc\n"), ("zero", b"mana.regen.inCombat=0\n"), ("25", b"mana.regen.inCombat=25\n")):
        dd_ = os.path.join(SCRATCH, "r-cfg-" + name)
        load_cfg(dd_, b"multiplier=1.0\n" + (line or b""))
        R["cfg"][name] = int(Mana.IN_COMBAT)
    D["R"] = R

    # ---------------------------------------------------------------- B: skill:fn:manaregen
    Bq = {}
    fn = ManaFn()
    ub = UUID(0x8888, 1)
    Mana.SRC.clear()

    def call(*a):
        r = fn.apply(JObj[:](list(a)))
        if r is None:
            return None
        cn = str(r.getClass().getName())
        if cn == "java.lang.Double":
            return float(r.doubleValue())
        if cn == "java.lang.Integer":
            return int(r.intValue())
        if cn == "java.lang.Boolean":
            return "true" if r.booleanValue() else "false"
        if cn == "[Ljava.lang.String;":
            return [str(x) for x in r]
        return "?" + cn
    Bq["seq"] = [call("get", ub), call("add", ub, "SkyyGear", JDouble(15.0)), call("add", ub, "SkyyAccessories", JInt(5)), call("get", ub),
                 call("sources", ub), call("add", ub, "SkyyGear", JDouble(20.0)), call("get", ub), call("remove", ub, "SkyyGear"), call("get", ub),
                 call("remove", ub, "SkyyGear"), call("add", ub, "Arcane", JDouble(-30.0)), call("get", ub), call("add", ub, "Arcane", JDouble(0.0)),
                 call("sources", ub)]
    Bq["bad"] = [call("add", ub, "", JDouble(5.0)), call("add", ub, "x" * 65, JDouble(5.0)), call("add", ub, "nan", JDouble(float("nan"))),
                 call("add", "not-a-uuid", "src", JDouble(5.0)), call("add", ub, "src"), call("remove", ub), call("get", "nope"), call("frob", ub),
                 fn.apply("not an array") is None, call("sources", None)]
    Mana.SRC.clear()
    call("add", ub, "Big", JDouble(5000.0))
    Bq["clamp"] = [call("get", ub), call("sources", ub)]
    u4 = UUID(0x8888, 2)
    call("add", u4, "Big", JDouble(10.0))
    Bq["clear"] = [call("clear", "Big"), call("get", ub), call("get", u4), call("clear", JInt(3))]
    Mana.SRC.clear()
    call("add", ub, "SkyyGear", JDouble(20.0))
    Mana.IN_COMBAT = 50
    Bq["action"] = [str(x) for x in Mana.showAction(ub, "Skyy")]
    Bq["action_null"] = [str(x) for x in Mana.showAction(None, "console")]
    Bq["types"] = [str(fn.apply(JObj[:](["get", ub])).getClass().getName()), str(fn.apply(JObj[:](["add", ub, "a", JDouble(1.0)])).getClass().getName()),
                   str(fn.apply(JObj[:](["clear", "a"])).getClass().getName()), str(fn.apply(JObj[:](["sources", ub])).getClass().getName())]
    Bq["total_feeds"] = round(float(Mana.amount(JArray(JFloat)([5, 0, 5]), Mana.total(ub), 50, JFloat(1.0), JFloat(0.0), JFloat(30.0))), 4)
    Mana.SRC.clear()
    D["B"] = Bq

    # ---------------------------------------------------------------- W: the combat state + skill:fn:combat (0.4.13)
    import time as _time
    W = {}
    Sys = JClass("java.lang.System")
    W["window0"] = int(Mana.WINDOW)                                # nothing was in combat in this JVM yet
    Mana.CMB.clear()
    Mana.NDLY.clear()

    def cl(entries, ago_ns, charge_ok=True, dead=False, last=None, a=None):
        a = a or acc
        dd.setLastDamageTime(last if last is not None else now.minusNanos(JLong(ago_ns)))
        charging.v = charge_ok
        a.arch = Arch.of(deathType) if dead else Arch.empty()
        return int(Mana.combatLeft(a, None, now, JArray(RGV)(entries)))

    def st_(entries_rg=None):
        return int(Mana.state(acc, None, now, (entries_rg or vanilla).getRegenerating()))
    W["never"] = [cl([vanilla], 0, last=Instant.MIN), st_(), int(Mana.WINDOW), int(Mana.NDLY.size())]
    # the Delay asked from the condition: needs a real hit (the accessor's lastDamageTime = the last argument), then cached per object
    dd.setLastDamageTime(Instant.MIN)
    d_min = int(Mana.delayOf(nodmg, acc, None, Instant.MIN))
    L0 = now.minusSeconds(1)
    dd.setLastDamageTime(L0)
    d_real = int(Mana.delayOf(nodmg, acc, None, L0))
    W["delay"] = [d_min, d_real, int(Mana.NDLY.size()), int(Mana.delayOf(nodmg, acc, None, Instant.MIN))]
    edges = (0, 1, 999999, 1000000, 1000001, 2000000000, 5999000000, 5999000001, 5999999999, 6000000000, 6000000001, 7000000000,
             10000000000, 3600000000000)
    W["edges"] = [[ns, cl([vanilla], ns)] for ns in edges]
    W["window1"] = int(Mana.WINDOW)
    # the sweep: every 1 ms from 0 to 6.1 s, the nanosecond edges around 6 s and 400 random instants - combatLeft against the Mana
    # regen's own test (state 1), its in-combat rate, the NoDamageTaken condition itself, and the exact ceiling
    rnd = random.Random(413)
    agos = list(range(0, 6100000001, 1000000)) + [NDT_NS + k for k in range(-5, 6)] + [rnd.randrange(0, 7000000000) for _ in range(400)]
    bad, n_in = [], 0
    vrg = JArray(RGV)([vanilla])
    charging.v = True
    acc.arch = Arch.empty()
    for ns in agos:
        dd.setLastDamageTime(now.minusNanos(JLong(ns)))
        left = int(Mana.combatLeft(acc, None, now, vrg))
        stt = int(Mana.state(acc, None, now, vanilla.getRegenerating()))
        rin = float(Mana.rates(acc, None, now, vrg)[2])
        ndt_ok = bool(nodmg.eval(acc, None, now))
        want = 0 if ns >= NDT_NS else -(-(NDT_NS - ns) // 1000000)
        n_in += 1 if left > 0 else 0
        if not ((left > 0) == (stt == 1) == (rin > 0.0) == (not ndt_ok)) or left != want:
            bad.append([ns, left, stt, rin, ndt_ok, want])
    W["sweep"] = {"n": len(agos), "in": n_in, "nbad": len(bad), "bad": bad[:8]}
    # charging / dead stop the refill (state 2), not the combat state
    W["charging"] = [cl([vanilla], 2000000000, charge_ok=False), st_()]
    W["dead"] = [cl([vanilla], 2000000000, dead=True), cl([vanilla], 10000000000, dead=True)]
    # another Delay in a second entry: the larger countdown wins; a Delay with nanoseconds rounds up; WINDOW follows the latest pulse
    e25 = entry(1.0, 1.0, RGT.ADDITIVE, [ENV["ndt"](Duration.ofMillis(2500))])
    e3n = entry(1.0, 1.0, RGT.ADDITIVE, [ENV["ndt"](Duration.ofNanos(3250000001))])
    W["two"] = [cl([vanilla, e25], 1000000000), int(Mana.WINDOW), cl([vanilla, e25], 5500000000), cl([e25, vanilla], 5500000000),
                cl([e25], 1000000000), int(Mana.WINDOW), cl([e25], 2500000000)]
    W["nanos"] = [cl([e3n], 0), int(Mana.WINDOW), cl([e3n], 3250000000), cl([e3n], 3250000001)]
    cl([vanilla], 0)                                               # WINDOW back to vanilla's 6000
    # entries that never count: Percentage, zero amount, no conditions, conditions without a NoDamageTaken
    W["never_count"] = [cl([entry(1.0, 0.5, RGT.PERCENTAGE, [nodmg])], 0), cl([entry(0.0, 0.2, RGT.ADDITIVE, [nodmg])], 0),
                        cl([entry(2.0, 1.0, RGT.ADDITIVE, None)], 0), cl([entry(1.0, 0.2, RGT.ADDITIVE, [ENV["Alive"](False), charging])], 0),
                        int(Mana.combatLeft(acc, None, now, None)), int(Mana.combatLeft(acc, None, None, vrg))]
    # a failing accessor (no DamageDataComponent: the condition throws): combat() drops the entry and logs once - never throws
    FakeAcc_ = JClass("skyytest.FakeAcc")
    abad = FakeAcc_()
    abad.dd = None
    abad.arch = Arch.empty()
    ubad = UUID(0xC0B, 9)
    Mana.CMB.put(ubad, JArray(JLong)([5000, int(Sys.currentTimeMillis())]))
    f0 = bool(Mana.CFAILED_ONCE)
    err = None
    try:
        Mana.combat(ubad, abad, None, now, vrg)
    except Exception as e:
        err = str(e)
    W["bad_acc"] = [f0, bool(Mana.CFAILED_ONCE), bool(Mana.CMB.containsKey(ubad)), err]
    Mana.combat(None, acc, None, now, vrg)                         # no player: nothing
    # the bridge Function itself
    CFn = JClass(PKG + "CombatFn")
    fnc = CFn()
    uc, uo = UUID(0xC0B, 1), UUID(0xC0B, 2)
    Mana.CMB.clear()

    def bval(x):
        r = fnc.apply(x)
        return None if r is None else [str(r.getClass().getName()), int(r.longValue())]
    W["fn_before"] = [bval(uc), bval(uo)]
    dd.setLastDamageTime(now)                                      # a pulse exactly at the hit
    charging.v = True
    acc.arch = Arch.empty()
    Mana.combat(uc, acc, None, now, vrg)
    e = Mana.CMB.get(uc)
    W["entry"] = None if e is None else [int(e[0]), int(e[1]) > 0]
    W["fn_after"] = bval(uc)
    W["fn_forms"] = [bval("window"), bval(" Window "), bval(JObj[:]([uc])), bval(JObj[:](["window"])), bval(uo)]
    W["fn_bad"] = [fnc.apply(None) is None, fnc.apply("nope") is None, fnc.apply(JInt(3)) is None, fnc.apply(JObj[:]([])) is None,
                   fnc.apply(JObj[:]([None])) is None]
    # pulse by pulse: the world clock moves 0.2 s a pulse; each answer read at its own pulse's wall time; state() at the same instant
    seq = []
    for k in range(36):
        nk = now.plusMillis(200 * k)
        Mana.combat(uc, acc, None, nk, vrg)
        e = Mana.CMB.get(uc)
        v = int(Mana.combatNow(uc, JLong(int(e[1])))) if e is not None else int(fnc.apply(uc).longValue())
        seq.append([k, v, int(Mana.state(acc, None, nk, vanilla.getRegenerating())), e is not None])
    W["pulses"] = seq
    # between pulses: the wall clock counts down; >= 1 while the pulse is fresh (<= STALE_MS); stale and run out = 0 + dropped
    Mana.CMB.put(uc, JArray(JLong)([3000, 1000000]))
    W["wall"] = [int(Mana.combatNow(uc, JLong(w))) for w in (1000000, 1000500, 1000999, 1001000, 1001001, 1002900, 999000)] + [bool(Mana.CMB.containsKey(uc))]
    W["wall_out"] = [int(Mana.combatNow(uc, JLong(1003000))), bool(Mana.CMB.containsKey(uc))]
    Mana.CMB.put(uc, JArray(JLong)([150, 1000000]))
    W["floor"] = [int(Mana.combatNow(uc, JLong(w))) for w in (1000100, 1000149, 1000150, 1000300, 1001000)] + [int(Mana.combatNow(uc, JLong(1001001))),
                                                                                                         bool(Mana.CMB.containsKey(uc))]
    W["consts"] = [int(Mana.STALE_MS), int(Mana.NDLY_CAP)]
    # the real wall clock through the Function: read, wait 0.3 s, read again
    dd.setLastDamageTime(now)
    Mana.combat(uc, acc, None, now, vrg)
    v1 = int(fnc.apply(uc).longValue())
    _time.sleep(0.3)
    v2 = int(fnc.apply(uc).longValue())
    W["real"] = [v1, v2]
    # an out-of-combat pulse removes the entry
    dd.setLastDamageTime(now.minusSeconds(10))
    Mana.combat(uc, acc, None, now, vrg)
    W["out_removes"] = [bool(Mana.CMB.containsKey(uc)), bval(uc)]
    W["window_end"] = [int(Mana.WINDOW), bval("window")]
    D["W"] = W

    # ---------------------------------------------------------------- E: the real ManaRegen.tick end to end (0.4.12 jar too: run_old)
    try:
        D["E"] = tick_trace(ENV, Mana, True)
    except Exception as e:
        D["E"] = {"error": str(e)}

    # ---------------------------------------------------------------- Y / H end to end: the 0.4.13 fix round (0.4.12 controls: run_old)
    for k, f in (("Ysw", switch_trace), ("Hch", charge_trace)):
        try:
            D[k] = f(ENV, Mana, True)
        except Exception as e:
            D[k] = {"error": str(e)}

    # ---------------------------------------------------------------- Y: ManaRegen.carried (pure) + the F2 prune
    Y = {}
    FloatC = JClass("java.lang.Float")

    def inst(v):
        if v is None:
            return None
        if v == "MIN":
            return Instant.MIN
        return Instant.ofEpochSecond(v // SEC, v % SEC)

    def jrec(r):
        if r is None:
            return None
        vals = []
        for k_, x in enumerate(r):
            if k_ == 0:
                vals.append(x)
            elif k_ == 2:
                vals.append(None if x is None else JLongC.valueOf(JLong(x)))
            elif k_ == 3:
                vals.append(None if x is None else FloatC.valueOf(JFloat(x)))
            else:
                vals.append(inst(x))
        return JArray(JObj)(vals)

    def car(s, wn, now_, dil, wall, r, i):
        x = Mana.carried(inst(s), wn, inst(now_), JFloat(dil), JLong(wall), jrec(r), i)
        return "keep" if x is None else _ns(x, Instant)
    try:
        Y["cases"] = [[c[0], car(*c[1:8])] for c in CARRY_CASES]
        smin = Instant.MIN.plusSeconds(1)                          # a stamp whose distance to any clock overflows a long of ns
        rmin = JArray(JObj)(["default", inst(CLK_A), JLongC.valueOf(JLong(W0)), FloatC.valueOf(JFloat(1.0)), smin, None, None])
        xo = Mana.carried(smin, "island", inst(CLK_B), JFloat(1.0), JLong(W0 + SEC), rmin, 0)
        Y["overflow"] = "keep" if xo is None else _ns(xo, Instant)
        Y["nsBetween"] = [int(Mana.nsBetween(Instant.MIN, inst(CLK_A))), int(Mana.nsBetween(inst(CLK_A), Instant.MIN)),
                          int(Mana.nsBetween(inst(CLK_B), inst(CLK_A)))]
        Y["random"] = [[c, car(*c)] for c in random_carry_cases(3000)]
        Y["consts"] = [int(Mana.CARRY_CAP), int(Mana.CARRY_SLACK)]
    except Exception as e:
        Y["error"] = str(e)
    # F2: Acro.retainOnline (the 30 s prune) keeps only online players in ManaRegen.CMB / CARRY / CLK (uP is online, uoff is not)
    try:
        AcroC = JClass(PKG + "Acro")
        uoff = UUID(0xDEAD, 7)
        for m_, mk_ in ((Mana.CMB, lambda: JArray(JLong)([4000, 1])), (Mana.CARRY, lambda: jrec(_rec("default", CLK_A, W0, 1.0))),
                        (Mana.CLK, lambda: JArray(JFloat)([0.0]))):
            m_.put(uoff, mk_())
            m_.put(uP, mk_())
        pre = [bool(Mana.CMB.containsKey(uoff)), bool(Mana.CARRY.containsKey(uoff)), bool(Mana.CLK.containsKey(uoff))]
        AcroC.retainOnline()
        Y["prune"] = {"pre": pre, "post": [bool(Mana.CMB.containsKey(uP)), bool(Mana.CMB.containsKey(uoff)), bool(Mana.CARRY.containsKey(uP)),
                                           bool(Mana.CARRY.containsKey(uoff)), bool(Mana.CLK.containsKey(uP)), bool(Mana.CLK.containsKey(uoff))]}
    except Exception as e:
        Y["prune"] = {"error": str(e)}
    Mana.CMB.clear()
    Mana.CARRY.clear()
    Mana.CLK.clear()
    D["Y"] = Y

    # ---------------------------------------------------------------- H: charging - state / rates / amount / stateLine + vanilla's entry
    H = {}
    FC, Cond = ENV["FixedCharging"], JClass("com.hypixel.hytale.server.core.modules.entity.condition.Condition")

    def ev(chg, ago_ns, dead=False, order=0):
        conds = [ENV["Alive"](False), nodmg, chg] if order == 0 else [chg, ENV["Alive"](False), nodmg]
        e_ = entry(1.0, 0.2, RGT.ADDITIVE, conds)
        dd.setLastDamageTime(Instant.MIN if ago_ns is None else now.minusNanos(JLong(ago_ns)))
        acc.arch = Arch.of(deathType) if dead else Arch.empty()
        return [int(Mana.state(acc, None, now, e_.getRegenerating())), [round(float(x), 4) for x in Mana.rates(acc, None, now, JArray(RGV)([e_]))],
                bool(Cond.allConditionsMet(acc, None, now, e_.getRegenerating()))]

    def am(r, p, f_, secs=1.0):
        return float(Mana.amount(JArray(JFloat)(r), p, f_, JFloat(secs), JFloat(0.0), JFloat(1.0e9)))

    def sl(r, p, f_, mx=30.0):
        return str(Mana.stateLine(JArray(JFloat)(r), p, f_, JFloat(mx)))
    try:
        H["ev"] = {"out": ev(FC(True, True), 10 * SEC), "chg_out": ev(FC(False, True), 10 * SEC), "chg_in": ev(FC(False, True), 2 * SEC),
                   "in": ev(FC(True, True), 2 * SEC), "dead_chg": ev(FC(False, True), 10 * SEC, True), "dead_chg_in": ev(FC(False, True), 2 * SEC, True),
                   "dead_chg_first": ev(FC(False, True), 10 * SEC, True, 1), "noninv_fail": ev(FC(False, False), 10 * SEC),
                   "noninv_pass": ev(FC(True, False), 10 * SEC), "never_chg": ev(FC(False, True), None), "edge6_chg": ev(FC(False, True), NDT_NS),
                   "edge5999_chg": ev(FC(False, True), NDT_NS - 1)}
        H["amount"] = {"chg_out_p0": am([5, 0, 0, 5, 0], 0.0, 50), "chg_out_p20": am([5, 0, 0, 5, 0], 20.0, 50), "chg_out_p1000": am([5, 0, 0, 5, 0], 1000.0, 50),
                       "chg_out_p5000": am([5, 0, 0, 5, 0], 5000.0, 50), "chg_out_neg": am([5, 0, 0, 5, 0], -40.0, 50),
                       "chg_out_pulse": am([5, 0, 0, 5, 0], 0.0, 50, 0.2), "chg_out_f0": am([5, 0, 0, 5, 0], 0.0, 0),
                       "chg_in_p0": am([5, 0, 5, 0, 5], 0.0, 50), "chg_in_p20": am([5, 0, 5, 0, 5], 20.0, 50), "chg_in_f0": am([5, 0, 5, 0, 5], 20.0, 0),
                       "chg_in_f100": am([5, 0, 5, 0, 5], 0.0, 100), "chg_in_pulse": am([5, 0, 5, 0, 5], 0.0, 50, 0.2), "dead": am([5, 0, 0, 0, 0], 20.0, 50),
                       "len3": am([5, 0, 0], 20.0, 50), "len4": am([5, 0, 0, 5], 20.0, 50), "cap": float(Mana.amount(JArray(JFloat)([5, 0, 0, 5, 0]), 0.0, 50,
                       JFloat(1.0), JFloat(29.5), JFloat(30.0))), "full": float(Mana.amount(JArray(JFloat)([5, 0, 0, 5, 0]), 0.0, 50, JFloat(1.0), JFloat(30.0), JFloat(30.0)))}
        sweep = []
        for dead in (False, True):
            for chg_now in (False, True):
                for ago in (None, 0, 1000000, 2 * SEC, NDT_NS - 1, NDT_NS, NDT_NS + 1, 10 * SEC, 3600 * SEC):
                    st_, r_, van = ev(FC(not chg_now, True), ago, dead)
                    for p in (0.0, 20.0, -40.0, 1000.0, 5000.0):
                        for f_ in (0, 50, 100, 150):
                            sweep.append([dead, chg_now, ago, p, f_, st_, r_, van, am(r_, p, f_)])
        H["sweep"] = sweep
        H["lines"] = [sl([5, 5, 0, 0, 0], 20.0, 50), sl([5, 5, 0, 0, 0], 0.0, 50), sl([5, 0, 0, 5, 0], 20.0, 50), sl([5, 0, 0, 5, 0], 0.0, 0),
                      sl([5, 0, 5, 0, 0], 20.0, 50), sl([5, 0, 5, 0, 5], 20.0, 50), sl([5, 0, 0, 0, 0], 20.0, 50), sl([5, 0, 5, 0, 0], 0.0, 50, 0.0),
                      sl([5, 0, 0], 20.0, 50), sl([5, 0, 5], 0.0, 0), sl([5, 0, 0, 5, 0], 5000.0, 150)]
    except Exception as e:
        H["error"] = str(e)
    # /skills mana EXECUTED: the real ManaCmd.execute (the stand-in store answers the Mana value, the hit stamp, the clock and the archetype;
    # PermissionsModule = a stand-in that says yes) - charging out of combat / in combat / dead + charging / out / in combat
    try:
        PermM = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule")
        setf(None, PermM, "instance", U.allocateInstance(JClass("skyytest.FakePerms").class_))
        MCmd = JClass(PKG + "ManaCmd")
        mc = U.allocateInstance(MCmd.class_)
        exm = MCmd.class_.getDeclaredMethod("execute", JClass("com.hypixel.hytale.server.core.command.system.CommandContext").class_,
                                            JClass("com.hypixel.hytale.component.Store").class_, JClass("com.hypixel.hytale.component.Ref").class_,
                                            PRef.class_, JClass("com.hypixel.hytale.server.core.universe.world.World").class_)
        exm.setAccessible(True)
        st0 = ENV["store"]
        ddm = ENV["DDC"]()
        st0.stats, st0.dd, st0.statsType, st0.ddType, st0.arch = ENV["fsm"], ddm, ENV["statsType"], ENV["ddType"], Arch.empty()
        setf(ENV["mv"], ENV["ESV"], "value", JFloat(10.0))
        setf(ENV["mv"], ENV["ESV"], "max", JFloat(30.0))
        Mana.SRC.clear()
        Mana.put(uP, "Test", 20.0)
        Mana.IN_COMBAT = 50
        mnow = ENV["tr"].getNow()

        def mana_cmd(chg_now, ago_s, dead=False):
            ENV["charging"].v = not chg_now
            ddm.setLastDamageTime(mnow.minusSeconds(ago_s))
            st0.arch = Arch.of(deathType) if dead else Arch.empty()
            texts()
            exm.invoke(mc, JArray(JObj)([None, st0, None, prP, None]))
            return texts()
        H["cmd"] = {"chg_out": mana_cmd(True, 10), "chg_in": mana_cmd(True, 2), "dead_chg": mana_cmd(True, 10, True), "out": mana_cmd(False, 10),
                    "in": mana_cmd(False, 2)}
        Mana.IN_COMBAT = 0
        H["text_f0"] = str(Mana.text(uP))
        Mana.IN_COMBAT = 50
        H["text_f50"] = str(Mana.text(uP))
        ENV["charging"].v = True
        st0.stats, st0.dd, st0.arch = None, None, None
        Mana.SRC.clear()
    except Exception as e:
        H["cmd"] = {"error": str(e)}
    D["H"] = H

    # ---------------------------------------------------------------- C: the loader (blocks appended once, LF / CRLF, an admin's switch)
    C = {}
    cb_, mb_ = D["curve_block"].encode("latin-1"), D["mreg_block"].encode("latin-1")
    full = D["defaults"].encode("latin-1")
    base_old = full[:full.index(b"\n# ---------- Class skill levels (SkyySkills 0.4.12)") + 1]   # every pre-0.4.12 block, no 0.4.12 key
    assert b"levels.class=" not in base_old and b"levels.class.same" not in base_old and b"mana.regen" not in base_old
    cdir = os.path.join(SCRATCH, "c-lf")
    load_cfg(cdir, base_old)
    c1_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    load_cfg(cdir)
    c2_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    C["lf"] = {"exact": c1_ == base_old + b"\n" + cb_ + b"\n" + mb_, "again_same": c1_ == c2_, "no_cr": b"\r" not in c1_}
    cdir = os.path.join(SCRATCH, "c-crlf")
    load_cfg(cdir, base_old.replace(b"\n", b"\r\n"))
    c3_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    C["crlf"] = {"exact": c3_ == (base_old + b"\n" + cb_ + b"\n" + mb_).replace(b"\n", b"\r\n"), "all_crlf": c3_.count(b"\r\n") == c3_.count(b"\n")}
    cdir = os.path.join(SCRATCH, "c-admin")
    load_cfg(cdir, b"multiplier=1.0\nlevels.class.sameAsOthers=true\n")
    c4_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    load_cfg(cdir)
    C["admin"] = {"same_kept": c4_.count(b"levels.class.sameAsOthers=") == 1 and b"levels.class.sameAsOthers=true" in c4_,
                  "list_added": c4_.count(b"\nlevels.class=") == 1, "SAME": bool(Defs.SAME),
                  "class_eq_general": int(Defs.levelOf(DIVINITY, JLong(67425))) == int(Defs.generalLevel(JLong(67425)))}
    cdir = os.path.join(SCRATCH, "c-noeol")
    base_noeol = base_old.rstrip(b"\n")
    load_cfg(cdir, base_noeol)
    c5_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    C["noeol"] = c5_ == base_noeol + b"\n\n" + cb_ + b"\n" + mb_
    cdir = os.path.join(SCRATCH, "c-short")
    txt = load_cfg(cdir, b"multiplier=1.0\nlevels.class=10,20,30\nlevels.class.sameAsOthers=false\nmana.regen.inCombat=50\n")
    C["short"] = [int(Defs.CMAX), int(Defs.maxOf(DIVINITY)), int(Defs.levelOf(DIVINITY, JLong(60))), int(Defs.levelOf(DIVINITY, JLong(59))), "max level 3" in txt,
                  open(os.path.join(cdir, "xp.properties"), "rb").read().count(b"levels.class=") == 1]
    cdir = os.path.join(SCRATCH, "c-bad")
    txt = load_cfg(cdir, b"multiplier=1.0\nlevels.class=10,abc\nlevels.class.sameAsOthers=false\nmana.regen.inCombat=50\n")
    C["bad"] = [int(Defs.CMAX), [int(x) for x in Defs.CPER] == T["cper"], "1 bad line(s) skipped" in txt]
    f = os.path.join(SCRATCH, "c-fresh")
    load_cfg(f)
    C["fresh_text"] = str(Cfg.load())
    C["fresh"] = [int(Defs.CMAX), bool(Defs.SAME), int(Mana.IN_COMBAT), [int(x) for x in Defs.CPER] == T["cper"]]
    D["C"] = C

    # ---------------------------------------------------------------- K: the kit rows + the class curve custom rows
    K = {}
    K["get"] = [str(Kit.customGet("levels.class.max")), str(Kit.customGet("levels.class.scale")), str(Kit.customGet("levels.max")), str(Kit.customGet("levels.scale"))]
    r60 = Kit.customSet("levels.class.max", "60")
    K["cut60"] = [str(r60[0]), str(r60[1]), str(r60[2]), [str(x) for x in r60[3]][0], len(str(r60[3][1]).split(",")), int(Defs.CMAX), int(Defs.maxOf(DIVINITY)), int(Defs.MAX)]
    # the kit would write the line; emulate it for curListC (the kit's get) by setting CPER directly through the returned list
    r100 = Kit.customSet("levels.class.max", "100")
    K["raise100"] = [str(r100[0]), str(r100[1]), str(r100[2]), str(r100[3][1]) == ",".join(str(x) for x in T["cper"]), int(Defs.CMAX)]
    r110 = Kit.customSet("levels.class.scale", "110")
    K["scale110"] = [str(r110[0]), str(r110[1]), int(Defs.CPER[0]), str(r110[2])]
    rb = Kit.customSet("levels.class.scale", "100")
    K["scale100"] = [str(rb[0]), str(rb[1]), [int(x) for x in Defs.CPER] == T["cper"]]
    K["bad"] = [str(Kit.customSet("levels.class.max", "0")[0]), str(Kit.customSet("levels.class.max", "101")[0]), str(Kit.customSet("levels.class.scale", "5")[0]),
                str(Kit.customSet("levels.class.max", "x")[0])]
    rg = Kit.customSet("levels.max", "50")
    K["general50"] = [str(rg[0]), str(rg[3][0]), int(Defs.MAX), int(Defs.CMAX), int(Defs.maxOf(DIVINITY))]
    Kit.customSet("levels.max", "100")
    HM = JClass("java.util.HashMap")
    vals = HM()
    vals.put("levels.class", "10,20,30,40")
    vals.put("levels", "50,125")
    K["read"] = [str(Kit.customRead("levels.class.max", vals)), str(Kit.customRead("levels.class.scale", vals)), str(Kit.customRead("levels.max", vals)),
                 str(Kit.customRead("levels.class.max", None)), str(Kit.customRead("levels.class.scale", None))]
    K["check"] = [Kit.checkLevels("levels.class", "1,2,3") is None, Kit.checkLevels("levels.class", "0,5") is not None,
                  Kit.checkLevels("levels.class", ",".join(["5"] * 101)) is not None]
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    D["K"] = K

    # ---------------------------------------------------------------- X: the review fixes
    from jpype import JInt as PInt
    X = {}
    JStrA = JArray(JClass("java.lang.String"))
    OvCfg = JClass(PKG + "OverallCfg")
    slots0, cls0 = OvCfg.SLOTS, bool(OvCfg.CLASS)

    def page_all(pg):
        """page_texts + the appended markup (CustomUICommand.text: the static labels such as 'Max Overall Level reached')"""
        b, ev = UCB(), UEB()
        err = None
        try:
            pg.build(None, b, ev, None)
        except Exception as e:
            err = str(e)
        return err, [str(c.data) for c in b.getCommands() if c.data is not None] + [str(c.text) for c in b.getCommands() if c.text is not None]
    # R1: no counted skill (Overall.maxLevel 0) -> never the max layout; a maxed player still gets it
    Store.DATA.remove(keyP)
    OvCfg.SLOTS = JArray(PInt)([])
    OvCfg.CLASS = False
    err, cmds = page_all(OverallPage(prP))
    X["ov_none"] = {"err": err, "max": int(Ovl.maxLevel(uP)), "next": [str(x) for x in Ovl.nextLines(0, 0)],
                    "title": has(cmds, "Level 0 of 0"), "sub": has(cmds, "No skill counts toward the Overall Level on this server"),
                    "line": has(cmds, "Nothing - no skill counts toward the Overall Level"), "maxlay": has(cmds, "Max Overall Level reached"),
                    "the_highest": has(cmds, "the highest Overall Level")}
    OvCfg.SLOTS = JArray(PInt)([MINING])
    dmax = JArray(JLong)(32)
    dmax[MINING] = 10 ** 12
    dmax[16 + MINING] = 100
    Store.DATA.put(keyP, dmax)
    err, cmds = page_all(OverallPage(prP))
    X["ov_max"] = {"err": err, "max": int(Ovl.maxLevel(uP)), "title": has(cmds, "Level 100 of 100"), "maxlay": has(cmds, "Max Overall Level reached"),
                   "the_highest": has(cmds, "the highest Overall Level"), "next": [str(x) for x in Ovl.nextLines(100, 100)]}
    dmax[MINING] = 67425
    err, cmds = page_all(OverallPage(prP))
    X["ov_mid"] = {"err": err, "title": has(cmds, "Level 15 of 100"), "maxlay": has(cmds, "Max Overall Level reached"), "next_hd": has(cmds, "Overall Level 16 adds"),
                   "next": [str(x) for x in Ovl.nextLines(15, 100)]}
    OvCfg.SLOTS = slots0
    OvCfg.CLASS = cls0
    Store.DATA.remove(keyP)
    # R4: the compact Server Setup answer (pure), the action, the full /skills mana text
    try:                                                           # (a jar without ManaRegen.compact still runs on: those checks fail)
        X["compact"] = [str(Mana.compact(0.0, JStrA([]), JFloat(5.0), 50)), str(Mana.compact(20.0, JStrA(["SkyyGear=+20"]), JFloat(5.0), 50)),
                        str(Mana.compact(20.0, JStrA(["SkyyGear=+20"]), JFloat(5.0), 0)), str(Mana.compact(0.0, JStrA([]), JFloat(0.0), 50)),
                        str(Mana.compact(0.0, JStrA([]), JFloat(0.0), 0)), str(Mana.compact(0.0, None, JFloat(5.0), 100))]
        many = ["Source%02d=+%d" % (i, i) for i in range(12)]
        X["compact_many"] = str(Mana.compact(1000.0, JStrA(many), JFloat(5.0), 100))
        X["compact_long"] = str(Mana.compact(5.0, JStrA(["x" * 64 + "=+5"]), JFloat(5.0), 50))
        X["compact_odd"] = str(Mana.compact(333.333, JStrA(many), JFloat(3.3333), 55))
        X["compact_two"] = str(Mana.compact(45.0, JStrA(["SkyyAccessories=+25", "SkyyGear=+20"]), JFloat(5.0), 50))
        rnd = random.Random(4124)
        worst = 0
        for _ in range(400):
            k = rnd.randint(1, 99)
            src_ = ["".join(rnd.choice("abcXYZ") for _ in range(rnd.randint(1, 64))) + "=+" + str(rnd.randint(-1000, 1000)) for _ in range(k)]
            p_ = round(rnd.uniform(0, 1000), 3) if rnd.random() < 0.7 else rnd.choice([0.0, 1000.0, 999.999])
            worst = max(worst, len(str(Mana.compact(p_, JStrA(src_), JFloat(rnd.choice([5.0, 3.3333, 0.0, 7.777, 100.0])), rnd.randint(0, 100)))))
        X["compact_worst"] = worst
    except Exception as e:
        X.update({"compact": "error: %s" % e, "compact_many": "", "compact_long": "", "compact_odd": "", "compact_two": "", "compact_worst": 999})
    Mana.SRC.clear()
    for i in range(12):
        Mana.put(ub, "Source%02d" % i, float(i + 1))
    Mana.put(ub, "SkyyGear", 20.0)
    Mana.IN_COMBAT = 50
    X["vanilla_rate"] = float(Mana.vanillaRate())
    X["action"] = [str(x) for x in Mana.showAction(ub, "Skyy")]
    X["action_null"] = [str(x) for x in Mana.showAction(None, "console")]
    Mana.SRC.clear()
    Mana.put(ub, "SkyyGear", 20.0)
    X["action1"] = str(Mana.showAction(ub, "Skyy")[2])
    X["text1"] = str(Mana.text(ub))
    Mana.SRC.clear()
    # R5: the class curve size message = the EFFECTIVE class totals after the change
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, False)

    def eff(top):
        e = [int(x) for x in Defs.ECUM]
        return [str(Defs.fmt(JLong(e[i]))) for i in (1, 20, top) if i < len(e)]
    r = Kit.customSet("levels.class.scale", "150")
    X["scale150"] = {"r": [str(r[0]), str(r[1]), str(r[2])], "eff": eff(100), "ecum1": int(Defs.ECUM[1]), "ccum1": int(Defs.CCUM[1])}
    r = Kit.customSet("levels.class.scale", "100")
    X["scale100"] = {"r": [str(r[0]), str(r[1]), str(r[2])], "eff": eff(100), "same_list": [int(x) for x in Defs.CPER] == T["cper"]}
    Kit.customSet("levels.class.max", "10")
    r = Kit.customSet("levels.class.scale", "100")
    X["scale_max10"] = [str(r[0]), str(r[2])]
    Defs.setClassTable(Defs.DEFAULT_CPER, True)
    r = Kit.customSet("levels.class.scale", "120")
    X["scale_same"] = [str(r[0]), str(r[2]), bool(Defs.SAME)]
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    # R9: a live curve change forgets who is published; the next publishOnline republishes skill:<uuid>
    Store.PUBLISHED.clear()
    Store.PUBLISHED.put(uP, JBool.TRUE)
    Kit.customSet("levels.class.max", "60")
    X["pub_custom"] = bool(Store.PUBLISHED.isEmpty())
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    Store.PUBLISHED.put(uP, JBool.TRUE)
    Kit.reload()
    X["pub_reload"] = bool(Store.PUBLISHED.isEmpty())
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    dpub = JArray(JLong)(32)
    dpub[DIVINITY] = 67425
    dpub[16 + DIVINITY] = 28
    Store.DATA.put(keyP, dpub)
    bridge.put("class:" + keyP, "Priest")
    Store.PUBLISHED.clear()
    Store.publish(uP)
    e2e = [str(bridge.get("skill:" + keyP)), bool(Store.PUBLISHED.containsKey(uP))]
    Kit.customSet("levels.class.max", "20")
    e2e += [str(bridge.get("skill:" + keyP)), bool(Store.PUBLISHED.containsKey(uP)), int(Store.level(uP, DIVINITY))]
    Store.publishOnline()
    e2e += [str(bridge.get("skill:" + keyP)), bool(Store.PUBLISHED.containsKey(uP))]
    X["pub_e2e"] = e2e
    Store.DATA.remove(keyP)
    Defs.setTable(Defs.DEFAULT_PER)
    Defs.setClassTable(Defs.DEFAULT_CPER, False)
    D["X"] = X
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: bytecode compare
def version_only(a, b):
    la, lb = a.split(chr(10)), b.split(chr(10))
    return len(la) == len(lb) and all(x == y or x.replace(OLD_VERSION, VERSION, 1) == y for x, y in zip(la, lb))


def run_bytecode(old, new, out):
    import skyybuild as B
    from jpype import JClass
    _jvm_start([B.JAVASSIST], verify=False)
    ClassPool, BAIS = JClass("javassist.ClassPool"), JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def listing(pool, data):
        cc = pool.makeClass(BAIS(data))
        ms = {}
        behaviors = list(cc.getDeclaredBehaviors())
        if cc.getClassInitializer() is not None:
            behaviors.append(cc.getClassInitializer())
        for mm in behaviors:
            k = "%s%s" % (mm.getName(), mm.getSignature())
            if mm.getMethodInfo().getCodeAttribute() is None:
                ms[k] = ""
                continue
            it = mm.getMethodInfo().getCodeAttribute().iterator()
            cpool = mm.getMethodInfo().getConstPool()
            lines = []
            while it.hasNext():
                pos_ = it.next()
                ln = str(IP.instructionString(it, pos_, cpool)).replace(chr(13), "<CR>").replace(chr(10), "<LF>")
                if it.byteAt(pos_) == 0xc1:                        # instanceof: javassist's InstructionPrinter prints no class - add it
                    ln = "instanceof Class " + str(cpool.getClassInfo(it.u16bitAt(pos_ + 1)))
                ln = re.sub(r"#\d+ = ", "", ln).replace("ldc_w ", "ldc ")
                ln = re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln)
                lines.append(ln)
            ms[k] = "\n".join(lines)
        fields = sorted("%s %s" % (f.getName(), f.getSignature()) for f in list(cc.getDeclaredFields()))
        return ms, fields

    zo, zn = zipfile.ZipFile(old), zipfile.ZipFile(new)
    res = {"diff": {}, "only_old": sorted(set(zo.namelist()) - set(zn.namelist())), "only_new": sorted(set(zn.namelist()) - set(zo.namelist())),
           "same": sorted(n for n in set(zo.namelist()) & set(zn.namelist()) if n.endswith(".class") and zo.read(n) == zn.read(n)), "calls": {}}
    for n in sorted(set(zo.namelist()) & set(zn.namelist())):
        if not n.endswith(".class") or zo.read(n) == zn.read(n):
            continue
        mo, fo = listing(ClassPool(False), zo.read(n))
        mn, fn = listing(ClassPool(False), zn.read(n))
        changed = sorted(k for k in set(mo) & set(mn) if mo[k] != mn[k])
        res["diff"][n] = {"changed": changed, "gone": sorted(set(mo) - set(mn)), "new": sorted(set(mn) - set(mo)),
                          "fields_gone": sorted(set(fo) - set(fn)), "fields_new": sorted(set(fn) - set(fo)),
                          "vo": [k for k in changed if version_only(mo[k], mn[k])]}
    # every SkillDefs level call in the new jar names its slot: no call to a (J)I / (J)J / (J)String lookup survives anywhere
    bad = []
    for n in zn.namelist():
        if not n.endswith(".class"):
            continue
        ms, _ = listing(ClassPool(False), zn.read(n))
        for k, v in ms.items():
            for ln in v.split("\n"):
                if "SkillDefs." in ln and re.search(r"SkillDefs\.(levelOf|intoLevel|needFor|progress)\(\(J\)", ln):
                    bad.append("%s %s: %s" % (n, k, ln.strip()))
    res["calls"]["global_lookups"] = bad

    # X (review fixes): instruction positions of the calls that matter, in the NEW jar (-1 = no such call)
    def where(cls, prefix, pats):
        ms_, _ = listing(ClassPool(False), zn.read("com/skyy/skills/%s.class" % cls))
        ks = [k for k in ms_ if k.startswith(prefix)]
        if len(ks) != 1:
            return {"methods": ks}
        ls = ms_[ks[0]].split(chr(10))
        return dict((p, [i for i, ln in enumerate(ls) if p in ln]) for p in pats)
    res["calls"]["acrosys"] = where("AcroSys", "tick(", ["ManaRegen.tick", "Acro.state", "AcroCfg.ENABLED", "Acro.move", "Acro.falls", "Brew.tick", "Xbow.tick", "Perks.tick"])
    res["calls"]["kit_reload"] = where("SkillKit", "reload(", ["SkillCfg.load", "SkillStore.republishAll"])
    res["calls"]["kit_custom"] = where("SkillKit", "customSet(", ["SkillDefs.setTable", "SkillDefs.setClassTable", "SkillStore.republishAll", "SkillKit.classTotals"])
    res["calls"]["reload_cmd"] = where("ReloadCmd", "execute(", ["SkillCfg.load", "SkillStore.republishAll"])
    res["calls"]["republish_body"] = where("SkillStore", "republishAll(", ["monitorenter", "monitorexit", "invoke"])
    # 0.4.13: ManaRegen.tick's order (pulse gate -> combat -> the refill) and the plugin's put / remove of skill:fn:combat
    res["calls"]["mr_tick"] = where("ManaRegen", "tick(", ["ManaRegen.CLK", "EntityStatMap.getComponentType", "ManaRegen.CMB", "TimeResource.getNow",
                                                          "TimeResource.getTimeDilationModifier", "ManaRegen.carry(",
                                                          "getRegeneratingValues", "ManaRegen.combat(", "ManaRegen.IN_COMBAT", "ManaRegen.total(", "getMax",
                                                          "ManaRegen.rates(", "ManaRegen.amount(", "addStatValue"])
    # 0.4.13 fix round: carry's calls (the world name, the three stamps through carried(), the record, the wall clock), state's Charging
    # test, ManaCmd's state line, Acro.retainOnline's prunes
    res["calls"]["mr_carry"] = where("ManaRegen", "carry(", ["DamageDataComponent.getComponentType", "Store.getExternalData", "EntityStore.getWorld",
                                                            "World.getName", "System.nanoTime", "ManaRegen.CARRY", "getLastDamageTime", "setLastDamageTime",
                                                            "getLastCombatAction", "setLastCombatAction", "getLastChargeTime", "setLastChargeTime",
                                                            "ManaRegen.carried(", "SkillCfg.warn"])
    res["calls"]["mr_state"] = where("ManaRegen", "state(", ["NoDamageTakenCondition", "ChargingCondition", "Condition.eval0(", "Condition.eval("])
    res["calls"]["mcmd"] = where("ManaCmd", "execute(", ["ManaRegen.rates(", "ManaRegen.stateLine(", "ManaRegen.text(", "holding a charge",
                                                         "IN COMBAT (vanilla"])
    res["calls"]["acro_retain"] = where("Acro", "retainOnline(", ["ManaRegen.CLK", "ManaRegen.CMB", "ManaRegen.CARRY", "retainAll"])
    res["calls"]["pl_setup"] = where("SkyySkillsPlugin", "setup(", ['"skill:fn:manaregen"', '"skill:fn:combat"', "Class com.skyy.skills.CombatFn",
                                                                   "Class com.skyy.skills.ManaRegenFn"])
    res["calls"]["pl_shutdown"] = where("SkyySkillsPlugin", "shutdown(", ['"skill:fn:manaregen"', '"skill:fn:combat"'])
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: the engine-access audit (section Z)
def run_audit(jar, fake, out):
    """every class / field / method / constructor reference in the jar's bytecode looked up with a MethodHandles.Lookup IN the referencing
    class (MethodHandles.privateLookupIn: the JVM's own access rules - a protected member only from a subclass, no package-private /
    private member of another class, public classes only; javassist compiles all of those, -Xverify:all does not catch them, the JVM
    refuses them with IllegalAccessError when the instruction first runs). Copied from SkyyUiProbe 0.3.1's harness section X. Control:
    skyytest.BadAccess (a class that is no page calling the page's protected sendUpdate) must be refused."""
    import skyybuild as B
    from jpype import JClass
    _jvm_start([B.JAVASSIST, jar, fake], verify=False)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    for p_ in (B.SERVER_JAR, jar, fake):
        CP.appendClassPath(p_)
    LIN, MTc, CPool, JMod_ = (JClass("skyytest.LookupIn"), JClass("java.lang.invoke.MethodType"), JClass("javassist.bytecode.ConstPool"),
                              JClass("java.lang.reflect.Modifier"))
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, loader)

    def lookup_audit(cn):
        D = jvm_class(cn)
        lk = LIN.lookupIn(D)
        cc = CP.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n = [], 0
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it_ = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it_.hasNext():
                p_ = it_.next()
                op = it_.byteAt(p_)
                if op not in XOPS:
                    continue
                where = "%s.%s @%d %s" % (cn.rsplit(".", 1)[-1], mi.getName(), p_, XOPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", loader).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)),
                                                 str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, loader)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn
                                    or (not JMod_.isPrivate(md) and str(C_.getPackageName()) == str(D.getPackageName()))):
                                raise ValueError("constructor %s %s%s is not accessible from %s" % (JMod_.toString(md), cname, desc, cn))
                        elif name == "<init>":
                            lk.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lk.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lk.findSpecial(C_, name, mt, D)
                        else:
                            lk.findVirtual(C_, name, mt)
                except Exception as ex_:
                    # a CALLER-SENSITIVE JDK method (Method.invoke, Field.get, Class.forName ...) cannot be looked up through a private
                    # lookup at all ("restricted lookup object") - that is the lookup API, not an access rule: such a call is allowed
                    # exactly when the method is public in a public class, which is checked here instead
                    ok_ = False
                    if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb8, 0xb9):
                        try:
                            mm_ = C_.getMethod(name, mt.parameterArray())
                            ok_ = JMod_.isPublic(int(C_.getModifiers())) and JMod_.isPublic(int(mm_.getModifiers()))
                            if ok_:
                                cs_.add("%s.%s" % (str(C_.getName()), name))
                        except Exception:
                            ok_ = False
                    if not ok_:
                        refused.append("%s: %s" % (where, ex_))
        return refused, n

    cs_ = set()
    names = [n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar).namelist() if n_.endswith(".class")]
    res = {"classes": len(names), "refs": 0, "refused": [], "per": {}}
    for cn in names:
        try:
            r_, k_ = lookup_audit(cn)
        except Exception as ex_:
            r_, k_ = ["%s: could not audit: %s" % (cn, ex_)], 0
        res["refused"] += r_
        res["refs"] += k_
        res["per"][cn.rsplit(".", 1)[-1]] = k_
    res["control"] = lookup_audit("skyytest.BadAccess")[0]
    res["caller_sensitive"] = sorted(cs_)
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent
def main():
    if "--mkfake" in sys.argv:
        return run_mkfake(arg("--mkfake"))
    if "--old-run" in sys.argv:
        return run_old(arg("--old-run"), arg("--out"), arg("--fake"), arg("--xs"))
    if "--new-run" in sys.argv:
        return run_new(arg("--new-run"), arg("--out"), arg("--fake"), arg("--xs"))
    if "--bytecode" in sys.argv:
        return run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
    if "--audit" in sys.argv:
        return run_audit(arg("--audit"), arg("--fake"), arg("--out"))
    for j in (JAR, OLD_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not os.path.isfile(LIVE):
        sys.exit("the live xp.properties is not at %s (pass --live <folder>; it is only ever read and copied)" % LIVE)
    scratch_root = os.path.join(TOOLS, "dev", "scratch").replace("\\", "/").lower().rstrip("/")
    here = SCRATCH.replace("\\", "/").lower().rstrip("/")
    if here == scratch_root or not here.startswith(scratch_root + "/"):
        sys.exit("--dir must be a folder INSIDE tools/dev/scratch/ (the whole folder is deleted afterwards), not %s" % SCRATCH)
    GUARD_OK[0] = True
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    shutil.copytree(LIVE_DIR, os.path.join(SCRATCH, "live-copy"))
    livenow = open(LIVE, "rb").read()
    check(b"\nlevels.class=" in livenow.replace(b"\r\n", b"\n") and b"\nmana.regen.inCombat=" in livenow.replace(b"\r\n", b"\n")
          and os.path.exists(os.path.join(LIVE_DIR, "class-curve.properties")),
          "the live Skyy_SkyySkills is 0.4.12's (levels.class + mana.regen.inCombat in xp.properties, class-curve.properties written)")
    prop = proposal_table()
    check([r[0] for r in prop] == list(range(1, 101)), "the proposal's section 5 table has levels 1-100")
    pcum = [0]
    for r in prop:
        pcum.append(pcum[-1] + r[1])
    gen = [50, 125, 200, 300, 500, 750, 1000, 1500, 2000, 3500, 5000, 7500, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 200000,
           300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1100000, 1200000, 1300000, 1400000, 1500000, 1600000,
           1700000, 1800000, 1900000, 2000000, 2100000, 2200000, 2300000, 2400000, 2500000, 2600000, 2750000, 2900000, 3100000,
           3400000, 3700000, 4000000] + [4300000 + 300000 * i for i in range(50)]
    gcum = [0]
    for x in gen:
        gcum.append(gcum[-1] + x)
    xs = totals_to_test(pcum, gcum)
    xs_file = os.path.join(SCRATCH, "xs.json")
    json.dump(xs, open(xs_file, "w"))
    me = os.path.abspath(__file__)
    fake = os.path.join(SCRATCH, "fake")
    p = subprocess.run([sys.executable, me, "--mkfake", fake, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and all(os.path.isfile(os.path.join(fake, "skyytest", n_ + ".class"))
                                    for n_ in ("FakeAcc", "FakeStore", "FakeCB", "FakeStatMap", "FixedCharging", "FakePerms", "LookupIn", "BadAccess")),
          "the stand-in classes were generated")
    outs = {"old": os.path.join(SCRATCH, "run-old.json"), "new": os.path.join(SCRATCH, "run-new.json"), "bc": os.path.join(SCRATCH, "bytecode.json"),
            "audit": os.path.join(SCRATCH, "audit.json")}
    p = subprocess.run([sys.executable, me, "--old-run", OLD_JAR, "--out", outs["old"], "--fake", fake, "--xs", xs_file, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["old"]), "child JVM for %s ran" % os.path.basename(OLD_JAR))
    p = subprocess.run([sys.executable, me, "--new-run", JAR, "--out", outs["new"], "--fake", fake, "--xs", xs_file, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["new"]), "child JVM for %s ran" % os.path.basename(JAR))
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", outs["bc"], "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["bc"]), "bytecode child ran")
    p = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", outs["audit"], "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["audit"]), "engine-access audit child ran")
    if FAILS:
        return finish()
    new, old, bc = json.load(open(outs["new"])), json.load(open(outs["old"])), json.load(open(outs["bc"]))
    au = json.load(open(outs["audit"]))
    # ---------------------------------------------------------------- A
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"][:3]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                             os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    if FAILS:
        return finish()
    D, O = new["data"], old["data"]
    # ---------------------------------------------------------------- T
    T = D["T"]
    check(T["cper"] == [r[1] for r in prop], "T: SkillDefs.DEFAULT_CPER = the proposal's section 5 'XP for level' for levels 1-100")
    check(T["ccum"] == pcum and [pcum[i] for i in (10, 20, 30, 40, 60, 100)] == [3510, 21540, 77290, 209090, 929090, 6627590]
          and [pcum[i] for i in range(1, 101)] == [r[2] for r in prop], "T: class totals = the proposal's Total column (20 at 21,540, 40 at 209,090, 100 at 6,627,590)")
    check(T["per"] == O["per"] == gen and T["cum"] == O["cum"] == gcum and [gcum[i] for i in range(1, 101)] == [r[3] for r in prop],
          "T: the general table = 0.4.12's (= the proposal's Old total column)")
    check(T["cper"] == O["cper"] and T["ccum"] == O["ccum"] and T["ecum"] == O["ecum"], "T: the class tables (CPER / CCUM / ECUM) = 0.4.12's")
    check(all(pcum[i] <= gcum[i] for i in range(101)) and T["ecum"] == T["ccum"], "T: the class table is at or below the general one at every level; ECUM = the class table")
    check(T["maxes"] == [100] * 16 and T["cmax"] == 100 and T["max"] == 100 and not T["same"], "T: maxOf 100 for every slot, CMAX 100, sameAsOthers off")
    nbad = []
    for s in [str(x) for x in T_SLOTS]:
        for i, (a, b) in enumerate(zip(T["xs"][s], O["xs"][s])):
            if a != b:
                nbad.append((s, xs[i], a, b))
    check(not nbad and len(T["xs"]) == len(O["xs"]) == len(T_SLOTS),
          "T: every slot (Mining, Acrobatics, legacy Combat, Cooking, Exploration, Archery, Divinity, Swordsmanship): level / into / need / progress = 0.4.12 for %d totals: %s" % (len(xs), nbad[:3]))

    def plevel(x):
        l = 0
        while l < 100 and x >= pcum[l + 1]:
            l += 1
        return l
    cbad = []
    for s in ("5", "15", "6"):
        for i, (lv, into, need, prog) in enumerate(T["xs"][s]):
            x = xs[i]
            L = plevel(x)
            wn = pcum[L + 1] - pcum[L] if L < 100 else 0
            if lv != L or into != x - pcum[L] or need != wn or (prog == "MAX") != (wn == 0):
                cbad.append((s, x, lv, into, need, L))
    check(not cbad, "T: class slots (Archery, Divinity, Swordsmanship) follow the proposal table for %d totals: %s" % (len(xs), cbad[:3]))
    check(T["general"] == O["general"], "T: SkillDefs.generalLevel = 0.4.12's for every total")
    print("T. class table = proposal (100 levels; 20 at 21,540 / 40 at 209,090 / 100 at 6,627,590), %d totals x %d slots = 0.4.12's" % (len(xs), len(T_SLOTS)))
    # ---------------------------------------------------------------- G
    G = D["G"]
    check(all(a == max(b, c) for a, b, c in G["steep"]) and any(b > c for a, b, c in G["steep"]) and any(c > b for a, b, c in G["steep"]),
          "G: a steeper class list: class level = max(general, class) at every total (both sides win somewhere)")
    check(G["cut60"][:3] == [60, 60, 100] and G["cut60"][3] == 0 and G["cut60"][4] == "MAX", "G: class max 60 caps class levels at 60 (Mining stays 100): %s" % G["cut60"])
    check(G["gen50"] == [50, 100, 60, 50, 20], "G: the general list cut to 50: Mining max 50, Divinity still 100 (929,090 = 60, 21,540 = 20): %s" % G["gen50"])
    check(G["same"] and G["back"], "G: sameAsOthers = the general table exactly; switching it off restores the class table")
    print("G. guard: level = max(general, class) up to the class max; general cut to 50 keeps class 51-100; sameAsOthers = general")
    # ---------------------------------------------------------------- P
    P = D["P"]
    check(P["level"] == [28, 15, 5], "P: SkillStore.level: Divinity 67,425 = 28 (0.4.11: 15), Mining 67,425 = 15, Archery 1,000 = 5 (0.4.11: 4): %s" % P["level"])
    fl = P["fn_level"]
    check(fl["Divinity"] == 28 and fl["Priest"] == 28 and fl["Combat"] == 28 and fl["div"] == 28 and fl["Mining"] == 15 and fl["Archery"] == 5,
          "P: skill:fn:level Divinity / Priest / Combat (current class) / div = 28, Mining 15, Archery 5: %s" % fl)
    check(P["fn_xp"] == [67425, 67425], "P: skill:fn:xp answers the TOTAL XP, unchanged (SkyyGuilds / SkyyTrees): %s" % P["fn_xp"])
    check("Mining:15" in P["levels"] and "Divinity:28" in P["levels"] and "Archery:5" in P["levels"], "P: skill:<uuid> = %s" % P["levels"])
    # Overall: 8 listed skills (Mining 15 + 7 x 0) + the class skill 28 = 43 / 9 = 4 (4.7)
    check(P["overall"] == [4, 47, 9] and fl["Overall"] == 4 and P["ovmax"] == 100, "P: Overall Level from the class level 28: %s (max %d)" % (P["overall"], P["ovmax"]))
    check(P["skills_page"] == [None, True, True, True, True, True], "P: /skills rows: 'Divinity  28' + 'XP to level 29', 'Mining  15' + 'XP to level 16': %s" % P["skills_page"])
    check(P["stats_page"] == [None, True, True] and P["stats_mining"] == [None, True, True], "P: Stats page 'Divinity - level 28 of 100' / 'Mining - level 15 of 100': %s %s" % (P["stats_page"], P["stats_mining"]))
    check(P["top_page"] == [None, True, True, True], "P: Top 10 Divinity: Level 28 (Pria) / Level 20 (Alex 21,540), rank line level 28: %s" % P["top_page"])
    check(P["overall_page"] == [None, True, True], "P: Overall page 'Level 4 of 100' + 'Divinity 28 (your class)': %s" % P["overall_page"])
    # +100 Divinity XP at 67,425: class level 28 starts at 61,490, level 29 needs 7,550 -> 5,935 + 100 = 6,035 -> "6035/7550"
    check(P["msg"] == ["+100 Divinity XP (5935/7550)"] and P["msg_take"] == "+1 Mining XP (0/30.0k)",
          "P: the +XP chat lines use each slot's table (Divinity 67,425 = 5,935 into level 29's 7,550; Mining 67,425 = 0 / 30k): %s %s" % (P["msg"], P["msg_take"]))
    check(P["party"] == "[Party] +6 Divinity XP (5935/7550) from Skyy's kill", "P: [Party] line: %s" % P["party"])
    lu = P["levelup"]
    check(lu["texts"][:2] == ["SKILL LEVEL UP  Divinity 19 -> 20   +2000 coins", "  next: Divinity 21 at 0/3350 XP - /skills"] and lu["coins"] == [[str(lu["coins"][0][0]), 2000]]
          and lu["paid"] == 20 and lu["level"] == 20, "P: a real class level up (21,539 -> 21,540): SKILL LEVEL UP Divinity 19 -> 20 +2000 coins, next at 3,350: %s" % lu)
    lm = P["levelup_mining"]
    check(lm["texts"][:1] == ["SKILL LEVEL UP  Mining 9 -> 10   +1000 coins"] and [c[1] for c in lm["coins"]] == [1000], "P: Mining 9,924 -> 9,925 = level 10 on the general table: %s" % lm)
    print("P. per-slot: level / skill:fn:level / skill:<uuid> / Overall / pages / chat / level-up rewards all use Divinity 28, Mining 15")
    # ---------------------------------------------------------------- M
    M = D["M"]
    lv = M["live"]
    # 0.4.13: 0.4.12 already ran on the live world (its record + both blocks are there) - a start reads the record and changes nothing
    check(lv["r1"]["ready"] and lv["r1"]["pending"] == {} and lv["r1"]["curve"] == "",
          "M live (0.4.12 already ran there): a start reads the record, scans nothing, nobody pending: %r" % lv["r1"]["curve"])
    check(lv["r1"]["heal"] == "", "M live: HealMig has nothing to do on the live data (its 0.4.11 marker is there): %r" % lv["r1"]["heal"])
    check(lv["changed1"] == [] and lv["xp_same"] and lv["blocks_there"] and lv["players_same"],
          "M live: start 1 writes nothing (xp.properties already holds both 0.4.12 blocks; record and player files untouched): %s" % lv["changed1"])
    check(lv["changed2"] == [] and lv["r2"]["ready"] and lv["r2"]["pending"] == {} and lv["r2"]["curve"] == "", "M live: start 2 changes nothing: %s" % lv["changed2"])
    check("\nscanned=" in lv["record"] and "\npending." not in lv["record"] and lv["record"].count("\r") == 0,
          "M live: the live record (scanned, nothing pending): %r" % lv["record"][:300])
    e1 = M["edit1"]
    # 0.4.13: the edited copies keep Skyy's real files; Skyy kept playing on 0.4.12, so a FRESH scan (record deleted) may also list real
    # profiles whose class level is higher on the class table than on the general one (documented: "deleted = the next start scans again:
    # the line again, never the coins"). Those stay pending here (nobody plays them); every count below is about the test profiles.
    TK, RK = set(M["test_keys"]), set(M["real_keys"])

    def tp(d):
        return dict((k, v) for k, v in d.items() if k in TK)

    def xp_(d):
        return dict((k, v) for k, v in d.items() if k not in TK)

    def rc(rec, kind):
        return sum(1 for ln in rec.splitlines() if ln.startswith(kind + ".") and ln[len(kind) + 1:].split("=")[0] in TK)
    extras = xp_(e1["start"]["pending"])
    check(set(extras) <= RK and all(len(v.split(":")) == 3 and int(v.split(":")[2]) > int(v.split(":")[1]) for v in extras.values()),
          "M edit: besides the test profiles a fresh scan lists only real profiles whose class level is higher on the class table: %s" % extras)
    check(sorted(tp(e1["start"]["pending"]).values()) == sorted(["15:15:28", "5:20:51", "5:4:5"]),
          "M edit: the scan records exactly the 3 risen test profiles (Divinity 15 -> 28, Archery 20 -> 51, Archery 4 -> 5): %s" % e1["start"]["pending"])
    check(rc(e1["rec1"], "pending") == 3 and rc(e1["rec1"], "done") == 0 and e1["rec1"].count("\npending.") == 3 + len(extras) and "\ndone." not in e1["rec1"],
          "M edit: the record holds the 3 pending test entries (+ %d real) before anyone plays" % len(extras))
    want_c1 = sum(100 * L for L in range(16, 29))
    t1 = e1["t1"]
    check(len(t1) >= 1 and t1[0] == "[Skills] Class skill curve updated: Divinity is now level 28 (was 15) - +28.6k coins for levels 16 to 28",
          "M edit: ONE chat line: %s" % t1)
    check(sum(c[1] for c in e1["c1"]) == want_c1 == 28600 and len(e1["c1"]) == 13 and e1["paid1"] == 28,
          "M edit: the level-up coins of exactly levels 16-28 (13 payouts, 28,600) and the paid marker 28: %s" % e1["c1"][:3])
    check(any(t.startswith("OVERALL LEVEL UP") for t in t1[1:]), "M edit: the Overall level up from the class jump: %s" % t1[1:])
    check(not e1["disk_paid_before"] and e1["disk_paid_after"] and rc(e1["rec2"], "done") == 1 and rc(e1["rec2"], "pending") == 2,
          "M edit: flush saves the player file (paid 28 on disk) before the record moves the entry to done")
    check(e1["t2"] == [] and e1["c2"] == [] and e1["t3"] == [] and e1["c3"] == [], "M edit: a second tick and a later small award pay / say nothing more: %s %s" % (e1["t2"], e1["t3"]))
    e2 = M["edit2"]
    check(len(tp(e2["start2"]["pending"])) == 2 and len(tp(e2["start2"]["done"])) == 1 and xp_(e2["start2"]["pending"]) == extras,
          "M edit: restart: 2 test profiles still pending, 1 done (the real ones still pending): %s" % e2["start2"]["pending"])
    want_c4 = sum(100 * L for L in range(21, 52))
    check(e2["t4"][:1] == ["[Skills] Class skill curve updated: Archery is now level 51 (was 20) - +111.6k coins for levels 21 to 51"]
          and sum(c[1] for c in e2["c4"]) == want_c4 == 111600, "M edit: profile 2 told when it becomes active (111,600 coins): %s" % e2["t4"][:2])
    check(e2["t5"][:2] == ["[Skills] Class skill curve updated: Archery is now level 5 (was 4) - +500 coins for level 5", "  Unlocked: Crossbows stay loaded when you switch slots"]
          and [c[1] for c in e2["c5"]] == [500], "M edit: Archery 4 -> 5 = the crossbow unlock line too: %s" % e2["t5"][:3])
    check(tp(e2["start3"]["pending"]) == {} and len(tp(e2["start3"]["done"])) == 3 and xp_(e2["start3"]["pending"]) == extras and e2["t6"] == [] and e2["c6"] == [],
          "M edit: a third start: no test profile pending, 3 done, nothing said or paid again")
    dk = e2["disk"]
    k1_, k2_, k3_ = sorted(dk, key=lambda k: (len(k), k))
    check("Combat.Priest.paid=28" in dk[k1_].splitlines() and "Combat.Archer.paid=51" in dk[k2_].splitlines() and "Combat.Archer.paid=5" in dk[k3_].splitlines(),
          "M edit: every told profile's paid marker is on disk (28 / 51 / 5)")
    check(rc(e2["rec3"], "done") == 3 and rc(e2["rec3"], "pending") == 0 and e2["rec3"].count("\npending.") == len(extras) and "Combat.Priest 15 -> 28 +28600 coins" in e2["rec3"],
          "M edit: the record ends with the 3 test profiles done (+ %d real still pending)" % len(extras))
    bz = M["busy"]
    check(bz["while"] == [[], True] and bz["after"][1] is False and bz["after"][0][:1] and bz["after"][0][0].startswith("[Skills] Class skill curve updated: Divinity is now level 28"),
          "M busy: profile:busy waits, told right after: %s" % bz)
    nw = M["nowrite"]
    check(not nw["w1"]["ready"] and nw["w1"]["pending"] == {} and nw["t"] == [] and not nw["rec"] and nw["w2"]["ready"] and len(tp(nw["w2"]["pending"])) == 1
          and xp_(nw["w2"]["pending"]) == extras,
          "M unwritable record: nobody told; the next start scans again: ready %s pending %s / %s" % (nw["w1"]["ready"], nw["w1"]["pending"], nw["w2"]["pending"]))
    nc = M["nocoins"]
    check(nc["t1"][:1] == ["[Skills] Class skill curve updated: Divinity is now level 28 (was 15)"] and sum(1 for x in nc["t1"] if "Class skill curve" in x) == 1
          and nc["paid"] == 15 and nc["t2"] == []
          and any("coins for earlier Divinity level ups" in t for t in nc["t3"]) and sum(c[1] for c in nc["coins"]) == 28600 and nc["paid_after"] == 28,
          "M no SkyyCoins: the line once (no coins), the levels stay owed and the next award pays them once: %s" % nc)
    print("M. ClassCurve: live copy (%d profile files, 0.4.12's record) unchanged by two starts; edited copy 3 test profiles told once each (28,600 / 111,600 / 500 coins, "
          "unlock line); %d real profile(s) a fresh scan would list: %s" % (lv["n_players"], len(extras), extras))
    # ---------------------------------------------------------------- R
    R = D["R"]
    a = R["amount"]
    check(a["out0"] == 0.0 and a["out20"] == 1.0 and a["out20_pulse"] == 0.2, "R: out of combat SkyySkills adds only the boost part: 0 / +20%% = 1 a second (vanilla 5 + 1 = 6): %s" % a)
    check(a["in0"] == 2.5 and a["in0_pulse"] == 0.5 and a["in20"] == 3.0 and a["in_f100"] == 5.0, "R: in combat 50%% of (5 + boosts): 2.5 / 3.0 a second, 100%% = 5: %s" % a)
    check(a["in_f0"] == 0.0 and a["out_f0"] == 1.0, "R: in-combat 0% = vanilla (nothing in combat), out-of-combat boosts still run")
    check(a["cap"] == 0.1 and a["full"] == 0.0 and a["nomana"] == 0.0 and a["charging"] == 0.0 and a["secs0"] == 0.0, "R: max Mana cap / full / no Mana pool / charging = 0")
    check(a["neg"] == 0.0 and a["neg_in"] == 2.5 and a["big"] == 50.0 and a["nan"] == 0.0 and a["f150"] == 5.0, "R: a negative total counts 0, 5000% clamps to 1000%, NaN = 0, factor clamps to 100")
    check(R["six_seconds"] == 15.0, "R: 6 s in combat in 0.2 s pulses at 50%% = 15 Mana: %s" % R["six_seconds"])
    rr = R["rates"]
    check(R["stubs"] == [1, 1, 1, 1], "R: the EntityModule / DamageModule / EntityStatsModule / TimeModule stand-ins took their instance field: %s" % R["stubs"])
    # 0.4.13 fix round: rates() = {base, out, in, chargeOut, chargeIn}; the 0.4.12 three numbers are the first three, unchanged but while
    # charging (Skyy's lock: charging out of combat -> chargeOut, charging in combat -> in + chargeIn; state 3 / 4)
    check(rr["out"] == [5.0, 5.0, 0.0, 0.0, 0.0] and rr["in"] == [5.0, 0.0, 5.0, 0.0, 0.0] and rr["edge6"] == [5.0, 5.0, 0.0, 0.0, 0.0]
          and rr["edge5999"] == [5.0, 0.0, 5.0, 0.0, 0.0],
          "R: real conditions: hit 10 s ago = out of combat, 2 s / 5.999 s = in combat, exactly 6 s = out (vanilla's >=): %s" % rr)
    check(rr["in_charging"] == [5.0, 0.0, 5.0, 0.0, 5.0] and rr["out_charging"] == [5.0, 0.0, 0.0, 5.0, 0.0] and rr["dead"] == [5.0, 0.0, 0.0, 0.0, 0.0]
          and rr["dead_in"] == [5.0, 0.0, 0.0, 0.0, 0.0],
          "R: charging in combat = the in-combat part (+ chargeIn), charging out of combat = chargeOut (SkyySkills refills it), dead = nothing: %s" % rr)
    check(rr["pct_entry"] == [5.0, 5.0, 0.0, 0.0, 0.0] and rr["zero_entry"] == [5.0, 5.0, 0.0, 0.0, 0.0] and rr["no_conds"] == [2.0, 2.0, 0.0, 0.0, 0.0]
          and rr["two"] == [6.0, 0.0, 6.0, 0.0, 0.0] and rr["state"] == [0, 1, 4, 3],
          "R: Percentage / zero entries ignored, no conditions = running, two entries add up; state out 0 / in 1 / charging in 4 / charging out 3: %s" % rr)
    check(R["cfg"] == {"default": 50, "150": 100, "neg": 0, "abc": 50, "zero": 0, "25": 25}, "R: mana.regen.inCombat load + clamps: %s" % R["cfg"])
    print("R. Mana regen: out 0 / +20%% = +%s/s, in combat %s/s (+20%%: %s), 0%% = vanilla, cap, no Mana; real conditions in / out / charging / dead" % (a["out20"], a["in0"], a["in20"]))
    # ---------------------------------------------------------------- B
    Bq = D["B"]
    check(Bq["seq"] == [0.0, "true", "true", 20.0, ["SkyyAccessories=+5", "SkyyGear=+15"], "true", 25.0, "true", 5.0, "false", "true", 0.0, "true", ["SkyyAccessories=+5"]],
          "B: add / replace / remove / get / sources; a negative total counts 0; add 0 removes: %s" % Bq["seq"])
    check(Bq["bad"] == ["false", "false", "false", "false", "false", "false", 0.0, None, True, []], "B: bad arguments: %s" % Bq["bad"])
    check(Bq["clamp"] == [1000.0, ["Big=+1000"]] and Bq["clear"] == [2, 0.0, 0.0, 0], "B: one source clamps to 1000, the total too; clear removes a source everywhere: %s %s" % (Bq["clamp"], Bq["clear"]))
    check(Bq["types"] == ["java.lang.Double", "java.lang.Boolean", "java.lang.Integer", "[Ljava.lang.String;"], "B: java.lang return types: %s" % Bq["types"])
    check(Bq["action"][0] == "ok" and Bq["action"][2].startswith("Mana Regen +20% (SkyyGear=+20). ") and ("In combat 50% of the normal refill." in Bq["action"][2]
          or "in combat 3/s (50%)." in Bq["action"][2]) and len(Bq["action"][2]) <= 110 and Bq["action_null"][0] == "ok",
          "B: the Server Setup action (the compact one-line answer, review fix R4): %s" % Bq["action"])
    check(Bq["total_feeds"] == 3.0, "B: a registered +20%% feeds the in-combat refill (3 a second): %s" % Bq["total_feeds"])
    print("B. skill:fn:manaregen: add/remove/get/sources/clear, clamps, java.lang types; action: %r" % Bq["action"][2][:120])
    # ---------------------------------------------------------------- W (0.4.13)
    W = D["W"]

    def ceil_ms(ns, delay=NDT_NS):
        return 0 if ns >= delay else -(-(delay - ns) // 1000000)
    check(W["window0"] == 0, "W: WINDOW is 0 before anybody was in combat: %s" % W["window0"])
    check(W["never"] == [0, 0, 0, 0], "W: never hit (lastDamageTime = Instant.MIN): out of combat (0), state 0, WINDOW 0, no Delay asked: %s" % W["never"])
    check(W["delay"] == [-1, NDT_NS, 1, NDT_NS],
          "W: the Delay asked from the condition: -1 without a real hit, exactly 6,000,000,000 ns after one, then cached (1 entry): %s" % W["delay"])
    ed = dict((a, b) for a, b in W["edges"])
    check(W["edges"] == [[ns, ceil_ms(ns)] for ns, _ in W["edges"]] and ed[0] == 6000 and ed[1000000] == 5999 and ed[5999999999] == 1 and ed[NDT_NS] == 0
          and ed[NDT_NS + 1] == 0, "W: right after a hit 6000, 1 ms later 5999, 1 ns before 6 s still 1, exactly 6 s = 0 (vanilla's >=), later 0: %s" % W["edges"])
    check(W["window1"] == 6000, "W: WINDOW = 6000 after the first in-combat answer: %s" % W["window1"])
    sw = W["sweep"]
    check(sw["nbad"] == 0 and sw["n"] == 6101 + 11 + 400 and sw["in"] > 6000,
          "W: %d instants (every 1 ms to 6.1 s, ns edges at 6 s, 400 random): combatLeft > 0 <=> ManaRegen.state == 1 <=> the in-combat refill rate > 0 "
          "<=> the NoDamageTaken condition fails, and combatLeft = ceil((6 s - since the hit) / 1 ms) - %d in combat; bad %s" % (sw["n"], sw["in"], sw["bad"]))
    check(W["charging"] == [4000, 4] and W["dead"] == [4000, 0],
          "W: charging (state 4: in combat + charging) / dead do not end the combat state (hit 2 s ago = 4000): %s %s" % (W["charging"], W["dead"]))
    check(W["two"] == [5000, 6000, 500, 500, 1500, 2500, 0],
          "W: a second entry (Delay 2.5 s): the larger countdown wins in either order, WINDOW follows the answer (6000 / 2500), exactly 2.5 s = 0: %s" % W["two"])
    check(W["nanos"] == [3251, 3251, 1, 0], "W: a Delay of 3,250,000,001 ns: 3251 ms (rounded up), window 3251, 1 ns before = 1, at it = 0: %s" % W["nanos"])
    check(W["never_count"] == [0, 0, 0, 0, 0, 0], "W: Percentage / zero-amount / condition-less / no-NoDamageTaken entries, no entries, no clock = never in combat: %s" % W["never_count"])
    check(W["bad_acc"] == [False, True, False, None], "W: a failing accessor: combat() never throws, drops the entry, logs once: %s" % W["bad_acc"])
    L = "java.lang.Long"
    check(W["fn_before"] == [[L, 0], [L, 0]], "W: skill:fn:combat before any hit / for an unknown player = Long 0: %s" % W["fn_before"])
    check(W["entry"] == [6000, True], "W: a pulse at the very hit records 6000 ms + its wall time: %s" % W["entry"])
    fa = W["fn_after"]
    check(fa is not None and fa[0] == L and 5900 <= fa[1] <= 6000, "W: skill:fn:combat right after the hit = Long ~6000 (6000 minus the wall ms since the pulse): %s" % fa)
    ff = W["fn_forms"]
    check(ff[0] == [L, 6000] and ff[1] == [L, 6000] and ff[2][0] == L and 5900 <= ff[2][1] <= 6000 and ff[3] == [L, 6000] and ff[4] == [L, 0],
          "W: apply(\"window\") / \" Window \" = Long 6000, apply(Object[]{uuid}) = the same as apply(uuid), Object[]{\"window\"} = 6000, another player 0: %s" % ff)
    check(W["fn_bad"] == [True] * 5, "W: apply(null / \"nope\" / an Integer / Object[]{} / Object[]{null}) = null: %s" % W["fn_bad"])
    pz = W["pulses"]
    check(len(pz) == 36 and all(v == (6000 - 200 * k if k < 30 else 0) and stt == (1 if k < 30 else 0) and pres == (k < 30) for k, v, stt, pres in pz),
          "W: pulse by pulse (0.2 s of world clock each): 6000, 5800, ... 200, then 0 at 6 s and the entry gone - state() == 1 exactly while > 0: %s" % (pz[:3] + pz[28:32]))
    check(W["wall"] == [3000, 2500, 2001, 2000, 1999, 100, 3000, True] and W["wall_out"] == [0, False],
          "W: between pulses the wall clock counts down (3000 -> 2500 after 0.5 s; a stale pulse keeps counting; a clock step back = no change); run out = 0 and dropped: %s %s"
          % (W["wall"], W["wall_out"]))
    check(W["floor"] == [50, 1, 1, 1, 1, 0, False], "W: while the pulse is fresh (<= 1 s) the answer stays >= 1 - only the next pulse ends combat; stale = 0 + dropped: %s" % W["floor"])
    check(W["consts"] == [1000, 3600000000000], "W: STALE_MS 1000, the Delay search cap 1 hour: %s" % W["consts"])
    rv1, rv2 = W["real"]
    check(5900 <= rv1 <= 6000 and 250 <= rv1 - rv2 <= 1500, "W: on the real wall clock (no pulse in between): %d, 0.3 s later %d" % (rv1, rv2))
    check(W["out_removes"] == [False, [L, 0]] and W["window_end"] == [6000, [L, 6000]], "W: an out-of-combat pulse removes the entry (Long 0); window 6000: %s %s"
          % (W["out_removes"], W["window_end"]))
    print("W. combat state: 0 before a hit, 6000 at the hit, ceil ms down to 0 at exactly 6 s; %d instants = the Mana regen's in-combat test; skill:fn:combat Long, "
          "window 6000, pulses 6000 -> 0, wall-clock countdown >= 1 while fresh" % sw["n"])
    # ---------------------------------------------------------------- E (0.4.13)
    En, Eo = D["E"], O["E"]
    check("error" not in En and "error" not in Eo, "E: the 500-tick script ran through the real ManaRegen.tick on both jars: %s / %s" % (En.get("error"), Eo.get("error")))
    if "error" not in En and "error" not in Eo:
        rn_, ro_ = En["rows"], Eo["rows"]
        # 0.4.13 fix round: identical to 0.4.12 up to the charging window; ticks 400-429 = charging IN combat (+20 %, in-combat 50 %):
        # 0.4.13 adds exactly the in-combat amount (3/s x the pulse's seconds), 0.4.12 nothing; from 430 on the same refill every tick
        diffs = [(a, b) for a, b in zip(rn_, ro_) if a[0] < 400 and a[:5] != b[:5]]
        check(len(rn_) == len(ro_) == 500 and not diffs and Eo["calls"] > 0 and En["index"] == Eo["index"] == 0,
              "E: ticks 0-399: after every tick the Mana, the addStatValue calls, the pulses and the world clock = the 0.4.12 jar's: first difference %s"
              % diffs[:2])
        chg_p = [(a, b) for a, b in zip(rn_, ro_) if 400 <= a[0] < 430 and a[3]]
        per_ci = 0.0 * 20.0 / 100.0 + 5.0 * (1.0 + 20.0 / 100.0) * 50.0 / 100.0 + 0.0 * (1.0 + 20.0 / 100.0)
        chg_bad = [(a[0], a[6], b[6], a[7]) for a, b in chg_p if b[6] != 0.0 or a[6] != f32(per_ci * a[7])]
        extra = sum(a[6] for a, b in chg_p)
        check(len(chg_p) >= 4 and not chg_bad and abs(extra - 3.0) < 0.15,
              "E: ticks 400-429 (charging in combat): 0.4.13 adds exactly 3/s x each pulse's seconds (%d pulses, +%.4f Mana), 0.4.12 nothing: %s"
              % (len(chg_p), extra, chg_bad[:3]))
        after_bad = [(a[0], a[1], b[1], a[6], b[6]) for a, b in zip(rn_, ro_) if a[0] >= 430 and (a[6] != b[6] or abs((a[1] - b[1]) - extra) > 1e-3
                                                                                                    or a[2] - b[2] != len(chg_p) or a[3:5] != b[3:5])]
        check(not after_bad and En["calls"] == Eo["calls"] + len(chg_p),
              "E: ticks 430-499: the same refill every tick on both jars (Mana offset = the charging Mana, %d more addStatValue calls): %s"
              % (len(chg_p), after_bad[:3]))
        check(En["warn"] == [False, False] and Eo["warn"] == [False, False], "E: no 'Mana regen in combat failed' on either jar: %s %s" % (En["warn"], Eo["warn"]))
        pulses = [r for r in rn_ if r[3]]
        cb_bad = [r for r in pulses if r[5] != (0 if (r[4] < 0 or 340 <= r[0] < 360) else ceil_ms(r[4]))]
        check(len(pulses) >= 70 and not cb_bad,
              "E: at all %d pulses the combat entry = ceil((6 s - since the last hit) / 1 ms) on the world clock (none never hit / out of combat / without a Mana value): %s"
              % (len(pulses), cb_bad[:4]))

        def calls(a, b):
            return rn_[b - 1][2] - (rn_[a - 1][2] if a > 0 else 0)

        def ents(a, b):
            return [r[5] for r in rn_[a:b] if r[3]]
        first_hit = [r[5] for r in rn_[30:40] if r[3]]
        ph = {"out": [calls(0, 30), ents(0, 30)], "first": first_hit[:1], "full": [calls(200, 230), min(ents(200, 230))],
              "zero": [calls(230, 300), min(ents(230, 300)), rn_[299][1]], "nopool": [calls(300, 340), min(ents(300, 340))],
              "novalue": [calls(340, 360), max(ents(340, 360))], "charging": [calls(400, 430), min(ents(400, 430))], "dead": [calls(430, 460), min(ents(430, 460))],
              "outboost": [calls(481, 490), max(ents(481, 490))], "refill": round(rn_[89][1] - rn_[29][1], 4), "refill20": round(rn_[149][1] - rn_[89][1], 4)}
        check(ph["out"][0] == 0 and set(ph["out"][1]) == {0} and ph["first"] and 5800 <= ph["first"][0] <= 6000,
              "E: never hit = no entry, no refill; the first pulse after the hit at tick 30 records ~6000: %s" % ph)
        check(ph["full"][0] == 0 and ph["full"][1] > 0 and ph["zero"][0] == 0 and ph["zero"][1] > 0 and ph["zero"][2] == 10.0 and ph["nopool"][0] == 0 and ph["nopool"][1] > 0,
              "E: the combat state is recorded where the refill returns early - full Mana, in-combat 0 %% + no boosts, no Mana pool (no addStatValue there): %s" % ph)
        check(ph["novalue"] == [0, 0] and ph["charging"][0] == len(chg_p) and ph["charging"][1] > 0 and ph["dead"][0] == 0 and ph["dead"][1] > 0,
              "E: no Mana value = no entry; charging in combat = the in-combat refill (0.4.13) and still in combat; dead = no refill, still in combat: %s" % ph)
        check(ph["outboost"][0] > 0 and ph["outboost"][1] == 0 and 4.4 <= ph["refill"] <= 5.6 and 5.3 <= ph["refill20"] <= 6.7,
              "E: out of combat with +20%% only the boost part refills (no entry); 2 s in combat refill ~5 (2.5/s), with +20%% ~6 (3/s): %s" % ph)
        print("E. real ManaRegen.tick, 500 ticks: Mana / addStatValue = 0.4.12 up to the charging window, there +%.3f Mana (charging in combat, %d pulses), "
              "then the same refill; combat entry = the world clock at all %d pulses, also at full Mana / 0 %% / no pool; refill 2 s in combat %s, with +20%% %s"
              % (extra, len(chg_p), len(pulses), ph["refill"], ph["refill20"]))
    # ---------------------------------------------------------------- C
    C = D["C"]
    nd, od = D["defaults"], O["defaults"]
    want = od.replace("# SkyySkills %s - XP rules" % OLD_VERSION, "# SkyySkills %s - XP rules" % VERSION, 1)
    check(nd == want and ("# SkyySkills %s - XP rules" % VERSION) in nd, "C: the 0.4.13 default file = 0.4.12's but the version line")
    check(C["lf"] == {"exact": True, "again_same": True, "no_cr": True}, "C: a 0.4.11-era LF file = itself + a blank line + the two blocks, once: %s" % C["lf"])
    check(C["crlf"] == {"exact": True, "all_crlf": True}, "C: the same file in CRLF: the blocks appended in CRLF, every byte before them kept: %s" % C["crlf"])
    check(C["admin"] == {"same_kept": True, "list_added": True, "SAME": True, "class_eq_general": True}, "C: an admin's sameAsOthers=true is kept (only the list appended): %s" % C["admin"])
    check(C["noeol"], "C: a file without a final newline gets one before the blank line")
    check(C["short"] == [3, 3, 3, 2, True, True], "C: a 3-entry class list = class max 3: %s" % C["short"])
    check(C["bad"] == [100, True, True], "C: a bad class list = the default class table + a bad line: %s" % C["bad"])
    check(C["fresh"] == [100, False, 50, True] and "class skills own table, max level 100, in-combat Mana regen 50%" in C["fresh_text"], "C: a fresh file: %s %s" % (C["fresh"], C["fresh_text"][-160:]))
    print("C. default file = 0.4.12's + the version line; pre-0.4.12 files get both blocks once (LF / CRLF kept); admin switch kept")
    # ---------------------------------------------------------------- K
    K = D["K"]
    ro, rn = O["rows"]["rows"], D["rows"]["rows"]
    ko, kn = [r[0] for r in ro], [r[0] for r in rn]
    check(rn == ro and len(rn) == 180, "K: the 180 Server Setup rows = 0.4.12's exactly (keys, order, every field)")
    check(kn[kn.index("levels"):kn.index("levels") + 7] == ["levels", "levels.scale", "levels.max"] + NEW_KEYS[:4] and kn[kn.index("overall.chat") + 1:kn.index("overall.chat") + 3] == NEW_KEYS[4:],
          "K: the class rows right after the general curve rows, the Mana rows after overall.chat")
    nr = dict((r[0], r) for r in rn)
    check(nr["levels.class"][3:10] == ["text", ",".join(str(r[1]) for r in prop), "1", "2000", "", "", "live,danger,adv"] and nr["levels.class.scale"][3:10] == ["int", "100", "10", "1000", "step=5", "%", "live,danger"]
          and nr["levels.class.max"][3:10] == ["int", "100", "1", "100", "step=5", "", "live,danger"] and nr["levels.class.sameAsOthers"][3:10] == ["bool", "false", "", "", "", "", "live,danger"]
          and nr["mana.regen.inCombat"][3:10] == ["int", "50", "0", "100", "step=5", "%", "live"] and nr["mana.regen.show"][3] == "action",
          "K: the 0.4.12 rows' types / defaults / bounds / flags")
    check(all(len(r[1]) <= 40 and len(r[10]) <= 100 for r in rn), "K: labels <= 40, help <= 100")
    check(K["get"] == ["100", "100", "100", "100"], "K: customGet class max / scale / max / scale: %s" % K["get"])
    check(K["cut60"][:2] == ["ok", "60"] and K["cut60"][3:] == ["levels.class", 60, 60, 60, 100] and "Class max level: 60 (was 100)" in K["cut60"][2],
          "K: Class max level 60: the class list cut, the general max untouched: %s" % K["cut60"])
    check(K["raise100"][:2] == ["ok", "100"] and K["raise100"][3:] == [True, 100] and "back with the XP they had before the cut" in K["raise100"][2], "K: raised to 100: the exact class list back: %s" % K["raise100"])
    check(K["scale110"][:3] == ["ok", "110", 55] and K["scale100"] == ["ok", "100", True], "K: class curve size 110 -> level 1 = 55; 100 = the exact default: %s %s" % (K["scale110"], K["scale100"]))
    check(K["bad"] == ["bad", "bad", "bad", "bad"], "K: out-of-range / non-number class curve values refused: %s" % K["bad"])
    check(K["general50"] == ["ok", "levels", 50, 100, 100], "K: the general Max level 50 leaves the class table alone: %s" % K["general50"])
    check(K["read"] == ["4", str(round(100 * 100 / (50 + 100 + 160 + 220))), "2", "100", "100"], "K: customRead from a History copy: %s" % K["read"])
    check(K["check"] == [True, True, True], "K: checkLevels guards levels.class too")
    check(D["kill"] == O["kill"] and D["base"] == O["base"] and D["other"] == O["other"], "K: kill XP at the defaults = 0.4.12's: %s" % D["kill"])
    check(D["paid"] == O["paid"], "K: grants / crafting / heal XP paid = 0.4.12's: %s" % D["paid"])
    print("K. rows 180 = 0.4.12's; class curve rows cut / raise / scale / read; XP maths = 0.4.12")
    # ---------------------------------------------------------------- F
    diff = bc["diff"]
    beyond = dict((n.split("/")[-1][:-6], d) for n, d in diff.items() if set(d["changed"]) != set(d["vo"]) or d["new"] or d["gone"]
                  or d["fields_new"] or d["fields_gone"])
    vonly = sorted(n.split("/")[-1][:-6] for n in diff if n.split("/")[-1][:-6] not in beyond)
    want_beyond = {"ManaRegen", "SkyySkillsPlugin", "ManaCmd", "Acro"}             # 0.4.13 fix round: + ManaCmd (state line), Acro (prune)
    check(set(beyond) == want_beyond, "F: classes changed beyond the version string: %s (unexpected %s, missing %s)" % (sorted(beyond), sorted(set(beyond) - want_beyond), sorted(want_beyond - set(beyond))))
    check(bc["only_new"] == ["com/skyy/skills/CombatFn.class"] and bc["only_old"] == [], "F: + CombatFn only: %s %s" % (bc["only_new"], bc["only_old"]))
    mr = beyond.get("ManaRegen", {})
    mr_ch = sorted(k.split("(")[0] for k in mr.get("changed", []) if k not in mr.get("vo", []))
    check(sorted(k.split("(")[0] for k in mr.get("new", [])) == ["carried", "carry", "combat", "combatLeft", "combatNow", "delayOf", "nsBetween", "stateLine"]
          and not mr.get("gone") and mr_ch in (["amount", "rates", "state", "text", "tick"], ["<clinit>", "amount", "rates", "state", "text", "tick"])
          and sorted(f.split(" ")[0] for f in mr.get("fields_new", [])) == ["CARRY", "CARRY_CAP", "CARRY_SLACK", "CFAILED_ONCE", "CMB", "KFAILED_ONCE", "NDLY",
                                                                             "NDLY_CAP", "STALE_MS", "WINDOW"] and not mr.get("fields_gone"),
          "F: ManaRegen: + delayOf / combatLeft / combat / combatNow / nsBetween / carried / carry / stateLine, + CMB / NDLY / WINDOW / CFAILED_ONCE / "
          "STALE_MS / NDLY_CAP / CARRY / KFAILED_ONCE / CARRY_CAP / CARRY_SLACK; changed: tick, state, rates, amount, text (+ the field initializer); "
          "nothing gone: new %s changed %s fields %s" % (mr.get("new"), mr_ch, mr.get("fields_new")))
    pl_ = beyond.get("SkyySkillsPlugin", {})
    check(sorted(k for k in pl_.get("changed", []) if k not in pl_.get("vo", [])) == ["setup()V", "shutdown()V"] and not pl_.get("new") and not pl_.get("gone")
          and not pl_.get("fields_new") and not pl_.get("fields_gone"), "F: SkyySkillsPlugin: only setup / shutdown changed: %s" % pl_)
    for cn_, want_m in (("ManaCmd", ["execute"]), ("Acro", ["retainOnline"])):
        d_ = beyond.get(cn_, {})
        check(sorted(k.split("(")[0] for k in d_.get("changed", []) if k not in d_.get("vo", [])) == want_m and not d_.get("new") and not d_.get("gone")
              and not d_.get("fields_new") and not d_.get("fields_gone"), "F: %s: only %s changed (0.4.13 fix round): %s" % (cn_, want_m, d_))
    check(bc["calls"]["global_lookups"] == [], "F: no (J) level lookup is called anywhere in the new jar: %s" % bc["calls"]["global_lookups"][:3])
    for cls in ("ManaRegenFn", "ClassCurve", "AcroSys", "SkillDefs", "SkillCfg", "SkillStore", "Overall", "SkillXp", "Perks", "SkillKit",
                "SkillsCmd", "SkillTick", "CfgRows", "CfgFile", "ReloadCmd", "KillSys", "HealXp", "BridgeXp", "BridgeTask", "HealMig", "ManaMig", "ManaGuard",
                "ManaCost", "SkillHealFn", "SkillAddFn", "SkillCraftFn", "SkillXpFn", "SkillFn", "OverallFn", "Xbow", "XbowCfg", "DivCfg", "OverallCfg",
                "BreakSys", "HarvestSys", "SkillClass", "CfgHist", "CfgLog", "SkillBonus", "SkillsPage", "StatsPage", "OverallPage", "TopCmd", "SkillMsg", "PartyXp"):
        check("com/skyy/skills/%s.class" % cls in bc["same"] or cls in vonly, "F: %s byte-identical (or the version string only)" % cls)
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    mo, mn = json.loads(zo.read("manifest.json")), json.loads(zn.read("manifest.json"))
    kd = sorted(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k))
    check(kd == ["Name", "Version"] and mn["Description"] == mo["Description"], "F: manifest: only %s differ (the Description is 0.4.12's)" % kd)
    nonclass = sorted(n for n in set(zo.namelist()) | set(zn.namelist()) if not n.endswith(".class") and n != "manifest.json"
                      and (n not in zo.namelist() or n not in zn.namelist() or zo.read(n) != zn.read(n)))
    check(nonclass == [], "F: every non-class entry byte-identical (the 40 spell overrides): %s" % nonclass[:5])
    print("F. class bytes: + CombatFn; changed beyond the version: %s; version only %d (%s); byte-identical %d"
          % (", ".join(sorted(beyond)), len(vonly), ", ".join(vonly), len([n for n in bc["same"]])))
    # ---------------------------------------------------------------- X: the review fixes
    X = D["X"]
    on = X["ov_none"]
    check(on["err"] is None and on["max"] == 0 and on["title"] and on["sub"] and on["line"] and not on["maxlay"] and not on["the_highest"]
          and on["next"] == ["Nothing - no skill counts toward the Overall Level"],
          "X R1: no counted skill: 'Level 0 of 0', 'No skill counts ...', one 'Nothing - no skill counts' line, NOT the max layout: %s" % on)
    om = X["ov_max"]
    check(om["err"] is None and om["max"] == 100 and om["title"] and om["maxlay"] and om["the_highest"] and om["next"] == [],
          "X R1: a maxed player (Mining 100 only) still gets 'Level 100 of 100' + 'Max Overall Level reached': %s" % om)
    oi = X["ov_mid"]
    check(oi["err"] is None and oi["title"] and not oi["maxlay"] and oi["next_hd"] and oi["next"] and not any("no skill counts" in x for x in oi["next"]),
          "X R1: Mining 15 only: 'Level 15 of 100' + 'Overall Level 16 adds' with its lines: %s" % oi)
    ac = bc["calls"]["acrosys"]
    check("methods" not in ac and len(ac["ManaRegen.tick"]) == 1 and all(len(ac[k]) >= 1 for k in ("Acro.state", "AcroCfg.ENABLED", "Acro.move", "Acro.falls", "Brew.tick", "Xbow.tick", "Perks.tick"))
          and ac["ManaRegen.tick"][0] < min(ac["Acro.state"][0], ac["AcroCfg.ENABLED"][0], ac["Acro.move"][0], ac["Acro.falls"][0], ac["Brew.tick"][0], ac["Xbow.tick"][0]),
          "X R3: AcroSys.tick calls ManaRegen.tick before Acro.state / the Acrobatics block / Brew.tick / Xbow.tick (instruction order): %s" % ac)
    cp = X["compact"]
    check(cp == ["Mana Regen +0% (no boosts). Refill 5/s, in combat 2.5/s (50%).", "Mana Regen +20% (SkyyGear=+20). Refill 6/s, in combat 3/s (50%).",
                 "Mana Regen +20% (SkyyGear=+20). Refill 6/s, in combat none (vanilla).", "Mana Regen +0% (no boosts). In combat 50% of the normal refill.",
                 "Mana Regen +0% (no boosts). In combat no refill (vanilla).", "Mana Regen +0% (no boosts). Refill 5/s, in combat 5/s (100%)."],
          "X R4: ManaRegen.compact lines (vanilla 5/s; +20%%; in-combat 0%%; rate unknown; null sources): %s" % cp)
    cm, cl, co, c2 = X["compact_many"], X["compact_long"], X["compact_odd"], X["compact_two"]
    check(cm == "Mana Regen +1000% (Source00=+0, Source01=+1, Source02=+2, +9 more). Refill 55/s, in combat 55/s (100%)."
          and cl == "Mana Regen +5% (1 source). Refill 5.25/s, in combat 2.625/s (50%)."
          and co == "Mana Regen +333.333% (Source00=+0, Source01=+1, +10 more). Refill 14.444/s, in combat 7.944/s (55%)."
          and c2 == "Mana Regen +45% (SkyyAccessories=+25, SkyyGear=+20). Refill 7.25/s, in combat 3.625/s (50%)." and X["compact_worst"] <= 110,
          "X R4: 12 sources at +1000%% (+9 more), one 64-character source (1 source), odd numbers, two that fit; 400 random lists: longest %d (<= 110): %r / %r / %r / %r"
          % (X["compact_worst"], cm, cl, co, c2))
    act, act1 = X["action"], X["action1"]
    vr = X["vanilla_rate"]
    tail = ("Refill %s/s" % ("%g" % (vr * 1.2))) if vr > 0 else "In combat 50% of the normal refill."
    check(act[0] == "ok" and len(act[2]) <= 110 and act[2].startswith("Mana Regen +98% (") and "+" in act[2] and "more)" in act[2]
          and act1.startswith("Mana Regen +20% (SkyyGear=+20). ") and tail in act1 and len(act1) <= 110
          and X["action_null"][0] == "ok" and X["action_null"][2].startswith("In game: your own. Mana Regen +0% (no boosts). ") and len(X["action_null"][2]) <= 110,
          "X R4: the Server Setup action answers the compact line (13 sources: %d characters; vanilla rate %s): %r / %r / %r" % (len(act[2]), vr, act[2], act1, X["action_null"][2]))
    check("Mana Regen boosts +20% (SkyyGear=+20)" in X["text1"] and "In combat: 50% of (vanilla + boosts)" in X["text1"]
          and X["text1"].endswith(". Charging - Mana still regenerates (the normal refill out of combat, the in-combat refill in combat).")
          and "Never while charging" not in X["text1"],
          "X R4: /skills mana keeps the full text (0.4.13: 'Charging - Mana still regenerates' instead of 'Never while charging'): %r" % X["text1"])
    s150, s100 = X["scale150"], X["scale100"]
    check(s150["r"][:2] == ["ok", "150"] and s150["ecum1"] == 50 and s150["ccum1"] == 75 and "needs 75" not in s150["r"][2]
          and s150["r"][2] == "Class level curve size: 150%% - class skill 1 at %s XP, 20 at %s, 100 at %s in total. Saved (applies now)." % tuple(s150["eff"])
          and s150["eff"][0] == "50" and s150["eff"][1] == "32.3k",
          "X R5: Class level curve size 150%%: the EFFECTIVE totals (class skill 1 at 50 XP - capped by the other list - not the list's 75): %s" % s150)
    check(s100["r"] == ["ok", "100", "Class level curve size: 100% - class skill 1 at 50 XP, 20 at 21.5k, 100 at 6.62m in total. Saved (applies now)."] and s100["same_list"],
          "X R5: back to 100%%: %s" % s100)
    check(X["scale_max10"] == ["ok", "Class level curve size: 100% - class skill 1 at 50 XP, 10 at 3510 in total. Saved (applies now)."],
          "X R5: class max 10: no '20 at': %s" % X["scale_max10"])
    check(X["scale_same"] == ["ok", "Class level curve size: 120% - not in use while Class skills use the other list is on. Saved (applies now).", True],
          "X R5: sameAsOthers on: the class list is not in use: %s" % X["scale_same"])
    check(X["pub_custom"] and X["pub_reload"], "X R9: SkillKit.customSet (a curve row) and SkillKit.reload clear SkillStore.PUBLISHED: %s %s" % (X["pub_custom"], X["pub_reload"]))
    pe = X["pub_e2e"]
    check("Divinity:28" in pe[0] and pe[1] and "Divinity:28" in pe[2] and not pe[3] and pe[4] == 20 and "Divinity:20" in pe[5] and pe[6],
          "X R9: skill:<uuid> Divinity:28 -> Class max level 20 -> the next publishOnline republishes Divinity:20: %s" % pe)
    kr, kc, rc, rb = bc["calls"]["kit_reload"], bc["calls"]["kit_custom"], bc["calls"]["reload_cmd"], bc["calls"]["republish_body"]
    check(len(kr.get("SkillStore.republishAll", [])) == 1 and len(kr.get("SkillCfg.load", [])) == 1 and kr["SkillCfg.load"][0] < kr["SkillStore.republishAll"][0]
          and len(rc.get("SkillStore.republishAll", [])) == 1 and len(rc.get("SkillCfg.load", [])) == 1 and rc["SkillCfg.load"][0] < rc["SkillStore.republishAll"][0]
          and len(kc.get("SkillStore.republishAll", [])) == 1 and kc["SkillStore.republishAll"][0] > max(kc["SkillDefs.setTable"] + kc["SkillDefs.setClassTable"])
          and len(kc.get("SkillKit.classTotals", [])) == 1 and kc["SkillKit.classTotals"][0] > max(kc["SkillDefs.setClassTable"]),
          "X R9 / R5: republishAll after SkillCfg.load in SkillKit.reload and /skills reload, after the table set in customSet (classTotals too): %s %s %s" % (kr, rc, kc))
    check(len(rb.get("monitorenter", [])) == 1 and len(rb.get("invoke", [])) == 1, "X R9: republishAll = one call inside the PUB lock: %s" % rb)
    mt = bc["calls"]["mr_tick"]

    def first(k):
        return mt[k][0] if mt.get(k) else -1
    order = ["ManaRegen.CLK", "TimeResource.getNow", "TimeResource.getTimeDilationModifier", "ManaRegen.carry(", "EntityStatMap.getComponentType",
             "getRegeneratingValues", "ManaRegen.combat(", "ManaRegen.IN_COMBAT", "ManaRegen.total(", "getMax", "ManaRegen.rates(", "ManaRegen.amount(", "addStatValue"]
    check("methods" not in mt and all(len(mt[k]) >= 1 for k in order) and len(mt["ManaRegen.combat("]) == 1 and len(mt["addStatValue"]) == 1
          and len(mt["ManaRegen.carry("]) == 1 and len(mt["TimeResource.getNow"]) == 1
          and [first(k) for k in order] == sorted(first(k) for k in order) and len(mt["getRegeneratingValues"]) == 1,
          "X 0.4.13: ManaRegen.tick = pulse gate (CLK) -> the clock + its dilation -> carry(...) -> the Mana value / entries (read once) -> combat(...) "
          "-> IN_COMBAT / total -> max -> amount(rates(...)) -> addStatValue: %s" % mt)
    mk_ = bc["calls"]["mr_carry"]
    seq_ = ["getLastDamageTime", "setLastDamageTime", "getLastCombatAction", "setLastCombatAction", "getLastChargeTime", "setLastChargeTime"]
    cr_ = mk_.get("ManaRegen.carried(", [])
    check("methods" not in mk_ and all(len(mk_[k]) == 1 for k in seq_) and len(cr_) == 3 and len(mk_["System.nanoTime"]) == 1
          and all(len(mk_[k]) >= 1 for k in ("DamageDataComponent.getComponentType", "Store.getExternalData", "EntityStore.getWorld", "World.getName",
                                             "ManaRegen.CARRY", "SkillCfg.warn"))
          and mk_["getLastDamageTime"][0] < cr_[0] < mk_["setLastDamageTime"][0] < mk_["getLastCombatAction"][0] < cr_[1] < mk_["setLastCombatAction"][0]
          < mk_["getLastChargeTime"][0] < cr_[2] < mk_["setLastChargeTime"][0] < mk_["ManaRegen.CARRY"][-1],
          "X fix F1: carry reads the world name (getExternalData -> getWorld -> getName), runs each of the three stamps through carried() between its "
          "get and set, then writes the record: %s" % mk_)
    ms_ = bc["calls"]["mr_state"]
    check("methods" not in ms_ and len(ms_["NoDamageTakenCondition"]) == 1 and len(ms_["ChargingCondition"]) == 1 and len(ms_["Condition.eval0("]) == 1
          and len(ms_["Condition.eval("]) == 1 and ms_["Condition.eval("][0] < ms_["NoDamageTakenCondition"][0] < ms_["ChargingCondition"][0] < ms_["Condition.eval0("][0],
          "X charging: state() = eval, then NoDamageTaken, then ChargingCondition + its eval0 (charging = an inverse Charging whose eval0 is true): %s" % ms_)
    mc_ = bc["calls"]["mcmd"]
    check("methods" not in mc_ and len(mc_["ManaRegen.rates("]) == 1 and len(mc_["ManaRegen.stateLine("]) == 1 and len(mc_["ManaRegen.text("]) == 1
          and mc_["ManaRegen.rates("][0] < mc_["ManaRegen.stateLine("][0] < mc_["ManaRegen.text("][0] and mc_["holding a charge"] == []
          and mc_["IN COMBAT (vanilla"] == [],
          "X charging: /skills mana = rates -> ManaRegen.stateLine -> text (the 0.4.12 'holding a charge' lines are gone from ManaCmd): %s" % mc_)
    ar_ = bc["calls"]["acro_retain"]
    check("methods" not in ar_ and len(ar_["ManaRegen.CLK"]) == 1 and len(ar_["ManaRegen.CMB"]) == 1 and len(ar_["ManaRegen.CARRY"]) == 1
          and ar_["ManaRegen.CLK"][0] < ar_["ManaRegen.CMB"][0] < ar_["ManaRegen.CARRY"][0],
          "X fix F2: Acro.retainOnline prunes ManaRegen.CLK, then CMB, then CARRY: %s" % ar_)
    ps, pd = bc["calls"]["pl_setup"], bc["calls"]["pl_shutdown"]
    check("methods" not in ps and "methods" not in pd and len(ps['"skill:fn:combat"']) == 1 and len(ps["Class com.skyy.skills.CombatFn"]) == 1
          and len(ps['"skill:fn:manaregen"']) == 1 and ps['"skill:fn:manaregen"'][0] < ps['"skill:fn:combat"'][0] < ps["Class com.skyy.skills.CombatFn"][0]
          and len(pd['"skill:fn:combat"']) == 1 and pd['"skill:fn:manaregen"'][0] < pd['"skill:fn:combat"'][0],
          "X 0.4.13: setup() puts skill:fn:combat = new CombatFn() right after skill:fn:manaregen; shutdown() removes it right after: %s %s" % (ps, pd))
    print("X. review fixes: Overall page without counted skills not max; Mana refill first in AcroSys.tick; compact action %d chars; effective class totals; skill:<uuid> republished;"
          " 0.4.13 tick order + skill:fn:combat put / removed; fix round: carry / state / stateLine / prune bytecode" % len(act[2]))
    check_fix_round(D, O, au, new)
    return finish()


def _cl(el):
    """combatLeft in ms for el ns since the hit (vanilla's 6 s): 0 at / after 6 s"""
    return 0 if el >= NDT_NS else -(-(NDT_NS - el) // 1000000)


def check_fix_round(D, O, au, new):
    """the 0.4.13 fix round's sections Y (F1 carry + F2 prune), H (charging), Z (engine-access audit) - see the module docstring"""
    # ---------------------------------------------------------------- Y pure
    Y = D["Y"]
    check("error" not in Y, "Y: the pure carry cases ran: %s" % Y.get("error"))
    if "error" not in Y:
        got = dict((n_, r_) for n_, r_ in Y["cases"])
        bad = [(c[0], got.get(c[0]), c[8], carried_py(*c[1:8])) for c in CARRY_CASES if got.get(c[0]) != c[8] or carried_py(*c[1:8]) != c[8]]
        check(len(Y["cases"]) == len(CARRY_CASES) == 29 and not bad,
              "Y: ManaRegen.carried on %d named cases = the hand-written expectation (and the Python model): %s" % (len(CARRY_CASES), bad[:3]))
        check(Y["overflow"] == "MIN", "Y: a recorded stamp whose distance to the clock overflows a long (Instant.MIN + 1 s) = Instant.MIN: %s" % Y["overflow"])
        check(Y["nsBetween"] == [9223372036854775807, -9223372036854775808, CLK_A - CLK_B],
              "Y: nsBetween never throws (an overflow = the far end of a long): %s" % Y["nsBetween"])
        rbad = [(c, r_, carried_py(*c)) for c, r_ in Y["random"] if carried_py(*c) != r_]
        outc = {"keep": 0, "MIN": 0, "now": 0, "carried": 0}
        for c, r_ in Y["random"]:
            outc["keep" if r_ == "keep" else "MIN" if r_ == "MIN" else "now" if r_ == c[2] else "carried"] += 1
        check(len(Y["random"]) == 3000 and not rbad and min(outc.values()) >= 10,
              "Y: 3000 random cases = the Python model of the rule (outcomes %s): %s" % (outc, rbad[:2]))
        check(Y["consts"] == [CARRY_CAP, CARRY_SLACK], "Y: CARRY_CAP 1 hour, CARRY_SLACK 1 s (ns): %s" % Y["consts"])
    pr_ = Y.get("prune", {})
    check(pr_.get("pre") == [True, True, True] and pr_.get("post") == [True, False, True, False, True, False],
          "Y F2: Acro.retainOnline drops an offline player's ManaRegen.CMB / CARRY / CLK entries and keeps the online one's: %s" % pr_)
    # ---------------------------------------------------------------- Y end to end (the real tick across worlds; 0.4.12 = the control)
    Sn, So = D["Ysw"], O["Ysw"]
    check("error" not in Sn and "error" not in So, "Y: the world-switch script ran through the real ManaRegen.tick on both jars: %s / %s"
          % (Sn.get("error"), So.get("error")))
    if "error" in Sn or "error" in So:
        return
    rows, rows_o = Sn["rows"], So["rows"]
    check(Sn["warn"] == [False, False] and So["warn"][0] is False, "Y: nothing logged 'failed' (tick / carry): %s %s" % (Sn["warn"], So["warn"]))

    def idx(rs, step):
        return next((k for k, r in enumerate(rs) if r["step"] == step), None)
    ks = dict((st, idx(rows, st)) for st in ("H1", "H2", "H3", "H4", "G", "I1", "I2", "B", "L0"))
    check(all(v is not None and v > 0 for v in ks.values()) and len(rows) == len(rows_o) and [r["step"] for r in rows] == [r["step"] for r in rows_o],
          "Y: every step pulsed on both jars, the same pulses: %s" % ks)
    if not all(v is not None and v > 0 for v in ks.values()):
        return
    # every first pulse in a new world: the three stamps = the rule applied to the records (the old world's clock + nanoTime at its last
    # pulse, this pulse's clock + nanoTime) - exactly, to the nanosecond
    hop = {}
    for st in ("H1", "H2", "H3", "H4"):
        k = ks[st]
        prev, cur = rows[k - 1], rows[k]
        exp = [carried_py(cur["before"][i], cur["rec"][0], cur["now"], 1.0, cur["rec"][2], prev["rec"], i) for i in range(3)]
        exp = [cur["before"][i] if exp[i] == "keep" else exp[i] for i in range(3)]
        hop[st] = {"exp": exp, "after": cur["after"], "gap": cur["rec"][2] - prev["rec"][2], "prev": prev, "cur": cur}
        check(cur["after"] == exp and cur["rec"][0] != prev["rec"][0],
              "Y %s: the first pulse in %s rewrites the stamps by the rule (from %s, wall gap %.3f s): got %s want %s"
              % (st, cur["w"], prev["w"], hop[st]["gap"] / 1e9, cur["after"], exp))
    t0 = Sn["t0"]
    h1 = hop["H1"]
    el1 = h1["cur"]["now"] - h1["after"][0]
    want_el1 = (h1["prev"]["rec"][1] - t0) + h1["gap"]
    # (the last pulse in 'default' falls 54-60 ticks of 1/30 s after the hit; the sleep is 0.25 s)
    check(el1 == want_el1 and h1["after"][0] == h1["after"][1] == h1["after"][2] and 53 * TICK_NS <= el1 - h1["gap"] <= 61 * TICK_NS
          and SEC // 4 <= h1["gap"] < 2 * SEC,
          "Y H1 ('default' 09:12 -> island 03:13): all three stamps = island now - (the old clock's %.3f s since the hit + %.3f s asleep) = %.3f s ago"
          % ((h1["prev"]["rec"][1] - t0) / 1e9, h1["gap"] / 1e9, el1 / 1e9))
    c1 = h1["cur"]
    check(c1["cmb"] == _cl(el1) and abs(h1["prev"]["cmb"] - h1["gap"] / 1e6 - c1["cmb"]) <= 1.0 and abs(c1["fn"] - c1["cmb"]) <= 250 and c1["state"] == 1,
          "Y H1: the countdown continues: last pulse in 'default' %d ms - %.1f ms asleep = %d ms in the island (skill:fn:combat %d), still in combat"
          % (h1["prev"]["cmb"], h1["gap"] / 1e6, c1["cmb"], c1["fn"]))
    s1 = h1["after"][0]
    i1 = [r for r in rows[ks["H1"]:] if r["step"] in ("H1", "I1")]
    i1_bad = [(r["now"] - s1, r["state"], r["cmb"], r["h15"]) for r in i1
              if r["state"] != (1 if r["now"] - s1 < NDT_NS else 0) or r["cmb"] != _cl(r["now"] - s1) or r["h15"] != (r["now"] - s1 >= 15 * SEC)
              or (r["step"] == "I1" and r["after"] != r["before"])]
    turn6 = next((r for r in i1 if r["state"] == 0), None)
    turn15 = next((r for r in i1 if r["h15"]), None)
    check(len(i1) >= 70 and not i1_bad and turn6 is not None and turn15 is not None and NDT_NS <= turn6["now"] - s1 < NDT_NS + SEC // 4
          and 15 * SEC <= turn15["now"] - s1 < 15 * SEC + SEC // 4,
          "Y I1: 15 s on the island: in combat / the countdown / Health's NoDamageTaken 15 s follow the REAL time since the hit at every pulse - "
          "combat ends %.3f s and Health's pause %.3f s after the hit (the stamps stay put): %s"
          % ((turn6["now"] - s1) / 1e9 if turn6 else -1, (turn15["now"] - s1) / 1e9 if turn15 else -1, i1_bad[:3]))
    o1 = [r for r in rows_o[ks["H1"]:] if r["step"] in ("H1", "I1")]
    check(o1 and all(r["state"] == 1 and not r["h15"] and r["after"][0] == t0 for r in o1),
          "Y control (0.4.12): on the island the 'default' stamp stays and every pulse for 15 s says IN COMBAT, Health's 15 s never ends (F1)")
    h2 = hop["H2"]
    tb = h2["prev"]["before"][0]
    el2 = h2["cur"]["now"] - h2["after"][0]
    check(el2 == (h2["prev"]["rec"][1] - tb) + h2["gap"] and 23 * TICK_NS <= el2 - h2["gap"] <= 31 * TICK_NS and h2["cur"]["state"] == 1
          and h2["cur"]["cmb"] == _cl(el2) and abs(h2["prev"]["cmb"] - h2["gap"] / 1e6 - h2["cur"]["cmb"]) <= 1.0,
          "Y H2 (island -> 15:00, a bigger clock): the island hit is %.3f s old in 'big' (%d ms left, was %d before the %.3f s hop), still in combat"
          % (el2 / 1e9, h2["cur"]["cmb"], h2["prev"]["cmb"], h2["gap"] / 1e9))
    o2 = rows_o[ks["H2"]]
    check(o2["state"] == 0 and o2["after"][0] == tb, "Y control (0.4.12): in 'big' the island stamp looks 11.8 hours old - out of combat at once (the teleport-regen hole)")
    i2 = [r for r in rows[ks["H2"]:ks["L0"]]]
    s2 = h2["after"][0]
    i2_bad = [(r["now"] - s2, r["state"], r["cmb"]) for r in i2 if r["state"] != (1 if r["now"] - s2 < NDT_NS else 0) or r["cmb"] != _cl(r["now"] - s2)]
    check(len(i2) >= 25 and not i2_bad and any(r["state"] == 0 for r in i2), "Y I2: the countdown in 'big' runs out on time: %s" % i2_bad[:3])
    h3 = hop["H3"]
    late = Sn["late"]
    el3 = h3["cur"]["now"] - h3["after"][0]
    check(h3["cur"]["before"][0] == late and late != h3["prev"]["rec"][4] and late > h3["prev"]["rec"][1]
          and el3 == h3["gap"] - (late - h3["prev"]["rec"][1]) and 0 < late - h3["prev"]["rec"][1] <= SEC // 10 and h3["cur"]["cmb"] == _cl(el3),
          "Y H3: a hit in 'big' one tick after its last pulse, then island: carried as the old world's (%.1f ms after that pulse; %.3f s old -> %d ms left)"
          % ((late - h3["prev"]["rec"][1]) / 1e6, el3 / 1e9, h3["cur"]["cmb"]))
    o3 = [r for r in rows_o[ks["H3"]:ks["H4"]]]
    check(o3 and all(r["state"] == 1 for r in o3), "Y control (0.4.12): that 'big' stamp is hours in the island's future - in combat at every island pulse")
    h4 = hop["H4"]
    fresh = Sn["fresh"]
    check(h4["cur"]["before"][0] == fresh and h4["after"][0] == fresh and h4["cur"]["cmb"] == _cl(h4["cur"]["now"] - fresh)
          and h4["after"][1] != h4["cur"]["before"][1] and h4["after"][2] != h4["cur"]["before"][2],
          "Y H4: a FRESH hit in 'default' before its first pulse is left alone (%d ms left); the other two stamps (still the island's) are carried"
          % h4["cur"]["cmb"])
    g = rows[ks["G"]]
    check(g["before"][0] == Sn["future"] and g["after"][0] == g["now"] and g["cmb"] == 6000 and g["state"] == 1,
          "Y G: a stamp 1 hour in the future of the same world's clock becomes now (6000 ms of combat, never stuck): %s" % g["after"])
    end_n, end_o = rows[-1], rows_o[-1]
    check(end_n["state"] == 1 and end_n["cmb"] == _cl(end_n["now"] - g["now"]) and end_o["state"] == 1 and end_o["after"][0] == Sn["future"],
          "Y G: 1 s later 0.4.13 counts down (%d ms); 0.4.12 keeps the future stamp - in combat for an hour" % end_n["cmb"])
    print("Y. world switch: 29 named + 3000 random carry cases; real tick 'default' 09:12 -> island 03:13 (%.3f s since the hit carried, combat ends "
          "%.3f s / Health 15 s %.3f s after it), -> 15:00 (%.3f s), late hit %.3f s, fresh hit kept, future stamp = now; 0.4.12 stuck / hole; F2 prune"
          % (el1 / 1e9, (turn6["now"] - s1) / 1e9 if turn6 else -1, (turn15["now"] - s1) / 1e9 if turn15 else -1, el2 / 1e9, el3 / 1e9))
    # ---------------------------------------------------------------- H pure
    H = D["H"]
    check("error" not in H, "H: the charging pure checks ran: %s" % H.get("error"))
    if "error" not in H:
        R5 = {0: [5.0, 5.0, 0.0, 0.0, 0.0], 1: [5.0, 0.0, 5.0, 0.0, 0.0], 2: [5.0, 0.0, 0.0, 0.0, 0.0], 3: [5.0, 0.0, 0.0, 5.0, 0.0], 4: [5.0, 0.0, 5.0, 0.0, 5.0]}
        want_ev = {"out": [0, R5[0], True], "chg_out": [3, R5[3], False], "chg_in": [4, R5[4], False], "in": [1, R5[1], False],
                   "dead_chg": [2, R5[2], False], "dead_chg_in": [2, R5[2], False], "dead_chg_first": [2, R5[2], False],
                   "noninv_fail": [2, R5[2], False], "noninv_pass": [0, R5[0], True], "never_chg": [3, R5[3], False],
                   "edge6_chg": [3, R5[3], False], "edge5999_chg": [4, R5[4], False]}
        evb = dict((k, (H["ev"].get(k), v)) for k, v in want_ev.items() if H["ev"].get(k) != v)
        check(not evb, "H: state / rates / vanilla's allConditionsMet on real conditions: charging out 3, charging in combat 4 (6 s edge exact), dead + "
                       "charging 2 (whatever the order), a non-inverse Charging that fails 2, passing 0: %s" % evb)
        a = H["amount"]
        want_a = {"chg_out_p0": 5.0, "chg_out_p20": 6.0, "chg_out_p1000": 55.0, "chg_out_p5000": 55.0, "chg_out_neg": 5.0, "chg_out_pulse": 1.0,
                  "chg_out_f0": 5.0, "chg_in_p0": 2.5, "chg_in_p20": 3.0, "chg_in_f0": 0.0, "chg_in_f100": 5.0, "chg_in_pulse": 0.5, "dead": 0.0,
                  "len3": 0.0, "len4": 6.0, "cap": 0.5, "full": 0.0}
        check(a == want_a, "H: amount(): charging out of combat = 5 x (1 + MR) a second (0.2 s = +1 like vanilla's step; in-combat %% does not "
                           "touch it), charging in combat = F x 5 x (1 + MR), dead 0, a 3-entry array as 0.4.12, never past max: %s"
              % dict((k, (a.get(k), v)) for k, v in want_a.items() if a.get(k) != v))
        sbad, ndbl = [], 0
        for dead, chg_now, ago, p, f_, st_, r_, van, ours in H["sweep"]:
            P = min(max(p, 0.0), 1000.0) / 100.0
            F = min(max(f_, 0), 100) / 100.0
            inc = ago is not None and ago < NDT_NS
            total = (5.0 if van else 0.0) + ours
            want = 0.0 if dead else (5.0 * (1.0 + P) * F if inc else 5.0 * (1.0 + P))
            if abs(total - want) > 1e-4 * max(1.0, want) or van != ((not dead) and (not chg_now) and (not inc)):
                sbad.append([dead, chg_now, ago, p, f_, st_, van, ours, total, want])
            if van:
                ndbl += 1
                if st_ != 0 or abs(ours - 5.0 * P) > 1e-4 * max(1.0, 5.0 * P):
                    sbad.append(["double", dead, chg_now, ago, p, f_, st_, ours])
        check(len(H["sweep"]) == 720 and not sbad and ndbl > 0,
              "H: 720 cases (dead x charging x 9 hit times x 5 boosts x 4 in-combat settings): vanilla's own entry + SkyySkills = 5 x (1 + MR) out of "
              "combat, F x 5 x (1 + MR) in combat - charging or not - 0 dead; where vanilla pays SkyySkills adds only the boost (%d cases): %s" % (ndbl, sbad[:3]))
        want_l = ["out of combat - vanilla refills 5/s, SkyySkills adds 1/s", "out of combat - vanilla refills 5/s",
                  "charging - Mana still regenerates: SkyySkills refills 6/s (vanilla pauses while you charge)",
                  "charging - Mana still regenerates: SkyySkills refills 5/s (vanilla pauses while you charge)",
                  "IN COMBAT (vanilla's 6 s pause) - SkyySkills refills 3/s (50% of 6/s)",
                  "IN COMBAT (vanilla's 6 s pause), charging - Mana still regenerates - SkyySkills refills 3/s (50% of 6/s)",
                  "no refill right now (dead, or another regen condition stops it)", "no Mana pool (max 0) - nothing refills",
                  "no refill right now (dead, or another regen condition stops it)", "IN COMBAT (vanilla's 6 s pause) - SkyySkills refills 0/s (0% of 5/s)",
                  "charging - Mana still regenerates: SkyySkills refills 55/s (vanilla pauses while you charge)"]
        check(H["lines"] == want_l, "H: ManaRegen.stateLine = 0.4.12's /skills mana lines + the charging lines: %s"
              % [(x, y) for x, y in zip(H["lines"], want_l) if x != y])
    cmd = H.get("cmd", {})
    tail_ = ". Charging - Mana still regenerates (the normal refill out of combat, the in-combat refill in combat)."
    want_c = {"chg_out": "[Skills] Mana 10 / 30 - charging - Mana still regenerates: SkyySkills refills 6/s (vanilla pauses while you charge) - last hit 10 s ago",
              "chg_in": "[Skills] Mana 10 / 30 - IN COMBAT (vanilla's 6 s pause), charging - Mana still regenerates - SkyySkills refills 3/s (50% of 6/s) - last hit 2 s ago",
              "dead_chg": "[Skills] Mana 10 / 30 - no refill right now (dead, or another regen condition stops it) - last hit 10 s ago",
              "out": "[Skills] Mana 10 / 30 - out of combat - vanilla refills 5/s, SkyySkills adds 1/s - last hit 10 s ago",
              "in": "[Skills] Mana 10 / 30 - IN COMBAT (vanilla's 6 s pause) - SkyySkills refills 3/s (50% of 6/s) - last hit 2 s ago"}
    cbad = dict((k, cmd.get(k)) for k, v in want_c.items() if not (isinstance(cmd.get(k), list) and len(cmd[k]) == 2 and cmd[k][0] == v
                                                                   and cmd[k][1].startswith("[Skills] Mana Regen boosts +20% (Test=+20). ") and cmd[k][1].endswith(tail_)))
    check("error" not in cmd and not cbad, "H: /skills mana EXECUTED (the real ManaCmd.execute): charging out of combat / in combat / dead / out / in "
                                           "combat lines + text()'s charging sentence: %s" % (cmd.get("error") or cbad))
    check(H.get("text_f0", "").endswith(". Charging - Mana still regenerates out of combat (the normal refill).") and H.get("text_f50", "").endswith(tail_),
          "H: text() at in-combat 0 %%: 'Charging - Mana still regenerates out of combat (the normal refill).': %r" % H.get("text_f0"))
    # ---------------------------------------------------------------- H end to end (the real tick; vanilla modelled per pulse; 0.4.12 = the control)
    Cn, Co = D["Hch"], O["Hch"]
    check("error" not in Cn and "error" not in Co, "H: the charging script ran through the real ManaRegen.tick on both jars: %s / %s" % (Cn.get("error"), Co.get("error")))
    if "error" in Cn or "error" in Co:
        return

    def expect(r, nw):
        step, t, added, secs, van, st_, rates_, since, chg, dead, p, f_ = r
        inc = 0 <= since < NDT_NS
        est = 2 if dead else ((4 if inc else 3) if nw else 2) if chg else (1 if inc else 0)
        er = {0: [5.0, 5.0, 0.0, 0.0, 0.0], 1: [5.0, 0.0, 5.0, 0.0, 0.0], 2: [5.0, 0.0, 0.0, 0.0, 0.0], 3: [5.0, 0.0, 0.0, 5.0, 0.0],
              4: [5.0, 0.0, 5.0, 0.0, 5.0]}[est]
        if not nw:
            er = er[:3]
        pp = min(max(p, 0.0), 1000.0)
        ff = min(max(f_, 0), 100)
        per = er[1] * pp / 100.0 + er[2] * (1.0 + pp / 100.0) * ff / 100.0
        if len(er) > 3:
            per = per + er[3] * (1.0 + pp / 100.0)
        aa = per * secs
        return est, (not dead) and (not chg) and (not inc), er, (f32(aa) if aa > 0.0 else 0.0), per
    steps = {}
    for nm_, rs_, nw in (("new", Cn["rows"], True), ("old", Co["rows"], False)):
        bad_ = []
        for r in rs_:
            if r[3] is None:
                bad_.append(["refill off the pulse", r])
                continue
            est, evan, er, ea, per = expect(r, nw)
            if r[5] != est or r[4] != evan or r[6] != er or r[2] != ea:
                bad_.append([r[0], r[1], r[2], ea, r[5], est, r[4], evan, r[6], er])
            if nw:
                tot = (5.0 if r[4] else 0.0) + per
                steps.setdefault(r[0], set()).add(round(tot, 6))
        check(len(rs_) >= 70 and not bad_, "H %s: at all %d pulses the state, vanilla's allConditionsMet, rates() and the addStatValue amount (the exact "
                                            "float) = the expectation: %s" % (nm_, len(rs_), bad_[:3]))
    want_tot = {"O": {6.0}, "C": {6.0}, "CI": {3.0}, "I": {3.0}, "D": {0.0}, "DN": {0.0}, "R": {6.0, 3.0}, "Z": {5.0}, "ZI": {0.0}}
    check(steps == want_tot or all(steps.get(k) == v or (k == "R" and steps.get(k) <= v) for k, v in want_tot.items()),
          "H new: vanilla + SkyySkills per second by step - out 6 / charging out 6 / charging in combat 3 / in combat 3 / dead 0 / charging at "
          "0 %% + no boosts 5 / charging in combat at 0 %% 0: %s" % steps)
    chg_old = [r for r in Co["rows"] if r[8] and not r[9]]
    chg_new = [r for r in Cn["rows"] if r[8] and not r[9] and r[0] in ("C", "CI", "Z")]
    check(chg_old and all(r[2] == 0.0 and not r[4] for r in chg_old) and chg_new and all(r[2] > 0.0 for r in chg_new),
          "H control (0.4.12): while charging (%d pulses) neither vanilla nor SkyySkills refilled - Skyy's report; 0.4.13 refills at every charging pulse"
          % len(chg_old))
    zz = [r for r in Cn["rows"] if r[0] == "Z"]
    check(zz and all(r[2] > 0.0 and r[10] == 0.0 and r[11] == 0 for r in zz), "H: charging out of combat with no boosts and in-combat 0 %% still "
                                                                            "refills vanilla's 5/s (0.4.12's early return there is gone): %s" % zz[:1])
    print("H. charging: state 3 / 4 on real conditions, 720-case sweep vs vanilla's entry (never double), stateLine + /skills mana executed; real tick "
          "%d pulses per jar - totals by step %s" % (len(Cn["rows"]), dict((k, sorted(v)) for k, v in sorted(steps.items()))))
    # ---------------------------------------------------------------- Z
    check(au["classes"] == new["classes"] and au["refs"] > 3000 and not au["refused"],
          "Z: engine-access audit (MethodHandles.privateLookupIn per class = the JVM's own rules): %d references in %d classes, refused %s"
          % (au["refs"], au["classes"], au["refused"][:5]))
    check(len(au["control"]) == 1 and "sendUpdate" in au["control"][0] and "invokevirtual" in au["control"][0],
          "Z: the control (a class that is no page calling the page's protected sendUpdate) is refused by the same audit: %s" % au["control"])
    check(all(x.startswith("java.") for x in au.get("caller_sensitive", [])),
          "Z: the only references the private lookup cannot resolve are public caller-sensitive JDK methods (checked public instead): %s"
          % au.get("caller_sensitive"))
    print("Z. engine-access audit: %d class / member references in %d classes (ManaRegen %d), 0 refused; control refused; caller-sensitive JDK "
          "calls checked as public: %s" % (au["refs"], au["classes"], au["per"].get("ManaRegen", 0), ", ".join(au.get("caller_sensitive", []))))


def finish():
    if not KEEP and GUARD_OK[0]:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("SkyySkills %s harness:" % VERSION, "PASS" if not FAILS else "FAIL")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
