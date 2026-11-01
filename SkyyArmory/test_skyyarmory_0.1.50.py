"""Harness for SkyyArmory 0.1.50 (round sig3a = the Armory half of research/UT-Mythic-Signatures.md 'sig3'; tools/armory_0_1_50_patch.py).
Build first:
    python tools/armory_0_1_50_patch.py && python SkyyArmory/build_skyyarmory_0.1.50.py
    python SkyyArmory/test_skyyarmory_0.1.50.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  S   static   the patch re-runs to identical bytes, line endings kept; 4 new classes, no new system / command; the jar vs 0.1.49: added = the 4
               classes + Doomcaller's item / texture / icon, nothing removed, changed non-class = manifest + lang; lang = the 0.1.49 lines
               unchanged + 2 Doomcaller lines (tier tag T6 Dusk first + plain, the Thorium staff's controls + Mana numbers, Style Guide 15
               spans only); Doomcaller's JSON = the jar's Thorium staff + the vanilla Doomed model / its own recoloured art, Variant, Lv 32, no
               recipe; no Weapon_Staff_Doomed file (SkyySkills owns it); the generated art differs from the vanilla pictures
  X   exec     EXECUTED in the JVM: the 21 rows (defaults, the clamps, the default file text); kindOf / live / full / fell; the W state machine
               (observe: baseline, full -> fall = window x1.35, slow fall / swap = none, the watch probe on any weapon = window x1, the fall the
               swing sees first); swing (window hits, A release Seven Cuts / Grave Chill, not full, another item, armed, A off); the A read-back
               (stayed empty -> PASS, refilled -> FAIL); the verdicts + report lines + the log on PASS / FAIL; armory:fn:sigfx (every argument
               shape -> Boolean / String, off, bad, queue cap, owns, watch / unwatch, reset); drain / run1 (window, stale, too late, Seven Cuts
               with / without a hit, from the last swing, Grave Chill armed then released, probe, another player's request kept, the old one
               dropped); the Seven Cuts job (due / stepped through 7 chops, the timeout, run drops it when the holder is gone, TravWorld.idle);
               armory:fn:sig per item (Second Opinion, Revolving Door, Weighted Vortex, Seven Cuts, Grave Chill, Doomcaller = Arcane Overload)
               incl. the row-driven texts <= 70 and every switch off -> the old answer; Rico (soOn / soPrefer / soHealAmt, RicoChain.ally);
               Sig2 (doorItem / doorOn / doorGap / pullSpeed, Sig2Job.mode); the engine glue with no engine (quiet); SkyyGear 0.3.53's
               GearSigX.sigOf through the bridge (when its jar is present); Doomcaller through ArmoryDefs (utBase / staffIndex)
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.49 -> 0.1.50: exactly the planned members (EXPECT) + the 4 new classes
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory (every migration + load): 0.1.50 writes nothing; start 2 = start 1;
               the 21 new keys read their defaults
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the meter falling on a real Vortexstrike and its hits carrying DamageSequence, Hepta Axe's
inherited meter filling and staying empty after our write, the Ghost Sword HUD meter from our modifier, the vanilla Freeze on a mob, the pull
velocity's real distance, the ally hop heal on a real player, the Doomcaller model / recolour in the client.
"""
import os, sys, json, subprocess, zipfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sig3a", "arm")]
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

VERSION, OLD = "0.1.50", "0.1.49"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyarmory_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyarmory_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "armory_0_1_50_patch.py")
GEAR_JAR = os.path.join(ROOT, "SkyyGear", "SkyyGear-0.3.53.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
LANG = "Server/Languages/en-US/server.lang"
DC = "Weapon_Staff_UT_Doomcaller"
PW, HEPTA, GHOST, SO, TS = "Weapon_Sword_UT_Paperweight", "Hepta_Axe", "GhostSword", "Weapon_Wand_UT_SecondOpinion", "Weapon_Bo_UT_Turnstile"
DC_FILES = ["Server/Item/Items/SkyyArmory/UT/%s.json" % DC, "Common/Items/SkyyArmory/UT/%s.png" % DC, "Common/Icons/ItemsGenerated/%s.png" % DC]
NEW_CLASSES = ["ArmorySig3", "ArmorySigFx", "Sig3Job", "Sig3Rec"]
Y_, G_, R_ = '<color is="#ffcc00">%s</color>', '<color is="#7ee08a">%s</color>', '<color is="#ff7a7a">%s</color>'
_SG3F = ["+f SG3_" + k for k in ("A_ON", "FX_ON", "GC_DMG", "GC_FRZ", "GC_GAIN", "GC_MAX", "RD_FLING", "RD_HITS", "RD_ON", "RD_PULL", "RD_TO", "SC_ARC",
                                  "SC_DMG", "SC_GAP", "SC_N", "SC_R", "SO_HEAL", "SO_ON", "WV_DMG", "W_ON", "W_WIN")]
EXPECT = {
    "ArmoryCfg": _SG3F + ["+m applySig3", "~<clinit>", "~m load", "~m reloadAll", "~m useDefaults", "~m apply"],
    "ArmoryCheck": ["~m packCheck", "~m packOf"],
    "ArmoryCmd": ["~c "],
    "ArmoryDbgCmd": ["~c "],
    "ArmoryDefs": ["~<clinit>"],
    "ArmoryHitSys": ["~m handle"],
    "ArmoryQuit": ["~m accept"],
    "ArmorySig2": ["+f DOOR_ID", "+f PULL_MAX", "+f PULL_S", "+f PULL_UP", "+f RD_CASTS", "+f RD_D0", "+f RD_D1", "+f RD_FLINGS", "+f RD_MEASURED",
                   "+f RD_PULLS", "+m door", "+m doorCount", "+m doorGap", "+m doorItem", "+m doorOn", "+m measure", "+m pull", "+m pullSpeed", "~<clinit>", "~m marker", "~m step"],
    "ArmorySigFn": ["~m sigOf"],
    "ArmoryTuneSys": ["~m handle"],
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],          # the kit: 21 new rows
    "Monk": ["+m sigCmd", "~m debugCmd", "~m help"],
    "Rico": ["+f SO_HEALED", "+f SO_HOPS", "+f SO_ID", "+f SO_XP", "+m room", "+m soAlly", "+m soHeal", "+m soHealAmt", "+m soOn", "+m soPrefer", "+m soXp",
             "~<clinit>", "~m marker", "~m step"],
    "RicoChain": ["+f ally", "+f heals"],
    "Sig2Job": ["+f mode", "+f pd0", "+f pulled"],
    "SkyyArmoryPlugin": ["~m publish", "~m setup", "~m shutdown", "~m start", "~m unpublish"],
    "TravTick": ["~m tick"],
    "TravWorld": ["+f sig3", "~c ", "~m idle", "~m run"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
MIGS = ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021", "migrate035", "migrate036", "migrate040",
        "migrateP5")
SIG3_KEYS = {"sig.so.enabled": "true", "sig.so.heal": "40", "sig.rd.enabled": "true", "sig.rd.hits": "3", "sig.rd.pull": "4", "sig.rd.to": "1.5",
             "sig.rd.fling": "2", "sig.w.enabled": "true", "sig.w.window": "1.5", "sig.wv.damage": "35", "sig.a.enabled": "true", "sig.sc.cuts": "7",
             "sig.sc.gap": "0.15", "sig.sc.damage": "0.35", "sig.sc.range": "3", "sig.sc.arc": "120", "sig.gc.damage": "1.5", "sig.gc.freeze": "1",
             "sig.gc.meter": "20", "sig.gc.charge": "1", "sig.fx.bridge": "true"}
strip = lambda t: re.sub(r"</?color[^>]*>", "", t)


def lang_of(jar):
    with zipfile.ZipFile(jar) as z:
        return z.read(LANG).decode("utf-8")


_ORIG_COMPARE = HK.run_compare


def compare_with_assets(out, jar, old_jar, pkg, expect, added, removed=()):
    _ORIG_COMPARE(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    ed = sorted(n for n in ea | eb if n not in ea or n not in eb or za.read(n) != zb.read(n))
    kept = [f for f in d["fails"] if not f.startswith("C: non-class entries changed")]
    if ed == sorted(["manifest.json", LANG] + DC_FILES):
        d["ok"] += 1
    else:
        kept.append("C: non-class entries changed = manifest + lang + Doomcaller's 3 files: got %s" % ed[:10])
    d["fails"] = kept
    d["notes"].append("C: non-class entries changed = manifest + lang + Doomcaller (the kit's manifest-only check replaced)")
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = compare_with_assets


# ---------------------------------------------------------------------------------------------------------------- S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyArmory 0.1.50 - build script') and g.count('VERSION = "0.1.50"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count("makeClass(") - o.count("makeClass(")),
         (0, 0, 4), "S no new system / command; 4 new classes")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), (sorted(["com/skyy/armory/%s.class" % c for c in NEW_CLASSES] + DC_FILES), []),
         "S added = the 4 classes + Doomcaller's item / texture / icon; nothing removed")
    nc = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    K.eq(nc, sorted(["manifest.json", LANG]), "S changed non-class = manifest + lang (every other item / art / interaction file byte-identical)")
    ma, mb = json.loads(za.read("manifest.json")), json.loads(zb.read("manifest.json"))
    K.check(mb["Version"] == VERSION and dict(ma, Version=VERSION, Name=ma["Name"].replace(OLD, VERSION)) == mb, "S manifest: only the Version (+ the version in Name) changed")
    la, lb = lang_of(OLD_JAR).rstrip("\n").split("\n"), lang_of(jar).rstrip("\n").split("\n")
    K.eq(lb[:len(la)], la, "S lang: every 0.1.49 line unchanged and in order")
    new = lb[len(la):]
    K.eq([x.split(" = ", 1)[0] for x in new], ["items.%s.name" % DC, "items.%s.description" % DC], "S lang: + exactly Doomcaller's name + description")
    K.check(len(set(x.split(" = ", 1)[0] for x in lb if " = " in x)) == len([x for x in lb if " = " in x]), "S lang: each key once")
    L = dict(x.split(" = ", 1) for x in lb if " = " in x)
    nm, ds = L["items.%s.name" % DC], L["items.%s.description" % DC]
    th = strip(L["items.Weapon_Staff_Thorium.description"])
    K.eq(nm, "Doomcaller", "S Doomcaller name (tools/ut_vanilla.py)")
    K.eq(strip(ds), "T6 Dusk - Untiered staff. " + th[len("T4 Thorium - "):], "S the description = T6 Dusk + 'Untiered staff.' + the Thorium staff's controls and Mana numbers (plain text)")
    K.check(ds.startswith(TT.tag_for(DC) + TT.SEP) and TT.tag_for(DC) == "T6 Dusk", "S the tier tag (tools/tier_tags.py: T6 Dusk) first and plain")
    sp = re.findall(r'<color is="(#[0-9a-f]{6})">([^<]*)</color>', ds)
    K.check(ds.isascii() and set(c for c, _w in sp) == {"#ffcc00", "#ff7a7a"} and ds.count("<color ") == ds.count("</color>") == len(sp)
            and Y_ % "Tap:" in ds and R_ % "10" + " Mana" in ds and Y_ % "Hold 1 s:" in ds and R_ % "50" + " Mana" in ds,
            "S the description's spans: actions yellow, the Mana costs red (Style Guide 15): %s" % ds)
    dj = json.loads(zb.read(DC_FILES[0]).decode("utf-8"))
    tj = [json.loads(zb.read(n).decode("utf-8")) for n in nb if n.endswith("/Weapon_Staff_Thorium.json")]
    K.eq(len(tj), 1, "S one Thorium staff file in the jar")
    tj = tj[0]
    vz = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))          # read-only
    vd = json.loads(vz.read("Server/Item/Items/Weapon/Staff/Weapon_Staff_Doomed.json").decode("utf-8-sig"))
    K.eq((dj["Model"], dj["Texture"], dj["Icon"], dj["Variant"], dj["ItemLevel"], "Recipe" in dj, dj["TranslationProperties"]),
         (vd["Model"], "Items/SkyyArmory/UT/%s.png" % DC, "Icons/ItemsGenerated/%s.png" % DC, True, 32, False,
          {"Name": "server.items.%s.name" % DC, "Description": "server.items.%s.description" % DC}),
         "S Doomcaller: the vanilla Doomed model by path, our recoloured art, Variant, Lv 32 (Zone 2), no recipe, our lang keys")
    keep = dict((k, v) for k, v in tj.items() if k not in ("Model", "Texture", "Icon", "Variant", "ItemLevel", "Recipe", "TranslationProperties", "IconProperties", "Scale", "Particles"))
    K.eq(dict((k, dj.get(k)) for k in keep), keep, "S Doomcaller = the jar's Thorium staff (Interactions / Ability 1 / meter / ready glow / Quality / chains) - only the look and texts differ")
    K.eq(dj.get("IconProperties"), vd.get("IconProperties"), "S Doomcaller keeps the vanilla Doomed icon framing")
    K.check(zb.read(DC_FILES[1]) != vz.read("Common/" + vd["Texture"]) and zb.read(DC_FILES[2]) != vz.read("Common/" + vd["Icon"]),
            "S the texture + icon are generated (the orange recolour), not the vanilla files")
    K.check(not [n for n in nb if os.path.basename(n) == "Weapon_Staff_Doomed.json"], "S no Weapon_Staff_Doomed file (SkyySkills ships its own with the class Mana cost)")
    K.check(re.search(r"0\.1\.50 Untiered \(sig3a\)", g) is not None and "import ut_vanilla as UTV" in g, "S Doomcaller comes from tools/ut_vanilla.py")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- X: executed
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray, JObject, JInt, JDouble, JBoolean, JLong, JFloat
    K = HK.Child(out)
    cp = [B.SERVER_JAR, B.JAVASSIST, jar] + ([GEAR_JAR] if os.path.isfile(GEAR_JAR) else [])
    HK.jvm(cp, verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, Defs, S2, S3, S4, Rico = (JClass(PKG + n) for n in ("ArmoryCfg", "ArmoryDefs", "ArmorySig2", "ArmorySig3", "ArmorySig4", "Rico"))
    Rec, Job, Fx, Fn, TW, RC, J2 = (JClass(PKG + n) for n in ("Sig3Rec", "Sig3Job", "ArmorySigFx", "ArmorySigFn", "TravWorld", "RicoChain", "Sig2Job"))
    UUID = JClass("java.util.UUID")
    F_, L_ = JFloat, JLong
    D_ = lambda a: JArray(JDouble)([float(x) for x in a])
    Cfg.useDefaults()
    # ---- the rows
    want = dict(SG3_SO_ON=True, SG3_SO_HEAL=40, SG3_RD_ON=True, SG3_RD_HITS=3, SG3_RD_PULL=4.0, SG3_RD_TO=1.5, SG3_RD_FLING=2.0, SG3_W_ON=True, SG3_W_WIN=1.5,
                SG3_WV_DMG=35, SG3_A_ON=True, SG3_SC_N=7, SG3_SC_GAP=0.15, SG3_SC_DMG=0.35, SG3_SC_R=3.0, SG3_SC_ARC=120, SG3_GC_DMG=1.5, SG3_GC_FRZ=1.0,
                SG3_GC_MAX=20, SG3_GC_GAIN=1.0, SG3_FX_ON=True)
    got = dict((k, (bool(getattr(Cfg, k)) if isinstance(v, bool) else (int(getattr(Cfg, k)) if isinstance(v, int) else round(float(getattr(Cfg, k)), 6)))) for k, v in want.items())
    K.eq(got, want, "X useDefaults -> applySig3: the 21 defaults")
    dc = str(Cfg.DEF_CFG)
    K.eq([k for k, v in SIG3_KEYS.items() if ("\n%s=%s\n" % (k, v)) not in dc], [], "X the default config.properties text carries the 21 new keys at their defaults")
    Pr = JClass("java.util.Properties")
    pp = Pr()
    for k_, v_ in (("sig.rd.hits", "99"), ("sig.sc.gap", "0.001"), ("sig.wv.damage", "-5"), ("sig.gc.freeze", "abc"), ("sig.a.enabled", "off"), ("sig.so.heal", "100")):
        pp.setProperty(k_, v_)
    Cfg.applySig3(pp)
    K.eq((int(Cfg.SG3_RD_HITS), round(float(Cfg.SG3_SC_GAP), 4), int(Cfg.SG3_WV_DMG), float(Cfg.SG3_GC_FRZ), bool(Cfg.SG3_A_ON), int(Cfg.SG3_SO_HEAL), int(Cfg.SG3_SC_N)),
         (10, 0.05, 0, 1.0, False, 100, 7), "X applySig3 clamps like the kit (max / min / bad text = default; a missing key = its default)")
    Cfg.useDefaults()
    # ---- kinds
    K.eq([int(S3.kindOf(JString(i))) for i in (PW, HEPTA, GHOST, "Weapon_Sword_Iron", SO, "")] + [int(S3.kindOf(None))], [1, 2, 3, 0, 0, 0, 0],
         "X kindOf: The Paperweight = W, Hepta Axe = A (its meter), Ghost Sword = A (our meter), others none")
    Cfg.SG3_W_ON, Cfg.SG3_A_ON = False, False
    off = [int(S3.live(k)) for k in (1, 2, 3)]
    Cfg.useDefaults()
    K.eq((off, [int(S3.live(k)) for k in (0, 1, 2, 3, 9)]), ([0, 0, 0], [0, 1, 2, 3, 0]), "X live: sig.w.enabled / sig.a.enabled off = not watched")
    K.eq([bool(S3.full(F_(a), F_(b))) for a, b in ((20, 20), (19.995, 20), (19, 20), (0, 0), (9, 9))], [True, True, False, False, True], "X full")
    K.eq([bool(S3.fell(F_(a), F_(b), F_(c), L_(t))) for a, b, c, t in ((20, 20, 0, 33), (20, 20, 2, 33), (20, 20, 2.5, 33), (19, 20, 0, 33), (20, 20, 0, 1001), (20, 0, 0, 33), (9, 9, 0, 0))],
         [True, True, False, False, False, False, True], "X fell: full -> <= 10 % within 1 s (not from below full, not slow, not without a meter)")
    # ---- the W state machine
    S3.reset()
    r = Rec(JString(PW), F_(0), F_(20), L_(1000))
    seq = [int(S3.observe(r, JString(PW), F_(10), F_(20), 1, False, L_(1033))), int(S3.observe(r, JString(PW), F_(20), F_(20), 1, False, L_(1066))),
           int(S3.observe(r, JString(PW), F_(0), F_(20), 1, False, L_(1100)))]
    K.eq((seq, int(S3.W_FALLS), int(r.winUntil), round(float(r.winMult), 4), str(r.winItem)), ([0, 0, 2], 1, 2600, 1.35, PW),
         "X W: The Paperweight's meter full -> empty within one tick = Vortexstrike fired: a 1.5 s window x1.35")
    hit1 = int(S3.swing(r, JString(PW), F_(0), F_(20), 1, L_(1200)))
    hit2 = int(S3.swing(r, JString(PW), F_(0), F_(20), 1, L_(2599)))
    late = int(S3.swing(r, JString(PW), F_(0), F_(20), 1, L_(2600)))
    K.eq((hit1, hit2, late, int(S3.W_HITS), int(S3.W_SCALED), str(S3.wVerdict(S3.W_FALLS, S3.W_HITS, S3.W_EMPTY))), (1, 1, 0, 2, 2, "PASS"),
         "X W: swings inside the window are signature hits (x1.35), the first one after it is not; the probe = PASS")
    K.eq((int(S3.W_FAST), int(S3.W_FIRST_MS)), (1, 100), "X FIX W timing: the window's first hit 0.1 s after the fall = an ability hit (counted once per window)")
    l0 = str(S3.line(0))
    K.check("first hit after the fall: last 0.1 s" in l0 and "within 0.5 s: 1" in l0 and "CHECK" not in l0, "X FIX W timing in the probe line: %s" % l0)
    K.eq(str(S3.wFirst(0, 0, -1)), "", "X FIX wFirst: no hits = nothing")
    K.check("CHECK: no hit came right after the fall" in str(S3.wFirst(2, 0, 900)), "X FIX wFirst: only late first hits (0.9 s) = PASS with a CHECK note (maybe plain swings)")
    S3.observe(r, JString(PW), F_(20), F_(20), 1, False, L_(3000))
    slow = int(S3.observe(r, JString(PW), F_(0), F_(20), 1, False, L_(4100)))
    S3.observe(r, JString(PW), F_(20), F_(20), 1, False, L_(4200))
    swap = int(S3.observe(r, JString("Weapon_Sword_Iron"), F_(0), F_(20), 0, False, L_(4233)))
    K.eq((slow, swap, int(S3.W_FALLS), str(r.item)), (0, 1, 1, "Weapon_Sword_Iron"), "X W: a slow drop (over 1 s) is no fire; a swap only re-baselines (no fire)")
    d = Rec(JString("Weapon_Sword_Iron"), F_(20), F_(20), L_(5000))
    dw = int(S3.observe(d, JString("Weapon_Sword_Iron"), F_(0), F_(20), 0, True, L_(5030)))
    dh = int(S3.swing(d, JString("Weapon_Sword_Iron"), F_(0), F_(20), 0, L_(5100)))
    K.eq((dw, round(float(d.winMult), 4), dh, int(S3.W_FALLS), int(S3.W_SCALED)), (2, 1.0, 1, 2, 2),
         "X W watch probe (/armory debug sig watch): any weapon's fall opens a x1 window - hits counted, never scaled")
    e = Rec(JString(PW), F_(20), F_(20), L_(6000))
    first = int(S3.swing(e, JString(PW), F_(0), F_(20), 1, L_(6020)))
    K.eq((first, int(S3.W_FALLS), int(e.winUntil)), (1, 3, 7520), "X W: the first spin hit that lands before the player's tick sees the fall opens the window itself")
    # ---- the A path
    h = Rec(JString(HEPTA), F_(0), F_(9), L_(0))
    S3.observe(h, JString(HEPTA), F_(9), F_(9), 2, False, L_(33))
    rel = int(S3.swing(h, JString(HEPTA), F_(9), F_(9), 2, L_(50)))
    K.eq((int(S3.A_FULL[0]), rel, int(S3.A_REL[0]), int(h.checkAt), str(S3.aVerdict(S3.A_FULL[0], S3.A_REL[0], S3.A_EMPTY[0], S3.A_REFILL[0]))), (1, 2, 1, 300, "WAITING"),
         "X A Hepta Axe: meter full seen, the next landed swing releases Seven Cuts, the read-back is due 250 ms later (WAITING)")
    early = int(S3.observe(h, JString(HEPTA), F_(0), F_(9), 2, False, L_(200)))
    back = int(S3.observe(h, JString(HEPTA), F_(0), F_(9), 2, False, L_(320)))
    K.eq((early, back, int(S3.A_EMPTY[0]), int(S3.A_REFILL[0]), str(S3.aVerdict(S3.A_FULL[0], S3.A_REL[0], S3.A_EMPTY[0], S3.A_REFILL[0]))), (0, 3, 1, 0, "PASS"),
         "X A Hepta Axe: the meter stayed empty after our write -> PASS")
    g_ = Rec(JString(GHOST), F_(20), F_(20), L_(0))
    rg = int(S3.swing(g_, JString(GHOST), F_(20), F_(20), 3, L_(10)))
    S3.observe(g_, JString(GHOST), F_(20), F_(20), 3, False, L_(300))
    K.eq((rg, int(S3.A_REL[1]), int(S3.A_REFILL[1]), str(S3.aVerdict(S3.A_FULL[1], S3.A_REL[1], S3.A_EMPTY[1], S3.A_REFILL[1]))), (3, 1, 1, "FAIL"),
         "X A Ghost Sword: Grave Chill released; a meter the engine refilled = FAIL")
    nf = int(S3.swing(h, JString(HEPTA), F_(5), F_(9), 2, L_(400)))
    oth = int(S3.swing(h, JString("Weapon_Battleaxe_Iron"), F_(9), F_(9), 0, L_(410)))
    h.armUntil = 5000
    arm = int(S3.swing(h, JString(HEPTA), F_(1), F_(9), 2, L_(420)))
    arm2 = int(S3.swing(h, JString(HEPTA), F_(1), F_(9), 2, L_(430)))
    K.eq((nf, oth, arm, arm2, int(h.armUntil)), (0, 0, 4, 0, 0), "X swing: not full = nothing, another item = nothing, a bridge-armed Grave Chill fires once")
    K.eq([str(S3.aVerdict(*a)) for a in ((0, 0, 0, 0), (1, 0, 0, 0), (1, 1, 0, 0), (1, 1, 1, 0), (1, 1, 1, 1))], ["NOT RUN", "WAITING", "WAITING", "PASS", "FAIL"], "X aVerdict table")
    K.eq([str(S3.wVerdict(a, b, c)) for a, b, c in ((0, 0, 0), (1, 0, 0), (1, 0, 1), (1, 1, 1))], ["NOT RUN", "WAITING", "FAIL", "PASS"],
         "X wVerdict: a fall waits for its hits; FAIL only after a whole window with no hit")
    K.eq([str(x) for x in S3.LASTV], ["PASS", "PASS", "FAIL"], "X verdicts(): each probe's last verdict kept (a PASS / FAIL change logs one INFO line)")
    rep = str(S3.text(JString("status"))).split("\n")
    K.check(len(rep) == 5 and rep[0].startswith("W fired window") and ": PASS - " in rep[0] and rep[1].startswith("A auto-release Hepta_Axe (Seven Cuts): PASS")
            and rep[2].startswith("A auto-release GhostSword (Grave Chill): FAIL") and rep[3].startswith("Revolving Door (The Turnstile)") and rep[4].startswith("armory:fn:sigfx"),
            "X the probe report (5 lines): %s" % rep)
    K.notes.append("X probe report: %s" % rep)
    K.eq(str(S3.text(JString("reset"))), "sig3 probe counters reset", "X reset")
    K.eq((int(S3.W_FALLS), int(S3.A_REL[0]), int(S3.A_REFILL[1]), [str(x) for x in S3.LASTV]), (0, 0, 0, ["", "", ""]), "X reset zeroes every counter")
    K.check(": NOT RUN - " in str(S3.line(0)) and ": NOT RUN - " in str(S3.line(1)), "X after a reset the probes say NOT RUN")
    S3.reset()
    q = Rec(JString(PW), F_(20), F_(20), L_(100))
    S3.observe(q, JString(PW), F_(0), F_(20), 1, False, L_(130))
    mid = str(S3.line(0))
    S3.observe(q, JString(PW), F_(0), F_(20), 1, False, L_(1700))
    K.check(": WAITING - " in mid and ": FAIL - " in str(S3.line(0)) and int(S3.W_EMPTY) == 1 and int(q.winUntil) == 0,
            "X W: WAITING right after the fall (no false FAIL in the log), FAIL once the 1.5 s window ended with no swing hit")
    S3.reset()
    # ---- armory:fn:sigfx
    fx = Fx()
    u = UUID.randomUUID()
    u2 = UUID.randomUUID()
    S3.REQ.clear()

    def call(*a):
        arr = JArray(JObject)(len(a))
        for i_, x in enumerate(a):
            arr[i_] = x
        return fx.apply(arr)
    S3.CLOCK = 10000
    r1 = call(u, JString("weightedVortex"), JString(PW), JObject(20, JInt))
    r2 = call(JString(str(u)), JString("probe"), JString(PW), JObject(20, JInt))
    r3 = call(u, JString("nope"), JString(PW), JObject(1, JInt))
    r4 = call(u, JString("probe"))
    r5 = fx.apply(JObject(5, JInt))
    r6 = call(None, JString("probe"), JString(PW), JObject(1, JInt))
    r7 = call(JString("not-a-uuid"), JString("probe"), JString(PW), JObject(1, JInt))
    K.eq([str(x.getClass().getName()) for x in (r1, r2, r3, r4, r5, r6, r7)], ["java.lang.Boolean"] * 7, "X armory:fn:sigfx Object[] answers are java.lang.Boolean")
    K.eq([bool(x) for x in (r1, r2, r3, r4, r5, r6, r7)], [True, True, False, False, False, False, False],
         "X armory:fn:sigfx: UUID / String uuid queued; unknown effect, too short, not an array, no / bad uuid refused")
    K.eq(int(S3.REQ.size()), 2, "X two requests queued")
    Cfg.SG3_FX_ON = False
    K.check(not bool(call(u, JString("probe"), JString(PW), JObject(1, JInt))), "X sig.fx.bridge off = refused")
    Cfg.SG3_FX_ON = True
    st_txt = fx.apply(JString("status"))
    K.check(isinstance(st_txt, str) and st_txt.startswith("W fired window"), "X apply(\"status\") = the report (a java.lang.String)")
    K.eq([str(fx.apply(JString("owns:" + i))) for i in (PW, HEPTA, GHOST, "Weapon_Sword_Iron", SO)], ["W", "A", "A", "", ""], "X apply(\"owns:<id>\") (SkyyGear must not double these)")
    w_ = str(fx.apply(JString("watch:" + str(u))))
    inw = bool(S3.DBG.containsKey(u))
    uw = str(fx.apply(JString("unwatch:" + str(u))))
    K.check(w_.startswith("sig3 watch ON") and inw and uw == "sig3 watch off." and not bool(S3.DBG.containsKey(u)) and str(fx.apply(JString("watch:x"))) == "no player",
            "X watch / unwatch:<uuid> toggles the any-weapon W probe for that player")
    # ---- drain / run1 (the player's tick)
    st = JClass("java.lang.Object")()
    n1 = int(S3.drain(u, JString(PW), st, None, L_(10100)))
    rr = S3.REC.get(u)
    K.eq((n1, int(S3.REQ.size()), int(S3.FX_RUN), int(S3.FX_PROBES), str(rr.item), int(rr.winUntil), round(float(rr.winMult), 4), int(rr.keepUntil)),
         (2, 0, 2, 1, PW, 11600, 1.35, 15100), "X drain: the player's 2 requests run on their tick (window opened x1.35 for 1.5 s, probe counted; the record kept 5 s)")
    call(u, JString("weightedVortex"), JString(PW), JObject(1, JInt))
    call(u2, JString("probe"), JString(PW), JObject(1, JInt))
    stale0 = int(S3.FX_STALE)
    n2 = int(S3.drain(u, JString("Weapon_Sword_Iron"), st, None, L_(10200)))
    K.eq((n2, int(S3.FX_STALE) - stale0, int(S3.REQ.size())), (1, 1, 1), "X drain: another item in the hand = too late (dropped); another player's request stays queued")
    S3.CLOCK = 20000
    call(u, JString("weightedVortex"), JString(PW), JObject(1, JInt))
    n3 = int(S3.drain(u, JString(PW), st, None, L_(23001)))
    K.eq((n3, int(S3.FX_STALE) - stale0, int(S3.REQ.size())), (1, 3, 0), "X drain: a request over 3 s old is too late; the other player's 13 s old request is dropped (never ticks)")
    tw = TW.get(st)
    tw.sig3.clear()
    S3.CLOCK = 30000
    call(u, JString("sevenCuts"), JString(HEPTA), JObject(60, JInt), JObject(40.0, JDouble))
    S3.drain(u, JString(HEPTA), st, None, L_(30010))
    j0 = tw.sig3.get(0) if tw.sig3.size() == 1 else None
    K.check(j0 is not None and (float(j0.base), round(float(j0.mult), 4), int(j0.left), int(j0.gap), int(j0.next)) == (40.0, 0.35, 7, 150, 30160),
            "X sevenCuts with a hit (40): a Seven Cuts job of 7 chops x0.35, 0.15 s apart, the first 0.15 s later")
    ref0 = int(S3.FX_REFUSED)
    nohit = bool(call(u, JString("sevenCuts"), JString(HEPTA), JObject(60, JInt)))
    K.check(not nohit and int(S3.REQ.size()) == 0, "X FIX sevenCuts with no hit and no recent watched swing = FALSE at once (the caller passes the hit)")
    S3.REC.remove(u)
    S3.drain(u, JString(HEPTA), st, None, L_(30020))
    K.eq((int(S3.FX_REFUSED) - ref0, int(tw.sig3.size())), (1, 1), "X sevenCuts with no hit and no recent swing = refused")
    S3.REC.remove(u)
    gm = S3.rec(u, JString(GHOST), L_(30025))
    gm.mod = True
    rh = S3.rec(u, JString(HEPTA), L_(30030))
    K.check(bool(rh.mod) and str(rh.item) == HEPTA and S3.rec(u, JString(HEPTA), L_(30031)) == rh,
            "X FIX rec(): a new record for another item keeps mod = TRUE (our Ghost Sword modifier still gets removed next tick)")
    rh.mod = False
    rh.lastBase, rh.lastAt = 30.0, 30030
    call(u, JString("sevenCuts"), JString(HEPTA), JObject(60, JInt))
    S3.drain(u, JString(HEPTA), st, None, L_(30040))
    K.eq((int(tw.sig3.size()), float(tw.sig3.get(1).base)), (2, 30.0), "X sevenCuts with no hit: the holder's last landed swing (within 5 s) is the base")
    call(u, JString("graveChill"), JString(GHOST), JObject(20, JInt))
    S3.drain(u, JString(GHOST), st, None, L_(30050))
    rgc = S3.REC.get(u)
    a1 = int(S3.swing(rgc, JString(GHOST), F_(0), F_(0), 0, L_(30060)))
    K.eq((int(rgc.armUntil), a1), (0, 4), "X graveChill: arms the next landed swing (it fires once)")
    K.check(not bool(tw.idle()), "X TravWorld.idle() sees the Seven Cuts jobs (TravTick keeps the world)")
    for i in range(int(S3.MAX_REQ) - int(S3.REQ.size())):
        call(u2, JString("probe"), JString(PW), JObject(1, JInt))
    K.check(not bool(call(u2, JString("probe"), JString(PW), JObject(1, JInt))) and int(S3.REQ.size()) == 256, "X the queue holds at most 256")
    S3.REQ.clear()
    S3.CLOCK = 0
    # ---- the job
    jb = Job(u, JString(HEPTA), 40.0, 0.35, 7, L_(150), D_([1, 0, 0]), L_(1150))
    seqj, t = [], 1000
    while t < 4000:
        dv = int(S3.due(jb, L_(t)))
        if dv < 0:
            break
        if dv == 1:
            seqj.append(t)
            S3.stepped(jb, L_(t))
        t += 25
    K.eq((seqj, int(jb.done), int(jb.left), int(S3.due(jb, L_(t)))), ([1150, 1300, 1450, 1600, 1750, 1900, 2050], 7, 0, -1), "X Seven Cuts: 7 chops 0.15 s apart, then it ends")
    jt = Job(u, JString(HEPTA), 40.0, 0.35, 7, L_(150), D_([1, 0, 0]), L_(1150))
    K.eq([int(S3.due(jt, L_(x))) for x in (1100, 1150, 21000, 21001)] + [int(S3.due(None, L_(1)))], [0, 1, 1, -1, -1], "X due: wait, due, the 20 s timeout, no job")
    S3.run(tw, None, None, L_(99999))
    K.eq((int(tw.sig3.size()), bool(tw.idle())), (0, True), "X run: due jobs whose holder is gone are dropped (no engine); the world is idle again")
    K.check(not bool(S3.cuts(None, u, JString(HEPTA), 10.0, None, L_(1))) and not bool(S3.cuts(st, u, JString(HEPTA), 0.0, None, L_(1))), "X cuts: no world / no hit = no job")
    TW.ALL.remove(st)
    # ---- armory:fn:sig per item
    f = Fn()

    def ask(i):
        a = JArray(JObject)(1)
        a[0] = JString(i)
        r_ = f.apply(a)
        return None if r_ is None else (str(r_[0]), str(r_[1]), int(r_[2]), str(r_[3]), bool(r_[4]), ["java.lang.String" if isinstance(r_[k], str) else str(r_[k].getClass().getName()) for k in range(5)])
    T5 = ["java.lang.String", "java.lang.String", "java.lang.Integer", "java.lang.String", "java.lang.Boolean"]
    wantA = {SO: ("Second Opinion", "Ricochet also hops through allies, healing each 40% of a hit.", 20, "quick hit +1~, charged hit +2", True, T5),
             TS: ("Revolving Door", "Whirling Staff pulls foes in 4 blocks, then flings them out.", 20, "hit +2~", True, T5),
             PW: ("Weighted Vortex", "Vortexstrike hits 35% harder.", 20, "swing +1~, thrust +3~", True, T5),
             HEPTA: ("Seven Cuts", "Full meter: your next swing chops 7 times, 0.35x each, in front.", 9, "swing +1~, downstrike +2~", True, T5),
             GHOST: ("Grave Chill", "Full meter: your next swing hits 1.5x and freezes the target 1 s.", 20, "swing +1~", True, T5)}
    K.eq(dict((i, ask(i)) for i in wantA), wantA, "X armory:fn:sig: the 5 signatures per item id, plain java.lang types")
    thor = ask("Weapon_Staff_Thorium")
    K.check(thor is not None and ask(DC) == thor and thor[0] == "Arcane Overload", "X Doomcaller answers as its Thorium base (Arcane Overload): %s" % (thor,))
    Cfg.SG3_SO_HEAL, Cfg.SG3_RD_PULL, Cfg.SG3_WV_DMG, Cfg.SG3_SC_N, Cfg.SG3_SC_DMG, Cfg.SG3_GC_DMG, Cfg.SG3_GC_FRZ = 100, 7.75, 200, 12, 0.05, 5.0, 0.0
    longs = [ask(i)[1] for i in wantA]
    K.eq(longs, ["Ricochet also hops through allies, healing each 100% of a hit.", "Whirling Staff pulls foes in 7.75 blocks, then flings them out.",
                 "Vortexstrike hits 200% harder.", "Full meter: your next swing chops 12 times, 0.05x each, in front.", "Full meter: your next swing hits 5x."],
         "X the lines follow the live rows")
    Cfg.SG3_SC_N, Cfg.SG3_SC_DMG, Cfg.SG3_GC_DMG, Cfg.SG3_GC_FRZ = 12, 2.75, 4.75, 2.75
    longest = max([ask(i)[1] for i in wantA] + longs, key=len)
    K.check(len(longest) <= 70, "X every line fits 70 characters at the rows' widest (%d: %s)" % (len(longest), longest))
    Cfg.useDefaults()
    Cfg.SG3_SO_ON, Cfg.SG3_RD_ON, Cfg.SG3_W_ON, Cfg.SG3_A_ON = False, False, False, False
    offs = [ask(i) for i in (SO, TS, PW, HEPTA, GHOST)]
    K.check(offs[0][0] == "Ricochet" and offs[1][0] == "Whirling Staff" and offs[2:] == [None, None, None],
            "X every switch off -> the old answer (Ricochet / Whirling Staff / SkyyGear's own for the rest): %s" % [o and o[0] for o in offs])
    Cfg.useDefaults()
    K.check(ask("Weapon_Wand_Iron")[0] == "Ricochet" and ask("Weapon_Bo_Iron")[0] == "Whirling Staff" and ask("Weapon_Sword_Iron") is None, "X other ids unchanged")
    # ---- Rico (Second Opinion) + Sig2 (Revolving Door)
    K.eq([bool(Rico.soOn(JString(i))) for i in (SO, "Weapon_Wand_Iron", "Weapon_Wand_UT_Cavewind")] + [bool(Rico.soOn(None))], [True, False, False, False], "X Rico.soOn: The Second Opinion only")
    K.eq([bool(Rico.soPrefer(a, b, c)) for a, b, c in ((3, 5, True), (5, 3, True), (5, 5, True), (9, 0, False), (-1, 5, True))], [True, False, False, True, False],
         "X soPrefer: the ally hop only when nearer than the next enemy (or no enemy is left)")
    K.eq([round(float(Rico.soHealAmt(x)), 4) for x in (10, 0, -3)], [4.0, 0.0, 0.0], "X soHealAmt: 40 % of the bounce's hit")
    ch = RC(u, JString(SO), 1, 10.0, 0.0, 0.0, 0.0, D_([1, 0, 0]), L_(1))
    K.eq((bool(ch.ally), int(ch.heals)), (False, 0), "X RicoChain: ally off by default (the marker sets it for The Second Opinion)")
    Cfg.SG3_SO_ON = False
    K.check(not bool(Rico.soOn(JString(SO))), "X sig.so.enabled off = the plain Ricochet")
    Cfg.useDefaults()
    K.eq([bool(S2.doorItem(JString(i))) for i in (TS, "Weapon_Bo_Iron", "Weapon_Bo_UT_CrushingTail")], [True, False, False], "X doorItem: The Turnstile only")
    Cfg.SG2_BO_ON = False
    bo_off = bool(S2.doorOn(JString(TS)))
    Cfg.useDefaults()
    K.eq((bool(S2.doorOn(JString(TS))), bo_off, int(S2.doorGap())), (True, False, 750), "X doorOn (Bo signature off too = off); 3 spins over 1.5 s = 0.75 s apart")
    K.eq([round(float(S2.pullSpeed(dd, 1.5)), 4) for dd in (4.0, 1.5, 1.52, 9.0, 3.0)], [7.1429, 0.0, 0.0, 16.0, 4.2857], "X pullSpeed: closes (d - 1.5) in 0.35 s, capped at 16")
    jd = J2(0, u, JString(TS), 10.0, 0.6, 4, L_(500), D_([1, 0, 0]), False, L_(1))
    K.eq((int(jd.mode), jd.pulled is None, int(S2.measure(jd, None, None))), (0, True, 0), "X Sig2Job.mode 0 by default; measure with nothing pulled = 0")
    K.eq([int(S2.doorCount(*a)) for a in ((0, 0, 2), (0, 1, 2), (0, 0, 0), (1, 0, 2), (2, 3, 0))], [2, 3, 0, 0, 3],
         "X FIX doorCount: a first spin that only pulled (no hit yet) is no miss (no charge back, the fling follows); a spin with nothing = miss")
    # ---- the glue with no engine: quiet
    try:
        S3.tickPlayer(None, None, None, None, None)
        S3.filter(None, None, None, None)
        S3.onHit(None, None, None)
        K.check(not bool(S3.freeze(None, None)) and int(S3.GC_NOFREEZE) == 1, "X freeze(no target) = no freeze, counted")
        K.check(not bool(S3.status(None, None, JString("Freeze"), 1.0)), "X status(no target) = false")
        K.eq(int(S3.ownMeter(None, 0, None, True)), 0, "X ownMeter(no stats) = nothing")
        K.check(Rico.soAlly(None, None, None, 0.0, 0.0, 0.0, None, None, None) is None and float(Rico.soHeal(None, None, u, 10.0)) == 0.0, "X soAlly / soHeal with nothing = nothing")
        Rico.soXp(u, 5.0)
        K.check(S3.lookOf(None, u) is None and S3.prune() >= 0, "X lookOf(no engine) = null; prune")
        S3.REC.put(u, Rec(JString(PW), F_(0), F_(20), L_(1)))
        S3.DBG.put(u, True)
        S3.quit(u)
        K.check(not bool(S3.REC.containsKey(u)) and not bool(S3.DBG.containsKey(u)), "X quit drops the player's record + watch")
        S3.clear()
        K.check(S3.REC.isEmpty() and S3.REQ.isEmpty() and S3.SEEN.isEmpty() and S3.REL.isEmpty(), "X clear")
    except Exception as ex:
        K.check(False, "X the glue edges threw: %s" % str(ex)[:300])
    K.notes.append("X status line: %s" % str(S3.statusText()))
    # ---- Doomcaller through ArmoryDefs
    K.eq((str(Defs.utBase(JString(DC))), int(Defs.staffIndex(JString(DC))) == int(Defs.staffIndex(JString("Weapon_Staff_Thorium"))) >= 0),
         ("Weapon_Staff_Thorium", True), "X Doomcaller answers as the Thorium staff (utBase, staffIndex: its chains, Mana, Arcane Overload)")
    # ---- SkyyGear 0.3.53 reads it (its Ability 1 block) when the jar is on the class path
    try:
        br.put("armory:fn:sig", f)
        GX = JClass("com.skyy.gear.GearSigX")
        outg = [(str(x[0]), str(x[1]), int(x[2]), str(x[3])) for x in (GX.sigOf(JString(i)) for i in (HEPTA, GHOST, PW, SO, TS))]
        K.eq([o[0] for o in outg], ["Seven Cuts", "Grave Chill", "Weighted Vortex", "Second Opinion", "Revolving Door"], "X SkyyGear 0.3.53 GearSigX.sigOf takes the 5 answers through armory:fn:sig")
        K.notes.append("X GearSigX.sigOf: %s" % outg)
        br.remove("armory:fn:sig")
    except Exception as ex:
        K.notes.append("X SkyyGear GearSigX not run (%s)" % str(ex)[:200])
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
    t1 = open(fp, "rb").read()
    K.check(b"0.1.50" not in t1 and (b"\r\n" in b0) == (b"\r\n" in t1), "D 0.1.50 writes nothing of its own; line endings kept")
    K.check(not [k for k in SIG3_KEYS if (k + "=").encode() in b0], "D the live file has none of the new keys (they read their defaults)")
    K.eq((bool(Cfg.SG3_W_ON), bool(Cfg.SG3_A_ON), int(Cfg.SG3_WV_DMG), int(Cfg.SG3_SC_N), bool(Cfg.SG3_FX_ON)), (True, True, 35, 7, True), "D the new rows at their defaults after the live load")
    K.notes.append("D files changed by start 1: %s" % sorted(k for k in set(hashes[0]) | set(hashes[1]) if hashes[0].get(k) != hashes[1].get(k))[:8])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=NEW_CLASSES,
           phases=[("static", run_static), ("exec", run_exec), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyArmory"))
