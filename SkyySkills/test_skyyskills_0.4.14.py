"""SkyySkills 0.4.14 - bare-JVM harness for Skyy's four locks of 2026-10-02 + two fixes (tools/skills_0_4_14_patch.py). Copied forward
from SkyySkills/test_skyyskills_0.4.13.py: every 0.4.13 section still runs against the 0.4.14 jar (the 0.4.12 jar stays the baseline of the
carried sections, as in 0.4.13); the class compare (F), the default file (C) and the rows (K) are against the SET pin 0.4.13.

    python SkyySkills/test_skyyskills_0.4.14.py [--jar <SkyySkills-0.4.14.jar>] [--prev <SkyySkills-0.4.13.jar>] [--old <SkyySkills-0.4.12.jar>]
                                                [--mobs <SkyyMobs jar>] [--dir <scratch>] [--live <Skyy_SkyySkills folder>] [--keep]

Build first (python tools/skills_0_4_14_patch.py, then python SkyySkills/build_skyyskills_0.4.14.py). Child processes start fresh JVMs (the
game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the jars; TEMP / TMP / java.io.tmpdir in the scratch folder). The live
world and Assets.zip are READ ONLY: the Skyy_SkyySkills folder is copied into the scratch folder and only that copy is ever written.
NEW in 0.4.14:
  KX  KILL XP BY MOB LEVEL: MobXp.levelFactor / gapFactor / factor for a grid of mob levels x class skills (= a Python model of Skyy's rule:
      x (1 + 0.05 (L - 1)), gap d = L - S: d > 5 -> 1 + 0.05 (d - 5) at most 3.5, d < -5 -> 1 - 0.05 (-d - 5) at least 0.1), MobXp.pay
      (exact products, the 1e-9 rule, chance rounding: floor / ceil + the mean); Skyy's example EXACTLY: a Lv 33 Skeleton_Scout (178 HP)
      at Divinity 11 = combatXp 36 x 3 x 2.6 x 1.85 = 519.48 (519 or 520, mean 519.48 over 20,000 kills; 0.4.13 = 108); MobXp.levelOf
      through the REAL SkyyMobs 0.1.2 MobLevelFn (its MOBS map) and stand-ins: no bridge, -1, 0, a Long, a String, null, throwing (logged
      once), no UUIDComponent, the wrong world; MobXp.kill end to end on a stand-in store: the killer's award, the party share through the
      real PartyXp.share2 / one2 with members on their OWN class skills (Archer 1, Warrior 30, Priest 40, Archer 60), one out of range, one
      in creative: each member's amount in [floor, ceil] of 0.5 x pay(...) and the means; mob:fn:level missing / the part off = 0.4.13
      exactly (108 + 54 each)
  RL  ROLL LANDINGS on the REAL engine objects (PlayerInput + its SetClientVelocity / SetMovementStates queue, MovementStates, Velocity,
      Player.currentFallDistance, a real EntityStatMap / EntityStatValue, MovementConfig with Assets.zip's Default.json roll numbers through
      the real World.getGameplayConfig -> GameplayConfig -> PlayerConfig -> MovementConfig asset map): the REAL
      DamageSystems$FallDamagePlayers.tick runs first (its Damage recorded by a CommandBuffer stand-in), then RollSys.tick on the same queue:
      for speeds 0..60 x rolling x in fluid x max health, RollSys.damage = the engine's damage exactly, a note exactly when the roll engaged
      (unreduced damage x 100 / max health); queue orders (states before the landing, two landings, velocity only in the component);
      acro.rollBonus 0 / acro.enabled off = no note; the engine's own DependencyGraph sorts RollSys before FallDamagePlayers before
      ProcessPlayerInput from every start order; Acro.noteFall skips the same landing (< 1 s), Acro.falls pays 400 ms later (alive, not in
      water, not creative) x 10 x 1.5 capped 2000, Acro.flush puts it into the store; the numbers table at 100 HP
  GP  GATHERING PACE: mult(level 0-25) for Mining / Foraging / Farming = 3 to level 10, a straight line to 1.5 at 20, 1.5 after; apply()
      on every slot at levels 0-25 (paced slots x mult with the 1e-9 rule and chance rounding, every other slot unchanged); read() clamps
      and the skill list (a non-gathering name warned + skipped), checkSkills; SkillXp.gain (blocks / F-harvests / sickles) paced before the
      tree Wisdom bonus, grants (gain3 bonus off) exact; statsLine at every level; the Stats page lines ("Gathering XP x3 up to level 10,
      then easing to x1.5 by level 20") and the summed tree / tool line now "Bonuses (trees + tools): ..." (Acrobatics keeps "Skill tree:")
  SK  SICKLE SWINGS: Sickle.keys() over a REAL BlockTypeAssetMap of every harvestable block of Assets.zip (StageFinal states, stateless
      blocks, earlier states, non-Farming blocks) with the REAL drop lists (ItemDropList / Multiple / Choice / Single / Droplist containers
      built from Server/Drops) = a Python model (produce key, lowest XP, multi, family, the drop ids); the REAL BlockHarvestUtils.getDrops
      (ItemModule.getRandomItemDrops) rolled per crop: every harvest starts with its produce and is ONE segment; random swings of 2-6 crops
      (+ a sap glob) = one segment per crop (the documented berry-merge case counted); the handlers EXECUTED with queued world tasks: a
      sickle swing pays each crop once (scaled rule XP x the pace), a cancelled pickup / a non-sickle / creative / farming.sickle.enabled
      off / profile:busy / an offline player pay nothing, an F-harvest (HarvestSys <- UseBlockEvent$Post) and an F pickup (BreakSys <-
      BreakBlockEvent with no item) pay NOTHING through Sickle (no double pay), a pickup 300 ms after the F pickup or on another thread
      does; the double drop through a real CombinedItemContainer (only the crop's own stacks, never the sap of the same swing); retain()
  DM  THE COMMENT FIX: DocMig.docUpdate on LF / CRLF / a hand-edited line / a continued value / two lines; DocMig.run once with a verified
      config-history copy, the second run nothing
  C14 the loader: a 0.4.13 file gets the 0.4.14 block once (LF / CRLF, only the missing keys, hand values never rewritten), a full file nothing
  FIX ROUND (reviews 2026-10-03): F1 Sickle.keys() = the 16 StageFinal produce keys only (the loop precondition checked in Assets.zip: every
      Health / Mana / Stamina plant and the cactus flower is stateless and hands back its own item); a sickle swing at a placed Health3 /
      Mana1 / Stamina2 / cactus flower / wild grass / boomshroom pays 0 and doubles nothing (dd.farming 1.0), 10 swings 0, ignorePlaced off 0,
      wheat + Health3 pays the wheat only; F2 a world with fall damage off: the REAL FallDamagePlayers.tick(F, I, Store) processes no landing
      and RollSys notes nothing (fallDamageOn cases + bytecode order); F3 PartyXp.howText with / without mob levels + the party row help;
      F4 gather.boost.early / late 0 -> 0.1 (a skill never stops earning gathering XP), the rows' min 0.1
  M   START TWICE on the scratch copy of the live data: start 1 = the comment fixed + the 0.4.14 block appended (+ the config-history copy),
      nothing else; start 2 changes nothing
NEW in 0.4.13 (carried): W the combat state on REAL engine conditions + skill:fn:combat (CombatFn); E the REAL ManaRegen.tick end to end
  (0.4.12 = the baseline; the 0.4.13 trace = 0.4.14's at every tick); Y world-switch carry + F2 prune; H charging; Z the engine-access audit
Carried forward (vs 0.4.12, as in 0.4.13): A (all three jars load and initialize under -Xverify:all), T, G, P, M (the edited copies), R, B,
  C (restated: the 0.4.14 default = 0.4.13's with the version line, the fixed comment and the 0.4.14 block), K (restated: 195 rows = 0.4.13's
  180 + the 15 new ones), F (restated: 0.4.13 vs 0.4.14), X (+ the 0.4.14 bytecode order checks)
Nothing is deployed. Default scratch folder: tools/dev/scratch/skills0414/harness (deleted at the end unless --keep; --dir must be a folder
INSIDE tools/dev/scratch/). Exit code 1 on any failure.
"""
import os, sys, re, json, math, shutil, subprocess, zipfile, random, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD_VERSION, PREV_VERSION = "0.4.14", "0.4.12", "0.4.13"
PKG = "com.skyy.skills."
CLASS_SLOTS = [5, 6, 7, 8, 9, 14, 15]
OTHER_SLOTS = [0, 1, 2, 3, 4, 10, 11, 12, 13]
ARCHERY, WARRIOR, DIVINITY, MINING, ALCHEMY, SMITHING, COOKING, EXPLORATION = 5, 6, 15, 0, 10, 11, 12, 13
HEALTHS = [-1.0, 2.0, 5.0, 7.0, 20.0, 37.0, 100.0, 250.0, 1000.0, 2500.0, 10000.0]
# the 6 rows 0.4.12 added (0.4.13 added none; 0.4.14 adds the 15 rows of N14_KEYS)
NEW_KEYS = ["levels.class", "levels.class.scale", "levels.class.max", "levels.class.sameAsOthers", "mana.regen.inCombat", "mana.regen.show"]
N14_KEYS = ["combat.levelXp.enabled", "combat.levelBonus", "combat.gap.free", "combat.gap.above", "combat.gap.max", "combat.gap.below",
            "combat.gap.min", "acro.rollBonus", "gather.boost.skills", "gather.boost.early", "gather.boost.earlyUntil", "gather.boost.late",
            "gather.boost.lateFrom", "farming.sickle.enabled", "farming.sickle.items"]
FORAGING, FARMING, ACROBATICS = 1, 2, 4
MREG_DOC_OLD = "# Never above max Mana, never while charging, nothing for a player without Mana (max Mana 0)."
MREG_DOC_NEW = "# Never above max Mana, nothing for a player without Mana (max Mana 0). Charging no longer pauses it (SkyySkills 0.4.13+)."
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


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skills0414", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyySkills-%s.jar" % OLD_VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyySkills-%s.jar" % PREV_VERSION)))
MOBS_JAR = os.path.abspath(arg("--mobs", os.path.join(ROOT, "SkyyMobs", "SkyyMobs-0.1.2.jar")))   # the SET pin of SkyyMobs (mob:fn:level)
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DIR = os.path.abspath(arg("--live", os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyySkills")))
LIVE = os.path.join(LIVE_DIR, "xp.properties")
ASSETS = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")   # read only (in memory)
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
    charging stand-in), FakePerms (PermissionsModule saying yes), LookupIn + BadAccess (the access audit and its control).
    0.4.14: FakeWorld QUEUE mode (world tasks wait for drain(), each in its own try); MapStore / MapChunk / MapCB (components per Ref / per
    entity, the world, invoke recorded - the REAL FallDamagePlayers.tick, RollSys, SickleSys, BreakSys, HarvestSys, PartyXp run on them);
    FakeAssetStore (a concrete AssetStore: the REAL getAssetMap answers a real asset map filled by the harness); FakeHotbar (the item in the
    main hand); FakeInventory (the double drop's storage: a real CombinedItemContainer)."""
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
    # 0.4.14 (section SK): QUEUE = world tasks wait in Q until drain() (the world thread runs them after the event dispatch); each task
    # runs inside its own try (ERR names what threw) - otherwise execute runs at once as in 0.4.13
    w.addField(CtField.make("public static volatile boolean QUEUE = false;", w))
    w.addField(CtField.make("public static final java.util.List Q = java.util.Collections.synchronizedList(new java.util.ArrayList());", w))
    w.addField(CtField.make("public static final java.util.List ERR = java.util.Collections.synchronizedList(new java.util.ArrayList());", w))
    w.addMethod(CtNewMethod.make("public void execute(java.lang.Runnable r) { RAN = RAN + 1; if (QUEUE) Q.add(r); else r.run(); }", w))
    w.addMethod(CtNewMethod.make("""public static int drain() {
  int n = 0;
  while (!Q.isEmpty()) {
    java.lang.Runnable r = (java.lang.Runnable) Q.remove(0);
    try { r.run(); } catch (Throwable t) { ERR.add(r.getClass().getName() + ": " + t); }
    n++;
    if (n > 100000) break;
  }
  return n;
}""", w))
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
    # ---- 0.4.14 stand-ins (all created with Unsafe.allocateInstance - no constructor runs; the maps are set from the harness)
    # MapStore: a Store answering components per Ref (IdentityHashMap Ref -> IdentityHashMap ComponentType -> Component), its world
    # (getExternalData), its clock, and recording invoke(ref, event)
    ms_ = cp.makeClass("skyytest.MapStore")
    ms_.setSuperclass(cp.get("com.hypixel.hytale.component.Store"))
    for decl in ("java.util.Map comps", "java.lang.Object ext", "com.hypixel.hytale.component.Resource time", "java.util.List events"):
        ms_.addField(CtField.make("public %s;" % decl, ms_))
    ms_.addConstructor(CtNewConstructor.make("public MapStore() { super(null, 0, null, null); }", ms_))
    ms_.addMethod(CtNewMethod.make("""public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (this.comps == null || r == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}""", ms_))
    ms_.addMethod(CtNewMethod.make("public java.lang.Object getExternalData() { return this.ext; }", ms_))
    ms_.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Resource getResource(com.hypixel.hytale.component.ResourceType t) { return this.time; }", ms_))
    ms_.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Archetype getArchetype(com.hypixel.hytale.component.Ref r) { return com.hypixel.hytale.component.Archetype.empty(); }", ms_))
    ms_.addMethod(CtNewMethod.make("public void invoke(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.system.EcsEvent e) { if (this.events != null) this.events.add(e); }", ms_))
    ms_.writeFile(out_dir)
    # MapChunk: one entity (index ignored): its components by type + its Ref
    mc_ = cp.makeClass("skyytest.MapChunk")
    mc_.setSuperclass(cp.get("com.hypixel.hytale.component.ArchetypeChunk"))
    for decl in ("java.util.Map comps", "com.hypixel.hytale.component.Ref ref"):
        mc_.addField(CtField.make("public %s;" % decl, mc_))
    mc_.addConstructor(CtNewConstructor.make("public MapChunk() { super(null, null); }", mc_))
    mc_.addMethod(CtNewMethod.make("""public com.hypixel.hytale.component.Component getComponent(int i, com.hypixel.hytale.component.ComponentType t) {
  return this.comps == null ? null : (com.hypixel.hytale.component.Component) this.comps.get(t);
}""", mc_))
    mc_.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Ref getReferenceTo(int i) { return this.ref; }", mc_))
    mc_.writeFile(out_dir)
    # MapCB: the CommandBuffer the REAL FallDamagePlayers.tick uses (its world through getExternalData; its Damage through invoke)
    cbm_ = cp.makeClass("skyytest.MapCB")
    cbm_.setSuperclass(cp.get("com.hypixel.hytale.component.CommandBuffer"))
    for decl in ("java.lang.Object ext", "java.util.List events", "java.util.List refs"):
        cbm_.addField(CtField.make("public %s;" % decl, cbm_))
    cbm_.addConstructor(CtNewConstructor.make("public MapCB() { super(null); }", cbm_))
    cbm_.addMethod(CtNewMethod.make("public java.lang.Object getExternalData() { return this.ext; }", cbm_))
    cbm_.addMethod(CtNewMethod.make("public void invoke(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.system.EcsEvent e) { this.refs.add(r); this.events.add(e); }", cbm_))
    cbm_.writeFile(out_dir)
    # FakeAssetStore: a concrete AssetStore whose REAL getAssetMap() answers its assetMap field (a real DefaultAssetMap / BlockTypeAssetMap /
    # IndexedLookupTableAssetMap filled from the harness)
    fas_ = cp.makeClass("skyytest.FakeAssetStore")
    fas_.setSuperclass(cp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fas_.addConstructor(CtNewConstructor.make("public FakeAssetStore() { super(null); }", fas_))
    fas_.writeFile(out_dir)
    # FakeHotbar: the item in the main hand (InventoryComponent.getItemInHand reads Hotbar.getActiveItem when no tool item is used)
    fh_ = cp.makeClass("skyytest.FakeHotbar")
    fh_.setSuperclass(cp.get("com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar"))
    fh_.addField(CtField.make("public com.hypixel.hytale.server.core.inventory.ItemStack item;", fh_))
    fh_.addConstructor(CtNewConstructor.make("public FakeHotbar() { super(); }", fh_))
    fh_.addMethod(CtNewMethod.make("public com.hypixel.hytale.server.core.inventory.ItemStack getActiveItem() { return this.item; }", fh_))
    fh_.writeFile(out_dir)
    # FakeInventory: the storage the double drop fills (a REAL CombinedItemContainer over a real SimpleItemContainer)
    fi_ = cp.makeClass("skyytest.FakeInventory")
    fi_.setSuperclass(cp.get("com.hypixel.hytale.server.core.inventory.Inventory"))
    fi_.addField(CtField.make("public com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer comb;", fi_))
    fi_.addConstructor(CtNewConstructor.make("public FakeInventory() { super(); }", fi_))
    fi_.addMethod(CtNewMethod.make("public com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer getCombinedStorageHotbarBackpack() { return this.comb; }", fi_))
    fi_.writeFile(out_dir)


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


# ============================================================================================ child: the 0.4.14 jar
def run_new(jar, out, fake, xs_file, crops_file):
    from jpype import JClass, JFloat, JLong, JImplements, JOverride, JArray, JObject
    res, path = common(jar, [fake] + ([MOBS_JAR] if os.path.isfile(MOBS_JAR) else []))   # 0.4.14: + SkyyMobs (the real mob:fn:level)
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
    D["n14_block"] = str(Cfg.N14_DEFAULTS)                       # 0.4.14
    D["block14_none"] = str(Cfg.block14(None))

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

    DMig = JClass(PKG + "DocMig")

    def start(d):
        """the plugin's setup order: ManaMig.run -> HealMig.run -> DocMig.run (0.4.14) -> SkillCfg.load -> ClassCurve.start (+ the kit's history
        init)"""
        Cfg.FILE = path(os.path.join(d, "xp.properties"))
        fresh_store(os.path.join(d, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        mr = [str(x) for x in Mig.run()]
        hr = str(HMig.run())
        dr = str(DMig.run())
        lt = str(Cfg.load())
        cr = str(Curve.start(path(d)))
        return {"mana": mr, "heal": hr, "doc": dr, "load": lt, "curve": cr, "ready": bool(Curve.READY),
                "pending": dict((str(k), str(v)) for k, v in Curve.PENDING.items()), "done": dict((str(k), str(v)) for k, v in Curve.DONE.items())}

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
                 "record": s1.get("class-curve.properties", b"").decode("latin-1"), "n_players": len([k for k in s0 if k.startswith("players/")]),
                 # 0.4.14: the three xp.properties texts, the new config-history copies (and whether one holds the old bytes exactly), the rest
                 "xp0": s0["xp.properties"].decode("latin-1"), "xp1": s1["xp.properties"].decode("latin-1"), "xp2": s2["xp.properties"].decode("latin-1"),
                 "new_bak": sorted(k for k in s1 if k not in s0), "bak_old": any(s1[k] == s0["xp.properties"] for k in s1 if k not in s0),
                 "others_same": all(s0[k] == s1.get(k) for k in s0 if k != "xp.properties" and not k.startswith("config-history/")),
                 "index_tail": s1.get("config-history/index.log", b"")[len(s0.get("config-history/index.log", b"")):].decode("latin-1")}
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
    nb_ = D["n14_block"].encode("latin-1")                        # 0.4.14: a pre-0.4.12 file gets the 0.4.14 block too (after the two)
    full = D["defaults"].encode("latin-1")
    base_old = full[:full.index(b"\n# ---------- Class skill levels (SkyySkills 0.4.12)") + 1]   # every pre-0.4.12 block, no 0.4.12 key
    assert b"levels.class=" not in base_old and b"levels.class.same" not in base_old and b"mana.regen" not in base_old
    cdir = os.path.join(SCRATCH, "c-lf")
    load_cfg(cdir, base_old)
    c1_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    load_cfg(cdir)
    c2_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    C["lf"] = {"exact": c1_ == base_old + b"\n" + cb_ + b"\n" + mb_ + b"\n" + nb_, "again_same": c1_ == c2_, "no_cr": b"\r" not in c1_}
    cdir = os.path.join(SCRATCH, "c-crlf")
    load_cfg(cdir, base_old.replace(b"\n", b"\r\n"))
    c3_ = open(os.path.join(cdir, "xp.properties"), "rb").read()
    C["crlf"] = {"exact": c3_ == (base_old + b"\n" + cb_ + b"\n" + mb_ + b"\n" + nb_).replace(b"\n", b"\r\n"), "all_crlf": c3_.count(b"\r\n") == c3_.count(b"\n")}
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
    C["noeol"] = c5_ == base_noeol + b"\n\n" + cb_ + b"\n" + mb_ + b"\n" + nb_
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

    # ---------------------------------------------------------------- C14: the 0.4.14 block reaching existing files (SkillCfg.ensure14)
    C14 = {}
    MobXpC, GPc, SickleC, AcroCfgC = JClass(PKG + "MobXp"), JClass(PKG + "GatherPace"), JClass(PKG + "Sickle"), JClass(PKG + "AcroCfg")
    try:
        f13 = full[:full.index(b"\n# ---------- Kill XP by mob level, roll landings")]   # = a 0.4.13 default file (both 0.4.12 blocks, no 0.4.14 key)
        f13 = f13.replace(MREG_DOC_NEW.encode("latin-1"), MREG_DOC_OLD.encode("latin-1"))
        assert b"combat.levelXp" not in f13 and b"gather.boost" not in f13 and f13.endswith(b"\n")
        for nm, txt0, nl in (("lf", f13, b"\n"), ("crlf", f13.replace(b"\n", b"\r\n"), b"\r\n")):
            cdir = os.path.join(SCRATCH, "c14-" + nm)
            load_cfg(cdir, txt0)
            a1 = open(os.path.join(cdir, "xp.properties"), "rb").read()
            load_cfg(cdir)
            a2 = open(os.path.join(cdir, "xp.properties"), "rb").read()
            C14[nm] = {"exact": a1 == txt0 + nl + nb_.replace(b"\n", nl), "again_same": a1 == a2, "comment_kept": MREG_DOC_OLD.encode("latin-1") in a1,
                       "values": [bool(MobXpC.ON), float(MobXpC.BONUS), int(MobXpC.FREE), float(MobXpC.ABOVE), float(MobXpC.MAX), float(MobXpC.BELOW),
                                  float(MobXpC.MIN), float(AcroCfgC.ROLL), str(GPc.TEXT), float(GPc.EARLY), int(GPc.UNTIL), float(GPc.LATE), int(GPc.FROM),
                                  bool(SickleC.ON), str(SickleC.ITEMS_TEXT)]}
        # hand values: two keys already set by an admin -> only the other 13 lines appended, the hand lines untouched and in force
        hand = f13 + b"combat.gap.max=5\ngather.boost.early=2\n"
        cdir = os.path.join(SCRATCH, "c14-hand")
        load_cfg(cdir, hand)
        a3 = open(os.path.join(cdir, "xp.properties"), "rb").read()
        tail = a3[len(hand):].decode("latin-1")
        C14["hand"] = {"prefix_kept": a3.startswith(hand), "tail_keys": [ln.split("=")[0] for ln in tail.split("\n") if ln and not ln.startswith("#")],
                       "tail_comments": sum(1 for ln in tail.split("\n") if ln.startswith("#")), "MAX": float(MobXpC.MAX), "EARLY": float(GPc.EARLY),
                       "max_lines": a3.count(b"combat.gap.max="), "early_lines": a3.count(b"gather.boost.early=")}
        load_cfg(cdir)
        C14["hand"]["again_same"] = open(os.path.join(cdir, "xp.properties"), "rb").read() == a3
        # every key present -> nothing appended (block14 = null)
        fullk = f13 + b"\n".join(ln for ln in nb_.split(b"\n") if ln and not ln.startswith(b"#")) + b"\n"
        cdir = os.path.join(SCRATCH, "c14-full")
        load_cfg(cdir, fullk)
        C14["full_same"] = open(os.path.join(cdir, "xp.properties"), "rb").read() == fullk
        # clamps / odd values through the loader
        cdir = os.path.join(SCRATCH, "c14-clamp")
        txtc = load_cfg(cdir, f13 + b"combat.levelXp.enabled=false\ncombat.levelBonus=-1\ncombat.gap.free=500\ncombat.gap.above=99\ncombat.gap.max=0.2\n"
                        b"combat.gap.below=-3\ncombat.gap.min=7\nacro.rollBonus=50\ngather.boost.skills=Mining, cooking ,farming,Mining\n"
                        b"gather.boost.early=-2\ngather.boost.earlyUntil=150\ngather.boost.late=1000\ngather.boost.lateFrom=-4\n"
                        b"farming.sickle.enabled=false\nfarming.sickle.items= , ,\n")
        C14["clamp"] = {"values": [bool(MobXpC.ON), float(MobXpC.BONUS), int(MobXpC.FREE), float(MobXpC.ABOVE), float(MobXpC.MAX), float(MobXpC.BELOW),
                                   float(MobXpC.MIN), float(AcroCfgC.ROLL), str(GPc.TEXT), float(GPc.EARLY), int(GPc.UNTIL), float(GPc.LATE), int(GPc.FROM),
                                   bool(SickleC.ON), str(SickleC.ITEMS_TEXT), [bool(x) for x in GPc.SLOTS][:4]],
                        "text": txtc}
        load_cfg(os.path.join(SCRATCH, "c14-clamp2"), b"multiplier=1.0\n")
        C14["fresh_values"] = [bool(MobXpC.ON), float(MobXpC.BONUS), int(MobXpC.FREE), float(MobXpC.ABOVE), float(MobXpC.MAX), float(MobXpC.BELOW),
                               float(MobXpC.MIN), float(AcroCfgC.ROLL), str(GPc.TEXT), float(GPc.EARLY), int(GPc.UNTIL), float(GPc.LATE), int(GPc.FROM),
                               bool(SickleC.ON), str(SickleC.ITEMS_TEXT)]
        _ft = open(os.path.join(SCRATCH, "c14-clamp2", "xp.properties"), "rb").read()
        C14["fresh_tail"] = _ft.endswith(b"\n" + nb_) and _ft.count(nb_) == 1 and _ft.count(mb_) == 1
    except Exception as e:
        C14["error"] = repr(e)
    D["C14"] = C14

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
    try:
        D.update(run_new14(dict(locals()), crops_file))           # 0.4.14: KX RL GP SK DM
    except Exception as e:
        import traceback
        D["N14_error"] = traceback.format_exc()[-3000:]
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: the 0.4.14 sections (KX RL GP SK DM)
def run_new14(L, crops_file):
    """0.4.14's new sections on the 0.4.14 jar (see the module docstring); L = run_new's locals (stand-ins, classes, helpers)"""
    import itertools
    import threading
    from jpype import JClass, JFloat, JLong, JArray, JInt, JDouble as JD, JImplements, JOverride, JObject
    U, setf, path, bridge, mkpr, texts, load_cfg = L["U"], L["setf"], L["path"], L["bridge"], L["mkpr"], L["texts"], L["load_cfg"]
    Cfg, Store, Xp, Defs, Px, StatsPage = L["Cfg"], L["Store"], L["Xp"], L["Defs"], L["Px"], L["StatsPage"]
    page_texts, has, PLAYERS, uni, Universe, PRef = L["page_texts"], L["has"], L["PLAYERS"], L["uni"], L["Universe"], L["PRef"]
    FakeW, ENV, Const, COINS = L["FakeW"], L["ENV"], L["Const"], L["COINS"]
    JBool, JLongC, JObj, JIntC = L["JBool"], L["JLongC"], L["JObj"], L["JInt"]
    UUID, HM, IHM, AL = JClass("java.util.UUID"), JClass("java.util.HashMap"), JClass("java.util.IdentityHashMap"), JClass("java.util.ArrayList")
    StampedLock, RLock = JClass("java.util.concurrent.locks.StampedLock"), JClass("java.util.concurrent.locks.ReentrantLock")
    out = {}
    model = json.load(open(crops_file))

    def findf(c, name):
        while c is not None:
            for f in c.getDeclaredFields():
                if str(f.getName()) == name:
                    f.setAccessible(True)
                    return f
            c = c.getSuperclass()
        raise RuntimeError("no field " + name)

    def setany(obj, name, val):
        findf(obj.getClass(), name).set(obj, val)

    def getany(obj, name):
        return findf(obj.getClass(), name).get(obj)

    def setstatic(cls, name, val):
        findf(cls.class_, name).set(None, val)

    def alloc(cls):
        return U.allocateInstance(cls.class_)

    def fstore(amap):
        st = alloc(JClass("skyytest.FakeAssetStore"))
        setany(st, "assetMap", amap)
        return st

    def defmap(d):
        m = alloc(JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap"))
        hm = HM()
        for k, v in d.items():
            hm.put(k, v)
        setany(m, "assetMap", hm)
        setany(m, "assetMapLock", StampedLock())
        return m

    def stub_store(clsname):
        """the class's static AssetStore field (whatever its name) = a FakeAssetStore over an EMPTY real asset map of getAssetMap's type"""
        cls = JClass(clsname)
        rt = cls.class_.getDeclaredMethod("getAssetMap").getReturnType()
        amap = U.allocateInstance(rt)
        JAWM = JClass("com.hypixel.hytale.assetstore.map.JsonAssetWithMap")
        for nm, val in (("assetMap", HM()), ("assetMapLock", StampedLock()), ("array", JArray(JAWM)(0)), ("arrayLock", RLock()),
                        ("keyToIndex", JClass("it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap")()), ("keyToIndexLock", StampedLock())):
            try:
                findf(amap.getClass(), nm).set(amap, val)
            except Exception:
                pass
        AS, Mod = JClass("com.hypixel.hytale.assetstore.AssetStore"), JClass("java.lang.reflect.Modifier")
        for f in cls.class_.getDeclaredFields():
            if f.getType() == AS.class_ and Mod.isStatic(f.getModifiers()):
                f.setAccessible(True)
                f.set(None, fstore(amap))

    # ---------------------------------------------------------------- the engine registries the new code reads (real classes, filled here)
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = EMc.get()
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    T = {}
    for fname in ("playerComponentType", "uuidComponentType", "transformComponentType", "playerInputComponentType", "velocityComponentType",
                  "movementStatesComponentType", "hotbarInventoryComponentType", "toolInventoryComponentType"):
        T[fname] = alloc(CT)
        setany(em, fname, T[fname])
    T["playerRef"] = alloc(CT)
    setany(uni, "playerRefComponentType", T["playerRef"])
    T["stats"] = ENV["statsType"]
    ITEM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    setstatic(ITEM, "ASSET_STORE", fstore(defmap({})))            # ItemStack(id, n) -> Item.UNKNOWN for every id (no item assets here)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    EST = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    GM = JClass("com.hypixel.hytale.protocol.GameMode")
    ESMc, ESVc = ENV["ESM"], ENV["ESV"]
    Ref = JClass("com.hypixel.hytale.component.Ref")
    AtomicRef = JClass("java.util.concurrent.atomic.AtomicReference")
    TRC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    UUC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    MapStore, MapChunk, MapCB = JClass("skyytest.MapStore"), JClass("skyytest.MapChunk"), JClass("skyytest.MapCB")

    def world(name):
        w = alloc(FakeW)
        setf(w, WLD, "name", name)
        es = alloc(EST)
        setf(es, EST, "world", w)
        return w, es

    def health(mx, val=None):
        esm = alloc(ESMc)
        hv = alloc(ESVc)
        for nm, v in (("id", "Health"), ("index", JInt(0)), ("value", JFloat(mx if val is None else val)), ("min", JFloat(0.0)), ("max", JFloat(mx))):
            setany(hv, nm, v)
        setany(esm, "values", JArray(ESVc)([hv]))
        return esm, hv

    def player(mode="Adventure", fall=0.0):
        p = alloc(PLA)
        setany(p, "gameMode", getattr(GM, mode))
        setany(p, "waitingForClientReady", AtomicRef())
        setany(p, "currentFallDistance", JD(fall))
        return p

    def put(store, ref, typ, comp):
        m = store.comps.get(ref)
        if m is None:
            m = IHM()
            store.comps.put(ref, m)
        m.put(typ, comp)

    def mkstore(es):
        st = alloc(MapStore)
        st.comps = IHM()
        st.ext = es
        st.events = AL()
        return st

    # ================================================================ KX: kill XP by mob level
    KX = {}
    try:
        load_cfg(os.path.join(SCRATCH, "kx-cfg"), b"multiplier=1.0\n")
        MobXp = JClass(PKG + "MobXp")
        KX["defaults"] = [bool(MobXp.ON), float(MobXp.BONUS), int(MobXp.FREE), float(MobXp.ABOVE), float(MobXp.MAX), float(MobXp.BELOW), float(MobXp.MIN),
                          float(Cfg.CLASS_MULT)]
        Ls = [-1, 0, 1, 2, 3, 5, 6, 10, 11, 16, 17, 25, 33, 40, 50, 60, 75, 100, 150]
        Ss = [-3, 0, 1, 5, 6, 10, 11, 16, 17, 20, 27, 28, 30, 33, 38, 39, 40, 44, 45, 50, 60, 100]
        KX["grid"] = [[l, s, float(MobXp.levelFactor(l)), float(MobXp.gapFactor(l, s)), float(MobXp.factor(l, s))] for l in Ls for s in Ss]
        # pay: exact products (the 1e-9 rule), class / non-class slots, nothing for 0 / negative
        KX["pay_exact"] = [int(MobXp.pay(DIVINITY, 36, 2.5)), int(MobXp.pay(MINING, 36, 2.5)), int(MobXp.pay(DIVINITY, 0, 3.0)), int(MobXp.pay(DIVINITY, 36, 0.0)),
                           int(MobXp.pay(DIVINITY, 36, -1.0)), int(MobXp.pay(DIVINITY, 10, 1.1)), int(MobXp.pay(ARCHERY, 20, 2.55 / 3.0)),
                           int(MobXp.pay(DIVINITY, 3000000000000000, 10.0))]
        # Skyy's example: Lv 33 Skeleton_Scout, 178 max health, Divinity 11
        base = int(Cfg.combatXp(None, JFloat(178.0)))
        f = float(MobXp.factor(33, 11))
        pays = [int(MobXp.pay(DIVINITY, base, f)) for _ in range(20000)]
        KX["skyy"] = {"base": base, "classXp": int(Cfg.classXp(DIVINITY, base)), "lf": float(MobXp.levelFactor(33)), "gf": float(MobXp.gapFactor(33, 11)),
                      "factor": f, "values": sorted(set(pays)), "mean": sum(pays) / float(len(pays)), "n": len(pays)}
        # a fractional pay: values and mean
        p2 = [int(MobXp.pay(ARCHERY, 7, 1.15)) for _ in range(20000)]
        KX["frac"] = {"values": sorted(set(p2)), "mean": sum(p2) / float(len(p2))}
        # the reader's clamps
        P = JClass("java.util.Properties")
        pr_ = P()
        for k_, v_ in (("combat.levelXp.enabled", "false"), ("combat.levelBonus", "-1"), ("combat.gap.free", "500"), ("combat.gap.above", "99"),
                       ("combat.gap.max", "0.2"), ("combat.gap.below", "-3"), ("combat.gap.min", "7")):
            pr_.setProperty(k_, v_)
        MobXp.read(pr_)
        KX["clamped"] = [bool(MobXp.ON), float(MobXp.BONUS), int(MobXp.FREE), float(MobXp.ABOVE), float(MobXp.MAX), float(MobXp.BELOW), float(MobXp.MIN),
                         float(MobXp.levelFactor(33)), float(MobXp.gapFactor(33, 1)), str(MobXp.text())]
        MobXp.read(P())
        KX["text"] = str(MobXp.text())
        # ---- MobXp.levelOf: the REAL SkyyMobs MobLevelFn (SET pin 0.1.2) on its MOBS map, then stand-ins
        wK, esK = world("default")
        stK = mkstore(esK)
        npc = Ref(stK, 7)
        un = UUID(0x30B, 33)
        put(stK, npc, T["uuidComponentType"], UUC(un))
        npc2 = Ref(stK, 8)                                           # no UUIDComponent
        lv = {}
        bridge.remove("mob:fn:level")
        lv["no_fn"] = int(MobXp.levelOf(stK, npc))
        real_fn = None
        try:
            real_fn = JClass("com.skyy.mobs.MobLevelFn")()
            MobInfo, MobLevel = JClass("com.skyy.mobs.MobInfo"), JClass("com.skyy.mobs.MobLevel")
            mi = MobInfo()
            mi.world, mi.uuid, mi.level, mi.role = "default", un, 33, "Skeleton_Scout"
            MobLevel.MOBS.put(un, mi)
            mi0 = MobInfo()
            un0 = UUID(0x30B, 0)
            mi0.world, mi0.uuid, mi0.level = "default", un0, 0
            MobLevel.MOBS.put(un0, mi0)
            bridge.put("mob:fn:level", real_fn)
            lv["real"] = int(MobXp.levelOf(stK, npc))
            lv["real_no_uuidc"] = int(MobXp.levelOf(stK, npc2))
            npc0 = Ref(stK, 9)
            put(stK, npc0, T["uuidComponentType"], UUC(un0))
            lv["real_level0"] = int(MobXp.levelOf(stK, npc0))
            npcU = Ref(stK, 10)
            put(stK, npcU, T["uuidComponentType"], UUC(UUID(0x30B, 404)))
            lv["real_unknown"] = int(MobXp.levelOf(stK, npcU))
            wI, esI = world("skyy-island-x")
            stI = mkstore(esI)
            npcI = Ref(stI, 7)
            put(stI, npcI, T["uuidComponentType"], UUC(un))
            lv["real_wrong_world"] = int(MobXp.levelOf(stI, npcI))
            stN = mkstore(None)
            npcN = Ref(stN, 7)
            put(stN, npcN, T["uuidComponentType"], UUC(un))
            lv["real_no_world"] = int(MobXp.levelOf(stN, npcN))
            lv["real_direct"] = int(real_fn.apply(JArray(JObj)(["default", un])).intValue())
        except Exception as e:
            lv["real_error"] = repr(e)
        CALLS = []

        @JImplements("java.util.function.Function")
        class Fn(object):
            def __init__(self, v, boom=False):
                self.v, self.boom = v, boom

            @JOverride
            def apply(self, o):
                CALLS.append([str(o[0]), str(o[1])])
                if self.boom:
                    raise RuntimeError("boom")
                return self.v
        for nm, fn_ in (("minus1", Fn(JIntC.valueOf(JInt(-1)))), ("zero", Fn(JIntC.valueOf(JInt(0)))), ("long12", Fn(JLongC.valueOf(JLong(12)))), ("string", Fn("12")), ("null", Fn(None)),
                        ("double7", Fn(JClass("java.lang.Double").valueOf(7.9)))):
            bridge.put("mob:fn:level", fn_)
            lv[nm] = int(MobXp.levelOf(stK, npc))
        f0 = bool(MobXp.FAILED_ONCE)
        bridge.put("mob:fn:level", Fn(None, True))
        lv["throw"] = [f0, int(MobXp.levelOf(stK, npc)), bool(MobXp.FAILED_ONCE), int(MobXp.levelOf(stK, npc))]
        bridge.put("mob:fn:level", "not a function")
        lv["not_fn"] = int(MobXp.levelOf(stK, npc))
        lv["nulls"] = [int(MobXp.levelOf(None, npc)), int(MobXp.levelOf(stK, None))]
        lv["args"] = CALLS[:1]
        KX["levelOf"] = lv
        # ---- MobXp.kill end to end: the killer + a party on their own class skills (PartyXp.share2 / one2 on the stand-in store)
        if real_fn is not None:
            bridge.put("mob:fn:level", real_fn)
        else:
            bridge.put("mob:fn:level", Fn(JIntC.valueOf(JInt(33))))
        bridge.put("class:fn:allowed", Const(JBool.TRUE))
        members = []

        def member(n, cls_, slot, lvl, pos, mode="Adventure", online=True):
            u = UUID(0x9A47, n)
            pr = mkpr(u, "M%d" % n)
            r = Ref(stK, 100 + n)
            setany(pr, "entity", r)
            put(stK, r, T["playerComponentType"], player(mode))
            tc = TRC()
            tc.getPosition().set(float(pos[0]), float(pos[1]), float(pos[2]))
            put(stK, r, T["transformComponentType"], tc)
            put(stK, r, T["stats"], health(100.0)[0])
            bridge.put("class:" + str(u), cls_)
            d = JArray(JLong)(32)
            cum = [int(x) for x in (Defs.CCUM if Defs.isClass(slot) else Defs.CUM)]
            d[slot] = cum[lvl]
            d[16 + slot] = lvl
            Store.DATA.put(str(u), d)
            if not online:
                PLAYERS.remove(u)
            return {"u": u, "pr": pr, "r": r, "slot": slot, "lvl": lvl, "cls": cls_}
        killer = member(0, "Priest", DIVINITY, 11, (0, 64, 0))
        mlist = [member(1, "Archer", ARCHERY, 1, (10, 64, 0)), member(2, "Warrior", WARRIOR, 30, (0, 64, 20)), member(3, "Priest", DIVINITY, 40, (30, 70, 30)),
                 member(4, "Archer", ARCHERY, 60, (-20, 64, -20)), member(5, "Archer", ARCHERY, 1, (60, 64, 0)), member(6, "Warrior", WARRIOR, 1, (5, 64, 5), "Creative")]
        ids_ = JArray(JClass("java.lang.String"))([str(killer["u"])] + [str(m["u"]) for m in mlist])
        bridge.put("party:fn:members", Const(ids_))
        levels = [int(Store.level(m["u"], m["slot"])) for m in [killer] + mlist]

        def xp_of(m):
            return int(Store.DATA.get(str(m["u"]))[m["slot"]])

        def reset_all():
            for m in [killer] + mlist:
                d = Store.DATA.get(str(m["u"]))
                cum = [int(x) for x in (Defs.CCUM if Defs.isClass(m["slot"]) else Defs.CUM)]
                d[m["slot"]] = cum[m["lvl"]]
                d[16 + m["slot"]] = m["lvl"]
        runs, kc, gains = 400, [], [[] for _ in mlist]
        for _ in range(runs):
            reset_all()
            before = [xp_of(m) for m in mlist]
            k0 = xp_of(killer)
            cx = int(MobXp.kill(killer["pr"], killer["r"], stK, DIVINITY, base, npc))
            kc.append([cx, xp_of(killer) - k0])
            for i, m in enumerate(mlist):
                gains[i].append(xp_of(m) - before[i])
        KX["kill"] = {"levels": levels, "killer": kc, "gains": gains, "factors": [float(MobXp.factor(33, m["lvl"])) for m in mlist],
                      "fraction": float(JClass(PKG + "PartyCfg").FRACTION), "radius": float(JClass(PKG + "PartyCfg").RADIUS)}
        texts()
        # no mob level (SkyyMobs missing) and the part off = 0.4.13 exactly
        reset_all()
        bridge.remove("mob:fn:level")
        k0, b0 = xp_of(killer), [xp_of(m) for m in mlist]
        cx = int(MobXp.kill(killer["pr"], killer["r"], stK, DIVINITY, base, npc))
        KX["no_level"] = [cx, xp_of(killer) - k0, [xp_of(m) - b for m, b in zip(mlist, b0)]]
        reset_all()
        bridge.put("mob:fn:level", real_fn if real_fn is not None else Fn(JIntC.valueOf(JInt(33))))
        MobXp.ON = False
        k0, b0 = xp_of(killer), [xp_of(m) for m in mlist]
        cx = int(MobXp.kill(killer["pr"], killer["r"], stK, DIVINITY, base, npc))
        KX["off"] = [cx, xp_of(killer) - k0, [xp_of(m) - b for m, b in zip(mlist, b0)]]
        MobXp.ON = True
        # the old share(...) signature still pays the 0.4.13 share of the given cx
        reset_all()
        b0 = [xp_of(m) for m in mlist]
        Px.share(killer["pr"], killer["r"], stK, JLong(108))
        KX["old_share"] = [xp_of(m) - b for m, b in zip(mlist, b0)]
        # FIX ROUND F3: the Stats how-to line - with mob levels (mob:fn:level + the part on) each member's share is worked out with their own
        # class skill level; without them (no SkyyMobs / the part off) the 0.4.13 text is exact and stays
        ht = [str(Px.howText())]
        bridge.remove("mob:fn:level")
        ht.append(str(Px.howText()))
        bridge.put("mob:fn:level", real_fn if real_fn is not None else Fn(JIntC.valueOf(JInt(33))))
        MobXp.ON = False
        ht.append(str(Px.howText()))
        MobXp.ON = True
        KX["howText"] = ht
        bridge.remove("party:fn:members")
        texts()
    except Exception as e:
        import traceback
        KX["error"] = traceback.format_exc()[-2500:]
    out["KX"] = KX

    # ================================================================ RL: roll landings on the real engine objects
    RL = {}
    try:
        load_cfg(os.path.join(SCRATCH, "rl-cfg"), b"multiplier=1.0\n")
        # GameplayConfig's static DEFAULT (its CombatConfig ...) asks the EntityEffect asset map: an empty one (no effect assets here)
        stub_store("com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect")
        AcroCfgC, AcroC, RollSys = JClass(PKG + "AcroCfg"), JClass(PKG + "Acro"), JClass(PKG + "RollSys")
        PIN = JClass("com.hypixel.hytale.server.core.modules.entity.player.PlayerInput")
        SMS = JClass("com.hypixel.hytale.server.core.modules.entity.player.PlayerInput$SetMovementStates")
        SCV = JClass("com.hypixel.hytale.server.core.modules.entity.player.PlayerInput$SetClientVelocity")
        MVS = JClass("com.hypixel.hytale.protocol.MovementStates")
        VEL = JClass("com.hypixel.hytale.server.core.modules.physics.component.Velocity")
        V3 = JClass("org.joml.Vector3d")
        MCF = JClass("com.hypixel.hytale.server.core.entity.entities.player.movement.MovementConfig")
        GPCc = JClass("com.hypixel.hytale.server.core.asset.type.gameplay.GameplayConfig")
        PCFc = JClass("com.hypixel.hytale.server.core.asset.type.gameplay.PlayerConfig")
        WCc = JClass("com.hypixel.hytale.server.core.universe.world.WorldConfig")
        DCause = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
        ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
        O2I = JClass("it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap")
        MSC = JClass("com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent")
        # the MovementConfig asset (Assets.zip Default.json roll numbers) behind the REAL World.getGameplayConfig chain
        mcv = model["movement"]
        mc = MCF("Default")
        for nm, key in (("minFallSpeedToEngageRoll", "MinFallSpeedToEngageRoll"), ("maxFallSpeedRollFullMitigation", "MaxFallSpeedRollFullMitigation"),
                        ("maxFallSpeedToEngageRoll", "MaxFallSpeedToEngageRoll"), ("fallDamagePartialMitigationPercent", "FallDamagePartialMitigationPercent")):
            setany(mc, nm, JFloat(float(mcv[key])))
        mcm = alloc(ILT)
        setany(mcm, "array", JArray(MCF)([mc]))
        setany(mcm, "arrayLock", RLock())
        setstatic(MCF, "ASSET_STORE", fstore(mcm))
        pc = PCFc()
        setany(pc, "movementConfigIndex", JInt(0))
        gcf = GPCc()
        setany(gcf, "playerConfig", pc)
        setstatic(GPCc, "ASSET_STORE", fstore(defmap({"Default": gcf})))
        wc = alloc(WCc)
        setany(wc, "gameplayConfig", "Default")
        setany(wc, "isFallDamageEnabled", True)                    # fix round F2: a world with fall damage on (every live world); RollSys asks it
        wR, esR = world("default")
        setany(wR, "worldConfig", wc)
        # DamageCause.FALL + its index (the engine's Damage constructor asks the cause asset map)
        fall = DCause("Fall")
        setstatic(DCause, "FALL", fall)
        dcm = alloc(ILT)
        k2i = O2I()
        k2i.addTo("Fall", JInt(5))                                   # (put is ambiguous from Python)
        setany(dcm, "keyToIndex", k2i)
        setany(dcm, "keyToIndexLock", StampedLock())
        setstatic(DCause, "ASSET_STORE", fstore(dcm))
        RL["chain"] = [float(RollSys.movementConfig(mkstore(esR)).getMinFallSpeedToEngageRoll()) if RollSys.movementConfig(mkstore(esR)) is not None else None,
                       bool(wR.getGameplayConfig().equals(gcf))]
        FDPc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$FallDamagePlayers")
        fdp = FDPc()
        rs = RollSys()
        uR = UUID(0x2011, 1)
        prR = mkpr(uR, "Roller")
        STATE = AcroC.STATE

        def scene(mx, val=None):
            st = mkstore(esR)
            ref = Ref(st, 0)
            setany(prR, "entity", ref)
            esm, hv = health(mx, val)
            pl = player("Adventure", 5.0)
            put(st, ref, T["stats"], esm)
            put(st, ref, T["playerComponentType"], pl)
            ch = alloc(MapChunk)
            ch.comps = IHM()
            ch.ref = ref
            cb = alloc(MapCB)
            cb.ext = esR
            cb.events, cb.refs = AL(), AL()
            return st, ref, ch, cb, pl, esm

        def landing(ch, pl, queue, vel_y, mx, esm):
            pin = PIN()
            for q in queue:
                if q[0] == "v":
                    pin.queue(SCV(V3(0.0, -float(q[1]), 0.0)))
                else:
                    ms = MVS()
                    ms.onGround, ms.rolling, ms.inFluid = q[1], q[2], q[3]
                    pin.queue(SMS(ms))
            vel = VEL()
            vel.getClientVelocity().set(0.0, -float(vel_y), 0.0)
            ch.comps.clear()
            for typ, comp in ((T["playerInputComponentType"], pin), (T["velocityComponentType"], vel), (T["playerComponentType"], pl),
                              (T["stats"], esm), (T["playerRef"], prR)):
                ch.comps.put(typ, comp)

        def run_both(queue, vel_y, mx, rolled_cfg=True):
            st, ref, ch, cb, pl, esm = scene(mx)
            landing(ch, pl, queue, vel_y, mx, esm)
            fdp.tick(JFloat(1.0 / 30.0), JInt(0), ch, st, cb)
            dmg = [float(e.getAmount()) for e in cb.events]
            fd_after = float(pl.getCurrentFallDistance())
            setany(pl, "currentFallDistance", JD(5.0))
            STATE.remove(uR)
            n0 = int(RollSys.NOTED)
            rs.tick(JFloat(1.0 / 30.0), JInt(0), ch, st, cb)
            s_ = STATE.get(uR)
            note = None if s_ is None or float(s_[288]) <= 0.0 else float(s_[289])
            return {"dmg": dmg, "fd_after": fd_after, "note": note, "noted": int(RollSys.NOTED) - n0}
        speeds = [0.0, 5.0, 20.9, 21.0, 21.0001, 21.5, 22.0, 23.0, 24.0, 24.9999, 25.0, 25.0001, 26.0, 27.5, 28.0, 30.0, 30.9999, 31.0, 31.0001, 32.0, 35.0,
                  40.0, 60.0]
        grid = []
        for mx in (100.0, 37.5, 250.0, 1000.0):
            for sp in speeds:
                for rolling in (False, True):
                    for fluid in (False, True):
                        r_ = run_both([("v", sp), ("s", True, rolling, fluid)], 0.0, mx)
                        d = [int(x) for x in RollSys.damage(sp, JFloat(mc.getMinFallSpeedToEngageRoll()), JFloat(mc.getMaxFallSpeedRollFullMitigation()),
                                                            JFloat(mc.getMaxFallSpeedToEngageRoll()), JFloat(mc.getFallDamagePartialMitigationPercent()),
                                                            JFloat(mx), rolling, fluid)]
                        grid.append([mx, sp, rolling, fluid, r_["dmg"], r_["fd_after"], r_["note"], r_["noted"], d])
        RL["grid"] = grid
        RL["mc"] = [float(mc.getMinFallSpeedToEngageRoll()), float(mc.getMaxFallSpeedRollFullMitigation()), float(mc.getMaxFallSpeedToEngageRoll()),
                    float(mc.getFallDamagePartialMitigationPercent())]
        # queue orders: the speed from the component only; a rolling state BEFORE the landing; two landings in one tick; no fall distance
        RL["vel_only"] = run_both([("s", True, True, False)], 28.0, 100.0)
        RL["before_landing"] = run_both([("s", False, True, False), ("v", 28.0), ("s", True, True, False)], 0.0, 100.0)
        RL["two_landings"] = run_both([("v", 30.0), ("s", True, True, False), ("v", 50.0), ("s", True, False, False)], 0.0, 100.0)
        RL["first_not_rolled"] = run_both([("v", 28.0), ("s", True, False, False), ("v", 28.0), ("s", True, True, False)], 0.0, 100.0)
        st, ref, ch, cb, pl, esm = scene(100.0)
        landing(ch, pl, [("v", 28.0), ("s", True, True, False)], 0.0, 100.0, esm)
        setany(pl, "currentFallDistance", JD(0.0))
        STATE.remove(uR)
        rs.tick(JFloat(1.0 / 30.0), JInt(0), ch, st, cb)
        fdp.tick(JFloat(1.0 / 30.0), JInt(0), ch, st, cb)
        RL["no_fall"] = [STATE.get(uR) is None or float(STATE.get(uR)[288]) == 0.0, len(cb.events)]
        # acro.rollBonus 0 / acro.enabled off: RollSys notes nothing
        AcroCfgC.ROLL = 0.0
        RL["roll0"] = run_both([("v", 25.0), ("s", True, True, False)], 0.0, 100.0)
        AcroCfgC.ROLL = 0.5
        AcroCfgC.ENABLED = False
        RL["acro_off"] = run_both([("v", 25.0), ("s", True, True, False)], 0.0, 100.0)
        AcroCfgC.ENABLED = True
        # FIX ROUND F2 (both reviews): a world with fall damage OFF - the REAL store-level FallDamagePlayers.tick(F, I, Store) returns before any
        # landing (no Damage, the fall distance kept), and RollSys notes nothing for the same rolled landing; switched on again = noted
        wcD = alloc(WCc)
        setany(wcD, "gameplayConfig", "Default")
        setany(wcD, "isFallDamageEnabled", False)
        wD, esD = world("default")
        setany(wD, "worldConfig", wcD)
        stD = mkstore(esD)
        refD = Ref(stD, 0)
        setany(prR, "entity", refD)
        esmD, hvD = health(100.0)
        plD = player("Adventure", 5.0)
        put(stD, refD, T["stats"], esmD)
        put(stD, refD, T["playerComponentType"], plD)
        chD = alloc(MapChunk)
        chD.comps = IHM()
        chD.ref = refD
        cbD = alloc(MapCB)
        cbD.ext = esD
        cbD.events, cbD.refs = AL(), AL()
        landing(chD, plD, [("v", 25.0), ("s", True, True, False)], 0.0, 100.0, esmD)
        fdp.tick(JFloat(1.0 / 30.0), JInt(0), stD)
        eng_off = [len(cbD.events), len(stD.events), float(plD.getCurrentFallDistance())]
        STATE.remove(uR)
        n0 = int(RollSys.NOTED)
        rs.tick(JFloat(1.0 / 30.0), JInt(0), chD, stD, cbD)
        s_ = STATE.get(uR)
        off_note = None if s_ is None or float(s_[288]) <= 0.0 else float(s_[289])
        off_noted = int(RollSys.NOTED) - n0
        setany(wcD, "isFallDamageEnabled", True)
        STATE.remove(uR)
        rs.tick(JFloat(1.0 / 30.0), JInt(0), chD, stD, cbD)
        s_ = STATE.get(uR)
        on_note = None if s_ is None or float(s_[288]) <= 0.0 else float(s_[289])
        wN, esN = world("no-config")                                 # a world whose WorldConfig is missing
        fn_ = [bool(RollSys.fallDamageOn(mkstore(esR))), bool(RollSys.fallDamageOn(mkstore(esN))), bool(RollSys.fallDamageOn(mkstore(None))),
               bool(RollSys.fallDamageOn(None))]
        setany(wcD, "isFallDamageEnabled", False)
        fn_.append(bool(RollSys.fallDamageOn(stD)))
        RL["fd_off"] = {"engine": eng_off, "note": off_note, "noted": off_noted, "on_note": on_note, "fn": fn_}
        STATE.remove(uR)
        # the system's shape + the engine's own DependencyGraph sort (RollSys before FallDamagePlayers before ProcessPlayerInput)
        deps = list(rs.getDependencies())
        RL["deps"] = [str(type(x).__name__) for x in deps] + [str(deps[0].getSystemClass().getName()) if deps else "", str(getany(deps[0], "order")) if deps else ""]
        RL["parallel"] = bool(rs.isParallel(64, 8))
        RL["group"] = rs.getGroup() is None
        PPIc = JClass("com.hypixel.hytale.server.core.modules.entity.player.PlayerSystems$ProcessPlayerInput")
        DG = JClass("com.hypixel.hytale.component.dependency.DependencyGraph")
        ISys = JClass("com.hypixel.hytale.component.system.ISystem")
        ppi = PPIc()
        orders = []
        for perm in itertools.permutations([fdp, ppi, rs]):
            g = DG(JArray(ISys)(list(perm)))
            g.resolveEdges(None)
            arr = JArray(ISys)(3)
            g.sort(arr)
            orders.append([str(x.getClass().getSimpleName()) for x in arr])
        RL["orders"] = orders
        # Acro: noteFall skips the same landing; falls pays 400 ms later x acro.fallDamageXp x (1 + rollBonus), capped; flush puts it into the store
        s_ = AcroC.state(uR)
        AcroC.profileReset(s_)
        AcroC.noteRoll(uR, JFloat(50.0))
        t0 = float(s_[288])
        AcroC.noteFall(uR, JFloat(16.0))
        skip = [float(s_[15]), float(s_[16])]
        s_[288] = t0 - 1500.0
        AcroC.noteFall(uR, JFloat(16.0))
        later = [float(s_[15]) > 0.0, float(s_[16])]
        RL["notefall"] = {"skip": skip, "later": later}
        st, ref, ch, cb, pl, esm = scene(100.0)

        def pay_case(amount, now_off, creative=False, dead=False, water=False):
            s2 = AcroC.state(uR)
            AcroC.profileReset(s2)
            for k in range(153, 281):
                s2[k] = 0.0
            esm2, hv2 = health(100.0, 0.0 if dead else 100.0)
            st.comps.get(ref).put(T["stats"], esm2)
            if water:
                msc = alloc(MSC)
                ms = MVS()
                ms.inFluid = True
                for fld in MSC.class_.getDeclaredFields():
                    if fld.getType() == MVS.class_:
                        fld.setAccessible(True)
                        fld.set(msc, ms)
                put(st, ref, T["movementStatesComponentType"], msc)
            else:
                st.comps.get(ref).remove(T["movementStatesComponentType"])
            AcroC.noteRoll(uR, JFloat(amount))
            tt = int(float(s2[288]))
            AcroC.falls(s2, st, ref, JLong(tt + now_off), creative)
            return [float(s2[152]), float(s2[288]), float(s2[290])]
        RL["falls"] = {"early": pay_case(30.0, 399), "paid": pay_case(30.0, 400), "cap": pay_case(500.0, 400), "creative": pay_case(30.0, 400, creative=True),
                       "dead": pay_case(30.0, 400, dead=True), "water": pay_case(30.0, 400, water=True), "consts": [float(AcroCfgC.FALL_DMG_XP),
                       float(AcroCfgC.FALL_MAX), float(AcroCfgC.ROLL), float(AcroCfgC.FALL_PER_MIN)]}
        # flush: the pending fall XP into the store (Acrobatics), the per-minute cap
        Store.DATA.remove(str(uR))
        s3 = AcroC.state(uR)
        AcroC.profileReset(s3)
        for k in range(153, 281):
            s3[k] = 0.0
        a0 = int(Store.data(uR)[ACROBATICS])
        st.comps.get(ref).remove(T["movementStatesComponentType"])   # out of the water again (the last falls case left it in)
        st.comps.get(ref).put(T["stats"], health(100.0)[0])
        AcroC.noteRoll(uR, JFloat(30.0))
        tt = int(float(s3[288]))
        AcroC.falls(s3, st, ref, JLong(tt + 400), False)
        AcroC.flush(prR, s3, JLong(tt + 400))
        a1 = int(Store.data(uR)[ACROBATICS])
        RL["flush"] = [a0, a1, float(s3[152])]
        # the numbers table at 100 max health: the engine's damage (0.4.13 paid that) and the roll note (0.4.14)
        table = []
        for sp in (21.5, 22.0, 25.0, 28.0, 31.0, 32.0):
            r_ = run_both([("v", sp), ("s", True, True, False)], 0.0, 100.0)
            table.append([sp, r_["dmg"], r_["note"]])
        RL["table"] = table
        RL["warn"] = bool(RollSys.FAILED_ONCE)
    except Exception as e:
        import traceback
        RL["error"] = traceback.format_exc()[-3000:]
    out["RL"] = RL

    # ================================================================ GP: the gathering pace (+ the Stats page label)
    GP = {}
    try:
        load_cfg(os.path.join(SCRATCH, "gp-cfg"), b"multiplier=1.0\n")
        GPc = JClass(PKG + "GatherPace")
        GP["defaults"] = [[bool(x) for x in GPc.SLOTS][:16], str(GPc.TEXT), float(GPc.EARLY), int(GPc.UNTIL), float(GPc.LATE), int(GPc.FROM), str(GPc.text())]
        GP["mult"] = [float(GPc.mult(lv)) for lv in range(0, 26)]
        uG = UUID(0x6A7E, 1)
        prG = mkpr(uG, "Gatherer")
        cum = [int(x) for x in Defs.CUM]
        ccum = [int(x) for x in Defs.CCUM]
        rows = []
        for slot in range(16):
            for lv in range(0, 26):
                d = JArray(JLong)(32)
                d[slot] = (ccum if Defs.isClass(slot) else cum)[lv]
                d[16 + slot] = lv
                Store.DATA.put(str(uG), d)
                got_lv = int(Store.level(uG, slot))
                vals = sorted(set(int(GPc.apply(uG, slot, JLong(7))) for _ in range(60)))
                rows.append([slot, lv, got_lv, int(GPc.apply(uG, slot, JLong(20))), vals, int(GPc.apply(uG, slot, JLong(0))), int(GPc.apply(None, slot, JLong(5)))])
        GP["apply"] = rows
        # chance rounding: 1 XP at level 13 (x2.55) -> 2 or 3, mean 2.55
        d = JArray(JLong)(32)
        d[MINING] = cum[13]
        Store.DATA.put(str(uG), d)
        p13 = [int(GPc.apply(uG, MINING, JLong(1))) for _ in range(20000)]
        GP["chance13"] = {"values": sorted(set(p13)), "mean": sum(p13) / float(len(p13))}
        GP["statsLine"] = dict((str(lv), [None if GPc.statsLine(s, lv) is None else str(GPc.statsLine(s, lv)) for s in (MINING, FORAGING, FARMING, ACROBATICS, ARCHERY)])
                               for lv in range(0, 26))
        # read(): the skill list (a non-gathering name warned + skipped, duplicates once), clamps, an empty list
        P = JClass("java.util.Properties")
        p_ = P()
        for k_, v_ in (("gather.boost.skills", "Mining, cooking ,FARMING,mining, "), ("gather.boost.early", "-2"), ("gather.boost.earlyUntil", "150"),
                       ("gather.boost.late", "1000"), ("gather.boost.lateFrom", "-4")):
            p_.setProperty(k_, v_)
        GPc.read(p_)
        GP["read"] = [[bool(x) for x in GPc.SLOTS][:4], str(GPc.TEXT), float(GPc.EARLY), int(GPc.UNTIL), float(GPc.LATE), int(GPc.FROM), str(GPc.text()),
                      float(GPc.mult(5)), float(GPc.mult(101))]
        p_ = P()
        p_.setProperty("gather.boost.skills", " , ")
        GPc.read(p_)
        GP["read_empty"] = [[bool(x) for x in GPc.SLOTS][:4], str(GPc.TEXT), str(GPc.text()), int(GPc.apply(uG, MINING, JLong(10)))]
        p_ = P()
        p_.setProperty("gather.boost.earlyUntil", "20")
        p_.setProperty("gather.boost.lateFrom", "10")
        GPc.read(p_)
        GP["crossed"] = [float(GPc.mult(lv)) for lv in (0, 10, 15, 20, 21, 30)]
        p_ = P()
        p_.setProperty("gather.boost.early", "1")
        p_.setProperty("gather.boost.late", "1")
        GPc.read(p_)
        GP["ones"] = [int(GPc.apply(uG, MINING, JLong(7))), GPc.statsLine(MINING, 0) is None]
        GPc.read(P())
        GP["check"] = [GPc.checkSkills("gather.boost.skills", "Mining,Foraging,Farming") is None, str(GPc.checkSkills("gather.boost.skills", "Mining,Cooking")),
                       GPc.checkSkills("gather.boost.skills", "") is None, GPc.checkSkills("gather.boost.skills", " , mining") is None,
                       str(GPc.checkSkills("gather.boost.skills", "Archery"))]
        GP["slotOf"] = [int(GPc.slotOf(x)) for x in ("Mining", "foraging", " Farming ", "", None, "Cooking", "Divinity")]
        # SkillXp: the pace before the tree Wisdom bonus (gain = blocks / F-harvests / sickles); grants (gain3 bonus off) exact
        def gained(slot, lv_xp, fn):
            d = JArray(JLong)(32)
            d[slot] = lv_xp
            Store.DATA.put(str(uG), d)
            fn()
            return int(Store.DATA.get(str(uG))[slot]) - lv_xp
        GP["gain"] = {"mining0": gained(MINING, 0, lambda: Xp.gain(prG, MINING, JLong(10))),
                      "grant0": gained(MINING, 0, lambda: Xp.gain3(prG, MINING, JLong(10), False, False)),
                      "acro0": gained(ACROBATICS, 0, lambda: Xp.gain(prG, ACROBATICS, JLong(10))),
                      "farming25": gained(FARMING, cum[25], lambda: Xp.gain(prG, FARMING, JLong(10))),
                      "foraging15": gained(FORAGING, cum[15], lambda: Xp.gain(prG, FORAGING, JLong(4)))}
        # FIX ROUND F4 (numbers review): gather.boost.early / late = 0 in the file (a skill that could never earn gathering XP: gain4 drops 0)
        # are kept at MIN_MULT 0.1 - 10 Mining XP at level 0 and at level 25 still pays 1, and 1 XP pays 0 or 1 (mean 0.1)
        p_ = P()
        p_.setProperty("gather.boost.early", "0")
        p_.setProperty("gather.boost.late", "0")
        GPc.read(p_)
        fl = [float(GPc.EARLY), float(GPc.LATE), float(GPc.MIN_MULT), str(GPc.text()), gained(MINING, 0, lambda: Xp.gain(prG, MINING, JLong(10))),
              gained(MINING, cum[25], lambda: Xp.gain(prG, MINING, JLong(10)))]
        d = JArray(JLong)(32)
        Store.DATA.put(str(uG), d)
        p1 = [int(GPc.apply(uG, MINING, JLong(1))) for _ in range(20000)]
        fl += [sorted(set(p1)), sum(p1) / float(len(p1))]
        GPc.read(P())
        GP["floor"] = fl
        SB = JClass("java.util.concurrent.ConcurrentHashMap")()
        tb = HM()
        tb.put("xp.mining", JClass("java.lang.Double").valueOf(0.5))
        tb.put("dd.mining", JClass("java.lang.Double").valueOf(0.1))
        tb.put("dodge.acrobatics", JClass("java.lang.Double").valueOf(0.05))
        SB.put("trees", tb)
        bridge.put("skill:bonus:" + str(uG), SB)
        GP["gain"]["mining0_wisdom"] = [gained(MINING, 0, lambda: Xp.gain(prG, MINING, JLong(10))) for _ in range(5)]
        # the Stats page: the pace line + the summed tree / tool line label
        d = JArray(JLong)(32)
        Store.DATA.put(str(uG), d)
        err, cmds = page_texts(StatsPage(prG, MINING))
        GP["page"] = {"err": err, "pace": [c for c in cmds if "Gathering XP" in c], "bonus": [c for c in cmds if "Bonuses (trees + tools)" in c],
                      "skilltree": [c for c in cmds if "Skill tree:" in c]}
        GP["treeLine"] = [str(StatsPage.treeLine(uG, MINING)), str(StatsPage.treeLine(uG, ACROBATICS)), StatsPage.treeLine(uG, FARMING) is None]
        d[MINING] = cum[15]
        err, cmds = page_texts(StatsPage(prG, MINING))
        GP["page15"] = [c for c in cmds if "Gathering XP" in c]
        d[MINING] = cum[30]
        err, cmds = page_texts(StatsPage(prG, MINING))
        GP["page30"] = [c for c in cmds if "Gathering XP" in c]
        err, cmds = page_texts(StatsPage(prG, ACROBATICS))
        GP["page_acro"] = [c for c in cmds if "Gathering XP" in c or "roll" in c]
        err, cmds = page_texts(StatsPage(prG, FARMING))
        GP["page_farming"] = [c for c in cmds if "sickle" in c]
        bridge.remove("skill:bonus:" + str(uG))
        Store.DATA.remove(str(uG))
    except Exception as e:
        import traceback
        GP["error"] = traceback.format_exc()[-2500:]
    out["GP"] = GP

    # ================================================================ SK: sickle swings
    SK = {}
    try:
        os.makedirs(os.path.join(SCRATCH, "sk-cfg"), exist_ok=True)
        load_cfg(os.path.join(SCRATCH, "sk-cfg"))                     # a FRESH default file: the default XP rules (the crop families' Farming XP)
        Sickle, SickleSys, SickleTask = JClass(PKG + "Sickle"), JClass(PKG + "SickleSys"), JClass(PKG + "SickleTask")
        BreakSys, HarvestSys = JClass(PKG + "BreakSys"), JClass(PKG + "HarvestSys")
        BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
        BTM = JClass("com.hypixel.hytale.assetstore.map.BlockTypeAssetMap")
        SDT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.StateData")
        BGA = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering")
        HDT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.HarvestingDropType")
        IDL = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemDropList")
        IDR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemDrop")
        CNT = "com.hypixel.hytale.server.core.asset.type.item.config.container."
        IDC = JClass(CNT + "ItemDropContainer")
        SIDC, MIDC, CIDC, DIDC = JClass(CNT + "SingleItemDropContainer"), JClass(CNT + "MultipleItemDropContainer"), JClass(CNT + "ChoiceItemDropContainer"), \
            JClass(CNT + "DroplistItemDropContainer")
        EIDC = JClass(CNT + "EmptyItemDropContainer")
        IM = JClass("com.hypixel.hytale.server.core.modules.item.ItemModule")
        BHU = JClass("com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils")
        IPE = JClass("com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent")
        BBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent")
        UBP = JClass("com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Post")
        IT = JClass("com.hypixel.hytale.protocol.InteractionType")
        V3I = JClass("org.joml.Vector3i")

        def container(c):
            t = c.get("Type")
            w = float(c.get("Weight", 100.0))
            if t == "Single":
                it = c.get("Item") or {}
                drop = IDR(it.get("ItemId"), None, int(it.get("QuantityMin", 1)), int(it.get("QuantityMax", 1)))
                return SIDC(drop, w)
            if t == "Multiple":
                kids = [container(x) for x in (c.get("Containers") or [])]
                return MIDC(JArray(IDC)(kids), w, int(c.get("MinCount", 1)), int(c.get("MaxCount", 1)))
            if t == "Choice":
                kids = [container(x) for x in (c.get("Containers") or [])]
                k = CIDC(JArray(IDC)(kids), w)
                setany(k, "rollsMin", JInt(int(c.get("RollsMin", 1))))
                setany(k, "rollsMax", JInt(int(c.get("RollsMax", 1))))
                return k
            if t == "Droplist":
                k = DIDC()
                setany(k, "droplistId", c.get("DroplistId"))
                setany(k, "weight", JD(w))
                return k
            k = alloc(EIDC)
            setany(k, "weight", JD(w))
            return k
        lists = {}
        for lid, body in model["drops"].items():
            cont = body.get("Container")
            lists[lid] = IDL(lid, container(cont) if isinstance(cont, dict) else None)
        setstatic(IDL, "ASSET_STORE", fstore(defmap(lists)))
        bts, by_id = [], {}
        states = {}
        for b in model["blocks"]:
            bt = alloc(BTY)
            setany(bt, "id", b["id"])
            if b.get("states") is not None:
                key = b["item"]
                sd = states.get(key)
                if sd is None:
                    sd = alloc(SDT)
                    s2b, b2s = HM(), HM()
                    for nm_ in b["states"]:
                        sid = "*%s_State_Definitions_%s" % (key, nm_)
                        s2b.put(nm_, sid)
                        b2s.put(sid, nm_)
                    setany(sd, "stateToBlock", s2b)
                    setany(sd, "blockToState", b2s)
                    states[key] = sd
                setany(bt, "state", sd)
            h = b.get("harvest")
            if h is not None:
                g = alloc(BGA)
                setany(g, "harvest", HDT(h.get("ItemId"), h.get("DropList")))
                setany(bt, "gathering", g)
            bts.append(bt)
            by_id[b["id"]] = bt
        btm = alloc(BTM)
        setany(btm, "array", JArray(BTY)([None] + bts + [None]))
        setany(btm, "arrayLock", RLock())
        setstatic(BTY, "ASSET_STORE", fstore(btm))
        imod = alloc(IM)
        setstatic(IM, "instance", imod)
        SK["fams"] = dict((str(fam), [int(x) for x in Cfg.resolve(fam)]) for fam in sorted(set(b["family"] for b in model["blocks"])))
        Sickle.KEYS = None
        ks = Sickle.keys()
        SK["keys"] = dict((str(k), [int(v[0]), bool(v[1]), None if v[2] is None else str(v[2]), sorted(str(x) for x in v[3])]) for k, v in ks.items())
        SysC = JClass("java.lang.System")
        SK["keys_cached"] = SysC.identityHashCode(Sickle.keys()) == SysC.identityHashCode(ks)
        SK["n_blocks"] = int(btm.getNextIndex())
        # the REAL rolled drops of every ripe Farming crop: each harvest = its produce first, one segment (fix round F1: ripe = StageFinal)
        rolls = {}
        ripe = [b for b in model["blocks"] if is_stage_final(b) and b.get("harvest")]
        for b in ripe:
            fam_rule = SK["fams"].get(b["family"])
            if not fam_rule or fam_rule[0] != FARMING or fam_rule[1] <= 0:
                continue
            bt = by_id[b["id"]]
            h = b["harvest"]
            res = {"first": {}, "segs": {}, "n": 0, "empty": 0}
            for _ in range(300):
                ds = BHU.getDrops(bt, 1, h.get("ItemId"), h.get("DropList"))
                lst = [ds.get(i) for i in range(ds.size())]
                if not lst:
                    res["empty"] += 1
                    continue
                fi = str(lst[0].getItemId())
                res["first"][fi] = res["first"].get(fi, 0) + 1
                sg = Sickle.segments(JClass("java.util.Arrays").asList(JArray(IS)(lst)), ks)
                sig = "%d:%s:%d" % (sg.size(), str(sg.get(0)[0]) if sg.size() else "-", sg.get(0)[1].size() if sg.size() else 0)
                ok = sg.size() == 1 and sg.get(0)[1].size() == len(lst)
                res["segs"]["ok" if ok else sig] = res["segs"].get("ok" if ok else sig, 0) + 1
                res["n"] += 1
            rolls[b["id"]] = res
        SK["rolls"] = rolls
        # random swings of 2-6 crops (+ a foreign stack after some crops): the Python model of segments decides the expected crops
        rnd = random.Random(4140)
        farm_ripe = [b for b in ripe if SK["fams"].get(b["family"], [0, 0])[0] == FARMING and SK["fams"].get(b["family"], [0, 0])[1] > 0]
        swings = []
        for _ in range(400):
            picks = [rnd.choice(farm_ripe) for _ in range(rnd.randint(2, 6))]
            stacks, crops = [], []
            for b in picks:
                ds = BHU.getDrops(by_id[b["id"]], 1, b["harvest"].get("ItemId"), b["harvest"].get("DropList"))
                lst = [ds.get(i) for i in range(ds.size())]
                stacks += lst
                crops.append([b["id"], [[str(x.getItemId()), int(x.getQuantity())] for x in lst]])
                if rnd.random() < 0.2:
                    sap = IS("Ingredient_Tree_Sap", 1)
                    stacks.append(sap)
                    crops[-1][1].append(["Ingredient_Tree_Sap", 1])
            sg = Sickle.segments(JClass("java.util.Arrays").asList(JArray(IS)(stacks)), ks)
            swings.append({"crops": crops, "segs": [[str(sg.get(i)[0]), [[str(x.getItemId()), int(x.getQuantity())] for x in sg.get(i)[1]]] for i in range(sg.size())]})
        SK["swings"] = swings
        SK["seg_edge"] = {}
        for nm, ids in (("empty", []), ("foreign_only", ["Ingredient_Tree_Sap", "Rubble_Stone"]), ("lead_foreign", ["Ingredient_Tree_Sap", "Plant_Crop_Wheat_Item", "Ingredient_Life_Essence"]),
                        ("berry_merge", ["Plant_Fruit_Berries_Red", "Plant_Fruit_Berries_Red", "Ingredient_Stick"]),
                        ("berry_two", ["Plant_Fruit_Berries_Red", "Ingredient_Stick", "Plant_Fruit_Berries_Red"]),
                        ("wheat_twice", ["Plant_Crop_Wheat_Item", "Plant_Crop_Wheat_Item"]),
                        ("sap_between_berries", ["Plant_Fruit_Berries_Red", "Ingredient_Tree_Sap", "Plant_Fruit_Berries_Red"])):
            sg = Sickle.segments(JClass("java.util.Arrays").asList(JArray(IS)([IS(i, 1) for i in ids])) if ids else AL(), ks)
            SK["seg_edge"][nm] = [[str(sg.get(i)[0]), [str(x.getItemId()) for x in sg.get(i)[1]]] for i in range(sg.size())]
        SK["seg_null"] = [int(Sickle.segments(None, ks).size()), int(Sickle.segments(AL(), None).size())]
        # ---- the handlers, executed (FakeWorld QUEUE: world tasks run on drain, like the world thread after the event dispatch)
        wS, esS = world("default")
        stS = mkstore(esS)
        uS = UUID(0x51C, 1)
        prS = mkpr(uS, "Sami")
        rS = Ref(stS, 0)
        setany(prS, "entity", rS)
        plS = player("Adventure")
        inv = alloc(JClass("skyytest.FakeInventory"))
        SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
        CIC = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
        IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
        box = SIC(JClass("java.lang.Short")(36).shortValue())
        inv.comb = CIC(JArray(IC)([box]))
        setany(plS, "inventory", inv)
        hot = alloc(JClass("skyytest.FakeHotbar"))
        hot.item = IS("Tool_Sickle_Iron", 1)
        for typ, comp in ((T["playerRef"], prS), (T["playerComponentType"], plS), (T["hotbarInventoryComponentType"], hot), (T["stats"], health(100.0)[0])):
            put(stS, rS, typ, comp)
        chS = alloc(MapChunk)
        chS.comps = IHM()
        chS.ref = rS
        FakeW.QUEUE = True
        FakeW.Q.clear()
        FakeW.ERR.clear()

        def farm_xp():
            return int(Store.data(uS)[FARMING])

        def set_farm(x):
            d = Store.data(uS)
            d[FARMING] = x
            d[16 + FARMING] = int(Defs.levelOf(FARMING, JLong(x)))

        def drops_of(bid):
            b = [x for x in model["blocks"] if x["id"] == bid][0]
            ds = BHU.getDrops(by_id[bid], 1, b["harvest"].get("ItemId"), b["harvest"].get("DropList"))
            return [ds.get(i) for i in range(ds.size())]

        def swing(stacks, cancel=(), pre=None):
            evs = [IPE(x) for x in stacks]
            for e in evs:
                SickleSys().handle(JInt(0), chS, stS, None, e)
            for i in cancel:
                evs[i].setCancelled(True)
            if pre is not None:
                pre()
            q = [str(x.getClass().getSimpleName()) for x in FakeW.Q]
            n = int(FakeW.drain())
            return q, n
        wheat = "*Plant_Crop_Wheat_Block_State_Definitions_StageFinal"
        carrot = "*Plant_Crop_Carrot_Block_State_Definitions_StageFinal"
        berry = "*Plant_Crop_Berry_Block_State_Definitions_StageFinal"
        cases = {}
        set_farm(0)
        x0 = farm_xp()
        q, n = swing(drops_of(wheat) + drops_of(carrot))
        cases["swing"] = {"xp": farm_xp() - x0, "queued": q, "pend_after": bool(Sickle.PEND.containsKey(uS))}
        x0 = farm_xp()
        q, n = swing(drops_of(wheat) + drops_of(berry) + drops_of(wheat), cancel=(0,))
        cases["cancel_first_stack"] = {"xp": farm_xp() - x0, "queued": q}
        evs_all = drops_of(wheat)
        x0 = farm_xp()
        q, n = swing(evs_all, cancel=tuple(range(len(evs_all))))
        cases["all_cancelled"] = {"xp": farm_xp() - x0, "queued": q}
        hot.item = IS("Tool_Hoe_Iron", 1)
        x0 = farm_xp()
        q, n = swing(drops_of(wheat))
        cases["hoe"] = {"xp": farm_xp() - x0, "queued": q}
        hot.item = None
        q, n = swing(drops_of(wheat))
        cases["empty_hand"] = {"xp": 0, "queued": q}
        hot.item = IS("Tool_Sickle_Iron", 1)
        setany(plS, "gameMode", GM.Creative)
        q, n = swing(drops_of(wheat))
        cases["creative"] = {"queued": q}
        setany(plS, "gameMode", GM.Adventure)
        Sickle.ON = False
        q, n = swing(drops_of(wheat))
        cases["off"] = {"queued": q}
        Sickle.ON = True
        bridge.put("profile:busy:" + str(uS), JBool.TRUE)
        x0 = farm_xp()
        q, n = swing(drops_of(wheat))
        cases["busy"] = {"xp": farm_xp() - x0, "queued": q, "pend_after": bool(Sickle.PEND.containsKey(uS))}
        bridge.remove("profile:busy:" + str(uS))
        x0 = farm_xp()
        q, n = swing(drops_of(wheat), pre=lambda: PLAYERS.remove(uS))
        cases["offline"] = {"xp": farm_xp() - x0, "queued": q}
        PLAYERS.put(uS, prS)
        # F-harvest: HarvestSys sees UseBlockEvent$Post on the ripe wheat first, then its pickups arrive (within 2 s) - Sickle pays nothing
        x0 = farm_xp()
        HarvestSys().handle(JInt(0), chS, stS, None, UBP(IT.values()[0], None, V3I(3, 64, 3), by_id[wheat]))
        use_rec = bool(Sickle.USE.containsKey(uS))
        evs = [IPE(x) for x in drops_of(wheat)]
        for e in evs:
            SickleSys().handle(JInt(0), chS, stS, None, e)
        q = [str(x.getClass().getSimpleName()) for x in FakeW.Q]
        pend = bool(Sickle.PEND.containsKey(uS))
        FakeW.drain()
        cases["f_harvest"] = {"use": use_rec, "queued": q, "pend": pend, "sickle_xp": farm_xp() - x0}
        Sickle.USE.put(uS, JLongC.valueOf(JLong(int(JClass("java.lang.System").currentTimeMillis()) - 2001)))
        x0 = farm_xp()
        q, n = swing(drops_of(wheat))
        cases["after_window"] = {"xp": farm_xp() - x0, "queued": q}
        Sickle.USE.clear()
        # F pickup of a loose block: BreakSys sees BreakBlockEvent(null item) first; the pickups of the same dispatch are not sickle swings
        # a loose block WITHOUT an XP rule (its BreakTask pays nothing itself, so any Farming XP here would come from Sickle)
        loose = [x for x in model["blocks"] if x["id"] == "Rubble_Stone"] or [x for x in model["blocks"] if SK["fams"].get(x["family"], [0])[0] < 0]
        lbt = by_id[loose[0]["id"]]
        SK["loose"] = [loose[0]["id"], SK["fams"].get(loose[0]["family"])]
        bev = BBE(None, V3I(5, 64, 5), lbt)
        x0 = farm_xp()
        BreakSys().handle(JInt(0), chS, stS, None, bev)
        brk = bool(Sickle.BRK.containsKey(uS))
        evs = [IPE(x) for x in drops_of(wheat)]
        for e in evs:
            SickleSys().handle(JInt(0), chS, stS, None, e)
        q = [str(x.getClass().getSimpleName()) for x in FakeW.Q]
        pend = bool(Sickle.PEND.containsKey(uS))
        FakeW.drain()
        cases["f_pickup"] = {"brk": brk, "queued": q, "pend": pend, "brk_after": bool(Sickle.BRK.containsKey(uS)), "sickle_xp": farm_xp() - x0}
        # the context is per thread and 250 ms: 300 ms later, or on another thread, the pickups count again
        BreakSys().handle(JInt(0), chS, stS, None, BBE(None, V3I(6, 64, 6), lbt))
        a = Sickle.BRK.get(uS)
        a[1] = JLongC.valueOf(JLong(int(JClass("java.lang.System").nanoTime()) - 300000000))
        x0 = farm_xp()
        q, n = swing(drops_of(wheat))
        cases["after_250ms"] = {"xp": farm_xp() - x0, "queued": q}
        Sickle.BRK.clear()
        BreakSys().handle(JInt(0), chS, stS, None, BBE(None, V3I(7, 64, 7), lbt))
        other = {}

        def other_thread():
            try:
                jt = JClass("java.lang.Thread")
                other["same"] = bool(Sickle.inBreak(uS, JClass("java.lang.System").nanoTime()))
            except Exception as ex:
                other["err"] = repr(ex)
        th = threading.Thread(target=other_thread)
        th.start()
        th.join()
        other["here"] = bool(Sickle.inBreak(uS, JClass("java.lang.System").nanoTime()))
        cases["thread"] = other
        FakeW.drain()
        Sickle.BRK.clear()
        # a break WITH the sickle in hand: no F-pickup context (its drops fall to the ground - no pickup event)
        BreakSys().handle(JInt(0), chS, stS, None, BBE(IS("Tool_Sickle_Iron", 1), V3I(8, 64, 8), by_id[wheat]))
        cases["break_with_sickle"] = {"brk": bool(Sickle.BRK.containsKey(uS))}
        FakeW.drain()
        # the double drop: dd.farming 1.0 -> every crop once more into storage, only that crop's own stacks (not the sap of the same swing)
        SB = JClass("java.util.concurrent.ConcurrentHashMap")()
        tb = HM()
        tb.put("dd.farming", JClass("java.lang.Double").valueOf(1.0))
        SB.put("trees", tb)
        bridge.put("skill:bonus:" + str(uS), SB)
        for i in range(36):
            box.removeItemStackFromSlot(JClass("java.lang.Short")(i).shortValue())
        wd = drops_of(wheat)
        texts()
        x0 = farm_xp()
        q, n = swing(wd + [IS("Ingredient_Tree_Sap", 1)])
        got = []
        for i in range(36):
            st_ = box.getItemStack(JClass("java.lang.Short")(i).shortValue())
            if st_ is not None and not st_.isEmpty():
                got.append([str(st_.getItemId()), int(st_.getQuantity())])
        cases["double"] = {"xp": farm_xp() - x0, "box": sorted(got), "want": sorted([[str(x.getItemId()), int(x.getQuantity())] for x in wd]),
                           "msg": [t for t in texts() if "Double drop" in t], "dd_failed": bool(JClass(PKG + "Perks").DD_FAILED_ONCE)}

        # FIX ROUND F1 (both reviews): the place / swing / place loop. A placed stateless plant swung by a sickle hands back its own item
        # (harvest0: no ripeness, no placed check) - its REAL harvest drops through the handlers must pay NOTHING and double nothing (dd.farming
        # 1.0 still on), with ignorePlaced on or off; wild grass (no StageFinal) neither; a swing through wheat + Health3 pays the wheat only
        def box_now():
            out_ = []
            for i_ in range(36):
                st2 = box.getItemStack(JClass("java.lang.Short")(i_).shortValue())
                if st2 is not None and not st2.isEmpty():
                    out_.append([str(st2.getItemId()), int(st2.getQuantity())])
            return sorted(out_)

        def box_clear():
            for i_ in range(36):
                box.removeItemStackFromSlot(JClass("java.lang.Short")(i_).shortValue())
        loop = {}
        for bid in ("Plant_Crop_Health3", "Plant_Crop_Mana1", "Plant_Crop_Stamina2", "Plant_Cactus_Flower",
                    "*Plant_Crop_Wild_Grass_Block_State_Definitions_Stage3", "Plant_Crop_Mushroom_Boomshroom_Small"):
            box_clear()
            ds = drops_of(bid)
            x0 = farm_xp()
            q, n = swing(ds)
            loop[bid] = {"ids": sorted(set(str(x.getItemId()) for x in ds)), "xp": farm_xp() - x0, "queued": q, "box": box_now()}
        box_clear()
        x0 = farm_xp()
        for _ in range(10):
            swing(drops_of("Plant_Crop_Health3"))
        loop["health3_x10"] = {"xp": farm_xp() - x0, "box": box_now()}
        Cfg.IGNORE_PLACED = False
        box_clear()
        x0 = farm_xp()
        q, n = swing(drops_of("Plant_Crop_Health3"))
        loop["health3_ignorePlaced_off"] = {"xp": farm_xp() - x0, "queued": q, "box": box_now()}
        Cfg.IGNORE_PLACED = True
        box_clear()
        wd2, hd2 = drops_of(wheat), drops_of("Plant_Crop_Health3")
        x0 = farm_xp()
        q, n = swing(wd2 + hd2)
        loop["mixed"] = {"xp": farm_xp() - x0, "queued": q, "box": box_now(), "want": sorted([[str(x.getItemId()), int(x.getQuantity())] for x in wd2])}
        box_clear()
        cases["loop"] = loop
        bridge.remove("skill:bonus:" + str(uS))
        # farming.sickle.items: only the listed id starts are sickles
        Sickle.ITEMS = JArray(JClass("java.lang.String"))(["Tool_Sickle_Iron"])
        hot.item = IS("Tool_Sickle_Copper", 1)
        q, n = swing(drops_of(wheat))
        cases["items_copper"] = {"queued": q}
        hot.item = IS("Tool_Sickle_Iron", 1)
        q, n = swing(drops_of(wheat))
        cases["items_iron"] = {"queued": q}
        Sickle.ITEMS = JArray(JClass("java.lang.String"))(["Tool_Sickle_"])
        SK["cases"] = cases
        SK["isSickle"] = [bool(Sickle.isSickle(x)) for x in ("Tool_Sickle_Iron", "Tool_Sickle_Crude", "Tool_Hoe_Iron", "tool_sickle_iron", None, "")]
        SK["check"] = [Sickle.checkItems("farming.sickle.items", "Tool_Sickle_") is None, str(Sickle.checkItems("farming.sickle.items", " , ")),
                       [str(x) for x in Sickle.parse(" Tool_Sickle_ ,Tool_Scythe_, Tool_Sickle_ ,")]]
        # retain: the contexts of players who left are dropped (Acro.retainOnline -> Sickle.retain)
        uOff = UUID(0x51C, 99)
        for m_ in (Sickle.BRK, Sickle.USE, Sickle.PEND):
            m_.put(uOff, JLongC.valueOf(JLong(1)))
            m_.put(uS, JLongC.valueOf(JLong(1)))
        JClass(PKG + "Acro").retainOnline()
        SK["retain"] = [bool(Sickle.BRK.containsKey(uOff)), bool(Sickle.USE.containsKey(uOff)), bool(Sickle.PEND.containsKey(uOff)),
                        bool(Sickle.BRK.containsKey(uS)), bool(Sickle.USE.containsKey(uS)), bool(Sickle.PEND.containsKey(uS))]
        for m_ in (Sickle.BRK, Sickle.USE, Sickle.PEND):
            m_.clear()
        SK["err"] = [str(x) for x in FakeW.ERR]
        SK["failed"] = [bool(Sickle.FAILED_ONCE), bool(Sickle.SEEN)]
        # a load drops the crop map (the rules may have changed)
        Sickle.keys()
        load_cfg(os.path.join(SCRATCH, "sk-cfg"))
        SK["keys_after_load"] = Sickle.KEYS is None
        FakeW.QUEUE = False
        FakeW.Q.clear()
    except Exception as e:
        import traceback
        SK["error"] = traceback.format_exc()[-3000:]
        try:
            JClass("skyytest.FakeWorld").QUEUE = False
        except Exception:
            pass
    out["SK"] = SK

    # ================================================================ DM: the comment fix (DocMig)
    DM = {}
    try:
        DMig = JClass(PKG + "DocMig")
        o_, n_ = MREG_DOC_OLD, MREG_DOC_NEW

        def du(t):
            r = DMig.docUpdate(t)
            return None if r is None else [str(r[0]), int(r[1])]
        DM["consts"] = [str(DMig.OLD), str(DMig.NEW), str(DMig.WHO)]
        DM["cases"] = {
            "lf": du("a=1\n" + o_ + "\nmana.regen.inCombat=50\n"),
            "crlf": du("a=1\r\n" + o_ + "\r\nmana.regen.inCombat=50\r\n"),
            "hand": du("a=1\n" + o_.replace("never while charging", "never while CHARGING") + "\n"),
            "indented": du("a=1\n  " + o_ + "\n"),
            "continued": du("a=1 \\\n" + o_ + "\nb=2\n"),
            "two": du(o_ + "\n" + o_ + "\n"),
            "no_eol": du("a=1\n" + o_),
            "none": du("a=1\nb=2\n"),
            "bang": du("a=1\n!" + o_[1:] + "\n")}
        # run() on a scratch file: the comment fixed once, the old bytes kept in config-history first; again = nothing
        dd = os.path.join(SCRATCH, "dm-run")
        os.makedirs(dd, exist_ok=True)
        src = ("x=1\r\n# head\r\n" + o_ + "\r\nmana.regen.inCombat=50\r\n").encode("latin-1")
        open(os.path.join(dd, "xp.properties"), "wb").write(src)
        Cfg.FILE = path(os.path.join(dd, "xp.properties"))
        L["Hist"].DIR = None
        L["Rows"].HOME = None
        L["CLog"].FILE = None
        r1 = str(DMig.run())
        a1 = open(os.path.join(dd, "xp.properties"), "rb").read()
        hist = []
        for r_, ds_, fs_ in os.walk(dd):
            for fn_ in fs_:
                if fn_ != "xp.properties":
                    hist.append([os.path.relpath(os.path.join(r_, fn_), dd).replace(os.sep, "/"), open(os.path.join(r_, fn_), "rb").read() == src])
        r2 = str(DMig.run())
        a2 = open(os.path.join(dd, "xp.properties"), "rb").read()
        DM["run"] = {"r1": r1, "a1": a1.decode("latin-1"), "hist": hist, "r2": r2, "same2": a1 == a2}
        Cfg.FILE = path(os.path.join(dd, "missing", "xp.properties"))
        DM["missing"] = str(DMig.run())
        Cfg.FILE = None
        DM["null"] = str(DMig.run())
    except Exception as e:
        import traceback
        DM["error"] = traceback.format_exc()[-2500:]
    out["DM"] = DM
    return out


# ============================================================================================ child: bytecode compare
def version_only(a, b):
    la, lb = a.split(chr(10)), b.split(chr(10))
    return len(la) == len(lb) and all(x == y or x.replace(PREV_VERSION, VERSION, 1) == y for x, y in zip(la, lb))


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
    # 0.4.14: the new call orders (section X 0.4.14)
    res["calls"]["kill_sys"] = where("KillSys", "onComponentAdded(", ["MobXp.kill(", "SkillCfg.combatXp(", "SkillXp.gain(", "PartyXp.share", "SkillCfg.classXp("])
    res["calls"]["mob_kill"] = where("MobXp", "kill(", ["MobXp.levelOf(", "SkillStore.level(", "MobXp.factor(", "MobXp.pay(", "SkillCfg.classXp(", "SkillXp.gain(",
                                                       "PartyXp.share2("])
    res["calls"]["gain4"] = where("SkillXp", "gain4(", ["ClassCurve.tick(", "GatherPace.apply(", "SkillBonus.boost(", "SkillStore.addK("])
    res["calls"]["fell_one"] = where("FellCredit", "one(", ["GatherPace.apply(", "SkillBonus.boost(", "SkillXp.gain3("])
    res["calls"]["break_sys"] = where("BreakSys", "handle(", ["getItemInHand", "Sickle.breakOpen(", "World.execute"])
    res["calls"]["break_task"] = where("BreakTask", "run(", ["Sickle.breakDone(", "isCancelled", "SkillXp.gain("])
    res["calls"]["harvest_sys"] = where("HarvestSys", "handle(", ["getHarvest", "Sickle.useOpen(", "SkillCfg.resolve(", "World.execute"])
    res["calls"]["sickle_sys"] = where("SickleSys", "handle(", ["Sickle.ON", "Sickle.inBreak(", "Sickle.inUse(", "SkillXp.creative(", "InventoryComponent.getItemInHand(",
                                                               "Sickle.isSickle(", "Sickle.add("])
    res["calls"]["roll_tick"] = where("RollSys", "tick(", ["AcroCfg.ENABLED", "AcroCfg.ROLL", "getMovementUpdateQueue", "getCurrentFallDistance", "RollSys.fallDamageOn(",
                                                          "RollSys.land("])
    res["calls"]["roll_fd"] = where("RollSys", "fallDamageOn(", ["Store.getExternalData", "EntityStore.getWorld", "World.getWorldConfig", "WorldConfig.isFallDamageEnabled"])
    res["calls"]["party_how"] = where("PartyXp", "howText(", ["MobXp.ON", '"mob:fn:level"', "of the kill XP at their own class skill level",
                                                             "of your kill XP (in their own class skill)"])
    res["calls"]["pl_setup14"] = where("SkyySkillsPlugin", "setup(", ["HealMig.run(", "DocMig.run(", "SkillCfg.load(", "Class com.skyy.skills.SickleSys",
                                                                     "Class com.skyy.skills.RollSys", "registerSystem"])
    res["calls"]["stats_lines"] = where("StatsPage", "lines(", ["GatherPace.statsLine(", "StatsPage.treeLine("])
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


# ============================================================================================ parent: the 0.4.14 Assets.zip model
def _resolved_items(z):
    items = {}
    for n in z.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            try:
                items[os.path.basename(n)[:-5]] = json.loads(z.read(n).decode("utf-8-sig"))
            except Exception:
                pass

    def resolved(iid, depth=0):
        d = items.get(iid)
        if d is None or depth > 20:
            return {}
        p = d.get("Parent")
        base = resolved(p, depth + 1) if isinstance(p, str) and p != iid else {}
        out = dict(base)
        for k, v in d.items():
            if k == "BlockType" and isinstance(v, dict) and isinstance(base.get("BlockType"), dict):
                bt = dict(base["BlockType"])
                bt.update(v)
                out["BlockType"] = bt
            else:
                out[k] = v
        return out
    return items, resolved


def crop_model():
    """every harvestable block of Assets.zip (read in memory, never written) as the BlockTypes the 0.4.14 child builds: an item with growth
    states = its base block (state data, never ripe when it has a StageFinal) + one block per state ("*<item>_State_Definitions_<name>",
    the state's Harvest over the base's; ripe = StageFinal, or any state of an item without one); an item without states = one block (ripe);
    + every drop list those harvests reach (Droplist containers followed) + vanilla's MovementConfig Default roll numbers"""
    z = zipfile.ZipFile(ASSETS)
    items, resolved = _resolved_items(z)
    drops = {}
    for n in z.namelist():
        if n.startswith("Server/Drops/") and n.endswith(".json"):
            try:
                drops[os.path.basename(n)[:-5]] = json.loads(z.read(n).decode("utf-8-sig"))
            except Exception:
                pass
    blocks, need = [], set()

    def harvest(g):
        h = (g or {}).get("Harvest") if isinstance(g, dict) else None
        if not isinstance(h, dict) or not (h.get("ItemId") or h.get("DropList")):
            return None
        return {"ItemId": h.get("ItemId"), "DropList": h.get("DropList")}
    for iid in sorted(items):
        bt = resolved(iid).get("BlockType")
        if not isinstance(bt, dict):
            continue
        defs = (bt.get("State") or {}).get("Definitions") or {}
        if not isinstance(defs, dict):
            defs = {}
        bh = harvest(bt.get("Gathering"))
        if defs:
            names = sorted(defs)
            final = "StageFinal" in names
            sb = []
            for nm in names:
                sd = defs.get(nm) or {}
                sh = harvest(sd.get("Gathering")) if isinstance(sd, dict) and isinstance(sd.get("Gathering"), dict) and sd["Gathering"].get("Harvest") else bh
                if sh is not None:
                    sb.append({"id": "*%s_State_Definitions_%s" % (iid, nm), "item": iid, "family": iid, "states": names, "state": nm, "harvest": sh,
                               "ripe": nm == "StageFinal" or not final})
            if bh is not None or sb:
                blocks.append({"id": iid, "item": iid, "family": iid, "states": names, "state": None, "harvest": bh, "ripe": not final})
                blocks.extend(sb)
        elif bh is not None:
            blocks.append({"id": iid, "item": iid, "family": iid, "states": None, "state": None, "harvest": bh, "ripe": True})
    for b in blocks:
        if b["harvest"] and b["harvest"].get("DropList"):
            need.add(b["harvest"]["DropList"])

    def walk(c, acc):
        if not isinstance(c, dict):
            return
        if c.get("Type") == "Droplist" and c.get("DroplistId"):
            if c["DroplistId"] not in acc:
                acc.add(c["DroplistId"])
                walk((drops.get(c["DroplistId"]) or {}).get("Container"), acc)
        for k in c.get("Containers") or []:
            walk(k, acc)
    acc = set(need)
    for lid in list(need):
        walk((drops.get(lid) or {}).get("Container"), acc)
    mcn = [n for n in z.namelist() if n.startswith("Server/Entity/MovementConfig/") and n.endswith("/Default.json")]
    mcj = json.loads(z.read(mcn[0]).decode("utf-8-sig")) if len(mcn) == 1 else {}
    mv = dict((k, mcj.get(k)) for k in ("MinFallSpeedToEngageRoll", "MaxFallSpeedRollFullMitigation", "MaxFallSpeedToEngageRoll",
                                         "FallDamagePartialMitigationPercent"))
    return {"blocks": blocks, "drops": dict((lid, drops[lid]) for lid in sorted(acc) if lid in drops), "movement": mv,
            "missing_lists": sorted(lid for lid in acc if lid not in drops)}


def all_drops_py(model, lid, depth=0):
    """ItemDropContainer.getAllDrops in Python: every Single's item id in container order (Multiple and Choice: all children, in order;
    Droplist: the referenced list's container; Empty / unknown: nothing)"""
    out = []
    body = model["drops"].get(lid)
    if body is None or depth > 20:
        return out

    def walk(c):
        if not isinstance(c, dict):
            return
        t = c.get("Type")
        if t == "Single":
            out.append((c.get("Item") or {}).get("ItemId"))
        elif t in ("Multiple", "Choice"):
            for k in c.get("Containers") or []:
                walk(k)
        elif t == "Droplist":
            out.extend(all_drops_py(model, c.get("DroplistId"), depth + 1))
    walk(body.get("Container"))
    return out


def is_stage_final(b):
    """fix round F1: the only blocks Sickle.keys() takes - the StageFinal state of a block with growth states (Sickle.addCrop:
    SkillCfg.hasFinalStage + stateOf == StageFinal)"""
    return b.get("state") == "StageFinal" and "StageFinal" in (b.get("states") or [])


def expected_keys(model, fams):
    """Sickle.keys() in Python: StageFinal blocks (fix round F1) with a Harvest whose family's rule pays Farming XP -> produce key (the first
    drop id, else the Harvest ItemId) -> [lowest XP, multi (the key twice in one harvest), alphabetically first family, every id those
    harvests can drop]"""
    exp = {}
    for b in model["blocks"]:
        h = b.get("harvest")
        if not h or not is_stage_final(b):
            continue
        rule = fams.get(b["family"])
        if not rule or rule[0] != FARMING or rule[1] <= 0:
            continue
        ds = all_drops_py(model, h.get("DropList")) if h.get("DropList") else []
        key, cnt, ids = None, 0, set()
        for i in ds:
            if i is None:
                continue
            ids.add(i)
            if key is None:
                key = i
            if key == i:
                cnt += 1
        iid = h.get("ItemId")
        if iid is not None:
            ids.add(iid)
            if key is None:
                key = iid
            if key == iid:
                cnt += 1
        if key is None:
            continue
        e = exp.get(key)
        if e is None:
            exp[key] = [rule[1], cnt > 1, b["family"], ids | {key}]
        else:
            e[0] = min(e[0], rule[1])
            e[1] = e[1] or cnt > 1
            e[2] = min(e[2], b["family"])
            e[3] |= ids
    return dict((k, [v[0], v[1], v[2], sorted(v[3])]) for k, v in exp.items())


def segments_py(ids, keys):
    """Sickle.segments in Python (keys = the Java map as returned: id -> [xp, multi, fam, ids])"""
    segs, cur, own, prev = [], None, None, None
    for i in ids:
        info = keys.get(i)
        if info is not None:
            if not (info[1] and cur is not None and i == prev and i == cur[0]):
                cur = [i, []]
                segs.append(cur)
                own = set(info[3])
        elif cur is not None and own is not None and i not in own:
            prev = i
            continue
        if cur is not None:
            cur[1].append(i)
        prev = i
    return segs


def f32r(x):
    return struct.unpack("f", struct.pack("f", float(x)))[0]


def roll_py(sp, mc, mx, rolling, fluid):
    """FallDamagePlayers' arithmetic in Python (the float fields widened to double like the engine): [unreduced, engine damage, rolled]"""
    mn, full, eng, pct = (f32r(v) for v in mc)
    if not (sp > mn) or fluid:
        return [0, 0, 0]
    base = math.pow(0.5799999833106995 * (sp - mn), 2.0) + 10.0
    d0 = int(math.floor(f32r(mx) / 100.0 * base))
    d1, r = d0, 0
    if rolling:
        if sp <= full:
            d1, r = 0, 1
        elif sp <= eng:
            d1, r = int(d0 * (1.0 - pct / 100.0)), 1
    return [d0, d1, r]


# ============================================================================================ parent
def main():
    if "--mkfake" in sys.argv:
        return run_mkfake(arg("--mkfake"))
    if "--old-run" in sys.argv:
        return run_old(arg("--old-run"), arg("--out"), arg("--fake"), arg("--xs"))
    if "--new-run" in sys.argv:
        return run_new(arg("--new-run"), arg("--out"), arg("--fake"), arg("--xs"), arg("--crops"))
    if "--bytecode" in sys.argv:
        return run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
    if "--audit" in sys.argv:
        return run_audit(arg("--audit"), arg("--fake"), arg("--out"))
    for j in (JAR, OLD_JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    if not os.path.isfile(ASSETS):
        sys.exit("Assets.zip is not at %s (read only, in memory)" % ASSETS)
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
    LIVE_STALE = MREG_DOC_OLD.encode("latin-1") in livenow
    LIVE_N14 = [k for k in N14_KEYS if ("\n" + k + "=").encode("latin-1") in livenow.replace(b"\r\n", b"\n")]
    print("live xp.properties: the stale Mana comment %s, %d / 15 keys of the 0.4.14 block already there" % ("present" if LIVE_STALE else "absent", len(LIVE_N14)))
    cmodel = crop_model()
    crops_file = os.path.join(SCRATCH, "crops.json")
    json.dump(cmodel, open(crops_file, "w"))
    mvv = cmodel["movement"]
    check(all(isinstance(mvv.get(k), (int, float)) for k in mvv) and len(mvv) == 4 and not cmodel["missing_lists"]
          and len([b for b in cmodel["blocks"] if b["ripe"]]) >= 40,
          "the Assets.zip model: %d harvestable blocks, %d drop lists (missing %s), MovementConfig Default roll %s" % (
              len(cmodel["blocks"]), len(cmodel["drops"]), cmodel["missing_lists"][:3], mvv))
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
                                    for n_ in ("FakeAcc", "FakeStore", "FakeCB", "FakeStatMap", "FixedCharging", "FakePerms", "LookupIn", "BadAccess",
                                               "MapStore", "MapChunk", "MapCB", "FakeAssetStore", "FakeHotbar", "FakeInventory")),
          "the stand-in classes were generated")
    outs = {"old": os.path.join(SCRATCH, "run-old.json"), "new": os.path.join(SCRATCH, "run-new.json"), "bc": os.path.join(SCRATCH, "bytecode.json"),
            "audit": os.path.join(SCRATCH, "audit.json"), "prev": os.path.join(SCRATCH, "run-prev.json")}
    p = subprocess.run([sys.executable, me, "--old-run", OLD_JAR, "--out", outs["old"], "--fake", fake, "--xs", xs_file, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["old"]), "child JVM for %s ran" % os.path.basename(OLD_JAR))
    p = subprocess.run([sys.executable, me, "--old-run", PREV_JAR, "--out", outs["prev"], "--fake", fake, "--xs", xs_file, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["prev"]), "child JVM for %s ran" % os.path.basename(PREV_JAR))
    p = subprocess.run([sys.executable, me, "--new-run", JAR, "--out", outs["new"], "--fake", fake, "--xs", xs_file, "--crops", crops_file, "--dir", SCRATCH],
                       env=env)
    check(p.returncode == 0 and os.path.isfile(outs["new"]), "child JVM for %s ran" % os.path.basename(JAR))
    p = subprocess.run([sys.executable, me, "--bytecode", PREV_JAR, "--new", JAR, "--out", outs["bc"], "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["bc"]), "bytecode child ran")
    p = subprocess.run([sys.executable, me, "--audit", JAR, "--fake", fake, "--out", outs["audit"], "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(outs["audit"]), "engine-access audit child ran")
    if FAILS:
        return finish()
    new, old, bc = json.load(open(outs["new"])), json.load(open(outs["old"])), json.load(open(outs["bc"]))
    au, prev = json.load(open(outs["audit"])), json.load(open(outs["prev"]))
    # ---------------------------------------------------------------- A
    for r in (new, prev, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"][:3]))
    print("A. -Xverify:all: %s %d / %d, %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                                     os.path.basename(prev["jar"]), prev["loaded"], prev["classes"],
                                                                     os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    if FAILS:
        return finish()
    D, O, PV = new["data"], old["data"], prev["data"]
    check("N14_error" not in D, "the 0.4.14 sections ran: %s" % D.get("N14_error"))
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
    check(T["general"] == PV["general"] and all(T["xs"][s_] == PV["xs"][s_] for s_ in T["xs"]) and T["cper"] == PV["cper"] and T["per"] == PV["per"],
          "T: every slot's level / into / need / progress and generalLevel = the 0.4.13 jar's too")
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
    # 0.4.14: 0.4.12 / 0.4.13 already ran on the live world (record + both 0.4.12 blocks) - start 1 = DocMig fixes the stale comment (a
    # config-history copy first) + SkillCfg.ensure14 appends the 0.4.14 block; nothing else; start 2 changes nothing
    check(lv["r1"]["ready"] and lv["r1"]["pending"] == {} and lv["r1"]["curve"] == "",
          "M live (0.4.12 already ran there): a start reads the record, scans nothing, nobody pending: %r" % lv["r1"]["curve"])
    check(lv["r1"]["heal"] == "", "M live: HealMig has nothing to do on the live data (its 0.4.11 marker is there): %r" % lv["r1"]["heal"])
    x0_ = lv["xp0"]
    nl_ = "\r\n" if "\r\n" in x0_ else "\n"
    want1 = x0_
    if MREG_DOC_OLD in x0_:
        want1 = nl_.join(MREG_DOC_NEW if ln.rstrip("\r") == MREG_DOC_OLD else ln for ln in x0_.split(nl_)) if nl_ == "\r\n" else \
            "\n".join(MREG_DOC_NEW if ln == MREG_DOC_OLD else ln for ln in x0_.split("\n"))
    blk_ = "".join(ln + "\n" for ln in D["n14_block"].split("\n") if ln and (ln.startswith("#") or ("\n" + ln.split("=")[0] + "=") not in "\n" + x0_.replace("\r\n", "\n")))
    if any(not ln.startswith("#") for ln in blk_.split("\n") if ln):
        want1 = want1 + (nl_ if want1.endswith("\n") or want1 == "" else nl_ + nl_) + blk_.replace("\n", nl_)
    check(lv["xp1"] == want1, "M live start 1: xp.properties = the live bytes with ONLY the stale Mana comment line rewritten (%s) + the 0.4.14 block "
          "appended (%d new key lines): first difference at %s" % ("was there" if MREG_DOC_OLD in x0_ else "was not there",
                                                                   sum(1 for ln in blk_.split("\n") if ln and not ln.startswith("#")),
                                                                   next((i for i, (a_, b_) in enumerate(zip(lv["xp1"], want1)) if a_ != b_), None)))
    stale_ = MREG_DOC_OLD in x0_
    check(lv["r1"]["doc"].startswith("xp.properties: the outdated Mana regen comment") == stale_ and (not stale_ or (lv["bak_old"] and len(lv["new_bak"]) == 1
          and lv["new_bak"][0].startswith("config-history/") and "0.4.14 Mana regen comment fix" in lv["index_tail"])),
          "M live start 1: DocMig %r; the old bytes kept in config-history first (%s, index line %r)" % (lv["r1"]["doc"][:90], lv["new_bak"], lv["index_tail"][-120:]))
    allowed_ = set(["xp.properties", "config-history/index.log"] + lv["new_bak"])
    check(set(lv["changed1"]) <= allowed_ and "xp.properties" in lv["changed1"] and lv["others_same"] and lv["players_same"],
          "M live start 1: only xp.properties + the config-history copy / index changed; class-curve record, players, placed blocks untouched: %s" % lv["changed1"])
    check(lv["changed2"] == [] and lv["xp2"] == lv["xp1"] and lv["r2"]["doc"] == "" and lv["r2"]["ready"] and lv["r2"]["pending"] == {} and lv["r2"]["curve"] == "",
          "M live: start 2 changes nothing (no stale line, every 0.4.14 key there): %s %r" % (lv["changed2"], lv["r2"]["doc"]))
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
    print("M. live copy (%d profile files, 0.4.12's record): start 1 = the stale comment fixed (History copy %s) + the 0.4.14 block appended, nothing else; "
          "start 2 nothing; ClassCurve: edited copy 3 test profiles told once each (28,600 / 111,600 / 500 coins, unlock line); %d real profile(s) a fresh "
          "scan would list: %s" % (lv["n_players"], ", ".join(lv["new_bak"]) or "-", len(extras), extras))
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
    En, Eo, Ep = D["E"], O["E"], PV["E"]
    check("error" not in En and "error" not in Eo, "E: the 500-tick script ran through the real ManaRegen.tick on both jars: %s / %s" % (En.get("error"), Eo.get("error")))
    check("error" not in Ep and [r[:5] + r[6:] for r in Ep.get("rows", [])] == [r[:5] + r[6:] for r in En.get("rows", [])] and Ep.get("calls") == En.get("calls")
          and PV.get("Hch", {}).get("rows") == D.get("Hch", {}).get("rows"),
          "E 0.4.14: the 500-tick Mana trace and the charging trace = the 0.4.13 jar's at every tick / pulse (the Mana regen is unchanged)")
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
    nd, od, pd_ = D["defaults"], O["defaults"], PV["defaults"]
    want = pd_.replace("# SkyySkills %s - XP rules" % PREV_VERSION, "# SkyySkills %s - XP rules" % VERSION, 1)
    check(MREG_DOC_OLD in want and MREG_DOC_NEW not in want, "C: the 0.4.13 default file holds the stale Mana comment line")
    want = want.replace(MREG_DOC_OLD, MREG_DOC_NEW, 1) + "\n" + D["n14_block"]
    check(nd == want and ("# SkyySkills %s - XP rules" % VERSION) in nd and MREG_DOC_OLD not in nd,
          "C: the 0.4.14 default file = 0.4.13's with the version line, the fixed Mana comment line and the 0.4.14 block at the end (first difference at %s)"
          % next((i for i, (a_, b_) in enumerate(zip(nd, want)) if a_ != b_), None))
    check(D["block14_none"] == D["n14_block"] and sum(1 for ln in D["n14_block"].split("\n") if ln and not ln.startswith("#")) == 15
          and D["n14_block"].endswith("\n"),
          "C: SkillCfg.block14(nothing set) = the whole 0.4.14 block (%d lines)" % D["n14_block"].count("\n"))
    check(C["lf"] == {"exact": True, "again_same": True, "no_cr": True}, "C: a 0.4.11-era LF file = itself + a blank line + the two 0.4.12 blocks + the 0.4.14 block, once: %s" % C["lf"])
    check(C["crlf"] == {"exact": True, "all_crlf": True}, "C: the same file in CRLF: the blocks appended in CRLF, every byte before them kept: %s" % C["crlf"])
    check(C["admin"] == {"same_kept": True, "list_added": True, "SAME": True, "class_eq_general": True}, "C: an admin's sameAsOthers=true is kept (only the list appended): %s" % C["admin"])
    check(C["noeol"], "C: a file without a final newline gets one before the blank line")
    check(C["short"] == [3, 3, 3, 2, True, True], "C: a 3-entry class list = class max 3: %s" % C["short"])
    check(C["bad"] == [100, True, True], "C: a bad class list = the default class table + a bad line: %s" % C["bad"])
    check(C["fresh"] == [100, False, 50, True] and "class skills own table, max level 100, in-combat Mana regen 50%" in C["fresh_text"], "C: a fresh file: %s %s" % (C["fresh"], C["fresh_text"][-160:]))
    print("C. default file = 0.4.13's + the version line, the fixed comment and the 0.4.14 block; pre-0.4.12 files get all three blocks once (LF / CRLF kept); admin switch kept")
    # ---------------------------------------------------------------- K
    K = D["K"]
    ro, rn, rp = O["rows"]["rows"], D["rows"]["rows"], PV["rows"]["rows"]
    ko, kn = [r[0] for r in ro], [r[0] for r in rn]
    rn13 = [r for r in rn if r[0] not in N14_KEYS]
    # fix round F3: the one 0.4.13 row that changed is party.combatShare.fraction's help (each member's share at their own class skill level)
    PARTY_HELP14 = "Share of the kill XP each nearby party member gets (0.5 = half), at their own class skill level."
    rp14 = [r if r[0] != "party.combatShare.fraction" else r[:10] + [PARTY_HELP14] for r in rp]
    check(len(rn) == 195 and rn13 == rp14 and rp == ro and rp14 != rp and len(rp) == 180 and sorted(set(kn) - set(ko)) == sorted(N14_KEYS),
          "K: 195 Server Setup rows = 0.4.13's 180 exactly (keys, order, every field; only party.combatShare.fraction's help reworded - fix F3) + the "
          "15 new 0.4.14 rows: %s" % sorted(set(kn) - set(ko)))
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
    check(D["kill"] == O["kill"] == PV["kill"] and D["base"] == O["base"] == PV["base"] and D["other"] == O["other"] == PV["other"],
          "K: kill XP at the defaults without a mob level (SkillCfg.combatXp / classXp) = 0.4.12's and 0.4.13's: %s" % D["kill"])
    check(D["paid"] == O["paid"] == PV["paid"], "K: grants / crafting / heal XP paid = 0.4.12's and 0.4.13's (no gathering pace on grants): %s" % D["paid"])
    n14 = dict((r[0], r) for r in rn if r[0] in N14_KEYS)
    want14 = {"combat.levelXp.enabled": ["Kill XP by mob level", "parts", "bool", "true", "", "", "", "", "live,part,danger"],
              "combat.levelBonus": ["Kill XP per mob level", "combat", "dec", "0.05", "0", "10", "", "", "live"],
              "combat.gap.free": ["Level gap with no change", "combat", "int", "5", "0", "100", "", "", "live"],
              "combat.gap.above": ["Higher mob: extra XP a level", "combat", "dec", "0.05", "0", "10", "", "", "live"],
              "combat.gap.max": ["Higher mob: XP cap", "combat", "dec", "3.5", "1", "100", "", "x", "live"],
              "combat.gap.below": ["Lower mob: XP lost a level", "combat", "dec", "0.05", "0", "10", "", "", "live"],
              "combat.gap.min": ["Lower mob: least XP", "combat", "dec", "0.1", "0", "1", "", "x", "live"],
              "acro.rollBonus": ["Extra XP for a rolled landing", "acrobatics", "dec", "0.5", "0", "10", "", "", "live"],
              "gather.boost.skills": ["Gathering pace skills", "gathering", "text", "Mining,Foraging,Farming", "", "300", "", "", "live"],
              "gather.boost.early": ["Early gathering XP boost", "gathering", "dec", "3", "0.1", "100", "", "x", "live"],   # fix F4: min 0.1
              "gather.boost.earlyUntil": ["Full boost up to level", "gathering", "int", "10", "0", "100", "", "", "live"],
              "gather.boost.late": ["Later gathering XP boost", "gathering", "dec", "1.5", "0.1", "100", "", "x", "live"],   # fix F4: min 0.1
              "gather.boost.lateFrom": ["Later boost from level", "gathering", "int", "20", "0", "100", "", "", "live"],
              "farming.sickle.enabled": ["Sickle swings pay Farming XP", "gathering", "bool", "true", "", "", "", "", "live"],
              "farming.sickle.items": ["Sickle item ids", "gathering", "text", "Tool_Sickle_", "", "500", "", "", "live,adv"]}
    bad14 = dict((k, n14.get(k, [None] * 11)[1:10]) for k, v in want14.items() if n14.get(k, [None] * 11)[1:10] != v)
    check(not bad14 and all(len(n14[k][10]) <= 100 and n14[k][10] for k in N14_KEYS), "K: the 15 new rows' labels / categories / types / defaults / bounds / units / flags "
          "(the part switch live,part,danger; help <= 100): %s" % bad14)
    check(kn[kn.index("divinity.healXp.enabled") + 1] == "combat.levelXp.enabled" and kn[kn.index("combat.classWeaponOnly") + 1:kn.index("combat.classWeaponOnly") + 7] == N14_KEYS[1:7]
          and kn[kn.index("acro.fallMaxXpPerMinute") + 1] == "acro.rollBonus" and kn[kn.index("block") - 7:kn.index("block")] == N14_KEYS[8:],
          "K: the new rows' places: the part switch after the heal XP switch, the gap rows after 'Only class weapons earn XP', the roll row after the fall cap, "
          "the gathering rows before the block table")
    dvals = dict(ln.split("=", 1) for ln in D["n14_block"].split("\n") if ln and not ln.startswith("#"))
    check(sorted(dvals) == sorted(N14_KEYS) and all(dvals[k] == n14[k][4] for k in N14_KEYS), "K: every new row's default = its line in the 0.4.14 block: %s" % dvals)
    print("K. rows 195 = 0.4.13's 180 + 15 new (places, fields, defaults = the block); class curve rows cut / raise / scale / read; XP maths without a mob level = 0.4.12 / 0.4.13")
    # ---------------------------------------------------------------- F (0.4.13 -> 0.4.14)
    check_f14(bc)
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
    check_0414(D, PV, bc, cmodel)
    return finish()


# 0.4.14 class compare: class -> (new methods, changed methods (beyond the version string; any of the alternatives), new fields)
F14_WANT = {
    "SkillCfg": (["block14", "ensure14"], [["ensureManaRegen", "load"], ["<clinit>", "ensureManaRegen", "load"]], ["N14_DEFAULTS"]),   # MREG_DEFAULTS is inlined
    "CfgFile": ([], [["<clinit>"]], []),                                                          # the kit's row arrays 180 -> 195
    "AcroCfg": (["readRoll", "rollText"], [[], ["<clinit>"]], ["ROLL"]),
    "Acro": (["noteRoll"], [["falls", "noteFall", "profileReset", "retainOnline"]], []),
    "SkillXp": ([], [["gain4"]], []),
    "FellCredit": ([], [["one"]], []),
    "PartyXp": (["one2", "share2"], [["howText", "one", "share"]], []),                           # fix round F3: howText (mob levels)
    "BreakSys": ([], [["handle"]], []),
    "BreakTask": ([], [["run"]], []),
    "HarvestSys": ([], [["handle"]], []),
    "KillSys": ([], [["onComponentAdded"]], []),
    "StatsPage": ([], [["how", "lines", "treeLine"]], []),
    "SkyySkillsPlugin": ([], [["setup"], ["setup", "start"]], []),
    "CfgRows": ([], [["<clinit>"]], []),
}
NEW14 = ["DocMig", "GatherPace", "MobXp", "RollSys", "Sickle", "SickleSys", "SickleTask"]


def check_f14(bc):
    diff = bc["diff"]
    beyond = dict((n.split("/")[-1][:-6], d) for n, d in diff.items() if set(d["changed"]) != set(d["vo"]) or d["new"] or d["gone"]
                  or d["fields_new"] or d["fields_gone"])
    vonly = sorted(n.split("/")[-1][:-6] for n in diff if n.split("/")[-1][:-6] not in beyond)
    check(set(beyond) == set(F14_WANT), "F: classes changed beyond the version string (0.4.13 -> 0.4.14): %s (unexpected %s, missing %s)"
          % (sorted(beyond), sorted(set(beyond) - set(F14_WANT)), sorted(set(F14_WANT) - set(beyond))))
    check(bc["only_new"] == ["com/skyy/skills/%s.class" % c for c in NEW14] and bc["only_old"] == [],
          "F: + the 7 new classes (MobXp, RollSys, GatherPace, Sickle, SickleSys, SickleTask, DocMig), none gone: %s %s" % (bc["only_new"], bc["only_old"]))
    for cn_, (wnew, wch, wf) in sorted(F14_WANT.items()):
        d_ = beyond.get(cn_, {})
        gotn = sorted(k.split("(")[0] for k in d_.get("new", []))
        gotc = sorted(set(k.split("(")[0] for k in d_.get("changed", []) if k not in d_.get("vo", [])))
        gotf = sorted(f.split(" ")[0] for f in d_.get("fields_new", []))
        check(gotn == sorted(wnew) and gotc in [sorted(x) for x in wch] and gotf == sorted(wf) and not d_.get("gone") and not d_.get("fields_gone"),
              "F: %s: + methods %s, changed %s, + fields %s, nothing gone (want %s / %s / %s)" % (cn_, gotn, gotc, gotf, wnew, wch, wf))
    check(bc["calls"]["global_lookups"] == [], "F: no (J) level lookup is called anywhere in the new jar: %s" % bc["calls"]["global_lookups"][:3])
    for cls in ("ManaRegen", "ManaRegenFn", "CombatFn", "ManaCmd", "ClassCurve", "AcroSys", "SkillDefs", "SkillStore", "Overall", "Perks", "SkillKit",
                "SkillsCmd", "SkillTick", "ReloadCmd", "HealXp", "BridgeXp", "BridgeTask", "HealMig", "ManaMig", "ManaGuard", "ManaCost",
                "SkillHealFn", "SkillAddFn", "SkillCraftFn", "SkillXpFn", "SkillFn", "OverallFn", "Xbow", "XbowCfg", "DivCfg", "OverallCfg", "SkillClass",
                "CfgHist", "CfgLog", "SkillBonus", "SkillsPage", "OverallPage", "TopCmd", "SkillMsg", "AcroFallSys", "AcroFallSeenSys", "HarvestTask",
                "PlaceSys", "Brew", "Fell", "FellWatch", "PartyCfg"):
        check("com/skyy/skills/%s.class" % cls in bc["same"] or cls in vonly, "F: %s byte-identical (or the version string only)" % cls)
    zp, zn = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
    mo, mn = json.loads(zp.read("manifest.json")), json.loads(zn.read("manifest.json"))
    kd = sorted(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k))
    sent = ("Kill XP grows with the SkyyMobs level and the level gap to your class skill (up to +250%; party members use their own class skill); a "
            "crouch-roll landing pays +50% Acrobatics XP; Mining, Foraging and Farming XP x3 to level 10, easing to x1.5 by level 20; sickle swings pay "
            "Farming XP and roll double drops (Server Setup). ")
    check(kd == ["Description", "Name", "Version"] and mn["Description"] == mo["Description"].replace("Uninstall / downgrade:", sent + "Uninstall / downgrade:", 1)
          and mn["Version"] == VERSION, "F: manifest: %s differ; the Description = 0.4.13's + the 0.4.14 sentence before 'Uninstall / downgrade'" % kd)
    nonclass = sorted(n for n in set(zp.namelist()) | set(zn.namelist()) if not n.endswith(".class") and n != "manifest.json"
                      and (n not in zp.namelist() or n not in zn.namelist() or zp.read(n) != zn.read(n)))
    check(nonclass == [], "F: every non-class entry byte-identical (the 40 spell overrides): %s" % nonclass[:5])
    print("F. class bytes 0.4.13 -> 0.4.14: + %s; changed beyond the version: %s; version only %d; byte-identical %d"
          % (", ".join(NEW14), ", ".join(sorted(beyond)), len(vonly), len(bc["same"])))



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


def _lf(L):
    return 1.0 if L < 1 else max(0.0, 1.0 + 0.05 * float(L - 1))


def _gf(L, S):
    if L < 1:
        return 1.0
    d = L - (0 if S < 0 else S)
    if d > 5:
        g = 1.0 + 0.05 * float(d - 5)
        return 3.5 if g > 3.5 else g
    if d < -5:
        g = 1.0 - 0.05 * float(-d - 5)
        return 0.1 if g < 0.1 else g
    return 1.0


def _pay_range(x):
    """MobXp.pay / GatherPace.apply rounding: a product within 1e-9 of a whole number is that number, else floor or ceil"""
    r = round(x)
    if abs(x - r) < 1e-9:
        return int(r), int(r)
    return int(math.floor(x)), int(math.floor(x)) + 1


def _mult(lv, e=3.0, u=10, l=1.5, f=20):
    if lv <= u:
        return e
    if lv >= f:
        return l
    return e + (l - e) * float(lv - u) / float(f - u)


def _num(v):
    """DivCfg.num"""
    if v == math.floor(v) and abs(v) < 1e15:
        return str(int(v))
    return repr(math.floor(v * 1000.0 + 0.5) / 1000.0)


def check_0414(D, PV, bc, cmodel):
    """0.4.14's sections KX RL GP SK DM C14 + the bytecode order checks (see the module docstring)"""
    # ---------------------------------------------------------------- KX
    KX = D.get("KX", {})
    check("error" not in KX, "KX: the kill XP section ran: %s" % KX.get("error"))
    if "error" not in KX:
        check(KX["defaults"] == [True, 0.05, 5, 0.05, 3.5, 0.05, 0.1, 3.0], "KX: defaults on, +5%% a level, free 5, +5%% to x3.5, -5%% to x0.1; class XP x3: %s" % KX["defaults"])
        gbad = [g for g in KX["grid"] if g[2] != _lf(g[0]) or g[3] != _gf(g[0], g[1]) or g[4] != _lf(g[0]) * _gf(g[0], g[1])]
        check(len(KX["grid"]) == 19 * 22 and not gbad, "KX: levelFactor / gapFactor / factor for %d (mob level, class skill) pairs = Skyy's rule exactly: %s"
              % (len(KX["grid"]), gbad[:3]))
        gm = dict(((g[0], g[1]), g) for g in KX["grid"])
        check(gm[(33, 11)][2:] == [_lf(33), 1.85, _lf(33) * 1.85] and abs(gm[(33, 11)][2] - 2.6) < 1e-12 and gm[(11, 11)][3] == 1.0 and gm[(16, 10)][3] == 1.05
              and gm[(17, 11)][3] == 1.05 and gm[(100, 1)][3] == 3.5 and gm[(5, 10)][3] == 1.0 and gm[(5, 11)][3] == 0.95 and gm[(1, 100)][3] == 0.1
              and gm[(0, 50)][2:] == [1.0, 1.0, 1.0] and gm[(-1, 50)][2:] == [1.0, 1.0, 1.0] and gm[(1, -3)][3] == 1.0,
              "KX: examples: Lv 33 vs 11 = 2.6 x 1.85; 6 levels above = x1.05; Lv 100 vs 1 capped x3.5; 6 below = x0.95; far below x0.1; no level = 1")
        check(KX["pay_exact"] == [270, 90, 0, 0, 0, 33, 51, 9000000000000000],
              "KX: MobXp.pay exact: 36 x 3 x 2.5 = 270, a non-class slot no x3 (90), 0 / no factor = 0, 10 x 3 x 1.1 = 33 (1e-9 rule), the cap: %s" % KX["pay_exact"])
        sk = KX["skyy"]
        check(sk["base"] == 36 and sk["classXp"] == 108 and abs(sk["lf"] - 2.6) < 1e-12 and sk["gf"] == 1.85 and abs(sk["factor"] - 2.6 * 1.85) < 1e-12
              and sk["values"] == [519, 520] and abs(sk["mean"] - 519.48) < 0.03,
              "KX SKYY'S EXAMPLE: Lv 33 Skeleton_Scout (178 HP) at Divinity 11: combatXp %d (0.4.13: x3 = %d) x %.4f x %.4f = %.2f -> %s, mean %.3f over %d kills"
              % (sk["base"], sk["classXp"], sk["lf"], sk["gf"], 36 * 3 * sk["factor"], sk["values"], sk["mean"], sk["n"]))
        check(KX["frac"]["values"] == [24, 25] and abs(KX["frac"]["mean"] - 24.15) < 0.03, "KX: 7 x 3 x 1.15 = 24.15 -> 24 / 25, mean %.3f" % KX["frac"]["mean"])
        check(KX["clamped"][:7] == [False, 0.0, 100, 10.0, 1.0, 0.0, 1.0] and KX["clamped"][7:9] == [1.0, 1.0] and KX["clamped"][9] == "off",
              "KX: the reader clamps (bonus 0..10, free 0..100, above 0..10, max 1..100, below 0..10, min 0..1); off = both factors 1: %s" % KX["clamped"])
        check(KX["text"] == "on (+5% a mob level; more than 5 levels above your class skill +5% a level up to x3.5, below -5% a level down to x0.1; SkyyMobs levels)",
              "KX: MobXp.text(): %r" % KX["text"])
        lv = KX["levelOf"]
        want_lv = {"no_fn": -1, "real": 33, "real_no_uuidc": -1, "real_level0": -1, "real_unknown": -1, "real_wrong_world": -1, "real_no_world": 33,
                   "real_direct": 33, "minus1": -1, "zero": -1, "long12": 12, "string": -1, "null": -1, "double7": 7, "throw": [False, -1, True, -1],
                   "not_fn": -1, "nulls": [-1, -1]}
        lbad = dict((k, (lv.get(k), v)) for k, v in want_lv.items() if lv.get(k) != v)
        check(not lbad and "real_error" not in lv, "KX: MobXp.levelOf through the REAL SkyyMobs 0.1.2 MobLevelFn (33; the wrong world, an unknown mob, level 0, no "
              "UUIDComponent = none) and stand-ins (no bridge / -1 / 0 / a String / null / a non-function = none, a Long 12 = 12, throwing = none + logged once): %s %s"
              % (lbad, lv.get("real_error")))
        check(lv.get("args") and lv["args"][0][0] == "default", "KX: mob:fn:level is asked Object[]{world name, the NPC's UUIDComponent uuid}: %s" % lv.get("args"))
        kk = KX["kill"]
        check(kk["levels"] == [11, 1, 30, 40, 60, 1, 1], "KX kill: the killer Divinity 11, members Archer 1 / Warrior 30 / Priest 40 / Archer 60 (+ one out of range, "
              "one in creative): %s" % kk["levels"])
        kbad = [r for r in kk["killer"] if r[0] not in (519, 520) or r[1] != r[0]]
        kmean = sum(r[0] for r in kk["killer"]) / float(len(kk["killer"]))
        check(len(kk["killer"]) == 400 and not kbad and abs(kmean - 519.48) < 0.1,
              "KX kill: MobXp.kill pays the killer 519 / 520 into Divinity every time (mean %.3f over 400 kills): %s" % (kmean, kbad[:3]))
        fr = kk["fraction"]
        mbad, means = [], []
        for i, (g, f) in enumerate(zip(kk["gains"], kk["factors"])):
            if i >= 4:
                if any(x != 0 for x in g):
                    mbad.append((i, "paid", sorted(set(g))))
                continue
            lo, hi = _pay_range(108.0 * f)
            lo2, hi2 = int(math.floor(lo * fr)), int(math.ceil(hi * fr))
            if any(x < lo2 or x > hi2 for x in g):
                mbad.append((i, sorted(set(g)), lo2, hi2))
            m_ = sum(g) / float(len(g))
            means.append(round(m_, 2))
            if abs(m_ - 108.0 * f * fr) > 0.2:
                mbad.append((i, "mean", m_, 108.0 * f * fr))
        check(not mbad and abs(fr - 0.5) < 1e-12, "KX party: each member gets 0.5 x pay(36 x 3 x levelFactor x THEIR OWN gap): Archer 1 -> x%.2f (%.2f), Warrior 30 -> x%.2f "
              "(%.2f), Priest 40 -> x%.2f (%.2f), Archer 60 -> x%.2f (%.2f) - means %s; out of range / creative 0: %s"
              % (kk["factors"][0], 54 * kk["factors"][0], kk["factors"][1], 54 * kk["factors"][1], kk["factors"][2], 54 * kk["factors"][2], kk["factors"][3],
                 54 * kk["factors"][3], means, mbad[:3]))
        check(KX["no_level"] == [108, 108, [54, 54, 54, 54, 0, 0]] and KX["off"] == [108, 108, [54, 54, 54, 54, 0, 0]] and KX["old_share"] == [54, 54, 54, 54, 0, 0],
              "KX: no mob level (SkyyMobs missing) / the part off = 0.4.13 exactly (108, members 54); the old share() signature = the 0.4.13 share: %s %s %s"
              % (KX["no_level"], KX["off"], KX["old_share"]))
        ht = KX.get("howText", [])
        check(len(ht) == 3 and ht[0] == ". Party members within 48 blocks get 50% of the kill XP at their own class skill level"
              and ht[1] == ht[2] == ". Party members within 48 blocks get 50% of your kill XP (in their own class skill)",
              "KX FIX F3: the Stats how-to line: with mob levels 'of the kill XP at their own class skill level'; no SkyyMobs / the part off = the "
              "0.4.13 text: %s" % ht)
        print("KX. kill XP by mob level: Skyy's Lv 33 / Divinity 11 example %s (mean %.2f, 0.4.13 108); party members on their own skill: means %s; no level = 0.4.13"
              % (sk["values"], sk["mean"], means))
    # ---------------------------------------------------------------- RL
    RL = D.get("RL", {})
    check("error" not in RL, "RL: the roll landing section ran: %s" % RL.get("error"))
    if "error" not in RL:
        mv = cmodel["movement"]
        mcw = [float(mv["MinFallSpeedToEngageRoll"]), float(mv["MaxFallSpeedRollFullMitigation"]), float(mv["MaxFallSpeedToEngageRoll"]),
               float(mv["FallDamagePartialMitigationPercent"])]
        check(RL["mc"] == [f32r(x) for x in mcw] and RL["chain"] == [f32r(mcw[0]), True],
              "RL: the MovementConfig behind the REAL World.getGameplayConfig -> PlayerConfig -> asset map = Assets.zip Default.json %s: %s" % (mcw, RL["chain"]))
        gb, nrolled, nengine = [], 0, 0
        for mx, sp, rolling, fluid, dmg, fd_after, note, noted, d in RL["grid"]:
            py = roll_py(sp, RL["mc"], mx, rolling, fluid)
            want_dmg = [float(d[1])] if d[1] > 0 else []
            want_note = None
            if rolling and not fluid and d[2] == 1 and d[0] > 0:
                want_note = f32r(f32r(f32r(float(d[0])) * 100.0) / f32r(mx))
            if dmg != want_dmg or d != py or note != want_note or noted != (1 if want_note is not None else 0) or fd_after != 0.0:
                gb.append([mx, sp, rolling, fluid, dmg, d, py, note, want_note, fd_after])
            nrolled += 1 if want_note is not None else 0
            nengine += 1 if dmg else 0
        check(len(RL["grid"]) == 4 * 23 * 4 and not gb and nrolled > 20 and nengine > 50,
              "RL: %d landings through the REAL FallDamagePlayers.tick then RollSys.tick: the engine's damage = RollSys.damage = the Python model, the fall "
              "distance reset, a roll note exactly when the roll engaged (%d) = the unreduced damage x 100 / max health: %s" % (len(RL["grid"]), nrolled, gb[:3]))
        g100 = dict(((r[1], r[2], r[3]), r) for r in RL["grid"] if r[0] == 100.0)
        check(g100[(25.0, True, False)][4] == [] and g100[(25.0, True, False)][6] is not None and g100[(25.0, False, False)][4] != []
              and g100[(31.0, True, False)][4] != [] and g100[(31.0, True, False)][6] is not None and g100[(31.0001, True, False)][6] is None
              and g100[(21.0, True, False)][6] is None and g100[(25.0, True, True)][6] is None,
              "RL: at 25 a roll takes ALL damage (no Damage event - 0.4.13 paid nothing) and is noted; at 31 partial + noted; past 31 or at 21 or in fluid no note")
        def note_of(r):
            return r["note"]
        check(note_of(RL["vel_only"]) is not None and RL["vel_only"]["dmg"] != [] and note_of(RL["before_landing"]) is not None
              and note_of(RL["two_landings"]) is not None and len(RL["two_landings"]["dmg"]) == 1 and note_of(RL["first_not_rolled"]) is None
              and RL["first_not_rolled"]["dmg"] != [] and RL["no_fall"] == [True, 0],
              "RL: the speed from the Velocity component alone; a rolling state before the landing ignored; two landings in one tick = the first only (one "
              "Damage, one note); a first landing without the roll = no note; no fall distance = nothing: %s %s %s %s %s"
              % (RL["vel_only"], RL["before_landing"], RL["two_landings"], RL["first_not_rolled"], RL["no_fall"]))
        check(RL["roll0"]["note"] is None and RL["acro_off"]["note"] is None, "RL: acro.rollBonus 0 / acro.enabled off = RollSys notes nothing: %s %s" % (RL["roll0"], RL["acro_off"]))
        fo = RL["fd_off"]
        check(fo["engine"] == [0, 0, 5.0] and fo["note"] is None and fo["noted"] == 0 and fo["on_note"] == 15.0 and fo["fn"] == [True, False, False, False, False],
              "RL FIX F2: a world with fall damage OFF: the REAL FallDamagePlayers.tick(F, I, Store) processes no landing (no Damage, fall distance kept 5) "
              "and RollSys notes nothing for a rolled 25 b/s landing (was 15 -> 225 XP); switched on = noted 15; fallDamageOn: on world / no config / "
              "no world / null store / off world = %s: %s" % (fo["fn"], fo))
        check(RL["deps"][-2:] == ["com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$FallDamagePlayers", "BEFORE"] and not RL["parallel"] and RL["group"],
              "RL: RollSys depends BEFORE DamageSystems$FallDamagePlayers, not parallel, no group: %s" % RL["deps"])
        check(len(RL["orders"]) == 6 and all(o == ["RollSys", "FallDamagePlayers", "ProcessPlayerInput"] for o in RL["orders"]),
              "RL: the engine's own DependencyGraph (resolveEdges + sort) puts RollSys before FallDamagePlayers before ProcessPlayerInput from all 6 start orders: %s"
              % RL["orders"])
        check(RL["notefall"]["skip"] == [0.0, 0.0] and RL["notefall"]["later"] == [True, 16.0],
              "RL: Acro.noteFall skips the Damage of a landing RollSys noted (< 1 s); 1.5 s later it records again: %s" % RL["notefall"])
        fa = RL["falls"]
        c_ = fa["consts"]
        check(c_ == [10.0, 2000.0, 0.5, 3000.0] and fa["early"][0] == 0.0 and fa["early"][1] > 0.0 and fa["paid"] == [450.0, 0.0, 1.0] and fa["cap"] == [2000.0, 0.0, 1.0]
              and fa["creative"] == [0.0, 0.0, 1.0] and fa["dead"] == [0.0, 0.0, 1.0] and fa["water"] == [0.0, 0.0, 1.0],
              "RL: Acro.falls pays a roll 400 ms later: 30 x 10 x 1.5 = 450, capped at acro.fallXpMax 2000, nothing in creative / dead / in water: %s" % fa)
        check(RL["flush"] == [0, 450, 0.0], "RL: Acro.flush puts the 450 into the store's Acrobatics XP (per-minute cap 3000): %s" % RL["flush"])
        check(not RL["warn"], "RL: RollSys never logged a failure")
        tab = []
        for sp, dmg, note in RL["table"]:
            old_xp = min(2000.0, (dmg[0] if dmg else 0.0) * 10.0)
            new_xp = min(2000.0, note * 10.0 * 1.5) if note is not None else old_xp
            tab.append("v%g: %s -> %s" % (sp, _num(old_xp), _num(new_xp)))
        RL["_table"] = tab
        print("RL. roll landings: %d landings = the real FallDamagePlayers; Fall XP at 100 HP rolling (0.4.13 -> 0.4.14): %s" % (len(RL["grid"]), "; ".join(tab)))
    # ---------------------------------------------------------------- GP
    GP = D.get("GP", {})
    check("error" not in GP, "GP: the gathering pace section ran: %s" % GP.get("error"))
    if "error" not in GP:
        check(GP["defaults"][0][:3] == [True, True, True] and not any(GP["defaults"][0][3:]) and GP["defaults"][1:6] == ["Mining,Foraging,Farming", 3.0, 10, 1.5, 20]
              and GP["defaults"][6] == "x3 to level 10, x1.5 from level 20 (Mining,Foraging,Farming)", "GP: defaults: %s" % GP["defaults"])
        check(GP["mult"] == [_mult(lv) for lv in range(26)], "GP: mult(level 0-25) = 3 to level 10, a straight line to 1.5 at 20, 1.5 after: %s"
              % ", ".join("%d:%s" % (i, _num(m)) for i, m in enumerate(GP["mult"])))
        ab = []
        for slot, lv, got_lv, a20, vals, a0, anull in GP["apply"]:
            m = _mult(lv) if slot in (MINING, FORAGING, FARMING) else 1.0
            lo, hi = _pay_range(20.0 * m)
            vlo, vhi = _pay_range(7.0 * m)
            if got_lv != lv or not (lo <= a20 <= hi) or (lo == hi and a20 != lo) or any(v < vlo or v > vhi for v in vals) or a0 != 0 or anull != 5:
                ab.append([slot, lv, got_lv, a20, vals, a0, anull])
        check(len(GP["apply"]) == 16 * 26 and not ab, "GP: GatherPace.apply on every slot at levels 0-25: Mining / Foraging / Farming x mult (20 XP -> 60, 57, 54 ... 30 "
              "exactly), every other slot unchanged; 0 stays 0, no player unchanged: %s" % ab[:3])
        c13 = GP["chance13"]
        check(c13["values"] == [2, 3] and abs(c13["mean"] - 2.55) < 0.03, "GP: 1 XP at Mining 13 (x2.55) -> 2 or 3, mean %.3f" % c13["mean"])
        sbad = []
        for lv in range(26):
            row = GP["statsLine"][str(lv)]
            if lv <= 10:
                w = "Gathering XP x3 up to level 10, then easing to x1.5 by level 20"
            elif lv < 20:
                w = "Gathering XP x%s now - easing to x1.5 by level 20" % _num(_mult(lv))
            else:
                w = "Gathering XP x1.5 (gathering pace)"
            if row != [w, w, w, None, None]:
                sbad.append((lv, row, w))
        check(not sbad, "GP: the Stats line at every level 0-25 (Acrobatics / Archery none): %s" % sbad[:3])
        check(GP["read"][0] == [True, False, True, False] and GP["read"][1:9] == ["Mining,Farming", 0.1, 100, 100.0, 0, "x0.1 to level 100, x100 from level 0 (Mining,Farming)", 0.1, 100.0],
              "GP: read(): 'Mining, cooking ,FARMING,mining' = Mining + Farming once (cooking warned + skipped), early -2 -> 0.1 (fix F4), until 150 -> 100, "
              "late 1000 -> 100, from -4 -> 0: %s" % GP["read"])
        fl = GP.get("floor", [])
        check(len(fl) == 8 and fl[:4] == [0.1, 0.1, 0.1, "x0.1 to level 10, x0.1 from level 20 (Mining,Foraging,Farming)"] and fl[4] == 1 and fl[5] == 1
              and fl[6] == [0, 1] and abs(fl[7] - 0.1) < 0.012,
              "GP FIX F4: gather.boost.early / late = 0 in the file are kept at 0.1 (MIN_MULT): 10 Mining XP at level 0 / 25 still pays 1 (was 0 - a skill "
              "stuck for good), 1 XP pays 0 or 1, mean %.3f: %s" % (fl[7] if len(fl) == 8 else -1, fl))
        check(GP["read_empty"] == [[False, False, False, False], "", "off (no skill listed)", 10] and GP["crossed"] == [3.0, 3.0, 3.0, 3.0, 1.5, 1.5]
              and GP["ones"] == [7, True], "GP: an empty list = off (XP unchanged); until 20 / from 10 = early through 20 then late (no division by zero); "
              "x1 / x1 = no change, no Stats line: %s %s %s" % (GP["read_empty"], GP["crossed"], GP["ones"]))
        check(GP["check"] == [True, "Only Mining, Foraging and Farming have a gathering pace (Cooking is not one).", True, True,
                              "Only Mining, Foraging and Farming have a gathering pace (Archery is not one)."] and GP["slotOf"] == [0, 1, 2, -1, -1, -2, -2],
              "GP: the Server Setup check refuses non-gathering skills: %s %s" % (GP["check"], GP["slotOf"]))
        gg = GP["gain"]
        check(gg["mining0"] == 30 and gg["grant0"] == 10 and gg["acro0"] == 10 and gg["farming25"] == 15 and gg["foraging15"] == 9 and gg["mining0_wisdom"] == [45] * 5,
              "GP: SkillXp.gain (blocks / F-harvests / sickles) 10 Mining XP at level 0 = 30; a grant (gain3, bonus off) = 10; Acrobatics 10; Farming 25 x1.5 = 15; "
              "Foraging 15 x2.25: 4 -> 9; with a +50%% tree Wisdom the pace comes first: 10 -> 30 -> 45: %s" % gg)
        def tx(lst):
            out_ = []
            for c_ in lst:
                try:
                    j_ = json.loads(c_)
                    out_ += [str(v_) for v_ in j_.values()] if isinstance(j_, dict) else [str(j_)]
                except Exception:
                    out_.append(c_)
            return out_
        pg = dict(GP["page"])
        for k_ in ("pace", "bonus", "skilltree"):
            pg[k_] = tx(pg[k_])
        GP["page15"], GP["page30"], GP["page_acro"], GP["page_farming"] = tx(GP["page15"]), tx(GP["page30"]), tx(GP["page_acro"]), tx(GP["page_farming"])
        check(pg["err"] is None and pg["pace"] == ["Gathering XP x3 up to level 10, then easing to x1.5 by level 20"] and len(pg["bonus"]) == 1
              and pg["bonus"][0].startswith("Bonuses (trees + tools): +10% double drops, +50% XP") and not pg["skilltree"]
              and GP["page15"] == ["Gathering XP x2.25 now - easing to x1.5 by level 20"] and GP["page30"] == ["Gathering XP x1.5 (gathering pace)"],
              "GP: the Stats page (Mining 0 / 15 / 30): the pace line + 'Bonuses (trees + tools): ...' (was 'Skill tree: ...'): %s %s %s" % (pg, GP["page15"], GP["page30"]))
        tl = GP["treeLine"]
        check(tl[0].startswith("Bonuses (trees + tools): ") and (tl[1] == "None" or tl[1].startswith("Skill tree: ")) and tl[2],
              "GP: StatsPage.treeLine: summed skill:bonus = 'Bonuses (trees + tools): ...', the Acrobatics tree line keeps 'Skill tree:', no bonus = no line: %s" % tl)
        check(any("crouch as you land to roll: +50%" in c for c in GP["page_acro"]) and not any("Gathering XP" in c for c in GP["page_acro"])
              and any("or swing a sickle through them" in c for c in GP["page_farming"]),
              "GP: the how-to lines: Acrobatics '... crouch as you land to roll: +50%%', Farming '... or swing a sickle through them': %s %s" % (GP["page_acro"], GP["page_farming"]))
        print("GP. gathering pace: x3 to 10 -> x1.5 at 20 (%s); apply on 16 slots x 26 levels; Stats line + 'Bonuses (trees + tools)'"
              % ", ".join("%d:%s" % (i, _num(m)) for i, m in enumerate(GP["mult"]) if 9 <= i <= 21))
    # ---------------------------------------------------------------- SK
    SK = D.get("SK", {})
    check("error" not in SK, "SK: the sickle section ran: %s" % SK.get("error"))
    if "error" not in SK:
        ek = expected_keys(cmodel, SK["fams"])
        kb = dict((k, (SK["keys"].get(k), ek.get(k))) for k in set(SK["keys"]) | set(ek) if SK["keys"].get(k) != ek.get(k))
        check(SK["keys"] == ek and len(ek) >= 14 and SK["keys_cached"] and SK["n_blocks"] == len(cmodel["blocks"]) + 2,
              "SK: Sickle.keys() over the REAL BlockTypeAssetMap (%d blocks) + the REAL drop lists = the Python model of Assets.zip (%d produce keys: key, lowest XP, "
              "multi, family, drop ids); cached: %s" % (SK["n_blocks"], len(ek), dict(list(kb.items())[:3])))
        check(ek.get("Plant_Crop_Wheat_Item", [0])[0] == 4 and ek.get("Plant_Fruit_Berries_Red", [0, False])[1] and not ek.get("Plant_Crop_Wheat_Item", [0, True])[1]
              and ek.get("Plant_Fruit_Berries_Red", [0, 0, ""])[2] == "Plant_Crop_Berry_Block" and "Ingredient_Life_Essence" not in ek,
              "SK: wheat 4 XP (single), berries multi (a second berry 3%%), family Plant_Crop_Berry_Block; essence is no produce: %s %s"
              % (ek.get("Plant_Crop_Wheat_Item"), ek.get("Plant_Fruit_Berries_Red")))
        rb = []
        for bid, r in sorted(SK["rolls"].items()):
            b = [x for x in cmodel["blocks"] if x["id"] == bid][0]
            ds = all_drops_py(cmodel, b["harvest"].get("DropList")) if b["harvest"].get("DropList") else []
            ds = [x for x in ds if x] + ([b["harvest"]["ItemId"]] if b["harvest"].get("ItemId") else [])
            key = ds[0] if ds else None
            if r["empty"] or list(r["first"]) != [key] or r["segs"] != {"ok": r["n"]} or r["n"] != 300:
                rb.append([bid, r])
        check(len(SK["rolls"]) >= 30 and not rb, "SK: the REAL BlockHarvestUtils.getDrops (ItemModule.getRandomItemDrops) of %d ripe Farming crops x 300 harvests: every "
              "harvest starts with its produce and is exactly ONE segment with all its stacks: %s" % (len(SK["rolls"]), rb[:2]))
        sb, merges = [], 0
        for sw in SK["swings"]:
            ids = [i for c in sw["crops"] for i, q in c[1]]
            want = segments_py(ids, SK["keys"])
            got = [[g[0], [i for i, q in g[1]]] for g in sw["segs"]]
            if got != want:
                sb.append([sw["crops"], got, want])
            if len(got) != len(sw["crops"]):
                # the documented undercount: a berry crop dropping only berries followed by another berry crop merges
                merges += 1
                ok = len(got) == len(sw["crops"]) - sum(1 for a, b in zip(sw["crops"], sw["crops"][1:])
                                                        if all(i == "Plant_Fruit_Berries_Red" for i, q in a[1]) and b[1] and b[1][0][0] == "Plant_Fruit_Berries_Red"
                                                        and ek.get("Plant_Fruit_Berries_Red"))
                if not ok:
                    sb.append(["count", sw["crops"], got])
        check(len(SK["swings"]) == 400 and not sb, "SK: 400 random swings of 2-6 crops (+ a sap stack after some): segments = the Python model; one segment per crop "
              "except the documented berry case (%d swings: a bush that dropped only berries right before another bush): %s" % (merges, sb[:1]))
        se = SK["seg_edge"]
        B, W, E_, St = "Plant_Fruit_Berries_Red", "Plant_Crop_Wheat_Item", "Ingredient_Life_Essence", "Ingredient_Stick"
        check(se["empty"] == [] and se["foreign_only"] == [] and se["lead_foreign"] == [[W, [W, E_]]] and se["berry_merge"] == [[B, [B, B, St]]]
              and se["berry_two"] == [[B, [B, St]], [B, [B]]] and se["wheat_twice"] == [[W, [W]], [W, [W]]] and se["sap_between_berries"] == [[B, [B]], [B, [B]]]
              and SK["seg_null"] == [0, 0], "SK: segments edge cases (nothing, foreign only, a foreign lead, the berry merge, two bushes, two wheats, sap between "
              "berries, null lists): %s" % se)
        cs = SK["cases"]
        wx = 3 * SK["fams"]["Plant_Crop_Wheat_Block"][1]
        cx_ = 3 * SK["fams"]["Plant_Crop_Carrot_Block"][1]
        bx_ = 3 * SK["fams"]["Plant_Crop_Berry_Block"][1]
        ST = ["SickleTask"]
        check(cs["swing"] == {"xp": wx + cx_, "queued": ST, "pend_after": False},
              "SK: a sickle swing through a ripe wheat and a carrot: ONE SickleTask, each crop paid once (%d + %d Farming XP = the rule x3 at level 0): %s" % (wx, cx_, cs["swing"]))
        check(cs["cancel_first_stack"] == {"xp": bx_ + wx, "queued": ST} and cs["all_cancelled"] == {"xp": 0, "queued": ST},
              "SK: a cancelled pickup pays nothing (wheat's produce cancelled -> berry + the second wheat = %d; all cancelled = 0): %s %s"
              % (bx_ + wx, cs["cancel_first_stack"], cs["all_cancelled"]))
        check(cs["hoe"] == {"xp": 0, "queued": []} and cs["empty_hand"]["queued"] == [] and cs["creative"]["queued"] == [] and cs["off"]["queued"] == [],
              "SK: a hoe / an empty hand / creative / farming.sickle.enabled off: SickleSys queues nothing: %s" % [cs["hoe"], cs["empty_hand"], cs["creative"], cs["off"]])
        check(cs["busy"] == {"xp": 0, "queued": ST, "pend_after": False} and cs["offline"] == {"xp": 0, "queued": ST},
              "SK: profile:busy / an offline player: the task pays nothing (and clears the burst): %s %s" % (cs["busy"], cs["offline"]))
        check(cs["f_harvest"] == {"use": True, "queued": ["HarvestTask"], "pend": False, "sickle_xp": 0} and cs["after_window"] == {"xp": wx, "queued": ST},
              "SK: NO DOUBLE PAY with an F-harvest: HarvestSys records the use, its pickups (within 2 s) queue no SickleTask (HarvestTask pays it); after the window "
              "the same pickups count: %s %s" % (cs["f_harvest"], cs["after_window"]))
        fp = cs["f_pickup"]
        check(SK["loose"][1][0] != FARMING and fp["brk"] and fp["pend"] is False and fp["sickle_xp"] == 0 and fp["queued"] in ([], ["BreakTask"])
              and fp["brk_after"] == (fp["queued"] == []),
              "SK: NO DOUBLE PAY with an F pickup (%s, not a Farming block - its BreakTask pays its own rule): BreakSys records BreakBlockEvent(null item), the "
              "wheat pickups of that dispatch queue no SickleTask (0 Farming XP); BreakTask closes the context: %s" % (SK["loose"], fp))
        check(cs["after_250ms"] == {"xp": wx, "queued": ["BreakTask"] + ST} and cs["thread"] == {"same": False, "here": True} and cs["break_with_sickle"] == {"brk": False},
              "SK: the F-pickup context is this thread's and 250 ms: 300 ms later the pickups pay, another thread is never blocked; a break with the sickle in hand "
              "opens no context: %s %s %s" % (cs["after_250ms"], cs["thread"], cs["break_with_sickle"]))
        dbl = cs["double"]

        def agg(lst):
            a = {}
            for i, q in lst:
                a[i] = a.get(i, 0) + q
            return a
        check(dbl["xp"] == wx and agg(dbl["box"]) == agg(dbl["want"]) and "Ingredient_Tree_Sap" not in agg(dbl["box"]) and dbl["msg"] and not dbl["dd_failed"],
              "SK: the double drop (dd.farming 1.0): the crop's own stacks once more into a REAL CombinedItemContainer, not the sap of the same swing, 'Double drop!' "
              "line: box %s want %s msg %s" % (agg(dbl["box"]), agg(dbl["want"]), dbl["msg"][:1]))
        check(cs["items_copper"]["queued"] == [] and cs["items_iron"]["queued"] == ST, "SK: farming.sickle.items = Tool_Sickle_Iron: a copper sickle no longer counts")
        # ---- FIX ROUND F1: the place / swing / place loop is closed
        loopers = ["Plant_Crop_Health%d" % i for i in (1, 2, 3)] + ["Plant_Crop_Mana%d" % i for i in (1, 2, 3)] + \
                  ["Plant_Crop_Stamina%d" % i for i in (1, 2, 3)] + ["Plant_Cactus_Flower"]
        pre = {}
        for iid in loopers:
            bl = [b for b in cmodel["blocks"] if b["id"] == iid]
            h_ = bl[0]["harvest"] if bl else None
            ds_ = ([x for x in all_drops_py(cmodel, h_.get("DropList")) if x] if h_ and h_.get("DropList") else []) + ([h_["ItemId"]] if h_ and h_.get("ItemId") else [])
            rule_ = SK["fams"].get(bl[0]["family"]) if bl else None
            pre[iid] = bool(bl) and bl[0]["states"] is None and iid in ds_ and bool(rule_) and rule_[0] == FARMING and rule_[1] > 0
        check(all(pre.values()), "SK FIX F1: the loop's precondition is real in Assets.zip - every Health / Mana / Stamina plant and the cactus flower is a "
              "stateless block whose Harvest hands back its OWN item and whose rule pays Farming XP: %s" % [k for k, v in pre.items() if not v])
        gone = ["Plant_Crop_Health%d" % i for i in (1, 2, 3)] + ["Plant_Crop_Mana%d" % i for i in (1, 2, 3)] + ["Plant_Crop_Stamina%d" % i for i in (1, 2, 3)] + \
               ["Plant_Cactus_Flower", "Ingredient_Fibre", "Ingredient_Charcoal", "Ingredient_Powder_Boom"]
        want16 = ["Plant_Crop_%s_Item" % c for c in ("Aubergine", "Carrot", "Cauliflower", "Chilli", "Corn", "Cotton", "Lettuce", "Onion", "Potato", "Pumpkin",
                                                      "Rice", "Tomato", "Turnip", "Wheat")] + ["Plant_Fruit_Apple", "Plant_Fruit_Berries_Red"]
        src_bad, self_bad = [], []
        for b in cmodel["blocks"]:
            h_ = b.get("harvest")
            rule_ = SK["fams"].get(b["family"])
            if not h_ or not rule_ or rule_[0] != FARMING or rule_[1] <= 0:
                continue
            ds_ = ([x for x in all_drops_py(cmodel, h_.get("DropList")) if x] if h_.get("DropList") else []) + ([h_["ItemId"]] if h_.get("ItemId") else [])
            if ds_ and ds_[0] in SK["keys"]:
                if not is_stage_final(b):
                    src_bad.append(b["id"])
                if b["item"] in SK["keys"][ds_[0]][3]:
                    self_bad.append([b["id"], ds_[0]])
        check(not [k for k in gone if k in SK["keys"]] and sorted(SK["keys"]) == sorted(want16) and not src_bad and not self_bad,
              "SK FIX F1: Sickle.keys() = the 16 StageFinal produce keys only (14 crops + apples + berries); none of the 13 stateless / no-final-stage "
              "keys (Health / Mana / Stamina plants, cactus flower, fibre, charcoal, boom powder); every key's blocks are StageFinal and none can drop its "
              "own block item: extra %s, missing %s, non-StageFinal sources %s, self drops %s"
              % (sorted(set(SK["keys"]) - set(want16)), sorted(set(want16) - set(SK["keys"])), src_bad[:3], self_bad[:3]))
        lp = cs["loop"]
        lbad = dict((k, v) for k, v in lp.items() if k in ("Plant_Crop_Health3", "Plant_Crop_Mana1", "Plant_Crop_Stamina2", "Plant_Cactus_Flower",
                                                          "*Plant_Crop_Wild_Grass_Block_State_Definitions_Stage3", "Plant_Crop_Mushroom_Boomshroom_Small")
                    and (v["xp"] != 0 or v["box"] != [] or v["queued"] not in ([], ST)))
        check(len(lp) == 9 and not lbad and "Plant_Crop_Health3" in lp["Plant_Crop_Health3"]["ids"] and "Plant_Cactus_Flower" in lp["Plant_Cactus_Flower"]["ids"]
              and lp["Plant_Crop_Health3"]["queued"] == ST and lp["health3_x10"] == {"xp": 0, "box": []}
              and lp["health3_ignorePlaced_off"] == {"xp": 0, "queued": ST, "box": []},
              "SK FIX F1: a sickle swing at a placed Health3 (its REAL drops = its own item) / Mana1 / Stamina2 / cactus flower / wild grass / a "
              "boomshroom pays 0 Farming XP and doubles nothing (dd.farming 1.0 on; was +60 XP a swing and a copied plant); 10 swings 0; ignorePlaced "
              "off 0: %s %s %s" % (lbad, lp.get("health3_x10"), lp.get("health3_ignorePlaced_off")))
        check(lp["mixed"]["xp"] == wx and lp["mixed"]["queued"] == ST and agg(lp["mixed"]["box"]) == agg(lp["mixed"]["want"])
              and "Plant_Crop_Health3" not in agg(lp["mixed"]["box"]),
              "SK FIX F1: one swing through a ripe wheat + a placed Health3 pays the wheat only (%d) and doubles only the wheat's stacks: %s" % (wx, lp["mixed"]))
        check(SK["isSickle"] == [True, True, False, False, False, False] and SK["check"] == [True, "Write at least one item id start, like Tool_Sickle_.",
              ["Tool_Sickle_", "Tool_Scythe_"]], "SK: isSickle / checkItems / parse: %s %s" % (SK["isSickle"], SK["check"]))
        check(SK["retain"] == [False, False, False, True, True, True], "SK: Acro.retainOnline drops the contexts / bursts of players who left: %s" % SK["retain"])
        check(SK["err"] == [] and SK["failed"] == [False, True] and SK["keys_after_load"], "SK: no world task threw, never 'failed', the info line once, a reload drops the "
              "crop map: %s %s" % (SK["err"][:3], SK["failed"]))
        print("SK. sickle swings: %d produce keys = the Assets.zip model; %d crops x 300 real harvests = one segment each; 400 swings (%d berry merges); "
              "no double pay with F-harvest / F pickup; double drop = the crop's own stacks" % (len(ek), len(SK["rolls"]), merges))
    # ---------------------------------------------------------------- DM
    DM = D.get("DM", {})
    check("error" not in DM, "DM: the DocMig section ran: %s" % DM.get("error"))
    if "error" not in DM:
        o_, n_ = MREG_DOC_OLD, MREG_DOC_NEW
        check(DM["consts"] == [o_, n_, "SkyySkills 0.4.14"], "DM: DocMig.OLD / NEW / WHO: %s" % DM["consts"])
        c = DM["cases"]
        want = {"lf": ["a=1\n" + n_ + "\nmana.regen.inCombat=50\n", 1], "crlf": ["a=1\r\n" + n_ + "\r\nmana.regen.inCombat=50\r\n", 1], "hand": None,
                "indented": None, "continued": None, "two": [n_ + "\n" + n_ + "\n", 2], "no_eol": ["a=1\n" + n_, 1], "none": None, "bang": None}
        cb = dict((k, (c.get(k), v)) for k, v in want.items() if c.get(k) != v)
        check(not cb, "DM: docUpdate: the exact line only (LF / CRLF kept, no final newline kept, two lines), never a hand-edited / indented / '!' line or a "
              "continued value's tail: %s" % cb)
        r = DM["run"]
        src = "x=1\r\n# head\r\n" + o_ + "\r\nmana.regen.inCombat=50\r\n"
        check(r["r1"].startswith("xp.properties: the outdated Mana regen comment") and r["a1"] == src.replace(o_, n_) and any(h[1] for h in r["hist"])
              and r["r2"] == "" and r["same2"] and DM["missing"] == "" and DM["null"] == "",
              "DM: DocMig.run: the comment fixed (CRLF kept), the old bytes in config-history first (%s); again = nothing; no file / no path = nothing: %r"
              % (r["hist"], r["r1"][:100]))
        print("DM. the stale Mana regen comment: exact-line rewrite (LF / CRLF), once, History copy first")
    # ---------------------------------------------------------------- C14
    C14 = D.get("C14", {})
    check("error" not in C14, "C14: the loader section ran: %s" % C14.get("error"))
    if "error" not in C14:
        dv = [True, 0.05, 5, 0.05, 3.5, 0.05, 0.1, 0.5, "Mining,Foraging,Farming", 3.0, 10, 1.5, 20, True, "Tool_Sickle_"]
        for nm in ("lf", "crlf"):
            x = C14[nm]
            check(x["exact"] and x["again_same"] and x["comment_kept"] and x["values"] == dv,
                  "C14 %s: a 0.4.13 file = itself + a blank line + the 0.4.14 block, once; the loader leaves the comment to DocMig; values = the defaults: %s" % (nm, x))
        h = C14["hand"]
        others = [k for k in N14_KEYS if k not in ("combat.gap.max", "gather.boost.early")]
        check(h["prefix_kept"] and h["tail_keys"] == others and h["tail_comments"] == sum(1 for ln in D["n14_block"].split("\n") if ln.startswith("#"))
              and h["MAX"] == 5.0 and h["EARLY"] == 2.0 and h["max_lines"] == 1 and h["early_lines"] == 1 and h["again_same"],
              "C14: an admin's combat.gap.max=5 / gather.boost.early=2 are kept (never rewritten, never duplicated): only the other 13 key lines appended, once: %s" % h)
        check(C14["full_same"], "C14: a file with every 0.4.14 key gets nothing")
        cl = C14["clamp"]["values"]
        check(cl == [False, 0.0, 100, 10.0, 1.0, 0.0, 1.0, 10.0, "Mining,Farming", 0.1, 100, 100.0, 0, False, "Tool_Sickle_", [True, False, True, False]],
              "C14: clamps through the loader (gather.boost.early -2 -> 0.1, fix F4; + an empty sickle list = the default): %s" % cl)
        check(C14["fresh_values"] == dv and C14["fresh_tail"], "C14: a minimal file ends with the 0.4.14 block once, values the defaults: %s" % C14["fresh_values"])
        print("C14. the 0.4.14 block reaches existing files once (LF / CRLF, only missing keys, hand values kept); clamps")
    # ---------------------------------------------------------------- X 0.4.14: bytecode order
    cl_ = bc["calls"]

    def first(d, k):
        return d[k][0] if d.get(k) else -1
    ks_ = cl_.get("kill_sys", {})
    check("methods" not in ks_ and len(ks_.get("MobXp.kill(", [])) == 1 and len(ks_.get("SkillCfg.combatXp(", [])) == 1 and ks_["SkillCfg.combatXp("][0] < ks_["MobXp.kill("][0]
          and ks_.get("SkillXp.gain(") == [] and ks_.get("PartyXp.share") == [] and ks_.get("SkillCfg.classXp(") == [],
          "X 0.4.14: KillSys.onComponentAdded = combatXp -> MobXp.kill (no direct gain / share / classXp left): %s" % ks_)
    mk_ = cl_.get("mob_kill", {})
    check("methods" not in mk_ and all(len(mk_.get(k, [])) == 1 for k in ("MobXp.levelOf(", "MobXp.pay(", "SkillCfg.classXp(", "SkillXp.gain(", "PartyXp.share2("))
          and first(mk_, "MobXp.levelOf(") < first(mk_, "MobXp.pay(") < first(mk_, "SkillXp.gain(") < first(mk_, "PartyXp.share2(")
          and first(mk_, "SkillCfg.classXp(") < first(mk_, "SkillXp.gain("),
          "X 0.4.14: MobXp.kill = levelOf -> pay (or classXp) -> SkillXp.gain -> PartyXp.share2: %s" % mk_)
    g4 = cl_.get("gain4", {})
    check("methods" not in g4 and len(g4.get("GatherPace.apply(", [])) == 1 and len(g4.get("SkillBonus.boost(", [])) == 1
          and first(g4, "ClassCurve.tick(") < first(g4, "GatherPace.apply(") < first(g4, "SkillBonus.boost(") < first(g4, "SkillStore.addK("),
          "X 0.4.14: SkillXp.gain4: ClassCurve.tick -> GatherPace.apply -> SkillBonus.boost (the pace before Wisdom) -> addK: %s" % g4)
    fo = cl_.get("fell_one", {})
    check("methods" not in fo and len(fo.get("GatherPace.apply(", [])) == 1 and first(fo, "GatherPace.apply(") < first(fo, "SkillBonus.boost(") < first(fo, "SkillXp.gain3("),
          "X 0.4.14: FellCredit.one (felled logs): GatherPace.apply -> SkillBonus.boost -> gain3: %s" % fo)
    bs = cl_.get("break_sys", {})
    bt_ = cl_.get("break_task", {})
    hs = cl_.get("harvest_sys", {})
    check("methods" not in bs and len(bs.get("Sickle.breakOpen(", [])) == 1 and first(bs, "Sickle.breakOpen(") < first(bs, "World.execute")
          and "methods" not in bt_ and len(bt_.get("Sickle.breakDone(", [])) == 1 and first(bt_, "Sickle.breakDone(") < first(bt_, "isCancelled")
          and "methods" not in hs and len(hs.get("Sickle.useOpen(", [])) == 1 and first(hs, "getHarvest") < first(hs, "Sickle.useOpen(") < first(hs, "SkillCfg.resolve("),
          "X 0.4.14: BreakSys opens the F-pickup context before queueing BreakTask, BreakTask closes it first thing, HarvestSys records the use after the harvest "
          "check and before the rule: %s %s %s" % (bs, bt_, hs))
    ss = cl_.get("sickle_sys", {})
    order_ = ["Sickle.ON", "Sickle.inBreak(", "Sickle.inUse(", "SkillXp.creative(", "InventoryComponent.getItemInHand(", "Sickle.isSickle(", "Sickle.add("]
    check("methods" not in ss and all(len(ss.get(k, [])) == 1 for k in order_) and [first(ss, k) for k in order_] == sorted(first(ss, k) for k in order_),
          "X 0.4.14: SickleSys.handle = ON -> F-pickup context -> F-harvest window -> creative -> the hand item is a sickle -> Sickle.add: %s" % ss)
    rt = cl_.get("roll_tick", {})
    check("methods" not in rt and all(len(rt.get(k, [])) >= 1 for k in ("AcroCfg.ENABLED", "AcroCfg.ROLL", "getMovementUpdateQueue", "getCurrentFallDistance", "RollSys.land("))
          and first(rt, "AcroCfg.ROLL") < first(rt, "getMovementUpdateQueue") < first(rt, "RollSys.land("),
          "X 0.4.14: RollSys.tick: the switches, then the queue, then land: %s" % rt)
    rf = cl_.get("roll_fd", {})
    check(len(rt.get("RollSys.fallDamageOn(", [])) == 1 and first(rt, "getCurrentFallDistance") < first(rt, "RollSys.fallDamageOn(") < first(rt, "RollSys.land(")
          and "methods" not in rf and all(len(rf.get(k, [])) == 1 for k in ("Store.getExternalData", "EntityStore.getWorld", "World.getWorldConfig", "WorldConfig.isFallDamageEnabled"))
          and first(rf, "EntityStore.getWorld") < first(rf, "World.getWorldConfig") < first(rf, "WorldConfig.isFallDamageEnabled"),
          "X FIX F2: RollSys.tick asks fallDamageOn (World.getWorldConfig().isFallDamageEnabled(), the engine's switch) after the fall distance and before "
          "land: %s %s" % (rt, rf))
    ph = cl_.get("party_how", {})
    check("methods" not in ph and all(len(ph.get(k, [])) == 1 for k in ("MobXp.ON", '"mob:fn:level"', "of the kill XP at their own class skill level",
                                                                       "of your kill XP (in their own class skill)"))
          and first(ph, "MobXp.ON") < first(ph, "of the kill XP at their own class skill level") < first(ph, "of your kill XP (in their own class skill)"),
          "X FIX F3: PartyXp.howText: with mob levels on 'of the kill XP at their own class skill level', else the 0.4.13 text: %s" % ph)
    ps = cl_.get("pl_setup14", {})
    check("methods" not in ps and len(ps.get("DocMig.run(", [])) == 1 and first(ps, "HealMig.run(") < first(ps, "DocMig.run(") < first(ps, "SkillCfg.load(")
          and len(ps.get("Class com.skyy.skills.SickleSys", [])) == 1 and len(ps.get("Class com.skyy.skills.RollSys", [])) == 1,
          "X 0.4.14: setup(): HealMig.run -> DocMig.run -> SkillCfg.load; SickleSys and RollSys registered: %s" % ps)
    sl = cl_.get("stats_lines", {})
    check("methods" not in sl and len(sl.get("GatherPace.statsLine(", [])) == 1, "X 0.4.14: StatsPage.lines calls GatherPace.statsLine: %s" % sl)
    print("X. 0.4.14 bytecode: KillSys -> MobXp.kill; gain4 / FellCredit pace before Wisdom; Sickle contexts in BreakSys / BreakTask / HarvestSys; SickleSys order; "
          "RollSys.tick; setup DocMig between HealMig and SkillCfg.load")
    lp_ = ((SK.get("cases") or {}).get("loop") or {}) if "error" not in SK else {}
    h3_ = lp_.get("Plant_Crop_Health3", {})
    fo_ = RL.get("fd_off", {}) if "error" not in RL else {}
    print("FIX. F1 sickle keys %d (StageFinal only); a placed Health3 swing (drops %s) pays %s XP + box %s, 10 swings %s, ignorePlaced off %s, wheat + Health3 "
          "pays %s; F2 fall damage off: engine Damage / fall distance %s, roll note %s (on again %s); F3 how-to %r; F4 early / late 0 -> %s, 10 XP at "
          "level 0 / 25 -> %s / %s" % (len(SK.get("keys", {})), h3_.get("ids"), h3_.get("xp"), h3_.get("box"), (lp_.get("health3_x10") or {}).get("xp"),
                                        (lp_.get("health3_ignorePlaced_off") or {}).get("xp"), (lp_.get("mixed") or {}).get("xp"), fo_.get("engine"),
                                        fo_.get("note"), fo_.get("on_note"), (KX.get("howText") or [None])[0], (GP.get("floor") or [None, None])[:2],
                                        (GP.get("floor") or [0] * 6)[4], (GP.get("floor") or [0] * 6)[5]))


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
