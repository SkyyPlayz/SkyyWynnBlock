"""Harness for SkyyAccessories 0.5.18 (CRAFT FROM THE BAG + AUTO-EQUIP + BIGGER LANTERN LIGHT; tools/accessories_0_5_18_patch.py).
Build first: python tools/accessories_0_5_18_patch.py, then

    python SkyyAccessories/test_skyyaccessories_0.5.18.py --build [--dir <empty folder inside tools/dev/scratch/>] [--keep]

--build builds the jar on the COMMITTED kit first: `git show HEAD:tools/skyyui.py` is copied to <dir>/../kit-head/skyyui.py and loaded as
the `skyyui` module, then build_skyyaccessories_0.5.18.py runs in this process (the SkyyTrees 0.3.17 runner) - so the jar stays on kit 1.5
while tools/skyyui.py holds another builder's uncommitted 1.6 edits. Without --build the existing jar is tested.

Phases (fresh child JVMs, tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.5.17 -> 0.5.18: + AccCraft, AccAutoTask, AccAutoPre, AccAutoPost; the page, config, plugin, lantern defaults changed
  CR  THE CRAFT, EXECUTED on the jar's own AccCraft with REAL engine containers (SimpleItemContainer storage 36 / hotbar 9 / backpack 9
      inside a stand-in Inventory, real ItemStacks + Items in a test Item map, REAL CraftingRecipe objects in a test recipe map, the
      engine's CombinedItemContainer / CraftingManager.getInputMaterials doing the counting), the REAL AccStore bag on scratch files, a
      stand-in SkyySacks Void bridge (count / all / take / put / commit with an owe ledger, a paused mode and a short-take fault):
        the list (this tab only, sorted by ItemLevel; the bag item, another tab, a hidden variant, an empty recipe left out); rows
        (have / need from inventory + Void + bag, CAN CRAFT green / NEEDS MATERIALS / LOCKED); a craft from the inventory -> straight into
        the bag (materials exactly gone, journal BEGIN + DONE); DOUBLE CLICK (the second finds nothing, changes nothing); Void materials
        (taken + committed); an upgrade whose lower rarity sits IN THE BAG (taken from the bag, the result in its place); the same one
        already in the bag -> inventory with the reason; FULL inventory + no bag room -> full rollback (Void put back, inventory slots
        identical, "nothing was used"); a Void take that comes up short -> rollback; auto-equip off; switch off; knowledge lock + known;
        profile busy; another profile's key (only that bag); resource-type inputs from the inventory and from the Void; stale / bad
        click data
  AU  AUTO-EQUIP of a bench / /craft craft (AccCraft.autoRun = AccAutoTask's work): a new line -> the bag (chat line); the same / a worse
      one -> stays (chat line with the reason); a better one -> upgraded, the old one back in the inventory; bag full -> stays; a stack
      that was there before (the snapshot) is never touched; switch off -> nothing
  MG  the lantern migration m518Update / migrate0518 (text: CRLF kept, only the five value texts + the marker line differ; custom values
      kept + noted; the marker -> nothing; a file without lantern lines -> marker at the end; a continued entry kept) and end to end on
      scratch files: History copy verified, 5 change-log lines, run once; the chain with migrate055 on a 0.5.4-style file
  CF  config: craft.bag / craft.autoEquip default on (first start writes them), a file without them = on (bytes untouched), false = off
      (summary), the kit edit sets the fields live, the config:def rows in the Accessory Bag section
  D   live     start twice on a scratch COPY of the live NewBetaTest Skyy_SkyyAccessories with 0.5.18's setup order (migrations,
               AccCfg.load, notices, AccSnd.load, the kit): the first start migrates the untouched lantern lines, the second changes nothing
  FX  the fix round (critics): the page markup in AccPage.class (Primary / Secondary tabs, no tertiary tab; the Craft tab's Disabled
      look + the Workbench-only empty line picked by AccDefs.CRAFT; the switched-off answer of the Craft tab), AccPage.infoColor on the
      real result texts (a craft that could not return an accessory is red), the auto-equip cap over storage + hotbar + backpack together,
      the journal without fsync (AccCraft.class never touches java.io.FileDescriptor)
  FX2 fix round 2: an upgrade from Void-only materials with the inventory full and all 60 bag storage slots full -> no auto-equip, full
      rollback, nothing lost (before: the upgraded-out accessory was destroyed, LOST); one bag slot free -> upgraded, the old one kept in
      that slot; acc:lamp:reach = the live lantern.reach (default "10,18,32,64", a live edit follows)
  AA  engine-access audit
NOT driven here: the page click itself (handleDataEvent needs a live UI page - its craft branch only calls AccCraft.clickIndex + craft, both
driven), CraftRecipeEvent firing (needs a live store: fire() answers true without one) and AccAutoPre / AccAutoPost.handle -> seen (needs a
live ArchetypeChunk + world; the task's work, autoRun, is driven). Exit code 1 on any failure.
"""
import os, sys, shutil, subprocess, importlib.util, runpy, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION = "0.5.18"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.17.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "acc0518", "harness")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyAccessories")
PKG = "com.skyy.accessories."
TAB = "Workbench_SkyyAccessories"
EXPECT = {
    "SkyyAccessoriesPlugin": ["~m setup", "~m shutdown"],   # fix round 2: shutdown removes acc:lamp:reach
    "AccLantern": ["~m pubLamp"],                            # fix round 2: + acc:lamp:reach
    "AccDefs": ["+f CRAFT", "+f AUTO", "~<clinit>"],
    "AccCfg": ["+f CRAFT_KEY", "+f AUTO_KEY", "+f M518_KEY", "+f M518_OLD", "+f M518_NEW", "+f M518_MARK", "+f M518_MARK_ID",
               "+f M518_WHO", "+m m518Idx", "+m m518Update", "+m m518Log", "+m migrate0518", "~m load", "~m writeDefaults", "~<clinit>"],
    "AccPage": ["+f mode", "+f craftPage", "+f craftIds", "+m buildCraft", "~m build", "~m handleDataEvent", "~m infoColor"],
    "CfgFile": ["~<clinit>"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = ["AccCraft", "AccAutoTask", "AccAutoPre", "AccAutoPost"]
LAN_IDS = ["Skyy_Talisman_Lantern_%s" % w for w in ("Common", "Uncommon", "Rare", "Epic")]
LAN_DESC_KEYS = sorted(["%sitems.%s.description" % (p_, i) for i in LAN_IDS for p_ in ("", "server.")])

# C: the kit's compare allows only manifest.json among non-class entries - 0.5.18 also changes server.lang (the four Lantern descriptions:
# "about 10 / 18 / 32 / 64 blocks"), checked line by line in CF (lang_diff)
_ChildBase = HK.Child


class _Child(_ChildBase):
    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            want = sorted(list(want) + ["Server/Languages/en-US/server.lang"])
        return _ChildBase.eq(self, got, want, what)


HK.Child = _Child


def lang_diff():
    import zipfile
    def lines(j):
        t = zipfile.ZipFile(j).read("Server/Languages/en-US/server.lang").decode("utf-8")
        return dict(l.split("=", 1) for l in t.split(chr(10)) if "=" in l)
    a, b = lines(OLD_JAR), lines(JAR)
    return sorted(set(a) ^ set(b)), sorted(k for k in a if k in b and a[k] != b[k]), b


def build_on_committed_kit():
    """--build: the committed tools/skyyui.py as `skyyui`, then the build script in this process; returns the kit note"""
    head = subprocess.run(["git", "show", "HEAD:tools/skyyui.py"], cwd=ROOT, capture_output=True, check=True).stdout
    kd = os.path.join(os.path.dirname(SCRATCH), "kit-head")
    assert os.path.realpath(kd).startswith(os.path.realpath(os.path.join(TOOLS, "dev", "scratch")) + os.sep), kd
    os.makedirs(kd, exist_ok=True)
    kf = os.path.join(kd, "skyyui.py")
    open(kf, "wb").write(head)
    sp = importlib.util.spec_from_file_location("skyyui", kf)
    m = importlib.util.module_from_spec(sp)
    sys.modules["skyyui"] = m
    sp.loader.exec_module(m)
    m.SKY_ART_DIR = os.path.join(ROOT, "art", "ui-kit-sky")
    tmp = os.path.join(os.path.dirname(SCRATCH), "tmp")
    os.makedirs(tmp, exist_ok=True)
    os.environ["TEMP"] = os.environ["TMP"] = tmp
    os.environ["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    script = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
    argv0 = sys.argv
    sys.argv = [script]
    try:
        runpy.run_path(script, run_name="__main__")
    finally:
        sys.argv = argv0
    return "built on the committed kit %s (git HEAD, loaded from %s)" % (m.kit_id(), kf)


# ======================================================================================== the shared stand-ins (one per child JVM)
class World(object):
    def __init__(self, scratch, verify=True, extra=()):
        from jpype import JClass, JShort, JImplements, JOverride, JObject, JArray, JString
        self.JClass, self.JShort, self.JObject, self.JArray = JClass, JShort, JObject, JArray
        HK.jvm([B.SERVER_JAR, JAR, B.JAVASSIST] + list(extra), verify=verify)
        Mod = JClass("java.lang.reflect.Modifier")
        uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        us = self.us = uf.get(None)
        jp = JClass("javassist.ClassPool")(True)
        jp.appendClassPath(B.SERVER_JAR)
        CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
        AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
        DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
        fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
        fake.addConstructor(CtC.make("public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
        FakeCls = fake.toClass(AS.class_)
        Item = self.Item = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
        CRR = self.CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")

        def store_for(cls):
            st = us.allocateInstance(FakeCls)
            dam = DAM()
            self.jfield(AS, "assetMap").set(st, dam)
            self.jfield(cls, "ASSET_STORE").set(None, st)
            return self.jfield(DAM, "assetMap").get(dam)
        self.imap = store_for(Item)
        self.rmap = store_for(CRR)
        self.unknown = Item.UNKNOWN
        self.Mod = Mod
        self.IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
        self.SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
        self.MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
        self.BRQ = JClass("com.hypixel.hytale.protocol.BenchRequirement")
        self.BT = JClass("com.hypixel.hytale.protocol.BenchType")
        self.IRT = JClass("com.hypixel.hytale.protocol.ItemResourceType")
        INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
        ICN = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
        CICN = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
        tinv = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyAccTestInv518", jp.get(INVN))
        for f_ in ("s", "h", "b"):
            tinv.addField(CtF.make("public %s %s;" % (ICN, f_), tinv))
        tinv.addConstructor(CtC.make("public SkyyAccTestInv518(%s s, %s h, %s b) { super(); this.s = s; this.h = h; this.b = b; }" % (ICN, ICN, ICN), tinv))
        for src_ in ("public %s getStorage() { return this.s; }" % ICN, "public %s getHotbar() { return this.h; }" % ICN,
                     "public %s getBackpack() { return this.b; }" % ICN,
                     "public %s getCombinedStorageHotbarBackpack() { return new %s(new %s[] { this.s, this.h, this.b }); }" % (CICN, CICN, ICN)):
            tinv.addMethod(CtM.make(src_, tinv))
        self.TInv = JClass(tinv.toClass(JClass(INVN).class_))
        tph = jp.makeClass("com.hypixel.hytale.server.core.io.SkyyAccTestPH518", jp.get("com.hypixel.hytale.server.core.io.PacketHandler"))
        tph.addField(CtF.make("public static java.util.ArrayList OUT;", tph))
        tph.addMethod(CtM.make("public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }", tph))
        tph.addMethod(CtM.make("public void write(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }", tph))
        self.TPH = JClass(tph.toClass(JClass("com.hypixel.hytale.server.core.io.PacketHandler").class_))
        self.TPH.OUT = JClass("java.util.ArrayList")()
        self.PRN = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
        self.PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
        self.PCD = JClass("com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData")
        self.UUID, self.Paths = JClass("java.util.UUID"), JClass("java.nio.file.Paths")
        self.bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
        JClass("java.lang.System").getProperties().put("skyy.bridge", self.bridge)
        self.KEYS = {}
        KEYS = self.KEYS

        @JImplements("java.util.function.Function")
        class KeyFn(object):
            @JOverride
            def apply(self, u):
                return KEYS.get(str(u), str(u))
        self._keyfn = KeyFn()
        self.bridge.put("profile:fn:key", self._keyfn)
        self.seq = 0
        J = lambda n: JClass(PKG + n)
        self.J = J
        self.Acc, self.Defs, self.Craft = J("AccStore"), J("AccDefs"), J("AccCraft")
        os.makedirs(os.path.join(scratch, "bags"), exist_ok=True)
        self.Acc.DIR = self.Paths.get(os.path.join(scratch, "bags"))
        self.LOGF = os.path.join(scratch, "crafts.log")
        self.Craft.LOGF = self.Paths.get(self.LOGF)

    def jfield(self, cls, name):
        c = cls.class_ if hasattr(cls, "class_") else cls
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    def item(self, iid, stack=100, level=0, variant=False, rtypes=()):
        it = self.us.allocateInstance(self.Item.class_)
        for f in self.Item.class_.getDeclaredFields():
            if self.Mod.isStatic(f.getModifiers()):
                continue
            f.setAccessible(True)
            f.set(it, f.get(self.unknown))
        self.jfield(self.Item, "id").set(it, iid)
        self.jfield(self.Item, "maxStack").setInt(it, int(stack))
        self.jfield(self.Item, "itemLevel").setInt(it, int(level))
        self.jfield(self.Item, "variant").setBoolean(it, bool(variant))
        if rtypes:
            arr = self.JArray(self.IRT)(len(rtypes))
            for i, (rid, q) in enumerate(rtypes):
                arr[i] = self.IRT(rid, int(q))
            self.jfield(self.Item, "resourceTypes").set(it, arr)
        self.imap.put(iid, it)
        return it

    def mq(self, iid=None, rt=None, q=1):
        return self.MQ(iid, rt, None, int(q), None)

    def recipe(self, out, ins, tab=TAB, know=False, rid=None):
        arr = self.JArray(self.MQ)(len(ins))
        for i, (a, q) in enumerate(ins):
            arr[i] = self.mq(rt=a[4:], q=q) if a.startswith("res:") else self.mq(a, None, q)
        po = self.mq(out, None, 1)
        outs = self.JArray(self.MQ)(1)
        outs[0] = po
        cats = self.JArray(self.JClass("java.lang.String"))(1)
        cats[0] = tab
        br = self.JArray(self.BRQ)(1)
        br[0] = self.BRQ(self.BT.Crafting, "Workbench", cats, 0, self.JArray(self.JClass("java.lang.String"))(0))
        r = self.CRR(arr, po, outs, 1, br, 0.0, bool(know), 0)
        rid = rid or (out + "_Recipe_Generated_0")
        self.jfield(self.CRR, "id").set(r, rid)
        self.rmap.put(rid, r)
        return rid

    def inv(self, fill=None, put=()):
        cs = dict(s=self.SIC(self.JShort(36)), h=self.SIC(self.JShort(9)), b=self.SIC(self.JShort(9)))
        if fill:
            for sec in "shb":
                for i in range(int(cs[sec].getCapacity())):
                    assert cs[sec].setItemStackForSlot(self.JShort(i), self.IS(fill, 1)).succeeded()
        for sec, sl, iid, q in put:
            assert cs[sec].setItemStackForSlot(self.JShort(sl), self.IS(iid, int(q))).succeeded()
        return self.TInv(cs["s"], cs["h"], cs["b"])

    def player(self, inv, name, known=None):
        p = self.us.allocateInstance(self.PLA.class_)
        self.jfield(self.PLA, "inventory").set(p, inv)
        if known is not None:
            d = self.PCD()
            hs = self.JClass("java.util.HashSet")()
            for k in known:
                hs.add(k)
            for fn in ("knownRecipes", "unmodifiableKnownRecipes"):
                self.jfield(self.PCD, fn).set(d, hs)
            for f in self.jclass_fields(self.PLA):
                if str(f.getType().getName()) == self.PCD.class_.getName():
                    f.setAccessible(True)
                    f.set(p, d)
        pr = self.us.allocateInstance(self.PRN.class_)
        self.seq += 1
        uid = self.UUID.fromString("00000000-0000-0000-0000-%012x" % (0xacc5180 + self.seq))
        self.jfield(self.PRN, "uuid").set(pr, uid)
        self.jfield(self.PRN, "username").set(pr, name)
        self.jfield(self.PRN, "packetHandler").set(pr, self.us.allocateInstance(self.TPH.class_))
        self.bridge.put("profile:epoch:%s" % uid, self.JObject(1, "java.lang.Long"))   # a loaded profile (AccStore.moveBlock)
        return p, pr, uid

    def jclass_fields(self, cls):
        c = cls.class_
        out = []
        while c is not None:
            out.extend(list(c.getDeclaredFields()))
            c = c.getSuperclass()
        return out

    def count(self, inv, iid):
        n = 0
        for c in (inv.getStorage(), inv.getHotbar(), inv.getBackpack()):
            for i in range(int(c.getCapacity())):
                it = c.getItemStack(self.JShort(i))
                if it is not None and not it.isEmpty() and str(it.getItemId()) == iid:
                    n += int(it.getQuantity())
        return n

    def slots(self, inv):
        """every slot as (section, index, id, qty) - to compare two moments exactly"""
        out = []
        for tag, c in (("s", inv.getStorage()), ("h", inv.getHotbar()), ("b", inv.getBackpack())):
            for i in range(int(c.getCapacity())):
                it = c.getItemStack(self.JShort(i))
                out.append((tag, i, None if it is None or it.isEmpty() else str(it.getItemId()), 0 if it is None or it.isEmpty() else int(it.getQuantity())))
        return out

    def bag(self, uid, key=None):
        s = self.Acc.slotsK(uid, key or str(uid))
        return [str(x) if x is not None else None for x in s]

    def chats(self):
        return int(self.TPH.OUT.size())


ITEMS = [("Skyy_Accessory_Workbench_T1", 1, 1), ("Skyy_Talisman_Lantern_Common", 1, 2), ("Skyy_Talisman_Speed_Common", 1, 4),
         ("Skyy_Accessory_Bag", 1, 18), ("Skyy_Talisman_Speed_Uncommon", 1, 21), ("Skyy_Accessory_Farmingbench_T1", 1, 15),
         ("Skyy_Accessory_Farmingbench_T2", 1, 25), ("Skyy_Talisman_Vitality_Common", 1, 6), ("Skyy_Talisman_Intelligence_Common", 1, 3),
         ("Bench_WorkBench", 100, 0), ("Ingredient_Bar_Copper", 100, 0), ("Ingredient_Crystal_Cyan", 100, 0), ("Ingredient_Feathers_Light", 100, 0),
         ("Furniture_Crude_Torch", 100, 0), ("Ingredient_Fabric_Scrap_Cotton", 100, 0), ("Ingredient_Stick", 100, 0), ("Ingredient_Crystal_Red", 100, 0)]
SPEED_IN = [("Ingredient_Crystal_Cyan", 2), ("Ingredient_Feathers_Light", 3), ("Ingredient_Bar_Copper", 2)]


def setup_recipes(W):
    for iid, st, lv in ITEMS:
        W.item(iid, st, lv)
    W.item("Skyy_Talisman_Speed_Ring", 1, 0, variant=True)                               # an old id (hidden variant)
    W.item("Wood_Fir_Trunk", 100, 0, rtypes=[("Wood_Softwood_Trunk", 1), ("Wood_Trunk", 1)])   # a resource-type input
    W.item("Wood_Oak_Trunk", 100, 0, rtypes=[("Wood_Hardwood_Trunk", 1), ("Wood_Trunk", 1)])
    ids = {}
    ids["wb"] = W.recipe("Skyy_Accessory_Workbench_T1", [("Bench_WorkBench", 1), ("Ingredient_Bar_Copper", 4)])
    ids["lan"] = W.recipe("Skyy_Talisman_Lantern_Common", [("Furniture_Crude_Torch", 4), ("Ingredient_Bar_Copper", 2)], know=True)
    ids["spd"] = W.recipe("Skyy_Talisman_Speed_Common", SPEED_IN)
    ids["spd2"] = W.recipe("Skyy_Talisman_Speed_Uncommon", [("Skyy_Talisman_Speed_Common", 1), ("Ingredient_Bar_Copper", 4)])
    ids["farm2"] = W.recipe("Skyy_Accessory_Farmingbench_T2", [("Skyy_Accessory_Farmingbench_T1", 1), ("res:Wood_Softwood_Trunk", 5)])
    ids["bag"] = W.recipe("Skyy_Accessory_Bag", [("res:Wood_Trunk", 4), ("Ingredient_Fabric_Scrap_Cotton", 4)])
    ids["other"] = W.recipe("Skyy_Talisman_Vitality_Common", [("Ingredient_Crystal_Red", 2)], tab="Workbench_Crafting")
    ids["variant"] = W.recipe("Skyy_Talisman_Speed_Ring", [("Ingredient_Bar_Copper", 1)])
    ids["empty"] = W.recipe("Skyy_Talisman_Intelligence_Common", [])
    return ids


def void_bridge(W, VOID):
    """the stand-in SkyySacks Void: VOID = {"n": {id: count}, "owe": {id: n}, "paused": False, "short": 0, "calls": []}"""
    from jpype import JImplements, JOverride, JObject, JClass

    def L(v):
        return JObject(int(v), "java.lang.Long")

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, mode):
            self.mode = mode

        @JOverride
        def apply(self, a):
            if self.mode == "all":
                m = JClass("java.util.HashMap")()
                for k, v in VOID["n"].items():
                    if v > 0:
                        m.put(k, L(v))
                return m
            iid = str(a[1])
            if self.mode == "count":
                return L(-1 if VOID["paused"] else VOID["n"].get(iid, 0))
            n = int(a[2])
            VOID["calls"].append((self.mode, iid, n))
            if self.mode == "take":
                t = min(n, VOID["n"].get(iid, 0))
                if VOID["short"] and t > 0:
                    t -= VOID["short"]
                VOID["n"][iid] = VOID["n"].get(iid, 0) - t
                VOID["owe"][iid] = VOID["owe"].get(iid, 0) + t
                return L(t)
            if self.mode == "put":
                t = min(n, VOID["owe"].get(iid, 0))
                VOID["owe"][iid] -= t
                VOID["n"][iid] = VOID["n"].get(iid, 0) + t
                return L(t)
            if self.mode == "commit":
                t = min(n, VOID["owe"].get(iid, 0))
                VOID["owe"][iid] -= t
                return L(t)
            return L(0)
    fns = [Fn(m) for m in ("count", "take", "put", "commit", "all")]
    for m, f in zip(("count", "take", "put", "commit", "all"), fns):
        W.bridge.put("sacks:fn:" + m, f)
    return fns


def run_craft(out, jar, scratch, _home):
    K = HK.Child(out)
    W = World(os.path.join(scratch, "cr"))
    ids = setup_recipes(W)
    C, Acc, Defs, JShort = W.Craft, W.Acc, W.Defs, W.JShort
    VOID = {"n": {}, "owe": {}, "paused": False, "short": 0, "calls": []}
    _keep = void_bridge(W, VOID)

    def journal():
        return open(W.LOGF, encoding="utf8").read() if os.path.exists(W.LOGF) else ""

    def craft(p, pr, u, rid, k=None):
        return str(C.craft(pr, None, None, p, u, k or str(u), rid))

    # ===== CR1 the list
    rs = [str(C.outId(r)) for r in C.recipes()]
    K.eq(rs, ["Skyy_Accessory_Workbench_T1", "Skyy_Talisman_Lantern_Common", "Skyy_Talisman_Speed_Common", "Skyy_Talisman_Speed_Uncommon",
              "Skyy_Accessory_Farmingbench_T2"], "CR1 the list: this tab only, ItemLevel order; no Accessory Bag, other tab, hidden variant or empty recipe")
    Sys = W.JClass("java.lang.System")
    K.check(Sys.identityHashCode(C.recipes()) == Sys.identityHashCode(C.recipes()), "CR1 ... built once (same object while the recipe table keeps its size)")
    # ===== CR2 rows
    inv = W.inv(put=[("s", 0, "Ingredient_Crystal_Cyan", 2), ("s", 1, "Ingredient_Feathers_Light", 3), ("h", 0, "Ingredient_Bar_Copper", 1)])
    p, pr, U = W.player(inv, "Alice")
    spd = W.CRR.getAssetMap().getAsset(ids["spd"])
    row = [str(x) for x in C.row(U, str(U), p, spd)]
    K.eq((row[0], row[2], row[5]), ("Skyy_Talisman_Speed_Common", "NORMAL - NEEDS MATERIALS", str(C.GREY)), "CR2 row: 1 of 2 Copper -> NEEDS MATERIALS, grey")
    K.check("1/2" in row[4] and "2/2" in row[4] and "3/3" in row[4], "CR2 ... have/need per ingredient: " + row[4])
    VOID["n"]["Ingredient_Bar_Copper"] = 5
    row = [str(x) for x in C.row(U, str(U), p, spd)]
    K.eq((row[2], row[5]), ("NORMAL - CAN CRAFT", str(C.GREEN)), "CR2 + 5 Copper in the Void -> CAN CRAFT, green")
    K.check("2/2" in row[4] and "1/2" not in row[4] and "3/2" not in row[4], "CR2 ... the Void counts; enough shows need/need: " + row[4])
    VOID["paused"] = True
    row = [str(x) for x in C.row(U, str(U), p, spd)]
    K.eq(row[2], "NORMAL - NEEDS MATERIALS", "CR2 the Void paused -> counts 0 (NEEDS MATERIALS)")
    VOID["paused"] = False
    lan = W.CRR.getAssetMap().getAsset(ids["lan"])
    K.eq([str(x) for x in C.row(U, str(U), p, lan)][2], "NORMAL - LOCKED", "CR2 a knowledge recipe not known -> LOCKED")
    # ===== CR3 craft: inventory + Void -> straight into the bag
    before = W.slots(inv)
    r = craft(p, pr, U, ids["spd"])
    K.eq(r, "crafted Normal Speed Accessory - it went straight into your bag", "CR3 craft -> the bag: " + r)
    K.eq((W.count(inv, "Ingredient_Crystal_Cyan"), W.count(inv, "Ingredient_Feathers_Light"), W.count(inv, "Ingredient_Bar_Copper")), (0, 0, 0),
         "CR3 ... the inventory materials are gone (2 Cyan, 3 Feathers, 1 Copper)")
    K.eq((VOID["n"]["Ingredient_Bar_Copper"], VOID["owe"].get("Ingredient_Bar_Copper")), (4, 0), "CR3 ... 1 Copper from the Void, committed")
    K.eq(W.bag(U)[0], "Skyy_Talisman_Speed_Common", "CR3 ... in bag slot 0")
    K.eq(W.count(inv, "Skyy_Talisman_Speed_Common"), 0, "CR3 ... not in the inventory")
    bf = open(os.path.join(scratch, "cr", "bags", "%s.properties" % U), encoding="latin-1").read()
    K.check("slot0=Skyy_Talisman_Speed_Common" in bf, "CR3 ... the bag file is saved at once")
    j = journal()
    K.check("BEGIN Alice" in j and "DONE Alice" in j and j.index("BEGIN") < j.index("DONE"), "CR3 ... journal BEGIN then DONE")
    K.eq(int(C.CRAFTED), 1, "CR3 ... counted")
    # ===== CR4 double click
    s0, b0, v0 = W.slots(inv), W.bag(U), dict(VOID["n"])
    r = craft(p, pr, U, ids["spd"])
    K.eq(r, "not enough materials for Normal Speed Accessory - nothing was used", "CR4 DOUBLE CLICK: the second click finds the materials gone")
    K.check(W.slots(inv) == s0 and W.bag(U) == b0 and VOID["n"] == v0, "CR4 ... nothing changed anywhere")
    # ===== CR5 the same one already in the bag -> the inventory, with the reason
    for sec, sl, iid, q in [("s", 3, "Ingredient_Crystal_Cyan", 2), ("s", 4, "Ingredient_Feathers_Light", 3), ("s", 5, "Ingredient_Bar_Copper", 2)]:
        inv.getStorage().setItemStackForSlot(JShort(sl), W.IS(iid, q))
    r = craft(p, pr, U, ids["spd"])
    K.eq(r, "crafted Normal Speed Accessory - it is in your inventory (your bag already has the same Speed Accessory)", "CR5 same one equipped -> inventory: " + r)
    K.eq((W.count(inv, "Skyy_Talisman_Speed_Common"), W.bag(U).count("Skyy_Talisman_Speed_Common")), (1, 1), "CR5 ... one in the inventory, one in the bag")
    # ===== CR6 upgrade from the inventory's lower one: the result replaces the bag's lower one, which comes back
    inv.getStorage().setItemStackForSlot(JShort(6), W.IS("Ingredient_Bar_Copper", 4))
    r = craft(p, pr, U, ids["spd2"])
    K.check(r.startswith("crafted Unique Speed Accessory - upgraded in your bag") and "is back in your inventory" in r, "CR6 upgrade in place: " + r)
    K.eq((W.bag(U)[0], W.count(inv, "Skyy_Talisman_Speed_Common"), W.count(inv, "Skyy_Talisman_Speed_Uncommon")),
         ("Skyy_Talisman_Speed_Uncommon", 1, 0), "CR6 ... the inventory's Normal was used, the bag's Normal came back to the inventory")
    # ===== CR7 the lower rarity IN THE BAG is an ingredient (inventory has none)
    inv7 = W.inv(put=[("s", 0, "Ingredient_Bar_Copper", 4)])
    p7, pr7, U7 = W.player(inv7, "Bea")
    Acc.equipK(U7, str(U7), "Skyy_Accessory_Workbench_T1")
    Acc.equipK(U7, str(U7), "Skyy_Talisman_Speed_Common")
    row = [str(x) for x in C.row(U7, str(U7), p7, W.CRR.getAssetMap().getAsset(ids["spd2"]))]
    K.check(row[2] == "UNIQUE - CAN CRAFT" and "1/1" in row[4], "CR7 row: the bag's Normal Speed counts: " + row[4])
    r = craft(p7, pr7, U7, ids["spd2"])
    K.eq(r, "crafted Unique Speed Accessory - it went straight into your bag", "CR7 craft with the bag's lower one: " + r)
    K.eq(W.bag(U7)[:3], ["Skyy_Accessory_Workbench_T1", "Skyy_Talisman_Speed_Uncommon", None], "CR7 ... taken from the bag, the result in its slot")
    K.eq((W.count(inv7, "Skyy_Talisman_Speed_Common"), W.count(inv7, "Ingredient_Bar_Copper")), (0, 0), "CR7 ... no Normal anywhere, Copper used")
    # ===== CR8 FULL inventory + the bag refuses -> FULL ROLLBACK
    inv8 = W.inv(fill="Ingredient_Stick")
    p8, pr8, U8 = W.player(inv8, "Cid")
    Acc.equipK(U8, str(U8), "Skyy_Talisman_Speed_Uncommon")
    VOID["n"].update({"Ingredient_Crystal_Cyan": 2, "Ingredient_Feathers_Light": 3, "Ingredient_Bar_Copper": 2})
    s0, v0 = W.slots(inv8), dict(VOID["n"])
    r = craft(p8, pr8, U8, ids["spd"])
    K.eq(r, "no room for Normal Speed Accessory in your inventory or bag - nothing was used", "CR8 full inventory, a better one equipped: " + r)
    K.check(W.slots(inv8) == s0 and VOID["n"] == v0 and all(v == 0 for v in VOID["owe"].values()), "CR8 ... the Void put back, the inventory identical")
    K.check("ROLLBACK Cid" in journal(), "CR8 ... journal ROLLBACK")
    # ===== CR9 a Void take that comes up short -> rollback of everything taken before
    inv9 = W.inv(put=[("s", 0, "Ingredient_Crystal_Cyan", 2)])
    p9, pr9, U9 = W.player(inv9, "Dee")
    VOID["short"] = 1
    s0 = W.slots(inv9)
    r = craft(p9, pr9, U9, ids["spd"])
    VOID["short"] = 0
    K.check(r.startswith("the Void gave") and r.endswith("- nothing was used"), "CR9 short Void take: " + r)
    K.check(W.slots(inv9) == s0 and W.bag(U9) == [None] * 60 and VOID["n"] == v0 and all(v == 0 for v in VOID["owe"].values()),
            "CR9 ... the inventory slot restored, every Void item back, nothing in the bag")
    # ===== CR10 auto-equip off -> the inventory
    Defs.AUTO = False
    r = craft(p9, pr9, U9, ids["spd"])
    Defs.AUTO = True
    K.eq(r, "crafted Normal Speed Accessory - it is in your inventory", "CR10 auto-equip off: the inventory")
    K.eq((W.count(inv9, "Skyy_Talisman_Speed_Common"), W.bag(U9).count("Skyy_Talisman_Speed_Common")), (1, 0), "CR10 ... not in the bag")
    # ===== CR11 switch off / CR12 profile busy / unloaded / CR13 knowledge
    inv11 = W.inv(put=[("s", 0, "Furniture_Crude_Torch", 4), ("s", 1, "Ingredient_Bar_Copper", 2)])
    p11, pr11, U11 = W.player(inv11, "Eve")
    s0 = W.slots(inv11)
    Defs.CRAFT = False
    K.eq(craft(p11, pr11, U11, ids["lan"]), "crafting from the bag is switched off on this server", "CR11 the switch off")
    Defs.CRAFT = True
    W.bridge.put("profile:busy:%s" % U11, W.JObject(True, "java.lang.Boolean"))
    K.eq(craft(p11, pr11, U11, ids["lan"]), "your profile is still loading - try again in a moment", "CR12 profile:busy -> nothing")
    W.bridge.remove("profile:busy:%s" % U11)
    K.eq(craft(p11, pr11, U11, ids["lan"]), "Normal Lantern Accessory is locked - collect Tree Sap to unlock it (Collections)", "CR13 knowledge recipe not known: locked")
    K.check(W.slots(inv11) == s0, "CR11-13 ... nothing used")
    p11b, pr11b, U11b = W.player(inv11, "Eve2", known=["Skyy_Talisman_Lantern_Common"])
    K.eq(craft(p11b, pr11b, U11b, ids["lan"]), "crafted Normal Lantern Accessory - it went straight into your bag", "CR13 ... known: crafted")
    K.eq(craft(p11, pr11, U11, "No_Such_Recipe"), "that recipe is not on the list any more - nothing was used", "CR14 an unknown recipe id")
    K.eq(craft(p11, pr11, U11, ids["other"]), "that recipe is not on the list any more - nothing was used", "CR14 another tab's recipe id")
    # ===== CR15 another profile's key: only that bag
    inv15 = W.inv(put=[("s", 0, "Bench_WorkBench", 1), ("s", 1, "Ingredient_Bar_Copper", 4)])
    p15, pr15, U15 = W.player(inv15, "Fay")
    k2 = str(U15) + "-p2"
    r = craft(p15, pr15, U15, ids["wb"], k=k2)
    K.check(r.endswith("it went straight into your bag") and W.bag(U15, k2)[0] == "Skyy_Accessory_Workbench_T1" and W.bag(U15)[0] is None,
            "CR15 the click's profile key: the result goes into THAT profile's bag only")
    # ===== CR16 resource-type inputs: inventory, then the Void
    inv16 = W.inv(put=[("s", 0, "Skyy_Accessory_Farmingbench_T1", 1), ("s", 1, "Wood_Fir_Trunk", 3), ("s", 2, "Wood_Oak_Trunk", 9)])
    p16, pr16, U16 = W.player(inv16, "Gus")
    VOID["n"]["Wood_Fir_Trunk"] = 10
    row = [str(x) for x in C.row(U16, str(U16), p16, W.CRR.getAssetMap().getAsset(ids["farm2"]))]
    K.check(row[2] == "UNIQUE - CAN CRAFT" and "5/5" in row[4], "CR16 row: softwood logs 3 inventory + Void (oak does not count): " + row[4])
    r = craft(p16, pr16, U16, ids["farm2"])
    K.eq(r, "crafted Farming Bench II - it went straight into your bag", "CR16 resource-type craft (no I18n here: the bag name): " + r)
    K.eq((W.count(inv16, "Wood_Fir_Trunk"), W.count(inv16, "Wood_Oak_Trunk"), VOID["n"]["Wood_Fir_Trunk"]), (0, 9, 8),
         "CR16 ... 3 fir logs from the inventory first, 2 from the Void, the oak untouched")
    # ===== CR17 click data
    K.eq([int(C.clickIndex(d)) for d in ('{"a":"cr:12"}', '{"a":"cr:0"}', '{"a":"cr:"}', '{"a":"un:3"}', '{"a":"cr:1x"}', None)],
         [12, 0, -1, -1, -1, -1], "CR17 clickIndex: cr:<n> only")
    # ===== FX2 (fix round 2) an upgrade whose materials free no slot: inventory full AND every bag storage slot (AccStore.CAP) full
    rv = W.recipe("Skyy_Talisman_Speed_Uncommon", [("Ingredient_Bar_Copper", 3)], rid="Skyy_Talisman_Speed_Uncommon_Recipe_VoidOnly")
    inv18 = W.inv(fill="Ingredient_Stick")
    p18, pr18, U18 = W.player(inv18, "Hob")
    cap = int(Acc.CAP)
    Acc.putK(U18, str(U18), 0, "Skyy_Talisman_Speed_Common")
    for i in range(1, cap):
        Acc.putK(U18, str(U18), i, "Skyy_Accessory_Workbench_T1")
    VOID["n"]["Ingredient_Bar_Copper"] = 10
    s0, b0, v0 = W.slots(inv18), W.bag(U18), dict(VOID["n"])
    K.check(None not in b0 and len(b0) == cap, "FX2 setup: all %d bag storage slots full, inventory full" % cap)
    r = craft(p18, pr18, U18, rv)
    K.eq(r, "no room for Unique Speed Accessory in your inventory or bag - nothing was used",
         "FX2 inventory + bag full, Void-only upgrade: no auto-equip, rolled back (before the fix: the bag's Normal was destroyed): " + r)
    K.check(W.slots(inv18) == s0 and W.bag(U18) == b0 and VOID["n"] == v0 and all(v == 0 for v in VOID["owe"].values()),
            "FX2 ... the inventory, the bag and the Void exactly as before")
    K.check(not bool(C.swapSafe(p18, U18, str(U18), "Skyy_Talisman_Speed_Uncommon")) and bool(C.swapSafe(p18, U18, str(U18), "Skyy_Talisman_Lantern_Common")),
            "FX2 swapSafe: false only when an upgrade would displace one with nowhere to go (a line not in the bag displaces nothing)")
    Acc.unequipK(U18, str(U18), cap - 1)
    r = craft(p18, pr18, U18, rv)
    K.eq(r, "crafted Unique Speed Accessory - upgraded in your bag - Normal Speed Accessory was kept in a free bag slot (inventory full)",
         "FX2 one bag slot free: upgraded, the old one kept in that slot: " + r)
    K.eq((W.bag(U18)[0], W.bag(U18)[cap - 1], VOID["n"]["Ingredient_Bar_Copper"]), ("Skyy_Talisman_Speed_Uncommon", "Skyy_Talisman_Speed_Common", 7),
         "FX2 ... slot 0 the Unique, the last slot the Normal, 3 Copper from the Void")
    # acc:lamp:reach (SkyyGear's helmet tooltip): the live lantern.reach
    Lan = W.JClass(PKG + "AccLantern")
    W.bridge.remove("acc:lamp:reach")
    Lan.pubLamp()
    K.eq(str(W.bridge.get("acc:lamp:reach")), "10,18,32,64", "FX2 acc:lamp:reach = the 0.5.18 defaults (Normal..Legendary)")
    r4 = int(Defs.LAN_REACH4)
    Defs.LAN_REACH4 = 40
    Lan.pubLamp()
    K.eq(str(W.bridge.get("acc:lamp:reach")), "10,18,32,40", "FX2 ... a live Server Setup edit follows on the next tick")
    Defs.LAN_REACH4 = r4
    Lan.pubLamp()
    K.check("LOST" not in journal(), "CR nothing was ever lost (journal)")
    # ===== FX the fix round
    Page = W.JClass(PKG + "AccPage")
    ok, no = str(Page.infoColor("equipped Normal Speed Accessory")), str(Page.infoColor("that click failed - tell an admin (server log)"))
    K.check(ok != no, "FX infoColor: green and red differ")
    K.eq([str(Page.infoColor(t)) for t in (
        "crafted Workbench Accessory I - it went straight into your bag",
        "crafted Unique Speed Accessory - upgraded in your bag - Normal Speed Accessory is back in your inventory",
        "crafted Unique Speed Accessory - upgraded in your bag - Normal Speed Accessory could not be returned - reported to the server log",
        "crafted Normal Speed Accessory - it is in your inventory (the same one of its line is already in your bag)",
        "Crafting from the bag is switched off on this server - craft accessories at a Workbench.",
        "not enough materials for Normal Speed Accessory - nothing was used")],
        [ok, ok, no, ok, no, no], "FX infoColor: a crafted line is green unless an accessory could not be returned (red); refusals red")
    z = zipfile.ZipFile(JAR)
    pc = z.read("com/skyy/accessories/AccPage.class")
    cc = z.read("com/skyy/accessories/AccCraft.class")
    K.check(b"java/io/FileDescriptor" not in cc and b"getFD" not in cc, "FX the craft journal no longer fsyncs (no FileDescriptor in AccCraft)")
    K.check(b"BEGIN " in journal().encode("utf8") and b"DONE " in journal().encode("utf8"), "FX ... and still writes BEGIN / DONE")
    K.check(b"Tertiary" not in pc, "FX no tertiary tab style left in the page (the locked vanilla tab rule)")
    K.check(pc.count(b"#SkyyAccTabCraft") >= 3, "FX the Craft tab markup: Bag view live + Disabled variant, Craft view (%d)" % pc.count(b"#SkyyAccTabCraft"))
    K.check(b"None - craft one in the Craft tab or at a Workbench" in pc and b"None - craft accessories at a Workbench" in pc,
            "FX the empty inventory line: both texts (picked by AccDefs.CRAFT at runtime)")
    K.check(b"Crafting from the bag is switched off on this server - craft accessories at a Workbench." in pc,
            "FX the Craft tab answers 'switched off' when crafting from the bag is off")
    z.close()
    K.save()


def run_auto(out, jar, scratch, _home):
    K = HK.Child(out)
    W = World(os.path.join(scratch, "au"))
    setup_recipes(W)
    C, Acc, Defs, JShort = W.Craft, W.Acc, W.Defs, W.JShort
    IHM = W.JClass("java.util.IdentityHashMap")

    def snap(inv, iid):
        return C.snap(inv, iid)

    # AU1 a new line -> the bag
    inv = W.inv(put=[("s", 0, "Skyy_Talisman_Speed_Common", 1)])
    p, pr, U = W.player(inv, "Hal")
    sn = snap(inv, "Skyy_Talisman_Speed_Common")
    inv.getStorage().setItemStackForSlot(JShort(5), W.IS("Skyy_Talisman_Speed_Common", 1))   # the crafted one arrives
    c0 = W.chats()
    r = str(C.autoRun(pr, p, "Skyy_Talisman_Speed_Common", sn, 1))
    K.eq(r, "1 in, 0 kept", "AU1 a new line: into the bag")
    K.eq((W.bag(U)[0], W.count(inv, "Skyy_Talisman_Speed_Common"), W.chats() - c0), ("Skyy_Talisman_Speed_Common", 1, 1),
         "AU1 ... the NEW stack went in, the one that was there before (snapshot) stayed; one chat line")
    K.check(inv.getStorage().getItemStack(JShort(0)) is not None and inv.getStorage().getItemStack(JShort(5)) is None, "AU1 ... exactly slot 5 left")
    # AU2 the same again -> stays, with the reason
    sn = snap(inv, "Skyy_Talisman_Speed_Common")
    inv.getStorage().setItemStackForSlot(JShort(6), W.IS("Skyy_Talisman_Speed_Common", 1))
    c0 = W.chats()
    K.eq(str(C.autoRun(pr, p, "Skyy_Talisman_Speed_Common", sn, 1)), "0 in, 1 kept", "AU2 the same one already in the bag: stays")
    K.eq((W.count(inv, "Skyy_Talisman_Speed_Common"), W.chats() - c0), (2, 1), "AU2 ... in the inventory, one chat line")
    # AU3 a better one -> upgraded, the old one back
    sn = snap(inv, "Skyy_Talisman_Speed_Uncommon")
    inv.getHotbar().setItemStackForSlot(JShort(2), W.IS("Skyy_Talisman_Speed_Uncommon", 1))
    K.eq(str(C.autoRun(pr, p, "Skyy_Talisman_Speed_Uncommon", sn, 1)), "1 in, 0 kept", "AU3 a better one: upgraded")
    K.eq((W.bag(U)[0], W.count(inv, "Skyy_Talisman_Speed_Common"), W.count(inv, "Skyy_Talisman_Speed_Uncommon")),
         ("Skyy_Talisman_Speed_Uncommon", 3, 0), "AU3 ... in place in the bag, the Normal back in the inventory")
    # AU4 a worse one -> stays
    sn = snap(inv, "Skyy_Talisman_Speed_Common")
    inv.getStorage().setItemStackForSlot(JShort(9), W.IS("Skyy_Talisman_Speed_Common", 1))
    K.eq(str(C.autoRun(pr, p, "Skyy_Talisman_Speed_Common", sn, 1)), "0 in, 1 kept", "AU4 a worse one: stays")
    # AU5 bag full (server limit 1, another line in it) -> stays
    old = int(Acc.SLOTS)
    Acc.SLOTS = 1
    sn = snap(inv, "Skyy_Accessory_Workbench_T1")
    inv.getStorage().setItemStackForSlot(JShort(10), W.IS("Skyy_Accessory_Workbench_T1", 1))
    K.eq(str(C.autoRun(pr, p, "Skyy_Accessory_Workbench_T1", sn, 1)), "0 in, 1 kept", "AU5 no free slot: stays")
    K.eq(str(C.why(U, str(U), "Skyy_Accessory_Workbench_T1")), "your Accessory Bag has no free slot", "AU5 ... the reason")
    Acc.SLOTS = old
    # AU6 several crafted at once: capped by the crafted count
    inv6 = W.inv()
    p6, pr6, U6 = W.player(inv6, "Ida")
    sn = snap(inv6, "Skyy_Talisman_Lantern_Common")
    for sl in range(3):
        inv6.getStorage().setItemStackForSlot(JShort(sl), W.IS("Skyy_Talisman_Lantern_Common", 1))
    K.eq(str(C.autoRun(pr6, p6, "Skyy_Talisman_Lantern_Common", sn, 3)), "1 in, 2 kept", "AU6 three crafted: one into the bag, two stay")
    sn = snap(inv6, "Skyy_Talisman_Lantern_Common")
    K.eq(str(C.autoRun(pr6, p6, "Skyy_Talisman_Lantern_Common", sn, 3)), "none", "AU6 nothing new since the snapshot: nothing at all")
    # AU7 switch off
    Defs.AUTO = False
    K.eq(str(C.autoRun(pr6, p6, "Skyy_Talisman_Lantern_Common", IHM(), 3)), "off", "AU7 the switch off: nothing")
    Defs.AUTO = True
    # AU8 profile busy -> stays (no move while a profile switch settles)
    W.bridge.put("profile:busy:%s" % U6, W.JObject(True, "java.lang.Boolean"))
    Acc.unequipK(U6, str(U6), 0)
    K.eq(str(C.autoRun(pr6, p6, "Skyy_Talisman_Lantern_Common", IHM(), 1)), "0 in, 1 kept", "AU8 profile busy: stays")
    W.bridge.remove("profile:busy:%s" % U6)
    # AU9 (fix round) one crafted, but new stacks in storage AND hotbar AND backpack (a profile switch between snapshot and task): ONE handled
    inv9 = W.inv()
    p9, pr9, U9 = W.player(inv9, "Jon")
    sn = snap(inv9, "Skyy_Talisman_Speed_Common")
    inv9.getStorage().setItemStackForSlot(JShort(0), W.IS("Skyy_Talisman_Speed_Common", 1))
    inv9.getHotbar().setItemStackForSlot(JShort(0), W.IS("Skyy_Talisman_Speed_Common", 1))
    inv9.getBackpack().setItemStackForSlot(JShort(0), W.IS("Skyy_Talisman_Speed_Common", 1))
    K.eq(str(C.autoRun(pr9, p9, "Skyy_Talisman_Speed_Common", sn, 1)), "1 in, 0 kept", "AU9 cap 1 over three containers: exactly one handled (0.5.18 before the fix: 1 in, 2 kept)")
    K.eq((W.bag(U9)[0], W.count(inv9, "Skyy_Talisman_Speed_Common")), ("Skyy_Talisman_Speed_Common", 2), "AU9 ... one in the bag, two untouched")
    K.eq(int(C.AUTOED), 4, "AU AUTOED counts the ones put in")
    K.check("AUTO Hal" in open(W.LOGF, encoding="utf8").read(), "AU ... journal AUTO lines")
    K.save()


# 0.5.17's default lantern part (the text a live file holds) - CRLF like the live file
OLD_LAN = ("# Lantern Accessory (0.5.5): ...\r\n# SkyyAccessories 0.5.5 Lantern defaults (Skyy 2026-10-04, smooth the edges): the hidden lights go at most 64 blocks up "
           "(0.5.4: 128) and are softer.\r\nline.Lantern=true\r\nlantern.glow.Normal=11\r\nlantern.glow.Unique=11\r\nlantern.glow.Rare=11\r\n"
           "lantern.glow.Legendary=11\r\nlantern.reach.Normal=6\r\nlantern.reach.Unique=12\r\nlantern.reach.Rare=24\r\nlantern.reach.Legendary=48\r\n"
           "lantern.height=64\r\nlantern.edge=96\r\nlantern.lights=7\r\nlantern.shareReach=false\r\n")


def run_mig(out, jar, scratch, _home):
    K = HK.Child(out)
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg = JClass(PKG + "AccCfg")
    Paths = JClass("java.nio.file.Paths")
    mark = str(Cfg.M518_MARK)
    t = "slots=18\r\n" + OLD_LAN + "starter.bag=true\r\n"
    r = Cfg.m518Update(t)
    nt = str(r[0])
    K.check("\r\n" + mark + "\r\nlantern.reach.Normal=10\r\n" in nt, "MG1 the marker right above the first reach line, CRLF kept")
    want = t.replace("reach.Normal=6", "reach.Normal=10").replace("reach.Unique=12", "reach.Unique=18").replace("reach.Rare=24", "reach.Rare=32") \
        .replace("reach.Legendary=48", "reach.Legendary=64").replace("lantern.lights=7", "lantern.lights=8").replace(
        "lantern.glow.Legendary=11\r\n", "lantern.glow.Legendary=11\r\n" + mark + "\r\n")
    K.eq(nt, want, "MG1 only the five value texts + the marker line differ")
    K.eq(str(r[1]), "lantern.reach.Normal 6 -> 10, lantern.reach.Unique 12 -> 18, lantern.reach.Rare 24 -> 32, lantern.reach.Legendary 48 -> 64, lantern.lights 7 -> 8",
         "MG1 the change text")
    K.eq(len(r[3]), 15, "MG1 five change rows (key, old, new)")
    K.check(Cfg.m518Update(nt) is None, "MG2 the marker present -> nothing (run once)")
    t2 = t.replace("lantern.reach.Legendary=48", "lantern.reach.Legendary=40").replace("lantern.lights=7", "lantern.lights = 7")
    r2 = Cfg.m518Update(t2)
    K.check("lantern.reach.Legendary=40" in str(r2[0]) and "lantern.lights = 8" in str(r2[0]), "MG3 a hand-edited value kept; 'key = value' spacing kept")
    K.eq([str(x) for x in r2[2]], ["lantern.reach.Legendary=40 kept (custom) - the 0.5.18 default is 64"], "MG3 ... the kept value noted")
    t3 = "slots=18\nstarter.bag=true\n"
    K.eq(str(Cfg.m518Update(t3)[0]), t3 + mark + "\n", "MG4 no lantern lines -> the marker at the end (the file's LF)")
    t4 = t.replace("lantern.reach.Rare=24\r\n", "lantern.reach.Rare=2\\\r\n  4\r\n")
    r4 = Cfg.m518Update(t4)
    K.check("lantern.reach.Rare=2\\\r\n  4\r\n" in str(r4[0]) and any("lantern.reach.Rare" in str(x) for x in r4[2]), "MG5 a continued entry is kept (noted)")
    t5 = t.replace("lantern.reach.Unique=12", "lantern.reach.Unique=18")
    K.check(not any("Unique" in str(x) for x in Cfg.m518Update(t5)[2]), "MG6 a line already at the new default is not noted")
    # end to end: History, change log, run once; the chain with migrate055 (a 0.5.4-style file: height 128, no 0.5.5 marker)
    home = os.path.join(scratch, "mg", "Skyy_SkyyAccessories")
    os.makedirs(home, exist_ok=True)
    f = os.path.join(home, "config.properties")
    old054 = ("slots=18\r\nline.Lantern=true\r\nlantern.reach.Normal=6\r\nlantern.reach.Unique=12\r\nlantern.reach.Rare=24\r\n"
              "lantern.reach.Legendary=48\r\nlantern.height=128\r\n")
    open(f, "wb").write(old054.encode("latin-1"))
    Cfg.FILE = Paths.get(f)
    a = str(Cfg.migrate055())
    b = str(Cfg.migrate0518())
    after = open(f, "rb").read().decode("latin-1")
    K.check("lantern.height 128 -> 64" in a and "0.5.18 Lantern reach" in b, "MG7 chain: migrate055 then migrate0518: %s | %s" % (a[:80], b[:80]))
    K.check("lantern.height=64\r\n" in after and "lantern.reach.Legendary=64\r\n" in after and "lantern.lights" not in after and
            str(Cfg.M55_MARK) in after and mark in after and after.index(mark) < after.index("lantern.reach.Normal"), "MG7 ... both markers, both updates")
    hist = os.path.join(home, "config-history")
    copies = []
    for root, _d, files in os.walk(hist):
        for fn in files:
            if fn.endswith(".properties") or "config" in fn:
                copies.append(open(os.path.join(root, fn), "rb").read())
    K.check(old054.encode("latin-1") in copies, "MG7 ... the 0.5.4 file is in config-history (%d copies)" % len(copies))
    logs = open(os.path.join(home, "config-changes.log"), encoding="latin-1").read() if os.path.exists(os.path.join(home, "config-changes.log")) else ""
    K.eq(sum(1 for ln in logs.splitlines() if "SkyyAccessories 0.5.18" in ln and "\tupdate\tlantern.reach." in ln), 4,
         "MG7 ... four 0.5.18 change-log lines (Server Setup -> Changes -> Undo); lantern.lights was absent: none")
    h0 = open(f, "rb").read()
    K.eq((str(Cfg.migrate055()), str(Cfg.migrate0518()), open(f, "rb").read() == h0), ("", "", True), "MG8 a second start: nothing, file untouched")
    K.save()


def run_cfg(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Paths = JClass("java.nio.file.Paths")
    Cfg, Defs = JClass(PKG + "AccCfg"), JClass(PKG + "AccDefs")
    mods = os.path.join(scratch, "cf", "mods")
    d = os.path.join(mods, "Skyy_SkyyAccessories")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "config.properties")
    Cfg.FILE = Paths.get(f)
    r = str(Cfg.load(True))
    t = open(f, encoding="latin-1").read()
    K.check("craft.bag=true" in t and "craft.autoEquip=true" in t and bool(Defs.CRAFT) and bool(Defs.AUTO), "CF a first start writes both keys (on)")
    K.check(str(Cfg.M518_MARK) in t and "lantern.reach.Legendary=64" in t and "lantern.lights=8" in t, "CF ... the new lantern defaults + the 0.5.18 marker (no migration later)")
    K.check(Cfg.m518Update(t) is None, "CF ... a fresh file never migrates")
    added, changed, lang = lang_diff()
    K.eq((added, changed), ([], LAN_DESC_KEYS), "CF server.lang: only the 8 Lantern description lines changed")
    K.check(all(("about %d blocks" % n) in lang["items.%s.description" % i] for i, n in zip(LAN_IDS, (10, 18, 32, 64))),
            "CF ... they say about 10 / 18 / 32 / 64 blocks")
    K.eq([int(x) for x in Defs.LAN_DEF], [11, 11, 11, 11, 10, 18, 32, 64, 64, 96, 8], "CF AccDefs.LAN_DEF = the 0.5.18 defaults")
    old = b"slots=18\r\nregenEverySeconds=5\r\n"
    open(f, "wb").write(old)
    Defs.CRAFT = False
    Defs.AUTO = False
    Cfg.reload()
    K.check(bool(Defs.CRAFT) and bool(Defs.AUTO) and open(f, "rb").read() == old, "CF a file without the keys = on, its bytes untouched")
    open(f, "wb").write(old + b"craft.bag=false\r\ncraft.autoEquip=false\r\n")
    r = str(Cfg.reload())
    K.check(not bool(Defs.CRAFT) and not bool(Defs.AUTO) and "the bag's Craft tab switched off" in r and "auto-equip of crafted accessories switched off" in r,
            "CF false = off, the summary says so: " + r)
    CP, Fn = JClass(PKG + "CfgPub"), JClass(PKG + "CfgFn")
    CP.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyAccessories"))
    Fn.cmdSetConsole("craft.bag", "true")
    Fn.cmdSetConsole("craft.autoEquip", "true")
    K.check(bool(Defs.CRAFT) and bool(Defs.AUTO), "CF the Server Setup edits set the fields live")
    CP.shutdown()
    br = JClass("java.lang.System").getProperties().get("skyy.bridge")
    hdr = br.get("config:def:SkyyAccessories") if br is not None else None
    rows = [[str(v) for v in r_] for r_ in hdr[7]] if hdr is not None else []
    K.eq([r_[0] for r_ in rows if r_[2] == "bag"], ["slots", "notice.boosters", "starter.bag", "craft.bag", "craft.autoEquip"], "CF the rows in the Accessory Bag section")
    lr = [r_ for r_ in rows if r_[0].startswith("lantern.reach.") or r_[0] == "lantern.lights"]
    K.eq([r_[4] for r_ in lr], ["10", "18", "32", "64", "8"], "CF the lantern rows show the new defaults")
    K.save()


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    f = os.path.join(home, "config.properties")
    t0 = open(f, "rb").read().decode("latin-1")
    h0 = HK.tree_hash(home)
    snaps, msgs = [], []
    for start in (1, 2):
        L = loader_for(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        J("AccStore").DIR = Paths.get(os.path.join(home, "bags"))
        J("AccCfg").FILE = Paths.get(f)
        J("AccCfg").migrate051()
        J("AccCfg").migrate055()
        msgs.append(str(J("AccCfg").migrate0518()))
        J("AccCfg").load(True)
        J("AccNotice").FILE = Paths.get(os.path.join(home, "notices.properties"))
        J("AccNotice").load()
        J("AccSnd").load(Paths.get(home))
        J("AccCraft").LOGF = Paths.get(os.path.join(home, "crafts.log"))
        J("CfgPub").start(Paths.get(mods), None)
        J("CfgPub").shutdown()
        snaps.append(HK.tree_hash(home))
        if start == 1:
            vals = [int(J("AccDefs").LAN_REACH1), int(J("AccDefs").LAN_REACH2), int(J("AccDefs").LAN_REACH3), int(J("AccDefs").LAN_REACH4),
                    int(J("AccDefs").LAN_LIGHTS)]
    t1 = open(f, "rb").read().decode("latin-1")
    was = [ln for ln in t0.splitlines() if ln.startswith("lantern.reach.") or ln.startswith("lantern.lights")]
    if was == ["lantern.reach.Normal=6", "lantern.reach.Unique=12", "lantern.reach.Rare=24", "lantern.reach.Legendary=48", "lantern.lights=7"]:
        K.check(msgs[0].startswith("config.properties updated to the 0.5.18 Lantern reach") and vals == [10, 18, 32, 64, 8],
                "D1 the live copy held the old defaults: migrated to 10 / 18 / 32 / 64, lights 8: %s" % msgs[0][:120])
    else:
        K.notes.append("D1 the live copy had custom lantern lines %s: %s" % (was, msgs[0][:160]))
    K.check(h0 != snaps[0] and t1.count("SkyyAccessories 0.5.18 Lantern reach") == 1, "D1 the first start changed the copy once (the marker once)")
    K.check(msgs[1] == "" and snaps[0] == snaps[1], "D2 the second start changes nothing")
    K.check(not os.path.exists(os.path.join(home, "crafts.log")), "D3 no craft journal without a craft")
    K.save()


if __name__ == "__main__":
    if "--build" in sys.argv and "--phase" not in sys.argv:
        print("kit: " + build_on_committed_kit())
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("craft", run_craft), ("auto", run_auto), ("mig", run_mig), ("cfg", run_cfg), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyAccessories"))
