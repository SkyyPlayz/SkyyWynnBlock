"""Harness for SkyyPets 0.4.8 (Balance P5 pets: kind budget, rarity x1.75, health / mana % of max, Fortune 88 / 70 + no cap, pet XP 50 / 5 %
with the P3 divisors off, the one-time PetsMigP5; tools/pets_0_4_8_patch.py). Build first:
    python tools/pets_0_4_8_patch.py && python SkyyPets/build_skyypets_0.4.8.py
    python SkyyPets/test_skyypets_0.4.8.py [--keep]

  S     static   the patch re-runs to identical bytes; one class added (PetsMigP5); setup order PetsCfgMig -> 2 -> P5 -> load
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.7 -> 0.4.8, engine-access audit
  K     kinds    EXECUTED through the jar's PetBuff.compute on real pet records (Lv 100, the kind's start rarity): every combat kind's DPS x EHP
                 (tools/balance_model.py's gear formulas) = 1 + 0.42 x its rarity bonus +- 5 %; the rarity rows 1 / 1.15 / 1.3 / 1.45 / 1.6 / 1.75;
                 a Rare Lv 30 Fortune-only pet = 34 Fortune, a Mythic Lv 100 with 5 pet rebirths = 192 (no cap clips it; a cap set by hand
                 still does); a two-stat kind 70 x rarity with its other stats unchanged; the 0.4.3 roster kinds (built-in lines) too
  PCT   health % EXECUTED on a REAL EntityStatMap: PetBuff.stats -> skyypet_health = 12 % x the max without it (base 100 -> +12; recomputed
                 stays +12, not compounding), mana the same; a pct that goes DOWN lowers at once; the max without us shrinking waits 3 s
                 (modPct with explicit clocks), then lowers; 0 removes the modifier
  XP    pet XP   EXECUTED PetXp.give: own skill 1000 -> +500 pet XP, other skill 1000 -> +50 (pets.xp.p3 off = no divisor); the pace check:
                 tools/balance_model.py p5_pet_xp_trace - a Mining / combat pet reaches Lv 50 at hour 28-33 of run 1
  MIG   update   PetsMigP5.mgUpdate (pure text) on: a 0.4.7 default file (all 9 rows + 33 kind lines move), CRLF kept, a hand-edited rarity
                 kept + noted, a hand-edited kind kept, a continued line kept, the bool any case ("TRUE"), no lines; sameAfter refuses an extra
                 change; run() writes the marker LAST and a second run does nothing; a fresh home = marker only
  LIVE  START TWICE on a scratch COPY of the live Skyy_SkyyPets (setup's chain): config.properties changes exactly the planned keys
                 (Properties), each to its new value; History copy; one change-log line per change; marker; every pet file reads; start 2 =
                 nothing written
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util, subprocess, shutil, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "balp5", "pets")]
import skyybuild as B
import harness_kit as HK
import balance_model as BM

_cmp0 = HK.run_compare
_s44 = importlib.util.spec_from_file_location("test_skyypets_0_4_4", os.path.join(HERE, "test_skyypets_0.4.4.py"))
T44 = importlib.util.module_from_spec(_s44)
_s44.loader.exec_module(T44)
T41 = T44.T41
HK.run_compare = _cmp0

VERSION = "0.4.8"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.7.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.7.py")
PATCH = os.path.join(TOOLS, "pets_0_4_8_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T44.PKG = PKG
EXPECT = {   # checked by hand 2026-10-21: the version texts (CfgFn / CfgRows / PetsCfg.seed / applyAll), the new defaults (PetKind kinds + names,
             # PetsCfg rows), PetBuff's Fortune cap 0 = none + the % stats, the setup's PetsMigP5 call
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
    "PetBuff": ["+f LOW", "+f LOW_MS", "+f PCTS", "+m flatMax", "+m flatOf", "+m modPct", "+m pctKey", "+m pctWant", "~<clinit>", "~m compute", "~m compute2", "~m stats"],
    "PetKind": ["~<clinit>"], "PetsCfg": ["~<clinit>", "~m applyAll", "~m applyScalars", "~m seed"], "SkyyPetsPlugin": ["~m setup"]}
ADDED = ["PetsMigP5"]
COMBAT = BM.P5_PET_KINDS
FORT_ONLY = ["Rabbit", "Bunny", "Cat", "Corgi", "Frog", "Mouse", "Squirrel", "Meerkat", "Turkey"]
FORT_TWO = ["Chicken", "Goat", "Warthog", "Bear", "Mosshorn", "Bison", "CrystalGolem", "Molerat", "Moose", "Owl"]
RAR = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]


def _props(b):
    from jpype import JClass
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.ByteArrayInputStream")(b))
    return {str(k): str(p.getProperty(k)) for k in p.stringPropertyNames()}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.8 - build script') and g.count('VERSION = "0.4.8"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.eq(g.count("= cls(") - o.count("= cls("), 1, "S one class added (PetsMigP5)")
    su = g[g.index("public void setup() {"):]
    K.check(su.index("PetsCfgMig.run(") < su.index("PetsCfgMig2.run(") < su.index("PetsMigP5.run(") < su.index("PetsCfg.load(mods)"), "S setup: Mig -> Mig2 -> MigP5 -> load")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_kinds(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "kinds")
    K, JClass = W["K"], W["JClass"]
    P_ = lambda n: JClass(PKG + n)
    Buff, Cfg, Kind = P_("PetBuff"), P_("PetsCfg"), P_("PetKind")
    keys = [str(x) for x in Kind.STAT_KEYS]
    K.eq([round(float(Cfg.factor(i)), 4) for i in range(1, 7)], [1.0, 1.15, 1.3, 1.45, 1.6, 1.75], "K rarity rows x1 / 1.15 / 1.3 / 1.45 / 1.6 / 1.75")
    K.check(abs(float(Cfg.FORT_CAP)) < 1e-12 and int(Cfg.XP_OWN) == 50 and int(Cfg.XP_OTHER) == 5 and not bool(Cfg.P3_ON),
            "K defaults: Fortune cap 0 (none), XP own 50 %% / other 5 %%, P3 divisors off")
    n = [0]

    def rec(kind, rarity_i, level, reb=0):
        n[0] += 1
        u, k, r = T44._mk(W, 800 + n[0])
        for kk, vv in (("kind", kind), ("rarity", str(rarity_i)), ("level", str(level)), ("rebirth", str(reb))):
            r.set("pet.p1.%s" % kk, vv)
        r.set("active.1", "p1")
        return r

    def totals(kind, rarity_i, level, reb=0):
        t = list(Buff.compute(rec(kind, rarity_i, level, reb), "w"))
        return dict((keys[i], float(t[i])) for i in range(len(t)) if abs(float(t[i])) > 1e-9)
    bad = []
    for kind, (r, st) in sorted(COMBAT.items()):
        ri = RAR.index(r) + 1
        t = totals(kind, ri, 100)
        tt = dict(t)
        tt["hpp"] = tt.pop("health", 0.0)
        got = BM.p5_dps(tt, caster=tt.get("mp", 0.0) > 0) * BM.p5_ehp(tt)
        want = 1.0 + 0.42 * float(Cfg.factor(ri))
        if abs(math.log(got) - math.log(want)) > 0.05 * math.log(want):
            bad.append((kind, round(got, 3), round(want, 3), t))
        exp = dict((k, v * float(Cfg.factor(ri))) for k, v in st.items())
        if any(abs(t.get(k, 0.0) - v) > 1e-6 for k, v in exp.items()):
            bad.append((kind, "values", t, exp))
    K.check(not bad, "K %d combat kinds at Lv 100 / their start rarity: DPS x EHP = 1 + 0.42 x rarity +- 5 %% (PetBuff.compute): %s" % (len(COMBAT), bad[:3]))
    ram = totals("Ram", 4, 100)
    K.check(abs(ram.get("health", 0) - 12 * 1.45) < 1e-6 and abs(ram.get("def", 0) - 28 * 1.45) < 1e-6, "K Ram Epic Lv 100: Health %.1f %% Defense %.1f (12 / 28 x1.45)" % (ram.get("health", 0), ram.get("def", 0)))
    fk = "fortune.mining"
    m30 = totals("Mouse", 3, 30)
    m100 = totals("Mouse", 6, 100, 5)
    K.check(abs(m30.get(fk, 0) - 88 * 1.3 * 0.3) < 1e-6 and abs(m100.get(fk, 0) - 88 * 1.75 * 1.25) < 1e-6,
            "K a Fortune-only pet (Mouse): Rare Lv 30 = %.1f, Mythic Lv 100 + 5 pet rebirths = %.1f Fortune (no cap)" % (m30.get(fk, 0), m100.get(fk, 0)))
    cm50 = totals("Mouse", 1, 50)
    K.check(abs(cm50.get(fk, 0) - 44.0) < 1e-6, "K test step: a Common Lv 50 Mouse gives 44 Mining Fortune (%.1f)" % cm50.get(fk, 0))
    g = totals("Goat", 2, 100)
    K.check(abs(g.get(fk, 0) - 70 * 1.15) < 1e-6 and abs(g.get("swing.mining", 0) - min(7.0, float(Cfg.SWING_CAP)) * 1.15) < 1e-6,
            "K a two-stat kind (Goat Uncommon Lv 100): Fortune 70 x1.15, its swing 7 unchanged (still under pets.swing.cap %s x1.15): %s" % (float(Cfg.SWING_CAP), g))
    cg = totals("CrystalGolem", 4, 100)
    K.check(abs(cg.get(fk, 0) - 70 * 1.45) < 1e-6, "K a 0.4.3 roster kind (Crystal Golem, built-in line) moved too: %s" % cg)
    Cfg.FORT_CAP = 10.0
    capped = totals("Mouse", 6, 100, 5)
    K.check(abs(capped.get(fk, 0) - 10.0 * 1.75 * 1.25) < 1e-6, "K a Fortune cap set by hand (10) still clips: %.2f (x capMult)" % capped.get(fk, 0))
    Cfg.FORT_CAP = 0.0
    hid = [str(k.id) for k in Cfg.KINDS]
    K.check(all(x in hid for x in list(COMBAT) + FORT_ONLY + FORT_TWO), "K every planned kind is loaded (%d kinds)" % len(hid))
    W["K"].save()


def fake_stats(JClass, names=("Health", "Oxygen", "Stamina", "Mana", "SignatureEnergy", "Ammo")):
    """a bare JVM has no EntityStatType asset store: one with the six default stats (min / max 0; the test's MAX modifiers give the max)"""
    from jpype import JInt, JArray, JImplements, JOverride, JObject, JString
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    US = uf.get(None)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fk = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestStatStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fk.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyTestStatStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fk))
    FKC = fk.toClass(AS.class_)

    def fld(c, n):
        f = c.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f
    C = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")

    @JImplements("java.util.function.IntFunction")
    class Arr(object):
        @JOverride
        def apply(self, n):
            return JArray(C)(int(n))
    m = ILT(Arr())
    arr = JArray(C)(len(names))
    kti = fld(ILT, "keyToIndex").get(m)
    for i, n in enumerate(names):
        o = US.allocateInstance(C.class_)
        fld(C, "id").set(o, JString(n))
        arr[i] = o
        kti.put(JObject(JString(n), JClass("java.lang.Object")), JInt(i))
    fld(ILT, "array").set(m, arr)
    fld(ILT, "nextIndex").set(m, JClass("java.util.concurrent.atomic.AtomicInteger")(len(names))) if "AtomicInteger" in str(fld(ILT, "nextIndex").getType()) else fld(ILT, "nextIndex").setInt(m, JInt(len(names)))
    st = US.allocateInstance(FKC)
    fld(AS, "tClass").set(st, C.class_)
    fld(AS, "assetMap").set(st, m)
    fld(JClass("com.hypixel.hytale.assetstore.AssetRegistry"), "storeMap").get(None).put(C.class_, st)
    fld(C, "ASSET_STORE").set(None, st)
    JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes").update()


def run_pct(out, jar, scratch, _home):
    from jpype import JClass, JInt, JFloat, JDouble, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Buff = JClass(PKG + "PetBuff")
    Kind = JClass(PKG + "PetKind")
    fake_stats(JClass)
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    HPI, MNI = int(DST.getHealth()), int(DST.getMana())
    m = ESM()
    m.update()
    m.putModifier(JInt(HPI), "pet048test", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(100.0)))
    m.putModifier(JInt(MNI), "pet048test", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(50.0)))
    hp0, mn0 = float(m.get(JInt(HPI)).getMax()), float(m.get(JInt(MNI)).getMax())
    keys = [str(x) for x in Kind.STAT_KEYS]
    JArr = JClass("double[]") if False else None
    from jpype import JArray
    t = JArray(JDouble)(len(keys))
    t[keys.index("health")] = 12.0
    t[keys.index("mana")] = 20.0

    def amt(i):
        c = m.getModifier(JInt(i), "skyypet_health" if i == HPI else "skyypet_mana")
        return None if c is None else float(c.getAmount())
    Buff.stats(m, t)
    a1, b1 = amt(HPI), amt(MNI)
    Buff.stats(m, t)
    a2 = amt(HPI)
    K.check(abs(a1 - 0.12 * hp0) < 0.02 and abs(b1 - 0.20 * mn0) < 0.02 and abs(a2 - a1) < 0.01,
            "PCT PetBuff.stats: Health +12 %% of the max without it (%.2f of %.1f), Mana +20 %% (%.2f of %.1f); the next second the same (no compounding: %.2f)" % (a1, hp0, b1, mn0, a2))
    K.check(abs(float(m.get(JInt(HPI)).getMax()) - (hp0 + a1)) < 0.05, "PCT the max Health reads base + the modifier (%.2f)" % float(m.get(JInt(HPI)).getMax()))
    t[keys.index("health")] = 6.0
    Buff.stats(m, t)
    K.check(abs(amt(HPI) - 0.06 * hp0) < 0.02, "PCT the pct going DOWN (12 -> 6) lowers at once: %.2f" % amt(HPI))
    # the max without us shrinks (another modifier drops): the lower value waits LOW_MS, then lands
    m.putModifier(JInt(HPI), "pet048test", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(50.0)))
    now = 10_000_000
    Buff.modPct(m, JInt(HPI), "skyypet_health", JDouble(6.0), JLong(now))
    w1 = amt(HPI)
    Buff.modPct(m, JInt(HPI), "skyypet_health", JDouble(6.0), JLong(now + 1000))
    w2 = amt(HPI)
    Buff.modPct(m, JInt(HPI), "skyypet_health", JDouble(6.0), JLong(now + 3500))
    w3 = amt(HPI)
    base2 = float(m.get(JInt(HPI)).getMax()) - w3
    K.check(abs(w1 - 0.06 * hp0) < 0.02 and abs(w2 - w1) < 1e-6 and abs(w3 - 0.06 * base2) < 0.02 and w3 < w1,
            "PCT the base shrinking waits 3 s (%.2f, %.2f after 1 s), then lowers (%.2f = 6 %% of %.1f)" % (w1, w2, w3, base2))
    t[keys.index("health")] = 0.0
    t[keys.index("mana")] = 0.0
    Buff.stats(m, t)
    K.check(amt(HPI) is None and amt(MNI) is None, "PCT pct 0 removes both modifiers")
    K.check(float(Buff.pctWant(JFloat(100.0), JFloat(0.0), JDouble(-200.0))) >= -90.0, "PCT a negative pct never takes more than 90 %% of the max")
    # fix round (critic: Health / Mana % compounding): % of the FLAT max = type max + flat additive modifiers; the other mods' % layers ignored
    ET = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    hf = ET.class_.getDeclaredField("max")
    hf.setAccessible(True)
    hf.setFloat(ET.getAssetMap().getAsset(JInt(HPI)), JFloat(100.0))
    hf.setFloat(ET.getAssetMap().getAsset(JInt(MNI)), JFloat(40.0))
    m2 = ESM()
    m2.update()
    for k_, v_ in (("Armor", 50.0), ("skyygear_hp", 40.0), ("skyyacc_health", 30.0), ("skyyskill_classhp", 10.0)):
        m2.putModifier(JInt(HPI), k_, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(v_)))
    for k_, v_ in (("skyyskill_mana_pool", 60.0), ("skyyacc_mana", 25.0), ("skyyskill_rebirthmana", 8.0)):
        m2.putModifier(JInt(MNI), k_, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(v_)))
    K.eq((round(float(Buff.flatMax(m2.get(JInt(HPI)), JInt(HPI))), 2), round(float(Buff.flatMax(m2.get(JInt(MNI)), JInt(MNI))), 2)), (150.0, 100.0),
         "PCT fix: flatMax Health = 100 + Armor 50, Mana = 40 + a flat pool 60 (Gear / Accessories / Skills %% layers skipped)")
    t[keys.index("health")] = 10.0
    t[keys.index("mana")] = 20.0
    for i_ in range(5):
        Buff.stats(m2, t)
    h2 = float(m2.getModifier(JInt(HPI), "skyypet_health").getAmount())
    n2 = float(m2.getModifier(JInt(MNI), "skyypet_mana").getAmount())
    K.check(abs(h2 - 15.0) < 0.02 and abs(n2 - 20.0) < 0.02, "PCT fix: Health 10 %% = 15 of the 150 flat max, Mana 20 %% = 20 of the 100 flat max, steady with the other %% layers on (%.2f, %.2f)" % (h2, n2))
    hf.setFloat(ET.getAssetMap().getAsset(JInt(HPI)), JFloat(0.0))
    hf.setFloat(ET.getAssetMap().getAsset(JInt(MNI)), JFloat(0.0))
    K.save()


def run_xp(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "xp")
    K, JClass = W["K"], W["JClass"]
    P_ = lambda n: JClass(PKG + n)
    Xp = P_("PetXp")
    u, k, r = T44._mk(W, 900)
    for kk, vv in (("kind", "Mouse"), ("rarity", "1"), ("level", "40")):          # Lv 40: the next level needs 9,920 XP - no level-up eats the test XP
        r.set("pet.m1.%s" % kk, vv)
    r.set("active.1", "m1")
    x0 = float(r.xpOf("m1")) if hasattr(r, "xpOf") else None
    Xp.give(u, "Mining", 1000)
    x1 = float(r.xpOf("m1")) if hasattr(r, "xpOf") else None
    Xp.give(u, "Foraging", 1000)
    x2 = float(r.xpOf("m1")) if hasattr(r, "xpOf") else None
    if x0 is not None:
        K.check(abs((x1 - x0) - 500.0) < 1e-6 and abs((x2 - x1) - 50.0) < 1e-6, "XP PetXp.give: Mining 1000 -> +%.0f pet XP (50 %%), Foraging 1000 -> +%.0f (5 %%), no P3 divisor" % (x1 - x0, x2 - x1))
    else:
        tot = str(r.get("pet.m1.xp"))
        K.check(tot in ("550", "550.0"), "XP PetXp.give: Mining 1000 + Foraging 1000 -> pet XP 550 (50 %% + 5 %%; no divisor): %s" % tot)
    t50, _l = BM.p5_pet_xp_trace("Mining")
    t50c, _c = BM.p5_pet_xp_trace("Class")
    K.check(t50 is not None and 28 <= t50 <= 33 and t50c is not None and 28 <= t50c <= 33,
            "XP pace (tools/balance_model.py, P3 player): Mining pet Lv 50 at %.1f h, combat pet at %.1f h (target 28-33)" % (t50 or -1, t50c or -1))
    W["K"].save()


def run_mig(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Mg, Log = P_("PetsMigP5"), P_("PetsLog")
    Log.LINES = JClass("java.util.ArrayList")()
    keys, olds, news = [str(x) for x in Mg.KEYS], [str(x) for x in Mg.OLDS], [str(x) for x in Mg.NEWS]
    ns = int(Mg.NS)
    K.eq((ns, len(keys)), (9, 42), "MIG 9 scalar rows + 33 kind lines")
    src = "\n".join(["# x"] + ["%s=%s" % (k, o) for k, o in zip(keys, olds)] + ["other=1", ""])

    def upd(t):
        r = Mg.mgUpdate(JString(t))
        return str(r[0]), int(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]]
    t1, n1, no1, d1 = upd(src)
    K.check(n1 == 42 and not no1 and t1 == "\n".join(["# x"] + ["%s=%s" % (k, n) for k, n in zip(keys, news)] + ["other=1", ""]),
            "MIG a 0.4.7 default file: every planned line moves, nothing else (%d)" % n1)
    t2, n2, _no2, _d2 = upd(src.replace("\n", "\r\n"))
    K.check(n2 == 42 and t2 == t1.replace("\n", "\r\n"), "MIG CRLF kept")
    h = src.replace("pets.rarity.mythic=1.5", "pets.rarity.mythic=2").replace("pets.xp.p3=true", "pets.xp.p3=TRUE")
    t3, n3, no3, _d3 = upd(h)
    K.check(n3 == 41 and "pets.rarity.mythic=2\n" in t3 and "pets.xp.p3=false" in t3 and len(no3) == 1 and "pets.rarity.mythic=2" in no3[0],
            "MIG hand-edited mythic 2 kept + noted, 'TRUE' counts as the old default: %s" % no3)
    ki = keys.index("kind.Ram")
    t4, n4, no4, _d4 = upd(src.replace(keys[ki] + "=" + olds[ki], keys[ki] + "=Combat/Epic/def:5"))
    K.check(n4 == 41 and "kind.Ram=Combat/Epic/def:5" in t4 and len(no4) == 1, "MIG a hand-edited kind kept + noted")
    K.check(upd(src.replace("pets.xp.ownPercent=100", "pets.xp.ownPercent=1\\\n00"))[1] == 41, "MIG a continued line is kept")
    K.eq(upd("a=1\n")[1], 0, "MIG no planned line = nothing")
    old_b = src.encode("latin-1")
    K.check(bool(Mg.sameAfter(old_b, t1.encode("latin-1"))) and not bool(Mg.sameAfter(old_b, (t1 + "extra=1\n").encode("latin-1"))),
            "MIG sameAfter: the planned change passes, an extra key is refused")
    d = os.path.join(scratch, "mig-run", "Skyy_SkyyPets")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "config.properties"), "wb").write(old_b)
    Paths = JClass("java.nio.file.Paths")
    m1 = str(Mg.run(Paths.get(d)))
    K.check("Balance P5 power (SkyyPets 0.4.8)" in m1 and os.path.isfile(os.path.join(d, "migrations", "pets-p5.done"))
            and open(os.path.join(d, "config.properties"), "rb").read() == t1.encode("latin-1"), "MIG run(): file updated, marker written: %s" % m1[:160])
    lg = open(os.path.join(d, "config-changes.log"), encoding="utf-8").read()
    K.check(lg.count("\tSkyyPets 0.4.8\t-\tupdate\t") == 9 and lg.count("\tupdate\tpets.kinds[") == 33, "MIG 9 + 33 change-log lines")
    K.check(str(Mg.run(Paths.get(d))) == "", "MIG second run = nothing (marker)")
    d2 = os.path.join(scratch, "mig-fresh", "Skyy_SkyyPets")
    os.makedirs(d2, exist_ok=True)
    K.check("defaults apply" in str(Mg.run(Paths.get(d2))) and os.path.isfile(os.path.join(d2, "migrations", "pets-p5.done")), "MIG a fresh home: marker only")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Mig, Mig2, MgP5, Log = P_("PetsCfg"), P_("PetStore"), P_("PetsCfgMig"), P_("PetsCfgMig2"), P_("PetsMigP5"), P_("PetsLog")
    Paths = JClass("java.nio.file.Paths")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.dirname(home)
    fc = os.path.join(home, "config.properties")
    lp = os.path.join(home, "config-changes.log")
    l0 = open(lp, "rb").read() if os.path.isfile(lp) else b""

    def start():
        Mig.run(Paths.get(home))
        Mig2.run(Paths.get(home))
        mid = open(fc, "rb").read()
        r = str(MgP5.run(Paths.get(home)))
        Cfg.load(Paths.get(mods))
        Store.ROOT = Paths.get(home)
        Store.DIR = Store.ROOT.resolve("pets")
        return mid, r, [int(x) for x in Store.scanAll()]
    mid, r1, sc1 = start()
    new = open(fc, "rb").read()
    print("   live PetsMigP5:", r1[:240])
    po, pn = _props(mid), _props(new)
    ch = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    keys, news = [str(x) for x in MgP5.KEYS], [str(x) for x in MgP5.NEWS]
    K.check(set(ch) <= set(keys) and all(pn[k] == news[keys.index(k)] for k in ch), "LIVE only planned keys change, each to its new value (%d changed)" % len(ch))
    K.check(len([c for c in ch if c.startswith("kind.")]) == 27 and "pets.rarity.mythic" in ch and "pets.xp.ownPercent" in ch and "pets.fortune.cap" in ch,
            "LIVE the 27 kind lines (31 in the file, the 4 Exploration kinds stay) + rarity / cap / XP rows of Skyy's file moved: %s" % [c for c in ch if not c.startswith("kind.")])
    K.check(any(open(os.path.join(rr, f_), "rb").read() == mid for rr, _d, fs in os.walk(os.path.join(home, "config-history")) for f_ in fs),
            "LIVE the History copy holds the file before the P5 update")
    lg = open(lp, "rb").read()[len(l0):].decode("utf-8")
    K.eq(lg.count("\tSkyyPets 0.4.8\t-\tupdate\t") + lg.count("\tupdate\tpets.kinds["), len(ch), "LIVE one change-log line per changed key")
    K.check(sc1[2] == 0 and sc1[3] == 0, "LIVE every pet file reads (%s)" % sc1)
    K.check(abs(float(Cfg.factor(6)) - 1.75) < 1e-9 and abs(float(Cfg.FORT_CAP)) < 1e-12 and int(Cfg.XP_OWN) == 50, "LIVE the loader reads the P5 values")
    t1 = T41.tree(home)
    _m2, r2, sc2 = start()
    K.check(r2 == "" and T41.tree(home) == t1 and sc2 == sc1, "LIVE start 2 writes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("kinds", run_kinds), ("pct", run_pct), ("xp", run_xp), ("mig", run_mig), ("live", run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
