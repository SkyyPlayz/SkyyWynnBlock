"""Harness for SkyyGear 0.2.18 (MULTITOOLS: InkBlindCat's Multitools as both a pickaxe and a hatchet; tools/gear_0_2_18_patch.py header).
Build first:
    python tools/gear_0_2_18_patch.py && python SkyyGear/build_skyygear_0.2.18.py

    python SkyyGear/test_skyygear_0.2.18.py [--jar <SkyyGear-0.2.18.jar>] [--old <SkyyGear-0.2.17.jar>] [--mt <Multitools-1.2.9.jar>] [--dir <scratch>] [--keep]

The 0.2.11 harness's helpers (stand-ins F, verify A, the bare-server boot of V, the engine-access audit AA) are loaded from
SkyyGear/test_skyygear_0.2.11.py and run on the 0.2.18 jar (the 0.2.12 - 0.2.17 harnesses do the same). The Multitools jar is COPIED into the
scratch folder (read only source: UserData/Mods/Multitools-1.2.9.jar) and loaded from there as its own pack.
  S  non-class entries 0.2.17 -> 0.2.18: only the manifest changed; nothing of the Multitools mod is in the jar (no file, no id)
  A  every class of the jar loads + verifies (-Xverify:all)
  V  the vanilla pack store by store + THE JAR as its own pack (real Item / BlockType / CraftingRecipe stores) + every item recipe generated the
     way CraftingPlugin.onItemAssetLoad does it
  X  the 0.2.17 tool sections X0 - X8 again (regression) + EVERY NEW CODE PATH EXECUTED (-Xverify:all):
     XM0 WITHOUT the Multitools jar: nothing found, nothing changed; family 6 by id, part.multitool off = a hatchet again
     XM1 WITH the jar (loaded as pack IBC:Multitools, its recipes generated like the engine): every multitool recipe = pickaxe + hatchet (+ the
         Iron shovel - the only craftable one) of its tier, same id / bench / time / output; a second run changes nothing; the salvage cap (the
         real Onyxium salvage is removed, the others are under the cap, a synthetic over-cap salvage is clamped); a reloaded multitool
         (LoadedAssetsEvent(Item) through GearBoxL) gets our recipe back
     XM2 stats: both sides = the same-tier pickaxe / hatchet x 85 % / x 70 % (with rarity boost + modifiers), held() posts dd.mining + only.mining
         + dd.foraging + xp.*, under-level (Mining AND Foraging), the REAL block hits (stone, log, soil), the live rows, part.tools off
     XM3 rarity on craft + the 6-key pool, no craft XP; XM4 reforge / level up end to end; XM5 craft level from the lower skill, tooltip lines,
         the gate line, GearMine sees a pickaxe, status text
  C  CLASS COMPARE 0.2.17 -> 0.2.18 (javassist members): only GearMulti added, only the listed classes / members differ
  D  THE ONE-TIME UPDATE migrate0218: synthetic files (fresh, LF / CRLF, no final newline, keys already there) + START TWICE on a scratch COPY
     of the live Skyy_SkyyGear folder (block appended, History copy, nothing else; the 2nd start changes nothing)
  AA THE ENGINE-ACCESS AUDIT
Scratch: tools/dev/scratch/gear0218/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.18"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear0218")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-0.2.17.jar")))      # read only
MT_SRC = os.path.abspath(arg("--mt", os.path.join(B.MODS_DIR, "Multitools-1.2.9.jar")))   # read only - copied into the scratch folder
MT_JAR = os.path.join(SCRATCH, "mt", "Multitools-1.2.9.jar")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
PKG = "com.skyy.gear."
TOOL_KEYS = ["mpow", "dpow", "cpow", "mfort", "ffort", "afort", "mwis", "fwis", "awis"]
FAM_KEYS = {1: {"mpow", "mfort", "mwis"}, 2: {"dpow", "mfort", "mwis"}, 3: {"cpow", "ffort", "fwis"}, 4: {"afort", "awis"}, 5: {"afort", "awis"}}
FAM_ID = {1: "Tool_Pickaxe_Iron", 2: "Tool_Shovel_Iron", 3: "Tool_Hatchet_Iron", 4: "Tool_Hoe_Iron", 5: "Tool_Sickle_Iron"}
MULTI_PRE = "Tool_Hatchet_Pickaxe_Multitool_"
MULTI_TIERS = ["Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
MULTI_KEYS = {"mpow", "cpow", "mfort", "ffort", "mwis", "fwis"}
MT_HEAD = "# ---- Multitools: the Multitools mod's multitools cost a pickaxe + hatchet (+ shovel) and count as both (SkyyGear 0.2.18) ----"
TR_HEAD = "# ---- Tool rarity: crafted gathering tools roll a rarity and tool modifiers (SkyyGear 0.2.17) ----"
EXPECT_CHANGED = {"GearCfg", "GearDefs", "GearData", "GearGate", "GearRoll", "GearTool", "GearMine", "GearBoxL", "SkyyGearPlugin",
                  "CfgRows", "CfgFile"}       # CfgRows / CfgFile: the kit's row tables (the 3 new rows) in <clinit>

_H211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
_t = open(_H211, encoding="utf-8").read()
_cut = _t.rindex('if __name__ == "__main__":')
H = {"__name__": "skyygear_h211", "__file__": _H211, "__builtins__": __builtins__}
exec(compile(_t[:_cut], _H211 + " (helpers)", "exec"), H)
H.update({"JAR": JAR, "OLD_JAR": OLD_JAR, "SCRATCH": SCRATCH, "FAKE_DIR": os.path.join(SCRATCH, "fake"), "VERSION": VERSION})
FAKE_DIR, FAKE_PKG = H["FAKE_DIR"], H["FAKE_PKG"]
Child, _jvm, jar_classes = H["Child"], H["_jvm"], H["jar_classes"]
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def jround(x):
    """Java Math.round for the positive values here (half up)"""
    return int(math.floor(x + 0.5))


# ====================================================================================================== S: non-class entries
def run_assets():
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(eb) - set(ea))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    check(not added and not (set(ea) - set(eb)) and changed == ["manifest.json"] and b'"0.2.18"' in eb["manifest.json"]
          and b"Multitools mod (by InkBlindCat, MIT)" in eb["manifest.json"],
          "S: 0.2.17 -> 0.2.18: no file added / removed, only the manifest changed (version + the multitool sentence with the credit): + %s ~ %s"
          % (added[:3], changed[:3]))
    mz = zipfile.ZipFile(MT_JAR)
    theirs = set(n for n in mz.namelist() if not n.endswith("/") and n not in ("META-INF/MANIFEST.MF", "manifest.json") and not n.endswith(".lang"))
    clash = sorted(set(zn.namelist()) & theirs)
    ids = set(os.path.basename(n)[:-5] for n in theirs if n.endswith(".json") and "_" in os.path.basename(n)[:-5])
    hit = sorted(n for n in eb if any(i.encode() in eb[n] for i in ids))
    check(not clash and not hit and not [n for n in zn.namelist() if "Multitool" in n or "inkblindcat" in n.lower()] and len(ids) >= 17,
          "S: the Multitools mod is never shipped or overridden: no path of its jar, no file naming one of its %d asset ids, no Multitool path: %s %s"
          % (len(ids), clash[:3], hit[:3]))


# ====================================================================================================== V + X
def run_engine(out):
    from jpype import JClass, JArray, JInt, JLong, JShort, JFloat, JDouble, JImplements, JOverride, JObject, JBoolean
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
    E = H["engine_boot"](K)
    K.check(set(E["fail"]) <= set(E["vfail"]), "V: the jar as its own pack: no failed store of its own (%s vs vanilla %s)" % (E["fail"], E["vfail"]))
    ours = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and ("SkyyGear_Spd_Mace" in r[1] or "Mace_Primary_Swing" in r[1] and "_Next" in r[1])]
    K.check(not ours, "V: no SEVERE / WARNING about the named mace steps in the bare boot: %s" % ours[:3])
    # the engine's generated item recipes (CraftingPlugin.onItemAssetLoad is not running in a bare boot): the same calls, every item
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    ITEM = E["ITEM"]
    HAL = JClass("java.util.ArrayList")
    # the bare boot decodes the Item store before the BlockSet store, so every vanilla tool (Tool.DurabilityLossBlockTypes names block sets:
    # "Unknown key! Stone") is missing - load the vanilla Tool_* item files again now that the block sets are in (the real server has them)
    BSc = JClass("com.hypixel.hytale.server.core.asset.type.blockset.config.BlockSet")
    AZP = os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Assets.zip")
    afs = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(AZP), JClass("java.util.HashMap")())
    with zipfile.ZipFile(AZP) as az_:
        tnames = [n for n in az_.namelist() if n.startswith("Server/Item/Items/Tool/") and n.endswith(".json")]
    tl_ = HAL()
    for n in tnames:
        tl_.add(afs.getPath("/" + n))
    had = ITEM.getAssetMap().getAsset("Tool_Pickaxe_Copper") is not None
    ITEM.getAssetStore().loadAssetsFromPaths("Hytale:Hytale", tl_)
    K.check(int(BSc.getAssetMap().getIndex("Stone")) >= 0 and not had and all(ITEM.getAssetMap().getAsset(i) is not None for i in (
        "Tool_Pickaxe_Copper", "Tool_Hatchet_Copper", "Tool_Shovel_Iron", "Tool_Pickaxe_Onyxium", "Tool_Hatchet_Crude", "Tool_Shovel_Copper")),
        "V: the %d vanilla tool items reloaded once the block sets are in (the bare boot had dropped them: %s)" % (len(tnames), had))

    def gen_recipes(items):
        lst = HAL()
        for it in items:
            if it is not None and it.hasRecipesToGenerate():
                it.collectRecipesToGenerate(lst)
        if lst.size() > 0:
            CRR.getAssetStore().loadAssets("Hytale:Hytale", lst)
        return int(lst.size())
    ng = gen_recipes(list(ITEM.getAssetMap().getAssetMap().values()))
    rmap = CRR.getAssetMap().getAssetMap()
    gid = lambda i: str(CRR.generateIdFromItemRecipe(ITEM.getAssetMap().getAsset(i), JInt(0)))
    K.check(ng > 300 and rmap.get(gid("Tool_Shovel_Iron")) is not None and rmap.get(gid("Tool_Shovel_Copper")) is None,
            "V: %d item recipes generated like the engine (Iron shovel has one: %s, the Copper shovel none); %d recipes in the store"
            % (ng, gid("Tool_Shovel_Iron"), rmap.size()))
    P = lambda n: JClass(PKG + n)
    (Cfg, Defs, Data, Roll, Tool, View, Forge, Ident, Lvl, Gate, Speed, Gear) = [P(n) for n in (
        "GearCfg", "GearDefs", "GearData", "GearRoll", "GearTool", "GearView", "GearForge", "GearIdent", "GearLevel", "GearGate", "GearSpeed", "Gear")]
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    BD = JClass("org.bson.BsonDocument")
    BA = JClass("org.bson.BsonArray")
    BI32 = JClass("org.bson.BsonInt32")
    Props = JClass("java.util.Properties")
    UUID = JClass("java.util.UUID")
    AL = JClass("java.util.ArrayList")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    SR = JClass("java.io.StringReader")
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000b017")
    PURSE, XP = {}, []
    LEVELS = {}

    @JImplements("java.util.function.Function")
    class CoinGet:
        @JOverride
        def apply(self, u): return JLong(PURSE.get(str(u), 0))

    @JImplements("java.util.function.Function")
    class CoinTake:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            if PURSE.get(u, 0) < n:
                return JBoolean(False)
            PURSE[u] = PURSE.get(u, 0) - n
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class CoinAdd:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            PURSE[u] = PURSE.get(u, 0) + n
            return JLong(PURSE[u])

    @JImplements("java.util.function.Function")
    class AddXp:
        @JOverride
        def apply(self, a):
            XP.append((str(a[1]), int(a[2]), str(a[3])))
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class SkillLv:
        @JOverride
        def apply(self, a):
            return JInt(LEVELS.get(str(a[1]), 0))
    br.put("coins:fn:get", CoinGet())
    br.put("coins:fn:take", CoinTake())
    br.put("coins:fn:add", CoinAdd())
    br.put("skill:fn:addxp", AddXp())
    br.put("skill:fn:level", SkillLv())

    def skills(mining=49, foraging=49, farming=49, smithing=0):
        LEVELS.clear()
        LEVELS.update({"Mining": mining, "Foraging": foraging, "Farming": farming, "Smithing": smithing, "Combat": 49})
        br.put("class:skill:" + str(U1), "Combat")
        Gate.forget(U1)
        Tool.LAST.clear()

    FRESH = str(Cfg.defaultsText())

    def props(**kv):
        p = Props()
        p.load(SR(FRESH))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        return p

    def apply(**kv):
        Cfg.apply(props(**kv), False)

    def doc(s):
        return Data.effective(s.getItemId(), s.getMetadata())

    def mods(d):
        out_ = []
        ms = Data.mods(d)
        for i in range(ms.size()):
            m = ms.get(i).asDocument()
            out_.append((str(Data.str(m, "s", "")), int(Data.num(m, "v", 0))))
        return out_

    def withmods(d, kv):
        a = BA()
        for k, v in kv:
            a.add(Data.mod(k, JInt(v)))
        d.put("mods", a)
        return d

    def gsrc():
        o = br.get("skill:bonus:" + str(U1))
        g = o.get("gear") if o is not None else None
        if g is None:
            return None
        out_ = {}
        for k in g.keySet():
            v_ = g.get(k)
            out_[str(k)] = v_ if isinstance(v_, str) else (str(v_) if "String" in str(type(v_)) else float(v_))
        return out_
    apply()
    skills()
    SI = lambda k: int(Defs.sIndex(k))
    R_MODS = [int(x) for x in Cfg.R_MODS]
    RN = [str(x) for x in Defs.R_ID]

    # ============================================================================ X0 rows, fresh file, boost parse
    L = FRESH.rstrip("\n").split("\n")
    ti = L.index("# ---- Tool rarity: crafted gathering tools roll a rarity and tool modifiers (SkyyGear 0.2.17) ----")
    mi = L.index(MT_HEAD)
    blk = L[ti:mi - 1]          # 0.2.18: the multitool block follows the 0.2.17 block
    mblk = L[mi:]
    K.check(L[mi - 1] == "" and len(mblk) == 2 + 2 * 3 and mblk[1].startswith("# SkyyGear 0.2.18 multitools (Skyy 2026-10-10)")
            and "part.multitool=true" in mblk and "multi.speedPct=85" in mblk and "multi.fortunePct=70" in mblk
            and bool(Cfg.MULTI_ON) and int(Cfg.MULTI_SPD) == 85 and int(Cfg.MULTI_FORT) == 70,
            "XM: the fresh file ends with the 0.2.18 block (heading, marker, 3 rows each with its help line); the defaults load: %s" % mblk[:3])
    apply(multi__speedPct="500", multi__fortunePct="-4")
    K.check(int(Cfg.MULTI_SPD) == 100 and int(Cfg.MULTI_FORT) == 0, "XM: hand-edited rows clamp (speed 500 -> 100, Fortune -4 -> 0)")
    Cfg.apply(Props(), False)
    K.check(bool(Cfg.MULTI_ON) and int(Cfg.MULTI_SPD) == 85 and int(Cfg.MULTI_FORT) == 70, "XM: a file without the 0.2.18 lines reads the defaults")
    apply()
    K.check(L[ti - 1] == "" and blk[1].startswith("# SkyyGear 0.2.17 tool rarity (Skyy 2026-10-10)") and len(blk) == 2 + 2 * (6 + 9)
            and "part.toolRarity=true" in blk and "tool.rarityBoost=0 5 10 15 20 25" in blk and "tool.spareSlotBoost=10.0" in blk
            and "tool.spareSlotMax=30.0" in blk and "tool.wisdom.cap=15.0" in blk and "tool.xpCraft=100" in blk
            and "stats.mpow=30,10" in blk and "stats.afort=10,10" in blk and "stats.awis=10,8" in blk
            and "# mfort = Mining Fortune (tool modifier: pickaxe, shovel)" in blk,
            "X0: the fresh file ends with the 0.2.17 block (heading, marker, 6 rows + 9 stats rows, each with its comment): %s" % blk[:4])
    K.check(sum(1 for x in L if x.startswith("stats.mpow=")) == 1 and L.index("stats.xpb=5,2") < ti,
            "X0: the tool stats rows sit only in the 0.2.17 block (the stats block keeps its 0.2.16 rows)")
    K.check(bool(Cfg.TOOL_RAR) and str(Cfg.TOOL_RBT) == "0 5 10 15 20 25" and float(Cfg.TOOL_SPARE) == 10.0 and float(Cfg.TOOL_SPAREMAX) == 30.0
            and float(Cfg.TOOL_WCAP) == 15.0 and int(Cfg.TOOL_XPC) == 100 and [float(Cfg.toolBoost(JInt(r))) for r in range(8)] == [0, 5, 10, 15, 20, 25, 0, 0],
            "X0: the defaults load; toolBoost Normal..Mythic 0/5/10/15/20/25, Set / Untiered 0")
    Cfg.apply(Props(), False)
    K.check(bool(Cfg.TOOL_RAR) and int(Cfg.TOOL_XPC) == 100 and float(Cfg.toolBoost(JInt(2))) == 10.0,
            "X0: a file with none of the 0.2.17 lines (an old file before the update) reads the defaults")
    apply(tool__rarityBoost="1 2 three", tool__wisdom__cap="900", tool__xpCraft="-5")
    K.check(str(Cfg.TOOL_RBT) == "0 5 10 15 20 25" and float(Cfg.TOOL_WCAP) == 100.0 and int(Cfg.TOOL_XPC) == 0,
            "X0: a hand-edited bad boost row -> the default (one WARN); caps clamp (Wisdom cap 900 -> 100, xpCraft -5 -> 0)")
    Cfg.TOOL_RBT = "10,20,30,40,50,60"
    K.check(float(Cfg.toolBoost(JInt(3))) == 40.0, "X0: a live Server Setup edit of the boost row (the kit sets the String field) is re-parsed at once")
    K.check(Cfg.checkBoost("tool.rarityBoost", "0 5 10 15 20 25") is None and Cfg.checkBoost("tool.rarityBoost", "1 2 3") is not None
            and Cfg.checkBoost("tool.rarityBoost", "0 5 10 15 20 999") is not None and Cfg.boostOf(" 0, 5,10 15 20 25 ") is not None,
            "X0: checkBoost refuses a wrong count / range, takes spaces or commas")
    K.check(Cfg.checkStat("stat[mpow]", "30,10") is None and Cfg.checkStat("stat[mpow]", "500,10") is not None and Cfg.checkStat("stat[nope]", "1,1") is not None,
            "X0: the Stats table knows the tool keys (the 4x-default question works on them)")
    apply()

    # ============================================================================ X1 the pools
    def pool(slot, iid):
        return sorted(str(Defs.S_KEY[i]) for i in Roll.pool(JInt(slot), iid))
    pools = dict((f, pool(3, FAM_ID[f])) for f in FAM_ID)
    K.check(all(set(pools[f]) == FAM_KEYS[f] for f in FAM_ID), "X1: each tool family rolls only its own keys: %s" % pools)
    K.check(pool(3, "Tool_Hammer_Iron") == [] and pool(3, None) == [] and pool(3, "Weapon_Sword_Iron") == [],
            "X1: a hammer (not a gathering tool), no item and a weapon have no tool pool")
    wsw, war = pool(0, "Weapon_Sword_Iron"), pool(2, "Armor_Iron_Chest")
    K.check(not set(wsw) & set(TOOL_KEYS) and not set(war) & set(TOOL_KEYS) and not set(pool(1, "Weapon_Staff_Iron")) & set(TOOL_KEYS)
            and "dmg" in wsw and "def" in war, "X1: weapons / spells / armor never roll a tool key (and keep their own pools)")
    K.check(not set(sum(pools.values(), [])) - set(TOOL_KEYS), "X1: a tool never rolls a combat stat")
    apply(part__toolRarity="false")
    off1 = pool(3, "Tool_Pickaxe_Iron")
    apply(part__tools="false")
    off2 = pool(3, "Tool_Pickaxe_Iron")
    apply()
    K.check(off1 == [] and off2 == [], "X1: part.toolRarity off or part.tools off -> no tool pool")

    # ============================================================================ X2 the craft roll distribution
    def bnd(key, r, lvl, boost=0.0):
        i = SI(key)
        f = float(Lvl.factor(JInt(lvl)))
        mx = float(Cfg.S_MAX[i]) * (1.0 + boost / 100.0)
        lo = max(1, jround(mx * float(Cfg.R_LO[r]) / 100.0 * f / 100.0))
        hi = max(1, jround(mx * float(Cfg.R_HI[r]) / 100.0 * f / 100.0))
        return lo, max(lo, hi)
    odds = [float(x) for x in Cfg.O_CRAFT]
    tot = sum(odds)
    N = 3000
    cnt = [0] * 8
    badd = []
    lv0 = int(Roll.craftLevel("Tool_Pickaxe_Iron", U1))
    for k in range(N):
        d = Roll.craftDoc("Tool_Pickaxe_Iron", U1, JInt(lv0))
        r = int(Data.rarity(d))
        cnt[r] += 1
        ms = mods(d)
        want_n = min(R_MODS[r], 3)
        sp = min(max(0, R_MODS[r] - 3) * 10.0, 30.0)
        if (len(ms) != want_n or len(set(k_ for k_, v in ms)) != len(ms) or not set(k_ for k_, v in ms) <= FAM_KEYS[1]
                or not all(bnd(k_, r, lv0, sp)[0] <= v <= bnd(k_, r, lv0, sp)[1] for k_, v in ms)
                or int(Data.num(d, "tr", 0)) != 1 or d.containsKey("spd") or int(Lvl.level("Tool_Pickaxe_Iron", d)) != lv0):
            badd.append((RN[r], ms))
    share = [c * 100.0 / N for c in cnt]
    exp = [o * 100.0 / tot for o in odds]
    tol = [4.0, 3.5, 2.5, 1.6, 0.9, 0, 0, 0]
    K.check(all(abs(share[r] - exp[r]) <= tol[r] for r in range(5)) and cnt[5] == cnt[6] == cnt[7] == 0 and not badd,
            "X2: 3000 crafted Iron pickaxes (Smithing 0, Lv %d) follow the craft odds column %s%% -> %s%%; never Mythic / Set / Untiered; each has "
            "min(rarity count, 3) distinct pickaxe modifiers inside the rarity's bounds at its level (+ the spare-slot boost from Legendary up), "
            "\"tr\", no speed tier, the craft level: bad %s" % (lv0, [round(x, 1) for x in exp[:5]], [round(x, 1) for x in share[:5]], badd[:3]))
    K.notes.append("X2 rarity counts over %d crafted pickaxes: %s" % (N, dict(zip(RN, cnt))))
    skills(smithing=100)
    c2 = [0] * 8
    for k in range(2000):
        c2[int(Data.rarity(Roll.craftDoc("Tool_Pickaxe_Iron", U1, JInt(lv0))))] += 1
    skills()
    K.check(c2[0] < 2000 * 0.40 and c2[1] > 2000 * 0.35 and c2[5] == c2[6] == c2[7] == 0,
            "X2: Smithing 100 (step-up chance capped at smith.cap 50%%) moves tools up the ladder like gear: Normal %d, Unique %d of 2000; still never Mythic"
            % (c2[0], c2[1]))
    apply(craft__maxRarity="rare")
    c3 = [0] * 8
    for k in range(1500):
        c3[int(Data.rarity(Roll.craftDoc("Tool_Hatchet_Iron", U1, JInt(20))))] += 1
    apply()
    K.check(c3[3] == c3[4] == c3[5] == 0 and c3[2] > 0, "X2: craft.maxRarity rare caps tools too: %s" % c3[:5])
    apply(odds__set="0,0,0", odds__normal="0,50,45", odds__unique="0,30,30", odds__rare="0,13,15", odds__legendary="0,5,7", odds__fabled="0,1.5,2.4")
    Cfg.O_CRAFT = JArray(JDouble)([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0, 0.0])
    c4 = [int(Data.rarity(Roll.craftDoc("Tool_Pickaxe_Iron", U1, JInt(20)))) for k in range(50)]
    w4 = int(Data.rarity(Roll.craftDoc("Armor_Cloth_Cotton_Chest", U1, JInt(20))))
    apply()
    K.check(set(c4) == {0} and w4 == int(Defs.R_SET), "X2: a Set craft roll (an admin weight) -> Normal on a tool (no set id), armor keeps Set")
    fams = {}
    for f, iid in FAM_ID.items():
        seen = set()
        for k in range(300):
            d = Roll.craftDoc(iid, U1, JInt(20))
            seen |= set(k_ for k_, v in mods(d))
        fams[f] = sorted(seen)
    K.check(all(set(fams[f]) == FAM_KEYS[f] for f in FAM_ID), "X2: over 300 crafts each family rolls every key of its pool and nothing else: %s" % fams)
    hoe = []
    for k in range(400):
        d = Roll.newDoc("Tool_Hoe_Iron", JInt(4), True, "test", JInt(30))
        hoe += [(k_, v) for k_, v in mods(d)]
    blo, bhi = bnd("afort", 4, 30, 30.0)
    plo, phi = bnd("afort", 4, 30, 0.0)
    K.check(len(hoe) == 800 and all(blo <= v <= bhi for k_, v in hoe if k_ == "afort") and max(v for k_, v in hoe if k_ == "afort") > phi
            and abs(float(Roll.spare(JInt(3), JInt(4), JInt(2))) - 30.0) < 1e-9 and float(Roll.spare(JInt(3), JInt(1), JInt(3))) == 0.0
            and float(Roll.spare(JInt(0), JInt(4), JInt(2))) == 0.0,
            "X2: the spare-slot boost: a Fabled hoe (5 slots, pool 2 -> +30%%, capped) rolls Farming Fortune %d-%d (unboosted %d-%d); weapons never boost"
            % (blo, bhi, plo, phi))
    sw = Roll.craftDoc("Weapon_Sword_Iron", U1, JInt(20))
    K.check(not set(k_ for k_, v in mods(sw)) & set(TOOL_KEYS) and sw.containsKey("spd") and int(Data.num(sw, "tr", 0)) == 0,
            "X2: a crafted sword is unchanged (combat modifiers, its speed tier, no tr)")
    apply(part__toolRarity="false")
    off = [Roll.craftDoc("Tool_Pickaxe_Iron", U1, JInt(20)) for k in range(30)]
    apply()
    hm = Roll.craftDoc("Tool_Hammer_Iron", U1, JInt(-1))
    K.check(all(int(Data.rarity(d)) == 0 and Data.mods(d).size() == 0 and int(Data.num(d, "tr", 0)) == 0 for d in off)
            and int(Data.rarity(hm)) == 0 and Data.mods(hm).size() == 0 and int(Data.num(hm, "tr", 0)) == 0,
            "X2: part.toolRarity off -> crafted pickaxes are Normal, no modifiers, no tr (0.2.16); a hammer is never rolled")
    sd = Speed.ensure("Tool_Pickaxe_Iron", Roll.craftDoc("Tool_Pickaxe_Iron", U1, JInt(20)))
    put = Data.put(IS("Tool_Pickaxe_Iron", JInt(1)), Roll.craftDoc("Tool_Pickaxe_Iron", U1, JInt(20)), U1)
    K.check(not sd.containsKey("spd") and not doc(put).containsKey("spd"),
            "X2: no weapon speed tier on a tool through GearSpeed.ensure or the document write (GearData.put) - Skyy 2026-10-06")

    # ============================================================================ X3 Smithing XP per crafted tool
    xc = [int(Cfg.xpCraft(JInt(r))) for r in range(5)]
    tier_f = float(Roll.xpTier(JInt(int(Roll.xpStart("Tool_Pickaxe_Iron")))))
    want = [jround(xc[r] * tier_f) for r in range(5)]
    got = [int(Roll.craftXp("Tool_Pickaxe_Iron", JInt(r))) for r in range(5)]
    swx = [int(Roll.craftXp("Weapon_Sword_Iron", JInt(r))) for r in range(5)]
    K.check(got == want and got == swx and got[0] == 250 and int(Roll.craftXp("Tool_Hammer_Iron", JInt(0))) == 0
            and int(Roll.craftXp("Tool_Pickaxe_Mithril", JInt(2))) == jround(xc[2] * float(Roll.xpTier(JInt(40)))),
            "X3: craft Smithing XP of an Iron pickaxe by rarity = xp.craft x the tier factor %.2f = %s (= an Iron sword's); hammer 0; Mithril x2" % (tier_f, got))
    apply(tool__xpCraft="50")
    half = [int(Roll.craftXp("Tool_Pickaxe_Iron", JInt(r))) for r in range(5)]
    apply(part__toolRarity="false")
    offx = int(Roll.craftXp("Tool_Pickaxe_Iron", JInt(2)))
    apply()
    K.check(half == [jround(x * tier_f * 0.5) for x in xc] and offx == 0, "X3: tool.xpCraft 50 halves it (%s); part.toolRarity off = no craft XP" % half)
    del XP[:]
    res = Roll.payCraft(U1, "Tool_Hatchet_Iron", " normal rare legendary", "Tester")
    tf2 = float(Roll.xpTier(JInt(int(Roll.xpStart("Tool_Hatchet_Iron")))))
    K.check(list(res) == [3, sum(jround(xc[r] * tf2) for r in (0, 2, 3)), 0] and XP == [("Smithing", jround(xc[r] * tf2), "gear:craft") for r in (0, 2, 3)],
            "X3: payCraft pays each crafted tool once through skill:fn:addxp (Smithing, source gear:craft): %s %s" % (list(res), XP))
    del XP[:]
    K.check(list(Roll.payCraft(U1, "Tool_Hammer_Iron", " normal", "Tester")) == [0, 0, 0] and XP == [], "X3: a hammer pays nothing")

    # ============================================================================ X3b FIX ROUND: no Smithing XP loop through the Salvagebench
    az = zipfile.ZipFile(os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Assets.zip"))
    items, sal = {}, {}
    for n in az.namelist():
        if n.startswith("Server/Item/Recipes/") and n.endswith(".json"):
            try:
                rd = json.loads(az.read(n).decode("utf-8-sig"))
            except Exception:
                continue
            ins = [x.get("ItemId") for x in (rd.get("Input") or []) if isinstance(x, dict)]
            if len(ins) == 1 and isinstance(ins[0], str):
                sal.setdefault(ins[0], []).append([o for o in (rd.get("Output") or []) if isinstance(o, dict)])
        elif n.startswith("Server/Item/Items/") and n.endswith(".json"):
            iid = os.path.basename(n)[:-5]
            if iid.startswith(("Tool_", "Weapon_", "Armor_")):
                try:
                    items[iid] = json.loads(az.read(n).decode("utf-8-sig"))
                except Exception:
                    pass

    def lap(iid):
        d = items.get(iid)
        if not isinstance(d, dict) or not isinstance(d.get("Recipe"), dict):
            return None
        mt = iid.rsplit("_", 1)[-1]
        bars = sum(int(x.get("Quantity", 1)) for x in (d["Recipe"].get("Input") or []) if isinstance(x, dict) and x.get("ItemId") == "Ingredient_Bar_" + mt)
        if bars <= 0:
            return None
        back = max([0] + [sum(int(o.get("Quantity", 1)) for o in os_ if o.get("ItemId") in ("Ore_" + mt, "Ingredient_Bar_" + mt)) for os_ in sal.get(iid, [])])
        return bars, back
    gear_meas = max(lap(i)[1] / float(lap(i)[0]) for i in items if lap(i) and bool(Data.isGear(i)))
    gear_worst = 0.5          # the 0.2.3 ANTI-FARM bound (build header: ore back <= 0.5 per bar on the live set, worst x2 per metal)
    tl, bad3 = [], []
    for iid in sorted(items):
        lb = lap(iid)
        if not lb or not bool(Data.toolRolls(iid)):
            continue
        bars, back = lb
        full = jround(xc[2] * float(Roll.xpTier(JInt(int(Roll.xpStart(iid))))))
        got_ = int(Roll.craftXp(iid, JInt(2)))
        tl.append((iid, bars, back, got_, full))
        # a lap (craft, salvage, smelt back) costs bars - back of the metal: XP per net bar never above a full-pay item at the gear bound
        if got_ > 0 and (back / float(bars) > gear_worst + 1e-9 or got_ / float(bars - back) > full / (bars * (1.0 - gear_worst)) + 1e-6):
            bad3.append((iid, bars, back, got_))
    sc = [int(Roll.craftXp("Tool_Sickle_Copper", JInt(r))) for r in range(5)]
    si = int(Roll.craftXp("Tool_Sickle_Iron", JInt(0)))
    K.check(gear_meas <= 0.5 + 1e-9 and not bad3 and len(tl) >= 15 and sc == [0, 0, 0, 0, 0]
            and si == jround(xc[0] * float(Roll.xpTier(JInt(int(Roll.xpStart("Tool_Sickle_Iron")))))) and int(Roll.toolXpPct("Tool_Pickaxe_Iron")) == 100
            and int(Roll.toolXpPct("Tool_Sickle_Copper")) == 0,
            "X3b (critic 1, XP loop): over %d rolling vanilla tools with a recipe, XP per NET bar of a craft -> salvage -> smelt lap is never above the "
            "0.2.3 anti-farm bound (ore back <= %.2f per bar; vanilla gear's worst %.2f); the Copper sickle (1 bar in, 1 ore back) pays %s, the Iron "
            "sickle (2 in, 1 back) full %d: %s" % (len(tl), gear_worst, gear_meas, sc, si, bad3[:3]))
    K.notes.append("X3b tools (id, bars, ore back, Rare XP, full Rare XP): %s" % [t for t in tl if t[3] != t[4] or "Sickle" in t[0] or "Hoe" in t[0]])
    del XP[:]
    res = Roll.payCraft(U1, "Tool_Sickle_Copper", " normal rare", "Tester")
    K.check(int(res[1]) == 0 and sum(x[1] for x in XP) == 0, "X3b: payCraft of two Copper sickles pays 0 Smithing XP: %s %s" % (list(res), XP))

    # ============================================================================ X3c FIX ROUND: the switch does not silently need part.levels
    apply(part__levels="false")
    cl = [bool(Roll.craftable(i)) for i in ("Tool_Pickaxe_Iron", "Tool_Sickle_Iron", "Tool_Hammer_Iron", "Weapon_Sword_Iron")]
    dl = Roll.craftDoc("Tool_Pickaxe_Iron", U1, JInt(int(Roll.craftLevel("Tool_Pickaxe_Iron", U1))))
    xl = int(Roll.craftXp("Tool_Pickaxe_Iron", JInt(0)))
    apply(part__levels="false", part__toolRarity="false")
    cl2 = bool(Roll.craftable("Tool_Pickaxe_Iron"))
    apply()
    cl3 = bool(Roll.craftable("Tool_Pickaxe_Iron"))
    K.check(cl == [True, True, False, True] and int(Data.num(dl, "tr", 0)) == 1 and not dl.containsKey("lvl") and xl == 250 and not cl2 and cl3,
            "X3c (critic 2): part.levels off -> a crafted pickaxe still gets its rolled document (tr, no level stamp) + its craft XP; a hammer not; "
            "both off -> not craftable (0.2.16); default on: %s %s" % (cl, cl2))

    # ============================================================================ X4 GearTool: the stats live
    def tstack(iid, lvl, r, kv, rolled=True):
        d = Roll.newDoc(iid, JInt(r), True, "test", JInt(lvl))
        withmods(d, kv)
        if not rolled:
            d.remove("tr")
        md = BD()
        md.put(str(Defs.DOC_KEY), d)
        return IS(iid, JInt(1)).withMetadata(md), d
    s1, d1 = tstack("Tool_Pickaxe_Iron", 23, 2, [("mpow", 20), ("mfort", 5), ("mwis", 7)])
    p0, f0 = float(Tool.power(JInt(1), JInt(23), JInt(2))), float(Tool.fortune(JInt(1), JInt(23), JInt(2)))
    pw = (1.0 + (p0 - 1.0) * 1.10) * 1.20
    fo = round(min(f0 * 1.10 + 5, 25.0) * 10.0) / 10.0
    ef = [float(x) for x in Tool.eff(JInt(1), JInt(23), JInt(2), d1)]
    K.check(abs(ef[0] - pw) < 1e-9 and abs(ef[1] - fo) < 1e-9 and ef[2] == 7.0,
            "X4: a Rare Iron pickaxe Lv 23 with Mining Power +20%% / Fortune +5 / Wisdom +7%%: power %.4f (level %.4f, rarity +10%% of the bonus, x1.2), "
            "Fortune %.1f (level %.1f x1.1 + 5), Wisdom 7: %s" % (pw, p0, fo, f0, ef))
    skills()
    st = [float(x) for x in Tool.stats(U1, s1)]
    K.check(len(st) == 9 and st[3] == 1.0 and abs(st[4] - pw) < 1e-9 and abs(st[5] - fo) < 1e-9 and st[8] == 7.0, "X4: stats() (Mining 49): %s" % st)
    br.remove("skill:bonus:" + str(U1))
    Tool.LAST.clear()
    Tool.held(U1, s1)
    g = gsrc()
    K.check(g is not None and abs(g["dd.mining"] - fo / 100.0) < 1e-9 and abs(g["xp.mining"] - 0.07) < 1e-9 and g["only.mining"] == "Rock_,Rubble_,Ore_",
            "X4: held() posts skill:bonus \"gear\" dd.mining = Fortune / 100 and xp.mining = the tool's Wisdom / 100 (SkyySkills' live XP bonus): %s" % g)
    s2, d2 = tstack("Tool_Pickaxe_Iron", 23, 4, [("mwis", 40), ("mfort", 60), ("mpow", 9000)])
    e2 = [float(x) for x in Tool.eff(JInt(1), JInt(23), JInt(2), d2)]
    K.check(e2[2] == 15.0 and e2[1] == 25.0 and e2[0] == 100.0, "X4: caps - Wisdom at tool.wisdom.cap 15, Fortune at tool.fortune.cap 25, power x100: %s" % e2)
    s3, d3 = tstack("Tool_Pickaxe_Iron", 23, 2, [("mpow", 20), ("mfort", 5), ("mwis", 7)], rolled=False)
    e3 = [float(x) for x in Tool.eff(JInt(1), JInt(23), JInt(2), d3)]
    K.check(abs(e3[0] - p0) < 1e-12 and abs(e3[1] - f0) < 1e-12 and e3[2] == 0.0,
            "X4: a tool document without \"tr\" (every tool before 0.2.17) works exactly like 0.2.16 (level power / Fortune, no Wisdom): %s" % e3)
    s4, d4 = tstack("Tool_Hatchet_Iron", 20, 1, [("mpow", 25), ("cpow", 10), ("ffort", 3), ("fwis", 4)])
    e4 = [float(x) for x in Tool.eff(JInt(3), JInt(20), JInt(2), d4)]
    ph = float(Tool.power(JInt(3), JInt(20), JInt(2)))
    K.check(abs(e4[0] - (1.0 + (ph - 1.0) * 1.05) * 1.10) < 1e-9 and e4[2] == 4.0,
            "X4: a hatchet counts only ITS keys (Chopping Power 10, not a stray Mining Power 25): %s" % e4)
    skills(mining=5)
    br.remove("skill:bonus:" + str(U1))
    Tool.held(U1, s1)
    stl = [float(x) for x in Tool.stats(U1, s1)]
    K.check(stl[3] == 0.0 and stl[4] == 1.0 and stl[5] == 0.0 and stl[8] == 0.0 and gsrc() is None,
            "X4: under-level (Mining 5 < Lv 23): no power, Fortune or Wisdom, nothing posted (like the level stats)")
    skills()
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    bmap = BTY.getAssetMap().getAssetMap()
    STONE, LOG = bmap.get("Rock_Stone"), bmap.get("Wood_Oak_Trunk")
    Tool.LAST.clear()
    h1 = float(Tool.onDamage(U1, s1, STONE, JFloat(0.3)))
    Tool.LAST.clear()
    h2 = float(Tool.onDamage(U1, s1, LOG, JFloat(0.3)))
    Tool.LAST.clear()
    h3 = float(Tool.onDamage(U1, s3, STONE, JFloat(0.3)))
    K.check(STONE is not None and abs(h1 - 0.3 * pw) < 1e-5 and abs(h2 - 0.3) < 1e-7 and abs(h3 - 0.3 * p0) < 1e-5,
            "X4: the REAL block hit (GearTool.onDamage on the real Rock_Stone / oak log BlockTypes): rolled pickaxe x%.4f on stone, vanilla on a log; "
            "an old pickaxe x%.4f" % (pw, p0))

    # ============================================================================ X5 tooltip + name colour
    def tip(iid, d, owner=U1):
        txt, col = AL(), AL()
        View.lines(iid, d, owner, txt, col)
        return [(str(txt.get(i)), None if col.get(i) is None else str(col.get(i))) for i in range(txt.size())]
    T1 = tip("Tool_Pickaxe_Iron", d1)
    tx = [a for a, c in T1]
    GRAY = str(Defs.C_GRAY)
    i_pow = next(i for i, a in enumerate(tx) if a.startswith("Mining Power +%d%%:" % round((pw - 1) * 100)))
    i_mod = tx.index("Mining Power: +20%")
    K.check(tx[0].startswith("Lv 23 - Requires Mining 23") and ("Mining Fortune +%s" % ("%g" % fo)) in " ".join(tx) and "Mining Wisdom +7% (more Mining XP)" in tx
            and i_pow < i_mod and "Mining Fortune: +5" in tx and "Mining Wisdom: +7%" in tx and all(c != GRAY for a, c in T1 if a.endswith(": +20%"))
            and "RARE TOOL" in tx, "X5: the rolled pickaxe tooltip - level line, the TOTAL power (hits) / Fortune / Wisdom, then the live modifier lines "
            "(white, not grey), RARE TOOL: %s" % tx)
    T3 = tip("Tool_Pickaxe_Iron", d3)
    K.check(not [a for a in (x for x, c in T3) if "Wisdom +" in a], "X5: an old (no tr) pickaxe shows no Wisdom line (it has none)")
    oldd = Roll.newDoc("Tool_Pickaxe_Iron", JInt(0), True, "test", JInt(23))
    oldd.remove("tr")
    withmods(oldd, [("dmg", 5)])
    T6 = tip("Tool_Pickaxe_Iron", oldd)
    K.check([c for a, c in T6 if a.startswith("Damage: +5")] == [GRAY], "X5: a weapon stat on an old SkyyRolls tool stays grey (it does nothing)")
    T7 = tip("Tool_Shovel_Iron", Roll.newDoc("Tool_Shovel_Iron", JInt(1), True, "test", JInt(20)))
    K.check([a for a, c in T7 if a.startswith("Digging Power +")], "X5: a shovel's power line says Digging Power")
    IDM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata")

    def namehex(stack):
        v = stack.getMetadata().get(IDM.KEY)
        return str(v.asDocument().toJson()).lower() if v is not None else ""
    n_rolled = namehex(Data.put(IS("Tool_Pickaxe_Iron", JInt(1)), d1, U1))
    n_old = namehex(Data.put(IS("Tool_Pickaxe_Iron", JInt(1)), d3, U1))
    nc = lambda j_: json.loads(j_).get("name", {}).get("color") if j_ else None
    K.check(nc(n_rolled) == str(Defs.R_HEX[2]).lower() and nc(n_old) not in (None, str(Defs.R_HEX[2]).lower()),
            "X5: GearView.apply - a rolled tool's name takes its rarity colour (Rare %s); an old tool keeps its own quality colour: %s | %s"
            % (Defs.R_HEX[2], n_rolled[:300], n_old[:300]))

    # ============================================================================ X6 reforge + level up on tools, end to end
    def count(c, iid):
        n = 0
        for i in range(int(c.getCapacity())):
            it = c.getItemStack(JShort(i))
            if it is not None and not it.isEmpty() and str(it.getItemId()) == iid:
                n += int(it.getQuantity())
        return n
    skills()
    PURSE[str(U1)] = 10 ** 6
    c6 = SIC(JShort(9))
    plain = IS("Tool_Pickaxe_Iron", JInt(1))
    c6.setItemStackForSlot(JShort(2), plain)
    K.check(Forge.docOf("Tool_Pickaxe_Iron", plain.getMetadata()) is not None and Forge.refuse(plain, Forge.docOf("Tool_Pickaxe_Iron", plain.getMetadata())) is None
            and Data.forgeable("Tool_Pickaxe_Iron") and not Data.forgeable("Tool_Hammer_Iron"),
            "X6: an old pickaxe WITHOUT any document can be reforged (docOf = a plain Normal document, written only on success)")
    del XP[:]
    lvT = int(Lvl.level("Tool_Pickaxe_Iron", None))
    cost = int(Cfg.costReforge(JInt(0), JInt(lvT)))
    r1 = Forge.reforge(c6, JInt(2), "Tool_Pickaxe_Iron", Forge.fp(plain), U1, "Tester", False, None, None)
    n1 = c6.getItemStack(JShort(2))
    dn = doc(n1)
    K.check(int(r1[0]) == 1 and count(c6, "Tool_Pickaxe_Iron") == 1 and int(n1.getQuantity()) == 1 and int(Data.num(dn, "tr", 0)) == 1
            and int(Data.rarity(dn)) == 0 and len(mods(dn)) == 1 and set(k for k, v in mods(dn)) <= FAM_KEYS[1] and int(Data.num(dn, "rfN", 0)) == 1
            and int(Lvl.level("Tool_Pickaxe_Iron", dn)) == lvT and bool(Lvl.stamped(dn)) and PURSE[str(U1)] == 10 ** 6 - cost
            and XP == [("Smithing", int(Cfg.xpReforge(JInt(0))), "gear:reforge")] and not dn.containsKey("spd"),
            "X6: reforge of the old pickaxe: coins %d taken first, ONE item before and after (no dupe), Normal kept, 1 pickaxe modifier, tr, level "
            "stamped %d, xp.reforge %d Smithing XP, no speed tier: %s" % (cost, lvT, int(Cfg.xpReforge(JInt(0))), mods(dn)))
    stale = Forge.reforge(c6, JInt(2), "Tool_Pickaxe_Iron", Forge.fp(plain), U1, "Tester", False, None, None)
    K.check(int(stale[0]) == 0 and PURSE[str(U1)] == 10 ** 6 - cost and count(c6, "Tool_Pickaxe_Iron") == 1,
            "X6: a stale fingerprint (the item changed) is refused before any coin moves")
    rr, c6r = Data.rarity(dn), None
    seen_mods = set()
    for k in range(12):
        cur = c6.getItemStack(JShort(2))
        rk = Forge.reforge(c6, JInt(2), "Tool_Pickaxe_Iron", Forge.fp(cur), U1, "Tester", False, None, None)
        seen_mods |= set(k_ for k_, v in mods(doc(c6.getItemStack(JShort(2)))))
        if int(rk[0]) != 1:
            c6r = rk[1]
    dd = doc(c6.getItemStack(JShort(2)))
    K.check(c6r is None and count(c6, "Tool_Pickaxe_Iron") == 1 and int(Data.num(dd, "rfN", 0)) == 13 and int(Data.rarity(dd)) == int(rr)
            and seen_mods == FAM_KEYS[1], "X6: 12 more reforges: every one done, rarity kept, the modifier moves inside the pickaxe pool %s, still one item"
            % sorted(seen_mods))
    skills(mining=40)
    cur = c6.getItemStack(JShort(2))
    lu = Forge.levelUp(c6, JInt(2), "Tool_Pickaxe_Iron", Forge.fp(cur), U1, "Tester", None, None)
    dl = doc(c6.getItemStack(JShort(2)))
    K.check(int(lu[0]) == 1 and int(Lvl.level("Tool_Pickaxe_Iron", dl)) == lvT + 1 and count(c6, "Tool_Pickaxe_Iron") == 1 and mods(dl) == mods(dd),
            "X6: level up works on a tool (Lv %d -> %d, modifiers kept, one item): %s" % (lvT, lvT + 1, lu[1]))
    skills()
    hamm = IS("Tool_Hammer_Iron", JInt(1))
    c6.setItemStackForSlot(JShort(4), hamm)
    p_before = PURSE[str(U1)]
    rh = Forge.reforge(c6, JInt(4), "Tool_Hammer_Iron", Forge.fp(hamm), U1, "Tester", False, None, None)
    apply(part__toolRarity="false")
    cur = c6.getItemStack(JShort(2))
    ro = Forge.reforge(c6, JInt(2), "Tool_Pickaxe_Iron", Forge.fp(cur), U1, "Tester", False, None, None)
    apply()
    K.check(int(rh[0]) == 0 and "only pickaxes, shovels, hatchets, hoes and sickles" in str(rh[1]) and int(ro[0]) == 0 and "Tool rarity is off" in str(ro[1])
            and PURSE[str(U1)] == p_before and count(c6, "Tool_Hammer_Iron") == 1,
            "X6: refused before coins - a hammer (%s); any tool while part.toolRarity is off (%s)" % (rh[1], ro[1]))
    PURSE[str(U1)] = 10
    cur = c6.getItemStack(JShort(2))
    rp = Forge.reforge(c6, JInt(2), "Tool_Pickaxe_Iron", Forge.fp(cur), U1, "Tester", False, None, None)
    K.check(int(rp[0]) == 0 and "Not enough coins" in str(rp[1]) and PURSE[str(U1)] == 10 and doc(c6.getItemStack(JShort(2))).toJson() == doc(cur).toJson(),
            "X6: not enough coins -> nothing changes")
    PURSE[str(U1)] = 10 ** 6

    # ============================================================================ X7 identify a tool document
    ud = Roll.newDoc("Tool_Hatchet_Iron", JInt(3), False, "test", JInt(20))
    md7 = BD()
    md7.put(str(Defs.DOC_KEY), ud)
    us7 = IS("Tool_Hatchet_Iron", JInt(1)).withMetadata(md7)
    c7 = SIC(JShort(4))
    c7.setItemStackForSlot(JShort(0), us7)
    K.check(Ident.refuse(us7, doc(us7)) is None and Data.mods(ud).size() == 0, "X7: an unidentified hatchet document can be identified (no modifiers yet)")
    i7 = Ident.identify(c7, JInt(0), "Tool_Hatchet_Iron", Forge.fp(us7), U1, "Tester", True, None, None)
    d7 = doc(c7.getItemStack(JShort(0)))
    K.check(int(i7[0]) == 1 and bool(Data.identified(d7)) and len(mods(d7)) == 3 and set(k for k, v in mods(d7)) == FAM_KEYS[3]
            and int(Data.num(d7, "tr", 0)) == 1 and count(c7, "Tool_Hatchet_Iron") == 1 and not d7.containsKey("spd"),
            "X7: identify (free, admin path) rolls the Legendary hatchet's 3 hatchet modifiers, tr, one item: %s" % mods(d7))
    r7 = Roll.identify("Tool_Sickle_Iron", Roll.newDoc("Tool_Sickle_Iron", JInt(2), False, "test", JInt(20)), U1)
    K.check(set(k for k, v in mods(r7)) == FAM_KEYS[5] and int(Data.num(r7, "tr", 0)) == 1, "X7: GearRoll.identify on a sickle: %s" % mods(r7))

    # ============================================================================ X8 status text
    stx = str(Tool.statusText())
    apply(part__toolRarity="false")
    stx2 = str(Tool.statusText())
    apply()
    K.check("crafted tool rarity on (boost 0 5 10 15 20 25%" in stx and "craft XP 100%" in stx and "OFF (part.toolRarity)" in stx2,
            "X8: the ready-line part: %s | %s" % (stx[-120:], stx2[-40:]))

    # ============================================================================ XM0 0.2.18 WITHOUT the Multitools jar
    GM, Mine, BoxL = P("GearMulti"), P("GearMine"), P("GearBoxL")
    MC, MI, MO = MULTI_PRE + "Copper", MULTI_PRE + "Iron", MULTI_PRE + "Onyxium"
    n0 = int(CRR.getAssetMap().getAssetMap().size())
    r0 = str(GM.replaceAll())
    K.check("not loaded" in r0 and GM.DONE.size() == 0 and int(CRR.getAssetMap().getAssetMap().size()) == n0 and int(GM.N[0]) == 0
            and Gear.item(MC) is None, "XM0: no Multitools jar -> nothing found, no recipe touched (%d recipes): %s" % (n0, r0))
    K.check(int(Data.toolFam(MC)) == 6 and int(Tool.fam(MC)) == 6 and bool(Data.isMulti(MC)) and not bool(Data.isMulti("Tool_Hatchet_Iron"))
            and bool(Data.toolRolls(MC)) and bool(Data.forgeable(MC)) and int(Tool.fam("Tool_Hatchet_Iron")) == 3 and int(Tool.row(JInt(6))) == 0,
            "XM0: a multitool id is GearTool family 6 (before its Tool_Hatchet_ prefix), rolls + reforges; a hatchet stays 3")
    FT = MULTI_PRE + "Firetine"
    K.check(not bool(Data.isMulti(FT)) and not bool(Data.multiId(FT)) and int(Data.toolFam(FT)) == 3 and int(Tool.fam(FT)) == 3
            and not bool(P("GearCfg").MULTI_SWAP) and int(Roll.toolXpPct(MC)) == 100,
            "XM0 (fix 3): only the 8 known tiers are multitools - Skyys-Modpack's %s stays a hatchet (family 3); (fix 1) before our recipe is live "
            "a multitool craft (the Multitools mod's bar recipe) pays the normal tool XP (%d%%)" % (FT, int(Roll.toolXpPct(MC))))
    apply(part__multitool="false")
    offf = (int(Data.toolFam(MC)), int(Tool.fam(MC)), str(GM.replaceAll()), sorted(pool(3, MC)))
    apply()
    K.check(offf[0] == 3 and offf[1] == 3 and "OFF (part.multitool)" in offf[2] and set(offf[3]) == FAM_KEYS[3],
            "XM0: part.multitool off -> a multitool is a plain hatchet again (the 0.2.17 view), no recipe work: %s" % (offf,))

    # ============================================================================ XM1 WITH the jar: the recipe, the salvage cap, a reload
    # its Common files (icons, models) first, as the boot does for a pack (the Item store validates the icon path)
    CAR = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry")
    FCA = JClass("com.hypixel.hytale.server.core.asset.common.asset.FileCommonAsset")
    mfs = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(MT_JAR), JClass("java.util.HashMap")())
    import hashlib
    with zipfile.ZipFile(MT_JAR) as mz_:
        for nm in mz_.namelist():
            if nm.startswith("Common/") and not nm.endswith("/"):
                CAR.addCommonAsset("IBC:Multitools", FCA(mfs.getPath("/" + nm), nm[len("Common/"):], hashlib.sha256(mz_.read(nm)).hexdigest(), None))
    mfail, mrec = E["loadpack"](MT_JAR, "IBC:Multitools", False)
    mitems = [ITEM.getAssetMap().getAsset(MULTI_PRE + t) for t in MULTI_TIERS]
    K.check(all(x is not None for x in mitems), "XM1: the Multitools jar (scratch copy) loaded as pack IBC:Multitools - its 8 items are in the real "
            "Item store (failed stores %s; %d log lines)" % (mfail, len(mrec)))
    ngm = gen_recipes(mitems)
    rid = lambda t: gid(MULTI_PRE + t)

    def sid(t):
        hits_ = [str(r.getId()) for r in list(CRR.getAssetMap().getAssetMap().values()) if r.getInput() is not None and len(r.getInput()) == 1
                 and r.getInput()[0] is not None and str(r.getInput()[0].getItemId()) == MULTI_PRE + t]
        return hits_[0] if len(hits_) == 1 else "none:%d" % len(hits_)
    SID = dict((t, sid(t)) for t in MULTI_TIERS)

    def inputs(r):
        return [(str(m.getItemId()) if m.getItemId() is not None else "res:" + str(m.getResourceTypeId()), int(m.getQuantity())) for m in r.getInput()]

    def outs(r):
        return [(str(m.getItemId()), int(m.getQuantity())) for m in (r.getOutputs() or [])]
    before = dict((t, CRR.getAssetMap().getAsset(rid(t))) for t in MULTI_TIERS)
    sal0 = dict((t, CRR.getAssetMap().getAsset(SID[t])) for t in MULTI_TIERS)
    K.check(ngm == 8 and all(before[t] is not None for t in MULTI_TIERS) and ("Ingredient_Bar_Copper", 5) in inputs(before["Copper"])
            and all(sal0[t] is not None for t in MULTI_TIERS),
            "XM1: before - the Multitools mod's own recipes (Copper: %s) and its 8 salvage recipes are live" % inputs(before["Copper"]))
    res1 = str(GM.replaceAll())
    after = dict((t, CRR.getAssetMap().getAsset(rid(t))) for t in MULTI_TIERS)
    OBJ = JClass("java.util.Objects")
    badr = []
    for t in MULTI_TIERS:
        want = [("Tool_Pickaxe_" + t, 1), ("Tool_Hatchet_" + t, 1)] + ([("Tool_Shovel_Iron", 1)] if t == "Iron" else [])
        a, b = after[t], before[t]
        if not (a is not None and inputs(a) == want and str(a.getId()) == rid(t) and OBJ.equals(a.getBenchRequirement(), b.getBenchRequirement())
                and float(a.getTimeSeconds()) == float(b.getTimeSeconds()) and bool(a.isKnowledgeRequired()) == bool(b.isKnowledgeRequired())
                and int(a.getRequiredMemoriesLevel()) == int(b.getRequiredMemoriesLevel()) and str(a.getPrimaryOutput().getItemId()) == MULTI_PRE + t
                and outs(a) == outs(b) and not a.equals(b)):
            badr.append((t, inputs(a) if a is not None else None))
    K.check(not badr and int(GM.N[0]) == 8 and "8 found, 8 recipe(s) set" in res1
            and "no craftable shovel for Crude, Copper, Thorium, Cobalt, Adamantite, Mithril, Onyxium" in res1,
            "XM1: every multitool recipe = 1 pickaxe + 1 hatchet (+ 1 Iron shovel - the only shovel a recipe makes) of its tier; same id, bench "
            "(Crude: Fieldcraft + Workbench), time, knowledge, output: %s | %s" % (badr[:2], res1))
    CFG_ = P("GearCfg")
    xp_on = int(Roll.toolXpPct(MC))
    apply(part__multitool="false")
    xp_off = (int(Roll.toolXpPct(MC)), [int(Roll.craftXp(MC, JInt(r_))) for r_ in range(5)], bool(Data.isMulti(MC)))
    apply()
    K.check(bool(CFG_.MULTI_SWAP) and xp_on == 0 and xp_off[0] == 0 and xp_off[1] == [0] * 5 and not xp_off[2],
            "XM1 (fix 1): our recipe is live -> a multitool craft pays NO Smithing XP, and still none after part.multitool is switched off mid-session "
            "(the swapped recipe stays until a restart; isMulti off = hatchet stats): %s" % (xp_off,))
    # the engine's own input check (CraftingManager.removeInputFromInventory -> ItemContainer.removeMaterials -> ItemStack.isEquivalentType =
    # same id AND same metadata) against SkyyGear tools: a recipe input with no metadata only takes a stack with NO metadata
    CMG = JClass("com.hypixel.hytale.builtin.crafting.component.CraftingManager")
    rmi = [m_ for m_ in CMG.class_.getDeclaredMethods() if str(m_.getName()) == "removeInputFromInventory" and len(m_.getParameterTypes()) == 3][0]
    rmi.setAccessible(True)
    rc_ = CRR.getAssetMap().getAsset(rid("Copper"))

    def craft_try(stacks):
        c_ = SIC(JShort(9))
        for i_, st_ in enumerate(stacks):
            c_.setItemStackForSlot(JShort(i_), st_)
        ok_ = bool(rmi.invoke(None, c_, rc_, JInt(1)))
        left = [(str(c_.getItemStack(JShort(i_)).getItemId()), c_.getItemStack(JShort(i_)).getMetadata() is not None)
                for i_ in range(9) if c_.getItemStack(JShort(i_)) is not None and not c_.getItemStack(JShort(i_)).isEmpty()]
        return ok_, left
    pd_, _x = tstack("Tool_Pickaxe_Copper", 10, 0, [], rolled=False)
    hd_, _x = tstack("Tool_Hatchet_Copper", 10, 0, [], rolled=False)
    prl, _x = tstack("Tool_Pickaxe_Copper", 10, 4, [("mpow", 20)])
    plain = [IS("Tool_Pickaxe_Copper", JInt(1)), IS("Tool_Hatchet_Copper", JInt(1))]
    t_doc, t_plain, t_mix = craft_try([pd_, hd_]), craft_try(plain), craft_try([prl, IS("Tool_Pickaxe_Copper", JInt(1)), IS("Tool_Hatchet_Copper", JInt(1))])
    K.check(not t_doc[0] and len(t_doc[1]) == 2 and t_plain[0] and t_plain[1] == [] and t_mix[0] and t_mix[1] == [("Tool_Pickaxe_Copper", True)],
            "XM1 (finding 2, VERIFIED on the engine): a rolled tool is NEVER used up - the bench input matcher needs the same metadata; BUT a "
            "SkyyGear-crafted (documented) Copper pickaxe + hatchet do NOT satisfy the multitool recipe either (doc %s | plain %s | Legendary + plain "
            "pickaxe -> the plain one is taken, the Legendary kept: %s)" % (t_doc, t_plain, t_mix))
    K.notes.append("BLOCKER: documented (crafted) tools cannot pay the multitool recipe - only never-crafted plain tools can: %s" % (t_doc,))
    res2 = str(GM.replaceAll())
    K.check(int(GM.N[0]) == 8 and "0 recipe(s) set" in res2 and "8 already set" in res2 and all(CRR.getAssetMap().getAsset(rid(t)).equals(after[t]) for t in MULTI_TIERS),
            "XM1: a second run changes nothing (idempotent - the same objects stay): %s" % res2[:120])
    # the salvage cap: what the required tools give back, from the live store
    byin = {}
    for r in list(CRR.getAssetMap().getAssetMap().values()):
        ins = r.getInput()
        if ins is not None and len(ins) == 1 and ins[0] is not None and ins[0].getItemId() is not None:
            byin.setdefault(str(ins[0].getItemId()), []).append(r)

    def allow(tools, item):
        return sum(max([0] + [sum(q for i_, q in outs(r) if i_ == item) for r in byin.get(tl, [])]) for tl in tools)
    over = []
    for t in MULTI_TIERS[:-1]:
        tl = ["Tool_Pickaxe_" + t, "Tool_Hatchet_" + t] + (["Tool_Shovel_Iron"] if t == "Iron" else [])
        s_ = CRR.getAssetMap().getAsset(SID[t])
        if s_ is None or not s_.equals(sal0[t]) or any(sum(q for i_, q in outs(s_) if i_ == it_) > allow(tl, it_) for it_, q0 in outs(s_)):
            over.append((t, outs(s_) if s_ is not None else None))
    K.check(not over and CRR.getAssetMap().getAsset(SID["Onyxium"]) is None and str(GM.SALV.get(SID["Onyxium"])) == "removed" and int(GM.N[2]) == 1,
            "XM1: the salvage cap on the REAL Multitools salvage: Crude..Mithril already give back no more than their tools (left as they are, e.g. "
            "Copper %s vs pickaxe + hatchet %d ore); Onyxium (3 ore, but its pickaxe / hatchet salvage to nothing) is REMOVED: %s"
            % (outs(sal0["Copper"]), allow(["Tool_Pickaxe_Copper", "Tool_Hatchet_Copper"], "Ore_Copper"), over))
    MQc = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    MQA = JArray(MQc)
    fid = CRR.class_.getDeclaredField("id")
    fid.setAccessible(True)
    fake = CRR(MQA([MQc(MC, None, None, JInt(1), None)]), MQc("Ore_Copper", None, None, JInt(9), None),
               MQA([MQc("Ore_Copper", None, None, JInt(9), None), MQc("Ingredient_Stick", None, None, JInt(9), None),
                    MQc("Ingredient_Bar_Gold", None, None, JInt(5), None)]), JInt(1), sal0["Copper"].getBenchRequirement(), JFloat(4.0), False, JInt(0))
    fid.set(fake, "SkyyTest_Salvage_Multi_Copper")
    lst = HAL()
    lst.add(fake)
    CRR.getAssetStore().loadAssets("Hytale:Hytale", lst)
    GM.replaceAll()
    fk = CRR.getAssetMap().getAsset("SkyyTest_Salvage_Multi_Copper")
    fko = outs(fk) if fk is not None else None
    GM.replaceAll()
    fk2 = CRR.getAssetMap().getAsset("SkyyTest_Salvage_Multi_Copper")
    K.check(fko == [("Ore_Copper", 2), ("Ingredient_Stick", 4)] and str(fk.getPrimaryOutput().getItemId()) == "Ore_Copper"
            and int(fk.getPrimaryOutput().getQuantity()) == 2 and str(GM.SALV.get("SkyyTest_Salvage_Multi_Copper")) == "capped" and fk2.equals(fk)
            and inputs(fk) == [(MC, 1)], "XM1: a synthetic over-cap salvage (9 ore, 9 sticks, 5 gold bars for a Copper multitool) is CLAMPED in the "
            "store to what a Copper pickaxe + hatchet salvage to (2 ore, 4 sticks, no gold), primary output 2 ore; a second run keeps it: %s" % fko)
    # a reloaded multitool: the engine regenerates the mod's recipe (as onItemAssetLoad does), then GearBoxL (LoadedAssetsEvent(Item), LAST)
    gen_recipes([ITEM.getAssetMap().getAsset(MC)])
    back = inputs(CRR.getAssetMap().getAsset(rid("Copper")))
    LAE = JClass("com.hypixel.hytale.assetstore.event.LoadedAssetsEvent")
    AUQ = JClass("com.hypixel.hytale.assetstore.AssetUpdateQuery")
    HM = JClass("java.util.HashMap")
    lm = HM()
    lm.put(MC, ITEM.getAssetMap().getAsset(MC))
    BoxL().accept(LAE(ITEM.class_, ITEM.getAssetMap(), lm, False, AUQ.DEFAULT))
    rel = inputs(CRR.getAssetMap().getAsset(rid("Copper")))
    lm2 = HM()
    lm2.put("Tool_Pickaxe_Iron", ITEM.getAssetMap().getAsset("Tool_Pickaxe_Iron"))
    nrun = int(GM.N[3])
    rel2 = int(GM.onLoaded(LAE(ITEM.class_, ITEM.getAssetMap(), lm2, False, AUQ.DEFAULT)))
    K.check(("Ingredient_Bar_Copper", 5) in back and rel == [("Tool_Pickaxe_Copper", 1), ("Tool_Hatchet_Copper", 1)] and rel2 == 0 and int(GM.N[3]) == nrun,
            "XM1: a reloaded Copper multitool (the engine regenerated the mod's recipe %s) gets pickaxe + hatchet again through the GearBoxL "
            "LoadedAssetsEvent(Item) listener; a reload without a multitool does nothing" % back[:2])

    # ============================================================================ XM2 the stats
    skills()
    KM = [("mpow", 20), ("cpow", 10), ("mfort", 5), ("ffort", 3), ("mwis", 4), ("fwis", 6)]
    sm, dm = tstack(MC, 15, 2, KM)
    sp_, dp_ = tstack("Tool_Pickaxe_Copper", 15, 2, KM)
    sh_, dh_ = tstack("Tool_Hatchet_Copper", 15, 2, KM)
    stm = [float(x) for x in Tool.stats(U1, sm)]
    stp = [float(x) for x in Tool.stats(U1, sp_)]
    sth = [float(x) for x in Tool.stats(U1, sh_)]
    r1 = lambda x: jround(x * 10.0) / 10.0
    K.check(len(stm) == 12 and stm[0] == 6.0 and stm[3] == 1.0 and abs(stm[4] - stp[4] * 0.85) < 1e-9 and abs(stm[9] - sth[4] * 0.85) < 1e-9
            and abs(stm[5] - r1(stp[5] * 0.70)) < 1e-9 and abs(stm[10] - r1(sth[5] * 0.70)) < 1e-9 and stm[8] == stp[8] == 4.0 and stm[11] == sth[8] == 6.0
            and stp[4] > 1.0 and sth[4] > 1.0 and stm[5] > 0.0 and stm[10] > 0.0 and stm[5] < stp[5] and stm[10] < sth[5],
            "XM2: a Rare Copper multitool Lv 15 (Mining Power +20, Chopping Power +10, Fortune +5 / +3, Wisdom 4 / 6) = a same Copper PICKAXE's Mining "
            "Power x0.85 (%.4f vs %.4f), a same HATCHET's Chopping Power x0.85 (%.4f vs %.4f), Fortune x0.70 (%.1f vs %.1f, %.1f vs %.1f), Wisdom in "
            "full - each side its own modifiers" % (stm[4], stp[4], stm[9], sth[4], stm[5], stp[5], stm[10], sth[5]))
    br.remove("skill:bonus:" + str(U1))
    Tool.LAST.clear()
    Tool.held(U1, sm)
    g = gsrc()
    K.check(g is not None and abs(g["dd.mining"] - stm[5] / 100.0) < 1e-9 and g["only.mining"] == "Rock_,Rubble_,Ore_" and abs(g["dd.foraging"] - stm[10] / 100.0) < 1e-9
            and abs(g["xp.mining"] - 0.04) < 1e-9 and abs(g["xp.foraging"] - 0.06) < 1e-9 and "only.foraging" not in g and bool(Mine.toolHeld(U1)),
            "XM2: held() posts BOTH rows in the gear source (dd.mining + the pickaxe's rock / ore filter, dd.foraging, xp.mining, xp.foraging); "
            "GearMine sees a pickaxe in hand (Mining Sets count): %s" % g)
    Tool.LAST.clear()
    hs = float(Tool.onDamage(U1, sm, STONE, JFloat(0.3)))
    Tool.LAST.clear()
    hl = float(Tool.onDamage(U1, sm, LOG, JFloat(0.3)))
    SOIL = bmap.get("Soil_Dirt")
    Tool.LAST.clear()
    hd = float(Tool.onDamage(U1, sm, SOIL, JFloat(0.3)))
    Tool.LAST.clear()
    hp_ = float(Tool.onDamage(U1, sp_, STONE, JFloat(0.3)))
    K.check(abs(hs - 0.3 * stm[4]) < 1e-5 and abs(hl - 0.3 * stm[9]) < 1e-5 and SOIL is not None and abs(hd - 0.3) < 1e-7 and hs < hp_,
            "XM2: the REAL block hits - stone x%.4f (the Copper pickaxe hits x%.4f), oak log x%.4f, dirt vanilla" % (stm[4], stp[4], stm[9]))
    skills(mining=49, foraging=5)
    br.remove("skill:bonus:" + str(U1))
    Tool.LAST.clear()
    Tool.held(U1, sm)
    stu = [float(x) for x in Tool.stats(U1, sm)]
    gc = list(Gate.check(U1, MC, dm, JInt(15)))
    Tool.LAST.clear()
    hu = float(Tool.onDamage(U1, sm, STONE, JFloat(0.3)))
    skills(mining=5, foraging=49)
    stu2 = [float(x) for x in Tool.stats(U1, sm)]
    skills()
    K.check(stu[3] == 0.0 and stu[4] == 0.85 and stu[9] == 0.85 and stu[5] == 0.0 and stu[10] == 0.0 and gsrc() is None and abs(hu - 0.3 * 0.85) < 1e-6
            and not bool(gc[0]) and str(gc[1]) == "Mining + Foraging" and int(gc[3]) == 5 and not bool(gc[4]) and stu2[3] == 0.0,
            "XM2: under level (Foraging 5 or Mining 5 < Lv 15 - it needs BOTH): no bonus, no Fortune / Wisdom posted, the speed share stays "
            "(x0.85, never faster than a single tool); the gate says Mining + Foraging (you: 5), never enforced: %s" % gc)
    apply(multi__speedPct="50", multi__fortunePct="100")
    sth2 = [float(x) for x in Tool.stats(U1, sm)]
    apply(part__tools="false")
    Tool.LAST.clear()
    hoff = float(Tool.onDamage(U1, sm, STONE, JFloat(0.3)))
    stoff = [float(x) for x in Tool.stats(U1, sm)]
    apply()
    K.check(abs(sth2[4] - stp[4] * 0.5) < 1e-9 and abs(sth2[5] - r1(stp[5])) < 1e-9 and abs(hoff - 0.3) < 1e-7 and stoff[4] == 1.0 and stoff[9] == 1.0,
            "XM2: the rows are live (speed 50%% -> x%.4f, Fortune 100%% = the pickaxe's); part.tools off -> a plain vanilla multitool" % sth2[4])

    # ============================================================================ XM3 rarity on craft, the 6-key pool, no craft XP
    pm_ = set(pool(3, MC))
    seenm, badm = set(), []
    for k in range(300):
        d_ = Roll.craftDoc(MC, U1, JInt(15))
        ks = [k_ for k_, v in mods(d_)]
        seenm |= set(ks)
        if not set(ks) <= MULTI_KEYS or int(Data.rarity(d_)) > 4 or int(Data.num(d_, "tr", 0)) != 1 or d_.containsKey("spd") or len(ks) != len(set(ks)):
            badm.append(ks)
    del XP[:]
    pcm = list(Roll.payCraft(U1, MC, " normal rare", "Tester"))
    K.check(pm_ == MULTI_KEYS and seenm == MULTI_KEYS and not badm and [int(Roll.craftXp(MC, JInt(r))) for r in range(5)] == [0] * 5
            and int(Roll.toolXpPct(MC)) == 0 and int(pcm[1]) == 0 and XP == [] and float(Roll.spare(JInt(3), JInt(5), JInt(6))) == 0.0,
            "XM3: the multitool pool = pickaxe + hatchet pools %s; 300 crafts roll only those (every one seen), a rarity Normal..Fabled, tr, no speed "
            "tier; assembling pays NO Smithing XP (craftXp 0, payCraft %s)" % (sorted(pm_), pcm))

    # ============================================================================ XM4 reforge + level up on a multitool, end to end
    skills()
    PURSE[str(U1)] = 10 ** 6
    cm = SIC(JShort(9))
    cm.setItemStackForSlot(JShort(3), sm)
    seen4, ok4 = set(), True
    for k in range(10):
        cur = cm.getItemStack(JShort(3))
        rr4 = Forge.reforge(cm, JInt(3), MC, Forge.fp(cur), U1, "Tester", False, None, None)
        d4 = doc(cm.getItemStack(JShort(3)))
        ks = [k_ for k_, v in mods(d4)]
        seen4 |= set(ks)
        ok4 = ok4 and int(rr4[0]) == 1 and count(cm, MC) == 1 and int(Data.rarity(d4)) == 2 and len(ks) == R_MODS[2] and set(ks) <= MULTI_KEYS
    skills(mining=40, foraging=40)
    cur = cm.getItemStack(JShort(3))
    lv4 = int(Lvl.level(MC, doc(cur)))
    lu4 = Forge.levelUp(cm, JInt(3), MC, Forge.fp(cur), U1, "Tester", None, None)
    skills()
    K.check(ok4 and len(seen4) >= 5 and int(lu4[0]) == 1 and int(Lvl.level(MC, doc(cm.getItemStack(JShort(3))))) == lv4 + 1 and count(cm, MC) == 1
            and Forge.refuse(cur, doc(cur)) is None,
            "XM4: 10 reforges of a Rare multitool: each done for coins, one item, rarity kept, %d modifiers from the 6-key pool (seen %s); level up "
            "Lv %d -> %d (Skyy: 'tools should be reforge able too')" % (R_MODS[2], sorted(seen4), lv4, lv4 + 1))

    # ============================================================================ XM5 craft level, tooltip, status
    skills(mining=30, foraging=12)
    ch = int(Roll.craftHave(MC, U1))
    cl5 = str(Roll.craftLabel(MC, U1))
    skills()
    T5 = tip(MC, dm)
    t5 = [a for a, c in T5]
    skills(mining=49, foraging=5)
    T6 = [a for a, c in tip(MC, dm)]
    skills()
    mpl = [a for a in t5 if a.startswith("Mining Power ")]
    cpl = [a for a in t5 if a.startswith("Chopping Power ")]
    K.check(ch == 12 and cl5 == "Mining + Foraging" and t5[0].startswith("Lv 15 - Requires Mining + Foraging 15") and len(mpl) == 1 and len(cpl) == 1
            and "per stone (plain pickaxe" in mpl[0] and "per log (plain hatchet" in cpl[0]
            and ("Mining Fortune +%s" % ("%g" % stm[5])) in " ".join(t5) and ("Foraging Fortune +%s" % ("%g" % stm[10])) in " ".join(t5)
            and "Mining Wisdom +4% (more Mining XP)" in t5 and "Foraging Wisdom +6% (more Foraging XP)" in t5
            and "Multitool: slightly slower and less Fortune than a single tool" in t5 and "No bonus until Mining + Foraging 15" in T6
            and T6[0].endswith("(you: 5)"),
            "XM5: a craft stamps the level from the LOWER skill (Mining 30, Foraging 12 -> %d, label %s); the tooltip shows BOTH stat sets + the "
            "trade-off line; under level: 'No bonus until Mining + Foraging 15', '(you: 5)': %s" % (ch, cl5, t5[:9]))
    stx3 = str(Tool.statusText())
    K.check("multitools on (speed 85%, Fortune 70% of a single tool" in stx3 and "8 found" in str(GM.LAST), "XM5: status text: %s | %s" % (stx3[-110:], str(GM.LAST)[:160]))
    K.notes.append("XM GearMulti.LAST: %s" % str(GM.LAST))
    K.save()


# ====================================================================================================== C: class compare
def run_compare(out):
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

    def members(p_, cn, vers):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())

        def code(b_):
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
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_

    pa, pb = pool_of(OLD_JAR), pool_of(JAR)
    na, nb = jar_classes(OLD_JAR), jar_classes(JAR)
    ns_a = int(pa.get(PKG + "GearDefs").getField("NS").getConstantValue())
    ns_b = int(pb.get(PKG + "GearDefs").getField("NS").getConstantValue())
    K.check(ns_a == ns_b == 50, "C: GearDefs.NS stays 50 (no stat row added): %d -> %d" % (ns_a, ns_b))
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn, ("0.2.17", "0.2.18")), members(pb, cn, ("0.2.17", "0.2.18"))
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd]
    add = sorted(c[len(PKG):] for c in set(nb) - set(na))
    gone = sorted(c[len(PKG):] for c in set(na) - set(nb))
    print("C. class compare 0.2.17 -> 0.2.18: + %s - %s" % (add, gone))
    for k in sorted(diffs):
        print("   %-16s %s" % (k, ", ".join(diffs[k])[:900]))
    K.check(add == ["GearMulti"] and not gone, "C: one class added (GearMulti), none removed: + %s - %s" % (add, gone))
    unexpected = sorted(set(diffs) - EXPECT_CHANGED)
    missing = sorted(EXPECT_CHANGED - set(diffs))
    K.check(not unexpected and not missing, "C: exactly the listed classes changed (unexpected %s, listed but unchanged %s)" % (unexpected, missing))
    want = {"GearData": {"+m isMulti", "+m multiId", "~m toolFam"},
            "GearGate": {"+m haveBoth", "+m checkMulti", "~m check"},
            "GearRoll": {"~m craftHave", "~m craftLabel", "~m toolXpPct"},
            "GearTool": {"+m r1", "+m mstats", "+m mpost", "+m mdamage", "+m mpowLine", "+m mlines", "~m fam", "~m row", "~m gate", "~m stats",
                         "~m held", "~m onDamage", "~m lines", "~m statusText", "~<clinit>"},
            "GearMine": {"~m toolHeld"}, "GearBoxL": {"~m accept"},
            "GearDefs": {"+f MULTI_PRE", "+f MULTI_T", "~<clinit>"}}
    bad = {}
    for k, v in want.items():
        got = set(diffs.get(k, []))
        if got != v:
            bad[k] = (sorted(v - got), sorted(got - v))
    K.check(not bad, "C: the classes changed exactly where the patch says (missing / extra): %s" % bad)
    cfg = set(diffs.get("GearCfg", []))
    K.check({"+m migrate0218", "+m mtUpdate", "~m apply", "+f MULTI_ON", "+f MULTI_SPD", "+f MULTI_FORT", "+f MT_GL", "~<clinit>", "~m defaultsText"} <= cfg
            and all(x.startswith("+") or x in ("~m apply", "~<clinit>", "~m defaultsText") for x in cfg),
            "C: GearCfg gains the update + the 3 row fields (only apply + clinit + the fresh text change): %s" % sorted(cfg))
    K.check(set(diffs.get("CfgRows", [])) == {"~<clinit>"} and set(diffs.get("CfgFile", [])) == {"~<clinit>"}, "C: CfgRows / CfgFile: only the row tables")
    pl = set(diffs.get("SkyyGearPlugin", []))
    K.check(pl and all(x.startswith("~") for x in pl), "C: SkyyGearPlugin: the version + the migrate0218 / GearMulti.start calls only: %s" % sorted(pl))
    K.save(diffs=diffs)


# ====================================================================================================== D: the one-time update
def run_update(out, home):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR], verify=True)
    Cfg = JClass(PKG + "GearCfg")
    Path = JClass("java.nio.file.Paths")
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(SCRATCH, "d-gear.log"))
    fresh = str(Cfg.defaultsText())
    K.check(Cfg.mtUpdate(fresh) is None and Cfg.trUpdate(fresh) is None and Cfg.ubUpdate(fresh) is None and Cfg.gmUpdate(fresh) is None
            and Cfg.guUpdate(fresh) is None, "D: a fresh 0.2.18 file carries the 0.2.14 - 0.2.18 markers")
    old = open(os.path.join(home, "config.properties"), "rb").read().decode("latin-1")
    BLOCK = fresh[fresh.index(MT_HEAD):]
    K.check("part.multitool" not in old and "multi.speedPct" not in old, "D: the live copy has no 0.2.18 key yet")
    base = old
    for nm in ("guUpdate", "gmUpdate", "ubUpdate", "trUpdate"):
        rr = getattr(Cfg, nm)(base)
        if rr is not None:
            base = str(rr[0])
            K.notes.append("D: the live copy lacked the %s block (added first, like the setup order)" % nm)

    def upd(text):
        r = Cfg.mtUpdate(text)
        return None if r is None else (str(r[0]), [str(x) for x in r[1]], str(r[2]))
    r = upd(base)
    exp = base + "\n" + BLOCK if base.endswith("\n") else None
    K.check(r is not None and exp is not None and r[0] == exp and r[1] == [] and r[2] == "part.multitool, multi.speedPct, multi.fortunePct",
            "D: the live file: the block appended = exactly the fresh file's block (3 keys), nothing else changed: %s" % (r[2] if r else None))
    K.check(upd(r[0]) is None, "D: the updated text carries the marker (run once)")
    rc = upd(base.replace("\n", "\r\n"))
    K.check(rc is not None and rc[0] == exp.replace("\n", "\r\n"), "D: a CRLF file keeps CRLF on every line (block included)")
    rn = upd(base.rstrip("\n"))
    K.check(rn is not None and rn[0] == exp.rstrip("\n"), "D: a file without a final newline: the block after its last line, still no final newline")
    hand = base + "multi.speedPct=60\n"
    rh = upd(hand)
    K.check(rh is not None and rh[0].count("multi.speedPct=") == 1 and "multi.speedPct=60" in rh[0] and len(rh[1]) == 1 and "multi.fortunePct=70" in rh[0]
            and rh[2] == "part.multitool, multi.fortunePct", "D: a key already in the file is KEPT + noted, the rest added: %s" % (rh[1] if rh else None))
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    files0 = sorted(os.path.relpath(os.path.join(a, f), home) for a, d, fs in os.walk(home) for f in fs)
    log0 = open(os.path.join(home, "config-changes.log"), "rb").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else b""
    snaps = []
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214",
                  "migrate0215", "migrate0216", "migrate0217", "migrate0218"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(os.path.join(home, "config.properties"), "rb").read())
        K.check(bool(Cfg.MULTI_ON) and int(Cfg.MULTI_SPD) == 85 and int(Cfg.MULTI_FORT) == 70 and bool(Cfg.TOOL_RAR), "D start %d: the loaded multitool rows" % step)
    K.check(snaps[0] == exp.encode("latin-1"), "D start 1: the live copy = the expected text byte for byte")
    K.check(snaps[1] == snaps[0], "D start 2: nothing changes")
    files1 = sorted(os.path.relpath(os.path.join(a, f), home) for a, d, fs in os.walk(home) for f in fs)
    newf = sorted(set(files1) - set(files0))
    hb = [open(os.path.join(home, f), "rb").read() for f in newf if f.startswith("config-history")]
    K.check(any(b == base.encode("latin-1") for b in hb) and all(f.startswith("config-history") for f in newf)
            and all(f.startswith("config-history") for f in set(files0) - set(files1)),
            "D: the History copy before 0.2.18 holds the bytes it saw; only config-history files were added (the kit prunes past KEEP): %s" % newf)
    log1 = open(os.path.join(home, "config-changes.log"), "rb").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else b""
    addl = [x for x in log1[len(log0):].decode("utf-8", "replace").split("\n") if x.strip()]
    K.check(log1.startswith(log0) and not [x for x in addl if "0.2.18" in x],
            "D: no config-changes.log row from 0.2.18 (a pure addition - no value changed): %s" % addl)
    K.save()


# ====================================================================================================== parent
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--old", OLD_JAR], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, n))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: H["run_mkfake"](arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--engine", lambda: run_engine(arg("--out"))), ("--compare", lambda: run_compare(arg("--out"))),
                     ("--update", lambda: run_update(arg("--out"), arg("--update"))), ("--audit", lambda: H["run_audit"](arg("--out")))):
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
    assert os.path.isfile(JAR) and os.path.isfile(OLD_JAR), (JAR, OLD_JAR)
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    with zipfile.ZipFile(OLD_JAR) as z_:
        assert '"Version": "0.2.17"' in z_.read("manifest.json").decode("utf-8"), "the old jar is not 0.2.17"
    assert os.path.isfile(MT_SRC), "the Multitools jar is needed for XM1: " + MT_SRC
    os.makedirs(os.path.dirname(MT_JAR), exist_ok=True)
    shutil.copyfile(MT_SRC, MT_JAR)          # read-only source; the children load the scratch copy
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        run_assets()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("engine", "--engine"), ("compare", "--compare")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        home = os.path.join(SCRATCH, "live")
        shutil.copytree(LIVE_DIR, home)
        print("D. live Skyy_SkyyGear copied (read-only source %s)" % LIVE_DIR)
        out = os.path.join(SCRATCH, "update.json")
        pr = child(env, "--update", home, "--out", out)
        check(pr.returncode == 0, "D: the child exited cleanly")
        take(out, "update")
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, 0 refused, control refused" % (a["refs"], a["classes"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
