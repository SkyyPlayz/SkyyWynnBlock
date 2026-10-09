"""Harness for SkyyGear 0.2.14 (Untiered / Mythic / Set, phase G1 of research/cloud/Untiered-Mythic-Spec.md) + the market wall in the partner
mods (SkyyAuctions 0.1.3 unchanged, SkyyMerchants 0.1 unchanged, SkyyBazaar 0.1.7). Build first:
    python tools/gear_0_2_14_patch.py && python SkyyGear/build_skyygear_0.2.14.py
    python tools/bazaar_0_1_7_patch.py && (cd SkyyBazaar && python build_skyybazaar_0.1.7.py)

    python SkyyGear/test_skyygear_0.2.14.py [--jar <SkyyGear-0.2.14.jar>] [--old <SkyyGear-0.2.13.jar>] [--dir <scratch>] [--keep]

The 0.2.11 harness's helpers (stand-ins F, verify A, the bare-server boot of V, the engine-access audit AA) are loaded from
SkyyGear/test_skyygear_0.2.11.py and run on the 0.2.14 jar (the 0.2.12 / 0.2.13 harnesses do the same).
  S  THE ASSETS (python): the 8th quality asset Skyy_Gear_Untiered (#ffaa00, the vanilla Legendary frame, the vanilla field set), its lang line,
     the orange bag item + its two generated textures; every other non-class entry of 0.2.13 byte-identical; the Bazaar jar: manifest only
  A  every class of both new jars loads + verifies (-Xverify:all)
  V  the vanilla pack store by store + THE JAR as its own pack: no failed store of its own; the ENGINE ASSET VALIDATORS took the new quality
     asset (ItemQuality store: Skyy_Gear_Untiered, its colour) and the orange bag item (its quality = that asset)
  X  EVERY NEW CODE PATH EXECUTED on the real Item store (-Xverify:all): X1 every rarity incl. Untiered renders (quality index, name colour,
     footer, trade-off line); X2 Mythic never rolls (1e5 rolls per odds column + the bag roll + the Smithing step-up at 100 %, a hand-edited
     file too) + the checks; X3 the level-up caps per rarity (+ the reforge.levelCap fallback); X4 the set check (0-4 pieces, swap mid-wear,
     mixed sets, unidentified pieces, part.stats off, totals + the Health lock, the tooltip block, /gear set, the inventory scan); X5 the
     orange bag (empty table + placeholder table: make, refuse before coins, identify with coins, re-identify, /gear box, gear:fn:box, the pool
     exclusion, newDoc / the legacy stamp, the reforge refusal); X6 the market wall + gear:fn:tradeable; X7 gear:fn:grant; X8 the kit checks
  M  THE MARKET WALL IN EACH PARTNER MOD (their real jars in the same JVM): SkyyAuctions 0.1.3 AhItem.tradeable refuses, SkyyMerchants 0.1
     MerchWall.why refuses, SkyyBazaar 0.1.7 Inv (veto / wallId / countIn / take) skips walled stacks; 0.1.6 control counts them
  C  CLASS COMPARE 0.2.13 -> 0.2.14 and SkyyBazaar 0.1.6 -> 0.1.7 (javassist members): only the listed classes / members differ
  D  THE ONE-TIME UPDATE: synthetic files (fresh, LF / CRLF, no final newline, hand-edited odds.mythic + reforge.levelCap, block keys already
     there) + START TWICE on a scratch COPY of the live Skyy_SkyyGear folder (rewrite, block, History copy, change-log row; the 2nd start
     changes nothing)
  AA THE ENGINE-ACCESS AUDIT
Scratch: tools/dev/scratch/rar01/gear (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.14"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "rar01")))     # --root: another task folder under tools/dev/scratch
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "gear")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-0.2.13.jar")))      # read only
AH_JAR = os.path.join(ROOT, "SkyyAuctions", "SkyyAuctions-0.1.3.jar")
MER_JAR = os.path.join(ROOT, "SkyyMerchants", "SkyyMerchants-0.1.jar")
BZ_JAR = os.path.join(ROOT, "SkyyBazaar", "SkyyBazaar-0.1.7.jar")
BZ_OLD = os.path.join(ROOT, "SkyyBazaar", "SkyyBazaar-0.1.6.jar")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
PKG = "com.skyy.gear."
ASSETS = os.path.join(os.path.dirname(B.SERVER_JAR), "..", "Assets.zip")
REASON = "Mythic, Untiered and Set gear never goes on the market - trade it directly with another player."
NEW_CLASSES = ["GearSet", "GearSetCmd", "GearUt", "GearWall"]
EXPECT_CHANGED = {"GearAdmin", "GearArmor", "GearBoxFn", "GearCfg", "GearCmd", "GearData", "GearDefs", "GearFn", "GearForge", "GearFx", "GearGiveCmd",
                  "GearPool", "GearRoll", "GearStamp", "GearStats", "GearUnid", "GearView", "ReforgePage", "SkyyGearPlugin",
                  # javassist inlines GearDefs.NR (7 -> 8: the 8th rarity) / the kit's row count (+2 rows: ut, set, levelUp.cap in, reforge.levelCap out)
                  "GearQual", "IdentifyPage", "CfgFile", "CfgRows"}
# members whose ONLY change is the inlined rarity count (bipush 7 -> bipush 8), checked instruction by instruction
NR_ONLY = [("GearQual", "parse"), ("GearQual", "text"), ("GearQual", "damaged"), ("IdentifyPage", "detail"), ("GearCfg", "importRolls")]

# ---- the 0.2.11 harness's helpers, run on THIS jar (its module text without its main call)
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


# ====================================================================================================== S: the assets (python)
def run_assets():
    zo, zn, za = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR), zipfile.ZipFile(ASSETS)
    q = json.loads(zn.read("Server/Item/Qualities/Skyy_Gear_Untiered.json"))
    van = json.loads(za.read("Server/Item/Qualities/Common.json").decode("utf-8-sig"))
    check(set(q) == set(van) and q["TextColor"] == "#ffaa00" and q["QualityValue"] == 7 and "Legendary" in q["ItemTooltipTexture"]
          and q["ItemEntityConfig"]["ParticleSystemId"] == "Drop_Legendary" and q["LocalizationKey"] == "server.general.qualities.Skyy_Gear_Untiered",
          "S: the 8th quality asset Skyy_Gear_Untiered: #ffaa00, QualityValue 7 (never 8+ = technical), the Legendary frame + glow, the vanilla field set: %s" % q)
    for k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture"):
        check(("Common/" + q[k]) in za.namelist() or ("Common/" + q[k][:-4] + "@2x.png") in za.namelist(), "S: the quality's %s is a vanilla texture (%s)" % (k, q[k]))
    lang = zn.read("Server/Languages/en-US/server.lang").decode("utf-8")
    check("general.qualities.Skyy_Gear_Untiered = Untiered" in lang and "items.Skyy_Unid_Bag_Untiered.name = Untiered Mystery Bag" in lang,
          "S: the lang lines of the quality + the orange bag")
    bag = json.loads(zn.read("Server/Item/Items/SkyyGear/Skyy_Unid_Bag_Untiered.json"))
    check(bag["Quality"] == "Skyy_Gear_Untiered" and bag["MaxStack"] == 1 and bag["Variant"] is True and bag["Tags"] == {"Type": ["Unidentified"]}
          and "Weapon" not in bag and "Armor" not in bag and "Recipe" not in bag, "S: the orange bag item: its quality, MaxStack 1, hidden, no use / recipe")
    for n in ("Common/Items/SkyyGear/Unid/Bag_Untiered.png", "Common/Icons/ItemsGenerated/Skyy_Unid_Bag_Untiered.png"):
        check(n in zn.namelist() and n not in za.namelist() and zn.read(n)[:8] == b"\x89PNG\r\n\x1a\n", "S: the generated bag texture %s (never a vanilla path)" % n)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(eb) - set(ea))
    gone = sorted(set(ea) - set(eb))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    check(added == ["Common/Icons/ItemsGenerated/Skyy_Unid_Bag_Untiered.png", "Common/Items/SkyyGear/Unid/Bag_Untiered.png",
                    "Server/Item/Items/SkyyGear/Skyy_Unid_Bag_Untiered.json", "Server/Item/Qualities/Skyy_Gear_Untiered.json"] and not gone
          and changed == ["Server/Languages/en-US/server.lang", "manifest.json"],
          "S: non-class entries 0.2.13 -> 0.2.14: + the quality / bag files, ~ server.lang + manifest only: + %s - %s ~ %s" % (added, gone, changed))
    lo, ln = zo.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines(), lang.splitlines()
    check(sorted(set(ln) - set(lo)) == sorted(["general.qualities.Skyy_Gear_Untiered = Untiered", "items.Skyy_Unid_Bag_Untiered.name = Untiered Mystery Bag",
                                               "items.Skyy_Unid_Bag_Untiered.description = Unidentified gear - identify it (/identify) to find out what is inside."])
          and not set(lo) - set(ln), "S: server.lang only gains the 3 new lines")
    bo, bn = zipfile.ZipFile(BZ_OLD), zipfile.ZipFile(BZ_JAR)
    xo = dict((n, bo.read(n)) for n in bo.namelist() if not n.endswith(".class"))
    xn = dict((n, bn.read(n)) for n in bn.namelist() if not n.endswith(".class"))
    check(sorted(set(xo) ^ set(xn)) == [] and sorted(n for n in xo if xo[n] != xn[n]) == ["manifest.json"] and b'"0.1.7"' in xn["manifest.json"],
          "S: SkyyBazaar 0.1.7 non-class entries: only manifest.json (0.1.7)")
    print("S. assets: the quality asset + 3 bag files added, server.lang +3 lines; SkyyBazaar: manifest only")


# ====================================================================================================== A: verify the Bazaar jar too
def run_verify_bz(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, BZ_JAR], verify=True)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = jar_classes(BZ_JAR)
    for n in names:
        try:
            Cls.forName(n, True, loader)
            K.ok += 1
        except Exception as e:
            K.check(False, "A: load + verify %s: %s" % (n, str(e)[:300]))
    K.notes.append("A: SkyyBazaar 0.1.7: %d classes loaded + initialised with -Xverify:all" % len(names))
    K.save()


# ====================================================================================================== V + X + M (the engine child)
def run_engine(out):
    from jpype import JClass, JArray, JInt, JLong, JShort, JFloat, JImplements, JOverride, JObject, JBoolean, JString
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR, AH_JAR, MER_JAR, BZ_JAR], verify=True, big=True)
    E = H["engine_boot"](K)
    ITEM, us, jf = E["ITEM"], E["us"], E["jf"]
    K.check(set(E["fail"]) <= set(E["vfail"]), "V: the jar as its own pack: no failed store of its own (%s vs vanilla %s)" % (E["fail"], E["vfail"]))
    ours = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and ("Untiered" in r[1] or "Skyy_Gear" in r[1] or "Skyy_Unid_Bag" in r[1])]
    K.check(not ours, "V: no SEVERE / WARNING about the quality assets or the bags: %s" % ours[:3])
    IQ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality")
    qi = int(IQ.getAssetMap().getIndex("Skyy_Gear_Untiered"))
    qa = IQ.getAssetMap().getAsset(JInt(qi)) if qi >= 0 else None
    K.check(qa is not None and str(qa.getId()) == "Skyy_Gear_Untiered", "V: the engine's ItemQuality store took Skyy_Gear_Untiered (validators passed): index %d" % qi)
    bagi = ITEM.getAssetMap().getAsset("Skyy_Unid_Bag_Untiered")
    K.check(bagi is not None and int(bagi.getQualityIndex()) == qi, "V: the orange bag item is loaded with that quality (%s)" % (bagi.getQualityIndex() if bagi else None))
    P = lambda n: JClass(PKG + n)
    (Cfg, Defs, Data, Roll, Unid, Pool, Ut, Set, Wall, Fn, Stats, Armor, Forge, Ident, View, Stamp, Lvl, Gate, BoxFn, Admin, Gear) = [
        P(n) for n in ("GearCfg", "GearDefs", "GearData", "GearRoll", "GearUnid", "GearPool", "GearUt", "GearSet", "GearWall", "GearFn", "GearStats",
                       "GearArmor", "GearForge", "GearIdent", "GearView", "GearStamp", "GearLevel", "GearGate", "GearBoxFn", "GearAdmin", "Gear")]
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    BD = JClass("org.bson.BsonDocument")
    BS = JClass("org.bson.BsonString")
    Props = JClass("java.util.Properties")
    UUID = JClass("java.util.UUID")
    AL = JClass("java.util.ArrayList")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    OA = JArray(JClass("java.lang.Object"))
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000a014")
    R_MY, R_SET, R_UT = int(Defs.R_MY), int(Defs.R_SET), int(Defs.R_UT)
    K.check((R_MY, R_SET, R_UT, int(Defs.NR)) == (5, 6, 7, 8) and [str(x) for x in Defs.R_ID][7] == "untiered" and str(Defs.R_HEX[7]) == "#FFAA00",
            "X0: 8 rarities, Untiered = index 7, #FFAA00")
    K.check("untiered:Untiered:#FFAA00" in str(Defs.TIERS), "X0: gear:tiers (the Auction House rarity filter) lists Untiered: %s" % Defs.TIERS)
    PURSE = {}

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
    br.put("coins:fn:get", CoinGet())
    br.put("coins:fn:take", CoinTake())
    br.put("coins:fn:add", CoinAdd())

    def props(**kv):
        p = Props()
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        return p

    def apply(p, from_file=False):     # False = the built-in level bands stay (these test files carry no level.material rows)
        Cfg.apply(p, from_file)
        Pool.TAB = None

    def jl(xs):
        return [str(x) for x in xs] if xs is not None else []

    def doc(s):
        return Data.effective(s.getItemId(), s.getMetadata())

    PH = props(ut__Weapon_Sword_Bronze="10,20,Placeholder: hits slowly", ut__Armor_Steel_Chest="15,25", ut__Weapon_Nope_Nothing="1,5")
    apply(Props(), False)

    # ============================================================================ X1 every rarity renders (incl. Untiered: a table id)
    apply(PH)
    rend = {}
    for r in range(8):
        iid = "Weapon_Sword_Bronze" if r == R_UT else "Weapon_Sword_Copper"
        d = Roll.newDoc(iid, JInt(r), True, "test", JInt(15 if r == R_UT else 12))
        s = Data.put(IS(iid, JInt(1)), d, U1)
        md = s.getMetadata()
        qn = str(Defs.qName(JInt(int(Gear.quality(s)))))
        ln = jl(View.plain(iid, d, U1))
        rend[r] = (int(Data.rarity(d)), qn, md.containsKey("SkyyGearView") and md.containsKey(str(JClass("com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata").KEY)), ln)
    okr = all(rend[r][0] == r and rend[r][1] == "Skyy_Gear_" + str(Defs.R_NAME[r]) and rend[r][2] for r in range(8))
    K.check(okr, "X1: every rarity incl. Untiered renders (its rarity, the Skyy_Gear_<Name> quality, the tooltip + view marker): %s"
            % dict((r, rend[r][:3]) for r in rend))
    utl = rend[R_UT][3]
    K.check(any(x.startswith("UNTIERED ") for x in utl) and "Placeholder: hits slowly" in utl and not any(x.startswith("Rarity:") for x in utl),
            "X1: the Untiered tooltip: the trade-off line + the UNTIERED footer: %s" % utl)
    dch = Roll.newDoc("Armor_Steel_Chest", JInt(1), True, "test", JInt(18))
    K.check("Untiered - fixed stats." in jl(View.plain("Armor_Steel_Chest", dch, U1)), "X1: a table row without a trade-off text shows 'Untiered - fixed stats.'")
    K.check(int(Data.rarity(Roll.newDoc("Weapon_Sword_Copper", JInt(R_UT), True, "t", JInt(12)))) == 0, "X1: newDoc never makes a non-table id Untiered (-> Normal)")
    dutl = Roll.newDoc("Weapon_Sword_Bronze", JInt(2), True, "t", JInt(50))
    K.check(int(Data.rarity(dutl)) == R_UT and int(Lvl.level("Weapon_Sword_Bronze", dutl)) == 20 and Data.mods(dutl).size() == 0,
            "X1: newDoc makes a table id Untiered whatever was asked, its level inside the row (50 -> 20), no modifiers (fixed stats)")

    # ============================================================================ X2 Mythic never rolls
    apply(Props(), False)
    N = 100000
    cnt = {}
    for col in (0, 1, 2):
        c = [0] * 8
        for _ in range(N):
            c[int(Roll.pickRarity(JInt(col)))] += 1
        cnt[col] = c
    K.check(all(cnt[col][R_MY] == 0 and cnt[col][R_UT] == 0 and cnt[col][R_SET] == 0 for col in cnt) and cnt[1][4] > 0 and cnt[2][4] > 0,
            "X2: 1e5 rolls per odds column (craft / mob / chest): never Mythic / Untiered / Set, Fabled still rolls: %s" % cnt)
    cb = [0] * 8
    for L in range(1, 50):
        for _ in range(N // 49):
            cb[int(Unid.rarity(JInt(1), JInt(L)))] += 1
        cb[int(Unid.rarity(JInt(2), JInt(21)))] += 1
    K.check(cb[R_MY] == 0 and cb[R_UT] == 0 and cb[4] > 0, "X2: 1e5 mystery-bag rolls (mob odds + the level boost Lv 1-49, chest tier IV): never Mythic / Untiered: %s" % cb)
    Gate.entry(U1)[2].put("Smithing", JObject(100, JClass("java.lang.Integer")))
    Cfg.SMITH_PER, Cfg.SMITH_CAP = 100.0, 100.0
    cc = [0] * 8
    for _ in range(N):
        cc[int(Roll.craftRarity(U1, None))] += 1
    K.check(cc[R_MY] == 0 and cc[R_UT] == 0 and cc[4] > 0 and float(Roll.smithChance(U1)) == 100.0,
            "X2: 1e5 crafts at a 100 %% Smithing step-up: the ladder stops at Fabled (never Mythic): %s" % cc)
    apply(props(odds__mythic="5,5,5", odds__untiered="7,7,7", craft__maxRarity="mythic"))
    Cfg.SMITH_PER, Cfg.SMITH_CAP = 100.0, 100.0
    K.check([float(Cfg.O_MOB[R_MY]), float(Cfg.O_CHEST[R_MY]), float(Cfg.O_CRAFT[R_UT])] == [0.0, 0.0, 0.0] and int(Cfg.craftMax()) == 4
            and str(Cfg.CRAFT_MAX) == "fabled", "X2: a hand-edited file (odds.mythic 5,5,5, odds.untiered 7,7,7, craft.maxRarity mythic) still counts as 0 / fabled")
    c2 = [0] * 8
    for _ in range(N):
        c2[int(Roll.pickRarity(JInt(1)))] += 1
        c2[int(Roll.craftRarity(U1, None))] += 1
    K.check(c2[R_MY] == 0 and c2[R_UT] == 0, "X2: ... and 2e5 rolls with that file: never Mythic / Untiered: %s" % c2)
    K.check(str(Cfg.checkOdds("odds[mythic]", "0|0.5|0.6")).startswith("Mythic gear only comes from bosses") and Cfg.checkOdds("odds[mythic]", "0|0|0") is None
            and str(Cfg.checkOdds("odds[untiered]", "1,0,0")).startswith("Untiered gear") and Cfg.checkOdds("odds[rare]", "10|13|15") is None
            and Cfg.checkOdds("odds[untiered]", "0|0|0") is None and "untiered" in str(Cfg.checkOdds("odds[bogus]", "1|1|1")),
            "X2: Server Setup refuses a Mythic / Untiered weight above 0 (and names untiered among the rarities)")
    apply(Props(), False)
    Cfg.SMITH_PER, Cfg.SMITH_CAP = 0.5, 50.0

    # ============================================================================ X3 level-up caps per rarity
    apply(PH)

    def lv_code(iid, r, cur, org=12):
        d = Roll.newDoc(iid, JInt(r), True, "craft", JInt(org))
        d.put("lvl0", JClass("org.bson.BsonInt32")(JInt(org)))
        d.put("lvl", JClass("org.bson.BsonInt32")(JInt(cur)))
        return int(Forge.lvlInfo(U1, iid, d)[0]), str(Forge.lvlInfo(U1, iid, d)[5])
    caps = {}
    for r in range(8):
        iid = "Weapon_Sword_Bronze" if r == R_UT else "Weapon_Longsword_Iron"
        cap = int(Cfg.lvCap(JInt(r)))
        at, txt = lv_code(iid, r, 12 + cap)
        below, _t2 = lv_code(iid, r, 12 + cap - 1)
        caps[str(Defs.R_ID[r])] = (cap, at, below, txt)
    K.check([caps[k][0] for k in ("normal", "unique", "rare", "legendary", "fabled", "mythic", "set", "untiered")] == [6, 6, 6, 6, 6, 2, 6, 3]
            and all(v[1] == 4 and v[2] != 4 for v in caps.values()) and "+2 for Mythic gear" in caps["mythic"][3] and "+3 for Untiered gear" in caps["untiered"][3],
            "X3: lvlInfo stops each rarity at its own cap (Normal..Fabled / Set +6, Untiered +3, Mythic +2): %s" % caps)
    apply(props(reforge__levelCap="10"))
    K.check([int(x) for x in Cfg.LV_CAP] == [10, 10, 10, 10, 10, 2, 10, 3], "X3: no levelUp.cap lines + a hand-set reforge.levelCap 10: 10 for the six, Mythic 2, Untiered 3: %s" % list(Cfg.LV_CAP))
    apply(props(reforge__levelCap="1", levelUp__cap__mythic="0", levelUp__cap__rare="9"))
    K.check([int(x) for x in Cfg.LV_CAP] == [1, 1, 9, 1, 1, 0, 1, 1], "X3: levelUp.cap lines win; reforge.levelCap 1 caps Untiered at 1 too: %s" % list(Cfg.LV_CAP))
    apply(Props(), False)
    K.check(str(Cfg.capText()) == "+6 (Mythic +2, Untiered +3)" and "level ups +6 (Mythic +2, Untiered +3)" in str(Cfg.g1Text()), "X3: capText / ready line: %s" % Cfg.capText())

    # ============================================================================ X4 armor sets
    SETP = props(set__testset="Test Guard,4,hp+100 def+10 str+5", set__other="Other Set,2,def+3", set__bad="Bad Set,4,foo+3 hp+x cd+4")
    apply(SETP)
    K.check(jl(Set.list().split(", ")) == ["bad", "other", "testset"] and int(Set.idx("TESTSET")) == 2, "X4: the set table (key order, any case): %s" % Set.list())
    tb = JClass("org.bson.BsonInt32")
    I_DEF, I_STR, I_CD = int(Defs.sIndex("def")), int(Defs.sIndex("str")), int(Defs.sIndex("cd"))
    K.check(str(Set.bonusText(Cfg.STAB, JInt(0))) == "+4% Crit Damage" and str(Set.bonusText(Cfg.STAB, JInt(2))) == "+5 Strength, +10 Defense, +100 Health",
            "X4: bonus texts (a bad word is skipped): %s / %s" % (Set.bonusText(Cfg.STAB, JInt(0)), Set.bonusText(Cfg.STAB, JInt(2))))
    SLOTS = ["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"]

    def piece(iid, sid=None, r=None, ident=True):
        d = Roll.newDoc(iid, JInt(R_SET if r is None else r), True, "test", JInt(1))
        d.put("lvl", tb(JInt(1)))
        if sid:
            d.put("set", BS(sid))
        if not ident:
            d.put("id", JClass("org.bson.BsonBoolean")(False))
        return Data.put(IS(iid, JInt(1)), d, U1)
    arm = SIC(JShort(4))
    STAB_ON = Cfg.STAB
    EMPTY = Cfg.readSets(Props())
    HK = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes").getHealth()

    def measure():
        Cfg.STAB = STAB_ON
        t1 = [int(x) for x in Stats.totals(U1, None, arm, None, True)]
        l1 = Armor.lockSums(U1, arm, JFloat(1.0)).get(JObject(HK, JClass("java.lang.Integer")))
        c1 = [int(x) for x in Set.counts(STAB_ON, U1, arm)]
        hp = float(Set.hp(U1, arm))
        Cfg.STAB = EMPTY
        t0 = [int(x) for x in Stats.totals(U1, None, arm, None, True)]
        l0 = Armor.lockSums(U1, arm, JFloat(1.0)).get(JObject(HK, JClass("java.lang.Integer")))
        Cfg.STAB = STAB_ON
        dl = (float(l1) if l1 is not None else 0.0) - (float(l0) if l0 is not None else 0.0)
        return c1, [t1[i] - t0[i] for i in range(len(t1))], dl, hp
    seen = {}
    for n in range(5):
        for k in range(4):
            arm.setItemStackForSlot(JShort(k), piece(SLOTS[k], "testset") if k < n else None)
        seen[n] = measure()
    okn = all(seen[n][0][2] == n for n in range(5)) and all(sum(abs(x) for x in seen[n][1]) == 0 and seen[n][2] == 0.0 for n in range(4))
    d4 = seen[4][1]
    K.check(okn and d4[I_DEF] == 10 and d4[I_STR] == 5 and sum(abs(x) for x in d4) == 15 and seen[4][2] == -100.0 and seen[4][3] == 100.0,
            "X4: 0-3 pieces = nothing; all 4 = +10 Defense +5 Strength in the totals and +100 Health in the Health lock (signed -100): %s"
            % dict((n, (seen[n][0], [(i, v) for i, v in enumerate(seen[n][1]) if v], seen[n][2])) for n in seen))
    arm.setItemStackForSlot(JShort(3), piece("Armor_Iron_Legs"))
    sw = measure()
    arm.setItemStackForSlot(JShort(3), piece("Armor_Iron_Legs", "testset"))
    back = measure()
    K.check(sw[0][2] == 3 and sum(abs(x) for x in sw[1]) == 0 and sw[2] == 0.0 and back[1][I_DEF] == 10 and back[2] == -100.0,
            "X4: swap mid-wear: a plain piece in the legs slot drops the bonus at once, the set piece back brings it back")
    arm.setItemStackForSlot(JShort(2), piece("Armor_Iron_Hands", "other"))
    arm.setItemStackForSlot(JShort(3), piece("Armor_Iron_Legs", "other"))
    mx = measure()
    K.check(mx[0] == [0, 2, 2] and mx[1][I_DEF] == 3 and mx[1][I_STR] == 0 and mx[2] == 0.0,
            "X4: mixed sets: 2 'other' (complete at 2: +3 Defense) + 2 'testset' (2/4: nothing): %s" % ((mx[0], mx[1][I_DEF]),))
    arm.setItemStackForSlot(JShort(2), piece("Armor_Iron_Hands", "testset", ident=False))
    arm.setItemStackForSlot(JShort(3), piece("Armor_Iron_Legs", "testset"))
    un = measure()
    K.check(un[0][2] == 3 and un[1][I_DEF] == 0, "X4: an unidentified set piece never counts (3/4)")
    arm.setItemStackForSlot(JShort(2), piece("Armor_Iron_Hands", "testset", r=R_MY))
    my = measure()
    K.check(my[0][2] == 4 and my[1][I_DEF] == 10, "X4: a Mythic piece of the set counts (the set field, not the rarity)")
    Cfg.PART_STATS = False
    off = Armor.lockSums(U1, arm, JFloat(1.0)).get(JObject(HK, JClass("java.lang.Integer")))
    Cfg.STAB = EMPTY
    off0 = Armor.lockSums(U1, arm, JFloat(1.0)).get(JObject(HK, JClass("java.lang.Integer")))
    Cfg.STAB = STAB_ON
    Cfg.PART_STATS = True
    K.check((float(off) if off is not None else 0.0) == (float(off0) if off0 is not None else 0.0), "X4: part.stats off = no set Health")
    # the tooltip block + the inventory scan + /gear set
    Set.note(U1, arm)
    cd = doc(arm.getItemStack(JShort(1)))
    tip4 = jl(View.plain("Armor_Iron_Chest", cd, U1))
    arm.setItemStackForSlot(JShort(3), None)
    Set.note(U1, arm)
    tip3 = jl(View.plain("Armor_Iron_Chest", cd, U1))
    tipn = jl(View.plain("Armor_Iron_Chest", cd, None))
    K.check("Set: Test Guard (4/4)" in tip4 and "Full set bonus: +5 Strength, +10 Defense, +100 Health" in tip4
            and "Set: Test Guard (3/4)" in tip3 and "Full set (all 4): +5 Strength, +10 Defense, +100 Health" in tip3 and "Set: Test Guard (4 pieces)" in tipn,
            "X4: the tooltip block (owner 4/4 + the bonus, 3/4 + the grey full-set line, neutral '(4 pieces)'): %s | %s" % ([x for x in tip4 if "et" in x], [x for x in tip3 if "et" in x]))
    tx, co = AL(), AL()
    Set.tipLines(U1, doc(arm.getItemStack(JShort(2))), JInt(R_MY), tx, co)
    tx2, co2 = AL(), AL()
    nd = doc(piece("Armor_Iron_Head", "nope"))
    Set.tipLines(U1, nd, JInt(R_SET), tx2, co2)
    K.check(jl(co)[0] == "#CC66CC" and jl(co)[1] == "#878e9c" and jl(tx2) == ["Set: nope (not set up on this server)"] and jl(co2) == ["#878e9c"],
            "X4: a Mythic set piece's block is purple (its bonus line grey while 3/4); an unknown set id = one grey line: %s %s" % (jl(co), jl(tx2)))
    K.check(str(Set.activeText(U1, arm)) == "none", "X4: /gear lists no complete set at 3/4")
    # the inventory scan updates the worn count + re-renders the pieces
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JByte(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        jf(Cc, "inventory").set(o_, cont)
        return o_
    from jpype import JByte

    def mkinv():
        inv_ = INV()
        cs_ = {"hotbar": SIC(JShort(9)), "storage": SIC(JShort(36)), "backpack": SIC(JShort(9)), "armor": SIC(JShort(4)), "utility": SIC(JShort(4)), "tools": SIC(JShort(4))}
        for f_, kind in (("hotbar", "Hotbar"), ("storage", "Storage"), ("backpack", "Backpack"), ("armor", "Armor"), ("utility", "Utility"), ("tools", "Tool")):
            jf(INV, f_).set(inv_, comp(kind, cs_[f_]))
        return inv_, cs_
    inv, cs = mkinv()
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    prx = us.allocateInstance(PR.class_)
    jf(PR, "uuid").set(prx, U1)
    jf(PR, "username").set(prx, "Tester")
    for k in range(4):
        cs["armor"].setItemStackForSlot(JShort(k), piece(SLOTS[k], "testset"))
    Set.WORN.clear()
    Stamp.scan(prx, inv)
    tips = jl(View.plain("Armor_Iron_Head", doc(cs["armor"].getItemStack(JShort(0))), U1))
    shown = str(cs["armor"].getItemStack(JShort(0)).getMetadata().toJson())
    K.check(int(Set.worn(U1, Cfg.STAB, JInt(2))) == 4 and "Set: Test Guard (4/4)" in tips and "(4/4)" in shown and "Test Guard: +5 Strength" in str(Set.activeText(U1, cs["armor"])),
            "X4: GearStamp.scan notes the worn count before it re-renders: the stored tooltip says (4/4); /gear lists the complete set")
    # /gear set (GearSet.join) + its refusals
    jd = doc(piece("Armor_Iron_Chest"))
    jd = jd.clone()
    jd.put("r", BS("rare"))
    r1 = Set.join(jd, "Armor_Iron_Chest", "TestSet")
    md_ = doc(piece("Armor_Iron_Chest", r=R_MY)).clone()
    r2 = Set.join(md_, "Armor_Iron_Chest", "testset")
    apply(PH)          # Armor_Steel_Chest is an Untiered row here (drop-only: no recipe makes it)
    ud = Roll.newDoc("Armor_Steel_Chest", JInt(0), True, "t", JInt(15))
    apply(SETP)
    r3 = Set.join(ud.clone(), "Armor_Steel_Chest", "testset")
    r4 = Set.join(jd.clone(), "Weapon_Sword_Copper", "testset")
    r5 = Set.join(jd.clone(), "Armor_Iron_Chest", "nope")
    cl = jd.clone()
    r6 = Set.join(cl, "Armor_Iron_Chest", "clear")
    K.check(r1 is None and str(jd.getString("set").getValue()) == "testset" and str(jd.getString("r").getValue()) == "set"
            and r2 is None and str(md_.getString("r").getValue()) == "mythic" and str(md_.getString("set").getValue()) == "testset"
            and str(r3) == "Untiered items cannot be in a set" and str(r4) == "only armor pieces can be in a set" and str(r5).startswith("no set 'nope'")
            and r6 is None and not cl.containsKey("set") and str(cl.getString("r").getValue()) == "set" and str(Set.join(jd.clone(), "Armor_Iron_Chest", " ")).startswith("usage"),
            "X4: /gear set: joins (Rare -> Set label, Mythic stays Mythic), refuses Untiered / weapons / unknown sets, clear keeps the rarity: %s"
            % [r1, r2, r3, r4, r5, r6])
    K.check(Set.checkSet("set[cobalt_quest]", "Cobalt Guard|4|hp+100 def+10") is None and "a-z" in str(Set.checkSet("set[Bad Id]", "A|4|hp+1"))
            and "Pieces" in str(Set.checkSet("set[x]", "A|5|hp+1")) and "Unknown bonus words: foo+3" in str(Set.checkSet("set[x]", "A|4|foo+3"))
            and "no commas" in str(Set.checkSet("set[x]", "A,b|4|hp+1")) and "name" in str(Set.checkSet("set[x]", " |4|hp+1"))
            and "Unknown bonus words: tdmg+2" in str(Set.checkSet("set[x]", "A|4|tdmg+2")),
            "X8: the Armor sets check (id, pieces 1-4, bonus words: hp or a live armor stat, no commas; a weapon-only stat is refused)")
    # FIX 3 (critic 3, PROFILES-CONTRACT rule 2): the worn-count cache is keyed by the PROFILE key, so a profile switch reads its own entry
    apply(SETP)
    STAB_ON = Cfg.STAB
    for k in range(4):
        cs["armor"].setItemStackForSlot(JShort(k), piece(SLOTS[k], "testset"))
    Set.WORN.clear()
    Set.note(U1, cs["armor"])
    w1 = (int(Set.worn(U1, Cfg.STAB, JInt(2))), sorted(str(k) for k in Set.WORN.keySet()))
    PROF = {"k": str(U1) + "-p2"}

    @JImplements("java.util.function.Function")
    class ProfKey:
        @JOverride
        def apply(self, u): return JString(PROF["k"])
    br.put("profile:fn:key", ProfKey())
    w2 = int(Set.worn(U1, Cfg.STAB, JInt(2)))
    cs["armor"].setItemStackForSlot(JShort(3), None)
    Set.note(U1, cs["armor"])
    w3 = (int(Set.worn(U1, Cfg.STAB, JInt(2))), sorted(str(k) for k in Set.WORN.keySet()))
    br.remove("profile:fn:key")
    w4 = int(Set.worn(U1, Cfg.STAB, JInt(2)))
    Set.forget(U1)
    w5 = Set.WORN.size()
    K.check(w1 == (4, [str(U1)]) and w2 == -1 and w3 == (3, sorted([str(U1), str(U1) + "-p2"])) and w4 == 4 and w5 == 0,
            "FIX 3: WORN keyed by Gear.pkey: profile 1 noted 4/4 under '<uuid>'; after a switch to '-p2' nothing stale is read (-1 = neutral text) "
            "until its own scan (3/4); back on profile 1 its own 4/4; forget clears both keys: %s %s %s %s %s" % (w1, w2, w3, w4, w5))

    # ============================================================================ X5 the orange bag
    apply(Props(), False)
    ti = dict((str(k), i) for i, k in enumerate(Pool.T_KEY))
    PURSE[str(U1)] = 10 ** 7
    K.check(int(Ut.size()) == 0 and Ut.bag(JInt(12), JInt(-1), "t", "t", JInt(0)) is None
            and BoxFn().apply(OA([None, JInt(12), "test", JInt(0), None, "untiered"])) is None
            and BoxFn().apply(OA(["Weapon_Sword", JInt(12), "test", JInt(0), None, "untiered"])) is None,
            "X5 empty table: no orange bag can be made (Ut.bag, gear:fn:box 'untiered')")
    ob = Unid.make(JInt(ti["Weapon_Sword"]), JInt(0), JInt(R_UT), JInt(10), JInt(14), "t", "t", JInt(0))
    obd = Unid.doc(ob)
    c9 = SIC(JShort(9))
    c9.setItemStackForSlot(JShort(4), ob)
    why0 = str(Unid.why(obd))
    rid = Ident.identify(c9, JInt(4), ob.getItemId(), Forge.fp(ob), U1, "Tester", False, None, None)
    K.check(str(ob.getItemId()) == "Skyy_Unid_Bag_Untiered" and str(Unid.title(obd)) == "Unidentified Untiered Sword"
            and why0 == "No Untiered sword is set up for Lv 10-14 on this server yet - keep the bag, it can be identified once one is added."
            and str(Ident.refuse(ob, None)) == why0 and int(rid[0]) == 0 and PURSE[str(U1)] == 10 ** 7 and c9.getItemStack(JShort(4)).getItemId() == ob.getItemId(),
            "X5 empty table: an orange bag is REFUSED before any coin moves (bag kept, purse unchanged): %s / %s" % (why0, rid[1]))
    apply(PH)
    K.check(int(Ut.size()) == 3 and int(Ut.count()) == 2 and str(Ut.statusText()) == "Untiered table 2 / 3 usable item(s)",
            "X5 placeholder table: 3 rows, 2 usable (an unknown item id is skipped)")
    pt = Pool.table()
    K.check(int(Pool.idIdx("Weapon_Sword_Bronze")) >= 0 and not bool(pt[2][int(Pool.idIdx("Weapon_Sword_Bronze"))]) and bool(pt[2][int(Pool.idIdx("Weapon_Sword_Copper"))]),
            "X5: a table id leaves the normal bag pool")
    picks = set()
    for _ in range(300):
        picks.add(str(Pool.pickItem(JInt(ti["Weapon_Sword"]), JInt(0), JInt(18))))
    K.check("Weapon_Sword_Bronze" not in picks and len(picks) >= 2, "X5: normal sword bags at Lv 18 never turn into the Untiered sword: %s" % sorted(picks))
    nb = Ut.bag(JInt(12), JInt(-1), "t", "t", JInt(0))
    nbd = Unid.doc(nb)
    fb = BoxFn().apply(OA(["Weapon_Sword", JInt(30), "luggage", JInt(2), None, "untiered"]))
    fbn = BoxFn().apply(OA([None, JInt(30), "luggage", JInt(2), None, "UNTIERED"]))
    K.check(nb is not None and int(Unid.rar(nbd)) == R_UT and str(nbd.getString("mys").getValue()) == "Weapon_Sword" and (int(Unid.lo(nbd)), int(Unid.hi(nbd))) == (10, 14)
            and fb is not None and (int(Unid.lo(Unid.doc(fb))), int(Unid.hi(Unid.doc(fb)))) == (18, 20) and fbn is not None and int(Unid.rar(Unid.doc(fbn))) == R_UT,
            "X5: Ut.bag at Lv 12 = an orange SWORD bag Lv 10-14 (the only row there); gear:fn:box 'untiered' at Lv 30 -> nearest covered (18-20 sword / any type)")
    # a single undocumented Untiered-table item that drops becomes an orange bag (mob drop / fresh chest / gear:fn:box with the stack)
    fi = Unid.fromItem(IS("Weapon_Sword_Bronze", JInt(1)), JInt(1), JInt(12), "mob")
    fl = BoxFn().apply(OA([IS("Weapon_Sword_Bronze", JInt(1)), JInt(30), "luggage", JInt(2), None]))
    fn_ = Unid.fromItem(IS("Weapon_Sword_Copper", JInt(1)), JInt(1), JInt(12), "mob")
    fo = Unid.fromItem(IS("Weapon_Sword_Bronze", JInt(1)), JInt(2), JInt(60), "zone")
    K.check(fi is not None and int(Unid.rar(Unid.doc(fi))) == R_UT and str(Unid.doc(fi).getString("mys").getValue()) == "Weapon_Sword"
            and (int(Unid.lo(Unid.doc(fi))), int(Unid.hi(Unid.doc(fi)))) == (10, 14) and fl is not None and int(Unid.rar(Unid.doc(fl))) == R_UT
            and (int(Unid.lo(Unid.doc(fl))), int(Unid.hi(Unid.doc(fl)))) == (18, 20) and fn_ is not None and int(Unid.rar(Unid.doc(fn_))) != R_UT
            and fo is not None and (int(Unid.lo(Unid.doc(fo))), int(Unid.hi(Unid.doc(fo)))) == (18, 20),
            "X5: a dropped Untiered-table item becomes an ORANGE bag of its type (mob Lv 12 -> 10-14, luggage stack Lv 30 / chest Lv 60 -> 18-20); "
            "another sword stays a normal bag")
    c9.setItemStackForSlot(JShort(4), nb)
    cost = int(Unid.cost(nbd))
    p0 = PURSE[str(U1)]
    ri = Ident.identify(c9, JInt(4), nb.getItemId(), Forge.fp(nb), U1, "Tester", False, None, None)
    got = c9.getItemStack(JShort(4))
    gd = doc(got)
    K.check(int(ri[0]) == 1 and str(got.getItemId()) == "Weapon_Sword_Bronze" and int(Data.rarity(gd)) == R_UT and 10 <= int(Lvl.level("Weapon_Sword_Bronze", gd)) <= 14
            and Data.mods(gd).size() == 0 and cost == 1500 + 100 * 14 and p0 - PURSE[str(U1)] == cost and gd.containsKey("box"),
            "X5: identify of the orange bag (coins first): the Untiered sword, Lv 10-14, no modifiers, cost 2,900 taken: %s %s" % (ri[1], cost))
    rw = Unid.rerollWhy(gd)
    rr = Unid.reroll(gd, U1)
    K.check(rw is None and rr is not None and str(rr[0]) == "Weapon_Sword_Bronze" and int(Data.rarity(rr[2])) == R_UT,
            "X5: re-identify stays inside the Untiered rows of its type")
    # the reforge refusal + level up still possible
    p1 = PURSE[str(U1)]
    rf = Forge.reforge(c9, JInt(4), got.getItemId(), Forge.fp(got), U1, "Tester", False, None, None)
    K.check(int(rf[0]) == 0 and "fixed stats" in str(rf[1]) and PURSE[str(U1)] == p1, "X5: an Untiered item cannot be reforged (refused before coins): %s" % rf[1])
    # the legacy stamp (lazy heal of a plain table id) + a documented one keeps its document
    hs = Stamp.stampStack(IS("Weapon_Sword_Bronze", JInt(1)), U1, None)
    hs2 = Stamp.stampStack(hs, U1, None)
    apply(Props(), False)
    old_doc = Data.put(IS("Weapon_Sword_Bronze", JInt(1)), Roll.newDoc("Weapon_Sword_Bronze", JInt(2), True, "craft", JInt(16)), U1)
    apply(PH)
    kept = Stamp.stampStack(old_doc, U1, None)
    K.check(int(Data.rarity(doc(hs))) == R_UT and (hs2 is hs or str(doc(hs2).toJson()) == str(doc(hs).toJson()))
            and int(Data.rarity(doc(kept))) == 2, "X5: the legacy stamp of a PLAIN table id = Untiered (once); a documented Rare copy keeps its document")
    K.check(str(Fn(JInt(2)).apply(OA(["Weapon_Sword_Bronze"]))) == "untiered" and str(Fn(JInt(2)).apply(OA(["Weapon_Sword_Copper"]))) == "normal",
            "X5: gear:fn:rarity on a plain id answers untiered for a table id (SkyyMerchants reads this)")
    # /gear box untiered + /gear give --rarity untiered + the rarity rule (admin bodies on a stand-in inventory)
    inv3, cs3 = mkinv()
    Admin.boxCmd(prx, inv3, "untiered 12")
    Admin.boxCmd(prx, inv3, "untiered 40 bow")
    Admin.giveCmd(prx, inv3, "Weapon_Sword_Copper --rarity untiered")
    Admin.giveCmd(prx, inv3, "Weapon_Sword_Bronze --rarity rare")
    Admin.giveCmd(prx, inv3, "Weapon_Sword_Bronze")
    stor = [cs3["storage"].getItemStack(JShort(k)) for k in range(36)]
    stor = [x for x in stor if x is not None and not x.isEmpty()]
    K.check(len(stor) == 2 and str(stor[0].getItemId()) == "Skyy_Unid_Bag_Untiered" and str(stor[1].getItemId()) == "Weapon_Sword_Bronze" and int(Data.rarity(doc(stor[1]))) == R_UT,
            "X5: /gear box untiered 12 gives an orange bag, no bow row = nothing; /gear give refuses Untiered on a non-table id and another rarity on a table id: %s"
            % [str(x.getItemId()) for x in stor])
    K.check(Ut.rarityWhy("Weapon_Sword_Bronze", JInt(R_UT)) is None and "always Untiered" in str(Ut.rarityWhy("Weapon_Sword_Bronze", JInt(R_MY)))
            and "not in the Untiered table" in str(Ut.rarityWhy("Weapon_Sword_Copper", JInt(R_UT))) and Ut.rarityWhy("Weapon_Sword_Copper", JInt(R_MY)) is None,
            "X5: /gear rarity: untiered only for table ids, table ids only untiered")
    K.check(Ut.checkUt("ut[Weapon_Sword_Bronze]", "10|20|hits slowly") is None and "not gear" in str(Ut.checkUt("ut[Ingredient_Stick]", "1|2|x"))
            and "Max level" in str(Ut.checkUt("ut[Weapon_Sword_Bronze]", "20|10|x")) and "no commas" in str(Ut.checkUt("ut[Weapon_Sword_Bronze]", "1,2,a,b"))
            and "1-100" in str(Ut.checkUt("ut[Weapon_Sword_Bronze]", "0|10|x")) and Ut.checkUt("ut[Armor_Steel_Chest]", "15|25") is None,
            "X8: the Untiered items check (gear with a bag type, levels 1-100, max >= min, no commas)")

    # FIX 1 (critic 1 + 2nd critic 1, Skyy "but you cant craft them."): an id a recipe makes is never Untiered
    rcp = Ut.recipeOuts()
    K.check(bool(Ut.crafted("Weapon_Sword_Iron")) and bool(Ut.crafted("Armor_Iron_Chest")) and not bool(Ut.crafted("Weapon_Sword_Bronze"))
            and not bool(Ut.crafted("Armor_Steel_Chest")) and len(Ut.CRAFTED) >= 100,
            "FIX 1: crafted(): Iron Sword / Iron Chest have a recipe, Bronze Sword / Steel Chest do not (%d build-time craftable ids; live recipe store %d outputs)"
            % (len(Ut.CRAFTED), rcp.size()))
    # (the bare harness boot loads only part of the recipe store - no generated item recipes - so the build-time list carries vanilla)
    K.check(all(ITEM.getAssetMap().getAsset(str(x)) is not None for x in list(rcp)[:200]), "FIX 1: the live recipe-store outputs are real item ids")
    RC = props(ut__Weapon_Sword_Iron="10,20,crafted test", ut__Weapon_Sword_Bronze="10,20,ok")
    apply(RC)
    Wc = Wall()
    ird = Roll.newDoc("Weapon_Sword_Iron", JInt(2), True, "craft", JInt(16))
    irs = Stamp.stampStack(IS("Weapon_Sword_Iron", JInt(1)), U1, None)
    f8 = Fn(JInt(8))
    cr_ut = f8.apply(OA([U1, "Weapon_Sword_Bronze", JInt(1), "craft"]))
    cr_ir = f8.apply(OA([U1, "Weapon_Sword_Iron", JInt(1), "craft"]))
    K.check(int(Ut.size()) == 2 and int(Ut.count()) == 1 and not bool(Ut.has("Weapon_Sword_Iron")) and bool(Ut.has("Weapon_Sword_Bronze"))
            and int(Data.rarity(ird)) == 2 and int(Data.rarity(doc(irs))) == 0 and Wc.apply(IS("Weapon_Sword_Iron", JInt(1))) is None
            and Ut.note("Weapon_Sword_Iron") is None and str(Fn(JInt(2)).apply(OA(["Weapon_Sword_Iron"]))) == "normal",
            "FIX 1: a recipe id in the Untiered table is IGNORED (1 / 2 usable): a crafted Iron Sword keeps its rolled rarity, a plain one stamps "
            "Normal, it is not walled, gear:fn:rarity says normal: %s" % [int(Ut.size()), int(Ut.count()), bool(Ut.has("Weapon_Sword_Iron")),
            bool(Ut.has("Weapon_Sword_Bronze")), int(Data.rarity(ird)), int(Data.rarity(doc(irs))), Wc.apply(IS("Weapon_Sword_Iron", JInt(1))),
            Ut.note("Weapon_Sword_Iron"), str(Fn(JInt(2)).apply(OA(["Weapon_Sword_Iron"])))])
    K.check(bool(Roll.craftable("Weapon_Sword_Iron")) and not bool(Roll.craftable("Weapon_Sword_Bronze")) and cr_ut is None
            and cr_ir is not None and int(Data.rarity(doc(cr_ir[0]))) != R_UT,
            "FIX 1: GearRoll.craftable is false for a table id; the /craft bridge (gear:fn mode 8) mints no Untiered item, a craftable id rolls normally")
    cu = str(Ut.checkUt("ut[Weapon_Sword_Iron]", "10|20|x"))
    K.check("can be crafted" in cu and Ut.checkUt("ut[Weapon_Sword_Bronze]", "10|20|x") is None and Ut.checkUt("ut[Armor_Steel_Chest]", "15|25") is None,
            "FIX 1: Server Setup refuses a craftable id: %s" % cu)
    # another mod's recipe (the LIVE store) counts too: a cached recipe-output set naming the Bronze Sword
    HS = JClass("java.util.HashSet")
    fake = HS()
    fake.add("Weapon_Sword_Bronze")
    n0 = int(JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe").getAssetMap().getAssetMap().size())
    Ut.RCP, Ut.RCP_N = fake, n0
    hb = bool(Ut.has("Weapon_Sword_Bronze"))
    nb2 = Ut.bag(JInt(12), JInt(-1), "t", "t", JInt(0))
    Ut.RCP, Ut.RCP_N = None, -1
    K.check(not hb and nb2 is None and bool(Ut.has("Weapon_Sword_Bronze")),
            "FIX 1: an id another mod's recipe makes (live store) is ignored too (no orange bag); the cache rebuilds from the store afterwards")
    apply(PH)

    # ============================================================================ X6 the market wall + gear:fn:tradeable
    apply(PH)
    Cfg.STAB = Cfg.readSets(SETP)
    W = Wall()
    cases = {
        "mythic sword": Data.put(IS("Weapon_Sword_Copper", JInt(1)), Roll.newDoc("Weapon_Sword_Copper", JInt(R_MY), True, "t", JInt(12)), U1),
        "set piece": piece("Armor_Iron_Legs", "testset"),
        "set rarity, no field": Data.put(IS("Armor_Iron_Legs", JInt(1)), Roll.newDoc("Armor_Iron_Legs", JInt(R_SET), True, "t", JInt(15)), U1),
        "rare piece in a set": piece("Armor_Iron_Head", "testset", r=2),
        "untiered sword": got,
        "plain UT id": IS("Weapon_Sword_Bronze", JInt(1)),
        "mythic bag": Unid.make(JInt(ti["Weapon_Sword"]), JInt(0), JInt(R_MY), JInt(10), JInt(14), "t", "t", JInt(0)),
        "set bag": Unid.make(JInt(ti["Armor_Chest"]), JInt(1), JInt(R_SET), JInt(10), JInt(14), "t", "t", JInt(0)),
        "orange bag": nb,
    }
    free = {
        "rare sword": Data.put(IS("Weapon_Sword_Copper", JInt(1)), Roll.newDoc("Weapon_Sword_Copper", JInt(2), True, "t", JInt(12)), U1),
        "fabled armor": Data.put(IS("Armor_Iron_Hands", JInt(1)), Roll.newDoc("Armor_Iron_Hands", JInt(4), True, "t", JInt(15)), U1),
        "plain sword": IS("Weapon_Sword_Copper", JInt(1)),
        "rare bag": Unid.make(JInt(ti["Weapon_Sword"]), JInt(0), JInt(2), JInt(10), JInt(14), "t", "t", JInt(0)),
        "stick": IS("Ingredient_Stick", JInt(5)),
    }
    wv = dict((k, W.apply(v)) for k, v in cases.items())
    fv = dict((k, W.apply(v)) for k, v in free.items())
    K.check(all(str(v) == REASON for v in wv.values()) and all(v is None for v in fv.values()) and W.apply("x") is None,
            "X6: the wall refuses Mythic / Untiered / Set gear + those bags, lets the rest through: %s | %s" % (wv, fv))
    tf = Fn(JInt(13))
    K.check(all(not bool(tf.apply(v)) for v in cases.values()) and all(bool(tf.apply(v)) for v in free.values())
            and bool(tf.apply(OA(["Weapon_Sword_Copper"]))) and not bool(tf.apply(OA(["Weapon_Sword_Bronze"]))) and tf.apply(JString("nope")) is None,
            "X6: gear:fn:tradeable (stacks and {id, metadata})")
    # fix round 2 (critic 2): a hand-edited Untiered row for an id that is NOT gear never walls that item (one WARN), gear rows still wall
    UNREAD = str(Wall.UNREAD)
    ng = None
    for cand in ("Rock_Stone", "Ingredient_Fibre", "Ingredient_Stick", "Plant_Fruit_Apple", "Ingredient_Bar_Iron"):
        if Gear.item(cand) is not None and not bool(Data.isGear(cand)) and not bool(Ut.crafted(cand)):
            ng = cand
            break
    K.check(ng is not None, "FIX2: found a real non-gear item no recipe makes for the stray-row check: %s" % ng)
    if ng is not None:
        apply(props(ut__Weapon_Sword_Bronze="10,20,x", **{"ut__" + ng: "1,10"}))
        K.check(bool(Ut.has(ng)) and W.apply(IS(ng, JInt(5))) is None and bool(tf.apply(OA([ng])))
                and str(W.apply(IS("Weapon_Sword_Bronze", JInt(1)))) == REASON and not bool(tf.apply(OA(["Weapon_Sword_Bronze"]))),
                "FIX2: a stray ut.%s row (not gear) never walls it on the Auction House / Bazaar; the gear row still walls" % ng)
        apply(PH)
        Cfg.STAB = Cfg.readSets(SETP)
    # fix round 2 (critic 3): the wall fails CLOSED on gear / bags whose document cannot be read (damaged, or a newer schema after a rollback)
    def raw(iid, key, val):
        md = BD()
        md.put(key, val)
        try:
            return IS(iid, JInt(1), md)
        except Exception:
            return IS(iid, JInt(1)).withMetadata(md)
    newer = BD()
    newer.put("v", tb(JInt(9)))
    newer.put("r", BS("normal"))
    ur = {
        "damaged gear doc": W.apply(raw("Weapon_Sword_Copper", str(Defs.DOC_KEY), BS("garbage"))),
        "newer schema doc": W.apply(raw("Weapon_Sword_Copper", str(Defs.DOC_KEY), newer)),
        "damaged bag doc": W.apply(raw(str(cases["rare bag"].getItemId()) if "rare bag" in cases else str(free["rare bag"].getItemId()), str(Unid.KEY), BS("garbage"))),
    }
    K.check(all(str(v) == UNREAD for v in ur.values()) and W.apply(IS("Weapon_Sword_Copper", JInt(1))) is None
            and not bool(tf.apply(raw("Weapon_Sword_Copper", str(Defs.DOC_KEY), BS("garbage")))),
            "FIX2: unreadable / newer gear and bag documents are refused (fail closed), a plain sword still lists: %s" % ur)

    # ============================================================================ X7 gear:fn:grant
    G = Fn(JInt(12))

    def grant(*a):
        return G.apply(OA(list(a)))
    g1 = grant("Weapon_Sword_Copper", JInt(12), None, None, None, U1, "quest")
    g2 = grant("Weapon_Sword_Bronze", JInt(5))
    g3 = grant("Armor_Iron_Legs", JInt(18), None, "testset")
    g4 = grant("Armor_Iron_Legs", JInt(18), "mythic", "testset", "boss_judge")
    g5 = grant("Weapon_Sword_Copper", JInt(99), "rare")
    bad = [grant("Weapon_Sword_Copper", JInt(12), "untiered"), grant("Weapon_Sword_Bronze", JInt(12), "rare"), grant("Weapon_Sword_Copper", JInt(12), None, "testset"),
           grant("Weapon_Sword_Bronze", JInt(12), None, "testset"), grant("Ingredient_Stick", JInt(5)), grant("Weapon_Sword_Copper", JInt(12), "bogus"),
           G.apply(JString("x")), G.apply(OA([])), grant("Weapon_Nope_Nothing", JInt(5))]
    d1, d2, d3, d4, d5 = [doc(x) for x in (g1, g2, g3, g4, g5)]
    b5 = list(Lvl.band("Weapon_Sword_Copper"))
    K.check(int(Data.rarity(d1)) <= 4 and bool(Data.identified(d1)) and str(d1.getString("src").getValue()) == "quest" and int(Lvl.level("Weapon_Sword_Copper", d1)) == 12
            and int(Data.rarity(d2)) == R_UT and int(Lvl.level("Weapon_Sword_Bronze", d2)) == 10
            and int(Data.rarity(d3)) == R_SET and str(d3.getString("set").getValue()) == "testset"
            and int(Data.rarity(d4)) == R_MY and str(d4.getString("set").getValue()) == "testset" and str(d4.getString("pool").getValue()) == "boss_judge"
            and int(Data.rarity(d5)) == 2 and int(Lvl.level("Weapon_Sword_Copper", d5)) == b5[1] and all(x is None for x in bad),
            "X7: gear:fn:grant: a random ladder rarity at the asked level, a table id Untiered (level into its row), a Set piece, a Mythic set piece with its "
            "pool, the level kept in the band (99 -> %d); refusals: %s" % (b5[1], [x is not None for x in bad]))
    # the 1e5-roll check of the grant's own random path (no rarity asked = the chest odds)
    gc = [0] * 8
    for _ in range(2000):
        gc[int(Data.rarity(doc(grant("Weapon_Sword_Copper", JInt(12)))))] += 1
    K.check(gc[R_MY] == 0 and gc[R_UT] == 0 and gc[R_SET] == 0, "X7: 2,000 grants without a rarity: never Mythic / Untiered / Set: %s" % gc)

    # ============================================================================ M the partner mods
    vt = CHM()
    vt.put("SkyyGear", W)
    br.put("market:veto", vt)
    AhItem = JClass("com.skyy.auctions.AhItem")
    ah = dict((k, AhItem.tradeable(v)) for k, v in cases.items() if not str(v.getItemId()).startswith("Skyy_Unid_"))
    ahf = dict((k, AhItem.tradeable(v)) for k, v in free.items() if k in ("rare sword", "fabled armor", "plain sword"))
    K.check(all(str(v) == REASON for v in ah.values()) and all(v is None for v in ahf.values()),
            "M: SkyyAuctions 0.1.3 AhItem.tradeable (listing + buying) refuses every walled item through market:veto, lists the rest: %s | %s" % (ah, ahf))
    MW = JClass("com.skyy.merchants.MerchWall")
    br.put("gear:fn:rarity", Fn(JInt(2)))
    K.check(str(MW.why("Weapon_Sword_Bronze")) == "Mythic, Untiered and Set gear is never sold" and MW.why("Weapon_Sword_Copper") is None,
            "M: SkyyMerchants 0.1 MerchWall.why never sells an Untiered-table id (gear:fn:rarity -> untiered): %s" % MW.why("Weapon_Sword_Bronze"))
    BI = JClass("com.skyy.bazaar.Inv")
    cz = SIC(JShort(6))
    cz.setItemStackForSlot(JShort(0), cases["mythic sword"])
    cz.setItemStackForSlot(JShort(1), free["rare sword"])
    cz.setItemStackForSlot(JShort(2), IS("Weapon_Sword_Copper", JInt(1)))
    cz.setItemStackForSlot(JShort(3), Data.put(IS("Weapon_Sword_Copper", JInt(1)), Roll.newDoc("Weapon_Sword_Copper", JInt(R_SET), True, "t", JInt(12)), U1))
    n_on = int(BI.countIn(cz, "Weapon_Sword_Copper"))
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    inv4, cs4 = mkinv()
    for k in range(4):
        cs4["storage"].setItemStackForSlot(JShort(k), cz.getItemStack(JShort(k)))
    pl = us.allocateInstance(PLA.class_)
    jf(PLA, "inventory").set(pl, inv4)
    took = int(BI.take(pl, "Weapon_Sword_Copper", JInt(10)))
    left = [None if cs4["storage"].getItemStack(JShort(k)) is None or cs4["storage"].getItemStack(JShort(k)).isEmpty()
            else int(Data.rarity(doc(cs4["storage"].getItemStack(JShort(k))))) for k in range(4)]
    K.check(n_on == 2 and took == 2 and left == [R_MY, None, None, R_SET] and str(BI.wallId("Weapon_Sword_Bronze")) == REASON and BI.wallId("Weapon_Sword_Copper") is None
            and str(BI.veto(cases["set piece"])) == REASON and not bool(BI.walled(IS("Weapon_Sword_Bronze", JInt(1)))),
            "M: SkyyBazaar 0.1.7: countIn / take skip the Mythic + Set copies (2 counted, 2 taken, the walled ones stay), a table id is refused "
            "as a product (buy0 / sell0), a plain stack is never asked: %s / %s / %s" % (n_on, took, left))

    @JImplements("java.util.function.Function")
    class Boom:
        @JOverride
        def apply(self, s): raise RuntimeError("boom")
    vt.put("Other", Boom())
    K.check(str(BI.veto(free["rare sword"])) == "could not check this item", "M: SkyyBazaar: a veto that throws counts as a refusal")
    vt.remove("Other")
    br.remove("market:veto")
    K.check(int(BI.countIn(cz, "Weapon_Sword_Copper")) == 4 and BI.wallId("Weapon_Sword_Bronze") is None,
            "M: SkyyBazaar without market:veto (no SkyyGear 0.2.14) = 0.1.6 behaviour (every stack counted)")
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
                for v_ in vers:
                    t_ = t_.replace(v_, "VER")
                lines_.append(t_)
            return "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
            d_["raw " + str(m_.getName())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_

    def compare(old, new, pkg, vers):
        pa, pb = pool_of(old), pool_of(new)
        na, nb = jar_classes(old), jar_classes(new)
        diffs = {}
        for cn in sorted(set(na) & set(nb)):
            ma, mb = members(pa, cn, vers), members(pb, cn, vers)
            dd = sorted(k for k in set(ma) | set(mb) if not k.startswith("raw ") and ma.get(k) != mb.get(k))
            if dd:
                diffs[cn[len(pkg):]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd]
        return sorted(c[len(pkg):] for c in set(nb) - set(na)), sorted(c[len(pkg):] for c in set(na) - set(nb)), diffs
    add, gone, diffs = compare(OLD_JAR, JAR, PKG, ("0.2.13", "0.2.14"))
    print("C. class compare 0.2.13 -> 0.2.14: + %s - %s" % (add, gone))
    for k in sorted(diffs):
        print("   %-16s %s" % (k, ", ".join(diffs[k])[:400]))
    K.check(add == NEW_CLASSES and not gone, "C: classes added = %s, none removed: + %s - %s" % (NEW_CLASSES, add, gone))
    unexpected = sorted(set(diffs) - EXPECT_CHANGED)
    missing = sorted(EXPECT_CHANGED - set(diffs))
    K.check(not unexpected and not missing, "C: exactly the listed classes changed (unexpected %s, listed but unchanged %s)" % (unexpected, missing))
    pa2, pb2 = pool_of(OLD_JAR), pool_of(JAR)
    nr_bad = []
    for cn_, mn_ in NR_ONLY:
        a_ = members(pa2, PKG + cn_, ())["raw " + mn_].split(chr(10))
        b_ = members(pb2, PKG + cn_, ())["raw " + mn_].split(chr(10))
        pairs = [(x, y) for x, y in zip(a_, b_) if x != y]
        if len(a_) != len(b_) or not pairs or any((x, y) != ("bipush 7", "bipush 8") for x, y in pairs):
            nr_bad.append((cn_, mn_, pairs[:3]))
    K.check(not nr_bad, "C: GearQual.parse / text / damaged, IdentifyPage.detail, GearCfg.importRolls differ ONLY by the inlined rarity count 7 -> 8: %s" % nr_bad)
    want = {"GearDefs": {"+f R_MY", "+f R_SET", "+f R_UT"}, "GearUnid": {"~m pick", "~m why", "~m rerollWhy", "~m title", "~m descMsg", "~m fromItem"},
            "GearPool": {"~m table"}, "GearData": {"~m legacy"}, "GearStats": {"~m totals"}, "GearArmor": {"~m lockSums"}, "GearStamp": {"~m scan"},
            "GearFx": {"~m forget"}, "GearBoxFn": {"~m apply"}, "GearFn": {"+m grant", "+m tradeable", "~m apply"}, "GearCmd": {"~c "}}
    bad = dict((k, (sorted(v - set(diffs.get(k, []))), sorted(set(diffs.get(k, [])) - v))) for k, v in want.items()
               if not v <= set(diffs.get(k, [])) or (k not in ("GearDefs",) and set(diffs.get(k, [])) - v - {"~<clinit>"}))
    K.check(not bad, "C: the small classes changed exactly where the patch says (missing / extra): %s" % bad)
    cfg = set(diffs.get("GearCfg", []))
    K.check({"+m migrate0214", "+m guUpdate", "+m guLog", "+m readUt", "+m readSets", "+m parseBonus", "+m bonusStat", "+m lvCap", "+m capText", "+m g1Text",
             "+m checkOdds", "~m apply", "~m craftMax", "~m checkRarityKey", "~m defaultsText"} <= cfg, "C: GearCfg gains the update, the readers, the caps, the odds check: %s" % sorted(cfg))
    badd, bgone, bd = compare(BZ_OLD, BZ_JAR, "com.skyy.bazaar.", ("0.1.6", "0.1.7"))
    print("C. class compare SkyyBazaar 0.1.6 -> 0.1.7: + %s - %s %s" % (badd, bgone, bd))
    K.check(not badd and not bgone and sorted(bd) == ["Inv", "Trader"] and sorted(bd["Inv"]) == ["+m veto", "+m wallId", "+m walled", "~m countIn", "~m take"]
            and sorted(bd["Trader"]) == ["~m buy0", "~m sell0"],
            "C: SkyyBazaar 0.1.7: only Inv (+veto / walled / wallId, countIn / take) and Trader (buy0 / sell0) (the version is in the manifest): %s" % bd)
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
    K.check(Cfg.guUpdate(fresh) is None and "odds.mythic=0,0,0\n" in fresh and (chr(10) + "reforge.levelCap=") not in fresh and fresh.endswith(
        "# ---- ut.<item id>=<min level>,<max level>,<trade-off line> (Untiered items: always Untiered, from orange bags and quests) ----\n"),
        "D: a fresh 0.2.14 file carries the marker (no update), Mythic odds 0,0,0, no reforge.levelCap, the block at its end")
    old = open(os.path.join(home, "config.properties"), "rb").read().decode("latin-1")
    BLOCK = fresh[fresh.index("# ---- Untiered, Mythic and Set (SkyyGear 0.2.14) ----"):]

    def upd(text):
        r = Cfg.guUpdate(text)
        return None if r is None else (str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]], str(r[4]))
    r = upd(old)
    exp = old.replace("\nodds.mythic=0,0.5,0.6\n", "\nodds.mythic=0,0,0\n") + "\n" + BLOCK
    K.check(r is not None and r[0] == exp and r[1] == "odds.mythic 0,0.5,0.6 -> 0,0,0" and r[3] == ["odds[mythic]", "0|0.5|0.6", "0|0|0"]
            and r[2] == [] and r[4].startswith("levelUp.cap.normal") and r[4].endswith("xp.craft.untiered"),
            "D: the live file: odds.mythic rewritten in place, the block appended = exactly the fresh file's block; one change-log row: %s %s" % (r[1] if r else None, r[2] if r else None))
    K.check(upd(r[0]) is None, "D: the updated text carries the marker (run once)")
    crlf = old.replace("\n", "\r\n")
    rc = upd(crlf)
    K.check(rc is not None and rc[0] == exp.replace("\n", "\r\n"), "D: a CRLF file keeps CRLF on every line (rewrite + block)")
    nonl = old.rstrip("\n")
    rn = upd(nonl)
    K.check(rn is not None and rn[0] == exp.rstrip("\n") + "" and rn[0].count("odds.mythic=0,0,0") == 1,
            "D: a file without a final newline: the block is appended after its last line, still no final newline")
    hand = old.replace("\nodds.mythic=0,0.5,0.6\n", "\nodds.mythic=0,1,1\n").replace("\nreforge.levelCap=6\n", "\nreforge.levelCap=9\n") \
        + "levelUp.cap.rare=4\nrarity.untiered=1,10,20\n"
    rh = upd(hand)
    K.check(rh is not None and "odds.mythic=0,1,1" in rh[0] and rh[1] == "" and rh[3] == [] and "reforge.levelCap=9" in rh[0]
            and "levelUp.cap.normal=9" in rh[0] and "levelUp.cap.mythic=2" in rh[0] and "levelUp.cap.untiered=3" in rh[0] and "levelUp.cap.set=9" in rh[0]
            and rh[0].count("levelUp.cap.rare=") == 1 and rh[0].count("rarity.untiered=") == 1 and len(rh[2]) == 4,
            "D: hand-edited odds.mythic / reforge.levelCap / block keys are KEPT + noted; the six +6 rarities carry 9, Untiered 3, Mythic 2: %s" % (rh[2] if rh else None))
    two = old.replace("\nodds.mythic=0,0.5,0.6\n", "\nodds.mythic=0,0.5,0.6\nodds.mythic=0,2,2\n")
    rt = upd(two)
    K.check(rt is not None and "odds.mythic=0,0.5,0.6\nodds.mythic=0,2,2" in rt[0] and rt[1] == "", "D: when the LAST odds.mythic entry is custom nothing is rewritten")
    # START TWICE on the scratch copy of the live folder (the real setup order: every older update, then 0.2.14, then load)
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    files0 = sorted(os.path.relpath(os.path.join(a, f), home) for a, d, fs in os.walk(home) for f in fs)
    log0 = open(os.path.join(home, "config-changes.log"), "rb").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else b""
    snaps = []
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(os.path.join(home, "config.properties"), "rb").read())
        K.check([int(x) for x in Cfg.LV_CAP] == [6, 6, 6, 6, 6, 2, 6, 3] and float(Cfg.O_MOB[5]) == 0.0 and float(Cfg.O_CHEST[5]) == 0.0
                and str(Cfg.CRAFT_MAX) == "fabled", "D start %d: the loaded caps + Mythic odds" % step)
    K.check(snaps[0] == exp.encode("latin-1"), "D start 1: the live copy = the expected text byte for byte")
    K.check(snaps[1] == snaps[0], "D start 2: nothing changes")
    files1 = sorted(os.path.relpath(os.path.join(a, f), home) for a, d, fs in os.walk(home) for f in fs)
    newf = sorted(set(files1) - set(files0))
    hist = [f for f in newf if f.startswith("config-history")]
    hb = [open(os.path.join(home, f), "rb").read() for f in hist]
    K.check(any(b == old.encode("latin-1") for b in hb) and all(f.startswith("config-history") for f in newf) and not set(files0) - set(files1),
            "D: the History copy holds the old bytes; only config-history files were added: %s" % newf)
    log1 = open(os.path.join(home, "config-changes.log"), "rb").read()
    added = log1[len(log0):].decode("utf-8", "replace").strip().split("\n")
    K.check(log1.startswith(log0) and len(added) == 1 and "\tSkyyGear 0.2.14\t-\tupdate\todds[mythic]\t0|0.5|0.6\t0|0|0\tdone" in added[0],
            "D: one config-changes.log row, status done (no dead Undo button - Mythic odds above 0 are refused; fix round 2): %s" % added)
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
                     ("--verifybz", lambda: run_verify_bz(arg("--out"))), ("--engine", lambda: run_engine(arg("--out"))),
                     ("--compare", lambda: run_compare(arg("--out"))),
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
    for j in (JAR, AH_JAR, MER_JAR, BZ_JAR, BZ_OLD):
        assert os.path.isfile(j), j
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    with zipfile.ZipFile(OLD_JAR) as z_:
        assert '"Version": "0.2.13"' in z_.read("manifest.json").decode("utf-8"), "the old jar is not 0.2.13"
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        run_assets()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("verifybz", "--verifybz"), ("engine", "--engine"), ("compare", "--compare")):
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
            try:
                os.rmdir(SCR_ROOT)          # only when empty (never another task's folder)
            except OSError:
                pass
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
