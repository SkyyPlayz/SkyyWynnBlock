"""Harness for SkyyPets 0.4.9 (Balance P8c: Beastmastery XP from pet XP + the Beastmastery tree rows; tools/pets_0_4_9_patch.py). Build first:
    python tools/pets_0_4_9_patch.py && python SkyyPets/build_skyypets_0.4.9.py
    python SkyyPets/test_skyypets_0.4.9.py [--keep]

  S     static   the patch re-runs to identical bytes; one class added (PetBm); give2's loop guard first; no new system / command
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.8 -> 0.4.9, engine-access audit
  BM    EXECUTED PetXp.give on real pet records with a recording skill:fn:addxp: the pet XP REALLY gained goes to Beastmastery as whole points
                 (args UUID, "Beastmastery", Long, "pets", profile key); fractions carry per profile; a pet at its max level sends nothing;
                 XP reported for "Beastmastery" itself feeds no pet and sends nothing (loop guard); FALSE / no SkyySkills / a throwing
                 function never breaks the grant; /petadmin xp (give2 p3 false) counts too
  V3    EXECUTED the Beastmastery tree rows through a stub tree:fn:level: pet XP rows per kind (Combat / Mining / green / all; maxed = x1.30,
                 Exploration x1.06), the 1 s rank cache; pet stat rows through PetBuff.compute2 (the Mining tree's Pet Synergy unchanged,
                 Stone Bond + Earthen Gift, Gentle Giant only on Rare+, the summon slot at its percent, a Combat pet, a green pet; maxed
                 = +15 % on a Rare+ pet of any kind, +13 % on a Common one; Kinship +3 % on every pet); fixer 2: Gentle Hand = +1 Hatchery
                 slot a rank (+ the bridge key, at most 10 extra; a respec never hides a filled slot); tree:reads:SkyyPets = the 30 rows' keys; trees.properties: the 12
                 old rows' numbers unchanged, a missing new line = the built-in number, a set one is read; the Server Setup rows
  LIVE  START TWICE on a scratch COPY of the live Skyy_SkyyPets: no one-time update runs (P5's marker is there), the live trees.properties
                 (written by 0.4.8, without the new lines) is read as it is and never rewritten, every pet file reads; start 2 = nothing
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "balp8c", "pets")]
import skyybuild as B
import harness_kit as HK
import trees_v3_effects as V3E

_cmp0 = HK.run_compare
_s44 = importlib.util.spec_from_file_location("test_skyypets_0_4_4", os.path.join(HERE, "test_skyypets_0.4.4.py"))
T44 = importlib.util.module_from_spec(_s44)
_s44.loader.exec_module(T44)
T41 = T44.T41
HK.run_compare = _cmp0

VERSION = "0.4.9"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.8.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.8.py")
PATCH = os.path.join(TOOLS, "pets_0_4_9_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T44.PKG = PKG
EXPECT = {   # checked by hand 2026-10-22
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],   # the version texts
    "PetsMigP5": ["~m mgLog", "~m run"],   # the version text in its log lines (0.4.8's update itself unchanged)
    "PetBuff": ["~m compute2"],
    "PetV3": ["+f HSC", "+f RARE_MIN", "+f XPC", "+f XPC_MS", "+m hatchSlots", "+m kindMatch", "+m synFor", "+m xpArr", "+m xpPct", "~<clinit>", "~m reads"],   # reads: the READS list (+ 18 keys)
    "PetHatchery": ["~m extra"],   # fixer 2: + Gentle Hand's Hatchery slots
    "PetXp": ["~m give2"],
    "PetsCfg": ["+f V3P12", "+f V3P13", "+f V3P14", "+f V3P15", "+f V3P16", "+f V3P17", "+f V3P18", "+f V3P19", "+f V3P20", "+f V3P21",
                "+f V3P22", "+f V3P23", "+f V3P24", "+f V3P25", "+f V3P26", "+f V3P27", "+f V3P28", "+f V3P29",
                "+f V3X12", "+f V3X13", "+f V3X14", "+f V3X15", "+f V3X16", "+f V3X17", "+f V3X18", "+f V3X19", "+f V3X20", "+f V3X21",
                "+f V3X22", "+f V3X23", "+f V3X24", "+f V3X25", "+f V3X26", "+f V3X27", "+f V3X28", "+f V3X29",
                "~<clinit>", "~m applyAll", "~m loadV3", "~m seed", "~m v3most", "~m v3per"],   # applyAll / seed: the version text
    "SkyyPetsPlugin": ["~m setup"]}
ADDED = ["PetBm"]
BMK = dict((V3E.up(e[0], e[1], e[2])["name"], V3E.key(e[0], e[1], e[2])) for e in V3E.rows("SkyyPets") if e[0] == "Beastmastery")
SYNK = V3E.key("Mining", 3, "r5a")   # the Mining tree's Pet Synergy (0.4.5)


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.9 - build script') and g.count('VERSION = "0.4.9"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("= cls(") - o.count("= cls("), 1, "S one class added (PetBm)")
    gv = g[g.index("public static int give2("):]
    K.check(gv.index("PetBm.isBeast(skill)") < gv.index("for (int s = 1; s <= 2; s++)") < gv.index("PetBm.add(u, bmg)"), "S give2: the loop guard first, the send last")
    K.check(g.index('bmc = cls("PetBm")') < g.index('xp = cls("PetXp")'), "S PetBm compiled before PetXp")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _stubs(W):
    """a recording skill:fn:addxp + a stub tree:fn:level (RANKS: saved key -> rank)"""
    JClass, JProxy = W["JClass"], W["JProxy"]
    BR = W["BR"]
    calls, mode, ranks = [], {"r": True}, {}

    def addxp(a):
        calls.append([str(a[0]), str(a[1]), int(a[2]), str(a[3]), str(a[4])])
        if mode["r"] == "throw":
            raise RuntimeError("boom")
        return JClass("java.lang.Boolean").valueOf(bool(mode["r"]))
    BR.put("skill:fn:addxp", JProxy("java.util.function.Function", dict={"apply": addxp}))
    BR.put("tree:fn:level", JProxy("java.util.function.Function", dict={"apply": lambda a: JClass("java.lang.Integer").valueOf(int(ranks.get(str(a[1]), 0)))}))
    return calls, mode, ranks


def _pet(r, pid, kind, rar, lvl, slot=None):
    for kk, vv in (("kind", kind), ("rarity", str(rar)), ("level", str(lvl))):
        r.set("pet.%s.%s" % (pid, kk), vv)
    if slot:
        r.set("active.%d" % slot, pid)


def run_bm(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "bm")
    K, JClass = W["K"], W["JClass"]
    P_ = lambda n: JClass(PKG + n)
    Xp, Bm, V3 = P_("PetXp"), P_("PetBm"), P_("PetV3")
    calls, mode, ranks = _stubs(W)
    u, k, r = T44._mk(W, 9101)
    _pet(r, "m1", "Mouse", 1, 40, slot=1)   # Lv 40: the next level needs 9,920 XP - no level-up in this test
    sk = str(P_("PetsCfg").kind("Mouse").skill)
    K.eq(sk, "Mining", "BM the Mouse is a Mining pet")
    x0 = int(r.xpOf("m1"))
    Xp.give(u, "Mining", 1000)
    K.check(int(r.xpOf("m1")) - x0 == 500 and calls == [[str(u), "Beastmastery", 500, "pets", k]],
            "BM Mining 1000 -> the pet +500 XP and skill:fn:addxp {UUID, Beastmastery, 500, pets, key}: %s" % calls)
    del calls[:]
    Xp.give(u, "Foraging", 30)   # other skill 5 % = 1.5 pet XP
    Xp.give(u, "Foraging", 30)
    K.check([c[2] for c in calls] == [1, 2] and int(r.xpOf("m1")) - x0 == 503, "BM fractions carry per profile: 1.5 -> 1, then 1.5 + 0.5 -> 2 (pet XP %d): %s" % (int(r.xpOf("m1")) - x0, calls))
    del calls[:]
    g0 = int(Bm.SENT.get())
    Xp.give(u, "Beastmastery", 1000)
    K.check(not calls and int(r.xpOf("m1")) - x0 == 503 and int(Bm.SENT.get()) == g0, "BM loop guard: XP reported for Beastmastery feeds no pet and sends nothing")
    # a pet at its max level gains nothing -> sends nothing
    u2, k2, r2 = T44._mk(W, 9102)
    cap = int(r2.capOf("x")) if False else None
    _pet(r2, "c1", "Mouse", 1, 50, slot=1)
    cap = int(r2.capOf("c1"))
    if cap != 50:
        _pet(r2, "c1", "Mouse", 1, cap, slot=1)
    del calls[:]
    Xp.give(u2, "Mining", 1000)
    K.check(not calls and int(r2.levelOf("c1")) == cap, "BM a pet at its max level (Lv %d) gains nothing - no Beastmastery XP" % cap)
    # fixer 1: the grant that takes a pet to its max level counts only the XP up to it
    _pet(r2, "c2", "Mouse", 1, cap - 1, slot=1)
    need = int(P_("PetMath").need(cap))
    del calls[:]
    Xp.give2(u2, "Mining", 10000000, False)
    K.check(int(r2.levelOf("c2")) == cap and [c[2] for c in calls] == [need] and float(Bm.room(r2, "c2")) == 0.0,
            "BM fixer 1: Lv %d -> %d with a huge grant sends only the %d XP up to the max level: %s" % (cap - 1, cap, need, calls))
    # FALSE / throw / no function
    mode["r"] = False
    del calls[:]
    rf0 = int(Bm.REFUSED.get())
    Xp.give(u, "Mining", 100)
    K.check(len(calls) == 1 and int(Bm.REFUSED.get()) == rf0 + 50, "BM SkyySkills answers FALSE (an older one) -> counted as refused, the pet still got its XP")
    # fixer 2: a refused offer keeps its points for the next grant (at most HOLD a profile)
    mode["r"] = True
    del calls[:]
    Xp.give(u, "Mining", 100)
    K.check([c[2] for c in calls] == [100] and int(Bm.REFUSED.get()) == rf0 + 50, "BM fixer 2: the 50 refused points go with the next grant (50 + 50 = 100): %s" % calls)
    Bm.giveBack("hold-test", 5000)
    K.eq(int(Bm.take("hold-test", 0.5)), int(Bm.HOLD), "BM fixer 2: at most HOLD (%d) refused points are kept a profile" % int(Bm.HOLD))
    mode["r"] = False
    mode["r"] = "throw"
    x1 = int(r.xpOf("m1"))
    n = int(Xp.give(u, "Mining", 100))
    K.check(n == 1 and int(r.xpOf("m1")) - x1 == 50 and bool(Bm.WARNED), "BM a throwing skill:fn:addxp never breaks the grant (one WARN)")
    mode["r"] = True
    W["BR"].remove("skill:fn:addxp")
    del calls[:]
    K.check(int(Bm.add(u, 10.0)) == 0, "BM no skill:fn:addxp (no SkyySkills) = nothing")
    _stubs_again = _stubs(W)
    calls2 = _stubs_again[0]
    Xp.give2(u, "Mining", 20, False)   # /petadmin xp
    K.check([c[2] for c in calls2] == [10], "BM /petadmin xp (give2 p3 false) counts too: %s" % calls2)
    W["K"].save()


def run_v3(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "v3")
    K, JClass = W["K"], W["JClass"]
    P_ = lambda n: JClass(PKG + n)
    Xp, V3, Buff, Cfg, Kind = P_("PetXp"), P_("PetV3"), P_("PetBuff"), P_("PetsCfg"), P_("PetKind")
    calls, mode, ranks = _stubs(W)
    keys = [str(x) for x in Kind.STAT_KEYS]
    fk = "fortune.mining"

    def setr(d):
        ranks.clear()
        ranks.update(d)
        V3.XPC.clear()
        V3.HSC.clear()
    # ---- pet XP rows
    u, k, r = T44._mk(W, 9201)
    _pet(r, "m1", "Mouse", 1, 40, slot=1)
    x0 = int(r.xpOf("m1"))
    setr({BMK["Digger's Calling"]: 5, BMK["Deep Tempering"]: 3, BMK["Rapid Learner"]: 3})
    del calls[:]
    Xp.give(u, "Mining", 1000)
    K.check(int(r.xpOf("m1")) - x0 == 650 and calls[-1][2] == 650, "V3 Mining pet with Digger's Calling 5 + Deep Tempering 3 + Rapid Learner 3: 500 x 1.30 = 650 pet XP (and 650 Beastmastery): %d"
            % (int(r.xpOf("m1")) - x0))
    allmax = dict((BMK[n_], V3E.maxrank("Beastmastery", b_, i_)) for n_, b_, i_ in
                  [(V3E.up(e[0], e[1], e[2])["name"], e[1], e[2]) for e in V3E.rows("SkyyPets") if e[0] == "Beastmastery"])
    setr(allmax)
    got = dict((s_, round(float(V3.xpPct(u, s_)), 9)) for s_ in ("Combat", "Mining", "Farming", "Foraging", "Exploration"))
    K.eq(got, {"Combat": 0.3, "Mining": 0.3, "Farming": 0.3, "Foraging": 0.3, "Exploration": 0.06}, "V3 every row maxed: pet XP +30 % a kind (the spec budget), Exploration pets +6 % (Rapid Learner)")
    ranks[BMK["Rapid Learner"]] = 0
    K.check(abs(float(V3.xpPct(u, "Mining")) - 0.3) < 1e-9, "V3 the ranks are cached for 1 s (a change inside the second is not read yet)")
    V3.XPC.clear()
    K.check(abs(float(V3.xpPct(u, "Mining")) - 0.24) < 1e-9, "V3 after the cache: Rapid Learner 0 -> Mining pets +24 %")
    # ---- pet stat rows (PetBuff.compute2)
    def stats(u_, r_):
        t = list(Buff.compute2(u_, r_, "w"))
        return dict((keys[i], float(t[i])) for i in range(len(t)) if abs(float(t[i])) > 1e-9)
    u3, k3, r3 = T44._mk(W, 9203)
    _pet(r3, "m1", "Mouse", 1, 50, slot=1)
    setr({})
    base = stats(u3, r3).get(fk, 0.0)
    K.check(abs(base - 44.0) < 1e-6, "V3 a Common Lv 50 Mouse = 44 Mining Fortune, no rows")
    setr({SYNK: 3})
    K.check(abs(stats(u3, r3).get(fk, 0.0) - 44.0 * 1.12) < 1e-6, "V3 the Mining tree's Pet Synergy 3 = +12 %% as in 0.4.5/0.4.8 (%.3f)" % stats(u3, r3).get(fk, 0.0))
    setr({BMK["Stone Bond"]: 4, BMK["Earthen Gift"]: 3})
    K.check(abs(stats(u3, r3).get(fk, 0.0) - 44.0 * 1.10) < 1e-6, "V3 Stone Bond 4 + Earthen Gift 3 = +10 %% on a Mining pet (%.3f)" % stats(u3, r3).get(fk, 0.0))
    setr({BMK["Gentle Giant"]: 2})
    K.check(abs(stats(u3, r3).get(fk, 0.0) - 44.0) < 1e-6, "V3 Gentle Giant gives a Common pet nothing")
    _pet(r3, "m1", "Mouse", 3, 50, slot=1)
    rare = 88.0 * float(Cfg.factor(3)) * 0.5
    K.check(abs(stats(u3, r3).get(fk, 0.0) - rare * 1.02) < 1e-6, "V3 Gentle Giant 2 = +2 %% on a Rare pet (fixer: 1 %% a rank) (%.3f vs %.3f)" % (stats(u3, r3).get(fk, 0.0), rare * 1.02))
    setr({BMK["Battle Bond"]: 4})
    K.check(abs(stats(u3, r3).get(fk, 0.0) - rare) < 1e-6, "V3 a Combat row gives a Mining pet nothing")
    setr(allmax)
    K.check(abs(stats(u3, r3).get(fk, 0.0) - rare * 1.15) < 1e-6, "V3 every row maxed: a Rare Mining pet +15 % (the spec budget)")
    _pet(r3, "m1", "Mouse", 1, 50, slot=1)
    K.check(abs(stats(u3, r3).get(fk, 0.0) - 44.0 * 1.13) < 1e-6, "V3 every row maxed: a Common Mining pet +13 % (no Gentle Giant; Kinship 3 included)")
    setr({BMK["Kinship of the Wild"]: 1})
    K.check(abs(stats(u3, r3).get(fk, 0.0) - 44.0 * 1.03) < 1e-6, "V3 fixer: Kinship of the Wild (the bottom +%% global node) = +3 %% on a Common Mining pet (%.3f)" % stats(u3, r3).get(fk, 0.0))
    setr({SYNK: 3, BMK["Stone Bond"]: 4, BMK["Earthen Gift"]: 3})
    K.check(abs(stats(u3, r3).get(fk, 0.0) - 44.0 * 1.22) < 1e-6, "V3 the two trees add (Mining 12 % + Beastmastery 10 %)")
    # a Combat pet + a summoned fighter (summon slot at its percent), a green pet
    u4, k4, r4 = T44._mk(W, 9204)
    _pet(r4, "d1", "Dog", 1, 100, slot=1)
    _pet(r4, "w1", "Wolf", 1, 100, slot=2)
    Cfg.SLOT2_MODE = "always"
    setr({})
    s0 = stats(u4, r4)
    setr({BMK["Battle Bond"]: 4, BMK["Predator's Gift"]: 3})
    s1 = stats(u4, r4)
    dog = dict((kk, float(vv)) for kk, vv in zip([str(x) for x in Cfg.kind("Dog").keys], [float(x) for x in Cfg.kind("Dog").vals]))
    wolf = dict((kk, float(vv)) for kk, vv in zip([str(x) for x in Cfg.kind("Wolf").keys], [float(x) for x in Cfg.kind("Wolf").vals]))
    p2 = float(Cfg.SLOT2_PCT) / 100.0
    want = dict((kk, s0.get(kk, 0.0) + 0.10 * dog.get(kk, 0.0) * float(Cfg.factor(1)) + 0.10 * p2 * wolf.get(kk, 0.0) * float(Cfg.factor(1))) for kk in set(s0) | set(dog) | set(wolf) if kk in keys)
    bad = [(kk, s1.get(kk, 0.0), want[kk]) for kk in want if abs(s1.get(kk, 0.0) - want[kk]) > 1e-6]
    K.check(not bad and str(Cfg.kind("Dog").skill) == "Combat" and str(Cfg.kind("Wolf").skill) == "Combat",
            "V3 Battle Bond 4 + Predator's Gift 3 = +10 %% on the Combat pet, + 10 %% x the summon percent (%s %%) on the summoned Wolf: %s" % (Cfg.SLOT2_PCT, bad[:3]))
    Cfg.SLOT2_MODE = "unlock"
    green = None
    for kn in [str(x.id) for x in Cfg.KINDS]:
        if str(Cfg.kind(kn).skill) == "Farming" and str(Cfg.roles(kn)).find("fighter") < 0:
            green = kn
            break
    u5, k5, r5 = T44._mk(W, 9205)
    _pet(r5, "f1", green, 1, 100, slot=1)
    setr({})
    g0 = stats(u5, r5)
    setr({BMK["Verdant Bond"]: 4, BMK["Wild Bond"]: 4, BMK["Nature's Gift"]: 3})
    g1 = stats(u5, r5)
    K.check(g0 and all(abs(g1.get(kk, 0.0) - v_ * 1.10) < 1e-6 for kk, v_ in g0.items()),
            "V3 a Farming pet (%s): Verdant Bond 4 + Nature's Gift 3 = +10 %%, Wild Bond (Foraging) nothing: %s -> %s" % (green, g0, g1))
    # ---- fixer 2: Gentle Hand = +1 Hatchery slot a rank (PetHatchery.extra / slots), docs/answered/pets.md 2026-10-16 LOCKED
    Hy = P_("PetHatchery")
    u6, k6, r6 = T44._mk(W, 9206)
    hs = int(Cfg.HATCH_SLOTS)
    setr({})
    K.check(int(Hy.extra(u6)) == 0 and int(Hy.slots(u6)) == hs and "(Beastmastery gives more)" in str(Hy.headText(r6, u6)),
            "V3 fixer 2: no Gentle Hand = the %d free Hatchery slots (%s)" % (hs, Hy.headText(r6, u6)))
    setr({BMK["Gentle Hand"]: 2})
    K.check(int(Hy.extra(u6)) == 2 and int(Hy.slots(u6)) == hs + 2 and "(2 from Beastmastery)" in str(Hy.headText(r6, u6)),
            "V3 fixer 2: Gentle Hand 2 = +2 Hatchery slots (%d): %s" % (int(Hy.slots(u6)), Hy.headText(r6, u6)))
    ranks[BMK["Gentle Hand"]] = 3
    K.check(int(Hy.extra(u6)) == 2, "V3 fixer 2: the Hatchery slot rank is cached for 1 s")
    V3.HSC.clear()
    K.check(int(Hy.extra(u6)) == 3 and int(Hy.slots(u6)) == hs + 3, "V3 fixer 2: Gentle Hand 3 (max) = +3 slots")
    W["BR"].put("pets:hatch:slots:" + str(u6), JClass("java.lang.Integer").valueOf(9))
    K.check(int(Hy.extra(u6)) == 10, "V3 fixer 2: the bridge key 9 + Gentle Hand 3 stops at 10 extra")
    W["BR"].remove("pets:hatch:slots:" + str(u6))
    r6.set("hatchery.%d" % (hs + 3), "Skyy_Pet_Egg_Common|0|h1|inv")
    setr({})
    K.check(int(Hy.shownSlots(r6, u6)) == hs + 3 and 1 <= int(Hy.freeSlot(r6, u6)) <= hs and int(Hy.used(r6)) == 1,
            "V3 fixer 2: a respec (Gentle Hand 3 -> 0) keeps the egg in slot %d on the page, new eggs go to slots 1-%d only" % (hs + 3, hs))
    r6.set("hatchery.%d" % (hs + 3), None)
    # tree:reads, the cfg numbers, the Server Setup rows
    V3.reads(True)
    rd = str(W["BR"].get("tree:reads:SkyyPets")).split(",")
    K.check(set(BMK.values()) <= set(rd) and [x for x in rd if x.startswith("Skill.")] == V3E.keys("SkyyPets") and len(V3E.keys("SkyyPets")) == 26,
            "V3 tree:reads:SkyyPets lists the 26 keys of its 30 rows (18 Beastmastery, fixer 2: + Gentle Hand): %d" % len(rd))
    R = V3E.rows("SkyyPets")
    K.check(all(abs(float(Cfg.v3per(i)) - R[i][5]) < 1e-12 and abs(float(Cfg.v3most(i)) - V3E.vmax(R[i])) < 1e-12 for i in range(len(R))),
            "V3 every row's built-in per / ceiling = the table (30 rows; the 12 old ones unchanged)")
    d = os.path.join(scratch, "v3cfg")
    os.makedirs(d, exist_ok=True)
    old12 = "".join(l + "\n" for l in V3E.cfg_text("SkyyPets").split("\n") if not l.startswith(("tree.Beastmastery", "# Beastmastery")) and l)
    open(os.path.join(d, "trees.properties"), "w").write(old12 + "tree.Beastmastery.b2.r1a.petxp.per=5\n")
    msg = str(Cfg.loadV3(JClass("java.nio.file.Paths").get(d)))
    ig = [i for i, e in enumerate(R) if (e[0], e[1], e[2]) == ("Beastmastery", 2, "r1a")][0]
    ih = [i for i, e in enumerate(R) if (e[0], e[1], e[2]) == ("Beastmastery", 2, "r4b")][0]
    K.check(msg == "trees.properties read" and abs(float(Cfg.v3per(ig)) - 0.05) < 1e-12 and abs(float(Cfg.v3per(ih)) - 0.04) < 1e-12
            and open(os.path.join(d, "trees.properties")).read().endswith("petxp.per=5\n"),
            "V3 a 0.4.8 trees.properties: a missing new line = the built-in number, a set one is read, the file is never rewritten")
    rows = dict((str(rr[0]), [str(x) for x in list(rr)]) for rr in P_("CfgRows").header()[7])
    nk = [V3E.ckey(e) + s_ for e in R if e[0] == "Beastmastery" for s_ in (".per", ".max")]
    K.check(all(x in rows and rows[x][2] == "trees" for x in nk) and len(nk) == 36, "V3 Server Setup -> Pets -> Skill trees: + 36 rows (fixer 2: + Gentle Hand's 2)")
    W["K"].save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Mig, Mig2, MgP5, Log = P_("PetsCfg"), P_("PetStore"), P_("PetsCfgMig"), P_("PetsCfgMig2"), P_("PetsMigP5"), P_("PetsLog")
    Paths = JClass("java.nio.file.Paths")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.dirname(home)
    t0 = T41.tree(home)
    tp = os.path.join(home, "trees.properties")
    tb = open(tp, "rb").read() if os.path.isfile(tp) else None

    def start():
        Mig.run(Paths.get(home))
        Mig2.run(Paths.get(home))
        r = str(MgP5.run(Paths.get(home)))
        Cfg.load(Paths.get(mods))
        v = str(Cfg.loadV3(Paths.get(home)))
        Store.ROOT = Paths.get(home)
        Store.DIR = Store.ROOT.resolve("pets")
        return r, v, [int(x) for x in Store.scanAll()]
    r1, v1, sc1 = start()
    print("   live start 1: P5 %r, %s, pet files %s" % (r1[:80], v1, sc1))
    K.check(v1 == "trees.properties read" and (r1 == "" or "Balance P5 power (SkyyPets 0.4.8)" in r1),
            "LIVE start 1: only 0.4.8's own P5 update may run (the live world has not started since the P5 deploy: %s); trees.properties read" % ("ran" if r1 else "already done"))
    K.check(tb is not None and open(tp, "rb").read() == tb and b"Beastmastery" not in tb, "LIVE the live trees.properties (0.4.8's, no Beastmastery lines) is not rewritten")
    R = V3E.rows("SkyyPets")
    K.check(all(abs(float(Cfg.v3per(i)) - R[i][5]) < 1e-12 for i in range(12, len(R))), "LIVE the 18 new rows read their built-in numbers")
    K.check(sc1[2] == 0 and sc1[3] == 0, "LIVE every pet file reads (%s)" % sc1)
    t1 = T41.tree(home)
    r2, v2, sc2 = start()
    K.check(r2 == "" and T41.tree(home) == t1 and sc2 == sc1, "LIVE start 2 writes nothing")
    K.check(all(x.startswith(("config-history", "migrations")) for x in set(t1) - set(t0)) and (r1 != "" or set(t1) == set(t0)),
            "LIVE no file added but P5's own History copy + marker: %s" % sorted(set(t1) - set(t0))[:5])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("bm", run_bm), ("v3", run_v3), ("live", run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
