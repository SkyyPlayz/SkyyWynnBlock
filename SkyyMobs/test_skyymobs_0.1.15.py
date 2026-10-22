"""Harness for SkyyMobs 0.1.15 (Balance P8b, the Combat tree's Spoils rows - tools/mobs_0_1_15_patch.py). Build first:
    python tools/mobs_0_1_15_patch.py && python SkyyMobs/build_skyymobs_0.1.15.py
    python SkyyMobs/test_skyymobs_0.1.15.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes (--out), line endings kept, two new classes, one new registerSystem
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.14 -> 0.1.15 (EXPECT below); added MobSpoils, SpoilsSys
  X  exec     EXECUTES MobSpoils: the 5 rows = tools/trees_v3_effects.py; ranks through a fake SkyyTrees tree:fn:level; vals at max (drop 10,
              coins 9, rare 3, bossRoll 9, dbl 6); THE RATE PROOF - 10,000 kills + 2,000 boss kills with every row maxed through the ROLLS
              seam (a drop list WITH gear in it): the extra rolls land on their % (drop / rare / double on every kill, Boss Hunter only on
              bosses), not one gear stack comes out, no gear:fn:* bridge is ever called (SkyyGear's UT meter + Mythic roll run on the
              kill, untouched); Coin Purse pays the mob's level through coins:fn:add on 9 %; Rare Drop picks the least-seen item; one roll
              per death; OFF / no SkyyTrees / no ranks = nothing; a Server Setup ceiling applies; loadV3 seeds trees.properties; SpoilsSys'
              dependencies (AFTER DropDeathItems, BEFORE CorpseRemoval) built from the real engine classes
  W  wiring   bytecode: SpoilsSys.tick waits for Role.hasDroppedDeathItems, one roll per mob, then extra / coins / spawn; spawn = the
              engine recipe (generateItemDrops + addEntities); systems() registers SpoilsSys only when both engine classes exist; setup:
              MobCfg.load -> loadV3 -> systems() -> reads(SYS_ON); shutdown reads(false)
  D  live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyMobs (the update chain + MobCfg.load + MobSpoils.loadV3):
              start 1 writes only the new trees.properties, start 2 nothing
  AA engine-access audit
  F  fixer    (critics 2026-10-22) the Spoils owner = the drop's owner as SkyySacks claims it (top damager in this world, else the killer;
              read before AND after SkyySacks' take); one roll per death holds 10 min past 512 entries (a 61 s old corpse never rolls
              again, an 11 min old entry is purged); the item-asset gear rule (weapon / armour / tool / durability / max stack 1) + a
              real ItemStack through clean()
NOT COVERED (UNVERIFIED in game): the extra stacks dropping beside a real dead mob and SkyySacks' auto-pickup claiming them.
Scratch: tools/dev/scratch/balp8bfix/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, subprocess, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.15"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp8bfix", "mobs")]
import skyybuild as B
import harness_kit as HK
import trees_v3_effects as V3E

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.14.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_15_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.14.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.mobs."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMobs")
ADDED = ["MobSpoils", "SpoilsSys"]
EXPECT = {
    "SkyyMobsPlugin": ["~m setup", "~m shutdown", "~m systems"],
    "MobCfg": ["~m load", "~m reloadAll", "~m useDefaults"],   # the version in the default files' first line (DEF_CFG / DEF_BANDS constants)
    "CfgFn": ["~m opExport"], "CfgRows": ["+f DL2", "~<clinit>", "~m defLines", "~m header"], "CfgFile": ["~<clinit>", "~m init"],
}
U = "00000000-0000-0000-0000-000000000115"


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.15 - build script') and g.count('VERSION = "0.1.15"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("),
          g.count("makeClass(") - o.count("makeClass(")), (1, 0, 2), "S one new system, no command, two new classes")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    S, SS = JClass(PKG + "MobSpoils"), JClass(PKG + "SpoilsSys")
    rows = V3E.rows("SkyyMobs")
    K.eq([str(x) for x in S.KEY], [V3E.key(e[0], e[1], e[2]) for e in rows], "X MobSpoils.KEY = trees_v3_effects' SkyyMobs rows")
    K.eq([float(S.v3per(i)) for i in range(5)], [e[5] for e in rows], "X per rank (whole %)")
    K.check(str(S.READS) == V3E.reads_csv("SkyyMobs"), "X tree:reads:SkyyMobs = the 5 keys")
    uu = JClass("java.util.UUID").fromString(U)
    RK = {}
    CN = {"gear": 0, "coins": [], "rolls": 0}

    @JImplements("java.util.function.Function")
    class Lvl(object):
        @JOverride
        def apply(self, a):
            return JClass("java.lang.Integer")(RK.get(str(a[1]), 0))

    @JImplements("java.util.function.Function")
    class Spy(object):
        @JOverride
        def apply(self, a):
            CN["gear"] += 1
            return None

    @JImplements("java.util.function.Function")
    class Coins(object):
        @JOverride
        def apply(self, a):
            CN["coins"].append((str(a[0]), int(a[1])))
            return JClass("java.lang.Long")(1)
    OA = JClass("java.lang.Object[]")
    Int = JClass("java.lang.Integer")
    import random
    rr = random.Random(7)
    SEQ = []

    @JImplements("java.util.function.Function")
    class Rolls(object):
        @JOverride
        def apply(self, dl):
            CN["rolls"] += 1
            l = JClass("java.util.ArrayList")()
            if SEQ:
                for it in SEQ.pop(0):
                    l.add(OA([JString(it[0]), Int(it[1])]))
                return l
            for it in [("Ingredient_Bone", 2), ("Ingredient_Hide_Light", 1), ("Weapon_Sword_Iron", 1), ("Armor_Iron_Head", 1), ("Tool_Pickaxe_Iron", 1),
                       ("Skyy_Unid_Bag_Rare", 1), ("Weapon_Shield_Iron", 1)] + ([("Rock_Gem_Ruby", 1)] if rr.random() < 0.1 else []):
                l.add(OA([JString(it[0]), Int(it[1])]))
            return l
    for g in ("gear:fn:box", "gear:fn:grant", "gear:fn:unid", "gear:fn:utdrop", "gear:fn:mythic"):
        br.put(g, Spy())
    S.ROLLS = Rolls()
    R = JClass("java.util.Random")
    # nothing without SkyyTrees / ranks
    S.C.clear()
    K.eq((int(S.extra(uu, "DL", True, R(1)).size()), int(S.coins(uu, 30, R(1)))), (0, 0), "X no SkyyTrees: no extra loot, no coins")
    br.put("tree:fn:level", Lvl())
    for e in rows:
        RK[V3E.key(e[0], e[1], e[2])] = V3E.maxrank(e[0], e[1], e[2])
    S.C.clear()
    K.eq([round(float(x), 6) for x in list(S.vals(uu))[1:]], [10.0, 9.0, 3.0, 9.0, 6.0], "X vals at max: drop 10, coins 9, rare 3, bossRoll 9, dbl 6")
    # THE RATE PROOF: 10,000 kills + 2,000 boss kills, every row maxed, a drop list with gear in it
    br.put("coins:fn:add", Coins())
    rnd = R(20261022)
    gear_out, items = 0, 0
    n0 = dict((k, int(getattr(S, k))) for k in ("N_DROP", "N_RARE", "N_BOSS", "N_DBL", "N_GEAR", "N_KILLS"))
    for i in range(10000):
        l = S.extra(uu, "DL_Mob", False, rnd)
        S.coins(uu, 30, rnd)
        for j in range(int(l.size())):
            if bool(S.gear(str(S.pid(l.get(j))))):
                gear_out += 1
            items += int(S.pn(l.get(j)))
    d = dict((k, int(getattr(S, k)) - n0[k]) for k in n0)
    nb0 = int(S.N_BOSS)
    for i in range(2000):
        l = S.extra(uu, "DL_Boss", True, rnd)
        for j in range(int(l.size())):
            if bool(S.gear(str(S.pid(l.get(j))))):
                gear_out += 1
    nb = int(S.N_BOSS) - nb0
    K.check(abs(d["N_DROP"] / 100.0 - 10.0) < 1.0 and abs(d["N_RARE"] / 100.0 - 3.0) < 0.6 and abs(d["N_DBL"] / 100.0 - 6.0) < 0.8 and d["N_BOSS"] == 0,
            "X 10,000 kills: Scavenger %.2f %% (10), Rare Drop %.2f %% (3), Lucky Kill %.2f %% (6), Boss Hunter 0 on plain mobs" % (d["N_DROP"] / 100.0, d["N_RARE"] / 100.0, d["N_DBL"] / 100.0))
    K.check(abs(nb / 20.0 - 9.0) < 1.6, "X 2,000 boss / mini boss kills: Boss Hunter %.2f %% (9)" % (nb / 20.0))
    K.check(abs(len(CN["coins"]) / 100.0 - 9.0) < 0.9 and all(c == (U, 30) for c in CN["coins"]), "X Coin Purse %.2f %% (9) of 10,000 kills, each the mob's level (30) to the killer" % (len(CN["coins"]) / 100.0))
    K.eq((gear_out, CN["gear"]), (0, 0), "X the UT / Mythic proof: 0 gear stacks out of %d extra items, 0 gear:fn:* calls (SkyyGear's UT meter + Mythic roll run on the kill only)" % items)
    K.check(d["N_GEAR"] > 1000, "X ... while the drop list offered gear %d times (all skipped)" % d["N_GEAR"])
    K.notes.append("X extra items a plain kill, every row maxed: %.3f (P5's UT 1-2 an hour + Mythic 1 per 5-10 boss kills are SkyyGear's kill rolls - unchanged)" % (items / 10000.0))
    # Rare Drop picks the least-seen item of 4 rolls
    SEQ[:] = [[("Ingredient_Bone", 2), ("Ingredient_Hide_Light", 1)], [("Ingredient_Bone", 2), ("Ingredient_Hide_Light", 1), ("Rock_Gem_Ruby", 1)],
              [("Ingredient_Bone", 2)], [("Ingredient_Bone", 2), ("Ingredient_Hide_Light", 1), ("Weapon_Sword_Iron", 1)]]
    K.eq(str(S.rarest("DL")), "Rock_Gem_Ruby", "X Rare Drop: the least-seen item of 4 rolls (Ruby 1 vs Hide 3, Bone 8; the sword skipped)")
    # one roll per death; OFF; ceilings
    mob = JClass("java.util.UUID").randomUUID()
    K.eq((bool(S.first(mob)), bool(S.first(mob))), (True, False), "X one roll per death (mob UUID)")
    # FIXER (b): a long-lived corpse (61 s) never rolls twice in a busy stretch (> 512 entries); an 11 min old entry is purged
    UUIDc, Long = JClass("java.util.UUID"), JClass("java.lang.Long")
    now = int(JClass("java.lang.System").currentTimeMillis())
    S.DONE.clear()
    old61, old11m = UUIDc.randomUUID(), UUIDc.randomUUID()
    for i in range(600):
        S.DONE.put(UUIDc.randomUUID(), Long(now - 61000))
    S.DONE.put(old61, Long(now - 61000))
    S.DONE.put(old11m, Long(now - 660000))
    S.PRUNED = 0
    K.check(bool(S.first(UUIDc.randomUUID())), "F a new kill rolls in a busy stretch (603 entries)")
    K.eq((bool(S.first(old61)), bool(S.DONE.containsKey(old11m)), int(S.DONE.size())), (False, False, 602),
         "F one roll per death holds 10 min: the 61 s old corpse does NOT roll again, the 11 min old entry is purged (was: 60 s)")
    K.eq(int(S.DONE_MS), 600000, "F DONE_MS = 10 min")
    S.DONE.clear()
    # FIXER (a): the Spoils owner = the drop's owner as SkyySacks claims it
    MC = JClass(PKG + "MobCredit")
    A, Bp, Ck = "00000000-0000-0000-0000-00000000000a", "00000000-0000-0000-0000-00000000000b", "00000000-0000-0000-0000-00000000000c"
    HERE = set([A, Bp])

    @JImplements("java.util.function.Function")
    class Players(object):
        @JOverride
        def apply(self, u):
            return JClass("java.lang.Boolean")(str(u) in HERE)
    S.PLAYERS = Players()
    mk = str(UUIDc.randomUUID())
    MC.hit(mk, A, 60.0, 40.0, 0.0, 100.0, now)      # A: top damager
    MC.hit(mk, Bp, 10.0, 30.0, 0.0, 100.0, now)     # B: lands the killing blow
    ub = UUIDc.fromString(Bp)
    K.eq(str(S.top(mk)), A, "F top(): the credit's top damager")
    K.eq(str(S.owner(mk, ub, None)), A, "F B lands the kill, A did the most damage and is here: Spoils roll on A's ranks and go to A (as SkyySacks' claim)")
    HERE.discard(A)
    K.eq(str(S.owner(mk, ub, None)), Bp, "F the top damager left this world: the killer (SkyySacks' fallback too)")
    HERE.add(A)
    K.eq(str(S.owner(mk, None, None)), A, "F no player killing blow, top damager here: the top damager")
    MC.read(mk, True)                                 # SkyySacks takes the entry first (same tick)
    K.eq(str(S.owner(mk, ub, None)), A, "F after SkyySacks' take (MobCredit.DEAD): still the top damager")
    K.eq(str(S.owner(str(UUIDc.randomUUID()), ub, None)), Bp, "F no credit: the killer")
    K.check(S.owner(str(UUIDc.randomUUID()), None, None) is None, "F no credit, no killer: nobody")
    mk2 = str(UUIDc.randomUUID())
    MC.hit(mk2, Ck, 60.0, 40.0, 0.0, 100.0, now)
    K.eq(str(S.owner(mk2, UUIDc.fromString(Ck), None)), Ck, "F the killer is the top damager: that player")
    # Coin Purse follows the owner: the coins go to the UUID passed in (the owner from tick)
    br.put("coins:fn:add", Coins())
    CN["coins"][:] = []
    S.C.clear()
    ua = UUIDc.fromString(A)
    rc = R(115)
    paid = sum(int(S.coins(ua, 7, rc)) for i in range(400))
    K.check(paid > 0 and all(c == (A, 7) for c in CN["coins"]), "F Coin Purse pays the owner passed in (A), %d coins over 400 rolls" % paid)
    br.remove("coins:fn:add")
    S.PLAYERS = None
    K.check(not bool(S.here(ua, None)), "F here(): no seam, no store = not here (the game path never throws)")
    # FIXER (c): the item-asset gear rule
    K.eq([bool(S.uniqOf(*a)) for a in [(None, None, None, 25, 0.0), (JString("w"), None, None, 25, 0.0), (None, JString("a"), None, 25, 0.0),
                                       (None, None, JString("t"), 25, 0.0), (None, None, None, 1, 0.0), (None, None, None, 25, 120.0)]],
         [False, True, True, True, True, True], "F uniqOf: plain stackable = loot; weapon / armour / tool / max stack 1 / durability = never repeated")
    try:
        st = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")(JString("Ingredient_Bone"), 2)
        ok = True
    except Exception as x:
        ok, st = False, str(x)[:120]
    if ok:
        u0 = bool(S.uniq(st))
        lst = JClass("java.util.ArrayList")()
        lst.add(st)
        ng = int(S.N_GEAR)
        n_out = int(S.clean(lst).size())
        K.check((n_out == 0) == u0 and int(S.N_GEAR) - ng == (1 if u0 else 0),
                "F a real ItemStack runs through uniq() inside clean() (no asset store here: uniq=%s -> %d out; unknown = skipped, the safe side)" % (u0, n_out))
    else:
        K.notes.append("F ItemStack could not be made without the asset store (%s) - uniq() covered by uniqOf + bytecode" % st)
        uf = JClass("java.lang.Class").forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        bare = uf.get(None).allocateInstance(JClass("com.hypixel.hytale.server.core.inventory.ItemStack"))
        K.check(bool(S.uniq(bare)), "F uniq() EXECUTED on a bare ItemStack (no asset store: the read throws -> skipped, the safe side - never a repeated unknown item)")
    S.ON = False
    K.eq((int(S.extra(uu, "DL", True, R(1)).size()), int(S.coins(uu, 30, R(1)))), (0, 0), "X Spoils OFF: nothing")
    S.ON = True
    S.V3X4 = 0.0
    S.C.clear()
    K.eq(round(float(S.vals(uu)[5]), 6), 0.0, "X a Server Setup ceiling of 0 turns Lucky Kill off at once")
    S.V3X4 = 6.0
    br.remove("coins:fn:add")
    S.C.clear()
    K.eq(sum(int(S.coins(uu, 30, R(i))) for i in range(200)), 0, "X no SkyyCoins: Coin Purse asks nothing")
    K.check(S.killer(None, None, None) is None, "X killer(no DeathComponent) = nobody")
    dd = os.path.join(scratch, "x")
    os.makedirs(dd, exist_ok=True)
    r = str(S.loadV3(JClass("java.nio.file.Paths").get(dd)))
    K.check("read" in r and open(os.path.join(dd, "trees.properties"), encoding="latin-1").read() == V3E.cfg_text("SkyyMobs"), "X loadV3 seeds trees.properties: %s" % r)
    K.check("Spoils" in str(S.text()), "X text(): %s" % S.text())
    S.reads(True)
    K.eq(str(br.get("tree:reads:SkyyMobs")), V3E.reads_csv("SkyyMobs"), "X reads(true) lists the keys")
    S.reads(False)
    K.check(br.get("tree:reads:SkyyMobs") is None, "X reads(false) removes our value")
    S.SYS_ON = False
    S.reads(S.SYS_ON)
    K.check(br.get("tree:reads:SkyyMobs") is None, "X fixer 2: reads(SYS_ON=false) publishes nothing (Spoils rows stay coming soon in SkyyTrees)")
    S.SYS_ON = True
    S.reads(S.SYS_ON)
    K.eq(str(br.get("tree:reads:SkyyMobs")), V3E.reads_csv("SkyyMobs"), "X fixer 2: reads(SYS_ON=true) lists the keys")
    S.reads(False)
    S.SYS_ON = False
    # SpoilsSys' dependencies from the real engine classes
    CL = JClass("java.lang.ClassLoader").getSystemClassLoader()
    SS.DDI = JClass("java.lang.Class").forName("com.hypixel.hytale.server.npc.systems.NPCDamageSystems$DropDeathItems", False, CL)
    SS.CR = JClass("java.lang.Class").forName("com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$CorpseRemoval", False, CL)
    sy = SS()
    deps = [str(x) for x in sy.getDependencies()]
    K.check(len(deps) == 2 and not bool(sy.isParallel(0, 1)), "X SpoilsSys: 2 dependencies (AFTER DropDeathItems, BEFORE CorpseRemoval), not parallel: %s" % [x[:90] for x in deps])
    K.save()


def run_wire(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for m in list(cp.get(PKG + cn).getDeclaredMethods()) + list(cp.get(PKG + cn).getDeclaredConstructors()):
            if str(m.getName()) == mn:
                IP(PS(bos)).print_(m)
        return str(bos.toString())
    t = code("SpoilsSys", "tick")
    ks = ["Role.hasDroppedDeathItems", "MobSpoils.first", "MobSpoils.killer", "MobSpoils.owner", "MobSpoils.extra", "MobSpoils.coins", "MobSpoils.spawn"]
    K.check(all(k in t for k in ks) and [t.index(k) for k in ks] == sorted(t.index(k) for k in ks), "W SpoilsSys.tick: hasDroppedDeathItems -> first -> killer -> owner -> extra -> coins -> spawn")
    cl = code("MobSpoils", "clean")
    K.check("MobSpoils.uniq" in cl and "MobSpoils.gear" in cl, "W fixer: clean() checks the item asset (uniq) and the name (gear)")
    uq = code("MobSpoils", "uniq")
    K.check(all(k in uq for k in ("ItemStack.getItem", "Item.getWeapon", "Item.getArmor", "Item.getTool", "Item.getMaxStack", "ItemStack.getMaxDurability")), "W fixer: uniq reads the asset")
    hr = code("MobSpoils", "here")
    K.check("Universe.getPlayer" in hr and "PlayerRef.getReference" in hr and "Ref.getStore" in hr, "W fixer: here() = SkyySacks' rule (Universe.getPlayer -> getReference -> same store)")
    sp = code("MobSpoils", "spawn")
    K.check("ItemComponent.generateItemDrops" in sp and "CommandBuffer.addEntities" in sp and "ItemStack.<init>" in sp, "W spawn = the engine recipe with new plain stacks")
    sy = code("SkyyMobsPlugin", "systems")
    K.check("SpoilsSys.<init>" in sy and sy.index("DropDeathItems") < sy.index("SpoilsSys.<init>"), "W systems(): SpoilsSys registered after both engine classes are found")
    s = code("SkyyMobsPlugin", "setup")
    K.check(s.index("MobCfg.load") < s.index("MobSpoils.loadV3") < s.index("SkyyMobsPlugin.systems") < s.index("MobSpoils.reads"), "W setup: MobCfg.load -> loadV3 -> systems() -> reads(SYS_ON)")
    K.check(s.index("SkyyMobsPlugin.systems") < s.index("MobSpoils.SYS_ON") < s.index("MobSpoils.reads"), "W fixer 2: reads() gets SYS_ON, read after systems() (no death system = keys never published)")
    K.check("MobSpoils.reads" in code("SkyyMobsPlugin", "shutdown"), "W shutdown: reads(false)")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg, S = JClass(PKG + "MobCfg"), JClass(PKG + "MobSpoils")
    P = JClass("java.nio.file.Paths")

    def start():
        Cfg.DIR = P.get(home)
        Cfg.FILE = P.get(os.path.join(home, "config.properties"))
        Cfg.BANDS = P.get(os.path.join(home, "bands.properties"))
        o = [str(JClass(PKG + m).run(P.get(home))) for m in ("MobMig", "MobMig14", "MobMig11", "MobMig12", "MobMigP4")]
        Cfg.load()
        o.append(str(S.loadV3(P.get(home))))
        return o
    h0 = tree_hash(home)
    o1 = start()
    h1 = tree_hash(home)
    ch = sorted(k for k in set(h0) | set(h1) if h0.get(k) != h1.get(k))
    K.eq(ch, ["trees.properties"], "D start 1 on a scratch COPY of the live data: only the new trees.properties (%s)" % [x[:60] for x in o1 if x])
    K.check(open(os.path.join(home, "trees.properties"), encoding="latin-1").read() == V3E.cfg_text("SkyyMobs"), "D trees.properties = the table's numbers")
    o2 = start()
    K.check(tree_hash(home) == h1 and all(x == "" for x in o2[:-1]), "D start 2 changes nothing")
    K.save()


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("exec", run_exec), ("wire", run_wire), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
