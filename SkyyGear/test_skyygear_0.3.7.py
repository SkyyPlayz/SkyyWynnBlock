"""Harness for SkyyGear 0.3.7 = the 0.3.6 harness's children run on the 0.3.7 jar (only the listed, explained deviations) + SUMMONS GO TO THE
HOTBAR FIRST (tools/gear_0_3_7_patch.py header). Build first:
    python tools/gear_0_3_7_patch.py && python SkyyGear/build_skyygear_0.3.7.py

    python SkyyGear/test_skyygear_0.3.7.py [--keep] [--only assets,verify,compare,h37,g36,snd,life,till]

Phases (fresh child JVMs, -Xverify:all where classes load):
  S37  non-class entries 0.3.6 -> 0.3.7: the same entries, only manifest.json changes (it names the round); the same classes
  A    every class loads + verifies (-Xverify:all)
  C37  CLASS COMPARE 0.3.6 -> 0.3.7: only GearLife changes (+ dest, + toHot, ~ give2 / move / fromVault / fromRequip); give2, move and
       fromVault call dest, fromRequip calls toHot
  H37  ONE booted engine (the 0.3.5 life setup: vanilla pack + SkyyCollections + SkyyFishing packs, real containers), EXECUTED:
       A  chest summon, the SELECTED hotbar slot empty -> it lands there ("into your Hotbar N"), gear.log LL-SUMMON -> Hotbar N
       B  the selected slot taken -> the first free hotbar slot
       C  the hotbar FULL -> the first free storage slot (the old place); D  everything full -> "No room", nothing moves
       E  the migration's first gifts (mode give) still go storage-first (not a summon)
       F  the closed Vault (SkyyVault stand-ins findLL / takeLL / doneLL / putBack) -> hotbar; the hotbar full -> storage
       G  the EXACT COPY (chest not loaded) -> the selected hotbar slot; then the LT5 rule on a hotbar copy: invested copy, the original turns
          up = retired, /lifelong on it (held in the hotbar) refused
       H  the legacy replacement (no snapshot) -> hotbar; the FIX2 swap: /lifelong on the retired original held in the hotbar swaps it back
       I  REQUIP (wardrobe:fn:fetch stand-in puts it in storage like SkyyWardrobe 0.2.1) -> moved on into the free hotbar slot (LL-HOTBAR);
          the hotbar full -> it stays in storage; the hotbar slot refuses -> put back where Requip put it (LL-HOTBAR-UNDO); the hotbar AND the
          storage refuse -> the LL-SUMMON-LOST warning + log line with the undo JSON (never silent)
       M  ONE /pickaxe = ONE chat line (the real PickaxeCmd.execute), chest and Vault
  G36 / SND / L35 / TILL  the 0.3.6 harness's children on the 0.3.7 jar (+ SkyyFishing 0.1.6): every check, the listed deviations only
Scratch: tools/dev/scratch/gear037/harness (deleted at the end unless --keep). Exit code 1 on any failure.
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


VERSION = "0.3.7"
V36 = "0.3.6"
SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear037")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
J36 = os.path.abspath(os.path.join(HERE, "SkyyGear-%s.jar" % V36))                       # read only
PKG = "com.skyy.gear."

# ---- the 0.3.6 harness as a library (it loads the 0.3.5 one); its children run on THIS jar in THIS scratch folder
_H36 = os.path.join(HERE, "test_skyygear_0.3.6.py")
_T36 = open(_H36, encoding="utf-8").read()
_cut = _T36.rindex('if __name__ == "__main__":')
_argv = sys.argv
sys.argv = [_H36, "--jar", JAR, "--root", SCR_ROOT, "--dir", SCRATCH]
H36 = {"__name__": "skyygear_h36", "__file__": os.path.abspath(__file__), "__builtins__": __builtins__}
exec(compile(_T36[:_cut], _H36 + " (library)", "exec"), H36)
sys.argv = _argv
H35 = H36["H35"]
H = H36["H"]
Child, _jvm, jar_classes = H36["Child"], H36["_jvm"], H36["jar_classes"]
FAKE_DIR = H36["FAKE_DIR"]
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


# ====================================================================================================== S37: the jar entries
def run_assets37():
    ea, eb = entries(J36), entries(JAR)
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n] and not n.endswith(".class"))
    check(sorted(ea) == sorted(eb) and changed == ["manifest.json"],
          "S37: 0.3.6 -> 0.3.7: the same entries (no file added / removed), only manifest.json changed among non-class files: %s / added %s gone %s"
          % (changed, sorted(set(eb) - set(ea))[:3], sorted(set(ea) - set(eb))[:3]))
    man = eb["manifest.json"].decode("utf-8")
    check('"0.3.7"' in man and "summoned lifelong tools land in your hotbar first" in man, "S37: the manifest names the round")


# ====================================================================================================== C37: class compare
def run_compare37(out):
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

    pa, pb = pool_of(J36), pool_of(JAR)
    na, nb = jar_classes(J36), jar_classes(JAR)
    d = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn, (V36, VERSION)), members(pb, cn, (V36, VERSION))
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            d[cn.split(".")[-1]] = sorted(set(("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd))
    for k in sorted(d):
        print("   %-18s %s" % (k, ", ".join(d[k])[:600]))
    want = {"GearLife": {"+m dest", "+m toHot", "+m unplace", "+f TEST_NOREAD2", "~<clinit>", "~m give2", "~m move", "~m fromVault", "~m fromRequip"}, "GearLL": {"+m refPow"}, "GearToolHitSys": {"~m handle"}}
    bad = dict((k, sorted(set(v) - want.get(k, set()))) for k, v in d.items() if set(v) - want.get(k, set()))
    K.check(na == nb and not bad and set(d.get("GearLife", [])) == want["GearLife"] and set(d.get("GearLL", [])) == want["GearLL"] and set(d.get("GearToolHitSys", [])) == want["GearToolHitSys"],
            "C37: 0.3.6 -> 0.3.7 changed exactly GearLL (+ refPow), GearToolHitSys.handle and GearLife (+ dest, + toHot, + unplace, + TEST_NOREAD2 (its <clinit> initialiser), ~ give2 / move / fromVault / fromRequip), the same classes: %s %s" % (bad, d.get("GearLife")))

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
    K.check(all(calls("GearLife", m_, "GearLife.dest") for m_ in ("give2", "move", "fromVault", "toHot")) and calls("GearLife", "fromRequip", "GearLife.toHot")
            and not calls("GearLife", "move", "GearStamp.firstEmpty") and not calls("GearLife", "fromVault", "GearStamp.firstEmpty"),
            "C37: give2 / move / fromVault / toHot ask GearLife.dest, fromRequip calls toHot, move / fromVault no longer pick storage-first")
    K.save()


# ====================================================================================================== H37: one booted engine
def run_h37(out):
    L = H35["g36_setup"](out)
    K = L["K"]
    try:
        _h37(L, K)
    except Exception:
        import traceback
        traceback.print_exc()
        K.check(False, "H37: the phase raised: %s" % traceback.format_exc()[-600:])
    K.save()


def _h37(L, K):
    from jpype import JClass, JInt, JShort, JByte, JImplements, JOverride, JObject, JArray, JString
    br, Gear, Data, Roll, LL, Life = L["br"], L["Gear"], L["Data"], L["Roll"], L["LL"], L["Life"]
    mkinv, world, stack, doc, lls, skills, wipe_home, logs, regfile, said = (L["mkinv"], L["world"], L["stack"], L["doc"], L["lls"], L["skills"],
                                                                             L["wipe_home"], L["logs"], L["regfile"], L["said"])
    PR1, U1, PKEY, RQ, SIC, ids, apply, FPM = L["PR1"], L["U1"], L["PKEY"], L["RQ"], L["SIC"], L["ids"], L["apply"], L["FPM"]
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    ASIC = JClass("com.hypixel.hytale.server.core.inventory.ActiveSlotInventoryComponent")
    HMap = JClass("java.util.HashMap")
    Bool_ = JClass("java.lang.Boolean")
    BI32 = JClass("org.bson.BsonInt32")
    fAct = ASIC.class_.getDeclaredField("activeSlot")
    fAct.setAccessible(True)
    fHot = INV.class_.getDeclaredField("hotbar")
    fHot.setAccessible(True)
    IRON = "Tool_Pickaxe_Iron"
    NAME = str(Gear.itemName(IRON))
    VKEYS = ("vault:fn:findLL", "vault:fn:takeLL", "vault:fn:doneLL", "vault:fn:putBack")
    FILL = "Ingredient_Bar_Copper"

    def select(inv_, n):
        fAct.setByte(fHot.get(inv_), JByte(n))

    def fill(c_, slots):
        for i_ in slots:
            c_.setItemStackForSlot(JShort(i_), stack(FILL))

    def free(c_):
        return [i_ for i_ in range(int(c_.getCapacity())) if c_.getItemStack(JShort(i_)) is None or c_.getItemStack(JShort(i_)).isEmpty()]

    def pick(cs_):
        return [x for x in lls(cs_, "p1") if x[2] == 0 and not bool(LL.isRt(doc(x[6])))]

    def slot_of(c_, uid):
        for i_ in range(int(c_.getCapacity())):
            s_ = c_.getItemStack(JShort(i_))
            if s_ is not None and not s_.isEmpty() and doc(s_) is not None and str(LL.uid(doc(s_))) == uid:
                return i_
        return -1

    def fresh(fail=()):
        wipe_home()
        logs()
        Life.TEST_CHESTS = None
        Life.TEST_WKEY = "world1~aaaa"
        PKEY[str(U1)] = "p1"
        for k_ in VKEYS + ("wardrobe:fn:fetch",):
            br.remove(k_)
        RQ.clear()
        LL.TOLD.clear()
        inv_, cs_ = mkinv(fail)
        ref_, st_, ch_, pl_ = world(inv_, cs_, PR1)
        skills(Mining=20, Foraging=20, Farming=20)
        d_ = Roll.newDoc(IRON, JInt(3), True, "craft", JInt(16))
        cs_["storage"].setItemStackForSlot(JShort(5), Data.put(stack(IRON), d_, None))
        Life.sweep0(PR1, inv_, True)
        return inv_, cs_, ref_, st_, pl_

    def to_chest(cs_, slot=3, loaded=True):
        p_ = pick(cs_)[0]
        chest_ = SIC(JShort(27))
        chest_.setItemStackForSlot(JShort(slot), p_[6])
        cs_[p_[0]].removeItemStackFromSlot(JShort(p_[1]))
        P_ = LL.reg("p1")
        for k_, v_ in (("locK", "chest"), ("locW", "world1~aaaa"), ("locX", "10"), ("locY", "64"), ("locZ", "-5")):
            P_.setProperty("pickaxe." + k_, v_)
        LL.save("p1", P_)
        Life.TEST_CHESTS = HMap()
        if loaded:
            Life.TEST_CHESTS.put("world1~aaaa|10|64|-5", chest_)
        return p_, chest_

    # ---- A: chest summon, the selected hotbar slot is empty -> there
    inv, cs, ref, st, pl = fresh()
    gifts = [(x[0], x[2]) for x in lls(cs, "p1") if x[2] != 0]
    K.check(sorted(gifts) == [("storage", 1), ("storage", 2), ("storage", 3)] and not [x for x in lls(cs, "p1") if x[0] == "hotbar"],
            "H37 E: the migration's first gifts (Crude hatchet / hoe / sickle, mode give) still go storage-first - not a summon: %s" % gifts)
    fill(cs["hotbar"], (0, 1))
    select(inv, 4)
    pA, chA = to_chest(cs)
    logs()
    rA = str(Life.reclaimW(PR1, pl, JInt(0), None))
    lgA = logs()
    K.check(int(inv.getActiveHotbarSlot()) == 4 and rA == "+Your %s came back from the chest at 10 64 -5 into your Hotbar 5." % NAME
            and slot_of(cs["hotbar"], pA[3]) == 4 and slot_of(chA, pA[3]) < 0 and len(pick(cs)) == 1 and ids(cs).get(IRON, 0) == 1
            and any("LL-SUMMON " in l and "-> Hotbar 5" in l for l in lgA) and any("LL-SUMMON-BEGIN " in l and "undo: " in l for l in lgA),
            "H37 A: /pickaxe from the loaded chest with the SELECTED hotbar slot (5) empty -> the same pickaxe lands there, the wording is kept, "
            "gear.log LL-SUMMON-BEGIN (undo) + LL-SUMMON -> Hotbar 5: %s" % rA)

    # ---- B: the selected slot is taken -> the first free hotbar slot
    select(inv, 0)
    pB, chB = to_chest(cs)
    rB = str(Life.reclaimW(PR1, pl, JInt(0), None))
    K.check(rB.endswith(" into your Hotbar 3.") and slot_of(cs["hotbar"], pB[3]) == 2 and len(pick(cs)) == 1,
            "H37 B: the selected slot (1) holds something -> the first free hotbar slot (3): %s" % rB)

    # ---- C: the hotbar full -> the first free storage slot (the old place)
    pC, chC = to_chest(cs)
    fill(cs["hotbar"], free(cs["hotbar"]))
    fs = free(cs["storage"])[0]
    rC = str(Life.reclaimW(PR1, pl, JInt(0), None))
    K.check(rC.endswith(" into your Inventory %d." % (fs + 1)) and slot_of(cs["storage"], pC[3]) == fs and len(pick(cs)) == 1,
            "H37 C: the hotbar FULL -> the first free inventory slot (Inventory %d), as before: %s" % (fs + 1, rC))

    # ---- D: everything full -> refused, nothing moved
    pD, chD = to_chest(cs)
    fill(cs["storage"], free(cs["storage"]))
    fill(cs["backpack"], free(cs["backpack"]))
    logs()
    rD = str(Life.reclaimW(PR1, pl, JInt(0), None))
    lgD = logs()
    K.check(rD.startswith("-No room") and slot_of(chD, pD[3]) == 3 and not pick(cs) and not any("LL-SUMMON" in l for l in lgD),
            "H37 D: no free slot anywhere -> 'No room', the pickaxe stays in the chest, nothing logged as moved: %s" % rD)

    # ---- F: the closed Vault -> hotbar; the hotbar full -> storage
    VAULT = {}

    @JImplements("java.util.function.Function")
    class VFind(object):
        @JOverride
        def apply(self, o):
            return JString("2:7") if VAULT.get("x") is not None else None

    @JImplements("java.util.function.Function")
    class VTake(object):
        @JOverride
        def apply(self, o):
            x_ = VAULT.pop("x", None)
            if x_ is None:
                return JString("-gone")
            VAULT["taken"] = x_
            return JArray(JObject)([JString("tok1"), x_])

    @JImplements("java.util.function.Function")
    class VDone(object):
        @JOverride
        def apply(self, o):
            VAULT["done"] = VAULT.get("done", 0) + 1
            return JObject(True, Bool_)

    @JImplements("java.util.function.Function")
    class VBack(object):
        @JOverride
        def apply(self, o):
            VAULT["x"] = VAULT.pop("taken", None)
            return JString("+")

    def vault_on():
        for k_, f_ in zip(VKEYS, (VFind(), VTake(), VDone(), VBack())):
            br.put(k_, f_)

    def to_vault(cs_):
        p_ = pick(cs_)[0]
        VAULT.clear()
        VAULT["x"] = p_[6]
        cs_[p_[0]].removeItemStackFromSlot(JShort(p_[1]))
        return p_

    inv, cs, ref, st, pl = fresh()
    vault_on()
    select(inv, 2)
    pF = to_vault(cs)
    logs()
    rF = str(Life.reclaimW(PR1, pl, JInt(0), None))
    lgF = logs()
    K.check(rF == "+Your %s came back from your Vault into your Hotbar 3." % NAME and slot_of(cs["hotbar"], pF[3]) == 2 and VAULT.get("done") == 1
            and len(pick(cs)) == 1 and any("LL-SUMMON " in l and "from the Vault 2:7 -> Hotbar 3" in l for l in lgF),
            "H37 F: /pickaxe with the tool in the CLOSED Vault -> takeLL, placed in the selected hotbar slot (3), read back, doneLL once: %s" % rF)
    pF2 = to_vault(cs)
    fill(cs["hotbar"], free(cs["hotbar"]))          # after taking it out of the hotbar
    fs2 = free(cs["storage"])[0]
    rF2 = str(Life.reclaimW(PR1, pl, JInt(0), None))
    K.check(rF2.endswith("from your Vault into your Inventory %d." % (fs2 + 1)) and slot_of(cs["storage"], pF2[3]) == fs2 and VAULT.get("done") == 1,
            "H37 F: the Vault with the hotbar full -> the first free inventory slot: %s" % rF2)

    # ---- M: one /pickaxe = one chat line (the real command), chest and Vault
    def run_cmd(cls, ref_, st_, pr_):
        P_ = JClass(PKG + cls)
        exe = [m_ for m_ in P_.class_.getDeclaredMethods() if str(m_.getName()) == "execute"][0]
        exe.setAccessible(True)
        exe.invoke(P_(), None, st_, ref_, pr_, None)
    pM = to_vault(cs)
    PR1.said = None
    run_cmd("PickaxeCmd", ref, st, PR1)
    sM = said(PR1)
    inv, cs, ref, st, pl = fresh()
    select(inv, 6)
    pM2, chM2 = to_chest(cs)
    PR1.said = None
    run_cmd("PickaxeCmd", ref, st, PR1)
    sM2 = said(PR1)
    K.check(len(sM) == 1 and "came back from your Vault into your Inventory" in sM[0] and len(sM2) == 1
            and "came back from the chest at 10 64 -5 into your Hotbar 7." in sM2[0] and slot_of(cs["hotbar"], pM2[3]) == 6,
            "H37 M: ONE /pickaxe (the real PickaxeCmd) = ONE chat line, from the Vault and from a chest (Skyy's double line = two commands): %s | %s" % (sM, sM2))

    # ---- G: the EXACT COPY (the chest is not loaded) -> the selected hotbar slot; then the LT5 rule with the copy in the hotbar
    inv, cs, ref, st, pl = fresh()
    select(inv, 6)
    pG, chG = to_chest(cs, loaded=False)
    logs()
    rG = str(Life.reclaimW(PR1, pl, JInt(0), None))
    lgG = logs()
    cpG = pick(cs)
    K.check(rG.startswith("+Your pickaxe cannot be reached") and "exact copy" in rG and len(cpG) == 1 and cpG[0][0] == "hotbar" and cpG[0][1] == 6
            and cpG[0][3] != pG[3] and any("LL-COPY " in l for l in lgG),
            "H37 G: the exact copy (chest not loaded) is born in the SELECTED hotbar slot (7): %s @ %s" % (rG[:90], cpG[0][:2] if cpG else None))
    d6 = doc(cpG[0][6]).clone()
    d6.put("rfN", BI32(JInt(int(Data.num(d6, "rfN", 0)) + 1)))
    cs["hotbar"].setItemStackForSlot(JShort(6), Data.put(stack(IRON), d6, None))
    LL.LAST.clear()
    Life.sweep0(PR1, inv, True)
    cs["storage"].setItemStackForSlot(JShort(34), chG.getItemStack(JShort(3)))
    chG.removeItemStackFromSlot(JShort(3))
    for _i in range(2):
        LL.LAST.clear()
        Life.sweep0(PR1, inv, True)
    o34 = cs["storage"].getItemStack(JShort(34))
    cs["hotbar"].setItemStackForSlot(JShort(7), o34)
    cs["storage"].removeItemStackFromSlot(JShort(34))
    select(inv, 7)
    rG2 = str(Life.repick(PR1, pl))
    wG = pick(cs)
    K.check(o34 is not None and bool(LL.isRt(doc(o34))) and rG2.startswith("-That pickaxe and your lifelong one are exact copies of each other")
            and len(wG) == 1 and wG[0][3] == cpG[0][3] and regfile("p1").get("pickaxe.uid") == cpG[0][3] and ids(cs).get(IRON, 0) == 2,
            "H37 G (= 0.3.5 LT5 FIX with the copy in the hotbar): the invested copy stays THE pickaxe, the original turns up RETIRED, /lifelong on "
            "it (held in Hotbar 8) is refused: %s" % rG2)

    # ---- H: the legacy replacement (no snapshot) -> hotbar; the FIX2 swap with the retired original held in the hotbar
    inv, cs, ref, st, pl = fresh()
    select(inv, 3)
    pH, chH = to_chest(cs, loaded=False)
    for k_ in ("pickaxe.snap", "pickaxe.snapId", "pickaxe.snapU"):
        LL.reg("p1").remove(k_)
    rH = str(Life.reclaimW(PR1, pl, JInt(0), None))
    rpH = pick(cs)
    ok_h = rH.startswith("+Here is a new Common") and len(rpH) == 1 and rpH[0][0] == "hotbar" and rpH[0][1] == 3
    if rpH:
        rd = doc(rpH[0][6]).clone()
        rd.put("rfN", BI32(JInt(1)))
        cs["hotbar"].setItemStackForSlot(JShort(3), Data.put(stack(str(rpH[0][6].getItemId())), rd, None))
    LL.LAST.clear()
    Life.sweep0(PR1, inv, True)
    cs["storage"].setItemStackForSlot(JShort(20), chH.getItemStack(JShort(3)))
    chH.removeItemStackFromSlot(JShort(3))
    for _i in range(2):
        LL.LAST.clear()
        Life.sweep0(PR1, inv, True)
    oH = cs["storage"].getItemStack(JShort(20))
    cs["hotbar"].setItemStackForSlot(JShort(0), oH)
    cs["storage"].removeItemStackFromSlot(JShort(20))
    select(inv, 0)
    logs()
    rH2 = str(Life.repick(PR1, pl))
    lgH = logs()
    h0 = cs["hotbar"].getItemStack(JShort(0))
    K.check(ok_h and oH is not None and bool(LL.isRt(doc(oH))) and rH2.startswith("+") and "again" in rH2 and not bool(LL.isRt(doc(h0)))
            and regfile("p1").get("pickaxe.uid") == pH[3] and any("LL-SWAP " in l for l in lgH),
            "H37 H (= 0.3.5 FIX2 safety-2 with the replacement in the hotbar): the new Common replacement lands in the selected slot (4); the original "
            "turns up retired; /lifelong on it (held in Hotbar 1) swaps it back: %s | %s" % (rH[:60], rH2))

    # ---- I: REQUIP -> moved on into the free hotbar slot; full -> stays; refusals -> put back / LOST logged
    FETCH = {"store": {}, "after": None}

    @JImplements("java.util.function.Function")
    class RqFetch(object):
        @JOverride
        def apply(self, o):
            eid_ = str(o[1])
            s_ = FETCH["store"].pop(eid_, None)
            if s_ is None:
                return JString("That item is not in Requip any more.")
            c_ = FETCH["cs"]["storage"]
            for i_ in range(int(c_.getCapacity())):
                if c_.getItemStack(JShort(i_)) is None:
                    c_.setItemStackForSlot(JShort(i_), s_)
                    break
            RQ["items"] = [r_ for r_ in RQ.get("items", []) if r_[0] != eid_]
            if FETCH["after"] is not None:
                FETCH["after"]()
            return JString("ok")

    def to_requip(cs_):
        p_ = pick(cs_)[0]
        FETCH["cs"] = cs_
        FETCH["store"]["e1"] = p_[6]
        RQ["items"] = [("e1", str(p_[6].getItemId()), p_[6].getMetadata())]
        cs_[p_[0]].removeItemStackFromSlot(JShort(p_[1]))
        br.put("wardrobe:fn:fetch", RqFetch())
        return p_

    inv, cs, ref, st, pl = fresh()
    select(inv, 5)
    pI = to_requip(cs)
    fsI = free(cs["storage"])[0]
    logs()
    rI = str(Life.reclaimW(PR1, pl, JInt(0), None))
    lgI = logs()
    K.check(rI == "+Your %s came out of your Requip into your Hotbar 6." % NAME and slot_of(cs["hotbar"], pI[3]) == 5 and slot_of(cs["storage"], pI[3]) < 0
            and len(pick(cs)) == 1 and ids(cs).get(IRON, 0) == 1 and any("LL-HOTBAR " in l and "Inventory %d -> Hotbar 6" % (fsI + 1) in l for l in lgI)
            and any("LL-SUMMON " in l and "from Requip e1 -> Hotbar 6" in l for l in lgI),
            "H37 I: /pickaxe from Requip: Requip puts it in storage (Inventory %d), it moves on into the selected hotbar slot (6), one pickaxe, "
            "LL-HOTBAR + LL-SUMMON logged: %s" % (fsI + 1, rI))
    pI2 = to_requip(cs)
    fill(cs["hotbar"], free(cs["hotbar"]))          # after taking it out of the hotbar
    fsI2 = free(cs["storage"])[0]
    logs()
    rI2 = str(Life.reclaimW(PR1, pl, JInt(0), None))
    lgI2 = logs()
    K.check(rI2.endswith("came out of your Requip into your Inventory %d." % (fsI2 + 1)) and slot_of(cs["storage"], pI2[3]) == fsI2
            and not any("LL-HOTBAR" in l for l in lgI2),
            "H37 I: Requip with the hotbar full -> it stays where Requip put it (Inventory %d), no hotbar move: %s" % (fsI2 + 1, rI2))
    # the hotbar slot refuses the write -> put back where Requip put it
    inv, cs, ref, st, pl = fresh(fail=("hotbar",))
    cs["hotbar"].refuseId = IRON
    select(inv, 1)
    pI3 = to_requip(cs)
    fsI3 = free(cs["storage"])[0]
    logs()
    rI3 = str(Life.reclaimW(PR1, pl, JInt(0), None))
    lgI3 = logs()
    K.check(rI3.endswith("came out of your Requip into your Inventory %d." % (fsI3 + 1)) and slot_of(cs["storage"], pI3[3]) == fsI3
            and len(pick(cs)) == 1 and any("LL-HOTBAR-UNDO " in l for l in lgI3) and not any("LL-SUMMON-LOST" in l for l in lgI3),
            "H37 I: the hotbar slot REFUSES the pickaxe -> it is put back exactly where Requip put it (Inventory %d), LL-HOTBAR-UNDO: %s" % (fsI3 + 1, rI3))
    # the hotbar AND the storage refuse (after Requip's own write) -> the LOST warning + record, never silent
    inv, cs, ref, st, pl = fresh(fail=("hotbar", "storage"))
    cs["hotbar"].refuseId = IRON
    select(inv, 1)
    pI4 = to_requip(cs)

    def trip():
        cs["storage"].refuseId = IRON
    FETCH["after"] = trip
    logs()
    rI4 = str(Life.reclaimW(PR1, pl, JInt(0), None))
    lgI4 = logs()
    FETCH["after"] = None
    K.check(rI4.startswith("-Moving your pickaxe went wrong") and any("LL-SUMMON-LOST " in l and pI4[3] in l and "undo: {" in l for l in lgI4)
            and any("LIFELONG TOOL OUT OF PLACE" in l for l in lgI4),
            "H37 I: the hotbar AND the storage refuse -> 'went wrong' + the LIFELONG TOOL OUT OF PLACE warning + LL-SUMMON-LOST with the undo JSON: %s" % rI4)
    K.notes.append("H37 I LOST log: %s" % [l[:160] for l in lgI4 if "LOST" in l or "OUT OF PLACE" in l])

    # ---- R (review 1 + 2): a place that does NOT read back is taken out of the slot BEFORE the restore - never two stacks
    def count_uid(cs_, extra, uid):
        n_ = len([x for x in lls(cs_, "p1") if x[3] == uid])
        for c_ in extra:
            n_ += 1 if slot_of(c_, uid) >= 0 else 0
        return n_
    Life.TEST_NOREAD2 = True
    try:
        # Requip -> toHot: placed in the hotbar, no read-back -> out again -> back where Requip put it
        inv, cs, ref, st, pl = fresh()
        select(inv, 2)
        pR1 = to_requip(cs)
        fsR1 = free(cs["storage"])[0]
        logs()
        rR1 = str(Life.reclaimW(PR1, pl, JInt(0), None))
        lgR1 = logs()
        K.check(rR1.endswith("into your Inventory %d." % (fsR1 + 1)) and slot_of(cs["storage"], pR1[3]) == fsR1 and slot_of(cs["hotbar"], pR1[3]) < 0
                and count_uid(cs, (), pR1[3]) == 1 and ids(cs).get(IRON, 0) == 1 and any("LL-HOTBAR-UNDO " in l for l in lgR1)
                and any("LL-SUMMON-BEGIN " in l and "to the hotbar undo: {" in l for l in lgR1) and not any("LL-SUMMON-LOST" in l for l in lgR1),
                "H37 R1 (review 1+2): toHot placed it but the read-back failed -> taken out of the hotbar slot FIRST, then back in Inventory %d: ONE "
                "stack, LL-SUMMON-BEGIN (undo JSON) before the take + LL-HOTBAR-UNDO: %s" % (fsR1 + 1, rR1))
        # chest -> move: placed in the hotbar, no read-back -> out again -> back in the chest
        inv, cs, ref, st, pl = fresh()
        select(inv, 4)
        pR2, chR2 = to_chest(cs)
        rR2 = str(Life.reclaimW(PR1, pl, JInt(0), None))
        K.check(rR2.startswith("-Your pickaxe could not be put into your inventory - it stayed in the chest") and slot_of(chR2, pR2[3]) == 3
                and slot_of(cs["hotbar"], pR2[3]) < 0 and count_uid(cs, (chR2,), pR2[3]) == 1 and ids(cs).get(IRON, 0) == 0,
                "H37 R2 (review 1, move): placed but not read back -> taken out of the hotbar slot, back in the chest: ONE stack: %s" % rR2)
        # ... and the slot will not give it back -> never restored into the chest (no duplicate), LL-SUMMON-LOST
        inv, cs, ref, st, pl = fresh(fail=("hotbar",))
        cs["hotbar"].rm = 1
        select(inv, 4)
        pR3, chR3 = to_chest(cs)
        logs()
        rR3 = str(Life.reclaimW(PR1, pl, JInt(0), None))
        lgR3 = logs()
        K.check(rR3.startswith("-Your pickaxe came out of the chest at 10 64 -5 but could not be checked - look in your Hotbar 5") and slot_of(chR3, pR3[3]) < 0
                and slot_of(cs["hotbar"], pR3[3]) == 4 and count_uid(cs, (chR3,), pR3[3]) == 1
                and any("LL-SUMMON-LOST " in l and "never restored" in l and "undo: {" in l for l in lgR3) and any("LIFELONG TOOL OUT OF PLACE" in l for l in lgR3),
                "H37 R3 (review 1, move): not read back AND the slot will not let it out -> NOT restored into the chest (one stack, in Hotbar 5), "
                "LL-SUMMON-LOST + the warning: %s" % rR3)
        # toHot, the slot will not let it out -> no restore, LOST
        inv, cs, ref, st, pl = fresh(fail=("hotbar",))
        cs["hotbar"].rm = 1
        select(inv, 1)
        pR4 = to_requip(cs)
        logs()
        rR4 = str(Life.reclaimW(PR1, pl, JInt(0), None))
        lgR4 = logs()
        K.check(rR4.startswith("-Moving your pickaxe went wrong") and slot_of(cs["hotbar"], pR4[3]) == 1 and count_uid(cs, (), pR4[3]) == 1
                and any("LL-SUMMON-LOST " in l and "never restored" in l for l in lgR4),
                "H37 R4 (review 1, toHot): not read back AND the hotbar slot will not let it out -> not restored into storage (one stack), LL-SUMMON-LOST: %s" % rR4)
    finally:
        Life.TEST_NOREAD2 = False

    _ore(L, K, fresh, pick, select)


def _ore(L, K, fresh, pick, select):
    """O: THE ORE GATE on the REAL engine pieces: the vanilla power (BlockHarvestUtils.getSpecPowerDamageBlock), our hit gate + tool power
    (GearToolHitSys.handle on a real DamageBlockEvent), then hits into a REAL BlockHealthSection with BlockHealthSystems$Tick's regeneration
    (5 s after the last hit, 0.1 health / s) between the swings"""
    from jpype import JClass, JInt, JShort, JFloat, JLong
    Data, Roll, LL, Life, Gear = L["Data"], L["Roll"], L["LL"], L["Life"], L["Gear"]
    stack, skills, PR1, U1 = L["stack"], L["skills"], L["PR1"], L["U1"]
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    BHU = JClass("com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils")
    BHS = JClass("com.hypixel.hytale.server.core.modules.blockhealth.BlockHealthSection")
    Instant = JClass("java.time.Instant")
    ITEM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    gsm = [m_ for m_ in BHU.class_.getDeclaredMethods() if str(m_.getName()) == "getSpecPowerDamageBlock"][0]
    gsm.setAccessible(True)

    def vpow(item_id, block):
        it_ = ITEM.getAssetMap().getAsset(item_id)
        bt_ = BTY.getAssetMap().getAsset(block)
        sp_ = gsm.invoke(None, it_, bt_, it_.getTool())
        return 0.0 if sp_ is None else float(sp_.getPower())
    K.notes.append("O vanilla power: Crude/copper %.3f Crude/iron %.3f Copper/iron %.3f Iron/iron %.3f" % (
        vpow("Tool_Pickaxe_Crude", "Ore_Copper_Stone"), vpow("Tool_Pickaxe_Crude", "Ore_Iron_Stone"), vpow("Tool_Pickaxe_Copper", "Ore_Iron_Stone"),
        vpow("Tool_Pickaxe_Iron", "Ore_Iron_Stone")))

    mkinv, world, wipe_home, logs, lls, doc, PKEY = L["mkinv"], L["world"], L["wipe_home"], L["logs"], L["lls"], L["doc"], L["PKEY"]
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    V3 = JClass("org.joml.Vector3i")
    GTH = JClass(PKG + "GearToolHitSys")()
    BHC = JClass("com.hypixel.hytale.server.core.modules.blockhealth.BlockHealth")

    LIFE_LAST = [None]

    def lifelong(tool_id, mining):
        wipe_home()
        logs()
        PKEY[str(U1)] = "p1"
        inv_, cs_ = mkinv()
        ref_, st_, ch_, pl_ = world(inv_, cs_, PR1)
        skills(Mining=mining, Foraging=mining, Farming=mining)
        if tool_id != "Tool_Pickaxe_Crude":
            cs_["storage"].setItemStackForSlot(JShort(5), Data.put(stack(tool_id), Roll.newDoc(tool_id, JInt(0), True, "craft", JInt(mining)), None))
        Life.sweep0(PR1, inv_, True)
        LIFE_LAST[0] = lls(cs_, "p1")
        p_ = [x for x in LIFE_LAST[0] if x[2] == 0][0]
        return p_[6], ch_, st_

    def lifelong_h(tool_id, lv):
        s_, ch_, st_ = lifelong("Tool_Pickaxe_Crude", lv)
        return [x for x in LIFE_LAST[0] if x[2] == 1][0][6], ch_, st_

    def per_hit(s_, ch_, st_, block):
        bt_ = BTY.getAssetMap().getAsset(block)
        v_ = vpow(str(s_.getItemId()), block)
        e_ = DBE(s_, V3(JInt(0), JInt(64), JInt(0)), bt_, JFloat(1.0), JFloat(v_))
        GTH.handle(JInt(0), ch_, st_, None, e_)
        return v_, (-1.0 if e_.isCancelled() else float(e_.getDamage()))

    def hits(d_, swing):
        """hits into a real BlockHealthSection; the engine's regeneration ticks (30 per s) run between the swings"""
        if d_ <= 0.0:
            return -1
        sec_ = BHS()
        t_ = [1000000]
        for n_ in range(1, 3000):
            h_ = float(sec_.damage(JInt(5), JFloat(d_), Instant.ofEpochMilli(JLong(t_[0]))))
            if bool(BHC.isDestroyed(JFloat(h_))):
                return n_
            for _k in range(int(round(swing * 30))):
                t_[0] += 33
                sec_.tickRegeneration(Instant.ofEpochMilli(JLong(t_[0])), JFloat(0.033), JLong(5), JFloat(0.1))
        return -1
    ROWS = {}
    for tool_, lv_, block_ in (("Tool_Pickaxe_Crude", 4, "Ore_Copper_Stone"), ("Tool_Pickaxe_Crude", 4, "Ore_Iron_Stone"),
                               ("Tool_Pickaxe_Copper", 12, "Ore_Iron_Stone"), ("Tool_Pickaxe_Iron", 15, "Ore_Iron_Stone"),
                               ("Tool_Pickaxe_Crude", 4, "Ore_Thorium_Sandstone"), ("Tool_Pickaxe_Copper", 12, "Ore_Thorium_Sandstone"), ("Tool_Hatchet_Crude", 4, "Wood_Maple_Trunk"), ("Tool_Hatchet_Crude", 4, "Wood_Oak_Trunk")):
        s_, ch_, st_ = lifelong(tool_, lv_) if "Pickaxe" in tool_ else lifelong_h(tool_, lv_)
        LL.SLOW.clear()
        v_, d_ = per_hit(s_, ch_, st_, block_)
        ROWS[(tool_, block_)] = (v_, d_, hits(d_, 0.33), hits(d_, 1.0))
    def row(t_, b_):
        return ROWS[(t_, b_)]
    iron_ref = int(-(-1.0 // vpow("Tool_Pickaxe_Iron", "Ore_Iron_Stone")))          # vanilla Iron pickaxe hits on iron ore (4)
    cr_cu, cr_fe, cu_fe, fe_fe, cr_th = (row("Tool_Pickaxe_Crude", "Ore_Copper_Stone"), row("Tool_Pickaxe_Crude", "Ore_Iron_Stone"),
                                         row("Tool_Pickaxe_Copper", "Ore_Iron_Stone"), row("Tool_Pickaxe_Iron", "Ore_Iron_Stone"),
                                         row("Tool_Pickaxe_Crude", "Ore_Thorium_Sandstone"))
    K.check(iron_ref == 4 and 9 <= cr_fe[2] <= 11 and 7 <= cu_fe[2] <= 11 and cr_fe[2] == cr_fe[3] and cu_fe[2] == cu_fe[3] and cr_cu[2] == 8 and fe_fe[2] <= 4,
            "H37 O: ONE TIER UP on the real engine pieces (vanilla spec power, GearToolHitSys.handle, a real BlockHealthSection + its 5 s / 0.1 per s "
            "regeneration between swings): Crude Lv 4 on iron ore %d hits, Copper Lv 12 on iron ore %d (its higher level power: a bit faster) (= ~2.5x the Iron pickaxe's %d vanilla hits; "
            "the same at 0.33 s and 1 s swings), Crude on copper ore %d (own tier, unchanged), Iron Lv 15 on iron %d" % (cr_fe[2], cu_fe[2], iron_ref, cr_cu[2], fe_fe[2]))
    th_ref = int(-(-1.0 // vpow("Tool_Pickaxe_Thorium", "Ore_Thorium_Sandstone")))
    K.check(th_ref == 4 and 36 <= cr_th[2] <= 44 and cr_th[3] == cr_th[2],
            "H37 O: TWO TIERS UP: Crude Lv 4 on thorium ore %d hits (= ~10x the Thorium pickaxe's %d vanilla hits), no regeneration while you keep "
            "swinging (1 s swings: %d)" % (cr_th[2], th_ref, cr_th[3]))
    h_ref = int(-(-1.0 // vpow("Tool_Hatchet_Iron", "Wood_Maple_Trunk")))
    cr_mp, cr_oak = row("Tool_Hatchet_Crude", "Wood_Maple_Trunk"), row("Tool_Hatchet_Crude", "Wood_Oak_Trunk")
    K.check(2 * h_ref <= cr_mp[2] <= 3 * h_ref and cr_oak[2] < cr_mp[2],
            "H37 O: LOGS too: the lifelong Crude hatchet Lv 4 on a Maple log (one up) %d hits = ~2.5x the Iron hatchet's %d vanilla hits; its own "
            "Oak log %d" % (cr_mp[2], h_ref, cr_oak[2]))
    s_, ch_, st_ = lifelong("Tool_Pickaxe_Crude", 4)
    v3, d3 = per_hit(s_, ch_, st_, "Ore_Cobalt_Shale")
    K.check(d3 < 0.0, "H37 O: THREE TIERS UP (Crude on cobalt ore) is refused - the hit is cancelled: %s" % d3)
    # a pause of more than 5 s heals the block (the engine's own rule): 6 hits, a 7 s pause, the rest
    sec_ = BHS()
    t0 = 1000000
    h1 = 1.0
    for n_ in range(6):
        h1 = float(sec_.damage(JInt(5), JFloat(cr_fe[1]), Instant.ofEpochMilli(JLong(t0 + n_ * 330))))
    tt = t0 + 5 * 330
    for _k in range(int(7 * 30)):
        tt += 33
        sec_.tickRegeneration(Instant.ofEpochMilli(JLong(tt)), JFloat(0.033), JLong(5), JFloat(0.1))
    h2 = float(sec_.getHealth(JInt(5)))
    K.check(h1 < 0.5 and h2 > h1 + 0.15, "H37 O: the engine heals a damaged block 0.1 / s from 5 s after its last hit (6 hits -> %.3f, after a 7 s pause %.3f) - "
            "keep swinging and it never heals" % (h1, h2))
    for k_, r_ in ROWS.items():
        K.notes.append("O %s Lv on %s: vanilla %.4f -> ours %.4f per hit: %s hits (0.33 s swings), %s hits (1 s swings)" % (k_[0], k_[1], r_[0], r_[1], r_[2], r_[3]))


# ====================================================================================================== L35 (the 0.3.5 life child on this jar)
L37_EXTRA = [
    ("G: THE 0.3.1 GATE MATRIX on the REAL hit system",
     "0.3.7 by design: a one / two up hit starts from the RIGHT-tier tool's power (Skyy's x2.5 / x10 rule), not the held tool's own; the matrix "
     "fed a fake 0.3 power - logs (hatchet power above 0.3) differ; H37 O checks the new rule on real powers"),
    ("FIX2 safety-2: /lifelong on the retired original swaps it back",
     "the 0.3.5 check writes hotbar slot 0 over the summoned replacement - 0.3.7 puts it there (the selected slot); H37 H re-proves the swap"),
    ("LT5 FIX (safety 1): /lifelong on the retired ORIGINAL of an invested exact copy is refused",
     "the 0.3.5 check writes hotbar slot 0 over the exact copy - 0.3.7 puts it there (the selected slot); H37 G re-proves the rule"),
]


def run_l35(env):
    out = os.path.join(SCRATCH, "life35.json")
    pr = child(env, "--life", "--out", out)
    check(pr.returncode == 0, "L35: the 0.3.5 life child exited cleanly on the 0.3.7 jar (%s)" % pr.returncode)
    if not os.path.isfile(out):
        check(False, "L35: no result")
        return
    r = json.load(open(out))
    OKS[0] += r["ok"]
    exp = list(H36["L35_EXPECTED"]) + L37_EXTRA
    dev, other = [], []
    for f in r["fails"]:
        hit = [w for p, w in exp if p in f]
        (dev if hit else other).append((f, hit[0] if hit else ""))
    check(not other and r["ok"] >= 300, "L35: every 0.3.5 life check passes on 0.3.7 (%d ok) except the explained deviations: unexpected %s" % (r["ok"], [o[0][:220] for o in other][:8]))
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
        print("  note (%s): %s" % (label, str(n)[:400]))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: H35["run_mkfake5"](arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--life", lambda: H35["run_life"](arg("--out"))), ("--compare37", lambda: run_compare37(arg("--out"))),
                     ("--h37", lambda: run_h37(arg("--out"))), ("--g36", lambda: H36["run_g36"](arg("--out"))),
                     ("--snd", lambda: H36["run_snd"](arg("--out"))), ("--till", lambda: H35["run_till"](arg("--out")))):
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
    for f_ in (JAR, J36, H36["FI6_SRC"], H35["CO_SRC"]):
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
            run_assets37()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("compare", "--compare37"), ("h37", "--h37"), ("g36", "--g36"), ("snd", "--snd"), ("till", "--till")):
            if not want(label):
                continue
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        if want("life"):
            run_l35(env)
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
