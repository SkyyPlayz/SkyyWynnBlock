"""Harness for SkyyArmory 0.1.28 (THE SPELLBLADE SWORD: Crescent Rush, the run-time sword guard, the Spellblade sword bonus;
tools/armory_0_1_28_patch.py). Build first:
    python tools/armory_0_1_28_patch.py && python SkyyArmory/build_skyyarmory_0.1.28.py

    python SkyyArmory/test_skyyarmory_0.1.28.py [--jar <SkyyArmory-0.1.28.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  T   assets   FROM THE JAR: the Longsword_Stab_Charged override = the vanilla file (Assets.zip, read now) with its Next turned into
               Parallel [launch the marker, EffectCondition(the never-applied effect) -> the vanilla Next byte for byte]; the marker =
               the blink marker shape; the hidden effect; the guard root / entry / wield (120 degrees, x0.5 melee, x0.7 move, 0.1 s raise,
               the vanilla sword guard's Stamina rule); no item file and no other longsword file shipped; SkyyGear's longsword tier copies
               charge into the overridden id; the default config file carries the 16 new rows with their defaults
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.27 -> 0.1.28: exactly the listed members differ (version texts normalised), Rush + ArmoryItemL added; non-class: the
               manifest + the 6 new files only; the hooks call Rush (KunaiJob.run kind 4, ArmoryTrav.added, ArmoryTuneSys.handle,
               TravTick.tick, the plugin start / setup)
  X   exec     EVERY NEW CODE PATH without a world: Momentum from a class:fn:abil stand-in (and junk / a throw / none),
               the dash length + direction (pitch limit, straight up = none), the hit
               rule on many geometries (sweep arc / behind / path / crescent below + above the Momentum gate / once per enemy), the
               Spellblade bonus rule (+ the class bridge, the ability-damage bridge), the guard map (EnumMap + HashMap, a Secondary kept,
               not a longsword), the guard on a REAL engine Item object (reflection write + packet cache), NPC copies skipped, the guard
               switch off, guardAll / onLoaded / filter / tickPlayer / KunaiJob kind 4 without a world (no throw, the right reason),
               the sword / hit caches, the marker code, the config loader (defaults, clamps), the status text
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory: the 2nd start changes nothing, 0.1.28 does not rewrite the file
  AA  audit    the engine-access audit
The engine-backed parts (the item packets reaching the client, the teleport, hits through the damage pipeline, SkyyClasses Momentum /
Imbue on the hits, Perfect Parries) need the game - the in-game steps. Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.28", "0.1.27"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "armory0128", "armory")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyArmory")
RUSH_VIA = "Longsword_Stab_Charged"
P_VIA = "Server/Item/Interactions/Weapons/Longsword/Attacks/Stab_Charged/Longsword_Stab_Charged.json"
NEW_FILES = sorted(["Server/Entity/Effects/SkyyArmory/SkyyArmory_Rush_Vanilla.json", P_VIA,
                    "Server/Item/Interactions/Weapons/Longsword/SkyyArmory/SkyyArmory_Longsword_Guard_Entry.json",
                    "Server/Item/Interactions/Weapons/Longsword/SkyyArmory/SkyyArmory_Longsword_Guard_Wield.json",
                    "Server/Item/RootInteractions/Weapons/Longsword/SkyyArmory/SkyyArmory_Longsword_Guard.json",
                    "Server/Projectiles/Player/SkyyArmory/SkyyArmory_Crescent_Rush.json"])
CFG_FIELDS = ["RUSH_ON", "RUSH_DIST", "RUSH_PERMOM", "RUSH_SWEEP", "RUSH_REACH", "RUSH_ARC", "RUSH_PATH", "RUSH_CRAT", "RUSH_CRES",
              "RUSH_CRANGE", "RUSH_CWID", "RUSH_MANA", "RUSH_STAM", "RUSH_HFALL", "BLADE_PCT", "GUARD_ON"]
# the members 0.1.28 changes (version texts normalised to VER)
EXPECT = {"ArmoryDefs": ["+f RUSH_CODE", "+f RUSH_MARK", "~<clinit>", "~m pids"],
          "ArmoryCfg": ["+f BLADE_TEXT", "+f GUARD_SET", "+f GUARD_NEXT"] + ["+f " + f for f in CFG_FIELDS] + ["+m bladeText", "~<clinit>", "~m apply",
                        "~m load", "~m reloadAll", "~m useDefaults"],          # these 3 inline DEF_CFG (the default file text grew)
          "ArmoryHooks": ["~<clinit>"], "ArmoryTrav": ["~m added"], "KunaiJob": ["~m run"], "ArmoryTuneSys": ["~m handle"],
          "TravTick": ["~m tick"], "CfgRows": ["~<clinit>"], "CfgFile": ["~<clinit>"],          # the kit: the rows + the default file text
          "SkyyArmoryPlugin": ["+m start", "~m publish", "~m setup", "~m shutdown", "~m unpublish"]}
ADDED = ["Rush", "ArmoryItemL"]


def jread(z, n):
    return json.loads(z.read(n).decode("utf-8-sig"))


# ---------------------------------------------------------------------------------------------------- T: the assets (parent, no JVM)
def run_assets():
    AZ = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    with zipfile.ZipFile(JAR) as z:
        names = z.namelist()
        ov = jread(z, P_VIA)
        van = jread(AZ, P_VIA)
        HK.check(ov["Type"] == "Simple" and ov["Effects"]["ItemAnimationId"] == "StabCharged" and ov["RunTime"] == 0
                 and ov["Effects"].get("WorldSoundEventId") == "SFX_Longsword_Special_Swing",
                 "T1: the override keeps the vanilla StabCharged pose + a swing sound on release")
        br = ov["Next"]["Interactions"]
        HK.check(ov["Next"]["Type"] == "Parallel" and len(br) == 2, "T1: the release = a 2-branch Parallel (a 1-entry Parallel fails validation)")
        la = br[0]["Interactions"][0]
        HK.check(la["Type"] == "LaunchProjectile" and la["ProjectileId"] == "SkyyArmory_Crescent_Rush", "T1: branch 1 launches the Crescent Rush marker")
        ec = br[1]["Interactions"][0]
        HK.check(ec["Type"] == "EffectCondition" and ec["Match"] == "All" and ec["EntityEffectIds"] == ["SkyyArmory_Rush_Vanilla"] and "Failed" not in ec,
                 "T1: branch 2 = EffectCondition on the hidden effect, no Failed")
        HK.check(ec["Next"] == van["Next"], "T1: ... whose Next is the vanilla stab EXACTLY (the damage breakdown - SkyyGear's K + tooltip - unchanged)")
        HK.check(dict((k, v) for k, v in ov.items() if k not in ("Next", "Effects")) == dict((k, v) for k, v in van.items() if k not in ("Next", "Effects")),
                 "T1: every other field of the vanilla file kept")
        eff = jread(z, "Server/Entity/Effects/SkyyArmory/SkyyArmory_Rush_Vanilla.json")
        HK.check(eff == jread(z, "Server/Entity/Effects/SkyyArmory/SkyyArmory_Speed_Slow.json"), "T2: the hidden effect = the SkyyArmory_Speed_* marker shape")
        blob = b"".join(z.read(n) for n in names if n.endswith(".class"))
        HK.check(b"SkyyArmory_Rush_Vanilla" not in blob, "T2: no Java code ever applies the hidden effect (the vanilla stab can never run)")
        mk = jread(z, "Server/Projectiles/Player/SkyyArmory/SkyyArmory_Crescent_Rush.json")
        bm = jread(z, "Server/Projectiles/Player/SkyyArmory/SkyyArmory_Blink_Copper.json")
        HK.check(mk == bm, "T3: the marker = the staff blink marker shape (invisible, harmless, Damage 0)")
        root = jread(z, "Server/Item/RootInteractions/Weapons/Longsword/SkyyArmory/SkyyArmory_Longsword_Guard.json")
        HK.check(root == {"RequireNewClick": True, "Interactions": ["SkyyArmory_Longsword_Guard_Entry"], "Tags": {"Attack": ["Melee"]}},
                 "T4: the guard root = the vanilla sword guard root shape (no Rules: the primary hold is never interrupted)")
        en = jread(z, "Server/Item/Interactions/Weapons/Longsword/SkyyArmory/SkyyArmory_Longsword_Guard_Entry.json")
        ser = en["Next"]["Next"]["Interactions"]
        HK.check(en["Type"] == "StatsCondition" and en["Costs"] == {"Stamina": 0.5} and en["Next"]["EntityEffectIds"] == ["Stamina_Broken"]
                 and en["Next"]["Match"] == "None" and ser[0] == {"Type": "ChangeStat", "StatModifiers": {"Stamina": -0.5}}
                 and ser[1]["RunTime"] == 0.1 and ser[1]["Effects"]["ItemAnimationId"] == "Guard" and ser[2] == "SkyyArmory_Longsword_Guard_Wield"
                 and en["Failed"] == "Common_Stamina_Insufficient" and en["Next"]["Failed"] == "Common_Stamina_Insufficient",
                 "T4: the entry: 0.5 Stamina, no guard while Stamina-broken, a 0.1 s raise, then the wield")
        wi = jread(z, "Server/Item/Interactions/Weapons/Longsword/SkyyArmory/SkyyArmory_Longsword_Guard_Wield.json")
        vw = jread(AZ, "Server/Item/Interactions/Weapons/Sword/Attacks/Secondary/Guard/Weapon_Sword_Secondary_Guard_Wield.json")
        aw = wi["AngledWielding"]
        HK.check(wi["Type"] == "Wielding" and aw["Angle"] == 0 and aw["AngleDistance"] == 60
                 and aw["DamageModifiers"] == {"Physical": 0.5, "Slashing": 0.5, "Bludgeoning": 0.5}
                 and aw["KnockbackModifiers"] == {"Physical": 0.5, "Slashing": 0.5, "Bludgeoning": 0.5}
                 and "DamageModifiers" not in wi and wi["HorizontalSpeedMultiplier"] == 0.7,
                 "T4: the wield: 120 degrees in front, melee damage + knockback x0.5, projectiles / behind untouched, move x0.7")
        HK.check(wi["StaminaCost"] == vw["StaminaCost"] and wi["BlockedEffects"] == vw["BlockedEffects"] and wi["Next"] == vw["Next"]
                 and wi["Effects"] == vw["Effects"] and wi["Forks"] == {"Primary": {"Interactions": ["Common_Guard_Shove_Animation"]}},
                 "T4: the vanilla sword guard's Stamina rule / blocked effects / pose / regen delay; left click = the 0-damage shove")
        HK.check(not [n for n in names if n.startswith("Server/Item/Items/") and "ongsword" in n] and
                 [n for n in names if "/Longsword/" in n and "/SkyyArmory/" not in n] == [P_VIA],
                 "T5: no longsword ITEM file shipped (the guard is added at run time); exactly one vanilla longsword file overridden")
        HK.check(not [n for n in names if "Zweihander" in n or "/Mace/" in n], "T5: nothing of the mace chain / Zweihander touched")
        # SkyyGear (the SET pin) charges into the overridden id
        sset = open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()
        gpin = dict(re.findall(r'\("(Skyy\w+)", "([0-9][0-9.]*)"\)', sset[sset.index("SET = ["):])).get("SkyyGear")
        gj = os.path.join(ROOT, "SkyyGear", "SkyyGear-%s.jar" % gpin)
        if os.path.isfile(gj):
            with zipfile.ZipFile(gj) as g:
                ls = [n for n in g.namelist() if n.endswith("_Longsword_Longsword_Attack.json")]
                HK.check(len(ls) == 3 and all(jread(g, n)["Next"]["1.565"] == RUSH_VIA for n in ls)
                         and not [n for n in g.namelist() if n.endswith("/" + RUSH_VIA + ".json")],
                         "T6: SkyyGear %s's 3 longsword tier copies charge into %s and it ships no copy of it" % (gpin, RUSH_VIA))
        vla = jread(AZ, "Server/Item/Interactions/Weapons/Longsword/Variants/Longsword_Attack.json")
        HK.check(vla["Next"]["1.565"] == RUSH_VIA, "T6: the vanilla Longsword_Attack charges into it too")
    AZ.close()


# ---------------------------------------------------------------------------------------------------- C: class compare
def run_compare(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(OLD_JAR), pool_of(jar)

    def code(b_):
        mi_ = b_.getMethodInfo()
        ca_ = mi_.getCodeAttribute()
        if ca_ is None:
            return ""
        it_ = ca_.iterator()
        cpl_ = mi_.getConstPool()
        lines_ = []
        while it_.hasNext():
            pos_ = it_.next()
            ln_ = re.sub(r"^ldc_w ", "ldc ", re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))))
            ln_ = re.sub(r"^((?:if\w*|goto(?:_w)?|jsr(?:_w)?)) -?\d+$", r"\1", ln_)
            lines_.append(ln_.replace(VERSION, "VER").replace(OLD, "VER"))
        return str(b_.getModifiers()) + "\n" + "\n".join(lines_)

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature()) + " " + str(f_.getModifiers())
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_
    na, nb = HK.jar_classes(OLD_JAR), HK.jar_classes(jar)
    K.eq(sorted(set(nb) - set(na)), sorted(PKG + a for a in ADDED), "C: classes added")
    K.eq(sorted(set(na) - set(nb)), [], "C: classes removed")
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = sorted(("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd)
    print("C. class compare %s -> %s: %d classes differ" % (OLD, VERSION, len(diffs)))
    for k in sorted(diffs):
        print("   %-22s %s" % (k, ", ".join(diffs[k])))
    K.eq(sorted(diffs), sorted(EXPECT), "C: the classes that differ")
    for k in sorted(EXPECT):
        K.eq(sorted(diffs.get(k, [])), sorted(EXPECT[k]), "C: %s members" % k)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    K.eq(sorted(eb - ea), NEW_FILES, "C: non-class entries added = the 6 Crescent Rush / guard files")
    K.eq(sorted(ea - eb), [], "C: non-class entries removed")
    K.eq(sorted(n for n in ea & eb if za.read(n) != zb.read(n)), ["manifest.json"], "C: non-class entries changed = the manifest only")

    def calls(cls, mname, target):
        c_ = pb.get(PKG + cls)
        for m_ in c_.getDeclaredMethods():
            if str(m_.getName()) != mname:
                continue
            ca = m_.getMethodInfo().getCodeAttribute()
            it_ = ca.iterator()
            cpl_ = m_.getMethodInfo().getConstPool()
            while it_.hasNext():
                pos_ = it_.next()
                if target in str(IP.instructionString(it_, pos_, cpl_)):
                    return True
        return False
    K.check(calls("KunaiJob", "run", "Rush.dash"), "C: KunaiJob.run kind 4 -> Rush.dash")
    K.check(calls("ArmoryTrav", "added", "Rush.marker"), "C: ArmoryTrav.added (the marker's SPAWN) -> Rush.marker")
    K.check(calls("ArmoryTuneSys", "handle", "Rush.filter"), "C: ArmoryTuneSys.handle -> Rush.filter (the sword bonus)")
    K.check(calls("TravTick", "tick", "Rush.tickPlayer"), "C: TravTick.tick -> Rush.tickPlayer (the hits)")
    K.check(calls("SkyyArmoryPlugin", "start", "Rush.guardAll"), "C: the plugin's start() -> Rush.guardAll")
    K.check(calls("SkyyArmoryPlugin", "setup", "ArmoryItemL") and calls("SkyyArmoryPlugin", "setup", "EventRegistry.register"),
            "C: setup registers the item reload listener")
    K.check(calls("Rush", "dash", "TravMath.scanL") and not calls("Rush", "dash", "TravMath.scan("), "C: the dash scans with scanL (blocks only)")
    K.check(calls("Rush", "dash", "Leap.take") and calls("Rush", "dash", "ArmoryTrav.allowed") and calls("Rush", "dash", "Kunai.arena"),
            "C: the dash pays (Leap.take), keeps the class lock and the locked-arena rule")
    K.check(calls("Rush", "strike", "DamageSystems.executeDamage") or calls("Rush", "hit", "DamageSystems.executeDamage"), "C: hits go through the damage pipeline")

    def first(cls, mname, target):
        c_ = pb.get(PKG + cls)
        for m_ in c_.getDeclaredMethods():
            if str(m_.getName()) != mname:
                continue
            ca = m_.getMethodInfo().getCodeAttribute()
            it_ = ca.iterator()
            cpl_ = m_.getMethodInfo().getConstPool()
            while it_.hasNext():
                pos_ = it_.next()
                if target in str(IP.instructionString(it_, pos_, cpl_)):
                    return int(pos_)
        return -1
    K.check(calls("Rush", "strike", "Shadow.attitude") and calls("Rush", "strike", "Rush.foe") and calls("Rush", "strike", "Shadow.protect"),
            "C (fix 1): strike asks Rush.foe with the engine attitude (Shadow.attitude) and Shadow.protect - friendly mobs never hit")
    fa, ft = first("Rush", "dash", "Kunai.arena"), first("Rush", "dash", "Leap.take")
    K.check(0 <= fa < ft, "C (fix 2): the locked-arena check runs BEFORE the cost (Kunai.arena at %d, Leap.take at %d)" % (fa, ft))
    K.check(calls("SkyyArmoryPlugin", "shutdown", "ArmoryCfg.GUARD_SET"), "C (fix 3): shutdown resets the guard latch")
    K.save()


# ---------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    R = JClass(PKG + "Rush")
    Cfg = JClass(PKG + "ArmoryCfg")
    Defs = JClass(PKG + "ArmoryDefs")
    UUID = JClass("java.util.UUID")
    br = Defs.bridge()
    U = UUID.randomUUID()

    @JImplements("java.util.function.Function")
    class Fn:
        def __init__(self, f): self.f = f

        @JOverride
        def apply(self, o): return self.f(o)
    Cfg.useDefaults()
    K.eq([float(Cfg.RUSH_DIST), float(Cfg.RUSH_PERMOM), float(Cfg.RUSH_SWEEP), float(Cfg.RUSH_REACH), int(Cfg.RUSH_ARC), float(Cfg.RUSH_PATH),
          int(Cfg.RUSH_CRAT), float(Cfg.RUSH_CRES), float(Cfg.RUSH_CRANGE), float(Cfg.RUSH_CWID), float(Cfg.RUSH_MANA),
          float(Cfg.RUSH_STAM), float(Cfg.RUSH_HFALL), int(Cfg.BLADE_PCT), bool(Cfg.GUARD_ON), bool(Cfg.RUSH_ON)],
         [6.0, 0.15, 1.5, 4.0, 180, 1.0, 10, 0.8, 8.0, 2.0, 8.0, 4.0, 8.0, 113, True, True], "X0: the defaults (spec: 6 + 0.15 / stack, 1.5 H reach 4 "
         "180 degrees, crescent 0.8 H 8 blocks at 10+, 8 Mana + 4 Stamina, bonus 113)")
    K.check("Crescent Rush on" in str(Cfg.BLADE_TEXT) and "113" in str(Cfg.BLADE_TEXT) and str(br.get("armory:blade")) == str(Cfg.BLADE_TEXT),
            "X0: the blade text + bridge armory:blade: %s" % Cfg.BLADE_TEXT)
    # X1 Momentum (class:fn:abil out[47])
    OA = JArray(JClass("java.lang.Object"))

    def abil(txt, n=48):
        a = OA(n)
        if txt is not None and n > 47:
            a[47] = JString(txt)
        return a
    K.eq([int(R.momOf(abil("Momentum 14 (Unstoppable)"))), int(R.momOf(abil("Momentum 3"))), int(R.momOf(abil(""))), int(R.momOf(abil("Momentum 99"))),
          int(R.momOf(abil("Momentum x"))), int(R.momOf(abil("Momentum 7", 44))), int(R.momOf(None)), int(R.momOf(JString("Momentum 5")))],
         [14, 3, 0, 40, 0, 0, 0, 0], "X1: momOf parses class:fn:abil out[47] (junk / short / null = 0, capped at 40)")
    seen = []
    br.put("class:fn:abil", Fn(lambda o: (seen.append(str(o)), abil("Momentum 20 (Unstoppable)"))[1]))
    K.check(int(R.momentum(U)) == 20 and seen == [str(U)], "X1: momentum(u) asks class:fn:abil with the UUID: %s" % seen)

    def boom(o):
        raise RuntimeError("x")
    br.put("class:fn:abil", Fn(boom))
    K.eq(int(R.momentum(U)), 0, "X1: a throwing bridge = 0 Momentum")
    br.remove("class:fn:abil")
    K.eq(int(R.momentum(U)), 0, "X1: no SkyyClasses = 0 Momentum")
    # X3 the dash
    K.eq([round(float(R.reach(6.0, 0.15, m)), 6) for m in (0, 10, 20, -3)], [6.0, 7.5, 9.0, 6.0], "X3: dash 6 + 0.15 x Momentum (9 at 20, never below 6)")

    def dirr(dx, dy, dz):
        d = R.dir(dx, dy, dz, 25.0)
        return None if d is None else [round(float(x), 6) for x in d]
    t25 = math.tan(math.radians(25.0))
    K.eq(dirr(1.0, 0.0, 0.0), [1.0, 0.0, 0.0], "X3: a level look = straight ahead")
    d2 = dirr(1.0, -1.0, 0.0)
    K.check(d2 is not None and abs(d2[1] / d2[0] + t25) < 1e-6 and abs(math.hypot(*d2) - 1.0) < 1e-6, "X3: 45 degrees down -> 25 degrees down (unit): %s" % d2)
    d3 = dirr(0.0, 0.5, 2.0)
    K.check(d3 is not None and abs(d3[1] / d3[2] - 0.25) < 1e-6, "X3: a small pitch is kept: %s" % d3)
    K.eq([dirr(0.0, 1.0, 0.0), dirr(0.0, -1.0, 0.0), dirr(float("nan"), 0.0, 1.0)], [None, None, None], "X3: straight up / down / NaN = no direction")
    # X4 the hit rule: s = {sx, sy, sz, ex, ey, ez, hx, hz, H, mom, t0, moved}; the dash along +x from 0 to 6, feet at 64
    DA = JArray(JClass("double"))

    def S(mom=0, moved=1.0, ex=6.0):
        return DA([0.0, 64.0, 0.0, ex, 64.0, 0.0, 1.0, 0.0, 8.0, float(mom), 0.0, moved])

    def kind(s, x, z, cres=False, y=64.0, h=1.8, w=0.6):
        return int(R.kindOf(s, x, y + h * 0.5, z, h * 0.5, w * 0.5, cres))
    s0 = S()
    K.eq([kind(s0, 9.0, 0.0), kind(s0, 6.0, 3.5), kind(s0, 6.0, -3.5), kind(s0, 6.2, 0.1), kind(s0, 10.6, 0.0), kind(s0, 6.0, 4.6)],
         [3, 3, 3, 3, 0, 0], "X4: the sweep: ahead 3, both sides at 3.5 (180 degrees), on top of you; 4.6 ahead / 4.6 aside = out of reach")
    K.eq([kind(s0, 3.0, 0.5), kind(s0, 1.0, -0.8), kind(s0, 4.0, 2.5)], [2, 2, 0], "X4: passed on the way (2 blocks wide + half the body): 2; "
         "2.5 off the path behind the dash end = none (the sweep only reaches AHEAD)")
    K.eq(kind(s0, 2.5, 0.0), 2, "X4: behind the dash end, on the path = the path hit (never the sweep: 180 degrees ahead only)")
    K.eq([kind(s0, 13.0, 0.0), kind(s0, 13.0, 0.0, True), kind(s0, 13.0, 1.4, True), kind(s0, 14.4, 0.0, True), kind(s0, 13.0, 0.0, True, 70.0)],
         [0, 1, 0, 0, 0], "X4: the crescent: only with the gate, 2 wide, 8 ahead, not far above")
    K.eq(kind(S(moved=0.0), 1.0, 0.0), 0, "X4: no dash = no path hits (a mob behind you stays untouched)")
    K.eq(kind(S(moved=0.0, ex=0.0), 2.0, 0.0), 3, "X4: no room ahead = the sweep where you stand")
    Cfg.RUSH_ARC = 90
    K.eq([kind(s0, 6.0, 3.5), kind(s0, 8.0, 1.5)], [0, 3], "X4: sweepArc 90: the sides are out, 37 degrees in")
    Cfg.RUSH_ARC = 360
    K.eq(kind(s0, 4.0, 0.0), 3, "X4: sweepArc 360: behind you in reach = the sweep")
    Cfg.RUSH_ARC = 180
    Cfg.RUSH_PATH = 0.0
    K.eq(kind(s0, 1.0, 0.0), 0, "X4: pathHit 0 = no path hits")
    Cfg.RUSH_PATH = 1.0
    K.eq([round(float(R.mult(k)), 6) for k in (3, 2, 1, 0)], [1.5, 1.0, 0.8, 0.0], "X4: hit multipliers sweep 1.5 / path 1.0 / crescent 0.8 (x H)")
    import random
    rnd = random.Random(128)
    bad = []
    for _ in range(3000):
        x, z = rnd.uniform(-6, 18), rnd.uniform(-6, 6)
        cres = rnd.random() < 0.5
        k = kind(s0, x, z, cres)
        dx, dz = x - 6.0, z
        dh = math.hypot(dx, dz)
        want = 0
        if dh <= 4.3 and (dh <= 0.8 or dx / dh >= -1e-9):
            want = 3
        elif x <= 6.0 + 1.3 and ((x >= 0 and abs(z) <= 1.0 + 0.3 + 0.45) or math.hypot(x, z) <= 1.75):
            want = 2
        elif cres and 0 < dx <= 8.3 and abs(z) <= 1.3:
            want = 1
        if want != k and not (want == 2 and k == 0 and abs(abs(z) - 1.75) < 0.05):
            bad.append((round(x, 2), round(z, 2), cres, k, want))
    K.check(len(bad) <= 30, "X4: 3000 random enemies classified like the rule (sweep > path > crescent; edge cases only): %d off %s" % (len(bad), bad[:4]))
    # X5 the Spellblade bonus
    K.eq([round(float(R.bonus(JString("Spellblade"), True, False, False)), 6), float(R.bonus(JString("Warrior"), True, False, False)),
          float(R.bonus(JString("Spellblade"), False, False, False)), float(R.bonus(JString("Spellblade"), True, True, False)),
          float(R.bonus(JString("Spellblade"), True, False, True)), float(R.bonus(None, True, False, False)), round(float(R.bonus(JString(" spellblade "), True, False, False)), 6)],
         [1.13, 1.0, 1.0, 1.0, 1.0, 1.0, 1.13], "X5: x1.13 only for a Spellblade's own sword melee hit (no projectile, no ability damage)")
    Cfg.BLADE_PCT = 100
    K.eq(float(R.bonus(JString("Spellblade"), True, False, False)), 1.0, "X5: blade.damagePercent 100 = off")
    Cfg.BLADE_PCT = 113
    br.put("class:" + str(U), JString("Spellblade"))
    K.eq(str(R.classOf(U)), "Spellblade", "X5: classOf reads the class:<uuid> bridge key")
    br.remove("class:" + str(U))
    K.eq(R.classOf(U), None, "X5: no key = no class")
    br.put("class:fn:abilhit", Fn(lambda o: U if str(o) == "ab" else None))
    K.check(bool(R.ability(JString("ab"))) and not bool(R.ability(JString("weapon"))), "X5: ability(d) = class:fn:abilhit names a caster")
    br.put("class:fn:abilhit", Fn(boom))
    K.check(not bool(R.ability(JString("ab"))), "X5: a throwing abilhit = a weapon hit (no throw)")
    br.remove("class:fn:abilhit")
    R.filter(None, None)
    K.ok += 1
    # X5b (fix 1): who a rush hit may land on - players (kind already judged PvP / party); mobs only unprotected AND Hostile (0) / Neutral (1)
    K.eq([bool(R.foe(False, False, 0)), bool(R.foe(False, False, 1)), bool(R.foe(False, False, 2)), bool(R.foe(False, True, 0)),
          bool(R.foe(True, False, 2)), bool(R.foe(True, True, 2))],
         [True, True, False, False, True, True], "X5b (fix 1): foe: hostile + neutral mobs yes, FRIENDLY / Revered / Ignore (2) never, protected never, players by kind")
    # X6 the guard map
    IT = JClass("com.hypixel.hytale.protocol.InteractionType")
    EM = JClass("java.util.EnumMap")
    HM = JClass("java.util.HashMap")
    m1 = EM(IT.class_)
    m1.put(IT.Primary, JString("Longsword_Attack"))
    n1 = R.withGuard(m1)
    K.check(n1 is not None and str(n1.get(IT.Secondary)) == "SkyyArmory_Longsword_Guard" and str(n1.get(IT.Primary)) == "Longsword_Attack"
            and n1.getClass().getName() == "java.util.EnumMap" and m1.get(IT.Secondary) is None,
            "X6: withGuard on an EnumMap: a NEW EnumMap + Secondary (the original untouched)")
    m2 = HM()
    m2.put(IT.Primary, JString("Longsword_Attack"))
    m2.put(IT.Ability1, JString("Root_X"))
    n2 = R.withGuard(m2)
    K.check(n2 is not None and n2.size() == 3 and str(n2.get(IT.Ability1)) == "Root_X", "X6: withGuard on a HashMap keeps the other keys")
    m3 = HM(m2)
    m3.put(IT.Secondary, JString("Somebody_Block"))
    m4 = HM()
    m4.put(IT.Primary, JString("Root_Weapon_Sword_Primary"))
    K.check(R.withGuard(m3) is None and R.withGuard(m4) is None and R.withGuard(None) is None, "X6: a longsword with its own right click / a sword / null = untouched")
    # X7 the guard on a REAL engine Item
    ITM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    fld = ITM.class_.getDeclaredField("interactions")
    fld.setAccessible(True)

    def item(iid, m):
        it = ITM(JString(iid))
        fld.set(it, m)
        return it
    real = item("Weapon_Longsword_Harness", EM(m1))
    g0 = int(R.GUARDS)
    K.check(bool(R.guardItem(real)) and str(real.getInteractions().get(IT.Secondary)) == "SkyyArmory_Longsword_Guard" and int(R.GUARDS) == g0 + 1
            and bool(R.GUARDED.containsKey("Weapon_Longsword_Harness")), "X7: guardItem on a real Item: the engine's interactions map now has the guard")
    K.check(not bool(R.guardItem(real)), "X7: a second call changes nothing (it has a right click now)")
    npc = item("Weapon_Longsword_Praetorian_NPC", EM(m1))
    K.check(not bool(R.guardItem(npc)) and npc.getInteractions().get(IT.Secondary) is None, "X7: an NPC copy never gets the guard")
    Cfg.GUARD_ON = False
    off = item("Weapon_Longsword_Off", EM(m1))
    K.check(not bool(R.guardItem(off)) and off.getInteractions().get(IT.Secondary) is None and "off" in str(R.guardAll()), "X7: blade.guard.enabled off = no guard")
    Cfg.GUARD_ON = True
    K.check(not bool(R.guardItem(None)), "X7: null item = nothing")
    ga = str(R.guardAll())
    K.check(len(ga) > 0, "X7: guardAll without loaded assets answers without a throw: %s" % ga)
    K.eq([int(R.onLoaded(None)), int(R.onLoaded(JString("x")))], [0, 0], "X7: onLoaded ignores a non-event")
    JClass(PKG + "ArmoryItemL")().accept(None)
    K.ok += 1
    # X8 the caches + unloaded engine reads
    R.SWORD.put("Longsword_Iron_Red", JObject(True, JClass("java.lang.Boolean")))
    K.check(bool(R.sword("Longsword_Iron_Red")) and not bool(R.sword(None)) and not bool(R.sword("Weapon_Nothing_Loaded"))
            and not bool(R.SWORD.containsKey("Weapon_Nothing_Loaded")), "X8: sword(): the cache answers; unreadable = no (never cached)")
    R.HCACHE.put("Longsword_Iron_Red", JObject(16.0, JClass("java.lang.Double")))
    K.eq([float(R.hOf("Longsword_Iron_Red")), float(R.hOf("Weapon_Nothing_Loaded")), float(R.hOf(None))], [16.0, 8.0, 8.0],
         "X8: hOf: cached 16; unreadable = blade.rush.hitFallback 8")
    K.eq([float(R.intHit("Longsword_Swing_Left_Damage")), float(R.rootHit("x")), float(R.intHit(None))], [-1.0, -1.0, -1.0], "X8: no assets loaded = -1 (no throw)")
    K.eq(int(Defs.pidCode("SkyyArmory_Crescent_Rush")), 15000, "X8: the marker's code (ArmoryTrav.added dispatches 15000 to Rush.marker)")
    # X9 the world-thread paths without a world
    KJ = JClass(PKG + "KunaiJob")
    KJ(4, U, None, DA([1.0, 0.0, 0.0]), 0, 0.0, 0.0).run()
    K.eq(str(R.LAST_WHY), "the swordsman left this world", "X9: KunaiJob kind 4 runs Rush.dash (no player = nothing happens)")
    R.PEND.put(U, S())
    R.tickPlayer(None, None, None)
    K.check(R.PEND.containsKey(U), "X9: tickPlayer without a player leaves the queue alone")
    K.eq(int(R.strike(None, None, U, S())), 0, "X9: strike without a player = 0 hits")
    R.clear()
    K.check(R.PEND.isEmpty() and R.SWORD.isEmpty() and R.HCACHE.isEmpty(), "X9: clear() empties the queues and caches")
    K.check("Crescent Rush:" in str(R.statusText()), "X9: statusText: %s" % R.statusText())
    # X10 the loader: clamps
    P = JClass("java.util.Properties")()
    for k_, v_ in (("blade.rush.distance", "99"), ("blade.rush.sweepArc", "5"), ("blade.damagePercent", "500"),
                   ("blade.rush.stamina", "-3"), ("blade.guard.enabled", "off"), ("blade.rush.crescentMomentum", "0")):
        P.setProperty(k_, v_)
    K.check(bool(Cfg.GUARD_SET) and bool(Cfg.GUARD_ON), "X10 (fix 3): the first load latched the guard (on)")
    Cfg.apply(P)
    K.eq([float(Cfg.RUSH_DIST), int(Cfg.RUSH_ARC), int(Cfg.BLADE_PCT), float(Cfg.RUSH_STAM), bool(Cfg.GUARD_ON), bool(Cfg.GUARD_NEXT), int(Cfg.RUSH_CRAT)],
         [12.0, 30, 200, 0.0, True, False, 0], "X10: the loader clamps like the rows (12 / 30 / 200 / 0), crescent from 0 = always; (fix 3) a live "
         "reload with blade.guard.enabled=off keeps the running guard (restart row) and only records the file value")
    K.check("OFF after a restart" in str(Cfg.BLADE_TEXT), "X10 (fix 3): the text says the switch waits for a restart: %s" % Cfg.BLADE_TEXT)
    Cfg.GUARD_SET = False
    Cfg.apply(P)
    K.check(not bool(Cfg.GUARD_ON) and bool(Cfg.GUARD_SET) and "after a restart" not in str(Cfg.BLADE_TEXT),
            "X10 (fix 3): a fresh start (latch reset by shutdown) reads blade.guard.enabled=off")
    Cfg.GUARD_SET = False
    Cfg.useDefaults()
    K.check(bool(Cfg.GUARD_ON) and "Crescent Rush hits too" in str(Cfg.BLADE_TEXT), "X10: defaults again; the text says the bonus counts on rush hits")
    dc = str(Cfg.DEF_CFG)
    K.check(all(("%s=%s" % (k_, v_)) in dc for k_, v_ in (("blade.rush.enabled", "true"), ("blade.rush.distance", "6"), ("blade.rush.perMomentum", "0.15"),
            ("blade.rush.mana", "8"), ("blade.rush.stamina", "4"), ("blade.damagePercent", "113"), ("blade.guard.enabled", "true"))) and "blade.rush.element" not in dc,
            "X10: the default config file carries the new rows")
    K.save()


# ---------------------------------------------------------------------------------------------------- D: live
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    f = os.path.join(home, "config.properties")
    before = open(f, "rb").read() if os.path.isfile(f) else None
    files0 = sorted(os.listdir(home))
    snaps = []
    for start in (1, 2):
        for m in ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(f, "rb").read() if os.path.isfile(f) else None)
    K.check(snaps[0] == snaps[1], "D: the 2nd start changes nothing")
    K.check(before is None or snaps[0] == before, "D: the live copy's config.properties is not rewritten by 0.1.28 (new keys read their defaults)")
    K.check(sorted(f_ for f_ in os.listdir(home) if not f_.startswith("config-history")) == sorted(f_ for f_ in files0 if not f_.startswith("config-history")),
            "D: no new file in the data folder")
    K.check(bool(Cfg.RUSH_ON) and int(Cfg.BLADE_PCT) == 113 and bool(Cfg.GUARD_ON), "D: Skyy's file has no blade.* lines -> the defaults apply")
    K.notes.append("D: live config.properties %s bytes" % (len(before) if before else 0))
    K.save()


def main():
    phases = {"mkfake": lambda: HK.run_mkfake(os.path.join(SCRATCH, "fake"), JAR), "verify": lambda: HK.run_verify(HK.arg("--out"), JAR),
              "audit": lambda: HK.run_audit(HK.arg("--out"), JAR, os.path.join(SCRATCH, "fake")),
              "compare": lambda: run_compare(HK.arg("--out"), JAR, SCRATCH, None), "exec": lambda: run_exec(HK.arg("--out"), JAR, SCRATCH, None),
              "live": lambda: run_live(HK.arg("--out"), JAR, SCRATCH, HK.arg("--home"))}
    if "--phase" in sys.argv:
        try:
            phases[HK.arg("--phase")]()
        except SystemExit:
            raise
        except Exception:
            import traceback
            traceback.print_exc()
            sys.exit(1)
        return
    assert os.path.isfile(JAR) and os.path.isfile(OLD_JAR), (JAR, OLD_JAR)
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    os.makedirs(os.path.join(SCRATCH, "fake"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]

    def child(label, *extra):
        out = os.path.join(SCRATCH, "%s.json" % label)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--phase", label, "--out", out, "--dir", SCRATCH, "--jar", JAR] + list(extra), env=env)
        HK.check(p.returncode == 0, "%s: the child exited cleanly (%s)" % (label, p.returncode))
        return out
    try:
        run_assets()
        child("mkfake")
        for label in ("verify", "compare", "exec"):
            HK.take(child(label), label)
        home = os.path.join(SCRATCH, "live", "Skyy_SkyyArmory")
        if os.path.isdir(LIVE_DIR):
            shutil.copytree(LIVE_DIR, home)
            print("D. live Skyy_SkyyArmory copied (read-only source %s)" % LIVE_DIR)
            HK.take(child("live", "--home", home), "live")
        else:
            HK.check(False, "D: no live folder %s" % LIVE_DIR)
        outa = child("audit")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            HK.check(not a["refused"] and a["refs"] > 100, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            HK.check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, %d refused, control refused" % (a["refs"], a["classes"], len(a["refused"])))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyArmory %s harness: %d ok, %d fail(s)" % (VERSION, HK.OKS[0], len(HK.FAILS)))
    for f in HK.FAILS:
        print("FAIL:", f)
    sys.exit(1 if HK.FAILS else 0)


if __name__ == "__main__":
    main()
