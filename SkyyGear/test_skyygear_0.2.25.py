"""SkyyGear 0.2.25 harness - THE LAG-FIX ROUND (tools/gear_0_2_25_patch.py; research/Code-Structure-Audit.md findings 5, 6, 7 + pack-wide
pattern 1). Built on tools/harness_kit.py (each phase in a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP /
java.io.tmpdir in the scratch folder). The 0.2.11 harness's engine_boot (the vanilla asset stores + this jar as its own pack) gives the
real Item / EntityStatType stores.

    python SkyyGear/test_skyygear_0.2.25.py [--jar SkyyGear-0.2.25.jar] [--old SkyyGear-0.2.24.jar] [--dir <scratch>] [--keep]
           [--iters 400]

  A   verify     every class loads + initialises with -Xverify:all (harness_kit)
  C   compare    0.2.24 -> 0.2.25: GearSnap added; exactly the listed classes / members differ; non-class entries: only manifest.json
  X   exec       BOTH jars in one JVM (each in its own class loader, the same item store and bridge):
      X1 THE RANDOMISED OLD-VS-NEW COMPARISON: --iters random loadouts (vanilla / mining / Untiered armor, rarities, levels, unidentified,
         broken, a configured set, no document, a non-gear item in an armor slot; swords / bows / staffs / Untiered weapons / a tool / bare
         hands), random gate levels (+ SkyySkills' level signal), class skill, SkyyClasses on / off, gear:extra, and every ~15 iterations a
         random config (part.gate / part.stats / level.armorNative / part.base / base.armorOn / part.utLines / garmor.miningOn /
         garmor.miningShare / level.noSkills / level.gateFloor / a set row): GearStats.totals (weapon, armor only, with / without extra,
         the ok flag), GearSet.counts / hp / activeText, GearArmor.lockSums (two broken factors) / fullSums(U) / inactive / why /
         hasInactive / hasResDelta / resDelta (Physical, Projectile, Fire) / healthDelta, GearMine.compute, GearUtFx.sum (weapon, armor
         only) / taken: 0.2.25 (first call = build, second call = the snapshot, and GearSnap.ON = false) == 0.2.24 for EVERY value
      X2 THE WORK COUNT per player: BSON metadata clones (ItemStack.getMetadata, counted on a stack subclass) of one GearTick second
         (the snapshot rebuilt - the worst case) and of one hit, + skill:fn:level calls of one GearTick second - 0.2.24 vs 0.2.25
      X3 GearGate level signal: no skill:fn:level call while skill:<uuid> / skill:overall:<uuid> stay; a new list -> polled, the change
         seen; 10 s without a signal -> polled; KNOWN deviation printed: a level change SkyySkills does not announce waits <= 10 s
      X4 GearFx.lockKey == LOCK + the stat id for every stat; built once (the array is reused)
      X5 GearStamp: our own transactions (selfNote / selfSeen, identity, a failed one never noted); scanSome on a real inventory: 12 gear
         slots a task, hotbar first, non-gear slots skipped, CUR / AGAIN / follow; the passes stamp exactly what one full scan stamps
      X6 GearOpened: load() not synchronized; 0.2.25 load == 0.2.24 load on a messy file; compact(): header + the last line of each
         position (no X), the same records read back, nothing to do = untouched bytes, a temporary world / no file = -1; lines queued
         after the compaction land after it
      X7 the bridge: Gear.bridge() is the lock-free kit form (perfworld_kit.bridge_static), the same map as skyy.bridge
      F  FIX ROUND (critics): F1 the compaction runs on its own daemon thread after COMPACT_DELAY_MS (executed: compactLater on a messy
         file; bytecode: Thread.start, no ScheduledExecutorService); F2 a background pass adds its counts up in MIG and reports once at
         its end; F3 a paused player's half-done pass retries after PAUSE_RETRY_MS (2 s), an unpaused one after the 250 ms gap
         (executed on the engine scheduler); F4 GearGate.POLL_MS = 3 s
      F2x FIX ROUND 2: F5 GearSnap ring slots are ONE pair { weapon, result } (6 weapons through a ring of 4: every find gives its own
         result or nothing, never another weapon's); F6 GearOpened.publish: the winner's W / PW / CH together, a loser gets the winner's
         W and changes nothing; F7 a fresh pass (scan) drops an abandoned pass's MIG counts (no notice), a continued pass still reports
         them (control); the join refresh clears MIG (bytecode)
  ST  live       START TWICE on a scratch COPY of the live Skyy_SkyyGear (quality file, every one-time update, GearCfg.load): no file
                 changed by either start
  AA  audit      the engine-access audit (harness_kit)
Scratch: tools/dev/scratch/perfgear/h25 (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, random, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PWK

VERSION, PREV = "0.2.25", "0.2.24"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(HK.arg("--old", os.path.join(HERE, "SkyyGear-%s.jar" % PREV)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "perfgear", "h25")))
ITERS = int(HK.arg("--iters", "400"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")

_H211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
_t = open(_H211, encoding="utf-8").read()
H = {"__name__": "skyygear_h211", "__file__": _H211, "__builtins__": __builtins__}
exec(compile(_t[:_t.rindex('if __name__ == "__main__":')], _H211 + " (helpers)", "exec"), H)
H.update({"JAR": JAR, "OLD_JAR": OLD_JAR, "SCRATCH": SCRATCH, "FAKE_DIR": os.path.join(SCRATCH, "fake"), "VERSION": VERSION})

# C: what 0.2.25 changes (method names; "f X" = a field, "c (..." = a constructor); filled from the patch
EXPECT = {
    "Gear": ["+f BRIDGE", "+m bridge0", "~m bridge"],
    "GearMove": ["~m bridge"],
    "GearGate": ["+f POLLS", "+f POLL_MS", "+f SIG", "+f VER", "+m bump", "+m same", "+m signal", "+m ver", "~<clinit>", "~m entry", "~m forget",
                 "~m have", "~m refresh"],
    "GearSet": ["+m counts0", "~m counts"],
    "GearStats": ["+m totals0", "~m totals"],
    "GearMine": ["+m compute0", "~m compute"],
    "GearArmor": ["+m fullSumsU", "+m hasInactive0", "+m hasResDelta0", "+m inactive0", "+m lockSums0", "+m resDelta0", "~m hasInactive",
                  "~m hasResDelta", "~m inactive", "~m lockSums", "~m resDelta"],
    "GearUtFx": ["+m sum0", "~m sum"],
    "GearFx": ["+f LKEYS", "+m lockKey", "~<clinit>", "~m armorPass", "~m forget", "~m hasLock", "~m locks", "~m second"],
    "GearOpened": ["+c ", "+f COMPACTED", "+f COMPACT_DELAY_MS", "+f PUBL", "+f cmp", "+m compact", "+m compact0", "+m compactLater", "+m publish", "+m publish0", "+m read2", "~<clinit>", "~c ", "~c ",
                   "~m load", "~m read", "~m run"],
    "GearStamp": ["+f AGAIN", "+f CUR", "+f MIG", "+f PAUSE_RETRY_MS", "+f SELF", "+f SKIPPED", "+f SLOTS_PER_TASK", "+m dirty0", "+m dirtyIn", "+m follow", "+m scanSome", "+m selfNote",
                  "+m selfSeen", "~<clinit>", "~m dirty", "~m forget", "~m scan"],
    # the version text (the ready line, the config header, the kit's export / header) and the kit's lock-free CfgRows.bridge (tools/skyycfg.py
    # gained it after 0.2.24 was built - every rebuilt mod picks it up)
    "SkyyGearPlugin": ["~m setup"], "GearCfg": ["~m defaultsText"], "CfgFn": ["~m opExport"],
    "CfgRows": ["+f BRIDGE", "+m bridge0", "~<clinit>", "~m bridge", "~m header"],
    "GearStampTask": ["~m run"],
    "GearInvSys": ["~m handle"],
    "GearRefreshTask": ["~m run"],
    "GearReady": ["~m accept"],
}
ADDED = ["GearSnap"]


# ============================================================================================================== X (both jars, one JVM)
def run_exec(out, jar, scratch, home):
    from jpype import JClass, JInt, JShort, JLong, JFloat, JDouble, JBoolean, JChar, JImplements, JOverride, JArray, JString
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls")
    os.makedirs(hcls, exist_ok=True)
    H["_jvm"]([B.SERVER_JAR, B.JAVASSIST, hcls], verify=True, big=True)
    E = H["engine_boot"](K)
    ITEM, us, jf = E["ITEM"], E["us"], E["jf"]
    # the vanilla tools (the 0.2.23 harness's step: the bare pack load leaves Server/Item/Items/Tool/ out)
    AZP = os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Assets.zip")
    afs = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(AZP), JClass("java.util.HashMap")())
    with zipfile.ZipFile(AZP) as az_:
        tnames = [n for n in az_.namelist() if n.startswith("Server/Item/Items/Tool/") and n.endswith(".json")]
    tl_ = JClass("java.util.ArrayList")()
    for n in tnames:
        tl_.add(afs.getPath("/" + n))
    ITEM.getAssetStore().loadAssetsFromPaths("Hytale:Hytale", tl_)
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    SYS = JClass("java.lang.ClassLoader").getSystemClassLoader()

    def loader(j):
        a = JArray(URL)(1)
        a[0] = File(j).toURI().toURL()
        return URLCL(a, SYS)
    LD = {"new": loader(JAR), "old": loader(OLD_JAR)}

    def P(tag, n):
        return JClass(PKG + n, loader=LD[tag])
    # the counting stack (X2): an ItemStack subclass that counts getMetadata() (= one BSON deep clone each, VERIFIED bytecode)
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    ISN = "com.hypixel.hytale.server.core.inventory.ItemStack"
    cs_ = CP.makeClass("skyygearh25.CountStack", CP.get(ISN))
    cs_.addField(JClass("javassist.CtField").make("public static int N = 0;", cs_))
    cs_.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public CountStack(String id, int q, double d, double md, org.bson.BsonDocument m) { super(id, q, d, md, m); }", cs_))
    cs_.addMethod(JClass("javassist.CtNewMethod").make("public org.bson.BsonDocument getMetadata() { N = N + 1; return super.getMetadata(); }", cs_))
    cs_.writeFile(hcls)
    CountStack = JClass("skyygearh25.CountStack")
    IS = JClass(ISN)
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    UUID = JClass("java.util.UUID")
    Props, SR, HM = JClass("java.util.Properties"), JClass("java.io.StringReader"), JClass("java.util.HashMap")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    U1 = UUID.fromString("00000000-0000-0000-0000-00000025a001")
    V1 = UUID.fromString("00000000-0000-0000-0000-00000025a002")
    LEVELS = {}
    CALLS = [0]

    @JImplements("java.util.function.Function")
    class SkillLv:
        @JOverride
        def apply(self, a):
            CALLS[0] += 1
            return JInt(LEVELS.get(str(a[1]), 0))

    @JImplements("java.util.function.Function")
    class Allowed:
        @JOverride
        def apply(self, a):
            return JBoolean(True)
    br.put("skill:fn:level", SkillLv())
    FRESH = {t_: str(P(t_, "GearCfg").defaultsText()) for t_ in ("new", "old")}
    K.check(FRESH["new"] == FRESH["old"].replace("# SkyyGear %s - " % PREV, "# SkyyGear %s - " % VERSION, 1),
            "X: the fresh config text of 0.2.25 == 0.2.24 but the version in its first line (no setting changed)")

    def apply_cfg(**kv):
        for t_ in ("new", "old"):
            p = Props()
            p.load(SR(FRESH[t_]))
            for k_, v_ in kv.items():
                p.setProperty(k_.replace("__", "."), v_)
            P(t_, "GearCfg").apply(p, False)
    apply_cfg()
    Defs = P("new", "GearDefs")
    NR = int(Defs.NR)
    allids = [str(x) for x in ITEM.getAssetMap().getAssetMap().keySet()]

    def armor_ids(slot):
        out_ = []
        for i in allids:
            if not i.startswith("Armor_") or not i.endswith("_" + slot):
                continue
            it = ITEM.getAssetMap().getAsset(i)
            if it is not None and it.getArmor() is not None:
                out_.append(i)
        return sorted(out_)
    SLOTS = ["Head", "Chest", "Hands", "Legs"]
    ARM = {sl: armor_ids(sl) for sl in SLOTS}
    MINE = [str(x) for x in P("new", "GearMine").IDS]
    UTA = {sl: [i for i in ARM[sl] if "_UT_" in i] for sl in SLOTS}
    WEAP = [i for i in allids if i.startswith("Weapon_") and (i.endswith("_Iron") or i.endswith("_Copper") or i.endswith("_Thorium")
                                                                  or "_UT_" in i)]
    WEAP = sorted(w for w in WEAP if P("new", "GearData").isGear(w))
    TOOLS_ = sorted(i for i in allids if i.startswith("Tool_Pickaxe_") and i.endswith(("_Iron", "_Copper")))
    K.check(all(len(ARM[sl]) > 20 for sl in SLOTS) and len(MINE) == 28 and all(UTA[sl] for sl in SLOTS) and len(WEAP) > 20 and TOOLS_,
            "X: the pools: armor %s, mining %d, Untiered armor %s, weapons %d, tools %s" % ({k_: len(v_) for k_, v_ in ARM.items()}, len(MINE),
                                                                                       {k_: len(v_) for k_, v_ in UTA.items()}, len(WEAP), TOOLS_[:2]))
    Data, Roll, Set_ = P("new", "GearData"), P("new", "GearRoll"), P("new", "GearSet")
    rnd = random.Random(20251013)
    STATE = {"set": False}

    def mkdoc(iid):
        r = rnd.randrange(NR)
        ident = rnd.random() < 0.8
        lvl = rnd.choice([-1, rnd.randint(1, 70)])
        d = Roll.newDoc(iid, JInt(r), ident, "test", JInt(lvl))
        if STATE["set"] and iid.startswith("Armor_") and rnd.random() < 0.35:
            Set_.join(d, iid, "harness")
        return d

    def mkstack(iid):
        if iid is None:
            return None
        s = IS(iid, JInt(1))
        if rnd.random() < 0.88:
            s = Data.put(s, mkdoc(iid), U1)
        if iid.startswith("Armor_") and rnd.random() < 0.15:
            s = s.withDurability(JDouble(0.0))
        return s

    def rnd_armor():
        a = SIC(JShort(4))
        for k_, sl in enumerate(SLOTS):
            x = rnd.random()
            if x < 0.12:
                continue
            if x < 0.30:
                iid = rnd.choice([m for m in MINE if m.endswith("_" + sl)])
            elif x < 0.42:
                iid = rnd.choice(UTA[sl])
            elif x < 0.45:
                a.setItemStackForSlot(JShort(k_), IS("Ingredient_Stick", JInt(1)))     # not gear, in an armor slot
                continue
            else:
                iid = rnd.choice(ARM[sl])
            a.setItemStackForSlot(JShort(k_), mkstack(iid))
        return a

    def rnd_weapon():
        x = rnd.random()
        if x < 0.12:
            return None
        if x < 0.18:
            return mkstack(rnd.choice(TOOLS_))
        if x < 0.21:
            return IS("Ingredient_Stick", JInt(1))
        return mkstack(rnd.choice(WEAP))

    def publish_levels():
        br.put("skill:" + str(U1), ",".join("%s:%d" % kv for kv in sorted(LEVELS.items())))

    def rnd_levels():
        LEVELS.clear()
        for k_ in ("Mining", "Foraging", "Combat", "Fury", "Archery", "Smithing", "Overall"):
            LEVELS[k_] = rnd.choice([0, 1, 5, 12, 25, 40, 60, rnd.randint(0, 70)])
        publish_levels()

    def rnd_gate():
        x = rnd.random()
        if x < 0.3:
            br.remove("class:skill:" + str(U1))
        else:
            br.put("class:skill:" + str(U1), rnd.choice(["Combat", "Fury", "Archery"]))
        if rnd.random() < 0.5:
            br.put("class:fn:allowed", Allowed())
        else:
            br.remove("class:fn:allowed")
        if rnd.random() < 0.3:
            br.put("gear:extra:" + str(U1), rnd.choice(["str:5,cc:3", "def:10", "hpr:2,spd:4", ""]))
        else:
            br.remove("gear:extra:" + str(U1))

    def rnd_cfg():
        kv = dict(part__gate=rnd.choice(["true", "false"]), part__stats=rnd.choice(["true", "true", "false"]),
                  level__armorNative=rnd.choice(["true", "false"]), part__base=rnd.choice(["true", "true", "false"]),
                  base__armorOn=rnd.choice(["true", "false"]), part__utLines=rnd.choice(["true", "false"]),
                  garmor__miningOn=rnd.choice(["true", "true", "false"]), garmor__miningShare=rnd.choice(["100", "50"]),
                  level__noSkills=rnd.choice(["pass", "block"]), level__gateFloor=rnd.choice(["0", "1", "5"]))
        STATE["set"] = rnd.random() < 0.6
        if STATE["set"]:
            kv["set__harness"] = "Harness Set,2,str+5 hp+10 def+3"
        apply_cfg(**kv)
        return kv

    def jl(x):
        if x is None:
            return None
        try:
            return [round(float(v), 6) for v in x]
        except Exception:
            return str(x)

    def jm(m):
        if m is None:
            return None
        return sorted((int(k_), round(float(m.get(k_)), 6)) for k_ in m.keySet())

    def results(t_, weapon, armor, new_order=False):
        St, Gs, Ga, Gm, Gu = P(t_, "GearStats"), P(t_, "GearSet"), P(t_, "GearArmor"), P(t_, "GearMine"), P(t_, "GearUtFx")
        Cfg = P(t_, "GearCfg")
        R = {}
        steps = []

        def tot():
            ok = JArray(JBoolean)(1)
            a = jl(St.totals(U1, weapon, armor, ok, True))
            ok2 = JArray(JBoolean)(1)
            b = jl(St.totals(U1, weapon, armor, ok2, False))
            R["tot"] = [a, bool(ok[0]), b, bool(ok2[0]), jl(St.totals(U1, None, armor, None, True)), jl(St.totals(U1, None, armor, None, False))]
        steps.append(tot)

        def sets():
            R["set"] = [jl(Gs.counts(Cfg.STAB, U1, armor)), round(float(Gs.hp(U1, armor)), 6), str(Gs.activeText(U1, armor))]
        steps.append(sets)

        def locks():
            R["lock"] = [jm(Ga.lockSums(U1, armor, JFloat(1.0))), jm(Ga.lockSums(U1, armor, JFloat(0.75))), jm(Ga.fullSums(armor, JFloat(0.75)))]
            if t_ == "new":
                R["lock"].append(jm(Ga.fullSumsU(U1, armor, JFloat(0.75))))
            else:
                R["lock"].append(jm(Ga.fullSums(armor, JFloat(0.75))))
        steps.append(locks)

        def per():
            rows = []
            for i in range(4):
                s = armor.getItemStack(JShort(i))
                rows.append([bool(Ga.inactive(U1, s)), None if Ga.why(U1, s) is None else str(Ga.why(U1, s)),
                             round(float(Ga.resDelta(U1, s, "Physical")), 6), round(float(Ga.resDelta(U1, s, "Projectile")), 6),
                             round(float(Ga.resDelta(U1, s, "Fire")), 6), round(float(Ga.healthDelta(U1, s, JFloat(0.75))), 6)])
            R["per"] = [rows, bool(Ga.hasInactive(U1, armor)), bool(Ga.hasResDelta(U1, armor))]
        steps.append(per)

        def mine():
            R["mine"] = jl(Gm.compute(U1, armor))
        steps.append(mine)

        def ut():
            R["ut"] = [jl(Gu.sum(U1, weapon, armor)), jl(Gu.sum(U1, None, armor)), round(float(Gu.taken(U1, armor)), 6)]
        steps.append(ut)
        if new_order:
            steps.reverse()
        for f_ in steps:
            f_()
        return R
    # ---------------------------------------------------------------------------------------------- X1 the randomised comparison
    Snap = P("new", "GearSnap")
    diffs, kinds = [], {"cfg": 0, "armor": 0, "levels": 0}
    cfgs = []
    b0, h0 = int(Snap.BUILDS.get()), int(Snap.HITS.get())
    for it_ in range(ITERS):
        if it_ % 15 == 0:
            cfgs.append(rnd_cfg())
            kinds["cfg"] += 1
        if it_ % 3 == 0:
            rnd_levels()
            kinds["levels"] += 1
            for t_ in ("new", "old"):
                P(t_, "GearGate").refresh(U1)
        if it_ % 5 == 0:
            rnd_gate()
        armor = rnd_armor()
        weapon = rnd_weapon()
        kinds["armor"] += 1
        ro = results("old", weapon, armor)
        rn1 = results("new", weapon, armor)
        rn2 = results("new", weapon, armor, new_order=True)
        Snap.ON = False
        rn3 = results("new", weapon, armor)
        Snap.ON = True
        for tag, rn in (("build", rn1), ("snapshot", rn2), ("off", rn3)):
            if rn != ro:
                bad = [k_ for k_ in ro if ro[k_] != rn.get(k_)]
                diffs.append((it_, tag, bad, {k_: (ro[k_], rn.get(k_)) for k_ in bad[:2]}))
        # the same armor again after a level change WITHOUT a refresh: both jars keep their cached levels (same), then refresh: same
        if it_ % 7 == 0:
            LEVELS["Combat"] = rnd.randint(0, 70)
            LEVELS["Fury"] = rnd.randint(0, 70)
            publish_levels()
            for t_ in ("new", "old"):
                P(t_, "GearGate").refresh(U1)
            ro = results("old", weapon, armor)
            rn = results("new", weapon, armor)
            if rn != ro:
                diffs.append((it_, "after-refresh", [k_ for k_ in ro if ro[k_] != rn.get(k_)], None))
    nb, nh = int(Snap.BUILDS.get()) - b0, int(Snap.HITS.get()) - h0
    K.check(not diffs and ITERS >= 100, "X1: %d random loadouts x (0.2.25 first call / snapshot / snapshot off) == 0.2.24 for every value (%d configs, "
            "%d level sets): %d differ %s" % (ITERS, kinds["cfg"], kinds["levels"], len(diffs), diffs[:2]))
    K.check(nb > 0 and nh > 3 * nb, "X1: the snapshot is really used (builds %d, reuses %d)" % (nb, nh))
    K.notes.append("X1: %d loadouts, %d configs, snapshot builds %d / reuses %d" % (ITERS, len(cfgs), nb, nh))
    # ---------------------------------------------------------------------------------------------- X2 the work count
    apply_cfg()
    STATE["set"] = False
    LEVELS.clear()
    LEVELS.update({"Mining": 20, "Foraging": 20, "Combat": 30, "Fury": 30, "Smithing": 5})
    publish_levels()
    br.put("class:skill:" + str(U1), "Fury")
    br.remove("gear:extra:" + str(U1))
    br.remove("class:fn:allowed")

    def counted(s):
        return CountStack(s.getItemId(), JInt(s.getQuantity()), JDouble(s.getDurability()), JDouble(s.getMaxDurability()), s.getMetadata())
    rnd.seed(7)
    loadout = []
    for sl, mat in zip(SLOTS, ("Iron", "Iron", "Copper", "Iron")):
        iid = "Armor_%s_%s" % (mat, sl)
        loadout.append(Data.put(IS(iid, JInt(1)), Roll.newDoc(iid, JInt(2), True, "test", JInt(15)), U1))
    hand0 = Data.put(IS("Weapon_Sword_Iron", JInt(1)), Roll.newDoc("Weapon_Sword_Iron", JInt(3), True, "test", JInt(15)), U1)
    varm0 = [Data.put(IS("Armor_Iron_%s" % sl, JInt(1)), Roll.newDoc("Armor_Iron_%s" % sl, JInt(1), True, "test", JInt(12)), V1) for sl in SLOTS]

    def mk_counted():
        a = SIC(JShort(4))
        v = SIC(JShort(4))
        for i, s in enumerate(loadout):
            a.setItemStackForSlot(JShort(i), counted(s))
        for i, s in enumerate(varm0):
            v.setItemStackForSlot(JShort(i), counted(s))
        return a, counted(hand0), v

    def tick(t_, armor, hand):
        Ga, St, Fx, Gm, Gu, Gg = P(t_, "GearArmor"), P(t_, "GearStats"), P(t_, "GearFx"), P(t_, "GearMine"), P(t_, "GearUtFx"), P(t_, "GearGate")
        f = JFloat(1.0)
        full = (lambda: Ga.fullSumsU(U1, armor, f)) if t_ == "new" else (lambda: Ga.fullSums(armor, f))
        Gg.refresh(U1)                                       # GearTick: the gate levels
        St.totals(U1, hand, armor, None, False)              # GearTick: gear:stats:<uuid> (totalsInv)
        Ga.lockSums(U1, armor, f)                            # GearFx.armorPass: the lock want
        full()                                               # armorPass: the raise check
        Fx.warnLines(None, U1, armor)                        # armorPass: the warn lines
        Gm.note(U1, armor)                                   # armorPass: the mining lines + lamp
        St.totals(U1, None, armor, None, True)               # armorPass: armor Speed
        full()                                               # GearFx.second: the Health sync check
        Gu.secondPass(U1, None, hand, armor, True)           # GearFx.second: Untiered max Health % + Mana regen
        St.totals(U1, hand, armor, None, True)               # GearFx.second: regen / stamina (totalsInv)

    def hit(t_, armor, hand, varm):
        Ga, St, Gu = P(t_, "GearArmor"), P(t_, "GearStats"), P(t_, "GearUtFx")
        ok = JArray(JBoolean)(1)
        St.totals(U1, hand, armor, ok, True)                 # GearHit.weaponHit
        Gu.sum(U1, hand, armor)                              # GearUtFx.onHit
        Ga.hasInactive(V1, varm)                             # GearHitSys: keep the pre-armor amount?
        Ga.hasResDelta(V1, varm)
        Ga.levelRes(V1, varm, HM(), False, None)             # GearArmorSys: GearArmor.fix (the per-stack resistance part)
        St.totals(V1, None, varm, None, True)                # GearArmorSys: Defense
        Gu.taken(V1, varm)                                   # GearArmorSys: Untiered damage taken
    W = {}
    for t_ in ("old", "new"):
        P(t_, "GearGate").refresh(U1)
        a, h, v = mk_counted()
        tick(t_, a, h)
        hit(t_, a, h, v)                                     # warm the caches (both jars have their own GearGate level caches)
        time.sleep(1.1)                                      # 0.2.25: the snapshot is now older than MAX_MS - the worst case
        CountStack.N = 0
        CALLS[0] = 0
        tick(t_, a, h)
        w_tick, c_tick = int(CountStack.N), CALLS[0]
        CountStack.N = 0
        for _i in range(10):
            hit(t_, a, h, v)
        w_hit = int(CountStack.N) / 10.0
        CountStack.N = 0
        CALLS[0] = 0
        tick(t_, a, h)                                       # a second tick within the same second (0.2.25: the snapshot)
        W[t_] = {"tick_clones": w_tick, "tick_skill_calls": c_tick, "hit_clones": w_hit, "tick2_clones": int(CountStack.N),
                 "tick2_skill_calls": CALLS[0]}
    print("X2. WORK PER PLAYER (BSON metadata clones; skill:fn:level calls), 4 armor pieces + a sword, 5 gate skills cached:")
    for t_ in ("old", "new"):
        print("    %s %s: one GearTick second %d clones + %d skill:fn:level calls; one hit %.1f clones; a 2nd tick inside the same second %d clones"
              % ({"old": "0.2.24", "new": "0.2.25"}[t_], "", W[t_]["tick_clones"], W[t_]["tick_skill_calls"], W[t_]["hit_clones"], W[t_]["tick2_clones"]))
    K.check(W["new"]["tick_clones"] < W["old"]["tick_clones"] and W["new"]["hit_clones"] < W["old"]["hit_clones"] / 3.0
            and W["new"]["tick_skill_calls"] == 0 < W["old"]["tick_skill_calls"],
            "X2: 0.2.25 does less world-thread work per player: %s" % W)
    K.notes.append("X2 WORK: %s" % json.dumps(W))
    # ---------------------------------------------------------------------------------------------- X3 GearGate level signal
    Gg = P("new", "GearGate")
    Gg.forget(U1)
    Gg.refresh(U1)
    Gg.have(U1, "Mining")
    Gg.have(U1, "Combat")
    p0 = int(Gg.POLLS.get())
    CALLS[0] = 0
    ch1 = bool(Gg.refresh(U1))
    c1 = CALLS[0]
    LEVELS["Mining"] = 33
    ch2 = bool(Gg.refresh(U1))                               # no signal yet: not seen (KNOWN deviation, <= 10 s)
    seen2 = int(Gg.have(U1, "Mining"))
    publish_levels()
    CALLS[0] = 0
    ch3 = bool(Gg.refresh(U1))
    c3 = CALLS[0]
    seen3 = int(Gg.have(U1, "Mining"))
    LEVELS["Combat"] = 44
    sg = Gg.SIG.get(U1)
    sg[2][0] = sg[2][0] - 11000                              # the last poll 11 s ago
    CALLS[0] = 0
    ch4 = bool(Gg.refresh(U1))
    c4 = CALLS[0]
    K.check(not ch1 and c1 == 0 and not ch2 and seen2 == 20 and ch3 and c3 >= 2 and seen3 == 33 and ch4 and c4 >= 2 and int(Gg.have(U1, "Combat")) == 44,
            "X3: no skill:fn:level call while the signal stays (%s calls); an unannounced change waits (seen %d); skill:<uuid> moved -> polled "
            "(%d calls, seen %d); 11 s later -> polled (%d calls, Combat %d)" % (c1, seen2, c3, seen3, c4, int(Gg.have(U1, "Combat"))))
    K.check(int(Gg.POLL_MS) == 3000, "F4: GearGate.POLL_MS = %d ms (fix round: 3 s, was 10 s)" % int(Gg.POLL_MS))
    K.notes.append("X3 KNOWN deviation: a level change SkyySkills does not publish in skill:<uuid> / skill:overall:<uuid> is seen within "
                   "GearGate.POLL_MS = %d ms (0.2.24: within 1 s)" % int(Gg.POLL_MS))
    # ---------------------------------------------------------------------------------------------- X4 GearFx lock keys
    Fx, View = P("new", "GearFx"), P("new", "GearView")
    EST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    nst = int(EST.getAssetMap().getNextIndex()) if hasattr(EST.getAssetMap(), "getNextIndex") else 12
    keys_ok = all(str(Fx.lockKey(i)) == str(Fx.LOCK) + str(View.statName(i)) for i in range(max(nst, 8)))
    IDH = JClass("java.lang.System").identityHashCode
    arr = Fx.LKEYS
    again = all(str(Fx.lockKey(i)) == str(Fx.LOCK) + str(View.statName(i)) for i in range(max(nst, 8)))
    K.check(keys_ok and again and arr is not None and IDH(Fx.LKEYS) == IDH(arr) and str(Fx.lockKey(0)).startswith("skyygear_lock_")
            and str(View.statName(0)) != "Stat 0",
            "X4: lockKey(i) == LOCK + the stat id for %d stats, the array built once and reused" % max(nst, 8))
    # ---------------------------------------------------------------------------------------------- X5 GearStamp
    St_ = P("new", "GearStamp")
    c0 = SIC(JShort(4))
    t1 = c0.setItemStackForSlot(JShort(0), IS("Weapon_Sword_Iron", JInt(1)))
    t2 = c0.setItemStackForSlot(JShort(1), IS("Weapon_Sword_Iron", JInt(1)))
    St_.selfNote(U1, t1)
    K.check(bool(St_.selfSeen(U1, t1)) and not bool(St_.selfSeen(U1, t1)) and not bool(St_.selfSeen(U1, t2)),
            "X5: selfSeen: our own transaction once (identity), not twice, not another one")
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    pr = us.allocateInstance(PRc.class_)
    jf(PRc, "uuid").set(pr, U1)
    try:
        jf(PRc, "username").set(pr, "Tester")
    except Exception:
        pass
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JClass("java.lang.Byte")(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        try:
            jf(Cc, "inventory").set(o_, cont)
        except Exception:
            pass
        return o_

    def mkinv():
        cs = {"hotbar": SIC(JShort(9)), "storage": SIC(JShort(36)), "backpack": SIC(JShort(9)), "armor": SIC(JShort(4)), "utility": SIC(JShort(4)),
              "tools": SIC(JShort(4))}
        inv_ = None
        try:
            inv_ = INV()
            for f_, kind in (("hotbar", "Hotbar"), ("storage", "Storage"), ("backpack", "Backpack"), ("armor", "Armor"), ("utility", "Utility"), ("tools", "Tool")):
                jf(INV, f_).set(inv_, comp(kind, cs[f_]))
            if inv_.getHotbar() is None or not inv_.getHotbar().equals(cs["hotbar"]):
                inv_ = None
        except Exception as e_:
            K.notes.append("X5: the stand-in Inventory could not be built: %s" % str(e_)[:200])
            inv_ = None
        return inv_, cs
    plan = []
    for i in range(9):
        plan.append(("hotbar", i, "Weapon_Sword_Iron" if i % 3 else "Ingredient_Stick"))
    for i in range(24):
        plan.append(("storage", i, ["Armor_Iron_Head", "Weapon_Shortbow_Copper", "Ingredient_Stick", "Armor_Copper_Legs"][i % 4]))

    def fill(cs):
        for sec, i, iid in plan:
            cs[sec].setItemStackForSlot(JShort(i), IS(iid, JInt(1)))
    inv1, cs1 = mkinv()
    inv2, cs2 = mkinv()
    if inv1 is None:
        K.check(False, "X5: no stand-in Inventory - the scan passes were not executed")
    else:
        fill(cs1)
        fill(cs2)
        St_.CUR.remove(U1)
        St_.AGAIN.remove(U1)
        St_.QUEUED.put(U1, JBoolean(True))                   # dirty0 coalesces: nothing is scheduled from the harness
        Gearish = sum(1 for _s, _i, iid in plan if iid != "Ingredient_Stick")
        tasks, stamped, first = 0, 0, None
        while True:
            St_.LAST.remove(U1)
            St_.RATE.remove(U1)
            cnt = St_.scanSome(pr, inv1, JInt(int(St_.SLOTS_PER_TASK)))
            tasks += 1
            stamped += int(cnt[0])
            if first is None:
                first = [int(cnt[0]), [list(x) for x in [St_.CUR.get(U1)] if x is not None], int(St_.SELF.get(U1).size()) if St_.SELF.get(U1) is not None else 0]
                mig_first = [int(x) for x in St_.MIG.get(U1)] if St_.MIG.get(U1) is not None else None
                St_.dirty(pr, None)                          # a change during the pass -> AGAIN
                ag = St_.AGAIN.containsKey(U1)
            if St_.CUR.get(U1) is None or tasks > 10:
                break
        mig_end = St_.MIG.containsKey(U1)
        St_.follow(pr)
        ag_after = St_.AGAIN.containsKey(U1)
        St_.RATE.remove(U1)
        full = St_.scan(pr, inv2)

        def view(cs):
            out_ = []
            for sec, i, iid in plan:
                s = cs[sec].getItemStack(JShort(i))
                d = Data.effective(s.getItemId(), s.getMetadata())
                out_.append((sec, i, str(s.getItemId()), int(Data.state(s.getMetadata())), None if d is None else int(Data.rarity(d))))
            return out_
        v1, v2 = view(cs1), view(cs2)
        hot_first = first[1] and first[1][0][0] == 4 and first[1][0][1] >= 0
        K.check(first[0] == 12 and hot_first and first[2] == 12 and tasks == (Gearish + 11) // 12 and stamped == Gearish == int(full[0])
                and v1 == v2 and ag and not ag_after,
                "X5: scanSome: 12 gear slots a task (first task %s, %d own writes noted; the hotbar's %d gear slots first, the pass stops in "
                "storage), non-gear slots skipped, %d tasks for %d gear slots == one full scan (%s); a change during the pass -> AGAIN, consumed by "
                "follow (%s -> %s)" % (first[0], first[2], sum(1 for x in plan if x[0] == "hotbar" and x[2] != "Ingredient_Stick"), tasks, Gearish,
                                       int(full[0]), ag, ag_after))
        K.check(mig_first == [12, 0] and not mig_end,
                "F2: a background pass adds its counts up (after task 1: MIG %s = 12 stamped, 0 migrated) and reports once when it ends (MIG "
                "cleared: %s)" % (mig_first, not mig_end))
        St_.QUEUED.remove(U1)
    # ---------------------------------------------------------------------------------------------- X6 GearOpened
    Mod = JClass("java.lang.reflect.Modifier")
    On, Oo = P("new", "GearOpened"), P("old", "GearOpened")
    mload = [m for m in On.class_.getDeclaredMethods() if str(m.getName()) == "load"][0]
    oload = [m for m in Oo.class_.getDeclaredMethods() if str(m.getName()) == "load"][0]
    K.check(not Mod.isSynchronized(mload.getModifiers()) and Mod.isSynchronized(oload.getModifiers()),
            "X6: GearOpened.load is no longer synchronized (0.2.24: synchronized)")
    cdir = os.path.join(scratch, "chests")
    os.makedirs(cdir, exist_ok=True)
    Paths = JClass("java.nio.file.Paths")
    lines = ["# SkyyGear - the containers of world w1 (harness header)", "1 64 1 W 2026-10-13T10:00", "2 64 2 P 2026-10-13T10:00",
             "1 64 1 T 2026-10-13T10:01 placer=00000000-0000-0000-0000-00000025a001 note", "3 70 3 L 2026-10-13T10:02 placer=00000000-0000-0000-0000-00000025a002 x",
             "bad line", "4 64 4 W t", "4 64 4 X t forgotten", "", "5 64 5", "2 64 2 W 2026-10-13T10:03", "-7 12 900000 T t placer=not-a-uuid",
             "6 64 6 Q t (bad state = W)"]
    open(os.path.join(cdir, "w1.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")

    def mem(C_, k):
        W_ = C_.W.get(k)
        return (sorted((int(x), str(W_.get(x))) for x in W_.keySet()), sorted((int(x), str(C_.PW.get(k).get(x))) for x in C_.PW.get(k).keySet()))
    for C_ in (On, Oo):
        C_.DIR = Paths.get(cdir)
    mo = mem(Oo, "w1") if Oo.load("w1") is not None else None
    mn = mem(On, "w1") if On.load("w1") is not None else None
    dropped = int(On.compact("w1"))
    after = open(os.path.join(cdir, "w1.txt"), encoding="utf-8").read().split("\n")
    On.evict("w1")
    On.load("w1")
    mr = mem(On, "w1")
    keep = after[1:-1]
    K.check(mo == mn == mr and len(mo[0]) == 6 and dropped == 5 and after[0] == lines[0] and after[-1] == ""
            and keep == ["1 64 1 T 2026-10-13T10:01 placer=00000000-0000-0000-0000-00000025a001 note", "3 70 3 L 2026-10-13T10:02 placer=00000000-0000-0000-0000-00000025a002 x",
                         "5 64 5", "2 64 2 W 2026-10-13T10:03", "-7 12 900000 T t placer=not-a-uuid", "6 64 6 Q t (bad state = W)"],
            "X6: 0.2.25 load == 0.2.24 load on a messy file (%d positions); compact dropped %d lines, kept the header + the last line of every "
            "position (no X), read back the same: %s" % (len(mo[0]) if mo else -1, dropped, keep))
    b1 = open(os.path.join(cdir, "w1.txt"), "rb").read()
    d2 = int(On.compact("w1"))
    On.TEMP.put("tmpw", JBoolean(True))
    d3 = int(On.compact("tmpw"))
    d4 = int(On.compact("nofile"))
    On.put("w1", JInt(9), JInt(64), JInt(9), JChar("W"), "after the compaction")
    On.flush()
    tail = open(os.path.join(cdir, "w1.txt"), encoding="utf-8").read().split("\n")
    K.check(d2 == 0 and open(os.path.join(cdir, "w1.txt"), "rb").read()[:len(b1)] == b1 and d3 == -1 and d4 == -1
            and tail[-2].startswith("9 64 9 W ") and not os.path.exists(os.path.join(cdir, "w1.txt.tmp")),
            "X6: nothing to drop = untouched (%d), a temporary world / no file = -1 (%d / %d), a line queued after the compaction is "
            "appended after it, no .tmp left" % (d2, d3, d4))
    # the scheduled compaction task itself (GearOpened(k, true).run()) on a fresh messy file
    open(os.path.join(cdir, "w2.txt"), "w", encoding="utf-8", newline=chr(10)).write(chr(10).join(["1 1 1 W a", "1 1 1 P b", "2 2 2 X c", ""]))
    c0 = int(On.COMPACTED.get())
    On(JString("w2"), True).run()
    K.check(open(os.path.join(cdir, "w2.txt"), encoding="utf-8").read().split(chr(10))[1:] == ["1 1 1 P b", ""] and int(On.COMPACTED.get()) == c0 + 1,
            "X6: the scheduled task GearOpened(world, true).run() compacts (the standard header + '1 1 1 P b')")
    # ---------------------------------------------------------------------------------------------- X5b the engine-driven paths (bytecode:
    # they need a live world / player; the parts they call are executed above)
    G_ = PWK.calls(JAR)
    CPb = JClass("javassist.ClassPool")(False)
    CPb.appendSystemPath()
    CPb.appendClassPath(B.SERVER_JAR)
    CPb.appendClassPath(JAR)

    def order(cn, mn, names):
        mi = [m_ for m_ in CPb.get(PKG + cn).getClassFile2().getMethods() if str(m_.getName()) == mn][0]
        it, cpl, seq = mi.getCodeAttribute().iterator(), mi.getConstPool(), []
        while it.hasNext():
            p_ = it.next()
            if it.byteAt(p_) in (0xb6, 0xb7, 0xb8, 0xb9):
                ix = it.u16bitAt(p_ + 1)
                try:
                    nm = str(cpl.getMethodrefName(ix))
                except Exception:
                    nm = str(cpl.getInterfaceMethodrefName(ix))
                if nm in names:
                    seq.append(nm)
        return seq
    has = lambda m_, c_: c_ in G_.get(m_, set())
    K.check(order("GearInvSys", "handle", ("getTransaction", "selfSeen", "dirty")) == ["getTransaction", "selfSeen", "dirty"]
            and has("GearStampTask.run", PKG + "GearStamp.scanSome") and has("GearStampTask.run", PKG + "GearStamp.follow")
            and not has("GearStampTask.run", PKG + "GearStamp.scan")
            and has("GearRefreshTask.run", PKG + "GearStamp.scanSome") and has("GearRefreshTask.run", PKG + "GearStamp.follow")
            and has("GearReady.accept", "java.util.concurrent.ThreadLocalRandom.nextLong")
            and all(has(m_, PKG + "GearStamp.scan") for m_ in ("ReforgeCmd.execute", "IdentifyCmd.execute", "UpCmd.execute", "SmithCmd.execute", "MultiCmd.execute"))
            and has("GearFx.armorPass", PKG + "GearArmor.fullSumsU") and has("GearFx.second", PKG + "GearArmor.fullSumsU")
            and not has("GearFx.armorPass", PKG + "GearArmor.fullSums") and has("GearFx.forget", PKG + "GearSnap.forget"),
            "X5b: GearInvSys.handle asks selfSeen(event.getTransaction()) BEFORE dirty; GearStampTask / the join refresh scan 12 slots + follow; "
            "the join refresh is staggered (ThreadLocalRandom); /reforge /identify /upgrade /smithing /multitool still scan everything; the armor "
            "pass + second read fullSumsU; GearFx.forget drops the snapshot")
    # ---------------------------------------------------------------------------------------------- X7 the bridge
    class Quiet(HK.Child):                               # collects bridge_static's verdicts without printing (GearMove is judged below)
        def check(self, cond, what):
            if not cond:
                self.fails.append(what)
            return cond
    KB = Quiet(os.path.join(scratch, "bridge-scratch.json"))
    found = PWK.bridge_static(KB, JAR)
    K.check(sorted(found) == ["CfgRows", "Gear", "GearMove"] and [f_ for f_ in KB.fails if "GearMove" not in f_] == [],
            "X7: CfgRows.bridge / Gear.bridge are the lock-free kit form: %s" % [f_ for f_ in KB.fails if "GearMove" not in f_])
    G, Mv = P("new", "Gear"), P("new", "GearMove")
    K.check(IDH(G.bridge()) == IDH(br) and IDH(G.BRIDGE) == IDH(br) and IDH(Mv.bridge()) == IDH(br),
            "X7: Gear.bridge() = the skyy.bridge map, cached in Gear.BRIDGE; GearMove.bridge() (tools/skyymove.py's copy) answers the same map")
    gm = PWK.calls(JAR).get("GearMove.bridge", set())
    K.check(gm == {"com.skyy.gear.Gear.bridge"}, "X7: GearMove.bridge() only calls the lock-free Gear.bridge (no synchronized(System.class)): %s" % sorted(gm))
    # ---------------------------------------------------------------------------------------------- F the fix round
    # F1: compactLater on a messy file: nothing at once, compacted by its own daemon thread after ~2 s
    open(os.path.join(cdir, "w3.txt"), "w", encoding="utf-8", newline=chr(10)).write(chr(10).join(["1 1 1 W a", "1 1 1 P b", "3 3 3 W c", ""]))
    c0 = int(On.COMPACTED.get())
    On.compactLater("w3")
    now_lines = open(os.path.join(cdir, "w3.txt"), encoding="utf-8").read().split(chr(10))
    t0 = time.time()
    while int(On.COMPACTED.get()) == c0 and time.time() - t0 < 8:
        time.sleep(0.1)
    took = time.time() - t0
    G2 = PWK.calls(JAR)
    cl = G2.get("GearOpened.compactLater", set())
    K.check(len(now_lines) == 4 and int(On.COMPACTED.get()) == c0 + 1 and 1.5 <= took < 8
            and open(os.path.join(cdir, "w3.txt"), encoding="utf-8").read().split(chr(10))[1:] == ["1 1 1 P b", "3 3 3 W c", ""]
            and "java.lang.Thread.start" in cl and not any("schedule" in c_ for c_ in cl),
            "F1: compactLater -> its own daemon thread: untouched at once, compacted %.1f s later (COMPACT_DELAY_MS %d); calls %s (no engine "
            "scheduler)" % (took, int(On.COMPACT_DELAY_MS), sorted(cl)))
    # F3: a half-done pass of a PAUSED player retries after 2 s, of an unpaused one after the 250 ms gap (both executed on the engine's
    # scheduler; the task finds no world for the stand-in player and frees QUEUED - the moment it ran)
    Sysc = JClass("java.lang.System")
    JLongArr = JArray(JLong)

    def retry(paused_):
        St_.QUEUED.remove(U1)
        St_.AGAIN.remove(U1)
        St_.CUR.put(U1, JArray(JInt)([1, 0]))
        nw = int(Sysc.currentTimeMillis())
        St_.RATE.put(U1, JLongArr([nw, 0, nw + 30000 if paused_ else 0]))
        St_.LAST.put(U1, JClass("java.lang.Long").valueOf(nw))
        St_.follow(pr)
        q0 = bool(St_.QUEUED.containsKey(U1))
        time.sleep(1.0)
        q1 = bool(St_.QUEUED.containsKey(U1))
        t_ = time.time()
        while St_.QUEUED.containsKey(U1) and time.time() - t_ < 5:
            time.sleep(0.05)
        q2 = bool(St_.QUEUED.containsKey(U1))
        St_.CUR.remove(U1)
        St_.RATE.remove(U1)
        St_.LAST.remove(U1)
        return q0, q1, q2
    rp = retry(True)
    ru = retry(False)
    fl = G2.get("GearStamp.follow", set())
    K.check(rp == (True, True, False) and ru == (True, False, False) and PKG + "GearStamp.dirtyIn" in fl and PKG + "GearStamp.paused" in fl
            and int(St_.PAUSE_RETRY_MS) == 2000,
            "F3: follow while paused -> one task in 2 s (queued %s, still waiting after 1 s %s, ran %s); unpaused -> the 250 ms gap (queued %s, "
            "ran within 1 s %s)" % (rp[0], rp[1], not rp[2], ru[0], not ru[1]))
    # ---------------------------------------------------------------------------------------------- F2x fix round 2
    # F5: the weapon ring - 6 weapons through 4 slots; every slot is one pair; find never mixes a weapon with another's result
    JObj = JClass("java.lang.Object")
    ent = JArray(JObj)(int(Snap.N))
    ws = [JClass("java.lang.Object")() for _i in range(6)]
    rs = [JArray(JObj)(1) for _i in range(6)]
    mixed, pairs_ok = [], True
    for i_ in range(6):
        Snap.keep(ent, JInt(5), ws[i_], rs[i_])
        ring = ent[5]
        pairs_ok = pairs_ok and len(ring) == 4 and all(ring[j_] is None or len(ring[j_]) == 2 for j_ in range(4))
        for j_ in range(i_ + 1):
            got = Snap.find(ent, JInt(5), ws[j_])
            if got is not None and IDH(got) != IDH(rs[j_]):
                mixed.append((i_, j_))
    last4 = [Snap.find(ent, JInt(5), ws[j_]) for j_ in range(6)]
    K.check(pairs_ok and not mixed and last4[0] is None and last4[1] is None and all(IDH(last4[j_]) == IDH(rs[j_]) for j_ in range(2, 6))
            and Snap.find(ent, JInt(7), ws[0]) is None,
            "F5: GearSnap ring = 4 pairs { weapon, result } (one reference write each): 6 weapons kept, the newest 4 found with their own "
            "result, the 2 oldest gone, never another weapon's result (mixed: %s)" % mixed)
    # F6: publish - the first loader's three maps together; a loser gets the winner's W and leaves PW / CH alone
    On.evict("pubw")
    m1, p1, h1, m2, p2, h2 = CHM(), CHM(), CHM(), CHM(), CHM(), CHM()
    w1 = On.publish("pubw", m1, p1, h1)
    w2 = On.publish("pubw", m2, p2, h2)
    K.check(w1 is None and w2 is not None and IDH(w2) == IDH(m1) and IDH(On.W.get("pubw")) == IDH(m1) and IDH(On.PW.get("pubw")) == IDH(p1)
            and IDH(On.CH.get("pubw")) == IDH(h1) and IDH(On.pmap("pubw")) == IDH(p1)
            and PKG + "GearOpened.publish" in G2.get("GearOpened.load", set()),
            "F6: GearOpened.publish: the winner's W / PW / CH together (first: %s), a loser gets the winner's W and changes nothing; load -> publish"
            % (w1 is None))
    On.evict("pubw")
    # F7: a fresh pass (scan) forgets an abandoned pass's MIG counts; a continued pass reports them (the control)
    Notice, Gm = P("new", "GearNotice"), P("new", "Gear")
    U7, U8 = UUID.fromString("00000000-0000-0000-0000-00000025a007"), UUID.fromString("00000000-0000-0000-0000-00000025a008")

    def mkpr(u_):
        p_ = us.allocateInstance(PRc.class_)
        jf(PRc, "uuid").set(p_, u_)
        try:
            jf(PRc, "username").set(p_, "T" + str(u_)[-1])
        except Exception:
            pass
        return p_
    res7 = {}
    for u_, fresh in ((U7, True), (U8, False)):
        p_ = mkpr(u_)
        inv_e, _cs = mkinv()
        if inv_e is None:
            res7[fresh] = None
            continue
        St_.CUR.remove(u_)
        St_.RATE.remove(u_)
        St_.MIG.put(u_, JArray(JInt)([0, 3]))
        if fresh:
            St_.scan(p_, inv_e)
        else:
            St_.scanSome(p_, inv_e, JInt(int(St_.SLOTS_PER_TASK)))
        res7[fresh] = (bool(Notice.shown(Gm.pkey(u_))), bool(St_.MIG.containsKey(u_)))
        St_.forget(u_)
    fx = []
    try:
        CPf = CPb.get(PKG + "GearRefreshTask")
        mi = [m_ for m_ in CPf.getClassFile2().getMethods() if str(m_.getName()) == "run"][0]
        it, cpl = mi.getCodeAttribute().iterator(), mi.getConstPool()
        while it.hasNext():
            p_ = it.next()
            if it.byteAt(p_) == 0xb2:
                fx.append(str(cpl.getFieldrefName(it.u16bitAt(p_ + 1))))
    except Exception as e_:
        fx.append("error: %s" % str(e_)[:120])
    K.check(res7.get(True) == (False, False) and res7.get(False) == (True, False) and "MIG" in fx and "CUR" in fx,
            "F7: scan (a fresh pass) with an abandoned pass's MIG {0, 3}: no notice, MIG cleared %s; the control - the same counts at the end "
            "of a continued pass give the notice %s; the join refresh reads CUR + MIG (clears both): %s"
            % (res7.get(True), res7.get(False), [f_ for f_ in fx if f_ in ("CUR", "MIG")]))
    K.save()


# ============================================================================================================== ST (start twice on a copy)
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Cfg, Qual, Log, G = P("GearCfg"), P("GearQual"), P("GearLog"), P("Gear")
    Paths = JClass("java.nio.file.Paths")
    starts = []
    for _n in range(2):
        b0 = HK.tree_hash(home)
        Cfg.DIR = Paths.get(home)
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        Log.FILE = Paths.get(os.path.join(home, "gear.log"))
        Qual.load(Paths.get(os.path.join(home, "quality.properties")))
        Cfg.importRolls(Cfg.FILE, Paths.get(os.path.join(os.path.dirname(home), "Skyy_SkyyRolls", "reforge.properties")))
        for m_ in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025",
                   "migrate0214", "migrate0215", "migrate0216", "migrate0217", "migrate0218"):
            getattr(Cfg, m_)()
        Cfg.load()
        a0 = HK.tree_hash(home)
        starts.append(sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k) and not k.endswith("gear.log")))
    K.check(starts == [[], []], "ST: two starts on a COPY of the live Skyy_SkyyGear (%d files): no file changed: %s" % (len(HK.tree_hash(home)), starts))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, [("exec", run_exec), ("live", run_live)], os.path.abspath(__file__),
           live=(LIVE_DIR, "Skyy_SkyyGear"))
