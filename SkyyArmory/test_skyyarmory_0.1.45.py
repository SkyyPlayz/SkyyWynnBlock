"""Harness for SkyyArmory 0.1.45 (sig2: the 4 family signatures Whirling Staff / Flurry / Kunai Fan / Page Storm; tools/armory_0_1_45_patch.py).
Build first:
    python tools/armory_0_1_45_patch.py && python SkyyArmory/build_skyyarmory_0.1.45.py
    python SkyyArmory/test_skyyarmory_0.1.45.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S   static   the patch re-runs to identical bytes; two new classes (ArmorySig2, Sig2Job), no command / system; the jar vs 0.1.44 entry by
               entry: added = the 2 classes + the 16 signature files (4 roots / casts / launches / markers), changed non-class = manifest +
               exactly the 69 item files, each = the 0.1.44 JSON + Interactions.Ability1 (its family's root) + the wand's meter + the wand's
               ready look ONLY; the roots / casts / launches = the wand's shape (StatsCondition 100 % -> ChangeStat -100 % -> the marker);
               the markers = the wand's Ricochet marker byte for byte; the wand's 4 signature files + 15 wands byte-identical; no lang change
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.44 -> 0.1.45: exactly the planned members (EXPECT) + the 2 new classes; Rico / RicoChain identical (the wand Ricochet
               unchanged); non-class entries: the S list exactly
  X   exec     EXECUTED in the JVM: the rows' defaults (useDefaults -> applySig2) and their clamps; famOf for all 69 ids + controls; the
               charge rules (gainFam matrix: a Bo / fist swing WITH the DamageSequence charges, without it / a projectile never; a kunai
               projectile charges, its melee never; a book never through onHit; off = never), gainAmt x w, bookAmt, the meter fill from 0
               to full (Bo 10 hits, fist 20 jabs, kunai 10 hits, book 10 single-target bursts / 4 of 3); the timing (gapMs, the job's due / stepped through all
               its pulses, the 20 s timeout > every job at the rows' maxima); the hit numbers (baseOf vs Monk / Kunai / the book table); the geometry (inside, rotY, fanDirs,
               fanPick incl. the nearest-on-the-line rule, tally / the 3+ bonus, keepNearest = the 64 cap); the 4 roots in ROOT_CHECK; the marker codes (13001-13004, Ricochet 13000 kept);
               armory:fn:sig answers for every family + the live rows + off; the glue edges (onHit / bookGain / marker / step / run with
               no engine: quiet, the job dropped when its caster is gone, kept while it waits; TravWorld.idle sees the job); SkyyGear 0.3.43's
               GearSigX.sigOf through the bridge (when its jar is present)
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration + load): 0.1.45 writes no row, the new keys read
               their defaults
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the server-side hits on real mobs, the meter rising on a real swing / kunai / burst, the
ready glow on the new models, the cast poses + sounds, the client pressing Ability 1 on these items.
"""
import os, sys, json, hashlib, subprocess, zipfile, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sig2fix", "arm")]
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.45", "0.1.44"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyarmory_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyarmory_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "armory_0_1_45_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
GEAR_JAR = os.path.join(ROOT, "SkyyGear", "SkyyGear-0.3.43.jar")
_SG2F = ["SG2_%s" % k for k in ("BO_ON", "BO_DMG", "BO_HITS", "BO_R", "BO_SEC", "BO_GAIN", "FI_ON", "FI_DMG", "FI_JABS", "FI_R", "FI_GAP", "FI_HEAVY",
                                  "FI_KNOCK", "FI_GAIN", "KU_ON", "KU_DMG", "KU_N", "KU_SPREAD", "KU_R", "KU_BONUS", "KU_GAIN", "BK_ON", "BK_DMG",
                                  "BK_TICKS", "BK_R", "BK_SEC", "BK_GAIN", "REFUND")]
EXPECT = {"ArmoryCfg": ["+f " + f_ for f_ in _SG2F] + ["+m applySig2", "~<clinit>", "~m apply",          # the 28 rows + their loader
                                                       "~m load", "~m reloadAll", "~m useDefaults"],          # the version text / DEF_CFG
          "ArmoryDefs": ["+f SG2_CODE0", "+f SG2_MARK", "~<clinit>", "~m pids"],          # the 4 marker codes (+ the pack-check id lists)
          "ArmoryCheck": ["~m packCheck", "~m packOf"],          # the version text
          "ArmoryHitSys": ["~m handle"],          # ArmorySig2.onHit
          "ArmorySigFn": ["~m sigOf"],          # ArmorySig2.answer
          "ArmoryTrav": ["~m added", "~m bookBurst"],          # the marker dispatch; the Page Burst charge
          "TravWorld": ["+f sig2", "~c ", "~m idle", "~m run"],          # the jobs list + ArmorySig2.run
          "SkyyArmoryPlugin": ["~m setup", "~m start"],          # the version text + the status line
          "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"],
          "CfgRows2": ["~<clinit>"]}          # the kit: the 28 new rows + the default file
if "--expect-dump" in sys.argv:
    EXPECT = {}
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040",
        "migrateP5")
ROOTS = ["SkyyArmory_Sig_Whirl", "SkyyArmory_Sig_Flurry", "SkyyArmory_Sig_KunaiFan", "SkyyArmory_Sig_PageStorm"]
NK = ["Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"]
MET = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"] + [w + "_SkyWynn" for w in NK]
FAM_IDS = [["Weapon_Bo_" + m for m in MET] + ["Weapon_Bo_UT_Turnstile", "Weapon_Staff_Bo_Wood", "Weapon_Staff_Bo_Bamboo"],
           ["Weapon_Fist_Gauntlets_" + m for m in MET] + ["Weapon_Fist_Wraps_" + c for c in ("Linen", "Cotton", "Silk", "Cindercloth", "Shadoweave")],
           ["Weapon_Kunai_" + m for m in ["Crude"] + MET], ["Weapon_Spellbook_" + m for m in MET]]
WAND_SIG_FILES = ["Server/Item/RootInteractions/Weapons/Wand/SkyyArmory/SkyyArmory_Wand_Signature.json",
                  "Server/Item/Interactions/Weapons/Wand/SkyyArmory/SkyyArmory_Wand_Signature_Cast.json",
                  "Server/Item/Interactions/Weapons/Wand/SkyyArmory/SkyyArmory_Wand_Signature_Launch.json",
                  "Server/Projectiles/Player/SkyyArmory/SkyyArmory_Wand_Ricochet.json"]


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def planned_entries():
    """(added non-class entries, changed non-class entries) the round plans, from the two jars"""
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    na, nb = set(za.namelist()), set(zb.namelist())
    add = sorted(n for n in nb - na if not n.endswith(".class"))
    items = {}
    for n in na & nb:
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            items[os.path.basename(n)[:-5]] = n
    chg = sorted(["manifest.json"] + [items[i] for f in FAM_IDS for i in f])
    return add, chg


# ---------------------------------------------------------------------------------------------------------------- C: compare (+ the planned assets)
_ORIG_COMPARE = HK.run_compare


def compare_with_assets(out, jar, old_jar, pkg, expect, added, removed=()):
    """harness_kit's compare, whose fixed 'non-class entries: manifest.json only' check is replaced by the round's planned list"""
    _ORIG_COMPARE(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    ed = sorted(n for n in ea | eb if n not in ea or n not in eb or za.read(n) != zb.read(n))
    add, chg = planned_entries()
    kept = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    gone = len(d["fails"]) - len(kept)
    want = sorted(add + chg)
    if ed == want:
        d["ok"] += 1
    else:
        kept.append("C: non-class entries changed = the plan: extra %s, missing %s" % (sorted(set(ed) - set(want))[:6], sorted(set(want) - set(ed))[:6]))
    d["fails"] = kept
    d["notes"].append("C: %d non-class entries changed (%d added files + %d changed incl. manifest) - the planned list (the kit's manifest-only check "
                      "replaced: %d)" % (len(ed), len(add), len(chg), gone))
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = compare_with_assets


# ---------------------------------------------------------------------------------------------------------------- S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyArmory 0.1.45 - build script') and g.count('VERSION = "0.1.45"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count("makeClass(") - o.count("makeClass(")),
         (0, 0, 2), "S no new system / command; two new classes")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    add, chg = planned_entries()
    K.eq(sorted(nb - na), sorted(add + ["com/skyy/armory/ArmorySig2.class", "com/skyy/armory/Sig2Job.class"]), "S added = the 2 classes + the signature files")
    K.eq(sorted(na - nb), [], "S nothing removed")
    K.eq(len(add), 16, "S 16 new signature files")
    nc = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(nc, chg, "S changed non-class = manifest + exactly the 69 item files")
    K.eq(sum(len(f) for f in FAM_IDS), 69, "S 69 items")
    J = lambda z, n: json.loads(z.read(n).decode("utf-8"))
    w_old = J(za, "Server/Item/Items/Weapon/Wand/Weapon_Wand_Iron.json")
    meter, look = w_old["Weapon"], w_old["ItemAppearanceConditions"]
    K.eq(meter, {"EntityStatsToClear": ["SignatureEnergy"], "StatModifiers": {"SignatureEnergy": [{"Amount": 20, "CalculationType": "Additive"}]}},
         "S the wand meter (the sword's 20) is the reference")
    bad = []
    for f, ids in enumerate(FAM_IDS):
        for i in ids:
            n = [x for x in chg if x.endswith("/" + i + ".json")]
            if len(n) != 1:
                bad.append((i, "path", n))
                continue
            a, b = J(za, n[0]), J(zb, n[0])
            exp = json.loads(json.dumps(a))
            exp["Interactions"]["Ability1"] = ROOTS[f]
            w = dict(a["Weapon"])
            w.update(meter)
            exp["Weapon"] = w
            exp["ItemAppearanceConditions"] = look
            if b != exp or "Ability1" in a["Interactions"]:
                bad.append((i, sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))))
    K.eq(bad, [], "S every changed item = 0.1.44 + Ability1 (its family root) + the wand meter + the wand ready look ONLY")
    wr = J(zb, WAND_SIG_FILES[0])
    wc = J(zb, WAND_SIG_FILES[1])
    wl = J(zb, WAND_SIG_FILES[2])
    wm = zb.read(WAND_SIG_FILES[3])
    shp = []
    for f, r in enumerate(ROOTS):
        rp = "Server/Item/RootInteractions/Weapons/Signature/SkyyArmory/%s.json" % r
        cpth = "Server/Item/Interactions/Weapons/Signature/SkyyArmory/%s_Cast.json" % r
        lp = "Server/Item/Interactions/Weapons/Signature/SkyyArmory/%s_Launch.json" % r
        mp = "Server/Projectiles/Player/SkyyArmory/%s_Mark.json" % r
        if sorted([rp, cpth, lp, mp]) != sorted(x for x in add if os.path.basename(x).startswith(r + ".") or os.path.basename(x).startswith(r + "_")):
            shp.append((r, "files"))
            continue
        ro, co, lo = J(zb, rp), J(zb, cpth), J(zb, lp)
        tag = {"Attack": ["Melee"]} if f < 2 else {"Attack": ["Ranged"]}
        if ro != {"RequireNewClick": True, "Interactions": [r + "_Cast"], "Tags": tag}:
            shp.append((r, "root", ro))
        cexp = json.loads(json.dumps(wc))
        cexp["Next"]["Next"] = r + "_Launch"
        if co != cexp:
            shp.append((r, "cast", co))
        if sorted(lo) != sorted(wl) or lo["Type"] != "LaunchProjectile" or lo["ProjectileId"] != r + "_Mark" or lo["RunTime"] != wl["RunTime"] \
                or sorted(lo["Effects"]) != ["ItemAnimationId", "WorldSoundEventId"]:
            shp.append((r, "launch", lo))
        if zb.read(mp) != wm:
            shp.append((r, "marker differs from the Ricochet marker"))
    K.eq(shp, [], "S roots / casts / launches = the wand's shape; markers = the Ricochet marker byte for byte")
    K.notes.append("S launch poses + sounds: %s" % [(r, J(zb, "Server/Item/Interactions/Weapons/Signature/SkyyArmory/%s_Launch.json" % r)["Effects"]) for r in ROOTS])
    K.check(wr["Interactions"] == ["SkyyArmory_Wand_Signature_Cast"] and all(za.read(x) == zb.read(x) for x in WAND_SIG_FILES),
            "S the wand's 4 signature files byte-identical (Ricochet unchanged)")
    wands = [n for n in nb if n.startswith("Server/Item/Items/Weapon/Wand/") and n.endswith(".json")]
    K.check(len(wands) >= 15 and all(za.read(x) == zb.read(x) for x in wands if x in na), "S every wand item byte-identical (%d)" % len(wands))
    K.check(not [n for n in chg if "/Languages/" in n or n.endswith(".lang")], "S no lang file changed")
    for i in ("Weapon_Bo_Iron", "Weapon_Kunai_Iron"):
        n = [x for x in chg if x.endswith("/" + i + ".json")][0]
        K.notes.append("S %s now: Interactions %s, Weapon %s" % (i, J(zb, n)["Interactions"], J(zb, n)["Weapon"]))
    # the default config file carries the 28 rows once, each with its comment
    dc = [x for x in g.split("\n") if x.startswith("    ('sig.") and ("'monk'" in x or "_MK," in x or "'kunai'" in x or "'book'" in x or "_SG," in x)]
    K.check(len([x for x in dc if any(x.startswith("    ('sig.%s." % k) for k in ("bo", "fist", "kunai", "book")) or x.startswith("    ('sig.refundMiss'")]) == 28,
            "S 28 new rows in the script")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray, JObject, JInt, JDouble, JBoolean, JLong
    K = HK.Child(out)
    cp = [B.SERVER_JAR, B.JAVASSIST, jar] + ([GEAR_JAR] if os.path.isfile(GEAR_JAR) else [])
    HK.jvm(cp, verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, Defs, S2, Job, Fn = (JClass(PKG + n) for n in ("ArmoryCfg", "ArmoryDefs", "ArmorySig2", "Sig2Job", "ArmorySigFn"))
    Monk, Kunai, TW = JClass(PKG + "Monk"), JClass(PKG + "Kunai"), JClass(PKG + "TravWorld")
    UUID = JClass("java.util.UUID")
    D_ = lambda a: JArray(JDouble)([float(x) for x in a])
    B_ = lambda a: JArray(JBoolean)([bool(x) for x in a])
    Cfg.useDefaults()
    # ---- the rows: defaults + clamps (applySig2 through apply)
    dflt = dict(SG2_BO_ON=True, SG2_BO_DMG=0.6, SG2_BO_HITS=4, SG2_BO_R=3.0, SG2_BO_SEC=1.5, SG2_BO_GAIN=2.0, SG2_FI_ON=True, SG2_FI_DMG=0.5,
                SG2_FI_JABS=6, SG2_FI_R=4.0, SG2_FI_GAP=0.12, SG2_FI_HEAVY=25, SG2_FI_KNOCK=1.0, SG2_FI_GAIN=1.0, SG2_KU_ON=True, SG2_KU_DMG=0.8,
                SG2_KU_N=5, SG2_KU_SPREAD=30, SG2_KU_R=20, SG2_KU_BONUS=1.0, SG2_KU_GAIN=2.0, SG2_BK_ON=True, SG2_BK_DMG=1.0, SG2_BK_TICKS=4,
                SG2_BK_R=5.0, SG2_BK_SEC=2.0, SG2_BK_GAIN=2.0, SG2_REFUND=True)
    got = dict((k, (bool(getattr(Cfg, k)) if isinstance(v, bool) else (int(getattr(Cfg, k)) if isinstance(v, int) else round(float(getattr(Cfg, k)), 6)))) for k, v in dflt.items())
    K.eq(got, dflt, "X useDefaults -> applySig2: the 28 defaults")
    Pr = JClass("java.util.Properties")
    pp = Pr()
    for k_, v_ in (("sig.bo.hits", "99"), ("sig.bo.radius", "0.1"), ("sig.fist.gap", "9"), ("sig.kunai.count", "-3"), ("sig.book.enabled", "off"),
                   ("sig.kunai.spread", "abc"), ("sig.refundMiss", "false")):
        pp.setProperty(k_, v_)
    Cfg.applySig2(pp)
    K.eq((int(Cfg.SG2_BO_HITS), float(Cfg.SG2_BO_R), float(Cfg.SG2_FI_GAP), int(Cfg.SG2_KU_N), bool(Cfg.SG2_BK_ON), int(Cfg.SG2_KU_SPREAD), bool(Cfg.SG2_REFUND),
          float(Cfg.SG2_BO_DMG)), (10, 1.0, 0.5, 1, False, 30, False, 0.6), "X applySig2 clamps like the kit (max / min / bad text = default; a missing key = its default)")
    Cfg.useDefaults()
    # ---- families
    fams = {}
    for f, ids in enumerate(FAM_IDS):
        for i in ids:
            fams[i] = int(S2.famOf(JString(i)))
    K.eq(sorted(set((i, f) for f, ids in enumerate(FAM_IDS) for i in ids) - set(fams.items())), [], "X famOf: all 69 ids -> their family")
    ctl = ["Weapon_Wand_Iron", "Weapon_Wand_UT_SecondOpinion", "Weapon_Staff_Iron", "Weapon_Sword_Iron", "Weapon_Wand_SoulCage_Iron",
           "Weapon_GreatShield_Iron", "Weapon_Daggers_Iron", "Weapon_Staff_UT_Loophole", "", None]
    K.eq([int(S2.famOf(None if i is None else JString(i))) for i in ctl], [-1] * len(ctl), "X famOf: wands / staffs / swords / cages / shields / none -> -1")
    K.eq([bool(S2.heavy(JString(i))) for i in ("Weapon_Fist_Gauntlets_Iron", "Weapon_Fist_Gauntlets_Lumen_SkyWynn", "Weapon_Fist_Wraps_Silk", "Weapon_Bo_Iron")],
         [True, True, False, False], "X heavy = gauntlets only")
    # ---- the charge rules
    hands = ["Weapon_Bo_Iron", "Weapon_Fist_Wraps_Linen", "Weapon_Kunai_Iron", "Weapon_Spellbook_Iron", "Weapon_Sword_Iron"]
    mat = [[int(S2.gainFam(JString(h), s)) for s in range(4)] for h in hands]
    K.eq(mat, [[0, -1, -1, -1], [1, -1, -1, -1], [-1, -1, 2, -1], [-1, -1, -1, -1], [-1, -1, -1, -1]],
         "X gainFam: Bo / fist swing WITH the DamageSequence only; kunai projectile only; a book never here; a sword never")
    K.eq(int(S2.gainFam(JString("Weapon_Bo_UT_Turnstile"), 0)), 0, "X the Untiered Turnstile charges as a Bo")
    Cfg.SG2_BO_ON = False
    K.eq(int(S2.gainFam(JString("Weapon_Bo_Iron"), 0)), -1, "X sig.bo.enabled off -> no charge")
    Cfg.SG2_BO_ON = True
    K.eq([round(float(S2.gainAmt(f, w)), 4) for f, w in ((0, 1.0), (0, 0.7), (1, 0.5), (2, 1.4), (3, 0.5), (0, 9.0), (0, -1.0), (-1, 1.0))],
         [2.0, 1.4, 0.5, 2.8, 2.0, 2.0, 2.0, 0.0], "X gainAmt: x the speed weight (books never; a weight out of 0..4 = 1)")
    K.eq([float(S2.bookAmt(JString(h), n)) for h, n in (("Weapon_Spellbook_Iron", 3), ("Weapon_Spellbook_Iron", 0), ("Weapon_Kunai_Iron", 3))],
         [6.0, 0.0, 0.0], "X bookAmt: + charge (2) per enemy the Page Burst hit, a book in hand only")
    K.eq([float(S2.fill(c, m, a)) for c, m, a in ((0, 20, 2), (19, 20, 2), (20, 20, 2), (0, 0, 2), (5, 20, 0))], [2.0, 20.0, -1.0, -1.0, -1.0],
         "X fill: + amount, clamped at the meter; full / no meter / nothing = no write")

    def hits_to_full(amt):
        cur, n = 0.0, 0
        while n < 1000:
            v = float(S2.fill(cur, 20.0, amt))
            if v < 0:
                break
            cur, n = v, n + 1
        return n
    full = [hits_to_full(float(S2.gainAmt(0, 1.0))), hits_to_full(float(S2.gainAmt(1, 1.0))), hits_to_full(float(S2.gainAmt(2, 1.0))),
            hits_to_full(float(S2.bookAmt(JString("Weapon_Spellbook_Iron"), 1))), hits_to_full(float(S2.bookAmt(JString("Weapon_Spellbook_Iron"), 3)))]
    K.eq(full, [10, 20, 10, 10, 4], "X FIX B1 the meter (20) fills from 0: Bo 10 hits, fist 20 jabs, kunai 10 hits, book 10 single-target bursts "
         "(Mage.md lock ~8-10) / 4 bursts of 3 enemies")
    # ---- timing + numbers
    K.eq([int(S2.gapMs(0, False)), int(S2.gapMs(1, False)), int(S2.gapMs(1, True)), int(S2.gapMs(2, False)), int(S2.gapMs(3, False))], [500, 120, 150, 0, 667],
         "X gapMs: spin 1.5 s / 3, jab 0.12 s (gauntlets +25 %), the fan at once, the storm 2 s / 3")
    K.eq([int(S2.pulses(f)) for f in range(4)], [4, 6, 1, 4], "X pulses: 4 spin hits, 6 jabs, 1 fan, 4 storm hits")
    K.eq([round(float(S2.dmgX(f, h)), 4) for f, h in ((0, False), (1, False), (1, True), (2, False), (3, False))], [0.6, 0.5, 0.625, 0.8, 1.0],
         "X dmgX: x a hit per family (gauntlets +25 %)")
    K.eq([float(S2.radius(f)) for f in range(4)], [3.0, 4.0, 20.0, 5.0], "X radius / reach / range")
    bi = int(Defs.bookIndex(JString("Weapon_Spellbook_Iron")))
    bases = [float(S2.baseOf(0, JString("Weapon_Bo_Iron"))), float(S2.baseOf(0, JString("Weapon_Bo_UT_Turnstile"))), float(S2.baseOf(0, JString("Weapon_Staff_Bo_Wood"))),
             float(S2.baseOf(1, JString("Weapon_Fist_Gauntlets_Iron"))), float(S2.baseOf(2, JString("Weapon_Kunai_Iron"))),
             float(S2.baseOf(3, JString("Weapon_Spellbook_Iron")))]
    want = [float(Monk.boHit(JString("Weapon_Bo_Iron"))), float(Monk.boHit(JString("Weapon_Bo_Iron"))), 5.0, float(Monk.fistHit(JString("Weapon_Fist_Gauntlets_Iron"))),
            float(Kunai.hitOf(int(Defs.kunaiIndex(JString("Weapon_Kunai_Iron"))))), float(Defs.B_DMG[bi]) * float(Cfg.BOOK_K) / float(Defs.BOOK_KDEF)]
    K.eq(bases, want, "X baseOf: the Bo swing (Turnstile = its Iron base, vanilla Bo 5), the gauntlet jab, the kunai hit, the Page Burst hit x book.k / 0.4")
    K.check(all(b > 0 for b in bases) and float(S2.baseOf(0, JString("Weapon_Sword_Iron"))) == 0.0 and float(S2.baseOf(3, None)) == 0.0, "X baseOf > 0; a wrong id = 0")
    K.notes.append("X hit numbers (Bo Iron, Turnstile, vanilla Bo, Iron gauntlet jab, Iron kunai, Iron book): %s" % bases)
    # ---- the geometry
    ins = list(S2.inside(D_([2.9, 3.1, 0, 0, 1]), D_([0.9, 0.9, 4.0, 3.8, 0.9]), D_([0, 0, 0, 0, 1]), B_([1, 1, 1, 1, 0]), 0.0, 0.9, 0.0, 3.0))
    K.eq([bool(x) for x in ins], [True, False, False, True, False], "X inside: 2.9 in / 3.1 out on the flat, 3.1 above out / 2.9 in, not-ok out")
    r90 = [round(float(x), 6) for x in S2.rotY(D_([1, 0, 0]), 90.0)]
    K.eq(r90, [0.0, 0.0, 1.0], "X rotY: +90 degrees turns x into z")
    fd = list(S2.fanDirs(D_([1, 0, 0]), 5, 30.0))
    import math
    angs = [round(math.degrees(math.atan2(fd[3 * k + 2], fd[3 * k])), 4) for k in range(5)]
    K.eq(angs, [-15.0, -7.5, 0.0, 7.5, 15.0], "X fanDirs: 5 kunai over 30 degrees, evenly")
    K.eq([round(float(x), 6) for x in S2.fanDirs(D_([0, 0, 1]), 1, 30.0)], [0.0, 0.0, 1.0], "X fanDirs: one kunai = the aim")
    K.eq(len(S2.fanDirs(None, 5, 30.0)), 0, "X fanDirs: no aim = none")
    E = (0.0, 1.6, 0.0)
    dirs = S2.fanDirs(D_([1, 0, 0]), 5, 30.0)
    close = [int(x) for x in S2.fanPick(D_([2]), D_([1.6]), D_([0]), D_([1]), B_([1]), E[0], E[1], E[2], dirs, 20.0)]
    far = [int(x) for x in S2.fanPick(D_([10]), D_([1.6]), D_([0]), D_([1]), B_([1]), E[0], E[1], E[2], dirs, 20.0)]
    both = [int(x) for x in S2.fanPick(D_([10, 2]), D_([1.6, 1.6]), D_([0, 0]), D_([1, 1]), B_([1, 1]), E[0], E[1], E[2], dirs, 20.0)]
    past = [int(x) for x in S2.fanPick(D_([21]), D_([1.6]), D_([0]), D_([1]), B_([1]), E[0], E[1], E[2], dirs, 20.0)]
    side = [int(x) for x in S2.fanPick(D_([5 * math.cos(math.radians(15))]), D_([1.6]), D_([5 * math.sin(math.radians(15))]), D_([1]), B_([1]), E[0], E[1], E[2], dirs, 20.0)]
    hidden = [int(x) for x in S2.fanPick(D_([2]), D_([1.6]), D_([0]), D_([1]), B_([0]), E[0], E[1], E[2], dirs, 20.0)]
    K.eq((close, far, both, past, side, hidden), ([0] * 5, [-1, -1, 0, -1, -1], [1] * 5, [-1] * 5, [-1, -1, -1, 0, 0], [-1] * 5),
         "X fanPick: a close enemy takes all 5, a far one only the middle kunai, the NEAREST on a line wins, past the range / not ok = none, "
         "one 15 degrees off takes the outer two")
    K.eq([list(S2.tally(JArray(JInt)(close), 1)), list(S2.tally(JArray(JInt)(far), 1)), list(S2.tally(JArray(JInt)([-1, 3, 0]), 2))], [[5], [1], [1, 0]],
         "X tally: kunai per enemy (5 -> the 3+ bonus, 1 -> none; out-of-range picks ignored)")
    # ---- the job: due / stepped through every pulse, the timeout
    u = UUID.randomUUID()
    j = Job(0, u, "Weapon_Bo_Iron", 10.0, 0.6, int(S2.pulses(0)), int(S2.gapMs(0, False)), D_([1, 0, 0]), False, JLong(1000))
    seq = []
    t = 1000
    for _k in range(12):
        dv = int(S2.due(j, JLong(t)))
        seq.append((t, dv))
        if dv == 1:
            S2.stepped(j, JLong(t))
        elif dv < 0:
            break
        t += 250
    K.eq([x for x in seq if x[1] == 1], [(1000, 1), (1500, 1), (2000, 1), (2500, 1)], "X a Whirling Staff job pulses at 0 / 0.5 / 1.0 / 1.5 s")
    K.eq(seq[-1][1], -1, "X ... then it ends (nothing left)")
    K.eq((int(j.done), int(j.left)), (4, 0), "X done 4, left 0")
    j2 = Job(1, u, "Weapon_Fist_Gauntlets_Iron", 10.0, 0.625, 6, 150, D_([1, 0, 0]), True, JLong(1000))
    K.eq([int(S2.due(j2, JLong(1000))), int(S2.due(j2, JLong(1000 + 11000))), int(S2.due(j2, JLong(1000 + 20000))), int(S2.due(j2, JLong(1000 + 20001))),
          int(S2.due(None, JLong(5)))], [1, 1, 1, -1, -1], "X FIX A2 due: 20 s after the cast it times out (11 s still runs); no job = ended")
    # FIX A2: every family's whole job at the rows' maxima ends before the timeout (12 jabs x 0.5 s x 2 = 11 s was cut at 10 s)
    Cfg.SG2_BO_HITS, Cfg.SG2_BO_SEC, Cfg.SG2_FI_JABS, Cfg.SG2_FI_GAP, Cfg.SG2_FI_HEAVY, Cfg.SG2_BK_TICKS, Cfg.SG2_BK_SEC = 10, 5.0, 12, 0.5, 100, 10, 6.0
    spans = [int(S2.gapMs(0, False)) * (int(S2.pulses(0)) - 1), int(S2.gapMs(1, True)) * (int(S2.pulses(1)) - 1), int(S2.gapMs(3, False)) * (int(S2.pulses(3)) - 1)]
    jm = Job(1, u, "Weapon_Fist_Gauntlets_Iron", 10.0, 1.0, int(S2.pulses(1)), int(S2.gapMs(1, True)), D_([1, 0, 0]), True, JLong(1000))
    tm = 1000
    nst = 0
    while nst < 40:
        dv = int(S2.due(jm, JLong(tm)))
        if dv < 0:
            break
        if dv == 1:
            S2.stepped(jm, JLong(tm))
            nst += 1
        tm += 50
    K.check(max(spans) < int(S2.MAX_MS) and nst == 12 and int(jm.left) == 0,
            "X FIX A2 at the maxima every job fits the timeout (spans ms %s < %d) and the gauntlet job fires all 12 jabs (%d)" % (spans, int(S2.MAX_MS), nst))
    Cfg.useDefaults()
    # FIX A1: at most 64 targets, the nearest (Rush's MAX_MOBS rule)
    K.eq(int(S2.MAX_TGT), 64, "X FIX A1 MAX_TGT = 64")
    dd = [float(150 - i) for i in range(150)]
    okk = B_([1] * 150)
    kept = int(S2.keepNearest(D_(dd), okk, 64))
    K.check(kept == 64 and sum(1 for x in okk if x) == 64 and all(bool(okk[i]) == (dd[i] <= 64.0) for i in range(150)),
            "X FIX A1 keepNearest: 150 enemies -> the 64 nearest stay ok")
    ok2 = B_([1, 0, 1, 1])
    K.eq((int(S2.keepNearest(D_([5, 1, 3, 3]), ok2, 2)), [bool(x) for x in ok2]), (2, [False, False, True, True]),
         "X FIX A1 keepNearest: not-ok never counts; the 2 nearest ok stay")
    ok3 = B_([1, 1, 1])
    K.eq((int(S2.keepNearest(D_([2, 2, 2]), ok3, 2)), [bool(x) for x in ok3]), (2, [True, True, False]), "X FIX A1 keepNearest: ties keep the first, never more than max")
    ok4 = B_([1, 1])
    K.eq((int(S2.keepNearest(D_([9, 1]), ok4, 64)), int(S2.keepNearest(None, ok4, 1))), (2, 0), "X FIX A1 keepNearest: under the cap = all kept; no array = 0")
    # FIX A5: the 4 signature roots are in the pack-ownership check
    rc = [str(x) for x in Defs.ROOT_CHECK]
    K.check(all(r in rc for r in ROOTS), "X FIX A5 ArmoryDefs.ROOT_CHECK lists the 4 signature roots (%d roots checked)" % len(rc))
    # ---- the codes
    K.eq([int(Defs.pidCode(JString(str(m)))) for m in Defs.SG2_MARK], [13001, 13002, 13003, 13004], "X the 4 markers -> codes 13001-13004")
    K.eq((int(Defs.pidCode(JString("SkyyArmory_Wand_Ricochet"))), int(Defs.RICO_CODE), int(S2.CODE0), int(Defs.SG2_CODE0)), (13000, 13000, 13001, 13001),
         "X the Ricochet keeps 13000")
    # ---- the bridge
    f = Fn()

    def ask(i):
        a = JArray(JObject)(1)
        a[0] = JString(i)
        r = f.apply(a)
        return None if r is None else (str(r[0]), str(r[1]), int(r[2]), str(r[3]), bool(r[4]), [str(r[k].getClass().getName()) if not isinstance(r[k], str) else "java.lang.String" for k in range(5)])
    T5 = ["java.lang.String", "java.lang.String", "java.lang.Integer", "java.lang.String", "java.lang.Boolean"]
    want_ans = {0: ("Whirling Staff", "Spin your staff: 4 hits on every enemy within 3 blocks.", 20, "hit +2~", True, T5),
                1: ("Flurry", "6 fast jabs at the nearest enemy in front; the last knocks it back.", 20, "jab +1~", True, T5),
                2: ("Kunai Fan", "Throw 5 kunai in a fan; an enemy hit by 3+ takes a bonus hit.", 20, "kunai hit +2~", True, T5),
                3: ("Page Storm", "A storm of pages: 4 hits on every enemy within 5 blocks.", 20, "each enemy a Page Burst hits +2", True, T5)}
    wrong = []
    for fm, ids in enumerate(FAM_IDS):
        for i in ids:
            a = ask(i)
            w = want_ans[fm]
            if fm == 1 and i.startswith("Weapon_Fist_Gauntlets_"):
                w = ("Flurry", "6 heavy jabs (+25%) at the nearest enemy; the last knocks it back.", 20, "jab +1~", True, T5)
            if a != w:
                wrong.append((i, a))
    K.eq(wrong, [], "X armory:fn:sig: all 69 ids answer their family (gauntlets: the heavy line) with plain java.lang types")
    K.eq(ask("Weapon_Wand_Iron")[0:4], ("Ricochet", "A bolt jumps from your target to the nearest enemy, up to 8 hits.", 20, "quick hit +1~, charged hit +2"),
         "X the wand still answers Ricochet (unchanged)")
    K.eq([ask(i) for i in ("Weapon_Sword_Iron", "Weapon_Staff_Iron", "Weapon_Wand_SoulCage_Iron", "Nope")], [None] * 4, "X not ours -> null")
    Cfg.SG2_BO_HITS, Cfg.SG2_BO_R, Cfg.SG2_BO_GAIN, Cfg.SG2_FI_KNOCK, Cfg.SG2_KU_BONUS, Cfg.SG2_BK_ON = 10, 7.75, 1.5, 0.0, 0.0, False
    a0, a1, a2, a3 = ask("Weapon_Bo_Iron"), ask("Weapon_Fist_Wraps_Linen"), ask("Weapon_Kunai_Iron"), ask("Weapon_Spellbook_Iron")
    K.eq((a0[1], a0[3], a1[1], a2[1], a3[4]), ("Spin your staff: 10 hits on every enemy within 7.75 blocks.", "hit +1.5~",
                                               "6 fast jabs at the nearest enemy in front.", "Throw 5 kunai in a fan.", False),
         "X the texts follow the live rows (10 hits / 7.75 blocks / +1.5; no knockback; no bonus; book off -> ready false)")
    Cfg.SG2_FI_JABS, Cfg.SG2_FI_HEAVY = 12, 100
    Cfg.SG2_FI_KNOCK = 3.0
    longest = ask("Weapon_Fist_Gauntlets_Iron")[1]
    K.check(len(longest) <= 70, "X the longest line fits 70 characters (%d: %s)" % (len(longest), longest))
    Cfg.useDefaults()
    # ---- SkyyGear 0.3.43 reads it (its tooltip answer) when the jar is on the class path
    try:
        br.put("armory:fn:sig", f)
        GX = JClass("com.skyy.gear.GearSigX")
        g0 = GX.sigOf(JString("Weapon_Bo_Iron"))
        g1 = GX.sigOf(JString("Weapon_Kunai_Iron"))
        K.eq((str(g0[0]), str(g0[1]), int(g0[2]), str(g0[3]), str(g1[0])),
             ("Whirling Staff", "Spin your staff: 4 hits on every enemy within 3 blocks.", 20, "hit +2~", "Kunai Fan"),
             "X SkyyGear 0.3.43 GearSigX.sigOf takes the answer through armory:fn:sig")
        try:
            seg = GX.charge(20, JString("hit +2~"), 1.0, 1.0)
            K.notes.append("X SkyyGear charge line segments for the Bo: %s" % [str(x) for x in seg])
        except Exception as ex2:
            K.notes.append("X SkyyGear charge() not run in the bare JVM (%s)" % str(ex2)[:120])
        br.remove("armory:fn:sig")
    except Exception as ex:
        K.notes.append("X SkyyGear GearSigX not run (%s) - SkyyGear's own harness renders the block" % str(ex)[:200])
    # ---- the glue with no engine: quiet, never throws
    try:
        S2.onHit(None, None, None)
        S2.bookGain(None, None, None, 3)
        S2.bookGain(None, None, u, 0)
        S2.marker(None, None, 13001, None, None)
        why_m = str(S2.LAST_WHY)
        S2.marker(None, None, 12999, None, None)
        why_c = str(S2.LAST_WHY)
        K.eq((why_m, why_c), ("no caster", "not a signature marker"), "X marker: no projectile record = no caster; a wrong code = refused (quiet)")
        K.check(not bool(S2.step(None, None, None, JLong(5))), "X step(null) = ended")
        S2.run(None, None, None, JLong(5))
        st = JClass("java.lang.Object")()
        tw = TW.get(st)
        K.check(bool(tw.idle()), "X a fresh TravWorld is idle")
        jw = Job(0, u, "Weapon_Bo_Iron", 10.0, 0.6, 4, 500, D_([1, 0, 0]), False, JLong(100000))
        tw.sig2.add(jw)
        K.check(not bool(tw.idle()), "X TravWorld.idle() sees a waiting signature job (TravTick keeps the world)")
        S2.run(tw, None, None, JLong(99000))
        K.eq(int(tw.sig2.size()), 1, "X run: a job not yet due is kept")
        S2.run(tw, None, None, JLong(100000))
        K.eq((int(tw.sig2.size()), str(S2.LAST_WHY)), (0, "the caster left this world"), "X run -> step: a due job whose caster is gone is dropped")
        tw.sig2.add(Job(2, u, "Weapon_Kunai_Iron", 10.0, 0.8, 0, 0, D_([1, 0, 0]), False, JLong(100000)))
        S2.run(tw, None, None, JLong(100000))
        K.eq(int(tw.sig2.size()), 0, "X run: a job with nothing left is dropped")
        K.check(bool(tw.idle()), "X ... and the world is idle again")
        TW.ALL.remove(st)
    except Exception as ex:
        K.check(False, "X the glue edges threw: %s" % str(ex)[:300])
    K.notes.append("X status line: %s" % str(S2.statusText()))
    K.save()


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
    K.check(b"sig.bo." not in b0 and b"sig.refundMiss" not in b0, "D the live file has none of the new keys (they read their defaults)")
    hashes = [tree_hash(home)]
    for start in (1, 2):
        rs = [str(getattr(Cfg, m)()) for m in MIGS]
        Cfg.load()
        hashes.append(tree_hash(home))
        if start == 1:
            K.notes.append("D start 1 migrations: %s" % [x[:120] for x in rs if x])
    K.check(hashes[1] == hashes[2], "D start 2 changes nothing")
    t1 = open(fp, "rb").read()
    K.check(b"sig.bo." not in t1 and b"0.1.45" not in t1 and (b"\r\n" in b0) == (b"\r\n" in t1), "D 0.1.45 writes no row of its own; line endings kept")
    K.eq((bool(Cfg.SG2_BO_ON), int(Cfg.SG2_BO_HITS), float(Cfg.SG2_KU_GAIN), bool(Cfg.SG2_REFUND)), (True, 4, 2.0, True), "D the new keys read their defaults")
    K.notes.append("D files changed by start 1: %s" % sorted(k for k in set(hashes[0]) | set(hashes[1]) if hashes[0].get(k) != hashes[1].get(k))[:8])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ArmorySig2", "Sig2Job"],
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
