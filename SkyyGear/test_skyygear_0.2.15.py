"""Harness for SkyyGear 0.2.15 (MINING ARMOR: the vanilla metal sets Copper..Onyxium = green Mining Sets, research/cloud/Mining-Armor-Spec.md;
+ the pets:stats reader). Build first:
    python tools/gear_0_2_15_patch.py && python SkyyGear/build_skyygear_0.2.15.py

    python SkyyGear/test_skyygear_0.2.15.py [--jar <SkyyGear-0.2.15.jar>] [--old <SkyyGear-0.2.14.jar>] [--dir <scratch>] [--keep]

The 0.2.11 harness's helpers (stand-ins F, verify A, the bare-server boot of V, the engine-access audit AA) are loaded from
SkyyGear/test_skyygear_0.2.11.py and run on the 0.2.15 jar (the 0.2.12 - 0.2.14 harnesses do the same).
  S  non-class entries 0.2.14 -> 0.2.15: only manifest.json changes
  A  every class of the jar loads + verifies (-Xverify:all)
  V  the vanilla pack store by store + THE JAR as its own pack (no asset change in this round; no failed store of its own)
  X  EVERY NEW CODE PATH EXECUTED on the real Item / BlockType stores (-Xverify:all): X0 the rows + fresh file + checks; X1 the 28 ids + the bag
     pool; X2 the table sums; X3 the Mining gate (check, gateLine, active); X4 new documents (craft at Mining level, drops, bags refused, bridge
     mode 9, give, Smithing XP); X5 Health / resistance = 0.2.14 (share 100) + the share; X6 compute / note / lamp / caps / old pieces; X7 the
     Fortune + Wisdom post (pickaxe, shovel, hatchet, sword, empty hand, under-level tool, off); X8 Mining Power (onDamage + the REAL
     GearToolHitSys.handle); X9 Speed through the REAL GearFx.armorPass (+ busy, forget); X10 tooltip; X11 reforge refused / level up works;
     X12 pets:stats; X13 sets (addTo / hp skip, bonus texts); X14 garmor.miningOn off = 0.2.14
  C  CLASS COMPARE 0.2.14 -> 0.2.15 (javassist members): GearMine added, only the listed classes / members differ
  D  THE ONE-TIME UPDATE migrate0215: synthetic files (fresh, LF / CRLF, no final newline, keys already there) + START TWICE on a scratch COPY
     of the live Skyy_SkyyGear folder (block appended, History copy, nothing else; the 2nd start changes nothing)
  AA THE ENGINE-ACCESS AUDIT
Scratch: tools/dev/scratch/mine01/gear (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.15"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "mine01")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "gear")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-0.2.14.jar")))      # read only
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
PKG = "com.skyy.gear."
REASON = "Mythic, Untiered and Set gear never goes on the market - trade it directly with another player."
TIERS = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
SLOTS = ["Head", "Chest", "Hands", "Legs"]
FULL = [1.5, 2.3, 3.8, 6.0, 8.3, 11.3, 15.0]
NEW_CLASSES = ["GearMine"]
EXPECT_CHANGED = {"GearCfg", "GearGate", "GearView", "GearRoll", "GearBase", "GearPool", "GearUnid", "GearTag", "GearBoxFn", "GearForge", "GearTool",
                  "GearSet", "GearStats", "GearFx", "GearAdmin", "SkyyGearPlugin",
                  # the kit's inlined row / category counts (+5 rows, +1 category)
                  "CfgRows", "CfgFile"}

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


# ====================================================================================================== S: non-class entries
def run_assets():
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    check(set(ea) == set(eb) and changed == ["manifest.json"] and b'"0.2.15"' in eb["manifest.json"],
          "S: non-class entries 0.2.14 -> 0.2.15: none added / removed, only manifest.json (0.2.15) changes: + %s - %s ~ %s"
          % (sorted(set(eb) - set(ea)), sorted(set(ea) - set(eb)), changed))
    print("S. assets: only the manifest changed")
    # fix round (design critic LOW 5): the garmor.mining column headings are spelled out
    cls = b"".join(zn.read(n) for n in zn.namelist() if n.endswith(".class"))
    check(b"Fortune Head Chest Legs Hands|Wisdom % Head Chest Legs Hands|Lamp 0-4" in cls and b"Fortune H C L Ha" not in cls,
          "S fix: the garmor.mining table headings read 'Fortune Head Chest Legs Hands | Wisdom % Head Chest Legs Hands | Lamp 0-4'")


# ====================================================================================================== V + X (the engine child)
def run_engine(out):
    from jpype import JClass, JArray, JInt, JLong, JShort, JFloat, JDouble, JImplements, JOverride, JObject, JBoolean, JString
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
    E = H["engine_boot"](K)
    ITEM, us, jf = E["ITEM"], E["us"], E["jf"]
    K.check(set(E["fail"]) <= set(E["vfail"]), "V: the jar as its own pack: no failed store of its own (%s vs vanilla %s)" % (E["fail"], E["vfail"]))
    # (the 0.2.11 / 0.2.12 harness note: the speed-tier interaction copies miss the Stamina stat types in the BARE boot only - not this round's)
    ours = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and ("SkyyGear" in r[1] or "GearMine" in r[1] or "Armor_" in r[1])
            and "SkyyGear_Spd" not in r[1]]
    spd = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and "SkyyGear_Spd" in r[1]]
    K.check(not ours, "V: no SEVERE / WARNING of ours (the 0.2.6 speed copies' known bare-boot Selector / Stamina gaps aside - those files are "
            "byte-identical to 0.2.14, S): %s" % ours[:3])
    K.notes.append("V: %d bare-boot lines about the unchanged speed-tier copies (known since 0.2.11)" % len(spd))
    P = lambda n: JClass(PKG + n)
    (Cfg, Defs, Data, Roll, Unid, Pool, Set, Wall, Fn, Stats, Armor, Forge, View, Stamp, Lvl, Gate, BoxFn, Mine, Tool, Base, Tag, Fx, Gear, Hit) = [
        P(n) for n in ("GearCfg", "GearDefs", "GearData", "GearRoll", "GearUnid", "GearPool", "GearSet", "GearWall", "GearFn", "GearStats",
                       "GearArmor", "GearForge", "GearView", "GearStamp", "GearLevel", "GearGate", "GearBoxFn", "GearMine", "GearTool", "GearBase",
                       "GearTag", "GearFx", "Gear", "GearToolHitSys")]
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    BS = JClass("org.bson.BsonString")
    BI32 = JClass("org.bson.BsonInt32")
    Props = JClass("java.util.Properties")
    UUID = JClass("java.util.UUID")
    HM = JClass("java.util.HashMap")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    Colls = JClass("java.util.Collections")
    SR = JClass("java.io.StringReader")
    OA = JArray(JClass("java.lang.Object"))
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000b015")
    R_SET = int(Defs.R_SET)
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
    LEVELS = {}

    @JImplements("java.util.function.Function")
    class SkillLv:
        @JOverride
        def apply(self, a):
            return JInt(LEVELS.get(str(a[1]), 0))

    def skills(mining=49, combat=10, smithing=0):
        LEVELS.clear()
        LEVELS.update({"Mining": mining, "Combat": combat, "Foraging": 49, "Smithing": smithing})
        br.put("skill:fn:level", SkillLv())
        Gate.forget(U1)
        Tool.LAST.clear()

    FRESH = str(Cfg.defaultsText())
    DEFP = Props()
    DEFP.load(SR(FRESH))

    def apply(p=None, from_file=False):
        Cfg.apply(DEFP if p is None else p, from_file)
        Pool.TAB = None

    def props(**kv):
        p = Props()
        p.load(SR(FRESH))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        return p

    def jl(xs):
        return [str(x) for x in xs] if xs is not None else []

    def doc(s):
        return Data.effective(s.getItemId(), s.getMetadata())

    def mid(t, sl):
        return "Armor_%s_%s" % (t, sl)

    def piece(t, sl, lvl=None, r=None, old=False):
        """a NEW mining piece (newDoc) or, old=True, a 0.2.14-style document made with mining armor OFF (rolled rarity + modifiers)"""
        iid = mid(t, sl)
        if old:
            Cfg.GM_ON = False
        b = list(Lvl.band(iid))
        d = Roll.newDoc(iid, JInt(R_SET if r is None else r), True, "craft", JInt(b[0] if lvl is None else lvl))
        if old:
            Cfg.GM_ON = True
        return Data.put(IS(iid, JInt(1)), d, U1)

    def wear(*stacks):
        a = SIC(JShort(4))
        for k, s_ in enumerate(stacks):
            if s_ is not None:
                a.setItemStackForSlot(JShort(k), s_)
        return a

    def fullset(t, lvl=None):
        return wear(*[piece(t, sl, lvl) for sl in SLOTS])

    def gsrc():
        o = br.get("skill:bonus:" + str(U1))
        if o is None or o.get("gear") is None:
            return None
        g = o.get("gear")
        return dict((str(k), (str(g.get(k)) if "String" in str(type(g.get(k))) or isinstance(g.get(k), str) else float(g.get(k)))) for k in g.keySet())

    apply()
    skills()

    # ============================================================================ X0 the rows, the fresh file, the checks
    tail = FRESH.rstrip("\n").split("\n")
    gi = tail.index("# ---- Mining armor: the vanilla metal sets Copper..Onyxium (SkyyGear 0.2.15) ----")
    blk = tail[gi:]
    K.check(blk[1].startswith("# SkyyGear 0.2.15 mining armor (Skyy 2026-10-09)") and len(blk) == 26 and tail[gi - 1] == ""
            and "garmor.miningOn=true" in blk and "garmor.miningShare=100" in blk and "armor.fortune.cap=15" in blk and "armor.wisdom.cap=10" in blk
            and "garmor.mining.cobalt=0.5 0.7 0.5 0.3,0.5 0.7 0.5 0.3,3" in blk and "set.mining_onyxium=Onyxium Mining Set,4,mfort+10 mpow+15 spd+10" in blk,
            "X0: the fresh file ends with the 0.2.15 block (heading, marker, 4 scalars, 7 tier rows, 7 set rows): %s" % blk[:3])
    K.check(bool(Cfg.GM_ON) and int(Cfg.GM_SHARE) == 100 and float(Cfg.GM_FCAP) == 15.0 and float(Cfg.GM_WCAP) == 10.0
            and [str(x) for x in Set.list().split(", ")] == ["mining_adamantite", "mining_cobalt", "mining_copper", "mining_iron", "mining_mithril",
                                                               "mining_onyxium", "mining_thorium"],
            "X0: the fresh file loads: mining armor on, share 100, caps 15 / 10, the seven Mining Sets in the Armor sets table: %s" % Set.list())
    gm = Cfg.readMine(props(garmor__mining__iron="1 2 3 4,0 0 0 9,4", garmor__mining__copper="bad"))
    K.check([float(x) for x in gm[0]][4:8] == [1.0, 2.0, 4.0, 3.0] and [float(x) for x in gm[1]][4:8] == [0.0, 0.0, 9.0, 0.0] and int(gm[2][1]) == 4
            and [float(x) for x in gm[0]][0:4] == [0.1, 0.2, 0.1, 0.1],
            "X0: readMine: a row is read Head Chest Legs Hands -> slot order Head Chest Hands Legs; a bad row keeps its default")
    K.check(Mine.checkRow("garmor.mining[cobalt]", "0.5 0.7 0.5 0.3|0 0 0 0|3") is None and "tiers are" in str(Mine.checkRow("garmor.mining[gold]", "0 0 0 0|0 0 0 0|0"))
            and "always stay" in str(Mine.checkRow("garmor.mining[iron]", None)) and "Write" in str(Mine.checkRow("garmor.mining[iron]", "1 2 3|0 0 0 0|1"))
            and "Write" in str(Mine.checkRow("garmor.mining[iron]", "1 2 3 4|0 0 0 0|5")) and "Write" in str(Mine.checkRow("garmor.mining[iron]", "1 2 3 101|0 0 0 0|1")),
            "X0: the Server Setup check of a tier row (tier name, 4 + 4 numbers 0-100, lamp 0-4, rows never removed)")
    K.check(Set.checkSet("set[mining_iron]", "Iron Mining Set|4|mfort+1.5") is None and Set.checkSet("set[mining_adamantite]", "A|4|mfort+5.5 mpow+10 spd+5") is None
            and "Mining Set's bonus" in str(Set.checkSet("set[mining_iron]", "Iron Mining Set|4|mfort+1 hp+50"))
            and Set.checkSet("set[quest_x]", "Q|4|hp+50 mfort+2") is None and "Unknown bonus words: mfort+0" in str(Set.checkSet("set[x]", "Q|4|mfort+0"))
            and "mfort mwis mpow" in str(Set.checkSet("set[x]", "Q|4|bogus+1")),
            "X0: the Armor sets check takes decimal mining words; a Mining Set takes mfort / mwis / mpow / spd only; mfort+0 is refused")
    K.check(abs(float(Mine.words("mfort+2.5 mpow+5 spd+5 mwis+1.25 foo+3")[0]) - 2.5) < 1e-9 and float(Mine.words("mfort+2.5 mpow+5")[2]) == 5.0
            and float(Mine.words("mwis+1.25")[1]) == 1.25 and str(Mine.wordsText("mfort+5.5 mpow+10 spd+5")) == "Mining Fortune +5.5, Mining Power +10%",
            "X0: the bonus words (mfort / mwis / mpow, decimals, others ignored) and their text")

    # ============================================================================ X1 the 28 ids + the bag pool
    ids = [str(x) for x in Mine.IDS]
    K.check(ids == [mid(t, sl) for t in TIERS for sl in SLOTS] and all(ITEM.getAssetMap().getAsset(i) is not None for i in ids)
            and all(str(ITEM.getAssetMap().getAsset(i).getArmor().getArmorSlot()) == SLOTS[k % 4] for k, i in enumerate(ids)),
            "X1: all 28 ids are in the real Item store with ArmorSlot Head / Chest / Hands / Legs (Onyxium Head / Chest / Legs included)")
    K.check(all(bool(Mine.isPiece(i)) for i in ids) and not bool(Mine.isPiece("Armor_Bronze_Chest")) and not bool(Mine.isPiece("Armor_Iron_Head_Red"))
            and not bool(Mine.isPiece(None)) and int(Mine.tier("Armor_Cobalt_Legs")) == 3 and str(Mine.setFor("Armor_Onyxium_Hands")) == "mining_onyxium",
            "X1: exact ids only (no Bronze, no Armory recolour prefix match), tier + set by id")
    pt = Pool.table()
    okp = [bool(x) for x in pt[2]]
    in_pool = [i for i in ids if int(Pool.idIdx(i)) >= 0 and okp[int(Pool.idIdx(i))]]
    heavy = {}
    for k in range(len(okp)):
        tk = str(Pool.T_KEY[int(Pool.P_T[k])])
        if okp[k] and int(Pool.P_AT[k]) == 1 and tk.startswith("Armor_"):
            heavy.setdefault(tk, []).append(str(Pool.P_ID[k]))
    K.check(not in_pool and sorted(heavy) == ["Armor_Chest", "Armor_Hands", "Armor_Head", "Armor_Legs"] and all(heavy.values())
            and any("Bronze" in x for x in heavy["Armor_Chest"]),
            "X1: none of the 28 in the bag pool (bags, unidentified roll, chest extras); Heavy bags still hold every slot: %s"
            % dict((k, len(v)) for k, v in heavy.items()))
    Cfg.GM_ON = False
    Pool.TAB = None
    pt0 = Pool.table()
    back = [i for i in ids if int(Pool.idIdx(i)) >= 0 and bool(pt0[2][int(Pool.idIdx(i))])]
    Cfg.GM_ON = True
    Pool.TAB = None
    K.check(len(back) == 28, "X1: garmor.miningOn off puts the 28 back into the pool (0.2.14): %d" % len(back))
    # fix round (safety critic MEDIUM 1): an OLD Heavy chest bag Lv 38-42 (made by 0.2.11-0.2.14, at=Heavy stored) whose range lost its metal pieces
    tyc = int(Pool.typeIdx("Armor_Chest"))
    Cfg.GM_ON = False
    Pool.TAB = None
    lc_old = int(Pool.levelCount(JInt(tyc), JInt(1), JInt(38), JInt(42)))
    Cfg.GM_ON = True
    Pool.TAB = None
    lc_new = int(Pool.levelCount(JInt(tyc), JInt(1), JInt(38), JInt(42)))
    top_ = int(Cfg.LOOT_TOP)
    for sl_ in SLOTS:
        ty_ = int(Pool.typeIdx("Armor_" + sl_))
        lvh, lv0 = list(Pool.levels(JInt(ty_), JInt(1))), list(Pool.levels(JInt(ty_), JInt(0)))
        K.notes.append("X1: Armor_%s levels 1-%d without a Heavy piece: %s; without ANY armor: %s" % (
            sl_, top_, [L for L in range(1, top_ + 1) if not lvh[L]], [L for L in range(1, top_ + 1) if not lv0[L]]))
    obag = Unid.boxSub(JInt(tyc), JInt(1), JInt(0), JInt(38), JInt(42), JInt(0))
    ow = Unid.why(obag)
    op = Unid.open(obag, U1)
    opid = None if op is None else str(op[0])
    oplv = None if op is None else int(op[1])
    gdx = None if op is None else op[2].clone()
    if gdx is not None:
        gdx.put("box", Unid.boxSub(JInt(tyc), JInt(1), JInt(0), JInt(38), JInt(42), JInt(0)))
    orw = None if gdx is None else Unid.rerollWhy(gdx)
    orr = None if gdx is None else Unid.reroll(gdx, U1)
    hb = Unid.open(Unid.boxSub(JInt(tyc), JInt(1), JInt(0), JInt(20), JInt(23), JInt(0)), U1)
    tyh = int(Pool.typeIdx("Armor_Hands"))
    h14 = Unid.open(Unid.boxSub(JInt(tyh), JInt(1), JInt(0), JInt(14), JInt(14), JInt(0)), U1)
    a40 = Unid.open(Unid.boxSub(JInt(tyc), JInt(0), JInt(0), JInt(38), JInt(42), JInt(0)), U1)
    ft = [int(x) for x in Unid.fit(JInt(tyc), JInt(1), JInt(38), JInt(42))]
    K.check(lc_old > 0 and lc_new == 0 and ow is None and opid is not None and not bool(Mine.isPiece(opid)) and int(Pool.atOfId(opid)) == 1
            and int(Data.slotOf(opid)) == 2 and 35 <= oplv <= 37 and ft == [1, 35, 37] and orw is None and orr is not None
            and not bool(Mine.isPiece(str(orr[0]))) and hb is not None and int(Pool.atOfId(str(hb[0]))) == 1
            and [int(x) for x in Unid.fit(JInt(tyc), JInt(1), JInt(20), JInt(23))] == [1, 20, 23]
            and h14 is not None and int(h14[1]) == 14 and not bool(Mine.isPiece(str(h14[0])))
            and a40 is not None and not bool(Mine.isPiece(str(a40[0]))) and Unid.why(Unid.boxSub(JInt(tyc), JInt(0), JInt(0), JInt(38), JInt(42), JInt(0))) is None,
            "X1 fix: an OLD Heavy chest bag Lv 38-42 (Heavy candidates 0.2.14 %d -> now %d; no armor at all at 38-44) still opens (why %s) with the "
            "nearest Heavy chest %s Lv %s (fit %s), re-identify works (%s); a Heavy bag whose range keeps a Heavy piece is unchanged (%s); a Heavy "
            "hands bag Lv 14 -> any hands Lv 14 (%s); an any-type chest bag Lv 38-42 opens (%s)"
            % (lc_old, lc_new, ow, opid, oplv, ft, None if orr is None else str(orr[0]), None if hb is None else str(hb[0]),
               None if h14 is None else str(h14[0]), None if a40 is None else str(a40[0])))

    # ============================================================================ X2 the table sums (Java tables)
    F_, W_ = [float(x) for x in Cfg.GM_TAB[0]], [float(x) for x in Cfg.GM_TAB[1]]
    st = Cfg.STAB
    sid = [str(x) for x in st[0]]
    fulls, wis = [], []
    for t in range(7):
        si = sid.index("mining_" + TIERS[t].lower())
        fulls.append(round(sum(F_[t * 4:t * 4 + 4]) + float(Mine.words(st[4][si])[0]), 2))
        wis.append(round(sum(W_[t * 4:t * 4 + 4]), 2))
    K.check(fulls == FULL and max(fulls) <= 15.0 and wis == [0.0, 0.0, 0.0, 2.0, 4.0, 6.0, 8.0] and max(wis) <= 10.0 and [int(x) for x in Cfg.GM_TAB[2]] == [1, 2, 2, 3, 3, 4, 4],
            "X2: the loaded tables = spec 4: full sets %s (<= 15), Wisdom %s (<= 10), lamps 1 2 2 3 3 4 4" % (fulls, wis))

    # ============================================================================ X3 the Mining gate
    skills(mining=30, combat=49)
    cob = piece("Cobalt", "Chest", 25)
    cd = doc(cob)
    c30 = Gate.check(U1, "Armor_Cobalt_Chest", cd, JInt(25))
    skills(mining=12, combat=49)
    c12 = Gate.check(U1, "Armor_Cobalt_Chest", cd, JInt(25))
    gl = View.gateLine(U1, "Armor_Cobalt_Chest", cd, JInt(25))
    act12 = bool(Stats.active(U1, "Armor_Cobalt_Chest", cd))
    K.check(bool(c30[0]) and str(c30[1]) == "Mining" and int(c30[3]) == 30 and not bool(c12[0]) and bool(c12[4])
            and str(gl[0]) == "Lv 25 - Requires Mining 25 (you: 12)" and bool(gl[2]) and not act12,
            "X3: the gate of a metal piece is Mining (Combat 49 does not help): Mining 30 ok, Mining 12 = inactive + red '%s'" % gl[0])
    bro = Data.put(IS("Armor_Bronze_Chest", JInt(1)), Roll.newDoc("Armor_Bronze_Chest", JInt(0), True, "craft", JInt(15)), U1)
    cb = Gate.check(U1, "Armor_Bronze_Chest", doc(bro), JInt(15))
    K.check(str(cb[1]) != "Mining", "X3: Bronze (combat Heavy) keeps the class gate: %s" % cb[1])

    # ============================================================================ X4 new documents
    skills(mining=30, combat=10)
    cr = Roll.craftDoc("Armor_Cobalt_Chest", U1)
    skills(mining=12, combat=10)
    cr12 = Roll.craftDoc("Armor_Cobalt_Chest", U1)
    cr12s = Data.put(IS("Armor_Cobalt_Chest", JInt(1)), cr12, U1)
    K.check(int(Data.rarity(cr)) == R_SET and int(Lvl.level("Armor_Cobalt_Chest", cr)) == 30 and Data.mods(cr).size() == 0 and bool(Data.identified(cr))
            and str(cr.getString("set").getValue()) == "mining_cobalt" and int(Lvl.level("Armor_Cobalt_Chest", cr12)) == 25
            and not bool(Stats.active(U1, "Armor_Cobalt_Chest", doc(cr12s))) and str(Roll.craftSkill("Armor_Cobalt_Chest", U1)) == "Mining"
            and str(Roll.craftLabel("Armor_Cobalt_Chest", U1)) == "Mining",
            "X4: craft Armor_Cobalt_Chest by Mining 30 / class 10 -> Lv 30, Set, 0 modifiers, set mining_cobalt; by Mining 12 -> Lv 25 (clamp) and inactive")
    xs, xn = int(Roll.craftXp("Armor_Cobalt_Chest", JInt(R_SET))), int(Roll.craftXp("Armor_Cobalt_Chest", JInt(0)))
    K.check(xs == xn and xs > 0 and int(Roll.craftXp("Armor_Bronze_Chest", JInt(R_SET))) > int(Roll.craftXp("Armor_Bronze_Chest", JInt(0))),
            "X4: a Set mining craft pays the Normal Smithing XP row (%d), other Set gear keeps the Set row" % xs)
    g1 = Roll.newDoc("Armor_Iron_Legs", JInt(4), False, "admin", JInt(60))
    K.check(int(Data.rarity(g1)) == R_SET and bool(Data.identified(g1)) and int(Lvl.level("Armor_Iron_Legs", g1)) == int(Lvl.band("Armor_Iron_Legs")[1])
            and Data.mods(g1).size() == 0, "X4: any new document (admin give: Fabled, unidentified, Lv 60) = identified Set, level kept in the band")
    md = Tag.unid(IS("Armor_Iron_Head", JInt(1)), JInt(1), JInt(33), "mob")
    mc = Tag.unid(IS("Armor_Thorium_Hands", JInt(1)), JInt(2), JInt(-1), "zone")
    mdd, mcd = doc(md), doc(mc)
    K.check(not bool(Unid.isBox(md.getItemId())) and int(Data.rarity(mdd)) == R_SET and bool(Data.identified(mdd)) and int(Lvl.level("Armor_Iron_Head", mdd)) == 23
            and str(mdd.getString("src").getValue()) == "drop" and int(Data.rarity(mcd)) == R_SET and int(Lvl.level("Armor_Thorium_Hands", mcd)) == int(Lvl.band("Armor_Thorium_Hands")[0])
            and str(mcd.getString("src").getValue()) == "chest",
            "X4: a native mob drop (mob Lv 33) = an identified Set Iron helmet Lv 23 (band cap), a chest one at its band start - never a bag")
    fi = Unid.fromItem(IS("Armor_Iron_Head", JInt(1)), JInt(1), JInt(20), "mob")
    fb = BoxFn().apply(OA([IS("Armor_Iron_Head", JInt(1)), JInt(20), "luggage", JInt(2), None]))
    ch = SIC(JShort(4))
    ch.setItemStackForSlot(JShort(0), IS("Armor_Iron_Head", JInt(1)))
    sp0 = int(Tag.spread(ch, JInt(0), JInt(20), "zone"))
    f9 = Fn(JInt(9)).apply(OA([IS("Armor_Copper_Legs", JInt(1)), "mob"]))
    K.check(fi is None and fb is None and sp0 == 0 and f9 is not None and int(Data.rarity(doc(f9))) == R_SET and bool(Data.identified(doc(f9))),
            "X4: fromItem / gear:fn:box with the stack / spread refuse a metal piece; gear:fn mode 9 (mob tag) makes an identified Set piece")
    W = Wall()
    K.check(str(W.apply(cob)) == REASON, "X4: a new Mining Set piece is behind the market wall (Set rarity - economy lock; see the report)")

    # ============================================================================ X5 Health / resistance = 0.2.14 at share 100
    apply()
    hr = []
    for t in ("Copper", "Iron", "Cobalt", "Mithril"):
        for sl in ("Head", "Chest"):
            iid = mid(t, sl)
            b = list(Lvl.band(iid))
            for L in (b[0], b[1]):
                d = Roll.newDoc(iid, JInt(R_SET), True, "t", JInt(L))
                a1 = [float(x) for x in Base.armorTarget(iid, d)]
                Cfg.GM_ON = False
                a0 = [float(x) for x in Base.armorTarget(iid, d)]
                Cfg.GM_ON = True
                Cfg.GM_SHARE = 60
                a6 = [float(x) for x in Base.armorTarget(iid, d)]
                Cfg.GM_SHARE = 100
                hr.append((iid, L, a1 == a0, abs(a6[0] - a0[0] * 0.6) < 1e-3 and abs(a6[1] - a0[1] * 0.6) < 1e-5))
    bd = Roll.newDoc("Armor_Bronze_Chest", JInt(0), True, "t", JInt(15))
    Cfg.GM_SHARE = 60
    bz = [float(x) for x in Base.armorTarget("Armor_Bronze_Chest", bd)]
    Cfg.GM_SHARE = 100
    K.check(all(x[2] and x[3] for x in hr) and bz == [float(x) for x in Base.armorTarget("Armor_Bronze_Chest", bd)],
            "X5: Health / resistance of Copper / Iron / Cobalt / Mithril pieces at band start + top = 0.2.14 exactly at share 100; share 60 = 60 %%; Bronze untouched: %s"
            % [x for x in hr if not (x[2] and x[3])])

    # ============================================================================ X6 compute / note / lamp / caps / old pieces
    skills(mining=49)

    def note(a):
        return [round(float(x), 4) for x in Mine.note(U1, a)]
    n4 = note(fullset("Cobalt"))
    n3 = note(wear(piece("Cobalt", "Head"), piece("Cobalt", "Chest"), None, piece("Cobalt", "Legs")))
    nmx = note(wear(piece("Cobalt", "Head"), piece("Cobalt", "Chest"), piece("Cobalt", "Hands"), piece("Mithril", "Legs")))
    nad = note(fullset("Adamantite"))
    non = note(fullset("Onyxium"))
    K.check(n4 == [6.0, 2.0, 8.0, 0.0, 3.0] and n3 == [1.7, 1.7, 0.0, 0.0, 3.0] and nmx == [2.4, 3.0, 0.0, 0.0, 3.0] and nad == [8.3, 4.0, 10.0, 5.0, 3.0]
            and non == [15.0, 8.0, 15.0, 10.0, 4.0],
            "X6: 4 Cobalt = Fortune 6.0 / Wisdom 2 / Power 8 / lamp Rare(3); 3 of 4 = pieces only; Cobalt x3 + Mithril legs = pieces only; Adamantite full "
            "= 8.3 + Speed 5; Onyxium full = 15.0 (= the cap) + Speed 10: %s %s %s %s %s" % (n4, n3, nmx, nad, non))
    skills(mining=30)
    nul = note(wear(piece("Cobalt", "Head"), piece("Cobalt", "Chest"), piece("Cobalt", "Hands"), piece("Cobalt", "Legs", 38)))
    K.check(nul == [1.5, 1.5, 0.0, 0.0, 3.0], "X6: one under-level piece (Legs Lv 38, Mining 30): its lines 0 and no set bonus: %s" % nul)
    skills(mining=49)
    Cfg.GM_FCAP = 10.0
    ncap = note(fullset("Onyxium"))
    Cfg.GM_FCAP = 15.0
    K.check(ncap[0] == 10.0, "X6: armor.fortune.cap 10 caps the Onyxium full set at 10: %s" % ncap)
    lk = "gear:lamp:" + str(U1)
    note(fullset("Cobalt"))
    l1 = br.get(lk)
    note(wear(None, piece("Cobalt", "Chest")))
    l2 = br.get(lk)
    note(wear(piece("Mithril", "Head")))
    l3 = br.get(lk)
    skills(mining=30)
    note(wear(piece("Mithril", "Head", 45)))
    l4 = br.get(lk)
    skills(mining=49)
    note(wear(piece("Copper", "Head")))
    l5 = br.get(lk)
    Fx.forget(U1)
    l6 = br.get(lk)
    K.check(int(l1) == 3 and l2 is None and int(l3) == 4 and l4 is None and int(l5) == 1 and l6 is None and Mine.ARM.get(U1) is None,
            "X6: gear:lamp:<uuid>: Cobalt helmet 3, helmet off -> removed, Mithril 4, under-level Mithril helmet -> removed, Copper 1, leave (GearFx.forget) -> removed: %s"
            % [l1, l2, l3, l4, l5, l6])
    # fix round (engine critic LOW 1): a late pass for a player who LEFT (GearTool.forget = PlayerDisconnectEvent) posts nothing; PlayerReady (back) restores
    note(fullset("Cobalt"))
    Tool.forget(U1)
    ng = Mine.note(U1, fullset("Cobalt"))
    lg, ag = br.get(lk), Mine.ARM.get(U1)
    Tool.back(U1)
    nb_ = note(fullset("Cobalt"))
    K.check(ng is None and lg is None and ag is None and nb_[0] == 6.0 and int(br.get(lk)) == 3,
            "X6 fix: GearMine.note after the player left: no cache, no gear:lamp key (%s %s); after PlayerReady the next pass posts again" % (lg, ag))
    Fx.forget(U1)
    # an OLD 0.2.14 Rare Iron chest (3 rolled modifiers) reads byte-identical, counts for the Iron set by id, shows the mining lines
    oldc = piece("Iron", "Chest", 18, r=2, old=True)
    od0 = Data.gearDoc(oldc.getMetadata())
    j0 = str(oldc.getMetadata().toJson())
    sc = Stamp.stampStack(oldc, U1, None)
    j1 = str(sc.getMetadata().toJson())
    a_old = wear(piece("Iron", "Head"), oldc, piece("Iron", "Hands"), piece("Iron", "Legs"))
    nold = note(a_old)
    Set.note(U1, a_old)
    tip = jl(View.plain("Armor_Iron_Chest", doc(oldc), U1))
    K.check(Data.mods(od0).size() == 3 and int(Data.rarity(od0)) == 2 and not od0.containsKey("set") and j0 == j1 and str(doc(oldc).toJson()) == str(od0.toJson())
            and nold[0] == 2.3 and "Mining Fortune +0.3" in tip and "Set: Iron Mining Set (4/4)" in tip
            and any(x.startswith("Full set bonus: Mining Fortune +1.5 (pickaxe or shovel in hand)") for x in tip) and W.apply(oldc) is None
            and any(x.startswith("Lv 18 - Requires Mining 18") for x in tip),
            "X6: an old Rare Iron chest (3 modifiers, no set field) stays byte-identical, counts for the Iron set by id (full 2.3), shows the "
            "mining lines + the set block + 'Requires Mining', and is NOT walled: %s" % [x for x in tip if "ining" in x or "Set" in x])

    # ============================================================================ X7 the Fortune + Wisdom post (skill:bonus "gear")
    skills(mining=49)
    note(fullset("Cobalt"))

    def held(iid, lvl=None):
        Tool.LAST.clear()
        s_ = IS(iid, JInt(1)) if lvl is None else Data.put(IS(iid, JInt(1)), Roll.newDoc(iid, JInt(0), True, "craft", JInt(lvl)), U1)
        stt = Tool.held(U1, s_)
        return gsrc(), (None if stt is None else [float(x) for x in stt])
    pk, pst = held("Tool_Pickaxe_Cobalt", 30)
    sh, sst = held("Tool_Shovel_Cobalt", 30)
    ht, hst = held("Tool_Hatchet_Cobalt", 30)
    sw, _x = held("Weapon_Sword_Iron")
    em = Tool.held(U1, None)
    emg = gsrc()
    K.check(pk is not None and abs(pk["dd.mining"] - (pst[5] + 6.0) / 100.0) < 1e-9 and pk["only.mining"] == "Rock_,Rubble_,Ore_" and abs(pk["xp.mining"] - 0.02) < 1e-9
            and sh is not None and abs(sh["dd.mining"] - (sst[5] + 6.0) / 100.0) < 1e-9 and sh["only.mining"] == "Soil_" and abs(sh["xp.mining"] - 0.02) < 1e-9
            and ht is not None and abs(ht["dd.foraging"] - hst[5] / 100.0) < 1e-9 and "xp.foraging" not in ht and "dd.mining" not in ht
            and sw is None and emg is None,
            "X7: pickaxe + 4 Cobalt: dd.mining = (tool %.1f + 6.0) / 100, only rock / ore, xp.mining 0.02; shovel -> Soil_; hatchet = its own Fortune only; "
            "sword / empty hand -> no source: %s | %s | %s" % (pst[5] if pst else -1, pk, sh, ht))
    skills(mining=30)
    note(fullset("Cobalt"))
    ul, ust = held("Tool_Pickaxe_Mithril", 45)
    K.check(ust is not None and ust[3] == 0.0 and ul is not None and abs(ul["dd.mining"] - 0.06) < 1e-9 and abs(ul["xp.mining"] - 0.02) < 1e-9,
            "X7: an UNDER-LEVEL pickaxe (Lv 45, Mining 30): the tool part is 0, the armor part is still posted (0.06 / 0.02): %s" % ul)
    skills(mining=49)
    note(wear())
    nt, nst = held("Tool_Pickaxe_Cobalt", 30)
    K.check(nt is not None and abs(nt["dd.mining"] - nst[5] / 100.0) < 1e-9 and "xp.mining" not in nt, "X7: no armor = exactly the 0.2.14 tool post: %s" % nt)

    # ============================================================================ X8 Mining Power
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    bmap = BTY.getAssetMap().getAssetMap()
    soils = sorted(str(k) for k in bmap.keySet() if bmap.get(k) is not None and bmap.get(k).getGathering() is not None
                   and bmap.get(k).getGathering().getBreaking() is not None and str(bmap.get(k).getGathering().getBreaking().getGatherType()) == "Soils")
    LOG, STONE, GRASS = bmap.get("Wood_Oak_Trunk"), bmap.get("Rock_Stone"), bmap.get(([x for x in soils if x.startswith("Soil_")] + soils)[0])

    def hit(iid, lvl, b_, d=0.3):
        Tool.LAST.clear()
        s_ = Data.put(IS(iid, JInt(1)), Roll.newDoc(iid, JInt(0), True, "craft", JInt(lvl)), U1) if lvl else IS(iid, JInt(1))
        return float(Tool.onDamage(U1, s_, b_, JFloat(d))), (float(Tool.stats(U1, s_)[4]) if Tool.stats(U1, s_) is not None else 1.0)
    note(fullset("Cobalt"))
    ps, pf = hit("Tool_Pickaxe_Cobalt", 30, STONE)
    pl, _f = hit("Tool_Pickaxe_Cobalt", 30, LOG)
    ss, sf = hit("Tool_Shovel_Cobalt", 30, GRASS)
    sst2, _f2 = hit("Tool_Shovel_Cobalt", 30, STONE)
    hl, hf = hit("Tool_Hatchet_Cobalt", 30, LOG)
    skills(mining=30)
    note(fullset("Cobalt"))
    us_, _f3 = hit("Tool_Pickaxe_Mithril", 45, STONE)
    skills(mining=49)
    note(wear())
    ps0, pf0 = hit("Tool_Pickaxe_Cobalt", 30, STONE)
    K.check(abs(ps - 0.3 * pf * 1.08) < 1e-5 and abs(pl - 0.3) < 1e-7 and abs(ss - 0.3 * sf * 1.08) < 1e-5 and abs(sst2 - 0.3) < 1e-7
            and abs(hl - 0.3 * hf) < 1e-5 and abs(us_ - 0.3 * 1.08) < 1e-5 and abs(ps0 - 0.3 * pf0) < 1e-5,
            "X8: Mining Power +8%% (Cobalt set): pickaxe on stone x tool x1.08, on a log vanilla; shovel on soil x1.08, on stone vanilla; hatchet = tool only; "
            "an under-level pickaxe x1.08 only; no armor = 0.2.14: %s" % [ps, pl, ss, sst2, hl, us_, ps0])
    # the REAL GearToolHitSys.handle through a stand-in chunk
    FU = JClass(FAKE_PKG + ".FakeUtil")
    for cn in ("com.hypixel.hytale.server.core.modules.entity.EntityModule", "com.hypixel.hytale.server.core.universe.Universe",
               "com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule"):
        FU.single(cn)
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    prx = us.allocateInstance(PRc.class_)
    jf(PRc, "uuid").set(prx, U1)
    jf(PRc, "username").set(prx, "Tester")
    FCh = JClass(FAKE_PKG + ".FakeChunk")
    chk = us.allocateInstance(FCh.class_)
    chk.comps = JClass("java.util.IdentityHashMap")()
    chk.comps.put(PRc.getComponentType(), prx)
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    ctor = [c for c in DBE.class_.getConstructors() if len(c.getParameterTypes()) == 5][0]
    pts = [str(p.getName()) for p in ctor.getParameterTypes()]
    JFl = JClass("java.lang.Float")

    def ev(s_, b_, d):
        args, nf = [], 0
        for p in pts:
            if p.endswith("ItemStack"):
                args.append(s_)
            elif p.endswith("BlockType"):
                args.append(b_)
            elif p == "float":
                args.append(JFl.valueOf(JFloat(1.0 if nf == 0 else d)))
                nf += 1
            else:
                args.append(JClass(p)(JInt(0), JInt(64), JInt(0)))
        return ctor.newInstance(JArray(JObject)(args))
    note(fullset("Cobalt"))
    Tool.LAST.clear()
    e1 = ev(Data.put(IS("Tool_Pickaxe_Cobalt", JInt(1)), Roll.newDoc("Tool_Pickaxe_Cobalt", JInt(0), True, "craft", JInt(30)), U1), STONE, 0.3)
    d0 = float(e1.getDamage())
    Hit().handle(JInt(0), chk, None, None, e1)
    K.check(abs(float(e1.getDamage()) - d0 * pf * 1.08) < 1e-5, "X8: the REAL GearToolHitSys.handle: pickaxe + Cobalt set on stone %.4f -> %.4f" % (d0, float(e1.getDamage())))

    # ============================================================================ X9 Speed through the REAL GearFx.armorPass
    FS, FBuf = JClass(FAKE_PKG + ".FakeStore"), JClass(FAKE_PKG + ".FakeBuffer")
    fst = us.allocateInstance(FS.class_)
    fst.comps = HM()
    buf = us.allocateInstance(FBuf.class_)
    buf.st = fst
    REFc = JClass("com.hypixel.hytale.component.Ref")
    ref = us.allocateInstance(REFc.class_)

    def apass(a):
        Fx.armorPass(U1, None, buf, ref, a, False)
        m_ = br.get("move:" + str(U1))
        e_ = None if m_ is None else m_.get("gear.armor")
        return None if e_ is None else round(float(e_.get("speed")), 5)
    ad = fullset("Adamantite")
    held("Tool_Pickaxe_Cobalt", 30)
    s_pick = apass(ad)
    held("Weapon_Sword_Iron")
    s_sword = apass(ad)
    held("Tool_Shovel_Cobalt", 30)
    s_shov = apass(ad)
    held("Tool_Pickaxe_Cobalt", 30)
    s_cob = apass(fullset("Cobalt"))
    tz = [int(x) for x in Stats.totals(U1, None, ad, None, True)]
    sp_per = float(Cfg.SPEED_PER)
    K.check(s_pick == round(5 * sp_per / 100.0, 5) and s_sword in (None, 0.0) and s_shov == s_pick and s_cob in (None, 0.0) and tz[int(Mine.I_SPD)] == 0,
            "X9: the REAL armor pass: Adamantite full set + pickaxe -> Speed %s (5 points x speed.per); sword in hand -> 0 at the next pass; shovel "
            "-> on; Cobalt (no spd) -> 0; the always-on totals never carry the Mining Set's spd" % s_pick)
    held("Tool_Pickaxe_Cobalt", 30)
    apass(fullset("Cobalt"))
    lb = br.get(lk)
    br.put("profile:busy:" + str(U1), "swap")
    apass(fullset("Cobalt"))
    lbusy, abusy = br.get(lk), Mine.ARM.get(U1)
    br.remove("profile:busy:" + str(U1))
    apass(fullset("Cobalt"))
    K.check(int(lb) == 3 and lbusy is None and abusy is None and int(br.get(lk)) == 3,
            "X9: profile:busy -> the lamp key and the mining cache are cleared; the next pass brings them back")
    Fx.forget(U1)

    # ============================================================================ X10 tooltip
    skills(mining=49)
    a10 = fullset("Cobalt")
    Set.note(U1, a10)
    hd = doc(a10.getItemStack(JShort(0)))
    t1 = jl(View.plain("Armor_Cobalt_Head", hd, U1))
    br.put("acc:lamp", "on")
    t2 = jl(View.plain("Armor_Cobalt_Head", hd, U1))
    br.remove("acc:lamp")
    a3 = wear(piece("Cobalt", "Head"), piece("Cobalt", "Chest"), piece("Cobalt", "Hands"))
    Set.note(U1, a3)
    t3 = jl(View.plain("Armor_Cobalt_Head", doc(a3.getItemStack(JShort(0))), U1))
    K.check("Lv 25 - Requires Mining 25" in t1 and "Mining Fortune +0.5" in t1 and "Mining Wisdom +0.5%" in t1 and "Mining lines work with a pickaxe or shovel in hand" in t1
            and "Set: Cobalt Mining Set (4/4)" in t1 and "Full set bonus: Mining Fortune +4, Mining Power +8% (pickaxe or shovel in hand)" in t1
            and not any(x.startswith("Lamp:") for x in t1) and "Lamp: Rare light (24 blocks)" in t2 and "Set: Cobalt Mining Set (3/4)" in t3
            and "Full set (all 4): Mining Fortune +4, Mining Power +8% (pickaxe or shovel in hand)" in t3 and any(x.startswith("SET ") for x in t1),
            "X10: the tooltip: Mining gate, the piece's lines, the green set block (4/4 / 3/4), the Lamp line only with acc:lamp on: %s" % t1)
    K.check(str(Set.activeText(U1, a10)).startswith("Cobalt Mining Set: Mining Fortune +4, Mining Power +8% (pickaxe or shovel in hand)")
            and "Mining Fortune +6" in str(Mine.meText(U1, a10)) and "mining armor on: 28 metal pieces" in str(Mine.statusText()),
            "X10: /gear lines (complete sets, the mining armor line) + the ready-line part: %s | %s" % (Set.activeText(U1, a10), Mine.meText(U1, a10)))
    # fix round (engine critic LOW 2): /gear during a profile swap posts no lamp
    Mine.clear(U1)
    br.put("profile:busy:" + str(U1), "swap")
    mb_ = str(Mine.meText(U1, a10))
    lbz = br.get("gear:lamp:" + str(U1))
    br.remove("profile:busy:" + str(U1))
    K.check("paused" in mb_ and lbz is None and Mine.ARM.get(U1) is None, "X10 fix: /gear while profile:busy: '%s', no gear:lamp posted (%s)" % (mb_, lbz))

    # ============================================================================ X11 reforge refused, level up works
    skills(mining=49)
    c11 = SIC(JShort(9))
    p11 = piece("Cobalt", "Chest", 25)
    c11.setItemStackForSlot(JShort(4), p11)
    PURSE[str(U1)] = 10 ** 7
    rf = Forge.reforge(c11, JInt(4), p11.getItemId(), Forge.fp(p11), U1, "Tester", False, None, None)
    p_after = PURSE[str(U1)]
    lu = Forge.levelUp(c11, JInt(4), p11.getItemId(), Forge.fp(p11), U1, "Tester", None, None)
    nd = doc(c11.getItemStack(JShort(4)))
    c11.setItemStackForSlot(JShort(5), oldc)
    rfo = Forge.reforge(c11, JInt(5), oldc.getItemId(), Forge.fp(oldc), U1, "Tester", False, None, None)
    K.check(int(rf[0]) == 0 and "fixed mining lines" in str(rf[1]) and p_after == 10 ** 7 and int(lu[0]) == 1 and int(Lvl.level("Armor_Cobalt_Chest", nd)) == 26
            and int(Data.rarity(nd)) == R_SET and Data.mods(nd).size() == 0 and int(rfo[0]) == 1,
            "X11: a Set mining piece: reforge refused before coins (%s); Level up works (Lv 25 -> 26, still Set, 0 modifiers); an OLD rolled piece still reforges (%s)"
            % (rf[1], rfo[1]))

    # ============================================================================ X12 pets:stats
    pk_ = "pets:stats:" + str(U1)

    def pmap(**kv):
        m_ = HM()
        for k, v in kv.items():
            m_.put(k.replace("__", "."), JObject(v, JClass("java.lang.Double")))
        return Colls.unmodifiableMap(m_)
    I = dict((k, int(Defs.sIndex(k))) for k in ("str", "cc", "cd", "def", "mp", "dmg"))
    br.remove("gear:extra:" + str(U1))
    br.put(pk_, pmap(str=2.5, cc=1.25, cd=0.5, swing__mining=5.0))
    x1 = [int(v) for v in Stats.extra(U1)]
    br.put("gear:extra:" + str(U1), "str:3,cc:1,def:4")
    x2 = [int(v) for v in Stats.extra(U1)]
    m3 = pmap(str=-0.5, mp=7.9, dmg=3.0)
    br.put(pk_, m3)
    x3 = [int(v) for v in Stats.extra(U1)]
    IDH = JClass("java.lang.System").identityHashCode
    same = IDH(Stats.pets(U1)) == IDH(Stats.pets(U1))
    tt = [int(v) for v in Stats.totals(U1, None, wear(), None, True)]
    br.remove(pk_)
    x4 = [int(v) for v in Stats.extra(U1)]
    br.remove("gear:extra:" + str(U1))
    x5 = Stats.extra(U1)
    K.check((x1[I["str"]], x1[I["cc"]], x1[I["cd"]], sum(x1)) == (2, 1, 0, 3) and (x2[I["str"]], x2[I["cc"]], x2[I["def"]]) == (5, 2, 4)
            and (x3[I["str"]], x3[I["mp"]], x3[I["dmg"]], x3[I["cc"]], x3[I["def"]]) == (2, 7, 3, 1, 4) and same and tt[I["mp"]] == 7
            and (x4[I["str"]], x4[I["mp"]]) == (3, 0) and x5 is None,
            "X12: pets:stats summed + floored (2.5 -> 2, 1.25 -> 1, swing.* skipped), added to gear:extra (str 3 + 2), a new map object re-parsed "
            "(-0.5 -> -1), the totals carry it, removed -> gear:extra only: %s" % [(x1[I["str"]], x1[I["cc"]]), (x2[I["str"]], x2[I["cc"]]), (x3[I["str"]], x3[I["mp"]])])

    # ============================================================================ X13 sets: addTo / hp skip the Mining Sets; other sets keep G1
    SP = props(set__qset="Quest Guard,4,hp+100 def+10 mfort+2")
    apply(SP)
    qa = wear(*[Data.put(IS(mid("Iron", sl), JInt(1)), Roll.newDoc(mid("Iron", sl), JInt(R_SET), True, "q", JInt(15)), U1) for sl in SLOTS])
    for k in range(4):
        s_ = qa.getItemStack(JShort(k))
        d_ = doc(s_).clone()
        d_.put("set", BS("qset"))
        qa.setItemStackForSlot(JShort(k), Data.put(IS(s_.getItemId(), JInt(1)), d_, U1))
    cq = [int(x) for x in Set.counts(Cfg.STAB, U1, qa)]
    ids13 = [str(x) for x in Cfg.STAB[0]]
    nq = note(qa)
    tq = [int(x) for x in Stats.totals(U1, None, qa, None, True)]
    K.check(cq[ids13.index("qset")] == 4 and cq[ids13.index("mining_iron")] == 0 and tq[int(Defs.sIndex("def"))] == 10 and float(Set.hp(U1, qa)) == 100.0
            and nq[0] == round(0.8 + 2.0, 4),
            "X13: Iron pieces with a quest set field belong ONLY to that set (Iron Mining Set 0/4): its def / hp stay always-on (G1), its mfort word "
            "rides the mining path (0.8 pieces + 2 = %s)" % nq[0])
    ad13 = fullset("Adamantite")
    K.check(float(Set.hp(U1, ad13)) == 0.0 and [int(x) for x in Stats.totals(U1, None, ad13, None, True)][int(Mine.I_SPD)] == 0
            and str(Set.bonusText(Cfg.STAB, JInt(ids13.index("mining_adamantite")))) == "Mining Fortune +5.5, Mining Power +10%, +5 Speed (pickaxe or shovel in hand)"
            and str(Set.bonusText(Cfg.STAB, JInt(ids13.index("qset")))) == "Mining Fortune +2, +10 Defense, +100 Health (pickaxe or shovel in hand)",
            "X13: a complete Mining Set adds no always-on stat / Health; bonus texts: %s" % Set.bonusText(Cfg.STAB, JInt(ids13.index("mining_adamantite"))))
    apply()

    # ============================================================================ X14 garmor.miningOn off = 0.2.14
    apply(props(garmor__miningOn="false"))
    skills(mining=1, combat=49)
    g0 = Gate.check(U1, "Armor_Cobalt_Chest", doc(cob), JInt(25))
    nd0 = Roll.newDoc("Armor_Cobalt_Chest", JInt(2), True, "craft", JInt(25))
    n0 = note(fullset("Cobalt"))
    t0 = jl(View.plain("Armor_Cobalt_Chest", doc(oldc), U1))
    sk0 = Roll.craftSkill("Armor_Cobalt_Chest", U1)
    K.check(not bool(Mine.isPiece("Armor_Cobalt_Chest")) and str(g0[1]) != "Mining" and int(Data.rarity(nd0)) == 2 and not nd0.containsKey("set")
            and n0 == [0.0, 0.0, 0.0, 0.0, 0.0] and not any("Mining" in x for x in t0) and Set.sidOf("Armor_Iron_Chest", doc(oldc)) is None
            and str(sk0) != "Mining" and "OFF" in str(Mine.statusText()),
            "X14: garmor.miningOn=false: class gate, rolled rarity, no set field, no lines, no set by id, craft skill not Mining (0.2.14 behaviour): %s" % t0[:3])
    apply()
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
                # branch targets move when the constant pool grows past 256 (ldc -> ldc_w): compare the instructions, not their offsets
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
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn, ("0.2.14", "0.2.15")), members(pb, cn, ("0.2.14", "0.2.15"))
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd]
    add = sorted(c[len(PKG):] for c in set(nb) - set(na))
    gone = sorted(c[len(PKG):] for c in set(na) - set(nb))
    print("C. class compare 0.2.14 -> 0.2.15: + %s - %s" % (add, gone))
    for k in sorted(diffs):
        print("   %-16s %s" % (k, ", ".join(diffs[k])[:600]))
    K.check(add == NEW_CLASSES and not gone, "C: classes added = %s, none removed: + %s - %s" % (NEW_CLASSES, add, gone))
    unexpected = sorted(set(diffs) - EXPECT_CHANGED)
    missing = sorted(EXPECT_CHANGED - set(diffs))
    K.check(not unexpected and not missing, "C: exactly the listed classes changed (unexpected %s, listed but unchanged %s)" % (unexpected, missing))
    want = {"GearGate": {"~m check"}, "GearBase": {"~m armorTarget"}, "GearPool": {"~m table"}, "GearUnid": {"~m fromItem", "+m fit", "~m why", "~m pick", "~m rerollWhy"},
            "GearTag": {"~m unid", "~m spread"}, "GearBoxFn": {"~m apply"}, "GearForge": {"~m reforge"}, "GearFx": {"~m armorPass", "~m forget"},
            "GearAdmin": {"~m me"}, "GearView": {"~m gateLine", "~m lines"},
            "GearRoll": {"~m newDoc", "~m craftSkill", "~m craftLabel", "~m craftXp"},
            "GearTool": {"+m postX", "~m post", "~m held", "~m onDamage"},
            "GearStats": {"+m gearExtra", "+m parsePets", "+m pets", "~m extra", "+f PCACHE", "~<clinit>"},
            "GearSet": {"+m sidOf", "+m tipLines", "~m tipLines", "~m bonusText", "~m counts", "~m addTo", "~m hp", "~m checkSet"}}
    bad = dict((k, (sorted(v - set(diffs.get(k, []))), sorted(set(diffs.get(k, [])) - v))) for k, v in want.items() if set(diffs.get(k, [])) != v)
    K.check(not bad, "C: the classes changed exactly where the patch says (missing / extra): %s" % bad)
    cfg = set(diffs.get("GearCfg", []))
    K.check({"+m migrate0215", "+m gmUpdate", "+m gmMissing", "+m gmDefaults", "+m readMine", "~m parseBonus", "~m apply", "+f GM_TAB", "+f GM_ON", "+f DGM_F"} <= cfg,
            "C: GearCfg gains the update, the reader, the fields, the parseBonus words: %s" % sorted(cfg))
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
    K.check(Cfg.gmUpdate(fresh) is None and Cfg.guUpdate(fresh) is None, "D: a fresh 0.2.15 file carries both markers (no update)")
    old = open(os.path.join(home, "config.properties"), "rb").read().decode("latin-1")
    BLOCK = fresh[fresh.index("# ---- Mining armor: the vanilla metal sets Copper..Onyxium (SkyyGear 0.2.15) ----"):]
    K.check("garmor" not in old and "set.mining_" not in old, "D: the live copy has no 0.2.15 key yet")
    # the live world may not have started on 0.2.14 yet (its marker missing): then migrate0214 runs first at the same start
    g14 = "SkyyGear 0.2.14 rarity update" in old
    base = old if g14 else str(Cfg.guUpdate(old)[0])
    K.notes.append("D: the live copy %s the 0.2.14 marker - %s" % ("has" if g14 else "lacks", "0.2.15 alone runs" if g14 else "0.2.14 then 0.2.15 run at the same start"))

    def upd(text):
        r = Cfg.gmUpdate(text)
        return None if r is None else (str(r[0]), [str(x) for x in r[1]], str(r[2]))
    r = upd(base)
    exp = base + "\n" + BLOCK if base.endswith("\n") else None
    K.check(r is not None and exp is not None and r[0] == exp and r[1] == [] and r[2].startswith("garmor.miningOn, garmor.miningShare")
            and r[2].endswith("set.mining_onyxium") and r[2].count(",") == 17,
            "D: the live file: the block appended = exactly the fresh file's block (18 keys), nothing else changed: %s" % (r[2] if r else None))
    K.check(upd(r[0]) is None, "D: the updated text carries the marker (run once)")
    rc = upd(base.replace("\n", "\r\n"))
    K.check(rc is not None and rc[0] == exp.replace("\n", "\r\n"), "D: a CRLF file keeps CRLF on every line (block included)")
    rn = upd(base.rstrip("\n"))
    K.check(rn is not None and rn[0] == exp.rstrip("\n"), "D: a file without a final newline: the block after its last line, still no final newline")
    ro = upd(old)
    K.check(ro is not None and ro[0] == old + "\n" + BLOCK, "D: an older (pre-0.2.14) shape gets the same block at its end")
    hand = base + "armor.fortune.cap=12\nset.mining_iron=My Iron,4,mfort+3\ngarmor.mining.copper=1 1 1 1,0 0 0 0,0\n"
    rh = upd(hand)
    K.check(rh is not None and rh[0].count("armor.fortune.cap=") == 1 and "armor.fortune.cap=12" in rh[0] and rh[0].count("set.mining_iron=") == 1
            and rh[0].count("garmor.mining.copper=") == 1 and len(rh[1]) == 3 and "garmor.mining.iron=" in rh[0],
            "D: keys already in the file are KEPT + noted (3), the rest added: %s" % (rh[1] if rh else None))
    # START TWICE on the scratch copy of the live folder (the real setup order: every older update, then 0.2.14, 0.2.15, then load)
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    files0 = sorted(os.path.relpath(os.path.join(a, f), home) for a, d, fs in os.walk(home) for f in fs)
    log0 = open(os.path.join(home, "config-changes.log"), "rb").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else b""
    snaps = []
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214", "migrate0215"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(os.path.join(home, "config.properties"), "rb").read())
        ids = sorted(str(x) for x in Cfg.STAB[0])
        K.check(bool(Cfg.GM_ON) and float(Cfg.GM_FCAP) == 15.0 and [x for x in ids if x.startswith("mining_")] == sorted("mining_" + t.lower() for t in TIERS)
                and [round(float(x), 2) for x in Cfg.GM_TAB[0]][12:16] == [0.5, 0.7, 0.3, 0.5],
                "D start %d: the loaded mining rows + the seven Mining Sets" % step)
    K.check(snaps[0] == exp.encode("latin-1"), "D start 1: the live copy = the expected text byte for byte")
    K.check(snaps[1] == snaps[0], "D start 2: nothing changes")
    # fix round (safety critic LOW 2): a marked file that lost set.mining_* rows is NOT rewritten (run-once) - the INFO line names them + the defaults
    K.check(str(Cfg.gmMissing(snaps[0].decode("latin-1"))) == "", "D fix: the updated live copy lacks no Mining Set row")
    cut = "\n".join(x for x in snaps[0].decode("latin-1").split("\n") if not x.startswith("set.mining_iron=") and not x.startswith("set.mining_onyxium="))
    K.check(str(Cfg.gmMissing(cut)) == "set.mining_iron, set.mining_onyxium"
            and str(Cfg.gmDefaults(cut)) == "set.mining_iron=Iron Mining Set,4,mfort+1.5; set.mining_onyxium=Onyxium Mining Set,4,mfort+10 mpow+15 spd+10"
            and Cfg.gmUpdate(cut) is None, "D fix: rows deleted after the update are named (%s), never re-added: %s" % (Cfg.gmMissing(cut), Cfg.gmDefaults(cut)))
    cfp = os.path.join(home, "config.properties")
    open(cfp, "wb").write(cut.encode("latin-1"))
    mr = str(Cfg.migrate0215())
    K.check(mr == "" and open(cfp, "rb").read() == cut.encode("latin-1"), "D fix: migrate0215 on that file writes nothing")
    open(cfp, "wb").write(snaps[0])
    files1 = sorted(os.path.relpath(os.path.join(a, f), home) for a, d, fs in os.walk(home) for f in fs)
    newf = sorted(set(files1) - set(files0))
    hb = [open(os.path.join(home, f), "rb").read() for f in newf if f.startswith("config-history")]
    K.check(any(b == base.encode("latin-1") for b in hb) and any(b == old.encode("latin-1") for b in hb) and all(f.startswith("config-history") for f in newf)
            and all(f.startswith("config-history") for f in set(files0) - set(files1)) and len(hb) == (1 if g14 else 2),
            "D: the History copy before 0.2.15 holds the bytes it saw (and 0.2.14's the original); only config-history files were added (the kit "
            "prunes its oldest copies past KEEP): %s %s"
            % (newf, [any(b_ == base.encode("latin-1") for b_ in hb), any(b_ == old.encode("latin-1") for b_ in hb), len(hb), sorted(set(files0) - set(files1))]))
    log1 = open(os.path.join(home, "config-changes.log"), "rb").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else b""
    addl = [x for x in log1[len(log0):].decode("utf-8", "replace").split("\n") if x.strip()]
    K.check(log1.startswith(log0) and not [x for x in addl if "0.2.15" in x] and all("SkyyGear 0.2.14" in x for x in addl),
            "D: no config-changes.log row from 0.2.15 (a pure addition - no value changed); only 0.2.14's own: %s" % addl)
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
        assert '"Version": "0.2.14"' in z_.read("manifest.json").decode("utf-8"), "the old jar is not 0.2.14"
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
