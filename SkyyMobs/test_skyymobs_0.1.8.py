"""Harness for SkyyMobs 0.1.8 (pet kills count for the owner, SkyySacks 0.8.4 pair; tools/mobs_0_1_8_patch.py). Every 0.1.7 check
(the kill credit) + the 0.1.8 pet path.
Build first: python tools/mobs_0_1_8_patch.py && python SkyyMobs/build_skyymobs_0.1.8.py

    python SkyyMobs/test_skyymobs_0.1.8.py [--keep] [--dir <scratch>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.7 -> 0.1.8: exactly MobCredit (+ PET_HITS, + petOwner), CreditSys (~ handle), the plugin (~ setup: the ready
              line) and the version text (MobCfg file templates, the kit) differ; no class added; non-class files: manifest only
  X  exec     EXECUTED: MobCredit.credited (alive / killing blow / overkill / no record), hit + read + take, 8 slots (a 9th replaces the
              smallest only when bigger), ties (the first stays on top), prune (> 512 mobs, 5 minutes); mob:fn:credit with a UUID, a
              String, Object[] { id, TRUE } (take), bad arguments; CreditSys on a REAL engine Store (EntityStore.REGISTRY, real Refs, the
              real forEachChunk + CommandBuffer): its group = the Inspect damage group; a player's hit on an NPC is recorded with the
              victim's health after the hit (EntityStatMap / EntityStatValue stand-ins), a projectile (ProjectileSource = the shooter),
              the killing blow capped to the health left; cancelled / zero / NPC attacker / a player victim / no health map -> as stated
              0.1.8 PET: pets:fn:ownerOf (stand-in for SkyyPets 0.4): a pet's melee hit and its projectile count for the OWNER (UUID or
              String answer), a pet's killing blow makes the owner the killer, owner + pet damage add up for "top damager"; no key / an
              unknown creature / junk / a throwing key -> not counted; PET_HITS counts
  D  live     a scratch COPY of the live Skyy_SkyyMobs: MobCfg.load with 0.1.6 and 0.1.7, twice each: the same settings text, files
              byte-identical
  AA engine-access audit
Scratch: tools/dev/scratch/pickup2/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.1.8"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.7.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "pickup2", "mobs")))
PKG = "com.skyy.mobs."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyMobs")
EXPECT = {
    "MobCredit": ["+f PET_HITS", "+m petOwner", "~<clinit>"],   # <clinit> = PET_HITS' initialiser
    "CreditSys": ["~m handle"],
    "SkyyMobsPlugin": ["~m setup"],    # the ready line names the pet path
    "MobCfg": ["~m load", "~m reloadAll", "~m useDefaults"],   # only the version number in the two file templates
    "CfgFn": ["~m opExport"],          # the kit's version text
    "CfgRows": ["~<clinit>", "~m header"],   # the version text in the rows table + header
}
ADDED = []


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JString, JFloat, JInt, JImplements, JOverride, JObject, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    MC, Fn_, CS = JClass(PKG + "MobCredit"), JClass(PKG + "MobCreditFn"), JClass(PKG + "CreditSys")
    System, UUID = JClass("java.lang.System"), JClass("java.util.UUID")
    now = int(System.currentTimeMillis())

    # ------------------------------------------------------------------ credited (pure)
    K.eq(float(MC.credited(30.0, 70.0, 0.0, 100.0, -1.0)), 30.0, "CRED: the mob lives on -> the whole hit")
    K.eq(float(MC.credited(50.0, 0.0, 0.0, 100.0, 10.0)), 10.0, "CRED: killing blow of 50 on 10 left -> 10")
    K.eq(float(MC.credited(50.0, 0.0, 0.0, 40.0, -1.0)), 40.0, "CRED: killing blow with no record -> the full health")
    K.eq(float(MC.credited(0.0, 50.0, 0.0, 100.0, -1.0)), 0.0, "CRED: zero")
    K.eq(float(MC.credited(5.0, 0.0, 0.0, 100.0, 0.0)), 0.0, "CRED: already at 0 -> nothing")

    # ------------------------------------------------------------------ hit / read / take / slots / ties / prune
    MC.T.clear()
    m = "mob-1"
    MC.hit(m, "A", 30.0, 70.0, 0.0, 100.0, now)
    MC.hit(m, "B", 30.0, 40.0, 0.0, 100.0, now)
    r = MC.read(m, False)
    K.check(str(r[0]) == "A" and float(r[1]) == 30.0 and float(r[2]) == 60.0 and r[3] is None and int(r[4]) == 2,
            "HIT: a tie keeps the first on top; total 60; no killing blow yet: %s" % list(r))
    MC.hit(m, "B", 100.0, 0.0, 0.0, 100.0, now)
    r = MC.read(m, True)
    K.check(str(r[0]) == "B" and float(r[1]) == 70.0 and str(r[3]) == "B", "HIT: the overkill counts the 40 left -> B 70 on top, killing blow B: %s" % list(r))
    K.check(MC.read(m, False) is None, "HIT: take removed the entry")
    for i in range(9):
        MC.hit("mob-2", "P%d" % i, float(10 + i), 500.0, 0.0, 1000.0, now)
    c = MC.T.get("mob-2")
    names = sorted(str(x) for x in c.who if x is not None)
    K.check(int(c.n) == 8 and "P8" in names and "P0" not in names, "SLOTS: 8 players kept, the 9th (bigger) replaced the smallest: %s" % names)
    MC.hit("mob-2", "P9", 1.0, 499.0, 0.0, 1000.0, now)
    K.check("P9" not in [str(x) for x in MC.T.get("mob-2").who], "SLOTS: a 10th smaller hit does not replace anyone")
    MC.T.clear()
    for i in range(600):
        MC.hit("old-%d" % i, "A", 1.0, 5.0, 0.0, 10.0, now - 600000)
    MC.hit("new", "A", 1.0, 5.0, 0.0, 10.0, now)
    K.check(int(MC.T.size()) <= 513 and MC.T.containsKey("new"), "PRUNE: over 512 tracked mobs, entries older than 5 minutes go (%d left)" % int(MC.T.size()))
    MC.T.clear()

    # ------------------------------------------------------------------ mob:fn:credit
    u = UUID.randomUUID()
    MC.hit(str(u), "A", 5.0, 5.0, 0.0, 10.0, now)
    f = Fn_()
    K.check(f.apply(u) is not None and f.apply(JString(str(u))) is not None, "FN: UUID and String arguments read")
    arr = JArray(JClass("java.lang.Object"))([u, JClass("java.lang.Boolean").TRUE])
    K.check(f.apply(arr) is not None and f.apply(u) is None, "FN: Object[] { id, TRUE } takes the entry")
    K.check(f.apply(None) is None and f.apply(JClass("java.lang.Integer")(3)) is None and f.apply(JArray(JClass("java.lang.Object"))(0)) is None,
            "FN: bad arguments -> null, never throws")

    # ------------------------------------------------------------------ CreditSys on a real Store
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jfield(cls, name):
        cc = cls
        while cc is not None:
            try:
                f_ = cc.getDeclaredField(name)
                f_.setAccessible(True)
                return f_
            except Exception:
                cc = cc.getSuperclass()
        raise KeyError(name)

    @JImplements("java.util.function.Supplier")
    class Sup(object):
        @JOverride
        def get(self):
            return None
    ES = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    ERS, AR = JClass("com.hypixel.hytale.component.EmptyResourceStorage"), JClass("com.hypixel.hytale.component.AddReason")
    UUIDC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    PRF = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    NPCE = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DMG = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DENT = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    DPRJ = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource")
    EMc, DMc, UNc = (JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule"), JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageModule"),
                     JClass("com.hypixel.hytale.server.core.universe.Universe"))
    ESMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    # stand-in health: an EntityStatMap whose get(int) answers one EntityStatValue with set value / min / max
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    EP = "com.hypixel.hytale.server.core.modules.entitystats."
    sv = jp.makeClass(EP + "SkyyHkValue", jp.get(EP + "EntityStatValue"))
    for f_ in ("public float v;", "public float mn;", "public float mx;"):
        sv.addField(CtF.make(f_, sv))
    sv.addConstructor(CtC.make("public SkyyHkValue(float v, float mn, float mx) { super(); this.v = v; this.mn = mn; this.mx = mx; }", sv))
    for nm_, f_ in (("get", "v"), ("getMin", "mn"), ("getMax", "mx")):
        sv.addMethod(CtM.make("public float %s() { return this.%s; }" % (nm_, f_), sv))
    SV = JClass(sv.toClass(JClass(EP + "EntityStatValue").class_))
    sm = jp.makeClass(EP + "SkyyHkMap", jp.get(EP + "EntityStatMap"))
    sm.addField(CtF.make("public " + EP + "EntityStatValue h;", sm))
    sm.addConstructor(CtC.make("public SkyyHkMap() { super(); this.h = null; }", sm))
    sm.addMethod(CtM.make("public " + EP + "EntityStatValue get(int i) { return this.h; }", sm))
    SM = JClass(sm.toClass(ESM.class_))
    REG = ES.REGISTRY
    T_UU = REG.registerComponent(UUIDC, Sup())
    T_PR = REG.registerComponent(PRF, Sup())
    T_NPC = REG.registerComponent(NPCE, Sup())
    T_ESM = REG.registerComponent(ESM, Sup())
    G_INS = REG.registerSystemGroup()
    em = us.allocateInstance(EMc.class_)
    jfield(EMc.class_, "uuidComponentType").set(em, T_UU)
    ctm = JClass("java.util.HashMap")()
    ctm.put(NPCE.class_, T_NPC)
    jfield(EMc.class_, "classToComponentType").set(em, ctm)
    jfield(EMc.class_, "instance").set(None, em)
    dm = us.allocateInstance(DMc.class_)
    jfield(DMc.class_, "inspectDamageGroup").set(dm, G_INS)
    jfield(DMc.class_, "instance").set(None, dm)
    un = us.allocateInstance(UNc.class_)
    jfield(UNc.class_, "playerRefComponentType").set(un, T_PR)
    jfield(UNc.class_, "instance").set(None, un)
    esm = us.allocateInstance(ESMOD.class_)
    jfield(ESMOD.class_, "entityStatMapComponentType").set(esm, T_ESM)
    jfield(ESMOD.class_, "instance").set(None, esm)
    st = REG.addStore(ES(None), ERS.get())
    sysc = CS()
    K.check(sysc.getGroup().equals(G_INS), "SYS: CreditSys runs in the Inspect damage group (after ApplyDamage)")

    def add(comps):
        h = REG.newHolder()
        for ty, c in comps:
            h.addComponent(ty, c)
        return st.addEntity(h, AR.SPAWN)
    pu, nu, vu, wu = UUID.randomUUID(), UUID.randomUUID(), UUID.randomUUID(), UUID.randomUUID()
    pref = add([(T_PR, PRF(None, pu, "Ava", "en-US", None, None)), (T_UU, UUIDC(pu))])
    npcatt = add([(T_NPC, us.allocateInstance(NPCE.class_)), (T_UU, UUIDC(nu))])
    hmap = SM()
    victim = add([(T_NPC, us.allocateInstance(NPCE.class_)), (T_UU, UUIDC(vu)), (T_ESM, hmap)])
    pvict = add([(T_PR, PRF(None, wu, "Ben", "en-US", None, None)), (T_UU, UUIDC(wu))])
    bare = add([(T_NPC, us.allocateInstance(NPCE.class_)), (T_UU, UUIDC(UUID.randomUUID()))])

    def fire(target, src, amt, hp=None, cancel=False):
        if hp is not None:
            hmap.h = SV(JFloat(hp[0]), JFloat(hp[1]), JFloat(hp[2]))
        d = DMG(src, JInt(0), JFloat(amt))
        if cancel:
            d.setCancelled(True)

        @JImplements("java.util.function.BiConsumer")
        class C(object):
            @JOverride
            def accept(self, chunk, cb):
                for i_ in range(int(chunk.size())):
                    if chunk.getReferenceTo(i_).equals(target):
                        sysc.handle(JInt(i_), chunk, st, cb, d)
        st.forEachChunk(sysc.getQuery(), C())
    MC.T.clear()
    fire(victim, DENT(pref), 30.0, hp=(70.0, 0.0, 100.0))
    r = MC.read(str(vu), False)
    K.check(r is not None and str(r[0]) == str(pu) and float(r[1]) == 30.0, "SYS: a player's hit on an NPC is recorded (30): %s" % (list(r) if r else None))
    fire(victim, DPRJ(pref, npcatt), 20.0, hp=(50.0, 0.0, 100.0))
    K.eq(float(MC.read(str(vu), False)[1]), 50.0, "SYS: a projectile counts for its shooter")
    for what, args in (("cancelled", (DENT(pref), 10.0, (40.0, 0.0, 100.0), True)), ("zero", (DENT(pref), 0.0, (50.0, 0.0, 100.0), False)),
                       ("an NPC attacker", (DENT(npcatt), 10.0, (40.0, 0.0, 100.0), False))):
        fire(victim, args[0], args[1], hp=args[2], cancel=args[3])
        K.eq(float(MC.read(str(vu), False)[1]), 50.0, "SYS: %s hit -> not counted" % what)
    fire(victim, DENT(pref), 500.0, hp=(0.0, 0.0, 100.0))
    r = MC.read(str(vu), True)
    K.check(float(r[1]) == 100.0 and str(r[3]) == str(pu), "SYS: the killing blow counts the 50 left (total 100), blow = Ava: %s" % list(r))
    fire(pvict, DENT(pref), 10.0)
    K.check(MC.read(str(wu), False) is None, "SYS: a player victim is never tracked")
    fire(bare, DENT(pref), 7.0)
    rb = [x for x in MC.T.keySet()]
    K.check(len(rb) == 1 and float(MC.read(str(rb[0]), False)[1]) == 7.0, "SYS: no health map -> the hit counts as it is")

    # ------------------------------------------------------------------ 0.1.8 PET: a pet's hit counts for its owner (pets:fn:ownerOf)
    @JImplements("java.util.function.Function")
    class OwnerFn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    bridge = JClass(PKG + "MobLevel").bridge()
    bridge.remove("pets:fn:ownerOf")
    MC.T.clear()
    p0 = int(MC.PET_HITS.get())
    fire(victim, DENT(npcatt), 10.0, hp=(90.0, 0.0, 100.0))
    K.check(MC.read(str(vu), False) is None and int(MC.PET_HITS.get()) == p0, "PET: no pets:fn:ownerOf -> an NPC's hit is not counted (0.1.7)")
    PETS = {str(nu): pu}
    bridge.put("pets:fn:ownerOf", OwnerFn(lambda o: PETS.get(str(o))))
    fire(victim, DENT(npcatt), 10.0, hp=(80.0, 0.0, 100.0))
    r = MC.read(str(vu), False)
    K.check(r is not None and str(r[0]) == str(pu) and float(r[1]) == 10.0 and int(MC.PET_HITS.get()) == p0 + 1,
            "PET: the pet's melee hit counts for its OWNER (Ava 10): %s" % (list(r) if r else None))
    fire(victim, DPRJ(npcatt, pref), 15.0, hp=(65.0, 0.0, 100.0))
    K.eq(float(MC.read(str(vu), False)[1]), 25.0, "PET: the pet's projectile counts for its owner too")
    fire(victim, DENT(pref), 20.0, hp=(45.0, 0.0, 100.0))
    K.eq((str(MC.read(str(vu), False)[0]), float(MC.read(str(vu), False)[1])), (str(pu), 45.0), "PET: owner + pet damage add up (one player, 45)")
    fire(victim, DENT(pvict), 40.0, hp=(5.0, 0.0, 100.0))
    K.eq(str(MC.read(str(vu), False)[0]), str(pu), "PET: Ava (45 with her pet) stays top damager over Ben (40)")
    PETS[str(nu)] = JString(str(pu))     # a String answer works too
    fire(victim, DENT(npcatt), 99.0, hp=(0.0, 0.0, 100.0))
    r = MC.read(str(vu), True)
    K.check(str(r[3]) == str(pu) and float(r[1]) == 50.0, "PET: the pet's killing blow (5 left) makes its OWNER the killer: %s" % list(r))

    def boom(o):
        raise RuntimeError("bad key")
    for what, fn in (("an unknown creature", lambda o: None), ("a junk answer", lambda o: JString("not-a-uuid")),
                     ("an Integer answer", lambda o: JClass("java.lang.Integer")(4)), ("a throwing key", boom)):
        bridge.put("pets:fn:ownerOf", OwnerFn(fn))
        h0 = int(MC.PET_HITS.get())
        fire(victim, DENT(npcatt), 10.0, hp=(90.0, 0.0, 100.0))
        K.check(MC.read(str(vu), False) is None and int(MC.PET_HITS.get()) == h0, "PET: %s -> not counted (never the wrong player)" % what)
    bridge.put("pets:fn:ownerOf", OwnerFn(lambda o: pu))
    fire(pvict, DENT(npcatt), 10.0)
    K.check(MC.read(str(wu), False) is None, "PET: a pet hitting a PLAYER is never tracked")
    bridge.remove("pets:fn:ownerOf")
    K.check(MC.petOwner(None, npcatt) is None, "PET: petOwner without the key -> null at once (no component read)")
    MC.T.clear()
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)

    def loader_for(j):
        URL = JClass("java.net.URL")
        arr = JArray(URL)(1)
        arr[0] = JClass("java.io.File")(j).toURI().toURL()
        return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())
    before = HK.tree_hash(home)
    P = JClass("java.nio.file.Paths")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    seen = None
    for start in (1, 2):
        for j in (OLD_JAR, jar):
            Cfg = JClass(PKG + "MobCfg", loader=loader_for(j))
            Cfg.DIR = P.get(home)
            Cfg.FILE = P.get(os.path.join(home, "config.properties"))
            Cfg.BANDS = P.get(os.path.join(home, "bands.properties"))
            Cfg.load()
            got = (str(Cfg.strengthText()), str(Cfg.LOADED), bool(Cfg.ON))
            if seen is None:
                seen = got
            K.check(got == seen, "D start %d %s: the live settings load the same: %s" % (start, os.path.basename(j), got[:2]))
    K.eq(HK.tree_hash(home), before, "D the live copy's bytes are unchanged by the loads")
    K.save()


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
