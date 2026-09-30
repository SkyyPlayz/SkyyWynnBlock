"""Bare-JVM check for SkyyEssentials 0.1.6 (the item durability switch; kept next to the build so the build report can be re-run).

    python SkyyEssentials/test_skyyessentials_0.1.6.py [--jar <SkyyEssentials-0.1.6.jar>] [--dir <scratch folder>] [--keep]

Build the jar first (python SkyyEssentials/build_skyyessentials_0.1.6.py). Child processes start fresh JVMs (the game's own JRE,
-Xverify:all, HytaleServer.jar + the jar + tools/javassist.jar on the classpath). A bare JVM has no asset stores, so an Item store and an
Interaction store are put in place (real DefaultAssetMap / IndexedLookupTableAssetMap, filled with REAL engine asset objects: Item,
ItemTool$DurabilityLossBlockTypes, BlockSelectorToolData, ModifyInventoryInteraction) - EssDur then runs its production path
(Item.getAssetMap().getAssetMap(), Interaction.getAssetMap().getAssetMap()) against them.
  phase main
    A  every class loads and verifies (-Xverify:all)
    B  defaults = 0.1.5's (the 0.1.5 build script's ROWS) + gameplay.durability false; the default file has the gameplay block
    C  the config kit header: 22 rows, 7 categories (gameplay second), every 0.1.5 row published exactly as before, the two new rows
    D  the switch on real engine objects: OFF zeroes the four costs (engine getters read 0), R1 keeps BrokenItem charges and repairs,
       ON restores exactly, OFF / ON twice, idempotent, an asset reload while OFF, a value changed meanwhile is left alone, stop()
       restores; SIMULATED LOSS through engine code: ItemUtils.updateItemStackDurability with the engine's own cost (sword, armor, a
       near-zero item: no break), BlockHarvestUtils.calculateDurabilityUse (tool fallback), the hammer / tool-block / ModifyInventory
       numbers, EssDurDeath on a real DeathComponent after the value PlayerDropItemsConfig copies (10 -> 0 while OFF, 10 kept ON, 10
       kept while the switch is UNAVAILABLE) and its dependencies (AFTER PlayerDropItemsConfig, BEFORE DropPlayerDeathItems, BEFORE
       PlayerDeathScreen)
    E  the row through config:fn:SkyyEssentials (console): turning ON asks (its own question), OFF does not, after= applies at once,
       a second caller with the same state does nothing, the file line, the change log, hand edit + reload (TCfg.reloadKit ->
       EssDur.sync), the 1 s re-check (EssDurTick), import preview, an asset reload while OFF (the listener only flags; EssDurTick
       rescans; a failed rescan keeps the flag and is retried)
    F  repair: isWear / needsRepair on real Items and stacks (cans, buckets, fertilizer skipped), the engine behaviour the action relies
       on (withDurability keeps metadata, replaceItemStackInSlot refuses a changed slot), EssRepairJob counting, the action asks first and
       answers without throwing in a bare JVM (no Universe)
    G  bytecode: setup probes EssDur.fields and registers EssDurDeath + the two asset listeners before CfgPub.start, start() ->
       EssDur.start after claimR, shutdown -> EssDur.stop before CfgPub.shutdown; the switch writes no item stack; the asset listener
       only sets the flag (no scan, no monitor: it runs inside the engine's ASSET_LOCK); the death rule reads EssDur.BROKEN
    H  permissions with the engine's own AbstractCommand code (unchanged commands: hytale:Adventurer gets only player nodes)
    I  garbage ops never throw
    J  the engine's own DependencyGraph on the real DeathSystems + EssDurDeath (stand-in EntityModule for their static queries): all 24
       registration orders put EssDurDeath after PlayerDropItemsConfig and before DropPlayerDeathItems and PlayerDeathScreen
  phase live1 / live2: two starts (load + config kit + EssDur.start / stop) on a scratch COPY of the live world's Skyy_SkyyEssentials
    folder (read only from UserData\\Saves\\HUD mod\\mods): the first start appends only the gameplay.durability block to config.properties
    and changes no other byte of any file; the second start changes nothing at all.
  Z  class byte-compare SkyyEssentials-0.1.5.jar vs 0.1.6.jar (which classes differ, and in the classes the switch does not touch only the
     version strings differ)
NOT runnable in a bare JVM: real worlds, players, damage, block breaks, deaths and the repair on a live inventory - in-game steps.
Nothing is deployed. Default scratch folder: tools/dev/scratch/ess016/test (git-ignored), deleted at the end unless --keep; TEMP/TMP and
java.io.tmpdir point into it. Exit code 1 on any failure.
"""
import os, sys, re, ast, json, shutil, subprocess, time, zipfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "dev"))
VERSION = "0.1.6"
PREV = "0.1.5"
PKG = "com.skyy.essentials."
LIVE = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData", "Saves", "HUD mod", "mods",
                    "Skyy_SkyyEssentials")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "ess016", "test")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyEssentials-%s.jar" % VERSION)))
PREV_JAR = os.path.join(HERE, "SkyyEssentials-%s.jar" % PREV)
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def script_list(script, name, env=None):
    """A module-level list literal (ROWS / KIT_ROWS) of a build script; the script is only read, never run."""
    src = open(os.path.join(HERE, script), encoding="utf8").read()
    m = re.search(r"^%s = (\[.*?^\])" % name, src, re.M | re.S)
    return eval(m.group(1), {"__builtins__": {}}, dict(env or {}))


def props_of(text):
    out = {}
    for l in text.replace("\r\n", "\n").split("\n"):
        s = l.strip()
        if not s or s[0] in "#!" or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def tree_bytes(d):
    out = {}
    for r, _, fs in os.walk(d):
        for f in fs:
            p = os.path.join(r, f)
            out[os.path.relpath(p, d).replace(os.sep, "/")] = open(p, "rb").read()
    return out


# ============================================================================================================== child: shared JVM setup
def boot(jar):
    import jpype
    import skyybuild as B
    from jpype import JClass
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, jar, B.JAVASSIST], convertStrings=True)
    return B


class World(object):
    """Fake Item + Interaction asset stores holding real engine asset objects (the SkyyGear harness pattern, extended)."""

    def __init__(self, B):
        from jpype import JClass, JArray, JImplements, JOverride
        self.J = JClass
        Unsafe = JClass("sun.misc.Unsafe")
        uf = Unsafe.class_.getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        self.us = uf.get(None)
        AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
        jp = JClass("javassist.ClassPool")(True)
        jp.appendClassPath(B.SERVER_JAR)
        fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
        fake.addConstructor(JClass("javassist.CtNewConstructor").make(
            "public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
        fcls = fake.toClass(AS.class_)
        fm = AS.class_.getDeclaredField("assetMap")
        fm.setAccessible(True)
        self.DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
        inner = self.DAM.class_.getDeclaredField("assetMap")
        inner.setAccessible(True)
        self.Item = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
        self.Inter = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction")
        # Item: a DefaultAssetMap
        istore = self.us.allocateInstance(fcls)
        self.imap = self.DAM()
        fm.set(istore, self.imap)
        self.fm, self.istore = fm, istore          # (E: an unreadable asset map for the failed-rescan retry check)
        f = self.Item.class_.getDeclaredField("ASSET_STORE")
        f.setAccessible(True)
        f.set(None, istore)
        # Interaction: an IndexedLookupTableAssetMap (Interaction.getAssetMap() casts to it)
        Inter = self.Inter

        @JImplements("java.util.function.IntFunction")
        class Arr(object):
            @JOverride
            def apply(self, n):
                return JClass("java.lang.reflect.Array").newInstance(Inter.class_, int(n))

        self._arr = Arr()
        nstore = self.us.allocateInstance(fcls)
        self.nmap = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")(self._arr)
        fm.set(nstore, self.nmap)
        f = Inter.class_.getDeclaredField("ASSET_STORE")
        f.setAccessible(True)
        f.set(None, nstore)
        self.items = inner.get(self.imap)          # the maps behind getAssetMap() (unmodifiable views of these)
        self.inters = inner.get(self.nmap)
        self.fields = {}

    def fld(self, cls, name):
        k = (str(cls.class_.getName()), name)
        if k not in self.fields:
            f = cls.class_.getDeclaredField(name)
            f.setAccessible(True)
            self.fields[k] = f
        return self.fields[k]

    def item(self, iid, max_dur=0.0, hit=0.0, weapon=False, armor=False, tool=None, hammer=None, repairable=True, consumable=False,
             death=True, put=True):
        J = self.J
        it = self.Item(iid)
        self.fld(self.Item, "maxDurability").setDouble(it, float(max_dur))
        self.fld(self.Item, "durabilityLossOnHit").setDouble(it, float(hit))
        if weapon:
            self.fld(self.Item, "weapon").set(it, J("com.hypixel.hytale.server.core.asset.type.item.config.ItemWeapon")())
        if armor:
            # (ItemArmor() is protected; an allocated instance is enough: only "has an armor config" is read)
            self.fld(self.Item, "armor").set(it, self.us.allocateInstance(J("com.hypixel.hytale.server.core.asset.type.item.config.ItemArmor").class_))
        if tool is not None:
            T = J("com.hypixel.hytale.server.core.asset.type.item.config.ItemTool")
            DL = J("com.hypixel.hytale.server.core.asset.type.item.config.ItemTool$DurabilityLossBlockTypes")
            arr = None
            if tool:
                arr = J("java.lang.reflect.Array").newInstance(DL.class_, len(tool))
                for i, v in enumerate(tool):
                    arr[i] = DL(None, None, float(v))
            t = T(None, 1.0, arr)          # the public ItemTool(ItemToolSpec[], float, DurabilityLossBlockTypes[])
            self.fld(self.Item, "tool").set(it, t)
        if hammer is not None:
            BS = J("com.hypixel.hytale.server.core.asset.type.item.config.BlockSelectorToolData")
            h = self.us.allocateInstance(BS.class_)
            self.fld(BS, "durabilityLossOnUse").setDouble(h, float(hammer))
            self.fld(self.Item, "blockSelectorToolData").set(it, h)
        self.fld(self.Item, "repairable").setBoolean(it, bool(repairable))
        self.fld(self.Item, "consumable").setBoolean(it, bool(consumable))
        self.fld(self.Item, "durabilityLossOnDeath").setBoolean(it, bool(death))
        if put:
            self.items.put(iid, it)
        return it

    def modinv(self, iid, adjust, broken=None):
        MI = self.J("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.ModifyInventoryInteraction")
        m = MI()
        self.fld(self.Inter, "id").set(m, iid)
        self.fld(MI, "adjustHeldItemDurability").setDouble(m, float(adjust))
        self.fld(MI, "brokenItem").set(m, broken)
        self.inters.put(iid, m)
        return m

    def adj(self, m):
        MI = self.J("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.ModifyInventoryInteraction")
        return float(self.fld(MI, "adjustHeldItemDurability").getDouble(m))


def paths_for(TC, ES, Paths, home):
    """What SkyyEssentialsPlugin.setup() points TCfg / EssStore at."""
    ES.CFG = Paths.get(os.path.join(home, "config.properties"))
    TC.DIR = Paths.get(home)
    TC.TDIR = Paths.get(os.path.join(home, "trades"))
    TC.PDIR = Paths.get(os.path.join(home, "trades", "pending"))
    TC.ADIR = Paths.get(os.path.join(home, "trades", "archive"))
    TC.LOGF = Paths.get(os.path.join(home, "trades", "trade.log"))
    TC.NAMESF = Paths.get(os.path.join(home, "trades", "names.properties"))


def vanilla_like(W):
    """A small vanilla-shaped asset set (numbers from research/Durability-Switch-Research.md 1 + 2.3)."""
    it = {
        "sword": W.item("Weapon_Sword_Test", 100, 0.21, weapon=True),
        "armor": W.item("Armor_Chest_Test", 100, 0.5, armor=True),
        "pick": W.item("Tool_Pickaxe_Test", 100, 0.25, tool=[0.25, 0.1]),
        "shovel": W.item("Tool_Shovel_Test", 100, 0.05, tool=[]),
        "hammer": W.item("Tool_Hammer_Test", 50, 0.0, tool=[], hammer=1.0),
        "can": W.item("Tool_Watering_Can_Test", 20, 0.0, repairable=False, death=False),
        "fert": W.item("Tool_Fertilizer_Test", 5, 0.0, tool=[], death=False),
        "bucket": W.item("Container_Bucket_Test", 3, 0.0, consumable=True, death=False),
        "healer": W.item("Weapon_Odd_Heal_Test", 100, -0.5, weapon=True),       # a negative cost (repair on hit) is not wear: untouched
        "plain": W.item("Ingredient_Stick_Test", 0, 0.0),
    }
    ia = {
        "hatchet": W.modinv("Hatchet_Chop_Damage_Test", -1.0),
        "staff": W.modinv("*Ice_Staff_Primary_Entry_Test", -0.5),
        "cans": W.modinv("Watering_Can_Use_Test", -1.0, "Tool_Watering_Can"),
        "bucket": W.modinv("*Container_Bucket_Test_Use", -1.0, "Empty"),
        "fert": W.modinv("Fertilizer_Use_Test", -1.0, "Empty"),
        "repair": W.modinv("Odd_Repair_Test", 5.0),
    }
    return it, ia


# ============================================================================================================== phase main
def run_main(jar):
    B = boot(jar)
    import jpype
    from jpype import JClass, JArray, JObject, JImplements, JOverride

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
    check(len(names) == 67, "67 classes in the jar (0.1.5: 61 + EssDur, EssDurTick, EssDurAssetL, EssRepairJob, EssRepairTask, EssDurDeath; got %d)"
          % len(names))
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return

    W = World(B)
    ES, TC, Rows, Pub, Dur = (JClass(PKG + "EssStore"), JClass(PKG + "TCfg"), JClass(PKG + "CfgRows"), JClass(PKG + "CfgPub"),
                              JClass(PKG + "EssDur"))
    UUID, Paths, Integer = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Integer")
    rows15 = script_list("build_skyyessentials_%s.py" % PREV, "ROWS")
    rows16 = script_list("build_skyyessentials_%s.py" % VERSION, "ROWS")

    # ---------------- B. defaults
    check(not bool(Dur.ON) and int(Dur.APPLIED) == -1 and not bool(Dur.STARTED), "EssDur.ON false (durability OFF), nothing applied yet")
    keys = [str(k) for k in TC.KEYS]
    for r in rows15:
        i = keys.index(r[0]) if r[0] in keys else -1
        check(i >= 0 and str(TC.get(i)) == r[6] and str(TC.DEFAULTS[i]) == r[6], "default %s = 0.1.5 %s (got %s)" % (
            r[0], r[6], TC.get(i) if i >= 0 else "missing"))
    check(len(keys) == len(rows15) + 1 and keys[-1] == "gameplay.durability", "one new loader key, gameplay.durability, last: %s" % keys[-3:])
    gi = keys.index("gameplay.durability")
    check(str(TC.get(gi)) == "false" and str(TC.DEFAULTS[gi]) == "false" and str(TC.TYPES[gi]) == "bool", "gameplay.durability bool false")
    dt = str(TC.DEFAULT_TEXT)
    check(dt.endswith("#\n# ---- gameplay (SkyyEssentials 0.1.6) ----\n# %s\ngameplay.durability=false\n" % rows16[-1][8]),
          "the default file ends with the gameplay block")
    check(props_of(dt) == dict((x[0], x[6]) for x in rows16), "default file keys + values = the 0.1.6 rows")
    print("B. defaults = 0.1.5 + gameplay.durability false")

    work = os.path.join(SCRATCH, "work")
    shutil.rmtree(work, ignore_errors=True)
    mods = os.path.join(work, "mods")
    home = os.path.join(mods, "Skyy_SkyyEssentials")
    os.makedirs(home)
    paths_for(TC, ES, Paths, home)
    cfgp = os.path.join(home, "config.properties")
    # a 0.1.5 file (every 0.1.5 key with its default, as 0.1.5 wrote it for a new install) - load appends only the new key
    t15 = "".join("%s=%s\n" % (r[0], r[6]) for r in rows15)
    open(cfgp, "wb").write(t15.encode("latin-1"))
    TC.load()
    now = open(cfgp, "rb").read().decode("latin-1")
    check(now == t15 + "#\n# ---- added by SkyyEssentials 0.1.6 (keys this file did not have yet, with their defaults) ----\n# %s\n"
          "gameplay.durability=false\n" % rows16[-1][8], "a 0.1.5 file gets exactly the gameplay.durability line appended:\n%s" % now[-400:])
    check(not bool(Dur.ON) and int(Dur.APPLIED) == -1, "load() sets the field only (the switch applies in start())")

    # ---------------- C. the kit header
    Pub.start(Paths.get(mods), None)
    bridge = TC.bridge()
    fn = bridge.get("config:fn:SkyyEssentials")
    hdr = bridge.get("config:def:SkyyEssentials")
    check(fn is not None and hdr is not None and str(hdr[3]) == VERSION, "config:fn + config:def published, version %s" % VERSION)
    cats = [str(x) for x in hdr[5]]
    labs = [str(x) for x in hdr[6]]
    check(cats == ["parts", "gameplay", "tpa", "msg", "privacy", "warps", "trade"] and labs[1] == "Gameplay", "categories %s %s" % (cats, labs))
    rows = [[str(x) for x in row] for row in hdr[7]]
    check(len(rows) == 22, "22 rows (0.1.5: 20 + gameplay.durability + gameplay.repairOnline; got %d)" % len(rows))
    byk = dict((x[0], x) for x in rows)
    kit15 = script_list("build_skyyessentials_%s.py" % PREV, "KIT_ROWS", {"CF": "@config.properties:"})
    for r in kit15:
        check(byk.get(r[0]) == [str(x) for x in r[:11]], "0.1.5 row %s published unchanged" % r[0])
    d = byk.get("gameplay.durability")
    check(d == ["gameplay.durability", "Item durability", "gameplay", "bool", "false", "", "", "", "", "live,danger",
                "Off: tools, weapons and armor never lose durability or break. Worn items keep their current value."], "row gameplay.durability %s" % d)
    a = byk.get("gameplay.repairOnline")
    check(a is not None and a[1:4] == ["Repair gear of online players", "gameplay", "action"] and a[7] == "Repair now" and a[9] == "danger"
          and len(a[10]) <= 100 and len(a) == 11, "row gameplay.repairOnline %s" % a)
    check(all(len(x[10]) <= 100 and len(x[1]) <= 40 for x in rows), "labels <= 40, help <= 100")
    check(int(Rows.KEEP) == 10, "KEEP = 10")

    def op(*args):
        arr = JArray(JObject)(len(args))
        for i, x in enumerate(args):
            arr[i] = x
        return fn.apply(arr)

    def R(r):
        return (str(r[0]), None if r[1] is None else str(r[1]), str(r[2])) if r is not None else None

    def get(k):
        v = op("get", k)
        return None if v is None else str(v)

    def cset(k, v, confirm="yes"):
        return R(op("set", k, v, None, None, confirm, "console"))

    def settle():
        Pub.flush()
        time.sleep(0.5)
        Pub.flush()

    def logs():
        return [str(x) for x in op("log", Integer.valueOf(200))]

    check(get("gameplay.durability") == "false", "kit get gameplay.durability = false")
    settle()
    check(open(cfgp, "rb").read().decode("latin-1") == now, "the kit does not rewrite the file at start")
    print("C. kit header done")

    # ---------------- D. the switch on real engine asset objects
    it, ia = vanilla_like(W)
    orig = {"sword": 0.21, "armor": 0.5, "pick": 0.25, "shovel": 0.05, "hammer": 0.0, "healer": -0.5, "plain": 0.0}

    def blk(item):
        tl = item.getTool()
        a_ = None if tl is None else tl.getDurabilityLossBlockTypes()
        return [] if a_ is None else [float(x.getDurabilityLossOnHit()) for x in a_]

    def state():
        return (dict((k, float(it[k].getDurabilityLossOnHit())) for k in orig), blk(it["pick"]),
                float(it["hammer"].getBlockSelectorToolData().getDurabilityLossOnUse()), dict((k, W.adj(v)) for k, v in ia.items()))

    vanilla = state()
    check(vanilla[1] == [0.25, 0.1] and vanilla[2] == 1.0 and vanilla[3]["hatchet"] == -1.0, "fixture reads back through the engine getters")
    check(bool(Dur.fields()) and not bool(Dur.BROKEN), "EssDur finds the five engine fields")
    try:
        Dur.fld(W.Item.class_, "noSuchField")
        check(False, "fld() refuses a missing field")
    except Exception:
        check(True, "fld() refuses a missing field")
    # client packet caches (SoftReferences the engine fills lazily): the changed assets' references get cleared, never replaced
    SR, Obj = JClass("java.lang.ref.SoftReference"), JClass("java.lang.Object")
    keep = [Obj() for _ in range(4)]                   # strong references: only EssDur may clear these

    def arm():
        refs = {"hammer": SR(keep[0]), "sword": SR(keep[1]), "hatchet": SR(keep[2]), "cans": SR(keep[3])}
        W.fld(W.Item, "cachedPacket").set(it["hammer"], refs["hammer"])
        W.fld(W.Item, "cachedPacket").set(it["sword"], refs["sword"])
        W.fld(W.Inter, "cachedPacket").set(ia["hatchet"], refs["hatchet"])
        W.fld(W.Inter, "cachedPacket").set(ia["cans"], refs["cans"])
        return refs

    def cleared(refs):
        same = (W.fld(W.Item, "cachedPacket").get(it["hammer"]).equals(refs["hammer"])
                and W.fld(W.Inter, "cachedPacket").get(ia["hatchet"]).equals(refs["hatchet"]))
        return same, dict((k, v.get() is None) for k, v in refs.items())

    refs = arm()
    # direct applies before start() (no re-check running yet)
    msg = str(Dur.applyLocked(False, False))
    same, cl = cleared(refs)
    check(same and cl == {"hammer": True, "sword": False, "hatchet": True, "cans": False},
          "OFF clears the packet caches of the changed hammer / interaction (SoftReference.clear, field kept), not the others: %s %s" % (same, cl))
    s_off = state()
    check(all(s_off[0][k] == 0.0 for k in ("sword", "armor", "pick", "shovel")) and s_off[0]["healer"] == -0.5 and s_off[0]["plain"] == 0.0,
          "OFF: positive hit costs 0 (engine getDurabilityLossOnHit), a negative one untouched: %s" % s_off[0])
    check(s_off[1] == [0.0, 0.0], "OFF: tool block costs 0 (DurabilityLossBlockTypes.getDurabilityLossOnHit): %s" % s_off[1])
    check(s_off[2] == 0.0, "OFF: hammer block-set cost 0 (getDurabilityLossOnUse)")
    check(s_off[3] == {"hatchet": 0.0, "staff": 0.0, "cans": -1.0, "bucket": -1.0, "fert": -1.0, "repair": 5.0},
          "OFF: ModifyInventory wear 0, BrokenItem charges and repairs kept (R1): %s" % s_off[3])
    check(int(Dur.APPLIED) == 0 and [int(Dur.N_HIT), int(Dur.N_BLK), int(Dur.N_USE), int(Dur.N_INT)] == [4, 2, 1, 2],
          "counts 4 hit / 2 tool block / 1 hammer / 2 interaction: %s" % [int(Dur.N_HIT), int(Dur.N_BLK), int(Dur.N_USE), int(Dur.N_INT)])
    check(msg.startswith("Item durability OFF: 4 hit costs, 2 tool block costs, 1 hammer costs and 2 interaction costs set to 0")
          and "Hatchet_Chop_Damage_Test" in msg and "*Ice_Staff_Primary_Entry_Test" in msg and "Watering_Can_Use_Test" not in msg,
          "OFF log line names the counts and the zeroed interaction ids: %s" % msg)
    check(Dur.applyLocked(False, True) is None and state() == s_off, "a second OFF (rescan) changes nothing and says nothing")
    check("interaction costs set to 0 (" not in str(Dur.applyLocked(False, False)), "the zeroed ids are logged once")
    refs = arm()
    msg = str(Dur.applyLocked(True, False))
    check(state() == vanilla and int(Dur.APPLIED) == 1, "ON: every cost back exactly: %s" % (state(),))
    same, cl = cleared(refs)
    check(same and cl == {"hammer": True, "sword": False, "hatchet": True, "cans": False}, "ON clears the same packet caches: %s" % cl)
    check(msg.startswith("Item durability ON (vanilla): 9 durability costs put back"), "ON log line (4 + 2 + 1 + 2): %s" % msg)
    Dur.applyLocked(False, False)
    Dur.applyLocked(True, False)
    check(state() == vanilla, "OFF / ON a second time: still the exact originals")
    # a value somebody changed while ON is the one the next OFF remembers; one changed while OFF is left alone by ON
    W.fld(W.Item, "durabilityLossOnHit").setDouble(it["sword"], 0.3)
    Dur.applyLocked(False, False)
    W.fld(W.Item, "durabilityLossOnHit").setDouble(it["armor"], 0.7)
    Dur.applyLocked(True, False)
    check(float(it["sword"].getDurabilityLossOnHit()) == 0.3 and float(it["armor"].getDurabilityLossOnHit()) == 0.7,
          "ON restores the value seen at OFF (0.3) and leaves a value changed meanwhile (0.7) alone")
    W.fld(W.Item, "durabilityLossOnHit").setDouble(it["sword"], 0.21)
    W.fld(W.Item, "durabilityLossOnHit").setDouble(it["armor"], 0.5)
    check(state() == vanilla, "fixture back to vanilla")

    # SIMULATED LOSS through engine code (ItemUtils.updateItemStackDurability = where L1-L6 all end, with the engine's own cost)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IU = JClass("com.hypixel.hytale.server.core.entity.ItemUtils")
    Short = JClass("java.lang.Short")

    def hit(key, dur, cost=None):
        c = SIC(Short.valueOf(4).shortValue())
        st = IS(str(it[key].getId()), 1, float(dur), 100.0, None)
        c.setItemStackForSlot(0, st)
        loss = float(it[key].getDurabilityLossOnHit()) if cost is None else cost()
        IU.updateItemStackDurability(None, st, c, 0, -loss, None)
        return float(c.getItemStack(0).getDurability())

    Dur.applyLocked(False, False)
    check(hit("sword", 50) == 50.0 and hit("armor", 50) == 50.0, "OFF: a sword hit / an armor hit leaves durability 50 (engine update path)")
    check(hit("sword", 0.1) == 0.1, "OFF: a sword at 0.1 durability does not break (no 'item broken' line / sound path)")
    check(hit("pick", 50, lambda: float(it["pick"].getTool().getDurabilityLossBlockTypes()[0].getDurabilityLossOnHit())) == 50.0,
          "OFF: a pickaxe block break leaves durability 50")
    check(hit("hammer", 50, lambda: float(it["hammer"].getBlockSelectorToolData().getDurabilityLossOnUse())) == 50.0,
          "OFF: a hammer block-set switch leaves durability 50")
    check(hit("sword", 50, lambda: -W.adj(ia["hatchet"])) == 50.0, "OFF: a hatchet hitting a mob (ModifyInventory) leaves durability 50")
    check(hit("sword", 50, lambda: -W.adj(ia["cans"])) == 49.0, "OFF: a watering can use still costs its charge (-1)")
    cdu = None
    try:
        BT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
        mcdu = JClass("com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils").class_.getDeclaredMethod(
            "calculateDurabilityUse", W.Item.class_, BT.class_)
        mcdu.setAccessible(True)
        bt = BT("Rock_Stone_Test")
        # a hard block: a BlockGathering without a soft drop (isSoft() = soft != null; a null gathering counts as soft -> 0)
        gth = W.us.allocateInstance(JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering").class_)
        W.fld(BT, "gathering").set(bt, gth)
        cdu = lambda k: float(mcdu.invoke(None, it[k], bt))
    except Exception as ex:
        print("calculateDurabilityUse not callable here: %s" % ex)
    check(cdu is not None and cdu("shovel") == 0.0, "OFF: BlockHarvestUtils.calculateDurabilityUse (tool fallback) = 0")
    Dur.applyLocked(True, False)
    check(abs(hit("sword", 50) - 49.79) < 1e-9 and hit("armor", 50) == 49.5, "ON: a sword hit costs 0.21, an armor hit 0.5 (vanilla)")
    check(hit("pick", 50, lambda: float(it["pick"].getTool().getDurabilityLossBlockTypes()[0].getDurabilityLossOnHit())) == 49.75
          and hit("hammer", 50, lambda: float(it["hammer"].getBlockSelectorToolData().getDurabilityLossOnUse())) == 49.0
          and hit("sword", 50, lambda: -W.adj(ia["hatchet"])) == 49.0, "ON: pickaxe 0.25, hammer 1, hatchet on a mob 1 (vanilla)")
    check(cdu is not None and cdu("shovel") == 0.05, "ON: calculateDurabilityUse (tool fallback) = 0.05 (got %s)" % (cdu and cdu("shovel")))

    # the death rule on a real DeathComponent (PlayerDropItemsConfig copies the world's 10 % first)
    DC = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    DeathSys = JClass(PKG + "EssDurDeath")
    ds = DeathSys()

    def death():
        dc = W.us.allocateInstance(DC.class_)       # (its no-arg constructor is not public; the percentage is a plain field)
        dc.setItemsDurabilityLossPercentage(10.0)
        ds.onComponentAdded(None, dc, None, None)
        return float(dc.getItemsDurabilityLossPercentage())

    Dur.ON = False
    check(death() == 0.0, "OFF: death durability loss 10 % -> 0 % (DropPlayerDeathItems skips at pct > 0)")
    Dur.ON = True
    check(death() == 10.0, "ON: death keeps 10 %")
    Dur.ON = False
    # 0.1.6 review: an UNAVAILABLE switch (a game update changed the engine fields) is vanilla everywhere, death included
    Dur.BROKEN = True
    check(death() == 10.0, "UNAVAILABLE (BROKEN) while OFF: death keeps 10 % too (not half a switch)")
    Dur.BROKEN = False
    check(death() == 0.0, "BROKEN back to false: OFF zeroes death wear again")
    ds.onComponentAdded(None, None, None, None)
    check(True, "a null component never throws")
    deps = [(str(x.getOrder()), str(x.getSystemClass().getName())) for x in ds.getDependencies()]
    DS = "com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$"
    check(sorted(deps) == sorted([("AFTER", DS + "PlayerDropItemsConfig"), ("BEFORE", DS + "DropPlayerDeathItems"),
                                  ("BEFORE", DS + "PlayerDeathScreen")]),
          "EssDurDeath runs AFTER PlayerDropItemsConfig, BEFORE DropPlayerDeathItems and BEFORE PlayerDeathScreen: %s" % deps)
    # (the engine's own dependency sort of the four death systems runs at the end of this phase, J: it needs a stand-in EntityModule)
    check(isinstance(ds, JClass(DS + "OnDeathSystem")), "EssDurDeath is an OnDeathSystem (RefChangeSystem on DeathComponent)")
    print("D. switch on engine objects done")

    # ---------------- start(): OFF applied, the 1 s re-check running
    Dur.ON = False
    Dur.start()
    check(bool(Dur.STARTED) and int(Dur.APPLIED) == 0 and state() == s_off, "start() with the switch OFF zeroes every cost")
    watcher = Dur.WATCH is not None
    print("re-check scheduled in this bare JVM:", watcher)

    # ---------------- E. the row through the kit (console)
    r = cset("gameplay.durability", "true", confirm="")
    check(r[0] == "confirm" and r[2] == "Turn item durability ON? Tools, weapons and armor wear out and can break again." and not bool(Dur.ON),
          "turning durability ON asks first, with its own question: %s" % (r,))
    r = cset("gameplay.durability", "true")
    check(r[0] == "ok" and bool(Dur.ON) and int(Dur.APPLIED) == 1 and state() == vanilla, "ON with yes: applied at once (after= hook): %s" % (r,))
    r = cset("gameplay.durability", "false", confirm="")
    check(r[0] == "ok" and not bool(Dur.ON) and int(Dur.APPLIED) == 0 and state() == s_off, "OFF does not ask and applies at once: %s" % (r,))
    # 0.1.6 review: the state check and the apply share the EssDur monitor - a second caller (the kit hook racing EssDurTick) with the
    # same state does nothing and returns no log line
    check(Dur.syncLocked(False) is None and int(Dur.APPLIED) == 0 and state() == s_off,
          "a second caller with the same state (OFF applied, no rescan flagged) does nothing and logs nothing")
    check(cset("gameplay.durability", "maybe")[0] == "bad" and not bool(Dur.ON), "a bad word is refused")
    r = cset("gameplay.durability", "on")
    check(r[0] == "ok" and bool(Dur.ON) and int(Dur.APPLIED) == 1, "typed 'on' works: %s" % (r,))
    cset("gameplay.durability", "off", confirm="")
    A_ = UUID.fromString("00000000-0000-0000-0000-0000000000aa")
    check(R(op("set", "gameplay.durability", "true", A_, "Someone", "yes", "menu"))[0] == "denied" and not bool(Dur.ON),
          "a player without skyyessentials.admin is denied")
    settle()
    t = open(cfgp, "rb").read().decode("latin-1")
    check(t == now, "after ON -> OFF the file line is back to gameplay.durability=false (line-preserving)")
    lg = logs()
    check(any(l.split("\t")[3:8] == ["console", "gameplay.durability", "false", "true", "ok"] for l in lg)
          and any(l.split("\t")[3:8] == ["console", "gameplay.durability", "true", "false", "ok"] for l in lg), "changes logged: %s" % lg[:4])
    # hand edit + the kit's reload op -> TCfg.reloadKit -> EssDur.sync (at once)
    open(cfgp, "wb").write(t.replace("gameplay.durability=false", "gameplay.durability=true").encode("latin-1"))
    r = R(op("reload", None, None, "console"))
    settle()
    time.sleep(0.3)
    check(r[0] == "ok" and bool(Dur.ON) and int(Dur.APPLIED) == 1 and state() == vanilla, "hand edit true + reload: switch ON: %s" % (r,))
    check(any(l.split("\t")[3:7] == ["file", "gameplay.durability", "false", "true"] for l in logs()), "hand edit logged via=file")
    t2 = open(cfgp, "rb").read().decode("latin-1")
    open(cfgp, "wb").write(t2.replace("gameplay.durability=true", "gameplay.durability=false").encode("latin-1"))
    op("reload", None, None, "console")
    settle()
    time.sleep(0.3)
    check(not bool(Dur.ON) and int(Dur.APPLIED) == 0 and state() == s_off, "hand edit back to false + reload: switch OFF")
    # the 1 s re-check: a field change that reached no hook (the kit sets field: values itself after a failed save, a mod call, ...)
    if watcher:
        Dur.ON = True
        t0 = time.time()
        while int(Dur.APPLIED) != 1 and time.time() - t0 < 3.0:
            time.sleep(0.1)
        check(int(Dur.APPLIED) == 1 and state() == vanilla, "EssDurTick follows ON within a second (%.1f s)" % (time.time() - t0))
        Dur.ON = False
        t0 = time.time()
        while int(Dur.APPLIED) != 0 and time.time() - t0 < 3.0:
            time.sleep(0.1)
        check(int(Dur.APPLIED) == 0 and state() == s_off, "EssDurTick follows OFF within a second (%.1f s)" % (time.time() - t0))
    else:
        Dur.ON = True
        JClass(PKG + "EssDurTick")().run()
        check(int(Dur.APPLIED) == 1, "EssDurTick.run follows ON (no scheduler in this JVM: run by hand)")
        Dur.ON = False
        JClass(PKG + "EssDurTick")().run()
        check(int(Dur.APPLIED) == 0, "EssDurTick.run follows OFF")
    code_ = op("export", "all")

    def unpack(cd):
        import base64, zlib
        body = str(cd).split(".")[2]
        return zlib.decompress(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))).decode("utf8")

    check(code_ is not None and "gameplay.durability=false" in unpack(code_).splitlines(), "export all carries gameplay.durability=false")
    ch = op("export", "changed")
    check(ch is not None and "gameplay.durability" not in unpack(ch), "the default value is not in an export of changed values")
    r = R(op("import", code_, None, None, "preview"))
    check(r is not None and r[0] == "ok" and "nothing to change" in r[2].lower(), "export -> import preview: nothing to change: %s" % (r,))
    # an asset reload while OFF (asset editor). 0.1.6 review: in game the listener runs inside AssetStore.loadAssets0 under
    # AssetRegistry.ASSET_LOCK, so it only raises EssDur.RESCAN (G checks its bytecode: no scan, no monitor); EssDurTick zeroes the new
    # Item / Interaction objects outside that lock within a second. A rescan that fails keeps the flag and is retried; ON restores them.
    def tick_until(cond, secs=3.0):
        if not watcher:
            JClass(PKG + "EssDurTick")().run()
        t0 = time.time()
        while not cond() and time.time() - t0 < secs:
            time.sleep(0.05)
        return bool(cond())

    new_axe = W.item("Weapon_Axe_Reloaded_Test", 100, 0.56, weapon=True)
    new_ia = W.modinv("Pickaxe_Mine_Damage_Reloaded_Test", -1.0)
    zeroed = lambda: float(new_axe.getDurabilityLossOnHit()) == 0.0 and W.adj(new_ia) == 0.0
    W.fm.set(W.istore, None)                           # the Item map cannot be read (as while the loader writes): the rescan throws
    JClass(PKG + "EssDurAssetL")().accept(None)
    check(tick_until(lambda: bool(Dur.RESCAN), 0.5) and float(new_axe.getDurabilityLossOnHit()) == 0.56,
          "the listener flags a rescan while OFF (and zeroes nothing itself)")
    if watcher:
        time.sleep(1.6)                                # at least one EssDurTick rescan attempt fails meanwhile
    else:
        JClass(PKG + "EssDurTick")().run()
    check(tick_until(lambda: bool(Dur.RESCAN), 0.5) and float(new_axe.getDurabilityLossOnHit()) == 0.56 and W.adj(new_ia) == -1.0
          and int(Dur.APPLIED) == 0, "a failed rescan keeps the flag (retried), changes nothing and keeps OFF applied")
    W.fm.set(W.istore, W.imap)
    check(tick_until(zeroed) and tick_until(lambda: not bool(Dur.RESCAN), 1.0) and state() == s_off,
          "the next EssDurTick rescans: the new objects are zeroed, the flag is cleared, the old ones stay 0")
    cset("gameplay.durability", "true")
    check(float(new_axe.getDurabilityLossOnHit()) == 0.56 and W.adj(new_ia) == -1.0 and state() == vanilla, "ON restores them too")
    JClass(PKG + "EssDurAssetL")().accept(None)
    check(not bool(Dur.RESCAN) and float(new_axe.getDurabilityLossOnHit()) == 0.56, "an asset reload while ON flags nothing, changes nothing")
    cset("gameplay.durability", "false", confirm="")
    # stop(): the originals go back (plugin unload), a new start() zeroes again
    Dur.stop()
    check(not bool(Dur.STARTED) and int(Dur.APPLIED) == -1 and state() == vanilla and float(new_axe.getDurabilityLossOnHit()) == 0.56,
          "stop() while OFF puts every original cost back")
    Dur.sync()
    check(state() == vanilla, "nothing is applied while stopped")
    Dur.start()
    check(int(Dur.APPLIED) == 0 and state() == s_off, "start() again zeroes again")
    Dur.stop()
    print("E. kit row done")

    # ---------------- F. repair
    wear = dict((k, bool(Dur.isWear(it[k]))) for k in it)
    check(wear == {"sword": True, "armor": True, "pick": True, "shovel": True, "hammer": True, "can": False, "fert": False, "bucket": False,
                   "healer": True, "plain": False}, "isWear: gear yes; watering can, fertilizer, bucket, plain no: %s" % wear)
    check(not bool(Dur.isWear(None)) and not bool(Dur.isWear(W.Item.UNKNOWN)), "isWear(null / UNKNOWN) false")
    check(it["plain"].getUtility() is not None, "engine fact: every Item has a default Utility config (so isWear must not use it)")

    def st_(key, dur, mx):
        return IS(str(it[key].getId()), 1, float(dur), float(mx), None)

    need = [bool(Dur.needsRepair(x)) for x in (st_("sword", 50, 100), st_("sword", 100, 100), st_("sword", 0, 100), st_("plain", 0, 0),
                                                 st_("can", 5, 20), st_("fert", 1, 5), st_("armor", 99.5, 100), None)]
    check(need == [True, False, True, False, False, False, True, False], "needsRepair: worn / full / broken / unbreakable / can / fertilizer "
          "/ armor / null: %s" % need)
    BD = JClass("org.bson.BsonDocument")
    md = BD.parse('{"SkyyGear": {"rarity": "Rare", "rolls": {"str": 7}}}')
    worn = IS(str(it["sword"].getId()), 1, 42.0, 100.0, md)
    fixed = worn.withDurability(worn.getMaxDurability())
    check(float(fixed.getDurability()) == 100.0 and str(fixed.getItemId()) == str(worn.getItemId()) and int(fixed.getQuantity()) == 1
          and fixed.getMetadata() is not None and fixed.getMetadata().equals(md), "withDurability keeps id, quantity and METADATA (SkyyGear rolls)")
    c = SIC(Short.valueOf(2).shortValue())
    c.setItemStackForSlot(0, worn)
    tx = c.replaceItemStackInSlot(0, worn, fixed)
    check(bool(tx.succeeded()) and float(c.getItemStack(0).getDurability()) == 100.0, "compare-and-set repair writes the slot")
    other = IS(str(it["sword"].getId()), 1, 10.0, 100.0, None)
    c.setItemStackForSlot(1, other)
    tx = c.replaceItemStackInSlot(1, worn, fixed)
    check(not bool(tx.succeeded()) and float(c.getItemStack(1).getDurability()) == 10.0,
          "a slot that changed meanwhile is left alone (no duplicate, nothing lost)")
    Job = JClass(PKG + "EssRepairJob")
    j = Job(None, "tester", 3)
    j.done(2, False)
    j.done(0, True)
    check(int(j.left.get()) == 1, "the job waits for every player")
    j.done(1, False)
    check([int(j.items.get()), int(j.players.get()), int(j.moved.get()), int(j.left.get())] == [3, 2, 1, 0], "job counts 3 items / 2 players / 1 moved")
    r = R(op("action", "gameplay.repairOnline", None, None, "", "console"))
    check(r[0] == "confirm" and r[2] == "Repair now? Fills worn tools, weapons and armor of everyone online to full. Cans, buckets and charges "
          "skipped.", "the repair action asks first (button text + help): %s" % (r,))
    r = R(op("action", "gameplay.repairOnline", None, None, "yes", "console"))
    check(r[0] == "bad" and "starting" in r[2], "before start() the action refuses: %s" % (r,))
    Dur.STARTED = True
    r = R(op("action", "gameplay.repairOnline", None, None, "yes", "console"))
    check(r is not None and r[0] in ("error", "ok"), "a bare JVM (no Universe) answers without throwing: %s" % (r,))
    Dur.STARTED = False
    check(R(op("action", "gameplay.repairOnline", A_, "Someone", "yes", "menu"))[0] == "denied", "the action needs skyyessentials.admin")
    print("F. repair done")

    # ---------------- G. bytecode
    Pool, IP, PS, BOS = (JClass("javassist.ClassPool"), JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"),
                         JClass("java.io.ByteArrayOutputStream"))
    pool = Pool(False)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    pool.appendSystemPath()

    def code(cls, meth, sig=None):
        cc = pool.get(PKG + cls)
        mm = [m_ for m_ in cc.getDeclaredMethods() if str(m_.getName()) == meth and (sig is None or sig in str(m_.getSignature()))][0]
        bos = BOS()
        IP(PS(bos)).print_(mm)
        return str(bos.toString()).splitlines()

    def idx(pat, lines):
        return [i for i, l in enumerate(lines) if pat in l]

    su = code("SkyyEssentialsPlugin", "setup")
    st = idx("CfgPub.start(", su)
    rs, rg = idx("ComponentRegistryProxy.registerSystem(", su), idx("EventRegistry.register((Ljava/lang/Class;Ljava/lang/Object;", su)
    check(len(st) == 1 and len(rs) == 1 and len(rg) == 2 and max(rs + rg) < st[0], "setup: EssDurDeath + 2 asset listeners before CfgPub.start")
    check(idx("EssDurDeath.<init>", su) and len(idx("EssDurAssetL.<init>", su)) == 2, "setup builds EssDurDeath and two EssDurAssetL")
    fp = idx("EssDur.fields(", su)
    check(len(fp) == 1 and fp[0] < st[0] and [l for l in su if "UNAVAILABLE" in l],
          "setup probes EssDur.fields() before CfgPub.start and the ready line can say UNAVAILABLE")
    # 0.1.6 review: the asset listener runs inside the engine's ASSET_LOCK - it may only raise the flag (no scan, no EssDur monitor)
    al = code("EssDur", "assetsLoaded")
    check(len(idx("putstatic", al)) == 1 and idx("EssDur.RESCAN", al) and not [l for l in al if "invoke" in l or "monitorenter" in l],
          "EssDur.assetsLoaded only sets RESCAN (no call, no monitor): %s" % [l for l in al if "invoke" in l or "putstatic" in l])
    check(not (pool.get(PKG + "EssDur").getDeclaredMethod("assetsLoaded").getModifiers() & 0x20), "assetsLoaded is not synchronized")
    la = [l for l in code("EssDurAssetL", "accept") if "invoke" in l]
    check(len(la) == 1 and "EssDur.assetsLoaded(" in la[0], "EssDurAssetL.accept calls only EssDur.assetsLoaded: %s" % la)
    dd = code("EssDurDeath", "onComponentAdded", "Lcom/hypixel/hytale/component/Component;")
    check(idx("EssDur.ON", dd) and idx("EssDur.BROKEN", dd), "the death rule reads EssDur.ON and EssDur.BROKEN")
    after = [l for l in su[st[0] + 1:] if "invoke" in l]
    check(not any(("register" in l) or ("regSetting" in l) for l in after), "nothing is registered after CfgPub.start")
    sta = code("SkyyEssentialsPlugin", "start")
    check(idx("claimR(", sta) and idx("EssDur.start(", sta) and idx("claimR(", sta)[0] < idx("EssDur.start(", sta)[0], "start: claimR then EssDur.start")
    sd = code("SkyyEssentialsPlugin", "shutdown")
    a1, a2, a3 = idx("EssDur.stop(", sd), idx("CfgPub.shutdown(", sd), idx("invokespecial", sd)
    check(a1 and a2 and a3 and a1[0] < a2[0] < a3[-1], "shutdown: EssDur.stop -> CfgPub.shutdown -> super.shutdown")
    allcode = []
    for cn in ("EssDur", "EssDurTick", "EssDurAssetL", "EssDurDeath", "EssRepairJob"):
        for mm in pool.get(PKG + cn).getDeclaredMethods():
            bos = BOS()
            IP(PS(bos)).print_(mm)
            allcode += str(bos.toString()).splitlines()
    check(not [l for l in allcode if re.search(r"ItemStack\.with|setItemStackForSlot|replaceItemStackInSlot|addItemStack|removeItemStack", l)],
          "the switch classes never create or write an item stack")
    rt = code("EssRepairTask", "run")
    check(len(idx("replaceItemStackInSlot(", rt)) == 1 and len(idx("ItemStack.withDurability(", rt)) == 1 and not idx("setItemStackForSlot", rt),
          "the repair writes only through one compare-and-set replaceItemStackInSlot")
    print("G. bytecode done")

    # ---------------- H. permissions (the engine's own AbstractCommand code; commands unchanged since 0.1.5)
    try:
        uf = JClass("java.lang.Class").forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        own = uf.get(None).allocateInstance(JClass("com.hypixel.hytale.server.core.command.system.CommandManager").class_)
    except Exception as ex:
        print("no CommandManager owner (%s)" % ex)
        own = None

    def tree(c_):
        out = [c_]
        for s_ in list(c_.getSubCommands().values()):
            out += tree(s_)
        return out

    player_roots = ["TpaCmd", "TpaHereCmd", "TpAcceptCmd", "TpDenyCmd", "TpaCancelCmd", "MsgCmd", "ReplyCmd", "RCmd", "TradeCmd"]
    admin_roots = {"FlyCmd": "skyyessentials.fly", "TradeAdminCmd": "skyyessentials.tradeadmin", "WarpAdminCmd": "skyyessentials.admin"}
    adv = []
    if own is not None:
        for n in player_roots + list(admin_roots):
            c_ = JClass(PKG + n)()
            for x in tree(c_):
                x.setOwner(own)
            mp = c_.getPermissionGroupsRecursive()
            nodes = [str(y) for k in mp.keySet() for y in mp.get(k)]
            if n in admin_roots:
                check(str(c_.getPermission()) == admin_roots[n] and mp.size() == 0, "/%s: %s, its nodes in NO group: %s" % (n, admin_roots[n], mp))
            else:
                check([str(k) for k in mp.keySet()] == ["hytale:Adventurer"] and nodes, "%s: hytale:Adventurer only: %s" % (n, mp))
                adv += nodes
        check(not [x for x in adv if x in admin_roots.values() or "admin" in x], "hytale:Adventurer gets no admin node: %s" % adv)
    else:
        check(False, "H skipped: no CommandManager owner")
    print("H. permissions done")

    # ---------------- I. garbage
    thrown = 0
    for g in [None, [], ["set", "gameplay.durability"], ["set", "gameplay.durability", 5, None, None, "yes", "console"],
              ["set", "gameplay.durability", "true", "notauuid", "n", "yes", "menu"], ["action", "gameplay.repairOnline"],
              ["action", "gameplay.repairOnline", "x", None, "yes", "menu"], ["get", "gameplay.repairOnline"], ["get", 7]]:
        try:
            if g is None:
                fn.apply(None)
            else:
                arr = JArray(JObject)(len(g))
                for i, x in enumerate(g):
                    arr[i] = x
                fn.apply(arr)
        except Exception as ex:
            thrown += 1
            print("threw", g, ex)
    check(thrown == 0 and not bool(Dur.ON), "garbage ops never throw, change nothing")
    for bad in (lambda: Dur.check(None, None), lambda: Dur.changed(None), lambda: Dur.assetsLoaded(), lambda: Dur.needsRepair(None)):
        try:
            bad()
        except Exception as ex:
            thrown += 1
            print("hook threw", ex)
    check(thrown == 0, "hooks never throw on null")
    Pub.shutdown()
    print("I. garbage done")

    # ---------------- J. the engine's own DependencyGraph on the REAL death systems + EssDurDeath (0.1.6 review, optional finding 9).
    # The engine systems' static QUERY fields need EntityModule.get() component types: a stand-in EntityModule (allocated, every
    # ComponentType field a distinct allocated ComponentType) is put in place for this last section only and removed afterwards.
    # SystemDependency matches systems by exact class, so these are the real edges. Every one of the 24 registration orders must give
    # PlayerDropItemsConfig < EssDurDeath < DropPlayerDeathItems and EssDurDeath < PlayerDeathScreen (the respawn page reads 0 %).
    EMc = JClass("java.lang.Class").forName("com.hypixel.hytale.server.core.modules.entity.EntityModule", False, loader)
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    Mod = JClass("java.lang.reflect.Modifier")
    fi = EMc.getDeclaredField("instance")
    fi.setAccessible(True)
    orders = set()
    try:
        em = W.us.allocateInstance(EMc)
        ctx = CT.class_.getDeclaredField("index")
        ctx.setAccessible(True)
        n_ = 0
        for f_ in EMc.getDeclaredFields():
            if f_.getType() == CT.class_ and not Mod.isStatic(f_.getModifiers()):
                ct = W.us.allocateInstance(CT.class_)
                n_ += 1
                ctx.setInt(ct, n_)
                f_.setAccessible(True)
                f_.set(em, ct)
        fi.set(None, em)
        import itertools
        DG = JClass("com.hypixel.hytale.component.dependency.DependencyGraph")
        ISys = JClass("com.hypixel.hytale.component.system.ISystem")
        names_ = ("PlayerDropItemsConfig", "DropPlayerDeathItems", "PlayerDeathScreen", "EssDurDeath")
        for perm in itertools.permutations(names_):
            sysl = [DeathSys() if x == "EssDurDeath" else JClass(DS + x)() for x in perm]
            arr = JArray(ISys)(len(sysl))
            for i, x in enumerate(sysl):
                arr[i] = x
            g = DG(arr)
            g.resolveEdges(None)
            out = JArray(ISys)(len(sysl))
            g.sort(out)
            orders.add(tuple(str(x.getClass().getSimpleName()) if x is not None else "?" for x in out))
    except Exception as ex:
        print("J: DependencyGraph not callable here: %s" % ex)
    finally:
        fi.set(None, None)
    ok = bool(orders) and all(len(o) == 4 and o.index("PlayerDropItemsConfig") < o.index("EssDurDeath") < o.index("DropPlayerDeathItems")
                              and o.index("EssDurDeath") < o.index("PlayerDeathScreen") for o in orders)
    check(ok, "J: engine DependencyGraph, all 24 registration orders: PlayerDropItemsConfig < EssDurDeath < DropPlayerDeathItems and "
              "EssDurDeath < PlayerDeathScreen: %s" % sorted(orders))
    print("J. engine dependency sort: %d distinct orders %s" % (len(orders), sorted(orders)))


# ============================================================================================================== phases live1 / live2
def run_live(jar, phase):
    B = boot(jar)
    from jpype import JClass, JArray, JObject
    W = World(B)
    vanilla_like(W)
    ES, TC, Pub, Dur = JClass(PKG + "EssStore"), JClass(PKG + "TCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "EssDur")
    Paths, Integer = JClass("java.nio.file.Paths"), JClass("java.lang.Integer")
    mods = os.path.join(SCRATCH, "live", "mods")
    home = os.path.join(mods, "Skyy_SkyyEssentials")
    snapf = os.path.join(SCRATCH, "live", "after-%s.json" % ("live1" if phase == "live2" else "copy"))
    before = tree_bytes(home)
    # a start: what setup() does with the data folder (TCfg.load, the config kit) and what start() adds (EssDur.start); then shutdown()
    paths_for(TC, ES, Paths, home)
    TC.load()
    Pub.start(Paths.get(mods), None)
    Dur.start()
    fn = TC.bridge().get("config:fn:SkyyEssentials")

    def op(*args):
        arr = JArray(JObject)(len(args))
        for i, x in enumerate(args):
            arr[i] = x
        return fn.apply(arr)

    check(str(op("get", "gameplay.durability")) == "false" and int(Dur.APPLIED) == 0, "%s: the switch starts OFF and is applied" % phase)
    hdr = TC.bridge().get("config:def:SkyyEssentials")
    check(any(str(r[0]) == "gameplay.durability" for r in hdr[7]), "%s: the new row is published" % phase)
    Pub.flush()
    time.sleep(0.6)
    Pub.flush()
    lg = [str(x) for x in op("log", Integer.valueOf(200))]
    check(not [l for l in lg if "\tclamped" in l or "\tinvalid" in l], "%s: no clamped / invalid log lines: %s" % (phase, lg[:3]))
    Dur.stop()
    Pub.shutdown()
    after = tree_bytes(home)
    if phase == "live1":
        cfg0 = before["config.properties"].decode("latin-1")
        cfg1 = after["config.properties"].decode("latin-1")
        nl = "\r\n" if "\r\n" in cfg0 else "\n"
        rows16 = script_list("build_skyyessentials_%s.py" % VERSION, "ROWS")
        add = ("" if cfg0.endswith("\n") else nl) + nl.join(["#", "# ---- added by SkyyEssentials 0.1.6 (keys this file did not have yet, with "
                                                               "their defaults) ----", "# " + rows16[-1][8], "gameplay.durability=false"]) + nl
        check(cfg1 == cfg0 + add, "live1: config.properties = the live bytes + exactly the gameplay.durability block:\n%s" % cfg1[len(cfg0):])
        check(sorted(after) == sorted(before), "live1: no file added or removed: %s" % sorted(set(after) ^ set(before)))
        diff = [k for k in before if k != "config.properties" and after.get(k) != before[k]]
        check(not diff, "live1: every other file byte-identical (config-changes.log, trades/...): %s" % diff)
        p0, p1 = props_of(cfg0), props_of(cfg1)
        check(dict((k, v) for k, v in p1.items() if k != "gameplay.durability") == p0 and p1.get("gameplay.durability") == "false",
              "live1: every existing value kept")
        json.dump({k: hashlib.sha1(v).hexdigest() for k, v in after.items()}, open(os.path.join(SCRATCH, "live", "after-live1.json"), "w"))
        print("live1: first start on the live copy: only the gameplay.durability block was appended (%d files checked)" % len(after))
    else:
        snap = json.load(open(os.path.join(SCRATCH, "live", "after-live1.json")))
        now = {k: hashlib.sha1(v).hexdigest() for k, v in after.items()}
        check(now == snap and tree_bytes(home) == before, "live2: the second start changed nothing (%d files)" % len(now))
        print("live2: second start on the live copy: nothing changed (%d files)" % len(now))


# ============================================================================================================== Z. class byte-compare
def compare_jars():
    from cpstrings import read_utf8_constants
    if not os.path.isfile(PREV_JAR):
        check(False, "Z: no %s to compare with" % PREV_JAR)
        return
    za, zb = zipfile.ZipFile(PREV_JAR), zipfile.ZipFile(JAR)
    ca = dict((n, za.read(n)) for n in za.namelist() if n.endswith(".class"))
    cb = dict((n, zb.read(n)) for n in zb.namelist() if n.endswith(".class"))
    short = lambda n: n.rsplit("/", 1)[-1][:-6]
    gone = sorted(short(n) for n in set(ca) - set(cb))
    new = sorted(short(n) for n in set(cb) - set(ca))
    same = sorted(short(n) for n in set(ca) & set(cb) if ca[n] == cb[n])
    changed = sorted(n for n in set(ca) & set(cb) if ca[n] != cb[n])
    check(not gone, "Z: no class removed: %s" % gone)
    check(new == ["EssDur", "EssDurAssetL", "EssDurDeath", "EssDurTick", "EssRepairJob", "EssRepairTask"], "Z: new classes %s" % new)
    # the classes the switch touches on purpose
    expected = {"SkyyEssentialsPlugin", "TCfg", "CfgRows"}
    ver_only = []
    for n in changed:
        sa, sb = set(read_utf8_constants(ca[n])), set(read_utf8_constants(cb[n]))
        da, db = sorted(sa - sb), sorted(sb - sa)
        if short(n) in expected:
            continue
        # anything else may differ only in the version text (0.1.5 -> 0.1.6)
        ok = [x.replace("0.1.5", "0.1.6") for x in da] == db
        ver_only.append(short(n))
        check(ok, "Z: %s differs in more than the version text: %s -> %s" % (short(n), da[:4], db[:4]))
    changed_s = sorted(short(n) for n in changed)
    check(expected <= set(changed_s), "Z: the switch classes changed: %s" % changed_s)
    print("Z. byte-compare 0.1.5 -> 0.1.6: %d identical, %d new %s, changed on purpose %s, version text only %s" % (
        len(same), len(new), new, sorted(expected & set(changed_s)), ver_only))
    return {"same": len(same), "new": new, "changed": changed_s, "ver_only": ver_only}


def main():
    ph = arg("--phase")
    if "--run" in sys.argv:
        jar = arg("--run")
        if ph == "main":
            run_main(jar)
        else:
            run_live(jar, ph)
        print("%s: %d checks passed, %d failed" % (ph, OKS[0], len(FAILS)))
        for f in FAILS:
            print("  FAILED:", f)
        sys.exit(1 if FAILS else 0)
    if not os.path.isfile(JAR):
        sys.exit("no jar at %s - build it first (python SkyyEssentials/build_skyyessentials_%s.py)" % (JAR, VERSION))
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    rc = 0
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--phase", "main", "--dir", SCRATCH], env=env)
    rc |= p.returncode
    # the live copy (read only from UserData: copied into the scratch folder, never written there)
    if os.path.isdir(LIVE):
        dstl = os.path.join(SCRATCH, "live", "mods", "Skyy_SkyyEssentials")
        shutil.copytree(LIVE, dstl)
        for ph in ("live1", "live2"):
            p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--phase", ph, "--dir", SCRATCH], env=env)
            rc |= p.returncode
    else:
        print("FAIL no live folder at %s" % LIVE)
        rc |= 1
    compare_jars()
    print("Z: %d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    rc |= 1 if FAILS else 0
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyEssentials %s bare-JVM check:" % VERSION, "PASS" if rc == 0 else "FAIL")
    sys.exit(rc)


if __name__ == "__main__":
    main()
