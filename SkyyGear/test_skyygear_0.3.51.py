"""Harness for SkyyGear 0.3.51 (Augments round A0: ATTACK SPEED LIVE - tools/gear_0_3_51_patch.py header).
Build first:
    python tools/gear_0_3_51_patch.py && python SkyyGear/build_skyygear_0.3.51.py
    python SkyyGear/test_skyygear_0.3.51.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.50 jar is the compare base):
  S  static   the patch re-runs to identical bytes, line endings kept, no new class / command / system; the jar's non-class files = 0.3.50's
              + the attack speed assets (5 step effects, the step copies of every family, their walk roots + animation sets), only manifest.json
              and the 9 decision trees changed; every 0.3.50 speed file byte-identical; every new copy = its family's Fast copy file for file
              and step for step (the same vanilla damage steps by id - tapHit); THE TREES walked in Python for every tier x step x
              effect set: no attack speed effect = exactly 0.3.50's leaf, a step = the copy at f / (1 + step) (its cooldown x f), no effect at
              all = the vanilla interaction; the fresh config file (stats.as=10,0, as.cap, the marker)
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.50 -> 0.3.51 (EXPECT below; the non-class list = the S phase's)
  E  engine   (the 0.2.11 harness's bare server boot: vanilla pack + THIS jar, every codec validator) - every new code path EXECUTED:
              V  the jar's assets load with no failed store; the 9 roots are SkyyGear's trees (active), the 5 step effects resolve (readyAs)
              P  pure parts: asStep, capAs (+ as.cap live), the door gear:as (Number, Object[] valid / expired, bad), cyc / winMs2 = the tables
              T  totals: an Attack Speed line on a weapon + on armor -> asOf; part.stats off / a bow / a wand / a tool / as.cap 0 = 0
              K  GearSpeed.tick on an ECS shim with a REAL EffectControllerComponent and the jar's REAL effect assets: the step effect on beside
                 the tier one, swap, lost + put back, the door, the cap, Medium, swing.tiers off, a bow; the state record
              H  GearSpeed.hitWeight on real Damage objects (DamageSequence meta = a real tap calculator): cycle x (1 + as), the swap window over
                 tier AND step, LAST = the cycle only, a non-tap step x1, as 0 = the 0.3.50 weight
              L  lines: modLine "(melee swings)", not grey, the roll pool (weight 0 never; a Server Setup weight rolls it), asText / describe / readyText
              M  migrateAs51 on a 0.3.50-default file (CRLF kept, 10,5 -> 10,0, History snapshot, change-log row, run once; a custom value kept + noted)
  D  live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: every one-time update + load() twice; the second start
              changes nothing; stats.as moved to 10,0 (it held the 0.3.50 default)
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the client playing the re-timed swing animations for the step copies (the 0.2.6 tier pattern, proven in game
for the tiers); how a +5 % step FEELS; Hytale honouring an EffectCondition nested 6 deep.
Scratch: tools/dev/scratch/aug_a0/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, re, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.51"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "aug_a0", "harness")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.50.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_51_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.50.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
ADDED = []
# the class compare 0.3.50 -> 0.3.51 (the first run's dump, reviewed: rows / migrateAs51 / GearDefs.I_AS / GearSpeed / suffix / /gear / setup)
EXPECT = {
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CfgRows1': ['~<clinit>'],
    'CfgRows2': ['~<clinit>'],
    'GearAdmin': ['~m me'],
    'GearCfg': ['+f AS_CAP', '+f H51_KEYS', '+f H51_MARK', '+f H51_MARK_ID', '+f H51_NEW', '+f H51_OLD', '+f H51_WHO', '+m h51Log', '+m h51Old', '+m h51Update', '+m migrateAs51', '~<clinit>', '~m apply', '~m defaultsText'],
    'GearDefs': ['+f I_AS', '~<clinit>'],
    'GearSpeed': ['+f AEFF', '+f AIDX', '+f AIDX_NEXT', '+f AIDX_TOLD', '+f AN', '+f AS_K', '+f AS_STEP', '+f A_SMAX', '+f A_W', '+f A_WALK', '+m asHint', '+m asNow', '+m asOf', '+m asStep', '+m asText', '+m asWant', '+m buffs', '+m capAs', '+m cyc', '+m lostA', '+m put', '+m readyAs', '+m walkRoot', '+m winMs2', '~<clinit>', '~m appliedW', '~m describe', '~m hitWeight', '~m put', '~m readyText', '~m reset', '~m state', '~m tick', '~m walk'],
    'GearView': ['~m suffix'],
    'SkyyGearPlugin': ['~m setup'],
}
U = "00000000-0000-0000-0000-000000000351"
AS_STEP, AS_K = 5, 5
AS_EFF = ["SkyyGear_Speed_As%02d" % (AS_STEP * s) for s in range(1, AS_K + 1)]
TIER_EFF = ["SkyyGear_Speed_Slow", "", "SkyyGear_Speed_Fast", "SkyyGear_Speed_SuperFast"]
TAGS = ["S", "M", "F", "X"]
FACT = [1.4, 1.0, 0.7, 0.5]
FAMS = ["Sword", "Daggers", "Longsword", "Spear", "Battleaxe", "Axe", "Club", "Flail", "Mace"]
DI = "Server/Item/Interactions/SkyyGear/Speed/"
DR = "Server/Item/RootInteractions/SkyyGear/Speed/"
DA = "Server/Item/Animations/SkyyGear/"
DE = "Server/Entity/Effects/SkyyGear/"


def speed_name(n):
    return n.startswith(DI) or n.startswith(DR) or n.startswith(DA) or n.startswith(DE)


def tree_paths(z):
    return sorted(n for n in z.namelist() if n.startswith(DI) and re.match(r"^SkyyGear_Spd_[A-Za-z]+\.json$", os.path.basename(n)))


def expected_nonclass(za, zb):
    """(added, changed) non-class entries the 0.3.51 jar may have vs 0.3.50: only attack speed assets added; manifest + the 9 trees changed"""
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    added = sorted(eb - ea)
    changed = sorted(n for n in ea & eb if za.read(n) != zb.read(n))
    return added, changed, sorted(ea - eb)


def resolve(node, effs, I):
    """walk a SkyyGear decision tree like the engine's EffectConditionInteraction: All = every id on the player, None = none of them"""
    for _ in range(40):
        if isinstance(node, str):
            if node.startswith("SkyyGear_Spd_") and node in I:
                node = I[node]
                continue
            return node
        if node.get("Type") == "EffectCondition":
            ids = node["EntityEffectIds"]
            ok = all(i in effs for i in ids) if node["Match"] == "All" else not any(i in effs for i in ids)
            node = node["Next"] if ok else node["Failed"]
            continue
        return node
    raise AssertionError("tree too deep")


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.51 - build script') and g.count('VERSION = "0.3.51"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 0), "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    added, changed, gone = expected_nonclass(za, zb)
    trees = tree_paths(zb)
    K.eq(len(trees), 9, "S nine family trees")
    K.eq(gone, [], "S no file removed")
    K.eq(changed, sorted(["manifest.json"] + trees), "S changed = manifest.json + the 9 trees")
    K.check(added and all(speed_name(n) for n in added), "S every added file is an attack speed asset: %s" % [n for n in added if not speed_name(n)][:5])
    K.eq(sorted(n for n in added if n.startswith(DE)), sorted(DE + e + ".json" for e in AS_EFF), "S the 5 step effects")
    K.check(all(json.loads(zb.read(DE + e + ".json")) == {"Duration": 3, "OverlapBehavior": "Overwrite"} for e in AS_EFF),
            "S each step effect = the tier effects' hidden marker (3 s, Overwrite, nothing else)")
    old_speed = [n for n in za.namelist() if speed_name(n) and n not in trees]
    K.check(all(za.read(n) == zb.read(n) for n in old_speed), "S every other 0.3.50 speed file byte-identical (%d)" % len(old_speed))
    K.notes.append("S %d attack speed assets added (%d interactions, %d roots, %d animation sets); jar %d -> %d bytes" % (
        len(added), len([n for n in added if n.startswith(DI)]), len([n for n in added if n.startswith(DR)]), len([n for n in added if n.startswith(DA)]),
        os.path.getsize(OLD_JAR), os.path.getsize(jar)))
    # the trees, walked
    Ib = dict((os.path.basename(n)[:-5], json.loads(zb.read(n))) for n in zb.namelist() if n.startswith(DI))
    Ia = dict((os.path.basename(n)[:-5], json.loads(za.read(n))) for n in za.namelist() if n.startswith(DI))
    Rb = dict((os.path.basename(n)[:-5], json.loads(zb.read(n))) for n in zb.namelist() if n.startswith(DR))
    bad, seen_tops = [], {}
    for fam in FAMS:
        tid = "SkyyGear_Spd_" + fam
        tb, ta = Ib[tid], Ia[tid]
        van = resolve(ta, set(), {})
        cd0 = float(resolve(ta, set([TIER_EFF[0]]), {})["Cooldown"]["Cooldown"]) / 1.4          # the family's vanilla cooldown (Slow is never floored)
        f_tier = [float(resolve(ta, set([TIER_EFF[x]]), {})["Cooldown"]["Cooldown"]) / cd0 if x != 1 else 1.0 for x in range(4)]          # 0.3.50's own (floored) factors
        f_floor = min(float(resolve(tb, set([TIER_EFF[x]] if x != 1 else []) | set([AS_EFF[y]]), {})["Cooldown"]["Cooldown"]) / cd0 for x in range(4) for y in range(AS_K))
        for t in range(4):
            base = set([TIER_EFF[t]] if t != 1 else [])
            old_leaf = resolve(ta, base, {})
            if resolve(tb, base, {}) != old_leaf:
                bad.append((fam, TAGS[t], "no step != 0.3.50"))
            for s in range(1, AS_K + 1):
                leaf = resolve(tb, base | set([AS_EFF[s - 1]]), {})
                # a higher step wins over a lower one (several on the player - never happens, but the order is the rule)
                if s > 1 and resolve(tb, base | set(AS_EFF[:s]), {}) != leaf:
                    bad.append((fam, TAGS[t], s, "highest step first"))
                if not isinstance(leaf, dict) or leaf.get("Type") != "TriggerCooldown":
                    bad.append((fam, TAGS[t], s, "leaf", leaf if isinstance(leaf, str) else leaf.get("Type")))
                    continue
                top = leaf["Next"]
                if top not in Ib:
                    bad.append((fam, TAGS[t], s, "top missing", top))
                    continue
                m = re.match(r"^SkyyGear_Spd([SMFX])(\d*)_%s_" % fam, top)
                if not m:
                    bad.append((fam, TAGS[t], s, "top name", top))
                    continue
                seen_tops.setdefault(fam, set()).add(top)
                f_want = FACT[t] / (1.0 + AS_STEP * s / 100.0)
                cdl = float(leaf["Cooldown"]["Cooldown"])
                f_real = cdl / cd0
                # the leaf runs this tier x step, or (the floored daggers / Super Fast swords) the floor copy already made: never slower than the
                # tier itself, never faster than tier / (1 + step), and off the exact factor only AT the family's floor (= its Super Fast leaf)
                if not (f_real >= f_want - 2e-3 and f_real <= f_tier[t] + 2e-3 and (abs(f_real - f_want) < 2e-3 or abs(f_real - f_floor) < 2e-3)):
                    bad.append((fam, TAGS[t], s, "cooldown", cdl, round(f_real, 4), round(f_want, 4), round(f_floor, 4)))
                if (DR + "SkyyGear_SpdWalk%s%s_%s.json" % (m.group(1), m.group(2), fam)) not in zb.namelist():
                    bad.append((fam, TAGS[t], s, "walk root missing"))
        if resolve(tb, set(), {}) != van:
            bad.append((fam, "nothing on = not vanilla"))
    K.check(not bad, "S the trees walked for every family x tier x step: no step = 0.3.50's leaf exactly; a step = its copy (f / (1 + step), floored "
            "copies reused), cooldown x f, the highest step first; nothing on = vanilla: %s" % bad[:6])
    K.notes.append("S step copies reached per family: %s" % dict((f, len(v)) for f, v in seen_tops.items()))
    # every new copy = the 0.3.50 Fast copy of its family file for file, step for step: the same vanilla damage / selector / effect steps by id
    # (so GearSpeed.tapHit's tier walk names every copy's hits), only RunTime / ChainingAllowance / Cooldown numbers and the copy's own ids differ
    def norm(x, tag, fam):
        if isinstance(x, dict):
            return dict((k, ("#" if k in ("RunTime", "ChainingAllowance", "Speed") else norm(v, tag, fam))) for k, v in x.items())
        if isinstance(x, list):
            return [norm(v, tag, fam) for v in x]
        if isinstance(x, str):
            return x.replace("SkyyGear_Spd%s_" % tag, "SkyyGear_SpdF_").replace("SkyyGear_SpdWalk%s_" % tag, "SkyyGear_SpdWalkF_")
        return x
    sbad, ncopy = [], 0
    for fam in FAMS:
        fF = dict((os.path.basename(n)[:-5], json.loads(zb.read(n))) for n in zb.namelist() if n.startswith(DI) and os.path.basename(n).startswith("SkyyGear_SpdF_%s_" % fam))
        tags = sorted(set(re.match(r"^SkyyGear_Spd([SMFX]\d+)_", os.path.basename(n)).group(1) for n in added
                          if n.startswith(DI) and re.match(r"^SkyyGear_Spd[SMFX]\d+_%s_" % fam, os.path.basename(n))))
        for tag in tags:
            ncopy += 1
            fT = dict((os.path.basename(n)[:-5].replace("SkyyGear_Spd%s_" % tag, "SkyyGear_SpdF_"), json.loads(zb.read(n))) for n in zb.namelist()
                      if n.startswith(DI) and os.path.basename(n).startswith("SkyyGear_Spd%s_%s_" % (tag, fam)))
            if sorted(fT) != sorted(fF):
                sbad.append((fam, tag, "files", sorted(set(fT) ^ set(fF))[:3]))
                continue
            for k in fF:
                if norm(fT[k], tag, fam) != norm(fF[k], "F", fam):
                    sbad.append((fam, tag, k))
                    break
    K.check(not sbad and ncopy >= 150, "S every attack speed copy (%d) = its family's 0.3.50 Fast copy file for file and step for step (the same vanilla damage "
            "steps by id), only the times + its own ids differ: %s" % (ncopy, sbad[:4]))
    # the fresh config file the build writes (via the generated script's own default text: read it from the jar's kit resource if any, else the script)
    K.check('("as", "Attack Speed", "wae", "%", 10, 0, 1, "aspd")' in g and '("as.cap", "Attack Speed cap", "combat", "dec", "25", "0", "25"' in g,
            "S the stat row (live, weight 0, aspd) + the as.cap row")
    K.check('H51_KEYS = ["stats.as"]' in g and 'H51_OLD = ["10,5"]' in g and "@PKG@.GearCfg.migrateAs51();" in g, "S migrateAs51: stats.as 10,5 -> the new default, called at setup")
    K.save()


# ====================================================================================================== C: the compare (non-class: the S rule)
def run_compare51(out, jar, old_jar, pkg, expect, added, removed=()):
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
    pa, pb = pool_of(old_jar), pool_of(jar)

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature()) + " " + str(f_.getModifiers())

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
                lines_.append(re.sub(r"^((?:if\w*|goto(?:_w)?|jsr(?:_w)?)) -?\d+$", r"\1", ln_))
            return str(b_.getModifiers()) + "\n" + "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_
    na, nb = HK.jar_classes(old_jar), HK.jar_classes(jar)
    K.eq(sorted(set(nb) - set(na)), sorted(pkg + a for a in added), "C: classes added")
    K.eq(sorted(set(na) - set(nb)), sorted(pkg + r for r in removed), "C: classes removed")
    diffs, same = {}, 0
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(pkg):] if cn.startswith(pkg) else cn] = sorted(("+" if k not in ma else ("-" if k not in mb else "~")) + k for k in dd)
        else:
            same += 1
    print("C. class compare %s -> %s: %d classes identical, %d differ" % (os.path.basename(old_jar), os.path.basename(jar), same, len(diffs)))
    got = dict((k, sorted(set(x.split("(")[0] for x in v))) for k, v in diffs.items())
    for k in sorted(got):
        print("   %-22s %s" % (k, ", ".join(got[k])))
    if expect is None:
        json.dump(got, open(os.path.join(os.path.dirname(SCRATCH), "expect.dump.json"), "w"), indent=1, sort_keys=True)
        K.check(False, "C: no EXPECT yet - wrote expect.dump.json next to the harness scratch (review it, then paste it as EXPECT)")
    else:
        K.eq(sorted(got), sorted(expect), "C: the classes that differ")
        for k in sorted(expect):
            K.eq(got.get(k, []), sorted(expect[k]), "C: %s members" % k)
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    a_, c_, g_ = expected_nonclass(za, zb)
    K.check(not g_ and all(speed_name(n) for n in a_) and c_ == sorted(["manifest.json"] + tree_paths(zb)),
            "C: non-class entries: only attack speed assets added (%d), manifest.json + the 9 trees changed" % len(a_))
    K.notes.append("C: %d identical, changed: %s" % (same, got))
    K.save()


HK.run_compare = run_compare51


# ====================================================================================================== E: engine
def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JString, JImplements, JOverride, JObject, JArray, JLong, JDouble, JBoolean, JFloat, JShort
    K = HK.Child(out)
    h211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
    t = open(h211, encoding="utf-8").read()
    t = t[:t.index("def run_engine(out):")]
    esc = os.path.join(scratch, "eng")
    os.makedirs(esc, exist_ok=True)
    argv0 = sys.argv
    sys.argv = [h211, "--jar", jar, "--dir", esc]
    H = {"__name__": "skyygear_h211_lib", "__file__": h211, "__builtins__": __builtins__}
    exec(compile(t, h211 + " (engine boot, library)", "exec"), H)
    sys.argv = argv0
    H.update({"JAR": jar, "SCRATCH": esc, "VERSION": VERSION})
    H["_jvm"]([B.SERVER_JAR, B.JAVASSIST, jar], verify=True, big=True)

    class KC(object):
        def __init__(self, k):
            self.k = k
            self.notes = k.notes

        def check(self, c, w):
            return self.k.check(c, "E boot: " + w)
    E = H["engine_boot"](KC(K))
    us = E["us"]
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Data, Roll, Spd, View, Stats, Defs = (P("GearCfg"), P("Gear"), P("GearData"), P("GearRoll"), P("GearSpeed"), P("GearView"),
                                                     P("GearStats"), P("GearDefs"))
    Props = JClass("java.util.Properties")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")
    HM = JClass("java.util.HashMap")
    SysJ = JClass("java.lang.System")
    OA = JArray(JObject)
    u = UUID.fromString(U)
    sysp = SysJ.getProperties()
    br = sysp.get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        sysp.put("skyy.bridge", br)
    data = os.path.join(scratch, "data")
    os.makedirs(data, exist_ok=True)
    Cfg.DIR = Paths.get(data)
    fresh = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(JClass("java.io.StringReader")(fresh))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    BASE = {"part__gate": "false"}          # the harness player has no class level: every gear item usable
    apply(**BASE)

    def fld(cls, name):
        k = cls.class_ if hasattr(cls, "class_") else cls
        while k is not None:
            try:
                f = k.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(name)

    # ================================================================================== V the assets in the real stores
    # the bare boot cannot decode / validate everything vanilla needs (no EntityStatType values, some Selector types: thousands of vanilla
    # assets fail the same way), so the rule is: every failing NEW speed asset has its 0.3.50 Fast / Slow / Super Fast twin failing the same way
    # in this boot, and the step effects / trees never fail
    fl = set()
    for lv, m in E["rec"]:
        mm = re.match(r"^Failed to (?:decode|validate) asset: (SkyyGear_Sp[a-zA-Z0-9_]+)", m)
        if mm:
            fl.add(mm.group(1))
    new_f = sorted(x for x in fl if re.match(r"^SkyyGear_Spd[SMFX]\d+_", x))
    orphan = [x for x in new_f if re.sub(r"^SkyyGear_Spd([SMFX])\d+_", "SkyyGear_SpdF_", x) not in fl and re.sub(r"^SkyyGear_Spd([SMFX])\d+_", "SkyyGear_SpdX_", x) not in fl
              and re.sub(r"^SkyyGear_Spd([SMFX])\d+_", "SkyyGear_SpdS_", x) not in fl]
    K.check(not orphan and not [x for x in fl if x.startswith("SkyyGear_Speed") or re.match(r"^SkyyGear_Spd_[A-Za-z]+$", x)] and set(E["fail"]) <= set(E["vfail"]) | set(["Interaction", "Item"]),
            "V every speed asset that fails in the bare boot has a 0.3.50 twin failing the same way (boot limits: %d vanilla stores failed too); the step "
            "effects + the 9 trees load: %s" % (len(E["vfail"]), orphan[:4]))
    K.notes.append("V boot failures: %d speed assets (%d new, all with a failing 0.3.50 twin); stores failed %s (vanilla %s)" % (len(fl), len(new_f), list(E["fail"]), list(E["vfail"])))
    K.notes.append("V jar pack log: %d lines, %d SEVERE / WARNING" % (len(E["rec"]), len([1 for lv, m in E["rec"] if lv in ("SEVERE", "WARNING")])))
    NM = int(Spd.NM)
    K.check(NM == 9 and all(bool(Spd.active(f)) for f in range(NM)), "V the 9 roots are SkyyGear's trees (active): %s" % [str(Spd.rootFirst(Spd.F_ROOT[f])) for f in range(NM)])
    Spd.AIDX = None
    Spd.AIDX_NEXT = 0
    K.check(bool(Spd.readyAs()) and len(list(Spd.AIDX)) == 5 and len(set(int(x) for x in Spd.AIDX)) == 5 and bool(Spd.ready()),
            "V readyAs resolves the 5 step effects (distinct indexes): %s" % (list(Spd.AIDX) if Spd.AIDX is not None else None))

    # ================================================================================== W every copy reaches the same damage steps
    ITEM = E["ITEM"]
    ids = sorted(str(k) for k in ITEM.getAssetMap().getAssetMap().keySet() if str(k).startswith("Weapon_"))
    rep = {}
    for iid in ids:
        f = int(Spd.famOf(JString(iid)))
        if 0 <= f < NM and f not in rep:
            rep[f] = iid
    K.eq(sorted(rep), list(range(NM)), "W one tier item per family found: %s" % rep)
    # ================================================================================== P pure parts
    K.eq([int(Spd.asStep(JDouble(x))) for x in (0.0, -3.0, 4.99, 5.0, 7.0, 9.999999999999, 12.0, 25.0, 40.0)], [0, 0, 0, 1, 1, 2, 2, 5, 5],
         "P asStep: whole 5 % steps (floor, the float edge counts), at most 5")
    K.eq([round(float(Spd.capAs(JDouble(x))), 6) for x in (-5.0, 0.0, 7.5, 25.0, 60.0)], [0.0, 0.0, 7.5, 25.0, 25.0], "P capAs: 0 .. as.cap 25")
    apply(as__cap="10", **BASE)
    c10 = float(Spd.capAs(JDouble(60.0)))
    apply(as__cap="0", **BASE)
    c0 = float(Spd.capAs(JDouble(60.0)))
    apply(as__cap="99", **BASE)
    c99 = float(Cfg.AS_CAP)
    apply(**BASE)
    K.check(c10 == 10.0 and c0 == 0.0 and c99 == 25.0 and float(Cfg.AS_CAP) == 25.0, "P as.cap live: 10 caps at 10, 0 = off, 99 is clamped to 25 (the ladder top): %s %s %s" % (c10, c0, c99))
    door = JClass("java.util.concurrent.ConcurrentHashMap")()
    br.put("gear:as:" + U, door)
    now = int(SysJ.currentTimeMillis())
    door.put("a", JObject(JDouble(4.0), "java.lang.Double"))
    door.put("b", OA([JObject(JDouble(3.0), "java.lang.Double"), JObject(JLong(now + 60000), "java.lang.Long")]))
    door.put("c", OA([JObject(JDouble(50.0), "java.lang.Double"), JObject(JLong(now - 1), "java.lang.Long")]))
    door.put("d", JString("x"))
    door.put("e", JObject(JDouble(500.0), "java.lang.Double"))
    door.put("f", JObject(JDouble(float("nan")), "java.lang.Double"))
    n1 = int(Spd.AN.get(1))
    bsum = float(Spd.buffs(u))
    K.check(abs(bsum - 107.0) < 1e-9 and int(Spd.AN.get(1)) - n1 == 3, "P the door gear:as: 4 + 3 (still valid) + 100 (500 clamped); the expired, the text and NaN skipped (%s)" % bsum)
    door.clear()
    br.remove("gear:as:" + U)
    K.check(float(Spd.buffs(u)) == 0.0 and float(Spd.buffs(None)) == 0.0, "P no door = 0")
    AWt, ASt, FW = list(Spd.A_W), list(Spd.A_SMAX), list(Spd.F_W)
    cbad = []
    for f in range(len(list(Spd.F_NAME))):
        for t in range(4):
            if abs(float(Spd.cyc(f, t, 0)) - FW[f * 4 + t]) > 1e-12:
                cbad.append((f, t, "step 0 != F_W"))
            for s in range(AS_K + 1):
                if abs(float(Spd.cyc(f, t, s)) - AWt[(f * 4 + t) * (AS_K + 1) + s]) > 1e-12 or int(Spd.winMs2(f, t, s)) != int(ASt[(f * 4 + t) * (AS_K + 1) + s] * 1000.0) + 150:
                    cbad.append((f, t, s))
            if s and f < NM and float(Spd.cyc(f, t, AS_K)) > float(Spd.cyc(f, t, 0)):
                cbad.append((f, t, "slower"))
    K.check(not cbad and float(Spd.cyc(0, -1, 0)) == 1.0 and float(Spd.cyc(-1, 2, 3)) == 1.0 and float(Spd.cyc(0, 2, 99)) == FW[2]
            and int(Spd.winMs2(0, -1, 0)) == int(Spd.winMs(0, -1)), "P cyc / winMs2 = the build tables (step 0 = F_W / winMs; Medium for -1; bad step = 0): %s" % cbad[:4])

    # ================================================================================== T totals -> asOf
    def sdoc(iid, lv, tier, mods=()):
        d_ = Roll.newDoc(JString(iid), 0, True, JString("admin"), lv)
        ar_ = JClass("org.bson.BsonArray")()
        for k_, v_ in mods:
            ar_.add(Data.mod(JString(k_), v_))
        d_.put("mods", ar_)
        if tier is None:
            d_.remove("spd")
        else:
            d_.put("spd", JClass("org.bson.BsonInt32")(tier))
        return d_

    def sstack(iid, lv, tier, mods=()):
        return Data.put(IS(JString(iid), 1), sdoc(iid, lv, tier, mods), u)
    sw = rep[0]
    s_fast_as = sstack(sw, 15, 2, [("as", 10)])
    ev = float(View.effVal(JString(sw), Data.effective(JString(sw), s_fast_as.getMetadata()), JString("as"), 10))
    I_AS = int(Defs.I_AS)
    t0 = [int(x) for x in Stats.totals(u, s_fast_as, None, None, True)]
    a0 = float(Spd.asOf(u, s_fast_as, None))
    K.check(t0[I_AS] == int(round(ev)) and a0 == float(t0[I_AS]) and a0 > 0, "T a +10 Attack Speed line on a Lv 15 sword (x slot power) = %d in the totals = asOf %s (effVal %.2f)" % (t0[I_AS], a0, ev))
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    arm = SIC(JShort(4))
    helm = None
    for iid in sorted(str(k) for k in ITEM.getAssetMap().getAssetMap().keySet() if str(k).startswith("Armor_") and str(k).endswith("_Head")):
        if int(Data.slotOf(JString(iid))) == 2:
            helm = iid
            break
    arm.setItemStackForSlot(JShort(0), sstack(helm, 15, None, [("as", 10)]))
    a1 = float(Spd.asOf(u, s_fast_as, arm))
    K.check(a1 > a0 and a1 <= 25.0, "T + an Attack Speed line on worn armor (%s) adds: %s -> %s" % (helm, a0, a1))
    door.put("x", JObject(JDouble(30.0), "java.lang.Double"))
    br.put("gear:as:" + U, door)
    a2 = float(Spd.asOf(u, s_fast_as, arm))
    door.clear()
    apply(part__stats="false", **BASE)
    a3 = float(Spd.asOf(u, s_fast_as, arm))
    apply(as__cap="0", **BASE)
    a4 = float(Spd.asOf(u, s_fast_as, arm))
    apply(**BASE)
    bow = next((i for i in ids if "Shortbow" in i and int(Data.slotOf(JString(i))) in (0, 1)), None)
    wand = next((i for i in ids if i.startswith("Weapon_Wand_") and int(Data.slotOf(JString(i))) in (0, 1)), None)
    a5 = float(Spd.asOf(u, sstack(bow, 15, None, [("as", 10)]), arm)) if bow else -1
    a6 = float(Spd.asOf(u, sstack(wand, 15, None, [("as", 10)]), arm)) if wand else -1
    a7 = float(Spd.asOf(u, IS(JString("Tool_Pickaxe_Iron"), 1), arm))
    a8 = float(Spd.asOf(u, None, arm))
    K.check(a2 == 25.0 and a3 == 0.0 and a4 == 0.0 and a5 == 0.0 and a6 == 0.0 and a7 == 0.0 and a8 == 0.0,
            "T + the door capped at 25; part.stats off = 0; as.cap 0 = 0; a bow (%s) / a wand (%s) / a pickaxe / an empty hand = 0: %s" % (bow, wand, [a2, a3, a4, a5, a6, a7, a8]))

    # ================================================================================== K the tick on an ECS shim + REAL effects
    jpz = JClass("javassist.ClassPool")(True)
    jpz.appendClassPath(B.SERVER_JAR)
    CTFz, CTMz = JClass("javassist.CtField"), JClass("javassist.CtNewMethod")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    CMPc, CTc, RFc = "com.hypixel.hytale.component.Component", "com.hypixel.hytale.component.ComponentType", "com.hypixel.hytale.component.Ref"
    cc_ = jpz.makeClass("com.hypixel.hytale.component.SkyyAsBuf", jpz.get("com.hypixel.hytale.component.CommandBuffer"))
    for src_ in ["F public static java.util.IdentityHashMap COMP = new java.util.IdentityHashMap();",
                 "public %s getComponent(%s r, %s t) { java.util.IdentityHashMap m = (java.util.IdentityHashMap) COMP.get(r); if (m == null) return null; return (%s) m.get(t); }" % (CMPc, RFc, CTc, CMPc)]:
        if src_.startswith("F "):
            cc_.addField(CTFz.make(src_[2:], cc_))
        else:
            cc_.addMethod(CTMz.make(src_, cc_))
    BufC = cc_.toClass(REFc.class_)
    Buf = JClass(BufC.getName())
    buf = us.allocateInstance(BufC)
    CTYc = JClass(CTc)
    MODc = JClass("java.lang.reflect.Modifier")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    fi_ = EMc.class_.getDeclaredField("instance")
    fi_.setAccessible(True)
    if fi_.get(None) is None:
        o_ = us.allocateInstance(EMc.class_)
        for fd_ in EMc.class_.getDeclaredFields():
            if fd_.getType() == CTYc.class_ and not MODc.isStatic(fd_.getModifiers()):
                fd_.setAccessible(True)
                fd_.set(o_, us.allocateInstance(CTYc.class_))
        fi_.set(None, o_)
    ESMm = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    fi2 = ESMm.class_.getDeclaredField("instance")
    fi2.setAccessible(True)
    if fi2.get(None) is None:
        o2 = us.allocateInstance(ESMm.class_)
        for fd_ in ESMm.class_.getDeclaredFields():
            if fd_.getType() == CTYc.class_ and not MODc.isStatic(fd_.getModifiers()):
                fd_.setAccessible(True)
                fd_.set(o2, us.allocateInstance(CTYc.class_))
        fi2.set(None, o2)
    ECCc = JClass("com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent")
    EFXc = JClass("com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect")
    AEEc = "com.hypixel.hytale.server.core.entity.effect.ActiveEntityEffect"
    ecc = ECCc()
    ref = us.allocateInstance(REFc.class_)
    fld(REFc, "index").setInt(ref, JInt(51))
    m_ = JClass("java.util.IdentityHashMap")()
    m_.put(ECCc.getComponentType(), ecc)
    Buf.COMP.put(ref, m_)
    ALL = [e for e in TIER_EFF if e] + AS_EFF

    def act():
        mm = ecc.getActiveEffects()
        return sorted(e for e in ALL if mm.get(JInt(int(EFXc.getAssetMap().getIndex(JString(e))))) is not None)

    def st():
        s_ = Spd.state(u)
        return [int(x) for x in s_[3]], float(s_[4][0]), [int(x) for x in s_[2]]

    def recheck():
        Spd.state(u)[2][0] = 0
        Spd.state(u)[2][1] = 0
    Spd.forget(u)
    kb = []
    Spd.tick(buf, ref, u, s_fast_as)
    A_, D_, L_ = st()
    if act() != sorted(["SkyyGear_Speed_Fast", "SkyyGear_Speed_As%02d" % (AS_STEP * int(Spd.asStep(JDouble(a0))))]) or A_[0] != A_[1] or D_ != a0:
        kb.append(("fast + step", act(), A_, D_))
    st1 = A_[1]
    Spd.tick(buf, ref, u, s_fast_as)
    if act() != sorted(["SkyyGear_Speed_Fast", AS_EFF[st1 - 1]]):
        kb.append(("again", act()))
    # lost step effect -> noted + put back
    lost0 = int(Spd.AN.get(2))
    ecc.removeEffect(ref, JInt(int(Spd.AIDX[st1 - 1])), buf)
    Spd.tick(buf, ref, u, s_fast_as)
    A_, D_, L_ = st()
    if int(Spd.AN.get(2)) != lost0 + 1 or act() != sorted(["SkyyGear_Speed_Fast", AS_EFF[st1 - 1]]) or A_[1] != st1 or A_[2] != 0:
        kb.append(("lost step", int(Spd.AN.get(2)) - lost0, act(), A_))
    # the door raises it to the cap
    door.put("banner", JObject(JDouble(30.0), "java.lang.Double"))
    br.put("gear:as:" + U, door)
    recheck()
    Spd.tick(buf, ref, u, s_fast_as)
    A_, D_, L_ = st()
    if act() != sorted(["SkyyGear_Speed_Fast", AS_EFF[4]]) or D_ != 25.0 or A_[1] != 5 or A_[2] != st1:
        kb.append(("door to the cap", act(), A_, D_))
    door.clear()
    # as.cap 7 -> step 1; as.cap 0 -> no step, the tier stays
    apply(as__cap="7", **BASE)
    recheck()
    Spd.tick(buf, ref, u, s_fast_as)
    A_, D_, L_ = st()
    if act() != sorted(["SkyyGear_Speed_Fast", AS_EFF[0]]) or D_ != 7.0 or A_[1] != 1:
        kb.append(("cap 7", act(), A_, D_))
    apply(as__cap="0", **BASE)
    recheck()
    Spd.tick(buf, ref, u, s_fast_as)
    A_, D_, L_ = st()
    if act() != ["SkyyGear_Speed_Fast"] or D_ != 0.0 or A_[1] != 0:
        kb.append(("cap 0", act(), A_, D_))
    apply(**BASE)
    # Medium + Attack Speed: only the step effect
    s_med_as = sstack(sw, 15, 1, [("as", 20)])
    Spd.tick(buf, ref, u, s_med_as)
    A_, D_, L_ = st()
    if act() != [AS_EFF[int(Spd.asStep(JDouble(D_))) - 1]] or L_[2] != -1:
        kb.append(("medium", act(), A_, D_, L_[2]))
    # swing.tiers off (fix round: "Off = all vanilla"): the tier effect AND the step effect go; the counted % stays (damage only); the /gear text says so
    Spd.FORCE_OFF = True
    Spd.tick(buf, ref, u, s_fast_as)
    A_, D_, L_ = st()
    txo = str(Spd.asText(u))
    if act() != [] or L_[2] != -1 or A_[0] != 0 or A_[1] != 0 or D_ != a0 or "swing.tiers OFF: damage only" not in txo:
        kb.append(("swing.tiers off", act(), A_, D_, L_[2], txo))
    Spd.FORCE_OFF = False
    # back on: the step comes back on the next re-check
    recheck()
    Spd.tick(buf, ref, u, s_fast_as)
    A_, D_, L_ = st()
    if act() != sorted(["SkyyGear_Speed_Fast", AS_EFF[int(Spd.asStep(JDouble(a0))) - 1]]) or A_[1] != int(Spd.asStep(JDouble(a0))):
        kb.append(("swing.tiers back on", act(), A_))
    # a bow / a tool: everything off
    Spd.tick(buf, ref, u, IS(JString("Tool_Pickaxe_Iron"), 1))
    if act() != [] or st()[0][1] != 0:
        kb.append(("tool", act(), st()[0]))
    # a stray step effect on a fresh player is removed on the first look
    Spd.forget(u)
    Spd.put(buf, ref, ecc, JInt(-1), JInt(3))
    stray = act()
    Spd.tick(buf, ref, u, sstack(sw, 15, 1, []))
    if stray != [AS_EFF[2]] or act() != [] or st()[0][1] != 0:
        kb.append(("stray", stray, act(), st()[0]))
    # refresh: a step effect with 1.4 s left is put back to 3 s on the 1 s re-check
    Spd.tick(buf, ref, u, s_fast_as)
    ae_ = ecc.getActiveEffects().get(JInt(int(Spd.AIDX[st1 - 1])))
    fld(JClass(AEEc), "remainingDuration").setFloat(ae_, JFloat(1.4))
    Spd.state(u)[2][1] = 0
    Spd.tick(buf, ref, u, s_fast_as)
    r_ = float(ecc.getActiveEffects().get(JInt(int(Spd.AIDX[st1 - 1]))).getRemainingDuration())
    if abs(r_ - 3.0) > 1e-5:
        kb.append(("refresh", r_))
    K.check(not kb, "K GearSpeed.tick on a REAL EffectControllerComponent with the jar's REAL step effects: the step beside the tier, a lost step noted "
            "(AN[2]) + put back, the door to the cap 25, as.cap 7 / 0, Medium (step only), swing.tiers off (no tier, no step - damage only; back on = the step again), a tool (all off), a stray "
            "step removed on the first look, refreshed to 3 s: %s" % kb)

    # ================================================================================== H the hit weight
    DMGc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DCSc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
    DSqc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCalculatorSystems$DamageSequence")
    DCSYc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCalculatorSystems")
    phys = int(DCSc.getAssetMap().getIndex(JString("Physical")))
    # the bare boot cannot walk the swing (some vanilla Selector steps fail to decode here, so the tier walk is empty): the tier walk's result is
    # seeded with a real DamageCalculator object (the static phase proved every step copy reaches the Fast copy's own damage steps by id)
    DCALC = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.combat.DamageCalculator")
    tapc = us.allocateInstance(DCALC.class_)
    nm_ = JClass("java.util.IdentityHashMap")()
    nm_.put(tapc, JClass("java.lang.Boolean").TRUE)
    Spd.NORM.put(JString(sw + "#2"), OA([nm_, JObject(JLong(int(SysJ.currentTimeMillis()) + 3600000), "java.lang.Long")]))
    tap = [tapc]

    def dmg(calc):
        d_ = DMGc(None, JInt(phys), JFloat(10.0))
        sq_ = us.allocateInstance(DSqc.class_)
        fld(DSqc, "damageCalculator").set(sq_, calc)
        d_.putMetaObject(DCSYc.DAMAGE_SEQUENCE, sq_)
        return d_
    hb = []
    Spd.forget(u)
    Spd.tick(buf, ref, u, s_fast_as)
    A_, D_, L_ = st()
    d1 = dmg(tap[0])
    w_in = float(Spd.hitWeight(d1, u, s_fast_as))
    if abs(w_in - min(1.0, float(Spd.cyc(0, 2, A_[1]))) * (1 + D_ / 100.0)) > 1e-9:
        hb.append(("in the window", w_in))
    Spd.state(u)[2][4] = int(SysJ.currentTimeMillis()) - 5000
    d2 = dmg(tap[0])
    w_out = float(Spd.hitWeight(d2, u, s_fast_as))
    last = Spd.LAST.get()
    if abs(w_out - float(Spd.cyc(0, 2, A_[1])) * (1 + D_ / 100.0)) > 1e-9 or last is None or abs(float(last[1]) - float(Spd.cyc(0, 2, A_[1]))) > 1e-12:
        hb.append(("after", w_out, None if last is None else float(last[1])))
    # DPS: hit weight / the cycle the swing ran = 1 + as, for every tier x every as on a 5 % grid and between
    dbad = []
    for t in range(4):
        for av in (0.0, 3.0, 5.0, 7.0, 12.0, 19.9, 25.0):
            st_ = int(Spd.asStep(JDouble(av)))
            s_ = Spd.state(u)
            s_[2][2], s_[2][3], s_[2][4] = (t if t != 1 else -1), (t if t != 1 else -1), 0
            s_[3][1], s_[3][2] = st_, st_
            s_[4][0] = av
            wv = float(Spd.hitWeight(dmg(tap[0]), u, s_fast_as))
            cy = float(Spd.cyc(0, t, st_))
            if abs(wv / cy - (1.0 + av / 100.0)) > 1e-9:
                dbad.append((t, av, wv, cy))
    if dbad:
        hb.append(("dps", dbad[:3]))
    # the swap window over the step: Fast +10 % -> Fast +20 % a moment ago = the faster (smaller) of the two
    s_ = Spd.state(u)
    s_[2][2], s_[2][3], s_[2][4] = 2, 2, int(SysJ.currentTimeMillis())
    s_[3][1], s_[3][2] = 2, 4
    s_[4][0] = 20.0
    wsw = float(Spd.hitWeight(dmg(tap[0]), u, s_fast_as))
    if abs(wsw - min(float(Spd.cyc(0, 2, 2)), float(Spd.cyc(0, 2, 4))) * 1.2) > 1e-9:
        hb.append(("step swap", wsw))
    # as 0 = exactly the 0.3.50 rule (weight(f, t)); a non-tap calculator x1; a pickaxe x1
    s_[2][2], s_[2][3], s_[2][4] = 2, 2, 0
    s_[3][1], s_[3][2] = 0, 0
    s_[4][0] = 0.0
    w0 = float(Spd.hitWeight(dmg(tap[0]), u, s_fast_as))
    s_[4][0] = 10.0
    other = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.combat.DamageCalculator")
    oc = us.allocateInstance(other.class_)
    wx = float(Spd.hitWeight(dmg(oc), u, s_fast_as))
    wt = float(Spd.hitWeight(dmg(tap[0]), u, IS(JString("Tool_Pickaxe_Iron"), 1)))
    Spd.FORCE_OFF = True
    s_[2][2] = -1
    s_[3][1] = 2
    woff = float(Spd.hitWeight(dmg(tap[0]), u, s_fast_as))
    s_[4][0] = 0.0
    woff0 = float(Spd.hitWeight(dmg(tap[0]), u, s_fast_as))
    Spd.FORCE_OFF = False
    if abs(w0 - float(Spd.weight(0, 2))) > 1e-12 or wx != 1.0 or wt != 1.0 or abs(woff - float(Spd.cyc(0, 1, 2)) * 1.1) > 1e-9 or woff0 != 1.0:
        hb.append(("rules", w0, wx, wt, woff, woff0))
    K.check(not hb and int(Spd.AN.get(0)) > 0, "H hitWeight on real Damage objects: the cycle the swing ran x (1 + as) (damage per second = 1 + as for every "
            "tier x as), the swap window over tier AND step, LAST = the cycle only, as 0 = the 0.3.50 weight, a non-tap step / a pickaxe x1, "
            "swing.tiers off + as = the Medium step copy, off + no as = x1: %s" % hb)
    Spd.forget(u)

    # ================================================================================== L lines, rolls, texts
    ml = str(View.modLine(JString("as"), 7))
    K.check(ml == "Attack Speed: +7% (melee swings)" and not bool(View.dim(JString("as"))) and not bool(View.later(JString("as")))
            and int(Defs.S_LIVE[I_AS]) == 1, "L the line: %r, not grey, live" % ml)
    pool0 = [int(x) for x in Roll.pool(0, JString(sw))]
    poolA = [int(x) for x in Roll.pool(2, JString(helm))]
    apply(stats__as="10,5", **BASE)
    pool1 = [int(x) for x in Roll.pool(0, JString(sw))]
    apply(**BASE)
    K.check(I_AS not in pool0 and I_AS not in poolA and I_AS in pool1, "L weight 0 = Attack Speed never rolls (weapon / armor); a Server Setup weight 5 rolls it")
    Spd.tick(buf, ref, u, s_fast_as)
    tx = str(Spd.asText(u))
    ds = str(Spd.describe(JString(sw), Data.effective(JString(sw), s_fast_as.getMetadata()), u))
    rt = str(Spd.readyText())
    K.check(tx.startswith("attack speed ") and "cap 25%" in tx and "swing step +" in tx and "attack speed " in ds and "Attack Speed live (melee swings, 5 steps of +5%, cap 25%)" in rt,
            "L texts: %s | %s" % (tx, rt[-90:]))
    K.notes.append("L /gear read line: " + ds[:400])
    hn = [str(Spd.asHint(JDouble(a_), s_, JDouble(c_), o_)) for a_, s_, c_, o_ in ((3.0, 0, 25.0, True), (7.0, 1, 25.0, True), (25.0, 5, 25.0, True),
          (12.0, 2, 12.0, True), (3.0, 0, 25.0, False), (0.0, 0, 25.0, True))]
    K.check(hn[0] == "; next swing step at +5% (under 5%: damage only, no faster swing yet)" and hn[1] == "; next swing step at +10%"
            and hn[2:] == ["", "", "", ""], "L asHint: under 5 %% = damage only, next step named; none at the top / past as.cap / swing.tiers off / 0: %s" % hn)
    Spd.forget(u)

    # ================================================================================== M migrateAs51
    cfgd = os.path.join(scratch, "cfg")
    os.makedirs(cfgd, exist_ok=True)
    fc = os.path.join(cfgd, "config.properties")
    t50 = fresh.replace(str(Cfg.H51_MARK) + "\n", "").replace("\nstats.as=10,0\n", "\nstats.as=10,5\n")
    assert "\nstats.as=10,5\n" in t50 and str(Cfg.H51_MARK_ID) not in t50
    raw = t50.replace("\n", "\r\n").encode("latin-1")
    open(fc, "wb").write(raw)
    Cfg.FILE = Paths.get(fc)
    m1 = str(Cfg.migrateAs51())
    t1 = open(fc, "rb").read()
    tt1 = t1.decode("latin-1")
    K.check("\r\nstats.as=10,0\r\n" in tt1 and "stats.as=10,5" not in tt1 and str(Cfg.H51_MARK_ID) in tt1 and tt1.count("\n") == tt1.count("\r\n")
            and len(tt1) - len(raw) < len(str(Cfg.H51_MARK)) + 10, "M migrateAs51: stats.as 10,5 -> 10,0, the marker added, CRLF kept, nothing else changed: %s" % m1[:200])
    hist = os.path.join(cfgd, "config-history")
    K.check(os.path.isdir(hist) and any(open(os.path.join(hist, f_), "rb").read() == raw for f_ in os.listdir(hist) if os.path.isfile(os.path.join(hist, f_))),
            "M a History snapshot of the old bytes first")
    chl = os.path.join(cfgd, "config-changes.log")
    K.check(os.path.isfile(chl) and "SkyyGear 0.3.51\t-\tupdate\tstats.as\t10,5\t10,0\tok" in open(chl, encoding="latin-1").read(), "M one change-log row (Undo)")
    K.eq(str(Cfg.migrateAs51()), "", "M a second start: nothing (the marker)")
    K.check(open(fc, "rb").read() == t1, "M ... and the file is byte-identical")
    open(fc, "w", encoding="latin-1", newline="").write(t50.replace("\nstats.as=10,5\n", "\nstats.as=12,7\n"))
    m2 = str(Cfg.migrateAs51())
    K.check("stats.as=12,7" in open(fc, encoding="latin-1").read() and "stats.as=12,7 kept" in m2, "M a hand-edited stats.as is kept + noted: %s" % m2[-200:])
    Cfg.FILE = None
    K.save()


# ====================================================================================================== D: start twice on the live copy
def run_live(out, jar, scratch, home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    fc = os.path.join(home, "config.properties")
    c0 = open(fc, "rb").read() if os.path.isfile(fc) else None
    K.check(c0 is not None, "D the live copy has a config.properties")
    K.notes.append("D the live copy's stats.as line: %s" % [l for l in c0.decode("latin-1").splitlines() if l.startswith("stats.as=")])
    Paths = JClass("java.nio.file.Paths")
    Cfg.FILE = Paths.get(fc)
    Cfg.DIR = Paths.get(home)
    MIG = ["migrate0326", "migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39", "migrateUt28", "migrateCan2", "migrateAs51"]
    m0 = "".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    c1 = open(fc, "rb").read()
    m1 = "".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    K.notes.append("D start 1: one-time updates said %r" % m0[:600])
    K.check(open(fc, "rb").read() == c1 and m1 == "", "D start 2 changes nothing")
    K.check(str(Cfg.H51_MARK_ID) in c1.decode("latin-1"), "D the live copy carries the migrateAs51 marker now")
    st = [l for l in c1.decode("latin-1").splitlines() if l.startswith("stats.as=")]
    had = [l for l in c0.decode("latin-1").splitlines() if l.startswith("stats.as=")]
    K.check((had == ["stats.as=10,5"] and st == ["stats.as=10,0"]) or (had != ["stats.as=10,5"] and st == had), "D stats.as: %s -> %s" % (had, st))
    K.check(float(Cfg.AS_CAP) == 25.0 and int(Cfg.S_W[int(JClass(PKG + "GearDefs").I_AS)]) == (0 if had == ["stats.as=10,5"] else int(Cfg.S_W[int(JClass(PKG + "GearDefs").I_AS)])),
            "D the live copy reads as.cap 25 (no line) and the Attack Speed weight 0")
    dl = [l for l in c0.decode("latin-1").splitlines()]
    dn = [l for l in c1.decode("latin-1").splitlines()]
    extra = [l for l in dn if l not in dl]
    K.check(all(l.startswith("stats.as=") or str(Cfg.H51_MARK_ID) in l or str(Cfg.H50_MARK_ID) in l or l.strip() == "" or "SkyyGear 0.3.5" in l for l in extra) or c1 == c0,
            "D only the 0.3.50 / 0.3.51 updates touched the file: %s" % extra[:5])
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("engine", run_engine), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
