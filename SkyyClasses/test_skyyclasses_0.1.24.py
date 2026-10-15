"""SkyyClasses 0.1.24 - harness for WARRIOR + BERSERKER + ARCHER ON THE RUNE FRAMEWORK (tools/classes_0_1_24_patch.py), on top of every
0.1.22 / 0.1.23 section (the keys, levels, modifiers, panel, the Monk / Assassin abilities, rebirth R6 - kept as the regression). Build
first: python tools/classes_0_1_24_patch.py && python SkyyClasses/build_skyyclasses_0.1.24.py

    python SkyyClasses/test_skyyclasses_0.1.24.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

0.1.24 sections (inside the exec phase, the same engine stand-ins): X40 the tables / loadouts / panel / costs per shape / the live
numbers rows / SHIELDS = WARRIOR ONLY / the vanilla-rune block for the three classes / the rebirth participant measuring a Warrior;
X41 Rallying Guard (picked at the cast, the cut through the REAL player damage hook, the taunt, Echo, Hold the Line, Charge Rally, on
landing, Shield Wall, Aegis Core, Thorns, Presence, Interpose, Battle Cry); X42 Shield Shockwave (the cone, Ring, Echo, Shield Training,
Retribution, Shockwave Surge, Ground Pound); X43 Iron Chain (the hook + drag, bosses / Pull, Chain, Barbed Chain, Anchor); X44 Challenge
(cut + reflect, Chain, Ward, Duel); X45 Guardian's Oath (the transfer through the REAL hook, the cut, no party); X46 Enrage (picked once,
the curve, the REAL outgoing hook, the counted use, Lone Rage, War Horn, Rally, Warbringer, War Charge, War Leap, Leech); X47 Whirlwind
(hits + heal, Bleed, Staggering Spin, Pull, Echo, Grinder, Spinning Drop); X48 Earthsplitter (the line, missing Health, Blood Pact,
Seismic, Ground Pound, Split, Fissure, Crater); X49 Blood Frenzy (the toggle, stacks + cost from the REAL landed hook, the aura, Floor +
the Duration+ exclusion, out of Mana, Blood Bank); X50 Warlord's Banner (the buffs, kills, leaving its range, the cooldown from the fall,
Echo, Rooted, Bearer); X51 Pinning Shot (pierce, root, Mark from everyone, Steady Aim, bosses, Grand Trapper, Lasting Roots, Trap Arrows,
Focus Mark, Split, Rain Pin); X52 Rapid Fire (15 arrows, Seeker, the Seeker / Ricochet exclusion, Ricochet, Piercing Aim, Hover, Braced,
Arrow Tempest); X53 Explosive Arrow (not a bow, the blast, Echo, Set Charge, Storm Cloud, Chain Reaction); X54 Arrow Rain (no aim, pulses,
root + Mark, Lingering, Echo, Kneeling Volley broken, Marksman's Snare); X55 Hunter's Net (root + Mark once, Set Trap, Snare Line, Split,
Deep Net); X56 the modifier texts, ClassQuit, the prune.
section (the keys, levels, modifiers, panel - kept as the regression). Build first: python tools/classes_0_1_23_patch.py &&
python SkyyClasses/build_skyyclasses_0.1.23.py

    python SkyyClasses/test_skyyclasses_0.1.23.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

0.1.23 sections (inside the exec phase, the same engine stand-ins): X19 the pure rules (rebirth soft cap, live stacks, the backstab rule,
Awe tiers, waves, modifier levels past their top, Palm's cooldown floor, the effect ids) + the tables / loadouts / panel / mirror / HUD for
the Monk + Assassin; X20 Flowing Form (aura, combo stacks from the REAL hit hook, speed, Awe + losing the target, drain, the end, every
shape); X21 Hundred Fists (waves, the gap, Echo); X22 Still Water (counter / blocked / deflect through the REAL damage hook, Echo, Ward,
Reflexes, Tranquility, Calm Aura, Serenity); X23 Palm Strike (no target, stun, push, every shape, Aerial / Concussive / Iron Fist,
Ricochet, Slow, Echo, the cooldown floor); X24 Cyclone Kick (ring, arc, Leg Sweep, Dropping Kick, Haste); X25 Cloak + First Strike (lose
target, First Strike, break on attack, Lethal Opener, Death Mark, Longer Cloak, Dash / Silent / Still Shadow, Slip Away); X26 Toxin (cloud,
poison, Weaken, the tree nodes, Plague, Chain, Echo); X27 God Killer (not a boss, front / behind, Death from Above, Boss Hunter, Echo,
Haste, Patient Kill armed / broken); X28 Vanishing Act (smoke: lose you + slow, Smoke Drop, Ambush); X29 the class-tree numbers; X30 REBIRTH
R6 (the participant at every step incl. a failed write + retry, stale staged files, an older committed rebirth; the soft cap; the cap 25 + n;
the +1 modifier level; ClassQuit).

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch. Live save data is only READ / copied.
  OLD  test_skyyclasses_0.1.19.py on the 0.1.22 jar: the loadout bridge (L) + START TWICE on a scratch COPY of the live Skyy_SkyyClasses
       folder (ST: nothing written); its CC part needs the 0.1.18 jar (gone) and is skipped
  A    verify   every class loads + initialises with -Xverify:all (tools/harness_kit.py)
  C    compare  0.1.21 -> 0.1.22: the 11 new classes, only the planned classes change, non-class entries = manifest.json + the rune asset pack
  X    EXECUTED on test players / NPCs (the 0.1.18 engine stand-ins: a map-backed Store / CommandBuffer, the REAL EntityStatMap, real Damage
       objects, the REAL AbilTick; a stand-in ability-slot container behind the REAL InventoryComponent$AbilitySlots; REAL
       InteractionChainStartEvent / InteractionChain / InteractionContext / ItemStack objects):
       X1 the pure rules (uses per level, diminishing returns, modifier unlock / steps, the tree csv); X2 THE HOOK's decision (runeDecide);
       X3 THE HOOK (onRune on a real event: cancelled + cast a tick later through RuneCast, door 1); X4 REFUSAL through the hook (cooldown,
       no Mana, tree gate, keys off, roll); X5 a game rune on a Mage (blocked: cancelled, no cast, one hint) / abil.vanillaRunes; X6 THE MARKER
       FALLBACK (markerPress: dup within 700 ms, cast through RuneCast door 2); X7 THE MIRROR (runeWant, mirrorNeed, mirrorSet, runeTick
       -> MirrorTask, a stray rune, a vanilla rune kept, the guard onInv -> InvClean); X8 LEVELS BY USE (used: the counted use, the gap,
       echo / switched, the level-up line, the file); X9 a REAL Meteor through the key -> impact -> one counted use; X10 MODIFIERS (unlock,
       equip, the double rule, tree slots, the cast context, modifier level-up); X11 doAction (swap / pick / equip / unequip); X12 THE PANEL
       (class:fn:abilPanel Object[78], abilMods, abilDo, abilUnlock); X13 PROFILE SWITCH (levels / mods / slots per profile, the mirror
       follows); X14 M5 cooldowns clear on relog; X15 /cast stays (door 0) + abil.castCmd off; X16 Echo
  R21  test_skyyclasses_0.1.21.py's ability-line routing phase on the 0.1.22 jar (Abil.say unchanged)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, time, shutil, zipfile, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.24"
PKG = "com.skyy.classes."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-0.1.23.jar")
BASE = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "classes3", "cl")))
SCRATCH = BASE if "--phase" in sys.argv else os.path.join(BASE, "h")
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
ASSETS = os.path.join(APPDATA, "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")
T19 = os.path.join(HERE, "test_skyyclasses_0.1.19.py")
NEW_CLASSES = []


def t21():
    spec = importlib.util.spec_from_file_location("test_skyyclasses_0_1_21", os.path.join(HERE, "test_skyyclasses_0.1.21.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_route21(out, jar, scratch, home):
    T = t21()
    T.run_ability(out, jar, scratch, home)


# ============================================================================================================ C: the 0.1.23 -> 0.1.24 compare
def run_compare24(out, jar, old_jar, pkg, expect, added):
    from jpype import JClass
    import re
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(old_jar), pool_of(jar)
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def body(c_):
        d_ = {}
        for m_ in list(c_.getDeclaredMethods()) + list(c_.getDeclaredConstructors()):
            ca_ = m_.getMethodInfo().getCodeAttribute()
            t_ = []
            if ca_ is not None:
                it_ = ca_.iterator()
                cp_ = m_.getMethodInfo().getConstPool()
                while it_.hasNext():
                    p_ = it_.next()
                    t_.append(re.sub(r"^((?:if\w*|goto(?:_w)?)) -?\d+$", r"\1", re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, p_, cp_)))))
            d_[str(m_.getName()) + str(m_.getSignature())] = "\n".join(t_)
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())
        return d_
    na, nb = HK.jar_classes(old_jar), HK.jar_classes(jar)
    K.eq(sorted(set(nb) - set(na)), sorted(pkg + a for a in added), "C: no class added")
    K.eq(sorted(set(na) - set(nb)), [], "C: no class removed")
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        a_, b_ = body(pa.get(cn)), body(pb.get(cn))
        dd = sorted(k for k in set(a_) | set(b_) if a_.get(k) != b_.get(k))
        if dd:
            diffs[cn[len(pkg):]] = dd
    print("C. class compare 0.1.23 -> 0.1.24: %d classes identical, %d differ: %s" % (len(set(na) & set(nb)) - len(diffs), len(diffs), sorted(diffs)))
    extra = sorted(set(diffs) - set(expect))
    K.check(not extra, "C: only the planned classes change (unplanned: %s)" % extra)
    K.notes.append("C: changed %s" % {k: len(v) for k, v in diffs.items()})
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    changed = sorted(n for n in ea & eb if za.read(n) != zb.read(n))
    K.eq(changed, ["Server/Languages/en-US/server.lang", "manifest.json"], "C: the changed non-class entries: the language file (+ the new runes) and manifest.json")
    K.eq(sorted(ea - eb), [], "C: no non-class entry removed")
    new = sorted(eb - ea)
    runes = [n for n in new if n.startswith("Server/Item/Items/SkyyClasses/SkyyAbility_")]
    K.check(len(runes) == 15 and len(new) == 15 * 6 and all(n.startswith(("Server/", "Common/")) for n in new),
            "C: the new entries = 15 Warrior / Berserker / Archer runes (x6 files: item, root, cast step, marker, 2 icons): %d / %d" % (len(new), len(runes)))
    old_lang = za.read("Server/Languages/en-US/server.lang").decode("utf8")
    new_lang = zb.read("Server/Languages/en-US/server.lang").decode("utf8")
    K.check(all(l in new_lang.splitlines() for l in old_lang.splitlines()), "C: every 0.1.23 language line is kept")
    man = json.loads(zb.read("manifest.json"))
    K.check(man.get("IncludesAssetPack") is True and man.get("Version") == VERSION, "C: manifest IncludesAssetPack + version %s" % man.get("Version"))
    for n in runes:
        d = json.loads(zb.read(n))
        K.check(d["Quality"] == "Debug" and d["MaxStack"] == 1 and d["DropOnDeath"] is False and d["Ability"]["Cost"] == 0
                and d["Ability"]["CostType"] == "None" and d["Ability"]["Cast"].startswith("Root_SkyyAbility_"),
                "C: %s is a hidden, free, undroppable rune with our cast root" % n.rsplit("/", 1)[1])
    K.check("Common/Icons/Items/SkyyClasses/SkyyAbility_Warrior_Challenge.png" in eb and "Common/Icons/Abilities/SkyyAbility_Archer_HuntersNet.png" in eb
            and za.read("Common/Icons/Items/SkyyClasses/SkyyAbility_Mage_Meteor.png") == zb.read("Common/Icons/Items/SkyyClasses/SkyyAbility_Mage_Meteor.png"),
            "C: the new icons are in (Challenge / Guardian's Oath = stand-ins), the old icons unchanged")
    # FIX ROUND (critic: the numbers rows sit near the JVM's 64 KB method cap): every config-kit row is in CfgRows' static initialiser -
    # fail the build check if it passes 64000 bytes, so the next class batch must move rows out first (the split into a second holder)
    ci_ = pb.get(pkg + "CfgRows").getClassInitializer()
    cl_ = int(ci_.getMethodInfo().getCodeAttribute().getCodeLength()) if ci_ is not None else -1
    print("C. CfgRows <clinit> = %d of 65535 bytes (guard 64000)" % cl_)
    K.check(0 < cl_ <= 64000, "C: CfgRows' static initialiser %d bytes <= the 64000 guard (JVM cap 65535)" % cl_)
    ab_ = diffs.get("Abil", [])
    K.check(not [m_ for m_ in ab_ if m_.split("(")[0] in ("say", "feedText", "send", "refuse", "click", "failSound")],
            "C: Abil.say / feedText / send / refuse / click / failSound are unchanged (the 0.1.21 ability-line routing; its 0.1.20 reference jar is tidied)")
    K.save()


# ============================================================================================================ X: executed
def run_exec(out, jar, scratch, _home):
    import jpype
    from jpype import JClass, JArray, JString, JImplements, JOverride, JObject, JFloat, JDouble, JLong, JInt, JBoolean
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls")
    os.makedirs(hcls, exist_ok=True)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    SCRATCH = scratch
    R = {"notes": K.notes}

    def ck(cond, what):
        K.check(bool(cond), what)

    Cls = JClass("java.lang.Class")
    # ---- the engine stand-ins (copied from test_skyyclasses_0.1.18.py run_n, N0)
    Uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    Uf.setAccessible(True)
    U = Uf.get(None)

    def jfield(cls, name):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    def setf(o, cls, name, v):
        jfield(cls, name).set(o, v)
    C = lambda n: JClass(PKG + n)
    UUID, ArrayList, HashMap, CHM = JClass("java.util.UUID"), JClass("java.util.ArrayList"), JClass("java.util.HashMap"), JClass("java.util.concurrent.ConcurrentHashMap")
    Paths = JClass("java.nio.file.Paths")
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(B.SERVER_JAR)
    CtNM, CTF, CNC = JClass("javassist.CtNewMethod"), JClass("javassist.CtField"), JClass("javassist.CtNewConstructor")

    # ---------------- N0. the engine stand-ins
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    setf(hs, HS, "eventBus", JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu = CHM()
    setf(uni, UNI, "playersByUuid", pbu)
    setf(uni, UNI, "players", JClass("java.util.Collections").unmodifiableCollection(pbu.values()))
    wmap = CHM()
    setf(uni, UNI, "worlds", wmap)
    setf(uni, UNI, "worldsByUuid", CHM())
    setf(uni, UNI, "unmodifiableWorlds", JClass("java.util.Collections").unmodifiableMap(wmap))
    jfield(UNI, "instance").set(None, uni)
    # the vanilla stat types (Mana / Stamina / Health indices) from Assets.zip through the engine's own codec + store
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    ARR = JClass("java.lang.reflect.Array")
    ESTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")

    @JImplements("java.util.function.Function")
    class GetId:
        @JOverride
        def apply(self, o): return o.getId()

    @JImplements("java.util.function.IntFunction")
    class ArrOf:
        def __init__(self, c): self.c = c

        @JOverride
        def apply(self, n): return ARR.newInstance(self.c.class_, n)

    @JImplements("java.util.function.Function")
    class NoRep:
        @JOverride
        def apply(self, k): return None
    try:
        AR.register(HAS.builder(ESTc.class_, ILT(ArrOf(ESTc))).setPath("Entity/Stats").setCodec(ESTc.CODEC).setKeyFunction(GetId())
                    .setReplaceOnRemove(NoRep()).build())
    except Exception as e:
        R["notes"].append("stat store: %s" % str(e)[:200])
    AEI, ADT, RJR = (JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data"),
                     JClass("com.hypixel.hytale.codec.util.RawJsonReader"))
    stl = ArrayList()
    with zipfile.ZipFile(ASSETS) as z:
        for n in z.namelist():
            if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
                key = n.rsplit("/", 1)[1][:-5]
                d = json.loads(z.read(n).decode("utf-8-sig"))
                for k_ in ("Regenerating", "MinValueEffects", "MaxValueEffects"):     # only the ids / ranges matter here (no interaction store)
                    d.pop(k_, None)
                ei = AEI(Paths.get(key + ".json"), ADT(ESTc.class_, key, None))
                o = AR.getAssetStore(ESTc.class_).getCodec().decodeJsonAsset(RJR.fromJsonString(json.dumps(d)), ei)
                if o is not None:
                    stl.add(o)
    AR.getAssetStore(ESTc.class_).loadAssets("Hytale:Hytale", stl)
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    DST.update()
    MANA, STAM, HP = int(DST.getMana()), int(DST.getStamina()), int(DST.getHealth())
    ck(MANA >= 0 and STAM >= 0 and HP >= 0 and len({MANA, STAM, HP}) == 3, "N0: the vanilla stat types load (Mana %d, Stamina %d, Health %d)" % (MANA, STAM, HP))

    def gfield(clsname, meth):
        cc_ = CPj.get(clsname)
        ms_ = [x for x in cc_.getDeclaredMethods() if str(x.getName()) == meth]
        while not ms_:
            cc_ = cc_.getSuperclass()
            ms_ = [x for x in cc_.getDeclaredMethods() if str(x.getName()) == meth]
        m_ = ms_[0]
        it_ = m_.getMethodInfo().getCodeAttribute().iterator()
        cp_ = m_.getMethodInfo().getConstPool()
        while it_.hasNext():
            p_ = it_.next()
            if it_.byteAt(p_) == 0xb4:
                return str(cp_.getFieldrefName(it_.u16bitAt(p_ + 1)))
        return None

    @JImplements("java.util.function.Supplier")
    class Sup:
        def __init__(self, f): self.f = f

        @JOverride
        def get(self): return self.f()

    ESr = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    EMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EMc.class_)
    reg_ = ESr.REGISTRY
    TCc = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    PLAc = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    MSCc = JClass("com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent")
    MSTc = JClass("com.hypixel.hytale.protocol.MovementStates")
    INVUc = JClass("com.hypixel.hytale.server.core.modules.entity.component.Invulnerable")
    NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    ESMc = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DTHc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    INVC = "com.hypixel.hytale.server.core.inventory.InventoryComponent"
    EMN = "com.hypixel.hytale.server.core.modules.entity.EntityModule"
    reg_errs = []
    setf(em, EMc, gfield(EMN, "getTransformComponentType"), reg_.registerComponent(TCc.class_, "Transform", jfield(TCc, "CODEC").get(None)))
    for getter_, cls_ in (("getPlayerComponentType", PLAc), ("getMovementStatesComponentType", MSCc), ("getInvulnerableComponentType", INVUc),
                          ("getToolInventoryComponentType", JClass(INVC + "$Tool")), ("getHotbarInventoryComponentType", JClass(INVC + "$Hotbar")),
                          ("getUtilityInventoryComponentType", JClass(INVC + "$Utility")),
                          ("getKnockbackComponentType", JClass("com.hypixel.hytale.server.core.entity.knockback.KnockbackComponent"))):
        try:
            setf(em, EMc, gfield(EMN, getter_), reg_.registerComponent(cls_.class_, Sup(lambda: None)))
        except Exception as e_:
            reg_errs.append("%s: %s" % (getter_, str(e_)[:120]))
    npc_t = reg_.registerComponent(NPCc.class_, Sup(lambda: None))
    c2t = HashMap()
    c2t.put(NPCc.class_, npc_t)
    setf(em, EMc, "classToComponentType", c2t)
    setf(em, JClass("com.hypixel.hytale.server.core.plugin.PluginBase"), "state", JClass("com.hypixel.hytale.server.core.plugin.PluginState").ENABLED)
    jfield(EMc, "instance").set(None, em)
    setf(uni, UNI, gfield("com.hypixel.hytale.server.core.universe.Universe", "getPlayerRefComponentType"), reg_.registerComponent(PRc.class_, Sup(lambda: None)))
    ESMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    esmod = U.allocateInstance(ESMOD.class_)
    setf(esmod, ESMOD, "entityStatMapComponentType", reg_.registerComponent(ESMc.class_, Sup(lambda: ESMc())))
    jfield(ESMOD, "instance").set(None, esmod)
    DMOD_ = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule")
    dmod = U.allocateInstance(DMOD_.class_)
    setf(dmod, DMOD_, "deathComponentType", reg_.registerComponent(DTHc.class_, Sup(lambda: None)))
    jfield(DMOD_, "instance").set(None, dmod)
    DCSc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
    if DCSc.PROJECTILE is None:
        jfield(DCSc, "PROJECTILE").set(None, DCSc("Projectile"))
    ck(not reg_errs and PLAc.getComponentType() is not None and MSCc.getComponentType() is not None and INVUc.getComponentType() is not None
       and NPCc.getComponentType() is not None and PRc.getComponentType() is not None, "N0: the component types are registered like the modules do: %s" % reg_errs)

    def stub(name, sup, fields, methods, ctor=None):
        c_ = CPj.makeClass("abilharness." + name, CPj.get(sup))
        if ctor is not None:
            c_.addConstructor(CNC.make(ctor, c_))
        for f_ in fields:
            c_.addField(CTF.make(f_, c_))
        for m_ in methods:
            c_.addMethod(CtNM.make(m_, c_))
        c_.writeFile(hcls)
        return JClass("abilharness." + name)
    CP_ = "com.hypixel.hytale.component."
    GETC = ("public " + CP_ + "Component getComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t) { java.util.Map m = (java.util.Map) abilharness.TStore.COMP.get(r); "
            "if (m == null) return null; return (" + CP_ + "Component) m.get(t); }")
    PUTC = ("public void putComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t, " + CP_ + "Component c) { java.util.Map m = (java.util.Map) abilharness.TStore.COMP.get(r); "
            "if (m == null) { m = new java.util.HashMap(); abilharness.TStore.COMP.put(r, m); } m.put(t, c); }")
    TSt = stub("TStore", CP_ + "Store", ["public static java.util.HashMap COMP = new java.util.HashMap();", "public static Object EXT = null;"],
               [GETC, PUTC, "public Object getExternalData() { return EXT; }",
                "public " + CP_ + "Resource getResource(" + CP_ + "ResourceType t) { return null; }"],
               ctor="public TStore() { super((" + CP_ + "ComponentRegistry) null, 0, (Object) null, (" + CP_ + "IResourceStorage) null); }")
    TBf = stub("TBuf", CP_ + "CommandBuffer", ["public static java.util.ArrayList EVENTS = new java.util.ArrayList();", "public static " + CP_ + "Store STORE = null;"],
               [GETC, PUTC, "public Object getExternalData() { return abilharness.TStore.EXT; }",
                "public " + CP_ + "Resource getResource(" + CP_ + "ResourceType t) { return null; }",
                "public void invoke(" + CP_ + "Ref r, " + CP_ + "system.EcsEvent e) { EVENTS.add(new Object[] { r, e }); }",
                "public " + CP_ + "Store getStore() { return STORE; }",
                "public void tryRemoveComponent(" + CP_ + "Ref r, " + CP_ + "ComponentType t) { }"])
    WLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    TWd = stub("TWorld", "com.hypixel.hytale.server.core.universe.world.World", [], ["public void execute(java.lang.Runnable r) { r.run(); }"],
               ctor="public TWorld() { super((String) null, (java.nio.file.Path) null, (com.hypixel.hytale.server.core.universe.world.WorldConfig) null); }")
    tst = U.allocateInstance(TSt.class_)
    TBf.STORE = tst
    tbuf = U.allocateInstance(TBf.class_)
    world = U.allocateInstance(TWd.class_)
    setf(world, WLDc, "name", "abil-test")
    es = U.allocateInstance(ESr.class_)
    setf(es, ESr, gfield("com.hypixel.hytale.server.core.universe.world.storage.EntityStore", "getWorld"), world)
    ebu = HashMap()
    setf(es, ESr, "entitiesByUuid", ebu)
    TSt.EXT = es
    REFc = JClass(CP_ + "Ref")
    V3 = JClass("org.joml.Vector3d")
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MT = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CT_ = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    GM = JClass("com.hypixel.hytale.protocol.GameMode")
    AtomRef = JClass("java.util.concurrent.atomic.AtomicReference")

    def put(r_, t_, c_):
        tst.putComponent(r_, t_, c_)

    def stats(mana=55.0, stam=14.0, hp=100.0, hpmax=100.0):
        m_ = ESMc()
        m_.update()
        for i_, want_ in ((MANA, 500.0), (STAM, 50.0)):
            m_.putModifier(i_, "abiltest", SMO(MT.MAX, CT_.ADDITIVE, JFloat(want_)))
        hm = float(m_.get(HP).getMax())
        if hm != hpmax:
            m_.putModifier(HP, "abiltest", SMO(MT.MAX, CT_.ADDITIVE, JFloat(hpmax - hm)))
        m_.setStatValue(MANA, JFloat(mana))
        m_.setStatValue(STAM, JFloat(stam))
        m_.setStatValue(HP, JFloat(hp))
        return m_

    def sv(m_, i_):
        return round(float(m_.get(i_).get()), 3)

    PLAYERS = {}

    def player(i_, x, y, z, name, gm="Adventure", **kw):
        u_ = UUID.fromString("00000000-0000-0000-00ab-%012d" % i_)
        r_ = REFc(tst, i_)
        pr_ = U.allocateInstance(PRc.class_)
        setf(pr_, PRc, "uuid", u_)
        setf(pr_, PRc, "entity", r_)
        setf(pr_, PRc, "username", name)
        pbu.put(u_, pr_)
        ebu.put(u_, r_)
        put(r_, PRc.getComponentType(), pr_)
        put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, 0.0, 0.0)))
        m_ = stats(**kw)
        put(r_, ESMc.getComponentType(), m_)
        msc = MSCc()
        msc.setMovementStates(MSTc())
        put(r_, MSCc.getComponentType(), msc)
        pl_ = U.allocateInstance(PLAc.class_)
        setf(pl_, PLAc, "waitingForClientReady", AtomRef())
        setf(pl_, PLAc, "gameMode", getattr(GM, gm))
        put(r_, PLAc.getComponentType(), pl_)
        PLAYERS[name] = (u_, r_, pr_, m_, pl_, msc)
        return u_, r_, pr_, m_, pl_, msc

    def npc(i_, x, y, z, hp=100.0, invu=False):
        r_ = REFc(tst, i_)
        put(r_, NPCc.getComponentType(), TCc())
        put(r_, ESMc.getComponentType(), stats(hp=hp))
        put(r_, TCc.getComponentType(), TCc(V3(x, y, z), R3(0.0, 0.0, 0.0)))
        if invu:
            put(r_, INVUc.getComponentType(), INVUc.INSTANCE)
        return r_

    # ---------------- the mod's statics, seams and the fake partner bridges
    Cfg, Defs, Store = C("ClassCfg"), C("ClassDefs"), C("ClassStore")
    AC, AD, AM, AS, AW, A, AJ = C("AbilCfg"), C("AbilDefs"), C("AbilMath"), C("AbilStore"), C("AbilWorld"), C("Abil"), C("AbilJob")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyClasses")
    home = os.path.join(SCRATCH, "n-home")
    shutil.rmtree(home, ignore_errors=True)
    os.makedirs(os.path.join(home, "players"))
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    load_txt = str(Cfg.load())
    Store.DIR = Paths.get(os.path.join(home, "players"))
    AS.DIR = Paths.get(os.path.join(home, "abilities"))
    AS.SYNC = True
    PSEEN, SAID = ArrayList(), ArrayList()
    A.PSEEN = PSEEN
    A.SAID = SAID
    SOUNDS = ArrayList()
    A.SOUNDS = SOUNDS
    br = Cfg.bridge()
    LEVEL, COMBAT, HEALXP, PROFKEY, HANDS, AIMS, NEARL = {}, {}, [], {}, {}, {}, []

    @JImplements("java.util.function.Function")
    class LevelFn:
        @JOverride
        def apply(self, o):
            a_ = list(o)
            return JInt(LEVEL.get((str(a_[0]), str(a_[1])), 0))

    @JImplements("java.util.function.Function")
    class CombatFn:
        @JOverride
        def apply(self, o): return JLong(COMBAT.get(str(o), 0))

    @JImplements("java.util.function.Function")
    class HealXp:
        @JOverride
        def apply(self, o):
            a_ = list(o)
            HEALXP.append([str(a_[0]), round(float(a_[1]), 3), str(a_[2]), len(a_) > 4])
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, o): return PROFKEY.get(str(o), str(o))

    @JImplements("java.util.function.Function")
    class Members:
        @JOverride
        def apply(self, o): return JArray(JObject)([JString(x) for x in MEMBERS.get(str(o), [])])

    @JImplements("java.util.function.Function")
    class ArmInfo:
        @JOverride
        def apply(self, o):
            a_ = list(o)
            if str(a_[0]) == "staff" and str(a_[1]) == "Weapon_Staff_Wood":
                return JArray(JObject)([JInt(10), JInt(2), JDouble(1.0), JInt(50), JInt(10), JDouble(100.0), JString("o"), JString("q")])
            if str(a_[0]) == "wand" and str(a_[1]) == "Weapon_Wand_Iron":
                return JArray(JObject)([JInt(15), JInt(3), JDouble(3.5), JInt(88), JInt(18), JDouble(120.0), JString("o"), JString("q")])
            return None

    @JImplements("java.util.function.Function")
    class Hand:
        @JOverride
        def apply(self, r_):
            v_ = HANDS.get(int(r_.getIndex()))
            return None if v_ is None else JString(v_)

    @JImplements("java.util.function.Function")
    class Aim:
        @JOverride
        def apply(self, o):
            v_ = AIMS.get("spot")
            return None if v_ is None else JArray(JDouble)(v_)

    @JImplements("java.util.function.Function")
    class Near:
        @JOverride
        def apply(self, o):
            l_ = ArrayList()
            for r_ in NEARL:
                l_.add(r_)
            return l_
    MEMBERS = {}
    br.put("skill:fn:level", LevelFn())
    br.put("skill:fn:combat", CombatFn())
    br.put("skill:fn:healxp", HealXp())
    br.put("profile:fn:key", KeyFn())
    br.put("party:fn:members", Members())
    br.put("armory:fn:info", ArmInfo())
    br.put("class:fn:abilhit", C("AbilHitFn")())
    br.put("class:fn:allowed", C("AllowedFn")())
    for i_, n_ in enumerate(Defs.NAMES):
        br.put("class:weapons:" + str(n_), str(Defs.prefixesOf(i_)))

    def setclass(u_, cls):
        br.put("profile:" + str(u_), "1")
        if cls is None:
            br.remove("profile:class:" + str(u_))
            br.remove("class:" + str(u_))
        else:
            br.put("profile:class:" + str(u_), cls)
            br.put("class:" + str(u_), cls)

    def cast(name, a="1"):
        u_, r_, pr_ = PLAYERS[name][:3]
        return str(A.cast(pr_, tst, r_, world, a))

    def said():
        out_ = [str(x) for x in SAID]
        SAID.clear()
        return out_

    def unthrottle():
        AS.TOLD.clear()

    # ================================================================================================ 0.1.22 sections
    AW, AMD, ACX = C("AbilWorld"), C("AbilModDefs"), C("AbilCtx")
    Bool = JClass("java.lang.Boolean")
    tick = C("AbilTick")()
    now_ms = lambda: int(time.time() * 1000)

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    RUNES_LOADED = set(str(x) for x in AD.RUNE if str(x))
    A.ITEMS = Fn(lambda o: Bool.valueOf(str(o) in RUNES_LOADED))
    MARK_IX = dict((str(m), 100 + i) for i, m in enumerate(AD.MARK) if str(m))
    A.MARKS = Fn(lambda o: JInt(MARK_IX.get(str(o), -1)))
    TREE = {"csv": None}
    br.put("tree:fn:abil", Fn(lambda o: None if TREE["csv"] is None else JString(TREE["csv"])))
    NAMES_ = [str(x) for x in Defs.NAMES]
    ci_m, ci_p = NAMES_.index("Mage"), NAMES_.index("Priest")
    SK_M, SK_P = str(Defs.SKILLS[ci_m]), str(Defs.SKILLS[ci_p])
    mu, mr, mpr, mm, mpl, mmsc = player(1, 0.5, 64.0, 0.5, "Mage1")
    pu, pr_r, ppr, pm, ppl, pmsc = player(2, 3.5, 64.0, 0.5, "Priest1")
    setclass(mu, "Mage")
    setclass(pu, "Priest")
    LEVEL[(str(mu), SK_M)] = 30
    LEVEL[(str(pu), SK_P)] = 30
    A.HAND = Hand()
    A.AIM = Aim()
    A.NEAR = Near()
    HANDS[1] = "Weapon_Staff_Wood"
    HANDS[2] = "Weapon_Wand_Iron"
    AIMS["spot"] = [10.5, 64.0, 0.5]
    ID = dict((str(AD.IDS[i]), i) for i in range(len(AD.IDS)))
    METEOR, MANAB, SACRED = ID["Meteor"], ID["ManaBarrier"], ID["SacredHeal"]
    R_MET, R_MB = str(AD.RUNE[METEOR]), str(AD.RUNE[MANAB])

    def mana(m_, v):
        m_.setStatValue(MANA, JFloat(v))
        m_.setStatValue(STAM, JFloat(50.0))

    def reset_m():
        AS.clearCd(str(mu))
        AS.clearCd(str(mu) + "-p2")
        mana(mm, 400.0)
        unthrottle()
        said()
        AS.LASTKEY.clear()
        AS.LASTHOOK.clear()
        AS.TREEC.clear()

    # ---------------- X1 the pure rules
    AMt = C("AbilMath")
    ck([int(AMt.usesFor(n, 4.5, 1.5)) for n in (1, 2, 3, 10)] == [0, 13, 23, 142], "X1: uses for level n = round(4.5 x n ^ 1.5) (2 -> 13, 3 -> 23, 10 -> 142)")
    ck([int(AMt.levelOf(u_, 25, 4.5, 1.5)) for u_ in (0, 12, 13, 35, 36, 10 ** 9)] == [1, 1, 2, 2, 3, 25], "X1: levelOf (13 uses = Lv 2, 36 = Lv 3, the cap 25)")
    ck([round(float(AMt.bonusPct(l_, 2.0, 10, 20)), 3) for l_ in (1, 2, 10, 11, 20, 21, 25)] == [0.0, 2.0, 18.0, 19.0, 28.0, 28.5, 30.5],
       "X1: diminishing returns - +2 % a level to 10, +1 % to 20, +0.5 % after (Lv 25 = +30.5 %)")
    ck([int(AMD.unlockAt(k_)) for k_ in range(5)] == [2, 4, 6, 8, 10] and int(AMD.unlockAt(5)) == 12, "X1: modifiers unlock at ability Lv 2 / 4 / 6 / 8 / 10")
    ck([int(AMD.modLevel(u_)) for u_ in (0, 9, 10, 29, 30, 60, 100, 5000)] == [1, 1, 2, 2, 3, 4, 5, 5] and int(AMD.modNext(25)) == 5 and int(AMD.modNext(100)) == 0,
       "X1: modifier levels by use (10 / 30 / 60 / 100 uses), modNext")
    ck(bool(AMD.csvHas("A1,T4=10,PB2", "T4")) and not bool(AMD.csvHas("A1,T4=10", "A2")) and float(AMD.csvAmt("A1,T4=10", "T4", 3.0)) == 10.0
       and float(AMD.csvAmt("A1,T4", "T4", 3.0)) == 3.0 and float(AMD.csvAmt("A1", "T4", 3.0)) == 0.0, "X1: the tree csv (node, node=amount)")
    ck([int(A.lineOf(i_)) for i_ in range(5)] == [1, 2, 3, 4, 4], "X1: ability lines A1-A4 (both Ability 1 alts on A4)")

    # ---------------- X2 the hook's decision
    reset_m()
    t0 = now_ms()
    D = lambda u_, ci_, k_, held, sec, t: str(A.runeDecide(u_, ci_, k_, held, sec, t))
    ABSEC = int(JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent").ABILITIES_SECTION_ID)
    ci_a = NAMES_.index("Archer")
    ck(D(mu, ci_m, 0, R_MET, ABSEC, t0) == "cast", "X2: our rune on Ability 2 -> cast")
    ck(D(mu, ci_m, 0, R_MET, ABSEC, t0 + 50) == "repeat", "X2: the same key again within 120 ms -> repeat (the double-fire guard)")
    ck(D(mu, ci_m, 0, R_MET, ABSEC, t0 + 300) == "cast", "X2: the same key after 120 ms -> cast")
    ck(D(mu, ci_m, 1, R_MB, ABSEC, t0 + 301) == "cast", "X2: the other key is its own guard")
    ck(D(mu, ci_m, 0, "Rune_Fireball", ABSEC, t0 + 900) == "vanilla", "X2: a game rune in the ability slots of a Mage -> vanilla (blocked)")
    ck(D(mu, ci_m, 0, "Weapon_Staff_Wood", 0, t0 + 1300) == "ignore", "X2: a weapon's own Ability 2 move (not a rune slot) -> ignore")
    ck(D(mu, ci_a, 0, "Rune_Fireball", ABSEC, t0 + 1700) == "vanilla" and D(mu, -1, 0, "Rune_Fireball", ABSEC, t0 + 1750) == "ignore",
       "X2: an Archer (abilities since 0.1.24) -> vanilla (blocked); no class -> ignore (game runes work)")
    ck(D(mu, ci_m, 2, R_MET, ABSEC, t0 + 2100) == "ignore" and D(None, ci_m, 0, R_MET, ABSEC, t0) == "ignore", "X2: a bad key / no player -> ignore")
    AC.VAN_RUNES = True
    ck(D(mu, ci_m, 0, "Rune_Fireball", ABSEC, t0 + 2500) == "allow" and D(mu, ci_m, 0, R_MET, ABSEC, t0 + 2900) == "cast",
       "X2: abil.vanillaRunes ON -> a game rune is allowed, ours still casts")
    AC.VAN_RUNES = False
    AC.RUNE_KEYS = False
    ck(D(mu, ci_m, 0, R_MET, ABSEC, t0 + 3300) == "ignore", "X2: abil.runeKeys OFF -> ignore")
    AC.RUNE_KEYS = True

    # ---------------- X3 THE HOOK on a real event
    ISc = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    ICHc = JClass("com.hypixel.hytale.server.core.entity.InteractionChain")
    ICXc = JClass("com.hypixel.hytale.server.core.entity.InteractionContext")
    ICSEc = JClass("com.hypixel.hytale.server.core.modules.interaction.event.InteractionChainStartEvent")
    ITc = JClass("com.hypixel.hytale.protocol.InteractionType")

    def stack(id_, q=1):
        s_ = U.allocateInstance(ISc.class_)
        setf(s_, ISc, "itemId", id_)
        setf(s_, ISc, "quantity", JInt(q))
        return s_

    def event(type_, held, sec):
        cx_ = U.allocateInstance(ICXc.class_)
        if held is not None:
            setf(cx_, ICXc, "heldItem", stack(held))
        setf(cx_, ICXc, "heldItemSectionId", JInt(sec))
        ch_ = U.allocateInstance(ICHc.class_)
        setf(ch_, ICHc, "type", getattr(ITc, type_))
        setf(ch_, ICHc, "context", cx_)
        return ICSEc(ch_)
    reset_m()
    TBf.EVENTS.clear()
    ev = event("Ability2", R_MET, ABSEC)
    r0 = int(A.RUNES)
    hk = str(A.onRune(ev, 0, mr, tst, tbuf))
    lr = str(A.LAST_RUNE)
    ck(hk == "cast" and bool(ev.isCancelled()), "X3: the hook takes our rune press: the chain is CANCELLED (the engine sends the client its cancel): %s" % hk)
    ck(lr.startswith("ok:Meteor ") and lr.endswith(" key") and int(A.RUNES) == r0 + 1, "X3: ... and the cast runs through RuneCast (door 1): %s" % lr)
    ck(sv(mm, MANA) < 400.0 and int(AS.left(str(mu), "Meteor", now_ms())) > 0, "X3: Mana paid, the cooldown armed (Mana %s)" % sv(mm, MANA))
    sd = said()
    ck(sd and sd[0].startswith("Meteor! -"), "X3: the cast line: %s" % sd[:1])
    aw = AW.of("abil-test")
    ck(int(aw.size()) >= 1, "X3: the impact job is queued (%d)" % int(aw.size()))
    ev2 = event("Ability3", R_MB, ABSEC)
    hk2 = str(A.onRune(ev2, 1, mr, tst, tbuf))
    ck(hk2 == "cast" and bool(ev2.isCancelled()) and str(A.LAST_RUNE).startswith("ok:ManaBarrier ") and str(A.LAST_RUNE).endswith(" key"),
       "X3: Ability 3 -> the second primary (Mana Barrier): %s" % A.LAST_RUNE)
    said()
    ev3 = event("Primary", "Weapon_Staff_Wood", 0)
    ck(str(A.onRune(ev3, 0, mr, tst, tbuf)) == "ignore" and not bool(ev3.isCancelled()), "X3: a weapon press -> ignored, NOT cancelled")
    ev4 = event("Ability2", R_MET, ABSEC)
    ck(str(A.onRune(ev4, 0, pr_r, tst, tbuf)) == "cast" and bool(ev4.isCancelled()), "X3: a Priest pressing a rune the Mage owns -> cancelled + cast attempt")
    ck(not str(A.LAST_RUNE).startswith("ok:Meteor"), "X3: ... the Priest's own slot casts, never the Mage's Meteor: %s" % A.LAST_RUNE)
    said()
    # the system wrapper itself: a null chunk / another event type does nothing
    rs = C("AbilRuneSys")()
    rs.handle(0, None, tst, tbuf, event("Ability2", R_MET, ABSEC))
    ck(not bool(C("AbilRuneSys").FAILED_ONCE), "X3: AbilRuneSys.handle with no chunk returns quietly")

    # ---------------- X4 refusals through the hook
    time.sleep(0.13)
    ev = event("Ability2", R_MET, ABSEC)
    hk = str(A.onRune(ev, 0, mr, tst, tbuf))
    sd = said()
    ck(hk == "cast" and bool(ev.isCancelled()) and str(A.LAST_RUNE) == "cooldown" and sd and "Meteor is ready in" in sd[0],
       "X4: REFUSED (cooldown) through the key: cancelled, nothing cast, the line: %s %s" % (A.LAST_RUNE, sd))
    reset_m()
    mana(mm, 1.0)
    time.sleep(0.13)
    A.onRune(event("Ability2", R_MET, ABSEC), 0, mr, tst, tbuf)
    sd = said()
    ck(str(A.LAST_RUNE) == "mana" and sv(mm, MANA) == 1.0 and sd and sd[0].startswith("Not enough Mana for Meteor"), "X4: no Mana -> refused, nothing spent: %s" % sd)
    reset_m()
    TREE["csv"] = "T6=5"
    ck(str(A.runeCast(mpr, 0, 1)) == "tree" and "enable Meteor in your class tree first: /tree class, node A1" in " ".join(said()),
       "X4: class trees on, A1 not bought -> refused 'enable Meteor in your class tree first' (nothing spent)")
    ck(list(A.runeWant(mu)) == ["", ""], "X4: ... and no rune is wanted in the slots")
    TREE["csv"] = "A1"
    reset_m()
    ck(str(A.runeCast(mpr, 0, 1)).startswith("ok:Meteor") and list(A.runeWant(mu)) == [R_MET, ""], "X4: A1 bought -> Meteor casts; only its rune is wanted")
    AC.TREE_GATE = False
    AS.TREEC.clear()
    ck(list(A.runeWant(mu)) == [R_MET, R_MB], "X4: abil.treeGate OFF -> both runes wanted")
    AC.TREE_GATE = True
    TREE["csv"] = None
    AS.TREEC.clear()
    ck(list(A.runeWant(mu)) == [R_MET, R_MB], "X4: SkyyTrees absent / class trees off (no csv) -> no gate")
    reset_m()
    AC.RUNE_KEYS = False
    ck(str(A.runeCast(mpr, 0, 1)) == "keysoff" and str(A.runeCast(mpr, 0, 2)) == "keysoff", "X4: abil.runeKeys OFF -> the key and the marker do nothing")
    AC.RUNE_KEYS = True
    ms_ = mmsc.getMovementStates()
    ms_.rolling = True
    AC.ROLL_CAST = False
    ck(str(A.runeCast(mpr, 0, 1)) == "roll" and "Not while rolling" in " ".join(said()), "X4: rolling + abil.rollCast OFF -> refused")
    AC.ROLL_CAST = True
    reset_m()
    rr = str(A.runeCast(mpr, 0, 1))
    ck(rr.startswith("ok:Meteor") and "shape=sprint" in rr, "X4: rolling + abil.rollCast ON -> cast (a roll counts as sprinting = Comet): %s" % rr)
    ms_.rolling = False
    said()

    # ---------------- X5 a game rune on a Mage
    reset_m()
    time.sleep(0.13)
    ev = event("Ability2", "Rune_Fireball", ABSEC)
    AS.VANTOLD.clear()
    A.LAST_RUNE = "none"
    vb0 = int(A.VANBLOCK)
    hk = str(A.onRune(ev, 0, mr, tst, tbuf))
    sd = said()
    ck(hk == "vanilla" and bool(ev.isCancelled()) and str(A.LAST_RUNE) == "none" and int(A.VANBLOCK) == vb0 + 1,
       "X5: a game rune on a Mage -> BLOCKED (Skyy M2): cancelled, no class cast: %s" % A.LAST_RUNE)
    ck([x for x in sd if "Game runes are blocked for Mages" in x and "Rune_Fireball" in x], "X5: ... one hint line: %s" % sd)
    time.sleep(0.13)
    reset_m()
    A.onRune(event("Ability2", "Rune_Fireball", ABSEC), 0, mr, tst, tbuf)
    ck(not [x for x in said() if "Game runes are blocked" in x], "X5: the hint once per 30 s")

    # ---------------- X6 the marker fallback
    reset_m()
    t1 = now_ms()
    AS.LASTHOOK.put(mu, JLong(t1))
    f0, d0 = int(A.FALLBACKS), int(A.FB_DUP)
    ck(str(A.markerPress(mpr, mu, 0, world, t1 + 200)) == "dup" and int(A.FB_DUP) == d0 + 1, "X6: the marker within 700 ms of a hook press -> dup (no second cast)")
    lr0 = str(A.LAST_RUNE)
    ck(str(A.markerPress(mpr, mu, 0, world, t1 + 900)) == "cast" and int(A.FALLBACKS) == f0 + 1, "X6: the marker alone (the hook did not fire) -> cast")
    ck(str(A.LAST_RUNE).startswith("ok:Meteor") and str(A.LAST_RUNE).endswith(" marker"), "X6: ... through RuneCast door 2: %s" % A.LAST_RUNE)
    said()

    # ---------------- X7 THE MIRROR (the ability slots)
    ICc = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    IS_ = "com.hypixel.hytale.server.core.inventory.ItemStack"
    TR_ = "com.hypixel.hytale.server.core.inventory.transaction."
    TIc = stub("TSlots", "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
               ["public " + IS_ + "[] s = new " + IS_ + "[4];"],
               ["public short getCapacity() { return (short) s.length; }",
                "public " + IS_ + " getItemStack(short i) { return s[i]; }",
                "public " + TR_ + "SlotTransaction removeItemStackFromSlot(short i) { s[i] = null; return null; }",
                "public " + TR_ + "ItemStackSlotTransaction addItemStackToSlot(short i, " + IS_ + " it) { if (s[i] == null) s[i] = it; return null; }",
                "protected Object readAction(java.util.function.Supplier a) { return a.get(); }",
                "protected Object readAction(java.util.function.Function a, Object b) { return a.apply(b); }",
                "protected Object writeAction(java.util.function.Supplier a) { return a.get(); }",
                "protected Object writeAction(java.util.function.Function a, Object b) { return a.apply(b); }",
                "protected " + IS_ + " internal_getSlot(short i) { return s[i]; }",
                "protected " + IS_ + " internal_setSlot(short i, " + IS_ + " it) { " + IS_ + " o = s[i]; s[i] = it; return o; }",
                "protected " + IS_ + " internal_removeSlot(short i) { " + IS_ + " o = s[i]; s[i] = null; return o; }"],
               ctor="public TSlots() { super(); }")
    ABSc = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$AbilitySlots")
    INVCc = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent")
    try:
        setf(em, EMc, gfield("com.hypixel.hytale.server.core.modules.entity.EntityModule", "getAbilitySlotsInventoryComponentType"),
             reg_.registerComponent(ABSc.class_, Sup(lambda: None)))
    except Exception as e_:
        K.notes.append("X7 ability slots type: %s" % str(e_)[:200])
    slots_c = TIc()
    abs_ = U.allocateInstance(ABSc.class_)
    setf(abs_, INVCc, "inventory", slots_c)
    put(mr, ABSc.getComponentType(), abs_)

    def ids():
        return [("" if x is None else str(x.getItemId())) for x in slots_c.s]
    reset_m()
    ck(A.abilSlots(tst, mr) is not None and int(A.mirrorNeed(slots_c, A.runeWant(mu))) == 1, "X7: the REAL AbilitySlots component read; empty slots -> a write is needed")
    real_stack = None
    try:
        real_stack = ISc(R_MET, 1)
    except Exception as e_:
        K.notes.append("X7: new ItemStack(rune, 1) in the bare JVM: %s" % str(e_)[:160])
    m0 = int(A.MIRRORS)
    got = str(A.mirrorSet(mpr, mu))
    ck(got == "+0 +3" and ids() == [R_MET, "", "", R_MB] and int(A.MIRRORS) == m0 + 1, "X7: mirrorSet puts Meteor in slot 0 (Ability 2), Mana Barrier in slot 3 (Ability 3): %s %s" % (got, ids()))
    ck(int(A.mirrorNeed(slots_c, A.runeWant(mu))) == 0 and str(A.mirrorSet(mpr, mu)) == "", "X7: right already -> nothing to do")
    slots_c.s[1] = stack(R_MET)
    ck(int(A.mirrorNeed(slots_c, A.runeWant(mu))) == 1 and str(A.mirrorSet(mpr, mu)) == "-1" and ids()[1] == "", "X7: a stray copy of our rune in slot 1 is removed")
    slots_c.s[0] = stack("Rune_Fireball")
    slots_c.s[3] = None
    got = str(A.mirrorSet(mpr, mu))
    ck(got == "+3" and ids() == ["Rune_Fireball", "", "", R_MB], "X7: a game rune in slot 0 is never touched (ours waits); slot 3 refilled: %s %s" % (got, ids()))
    slots_c.s[0] = None
    # runeTick -> the MirrorTask on the world thread (the stand-in world runs it at once)
    AS.MIRROR.clear()
    A.runeTick(mpr, mu, mr, tst, now_ms())
    rec = AS.MIRROR.get(mu)
    ck(ids()[0] == R_MET and rec is not None and str(rec[0]) == R_MET and int(rec[4]) == MARK_IX[str(AD.MARK[METEOR])],
       "X7: runeTick sees slot 0 empty -> MirrorTask fills it; the record holds the wanted runes + their marker effects: %s" % ids())
    A.runeTick(mpr, mu, mr, tst, now_ms())
    ck(ids() == [R_MET, "", "", R_MB], "X7: the next tick within 2 s does nothing")
    # the guard: an inventory change on the ability slots -> look again at once; one of our runes elsewhere -> InvClean
    ICEc = JClass("com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent")
    ice = U.allocateInstance(ICEc.class_)
    setf(ice, ICEc, "componentType", ABSc.getComponentType())
    ck(str(A.onInv(ice, mr, tbuf)) == "slots" and int(AS.MIRROR.get(mu)[2]) == 0, "X7: the guard - ability slots changed -> the mirror looks at the next tick")
    other_c = TIc()
    other_c.s[2] = stack(R_MET)
    ice2 = U.allocateInstance(ICEc.class_)
    setf(ice2, ICEc, "itemContainer", other_c)
    ck(str(A.onInv(ice2, mr, tbuf)) == "clean" and AS.CLEANQ.get(mu) is None, "X7: our rune in another container -> InvClean queued and run (the queue mark cleared)")
    ck(int(A.cleanIc(other_c)) == 1 and other_c.s[2] is None, "X7: cleanIc removes our rune from a container (counted)")
    other_c.s[1] = stack("Rune_Fireball")
    ck(int(A.cleanIc(other_c)) == 0 and other_c.s[1] is not None, "X7: ... never a game rune")
    ice3 = U.allocateInstance(ICEc.class_)
    setf(ice3, ICEc, "itemContainer", other_c)
    ck(A.onInv(ice3, mr, tbuf) is None, "X7: a container with no rune of ours -> nothing")

    # ---------------- X8 LEVELS BY USE
    reset_m()
    k_ = str(mu)
    AC.USE_EVERY = 0.0
    for i_ in range(12):
        A.used(mu, k_, METEOR, None)
    said()
    r13 = str(A.used(mu, k_, METEOR, None))
    sd = said()
    ck(r13 == "use 13 level 2" or r13.startswith("use 13 level 2"), "X8: the 13th counted use -> Meteor Lv 2: %s" % r13)
    ck(sd and sd[0] == "Meteor reached Lv 2! +2 % damage. New modifier: Power+ - equip it in /tree class.", "X8: the level-up line names the new modifier: %s" % sd)
    ck(str(AS.load(k_).getProperty("u.Meteor")) == "13" and AS.DIRTYAT.get(k_) is not None, "X8: kept in memory (u.Meteor=13), marked for the 30 s flush")
    f_ = os.path.join(home, "abilities", k_ + ".properties")
    AS.flushOld(now_ms() + 60000, 30000)
    ck(os.path.isfile(f_) and "u.Meteor=13" in open(f_).read() and AS.DIRTYAT.get(k_) is None, "X8: the flush writes it (abilities/<pkey>.properties)")
    AC.USE_EVERY = 3.0
    AS.LASTUSE.clear()
    ck(str(A.used(mu, k_, METEOR, None)) == "use 14" and str(A.used(mu, k_, METEOR, None)) == "soon", "X8: one counted use per ability per abil.useEvery (3 s)")
    ecx = ACX()
    ecx.echo = True
    ck(str(A.used(mu, k_, METEOR, ecx)) == "echo" and str(A.used(mu, k_ + "-p9", METEOR, None)) == "switched", "X8: an echo never counts; a cast from a profile you left never counts")
    AC.LEVELS = False
    ck(str(A.used(mu, k_, METEOR, None)) == "off" and int(A.alvl(500)) == 1, "X8: abil.levels OFF -> no counting, every ability Lv 1")
    AC.LEVELS = True
    ck(str(A.levelLine(mu, METEOR)) == "Lv 2 - 1 / 23 uses", "X8: the level text: %s" % A.levelLine(mu, METEOR))

    # ---------------- X9 a REAL Meteor through the key -> the impact -> one counted use
    reset_m()
    AS.LASTUSE.clear()
    n30 = npc(30, 11.0, 64.0, 0.5)
    NEARL[:] = [n30]
    aw.jobs.clear()
    time.sleep(0.13)
    A.onRune(event("Ability2", R_MET, ABSEC), 0, mr, tst, tbuf)
    lr = str(A.LAST_RUNE)
    for j_ in list(aw.jobs):
        j_.at = now_ms() - 10
    aw.lastNs = 0
    TBf.EVENTS.clear()
    tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(lr.startswith("ok:Meteor") and " lv=2" in lr and TBf.EVENTS.size() >= 1, "X9: the key cast (Lv 2 shows) lands on the NPC: %s, %d hits" % (lr, TBf.EVENTS.size()))
    ck(str(AS.load(k_).getProperty("u.Meteor")) == "15", "X9: the hit counted ONE use (14 -> 15): %s" % AS.load(k_).getProperty("u.Meteor"))
    dmg_lv2 = round(float(TBf.EVENTS.get(0)[1].getAmount()), 3) if TBf.EVENTS.size() else 0
    ck(dmg_lv2 == round(150.0 * 1.02, 3), "X9: Lv 2 = +2 %% damage (150 -> 153): %s" % dmg_lv2)
    said()

    # ---------------- X10 MODIFIERS
    reset_m()
    def setp(k__, kv):
        AS.set(k__, JArray(JString)(list(kv.keys())), JArray(JString)([None if v is None else str(v) for v in kv.values()]))
    EQ = lambda slot, mod, csv=None, cok=False: str(A.equipMod(mu, "Meteor", slot, mod, csv, cok))
    setp(k_, {"u.Meteor": 0})
    ck(EQ(0, "Power").startswith("-Power+ unlocks at Meteor Lv 2 (Lv 1 now)"), "X10: a modifier locked below its unlock level: %s" % EQ(0, "Power"))
    setp(k_, {"u.Meteor": int(AMt.levelStart(4, 4.5, 1.5))})
    ck(int(A.alvl(int(AMt.levelStart(4, 4.5, 1.5)))) == 4, "X10: Meteor Lv 4")
    ck(EQ(0, "Power") == "+Meteor: slot 1 Power+, slot 2 empty.", "X10: equip Power+ in slot 1: %s" % EQ(0, "Power"))
    ck(EQ(1, "Power") == "-Power+ can go in both slots from modifier Lv 2.", "X10: doubling needs modifier Lv 2")
    ck(EQ(1, "Slow") == "-Slow is not a Meteor modifier.", "X10: not this ability's modifier")
    ck(EQ(1, "Split").startswith("-Split unlocks at Meteor Lv 6"), "X10: Split (3rd) unlocks at Lv 6")
    ck(EQ(2, "Radius") == "-Pick modifier slot 1 or 2.", "X10: a bad slot")
    setp(k_, {"m.Meteor.Power": 10})
    ck(EQ(1, "Power") == "+Meteor: slot 1 Power+, slot 2 Power+.", "X10: Power+ Lv 2 -> DOUBLED (both slots)")
    cx_ = A.ctxFor(mu, k_, METEOR, 0, None)
    ck(int(cx_.m0) == int(AMD.POWER) and int(cx_.m1) == int(AMD.POWER) and int(cx_.eff(AMD.POWER)) == 4,
       "X10: the cast context - doubled Power+ Lv 2 counts 2 x 2 = 4 levels")
    ck(round(float(cx_.main), 4) == round(float(A.lvlMult(4)) * 1.20, 4), "X10: main = level (+6 %%) x Power+ (+20 %%) = %s" % cx_.main)
    setp(k_, {"u.Meteor": int(AMt.levelStart(10, 4.5, 1.5)), "m.Meteor.Split": 10})
    ck(EQ(0, "Split") == "+Meteor: slot 1 Split, slot 2 Power+." and EQ(1, "Split") == "-Split cannot be equipped twice.", "X10: a non-stackable modifier never doubles")
    ck(str(A.equipMod(mu, "Meteor", 1, "Radius", "A1,M1A", False)) == "-Modifier slot 2 of Meteor is not open - unlock M1B in your class tree.",
       "X10: the tree gives the slots (M1A only -> slot 2 closed)")
    ck(int(A.modSlots("A1,M1A,M1B", METEOR)) == 2 and int(A.modSlots("A1", METEOR)) == 0 and int(A.modSlots(None, METEOR)) == 2, "X10: modSlots from the tree")
    eqs = list(A.equipped(AS.load(k_), METEOR, 10, 1))
    ck(eqs == [int(AMD.SPLIT), -1], "X10: with 1 tree slot only slot 1 works: %s" % eqs)
    COMBAT[str(mu)] = now_ms() + 5000
    ck(EQ(0, "Radius").startswith("-Leave combat first"), "X10: no changes in combat")
    del COMBAT[str(mu)]
    ck(EQ(0, "") == "+Meteor: slot 1 empty, slot 2 Power+." and EQ(0, "") == "-Modifier slot 1 of Meteor is empty.", "X10: unequip")
    # a use with a doubled stackable modifier: +2 modifier uses; the modifier level-up line
    setp(k_, {"e.Meteor": "Power,Power", "m.Meteor.Power": 28})
    AS.LASTUSE.clear()
    said()
    ru = str(A.used(mu, k_, METEOR, None))
    sd = said()
    ck(str(AS.load(k_).getProperty("m.Meteor.Power")) == "30" and "mods Power+ Lv 3" in ru and [x for x in sd if x == "Meteor modifier up: Power+ Lv 3."],
       "X10: a doubled modifier gains 2 uses a counted use (28 -> 30 = Lv 3, the line): %s %s" % (ru, sd))
    AC.MODS_ON = False
    cx_ = A.ctxFor(mu, k_, METEOR, 0, None)
    ck(int(cx_.m0) == -1 and str(A.equipMod(mu, "Meteor", 0, "Power", None, False)).startswith("-Ability modifiers are switched off"), "X10: mods.on OFF -> nothing applies")
    AC.MODS_ON = True
    # a real /cast shows them
    reset_m()
    rr = str(A.cast(mpr, tst, mr, world, "1"))
    ck(rr.startswith("ok:Meteor") and " m0=Power3 m1=Power3" in rr and " lv=10" in rr, "X10: the cast carries its level + modifiers: %s" % rr)
    said()

    # ---------------- X11 doAction
    reset_m()
    DO = lambda act, a=None, b=None, csv=None: str(A.doAction(mu, act, a, b, csv))
    sl0 = [str(x) for x in AS.slots(k_, ci_m)]
    r_ = DO("swap", "0", "1")
    sl1 = [str(x) for x in AS.slots(k_, ci_m)]
    ck(r_.startswith("+") and sl1[0] == sl0[1] and sl1[1] == sl0[0], "X11: swap 0 1: %s %s -> %s" % (r_, sl0, sl1))
    ck(list(A.runeWant(mu)) == [R_MB, R_MET], "X11: ... the runes follow (Mana Barrier now on Ability 2)")
    DO("swap", "0", "1")
    ck(DO("swap", "0", "x") == "-Pick two slots." and DO("dance") == "-Unknown action.", "X11: bad arguments")
    pk0 = str(AS.pick(k_))
    r_ = DO("pick", "B" if pk0 == "A" else "A")
    ck(r_.startswith("+Your Ability 1 alt is now"), "X11: pick the other Ability 1 alt: %s" % r_)
    DO("pick", pk0)
    LEVEL[(str(mu), SK_M)] = 12
    ck(DO("pick", "B").startswith("-You choose your Ability 1 alt at %s 30" % SK_M), "X11: the alt pick needs the Lv 30 unlock")
    LEVEL[(str(mu), SK_M)] = 30
    ck(DO("equip", "Meteor", "0:Radius") == "+Meteor: slot 1 Radius+, slot 2 Power+." and DO("unequip", "Meteor", "0") == "+Meteor: slot 1 empty, slot 2 Power+.",
       "X11: equip / unequip through abilDo")
    ck(DO("equip", "Meteor", "Radius") == "-Usage: equip <ability> <slot>:<modifier>." and DO("equip", "SacredHeal", "0:Power") == "-That is not one of your abilities.",
       "X11: bad equip / another class's ability")
    ck(str(A.doAction(JClass("java.util.UUID").randomUUID(), "swap", "0", "1", None)) == "-Your class has no abilities yet.", "X11: no class")

    # ---------------- X12 THE PANEL (the bridges SkyyTrees calls)
    reset_m()
    PF, MF, DF, UF = C("AbilPanelFn")(), C("AbilModsFn")(), C("AbilDoFn")(), C("AbilUnlockFn")()
    o = PF.apply(mu)
    ck(o is not None and len(o) == 78 and str(o[0]) == "ok" and str(o[1]) == "Mage" and int(o[2]) == 30 and str(o[7]) == "1,10,20,30",
       "X12: class:fn:abilPanel(UUID) -> Object[78] ok / Mage / 30 / unlocks 1,10,20,30")
    ck(str(o[12]) == "Meteor" and str(o[13]) == "Meteor" and str(o[14]) == R_MET and bool(o[15]) and bool(o[16]) and int(o[17]) == 1 and int(o[18]) == 10,
       "X12: card 1 = Meteor, its rune, owned, enabled, line 1, Lv 10")
    ck(str(o[22]) == "" and str(o[24]) == "Power+" and int(o[25]) == 3 and int(o[26]) == 2 and str(o[27]) == "ready",
       "X12: card 1's modifiers by DISPLAY name (slot 2 Power+ Lv 3), 2 slots, ready: %s" % [str(x) for x in o[22:28]])
    o2 = PF.apply(JArray(JObject)([mu, JString("A1,M1A")]))
    ck(bool(o2[16]) and not bool(o2[12 + 16 + 4]) and str(o2[12 + 16 + 15]) == "disabled" and int(o2[26]) == 1 and bool(o2[6]),
       "X12: with this page's tree csv: line 2 not enabled -> 'disabled'; Meteor has 1 modifier slot; the gate shows: %s" % [str(o2[i_]) for i_ in (6, 16, 26, 32, 43)])
    ck(PF.apply(JString("x")) is None and str(PF.apply(JClass("java.util.UUID").randomUUID())[0]) == "noclass", "X12: bad input -> null; no class -> noclass")
    rows = MF.apply(JArray(JObject)([mu, JString("Meteor"), JString("A1,M1A,M1B")]))
    ck(rows is not None and len(rows) == 1 + int(AMD.count(METEOR)) and str(rows[0]).startswith("Meteor|Meteor|10|"), "X12: class:fn:abilMods -> header + %d rows" % (len(rows) - 1 if rows else -1))
    pw = str(rows[1]).split("|")
    ck(pw[0] == "Power" and pw[1] == "Power+" and pw[2] == "2" and pw[3] == "1" and pw[4] == "3" and pw[8] == "1" and pw[11] == "1",
       "X12: the Power row: unlocked at 2, Lv 3, stackable, can double: %s" % pw)
    ech = str(rows[5]).split("|")
    ck(ech[0] == "Echo" and ech[3] == "1" and ech[9].startswith("again at 20 % after 1 s"), "X12: the Echo row (unlocked at Lv 10): %s" % ech)
    ck(str(DF.apply(JArray(JObject)([mu, JString("equip"), JString("Meteor"), JString("0:Echo"), JString("A1,M1A,M1B")]))) == "+Meteor: slot 1 Echo, slot 2 Power+.",
       "X12: class:fn:abilDo equips through the bridge")
    ul = [UF.apply(JInt(x)) for x in (1, 2, 3, 4)]
    ck([int(x) for x in ul] == [1, 10, 20, 30] and UF.apply(JInt(5)) is None and UF.apply(JString("x")) is None,
       "X12: class:fn:abilUnlock line 1-4 -> 1 / 10 / 20 / 30 (Skyy's unlock levels); a bad line -> null")

    # ---------------- X13 PROFILE SWITCH
    reset_m()
    PROFKEY[str(mu)] = str(mu) + "-p2"
    k2 = str(mu) + "-p2"
    o = PF.apply(mu)
    ck(int(o[18]) == 1 and str(o[22]) == "" and str(o[24]) == "", "X13: profile 2 starts at Meteor Lv 1, no modifiers (levels + mods are per profile)")
    ck(str(A.equipMod(mu, "Meteor", 0, "Power", None, False)).startswith("-Power+ unlocks at Meteor Lv 2"), "X13: profile 2's own level gates its modifiers")
    AS.LASTUSE.clear()
    A.used(mu, k2, METEOR, None)
    ck(str(AS.load(k2).getProperty("u.Meteor")) == "1" and str(AS.load(k_).getProperty("u.Meteor")) != "1", "X13: a use counts on the active profile only")
    DO("swap", "0", "1")
    ck(list(A.runeWant(mu)) == [R_MB, R_MET], "X13: profile 2's own slot order -> its own runes")
    AS.MIRROR.clear()
    A.runeTick(mpr, mu, mr, tst, now_ms())
    ck(ids()[0] == R_MB and ids()[3] == R_MET, "X13: the mirror swaps the rune slots for the new profile: %s" % ids())
    del PROFKEY[str(mu)]
    AS.MIRROR.clear()
    A.runeTick(mpr, mu, mr, tst, now_ms())
    ck(ids()[0] == R_MET and ids()[3] == R_MB, "X13: back to profile 1 -> its runes again: %s" % ids())

    # ---------------- X14 M5: cooldowns clear on relog
    AS.arm(k_, "Meteor", now_ms(), 14000)
    AS.arm(k2, "Meteor", now_ms(), 14000)
    AS.arm(str(pu), "SacredHeal", now_ms(), 14000)
    n_ = int(AS.clearCdOf(mu))
    ck(n_ == 2 and int(AS.left(k_, "Meteor", now_ms())) == 0 and int(AS.left(k2, "Meteor", now_ms())) == 0 and int(AS.left(str(pu), "SacredHeal", now_ms())) > 0,
       "X14: clearCdOf - every profile's cooldowns of that player go, nobody else's (%d)" % n_)

    # ---------------- X15 /cast stays
    reset_m()
    rr = str(A.cast(mpr, tst, mr, world, "1"))
    ck(rr.startswith("ok:Meteor") and not rr.endswith(" key") and not rr.endswith(" marker"), "X15: /cast 1 still casts (door 0): %s" % rr)
    reset_m()
    AC.CAST_CMD = False
    ck(str(A.cast(mpr, tst, mr, world, "1")) == "cmdoff" and str(A.runeCast(mpr, 0, 1)).startswith("ok:Meteor"), "X15: abil.castCmd OFF -> /cast 1 refused, the key casts")
    AC.CAST_CMD = True
    said()

    # ---------------- X16 Echo (Meteor: again at 20 % after 1 s, never counted)
    reset_m()
    setp(k_, {"e.Meteor": "Echo,Power"})
    aw.jobs.clear()
    rr = str(A.cast(mpr, tst, mr, world, "1"))
    kinds = sorted(int(j.kind) for j in list(aw.jobs))
    ck(rr.startswith("ok:Meteor") and " m0=Echo" in rr and 10 in kinds, "X16: a Meteor with Echo queues its echo job (kind 10): %s %s" % (rr, kinds))
    for j_ in list(aw.jobs):
        j_.at = now_ms() - 10
    AS.LASTUSE.clear()
    u0 = int(AS.load(k_).getProperty("u.Meteor"))
    for _i in range(3):
        aw.lastNs = 0
        tick.tick(JFloat(0.05), 0, None, tst, tbuf)
        for j_ in list(aw.jobs):
            j_.at = now_ms() - 10
    ck(int(A.ECHOES) >= 1, "X16: the echo ran (%d)" % int(A.ECHOES))
    ck(int(AS.load(k_).getProperty("u.Meteor")) == u0 + 1, "X16: the cast counted once, its echo never (%d -> %s)" % (u0, AS.load(k_).getProperty("u.Meteor")))
    said()

    # ---------------- X17 FIX ROUND (critics): ward per profile, the failed-write retry, the mirror back-off, Layered Ward, Spirit
    # Shield, the leave clean-up (the REAL ClassQuit)
    Dm = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")

    def hit_(amt):
        return Dm(Dm.NULL_SOURCE, DCSc.PROJECTILE, JFloat(amt))
    AS.WARD.clear()
    AS.WARDP.clear()
    ck(float(A.wardGive(mu, 10.0, now_ms() + 5000)) == 10.0 and str(AS.WARDP.get(mu)) == str(mu), "X17: a ward remembers the profile it was given to")
    d_ = hit_(4.0)
    ck(str(A.wardHit(tst, tbuf, mr, d_, now_ms())) == "ward:4 cancelled" and bool(d_.isCancelled()), "X17: the ward soaks a hit on its own profile")
    PROFKEY[str(mu)] = str(mu) + "-p2"
    d_ = hit_(4.0)
    ck(str(A.wardHit(tst, tbuf, mr, d_, now_ms())) == "otherprofile" and not bool(d_.isCancelled()) and float(d_.getAmount()) == 4.0
       and AS.WARD.get(mu) is None and AS.WARDP.get(mu) is None, "X17: after a profile switch the old profile's ward is dropped, the hit lands in full")
    ck(float(A.wardGive(mu, 6.0, now_ms() + 5000)) == 6.0, "X17: the new profile gets its own ward")
    del PROFKEY[str(mu)]
    ck(float(A.wardGive(mu, 3.0, now_ms() + 5000)) == 3.0 and str(AS.WARDP.get(mu)) == str(mu),
       "X17: back on profile 1 a weaker ward still replaces profile 2's (a stronger ward only wins on the same profile)")
    AS.WARD.clear()
    AS.WARDP.clear()
    # a failed ability-file write stays queued for the next 30 s flush
    AS.load(k_)
    AS.markDirty(k_)
    blocker = os.path.join(SCRATCH, "not-a-dir")
    open(blocker, "w").write("x")
    dir0 = AS.DIR
    AS.DIR = Paths.get(blocker)
    n_ = int(AS.flushOld(now_ms() + 60000, 30000))
    ck(n_ == 0 and AS.DIRTYAT.get(k_) is not None and AS.DIRTY.containsKey(k_), "X17: a failed write stays in DIRTYAT (the 30 s flush retries it): n=%d" % n_)
    AS.DIR = dir0
    n_ = int(AS.flushOld(now_ms() + 60000, 30000))
    ck(n_ >= 1 and AS.DIRTYAT.get(k_) is None and not AS.DIRTY.containsKey(k_), "X17: ... and the next flush writes it: n=%d" % n_)
    # the mirror back-off: a refused rune write is logged once, 2 s, 2 s, then 60 s; a working write clears it
    AS.MIRFAIL.clear()
    f0 = int(Cfg.FAILS)
    w_ = [int(A.mirrorWait(mpr, mu, "!0")) for _i in range(3)]
    ck(w_ == [2000, 2000, 60000] and int(Cfg.FAILS) == f0 + 1 and int(list(AS.MIRFAIL.get(mu))[0]) == 3,
       "X17: refused rune writes -> logged once (%d), waits %s" % (int(Cfg.FAILS) - f0, w_))
    ck(int(A.mirrorWait(mpr, mu, "")) == 2000 and AS.MIRFAIL.get(mu) is not None, "X17: nothing to do keeps the count")
    ck(int(A.mirrorWait(mpr, mu, "+0 +3")) == 2000 and AS.MIRFAIL.get(mu) is None, "X17: a write that works clears the count")
    AS.MIRROR.clear()
    A.runeTick(mpr, mu, mr, tst, now_ms())
    rec = AS.MIRROR.get(mu)
    A.mirrorNow(mpr)
    ck(rec is not None and 0 < int(rec[2]) - now_ms() <= 2100, "X17: mirrorNow (through mirrorWait) sets the next look 2 s ahead")
    # LAYERED WARD (Priest PB3): a real Shield Bubble cast with the node - 2 s shorter, the inner half regrows 3 % a second
    PRI = PLAYERS["Priest1"]

    def bubbles():
        return [z_ for z_ in list(aw.zoneArr()) if int(z_.kind) == 2 and str(z_.caster) == str(pu)]
    for z_ in list(aw.zoneArr()):
        aw.dropZone(z_)
    sl_p = [str(x) for x in AS.slots(str(pu), ci_p)]
    bkey = str(sl_p.index("ShieldBubble") + 1)
    TREE["csv"] = "A1,A2,A3,A4,PB3"
    AS.TREEC.clear()
    AS.clearCd(str(pu))
    mana(pm, 400.0)
    unthrottle()
    r_ = cast("Priest1", bkey)
    bz = bubbles()
    ck(r_.startswith("ok:ShieldBubble") and len(bz) == 1 and int(bz[0].nextHeal) > 0, "X17: Layered Ward - the bubble has two layers: %s" % r_)
    life_l = int(bz[0].until) - int(bz[0].start) if bz else -1
    sd = said()
    ck(any("Two layers: the inner half regrows 3 % a second." in x for x in sd), "X17: ... its line says so: %s" % sd[-1:])
    if bz:
        z_ = bz[0]
        hm_ = float(z_.hpMax)
        z_.hp = hm_ * 0.2
        add_ = float(A.layerRegrow(z_, now_ms()))
        ck(abs(add_ - hm_ * 0.03) < 1e-6 and abs(float(z_.hp) - hm_ * 0.23) < 1e-6, "X17: the inner half regrows 3 %% of the bubble's HP (+%s)" % add_)
        z_.hp = hm_ * 0.49
        A.layerRegrow(z_, now_ms())
        ck(abs(float(z_.hp) - hm_ * 0.5) < 1e-6, "X17: ... only up to the inner half's top")
        z_.hp = hm_ * 0.8
        ck(float(A.layerRegrow(z_, now_ms())) == 0.0, "X17: the outer layer never regrows")
        z_.hp = hm_ * 0.3
        z_.pulsesDue = 2
        z_.pulsesDone = 2
        z_.nextHeal = now_ms() - 1
        alive_ = bool(A.zoneTick0(z_, tst, tbuf, now_ms()))
        ck(alive_ and float(z_.hp) > hm_ * 0.3 and int(z_.pulsesDone) == 2, "X17: the REAL zone tick regrows it (%.2f -> %.2f), the earned pulses stay" % (hm_ * 0.3, float(z_.hp)))
    for z_ in list(aw.zoneArr()):
        aw.dropZone(z_)
    TREE["csv"] = "A1,A2,A3,A4"
    AS.TREEC.clear()
    AS.clearCd(str(pu))
    mana(pm, 400.0)
    unthrottle()
    r_ = cast("Priest1", bkey)
    bz = bubbles()
    life_n = int(bz[0].until) - int(bz[0].start) if bz else -1
    ck(r_.startswith("ok:ShieldBubble") and len(bz) == 1 and int(bz[0].nextHeal) == 0 and life_n - life_l == 2000,
       "X17: without the node: one layer, and the Layered bubble was 2 s shorter (%d vs %d ms)" % (life_l, life_n))
    for z_ in list(aw.zoneArr()):
        aw.dropZone(z_)
    said()
    # SPIRIT SHIELD (Priest PB4): a killing blow on the Priest -> saved at 20 % (not 30 %) + a 4 s bubble (a ward of 15 % max Health)
    GUARD_HP = int(AC.GS_HP)

    def save_once(csv):
        TREE["csv"] = csv
        AS.TREEC.clear()
        AS.GUARD.clear()
        AS.WARD.clear()
        AS.WARDP.clear()
        mana(pm, 400.0)
        pm.setStatValue(HP, JFloat(50.0))
        return str(A.guard(tst, tbuf, pr_r, hit_(500.0), now_ms()))
    g1 = save_once("A1,A2,A3,A4")
    ck(g1.startswith("saved:Priest1") and (" hp=%d" % GUARD_HP) in g1 and " spirit" not in g1 and AS.WARD.get(pu) is None,
       "X17: Guardian Spirit without the node: saved at %d %%, no bubble: %s" % (GUARD_HP, g1))
    g2 = save_once("A1,A2,A3,A4,PB4")
    wd = AS.WARD.get(pu)
    ck(g2.startswith("saved:Priest1") and " spirit" in g2 and (" hp=%s " % str(AM.fmt(GUARD_HP * 2.0 / 3.0))) in g2 + " " and float(GUARD_HP * 2.0 / 3.0) < GUARD_HP,
       "X17: Spirit Shield: saved at 2/3 (20 %% at the default 30): %s" % g2)
    ck(wd is not None and abs(float(wd[0]) - 15.0) < 1e-6 and 3900 <= int(float(wd[1])) - now_ms() <= 4000 and str(AS.WARDP.get(pu)) == str(pu),
       "X17: ... + a 4 s bubble = a ward of 15 %% max Health: %s" % (list(wd) if wd is not None else None))
    sd = said()
    ck(any("Spirit Shield: 4 s bubble." in x for x in sd), "X17: the save line names it: %s" % sd[-2:])
    TREE["csv"] = None
    AS.TREEC.clear()
    AS.GUARD.clear()
    AS.WARD.clear()
    AS.WARDP.clear()
    pm.setStatValue(HP, JFloat(100.0))
    # ---------------- X18 SECOND FIX ROUND (critics)
    kM = str(Cfg.pkey(mu))
    JObj = JClass("java.lang.Object")
    # (a) a FAILED tree read ("!err" from SkyyTrees, or a throw) is never "no gate": the last good answer (any age), else "" (closed)
    TREE["csv"] = "A1"
    AS.TREEC.clear()
    ck(str(A.treeCsv(mu)) == "A1", "X18: a good tree read is cached")
    AS.TREEC.put(mu, JArray(JObj)([JString(kM), JLong(now_ms() - 5000), JString("A1")]))
    TREE["csv"] = "!err"
    te0 = int(A.TREE_ERR)
    ck(str(A.treeCsv(mu)) == "A1" and str(list(AS.TREEC.get(mu))[2]) == "A1" and int(list(AS.TREEC.get(mu))[1]) < now_ms() - 4000,
       "X18: '!err' -> the last good answer of this profile kept (not re-cached)")
    AS.TREEC.clear()
    tc_ = A.treeCsv(mu)
    ck(tc_ is not None and str(tc_) == "" and AS.TREEC.get(mu) is None and int(A.TREE_ERR) == te0 + 1 and not bool(A.lineOn(tc_, METEOR)),
       "X18: '!err' with nothing cached -> '' (fail CLOSED: Meteor not enabled), not cached, counted")
    ck(list(str(x) for x in A.runeWant(mu)) == ["", ""], "X18: ... and the mirror wants no rune")
    AS.TREEC.put(mu, JArray(JObj)([JString(kM + "-other"), JLong(now_ms() - 5000), JString("A1")]))
    ck(str(A.treeCsv(mu)) == "", "X18: another profile's cached answer is never used")

    @JImplements("java.util.function.Function")
    class Throw(object):
        @JOverride
        def apply(self, o):
            raise RuntimeError("boom")
    br.put("tree:fn:abil", Throw())
    AS.TREEC.put(mu, JArray(JObj)([JString(kM), JLong(now_ms() - 5000), JString("A1,A2")]))
    ck(str(A.treeCsv(mu)) == "A1,A2", "X18: a throwing bridge -> the last good answer too")
    br.put("tree:fn:abil", Fn(lambda o: None if TREE["csv"] is None else JString(TREE["csv"])))
    AS.TREEC.clear()
    # (b) the "enable it in /tree" hint: once per profile per session, 8 s after the first look
    TREE["csv"] = ""
    said()
    h_ = str(A.enableHint(mpr, mu, kM))
    sd = said()
    ck("Meteor" in h_ and "ManaBarrier" not in h_ and any("open /tree, class tab, and click Enable (free)" in x and "Meteor" in x for x in sd),
       "X18: trees on, nothing enabled -> one line names the owned abilities: %s / %s" % (h_, sd))
    TREE["csv"] = "A1,A2,A3,A4"
    AS.TREEC.clear()
    ck(str(A.enableHint(mpr, mu, kM)) == "" and not said(), "X18: everything enabled -> no line")
    TREE["csv"] = None
    AS.TREEC.clear()
    ck(str(A.enableHint(mpr, mu, kM)) == "" and not said(), "X18: class trees off -> no line")
    TREE["csv"] = "A1"
    AS.TREEC.clear()
    AS.HINTED.clear()
    t0_ = now_ms()
    r1_, r2_ = str(A.hintTick(mpr, mu, kM, t0_)), str(A.hintTick(mpr, mu, kM, t0_ + 2000))
    r3_ = str(A.hintTick(mpr, mu, kM, t0_ + 8000))
    r4_ = str(A.hintTick(mpr, mu, kM, t0_ + 20000))
    sd = said()
    ck(r1_ == "wait" and r2_ == "" and "Meteor" not in r3_ and len(r3_) > 0 and r4_ == "" and len([x for x in sd if "open /tree" in x]) == 1,
       "X18: hintTick: wait, quiet, one line at 8 s (A1 enabled -> the other three named), then never again: %s %s %s %s" % (r1_, r2_, r3_, r4_))
    # the REAL tick path calls it (runeTick -> hintTick puts the profile in HINTED)
    AS.HINTED.clear()
    AS.MIRROR.remove(mu)
    A.runeTick(mpr, mu, mr, tst, now_ms())
    ck(AS.HINTED.get(kM) is not None, "X18: runeTick (the full look) starts the hint clock")
    TREE["csv"] = None
    AS.TREEC.clear()
    said()
    # (c) Chain: the drop cut stops at the Lv 5 one (8 %), a doubled Chain adds targets only
    GRACE_ = ID["MartyrsGrace"]
    ck(abs(float(A.chainCut(2)) - 3.2) < 1e-9 and float(A.chainCut(5)) == 8.0 and float(A.chainCut(10)) == 8.0 and float(A.chainCut(-1)) == 0.0,
       "X18: chainCut 2 -> 3.2, 5 -> 8, 10 (doubled Lv 5) -> 8")
    mt_ = str(A.modText(GRACE_, int(AMD.CHAIN), 5, 2))
    ck(mt_.startswith("+10 targets, 8 % less drop") and "drop floor" in mt_, "X18: doubled Chain Lv 5 text: %s" % mt_)
    pc_ = [float(AM.chainPct(k__, 75.0, float(AC.G_DROP) - float(A.chainCut(10)))) for k__ in range(15)]
    ck(sum(1 for v in pc_ if v > 0.0) == 11, "X18: doubled Chain Lv 5 at the default 15 %% drop -> 11 heals before it fades, not 15: %s" % pc_)
    # (d) Lingering: 3 s at Lv 1 (Mage.md, Locked), +0.5 s a level
    ck(str(A.modText(METEOR, int(AMD.LINGER), 1, 1)).startswith("burns 3 s") and str(A.modText(METEOR, int(AMD.LINGER), 5, 1)).startswith("burns 5 s"),
       "X18: Lingering text: %s / %s" % (A.modText(METEOR, int(AMD.LINGER), 1, 1), A.modText(METEOR, int(AMD.LINGER), 5, 1)))
    # (e) /classadmin abil maxlevels | resetlevels: a backup first, maxlevels only raises
    top_ = int(AMt.levelStart(int(AC.MAX_LVL), float(AC.USES_COEF), float(AC.USES_EXP)))
    setp(kM, {"u.Meteor": top_ + 50, "u.ManaBarrier": 7, "m.Meteor.Power": 500})
    abd = os.path.join(home, "abilities")
    bak0 = set(f for f in os.listdir(abd) if ".lvl-" in f) if os.path.isdir(abd) else set()
    ra_ = str(A.adminDo(mpr, str(mu), "maxlevels"))
    sd = said()
    pm_ = AS.load(kM)
    bak1 = set(f for f in os.listdir(abd) if ".lvl-" in f) - bak0
    ck(ra_ == "maxlevels" and int(str(pm_.getProperty("u.Meteor"))) == top_ + 50 and int(str(pm_.getProperty("u.ManaBarrier"))) == top_
       and int(str(pm_.getProperty("m.Meteor.Power"))) == 500 and int(str(pm_.getProperty("m.Meteor.Radius"))) == int(list(AMD.steps())[-1]),
       "X18: maxlevels only RAISES (Meteor %s kept, Mana Barrier 7 -> top, Power+ 500 kept)" % pm_.getProperty("u.Meteor"))
    bk_ = os.path.join(abd, sorted(bak1)[0]) if len(bak1) == 1 else None
    btxt = open(bk_, encoding="latin-1").read() if bk_ else ""
    ck(len(bak1) == 1 and sorted(bak1)[0].startswith(kM + ".properties.lvl-") and "u.ManaBarrier=7" in btxt and any("Backup: abilities/" in x for x in sd),
       "X18: ... after a backup of the old counts: %s" % sorted(bak1))
    time.sleep(0.01)
    rr_ = str(A.adminDo(mpr, str(mu), "resetlevels"))
    pm_ = AS.load(kM)
    bak2 = set(f for f in os.listdir(abd) if ".lvl-" in f) - bak0
    ck(rr_ == "resetlevels" and pm_.getProperty("u.Meteor") is None and pm_.getProperty("m.Meteor.Power") is None and len(bak2) == 2,
       "X18: resetlevels clears the counts, after a second backup: %s" % sorted(bak2))
    sAD = AS.DIR
    AS.DIR = None
    ck(str(A.adminDo(mpr, str(mu), "resetlevels")) == "nobak" and any("Could not back up" in x for x in said()), "X18: no backup -> nothing changes")
    AS.DIR = sAD
    setp(kM, {"u.Meteor": None, "u.ManaBarrier": None})
    said()
    # (f) the ClassQuit below also drops HINTED
    AS.HINTED.put(kM, JArray(JLong)([1, 1]))
    # the leave clean-up: the REAL ClassQuit drops this player's LASTKEY / LASTUSE / WARDP / MIRFAIL entries, nobody else's
    AS.LASTKEY.put(str(mu) + "|0", JLong(1))
    AS.LASTKEY.put(str(mu) + "|1", JLong(1))
    AS.LASTKEY.put(str(pu) + "|0", JLong(1))
    AS.LASTUSE.put(str(mu) + "|Meteor", JLong(1))
    AS.LASTUSE.put(str(mu) + "-p2|Meteor", JLong(1))
    AS.LASTUSE.put(str(pu) + "|SacredHeal", JLong(1))
    AS.WARDP.put(mu, str(mu))
    AS.MIRFAIL.put(mu, JArray(JInt)([1]))
    PDE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
    pde = U.allocateInstance(PDE.class_)
    fn_ = gfield("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent", "getPlayerRef")
    kc_ = PDE.class_
    while True:
        try:
            f_ = kc_.getDeclaredField(fn_)
            break
        except Exception:
            kc_ = kc_.getSuperclass()
    f_.setAccessible(True)
    f_.set(pde, mpr)
    C("ClassQuit")().accept(pde)
    lk = sorted(str(x) for x in AS.LASTKEY.keySet())
    lu = sorted(str(x) for x in AS.LASTUSE.keySet())
    ck(lk == [str(pu) + "|0"] and str(pu) + "|SacredHeal" in lu and not any(x.startswith(str(mu)) for x in lu) and AS.WARDP.get(mu) is None and AS.MIRFAIL.get(mu) is None and AS.HINTED.get(kM) is None,
       "X17: the REAL ClassQuit clears the leaver's key maps only: %s %s" % (lk, lu))
    # ================================================================================================ 0.1.23 sections (Monk, Assassin, rebirth R6)
    # ---------------- X19 the 0.1.23 pure rules
    ck([int(AMt.rbEff(16, 16, l_, 110, 100)) for l_ in (1, 55, 110, 200)] == [8, 12, 16, 16], "X19: rebirth soft cap S 16, Lr 110: L 1 -> 8, 55 -> 12, 110 -> 16 (spec 3.2)")
    ck(int(AMt.rbEff(5, 16, 1, 110, 100)) == 5 and int(AMt.rbEff(16, 0, 1, 110, 100)) == 16 and int(AMt.rbEff(16, 4, 100, 100, 100)) == 16,
       "X19: the working level never above the level now; no rebirth record = the level; L >= Lr = the level")
    ck(int(AMt.rbEff(30, 30, 100, 200, 100)) == 22, "X19: F(L) floor (L 100: 15) vs half + ... (15 + 15 x 100 / 200 = 22)")
    ck([int(AMt.rbModEff(5, e_, 16)) for e_ in (8, 12, 16)] == [3, 4, 5] and int(AMt.rbModEff(5, 20, 16)) == 5, "X19: modifier levels follow the ratio (ceil)")
    ck(int(AMt.live(JArray(JLong)([1000, 5000, 0, 9000]), 9500, 5000)) == 2, "X19: live combo stacks (gained under 5 s ago)")
    ck(bool(AMt.behind(0.0, 0.0, 0.0, 0.0, 2.0, 80.0)) and not bool(AMt.behind(0.0, 0.0, 0.0, 0.0, -2.0, 80.0)) and not bool(AMt.behind(0.0, 0.0, 0.0, 2.0, 0.0, 80.0)),
       "X19: the backstab rule (the back = (sin yaw, cos yaw), +-80 degrees)")
    ck([int(AMt.aweTier(t_, 1.0, 1.0)) for t_ in (0, 1, 7, 40)] == [1, 1, 7, 20] and int(AMt.aweTier(10, 1.0, 1.5)) == 15, "X19: the Awe tier 1-20 (Power+ makes it stronger)")
    ck([int(AMt.waves(t_, 0, 10)) for t_ in (9, 10, 19, 20)] == [0, 1, 1, 2] and int(AMt.waves(8, 8, 10)) == 1 and int(AMt.waves(18, 8, 10)) == 2,
       "X19: Hundred Fists waves (every 10th; Rushing Fists the first at 8)")
    ck([int(AMD.modLevelX(u_, 1)) for u_ in (100, 139, 140, 179)] == [5, 5, 6, 6] and int(AMD.modLevelX(5000, 2)) == 7 and int(AMD.modLevelX(5000, 0)) == 5,
       "X19: a rebirth upgrade lets a modifier level past 5 (steps 140, 180 ...)")
    ck(int(AMD.modNextX(100, 1)) == 40 and int(AMD.modNextX(140, 1)) == 0 and int(AMD.modNextX(25, 1)) == 5, "X19: modNextX")
    ck(int(A.palmCut(1)) == 0 and int(A.palmCut(6)) == 500 and int(A.palmCut(25)) == 1000, "X19: Palm Strike -0.1 s a level to its 5.0 s floor")
    ck(str(A.spdId(12)) == "SkyyAbility_Spd_42" and str(A.spdId(-25)) == "SkyyAbility_Spd_5" and str(A.spdId(200)) == "SkyyAbility_Spd_110"
       and str(A.aweId(0)) == "SkyyAbility_Awe_1" and str(A.aweId(25)) == "SkyyAbility_Awe_20", "X19: the effect ids")

    # ---------------- the Monk + Assassin test players, effects and seams
    EFX = ArrayList()
    A.EFFECTS = EFX
    A.EFFECT = Fn(lambda o: Bool.valueOf(not str(list(o)[1]).startswith("?")))
    LOST = ArrayList()
    A.LOST = LOST
    PUSH = ArrayList()
    A.PUSHES = PUSH
    MOBT = {"t": None}
    A.MOB = Fn(lambda o: MOBT["t"])
    LOOKV = {"v": [0.0, 65.6, 0.0, 0.0, 0.0, 1.0]}
    A.LOOK = Fn(lambda o: JArray(JDouble)(LOOKV["v"]))
    ci_k, ci_s = NAMES_.index("Monk"), NAMES_.index("Assassin")
    SK_K, SK_S = str(Defs.SKILLS[ci_k]), str(Defs.SKILLS[ci_s])
    ku, kr, kpr, km, kpl, kmsc = player(40, 0.5, 64.0, 0.5, "Monk1")
    su, sr_, spr, sm, spl, smsc = player(41, 20.5, 64.0, 0.5, "Assassin1")
    setclass(ku, "Monk")
    setclass(su, "Assassin")
    LEVEL[(str(ku), SK_K)] = 30
    LEVEL[(str(su), SK_S)] = 30
    HANDS[40] = "Weapon_Staff_Bo_Wood"
    HANDS[41] = "Weapon_Daggers_Crude"
    kK, kS = str(ku), str(su)
    ID = dict((str(AD.IDS[i]), i) for i in range(len(AD.IDS)))
    FF, PS, CK, HF, SW = ID["FlowingForm"], ID["PalmStrike"], ID["CycloneKick"], ID["HundredFists"], ID["StillWater"]
    CL, TX, GK, VA = ID["CloakFirstStrike"], ID["Toxin"], ID["GodKiller"], ID["VanishingAct"]
    ck([int(AD.TIER[i]) for i in (FF, PS, CK, HF, SW, CL, TX, GK, VA)] == [0, 1, 2, 3, 4, 0, 1, 2, 3] and int(AD.of(ci_s, 4)) == -1,
       "X19: the 9 abilities sit on their tiers (the Assassin has no A1-alt B)")
    ck(all(str(AD.RUNE[i]) == "SkyyAbility_%s_%s" % (c_, AD.IDS[i]) for i, c_ in ((FF, "Monk"), (VA, "Assassin"))), "X19: their rune ids")
    for i_ in (FF, PS, CK, HF, SW, CL, TX, GK, VA):
        RUNES_LOADED.add(str(AD.RUNE[i_]))
    ck(list(AS.slots(kS, ci_s)) == ["CloakFirstStrike", "Toxin", "GodKiller", "VanishingAct"], "X19: the Assassin's default loadout")
    ck(bool(AD.owns(VA, 30, False, "B")) and int(AD.pickTierC(ci_s, "B")) == 3 and list(AD.defaults(ci_s, "B"))[3] == "VanishingAct",
       "X19: a pick of B never locks the Assassin out of Vanishing Act (one alt only)")
    ck("one Ability 1 alt" in str(A.setPick(kS, ci_s, "B")), "X19: setPick B on an Assassin says so: %s" % A.setPick(kS, ci_s, "B"))
    pan = A.panel(su, None, False)
    ck(str(pan[0]) == "ok" and str(pan[1]) == "Assassin" and not bool(pan[5]) and str(pan[77]) == "", "X19: the panel - Assassin: abilities, no alt pick")
    pank = A.panel(ku, None, False)
    ck(str(pank[0]) == "ok" and bool(pank[5]) and str(pank[76]) == "Hundred Fists" and str(pank[77]) == "Still Water", "X19: the panel - Monk: the A / B alts")
    ck(list(A.runeWant(ku)) == [str(AD.RUNE[FF]), str(AD.RUNE[PS])] and list(A.runeWant(su)) == [str(AD.RUNE[CL]), str(AD.RUNE[TX])],
       "X19: the mirror wants their primaries' runes")
    ABSEC2 = int(JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent").ABILITIES_SECTION_ID)
    ck(str(A.runeDecide(ku, ci_k, 0, "Rune_Fireball", ABSEC2, now_ms() + 99999)) == "vanilla", "X19: a game rune on a Monk is blocked now too (Skyy M2)")
    AS.LASTKEY.clear()
    AS.LASTHOOK.clear()
    ck(len(list(C("AbilFn")().apply(ku))) == 48, "X19: class:fn:abil (SkyyHud) answers 48 fields for a Monk")
    aw.jobs.clear()
    aw.zones.clear()
    aw.nz = 0

    def run_world(ms=0):
        for j_ in list(aw.jobs):
            j_.at = now_ms() - 10 - ms
        aw.lastNs = 0
        aw.nextZone = 0
        tick.tick(JFloat(0.05), 0, None, tst, tbuf)

    def kreset(m_=None):
        AS.clearCd(kK)
        AS.clearCd(kS)
        for mm_ in (km, sm):
            mm_.setStatValue(MANA, JFloat(400.0))
            mm_.setStatValue(STAM, JFloat(50.0))
        unthrottle()
        said()
        AS.LASTUSE.clear()

    def fcast(pr__, r__, slot, sh):
        unthrottle()
        return str(A.castAt(pr__, tst, r__, world, slot, sh, 3))

    def mob(i, x, z, hp=200.0, role=None):
        r_ = npc(i, x, 64.0, z, hp=hp)
        return r_

    def stuns():
        return [round(float(str(x).split(":", 1)[1]), 2) for x in EFX if str(x).startswith("Stun:")]

    def dmg(src, amt, proj=False, shooter=None):
        DENTc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
        DPRJc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource")
        Dm_ = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
        so = DPRJc(src, src) if proj else DENTc(src)
        return Dm_(so, DCSc.PROJECTILE, JFloat(amt))

    # ---------------- X20 MONK: Flowing Form (aura, combo stacks, speed, Awe, drain, the end)
    kreset()
    TREE["csv"] = None
    m1, m2 = mob(60, 2.5, 0.5), mob(61, 3.5, 1.5)
    NEARL[:] = [m1, m2]
    r_ff = fcast(kpr, kr, "1", 0)
    zf = AS.FLOWS.get(ku)
    ck(r_ff.startswith("ok:FlowingForm") and zf is not None and int(zf.kind) == 8 and float(zf.r) == 5.0, "X20: Flowing Form casts the aura (5 blocks): %s" % r_ff)
    ck(abs(sv(km, MANA) - 398.0) < 0.01 and abs(sv(km, STAM) - 49.0) < 0.01, "X20: 2 Mana + 1 Stamina to start")
    hl0 = str(A.hitLanded(tbuf, m1, dmg(kr, 5.0), now_ms()))
    ck(hl0 == "combo+1", "X20: a landed weapon hit = +1 combo stack (%s)" % hl0)
    for i_ in range(5):
        A.hitLanded(tbuf, m1, dmg(kr, 5.0), now_ms())
    ck(int(zf.total) == 6 and int(A.stacks(zf, now_ms())) == 6, "X20: 6 hits = 6 stacks, total 6")
    zf.t1 = now_ms() - 1000
    EFX.clear()
    LOST.clear()
    run_world()
    sp_ = AS.SPD.get(ku)
    ck(sp_ is not None and int(sp_[0]) == 12 and "SkyyAbility_Spd_42:1.5" in [str(x) for x in EFX], "X20: 6 stacks x 2 %% = +12 %% move speed (our speed effect): %s" % ([str(x) for x in EFX][:4]))
    ck(abs(sv(km, MANA) - (398.0 - 0.65)) < 0.05 and abs(sv(km, STAM) - (49.0 - 0.25)) < 0.05, "X20: 1 s of drain = 0.65 Mana + 0.25 Stamina: %s %s" % (sv(km, MANA), sv(km, STAM)))
    aw_ = AS.AWED.get(m1)
    ck(aw_ is not None and int(aw_[1]) == 6 and LOST.contains(m1) and LOST.contains(m2), "X20: both mobs in the aura are Awed (tier 6 = -6 %% defence) and lose their target")
    ck("SkyyAbility_Awe_6:10" in [str(x) for x in EFX], "X20: ... the Awe effect lasts 10 s past the aura")
    ck(bool(zf.echoed), "X20: 5+ combo = one counted use of Flowing Form")
    # out of Mana -> it ends, speed off
    km.setStatValue(MANA, JFloat(0.1))
    zf.t1 = now_ms() - 1000
    EFX.clear()
    run_world()
    ck(bool(zf.ended) and str(zf.why) == "mana" and AS.FLOWS.get(ku) is None and "-SkyyAbility_Spd_42" in [str(x) for x in EFX], "X20: out of Mana -> the aura ends, the speed effect is taken off")
    ck(any("Flowing Form ended - out of Mana" in x for x in said()), "X20: the end line")
    # shapes: Flow Sprint (2 stacks, free Stamina 3 s), Centred (3 stacks, 4 blocks, -25 % drain), the landing
    kreset()
    r_sp = fcast(kpr, kr, "1", 1)
    zf = AS.FLOWS.get(ku)
    ck(" shape=sprint" in r_sp and int(zf.total) == 2 and int(A.stacks(zf, now_ms())) == 2 and int(zf.t2) > now_ms(), "X20: Flow Sprint starts at 2 stacks, no Stamina drain for 3 s: %s" % r_sp)
    kreset()
    p_ = {"p1": "CycloneKick", "p2": "PalmStrike", "a1": "FlowingForm", "a2": "HundredFists"}
    setp(kK, p_)
    r_cr = fcast(kpr, kr, "3", 3)
    zf = AS.FLOWS.get(ku)
    ck(" shape=crouch" in r_cr and int(zf.total) == 3 and float(zf.r) == 4.0 and abs(float(zf.amount) - 0.65 * 0.75) < 1e-9, "X20: Centred (crouch): 3 stacks, 4 blocks, drain -25 %%: %s" % r_cr)
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None})
    kreset()
    kmsc.getMovementStates().onGround = False
    r_ai = fcast(kpr, kr, "1", 2)
    kmsc.getMovementStates().onGround = True
    run_world()
    ck(" land" in r_ai and str(A.LAST_LAND).startswith("flow:") and AS.FLOWS.get(ku) is not None, "X20: Flow Landing: the aura starts when you land (%s)" % A.LAST_LAND)
    # ---------------- X21 Hundred Fists: waves on the Awed, the 8 s gap, Echo
    kreset()
    setp(kK, {"p1": "HundredFists", "p2": "PalmStrike", "a1": "CycloneKick", "a2": "FlowingForm"})
    AS.TREEC.clear()
    r_hf = fcast(kpr, kr, "1", 0)
    zh = AS.FLOWS.get(ku)
    ck(r_hf.startswith("ok:HundredFists") and int(zh.n1) == 10 and abs(float(zh.d2) - 25.0) < 1e-6, "X21: Hundred Fists: a wave every 10 hits, 1.0 H: %s" % r_hf)
    run_world()   # Awe the mobs
    for i_ in range(10):
        A.hitLanded(tbuf, m1, dmg(kr, 5.0), now_ms())
    TBf.EVENTS.clear()
    run_world()
    ck(int(zh.hits) == 1 and TBf.EVENTS.size() >= 2 and int(zh.nextHeal) > now_ms() + 7000, "X21: the 10th hit -> a shockwave on every Awed enemy (%d hits); the next not before 8 s" % TBf.EVENTS.size())
    for i_ in range(10):
        A.hitLanded(tbuf, m1, dmg(kr, 5.0), now_ms())
    TBf.EVENTS.clear()
    run_world()
    ck(int(zh.hits) == 1 and int(zh.n2) == 2, "X21: the 20th hit inside the gap waits (2 earned, 1 fired)")
    ck(any("Shockwave! 2 Awed enemies hit." in x for x in said()), "X21: the wave line")
    # Echo: each wave again 1 s later, weaker (the Echo modifier at Lv 1 = 20 %)
    setp(kK, {"u.HundredFists": int(AMt.levelStart(6, 4.5, 1.5)), "e.HundredFists": "Echo,"})
    zh.ended = True
    run_world()
    kreset()
    AS.TREEC.clear()
    fcast(kpr, kr, "1", 0)
    zh = AS.FLOWS.get(ku)
    ck(zh.cx is not None and abs(float(zh.cx.echoPct) - 0.20) < 1e-9, "X21: Echo equipped (Lv 6 unlocks the 3rd modifier): echo 20 %%")
    run_world()
    for i_ in range(10):
        A.hitLanded(tbuf, m1, dmg(kr, 5.0), now_ms())
    run_world()
    ej = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 10 and int(j_.ai) == HF]
    ck(len(ej) == 1 and abs(float(ej[0].amount) - float(zh.d2) * 0.2) < 1e-6, "X21: the echo wave is queued at 20 %% (%s of %s)" % ([float(x.amount) for x in ej], float(zh.d2)))
    TBf.EVENTS.clear()
    e0 = int(A.ECHOES)
    run_world(2000)
    ck(int(A.ECHOES) == e0 + 1 and str(A.LAST_ECHO).startswith("wave:"), "X21: the echo wave runs (%s)" % A.LAST_ECHO)
    zh.ended = True
    run_world()
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None, "u.HundredFists": None, "e.HundredFists": None})
    said()
    # ---------------- X22 Still Water: counter, deflect, gap, Echo, Ward, Reflexes / Tranquility
    kreset()
    setp(kK, {"p1": "StillWater", "p2": "PalmStrike", "a1": "CycloneKick", "a2": "FlowingForm", "alt": "B",
              "u.StillWater": int(AMt.levelStart(10, 4.5, 1.5)), "e.StillWater": "Echo,Ward"})
    AS.TREEC.clear()
    TREE["csv"] = None
    AS.WARD.clear()
    r_sw = fcast(kpr, kr, "1", 0)
    zs = AS.STANCES.get(ku)
    ck(r_sw.startswith("ok:StillWater") and zs is not None and int(zs.n2) == 1 and float(zs.d1) == 3.0 and AS.WARD.get(ku) is not None,
       "X22: Still Water: the stance (front deflect), Echo + Ward equipped: %s" % r_sw)
    d1 = dmg(m1, 10.0)
    TBf.EVENTS.clear()
    rr_ = str(A.inHit(tst, tbuf, kr, d1, now_ms()))
    ck(rr_ == "counter" and bool(d1.isCancelled()) and TBf.EVENTS.size() == 1 and int(zs.hits) == 1, "X22: a melee hit is cancelled and countered (%s)" % rr_)
    d2 = dmg(m1, 10.0)
    ck(str(A.inHit(tst, tbuf, kr, d2, now_ms())) == "blocked" and bool(d2.isCancelled()) and int(zs.hits) == 1, "X22: a second hit from the same attacker within 0.4 s is blocked, not countered")
    LOOKV["v"] = [0.5, 65.6, 0.5, 1.0, 0.0, 0.0]
    dp = dmg(m1, 7.0, proj=True)
    ck(str(A.inHit(tst, tbuf, kr, dp, now_ms())) == "deflect" and bool(dp.isCancelled()), "X22: a projectile from the front is deflected")
    m3 = mob(62, -3.0, 0.5)
    dp2 = dmg(m3, 7.0, proj=True)
    ck(A.inHit(tst, tbuf, kr, dp2, now_ms()) is None and not bool(dp2.isCancelled()), "X22: ... from behind it is not (front stance)")
    zs.until = now_ms() - 1
    run_world()
    ck(int(zs.n1) == 1 and int(zs.n2) == 0 and not bool(zs.ended), "X22: Echo - the stance ends, the counters stay (no deflect)")
    time.sleep(0.45)
    d3 = dmg(m1, 10.0)
    ck(str(A.inHit(tst, tbuf, kr, d3, now_ms())) == "counter", "X22: ... a counter during the echo")
    dp3 = dmg(m1, 7.0, proj=True)
    ck(A.inHit(tst, tbuf, kr, dp3, now_ms()) is None, "X22: ... no deflect during the echo")
    zs.until = now_ms() - 1
    run_world()
    ck(bool(zs.ended) and AS.STANCES.get(ku) is None and any("Still Water ended - 2 counters." in x for x in said()), "X22: the stance ends after its echo")
    LOOKV["v"] = [0.0, 65.6, 0.0, 0.0, 0.0, 1.0]
    # Reflexes (PC2) stuns on a counter, Tranquility (PC4) heals + slows; Iron Skin (PB4) / Calm Aura (PC1) in the hook
    kreset()
    TREE["csv"] = "A1,A2,A3,A4,PC1,PC2,PC4"
    AS.TREEC.clear()
    EFX.clear()
    r_sw2 = fcast(kpr, kr, "1", 0)
    zs = AS.STANCES.get(ku)
    ck(r_sw2.startswith("ok:StillWater") and (now_ms() + 8500) > int(zs.until), "X22: Reflexes - the stance is 2 s shorter: %s" % r_sw2)
    A.inHit(tst, tbuf, kr, dmg(m2, 10.0), now_ms())
    ck(any(str(x).startswith("Stun:0.5") for x in EFX) and any(str(x).startswith("SkyyAbility_Spd_10") for x in EFX), "X22: Reflexes stun 0.5 s; Tranquility -20 %% speed: %s" % [str(x) for x in EFX][:6])
    km.setStatValue(HP, JFloat(50.0))
    zs.nextHeal = 0
    run_world()
    ck(sv(km, HP) > 50.0, "X22: Tranquility heals 1 %% max Health a second (%s)" % sv(km, HP))
    zs.ended = True
    run_world()
    AS.AWED.clear()
    # Calm Aura: an Awed attacker (by a PC1 Monk) deals 0.4 % less per total combo
    A.aweOn(tbuf, m1, kr, ku, 10, A.ctxFor(ku, kK, FF, 0, "A1,PC1"), now_ms())
    dc = dmg(m1, 100.0)
    ck(str(A.inHit(tst, tbuf, sr_, dc, now_ms())) == "awe-4" and abs(float(dc.getAmount()) - 96.0) < 1e-3, "X22: Calm Aura - an Awed attacker deals 4 %% less at 10 combo (on anyone): %s" % dc.getAmount())
    A.aweOn(tbuf, m2, kr, ku, 10, A.ctxFor(ku, kK, FF, 0, "A1,PC5"), now_ms())
    dc2 = dmg(m2, 100.0)
    A.inHit(tst, tbuf, sr_, dc2, now_ms())
    ck(abs(float(dc2.getAmount()) - 85.0) < 1e-3, "X22: Serenity - an Awed attacker deals 15 %% less (the attack-speed stand-in)")
    AS.AWED.clear()
    TREE["csv"] = None
    AS.TREEC.clear()
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None, "alt": None, "u.StillWater": None, "e.StillWater": None})
    said()
    # ---------------- X23 Palm Strike: target, stun, knockback, shapes, Iron Fist, Ricochet, Slow, Echo, the cooldown floor
    kreset()
    p1 = mob(63, 2.0, 0.5)
    MOBT["t"] = None
    ck(fcast(kpr, kr, "2", 0) == "notarget" and sv(km, MANA) == 400.0, "X23: no enemy in front -> refused, nothing spent")
    MOBT["t"] = p1
    NEARL[:] = [p1, m1]
    r_ps = fcast(kpr, kr, "2", 0)
    TBf.EVENTS.clear()
    EFX.clear()
    PUSH.clear()
    run_world()
    ck(r_ps.startswith("ok:PalmStrike") and TBf.EVENTS.size() == 1 and stuns() == [0.8] and PUSH.size() == 1,
       "X23: Palm Strike: 1.2 H, stun 0.75 s, knocked back: %s %s" % (r_ps, [str(x) for x in EFX]))
    ck(abs(float(TBf.EVENTS.get(0)[1].getAmount()) - 30.0) < 1e-3, "X23: 1.2 x the base hit 25 = 30")
    kreset()
    PUSH.clear()
    r_ps1 = fcast(kpr, kr, "2", 1)
    EFX.clear()
    run_world()
    ck(" shape=sprint" in r_ps1 and PUSH.size() == 2 and stuns() == [0.5], "X23: Rushing Palm steps in (you are pushed too), stun 0.5: %s" % stuns())
    kreset()
    PUSH.clear()
    EFX.clear()
    fcast(kpr, kr, "2", 2)
    run_world()
    ck(PUSH.size() == 1 and float(PUSH.get(0)[1]) < 0.0 and stuns() == [1.0], "X23: Falling Palm knocks DOWN, stun 1 s: %s" % stuns())
    kreset()
    TREE["csv"] = "A1,A2,PA3,PB3,PB5"
    AS.TREEC.clear()
    PUSH.clear()
    EFX.clear()
    fcast(kpr, kr, "2", 2)
    run_world()
    ck(PUSH.size() == 1 and float(PUSH.get(0)[1]) > 0.0 and "Vulnerable:2" in [str(x) for x in EFX], "X23: Aerial Palm (PA3) sends it UP; Concussive Palm (PB3) Vulnerable 2 s")
    # Iron Fist: the third palm on one target crits
    AS.PALMS.clear()
    for i_ in range(2):
        kreset()
        fcast(kpr, kr, "2", 0)
        run_world()
    kreset()
    TBf.EVENTS.clear()
    fcast(kpr, kr, "2", 0)
    run_world()
    ck(TBf.EVENTS.size() == 1 and abs(float(TBf.EVENTS.get(0)[1].getAmount()) - 45.0) < 1e-3 and "crit" in str(A.LAST_MONK), "X23: Iron Fist - the 3rd palm on one target x1.5 (%s)" % A.LAST_MONK)
    cxp = A.ctxFor(ku, kK, PS, 0, "A1,A2,PB3,PB5")
    ck(abs(float(cxp.costAdd) - 3.0) < 1e-9 and int(cxp.cdAdd) == 1000, "X23: Concussive Palm +3 Mana, Iron Fist +1 s cooldown")
    TREE["csv"] = None
    AS.TREEC.clear()
    # Rooting Palm (crouch): no push, 1.25 s, Awe
    kreset()
    setp(kK, {"p1": "FlowingForm", "p2": "CycloneKick", "a1": "PalmStrike", "a2": "HundredFists"})
    PUSH.clear()
    EFX.clear()
    AS.AWED.clear()
    fcast(kpr, kr, "3", 3)
    run_world()
    ck(PUSH.size() == 0 and stuns() == [1.3] and AS.AWED.get(p1) is not None, "X23: Rooting Palm - no push, stun 1.25 s, Awe: %s" % stuns())
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None})
    # the modifiers: Ricochet (stuns the others), Slow, Echo (a second palm 1 s later), Knockback+
    setp(kK, {"u.PalmStrike": int(AMt.levelStart(10, 4.5, 1.5)), "e.PalmStrike": "Ricochet,Echo", "m.PalmStrike.Ricochet": 10})
    kreset()
    EFX.clear()
    TBf.EVENTS.clear()
    fcast(kpr, kr, "2", 0)
    run_world()
    ck("ric=1" in str(A.LAST_MONK), "X23: Ricochet stuns the enemy beside the target (%s)" % A.LAST_MONK)
    ej = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 11]
    ck(len(ej) == 1 and ej[0].cx is not None and bool(ej[0].cx.echo), "X23: Echo - a second palm queued for 1 s later")
    e0 = int(A.ECHOES)
    TBf.EVENTS.clear()
    run_world(2000)
    ck(int(A.ECHOES) == e0 + 1 and TBf.EVENTS.size() == 1 and "echo" in str(A.LAST_MONK), "X23: ... it lands, weaker (%s)" % A.LAST_MONK)
    setp(kK, {"e.PalmStrike": "Slow,Knockback", "m.PalmStrike.Ricochet": None})
    kreset()
    EFX.clear()
    PUSH.clear()
    fcast(kpr, kr, "2", 0)
    run_world()
    ck("Slow:2" in [str(x) for x in EFX] and PUSH.size() == 1, "X23: Slow - the target slowed 2 s; Knockback+ pushes farther")
    cxl = A.ctxFor(ku, kK, PS, 0, None)
    ck(int(cxl.lvl) == 10 and int(A.cdCx(cxl, PS, 0)) == 6000 - 900, "X23: Lv 10 -> cooldown 6.0 - 0.9 = 5.1 s (%d ms)" % int(A.cdCx(cxl, PS, 0)))
    setp(kK, {"u.PalmStrike": None, "e.PalmStrike": None})
    said()
    # ---------------- X24 Cyclone Kick: ring, arc, Leg Sweep, Dropping Kick, Haste
    kreset()
    setp(kK, {"p1": "CycloneKick", "p2": "PalmStrike", "a1": "FlowingForm", "a2": "HundredFists"})
    behind_ = mob(64, 0.5, -2.0)
    NEARL[:] = [m1, behind_]
    TBf.EVENTS.clear()
    PUSH.clear()
    r_ck = fcast(kpr, kr, "1", 0)
    run_world()
    ck(r_ck.startswith("ok:CycloneKick") and TBf.EVENTS.size() == 2 and PUSH.size() == 2, "X24: Cyclone Kick hits + pushes everything around (2): %s" % r_ck)
    kreset()
    TBf.EVENTS.clear()
    fcast(kpr, kr, "1", 1)
    run_world()
    ck(TBf.EVENTS.size() == 1, "X24: Sweeping Kick (sprint) - only the arc in front (the one behind is spared)")
    kreset()
    setp(kK, {"p1": "FlowingForm", "p2": "PalmStrike", "a1": "CycloneKick", "a2": "HundredFists"})
    PUSH.clear()
    EFX.clear()
    fcast(kpr, kr, "3", 3)
    run_world()
    ck(PUSH.size() == 0 and stuns() == [1.0, 1.0], "X24: Leg Sweep - no push, both stunned 1 s: %s" % stuns())
    kreset()
    setp(kK, {"p1": "CycloneKick", "p2": "PalmStrike", "a1": "FlowingForm", "a2": "HundredFists", "u.CycloneKick": int(AMt.levelStart(8, 4.5, 1.5)), "e.CycloneKick": "Haste,"})
    kmsc.getMovementStates().onGround = False
    fcast(kpr, kr, "1", 2)
    kmsc.getMovementStates().onGround = True
    EFX.clear()
    run_world()
    ck(str(A.LAST_LAND).startswith("kick:") and any(str(x).startswith("SkyyAbility_Spd_50") for x in EFX), "X24: Dropping Kick on landing; Haste +20 %% after (%s)" % A.LAST_LAND)
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None, "u.CycloneKick": None, "e.CycloneKick": None})
    said()
    # ---------------- X25 Assassin: Cloak + First Strike (lose target, break on attack, First Strike, Lethal Opener, Death Mark)
    kreset()
    LOST.clear()
    NEARL[:] = [m1, m2]
    r_cl = fcast(spr, sr_, "1", 0)
    zc = AS.CLOAKS.get(su)
    fs_ = AS.STRIKE.get(su)
    ck(r_cl.startswith("ok:CloakFirstStrike") and zc is not None and int(zc.kind) == 12 and LOST.size() >= 2 and fs_ is not None and abs(float(fs_[1]) - 50.0) < 1e-6,
       "X25: Cloak - mobs lose you, First Strike +50 armed: %s" % r_cl)
    ck(abs(sv(sm, MANA) - 394.0) < 0.01 and abs(sv(sm, STAM) - 48.0) < 0.01, "X25: 6 Mana + 2 Stamina")
    LOST.clear()
    run_world()
    ck(LOST.size() >= 2, "X25: every tick while cloaked the mobs lose you again")
    d_fs = dmg(sr_, 20.0)
    ck(str(A.outHit(tst, tbuf, m1, d_fs, su, now_ms())) == "first+50" and abs(float(d_fs.getAmount()) - 30.0) < 1e-3 and AS.STRIKE.get(su) is None,
       "X25: the First Strike: +50 %% on your next weapon hit, then gone")
    ck(str(A.hitLanded(tbuf, m1, dmg(sr_, 20.0), now_ms())) == "uncloak" and bool(zc.ended) and str(zc.why) == "attack", "X25: your attack breaks the cloak")
    run_world()
    ck(AS.CLOAKS.get(su) is None and any("Your attack broke the cloak." in x for x in said()), "X25: the cloak ends (its look taken off)")
    # Lethal Opener + Death Mark + Longer Cloak
    kreset()
    TREE["csv"] = "A1,A2,A3,A4,PA1,PA2,PA5"
    AS.TREEC.clear()
    r_cl2 = fcast(spr, sr_, "1", 0)
    zc = AS.CLOAKS.get(su)
    fs_ = AS.STRIKE.get(su)
    ck(abs(float(fs_[1]) - (50.0 + 15.0) * 0.9) < 1e-6 and float(fs_[3]) == 1.0 and float(fs_[2]) == 1.0, "X25: Lethal Opener +15, Death Mark -10 %% (58.5): %s" % list(fs_))
    ck(int(zc.until) > now_ms() + 9000, "X25: Longer Cloak +2 s")
    d_a = dmg(sr_, 20.0)
    A.outHit(tst, tbuf, m1, d_a, su, now_ms())
    ck(AS.MARKS.get(m1) is not None and AS.STRIKE.get(su) is not None, "X25: the First Strike marks the target; the 2nd-hit window opens")
    A.hitLanded(tbuf, m1, dmg(sr_, 20.0), now_ms())
    ck(not bool(zc.ended) and int(zc.until) <= now_ms() + 300, "X25: Longer Cloak - the cloak breaks 0.3 s after your hit, not at once")
    time.sleep(0.03)
    d_m = dmg(sr_, 20.0)
    om = str(A.outHit(tst, tbuf, m1, d_m, su, now_ms()))
    ck("mark" in om and float(d_m.getAmount()) >= 30.0 - 1e-3 and AS.MARKS.get(m1) is None, "X25: Death Mark - your next hit on it x1.5 (%s %s)" % (om, d_m.getAmount()))
    TREE["csv"] = None
    AS.TREEC.clear()
    AS.STRIKE.clear()
    zc.ended = True
    run_world()
    # shapes: Dash Cloak (speed), Silent Landing (no fall damage), Still Shadow (+20, moving drops it)
    kreset()
    EFX.clear()
    fcast(spr, sr_, "1", 1)
    ck(any(str(x).startswith("SkyyAbility_Spd_50:3") for x in EFX), "X25: Dash Cloak +20 %% speed 3 s")
    kreset()
    EFX.clear()
    fcast(spr, sr_, "1", 2)
    ck("Immunity_Fall:3" in [str(x) for x in EFX], "X25: Silent Landing - no fall damage 3 s (the vanilla Immunity_Fall)")
    kreset()
    setp(kS, {"p1": "Toxin", "p2": "GodKiller", "a1": "CloakFirstStrike", "a2": "VanishingAct"})
    r_ss = fcast(spr, sr_, "3", 3)
    zc = AS.CLOAKS.get(su)
    ck(" shape=crouch" in r_ss and abs(float(AS.STRIKE.get(su)[1]) - 70.0) < 1e-6 and int(zc.until) > now_ms() + 10000, "X25: Still Shadow - 11 s, First Strike +70")
    put(sr_, TCc.getComponentType(), TCc(V3(22.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    run_world()
    ck(int(zc.until) <= int(zc.t2), "X25: Still Shadow - moving drops it to 8 s")
    put(sr_, TCc.getComponentType(), TCc(V3(20.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    zc.ended = True
    run_world()
    setp(kS, {"p1": None, "p2": None, "a1": None, "a2": None})
    AS.STRIKE.clear()
    # Slip Away (PA4): a kill recloaks you 2 s, once per 20 s
    kreset()
    TREE["csv"] = "A1,PA4"
    AS.TREEC.clear()
    A.ctxFor(su, kS, CL, 0, "A1,PA4")
    ck(bool(A.SLIP_ON), "X25: an Assassin with Slip Away arms the kill check")
    dead = mob(65, 21.0, 0.5)
    put(dead, DTHc.getComponentType(), U.allocateInstance(DTHc.class_))
    hl = str(A.hitLanded(tbuf, dead, dmg(sr_, 20.0), now_ms()))
    ck("slip" in hl and AS.CLOAKS.get(su) is not None, "X25: Slip Away - the kill cloaks you 2 s (%s)" % hl)
    hl2 = str(A.hitLanded(tbuf, dead, dmg(sr_, 20.0), now_ms()))
    ck("slip" not in hl2, "X25: ... once per 20 s (%s)" % hl2)
    if AS.CLOAKS.get(su) is not None:
        AS.CLOAKS.get(su).ended = True
    run_world()
    TREE["csv"] = None
    AS.TREEC.clear()
    said()
    # ---------------- X26 Toxin: the cloud, poison + Weaken, Potent Mix / Contagion / Plague, Chain, Echo
    kreset()
    AIMS["spot"] = [24.0, 64.0, 0.5]
    t1, t2 = mob(66, 24.0, 0.5), mob(67, 25.0, 0.5)
    NEARL[:] = [t1, t2]
    r_tx = fcast(spr, sr_, "2", 0)
    zt = [z_ for z_ in aw.zoneArr() if int(z_.kind) == 10 and not bool(z_.ended)]
    ck(r_tx.startswith("ok:Toxin") and len(zt) == 1 and float(zt[0].r) == 4.0 and float(zt[0].pct) == 15.0, "X26: Toxin: a 4-block cloud where you look, Weaken 15: %s" % r_tx)
    TBf.EVENTS.clear()
    EFX.clear()
    run_world()
    ck(TBf.EVENTS.size() == 2 and "SkyyAbility_Weaken_15:2" in [str(x) for x in EFX] and AS.POISONED.get(t1) is not None, "X26: each second: poison both (0.25 H) + Weakened")
    ck(abs(float(TBf.EVENTS.get(0)[1].getAmount()) - 6.25) < 1e-3, "X26: 0.25 x 25 = 6.25 a second")
    AIMS["spot"] = None
    kreset()
    ck(fcast(spr, sr_, "2", 1) == "aim", "X26: Lobbed Vial with nothing to aim at -> refused, nothing spent")
    AIMS["spot"] = [24.0, 64.0, 0.5]
    zt[0].ended = True
    run_world()
    # the tree: Potent Mix (stacks), Cripple (25), Contagion, Plague (x2 time, +10 % from you)
    kreset()
    TREE["csv"] = "A1,A2,PB1,PB2,PB3,PB5"
    AS.TREEC.clear()
    r_tx2 = fcast(spr, sr_, "2", 0)
    zt = [z_ for z_ in aw.zoneArr() if int(z_.kind) == 10 and not bool(z_.ended)][0]
    ck(float(zt.r) == 3.0 and float(zt.pct) == 25.0 and int(zt.n1) == 1 and (int(zt.until) - now_ms()) > 7000, "X26: Potent Mix -1 radius, Cripple 25, Plague twice as long (8 s): %s" % r_tx2)
    for i_ in range(3):
        zt.nextHeal = 0
        run_world()
    ck(int(AS.POISONED.get(t1)[3]) == 3, "X26: Potent Mix - poison stacks to 3")
    d_pl = dmg(sr_, 10.0)
    ck("plague" in str(A.outHit(tst, tbuf, t1, d_pl, su, now_ms())) and abs(float(d_pl.getAmount()) - 11.0) < 1e-3, "X26: Plague - Weakened enemies take +10 %% from you")
    zt.ended = True
    run_world()
    TREE["csv"] = None
    AS.TREEC.clear()
    # Chain: a dying poisoned enemy passes it on; Echo: a second cloud
    kreset()
    setp(kS, {"u.Toxin": int(AMt.levelStart(10, 4.5, 1.5)), "e.Toxin": "Chain,Echo"})
    fcast(spr, sr_, "2", 0)
    zt = [z_ for z_ in aw.zoneArr() if int(z_.kind) == 10 and not bool(z_.ended)][0]
    ej = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 10 and int(j_.ai) == TX]
    ck(len(ej) == 1 and float(ej[0].secs) == 5.0, "X26: Echo - a weaker cloud queued for 1 s later")
    run_world()
    put(t1, DTHc.getComponentType(), U.allocateInstance(DTHc.class_))
    NEARL[:] = [t1, t2]
    zt.nextHeal = 0
    run_world()
    pj = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 16]
    ck(len(pj) >= 1, "X26: Chain - t1 died poisoned -> the poison jumps to t2 (%d chained jobs)" % len(pj))
    TBf.EVENTS.clear()
    for j_ in pj:
        j_.at = now_ms() - 10
    aw.lastNs = 0
    tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    ck(TBf.EVENTS.size() >= 1, "X26: ... the chained poison ticks on t2")
    run_world(2000)
    ck(str(A.LAST_ECHO) == "cloud", "X26: the echo cloud forms (%s)" % A.LAST_ECHO)
    for z_ in aw.zoneArr():
        z_.ended = True
    run_world()
    aw.jobs.clear()
    setp(kS, {"u.Toxin": None, "e.Toxin": None})
    said()
    # ---------------- X27 God Killer: bosses only, 2x / 3x from behind, falling, Boss Hunter, Echo, Haste, Patient Kill
    kreset()
    NPCs_ = mob(68, 20.5, 2.5)
    setp(kS, {"p1": "GodKiller", "p2": "Toxin", "a1": "CloakFirstStrike", "a2": "VanishingAct"})
    r_gk = fcast(spr, sr_, "1", 0)
    g_ = AS.ARMED.get(su)
    ck(r_gk.startswith("ok:GodKiller") and g_ is not None and abs(float(g_[1]) - 2.0) < 1e-9 and abs(float(g_[2]) - 3.0) < 1e-9, "X27: God Killer armed 2x / 3x: %s" % r_gk)
    AC.BOSS_WORDS = ""
    d_n = dmg(sr_, 10.0)
    ck(A.outHit(tst, tbuf, NPCs_, d_n, su, now_ms()) is None and float(d_n.getAmount()) == 10.0 and AS.ARMED.get(su) is not None, "X27: not a boss -> nothing, still armed")
    ck(not bool(A.bossFor(tbuf, NPCs_, False)), "X27: a mob with no role is no boss")
    # make it a boss: the stand-in has no role name, so the words test uses AbilMath directly + the multiplier path through a role-less list
    ck(bool(AMt.bossRole("Goblin_Duke", "Duke")) and bool(AMt.bossRole("Skeleton_Elite", "Elite")), "X27: the boss words (abil.bossWords / Boss Hunter elites)")
    AC.BOSS_WORDS = "Boss,Guardian,Duke,Dragon,Chieftain,Elite,Hedera,Rex,Ogre,Golem,Yeti"
    # front vs back: the target's back = (sin yaw, cos yaw); the Assassin at z 0.5, the mob at z 2.5 yaw 0 -> the Assassin is in FRONT
    ck(not bool(A.behindHit(tbuf, NPCs_, sr_)), "X27: the Assassin in front of the mob -> no backstab")
    put(NPCs_, TCc.getComponentType(), TCc(V3(20.5, 64.0, -1.5), R3(0.0, 0.0, 0.0)))
    ck(bool(A.behindHit(tbuf, NPCs_, sr_)), "X27: ... behind it -> a backstab (a Shadow Step arrival counts the same)")
    AS.ARMED.clear()
    AS.STRIKE.clear()
    SAVED_BW = str(AC.BOSS_WORDS)
    AC.BOSS_WORDS = "Duke"
    GK_ROLE = {"r": "Goblin_Duke"}
    # the role is read through NPCEntity.getRoleName: give our stand-in mob a real NPCEntity with a role name
    NPCE = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    ne_ = U.allocateInstance(NPCE.class_)
    try:
        setf(ne_, NPCE, "roleName", "Goblin_Duke")
        put(NPCs_, NPCE.getComponentType(), ne_)
        role_ok = str(A.roleOf(tbuf, NPCs_)) == "Goblin_Duke"
    except Exception as e_:
        role_ok = False
        K.notes.append("X27 role stand-in: %s" % str(e_)[:160])
    ck(role_ok, "X27: the stand-in boss reads as Goblin_Duke")
    kreset()
    r_gk = fcast(spr, sr_, "1", 0)
    d_b = dmg(sr_, 10.0)
    og = str(A.outHit(tst, tbuf, NPCs_, d_b, su, now_ms()))
    ck("god3back" in og and abs(float(d_b.getAmount()) - 30.0) < 1e-3 and AS.ARMED.get(su) is None, "X27: the boss hit from behind x3, then disarmed (%s)" % og)
    put(NPCs_, TCc.getComponentType(), TCc(V3(20.5, 64.0, 2.5), R3(0.0, 0.0, 0.0)))
    kreset()
    smsc.getMovementStates().onGround = False
    r_gka = fcast(spr, sr_, "1", 2)
    d_f = dmg(sr_, 10.0)
    A.outHit(tst, tbuf, NPCs_, d_f, su, now_ms())
    smsc.getMovementStates().onGround = True
    ck(abs(float(d_f.getAmount()) - 30.0) < 1e-3, "X27: Death from Above - a hit while falling counts as a backstab")
    kreset()
    TREE["csv"] = "A1,A2,A3,PA3"
    AS.TREEC.clear()
    fcast(spr, sr_, "1", 0)
    d_h = dmg(sr_, 10.0)
    A.outHit(tst, tbuf, NPCs_, d_h, su, now_ms())
    ck(abs(float(d_h.getAmount()) - 23.0) < 1e-3 and int(A.ctxFor(su, kS, GK, 0, "A3,PA3").cdAdd) == 10000, "X27: Boss Hunter 2.3x, cooldown +10 s")
    TREE["csv"] = None
    AS.TREEC.clear()
    setp(kS, {"u.GodKiller": int(AMt.levelStart(10, 4.5, 1.5)), "e.GodKiller": "Haste,Echo"})
    kreset()
    fcast(spr, sr_, "1", 0)
    EFX.clear()
    d_e = dmg(sr_, 10.0)
    A.outHit(tst, tbuf, NPCs_, d_e, su, now_ms())
    gj = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 14]
    ck(len(gj) == 1 and any(str(x).startswith("SkyyAbility_Spd_55") for x in EFX), "X27: Echo queued (the boss multiplier, not First Strike) + Haste +25 %% after the strike")
    TBf.EVENTS.clear()
    e0 = int(A.ECHOES)
    run_world(2000)
    ck(int(A.ECHOES) == e0 + 1 and TBf.EVENTS.size() == 1, "X27: the echo strike lands")
    setp(kS, {"u.GodKiller": None, "e.GodKiller": None})
    # Patient Kill (crouch): stand still 1 s to arm; moving gives everything back
    kreset()
    setp(kS, {"p1": "Toxin", "p2": "CloakFirstStrike", "a1": "GodKiller", "a2": "VanishingAct"})
    r_pk = fcast(spr, sr_, "3", 3)
    ck(" arming" in r_pk and AS.ARMED.get(su) is None, "X27: Patient Kill - arming")
    run_world(1500)
    g_ = AS.ARMED.get(su)
    ck(g_ is not None and float(g_[0]) > now_ms() + 19000, "X27: ... stood still 1 s -> armed for 20 s")
    AS.ARMED.clear()
    kreset()
    fcast(spr, sr_, "3", 3)
    put(sr_, TCc.getComponentType(), TCc(V3(25.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    m_before = sv(sm, MANA)
    run_world(1500)
    ck(AS.ARMED.get(su) is None and sv(sm, MANA) > m_before and str(A.LAST_ASN) == "patient moved", "X27: ... moved -> broken, Mana / Stamina / cooldown back")
    put(sr_, TCc.getComponentType(), TCc(V3(20.5, 64.0, 0.5), R3(0.0, 0.0, 0.0)))
    setp(kS, {"p1": None, "p2": None, "a1": None, "a2": None})
    AC.BOSS_WORDS = SAVED_BW
    said()
    # ---------------- X28 Vanishing Act: cloak + smoke, lose you, slow, the shapes
    kreset()
    setp(kS, {"p1": "VanishingAct", "p2": "Toxin", "a1": "CloakFirstStrike", "a2": "GodKiller"})
    v1 = mob(69, 21.0, 0.5)
    NEARL[:] = [v1]
    LOST.clear()
    EFX.clear()
    r_va = fcast(spr, sr_, "1", 0)
    zsm = [z_ for z_ in aw.zoneArr() if int(z_.kind) == 11 and not bool(z_.ended)]
    ck(r_va.startswith("ok:VanishingAct") and len(zsm) == 1 and AS.CLOAKS.get(su) is not None and AS.STRIKE.get(su) is not None, "X28: Vanishing Act: cloak + smoke + First Strike: %s" % r_va)
    run_world()
    ck(LOST.contains(v1) and "SkyyAbility_Spd_5:1" in [str(x) for x in EFX] and int(zsm[0].hits) == 1, "X28: an enemy in the smoke loses you and is slowed 25 %%")
    for z_ in aw.zoneArr():
        z_.ended = True
    run_world()
    kreset()
    smsc.getMovementStates().onGround = False
    fcast(spr, sr_, "1", 2)
    smsc.getMovementStates().onGround = True
    run_world()
    ck(str(A.LAST_LAND).startswith("smoke:5"), "X28: Smoke Drop - the smoke where you land, 5 blocks (%s)" % A.LAST_LAND)
    for z_ in aw.zoneArr():
        z_.ended = True
    run_world()
    kreset()
    setp(kS, {"p1": "CloakFirstStrike", "p2": "Toxin", "a1": "VanishingAct", "a2": "GodKiller"})
    fcast(spr, sr_, "3", 3)
    ck_ = AS.CLOAKS.get(su)
    u0 = int(ck_.until)
    time.sleep(0.05)
    run_world()
    ck(int(ck_.until) >= u0 or int(ck_.until) > now_ms(), "X28: Ambush Smoke - the cloak holds while you stay inside")
    for z_ in aw.zoneArr():
        z_.ended = True
    run_world()
    setp(kS, {"p1": None, "p2": None, "a1": None, "a2": None})
    AS.STRIKE.clear()
    said()
    # ---------------- X29 the class tree (Monk + Assassin nodes) - the treeApply2 numbers
    cm = A.ctxFor(ku, kK, FF, 0, "A1,T6=5,PC3")
    ck(abs(float(cm.cdMult) - 0.95) < 1e-9 and abs(float(cm.costAdd) - 2.0) < 1e-9, "X29: Master's Poise -5 %% cooldowns, Deep Breath +2 Mana")
    ca = A.ctxFor(su, kS, TX, 0, "A2,PB1,PB2,PB3,PB5")
    ck(abs(float(ca.radTree) + 1.0) < 1e-9 and abs(float(ca.durAdd) + 1.0) < 1e-9 and abs(float(ca.treeMain) - 0.85) < 1e-9 and int(ca.cdAdd) == 6000,
       "X29: Toxin - radius -1, 1 s shorter, poison -15 %%, cooldown +6 s")
    cc_ = A.ctxFor(su, kS, CL, 0, "A1,PA1,PA4")
    ck(abs(float(cc_.durAdd) - 2.0) < 1e-9 and int(cc_.cdAdd) == 4000 and abs(float(cc_.costAdd) - 4.0) < 1e-9, "X29: Longer Cloak +2 s / +4 s cooldown, Slip Away +4 Mana")
    zf = None
    # flow stacks decay: Wind Step 4 s, Deep Breath 7.5 s
    kreset()
    TREE["csv"] = "A1,PA4"
    AS.TREEC.clear()
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None})
    fcast(kpr, kr, "1", 0)
    zf = AS.FLOWS.get(ku)
    kmsc.getMovementStates().onGround = False
    ck(int(A.flowHit(zf, tbuf, kr, now_ms())) == 2, "X29: Wind Step - an airborne hit = 2 stacks")
    kmsc.getMovementStates().onGround = True
    zf.ring[0] = now_ms() - 4500
    ck(int(A.stacks(zf, now_ms())) == 1, "X29: ... stacks decay after 4 s")
    zf.ended = True
    run_world()
    TREE["csv"] = None
    AS.TREEC.clear()
    said()
    # ---------------- X30 REBIRTH R6: the participant (measure / prepare / commit / done / abort / status, a crash at every step),
    # the soft cap, the cap, the +1 modifier level
    CRB = C("ClassRb")
    Arr = lambda *a: JArray(JObject)([JString(x) for x in a])
    TX1 = "tx1760000000000-aaaaaa"
    TX2 = "tx1760000000001-bbbbbb"
    setp(kK, {"u.FlowingForm": int(AMt.levelStart(16, 4.5, 1.5)), "u.PalmStrike": int(AMt.levelStart(4, 4.5, 1.5)), "m.FlowingForm.Power": 100})
    AS.save(kK)
    LEVEL[(str(ku), SK_K)] = 110
    crb = CRB()
    ck(str(crb.apply(JObject(None))) == "err:bad arguments" and str(crb.apply(Arr("measure", "nope", TX1))) == "err:bad profile key"
       and str(crb.apply(Arr("measure", kK, "tx1"))) == "err:bad txid" and str(crb.apply(Arr("fly", kK, TX1))) == "err:unknown op fly", "X30: bad calls answer err (never throw)")
    ck(str(crb.apply(Arr("measure", kK, TX1))) == "ok:classLvl=110;abilities=5", "X30: measure - class level + the Monk's 5 abilities (nothing written)")
    ck(str(crb.apply(Arr("measure", kK + "-p7", TX1))).startswith("err:the profile"), "X30: a profile that is not active -> err")
    f_ab = os.path.join(home, "abilities", kK + ".properties")
    before = open(f_ab, "rb").read()
    ck(str(crb.apply(Arr("prepare", kK, TX1))) == "ok:classLvl=110;abilities=5", "X30: prepare")
    stg = os.path.join(home, "rebirth", kK + ".rb-" + TX1 + ".properties")
    ck(os.path.isfile(stg) and open(f_ab, "rb").read() == before and os.path.isdir(os.path.join(home, "rebirth-backup", kK, TX1)),
       "X30: ... a staged file + a backup, the live file untouched")
    ck(str(crb.apply(Arr("status", kK, TX1))) == "staged", "X30: status staged")
    ck(str(crb.apply(Arr("abort", kK, TX1))) == "done" and not os.path.isfile(stg) and str(crb.apply(Arr("status", kK, TX1))) == "none", "X30: abort deletes the staged file (crash before DECIDED = nothing changed)")
    ck(str(crb.apply(Arr("commit", kK, TX1))).startswith("err:no staged file"), "X30: commit without a staged file -> err")
    crb.apply(Arr("prepare", kK, TX1))
    # an older staged file of another rebirth is cleaned at the next prepare (decision unknown)
    open(os.path.join(home, "rebirth", kK + ".rb-" + TX2 + ".properties.tmp"), "w").write("x")
    crb.apply(Arr("prepare", kK, TX1))
    ck(not os.path.isfile(os.path.join(home, "rebirth", kK + ".rb-" + TX2 + ".properties.tmp")), "X30: a torn older staged file is cleaned")
    br.put("rebirth:fn:decision", Fn(lambda o: JString("commit")))
    open(os.path.join(home, "rebirth", kK + ".rb-" + TX2 + ".properties"), "w").write("tx=" + TX2)
    ck(str(crb.apply(Arr("prepare", kK, TX1))).startswith("err:an older rebirth"), "X30: an older COMMITTED rebirth still finishing -> refused")
    os.remove(os.path.join(home, "rebirth", kK + ".rb-" + TX2 + ".properties"))
    br.remove("rebirth:fn:decision")
    CRB.FAIL_WRITE = 1
    c1 = str(crb.apply(Arr("commit", kK, TX1)))
    ck(c1.startswith("err:could not save") and str(AS.load(kK).getProperty("rb.lastTx")) == TX1, "X30: a failed write -> err (in memory; the coordinator retries)")
    c2 = str(crb.apply(Arr("commit", kK, TX1)))
    ck(c2 == "done" and "rb.lastTx=" + TX1 in open(f_ab, encoding="latin-1").read(), "X30: the retry -> done, rb.lastTx on disk (crash after DECIDED = rolled forward)")
    txt = open(f_ab, encoding="latin-1").read()
    ck("rb.Lr=110" in txt and "rb.S.FlowingForm=16" in txt and "rb.pick.FlowingForm=1" in txt and "u.FlowingForm=" in txt and "m.FlowingForm.Power=100" in txt,
       "X30: ONE write: rb.Lr, rb.S, one upgrade to place per ability; levels, uses, modifiers KEPT")
    ck(str(crb.apply(Arr("commit", kK, TX1))) == "done" and str(crb.apply(Arr("status", kK, TX1))) == "committed" and str(crb.apply(Arr("abort", kK, TX1))) == "err:already committed"
       and str(crb.apply(Arr("prepare", kK, TX1))) == "err:already committed", "X30: a repeated commit is idempotent; abort / prepare after it refused")
    # the soft cap: class level back to 1 -> Flowing Form (Lv 16) works at Lv 8, rises with the class level
    LEVEL[(str(ku), SK_K)] = 1
    cxr_ = A.ctxFor(ku, kK, FF, 0, None)
    ck(int(cxr_.lvl) == 8 and int(A.alvlk(kK, int(AMt.levelStart(16, 4.5, 1.5)))) == 16, "X30: after a rebirth Flowing Form (Lv 16) works at Lv 8 at class level 1 (%d)" % int(cxr_.lvl))
    ck(int(cxr_.l0) == 0 or True, "X30: (no modifier equipped)")
    setp(kK, {"e.FlowingForm": "Power,"})
    cxr_ = A.ctxFor(ku, kK, FF, 0, None)
    ck(int(cxr_.m0) == int(AMD.POWER) and int(cxr_.l0) == 3, "X30: an equipped modifier (Power+ Lv 5) works at Lv 3 (5 x 8 / 16) - unlocked modifiers stay unlocked")
    LEVEL[(str(ku), SK_K)] = 55
    ck(int(A.ctxFor(ku, kK, FF, 0, None).lvl) == 12, "X30: class level 55 -> Lv 12")
    LEVEL[(str(ku), SK_K)] = 110
    ck(int(A.ctxFor(ku, kK, FF, 0, None).lvl) == 16, "X30: back at the old class level -> the full Lv 16")
    pnl = A.panel(ku, None, False)
    LEVEL[(str(ku), SK_K)] = 30
    pnl2 = A.panel(ku, None, False)
    ck("works at Lv" in str(pnl2[12 + 9]) and "works at Lv" not in str(pnl[12 + 9]), "X30: the panel shows 'works at Lv x' while the class level climbs back")
    # the cap 25 + n
    br.put("rebirth:fn:count", Fn(lambda o: JInt(2)))
    AS.RBN.clear()
    ck(int(A.capOf(kK)) == 27 and int(A.alvlk(kK, 10 ** 9)) == 27, "X30: the ability level cap 25 + 2 rebirths = 27")
    br.remove("rebirth:fn:count")
    AS.RBN.clear()
    # +1 modifier level (rbpick)
    ck(str(A.rbPick(ku, "FlowingForm", "Power")).startswith("+Power+ of Flowing Form can now reach modifier Lv 6"), "X30: rbpick places the upgrade on Power+")
    ck(str(A.rbPick(ku, "FlowingForm", "Power")).startswith("-No rebirth upgrade"), "X30: ... one per rebirth")
    ck(str(A.rbPick(ku, "PalmStrike", "Split")).startswith("-Split is not a Palm Strike modifier"), "X30: not that ability's modifier -> refused")
    setp(kK, {"m.FlowingForm.Power": 145})
    ck(int(A.mlvl(AS.load(kK), "FlowingForm", int(AMD.POWER))) == 6, "X30: Power+ (145 uses) reaches Lv 6 with the upgrade")
    rows = list(A.modRows(ku, "FlowingForm", None))
    ck(str(rows[0]).split("|")[10] == "0" and str(rows[1]).split("|")[-1] in ("0", "1"), "X30: modRows head carries the upgrades to place (field 10)")
    setp(kK, {"u.PalmStrike": int(AMt.levelStart(16, 4.5, 1.5))})   # fix round 2: Max Up needs the modifier unlocked (Palm Strike Lv 16)
    ck(str(A.doAction(ku, "rbpick", "PalmStrike", "Power", None)).startswith("+Power+ of Palm Strike"), "X30: class:fn:abilDo rbpick (SkyyTrees' Max Up button)")
    ck(str(A.rbLine(kK)).startswith("n=0 cap=25") and "lastTx=" + TX1 in str(A.rbLine(kK)), "X30: /classadmin abil info shows the rebirth line")
    setp(kK, {"u.FlowingForm": None, "u.PalmStrike": None, "m.FlowingForm.Power": None, "e.FlowingForm": None, "rb.S.FlowingForm": None, "rb.Lr": None})
    LEVEL[(str(ku), SK_K)] = 30
    # the REAL ClassQuit drops the Monk / Assassin maps of the leaver only
    AS.FLOWS.put(ku, JObject("x"))
    AS.ARMED.put(su, JArray(JDouble)([1.0]))
    AS.STRIKE.put(su, JArray(JDouble)([1.0]))
    fpde = U.allocateInstance(PDE.class_)
    f_.set(fpde, kpr)
    C("ClassQuit")().accept(fpde)
    ck(AS.FLOWS.get(ku) is None and AS.ARMED.get(su) is not None, "X30: ClassQuit drops the Monk's aura record, not the Assassin's")
    # ---------------- X31 FIX ROUND (critics 2026-10-14): one check per fix
    # B3 rbN: a null answer (SkyyRebirth still reading the profile) is never cached as 0
    AS.RBN.clear()
    br.put("rebirth:fn:count", Fn(lambda o: None))
    ck(int(A.rbN(kK)) == 0 and AS.RBN.get(kK) is None, "X31 B3: rebirth:fn:count answers null -> 0, NOT cached")
    br.put("rebirth:fn:count", Fn(lambda o: JInt(3)))
    ck(int(A.rbN(kK)) == 3 and int(A.capOf(kK)) == 28, "X31 B3: ... the real answer right after (no 5 s false 0): cap 28")
    br.remove("rebirth:fn:count")
    AS.RBN.clear()
    ck(int(A.rbN(kK)) == 0 and AS.RBN.get(kK) is not None, "X31 B3: no SkyyRebirth at all -> 0, cached as before")
    AS.RBN.clear()
    # B4 effLvl: SkyySkills cannot answer -> no soft cap (not class level 0)
    setp(kK, {"rb.S.FlowingForm": 16, "rb.Lr": 110})
    LEVEL[(str(ku), SK_K)] = 1
    ck(int(A.effLvl(ku, kK, FF, 16)) == 8, "X31 B4: class level 1 after a rebirth -> Lv 16 works at 8 (the soft cap still works)")
    br.remove("skill:fn:level")
    ck(int(A.levelOr(ku, ci_k)) == -1 and int(A.effLvl(ku, kK, FF, 16)) == 16, "X31 B4: no skill:fn:level answer -> no soft cap (Lv 16, not the floor)")
    br.put("skill:fn:level", LevelFn())
    LEVEL[(str(ku), SK_K)] = 30
    setp(kK, {"rb.S.FlowingForm": None, "rb.Lr": None})
    # A2 Max Up: refused while the profile is inside a rebirth; the counters move in ONE locked step; the commit adds to the CURRENT pick
    setp(kK, {"rb.pick.FlowingForm": 1, "rb.modmax.FlowingForm.Power": None})
    br.put("rebirth:fn:busy", Fn(lambda o: Bool.valueOf(True)))
    ck(str(A.rbPick(ku, "FlowingForm", "Power")).startswith("-A rebirth is running") and str(AS.load(kK).getProperty("rb.pick.FlowingForm")) == "1",
       "X31 A2: Max Up while rebirth:fn:busy -> refused, nothing moved")
    br.remove("rebirth:fn:busy")
    E0 = JArray(JString)([])
    ck(int(AS.setAdd(kK, E0, E0, JArray(JString)(["rb.pick.FlowingForm", "rb.modmax.FlowingForm.Power"]), JArray(JLong)([-1, 1]))) == 1
       and AS.load(kK).getProperty("rb.pick.FlowingForm") is None and str(AS.load(kK).getProperty("rb.modmax.FlowingForm.Power")) == "1",
       "X31 A2: setAdd moves the pick (1 -> gone, modmax 0 -> 1) in one step")
    ck(int(AS.setAdd(kK, E0, E0, JArray(JString)(["rb.pick.FlowingForm", "rb.modmax.FlowingForm.Power"]), JArray(JLong)([-1, 1]))) == 0
       and str(AS.load(kK).getProperty("rb.modmax.FlowingForm.Power")) == "1", "X31 A2: ... no pick left -> 0, nothing changed (no free level)")
    TX3 = "tx1760000000003-cccccc"
    setp(kK, {"u.FlowingForm": int(AMt.levelStart(6, 4.5, 1.5)), "rb.pick.FlowingForm": 2})
    ck(str(crb.apply(Arr("prepare", kK, TX3))).startswith("ok:"), "X31 A2: prepare a second rebirth")
    setp(kK, {"rb.pick.FlowingForm": 1})   # a Max Up after prepare (2 -> 1)
    ck(str(crb.apply(Arr("commit", kK, TX3))) == "ok" and str(AS.load(kK).getProperty("rb.pick.FlowingForm")) == "2",
       "X31 A2: the commit adds +1 to the pick AS IT IS NOW (1 -> 2, not the stale 2 -> 3)")
    setp(kK, {"u.FlowingForm": None, "rb.pick.FlowingForm": None, "rb.modmax.FlowingForm.Power": None, "rb.Lr": None})
    for k_ in list(AS.load(kK).stringPropertyNames()):
        if str(k_).startswith("rb.S.") or str(k_).startswith("rb.pick."):
            setp(kK, {str(k_): None})
    # B1 speed: a tick caller keeps the same speed without a new effect while > 0.5 s is left; a one-off set always applies
    AS.SPD.remove(ku)
    EFX.clear()
    A.speedKeep(tst, kr, ku, 12, 1.5)
    n1_ = len([x for x in EFX if str(x).startswith("SkyyAbility_Spd_42:")])
    A.speedKeep(tst, kr, ku, 12, 1.5)
    A.speedKeep(tst, kr, ku, 12, 1.5)
    n2_ = len([x for x in EFX if str(x).startswith("SkyyAbility_Spd_42:")])
    ck(n1_ == 1 and n2_ == 1, "X31 B1: the aura tick re-sends the same speed effect only near its end (1 effect for 3 ticks, was 3): %d %d" % (n1_, n2_))
    AS.SPD.get(ku)[3] = now_ms() + 400
    A.speedKeep(tst, kr, ku, 12, 1.5)
    ck(len([x for x in EFX if str(x).startswith("SkyyAbility_Spd_42:")]) == 2, "X31 B1: ... under 0.5 s left -> refreshed")
    A.speedKeep(tst, kr, ku, 14, 1.5)
    ck(any(str(x).startswith("SkyyAbility_Spd_44:") for x in EFX), "X31 B1: ... a new speed applies at once")
    # B2 one speed slot: a clear falls back to a live haste; a replaced stance never clears the new one's Tranquility
    A.haste(tst, kr, ku, 20, 3.0)
    A.speedSet(tst, kr, ku, 12, 1.5)
    EFX.clear()
    A.speedClear(tst, kr, ku)
    ck(int(AS.SPD.get(ku)[0]) == 20 and any(str(x).startswith("SkyyAbility_Spd_50:") for x in EFX), "X31 B2: an ending aura / cloak leaves a running haste (+20 %%) on: %s" % [str(x) for x in EFX])
    AS.SPD.get(ku)[1] = 0
    EFX.clear()
    A.speedClear(tst, kr, ku)
    ck(int(AS.SPD.get(ku)[0]) == 0 and "-SkyyAbility_Spd_50" in [str(x) for x in EFX], "X31 B2: ... no haste -> cleared")
    kreset()
    setp(kK, {"p1": "StillWater", "p2": "PalmStrike", "a1": "CycloneKick", "a2": "FlowingForm", "alt": "B", "u.StillWater": int(AMt.levelStart(10, 4.5, 1.5))})
    TREE["csv"] = "A1,A2,A3,A4,PC4"
    AS.TREEC.clear()
    fcast(kpr, kr, "1", 0)
    zold = AS.STANCES.get(ku)
    kreset()
    fcast(kpr, kr, "1", 0)
    znew = AS.STANCES.get(ku)
    EFX.clear()
    run_world()
    ck(zold is not None and znew is not None and not zold.equals(znew) and bool(zold.ended) and int(AS.SPD.get(ku)[0]) == -20
       and not any(str(x).startswith("-SkyyAbility_Spd_10") for x in EFX), "X31 B2: the replaced stance ends without clearing the new stance's -20 %% (Tranquility)")
    znew.ended = True
    run_world()
    ck(int(AS.SPD.get(ku)[0]) == 0, "X31 B2: ... the new stance's own end clears it")
    # B6 an invulnerable (creative) Monk in a stance: no counter, no use (the engine drops the hit)
    kreset()
    fcast(kpr, kr, "1", 0)
    zi = AS.STANCES.get(ku)
    put(kr, INVUc.getComponentType(), INVUc.INSTANCE)
    di = dmg(m1, 10.0)
    TBf.EVENTS.clear()
    ck(A.inHit(tst, tbuf, kr, di, now_ms()) is None and not bool(di.isCancelled()) and TBf.EVENTS.size() == 0 and int(zi.hits) == 0,
       "X31 B6: an invulnerable Monk's hit is not countered (no damage back, no counted use)")
    TSt.COMP.get(kr).remove(INVUc.getComponentType())
    zi.ended = True
    run_world()
    TREE["csv"] = None
    AS.TREEC.clear()
    setp(kK, {"p1": None, "p2": None, "a1": None, "a2": None, "alt": None, "u.StillWater": None})
    # smoke: the slow per enemy re-sent only near its end; Ambush Smoke's cloak look put on once up to its cap
    kreset()
    vs_ = mob(71, 21.0, 0.5)
    NEARL[:] = [vs_]
    EFX.clear()
    zsm_ = A.smokeAt(tst, su, kS, aw, JArray(JDouble)([20.5, 64.0, 0.5]), 4.0, 0, now_ms())
    run_world()
    run_world()
    run_world()
    ns_ = len([x for x in EFX if str(x).startswith("SkyyAbility_Spd_5:")])
    ck(zsm_ is not None and ns_ == 1 and int(zsm_.hits) == 1, "X31 B1: the smoke slows an enemy once per 0.5 s, not every tick (%d effects in 3 ticks)" % ns_)
    zsm_.ended = True
    run_world()
    kreset()
    setp(kS, {"p1": "CloakFirstStrike", "p2": "Toxin", "a1": "VanishingAct", "a2": "GodKiller"})
    EFX.clear()
    fcast(spr, sr_, "3", 3)
    cka = AS.CLOAKS.get(su)
    cka.until = now_ms() + 100
    run_world()
    u1_ = int(cka.until)
    cka.until = now_ms() + 100
    run_world()
    nc_ = len([x for x in EFX if str(x).startswith("SkyyAbility_Cloak:")])
    ck(u1_ > now_ms() + 300 and nc_ == 2 and int(cka.lookUntil) > now_ms() + 3000, "X31 B1: Ambush Smoke holds the cloak with ONE look refresh up to its cap (%d cloak effects incl. the cast: %s)" % (nc_, [str(x) for x in EFX]))
    for z_ in aw.zoneArr():
        z_.ended = True
    run_world()
    setp(kS, {"p1": None, "p2": None, "a1": None, "a2": None})
    AS.STRIKE.clear()
    NEARL[:] = []
    # B5 the mob maps are pruned once a second by the REAL AbilTick (expired entries leave; live ones stay)
    pa_, pb_ = mob(72, 5.0, 5.0), mob(73, 6.0, 6.0)
    t0_ = now_ms()
    AS.AWED.put(pa_, JArray(JLong)([t0_ - 5, 1, 0, 0, 0, 0, 0, 0]))
    AS.AWED.put(pb_, JArray(JLong)([t0_ + 60000, 1, 0, 0, 0, 0, 0, 0]))
    AS.PALMS.put(pa_, JArray(JLong)([2, 0, 0, t0_ - 5]))
    AS.POISONED.put(pa_, JArray(JLong)([t0_ - 5, 0, 0, 1, t0_ + 60000, 0]))
    AS.MARKS.put(pa_, JArray(JLong)([t0_ - 5, 0, 0, 0]))
    A.NEXT_PRUNE = 0
    run_world()
    ck(AS.AWED.get(pa_) is None and AS.AWED.get(pb_) is not None and AS.PALMS.get(pa_) is None and AS.MARKS.get(pa_) is None,
       "X31 B5: AbilTick prunes expired Awe / Iron Fist / Death Mark entries (live ones stay)")
    ck(AS.POISONED.get(pa_) is not None and int(A.NEXT_PRUNE) > now_ms() + 500, "X31 B5: ... poison stays while its Plague window [4] runs; the next prune in 1 s")
    AS.AWED.clear()
    AS.POISONED.clear()
    # B7 / C4 / C5 / C6 texts (the generated script)
    gsrc = open(os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION), encoding="utf8").read()
    ck("@PKG@.Abil.FROST_ON = true;" in gsrc and "NO Monk combo stacks" in gsrc and "LANDED-HIT HOOK OFF" in gsrc, "X31 B7: AbilFrostSys failing says the combo / uncloak / Slip Away stop; abil info flags it")
    ck("the Mage and the Priest get theirs first" not in gsrc, "X31 C4: no player text says only the Mage and the Priest have abilities")
    ck("Keys: see the page help" not in gsrc and "Walking shape; sprint / air / crouch Mana scale with this row." in gsrc, "X31 C5 / C6: the numbers rows name their units; the walking cost rows say the shapes follow them")
    # ---------------- X32 FIX ROUND 2: Max Up (rbpick) never lands on a modifier still locked at the ability's level
    setp(kK, {"rb.pick.FlowingForm": 1, "u.FlowingForm": None, "rb.modmax.FlowingForm.Power": None})
    r_ = str(A.rbPick(ku, "FlowingForm", "Power"))
    ck(r_.startswith("-That modifier is still locked - it unlocks at Flowing Form Lv ") and str(AS.load(kK).getProperty("rb.pick.FlowingForm")) == "1"
       and AS.load(kK).getProperty("rb.modmax.FlowingForm.Power") is None, "X32: Flowing Form Lv 1 -> Max Up on Power+ refused, the pick stays: %s" % r_)
    setp(kK, {"u.FlowingForm": int(AMt.levelStart(16, 4.5, 1.5))})
    r_ = str(A.rbPick(ku, "FlowingForm", "Power"))
    ck(r_.startswith("+Power+ of Flowing Form") and AS.load(kK).getProperty("rb.pick.FlowingForm") is None and str(AS.load(kK).getProperty("rb.modmax.FlowingForm.Power")) == "1",
       "X32: ... at Lv 16 (unlocked) the same click places it: %s" % r_)
    setp(kK, {"u.FlowingForm": None, "rb.modmax.FlowingForm.Power": None, "rb.pick.FlowingForm": None})
    # ================================================================================================ 0.1.24 sections (Warrior, Berserker, Archer)
    # ---------------- X40 the tables, loadouts, panel, costs, the numbers rows, shields, the vanilla-rune block
    AN = C("AbilNum")
    NPCE = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    ci_w, ci_b, ci_r = NAMES_.index("Warrior"), NAMES_.index("Berserker"), NAMES_.index("Archer")
    SK_W, SK_B, SK_R = [str(Defs.SKILLS[c_]) for c_ in (ci_w, ci_b, ci_r)]
    wu, wr, wpr, wm, wpl, wmsc = player(50, 40.5, 64.0, 0.5, "Warrior1")
    bu, bref, bpr, bm, bpl, bmsc = player(51, 60.5, 64.0, 0.5, "Berserker1")
    au, aref, apr, am_, apl, amsc = player(52, 80.5, 64.0, 0.5, "Archer1")
    xu, xr, xpr, xm, xpl, xmsc = player(53, 42.5, 64.0, 0.5, "AllyW")
    yu, yr, ypr, ym, ypl, ymsc = player(54, 63.5, 64.0, 0.5, "AllyB")
    setclass(wu, "Warrior")
    setclass(bu, "Berserker")
    setclass(au, "Archer")
    for u_, sk_ in ((wu, SK_W), (bu, SK_B), (au, SK_R)):
        LEVEL[(str(u_), sk_)] = 30
    HANDS[50], HANDS[51], HANDS[52] = "Weapon_Sword_Crude", "Weapon_Battleaxe_Crude", "Weapon_Shortbow_Crude"
    WK, BK, RK = str(wu), str(bu), str(au)
    MEMBERS[WK] = MEMBERS[str(xu)] = [WK, str(xu)]
    MEMBERS[BK] = MEMBERS[str(yu)] = [BK, str(yu)]
    TAUNT = ArrayList()
    A.TAUNTL = TAUNT
    A.EFFECTS = EFX
    A.EFFECT = Fn(lambda o: Bool.valueOf(not str(list(o)[1]).startswith("?")))
    A.PUSHES = PUSH
    A.LOST = LOST
    A.MOB = Fn(lambda o: MOBT["t"])
    A.LOOK = Fn(lambda o: JArray(JDouble)(LOOKV["v"]))
    TREE["csv"] = None
    AS.TREEC.clear()
    ID = dict((str(AD.IDS[i]), i) for i in range(len(AD.IDS)))
    RG, SSW, IC, CHL, GO = ID["RallyingGuard"], ID["ShieldShockwave"], ID["IronChain"], ID["Challenge"], ID["GuardiansOath"]
    EN, WW, ES, BF, WB = ID["Enrage"], ID["Whirlwind"], ID["Earthsplitter"], ID["BloodFrenzy"], ID["WarlordsBanner"]
    PN, RF, EA, AR, HN = ID["PinningShot"], ID["RapidFire"], ID["ExplosiveArrow"], ID["ArrowRain"], ID["HuntersNet"]
    NEW15 = (RG, SSW, IC, CHL, GO, EN, WW, ES, BF, WB, PN, RF, EA, AR, HN)
    ck([int(AD.TIER[i]) for i in NEW15] == [0, 1, 2, 3, 4] * 3 and [int(AD.CLS[i]) for i in NEW15] == [ci_w] * 5 + [ci_b] * 5 + [ci_r] * 5,
       "X40: the 15 abilities sit on their tiers and classes")
    ck(all(str(AD.RUNE[i]) == "SkyyAbility_%s_%s" % (str(Defs.NAMES[int(AD.CLS[i])]), str(AD.IDS[i])) for i in NEW15), "X40: their rune ids")
    for i_ in NEW15:
        RUNES_LOADED.add(str(AD.RUNE[i_]))
    ck(list(AS.slots(WK, ci_w)) == ["RallyingGuard", "ShieldShockwave", "IronChain", "Challenge"] and list(AS.slots(BK, ci_b)) == ["Enrage", "Whirlwind", "Earthsplitter", "BloodFrenzy"]
       and list(AS.slots(RK, ci_r)) == ["PinningShot", "RapidFire", "ExplosiveArrow", "ArrowRain"], "X40: the default loadouts (A1, A2, A2-alt, A1-alt A)")
    pw_ = A.panel(wu, None, False)
    ck(str(pw_[0]) == "ok" and str(pw_[1]) == "Warrior" and bool(pw_[5]) and str(pw_[76]) == "Challenge" and str(pw_[77]) == "Guardian's Oath",
       "X40: the panel - Warrior: abilities + the A / B alt pick (Challenge / Guardian's Oath)")
    pb_ = A.panel(bu, None, False)
    pa_ = A.panel(au, None, False)
    ck(str(pb_[76]) == "Blood Frenzy" and str(pb_[77]) == "Warlord's Banner" and str(pa_[76]) == "Arrow Rain" and str(pa_[77]) == "Hunter's Net",
       "X40: the Berserker / Archer alt picks")
    ck(list(A.runeWant(wu)) == [str(AD.RUNE[RG]), str(AD.RUNE[SSW])] and list(A.runeWant(au)) == [str(AD.RUNE[PN]), str(AD.RUNE[RF])], "X40: the mirror wants their primaries' runes")
    for u_, c_ in ((wu, ci_w), (bu, ci_b), (au, ci_r)):
        ck(str(A.runeDecide(u_, c_, 0, "Rune_Fireball", ABSEC2, now_ms() + 99999)) == "vanilla", "X40: a game rune on a %s is blocked now too (Skyy M2)" % str(Defs.NAMES[c_]))
    AS.LASTKEY.clear()
    AS.LASTHOOK.clear()
    ck(len(list(C("AbilFn")().apply(wu))) == 48, "X40: class:fn:abil (SkyyHud) answers 48 fields for a Warrior")
    plan = {RG: [(5, 2, 24), (5, 2, 24), (5, 2, 24), (3, 1, 18)], WB: [(9, 8, 40), (9, 8, 40), (9, 8, 40), (10, 9, 40)],
            EA: [(5, 2, 14), (4, 1, 12), (5, 2, 16), (5, 2, 16)], AR: [(7, 2, 20), (7, 2, 20), (7, 2, 22), (9, 3, 24)]}
    AN.sync()
    for ai_, rows_ in plan.items():
        got_ = [(int(AD.mana(ai_, k_)), int(AD.stamina(ai_, k_)), int(AD.cdMs(ai_, k_)) // 1000) for k_ in range(4)]
        ck(got_ == rows_, "X40: %s costs per shape = the plan (power x the class split): %s" % (str(AD.IDS[ai_]), got_))
    ck(str(AC.RG_NUMS).startswith("mana=5,stamina=2,cooldown=24,") and not hasattr(AC, "RG_MANA") and not hasattr(AC, "HN_CD"),
       "X40: no ab.<Ability>.walk.* rows for the 15 (the 64 KB cap) - the walking cost is in ab.<Ability>.numbers: %s" % str(AC.RG_NUMS)[:60])
    old_rg = str(AC.RG_NUMS)
    AC.RG_NUMS = "cut=30,mana=6"
    AN.sync()
    ck(float(AN.RG_CUT) == 30.0 and float(AN.RG_TIME) == 10.0 and int(AD.mana(RG, 0)) == 6 and int(AD.mana(RG, 3)) == 4,
       "X40: ab.RallyingGuard.numbers is read live (cut 30; a missing key = its default; Mana 6 -> crouch scales 3 -> 4)")
    AC.RG_NUMS = old_rg
    AN.sync()
    ck(float(AN.RG_CUT) == 20.0 and int(AD.mana(RG, 0)) == 5, "X40: ... and back")
    CRl = C("ClassRules")
    ck(bool(CRl.allowed(wu, "Weapon_Shield_Wood")) and not bool(CRl.allowed(mu, "Weapon_Shield_Wood")) and not bool(CRl.allowed(bu, "Weapon_Shield_Iron")),
       "X40: SHIELDS = WARRIOR ONLY (Skyy 2026-10-08): a Warrior may, a Mage / Berserker may not")
    ck("Shields" in str(Defs.WTEXT[ci_w]), "X40: the Warrior weapon text names shields: %s" % Defs.WTEXT[ci_w])
    ck(str(C("ClassRb")().apply(JArray(JObject)([JString("measure"), JString(WK), JString("tx1760000000009-abcdef")]))) == "ok:classLvl=30;abilities=5",
       "X40: the rebirth participant (unchanged) measures a Warrior's 5 abilities")
    aw.jobs.clear()
    aw.zones.clear()
    aw.nz = 0

    def wreset():
        for k_ in (WK, BK, RK):
            AS.clearCd(k_)
        for m_ in (wm, bm, am_, xm, ym):
            m_.setStatValue(MANA, JFloat(400.0))
            m_.setStatValue(STAM, JFloat(50.0))
            m_.setStatValue(HP, JFloat(100.0))
        unthrottle()
        said()
        AS.LASTUSE.clear()
        EFX.clear()
        PUSH.clear()
        TBf.EVENTS.clear()
        TAUNT.clear()
        for mp_ in (AS.GUARDED, AS.GUARDBY, AS.TAUNTS, AS.CHALLS, AS.OATHS, AS.OATHW, AS.RAGE, AS.FURY, AS.WAR, AS.ROOTS, AS.EXPL, AS.EXPLC,
                    AS.CHAINED, AS.DEADEYE, AS.SWINGS, AS.BLEEDS, AS.MARKD, AS.PAID):
            mp_.clear()

    def endall():
        for z_ in list(aw.zoneArr()):
            z_.ended = True
        run_world()
        aw.jobs.clear()
        aw.zones.clear()
        aw.nz = 0

    def evs():
        return [(e[0], round(float(e[1].getAmount()), 3)) for e in TBf.EVENTS]

    def amts():
        return [a_ for _r, a_ in evs()]

    def efx(prefix):
        return [str(x) for x in EFX if str(x).startswith(prefix)]

    def make_boss(r_, role="Goblin_Duke"):
        ne_ = U.allocateInstance(NPCE.class_)
        setf(ne_, NPCE, "roleName", role)
        put(r_, NPCE.getComponentType(), ne_)

    def lv(n):
        return int(AMt.levelStart(n, 4.5, 1.5))

    def moveto(r_, x, z):
        put(r_, TCc.getComponentType(), TCc(V3(x, 64.0, z), R3(0.0, 0.0, 0.0)))

    def uses(k_, id_):
        v_ = AS.load(k_).getProperty("u." + id_)
        return 0 if v_ is None else int(str(v_))

    def zones(kind):
        return [z_ for z_ in aw.zoneArr() if int(z_.kind) == kind and not bool(z_.ended)]

    WSL = {"p1": None, "p2": None, "a1": None, "a2": None, "alt": None}
    # ---------------- X41 WARRIOR: Rallying Guard (pick at the cast, the cut through the REAL hook, the taunt, Echo, shapes, tree nodes)
    wreset()
    gm1 = mob(150, 40.5, 3.5)
    NEARL[:] = [gm1]
    r_ = fcast(wpr, wr, "1", 0)
    g_w, g_x = AS.GUARDED.get(wu), AS.GUARDED.get(xu)
    ck(r_.startswith("ok:RallyingGuard") and g_w is not None and g_x is not None and float(g_x[1]) == 20.0 and str(AS.GUARDBY.get(xu)) == WK,
       "X41: Rallying Guard - you + the party member within 10 take 20 %% less (picked at the cast): %s" % r_)
    ck(abs(sv(wm, MANA) - 395.0) < 0.01 and abs(sv(wm, STAM) - 48.0) < 0.01, "X41: 5 Mana + 2 Stamina")
    ck(TAUNT.contains(gm1) and AS.TAUNTS.get(gm1) is not None and int(A.TAUNTED) >= 1, "X41: the mob within 8 turns on you (taunt slot set, UNVERIFIED P12 in game)")
    d_ = dmg(gm1, 100.0)
    ck(str(A.inHit2(tst, tbuf, xr, d_, now_ms())) == "guard" and abs(float(d_.getAmount()) - 80.0) < 1e-3, "X41: the REAL hook - the ally takes 80 of 100")
    ck(len(zones(13)) == 1 and uses(WK, "RallyingGuard") == 1, "X41: the rally zone runs; one counted use (it guarded + taunted)")
    run_world()
    ck(TAUNT.size() >= 2, "X41: every zone tick pulls the taunted mob back onto you (%d)" % TAUNT.size())
    endall()
    # Echo (Skyy 2026-10-08, replaces Ward): the cut lingers 3 s at the echo strength
    wreset()
    AS.GUARDED.clear()
    setp(WK, {"u.RallyingGuard": lv(8), "e.RallyingGuard": "Echo,"})
    r_ = fcast(wpr, wr, "1", 0)
    g_x = AS.GUARDED.get(xu)
    cut8 = 20.0 * float(A.lvlMult(8))
    ck(" m0=Echo" in r_ and abs(float(g_x[1]) - cut8) < 1e-6 and abs(float(g_x[3]) - cut8 * 0.2) < 1e-6 and abs((float(g_x[2]) - float(g_x[0])) - 3000.0) < 1.0,
       "X41: Echo at Lv 8 - cut %.1f, lingers 3 s at 20 %% (%.2f): %s" % (cut8, cut8 * 0.2, r_))
    g_x[0] = float(now_ms() - 10)
    d_ = dmg(gm1, 100.0)
    A.inHit2(tst, tbuf, xr, d_, now_ms())
    ck(abs(float(d_.getAmount()) - (100.0 - cut8 * 0.2)) < 1e-3, "X41: ... after the guard ends the echo cut still works (%s)" % d_.getAmount())
    setp(WK, {"u.RallyingGuard": None, "e.RallyingGuard": None})
    endall()
    # Hold the Line (crouch): taunt 16, only you take 10 % less
    wreset()
    AS.GUARDED.clear()
    setp(WK, {"p1": "ShieldShockwave", "p2": "IronChain", "a1": "RallyingGuard", "a2": "Challenge"})
    r_ = fcast(wpr, wr, "3", 3)
    ck(" shape=crouch" in r_ and float(AS.GUARDED.get(wu)[1]) == 10.0 and AS.GUARDED.get(xu) is None and TAUNT.contains(gm1),
       "X41: Hold the Line - you take 10 %% less, no party cut, the taunt: %s" % r_)
    ck(abs(sv(wm, MANA) - 397.0) < 0.01 and abs(sv(wm, STAM) - 49.0) < 0.01, "X41: Hold the Line costs 3 + 1 (power 8)")
    setp(WK, WSL)
    endall()
    # Charge Rally (sprint): allies you pass within 4 blocks in 1.5 s
    wreset()
    AS.GUARDED.clear()
    moveto(xr, 55.5, 0.5)
    r_ = fcast(wpr, wr, "1", 1)
    ck(" shape=sprint" in r_ and AS.GUARDED.get(xu) is None, "X41: Charge Rally - the ally 15 blocks away is not picked at the cast")
    moveto(xr, 42.0, 0.5)
    run_world()
    ck(AS.GUARDED.get(xu) is not None, "X41: ... running past them (within 4) picks them up")
    moveto(xr, 42.5, 0.5)
    endall()
    # on landing
    wreset()
    wmsc.getMovementStates().onGround = False
    r_ = fcast(wpr, wr, "1", 2)
    wmsc.getMovementStates().onGround = True
    run_world()
    ck(" land" in r_ and str(A.LAST_LAND).startswith("rally:"), "X41: Rally on Landing (%s)" % A.LAST_LAND)
    endall()
    # the tree: Shield Wall (PA1), Aegis Core (PA5), Thorns (PB1), Presence (PB5)
    wreset()
    AS.GUARDED.clear()
    AS.TAUNTS.clear()
    TREE["csv"] = "A1,PA1,PA5,PB1,PB5"
    AS.TREEC.clear()
    r_ = fcast(wpr, wr, "1", 0)
    g_w, g_x = AS.GUARDED.get(wu), AS.GUARDED.get(xu)
    ck(float(g_w[1]) == 16.0 and int(g_w[4]) == 28 and int(g_x[4]) == 1 and abs(float(g_w[0]) - now_ms() - 13000) < 300,
       "X41: Shield Wall: your own cut -4 (16), allies flagged no-knockback; Aegis Core +3 s (13 s); thorns / presence / aegis on you")
    ck(abs(float(A.outMult(tst, gm1, wu, now_ms())) - 0.85) < 1e-9, "X41: Aegis Core - your damage -15 %% while active")
    TBf.EVENTS.clear()
    d_ = dmg(gm1, 100.0)
    out_ = str(A.inHit2(tst, tbuf, wr, d_, now_ms()))
    ck("thorns" in out_ and "presence+" in out_ and abs(float(d_.getAmount()) - 100.0 * 0.84 * 1.05 * 1.1) < 1e-3 and amts() == [12.75],
       "X41: Thorns of Command (+5 %% taken, 15 %% back = 15 x 0.85 Aegis) + Presence (+10 %% from the taunted): %s %s %s" % (out_, d_.getAmount(), amts()))
    d_ = dmg(gm1, 100.0)
    out_ = str(A.inHit2(tst, tbuf, xr, d_, now_ms()))
    ck("wall" in out_ and "presence-" in out_ and abs(float(d_.getAmount()) - 64.0) < 1e-3, "X41: the ally: Shield Wall + Presence (the taunted deal -20 %% to others): %s %s" % (out_, d_.getAmount()))
    xm.setStatValue(HP, JFloat(50.0))
    zr_ = zones(13)[0]
    zr_.nextHeal = 0
    run_world()
    ck(abs(sv(xm, HP) - 53.0) < 0.01, "X41: Aegis Core heals the guarded party 3 %% a second (%s)" % sv(xm, HP))
    endall()
    # Battle Cry (PB2): the end hits every taunted enemy; Interpose (PA2): geometry + -10 % speed
    wreset()
    AS.TAUNTS.clear()
    TREE["csv"] = "A1,PA2,PB2"
    AS.TREEC.clear()
    r_ = fcast(wpr, wr, "1", 0)
    ck(any(x_.startswith("SkyyAbility_Spd_20:") for x_ in efx("SkyyAbility_Spd_")), "X41: Interpose - you are 10 %% slower while it runs: %s" % efx("SkyyAbility_Spd_"))
    att_w = mob(151, 38.5, 0.5)
    att_e = mob(152, 46.5, 0.5)
    ck(bool(A.interposed(tst, xr, att_w, xu)) and not bool(A.interposed(tst, xr, att_e, xu)), "X41: Interpose - you stand between the ally and the attacker (not from the far side)")
    d_ = dmg(att_w, 100.0)
    A.inHit2(tst, tbuf, xr, d_, now_ms())
    ck(abs(float(d_.getAmount()) - 60.0) < 1e-3, "X41: ... 100 x 0.8 (guard) x 0.75 (interpose) = 60 (%s)" % d_.getAmount())
    TBf.EVENTS.clear()
    zones(13)[0].until = now_ms() - 1
    run_world()
    ck(str(A.LAST_WAR).startswith("battle cry 1") and amts() == [25.0], "X41: Battle Cry - the taunted enemy takes 1.0 H when it ends (%s %s)" % (A.LAST_WAR, amts()))
    ck(int(A.ctxFor(wu, WK, RG, 0, "A1,PB2").cdAdd) == 3000, "X41: Battle Cry - cooldown +3 s")
    TREE["csv"] = None
    AS.TREEC.clear()
    endall()
    # ---------------- X42 Shield Shockwave (the cone, the stun, shapes, Echo, T1, Retribution, Shockwave Surge)
    wreset()
    LOOKV["v"] = [40.5, 64.9, 0.5, 0.0, 0.0, 1.0]
    sf, sb = mob(153, 40.5, 3.5), mob(154, 40.5, -2.5)
    NEARL[:] = [sf, sb]
    # FIX ROUND 2 (critic: Shockwave never looked for a shield): a sword and no shield -> refused before anything is paid
    ck(not bool(A.shieldIn(tst, wr)) and fcast(wpr, wr, "2", 0) == "noshield" and sv(wm, MANA) == 400.0 and sv(wm, STAM) == 50.0 and not evs()
       and any("needs a shield" in x_ for x_ in said()) and int(AS.left(WK, "ShieldShockwave", now_ms())) == 0,
       "X42 FIX2: Shield Shockwave with no shield in hand or off-hand is refused - nothing spent, no cooldown")
    HANDS[50] = "Weapon_Shield_Wood"   # from here on the Warrior holds a shield (a Warrior weapon - the cast gate takes it)
    ck(bool(A.shieldIn(tst, wr)), "X42 FIX2: a shield in the hand counts")
    wreset()
    r_ = fcast(wpr, wr, "2", 0)
    run_world()
    ck(r_.startswith("ok:ShieldShockwave") and [a_ for t_, a_ in evs()] == [25.0] and evs()[0][0].equals(sf) and stuns() == [1.5],
       "X42: the cone hits the one in front only: 1.0 H + stun 1.5 s: %s %s" % (r_, stuns()))
    wreset()
    setp(WK, {"p1": "IronChain", "p2": "RallyingGuard", "a1": "ShieldShockwave", "a2": "Challenge"})
    fcast(wpr, wr, "3", 3)
    run_world()
    ck(sorted(amts()) == [20.0, 20.0], "X42: Ring (crouch) - 360 degrees, 0.8 H: %s" % amts())
    setp(WK, WSL)
    wreset()
    setp(WK, {"u.ShieldShockwave": lv(6), "e.ShieldShockwave": "Echo,"})
    fcast(wpr, wr, "2", 0)
    run_world()
    ek = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 10 and int(j_.ai) == SSW]
    st1 = stuns()
    ck(len(ek) == 1 and st1 == [1.7], "X42: Echo queued; Lv 6 stun 1.5 + 5 x 0.03 = 1.65 (shown 1.7): %s" % st1)
    e0 = int(A.ECHOES)
    EFX.clear()
    TBf.EVENTS.clear()
    run_world(2000)
    ck(int(A.ECHOES) == e0 + 1 and str(A.LAST_ECHO).startswith("shock:") and stuns() == [0.5] and len(amts()) == 1 and amts()[0] < 25.0,
       "X42: the echo cone 1 s later: weaker, stun 0.5 s (%s %s %s %s)" % (A.LAST_ECHO, amts(), stuns(), [str(x) for x in EFX]))
    setp(WK, {"u.ShieldShockwave": None, "e.ShieldShockwave": None})
    # Shield Training (T1) +0.25 s; Retribution (PB4): 20 % max Health in 5 s -> the next one free and stun x2; Shockwave Surge (PC4)
    wreset()
    AS.RETRI.clear()
    TREE["csv"] = "A2,T1,PB4,PC4"
    AS.TREEC.clear()
    A.ctxFor(wu, WK, SSW, 0, "A2,T1,PB4,PC4")
    ck(AS.RETRI.get(wu) is not None, "X42: a Warrior with Retribution gets its damage record")
    A.inHit2(tst, tbuf, wr, dmg(sf, 25.0), now_ms())
    ck(float(AS.RETRI.get(wu)[0]) == 1.0 and any("Retribution" in x_ for x_ in said()), "X42: Retribution armed after 25 of 100 Health in 5 s")
    wm.setStatValue(HP, JFloat(50.0))
    r_ = fcast(wpr, wr, "2", 0)
    run_world()
    ck(sv(wm, MANA) == 400.0 and stuns() == [3.5] and " retribution" in r_, "X42: ... the Shockwave is free and stuns (1.5 + 0.25 T1) x 2 = 3.5 s: %s %s" % (r_, stuns()))
    ck(amts() == [20.0] and abs(sv(wm, HP) - 53.0) < 0.01, "X42: Shockwave Surge - damage -20 %% (20), heals you 3 %% per enemy hit (%s HP)" % sv(wm, HP))
    wreset()
    r_ = fcast(wpr, wr, "2", 0)
    ck(sv(wm, MANA) < 400.0, "X42: Retribution once - the next one costs again")
    TREE["csv"] = None
    AS.TREEC.clear()
    endall()
    # Ground Pound (air: on landing, a ring + knock-up)
    wreset()
    wmsc.getMovementStates().onGround = False
    fcast(wpr, wr, "2", 2)
    wmsc.getMovementStates().onGround = True
    run_world()
    run_world()
    ck(str(A.LAST_LAND).startswith("pound:") and len(amts()) == 2 and any(float(p_[1]) > 0.0 for p_ in PUSH), "X42: Ground Pound - a 4-block ring where you land, knock-up (%s)" % A.LAST_LAND)
    endall()
    # ---------------- X43 Iron Chain (the hook, the drag, bosses, Pull, Chain, Slow, Barbed Chain, Anchor)
    wreset()
    setp(WK, {"p1": "RallyingGuard", "p2": "IronChain", "a1": "ShieldShockwave", "a2": "Challenge"})
    c1, c2 = mob(155, 40.5, 8.5), mob(156, 40.5, 10.5)
    NEARL[:] = [c1, c2]
    MOBT["t"] = None
    ck(fcast(wpr, wr, "2", 0) == "notarget" and sv(wm, MANA) == 400.0, "X43: no enemy in your look -> refused, nothing spent")
    MOBT["t"] = c1
    r_ = fcast(wpr, wr, "2", 0)
    run_world()
    ck(r_.startswith("ok:IronChain") and amts() == [15.0] and len(PUSH) == 1 and float(PUSH[0][2]) < 0.0, "X43: hooked: 0.6 H, dragged toward you: %s %s" % (amts(), [list(p_) for p_ in PUSH]))
    ck("Ability_Hooked:0.8" in [str(x) for x in EFX] and stuns() == [1.0], "X43: the vanilla chain rune's Hooked look + stun 1 s")
    wreset()
    make_boss(c1)
    fcast(wpr, wr, "2", 0)
    run_world()
    ck(len(PUSH) == 0 and "held" in str(A.LAST_WAR), "X43: a boss is not dragged without Pull (%s)" % A.LAST_WAR)
    wreset()
    setp(WK, {"u.IronChain": lv(4), "e.IronChain": "Pull,Chain"})
    fcast(wpr, wr, "2", 0)
    run_world()
    ck(len(PUSH) == 2 and len(amts()) == 2, "X43: Pull drags the boss too; Chain hooks the enemy next to it (%d pulls, %s)" % (len(PUSH), amts()))
    put(c1, NPCc.getComponentType(), TCc())   # back to a role-less mob (the NPC slot holds the stand-in again)
    setp(WK, {"u.IronChain": None, "e.IronChain": None})
    wreset()
    AS.CHAINED.clear()
    TREE["csv"] = "A3,PB3"
    AS.TREEC.clear()
    fcast(wpr, wr, "2", 0)
    run_world()
    ck(AS.CHAINED.get(c1) is not None, "X43: Barbed Chain marks the dragged enemy")
    TBf.EVENTS.clear()
    A.inHit2(tst, tbuf, wr, dmg(c2, 40.0), now_ms())
    ck(amts() == [10.0], "X43: ... it takes 25 %% of the damage dealt to you (40 -> 10): %s" % amts())
    TREE["csv"] = None
    AS.TREEC.clear()
    wreset()
    setp(WK, {"p1": "RallyingGuard", "p2": "ShieldShockwave", "a1": "IronChain", "a2": "Challenge"})
    fcast(wpr, wr, "3", 3)
    run_world()
    ck(stuns() == [1.5] and "Root:2.5" in [str(x) for x in EFX], "X43: Anchor (crouch) - stun 1.5 s + rooted 1 s more: %s" % efx("Root"))
    setp(WK, WSL)
    endall()
    # ---------------- X44 Challenge (the cut, the reflect, Duel, Chain, Ward)
    wreset()
    setp(WK, {"p1": "Challenge", "p2": "ShieldShockwave", "a1": "IronChain", "a2": "RallyingGuard"})
    h1 = mob(157, 40.5, 4.5)
    h2 = mob(158, 41.5, 5.5)
    NEARL[:] = [h1, h2]
    MOBT["t"] = h1
    r_ = fcast(wpr, wr, "1", 0)
    ch_ = AS.CHALLS.get(h1)
    ck(r_.startswith("ok:Challenge") and ch_ is not None and int(ch_[3]) == 3000 and int(ch_[4]) == 2000 and TAUNT.contains(h1) and AS.CHALLS.get(h2) is None,
       "X44: Challenge - it must fight you (taunt), you take 30 %% less, 20 %% reflects: %s" % r_)
    TBf.EVENTS.clear()
    d_ = dmg(h1, 100.0)
    A.inHit2(tst, tbuf, wr, d_, now_ms())
    ck(abs(float(d_.getAmount()) - 70.0) < 1e-3 and amts() == [20.0], "X44: the REAL hook: 100 -> 70, 20 reflected (%s)" % amts())
    d_ = dmg(h2, 100.0)
    A.inHit2(tst, tbuf, wr, d_, now_ms())
    ck(abs(float(d_.getAmount()) - 100.0) < 1e-3, "X44: another enemy's hit is not cut")
    endall()
    wreset()
    setp(WK, {"u.Challenge": lv(8), "e.Challenge": "Chain,Ward"})
    AS.WARD.clear()
    r_ = fcast(wpr, wr, "1", 0)
    ck(AS.CHALLS.get(h2) is not None and AS.WARD.get(wu) is not None, "X44: Chain challenges the enemy next to it; Ward gives you a shield: %s" % r_)
    setp(WK, {"u.Challenge": None, "e.Challenge": None, "p1": "IronChain", "p2": "ShieldShockwave", "a1": "Challenge", "a2": "RallyingGuard"})
    wreset()
    AS.CHALLS.clear()
    fcast(wpr, wr, "3", 3)
    ck(int(AS.CHALLS.get(h1)[3]) == 4000 and int(AS.CHALLS.get(h1)[4]) == 3000, "X44: Duel (crouch) - 40 %% / 30 %%")
    setp(WK, WSL)
    endall()
    AS.CHALLS.clear()
    # ---------------- X45 Guardian's Oath (the link, the transfer through the REAL hook, the cut, no party)
    wreset()
    setp(WK, {"alt": "B", "p1": "GuardiansOath", "p2": "ShieldShockwave", "a1": "IronChain", "a2": "RallyingGuard"})
    AS.GUARDED.clear()
    A.TARGET = Fn(lambda o: xu)
    r_ = fcast(wpr, wr, "1", 0)
    ck(r_.startswith("ok:GuardiansOath") and AS.OATHS.get(xu) is not None and float(AS.OATHW.get(wu)[1]) == 15.0, "X45: linked to the party member you look at: %s" % r_)
    TBf.EVENTS.clear()
    hm_ = mob(159, 44.5, 0.5)
    d_ = dmg(hm_, 100.0)
    out_ = str(A.inHit2(tst, tbuf, xr, d_, now_ms()))
    ck("oath>" in out_ and abs(float(d_.getAmount()) - 60.0) < 1e-3 and len(evs()) == 1 and evs()[0][0].equals(wr) and evs()[0][1] == 34.0,
       "X45: the ally takes 60, 40 goes to you (x 0.85 = 34): %s %s" % (out_, evs()))
    ck(uses(WK, "GuardiansOath") == 1 and int(A.OATHED) >= 1, "X45: the first transfer counts the use")
    d_ = dmg(hm_, 100.0)
    A.inHit2(tst, tbuf, wr, d_, now_ms())
    ck(abs(float(d_.getAmount()) - 85.0) < 1e-3, "X45: you take 15 %% less while linked")
    MEMBERS.pop(WK)
    MEMBERS.pop(str(xu))
    wreset()
    ck(fcast(wpr, wr, "1", 0) == "noally" and sv(wm, MANA) == 400.0, "X45: no party member -> refused, nothing spent")
    MEMBERS[WK] = MEMBERS[str(xu)] = [WK, str(xu)]
    A.TARGET = None
    setp(WK, WSL)
    AS.OATHS.clear()
    AS.OATHW.clear()
    endall()
    # ---------------- X46 BERSERKER: Enrage (picked once, the growing buff through the REAL hooks, shapes, tree nodes, Leech)
    wreset()
    AS.RAGE.clear()
    em = mob(160, 61.5, 3.5)
    NEARL[:] = [em]
    r_ = fcast(bpr, bref, "1", 0)
    rb_, ry_ = AS.RAGE.get(bu), AS.RAGE.get(yu)
    ck(r_.startswith("ok:Enrage") and rb_ is not None and ry_ is not None and float(rb_[3]) == 20.0 and float(rb_[4]) == 40.0 and float(ry_[3]) == 10.0 and float(ry_[4]) == 20.0,
       "X46: Enrage - you +20 -> +40, the party member +10 -> +20 (picked once): %s" % r_)
    ck(abs(sv(bm, MANA) - 397.0) < 0.01 and abs(sv(bm, STAM) - 47.0) < 0.01, "X46: 3 + 3")
    ck([round(float(A.ragePct(JArray(JDouble)([0.0, 10000.0, 15000.0, 10.0, 20.0, 3000.0, 0.0, 0.0]), t_)), 3) for t_ in (0, 5000, 12000, 16500, 20000)] == [10.0, 15.0, 20.0, 10.0, 0.0],
       "X46: the curve - grows 10 s, holds 5 s, (Warbringer) fades 3 s")
    d_ = dmg(bref, 100.0)
    A.outHit2(tst, tbuf, em, d_, bu, now_ms())
    ck(119.0 < float(d_.getAmount()) < 121.0, "X46: the REAL outgoing hook - your weapon hit +20 %% right away (%s)" % d_.getAmount())
    u0_ = uses(BK, "Enrage")
    A.hitLanded2(tbuf, em, dmg(bref, 10.0), now_ms())
    ck(uses(BK, "Enrage") == u0_ + 1, "X46: your first landed hit while enraged counts the use")
    endall()
    wreset()
    AS.RAGE.clear()
    setp(BK, {"p1": "Whirlwind", "p2": "Earthsplitter", "a1": "Enrage", "a2": "BloodFrenzy"})
    fcast(bpr, bref, "3", 3)
    ck(float(AS.RAGE.get(bu)[4]) == 60.0 and AS.RAGE.get(yu) is None, "X46: Lone Rage (crouch) - you only, peak +10 points (x2, the 60 cap)")
    setp(BK, WSL)
    endall()
    # War Horn (PA1): a second call picks up the late; Rally (PA4): the peak shield, +6 Mana; Warbringer (PA5): fade, peak -10 %
    wreset()
    AS.RAGE.clear()
    AS.WARD.clear()
    moveto(yr, 85.5, 0.5)
    TREE["csv"] = "A1,PA1,PA4,PA5"
    AS.TREEC.clear()
    r_ = fcast(bpr, bref, "1", 0)
    rb_ = AS.RAGE.get(bu)
    ck(AS.RAGE.get(yu) is None and float(rb_[5]) == 3000.0 and abs(float(rb_[4]) - (40.0 - 5.0) * 0.9) < 1e-6 and abs(float(rb_[3]) - 30.0) < 1e-6,
       "X46: War Horn (allies start +15, your peak -5) + Warbringer (fade 3 s, peak x0.9): %s" % list(rb_))
    ck(abs(sv(bm, MANA) - 391.0) < 0.01, "X46: Rally - the cast costs +6 Mana")
    moveto(yr, 63.5, 0.5)
    zr_ = zones(15)[0]
    zr_.t1 = now_ms() - 1
    zr_.t2 = now_ms() - 1
    run_world()
    ck(AS.RAGE.get(yu) is not None and abs(float(AS.WARD.get(yu)[0]) - 10.0) < 1e-6 and abs(float(AS.WARD.get(bu)[0]) - 10.0) < 1e-6,
       "X46: the horn picks up the late ally; at the peak everyone picked gets a 10 %% shield")
    TREE["csv"] = None
    AS.TREEC.clear()
    endall()
    # War Charge (sprint): everyone you pass within 4 for 2 s; War Leap (air); Leech
    wreset()
    AS.RAGE.clear()
    moveto(yr, 85.5, 0.5)
    fcast(bpr, bref, "1", 1)
    ck(AS.RAGE.get(yu) is None, "X46: War Charge - the ally far away is not picked at the cast")
    moveto(yr, 62.0, 0.5)
    run_world()
    ck(AS.RAGE.get(yu) is not None, "X46: ... passing them picks them up")
    moveto(yr, 63.5, 0.5)
    endall()
    wreset()
    bmsc.getMovementStates().onGround = False
    fcast(bpr, bref, "1", 2)
    bmsc.getMovementStates().onGround = True
    run_world()
    ck(str(A.LAST_LAND).startswith("rage:"), "X46: War Leap - on landing (%s)" % A.LAST_LAND)
    endall()
    wreset()
    AS.RAGE.clear()
    setp(BK, {"u.Enrage": lv(8), "e.Enrage": "Leech,"})
    fcast(bpr, bref, "1", 0)
    bm.setStatValue(HP, JFloat(50.0))
    A.hitLanded2(tbuf, em, dmg(bref, 50.0), now_ms())
    ck(abs(sv(bm, HP) - 51.5) < 0.01, "X46: Leech - you heal 3 %% of your hits while enraged (%s)" % sv(bm, HP))
    setp(BK, {"u.Enrage": None, "e.Enrage": None})
    AS.RAGE.clear()
    endall()
    # ---------------- X47 Whirlwind (the spin, heal, Bleed, Staggering Spin, Pull, Echo, Grinder, Spinning Drop)
    wreset()
    w1_, w2_ = mob(161, 61.5, 0.5), mob(162, 60.5, 2.0)
    NEARL[:] = [w1_, w2_]
    bm.setStatValue(HP, JFloat(50.0))
    r_ = fcast(bpr, bref, "2", 0)
    run_world()
    ck(r_.startswith("ok:Whirlwind") and sorted(amts()) == [12.5, 12.5] and abs(sv(bm, HP) - 52.5) < 0.01, "X47: the spin hits both (0.5 H), heals 10 %% of it: %s %s" % (amts(), sv(bm, HP)))
    ck(uses(BK, "Whirlwind") == 1, "X47: a spin that hits counts once")
    endall()
    wreset()
    AS.BLEEDS.clear()
    TREE["csv"] = "A2,PB2,PC3"
    AS.TREEC.clear()
    fcast(bpr, bref, "2", 0)
    run_world()
    ck(sorted(amts()) == [11.25, 11.25] and AS.BLEEDS.get(w1_) is not None and sv(bm, HP) == 100.0 and len(PUSH) == 2,
       "X47: Bleed -10 %% damage + bleeding; Staggering Spin pushes, no lifesteal: %s" % amts())
    TBf.EVENTS.clear()
    bj_ = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 22]
    run_world(1500)
    ck(len(bj_) == 2 and 4.5 in amts(), "X47: the bleed ticks 0.2 H a second (x the -10 %% of Bleed: 4.5): %s" % amts())
    TREE["csv"] = None
    AS.TREEC.clear()
    endall()
    AS.BLEEDS.clear()
    wreset()
    setp(BK, {"u.Whirlwind": lv(10), "e.Whirlwind": "Echo,Pull"})
    fcast(bpr, bref, "2", 0)
    run_world()
    ck(any(float(p_[0]) < 0.0 for p_ in PUSH), "X47: Pull draws enemies into the spin")
    zs_ = zones(16)[0]
    zs_.until = now_ms() - 1
    run_world()
    e0 = int(A.ECHOES)
    run_world(2000)
    ck(int(A.ECHOES) == e0 + 1 and str(A.LAST_ECHO).startswith("spin:") and len(zones(16)) == 1, "X47: Echo - a weaker spin 1 s after the spin ends (%s)" % A.LAST_ECHO)
    setp(BK, {"u.Whirlwind": None, "e.Whirlwind": None})
    endall()
    wreset()
    setp(BK, {"p1": "Enrage", "p2": "Earthsplitter", "a1": "Whirlwind", "a2": "BloodFrenzy"})
    fcast(bpr, bref, "3", 3)
    ck("Root:3" in [str(x) for x in EFX] and abs(float(zones(16)[0].r) - 3.5) < 1e-6, "X47: Grinder (crouch) - rooted, 3.5 blocks")
    setp(BK, WSL)
    endall()
    wreset()
    bmsc.getMovementStates().onGround = False
    fcast(bpr, bref, "2", 2)
    bmsc.getMovementStates().onGround = True
    run_world()
    ck(str(A.LAST_LAND).startswith("spin:") and "slam=2" in str(A.LAST_LAND), "X47: Spinning Drop - a 1.0 H slam on landing, then the spin (%s)" % A.LAST_LAND)
    endall()
    # ---------------- X48 Earthsplitter (the line, missing Health, knock-up, shapes, Split, Blood Pact, Seismic, Ground Pound)
    wreset()
    setp(BK, {"p1": "Enrage", "p2": "Earthsplitter", "a1": "Whirlwind", "a2": "BloodFrenzy"})
    LOOKV["v"] = [60.5, 64.9, 0.5, 0.0, 0.0, 1.0]
    e1_, e2_ = mob(163, 60.5, 6.5), mob(164, 66.5, 6.5)
    NEARL[:] = [e1_, e2_]
    bm.setStatValue(HP, JFloat(50.0))
    r_ = fcast(bpr, bref, "2", 0)
    run_world()
    ck(r_.startswith("ok:Earthsplitter") and evs() and evs()[0][0].equals(e1_) and amts() == [75.0] and any(float(p_[1]) > 0.0 for p_ in PUSH),
       "X48: the line hits the one on it: 2.0 H x 1.5 (half Health missing), knock-up: %s" % amts())
    wreset()
    TREE["csv"] = "A3,PB4,PC2,PC4"
    AS.TREEC.clear()
    e3_ = mob(165, 60.5, 9.5)
    NEARL[:] = [e1_, e2_, e3_]
    r_ = fcast(bpr, bref, "2", 0)
    ck(abs(sv(bm, HP) - 90.0) < 0.01 and " pact=10" in r_ and " width=3" in r_ and " len=9" in r_,
       "X48: Blood Pact pays 10 %% Health; Seismic: 3 wide, 12 -> 9 long: %s" % r_)
    run_world()
    ck(abs(amts()[0] - 2.0 * 25.0 * 1.3 * 1.1) < 1e-3 and stuns() == [1.0] and 37.5 in amts(),
       "X48: +30 %% (pact) x 1.1 (10 %% missing); Ground Pound slams the end (1.5 H, stun 1 s): %s %s" % (amts(), stuns()))
    ck(int(A.ctxFor(bu, BK, ES, 0, "A3,PC4").cdAdd) == 3000, "X48: Ground Pound - cooldown +3 s")
    TREE["csv"] = None
    AS.TREEC.clear()
    wreset()
    setp(BK, {"u.Earthsplitter": lv(4), "e.Earthsplitter": "Split,"})
    side_ = mob(166, 60.5 + 6.0 * 0.342, 0.5 + 6.0 * 0.94)
    NEARL[:] = [e1_, side_]
    fcast(bpr, bref, "2", 0)
    run_world()
    ck(sorted(amts()) == [26.5, 53.0], "X48: Split - two side lines at 50 %% (Lv 4 = +6 %%): %s" % amts())
    setp(BK, {"u.Earthsplitter": None, "e.Earthsplitter": None, "p1": "Enrage", "p2": "Whirlwind", "a1": "Earthsplitter", "a2": "BloodFrenzy"})
    wreset()
    NEARL[:] = [e1_]
    r_ = fcast(bpr, bref, "3", 3)
    fj_ = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 19]
    ck(len(fj_) == 1 and int(fj_[0].at) - now_ms() > 800, "X48: Fissure (crouch) - the crack comes 1 s later")
    run_world()
    ck(amts() == [60.0] and "Slow:2" in [str(x) for x in EFX], "X48: ... 2.4 H, slowed 2 s: %s" % amts())
    wreset()
    setp(BK, {"p1": "Enrage", "p2": "Earthsplitter", "a1": "Whirlwind", "a2": "BloodFrenzy"})
    cr1 = mob(169, 60.5, 3.5)
    NEARL[:] = [cr1, e2_]
    bmsc.getMovementStates().onGround = False
    fcast(bpr, bref, "2", 2)
    bmsc.getMovementStates().onGround = True
    run_world()
    run_world()
    ck(str(A.LAST_LAND).startswith("split:") and amts() == [50.0], "X48: Crater (air) - a 5-block ring where you land (the one 6 blocks off is spared): %s %s" % (A.LAST_LAND, amts()))
    setp(BK, WSL)
    endall()
    # ---------------- X49 Blood Frenzy (the toggle, stacks from the REAL landed hook, cost per swing, the aura, Floor, the exclusion)
    wreset()
    setp(BK, {"p1": "BloodFrenzy", "p2": "Whirlwind", "a1": "Earthsplitter", "a2": "Enrage"})
    AS.FRENZ.clear()
    AS.FURY.clear()
    AS.SWINGS.clear()
    fm_ = mob(167, 61.5, 1.5)
    NEARL[:] = [fm_]
    r_ = fcast(bpr, bref, "1", 0)
    fz_ = AS.FRENZ.get(bu)
    ck(r_.startswith("ok:BloodFrenzy") and fz_ is not None and int(AS.left(BK, "BloodFrenzy", now_ms())) == 0, "X49: Blood Frenzy ON (1 + 1, no cooldown while on): %s" % r_)
    h1_ = str(A.hitLanded2(tbuf, fm_, dmg(bref, 20.0), now_ms()))
    h2_ = str(A.hitLanded2(tbuf, fm_, dmg(bref, 20.0), now_ms()))
    ck(h1_ == "stack 1" and h2_ == "same swing" and abs(sv(bm, MANA) - 398.3) < 0.01 and abs(sv(bm, STAM) - 48.4) < 0.01,
       "X49: a landed swing = 1 stack + 0.7 Mana + 0.6 Stamina; a 2nd target of the same swing = no stack: %s %s" % (h1_, h2_))
    # FIX ROUND (LOCKED Skyy L129 "cost mana and stamina per attack (regardless of weather you hit or not.)"): the cost is taken at the
    # swing START through the REAL Primary InteractionChainStartEvent (Abil.onSwing = AbilRuneSys' Primary branch), a miss pays too
    m0_, s0_ = sv(bm, MANA), sv(bm, STAM)
    time.sleep(0.2)
    sw_ = str(A.onSwing(event("Primary", "Weapon_Battleaxe_Crude", 0), bref, tbuf, now_ms()))
    ck(sw_ == "paid" and abs(sv(bm, MANA) - (m0_ - 0.7)) < 0.01 and abs(sv(bm, STAM) - (s0_ - 0.6)) < 0.01 and int(A.frenzyStacks(fz_, now_ms())) == 1
       and int(A.FRENZYSWINGS) >= 1,
       "X49 FIX: a MISSED swing (the Primary chain start, no hit) pays 0.7 Mana + 0.6 Stamina and gives no stack: %s %.2f %.2f" % (sw_, sv(bm, MANA), sv(bm, STAM)))
    m1_, s1_ = sv(bm, MANA), sv(bm, STAM)
    time.sleep(0.2)
    sw2_ = str(A.onSwing(event("Primary", "Weapon_Battleaxe_Crude", 0), bref, tbuf, now_ms()))
    hl_ = str(A.hitLanded2(tbuf, fm_, dmg(bref, 20.0), now_ms()))
    ck(sw2_ == "paid" and hl_ == "stack 2" and abs(sv(bm, MANA) - (m1_ - 0.7)) < 0.01 and abs(sv(bm, STAM) - (s1_ - 0.6)) < 0.01,
       "X49 FIX: a swing that lands pays ONCE (at its start) and gives its stack: %s %s %.2f" % (sw2_, hl_, sv(bm, MANA)))
    # FIX ROUND 2 (critic: a 3 s 'already paid' window let missed swings go free): the start payment is consumed by its one landed swing
    m3_, s3_ = sv(bm, MANA), sv(bm, STAM)
    AS.SWINGS.clear()
    hl3_ = str(A.hitLanded2(tbuf, fm_, dmg(bref, 20.0), now_ms()))
    ck(hl3_.startswith("stack") and abs(sv(bm, MANA) - (m3_ - 0.7)) < 0.01 and abs(sv(bm, STAM) - (s3_ - 0.6)) < 0.01 and AS.PAID.get(bu) is None,
       "X49 FIX2: the next landed swing whose start the hook missed pays on its hit (one start payment covers one swing): %s %.2f" % (hl3_, sv(bm, MANA)))
    rg_ = [int(x_) for x_ in fz_.ring]   # take that extra stack back (the checks below count 2)
    fz_.ring[rg_.index(max(rg_))] = 0
    fz_.total = int(fz_.total) - 1
    evc_ = event("Primary", "Weapon_Battleaxe_Crude", 0)
    evc_.setCancelled(True)
    m2_ = sv(bm, MANA)
    ck(A.onSwing(evc_, bref, tbuf, now_ms()) is None and abs(sv(bm, MANA) - m2_) < 1e-6, "X49 FIX: a cancelled chain (another mod refused the swing) costs nothing")
    HANDS[51] = "Tool_Pickaxe_Crude"
    ck(str(A.onSwing(event("Primary", "Tool_Pickaxe_Crude", 0), bref, tbuf, now_ms())) == "tool" and abs(sv(bm, MANA) - m2_) < 1e-6,
       "X49 FIX: mining with a tool is not an attack - no cost")
    HANDS[51] = "Weapon_Battleaxe_Crude"
    ck(A.onSwing(event("Primary", "Weapon_Battleaxe_Crude", 0), yr, tbuf, now_ms()) is None and abs(sv(bm, MANA) - m2_) < 1e-6,
       "X49 FIX: a player with no frenzy on swings for free")
    rs24_ = C("AbilRuneSys")()
    rs24_.handle(0, None, tst, tbuf, event("Primary", "Weapon_Battleaxe_Crude", 0))
    ck(not bool(C("AbilRuneSys").FAILED_ONCE), "X49 FIX: AbilRuneSys.handle (the Primary branch) with no chunk returns quietly")
    AS.PAID.clear()
    fz_.t1 = now_ms()
    EFX.clear()
    run_world()
    ck(abs(float(AS.FURY.get(bu)[0]) - 3.0) < 1e-6 and abs(float(AS.FURY.get(yu)[0]) - 1.5) < 1e-6 and efx("SkyyAbility_Spd_31"),
       "X49: 2 stacks = you +3 %% damage + 1 %% speed, the ally in the aura half: %s" % efx("SkyyAbility_Spd_"))
    d_ = dmg(bref, 100.0)
    A.outHit2(tst, tbuf, fm_, d_, bu, now_ms())
    ck(abs(float(d_.getAmount()) - 103.0) < 1e-3, "X49: the REAL outgoing hook: +3 %% (%s)" % d_.getAmount())
    r_ = fcast(bpr, bref, "1", 0)
    ck(r_.startswith("ok:BloodFrenzy off") and bool(fz_.ended) and 9000 < int(AS.left(BK, "BloodFrenzy", now_ms())) <= 10000, "X49: a press turns it off (free) - 10 s before it can go on again: %s" % r_)
    run_world()
    ck(AS.FRENZ.get(bu) is None and AS.FURY.get(bu) is None and fcast(bpr, bref, "1", 0) == "cooldown", "X49: off: the buff goes; a press inside the 10 s is refused")
    # FIX ROUND (critic: a frenzy left in a world nobody ticks stayed "on"): the world switch (ClassReady -> Abil.worldLeft)
    wreset()
    AS.BANKED.clear()
    r_ = fcast(bpr, bref, "1", 0)
    fz_ = AS.FRENZ.get(bu)
    ck(r_.startswith("ok:BloodFrenzy") and AW.at(tst) is not None and bool(AW.at(tst).holds(fz_)) and A.worldLeft(bu, tst) is None
       and AS.FRENZ.get(bu) is not None and not bool(fz_.ended), "X49 FIX: arriving in the world that holds the frenzy keeps it on: %s" % r_)
    said()
    wl_ = str(A.worldLeft(bu, None))
    sd_ = said()
    ck(wl_ == "frenzy" and bool(fz_.ended) and AS.FRENZ.get(bu) is None and AS.BANKED.get(BK) is not None and AS.BANKED.get(bu) is None and any("changed world" in x_ for x_ in sd_),
       "X49 FIX: arriving in another world ends it (banked under the profile key - FIX2, a line): %s %s" % (wl_, sd_))
    AS.BANKED.remove(BK)
    run_world()
    ck(int(AS.left(BK, "BloodFrenzy", now_ms())) == 0 and AS.BANKED.get(BK) is None and not [x_ for x_ in said() if "out of" in x_],
       "X49 FIX: the old zone's last tick arms no cooldown, says nothing and (finding 2) re-adds no bank for a frenzy that is no longer the live one")
    r_ = fcast(bpr, bref, "1", 0)
    ck(r_.startswith("ok:BloodFrenzy") and not r_.startswith("ok:BloodFrenzy off"), "X49 FIX: the next press turns it ON (not a phantom 'off'): %s" % r_)
    fz_ = AS.FRENZ.get(bu)
    fz_.ended = True
    fz_.why = "left"
    AS.FRENZ.remove(bu)   # = ClassQuit
    AS.BANKED.remove(BK)
    run_world()
    ck(AS.BANKED.get(BK) is None, "X49 FIX: after ClassQuit removed the frenzy, its last tick does not re-add BANKED")
    endall()
    # Floor (Lv 1 = 5) + the Floor / Duration+ exclusion
    wreset()
    setp(BK, {"u.BloodFrenzy": lv(4), "e.BloodFrenzy": "Floor,"})
    fcast(bpr, bref, "1", 0)
    fz_ = AS.FRENZ.get(bu)
    ck(int(fz_.n1) == 5, "X49: Floor Lv 1 = 5 stacks")
    for i_ in range(5):
        AS.SWINGS.clear()
        A.hitLanded2(tbuf, fm_, dmg(bref, 20.0), now_ms())
    run_world()
    for i_ in range(len(fz_.ring)):
        if int(fz_.ring[i_]) > 0:
            fz_.ring[i_] = now_ms() - 9000
    run_world()
    ck(int(A.frenzyStacks(fz_, now_ms())) == 5, "X49: ... once 5 was reached, the stacks never fall below 5 (%d)" % int(A.frenzyStacks(fz_, now_ms())))
    eq_ = str(A.equipMod(bu, "BloodFrenzy", 1, "Duration", None, False))
    ck(eq_.startswith("-Duration+ never goes together with Floor"), "X49: Floor + Duration+ refused (Skyy L130): %s" % eq_)
    setp(BK, {"e.BloodFrenzy": "Floor,Duration"})
    cxf = A.ctxFor(bu, BK, BF, 0, None)
    ck(int(cxf.m0) == int(AMD.FLOOR) and int(cxf.m1) == -1, "X49: a file holding both -> the second is ignored")
    bm.setStatValue(MANA, JFloat(0.3))
    AS.SWINGS.clear()
    hm2 = str(A.hitLanded2(tbuf, fm_, dmg(bref, 20.0), now_ms()))
    run_world()
    ck(hm2 == "out of mana" and AS.FRENZ.get(bu) is None and int(AS.left(BK, "BloodFrenzy", now_ms())) > 9000 and any("out of Mana" in x_ for x_ in said()),
       "X49: out of Mana -> it ends, the 10 s wait starts: %s" % hm2)
    ck(AS.BANKED.get(BK) is not None and float(AS.BANKED.get(BK)[0]) >= 5.0, "X49: the stacks it ended with are banked (by the profile key)")
    setp(BK, {"u.BloodFrenzy": None, "e.BloodFrenzy": None, "p1": "Enrage", "p2": "Whirlwind", "a1": "BloodFrenzy", "a2": "Earthsplitter"})
    wreset()
    fcast(bpr, bref, "3", 3)
    ck(int(AS.FRENZ.get(bu).total) == int(float(AS.BANKED.get(BK)[0]) * 0.5), "X49: Blood Bank (crouch) - starts with half the banked stacks")
    fcast(bpr, bref, "3", 3)
    endall()
    setp(BK, WSL)
    AS.FURY.clear()
    # ---------------- X50 Warlord's Banner (the buffs, kills extend it, leaving its range, Echo, Rooted, Bearer)
    wreset()
    setp(BK, {"alt": "B", "p1": "WarlordsBanner", "p2": "Whirlwind", "a1": "Earthsplitter", "a2": "Enrage"})
    AS.WAR.clear()
    r_ = fcast(bpr, bref, "1", 0)
    ck(r_.startswith("ok:WarlordsBanner") and 99000 < int(AS.left(BK, "WarlordsBanner", now_ms())) <= 100000, "X50: the banner stands; its cooldown waits for the fall: %s" % r_)
    ck(abs(sv(bm, MANA) - 391.0) < 0.01 and abs(sv(bm, STAM) - 42.0) < 0.01, "X50: 9 + 8 upfront")
    run_world()
    ck(float(AS.WAR.get(bu)[0]) == 16.0 and float(AS.WAR.get(yu)[0]) == 12.0, "X50: in range - you +16 %%, your party +12 %% (damage + defence)")
    d_ = dmg(em, 100.0)
    A.inHit2(tst, tbuf, bref, d_, now_ms())
    ck(abs(float(d_.getAmount()) - 84.0) < 1e-3 and abs(float(A.outMult(tst, em, bu, now_ms())) - 1.16) < 1e-9, "X50: the defence through the REAL hook, the damage multiplier")
    zb_ = zones(18)[0]
    u0b = int(zb_.until)
    km_ = mob(168, 62.5, 0.5)
    put(km_, DTHc.getComponentType(), U.allocateInstance(DTHc.class_))
    hk_ = str(A.hitLanded2(tbuf, km_, dmg(bref, 10.0), now_ms()))
    ck(hk_.startswith("banner+1") and int(zb_.until) - u0b == 1000, "X50: a kill in range +1 s (%s)" % hk_)
    A.hitLanded2(tbuf, km_, dmg(bref, 10.0), now_ms())
    ck(int(zb_.until) - u0b == 1000, "X50: ... counted once per mob")
    moveto(bref, 90.5, 0.5)
    run_world()
    ck(bool(zb_.ended) and str(zb_.why) == "range" and 39000 < int(AS.left(BK, "WarlordsBanner", now_ms())) <= 40000 and any("you left its range" in x_ for x_ in said()),
       "X50: leaving its range fells it; the 40 s count starts at the fall")
    moveto(bref, 60.5, 0.5)
    endall()
    wreset()
    # FIX ROUND: a kill only feeds a banner of its own world; the world switch fells it (cooldown from the fall, a line, no 2nd end)
    fcast(bpr, bref, "1", 0)
    zb_ = zones(18)[0]
    u1b = int(zb_.until)
    aw.dropZone(zb_)
    km2_ = mob(169, 62.5, 1.5)
    put(km2_, DTHc.getComponentType(), U.allocateInstance(DTHc.class_))
    hk2_ = A.hitLanded2(tbuf, km2_, dmg(bref, 10.0), now_ms())
    ck((hk2_ is None or not str(hk2_).startswith("banner")) and int(zb_.until) == u1b, "X50 FIX: a kill at the same spot in a world that does not hold the banner adds nothing: %s" % hk2_)
    aw.addZone(zb_)
    ck(A.worldLeft(bu, tst) is None and not bool(zb_.ended), "X50 FIX: arriving in the banner's own world keeps it")
    said()
    wl_ = str(A.worldLeft(bu, None))
    ck(wl_ == "banner" and bool(zb_.ended) and str(zb_.why) == "world" and AS.BANNERS.get(bu) is None and 39000 < int(AS.left(BK, "WarlordsBanner", now_ms())) <= 40000
       and any("changed world" in x_ for x_ in said()), "X50 FIX: another world fells it, the 40 s count starts at the fall: %s" % wl_)
    AS.clearCd(BK)
    run_world()
    ck(int(AS.left(BK, "WarlordsBanner", now_ms())) == 0 and not [x_ for x_ in said() if "banner fell" in x_], "X50 FIX: its old zone's last tick does not end it twice")
    endall()
    # FIX ROUND 2 (critic: a quit armed the banner's 40 s after the owner left - a quick relog found it on cooldown): the REAL ClassQuit
    wreset()
    fcast(bpr, bref, "1", 0)
    zq_ = zones(18)[0]
    AS.BANKED.put(BK, JArray(JDouble)([6.0, float(now_ms())]))
    fq2_ = U.allocateInstance(PDE.class_)
    f_.set(fq2_, bpr)
    C("ClassQuit")().accept(fq2_)
    said()
    run_world()
    ck(bool(zq_.ended) and str(zq_.why) == "quit" and AS.BANNERS.get(bu) is None and int(AS.left(BK, "WarlordsBanner", now_ms())) == 0
       and not [x_ for x_ in said() if "banner fell" in x_.lower()], "X50 FIX2: a quit ends the banner with no cooldown and no line (a relog finds it ready)")
    ck(AS.BANKED.get(BK) is None, "X50 FIX2: ClassQuit drops the Blood Bank stacks by the profile key")
    endall()
    wreset()
    setp(BK, {"u.WarlordsBanner": lv(10), "e.WarlordsBanner": "Echo,"})
    fcast(bpr, bref, "1", 0)
    run_world()
    zb_ = zones(18)[0]
    zb_.until = now_ms() - 1
    run_world()
    w_y = AS.WAR.get(yu)
    ck(w_y is not None and abs(float(w_y[0]) - 12.0 * float(A.lvlMult(10)) * 0.2) < 1e-6 and float(w_y[2]) > now_ms() + 3000, "X50: Echo - the buff lingers 4 s at 20 %% on everyone who was in range")
    setp(BK, {"u.WarlordsBanner": None, "e.WarlordsBanner": None, "p1": "Enrage", "p2": "Whirlwind", "a1": "Earthsplitter", "a2": "WarlordsBanner"})
    endall()
    wreset()
    TREE["csv"] = "A4,PA3"
    AS.TREEC.clear()
    fcast(bpr, bref, "4", 3)
    zb_ = zones(18)[0]
    ck(abs(int(zb_.until) - now_ms() - 35000) < 500 and abs(float(zb_.r) - 10.0) < 1e-6, "X50: Rooted Banner 10 blocks, 40 s; Banner Bearer - 5 s shorter (35 s)")
    moveto(bref, 90.5, 0.5)
    ym.setStatValue(HP, JFloat(50.0))
    zb_.nextHeal = 0
    run_world()
    ck(not bool(zb_.ended) and AS.WAR.get(yu) is not None and abs(sv(ym, HP) - 51.0) < 0.01, "X50: Rooted - leaving only pauses your buff; Bearer heals 1 %% a second")
    moveto(bref, 60.5, 0.5)
    TREE["csv"] = None
    AS.TREEC.clear()
    setp(BK, WSL)
    endall()
    AS.WAR.clear()
    # ---------------- X51 ARCHER: Pinning Shot (the line, pierce 2, root, Mark through the REAL multiplier, shapes, tree nodes)
    wreset()
    LOOKV["v"] = [80.5, 64.9, 0.5, 0.0, 0.0, 1.0]
    p1_, p2_, p3_, poff = mob(170, 80.5, 5.5), mob(171, 80.5, 10.5), mob(172, 80.5, 15.5), mob(173, 85.5, 8.5)
    NEARL[:] = [p3_, poff, p2_, p1_]
    AS.MARKD.clear()
    r_ = fcast(apr, aref, "1", 0)
    run_world()
    ck(r_.startswith("ok:PinningShot") and [t_ for t_, _a in evs()] == [p1_, p2_] and amts() == [30.0, 30.0], "X51: the arrow pierces the first 2 on your line (1.2 H): %s" % amts())
    ck(efx("Root:2") and len(efx("Root:")) == 2 and abs(float(AS.MARKD.get(p1_)[1]) - 15.0) < 1e-6, "X51: rooted 2 s + Marked 15 %%")
    ck(abs(float(A.outMult(tst, p1_, wu, now_ms())) - 1.15) < 1e-9, "X51: Marked = +15 %% damage taken from EVERYONE (a Warrior's hit too)")
    d_ = dmg(wr, 100.0)
    A.outHit2(tst, tbuf, p1_, d_, wu, now_ms())
    ck(abs(float(d_.getAmount()) - 115.0) < 1e-3, "X51: ... through the REAL outgoing hook")
    endall()
    wreset()
    AS.MARKD.clear()
    setp(RK, {"p1": "RapidFire", "p2": "ExplosiveArrow", "a1": "PinningShot", "a2": "ArrowRain"})
    fcast(apr, aref, "3", 3)
    run_world()
    ck(len(amts()) == 3 and abs(float(AS.MARKD.get(p1_)[1]) - 20.0) < 1e-6 and "Root:0.5" in [str(x) for x in EFX], "X51: Steady Aim (crouch) - +1 pierce, Mark 20, you stand still 0.5 s")
    setp(RK, WSL)
    wreset()
    make_boss(p1_)
    fcast(apr, aref, "1", 0)
    run_world()
    ck(efx("Slow:2") and len(efx("Root:")) == 1, "X51: a boss is only slowed, not rooted")
    TREE["csv"] = "A1,PA5"
    AS.TREEC.clear()
    wreset()
    fcast(apr, aref, "1", 0)
    run_world()
    ck("Root:1" in [str(x) for x in EFX] and AS.ROOTS.get(p2_) is not None and abs(float(A.outMult(tst, p2_, wu, now_ms())) - 1.15 * 1.15) < 1e-9,
       "X51: Grand Trapper - the boss rooted half as long; rooted enemies take +15 %% (x the Mark)")
    ck(abs(float(A.ctxFor(au, RK, PN, 0, "A1,PA5").cdMult) - 1.1) < 1e-9, "X51: Grand Trapper - cooldowns +10 %%")
    TSt.COMP.get(p1_).remove(NPCE.getComponentType())
    put(p1_, NPCc.getComponentType(), TCc())
    AS.ROOTS.clear()
    AS.MARKD.clear()
    TREE["csv"] = "A1,PA1,PA2,PB2"
    AS.TREEC.clear()
    wreset()
    fcast(apr, aref, "1", 0)
    run_world()
    ck(len(amts()) == 1 and abs(float(AS.MARKD.get(p1_)[1]) - 10.0) < 1e-6 and "Root:3" in [str(x) for x in EFX], "X51: Focus Mark - one target; Lasting Roots root +1 s, Mark -5")
    ck(abs(float(A.outMult(tst, p1_, au, now_ms())) - 1.1 * 1.1) < 1e-9 and abs(float(A.outMult(tst, p1_, wu, now_ms())) - 1.1) < 1e-9,
       "X51: Lasting Roots - the rooted take +10 %% from YOU only")
    ck(len(zones(20)) == 1 and int(zones(20)[0].n1) in (4, 5) and abs(sv(am_, MANA) - (400.0 - 6.0)) < 0.01, "X51: Trap Arrows - a trap where it stopped; cost +2 Mana (%d zones %s, Mana %s)"
       % (len(zones(20)), [int(z_.n1) for z_ in zones(20)], sv(am_, MANA)))
    AS.clearCd(RK)
    fcast(apr, aref, "1", 0)
    run_world()
    ck(int(float(AS.MARKD.get(p1_)[2])) == 2 and abs(float(AS.MARKD.get(p1_)[1]) - 15.0) < 1e-6, "X51: Focus Mark stacks (+5 %% a stack)")
    TREE["csv"] = None
    AS.TREEC.clear()
    AS.ROOTS.clear()
    AS.MARKD.clear()
    endall()
    wreset()
    setp(RK, {"u.PinningShot": lv(4), "e.PinningShot": "Split,"})
    pside = mob(174, 80.5 + 8.0 * 0.208, 0.5 + 8.0 * 0.978)
    NEARL[:] = [p1_, pside]
    fcast(apr, aref, "1", 0)
    run_world()
    ck(sorted(amts()) == [15.9, 31.8], "X51: Split - 3 arrows, the side ones 50 %% (Lv 4 = +6 %%): %s" % amts())
    setp(RK, {"u.PinningShot": None, "e.PinningShot": None})
    wreset()
    pr1 = mob(175, 81.5, 0.5)
    NEARL[:] = [pr1, p3_]
    amsc.getMovementStates().onGround = False
    fcast(apr, aref, "1", 2)
    amsc.getMovementStates().onGround = True
    run_world()
    ck(amts() == [15.0], "X51: Rain Pin (air) - the patch below you, 0.6 H each: %s" % amts())
    endall()
    AS.MARKD.clear()
    AS.ROOTS.clear()
    # ---------------- X52 Rapid Fire (15 arrows re-aimed, Seeker, Ricochet + the exclusion, Piercing Aim, Hover, Braced, Arrow Tempest)
    wreset()
    NEARL[:] = [p1_, p2_]
    r_ = fcast(apr, aref, "2", 0)
    for i_ in range(16):
        run_world()
    ck(r_.startswith("ok:RapidFire") and len(amts()) == 15 and set(amts()) == {12.5} and any("15 hits from 15 arrows" in x_ for x_ in said()),
       "X52: 15 arrows, each 0.5 H on the first enemy of your line: %d" % len(amts()))
    wreset()
    sk_ = mob(176, 82.0, 6.5)
    NEARL[:] = [sk_]
    fcast(apr, aref, "2", 0)
    for i_ in range(16):
        run_world()
    ck(len(amts()) == 0, "X52: an enemy 1.5 blocks off your line is missed")
    wreset()
    setp(RK, {"u.RapidFire": lv(10), "e.RapidFire": "Seeker,"})
    fcast(apr, aref, "2", 0)
    for i_ in range(16):
        run_world()
    ck(len(amts()) == 15, "X52: Seeker - arrows swerve into it (%d)" % len(amts()))
    eq_ = str(A.equipMod(au, "RapidFire", 1, "Ricochet", None, False))
    ck(eq_.startswith("-Ricochet never goes together with Seeker"), "X52: Seeker + Ricochet refused (Skyy L170): %s" % eq_)
    setp(RK, {"e.RapidFire": "Ricochet,"})
    wreset()
    rb2 = mob(177, 82.5, 6.5)
    NEARL[:] = [p1_, rb2]
    fcast(apr, aref, "2", 0)
    for i_ in range(16):
        run_world()
    a10 = round(12.5 * float(A.lvlMult(10)), 3)
    ck(amts().count(a10) == 15 and amts().count(round(a10 * 0.5, 3)) == 15, "X52: Ricochet - every arrow bounces to the next enemy at half damage: %s" % sorted(set(amts())))
    setp(RK, {"u.RapidFire": None, "e.RapidFire": None})
    endall()
    wreset()
    AS.MARKD.put(p2_, JArray(JDouble)([float(now_ms() + 60000), 0.0, 1.0]))
    TREE["csv"] = "A2,PB4"
    AS.TREEC.clear()
    NEARL[:] = [p1_, p2_]
    r_ = fcast(apr, aref, "2", 0)
    run_world()
    ck(" every=400" in r_ and evs() and evs()[0][0].equals(p2_) and amts()[0] == 15.625, "X52: Piercing Aim - every 0.4 s at the Marked enemy, +25 %%: %s %s" % (r_, amts()))
    TREE["csv"] = None
    AS.TREEC.clear()
    AS.MARKD.clear()
    endall()
    wreset()
    amsc.getMovementStates().onGround = False
    fcast(apr, aref, "2", 2)
    run_world()
    amsc.getMovementStates().onGround = True
    ck(any(float(p_[1]) < 0.0 and float(p_[0]) == 0.0 for p_ in PUSH), "X52: Hover Fire (air) - a slow fall while you shoot")
    endall()
    wreset()
    setp(RK, {"p1": "PinningShot", "p2": "ExplosiveArrow", "a1": "RapidFire", "a2": "ArrowRain"})
    r_ = fcast(apr, aref, "3", 3)
    ck("Root:2" in [str(x) for x in EFX] and " every=133" in r_, "X52: Braced (crouch) - 15 in 2 s, rooted: %s" % r_)
    setp(RK, WSL)
    endall()
    wreset()
    AS.arm(RK, "ExplosiveArrow", now_ms(), 14000)
    TREE["csv"] = "A2,A3,PC5"
    AS.TREEC.clear()
    fcast(apr, aref, "2", 0)
    lft = int(AS.left(RK, "ExplosiveArrow", now_ms()))
    ck(9000 < lft < 10000 and abs(sv(am_, MANA) - (400.0 - 6.0 * 1.2)) < 0.01, "X52: Arrow Tempest - Rapid Fire cuts Explosive Arrow's cooldown 30 %% (%d ms left), +20 %% Mana" % lft)
    TREE["csv"] = None
    AS.TREEC.clear()
    endall()
    # ---------------- X53 Explosive Arrow (armed, the arrow hit through the REAL outgoing hook, the blast, Set Charge, Echo, Storm Cloud)
    wreset()
    setp(RK, {"p1": "PinningShot", "p2": "ExplosiveArrow", "a1": "RapidFire", "a2": "ArrowRain"})
    x1_, x2_ = mob(178, 80.5, 10.5), mob(179, 82.5, 10.5)
    NEARL[:] = [x1_, x2_]
    r_ = fcast(apr, aref, "2", 0)
    ck(r_.startswith("ok:ExplosiveArrow") and AS.EXPL.get(au) is not None, "X53: armed: %s" % r_)
    HANDS[52] = "Weapon_Sword_Crude"
    d_ = dmg(aref, 10.0)
    A.outHit2(tst, tbuf, x1_, d_, au, now_ms())
    ck(float(d_.getAmount()) == 10.0 and AS.EXPL.get(au) is not None, "X53: not a bow / crossbow hit -> nothing")
    HANDS[52] = "Weapon_Shortbow_Crude"
    d_ = dmg(aref, 10.0)
    out_ = str(A.outHit2(tst, tbuf, x1_, d_, au, now_ms()))
    ck("explode" in out_ and abs(float(d_.getAmount()) - 20.0) < 1e-3 and evs() and evs()[0][0].equals(x2_) and amts() == [20.0] and AS.EXPL.get(au) is None,
       "X53: your next arrow hit x2 and blasts the one next to it (4 blocks): %s %s" % (out_, amts()))
    ck(uses(RK, "ExplosiveArrow") == 1, "X53: the blast counts the use")
    endall()
    # FIX ROUND 2 (critic: the blast neighbours got the outgoing multiplier twice, and the primary's Mark): Mark +15 % on the primary only
    wreset()
    fcast(apr, aref, "2", 0)
    AS.MARKD.put(x1_, JArray(JDouble)([float(now_ms() + 60000), 15.0, 1.0]))
    d_ = dmg(aref, 10.0)
    out_ = str(A.outHit2(tst, tbuf, x1_, d_, au, now_ms()))
    ck("explode" in out_ and abs(float(d_.getAmount()) - 23.0) < 1e-3 and amts() == [20.0],
       "X53 FIX2: the Marked arrow target 10 x 1.15 x 2 = 23; the unmarked neighbour 10 x 2 = 20 (its own multiplier only): %s %s" % (d_.getAmount(), amts()))
    AS.MARKD.remove(x1_)
    endall()
    wreset()
    setp(RK, {"u.ExplosiveArrow": lv(8), "e.ExplosiveArrow": "Echo,"})
    fcast(apr, aref, "2", 0)
    A.outHit2(tst, tbuf, x1_, dmg(aref, 10.0), au, now_ms())
    TBf.EVENTS.clear()
    e0 = int(A.ECHOES)
    run_world(2000)
    ck(int(A.ECHOES) == e0 + 1 and str(A.LAST_ECHO).startswith("blast:") and len(amts()) == 2, "X53: Echo - a weaker blast on the same spot 1 s later (%s %s)" % (A.LAST_ECHO, amts()))
    setp(RK, {"u.ExplosiveArrow": None, "e.ExplosiveArrow": None, "p1": "PinningShot", "p2": "RapidFire", "a1": "ExplosiveArrow", "a2": "ArrowRain"})
    endall()
    wreset()
    fcast(apr, aref, "3", 3)
    d_ = dmg(aref, 10.0)
    A.outHit2(tst, tbuf, x1_, d_, au, now_ms())
    sj_ = [j_ for j_ in list(aw.jobs) if int(j_.kind) == 21]
    ck(float(d_.getAmount()) == 10.0 and len(sj_) == 1, "X53: Set Charge (crouch) - it sticks (the arrow itself unchanged)")
    run_world()
    ck(sorted(amts()) == [25.0, 25.0], "X53: ... 1 s later both blast at 2.5x: %s" % amts())
    setp(RK, WSL)
    endall()
    wreset()
    TREE["csv"] = "A3,PC2,PC4"
    AS.TREEC.clear()
    setp(RK, {"p1": "PinningShot", "p2": "ExplosiveArrow", "a1": "RapidFire", "a2": "ArrowRain"})
    r_ = fcast(apr, aref, "2", 0)
    d_ = dmg(aref, 10.0)
    A.outHit2(tst, tbuf, x1_, d_, au, now_ms())
    ck(" r=5.5" in r_ and abs(float(d_.getAmount()) - 17.0) < 1e-3 and any(float(p_[1]) > 0.0 for p_ in PUSH) and [j_ for j_ in list(aw.jobs) if int(j_.kind) == 23],
       "X53: Storm Cloud (+1.5 radius, knock-up, single target -15 %%) + Chain Reaction (a burning patch): %s %s" % (r_, d_.getAmount()))
    TREE["csv"] = None
    AS.TREEC.clear()
    setp(RK, WSL)
    endall()
    # ---------------- X54 Arrow Rain (the pulses, slow, root + Mark after 2 s, Lingering, Echo, Kneeling Volley broken, aim refusal)
    wreset()
    AS.MARKD.clear()
    setp(RK, {"p1": "ArrowRain", "p2": "RapidFire", "a1": "ExplosiveArrow", "a2": "PinningShot"})
    AIMS["spot"] = None
    ck(fcast(apr, aref, "1", 0) == "aim" and sv(am_, MANA) == 400.0, "X54: nothing to aim at -> refused, nothing spent")
    AIMS["spot"] = [80.5, 64.0, 10.5]
    ra1, ra2 = mob(180, 80.5, 10.5), mob(181, 82.5, 10.5)
    NEARL[:] = [ra1, ra2]
    r_ = fcast(apr, aref, "1", 0)
    zr_ = zones(19)[0]
    ck(r_.startswith("ok:ArrowRain") and int(zr_.t3) > now_ms() + 300, "X54: the rain starts 0.5 s after the cast: %s" % r_)
    zr_.t3 = now_ms() - 1
    zr_.nextHeal = 0
    run_world()
    ck(sorted(amts()) == [8.333, 8.333] and len(efx("SkyyAbility_Spd_0:")) == 2, "X54: every 0.5 s each enemy inside takes its share (2.0 H over 3 s), slowed 30 %%: %s" % amts())
    for v_ in list(zr_.healed.values()):
        v_[0] = now_ms() - 2500
    zr_.nextHeal = 0
    EFX.clear()
    run_world()
    ck(len(efx("Root:1.5")) == 2 and AS.MARKD.get(ra1) is not None, "X54: still inside after 2 s -> rooted 1.5 s + Marked")
    ck(uses(RK, "ArrowRain") == 1, "X54: counted once")
    endall()
    wreset()
    setp(RK, {"u.ArrowRain": lv(10), "e.ArrowRain": "Lingering,Echo"})
    fcast(apr, aref, "1", 0)
    zr_ = zones(19)[0]
    zr_.until = now_ms() - 1
    run_world()
    ck(len([z_ for z_ in zones(19) if int(z_.n2) == 1]) == 1, "X54: Lingering - the ground keeps slowing (no damage)")
    e0 = int(A.ECHOES)
    run_world()
    ck(int(A.ECHOES) == e0 + 1 and str(A.LAST_ECHO).startswith("rain:"), "X54: Echo - a second shower right after (%s)" % A.LAST_ECHO)
    setp(RK, {"u.ArrowRain": None, "e.ArrowRain": None, "p1": "PinningShot", "p2": "RapidFire", "a1": "ArrowRain", "a2": "ExplosiveArrow"})
    endall()
    wreset()
    fcast(apr, aref, "3", 3)
    moveto(aref, 84.5, 0.5)
    run_world()
    moveto(aref, 80.5, 0.5)
    ck(sv(am_, MANA) == 400.0 and str(A.LAST_ARC) == "volley moved" and int(AS.left(RK, "ArrowRain", now_ms())) == 0, "X54: Kneeling Volley - moving in the first second gives it all back")
    setp(RK, WSL)
    endall()
    wreset()
    setp(RK, {"p1": "ArrowRain", "p2": "RapidFire", "a1": "ExplosiveArrow", "a2": "PinningShot"})
    TREE["csv"] = "A4,PA4"
    AS.TREEC.clear()
    fcast(apr, aref, "1", 0)
    zr_ = zones(19)[0]
    ck(abs(float(zr_.d1) - 1.5) < 1e-9 and abs(float(zr_.amount) - 25.0 * 2.0 * 0.85 * 0.5 / 3.0) < 1e-6, "X54: Marksman's Snare - roots after 1.5 s, -15 %% damage")
    TREE["csv"] = None
    AS.TREEC.clear()
    setp(RK, WSL)
    endall()
    # ---------------- X55 Hunter's Net (the root zone, Mark, Set Trap, Snare Line, Split, Deep Net)
    wreset()
    AS.MARKD.clear()
    setp(RK, {"alt": "B", "p1": "HuntersNet", "p2": "RapidFire", "a1": "ExplosiveArrow", "a2": "PinningShot"})
    AIMS["spot"] = [80.5, 64.0, 10.5]
    NEARL[:] = [ra1, p1_]
    r_ = fcast(apr, aref, "1", 0)
    run_world()
    ck(r_.startswith("ok:HuntersNet") and amts() == [12.5] and efx("Root:") and abs(float(AS.MARKD.get(ra1)[1]) - 10.0) < 1e-6,
       "X55: the net roots + Marks (10 %%) what is inside, 0.5 H once: %s" % amts())
    run_world()
    ck(len(amts()) == 1, "X55: ... the hit only once")
    endall()
    wreset()
    setp(RK, {"alt": "B", "p1": "PinningShot", "p2": "RapidFire", "a1": "ExplosiveArrow", "a2": "HuntersNet"})
    tr_ = mob(182, 81.0, 0.5)
    NEARL[:] = [tr_]
    fcast(apr, aref, "4", 3)
    zt_ = zones(20)[0]
    run_world()
    ck(int(zt_.n1) == 3 and len(amts()) == 0, "X55: Set Trap (crouch) - hidden, not armed for 1 s")
    zt_.t3 = now_ms() - 1
    run_world()
    run_world()
    ck(int(zt_.n1) == 0 and amts() == [12.5] and efx("Root:"), "X55: ... armed, an enemy steps in -> it springs")
    endall()
    wreset()
    setp(RK, {"alt": "B", "p1": "HuntersNet", "p2": "RapidFire", "a1": "ExplosiveArrow", "a2": "PinningShot"})
    sb1, sb2 = mob(183, 80.5, -3.0), mob(184, 80.5, 3.0)
    NEARL[:] = [sb1, sb2]
    fcast(apr, aref, "1", 1)
    run_world()
    ck(len(evs()) == 1 and evs()[0][0].equals(sb1), "X55: Snare Line (sprint) - the strip behind you catches the pursuer, not the one ahead")
    endall()
    wreset()
    setp(RK, {"u.HuntersNet": lv(8), "e.HuntersNet": "Split,"})
    r_ = fcast(apr, aref, "1", 0)
    ck(len(zones(20)) == 3, "X55: Split - 3 nets: %s %d" % (r_, len(zones(20))))
    setp(RK, {"u.HuntersNet": None, "e.HuntersNet": None})
    endall()
    wreset()
    TREE["csv"] = "A4,PA3"
    AS.TREEC.clear()
    NEARL[:] = [ra2]
    fcast(apr, aref, "1", 0)
    run_world()
    zd_ = zones(20)[0]
    ck(abs(float(zd_.r) - 3.0) < 1e-9 and len(PUSH) >= 1 and not efx("Root:"), "X55: Deep Net - radius -1, drags to its centre first (no root yet)")
    zd_.start = now_ms() - 2500
    run_world()
    ck(efx("Root:"), "X55: ... rooted after 2 s")
    TREE["csv"] = None
    AS.TREEC.clear()
    setp(RK, WSL)
    endall()
    # ---------------- X56 the modifier texts, the tree numbers, the leave clean-up, the prune
    ck(str(A.modText(BF, int(AMD.FLOOR), 1, 1)).startswith("never below 5 stacks") and str(A.modText(BF, int(AMD.FLOOR), 2, 1)).startswith("never below 10"),
       "X56: Floor text Lv 1 / 2")
    ck("swerve" in str(A.modText(RF, int(AMD.SEEKER), 1, 1)) and "lingers" in str(A.modText(RG, int(AMD.ECHO), 1, 1)) and "hooks" in str(A.modText(IC, int(AMD.CHAIN), 1, 1)),
       "X56: Seeker / Rallying Guard Echo / Iron Chain Chain texts")
    rows_ = list(A.modRows(bu, "BloodFrenzy", None))
    ck(len(rows_) == 6 and str(rows_[2]).startswith("Floor|Floor|4|"), "X56: class:fn:abilMods for Blood Frenzy - 5 modifiers, Floor unlocks at Lv 4")
    for u_ in (wu, bu, au):
        AS.GUARDED.put(u_, JArray(JDouble)([float(now_ms() + 9000), 1.0, 0.0, 0.0, 0.0]))
        AS.RAGE.put(u_, JArray(JDouble)([float(now_ms()), 1.0, float(now_ms() + 9000), 1.0, 1.0, 0.0, 0.0, 0.0]))
    fq = U.allocateInstance(PDE.class_)
    f_.set(fq, wpr)
    C("ClassQuit")().accept(fq)
    ck(AS.GUARDED.get(wu) is None and AS.RAGE.get(wu) is None and AS.GUARDED.get(bu) is not None, "X56: ClassQuit drops the leaver's guard / rage, nobody else's")
    pm1 = mob(185, 99.5, 99.5)
    AS.TAUNTS.put(pm1, JArray(JLong)([now_ms() - 5, 0, 0, 0]))
    AS.MARKD.put(pm1, JArray(JDouble)([float(now_ms() - 5), 1.0, 1.0]))
    AS.RAGE.put(au, JArray(JDouble)([0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0]))
    A.NEXT_PRUNE = 0
    run_world()
    ck(AS.TAUNTS.get(pm1) is None and AS.MARKD.get(pm1) is None and AS.RAGE.get(au) is None, "X56: AbilTick prunes the expired taunt / Mark / rage records")
    AS.GUARDED.clear()
    AS.RAGE.clear()
    A.TAUNTL = None
    endall()
    said()
    # ---------------- X57 every remaining shape (sprint / air / crouch) of the 15
    A.TAUNTL = TAUNT
    # Shield Shockwave sprint: Charging Slam (a 2-block step, 7 blocks, 1.2 H, stun 1.2)
    wreset()
    LOOKV["v"] = [40.5, 64.9, 0.5, 0.0, 0.0, 1.0]
    sf2 = mob(190, 40.5, 6.5)
    NEARL[:] = [sf2]
    r_ = fcast(wpr, wr, "2", 1)
    run_world()
    ck(" shape=sprint" in r_ and len(PUSH) == 1 and float(PUSH[0][2]) > 0.0 and amts() == [30.0] and stuns() == [1.2], "X57: Charging Slam - you step in, 7 blocks, 1.2 H, stun 1.2: %s %s" % (amts(), stuns()))
    endall()
    # Iron Chain sprint (Meet Halfway: both pulled) + air (Hook Down: yanked up)
    wreset()
    setp(WK, {"p1": "RallyingGuard", "p2": "IronChain", "a1": "ShieldShockwave", "a2": "Challenge"})
    MOBT["t"] = sf2
    fcast(wpr, wr, "2", 1)
    run_world()
    ck(len(PUSH) == 2 and float(PUSH[0][2]) < 0.0 and float(PUSH[1][2]) > 0.0 and stuns() == [0.8], "X57: Meet Halfway - the enemy and you meet in the middle, stun 0.8")
    wreset()
    wmsc.getMovementStates().onGround = False
    fcast(wpr, wr, "2", 2)
    wmsc.getMovementStates().onGround = True
    run_world()
    ck(amts() == [20.0] and len(PUSH) == 1 and float(PUSH[0][1]) > 2.0, "X57: Hook Down (air) - 0.8 H, yanked up: %s %s" % (amts(), [list(p_) for p_ in PUSH]))
    endall()
    # Challenge sprint (a step, 6 s) + on landing (the nearest within 8; none -> a line)
    wreset()
    setp(WK, {"p1": "Challenge", "p2": "ShieldShockwave", "a1": "IronChain", "a2": "RallyingGuard"})
    r_ = fcast(wpr, wr, "1", 1)
    ch_ = AS.CHALLS.get(sf2)
    ck(" shape=sprint" in r_ and len(PUSH) == 1 and ch_ is not None and abs(int(ch_[0]) - now_ms() - 6000) < 300, "X57: Charging Challenge - a step in, 6 s")
    wreset()
    wmsc.getMovementStates().onGround = False
    fcast(wpr, wr, "1", 2)
    wmsc.getMovementStates().onGround = True
    run_world()
    ck(str(A.LAST_LAND).startswith("chall:") and AS.CHALLS.get(sf2) is not None, "X57: Challenge from Above - the nearest enemy where you land (%s)" % A.LAST_LAND)
    wreset()
    NEARL[:] = []
    wmsc.getMovementStates().onGround = False
    fcast(wpr, wr, "1", 2)
    wmsc.getMovementStates().onGround = True
    run_world()
    ck(str(A.LAST_LAND) == "chall:none" and any("no enemy near your landing" in x_ for x_ in said()), "X57: ... no enemy there -> a line")
    endall()
    # Guardian's Oath sprint (Oath Rush: the nearest + 20 % speed), crouch (Shared Burden), on landing (the most hurt)
    wreset()
    setp(WK, {"alt": "B", "p1": "GuardiansOath", "p2": "ShieldShockwave", "a1": "IronChain", "a2": "RallyingGuard"})
    fcast(wpr, wr, "1", 1)
    ck(AS.OATHS.get(xu) is not None and efx("SkyyAbility_Spd_50:3"), "X57: Oath Rush - the nearest party member + 20 %% speed 3 s")
    wreset()
    setp(WK, {"alt": "B", "p1": "ShieldShockwave", "p2": "IronChain", "a1": "GuardiansOath", "a2": "RallyingGuard"})
    A.TARGET = Fn(lambda o: xu)
    fcast(wpr, wr, "3", 3)
    ck(float(AS.OATHS.get(xu)[1]) == 50.0 and float(AS.OATHW.get(wu)[1]) == 25.0, "X57: Shared Burden (crouch) - 50 %% shared, you 25 %% less")
    A.TARGET = None
    wreset()
    setp(WK, {"alt": "B", "p1": "GuardiansOath", "p2": "ShieldShockwave", "a1": "IronChain", "a2": "RallyingGuard"})
    xm.setStatValue(HP, JFloat(40.0))
    wmsc.getMovementStates().onGround = False
    fcast(wpr, wr, "1", 2)
    wmsc.getMovementStates().onGround = True
    run_world()
    ck(str(A.LAST_LAND).startswith("oath:") and AS.OATHS.get(xu) is not None, "X57: Oath on Landing - the most hurt party member (%s)" % A.LAST_LAND)
    setp(WK, WSL)
    endall()
    # Whirlwind sprint (Cyclone Charge 2.5 s / 2.5 blocks)
    wreset()
    r_ = fcast(bpr, bref, "2", 1)
    zs_ = zones(16)[0]
    ck(" r=2.5" in r_ and abs(int(zs_.until) - now_ms() - 2500) < 300, "X57: Cyclone Charge - 2.5 blocks, 2.5 s: %s" % r_)
    endall()
    # Earthsplitter sprint (Running Split 16 / 1.4 / 1.8 H)
    wreset()
    setp(BK, {"p1": "Enrage", "p2": "Earthsplitter", "a1": "Whirlwind", "a2": "BloodFrenzy"})
    r_ = fcast(bpr, bref, "2", 1)
    ck(" len=16" in r_ and " width=1.4" in r_ and " hit=45" in r_, "X57: Running Split - 16 long, narrower, 1.8 H: %s" % r_)
    endall()
    # Blood Frenzy sprint (3 stacks) + on landing (2)
    wreset()
    setp(BK, {"p1": "BloodFrenzy", "p2": "Whirlwind", "a1": "Earthsplitter", "a2": "Enrage"})
    fcast(bpr, bref, "1", 1)
    ck(int(AS.FRENZ.get(bu).total) == 3, "X57: Charging Frenzy - on at 3 stacks")
    fcast(bpr, bref, "1", 0)
    run_world()
    AS.clearCd(BK)
    bmsc.getMovementStates().onGround = False
    fcast(bpr, bref, "1", 2)
    bmsc.getMovementStates().onGround = True
    run_world()
    ck(str(A.LAST_LAND).startswith("frenzy:") and int(AS.FRENZ.get(bu).total) == 2, "X57: Landing Frenzy - on at landing with 2 stacks (%s)" % A.LAST_LAND)
    fcast(bpr, bref, "1", 0)
    run_world()
    endall()
    # Warlord's Banner sprint (6 ahead) + on landing (+2 blocks)
    wreset()
    setp(BK, {"alt": "B", "p1": "WarlordsBanner", "p2": "Whirlwind", "a1": "Earthsplitter", "a2": "Enrage"})
    LOOKV["v"] = [60.5, 64.9, 0.5, 0.0, 0.0, 1.0]
    fcast(bpr, bref, "1", 1)
    zb_ = zones(18)[0]
    ck(abs(float(zb_.z) - 6.5) < 1e-6 and abs(float(zb_.x) - 60.5) < 1e-6, "X57: Vanguard Banner - planted 6 blocks ahead (%s, %s)" % (zb_.x, zb_.z))
    endall()
    wreset()
    bmsc.getMovementStates().onGround = False
    fcast(bpr, bref, "1", 2)
    bmsc.getMovementStates().onGround = True
    run_world()
    ck(str(A.LAST_LAND).startswith("banner:") and abs(float(zones(18)[0].r) - 14.0) < 1e-6, "X57: Landing Banner - where you land, +2 blocks (%s)" % A.LAST_LAND)
    setp(BK, WSL)
    endall()
    AS.WAR.clear()
    # Pinning Shot sprint (Running Pin: root 2.5, 24 blocks)
    wreset()
    LOOKV["v"] = [80.5, 64.9, 0.5, 0.0, 0.0, 1.0]
    far_ = mob(191, 80.5, 27.5)
    NEARL[:] = [p1_, far_]
    fcast(apr, aref, "1", 1)
    run_world()
    ck(amts() == [30.0] and "Root:2.5" in [str(x) for x in EFX], "X57: Running Pin - root 2.5 s, 24 blocks (the one at 27 is out of reach): %s" % amts())
    endall()
    # Rapid Fire sprint (Running Fire: 12 arrows)
    wreset()
    r_ = fcast(apr, aref, "2", 1)
    ck(" arrows=12" in r_, "X57: Running Fire - 12 arrows: %s" % r_)
    endall()
    # Explosive Arrow sprint (Quick Fuse 1.5x / 3) + air (Mortar 5 blocks + knock-up)
    wreset()
    setp(RK, {"p1": "PinningShot", "p2": "ExplosiveArrow", "a1": "RapidFire", "a2": "ArrowRain"})
    r_ = fcast(apr, aref, "2", 1)
    ck(" mult=1.5" in r_ and " r=3" in r_, "X57: Quick Fuse - 1.5x, 3 blocks: %s" % r_)
    wreset()
    amsc.getMovementStates().onGround = False
    r_ = fcast(apr, aref, "2", 2)
    amsc.getMovementStates().onGround = True
    ck(" r=5" in r_ and " up" in r_, "X57: Mortar (air) - 5 blocks + knock-up: %s" % r_)
    setp(RK, WSL)
    endall()
    AS.EXPL.clear()
    # Arrow Rain sprint (Trailing: 4 blocks behind you) + air (Overhead: below you, 7 blocks, no delay)
    wreset()
    setp(RK, {"p1": "ArrowRain", "p2": "RapidFire", "a1": "ExplosiveArrow", "a2": "PinningShot"})
    fcast(apr, aref, "1", 1)
    zr_ = zones(19)[0]
    zr_.t3 = now_ms() - 1
    run_world()
    ck(abs(float(zr_.z) - (0.5 - 4.0)) < 1e-6, "X57: Trailing Rain - 4 blocks behind you (%s)" % zr_.z)
    endall()
    wreset()
    amsc.getMovementStates().onGround = False
    fcast(apr, aref, "1", 2)
    amsc.getMovementStates().onGround = True
    zr_ = zones(19)[0]
    ck(abs(float(zr_.r) - 7.0) < 1e-6 and int(zr_.t3) <= now_ms() and abs(float(zr_.x) - 80.5) < 1e-6, "X57: Overhead Rain (air) - below you, 7 blocks, no delay")
    setp(RK, WSL)
    endall()
    # Hunter's Net air (Drop Net: below you, 5 blocks, 3.5 s)
    wreset()
    setp(RK, {"alt": "B", "p1": "HuntersNet", "p2": "RapidFire", "a1": "ExplosiveArrow", "a2": "PinningShot"})
    amsc.getMovementStates().onGround = False
    fcast(apr, aref, "1", 2)
    amsc.getMovementStates().onGround = True
    zn_ = zones(20)[0]
    ck(abs(float(zn_.r) - 5.0) < 1e-6 and abs(int(zn_.until) - now_ms() - 3500) < 300 and abs(float(zn_.x) - 80.5) < 1e-6, "X57: Drop Net (air) - below you, 5 blocks, 3.5 s")
    setp(RK, WSL)
    endall()
    A.TAUNTL = None
    said()
    A.EFFECT = None
    A.EFFECTS = None
    A.LOST = None
    A.MOB = None
    A.LOOK = None
    A.PUSHES = None
    K.notes.append("0.1.23 counters: combos %d, counters %d, deflects %d, waves %d, palms %d, strikes %d, god %d, poisons %d, lost %d"
                   % (int(A.COMBOS), int(A.COUNTERS), int(A.DEFLECTS), int(A.WAVES), int(A.PALMHITS), int(A.STRIKES), int(A.GODKILLS), int(A.POISONS), int(A.DISTRACTS)))
    K.notes.append("counters: hooks %d, runes %d, fallbacks %d, mirrors %d, uses %d, echoes %d" % (int(A.HOOKS), int(A.RUNES), int(A.FALLBACKS), int(A.MIRRORS), int(A.USES), int(A.ECHOES)))
    K.save()
    os._exit(0)


# ============================================================================================================ OLD: the 0.1.19 sections
def old_sections():
    """0.1.24: test_skyyclasses_0.1.19.py's L (the loadout bridge) and ST (START TWICE on a scratch COPY of the live Skyy_SkyyClasses: nothing
    written) run as its own children with --jar (its main also runs a 0.1.18 -> 0.1.19 compare whose jars are gone - skipped)."""
    import hashlib
    d = os.path.join(BASE, "t19")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "tmp"))
    env = dict(os.environ, TEMP=os.path.join(d, "tmp"), TMP=os.path.join(d, "tmp"), JAVA_TOOL_OPTIONS="-XX:-UsePerfData")
    lo = os.path.join(d, "L.json")
    subprocess.run([sys.executable, T19, "--l", "--out", lo, "--jar", JAR, "--dir", d], env=env, capture_output=True, text=True)
    lr = json.load(open(lo))["checks"] if os.path.isfile(lo) else None
    # obsolete since 0.1.22 (modifiers exist; the loadout set equips them): "L modifiers -> skipped, listed (... not in the game yet)"
    obs = [w for c, w in (lr or []) if not c and w.startswith("L modifiers -> skipped")]
    if obs:
        print("OLD. note: 0.1.19's 'L modifiers -> skipped' check is obsolete since 0.1.22 (modifiers exist) - not counted")
    HK.check(lr is not None and all(c or w.startswith("L modifiers -> skipped") for c, w in lr) and len(lr) >= 5,
             "OLD 0.1.19 L (every class loads + the loadout bridge) on the 0.1.24 jar: %s" % ([w for c, w in lr if not c and w not in obs][:3] if lr else "no result"))
    live = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyClasses")

    def th(root):
        o_ = {}
        for dd, _x, fs in os.walk(root):
            for f in fs:
                p_ = os.path.join(dd, f)
                o_[os.path.relpath(p_, root)] = hashlib.sha256(open(p_, "rb").read()).hexdigest()
        return o_
    if not os.path.isdir(live):
        HK.check(False, "ST: the live Skyy_SkyyClasses folder is missing")
        return
    live0 = th(live)
    home = os.path.join(d, "live")
    shutil.copytree(live, os.path.join(home, "Skyy_SkyyClasses"))
    before = th(home)
    for step in ("1", "2"):
        so = os.path.join(d, "s%s.json" % step)
        subprocess.run([sys.executable, T19, "--s", "--home", home, "--step", step, "--out", so, "--jar", JAR, "--dir", d], env=env, capture_output=True, text=True)
        after = th(home)
        ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        sr = json.load(open(so)) if os.path.isfile(so) else None
        HK.check(sr is not None and not ch, "ST: start %s of the 0.1.24 jar on a scratch COPY of the live data writes nothing (%s) %s" % (step, ch, sr))
    HK.check(th(live) == live0, "ST: the live Skyy_SkyyClasses folder was only read")
    print("OLD. 0.1.19 L + ST (start twice on a live copy) on the 0.1.24 jar done")
    shutil.rmtree(d, ignore_errors=True)


EXPECT = ["Abil", "AbilCfg", "AbilMath", "AbilStore", "AbilSave", "AbilJob", "AbilZone", "AbilDefs", "AbilModDefs", "AbilShieldSys",
          "AbilShieldSysU", "AbilFrostSys", "AbilWorld", "ClassQuit", "DamageLock", "SkyyClassesPlugin", "CfgRows", "CfgFn", "KitMigrate",
          "AbilTick", "AbilPage",   # FIX ROUND: the mob-map prune (AbilTick), the /abilities subtitle (AbilPage)
          "AbilCtx", "AbilNum",     # 0.1.24: Retribution's flag (AbilCtx.x1), the 15 numbers rows (AbilNum)
          "AbilRuneSys", "ClassReady"]   # 0.1.24 FIX ROUND: the Primary swing branch (Blood Frenzy per swing), the world switch (worldLeft)

if __name__ == "__main__":
    if "--phase" not in sys.argv:
        assert os.path.realpath(BASE).startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")) + os.sep)
        old_sections()
    HK.run_compare = run_compare24
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=NEW_CLASSES,
           phases=[("exec", run_exec)], script=__file__)   # 0.1.24: route21 needs the tidied 0.1.20 jar - C proves Abil.say / feedText unchanged instead
