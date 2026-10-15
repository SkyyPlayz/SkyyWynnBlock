"""Harness for SkyyArmory 0.1.26 (CASTER SPEED TIERS; tools/armory_0_1_26_patch.py). Build first:
    python tools/armory_0_1_26_patch.py && python SkyyArmory/build_skyyarmory_0.1.26.py

    python SkyyArmory/test_skyyarmory_0.1.26.py [--jar <SkyyArmory-0.1.26.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.25 -> 0.1.26: exactly the listed members differ, ArmorySpeedFn added; non-class: only the speed files added (3 effects +
               16 trees + 16 x 3 tier copies of the Charging / quick / quick spend + the Wand_Primary root override), the 15 owned root files +
               the manifest changed; every other file byte for byte the same; Rico.gain calls ArmorySpeedFn.handW for the quick hits only
  T   assets   THE TREES FROM THE JAR: every root -> its tree; the tree = Match None -> the Medium Charging, then Slow / Fast / Super Fast leaves
               (TriggerCooldown 0.49 / 0.245 / 0.175 -> the tier Charging); a tier Charging = the Medium one with only key 0 changed; the
               tier quick = the Medium quick with only Costs / RunTime / its spend changed; the hold (charged) untouched; DPS (per hit x w /
               cycle) and Mana per second (cost / cycle) within 2 % of Medium on every root and tier; the 3 effects = the hidden marker
  X   exec     EVERY NEW CODE PATH without an engine: armory:fn:speed "effects" / "weights" / an id while the items are not loaded ("unloaded")
               / bad arguments (null, never a throw); rootIndex; live() off the asset maps (false, no throw); handW with a gear:fn:speed stand-in
               (1.4 / 0.5 / 1 / junk / a throw / none -> clamped); statusText; the key is published and in the shutdown list
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyArmory: the 2nd start changes nothing, 0.1.26 does not rewrite the file
  AA  audit    the engine-access audit
The engine-backed checks (the pack loads with every codec validator, armory:fn:speed on the REAL items / roots, SkyyGear's families, effects,
hits and tooltips) run in SkyyGear/test_skyygear_0.3.8.py (H38), which loads this jar as a pack. Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.26", "0.1.25"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "caster", "armory")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyArmory")
METALS = ["Wood", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
W = [1.4, 1.0, 0.7, 0.5]
TAG = ["S", "M", "F", "X"]
EFF = ["SkyyArmory_Speed_Slow", "", "SkyyArmory_Speed_Fast", "SkyyArmory_Speed_SuperFast"]
WQ = [1, 2, 3, 5, 8, 12, 17, 17]          # the quick Mana ladder (wands); staffs = 2x
# the members 0.1.26 changes (version texts are normalised to VER, so only real changes show): Rico.gain (the meter weight), ArmoryCheck
# (+ speedCheck, packCheck runs it + new words), ArmoryDefs <clinit> (the check lists grew), the plugin (publish / unpublish: the new key in the
# list; setup: the new ready line)
EXPECT = {"ArmoryCheck": ["+m speedCheck", "~m packCheck"], "SkyyArmoryPlugin": ["~m publish", "~m setup", "~m unpublish"],
          "Rico": ["~m gain"], "ArmoryDefs": ["~<clinit>"],
          "CfgRows": ["~<clinit>"]}          # fix round: the read-only rows' help texts (Medium speed tier)
ADDED = ["ArmorySpeedFn"]


def jread(z, n):
    return json.loads(z.read(n).decode("utf-8"))


def specs():
    """(root id, root path, family, Medium Charging, its path, interaction dir, quick, spend, quick pid, quick Mana, tap RunTime, hold key)"""
    pw, ps = "Server/Item/Interactions/Weapons/Wand/SkyyArmory/", "Server/Item/Interactions/Weapons/Staff/SkyyArmory/"
    out = [("Wand_Primary", "Server/Item/RootInteractions/Weapons/Wand/Wand_Primary.json", 0, "Wand_Primary",
            "Server/Item/Interactions/Weapons/Wand/Wand_Primary.json", pw, "SkyyArmory_Wand_Quick_Wood", "SkyyArmory_Wand_Quick_Cost_Wood",
            "SkyyArmory_QuickOrb_Wood", 1, 0.1, "0.35")]
    for i, m in enumerate(METALS):
        if m != "Wood":
            r = "SkyyArmory_Wand_Primary_" + m
            out.append((r, "Server/Item/RootInteractions/Weapons/Wand/SkyyArmory/%s.json" % r, 0, r, pw + r + ".json", pw, "SkyyArmory_Wand_Quick_" + m,
                        "SkyyArmory_Wand_Quick_Cost_" + m, "SkyyArmory_QuickOrb_" + m, WQ[i], 0.1, "0.35"))
    for i, m in enumerate(METALS):
        r = "SkyyArmory_Staff_Primary_" + m
        out.append((r, "Server/Item/RootInteractions/Weapons/Staff/SkyyArmory/%s.json" % r, 1, r, ps + r + ".json", ps, "SkyyArmory_Staff_Quick_" + m,
                    "SkyyArmory_Staff_Quick_Cost_" + m, "SkyyArmory_StaffQuickOrb_" + m, 2 * WQ[i], 0.31, "1"))
    return out


# ---------------------------------------------------------------------------------------------------- T: the trees, read from the jar
def run_trees():
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    na, nb = set(za.namelist()), set(zb.namelist())
    SP = specs()
    HK.check(len(SP) == 16, "T: 16 tier roots (Wood wand + 7 metal wands + 8 ladder staffs)")
    rows = []
    for (r, rp, fam, med, medp, idir, qi, qc, qp, qm, rt, hk) in SP:
        root = jread(zb, rp)
        tree_id = "SkyyArmory_Spd_" + med
        HK.check(root == {"Interactions": [tree_id]}, "T: root %s runs its tree %s: %s" % (r, tree_id, root))
        if r == "Wand_Primary":
            HK.check(rp not in na, "T: the Wand_Primary root override is new in 0.1.26 (vanilla path)")
        else:
            HK.check(jread(za, rp) == {"Interactions": [med]}, "T: 0.1.25's root %s ran the Charging step directly" % r)
        # the Medium chain is 0.1.25's byte for byte
        HK.check(za.read(medp) == zb.read(medp) and za.read(idir + qi + ".json") == zb.read(idir + qi + ".json"),
                 "T: %s: the Medium Charging + quick files are 0.1.25's byte for byte" % r)
        tree = jread(zb, idir + tree_id + ".json")
        HK.check(tree.get("Type") == "EffectCondition" and tree.get("Match") == "None" and tree.get("EntityEffectIds") == [EFF[0], EFF[2], EFF[3]]
                 and tree.get("Next") == med, "T: %s tree: no tier effect -> the Medium Charging %s" % (r, med))
        node = tree.get("Failed")
        chm = jread(zb, medp)
        qm0 = jread(zb, idir + qi + ".json")
        cyc_m = max(rt, 0.35)
        dps_m, mps_m = 1.0 / cyc_m, qm / cyc_m
        got = {}
        for t in (0, 2, 3):
            HK.check(isinstance(node, dict) and node.get("Type") == "EffectCondition" and node.get("Match") == "All"
                     and node.get("EntityEffectIds") == [EFF[t]], "T: %s tree step %s checks %s" % (r, t, EFF[t]))
            leaf = node.get("Next") or {}
            cd = (leaf.get("Cooldown") or {}).get("Cooldown")
            cht = "SkyyArmory_Spd%s_%s" % (TAG[t], med)
            HK.check(leaf.get("Type") == "TriggerCooldown" and abs(cd - round(0.35 * W[t], 4)) < 1e-9 and leaf.get("Next") == cht,
                     "T: %s %s: TriggerCooldown %s -> %s" % (r, TAG[t], cd, leaf.get("Next")))
            ch = jread(zb, idir + cht + ".json")
            qit = "SkyyArmory_Spd%s_%s" % (TAG[t], qi)
            qct = "SkyyArmory_Spd%s_%s" % (TAG[t], qc)
            exp_ch = json.loads(json.dumps(chm))
            exp_ch["Next"]["0"] = qit
            HK.check(ch == exp_ch and ch["Next"][hk] == chm["Next"][hk], "T: %s %s: the tier Charging = Medium with only the tap changed (hold %s -> %s kept)" % (r, TAG[t], hk, chm["Next"][hk]))
            q = jread(zb, idir + qit + ".json")
            cost = round(qm * W[t], 1)
            rtt = round(min(rt * W[t], 0.35 * W[t] - 0.1), 4)
            exp_q = json.loads(json.dumps(qm0))
            exp_q["Costs"] = {"Mana": cost}
            exp_q["RunTime"] = rtt
            exp_q["Next"]["Interactions"][0] = {"Interactions": [qct]}
            HK.check(q == exp_q, "T: %s %s: the tier quick = Medium with Mana %s, RunTime %s, its own spend: %s" % (r, TAG[t], cost, rtt, q))
            HK.check(jread(zb, idir + qct + ".json") == {"Type": "ChangeStat", "StatModifiers": {"Mana": -cost}}, "T: %s %s: the spend = -%s Mana" % (r, TAG[t], cost))
            cyc = max(rtt, cd)
            got[t] = (W[t] / cyc, cost / cyc)
            node = node.get("Failed")
        HK.check(node == med, "T: %s tree ends at the Medium Charging" % r)
        bad = [(t, round(d / dps_m, 4), round(m / mps_m, 4)) for t, (d, m) in got.items() if abs(d / dps_m - 1) > 0.02 or abs(m / mps_m - 1) > 0.02]
        HK.check(not bad, "T: %s: damage per second and Mana per second within 2 %% of Medium on every tier: %s" % (r, bad))
        rows.append((r, [round(got[t][0] / dps_m, 4) for t in (0, 2, 3)], [round(got[t][1] / mps_m, 4) for t in (0, 2, 3)]))
    for t in (0, 2, 3):
        p = "Server/Entity/Effects/SkyyArmory/%s.json" % EFF[t]
        HK.check(jread(zb, p) == {"Duration": 3, "OverlapBehavior": "Overwrite"}, "T: %s = the hidden 3 s marker (SkyyGear_Speed_*'s shape)" % EFF[t])
    print("T. DPS / Mana-per-second ratios to Medium (Slow, Fast, Super Fast): " + "; ".join("%s %s %s" % (r, d, m) for r, d, m in rows[:4]) + " ...")
    # non-class entries: added = exactly the speed files; changed = the 15 owned roots + the manifest
    added = sorted(n for n in nb - na if not n.endswith(".class"))
    want_added = sorted(set(["Server/Entity/Effects/SkyyArmory/%s.json" % EFF[t] for t in (0, 2, 3)] + [SP[0][1]]
                            + [sp[5] + "SkyyArmory_Spd_%s.json" % sp[3] for sp in SP]
                            + [sp[5] + "SkyyArmory_Spd%s_%s.json" % (TAG[t], x) for sp in SP for t in (0, 2, 3) for x in (sp[3], sp[6], sp[7])]))
    HK.check(added == want_added and len(added) == 164, "T: the non-class files added = exactly the speed files (%d; %s)" % (len(added), sorted(set(added) ^ set(want_added))[:4]))
    HK.check(not [n for n in na - nb], "T: nothing removed")
    changed = sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n))
    HK.check(changed == sorted([sp[1] for sp in SP[1:]] + ["manifest.json"]), "T: changed = the 15 owned root files + the manifest: %s" % changed[:5])
    man = zb.read("manifest.json").decode("utf-8")
    HK.check('"0.1.26"' in man and "Speed tiers (with SkyyGear)" in man, "T: the manifest names the round")
    # FIX (critic 5): the read-only Server Setup rows say their quick numbers are Medium + how the tiers scale them (help text in the class pool)
    cls_new = b"".join(zb.read(n) for n in nb if n.endswith(".class"))
    cls_old = b"".join(za.read(n) for n in na if n.endswith(".class"))
    helps = [b"Quick numbers = Medium speed tier.", b"Quick = Medium speed tier.", b"its tap (Medium speed). Rotten and Tribal",
             b"Speed tiers (SkyyGear, per item): tap time, quick Mana and hit x 1.4 / 0.7 / 0.5."]
    gone = [b"damage before levels, SkyyGear level band.", b"the tap chain lengths, the look and the size path."]
    HK.check(all(h in cls_new for h in helps) and not [g for g in gone if g in cls_new] and all(g in cls_old for g in gone),
             "T FIX: the wand / staff / Wood wand / quick shot Server Setup help texts name the Medium tier and the speed scaling (old texts gone): %s"
             % [h for h in helps if h not in cls_new])


# ---------------------------------------------------------------------------------------------------- C: class compare (the kit's, own non-class rule)
def run_compare(out, jar, scratch, _home):
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
    pa, pb = pool_of(OLD_JAR), pool_of(jar)

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
            ln_ = re.sub(r"^((?:if\w*|goto(?:_w)?|jsr(?:_w)?)) -?\d+$", r"\1", ln_)
            lines_.append(ln_.replace(VERSION, "VER").replace(OLD, "VER"))
        return str(b_.getModifiers()) + "\n" + "\n".join(lines_)

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature()) + " " + str(f_.getModifiers())
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_
    na, nb = HK.jar_classes(OLD_JAR), HK.jar_classes(jar)
    K.eq(sorted(set(nb) - set(na)), sorted(PKG + a for a in ADDED), "C: classes added")
    K.eq(sorted(set(na) - set(nb)), [], "C: classes removed")
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = sorted(("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd)
    for k in sorted(diffs):
        print("   %-22s %s" % (k, ", ".join(diffs[k])))
    K.eq(sorted(diffs), sorted(EXPECT), "C: the classes that differ")
    for k in sorted(EXPECT):
        K.eq(sorted(diffs.get(k, [])), sorted(EXPECT[k]), "C: %s members" % k)

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
    K.check(calls("Rico", "gain", "ArmorySpeedFn.handW") and calls("ArmoryCheck", "packCheck", "ArmoryCheck.speedCheck")
            and calls("SkyyArmoryPlugin", "publish", "ArmorySpeedFn") and calls("SkyyArmoryPlugin", "setup", "ArmorySpeedFn.statusText"),
            "C: Rico.gain asks ArmorySpeedFn.handW, packCheck runs speedCheck, the plugin publishes ArmorySpeedFn + logs its status")
    # the ArmoryDefs <clinit> difference is ONLY the check lists (ROOT_CHECK + INT_CHECK grew) + the version text
    K.check("ArmorySpeedFn" not in str(members(pb, PKG + "ArmoryDefs")), "C: ArmoryDefs does not call the new class (lists only)")
    K.save()


# ---------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JString, JImplements, JOverride, JDouble
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Fn = JClass(PKG + "ArmorySpeedFn")
    f = Fn()
    K.eq(str(f.apply("effects")), "SkyyArmory_Speed_Slow,,SkyyArmory_Speed_Fast,SkyyArmory_Speed_SuperFast", "X1: armory:fn:speed effects")
    K.eq(str(f.apply("weights")), "1.4,1.0,0.7,0.5", "X1: armory:fn:speed weights")
    a = f.apply("Weapon_Staff_Wood")
    K.check(a is not None and str(a) == "unloaded", "X1: an id while the items are not loaded = \"unloaded\" (SkyyGear asks again later): %s" % a)
    K.check(f.apply(None) is None and f.apply(JArray(JObject)([JString("x")])) is None and f.apply(JObject(JDouble(1.0))) is None, "X1: bad arguments = null, never a throw")
    K.eq([int(Fn.rootIndex(x)) for x in ("Wand_Primary", "SkyyArmory_Wand_Primary_Copper", "SkyyArmory_Staff_Primary_Wood", "SkyyArmory_Staff_Primary_Onyxium", "Root_Weapon_Sword_Primary", None)],
         [0, 1, 8, 15, -1, -1], "X2: rootIndex (16 roots: Wood wand first, staffs 8-15; others / null -1)")
    K.check(len(Fn.R_ROOT) == 16 and len(Fn.T_CH) == 64 and len(Fn.T_COST) == 64 and str(Fn.T_CH[1]) == "" and str(Fn.T_CH[0]) == "SkyyArmory_SpdS_Wand_Primary"
            and abs(float(Fn.T_COST[4 * 8 + 3]) - 1.0) < 1e-9 and abs(float(Fn.T_COST[4 * 15 + 0]) - 47.6) < 1e-9,
            "X2: the tier tables (Wood staff Super Fast 1.0 Mana, Onyxium staff Slow 47.6)")
    K.check(not bool(Fn.live(0)) and not bool(Fn.live(-1)) and not bool(Fn.live(99)), "X3: live() without loaded roots = false, never a throw")
    st = str(Fn.statusText())
    K.check(st.startswith("caster speed tiers: 0/16 wand / staff roots run their tier tree") and "gear:fn:speed not loaded yet" in st, "X3: statusText: %s" % st[:160])
    UUID = JClass("java.util.UUID")
    U = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    br = JClass(PKG + "ArmoryDefs").bridge()
    K.eq([float(Fn.handW(U, "Weapon_Wand_Copper"))], [1.0], "X4: handW without SkyyGear = 1")
    ANS = {"v": None, "raise": False, "seen": []}

    @JImplements("java.util.function.Function")
    class GearSpeed(object):
        @JOverride
        def apply(self, o):
            ANS["seen"].append([str(x) for x in o])
            if ANS["raise"]:
                raise ValueError("boom")
            return ANS["v"]
    br.put("gear:fn:speed", GearSpeed())
    Dbl = JClass("java.lang.Double")
    res = []
    for v in (JObject(JDouble(1.4), Dbl), JObject(JDouble(0.5), Dbl), JObject(JDouble(1.0), Dbl), JString("junk"), JObject(JDouble(9.0), Dbl),
              JObject(JDouble(-1.0), Dbl), None):
        ANS["v"] = v
        res.append(round(float(Fn.handW(U, "Weapon_Wand_Copper")), 6))
    ANS["raise"] = True
    res.append(round(float(Fn.handW(U, "Weapon_Wand_Copper")), 6))
    K.eq(res, [1.4, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], "X4: handW = SkyyGear's applied weight (1.4 / 0.5 / 1), junk / out of range / null / a throw = 1")
    K.check(ANS["seen"][0] == ["applied", str(U), "Weapon_Wand_Copper"], "X4: handW asks gear:fn:speed {\"applied\", uuid, id}: %s" % ANS["seen"][:1])
    K.check(float(Fn.handW(None, "x")) == 1.0 and float(Fn.handW(U, None)) == 1.0, "X4: handW null arguments = 1")
    st2 = str(Fn.statusText())
    K.check("gear:fn:speed found" in st2, "X3: statusText sees gear:fn:speed")
    br.remove("gear:fn:speed")
    with zipfile.ZipFile(jar) as z_:
        pl_ = z_.read("com/skyy/armory/SkyyArmoryPlugin.class")
    K.check(pl_.count(b"armory:fn:speed") >= 1 and b"ArmorySpeedFn" in pl_, "X5: SkyyArmoryPlugin publishes armory:fn:speed (ArmorySpeedFn) and lists it for the shutdown removal")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    f = os.path.join(home, "config.properties")
    before = open(f, "rb").read() if os.path.isfile(f) else None
    files0 = sorted(os.listdir(home))
    snaps = []
    for start in (1, 2):
        for m in ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(f, "rb").read() if os.path.isfile(f) else None)
    K.check(snaps[0] == snaps[1], "D: the 2nd start changes nothing")
    K.check(before is None or snaps[0] == before, "D: the live copy's config.properties is not rewritten by 0.1.26 (no config change): %s" % (before is not None))
    K.check(sorted(f_ for f_ in os.listdir(home) if not f_.startswith("config-history")) == sorted(f_ for f_ in files0 if not f_.startswith("config-history")),
            "D: no new file in the data folder")
    K.notes.append("D: live config.properties %s bytes" % (len(before) if before else 0))
    K.save()


def main():
    phases = {"mkfake": lambda: HK.run_mkfake(os.path.join(SCRATCH, "fake"), JAR), "verify": lambda: HK.run_verify(HK.arg("--out"), JAR),
              "audit": lambda: HK.run_audit(HK.arg("--out"), JAR, os.path.join(SCRATCH, "fake")),
              "compare": lambda: run_compare(HK.arg("--out"), JAR, SCRATCH, None), "exec": lambda: run_exec(HK.arg("--out"), JAR, SCRATCH, None),
              "live": lambda: run_live(HK.arg("--out"), JAR, SCRATCH, HK.arg("--home"))}
    if "--phase" in sys.argv:
        try:
            phases[HK.arg("--phase")]()
        except SystemExit:
            raise
        except Exception:
            import traceback
            traceback.print_exc()
            sys.exit(1)
        return
    assert os.path.isfile(JAR) and os.path.isfile(OLD_JAR), (JAR, OLD_JAR)
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    os.makedirs(os.path.join(SCRATCH, "fake"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]

    def child(label, *extra):
        out = os.path.join(SCRATCH, "%s.json" % label)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--phase", label, "--out", out, "--dir", SCRATCH, "--jar", JAR] + list(extra), env=env)
        HK.check(p.returncode == 0, "%s: the child exited cleanly (%s)" % (label, p.returncode))
        return out
    try:
        run_trees()
        child("mkfake")
        for label in ("verify", "compare", "exec"):
            HK.take(child(label), label)
        home = os.path.join(SCRATCH, "live", "Skyy_SkyyArmory")
        if os.path.isdir(LIVE_DIR):
            shutil.copytree(LIVE_DIR, home)
            print("D. live Skyy_SkyyArmory copied (read-only source %s)" % LIVE_DIR)
            HK.take(child("live", "--home", home), "live")
        else:
            HK.check(False, "D: no live folder %s" % LIVE_DIR)
        outa = child("audit")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            HK.check(not a["refused"] and a["refs"] > 100, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            HK.check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, %d refused, control refused" % (a["refs"], a["classes"], len(a["refused"])))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyArmory %s harness: %d ok, %d fail(s)" % (VERSION, HK.OKS[0], len(HK.FAILS)))
    for f in HK.FAILS:
        print("FAIL:", f)
    sys.exit(1 if HK.FAILS else 0)


if __name__ == "__main__":
    main()
