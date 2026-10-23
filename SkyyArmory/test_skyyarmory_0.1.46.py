"""Harness for SkyyArmory 0.1.46 (sig4: the base signatures Arcane Overload / Soul Release / Skewer Charge / Cleave / Skull Crack / Meridian Cut /
Iron Curtain; tools/armory_0_1_46_patch.py). Build first:
    python tools/armory_0_1_46_patch.py && python SkyyArmory/build_skyyarmory_0.1.46.py
    python SkyyArmory/test_skyyarmory_0.1.46.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S   static   the patch re-runs to identical bytes; two new classes (ArmorySig4, Sig4Job), no command / system; the jar vs 0.1.45 entry by
               entry: added = the 2 classes + the 28 signature files + the vanilla family item overrides (each = the Assets.zip file +
               Ability1 + the wand meter + the ready look ONLY), changed non-class = manifest + exactly our family items (each = the 0.1.45 JSON
               + the same 3 fields ONLY); roots / casts / launches = the wand's shape; markers = the Ricochet marker byte for byte; the wand's
               + sig2's signature files byte-identical; no lang change; the 43 rows
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.45 -> 0.1.46: exactly the planned members (EXPECT) + the 2 new classes; ArmorySig2 / Rico / RicoChain identical
  X   exec     EXECUTED in the JVM: the 43 defaults (useDefaults -> applySig4) + clamps; famOf / baseOf for every item of the jar's 7 roots +
               controls; the charge rules (gainFam / gainAmt / staffAmt / soulAmt) and the meter from 0 to full per family; pulses / gaps /
               timeouts (every job at the rows' maxima fits MAX_MS); the geometry (flat, inCone, front, carryV, stallStep, wallTouch,
               wallSide); soulHit / healOf; the Mana-back cost (tierOfW / costOf vs ArmorySpeedFn.T_COST); Arcane Overload EXECUTED end to end
               without the engine (marker gate -> OVER job -> staffShot marks 3 shots via the Leap.HAND seam, a 4th is normal -> boost x2 on
               the shot's TravShot record + the job's hit count -> the watch ends after the grace); a Soul Release record read back (Soul.LASTB
               window); the codes 13005-13011 (sig2 13001-13004 + Ricochet 13000 kept); ROOT_CHECK; armory:fn:sig for every family + live
               rows + maxima <= 70 characters; sig2 / wand answers unchanged; SkyyGear 0.3.43 GearSigX.sigOf through the bridge (its jar
               present); the glue edges with no engine (quiet, never throw; run drops a job whose caster is gone; idle sees the jobs)
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration + load): 0.1.46 writes no row, the new keys read
               their defaults
  AA  audit    the engine-access audit
FIX ROUND (critics; a check per fix): S the 13 vanilla ids another installed mod ships (Skyys-HyMax Mithril / Onyxium, More To Explore) are
  NOT in the jar and answer null; X the dash ends on time at 20 / 30 TPS (dashOn), the quit hook drops OVER + Soul.LASTB (quit), clear() empties
  OVER; the tooltip lines carry the multiplier; C ArmoryQuit.accept + SkyyArmoryPlugin.shutdown changed (the new calls).
Not executed here (UNVERIFIED until the game): the server-side hits / dash / shove / stun / heal on real mobs, the meter rising on a real swing /
shot / Binding, the vanilla file overrides loading over Assets.zip, the cast poses + sounds, the client pressing Ability 1 on these items.
"""
import os, sys, json, hashlib, subprocess, zipfile, glob, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sig4", "arm")]
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.46", "0.1.45"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyarmory_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyarmory_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "armory_0_1_46_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
GEAR_JAR = os.path.join(ROOT, "SkyyGear", "SkyyGear-0.3.43.jar")
AZ_PATH = os.path.join(os.path.dirname(os.path.dirname(B.INSTALLED_SERVER_JAR)), "Assets.zip")          # read only (a zip, never a JVM)
KEYS4 = ["ST_ON", "ST_SHOTS", "ST_DMG", "ST_SEC", "ST_GAINQ", "ST_GAINC", "SO_ON", "SO_DMG", "SO_CAP", "SO_WIN", "SO_HEAL", "SO_HR", "SO_GAIN",
         "SP_ON", "SP_DIST", "SP_SEC", "SP_DMG", "SP_PIN", "SP_GAIN", "AX_ON", "AX_DMG", "AX_HITS", "AX_ARC", "AX_R", "AX_GAP", "AX_GAIN",
         "CL_ON", "CL_DMG", "CL_STUN", "CL_R", "CL_GAIN", "LS_ON", "LS_DMG", "LS_ARC", "LS_R", "LS_GAIN", "GS_ON", "GS_SEC", "GS_W", "GS_DIST",
         "GS_PUSH", "GS_DMG", "GS_GAIN"]
EXPECT = {"ArmoryCfg": ["+f SG4_" + k for k in KEYS4] + ["+m applySig4", "~<clinit>", "~m apply", "~m load", "~m reloadAll", "~m useDefaults"],
          "ArmoryDefs": ["+f SG4_CODE0", "+f SG4_MARK", "~<clinit>", "~m pids"],          # the 7 marker codes + ROOT_CHECK
          "ArmoryCheck": ["~m packCheck", "~m packOf"],          # the version text
          "ArmoryHitSys": ["~m handle"],          # ArmorySig4.onHit + staffGain
          "ArmoryTuneSys": ["~m handle"],          # ArmorySig4.filter (the Arcane Overload x2)
          "ArmorySigFn": ["~m sigOf"],          # ArmorySig2 first, then ArmorySig4.answer
          "ArmoryTrav": ["~m added"],          # the marker dispatch + staffShot
          "TravShot": ["+f sig4", "~m next"],          # the overload mark (kept by a pierce continuation)
          "TravWorld": ["+f sig4", "~c ", "~m idle", "~m run"],          # the jobs list + ArmorySig4.run
          "Soul": ["+f LASTB", "+f SIG_GAINS", "~<clinit>", "~m release", "~m step", "~m clear"],          # the released Bindings + the Binding charge
          "SkyyArmoryPlugin": ["~m setup", "~m start", "~m shutdown"],          # the version text + the status line; fix: ArmorySig4.clear()
          "ArmoryQuit": ["~m accept"],          # fix: ArmorySig4.quit (the quitter's Overload watch + released Bindings)
          "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"],
          "CfgRows2": ["~<clinit>"]}          # the kit: the 43 new rows + the default file + the relabelled tab + the sig.refundMiss text
if "--expect-dump" in sys.argv:
    EXPECT = {}
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040",
        "migrateP5")
ROOTS = ["SkyyArmory_Sig_ArcaneOverload", "SkyyArmory_Sig_SoulRelease", "SkyyArmory_Sig_SkewerCharge", "SkyyArmory_Sig_Cleave",
         "SkyyArmory_Sig_SkullCrack", "SkyyArmory_Sig_MeridianCut", "SkyyArmory_Sig_IronCurtain"]
NAMES = ["Arcane Overload", "Soul Release", "Skewer Charge", "Cleave", "Skull Crack", "Meridian Cut", "Iron Curtain"]
SIG2_ROOTS = ["SkyyArmory_Sig_Whirl", "SkyyArmory_Sig_Flurry", "SkyyArmory_Sig_KunaiFan", "SkyyArmory_Sig_PageStorm"]
WAND_SIG_FILES = ["Server/Item/RootInteractions/Weapons/Wand/SkyyArmory/SkyyArmory_Wand_Signature.json",
                  "Server/Item/Interactions/Weapons/Wand/SkyyArmory/SkyyArmory_Wand_Signature_Cast.json",
                  "Server/Item/Interactions/Weapons/Wand/SkyyArmory/SkyyArmory_Wand_Signature_Launch.json",
                  "Server/Projectiles/Player/SkyyArmory/SkyyArmory_Wand_Ricochet.json"]
NK = ["Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"]


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def jar_items(z):
    out = {}
    for n in z.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            out[n] = json.loads(z.read(n).decode("utf-8"))
    return out


def fam_items(jar):
    """item id -> family index (its Ability1 is one of the 7 roots), read from the built jar"""
    z = zipfile.ZipFile(jar)
    out = {}
    for n, j in jar_items(z).items():
        a1 = (j.get("Interactions") or {}).get("Ability1")
        if a1 in ROOTS:
            out[os.path.basename(n)[:-5]] = (ROOTS.index(a1), n)
    return out


def planned_entries():
    """(added non-class entries, changed non-class entries) the round plans, from the two jars"""
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    na, nb = set(za.namelist()), set(zb.namelist())
    fi = fam_items(JAR)
    add = sorted(n for n in nb - na if not n.endswith(".class"))
    chg = sorted(["manifest.json"] + [n for i, (f, n) in fi.items() if n in na])
    return add, chg, fi


# ---------------------------------------------------------------------------------------------------------------- C: compare (+ the planned assets)
_ORIG_COMPARE = HK.run_compare


def compare_with_assets(out, jar, old_jar, pkg, expect, added, removed=()):
    _ORIG_COMPARE(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    ed = sorted(n for n in ea | eb if n not in ea or n not in eb or za.read(n) != zb.read(n))
    add, chg, _fi = planned_entries()
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
    K.check(g.startswith('"""SkyyArmory 0.1.46 - build script') and g.count('VERSION = "0.1.46"') == 1, "S header + VERSION")
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
    add, chg, fi = planned_entries()
    sigf = [n for n in add if "/SkyyArmory/SkyyArmory_Sig_" in n]
    van = sorted(n for n in add if n.startswith("Server/Item/Items/"))
    K.eq(sorted(nb - na), sorted(add + ["com/skyy/armory/ArmorySig4.class", "com/skyy/armory/Sig4Job.class"]), "S added = the 2 classes + the planned files")
    K.eq(sorted(na - nb), [], "S nothing removed")
    K.eq((len(sigf), sorted(set(add) - set(sigf) - set(van))), (28, []), "S 28 new signature files; the other added files are the vanilla overrides")
    nc = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(nc, chg, "S changed non-class = manifest + exactly our family items")
    cnt = [sum(1 for i, (f, n) in fi.items() if f == k) for k in range(7)]
    K.eq(cnt, [17, 16, 23, 19, 25, 23, 15], "S items per family (staff 16 + Loophole, soul 16, spear 8 + 15 vanilla, axe 8 + 11, club 8 + 17, "
         "longsword 8 + 15, great shield 15)")
    K.eq((len(van), len(chg) - 1), (58, 80), "S 58 vanilla item files overridden, 80 of our items changed")
    ext = ["Server/Item/Items/Weapon/%s/Weapon_%s_%s.json" % (a_, a_, b_) for a_ in ("Spear", "Axe", "Club", "Longsword") for b_ in ("Mithril", "Onyxium")] + \
          ["Server/Item/Items/Weapon/Club/Weapon_Club_%s.json" % x_ for x_ in ("Zombie_Arm", "Zombie_Burnt_Arm", "Zombie_Burnt_Leg", "Zombie_Leg")] + \
          ["Server/Item/Items/Weapon/Longsword/Weapon_Longsword_Spectral.json"]
    K.check(len(ext) == 13 and not [n for n in ext if n in nb], "S FIX: the 13 vanilla files Skyys-HyMax / More To Explore ship are NOT in the jar (theirs stay whole)")
    hm = os.path.join(B.MODS_DIR, "Skyys-HyMax.zip")
    if os.path.isfile(hm):
        hz = set(zipfile.ZipFile(hm).namelist())
        K.check(not (hz & (nb - na)), "S FIX: no file 0.1.46 ADDS is a path the installed Skyys-HyMax ships (%s)" % sorted(hz & (nb - na))[:4])
        K.notes.append("S older clash (0.1.45 already, not this round): Skyys-HyMax + SkyyArmory both ship %s" % sorted(n for n in hz & na if n.startswith("Server/")))
    J = lambda z, n: json.loads(z.read(n).decode("utf-8"))
    w_old = J(za, "Server/Item/Items/Weapon/Wand/Weapon_Wand_Iron.json")
    meter, look = w_old["Weapon"], w_old["ItemAppearanceConditions"]
    import zipfile as _zf
    AZ = _zf.ZipFile(os.path.abspath(AZ_PATH))
    azn = set(AZ.namelist())
    bad, nolook = [], []
    for i, (f, n) in sorted(fi.items()):
        b = J(zb, n)
        if n in na:
            a = J(za, n)
        elif n in azn:
            a = json.loads(AZ.read(n).decode("utf-8-sig"))
        else:
            bad.append((i, "no source"))
            continue
        exp = json.loads(json.dumps(a))
        exp["Interactions"]["Ability1"] = ROOTS[f]
        w = dict(a.get("Weapon") or {})
        w.update(meter)
        exp["Weapon"] = w
        if "ItemAppearanceConditions" in b:
            iac = dict(a.get("ItemAppearanceConditions") or {})
            iac.update(look)
            exp["ItemAppearanceConditions"] = iac
        else:
            nolook.append(i)
        if b != exp or "Ability1" in (a.get("Interactions") or {}):
            bad.append((i, sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))))
    K.eq(bad, [], "S every family item = its source (0.1.45 / Assets.zip) + Ability1 (its family root) + the wand meter + the ready look ONLY")
    K.check(sorted(nolook) == sorted(i for i, (f, n) in fi.items() if f == 1), "S only the 16 soul items have no ready glow (no Handle node): %s" % nolook[:4])
    K.check(all(n in azn for n in van), "S every added item file is a vanilla path (same path as Assets.zip)")
    K.check(not [n for n in van if n.endswith("_NPC.json")], "S no _NPC copy shipped (they inherit their parent)")
    wc = J(zb, WAND_SIG_FILES[1])
    wl = J(zb, WAND_SIG_FILES[2])
    wm = zb.read(WAND_SIG_FILES[3])
    shp = []
    for f, r in enumerate(ROOTS):
        rp = "Server/Item/RootInteractions/Weapons/Signature/SkyyArmory/%s.json" % r
        cpth = "Server/Item/Interactions/Weapons/Signature/SkyyArmory/%s_Cast.json" % r
        lp = "Server/Item/Interactions/Weapons/Signature/SkyyArmory/%s_Launch.json" % r
        mp = "Server/Projectiles/Player/SkyyArmory/%s_Mark.json" % r
        if sorted([rp, cpth, lp, mp]) != sorted(x for x in sigf if os.path.basename(x).startswith(r + ".") or os.path.basename(x).startswith(r + "_")):
            shp.append((r, "files"))
            continue
        ro, co, lo = J(zb, rp), J(zb, cpth), J(zb, lp)
        tag = {"Attack": ["Ranged"]} if f < 2 else {"Attack": ["Melee"]}
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
    K.notes.append("S launch poses + sounds: %s" % [(r[len("SkyyArmory_Sig_"):], J(zb, "Server/Item/Interactions/Weapons/Signature/SkyyArmory/%s_Launch.json" % r)["Effects"]) for r in ROOTS])
    s2f = [n for n in na if any(("/%s" % r) in n for r in SIG2_ROOTS)]
    K.check(len(s2f) == 16 and all(za.read(x) == zb.read(x) for x in s2f + WAND_SIG_FILES), "S the wand's 4 + sig2's 16 signature files byte-identical")
    s2items = [n for n, j in jar_items(za).items() if (j.get("Interactions") or {}).get("Ability1") in SIG2_ROOTS + ["SkyyArmory_Wand_Signature"]]
    K.check(len(s2items) >= 69 + 15 and all(za.read(x) == zb.read(x) for x in s2items), "S every sig2 / wand signature item byte-identical (%d)" % len(s2items))
    K.check(not [n for n in nc + add if "/Languages/" in n or n.endswith(".lang")], "S no lang file changed")
    for i in ("Weapon_Axe_Iron", "Weapon_Staff_Iron", "Weapon_Wand_SoulCage_Iron", "Weapon_GreatShield_Iron"):
        K.notes.append("S %s now: Interactions %s, Weapon %s, looks %s" % (i, J(zb, fi[i][1])["Interactions"], J(zb, fi[i][1])["Weapon"],
                                                                         sorted(J(zb, fi[i][1]).get("ItemAppearanceConditions", {}))))
    rows = [x for x in g.split("\n") if x.startswith("    ('sig.") and any(x.startswith("    ('sig.%s." % k) for k in ("staff", "soul", "spear", "axe", "club", "longsword", "gs"))]
    K.eq(len(rows), 43, "S 43 new rows in the script")
    K.check('("hop", "Signatures + wand")' in g and "every family but the wand" in g, "S the tab relabelled + sig.refundMiss covers every family")
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
    Cfg, Defs, S4, Job, Fn = (JClass(PKG + n) for n in ("ArmoryCfg", "ArmoryDefs", "ArmorySig4", "Sig4Job", "ArmorySigFn"))
    S2, Soul, TW, Shot, Spd, Leap = (JClass(PKG + n) for n in ("ArmorySig2", "Soul", "TravWorld", "TravShot", "ArmorySpeedFn", "Leap"))
    UUID = JClass("java.util.UUID")
    HMap = JClass("java.util.HashMap")
    D_ = lambda a: JArray(JDouble)([float(x) for x in a])
    B_ = lambda a: JArray(JBoolean)([bool(x) for x in a])
    Cfg.useDefaults()
    # ---- the rows: defaults + clamps (applySig4 through apply)
    dflt = dict(ST_ON=True, ST_SHOTS=3, ST_DMG=2.0, ST_SEC=10.0, ST_GAINQ=1.0, ST_GAINC=2.0, SO_ON=True, SO_DMG=1.0, SO_CAP=6.0, SO_WIN=5.0, SO_HEAL=25,
                SO_HR=4.0, SO_GAIN=2.0, SP_ON=True, SP_DIST=6.0, SP_SEC=0.4, SP_DMG=1.25, SP_PIN=1.0, SP_GAIN=1.5, AX_ON=True, AX_DMG=0.8, AX_HITS=3,
                AX_ARC=180, AX_R=4.0, AX_GAP=0.25, AX_GAIN=1.5, CL_ON=True, CL_DMG=2.5, CL_STUN=1.0, CL_R=4.0, CL_GAIN=1.5, LS_ON=True, LS_DMG=1.25,
                LS_ARC=160, LS_R=5.0, LS_GAIN=1.5, GS_ON=True, GS_SEC=4.0, GS_W=3.0, GS_DIST=2.5, GS_PUSH=2.0, GS_DMG=1.0, GS_GAIN=2.0)
    K.eq(sorted(dflt), sorted(KEYS4), "X the harness knows all 43 fields")
    got = dict((k, (bool(getattr(Cfg, "SG4_" + k)) if isinstance(v, bool) else (int(getattr(Cfg, "SG4_" + k)) if isinstance(v, int) else
                                                                                 round(float(getattr(Cfg, "SG4_" + k)), 6)))) for k, v in dflt.items())
    K.eq(got, dflt, "X useDefaults -> applySig4: the 43 defaults")
    Pr = JClass("java.util.Properties")
    pp = Pr()
    for k_, v_ in (("sig.axe.hits", "99"), ("sig.spear.seconds", "0.01"), ("sig.gs.width", "abc"), ("sig.soul.heal", "-5"), ("sig.club.enabled", "off"),
                   ("sig.staff.damage", "0.5"), ("sig.longsword.arc", "720")):
        pp.setProperty(k_, v_)
    Cfg.applySig4(pp)
    K.eq((int(Cfg.SG4_AX_HITS), float(Cfg.SG4_SP_SEC), float(Cfg.SG4_GS_W), int(Cfg.SG4_SO_HEAL), bool(Cfg.SG4_CL_ON), float(Cfg.SG4_ST_DMG), int(Cfg.SG4_LS_ARC),
          float(Cfg.SG4_SO_DMG)), (6, 0.15, 3.0, 0, False, 1.0, 360, 1.0), "X applySig4 clamps like the kit (max / min / bad text = default; a missing key = its default)")
    Cfg.useDefaults()
    # ---- families + hit numbers (the jar's items with the 7 roots)
    fi = fam_items(jar)
    ids = [str(x) for x in S4.ID]
    K.eq(sorted(ids), sorted(fi), "X ArmorySig4.ID = exactly the items carrying the 7 roots (%d)" % len(ids))
    wrong = [(i, int(S4.famOf(JString(i))), f) for i, (f, n) in fi.items() if int(S4.famOf(JString(i))) != f]
    K.eq(wrong, [], "X famOf: every item -> its family")
    ctl = ["Weapon_Bo_Iron", "Weapon_Wand_Iron", "Weapon_Sword_Iron", "Weapon_Staff_Bone", "Weapon_Staff_Crystal_Flame", "Weapon_Longsword_Praetorian_NPC",
           "Hepta_Axe", "Weapon_Shield_Iron", "Weapon_Axe_Lead", "Weapon_Axe_Mithril", "Weapon_Longsword_Spectral", "Weapon_Club_Zombie_Arm", "", None]
    K.eq([int(S4.famOf(None if i is None else JString(i))) for i in ctl], [-1] * len(ctl),
         "X famOf: Bo / wand / sword / SkyySkills + Crystal staffs / NPC copies / pack / shields / FIX: the HyMax + More To Explore ids / none -> -1")
    want_h = {"Weapon_Axe_Iron": 17.0, "Weapon_Club_Iron": 17.0, "Weapon_Longsword_Iron": 16.0, "Weapon_Spear_Iron": 15.0, "Weapon_Club_Zombie_Frost_Arm": 7.0,
              "Weapon_Longsword_Flame": 31.0, "Weapon_Staff_Iron": 1.0, "Weapon_Wand_SoulOrb": 1.0, "Weapon_Staff_UT_Loophole": 1.0}
    K.eq(dict((i, float(S4.baseOf(JString(i)))) for i in want_h), want_h, "X baseOf: the axe / club / longsword swing, the spear throw (Assets.zip numbers); staff / soul 1")
    gsi = [str(x) for x in Defs.GS_IDS]
    K.eq([float(S4.baseOf(JString(i))) for i in gsi], [float(x) for x in Defs.GS_H], "X baseOf: every great shield = ArmoryDefs.GS_H (the same-metal longsword swing)")
    K.check(all(float(S4.baseOf(JString(i))) > 0.0 for i in ids), "X every item has a hit number > 0")
    K.notes.append("X zone-metal hit numbers: %s" % [(i, float(S4.baseOf(JString(i)))) for i in ids if i.endswith("Lead_SkyWynn")])
    # ---- the charge rules
    hands = ["Weapon_Spear_Iron", "Weapon_Axe_Lead_SkyWynn", "Weapon_Club_Iron", "Weapon_Longsword_Iron", "Weapon_GreatShield_Iron", "Weapon_Staff_Iron",
             "Weapon_Wand_SoulCage_Iron", "Weapon_Bo_Iron"]
    mat = [[int(S4.gainFam(JString(h), s)) for s in range(4)] for h in hands]
    K.eq(mat, [[2, -1, -1, -1], [3, -1, -1, -1], [4, -1, -1, -1], [5, -1, -1, -1], [6, -1, -1, -1], [-1] * 4, [-1] * 4, [-1] * 4],
         "X gainFam: a melee swing WITH the DamageSequence only; staffs / souls never here; a Bo (sig2) never here")
    Cfg.SG4_AX_ON = False
    K.eq(int(S4.gainFam(JString("Weapon_Axe_Iron"), 0)), -1, "X sig.axe.enabled off -> no charge")
    Cfg.SG4_AX_ON = True
    K.eq([round(float(S4.gainAmt(f, w)), 4) for f, w in ((2, 1.0), (3, 0.7), (6, 1.4), (5, 9.0), (4, -1.0), (0, 1.0), (1, 1.0))],
         [1.5, 1.05, 2.8, 1.5, 1.5, 0.0, 0.0], "X gainAmt: x the speed weight (out of 0..4 = 1); staff / soul 0")
    K.eq([round(float(S4.staffAmt(c, w)), 4) for c, w in ((3001, 1.0), (3001, 0.5), (4002, 0.5), (2001, 1.0), (5000, 1.0))], [1.0, 0.5, 2.0, 0.0, 0.0],
         "X staffAmt: quick +1 x w, charged +2, a wand / other code nothing")
    K.eq([float(S4.soulAmt(s)) for s in (0.5, 1.0, 0.0, -1.0)], [1.0, 2.0, 0.0, 0.0], "X soulAmt: +2 a second of Binding damage")
    Cfg.SG4_ST_ON = False
    K.eq((float(S4.staffAmt(3001, 1.0)),), (0.0,), "X sig.staff.enabled off -> no staff charge")
    Cfg.useDefaults()

    def to_full(amt):
        cur, n = 0.0, 0
        while n < 1000:
            v = float(S2.fill(cur, 20.0, amt))
            if v < 0:
                break
            cur, n = v, n + 1
        return n
    full = [to_full(float(S4.gainAmt(f, 1.0))) for f in (2, 3, 4, 5, 6)] + [to_full(float(S4.staffAmt(3000, 1.0))), to_full(float(S4.staffAmt(4000, 1.0))),
                                                                            to_full(float(S4.soulAmt(1.0)))]
    K.eq(full, [14, 14, 14, 14, 10, 20, 10, 10], "X the meter (20) fills from 0: spear / axe / club / longsword 14 hits, great shield 10, staff 20 quick / "
         "10 charged hits, soul 10 seconds of Binding damage (sig2's 10-20 range)")
    # ---- pulses / gaps / numbers
    K.eq([int(S4.pulses(f)) for f in range(7)], [1, 1, 13, 3, 1, 2, 16], "X pulses: watch 1, pop 1, dash 13 ticks (0.4 s), 3 chops, 1 blow, 2 cuts, wall 16 (4 s)")
    K.eq([int(S4.gapMs(f)) for f in range(7)], [250, 0, 33, 250, 0, 150, 250], "X gapMs")
    K.eq([round(float(S4.dmgX(f)), 4) for f in range(7)], [2.0, 1.0, 1.25, 0.8, 2.5, 1.25, 1.0], "X dmgX")
    K.eq([float(S4.radius(f)) for f in range(7)], [0.0, 0.0, 2.7, 4.0, 4.0, 5.0, 3.0], "X radius / reach / the wall query")
    K.eq([float(S4.arcOf(f)) for f in (3, 5, 4)], [180.0, 160.0, 360.0], "X arcOf")
    K.eq((round(float(S4.dashV()), 6), int(S4.dashTicks()), int(S4.wallPulses())), (15.0, 13, 16), "X the dash 15 blocks a second (6 / 0.4), 13 ticks; the wall 16 pulses")
    # ---- the jobs: due / stepped through every pulse; every job at the rows' maxima fits MAX_MS
    u = UUID.randomUUID()

    def pulses_of(f, item, base=10.0):
        j = Job(f, u, item, base, float(S4.dmgX(f)), int(S4.pulses(f)), int(S4.gapMs(f)), D_([1, 0, 0]), JLong(1000))
        seq, t = [], 1000
        for _k in range(400):
            dv = int(S4.due(j, JLong(t)))
            if dv == 1:
                seq.append(t)
                S4.stepped(j, JLong(t))
            elif dv < 0:
                break
            t += 10
        return seq
    K.eq(pulses_of(3, "Weapon_Axe_Iron"), [1000, 1250, 1500], "X a Cleave job chops at 0 / 0.25 / 0.5 s")
    K.eq(pulses_of(5, "Weapon_Longsword_Iron"), [1000, 1150], "X a Meridian Cut job cuts at 0 / 0.15 s")
    K.eq(len(pulses_of(6, "Weapon_GreatShield_Iron")), 16, "X an Iron Curtain job pulses 16 times (4 s / 0.25)")
    K.eq(len(pulses_of(2, "Weapon_Spear_Iron")), 13, "X a Skewer Charge job ticks 13 times")

    def dash_moves(tick_ms):
        """FIX: the pulses that still MOVE you (dash() keeps the speed while left > 1 and dashOn) at a server tick of tick_ms"""
        j = Job(2, u, "Weapon_Spear_Iron", 10.0, 1.25, int(S4.pulses(2)), int(S4.gapMs(2)), D_([1, 0, 0]), JLong(1000))
        mv, t, k = 0, 1000.0, 0
        while k < 400:
            now = int(t)
            dv = int(S4.due(j, JLong(now)))
            if dv < 0:
                break
            if dv == 1:
                if int(j.left) > 1 and bool(S4.dashOn(j, JLong(now))):
                    mv += 1
                else:
                    j.left = 1
                S4.stepped(j, JLong(now))
            t += tick_ms
            k += 1
        return mv
    m30, m20 = dash_moves(1000.0 / 30.0), dash_moves(50.0)
    K.eq((bool(S4.dashOn(Job(2, u, "x", 1.0, 1.0, 13, 33, D_([1, 0, 0]), JLong(1000)), JLong(1399))),
          bool(S4.dashOn(Job(2, u, "x", 1.0, 1.0, 13, 33, D_([1, 0, 0]), JLong(1000)), JLong(1400))), bool(S4.dashOn(None, JLong(5)))), (True, False, False),
         "X FIX dashOn: the dash runs for sig.spear.seconds (0.4 s) of time")
    K.check(abs(m30 * (1000.0 / 30.0) * 0.015 - 6.0) <= 0.6 and abs(m20 * 50.0 * 0.015 - 6.0) <= 0.6,
            "X FIX the dash covers ~6 blocks at 30 TPS (%d moving ticks = %.2f) AND at 20 TPS (%d = %.2f; was 13 ticks = 9.75)" % (
                m30, m30 * (1000.0 / 30.0) * 0.015, m20, m20 * 0.75))
    K.eq((pulses_of(4, "Weapon_Club_Iron"), pulses_of(1, "Weapon_Wand_SoulOrb")), ([1000], [1000]), "X Skull Crack / Soul Release: one pulse at once")
    Cfg.SG4_AX_HITS, Cfg.SG4_AX_GAP, Cfg.SG4_GS_SEC, Cfg.SG4_SP_SEC, Cfg.SG4_ST_SEC = 6, 1.0, 10.0, 1.5, 30.0
    spans = [int(S4.gapMs(3)) * (int(S4.pulses(3)) - 1), int(S4.gapMs(6)) * (int(S4.pulses(6)) - 1), int(S4.gapMs(2)) * (int(S4.pulses(2)) - 1),
             int(round(float(Cfg.SG4_ST_SEC) * 1000)) + int(S4.GRACE_MS)]
    K.check(max(spans) < int(S4.MAX_MS), "X at the maxima every job fits the timeout (spans ms %s < %d)" % (spans, int(S4.MAX_MS)))
    Cfg.useDefaults()
    jt = Job(3, u, "Weapon_Axe_Iron", 10.0, 0.8, 3, 250, D_([1, 0, 0]), JLong(1000))
    K.eq([int(S4.due(jt, JLong(1000 + 45000))), int(S4.due(jt, JLong(1000 + 45001))), int(S4.due(None, JLong(5)))], [1, -1, -1],
         "X due: 45 s after the cast it times out; no job = ended")
    # ---- the geometry
    K.eq([[round(float(x), 6) for x in S4.flat(D_([3, 9, 4]))], S4.flat(D_([0, 1, 0])), S4.flat(None)], [[0.6, 0.0, 0.8], None, None],
         "X flat: the look on the flat; straight up / none = null")
    cone = [bool(x) for x in S4.inCone(D_([3, -3, 0, 3.9, 4.1, 3, 0.3, 2.7, 2.9]), D_([0.9] * 8 + [4.0]), D_([0, 0, 3, 0, 0, 0.1, 0, 2.6, 0]),
                                       B_([1, 1, 1, 1, 1, 0, 1, 1, 1]), 0.0, 0.9, 0.0, 1.0, 0.0, 4.0, 180.0)]
    K.eq(cone, [True, False, True, True, False, False, True, True, True],
         "X inCone 180 / 4 blocks: ahead in, behind out, beside in (the edge), 3.9 in / 4.1 out, not-ok out, very close in, 44 degrees in, 3.1 above in (reach 4)")
    narrow = [bool(x) for x in S4.inCone(D_([3, 2, 2]), D_([0.9] * 3), D_([0, 1.4, 2.0]), B_([1, 1, 1]), 0.0, 0.9, 0.0, 1.0, 0.0, 5.0, 80.0)]
    K.eq(narrow, [True, True, False], "X inCone 80 degrees: 0 in, 35 in, 45 out")
    K.eq([bool(x) for x in S4.inCone(D_([-3]), D_([0.9]), D_([0]), B_([1]), 0.0, 0.9, 0.0, 1.0, 0.0, 4.0, 360.0)], [True], "X inCone 360 = all around")
    fr = [int(S4.front(D_(xs), D_(zs), D_([1.0] * len(xs)), B_([1] * len(xs)), 0.0, 0.0, 1.0, 0.0, 2.2)) for xs, zs in
          (([1.5, 1.0], [0.0, 0.5]), ([3.5], [0.0]), ([1.0], [1.5]), ([-1.0], [0.0]), ([2.6], [0.9]))]
    K.eq(fr, [1, -1, -1, -1, 0], "X front: the nearest in your path; past the reach / to the side / behind = none; a wide body at the edge counts")
    K.eq([round(float(S4.carryV(a, 15.0)), 4) for a in (1.4, 0.4, 5.0, -3.0)], [15.0, 21.6667, 7.5, 30.0], "X carryV: keep it 1.4 ahead (half .. twice your speed)")
    K.eq([int(S4.stallStep(p_, m_, a_)) for p_, m_, a_ in ((0, 0.1, 0.5), (2, 0.1, 0.5), (2, 0.4, 0.5))], [1, 3, 0], "X stallStep: < 30 % of the asked move counts up")
    wt = [bool(S4.wallTouch(x, z, 1.0, 2.5, 0.0, 1.0, 0.0, 1.5, 0.6)) for x, z in ((2.5, 0.0), (3.7, 0.0), (3.2, 0.0), (2.5, 1.9), (2.5, 2.1), (1.4, 0.0))]
    K.eq(wt, [True, False, True, True, False, True], "X wallTouch: the middle, past its thickness out, 0.7 ahead in, the ends (1.5 + body) in / out")
    K.eq([float(S4.wallSide(x, 0.0, 2.5, 0.0, 1.0, 0.0)) for x in (3.0, 2.0)], [1.0, -1.0], "X wallSide: shoved to the side it stands on")
    # ---- Soul Release numbers
    dps0 = float(Soul.dps(2))
    K.eq([round(float(S4.soulHit(d_, 2)), 4) for d_ in (10.0, dps0 * 6 + 50, 0.0)], [10.0, round(dps0 * 6, 4), 0.0],
         "X soulHit: the stored damage, capped at 6 s of the cage's Binding damage (Iron %s a second)" % dps0)
    Cfg.SG4_SO_DMG = 2.0
    K.eq(round(float(S4.soulHit(10.0, 2)), 4), 20.0, "X soulHit x sig.soul.damage")
    Cfg.useDefaults()
    K.eq([float(S4.healOf(h_)) for h_ in (40.0, 0.0, -3.0)], [10.0, 0.0, 0.0], "X healOf: 25 % of the pop")
    # ---- the Mana back (ArmorySpeedFn.T_COST, 4 per root, the staff roots)
    rf = [int(x) for x in Spd.R_FAM]
    ws = [float(x) for x in Spd.W]
    tc = [float(x) for x in Spd.T_COST]
    si = [k for k in range(len(rf)) if rf[k] == 1]
    K.check(len(si) >= 16, "X ArmorySpeedFn has the staff roots (%d)" % len(si))
    costs = [[round(float(S4.costOf(k, ws[t])), 4) for t in range(4)] for k in si]
    K.eq(costs, [[round(tc[k * 4 + t], 4) for t in range(4)] for k in si], "X costOf = the root's quick cost at each speed tier")
    K.eq((int(S4.tierOfW(1.0)), int(S4.tierOfW(0.69)), float(S4.costOf(-1, 1.0))), (1, 2, 0.0), "X tierOfW (nearest), costOf(no root) = 0")
    K.notes.append("X staff quick Mana by tier (Slow / Medium / Fast / Super Fast): %s" % costs[:3])
    # ---- ARCANE OVERLOAD EXECUTED without the engine: the job, 3 marked shots (+ a 4th normal), the x2 boost on the shot record, the watch
    hand = HMap()
    Leap.HAND = hand
    cu = UUID.randomUUID()
    hand.put(cu, JString("Weapon_Staff_Iron"))
    S4.CLOCK = 50000
    S4.OVER.clear()
    jo = Job(0, cu, "Weapon_Staff_Iron", 1.0, 2.0, 1, 250, D_([1, 0, 0]), JLong(50000))
    jo.shots = 3
    jo.until = 50000 + 10000
    S4.OVER.put(cu, jo)
    shots = [Shot(0.0, 0.0, 0.0, 30.0, 3001, cu, JString("q")) for _k in range(4)]
    b0 = int(S4.BOOSTS)
    for s in shots:
        S4.staffShot(s, cu, None)
    K.eq(([int(s.sig4) for s in shots], int(jo.shots), int(S4.BOOSTS) - b0, int(jo.lastShot)), ([2, 2, 2, 1], 0, 3, 50000),
         "X staffShot: 3 shots overloaded (mark 2), the 4th normal (1); the job counts them down")
    cont = shots[0].next()
    S4.staffShot(cont, cu, None)
    K.eq(int(cont.sig4), 2, "X a pierce continuation keeps the overload (TravShot.next copies sig4; judged once)")
    other = Shot(0.0, 0.0, 0.0, 30.0, 3001, UUID.randomUUID(), JString("q"))
    S4.staffShot(other, other.caster, None)
    K.eq(int(other.sig4), 1, "X another player's shot is normal")
    tw = TW.get(JClass("java.lang.Object")())
    kb, kn = JClass("java.lang.Object")(), JClass("java.lang.Object")()
    tw.quick.put(kb, shots[0])
    tw.quick.put(kn, shots[3])
    bh = int(S4.BOOST_HITS)
    K.eq((float(S4.boost(tw, kb)), float(S4.boost(tw, kn)), float(S4.boost(tw, JClass("java.lang.Object")())), float(S4.boost(None, kb))), (2.0, 1.0, 1.0, 1.0),
         "X boost: an overloaded shot's hit x2 (sig.staff.damage), a normal / unknown shot x1")
    K.eq((int(S4.BOOST_HITS) - bh, int(jo.hits)), (1, 1), "X boost counts the overload's hit on its job")
    K.eq([bool(S4.watchEnd(jo, JLong(t))) for t in (50000, 52999, 53000)], [False, False, True], "X watchEnd: every shot fired -> 3 s grace after the last, then over")
    jo2 = Job(0, cu, "Weapon_Staff_Iron", 1.0, 2.0, 1, 250, D_([1, 0, 0]), JLong(50000))
    jo2.shots = 3
    jo2.until = 60000
    K.eq([bool(S4.watchEnd(jo2, JLong(t))) for t in (59999, 60000)], [False, True], "X watchEnd: no shot fired -> over at its time")
    jo2.lastShot = 59500
    jo2.shots = 2
    K.eq([bool(S4.watchEnd(jo2, JLong(t))) for t in (60000, 62499, 62500)], [False, False, True], "X watchEnd: time up with a shot in flight -> its grace first")
    late = Shot(0.0, 0.0, 0.0, 30.0, 3001, cu, JString("q"))
    S4.CLOCK = 60001
    S4.staffShot(late, cu, None)
    K.eq(int(late.sig4), 1, "X a shot after the overload's time is normal")
    hand.put(cu, JString("Weapon_Staff_Cobalt"))
    jo2.until = 99999
    S4.OVER.put(cu, jo2)
    sw = Shot(0.0, 0.0, 0.0, 30.0, 3001, cu, JString("q"))
    S4.staffShot(sw, cu, None)
    K.eq(int(sw.sig4), 1, "X a shot from ANOTHER staff than the one cast with is normal")
    S4.OVER.clear()
    S4.CLOCK = 0
    Leap.HAND = None
    TW.ALL.clear()
    # ---- FIX: the quit hook (ArmorySig4.quit from ArmoryQuit) drops the quitter's Overload watch + released Bindings; clear() empties OVER
    qu, qo = UUID.randomUUID(), UUID.randomUUID()
    S4.OVER.put(qu, Job(0, qu, "Weapon_Staff_Iron", 1.0, 2.0, 1, 250, D_([1, 0, 0]), JLong(1)))
    S4.OVER.put(qo, Job(0, qo, "Weapon_Staff_Iron", 1.0, 2.0, 1, 250, D_([1, 0, 0]), JLong(1)))
    Soul.LASTB.put(qu, JArray(JObject)(4))
    Soul.LASTB.put(qo, JArray(JObject)(4))
    S4.quit(qu)
    S4.quit(None)
    K.eq((bool(S4.OVER.containsKey(qu)), bool(Soul.LASTB.containsKey(qu)), bool(S4.OVER.containsKey(qo)), bool(Soul.LASTB.containsKey(qo))),
         (False, False, True, True), "X FIX quit: the quitter's OVER + Soul.LASTB entries go, another player's stay; quit(null) is quiet")
    S4.clear()
    K.eq(int(S4.OVER.size()), 0, "X FIX clear (setup / shutdown): OVER empty")
    # ---- Soul Release: the released Bindings' record (Soul.release writes it; read back within the window)
    Soul.LASTB.clear()
    K.check(int(Soul.LASTB.size()) == 0 and int(Soul.SIG_GAINS) == 0, "X Soul.LASTB / SIG_GAINS start empty")
    # ---- the codes + ROOT_CHECK
    K.eq([int(Defs.pidCode(JString(str(m)))) for m in Defs.SG4_MARK], list(range(13005, 13012)), "X the 7 markers -> codes 13005-13011")
    K.eq(([int(Defs.pidCode(JString(str(m)))) for m in Defs.SG2_MARK], int(Defs.pidCode(JString("SkyyArmory_Wand_Ricochet"))), int(S4.CODE0)),
         ([13001, 13002, 13003, 13004], 13000, 13005), "X sig2 keeps 13001-13004, the Ricochet 13000")
    rc = [str(x) for x in Defs.ROOT_CHECK]
    K.check(all(r in rc for r in ROOTS + SIG2_ROOTS), "X ArmoryDefs.ROOT_CHECK lists the 7 + 4 signature roots (%d roots checked)" % len(rc))
    # ---- the bridge
    f = Fn()

    def ask(i):
        a = JArray(JObject)(1)
        a[0] = JString(i)
        r = f.apply(a)
        return None if r is None else (str(r[0]), str(r[1]), int(r[2]), str(r[3]), bool(r[4]), [str(r[k].getClass().getName()) if not isinstance(r[k], str) else "java.lang.String" for k in range(5)])
    T5 = ["java.lang.String", "java.lang.String", "java.lang.Integer", "java.lang.String", "java.lang.Boolean"]
    want_ans = {0: ("Arcane Overload", "Next 3 quick shots (10 s) hit 2x and give their Mana back.", 20, "quick hit +1~, charged hit +2", True, T5),
                1: ("Soul Release", "Pop every Binding: each takes its damage again, allies heal 25%.", 20, "+2 a second while a Binding hits", True, T5),
                2: ("Skewer Charge", "Dash 6 blocks; first enemy carried, hit twice (1.25x), pinned.", 20, "stab +1.5~", True, T5),
                3: ("Cleave", "3 chops (0.8x each) on every enemy in a 180-degree arc in front.", 20, "swing +1.5~", True, T5),
                4: ("Skull Crack", "One 2.5x blow on the enemy in front; it is stunned 1 s.", 20, "swing +1.5~", True, T5),
                5: ("Meridian Cut", "Two cuts (1.25x each) on every enemy in a 160-degree arc, 5 blocks.", 20, "swing +1.5~", True, T5),
                6: ("Iron Curtain", "A 3-block wall of force for 4 s shoves enemies that touch it.", 20, "shield hit +2~", True, T5)}
    wrong = [(i, ask(i)) for i, (fm, n) in fi.items() if ask(i) != want_ans[fm]]
    K.eq(wrong, [], "X armory:fn:sig: every item of the 7 families answers its signature with plain java.lang types (%d); FIX: the lines name the multiplier" % len(fi))
    K.eq(ask("Weapon_Wand_Iron")[0:4], ("Ricochet", "A bolt jumps from your target to the nearest enemy, up to 8 hits.", 20, "quick hit +1~, charged hit +2"),
         "X the wand still answers Ricochet (unchanged)")
    K.eq((ask("Weapon_Bo_Iron")[0], ask("Weapon_Kunai_Iron")[0], ask("Weapon_Spellbook_Iron")[0]), ("Whirling Staff", "Kunai Fan", "Page Storm"),
         "X sig2's answers unchanged (asked first)")
    K.eq([ask(i) for i in ("Weapon_Sword_Iron", "Weapon_Staff_Bone", "Weapon_Staff_Crystal_Flame", "Hepta_Axe", "Weapon_Shield_Iron", "Nope", "Weapon_Spear_Onyxium", "Weapon_Club_Zombie_Arm")], [None] * 8,
         "X not ours -> null (SkyyGear shows the vanilla / pack answer or 'none')")
    Cfg.SG4_AX_HITS, Cfg.SG4_SO_HEAL, Cfg.SG4_SO_DMG, Cfg.SG4_SP_PIN, Cfg.SG4_CL_STUN, Cfg.SG4_GS_PUSH, Cfg.SG4_LS_ON = 1, 0, 1.5, 0.0, 0.0, 0.0, False
    live = (ask("Weapon_Axe_Iron")[1], ask("Weapon_Wand_SoulOrb")[1], ask("Weapon_Spear_Iron")[1], ask("Weapon_Club_Iron")[1], ask("Weapon_GreatShield_Iron")[1],
            ask("Weapon_Longsword_Iron")[4])
    K.eq(live, ("One chop (0.8x) on every enemy in a 180-degree arc in front.", "Pop every Binding: each takes 1.5x its damage.",
                "Dash 6 blocks; first enemy carried, hit twice (1.25x).", "One 2.5x blow on the enemy in front.", "A 3-block wall of force for 4 s hits enemies that touch it.",
                False), "X the texts follow the live rows (1 chop, no heal, x1.5, no pin, no stun, no shove; longsword off -> ready false)")
    Cfg.useDefaults()
    Cfg.SG4_ST_SHOTS, Cfg.SG4_ST_SEC, Cfg.SG4_ST_DMG, Cfg.SG4_SO_DMG, Cfg.SG4_SO_HEAL, Cfg.SG4_SP_DIST, Cfg.SG4_AX_HITS, Cfg.SG4_AX_ARC = 10, 29.75, 4.75, 4.75, 100, 11.75, 6, 360
    Cfg.SG4_CL_STUN, Cfg.SG4_LS_ARC, Cfg.SG4_LS_R, Cfg.SG4_GS_W, Cfg.SG4_GS_SEC = 2.75, 360, 7.75, 7.75, 9.75
    Cfg.SG4_SP_DMG, Cfg.SG4_AX_DMG, Cfg.SG4_CL_DMG, Cfg.SG4_LS_DMG = 4.75, 4.75, 7.75, 4.75          # FIX: the multipliers at their maxima too
    longest = [ask(fi_)[1] for fi_ in ("Weapon_Staff_Iron", "Weapon_Wand_SoulOrb", "Weapon_Spear_Iron", "Weapon_Axe_Iron", "Weapon_Club_Iron",
                                       "Weapon_Longsword_Iron", "Weapon_GreatShield_Iron")]
    K.check(all(len(t) <= 70 for t in longest), "X every text at the rows' maxima fits 70 characters: %s" % [(len(t), t) for t in longest if len(t) > 64])
    Cfg.useDefaults()
    # ---- SkyyGear 0.3.43 reads it (its tooltip answer) when the jar is on the class path
    try:
        br.put("armory:fn:sig", f)
        GX = JClass("com.skyy.gear.GearSigX")
        g0 = GX.sigOf(JString("Weapon_Axe_Iron"))
        g1 = GX.sigOf(JString("Weapon_Wand_SoulCage_Iron"))
        g2 = GX.sigOf(JString("Weapon_Longsword_Lead_SkyWynn"))
        K.eq((str(g0[0]), str(g0[1]), int(g0[2]), str(g0[3]), str(g1[0]), str(g2[0])),
             ("Cleave", "3 chops (0.8x each) on every enemy in a 180-degree arc in front.", 20, "swing +1.5~", "Soul Release", "Meridian Cut"),
             "X SkyyGear 0.3.43 GearSigX.sigOf takes the answer through armory:fn:sig (a vanilla id too)")
        try:
            seg = GX.charge(20, JString("swing +1.5~"), 1.0, 1.0)
            K.notes.append("X SkyyGear charge line segments for the axe: %s" % [str(x) for x in seg])
        except Exception as ex2:
            K.notes.append("X SkyyGear charge() not run in the bare JVM (%s)" % str(ex2)[:120])
        br.remove("armory:fn:sig")
    except Exception as ex:
        K.notes.append("X SkyyGear GearSigX not run (%s) - SkyyGear's own harness renders the block" % str(ex)[:200])
    # ---- the glue with no engine: quiet, never throws
    try:
        S4.onHit(None, None, None)
        S4.staffGain(None, None, None, 3001)
        S4.filter(None, None, None)
        S4.staffShot(None, None, None)
        S4.marker(None, None, 13005, None, None)
        why_m = str(S4.LAST_WHY)
        S4.marker(None, None, 13004, None, None)
        why_c = str(S4.LAST_WHY)
        K.eq((why_m, why_c), ("no caster", "not a signature marker"), "X marker: no projectile record = no caster; sig2's code = not ours (quiet)")
        K.check(not bool(S4.step(None, None, None, JLong(5))), "X step(null) = ended")
        S4.run(None, None, None, JLong(5))
        st = JClass("java.lang.Object")()
        tw = TW.get(st)
        K.check(bool(tw.idle()), "X a fresh TravWorld is idle")
        jw = Job(3, u, "Weapon_Axe_Iron", 10.0, 0.8, 3, 250, D_([1, 0, 0]), JLong(100000))
        tw.sig4.add(jw)
        K.check(not bool(tw.idle()), "X TravWorld.idle() sees a waiting signature job (TravTick keeps the world)")
        S4.run(tw, None, None, JLong(99000))
        K.eq(int(tw.sig4.size()), 1, "X run: a job not yet due is kept")
        S4.run(tw, None, None, JLong(100000))
        K.eq((int(tw.sig4.size()), str(S4.LAST_WHY)), (0, "the caster left this world"), "X run -> step: a due job whose caster is gone is dropped")
        jw0 = Job(0, u, "Weapon_Staff_Iron", 1.0, 2.0, 1, 250, D_([1, 0, 0]), JLong(100000))
        jw0.until = 110000
        S4.OVER.put(u, jw0)
        tw.sig4.add(jw0)
        S4.run(tw, None, None, JLong(100000))
        K.eq((int(tw.sig4.size()), bool(S4.OVER.containsKey(u))), (0, False), "X run: an ended Arcane Overload job leaves OVER too")
        K.check(bool(tw.idle()), "X ... and the world is idle again")
        TW.ALL.remove(st)
    except Exception as ex:
        K.check(False, "X the glue edges threw: %s" % str(ex)[:300])
    K.notes.append("X status line: %s" % str(S4.statusText()))
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
    K.check(b"sig.staff." not in b0 and b"sig.gs." not in b0, "D the live file has none of the new keys (they read their defaults)")
    hashes = [tree_hash(home)]
    for start in (1, 2):
        rs = [str(getattr(Cfg, m)()) for m in MIGS]
        Cfg.load()
        hashes.append(tree_hash(home))
        if start == 1:
            K.notes.append("D start 1 migrations: %s" % [x[:120] for x in rs if x])
    K.check(hashes[1] == hashes[2], "D start 2 changes nothing")
    t1 = open(fp, "rb").read()
    K.check(b"sig.staff." not in t1 and b"0.1.46" not in t1 and (b"\r\n" in b0) == (b"\r\n" in t1), "D 0.1.46 writes no row of its own; line endings kept")
    K.eq((bool(Cfg.SG4_ST_ON), int(Cfg.SG4_ST_SHOTS), float(Cfg.SG4_AX_GAIN), int(Cfg.SG4_LS_ARC), bool(Cfg.SG2_REFUND)), (True, 3, 1.5, 160, True),
         "D the new keys read their defaults")
    K.notes.append("D files changed by start 1: %s" % sorted(k for k in set(hashes[0]) | set(hashes[1]) if hashes[0].get(k) != hashes[1].get(k))[:8])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ArmorySig4", "Sig4Job"],
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
