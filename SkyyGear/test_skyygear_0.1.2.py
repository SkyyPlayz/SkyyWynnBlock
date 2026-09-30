"""Bare-JVM check for SkyyGear 0.1.2 (the 0.1.1 harness carried forward - sections A-Y unchanged apart from the 0.1.2 version strings
and the two roll entry points that gained an item-id overload - + section Z for 0.1.2), kept next to the build so the build report's
JVM claim can be re-run.

    python SkyyGear/test_skyygear_0.1.2.py [--jar <SkyyGear-0.1.2.jar>] [--dir <scratch folder>] [--live <config.properties>] [--keep]

--live = the config.properties to copy (read only) for test X(a); default: the "HUD mod" test world's Skyy_SkyyGear/config.properties.
Build the jar first (python SkyyGear/build_skyygear_0.1.2.py). A child process starts a fresh JVM (the game's own JRE, -Xverify:all,
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
  X  0.1.1: Skyy's level table (built-in, default file, loader, GearLevel.level, the row help) and the one-time config.properties
     update GearCfg.migrate011 on scratch copies: (a) the live file (exact bytes: six lines + the marker, History copy = the old
     bytes, six config-changes.log lines, the INFO line printed), (b) one hand-edited material kept + noted, (c) CRLF kept, (d) no
     file (nothing written; the loader's fresh 0.1.1 file carries the marker), (e) a second start changes nothing, (f) a file the
     config kit wrote in game (tset / set / remove through config:fn:SkyyGear + flush): custom kept, removed line stays removed, the
     kit's history + log lines kept, undo of an update line and of the kit's own line still work, old values set back after the
     update survive the next start, (g) the pure text step on edge cases (spacing, case, duplicates, continuation, templates, no
     header, no final newline, separators, trailing spaces, marker in a value), (i) the review of 0.1.1: finding 4 = a file ending
     inside a still-open continued entry gets the marker just before that entry (fixed cases + 3000 random files checked against
     java.util.Properties and byte for byte + migrate011 end to end, no marker per start), finding 3 = no rewrite unless
     config-history holds the old bytes (blocked History folder -> WARN + untouched, then updated; a failed write retried without a
     second copy; a copy whose index line failed still counts), (h) non-ASCII bytes + BOM kept, a folder in place of the file = WARN and nothing written;
     setup() order importRolls -> migrate011 -> migrateStat011 -> load -> CfgPub.start (bytecode)
  Y  0.1.1 stat defaults (OPEN-QUESTIONS LOCKED 2026-09-30: pool.later off, stat.levelFull 40): (a) row defaults + help (pool.later
     has no Placeholder claim any more - B's design-10 list drops it), the field initial values (bytecode), the loader fallback
     (missing / unreadable line), the level factor (full power from 40), the fresh default file (values + the stat marker above the
     pool.later help line; neither update touches it); (b) the live file on a scratch copy through both updates in the setup order:
     exact bytes (two value lines + the marker), the INFO line printed, two History versions, two scalar change-log lines, the
     loader + the ready line's stat part; (c) a second start changes nothing; (d) CRLF; (e) hand-edited values kept + noted (on,
     True, 45, 50.0) or silent (already new, missing lines -> the marker under the level marker); (f) the config kit's log op lists
     the two lines, Undo (set back) works and survives the next start; (g) History blocked -> no rewrite + WARN (also on the whole
     live start), then updated; a failed write retried without a second copy; no anchor -> WARN, untouched; (h) the pure text step
     on edge cases + 2000 random files checked against java.util.Properties and byte for byte; (i) EVERY roll path with pool.later
     off never yields a coming-later stat: GearRoll.rollMods over all slots / rarities / levels, /gear give (newDoc), crafting
     (craftDoc, the bench per-item roll GearCraftTask.rollIn, the SkyySacks /craft bridge gear:fn:roll for craft and other sources),
     mob drops (GearTag.unid + gear:fn:unid, then the Identify page GearIdent.identify and /gear identify GearRoll.identify), loot
     chests (GearTag.tagContainer + Identify all GearIdent.allIn), the Reforge page (GearForge.reforge paid) and /gear reroll (free),
     SkyyRolls migration (GearData.migrate / effective / the passive stamp) - with the coming-later weights raised to 100000 so one
     leak would dominate (a pool.later-on control run shows them), GearRoll.RNG is a never-seeded SecureRandom so "many seeds" =
     many independent rolls; the bytecode shows GearRoll.pool is the only way into a roll (callers of pool / GearData.mod /
     rollMods); gear that already has one keeps it until its next reforge (the lock), and loses it on that reforge
  Z  0.1.2 Charged Attack Damage: Z1 the stat row (after Crit Damage), the rows charged.on / spellFactor / log, loader clamps, the
     fresh default file, the tooltip (+ grey "off on this server"); Z2 hitAmount (x (1 + chg) after Strength / Magical Power, spells x
     (1 + 0.15 chg), crits after, clamp at 0, True / element damage never multiplied); Z3 the calculator index built from the REAL
     Assets.zip: the build's own Python walk vs the jar's collector on engine objects walked by the engine's InteractionManager.walkChain
     for every vanilla weapon + the More Crossbow Tiers crossbows (per calculator flags + class, launches, has / partial), and the
     runtime eligibility == the baked list; Z4 the per-hit rule on those real calculators (bow glow draw + headshot yes, partial draws
     no, volley / signature no, sword / axe / longsword / daggers + backstab / mace / Void scythe yes, crossbow 3rd bolt yes (trusted),
     the same bolt / a Class-tagged swing on an untrusted id no, unknown calculators, flail club / Crystal Ice no, prototype bow
     ambiguous no, legacy launches, charged.on off; GearCharged.judge on a real Damage when a bare JVM can build one); Z4b the review
     of 0.1.2 (finding 1: a picked launch record of another weapon - spear / sword record, bow arrow - never lets a partial draw count,
     the glow draw and the crossbow combo still count via the live records' walks, the Class-tag fallback is melee only, every live
     weapon that knows a step must call it charged, a legacy launch flag counts only with one weapon in the air; finding 2: the
     Vampire bow never counts / rolls; finding 3: one chgmiss WARN per weapon id; finding 4 + 5 in Z9 / Z6); Z5 roll
     eligibility per weapon family + armor / Equipment, charged.on off = never (every roll path, chg the only weighted stat), the baked fallback
     when the walk cannot run; Z6 the verifier's cases (single spellbook, single spear: the hand snapshot supplies the stack, its own
     stats + the charged flag now apply; stale / foreign / non-gear snapshots never; per player); Z7 the one-time update migrate012 on
     scratch copies (the live file through all three updates: exact bytes, INFO, History, no change-log line, the loader, Server Setup
     lists chg; second start; fresh file; CRLF; kept hand edits; missing anchors + the end-of-file continuation trap; 3000 random
     files vs java.util.Properties; History blocked); Z8 setup()'s file steps twice on a scratch copy of the whole live
     Skyy_SkyyGear folder (second start: every file but gear.log byte-identical); Z9 bytecode (setup order, the combat hook, the shot
     record, roll entry points, /gear charged admin); Z10 the class byte-compare 0.1.1 -> 0.1.2 (every difference listed)
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
VERSION = "0.1.2"
PKG = "com.skyy.gear."
LIVE_DEFAULT = os.path.join(os.environ.get("APPDATA", ""), "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyGear",
                            "config.properties")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "gear012", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv
LIVE = os.path.abspath(arg("--live", LIVE_DEFAULT))

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
    # (0.1.1 stat defaults: pool.later left the design-10 list - its default is Skyy's lock now; section Y checks its help)
    for k in ("craft.maxRarity", "migrate.maxRarity", "regen.periodMs", "level.armorNative"):
        check(helps[k].endswith(PH), "design 10: %s help ends with the Placeholder suffix" % k)
    check("Placeholder" not in helps["pool.later"], "0.1.1: pool.later help makes no Placeholder claim (Skyy's lock)")
    check(helps["stat"].startswith("dmg Damage, str Strength, mp Magical Power"), "design 7: the stat row help is a key legend")
    dt = str(Cfg.defaultsText())
    check("# dmg = Damage (weapon, %)" in dt and "# hprp = Health Regen % (weapon, armor, %)" in dt and "# lbonus = Loot Bonus" in dt,
          "design 7: config.properties names every stat key above its line")
    check("(spec 4.2)" not in str(Cfg.checkStat("stat[nope]", "1|1")) and "config.properties" in str(Cfg.checkStat("stat[nope]", "1|1")),
          "design 7: the unknown-stat message has no spec pointer")
    check("migrate.clampToLevel=false" in dt and "gear.include=" in dt and "kind.prefix.<id prefix>" in dt, "default file has the new keys")
    # 0.1.1: Skyy's level table in the default file, the marker under the levels header, the row help, the kit's version
    check(helps["level.material"] == "Level for gear of this material (first matching word of the id). Defaults: Skyy's table, 2026-09-30."
          and types["level.material"] == "table", "0.1.1: the Level by material row help (no Placeholder claim, <= 100)")
    check(all(("\nlevel.material.%s=%d\n" % tl) in dt for tl in (("Crude", 0), ("Wood", 0), ("Copper", 10), ("Bronze", 15), ("Iron", 15),
          ("Thorium", 20), ("Cobalt", 25), ("Adamantite", 35), ("Mithril", 40), ("Onyxium", 40))), "0.1.1: the default file has Skyy's table")
    check(("\n" + str(Cfg.LV_HEAD) + "\n" + str(Cfg.LV_MARK) + "\n") in dt and dt.startswith("# SkyyGear %s - " % VERSION),
          "0.1.1: the default file carries the update marker under the levels header + the %s header line" % VERSION)
    check(str(Rows.VERSION) == VERSION and str(Cfg.LV_WHO) == "SkyyGear 0.1.1", "0.1.1: kit VERSION (%s) + the update's fixed name" % VERSION)
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

    # ---------------- X. 0.1.1: Skyy's level table + the one-time config.properties update (GearCfg.migrate011)
    NEW = [("Crude", 0), ("Wood", 0), ("Copper", 10), ("Bronze", 15), ("Iron", 15), ("Thorium", 20), ("Cobalt", 25), ("Adamantite", 35),
           ("Mithril", 40), ("Onyxium", 40)]
    CH6 = [("Iron", 20, 15), ("Thorium", 30, 20), ("Cobalt", 35, 25), ("Adamantite", 40, 35), ("Mithril", 50, 40), ("Onyxium", 50, 40)]
    old_of = dict((t, o) for t, o, n in CH6)
    check([str(x) for x in Cfg.MAT_T] == [t for t, l in NEW] and [int(x) for x in Cfg.MAT_L] == [l for t, l in NEW],
          "X: built-in table = Skyy's 2026-09-30 table")
    check([int(x) for x in Cfg.MAT_OLD] == [old_of.get(t, l) for t, l in NEW], "X: MAT_OLD = the 0.1 placeholders")
    Cfg.apply(Props(), False)
    for iid, lv_ in (("Weapon_Sword_Crude", 0), ("Weapon_Staff_Wood", 0), ("Weapon_Sword_Copper", 10), ("Weapon_Sword_Bronze", 15),
                     ("Armor_Iron_Chest", 15), ("Weapon_Sword_Thorium", 20), ("Weapon_Sword_Cobalt", 25), ("Weapon_Sword_Adamantite", 35),
                     ("Armor_Mithril_Head", 40), ("Weapon_Sword_Onyxium", 40)):
        check(int(Lvl.level(iid, None)) == lv_, "X: GearLevel.level(%s) = %d (built-in defaults)" % (iid, lv_))
    LVM, LVH = str(Cfg.LV_MARK), str(Cfg.LV_HEAD)
    check(LVM == "# SkyyGear 0.1.1 level defaults (Skyy 2026-09-30): Crude 0, Wood 0, Copper 10, Bronze 15, Iron 15, Thorium 20, Cobalt 25, "
          "Adamantite 35, Mithril 40, Onyxium 40", "X: the marker text")
    dflt = str(Cfg.defaultsText())
    # the 0.1.2 default file without its 0.1.2 lines (the chg stat line + the charged block) = what sections X / Y compared with in 0.1.1
    _chl = set(["# chg = Charged Attack Damage (weapon, armor, %)", "stats.chg=30,5", str(Cfg.CH_MARK)] + [str(x) for x in Cfg.CH_ROWC]
               + [str(x) for x in Cfg.CH_ROWL])
    dflt011 = "\n".join(l_ for l_ in dflt.split("\n") if l_ not in _chl)
    INFO6 = ("config.properties updated to the 0.1.1 level table: Iron 20 -> 15, Thorium 30 -> 20, Cobalt 35 -> 25, Adamantite 40 -> 35, "
             "Mithril 50 -> 40, Onyxium 50 -> 40 (the old file is in config-history; Server Setup -> Changes can undo each line)")
    XD = os.path.join(SCRATCH, "work", "x011")
    Log.FILE = None

    def case(name, data):
        """<XD>/<name>/mods/Skyy_SkyyGear/config.properties with these bytes (None = no file); GearCfg.FILE / DIR point there"""
        shutil.rmtree(os.path.join(XD, name), ignore_errors=True)
        d_ = os.path.join(XD, name, "mods", "Skyy_SkyyGear")
        os.makedirs(d_)
        f_ = os.path.join(d_, "config.properties")
        if data is not None:
            open(f_, "wb").write(data)
        Cfg.DIR = Paths.get(d_)
        Cfg.FILE = Paths.get(f_)
        return d_, f_

    def rb(p):
        return open(p, "rb").read()

    def baks(d_):
        hd = os.path.join(d_, "config-history")
        return sorted(x for x in os.listdir(hd) if x.endswith(".bak")) if os.path.isdir(hd) else []

    def lines_of(p):
        return [l for l in open(p, encoding="utf-8").read().split("\n") if l.strip()] if os.path.isfile(p) else []

    def idx(d_):
        return lines_of(os.path.join(d_, "config-history", "index.log"))

    def clog(d_):
        return lines_of(os.path.join(d_, "config-changes.log"))

    def upd(text, changes):
        """the expected update: these (material, old, new) value lines changed + the marker under the levels header, endings kept"""
        nl = "\r\n" if "\r\n" in text else "\n"
        out = text
        for t, o, n in changes:
            a_ = nl + "level.material.%s=%d%s" % (t, o, nl)
            assert out.count(a_) == 1, (t, o)
            out = out.replace(a_, nl + "level.material.%s=%d%s" % (t, n, nl))
        assert out.count(LVH + nl) == 1
        return out.replace(LVH + nl, LVH + nl + LVM + nl)

    def info_for(changes):
        return ("config.properties updated to the 0.1.1 level table: " + ", ".join("%s %d -> %d" % c for c in changes)
                + " (the old file is in config-history; Server Setup -> Changes can undo each line)")

    check(info_for(CH6) == INFO6, "X: expected INFO text helper")
    live = None
    if not os.path.isfile(LIVE):
        check(False, "X(a): the live config.properties is missing: %s (pass --live <file>)" % LIVE)
    else:
        live = rb(LIVE)            # read only: every test below works on scratch copies
    if live is not None:
        lt = live.decode("latin-1")
        # (a) the exact live file
        d, f = case("a-live", live)
        exp = upd(lt, CH6)
        res = str(Cfg.migrate011())
        got = rb(f)
        check(got == exp.encode("latin-1"), "X(a): the live file -> exactly six value lines changed + the marker, every other byte kept")
        check(res.split("\n") == [INFO6], "X(a): one INFO line: %r" % res)
        print("X. INFO line the live file produces: [SkyyGear] " + res.split("\n")[0])
        b = baks(d)
        check(len(b) == 1 and rb(os.path.join(d, "config-history", b[0])) == live, "X(a): History keeps the old file (one .bak = the old bytes)")
        ix = idx(d)
        check(len(ix) == 1 and ix[0].split("\t")[1] == "Skyy_SkyyGear/config.properties"
              and ix[0].split("\t")[3:] == ["SkyyGear 0.1.1", "before the 0.1.1 level table update"], "X(a): index.log names the update: %s" % ix)
        cl = clog(d)
        want = [["SkyyGear 0.1.1", "-", "update", "level.material[%s]" % t, str(o), str(n), "ok"] for t, o, n in CH6]
        check([l.split("\t")[1:] for l in cl] == want and all(re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$", l.split("\t")[0]) for l in cl),
              "X(a): six config-changes.log lines in the kit's format (Undo-able ok lines): %s" % cl)
        check(not os.path.exists(f + ".tmp"), "X(a): no temp file left")
        Cfg.load()
        check(all(int(Cfg.MAT.get(t.lower())) == n for t, o, n in CH6) and int(Cfg.MAT.get("copper")) == 10, "X(a): the loader reads the new levels")
        check(str(Cfg.matText()) == "Crude 0, Wood 0, Copper 10, Bronze 15, Iron 15, Thorium 20, Cobalt 25, Adamantite 35, Mithril 40, Onyxium 40",
              "X(a): the ready line's table: " + str(Cfg.matText()))
        same = exp.replace("# SkyyGear 0.1 - ", "# SkyyGear %s - " % VERSION, 1) == dflt011
        print("X. the level-updated live file %s the 0.1.1 default file apart from the version in line 1 (the stat defaults follow in Y)"
              % ("EQUALS" if same else "DIFFERS FROM"))
        # (e) a second start
        check(str(Cfg.migrate011()) == "" and rb(f) == got and len(baks(d)) == 1 and len(idx(d)) == 1 and len(clog(d)) == 6,
              "X(e): a second start changes nothing (file, History, change log)")

        # (b) one hand-edited material
        tb = lt.replace("\nlevel.material.Cobalt=35\n", "\nlevel.material.Cobalt=30\n")
        check(tb != lt, "X(b): test file has Cobalt=30")
        d, f = case("b-custom", tb.encode("latin-1"))
        ch5 = [c for c in CH6 if c[0] != "Cobalt"]
        res = str(Cfg.migrate011()).split("\n")
        check(rb(f) == upd(tb, ch5).encode("latin-1"), "X(b): Cobalt=30 kept, the other five updated, every other byte kept")
        check(res == [info_for(ch5), "level.material.Cobalt=30 kept (custom) - the 0.1.1 default is 25"], "X(b): INFO + the kept note: %s" % res)
        check([l.split("\t")[4] for l in clog(d)] == ["level.material[%s]" % c[0] for c in ch5], "X(b): five change-log lines, none for Cobalt")
        Cfg.load()
        check(int(Cfg.MAT.get("cobalt")) == 30 and int(Cfg.MAT.get("iron")) == 15, "X(b): the loader: Cobalt 30, Iron 15")
        check(str(Cfg.migrate011()) == "", "X(b): the kept note is logged once (the next start does nothing)")

        # (c) CRLF
        tc = lt.replace("\n", "\r\n")
        d, f = case("c-crlf", tc.encode("latin-1"))
        res = str(Cfg.migrate011())
        gc = rb(f)
        check(gc == upd(tc, CH6).encode("latin-1") and gc.count(b"\n") == gc.count(b"\r\n") and gc.replace(b"\r\n", b"\n") == got,
              "X(c): a CRLF file gets the same update, every line (the marker too) still ends CRLF")
        check(res == INFO6, "X(c): same INFO line")
        Cfg.load()
        check(int(Cfg.MAT.get("mithril")) == 40, "X(c): the loader reads the CRLF file")

    # (d) no file
    d, f = case("d-nofile", None)
    check(str(Cfg.migrate011()) == "" and not os.path.exists(f) and not os.path.exists(os.path.join(d, "config-history"))
          and not os.path.exists(os.path.join(d, "config-changes.log")), "X(d): no file -> the update writes nothing")
    Cfg.load()
    fd = rb(f) if os.path.isfile(f) else b""
    check(fd == dflt.encode("utf-8") and LVM.encode("ascii") in fd, "X(d): the loader writes the 0.1.1 default file, marker included")
    check(str(Cfg.migrate011()) == "" and rb(f) == fd, "X(d): the next start leaves the fresh file alone")
    check(int(Cfg.MAT.get("iron")) == 15 and int(Cfg.MAT.get("onyxium")) == 40, "X(d): fresh file levels")
    Cfg.FILE = None
    check(str(Cfg.migrate011()) == "", "X(d): no FILE set -> nothing")

    # (f) a file the config kit wrote in game (Server Setup): tset / set / remove through config:fn:SkyyGear, then 0.1.1 starts
    if live is not None:
        CfgPub = J("CfgPub")
        OA = JArray(JObject)
        d, f = case("f-kit", live)
        mods = os.path.dirname(d)
        Cfg.load()
        CfgPub.start(Paths.get(mods), None)
        fn = bridge.get("config:fn:SkyyGear")
        r1 = fn.apply(OA(["tset", "level.material", "Iron", "25", None, "console", "yes", "console"]))
        r2 = fn.apply(OA(["set", "part.gate", "false", None, "console", "yes", "console"]))
        r3 = fn.apply(OA(["remove", "level.material", "Onyxium", None, "console", "yes", "console"]))
        check(all(r_ is not None and str(r_[0]) == "ok" for r_ in (r1, r2, r3)), "X(f): in-game changes accepted: %s" % [
            None if r_ is None else str(r_[2]) for r_ in (r1, r2, r3)])
        CfgPub.flush()
        kt = rb(f).decode("latin-1")
        kit_log = clog(d)
        check("\nlevel.material.Iron=25\n" in kt and "\npart.gate=false\n" in kt and "level.material.Onyxium" not in kt and len(baks(d)) == 1
              and len(kit_log) == 3, "X(f): the kit wrote the file (Iron 25, part.gate off, Onyxium removed), 1 History copy, 3 log lines")
        res = str(Cfg.migrate011()).split("\n")
        ch4 = [("Thorium", 30, 20), ("Cobalt", 35, 25), ("Adamantite", 40, 35), ("Mithril", 50, 40)]
        check(rb(f) == upd(kt, ch4).encode("latin-1"),
              "X(f): four updated; Iron 25, part.gate=false and the kit's line layout kept; the removed Onyxium line is not added back")
        check(res == [info_for(ch4), "level.material.Iron=25 kept (custom) - the 0.1.1 default is 15"], "X(f): INFO + kept note: %s" % res)
        cl = clog(d)
        check(cl[:3] == kit_log and [l.split("\t")[4] for l in cl[3:]] == ["level.material[%s]" % c[0] for c in ch4],
              "X(f): the kit's own log lines stay as they were, four update lines after them")
        b = baks(d)
        check(len(b) == 2 and rb(os.path.join(d, "config-history", b[0])) == live and rb(os.path.join(d, "config-history", b[1])) == kt.encode("latin-1"),
              "X(f): the kit's History copy stays, the update adds one (= the kit-written file)")
        # the next start: loader + kit read the updated file; Undo the way SkyyMenu sends it (tset back to the log line's old value)
        Cfg.load()
        CfgPub.start(Paths.get(mods), None)
        lg = [str(x) for x in fn.apply(OA(["log", Integer.valueOf(20)]))]
        check(sum(1 for l in lg if "\tupdate\tlevel.material[" in l and l.endswith("\tok")) == 4 and len(lg) == 7,
              "X(f): the kit's log op lists the four update lines as ok (SkyyMenu offers Undo on them)")
        ks = fn.apply(OA(["keys", "level.material", ""]))
        now_ = dict(zip([str(x) for x in ks[0]], [str(x) for x in ks[2]]))
        check(now_.get("Thorium") == "20" and now_.get("Iron") == "25" and "Onyxium" not in now_, "X(f): kit memory = the updated file: %s" % now_)
        u1 = fn.apply(OA(["tset", "level.material", "Thorium", "30", None, "console", "yes", "console"]))    # Undo 'Thorium 30 -> 20'
        u2 = fn.apply(OA(["tset", "level.material", "Iron", "20", None, "console", "yes", "console"]))       # Undo the kit's 'Iron 20 -> 25'
        CfgPub.flush()
        kt2 = rb(f).decode("latin-1")
        check(str(u1[0]) == "ok" and str(u2[0]) == "ok" and "\nlevel.material.Thorium=30\n" in kt2 and "\nlevel.material.Iron=20\n" in kt2,
              "X(f): Undo of an update line and of the kit's older line both work")
        check(str(Cfg.migrate011()) == "" and rb(f).decode("latin-1") == kt2, "X(f): old numbers set back after the update survive the next start")
        Cfg.load()
        check(int(Cfg.MAT.get("thorium")) == 30 and int(Cfg.MAT.get("iron")) == 20 and Cfg.MAT.get("onyxium") is None
              and int(Cfg.MAT.get("cobalt")) == 25, "X(f): loader after the undos: Thorium 30, Iron 20, no Onyxium line, Cobalt 25")

    # (g) the pure text step on edge cases
    BS = chr(92)
    H = LVH + "\n"

    def lv(t):
        r_ = Cfg.lvUpdate(t)
        return None if r_ is None else (str(r_[0]), str(r_[1]), [str(x) for x in r_[2]], [str(x) for x in r_[3]])

    r = lv(H + "level.material.Iron = 20\nlevel.material.thorium:30\nlevel.material.Cobalt 35\nlevel.material.MITHRIL=50   \n")
    check(r[0] == H + LVM + "\nlevel.material.Iron = 15\nlevel.material.thorium:20\nlevel.material.Cobalt 25\nlevel.material.MITHRIL=40\n"
          and r[3] == ["Iron", "20", "15", "thorium", "30", "20", "Cobalt", "35", "25", "MITHRIL", "50", "40"],
          "X(g): spacing, ':' / ' ' separators, any-case entry words and trailing spaces: value text replaced only (%r)" % (r,))
    r = lv(H + "level.material.Iron=20\nx=1\nlevel.material.Iron=22\n")
    check(r[0] == H + LVM + "\nlevel.material.Iron=20\nx=1\nlevel.material.Iron=22\n" and r[3] == []
          and r[2] == ["level.material.Iron=22 kept (custom) - the 0.1.1 default is 15"], "X(g): last line wins - custom 22 kept, the dead 20 left")
    r = lv(H + "level.material.Iron=22\nlevel.material.Iron=20\n")
    check(r[0] == H + LVM + "\nlevel.material.Iron=22\nlevel.material.Iron=15\n" and r[3] == ["Iron", "20", "15"], "X(g): last line 20 -> updated")
    r = lv(H + "level.material.Iron=2" + BS + "\n    0\nlevel.material.Mithril=50\n")
    check(r[0] == H + LVM + "\nlevel.material.Iron=2" + BS + "\n    0\nlevel.material.Mithril=40\n" and r[3] == ["Mithril", "50", "40"]
          and r[2] == ["level.material.Iron=20 kept (custom) - the 0.1.1 default is 15"], "X(g): a continued entry is never rewritten (noted)")
    r = lv(H + "a=x" + BS + "\nlevel.material.Iron=20\n")
    check(r[0] == H + LVM + "\na=x" + BS + "\nlevel.material.Iron=20\n" and r[3] == [] and r[2] == [], "X(g): a continuation line is not a key")
    r = lv(H + "#level.material.Iron=20\n! level.material.Mithril=50\n")
    check(r[0] == H + LVM + "\n#level.material.Iron=20\n! level.material.Mithril=50\n" and r[1] == "" and r[2] == [] and r[3] == [],
          "X(g): commented / template lines never change (a missing line stays missing)")
    r = lv(H + "level.material.Iron=15\nlevel.material.Copper=12\nlevel.material.Gold=20\nlevel.material.=20\nlevel.material.Onyxium=20.0\n")
    check(r[0] == H + LVM + "\nlevel.material.Iron=15\nlevel.material.Copper=12\nlevel.material.Gold=20\nlevel.material.=20\nlevel.material.Onyxium=20.0\n"
          and r[3] == [] and r[2] == ["level.material.Onyxium=20.0 kept (custom) - the 0.1.1 default is 40"],
          "X(g): already new / unchanged material / unknown word / empty word untouched and silent; 20.0 is custom")
    r = lv("a=1\nlevel.material.Iron=20\nb=2\n")
    check(r[0] == "a=1\n" + LVM + "\nlevel.material.Iron=15\nb=2\n", "X(g): no levels header -> marker before the first level.material line")
    check(lv("a=1\nb=2\n")[0] == "a=1\nb=2\n" + LVM + "\n", "X(g): no header, no level lines -> marker at the end")
    check(lv("a=1")[0] == "a=1\n" + LVM and lv("a=1\r\nb=2")[0] == "a=1\r\nb=2\r\n" + LVM and lv("")[0] == LVM + "\n",
          "X(g): no final newline stays so (CRLF kept); empty text")
    check(lv(LVH + "\r\nlevel.material.Iron=20\n")[0] == LVH + "\r\n" + LVM + "\r\nlevel.material.Iron=15\n", "X(g): the marker takes the header's CR")
    r = lv(H + "level.material.Iron=20\n\n# ---- changed in game (SkyWynn Menu) ----\nlevel.material.Mithril=50\n")
    check(r[0] == H + LVM + "\nlevel.material.Iron=15\n\n# ---- changed in game (SkyWynn Menu) ----\nlevel.material.Mithril=40\n",
          "X(g): a line the kit appended under its 'changed in game' header is updated in place")
    check(Cfg.lvUpdate("# SkyyGear 0.1.1 level defaults, anything\nlevel.material.Iron=20\n") is None
          and Cfg.lvUpdate("x=1\n  ! SkyyGear 0.1.1 level defaults\n") is None, "X(g): a comment line with the marker id = already done")
    r = lv("note=SkyyGear 0.1.1 level defaults\nlevel.material.Iron=20\n")
    check(r is not None and "level.material.Iron=15" in r[0], "X(g): the marker id inside a value does not count")

    # (i) review of 0.1.1, finding 4: a file that ends inside a still-open continued entry (the append-at-end branch) gets the marker
    # just before that entry; java.util.Properties reads the same values before and after, the marker is a comment, a second pass
    # finds it, every other byte is kept
    StringReader = JClass("java.io.StringReader")
    MID = str(Cfg.LV_MARK_ID)

    def props(t):
        p_ = Props()
        p_.load(StringReader(t))
        return dict((str(k_), str(p_.getProperty(k_))) for k_ in p_.stringPropertyNames())

    def marker_ok(t, out, rows=()):
        """Properties(out) = Properties(t) + the updated rows, no key / value holds the marker id, the next pass does nothing"""
        want = props(t)
        for i_ in range(0, len(rows), 3):
            want["level.material." + rows[i_]] = rows[i_ + 2]
        got_ = props(out)
        return (got_ == want and not any(MID in k_ or MID in v_ for k_, v_ in got_.items()) and Cfg.lvUpdate(out) is None
                and out.count(MID) == 1)

    for t, want in (
            ("a=abc" + BS, LVM + "\na=abc" + BS),
            ("a=abc" + BS + "\n", LVM + "\na=abc" + BS + "\n"),
            ("x=1\r\na=abc" + BS + "\r\n", "x=1\r\n" + LVM + "\r\na=abc" + BS + "\r\n"),
            ("x=1\r\na=abc" + BS, "x=1\r\n" + LVM + "\r\na=abc" + BS),
            ("x=1\na=x" + BS + "\n  y" + BS + "\n", "x=1\n" + LVM + "\na=x" + BS + "\n  y" + BS + "\n"),
            ("# c\na=x" + BS + "\n#c" + BS, "# c\n" + LVM + "\na=x" + BS + "\n#c" + BS),        # '#c\' is a continuation line here
            ("a=1\n" + BS + "\n", "a=1\n" + LVM + "\n" + BS + "\n"),                            # a lone backslash (Properties: key "")
            ("#c" + BS + "\n", "#c" + BS + "\n" + LVM + "\n"),                                  # a comment never continues: at the end
            ("a=1\n#c" + BS, "a=1\n#c" + BS + "\n" + LVM),
            ("a=abc" + BS + BS + "\n", "a=abc" + BS + BS + "\n" + LVM + "\n"),                  # an even count = an escaped backslash
            ("a=x" + BS + "\n#c\n", "a=x" + BS + "\n#c\n" + LVM + "\n")):                       # the entry ended before the last line
        r = lv(t)
        check(r is not None and r[0] == want and marker_ok(t, r[0]), "X(i): finding 4 - %r -> %r (got %r)" % (t, want, r and r[0]))
    # the same rule over random files (fixed seed): pieces with odd / even backslashes, comments ending in one, lone backslashes,
    # blank lines, level lines (one spelling per material, so Properties keys match the rows), LF / CRLF, with / without final newline
    import random
    rnd = random.Random(20260930)
    pieces = ["a=1", "b=x" + BS, "c=y" + BS + BS, "#c" + BS, "# note", "", "   z" + BS, BS, "d:e", "  f g" + BS, "!x" + BS,
              "level.material.Iron=20", "level.material.Mithril=50", "level.material.Copper=10", "level.material.Iron=22", LVH]
    def bytes_kept(t, out):
        """out = t + exactly one marker line; only level.material value lines differ (a CR may join the last line when the marker
        is appended after a last line without newline)"""
        ol, tl = out.split("\n"), t.split("\n")
        mi = [i_ for i_, x_ in enumerate(ol) if MID in x_]
        if len(mi) != 1 or ol[mi[0]].rstrip("\r") != LVM:
            return False
        m_ = mi[0]
        rest = ol[:m_] + ol[m_ + 1:]
        if len(rest) != len(tl):
            return False
        for i_, (a_, b_) in enumerate(zip(rest, tl)):
            if a_ == b_ or (a_.startswith("level.material.") and b_.startswith("level.material.")):
                continue
            if i_ == len(tl) - 1 and m_ == len(ol) - 1 and a_ == b_ + "\r":
                continue
            return False
        return True

    bad = []
    for n_ in range(3000):
        ls_ = [rnd.choice(pieces) for _q in range(rnd.randint(0, 7))]
        if n_ % 2 == 0:
            ls_ = [p_ for p_ in ls_ if not p_.startswith("level.material.") and p_ != LVH]      # half the cases hit the end branch
        if BS in ls_:
            # a lone backslash line continues into the next line and adds nothing, so java.util.Properties takes the NEXT line's key;
            # the kit's CfgFile.key reads only the first physical line (key ""). A kit-wide limit, not the update's: no level lines here
            ls_ = [p_ for p_ in ls_ if not p_.startswith("level.material.")]
        nl_ = "\r\n" if rnd.random() < 0.3 else "\n"
        t = nl_.join(ls_) + (nl_ if rnd.random() < 0.6 else "")
        r = lv(t)
        if r is None or not marker_ok(t, r[0], r[3]) or not bytes_kept(t, r[0]):
            bad.append(t)
    check(not bad, "X(i): finding 4 - 3000 random files: same Properties values (+ updated rows), marker = one comment line and the "
                   "only line added, the next pass does nothing (%d bad, first %r)" % (len(bad), bad[:1]))
    # migrate011 end to end: such a file is updated once; before the fix the next start added another marker every time
    ti = b"a=1\nb=abc\\"
    d, f = case("i-open", ti)
    res = str(Cfg.migrate011())
    check(res == "config.properties: no level.material line still had its 0.1 default - nothing changed (0.1.1 level table marker added)"
          and rb(f) == b"a=1\n" + LVM.encode("ascii") + b"\nb=abc\\", "X(i): finding 4 - migrate011 on a file ending in a continued entry")
    check(str(Cfg.migrate011()) == "" and rb(f) == b"a=1\n" + LVM.encode("ascii") + b"\nb=abc\\" and len(baks(d)) == 1,
          "X(i): finding 4 - the next start finds the marker (no second marker, no second History copy)")

    # (i) finding 3: the update only rewrites the file once config-history holds the old bytes
    tx = ("a=1\n" + H + "level.material.Iron=20\nlevel.material.Mithril=50\n").encode("latin-1")
    info2 = info_for([("Iron", 20, 15), ("Mithril", 50, 40)])
    d, f = case("i-nohist", tx)
    open(os.path.join(d, "config-history"), "wb").write(b"blocker")          # a plain file where the History folder goes
    glf = os.path.join(XD, "i-gear.log")                                      # Gear.warn's gear.log copy (no server logger here)
    Log.FILE = Paths.get(glf)
    res = str(Cfg.migrate011())
    Log.flush()
    Log.FILE = None
    gl = open(glf, encoding="utf-8").read() if os.path.isfile(glf) else ""
    check(res == "" and rb(f) == tx and not os.path.exists(os.path.join(d, "config-changes.log"))
          and not os.path.exists(f + ".tmp"), "X(i): finding 3 - config-history cannot be written -> file untouched, no change-log lines")
    check("WARN config.properties NOT updated to the 0.1.1 level table: the old file could not be kept in " in gl
          and "(the file is used as it is; the next start tries again)" in gl and "CONFIG 0.1.1" not in gl,
          "X(i): finding 3 - the WARN line says why and that the next start retries: %r" % gl)
    os.remove(os.path.join(d, "config-history"))
    res = str(Cfg.migrate011())
    b = baks(d)
    check(res == info2 and len(b) == 1 and rb(os.path.join(d, "config-history", b[0])) == tx and len(clog(d)) == 2
          and LVM.encode("ascii") in rb(f), "X(i): finding 3 - the next start (History writable again) updates; the old bytes are kept: %r" % res)
    # a failed file write after the History copy: the retry reuses the equal copy (snapshot skips it, lvSaved accepts it)
    d, f = case("i-retry", tx)
    os.makedirs(f + ".tmp")                                                   # the kit's temp file cannot be created
    ok1 = str(Cfg.migrate011()) == "" and rb(f) == tx and len(baks(d)) == 1 and not os.path.exists(os.path.join(d, "config-changes.log"))
    os.rmdir(f + ".tmp")
    res = str(Cfg.migrate011())
    b = baks(d)
    check(ok1 and res == info2 and len(b) == 1 and rb(os.path.join(d, "config-history", b[0])) == tx and len(idx(d)) == 1
          and len(clog(d)) == 2, "X(i): finding 3 - a failed write keeps the file; the retry updates without a second History copy: %r" % res)
    # a copy whose index.log line failed still holds the bytes: the update goes on (no endless retry on an orphan copy)
    d, f = case("i-noindex", tx)
    os.makedirs(os.path.join(d, "config-history", "index.log"))              # a folder where index.log goes
    res = str(Cfg.migrate011())
    b = baks(d)
    check(res == info2 and len(b) == 1 and rb(os.path.join(d, "config-history", b[0])) == tx,
          "X(i): finding 3 - a History copy without its index line still counts: %r" % res)

    # (h) bytes: BOM + ISO-8859-1 bytes + a \u escape kept; a folder in place of the file
    rawh = (b"\xef\xbb\xbf# caf\xe9 \xff\r\n" + LVH.encode("ascii") + b"\r\nlevel.material.Iron=20\r\nname=\\u00e9t\xe9\r\n")
    d, f = case("h-bytes", rawh)
    Cfg.migrate011()
    check(rb(f) == b"\xef\xbb\xbf# caf\xe9 \xff\r\n" + LVH.encode("ascii") + b"\r\n" + LVM.encode("ascii")
          + b"\r\nlevel.material.Iron=15\r\nname=\\u00e9t\xe9\r\n", "X(h): BOM, ISO-8859-1 bytes and escapes kept byte for byte")
    d, f = case("h-folder", None)
    os.makedirs(f)
    check(str(Cfg.migrate011()) == "" and os.path.isdir(f) and not os.path.exists(os.path.join(d, "config-history")),
          "X(h): a folder named config.properties -> WARN, nothing written, no exception")
    Cfg.FILE = None
    Cfg.DIR = None

    # setup() order (bytecode): SkyyRolls cost import -> the update -> the loader -> the config kit; the ready line reads the table
    su = code("SkyyGearPlugin", "setup")

    def pos(needle):
        return next((i for i, l in enumerate(su) if needle in l), -1)

    check(0 <= pos("GearCfg.importRolls") < pos("GearCfg.migrate011") < pos("GearCfg.migrateStat011") < pos("GearCfg.load") < pos("CfgPub.start"),
          "X/Y: setup() runs importRolls -> migrate011 -> migrateStat011 -> load -> CfgPub.start")
    check(pos("GearCfg.load") < pos("GearCfg.matText") < pos("GearCfg.statText") < pos("CfgPub.start"),
          "X/Y: the ready line lists the loaded level table, then the loaded stat defaults")
    print("X. 0.1.1 level table + update done")

    # ---------------- Y. 0.1.1 stat defaults: pool.later off + stat.levelFull 40 (defaults, loader, one-time update, every roll path)
    STM, STID = str(Cfg.ST_MARK), str(Cfg.ST_MARK_ID)
    check(STM == "# SkyyGear 0.1.1 stat defaults (Skyy 2026-09-30): coming-later stats never roll (pool.later false), full modifier power "
          "from item level 40 (stat.levelFull 40, Mithril / Onyxium)", "Y: the stat marker text")
    check([str(x) for x in Cfg.ST_KEY] == ["pool.later", "stat.levelFull"] and [str(x) for x in Cfg.ST_OLD] == ["true", "50"]
          and [str(x) for x in Cfg.ST_NEW] == ["false", "40"], "Y: keys, 0.1 texts, 0.1.1 texts")
    check(STID not in LVM and str(Cfg.LV_MARK_ID) not in STM, "Y: the two markers never match each other")
    WHY = {"pool.later": "coming-later stats never roll", "stat.levelFull": "full modifier power from item level 40 = Mithril / Onyxium"}
    ST2 = [("pool.later", "true", "false"), ("stat.levelFull", "50", "40")]

    def st_info(changes):
        return ("config.properties updated to the 0.1.1 stat defaults: " + ", ".join("%s %s -> %s (%s)" % (k, o, n, WHY[k]) for k, o, n in changes)
                + " (the old file is in config-history; Server Setup -> Changes can undo each line)")

    STINFO = st_info(ST2)
    NOCHG = "config.properties: no pool.later / stat.levelFull line still had its 0.1 default - nothing changed (0.1.1 stat defaults marker added)"
    READY = "coming-later stats never roll; full modifier power from item level 40"

    def st_upd(text, changes, anchor="# Roll coming-later stats: "):
        """the expected stat update: these value lines changed + the marker on its own line right above the anchor line"""
        nl = "\r\n" if "\r\n" in text else "\n"
        out = text
        for k, o, n in changes:
            a_ = nl + "%s=%s%s" % (k, o, nl)
            assert out.count(a_) == 1, (k, o)
            out = out.replace(a_, nl + "%s=%s%s" % (k, n, nl))
        assert out.count(nl + anchor) == 1, anchor
        return out.replace(nl + anchor, nl + STM + nl + anchor)

    # (a) defaults: rows, field initial values, loader fallback, level factor, the fresh file
    check(defs["pool.later"] == "false" and types["pool.later"] == "bool" and defs["stat.levelFull"] == "40" and types["stat.levelFull"] == "int",
          "Y(a): row defaults pool.later false, stat.levelFull 40")
    check(helps["pool.later"] == "Off (Skyy, 2026-09-30) = stats that do nothing yet never roll. On = they may roll, shown grey."
          and helps["stat.levelFull"] == "Gear this level or higher rolls at full power (40 = Mithril)." + PH, "Y(a): the two row help texts")
    mi_ = pool.get(PKG + "GearCfg").getClassInitializer().getMethodInfo()
    it_ = mi_.getCodeAttribute().iterator()
    clinit = []
    while it_.hasNext():
        clinit.append(str(IP.instructionString(it_, it_.next(), mi_.getConstPool())))
    check("iconst_0" in before_call(clinit, "GearCfg.POOL_LATER") and "bipush 40" in before_call(clinit, "GearCfg.LEVEL_FULL"),
          "Y(a): field initial values POOL_LATER false, LEVEL_FULL 40 (%s / %s)" % (before_call(clinit, "GearCfg.POOL_LATER"),
                                                                                    before_call(clinit, "GearCfg.LEVEL_FULL")))
    Cfg.POOL_LATER = True
    Cfg.LEVEL_FULL = 50
    Cfg.apply(Props(), False)
    check(not bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 40, "Y(a): loader fallback without the lines = off / 40")
    p = Props()
    p.setProperty("pool.later", "maybe")
    p.setProperty("stat.levelFull", "lots")
    Cfg.POOL_LATER = True
    Cfg.apply(p, False)
    check(not bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 40, "Y(a): an unreadable value falls back to off / 40 too")
    Cfg.apply(Props(), False)
    check(abs(float(Lvl.factor(0)) - 25.0) < 1e-9 and abs(float(Lvl.factor(20)) - 62.5) < 1e-9 and abs(float(Lvl.factor(40)) - 100.0) < 1e-9
          and abs(float(Lvl.factor(50)) - 100.0) < 1e-9, "Y(a): level factor 25 % at 0, 62.5 % at 20 (Thorium), full power from 40")
    check(int(Roll.bounds(si("dmg"), 5, 40)[1]) == int(Roll.bounds(si("dmg"), 5, 100)[1]) > int(Roll.bounds(si("dmg"), 5, 35)[1]),
          "Y(a): Mithril / Onyxium (level 40) reach the top roll, Adamantite (35) does not")
    check(("\n" + STM + "\n# Roll coming-later stats: " + helps["pool.later"] + "\npool.later=false\n") in dflt and dflt.count(STID) == 1
          and ("\n# Item level with full modifier power: " + helps["stat.levelFull"] + "\nstat.levelFull=40\n") in dflt,
          "Y(a): the default file: pool.later=false, stat.levelFull=40, the marker right above the pool.later help line")
    d, f = case("y-fresh", None)
    Cfg.load()
    fd = rb(f) if os.path.isfile(f) else b""
    check(fd == dflt.encode("utf-8") and str(Cfg.migrate011()) == "" and str(Cfg.migrateStat011()) == "" and rb(f) == fd
          and not os.path.exists(os.path.join(d, "config-history")) and not os.path.exists(os.path.join(d, "config-changes.log")),
          "Y(a): a fresh file carries both markers - neither update touches it")
    Cfg.load()
    check(not bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 40 and str(Cfg.statText()) == READY, "Y(a): the fresh file loads off / 40")

    OA = JArray(JObject)
    if live is not None:
        lt = live.decode("latin-1")
        # (b) the live file on a scratch copy, both updates in the setup order
        d, f = case("y-live", live)
        r1 = str(Cfg.migrate011())
        mid = rb(f)
        r2 = str(Cfg.migrateStat011())
        got = rb(f)
        exp_mid = upd(lt, CH6)
        exp = st_upd(exp_mid, ST2)
        check(mid == exp_mid.encode("latin-1") and got == exp.encode("latin-1"),
              "Y(b): the live file -> the level update, then exactly the two value lines (pool.later, stat.levelFull) + the stat marker, "
              "every other byte kept")
        check(r1 == INFO6 and r2.split("\n") == [STINFO], "Y(b): the INFO lines: %r / %r" % (r1, r2))
        print("Y. INFO line the live file produces: [SkyyGear] " + r2.split("\n")[0])
        b = baks(d)
        check(len(b) == 2 and rb(os.path.join(d, "config-history", b[0])) == live and rb(os.path.join(d, "config-history", b[1])) == mid,
              "Y(b): History = the 0.1 file (before the level update) + the file before the stat update")
        ix = idx(d)
        check(len(ix) == 2 and ix[1].split("\t")[1] == "Skyy_SkyyGear/config.properties"
              and ix[1].split("\t")[3:] == ["SkyyGear 0.1.1", "before the 0.1.1 stat defaults update"], "Y(b): index.log names the stat update: %s" % ix)
        cl = clog(d)
        want = [["SkyyGear 0.1.1", "-", "update", k, o, n, "ok"] for k, o, n in ST2]
        check(len(cl) == 8 and [l.split("\t")[1:] for l in cl[6:]] == want
              and all(re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$", l.split("\t")[0]) for l in cl[6:]),
              "Y(b): two more config-changes.log lines in the kit's scalar-row format (Undo-able ok lines): %s" % cl[6:])
        check(not os.path.exists(f + ".tmp"), "Y(b): no temp file left")
        Cfg.load()
        check(not bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 40 and str(Cfg.statText()) == READY, "Y(b): the loader reads off / 40")
        print("Y. ready line (live copy, after both updates): [SkyyGear] 0.1.1 ready - ... level by material (combat gear vs the class weapon skill): "
              + str(Cfg.matText()) + "; " + str(Cfg.statText()) + "; Server Setup -> Gear")
        gl_, dl_ = got.decode("latin-1").split("\n"), dflt011.split("\n")
        dif = [i_ for i_ in range(max(len(gl_), len(dl_))) if i_ >= len(gl_) or i_ >= len(dl_) or gl_[i_] != dl_[i_]]
        print("Y. the fully updated live file %s every value of a fresh 0.1.1 file; it differs in %d line(s) (comments are never rewritten): %s"
              % ("HAS" if props(got.decode("latin-1")) == props(dflt011) else "does NOT have", len(dif), [dl_[i_][:45] for i_ in dif if i_ < len(dl_)]))
        # (c) a second start
        check(str(Cfg.migrate011()) == "" and str(Cfg.migrateStat011()) == "" and rb(f) == got and len(baks(d)) == 2 and len(idx(d)) == 2
              and len(clog(d)) == 8, "Y(c): a second start changes nothing (file, History, change log)")

        # (d) CRLF
        tc = lt.replace("\n", "\r\n")
        d, f = case("y-crlf", tc.encode("latin-1"))
        Cfg.migrate011()
        midc = rb(f).decode("latin-1")
        res = str(Cfg.migrateStat011())
        gc = rb(f)
        check(gc == st_upd(midc, ST2).encode("latin-1") and gc.count(b"\n") == gc.count(b"\r\n") and gc.replace(b"\r\n", b"\n") == got
              and res == STINFO, "Y(d): a CRLF file gets the same update, every line (the marker too) still ends CRLF")

        # (e) hand-edited values: kept + noted once, or silent
        for name, edits, notes, chs, pl, lf in (
                ("on", [("\npool.later=true\n", "\npool.later=on\n")], ["pool.later=on kept (custom) - the 0.1.1 default is false"], [ST2[1]], True, 40),
                ("True", [("\npool.later=true\n", "\npool.later=True\n")], ["pool.later=True kept (custom) - the 0.1.1 default is false"], [ST2[1]], True, 40),
                ("off", [("\npool.later=true\n", "\npool.later=false\n")], [], [ST2[1]], False, 40),
                ("45", [("\nstat.levelFull=50\n", "\nstat.levelFull=45\n")], ["stat.levelFull=45 kept (custom) - the 0.1.1 default is 40"], [ST2[0]], False, 45),
                ("50.0", [("\nstat.levelFull=50\n", "\nstat.levelFull=50.0\n")], ["stat.levelFull=50.0 kept (custom) - the 0.1.1 default is 40"], [ST2[0]], False, 50),
                ("both", [("\npool.later=true\n", "\npool.later=yes\n"), ("\nstat.levelFull=50\n", "\nstat.levelFull=60\n")],
                 ["pool.later=yes kept (custom) - the 0.1.1 default is false", "stat.levelFull=60 kept (custom) - the 0.1.1 default is 40"], [], True, 60)):
            te = lt
            for a_, b_ in edits:
                te = te.replace(a_, b_)
            d, f = case("y-" + name, te.encode("latin-1"))
            Cfg.migrate011()
            mide = rb(f).decode("latin-1")
            res = str(Cfg.migrateStat011()).split("\n")
            check(te != lt and rb(f) == st_upd(mide, chs).encode("latin-1"), "Y(e) %s: the custom line kept, the other updated, every other byte kept" % name)
            check(res == [st_info(chs) if chs else NOCHG] + notes, "Y(e) %s: INFO + note: %s" % (name, res))
            check([l.split("\t")[4] for l in clog(d)[6:]] == [c[0] for c in chs], "Y(e) %s: change-log lines only for the updated key" % name)
            Cfg.load()
            check(bool(Cfg.POOL_LATER) == pl and int(Cfg.LEVEL_FULL) == lf and (("ROLL" in str(Cfg.statText())) == pl),
                  "Y(e) %s: the loader: pool.later %s, levelFull %d, the ready line says so (%s)" % (name, pl, lf, str(Cfg.statText())))
            check(str(Cfg.migrateStat011()) == "", "Y(e) %s: the note is logged once (the next start does nothing)" % name)
        # both lines missing: silent, the marker right under the level marker, the loader's fallback applies
        tm = lt.replace("\npool.later=true\n", "\n").replace("\nstat.levelFull=50\n", "\n")
        d, f = case("y-missing", tm.encode("latin-1"))
        Cfg.migrate011()
        midm = rb(f).decode("latin-1")
        res = str(Cfg.migrateStat011())
        check(tm != lt and res == NOCHG and rb(f) == midm.replace(LVM + "\n", LVM + "\n" + STM + "\n", 1).encode("latin-1") and len(clog(d)) == 6,
              "Y(e) missing: no line -> nothing changed, the marker right under the level marker")
        Cfg.load()
        check(not bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 40, "Y(e) missing: the loader's new fallback = off / 40")

        # (f) the config kit after the update: log op, Undo (set back), the next start keeps the undone values
        CfgPub = J("CfgPub")
        d, f = case("y-kit", live)
        mods = os.path.dirname(d)
        Cfg.migrate011()
        Cfg.migrateStat011()
        Cfg.load()
        CfgPub.start(Paths.get(mods), None)
        fn = bridge.get("config:fn:SkyyGear")
        lg = [str(x) for x in fn.apply(OA(["log", Integer.valueOf(20)]))]
        check(sum(1 for l in lg if l.endswith("\tupdate\tpool.later\ttrue\tfalse\tok") or l.endswith("\tupdate\tstat.levelFull\t50\t40\tok")) == 2,
              "Y(f): the kit's log op lists the two stat update lines as ok (SkyyMenu offers Undo on them)")
        g1, g2 = fn.apply(OA(["get", "pool.later"])), fn.apply(OA(["get", "stat.levelFull"]))
        check("false" in str(g1) and "40" in str(g2), "Y(f): kit memory = the updated file (%s / %s)" % (g1, g2))
        u1 = fn.apply(OA(["set", "pool.later", "true", None, "console", "yes", "console"]))
        u2 = fn.apply(OA(["set", "stat.levelFull", "50", None, "console", "yes", "console"]))
        CfgPub.flush()
        kt2 = rb(f).decode("latin-1")
        check(str(u1[0]) == "ok" and str(u2[0]) == "ok" and "\npool.later=true\n" in kt2 and "\nstat.levelFull=50\n" in kt2 and STID in kt2,
              "Y(f): Undo (set back to the old value) of both update lines works, the marker stays")
        check(str(Cfg.migrate011()) == "" and str(Cfg.migrateStat011()) == "" and rb(f).decode("latin-1") == kt2,
              "Y(f): values set back after the update survive the next start")
        Cfg.load()
        check(bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 50 and "ROLL" in str(Cfg.statText()),
              "Y(f): the loader after the undo: on / 50, the ready line says coming-later stats ROLL")
        # (g) the whole live start with History blocked: both updates WARN, nothing is written
        d, f = case("y-nohist-live", live)
        open(os.path.join(d, "config-history"), "wb").write(b"blocker")
        glf = os.path.join(XD, "y-gear-live.log")
        Log.FILE = Paths.get(glf)
        ra, rb2 = str(Cfg.migrate011()), str(Cfg.migrateStat011())
        Log.flush()
        Log.FILE = None
        gl = open(glf, encoding="utf-8").read() if os.path.isfile(glf) else ""
        check(ra == "" and rb2 == "" and rb(f) == live and not os.path.exists(os.path.join(d, "config-changes.log")),
              "Y(g): live start with History blocked -> the file stays the 0.1 file byte for byte")
        check("NOT updated to the 0.1.1 level table" in gl and "NOT updated to the 0.1.1 stat defaults" in gl, "Y(g): two WARN lines (%r)" % gl)

    # (g) History blocked on a file that only needs the stat update, then writable again; a failed write; no anchor
    ty = (H + LVM + "\nlevel.material.Iron=15\n# Roll coming-later stats: x\npool.later=true\nstat.levelFull=50\n").encode("latin-1")
    d, f = case("y-nohist", ty)
    open(os.path.join(d, "config-history"), "wb").write(b"blocker")
    glf = os.path.join(XD, "y-gear.log")
    Log.FILE = Paths.get(glf)
    res = str(Cfg.migrateStat011())
    Log.flush()
    Log.FILE = None
    gl = open(glf, encoding="utf-8").read() if os.path.isfile(glf) else ""
    check(res == "" and rb(f) == ty and not os.path.exists(os.path.join(d, "config-changes.log")) and not os.path.exists(f + ".tmp"),
          "Y(g): config-history cannot be written -> file untouched, no change-log lines")
    check("WARN config.properties NOT updated to the 0.1.1 stat defaults: the old file could not be kept in " in gl
          and "(the file is used as it is; the next start tries again)" in gl and "CONFIG 0.1.1" not in gl, "Y(g): the WARN says why + retry: %r" % gl)
    Cfg.load()
    check(bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 50, "Y(g): the untouched file is used as it is until the update can run")
    os.remove(os.path.join(d, "config-history"))
    res = str(Cfg.migrateStat011())
    b = baks(d)
    check(res == STINFO and len(b) == 1 and rb(os.path.join(d, "config-history", b[0])) == ty and len(clog(d)) == 2
          and rb(f) == st_upd(ty.decode("latin-1"), ST2).encode("latin-1"), "Y(g): the next start (History writable) updates: %r" % res)
    Cfg.load()
    check(not bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 40, "Y(g): then off / 40")
    d, f = case("y-retry", ty)
    os.makedirs(f + ".tmp")
    ok1 = str(Cfg.migrateStat011()) == "" and rb(f) == ty and len(baks(d)) == 1 and not os.path.exists(os.path.join(d, "config-changes.log"))
    os.rmdir(f + ".tmp")
    res = str(Cfg.migrateStat011())
    check(ok1 and res == STINFO and len(baks(d)) == 1 and len(idx(d)) == 1 and len(clog(d)) == 2,
          "Y(g): a failed write keeps the file; the retry updates without a second History copy: %r" % res)
    d, f = case("y-noanchor", b"a=1\nb=2\n")
    check(str(Cfg.migrateStat011()) == "" and rb(f) == b"a=1\nb=2\n" and not os.path.exists(os.path.join(d, "config-history")),
          "Y(g): no stat line and no level marker -> WARN, untouched (unreachable after migrate011)")
    res1, res2 = str(Cfg.migrate011()), str(Cfg.migrateStat011())
    check(res2 == NOCHG and rb(f) == ("a=1\nb=2\n" + LVM + "\n" + STM + "\n").encode("ascii"), "Y(g): in the setup order the marker goes under the level marker")

    # (h) the pure text step on edge cases
    def st(t):
        r_ = Cfg.stUpdate(t)
        return None if r_ is None else (str(r_[0]), str(r_[1]), [str(x) for x in r_[2]], [str(x) for x in r_[3]])

    r = st("pool.later = true\nstat.levelFull:50   \n")
    check(r[0] == STM + "\npool.later = false\nstat.levelFull:40\n" and r[3] == ["pool.later", "true", "false", "stat.levelFull", "50", "40"]
          and r[1] == "pool.later true -> false (%s), stat.levelFull 50 -> 40 (%s)" % (WHY["pool.later"], WHY["stat.levelFull"]),
          "Y(h): spacing, ':' separator, trailing spaces: value text replaced only; the marker above the first entry (%r)" % (r,))
    check(st("a=1\n# help\npool.later=true\n")[0] == "a=1\n" + STM + "\n# help\npool.later=false\n", "Y(h): a help comment right on top -> above it")
    check(st("# help\n\npool.later=true\n")[0] == "# help\n\n" + STM + "\npool.later=false\n", "Y(h): a blank line between -> right above the entry")
    check(st("a=x" + BS + "\n# no comment\npool.later=true\n")[0] == "a=x" + BS + "\n# no comment\n" + STM + "\npool.later=false\n",
          "Y(h): a continuation line that looks like a comment is not a help comment")
    r = st("pool.later=true\nx=1\npool.later=on\n")
    check(r[0] == STM + "\npool.later=true\nx=1\npool.later=on\n" and r[3] == [] and r[2] == ["pool.later=on kept (custom) - the 0.1.1 default is false"],
          "Y(h): last line wins - custom on kept, the dead true left")
    r = st("pool.later=on\npool.later=true\n")
    check(r[0] == STM + "\npool.later=on\npool.later=false\n" and r[3] == ["pool.later", "true", "false"], "Y(h): last line true -> updated")
    r = st("pool.later=tr" + BS + "\n    ue\nstat.levelFull=50\n")
    check(r[0] == STM + "\npool.later=tr" + BS + "\n    ue\nstat.levelFull=40\n" and r[3] == ["stat.levelFull", "50", "40"]
          and r[2] == ["pool.later=true kept (custom) - the 0.1.1 default is false"], "Y(h): a continued entry is never rewritten (noted)")
    r = st(LVM + "\n#pool.later=true\n! stat.levelFull=50\n")
    check(r[0] == LVM + "\n" + STM + "\n#pool.later=true\n! stat.levelFull=50\n" and r[1] == "" and r[2] == [] and r[3] == [],
          "Y(h): commented / template lines never change; no entry -> the marker right under the level marker")
    r = st("POOL.LATER=true\nstat.levelfull=50\n" + LVM + "\n")
    check(r[0] == "POOL.LATER=true\nstat.levelfull=50\n" + LVM + "\n" + STM + "\n" and r[3] == [] and r[2] == [],
          "Y(h): keys are case-sensitive like the loader (other-case lines are not the setting and stay)")
    check(st(LVM)[0] == LVM + "\n" + STM and st("a=1\r\n" + LVM)[0] == "a=1\r\n" + LVM + "\r\n" + STM
          and st(LVM + "\r\nb=2\r\n")[0] == LVM + "\r\n" + STM + "\r\nb=2\r\n", "Y(h): under the level marker: no final newline stays so, CRLF kept")
    check(st("a=1\r\npool.later=true")[0] == "a=1\r\n" + STM + "\r\npool.later=false", "Y(h): the marker takes the file's CRLF above a last line")
    check(Cfg.stUpdate("# SkyyGear 0.1.1 stat defaults, anything\npool.later=true\n") is None
          and Cfg.stUpdate("x=1\n  ! SkyyGear 0.1.1 stat defaults\n") is None, "Y(h): a comment line with the marker id = already done")
    r = st("note=SkyyGear 0.1.1 stat defaults\npool.later=true\n")
    check(r is not None and "\npool.later=false\n" in r[0], "Y(h): the marker id inside a value does not count")
    r = st("stat.levelFull=40\npool.later=false\n")
    check(r[0] == STM + "\nstat.levelFull=40\npool.later=false\n" and r[1] == "" and r[2] == [] and r[3] == [], "Y(h): already the new defaults: silent")
    try:
        Cfg.stUpdate("a=1\nb=2\n")
        thrown = False
    except Exception:
        thrown = True
    check(thrown, "Y(h): no entry and no level marker -> refused (the caller WARNs)")
    # random files (fixed seed): the level marker first, then pieces with odd / even backslashes, comments, blanks, stat lines,
    # LF / CRLF, with / without final newline: Properties values = before + the updated rows, the marker = one comment line and the only
    # line added, the next pass does nothing
    rnd2 = random.Random(20260930 + 11)
    spieces = ["a=1", "b=x" + BS, "c=y" + BS + BS, "#c" + BS, "# note", "", "   z" + BS, "d:e", "  f g" + BS, "!x" + BS, "# help",
               "pool.later=true", "pool.later=on", "pool.later = true", "stat.levelFull=50", "stat.levelFull = 45", "stat.levelFull:50"]

    def st_ok(t, out, rows):
        want_ = props(t)
        for i_ in range(0, len(rows), 3):
            want_[rows[i_]] = rows[i_ + 2]
        got_ = props(out)
        return (got_ == want_ and not any(STID in k_ or STID in v_ for k_, v_ in got_.items()) and Cfg.stUpdate(out) is None
                and out.count(STID) == 1)

    def st_bytes(t, out):
        ol, tl = out.split("\n"), t.split("\n")
        mi = [i_ for i_, x_ in enumerate(ol) if STID in x_]
        if len(mi) != 1 or ol[mi[0]].rstrip("\r") != STM:
            return False
        m_ = mi[0]
        rest = ol[:m_] + ol[m_ + 1:]
        if len(rest) != len(tl):
            return False
        for i_, (a_, b_) in enumerate(zip(rest, tl)):
            if a_ == b_ or (a_.startswith(("pool.later", "stat.levelFull")) and b_.startswith(("pool.later", "stat.levelFull"))):
                continue
            if i_ == len(tl) - 1 and m_ == len(ol) - 1 and a_ == b_ + "\r":
                continue
            return False
        return True

    bad = []
    for n_ in range(2000):
        ls_ = [LVM] + [rnd2.choice(spieces) for _q in range(rnd2.randint(0, 8))]
        nl_ = "\r\n" if rnd2.random() < 0.3 else "\n"
        t = nl_.join(ls_) + (nl_ if rnd2.random() < 0.6 else "")
        r = st(t)
        if r is None or not st_ok(t, r[0], r[3]) or not st_bytes(t, r[0]):
            bad.append(t)
    check(not bad, "Y(h): 2000 random files: same Properties values (+ updated rows), the marker = one comment line and the only line added, "
                   "the next pass does nothing (%d bad, first %r)" % (len(bad), bad[:1]))

    # (i) EVERY roll path with pool.later off (the loader default) never yields a coming-later stat
    later = set(SK[i] for i in range(int(Defs.NS)) if int(Defs.S_LIVE[i]) == 0)
    check(len(later) == 19 and {"fer", "thorns", "weak", "as", "lbonus", "xpb"} <= later, "Y(i): 19 coming-later stats: %s" % sorted(later))
    p = Props()
    p.setProperty("gear.include", "Skyy_Ring_")
    p.setProperty("kind.prefix.Skyy_Ring_", "equipment")
    Cfg.apply(p, False)
    check(not bool(Cfg.POOL_LATER), "Y(i): pool.later is off from the loader default")
    w0 = [int(v) for v in Cfg.S_W]
    wa = JArray(JInt)(len(w0))
    for i in range(len(w0)):
        wa[i] = 100000 if SK[i] in later else w0[i]
    Cfg.S_W = wa                       # one leak would dominate: every coming-later stat outweighs every live one 1000+ to 1

    def keys_of(dd):
        return [str(m.asDocument().getString("s").getValue()) for m in Data.mods(dd)]

    def doc_of(s_):
        return Data.gearDoc(s_.getMetadata())

    tally = {}

    def seen(path, dd):
        t_ = tally.setdefault(path, [0, 0, []])
        ks_ = keys_of(dd) if dd is not None else []
        t_[0] += 1
        t_[1] += len(ks_)
        t_[2] += [k_ for k_ in ks_ if k_ in later]

    IDS = ["Weapon_Sword_Iron", "Weapon_Shortbow_Crude", "Weapon_Staff_Wood", "Weapon_Spellbook_Frost", "Weapon_Daggers_Crude",
           "Armor_Mithril_Chest", "Armor_Iron_Head", "Skyy_Ring_Gold"]
    check(sorted(set(int(Data.slotOf(i)) for i in IDS)) == [0, 1, 2, 4], "Y(i): the test items cover weapon, spell weapon, armor, Equipment")
    # control: with pool.later ON the same weights make coming-later stats show up on every path shape (the detector works)
    Cfg.POOL_LATER = True
    ctl = sum(1 for _ in range(40) for k_ in keys_of(Roll.newDoc("Armor_Mithril_Chest", 5, True, "admin")) if k_ in later)
    ctl2 = sum(1 for _ in range(40) for k_ in keys_of(Roll.craftDoc("Skyy_Ring_Gold", U1)) if k_ in later)
    Cfg.POOL_LATER = False
    check(ctl > 100 and ctl2 > 0, "Y(i): control run with pool.later ON: coming-later stats roll (%d on 40 Mythic armor pieces, %d on rings)" % (ctl, ctl2))
    # 1. the roll itself: every slot, rarity, level
    for slot in (0, 1, 2, 4):
        for rr in range(7):
            for lvl in (0, 15, 40, 100):
                for _ in range(60):
                    arr = Roll.rollMods(slot, rr, lvl)
                    dd = BD()
                    dd.put("mods", arr)
                    seen("GearRoll.rollMods (every slot / rarity / level)", dd)
    # 2. /gear give (newDoc) and crafting (craftDoc = GearCraftSys on the benches)
    for iid in IDS:
        for rr in range(7):
            for _ in range(30):
                seen("/gear give (GearRoll.newDoc)", Roll.newDoc(iid, rr, True, "admin"))
        for _ in range(150):
            seen("crafting (GearRoll.craftDoc)", Roll.craftDoc(iid, U1))
    # 3. the bench per-item roll (GearCraftTask.rollIn) on a stack of spears
    for _ in range(40):
        ch_, cs_ = SIC(9), SIC(36)
        ch_.setItemStackForSlot(2, IS("Weapon_Spear_Crude", 3))
        CraftTask.rollIn(JArray(IC)([ch_, cs_]), JArray(IC)([cs_]), U1, "Weapon_Spear_Crude", IdMap(), 3, None, None)
        for x_ in [ch_.getItemStack(2)] + [cs_.getItemStack(i) for i in range(36)]:
            if x_ is not None and not x_.isEmpty():
                seen("bench craft per item (GearCraftTask.rollIn)", doc_of(x_))
    # 4. the SkyySacks /craft bridge gear:fn:roll (craft rolls + another source). setup() is not run here: the same GearFn objects it
    # puts on the bridge (gear:fn:roll = new GearFn(8), gear:fn:unid = new GearFn(9) - checked in the setup() bytecode)
    su_ = code("SkyyGearPlugin", "setup")
    fi_r = next((i_ for i_, l_ in enumerate(su_) if '"gear:fn:roll"' in l_), -1)
    fi_u = next((i_ for i_, l_ in enumerate(su_) if '"gear:fn:unid"' in l_), -1)
    check(fi_r > 0 and any("bipush 8" in l_ for l_ in su_[fi_r:fi_r + 4]) and fi_u > 0 and any("bipush 9" in l_ for l_ in su_[fi_u:fi_u + 4]),
          "Y(i): setup() registers gear:fn:roll = GearFn(8), gear:fn:unid = GearFn(9)")
    froll = J("GearFn")(8)
    for iid in IDS[:6]:
        for src in ("craft", "sacks"):
            outs = froll.apply(OA([U1, iid, Integer.valueOf(64), src]))
            check(outs is not None and len(outs) == 64, "Y(i): gear:fn:roll %s x64 for %s" % (src, iid))
            for x_ in outs:
                seen("SkyySacks /craft bridge (gear:fn:roll)", doc_of(x_))
    # 5. mob drops (GearTag.unid, gear:fn:unid) -> the Identify page (GearIdent.identify, paid) and /gear identify (GearRoll.identify)
    bridge.put("coins:fn:take", Take())
    bridge.put("coins:fn:get", Purse())
    bridge.put("coins:fn:add", Purse())
    funid = J("GearFn")(9)
    Cfg.PART_DROPS = True
    for iid in IDS:
        for _ in range(40):
            s_ = Tag.unid(IS(iid, 1), 1)
            dd = doc_of(s_)
            check(dd is not None and not bool(Data.identified(dd)) and keys_of(dd) == [], "Y(i): a mob drop is unidentified without modifiers") if _ == 0 else None
            c_, g_ = SIC(9), SIC(9)
            c_.setItemStackForSlot(0, s_)
            ri = Ident.identify(c_, 0, iid, Forge.fp(c_.getItemStack(0)), U1, "tester", False, JArray(IC)([g_]), JArray(IC)([c_, g_]))
            if int(ri[0]) != 1:
                check(False, "Y(i): Identify page refused %s: %s" % (iid, ri[1]))
                continue
            seen("mob drop -> Identify page (GearTag.unid + GearIdent.identify)", doc_of(c_.getItemStack(0)))
            s2_ = funid.apply(OA([IS(iid, 1), "mob"]))
            seen("mob drop -> /gear identify (gear:fn:unid + GearRoll.identify)", Roll.identify(iid, doc_of(s2_), U1))
    # 6. loot chests (GearTag.tagContainer) -> Identify all (GearIdent.allIn)
    for _ in range(15):
        chest = SIC(27)
        chest.setItemStackForSlot(0, IS("Weapon_Spellbook_Demon", 4))
        for j_, iid in enumerate(IDS[:4] + IDS[5:7]):
            chest.setItemStackForSlot(10 + j_, IS(iid, 1))
        Tag.tagContainer(chest, "test")
        by_ = JArray(IC)(6)
        by_[0] = chest
        rows_ = ArrayList()
        for sl in range(27):
            x_ = chest.getItemStack(sl)
            if x_ is not None and not x_.isEmpty():
                rr_ = JArray(JInt)(2)
                rr_[0] = 0
                rr_[1] = sl
                rows_.add(rr_)
        Ident.allIn(by_, rows_, U1, "tester", ArrayList())
        for sl in range(27):
            x_ = chest.getItemStack(sl)
            if x_ is not None and not x_.isEmpty():
                dd = doc_of(x_)
                if dd is not None and bool(Data.identified(dd)):
                    seen("loot chest -> Identify all (GearTag.tagContainer + GearIdent.allIn)", dd)
    # 7. reforge: the Reforge page (paid) and /gear reroll (free) on gear that HAS a coming-later stat; GearRoll.reforge itself
    def with_fer(iid):
        dd = Roll.newDoc(iid, 3, True, "admin")
        arr = JClass("org.bson.BsonArray")()
        arr.add(Data.mod("fer", 5))
        arr.add(Data.mod("dmg", 3))
        dd.put("mods", arr)
        return dd

    for iid in IDS:
        for free in (False, True):
            for _ in range(40):
                c_, g_ = SIC(9), SIC(9)
                c_.setItemStackForSlot(0, Data.put(IS(iid, 1), with_fer(iid), U1))
                rf_ = Forge.reforge(c_, 0, iid, Forge.fp(c_.getItemStack(0)), U1, "tester", free, JArray(IC)([g_]), JArray(IC)([c_, g_]))
                if int(rf_[0]) != 1:
                    check(False, "Y(i): reforge refused %s: %s" % (iid, rf_[1]))
                    continue
                seen("/gear reroll (GearForge.reforge, free)" if free else "Reforge page (GearForge.reforge, paid)", doc_of(c_.getItemStack(0)))
        for _ in range(30):
            seen("GearRoll.reforge", Roll.reforge(iid, with_fer(iid)))
    for k in ("coins:fn:take", "coins:fn:get", "coins:fn:add"):
        bridge.remove(k)
    # 8. SkyyRolls migration (GearData.migrate, the in-memory view GearData.effective, the passive stamp GearStamp.stampStack)
    BI2 = JClass("org.bson.BsonInt32")
    rng3 = random.Random(7)
    for mb in ("stats", "roll", "item"):
        Cfg.MIGRATE_BY = mb
        for _ in range(60):
            ro = BD()
            ro.append("dmg", BI2(rng3.randint(0, 30)))
            ro.append("str", BI2(rng3.randint(0, 25)))
            ro.append("crit", BI2(rng3.randint(0, 15)))
            ro.append("quality", BI2(rng3.randint(0, 100)))
            iid = rng3.choice(IDS[:7])
            seen("SkyyRolls migration (GearData.migrate)", Data.migrate(iid, ro))
            md_ = BD()
            md_.append("SkyyRolls", ro)
            seen("SkyyRolls migration (GearData.effective)", Data.effective(iid, md_))
            seen("SkyyRolls migration (GearStamp.stampStack)", doc_of(Stamp.stampStack(IS(iid, 1).withMetadata(md_), U1, None)))
    Cfg.MIGRATE_BY = "stats"
    for path_, (n_items, n_mods, leaks) in sorted(tally.items()):
        check(n_items > 0 and n_mods > 0 and not leaks, "Y(i): %s: %d items / %d modifiers, %d coming-later (%s)" % (path_, n_items, n_mods, len(leaks), sorted(set(leaks))[:5]))
    print("Y. roll paths with pool.later off: " + "; ".join("%s %d/%d" % (p_, v_[0], v_[1]) for p_, v_ in sorted(tally.items())))
    # gear that already has one keeps it until its next reforge (the lock): a split / the passive scan copy the document, no roll
    kd = with_fer("Weapon_Sword_Iron")
    ks_ = Data.put(IS("Weapon_Sword_Iron", 1), kd, U1)
    check("fer" in keys_of(doc_of(Stamp.stampStack(ks_, U1, None))) and "fer" in keys_of(Stamp.splitDoc("Weapon_Sword_Iron", ks_.getMetadata(), 0, U1)),
          "Y(i): gear that already has a coming-later stat keeps it (passive stamp, stack split)")
    check(any("(coming later)" in str(x) for x in View.plain("Weapon_Sword_Iron", kd, None)), "Y(i): ... shown '(coming later)' in its tooltip")
    check("fer" not in keys_of(Roll.reforge("Weapon_Sword_Iron", kd)), "Y(i): ... and loses it on its next reforge")
    # the bytecode: GearRoll.pool is the only way into a roll - pool <- rollMods only; GearData.mod <- rollMods + migrate only;
    # rollMods <- newDoc / reforge / identify only (every path above ends in one of these)
    callers = {}
    for cn in names:
        if not cn.startswith(PKG):
            continue
        for mm in pool.get(cn).getDeclaredMethods():
            bo_ = BOS()
            IP(PS(bo_)).print_(mm)
            tx_ = str(bo_.toString())
            for callee in ("GearRoll.pool(", "GearData.mod(", "GearRoll.rollMods(", "GearRoll.newDoc(", "GearRoll.reforge(", "GearRoll.identify(",
                           "GearRoll.craftDoc(", "GearRoll.unidDoc("):
                if ("gear." + callee) in tx_:
                    callers.setdefault(callee, set()).add(cn[len(PKG):] + "." + str(mm.getName()))
    # 0.1.2: pool(slot, id) / rollMods(id, ...) got the item id; the old signatures stay as one-line overloads (Z9 checks by signature)
    check(callers.get("GearRoll.pool(") == {"GearRoll.rollMods", "GearRoll.pool"}, "Y(i): GearRoll.pool is called by rollMods (+ its own overload) only: %s" % callers.get("GearRoll.pool("))
    check(callers.get("GearData.mod(") == {"GearRoll.rollMods", "GearData.migrate"}, "Y(i): GearData.mod (a new modifier) only in rollMods + migrate: %s" % callers.get("GearData.mod("))
    check(callers.get("GearRoll.rollMods(") == {"GearRoll.newDoc", "GearRoll.reforge", "GearRoll.identify", "GearRoll.rollMods"},
          "Y(i): rollMods is called by newDoc / reforge / identify only: %s" % callers.get("GearRoll.rollMods("))
    print("Y. roll entry points (bytecode): " + "; ".join("%s <- %s" % (k_[:-1], ", ".join(sorted(v_))) for k_, v_ in sorted(callers.items())
                                                         if k_ in ("GearRoll.newDoc(", "GearRoll.reforge(", "GearRoll.identify(", "GearRoll.craftDoc(", "GearRoll.unidDoc(")))
    Cfg.apply(Props(), False)
    Cfg.FILE = None
    Cfg.DIR = None
    print("Y. 0.1.1 stat defaults + update + roll paths done")

    # ================================================================================================================================
    # Z. 0.1.2 Charged Attack Damage (OPEN-QUESTIONS LOCKED 2026-09-30, research/Charged-Attack-Research.md + the verifier's cases)
    # ================================================================================================================================
    Chg, Hand, Charged = J("GearChg"), J("GearHand"), J("GearCharged")
    I_CHG = si("chg")
    Cfg.apply(Props(), False)
    Cfg.FILE = None
    Cfg.DIR = None
    Log.FILE = None
    # ---- Z1. the stat row, the config rows, the loader, the default file, the tooltip
    check(I_CHG == si("cd") + 1 and int(Defs.I_CHG) == I_CHG and int(Hit.I_CHG) == I_CHG, "Z1: chg sits right after cd; I_CHG constants")
    check(str(Defs.S_LABEL[I_CHG]) == "Charged Attack Damage" and str(Defs.S_SLOT[I_CHG]) == "wa" and str(Defs.S_UNIT[I_CHG]) == "%"
          and int(Defs.S_MAXDEF[I_CHG]) == 30 and int(Defs.S_WDEF[I_CHG]) == 5 and int(Defs.S_LIVE[I_CHG]) == 1 and str(Defs.S_SUF[I_CHG]) == ""
          and int(Cfg.S_MAX[I_CHG]) == 30 and int(Cfg.S_W[I_CHG]) == 5, "Z1: STATS row chg (weapons + armor, %, max 30, weight 5, live)")
    zk = [str(k) for k in Rows.KEYS]
    zcol = lambda arr: dict(zip(zk, [str(x) for x in arr]))
    zt, zd, zf, zh, zu, zmin, zmax = (zcol(Rows.TYPES), zcol(Rows.DEFS), zcol(Rows.FLAGS), zcol(Rows.HELPS), zcol(Rows.UNITS), zcol(Rows.MINS),
                                      zcol(Rows.MAXS))
    check(zt.get("charged.on") == "bool" and zd.get("charged.on") == "true" and zf.get("charged.on") == "live"
          and zh.get("charged.on") == "Charged Attack Damage boosts fully charged hits. Off = it does nothing and never rolls.",
          "Z1: row charged.on (bool, default on, live)")
    check(zt.get("charged.spellFactor") == "dec" and zd.get("charged.spellFactor") == "0.15" and zmin.get("charged.spellFactor") == "0"
          and zmax.get("charged.spellFactor") == "1" and zu.get("charged.spellFactor") == "x" and "danger" in zf.get("charged.spellFactor", "").split(",")
          and "Placeholder" not in zh.get("charged.spellFactor", "") and "(Skyy)" in zh.get("charged.spellFactor", ""),
          "Z1: row charged.spellFactor (dec 0.15, 0-1, x, danger, Skyy's number - no Placeholder claim)")
    check(zt.get("charged.log") == "bool" and zd.get("charged.log") == "false" and "adv" in zf.get("charged.log", "").split(","),
          "Z1: row charged.log (bool, off, advanced)")
    check(all(len(zh[k]) <= 100 for k in ("charged.on", "charged.spellFactor", "charged.log")), "Z1: help texts <= 100 characters")
    check(bool(Cfg.CHG_ON) and abs(float(Cfg.CHG_SPELL) - 0.15) < 1e-12 and not bool(Cfg.CHG_LOG), "Z1: built-in defaults on / 0.15 / off")
    for txt, want in ((("charged.on", "off"), ("charged.spellFactor", "2"), ("charged.log", "yes")), (False, 1.0, True)), \
                     ((("charged.spellFactor", "-1"),), (True, 0.0, False)), ((("charged.spellFactor", "abc"), ("charged.on", "maybe")), (True, 0.15, False)):
        pz = Props()
        for k_, v_ in txt:
            pz.setProperty(k_, v_)
        Cfg.apply(pz, True)
        check((bool(Cfg.CHG_ON), round(float(Cfg.CHG_SPELL), 6), bool(Cfg.CHG_LOG)) == want, "Z1: loader %s -> %s (clamps / defaults)" % (txt, want))
    Cfg.apply(Props(), False)
    zdt = str(Cfg.defaultsText())
    zdl = zdt.split("\n")
    CHM = str(Cfg.CH_MARK)
    check(CHM == "# SkyyGear 0.1.2 charged attack lines (Skyy 2026-09-30): Charged Attack Damage on weapons with a charged attack + armor, "
          "bows only the glowing full draw, spells x 0.15, never clubs" and str(Cfg.CH_WHO) == "SkyyGear 0.1.2", "Z1: the 0.1.2 marker text + name")
    check(zdl[zdl.index("stats.cd=30,10") + 1:zdl.index("stats.cd=30,10") + 3] == ["# chg = Charged Attack Damage (weapon, armor, %)", "stats.chg=30,5"]
          and zdl[zdl.index("speed.per=1") + 1] == CHM and zdl[zdl.index("speed.per=1") + 2:zdl.index("speed.per=1") + 8:2] == [
              "# Charged Attack Damage in combat: " + zh["charged.on"], "# Charged bonus on spells: " + zh["charged.spellFactor"],
              "# Log charged hits: " + zh["charged.log"]]
          and zdl[zdl.index("speed.per=1") + 3:zdl.index("speed.per=1") + 9:2] == ["charged.on=true", "charged.spellFactor=0.15", "charged.log=false"]
          and zdt.count(str(Cfg.CH_MARK_ID)) == 1 and zdt.startswith("# SkyyGear 0.1.2 - "),
          "Z1: fresh default file: stats.chg under stats.cd, the marker + the three rows under speed.per")
    check(str(View.modLine("chg", 12)) == "Charged Attack Damage: +12%" and not bool(View.dim("chg")), "Z1: tooltip line 'Charged Attack Damage: +12%'")
    Cfg.CHG_ON = False
    check(str(View.modLine("chg", 12)) == "Charged Attack Damage: +12% (off on this server)" and bool(View.dim("chg")) and not bool(View.dim("cd")),
          "Z1: charged.on off -> the line says so and is grey")
    Cfg.CHG_ON = True
    print("Z1. stat row + config rows + loader + default file + tooltip done")

    # ---- Z2. hitAmount: one separate factor after Strength / Magical Power, before the crit roll; spells x charged.spellFactor
    def tz(**kw):
        a_ = JArray(JInt)(int(Defs.NS))
        for k_, v_ in kw.items():
            a_[si(k_)] = v_
        return a_
    t0 = tz(chg=30, str=10, mp=20)
    HA = Hit.hitAmount
    check(abs(float(HA(100.0, t0, False, False, 0.9, 0.9)) - 110.0) < 1e-9 and float(HA(100.0, t0, False, 0.9, 0.9)) == float(HA(100.0, t0, False, False, 0.9, 0.9)),
          "Z2: not charged = 100 x 1.10 (Strength) - the 5-argument hitAmount is the same")
    check(abs(float(HA(100.0, t0, False, True, 0.9, 0.9)) - 143.0) < 1e-9, "Z2: charged melee / bow = 100 x 1.10 x 1.30 = 143")
    check(abs(float(HA(100.0, t0, True, True, 0.9, 0.9)) - 100.0 * 1.20 * 1.045) < 1e-9, "Z2: charged spell = 100 x 1.20 (Magical Power) x (1 + 0.15 x 30%) = 125.4")
    check(abs(float(HA(100.0, t0, True, False, 0.9, 0.9)) - 120.0) < 1e-9, "Z2: uncharged spell = 100 x 1.20")
    Cfg.CHG_SPELL = 0.5
    check(abs(float(HA(100.0, t0, True, True, 0.9, 0.9)) - 100.0 * 1.2 * 1.15) < 1e-9, "Z2: the spell share follows charged.spellFactor (0.5 -> x 1.15)")
    Cfg.CHG_SPELL = 0.15
    tc = tz(chg=30, str=10, cc=100, cd=0)
    check(abs(float(HA(100.0, tc, False, True, 0.0, 0.9)) - 286.0) < 1e-9 and abs(float(HA(100.0, tc, False, False, 0.0, 0.9)) - 220.0) < 1e-9,
          "Z2: a charged crit gets both (143 x 2 = 286; uncharged crit 220)")
    to = tz(chg=30, cc=150)
    check(abs(float(HA(100.0, to, False, True, 0.0, 0.1)) - 520.0) < 1e-9, "Z2: overcrit after the charged factor (100 x 1.3 x 2 x 2)")
    check(float(HA(100.0, tz(chg=-200), False, True, 0.9, 0.9)) == 0.0 and float(HA(100.0, tz(chg=-50), False, True, 0.9, 0.9)) == 50.0,
          "Z2: the factor is clamped at 0 (gear:extra may be negative), never below 0")
    te = tz(chg=30, tdmg=5, fFire=6, rElem=1)
    check(float(HA(100.0, te, False, True, 0.9, 0.9)) == float(HA(100.0, tz(chg=30), False, True, 0.9, 0.9)) == 130.0,
          "Z2: True Damage and element lines are not in the multiplied amount")
    ie = Hit.info(U1, te)
    check(int(ie[1]) == 5 and int(ie[5]) == 11, "Z2: ... they travel unmultiplied to GearTrueSys (info: True 5, elements 6 + 5 x 1 = 11)")
    print("Z2. hitAmount maths done")

    # ---- Z3. the calculator index built from the REAL Assets.zip. The build's own Python walk (exec'd from the build script, so it
    # is the same code the build self-check ran) resolves every weapon item from the raw JSON; the same JSON is turned into real engine
    # objects (ChargingInteraction, ReplaceInteraction, SerialInteraction, SimpleInteraction, DamageEntityInteraction + DamageCalculator
    # / Angled / Targeted, ProjectileInteraction + ProjectileConfig, LaunchProjectileInteraction, RootInteraction; one object per asset
    # id or inline JSON object = the engine's sharing) in fake Interaction / RootInteraction / ProjectileConfig / Item asset maps; then
    # the JAR walks them with the ENGINE's InteractionManager.walkChain (GearChg.ensure -> GearChgWalk). Both answers must agree per
    # calculator object for every vanilla weapon + the pack's More Crossbow Tiers crossbows.
    import zipfile as _zf
    bsrc = open(os.path.join(HERE, "build_skyygear_%s.py" % VERSION), encoding="utf-8").read()
    wz = {}
    exec(bsrc[bsrc.index("# ---- CHARGED WALKER BEGIN"):bsrc.index("# ---- CHARGED WALKER END")], wz)
    AzWalker = wz["AzWalker"]
    AZP = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    azz = _zf.ZipFile(AZP)
    mct = {}
    mctp = os.path.join(B.MODS_DIR, "More_Crossbow_Tiers.zip")
    if os.path.isfile(mctp):
        with _zf.ZipFile(mctp) as zz_:
            for n_ in zz_.namelist():
                if n_.startswith("Server/Item/Items/") and n_.endswith(".json"):
                    mct[os.path.basename(n_)[:-5]] = json.loads(zz_.read(n_).decode("utf-8-sig"))
    WK = AzWalker(azz, azz.namelist(), mct)
    VAN = sorted(i for i in WK.items if i.startswith("Weapon_") and not str(WK.items[i]).startswith("overlay:"))
    PACKI = sorted(mct)
    check(sorted([str(x) for x in Chg.TRUST]) == sorted(set(VAN) | set(PACKI)) and len(PACKI) in (0, 4),
          "Z3: the jar's trust list = every vanilla weapon id + the pack's More Crossbow Tiers ids (%d + %d)" % (len(VAN), len(PACKI)))
    ufz = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    ufz.setAccessible(True)
    UZ = ufz.get(None)
    FKC = store.getClass()          # the fake AssetStore class made at the start (only getAssetMap() is ever used)
    ASz = JClass("com.hypixel.hytale.assetstore.AssetStore")

    def fz(cls, name):
        f_ = cls.class_.getDeclaredField(name)
        f_.setAccessible(True)
        return f_

    def zstore(amap):
        st_ = UZ.allocateInstance(FKC)
        fz(ASz, "assetMap").set(st_, amap)
        return st_

    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
    Inter, RootI = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    ChargingI, SerialI, ReplaceI, SimpleI = (JClass(PI + "client.ChargingInteraction"), JClass(PI + "none.SerialInteraction"),
                                             JClass(PI + "none.ReplaceInteraction"), JClass(PI + "SimpleInteraction"))
    DEIz, TGTz, ANGz = (JClass(PI + "server.DamageEntityInteraction"), JClass(PI + "server.DamageEntityInteraction$TargetedDamage"),
                        JClass(PI + "server.DamageEntityInteraction$AngledDamage"))
    DCALCz, DCLSz = JClass(PI + "server.combat.DamageCalculator"), JClass(PI + "server.combat.DamageClass")
    LPIz = JClass(PI + "server.LaunchProjectileInteraction")
    PJIz = JClass("com.hypixel.hytale.server.core.modules.projectile.interaction.ProjectileInteraction")
    PJCz = JClass("com.hypixel.hytale.server.core.modules.projectile.config.ProjectileConfig")
    ItemZ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    F2O = JClass("it.unimi.dsi.fastutil.floats.Float2ObjectOpenHashMap")
    O2I = JClass("it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap")
    SLk = JClass("java.util.concurrent.locks.StampedLock")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    DAMz = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    JAWM = JClass("com.hypixel.hytale.assetstore.map.JsonAssetWithMap")
    F_ID = fz(Inter, "id")
    HM = JClass("java.util.HashMap")

    def zalloc(cls, iid=None):
        o_ = UZ.allocateInstance(cls.class_)
        if iid is not None:
            F_ID.set(o_, iid)
        return o_

    def item_ms(iid):
        seen_, cur_ = 0, iid
        while cur_ in WK.items and seen_ < 16:
            d_ = WK.js(WK.items[cur_]) or {}
            if "MaxStack" in d_:
                return int(d_["MaxStack"])
            cur_, seen_ = d_.get("Parent"), seen_ + 1
        return 1

    class Model(object):
        """real engine objects from the JSON, one per interaction key (asset id / inline object identity) like the engine"""
        def __init__(s):
            s.inter, s.roots, s.cfgs, s.bykey, s.rootkey, s.calc, s.n, s.missing = {}, {}, {}, {}, {}, {}, 0, []

        def gen(s, p_):
            s.n += 1
            return "*%s%d" % (p_, s.n)

        def root(s, refs, key=None):
            if key is not None and key in s.rootkey:
                return s.rootkey[key]
            rid = s.gen("root")
            if key is not None:
                s.rootkey[key] = rid
            ids_ = [i_ for i_ in (s.ref(r_) for r_ in refs) if i_]
            s.roots[rid] = RootI(rid, JArray(JString)(ids_))
            return rid

        def serial(s, refs):
            ids_ = [i_ for i_ in (s.ref(r_) for r_ in refs) if i_]
            if not ids_:
                return None
            if len(ids_) == 1:
                return ids_[0]
            sid = s.gen("ser")
            o_ = zalloc(SerialI, sid)
            fz(SerialI, "interactions").set(o_, JArray(JString)(ids_))
            s.inter[sid] = o_
            return sid

        def mkcalc(s, c_, key):
            if not isinstance(c_, dict):
                return None
            o_ = UZ.allocateInstance(DCALCz.class_)
            fz(DCALCz, "damageClass").set(o_, {"Charged": DCLSz.CHARGED, "Signature": DCLSz.SIGNATURE, "Light": DCLSz.LIGHT}.get(
                c_.get("Class", "Unknown"), DCLSz.UNKNOWN))
            s.calc[key] = o_
            return o_

        def simple(s, o_, nx, fl):
            fz(SimpleI, "next").set(o_, s.serial(nx))
            fz(SimpleI, "failed").set(o_, s.serial(fl))

        def ref(s, r_):
            iid, d_, key = WK.interaction(r_)
            if d_ is None:
                s.missing.append(r_ if isinstance(r_, str) else "<inline>")
                return None
            if key in s.bykey:
                return s.bykey[key]
            my = iid if iid is not None else s.gen("inl")
            s.bykey[key] = my
            o = WK.norm(d_)
            if o["charge"] is not None:
                ob = zalloc(ChargingI, my)
                m_ = F2O()
                for k_, rs in o["charge"]:
                    cid = s.serial(rs)
                    if cid:
                        m_.put(JFloat(k_), JString(cid))
                fz(ChargingI, "next").set(ob, m_)
                fz(ChargingI, "failed").set(ob, s.serial(o["failed"]))
            elif o["replace"] is not None:
                ob = zalloc(ReplaceI, my)
                var, dflt_ = o["replace"]
                fz(ReplaceI, "variable").set(ob, var)
                fz(ReplaceI, "defaultValue").set(ob, s.root(dflt_, ("replace", key)) if dflt_ else None)
            elif o["dmg"] is not None:
                ob = zalloc(DEIz, my)
                calc, ang, tgt = o["dmg"]
                fz(DEIz, "damageCalculator").set(ob, s.mkcalc(calc, key + (None,)))
                arr = JArray(ANGz)(len(ang))
                for i_, c_ in enumerate(ang):
                    a_ = UZ.allocateInstance(ANGz.class_)
                    fz(TGTz, "damageCalculator").set(a_, s.mkcalc(c_, key + ("a%d" % i_,)))
                    arr[i_] = a_
                fz(DEIz, "angledDamage").set(ob, arr)
                tm = HM()
                for k_, c_ in tgt.items():
                    t_ = UZ.allocateInstance(TGTz.class_)
                    fz(TGTz, "damageCalculator").set(t_, s.mkcalc(c_, key + ("t:" + k_,)))
                    tm.put(k_, t_)
                fz(DEIz, "targetedDamage").set(ob, tm)
                fz(DEIz, "next").set(ob, s.serial(o["next"]))
                fz(DEIz, "failed").set(ob, s.serial(o["failed"]))
            elif o["proj"] is not None:
                ob = zalloc(PJIz, my)
                cfg = o["proj"]
                cid = cfg if isinstance(cfg, str) else s.gen("cfg")
                if cid not in s.cfgs:
                    pc = UZ.allocateInstance(PJCz.class_)
                    fz(PJCz, "id").set(pc, cid)
                    s.cfgs[cid] = pc
                    im = HM()
                    im.put(ITY.ProjectileHit, s.root(WK.pcfg_hit(cfg), ("cfg", cid)))
                    fz(PJCz, "interactions").set(pc, im)
                fz(PJIz, "config").set(ob, cid)
                s.simple(ob, o["next"], o["failed"])
            elif o["launch"] is not None:
                ob = zalloc(LPIz, my)
                fz(LPIz, "projectileId").set(ob, o["launch"])
                s.simple(ob, o["next"], o["failed"])
            else:
                ob = zalloc(SimpleI, my)
                s.simple(ob, o["next"], o["failed"])
            s.inter[my] = ob
            return my

        def item(s, iid, as_id=None):
            it = WK.item(iid)
            ob = UZ.allocateInstance(ItemZ.class_)
            fz(ItemZ, "id").set(ob, as_id or iid)
            fz(ItemZ, "maxStack").setInt(ob, item_ms(iid))
            im = HM()
            for t_, rr in (it.get("Interactions") or {}).items():
                try:
                    ty = ITY.valueOf(t_)
                except Exception:
                    continue
                im.put(ty, s.root(WK.root_ids(rr), ("iroot", rr) if isinstance(rr, str) else ("iroot", id(rr))))
            vm = HM()
            for var, v_ in (it.get("InteractionVars") or {}).items():
                vm.put(var, s.root(WK.root_ids(v_), ("var", v_) if isinstance(v_, str) else ("var", id(v_))))
            fz(ItemZ, "interactions").set(ob, im)
            fz(ItemZ, "interactionVars").set(ob, vm)
            return ob

    def indexed(entries):
        m_ = UZ.allocateInstance(ILT.class_)
        fz(DAMz, "assetMapLock").set(m_, SLk())
        am_ = HM()
        fz(DAMz, "assetMap").set(m_, am_)
        fz(ILT, "keyToIndexLock").set(m_, SLk())
        kti = O2I()
        kti.defaultReturnValue(-2147483648)
        arr = JArray(JAWM)(len(entries))
        for i_, (k_, v_) in enumerate(entries.items()):
            arr[i_] = v_
            kti.put(JString(k_), JInt(i_))
            am_.put(k_, v_)
        fz(ILT, "keyToIndex").set(m_, kti)
        fz(ILT, "array").set(m_, arr)
        return m_

    MZ = Model()
    ALLW = sorted(set(VAN) | set(PACKI))
    zitems = dict((i, MZ.item(i)) for i in ALLW)
    # two fake third-party items for the verifier's "loose Class tag" case (never vanilla / pack = untrusted): the vanilla crossbow's
    # chains under a modded id, and a sword whose normal swing a mod tagged Class Charged
    zitems["Weapon_Crossbow_Modded"] = MZ.item("Weapon_Crossbow_Iron", "Weapon_Crossbow_Modded")
    loose_calc = UZ.allocateInstance(DCALCz.class_)
    fz(DCALCz, "damageClass").set(loose_calc, DCLSz.CHARGED)
    ld = zalloc(DEIz, "*loose_dmg")
    fz(DEIz, "damageCalculator").set(ld, loose_calc)
    fz(DEIz, "angledDamage").set(ld, JArray(ANGz)(0))
    fz(DEIz, "targetedDamage").set(ld, HM())
    MZ.inter["*loose_dmg"] = ld
    MZ.roots["*loose_root"] = RootI("*loose_root", JArray(JString)(["*loose_dmg"]))
    lit = UZ.allocateInstance(ItemZ.class_)
    fz(ItemZ, "id").set(lit, "Weapon_Sword_LooseTag")
    fz(ItemZ, "maxStack").setInt(lit, 1)
    lim = HM()
    lim.put(ITY.Primary, "*loose_root")
    fz(ItemZ, "interactions").set(lit, lim)
    fz(ItemZ, "interactionVars").set(lit, HM())
    zitems["Weapon_Sword_LooseTag"] = lit
    check(not MZ.missing, "Z3: every interaction / root the weapons reference resolves (%s)" % MZ.missing[:5])
    old_inter_store = fz(Inter, "ASSET_STORE").get(None)
    fz(Inter, "ASSET_STORE").set(None, zstore(indexed(MZ.inter)))
    fz(RootI, "ASSET_STORE").set(None, zstore(indexed(MZ.roots)))
    dcf = DAMz()
    for k_, v_ in MZ.cfgs.items():
        fz(DAMz, "assetMap").get(dcf).put(k_, v_)
    fz(PJCz, "ASSET_STORE").set(None, zstore(dcf))
    imap = fz(DAMz, "assetMap").get(store.getAssetMap())
    for k_, v_ in zitems.items():
        imap.put(k_, v_)
    print("Z3. engine model from Assets.zip: %d interactions, %d roots, %d projectile configs, %d items" % (len(MZ.inter), len(MZ.roots),
                                                                                                         len(MZ.cfgs), len(zitems)))
    Chg.clear()
    zsum, zbad = {}, []
    for i in ALLW:
        e = Chg.ensure(i)
        py = WK.summary(i, True)
        zsum[i] = (e, py)
        jc = e[0]
        if not bool(e[7]) or not bool(e[5]):
            zbad.append("%s: walk not ok (%s)" % (i, str(e[4])))
            continue
        for k_, pe in py["calcs"].items():
            jo = MZ.calc.get(k_)
            jf = jc.get(jo) if jo is not None else None
            if jf is None or int(jf[0]) != pe[0] or int(jf[1]) != {"Unknown": 0, "Light": 1, "Charged": 2, "Signature": 3}[pe[1]]:
                zbad.append("%s: calc %s py %s java %s" % (i, k_[-1], pe[:2], None if jf is None else [int(x) for x in jf]))
        if jc.size() != len(py["calcs"]):
            zbad.append("%s: %d java calculators vs %d python" % (i, jc.size(), len(py["calcs"])))
        jl = dict((str(k_), int(e[1].get(k_)[0])) for k_ in e[1].keySet())
        if jl != dict((p_, v_[0]) for p_, v_ in py["launches"].items()):
            zbad.append("%s: launches java %s python %s" % (i, jl, py["launches"]))
        if bool(e[2]) != py["has"] or bool(e[3]) != py["partial"]:
            zbad.append("%s: has/partial java %s/%s python %s/%s" % (i, bool(e[2]), bool(e[3]), py["has"], py["partial"]))
    check(not zbad, "Z3: the jar's engine walk == the build's Python walk for all %d weapons (per calculator flags + class, launches, has, "
                    "partial): %d differences %s" % (len(ALLW), len(zbad), zbad[:6]))
    check(sorted(i for i in ALLW if bool(Chg.hasCharged(i)) and bool(Data.isGear(i))) == sorted(str(x) for x in Chg.FALLBACK),
          "Z3: the runtime eligibility (walk) == the list the build baked (GearChg.FALLBACK, %d items)" % len(Chg.FALLBACK))

    # ---- Z4. the per-hit rule on the real calculators (signal A / B / C, the glow step, the verifier's loose-tag case, exclusions)
    def zcalcs(i, want_flags, cls=None, sub="any"):
        e_, py_ = zsum[i]
        out_ = []
        for k_, pe in py_["calcs"].items():
            if pe[0] == want_flags and (cls is None or pe[1] == cls) and (sub == "any" or pe[2] == sub):
                out_.append((MZ.calc[k_], pe))
        return out_

    WHY = JArray(JString)(1)
    SysId = JClass("java.lang.System").identityHashCode

    def same(a_, b_):
        return a_ is not None and b_ is not None and int(SysId(a_)) == int(SysId(b_))

    def jc(calc, wid, seq=True, shot=False, pid=None, proj=False, alts=None):
        """proj = a projectile hit judged against a launch record; alts = None for the projectile's own record (find), else the item
        ids of the shooter's live records (a record GearShotTrack.pick chose)"""
        al = None if alts is None else JArray(JString)(list(alts))
        r_ = int(Chg.judgeCalc(calc, seq, wid, proj, al, shot, pid, WHY))
        return r_, str(WHY[0])

    FULL_, PART_, NORM_ = 1, 2, 4
    bfull = zcalcs("Weapon_Shortbow_Iron", FULL_)
    bpart = zcalcs("Weapon_Shortbow_Iron", PART_)
    check(sorted((pe[1], pe[2] or "") for c_, pe in bfull) == [("Charged", ""), ("Unknown", "targeted:Head")] and len(bpart) == 4
          and all(pe[1] == "Charged" for c_, pe in bpart), "Z4: Iron shortbow: FULL = the glow draw + its headshot, 4 PARTIAL draws (all tagged Charged)")
    # the glow step IS the 1.2 s draw strength 4: the FULL calculator is the Iron bow's own Primary_Shoot_Damage_Strength_4 override
    ivars = WK.item("Weapon_Shortbow_Iron")["InteractionVars"]
    s4 = ivars["Primary_Shoot_Damage_Strength_4"]["Interactions"][0]
    s4key = WK.interaction(s4)[2]
    check(MZ.calc.get(s4key + (None,)) is not None and any(same(c_, MZ.calc.get(s4key + (None,))) for c_, pe in bfull)
          and any(same(c_, MZ.calc.get(s4key + ("t:Head",))) for c_, pe in bfull), "Z4: ... that FULL step is the Iron bow's Strength_4 damage (+ Head)")
    # an arrow hit is a projectile hit judged against the bow's launch record (picked: alts = the live record ids) - also as a melee call
    for kw_ in ({}, {"proj": True, "alts": ["Weapon_Shortbow_Iron"]}, {"proj": True}):
        for c_, pe in bfull:
            r_, w_ = jc(c_, "Weapon_Shortbow_Iron", **kw_)
            check(r_ == 1 and w_.startswith("full charge 1.2 s"), "Z4: glow draw %s counts %s: %s" % (pe[2] or "body", kw_, w_))
        for c_, pe in bpart:
            r_, w_ = jc(c_, "Weapon_Shortbow_Iron", **kw_)
            check(r_ == 0 and w_.startswith("partial charge (") and "only the full charge counts" in w_, "Z4: partial draw never counts %s: %s" % (kw_, w_))
    sig = zcalcs("Weapon_Shortbow_Iron", 7, "Signature")
    check(len(sig) == 1 and jc(sig[0][0], "Weapon_Shortbow_Iron") == (0, "signature ability (Hytale Class Signature)"),
          "Z4: the shortbow volley (Signature, charged 1.5 s) never counts")
    sw = zcalcs("Weapon_Sword_Iron", FULL_)
    check(len(sw) == 1 and jc(sw[0][0], "Weapon_Sword_Iron") == (1, "full charge 0.65 s (Hytale Charged tag)"), "Z4: sword thrust 0.65 s counts")
    swl = zcalcs("Weapon_Sword_Iron", NORM_, "Light")
    check(len(swl) == 3 and all(jc(c_, "Weapon_Sword_Iron") == (0, "normal attack") for c_, pe in swl), "Z4: sword swings (Light) never count")
    sws = [c_ for c_, pe in zcalcs("Weapon_Sword_Iron", NORM_ | 8, "Signature")]
    check(len(sws) == 2 and all(jc(c_, "Weapon_Sword_Iron")[0] == 0 for c_ in sws), "Z4: sword signature (Ability1) never counts")
    ax = zcalcs("Weapon_Axe_Iron", FULL_)
    check(len(ax) == 1 and jc(ax[0][0], "Weapon_Axe_Iron") == (1, "full charge 1.39 s (untagged step, from the walk)"),
          "Z4: axe 1.39 s charged swing counts (untagged: signal B only)")
    check(all(jc(c_, "Weapon_Axe_Iron") == (0, "normal attack") for c_, pe in zcalcs("Weapon_Axe_Iron", NORM_)), "Z4: axe normal swings do not")
    ls = zcalcs("Weapon_Longsword_Iron", FULL_)
    check(len(ls) == 1 and jc(ls[0][0], "Weapon_Longsword_Iron")[1] == "full charge 1.565 s (untagged step, from the walk)", "Z4: longsword 1.565 s")
    dg = zcalcs("Weapon_Daggers_Iron", FULL_)
    check(sorted(pe[2] or "" for c_, pe in dg) == ["", "angled0"] and all(jc(c_, "Weapon_Daggers_Iron")[0] == 1 for c_, pe in dg),
          "Z4: dagger pounce + its backstab (untagged AngledDamage) count")
    mc = zcalcs("Weapon_Mace_Iron", FULL_)
    check(len(mc) == 3 and all(jc(c_, "Weapon_Mace_Iron")[1] == "full charge 2 s (Hytale Charged tag)" for c_, pe in mc), "Z4: mace 2.0 s charged swings")
    scy = zcalcs("Weapon_Battleaxe_Scythe_Void", FULL_)
    check(len(scy) == 1 and jc(scy[0][0], "Weapon_Battleaxe_Scythe_Void")[1] == "full charge 1.67 s (untagged step, from the walk)", "Z4: Void scythe")
    xb = zcalcs("Weapon_Crossbow_Iron", NORM_, "Charged")
    check(len(xb) == 1 and jc(xb[0][0], "Weapon_Crossbow_Iron") == (1, "Hytale Charged tag on a hit without a hold (crossbow 3rd bolt in a row)")
          and jc(xb[0][0], "Weapon_Crossbow_Iron", proj=True, alts=["Weapon_Crossbow_Iron"]) == (1, "Hytale Charged tag on a hit without a hold (crossbow 3rd bolt in a row)"),
          "Z4: crossbow 3rd bolt (Hytale's Charged combo, no hold) counts (signal A, trusted vanilla), also as the projectile hit it is")
    if PACKI:
        xbm = zcalcs("Weapon_Crossbow_Cobalt", NORM_, "Charged")
        check(len(xbm) == 1 and jc(xbm[0][0], "Weapon_Crossbow_Cobalt")[0] == 1 and bool(Chg.hasCharged("Weapon_Crossbow_Cobalt")),
              "Z4: More Crossbow Tiers Cobalt crossbow: its inherited combo counts + it may roll (pack item = trusted)")
    # verifier: signal A trusts loose Class tags from other mods -> only vanilla + pack ids; an untrusted item needs B or C
    xmod = Chg.ensure("Weapon_Crossbow_Modded")
    xmc = [c_ for c_ in xmod[0].keySet() if int(xmod[0].get(c_)[1]) == 2 and int(xmod[0].get(c_)[0]) == NORM_]
    check(len(xmc) == 1 and same(xmc[0], xb[0][0]) and jc(xmc[0], "Weapon_Crossbow_Modded") == (0, "Charged tag on an untrusted item (not vanilla or pack) - ignored")
          and not bool(Chg.hasCharged("Weapon_Crossbow_Modded")), "Z4: the same combo bolt on an untrusted (modded) id never counts and never rolls")
    check(jc(loose_calc, "Weapon_Sword_LooseTag") == (0, "Charged tag on an untrusted item (not vanilla or pack) - ignored")
          and not bool(Chg.hasCharged("Weapon_Sword_LooseTag")) and "Hytale Charged-tagged combo hit" in str(Chg.summary("Weapon_Sword_LooseTag")),
          "Z4: a mod's normal swing tagged Class Charged: ignored, the stat never rolls on that weapon")
    # not in the item's walk (another item's calculator / a new asset object): Class tag only for trusted ids without partial levels
    nc = UZ.allocateInstance(DCALCz.class_)
    fz(DCALCz, "damageClass").set(nc, DCLSz.CHARGED)
    check(jc(nc, "Weapon_Sword_Iron") == (1, "Hytale Charged tag (the step is not in the walk)"), "Z4: unknown Charged calc, trusted sword -> counts")
    check(jc(nc, "Weapon_Shortbow_Iron") == (0, "Charged tag on an item with partial charge levels, step not in the walk - ignored"),
          "Z4: ... on a bow (partial draws) it does not (a partial draw can never slip through)")
    check(jc(nc, "Weapon_Sword_LooseTag")[0] == 0, "Z4: ... nor on an untrusted item")
    fz(DCALCz, "damageClass").set(nc, DCLSz.UNKNOWN)
    check(jc(nc, "Weapon_Sword_Iron") == (0, "normal attack (the step is not in the walk)"), "Z4: an unknown untagged calc never counts")
    # exclusions (Skyy: clubs, Kunai, Crystal Flame; verifier: Crystal Ice)
    fl = zcalcs("Weapon_Club_Steel_Flail_Rusty", FULL_)
    ci = zcalcs("Weapon_Staff_Crystal_Ice", FULL_)
    check(len(fl) == 1 and jc(fl[0][0], "Weapon_Club_Steel_Flail_Rusty") == (0, "excluded family (clubs, Kunai, Crystal Flame / Crystal Ice staff, Vampire bow)")
          and len(ci) == 1 and jc(ci[0][0], "Weapon_Staff_Crystal_Ice")[0] == 0, "Z4: flail club charged spin + Crystal Ice charged ball never count")
    amb = zcalcs("Weapon_Shortbow_Bomb", FULL_ | PART_)
    check(len(amb) == 1 and jc(amb[0][0], "Weapon_Shortbow_Bomb") == (0, "ambiguous: this damage step is reached charged and uncharged")
          and not bool(Chg.hasCharged("Weapon_Shortbow_Bomb")), "Z4: prototype bow: one damage step for every draw = ambiguous, never counts / rolls")
    # signal C: legacy projectiles (spear throw, spell orbs)
    check(int(Chg.launchCode("Weapon_Spear_Iron", "Spear_Iron")) == 1 and int(Chg.launchCode("Weapon_Spear_Iron", "Spear_Copper")) == -1
          and int(Chg.launchCode("Weapon_Staff_Iron", "Skeleton_Mage_Corruption_Orb")) == 1
          and int(Chg.launchCode("Weapon_Spellbook_Fire", "Skeleton_Mage_Corruption_Orb")) == 1
          and int(Chg.launchCode("Weapon_Wand_Wood", "Skeleton_Mage_Corruption_Orb")) == 1
          and int(Chg.launchCode("Weapon_Staff_Frost", "Ice_Ball")) == 1 and int(Chg.launchCode("Weapon_Staff_Crystal_Red", "Fireball")) == 1
          and int(Chg.launchCode("Weapon_Shortbow_Vampire", "Arrow_FullCharge")) == 1 and int(Chg.launchCode("Weapon_Shortbow_Vampire", "Arrow_HalfCharge")) == 0,
          "Z4: launch codes: spear throw / staff / spellbook / wand orbs / Frost Ice_Ball / Crystal Red Fireball charged; Vampire full vs half draw")
    # a legacy projectile hit carries its own record (GearShotTrack.find): proj, alts None
    check(jc(None, "Weapon_Spear_Iron", False, True, "Spear_Iron", proj=True) == (1, "charged launch (Spear_Iron)")
          and jc(None, "Weapon_Spear_Iron", False, False, "Spear_Iron", proj=True) == (0, "launch not charged (Spear_Iron)")
          and jc(None, "Weapon_Sword_Iron", False, False, None) == (0, "no damage step and no charged launch"), "Z4: signal C (no DamageSequence)")
    # the Vampire bow (review of 0.1.2 finding 2): its 1.0 s arrow never glows -> excluded, never counts (its launch code stays 1 = the
    # walk itself is unchanged), never rolls
    check(jc(None, "Weapon_Shortbow_Vampire", False, True, "Arrow_FullCharge", proj=True) == (0, "excluded family (clubs, Kunai, Crystal Flame / Crystal Ice staff, Vampire bow)")
          and not bool(Chg.hasCharged("Weapon_Shortbow_Vampire")) and not bool(Chg.canRoll("Weapon_Shortbow_Vampire", 0))
          and "the Vampire bow's arrow never glows" in str(Chg.summary("Weapon_Shortbow_Vampire"))
          and "Weapon_Shortbow_Vampire" in [str(x) for x in Chg.EXCL] and "Weapon_Shortbow_Vampire" not in [str(x) for x in Chg.FALLBACK],
          "Z4: Vampire bow (no glow): its full-charge arrow never counts, it never rolls, the probe says why")

    # ---- Z4b. review of 0.1.2 finding 1: a picked record (GearShotTrack.pick = the WEAKER weapon when several are in the air) may be
    # another weapon than the arrow's. The reviewer's case: a spear / sword record picked for a bow arrow - the old melee fallback
    # ("Class Charged, step not in the walk") counted a PARTIAL draw (judgeCalc(Charged calc, spear) = 1). Now:
    SP_, SW_, BW_, XB_ = "Weapon_Spear_Iron", "Weapon_Sword_Iron", "Weapon_Shortbow_Iron", "Weapon_Crossbow_Iron"
    for wid_ in (SP_, SW_):
        for c_, pe in bpart:
            check(jc(c_, wid_, proj=True, alts=[wid_]) == (0, "projectile step not in the walk of its shot's weapon - not charged"),
                  "Z4b: a partial draw judged against a picked %s record (only it in the air) never counts" % wid_)
            check(jc(c_, wid_, proj=True) == (0, "projectile step not in the walk of its shot's weapon - not charged"),
                  "Z4b: ... nor against an exact %s record" % wid_)
            r_, w_ = jc(c_, wid_, proj=True, alts=[wid_, BW_])
            check(r_ == 0 and w_.startswith("partial charge (") and w_.endswith(" - only the full charge counts - fired by " + BW_),
                  "Z4b: a partial draw with a %s shot + the bow's shots in the air: found in the bow's walk = partial (%s)" % (wid_, w_))
        for c_, pe in bfull:
            check(jc(c_, wid_, proj=True, alts=[BW_, wid_]) == (1, "full charge 1.2 s (Hytale Charged tag) - fired by " + BW_)
                  if pe[1] == "Charged" else jc(c_, wid_, proj=True, alts=[BW_, wid_])[0] == 1,
                  "Z4b: the glow draw %s with a %s shot in the air still counts (found in the bow's walk)" % (pe[2] or "body", wid_))
    check(jc(xb[0][0], SP_, proj=True, alts=[SP_, XB_]) == (1, "Hytale Charged tag on a hit without a hold (crossbow 3rd bolt in a row) - fired by " + XB_)
          and jc(xb[0][0], SP_, proj=True, alts=[SP_])[0] == 0,
          "Z4b: the crossbow's 3rd bolt with a spear in the air counts via the crossbow's walk; judged against the spear alone never")
    # the melee fallback is unchanged (a melee hit has no record): an unknown Charged calc on a trusted sword still counts
    ncm = UZ.allocateInstance(DCALCz.class_)
    fz(DCALCz, "damageClass").set(ncm, DCLSz.CHARGED)
    check(jc(ncm, SW_) == (1, "Hytale Charged tag (the step is not in the walk)") and jc(ncm, SW_, proj=True, alts=[SW_, SP_])[0] == 0
          and jc(ncm, XB_, proj=True) == (0, "projectile step not in the walk of its shot's weapon - not charged"),
          "Z4b: the Class-tag fallback is melee only; an unknown projectile step never counts")
    # several live weapons that know the same step must all call it charged (fake index entries: a weapon whose walk has the glow
    # calculator as a partial step, and an excluded weapon whose walk has it)
    OBJ = JClass("java.lang.Object")

    def fake_entry(calc, flags, ms):
        m_ = IdMap()
        m_.put(calc, JArray(JInt)([flags, 2, ms]))
        e_ = JArray(OBJ)(8)
        BT_ = JClass("java.lang.Boolean").TRUE
        for i_, v_ in enumerate([m_, HashMap(), BT_, BT_, JString("fake"), BT_, JClass("java.lang.Long").valueOf(JLong(int(time.time() * 1000))), BT_]):
            e_[i_] = v_
        return e_
    gc_ = [c_ for c_, pe in bfull if pe[1] == "Charged"][0]
    Chg.ITEMS.put("Weapon_Shortbow_FakePartial", fake_entry(gc_, PART_, 900))
    Chg.ITEMS.put("Weapon_Club_FakeShooter", fake_entry(gc_, FULL_, 1200))
    check(jc(gc_, BW_, proj=True, alts=[BW_, "Weapon_Shortbow_FakePartial"]) == (0, "partial charge (0.9 s) - only the full charge counts - fired by Weapon_Shortbow_FakePartial")
          and jc(gc_, BW_, proj=True, alts=[BW_, "Weapon_Club_FakeShooter"]) == (0, "fired by Weapon_Club_FakeShooter - excluded family")
          and jc(gc_, BW_, proj=True, alts=[BW_, "Weapon_Shortbow_Crude"])[0] == 1,
          "Z4b: a step one live weapon calls partial (or an excluded weapon knows) never counts; unknown to the others = the bow decides")
    Chg.ITEMS.remove("Weapon_Shortbow_FakePartial")
    Chg.ITEMS.remove("Weapon_Club_FakeShooter")
    # a legacy launch flag without a damage step: only while one weapon is in the air
    check(jc(None, SP_, False, True, "Spear_Iron", proj=True, alts=[SP_]) == (1, "charged launch (Spear_Iron)")
          and jc(None, SP_, False, True, "Spear_Iron", proj=True, alts=[SP_, BW_]) == (0, "charged launch (Spear_Iron) but shots of several weapons are in the air and the hit has no damage step - not charged"),
          "Z4b: a picked charged launch record counts only when it is the only weapon in the air")
    # finding 3: one WARN per weapon id when a Class-tagged step of a walked vanilla weapon is missing after the re-walk
    for k_ in [str(x) for x in Gear.ONCE.keySet()]:
        if k_.startswith("chgmiss:"):
            Gear.ONCE.remove(k_)
    jc(ncm, SW_)
    jc(ncm, SW_)
    jc(ncm, XB_, proj=True)
    jc(ncm, "Weapon_Sword_LooseTag")
    fz(DCALCz, "damageClass").set(ncm, DCLSz.UNKNOWN)
    jc(ncm, "Weapon_Axe_Iron")
    for c_, pe in bfull:
        jc(c_, BW_, proj=True, alts=[BW_])
    jc(bpart[0][0], SP_, proj=True, alts=[SP_, BW_])
    miss_ = sorted(str(x) for x in Gear.ONCE.keySet() if str(x).startswith("chgmiss:"))
    check(miss_ == ["chgmiss:" + XB_, "chgmiss:" + SW_],
          "Z4b: finding 3 - a missing Class-tagged step logs once per weapon id (never for untrusted ids, untagged steps, known steps, a step "
          "another live weapon knows): %s" % miss_)
    print("Z4b. review of 0.1.2: picked records, the melee-only fallback, the missing-step WARN done")
    check(jc(bfull[0][0], None) == (0, "no weapon"), "Z4: no weapon -> no")
    Cfg.CHG_ON = False
    check(jc(bfull[0][0], "Weapon_Shortbow_Iron") == (0, "charged.on is off") and jc(None, "Weapon_Spear_Iron", False, True, "Spear_Iron")[0] == 0,
          "Z4: charged.on off -> nothing counts")
    Cfg.CHG_ON = True
    # GearCharged.judge end to end on a real Damage with the engine's DamageSequence meta (when a bare JVM can build one)
    try:
        Dmg = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
        DSq = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCalculatorSystems$DamageSequence")
        DCS_ = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCalculatorSystems")
        dz = Dmg(None, 0, 10.0)
        sq = UZ.allocateInstance(DSq.class_)
        fz(DSq, "damageCalculator").set(sq, sw[0][0])
        dz.putMetaObject(DCS_.DAMAGE_SEQUENCE, sq)
        w2 = JArray(JString)(1)
        r_a = bool(Charged.judge(dz, "Weapon_Sword_Iron", None, None, w2))
        wa_ = str(w2[0])
        dz2 = Dmg(None, 0, 10.0)
        r_b = bool(Charged.judge(dz2, "Weapon_Sword_Iron", None, None, w2))
        check(r_a and wa_ == "full charge 0.65 s (Hytale Charged tag)" and not r_b and str(w2[0]) == "no damage step and no charged launch",
              "Z4: GearCharged.judge on a real Damage: the DamageSequence meta decides (%s)" % wa_)
        # review finding 1 end to end: a partial-draw arrow Damage judged against a picked spear record
        dz3 = Dmg(None, 0, 10.0)
        sq3 = UZ.allocateInstance(DSq.class_)
        fz(DSq, "damageCalculator").set(sq3, bpart[0][0])
        dz3.putMetaObject(DCS_.DAMAGE_SEQUENCE, sq3)
        spr_ = Shot(U1, IS("Weapon_Spear_Iron", 1), None, None)
        r_c = bool(Charged.judge(dz3, "Weapon_Spear_Iron", spr_, JArray(JString)(["Weapon_Spear_Iron"]), w2))
        wc_ = str(w2[0])
        r_d = bool(Charged.judge(dz3, "Weapon_Spear_Iron", spr_, JArray(JString)(["Weapon_Spear_Iron", "Weapon_Shortbow_Iron"]), w2))
        wd_ = str(w2[0])
        r_e = bool(Charged.judge(dz3, "Weapon_Spear_Iron", None, JArray(JString)(["Weapon_Spear_Iron"]), w2))
        check(not r_c and wc_ == "projectile step not in the walk of its shot's weapon - not charged" and not r_d and wd_.startswith("partial charge (")
              and wd_.endswith("fired by Weapon_Shortbow_Iron") and r_e and str(w2[0]) == "Hytale Charged tag (the step is not in the walk)",
              "Z4: GearCharged.judge: a partial-draw arrow against a picked spear record never counts (%s / %s); melee (no record) keeps the fallback"
              % (wc_, wd_))
    except Exception as ex_:
        print("Z4. note: a bare JVM cannot build a Damage here (%s) - judge() is covered through judgeCalc + the bytecode check" % ex_)
    print("Z4. per-hit rules done")

    # ---- Z5. roll eligibility per family (runtime walk), charged.on off, and the fallback when the walk cannot run
    fam_tab = []
    FAMS = ["Weapon_Sword_", "Weapon_Battleaxe_", "Weapon_Mace_", "Weapon_Daggers_", "Weapon_Axe_", "Weapon_Longsword_", "Weapon_Spear_",
            "Weapon_Shortbow_", "Weapon_Crossbow_", "Weapon_Staff_", "Weapon_Wand_", "Weapon_Spellbook_", "Weapon_Club_", "Weapon_Kunai"]
    for fp in FAMS:
        g_ = [i for i in ALLW if i.startswith(fp) and bool(Data.isGear(i))]
        yes = [i for i in g_ if I_CHG in [int(x) for x in Roll.pool(int(Data.slotOf(i)), i)]]
        e0 = zsum[yes[0]][0] if yes else None
        fam_tab.append((fp, len(g_), len(yes), sorted(set(g_) - set(yes)), str(e0[4]).split(" - ", 1)[1].split(";")[0] if e0 is not None else "-"))
    exp_tab = {"Weapon_Sword_": (23, 23), "Weapon_Battleaxe_": (15, 15), "Weapon_Mace_": (12, 12), "Weapon_Daggers_": (16, 16),
               "Weapon_Axe_": (13, 13), "Weapon_Longsword_": (18, 18), "Weapon_Spear_": (17, 17), "Weapon_Shortbow_": (19, 14),
               "Weapon_Crossbow_": (2 + len(PACKI), 2 + len(PACKI)), "Weapon_Staff_": (24, 22), "Weapon_Wand_": (5, 3),
               "Weapon_Spellbook_": (6, 5), "Weapon_Club_": (22, 0), "Weapon_Kunai": (1, 0)}
    check(all((ng, nr) == exp_tab[fp] for fp, ng, nr, _no, _s in fam_tab), "Z5: per family (gear items, may roll chg) = %s"
          % [(fp, ng, nr) for fp, ng, nr, _no, _s in fam_tab])
    print("Z5. per family (runtime walk, charged.on on): family | gear | may roll | never rolls on | what counts (first item)")
    for fp, ng, nr, no, sm in fam_tab:
        print("     %-18s %3d %3d  %s | %s" % (fp, ng, nr, ", ".join(x[len("Weapon_"):] for x in no) or "-", sm))
    check(I_CHG in [int(x) for x in Roll.pool(2, "Armor_Iron_Chest")] and I_CHG in [int(x) for x in Roll.pool(2, None)]
          and I_CHG not in [int(x) for x in Roll.pool(0, None)] and I_CHG not in [int(x) for x in Roll.pool(4, "Skyy_Ring_Gold")],
          "Z5: armor always may roll it; a weapon without a known id never; Equipment never")
    Cfg.CHG_ON = False
    check(not any(I_CHG in [int(x) for x in Roll.pool(s_, i)] for i in ALLW + ["Armor_Iron_Chest", None] for s_ in (0, 1, 2, 4)),
          "Z5: charged.on off -> never in any pool (Skyy's lock: a stat that does nothing never rolls)")
    Cfg.CHG_ON = True
    # every roll path with chg the ONLY stat that has a weight (every other stats.<key> weight 0, chg at the loader's cap 100000) so
    # one leak would show and a charged item's every roll must carry it (review-of-0.1.2 run: with the other weights left on, a
    # one-modifier roll - Normal craft / identify - could still pick another stat now and then: one run gave a flaky 119/120)
    pw = Props()
    smx_ = [int(x) for x in Cfg.S_MAX]
    for i_, k_ in enumerate(SK):
        pw.setProperty("stats." + k_, "%d,%d" % (smx_[i_], 100000 if k_ == "chg" else 0))
    Cfg.apply(pw, False)
    check([i_ for i_ in range(len(SK)) if int(Cfg.S_W[i_]) != 0] == [I_CHG] and int(Cfg.S_W[I_CHG]) == 100000,
          "Z5: roll-path test setup: chg is the only weighted stat")

    def has_chg(dd):
        return "chg" in keys_of(dd)
    paths = lambda iid: [Roll.newDoc(iid, 5, True, "admin"), Roll.craftDoc(iid, U1), Roll.identify(iid, Roll.unidDoc(iid, 1, "drop"), U1),
                         Roll.reforge(iid, Roll.newDoc(iid, 3, True, "admin"))]
    on_sword = sum(1 for _ in range(30) for dd in paths("Weapon_Sword_Iron") if has_chg(dd))
    on_bow = sum(1 for _ in range(30) for dd in paths("Weapon_Shortbow_Crude") if has_chg(dd))
    on_armor = sum(1 for _ in range(30) for dd in paths("Armor_Iron_Chest") if has_chg(dd))
    on_club = sum(1 for _ in range(30) for dd in paths("Weapon_Club_Iron") + paths("Weapon_Club_Steel_Flail_Rusty") + paths("Weapon_Kunai")
                  + paths("Weapon_Staff_Crystal_Ice") + paths("Weapon_Staff_Crystal_Flame") + paths("Weapon_Shortbow_Bomb")
                  + paths("Weapon_Shortbow_Vampire") if has_chg(dd))
    Cfg.CHG_ON = False
    off_all = sum(1 for _ in range(30) for iid in ("Weapon_Sword_Iron", "Armor_Iron_Chest", "Weapon_Spear_Iron", "Weapon_Staff_Wood")
                  for dd in paths(iid) if has_chg(dd))
    Cfg.CHG_ON = True
    check(on_sword == 120 and on_bow == 120 and on_armor == 120 and on_club == 0 and off_all == 0,
          "Z5: /gear give, crafting, identify, reforge: chg on every charged weapon / armor roll (%d/%d/%d of 120), never on clubs / Kunai / "
          "Crystal Ice / Crystal Flame / prototype bow / Vampire bow (%d), never with charged.on off (%d)" % (on_sword, on_bow, on_armor, on_club, off_all))
    Cfg.apply(Props(), False)
    # the walk cannot run (no item assets): the list the build baked decides, excluded families still never
    saved = dict((k_, imap.get(k_)) for k_ in ("Weapon_Sword_Iron", "Weapon_Club_Iron", "Weapon_Shortbow_Bomb", "Weapon_Crossbow_Modded"))
    for k_ in saved:
        imap.remove(k_)
    Chg.clear()
    check(bool(Chg.hasCharged("Weapon_Sword_Iron")) and not bool(Chg.hasCharged("Weapon_Club_Iron")) and not bool(Chg.hasCharged("Weapon_Shortbow_Bomb"))
          and not bool(Chg.hasCharged("Weapon_Crossbow_Modded")) and "using the built-in list: has a charged attack" in str(Chg.summary("Weapon_Sword_Iron")),
          "Z5: without a runtime walk the baked vanilla list decides (sword yes; club, prototype bow, unknown modded id no)")
    for k_, v_ in saved.items():
        imap.put(k_, v_)
    Chg.clear()
    print("Z5. roll eligibility done")

    # ---- Z6. the verifier's failure cases: a single spellbook / a single thrown spear is used up by the cast before GearShotTrack
    # records the projectile -> GearHand.pick supplies the stack that launched it (live hand first, then the snapshot <= 1 s old)
    def gstack(iid, pairs=(("chg", 20), ("str", 7))):
        dd = Roll.newDoc(iid, 0, True, "admin")
        arr_ = JClass("org.bson.BsonArray")()
        for k_, v_ in pairs:
            arr_.add(Data.mod(k_, v_))
        dd.put("mods", arr_)
        return Data.put(IS(iid, 1), dd, U1)

    ORB, SPR = "Skeleton_Mage_Corruption_Orb", "Spear_Iron"
    book, spear, sword = gstack("Weapon_Spellbook_Fire"), gstack("Weapon_Spear_Iron"), gstack("Weapon_Sword_Iron")
    EMPTY = None
    now_ms = int(time.time() * 1000)
    Hand.CUR.clear()
    Hand.seen(U1, book)                                   # the book was in the hand at the last tick
    pk = Hand.pick(U1, EMPTY, ORB, now_ms + 50)
    check(pk is not None and pk.equals(book), "Z6: single spellbook: the hand is empty at the record, the snapshot supplies the book")
    check(int(Chg.launchCode(pk.getItemId(), ORB)) == 1, "Z6: ... and its orb launch is charged (GearShot.charged)")
    Hand.CUR.clear()
    Hand.seen(U1, book)
    Hand.seen(U1, EMPTY)                                  # GearHandSys ran after the cast used the book up (the other system order)
    check(Hand.pick(U1, EMPTY, ORB, int(time.time() * 1000) + 20).equals(book), "Z6: ... also when the snapshot already saw the empty hand")
    Hand.CUR.clear()
    Hand.seen(U1, spear)
    ps_ = Hand.pick(U1, EMPTY, SPR, int(time.time() * 1000) + 30)
    check(ps_ is not None and ps_.equals(spear) and int(Chg.launchCode(ps_.getItemId(), SPR)) == 1, "Z6: single thrown spear: the snapshot supplies the spear")
    four = IS("Weapon_Spellbook_Fire", 4)
    check(same(Hand.pick(U1, four, ORB, now_ms), four), "Z6: a stack of books still in the hand = the live hand wins")
    Hand.CUR.clear()
    Hand.seen(U1, spear)
    Hand.seen(U1, EMPTY)
    check(Hand.pick(U1, EMPTY, SPR, int(time.time() * 1000) + 2500) is None, "Z6: a snapshot older than 1 s is never used")
    Hand.CUR.clear()
    Hand.seen(U1, spear)
    check(Hand.pick(U1, EMPTY, ORB, now_ms) is None, "Z6: a snapshot that does not launch this projectile is never used")
    Hand.CUR.clear()
    Hand.seen(U1, IS("Weapon_Bomb_Potion_Poison", 1))
    check(Hand.pick(U1, EMPTY, "Bomb_Potion_Poison", now_ms) is None, "Z6: a non-gear snapshot (a thrown potion bomb) is never used (0.1 behaviour)")
    Hand.CUR.clear()
    Hand.seen(U1, sword)
    check(Hand.pick(U2, EMPTY, SPR, now_ms) is None, "Z6: snapshots are per player")
    # review of 0.1.2 finding 5: an empty hand that turns into another empty hand (null <-> ItemStack.EMPTY) keeps the previous slot
    Hand.CUR.clear()
    Hand.seen(U1, spear)
    Hand.seen(U1, EMPTY)
    Hand.seen(U1, IS.EMPTY)
    Hand.seen(U1, EMPTY)
    ps2_ = Hand.pick(U1, IS.EMPTY, SPR, int(time.time() * 1000) + 30)
    check(ps2_ is not None and ps2_.equals(spear) and bool(IS.EMPTY.isEmpty()),
          "Z6: finding 5 - null / empty-stack flips of an empty hand never push the thrown spear out of the snapshot")
    # what the fix changes in combat: the recorded main now carries the book's own stats (it had none) and the level gate sees it
    rec_ = Shot(U1, book, None, None)
    rec_.charged = True
    rec_.pid = ORB
    tb = Stats.totals(U1, rec_.main, None, None, True)
    check(int(tb[I_CHG]) == 20 and int(tb[si("str")]) == 7 and int(Stats.totals(U1, None, None, None, True)[I_CHG]) == 0,
          "Z6: the single book's own Charged Attack Damage 20% + Strength 7 now apply to its orb (before: empty hand = armor only)")
    check(jc(None, rec_.main.getItemId(), False, rec_.charged, rec_.pid, proj=True) == (1, "charged launch (Skeleton_Mage_Corruption_Orb)")
          and abs(float(Hit.hitAmount(100.0, tb, True, True, 0.9, 0.9)) - 100.0 * 1.0 * 1.03) < 1e-9,
          "Z6: the orb counts as charged, as a spell: 100 x (1 + 0.15 x 20%) = 103 (no Magical Power on the book)")
    check(not bool(Chg.canRoll("Weapon_Staff_Crystal_Ice", 1)) and not bool(Chg.canRoll("Weapon_Staff_Crystal_Flame", 1))
          and bool(Chg.canRoll("Weapon_Staff_Iron", 1)) and bool(Chg.canRoll("Weapon_Spellbook_Fire", 1)) and bool(Chg.canRoll("Weapon_Wand_Wood", 1)),
          "Z6: Crystal Ice (its Ice hits never reach the stat code) + Crystal Flame never roll it; orb staffs / spellbooks / wands do")
    Hand.CUR.clear()
    print("Z6. verifier cases done")

    # ---- Z7. the one-time config.properties update GearCfg.migrate012 (setup order importRolls -> migrate011 -> migrateStat011 ->
    # migrate012 -> load), on scratch copies
    ZD = os.path.join(SCRATCH, "work", "z012")

    def zcase(name, data):
        shutil.rmtree(os.path.join(ZD, name), ignore_errors=True)
        d_ = os.path.join(ZD, name, "mods", "Skyy_SkyyGear")
        os.makedirs(d_)
        f_ = os.path.join(d_, "config.properties")
        if data is not None:
            open(f_, "wb").write(data)
        Cfg.DIR = Paths.get(d_)
        Cfg.FILE = Paths.get(f_)
        return d_, f_

    CHG2 = ["# chg = Charged Attack Damage (weapon, armor, %)", "stats.chg=30,5"]
    BLK = [CHM] + [x for k_ in ("charged.on", "charged.spellFactor", "charged.log") for x in (
        {"charged.on": "# Charged Attack Damage in combat: ", "charged.spellFactor": "# Charged bonus on spells: ",
         "charged.log": "# Log charged hits: "}[k_] + zh[k_], "%s=%s" % (k_, zd[k_]))]
    ADD_ALL = "stats.chg, charged.on, charged.spellFactor, charged.log"
    INFO12 = ("config.properties: added the 0.1.2 Charged Attack Damage lines (%s) with their built-in defaults - nothing changes in effect; "
              "the old file is in config-history" % ADD_ALL)

    def exp12(t, anchor_c="stats.cd=30,10", anchor_b="speed.per=1", nl="\n"):
        """the expected result, built independently: the two blocks right after their anchor lines"""
        ls_ = t.split(nl)
        i_ = ls_.index(anchor_b)
        ls_[i_ + 1:i_ + 1] = BLK
        j_ = ls_.index(anchor_c)
        ls_[j_ + 1:j_ + 1] = CHG2
        return nl.join(ls_)

    if live is not None:
        d, f = zcase("a-live", live)
        r011 = str(Cfg.migrate011())
        r_st = str(Cfg.migrateStat011())
        mid = rb(f)
        r12 = str(Cfg.migrate012())
        got = rb(f)
        check(r011.startswith("config.properties updated to the 0.1.1 level table") and r_st.startswith("config.properties updated to the 0.1.1 stat defaults"),
              "Z7(a): the live 0.1 file first gets both 0.1.1 updates (sections X / Y)")
        check(got == exp12(mid.decode("latin-1")).encode("latin-1"), "Z7(a): exactly the stat line under stats.cd + the marker and three rows under speed.per")
        check(r12 == INFO12, "Z7(a): the INFO line: %s" % r12)
        print("Z7. INFO line the live file produces: [SkyyGear] " + r12)
        pm, pg = props(mid.decode("latin-1")), props(got.decode("latin-1"))
        check(all(pg.get(k_) == v_ for k_, v_ in pm.items()) and sorted(set(pg) - set(pm)) == ["charged.log", "charged.on", "charged.spellFactor", "stats.chg"]
              and pg["stats.chg"] == "30,5" and pg["charged.spellFactor"] == "0.15", "Z7(a): every old value kept; the four new keys hold their defaults")
        b_ = baks(d)
        ix = idx(d)
        check(len(b_) == 3 and rb(os.path.join(d, "config-history", b_[0])) == live and rb(os.path.join(d, "config-history", b_[2])) == mid
              and ix[2].split("\t")[3:] == ["SkyyGear 0.1.2", "before the 0.1.2 charged attack lines"],
              "Z7(a): History = the 0.1 file, after the level update, after the stat update (3 versions; the last named 'SkyyGear 0.1.2')")
        check(len(clog(d)) == 8, "Z7(a): no config-changes.log line (values unchanged) - still the 8 lines of the two 0.1.1 updates")
        Cfg.load()
        check(bool(Cfg.CHG_ON) and abs(float(Cfg.CHG_SPELL) - 0.15) < 1e-12 and int(Cfg.S_MAX[I_CHG]) == 30 and int(Cfg.S_W[I_CHG]) == 5,
              "Z7(a): the loader reads the new lines")
        fresh = zdt.encode("latin-1")
        check(props(got.decode("latin-1")) == props(zdt), "Z7(a): the fully updated live file has every value of a fresh 0.1.2 file")
        # (b) the second start changes nothing
        check(str(Cfg.migrate011()) == "" and str(Cfg.migrateStat011()) == "" and str(Cfg.migrate012()) == "" and rb(f) == got
              and len(baks(d)) == 3 and len(idx(d)) == 3, "Z7(b): a second start changes nothing (file, History)")
        # (f) Server Setup's stat table lists chg now (the reason for the update): the kit's keys op after CfgPub.start
        CfgPubZ = J("CfgPub")
        OAz = JArray(JObject)
        CfgPubZ.start(Paths.get(os.path.dirname(d)), None)
        ks_ = bridge.get("config:fn:SkyyGear").apply(OAz(["keys", "stat", ""]))
        kd_ = dict(zip([str(x) for x in ks_[0]], [str(x) for x in ks_[2]]))
        cg_ = bridge.get("config:fn:SkyyGear").apply(OAz(["get", "charged.spellFactor"]))
        check(kd_.get("chg") == "30|5" and str(cg_) == "0.15", "Z7(f): Server Setup lists stat chg 30|5 and charged.spellFactor 0.15 (%s)" % kd_.get("chg"))
        rset = bridge.get("config:fn:SkyyGear").apply(OAz(["set", "charged.on", "false", None, "console", "yes", "console"]))
        CfgPubZ.flush()
        check(str(rset[0]) == "ok" and "\ncharged.on=false\n" in rb(f).decode("latin-1") and not bool(Cfg.CHG_ON),
              "Z7(f): switching charged.on off in game rewrites only that line and applies at once")
        Cfg.CHG_ON = True
    # (c) no file: the loader writes the fresh 0.1.2 file (marker included); the update leaves it alone
    d, f = zcase("c-fresh", None)
    check(str(Cfg.migrate012()) == "" and not os.path.exists(f), "Z7(c): no file -> nothing written")
    Cfg.load()
    fz_ = rb(f)
    check(fz_ == zdt.encode("utf-8") and str(Cfg.migrate012()) == "" and rb(f) == fz_ and not baks(d), "Z7(c): the fresh file never updates")
    # (d) CRLF kept; (e) keys already there kept + noted; (g) anchors missing / the end-of-file continuation trap
    base = zdt.replace(CHM + "\n", "").replace("\n".join(CHG2) + "\n", "")
    for k_ in ("charged.on", "charged.spellFactor", "charged.log"):
        base = base.replace(BLK[1 + 2 * ("charged.on", "charged.spellFactor", "charged.log").index(k_)] + "\n%s=%s\n" % (k_, zd[k_]), "")
    check("charged." not in base and "stats.chg" not in base and str(Cfg.CH_MARK_ID) not in base, "Z7: the 0.1.1-shaped test file has no 0.1.2 line")
    r = Cfg.chUpdate(base)
    check(r is not None and str(r[0]) == exp12(base) and str(r[0]) == zdt, "Z7: the text step on the 0.1.1 shape gives exactly the fresh 0.1.2 file")
    crlf = base.replace("\n", "\r\n")
    r = Cfg.chUpdate(crlf)
    check(r is not None and str(r[0]) == exp12(base).replace("\n", "\r\n"), "Z7(d): CRLF kept on every added line")
    hand_ = base.replace("stats.cd=30,10\n", "stats.cd=30,10\nstats.chg=10,1\n").replace("speed.per=1\n", "speed.per=1\ncharged.on=false\n")
    r = Cfg.chUpdate(hand_)
    check(r is not None and str(r[1]) == "charged.spellFactor, charged.log" and [str(x) for x in r[2]] == [
        "stats.chg is already in the file - kept", "charged.on is already in the file - kept"]
          and props(str(r[0]))["stats.chg"] == "10,1" and props(str(r[0]))["charged.on"] == "false", "Z7(e): hand-added lines kept + noted")
    ends = [("a=1\nstats.dmg=30,10\ncombat.strPer=1\n", "a=1\nstats.dmg=30,10\n" + "\n".join(CHG2) + "\ncombat.strPer=1\n" + "\n".join(BLK) + "\n"),
            ("a=1\n", "a=1\n" + "\n".join(BLK[:1] + CHG2 + BLK[1:]) + "\n"),
            ("a=1", "a=1\n" + "\n".join(BLK[:1] + CHG2 + BLK[1:])),
            ("a=1\r\nb=x\\", "a=1\r\n" + "\r\n".join(BLK[:1] + CHG2 + BLK[1:]) + "\r\nb=x\\"),
            ("speed.per=2\\", "\n".join(BLK[:1] + CHG2 + BLK[1:]) + "\nspeed.per=2\\"),
            ("a=1\nb=x\\\n", "a=1\n" + "\n".join(BLK[:1] + CHG2 + BLK[1:]) + "\nb=x\\\n"),
            ("speed.per=1\\\n", "\n".join(BLK[:1] + CHG2 + BLK[1:]) + "\nspeed.per=1\\\n"),
            ("stats.cd=1\\\n\ncombat.strPer=1\n", "stats.cd=1\\\n\n" + "\n".join(CHG2) + "\ncombat.strPer=1\n" + "\n".join(BLK) + "\n"),
            ("\\\ncharged.on=false\nspeed.per=1\n", "\\\ncharged.on=false\nspeed.per=1\n" + "\n".join(BLK[:1] + CHG2 + BLK[3:]) + "\n"),
            ("", "\n".join(BLK[:1] + CHG2 + BLK[1:]) + "\n")]
    for t_, want in ends:
        r = Cfg.chUpdate(t_)
        check(r is not None and str(r[0]) == want and Cfg.chUpdate(str(r[0])) is None, "Z7(g): %r -> %r (got %r)" % (t_, want, r and str(r[0])))
    check(Cfg.chUpdate("x=1\n# " + str(Cfg.CH_MARK_ID) + " anything\n") is None and Cfg.chUpdate("x=1\n  ! " + str(Cfg.CH_MARK_ID) + "\n") is None
          and Cfg.chUpdate("note=" + str(Cfg.CH_MARK_ID) + "\n") is not None, "Z7(g): the marker counts only in a comment line")
    # (h) random files: same Properties values + only the missing new keys (with their defaults), the old lines in order, run once
    import random as _r
    rz = _r.Random(20260930 + 12)
    BSl = "\\"
    zpieces = ["a=1", "b=x" + BSl, "c=y" + BSl + BSl, "#c" + BSl, "# note", "", "   z" + BSl, BSl, "d:e", "  f g" + BSl, "!x" + BSl,
               "stats.cd=30,10", "stats.dmg=30,10", "speed.per=1", "combat.strPer=1", "stats.chg=9,9", "charged.on=false", "crit.base=0"]
    newk = {"stats.chg": "30,5", "charged.on": "true", "charged.spellFactor": "0.15", "charged.log": "false"}
    zbad2 = []
    for n_ in range(3000):
        ls_ = [rz.choice(zpieces) for _q in range(rz.randint(0, 10))]
        nl_ = "\r\n" if rz.random() < 0.3 else "\n"
        t_ = nl_.join(ls_) + (nl_ if rz.random() < 0.6 else "")
        r = Cfg.chUpdate(t_)
        if r is None:
            zbad2.append(("none", t_))
            continue
        o_ = str(r[0])
        pt_, po_ = props(t_), props(o_)
        want = dict(pt_)
        for k_, v_ in newk.items():
            want.setdefault(k_, v_)
        # the added lines removed again = the original text, byte for byte (CR of an appended-after line aside)
        added = set(BLK + CHG2)
        back = [x for x in o_.split("\n") if x.rstrip("\r") not in added]
        back_t = "\n".join(back)
        if po_ != want or Cfg.chUpdate(o_) is not None or (back_t != t_ and back_t.replace("\r", "") != t_.replace("\r", "")):
            zbad2.append(("bad", t_))
    check(not zbad2, "Z7(h): 3000 random files (continuations, comments ending in a backslash, lone backslashes, CRLF, no final newline): "
                     "Properties = old values + only the missing new keys, old lines kept in order, the next pass does nothing (%d bad, first %r)"
                     % (len(zbad2), zbad2[:1]))
    # (i) History cannot be written -> WARN, untouched, the next start updates
    if live is not None:
        d, f = zcase("i-nohist", live)
        Cfg.migrate011()
        Cfg.migrateStat011()
        before = rb(f)
        shutil.rmtree(os.path.join(d, "config-history"))
        open(os.path.join(d, "config-history"), "w").write("x")
        Log.FILE = Paths.get(os.path.join(d, "gear.log"))
        check(str(Cfg.migrate012()) == "" and rb(f) == before, "Z7(i): History blocked -> the file stays untouched")
        Log.flush()
        gl = open(os.path.join(d, "gear.log"), encoding="utf-8").read() if os.path.exists(os.path.join(d, "gear.log")) else ""
        check("NOT given the 0.1.2 charged attack lines" in gl and "the next start tries again" in gl, "Z7(i): one WARN says why")
        os.remove(os.path.join(d, "config-history"))
        check(str(Cfg.migrate012()) == INFO12 and rb(f) == exp12(before.decode("latin-1")).encode("latin-1"), "Z7(i): the next start updates it")
        Log.FILE = None
    Cfg.FILE = None
    Cfg.DIR = None
    Cfg.apply(Props(), False)
    print("Z7. migrate012 done")

    # ---- Z8. start twice on a scratch COPY of the whole live Skyy_SkyyGear folder (read only source): setup()'s file steps in its
    # order - GearQual.load, importRolls, migrate011, migrateStat011, migrate012, load, CfgPub.start - then the same again
    live_dir = os.path.dirname(LIVE)
    if os.path.isdir(live_dir):
        z8 = os.path.join(ZD, "live-start", "mods")
        shutil.rmtree(os.path.dirname(z8), ignore_errors=True)
        shutil.copytree(live_dir, os.path.join(z8, "Skyy_SkyyGear"))
        rolls_src = os.path.join(os.path.dirname(live_dir), "Skyy_SkyyRolls")
        if os.path.isdir(rolls_src):
            shutil.copytree(rolls_src, os.path.join(z8, "Skyy_SkyyRolls"))
        gdir = os.path.join(z8, "Skyy_SkyyGear")

        def snapshot_dir():
            out_ = {}
            for root_, _ds, fs_ in os.walk(gdir):
                for fn_ in fs_:
                    p_ = os.path.join(root_, fn_)
                    out_[os.path.relpath(p_, gdir).replace(os.sep, "/")] = rb(p_)
            return out_

        def start_once():
            Cfg.DIR = Paths.get(gdir)
            Cfg.FILE = Paths.get(os.path.join(gdir, "config.properties"))
            Log.FILE = Paths.get(os.path.join(gdir, "gear.log"))
            Qual.load(Paths.get(os.path.join(gdir, "quality.properties")))
            Cfg.importRolls(Cfg.FILE, Paths.get(os.path.join(z8, "Skyy_SkyyRolls", "reforge.properties")))
            infos = [str(Cfg.migrate011()), str(Cfg.migrateStat011()), str(Cfg.migrate012())]
            Cfg.load()
            J("CfgPub").start(Paths.get(z8), None)
            J("CfgPub").flush()
            Log.flush()
            return infos

        pre = snapshot_dir()
        i1 = start_once()
        s1 = snapshot_dir()
        i2 = start_once()
        s2 = snapshot_dir()
        changed1 = sorted(k_ for k_ in set(s1) | set(pre) if s1.get(k_) != pre.get(k_))
        changed2 = sorted(k_ for k_ in set(s2) | set(s1) if s2.get(k_) != s1.get(k_) and k_ != "gear.log")
        check(all(x for x in i1) and i1[2] == INFO12 and not any(x for x in i2),
              "Z8: first start: the three one-time updates run (level table, stat defaults, charged lines); second start: none")
        check(not changed2, "Z8: second start - every file except gear.log is byte-identical: %s" % changed2)
        hist = sorted(k_ for k_ in s1 if k_.startswith("config-history/") and k_.endswith(".bak"))
        check(len(hist) == 3 and s1[hist[0]] == pre["config.properties"], "Z8: first start keeps 3 History versions, the first = the live file")
        check(props(s1["config.properties"].decode("latin-1")) == props(zdt), "Z8: the live data ends with every value of a fresh 0.1.2 file")
        print("Z8. live copy: first start changed %s; second start changed %s (gear.log only)" % (changed1, changed2 or "nothing"))
        for x in i1:
            print("Z8.   [SkyyGear] " + x.split("\n")[0])
        Log.FILE = None
        Cfg.FILE = None
        Cfg.DIR = None
        Cfg.apply(Props(), False)
    else:
        print("Z8. note: no live Skyy_SkyyGear folder at %s - the live start test was skipped" % live_dir)

    # ---- Z9. bytecode: setup order, the combat hook, the shot record, the roll entry points, /gear charged (admin)
    def mcode(cls, name, sig=None):
        cc_ = pool.get(PKG + cls)
        outs = []
        for mm in list(cc_.getDeclaredMethods()):
            if str(mm.getName()) == name and (sig is None or sig in str(mm.getSignature())):
                bo_ = BOS()
                IP(PS(bo_)).print_(mm)
                outs.append(str(bo_.toString()))
        return "\n".join(outs)

    su = mcode("SkyyGearPlugin", "setup")
    order = [su.find("GearCfg.importRolls("), su.find("GearCfg.migrate011("), su.find("GearCfg.migrateStat011("), su.find("GearCfg.migrate012("),
             su.find("GearCfg.load("), su.find("GearCharged.setup("), su.find("CfgPub.start(")]
    check(all(x >= 0 for x in order) and order == sorted(order), "Z9: setup(): importRolls -> migrate011 -> migrateStat011 -> migrate012 -> load -> "
                                                                  "GearCharged.setup -> CfgPub.start (%s)" % order)
    hs = mcode("GearHitSys", "handle")
    check("GearCharged.watch(" in hs and "GearCharged.judge(" in hs and "GearCharged.note(" in hs
          and "GearHit.hitAmount((D[IZZDD)D)" in hs and "GearHit.hitAmount((D[IZDD)D)" not in hs,
          "Z9: GearHitSys judges the hit and calls the 6-argument hitAmount (never the old 5-argument one)")
    # review of 0.1.2 finding 1: the judge gets the live record ids only for a picked record (GearShotTrack.find's own record = exact)
    check("GearShotTrack.liveIds(" in hs and hs.find("GearShotTrack.liveIds(") < hs.find("GearCharged.judge("),
          "Z9: GearHitSys passes GearShotTrack.liveIds to GearCharged.judge")
    # finding 4: note() builds its line only while a probe is armed or charged.log is on
    nt_ = mcode("GearCharged", "note")
    check(0 <= nt_.find("GearCharged.watch(") < nt_.find("Gear.fnum(") and 0 <= nt_.find("GearCfg.CHG_LOG") < nt_.find("Gear.fnum("),
          "Z9: finding 4 - GearCharged.note checks the probe + charged.log before it builds the line")
    Charged.PROBE.clear()
    Charged.LAST.clear()
    Cfg.CHG_LOG = False
    Charged.note(U1, None, IS("Weapon_Sword_Iron", 1), True, "test", False, 20, JFloat(10.0), 12.0)
    lz_ = Charged.LAST.size()
    Charged.PROBE.put(U1, JClass("java.lang.Long").valueOf(JLong(int(time.time() * 1000) + 60000)))
    Charged.note(U1, None, IS("Weapon_Sword_Iron", 1), True, "test", False, 20, JFloat(10.0), 12.0)
    lp_ = Charged.LAST.get(U1)
    check(lz_ == 0 and lp_ is not None and str(lp_[1]).startswith("CHARGED - test - Weapon_Sword_Iron - damage "),
          "Z9: note(): nothing kept without a probe; an armed probe keeps the line (%s)" % (None if lp_ is None else str(lp_[1])))
    Charged.PROBE.clear()
    Charged.LAST.clear()
    st_ = mcode("GearShotTrack", "onEntityAdded")
    check("getProjectileAssetName" in st_ and "GearHand.pick(" in st_ and "GearChg.launchCode(" in st_ and "GearShot.charged" in st_,
          "Z9: GearShotTrack records the projectile id, takes the hand snapshot, sets GearShot.charged")
    callers2 = {}
    for cn in names:
        if not cn.startswith(PKG):
            continue
        for mm in pool.get(cn).getDeclaredMethods():
            bo_ = BOS()
            IP(PS(bo_)).print_(mm)
            tx_ = str(bo_.toString())
            for callee in ("GearRoll.pool((ILjava/lang/String;)", "GearRoll.pool((I)", "GearRoll.rollMods((Ljava/lang/String;III)",
                           "GearRoll.rollMods((III)", "GearChg.canRoll(", "GearHand.pick(", "GearCharged.judge("):
                if ("gear." + callee) in tx_:
                    callers2.setdefault(callee, set()).add(cn[len(PKG):] + "." + str(mm.getName()) + str(mm.getSignature()).split(")")[0] + ")")
    check(callers2.get("GearRoll.pool((ILjava/lang/String;)") == {"GearRoll.rollMods(Ljava/lang/String;III)", "GearRoll.pool(I)"},
          "Z9: pool(slot, id) <- rollMods(id, ...) + the pool(slot) overload only: %s" % callers2.get("GearRoll.pool((ILjava/lang/String;)"))
    check("GearRoll.pool((I)" not in callers2, "Z9: nothing calls the id-less pool(slot) (%s)" % callers2.get("GearRoll.pool((I)"))
    check(callers2.get("GearRoll.rollMods((Ljava/lang/String;III)") == {"GearRoll.newDoc(Ljava/lang/String;IZLjava/lang/String;)",
                                                                        "GearRoll.reforge(Ljava/lang/String;Lorg/bson/BsonDocument;)",
                                                                        "GearRoll.identify(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/UUID;)",
                                                                        "GearRoll.rollMods(III)"},
          "Z9: rollMods(id, ...) <- newDoc / reforge / identify (with the item id) + the old overload: %s" % callers2.get("GearRoll.rollMods((Ljava/lang/String;III)"))
    check("GearRoll.rollMods((III)" not in callers2, "Z9: nothing calls the id-less rollMods(slot, r, lvl)")
    check(callers2.get("GearChg.canRoll(") == {"GearRoll.pool(ILjava/lang/String;)", "GearCharged.probe(Ljava/util/UUID;Lcom/hypixel/hytale/server/core/inventory/ItemStack;[ILjava/lang/String;)"},
          "Z9: canRoll <- GearRoll.pool (+ the read-only probe): %s" % callers2.get("GearChg.canRoll("))
    cc_ = pool.get(PKG + "GearChargedCmd")
    IPc = JClass("javassist.bytecode.InstructionPrinter")
    k0 = cc_.getDeclaredConstructors()[0]
    it_ = k0.getMethodInfo().getCodeAttribute().iterator()
    cpz = k0.getMethodInfo().getConstPool()
    ops = []
    while it_.hasNext():
        pos_ = it_.next()
        ops.append(str(IPc.instructionString(it_, pos_, cpz)))
    ctxt = "\n".join(ops)
    check("requirePermission" in ctxt and "setPermissionGroups" in ctxt and "anewarray" in ctxt and "iconst_0" in ctxt and "skyygear.admin" in ctxt
          and '"charged"' in ctxt, "Z9: /gear charged = requirePermission(skyygear.admin) + setPermissionGroups(new String[0])")
    gk = pool.get(PKG + "GearCmd").getDeclaredConstructors()[0]
    it_ = gk.getMethodInfo().getCodeAttribute().iterator()
    cpz = gk.getMethodInfo().getConstPool()
    ops = []
    while it_.hasNext():
        pos_ = it_.next()
        ops.append(str(IPc.instructionString(it_, pos_, cpz)))
    check("GearChargedCmd" in "\n".join(ops) and '"hytale:Adventurer"' in "\n".join(ops), "Z9: /gear (Adventurer) adds the admin sub-command charged")
    try:
        cmdz = J("GearChargedCmd")()
        AC_ = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
        fpg = AC_.class_.getDeclaredField("permissionGroups")
        fpg.setAccessible(True)
        grp = fpg.get(cmdz)
        check(grp is not None and len(grp) == 0, "Z9: the constructed /gear charged command carries an empty permission-group list")
    except Exception as ex_:
        print("Z9. note: constructing the command object in a bare JVM failed (%s) - the constructor bytecode check above stands" % ex_)
    print("Z9. bytecode done")

    # ---- Z10. class byte-compare 0.1.1 -> 0.1.2 (instruction text with constant-pool numbers stripped, fields with their types and
    # constant values): every difference must be one of the listed new parts (a member outside this list = FAIL)
    jar011 = os.path.join(HERE, "SkyyGear-0.1.1.jar")

    def znorm(t):
        """instruction text without constant-pool numbers, byte offsets and branch targets; ldc_w = ldc (a constant pool that grew past
        255 entries turns ldc into ldc_w and shifts every offset after it - the same code)"""
        out_ = []
        for ln in t.split("\n"):
            ln = re.sub(r"#\d+ = ", "", ln)
            ln = re.sub(r"^\s*\d+: ", "", ln)
            ln = ln.replace("ldc_w ", "ldc ")
            ln = re.sub(r"^(goto|goto_w|jsr|if\w*) \d+", r"\1 L", ln)
            out_.append(ln)
        return "\n".join(out_)

    def ival(ln):
        m_ = re.match(r"^(?:iconst_(\d)|bipush (-?\d+)|sipush (-?\d+))$", ln.strip())
        return None if not m_ else int([g for g in m_.groups() if g is not None][0])

    def shift_only(a_, b_):
        """0.1.1 -> 0.1.2 differs ONLY by the stat-index shift: chg went in at index 5, so every stat index >= 5 (and the stat count 40,
        i.e. NS) is exactly one higher; javassist inlines static final int constants, so the methods that use them change that way"""
        la_, lb_ = a_.split("\n"), b_.split("\n")
        if len(la_) != len(lb_):
            return False
        for x_, y_ in zip(la_, lb_):
            if x_ == y_:
                continue
            vx, vy = ival(x_), ival(y_)
            if vx is None or vy is None or vy != vx + 1 or not (5 <= vx <= 40):
                return False
        return True

    if os.path.isfile(jar011):
        def cls_members(p_, cn):
            cc_ = p_.get(cn)
            mem = {}
            for mm in list(cc_.getDeclaredMethods()):
                bo_ = BOS()
                IP(PS(bo_)).print_(mm)
                mem["m " + str(mm.getName()) + str(mm.getSignature())] = znorm(str(bo_.toString()))
            for k0 in list(cc_.getDeclaredConstructors()):
                ca = k0.getMethodInfo().getCodeAttribute()
                it_ = ca.iterator()
                cp_ = k0.getMethodInfo().getConstPool()
                ops_ = []
                while it_.hasNext():
                    pz_ = it_.next()
                    ops_.append(str(JClass("javassist.bytecode.InstructionPrinter").instructionString(it_, pz_, cp_)))
                mem["c " + str(k0.getSignature())] = znorm("\n".join(ops_))
            ci = cc_.getClassInitializer()
            if ci is not None:
                ca = ci.getMethodInfo().getCodeAttribute()
                it_ = ca.iterator()
                cp_ = ci.getMethodInfo().getConstPool()
                ops_ = []
                while it_.hasNext():
                    pz_ = it_.next()
                    ops_.append(str(JClass("javassist.bytecode.InstructionPrinter").instructionString(it_, pz_, cp_)))
                mem["<clinit>"] = znorm("\n".join(ops_))
            for f_ in list(cc_.getDeclaredFields()):
                cv = None
                try:
                    cv = f_.getConstantValue()
                except Exception:
                    cv = None
                mem["f " + str(f_.getName())] = str(f_.getSignature()) + " = " + str(cv)
            mem["interfaces"] = ",".join(sorted(str(x) for x in cc_.getClassFile().getInterfaces())) + " super " + str(cc_.getClassFile().getSuperclass())
            return mem

        pa = Pool(False)
        pa.appendClassPath(jar011)
        pa.appendClassPath(B.SERVER_JAR)
        pa.appendSystemPath()
        pb = Pool(False)
        pb.appendClassPath(jar)
        pb.appendClassPath(B.SERVER_JAR)
        pb.appendSystemPath()
        n011 = sorted(n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar011).namelist() if n.endswith(".class"))
        n012 = sorted(n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class"))
        added_cls = sorted(set(n012) - set(n011))
        gone_cls = sorted(set(n011) - set(n012))
        diffs, shifted = {}, {}
        for cn in sorted(set(n011) & set(n012)):
            ma, mb = cls_members(pa, cn), cls_members(pb, cn)
            dd = sorted(k_ for k_ in set(ma) | set(mb) if ma.get(k_) != mb.get(k_))
            for k_ in dd:
                if k_ in ma and k_ in mb and k_.startswith("f ") and ma[k_].split(" = ")[0] == mb[k_].split(" = ")[0]:
                    try:
                        if int(mb[k_].split(" = ")[1]) == int(ma[k_].split(" = ")[1]) + 1 and 5 <= int(ma[k_].split(" = ")[1]) <= 40:
                            shifted.setdefault(cn[len(PKG):], []).append(k_)
                            continue
                    except ValueError:
                        pass
                if k_ in ma and k_ in mb and not k_.startswith("f ") and shift_only(ma[k_], mb[k_]):
                    shifted.setdefault(cn[len(PKG):], []).append(k_)
                    continue
                diffs.setdefault(cn[len(PKG):], []).append(("+" if k_ not in ma else ("-" if k_ not in mb else "~")) + k_)
        # every difference, with its reason (checked by hand against the build script; kept exact so a stray change fails here)
        EXPECT = {
            # config kit (tools/skyycfg.py, regenerated from the rows): 41 -> 44 rows, VERSION 0.1.1 -> 0.1.2
            "CfgFile": ["~<clinit>"],
            "CfgFn": ["~m opExport([Ljava/lang/Object;)Ljava/lang/Object;"],
            "CfgRows": ["~<clinit>", "~f VERSION", "~m header()[Ljava/lang/Object;"],
            # /gear charged (read only, before the profile:busy check)
            "GearAdmin": ["~m run(Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/universe/PlayerRef;Ljava/lang/String;Ljava/lang/String;)V"],
            # disconnect: GearCharged.forget (probe + hand snapshot)
            "GearBye": ["~m accept(Ljava/lang/Object;)V"],
            # the charged.* fields + loader lines, the stat arrays (41 stats), the default text, migrate012 + its text step
            "GearCfg": ["~<clinit>", "+f CHG_ADD", "+f CHG_LOG", "+f CHG_ON", "+f CHG_SPELL", "+f CH_MARK", "+f CH_MARK_ID", "+f CH_ROWC",
                        "+f CH_ROWK", "+f CH_ROWL", "+f CH_WHO", "~m apply(Ljava/util/Properties;Z)V", "+m chAfter(Ljava/util/ArrayList;II)I",
                        "+m chEnd(Ljava/util/ArrayList;I[Ljava/lang/String;)I", "+m chPut(Ljava/util/ArrayList;ILjava/util/ArrayList;Ljava/lang/String;)V",
                        "+m chUpdate(Ljava/lang/String;)[Ljava/lang/Object;", "~m defaultsText()Ljava/lang/String;", "+m migrate012()Ljava/lang/String;"],
            # /gear adds the charged sub-command
            "GearCmd": ["~c ()V"],
            # the stat tables with chg after cd + I_CHG
            "GearDefs": ["~<clinit>", "+f I_CHG"],
            # the charged factor (6-argument hitAmount; the 5-argument one now delegates with chg = false)
            "GearHit": ["+f I_CHG", "~m hitAmount(D[IZDD)D", "+m hitAmount(D[IZZDD)D"],
            # judge + note + the 6-argument hitAmount, srec
            "GearHitSys": ["~m handle(ILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/system/EcsEvent;)V"],
            # the item id reaches the pool (newDoc / reforge / identify pass it; the id-less overloads delegate)
            "GearRoll": ["~m identify(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/UUID;)Lorg/bson/BsonDocument;",
                         "~m newDoc(Ljava/lang/String;IZLjava/lang/String;)Lorg/bson/BsonDocument;", "~m pool(I)[I", "+m pool(ILjava/lang/String;)[I",
                         "~m reforge(Ljava/lang/String;Lorg/bson/BsonDocument;)Lorg/bson/BsonDocument;", "~m rollMods(III)Lorg/bson/BsonArray;",
                         "+m rollMods(Ljava/lang/String;III)Lorg/bson/BsonArray;"],
            # the launch record: charged flag, projectile id, snapshot used
            "GearShot": ["+f charged", "+f pid", "+f snap"],
            # + the review of 0.1.2 finding 1: liveIds (the item ids of the shooter's live records for the charged judge)
            "GearShotTrack": ["+m liveIds(Ljava/util/UUID;)[Ljava/lang/String;",
                              "~m onEntityAdded(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/AddReason;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V"],
            # the grey "(off on this server)" line while charged.on is off
            "GearView": ["+m dim(Ljava/lang/String;)Z", "~m statLines(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/ArrayList;Ljava/util/ArrayList;)V",
                         "~m suffix(I)Ljava/lang/String;"],
            # migrate012 in the setup order, GearCharged.setup (GearHandSys), the ready line
            "SkyyGearPlugin": ["~m setup()V"]}
        check([c[len(PKG):] for c in added_cls] == ["GearCharged", "GearChargedCmd", "GearChg", "GearChgState", "GearChgVars", "GearChgWalk", "GearHand",
                                                    "GearHandSys"] and not gone_cls,
              "Z10: new classes = the 7 charged-attack classes + GearChargedCmd, none removed: %s / %s" % (added_cls, gone_cls))
        extra = dict((c, [m for m in ms if m not in EXPECT.get(c, [])]) for c, ms in diffs.items())
        extra = dict((c, ms) for c, ms in extra.items() if ms)
        missing_ = dict((c, [m for m in ms if m not in diffs.get(c, [])]) for c, ms in EXPECT.items())
        missing_ = dict((c, ms) for c, ms in missing_.items() if ms)
        check(not extra, "Z10: no difference outside the listed new parts: %s" % extra)
        check(not missing_, "Z10: every listed part really differs (the list is exact): %s" % missing_)
        same_cls = len(set(n011) & set(n012)) - len(set(diffs) | set(shifted))
        print("Z10. 0.1.1 -> 0.1.2 class compare: %d classes identical, %d with new parts, %d with only the stat-index shift, %d new"
              % (same_cls, len(diffs), len(set(shifted) - set(diffs)), len(added_cls)))
        for c in sorted(diffs):
            print("     %-16s %s" % (c, ", ".join(re.sub(r"\(.*", "", m_) for m_ in diffs[c])))
        print("     stat-index shift only (every stat index >= 5 and NS exactly +1): " + "; ".join(
            "%s: %s" % (c, ", ".join(re.sub(r"\(.*", "", m_) for m_ in ms)) for c, ms in sorted(shifted.items())))
        ea = [n for n in zipfile.ZipFile(jar011).namelist() if not n.endswith(".class")]
        eb = [n for n in zipfile.ZipFile(jar).namelist() if not n.endswith(".class")]
        za, zb = zipfile.ZipFile(jar011), zipfile.ZipFile(jar)
        ndiff = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
        check(ndiff == ["manifest.json"], "Z10: non-class entries: only manifest.json differs (version): %s" % ndiff)
    else:
        print("Z10. note: SkyyGear-0.1.1.jar not found - the class compare was skipped")
    print("Z. 0.1.2 Charged Attack Damage done")


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
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--dir", SCRATCH, "--live", LIVE], env=env)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s bare-JVM check:" % VERSION, "PASS" if p.returncode == 0 else "FAIL")
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
