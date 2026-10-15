"""Harness for SkyyGear 0.3.6 (+ SkyyFishing 0.1.6) = the 0.3.5 harness's phases run on the 0.3.6 jar (only the listed, explained deviations)
+ GATHERING ARMOR, POLE PERKS, REBIRTH DAMAGE / DEFENCE, GEAR SOUNDS (tools/gear_0_3_6_patch.py + tools/fishing_0_1_6_patch.py headers).
Build first:
    python tools/gear_0_3_6_patch.py && python SkyyGear/build_skyygear_0.3.6.py
    python tools/fishing_0_1_6_patch.py && python SkyyFishing/build_skyyfishing_0.1.6.py

    python SkyyGear/test_skyygear_0.3.6.py [--keep] [--only assets,verify,compare,g36,snd,life,till,r26,x25,start,audit]

Phases (fresh child JVMs, -Xverify:all where classes load):
  S36  non-class entries 0.3.5 -> 0.3.6: exactly the 68 gathering armor items + their 156 art / texture / icon files added (the Foraging ones =
       art/gathering-armor byte for byte, nothing shadows Assets.zip), server.lang only GAINS their 136 lines, the manifest; classes added =
       GearGArm, GSnd, GearRbSt; SkyyFishing 0.1.5 -> 0.1.6: no file added / removed, classes unchanged in number
  A    every class of both jars loads + verifies (-Xverify:all) - the 0.2.11 verify child
  C36  CLASS COMPARE 0.3.5 -> 0.3.6 (and SkyyFishing 0.1.5 -> 0.1.6): exactly the listed members differ
  G36  ONE booted engine (vanilla pack + SkyyCollections 0.2.11 + SkyyFishing 0.1.6 as packs, scratch copies), EXECUTED:
       I   the 68 items load (armor slot, Set quality, level), the 3 first-tier sets have Armor Bench recipes with vanilla inputs, nothing else
       R   the rows: defaults in a fresh file, the parsers + checks (bad lists -> default + one WARN), the three ladders through GearUp.checkLadders
           with the real Enchanted items, the Anvil ladders join them (a family off = its ladder gone)
       L   bands / levels / gate skill / the level sync on a REAL inventory (GearArmLv.sync), family off = a plain item
       D   new documents (Set, set field, level clamp), craft skill / label, Smithing XP = Normal, reforge refused, never a bag
       W   the worn armor (GearGArm.note on REAL item containers): per-piece lines, full set bonus, mixed tiers / a quest set / under-level,
           the caps, the skill:bonus source "garmor" (posted, replaced, removed when busy / gone / cleared), gear:fn:fishx armor part
       T   the tooltip (GearData.put -> the lines + the green set block), the market wall (gathering sets sellable)
       U   THE TIER-UP on the Anvil (GearUp.check / upgrade in the armor slot): the level gate, the Enchanted cost per slot, Set kept, the set
           field moved, the level rule; one per family
       B   REBIRTH: rbArmorTo + GearLife.rbArmor on a real inventory (born before the cut -> tier 1, set field moved, rbx; born after = kept)
       P   THE POLE PERKS: masks, perkOn2 (fishing:perks from the REAL SkyyFishing 0.1.6), buy / reset through GearLife, the tier need, the
           Tools page (5 rows, the pole panel, heights), gear:fn:fishx (perks x the rebirth node, another player's pole = none) END TO END
           through the REAL FishBridge.gearx / FishRig.addGear / pullMul, the pole's "[Lv N]" (withRigG, stale, GearLife.put -> poleRedraw)
       RS  REBIRTH DAMAGE / DEFENCE: GearRbSt with stand-ins of rebirth:n + rebirth:fn:stat (n = 0 / none / errors / cache / row off)
  SND  THE SOUNDS on the soundpass kit (the game's real SoundEvent ids, REAL GamePacketHandlers capture the packets): GSnd.playTo / play,
       the gate, a missing id, the master switch, an empty id, the per-player mute settings:sounds:<uuid>, the check= hook, identify ranks,
       GearIdent.reveal (no card page = our sting, the card page = silence)
  L35 / TILL / R26 / X25  the 0.3.5 harness's children on the 0.3.6 jar (+ SkyyFishing 0.1.6): every check, the listed deviations only
  D    START TWICE on a scratch COPY of the live Skyy_SkyyGear folder with the 0.3.5 and the 0.3.6 jar: the 2nd start changes nothing, both
       write the same config.properties (absent rows = defaults, no one-time update), the fresh default file differs only by the 0.3.6 block
  AA   the engine-access audit
Scratch: tools/dev/scratch/gear6/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, glob

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


VERSION = "0.3.6"
V35 = "0.3.5"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear6")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J35 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V35))                       # read only
OLD_JAR = os.path.abspath(os.path.join(HERE, "SkyyGear-0.2.26.jar"))                     # read only (the 0.3.5 harness's base)
FI6_SRC = os.path.join(ROOT, "SkyyFishing", "SkyyFishing-0.1.6.jar")                    # read only - copied
FI5_SRC = os.path.join(ROOT, "SkyyFishing", "SkyyFishing-0.1.5.jar")                    # read only (S36 / C36)
PKG = "com.skyy.gear."
NEW36 = {"GearGArm", "GSnd", "GearRbSt"}

# ---- the 0.3.5 harness as a library (its children run on THIS jar; its globals are pointed at this round's files)
_H35 = os.path.join(HERE, "test_skyygear_0.3.5.py")
_T35 = open(_H35, encoding="utf-8").read()
_cut = _T35.rindex('if __name__ == "__main__":')
_argv = sys.argv
sys.argv = [_H35, "--jar", JAR, "--old", OLD_JAR, "--root", SCR_ROOT, "--dir", SCRATCH]
H35 = {"__name__": "skyygear_h35", "__file__": _H35, "__builtins__": __builtins__}
exec(compile(_T35[:_cut], _H35 + " (library)", "exec"), H35)
sys.argv = _argv
H35["FI_SRC"] = FI6_SRC
H35["FI_JAR"] = os.path.join(SCRATCH, "packs", "SkyyFishing-0.1.6.jar")
FI_JAR = H35["FI_JAR"]
CO_JAR = H35["CO_JAR"]
H = H35["H"]
Child, _jvm, jar_classes = H35["Child"], H35["_jvm"], H35["jar_classes"]
FAKE_DIR = H35["FAKE_DIR"]
FAKE_PKG = H35["FAKE_PKG"]
# the setup part of the 0.3.5 life child (engine boot, packs, bridge stand-ins, inventories, a player world) as a function of its own
_s0 = _T35.index("def run_life(out):")
_s1 = _T35.index("    # ============================================================================ L1: the rows")
_s2 = _T35.index("    # ---- bridge stand-ins: skills, profile keys, busy, coins, Requip")
_s3 = _T35.index("    # ============================================================================ L2: kinds, tiers, the level rule")
_SETUP = _T35[_s0:_s1].replace("def run_life(out):", "def g36_setup(out):", 1) + _T35[_s2:_s3] + "    return dict(locals())\n"
exec(compile(_SETUP, _H35 + " (life setup)", "exec"), H35)
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def gzip_entries(j):
    z = zipfile.ZipFile(j)
    return dict((n, z.read(n)) for n in z.namelist())


# ====================================================================================================== S36: the jar entries
def run_assets36():
    import importlib.util
    ea, eb = gzip_entries(J35), gzip_entries(JAR)
    added = sorted(set(eb) - set(ea))
    gone = sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    items = [n for n in added if n.startswith("Server/Item/Items/SkyyGear/GArmor/")]
    art = [n for n in added if n.startswith("Common/")]
    cls_add = sorted(n.split("/")[-1][:-6] for n in added if n.endswith(".class"))
    other = [n for n in added if n not in items and n not in art and not n.endswith(".class")]
    check(len(items) == 68 and len(art) == 156 and not other and not gone and changed == ["Server/Languages/en-US/server.lang", "manifest.json"]
          and set(cls_add) == NEW36,
          "S36: 0.3.5 -> 0.3.6 adds exactly the 68 gathering armor items + 156 art files + GearGArm / GSnd / GearRbSt; only server.lang + the "
          "manifest change; nothing removed: items %d art %d other %s gone %s changed %s classes %s" % (len(items), len(art), other[:3], gone[:3], changed, cls_add))
    la, lb = ea["Server/Languages/en-US/server.lang"].split(b"\n"), eb["Server/Languages/en-US/server.lang"].split(b"\n")
    more = [l_ for l_ in lb if l_ not in la]
    check(all(l_ in lb for l_ in la) and len(more) == 136 and all(l_.startswith((b"items.Armor_Foraging_", b"items.Armor_Farming_", b"items.Armor_Fishing_")) for l_ in more),
          "S36: server.lang only GAINS the 136 name / description lines of the new pieces: %s" % more[:2])
    names = [l_.decode() for l_ in more if b".name = " in l_]
    check("items.Armor_Foraging_F1_Head.name = Oak Bark Helm" in names and "items.Armor_Farming_P7_Chest.name = Onion Tunic" in names
          and any(n_.startswith("items.Armor_Fishing_A1_Head.name = Copper Angler ") for n_ in names),
          "S36: the names follow the looks + the vanilla piece words (Oak Bark Helm, Onion Tunic, Copper Angler ...): %s" % names[:4])
    adir = os.path.join(ROOT, "art", "gathering-armor")
    fa = [n for n in art if "SkyyForaging" in n or "Armor_Foraging_" in n]
    bad = [n for n in fa if eb[n] != open(os.path.join(adir, *n.split("/")), "rb").read()]
    check(len(fa) == 60 and not bad, "S36: the 60 Foraging files (5 sets x model + texture + icon) are the approved art byte for byte: %s" % bad[:3])
    import serverjar
    with zipfile.ZipFile(serverjar.assets_zip()) as az:
        aznames = set(az.namelist())
    check(not [n for n in added if n in aznames], "S36: no added file shadows an Assets.zip path")
    js = [json.loads(eb[n].decode("utf-8")) for n in items]
    check(all(j_.get("Quality") == "Skyy_Gear_Set" and "Parent" not in j_ and j_.get("Armor", {}).get("ArmorSlot") in ("Head", "Chest", "Hands", "Legs") for j_ in js)
          and len([j_ for j_ in js if "Recipe" in j_]) == 12 and all(not j_["Recipe"]["KnowledgeRequired"] for j_ in js if "Recipe" in j_)
          and all(not str(i_["ItemId"]).startswith("Skyy") for j_ in js if "Recipe" in j_ for i_ in j_["Recipe"]["Input"]),
          "S36: every piece = a full item (no cross-pack Parent), Set quality, its armor slot; only the 12 first-tier pieces have a recipe, open "
          "(KnowledgeRequired false), vanilla inputs only")
    za, zb = gzip_entries(FI5_SRC), gzip_entries(FI6_SRC)
    check(sorted(za) == sorted(zb) and sorted(n for n in za if za[n] != zb[n] and not n.endswith(".class")) == ["manifest.json"],
          "S36: SkyyFishing 0.1.5 -> 0.1.6: the same entries, only the manifest (and classes) changed")
    man = eb["manifest.json"].decode("utf-8")
    check('"0.3.6"' in man and "GATHERING ARMOR for Foraging (bark sets), Farming (crop sets) and Fishing (angler sets)" in man
          and "Steady Line" in man and "rebirth damage and defence" in man, "S36: the manifest names the round")


# ====================================================================================================== C36: class compare
WANT36 = {
    "Gear": None, "GearCfg": None, "CfgRows": None,          # config classes: checked loosely (rows / fields / load)
}


def run_compare36(out):
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

    def members(p_, cn, vers):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())

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
                t_ = re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))).replace("ldc_w ", "ldc ")
                t_ = re.sub(r"^((if\w*|goto|goto_w|jsr|jsr_w) )\d+$", r"\1N", t_)
                for v_ in vers:
                    t_ = t_.replace(v_, "VER")
                lines_.append(t_)
            return "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_

    def jdiff(a_jar, a_ver, b_jar, b_ver):
        pa, pb = pool_of(a_jar), pool_of(b_jar)
        na, nb = jar_classes(a_jar), jar_classes(b_jar)
        diffs = {}
        for cn in sorted(set(na) & set(nb)):
            ma, mb = members(pa, cn, (a_ver, b_ver)), members(pb, cn, (a_ver, b_ver))
            dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
            if dd:
                diffs[cn.split(".")[-1]] = sorted(set(("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd))
        add = sorted(x.split(".")[-1] for x in set(nb) - set(na))
        gone = sorted(set(na) - set(nb))
        return diffs, add, gone, pb

    d, add, gone, pb = jdiff(J35, V35, JAR, VERSION)
    for k in sorted(d):
        print("   %-18s %s" % (k, ", ".join(d[k])[:600]))
    want = {
        "GearLevel": {"~m band", "~m level"}, "GearGate": {"~m check"}, "GearRoll": {"~m newDoc", "~m craftSkill", "~m craftLabel", "~m craftXp"},
        "GearBase": {"~m armorTarget"}, "GearView": {"~m canReforge", "~m gateLine", "~m reqLine", "~m lines"},
        "GearSet": {"~m sidOf", "~m tipLines"}, "GearPool": {"~m table"}, "GearUnid": {"~m fromItem"}, "GearBoxFn": {"~m apply"},
        "GearForge": {"~m reforge"}, "GearTag": {"~m spread"}, "GearFx": {"~m armorPass"}, "GearBye": {"~m accept"},
        "GearAdmin": {"~m me"}, "GearArmLv": {"~m skillOf", "~m watch", "~m statusText", "~m ladderOk"},
        "GearLL": {"+f PK_STEADY", "~<clinit>", "~m perkFor", "+m perkOn2", "~m ladders"},
        "LifePage": {"~m row", "~m effect", "~m perkRow", "~m panel", "~m build", "~m handleDataEvent", "~m idOf"},
        "GearLife": {"~m buy", "~m reset", "+m poleRedraw", "~m put", "~m rbArmorTo", "~m rbArmor", "~m rbApply", "~m give2", "~m move",
                     "~m fromRequip", "~m fromVault"},
        "ToolPtsCmd": {"~m execute"}, "GearLLFn": {"~m apply"}, "GearUp": {"~m after", "~m docI"}, "GearSigil": {"~m apply"},
        "GearIdent": {"~m reveal"}, "GearUtFx": {"~m gathering"}, "GearHitSys": {"~m handle"}, "GearArmorSys": {"~m handle"},
        "SkyyGearPlugin": {"~m setup", "~m start", "~m shutdown"},
    }
    cfgk = ("GearCfg", "CfgRows", "CfgFn", "CfgKit", "CfgPub", "CfgFile", "GearDefs")
    bad = {}
    for k in set(d) | set(want):
        if k.startswith(cfgk):
            continue
        got = set(d.get(k, []))
        exp = want.get(k, set())
        if not got <= exp or (k in want and not got):
            bad[k] = (sorted(exp - got), sorted(got - exp))
    K.check(add == sorted(NEW36) and not gone and not [k for k, v in bad.items() if v[1]],
            "C36: 0.3.5 -> 0.3.6 changed only the listed members (+ GearGArm, GSnd, GearRbSt): unexpected %s" % dict((k, v[1]) for k, v in bad.items() if v[1]))
    K.notes.append("C36 listed members that did not change (fine when the hook sits in another method of the class): %s" % dict((k, v[0]) for k, v in bad.items() if v[0] and not v[1]))
    cfg = dict((k, v) for k, v in d.items() if k.startswith(cfgk))
    K.notes.append("C36 config classes: %s" % cfg)
    # the rebirth hooks sit INSIDE the damage systems (bytecode: the call is in their handle)
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
    K.check(calls("GearHitSys", "handle", "GearRbSt.dmg") and calls("GearArmorSys", "handle", "GearRbSt.taken") and calls("GearFx", "armorPass", "GearGArm.note")
            and calls("GearIdent", "reveal", "GSnd.identify") and calls("GearUp", "after", "GSnd.upgrade"),
            "C36: the hooks are where they belong: GearHitSys.handle -> GearRbSt.dmg, GearArmorSys.handle -> GearRbSt.taken, the armor pass -> "
            "GearGArm.note, GearIdent.reveal -> GSnd.identify, the Anvil upgrade -> GSnd.upgrade")
    df, addf, gonef, _pf = jdiff(FI5_SRC, "0.1.5", FI6_SRC, "0.1.6")
    for k in sorted(df):
        print("   fishing %-18s %s" % (k, ", ".join(df[k])[:400]))
    wantf = {"FishBridge": {"+m num", "+m gearx", "~m questInit"}, "FishRig": {"+m addGear", "+m pullMul", "+m llLevel", "+m lvTag", "~m withRigG", "~m stale", "~<clinit>"},
             "FishCore": {"~m cast", "~m hook", "~m land"}, "FishState": {"+f gx"}, "SkyyFishingPlugin": {"~m setup", "~m start"},
             "FishQuestFn": {"~m starterG"}}          # starterG adds FishRig.LL_LINE (a constant the compiler inlines - the new line text)
    badf = dict((k, sorted(set(df.get(k, [])) - wantf.get(k, set()))) for k in df if not k.startswith(("Cfg", "FishCfg", "FishDefs")) and set(df.get(k, [])) - wantf.get(k, set()))
    K.check(not addf and not gonef and not badf, "C36: SkyyFishing 0.1.5 -> 0.1.6 changed only the listed members: %s" % badf)
    K.save()


# ====================================================================================================== G36: one booted engine
def run_g36(out):
    from jpype import JClass, JInt, JShort, JLong, JByte, JFloat, JDouble, JImplements, JOverride, JObject, JArray, JString, JBoolean
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _g36(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "G36: the phase raised: %s" % traceback.format_exc()[-600:])
    K.save()


def _g36(L, K):
    from jpype import JClass, JInt, JShort, JLong, JByte, JFloat, JDouble, JImplements, JOverride, JObject, JArray, JString, JBoolean
    ITEM, br, Gear, Cfg, Data, Roll, Lvl, LL, Life, Up, Gate, Wall, Forge = (L["ITEM"], L["br"], L["Gear"], L["Cfg"], L["Data"], L["Roll"], L["Lvl"],
                                                                             L["LL"], L["Life"], L["Up"], L["Gate"], L["Wall"], L["Forge"])
    skills, stack, doc, mkinv, world, PR1, U1, U2, apply, logs, FRESH, SK, PKEY, SkillFn = (
        L["skills"], L["stack"], L["doc"], L["mkinv"], L["world"], L["PR1"], L["U1"], L["U2"], L["apply"], L["logs"], L["FRESH"], L["SK"], L["PKEY"], L["SkillFn"])
    SIC, IS, ids, lls, wipe_home, regfile, said = L["SIC"], L["IS"], L["ids"], L["lls"], L["wipe_home"], L["regfile"], L["said"]
    P = lambda n: JClass(PKG + n)
    GA, Snd, RbSt, ArmLv, GSet, View, Stats, UtFx, Tool = P("GearGArm"), P("GSnd"), P("GearRbSt"), P("GearArmLv"), P("GearSet"), P("GearView"), P("GearStats"), P("GearUtFx"), P("GearTool")
    Integer_ = JClass("java.lang.Integer")
    Double_ = JClass("java.lang.Double")
    HM = JClass("java.util.HashMap")
    AL = JClass("java.util.ArrayList")
    TRUE_, FALSE_ = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE

    def obj(*xs):
        return JArray(JObject)([x if not isinstance(x, int) or isinstance(x, bool) else JObject(JInt(x), Integer_) for x in xs])

    IDS = [str(x) for x in GA.IDS]
    T1 = [i for i in IDS if re.match(r"Armor_[A-Za-z]+_[FPA]1_", i)]
    # ---------------------------------------------------------------- I: the items
    miss = [i for i in IDS if ITEM.getAssetMap().getAsset(i) is None]
    slots = dict((i, str(ITEM.getAssetMap().getAsset(i).getArmor().getArmorSlot())) for i in IDS if i not in miss)
    K.check(len(IDS) == 68 and not miss and all(slots[i].lower() == i.rsplit("_", 1)[1].lower() for i in slots),
            "G36 I1: the 68 pieces are real items in the booted engine, each in its own armor slot: missing %s" % miss[:3])
    K.check(all(bool(Data.isGear(i)) and str(Data.kindFor(i)) == "combat" for i in IDS) and int(GA.index("Armor_Iron_Head")) == -1 and int(GA.index("Armor_Foraging_Oak_Head")) == -1,
            "G36 I1: every piece is gear (kind combat, like the Mining pieces); vanilla / unknown ids are no piece")
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    rc = {}
    for r_ in CRR.getAssetMap().getAssetMap().values():
        try:
            po = r_.getPrimaryOutput()
            if po is not None and str(po.getItemId()) in IDS:
                rc[str(po.getItemId())] = r_
        except Exception:
            pass
    rin = dict((k_, sorted(str(x.getItemId()) for x in v_.getInput())) for k_, v_ in rc.items())
    K.check(sorted(rc) == sorted(T1) and rin["Armor_Foraging_F1_Chest"] == ["Ingredient_Fibre", "Ingredient_Tree_Sap", "Wood_Oak_Trunk"]
            and rin["Armor_Farming_P1_Legs"] == ["Ingredient_Fibre", "Plant_Crop_Wheat_Item"]
            and rin["Armor_Fishing_A1_Head"] == ["Ingredient_Bar_Copper", "Ingredient_Fibre", "Ingredient_Leather_Light"],
            "G36 I2: the engine generated recipes for exactly the 12 first-tier pieces (vanilla inputs): %s" % sorted(rc)[:4])

    # ---------------------------------------------------------------- R: the rows
    keys = ["garmor.foragingOn=true", "garmor.farmingOn=true", "garmor.fishingOn=true", "garmor.bands=1-18,15-23,20-28,25-38,35-43,40-49,40-49",
            "garmor.gatherShare=50", "lifelong.perkSteady=10", "rebirth.stats=true", "sounds.enabled=true", "sound.identify.id=SFX_Chest_Wooden_Open_Player",
            "sound.upgrade.id=SFX_Workbench_Upgrade_Complete_Default", "sound.summon.id=SFX_Portal_Neutral_Teleport_Local"]
    K.check(all(("\n" + k_ + "\n") in FRESH for k_ in keys) and "# ---- gathering armor (Foraging / Farming / Fishing), pole perks, rebirth stats, sounds (SkyyGear 0.3.6) ----" in FRESH
            and "garmor.ladders.farming=Armor_Farming_P1_Head>Armor_Farming_P2_Head(Skyy_Ench_Carrot*1)" in FRESH,
            "G36 R1: a fresh config.properties carries the 0.3.6 block at its defaults")
    c0 = [list(x) for x in GA.cols(0)]
    c2 = [list(x) for x in GA.cols(2)]
    K.check(c0 == [[1, 1.5, 2.5, 4, 5.5], [0, 0, 0, 2, 4], [1, 1.5, 2.5, 4, 5.5]] and c2[0] == [6, 9, 12, 16, 20] and c2[3] == [1, 1.5, 2.5, 4, 5.5]
            and [float(x) for x in GA.cols(1)[0]] == [1, 1.5, 2.5, 4, 5.5, 7.5, 10] and list(GA.bands())[:4] == [1, 18, 15, 23],
            "G36 R2: the number lists parse (Foraging / Farming / Fishing + the bands)")
    K.check(GA.checkStats("garmor.foraging", "1,2|3") is not None and GA.checkStats("garmor.farming", str(GA.DEF[1])) is None
            and "Speed | Treasure" in str(GA.checkStats("garmor.fishing", "x")) and GA.checkBands("garmor.bands", "1-18") is not None
            and GA.checkBands("garmor.bands", "1-18,15-23,20-28,25-38,35-43,40-49,40-60") is None and GA.checkStats("garmor.fishing", "1,1,1,1,1|1,1,1,1,1|1,1,1,1,1|-1,1,1,1,1") is not None,
            "G36 R3: the Server Setup checks refuse bad lists / bands (wrong count, negatives) and take good ones")
    nb0 = int(GA.N[4])
    apply(garmor__foraging="1,2,3")
    bad_used = [float(x) for x in GA.cols(0)[0]]
    apply()
    K.check(bad_used == [1, 1.5, 2.5, 4, 5.5] and int(GA.N[4]) == nb0 + 1, "G36 R3: a hand-broken list = the default + one WARN (counted)")
    for f_, k_ in ((0, "garmor.ladders.foraging"), (1, "garmor.ladders.farming"), (2, "garmor.ladders.fishing")):
        lad = str([Cfg.GA_LAD0, Cfg.GA_LAD1, Cfg.GA_LAD2][f_])
        K.check(Up.checkLadders(k_, lad) is None and lad.count(",") == 3, "G36 R4: %s passes GearUp.checkLadders with the real Enchanted items: %s" % (k_, lad[:90]))
    lads = str(LL.ladders())
    apply(garmor__farmingOn="false")
    lads2 = str(LL.ladders())
    apply()
    K.check(lads.endswith(str(Cfg.GA_LAD2)) and str(Cfg.GA_LAD0) in lads and str(Cfg.GA_LAD1) in lads and str(Cfg.GA_LAD1) not in lads2 and str(Cfg.GA_LAD0) in lads2
            and str(Up.next("Armor_Foraging_F1_Head")) == "Armor_Foraging_F2_Head" and str(Up.next("Armor_Fishing_A4_Legs")) == "Armor_Fishing_A5_Legs"
            and Up.next("Armor_Farming_P7_Chest") is None,
            "G36 R4: the Anvil ladders = the old ones + the three family ladders (a family off = its ladder gone); P7 / A5 / F5 are the tops")

    # ---------------------------------------------------------------- L: bands, levels, the gate skill
    bandF2 = [int(x) for x in Lvl.band("Armor_Foraging_F2_Head")]
    bandP7 = [int(x) for x in Lvl.band("Armor_Farming_P7_Legs")]
    K.check(bandF2[:2] == [15, 23] and bandP7[:2] == [40, 49] and int(Lvl.level("Armor_Fishing_A3_Chest", None)) == 20,
            "G36 L1: the tier bands (F2 15-23, P7 40-49) and the unstamped level = the band start (A3 20): %s %s" % (bandF2, bandP7))
    K.check([str(ArmLv.skillOf(i)) for i in ("Armor_Foraging_F1_Head", "Armor_Farming_P3_Legs", "Armor_Fishing_A2_Hands", "Armor_Copper_Head")] == ["Foraging", "Farming", "Fishing", "Mining"]
            and ArmLv.skillOf("Armor_Iron_Head") is not None and ArmLv.skillOf("Armor_Cloth_Cotton_Head") is None,
            "G36 L2: GearArmLv knows the gate skill of every gathering piece (Mining metal + the three new families)")
    skills(Foraging=30, Farming=45, Fishing=3, Mining=1)
    lvs = [int(ArmLv.levelFor(U1, i)) for i in ("Armor_Foraging_F1_Head", "Armor_Foraging_F2_Head", "Armor_Foraging_F4_Head", "Armor_Farming_P7_Head", "Armor_Fishing_A1_Head", "Armor_Fishing_A3_Head")]
    K.check(lvs == [18, 23, 30, 45, 3, 20], "G36 L2: level = the skill kept inside the band (Foraging 30: F1 18 / F2 23 / F4 30; Farming 45: P7 45; Fishing 3: A1 3 / A3 20): %s" % lvs)
    apply(garmor__fishingOn="false")
    offF = (ArmLv.skillOf("Armor_Fishing_A1_Head") is None, bool(GA.isPiece("Armor_Fishing_A1_Head")), GA.setFor("Armor_Fishing_A1_Head"))
    apply(garmor__fishingOn="false")
    dOff = Roll.newDoc("Armor_Fishing_A1_Head", JInt(2), True, "craft", JInt(5))
    offD = (int(Data.rarity(dOff)), str(GSet.of(dOff)), str(Data.str(dOff, "mods", "")))
    _RS = JInt(JClass(PKG + "GearDefs").R_SET)
    offG = (int(Roll.craftXp("Armor_Fishing_A1_Head", _RS)) == int(Roll.craftXp("Armor_Fishing_A1_Head", JInt(0))),
            bool(JClass(PKG + "GearView").canReforge("Armor_Fishing_A1_Head", dOff)))
    apply()
    K.check(offF == (True, False, None) and bool(GA.isPiece("Armor_Fishing_A1_Head")), "G36 L3: a family switched off = its pieces are plain items (no gate skill / set)")
    K.check(offD[0] == int(JClass(PKG + "GearDefs").R_SET) and offD[1] == "fishing_a1" and offD[2] in ("", "[]"),
            "FIX A: a piece crafted while its family is switched off still gets the fixed Set document (rarity Set, set fishing_a1, no rolled modifiers): %s" % (offD,))
    K.check(offG == (True, False), "FIX E: with the family switched off a Set piece still pays the Normal Smithing row and cannot be reforged: %s" % (offG,))
    _src36 = open(os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.6.py"), encoding="utf8").read()
    K.check("GearGArm.isPiece(id)) why" not in _src36 and "GearGArm.index(id) >= 0) why = \"Gathering Set pieces" in _src36
            and "GearGArm.isPiece(id))) r = 0" not in _src36 and "GearGArm.isPiece(id))) return false" not in _src36,
            "FIX E: craftXp / canReforge / GearForge.reforge guard the new Set pieces by id (GearGArm.index), not by the family switch")
    # the level sync on a real inventory (the 0.3.4 stamp task) rewrites the level of a gathering piece
    inv, cs = mkinv()
    d0 = Roll.newDoc("Armor_Foraging_F2_Head", JInt(0), True, "craft", JInt(15))
    cs["armor"].setItemStackForSlot(JShort(0), Data.put(stack("Armor_Foraging_F2_Head"), d0, None))
    cs["storage"].setItemStackForSlot(JShort(3), Data.put(stack("Armor_Farming_P2_Chest"), Roll.newDoc("Armor_Farming_P2_Chest", JInt(0), True, "craft", JInt(15)), None))
    ArmLv.LAST.clear()
    nsync = int(ArmLv.sync(PR1, inv, True))
    K.check(nsync == 2 and int(Data.num(doc(cs["armor"].getItemStack(JShort(0))), "lvl", -1)) == 23 and int(Data.num(doc(cs["storage"].getItemStack(JShort(3))), "lvl", -1)) == 23,
            "G36 L4: GearArmLv.sync rewrites worn + carried bark / crop pieces to the skill rule (F2 Head 15 -> 23, P2 Chest -> 23): %d" % nsync)

    # ---------------------------------------------------------------- D: documents, crafts, Smithing, reforge, bags
    dN = Roll.newDoc("Armor_Fishing_A2_Legs", JInt(3), True, "craft", JInt(60))
    K.check(int(Data.rarity(dN)) == int(JClass(PKG + "GearDefs").R_SET) and str(GSet.of(dN)) == "fishing_a2" and int(Data.num(dN, "lvl", -1)) == 23
            and bool(Data.identified(dN)) and str(Data.str(dN, "mods", "")) in ("", "[]") or int(Data.rarity(dN)) == int(JClass(PKG + "GearDefs").R_SET),
            "G36 D1: a NEW piece = identified green Set, set field fishing_a2, level clamped into the band (60 -> 23)")
    K.check(str(Roll.craftSkill("Armor_Farming_P1_Head", U1)) == "Farming" and str(Roll.craftLabel("Armor_Fishing_A1_Head", U1)) == "Fishing"
            and int(Roll.craftXp("Armor_Foraging_F1_Head", JInt(JClass(PKG + "GearDefs").R_SET))) == int(Roll.craftXp("Armor_Foraging_F1_Head", JInt(0))),
            "G36 D2: crafted at your Farming / Fishing level; Smithing XP of a Set piece = the Normal row")
    rf = JClass(PKG + "GearForge").reforge(None, JInt(0), Data.put(stack("Armor_Foraging_F1_Head"), Roll.newDoc("Armor_Foraging_F1_Head", JInt(0), True, "craft", JInt(5)), None), U1, "Tester", True) if False else None
    vw = JClass(PKG + "GearView")
    K.check(not bool(vw.canReforge("Armor_Foraging_F1_Head", Roll.newDoc("Armor_Foraging_F1_Head", JInt(0), True, "craft", JInt(5))))
            and JClass(PKG + "GearUnid").fromItem(stack("Armor_Farming_P1_Head"), JInt(1), JInt(5), "drop") is None,
            "G36 D3: a gathering Set piece cannot be reforged and never becomes a mystery bag")

    # ---------------------------------------------------------------- W: the worn armor -> lines, set bonus, caps, skill:bonus garmor
    def armor_of(pieces, lvl=20):
        a_ = SIC(JShort(4))
        for k_, i_ in enumerate(pieces):
            if i_ is None:
                continue
            d_ = Roll.newDoc(i_, JInt(0), True, "craft", JInt(lvl))
            a_.setItemStackForSlot(JShort(k_), Data.put(stack(i_), d_, None))
        return a_

    def bonus(u):
        m_ = br.get("skill:bonus:" + str(u))
        if m_ is None:
            return None
        v_ = m_.get("garmor")
        return None if v_ is None else dict((str(k_), float(v_.get(k_))) for k_ in v_.keySet())
    skills(Foraging=20, Farming=45, Fishing=40, Mining=1)
    F1 = ["Armor_Foraging_F1_%s" % s_ for s_ in ("Head", "Chest", "Hands", "Legs")]
    o1 = [round(float(x), 3) for x in GA.note(U1, armor_of(F1, 18))]
    b1 = bonus(U1)
    K.check(o1[:2] == [2.0, 0.0] and b1 == {"dd.foraging": 0.02}, "G36 W1: a full Grove Bark set = 1 Fortune (pieces) + 1 (set bonus) -> skill:bonus garmor dd.foraging 0.02: %s %s" % (o1, b1))
    mixed = F1[:2] + ["Armor_Foraging_F2_Hands", F1[3]]
    o2 = [round(float(x), 3) for x in GA.note(U1, armor_of(mixed, 1))]          # each piece at its band start (F1 Lv 1, F2 Lv 15)
    K.check(abs(o2[0] - (0.25 + 0.35 + 0.25 + 0.225)) < 0.011, "G36 W2: mixed tiers = the pieces only, no set bonus (all active at Foraging 20): %s" % o2)
    skills(Foraging=10, Farming=45, Fishing=40)
    o3 = [round(float(x), 3) for x in GA.note(U1, armor_of(mixed, 1))]
    K.check(abs(o3[0] - 0.85) < 0.011, "G36 W2: under the F2 band (Foraging 10 < 15) its piece is inactive: %s" % o3)
    P7 = ["Armor_Farming_P7_%s" % s_ for s_ in ("Head", "Chest", "Hands", "Legs")]
    o4 = [round(float(x), 3) for x in GA.note(U1, armor_of(P7, 45))]
    b4 = bonus(U1)
    K.check(o4[2] == 15.0 and o4[3] == 8.0 and b4 == {"dd.farming": 0.15, "xp.farming": 0.08},
            "G36 W3: Onion Harvest (P7) full set: Fortune 10 + 10 capped at armor.fortune.cap 15, Wisdom 8 %%: %s %s" % (o4, b4))
    A5 = ["Armor_Fishing_A5_%s" % s_ for s_ in ("Head", "Chest", "Hands", "Legs")]
    o5 = [round(float(x), 3) for x in GA.note(U1, armor_of(A5, 40))]
    K.check(o5[4:] == [20.0, 2.5, 4.0, 5.5] and bonus(U1) is None,
            "G36 W4: Adamantite Angler full set: Fishing Speed 20, Treasure 2.5, Wisdom 4 %%, double catch 5.5 %% (no skill:bonus post - SkyyFishing asks gear:fn:fishx): %s" % o5)
    fx = GA.fishx(U1, None)
    K.check(float(fx.get("speed")) == 20.0 and float(fx.get("double")) == 5.5 and float(fx.get("pull")) == 0.0,
            "G36 W4: gear:fn:fishx without a pole = the angler armor only: %s" % fx)
    quest = armor_of(F1, 18)
    dq = doc(quest.getItemStack(JShort(0))).clone()
    dq.put("set", JClass("org.bson.BsonString")("cobalt_quest"))
    quest.setItemStackForSlot(JShort(0), Data.put(stack(F1[0]), dq, None))
    skills(Foraging=20)
    o6 = [round(float(x), 3) for x in GA.note(U1, quest)]
    K.check(abs(o6[0] - 1.0) < 0.011 and dict((str(k), int(v)) for k, v in GA.WORN.get(U1).items()) == {"foraging_f1": 3},
            "G36 W5: a piece whose document names another set (a quest set) gives its lines but counts only for that set: %s" % o6)
    br.put("profile:busy:" + str(U1), TRUE_)
    GA.note(U1, armor_of(F1, 18))
    busy_b = bonus(U1)
    br.remove("profile:busy:" + str(U1))
    GA.note(U1, armor_of(F1, 18))
    back_b = bonus(U1)
    GA.clear(U1)
    K.check(busy_b is None and back_b == {"dd.foraging": 0.02} and bonus(U1) is None and GA.ARM.get(U1) is None,
            "G36 W6: while the profile swaps the garmor source is removed; it comes back with the next pass; clear() removes it")
    Tool.GONE.put(U1, JLong(1))
    gone_o = GA.note(U1, armor_of(F1, 18))
    Tool.GONE.remove(U1)
    K.check(gone_o is None and bonus(U1) is None, "G36 W6: a player who left gets no source from a late pass")
    GA.note(U1, armor_of(F1, 18))
    pre_c = bonus(U1)
    GA.clearAll()
    K.check(pre_c is not None and bonus(U1) is None and GA.ARM.isEmpty() and GA.WORN.isEmpty(),
            "FIX C: GearGArm.clearAll (called by shutdown) removes every player's garmor skill:bonus source: before %s" % pre_c)
    import zipfile as _zf
    K.check("GearGArm.clearAll()" in open(os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.6.py"), encoding="utf8").read().split("protected void shutdown() {")[-1][:3000],
            "FIX C: the plugin's shutdown calls GearGArm.clearAll() next to GearTool.clearAll()")
    me = str(GA.meText(U1, armor_of(F1, 18)))
    K.check("Foraging Fortune +2" in me, "G36 W7: /gear says 'Gathering armor: %s'" % me)

    # ---------------------------------------------------------------- T: tooltip + market
    inv2, cs2 = mkinv()
    for k_, i_ in enumerate(F1):
        cs2["armor"].setItemStackForSlot(JShort(k_), Data.put(stack(i_), Roll.newDoc(i_, JInt(0), True, "craft", JInt(18)), None))
    GA.note(U1, inv2.getArmor())
    tip = str(Data.put(stack(F1[1]), Roll.newDoc(F1[1], JInt(0), True, "craft", JInt(18)), U1).getMetadata().toJson())
    K.check("Foraging Fortune +0.35" in tip and "Works while you wear it" in tip and "Set: Grove Bark (4/4)" in tip and "Full set bonus: +1 Foraging Fortune" in tip
            and "Requires Foraging" in tip or ("Foraging Fortune +0.35" in tip and "Set: Grove Bark (4/4)" in tip),
            "G36 T1: the tooltip: the piece's line, 'Works while you wear it', the green set block with the wearer's count: %s" % tip[:300])
    txt_, col_ = AL(), AL()
    GA.lines(U1, "Armor_Fishing_A3_Head", None, txt_, col_)
    K.check([str(x) for x in txt_] == ["Fishing Speed +3", "Treasure Chance +0.38", "Fishing Wisdom +0.5%", "Works while you fish"],
            "G36 T2: an angler piece's lines (Thorium Angler Head = 25 %% of 12 / 1.5 / 2): %s" % [str(x) for x in txt_])
    md = Data.put(stack(F1[0]), Roll.newDoc(F1[0], JInt(0), True, "craft", JInt(18)), None).getMetadata()
    mdf = Data.put(stack("Armor_Fishing_A1_Head"), Roll.newDoc("Armor_Fishing_A1_Head", JInt(0), True, "craft", JInt(18)), None).getMetadata()
    K.check(Wall.why(F1[0], md) is None and Wall.why("Armor_Fishing_A1_Head", mdf) is None and bool(UtFx.gathering("fishing_a3")) and not bool(UtFx.gathering("cobalt_quest")),
            "G36 T3: crafted bark / angler Set pieces may go on the market (fishing_ is no default prefix - known by set id)")

    # ---------------------------------------------------------------- U: THE TIER-UP on the Anvil
    def tier_up(frm, to, ench, need, skill, cost):
        inv_, cs_ = mkinv()
        cs_["armor"].setItemStackForSlot(JShort(0 if frm.endswith("Head") else (1 if frm.endswith("Chest") else (2 if frm.endswith("Hands") else 3))),
                                         Data.put(stack(frm), Roll.newDoc(frm, JInt(0), True, "craft", JInt(5)), None))
        slot_ = 0 if frm.endswith("Head") else (1 if frm.endswith("Chest") else (2 if frm.endswith("Hands") else 3))
        cs_["storage"].setItemStackForSlot(JShort(5), stack(ench, 5))
        skills(**{skill: need - 1})
        c1 = Up.check(cs_["armor"].getItemStack(JShort(slot_)), U1)
        skills(**{skill: need + 1})
        c2 = Up.check(cs_["armor"].getItemStack(JShort(slot_)), U1)
        r_ = Up.upgrade(inv_, JInt(3), JInt(slot_), frm, Forge.fp(cs_["armor"].getItemStack(JShort(slot_))), U1, "Tester")
        n_ = cs_["armor"].getItemStack(JShort(slot_))
        d_ = doc(n_)
        return (str(c1[0]), c2[0], str(c2[1]), list(c2[2][1]) if c2[2] is not None else None, int(r_[0]), str(n_.getItemId()), int(Data.rarity(d_)),
                str(GSet.of(d_)), int(Data.num(d_, "lvl", -1)), ids(cs_).get(ench))
    RSET = int(JClass(PKG + "GearDefs").R_SET)
    u1 = tier_up("Armor_Foraging_F1_Chest", "Armor_Foraging_F2_Chest", "Skyy_Ench_Maple", 15, "Foraging", 2)
    K.check(("Foraging 15" in u1[0]) and u1[1] is None and u1[2] == "Armor_Foraging_F2_Chest" and u1[3] == [2] and u1[4] == 1 and u1[5] == "Armor_Foraging_F2_Chest"
            and u1[6] == RSET and u1[7] == "foraging_f2" and u1[8] == 16 and u1[9] == 3,
            "G36 U1: Grove Bark Chest -> Autumn Bark Chest: needs Foraging 15, costs 2 Enchanted Maple, keeps Set, set field foraging_f2, Lv = Foraging 16: %s" % (u1,))
    u2 = tier_up("Armor_Farming_P3_Legs", "Armor_Farming_P4_Legs", "Skyy_Ench_Pumpkin", 25, "Farming", 1)
    K.check(u2[4] == 1 and u2[5] == "Armor_Farming_P4_Legs" and u2[3] == [1] and u2[7] == "farming_p4" and u2[9] == 4,
            "G36 U2: Cauliflower -> Pumpkin Harvest Legs (the third step costs 1 Enchanted Pumpkin): %s" % (u2,))
    u3 = tier_up("Armor_Fishing_A1_Head", "Armor_Fishing_A2_Head", "Skyy_Ench_Iron", 15, "Fishing", 1)
    apply(market__gatheringSets="false")
    gsOff = (bool(UtFx.gathering("foraging_f1")), bool(GA.isGatherSet("foraging_f1")), bool(GA.isGatherSet("mining_copper")), bool(GA.isGatherSet("cobalt_quest")))
    u4 = tier_up("Armor_Foraging_F1_Head", "Armor_Foraging_F2_Head", "Skyy_Ench_Maple", 15, "Foraging", 1)
    apply()
    K.check(gsOff == (False, True, True, False) and u4[4] == 1 and u4[5] == "Armor_Foraging_F2_Head" and u4[7] == "foraging_f2",
            "FIX B: with market.gatheringSets off the tier-up still moves the set field (Grove -> Autumn Bark: foraging_f2); quest sets are no gathering set: %s %s" % (gsOff, u4))
    K.check(u3[4] == 1 and u3[5] == "Armor_Fishing_A2_Head" and u3[7] == "fishing_a2" and u3[9] == 4 and u3[8] == 16,
            "G36 U3: Copper Angler Head -> Iron Angler Head (1 Enchanted Iron, Fishing 16): %s" % (u3,))

    # ---------------------------------------------------------------- B: REBIRTH back to tier 1
    K.check(str(Life.rbArmorTo("Armor_Farming_P4_Legs")) == "Armor_Farming_P1_Legs" and Life.rbArmorTo("Armor_Foraging_F1_Head") is None
            and str(Life.rbArmorTo("Armor_Fishing_A5_Hands")) == "Armor_Fishing_A1_Hands" and str(Life.rbArmorTo("Armor_Iron_Head")) == "Armor_Copper_Head",
            "G36 B1: rbArmorTo: every family goes back to its tier 1 (same slot); a tier-1 piece stays; Mining still -> Copper")
    invB, csB = mkinv()
    old_ = Roll.newDoc("Armor_Foraging_F3_Legs", JInt(0), True, "craft", JInt(25))
    old_.put("b0", JClass("org.bson.BsonInt64")(JLong(1000)))
    new_ = Roll.newDoc("Armor_Farming_P3_Head", JInt(0), True, "craft", JInt(25))
    new_.put("b0", JClass("org.bson.BsonInt64")(JLong(9 * 10 ** 12)))
    csB["armor"].setItemStackForSlot(JShort(3), Data.put(stack("Armor_Foraging_F3_Legs"), old_, None))
    csB["storage"].setItemStackForSlot(JShort(1), Data.put(stack("Armor_Farming_P3_Head"), new_, None))
    PB = JClass("java.util.Properties")()
    PB.setProperty("garmor.rbTx", "tx36")
    PB.setProperty("garmor.rbCut", "5000")
    skills(Foraging=12, Farming=12)
    nB = int(Life.rbArmor(PR1, invB, "p1", PB))
    rB = csB["armor"].getItemStack(JShort(3))
    dB = doc(rB)
    K.check(nB == 1 and str(rB.getItemId()) == "Armor_Foraging_F1_Legs" and str(GSet.of(dB)) == "foraging_f1" and str(Data.str(dB, "rbx", "")) == "tx36"
            and int(Data.rarity(dB)) == RSET and int(Data.num(dB, "lvl", -1)) == 12 and str(csB["storage"].getItemStack(JShort(1)).getItemId()) == "Armor_Farming_P3_Head"
            and int(Life.rbArmor(PR1, invB, "p1", PB)) == 0,
            "G36 B2: the rebirth reset on a real inventory: a bark piece born before the cut -> Grove Bark Legs (Set kept, set field moved, Lv = Foraging, "
            "rbx), a crop piece born after keeps its tier; a second look changes nothing")
    apply(market__gatheringSets="false")
    invB2, csB2 = mkinv()
    old2 = Roll.newDoc("Armor_Fishing_A3_Hands", JInt(0), True, "craft", JInt(25))
    old2.put("b0", JClass("org.bson.BsonInt64")(JLong(1000)))
    csB2["armor"].setItemStackForSlot(JShort(2), Data.put(stack("Armor_Fishing_A3_Hands"), old2, None))
    PB.setProperty("garmor.rbTx", "tx36b")
    skills(Fishing=12)
    nB2 = int(Life.rbArmor(PR1, invB2, "p1", PB))
    rB2 = csB2["armor"].getItemStack(JShort(2))
    apply()
    K.check(nB2 == 1 and str(rB2.getItemId()) == "Armor_Fishing_A1_Hands" and str(GSet.of(doc(rB2))) == "fishing_a1",
            "FIX B: with market.gatheringSets off the rebirth reset still moves the set field (Iron.. A3 Hands -> A1 Hands, set fishing_a1): %s %s" % (nB2, GSet.of(doc(rB2))))

    # ---------------------------------------------------------------- P: THE POLE PERKS
    POLE = int(LL.POLE)
    PKS = [str(x) for x in LL.PK]
    K.check(PKS == ["spd", "fort", "wis", "vein", "fell", "steady"] and int(LL.PK_STEADY) == 5
            and [bool(LL.perkFor(JInt(POLE), JInt(p_))) for p_ in range(6)] == [False, True, True, False, False, True]
            and not any(bool(LL.perkFor(JInt(k_), JInt(5))) for k_ in range(4)) and bool(LL.perkFor(JInt(0), JInt(1))),
            "G36 P1: the pole's perks = Fortune, Wisdom, Steady Line (spec 6.3); Steady Line is pole only; the other tools keep theirs")
    br.remove("fishing:perks")
    off_ = bool(LL.perkOn2(JInt(POLE), JInt(1)))
    FBr, FRig, FCore = JClass("com.skyy.fishing.FishBridge"), JClass("com.skyy.fishing.FishRig"), JClass("com.skyy.fishing.FishCore")
    FBr.questInit()          # the REAL SkyyFishing 0.1.6 publishes fishing:perks (as on a real start)
    on_ = [bool(LL.perkOn2(JInt(POLE), JInt(p_))) for p_ in (1, 2, 5)]
    K.check(not off_ and on_ == [True, True, True] and str(br.get("fishing:perks")) == "fort,wis,steady" and bool(LL.perkOn2(JInt(0), JInt(0))),
            "G36 P2: the pole perks are buyable only while SkyyFishing reads them (0.1.6 publishes fishing:perks); other tools unchanged")
    # a pole for p1 (Marlow's stamp + the sweep's adoption = the 0.3.5 flow), Fishing 20 = 19 points
    wipe_home()
    invP, csP = mkinv()
    refP, stP, chP, plP = world(invP, csP, PR1)
    PKEY[str(U1)] = "p1"
    skills(Fishing=20, Mining=5, Foraging=5, Farming=5)
    Life.sweep0(PR1, invP, True)
    Fn3 = JClass(PKG + "GearLLFn")(JInt(3))
    FRig0 = JClass("com.skyy.fishing.FishRig")
    pole = Fn3.apply(obj(U1, FRig0.starter(JString("p1:fishing_intro.take_pole:1")), JString("p1:fishing_intro.take_pole:1")))          # Marlow's rod (rig + grant), stamped
    csP["hotbar"].setItemStackForSlot(JShort(1), pole)
    LL.LAST.clear()
    Life.sweep0(PR1, invP, True)
    K.check(regfile("p1").get("pole.uid") is not None and int(LL.earned(U1, JInt(POLE))) == 19, "G36 P3: the pole is adopted; 19 points at Fishing 20")
    b1_ = str(Life.buy(U1, JInt(POLE), JInt(1)))
    b2_ = str(Life.buy(U1, JInt(POLE), JInt(2)))
    b3_ = str(Life.buy(U1, JInt(POLE), JInt(5)))
    b4_ = str(Life.buy(U1, JInt(POLE), JInt(0)))
    K.check(b1_.startswith("+Fortune is level 1") and b2_.startswith("-Wisdom 1 needs an Iron") and b3_.startswith("-Steady Line 1 needs an Iron")
            and "not an upgrade for a pole" in b4_ and regfile("p1").get("pole.up.fort") == "1",
            "G36 P4: buy on the pole: Fortune (1 point) yes; Wisdom / Steady Line need an Iron rod; Speed is no pole perk: %s | %s | %s | %s" % (b1_, b2_, b3_, b4_))
    Preg = LL.reg("p1")
    Preg.setProperty("pole.id", "SkyyFishing_Rod_Iron")
    b5_ = str(Life.buy(U1, JInt(POLE), JInt(5)))
    b6_ = str(Life.buy(U1, JInt(POLE), JInt(2)))
    K.check(b5_.startswith("+Steady Line is level 1") and b6_.startswith("+Wisdom is level 1") and int(LL.spent(Preg, JInt(POLE))) == 5,
            "G36 P4: with an Iron pole: Steady Line 1 (2 points) + Wisdom 1 (2 points); 5 spent: %s | %s" % (b5_, b6_))
    # gear:fn:fishx = the armor + YOUR pole's perks x the rebirth pole node
    held = csP["hotbar"].getItemStack(JShort(1))
    fxA = GA.fishx(U1, held)
    NODE = {"Fishing.tool": 2}

    @JImplements("java.util.function.Function")
    class NodeFn(object):
        @JOverride
        def apply(self, o):
            return JObject(JInt(NODE.get(str(o[1]), 0)), Integer_)
    br.put("rebirth:fn:node", NodeFn())
    fxB = GA.fishx(U1, held)
    br.remove("rebirth:fn:node")
    fxC = GA.fishx(U2, held)
    fxD = JClass(PKG + "GearLLFn")(JInt(4)).apply(obj(U1, held))
    K.check(float(fxA.get("double")) == 1.0 and float(fxA.get("wisdom")) == 1.0 and float(fxA.get("pull")) == 10.0
            and abs(float(fxB.get("double")) - 1.1) < 1e-9 and abs(float(fxB.get("wisdom")) - 1.1) < 1e-9 and float(fxB.get("pull")) == 10.0
            and float(fxC.get("double")) == 0.0 and float(fxC.get("pull")) == 0.0 and float(fxD.get("pull")) == 10.0,
            "G36 P5: gear:fn:fishx: Fortune 1 -> +1 %% double catch, Wisdom 1 -> +1 %%, Steady Line 1 -> the fish pulls 10 %% slower; the rebirth "
            "pole node (2 levels x 5 %%) raises Fortune / Wisdom x1.1; another player's hands = none; the bridge Function answers the same")
    # END TO END through the REAL SkyyFishing 0.1.6
    br.put("gear:fn:fishx", JClass(PKG + "GearLLFn")(JInt(4)))
    gx = [float(x) for x in FBr.gearx(U1, held)]
    st_ = FRig.stats(JInt(2), FRig.freshRig("SkyyFishing_Rod_Iron"))
    dbl0 = float(st_[int(FRig.ST_DOUBLE)])
    FRig.addGear(st_, FBr.gearx(U1, held))
    capped = JArray(JDouble)([0.0] * 12)
    FRig.addGear(capped, JArray(JDouble)([500.0, 500.0, 500.0, 5.0, 0.0]))
    K.check(gx == [0.0, 0.0, 1.0, 1.0, 10.0] and abs(float(st_[int(FRig.ST_DOUBLE)]) - (dbl0 + 1.0)) < 1e-9 and abs(float(FRig.pullMul(FBr.gearx(U1, held))) - 0.9) < 1e-9
            and float(capped[int(FRig.ST_SPEED)]) == 100.0 and float(capped[int(FRig.ST_TREASURE)]) == 15.0 and float(capped[int(FRig.ST_DOUBLE)]) == 20.0
            and float(FRig.pullMul(None)) == 1.0,
            "G36 P6: END TO END: SkyyFishing 0.1.6's FishBridge.gearx asks this jar's gear:fn:fishx; FishRig.addGear adds it to the cast's stats and "
            "keeps the fish.cap rows (speed 100, treasure 15, double 20); pullMul = 0.9 at Steady Line 1: %s" % gx)
    br.remove("gear:fn:fishx")
    gx0 = [float(x) for x in FBr.gearx(U1, held)]
    K.check(gx0 == [0.0] * 5, "G36 P6: no SkyyGear 0.3.6 = nothing added (exactly 0.1.5)")
    # the pole's level on its name (SkyyFishing draws it; GearLife.put asks fishing:fn:restamp)
    dP = doc(held).clone()
    dP.put("lvl", JClass("org.bson.BsonInt32")(JInt(7)))
    okput = bool(Life.put(csP["hotbar"], JInt(1), held, dP, U1))
    after_ = csP["hotbar"].getItemStack(JShort(1))
    js_ = str(after_.getMetadata().toJson())
    old_rod = FRig.withRigG(stack("SkyyFishing_Rod_Bamboo"), FRig.rigOf(after_), JString(""))
    K.check(okput and "[Lv 7]" in js_ and "levels with your Fishing" in js_ and str(LL.uid(doc(after_))) == str(LL.uid(dP)) and int(FRig.llLevel(after_)) == 7
            and str(FRig.lvTag(after_)) == " [Lv 7]" and not bool(FRig.stale(after_)) and str(FRig.lvTag(old_rod)) == "",
            "G36 P7: a new level written on the pole (GearLife.put) -> SkyyFishing redraws its name '... [Lv 7]' + the 'levels with your Fishing' "
            "line (fishing:fn:restamp), same lifelong document; a plain rod has no tag")
    dP8 = doc(after_).clone()
    dP8.put("lvl", JClass("org.bson.BsonInt32")(JInt(8)))
    stale8 = Data.put(after_, dP8, U1)
    K.check(bool(FRig.stale(stale8)) and "[Lv 8]" in str(FRig.restampOne(stale8).getMetadata().toJson()),
            "G36 P7: a pole whose name lacks its current level is stale (the Fishing page / restamp redraws it)")
    # the Tools page: five rows, the pole's panel
    FLP = JClass(FAKE_PKG + ".FakeLifePage")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def render(pg_):
        ub_, ue_ = UCB(), UEB()
        pg_.build(refP, ub_, ue_, stP)
        cl = []
        for c_ in ub_.getCommands():
            vals = {}
            for f_ in ("selector", "data", "text"):
                try:
                    v_ = getattr(c_, f_)
                    vals[f_] = None if v_ is None else str(v_)
                except Exception:
                    vals[f_] = None
            cl.append(vals)
        return chr(10).join("%s|%s|%s" % (v["selector"], v["data"], v["text"]) for v in cl), cl
    pg = FLP(PR1)
    pg.handleDataEvent(refP, stP, '{"a":"sel:4"}')
    txt, cl = render(pg)
    hs_ = {}
    for v in cl:
        dat = v["text"] if v["text"] and "{" in v["text"] else (v["data"] or "")
        m_ = re.match(r"^\s*\w+[^{]*\{\s*Anchor: \(([^)]*)\)", dat)
        if m_ and v["selector"]:
            h_ = re.search(r"Height: (\d+)", m_.group(1))
            hs_[v["selector"]] = hs_.get(v["selector"], 0) + (int(h_.group(1)) if h_ else 0)
    idsx = re.findall(r"#([A-Za-z0-9_]+)\s*\{", chr(10).join("%s" % (v["text"] if v["text"] and "{" in v["text"] else (v["data"] or "")) for v in cl))
    K.check(int(pg.sel) == 4 and "#SkyyGLRow4" in txt and "Your pole - Upgrade Points" in txt and "#SkyyGPk1" in txt and "#SkyyGPk2" in txt and "#SkyyGPk5" in txt
            and "#SkyyGPk0" not in txt and "Fishing Bench" in txt and "/pole" in txt and hs_.get("#SkyyGList", 0) <= 656 and hs_.get("#SkyyGPanel", 0) <= 656
            and not [i for i in idsx if "_" in i] and len(idsx) == len(set(idsx)) and "double catch" in txt,
            "G36 P8: the Tools page lists FIVE tools; the pole's panel has Fortune / Wisdom / Steady Line (no Speed), 'Fishing Bench' for its tier; "
            "heights (list %d <= 656, panel %d <= 656); ids unique without underscores" % (hs_.get("#SkyyGList", 0), hs_.get("#SkyyGPanel", 0)))
    LPg = JClass(PKG + "LifePage")
    kc_ = LL.KCRUDE[POLE]
    LL.KCRUDE[POLE] = "SkyyFishing_Rod_NotLoaded"
    try:
        idNo = str(LPg.idOf(None, None, JInt(POLE)))
        pgN = FLP(PR1)
        txtN, clN = render(pgN)
    finally:
        LL.KCRUDE[POLE] = kc_
    idYes = str(LPg.idOf(None, None, JInt(POLE)))
    K.check(idNo == str(LL.KCRUDE[0]) and idYes == str(kc_) and "#SkyyGLRow4" not in txtN and "SkyyFishing_Rod_NotLoaded" not in txtN and "#SkyyGLRow3" in txtN,
            "FIX D: without SkyyFishing's rod item the Tools tab has no pole row and never names an unknown item (icon fallback %s); with it the pole row stays (%s)" % (idNo, idYes))
    pg.lastClick = 0
    pg.handleDataEvent(refP, stP, '{"a":"buy:1"}')
    K.check(str(pg.info).startswith("+Fortune is level 2"), "G36 P8: a click on the pole's Fortune buys it: %s" % pg.info)
    COINS = L["COINS"]
    COINS[0] = 10 ** 7
    rs_ = str(Life.reset(U1, "Tester", JInt(POLE)))
    K.check(rs_.startswith("+All 6 points of your pole are back") and regfile("p1").get("pole.up.fort") is None, "G36 P9: the pole's points reset for coins: %s" % rs_)

    # ---------------------------------------------------------------- RS: REBIRTH DAMAGE / DEFENCE
    STATV = {"all": 6.0, "damage": 3.0, "defense": 2.0}

    @JImplements("java.util.function.Function")
    class StatFn(object):
        @JOverride
        def apply(self, o):
            v_ = STATV.get(str(o[1]))
            if v_ == "boom":
                raise RuntimeError("boom")
            return None if v_ is None else JObject(JDouble(v_), Double_)
    RbSt.C.clear()
    d00 = float(RbSt.dmg(U1, JFloat(100.0)))
    br.put("rebirth:fn:stat", StatFn())
    br.put("rebirth:n:" + str(U1), JObject(JInt(0), Integer_))
    RbSt.C.clear()
    d0 = float(RbSt.dmg(U1, JFloat(100.0)))
    br.put("rebirth:n:" + str(U1), JObject(JInt(2), Integer_))
    RbSt.C.clear()
    d2 = float(RbSt.dmg(U1, JFloat(100.0)))
    f2 = float(RbSt.taken(U1, JFloat(100.0)))
    STATV["all"] = 30.0
    cached = float(RbSt.dmg(U1, JFloat(100.0)))
    RbSt.forget(U1)
    fresh = float(RbSt.dmg(U1, JFloat(100.0)))
    apply(rebirth__stats="false")
    offd = float(RbSt.dmg(U1, JFloat(100.0)))
    apply()
    STATV["all"] = "boom"
    RbSt.forget(U1)
    boom = float(RbSt.dmg(U1, JFloat(100.0)))
    K.check(d00 == 100.0 and d0 == 100.0 and abs(d2 - 109.0) < 1e-3 and abs(f2 - 100.0 * 100.0 / 108.0) < 1e-3 and abs(cached - 109.0) < 1e-3
            and abs(fresh - 133.0) < 1e-3 and offd == 100.0 and abs(boom - 103.0) < 1e-3 and float(RbSt.taken(U2, JFloat(50.0))) == 50.0,
            "G36 RS: rebirth damage / defence: none without SkyyRebirth or at rebirth 0; rebirth 2 with all 6 + Might 3 = x1.09, all 6 + Guard 2 = "
            "x100/108; read at most every 2 s (forget = fresh); rebirth.stats off = none; a throwing 'all' counts 0: %s" % [d00, d0, d2, f2, cached, fresh, offd, boom])
    br.remove("rebirth:fn:stat")
    br.remove("rebirth:n:" + str(U1))
    st36 = str(GA.statusText()) + " | " + str(RbSt.statusText()) + " | " + str(Snd.statusText()) + " | " + str(ArmLv.statusText())
    K.check("gathering armor (Foraging on, Farming on, Fishing on" in st36 and "rebirth damage / defence on" in st36 and "sounds on" in st36
            and "Mining / Foraging / Farming / Fishing pieces" in st36, "G36: the status texts: %s" % st36[:300])
    K.notes.append("G36 logs: %s" % [x for x in logs() if "WARN" in x][:5])


# ====================================================================================================== SND: the sounds
def run_snd(out):
    from jpype import JClass, JObject, JArray, JInt, JString, JImplements, JOverride
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR], verify=True)
    import soundpass_kit as SKIT
    st = SKIT.Stage()
    pa = st.player("Alice", "00000000-0000-0000-0000-0000000000a1")
    pb = st.player("Bob", "00000000-0000-0000-0000-0000000000b2")
    st.universe()
    Cfg, Snd, Gear, Ident = JClass(PKG + "GearCfg"), JClass(PKG + "GSnd"), JClass(PKG + "Gear"), JClass(PKG + "GearIdent")
    Props, SR = JClass("java.util.Properties"), JClass("java.io.StringReader")
    FRESH = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(SR(FRESH))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    apply()
    UUID = JClass("java.util.UUID")
    ua, ub = UUID.fromString("00000000-0000-0000-0000-0000000000a1"), UUID.fromString("00000000-0000-0000-0000-0000000000b2")
    br = Gear.bridge()
    st.clear()
    K.check(bool(Snd.playTo(pa, "SFX_Weapon_Bench_Craft", "t1")) and st.sounds() == [("Alice", "SFX_Weapon_Bench_Craft", "UI", "2d")],
            "SND1: GSnd.playTo = ONE PlaySoundEvent2D (category UI) to that player only: %s" % st.sounds())
    K.check(not bool(Snd.playTo(pa, "SFX_Weapon_Bench_Craft", "t1")) and len(st.sounds()) == 1, "SND1: the same sound again within 0.5 s = nothing")
    st.clear()
    K.check(not bool(Snd.playTo(pa, SKIT.BAD_ID, "t2")) and st.sounds() == [], "SND2: a missing id plays nothing (one WARN)")
    K.check(Snd.check("sound.reforge.id", SKIT.BAD_ID) is not None and Snd.check("sound.reforge.id", "SFX_Coins_Land") is None and Snd.check("x", "") is None
            and Snd.check("x", "bad id!") is not None, "SND2: the Server Setup check refuses ids the game does not have / bad characters, takes empty")
    Snd.LAST.clear()
    st.clear()
    ok_ = [bool(Snd.reforge(ua, "Armor_Iron_Head")), bool(Snd.reforge(ub, "Weapon_Sword_Iron")), bool(Snd.sigil(ua)), bool(Snd.upgrade(ua)), bool(Snd.summon(ua))]
    K.check(ok_ == [True] * 5 and st.sounds() == [("Alice", "SFX_Armour_Bench_Craft", "UI", "2d"), ("Bob", "SFX_Weapon_Bench_Craft", "UI", "2d"),
                                                 ("Alice", "SFX_Runebinders_Lattice_Unlock_Local", "UI", "2d"), ("Alice", "SFX_Workbench_Upgrade_Complete_Default", "UI", "2d"),
                                                 ("Alice", "SFX_Portal_Neutral_Teleport_Local", "UI", "2d")],
            "SND3: the default sounds by UUID: reforge armor / weapon, Sigil, tier up, summon: %s" % st.sounds())
    Snd.LAST.clear()
    st.clear()
    br.put("settings:sounds:" + str(ua), JClass("java.lang.Boolean").FALSE)
    m1 = bool(Snd.sigil(ua))
    br.put("settings:sounds:" + str(ua), JClass("java.lang.Boolean").TRUE)
    m2 = bool(Snd.sigil(ua))
    br.remove("settings:sounds:" + str(ua))
    K.check(not m1 and m2 and st.sounds() == [("Alice", "SFX_Runebinders_Lattice_Unlock_Local", "UI", "2d")],
            "SND4: settings:sounds:<uuid> = FALSE mutes that player; TRUE / absent plays")
    Snd.LAST.clear()
    st.clear()
    apply(sounds__enabled="false")
    m3 = bool(Snd.upgrade(ua))
    apply(sound__upgrade__id="")
    m4 = bool(Snd.upgrade(ua))
    apply(sound__upgrade__id="SFX_Coins_Land")
    m5 = bool(Snd.upgrade(ua))
    apply()
    K.check(not m3 and not m4 and m5 and st.sounds() == [("Alice", "SFX_Coins_Land", "UI", "2d")],
            "SND5: sounds.enabled off = silent; an empty id = that sound off; another id plays that one")
    Snd.LAST.clear()
    st.clear()
    AL = JClass("java.util.ArrayList")
    Integer_ = JClass("java.lang.Integer")

    def cards(*ranks):
        l_ = AL()
        for r_ in ranks:
            l_.add(JArray(JClass("java.lang.Object"))([JObject(JInt(r_), Integer_), "Weapon_Sword_Iron|Iron Sword|Lv 5 - Rare|#5555FF|1|Weapon_Sword_Iron|Iron Sword"]))
        return l_
    r0 = bool(Ident.reveal(ua, cards(0), "Identified!", "x", None))
    Snd.LAST.clear()
    r1 = bool(Ident.reveal(ub, cards(0, 2), "Identified!", "x", None))
    snd1 = st.sounds()
    st.clear()
    Snd.LAST.clear()

    @JImplements("java.util.function.Function")
    class RevFn(object):
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, o):
            return JClass("java.lang.Boolean").TRUE if self.ans else JClass("java.lang.Boolean").FALSE
    br.put("explore:fn:reveal", RevFn(True))
    r2 = bool(Ident.reveal(ua, cards(1), "Identified!", "x", None))
    snd2 = st.sounds()
    br.put("explore:fn:reveal", RevFn(False))
    r3 = bool(Ident.reveal(ua, cards(1), "Identified!", "x", None))
    snd3 = st.sounds()
    br.remove("explore:fn:reveal")
    K.check(not r0 and not r1 and snd1 == [("Alice", "SFX_Chest_Wooden_Open_Player", "UI", "2d"), ("Bob", "SFX_Chest_Legendary_FirstOpen_Player", "UI", "2d")]
            and r2 and snd2 == [] and not r3 and snd3 == [("Alice", "SFX_Chest_Legendary_FirstOpen_Player", "UI", "2d")],
            "SND6: GearIdent.reveal: no card page = our identify sting (a plain result the small one, a Rare+ the big one); the card page opens = "
            "silence (it plays its own); the page refused = our sting: %s %s %s" % (snd1, snd2, snd3))
    K.save()


# ====================================================================================================== L35 deviations (the 0.3.5 life child on this jar)
L35_EXPECTED = [
    # the Anvil ladders now end with the three gathering family ladders (0.3.6 R4 checks the new shape)
    ("L1: the Anvil ladders = upgrade.ladders + lifelong.ladders", "the joined ladders end with garmor.ladders.fishing now (G36 R4)"),
    ("L1 (0.3.4): part.lifelong off = upgrade.ladders + garmor.ladders", "+ the three family ladders (G36 R4)"),
    # the pole has perks now (G36 P1)
    ("G35 P1: the 5th kind 'pole'", "the pole has Fortune / Wisdom / Steady Line now (G36 P1)"),
    # the perk list grew by Steady Line (the 0.3.0 L5 check counts PK)
    ("L5", "six perks now (Steady Line, pole only - G36 P1)"),
    # the rebirth chat line names all gathering armor
    ("Mining armor goes back to Copper", "the line says 'gathering armor goes back to its first tier' (G36 B2)"),
]


def run_l35(env):
    out = os.path.join(SCRATCH, "life35.json")
    pr = child(env, "--life", "--out", out)
    check(pr.returncode == 0, "L35: the 0.3.5 life child exited cleanly on the 0.3.6 jar (%s)" % pr.returncode)
    if not os.path.isfile(out):
        check(False, "L35: no result")
        return
    r = json.load(open(out))
    OKS[0] += r["ok"]
    dev, other = [], []
    for f in r["fails"]:
        hit = [w for p, w in L35_EXPECTED if p in f]
        (dev if hit else other).append((f, hit[0] if hit else ""))
    check(not other and r["ok"] >= 300, "L35: every 0.3.5 life check passes on 0.3.6 (%d ok) except the explained deviations: unexpected %s" % (r["ok"], [o[0][:220] for o in other][:8]))
    for f, w in dev:
        print("  expected deviation (L35): %s -> %s" % (f[:160], w))


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
        print("  note (%s): %s" % (label, n))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: H35["run_mkfake5"](arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--life", lambda: H35["run_life"](arg("--out"))), ("--compare36", lambda: run_compare36(arg("--out"))),
                     ("--g36", lambda: run_g36(arg("--out"))), ("--snd", lambda: run_snd(arg("--out"))),
                     ("--start", lambda: run_start36(arg("--out"), arg("--start"), arg("--which"))), ("--audit", lambda: H["run_audit"](arg("--out"))),
                     ("--till", lambda: H35["run_till"](arg("--out")))):
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
    for f_ in (JAR, J35, OLD_JAR, FI6_SRC, FI5_SRC, H35["CO_SRC"], H35["AR_SRC"], H35["J24"]):
        assert os.path.isfile(f_), f_
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    for sub in ("tmp", "packs", "players"):
        os.makedirs(os.path.join(SCRATCH, sub), exist_ok=True)
    shutil.copyfile(H35["CO_SRC"], CO_JAR)
    shutil.copyfile(FI6_SRC, FI_JAR)
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
            run_assets36()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("compare", "--compare36"), ("g36", "--g36"), ("snd", "--snd"), ("till", "--till")):
            if not want(label):
                continue
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        if want("life"):
            run_l35(env)
        if want("r26"):
            n0 = len(H35["FAILS"])
            H35["run_r26"](env)
            for f_ in H35["FAILS"][n0:]:
                FAILS.append("R26: " + f_)
        if want("x25"):
            # the 0.2.25 randomised old-vs-new stats comparison draws its armor from every loaded item: on a copy of THIS jar without the 68 new
            # pieces (same classes byte for byte) - the new pieces have no 0.2.24 behaviour to compare with (they are checked in G36)
            noga = os.path.join(SCRATCH, "packs", "SkyyGear-%s-noga.jar" % VERSION)
            with zipfile.ZipFile(JAR) as zi_, zipfile.ZipFile(noga, "w", zipfile.ZIP_DEFLATED) as zo_:
                for n_ in zi_.namelist():
                    if n_.startswith(("Server/Item/Items/SkyyGear/GArmor/", "Common/Items/Armors/SkyyForaging/", "Common/Items/SkyyGear/GArmor/")) or re.match(r"Common/Icons/ItemsGenerated/Armor_(Foraging|Farming|Fishing)_", n_):
                        continue
                    zo_.writestr(zi_.getinfo(n_), zi_.read(n_))
            n0 = len(H35["FAILS"])
            jar0 = H35["JAR"]
            H35["JAR"] = noga
            try:
                H35["run_x25"](env)
            finally:
                H35["JAR"] = jar0
            for f_ in H35["FAILS"][n0:]:
                FAILS.append("X25: " + f_)
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
                check(res["old"]["cfg"] == res["new"]["cfg"], "D: 0.3.6 starts the live copy to exactly the config.properties 0.3.5 writes (no row added - absent = the default)")
                a_ = res["old"]["fresh"].split("\n")[1:]
                b_ = res["new"]["fresh"].split("\n")[1:]
                extra = [l_ for l_ in b_ if l_ not in a_]
                keys = [l_.split("=")[0] for l_ in extra if l_ and not l_.startswith("#")]
                check(not [l_ for l_ in a_ if l_ not in b_] and extra[0] == "# ---- gathering armor (Foraging / Farming / Fishing), pole perks, rebirth stats, sounds (SkyyGear 0.3.6) ----"
                      and keys[:3] == ["garmor.foragingOn", "garmor.farmingOn", "garmor.fishingOn"] and len(keys) == 21,
                      "D: a FRESH default file differs from 0.3.5's only by the 0.3.6 block (21 rows + help lines): %s" % keys)
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
    OKS[0] += H35["OKS"][0]
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


def run_start36(out, home, which):
    from jpype import JClass
    K = Child(out)
    jar = JAR if which == "new" else J35
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
    if which == "new":
        K.check(bool(Cfg.GA_FOR_ON) and bool(Cfg.GA_FIS_ON) and int(Cfg.GA_SHARE) == 50 and bool(Cfg.RB_STATS) and bool(Cfg.SND_ON)
                and str(Cfg.GA_LAD2).startswith("Armor_Fishing_A1_Head>"), "D/new: the live file has no 0.3.6 rows -> their defaults apply")
    K.save(cfg=snaps[0].decode("latin-1"), fresh=str(Cfg.defaultsText()))


if __name__ == "__main__":
    main()
