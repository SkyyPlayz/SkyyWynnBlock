"""Harness for SkyyArmory 0.1.37 (the wand controls: hold right = block, hold left = the launch, on EVERY wand; tools/armory_0_1_37_patch.py).
Build first:
    python tools/armory_0_1_37_patch.py && python SkyyArmory/build_skyyarmory_0.1.37.py

    python SkyyArmory/test_skyyarmory_0.1.37.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.36 -> 0.1.37: exactly the planned members (EXPECT) + the new class WandGuard; non-class entries: manifest.json + server.lang
  T   table    the per-wand INPUT -> ACTION table (tap left, hold left, tap right, hold right) for the 15 metal wands, the Second Opinion, the
               vanilla Wood / Rotten / Tribal wands (SkyySkills' SET item files + the jar's own WandGuard.withGuard run on them) and the 16 Soul
               items (control), BEFORE (0.1.36 jar, the Wood wands' raw files) and AFTER (0.1.37): the chain walked through the item JSON, the
               jar's interactions (Armory > SkyySkills > Assets.zip, item InteractionVars + Parent merges) to its projectile, and the projectile
               through the jar's own code path (ArmoryDefs.pidCode / woodSpawn -> 2000 = Leap.onWandOrb, bytecode-checked); the guard root
               walked to the vanilla Wielding (Common_Guard_Wield) with its Stamina rule (0.5 Stamina to start, none while Stamina_Broken)
  G   guard    WandGuard executed: woodId, withGuard (a copy; Primary / Ability1 kept; null when already guarded / own right-click), withPrio
               (a new config = DEFAULT_WEAPON's shape + the {"Secondary": {"MainHand": 1}} priority; the shared DEFAULT objects never written;
               an item's own config left alone), apply() on a real engine Item (the guard written + a fresh packet), the engine hand choice
               (InteractionContext's rule) with an empty / shield / torch off-hand
  P   physics  hold left still = the 0.1.36 hop: defaults force 30 / maxUp 20 / lift 8, the launch vector of a level / 45 deg / straight-down
               look through the jar's TravMath, flown with the engine decay model of the 0.1.36 harness (~12 blocks level)
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the client's own guard pose / block feel on the Wood wands after the run-time change (the same
run-time write the longsword guard uses since 0.1.28), the live start line "wand guard: 3 of 3 ...".
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.37", "0.1.36"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.52.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "arm37", "harness")))
PKG = "com.skyy.armory."
ASSETS = os.path.join(os.path.dirname(os.path.dirname(B.INSTALLED_SERVER_JAR)), "Assets.zip")
LANG = "Server/Languages/en-US/server.lang"
GUARD = "Root_Common_Guard_Entry_StaminaCondition"
METALS = ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium") + tuple(w + "_SkyWynn" for w in
                                                                                              ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"))
OUR_WANDS = ["Weapon_Wand_" + m for m in METALS] + ["Weapon_Wand_UT_SecondOpinion"]
WOOD = ["Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal"]
SOUL = ["Weapon_Wand_SoulOrb"] + ["Weapon_Wand_SoulCage_" + m for m in METALS]
P_ITEM = "Server/Item/Items/Weapon/Wand/%s.json"
ONE_HAND_CFG = {"Priorities": {"Secondary": {"MainHand": 1}}}
EXPECT = {"ArmoryItemL": ["~m accept"],          # + WandGuard.onLoaded
          "SkyyArmoryPlugin": ["~m setup", "~m start"],          # + WandGuard.applyAll's start line, the version text
          "ArmoryCheck": ["~m packCheck", "~m packOf"],          # the version text
          "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"],          # the config file's header line (version text)
          "ArmoryHooks": ["~<clinit>"],          # the fixed.guard row words
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],          # the version text
          "CfgRows2": ["~<clinit>"]}          # the version text + the fixed.guard row words
ADDED = ["WandGuard"]
WANT_AFTER = {"tapL": "quick shot", "holdL": "LAUNCH (Leap.onWandOrb hop) + charged orb", "tapR": "guard (short block)", "holdR": "guard (block)"}

_orig_compare = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    E = HK.Child.eq

    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            want = sorted(["manifest.json", LANG])
        return E(self, got, want, what)
    HK.Child.eq = eq
    try:
        _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = E
HK.run_compare = _compare


def setup_jvm(jar, *more):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR] + list(more) + [jar], verify=True)
    JClass(PKG + "ArmoryLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory")
    return JClass


def jload(z, n):
    return json.loads(z.read(n).decode("utf-8-sig"))


class Src(object):
    """interaction / root lookup the engine way for this pack: the Armory jar wins, then SkyySkills, then Assets.zip (by file name)"""

    def __init__(self, jars):
        self.ints, self.roots = {}, {}
        for j in jars:
            z = zipfile.ZipFile(j)
            for n in z.namelist():
                if not n.endswith(".json"):
                    continue
                b = os.path.basename(n)[:-5]
                if n.startswith("Server/Item/Interactions/"):
                    self.ints.setdefault(b, (z, n))
                elif n.startswith("Server/Item/RootInteractions/"):
                    self.roots.setdefault(b, (z, n))

    def i(self, k):
        z, n = self.ints[k]
        return jload(z, n)

    def r(self, k):
        z, n = self.roots[k]
        return jload(z, n)


def walk(S, x, ivars, out, depth=0):
    """every Type and projectile on the SUCCESS path of an interaction (no Failed / Forks), item vars applied to Replace, Parent merged"""
    assert depth < 40, x
    if isinstance(x, list):
        for y in x:
            walk(S, y, ivars, out, depth + 1)
        return
    if isinstance(x, str):
        if x in S.ints:
            walk(S, S.i(x), ivars, out, depth + 1)
        elif x in S.roots:
            walk(S, S.r(x).get("Interactions"), ivars, out, depth + 1)
        else:
            out["missing"].append(x)
        return
    if not isinstance(x, dict):
        return
    if "Parent" in x and "Type" not in x:
        base = dict(S.i(x["Parent"]))
        base.update(dict((k, v) for k, v in x.items() if k != "Parent"))
        x = base
    t = x.get("Type")
    out["types"].append(t or "-")
    if t == "LaunchProjectile":
        out["pids"].append(x["ProjectileId"])
    if t == "Wielding":
        out["wield"].append(x)
    if t == "StatsCondition":
        out["costs"].append(x.get("Costs"))
    if t == "EffectCondition":
        out["effects"].append((x.get("Match"), tuple(x.get("EntityEffectIds") or ())))
    if t == "Replace":
        v = ivars.get(x["Var"]) if ivars else None
        if v is None and x.get("DefaultOk"):
            v = x.get("DefaultValue")
        if v is not None:
            walk(S, v.get("Interactions") if isinstance(v, dict) and "Interactions" in v and "Type" not in v else v, ivars, out, depth + 1)
        return
    if t == "Charging":
        out["charging"].append(x)
        return
    if "Interactions" in x:
        walk(S, x["Interactions"], ivars, out, depth + 1)
    if "Next" in x and t != "Charging":
        walk(S, x["Next"], ivars, out, depth + 1)


def new_out():
    return {"types": [], "pids": [], "wield": [], "costs": [], "effects": [], "charging": [], "missing": []}


def root_entry(S, root_id, ivars):
    """the root's first interaction on the no-speed-effect path (the SkyyArmory_Spd_ wrapper's Next) -> the Charging, or the walk"""
    o = new_out()
    walk(S, S.r(root_id).get("Interactions"), ivars, o)          # an item names a ROOT (Wand_Primary is both a root and an interaction)
    return o


def act(JC, S, leaf, ivars, item):
    """one input's result: the projectile's action through the jar's code path, or the guard"""
    o = new_out()
    walk(S, leaf, ivars, o)
    D = JC(PKG + "ArmoryDefs")
    if o["wield"]:
        return "guard", o
    for p in o["pids"]:
        c = int(D.pidCode(p))
        if 1000 <= c < 2000:
            return "quick shot", o
        if 2000 <= c < 3000:
            return "LAUNCH (Leap.onWandOrb hop) + charged orb", o
        if c < 0 and int(D.woodSpawn(p, 0, True, item)) == 2000:
            return "LAUNCH (Leap.onWandOrb hop) + charged orb", o
    if any(int(D.pidCode(p)) == int(D.WINGS_CODE) for p in o["pids"]):
        return "Wings of Fate", o
    return "other %s %s" % (o["pids"], o["types"][:6]), o


def table(JC, S, item, inter, ivars):
    """{tapL, holdL, tapR, holdR} for one item's (effective) interactions"""
    row = {}
    for side, key in (("L", "Primary"), ("R", "Secondary")):
        rid = inter.get(key)
        e = root_entry(S, rid, ivars)
        if e["charging"]:
            ch = e["charging"][0]
            ks = sorted(ch["Next"], key=float)
            tap, hold = ch["Next"][ks[0]], ch["Next"][ks[-1]]
            row["tap" + side] = act(JC, S, tap, ivars, item)[0]
            row["hold" + side] = act(JC, S, hold, ivars, item)[0] if len(ks) > 1 else "held Charging (%s)" % rid
        elif e["wield"]:
            row["tap" + side], row["hold" + side] = "guard (short block)", "guard (block)"
        else:
            row["tap" + side] = row["hold" + side] = "other %s" % e["types"][:5]
    return row


def run_table(out, jar, scratch, _home):
    from jpype import JClass, JObject
    K = HK.Child(out)
    JC = setup_jvm(jar, B.JAVASSIST)
    WG = JC(PKG + "WandGuard")
    IT = JC("com.hypixel.hytale.protocol.InteractionType")
    EM = JC("java.util.EnumMap")

    def guarded(inter):
        m = EM(IT)
        for k, v in inter.items():
            m.put(getattr(IT, k), v)
        n = WG.withGuard(m)
        if n is None:
            return dict(inter)
        return dict((str(k.name()), str(n.get(k))) for k in n.keySet())
    sk = zipfile.ZipFile(SKILLS_JAR)
    res = {}
    for label, j in (("before", OLD_JAR), ("after", jar)):
        S = Src([j, SKILLS_JAR, ASSETS])
        z = zipfile.ZipFile(j)
        rows = {}
        for iid in OUR_WANDS + WOOD + SOUL:
            d = jload(sk, P_ITEM % iid) if iid in WOOD else jload(z, P_ITEM % iid)
            inter = dict(d["Interactions"])
            if iid in WOOD and label == "after":
                inter = guarded(inter)
            rows[iid] = (table(JC, S, iid, inter, d.get("InteractionVars") or {}), inter, d)
        res[label] = rows
    # the table (printed into the notes; the report copies it)
    for iid in OUR_WANDS + WOOD + SOUL[:2]:
        b, a = res["before"][iid][0], res["after"][iid][0]
        K.notes.append("T: %-34s BEFORE tapL=%s | holdL=%s | tapR=%s | holdR=%s" % (iid, b["tapL"], b["holdL"], b["tapR"], b["holdR"]))
        K.notes.append("T: %-34s AFTER  tapL=%s | holdL=%s | tapR=%s | holdR=%s" % (iid, a["tapL"], a["holdL"], a["tapR"], a["holdR"]))
    bad = [(i, res["after"][i][0]) for i in OUR_WANDS + WOOD if res["after"][i][0] != WANT_AFTER]
    K.check(not bad, "T: AFTER, every wand (15 metals + Second Opinion + Wood / Rotten / Tribal): tap left = quick shot, hold left = the launch, "
            "tap right = a short guard, hold right = the guard: %s" % bad[:3])
    K.check(all(res["before"][i][0] == WANT_AFTER for i in OUR_WANDS), "T: BEFORE, the 16 Armory wands were already right (no change for them)")
    wb = [(i, res["before"][i][0]) for i in WOOD]
    K.check(all(r["tapR"] == "quick shot" and r["holdR"] == WANT_AFTER["holdL"] and r["tapL"] == "quick shot" and r["holdL"] == WANT_AFTER["holdL"]
                for _i, r in wb), "T: REPRO - BEFORE, the Wood / Rotten / Tribal wands' right click = the left click (hold right = THE LAUNCH, no block): %s" % wb[:1])
    # the Wood wands: only Secondary changes; Primary / Ability1 kept
    wi = [(i, res["before"][i][1], res["after"][i][1]) for i in WOOD]
    K.check(all(a == dict(b, Secondary=GUARD) and a["Primary"] == "Wand_Primary" and a.get("Ability1") == "SkyyArmory_Wand_Signature" for _i, b, a in wi),
            "T: WandGuard.withGuard on the SET SkyySkills files changes only Secondary -> %s (Primary Wand_Primary, Ability1 the signature kept)" % GUARD)
    # the guard root reaches the vanilla Wielding with the Stamina rule
    S = Src([jar, SKILLS_JAR, ASSETS])
    g = root_entry(S, GUARD, {})
    w = g["wield"][0] if g["wield"] else {}
    K.check(len(g["wield"]) == 1 and w.get("Effects", {}).get("ItemAnimationId") == "Guard" and w.get("AngledWielding", {}).get("DamageModifiers", {}).get("Physical") == 0
            and {"Stamina": 0.5} in g["costs"] and ("None", ("Stamina_Broken",)) in g["effects"] and not g["pids"] and not g["missing"],
            "T: hold right reaches the guard root -> Common_Guard_Entry_StaminaCondition (0.5 Stamina to start, none while Stamina_Broken) -> the "
            "Wielding Common_Guard_Wield (Guard pose, front 90 deg x0 damage): %s / %s" % (g["costs"], g["effects"]))
    gr = S.r(GUARD)
    K.check(gr.get("RequireNewClick") is True and gr.get("Rules") == {"Interrupting": ["Primary"]} and GUARD not in S.ints,
            "T: the guard root is the vanilla file (RequireNewClick, interrupts a left-click charge) - not shipped by any jar")
    K.check(all(not [k for k in (res["after"][i][2].get("InteractionVars") or {}) if k.startswith("Guard")] for i in OUR_WANDS + WOOD),
            "T: no wand overrides a Guard_* var (the vanilla guard numbers + Stamina rule apply as is)")
    # the Wand animation set has the Guard pose (Parent Sword) for the Wood wands; ours use SkyyArmory_Wand
    with zipfile.ZipFile(ASSETS) as az:
        wa = jload(az, "Server/Item/Animations/Wand.json")
        sw = jload(az, "Server/Item/Animations/Sword.json")
    K.check(wa.get("Parent") == "Sword" and "Guard" in (sw.get("Animations") or {}) and all(res["after"][i][2].get("PlayerAnimationsId") == "Wand" for i in WOOD),
            "T: the Wood wands' Wand animation set inherits Sword's Guard pose")
    # one-handed + MainHand priority kept on our wands; the Soul items untouched
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    K.check(all(zo.read(P_ITEM % i) == zn.read(P_ITEM % i) for i in OUR_WANDS + SOUL), "T: the 16 Armory wand + 16 Soul item files are byte-identical to 0.1.36")
    K.check(all(res["after"][i][2].get("Utility") == {"Compatible": True} and res["after"][i][2].get("InteractionConfig") == ONE_HAND_CFG for i in OUR_WANDS + SOUL),
            "T: every Armory wand + Soul item keeps Utility Compatible (one-handed) + the MainHand right-click priority")
    so = [(i, res["after"][i][0]) for i in SOUL]
    K.check(all(r["holdL"] == "Wings of Fate" and r["holdR"] == "held Charging (SkyyArmory_Soul_Bind)" for _i, r in so)
            and all(res["after"][i][1] == {"Primary": "SkyyArmory_Soul_Wings", "Secondary": "SkyyArmory_Soul_Bind"} for i in SOUL),
            "T: Soul Orb / Cages unchanged - left = SkyyArmory_Soul_Wings (Wings of Fate), right hold = SkyyArmory_Soul_Bind (Bindings): %s" % so[:1])
    # the code path behind "LAUNCH": ArmoryTravSys.onEntityAdded -> pidCode, else woodCode; ArmoryTrav.added -> Leap.onWandOrb (bytecode)
    CPc = JC("javassist.ClassPool")
    cp = CPc(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)

    def calls(cn, mn):
        out_ = []
        for m in cp.get(PKG + cn).getDeclaredMethods():
            if str(m.getName()) != mn:
                continue
            ca, cpl = m.getMethodInfo().getCodeAttribute(), m.getMethodInfo().getConstPool()
            it = ca.iterator()
            while it.hasNext():
                p = it.next()
                if it.byteAt(p) in (0xb8, 0xb6, 0xb9):
                    out_.append(str(cpl.getMethodrefName(it.u16bitAt(p + 1))) if it.byteAt(p) != 0xb9 else str(cpl.getInterfaceMethodrefName(it.u16bitAt(p + 1))))
        return out_
    ea, ad = calls("ArmoryTravSys", "onEntityAdded"), calls("ArmoryTrav", "added")
    wc = calls("ArmoryTrav", "woodCode")
    K.check("pidCode" in ea and "woodCode" in ea and "added" in ea and "onWandOrb" in ad and "woodSpawn" in wc,
            "T: code path - a charged orb's SPAWN: ArmoryTravSys.onEntityAdded -> pidCode / woodCode (woodSpawn) -> ArmoryTrav.added -> Leap.onWandOrb")
    D = JC(PKG + "ArmoryDefs")
    K.check(all(int(D.woodSpawn("Skeleton_Mage_Corruption_Orb", 0, True, i)) == 2000 for i in WOOD) and int(D.woodSpawn("Skeleton_Mage_Corruption_Orb", 0, False, "Weapon_Wand_Wood")) == -1,
            "T: the Wood-tier wand charged orb = code 2000 only from a player holding one (NPC orbs stay plain)")
    K.save(table=dict((i, {"before": res["before"][i][0], "after": res["after"][i][0]}) for i in OUR_WANDS + WOOD + SOUL))


def run_guard(out, jar, scratch, _home):
    K = HK.Child(out)
    JC = setup_jvm(jar)
    WG = JC(PKG + "WandGuard")
    IT = JC("com.hypixel.hytale.protocol.InteractionType")
    PS = JC("com.hypixel.hytale.protocol.PrioritySlot")
    IC = JC("com.hypixel.hytale.server.core.modules.interaction.interaction.config.InteractionConfiguration")
    IPR = JC("com.hypixel.hytale.server.core.modules.interaction.interaction.config.InteractionPriority")
    Item = JC("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    EM, HM = JC("java.util.EnumMap"), JC("java.util.HashMap")
    JInt = JC("java.lang.Integer")
    K.check([bool(WG.woodId(i)) for i in WOOD + ["Weapon_Wand_Iron", "Weapon_Wand_SoulOrb", None]] == [True, True, True, False, False, False],
            "G: woodId = exactly the Wood / Rotten / Tribal wands")
    K.check(str(WG.GUARD) == GUARD and str(WG.ROOT) == "Wand_Primary" and str(WG.PRIO_FROM) == "Weapon_Wand_Iron", "G: constants")

    def em(**kv):
        m = EM(IT)
        for k, v in kv.items():
            m.put(getattr(IT, k), v)
        return m
    src = em(Primary="Wand_Primary", Secondary="Wand_Primary", Ability1="SkyyArmory_Wand_Signature")
    n = WG.withGuard(src)
    K.check(n is not None and str(n.get(IT.Secondary)) == GUARD and str(n.get(IT.Primary)) == "Wand_Primary" and str(n.get(IT.Ability1)) == "SkyyArmory_Wand_Signature"
            and str(src.get(IT.Secondary)) == "Wand_Primary" and str(n.getClass().getName()) == "java.util.EnumMap" and int(n.size()) == 3,
            "G: withGuard = a COPY (EnumMap kept) with Secondary = the guard, Primary + Ability1 kept, the input untouched")
    nulls = [WG.withGuard(em(Primary="Wand_Primary", Secondary=GUARD)), WG.withGuard(em(Primary="Wand_Primary", Secondary="Someone_Else")),
             WG.withGuard(em(Primary="Other", Secondary="Wand_Primary")), WG.withGuard(None), WG.withGuard(em(Primary="Wand_Primary"))]
    K.check(all(x is None for x in nulls), "G: withGuard leaves alone: already guarded, another mod's right-click, another Primary, null, no Secondary")
    hm = HM()
    hm.put(IT.Primary, "Wand_Primary")
    hm.put(IT.Secondary, "Wand_Primary")
    K.check(str(WG.withGuard(hm).get(IT.Secondary)) == GUARD, "G: withGuard on a plain HashMap too")
    # the priority: a map of the codec's shape ({InteractionType -> InteractionPriority({slot -> int})})
    slots = HM()
    slots.put(PS.MainHand, JInt(1))
    pm = HM()
    pm.put(IT.Secondary, IPR(slots))
    dw, d0 = IC.DEFAULT_WEAPON, IC.DEFAULT
    c = WG.withPrio(dw, pm)
    fo = IC.class_.getDeclaredField("displayOutlines")
    fo.setAccessible(True)
    K.check(c is not None and not c.equals(dw) and int(c.getPriorityFor(IT.Secondary, PS.MainHand)) == 1 and int(c.getPriorityFor(IT.Secondary, PS.OffHand)) == 0
            and int(c.getPriorityFor(IT.Primary, PS.MainHand)) == 0 and bool(fo.get(c)) == bool(fo.get(dw)) and int(dw.getPriorityFor(IT.Secondary, PS.MainHand)) == 0,
            "G: withPrio(DEFAULT_WEAPON) = a NEW config (DEFAULT_WEAPON's displayOutlines %s) with right-click MainHand 1 only; DEFAULT_WEAPON itself still 0" % bool(fo.get(dw)))
    c0 = WG.withPrio(d0, pm)
    K.check(c0 is not None and bool(fo.get(c0)) == bool(fo.get(d0)) and int(d0.getPriorityFor(IT.Secondary, PS.MainHand)) == 0,
            "G: withPrio(DEFAULT) = a new config of DEFAULT's shape; DEFAULT itself untouched")
    own = IC()
    K.check(WG.withPrio(own, pm) is None and WG.withPrio(dw, None) is None and WG.withPrio(None, pm) is None,
            "G: withPrio leaves an item's OWN config alone; no map / no config = nothing")
    # apply() on a real engine Item (no asset store in this JVM: prioMap() is null -> the guard only)
    FI = Item.class_.getDeclaredField("interactions")
    FI.setAccessible(True)
    FC = Item.class_.getDeclaredField("interactionConfig")
    FC.setAccessible(True)
    it = Item("Weapon_Wand_Wood")
    FI.set(it, em(Primary="Wand_Primary", Secondary="Wand_Primary", Ability1="SkyyArmory_Wand_Signature"))
    FC.set(it, dw)
    r1 = int(WG.apply(it))
    m1 = it.getInteractions()
    r2 = int(WG.apply(it))
    it2 = Item("Weapon_Wand_Iron")
    FI.set(it2, em(Primary="Wand_Primary", Secondary="Wand_Primary"))
    r3 = int(WG.apply(it2))
    K.check(r1 == 1 and str(m1.get(IT.Secondary)) == GUARD and str(m1.get(IT.Primary)) == "Wand_Primary" and r2 == 0 and r3 == 0
            and str(it2.getInteractions().get(IT.Secondary)) == "Wand_Primary" and it.getInteractionConfig().equals(dw),
            "G: apply(Item Weapon_Wand_Wood) writes the guard (1; no asset store here = no priority, DEFAULT_WEAPON kept), a 2nd apply = 0, another id = untouched")
    K.check(int(WG.GUARDS) == 1 and int(WG.onLoaded(None)) == 0, "G: counters + onLoaded(null) = 0")
    # the engine hand choice (InteractionContext.forInteraction, the 0.1.36 harness's port): with the guard + priority the Wood wand keeps right click
    with zipfile.ZipFile(ASSETS) as az:
        vit = dict((x.split("/")[-1][:-5], x) for x in az.namelist() if x.startswith("Server/Item/Items/") and x.endswith(".json"))
        shield, torch = jload(az, vit["Template_Weapon_Shield"]), jload(az, vit["Furniture_Crude_Torch"])

    def prio(item, itype, slot):
        p = ((item or {}).get("InteractionConfig") or {}).get("Priorities") or {}
        v = p.get(itype)
        if v is None:
            return 0
        return int(v) if isinstance(v, (int, float)) else int(v.get(slot, 0))

    def route(main, off, itype):
        if main is None and off is not None:
            return "off"
        if main is None or off is None:
            return "main"
        pm_, po = prio(main, itype, "MainHand"), prio(off, itype, "OffHand")
        if pm_ == po:
            return "off" if itype == "Secondary" and (main.get("Utility") or {}).get("Compatible", False) else "main"
        if pm_ < po:
            return "off"
        if itype not in (main.get("Interactions") or {}):
            return "off"
        return "main"
    wood = {"Interactions": {"Primary": "Wand_Primary", "Secondary": GUARD}, "Utility": {"Compatible": True}, "InteractionConfig": ONE_HAND_CFG}
    nop = dict(wood)
    nop.pop("InteractionConfig")
    K.check([route(wood, o, "Secondary") for o in (None, shield, torch)] == ["main"] * 3 and route(nop, shield, "Secondary") == "off"
            and route(wood, shield, "Primary") == "main",
            "G: HAND - with the priority the Wood wand's right-click guard wins over a shield / torch off-hand (without it the shield takes right-click = "
            "the shield's own block); left click stays the wand's")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- P: hold left = the 0.1.36 hop
def fly(vh, vy, cfg, g=32.0, hz=60, y0=0.0):
    """the 0.1.36 harness model: one Velocity Set flown tick by tick with the engine's split-velocity decay (MotionControllerBase.steer0)"""
    air, airmax, gr, grmax, th, style = cfg
    dt = 1.0 / hz
    x, y, t, airt = 0.0, y0, 0, 0
    while t < 20 * hz:
        ground = y <= 1e-9 and vy <= 0.0
        r, rm = (gr, grmax) if ground else (air, airmax)
        if vh < th:
            k = (vh * vh) / (th * th) if style == "Exp" else vh / th
            r = r * k + rm * (1.0 - k)
        vh *= r ** (60.0 / hz)
        if not ground:
            vy -= g * dt
            airt += 1
        x += vh * dt
        y += vy * dt
        if y < 0.0:
            y, vy = 0.0, 0.0
        t += 1
        if vh < 0.05 and y <= 0.0:
            break
    return x, airt / float(hz)


def run_physics(out, jar, scratch, _home):
    K = HK.Child(out)
    JC = setup_jvm(jar)
    Cfg, TM, AT = JC(PKG + "ArmoryCfg"), JC(PKG + "TravMath"), JC(PKG + "ArmoryTrav")
    Props, SR = JC("java.util.Properties"), JC("java.io.StringReader")
    p = Props()
    p.load(SR(str(Cfg.DEF_CFG)))
    Cfg.apply(p)
    K.eq([float(Cfg.HOP_FORCE), float(Cfg.HOP_MAXUP), float(Cfg.HOP_LIFT)], [30.0, 20.0, 8.0], "P: the hop defaults are the 0.1.36 ones (force 30, maxUp 20, lift 8)")
    vc = AT.dash()
    cfg = (float(vc.getAirResistance()), float(vc.getAirResistanceMax()), float(vc.getGroundResistance()), float(vc.getGroundResistanceMax()),
           float(vc.getThreshold()), str(vc.getStyle()))

    def launch(pitch):
        a = math.radians(pitch)
        hv = list(TM.hopVector(0.0, -math.sin(a), math.cos(a), 30.0, False))
        up = float(TM.liftUp(float(TM.launchUp(hv[1], 20.0)), 8.0, 20.0))
        vy = float(TM.hopVy(up, float("nan"), 21.0))
        return math.hypot(hv[0], hv[2]), vy
    lv, l45, ld = launch(0), launch(45), launch(90)
    d0, d45 = fly(lv[0], lv[1], cfg)[0], fly(l45[0], l45[1], cfg)[0]
    K.notes.append("P: level %s -> %.2f blocks; 45 deg %s -> %.2f; straight down %s" % (lv, d0, l45, d45, ld))
    K.check(abs(lv[0] - 30.0) < 1e-6 and lv[1] == 8.0 and 11.0 <= d0 <= 13.0, "P: a level look launches 30 sideways + 8 up = %.2f blocks (0.1.36: ~12)" % d0)
    K.check(ld[0] < 1e-6 and ld[1] == 20.0 and 9.0 <= d45 <= 11.5, "P: straight down = 20 up (maxUp), 45 deg = %.2f blocks (0.1.36: ~10.3)" % d45)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("table", run_table), ("guard", run_guard), ("physics", run_physics)], script=__file__)
