"""Harness for SkyyArmory 0.1.52 (lean round gfist: the fist weapons keep both fists on screen in first person; tools/armory_0_1_52_patch.py).
Build first:
    python tools/armory_0_1_52_patch.py && python SkyyArmory/build_skyyarmory_0.1.52.py
    python SkyyArmory/test_skyyarmory_0.1.52.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S   static   the patch re-runs to identical bytes, line endings kept; no new class / system / command; the jar vs 0.1.51: nothing added or
               removed, changed non-class = manifest + SkyyArmory_Fist.json only; in that set exactly the 36 movement entries changed and only
               their FirstPerson (-> the vanilla Dual_Handed/Unarmed/Idle_FPS = the vanilla Gloves set's movement pose); every ThirdPerson /
               Speed / Looping / attack / Guard entry byte-equal; the 15 gauntlets + 5 wraps + 2 Untiered fists (and nothing else) use the set.
               VISIBILITY (the judge): forward kinematics on the Assets.zip files (arm + forearm quaternions turning a hanging 2-length arm;
               +z forward, +y up). In view = both hands forward >= 1.0 and height >= -0.6. Yardstick: the vanilla Daggers set's every
               first-person file (both daggers on screen in game) passes; the unarmed Guard (Skyy sees the gauntlets) passes; the vanilla
               Default idle / walk / run (Skyy: no hands) fail. Then: every non-attack entry of the new set either keeps the previous
               first-person pose (Step / Jump / Fall) or passes - except the declared vanilla actions Interact + MantleUp / Left / Right.
               The new pose keys no Attachment bone (as the Guard / punch poses), so the held model is not turned.
  X   exec     EXECUTED in the JVM: the REAL engine codec (ItemPlayerAnimations) decodes the jar's SkyyArmory_Fist set (no unknown key, no
               validation failure); the decoded Idle / Walk / Run / Sprint / Crouch / Swim / Climb entries carry the fists-up file, Jump / Fall
               keep the previous pose, the Guard / jab entries are unchanged; the 0.1.51 set decodes to the Default files (the before)
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.51 -> 0.1.52: exactly the planned members (EXPECT = the version text only)
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory: 0.1.52 writes nothing; start 2 = start 1
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the client drawing the gauntlet / wrap models in the fists-up pose (the client renders; the
server only sends the set), how the static stance feels while walking / running (the vanilla Gloves set does the same).
"""
import os, sys, json, subprocess, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gfist", "arm")]
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.52", "0.1.51"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyarmory_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyarmory_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "armory_0_1_52_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
AZP = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")          # read-only
P_FIST = "Server/Item/Animations/SkyyArmory/SkyyArmory_Fist.json"
READY = "Characters/Animations/Items/Dual_Handed/Unarmed/Idle_FPS.blockyanim"
KEYS = ["Idle", "Walk", "WalkBackward", "Run", "RunBackward", "Sprint", "Crouch", "CrouchWalk", "CrouchWalkBackward", "CrouchSlide",
        "FlyIdle", "Fly", "FlyBackward", "FlyFast", "FlyCrouchIdle", "FlyCrouch", "FlyCrouchBackward",
        "SwimIdle", "Swim", "SwimBackward", "SwimFast", "SwimJump", "SwimFloat", "SwimSink", "SwimDive", "SwimDiveBackward", "SwimDiveFast",
        "FluidIdle", "FluidWalk", "FluidWalkBackward", "FluidRun", "ClimbIdle", "ClimbUp", "ClimbDown", "ClimbLeft", "ClimbRight"]
KEEP = ["Interact", "MantleUp", "MantleLeft", "MantleRight"]
EXPECT = {
    # the version text only (0.1.51 -> 0.1.52), as every Armory round
    # (a string diff of every changed class shows only "0.1.51" -> "0.1.52"; ArmoryDefs' version constants are ConstantValue fields = no member diff)
    "SkyyArmoryPlugin": ["~m setup", "~m start"], "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "ArmoryCheck": ["~m packCheck", "~m packOf"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040",
        "migrateP5")

_ORIG_COMPARE = HK.run_compare


def compare_with_assets(out, jar, old_jar, pkg, expect, added, removed=()):
    _ORIG_COMPARE(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    ed = sorted(n for n in ea | eb if n not in ea or n not in eb or za.read(n) != zb.read(n))
    kept = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    if ed == sorted(["manifest.json", P_FIST]):
        d["ok"] += 1
    else:
        kept.append("C: non-class entries changed = manifest + the fist animation set: got %s" % ed[:10])
    d["fails"] = kept
    d["notes"].append("C: non-class entries changed = manifest + SkyyArmory_Fist.json (the kit's manifest-only check replaced)")
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = compare_with_assets


# ---------------------------------------------------------------------------------------------------------------- the visibility judge
def hands(vz, path):
    """{side: (forward, height)} of the hand at the end of upper arm + forearm (1 length each, hanging at rest), averaged over the arm keys"""
    def qm(a, b):
        return (a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1], a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
                a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3], a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2])

    def rt(q, v):
        return qm(qm(q, (v[0], v[1], v[2], 0.0)), (-q[0], -q[1], -q[2], q[3]))[:3]

    def q0(k):
        return tuple(float(k["delta"][c]) for c in "xyzw")
    na = json.loads(vz.read("Common/" + path).decode("utf-8-sig")).get("nodeAnimations") or {}
    ident = [{"delta": {"x": 0, "y": 0, "z": 0, "w": 1}}]
    out = {}
    for s in ("R", "L"):
        ak = (na.get(s + "-Arm") or {}).get("orientation") or ident
        fq = q0(((na.get(s + "-Forearm") or {}).get("orientation") or ident)[0])
        tips = []
        for k in ak:
            qa = q0(k)
            e, h = rt(qa, (0, -1, 0)), rt(qm(qa, fq), (0, -1, 0))
            tips.append((e[2] + h[2], e[1] + h[1]))
        out[s] = (round(sum(t[0] for t in tips) / len(tips), 2), round(sum(t[1] for t in tips) / len(tips), 2))
    return out


def seen(vz, path):
    return all(f >= 1.0 and h >= -0.6 for f, h in hands(vz, path).values())


def bones(vz, path):
    return sorted((json.loads(vz.read("Common/" + path).decode("utf-8-sig")).get("nodeAnimations") or {}).keys())


# ---------------------------------------------------------------------------------------------------------------- S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyArmory 0.1.52 - build script') and g.count('VERSION = "0.1.52"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count("makeClass(") - o.count("makeClass(")),
         (0, 0, 0), "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb, vz = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar), zipfile.ZipFile(AZP)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S nothing added, nothing removed")
    nc = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(nc, sorted(["manifest.json", P_FIST]), "S changed non-class = manifest + SkyyArmory_Fist.json (every item / interaction / model / lang byte-identical)")
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    K.check(mb["Version"] == VERSION and dict(ma, Version=VERSION, Name=ma["Name"].replace(OLD, VERSION)) == mb, "S manifest: only the Version changed")
    so, sn = json.loads(za.read(P_FIST).decode("utf-8")), json.loads(zb.read(P_FIST).decode("utf-8"))
    ao, an = so["Animations"], sn["Animations"]
    K.eq(dict(sn, Animations=None), dict(so, Animations=None), "S the set's Camera / WiggleWeights / no Parent unchanged")
    K.eq(sorted(an), sorted(ao), "S the same entry names")
    ch = sorted(k for k in an if an[k] != ao.get(k))
    K.eq(ch, sorted(KEYS), "S exactly the 36 movement entries changed")
    K.check(all(an[k]["FirstPerson"] == READY and dict(an[k], FirstPerson=None) == dict(ao[k], FirstPerson=None) for k in KEYS),
            "S in those only FirstPerson changed (-> %s); ThirdPerson / Speed / Looping / blend kept" % READY)
    K.check(all(ao[k]["FirstPerson"].startswith(("Characters/Animations/Default/", "Characters/Animations/Swim/", "Characters/Animations/Fly/",
                                                  "Characters/Animations/Climb/", "Characters/Animations/Slide/")) for k in KEYS),
            "S the replaced files were the vanilla Default-set movement poses")
    att = [k for k in an if "/Attacks/" in an[k].get("FirstPerson", "")]
    K.check(sorted(att) == sorted(["SwingLeft", "SwingRight", "SwingUpLeft", "Guard", "JabLeft", "JabRight", "PowerUp"]) and all(an[k] == ao[k] for k in att),
            "S the 7 attack / Guard entries byte-equal: %s" % sorted(att))
    # ---- the judge, calibrated on vanilla
    dg = json.loads(vz.read("Server/Item/Animations/Daggers.json").decode("utf-8-sig"))["Animations"]
    dfp = sorted(set(e["FirstPerson"] for e in dg.values() if "FirstPerson" in e and "/Attacks/" not in e["FirstPerson"] and "Dash" not in e["FirstPerson"]
                     and "Backflip" not in e["FirstPerson"] and "Interact" not in e["FirstPerson"]))
    dbad = [p_ for p_ in dfp if not seen(vz, p_)]
    K.check(len(dfp) >= 20 and not dbad, "S yardstick: all %d vanilla Daggers movement first-person files keep both hands in view (%s)" % (len(dfp), dbad[:3]))
    df = json.loads(vz.read("Server/Item/Animations/Default.json").decode("utf-8-sig"))["Animations"]
    K.check(not [k for k in ("Idle", "Walk", "Run", "Sprint", "Crouch", "SwimIdle", "FlyIdle") if seen(vz, df[k]["FirstPerson"])],
            "S yardstick: the vanilla Default idle / walk / run / sprint / crouch / swim / fly hide the hands (Skyy's screenshot: no hands)")
    K.check(seen(vz, an["Guard"]["FirstPerson"]), "S yardstick: the unarmed Guard pose shows the hands (Skyy: the gauntlets show while blocking) %s" % hands(vz, an["Guard"]["FirstPerson"]))
    K.check(seen(vz, READY), "S the fists-up pose keeps both hands in view %s" % hands(vz, READY))
    K.check(not [b_ for b_ in bones(vz, READY) if "Attachment" in b_] and bones(vz, READY) == bones(vz, an["Guard"]["FirstPerson"]),
            "S the fists-up pose keys only the arm / forearm / hand bones, like the Guard (the held model keeps its blocking orientation)")
    gl = json.loads(vz.read("Server/Item/Animations/Gloves.json").decode("utf-8-sig"))["Animations"]
    K.check(all(gl[k]["FirstPerson"] == READY for k in ("Idle", "Walk", "Run", "Crouch", "Jump", "Fall", "Swim", "ClimbIdle")),
            "S vanilla precedent: the vanilla Gloves set plays this file for its movement states")
    bad = []
    for k, e in an.items():
        fp = e.get("FirstPerson")
        if fp is None:
            if not e.get("KeepPreviousFirstPersonAnimation"):
                bad.append(k)
        elif "/Attacks/" not in fp and k not in KEEP and not seen(vz, fp):
            bad.append("%s %s" % (k, hands(vz, fp)))
    kp = sorted(k for k, e in an.items() if "FirstPerson" not in e)
    K.check(not bad, "S EVERY non-attack entry keeps both fists in view or keeps the previous pose (%d keep-previous: %s): %s" % (len(kp), kp, bad))
    K.check(all(not seen(vz, ao[k]["FirstPerson"]) for k in KEYS), "S each of the 36 replaced files did hide the hands in 0.1.51")
    users = sorted(json.loads(zb.read(n).decode("utf-8")).get("Id", os.path.basename(n)[:-5]) for n in nb if n.startswith("Server/Item/Items/") and n.endswith(".json")
                   and json.loads(zb.read(n).decode("utf-8")).get("PlayerAnimationsId") == "SkyyArmory_Fist")
    K.check(len(users) == 22 and len([u for u in users if u.startswith("Weapon_Fist_Gauntlets_")]) == 15 and len([u for u in users if u.startswith("Weapon_Fist_Wraps_")]) == 5
            and sorted(u for u in users if u.startswith("Weapon_Fist_UT_")) == ["Weapon_Fist_UT_EmberrootWraps", "Weapon_Fist_UT_SteppeWind"],
            "S the set's users = the 15 gauntlets + 5 wraps + the 2 Untiered fist weapons (Steppe Wind, Emberroot Wraps): %d" % len(users))
    K.notes.append("S hands (forward, height): fists-up %s, Default idle %s, Daggers idle %s, Guard %s" % (
        hands(vz, READY), hands(vz, df["Idle"]["FirstPerson"]), hands(vz, dg["Idle"]["FirstPerson"]), hands(vz, an["Guard"]["FirstPerson"])))
    K.save()


# ---------------------------------------------------------------------------------------------------------------- X: executed
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(scratch, "universe")]))
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")          # the 0.1.51 harness's bare HytaleServer with an EventBus
    uf.setAccessible(True)
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = uf.get(None).allocateInstance(HS.class_)

    def setf(obj, cls, name, v):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, v)
    setf(hs, HS, "eventBus", JClass("com.hypixel.hytale.event.EventBus")(False))
    setf(None, HS, "instance", hs)
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    IPA = JClass("com.hypixel.hytale.server.core.asset.type.itemanimation.config.ItemPlayerAnimations")
    if AR.getAssetStore(IPA.class_) is None:
        HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")

        @JImplements("java.util.function.Function")
        class GetId:
            @JOverride
            def apply(self, o): return o.getId()
        AR.register(HAS.builder(IPA.class_, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")()).setPath("Item/Animations")
                    .setCodec(IPA.CODEC).setKeyFunction(GetId()).build())
        K.notes.append("X registered an ItemPlayerAnimations store by hand")
    AEI = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo")
    ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
    Paths = JClass("java.nio.file.Paths")

    def dec(key, text):
        ei = AEI(Paths.get(key + ".json"), ADT(IPA.class_, key, None))
        try:
            o = AR.getAssetStore(IPA.class_).getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception as e:
            return None, "exception " + str(e)[:300]
        prob = []
        vr = ei.getValidationResults()
        if vr is not None and vr.hasFailed():
            prob.append("validation failed")
        uk = [str(x) for x in ei.getUnknownKeys()]
        if uk:
            prob.append("unknown keys %s" % uk)
        return o, "; ".join(prob)

    def fp(o, k):
        a = o.getAnimations().get(JString(k))
        if a is None:
            return None, None
        f_, kp_ = None, None
        for m in a.getClass().getMethods():
            n = str(m.getName())
            if m.getParameterCount() == 0 and n.lower() in ("getfirstperson", "firstperson"):
                f_ = m.invoke(a)
            if m.getParameterCount() == 0 and "keeppreviousfirstperson" in n.lower():
                kp_ = m.invoke(a)
        if f_ is None:
            for fld in a.getClass().getDeclaredFields():
                n = str(fld.getName()).lower()
                fld.setAccessible(True)
                if n == "firstperson":
                    f_ = fld.get(a)
                if "keepprevious" in n:
                    kp_ = fld.get(a)
        return (None if f_ is None else str(f_)), (None if kp_ is None else bool(kp_))
    new, wn = dec("SkyyArmory_Fist", zipfile.ZipFile(jar).read(P_FIST).decode("utf-8"))
    old, wo = dec("SkyyArmory_Fist", zipfile.ZipFile(OLD_JAR).read(P_FIST).decode("utf-8"))
    K.check(new is not None and not wn, "X the 0.1.52 SkyyArmory_Fist decodes through the engine ItemPlayerAnimations codec: %s" % wn)
    K.check(old is not None and not wo, "X the 0.1.51 set decodes too (the before): %s" % wo)
    if new is not None and old is not None:
        K.eq(int(new.getAnimations().size()), int(old.getAnimations().size()), "X the same number of decoded entries")
        got = dict((k, fp(new, k)[0]) for k in ("Idle", "Walk", "Run", "Sprint", "Crouch", "SwimIdle", "ClimbUp", "FlyIdle"))
        K.check(all(v is not None and v.endswith("Dual_Handed/Unarmed/Idle_FPS.blockyanim") for v in got.values()),
                "X decoded movement entries carry the fists-up first-person file: %s" % got)
        was = dict((k, fp(old, k)[0]) for k in ("Idle", "Walk", "Run"))
        K.check(all(v is not None and "/Default/" in v for v in was.values()), "X the 0.1.51 decode had the Default (arms-down) files: %s" % was)
        kp = [fp(new, k) for k in ("Jump", "JumpRun", "Fall", "FallFar", "StepWalk")]
        K.check(all(f_ is None and k_ is True for f_, k_ in kp), "X Jump / Fall / Step keep the previous (fists-up) first-person pose: %s" % kp)
        K.eq([fp(new, k)[0] for k in ("Guard", "JabLeft", "JabRight", "PowerUp")], [fp(old, k)[0] for k in ("Guard", "JabLeft", "JabRight", "PowerUp")],
             "X Guard + jab entries decode exactly as in 0.1.51")
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
    hashes = [HK.tree_hash(home)]
    for start in (1, 2):
        rs = [str(getattr(Cfg, m)()) for m in MIGS]
        Cfg.load()
        hashes.append(HK.tree_hash(home))
        if start == 1:
            K.notes.append("D start 1 migrations: %s" % [x[:120] for x in rs if x])
    K.check(hashes[1] == hashes[2], "D start 2 changes nothing")
    K.check(hashes[0] == hashes[1], "D start 1 changes nothing either (0.1.52 has no row / migration)")
    t1 = open(fp, "rb").read()
    K.check(b"0.1.52" not in t1 and (b"\r\n" in b0) == (b"\r\n" in t1), "D 0.1.52 writes nothing of its own; line endings kept")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
