"""Harness for SkyyGear 0.3.52 (Augments round A2: SOCKETS + ITEMS - tools/gear_0_3_52_patch.py header).
Build first:
    python tools/gear_0_3_52_patch.py && python SkyyGear/build_skyygear_0.3.52.py
    python SkyyGear/test_skyygear_0.3.52.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.51 jar is the compare base):
  S  static   the patch re-runs to identical bytes, line endings kept, ONE new class (GearAug), no new command / system; the jar's non-class
              files = 0.3.51's + the 120 augment items + 38 art files (fix round 3 M1: Swift / Sage ship), only manifest.json + server.lang changed; every item (Quality by tier,
              the Alchemy Bench recipe, the fuse chain), every lang line (tier tag first, GIVES / FITS / USE / HOW); tools/tier_tags.py rows;
              the fresh config file (27 augment rows, their defaults)
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.51 -> 0.3.52 (EXPECT below)
  E  engine   (the 0.2.11 harness's bare server boot: vanilla pack + THIS jar) - every new code path EXECUTED:
              V  the 120 augment items in the real Item store (Quality, MaxStack, recipe); no augment asset fails
              P  config: augParse / augCheck / augOr (defaults, a live edit, a bad line = the default + WARN), every text row's shape
              Q  pure: ent / code / idOf / name / tierHex / raw / added / ladderT / kindAt / base / slots (every rarity, weapon + armor + tools,
                 unidentified, part.augments off, aug.extraSlots lowered) / fits / plan (add, replace, fuse, lower refused, top refused, same refused,
                 not fitting, no slot) / docWith / carry / gives
              T  totals0: stat augments + armor element Defence summed with the rolled lines (rounded once), no augment = identical totals,
                 a non-fitting / past-the-slots entry counts nothing
              M  fix round 3 (M1): Swift / Sage - GearAug.manaOf (exact, fitting + inside the slots, part.augments off, a live aug.stat.Swift
                 edit), their first stats in totals0 (Speed / Magical Power), GearUtFx.manaWorn on a REAL armor container (active pieces only),
                 GearUtFx.pctKey / flatOf skip skyygear_mana + the other mods' % layers, GearUtFx.mpApply on a REAL EntityStatMap (% of the
                 FLAT max, steady with the Pets / Accessories / Skills Mana % layers on it, lowering waits for synced, 0 removes), and
                 GearUtFx.secondPass end to end (worn Swift + Sage -> skyygear_mana; part.augments / part.stats off -> removed)
              W  weap / power (socketed tiers, + 3 a rolled element line, Raw Elemental, + 5 Imbue), GearElem.pcts2 (the pet gate opens), a REAL
                 GearElem.split (element part + Poison + inf[8] Power, a fake classes:fn:imbue)
              H  GearAug.states on an ECS shim: a fake classes:fn:elemHit gets {attacker, victim UUID, power5, dealt parts, hit, heavy, world};
                 aug.states off / no Power / no bridge = nothing sent; gear:elemStates follows aug.states / elem.on (GearElem.onEdit)
              X  GearAug.apply on REAL inventories + fake bags (sacks:fn:count / take / put / commit): add (inventory), replace (bags; the old one
                 destroyed), fuse (one used), every refusal moves nothing, a short bag = everything back, a failing write = everything back,
                 a stack of 2 refused; counts exact; Smithing XP; addSlot (coins first, Smithing level, the cap) / removeSlot (empty added only)
              K  tools: toolFx + GearTool.stats of a lifelong pickaxe (Delver Power x, Prospector Fortune), GearLL.swingOf (Breaking Speed),
                 noteArmor / armFx (worn Mining armor tool kinds), GearTool.held's post
              U  the tooltip (GearView.lines: the AUGMENTS section, segments, "(no slot)", ELEMENT POWER) + plain(); Anvil > Augments: anAugPanel
                 built on REAL UICommandBuilders and walked like the client (every selector exists), the button text per plan, anAugDo (arm,
                 then the write), anAugSlotDo, the sub-tab row (anvilSub3), anRows / anFitsMode filter
  D  live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: every one-time update + load() twice; the second start
              changes nothing; the augment rows read their defaults (no line in the live file)
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the client drawing the Augments tab / the tooltip segments; the Alchemy Bench showing the 120 recipes in its
Misc tab; SkyyClasses 0.1.51 putting the states from a real hit (FIX checks: F1-F7 in S / Q / W / X / U, fix round 2 G1-G4 in U, fix round 3 M1 in S / Q / M); a socketed item surviving AH / trade / Vault / Requip / Wardrobe (spec X6); the
client's Mana bar showing the raised max.
Scratch: tools/dev/scratch/aug_a2/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.52"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "aug_a2", "harness")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.51.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_52_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.51.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
ADDED = ["GearAug"]
EXPECT = {          # the first run's dump, reviewed: the config rows / tables, GearAug's callers (totals0, split, the hit systems, the tool readers,
          # the merges, the tooltip, the Anvil page + its sub-tab row, setup / shutdown)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CfgRows1': ['~<clinit>'],
    'CfgRows2': ['~<clinit>'],
    'GearCfg': ['+f AUG_EA', '+f AUG_EA_T', '+f AUG_EP', '+f AUG_EP_T', '+f AUG_EW', '+f AUG_EW_T', '+f AUG_EXTRA', '+f AUG_ON', '+f AUG_POI', '+f AUG_POI_T', '+f AUG_SA', '+f AUG_SA_T', '+f AUG_SCALE', '+f AUG_SCALE_T', '+f AUG_SCOST', '+f AUG_SLV', '+f AUG_ST', '+f AUG_STATES', '+f AUG_ST_T', '+f AUG_SW', '+f AUG_SW_T', '+f AUG_V', '+f AUG_V0_T', '+f AUG_V10_T', '+f AUG_V11_T', '+f AUG_V12_T', '+f AUG_V1_T', '+f AUG_V2_T', '+f AUG_V3_T', '+f AUG_V4_T', '+f AUG_V5_T', '+f AUG_V6_T', '+f AUG_V7_T', '+f AUG_V8_T', '+f AUG_V9_T', '+f AUG_XP', '+f AUG_XP_T', '+m augAfter', '+m augCheck', '+m augI', '+m augNums', '+m augOr', '+m augParse', '+m augRead', '+m augShape', '~<clinit>', '~m apply', '~m defaultsText'],
    'GearElem': ['+m imbOnly', '+m pcts2', '~m forget', '~m note', '~m onEdit', '~m pcts', '~m split'],
    'GearHit': ['~m info', '~m weaponHit2'],
    'GearHub': ['+m anvilSub3'],
    'GearLL': ['~m harvOf', '~m invested', '~m swingOf'],
    'GearLeechSys': ['~m handle'],
    'GearLife': ['~m give2', '~m harvDoc', '~m harvDocAll', '~m mtDoc'],
    'GearMerge': ['~m docI'],
    'GearStats': ['~m totals0'],
    'GearTool': ['~m held', '~m mstats', '~m stats'],
    'GearTrueSys': ['~m handle'],
    'GearUtFx': ['+f MKEY', '+m manaWorn', '+m mpApply', '~m pctKey', '~m secondPass'],          # fix round 3 (M1): the augment Mana % modifier
    'GearView': ['~<clinit>', '~m lines'],
    'ReforgePage': ['+f anAgArm', '+f anAgF', '+f anAgKey', '+f anAgPick', '+f anAgSlot', '+f anAugM', '+m anAugDo', '+m anAugKey', '+m anAugPanel', '+m anAugReset', '+m anAugSlotDo', '~m anBuild', '~m anEvent', '~m anFitsMode', '~m anList', '~m anRows', '~m skyHde'],
    'SkyyGearPlugin': ['~m setup', '~m shutdown'],
}
U = "00000000-0000-0000-0000-000000000352"
KINDS = ["Brute", "Edge", "Precision", "Arcane", "Tempo", "Bulwark", "Warrior", "Swift", "Vital", "Sage", "Prospector", "Scholar", "Delver",
         "Earth", "Thunder", "Water", "Fire", "Air", "Poison"]
TOP = dict((k, 10 if k in ("Earth", "Thunder", "Water", "Fire", "Air") else 5) for k in KINDS)
LATER = ()          # fix F1 hid Swift / Sage; fix round 3 (M1, Skyy "Add them now"): every kind ships (the gear Mana key skyygear_mana)
IDS = ["Skyy_Aug_%s_%d" % (k, n) for k in KINDS if k not in LATER for n in range(1, TOP[k] + 1)]
QUAL = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
AUG_ROWS = ["part.augments", "aug.states", "aug.slots.weapon", "aug.slots.armor", "aug.slots.tool", "aug.extraSlots", "aug.slotLevel", "aug.slotCost",
            "aug.tierScale"] + ["aug.stat." + k for k in KINDS[:13] if k not in LATER] + ["aug.poison", "aug.elem.weapon", "aug.elem.power", "aug.elem.armor", "aug.xp"]


def aug_name(n):
    return n.startswith("Server/Item/Items/SkyyGear/Aug/") or n.startswith("Common/Items/SkyyGear/Aug/") or re.match(r"^Common/Icons/ItemsGenerated/Skyy_Aug_[A-Za-z]+\.png$", n)


def expected_nonclass(za, zb):
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    return sorted(eb - ea), sorted(n for n in ea & eb if za.read(n) != zb.read(n)), sorted(ea - eb)


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.52 - build script') and g.count('VERSION = "0.3.52"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 1), "S one new class (GearAug), no new system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    added, changed, gone = expected_nonclass(za, zb)
    K.eq(gone, [], "S no file removed")
    K.eq(changed, ["Server/Languages/en-US/server.lang", "manifest.json"], "S changed = manifest.json + server.lang")
    K.check(added and all(aug_name(n) for n in added), "S every added file is an augment file: %s" % [n for n in added if not aug_name(n)][:5])
    items = sorted(n for n in added if n.startswith("Server/Item/Items/"))
    K.eq(items, sorted("Server/Item/Items/SkyyGear/Aug/%s.json" % i for i in IDS), "S the 120 augment items (fix round 3 M1: Swift + Sage included)")
    K.eq(len(added) - len(items), 2 * (len(KINDS) - len(LATER)), "S 38 art files (a texture + an icon per kind, all 19)")
    bad = []
    for i in IDS:
        j = json.loads(zb.read("Server/Item/Items/SkyyGear/Aug/%s.json" % i))
        k, n = i.split("_")[2], int(i.split("_")[3])
        q = QUAL[(n - 1) // 2 if TOP[k] == 10 else n - 1]
        r = j["Recipe"]
        br = r["BenchRequirement"][0]
        ins = dict((x["ItemId"], x["Quantity"]) for x in r["Input"])
        if j["Quality"] != q or j["MaxStack"] != 64 or j["Icon"] != "Icons/ItemsGenerated/Skyy_Aug_%s.png" % k or br["Id"] != "Alchemybench" \
                or br["Categories"] != ["Alchemy_Potions_Misc"] or j["Texture"] != "Items/SkyyGear/Aug/Aug_%s.png" % k:
            bad.append((i, "item", j["Quality"], q))
        if TOP[k] == 10:
            want = ({"Ingredient_Crystal_Green": 2, "Ingredient_Lightning_Essence": 2, "Ingredient_Water_Essence": 2, "Ingredient_Fire_Essence": 2,
                     "Ingredient_Crystal_Cyan": 2}[[x for x in ins][0]] if n == 1 else 2)
            if (n == 1 and list(ins.values()) != [2]) or (n > 1 and ins != {"Skyy_Aug_%s_%d" % (k, n - 1): 2}):
                bad.append((i, "fuse recipe", ins, want))
        else:
            mat = [("Ingredient_Bar_Copper", 4), ("Skyy_Ench_Thorium", 1), ("Skyy_Ench_Cobalt", 1), ("Skyy_Ench_Adamantite", 1), ("Skyy_Ench_Mithril", 1)][n - 1]
            if len(ins) != 2 or ins.get(mat[0]) != mat[1]:
                bad.append((i, "recipe", ins))
    K.check(not bad, "S every item: Quality by tier, MaxStack 64, the kind's icon + texture, Alchemy Bench Misc; elemental T1 = 2 essence / crystal, "
            "T(n+1) = 2 x T(n); stat / Poison = 1 gem (Venom Sac) + 4 Copper Bars / 1 Enchanted zone metal: %s" % bad[:4])
    lang = zb.read("Server/Languages/en-US/server.lang").decode("utf-8")
    lb = []
    for i in IDS:
        k, n = i.split("_")[2], int(i.split("_")[3])
        rom = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"][n - 1]
        nm = [l for l in lang.splitlines() if l.startswith("items.%s.name = " % i)]
        ds = [l for l in lang.splitlines() if l.startswith("items.%s.description = " % i)]
        if nm != ["items.%s.name = %s Augment %s" % (i, k, rom)] or len(ds) != 1 or not ds[0].split(" = ", 1)[1].startswith("T%d Augment - %s (" % (n, k)) \
                or not all(s in ds[0] for s in ("GIVES", "FITS", "USE", "HOW", "Crafting > Anvil > Augments", "destroys the old augment")):
            lb.append(i)
    K.check(not lb, "S lang: '<Kind> Augment <Roman>', the description starts with its tier tag 'Tn Augment - <Kind> (...)' + GIVES / FITS / USE / HOW: %s" % lb[:3])
    K.check("coming later" not in lang and all(("Common/Items/SkyyGear/Aug/Aug_%s.png" % k) in added and ("Common/Icons/ItemsGenerated/Skyy_Aug_%s.png" % k) in added for k in ("Swift", "Sage")),
            "M1: Swift / Sage ship - their texture + icon, no 'coming later' note")
    sw5 = [l for l in lang.splitlines() if l.startswith("items.Skyy_Aug_Swift_5.description = ")]
    sg1 = [l for l in lang.splitlines() if l.startswith("items.Skyy_Aug_Sage_1.description = ")]
    K.check(len(sw5) == 1 and sw5[0].split(" = ", 1)[1].startswith("T5 Augment - Swift (stat)") and ">Speed</color>" in sw5[0] and "<b>+0.5</b>" in sw5[0]
            and ">Mana</color>" in sw5[0] and "<b>+2%</b>" in sw5[0] and "Combat armor" in sw5[0],
            "M1: Swift V's item text: tag first, GIVES Speed +0.5 + Mana +2%%, FITS Combat armor: %s" % sw5[:1])
    K.check(len(sg1) == 1 and sg1[0].split(" = ", 1)[1].startswith("T1 Augment - Sage (stat)") and ">Magical Power</color>" in sg1[0] and "<b>+0.6</b>" in sg1[0]
            and ">Mana</color>" in sg1[0] and "<b>+0.8%</b>" in sg1[0], "M1: Sage I's item text: Magical Power +0.6 (1.6 x 40 %%) + Mana +0.8%% (2 x 40 %%): %s" % sg1[:1])
    swj = json.loads(zb.read("Server/Item/Items/SkyyGear/Aug/Skyy_Aug_Swift_1.json"))
    sgj = json.loads(zb.read("Server/Item/Items/SkyyGear/Aug/Skyy_Aug_Sage_5.json"))
    K.check(dict((x["ItemId"], x["Quantity"]) for x in swj["Recipe"]["Input"]) == {"Rock_Gem_Zephyr": 1, "Ingredient_Bar_Copper": 4}
            and dict((x["ItemId"], x["Quantity"]) for x in sgj["Recipe"]["Input"]) == {"Rock_Gem_Sapphire": 1, "Skyy_Ench_Mithril": 1}
            and swj["Quality"] == "Common" and sgj["Quality"] == "Legendary", "M1: Swift I = Zephyr + 4 Copper Bars (Common), Sage V = Sapphire + Enchanted Mithril (Legendary)")
    tl_ = [l for l in lang.splitlines() if l.startswith("items.Skyy_Aug_Tempo_1.description = ")]
    K.check(len(tl_) == 1 and "Melee weapons (not bows, wands or staffs)" in tl_[0], "FIX F2: Tempo's FITS says melee weapons only: %s" % tl_[:1])
    pl_ = [l for l in lang.splitlines() if l.startswith("items.Skyy_Aug_Poison_1.description = ")]
    K.check(len(pl_) == 1 and "10 s" not in pl_[0] and "over a few seconds" in pl_[0], "FIX F6: the Poison item text has no fixed seconds: %s" % pl_[:1])
    bl_ = [l for l in lang.splitlines() if l.startswith("items.Skyy_Aug_Bulwark_1.description = ")]
    K.check(len(bl_) == 1 and "Fractions add up with your other gear lines" in bl_[0], "FIX F6: a stat augment says fractions add up with the kit")
    import importlib
    TT = importlib.import_module("tier_tags")
    K.check("Augment" in TT.OWN_LADDERS and sorted(TT.ids_in("augment")) == sorted(IDS) and all(TT.owner(i) == "SkyyGear" for i in IDS)
            and TT.tag_for("Skyy_Aug_Fire_10") == "T10 Augment" and TT.tag_for("Skyy_Aug_Brute_3") == "T3 Augment", "S tools/tier_tags.py: the Augment ladder, 120 rows owned by SkyyGear")
    K.check(tuple(TT.AUG_LATER) == () and len(TT.AUG_IDS) == 120 and len([i for i in TT.AUG_IDS if "_Swift_" in i or "_Sage_" in i]) == 10
            and TT.tag_for("Skyy_Aug_Swift_5") == "T5 Augment" and TT.tag_for("Skyy_Aug_Sage_1") == "T1 Augment", "M1: tier_tags.py holds the 10 Swift / Sage rows (120)")
    K.check(len(AUG_ROWS) == 27 and all(('("%s", ' % k) in g for k in AUG_ROWS), "S the 27 augment Server Setup rows are in the script")
    K.check('("aug.stat.Swift", ' in g and '("aug.stat.Sage", ' in g and g.count('"skyygear_mana"') == 1, "M1: the Swift / Sage Server Setup rows + the one Mana key")
    K.notes.append("S %d files added; jar %d -> %d bytes" % (len(added), os.path.getsize(OLD_JAR), os.path.getsize(jar)))
    K.save()


def run_compare52(out, jar, old_jar, pkg, expect, added, removed=()):
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
        json.dump(got, open(os.path.join(os.path.dirname(SCRATCH), "expect52.dump.json"), "w"), indent=1, sort_keys=True)
        K.check(False, "C: no EXPECT yet - wrote expect52.dump.json next to the harness scratch (review it, then paste it as EXPECT)")
    else:
        K.eq(sorted(got), sorted(expect), "C: the classes that differ")
        for k in sorted(expect):
            K.eq(got.get(k, []), sorted(expect[k]), "C: %s members" % k)
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    a_, c_, g_ = expected_nonclass(za, zb)
    K.check(not g_ and all(aug_name(n) for n in a_) and c_ == ["Server/Languages/en-US/server.lang", "manifest.json"],
            "C: non-class entries: only augment files added (%d), manifest.json + server.lang changed" % len(a_))
    K.notes.append("C: %d identical, changed: %s" % (same, got))
    K.save()


HK.run_compare = run_compare52


# ====================================================================================================== E: engine
def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JString, JImplements, JOverride, JObject, JArray, JLong, JDouble, JBoolean, JFloat, JShort, JByte
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
    Cfg, Gear, Data, Roll, View, Stats, Defs, Aug, Elem, Tool, LL, GHit = (P("GearCfg"), P("Gear"), P("GearData"), P("GearRoll"), P("GearView"),
                                                                       P("GearStats"), P("GearDefs"), P("GearAug"), P("GearElem"), P("GearTool"),
                                                                       P("GearLL"), P("GearHit"))
    Props = JClass("java.util.Properties")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    BA = JClass("org.bson.BsonArray")
    BS = JClass("org.bson.BsonString")
    BI = JClass("org.bson.BsonInt32")
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")
    AL = JClass("java.util.ArrayList")
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
    BASE = {"part__gate": "false"}
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

    @JImplements("java.util.function.Function")
    class PyFn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, a):
            return self.f(a)
    ITEM = E["ITEM"]
    allids = sorted(str(k) for k in ITEM.getAssetMap().getAssetMap().keySet())

    # ================================================================================== V the items in the real store
    miss = [i for i in IDS if Gear.item(JString(i)) is None]
    K.check(not miss, "V the 120 augment items are in the real Item store: missing %s" % miss[:4])
    af = [m for lv, m in E["rec"] if "Skyy_Aug_" in m and lv in ("SEVERE", "WARNING")]
    K.check(not af, "V no augment asset fails / warns in the bare boot: %s" % af[:3])
    K.notes.append("V jar pack log: %d lines, %d SEVERE / WARNING, stores failed %s" % (len(E["rec"]), len([1 for lv, m in E["rec"] if lv in ("SEVERE", "WARNING")]), list(E["fail"])))

    # ================================================================================== P config
    pb = []
    if [int(x) for x in Cfg.AUG_SW] != [1, 1, 2, 2, 3, 3, 1, 2] or [int(x) for x in Cfg.AUG_SA] != [0, 1, 1, 2, 2, 3, 1, 1] or [int(x) for x in Cfg.AUG_ST] != [1, 2, 3]:
        pb.append(("slots", list(Cfg.AUG_SW), list(Cfg.AUG_SA)))
    if [float(x) for x in Cfg.AUG_SCALE] != [40.0, 55.0, 70.0, 85.0, 100.0] or [int(x) for x in Cfg.AUG_EP] != list(range(1, 11)) or abs(float(Cfg.AUG_EW[9]) - 3.0) > 1e-9:
        pb.append(("tables", list(Cfg.AUG_SCALE)))
    if [round(float(x), 3) for x in list(Cfg.AUG_V)[:2]] != [4.0, 4.8] or [round(float(x), 3) for x in list(Cfg.AUG_V)[8:10]] != [2.0, 2.4]:
        pb.append(("stat values (Brute 4 / 4.8, Tempo 2 / 2.4)", list(Cfg.AUG_V)[:10]))
    apply(aug__slots__weapon="2,2,2,2,2,2,2,2", aug__stat__Brute="10,20", aug__elem__power="2,2,2,2,2,2,2,2,2,2", **BASE)
    if [int(x) for x in Cfg.AUG_SW] != [2] * 8 or abs(float(Aug.val(0, 0, 5)) - 10.0) > 1e-9 or abs(float(Aug.val(0, 1, 3)) - 14.0) > 1e-9 or int(Aug.ep(7)) != 2:
        pb.append(("a live edit", list(Cfg.AUG_SW), float(Aug.val(0, 0, 5))))
    apply(aug__slots__weapon="1,2,x", aug__tierScale="40,55", aug__slots__tool="1,2,9", **BASE)
    if [int(x) for x in Cfg.AUG_SW] != [1, 1, 2, 2, 3, 3, 1, 2] or [float(x) for x in Cfg.AUG_SCALE] != [40.0, 55.0, 70.0, 85.0, 100.0] or [int(x) for x in Cfg.AUG_ST] != [1, 2, 3]:
        pb.append(("bad lines = the defaults", list(Cfg.AUG_SW)))
    apply(**BASE)
    chk = [Cfg.augCheck(JString("aug.slots.weapon"), JString("1,1,2,2,3,3,1,2")), Cfg.augCheck(JString("aug.slots.weapon"), JString("1,1,2")),
           Cfg.augCheck(JString("aug.slots.tool"), JString("1,2,2.5")), Cfg.augCheck(JString("aug.stat.Brute"), JString("4,4.8")),
           Cfg.augCheck(JString("aug.elem.power"), JString("1,2,3,4,5,6,7,8,9,11")), Cfg.augCheck(JString("other.key"), JString("x"))]
    if chk[0] is not None or chk[1] is None or chk[2] is None or chk[3] is not None or chk[4] is None or chk[5] is not None:
        pb.append(("augCheck", [None if c is None else str(c) for c in chk]))
    Cfg.AUG_SW_T = JString("3,3,3,3,3,3,3,3")
    Cfg.augAfter(JString("aug.slots.weapon"))
    if [int(x) for x in Cfg.AUG_SW] != [3] * 8:
        pb.append(("augAfter (the kit's live edit)", list(Cfg.AUG_SW)))
    apply(**BASE)
    K.check(not pb, "P config: the defaults, a live edit (slots, Brute 10 / 20 = val, Power), bad lines -> the defaults, augCheck refuses a wrong count / "
            "a non-whole slot / Power 11, augAfter re-parses: %s" % pb)
    K.notes.append("P augCheck message: %s" % chk[1])

    # ================================================================================== Q pure parts
    def doc(iid, r=0, ident=True, lv=15, aug=None, add=0, mods=()):
        d_ = Roll.newDoc(JString(iid), JInt(r), ident, JString("admin"), JInt(lv))
        d_.put("r", BS(Defs.R_ID[r]))          # the rarity exactly (newDoc keeps Untiered for the table's ids only)
        ar_ = BA()
        for k_, v_ in mods:
            ar_.add(Data.mod(JString(k_), JInt(v_)))
        d_.put("mods", ar_)
        if aug is not None:
            a_ = BA()
            for x_ in aug:
                a_.add(BS(JString(x_)))
            d_.put("aug", a_)
        if add:
            d_.put("augAdd", BI(JInt(add)))
        return d_

    def stack(iid, d_, q=1):
        return Data.put(IS(JString(iid), JInt(q)), d_, u)
    sw = next(i for i in allids if i.startswith("Weapon_Sword_") and int(Data.slotOf(JString(i))) == 0)
    wand = next((i for i in allids if i.startswith("Weapon_Wand_") and int(Data.slotOf(JString(i))) == 1), None)
    helm = next(i for i in allids if i.startswith("Armor_") and i.endswith("_Head") and int(Data.slotOf(JString(i))) == 2 and bool(View.combatArmor(JString(i))))
    mine = next((i for i in allids if int(Data.slotOf(JString(i))) == 2 and int(P("GearMine").index(JString(i))) >= 0), None)
    fish = next((i for i in allids if int(Data.slotOf(JString(i))) == 2 and str(P("GearGArm").gateAny(JString(i))) == "Fishing"), None)
    pick = "Tool_Pickaxe_Iron"          # by id (the bare boot does not load every tool; the document tests need only the id)
    pickT = "Tool_Pickaxe_Adamantite"
    K.notes.append("Q items: sword %s, wand %s, helm %s, mining %s, fishing %s, pickaxe %s / %s" % (sw, wand, helm, mine, fish, pick, pickT))
    qb = []
    if [list(Aug.ent(JString(x))) if Aug.ent(JString(x)) is not None else None for x in ("S:Brute:3", "E:Fire:7", "M:Poison:5", "E:Fire:11", "S:Fire:3", "", "X", "E:Bogus:2", "S:Brute:x", "S:Swift:3", "S:Sage:1")] \
            != [[0, 3], [16, 7], [18, 5], None, None, None, None, None, None, [7, 3], [9, 1]]:
        qb.append("ent (+ fix round 3 M1: Swift / Sage entries read)")
    if [bool(Aug.occupied(JString(x))) for x in ("", " ", "E:Fire:11", "S:Brute:3")] != [False, False, True, True]:
        qb.append("fix F3: occupied")
    if str(Aug.code(16, 7)) != "E:Fire:7" or list(Aug.idOf(JString("Skyy_Aug_Air_10"))) != [17, 10] or Aug.idOf(JString("Skyy_Aug_Air_11")) is not None \
            or str(Aug.itemId(0, 5)) != "Skyy_Aug_Brute_5" or str(Aug.name(16, 7)) != "Fire VII" or str(Aug.itemName(0, 3)) != "Brute Augment III":
        qb.append("code / idOf / itemId / name")
    if [str(Aug.tierHex(0, t_)) for t_ in (1, 3, 5)] != ["#c9d2dd", "#2770b7", "#bb8a2c"] or [str(Aug.tierHex(16, t_)) for t_ in (1, 2, 3, 10)] != ["#c9d2dd", "#c9d2dd", "#3e9049", "#bb8a2c"]:
        qb.append("tierHex")
    if int(Aug.ladderT(JString("Tool_Pickaxe_Iron"))) != 2 or int(Aug.ladderT(JString("Tool_Pickaxe_Adamantite"))) != 10 or int(Aug.ladderT(JString("Tool_Pickaxe_Mithril"))) != 13 or int(Aug.ladderT(JString("Weird"))) != 0:
        qb.append("ladderT")
    ll = doc(pick, r=1)
    ll.put("ll", BI(JInt(1)))
    kinds = [int(Aug.kindAt(JString(sw), doc(sw))), int(Aug.kindAt(JString(wand), doc(wand))) if wand else 2, int(Aug.kindAt(JString(helm), doc(helm))),
             int(Aug.kindAt(JString(mine), doc(mine))) if mine else 4, int(Aug.kindAt(JString(fish), doc(fish))) if fish else 5,
             int(Aug.kindAt(JString(pick), ll)), int(Aug.kindAt(JString(pick), doc(pick))), int(Aug.kindAt(JString("Tool_WaterCan_Iron"), ll))]
    if kinds != [1, 2, 3, 4, 5, 6, 0, 0]:          # ... a lifelong watering can holds none
        qb.append(("kindAt", kinds))
    sl = [int(Aug.slots(JString(sw), doc(sw, r=r_))) for r_ in range(8)] + [int(Aug.slots(JString(helm), doc(helm, r=r_))) for r_ in range(8)]
    if sl != [1, 1, 2, 2, 3, 3, 1, 2, 0, 1, 1, 2, 2, 3, 1, 1]:
        qb.append(("slots by rarity", sl))
    ll2 = doc(pickT or pick, r=0)
    ll2.put("ll", BI(JInt(1)))
    if int(Aug.slots(JString(pick), ll)) != 1 or (pickT and int(Aug.slots(JString(pickT), ll2)) != 3) or int(Aug.slots(JString(pick), doc(pick))) != 0:
        qb.append(("tool slots", int(Aug.slots(JString(pick), ll))))
    if int(Aug.slots(JString(sw), doc(sw, r=2, add=1))) != 3 or int(Aug.slots(JString(sw), doc(sw, r=2, add=5))) != 3 or int(Aug.slots(JString(sw), doc(sw, r=2, ident=False))) != 0:
        qb.append("augAdd / the cap / unidentified")
    apply(aug__extraSlots="0", **BASE)
    x0 = int(Aug.slots(JString(sw), doc(sw, r=2, add=1)))
    apply(part__augments="false", **BASE)
    x1 = int(Aug.slots(JString(sw), doc(sw, r=2)))
    apply(**BASE)
    if x0 != 2 or x1 != 0:
        qb.append(("extraSlots 0 / part.augments off", x0, x1))
    FITW = {1: [1, 2], 2: [2], 3: [3], 4: [4, 6], 5: [1, 2, 3, 4, 5], 6: [1]}
    fb = [(k_, w_) for k_ in range(len(KINDS)) for w_ in range(0, 7) if bool(Aug.fits(k_, w_)) != (w_ in FITW[int(Aug.FIT[k_])])]
    if fb or [int(Aug.FIT[k_]) for k_ in range(len(KINDS))] != [1, 1, 1, 2, 6, 3, 3, 3, 3, 3, 4, 4, 4, 5, 5, 5, 5, 5, 1]:
        qb.append(("fits (fix F2: Tempo = 6)", fb[:4]))
    bow = next((i for i in allids if ("Shortbow" in i or "Crossbow" in i or i.startswith("Weapon_Bow")) and int(Data.slotOf(JString(i))) == 0), None)
    fa = [bool(Aug.fitsAt(4, 1, JString(sw))), bool(Aug.fitsAt(4, 1, JString(bow))) if bow else False, bool(Aug.fitsAt(0, 1, JString(bow))) if bow else True,
          bool(Aug.fitsAt(4, 2, JString(wand))) if wand else False]
    if fa != [True, False, True, False] or not bool(Aug.melee(JString(sw))):
        qb.append(("fix F2: fitsAt - Tempo on a sword yes, on a bow / wand no; Brute on a bow yes", fa, bow))
    if bow:
        pb_ = Aug.plan(JString(bow), doc(bow, r=4), JInt(0), JInt(4), JInt(1))
        if int(pb_[0]) != -1 or "melee weapons" not in str(pb_[1]) or Aug.gives(4, 1, 1, JString(bow)) is not None:
            qb.append(("fix F2: Tempo on a bow refused + no gives", str(pb_[1])))
        K.notes.append("FIX F2: bow %s, plan says %r" % (bow, str(pb_[1])))

    def plan(iid, d_, si, k_, t_):
        r_ = Aug.plan(JString(iid), d_, JInt(si), JInt(k_), JInt(t_))
        return int(r_[0]), str(r_[1]), int(r_[2]), None if r_[3] is None else str(r_[3])
    dw = doc(sw, r=4, aug=["S:Brute:3", "E:Fire:4", ""])
    pl = [plan(sw, dw, 2, 1, 2), plan(sw, dw, 0, 1, 2), plan(sw, dw, 1, 16, 4), plan(sw, dw, 1, 16, 6), plan(sw, dw, 1, 16, 2), plan(sw, dw, 0, 0, 3),
          plan(sw, dw, 2, 5, 3), plan(sw, dw, 5, 0, 1), plan(sw, doc(sw, r=4, aug=["E:Fire:10"]), 0, 16, 10), plan(helm, doc(helm, r=0), 0, 5, 1),
          plan(sw, dw, 0, 0, 5), plan(sw, dw, 2, 18, 5)]
    want_ops = [0, 1, 2, 1, -1, -1, -1, -1, -1, -1, 1, 0]
    if [p_[0] for p_ in pl] != want_ops or pl[2][1] != "E:Fire:5" or pl[2][2] != 1 or pl[2][3] != "E:Fire:4" or pl[1][3] != "S:Brute:3" or pl[0][1] != "S:Edge:2" \
            or "downgrade" not in pl[4][1] or "already holds" not in pl[5][1] or "fit combat armor" not in pl[6][1] or "top tier" not in pl[8][1] or "no augment slot" not in pl[9][1]:
        qb.append(("plan", pl))
    K.notes.append("Q plan refusals: %s" % [p_[1] for p_ in pl if p_[0] < 0])
    du = doc(sw, r=4, aug=["E:Fire:11", "", "S:Swift:2"])          # fix F3: damaged / a newer version's - kept (Swift reads since M1; it does not fit a sword)
    pu = [plan(sw, du, 0, 0, 1), plan(sw, du, 1, 0, 1), plan(sw, du, 0, 16, 10)]
    if [p_[0] for p_ in pu] != [-1, 0, -1] or "cannot read" not in pu[0][1] or str(Aug.rowSub(stack(sw, du))) != "2 / 3 augments":
        qb.append(("fix F3: an unreadable slot is refused (kept), the empty one is free, it counts as filled", pu, str(Aug.rowSub(stack(sw, du)))))
    K.notes.append("FIX F3: %s" % pu[0][1])
    nd = Aug.docWith(dw, JInt(1), JString("E:Fire:5"), JInt(3))
    if list(str(x) for x in Aug.raw(nd)) != ["S:Brute:3", "E:Fire:5", ""] or list(str(x) for x in Aug.raw(dw)) != ["S:Brute:3", "E:Fire:4", ""]:
        qb.append(("docWith (a clone)", list(Aug.raw(nd))))
    nd2 = Aug.docWith(doc(sw, r=4), JInt(2), JString("S:Edge:1"), JInt(3))
    if list(str(x) for x in Aug.raw(nd2)) != ["", "", "S:Edge:1"]:
        qb.append(("docWith (empty)", list(Aug.raw(nd2))))
    cd = doc(pick)
    Aug.carry(cd, doc(pick, aug=["S:Delver:2", ""], add=1), doc(pick, aug=["", "S:Prospector:4", "junk"]))
    if list(str(x) for x in Aug.raw(cd)) != ["S:Delver:2", "S:Prospector:4", "junk"] or int(Aug.added(cd)) != 1:
        qb.append(("carry (fix F3: an unreadable entry is carried, never dropped)", list(Aug.raw(cd))))
    cd2 = doc(pick)
    Aug.carry(cd2, doc(pick), None)
    if cd2.containsKey("aug") or cd2.containsKey("augAdd"):
        qb.append("carry of nothing writes nothing")
    gv = [str(Aug.gives(0, 5, 1, JString(sw))), str(Aug.gives(16, 10, 1, JString(sw))), str(Aug.gives(16, 10, 3, JString(helm))), str(Aug.gives(18, 5, 1, JString(sw))),
          str(Aug.gives(7, 5, 3, JString(helm))), str(Aug.gives(10, 5, 6, JString(pick))), Aug.gives(5, 5, 1, JString(sw))]
    if gv[0] != "+4 Strength, +4.8% Crit Damage" or gv[1] != "+3% Fire Damage, Element Power 10" or gv[2] != "+6 Fire Defence" or gv[3] != "+2% Poison over 10 s" \
            or gv[4] != "+0.5 Speed, +2% Mana" or gv[5] != "+4% Breaking Speed, +25 Mining Fortune" or gv[6] is not None:
        qb.append(("gives", gv))
    K.check(not qb, "Q pure: ent / code / idOf / itemId / name / tierHex / ladderT / kindAt (weapon, spell, combat armor, Mining armor, Fishing armor, "
            "lifelong tool, plain tool) / slots by rarity (weapon 1,1,2,2,3,3,1,2; armor 0,1,1,2,2,3,1,1; tools by tier) + augAdd + the cap + "
            "unidentified / extraSlots 0 / part.augments off / fits / plan (add, replace, fuse, lower, same, not fitting, no slot, top, out of range) "
            "/ docWith (a clone) / carry / gives: %s" % qb)
    K.notes.append("Q gives: %s" % gv)

    # ================================================================================== T totals0
    I = dict((str(Defs.S_KEY[i]), i) for i in range(int(Defs.NS)))
    tb = []

    def tot(w_=None, arm_=None):
        return [int(x) for x in Stats.totals0(u, w_, arm_, None, False)]
    s0 = stack(sw, doc(sw, r=4, mods=[("str", 10)]))
    s1 = stack(sw, doc(sw, r=4, mods=[("str", 10)], aug=["S:Brute:5", "S:Edge:3"]))
    s2 = stack(sw, doc(sw, r=4, mods=[("str", 10)], aug=["S:Bulwark:5", "E:Fire:10", "M:Poison:5"]))
    s3 = stack(sw, doc(sw, r=0, mods=[("str", 10)], aug=["", "S:Brute:5"]))
    t0, t1, t2, t3 = tot(s0), tot(s1), tot(s2), tot(s3)
    ev = float(View.effVal(JString(sw), Data.effective(JString(sw), s0.getMetadata()), JString("str"), 10))
    if t1[I["str"]] != int(round(ev + 4.0)) or t1[I["cd"]] != 5 or t1[I["dmg"]] != int(round(2.8 * 0.7)) or t1[I["cc"]] != int(round(1.4 * 0.7)):
        tb.append(("Brute V + Edge III on a sword", t1[I["str"]], t1[I["cd"]], t1[I["dmg"]], t1[I["cc"]], ev))
    if t2 != t0 or t3 != t0:
        tb.append(("a non-fitting armor kind / element (per hit) / Poison (per hit) / past the slots = nothing in the totals", [i for i in range(len(t0)) if t2[i] != t0[i]]))
    arm = SIC(JShort(4))
    arm.setItemStackForSlot(JShort(0), stack(helm, doc(helm, r=5, aug=["S:Bulwark:5", "E:Fire:10", "S:Brute:5"])))
    arm.setItemStackForSlot(JShort(1), stack(helm, doc(helm, r=5, aug=["S:Bulwark:5"])))
    ta = tot(None, arm)
    if ta[I["def"]] != 2 or ta[I["hpp"]] != 2 or ta[I["dFire"]] != 6 or ta[I["str"]] != 0:
        tb.append(("2 x Bulwark V (0.9 + 0.9 = 1.8 -> 2 Defense once) + Fire X armor (6 Fire Defence); Brute (weapon kind) on armor = 0", ta[I["def"]], ta[I["hpp"]], ta[I["dFire"]]))
    apply(part__augments="false", **BASE)
    toff = tot(s1)
    apply(**BASE)
    if toff != t0:
        tb.append("part.augments off = the 0.3.51 totals")
    K.check(not tb, "T totals0: Brute V + Edge III add their stats (rounded once with the rolled lines), armor Bulwark + Fire Defence summed over the kit, "
            "a non-fitting / per-hit / past-the-slots entry adds nothing, part.augments off = identical: %s" % tb)

    # ================================================================================== M fix round 3 (M1): Swift / Sage -> Mana % (skyygear_mana)
    mb = []
    Fx = P("GearUtFx")
    KSW, KSG = KINDS.index("Swift"), KINDS.index("Sage")
    mo = lambda iid, d_: round(float(Aug.manaOf(JString(iid), d_)), 6)
    hm5 = doc(helm, r=5, aug=["S:Swift:5", "S:Sage:5", "S:Swift:1"])          # Mythic armor: 3 slots
    if [mo(helm, hm5), mo(helm, doc(helm, r=4, aug=["S:Sage:3"])), mo(sw, doc(sw, r=4, aug=["S:Swift:5"])), mo(helm, doc(helm, r=0, aug=["S:Swift:5"])),
            mo(helm, doc(helm, r=5, aug=["S:Brute:5", "E:Fire:10", "S:Vital:5"])), mo(helm, doc(helm, r=5, ident=False, aug=["S:Swift:5"]))] != [4.8, 1.4, 0.0, 0.0, 0.0, 0.0]:
        mb.append(("manaOf: Swift V + Sage V + Swift I = 2 + 2 + 0.8; Sage III 1.4; on a sword / no slot (Normal) / other kinds / unidentified = 0",
                   mo(helm, hm5), mo(sw, doc(sw, r=4, aug=["S:Swift:5"]))))
    if [str(Aug.K1[KSW]), str(Aug.K2[KSW]), str(Aug.K1[KSG]), str(Aug.K2[KSG]), int(Aug.S2[KSW]), int(Aug.S2[KSG]), bool(Aug.LATER[KSW]), bool(Aug.LATER[KSG])] \
            != ["spd", "manap", "mp", "manap", -1, -1, False, False]:
        mb.append("the Swift / Sage table rows (Speed / Magical Power + manap, not a STATS key, not LATER)")
    apply(aug__stat__Swift="0.5,10", **BASE)
    m_ed = mo(helm, hm5)
    apply(part__augments="false", **BASE)
    m_off = mo(helm, hm5)
    apply(**BASE)
    if abs(m_ed - (10.0 + 2.0 + 4.0)) > 1e-9 or m_off != 0.0:
        mb.append(("a live aug.stat.Swift edit (Mana 10 at V, x 40 % at I) / part.augments off", m_ed, m_off))
    armM = SIC(JShort(4))
    armM.setItemStackForSlot(JShort(0), stack(helm, hm5))
    armM.setItemStackForSlot(JShort(1), stack(helm, doc(helm, r=4, aug=["S:Sage:3"])))
    armM.setItemStackForSlot(JShort(2), stack(sw, doc(sw, r=4, aug=["S:Swift:5"])))          # not armor: never counted
    tm = tot(None, armM)
    if tm[I["spd"]] != int(round(0.5 + 0.2)) or tm[I["mp"]] != int(round(1.6 + 1.6 * 0.7)):
        mb.append(("totals0: Swift's Speed (0.5 + 0.2 -> 1) + Sage's Magical Power (1.6 + 1.12 -> 3), rounded once", tm[I["spd"]], tm[I["mp"]]))
    mw = round(float(Fx.manaWorn(u, armM)), 6)
    if mw != 6.2 or float(Fx.manaWorn(u, None)) != 0.0:
        mb.append(("manaWorn: 4.8 + 1.4 over the worn armor (the sword in slot 2 ignored)", mw))
    apply(part__gate="true")
    gw = round(float(Fx.manaWorn(u, armM)), 6)
    apply(**BASE)
    K.notes.append("M manaWorn with part.gate on (the class / level gate may switch pieces off): %s" % gw)
    if str(Fx.MKEY) != "skyygear_mana" or not bool(Fx.pctKey(JString("skyygear_mana"))) or bool(Fx.pctKey(JString("skyyskill_classmana"))):
        mb.append(("MKEY / pctKey", str(Fx.MKEY)))
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    ESMc = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DSTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    ETc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    mm = JClass("java.util.HashMap")()
    for k_, v_ in (("Armor", 50.0), ("skyyskill_classmana", 20.0), ("skyygear_mana", 40.0), ("skyygear_hp", 9.0), ("skyyacc_mana", 30.0), ("skyypet_mana", 20.0),
                   ("skyyskill_rebirthmana", 15.0)):
        mm.put(k_, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(v_)))
    if float(Fx.flatOf(JFloat(100.0), mm)) != 170.0:
        mb.append(("flatOf: type max 100 + Armor 50 + class Mana 20; Gear Mana / Health, accessory, pet, rebirth %% layers skipped", float(Fx.flatOf(JFloat(100.0), mm))))
    MI = int(DSTc.getMana())
    mt = ETc.getAssetMap().getAsset(JInt(MI))
    K.notes.append("M the Mana stat type: index %d, %s" % (MI, None if mt is None else "max %s" % float(mt.getMax())))
    if mt is None:
        mb.append("the bare boot has no Mana stat type")
    else:
        hfm = ETc.class_.getDeclaredField("max")
        hfm.setAccessible(True)
        max0 = float(hfm.getFloat(mt))
        hfm.setFloat(mt, JFloat(100.0))
        try:
            em = ESMc()
            em.update()
            em.putModifier(JInt(MI), "aug2btest", SMO(MTG.MAX, CAL.ADDITIVE, JFloat(50.0)))          # a flat source: flat max 150
            for k_, v_ in (("skyypet_mana", 30.0), ("skyyacc_mana", 20.0), ("skyyskill_rebirthmana", 15.0)):          # the other mods' % layers
                em.putModifier(JInt(MI), k_, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(v_)))
            amt = lambda: (lambda c: None if c is None else round(float(c.getAmount()), 3))(em.getModifier(JInt(MI), "skyygear_mana"))
            seq = []
            for _ in range(4):
                Fx.mpApply(em, JDouble(6.2), True)
                seq.append(amt())
            Fx.mpApply(em, JDouble(2.0), False)
            low_wait = amt()
            Fx.mpApply(em, JDouble(2.0), True)
            low_now = amt()
            Fx.mpApply(em, JDouble(10.0), False)
            raise_now = amt()
            Fx.mpApply(em, JDouble(0.0), False)
            gone = amt()
            if seq != [9.3] * 4 or low_wait != 9.3 or low_now != 3.0 or raise_now != 15.0 or gone is not None:
                mb.append(("mpApply on a REAL EntityStatMap: 6.2 %% of the flat 150 = 9.3, steady (no compounding with the pet / accessory / rebirth %% "
                           "layers), lowering waits for synced, raising at once, 0 removes", seq, low_wait, low_now, raise_now, gone))
            # GearUtFx.secondPass end to end: the worn Swift / Sage kit -> skyygear_mana; part.augments / part.stats off -> removed
            Fx.secondPass(u, em, None, armM, True)
            sp1 = amt()
            Fx.secondPass(u, em, None, armM, True)
            sp2 = amt()
            apply(part__augments="false", **BASE)
            Fx.secondPass(u, em, None, armM, True)
            sp3 = amt()
            apply(**BASE)
            Fx.secondPass(u, em, None, armM, True)
            sp4 = amt()
            apply(part__stats="false", **BASE)
            Fx.secondPass(u, em, None, armM, True)
            sp5 = amt()
            apply(**BASE)
            Fx.secondPass(u, em, None, None, True)
            sp6 = amt()
            if [sp1, sp2, sp3, sp4, sp5, sp6] != [9.3, 9.3, None, 9.3, None, None]:
                mb.append(("secondPass: worn Swift + Sage = 9.3 (6.2 %% of 150), steady, part.augments off / part.stats off / no armor = removed",
                           [sp1, sp2, sp3, sp4, sp5, sp6]))
            K.notes.append("M max Mana with the kit: %.2f (flat 150 + others' layers 65 + Gear %.2f)" % (float(em.get(JInt(MI)).getMax()), sp4 or 0.0))
        finally:
            hfm.setFloat(mt, JFloat(max0))
    K.check(not mb, "M fix round 3 (M1): Swift / Sage Mana %% - manaOf (exact, fitting, inside the slots, a live edit, part.augments off), totals0 "
            "(Speed / Magical Power), manaWorn on a REAL armor container, pctKey / flatOf, mpApply on a REAL EntityStatMap (no compounding, "
            "synced lowering), secondPass end to end: %s" % mb)

    # ================================================================================== W weap / power / pcts2 / split
    wb = []
    dwe = doc(sw, r=5, aug=["E:Earth:3", "E:Fire:10", "M:Poison:5"], mods=[("fFire", 2), ("rElem", 1)])          # Mythic: 3 slots
    aw = [float(x) for x in Aug.weap(JString(sw), dwe)]
    if [round(x, 4) for x in aw] != [0.7, 0.0, 0.0, 3.0, 0.0, 2.0, 3.0, 0.0, 0.0, 10.0, 0.0]:
        wb.append(("weap", aw))
    pw = [int(x) for x in Aug.power(JString(sw), dwe, Aug.weap(JString(sw), dwe), JInt(3))]
    pw0 = [int(x) for x in Aug.power(JString(sw), doc(sw), None, JInt(-1))]
    if pw != [3 + 3, 3, 3, 10 + 3 + 3 + 5, 3] or pw0 != [0, 0, 0, 0, 0]:
        wb.append(("power: socketed + 3 a rolled line + rElem 3 each + Imbue 5", pw, pw0))
    if [float(x) for x in Aug.weap(JString(helm), doc(helm, r=4, aug=["E:Fire:10"]))] != [0.0] * 11:
        wb.append("weap of an armor piece = nothing")
    pets = [0] * int(Defs.NS)
    pets[I["fFire"]] = 10
    JI = JArray(JInt)
    z = JI(int(Defs.NS))
    pj = JI(pets)
    p_no = [float(x) for x in Elem.pcts(pj, z, z, pj, False, -1, 0.0)]          # full = the totals with the pets in them
    p_ag = [float(x) for x in Elem.pcts2(pj, z, z, pj, False, -1, 0.0, JArray(JDouble)([0.0, 0.0, 0.0, 3.0, 0.0, 0.0]))]
    if p_no[3] != 0.0 or abs(p_ag[3] - 13.0) > 1e-9:
        wb.append(("pcts2: the augment opens the pet gate (10 + 3)", p_no, p_ag))
    br.put("classes:fn:imbue", PyFn(lambda a: JString("Fire;30")))
    apply(**BASE)
    main = stack(sw, dwe)
    inf = GHit.info(u, None)
    tt = Stats.totals(u, main, None, None, True)
    Elem.split(inf, u, main, None, tt, JDouble(100.0), True)
    br.remove("classes:fn:imbue")
    parts = [int(x) for x in inf[6]] if inf[6] is not None else None
    if len(inf) != 11 or parts is None or parts[3] < 30 + 3 or inf[7] is None or int(inf[7]) < 2 or list(int(x) for x in inf[8]) != [6, 3, 3, 21, 3]:
        wb.append(("split", len(inf), parts, inf[7], list(inf[8]) if inf[8] is not None else None))
    K.notes.append("W split on a 100 hit: parts %s, Poison %s, Power %s" % (parts, inf[7], list(inf[8]) if inf[8] is not None else None))
    fb4 = []
    br.put("classes:fn:imbue", PyFn(lambda a: JString("Fire;30")))
    apply(**BASE)
    io = Elem.imbOnly(u, IS(JString("Weapon_Sword_Nope"), JInt(1)), True)
    io_np = Elem.imbOnly(u, main, False)
    apply(aug__states="false", **BASE)
    io_off = Elem.imbOnly(u, main, True)
    apply(**BASE)
    br.remove("classes:fn:imbue")
    io_no = Elem.imbOnly(u, main, True)
    if io is None or len(io) != 11 or [int(x) for x in io[8]] != [0, 0, 0, 5, 0] or int(io[1]) != 0 or int(io[2]) != 0 or int(io[5]) != 0 or io[6] is not None \
            or str(io[4]) != U or io_np is not None or io_off is not None or io_no is not None:
        fb4.append(("imbOnly", None if io is None else [str(x) for x in io], io_np, io_off, io_no))
    K.check(not fb4, "FIX F4: GearElem.imbOnly - a running Imbue on an NPC hit with no gear stats gives info[8] = Imbue's Power 5 only (no damage parts); "
            "a player victim / aug.states off / no Imbue = null: %s" % fb4)
    K.check(not wb, "W weap (element %% + Poison + socketed Power on a weapon, nothing on armor), power (+3 a rolled line, Raw Elemental +3 each, Imbue +5), "
            "pcts2 (the pet gate opens), a REAL split (Fire part = rolled 2 + Raw 1 + augment 3 + Imbue 30 of a 100 hit, Poison 2, inf[8] Power): %s" % wb)

    # ================================================================================== H states on an ECS shim
    jpz = JClass("javassist.ClassPool")(True)
    jpz.appendClassPath(B.SERVER_JAR)
    CTFz, CTMz = JClass("javassist.CtField"), JClass("javassist.CtNewMethod")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    CMPc, CTc, RFc = "com.hypixel.hytale.component.Component", "com.hypixel.hytale.component.ComponentType", "com.hypixel.hytale.component.Ref"
    cc_ = jpz.makeClass("com.hypixel.hytale.component.SkyyAugBuf", jpz.get("com.hypixel.hytale.component.CommandBuffer"))
    cc_.addField(CTFz.make("public static java.util.IdentityHashMap COMP = new java.util.IdentityHashMap();", cc_))
    cc_.addMethod(CTMz.make("public %s getComponent(%s r, %s t) { java.util.IdentityHashMap m = (java.util.IdentityHashMap) COMP.get(r); if (m == null) return null; return (%s) m.get(t); }" % (CMPc, RFc, CTc, CMPc), cc_))
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
    UUIDC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    vu = UUID.fromString("00000000-0000-0000-0000-00000000b0b0")
    try:
        uc = UUIDC(vu)
    except Exception:
        uc = us.allocateInstance(UUIDC.class_)
        for fd_ in UUIDC.class_.getDeclaredFields():
            if fd_.getType() == UUID.class_:
                fd_.setAccessible(True)
                fd_.set(uc, vu)
    vref = us.allocateInstance(REFc.class_)
    fld(REFc, "index").setInt(vref, JInt(52))
    m_ = JClass("java.util.IdentityHashMap")()
    m_.put(UUIDC.getComponentType(), uc)
    Buf.COMP.put(vref, m_)
    GOT = []

    def eh(a):
        GOT.append([a[0], a[1], list(int(x) for x in a[2]), list(float(x) for x in a[3]), float(a[4]), bool(a[5]), a[6]])
        return JBoolean(True)
    hb = []
    info = GHit.info(u, None)
    info[8] = JArray(JInt)([0, 0, 0, 7, 0])
    info[9] = JArray(JInt)([0, 0, 0, 12, 0])
    info[10] = JObject(JBoolean(True), "java.lang.Boolean")
    n8 = int(Aug.N[8])
    Aug.states(u, buf, vref, info, JDouble(80.0))
    if int(Aug.N[8]) != n8 + 1:
        hb.append("no bridge = counted, nothing sent")
    br.put("classes:fn:elemHit", PyFn(eh))
    Aug.states(u, buf, vref, info, JDouble(80.0))
    if len(GOT) != 1 or str(GOT[0][0]) != U or str(GOT[0][1]) != str(vu) or GOT[0][2] != [0, 0, 0, 7, 0] or GOT[0][3] != [0.0, 0.0, 0.0, 12.0, 0.0] \
            or GOT[0][4] != 80.0 or GOT[0][5] is not True or GOT[0][6] is not None:
        hb.append(("sent", GOT))
    info[8] = JArray(JInt)([0, 0, 0, 0, 0])
    Aug.states(u, buf, vref, info, JDouble(80.0))
    info[8] = JArray(JInt)([0, 0, 0, 7, 0])
    apply(aug__states="false", **BASE)
    Aug.states(u, buf, vref, info, JDouble(80.0))
    apply(elem__on="false", **BASE)
    Aug.states(u, buf, vref, info, JDouble(80.0))
    apply(**BASE)
    Aug.states(u, buf, vref, info, JDouble(0.0))
    if len(GOT) != 1:
        hb.append(("no Power / aug.states off / elem.on off / nothing dealt = nothing sent", len(GOT)))
    Elem.onEdit(None)
    on1 = br.get("gear:elemStates")
    apply(aug__states="false", **BASE)
    Elem.onEdit(JString("aug.states"))
    on2 = br.get("gear:elemStates")
    apply(**BASE)
    Elem.onEdit(None)
    if on1 is None or not bool(on1) or on2 is not None or br.get("gear:elemStates") is None:
        hb.append(("gear:elemStates", on1, on2))
    br.remove("classes:fn:elemHit")
    K.check(not hb, "H states: no bridge = counted; the fake classes:fn:elemHit gets {attacker, victim UUID, power5 (a copy), dealt parts, hit, heavy, "
            "world}; no Power / aug.states off / elem.on off / 0 dealt = nothing; gear:elemStates follows aug.states (onEdit): %s" % hb)

    # ================================================================================== X the writes on REAL inventories + fake bags
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"
    SECS = (("hotbar", "Hotbar", 9), ("storage", "Storage", 36), ("backpack", "Backpack", 9), ("armor", "Armor", 4), ("utility", "Utility", 4), ("tools", "Tool", 4))
    SETM = SIC.class_.getMethod("setItemStackForSlot", JShort.class_, IS.class_)
    fc_ = jpz.makeClass("com.hypixel.hytale.server.core.inventory.container.SkyyFailSIC", jpz.get("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"))
    fc_.addField(CTFz.make("public static volatile int FAIL = -1;", fc_))
    fc_.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyFailSIC(short n) { super(n); }", fc_))
    fc_.addMethod(CTMz.make("public %s setItemStackForSlot(short s, com.hypixel.hytale.server.core.inventory.ItemStack it) { if (FAIL == (int) s) throw new IllegalStateException(\"harness: write refused\"); return super.setItemStackForSlot(s, it); }" % SETM.getReturnType().getName(), fc_))
    FailC = fc_.toClass(SIC.class_)
    Fail = JClass(FailC.getName())

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JByte(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        fld(Cc, "inventory").set(o_, cont)
        return o_

    def mkinv(failhot=False):
        inv_ = INV()
        cs_ = {}
        for f_, kind, n_ in SECS:
            cs_[f_] = Fail(JShort(n_)) if (failhot and f_ == "hotbar") else SIC(JShort(n_))
            try:
                fld(INV, f_).set(inv_, comp(kind, cs_[f_]))
            except Exception:
                fld(INV, f_).set(inv_, cs_[f_])
        return inv_, cs_

    def count(cs_, iid):
        n = 0
        for f_, _k, _n in SECS:
            c_ = cs_[f_]
            for i_ in range(int(c_.getCapacity())):
                s_ = c_.getItemStack(JShort(i_))
                if s_ is not None and not s_.isEmpty() and str(s_.getItemId()) == iid:
                    n += int(s_.getQuantity())
        return n
    BAG, TOOK, PUT, COM, SHORT = {}, [], [], [], set()

    def bag_count(a):
        try:
            CALLS["count"] += 1
        except NameError:
            pass
        return JObject(JLong(BAG.get(str(a[1]), 0)), "java.lang.Long")

    def bag_take(a):
        i, n = str(a[1]), int(a[2])
        g = 0 if i in SHORT else min(n, BAG.get(i, 0))
        BAG[i] = BAG.get(i, 0) - g
        TOOK.append((i, g))
        return JObject(JLong(g), "java.lang.Long")

    def bag_put(a):
        i, n = str(a[1]), int(a[2])
        BAG[i] = BAG.get(i, 0) + n
        PUT.append((i, n))
        return JObject(JLong(n), "java.lang.Long")
    br.put("sacks:fn:count", PyFn(bag_count))
    br.put("sacks:fn:take", PyFn(bag_take))
    br.put("sacks:fn:put", PyFn(bag_put))
    br.put("sacks:fn:commit", PyFn(lambda a: (COM.append((str(a[1]), int(a[2]))), JObject(JLong(int(a[2])), "java.lang.Long"))[1]))
    XP = []
    br.put("skill:fn:addxp", PyFn(lambda a: (XP.append((str(a[1]), int(a[2]), str(a[3]))), JBoolean(True))[1]))
    LV = {"Smithing": 12, "Mining": 30, "Foraging": 30, "Farming": 30}
    br.put("skill:fn:level", PyFn(lambda a: JObject(JInt(LV.get(str(a[1]), 0)), "java.lang.Integer")))
    COINS = [100000]

    def ctake(a):
        n = int(a[1])
        if n > COINS[0]:
            return JBoolean(False)
        COINS[0] -= n
        return JBoolean(True)
    br.put("coins:fn:get", PyFn(lambda a: JObject(JLong(COINS[0]), "java.lang.Long")))
    br.put("coins:fn:take", PyFn(ctake))
    br.put("coins:fn:add", PyFn(lambda a: (COINS.__setitem__(0, COINS[0] + int(a[1])), JObject(JLong(COINS[0]), "java.lang.Long"))[1]))
    P("GearGate").forget(u)
    FP = P("GearForge")
    xb = []
    inv, cs = mkinv()
    cs["hotbar"].setItemStackForSlot(JShort(0), stack(sw, doc(sw, r=4)))          # Legendary: 2 slots
    cs["storage"].setItemStackForSlot(JShort(3), IS(JString("Skyy_Aug_Brute_3"), JInt(2)))
    cs["storage"].setItemStackForSlot(JShort(4), IS(JString("Skyy_Aug_Fire_4"), JInt(1)))
    cs["backpack"].setItemStackForSlot(JShort(0), IS(JString("Skyy_Aug_Fire_4"), JInt(1)))

    def at0():
        return cs["hotbar"].getItemStack(JShort(0))

    def ap(si, aid, inv_=None, sec=0, slot=0, iid=None):
        it_ = (inv_ or inv).getHotbar().getItemStack(JShort(slot)) if sec == 0 else None
        if it_ is None:
            it_ = at0()
        r_ = Aug.apply(inv_ or inv, JInt(sec), JInt(slot), JString(iid or sw), FP.fp(it_), JInt(si), JString(aid), u, JString("Tester"))
        return int(r_[0]), str(r_[1])

    def augs():
        return [str(x) for x in Aug.raw(Data.gearDoc(at0().getMetadata()))]
    CALLS = {"all": 0, "count": 0}

    def bag_all(a):
        CALLS["all"] += 1
        m_ = JClass("java.util.HashMap")()
        for k_, v_ in BAG.items():
            if v_ > 0:
                m_.put(JString(k_), JObject(JLong(v_), "java.lang.Long"))
        return m_
    br.put("sacks:fn:all", PyFn(bag_all))
    own = [int(x) for x in Aug.owned(inv, u)]
    if own[IDS.index("Skyy_Aug_Brute_3")] != 2 or own[IDS.index("Skyy_Aug_Fire_4")] != 2 or sum(own) != 4:
        xb.append(("owned", [(IDS[i], own[i]) for i in range(len(own)) if own[i]]))
    BAG["Skyy_Aug_Air_9"] = 3
    c_before = dict(CALLS)
    own2 = [int(x) for x in Aug.owned(inv, u)]
    del BAG["Skyy_Aug_Air_9"]
    K.check(own2[IDS.index("Skyy_Aug_Air_9")] == 3 and sum(own2) == 7 and CALLS["all"] == c_before["all"] + 1 and CALLS["count"] == c_before["count"],
            "FIX F5: owned() reads the bags with ONE sacks:fn:all call (Air IX x3 in a bag counted): %s" % CALLS)
    r1 = ap(0, "Skyy_Aug_Brute_3")
    if r1[0] != 1 or augs()[:1] != ["S:Brute:3"] or count(cs, "Skyy_Aug_Brute_3") != 1 or count(cs, sw) != 1 or ("Smithing", 20, "gear:augment") not in XP:
        xb.append(("add", r1, augs(), count(cs, "Skyy_Aug_Brute_3"), XP))
    BAG["Skyy_Aug_Edge_2"] = 1
    r2 = ap(0, "Skyy_Aug_Edge_2")
    if r2[0] != 1 or augs()[0] != "S:Edge:2" or BAG["Skyy_Aug_Edge_2"] != 0 or ("Skyy_Aug_Edge_2", 1) not in COM or "destroyed" not in r2[1] or count(cs, "Skyy_Aug_Brute_3") != 1:
        xb.append(("replace from the bags (Brute destroyed, nothing back)", r2, augs(), BAG, COM))
    r3 = ap(1, "Skyy_Aug_Fire_4")
    r4 = ap(1, "Skyy_Aug_Fire_4")
    if r3[0] != 1 or r4[0] != 1 or augs()[:2] != ["S:Edge:2", "E:Fire:5"] or count(cs, "Skyy_Aug_Fire_4") != 0 or "Fused" not in r4[1]:
        xb.append(("add + fuse (Fire IV + Fire IV = Fire V, one item each)", r3, r4, augs(), count(cs, "Skyy_Aug_Fire_4")))
    cs["storage"].setItemStackForSlot(JShort(5), IS(JString("Skyy_Aug_Fire_2"), JInt(1)))
    cs["storage"].setItemStackForSlot(JShort(6), IS(JString("Skyy_Aug_Bulwark_1"), JInt(1)))
    snap = (augs(), count(cs, "Skyy_Aug_Fire_2"), count(cs, "Skyy_Aug_Bulwark_1"), count(cs, "Skyy_Aug_Brute_3"))
    rr = [ap(1, "Skyy_Aug_Fire_2"), ap(0, "Skyy_Aug_Bulwark_1"), ap(0, "Skyy_Aug_Edge_2"), ap(5, "Skyy_Aug_Brute_3"), ap(0, "Skyy_Aug_Air_3"), ap(0, "Skyy_Aug_Nope_1")]
    if [x[0] for x in rr] != [0] * 6 or (augs(), count(cs, "Skyy_Aug_Fire_2"), count(cs, "Skyy_Aug_Bulwark_1"), count(cs, "Skyy_Aug_Brute_3")) != snap:
        xb.append(("refusals move nothing", rr))
    K.notes.append("X refusals: %s" % [x[1] for x in rr])
    BAG["Skyy_Aug_Earth_1"] = 1
    SHORT.add("Skyy_Aug_Earth_1")
    rs = ap(0, "Skyy_Aug_Earth_1")
    SHORT.discard("Skyy_Aug_Earth_1")
    if rs[0] != -1 or augs()[0] != "S:Edge:2" or BAG["Skyy_Aug_Earth_1"] != 1:
        xb.append(("a short bag = nothing used", rs, augs(), BAG.get("Skyy_Aug_Earth_1")))
    inv2, cs2 = mkinv(failhot=True)
    cs2["hotbar"].setItemStackForSlot(JShort(0), stack(sw, doc(sw, r=4)))
    cs2["storage"].setItemStackForSlot(JShort(0), IS(JString("Skyy_Aug_Brute_1"), JInt(3)))
    Fail.FAIL = 0
    it2 = cs2["hotbar"].getItemStack(JShort(0))
    rw = Aug.apply(inv2, JInt(0), JInt(0), JString(sw), FP.fp(it2), JInt(0), JString("Skyy_Aug_Brute_1"), u, JString("Tester"))
    Fail.FAIL = -1
    if int(rw[0]) != -1 or count(cs2, "Skyy_Aug_Brute_1") != 3 or [str(x) for x in Aug.raw(Data.gearDoc(cs2["hotbar"].getItemStack(JShort(0)).getMetadata()))] != []:
        xb.append(("a refused write = the augments back, the item unchanged", str(rw[1]), count(cs2, "Skyy_Aug_Brute_1")))
    inv3, cs3 = mkinv()
    cs3["hotbar"].setItemStackForSlot(JShort(0), stack(sw, doc(sw, r=4), q=2))
    cs3["storage"].setItemStackForSlot(JShort(0), IS(JString("Skyy_Aug_Brute_1"), JInt(1)))
    it3 = cs3["hotbar"].getItemStack(JShort(0))
    rst = Aug.apply(inv3, JInt(0), JInt(0), JString(sw), FP.fp(it3), JInt(0), JString("Skyy_Aug_Brute_1"), u, JString("Tester"))
    if int(rst[0]) != 0 or "stack of 2" not in str(rst[1]) or count(cs3, "Skyy_Aug_Brute_1") != 1:
        xb.append(("a stack of 2 refused", str(rst[1])))
    # slots: add (coins first, Smithing level, the cap), remove (empty added only)
    c0 = COINS[0]
    it_ = at0()
    ra = Aug.addSlot(inv, JInt(0), JInt(0), JString(sw), FP.fp(it_), u, JString("Tester"))
    cost = int(Aug.slotCost(JInt(4)))          # Fabled
    d_ = Data.gearDoc(at0().getMetadata())
    if int(ra[0]) != 1 or int(Aug.added(d_)) != 1 or int(Aug.slots(JString(sw), d_)) != 4 or COINS[0] != c0 - cost or cost <= 0:
        xb.append(("addSlot", str(ra[1]), COINS[0], c0, cost))
    rb = Aug.addSlot(inv, JInt(0), JInt(0), JString(sw), FP.fp(at0()), u, JString("Tester"))
    if int(rb[0]) != 0 or "the most is 1" not in str(rb[1]) or COINS[0] != c0 - cost:
        xb.append(("addSlot past aug.extraSlots refused, no coins", str(rb[1])))
    cs["storage"].setItemStackForSlot(JShort(7), IS(JString("Skyy_Aug_Air_1"), JInt(1)))
    ap(3, "Skyy_Aug_Air_1")          # into the added 4th slot
    rc = Aug.removeSlot(inv, JInt(0), JInt(0), JString(sw), FP.fp(at0()), u, JString("Tester"))
    if int(rc[0]) != 0 or "never come out" not in str(rc[1]) or augs()[3:4] != ["E:Air:1"]:
        xb.append(("removeSlot of a filled added slot refused", str(rc[1]), augs()))
    inv4, cs4 = mkinv()
    cs4["hotbar"].setItemStackForSlot(JShort(0), stack(sw, doc(sw, r=4, add=1)))
    rd = Aug.removeSlot(inv4, JInt(0), JInt(0), JString(sw), FP.fp(cs4["hotbar"].getItemStack(JShort(0))), u, JString("Tester"))
    d4 = Data.gearDoc(cs4["hotbar"].getItemStack(JShort(0)).getMetadata())
    if int(rd[0]) != 1 or int(Aug.added(d4)) != 0 or d4.containsKey("augAdd"):
        xb.append(("removeSlot of an empty added slot", str(rd[1])))
    inv6, cs6 = mkinv()
    cs6["hotbar"].setItemStackForSlot(JShort(0), stack(sw, doc(sw, r=4, add=1, aug=["", "", "", "E:Fire:11"])))
    rf3 = Aug.removeSlot(inv6, JInt(0), JInt(0), JString(sw), FP.fp(cs6["hotbar"].getItemStack(JShort(0))), u, JString("Tester"))
    d6 = Data.gearDoc(cs6["hotbar"].getItemStack(JShort(0)).getMetadata())
    K.check(int(rf3[0]) == 0 and "cannot read" in str(rf3[1]) and int(Aug.added(d6)) == 1 and [str(x) for x in Aug.raw(d6)][3:4] == ["E:Fire:11"],
            "FIX F3: Remove slot refuses an added slot holding an unreadable entry (kept): %s" % str(rf3[1]))
    LV["Smithing"] = 3
    P("GearGate").forget(u)
    re_ = Aug.addSlot(inv4, JInt(0), JInt(0), JString(sw), FP.fp(cs4["hotbar"].getItemStack(JShort(0))), u, JString("Tester"))
    LV["Smithing"] = 12
    P("GearGate").forget(u)
    if int(re_[0]) != 0 or "Smithing Lv 10" not in str(re_[1]):
        xb.append(("addSlot under Smithing 10 refused", str(re_[1])))
    K.check(not xb, "X apply on REAL inventories: add from the inventory (+ Smithing XP), replace from the bags (take + commit; the old one destroyed), "
            "add + fuse (one each), 6 refusals move nothing, a short bag / a refused write = everything back, a stack of 2 refused; addSlot (coins "
            "first, the cap, Smithing Lv 10) / removeSlot (filled refused, empty added removed): %s" % xb)
    K.notes.append("X N = %s; last messages: %s | %s | %s" % (list(Aug.N), r2[1], r4[1], str(ra[1])))

    # ================================================================================== K tools + gathering armor
    kb = []
    pk = str(Gear.pkey(u))
    dl = doc(pickT, r=2, aug=["S:Delver:5", "S:Prospector:5"])          # T10: 3 slots (an Iron one has 1)
    dl.put("ll", BI(JInt(1)))
    dl.put("lo", BS(JString(pk)))
    fx = [round(float(x), 6) for x in Aug.toolFx(JString(pickT), dl)]
    dli = doc(pick, r=2, aug=["S:Delver:5", "S:Prospector:5"])
    dli.put("ll", BI(JInt(1)))
    if [round(float(x), 6) for x in Aug.toolFx(JString(pick), dli)] != [3.0, 6.0, 0.0, 0.0]:
        kb.append(("an Iron lifelong pickaxe has 1 slot: only the first counts", list(Aug.toolFx(JString(pick), dli))))
    if fx != [7.0, 6.0, 25.0, 0.0]:
        kb.append(("toolFx", fx))
    dl0 = doc(pickT, r=2)
    dl0.put("ll", BI(JInt(1)))
    dl0.put("lo", BS(JString(pk)))
    P("GearGate").forget(u)
    s_a = Tool.stats(u, stack(pickT, dl))
    s_b = Tool.stats(u, stack(pickT, dl0))
    if s_a is None or s_b is None or (float(s_b[3]) > 0 and (abs(float(s_a[4]) - min(float(s_b[4]) * 1.06, float(Cfg.pmax()))) > 1e-6 or abs(float(s_a[5]) - min(round((float(s_b[5]) + 25.0) * 10) / 10.0, float(Cfg.fcap()))) > 0.051)):
        kb.append(("GearTool.stats: Delver Power x1.06, Prospector +25 Fortune", None if s_a is None else list(s_a)[:6], None if s_b is None else list(s_b)[:6]))
    K.notes.append("K GearTool.stats with / without: %s / %s" % (None if s_a is None else [round(float(x), 3) for x in list(s_a)[:9]], None if s_b is None else [round(float(x), 3) for x in list(s_b)[:9]]))
    reg = Props()
    reg.setProperty("pickaxe.id", JString(pickT))
    reg.setProperty("pickaxe.uid", JString("harness-uid"))
    LL.REG.put(JString(pk), reg)
    sv_a = float(LL.swingOf(u, stack(pickT, dl)))
    sv_b = float(LL.swingOf(u, stack(pickT, dl0)))
    if abs(sv_a - sv_b - 7.0) > 1e-6:
        kb.append(("swingOf: + 7 % Breaking Speed (Prospector 4 + Delver 3)", sv_a, sv_b))
    if mine:
        ar = SIC(JShort(4))
        ar.setItemStackForSlot(JShort(0), stack(mine, doc(mine, r=3, aug=["S:Scholar:5", "S:Prospector:5"])))          # Legendary: 2 slots
        Aug.noteArmor(u, ar)
        a0 = [round(float(x), 6) for x in Aug.armFx(u, 0)]
        a2 = [round(float(x), 6) for x in Aug.armFx(u, 2)]
        Aug.noteArmor(u, SIC(JShort(4)))
        a3 = [float(x) for x in Aug.armFx(u, 0)]
        if a0 != [4.0, 0.0, 40.0, 3.0] or a2 != [0.0] * 4 or a3 != [0.0] * 4 or Aug.ARM.get(u) is not None:
            kb.append(("noteArmor / armFx (Mining row: Breaking Speed 4, Fortune 25 + 15, Wisdom 3)", a0, a2, a3))
        Aug.noteArmor(u, ar)
        sv_c = float(LL.swingOf(u, stack(pickT, dl0)))
        if abs(sv_c - sv_b - 4.0) > 1e-6:
            kb.append(("swingOf + the worn Mining armor's 4 %", sv_c, sv_b))
        gsrc = None
        try:
            Tool.LAST.clear()
            Tool.held(u, stack(pickT, dl0))
            bon = br.get("skill:bonus:" + U)
            gsrc = bon.get(Tool.SRC) if bon is not None else None
        except Exception as ex_:
            K.notes.append("K GearTool.held threw in the bare boot: %s" % str(ex_)[:300])
        K.notes.append("K the held post with Mining armor augments: %s" % gsrc)
        if gsrc is None or float(gsrc.get("xp.mining")) < 0.03 - 1e-9:
            kb.append(("GearTool.held posts the armor's Wisdom", gsrc))
        Aug.ARM.clear()
    else:
        kb.append("no Mining armor piece in the bare boot")
    K.check(not kb, "K tools: toolFx (Prospector + Delver), GearTool.stats of a lifelong pickaxe (Power x 1.06, + 25 Fortune), GearLL.swingOf (+7 %%), "
            "noteArmor / armFx (the Mining row; cleared when taken off), the worn armor's Breaking Speed + the held post's Wisdom: %s" % kb)

    # ================================================================================== U tooltip + the Augments tab
    ub = []
    txt, col = AL(), AL()
    dtp = doc(sw, r=3, aug=["S:Brute:3", "E:Fire:7", "S:Bulwark:2", "E:Air:2"])          # Legendary 2 slots: the last two are past the slots
    View.lines(JString(sw), dtp, u, txt, col)
    tl = [str(x) for x in txt]
    cl = [None if x is None else str(x) for x in col]
    if "AUGMENTS" not in tl:
        ub.append(("no AUGMENTS section", tl))
    else:
        i0 = tl.index("AUGMENTS")
        sec = tl[i0 + 1:i0 + 7]
        if sec[0] != "2 of 2 augment slots filled" or not sec[1].startswith("[Brute III]" + chr(2)) or not sec[2].startswith("[Fire VII]" + chr(2)) \
                or "(no slot - counts nothing)" not in sec[3] or "(no slot" not in sec[4] or not sec[5].startswith("ELEMENT POWER") or "Fire 7" not in sec[5] \
                or not cl[i0 + 2].startswith("&*") or ("STATS" in tl and tl.index("STATS") > i0):
            ub.append(("section", sec, cl[i0 + 1:i0 + 7]))
    K.notes.append("U tooltip lines: %s" % [x.replace(chr(2), "|") for x in tl])
    K.check("Fractions add up with your other gear lines (each stat's total is rounded once)." in tl and "Salvaging or selling this item destroys its augments." in tl
            and tl.index("Salvaging or selling this item destroys its augments.") > tl.index([x for x in tl if x.startswith("ELEMENT POWER")][0] if [x for x in tl if x.startswith("ELEMENT POWER")] else "AUGMENTS"),
            "FIX F6: the tooltip says fractions add up (Brute III: 2.8 Strength) + salvage destroys augments, after ELEMENT POWER")
    txu, cou = AL(), AL()
    View.lines(JString(sw), doc(sw, r=4, aug=["E:Fire:11", "S:Edge:1"]), u, txu, cou)
    tlu = [str(x) for x in txu]
    K.check("[ unreadable ] kept - this version cannot read it" in tlu and "2 of 3 augment slots filled" in tlu, "FIX F3: the tooltip shows an unreadable entry as kept: %s" % tlu[-6:])

    # ---- FIX ROUND 2 (second critics): G1 invested, G2 merge cap + summed paid slots, G3 retired / foreign lifelong tool, G4 ELEMENT POWER = power()
    LLc = P("GearLL")
    gb = []
    pkG = str(Gear.pkey(u))
    def lld(iid, lo=pkG, rt=False, rp=False, **kw):
        d_ = doc(iid, r=2, **kw)
        d_.put("ll", BI(JInt(1)))
        d_.put("lo", BS(JString(lo)))
        if rt:
            d_.put("lrt", BI(JInt(1)))
        if rp:
            t_ = int(LLc.tier(JString(iid)))
            d_.put("lrp", BI(JInt(1)))
            d_.put("lrpT", BI(JInt(t_)))
            d_.put("lrpL", BI(JInt(int(LLc.lrank(JString(iid))))))
        return d_
    rp0 = lld(pickT, rp=True)
    rp1 = lld(pickT, rp=True)
    rp1.put("agN", BI(JInt(1)))
    rp2 = lld(pickT, rp=True)
    rp2.put("agN", BI(JInt(2)))
    rp2.put("lrpA", BI(JInt(2)))
    inv_g = [bool(LLc.invested(JString(pickT), x_)) for x_ in (rp0, rp1, rp2)]
    if inv_g != [False, True, False]:
        gb.append(("G1 invested: plain copy no, an augment after the copy yes, the copy's own baseline no", inv_g))
    nwl = Aug.docWith(lld(pickT, rp=True), JInt(0), JString("S:Delver:1"), JInt(3))
    nws = Aug.docWith(doc(sw, r=4), JInt(0), JString("S:Edge:1"), JInt(3))
    if int(Data.num(nwl, JString("agN"), JInt(0))) != 1 or not bool(LLc.invested(JString(pickT), nwl)) or nws.containsKey("agN"):
        gb.append("G1 docWith bumps agN on a lifelong tool only (and that invests a replacement)")
    big = ["E:Fire:%d" % (1 + i % 9) for i in range(20)]
    cg = doc(pick)
    Aug.carry(cg, doc(pick, aug=big, add=1), doc(pick, aug=big, add=1))
    if len(list(Aug.raw(cg))) != 32 or int(Aug.added(cg)) != 2 or len(list(Aug.raw(doc(pick, aug=big + big)))) != 32:
        gb.append(("G2 carry: 32 kept (raw reads 32), paid slots summed", len(list(Aug.raw(cg))), int(Aug.added(cg))))
    cg2 = doc(pick)
    Aug.carry(cg2, doc(pick, add=6), doc(pick, add=5))
    if int(Aug.added(cg2)) != 8:
        gb.append(("G2 carry: summed paid slots stop at 8", int(Aug.added(cg2))))
    pr_ = Aug.plan(JString(pickT), lld(pickT, rt=True), JInt(0), JInt(12), JInt(1))
    if int(pr_[0]) != -1 or "Only your own working lifelong tool" not in str(pr_[1]):
        gb.append(("G3 plan refuses a retired lifelong tool", str(pr_[1])))
    c0g = COINS[0]
    res_g = []
    for lo_, rt_ in ((pkG, True), ("someone-else", False), (pkG, False)):
        inv_x, cs_x = mkinv()
        cs_x["hotbar"].setItemStackForSlot(JShort(0), stack(pickT, lld(pickT, lo=lo_, rt=rt_)))
        cs_x["storage"].setItemStackForSlot(JShort(3), IS(JString("Skyy_Aug_Delver_1"), JInt(1)))
        it_x = cs_x["hotbar"].getItemStack(JShort(0))
        ra_ = Aug.apply(inv_x, JInt(0), JInt(0), JString(pickT), FP.fp(it_x), JInt(0), JString("Skyy_Aug_Delver_1"), u, JString("Tester"))
        left_ = cs_x["storage"].getItemStack(JShort(3))
        rs_ = Aug.addSlot(inv_x, JInt(0), JInt(0), JString(pickT), FP.fp(cs_x["hotbar"].getItemStack(JShort(0))), u, JString("Tester"))
        dx_ = Data.gearDoc(cs_x["hotbar"].getItemStack(JShort(0)).getMetadata())
        res_g.append((int(ra_[0]), str(ra_[1])[:60], left_ is not None and not left_.isEmpty(), int(rs_[0]), int(Data.num(dx_, JString("agN"), JInt(0)))))
    if [(r_[0], r_[2], r_[3], r_[4]) for r_ in res_g[:2]] != [(0, True, 0, 0), (0, True, 0, 0)] or COINS[0] != c0g - int(Aug.slotCost(JInt(2))) \
            or res_g[2][0] != 1 or res_g[2][2] or res_g[2][3] != 1 or res_g[2][4] != 2:
        gb.append(("G3 retired / another profile's lifelong tool: apply + addSlot refused, nothing taken; G1 own tool: apply + addSlot bump agN to 2", res_g, COINS[0], c0g))
    tg, cgx = AL(), AL()
    View.lines(JString(sw), doc(sw, r=4, mods=[("fFire", 2)]), u, tg, cgx)
    tgl = [str(x) for x in tg]
    tg2, cg2x = AL(), AL()
    View.lines(JString(sw), doc(sw, r=4, aug=["E:Fire:2"], mods=[("fFire", 2)]), u, tg2, cg2x)
    tg2l = [str(x) for x in tg2]
    ep1 = [x for x in tgl if x.startswith("ELEMENT POWER")]
    ep2 = [x for x in tg2l if x.startswith("ELEMENT POWER")]
    if not ep1 or "Fire 3" not in ep1[0] or not ep2 or "Fire 5" not in ep2[0]:
        gb.append(("G4 ELEMENT POWER = what a hit sends (rolled line 3, + Fire II = 5)", ep1, ep2))
    K.check(not gb, "FIX ROUND 2: G1 a /pickaxe copy with a later augment / paid slot is invested (agN > lrpA; docWith + addSlot bump it on lifelong tools only), "
            "G2 a merge keeps 32 entries + sums the paid slots (max 8), G3 a retired / another profile's lifelong tool takes nothing (no item, no coins), "
            "G4 the tooltip's ELEMENT POWER = power(): %s" % gb)
    K.notes.append("FIX ROUND 2: %s" % res_g)
    txw, cow = AL(), AL()
    View.lines(JString(sw), doc(sw, r=4, aug=["E:Fire:10"]), u, txw, cow)
    K.check("Fractions add up with your other gear lines (each stat's total is rounded once)." not in [str(x) for x in txw],
            "FIX F6: no fraction note when nothing rounds (a weapon element is exact per hit)")
    pl_ = [str(x) for x in View.plain(JString(sw), dtp, u)]
    if "AUGMENTS" in pl_:
        ub.append("plain() keeps the section title")
    txt2, col2 = AL(), AL()
    View.lines(JString(sw), doc(sw, r=0), u, txt2, col2)
    txt3, col3 = AL(), AL()
    View.lines(JString(helm), doc(helm, r=0), u, txt3, col3)
    if "1 of 1" in " ".join(str(x) for x in txt2) or "AUGMENTS" not in [str(x) for x in txt2] or "AUGMENTS" in [str(x) for x in txt3]:
        ub.append(("a Normal sword shows 0 of 1; a Normal helm (0 slots) no section", [str(x) for x in txt2][-6:]))
    # the page
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    pr = us.allocateInstance(PR.class_)
    fld(PR, "uuid").set(pr, u)
    fld(PR, "username").set(pr, JString("Tester"))
    RP = P("ReforgePage")
    pg = us.allocateInstance(RP.class_)
    k_ = RP.class_
    while k_ is not None:
        for f_ in k_.getDeclaredFields():
            if f_.getType() == PR.class_:
                f_.setAccessible(True)
                f_.set(pg, pr)
        k_ = k_.getSuperclass()
    IDRX = re.compile(r"#([A-Za-z0-9]+)\s*\{")
    SELRX = re.compile(r"#([A-Za-z0-9]+)")

    def walk(b_, ev_, have):
        have = set(have)
        miss = []
        for c in b_.getCommands():
            t_ = str(c.type)
            sel = str(c.selector) if c.selector is not None else ""
            for n_ in SELRX.findall(sel):
                if n_ not in have:
                    miss.append((t_, sel))
            if "Append" in t_ or "Insert" in t_:
                have.update(IDRX.findall(str(c.text) if c.text is not None else ""))
        unb = [str(e.selector) for e in ev_.getEvents() if any(n_ not in have for n_ in SELRX.findall(str(e.selector)))]
        return miss, unb, have

    def texts(b_):
        out_ = {}
        for c in b_.getCommands():
            if str(c.type) == "Set" and c.selector is not None and str(c.selector).endswith(".Text"):
                v = str(c.data) if c.data is not None else ""
                try:
                    o_ = json.loads(v)
                    if isinstance(o_, dict):
                        o_ = o_.get("0", list(o_.values())[0] if o_ else "")
                    v = o_ if isinstance(o_, str) else str(o_)
                except Exception:
                    pass
                out_[str(c.selector)[1:-5]] = v
        return out_
    inv5, cs5 = mkinv()
    cs5["hotbar"].setItemStackForSlot(JShort(0), stack(sw, doc(sw, r=4, aug=["S:Brute:3"])))
    cs5["storage"].setItemStackForSlot(JShort(0), IS(JString("Skyy_Aug_Edge_2"), JInt(1)))
    cs5["storage"].setItemStackForSlot(JShort(1), IS(JString("Skyy_Aug_Fire_1"), JInt(2)))
    cs5["storage"].setItemStackForSlot(JShort(2), IS(JString("Skyy_Aug_Bulwark_1"), JInt(1)))
    BAG.clear()
    pg.anAugM = True
    pg.epoch = Gear.epoch(u)
    pg.info = JString("")
    if not bool(pg.anFitsMode(cs5["hotbar"].getItemStack(JShort(0)))) or bool(pg.anFitsMode(IS(JString("Skyy_Aug_Edge_2"), JInt(1)))):
        ub.append("anFitsMode on the Augments tab")
    rows = pg.anRows(inv5)
    if rows.size() != 1:
        ub.append(("anRows: only the gear that holds augments", rows.size()))
    ok_ = bool(pg.anPick(inv5, JInt(0), JInt(0)))
    sel = cs5["hotbar"].getItemStack(JShort(0))

    def build(have_sel=True):
        b_, ev_ = UCB(), UEB()
        b_.appendInline(JString("#SkyyGBody"), JString("Group #SkyyGMain { }"))
        pg.anAugPanel(b_, ev_, u, sel if have_sel else None, inv5, JLong(5000))
        miss, unb, have = walk(b_, ev_, ("SkyyGBody",))
        return miss, unb, texts(b_), [str(c.text) for c in b_.getCommands() if c.text is not None]
    m0, u0, t0_, a0_ = build(False)
    pg.anAgSlot = 0
    pg.anAgPick = None
    m1, u1, t1_, a1_ = build()
    pg.anAgPick = JString("Skyy_Aug_Edge_2")
    m2, u2, t2_, a2_ = build()
    pg.anAgSlot = 1
    m3, u3, t3_, a3_ = build()
    pg.anAgPick = JString("Skyy_Aug_Bulwark_1")
    m4, u4, t4_, a4_ = build()
    pg.anAgF = 2
    m5, u5, t5_, a5_ = build()
    pg.anAgF = 0
    apply(aug__extraSlots="3", **BASE)
    sel_keep = sel
    sel = stack(sw, doc(sw, r=5, add=3, aug=["S:Precision:3", "E:Fire:11"]))          # Mythic 3 + 3 added = 6 slots
    pg.anAgSlot = 0
    m6, u6, t6_, a6_ = build()
    sel = sel_keep
    apply(**BASE)
    slotsx = [x for x in a6_ if "#SkyyGAgS" in x and "Button" in x]
    K.check(len(slotsx) == 6 and not any("ItemIcon" in x for x in slotsx) and all("ShrinkTextToFit: true" in x and "Wrap" not in x for x in slotsx)
            and t6_.get("SkyyGAgSL0") == "Precision III" and t6_.get("SkyyGAgSL1") == "Unreadable (kept)" and not m6 and not u6,
            "FIX F7 + F3: 6 slots drop the icon and shrink (no wrap); an unreadable slot shows 'Unreadable (kept)': %s %s" % ([t6_.get("SkyyGAgSL%d" % i) for i in range(6)], (m6 + u6)[:2]))
    if m0 or u0 or m1 or u1 or m2 or u2 or m3 or u3 or m4 or u4 or m5 or u5:
        ub.append(("selectors", (m0 + m1 + m2 + m3 + m4 + m5)[:3], (u0 + u1 + u2 + u3 + u4 + u5)[:3]))
    btn = lambda a_: [x for x in a_ if "#SkyyGAgDo" in x]
    b1 = re.search(r'#SkyyGAgDo \{[^}]*Text: "([^"]*)"', " ".join(a1_))
    if t1_.get("SkyyGAgHead", "").find("AUGMENT SLOTS  1 / 3") != 0 or t1_.get("SkyyGAgSL0") != "Brute III" or t1_.get("SkyyGAgSL1") != "Empty" \
            or "SkyyGAgR" + str(IDS.index("Skyy_Aug_Edge_2")) + "" not in " ".join(a1_) or (b1 and b1.group(1) != "Pick an augment"):
        ub.append(("panel", t1_.get("SkyyGAgHead"), t1_.get("SkyyGAgSL0"), t1_.get("SkyyGAgSL1"), b1 and b1.group(1)))
    def dobtn(a_):
        mm = re.search(r'#SkyyGAgDo \{[^}]*Text: "([^"]*)"', " ".join(a_))
        return mm.group(1) if mm else None
    dos = [dobtn(a1_), dobtn(a2_), dobtn(a3_), dobtn(a4_)]
    if dos != ["Pick an augment", "Replace slot 1", "Add to slot 2", "Cannot go there"]:
        ub.append(("the Do button per plan", dos))
    gtxt = t1_.get("SkyyGAgRG%d" % IDS.index("Skyy_Aug_Bulwark_1"), "")
    if not gtxt.startswith("Fits combat armor") or not t1_.get("SkyyGAgRG%d" % IDS.index("Skyy_Aug_Edge_2"), "").startswith("+"):
        ub.append(("row gives / fits", gtxt))
    K.notes.append("U panel texts: head %r, rows %d" % (t1_.get("SkyyGAgHead"), len([k for k in t1_ if k.startswith("SkyyGAgRN")])))
    if len([k for k in t5_ if k.startswith("SkyyGAgRN")]) != 1:
        ub.append(("the Elemental filter shows only Fire I", [t5_[k] for k in t5_ if k.startswith("SkyyGAgRN")]))
    # anAugDo: replace = arm, then the write
    pg.anAgSlot = 0
    pg.anAgPick = JString("Skyy_Aug_Edge_2")
    pg.lastForge = JLong(0)
    pg.anAugDo(inv5)
    i1 = str(pg.info)
    pg.lastForge = JLong(0)
    pg.anAugDo(inv5)
    i2 = str(pg.info)
    d5 = Data.gearDoc(cs5["hotbar"].getItemStack(JShort(0)).getMetadata())
    if not i1.startswith("=Click Confirm") or "Brute III will be DESTROYED" not in i1 or not i2.startswith("+Edge II replaced Brute III") \
            or [str(x) for x in Aug.raw(d5)][:1] != ["S:Edge:2"] or count(cs5, "Skyy_Aug_Edge_2") != 0:
        ub.append(("anAugDo arm + write", i1, i2))
    pg.anAgSlot = 1
    pg.anAgPick = JString("Skyy_Aug_Fire_1")
    pg.lastForge = JLong(0)
    pg.anAugDo(inv5)
    i3 = str(pg.info)
    pg.lastForge = JLong(0)
    pg.anAugSlotDo(inv5, True)
    i4 = str(pg.info)
    if not i3.startswith("+Fire I is in slot 2") or not i4.startswith("+Added a slot"):
        ub.append(("anAugDo add / anAugSlotDo", i3, i4))
    b_, ev_ = UCB(), UEB()
    b_.appendInline(JString("#SkyyGSub"), JString("Group #SkyyGHp { }"))
    P("GearHub").anvilSub3(b_, ev_, JInt(2), True, True)
    sub = " ".join(str(c.text) for c in b_.getCommands() if c.text is not None) + " " + " ".join(str(getattr(e, "data", e)) for e in ev_.getEvents())
    K.notes.append("U sub-tab row: %d commands, %d events" % (len(list(b_.getCommands())), len(list(ev_.getEvents()))))
    if "Augments" not in sub or "mode:7" not in sub:
        ub.append(("anvilSub3", sub[:300]))
    K.check(not ub, "U the tooltip AUGMENTS section (count, slots in the tier colour + gain, past the slots '(no slot)', ELEMENT POWER, after STATS; plain() "
            "skips the title; a 0-slot helm shows none), the Augments panel on REAL builders walked like the client (head, slots, rows, filter), anAugDo "
            "(Replace arms, the second click writes; Add), anAugSlotDo, anRows / anFitsMode, anvilSub3: %s" % ub)
    K.check("augments on (120 items" in str(Aug.statusText()), "U the ready-line part: %s" % str(Aug.statusText())[:200])
    K.notes.append("U status: " + str(Aug.statusText()))
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
    K.check(not [l for l in c1.decode("latin-1").splitlines() if l.startswith("aug.") or l.startswith("part.augments")] and bool(Cfg.AUG_ON) and bool(Cfg.AUG_STATES)
            and [int(x) for x in Cfg.AUG_SW] == [1, 1, 2, 2, 3, 3, 1, 2] and int(Cfg.AUG_EXTRA) == 1, "D the live file has no augment line; the rows read their defaults")
    dl = c0.decode("latin-1").splitlines()
    dn = c1.decode("latin-1").splitlines()
    extra = [l for l in dn if l not in dl]
    K.check(c1 == c0 or all(l.startswith("stats.as=") or "SkyyGear 0.3.5" in l or l.strip() == "" for l in extra),
            "D only the 0.3.50 / 0.3.51 updates may touch the file (0.3.52 adds none): %s" % extra[:5])
    K.save()


HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("engine", run_engine), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
