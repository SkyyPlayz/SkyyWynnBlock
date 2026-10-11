"""Harness for SkyyGear 0.2.16 (THE FIRST UNTIERED BATCH + gathering sets on the market; research/cloud/UT-First-Batch-Build.md). Build first:
    python tools/gear_0_2_16_patch.py && python SkyyGear/build_skyygear_0.2.16.py
    (the SkyyArmory part: python tools/armory_0_1_15_patch.py && python SkyyArmory/build_skyyarmory_0.1.15.py)

    python SkyyGear/test_skyygear_0.2.16.py [--jar <SkyyGear-0.2.16.jar>] [--old <SkyyGear-0.2.15.jar>] [--armory <SkyyArmory-0.1.15.jar>] [--dir <scratch>] [--keep]

The 0.2.11 harness's helpers (stand-ins F, verify A, the bare-server boot of V, the engine-access audit AA) are loaded from
SkyyGear/test_skyygear_0.2.11.py and run on the 0.2.16 jar (the 0.2.12 - 0.2.15 harnesses do the same).
  S  non-class entries 0.2.15 -> 0.2.16: only the 16 Untiered copies + their 32 pictures + the 4 arrow configs are added; manifest + lang change
     (the lang = the old bytes + 32 lines); every copy = its vanilla base JSON with ONLY the planned keys changed (no Recipe, Variant, the orange
     quality, Lv 15, own name / texture / icon; Short Notice + its 4 arrow vars); the arrow configs (x2 launch force + air cap, gravity 0);
     MUTANT: a copy that kept its Recipe fails the same check
  A  every class of the jar loads + verifies (-Xverify:all)
  V  the vanilla pack store by store + THE JAR as its own pack (engine validators on the 16 items + 4 arrow configs); the copies in the real
     Item store (orange quality, Variant, no recipe to generate - control: the Iron sword has one), the configs in the real ProjectileConfig store
  X  EVERY NEW CODE PATH EXECUTED on the real stores (-Xverify:all): X0 rows + fresh file + parse / checks; X1 rows usable (the 3 SkyyArmory
     ones missing in a SkyyGear-only server), the Bo bag type, the developer bows out of the pool, Mythic ids; X2 never craftable; X3 band /
     base twin; X4 documents + the fixed speed tier (+ lazy heal); X5 the totals (body lines at Lv 15 / 22 / 29, fixed lines, armor Damage
     without the slot filter - mutant: the filtered path drops it); X6 the hit tricks (pure + the REAL GearUtFx.onHit on stand-ins: backstab
     cone, low Health, shot range, knockback) + damage taken; X7 the max Health modifier on a REAL EntityStatMap + the Mana regen registry;
     X8 the orange bag sources (swap odds 2 % / luggage 1-2-4-8 % / never off-band, the REAL mobRoll / chestExtra / gear:fn:box, the type
     weights, identify + re-roll); X9 the market wall split; X10 tooltip; X11 switches; X12 the bridges (gear:fn:utfx, grant)
  Y  (the 3 SkyyArmory copies: SkyyArmory/test_skyyarmory_0.1.15.py R18)
  C  CLASS COMPARE 0.2.15 -> 0.2.16 (javassist members): GearUtFx added, only the listed classes / members differ
  D  THE ONE-TIME UPDATE migrate0216: synthetic files (fresh, LF / CRLF, no final newline, keys already there) + START TWICE on a scratch COPY
     of the live Skyy_SkyyGear folder (block appended, History copy, nothing else; the 2nd start changes nothing)
  AA THE ENGINE-ACCESS AUDIT
Scratch: tools/dev/scratch/ut02/gear (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.16"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "ut02")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "gear")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-0.2.15.jar")))      # read only
ARM_JAR = os.path.abspath(arg("--armory", os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.15.jar")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
AZ_PATH = os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Assets.zip")
PKG = "com.skyy.gear."
REASON = "Mythic, Untiered and quest / boss Set gear never goes on the market - trade it directly with another player."
SLOTS = ["Head", "Chest", "Hands", "Legs"]
GEAR_COPIES = (["Weapon_Sword_UT_Paperweight", "Weapon_Battleaxe_UT_Overtime", "Weapon_Daggers_UT_PocketKnife", "Weapon_Shortbow_UT_ShortNotice"]
               + ["Armor_UT_%s_%s" % (n, s) for n in ("FilingCabinet", "Courier", "Intern") for s in SLOTS])
BASES = dict([("Weapon_Sword_UT_Paperweight", "Weapon_Sword_Iron"), ("Weapon_Battleaxe_UT_Overtime", "Weapon_Battleaxe_Iron"),
              ("Weapon_Daggers_UT_PocketKnife", "Weapon_Daggers_Iron"), ("Weapon_Shortbow_UT_ShortNotice", "Weapon_Shortbow_Iron")]
             + [("Armor_UT_FilingCabinet_" + s, "Armor_Iron_" + s) for s in SLOTS] + [("Armor_UT_Courier_" + s, "Armor_Leather_Medium_" + s) for s in SLOTS]
             + [("Armor_UT_Intern_" + s, "Armor_Cloth_Cotton_" + s) for s in SLOTS])
ARMORY_IDS = ["Weapon_Staff_UT_Loophole", "Weapon_Wand_UT_SecondOpinion", "Weapon_Bo_UT_Turnstile"]
DEV_UT = ["Weapon_Shortbow_Ricochet", "Weapon_Shortbow_Combat", "Weapon_Shortbow_Test_Zoom"]
DEV_MY = ["Weapon_Shortbow_Vampire", "Weapon_Shortbow_Bomb", "Weapon_Shortbow_Pull"]
ALL_UT = GEAR_COPIES + ARMORY_IDS + DEV_UT
NEW_CLASSES = ["GearUtFx"]
EXPECT_CHANGED = {"GearCfg", "GearLevel", "GearBase", "GearSpeed", "GearRoll", "GearData", "GearStats", "GearView", "GearFx", "GearHitSys",
                  "GearArmorSys", "GearUt", "GearLoot", "GearBoxFn", "GearWall", "GearFn", "GearPool", "GearAdmin", "GearCmd", "SkyyGearPlugin",
                  "GearUnid", "GearIdent", "IdentifyPage",          # fix round (ut02 review): the Untiered re-roll
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
def copy_bad(cid, cj, base):
    """the planned change of a vanilla base item JSON -> the copy; returns the keys that differ otherwise (empty = exactly the plan)"""
    want = json.loads(json.dumps(base))
    for k in ("Recipe", "$Comment"):
        want.pop(k, None)
    want["TranslationProperties"] = {"Name": "server.items.%s.name" % cid, "Description": "server.items.%s.description" % cid}
    want["Quality"] = "Skyy_Gear_Untiered"
    want["Variant"] = True
    want["ItemLevel"] = 15
    want["Texture"] = "Items/SkyyGear/UT/%s.png" % cid
    want["Icon"] = "Icons/ItemsGenerated/%s.png" % cid
    if cid == "Weapon_Shortbow_UT_ShortNotice":
        iv = want.setdefault("InteractionVars", {})
        for n in range(4):
            iv["Primary_Shoot_Strength_%d" % n] = {"Interactions": [{"Parent": "Weapon_Shortbow_Primary_Shoot_Strength_%d" % n,
                                                                    "Config": "SkyyGear_UT_ShortNotice_Arrow_%d" % n}]}
    return sorted(k for k in set(want) | set(cj) if want.get(k) != cj.get(k))


def run_assets():
    sys.path.insert(0, TOOLS)
    import skyyart as SA
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    az = zipfile.ZipFile(AZ_PATH)
    azi = dict((os.path.basename(n)[:-5], n) for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(eb) - set(ea))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    want_add = sorted(["Server/Item/Items/SkyyGear/UT/%s.json" % c for c in GEAR_COPIES] + ["Common/Items/SkyyGear/UT/%s.png" % c for c in GEAR_COPIES]
                      + ["Common/Icons/ItemsGenerated/%s.png" % c for c in GEAR_COPIES]
                      + ["Server/ProjectileConfigs/SkyyGear/SkyyGear_UT_ShortNotice_Arrow_%d.json" % n for n in range(4)])
    check(added == want_add and not (set(ea) - set(eb)) and changed == ["Server/Languages/en-US/server.lang", "manifest.json"]
          and b'"0.2.16"' in eb["manifest.json"],
          "S: 0.2.15 -> 0.2.16 adds exactly the 16 copies + 32 pictures + 4 arrow configs; only the lang + manifest change: + %s ~ %s"
          % ([a for a in added if a not in want_add][:5], changed))
    lo, ln = ea["Server/Languages/en-US/server.lang"].decode("utf-8"), eb["Server/Languages/en-US/server.lang"].decode("utf-8")
    extra = ln[len(lo):].strip("\n").split("\n") if ln.startswith(lo) else None
    check(extra is not None and len(extra) == 32 and all(any(x.startswith("items.%s.%s = " % (c, k)) for x in extra) for c in GEAR_COPIES for k in ("name", "description"))
          and "items.Weapon_Sword_UT_Paperweight.name = The Paperweight" in extra
          and "items.Armor_UT_Courier_Hands.description = Untiered light armor." in extra
          and not [x for x in extra if ".description = " in x and x.count(".") > 3],
          "S: the lang = the 0.2.15 bytes + 32 lines (name + description of every copy; FIX: the description only names the kind - the ONE "
          "orange trade-off line comes from the ut.<id> row): %s" % (extra[:2] if extra else None))
    bad = {}
    for c in GEAR_COPIES:
        cj = json.loads(eb["Server/Item/Items/SkyyGear/UT/%s.json" % c].decode("utf-8"))
        base = json.loads(az.read(azi[BASES[c]]).decode("utf-8-sig"))
        d = copy_bad(c, cj, base)
        if d or "Recipe" in cj:
            bad[c] = d
        for p in (cj["Texture"], cj["Icon"]):
            w, h = SA.png_size(eb["Common/" + p])
            if not (w > 0 and h > 0) or ("Common/" + p) in az.namelist():
                bad[c + " " + p] = "bad picture"
    check(not bad, "S: every copy = its vanilla base JSON with ONLY the planned keys changed (no Recipe, Variant, orange quality, Lv 15, own name / "
          "texture / icon; Short Notice's 4 arrow vars); every picture a valid PNG that shadows nothing: %s" % bad)
    # MUTANT: a copy that kept its base's Recipe (or lost Variant) fails the same check
    pw = json.loads(eb["Server/Item/Items/SkyyGear/UT/Weapon_Sword_UT_Paperweight.json"].decode("utf-8"))
    bj = json.loads(az.read(azi["Weapon_Sword_Iron"]).decode("utf-8-sig"))
    m1 = dict(pw)
    m1["Recipe"] = bj["Recipe"]
    m2 = dict(pw)
    m2.pop("Variant")
    check(copy_bad("Weapon_Sword_UT_Paperweight", m1, bj) == ["Recipe"] and copy_bad("Weapon_Sword_UT_Paperweight", m2, bj) == ["Variant"],
          "S mutants: a copy that kept its Recipe / lost Variant FAILS the copy check (%s / %s)"
          % (copy_bad("Weapon_Sword_UT_Paperweight", m1, bj), copy_bad("Weapon_Sword_UT_Paperweight", m2, bj)))
    cbad = []
    for n in range(4):
        cj = json.loads(eb["Server/ProjectileConfigs/SkyyGear/SkyyGear_UT_ShortNotice_Arrow_%d.json" % n].decode("utf-8"))
        vj = json.loads(az.read("Server/ProjectileConfigs/Weapons/Shortbow/Projectile_Config_Arrow_Shortbow_Strength_%d.json" % n).decode("utf-8-sig"))
        ph = dict(vj["Physics"])
        ph["Gravity"] = 0
        ph["TerminalVelocityAir"] = vj["Physics"]["TerminalVelocityAir"] * 2
        if cj != {"Parent": "Projectile_Config_Arrow_Shortbow_Strength_%d" % n, "LaunchForce": vj["LaunchForce"] * 2, "Physics": ph}:
            cbad.append(n)
    check(not cbad, "S: the 4 Short Notice arrow configs = the vanilla Strength 0-3 configs as Parent, x2 launch force, x2 air speed cap, gravity 0: bad %s" % cbad)
    print("S. assets: 16 copies + 32 pictures + 4 arrow configs, the lang + 32 lines")


# ====================================================================================================== V + X (the engine child)
def run_engine(out):
    from jpype import JClass, JArray, JInt, JLong, JShort, JFloat, JDouble, JImplements, JOverride, JObject, JBoolean, JString
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
    E = H["engine_boot"](K)
    ITEM, us, jf = E["ITEM"], E["us"], E["jf"]
    K.check(set(E["fail"]) <= set(E["vfail"]), "V: the jar as its own pack: no failed store of its own (%s vs vanilla %s)" % (E["fail"], E["vfail"]))
    # the bare JVM lacks a few codecs / stats the game has: the vanilla base items log the SAME lines here (a copy's line with its base id in
    # place of the copy id must appear in the vanilla pack's own log) - anything else about a copy or an arrow config is ours
    vset = set(r[1] for r in E["vrec"])

    def vanilla_too(m_):
        for c_, b_ in BASES.items():
            if c_ in m_ and m_.replace(c_, b_) in vset:
                return True
        return False
    ours = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and ("SkyyGear" in r[1] or "_UT_" in r[1] or "ShortNotice" in r[1])
            and "SkyyGear_Spd" not in r[1]]
    real = [r for r in ours if not vanilla_too(r[1])]
    K.check(not real, "V: no SEVERE / WARNING about the Untiered copies or the arrow configs beyond the bare-boot lines their vanilla bases log too "
            "(the engine's validators ran on them; %d known lines): %s" % (len(ours) - len(real), real[:3]))
    K.notes.append("V: %d bare-boot lines about the copies that their vanilla base items log the same way (missing bare-JVM parents)" % (len(ours) - len(real)))
    P = lambda n: JClass(PKG + n)
    (Cfg, Defs, Data, Roll, Unid, Pool, Set, Wall, Fn, Stats, View, Lvl, Gate, BoxFn, Ut, Fx, Gear, Hit, Base, Speed, Loot, Mine) = [
        P(n) for n in ("GearCfg", "GearDefs", "GearData", "GearRoll", "GearUnid", "GearPool", "GearSet", "GearWall", "GearFn", "GearStats",
                       "GearView", "GearLevel", "GearGate", "GearBoxFn", "GearUt", "GearFx", "Gear", "GearHit", "GearBase", "GearSpeed",
                       "GearLoot", "GearMine")]
    UF = P("GearUtFx")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    BS = JClass("org.bson.BsonString")
    BI32 = JClass("org.bson.BsonInt32")
    Props = JClass("java.util.Properties")
    UUID = JClass("java.util.UUID")
    HM = JClass("java.util.HashMap")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    SR = JClass("java.io.StringReader")
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000b016")
    R_UT, R_MY, R_SET = int(Defs.R_UT), int(Defs.R_MY), int(Defs.R_SET)
    SI = lambda k: int(Defs.sIndex(k))
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

    def skills(combat=49):
        LEVELS.clear()
        LEVELS.update({"Mining": 49, "Combat": combat, "Foraging": 49, "Smithing": 0})
        br.put("skill:fn:level", SkillLv())
        br.put("class:skill:" + str(U1), "Combat")
        Gate.forget(U1)

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

    def ut(iid, lvl=20):
        return Data.put(IS(iid, JInt(1)), Roll.newDoc(iid, JInt(0), True, "test", JInt(lvl)), U1)

    def wear(*stacks):
        a = SIC(JShort(4))
        for k, s_ in enumerate(stacks):
            if s_ is not None:
                a.setItemStackForSlot(JShort(k), s_)
        return a

    def tot(weapon=None, armor=None):
        return [int(x) for x in Stats.totals(U1, weapon, armor, None, True)]
    apply()
    skills()

    # ============================================================================ X0 the rows, the fresh file, the parse / checks
    tail = FRESH.rstrip("\n").split("\n")
    gi = tail.index("# ---- The first Untiered batch + gathering sets on the market (SkyyGear 0.2.16) ----")
    blk = tail[gi:]
    K.check(blk[1].startswith("# SkyyGear 0.2.16 untiered batch (Skyy 2026-10-09)") and tail[gi - 1] == "" and len(blk) == 2 + 2 * 10 + 1 + 22 + 1 + 22
            and "utdrop.luggage=1 2 4 8" in blk and "ut.Weapon_Sword_UT_Paperweight=15,29,Hits 50% harder. Swings 40% slower." in blk
            and "utfx.Weapon_Sword_UT_Paperweight=str cd,dmg+7 swing=slow" in blk and "utfx.Armor_UT_FilingCabinet_Hands=def,hp+6.25 dmg-2" in blk
            and "gear.mythicItems=Weapon_Shortbow_Vampire,Weapon_Shortbow_Bomb,Weapon_Shortbow_Pull" in blk and "market.gatheringSets=true" in blk,
            "X0: the fresh file ends with the 0.2.16 block (heading, marker, 10 scalars, 22 ut rows, 22 utfx rows): %d lines" % len(blk))
    K.check(int(Ut.size()) == 22 and len(Cfg.UTFX[0]) == 22 and all(UF.row(i) is not None for i in ALL_UT) and bool(Cfg.UT_ON) and int(Cfg.UT_POWER) == 70
            and float(Cfg.UT_MOB) == 2.0 and float(Cfg.UT_CHEST) == 2.0 and str(Cfg.UT_LUG) == "1 2 4 8" and int(Cfg.UT_ARMOR) == 50 and int(Cfg.UT_LEAN) == 3,
            "X0: the fresh file loads 22 ut + 22 utfx rows and the scalars (on, 70 %, 2 / 2 %, 1 2 4 8, armor 50 %, lean x3)")
    bads = {}
    for i in ALL_UT:
        sb = JClass("java.lang.StringBuilder")()
        r_ = UF.parseRow(DEFP.getProperty("utfx." + i), sb)
        if r_ is None or sb.length() > 0:
            bads[i] = str(sb)
    K.check(not bads, "X0: every default utfx row parses with no unknown word: %s" % bads)
    sb = JClass("java.lang.StringBuilder")()
    pr = UF.parseRow("mp bogus cc,dmg-30 dmg+5 pierce+1 swing=fast hp+6.25 cc+1.5 nope+1 kb=100 swing+1", sb)
    K.check(list(pr[0]) == [SI("mp"), SI("cc")] and int(pr[1][SI("dmg")]) == -25 and float(pr[2][int(UF.T_PIERCE)]) == 1.0 and int(pr[3]) == 2
            and float(pr[2][int(UF.T_HP)]) == 6.25 and float(pr[2][int(UF.T_KB)]) == 100.0 and str(sb) == "bogus cc+1.5 nope+1 swing+1"
            and UF.parseRow("a,b,c", None) is None,
            "X0: parseRow - body keys (unknown skipped), fixed sums (dmg-30 dmg+5 = -25), tricks with decimals, swing=fast, '=' numbers; bad words "
            "listed (%s); three cells = not a row" % sb)
    K.check(UF.checkRow("utfx[Weapon_Sword_Iron]", "str cd|dmg+7 swing=slow") is None and "Unknown words: zzz" in str(UF.checkRow("utfx[Weapon_Sword_Iron]", "str zzz|dmg+7"))
            and "not gear" in str(UF.checkRow("utfx[Ingredient_Stick]", "str|dmg+1")) and "Write" in str(UF.checkRow("utfx[Weapon_Sword_Iron]", "a|b|c"))
            and [float(x) for x in UF.lug("1 2 4 8")] == [1.0, 2.0, 4.0, 8.0] and UF.lug("1 2 4") is None and UF.lug("1 2 4 101") is None
            and UF.checkLug("utdrop.luggage", "1 2 4 8") is None and "four percents" in str(UF.checkLug("utdrop.luggage", "x")),
            "X0: the Server Setup checks (utfx rows, the luggage percents)")
    apply(props(utdrop__luggage="9 9", utline__power="500", utfx__Weapon_Sword_UT_Paperweight="str cd,dmg+7 wobble+3"))
    K.check(str(Cfg.UT_LUG) == "1 2 4 8" and int(Cfg.UT_POWER) == 100 and list(UF.row("Weapon_Sword_UT_Paperweight")[0]) == [SI("str"), SI("cd")],
            "X0: a bad luggage text -> the default, power clamped to 100, a row with an unknown word keeps the rest")
    apply()

    # ============================================================================ X1 rows usable, the Bo type, the developer bows, Mythic ids
    t_ = Cfg.UTAB
    ids_ = [str(x) for x in t_[0]]
    usable = [ids_[i] for i in range(len(ids_)) if bool(Ut.ok(t_, JInt(i)))]
    K.check(sorted(usable) == sorted(GEAR_COPIES + DEV_UT) and int(Ut.count()) == 19 and all(ITEM.getAssetMap().getAsset(i) is None for i in ARMORY_IDS),
            "X1: a SkyyGear-only server: 19 of 22 rows usable - the 3 SkyyArmory ids are missing items and never handed out: %s"
            % sorted(set(ids_) - set(usable)))
    tk = [str(x) for x in Pool.T_KEY]
    K.check("Weapon_Bo" in tk and str(Pool.T_NAME[tk.index("Weapon_Bo")]) == "Bo Staff" and int(Pool.typeOfId("Weapon_Bo_UT_Turnstile")) == tk.index("Weapon_Bo")
            and int(Pool.typeOfId("Weapon_Staff_UT_Loophole")) == tk.index("Weapon_Staff") and int(Pool.typeOfId("Armor_UT_Intern_Legs")) == tk.index("Armor_Legs")
            and int(Pool.levelCount(JInt(tk.index("Weapon_Bo")), JInt(0), JInt(1), JInt(100))) == 0 and len(tk) == 19,
            "X1: the Bo Staff bag type (19 types; the Turnstile is a Bo; no random-bag item is a Bo)")
    K.check(all(int(Pool.idIdx(b)) < 0 for b in DEV_UT + DEV_MY) and all(int(Pool.typeOfId(b)) == tk.index("Weapon_Shortbow") for b in DEV_UT),
            "X1: the 6 developer bows are out of the random bag pool (still bows for the orange bags)")
    nv = Roll.newDoc("Weapon_Shortbow_Vampire", JInt(2), True, "drop", JInt(10))
    lg = Data.legacy("Weapon_Shortbow_Pull")
    nr = Roll.newDoc("Weapon_Shortbow_Ricochet", JInt(2), True, "drop", JInt(10))
    apply(props(gear__mythicItems="Weapon_Sword_Iron"))
    pt = Pool.table()
    sw_ok = bool(pt[2][int(Pool.idIdx("Weapon_Sword_Iron"))])
    nv2 = Roll.newDoc("Weapon_Shortbow_Vampire", JInt(2), True, "drop", JInt(10))
    apply()
    pt0 = Pool.table()
    K.check(int(Data.rarity(nv)) == R_MY and int(Data.rarity(lg)) == R_MY and int(Data.rarity(nr)) == R_UT and not sw_ok and bool(pt0[2][int(Pool.idIdx("Weapon_Sword_Iron"))])
            and int(Data.rarity(nv2)) == 2,
            "X1: gear.mythicItems - a new Vampire bow is Mythic, a plain Pull bow is stamped Mythic, a Ricochet is Untiered; an id added to the list "
            "leaves the bag pool; an id taken off rolls normally again")

    # ============================================================================ X2 never craftable
    outs = set(str(x) for x in Ut.recipeOuts())
    K.check(len(outs) > 20 and not (set(ALL_UT) & outs) and not any(bool(Ut.crafted(i)) for i in ALL_UT)
            and not any(bool(Roll.craftable(i)) for i in GEAR_COPIES + DEV_UT) and bool(Roll.craftable("Weapon_Sword_Iron")),
            "X2: no recipe in the live CraftingRecipe store (%d outputs) makes an Untiered id; GearRoll.craftable says no (control: the Iron sword yes)" % len(outs))
    nrc = [i for i in GEAR_COPIES if bool(ITEM.getAssetMap().getAsset(i).hasRecipesToGenerate())]
    K.check(not nrc and bool(ITEM.getAssetMap().getAsset("Weapon_Sword_Iron").hasRecipesToGenerate())
            and bool(ITEM.getAssetMap().getAsset("Armor_Leather_Medium_Chest").hasRecipesToGenerate()),
            "X2: the 16 copies in the REAL Item store generate no recipe - not even the Leather / Cloth copies whose base's Parent has one "
            "(control: the Iron sword and Leather_Medium_Chest do): %s" % nrc)
    qbad = [i for i in GEAR_COPIES if not bool(ITEM.getAssetMap().getAsset(i).isVariant())
            or str(JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality").getAssetMap().getAsset(
                JInt(ITEM.getAssetMap().getAsset(i).getQualityIndex())).getId()) != "Skyy_Gear_Untiered"]
    arm_ok = all(str(ITEM.getAssetMap().getAsset("Armor_UT_%s_%s" % (n, s)).getArmor().getArmorSlot()) == s for n in ("FilingCabinet", "Courier", "Intern") for s in SLOTS)
    K.check(not qbad and arm_ok, "X2: every copy is Variant (hidden from creative) with the orange Skyy_Gear_Untiered quality; armor slots kept: %s" % qbad)
    PCF = JClass("com.hypixel.hytale.server.core.modules.projectile.config.ProjectileConfig")
    pc = [(PCF.getAssetMap().getAsset("SkyyGear_UT_ShortNotice_Arrow_%d" % n), PCF.getAssetMap().getAsset("Projectile_Config_Arrow_Shortbow_Strength_%d" % n)) for n in range(4)]
    K.check(all(a is not None and b is not None and abs(float(a.getLaunchForce()) - 2 * float(b.getLaunchForce())) < 1e-9 and float(a.getGravity()) == 0.0
                and float(b.getGravity()) > 0.0 for a, b in pc),
            "X2: the 4 arrow configs are in the REAL ProjectileConfig store: x2 launch force, gravity 0 (vanilla's > 0)")
    snv = ITEM.getAssetMap().getAsset("Weapon_Shortbow_UT_ShortNotice").getInteractionVars()
    K.check(all(snv.containsKey("Primary_Shoot_Strength_%d" % n) for n in range(4)) and snv.containsKey("Primary_Shoot_Damage_Strength_4"),
            "X2: Short Notice's item vars name the 4 arrow launches (+ keep the Iron bow's damage vars)")

    # ============================================================================ X3 the band + the base twin
    K.check([int(x) for x in Lvl.band("Weapon_Sword_UT_Paperweight")] == [15, 29, 1] and [int(x) for x in Lvl.band("Armor_UT_Intern_Head")] == [15, 29, 1]
            and [int(x) for x in Lvl.band("Weapon_Shortbow_Ricochet")] == [15, 29, 1] and int(Lvl.band("Weapon_Sword_Iron")[0]) == 15,
            "X3: GearLevel.band of an Untiered id = its row's range 15-29 (the level-up cap reads it); the Iron sword keeps its own band")
    twin = [(c, str(Base.kunaiTwin(c))) for c in ("Weapon_Sword_UT_Paperweight", "Weapon_Bo_UT_Turnstile", "Weapon_Staff_UT_Loophole")]
    m_c = float(Base.mult("Weapon_Sword_UT_Paperweight", doc(ut("Weapon_Sword_UT_Paperweight", 22)), False))
    m_b = float(Base.mult("Weapon_Sword_Iron", doc(Data.put(IS("Weapon_Sword_Iron", JInt(1)), Roll.newDoc("Weapon_Sword_Iron", JInt(0), True, "t", JInt(22)), U1)), False))
    K.check(twin[0][1] == "Weapon_Sword_Iron" and twin[1][1] == "Weapon_Sword_Iron" and twin[2][1] == "Weapon_Staff_Iron" and abs(m_c - m_b) < 1e-9 and m_c > 0.0,
            "X3: a copy scales exactly like its base (twin %s; Lv 22 multiplier copy %.4f = Iron sword %.4f)" % (twin, m_c, m_b))

    # ============================================================================ X4 documents + the fixed speed tier (+ the lazy heal)
    d40 = doc(ut("Weapon_Daggers_UT_PocketKnife", 40))
    d5 = doc(ut("Armor_UT_Courier_Chest", 5))
    pw = doc(ut("Weapon_Sword_UT_Paperweight", 22))
    old = pw.clone()
    old.put("spd", BI32(2))
    n9 = int(UF.N[9])
    healed = Speed.ensure("Weapon_Sword_UT_Paperweight", old)
    st_old = Data.put(IS("Weapon_Sword_UT_Paperweight", JInt(1)), old, U1)
    sword_rolls = set()
    for _ in range(40):
        sword_rolls.add(int(Speed.tierOf(doc(Data.put(IS("Weapon_Sword_Iron", JInt(1)), Roll.newDoc("Weapon_Sword_Iron", JInt(0), True, "t", JInt(20)), U1)))))
    K.check(int(Data.rarity(d40)) == R_UT and int(Lvl.level("Weapon_Daggers_UT_PocketKnife", d40)) == 29 and int(Lvl.level("Armor_UT_Courier_Chest", d5)) == 15
            and int(Speed.tierOf(pw)) == 0 and int(Speed.tierOf(healed)) == 0 and int(Speed.tierOf(doc(st_old))) == 0 and int(UF.N[9]) >= n9 + 2
            and int(UF.swingOf("Weapon_Sword_UT_Paperweight")) == 0 and int(UF.swingOf("Weapon_Sword_Iron")) == -1 and len(sword_rolls) > 1,
            "X4: new Untiered documents (levels kept in 15-29); the Paperweight is always Slow - a copy holding Fast is healed on its next write "
            "(lazy heal, counter +%d); a plain Iron sword still rolls its tier (%s)" % (int(UF.N[9]) - n9, sorted(sword_rolls)))

    # ============================================================================ X5 the totals
    def lines_at(iid, lv):
        return [int(x) for x in UF.lines(iid, doc(ut(iid, lv)))]
    pwl = dict((lv, lines_at("Weapon_Sword_UT_Paperweight", lv)) for lv in (15, 22, 29))
    K.check([(pwl[lv][SI("str")], pwl[lv][SI("cd")], pwl[lv][SI("dmg")]) for lv in (15, 22, 29)] == [(9, 11, 7), (12, 14, 7), (14, 17, 7)],
            "X5: the Paperweight's lines = the spec's body-line table (Strength 9 / 12 / 14, Crit Damage 11 / 14 / 17 at Lv 15 / 22 / 29) + Damage +7: %s"
            % [(pwl[lv][SI("str")], pwl[lv][SI("cd")]) for lv in (15, 22, 29)])
    lp = lines_at("Weapon_Daggers_UT_PocketKnife", 22)
    lr = lines_at("Weapon_Shortbow_Ricochet", 15)
    K.check((lp[SI("cc")], lp[SI("cd")]) == (7, 14) and (lr[SI("str")], lr[SI("cc")], lr[SI("dmg")]) == (9, 6, -20),
            "X5: the Pocket Knife (Crit Chance 7 %, Crit Damage 14 % at Lv 22); the Ricochet bow (Strength 9, Crit Chance 6 %, Damage -20 at Lv 15)")
    pws = ut("Weapon_Sword_UT_Paperweight", 22)
    t1 = tot(pws)
    K.check(t1[SI("str")] == 12 and t1[SI("cd")] == 14 and t1[SI("dmg")] == 7, "X5: GearStats.totals carries an active Untiered weapon's lines: %s" % t1[:5])
    skills(combat=10)
    t1u = tot(pws)
    skills()
    K.check(t1u[SI("str")] == 0 and t1u[SI("dmg")] == 0, "X5: under the item's level (Combat 10 < Lv 22) the lines give nothing (inactive)")
    fc = wear(*[ut("Armor_UT_FilingCabinet_" + s, 15) for s in SLOTS])
    cu = wear(*[ut("Armor_UT_Courier_" + s, 15) for s in SLOTS])
    tf, tc = tot(None, fc), tot(None, cu)
    K.check(tf[SI("def")] == 36 and tf[SI("dmg")] == -10 and tc[SI("spd")] == 15 and tc[SI("cc")] == 5 and tc[SI("cd")] == 44,
            "X5: armor - the Filing Cabinet set: Defense 4 x 9 = 36 and Damage -10 (armor Damage COUNTS: no slot filter); the Courier's: Speed 15, "
            "Crit Chance 5 %%, Crit Damage 4 x 11: %s / %s" % ((tf[SI("def")], tf[SI("dmg")]), (tc[SI("spd")], tc[SI("cc")], tc[SI("cd")])))
    # MUTANT: through the modifier path (the slot filter) armor Damage would be dropped
    md = Data.base("combat", JInt(0), True, "t")
    ma = JClass("org.bson.BsonArray")()
    ma.add(Data.mod("dmg", JInt(-3)))
    md.put("mods", ma)
    tm = JArray(JInt)(int(Defs.NS))
    Stats.addMods(tm, md, True)
    K.check(int(tm[SI("dmg")]) == 0, "X5 mutant: the slot-filtered modifier path drops an armor Damage line (0) - only the Untiered path keeps it")
    hw = 1.4 * 1.07
    t22 = tot(pws)
    a = float(Hit.hitAmount(JDouble(100.0), JArray(JInt)(t22), False, False, JDouble(0.999), JDouble(0.999)))
    fam = int(Speed.famOf("Weapon_Sword_UT_Paperweight"))
    K.check(fam >= 0 and abs(float(Speed.weight(JInt(fam), JInt(0))) - 1.4) < 1e-9 and abs(a - 100.0 * 1.07 * (1.0 + 12 * float(Cfg.STR_PER) / 100.0)) < 1e-6
            and abs(hw - 1.498) < 1e-9,
            "X5: a Paperweight hit = x1.07 (Damage +7) x Strength, and its Slow tier hits x1.4 (one hit x1.498, DPS x1.07): %.3f" % a)

    # ============================================================================ X6 the hit tricks + damage taken
    tkP = [float(x) for x in UF.tricks("Weapon_Daggers_UT_PocketKnife", d40)]
    K.check([int(UF.cone(0.0, 1.0, 0.0, -3.0)), int(UF.cone(0.0, 1.0, 0.0, 3.0)), int(UF.cone(0.0, 1.0, 3.0, 0.0)), int(UF.cone(0.0, 0.0, 1.0, 0.0)),
             int(UF.cone(0.0, 1.0, 1.0, -0.55)), int(UF.cone(0.0, 1.0, 1.0, -0.6)), int(UF.cone(0.0, 1.0, 1.0, 0.55)), int(UF.cone(0.0, 1.0, 1.0, 0.6))]
            == [1, -1, 0, -2, 0, 1, 0, -1],
            "X6: the cone (facing +z): behind 1, in front -1, side 0, no facing -2; the 120 degree cones' edges (cos +-0.5 at dz = +-0.577 dx)")
    hmp = lambda tk_, hf, cn, dist, shot: round(float(UF.hitMult(JArray(JDouble)(tk_), JDouble(hf), JInt(cn), JDouble(dist), shot)), 6)
    tkO = [float(x) for x in UF.tricks("Weapon_Battleaxe_UT_Overtime", doc(ut("Weapon_Battleaxe_UT_Overtime")))]
    tkS = [float(x) for x in UF.tricks("Weapon_Shortbow_UT_ShortNotice", doc(ut("Weapon_Shortbow_UT_ShortNotice")))]
    K.check([hmp(tkP, -1, 1, 2, False), hmp(tkP, -1, 0, 2, False), hmp(tkP, -1, -1, 2, False), hmp(tkP, -1, -2, 2, False)] == [1.5, 1.0, 0.7, 1.0]
            and [hmp(tkO, 0.4, -2, 2, False), hmp(tkO, 0.5, -2, 2, False), hmp(tkO, 0.8, -2, 2, False), hmp(tkO, -1, -2, 2, False)] == [1.3, 1.0, 1.0, 1.0]
            and [hmp(tkS, -1, -2, 11.9, True), hmp(tkS, -1, -2, 12.5, True), hmp(tkS, -1, -2, 30, False)] == [1.0, 0.0, 1.0],
            "X6: hit factors - Pocket Knife back x1.5 / side x1 / front x0.7 / unknown x1; Overtime x1.3 only under half Health; Short Notice: a shot "
            "past 12 blocks does nothing (melee never)")
    # the REAL GearUtFx.onHit on stand-ins (FakeStore / FakeBuffer): positions, the victim's head facing, the attacker's Health, knockback
    for cn in ("com.hypixel.hytale.server.core.modules.entity.EntityModule", "com.hypixel.hytale.server.core.universe.Universe",
               "com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule"):
        JClass(FAKE_PKG + ".FakeUtil").single(cn)
    FS, FBuf = JClass(FAKE_PKG + ".FakeStore"), JClass(FAKE_PKG + ".FakeBuffer")
    fst = us.allocateInstance(FS.class_)
    fst.comps = HM()
    buf = us.allocateInstance(FBuf.class_)
    buf.st = fst
    REFc = JClass("com.hypixel.hytale.component.Ref")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    HRC = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    KBC = JClass("com.hypixel.hytale.server.core.entity.knockback.KnockbackComponent")
    ESM = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    DST = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    DMG = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DCS = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
    R3F = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    V3 = JClass("org.joml.Vector3d")
    IHM = JClass("java.util.IdentityHashMap")

    def ref(i):
        r_ = us.allocateInstance(REFc.class_)
        jf(REFc, "index").setInt(r_, JInt(i))
        jf(REFc, "store").set(r_, fst)
        fst.comps.put(r_, IHM())
        return r_

    def put(r_, t_, c_):
        fst.comps.get(r_).put(t_, c_)
    att, vic = ref(11), ref(12)
    hr = HRC(R3F(JFloat(0.0), JFloat(0.7), JFloat(0.0)))
    fw = hr.getDirection()
    fx_, fz_ = float(fw.x()), float(fw.z())
    ln = (fx_ * fx_ + fz_ * fz_) ** 0.5
    put(vic, HRC.getComponentType(), hr)
    put(vic, TC.getComponentType(), TC(V3(JDouble(0.0), JDouble(64.0), JDouble(0.0)), R3F()))
    HPI = int(DST.getHealth())
    SMOc = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    MTGc = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    CALc = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")

    def esm100():
        m_ = ESM()
        m_.update()
        m_.putModifier(JInt(HPI), "gear016test", SMOc(MTGc.MAX, CALc.ADDITIVE, JFloat(100.0)))
        m_.setStatValue(JInt(HPI), JFloat(100.0))
        return m_
    m_att = esm100()
    put(att, ESM.getComponentType(), m_att)
    kc = KBC()
    put(vic, KBC.getComponentType(), kc)
    ci = int(DCS.getAssetMap().getIndex("Physical"))

    def onhit(stack_, at_xz, amount=100.0, shot=False, hp=None, arm=None):
        put(att, TC.getComponentType(), TC(V3(JDouble(at_xz[0]), JDouble(64.0), JDouble(at_xz[1])), R3F()))
        if hp is not None:
            m_att.setStatValue(JInt(HPI), JFloat(float(m_att.get(JInt(HPI)).getMax()) * hp))
        d_ = DMG(None, JInt(ci), JFloat(amount))
        UF.onHit(d_, buf, att, vic, U1, stack_, arm, shot)
        return round(float(d_.getAmount()), 4)
    pk = ut("Weapon_Daggers_UT_PocketKnife", 22)
    behind = (-3.0 * fx_ / ln, -3.0 * fz_ / ln)
    front = (3.0 * fx_ / ln, 3.0 * fz_ / ln)
    side = (3.0 * fz_ / ln, -3.0 * fx_ / ln)
    oh = [onhit(pk, behind), onhit(pk, side), onhit(pk, front)]
    ot = ut("Weapon_Battleaxe_UT_Overtime", 22)
    oo = [onhit(ot, side, hp=0.3), onhit(ot, side, hp=0.9)]
    K.notes.append("X6: attacker Health %s / max %s, hpFrac %s" % (m_att.get(JInt(HPI)).get(), m_att.get(JInt(HPI)).getMax(), UF.hpFrac(m_att)))
    sn = ut("Weapon_Shortbow_UT_ShortNotice", 22)
    os_ = [onhit(sn, (11.0, 0.0), shot=True), onhit(sn, (14.0, 0.0), shot=True), onhit(sn, (14.0, 0.0), shot=False)]
    # FIXER 2: a range-cut shot is CANCELLED, so GearTrueSys (returns on isCancelled) adds no True Damage 10 and GearLeechSys pays nothing;
    # a shot inside the range keeps it (the GearTrueSys rule replayed on the REAL Damage after the REAL onHit)

    def true_after(at_xz, td=10):
        put(att, TC.getComponentType(), TC(V3(JDouble(at_xz[0]), JDouble(64.0), JDouble(at_xz[1])), R3F()))
        d_ = DMG(None, JInt(ci), JFloat(100.0))
        UF.onHit(d_, buf, att, vic, U1, sn, None, True)
        if not d_.isCancelled():
            d_.setAmount(JFloat(float(d_.getAmount()) + td))
        return (bool(d_.isCancelled()), round(float(d_.getAmount()), 4))
    trc = [true_after((14.0, 0.0)), true_after((11.0, 0.0))]
    K.check(trc == [(True, 0.0), (False, 110.0)]
            and bool(UF.rangeCut(JArray(JDouble)(tkS), JDouble(12.5), True)) and not bool(UF.rangeCut(JArray(JDouble)(tkS), JDouble(12.5), False))
            and not bool(UF.rangeCut(JArray(JDouble)(tkS), JDouble(11.9), True)) and not bool(UF.rangeCut(JArray(JDouble)(tkS), JDouble(-1.0), True)),
            "X6 FIX 2: a Short Notice shot past 12 blocks is CANCELLED, so True Damage 10 after it ends at 0 (inside 12: 100 + 10 = 110): %s; rangeCut "
            "only for a shot past the range with a known distance" % trc)
    K.check(oh == [150.0, 100.0, 70.0] and oo == [130.0, 100.0] and os_ == [100.0, 0.0, 100.0],
            "X6: the REAL GearUtFx.onHit - Pocket Knife from behind / the side / the front of the victim's HEAD FACING (the engine's own "
            "HeadRotation.getDirection) %s; Overtime at 30 %% / 90 %% Health (a REAL EntityStatMap) %s; Short Notice shot at 11 / 14 blocks + melee %s"
            % (oh, oo, os_))
    kmod = jf(KBC, "modifiers").get(kc)
    n0 = int(kmod.size()) if kmod is not None else 0
    apply(props(utfx__Weapon_Sword_UT_Paperweight="str cd,dmg+7 swing=slow kb+100"))
    onhit(pws, side)
    kmod = jf(KBC, "modifiers").get(kc)
    kv = [float(kmod.getDouble(JInt(i))) for i in range(int(kmod.size()))] if kmod is not None else []
    onhit(pws, side, shot=True)
    kv2 = [float(kmod.getDouble(JInt(i))) for i in range(int(kmod.size()))] if kmod is not None else []
    apply()
    K.check(n0 == 0 and kv == [2.0] and kv2 == [2.0], "X6: a kb+100 line adds ONE x2 modifier to the hit's KnockbackComponent (melee only): %s" % kv)
    cou = wear(*[ut("Armor_UT_Courier_" + s, 15) for s in SLOTS])
    K.check(float(UF.taken(U1, cou)) == 20.0 and abs(float(UF.takenAmount(JFloat(50.0), JDouble(20.0))) - 60.0) < 1e-4 and float(UF.takenAmount(JFloat(50.0), JDouble(-200.0))) == 0.0
            and float(UF.taken(U1, wear(ut("Armor_UT_Courier_Head", 15)))) == 5.0,
            "X6: damage taken - the full Courier's set +20 %% (one piece +5 %%): 50 -> 60; never below 0")

    # ============================================================================ X7 the max Health modifier (REAL EntityStatMap) + Mana regen
    m = esm100()
    mx0 = float(m.get(JInt(HPI)).getMax())
    K.check(mx0 >= 100.0, "X7: the test stat map has a Health max (%s, Health index %d)" % (mx0, HPI))
    intern = wear(*[ut("Armor_UT_Intern_" + s, 15) for s in SLOTS])
    fcab = wear(*[ut("Armor_UT_FilingCabinet_" + s, 15) for s in SLOTS])
    REGS = []

    @JImplements("java.util.function.Function")
    class ManaReg:
        @JOverride
        def apply(self, a):
            REGS.append(tuple(str(x) if i_ != 3 else float(x) for i_, x in enumerate(a)))
            return JBoolean(True)
    br.put("skill:fn:manaregen", ManaReg())
    tkI = [float(x) for x in UF.sum(U1, ot, intern)]
    n5 = int(UF.N[5])
    for _ in range(5):
        UF.secondPass(U1, m, None, None, True)
    K.check(int(UF.N[5]) == n5 and UF.MREG.get(U1) is None and len(REGS) == 0,
            "X7 FIX: a player with no Untiered robes - no Mana regen post, no count, every second (the 'mana posts' counter stays %d)" % n5)
    UF.secondPass(U1, m, None, fcab, True)
    mx1 = float(m.get(JInt(HPI)).getMax())
    UF.secondPass(U1, m, None, fcab, True)
    mx1b = float(m.get(JInt(HPI)).getMax())
    # FIX (engine review 1's rule): while the engine's armor Health is NOT synced (right after a join) a change that LOWERS max waits; raising
    # never waits; removing never waits
    cur1 = float(m.get(JInt(HPI)).get())
    m.setStatValue(JInt(HPI), JFloat(mx1))
    UF.hpApply(m, JDouble(10.0), False)
    mxs1 = float(m.get(JInt(HPI)).getMax())
    hps1 = float(m.get(JInt(HPI)).get())
    UF.hpApply(m, JDouble(40.0), False)
    mxs2 = float(m.get(JInt(HPI)).getMax())
    UF.hpApply(m, JDouble(10.0), True)
    mxs3 = float(m.get(JInt(HPI)).getMax())
    UF.hpApply(m, JDouble(-20.0), False)
    mxs4 = float(m.get(JInt(HPI)).getMax())
    UF.hpApply(m, JDouble(0.0), False)
    mxs5 = float(m.get(JInt(HPI)).getMax())
    UF.hpApply(m, JDouble(-20.0), False)
    mxs6 = float(m.get(JInt(HPI)).getMax())
    UF.hpApply(m, JDouble(0.0), True)
    m.setStatValue(JInt(HPI), JFloat(cur1))
    K.check(abs(mxs1 - mx1) < 1e-3 and abs(hps1 - mx1) < 1e-3 and abs(mxs2 - mx0 * 1.4) < 0.02 and abs(mxs3 - mx0 * 1.1) < 0.02
            and abs(mxs4 - mx0 * 1.1) < 0.02 and abs(mxs5 - mx0) < 1e-3 and abs(mxs6 - mx0) < 1e-3,
            "X7 FIX: not synced - +25 %% -> +10 %% waits (max %.1f, Health kept %.1f), a raise to +40 %% goes through (%.1f); synced the drop to +10 %% "
            "lands (%.1f); a negative %% waits while not synced (%.1f, also from no modifier %.1f); removal is immediate (%.1f)"
            % (mxs1, hps1, mxs2, mxs3, mxs4, mxs6, mxs5))
    UF.secondPass(U1, m, None, fcab, True)
    UF.secondPass(U1, m, ot, intern, True)
    mx2 = float(m.get(JInt(HPI)).getMax())
    br.put("profile:busy:" + str(U1), "swap")
    UF.secondPass(U1, m, ot, intern, True)
    mxb = float(m.get(JInt(HPI)).getMax())
    br.remove("profile:busy:" + str(U1))
    UF.secondPass(U1, m, None, None, True)
    mx3 = float(m.get(JInt(HPI)).getMax())
    K.check(tkI[int(UF.T_HP)] == -30.0 and tkI[int(UF.T_MREGEN)] == 50.0 and abs(mx1 - mx0 * 1.25) < 0.02 and abs(mx1b - mx1) < 1e-4
            and abs(mx2 - mx0 * 0.7) < 0.02 and abs(mxb - mx0) < 1e-4 and abs(mx3 - mx0) < 1e-4 and m.getModifier(JInt(HPI), "skyygear_ut_hp") is None,
            "X7: the REAL EntityStatMap - Filing Cabinet set +25 %% (%.1f -> %.1f, steady on the next pass), Overtime held + 4 Intern pieces -30 %% (%.1f), "
            "profile:busy and nothing worn = the modifier removed (%.1f / %.1f)" % (mx0, mx1, mx2, mxb, mx3))
    K.check(REGS == [("add", str(U1), "SkyyGear Untiered", 50.0), ("remove", str(U1), "SkyyGear Untiered")] and UF.MREG.get(U1) is None,
            "X7: Mana regen through SkyySkills' skill:fn:manaregen: +50 %% posted once (not again while unchanged), removed when gone: %s" % REGS)
    UF.secondPass(U1, m, None, intern, True)
    UF.forget(U1)
    K.check(REGS[-1] == ("remove", str(U1), "SkyyGear Untiered") and len(REGS) == 4, "X7: leaving (GearFx.forget -> GearUtFx.forget) removes the Mana source")
    apply(props(part__utLines="false"))
    UF.secondPass(U1, m, None, fcab, True)
    K.check(abs(float(m.get(JInt(HPI)).getMax()) - mx0) < 1e-4 and UF.sum(U1, ot, fcab) is None, "X7: part.utLines off = no modifier, no tricks")
    apply()

    # ============================================================================ X8 the orange bag sources
    box0 = IS("Skyy_Unid_Bag_Normal", JInt(1))

    def swaps(L, share, n):
        o_ = 0
        for _ in range(n):
            b_ = Ut.swap(box0, JInt(L), JDouble(share), None, "t", "t", JInt(0), JInt(6))
            if b_ is not box0 and str(b_.getItemId()) == "Skyy_Unid_Bag_Untiered":
                o_ += 1
        return o_
    s20, s10, s35 = swaps(20, 2.0, 50000), swaps(10, 2.0, 5000), swaps(35, 2.0, 5000)
    K.check(800 <= s20 <= 1200 and s10 == 0 and s35 == 0 and not bool(Ut.covers(JInt(14))) and bool(Ut.covers(JInt(15))) and bool(Ut.covers(JInt(29))) and not bool(Ut.covers(JInt(30))),
            "X8: the swap - 2 %% of 50,000 bags at Lv 20 become orange (%d); none at Lv 10 / 35 (only Untiered levels 15-29)" % s20)
    picks = {}
    for _ in range(20000):
        ty_ = int(Ut.pickTypeFor(JInt(20), None))
        picks[tk[ty_]] = picks.get(tk[ty_], 0) + 1
    arm_n = sum(v for k, v in picks.items() if k.startswith("Armor_"))
    lean = JArray(JString)(["Weapon_Daggers_"])
    lp_ = {}
    for _ in range(20000):
        ty_ = int(Ut.pickTypeFor(JInt(20), lean))
        if not tk[ty_].startswith("Armor_"):
            lp_[tk[ty_]] = lp_.get(tk[ty_], 0) + 1
    wn = sum(lp_.values())
    K.check(9300 <= arm_n <= 10700 and sorted(picks) == sorted(["Armor_Head", "Armor_Chest", "Armor_Hands", "Armor_Legs", "Weapon_Sword", "Weapon_Battleaxe",
                                                               "Weapon_Daggers", "Weapon_Shortbow"])
            and abs(lp_.get("Weapon_Daggers", 0) / float(wn) - 3.0 / 9.0) < 0.03 and abs(lp_.get("Weapon_Shortbow", 0) / float(wn) - 4.0 / 9.0) < 0.03,
            "X8: the bag type - armor %d / 20,000 (~50 %%); weapons by rows (bows 4: Short Notice + 3 developer bows), own-class x3 (daggers %.3f of "
            "weapons, want 0.333); no Staff / Wand / Bo without SkyyArmory" % (arm_n, lp_.get("Weapon_Daggers", 0) / float(wn)))
    # identify 2,000 orange bags: an Untiered row of the bag's type, its level inside the bag and 15-29, its lines exact
    ibad = []
    for _ in range(2000):
        b_ = Ut.bagFor(JInt(20), None, "t", "t", JInt(0))
        bd_ = Unid.doc(b_)
        lo_, hi_, ty_ = int(Unid.lo(bd_)), int(Unid.hi(bd_)), int(Unid.type(bd_))
        o_ = Unid.open(bd_, U1)
        if o_ is None:
            ibad.append(("none", lo_, hi_))
            continue
        iid_, lv_, gd_ = str(o_[0]), int(o_[1]), o_[2]
        exp_ = [0] * int(Defs.NS)
        r_ = UF.row(iid_)
        for si_ in list(r_[0]):
            exp_[int(si_)] += int(UF.bodyVal(JInt(si_), JInt(lv_)))
        for k_ in range(int(Defs.NS)):
            exp_[k_] += int(r_[1][k_])
        if (iid_ not in GEAR_COPIES + DEV_UT or int(Pool.typeOfId(iid_)) != ty_ or not (lo_ <= lv_ <= hi_) or not (15 <= lv_ <= 29)
                or int(Data.rarity(gd_)) != R_UT or [int(x) for x in UF.lines(iid_, gd_)] != exp_):
            ibad.append((iid_, lv_, lo_, hi_))
    K.check(not ibad, "X8: 2,000 orange bags identified - always an Untiered row of the bag's type, level inside the bag and 15-29, rarity Untiered, "
            "its lines exactly body (utline.power) + fixed: %s" % ibad[:3])
    rb = Ut.bagFor(JInt(22), None, "t", "t", JInt(0))
    ro = Unid.open(Unid.doc(rb), U1)
    rd = ro[2].clone()
    rd.put("box", Unid.boxSub(JInt(Unid.type(Unid.doc(rb))), JInt(0), JInt(R_UT), JInt(Unid.lo(Unid.doc(rb))), JInt(Unid.hi(Unid.doc(rb))), JInt(0)))
    # FIX (ut02 review; UT-First-Batch-Build 3.1): an Untiered item re-rolls into ANOTHER Untiered item - a weapon into any other Untiered
    # weapon (own-class x3), an armor piece into another piece of its own set - never itself; nothing else = refused before any coin
    def utbox(iid, lo_=15, hi_=29):
        d_ = doc(ut(iid, 22)).clone()
        d_.put("box", Unid.boxSub(JInt(Pool.typeOfId(iid)), JInt(0), JInt(R_UT), JInt(lo_), JInt(hi_), JInt(1)))
        return d_
    wd = utbox("Weapon_Sword_UT_Paperweight")
    rw = [Unid.reroll(wd, U1, "Weapon_Sword_UT_Paperweight", None) for _ in range(600)]
    ad = utbox("Armor_UT_FilingCabinet_Head")
    ra = [Unid.reroll(ad, U1, "Armor_UT_FilingCabinet_Head", None) for _ in range(300)]

    def rr_ok(x, fam):
        if x is None:
            return False
        i_, b_ = str(x[0]), Unid.boxOf(x[2])
        return (i_ in fam and int(Data.rarity(x[2])) == R_UT and 15 <= int(x[1]) <= 29 and int(Unid.type(b_)) == int(Pool.typeOfId(i_))
                and int(Unid.lo(b_)) == 15 and int(Unid.hi(b_)) == 29 and int(Unid.rerolls(b_)) == 2 and int(Data.rarity(doc(x[3]))) == R_UT)
    weps = [i for i in GEAR_COPIES + DEV_UT if not i.startswith("Armor_") and i != "Weapon_Sword_UT_Paperweight"]
    fcs = ["Armor_UT_FilingCabinet_" + s for s in SLOTS[1:]]
    wset, aset = sorted(set(str(x[0]) for x in rw)), sorted(set(str(x[0]) for x in ra))
    rl = [str(Unid.reroll(wd, U1, "Weapon_Sword_UT_Paperweight", JArray(JString)(["Weapon_Daggers_"]))[0]) for _ in range(8000)]
    pk = rl.count("Weapon_Daggers_UT_PocketKnife") / 8000.0
    rcur = Unid.reroll(rd, U1, str(ro[0]), None)
    K.check(all(rr_ok(x, weps) for x in rw) and wset == sorted(weps) and all(rr_ok(x, fcs) for x in ra) and aset == sorted(fcs)
            and abs(pk - 3.0 / 8.0) < 0.03 and rcur is not None and str(rcur[0]) != str(ro[0]) and int(Data.rarity(rcur[2])) == R_UT,
            "X8 FIX: re-roll of the Paperweight -> every other Untiered weapon, never itself (%s); the Filing Cabinet Helm -> the other 3 Filing "
            "Cabinet pieces only (%s); own-class daggers lean %.3f (want 0.375 = 3 / 8); level 15-29, box type = the new item's, re-roll count + 1"
            % (wset, aset, pk))
    w_ok = [Unid.rerollWhy("Weapon_Sword_UT_Paperweight", wd), Unid.rerollWhy("Armor_UT_FilingCabinet_Head", ad)]
    apply(props(**dict(("ut__Armor_UT_FilingCabinet_" + s, "40,45,x") for s in SLOTS[1:])))
    w_one = Unid.rerollWhy("Armor_UT_FilingCabinet_Head", ad)
    r_one = Unid.reroll(ad, U1, "Armor_UT_FilingCabinet_Head", None)
    w_one_w = Unid.rerollWhy("Weapon_Sword_UT_Paperweight", wd)
    apply()
    w_far = Unid.rerollWhy("Weapon_Sword_UT_Paperweight", utbox("Weapon_Sword_UT_Paperweight", 40, 45))
    K.check(w_ok == [None, None] and w_one is not None and "No other Untiered piece of this set" in str(w_one) and r_one is None and w_one_w is None
            and w_far is not None and "No other Untiered weapon" in str(w_far),
            "X8 FIX: nothing else to roll is refused BEFORE the coins (GearIdent.reroll + the page read rerollWhy(id, d)): the set's other pieces "
            "moved to Lv 40-45 -> '%s'; a bag range with no row -> '%s'" % (w_one, w_far))
    # the REAL GearLoot.chestExtra + GearBoxFn (Unclaimed Luggage) + mobRoll
    Cfg.LOOT_CHEST_PCT = 100.0
    Cfg.UT_CHEST = 100.0
    c20, c10 = SIC(JShort(3)), SIC(JShort(3))
    Loot.chestExtra(c20, JInt(20), "t")
    Loot.chestExtra(c10, JInt(10), "t")
    apply()
    got20 = [str(c20.getItemStack(JShort(i)).getItemId()) for i in range(3) if c20.getItemStack(JShort(i)) is not None and not c20.getItemStack(JShort(i)).isEmpty()]
    got10 = [str(c10.getItemStack(JShort(i)).getItemId()) for i in range(3) if c10.getItemStack(JShort(i)) is not None and not c10.getItemStack(JShort(i)).isEmpty()]
    K.check(got20 == ["Skyy_Unid_Bag_Untiered"] and len(got10) == 1 and got10[0] != "Skyy_Unid_Bag_Untiered",
            "X8: the REAL chestExtra at utdrop.chest 100 %%: ONE bag, orange at Lv 20; a normal bag at Lv 10: %s / %s" % (got20, got10))
    bx = BoxFn()

    def lug(tier, L=20, a0=None, n=1):
        o_ = 0
        for _ in range(n):
            b_ = bx.apply(JArray(JObject)([a0, JInt(L), "lootchest", JInt(tier), U1]))
            if b_ is not None and str(b_.getItemId()) == "Skyy_Unid_Bag_Untiered":
                o_ += 1
        return o_
    lt = [lug(t, n=20000) for t in (1, 2, 3, 4)]
    K.check(150 <= lt[0] <= 260 and 320 <= lt[1] <= 480 and 680 <= lt[2] <= 920 and 1430 <= lt[3] <= 1770,
            "X8: the REAL gear:fn:box (Unclaimed Luggage) - orange per bag at tiers I-IV over 20,000 each: %s (1 / 2 / 4 / 8 %%)" % lt)
    Cfg.UT_LUG = "100 100 100 100"
    l100 = [lug(1), lug(0), lug(1, L=10), lug(1, a0="Weapon_Sword"), lug(1, a0=IS("Weapon_Sword_Iron", JInt(1)))]
    apply()
    K.check(l100 == [1, 0, 0, 0, 0], "X8: luggage at 100 %%: orange at tier I; never tier 0 / Lv 10 / a type asked / a vanilla item given: %s" % l100)
    # the REAL mobRoll (stand-ins as in the 0.2.11 harness): the extra bag at 100 % + utdrop.mob 100 % is orange at Lv 20, normal at Lv 10
    UUIDC = JClass("com.hypixel.hytale.server.core.entity.UUIDComponent")
    DTH = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    DENT = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    GM = JClass("com.hypixel.hytale.protocol.GameMode")
    prx = us.allocateInstance(PRc.class_)
    jf(PRc, "uuid").set(prx, U1)
    jf(PRc, "username").set(prx, "Tester")
    killer = ref(31)
    kpl = us.allocateInstance(PLA.class_)
    jf(PLA, "gameMode").set(kpl, GM.Adventure)
    put(killer, PLA.getComponentType(), kpl)
    put(killer, PRc.getComponentType(), prx)
    FCh = JClass(FAKE_PKG + ".FakeChunk")
    chunk = us.allocateInstance(FCh.class_)

    def mkchunk(npc_u):
        m_ = IHM()
        u_ = us.allocateInstance(UUIDC.class_)
        jf(UUIDC, "uuid").set(u_, npc_u)
        m_.put(UUIDC.getComponentType(), u_)
        h_ = us.allocateInstance(HRC.class_)
        jf(HRC, "rotation").set(h_, R3F())
        m_.put(HRC.getComponentType(), h_)
        chunk.comps = m_
        return chunk

    def death():
        o_ = us.allocateInstance(DTH.class_)
        d_ = us.allocateInstance(DMG.class_)
        jf(DMG, "source").set(d_, DENT(killer))
        jf(DTH, "deathInfo").set(o_, d_)
        return o_
    SPAWNED = []

    @JImplements("java.util.function.BiFunction")
    class Spawn:
        @JOverride
        def apply(self, box_, at_):
            SPAWNED.append(str(box_.getItemId()))
            return None
    Loot.SPAWN = Spawn()
    Cfg.LOOT_MOB_PCT = 100.0
    Cfg.UT_MOB = 100.0
    Loot.HOUR.clear()
    Loot.ROLLED.clear()
    n6 = int(UF.N[6])
    pos = V3(JDouble(5.0), JDouble(70.0), JDouble(5.0))
    m20 = int(Loot.mobRoll(mkchunk(UUID.randomUUID()), JInt(0), fst, buf, death(), pos, JInt(20), "w"))
    m10 = int(Loot.mobRoll(mkchunk(UUID.randomUUID()), JInt(0), fst, buf, death(), pos, JInt(10), "w"))
    Loot.SPAWN = None
    apply()
    K.check(m20 == 1 and m10 == 1 and len(SPAWNED) == 2 and SPAWNED[0] == "Skyy_Unid_Bag_Untiered" and SPAWNED[1] != "Skyy_Unid_Bag_Untiered"
            and int(UF.N[6]) == n6 + 1 and "orange bags: 2% of extra mob bags" in str(Loot.countsText()),
            "X8: the REAL mobRoll - ONE extra bag a death, orange at Lv 20 (utdrop.mob 100 %%), normal at Lv 10; counters in /gear loot: %s" % SPAWNED)

    # ============================================================================ X9 the market wall split
    iron = Data.put(IS("Armor_Iron_Head", JInt(1)), Roll.newDoc("Armor_Iron_Head", JInt(0), True, "craft", JInt(15)), U1)
    qd = Roll.newDoc("Armor_Bronze_Head", JInt(R_SET), True, "q", JInt(10))
    qd.put("set", BS("quest_guard"))
    quest = Data.put(IS("Armor_Bronze_Head", JInt(1)), qd, U1)
    vam = Data.put(IS("Weapon_Shortbow_Vampire", JInt(1)), nv, U1)
    obag = Ut.bagFor(JInt(20), None, "t", "t", JInt(0))
    sbag = Unid.make(JInt(tk.index("Armor_Head")), JInt(1), JInt(R_SET), JInt(10), JInt(12), "t", "t", JInt(0))
    why = lambda s_: Wall.why(s_.getItemId(), s_.getMetadata())
    w = [why(iron), why(quest), why(vam), why(pws), why(obag), why(sbag), why(IS("Weapon_Sword_UT_Paperweight", JInt(1))), why(IS("Weapon_Sword_Iron", JInt(1)))]
    apply(props(market__gatheringSets="false"))
    w_off = why(iron)
    apply(props(market__gatheringPrefixes="quest_"))
    w_q = [why(quest), why(iron)]
    apply()
    # FIX (ut02 review): a quest / boss Set piece on a METAL id whose set field was cleared (/gear set clear keeps the rarity) stays walled -
    # only the document's own set field counts, never the by-id Mining Set fallback
    cld = Roll.newDoc("Armor_Iron_Chest", JInt(R_SET), True, "q", JInt(15))
    cld.put("set", BS("quest_guard"))
    cld.remove("set")
    clr = Data.put(IS("Armor_Iron_Chest", JInt(1)), cld, U1)
    old_iron = Data.put(IS("Armor_Iron_Legs", JInt(1)), Roll.newDoc("Armor_Iron_Legs", JInt(0), True, "craft", JInt(15)), U1)
    od_ = doc(old_iron).clone()
    od_.put("r", BS("normal"))
    od_.remove("set")
    old_iron = Data.put(IS("Armor_Iron_Legs", JInt(1)), od_, U1)
    K.check(int(Data.rarity(doc(clr))) == R_SET and Set.of(doc(clr)) is None and str(Set.sidOf("Armor_Iron_Chest", doc(clr))) == "mining_iron"
            and str(why(clr)) == REASON and why(old_iron) is None,
            "X9 FIX: a Set-rarity metal piece with NO set field (a cleared quest piece; sidOf would say mining_iron) is walled: %s; an old plain "
            "metal piece (normal rarity, no set) still sells: %s" % (why(clr), why(old_iron)))
    K.check(int(Data.rarity(doc(iron))) == R_SET and str(Set.of(doc(iron))) == "mining_iron" and w[0] is None and all(str(x) == REASON for x in w[1:7]) and w[7] is None
            and str(w_off) == REASON and w_q[0] is None and str(w_q[1]) == REASON
            and bool(Fn(JInt(13)).apply(iron)) and not bool(Fn(JInt(13)).apply(quest)),
            "X9: the market wall - a crafted Mining Set piece (mining_iron) is SELLABLE; a quest Set, a Mythic bow, an Untiered item, an orange bag, a "
            "Set bag and a plain Untiered id stay walled; a plain Iron sword sells; market.gatheringSets off walls the mining piece again; the "
            "prefixes row decides (quest_ -> that set sells, mining no more); gear:fn:tradeable agrees: %s" % [None if x is None else "walled" for x in w])

    # ============================================================================ X10 the tooltip
    tp = jl(View.plain("Weapon_Sword_UT_Paperweight", doc(pws), U1))
    tc_ = jl(View.plain("Armor_UT_Courier_Chest", doc(ut("Armor_UT_Courier_Chest", 15)), U1))
    K.check("Strength: +12" in tp and "Crit Damage: +14%" in tp and "Damage: +7%" in tp and "Hits 50% harder. Swings 40% slower." in tp
            and "Attack Speed: Slow" in tp and "Damage taken +5%" in tc_ and "Speed: +4" in tc_ and "Crit Chance: +2%" in tc_ and "UNTIERED WEAPON" in tp
            and tp.index("Strength: +12") < tp.index("Hits 50% harder. Swings 40% slower.") < tp.index("UNTIERED WEAPON"),
            "X10: the tooltip - the body + fixed lines, the trick lines, the orange trade-off line, the Slow tier, UNTIERED: %s | %s" % (tp, tc_))
    apply(props(part__utLines="false"))
    tpo = jl(View.plain("Weapon_Sword_UT_Paperweight", doc(pws), U1))
    tot_off = tot(pws)
    apply()
    K.check("(Untiered lines are off on this server)" in tpo and "Strength: +12" not in tpo and tot_off[SI("str")] == 0 and tot_off[SI("dmg")] == 0,
            "X10/X11: part.utLines off - the tooltip says so and the totals carry nothing")

    # ============================================================================ X12 the bridges: gear:fn:utfx + gear:fn:grant
    fu = Fn(JInt(14))
    K.check(float(fu.apply(JArray(JObject)(["Weapon_Staff_UT_Loophole", "pierce"]))) == 1.0 and float(fu.apply(JArray(JObject)(["Weapon_Wand_UT_SecondOpinion", "heal"]))) == 50.0
            and float(fu.apply(JArray(JObject)(["Weapon_Wand_UT_SecondOpinion", "dmg"]))) == -40.0 and float(fu.apply(JArray(JObject)(["Weapon_Sword_Iron", "dmg"]))) == 0.0
            and fu.apply("x") is None and float(fu.apply(JArray(JObject)(["Weapon_Staff_UT_Loophole", "nope"]))) == 0.0,
            "X12: gear:fn:utfx (SkyyArmory's read) - Loophole pierce 1, Second Opinion heal 50 / dmg -40; a plain id 0; bad input null")
    g1 = Fn.grant(JArray(JObject)(["Weapon_Daggers_UT_PocketKnife", JInt(40), "untiered", "", "", U1, "test"]))
    g2 = Fn.grant(JArray(JObject)(["Weapon_Daggers_UT_PocketKnife", JInt(-1), "", "", "", U1, "test"]))
    g3 = Fn.grant(JArray(JObject)(["Weapon_Daggers_UT_PocketKnife", JInt(20), "rare", "", "", U1, "test"]))
    K.check(g1 is not None and int(Lvl.level("Weapon_Daggers_UT_PocketKnife", doc(g1))) == 29 and int(Data.rarity(doc(g1))) == R_UT and g2 is not None
            and int(Data.rarity(doc(g2))) == R_UT and 15 <= int(Lvl.level("Weapon_Daggers_UT_PocketKnife", doc(g2))) <= 29 and g3 is None,
            "X12: gear:fn:grant (what /gear ut give and later quests / bosses use): Untiered, level kept in 15-29; another rarity refused")
    K.check("Untiered table 19 / 22 usable" in str(Ut.statusText()), "X12: the status text: %s" % Ut.statusText())

    # Y: the three SkyyArmory copies are checked in SkyyArmory's own harness (its boot loads its pack the way the game does: the copies, their
    # validators, the pierce / heal paths through gear:fn:utfx); here they are the "missing partner" rows (X1)
    K.notes.append("Y: the 3 SkyyArmory rows are exercised by SkyyArmory/test_skyyarmory_0.1.15.py (R18); here: missing -> never handed out (X1)")
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
    diffs = {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn, ("0.2.15", "0.2.16")), members(pb, cn, ("0.2.15", "0.2.16"))
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(PKG):]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd]
    add = sorted(c[len(PKG):] for c in set(nb) - set(na))
    gone = sorted(c[len(PKG):] for c in set(na) - set(nb))
    print("C. class compare 0.2.15 -> 0.2.16: + %s - %s" % (add, gone))
    for k in sorted(diffs):
        print("   %-16s %s" % (k, ", ".join(diffs[k])[:700]))
    K.check(add == sorted(NEW_CLASSES + ["GearUtCmd"]) and not gone, "C: classes added = GearUtFx + GearUtCmd (/gear ut), none removed: + %s - %s" % (add, gone))
    unexpected = sorted(set(diffs) - EXPECT_CHANGED)
    missing = sorted(EXPECT_CHANGED - set(diffs))
    K.check(not unexpected and not missing, "C: exactly the listed classes changed (unexpected %s, listed but unchanged %s)" % (unexpected, missing))
    want = {"GearLevel": {"~m band"}, "GearBase": {"~m kunaiTwin", "~m shots"}, "GearSpeed": {"~m ensure"}, "GearRoll": {"~m newDoc"},
            "GearData": {"~m legacy"}, "GearStats": {"~m totals"}, "GearView": {"+m utLines", "~m lines"}, "GearFx": {"~m second", "~m forget"},
            "GearHitSys": {"~m handle"}, "GearArmorSys": {"~m handle"}, "GearPool": {"~m table", "~<clinit>"}, "GearBoxFn": {"~m apply"}, "GearWall": {"~m why"},
            "GearFn": {"+m utfx", "~m apply"}, "GearLoot": {"~m mobRoll", "~m chestExtra", "+m countsText0", "~m countsText"},
            "GearUt": {"+m covers", "+m rowsOf", "+m pickTypeFor", "+m bagFor", "+m swap", "+m dropsText",
                       "+m family", "+m rerollFits", "+m rerollCount", "+m rerollItem", "+m rerollLevel"},
            "GearUnid": {"~m rerollWhy", "+m rerollWhy", "+m utReroll", "+m reroll"}, "GearIdent": {"~m reroll"}, "IdentifyPage": {"~m detailReroll"},
            "GearAdmin": {"+m utCmd", "~m run"}, "GearCmd": {"~c "}}
    bad = dict((k, (sorted(v - set(diffs.get(k, []))), sorted(set(diffs.get(k, [])) - v))) for k, v in want.items() if set(diffs.get(k, [])) != v)
    K.check(not bad, "C: the classes changed exactly where the patch says (missing / extra): %s" % bad)
    # the ECS call sites (the systems need the live engine): the new calls sit in the changed methods, in order (the callees run in X6 / X7)
    def code_of(cn, mname):
        ms_ = members(pb, PKG + cn, ())
        return chr(10).join(v for k, v in ms_.items() if k.startswith("m " + mname + "("))
    hs_c = code_of("GearHitSys", "handle")
    as_c = code_of("GearArmorSys", "handle")
    fx_c, fo_c = code_of("GearFx", "second"), code_of("GearFx", "forget")
    K.check(0 <= hs_c.find("GearSpeed.perHit") < hs_c.find("GearUtFx.onHit") and as_c.find("I_DEF") < as_c.find("GearUtFx.taken") < as_c.find("GearUtFx.takenAmount")
            and 0 <= fx_c.find("GearFx.armorPass") < fx_c.find("GearUtFx.secondPass") and "GearUtFx.forget" in fo_c,
            "C: the ECS call sites - GearHitSys.handle calls GearUtFx.onHit right after the speed tier's perHit; GearArmorSys.handle applies "
            "GearUtFx.taken after Defense; GearFx.second runs GearUtFx.secondPass after the armor pass; GearFx.forget -> GearUtFx.forget")
    cfg = set(diffs.get("GearCfg", []))
    K.check({"+m migrate0216", "+m ubUpdate", "+m readUtfx", "~m apply", "+f UTFX", "+f UT_ON", "+f UB_GL", "~<clinit>"} <= cfg,
            "C: GearCfg gains the update, the reader, the fields: %s" % sorted(cfg))
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
    K.check(Cfg.ubUpdate(fresh) is None and Cfg.gmUpdate(fresh) is None and Cfg.guUpdate(fresh) is None, "D: a fresh 0.2.16 file carries the 0.2.14 / 0.2.15 / 0.2.16 markers")
    old = open(os.path.join(home, "config.properties"), "rb").read().decode("latin-1")
    BLOCK = fresh[fresh.index("# ---- The first Untiered batch + gathering sets on the market (SkyyGear 0.2.16) ----"):]
    K.check("utfx." not in old and "ut.Weapon_" not in old, "D: the live copy has no 0.2.16 key yet")
    g15 = "SkyyGear 0.2.15 mining armor" in old
    base = old
    if "SkyyGear 0.2.14 rarity update" not in base:
        base = str(Cfg.guUpdate(base)[0])
    if not g15:
        base = str(Cfg.gmUpdate(base)[0])
    K.notes.append("D: the live copy %s the 0.2.15 marker" % ("has" if g15 else "lacks"))

    def upd(text):
        r = Cfg.ubUpdate(text)
        return None if r is None else (str(r[0]), [str(x) for x in r[1]], str(r[2]))
    r = upd(base)
    exp = base + "\n" + BLOCK if base.endswith("\n") else None
    K.check(r is not None and exp is not None and r[0] == exp and r[1] == [] and r[2].startswith("part.utLines, utline.power")
            and r[2].endswith("utfx.Weapon_Shortbow_Test_Zoom") and r[2].count(",") == 53,
            "D: the live file: the block appended = exactly the fresh file's block (54 keys), nothing else changed: %s" % (r[2][:80] if r else None))
    K.check(upd(r[0]) is None, "D: the updated text carries the marker (run once)")
    rc = upd(base.replace("\n", "\r\n"))
    K.check(rc is not None and rc[0] == exp.replace("\n", "\r\n"), "D: a CRLF file keeps CRLF on every line (block included)")
    rn = upd(base.rstrip("\n"))
    K.check(rn is not None and rn[0] == exp.rstrip("\n"), "D: a file without a final newline: the block after its last line, still no final newline")
    hand = base + "utdrop.mob=5\nut.Weapon_Sword_UT_Paperweight=15,20,My line\nutfx.Weapon_Sword_UT_Paperweight=str,dmg+1\n"
    rh = upd(hand)
    K.check(rh is not None and rh[0].count("utdrop.mob=") == 1 and "utdrop.mob=5" in rh[0] and rh[0].count("ut.Weapon_Sword_UT_Paperweight=") == 1
            and rh[0].count("utfx.Weapon_Sword_UT_Paperweight=") == 1 and len(rh[1]) == 3 and "utfx.Weapon_Shortbow_Combat=" in rh[0],
            "D: keys already in the file are KEPT + noted (3), the rest added: %s" % (rh[1] if rh else None))
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    files0 = sorted(os.path.relpath(os.path.join(a, f), home) for a, d, fs in os.walk(home) for f in fs)
    log0 = open(os.path.join(home, "config-changes.log"), "rb").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else b""
    snaps = []
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214",
                  "migrate0215", "migrate0216"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(os.path.join(home, "config.properties"), "rb").read())
        K.check(len(Cfg.UTAB[0]) == 22 and len(Cfg.UTFX[0]) == 22 and bool(Cfg.UT_ON) and str(Cfg.UT_LUG) == "1 2 4 8",
                "D start %d: the loaded Untiered rows (22 + 22) and the scalars" % step)
    K.check(snaps[0] == exp.encode("latin-1"), "D start 1: the live copy = the expected text byte for byte")
    K.check(snaps[1] == snaps[0], "D start 2: nothing changes")
    files1 = sorted(os.path.relpath(os.path.join(a, f), home) for a, d, fs in os.walk(home) for f in fs)
    newf = sorted(set(files1) - set(files0))
    hb = [open(os.path.join(home, f), "rb").read() for f in newf if f.startswith("config-history")]
    K.check(any(b == base.encode("latin-1") for b in hb) and all(f.startswith("config-history") for f in newf)
            and all(f.startswith("config-history") for f in set(files0) - set(files1)),
            "D: the History copy before 0.2.16 holds the bytes it saw; only config-history files were added (the kit prunes past KEEP): %s" % newf)
    log1 = open(os.path.join(home, "config-changes.log"), "rb").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else b""
    addl = [x for x in log1[len(log0):].decode("utf-8", "replace").split("\n") if x.strip()]
    K.check(log1.startswith(log0) and not [x for x in addl if "0.2.16" in x],
            "D: no config-changes.log row from 0.2.16 (a pure addition - no value changed): %s" % addl)
    K.save()


# ====================================================================================================== parent
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--old", OLD_JAR, "--armory", ARM_JAR], env=env)


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
        assert '"Version": "0.2.15"' in z_.read("manifest.json").decode("utf-8"), "the old jar is not 0.2.15"
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
