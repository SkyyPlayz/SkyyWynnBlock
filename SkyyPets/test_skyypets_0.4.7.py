"""Harness for SkyyPets 0.4.7 (pet XP after Balance P3: the per-action divisors, pets.xp.pace; tools/pets_0_4_7_patch.py).
Build first: python tools/pets_0_4_7_patch.py; python SkyyPets/build_skyypets_0.4.7.py

    python SkyyPets/test_skyypets_0.4.7.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  A / C / AA  (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.6 -> 0.4.7 (exactly the planned members),
              engine-access audit
  V3          0.4.5's V3 phase on the 0.4.7 jar (the skill-tree pet rows unchanged)
  RBX         0.4.6's rebirth pet XP phase on the 0.4.7 jar with pets.xp.p3 OFF (the petecho multiplier unchanged)
  BEFORE      the 0.4.6 JAR (its own JVM): the pet XP every action below gave with the 0.4.56 / 0.1.14 / 0.3.1 / 0.1.11 XP per action
  P3          EXECUTED on 0.4.7: the same actions remembered (PetP3.note - what the three recorders call) and paid with the P3 XP per
              action -> the pet gets the BEFORE XP within 10 % (Mining Copper / Onyxium / stone / Mithril, Foraging Oak / Crystal / Birch,
              Farming Wheat / Mushroom, Orchard berry F-harvest, Alchemy Lesser / Greater, Smithing Onyxium bar, Cooking Bread / Fisherman
              pie, Ranching egg, Fishing Lv 30, Acrobatics Lv 50, Exploration Lv 1, a kill = x1); the Java rule twin = the patch's Python
              twin on every id; ? divisors; Smithing -> the last ore; pace x2; p3 off = raw; /petadmin xp (give2 false) = raw x pace; the
              level cache; Server Setup checks; forget
  LIVE        0.4.5's LIVE phase on the 0.4.7 jar (start twice on a scratch COPY of the live Skyy_SkyyPets)
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_s46 = importlib.util.spec_from_file_location("test_skyypets_0_4_6", os.path.join(HERE, "test_skyypets_0.4.6.py"))
T46 = importlib.util.module_from_spec(_s46)
_s46.loader.exec_module(T46)
T45, T44, T41 = T46.T45, T46.T44, T46.T41
HK.run_compare = _cmp0

VERSION = "0.4.7"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.6.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "pets047", "harness")))
T45.VERSION, T45.JAR = VERSION, JAR
EXPECT = {
    "PetXp": sorted(["+m give2", "~m give", "~m forget"]),
    "PetOps": ["~m admin"], "CfgFile": ["~<clinit>"],   # CfgFile: the default config text (+ the new rows)
    "SkyyPetsPlugin": ["~m setup"],
    "PetsCfg": sorted(["+f P3_ALCHEMY", "+f P3_COOKING", "+f P3_EXPL", "+f P3_FARMING", "+f P3_FLAT", "+f P3_FORAGING", "+f P3_LEVEL",
                       "+f P3_MINING", "+f P3_ON", "+f P3_SMITHING", "+f PACE", "+m checkP3", "+m checkP3List", "~<clinit>", "~m applyAll", "~m applyScalars", "~m seed"]),
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
}
ADDED = ["PetP3", "PetBreakSys", "PetHarvestSys", "PetCraftSys"]

# f(L) of SkyySkills P3Xp (xp.levelFactor.skills)
F_LV = lambda lv: 1.0 + 0.13 * (lv - 1) + 0.004 * (lv - 1) ** 2
# (label, skill the XP goes to, id remembered or None, kind 0 break / 1 craft / 2 F-harvest, XP per action 0.4.56 era, XP per action P3, levels)
# The amounts = the default tables tools/pets_0_4_7_patch.py reads from the jars (SkyySkills 0.4.56 / 0.4.57 xp.properties, SkyyCooking
# 0.1.14 / 0.1.15 xp.<dish>, SkyyExploration chunks.xp 60 -> 8, SkyyFishing fish.xp.mult 1 -> 6 + f(L), acro.jumpXp 2 -> 3 x f(L)).
ACTIONS = [
    ("Mining Copper", "Mining", "Ore_Copper_Stone", 0, 5, 50, None),
    ("Mining Onyxium", "Mining", "Ore_Onyxium_Stone", 0, 40, 2650, None),
    ("Mining Mithril", "Mining", "Ore_Mithril_Basalt", 0, 25, 1800, None),
    ("Mining stone", "Mining", "Rock_Stone", 0, 1, 1, None),
    ("Foraging Oak", "Foraging", "Wood_Oak_Trunk", 0, 6, 35, None),
    ("Foraging Crystal (full)", "Foraging", "Wood_Crystal_Trunk_Full", 0, 30, 1600, None),
    ("Foraging Banyan", "Foraging", "Wood_Banyan_Trunk", 0, 10, 1400, None),
    ("Farming Wheat", "Farming", "Plant_Crop_Wheat_Block", 0, 4, 40, None),
    ("Farming Mushroom", "Farming", "Plant_Crop_Mushroom_Block", 0, 3, 1850, None),
    ("Orchard berry (F-harvest)", "Orchard", "Plant_Crop_Berry_Bush", 2, 3, 40, None),
    ("Alchemy Lesser Health", "Alchemy", "Potion_Health_Lesser", 1, 50, 1500, None),
    ("Alchemy Greater Health", "Alchemy", "Potion_Health_Greater", 1, 18000, 33900, None),
    ("Smithing Onyxium bar", "Smithing", "Ingredient_Bar_Onyxium", 1, 40, 2650, None),
    ("Cooking Bread", "Cooking", "Food_Bread", 1, 9100, 950, None),
    ("Cooking Fisherman pie", "Cooking", "Food_Skyy_Fisherman_Pie", 1, 14950, 67100, None),
    ("Ranching egg", "Ranching", None, 0, 3, 30, None),
    ("Fishing Lv 30", "Fishing", None, 0, 10, int(round(10 * 6 * F_LV(30))), 30),
    ("Acrobatics jump Lv 50", "Acrobatics", None, 0, 2, int(round(3 * F_LV(50))), 50),
    ("Exploration chunk Lv 1", "Exploration", None, 0, 60, 8, 1),
    ("Kill (Combat.Warrior)", "Combat.Warrior", None, 0, 150, 150, None),
]
REPEAT = 20


def _pet(W, n):
    u, k, r = T44._mk(W, n)
    Cfg = W["JClass"](PKG + "PetsCfg")
    for kk, vv in (("kind", "Goat"), ("rarity", "1"), ("level", "1"), ("rebirth", str(int(Cfg.REB_MAX)))):
        r.set("pet.g1.%s" % kk, vv)
    r.set("active.1", "g1")
    return u, r


def _levels(W, LVL):
    Int = W["JClass"]("java.lang.Integer")
    W["BR"].put("skill:fn:level", W["JProxy"]("java.util.function.Function", dict={"apply": lambda a: Int.valueOf(int(LVL.get(str(a[1]), 1)))}))


def _gainer(W, u, r):
    PM, Xp = W["JClass"](PKG + "PetMath"), W["JClass"](PKG + "PetXp")

    def total():
        return sum(int(PM.need(l)) for l in range(2, int(r.levelOf("g1")) + 1)) + int(r.xpOf("g1"))

    def run(skill, amount, before=None, raw=False):
        r.set("pet.g1.level", "1")
        r.set("pet.g1.xp", "0")
        x0 = total()
        for _ in range(REPEAT):
            if before:
                before()
            if raw:
                Xp.give2(u, skill, amount, False)
            else:
                Xp.give(u, skill, amount)
        return total() - x0
    return run


def run_before(out, jar, scratch, _home):
    """the 0.4.6 jar: pet XP per action with the pre-P3 XP per action"""
    W = T44._world(out, OLD_JAR, scratch, "before")
    K = W["K"]
    LVL = {}
    _levels(W, LVL)
    u, r = _pet(W, 811)
    run = _gainer(W, u, r)
    res = {}
    for lab, sk, iid, kind, old, new, lv in ACTIONS:
        if lv:
            LVL[sk] = lv
        res[lab] = run(sk, old)
        K.check(res[lab] > 0, "BEFORE %s: 0.4.6 gives the pet %d XP for %d x %d %s XP" % (lab, res[lab], REPEAT, old, sk))
    json.dump(res, open(os.path.join(scratch, "before-gains.json"), "w"))
    K.save()


def run_p3(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "p3")
    K, JClass = W["K"], W["JClass"]
    P3, Cfg, Xp = JClass(PKG + "PetP3"), JClass(PKG + "PetsCfg"), JClass(PKG + "PetXp")
    LVL = {}
    _levels(W, LVL)
    before = json.load(open(os.path.join(scratch, "before-gains.json")))
    u, r = _pet(W, 812)
    run = _gainer(W, u, r)
    K.check(bool(Cfg.P3_ON) and float(Cfg.PACE) == 1.0, "P3 defaults: pets.xp.p3 on, pets.xp.pace 1")
    table = []
    for lab, sk, iid, kind, old, new, lv in ACTIONS:
        if lv:
            LVL[sk] = lv
        P3.LV.clear()
        note = (lambda i, k: (lambda: P3.note(u, i, k)))(iid, kind) if iid else None
        got = run(sk, new, note)
        want = before[lab]
        raw = new * REPEAT * (1.0 if sk == "Mining" else 0.5)
        ok = abs(got - want) <= max(2, 0.10 * want)
        table.append("%-26s before %8d  after %8d  (raw P3 %9d)  %+.1f %%" % (lab, want, got, raw, 100.0 * (got - want) / max(1, want)))
        K.check(ok, "P3 %s: the pet gets the pre-P3 XP within 10 %% (0.4.6 + old XP %d, 0.4.7 + P3 XP %d)" % (lab, want, got))
    K.notes.append("P3 before / after table (%d actions each, a Mining pet: Mining 100 %%, other skills 50 %%):\n  " % REPEAT + "\n  ".join(table))
    print("\n".join(table))
    # the Java rule twin = the patch's Python twin (SkyySkills SkillCfg.resolve) on every rule id and a few derived ids
    import importlib.util as _iu
    src = open(os.path.join(TOOLS, "pets_0_4_7_patch.py"), encoding="utf8").read()
    pre = src[:src.index("# ---------------------------------------------------------------------------------------------------- the patch")]
    ns = {"__file__": os.path.join(TOOLS, "pets_0_4_7_patch.py"), "__name__": "p3twin"}
    exec(compile(pre, "pets_0_4_7_patch.py (data part)", "exec"), ns)
    rules = [x for x in ns["R_NEW"] if x[2] in ("Mining", "Foraging", "Farming")]
    ids = []
    for k, i, s, x in rules:
        ids += [i, i + "_Block", "Zz" + i, i[:-1] if len(i) > 3 else i]
    ids += ["Rock_Bedrock", "Ore_Copper_Stone", "Wood_Oak_Trunk_Full", "Plant_Crop_Wheat_Block", "Soil_Grass", "Furniture_Chest"]
    bad = []
    for i in ids:
        jr = int(P3.rule(i))
        pr = ns["_resolve"](rules, i)
        jt = None if jr < 0 else (int(P3.R_KIND[jr]), str(P3.R_ID[jr]), str(P3.R_SKILL[jr]))
        pt = None if pr is None else (pr[0], pr[1], pr[2])
        if jt != pt:
            bad.append((i, jt, pt))
    K.check(not bad, "P3 the Java rule twin matches SkyySkills' resolve on %d ids: %s" % (len(ids), bad[:5]))
    # the ? divisors before any action; Smithing without a craft = the last ore; a kill x1; an unknown block / craft remembers nothing
    u2, r2 = _pet(W, 813)
    K.check(abs(float(P3.div(u2, "Mining")) - 10.0) < 1e-6 and abs(float(P3.div(u2, "Cooking")) - 0.1176) < 1e-6
            and abs(float(P3.div(u2, "Smithing")) - 22.0) < 1e-6 and abs(float(P3.div(u2, "Alchemy")) - 8.667) < 1e-6,
            "P3 nothing known yet: the ? divisors (Mining 10 = T1; review fix 1: crafts = the median - Cooking 0.1176, Smithing 22, Alchemy 8.667)")
    K.check(P3.note(u2, "Furniture_Chest", 0) is None and P3.note(u2, "Weapon_Sword_Iron", 1) is None and P3.note(u2, "Ore_Copper_Stone", 2) is None,
            "P3 a block without a rule / an unlisted craft / an F-use of a non-Farming block remembers nothing")
    P3.note(u2, "Ore_Titanium_Stone", 0)
    K.check(abs(float(P3.div(u2, "Smithing")) - 22.0) < 1e-6, "P3 FIX 1: furnace Smithing XP without a craft = the neutral median 22 (never the last ore)")
    P3.note(u2, "Ingredient_Bar_Copper", 1)
    K.check(abs(float(P3.div(u2, "Smithing")) - 10.0) < 1e-6 and abs(float(P3.div(u2, "Mining")) - 86.0) < 1e-6, "P3 a known bar wins; Mining keeps its ore")
    # review fix 1: a craft counts for 3 s only (campfire / cook:fn:out / SmeltTask XP comes without a craft event); gathering stays
    P3.note(u2, "Food_Skyy_Fisherman_Pie", 1)
    K.check(abs(float(P3.div(u2, "Cooking")) - 4.488) < 1e-6, "P3 FIX 1: a fresh dish craft is used (Fisherman pie 4.488)")
    key = str(u2) + "|Cooking"
    a = P3.LAST.get(key)
    a[1] = a[1] - 3500.0
    K.check(abs(float(P3.div(u2, "Cooking")) - 0.1176) < 1e-6, "P3 FIX 1: a dish crafted 3.5 s ago no longer counts -> neutral 0.1176 (a campfire dish)")
    a[1] = a[1] + 1000.0
    K.check(abs(float(P3.div(u2, "Cooking")) - 4.488) < 1e-6, "P3 FIX 1: ... 2.5 s ago still counts")
    m = P3.LAST.get(str(u2) + "|Mining")
    m[1] = m[1] - 600000.0
    K.check(abs(float(P3.div(u2, "Mining")) - 86.0) < 1e-6, "P3 FIX 1: a gathering action stays until the next one (Titanium 86 after 10 min)")
    sm = P3.LAST.get(str(u2) + "|Smithing")
    sm[1] = sm[1] - 5000.0
    K.check(abs(float(P3.div(u2, "Smithing")) - 22.0) < 1e-6, "P3 FIX 1: a bar crafted 5 s ago -> furnace XP after it = neutral 22")
    # review fix 2: PetBreakSys asks isCancelled BEFORE PetP3.note (bytecode order in the jar)
    import zipfile as _zf, struct as _st
    cb = _zf.ZipFile(jar).read("com/skyy/pets/PetBreakSys.class")
    n_ = _st.unpack(">H", cb[8:10])[0]
    i_, k_, cp = 10, 1, {}
    while k_ < n_:
        t_ = cb[i_]
        if t_ == 1:
            l_ = _st.unpack(">H", cb[i_ + 1:i_ + 3])[0]; cp[k_] = ("u", cb[i_ + 3:i_ + 3 + l_].decode("utf8", "replace")); i_ += 3 + l_
        elif t_ in (10, 11, 9, 12):
            cp[k_] = (t_, _st.unpack(">H", cb[i_ + 1:i_ + 3])[0], _st.unpack(">H", cb[i_ + 3:i_ + 5])[0]); i_ += 5
        elif t_ in (3, 4, 17, 18): i_ += 5
        elif t_ in (5, 6): i_ += 9; k_ += 1
        elif t_ in (7, 8, 16, 19, 20): cp[k_] = (t_, _st.unpack(">H", cb[i_ + 1:i_ + 3])[0]); i_ += 3
        elif t_ == 15: i_ += 4
        k_ += 1
    name = lambda ix: cp[cp[cp[ix][2]][1]][1] if ix in cp and cp[ix][0] in (10, 11) else None
    pos = {}
    for j in range(i_, len(cb) - 2):
        if cb[j] in (0xb6, 0xb8, 0xb9):
            nm = name(_st.unpack(">H", cb[j + 1:j + 3])[0])
            if nm in ("isCancelled", "note") and nm not in pos:
                pos[nm] = j
    K.check("isCancelled" in pos and "note" in pos and pos["isCancelled"] < pos["note"], "P3 FIX 2: PetBreakSys checks isCancelled before PetP3.note %s" % pos)
    K.check(float(P3.div(u2, "Combat")) == 1.0 and float(P3.div(u2, "Combat.Mage")) == 1.0 and float(P3.div(u2, "Battlemagic")) == 1.0,
            "P3 kill / class XP x1 (Combat, Combat.<class>, an unknown skill)")
    K.check(abs(float(P3.div(u2, "mining")) - 86.0) < 1e-6, "P3 skill names match without case")
    # Exploration zones by level
    for lv, z in ((1, 0), (19, 0), (20, 1), (45, 2), (65, 3), (99, 4)):
        LVL["Exploration"] = lv
        P3.LV.clear()
        K.check(abs(float(P3.div(u2, "Exploration")) - [0.1304, 0.3696, 0.5601, 0.6012, 0.9642][z]) < 1e-6, "P3 Exploration Lv %d = Zone %d divisor" % (lv, z + 1))
    # the level cache: 5 s
    LVL["Fishing"] = 10
    P3.LV.clear()
    d10 = float(P3.div(u2, "Fishing"))
    LVL["Fishing"] = 50
    K.check(float(P3.div(u2, "Fishing")) == d10 and abs(d10 - 6 * F_LV(10)) < 1e-6, "P3 the level is cached (5 s): Fishing Lv 10 = 6 x f(10)")
    # pace, p3 off, /petadmin xp
    run2 = _gainer(W, u2, r2)
    prb = 1.0 + float(Cfg.REB_XP) * int(r2.rebirthOf("g1")) / 100.0   # the pet's own rebirth bonus (0.3.0) stays
    P3.note(u2, "Ore_Onyxium_Stone", 0)
    g1 = run2("Mining", 2650)
    Cfg.PACE = 2.0
    g2 = run2("Mining", 2650)
    K.check(abs(g2 - 2 * g1) <= 2 and abs(g1 - REPEAT * 40 * prb) <= 2, "P3 pets.xp.pace 2 doubles the pet XP (%d -> %d)" % (g1, g2))
    ga = run2("Mining", 2650, raw=True)
    K.check(abs(ga - 2 * REPEAT * 2650 * prb) <= 2, "P3 /petadmin xp (give2 false) = the amount as typed x pace (%d)" % ga)
    Cfg.PACE = 1.0
    Cfg.P3_ON = False
    K.check(P3.note(u2, "Ore_Copper_Stone", 0) is None, "P3 off: nothing is remembered")
    gr = run2("Mining", 2650)
    K.check(abs(gr - REPEAT * 2650 * prb) <= 2, "P3 off: pets follow raw skill XP (%d)" % gr)
    Cfg.P3_ON = True
    # Server Setup: the divisor rows are live text fields; an edit changes the divisor; the checks refuse junk
    old = str(Cfg.P3_MINING)
    Cfg.P3_MINING = old.replace("Ore_Onyxium:66.25", "Ore_Onyxium:20")
    P3.note(u2, "Ore_Onyxium_Stone", 0)
    K.check(abs(float(P3.div(u2, "Mining")) - 20.0) < 1e-6, "P3 an edited Mining row is used at once (Onyxium 20)")
    Cfg.P3_MINING = old
    for v, ok in (("?:10,Ore_Copper:10", True), ("-", True), ("Ore_Copper", False), ("Ore_Copper:0", False), ("Ore_Copper:abc", False),
                  ("Ore_Copper:200000", False), ("Ore_Copper:-1", False)):
        res = Cfg.checkP3("pets.xp.p3.mining", v)
        K.check((res is None) == ok, "P3 checkP3 %r -> %s" % (v, res))
    K.check(Cfg.checkP3List("pets.xp.p3.levelSkills", "Acrobatics,Fishing") is None and Cfg.checkP3List("k", "Fish1ng") is not None,
            "P3 checkP3List: skill names only")
    K.check(len(P3.parse("?:1,bad,Ore_:x,Ore_Iron:2")) == 2, "P3 a bad entry is skipped at run time (the check refuses it in Server Setup)")
    # forget
    Xp.forget(u2)
    K.check(not any(str(k).startswith(str(u2) + "|") for k in P3.LAST.keySet().toArray()), "P3 forget (leave) clears the remembered actions")
    K.save()


def run_rbx_off(out, jar, scratch, home):
    """0.4.6's RBX phase with the P3 divisors off (it pays Mining XP to a Mining pet and expects the raw share)"""
    w0 = T44._world

    def w(*a, **kw):
        W = w0(*a, **kw)
        W["JClass"](PKG + "PetsCfg").P3_ON = False
        return W
    T44._world = w
    try:
        T46.run_rbx(out, jar, scratch, home)
    finally:
        T44._world = w0


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("v3", T45.run_v3), ("rbx", run_rbx_off), ("before", run_before), ("p3", run_p3), ("live", T45.run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
