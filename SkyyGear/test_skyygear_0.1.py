"""Bare-JVM check for SkyyGear 0.1 after the three reviews (research/SkyyGear-0.1-Review-Findings.md), kept next to the build so the
build report's JVM claim can be re-run.

    python SkyyGear/test_skyygear_0.1.py [--jar <SkyyGear-0.1.jar>] [--dir <scratch folder>] [--keep]

Build the jar first (python SkyyGear/build_skyygear_0.1.py). A child process starts a fresh JVM (the game's own JRE, -Xverify:all,
-XX:-UsePerfData, HytaleServer.jar + the jar + tools/javassist.jar on the classpath; TEMP / TMP / java.io.tmpdir in the scratch
folder) and checks:
  A  every class loads and verifies
  B  config rows: gear.include, kind.prefix, migrate.clampToLevel (danger), KEEP 10, help <= 100, the Placeholder suffix on the five
     rows (design 10), the stat legend (design 7), the default file's per-key legend lines
  C  exploit 3: the 14 ammo ids stay ammo, Weapon_Shortbow_Bomb is gear
  D  design 1: gear.include (bags never), kind.prefix (longest wins, bad values dropped), the Equipment slot 4 + letter e, enforced kinds
  E  design 2: gear:extra:<uuid> parsed into the one totals function (withExtra on / off)
  F  design 3 / 4: vanilla #ff6b6b / #39f493, Mythic #CC66CC (defs + the quality asset), no old red / orange constants left
  G  design 5: Health Regen % never rolls without Raw Health Regen; its label
  H  design 6 / 8 / 9 / 11: the spell suffix, elements out of the hit math and into info[5], identify texts follow identify.command,
     the five coming-later Keep stats
  L  engine 1: GearFx.plan (lower always, raise only when the engine's Armor modifier is synced), a simulation of the engine clamp
     (EntityStatValue.computeModifiers) over equip / unequip / swap / level-up / break sequences in every order the two passes can
     run relative to EntityStatsSystems$Recalculate, the Armor key, GearLockSys ordered BEFORE Recalculate, raise flags (bytecode)
  M  engine 2: broken armor = amount x BrokenPenalties factor (the engine's computeStatModifiers shape)
  N  engine 3: armor in the hand is never judged as a weapon; an unidentified weapon still is
  O  engine 4: quality.properties parse / write / moved-index WARN (no epoch bump since follow-up 7); a stale stack quality is
     rewritten; sig uses names
  P  engine 5: GearFxInvSys only reacts to the armor container (bytecode)
  Q  engine 6: GearLog - line() and take() never wait for the disk lock; flush() writes under WLOCK only
  R  engine 7: writeAtomic replace / no-replace, no temp file left
  S  exploit 1: GearShotTrack.newest (newest live record of that shooter inside the 10 s window); GearHitSys uses pick (bytecode)
  T  exploit 2: stack split (storage first, counted, full inventory keeps the stack, nonces), craft rolls per item + the q <= cap - n
     rule, chest split per item, Identify all skips rows it cannot split
  U  exploit 4: migrated armor drops dmg and scores without it
  V  exploit 5: migrate.clampToLevel caps each migrated value at GearRoll.bounds(i, rarity, level)[1]
  W  follow-up review of e43c8bf: 1 gear.include guard (check hook, loader drops, ammo beats include, stackable included ids,
     kind equipment), 2 MaxStack ammo rule + split ceiling (fake Item assets with a MaxStack), 3 no hotbar split + 5-slot floor +
     no passive split + Identify / Reforge / Identify all take one item off a stack, 4 GearShotTrack.pick (weaker weapon) + the
     no-record WARN, 5 GearLockSys primes from saved locks, 6 scheduleRecalculate after waits, 7 unreadable quality.properties
     kept, 8 a throwing destination restores the source (split + takeOne), 9 gear:extra saturation + hit never below 0,
     10 negative armor sums cancelled (plan + clamp simulation)
Not testable without the game (UNVERIFIED in the build report): the real system order around Recalculate, the engine recalculating a
live EntityStatMap, projectile records on real arrows, item entities, loot chests, pages on a client, the quality asset pack.
Nothing is deployed. Default scratch folder: tools/dev/scratch/skyygear-test (git-ignored), deleted at the end unless --keep.
Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, time, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.1"
PKG = "com.skyy.gear."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyygear-test")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


PH = " Placeholder - Skyy tunes this."
AMMO_IDS = ["Weapon_Arrow_Clearshot", "Weapon_Arrow_Crude", "Weapon_Arrow_Deadeye", "Weapon_Arrow_Iron", "Weapon_Arrow_Trueshot",
            "Weapon_Bomb", "Weapon_Bomb_Continuous", "Weapon_Bomb_Fire", "Weapon_Bomb_Large_Fire", "Weapon_Bomb_Popberry",
            "Weapon_Bomb_Potion_Poison", "Weapon_Bomb_Stun", "Weapon_Dart_Tribal", "Weapon_Grenade_Frag"]


# ============================================================================================================== engine clamp model
class StatModel:
    """EntityStatValue as the bytecode does it (2026-09-29): every putModifier / removeModifier recomputes max = base + the MAX
    ADDITIVE modifiers and clamps value into [min, max] at once."""

    def __init__(self, base, value):
        self.base = base
        self.value = value
        self.mods = {}

    def max(self):
        return self.base + sum(self.mods.values())

    def put(self, key, amt):
        if amt == 0:
            self.mods.pop(key, None)
        else:
            self.mods[key] = amt
        self.value = min(max(self.value, 0.0), self.max())


# ============================================================================================================== child: the checks
def run(jar):
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JObject, JImplements, JOverride, JFloat, JInt, JBoolean, JLong, JString
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, jar, B.JAVASSIST], convertStrings=True)

    # ---------------- A. load + verify
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return

    # a bare JVM has no Item asset store and every ItemStack constructor calls getItem(): an empty store (Item.UNKNOWN for every
    # id) is put in place without running its constructor, so stacks, containers and the gear writes can run here
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    store = us.allocateInstance(fake.toClass(AS.class_))    # never constructed: only getAssetMap() (a plain field read) is used
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    fm.set(store, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())
    fi_ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)

    J = lambda n: JClass(PKG + n)
    Gear, Defs, Cfg, Data, Roll, View, Stats, Stamp, Forge, Hit, Shot, Track, Armor, Fx, Tag, Ident, Qual, Log, Rows, Lvl = (
        J("Gear"), J("GearDefs"), J("GearCfg"), J("GearData"), J("GearRoll"), J("GearView"), J("GearStats"), J("GearStamp"),
        J("GearForge"), J("GearHit"), J("GearShot"), J("GearShotTrack"), J("GearArmor"), J("GearFx"), J("GearTag"), J("GearIdent"),
        J("GearQual"), J("GearLog"), J("CfgRows"), J("GearLevel"))
    CraftTask = J("GearCraftTask")
    UUID, Paths, Props = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.util.Properties")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    BD = JClass("org.bson.BsonDocument")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    HashMap, IdMap, ArrayList = JClass("java.util.HashMap"), JClass("java.util.IdentityHashMap"), JClass("java.util.ArrayList")
    Integer = JClass("java.lang.Integer")
    bridge = Gear.bridge()
    Cfg.apply(Props(), False)          # the built-in defaults (no file): material table + every default
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000aaaa")
    U2 = UUID.fromString("00000000-0000-0000-0000-00000000bbbb")
    SK = [str(x) for x in Defs.S_KEY]
    si = SK.index

    # ---------------- B. config rows
    keys = [str(k) for k in Rows.KEYS]
    helps = dict(zip(keys, [str(h) for h in Rows.HELPS]))
    flags = dict(zip(keys, [str(f) for f in Rows.FLAGS]))
    types = dict(zip(keys, [str(t) for t in Rows.TYPES]))
    defs = dict(zip(keys, [str(d) for d in Rows.DEFS]))
    opts = dict(zip(keys, [str(o) for o in Rows.OPTS]))
    check(int(Rows.KEEP) == 10, "config kit KEEP = 10 (LOCKED)")
    check("gear.include" in keys and types["gear.include"] == "text" and defs["gear.include"] == "", "row gear.include (text, empty)")
    check("kind.prefix" in keys and types["kind.prefix"] == "table" and opts["kind.prefix"] == "text;type;Kind", "row kind.prefix (text table)")
    check("migrate.clampToLevel" in keys and types["migrate.clampToLevel"] == "bool" and defs["migrate.clampToLevel"] == "false"
          and "danger" in flags["migrate.clampToLevel"].split(","), "row migrate.clampToLevel (bool, default false, danger)")
    check(all(len(h) <= 100 for h in helps.values()), "every help <= 100 characters")
    for k in ("craft.maxRarity", "migrate.maxRarity", "regen.periodMs", "pool.later", "level.armorNative"):
        check(helps[k].endswith(PH), "design 10: %s help ends with the Placeholder suffix" % k)
    check(helps["stat"].startswith("dmg Damage, str Strength, mp Magical Power"), "design 7: the stat row help is a key legend")
    dt = str(Cfg.defaultsText())
    check("# dmg = Damage (weapon, %)" in dt and "# hprp = Health Regen % (weapon, armor, %)" in dt and "# lbonus = Loot Bonus" in dt,
          "design 7: config.properties names every stat key above its line")
    check("(spec 4.2)" not in str(Cfg.checkStat("stat[nope]", "1|1")) and "config.properties" in str(Cfg.checkStat("stat[nope]", "1|1")),
          "design 7: the unknown-stat message has no spec pointer")
    check("migrate.clampToLevel=false" in dt and "gear.include=" in dt and "kind.prefix.<id prefix>" in dt, "default file has the new keys")
    print("B. config rows done")

    # ---------------- C. exploit 3: ammo
    for i in AMMO_IDS:
        check(bool(Data.ammo(i)) and not bool(Data.isGear(i)), "exploit 3: %s is ammo, not gear" % i)
    check(not bool(Data.ammo("Weapon_Shortbow_Bomb")) and bool(Data.isGear("Weapon_Shortbow_Bomb")), "exploit 3: Weapon_Shortbow_Bomb is gear")
    check(bool(Data.isGear("Weapon_Sword_Iron")) and bool(Data.isGear("Armor_Iron_Chest")) and not bool(Data.isGear("Weapon_Shield_Iron")),
          "gear rules unchanged for swords, armor, shields")
    print("C. ammo done")

    # ---------------- D. design 1: gear.include / kind.prefix / Equipment
    check(not bool(Data.isGear("Skyy_Sword_Test")) and not bool(Data.isGear("Tool_Pickaxe_Iron")), "Skyy_ and Tool_ ids are not gear by default")
    p = Props()
    p.setProperty("gear.include", "Skyy_Sword_, Skyy_Ring_,Skyy_Sack_,Skyy_Bag_,Skyy_Accessory_Bag,Tool_Pickaxe_")
    p.setProperty("kind.prefix.Skyy_Ring_", "Equipment")
    p.setProperty("kind.prefix.Armor_", "mining")
    p.setProperty("kind.prefix.Armor_Iron_", "farming")
    p.setProperty("kind.prefix.Weapon_Bad_", "sword")
    Cfg.apply(p, False)
    check(bool(Data.isGear("Skyy_Sword_Test")) and bool(Data.isGear("Skyy_Ring_Gold")), "gear.include opts Skyy_ ids in")
    for b in ("Skyy_Sack_Mining_Small", "Skyy_Bag_Rare", "Skyy_Accessory_Bag"):
        check(not bool(Data.isGear(b)), "bags are never gear, even through gear.include: " + b)
    check(str(Data.kindFor("Skyy_Ring_Gold")) == "equipment" and int(Data.slotOf("Skyy_Ring_Gold")) == 4, "kind.prefix equipment -> slot 4")
    check(str(View.slotWord("Skyy_Ring_Gold")) == "EQUIPMENT", "slot word EQUIPMENT")
    check(str(Data.kindFor("Armor_Iron_Chest")) == "farming" and str(Data.kindFor("Armor_Copper_Chest")) == "mining", "longest kind prefix wins")
    check(str(Data.kindFor("Weapon_Bad_X")) == "combat" and not Cfg.KINDP.containsKey("Weapon_Bad_"), "a bad kind value is dropped")
    check(int(Data.slotOf("Tool_Pickaxe_Iron")) == 3 and str(Data.kindFor("Tool_Pickaxe_Iron")) == "mining", "an included tool stays a tool (slot 3, mining)")
    e_ok = sorted(SK[i] for i in range(int(Defs.NS)) if bool(Roll.allowed(i, 4)))
    check(e_ok == sorted(["str", "mp", "as", "spd"]), "letter e = Strength, Magical Power, Attack Speed, Speed: %s" % e_ok)
    check(bool(Defs.enforcedKind("combat")) and bool(Defs.enforcedKind("equipment")) and not bool(Defs.enforcedKind("mining")),
          "enforced kinds: combat + equipment (gathering later)")
    check(Cfg.checkKind("kind.prefix[Skyy_Ring_]", "Equipment") is None and Cfg.checkKind("kind.prefix[X]", "sword") is not None,
          "kind.prefix check hook")
    d = Roll.newDoc("Skyy_Ring_Gold", 5, True, "admin")
    ms = [str(m.asDocument().getString("s").getValue()) for m in Data.mods(d)]
    check(all(k in ("str", "mp", "as", "spd") for k in ms) and len(ms) >= 1, "an Equipment piece rolls only letter-e stats: %s" % ms)
    Cfg.apply(Props(), False)
    check(not bool(Data.isGear("Skyy_Sword_Test")) and str(Data.kindFor("Armor_Iron_Chest")) == "combat", "defaults back")
    print("D. include / kinds done")

    # ---------------- E. design 2: gear:extra
    bridge.put("gear:extra:" + str(U1), "str:40, cc:10,bogus:5,def:x,spd:-2,cd")
    x = Stats.extra(U1)
    check(x is not None and int(x[si("str")]) == 40 and int(x[si("cc")]) == 10 and int(x[si("spd")]) == -2 and int(x[si("def")]) == 0,
          "gear:extra parsed (unknown keys and bad parts skipped)")
    ok = JArray(JClass("boolean"))(1)
    t = Stats.totals(U1, None, None, ok, True)
    check(int(t[si("str")]) == 40 and int(t[si("cc")]) == 10 and bool(ok[0]), "totals withExtra adds gear:extra")
    t = Stats.totals(U1, None, None, None, False)
    check(sum(int(v) for v in t) == 0, "totals without extra = gear only (gear:stats stays SkyyGear's own)")
    check(Stats.extra(U2) is None, "no gear:extra -> null")
    bridge.remove("gear:extra:" + str(U1))
    print("E. extra done")

    # ---------------- F. design 3 / 4: colours
    check(str(Defs.C_BAD) == "#ff6b6b" and str(Defs.C_OK) == "#39f493", "vanilla red / green")
    check(str(Defs.R_HEX[5]) == "#CC66CC" and str(Defs.R_PAGEHEX[5]) == "#CC66CC", "Mythic #CC66CC")
    zq = json.loads(zipfile.ZipFile(jar).read("Server/Item/Qualities/Skyy_Gear_Mythic.json").decode("utf-8"))
    check(zq["TextColor"] == "#cc66cc", "the Mythic quality asset TextColor")
    raw = zipfile.ZipFile(jar)
    for cn in ("GearGate", "IdentifyPage", "GearView", "ReforgePage"):
        b = raw.read("com/skyy/gear/%s.class" % cn)
        check(b"#ff9d6b" not in b and b"#FF5555" not in b and b"#55FF55" not in b, "%s has no old red / orange / green literal" % cn)
    print("F. colours done")

    # ---------------- G. design 5: Health Regen % only with Raw Health Regen
    check(str(Defs.S_LABEL[si("hprp")]) == "Health Regen %", "hprp label")
    w0 = [int(v) for v in Cfg.S_W]
    w = JArray(JInt)(len(w0))
    for i in range(len(w0)):
        w[i] = 0
    w[si("hprp")] = 1000
    w[si("str")] = 1
    Cfg.S_W = w
    alone = 0
    for _ in range(300):
        ks = [str(m.asDocument().getString("s").getValue()) for m in Roll.rollMods(0, 5, 50)]
        if "hprp" in ks and "hpr" not in ks:
            alone += 1
    check(alone == 0, "hprp never rolls without hpr (hpr weight 0)")
    w[si("hpr")] = 1
    Cfg.S_W = w
    both = 0
    for _ in range(300):
        ks = [str(m.asDocument().getString("s").getValue()) for m in Roll.rollMods(0, 5, 50)]
        if "hprp" in ks:
            both += 1
            if "hpr" not in ks:
                alone += 1
    check(alone == 0 and both > 0, "hprp rolls after hpr (%d rolls had it)" % both)
    w2 = JArray(JInt)(len(w0))
    for i in range(len(w0)):
        w2[i] = w0[i]
    Cfg.S_W = w2
    print("G. regen rule done")

    # ---------------- H. design 6 / 8 / 9 / 11
    check(str(View.suffix(si("mp"))) == " (spell attacks only)", "design 6: Magical Power suffix")
    for k in ("lbonus", "lquality", "stealing", "trophy", "xpb"):
        i = si(k)
        check(int(Defs.S_LIVE[i]) == 0 and int(Defs.S_WDEF[i]) == 2 and str(Defs.S_SLOT[i]) == "wa", "design 11: %s coming later, weight 2" % k)
    t = JArray(JInt)(int(Defs.NS))
    t[si("fFire")] = 6
    t[si("fAir")] = 2
    t[si("rElem")] = 3
    check(abs(float(Hit.hitAmount(10.0, t, False, 0.9, 0.9)) - 10.0) < 1e-9, "design 8: flat elements are not in the hit math")
    check(int(Hit.elemSum(t)) == 6 + 2 + 15, "design 8: elemSum = flats + 5 x Raw Elemental")
    t[si("cc")] = 100
    check(abs(float(Hit.hitAmount(10.0, t, False, 0.0, 0.9)) - 20.0) < 1e-9, "design 8: a crit doubles only the physical part")
    inf = Hit.info(U1, t)
    check(len(inf) == 6 and int(inf[5]) == 23, "design 8: info[5] carries the element sum for GearTrueSys")
    unid = Roll.newDoc("Weapon_Sword_Iron", 2, False, "drop")
    Cfg.IDENTIFY_CMD = False
    pl = " | ".join(str(s) for s in View.plain("Weapon_Sword_Iron", unid, None))
    check("Identify: at the identifier - " in pl and "/identify" not in pl, "design 9: tooltip text without /identify: " + pl)
    st = Data.put(IS("Weapon_Sword_Iron", 1), unid, U1)
    check(str(Forge.refuse(st, unid)) == "Identify it first", "design 9: reforge refusal without /identify")
    jb = Hit.judge(U1, st, False)
    check(jb is not None and str(jb[2]) == "Identify it first", "design 9: popup without /identify")
    Cfg.IDENTIFY_CMD = True
    pl = " | ".join(str(s) for s in View.plain("Weapon_Sword_Iron", unid, None))
    check("Identify: /identify - " in pl and str(Forge.refuse(st, unid)) == "Identify it first: /identify", "design 9: /identify when the command is on")
    print("H. texts done")

    # ---------------- L. engine 1: the lock never eats the current value
    plan = lambda have, want, raise_, eng, full: float(Fx.plan(JFloat(have), JFloat(want), raise_, JFloat(eng), JFloat(full)))
    check(plan(17, 0, False, 0, 0) == 0 and plan(17, 12.75, False, 17, 12.75) == 12.75, "plan: lowering is always done")
    check(plan(0, 17, False, 17, 17) == 0, "plan: never raises without raise (GearFxInvSys / GearLockSys)")
    check(plan(0, 17, True, 0, 17) == 0, "plan: no raise while the engine has not applied the piece")
    check(plan(0, 17, True, 17, 17) == 17 and plan(5, 17, True, 22, 22) == 17, "plan: raise once synced")
    check(str(Fx.armorKey()) == str(CAL.ADDITIVE.createKey("Armor")), "the engine's Armor key: %s" % Fx.armorKey())

    def sim(steps, base=100.0):
        """steps: list of (container_sum_full, inactive_sum, order). order = the sequence of passes for this change:
        'E' engine Recalculate (Armor := full), 'L' a lower-only pass (GearLockSys / GearFxInvSys), 'T' the 1 s tick (raise allowed).
        Returns the list of (value, steady max) after each change."""
        m = StatModel(base, base)
        lock = 0.0
        engine = 0.0
        out = []
        for full, inact, order in steps:
            for o in order:
                if o == "E":
                    engine = full
                    m.put("Armor", engine)
                else:
                    nxt = plan(lock, inact, o == "T", engine, full)
                    if nxt != lock:
                        lock = nxt
                        m.put("lock", -lock)
            out.append((m.value, base + full - inact))
        return out

    # the player starts full; a change is applied in the orders the engine can produce: the lower-only pass runs BEFORE
    # Recalculate (GearLockSys dependency) or at the latest from the armor change event; the tick comes after (next second)
    cases = {
        "equip an inactive +17 piece": [(0, 0, "ET"), (17, 17, "LET")],
        "unequip it": [(17, 17, "ET"), (0, 0, "LET")],
        "swap active +17 for inactive +17": [(17, 0, "ET"), (17, 17, "LET")],
        "swap inactive +17 for active +17": [(17, 17, "ET"), (17, 0, "LET")],
        "level up (inactive becomes active)": [(17, 17, "ET"), (17, 0, "T")],
        "class change (active becomes inactive)": [(17, 0, "ET"), (17, 17, "T")],
        "inactive piece breaks (x0.75)": [(17, 17, "ET"), (12.75, 12.75, "LET")],
        "two pieces, one inactive leaves": [(34, 17, "ET"), (17, 0, "LET")],
        "tick before the engine (equip)": [(0, 0, "ET"), (17, 17, "TLET")],
    }
    for name, steps in cases.items():
        res = sim(steps)
        ok_ = True
        for i, (v, steady) in enumerate(res):
            prev_v = res[i - 1][0] if i else 100.0
            # the value may only drop to the new steady max (vanilla behaviour for a lower max), never below it
            if v + 1e-6 < min(prev_v, steady):
                ok_ = False
        check(ok_, "engine 1 simulation keeps the current value: %s -> %s" % (name, res))
    # negative control: an unequipped piece whose lock shrinks only AFTER Recalculate loses the value - why GearLockSys is ordered
    # BEFORE EntityStatsSystems$Recalculate (and GearFxInvSys lowers too)
    late = sim([(17, 17, "ET"), (0, 0, "ELT")])
    check(late[1][0] == 83.0, "the model sees the loss when the lock shrinks after Recalculate: %s" % late)
    # the old order (lock raised on the change event, before Recalculate) loses current value: the simulation sees it
    old = StatModel(100.0, 100.0)
    old.put("lock", -17.0)
    old.put("Armor", 17.0)
    check(old.value == 83.0 and old.max() == 100.0, "the reviewed bug reproduces in the model (lock before Recalculate eats 17 HP)")
    # bytecode: GearFxInvSys never raises, GearFx.second raises, GearLockSys is lower-only, ordered BEFORE Recalculate
    Pool, IP, PS, BOS = (JClass("javassist.ClassPool"), JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"),
                         JClass("java.io.ByteArrayOutputStream"))
    pool = Pool(False)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    pool.appendSystemPath()

    def code(cls, meth):
        cc = pool.get(PKG + cls)
        out = []
        for mm in cc.getDeclaredMethods():
            if str(mm.getName()) == meth:
                bos = BOS()
                IP(PS(bos)).print_(mm)
                out += str(bos.toString()).splitlines()
        return out

    def before_call(lines, needle):
        for i, l in enumerate(lines):
            if needle in l:
                return lines[i - 1].strip()
        return ""

    fi = code("GearFxInvSys", "handle")
    check(before_call(fi, "GearFx.armorPass").endswith("iconst_0"), "GearFxInvSys: armorPass(..., raise = false)")
    se = code("GearFx", "second")
    check(before_call(se, "GearFx.armorPass").endswith("iconst_1"), "GearFx.second (1 s tick): armorPass(..., raise = true)")
    lo = code("GearFx", "lowerNow")
    check(before_call(lo, "GearFx.locks").endswith("iconst_0"), "GearFx.lowerNow: locks(..., raise = false)")
    lk = code("GearLockSys", "tick")
    check(any("GearFx.lowerNow" in l for l in lk) and not any("armorPass" in l for l in lk), "GearLockSys only lowers")
    LS = J("GearLockSys")
    Recalc = Cls.forName("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsSystems$Recalculate", False, loader)
    LS.RECALC = Recalc
    deps = LS(True).getDependencies()
    dep = deps.iterator().next() if deps.size() == 1 else None
    check(dep is not None and str(dep.getOrder()) == "BEFORE" and str(dep.getSystemClass().getName()).endswith("EntityStatsSystems$Recalculate"),
          "GearLockSys is ordered BEFORE EntityStatsSystems$Recalculate")
    check(LS(False).getDependencies().size() == 0 and not bool(LS(True).isParallel(1, 1)), "unordered fallback has no dependency; not parallel")
    su = code("GearFx", "setup")
    check(any("EntityStatsSystems$Recalculate" in l for l in su) and any("GearLockSysU" in l for l in su), "setup orders GearLockSys + fallback")
    print("L. engine 1 done")

    # ---------------- M. engine 2: broken armor factor
    m = HashMap()
    a0 = JArray(SMO)(1)
    a0[0] = SMO(MTG.MAX, CAL.ADDITIVE, JFloat(17.0))
    a2 = JArray(SMO)(2)
    a2[0] = SMO(MTG.MAX, CAL.ADDITIVE, JFloat(5.0))
    a2[1] = SMO(MTG.MAX, CAL.MULTIPLICATIVE, JFloat(0.1))
    m.put(Integer.valueOf(0), a0)
    m.put(Integer.valueOf(2), a2)
    out = HashMap()
    Armor.addSums(m, True, JFloat(0.75), out, None)
    check(abs(float(out.get(Integer.valueOf(0))) - 12.75) < 1e-6 and abs(float(out.get(Integer.valueOf(2))) - 3.75) < 1e-6,
          "broken piece: amount x 0.75 (additive only): %s" % out)
    out = HashMap()
    Armor.addSums(m, False, JFloat(0.75), out, None)
    check(abs(float(out.get(Integer.valueOf(0))) - 17.0) < 1e-6 and abs(float(out.get(Integer.valueOf(2))) - 5.0) < 1e-6, "whole piece: full amount")
    a3 = JArray(SMO)(1)
    a3[0] = SMO(MTG.MIN, CAL.ADDITIVE, JFloat(4.0))
    m3 = HashMap()
    m3.put(Integer.valueOf(1), a3)
    out = HashMap()
    Armor.addSums(m3, False, JFloat(1.0), out, None)
    check(abs(float(out.get(Integer.valueOf(1))) - 4.0) < 1e-6, "every target counts (the engine puts every additive sum on MAX)")
    check(abs(float(Armor.brokenFactor(None)) - 1.0) < 1e-6, "no world -> factor 1")
    print("M. engine 2 done")

    # ---------------- N. engine 3: armor in the hand is not a weapon
    ua = Data.put(IS("Armor_Iron_Chest", 1), Roll.newDoc("Armor_Iron_Chest", 3, False, "drop"), U1)
    check(Hit.judge(U1, ua, False) is None and Hit.judge(U1, ua, True) is None, "unidentified armor in hand / utility is never judged")
    check(Hit.judge(U1, st, False) is not None, "an unidentified weapon still blocks")
    print("N. engine 3 done")

    # ---------------- O. engine 4: quality indices
    pq = Props()
    pq.setProperty("Skyy_Gear_Normal", "40")
    pq.setProperty("Skyy_Gear_Rare", "42")
    q = Qual.parse(pq)
    check(q is not None and int(q[0]) == 40 and int(q[1]) == -1 and int(q[2]) == 42, "quality.properties parse")
    check(Qual.parse(Props()) is None, "an empty file = no indices")
    now = JArray(JInt)(7)
    for i in range(7):
        now[i] = 40 + i
    check(not bool(Qual.differs(q, now)), "same indices -> not moved")
    now[2] = 50
    check(bool(Qual.differs(q, now)) and not bool(Qual.differs(None, now)), "a moved index is seen; no file = not moved")
    qf = os.path.join(SCRATCH, "work", "Skyy_SkyyGear", "quality.properties")
    os.makedirs(os.path.dirname(qf), exist_ok=True)
    open(qf, "w").write("Skyy_Gear_Normal=40\nSkyy_Gear_Unique=41\nSkyy_Gear_Rare=42\n")
    Qual.load(Paths.get(qf))
    check(bool(Qual.wasOurs(41)) and not bool(Qual.wasOurs(7)), "wasOurs = an index of the last start")
    ep = int(Cfg.EPOCH)
    Qual.CHECKED = False
    Qual.check(now)
    # follow-up review 7 (changed check): no epoch bump any more - GearView.apply rewrites a stack whose quality index moved
    check(bool(Qual.MOVED) and int(Cfg.EPOCH) == ep, "moved indices: WARN, the config epoch stays (GearView.apply rewrites effQ != curQ)")
    J("GearQual")(Qual.text(now)).run()
    txtq = open(qf).read()
    check("Skyy_Gear_Rare=50" in txtq and "Skyy_Gear_Mythic=45" in txtq, "quality.properties rewritten with today's indices")
    check(bool(Defs.validQ(Integer.MIN_VALUE)) and not bool(Defs.validQ(5)) and not bool(Defs.validQ(-3)), "validQ: own ok, unknown index not")
    check(str(Defs.qName(Integer.MIN_VALUE)) == "own", "sig names the quality, never the raw index")
    doc = Roll.newDoc("Weapon_Sword_Iron", 1, True, "admin")
    good = Data.put(IS("Weapon_Sword_Iron", 1), doc, U1)
    stale = good.withQuality(5)
    fixed = View.apply(stale, doc, U1)
    ident = JClass("java.lang.System").identityHashCode
    check(int(fixed.getQualityIndex()) == int(good.getQualityIndex()) and ident(fixed) != ident(stale),
          "a stack whose quality index resolves to nothing is rewritten to the item's own quality (%s)" % fixed.getQualityIndex())
    check(ident(View.apply(fixed, doc, U1)) == ident(fixed), "and stays put afterwards (no rewrite loop)")
    check(ident(View.apply(good, doc, U1)) == ident(good), "a correct stack is left alone (same object)")
    print("O. engine 4 done")

    # ---------------- P. engine 5: armor container only
    check(any("InventoryChangeEvent.getItemContainer" in l for l in fi) and any("InventoryChangeEvent.getInventory" in l for l in fi)
          and any("Inventory.getArmor" in l for l in fi), "GearFxInvSys checks the event's container against the armor container")
    ia = [i for i, l in enumerate(fi) if "getItemContainer" in l]
    ap = [i for i, l in enumerate(fi) if "GearFx.armorPass" in l]
    check(ia and ap and ia[0] < ap[0], "the container check comes before the armor pass")
    print("P. engine 5 done")

    # ---------------- Q. engine 6: GearLog outside its lock
    Mod = JClass("java.lang.reflect.Modifier")
    LogC = Cls.forName(PKG + "GearLog", False, loader)
    msync = lambda n: bool(Mod.isSynchronized([x for x in LogC.getDeclaredMethods() if str(x.getName()) == n][0].getModifiers()))
    check(not msync("flush") and msync("take") and msync("kick") and not msync("write"), "flush / write unsynchronized, take / kick hold the monitor")
    lf = os.path.join(SCRATCH, "work", "gear.log")
    Log.FILE = Paths.get(lf)
    WL = Log.WLOCK
    holding = {"on": False}

    @JImplements("java.lang.Runnable")
    class Hold:
        @JOverride
        def run(self):
            with jpype.synchronized(WL):
                holding["on"] = True
                time.sleep(1.2)
            holding["on"] = False

    th = JClass("java.lang.Thread")(Hold())
    th.start()
    for _ in range(50):
        if holding["on"]:
            break
        time.sleep(0.02)
    t0 = time.time()
    Log.line("REVIEW-TEST one")
    Log.line("REVIEW-TEST two")
    s_ = str(Log.take())
    dt_ = time.time() - t0
    check(holding["on"] and dt_ < 0.5 and "REVIEW-TEST one" in s_ and "REVIEW-TEST two" in s_,
          "line() + take() never wait for the disk lock (%.3f s while WLOCK is held)" % dt_)
    Log.line("REVIEW-TEST three")
    t0 = time.time()
    Log.flush()
    dt2 = time.time() - t0
    th.join()
    check(dt2 > 0.2, "flush() writes under WLOCK (it waited %.3f s)" % dt2)
    check(os.path.isfile(lf) and "REVIEW-TEST three" in open(lf).read(), "gear.log written")
    Log.FILE = None
    print("Q. engine 6 done")

    # ---------------- R. engine 7: writeAtomic
    wf = os.path.join(SCRATCH, "work", "atomic", "a.properties")
    if os.path.exists(wf):
        os.remove(wf)
    Cfg.writeAtomic(Paths.get(wf), "x=1\n", False)
    Cfg.writeAtomic(Paths.get(wf), "x=2\n", False)
    check(open(wf).read() == "x=1\n", "replace = false never overwrites an existing file")
    Cfg.writeAtomic(Paths.get(wf), "x=3\n", True)
    check(open(wf).read() == "x=3\n" and not os.path.exists(wf + ".tmp"), "replace = true writes, no temp file left")
    wa = code("GearCfg", "writeAtomic")
    check(any("ATOMIC_MOVE" in l for l in wa) and any("REPLACE_EXISTING" in l for l in wa), "writeAtomic moves with ATOMIC_MOVE + REPLACE_EXISTING")
    check(any("FileDescriptor.sync" in l for l in wa) and any("getFD" in l for l in wa), "writeAtomic fsyncs the temp file first")
    print("R. engine 7 done")

    # ---------------- S. exploit 1: newest launch record
    Track.SHOTS.clear()
    bowA, bowB, bowC = IS("Weapon_Shortbow_Crude", 1), IS("Weapon_Shortbow_Iron", 1), IS("Weapon_Shortbow_Copper", 1)
    ms_ = int(JClass("java.lang.System").currentTimeMillis())
    for key, bow, age, who in (("a", bowA, 5000, U1), ("b", bowB, 1000, U1), ("c", bowC, 20000, U1), ("d", bowC, 100, U2)):
        r = Shot(who, bow, None, None)
        r.at = ms_ - age
        Track.SHOTS.put(UUID.nameUUIDFromBytes(key.encode()), r)
    nw = Track.newest(U1)
    check(nw is not None and str(nw.main.getItemId()) == "Weapon_Shortbow_Iron", "newest live record of that shooter (not another player's)")
    Track.SHOTS.remove(UUID.nameUUIDFromBytes(b"b"))
    check(str(Track.newest(U1).main.getItemId()) == "Weapon_Shortbow_Crude", "an older live record next")
    Track.SHOTS.remove(UUID.nameUUIDFromBytes(b"a"))
    check(Track.newest(U1) is None, "a record outside the 10 s window never counts")
    Track.SHOTS.clear()
    hs = code("GearHitSys", "handle")
    # follow-up review 4 (changed check): GearHitSys now asks GearShotTrack.pick (newest, or the weaker weapon), not newest()
    check(any("GearShotTrack.pick" in l for l in hs) and any("GearHit.family" in l for l in hs), "GearHitSys takes projectile hits from pick()")
    print("S. exploit 1 done")

    # ---------------- T. exploit 2: per-item rolls / stamps
    # (follow-up review 3: split takes a floor argument - 0 here, the player floor is tested in W; give = storage, backpack)
    hot, sto, bak = SIC(9), SIC(36), SIC(9)
    give = JArray(IC)([sto, bak])
    alls = JArray(IC)([hot, sto, bak])
    hot.setItemStackForSlot(0, IS("Weapon_Spear_Crude", 3))
    moved = int(Stamp.split(hot, 0, give, alls, U1, 0, 64, 0, None))
    s0, s1, s2 = hot.getItemStack(0), sto.getItemStack(0), sto.getItemStack(1)
    check(moved == 2 and int(s0.getQuantity()) == 1 and s1 is not None and int(s1.getQuantity()) == 1 and int(s2.getQuantity()) == 1,
          "a stack of 3 spears -> the slot keeps 1, two singles go to storage first")
    check(int(Stamp.countId(alls, "Weapon_Spear_Crude")) == 3, "counted before / after: still 3 spears")
    d1, d2 = Data.gearDoc(s1.getMetadata()), Data.gearDoc(s2.getMetadata())
    check(d1 is not None and d2 is not None and d1.containsKey("k") and d2.containsKey("k") and str(d1.toJson()) != str(d2.toJson()),
          "each split single has its own document with a nonce (they never stack again)")
    check(not bool(s1.isStackableWith(s2)), "two split singles are not stackable")
    # full inventory: nothing moves, the stack stays whole
    fh, fs = SIC(2), SIC(2)
    fs.setItemStackForSlot(0, IS("Ingredient_Stick", 1))
    fs.setItemStackForSlot(1, IS("Ingredient_Stick", 1))
    fh.setItemStackForSlot(1, IS("Ingredient_Stick", 1))
    fh.setItemStackForSlot(0, IS("Weapon_Spear_Crude", 5))
    moved = int(Stamp.split(fh, 0, JArray(IC)([fs, fh]), JArray(IC)([fh, fs]), U1, 0, 64, 0, None))
    check(moved == 0 and int(fh.getItemStack(0).getQuantity()) == 5, "full inventory: the stack stays whole (never dropped)")
    fs.setItemStackForSlot(1, None)
    moved = int(Stamp.split(fh, 0, JArray(IC)([fs, fh]), JArray(IC)([fh, fs]), U1, 0, 64, 0, None))
    check(moved == 1 and int(fh.getItemStack(0).getQuantity()) == 4 and int(Stamp.countId(JArray(IC)([fh, fs]), "Weapon_Spear_Crude")) == 5,
          "one free slot: one single moves, the rest stays one stack, count unchanged")
    # an unidentified stack: every single keeps the rarity, stays unidentified
    uh, us = SIC(3), SIC(9)
    ud = Roll.unidDoc("Weapon_Spellbook_Frost", 1, "drop")
    ud.put("r", JClass("org.bson.BsonString")("rare"))
    uh.setItemStackForSlot(0, Data.put(IS("Weapon_Spellbook_Frost", 4), ud, None))
    moved = int(Stamp.split(uh, 0, JArray(IC)([us, uh]), JArray(IC)([uh, us]), U1, 0, 64, 0, None))
    docs = [Data.gearDoc(us.getItemStack(i).getMetadata()) for i in range(3)]
    check(moved == 3 and all(dd is not None and not bool(Data.identified(dd)) and int(Data.rarity(dd)) == 2 for dd in docs),
          "an unidentified stack of 4 -> 4 unidentified Rare singles")
    # crafted output: every item rolls; a stack bigger than the craft count is never rolled as one
    ch, cs_ = SIC(9), SIC(36)
    ch.setItemStackForSlot(2, IS("Weapon_Spear_Crude", 3))
    got = JClass("java.lang.StringBuilder")()
    n = int(CraftTask.rollIn(JArray(IC)([ch, cs_]), JArray(IC)([cs_]), U1, "Weapon_Spear_Crude", IdMap(), 3, None, got))
    rolled = [x for x in [ch.getItemStack(2)] + [cs_.getItemStack(i) for i in range(4)] if x is not None and not x.isEmpty()]
    srcs = [str(Data.gearDoc(x.getMetadata()).getString("src").getValue()) for x in rolled]
    check(n == 3 and len(rolled) == 3 and all(int(x.getQuantity()) == 1 for x in rolled) and srcs == ["craft"] * 3,
          "Weapon_Spear_Crude outputs 3 -> 3 rolled singles (%d, %s, got%s)" % (n, srcs, got))
    ch2, cs2 = SIC(9), SIC(36)
    ch2.setItemStackForSlot(0, IS("Weapon_Spear_Crude", 5))
    n = int(CraftTask.rollIn(JArray(IC)([ch2, cs2]), JArray(IC)([cs2]), U1, "Weapon_Spear_Crude", IdMap(), 3, None, None))
    check(n == 0 and int(ch2.getItemStack(0).getQuantity()) == 5 and not bool(Data.hasAnyDoc(ch2.getItemStack(0).getMetadata())),
          "a merged stack of 5 for a craft of 3 is never rolled as one (q > cap - n)")
    # loot chest: per-item unidentified documents inside the same chest
    Cfg.PART_CHESTS = True
    chest = SIC(27)
    chest.setItemStackForSlot(0, IS("Weapon_Spellbook_Demon", 5))
    tagged = int(Tag.tagContainer(chest, "test"))
    items = [chest.getItemStack(i) for i in range(27) if chest.getItemStack(i) is not None and not chest.getItemStack(i).isEmpty()]
    check(len(items) == 5 and all(int(x.getQuantity()) == 1 and not bool(Data.identified(Data.gearDoc(x.getMetadata()))) for x in items)
          and tagged == 5, "a loot chest stack of 5 spellbooks -> 5 unidentified singles (%d tagged)" % tagged)
    # Identify all skips a refused row and goes on
    coins = {"take": 0}

    @JImplements("java.util.function.Function")
    class Take:
        @JOverride
        def apply(self, o):
            coins["take"] += 1
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class Purse:
        @JOverride
        def apply(self, o):
            return JLong(10 ** 9)

    bridge.put("coins:fn:take", Take())
    bridge.put("coins:fn:get", Purse())
    bridge.put("coins:fn:add", Purse())
    ih = SIC(9)
    ud2 = Roll.unidDoc("Weapon_Sword_Iron", 1, "drop")
    ih.setItemStackForSlot(0, Data.put(IS("Weapon_Spear_Crude", 2), Roll.unidDoc("Weapon_Spear_Crude", 1, "drop"), None))
    ih.setItemStackForSlot(1, Data.put(IS("Weapon_Sword_Iron", 1), ud2, None))
    by = JArray(IC)(6)
    by[0] = ih
    rows = ArrayList()
    for sl in (0, 1):
        rr = JArray(JInt)(2)
        rr[0] = 0
        rr[1] = sl
        rows.add(rr)
    rec = ArrayList()
    res = Ident.allIn(by, rows, U1, "tester", rec)
    # follow-up review 3 (changed check): a stack is no longer refused as such - with no storage / backpack room (none here) it
    # cannot give up one item: "Free 6 slots to split this stack"
    check(int(res[0]) == 1 and int(res[2]) == 1 and res[4] is None and "Free 6 slots to split this stack" in str(res[3]),
          "Identify all: the stack row without room is skipped, the next item is identified (%s)" % [str(x) for x in res])
    check(bool(Data.identified(Data.gearDoc(ih.getItemStack(1).getMetadata()))) and coins["take"] == 1, "exactly one paid identify")
    print("T. exploit 2 done")

    # ---------------- W. follow-up review of the fix commit e43c8bf
    BA_, BS_, BI_ = JClass("org.bson.BsonArray"), JClass("org.bson.BsonString"), JClass("org.bson.BsonInt32")
    ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    amf = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap").class_.getDeclaredField("assetMap")
    amf.setAccessible(True)
    idf = ItemC.class_.getDeclaredField("id")
    idf.setAccessible(True)
    msf = ItemC.class_.getDeclaredField("maxStack")
    msf.setAccessible(True)
    unsafe = uf.get(None)             # (section T reuses the name us for a container)

    def fake_item(iid, ms):
        """an Item asset with only an id + MaxStack (never constructed, like the fake store) so GearData.maxStack sees it"""
        it_ = unsafe.allocateInstance(ItemC.class_)
        idf.set(it_, iid)
        msf.setInt(it_, ms)
        amf.get(store.getAssetMap()).put(iid, it_)

    def with_mods(iid, pairs):
        dd = Roll.newDoc(iid, 0, True, "admin")
        arr = BA_()
        for k, v in pairs:
            md = BD()
            md.append("s", BS_(k))
            md.append("v", BI_(v))
            arr.add(md)
        dd.put("mods", arr)
        return dd

    def qty(c, i):
        s_ = c.getItemStack(i)
        return 0 if s_ is None or s_.isEmpty() else int(s_.getQuantity())

    FREE = int(Defs.FREE_KEEP)
    check(FREE == 5 and int(Defs.STACK_CEIL) == 30, "follow-up constants: 5 free slots, split ceiling MaxStack 30")

    # 1. gear.include guard
    for bad in ("Skyy_", "Weapon_", "Armor_", "Tool_", "skyy_", "Wea", "Sky"):
        check(Cfg.checkInclude("gear.include", "Skyy_Ring_," + bad) is not None, "W1: gear.include refuses %r" % bad)
    check(Cfg.checkInclude("gear.include", "Skyy_Ring_, Tool_Pickaxe_,Weapon_Arrow_") is None and Cfg.checkInclude("gear.include", "") is None
          and Cfg.checkInclude("gear.include", None) is None, "W1: narrow prefixes (6+ characters) pass the check")
    check(any("checkInclude" in str(x) for x in Rows.BCHECK), "W1: the gear.include row binds the check hook")
    check("6+" in helps["gear.include"], "W1: the row help names the 6-character rule")
    p = Props()
    p.setProperty("gear.include", "Skyy_,Weapon_,Wea,Skyy_Talisman_,Weapon_Arrow_,Skyy_Cook_Food_,Weapon_Knife_")
    Cfg.apply(p, False)
    check([str(x) for x in Cfg.incl()] == ["Skyy_Talisman_", "Weapon_Arrow_", "Skyy_Cook_Food_", "Weapon_Knife_"],
          "W1: the loader drops refused entries from a hand edit: %s" % [str(x) for x in Cfg.incl()])
    check(not any(bool(Data.isGear(x)) for x in ("Skyy_Menu", "Skyy_Market", "Skyy_Vault_Small", "Skyy_Accessory_Omni")),
          "W1: a bare Skyy_ entry pulls nothing in (menu, market, vault, accessory)")
    check(not bool(Data.isGear("Weapon_Arrow_Iron")) and not bool(Data.isGearMs("Weapon_Arrow_Iron", 40)) and not bool(Data.isGearMs("Weapon_Arrow_Iron", 1)),
          "W1: include never beats the ammo rule (Weapon_Arrow_ included, arrows stay ammo)")
    tal = "Skyy_Talisman_Luck"
    check(bool(Data.isGear(tal)) and str(Data.kindFor(tal)) == "equipment" and int(Data.slotOf(tal)) == 4,
          "W1: an included non-family id without a kind.prefix row is kind equipment (slot 4)")
    tst = Data.put(IS(tal, 1), Roll.newDoc(tal, 2, False, "drop"), U1)
    check(Hit.judge(U1, tst, False) is None and Hit.judge(U1, tst, True) is None, "W1: an unidentified included talisman never blocks a hit")
    check(not bool(Data.isGearMs("Skyy_Cook_Food_Pie", 64)) and not bool(Data.isGearMs(tal, 5)),
          "W1: an included id that stacks is gear only in Weapon_ / Armor_ / Tool_")
    check(not bool(Data.isGearMs("Weapon_Knife_Throw", 40)) and bool(Data.isGearMs("Weapon_Knife_Throw", 20)) and bool(Data.isGearMs("Weapon_Knife_Throw", 1)),
          "W1: an included family id is gear up to MaxStack 30, never above")
    fake_item("Skyy_Cook_Food_Pie", 64)
    fake_item("Weapon_Knife_Throw", 40)
    check(int(Data.maxStack("Skyy_Cook_Food_Pie")) == 64 and int(Data.maxStack("Nope_Item")) == -1, "W1: maxStack reads the Item asset (-1 = none)")
    check(not bool(Data.isGear("Skyy_Cook_Food_Pie")) and not bool(Data.isGear("Weapon_Knife_Throw")),
          "W1: through the asset: included food (64) and an included Weapon_ above 30 stay plain items")
    Cfg.apply(Props(), False)

    # 2. MaxStack ammo rule + split ceiling
    check(not bool(Data.ammoMs("Weapon_Shortbow_Bomb", 1)) and bool(Data.ammoMs("Weapon_Shortbow_Bomb", 20)),
          "W2: parts[1] rule only for single items; a stackable id keeps the any-token test")
    check(bool(Data.ammoMs("Weapon_Arrow_Iron", 40)) and bool(Data.ammoMs("Weapon_Arrow_Iron", 1)) and not bool(Data.ammoMs("Weapon_Spear_Iron", 30)),
          "W2: arrows are ammo either way, spears (30) are not")
    fake_item("Weapon_Knife_Stack", 40)
    fake_item("Weapon_Knife_Small", 20)
    check(bool(Data.isGear("Weapon_Knife_Stack")), "W2: a stackable Weapon_ id above 30 is still gear (gear.exclude decides)")
    kh, ks = SIC(3), SIC(9)
    kh.setItemStackForSlot(0, IS("Weapon_Knife_Stack", 10))
    m40 = int(Stamp.split(kh, 0, JArray(IC)([ks]), JArray(IC)([kh, ks]), U1, 0, 64, 0, None))
    check(m40 == 0 and qty(kh, 0) == 10 and all(qty(ks, i) == 0 for i in range(9)), "W2: split skips an id with MaxStack 40 (stack untouched)")
    kh.setItemStackForSlot(1, IS("Weapon_Knife_Small", 3))
    m20 = int(Stamp.split(kh, 1, JArray(IC)([ks]), JArray(IC)([kh, ks]), U1, 0, 64, 0, None))
    check(m20 == 2 and qty(kh, 1) == 1, "W2: an id with MaxStack 20 still splits (%d)" % m20)

    # 3. no hotbar, 5-slot floor, no passive split, actions take one item off a stack
    gv = code("GearStamp", "giveOf")
    check(any("Inventory.getStorage" in l for l in gv) and any("Inventory.getBackpack" in l for l in gv) and not any("getHotbar" in l for l in gv),
          "W3: giveOf = storage + backpack, never the hotbar")
    sc = code("GearStamp", "scan")
    check(not any("GearStamp.split" in l for l in sc) and not any("takeOne" in l for l in sc), "W3: the passive scan never splits")
    fc, fsto = SIC(9), SIC(6)
    fc.setItemStackForSlot(0, IS("Weapon_Spear_Crude", 3))
    nf = int(CraftTask.rollIn(JArray(IC)([fc, fsto]), JArray(IC)([fsto]), U1, "Weapon_Spear_Crude", IdMap(), 3, None, None))
    check(nf == 1 and qty(fc, 0) == 2 and sum(1 for i in range(6) if qty(fsto, i) == 0) == 5
          and not bool(Data.hasAnyDoc(fc.getItemStack(0).getMetadata())),
          "W3: craft rolls keep the 5-slot floor (6 free: one rolled single, the stack of 2 stays unrolled)")
    h3, s3 = SIC(9), SIC(7)
    h3.setItemStackForSlot(0, IS("Weapon_Spear_Crude", 5))
    mv3 = int(Stamp.split(h3, 0, JArray(IC)([s3]), JArray(IC)([h3, s3]), U1, 1, 4, FREE, None))
    free3 = sum(1 for i in range(7) if qty(s3, i) == 0)
    check(mv3 == 2 and qty(h3, 0) == 3 and free3 == 5 and all(qty(h3, i) == 0 for i in range(1, 9))
          and int(Stamp.countId(JArray(IC)([h3, s3]), "Weapon_Spear_Crude")) == 5,
          "W3: 7 free storage slots -> 2 singles, 5 stay free, nothing lands in the hotbar (%d moved)" % mv3)
    sp3 = IS("Weapon_Spear_Crude", 3)
    st3 = Stamp.stampStack(sp3, U1, None)
    d3 = Data.gearDoc(st3.getMetadata())
    check(int(st3.getQuantity()) == 3 and d3 is not None and int(Data.rarity(d3)) == 0, "W3: the passive stamp keeps a stack of identical items whole")
    check(Stamp.stackWhy(IS("Weapon_Spear_Crude", 1), JArray(IC)([]), "identify") is None
          and str(Stamp.stackWhy(sp3, JArray(IC)([SIC(4)]), "identify")) == "Free 2 slots to split this stack - identify works on one item at a time."
          and Stamp.stackWhy(sp3, JArray(IC)([SIC(6)]), "identify") is None, "W3: stackWhy needs 6 free slots (1 + the 5 kept free)")
    coins["take"] = 0
    ud3 = Roll.unidDoc("Weapon_Spear_Crude", 1, "drop")
    ud3.put("r", BS_("rare"))
    ih3, is3 = SIC(9), SIC(9)
    ih3.setItemStackForSlot(0, Data.put(IS("Weapon_Spear_Crude", 3), ud3, None))
    it3 = ih3.getItemStack(0)
    r3 = Ident.identify(ih3, 0, "Weapon_Spear_Crude", Forge.fp(it3), U1, "tester", False, JArray(IC)([is3, None]), JArray(IC)([ih3, is3]))
    rest3 = Data.gearDoc(is3.getItemStack(0).getMetadata()) if qty(is3, 0) else None
    check(int(r3[0]) == 1 and qty(ih3, 0) == 1 and bool(Data.identified(Data.gearDoc(ih3.getItemStack(0).getMetadata())))
          and qty(is3, 0) == 2 and rest3 is not None and not bool(Data.identified(rest3)) and int(Data.rarity(rest3)) == 2
          and coins["take"] == 1 and r3[6] is not None and int(r3[6][1]) == 0,
          "W3: Identify on a stack of 3 identifies one item in place, the other 2 move on unidentified, paid once (%s)" % str(r3[1]))
    ih4, is4 = SIC(9), SIC(5)
    ih4.setItemStackForSlot(0, Data.put(IS("Weapon_Spear_Crude", 3), ud3, None))
    it4 = ih4.getItemStack(0)
    r4 = Ident.identify(ih4, 0, "Weapon_Spear_Crude", Forge.fp(it4), U1, "tester", False, JArray(IC)([is4]), JArray(IC)([ih4, is4]))
    check(int(r4[0]) == 0 and str(r4[1]) == "Free 1 slot to split this stack - identify works on one item at a time." and qty(ih4, 0) == 3
          and coins["take"] == 1, "W3: no room -> refused before any coin moves, the stack is untouched (%s)" % str(r4[1]))
    rh, rs5 = SIC(9), SIC(9)
    rh.setItemStackForSlot(0, Data.put(IS("Weapon_Spear_Crude", 2), with_mods("Weapon_Spear_Crude", [("dmg", 3)]), U1))
    r5 = Forge.reforge(rh, 0, "Weapon_Spear_Crude", Forge.fp(rh.getItemStack(0)), U1, "tester", True, JArray(IC)([rs5]), JArray(IC)([rh, rs5]))
    check(int(r5[0]) == 1 and qty(rh, 0) == 1 and qty(rs5, 0) == 1 and int(Stamp.countId(JArray(IC)([rh, rs5]), "Weapon_Spear_Crude")) == 2,
          "W3: Reforge on a stack of 2 reforges one item, the other moves to a free slot (%s)" % str(r5[1]))
    ah, as_ = SIC(9), SIC(9)
    ah.setItemStackForSlot(0, Data.put(IS("Weapon_Spear_Crude", 3), ud3, None))
    ah.setItemStackForSlot(1, Data.put(IS("Weapon_Sword_Iron", 1), Roll.unidDoc("Weapon_Sword_Iron", 1, "drop"), None))
    by2 = JArray(IC)(6)
    by2[0] = ah
    by2[1] = as_
    rows2 = ArrayList()
    for sl in (0, 1):
        rr = JArray(JInt)(2)
        rr[0] = 0
        rr[1] = sl
        rows2.add(rr)
    coins["take"] = 0
    res2 = Ident.allIn(by2, rows2, U1, "tester", ArrayList())
    left = [x for c_ in (ah, as_) for i in range(9) for x in [c_.getItemStack(i)] if x is not None and not x.isEmpty()]
    check(int(res2[0]) == 4 and int(res2[2]) == 0 and coins["take"] == 4 and len(left) == 4 and all(int(x.getQuantity()) == 1 for x in left)
          and all(bool(Data.identified(Data.gearDoc(x.getMetadata()))) for x in left),
          "W3: Identify all works a stack of 3 item by item (4 paid identifies, 4 identified singles) %s" % [str(x) for x in res2])

    # 4. projectile attribution
    Track.SHOTS.clear()
    ms_ = int(JClass("java.lang.System").currentTimeMillis())
    strong = Data.put(IS("Weapon_Shortbow_Crude", 1), with_mods("Weapon_Shortbow_Crude", [("dmg", 20), ("str", 10)]), U1)
    weak = Data.put(IS("Weapon_Shortbow_Crude", 1), with_mods("Weapon_Shortbow_Crude", [("dmg", 2)]), U1)
    ra, rb = Shot(U1, strong, None, None), Shot(U1, weak, None, None)
    ra.at, rb.at = ms_ - 1000, ms_ - 3000
    Track.SHOTS.put(UUID.nameUUIDFromBytes(b"wa"), ra)
    check(str(Forge.fp(Track.pick(U1, None).main)) == str(Forge.fp(strong)), "W4: one live record -> that record")
    Track.SHOTS.put(UUID.nameUUIDFromBytes(b"wb"), rb)
    check(str(Forge.fp(Track.newest(U1).main)) == str(Forge.fp(strong)) and str(Forge.fp(Track.pick(U1, None).main)) == str(Forge.fp(weak)),
          "W4: two live records with different weapons -> the WEAKER one, not the newest")
    rc = Shot(U1, strong, None, None)
    rc.at = ms_ - 500
    Track.SHOTS.remove(UUID.nameUUIDFromBytes(b"wb"))
    Track.SHOTS.put(UUID.nameUUIDFromBytes(b"wc"), rc)
    pk = Track.pick(U1, None)
    check(pk is not None and int(pk.at) == int(rc.at), "W4: the same weapon twice -> the newest record")
    Track.SHOTS.clear()
    check(Track.pick(U1, None) is None, "W4: no live record -> none")
    check(any("norecord" in l for l in hs) and any("Gear.warnOnce" in l for l in hs), "W4: a projectile hit without a record logs one WARN")

    # 5 / 6. saved locks + the Recalculate nudge (bytecode)
    lt = code("GearLockSys", "tick")
    check(any("GearFx.PRIMED" in l for l in lt) and any("GearFx.hasLock" in l for l in lt), "W5: GearLockSys looks once for saved lock modifiers")
    ga = code("GearReady", "accept")
    check(any("GearFx.PRIMED" in l for l in ga), "W5: PlayerReady (join / world switch) clears PRIMED")
    check(any("GearFx.PRIMED" in l for l in code("GearFx", "forget")), "W5: disconnect forgets PRIMED")
    hl = code("GearFx", "hasLock")
    check(any("EntityStatMap.getModifier" in l for l in hl) and not bool(Fx.hasLock(None)), "W5: hasLock reads the lock modifiers (null map = none)")
    lk2 = code("GearFx", "locks")
    check(any("getStatModifiersManager" in l for l in lk2) and any("StatModifiersManager.scheduleRecalculate" in l for l in lk2),
          "W6: a lock that keeps waiting asks the engine for a Recalculate")

    # 7. unreadable quality.properties is left alone
    open(qf, "w").write("Skyy_Gear_Normal=forty\nSkyy_Gear_Rare=42\n")
    Qual.load(Paths.get(qf))
    Qual.CHECKED = False
    Qual.check(now)
    J("GearQual")(Qual.text(now)).run()
    time.sleep(0.4)
    check(bool(Qual.UNREAD) and Qual.OLD is None and open(qf).read() == "Skyy_Gear_Normal=forty\nSkyy_Gear_Rare=42\n",
          "W7: an unreadable quality.properties is never overwritten")
    open(qf, "w").write("")
    Qual.load(Paths.get(qf))
    check(not bool(Qual.UNREAD), "W7: an empty file is not 'unreadable' (it may be rewritten)")

    # 8. a throwing destination restores the source
    CtC = JClass("javassist.CtNewConstructor")
    CtM = JClass("javassist.CtNewMethod")
    tb = jp.makeClass("com.hypixel.hytale.server.core.inventory.container.SkyyTestThrowBox",
                      jp.get("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"))
    tb.addConstructor(CtC.make("public SkyyTestThrowBox(short n) { super(n); }", tb))
    tb.addMethod(CtM.make("public com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction setItemStackForSlot(short s, "
                          "com.hypixel.hytale.server.core.inventory.ItemStack st) { throw new IllegalStateException(\"test: no writes\"); }", tb))
    ThrowBox = JClass(tb.toClass(SIC.class_).getName())
    from jpype import JShort
    dstb = ThrowBox(JShort(9))
    srcb = SIC(3)
    srcb.setItemStackForSlot(0, IS("Weapon_Spear_Crude", 4))
    both = JArray(IC)([srcb, dstb])
    mv8 = int(Stamp.split(srcb, 0, JArray(IC)([dstb]), both, U1, 0, 64, 0, None))
    check(mv8 == 0 and qty(srcb, 0) == 4 and int(Stamp.countId(both, "Weapon_Spear_Crude")) == 4, "W8: split - destination write throws -> the source is restored")
    t8 = Stamp.takeOne(srcb, 0, JArray(IC)([dstb]), both, U1)
    check(t8 is None and qty(srcb, 0) == 4 and int(Stamp.countId(both, "Weapon_Spear_Crude")) == 4, "W8: takeOne - destination write throws -> the source is restored")
    tg = code("GearTag", "tagContainer")
    check(any("chestsplit" in l for l in tg), "W8: tagContainer catches its own split")

    # 9. gear:extra saturation, Damage % floor, hit never below 0
    xs = Stats.parseExtra(",".join(["str:1000000"] * 3000) + ",dmg:-500,cd:-400")
    check(int(xs[si("str")]) == 1000000 and int(xs[si("dmg")]) == -500, "W9: 3000 parts of str:1000000 saturate at 1,000,000 (no wrap)")
    t9 = JArray(JInt)(int(Defs.NS))
    t9[si("dmg")] = -500
    check(float(Hit.hitAmount(10.0, t9, False, 0.9, 0.9)) == 0.0, "W9: Damage % below -100 counts as -100 (hit 0, never negative)")
    t9[si("dmg")] = -50
    check(abs(float(Hit.hitAmount(10.0, t9, False, 0.9, 0.9)) - 5.0) < 1e-9, "W9: Damage -50 % halves the hit")
    t9[si("dmg")] = 0
    t9[si("str")] = -1000
    check(float(Hit.hitAmount(10.0, t9, False, 0.9, 0.9)) == 0.0, "W9: negative Strength never makes a hit negative")
    t9[si("str")] = 0
    t9[si("cc")] = 100
    t9[si("cd")] = -400
    check(float(Hit.hitAmount(10.0, t9, False, 0.0, 0.9)) == 0.0, "W9: a negative crit multiplier floors at 0")
    t9 = JArray(JInt)(int(Defs.NS))
    t9[si("rElem")] = 1000000000
    t9[si("fFire")] = 1000000000
    check(int(Hit.elemSum(t9)) == 1000000000, "W9: elemSum saturates")
    bridge.put("gear:extra:" + str(U2), "str:1000000")
    top9 = Data.put(IS("Weapon_Sword_Crude", 1), with_mods("Weapon_Sword_Crude", [("str", 2147483000)]), U2)
    t10 = Stats.totals(U2, top9, None, None, True)
    check(int(t10[si("str")]) == 1000000000, "W9: gear + gear:extra totals saturate instead of wrapping (%d)" % int(t10[si("str")]))
    bridge.remove("gear:extra:" + str(U2))

    # 10. negative armor sums cancelled (signed plan)
    check(plan(0, -5, False, 0, 0) == -5, "W10: a negative sum is cancelled at once (+5 max = safe)")
    check(plan(-5, 0, False, -5, 0) == -5 and plan(-5, 0, True, -5, 0) == -5 and plan(-5, 0, True, 0, 0) == 0,
          "W10: taking a negative cancel away waits for the tick + the synced engine")
    check(plan(-5, 12, True, 7, 7) == 12, "W10: a mixed sum grows like a positive one once synced")
    neg = {
        "equip an inactive -5 piece": [(0, 0, "ET"), (-5, -5, "LET")],
        "unequip an inactive -5 piece": [(-5, -5, "LET"), (0, 0, "LET")],
        "level up: inactive -5 becomes active": [(-5, -5, "LET"), (-5, 0, "T")],
        "class change: active -5 becomes inactive": [(-5, 0, "LET"), (-5, -5, "T")],
        "tick before the engine (unequip -5)": [(-5, -5, "LET"), (0, 0, "TLET")],
        "inactive +17 and -5 on one stat (sum +12), unequip the -5": [(12, 12, "LET"), (17, 17, "LET")],
    }
    for name, steps in neg.items():
        res = sim(steps)
        ok_ = True
        for i, (v, steady) in enumerate(res):
            prev_v = res[i - 1][0] if i else 100.0
            if v + 1e-6 < min(prev_v, steady):
                ok_ = False
        check(ok_, "W10 simulation keeps the current value: %s -> %s" % (name, res))
    ctl = StatModel(100.0, 100.0)
    ctl.put("lock", 5.0)          # the -5 piece goes on: its cancel first (max 105) ...
    ctl.put("Armor", -5.0)        # ... then the engine's -5 (max 100, value 100)
    ctl.put("lock", 0.0)          # unequip, cancel removed BEFORE Recalculate drops the -5: max 95 -> the value is clamped
    check(ctl.value == 95.0, "W10: the model sees the loss when a negative cancel goes before Recalculate (why it waits)")
    for k in ("coins:fn:take", "coins:fn:get", "coins:fn:add"):
        bridge.remove(k)
    print("W. follow-up review done")

    # ---------------- U / V. exploit 4 / 5: migration
    BI = JClass("org.bson.BsonInt32")
    rolls = BD()
    rolls.append("dmg", BI(30))
    rolls.append("str", BI(0))
    rolls.append("crit", BI(0))
    rolls.append("quality", BI(10))
    ma = Data.migrate("Armor_Iron_Chest", rolls)
    mw = Data.migrate("Weapon_Sword_Iron", rolls)
    check([str(m.asDocument().getString("s").getValue()) for m in Data.mods(ma)] == [] and int(Data.rarity(ma)) == 0,
          "exploit 4: migrated armor drops dmg and scores 0 without it")
    check([str(m.asDocument().getString("s").getValue()) for m in Data.mods(mw)] == ["dmg"] and int(Data.rarity(mw)) == 1,
          "a migrated weapon keeps dmg (score 33 -> Unique)")
    check(ma.containsKey("old") and int(ma.getDocument("old").getInt32("dmg").getValue()) == 30, "the whole old document stays in old")
    top = BD()
    top.append("dmg", BI(30))
    top.append("str", BI(25))
    top.append("crit", BI(15))
    Cfg.MIGRATE_CLAMP = False
    m0 = Data.migrate("Weapon_Sword_Crude", top)
    vals0 = dict((str(m.asDocument().getString("s").getValue()), int(m.asDocument().getInt32("v").getValue())) for m in Data.mods(m0))
    check(vals0 == {"dmg": 30, "str": 25, "cc": 15} and int(Data.rarity(m0)) == 4, "clampToLevel off: the rolls stay (LOCKED) %s" % vals0)
    Cfg.MIGRATE_CLAMP = True
    m1 = Data.migrate("Weapon_Sword_Crude", top)
    vals1 = dict((str(m.asDocument().getString("s").getValue()), int(m.asDocument().getInt32("v").getValue())) for m in Data.mods(m1))
    want = dict((k, int(Roll.bounds(si(k), 4, int(Lvl.level("Weapon_Sword_Crude", m1)))[1])) for k in ("dmg", "str", "cc"))
    check(vals1 == want and vals1 == {"dmg": 8, "str": 7, "cc": 4}, "clampToLevel on: capped at bounds(i, Fabled, level 0)[1] %s" % vals1)
    Cfg.MIGRATE_CLAMP = False
    print("U/V. migration done")


def main():
    if "--run" in sys.argv:
        run(arg("--run"))
        print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
        for f in FAILS:
            print("  FAILED:", f)
        sys.exit(1 if FAILS else 0)
    if not os.path.isfile(JAR):
        sys.exit("no jar at %s - build it first (python SkyyGear/build_skyygear_%s.py)" % (JAR, VERSION))
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--dir", SCRATCH], env=env)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s bare-JVM check:" % VERSION, "PASS" if p.returncode == 0 else "FAIL")
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
