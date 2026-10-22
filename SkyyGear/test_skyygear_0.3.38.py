"""Harness for SkyyGear 0.3.38 (packprep: the real lock reason through sacks:fn:craftWhy, Farming textures in multiples of 32, pack weapons by
id, no guns - tools/gear_0_3_38_patch.py). Build first:
    python tools/gear_0_3_38_patch.py && python SkyyGear/build_skyygear_0.3.38.py
    python SkyyGear/test_skyygear_0.3.38.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes, line endings kept, no new class / command / system; the three lockWhy callers pass the player;
              the conversion sits in scanSome before the gear test
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.37 -> 0.3.38 (EXPECT below); non-class files: exactly the 28 padded Farming textures + manifest.json
  X  exec     EXECUTES the new paths in a bare JVM:
              X1 GearSmith.whyText: Skyy's Bronze case word for word ("Not unlocked yet - needs the Copper collection V (201 / 500) and Iron V -
                 /collections", card "Locked - Copper V collection"), every alloy pair, a plain metal (no "and"), "know" alone, bench need / have
                 (none / yours), the combat variant, table / unknown / paused / null / junk -> null (0.3.37 text)
              X2 lockWhyU with a stand-in sacks:fn:craftWhy: know -> the collection text; null / no bridge / a throwing bridge -> lockWhy's text
              X3 pack weapons: Voidice sword / staff = gear like Weapon_Sword_Frost / Weapon_Staff_Crystal_Ice (isGear, kindFor combat, isSpell,
                 GearBase.family, typeWord), a Normal legacy document, a Mythic Sigil refused (PACKMY), Fabled allowed; pack.weapons empty = 0.3.37
                 (no gear); chains / a non-Weapon_ target refused; the Voidice repair kit is no tool / gear; Utility_ (the ArmorBench recipes'
                 outputs) are no gear and never refused by the bench veto
              X4 no guns: convTo / convStack / convSlot on a real SimpleItemContainer (the Blunderbuss -> the Ancient Steel crossbow, 64 bullets ->
                 64 crude arrows, counts before / after, other stacks untouched), a missing target = left alone, pack.convert empty = off, guns
                 are never gear
              X5 textures: every PNG of the 0.3.38 jar outside Common/UI/ in multiples of 32; the 28 padded Farming textures = Quirk's originals
                 pixel for pixel (top-left) + transparent padding; the models byte-identical to 0.3.37's; 0.3.37 had exactly those 28 off
              X6 fixer 2: GearPack.family - a pack boss that dies and spawns its next form (Gravedigger -> Beast, Sv2 / Calamity phases) is one
                 family, so firstOfFight gives one Mythic roll per fight
  D  live     every migration TWICE on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear (0.3.38 adds none): the second start changes
              nothing; the live file loads with the pack rows at their defaults (the live file has no pack line)
  AA engine-access audit
Scratch: tools/dev/scratch/packprep/gear (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.38"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "packprep", "gear")]
import skyybuild as B
import harness_kit as HK
import skyyart as SA

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.37.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_38_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.37.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
FARM_ART = os.path.join(os.environ.get("SKYWYNN_PRIVATE_ART") or os.path.join(os.path.dirname(ROOT), "SkyWynn-PRIVATE-art"), "farming-armor")
EXPECT = {"CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"],
          "GearBase": ["~m family"], "GearPack": ["~m family"], "GearCfg": ["+f PACK_CONVERT", "+f PACK_WEAPONS", "~<clinit>", "~m apply", "~m defaultsText"],
          "GearData": ["+<clinit>", "+f PC_MAP", "+f PC_SRC", "+f PW_MAP", "+f PW_SRC", "+m convTo", "+m packAs", "+m pairs", "~m isGear", "~m isGearMs", "~m isSpell", "~m kindFor"],
          "GearSigil": ["+f PACKMY", "~m why"],
          "GearSmith": ["+f ALLOY38", "+m alloyOther", "+m collTier", "+m lockWhyU", "+m pint", "+m plong", "+m whyText", "~<clinit>", "~m craft", "~m state"],
          "GearStamp": ["+f CONV_N", "+m convNote", "+m convSlot", "+m convStack", "~<clinit>", "~m scanSome"],
          "GearView": ["~m typeWord"], "SmithPage": ["~m pieceRow"], "SkyyGearPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
_RC = HK.run_compare


def _farm_pad_names():
    with zipfile.ZipFile(OLD_JAR) as z:
        return sorted(n for n in z.namelist() if n.lower().endswith(".png") and not n.startswith("Common/UI/") and any(d % 32 for d in SA.png_size(z.read(n))))


def _run_compare(out, jar, old_jar, pkg, expect, added, removed):
    """the kit's compare (it allows only manifest.json to change) + the planned asset changes: the 28 padded Farming textures"""
    _RC(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    ch = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    pad = _farm_pad_names()
    plan = sorted(pad + ["manifest.json"])
    fl = [f for f in d["fails"] if f.startswith("C: non-class entries changed:")]
    if fl and ch == plan and na == nb:
        d["fails"].remove(fl[0])
        d["ok"] += 1
        d["notes"].append("C: the non-class changes are the planned ones: %d padded Farming textures + manifest.json" % len(pad))
    elif ch != plan or na != nb:
        d["fails"].append("C: UNPLANNED non-class changes: %s / added %s / removed %s" % ([n for n in ch if n not in plan][:6], sorted(nb - na)[:4], sorted(na - nb)[:4]))
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = _run_compare


def _props(txt):
    from jpype import JClass
    out = {}
    p = JClass("java.util.Properties")()
    p.load(JClass("java.io.StringReader")(txt))
    for k in p.stringPropertyNames():
        out[str(k)] = str(p.getProperty(k))
    return out


def tmod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    old = sys.argv
    sys.argv = [old[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = old
    return m


_saved_run = HK.run
HK.run = lambda *a, **k: None          # the 0.3.36 harness calls HK.run at import - a no-op while it is loaded as a helper (fake_items)
T36 = tmod(os.path.join(HERE, "test_skyygear_0.3.36.py"), "tg0336_for38")
HK.run = _saved_run
HK.run_compare = _run_compare


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.38 - build script') and g.count('VERSION = "0.3.38"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", 'mk("'):
        K.check(g.count(w) == o.count(w), "S no new %s text" % w)
    K.check(g.count("r0(lockWhyU(u, rc, false));") == 1 and g.count("lock = lockWhyU(u, (@CRR@) row[2], true);") == 1 and g.count("@PKG@.GearSmith.lockWhyU(u, rc, false); }") == 1
            and g.count("r0(lockWhy(rc, false));") == 0 and g.count("lock = lockWhy((@CRR@) row[2], true);") == 0, "S the three lockWhy callers pass the player (lockWhyU)")
    sc = g[g.index("public static int[] scanSome("):]
    K.check(sc.index("s = convSlot(pr, c, i, s);") < sc.index("if (!@PKG@.GearData.isGear(sid) && !@PKG@.GearData.isTool(sid)) continue;"), "S the conversion runs before the gear test of the scan")
    K.check(g.count("String pa0 = packAs(id);") == 4 and g.count("@PKG@.GearData.packAs(id); if (pa0 != null) id = pa0;") == 2, "S packAs in isGear / isGearMs / isSpell / kindFor + family / typeWord")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JString, JArray, JObject, JShort
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    Cfg, Gd, Sm, Sg, Gs = JClass(PKG + "GearCfg"), JClass(PKG + "GearData"), JClass(PKG + "GearSmith"), JClass(PKG + "GearSigil"), JClass(PKG + "GearStamp")
    Df, Rl, Gv, Gb, Gp = JClass(PKG + "GearDefs"), JClass(PKG + "GearRoll"), JClass(PKG + "GearView"), JClass(PKG + "GearBase"), JClass(PKG + "GearPack")
    # ---- X1 whyText (fixer: 5th argument = the alloy's other metal's tier from coll:fn:tier, -1 = unknown)
    WT = lambda c, i, cb, sh, ot=-1: Sm.whyText(c, i, cb, sh, ot)
    ids = "SkyyGear_Recipe_Armor_Bronze_Head_Armor_Mining_Bronze_Head"
    want_l = "Not unlocked yet - needs the Copper collection V (201 / 500) and Iron V - /collections"
    K.eq(str(WT("know|Copper|Copper|5|500|201", ids, False, False, 4)), want_l, "X1 Skyy's Bronze case (Iron IV), word for word")
    K.eq(str(WT("know|Copper|Copper Ore|5|500|201", ids, False, False, 4)), want_l, "X1 the real collection name 'Copper Ore' reads 'the Copper collection'")
    K.eq(str(WT("know|Copper|Copper|5|500|201", ids, False, True, 4)), "Locked - Copper V collection", "X1 the card text")
    K.eq(str(WT("know|Copper|Copper|5|500|201", ids, False, False, 5)), "Not unlocked yet - needs the Copper collection V (201 / 500) - /collections",
         "X1 critic 5: Iron V already done -> no 'and Iron V'")
    K.eq(str(WT("know|Copper|Copper|5|500|201", ids, False, False, -1)), "Not unlocked yet - needs the Copper collection V (201 / 500) - /collections",
         "X1 critic 5: Iron's tier unknown (no coll:fn:tier) -> no claim about Iron")
    K.eq(str(WT("know|Copper|Copper Ore|5|500|612", ids, False, False, 4)), "Not unlocked yet - needs the Iron collection V - /collections",
         "X1 critic 5: Copper V done, Iron IV -> names only Iron")
    K.eq(str(WT("know|Copper|Copper Ore|5|500|612", ids, False, True, 4)), "Locked - Iron V collection", "X1 critic 5: ... card names Iron")
    K.eq(str(WT("know|Iron|Iron|5|500|228", ids, True, False, 4)), "Not unlocked yet - needs the Iron collection V (228 / 500) and Copper V - /collections",
         "X1 Iron listed first -> 'and Copper V' (the combat flag does not change a knowledge text)")
    K.eq(str(WT("know|Copper|Copper|3|2500|12345", "Tool_Pickaxe_Copper", False, False, 1)), "Not unlocked yet - needs the Copper collection III (12,345 / 2,500) - /collections",
         "X1 a plain metal recipe: no 'and', thousands separators")
    pairs = [("Dusk", "Thorium", "Lead"), ("Azurvane", "Cobalt", "Chromium"), ("Cinder", "Adamantite", "Slag"), ("Lumen", "Mithril", "Titanium")]
    for al, a, b in pairs:
        t = str(WT("know|%s|%s|5|900|1" % (b, b), "SkyyGear_Recipe_Armor_%s_Chest" % al, False, False, 0))
        K.check(t.endswith("and %s V - /collections" % a), "X1 %s = %s + %s: %s" % (al, a, b, t))
    K.eq(str(WT("know", ids, False, False)), "Not unlocked yet - a collection tier unlocks it - /collections", "X1 'know' alone")
    K.eq(str(WT("know", ids, False, True)), "Locked - collection", "X1 'know' alone, card")
    K.eq(str(WT("bench|Armor_Bench|2|0", ids, False, False)), "Needs the Armor Bench II accessory in your Void Charms (none equipped) - or craft it at a Armor Bench (tier 2).",
         "X1 bench need II, none equipped")
    K.eq(str(WT("bench|Armor_Bench|2|1", ids, False, True)), "Locked - needs Armor Bench II accessory", "X1 bench card text")
    K.check("(yours is Armor Bench I)" in str(WT("bench|Armor_Bench|2|1", ids, False, False)), "X1 bench: what is equipped")
    K.check("combat gear is crafted on this tab only" in str(WT("bench|Weapon_Bench|1|0", "Weapon_Sword_Iron", True, False)), "X1 bench: the combat variant")
    for c in ("table", "unknown", "paused", "bench||1|0", "junk", None, "know|Copper"):
        r = WT(c, ids, False, False) if c != "know|Copper" else WT(c, ids, False, True)
        if c == "know|Copper":
            K.eq(str(r), "Locked - collection", "X1 a cut know answer -> the plain collection text")
        else:
            K.check(r is None, "X1 %r -> null (0.3.37's text)" % c)
    K.eq(str(Sm.alloyOther("x_Bronze_y", "copper")), "Iron", "X1 alloyOther any case")
    K.check(Sm.alloyOther("Armor_Iron_Chest", "Iron") is None and Sm.alloyOther(None, "Iron") is None, "X1 alloyOther: no alloy word -> null")

    # ---- X2 lockWhyU with a stand-in bridge (a bare CraftingRecipe: id only, no output, no bench)
    @JImplements("java.util.function.Function")
    class Cv(object):
        def __init__(self, a, boom=False):
            self.a, self.boom = a, boom

        @JOverride
        def apply(self, x):
            if self.boom:
                raise RuntimeError("boom")
            return self.a
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    US = uf.get(None)
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    rc = US.allocateInstance(CRR.class_)
    fid = CRR.class_.getDeclaredField("id")
    fid.setAccessible(True)
    fid.set(rc, JString("SkyyGear_Recipe_Armor_Bronze_Head"))
    U = JClass("java.util.UUID").fromString("d8ddde89-98b2-4739-983e-a39773d582b6")
    old_l, old_s = str(Sm.lockWhy(rc, False)), str(Sm.lockWhy(rc, True))
    K.eq(str(Sm.lockWhyU(U, rc, False)), old_l, "X2 no bridge (SkyySacks 0.8.27) -> 0.3.37's text: %s" % old_l)
    br.put("sacks:fn:craftWhy", Cv("know|Copper|Copper Ore|5|500|201"))
    K.eq(str(Sm.lockWhyU(U, rc, False)), "Not unlocked yet - needs the Copper collection V (201 / 500) - /collections",
         "X2 know answer, no coll:fn:tier -> no claim about Iron")

    @JImplements("java.util.function.Function")
    class Tier(object):
        def __init__(self, m):
            self.m, self.seen = m, []

        @JOverride
        def apply(self, x):
            self.seen.append((str(x[0]), str(x[1])))
            v = self.m.get(str(x[1]))
            return None if v is None else JClass("java.lang.Integer").valueOf(v)
    tf = Tier({"Iron": 4})
    br.put("coll:fn:tier", tf)
    K.eq(str(Sm.lockWhyU(U, rc, False)), want_l, "X2 the bridge's know answer + Iron IV (coll:fn:tier) -> Skyy's text")
    K.check(tf.seen and tf.seen[-1] == (str(U), "Iron"), "X2 coll:fn:tier asked {player, Iron}: %s" % tf.seen[-1:])
    br.put("coll:fn:tier", Tier({"Iron": 5}))
    K.eq(str(Sm.lockWhyU(U, rc, False)), "Not unlocked yet - needs the Copper collection V (201 / 500) - /collections", "X2 Iron V done -> Copper only")
    br.put("coll:fn:tier", Tier({"Iron": 4}))
    br.put("sacks:fn:craftWhy", Cv("know|Copper|Copper|5|500|201"))
    K.eq(str(Sm.lockWhyU(U, rc, True)), "Locked - Copper V collection", "X2 ... card")
    br.put("sacks:fn:craftWhy", Cv(None))
    K.eq(str(Sm.lockWhyU(U, rc, True)), old_s, "X2 null answer -> 0.3.37's text")
    br.put("sacks:fn:craftWhy", Cv(None, True))
    K.eq(str(Sm.lockWhyU(U, rc, False)), old_l, "X2 a throwing bridge -> 0.3.37's text (one WARN)")
    br.put("sacks:fn:craftWhy", Cv("bench|Armor_Bench|1|0"))
    K.check(str(Sm.lockWhyU(U, rc, False)).startswith("Needs the Armor Bench I accessory in your Void Charms (none equipped)"), "X2 the bridge's bench answer")
    K.eq(str(Sm.lockWhyU(None, rc, False)), old_l, "X2 no player -> 0.3.37's text")
    br.remove("sacks:fn:craftWhy")
    br.remove("coll:fn:tier")

    # ---- X3 pack weapons
    VS, VT, KIT = "Sv2_Weapon_Sword_Voidice", "Sv2_Weapon_Staff_Voidice", "Sv2_Tool_Repair_Kit_Voidice"
    GUN, BUL, XB, AR = "Weapon_Gun_Blunderbuss_Gravedigger", "Weapon_Gun_Blunderbuss_Gravedigger_Bullet", "Weapon_Crossbow_Ancient_Steel", "Weapon_Arrow_Crude"
    SOULS = {"Weapon_Sword_Darkmoon": ("Weapon_Sword_Mithril", "Sword", "SWORD", False), "Weapon_Sword_Farron": ("Weapon_Sword_Iron", "Sword", "SWORD", False),
             "Weapon_Battleaxe_Ogre_Wood_Fence": ("Weapon_Mace_Mithril", "Mace", "MACE", False), "Weapon_Cane_Conductor": ("Weapon_Axe_Mithril", "Axe", "AXE", False),
             "Weapon_Staff_Frenzied": ("Weapon_Axe_Mithril", "Axe", "AXE", False), "Weapon_Spellbook_Bishop": ("Weapon_Spellbook_Fire", "Spellbook", "SPELLBOOK", True)}
    n = T36.fake_items(JClass, ["Weapon_Sword_Frost", "Weapon_Staff_Crystal_Ice", VS, VT, KIT, GUN, BUL, XB, AR, "Weapon_Sword_Iron", "Skyy_Sigil_Mythic",
                                "Skyy_Sigil_Fabled", "Utility_Leather_Backpack"] + list(SOULS) + ["Weapon_Sword_Mithril", "Weapon_Mace_Mithril", "Weapon_Axe_Mithril", "Weapon_Spellbook_Fire"])
    K.eq(n, 23, "X3 the stand-in item store (+ the 6 Souls weapons and 4 look-alikes)")
    IS0 = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    K.eq(str(Cfg.PACK_WEAPONS), "Sv2_Weapon_Sword_Voidice=Weapon_Sword_Frost, Sv2_Weapon_Staff_Voidice=Weapon_Staff_Crystal_Ice, "
         + ", ".join("%s=%s" % (k, v[0]) for k, v in SOULS.items()), "X3 pack.weapons default (Voidice + the 6 Souls like Bosses weapons)")
    Cfg.SIG_ON, Cfg.SIG_MY = True, True
    for sid, (la, fam, tw, spell) in SOULS.items():
        K.check(str(Gd.packAs(sid)) == la and bool(Gd.isGear(sid)) and str(Gd.kindFor(sid)) == "combat" and bool(Gd.isSpell(sid)) == bool(Gd.isSpell(la)),
                "X3 critic: Souls %s graded like %s (gear, combat, spell %s)" % (sid, la, bool(Gd.isSpell(sid))))
        K.check(str(Gb.family(sid)) == str(Gb.family(la)), "X3 critic: %s family %s = %s's" % (sid, Gb.family(sid), la))
        K.eq(str(Sg.why(IS0(sid, 1), Rl.newDoc(sid, 2, True, "drop", 50), int(Df.R_MY))), str(Sg.PACKMY), "X3 critic: a Mythic Sigil on %s is refused" % sid)
    K.check(not bool(Gd.isSpell("Weapon_Staff_Frenzied")) and str(Gb.family("Weapon_Staff_Frenzied")) != "Staff",
            "X3 critic: the Frenzied 'staff' (Axe animations, Axe_Attack) is a melee axe, not a spell staff")
    K.check(str(Gd.packAs(VS)) == "Weapon_Sword_Frost" and str(Gd.packAs(VT)) == "Weapon_Staff_Crystal_Ice" and Gd.packAs("Weapon_Sword_Frost") is None and Gd.packAs(None) is None,
            "X3 packAs")
    K.check(bool(Gd.isGear(VS)) == bool(Gd.isGear("Weapon_Sword_Frost")) == True and bool(Gd.isGear(VT)) and bool(Gd.isGearMs(VS, 1)), "X3 the Voidice weapons are gear like their look-alikes")
    K.check(str(Gd.kindFor(VS)) == "combat" and str(Gd.kindFor(VT)) == "combat", "X3 kind combat (0.3.37: equipment - no Weapon_ family)")
    K.check(bool(Gd.isSpell(VT)) and not bool(Gd.isSpell(VS)), "X3 the staff is a spell weapon, the sword is not")
    K.check(str(Gb.family(VS)) == "Sword" and str(Gb.family(VT)) == "Staff", "X3 GearBase.family = the look-alike's")
    K.check(str(Gv.typeWord(VS)) == "SWORD" and str(Gv.typeWord(VT)) == "STAFF", "X3 the rarity line word: %s / %s" % (Gv.typeWord(VS), Gv.typeWord(VT)))
    K.check(int(Gd.slotOf(VS)) == 0 and int(Gd.slotOf(VT)) == 1, "X3 slots weapon / spell")
    lg = Gd.legacy(VS)
    K.check(int(Gd.rarity(lg)) == 0 and str(Gd.kind(lg)) == "combat", "X3 a picked-up Voidice gets a Normal combat document (never UT / Mythic)")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Cfg.SIG_ON, Cfg.SIG_MY = True, True
    dd = Rl.newDoc(VS, 2, True, "drop", 40)
    K.eq(str(Sg.why(IS(VS, 1), dd, int(Df.R_MY))), str(Sg.PACKMY), "X3 a Mythic Sigil on a Voidice weapon is refused")
    K.check(Sg.why(IS(VS, 1), dd, 4) is None, "X3 a Fabled Sigil works on it: %s" % Sg.why(IS(VS, 1), dd, 4))
    K.check(Sg.why(IS("Weapon_Sword_Iron", 1), Rl.newDoc("Weapon_Sword_Iron", 2, True, "drop", 12), int(Df.R_MY)) is None, "X3 a Mythic Sigil on a dropped vanilla sword still works")
    K.check(not bool(Gd.isGear(KIT)) and not bool(Gd.isTool(KIT)) and not bool(Gd.isGear("Utility_Leather_Backpack")), "X3 the repair kit + the ArmorBench Utility outputs are no gear / tool")
    K.check(Gp.benchWhy(None, "Utility_Leather_Backpack") is None and not bool(Gp.offBench("Utility_Leather_Backpack")), "X3 the bench veto never refuses the Utility recipes")
    keep = Cfg.PACK_WEAPONS
    Cfg.PACK_WEAPONS = ""
    K.check(not bool(Gd.isGear(VS)) and str(Gd.kindFor(VS)) == "equipment" and Gb.family(VS) is None, "X3 pack.weapons empty = 0.3.37 (no gear)")
    Cfg.PACK_WEAPONS = "Sv2_Weapon_Sword_Voidice=Sv2_Weapon_Staff_Voidice, Sv2_Weapon_Staff_Voidice=Weapon_Staff_Crystal_Ice"
    K.check(Gd.packAs(VS) is None and str(Gd.packAs(VT)) == "Weapon_Staff_Crystal_Ice", "X3 a non-Weapon_ / chained target is refused")
    Cfg.PACK_WEAPONS = "Sv2_Weapon_Sword_Voidice=Weapon_Gun_Blunderbuss"
    K.check(not bool(Gd.isGear(VS)), "X3 a look-alike that is no gear (gear.exclude Weapon_Gun) -> no gear")
    Cfg.PACK_WEAPONS = keep

    # ---- X4 no guns
    K.eq(str(Cfg.PACK_CONVERT), "Weapon_Gun_Blunderbuss_Gravedigger=Weapon_Crossbow_Ancient_Steel, Weapon_Gun_Blunderbuss_Gravedigger_Bullet=Weapon_Arrow_Crude", "X4 pack.convert default")
    K.check(not bool(Gd.isGear(GUN)) and not bool(Gd.isGear(BUL)), "X4 guns / bullets are never gear (gear.exclude Weapon_Gun)")
    K.check(str(Gd.convTo(GUN)) == XB and str(Gd.convTo(BUL)) == AR and Gd.convTo(XB) is None and Gd.convTo("Weapon_Sword_Iron") is None, "X4 convTo")
    cs = Gs.convStack(IS(BUL, 64), AR)
    K.check(str(cs.getItemId()) == AR and int(cs.getQuantity()) == 64, "X4 convStack: 64 bullets -> 64 crude arrows")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    c = SIC(JShort(5))
    c.setItemStackForSlot(JShort(0), IS(GUN, 1))
    c.setItemStackForSlot(JShort(1), IS(BUL, 64))
    c.setItemStackForSlot(JShort(2), IS("Weapon_Sword_Iron", 1))

    def cnt(cc, i_):
        t = 0
        for s_ in range(int(cc.getCapacity())):
            x = cc.getItemStack(JShort(s_))
            if x is not None and not x.isEmpty() and str(x.getItemId()) == i_:
                t += int(x.getQuantity())
        return t
    before = (cnt(c, GUN), cnt(c, BUL), cnt(c, XB), cnt(c, AR), cnt(c, "Weapon_Sword_Iron"))
    n0 = int(Gs.CONV_N.get())
    for i in range(3):
        r = Gs.convSlot(None, c, i, c.getItemStack(JShort(i)))
    after = (cnt(c, GUN), cnt(c, BUL), cnt(c, XB), cnt(c, AR), cnt(c, "Weapon_Sword_Iron"))
    K.eq(before, (1, 64, 0, 0, 1), "X4 the container before")
    K.eq(after, (0, 0, 1, 64, 1), "X4 convSlot on a real SimpleItemContainer: the gun -> the crossbow, 64 bullets -> 64 arrows, the sword untouched")
    K.eq(int(Gs.CONV_N.get()) - n0, 2, "X4 two conversions counted (logged)")
    keepc = Cfg.PACK_CONVERT
    Cfg.PACK_CONVERT = "Weapon_Gun_Blunderbuss_Gravedigger=Weapon_No_Such_Item"
    K.check(Gd.convTo(GUN) is None, "X4 a missing target item -> left alone (one WARN)")
    Cfg.PACK_CONVERT = ""
    c.setItemStackForSlot(JShort(3), IS(GUN, 1))
    r = Gs.convSlot(None, c, 3, c.getItemStack(JShort(3)))
    K.check(str(r.getItemId()) == GUN and cnt(c, GUN) == 1, "X4 pack.convert empty = off")
    Cfg.PACK_CONVERT = keepc

    # ---- X5 textures
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    bad = [x for x in zn.namelist() if x.lower().endswith(".png") and not x.startswith("Common/UI/") and any(d_ % 32 for d_ in SA.png_size(zn.read(x)))]
    K.eq(bad, [], "X5 every PNG of the jar outside Common/UI/ in multiples of 32")
    pad = _farm_pad_names()
    K.check(len(pad) == 28 and all("/SkyyFarming/" in x and x.endswith("_Texture.png") for x in pad), "X5 0.3.37 had exactly the 28 Farming textures off (%d)" % len(pad))
    ok = 0
    for x in pad:
        crop = x.split("/")[-2]
        orig = open(os.path.join(FARM_ART, crop, *x.split("/")), "rb").read()
        assert orig == zo.read(x)
        a, b = SA.png_decode(orig), SA.png_decode(zn.read(x))
        same = all(b.px[y * b.w * 4:y * b.w * 4 + a.w * 4] == a.px[y * a.w * 4:(y + 1) * a.w * 4] for y in range(a.h))
        clear = all(b.px[(y * b.w + xx) * 4 + 3] == 0 for y in range(b.h) for xx in range(b.w) if xx >= a.w or y >= a.h)
        mod = x.replace("_Texture.png", ".blockymodel")
        if same and clear and b.w % 32 == 0 and b.h % 32 == 0 and b.w - a.w < 32 and b.h - a.h < 32 and zn.read(mod) == zo.read(mod):
            ok += 1
    K.eq(ok, 28, "X5 the 28 padded textures = Quirk's originals pixel for pixel + transparent padding < 32 px, models byte-identical")
    # ---- X6 fixer 2: one Mythic roll per pack boss fight (a death that spawns the next form = the same family)
    fam = lambda r_: str(Gp.family(r_))
    K.check(fam("SLB_Gravedigger_Beast") == fam("SLB_Gravedigger") == "SLB_Gravedigger", "X6 the Gravedigger and its spawned Beast are one family")
    K.check(fam("SLB_Bishop_Aerial") == fam("SLB_Bishop") and fam("SLB_Conductor_Disguise") == fam("SLB_Conductor"), "X6 Bishop / Conductor forms = one family")
    K.check(len(set(fam("Sv2_CompositeBoss_" + x_) for x_ in ("Dormant", "P1", "P2", "P3"))) == 1 and fam("Sv2_CompositeBoss_P3") == "Sv2_CompositeBoss",
            "X6 the Bandit Boss Dormant + P1-P3 = one family")
    K.check(fam("SLB_Ancient_Calamity_P1") == fam("SLB_Ancient_Calamity_P2") == "SLB_Ancient_Calamity", "X6 Ancient Calamity P1 / P2 = one family")
    K.check(fam("Goblin_Duke_Phase_2") == "Goblin_Duke" and fam("Skeleton_Elite") == "Skeleton_Elite" and fam("Foo_P") == "Foo_P" and fam("Foo_Px1") == "Foo_Px1"
            and fam("_Beast") == "_Beast" and fam("SLB_Rubeus_Beast") != fam("SLB_Gravedigger") and fam(None) == "" and fam("SLB_Nightlord") == "SLB_Nightlord",
            "X6 0.3.37 families unchanged (_Phase, plain roles), odd ids left alone, different bosses stay apart")
    pu = JClass("java.util.UUID").randomUUID()
    t0 = int(JClass("java.lang.System").currentTimeMillis())
    r1 = bool(Gp.firstOfFight(pu, Gp.family("SLB_Gravedigger"), t0))
    r2 = bool(Gp.firstOfFight(pu, Gp.family("SLB_Gravedigger_Beast"), t0 + 30000))
    r3 = bool(Gp.firstOfFight(pu, Gp.family("SLB_Nightlord"), t0 + 30000))
    K.check(r1 and not r2 and r3, "X6 firstOfFight: the Beast 30 s after the Gravedigger = no second roll; another boss still rolls (%s %s %s)" % (r1, r2, r3))
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    fc = os.path.join(home, "config.properties")
    Cfg.FILE = JClass("java.nio.file.Paths").get(fc)
    MIG = [m for m in ("migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7")]
    t0 = HK.tree_hash(home)
    m1 = [str(getattr(Cfg, m)()) for m in MIG]
    t1 = HK.tree_hash(home)
    m2 = "".join(str(getattr(Cfg, m)()) for m in MIG)
    t2 = HK.tree_hash(home)
    K.notes.append("D start 1 on the live copy (0.3.37's migrations; 0.3.38 adds none): %s" % [x[:120] for x in m1 if x])
    K.check(m2 == "" and t1 == t2, "D start 2: nothing changes (%r)" % m2[:120])
    K.check(all("0.3.38" not in x for x in m1), "D 0.3.38 writes no migration of its own")
    txt = open(fc, "rb").read().decode("latin-1")
    Cfg.load()
    if "pack.weapons" not in txt and "pack.convert" not in txt:
        K.check(str(Cfg.PACK_WEAPONS).startswith("Sv2_Weapon_Sword_Voidice=") and str(Cfg.PACK_CONVERT).startswith("Weapon_Gun_Blunderbuss_Gravedigger="),
                "D the live file has no pack line -> the pack rows load at their defaults")
    K.check(bool(Cfg.SMITH_COMBAT) and str(Cfg.NOT_BOSS) == "Skeleton_Elite*", "D the rest of the live file loads as before")
    K.notes.append("D files changed by start 1 (0.3.37 would do the same): %s" % sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k))[:8])
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
