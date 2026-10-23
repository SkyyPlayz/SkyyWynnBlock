"""Harness for SkyyGear 0.3.41 (gear041: Quirk's fixed held tools, Farming UV boxes, a reproducible build, the vanilla Flame longsword -
tools/gear_0_3_41_patch.py).
Build first:
    python tools/gear_0_3_41_patch.py && python SkyyGear/build_skyygear_0.3.41.py
    python SkyyGear/test_skyygear_0.3.41.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes, line endings kept, no new class / command / system; HP5 / HP6 / HP7_TBL sorted by
              (-len, text). THE JAR: the 4 Quirk models = her FIXED files (JSON equal), never her rejected originals; every one passes the
              build's own held-tool check (_g26_check, run here from the generated script) with no FIX line; the 25 Multitools / Harvesters
              use her model + a texture whose size is her texture's + a 64 x 64 icon, Titanium / Lumen = her fixed textures byte for byte; no
              0.3.12 Harvester recolour art is left; FARMING: every UV box of the 60 Quirk models lands on the same texels in the padded jar
              texture as in her file (and inside her file), padding transparent; every PNG outside Common/UI/ is a multiple of 32; no file
              overrides Weapon_Longsword_Flame
  R  repro    builds the generated script TWICE more (PYTHONHASHSEED 1 and 2, SKYWYNN_GEAR_OUTDIR = scratch): both jars byte-identical
              to each other and to SkyyGear/SkyyGear-0.3.41.jar; then the FALLBACK build (SKYWYNN_G41_FIXED_DIR = a missing folder): the loud
              NOTE, 0 items use her model, 25 keep the 0.3.25 look, the FIX lines for Quirk, no Quirk model in that jar
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.40 -> 0.3.41 (EXPECT below)
  X  exec     EXECUTES in a bare JVM: GearESw.flat / swingOk for the Flame longsword (Fire swing yes; Physical / Ice / no damage sequence /
              a shot / esword.on off no), innate / abilityText / abilityHead unchanged for it (no Armory element), the 4 Armory swords exactly
              as 0.3.40, counted on a projectile hit with a stand-in Flame longsword stack (no swing, a non-swing sword hit), statusText,
              GearCfg.HP7_TBL order, the esword.on help text
  W  wiring   bytecode: swing asks flat before shotSrc, swingOk asks flat, counted asks flat; weaponHit2 still gates on GearESw.counted
  D  live     start TWICE on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: the second start changes nothing, no new row written
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): a real Flame longsword swing's DAMAGE_SEQUENCE + Fire cause through GearHitSys (the bare JVM has no
DamageCause asset map), how her models sit in the hand / swing in game, the icons in the inventory.
Scratch: tools/dev/scratch/gear041/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.41"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gear041", "harness")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.40.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_41_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.40.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
PRIV = os.environ.get("SKYWYNN_PRIVATE_ART") or os.path.join(os.path.dirname(ROOT), "SkyWynn-PRIVATE-art")
TOOLS_PRIV = os.path.join(PRIV, "metal-art", "Tools-PRIVATE")
FIXED = os.path.join(TOOLS_PRIV, "z5-held-tools-fixed")
FARM = os.path.join(PRIV, "farming-armor")
ADDED = []
EXPECT = {
    "GearCfg": ["~<clinit>", "~m defaultsText"], "CfgRows": ["~m header"], "CfgRows2": ["~<clinit>"], "CfgFn": ["~m opExport"], "SkyyGearPlugin": ["~m setup"],
    "GearESw": ["+f FLAT", "+m flat", "~<clinit>", "~m counted", "~m statusText", "~m swing", "~m swingOk"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
IDS = ["Weapon_Elemental_Flame", "Weapon_Elemental_Ice", "Weapon_Elemental_Gravity", "Weapon_Elemental_Poison"]
FL = "Weapon_Longsword_Flame"


def _jload(b):
    return json.loads(b.decode("utf-8-sig") if isinstance(b, (bytes, bytearray)) else b)


def run_static(out, jar, scratch, home):
    import skyyart as SA
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.41 - build script') and g.count('VERSION = "0.3.41"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 0), "S no new system / command / class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.check("The Armory's 4 Elemental swords + the vanilla Flame longsword hit like our weapons. Off = flat hits." in g, "S the esword.on help names the Flame longsword (<= 100 chars)")
    K.check(g.count("key=lambda _t: (-len(_t), _t))") == 3 and not [l_ for l_ in g.splitlines() if "_TBL = sorted(set(" in l_ and "key=len" in l_],
            "S HP5 / HP6 / HP7_TBL: longest first, ties by text")
    z = zipfile.ZipFile(jar)
    names = set(z.namelist())
    # ---- the held tools
    AZ = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    hoe = [n for n in AZ.namelist() if n.endswith("/Tool_Hoe_Thorium.json") and n.startswith("Server/Item/Items/")]
    gl = {"SA": SA, "AZ": AZ, "json": json,
          "G26_VAN": {"Multitool": "Items/Tools/Pickaxe/Mithril.blockymodel", "Harvester": _jload(AZ.read(hoe[0]))["Model"]},
          "G26_VNAME": {"Multitool": "the vanilla Mithril pickaxe", "Harvester": "the vanilla Thorium hoe"}}
    exec(g[g.index("def _g26_json(b):"):g.index("def _g26_repose(")], gl)
    K.check(os.path.isdir(FIXED), "S Quirk's fixed folder is on this PC: %s" % FIXED)
    for t in ("Multitool", "Harvester"):
        for b in ("Titanium", "Lumen"):
            jp = "Common/Items/SkyyGear/Metal/Quirk/%s_%s.blockymodel" % (t, b)
            K.check(jp in names, "S the jar ships %s" % jp)
            if jp not in names or not os.path.isdir(FIXED):
                continue
            mj = _jload(z.read(jp))
            fx = _jload(open(os.path.join(FIXED, "%s_%s.blockymodel" % (b, t)), "rb").read())
            K.check(mj == fx, "S %s %s in the jar = her FIXED file (JSON equal)" % (b, t))
            op = os.path.join(TOOLS_PRIV, b, t + ".blockymodel")
            if os.path.isfile(op):
                K.check(mj != _jload(open(op, "rb").read()), "S %s %s is not her rejected original" % (b, t))
            tex = z.read("Common/Items/Tools/SkyyMetal/%s/%s_Texture.png" % (t, b))
            K.check(tex == open(os.path.join(FIXED, "%s_%s_Texture.png" % (b, t)), "rb").read(), "S %s %s texture = her fixed texture byte for byte" % (b, t))
            f, n = gl["_g26_check"](t, mj, tex)
            K.check(not f, "S %s %s passes the build's held-tool check in the jar: %s" % (b, t, f))
            K.check(mj["nodes"][0]["name"] == "R-Attachment" and [c.get("name") for c in mj["nodes"][0].get("children") or []] == ["Origin_Projectile"],
                    "S %s %s: R-Attachment > Origin_Projectile (her vanilla chain)" % (b, t))
            if n:
                K.notes.append("S notes %s %s: %s" % (b, t, n))
    items = []
    for nm in sorted(names):
        if nm.startswith("Server/Item/Items/SkyyGear/") and ("Multitool" in nm or "Harvester" in nm) and nm.endswith(".json"):
            j = _jload(z.read(nm))
            if j.get("Model", "").startswith("Items/SkyyGear/Metal/Quirk/"):
                items.append(nm)
                tp, ip = "Common/" + j["Texture"], "Common/" + j["Icon"]
                base = j["Model"].rsplit("_", 1)[1].split(".")[0]
                tool = j["Model"].rsplit("/", 1)[1].split("_")[0]
                ok = tp in names and ip in names and SA.png_size(z.read(ip)) == (64, 64) and \
                    SA.png_size(z.read(tp)) == SA.png_size(open(os.path.join(FIXED, "%s_%s_Texture.png" % (base, tool)), "rb").read()) and \
                    j.get("IconProperties") is not None
                K.check(ok, "S %s: her %s %s model, its texture (her size) + 64x64 icon in the jar" % (nm.rsplit("/", 1)[1], base, tool))
    K.eq(len(items), 25, "S all 25 Multitools / Harvesters use her fixed model (0 keep the 0.3.25 look)")
    left = sorted(n_ for n_ in names if n_.startswith("Common/Items/SkyyGear/Harvester/") or (n_.startswith("Common/Icons/ItemsGenerated/Tool_Sickle_Harvester_")))
    K.eq(left, [], "S no 0.3.12 Harvester recolour art left in the jar")
    # ---- farming: every UV box on the same texels
    farm = sorted(n_ for n_ in names if n_.startswith("Common/Items/Armors/SkyyFarming/") and n_.endswith(".blockymodel"))
    K.eq(len(farm), 60, "S 60 Farming models in the jar")
    faces = bad = padbad = 0
    for mp in farm:
        crop = mp.split("/")[4]
        tp = mp[:-len(".blockymodel")] + "_Texture.png"
        src_t = os.path.join(FARM, crop, *tp.split("/"))
        src_m = os.path.join(FARM, crop, *mp.split("/"))
        if not (os.path.isfile(src_t) and os.path.isfile(src_m)):
            K.check(False, "S Quirk's Farming file is on this PC: %s" % src_t)
            continue
        K.check(z.read(mp) == open(src_m, "rb").read(), "S %s = her model byte for byte (UVs untouched)" % mp)
        a, jb = SA.png_decode(open(src_t, "rb").read()), SA.png_decode(z.read(tp))
        K.check(jb.w % 32 == 0 and jb.h % 32 == 0 and jb.w >= a.w and jb.h >= a.h and jb.w - a.w < 32 and jb.h - a.h < 32, "S %s %dx%d -> %dx%d (next x32)" % (tp, a.w, a.h, jb.w, jb.h))
        for fc in SA.model_faces(_jload(z.read(mp))):
            faces += 1
            x0, y0, x1, y1 = SA.face_rect(fc)
            if x0 < 0 or y0 < 0 or x1 > a.w or y1 > a.h:
                bad += 1
                continue
            for y in range(y0, y1):
                if a.px[(y * a.w + x0) * 4:(y * a.w + x1) * 4] != jb.px[(y * jb.w + x0) * 4:(y * jb.w + x1) * 4]:
                    bad += 1
                    break
        padbad += sum(1 for y in range(jb.h) for x in range(jb.w) if (x >= a.w or y >= a.h) and jb.px[(y * jb.w + x) * 4 + 3] != 0)
    K.check(faces > 1000 and bad == 0, "S Farming: %d UV boxes, %d not on the same texels as her file" % (faces, bad))
    K.eq(padbad, 0, "S Farming: the padding is transparent")
    png = [n_ for n_ in names if n_.lower().endswith(".png") and not n_.startswith("Common/UI/")]
    odd = [n_ for n_ in png if any(v % 32 for v in SA.png_size(z.read(n_)))]
    K.check(len(png) > 300 and not odd, "S every PNG outside Common/UI/ (%d) is a multiple of 32: %s" % (len(png), odd[:4]))
    ui = [n_ for n_ in names if n_.lower().endswith(".png") and n_.startswith("Common/UI/") and any(v % 32 for v in SA.png_size(z.read(n_)))]
    K.notes.append("S Common/UI/ PNGs not x32 (UI 9-slice art, exempt as in 0.3.38; the client warns only on model textures): %d" % len(ui))
    K.check(not [n_ for n_ in names if n_.endswith("/" + FL + ".json")], "S no file overrides the vanilla Flame longsword (code path only)")
    K.save()


def _build(env_extra, outdir, log):
    env = dict(os.environ)
    env.update(env_extra)
    env["SKYWYNN_GEAR_OUTDIR"] = outdir
    os.makedirs(outdir, exist_ok=True)
    p = subprocess.run([sys.executable, GEN], capture_output=True, text=True, env=env)
    open(log, "w", encoding="utf8").write(p.stdout + "\n" + p.stderr)
    return p.returncode, p.stdout, os.path.join(outdir, "SkyyGear-%s.jar" % VERSION)


def run_repro(out, jar, scratch, home):
    K = HK.Child(out)
    d = os.path.join(scratch, "repro")
    jars = []
    for seed in ("1", "2"):
        rc, so, j = _build({"PYTHONHASHSEED": seed}, os.path.join(d, "seed" + seed), os.path.join(d, "seed%s.log" % seed))
        K.check(rc == 0 and ("assembled " + j) in so, "R build with PYTHONHASHSEED=%s assembled (rc %s)" % (seed, rc))
        jars.append(j)
    if all(os.path.isfile(j) for j in jars):
        a, b, c = (open(x, "rb").read() for x in jars + [jar])
        K.check(a == b, "R two fresh builds (hash seeds 1 / 2) are byte-identical jars (%d / %d bytes)" % (len(a), len(b)))
        K.check(a == c, "R ... and identical to SkyyGear/SkyyGear-%s.jar" % VERSION)
        if a != b:
            za, zb = zipfile.ZipFile(jars[0]), zipfile.ZipFile(jars[1])
            K.notes.append("R differing entries: %s" % [n for n in za.namelist() if n in zb.namelist() and za.read(n) != zb.read(n)][:10])
        ga, gb = zipfile.ZipFile(jars[0]).read("com/skyy/gear/GearCfg.class"), zipfile.ZipFile(jars[1]).read("com/skyy/gear/GearCfg.class")
        K.check(ga == gb, "R GearCfg.class identical (0.3.40: 8 bytes differed - the HP7_TBL tie)")
    # the fallback: the fixed folder missing = her rejected originals, the 0.3.25 look, the fix list
    rc, so, j = _build({"SKYWYNN_G41_FIXED_DIR": os.path.join(d, "no-such-folder")}, os.path.join(d, "fallback"), os.path.join(d, "fallback.log"))
    K.check(rc == 0 and ("assembled " + j) in so, "R fallback build (fixed folder missing) assembled (rc %s)" % rc)
    K.check("0.3.41 NOTE: Quirk's fixed held tools are not at" in so, "R fallback: the loud NOTE")
    K.check("0 items use her model, 25 keep the 0.3.25 look" in so and so.count("FIX for Quirk - ") >= 4 and "byte for byte)" in so,
            "R fallback: 0 use her model, 25 keep the 0.3.25 look, the FIX lines, the approved files byte for byte")
    if os.path.isfile(j):
        zf = zipfile.ZipFile(j)
        K.check(not [n for n in zf.namelist() if "/Quirk/" in n], "R fallback jar ships no Quirk model")
    K.notes.append("R fallback FIX lines: %s" % [l_ for l_ in so.splitlines() if "FIX for Quirk" in l_][:4])
    K.save()


def run_exec(out, jar, scratch, home):
    import jpype
    from jpype import JClass, JInt, JArray
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg, S = JClass(PKG + "GearCfg"), JClass(PKG + "GearESw")
    K.eq([bool(S.flat(i)) for i in (FL, "Weapon_Longsword_Cobalt", "Weapon_Staff_Crystal_Flame", "Weapon_Elemental_Flame", None)], [True, False, False, False, False],
         "X flat: only the vanilla Flame longsword")
    K.eq([bool(S.swingOk(FL, c, True, False)) for c in ("Fire", "Physical", "Ice", "Poison", None)], [True, False, False, False, False],
         "X swingOk: the Flame longsword's Fire swing only")
    K.eq([bool(S.swingOk(FL, "Fire", False, False)), bool(S.swingOk(FL, "Fire", True, True))], [False, False], "X no damage sequence / a shot = no swing")
    Cfg.ESW_ON = False
    K.check(not bool(S.swingOk(FL, "Fire", True, False)), "X esword.on off = flat again (0.3.40)")
    Cfg.ESW_ON = True
    K.eq([bool(S.swingOk(i, c, True, False)) for i, c in (("Weapon_Elemental_Flame", "Fire"), ("Weapon_Elemental_Gravity", "Fire"), ("Weapon_Elemental_Poison", "Poison"),
                                                          ("Weapon_Elemental_Ice", "Ice"), ("Weapon_Elemental_Flame", "Physical"))], [True, True, True, True, False],
         "X the 4 Armory swords exactly as 0.3.40")
    K.eq((int(S.which(FL)), int(S.elemOf(FL))), (-1, -1), "X the Flame longsword is no Armory sword (no element index)")
    t = JArray(JInt)([0] * int(JClass(PKG + "GearDefs").NS))
    K.check(S.innate(FL, t) is t or list(S.innate(FL, t)) == list(t), "X innate: no element added for the Flame longsword")
    K.check(S.abilityText(FL) is None and S.abilityHead(FL) is None, "X no Elemental Blade line on the Flame longsword")
    st = str(S.statusText())
    K.check("vanilla Flame longsword" in st, "X ready line: %s" % st)
    # counted on a projectile hit with a stand-in Flame longsword stack: no swing, counted as a non-swing sword hit
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Unsafe = JClass("sun.misc.Unsafe")
    fu = Unsafe.class_.getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    un = fu.get(None)
    fl = dict((str(f.getName()), f) for f in IS.class_.getDeclaredFields())
    s_ = un.allocateInstance(IS.class_)
    for n_, v_ in (("itemId", FL), ("quantity", JInt(1))):
        fl[n_].setAccessible(True)
        fl[n_].set(s_, v_)
    K.check(str(s_.getItemId()) == FL and not bool(s_.isEmpty()), "X stand-in Flame longsword stack")
    DMGc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DPRJc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource")
    dfl = dict((str(f.getName()), f) for f in DMGc.class_.getDeclaredFields())
    dp = un.allocateInstance(DMGc.class_)
    dfl["source"].setAccessible(True)
    dfl["source"].set(dp, un.allocateInstance(DPRJc.class_))
    n0, n1 = int(S.N[0]), int(S.N[1])
    K.check(not bool(S.swing(dp, s_)) and not bool(S.counted(dp, s_)) and int(S.N[0]) == n0 and int(S.N[1]) == n1 + 1,
            "X a projectile hit while holding the Flame longsword: no swing, counted as a non-swing sword hit (the flat branch ran)")
    K.eq([str(x) for x in Cfg.HP7_TBL], ["cost.identify.", "cost.levelUp.", "cost.reforge."], "X GearCfg.HP7_TBL: longest first, ties by text")
    K.eq([str(x) for x in Cfg.HP7_TBK], ["cost.identify", "cost.levelUp", "cost.reforge"], "X HP7_TBK follows HP7_TBL")
    K.save()


def run_wire(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for m in cp.get(PKG + cn).getDeclaredMethods():
            if str(m.getName()) == mn:
                IP(PS(bos)).print_(m)
        return str(bos.toString())
    sw = code("GearESw", "swing")
    K.check("GearESw.flat" in sw and sw.index("GearESw.flat") < sw.index("GearESw.shotSrc") < sw.index("getCause"), "W swing: which / flat, then shotSrc, then the cause")
    K.check("GearESw.flat" in code("GearESw", "swingOk") and "GearESw.flat" in code("GearESw", "counted"), "W swingOk + counted ask flat")
    w = code("GearHit", "weaponHit2")
    K.check("GearESw.counted" in w and w.index("GearHit.family") < w.index("GearESw.counted") < w.index("GearBase.weaponMult"), "W weaponHit2: the gate unchanged (family, then counted)")
    K.check("GearESw.swing" in code("GearHitSys", "handle"), "W GearHitSys: the Untiered tricks on a counted swing (unchanged)")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    fc = os.path.join(home, "config.properties")
    Cfg.FILE = JClass("java.nio.file.Paths").get(fc)
    MIG = ["migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39"]
    before = open(fc, "rb").read()
    t0 = HK.tree_hash(home)
    m1 = [str(getattr(Cfg, m)()) for m in MIG]
    Cfg.load()
    t1 = HK.tree_hash(home)
    m2 = "".join(str(getattr(Cfg, m)()) for m in MIG)
    Cfg.load()
    t2 = HK.tree_hash(home)
    K.notes.append("D start 1 on the live copy: %s" % [x[:160] for x in m1 if x])
    K.check(m2 == "" and t1 == t2, "D start 2: nothing changes (%r)" % m2[:120])
    txt = open(fc, "rb").read().decode("latin-1")
    K.check((b"\r\n" in before) == ("\r\n" in txt), "D line endings kept")
    K.eq((bool(Cfg.ESW_ON), int(Cfg.ESW_ELEM), int(Cfg.ESW_POISON)), (True, 8, 20), "D the live file loads (esword rows at their defaults)")
    K.check("esword." not in txt and "0.3.41" not in txt, "D 0.3.41 writes no row of its own (no migration)")
    K.notes.append("D files changed by start 1 (older rounds' one-time updates the live world has not run yet): %s" % sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k))[:8])
    K.save()


# the kit's compare wants only manifest.json among the non-class entries; 0.3.41 changes art on purpose - each changed entry must be one of
# the held-tool files (Quirk's models, their textures / icons / item JSON, the 0.3.12 Harvester art that leaves) or a vanilla-derived armor
# Legs JSON whose ONLY change is CosmeticsToHide + "Overpants" (the game update of 2026-10-23 08:22 added it to the vanilla Legs we copy)
HELD = ("/Metal/Quirk/", "SkyyMetal_Multitool_", "SkyyMetal_Harvester_", "/SkyyMetal/Multitool/", "/SkyyMetal/Harvester/", "Tool_Sickle_Harvester_",
        "/SkyyGear/Harvester/", "_Pickaxe_Multitool_")


def _nonclass_ok(old_jar, jar, got):
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    bad = []
    for n in got:
        if n == "manifest.json" or any(h in n for h in HELD):
            continue
        if n.endswith("_Legs.json") and n in za.namelist() and n in zb.namelist():
            a, b = _jload(za.read(n)), _jload(zb.read(n))
            ca, cb = (a.get("Armor") or {}).get("CosmeticsToHide"), (b.get("Armor") or {}).get("CosmeticsToHide")
            if isinstance(ca, list) and isinstance(cb, list) and cb == ca + ["Overpants"]:
                a["Armor"]["CosmeticsToHide"] = cb
                if a == b:
                    continue
        bad.append(n)
    return bad


_eq0 = HK.Child.eq


def _eq41(self, got, want, what):
    if what == "C: non-class entries changed":
        bad = _nonclass_ok(OLD_JAR, JAR, got)
        held = len([n for n in got if any(h in n for h in HELD)])
        legs = len([n for n in got if n.endswith("_Legs.json")])
        self.notes.append("C: non-class changes: %d held-tool files, %d Legs JSON (+ Overpants from the game update), manifest" % (held, legs))
        return self.check(not bad and held > 50, "C: every non-class change is a held-tool file or a Legs + Overpants JSON (others: %s)" % bad[:6])
    return _eq0(self, got, want, what)


HK.Child.eq = _eq41
HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("repro", run_repro), ("exec", run_exec), ("wire", run_wire), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
