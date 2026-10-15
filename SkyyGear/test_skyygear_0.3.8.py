"""Harness for SkyyGear 0.3.8 = the 0.3.7 harness's children run on the 0.3.8 jar (only the listed, explained deviations) + WEAPON SPEED TIERS
FOR WANDS AND STAFFS with SkyyArmory 0.1.26 (tools/gear_0_3_8_patch.py header). Build first:
    python tools/armory_0_1_26_patch.py && python SkyyArmory/build_skyyarmory_0.1.26.py
    python tools/gear_0_3_8_patch.py && python SkyyGear/build_skyygear_0.3.8.py

    python SkyyGear/test_skyygear_0.3.8.py [--keep] [--only assets,verify,compare,h38,h37,g36,snd,till,life,start,audit]

Phases (fresh child JVMs, -Xverify:all where classes load):
  S38  non-class entries 0.3.7 -> 0.3.8: the same entries, only manifest.json changes; the same classes
  A    every class loads + verifies (-Xverify:all)
  C38  CLASS COMPARE 0.3.7 -> 0.3.8: exactly the listed members differ; the wiring (weaponHit -> shotWeight, onEntityAdded -> shotW, famCalc ->
       casterFam, put -> readyC, tick -> lostC, weaponRows -> casterRows, mode 11 -> appliedFor)
  H38  ONE booted engine (the 0.3.5 life setup) + SkyyArmory 0.1.26 LOADED AS ITS OWN PACK (every codec validator) + its real classes, EXECUTED:
       P  the pack: every tier root runs its tree, the trees / tier copies / 3 effects are loaded assets, no SEVERE / WARNING about them;
          ArmoryCheck.packCheck (speedCheck) on the loaded assets: 16 of 16 trees live, every tier copy reads back
       B  armory:fn:speed on the REAL items: the 8 wands / 8 staffs / Wood-Rotten-Tribal wands / Untiered Loophole + Second Opinion answer
          their family, root, tree (live), quick projectile and weights; Soul Orb / Cages, spellbooks, Bo staffs, a sword = null; an unknown id
          = "unloaded"
       F  SkyyGear's families: famOf = NM (Wand) / NM + 1 (Staff) for them, -1 for the excluded ones; without armory:fn:speed nothing is
          cached and casters have no family; casterFam "unloaded" = not cached
       R  THE ROLL: 1 200 old staffs / wands without a tier get one on their FIRST stamp scan (about 25 % each), a second scan changes nothing,
          one gear.log SPEED line each; unidentified = none, identify rolls it, reforge keeps it; excluded casters never get one
       T  THE TOOLTIP on every tier: "<Tier> Attack Speed" in the head, "Quick Shot N damage - M Mana" with N = the per-hit damage x w and M =
          Mana x w in tenths (= SkyyArmory's tier asset cost for that root); the Charged rows equal on every tier; Medium = 0.3.7's row;
          switched off = no head, the 0.3.7 row
       E  THE TIER EFFECTS on a REAL EffectControllerComponent: a Slow staff puts SkyyGear_Speed_Slow + SkyyArmory_Speed_Slow, a change swaps
          both sets, Medium / an excluded item = none; the caster effect lost -> noted + put back; SkyyArmory's set missing = casters Medium
       H  THE HIT (GearHit.weaponHit on real Damage objects): a quick shot's record weight x the hit (Slow 1.4 ... Super Fast 0.5), charged /
          other projectiles x1, switched off x1; shotW = the APPLIED tier only for the weapon's own quick projectile, the swap window takes the
          smaller weight; DAMAGE PER SECOND and MANA PER SECOND (SkyyArmory's tier cooldowns + costs) within 2 % of Medium on all 16 roots
       G  gear:fn:speed {"applied", uuid, id} = the applied weight; SkyyArmory's ArmorySpeedFn.handW through it (the wand signature meter)
       D  /gear read describes a caster, the ready / roots texts name the casters
  H37 / G36 / SND / TILL / L35  the 0.3.7 harness's children on the 0.3.8 jar: every check, the listed deviations only
  D    START TWICE on a scratch COPY of the live Skyy_SkyyGear folder with 0.3.7 and 0.3.8: the 2nd start changes nothing, both write the same
       config.properties (no row, no one-time update), the fresh default file is the same
  AA   the engine-access audit
Scratch: tools/dev/scratch/caster/gear/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, glob, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


VERSION = "0.3.8"
V37 = "0.3.7"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "caster", "gear")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J37 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V37))                       # read only
AR26 = os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.26.jar")                       # read only (loaded as a pack + its classes)
PKG = "com.skyy.gear."
APKG = "com.skyy.armory."
TIERS = ["Slow", "Medium", "Fast", "Super Fast"]
W = [1.4, 1.0, 0.7, 0.5]

# ---- the 0.3.7 harness as a library (it loads the 0.3.6 / 0.3.5 ones); its children run on THIS jar in THIS scratch folder
_H37 = os.path.join(HERE, "test_skyygear_0.3.7.py")
_T37 = open(_H37, encoding="utf-8").read()
_cut = _T37.rindex('if __name__ == "__main__":')
_argv = sys.argv
sys.argv = [_H37, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH]
H37 = {"__name__": "skyygear_h37", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(_T37[:_cut], _H37 + " (library)", "exec"), H37)
sys.argv = _argv
H36 = H37["H36"]
H35 = H37["H35"]
H = H37["H"]
Child, _jvm, jar_classes = H37["Child"], H37["_jvm"], H37["jar_classes"]
FAKE_DIR = H37["FAKE_DIR"]
FAKE_PKG = H36["FAKE_PKG"]
# SkyyCollections 0.2.11 (the 0.3.5 life setup's Enchanted items) was tidied away; the newest built jar carries the same Skyy_Ench_* items
if not os.path.isfile(H35["CO_SRC"]):
    _co = sorted(glob.glob(os.path.join(ROOT, "SkyyCollections", "SkyyCollections-0.2.*.jar")), key=lambda p_: [int(x_) for x_ in re.findall(r"\d+", os.path.basename(p_))])
    if _co:
        H35["CO_SRC"] = _co[-1]
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S38: the jar entries
def run_assets38():
    ea, eb = entries(J37), entries(JAR)
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(sorted(ea) == sorted(eb) and changed == ["manifest.json"],
          "S38: 0.3.7 -> 0.3.8: the same entries (no file added / removed), only manifest.json changed among non-class files: %s / added %s gone %s"
          % (changed, sorted(set(eb) - set(ea))[:3], sorted(set(ea) - set(eb))[:3]))
    man = eb["manifest.json"].decode("utf-8")
    check('"0.3.8"' in man and "wands and staffs roll speed tiers too" in man, "S38: the manifest names the round")


# ====================================================================================================== C38: class compare
C38_WANT = {
    "GearSpeed": {"+f NM", "+f CEFF", "+f IDXC", "+f IDXC_NEXT", "+f IDXC_TOLD", "+f CACT", "~<clinit>", "+m casterFam", "+m manaText",
                  "+m casterInfo", "+m casterOn", "+m activeFor", "+m appliedFor", "+m shotW", "+m readyC", "+m putOne", "+m lostC",
                  "+m shotWeight", "~m famCalc", "~m active", "~m reset", "~m rootsText", "~m shows", "~m walk", "~m wantOf", "~m put",
                  "~m tick", "~m describe", "~m readyText"},
    "GearShot": {"+f w"}, "GearShotTrack": {"~m onEntityAdded"}, "GearHit": {"~m weaponHit"}, "GearFn": {"~m apply"},
    "GearBase": {"~m shots"}, "GearView": {"+m casterRows", "~m weaponRows"},
}


def run_compare38(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_

    def code(b_, vers):
        mi_ = b_.getMethodInfo()
        ca_ = mi_.getCodeAttribute()
        if ca_ is None:
            return ""
        it_ = ca_.iterator()
        cpl_ = mi_.getConstPool()
        lines_ = []
        while it_.hasNext():
            pos_ = it_.next()
            t_ = re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))).replace("ldc_w ", "ldc ")
            t_ = re.sub(r"^((if\w*|goto|goto_w|jsr|jsr_w) )\d+$", r"\1N", t_)
            for v_ in vers:
                t_ = t_.replace(v_, "VER")
            lines_.append(t_)
        return "\n".join(lines_)

    def members(p_, cn, vers):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_, vers)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_, vers)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci, vers)
        return d_

    pa, pb = pool_of(J37), pool_of(JAR)
    na, nb = jar_classes(J37), jar_classes(JAR)
    d = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn, (V37, VERSION)), members(pb, cn, (V37, VERSION))
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            d[cn.split(".")[-1]] = sorted(set(("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd))
    for k in sorted(d):
        print("   %-18s %s" % (k, ", ".join(d[k])[:900]))
    bad = dict((k, sorted(set(v) ^ C38_WANT.get(k, set()))) for k, v in d.items() if set(v) != C38_WANT.get(k, set()))
    miss = sorted(k for k in C38_WANT if k not in d)
    K.check(na == nb and not bad and not miss, "C38: 0.3.7 -> 0.3.8 changed exactly the listed members, the same classes: differences %s, missing %s" % (bad, miss))

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
    wires = [("GearHit", "weaponHit", "GearSpeed.shotWeight"), ("GearHit", "weaponHit", "GearSpeed.hitWeight"), ("GearShotTrack", "onEntityAdded", "GearSpeed.shotW"),
             ("GearShotTrack", "onEntityAdded", "GearShot.w"), ("GearSpeed", "famCalc", "GearSpeed.casterFam"), ("GearSpeed", "put", "GearSpeed.readyC"),
             ("GearSpeed", "put", "GearSpeed.putOne"), ("GearSpeed", "tick", "GearSpeed.lostC"), ("GearView", "weaponRows", "GearView.casterRows"),
             ("GearFn", "apply", "GearSpeed.appliedFor"), ("GearSpeed", "shows", "GearSpeed.activeFor"), ("GearSpeed", "wantOf", "GearSpeed.activeFor")]
    K.check(all(calls(*w_) for w_ in wires), "C38: the wiring: %s" % [w_ for w_ in wires if not calls(*w_)])
    K.save()


# ====================================================================================================== H38: one booted engine + SkyyArmory 0.1.26
def run_h38(out):
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h38(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H38: the phase raised: %s" % traceback.format_exc()[-900:])
    K.save()


def arm_specs():
    """(root, Medium Charging, family, the item ids that use it, quick projectile)"""
    out = [("Wand_Primary", "Wand_Primary", "Wand", ["Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal"], "SkyyArmory_QuickOrb_Wood")]
    for m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"):
        r = "SkyyArmory_Wand_Primary_" + m
        out.append((r, r, "Wand", ["Weapon_Wand_" + m] + (["Weapon_Wand_UT_SecondOpinion"] if m == "Iron" else []), "SkyyArmory_QuickOrb_" + m))
    for m in ("Wood", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"):
        r = "SkyyArmory_Staff_Primary_" + m
        out.append((r, r, "Staff", ["Weapon_Staff_" + m] + (["Weapon_Staff_UT_Loophole"] if m == "Iron" else []), "SkyyArmory_StaffQuickOrb_" + m))
    return out


def _h38(L, K):
    from jpype import JClass, JInt, JShort, JFloat, JDouble, JObject, JArray, JString, JLong
    E, addpack, br, Data, Roll, apply, logs = L["E"], L["addpack"], L["br"], L["Data"], L["Roll"], L["apply"], L["logs"]
    us, jf, U1 = L["us"], L["jf"], L["U1"]
    P = lambda n: JClass(PKG + n)
    Spd, View, Stamp, Base, Hit, Shot, GFn, Defs = (P("GearSpeed"), P("GearView"), P("GearStamp"), P("GearBase"), P("GearHit"), P("GearShot"),
                                                     P("GearFn"), P("GearDefs"))
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    BD = JClass("org.bson.BsonDocument")
    BI32 = JClass("org.bson.BsonInt32")
    AL = JClass("java.util.ArrayList")
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    INT, ROOTI = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    EFX = JClass("com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect")
    NM = int(Spd.NM)
    K.check(NM == 9 and list(Spd.F_NAME)[NM:] == ["Wand", "Staff"] and len(Spd.F_W) == 44 and [float(x) for x in list(Spd.F_W)[36:]] == W * 2,
            "H38: two caster families after the 9 melee ones (Wand %d, Staff %d), weights 1.4 / 1 / 0.7 / 0.5" % (NM, NM + 1))

    # ============================================================================ P: SkyyArmory 0.1.26 as its own pack
    afail, arec = addpack(AR26, "Skyy:SkyyArmory")
    ours = [r for r in arec if r[0] in ("SEVERE", "WARNING") and any(x in r[1] for x in ("SkyyArmory_Spd", "SkyyArmory_Speed", "Wand_Primary"))]

    def same_as_medium(r_):
        """a bare-boot artifact: this JVM has no 'Mana' EntityStatType (vanilla's own stat store fails here), so a quick shot with a Mana cost
        fails validation and is removed - a tier copy failing / removed EXACTLY like its Medium original (the 0.1.25 file) is that, not ours"""
        m_ = re.match(r"Failed to validate asset: SkyyArmory_Spd[SFX]_([A-Za-z0-9_]+), ", r_[1])
        if m_ and "Asset 'Mana' of type" in r_[1]:
            return any(x_[1].startswith("Failed to validate asset: %s, " % m_.group(1)) and "Asset 'Mana' of type" in x_[1] for x_ in arec)
        m_ = re.match(r"Removing child asset '(\**)SkyyArmory_Spd[SFX]_([A-Za-z0-9_]+)' of removed asset", r_[1])
        if m_:
            return any(x_[1].startswith("Removing child asset '%s%s' of removed asset" % (m_.group(1), m_.group(2))) for x_ in arec)
        return False
    art = [r for r in ours if same_as_medium(r)]
    ours = [r for r in ours if r not in art]
    K.check(not ours, "H38 P: no SEVERE / WARNING record about the speed trees, tier copies, effects or the Wand_Primary root (except %d tier copies failing "
                      "exactly like their Medium originals: this bare JVM has no Mana stat): %s" % (len(art), [r[1][:200] for r in ours[:3]]))
    K.notes.append("H38 P: %d bare-boot Mana-stat records on tier copies, each matched by the same record on its 0.1.25 original" % len(art))
    K.notes.append("H38 P: SkyyArmory 0.1.26 pack: failed stores in this bare boot %s (vanilla's own %s)" % (afail, E["vfail"]))
    SP = arm_specs()
    pbad = []
    for r, med, fam, items, qp in SP:
        ra = ROOTI.getAssetMap().getAsset(r)
        ids = list(ra.getInteractionIds()) if ra is not None else []
        tree = "SkyyArmory_Spd_" + med
        if ids[:1] != [tree]:
            pbad.append((r, "root", ids))
        ta = INT.getAssetMap().getAsset(tree)
        if ta is None or not str(ta.getClass().getName()).endswith("EffectConditionInteraction"):
            pbad.append((r, "tree", None if ta is None else str(ta.getClass().getName())))
        for t in ("S", "F", "X"):
            for x_, cls_ in (("SkyyArmory_Spd%s_%s" % (t, med), "ChargingInteraction"),):
                a_ = INT.getAssetMap().getAsset(x_)
                if a_ is None or not str(a_.getClass().getName()).endswith(cls_):
                    pbad.append((r, x_, None if a_ is None else str(a_.getClass().getName())))
    eidx = [int(EFX.getAssetMap().getIndex(e_)) for e_ in ("SkyyArmory_Speed_Slow", "SkyyArmory_Speed_Fast", "SkyyArmory_Speed_SuperFast")]
    K.check(not pbad and all(x_ >= 0 for x_ in eidx), "H38 P: the 16 roots run their trees (EffectCondition), the tier Charging copies + the 3 effects are LOADED assets: %s %s" % (pbad[:4], eidx))
    # SkyyArmory's own classes (a child loader of the system one, like a plugin): ArmorySpeedFn, ArmoryInfoFn, ArmoryCheck
    URL, File = JClass("java.net.URL"), JClass("java.io.File")
    acl = JClass("java.net.URLClassLoader")(JArray(URL)([File(AR26).toURI().toURL()]), JClass("java.lang.ClassLoader").getSystemClassLoader())
    ASF = JClass(APKG + "ArmorySpeedFn", loader=acl)
    AIF = JClass(APKG + "ArmoryInfoFn", loader=acl)
    ACK = JClass(APKG + "ArmoryCheck", loader=acl)
    asf = ASF()
    pc = [str(x_) for x_ in ACK.packCheck()]
    sbad = AL()
    nlive = int(ACK.speedCheck(sbad, INT.getAssetMap()))
    sbad = [str(x_) for x_ in sbad]
    real = []
    for l_ in sbad:
        id_ = l_.split(" ")[0]
        m_ = re.match(r"SkyyArmory_Spd[SFX]_(.+)$", id_)
        # a tier quick / spend whose Medium original is ALSO not loaded here (the bare boot's missing Mana stat) - else a real read-back failure
        if l_.startswith("root ") or not m_ or " keys " in l_ or INT.getAssetMap().getAsset(m_.group(1)) is not None:
            real.append(l_)
    nkeys = sum(1 for l_ in sbad if " keys " in l_)
    K.check(nlive == 16 and not real and nkeys == 0 and "caster speed trees live on 16 of 16 roots" in pc[1],
            "H38 P: ArmoryCheck.speedCheck / packCheck on the LOADED assets: 16 of 16 trees live, every tier Charging reads back its keys, the tier "
            "quick shots fail only where their Medium original is missing in this bare boot (no Mana stat): %s" % real[:4])
    K.notes.append("H38 P: speedCheck complaints %d (all bare-boot Mana artifacts), keys 0" % len(sbad))
    K.notes.append("H38 P: packCheck %s: %s" % (pc[0], pc[1][:300]))
    st_ = str(ASF.statusText())
    K.check(st_.startswith("caster speed tiers: 16/16 wand / staff roots run their tier tree"), "H38 P: ArmorySpeedFn.statusText on the loaded roots: %s" % st_[:120])

    # ============================================================================ B: armory:fn:speed on the real items
    bbad = []
    for r, med, fam, items, qp in SP:
        for i_ in items:
            a_ = asf.apply(i_)
            got = None if a_ is None else [str(x_) if not hasattr(x_, "doubleValue") else float(x_.doubleValue()) for x_ in a_]
            want = [fam, r, "SkyyArmory_Spd_" + med, "true", qp] + W
            if got is not None:
                got[3] = got[3].lower()
            if got is None or got[:5] != want[:5] or [round(x_, 9) for x_ in got[5:]] != W:
                bbad.append((i_, got))
    nulls = {}
    for i_ in ("Weapon_Wand_SoulOrb", "Weapon_Wand_SoulCage_Copper", "Weapon_Spellbook_Copper", "Weapon_Staff_Bo_Wood", "Weapon_Bo_Copper", "Weapon_Sword_Iron"):
        nulls[i_] = asf.apply(i_)
    unl = asf.apply("Weapon_Wand_NotAnItem")
    K.check(not bbad and all(v_ is None for v_ in nulls.values()) and str(unl) == "unloaded",
            "H38 B: armory:fn:speed on the REAL items: 21 casters answer family / root / tree (live) / quick projectile / weights; Soul Orb + Cage, "
            "spellbook, Bo staffs, sword = null; an unknown id = unloaded: %s %s %s" % (bbad[:3], [k_ for k_, v_ in nulls.items() if v_ is not None], unl))

    # ============================================================================ F: SkyyGear's families
    br.remove("armory:fn:speed")
    Spd.reset()
    f_none = int(Spd.famOf("Weapon_Staff_Wood"))
    cached = bool(Spd.FAM.containsKey("Weapon_Staff_Wood"))
    br.put("armory:fn:speed", asf)
    br.put("armory:fn:info", AIF())
    Spd.reset()
    FAMS = {"Weapon_Staff_Wood": NM + 1, "Weapon_Staff_Onyxium": NM + 1, "Weapon_Wand_Wood": NM, "Weapon_Wand_Copper": NM, "Weapon_Wand_Tribal": NM,
            "Weapon_Staff_UT_Loophole": NM + 1, "Weapon_Wand_UT_SecondOpinion": NM, "Weapon_Wand_SoulOrb": -1, "Weapon_Spellbook_Copper": -1,
            "Weapon_Staff_Bo_Wood": -1, "Weapon_Sword_Iron": 0}
    gotf = dict((i_, int(Spd.famOf(i_))) for i_ in FAMS)
    K.check(f_none == -1 and not cached and gotf == FAMS, "H38 F: famOf - without armory:fn:speed a staff has no family and nothing is cached; with it: %s" % gotf)

    class Unl(object):
        pass
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class UnlFn(object):
        @JOverride
        def apply(self, o):
            return JString("unloaded")
    br.put("armory:fn:speed", UnlFn())
    Spd.reset()
    K.check(int(Spd.casterFam("Weapon_Staff_Wood")) == -100 and int(Spd.famOf("Weapon_Staff_Wood")) == -1 and not bool(Spd.FAM.containsKey("Weapon_Staff_Wood"))
            and int(Spd.casterFam("Weapon_Sword_Iron")) == -1, "H38 F: an \"unloaded\" answer = not known yet (-100, never cached)")
    br.put("armory:fn:speed", asf)
    Spd.reset()

    # ============================================================================ R: the roll (first sight), identify, reforge, excluded
    def stk(iid, d_):
        return IS(iid, JInt(1)).withMetadata(BD(str(Defs.DOC_KEY), d_))

    def old_doc(iid, lvl=5):
        d_ = Roll.newDoc(iid, JInt(1), True, "admin", JInt(lvl)).clone()
        d_.remove("spd")
        return d_
    logs()
    cnt = [0, 0, 0, 0]
    same, bad_r = 0, []
    CAS = ["Weapon_Staff_Wood", "Weapon_Wand_Copper", "Weapon_Staff_Iron", "Weapon_Wand_Wood"]
    for k_ in range(1200):
        iid = CAS[k_ % 4]
        s0 = stk(iid, old_doc(iid))
        if int(Spd.tierOf(Data.gearDoc(s0.getMetadata()))) != -1:
            bad_r.append(("pre", iid))
        s1 = Stamp.stampStack(s0, U1, JArray(JInt)(3))
        t1 = int(Spd.tierOf(Data.gearDoc(s1.getMetadata())))
        if t1 < 0:
            bad_r.append((iid, t1))
            continue
        cnt[t1] += 1
        s2 = Stamp.stampStack(s1, U1, JArray(JInt)(3))
        if s2 == s1 or (s2.getMetadata() is not None and s2.getMetadata().equals(s1.getMetadata())):
            same += 1
    lg = logs()
    spl = [l_ for l_ in lg if " SPEED Weapon_" in l_ or l_.startswith("SPEED Weapon_") or "SPEED Weapon_" in l_]
    K.check(not bad_r and sum(cnt) == 1200 and all(abs(c_ / 1200.0 - 0.25) < 0.05 for c_ in cnt) and same == 1200 and len(spl) >= 1200,
            "H38 R: FIRST SIGHT - 1 200 old wands / staffs without a tier get one on their first stamp scan (Slow / Medium / Fast / Super Fast %s), a "
            "second scan changes nothing (%d / 1200), one gear.log SPEED line each (%d): %s" % (cnt, same, len(spl), bad_r[:3]))
    u_ = Roll.newDoc("Weapon_Staff_Copper", JInt(2), False, "drop", JInt(12))
    idd = Roll.identify("Weapon_Staff_Copper", u_, U1)
    kept = []
    for t in range(4):
        d_ = old_doc("Weapon_Staff_Copper", 12)
        d_.put("spd", BI32(JInt(t)))
        for nm_, nd_ in (("reforge", Roll.reforge("Weapon_Staff_Copper", d_)), ("put", Data.gearDoc(Data.put(IS("Weapon_Staff_Copper", JInt(1)), d_, U1).getMetadata()))):
            if int(Spd.tierOf(nd_)) != t:
                kept.append((t, nm_))
    exd = []
    for i_ in ("Weapon_Wand_SoulOrb", "Weapon_Spellbook_Copper", "Weapon_Staff_Bo_Wood"):
        try:
            d_ = old_doc(i_)
        except Exception:
            continue
        if int(Spd.tierOf(Spd.ensure(i_, d_))) != -1 or int(Spd.tierOf(Data.gearDoc(Stamp.stampStack(stk(i_, d_), U1, JArray(JInt)(3)).getMetadata()))) != -1:
            exd.append(i_)
    K.check(int(Spd.tierOf(u_)) == -1 and int(Spd.tierOf(idd)) in (0, 1, 2, 3) and not kept and not exd,
            "H38 R: unidentified = no tier, identify rolls it, reforge / rewrites keep it, the Soul Orb / spellbook / Bo staff never get one: %s %s" % (kept, exd))

    # ============================================================================ T: the tooltip
    COST = {}
    for i_ in range(len(list(ASF.R_ROOT))):
        COST[str(ASF.R_ROOT[i_])] = [float(ASF.T_COST[i_ * 4 + t]) for t in range(4)]
        COST[str(ASF.R_ROOT[i_]) + "#cd"] = [float(ASF.T_CD[i_ * 4 + t]) for t in range(4)]

    def tip(iid, d_):
        tx_, co_ = AL(), AL()
        View.lines(iid, d_, None, tx_, co_)
        return [str(x_) for x_ in tx_]

    BASE = {}

    def tdoc(iid, t, lvl=12):
        """the SAME identified document (one roll per item id + level) with tier t (-1 = none) - only "spd" differs between tiers"""
        if (iid, lvl) not in BASE:
            BASE[(iid, lvl)] = old_doc(iid, lvl)
        d_ = BASE[(iid, lvl)].clone()
        if t >= 0:
            d_.put("spd", BI32(JInt(t)))
        return d_
    tbad, samples = [], {}
    for r, med, fam, items, qp in SP:
        for iid in items[:1]:
            charged = None
            for t in range(4):
                d_ = tdoc(iid, t)
                sh = Base.shots(iid, d_)
                ls = tip(iid, d_)
                if sh is None:
                    tbad.append((iid, "no shots"))
                    break
                qm, qraw = int(sh[5]), float(sh[8])
                qw = str(sh[7]) if sh[7] is not None else ""
                mana = str(Spd.manaText(Spd.manaCost(float(qm), W[t])))
                want_q = "Quick Shot %d damage - %s Mana" % (int(math.floor(qraw * W[t] + 1e-6)), mana) + (" - " + qw if qw else "")
                head = "%s Attack Speed" % TIERS[t]
                ch_ = [l_ for l_ in ls if l_.startswith("Deals ") or l_.startswith("Mana Cost: ")]
                if charged is None:
                    charged = ch_
                if head not in ls or want_q not in ls or ch_ != charged or abs(Spd.manaCost(float(qm), W[t]) - COST[r][t]) > 1e-9:
                    tbad.append((iid, TIERS[t], head in ls, want_q, [l_ for l_ in ls if l_.startswith("Quick Shot")], COST[r][t]))
                if t == 1 and want_q != str(View.quickRow(sh)):
                    tbad.append((iid, "Medium row differs from 0.3.7's", want_q, str(View.quickRow(sh))))
                if iid in ("Weapon_Staff_Wood", "Weapon_Wand_Copper"):
                    samples["%s %s" % (iid, TIERS[t])] = [l_ for l_ in ls if "Attack Speed" in l_ or l_.startswith("Quick Shot") or l_.startswith("Deals ") or l_.startswith("Mana Cost")]
    Spd.FORCE_OFF = True
    off = tip("Weapon_Staff_Wood", tdoc("Weapon_Staff_Wood", 3))
    sh0 = Base.shots("Weapon_Staff_Wood", tdoc("Weapon_Staff_Wood", 3))
    Spd.FORCE_OFF = False
    none_ = tip("Weapon_Staff_Wood", tdoc("Weapon_Staff_Wood", -1))
    K.check(not tbad, "H38 T: TOOLTIP on every root and tier: '<Tier> Attack Speed' + 'Quick Shot <per hit x w> damage - <Mana x w> Mana' (= SkyyArmory's "
                      "tier asset cost), the Charged rows equal, Medium = 0.3.7's row: %s" % tbad[:3])
    K.check(not any("Attack Speed" in l_ for l_ in off) and str(View.quickRow(sh0)) in off and not any("Attack Speed" in l_ for l_ in none_),
            "H38 T: switched off / no tier yet = no speed head, the 0.3.7 quick row: %s" % [l_ for l_ in off if "Quick" in l_])
    for k_ in sorted(samples):
        print("H38 T. %-28s %s" % (k_, samples[k_]))

    # ============================================================================ E: the tier effects on a REAL EffectControllerComponent
    ECCc = JClass("com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    FS, FBuf = JClass(FAKE_PKG + ".FakeStore"), JClass(FAKE_PKG + ".FakeBuffer")
    IHM = JClass("java.util.IdentityHashMap")
    JClass(FAKE_PKG + ".FakeUtil").single("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")          # removeEffect asks it for the stat map type
    ecc = ECCc()
    ref = us.allocateInstance(REFc.class_)
    jf(REFc, "index").setInt(ref, JInt(38))
    st = us.allocateInstance(FS.class_)
    st.comps = JClass("java.util.HashMap")()
    pm = IHM()
    pm.put(ECCc.getComponentType(), ecc)
    st.comps.put(ref, pm)
    jf(REFc, "store").set(ref, st)
    buf = us.allocateInstance(FBuf.class_)
    buf.st = st
    UUID = JClass("java.util.UUID")
    U8 = UUID.fromString("00000000-0000-0000-0000-0000000000e8")
    Spd.IDX, Spd.IDX_NEXT, Spd.IDX_TOLD = None, JLong(0), False
    Spd.IDXC, Spd.IDXC_NEXT, Spd.IDXC_TOLD = None, JLong(0), False
    Spd.forget(U8)
    NAMES = ["SkyyGear_Speed_Slow", "SkyyGear_Speed_Fast", "SkyyGear_Speed_SuperFast", "SkyyArmory_Speed_Slow", "SkyyArmory_Speed_Fast", "SkyyArmory_Speed_SuperFast"]

    def act():
        m_ = ecc.getActiveEffects()
        return sorted(n_ for n_ in NAMES if m_.get(JInt(int(EFX.getAssetMap().getIndex(n_)))) is not None)
    s_ = dict((t, stk("Weapon_Staff_Wood", tdoc("Weapon_Staff_Wood", t))) for t in range(4))
    sw_fast = stk("Weapon_Sword_Iron", Roll.newDoc("Weapon_Sword_Iron", JInt(1), True, "admin", JInt(15)).clone())
    sw_fast.getMetadata()
    d_sw = Data.gearDoc(sw_fast.getMetadata()).clone()
    d_sw.put("spd", BI32(JInt(2)))
    sw_fast = stk("Weapon_Sword_Iron", d_sw)
    seq = []
    Spd.tick(buf, ref, U8, s_[0])
    seq.append(("slow staff", act()))
    Spd.tick(buf, ref, U8, s_[3])
    seq.append(("super fast staff", act()))
    Spd.tick(buf, ref, U8, s_[1])
    seq.append(("medium staff", act()))
    Spd.tick(buf, ref, U8, sw_fast)
    seq.append(("fast sword", act()))
    Spd.tick(buf, ref, U8, stk("Weapon_Spellbook_Copper", old_doc("Weapon_Spellbook_Copper")))
    seq.append(("spellbook", act()))
    want = [("slow staff", ["SkyyArmory_Speed_Slow", "SkyyGear_Speed_Slow"]), ("super fast staff", ["SkyyArmory_Speed_SuperFast", "SkyyGear_Speed_SuperFast"]),
            ("medium staff", []), ("fast sword", ["SkyyArmory_Speed_Fast", "SkyyGear_Speed_Fast"]), ("spellbook", [])]
    K.check(seq == want and Spd.IDXC is not None and [int(x_) for x_ in Spd.IDXC][1] == -1,
            "H38 E: GearSpeed.tick on a REAL EffectControllerComponent puts SkyyGear's AND SkyyArmory's effect of the held tier, a change swaps both sets, "
            "Medium / a spellbook = none: %s" % seq)
    Spd.tick(buf, ref, U8, s_[0])
    lost0 = int(Spd.N.get(8))
    ecc.removeEffect(ref, JInt(int(EFX.getAssetMap().getIndex("SkyyArmory_Speed_Slow"))), buf)
    Spd.tick(buf, ref, U8, s_[0])
    K.check(int(Spd.N.get(8)) == lost0 + 1 and act() == ["SkyyArmory_Speed_Slow", "SkyyGear_Speed_Slow"],
            "H38 E: the caster effect lost (died / cleared) = noted (N[8]) and put back at once: %s" % act())

    # ============================================================================ H: the hit, shotW, DPS + Mana per second
    stt = Spd.ST.get(U8)
    L_ = stt[2]
    L_[4] = JLong(int(L_[4]) - 60000)          # out of the swap window
    w_slow = float(Spd.appliedW(U8, JInt(NM + 1)))
    qs = float(Spd.shotW(U8, s_[0], "SkyyArmory_StaffQuickOrb_Wood"))
    qc = float(Spd.shotW(U8, s_[0], "SkyyArmory_StaffOrb_Wood"))
    qo = float(Spd.shotW(U8, s_[0], "SkyyArmory_QuickOrb_Copper"))
    qn = float(Spd.shotW(U8, IS("Weapon_Spellbook_Copper", JInt(1)), "SkyyArmory_StaffQuickOrb_Wood"))
    Spd.tick(buf, ref, U8, s_[3])
    q_swap = float(Spd.shotW(U8, s_[3], "SkyyArmory_StaffQuickOrb_Wood"))
    Spd.tick(buf, ref, U8, s_[0])
    q_back = float(Spd.shotW(U8, s_[0], "SkyyArmory_StaffQuickOrb_Wood"))
    L_ = Spd.ST.get(U8)[2]
    L_[4] = JLong(int(L_[4]) - 60000)
    q_late = float(Spd.shotW(U8, s_[0], "SkyyArmory_StaffQuickOrb_Wood"))
    Spd.tick(buf, ref, U8, s_[1])
    L_ = Spd.ST.get(U8)[2]
    L_[4] = JLong(int(L_[4]) - 60000)
    q_med = float(Spd.shotW(U8, s_[1], "SkyyArmory_StaffQuickOrb_Wood"))
    K.check(abs(w_slow - 1.4) < 1e-12 and abs(qs - 1.4) < 1e-12 and qc == 0.0 and qo == 0.0 and qn == 0.0 and abs(q_swap - 0.5) < 1e-12
            and abs(q_back - 0.5) < 1e-12 and abs(q_late - 1.4) < 1e-12 and q_med == 0.0,
            "H38 H: shotW = the APPLIED tier for the weapon's own quick projectile (Slow 1.4), 0 for its charged orb / another projectile / a spellbook; a swap "
            "takes the smaller weight inside the window (Super Fast 0.5, back to Slow still 0.5), then 1.4; Medium = 0: %s" % [w_slow, qs, qc, qo, qn, q_swap, q_back, q_late, q_med])
    apply(part__stats="false")
    DMGc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DCc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
    cidx = int(DCc.getAssetMap().getIndex("Physical"))

    def hit(stack_, w_, amount=100.0):
        rec = Shot(U1, stack_, None, None)
        rec.w = float(w_)
        d_ = DMGc(None, JInt(cidx), JFloat(amount))
        Hit.weaponHit(d_, U1, None, stack_, True, rec, rec, None)
        return float(d_.getAmount())
    hbad, rows = [], []
    for r, med, fam, items, qp in SP:
        iid = items[0]
        base = None
        dps, mps = [], []
        for t in range(4):
            st_t = stk(iid, tdoc(iid, t, 12))
            a_ = hit(st_t, W[t] if t != 1 else 0.0)
            if base is None and t == 0:
                pass
            cyc = COST[r + "#cd"][t]
            dps.append(a_ / cyc)
            mps.append(COST[r][t] / cyc)
        if any(abs(x_ / dps[1] - 1.0) > 0.02 for x_ in dps) or any(abs(x_ / mps[1] - 1.0) > 0.02 for x_ in mps):
            hbad.append((r, dps, mps))
        rows.append((r, [round(x_ / dps[1], 4) for x_ in dps], [round(x_ / mps[1], 4) for x_ in mps]))
    st_s = stk("Weapon_Staff_Wood", tdoc("Weapon_Staff_Wood", 0, 12))
    a1, a14, a0 = hit(st_s, 0.0), hit(st_s, 1.4), hit(st_s, 1.0)
    Spd.FORCE_OFF = True
    aoff = hit(st_s, 1.4)
    Spd.FORCE_OFF = False
    dw = DMGc(None, JInt(cidx), JFloat(100.0))
    w0 = float(Spd.shotWeight(None, dw))
    K.check(abs(a14 / a1 - 1.4) < 1e-4 and abs(a0 - a1) < 1e-4 and abs(aoff - a1) < 1e-4 and w0 == 1.0,
            "H38 H: GearHit.weaponHit on real Damage: a record weight 1.4 = x1.4, 0 / 1 = x1, switched off = x1, no record = x1: %s" % [a1, a14, a0, aoff, w0])
    K.check(not hbad, "H38 H: DAMAGE PER SECOND (weaponHit per hit / SkyyArmory's tier cooldown) and MANA PER SECOND (SkyyArmory's tier cost / cooldown) within "
                      "2 %% of Medium on all 16 roots: %s" % hbad[:3])
    print("H38 H. DPS ratio to Medium (Slow, Medium, Fast, Super Fast) | Mana/s ratio: " + "; ".join("%s %s %s" % r_ for r_ in rows[:3]) + " ...")
    apply()

    # ============================================================================ G: gear:fn:speed "applied" + SkyyArmory's meter weight
    fsp = GFn(JInt(11))
    br.put("gear:fn:speed", fsp)
    Spd.tick(buf, ref, U8, s_[0])
    L_ = Spd.ST.get(U8)[2]
    L_[4] = JLong(int(L_[4]) - 60000)
    ap = fsp.apply(JArray(JObject)([JString("applied"), U8, JString("Weapon_Staff_Wood")]))
    ap_none = fsp.apply(JArray(JObject)([JString("applied"), U8, JString("Weapon_Spellbook_Copper")]))
    ap_bad = fsp.apply(JArray(JObject)([JString("applied"), JString("x"), JString("Weapon_Staff_Wood")]))
    hw = float(ASF.handW(U8, "Weapon_Staff_Wood"))
    inf = fsp.apply(st_s)
    K.check(abs(float(ap) - 1.4) < 1e-12 and float(ap_none) == 1.0 and float(ap_bad) == 1.0 and abs(hw - 1.4) < 1e-12
            and inf is not None and str(inf[0]) == "Slow" and str(inf[4]) == "Staff" and bool(inf[2]),
            "H38 G: gear:fn:speed {applied, uuid, id} = the applied weight (1.4), 1 for a spellbook / bad uuid; SkyyArmory's ArmorySpeedFn.handW through it = 1.4; "
            "the stack answer = { Slow, 1.4, shown, 0, Staff }: %s %s %s %s %s" % (ap, ap_none, ap_bad, hw, None if inf is None else list(inf)))
    br.remove("gear:fn:speed")

    # ============================================================================ D: /gear read + the ready texts
    rd = str(Spd.describe("Weapon_Staff_Wood", tdoc("Weapon_Staff_Wood", 0), U8))
    rt = str(Spd.readyText())
    ro = str(Spd.rootsText())
    K.check(rd.startswith("weapon speed: Staff family (SkyyArmory's tier tree live, caster effects loaded), Slow - quick-shot time, Mana and hit x1.4")
            and "melee families + wands / staffs on SkyyArmory's tier trees" in rt and "wands / staffs: SkyyArmory's caster tier effects loaded" in ro,
            "H38 D: /gear read + ready / roots texts: %s | %s | %s" % (rd[:160], rt[:120], ro[-90:]))
    # SkyyArmory's caster set missing -> casters are Medium (no line), melee untouched
    Spd.IDXC, Spd.IDXC_TOLD, Spd.IDXC_NEXT = None, True, JLong(2 ** 62)
    Spd.CACT.clear()
    K.check(not bool(Spd.shows("Weapon_Staff_Wood", tdoc("Weapon_Staff_Wood", 0))) and bool(Spd.shows("Weapon_Sword_Iron", d_sw))
            and float(Spd.shotW(U8, s_[0], "SkyyArmory_StaffQuickOrb_Wood")) == 0.0,
            "H38 E: SkyyArmory's caster effects missing = no caster line / weight, melee still shown")
    Spd.IDXC_TOLD, Spd.IDXC_NEXT = False, JLong(0)
    # FIX 1 (critic): missing at the last try + the 10 s retry due -> holding ONLY a staff re-resolves the caster set and puts its effect
    Spd.tick(buf, ref, U8, s_[1])          # Medium staff: no effect, nothing applied
    Spd.IDXC, Spd.IDXC_TOLD, Spd.IDXC_NEXT = None, True, JLong(0)
    Spd.CACT.clear()
    Spd.tick(buf, ref, U8, s_[0])
    retry = act()
    K.check(Spd.IDXC is not None and retry == ["SkyyArmory_Speed_Slow", "SkyyGear_Speed_Slow"],
            "H38 FIX1: a caster set missing at the last try is retried once IDXC_NEXT passes while only a staff is held (was: Medium until a "
            "restart): %s" % retry)
    Spd.tick(buf, ref, U8, s_[1])
    Spd.IDXC, Spd.IDXC_TOLD, Spd.IDXC_NEXT = None, True, JLong(2 ** 62)
    Spd.CACT.clear()
    Spd.tick(buf, ref, U8, s_[0])
    K.check(Spd.IDXC is None and act() == [], "H38 FIX1: inside the 10 s wait the staff stays Medium (no effect, no retry spam): %s" % act())
    # FIX 2 (critic): GearSpeed.reset() (the Item reload) drops the caster set like the melee one
    Spd.IDXC, Spd.IDXC_TOLD, Spd.IDXC_NEXT = JArray(JInt)([1, -1, 2, 3]), True, JLong(12345)
    Spd.reset()
    K.check(Spd.IDXC is None and not bool(Spd.IDXC_TOLD) and int(Spd.IDXC_NEXT) == 0 and Spd.IDX is None,
            "H38 FIX2: GearSpeed.reset() clears IDXC / IDXC_TOLD / IDXC_NEXT (and IDX)")
    Spd.tick(buf, ref, U8, s_[1])
    Spd.tick(buf, ref, U8, s_[3])
    K.check(Spd.IDXC is not None and act() == ["SkyyArmory_Speed_SuperFast", "SkyyGear_Speed_SuperFast"],
            "H38 FIX2: after reset() both sets re-resolve on the next held tier weapon: %s" % act())


# ====================================================================================================== D: start twice (0.3.7 and 0.3.8)
def run_start38(out, home, which):
    from jpype import JClass
    K = Child(out)
    jar = JAR if which == "new" else J37
    _jvm([B.SERVER_JAR, jar], verify=(which == "new"))
    Cfg = JClass(PKG + "GearCfg")
    Path = JClass("java.nio.file.Paths")
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    lld = os.path.join(home, "lifelong")
    ll0 = sorted(os.listdir(lld)) if os.path.isdir(lld) else None
    snaps = []
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214",
                  "migrate0215", "migrate0216", "migrate0217", "migrate0218", "migrate031"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(os.path.join(home, "config.properties"), "rb").read())
    K.check(snaps[1] == snaps[0], "D/%s: the 2nd start changes nothing" % which)
    K.check((sorted(os.listdir(lld)) if os.path.isdir(lld) else None) == ll0, "D/%s: the start never touches the lifelong folder" % which)
    K.save(cfg=snaps[0].decode("latin-1"), fresh=str(Cfg.defaultsText()))


# ====================================================================================================== parent
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--root", SCR_ROOT], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, str(n)[:400]))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: H35["run_mkfake5"](arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--life", lambda: H35["run_life"](arg("--out"))), ("--compare38", lambda: run_compare38(arg("--out"))),
                     ("--h38", lambda: run_h38(arg("--out"))), ("--h37", lambda: H37["run_h37"](arg("--out"))),
                     ("--g36", lambda: H36["run_g36"](arg("--out"))), ("--snd", lambda: H36["run_snd"](arg("--out"))),
                     ("--till", lambda: H35["run_till"](arg("--out"))), ("--start", lambda: run_start38(arg("--out"), arg("--start"), arg("--which"))),
                     ("--audit", lambda: H["run_audit"](arg("--out")))):
        if flag in sys.argv:
            try:
                fn()
            except SystemExit:
                raise
            except Exception:
                import traceback
                traceback.print_exc()
                sys.exit(1)
            return
    for f_ in (JAR, J37, AR26, H36["FI6_SRC"], H35["CO_SRC"]):
        assert os.path.isfile(f_), f_
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    for sub in ("tmp", "packs", "players"):
        os.makedirs(os.path.join(SCRATCH, sub), exist_ok=True)
    shutil.copyfile(H35["CO_SRC"], H36["CO_JAR"])
    shutil.copyfile(H36["FI6_SRC"], H36["FI_JAR"])
    for f_ in glob.glob(os.path.join(H35["LIVE_PLAYERS"], "*.json")):
        shutil.copyfile(f_, os.path.join(SCRATCH, "players", os.path.basename(f_)))
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    only = arg("--only")
    want = (lambda x: not only or x in only.split(","))
    try:
        if want("assets"):
            run_assets38()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("compare", "--compare38"), ("h38", "--h38"), ("h37", "--h37"), ("g36", "--g36"),
                            ("snd", "--snd"), ("till", "--till")):
            if not want(label):
                continue
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        if want("life"):
            n0 = len(H37["FAILS"])
            H37["run_l35"](env)
            for f_ in H37["FAILS"][n0:]:
                FAILS.append("L35: " + f_)
            OKS[0] += H37["OKS"][0]
        if want("start"):
            res = {}
            for which in ("old", "new"):
                home = os.path.join(SCRATCH, "live-" + which)
                shutil.copytree(H35["LIVE_DIR"], home)
                out = os.path.join(SCRATCH, "start-%s.json" % which)
                pr = child(env, "--start", home, "--which", which, "--out", out)
                check(pr.returncode == 0, "D/%s: the child exited cleanly" % which)
                res[which] = take(out, "start-" + which)
            print("D. live Skyy_SkyyGear copied twice (read-only source %s)" % H35["LIVE_DIR"])
            if res.get("old") and res.get("new"):
                check(res["old"]["cfg"] == res["new"]["cfg"], "D: 0.3.8 starts the live copy to exactly the config.properties 0.3.7 writes (no row, no one-time update)")
                a_ = res["old"]["fresh"].split("\n")[1:]
                b_ = res["new"]["fresh"].split("\n")[1:]
                check(a_ == b_, "D: a FRESH default file is 0.3.7's (no new row): %s" % [l_ for l_ in b_ if l_ not in a_][:3])
                fo = sorted(f for f in os.listdir(os.path.join(SCRATCH, "live-old")) if not f.startswith("config-history"))
                fn_ = sorted(f for f in os.listdir(os.path.join(SCRATCH, "live-new")) if not f.startswith("config-history"))
                check(fo == fn_, "D: the same files after the starts: %s / %s" % (fo, fn_))
        if want("audit"):
            outa = os.path.join(SCRATCH, "audit.json")
            pa = child(env, "--audit", "--out", outa)
            check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
            if os.path.isfile(outa):
                a = json.load(open(outa))
                check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
                print("AA. engine-access audit: %d references in %d classes, 0 refused" % (a["refs"], a["classes"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
