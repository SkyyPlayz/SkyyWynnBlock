"""SkyySkills 0.4.35 - harness for REBIRTH R1 (run XP past max, level caps from rebirth:fn:cap, skill:fn:run) + half Farming XP one tier
above the tool (gear:fn:farmTier) - tools/skills_0_4_35_patch.py.
Build first: python tools/skills_0_4_35_patch.py && python SkyySkills/build_skyyskills_0.4.35.py

    python SkyySkills/test_skyyskills_0.4.35.py --dir <empty folder inside tools/dev/scratch/> [--keep]
    (SKYY_OLD_JAR_DIR=<folder with SkyySkills-0.4.31.jar> when tools/tidy_local.py has archived it: the 0.4.32 exec / live phases use it)

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.34 -> 0.4.35: exactly the planned members differ; SkillCap, FarmTier, SkillRunFn added
  RB  rebirth  EXECUTED (the real xp.properties tables from SkillCfg.load):
               SAME AS 0.4.34 without SkyyRebirth: every slot, every level boundary (L-1 / L / L+1 XP) and 2,000 random totals:
               levelCap / intoCap / needCap / progressCap at the table cap = levelOf / intoLevel / needFor / progress, SkillCap = the
               tables; XP PAST MAX: addK stores every point past the max level (saved + read back), skill:fn:run (UUID, pkey, offline pkey
               file NOT cached, class, combat, exploration, bad arguments); CAPS VIA THE BRIDGE: a stand-in rebirth:fn:cap (+10 levels):
               asked once per profile per TTL with { pkey, saved name, Integer base } for every slot but Exploration, cached, asked again
               on a new function / TTL 0; levels above the table (flat last step), need / into / progress, SkillStore.level,
               skill:<uuid>, skill:fn:level, skill:fn:run, addK level-up detection across the old max, owesK + payOwedK pay each new
               level once through the paid marker (stand-in coins:fn:add), the XP chat line + party line progress; odd answers (below
               base, not a number, throws, > +1000) = base / clamped; removing the function = the tables at once; static: gain4 clamps
               the Overall Level call, the /skills rows + Stats page use the capped values;
               HALF FARMING XP: FarmTier.half / apply for every gear:fn:farmTier answer (-1 / 0 / 1 / 2 / odd / throws / none), the
               arguments it sends, breakXp on stand-in BreakBlockEvents (block id, held id, empty hand), Sickle.award END TO END with a
               stand-in player + pickup events (half the Farming XP stored one tier up, full XP without SkyyGear), SickleSys remembers
               the sickle (static), Sickle.retain prunes HELD, BreakTask.run calls FarmTier.breakXp for Farming only (static);
               FIX ROUND: payOwedK(k) pays at profile k's cap while another profile is active (both directions); skill:fn:run
               refuses a String that is not a profile key (paths); a null rebirth:fn:cap answer is kept RETRY ms (not TTL) and then
               re-asked; farming.tierUpXpFactor (FarmTier.scale, Sickle.read clamps, x1 = SkyyGear not asked, the fresh default file)
  R   route    test_skyyskills_0.4.34.py's route phase on the 0.4.35 jar (the 0.4.34 chat / feed texts = 0.4.33's word for word)
  X   exec     test_skyyskills_0.4.32.py's exec phase on the 0.4.35 jar (every 0.4.32 lag-fix path still holds)
  D   live     test_skyyskills_0.4.32.py's live phase on the 0.4.35 jar: START TWICE on a scratch COPY of the live Skyy_SkyySkills; +
               every live player file through readFile: the 0.4.35 levels / paid markers / skill:fn:run = the tables with no SkyyRebirth
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, random, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.4.35"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.34.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rebirth12", "sk")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")
os.environ.setdefault("SKYYROUTE_SESSION", os.path.join(SCRATCH, "routesession"))   # the 0.4.34 route phase's session file stays in scratch

EXPECT = {
    "SkillDefs": ["+f CAP_EXTRA_MAX", "+m capMax", "+m cumAt", "+m intoCap", "+m levelCap", "+m needCap", "+m progressCap", "+m rebirthResets",
                  "+m stepTop"],
    # fix round: payLocked / payGuarded take the profile key k (new signatures = - old + new), payOwedK passes it
    "SkillStore": ["+m payGuarded", "+m payLocked", "-m payGuarded", "-m payLocked", "~m addK", "~m level", "~m levelsOf", "~m owesK",
                   "~m payOwedK", "~m readFile"],
    "SkillMsg": ["~m line"],
    "PartyXp": ["~m text"],
    "SkillXp": ["~m gain4"],
    "SkillsPage": ["~m build"],
    "StatsPage": ["~m build"],
    "BreakTask": ["~m run"],
    "Sickle": ["+f HELD", "+f TIER_XP", "~<clinit>", "~m award", "~m read", "~m retain"],   # fix round: + TIER_XP (farming.tierUpXpFactor)
    "SickleSys": ["~m handle"],
    "SkyySkillsPlugin": ["~m setup", "~m shutdown"],
    # version texts only (inlined strings): the pack name "Skyy:0.4.35 SkyySkills", the xp.properties header, the config kit's export header
    "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"],
    "SkillCfg": ["~m load"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "CfgFile": ["~<clinit>"],   # fix round: the kit's default xp.properties text + farming.tierUpXpFactor=0.5 (fresh files only)
}
ADDED = ["SkillCap", "FarmTier", "SkillRunFn"]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T34 = tmod("test_skyyskills_0.4.34.py", "t0434")      # it loads test_skyyskills_0.4.32.py (+ SKYY_OLD_JAR_DIR for 0.4.31) itself
T32 = T34.T32


# ====================================================================================================== RB: rebirth R1 + half Farming XP
def run_rebirth(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JLong, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Defs, Cfg, Sto, Cap, Run, FT, SKL, SM, PX, Ovl = (P("SkillDefs"), P("SkillCfg"), P("SkillStore"), P("SkillCap"), P("SkillRunFn"),
                                                       P("FarmTier"), P("Sickle"), P("SkillMsg"), P("PartyXp"), P("Overall"))
    UUID, Long, Integer, Bool, Str = (JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.lang.Integer"),
                                      JClass("java.lang.Boolean"), JClass("java.lang.String"))
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    base = os.path.join(scratch, "rb")
    pd = os.path.join(base, "players")
    os.makedirs(pd)
    Cfg.FILE = T32.path(os.path.join(base, "xp.properties"))
    K.notes.append("RB load: %s" % str(Cfg.load())[:200])
    Sto.DIR = T32.path(pd)
    bridge = Sto.bridge()
    for k_ in ("rebirth:fn:cap", "gear:fn:farmTier", "coins:fn:add"):
        bridge.remove(k_)

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)

    N = int(Defs.N)
    MINING, FARMING, EXPL, ACRO = int(Defs.MINING), int(Defs.FARMING), int(Defs.EXPLORATION), int(Defs.ACROBATICS)
    NAMES = [str(x) for x in Defs.NAMES]

    def cum(s):
        return [int(x) for x in Defs.cumOf(s)]

    # ---- 1. SAME AS 0.4.34 without SkyyRebirth (every slot, every boundary, random totals)
    rnd = random.Random(435)
    bad, n_eq = [], 0
    for s in range(N):
        c = cum(s)
        mx = int(Defs.maxOf(s))
        tots = set([0, 1, c[-1] * 3 + 17])
        for L in range(len(c)):
            tots.update([max(0, c[L] - 1), c[L], c[L] + 1])
        for _ in range(120):
            tots.add(rnd.randrange(0, c[-1] * 2 + 2))
        for t in sorted(tots):
            got = (int(Defs.levelCap(s, t, mx)), int(Defs.intoCap(s, t, mx)), int(Defs.needCap(s, t, mx)), str(Defs.progressCap(s, t, mx)),
                   int(Cap.level("00000000-0000-4000-8000-00000000eeee", s, t)))
            want = (int(Defs.levelOf(s, t)), int(Defs.intoLevel(s, t)), int(Defs.needFor(s, t)), str(Defs.progress(s, t)), int(Defs.levelOf(s, t)))
            n_eq += 1
            if got != want:
                bad.append((s, t, got, want))
    K.check(not bad, "RB same as 0.4.34: %d (slot, total) pairs - capped maths at the table cap = the table maths, SkillCap = the tables: %s"
            % (n_eq, bad[:3]))
    K.check(int(Cap.ASKS.get()) == 0, "RB no SkyyRebirth: rebirth:fn:cap never asked")
    K.check([bool(Defs.rebirthResets(s)) for s in range(N)] == [s != EXPL for s in range(N)], "RB rebirthResets: every slot but Exploration")

    # ---- 2. XP PAST MAX is counted and stored
    u = UUID.fromString("00000000-0000-4000-8000-000000000435")
    k = str(u)
    cm = cum(MINING)
    mmax = int(Defs.maxOf(MINING))
    step = cm[-1] - cm[-2]
    d = Sto.dataK(k, u)
    past = cm[-1] + 5 * step
    r = Sto.addK(k, u, "Tester", MINING, past)
    K.check(int(d[MINING]) == past and int(r[1]) == mmax and int(r[2]) == past,
            "RB XP past max: addK keeps all %d XP (max level %d at %d XP), level stays %d" % (past, mmax, cm[-1], int(r[1])))
    Sto.addK(k, u, "Tester", MINING, 1000)
    K.check(int(d[MINING]) == past + 1000, "RB XP past max: a second gain past max adds on (%d)" % int(d[MINING]))
    Sto.saveNow(k)
    got = Sto.readFile(k, None)
    K.check(int(got[0][MINING]) == past + 1000, "RB XP past max: saved to players/<pkey>.properties and read back")
    Sto.wr(d, MINING, past)
    RF = Run()
    a = RF.apply(JArray(JClass("java.lang.Object"))([u, "mining"]))
    K.check(a is not None and [int(a[0]), int(a[1]), int(a[2]), int(a[3]), bool(a[4]), str(a[5])] == [mmax, mmax, past, cm[-1], True, "Mining"],
            "RB skill:fn:run (UUID, mining): level / cap / run XP / XP to the cap / resets / name = %s" % (None if a is None else list(a)))
    a2 = RF.apply(JArray(JClass("java.lang.Object"))([k, "Mining"]))
    K.check(a2 is not None and int(a2[2]) == past, "RB skill:fn:run (pkey String) = the loaded profile")
    ae = RF.apply(JArray(JClass("java.lang.Object"))([u, "exploration"]))
    K.check(ae is not None and bool(ae[4]) is False and str(ae[5]) == "Exploration", "RB skill:fn:run exploration: resets = false")
    K.check(RF.apply(JArray(JClass("java.lang.Object"))([u, "class"])) is None, "RB skill:fn:run class without a class = null")
    us = str(u)
    bridge.put("class:" + us, "Archer")
    ac = RF.apply(JArray(JClass("java.lang.Object"))([u, "class"]))
    K.check(ac is not None and str(ac[5]) == "Combat.Archer" and bool(ac[4]), "RB skill:fn:run class = the profile's class skill (%s)" % (None if ac is None else str(ac[5])))
    acb = RF.apply(JArray(JClass("java.lang.Object"))([u, "combat"]))
    K.check(acb is not None and str(acb[5]) == "Combat.Archer", "RB skill:fn:run combat = the class row")
    K.check(RF.apply(JArray(JClass("java.lang.Object"))([k, "class"])) is None, "RB skill:fn:run class with a pkey (no UUID) = null")
    for bad_arg, what in ((None, "null"), (u, "a bare UUID"), (JArray(JClass("java.lang.Object"))([u]), "one element"),
                          (JArray(JClass("java.lang.Object"))([u, "nope"]), "unknown skill"), (JArray(JClass("java.lang.Object"))([Integer(3), "mining"]), "not a key"),
                          (JArray(JClass("java.lang.Object"))(["../../players/" + k, "mining"]), "a path (fix round: never read outside players/)"),
                          (JArray(JClass("java.lang.Object"))(["..\\..\\x", "mining"]), "a Windows path"),
                          (JArray(JClass("java.lang.Object"))(["abc", "mining"]), "not a profile key"),
                          (JArray(JClass("java.lang.Object"))([k + "-px", "mining"]), "a bad -p suffix")):
        K.check(RF.apply(bad_arg) is None, "RB skill:fn:run %s = null" % what)
    ko = "00000000-0000-4000-8000-0000000004ff-p2"
    open(os.path.join(pd, ko + ".properties"), "w", encoding="latin-1").write("name=Off\nMining=%d\nFarming=77\n" % (past + 3))
    ao = RF.apply(JArray(JClass("java.lang.Object"))([ko, "mining"]))
    K.check(ao is not None and int(ao[2]) == past + 3 and int(ao[0]) == mmax and not Sto.DATA.containsKey(ko),
            "RB skill:fn:run offline pkey: read from its file, NOT kept in memory")
    K.check(bool(Run.validKey(k)) and bool(Run.validKey(ko)) and not Run.validKey("../" + k) and not Run.validKey(None),
            "RB SkillRunFn.validKey: <uuid> / <uuid>-p<n> only")

    # ---- 3. CAPS VIA THE BRIDGE (rebirth:fn:cap)
    calls = []
    S = {"add": 10, "mode": "ok"}

    def f_cap(o):
        calls.append((str(o[0]), str(o[1]), int(o[2])))
        if S["mode"] == "throw":
            raise RuntimeError("boom")
        if S["mode"] == "text":
            return "abc"
        if S["mode"] == "none":
            return None
        if "per" in S:
            return Integer(int(o[2]) + S["per"].get(str(o[0]), 0))
        return Integer(int(o[2]) + S["add"])
    FC = Fn(f_cap)
    bridge.put("rebirth:fn:cap", FC)
    Cap.CACHE.clear()
    a0 = int(Cap.ASKS.get())
    K.eq(int(Cap.cap(k, MINING)), mmax + 10, "RB cap: Mining = today's + 10")
    asked = sorted(c[1] for c in calls)
    K.check(int(Cap.ASKS.get()) - a0 == N - 1 and "Exploration" not in asked and asked == sorted(n for n in NAMES if n != "Exploration")
            and all(c[0] == k for c in calls) and all(c[2] == int(Defs.maxOf(NAMES.index(c[1]))) for c in calls),
            "RB cap: one fetch = one ask per slot but Exploration, with { pkey, saved name, Integer base }: %s" % calls[:3])
    K.eq(int(Cap.cap(k, EXPL)), int(Defs.maxOf(EXPL)), "RB cap: Exploration never rises")
    K.eq(int(Cap.cap(k, ACRO)), int(Defs.maxOf(ACRO)) + 10, "RB cap: Acrobatics rises")
    arch = int(Defs.indexOf("archery"))
    K.eq(int(Cap.cap(k, arch)), int(Defs.maxOf(arch)) + 10, "RB cap: a class skill rises")
    n_calls = len(calls)
    Cap.cap(k, MINING)
    Cap.level(k, FARMING, 5)
    K.check(len(calls) == n_calls, "RB cap: cached per profile (no new ask inside the TTL)")
    K.eq(int(Cap.level(k, MINING, past)), mmax + 5, "RB levels above the table: max + 5 at 5 last-steps past the max XP")
    K.eq(int(Cap.need(k, MINING, past)), step, "RB need above the table = the last table step")
    K.eq(int(Cap.into(k, MINING, past + 7)), 7, "RB into above the table")
    K.eq(str(Cap.progress(k, MINING, past + 7)), "%s/%s" % (str(Defs.fmt(7)), str(Defs.fmt(step))), "RB progress above the table")
    top = cm[-1] + 10 * step + 999999
    K.eq(int(Cap.level(k, MINING, top)), mmax + 10, "RB level stops at the new cap")
    K.eq(int(Cap.need(k, MINING, top)), 0, "RB need at the new cap = 0 (MAX)")
    K.eq(str(Cap.progress(k, MINING, top)), "MAX", "RB progress at the new cap = MAX")
    K.eq(int(Sto.level(u, MINING)), mmax + 5, "RB SkillStore.level = the capped level")
    Sto.publish(u)
    sk = str(bridge.get("skill:" + us))
    K.check(("Mining:%d" % (mmax + 5)) in sk, "RB skill:<uuid> publishes the capped level: %s" % sk[:80])
    LF = P("SkillFn")()
    K.eq(int(LF.apply(JArray(JClass("java.lang.Object"))([u, "mining"]))), mmax + 5, "RB skill:fn:level = the capped level")
    a3 = RF.apply(JArray(JClass("java.lang.Object"))([u, "mining"]))
    K.check(int(a3[0]) == mmax + 5 and int(a3[1]) == mmax + 10 and int(a3[3]) == cm[-1] + 10 * step,
            "RB skill:fn:run with the raised cap: level %d / cap %d / XP to the cap %d" % (int(a3[0]), int(a3[1]), int(a3[3])))
    # level-up detection across the old max
    Sto.wr(d, MINING, cm[-1] - 1)
    r = Sto.addK(k, u, "Tester", MINING, step + 2)
    K.check(int(r[0]) == mmax - 1 and int(r[1]) == mmax + 1, "RB addK: a level up across the old max (%d -> %d)" % (int(r[0]), int(r[1])))
    # coin rewards: each new level once, through the paid marker
    paid = []

    def f_coins(o):
        paid.append(int(o[1]))
        return Long(1000000)
    bridge.put("coins:fn:add", Fn(f_coins))
    Sto.wr(d, MINING, past)
    Sto.wr(d, N + MINING, mmax)
    K.check(bool(Sto.owesK(k, u, MINING)), "RB owesK: levels above the old max are owed")
    res = Sto.payOwedK(k, u, MINING)
    per = int(Cfg.COINS_PER_LEVEL)
    K.check(res is not None and int(d[N + MINING]) == mmax + 5 and paid == [per * L for L in range(mmax + 1, mmax + 6)],
            "RB payOwedK: levels %d..%d paid once each (%s), the marker at %d" % (mmax + 1, mmax + 5, paid, int(d[N + MINING])))
    K.check(not bool(Sto.owesK(k, u, MINING)) and Sto.payOwedK(k, u, MINING) is None and len(paid) == 5, "RB nothing paid twice")
    # fix round (critic): profile A (k) pays at ITS cap even while profile B (active, +10 more) is the player's profile at payout time
    kB = k + "-p2"
    S["per"] = {k: 0, kB: 20}
    bridge.put("profile:fn:key", Fn(lambda o: kB if str(o) == us else None))
    Cap.CACHE.clear()
    keep = (int(d[MINING]), int(d[N + MINING]))
    Sto.wr(d, MINING, cm[-1] + 15 * step)
    Sto.wr(d, N + MINING, mmax)
    del paid[:]
    owed_a = bool(Sto.owesK(k, u, MINING))
    res_a = Sto.payOwedK(k, u, MINING)
    K.check(str(Sto.pkey(u)) == kB and int(Cap.cap(kB, MINING)) == mmax + 20 and int(Cap.cap(k, MINING)) == mmax
            and not owed_a and res_a is None and paid == [] and int(d[N + MINING]) == mmax,
            "RB payOwedK(k): profile A at its OWN cap (%d) pays nothing while active profile B has cap %d (paid %s)" % (mmax, mmax + 20, paid))
    S["per"] = {k: 10, kB: 0}
    Cap.CACHE.clear()
    res_a = Sto.payOwedK(k, u, MINING)
    K.check(res_a is not None and paid == [per * L for L in range(mmax + 1, mmax + 11)] and int(d[N + MINING]) == mmax + 10,
            "RB payOwedK(k): profile A pays up to ITS cap (+10) while active profile B has none: %s" % paid)
    Sto.wr(d, MINING, keep[0])
    Sto.wr(d, N + MINING, keep[1])
    bridge.remove("profile:fn:key")
    S.pop("per")
    del paid[:]
    Cap.CACHE.clear()
    # the chat lines (progress at the raised cap)
    p = JArray(JLong)(N)
    p[MINING] = 10
    line = str(SM.line(u, p))
    K.eq(line, "+10 Mining XP (%s)" % str(Defs.progressCap(MINING, past, mmax + 10)), "RB SkillMsg.line: progress at the profile's cap")
    p2 = JArray(JLong)(N + 1)
    p2[MINING] = 4
    ptxt = str(PX.text(u, p2, "Skyy"))
    K.check(("(%s)" % str(Defs.progressCap(MINING, past, mmax + 10))) in ptxt, "RB PartyXp.text: progress at the profile's cap: %s" % ptxt)
    # odd answers
    for mode, add, want, what in (("ok", -5, mmax, "an answer below today's cap = today's"), ("text", 0, mmax, "not a number = today's"),
                                  ("ok", 5000, mmax + 1000, "a raise above +1000 is clamped"), ("throw", 0, mmax, "a throwing function = today's")):
        S["mode"], S["add"] = mode, add
        Cap.CACHE.clear()
        K.eq(int(Cap.cap(k, MINING)), want, "RB cap: " + what)
    K.check(bool(Cap.WARNED), "RB cap: the throwing function warned (once per JVM)")
    # fix round (critic): a null answer (SkyyRebirth still reading the file) is kept RETRY ms only, then asked again - never 5 s of 'no raise'
    S["mode"], S["add"] = "none", 10
    Cap.CACHE.clear()
    Cap.RETRY = 60000
    K.eq(int(Cap.cap(k, MINING)), mmax, "RB cap: a null answer = today's cap for now")
    e0 = Cap.CACHE.get(k)
    K.check(e0 is not None and int(e0[1][N]) == 1, "RB cap: a null answer marks the cache entry 'retry soon'")
    nn = len(calls)
    S["mode"] = "ok"
    Cap.cap(k, MINING)
    K.check(len(calls) == nn, "RB cap: inside RETRY the entry is used (no ask storm)")
    Cap.RETRY = 0
    K.eq(int(Cap.cap(k, MINING)), mmax + 10, "RB cap: after RETRY it is asked again and the real raise (+10) applies")
    K.check(int(Cap.CACHE.get(k)[1][N]) == 0 and Cap.TTL == 5000, "RB cap: a full answer is kept the normal TTL")
    nn = len(calls)
    Cap.cap(k, MINING)
    K.check(len(calls) == nn, "RB cap: a full answer is not re-asked inside the TTL (RETRY 0 does not apply)")
    Cap.RETRY = 250
    S["mode"], S["add"] = "ok", 10
    Cap.CACHE.clear()
    Cap.cap(k, MINING)
    n1 = len(calls)
    FC2 = Fn(f_cap)
    bridge.put("rebirth:fn:cap", FC2)
    Cap.cap(k, MINING)
    K.check(len(calls) == n1 + N - 1, "RB cap: a NEW function object is asked at once (not the old cache)")
    Cap.TTL = 0
    Cap.cap(k, MINING)
    K.check(len(calls) == n1 + 2 * (N - 1), "RB cap: TTL 0 = asked every time")
    Cap.TTL = 5000
    bridge.remove("rebirth:fn:cap")
    K.eq(int(Cap.cap(k, MINING)), mmax, "RB no rebirth:fn:cap any more = the tables at once")
    K.eq(int(Sto.level(u, MINING)), mmax, "RB SkillStore.level back at the table max")
    # static: the Overall clamp, the pages, the level-up line
    g = PW.calls(jar)
    gx = g.get("SkillXp.gain4", set())
    K.check("java.lang.Math.min" in gx and PKG + "Overall.levelUp" in gx and PKG + "SkillCap.need" in gx and PKG + "SkillCap.progress" in gx
            and PKG + "SkillDefs.needFor" not in gx and PKG + "SkillDefs.progress" not in gx,
            "RB static: gain4 = SkillCap.need / progress + Overall.levelUp with Math.min (table levels)")
    sp = g.get("StatsPage.build", set())
    K.check(all(PKG + "SkillCap." + m in sp for m in ("levelU", "intoU", "needU", "capU")) and PKG + "SkillDefs.maxOf" not in sp,
            "RB static: the Stats page shows the capped level, XP and 'level x of cap'")
    kp = g.get("SkillsPage.build", set())
    K.check(all(PKG + "SkillCap." + m in kp for m in ("levelU", "intoU", "needU")), "RB static: the /skills rows use the capped values")
    K.check(PKG + "SkillCap.level" in g.get("SkillStore.readFile", set()), "RB static: a file without a paid marker defaults to the capped level")

    # ---- 4. HALF FARMING XP one tier above the hoe / sickle (gear:fn:farmTier)
    K.check([int(FT.half(10, 0.1)), int(FT.half(11, 0.3)), int(FT.half(11, 0.7)), int(FT.half(1, 0.4)), int(FT.half(1, 0.6)), int(FT.half(0, 0.1)),
             int(FT.half(-3, 0.1))] == [5, 6, 5, 1, 0, 0, -3], "RB FarmTier.half: even / odd (the last point 50 %) / 1 / 0 / negative")
    K.eq(int(FT.apply(u, "Plant_Crop_Wheat_Block", "Tool_Hoe_Copper", 10)), 10, "RB FarmTier: no SkyyGear = full XP")
    K.check(int(FT.ASKED.get()) == 0, "RB FarmTier: no SkyyGear = nothing asked")
    G = {"ans": 0, "args": None, "throw": False}

    def f_farm(o):
        G["args"] = (o[0], None if o[1] is None else str(o[1]), None if o[2] is None else str(o[2]))
        if G["throw"]:
            raise RuntimeError("gear boom")
        return G["ans"]
    bridge.put("gear:fn:farmTier", Fn(f_farm))
    for ans, amt, want, what in ((Integer(0), 10, 10, "0 normal"), (Integer(-1), 10, 10, "-1 not gated"), (Integer(1), 10, 5, "1 one tier up = half"),
                                 (Integer(2), 10, 5, "2 (refused - halved if it ever breaks)"), (None, 10, 10, "null = full"),
                                 ("x", 10, 10, "not a number = full")):
        G["ans"] = ans
        K.eq(int(FT.apply(u, "Plant_Crop_Wheat_Block", "Tool_Hoe_Copper", amt)), want, "RB FarmTier: " + what)
    K.check(G["args"] is not None and str(G["args"][0]) == us and G["args"][1:] == ("Plant_Crop_Wheat_Block", "Tool_Hoe_Copper"),
            "RB FarmTier asks with { UUID, block id, held item id }: %s" % (G["args"],))
    G["ans"] = Integer(1)
    odd = [int(FT.apply(u, "b", "h", 11)) for _ in range(400)]
    K.check(set(odd) == {5, 6} and 120 < odd.count(6) < 280, "RB FarmTier: 11 XP one tier up pays 5 or 6 (6 about half the time: %d / 400)" % odd.count(6))
    G["throw"] = True
    K.eq(int(FT.apply(u, "b", "h", 10)), 10, "RB FarmTier: a throwing SkyyGear = full XP")
    K.check(bool(FT.WARNED), "RB FarmTier: the failure warned (once per JVM)")
    G["throw"] = False
    K.eq(int(FT.apply(u, None, "h", 10)), 10, "RB FarmTier: no block id = full XP, not asked")
    # fix round (critic: the 0.5 was hard-coded): farming.tierUpXpFactor (Sickle.TIER_XP), a Server Setup row
    K.check([int(FT.scale(10, 0.5, 0.1)), int(FT.scale(11, 0.5, 0.3)), int(FT.scale(11, 0.5, 0.7)), int(FT.scale(10, 0.25, 0.9)),
             int(FT.scale(10, 0.25, 0.1)), int(FT.scale(10, 0.0, 0.1)), int(FT.scale(10, 1.0, 0.1)), int(FT.scale(-3, 0.5, 0.1))]
            == [5, 6, 5, 2, 3, 0, 10, -3], "RB FarmTier.scale: x0.5 = half, x0.25 (2.5 -> 2 or 3), x0 = 0, x1 = all")
    K.eq(float(SKL.TIER_XP), 0.5, "RB farming.tierUpXpFactor: the default (no line in an old xp.properties) = 0.5")
    Props = JClass("java.util.Properties")
    for v_, want_ in (("0.3", 0.3), ("7", 1.0), ("-1", 0.0), ("abc", 0.5), (None, 0.5)):
        pp_ = Props()
        if v_ is not None:
            pp_.setProperty("farming.tierUpXpFactor", v_)
        SKL.read(pp_)
        K.eq(float(SKL.TIER_XP), want_, "RB Sickle.read farming.tierUpXpFactor=%s -> %s (clamped 0-1, bad = 0.5)" % (v_, want_))
    G["ans"] = Integer(1)
    SKL.TIER_XP = 0.25
    K.eq(int(FT.apply(u, "b", "h", 8)), 2, "RB FarmTier at x0.25: 8 XP one tier up = 2")
    SKL.TIER_XP = 1.0
    a_before = int(FT.ASKED.get())
    K.check(int(FT.apply(u, "b", "h", 8)) == 8 and int(FT.ASKED.get()) == a_before, "RB FarmTier at x1 (off): full XP, SkyyGear not asked")
    SKL.TIER_XP = 0.5
    deftxt = open(os.path.join(base, "xp.properties"), encoding="latin-1").read() if os.path.isfile(os.path.join(base, "xp.properties")) else str(Cfg.DEFAULTS)
    K.check("\nfarming.tierUpXpFactor=0.5\n" in deftxt, "RB a fresh xp.properties carries farming.tierUpXpFactor=0.5")
    # breakXp on stand-in events (Unsafe: the engine classes without their asset-backed constructors; the REAL getters run)
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def setf(obj, cls, name, val):
        c = cls
        while c is not None:
            for f in c.getDeclaredFields():
                if str(f.getName()) == name:
                    f.setAccessible(True)
                    if isinstance(val, int) and not isinstance(val, bool):
                        f.setInt(obj, val)
                    else:
                        f.set(obj, val)
                    return True
            c = c.getSuperclass()
        return False
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    BBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent")

    def stack(iid, q):
        st = U.allocateInstance(IS.class_)
        setf(st, IS.class_, "itemId", iid)
        setf(st, IS.class_, "quantity", q)
        return st
    try:
        bt = U.allocateInstance(BTY.class_)
        ok_bt = setf(bt, BTY.class_, "id", "Plant_Crop_Wheat_Block") and str(bt.getId()) == "Plant_Crop_Wheat_Block"
        ev = U.allocateInstance(BBE.class_)
        ok_ev = setf(ev, BBE.class_, "blockType", bt) and setf(ev, BBE.class_, "itemInHand", stack("Tool_Hoe_Crude", 1))
        K.check(ok_bt and ok_ev, "RB stand-in BreakBlockEvent built (blockType + itemInHand)")
        G["ans"], G["args"] = Integer(1), None
        K.eq(int(FT.breakXp(u, ev, 20)), 10, "RB FarmTier.breakXp: one tier up = half")
        K.check(G["args"] is not None and G["args"][1:] == ("Plant_Crop_Wheat_Block", "Tool_Hoe_Crude"), "RB breakXp sends the event's block id + held id: %s" % (G["args"],))
        setf(ev, BBE.class_, "itemInHand", None)
        G["args"] = None
        FT.breakXp(u, ev, 20)
        K.check(G["args"] is not None and G["args"][2] is None, "RB breakXp with an empty hand sends held = null")
        K.eq(int(FT.breakXp(u, None, 20)), 20, "RB breakXp without an event = the amount")
    except Exception as e:
        K.check(False, "RB breakXp stand-ins: %s" % e)
    # Sickle.award END TO END: a stand-in player + two pickup events (the real segments / gain / addK path), one tier up then no SkyyGear
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    IPE = JClass("com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent")
    try:
        Cfg.FEEDBACK = False                     # no chat on a stand-in player
        pr = U.allocateInstance(PR.class_)
        K.check(setf(pr, PR.class_, "uuid", u) and str(pr.getUuid()) == us, "RB stand-in PlayerRef")
        HM, AL, HS = JClass("java.util.HashMap"), JClass("java.util.ArrayList"), JClass("java.util.HashSet")
        keys = HM()
        own = HS()
        own.add("Plant_Crop_Wheat_Item")
        keys.put("Plant_Crop_Wheat_Item", JArray(JClass("java.lang.Object"))([Long(40), Bool.FALSE, "Plant_Crop_Wheat_Block", own]))
        SKL.KEYS = keys

        def pickup(iid, q):
            e = U.allocateInstance(IPE.class_)
            setf(e, IPE.class_, "itemStack", stack(iid, q))
            return e
        bridge.put("settings:fn:get", Fn(lambda o: Bool.FALSE))   # every chat switch off: a stand-in player cannot receive packets
        Sto.wr(Sto.dataK(k, u), FARMING, cum(FARMING)[min(30, len(cum(FARMING)) - 1)])   # a steady gathering pace (no level boundary)
        before = int(Sto.dataK(k, u)[FARMING])
        SKL.HELD.put(u, "Tool_Sickle_Crude")
        G["ans"], G["args"] = Integer(1), None
        evs = AL()
        evs.add(pickup("Plant_Crop_Wheat_Item", 2))
        n_paid = int(SKL.award(pr, evs, "default"))
        mid = int(Sto.dataK(k, u)[FARMING])
        K.check(n_paid == 1 and G["args"] is not None and G["args"][1:] == ("Plant_Crop_Wheat_Block", "Tool_Sickle_Crude"),
                "RB Sickle.award asks FarmTier with the crop family + the remembered sickle: %s" % (G["args"],))
        bridge.remove("gear:fn:farmTier")
        evs2 = AL()
        evs2.add(pickup("Plant_Crop_Wheat_Item", 2))
        SKL.award(pr, evs2, "default")
        after = int(Sto.dataK(k, u)[FARMING])
        gained_half, gained_full = mid - before, after - mid
        K.check(gained_full > 0 and abs(2 * gained_half - gained_full) <= 2,
                "RB Sickle.award: one tier up stores half the Farming XP (%d) of a normal swing (%d)" % (gained_half, gained_full))
    except Exception as e:
        K.check(False, "RB Sickle.award end to end: %s" % e)
    finally:
        Cfg.FEEDBACK = True
        bridge.remove("settings:fn:get")
    # HELD: remembered by SickleSys, pruned with the other sickle contexts; BreakTask: Farming only
    SKL.HELD.put(UUID.randomUUID(), "Tool_Sickle_Crude")
    SKL.retain(JClass("java.util.HashSet")())
    K.check(SKL.HELD.isEmpty(), "RB Sickle.retain prunes HELD (players who left)")
    K.check(PKG + "FarmTier.apply" in g.get("Sickle.award", set()), "RB static: Sickle.award -> FarmTier.apply")
    K.check(PKG + "FarmTier.breakXp" in g.get("BreakTask.run", set()), "RB static: BreakTask.run -> FarmTier.breakXp")
    K.check("java.util.concurrent.ConcurrentHashMap.put" in g.get("SickleSys.handle", set()), "RB static: SickleSys.handle remembers the sickle (HELD.put)")
    K.check(PKG + "FarmTier.apply" not in g.get("HarvestTask.run", set()) and PKG + "FarmTier.breakXp" not in g.get("HarvestTask.run", set()),
            "RB static: F-harvests by hand are never gated (HarvestTask untouched)")
    K.notes.append("RB caps asked %d times, FarmTier asked %d / halved %d" % (int(Cap.ASKS.get()), int(FT.ASKED.get()), int(FT.HALVED.get())))
    K.save()


def run_route(out, jar, scratch, home):
    return T34.run_route(out, jar, scratch, home)


def run_exec(out, jar, scratch, home):
    T32.SCRATCH = scratch
    return T32.run_exec(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    T32.run_live(os.path.join(scratch, "live32.json"), jar, scratch, home)
    import json
    from jpype import JClass, JArray
    K = HK.Child(out)
    prev = json.load(open(os.path.join(scratch, "live32.json")))
    K.ok += prev["ok"]
    K.fails += prev["fails"]
    K.notes += prev["notes"]
    # every live player file through 0.4.35 (no SkyyRebirth): levels, default paid markers and skill:fn:run = the tables
    L = T32.loader_for(jar)
    Jc = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Defs, Cap, Run = Jc("SkillCfg"), Jc("SkillStore"), Jc("SkillDefs"), Jc("SkillCap"), Jc("SkillRunFn")
    lc = os.path.join(os.path.dirname(home), "copy-new")
    Cfg.FILE = T32.path(os.path.join(lc, "xp.properties"))
    Cfg.load()
    Sto.DIR = T32.path(os.path.join(lc, "players"))
    n, bad = 0, []
    pdir = os.path.join(lc, "players")
    RF = Run()
    for fn in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
        if not fn.endswith(".properties"):
            continue
        kk = fn[:-11]
        got = Sto.readFile(kk, None)
        dd = got[0]
        for s in range(int(Defs.N)):
            t = int(dd[s])
            if int(Cap.level(kk, s, t)) != int(Defs.levelOf(s, t)):
                bad.append((kk, s))
        a = RF.apply(JArray(JClass("java.lang.Object", loader=L))([kk, "mining"]))
        if a is None or int(a[2]) != int(dd[int(Defs.MINING)]) or int(a[0]) != int(Defs.levelOf(int(Defs.MINING), int(dd[int(Defs.MINING)]))):
            bad.append((kk, "run"))
        n += 1
    K.check(n > 0 and not bad, "D 0.4.35: %d live player files - capped levels + skill:fn:run = the tables (no SkyyRebirth): %s" % (n, bad[:3]))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("rebirth", run_rebirth), ("route", run_route), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyySkills"))
