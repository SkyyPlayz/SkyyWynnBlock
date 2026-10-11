"""Harness for SkyyGear 0.2.17 (TOOL RARITY ON CRAFT + the mace load warnings; tools/gear_0_2_17_patch.py header). Build first:
    python tools/gear_0_2_17_patch.py && python SkyyGear/build_skyygear_0.2.17.py

    python SkyyGear/test_skyygear_0.2.17.py [--jar <SkyyGear-0.2.17.jar>] [--old <SkyyGear-0.2.16.jar>] [--dir <scratch>] [--keep]

The 0.2.11 harness's helpers (stand-ins F, verify A, the bare-server boot of V, the engine-access audit AA) are loaded from
SkyyGear/test_skyygear_0.2.11.py and run on the 0.2.17 jar (the 0.2.12 - 0.2.16 harnesses do the same).
  S  non-class entries 0.2.16 -> 0.2.17: only the 18 named mace steps added, the 9 mace tap + 9 Selector files + the manifest changed; RE-INLINED
     every speed file equals 0.2.16's JSON; every string id in the speed files resolves (vanilla or a speed file); no inline Next / Failed left on
     the chain a named Charging child starts
  A  every class of the jar loads + verifies (-Xverify:all)
  V  the vanilla pack store by store + THE JAR as its own pack (real Item / BlockType stores)
  X  EVERY NEW CODE PATH EXECUTED on the real stores (-Xverify:all): X0 rows + fresh file + boost parse / check; X1 the pools (each family its
     own keys, never a combat stat, off switches); X2 THE ROLL DISTRIBUTION per rarity over 3000 crafted pickaxes (odds column, Smithing step-up,
     craft.maxRarity, never Mythic / Set / Untiered, modifier count per rarity, values inside the (boosted) bounds, "tr", no speed tier) + every
     family + the spare-slot boost + a weapon untouched + switches off; X3 Smithing XP per crafted tool (craftXp + payCraft through a stand-in
     skill:fn:addxp, tool.xpCraft); X4 GearTool: eff / stats / held (skill:bonus "gear" dd + xp), caps, under-level, a plain old tool = 0.2.16,
     the block hit on REAL BlockTypes; X5 tooltip + name colour; X6 REFORGE / LEVEL UP on tools end to end (coins first, the item count never
     changes, an old tool without any document, refusals before coins, stale fingerprint); X7 identify a tool document; X8 status text
  C  CLASS COMPARE 0.2.16 -> 0.2.17 (javassist members): no class added / removed, only the listed classes / members differ
  D  THE ONE-TIME UPDATE migrate0217: synthetic files (fresh, LF / CRLF, no final newline, keys already there) + START TWICE on a scratch COPY
     of the live Skyy_SkyyGear folder (block appended, History copy, nothing else; the 2nd start changes nothing)
  AA THE ENGINE-ACCESS AUDIT
Scratch: tools/dev/scratch/gear0217/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2.17"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear0217")))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-0.2.16.jar")))      # read only
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
PKG = "com.skyy.gear."
SPD = "Server/Item/Interactions/SkyyGear/Speed/"
TOOL_KEYS = ["mpow", "dpow", "cpow", "mfort", "ffort", "afort", "mwis", "fwis", "awis"]
FAM_KEYS = {1: {"mpow", "mfort", "mwis"}, 2: {"dpow", "mfort", "mwis"}, 3: {"cpow", "ffort", "fwis"}, 4: {"afort", "awis"}, 5: {"afort", "awis"}}
FAM_ID = {1: "Tool_Pickaxe_Iron", 2: "Tool_Shovel_Iron", 3: "Tool_Hatchet_Iron", 4: "Tool_Hoe_Iron", 5: "Tool_Sickle_Iron"}
NAMED = sorted("SkyyGear_Spd%s_Mace_Weapon_Mace_Primary_Swing_%s%s_Next" % (t, w, x) for t in ("S", "F", "X") for w in ("Left", "Right", "Up_Left")
               for x in ("", "_Selector"))
EXPECT_CHANGED = {"GearCfg", "GearDefs", "GearData", "GearRoll", "GearTool", "GearView", "GearForge", "ReforgePage", "GearIdent", "SkyyGearPlugin",
                  "CfgRows", "CfgFile"}       # CfgRows / CfgFile: the kit's row tables (the 6 new rows, the xp.craft help line) in <clinit>

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


# ====================================================================================================== S: non-class entries + the mace chain
def run_assets():
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(eb) - set(ea))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    want_add = sorted(SPD + n + ".json" for n in NAMED)
    want_chg = sorted([SPD + n[:-5] + ".json" for n in NAMED] + ["manifest.json"])
    check(added == want_add and not (set(ea) - set(eb)) and changed == want_chg and b'"0.2.17"' in eb["manifest.json"],
          "S: 0.2.16 -> 0.2.17 adds exactly the 18 named mace steps; only their 18 parents (9 taps + 9 Selectors) + the manifest change: "
          "+ %s ~ %s" % ([a for a in added if a not in want_add][:3], [c for c in changed if c not in want_chg][:3]))
    rp, gi = zn.read("com/skyy/gear/ReforgePage.class"), zn.read("com/skyy/gear/GearIdent.class")
    check(b"Pick a weapon, armor piece or tool. Reforge" in rp and b"Pick a weapon or armor piece. Reforge" not in rp
          and b"only weapons and armor get identified." in gi and b"gathering tools get identified" not in gi,
          "S (fix round, critics 2 + 3): the Reforge subtitle names tools; the Identify refusal says weapons and armor (its list shows gear only)")
    I_new = dict((os.path.basename(n)[:-5], json.loads(v)) for n, v in eb.items() if n.startswith(SPD) and n.endswith(".json"))
    I_old = dict((os.path.basename(n)[:-5], json.loads(v)) for n, v in ea.items() if n.startswith(SPD) and n.endswith(".json"))

    def inline(x):
        if isinstance(x, dict):
            return dict((k, (inline(I_new[v]) if k in ("Next", "Failed") and isinstance(v, str) and v in NAMED else inline(v))) for k, v in x.items())
        if isinstance(x, list):
            return [inline(v) for v in x]
        return x
    bad = [k for k in I_old if inline(I_new.get(k)) != I_old[k]]
    check(not bad and set(I_new) == set(I_old) | set(NAMED),
          "S: re-inlined (each named <step>_Next put back as the inline step), EVERY speed interaction file equals 0.2.16's JSON - maces swing "
          "exactly as before: %s" % bad[:3])
    az = zipfile.ZipFile(os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Assets.zip"))
    vanilla = set(os.path.basename(n)[:-5] for n in az.namelist() if n.startswith("Server/Item/Interactions/") and n.endswith(".json"))
    refs = []

    def walk(x):
        if isinstance(x, dict):
            for k in ("Next", "Failed"):
                v = x.get(k)
                if isinstance(v, str):
                    refs.append(v)
                elif isinstance(v, dict) and x.get("Type") == "Charging":
                    refs.extend(c for c in v.values() if isinstance(c, str))
            for lst in ((x.get("DefaultValue") or {}).get("Interactions") if isinstance(x.get("DefaultValue"), dict) else None, x.get("Interactions")):
                if isinstance(lst, list):
                    refs.extend(r for r in lst if isinstance(r, str))
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(list(I_new.values()))
    miss = sorted(set(r for r in refs if r not in I_new and r not in vanilla))
    check(not miss and len(refs) > 500, "S: %d string ids in the speed files - every one is a vanilla interaction or a speed file: %s" % (len(refs), miss[:5]))
    # the chain each named Charging child starts: no inline Next / Failed step left anywhere on it
    work = [x for k, v in I_new.items() if k.rsplit("_", 1)[-1].startswith("Hold") for x in ((v.get("DefaultValue") or {}).get("Interactions") or [])]
    seen, inl = set(), []
    while work:
        x = work.pop()
        if x in seen or x not in I_new:
            continue
        seen.add(x)
        d = I_new[x]
        for k in ("Next", "Failed"):
            v = d.get(k)
            if isinstance(v, dict) and d.get("Type") != "Charging":
                inl.append(x + "." + k)
            elif isinstance(v, str):
                work.append(v)
        work += [y for y in ((d.get("DefaultValue") or {}).get("Interactions") or []) if isinstance(y, str)] if isinstance(d.get("DefaultValue"), dict) else []
    check(not inl and len(seen) >= 36, "S: the %d steps the named Charging children reach carry no inline Next / Failed (the 0.2.16 jar's 9 WARN lines "
          "'Missing interaction *..._Swing_*_Next' and the 9 *..._Selector_Next ones a first try moved to): %s" % (len(seen), inl[:3]))
    j = json.loads(eb[SPD + "SkyyGear_SpdF_Mace_Weapon_Mace_Primary_Swing_Left.json"])
    check(j.get("Next") == "SkyyGear_SpdF_Mace_Weapon_Mace_Primary_Swing_Left_Next"
          and I_new["SkyyGear_SpdF_Mace_Weapon_Mace_Primary_Swing_Left_Next"]["Var"] == "SkyyGear_Spd_Swing_Left_Selector"
          and I_new["SkyyGear_SpdF_Mace_Weapon_Mace_Primary_Swing_Left_Selector"]["Next"] == "SkyyGear_SpdF_Mace_Weapon_Mace_Primary_Swing_Left_Selector_Next"
          and I_new["SkyyGear_SpdF_Mace_Weapon_Mace_Primary_Swing_Left_Selector_Next"] == {"Type": "Simple", "$Comment": "Pad the interaction length",
                                                                                          "RunTime": 0.2919},
          "S: the Fast mace Swing_Left -> named Next (its Replace, renamed variable kept) -> Selector -> named pad step (the vanilla shape, named)")


# ====================================================================================================== V + X
def run_engine(out):
    from jpype import JClass, JArray, JInt, JLong, JShort, JFloat, JDouble, JImplements, JOverride, JObject, JBoolean
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
    E = H["engine_boot"](K)
    K.check(set(E["fail"]) <= set(E["vfail"]), "V: the jar as its own pack: no failed store of its own (%s vs vanilla %s)" % (E["fail"], E["vfail"]))
    ours = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and ("SkyyGear_Spd_Mace" in r[1] or "Mace_Primary_Swing" in r[1] and "_Next" in r[1])]
    K.check(not ours, "V: no SEVERE / WARNING about the named mace steps in the bare boot: %s" % ours[:3])
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
    blk = L[ti:]
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
    # the stat table grew by the 9 tool rows: GearDefs.NS is a compile-time constant, so every method that sizes an int[NS] / int[NS + 1] array
    # changes only in that number - such a member counts as NS-only (checked: the code is equal once NS / NS + 1 are named)
    ns_a = int(pa.get(PKG + "GearDefs").getField("NS").getConstantValue())
    ns_b = int(pb.get(PKG + "GearDefs").getField("NS").getConstantValue())
    K.check(ns_a == 41 and ns_b == 50, "C: GearDefs.NS 41 -> 50 (the 9 tool rows): %d -> %d" % (ns_a, ns_b))

    def nsn(code, ns):
        code = re.sub(r"(?<![\w.#])%d(?![\w.])" % (ns + 1), "NS1", code)
        return re.sub(r"(?<![\w.#])%d(?![\w.])" % ns, "NS", code)
    diffs, nsonly = {}, {}
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn, ("0.2.16", "0.2.17")), members(pb, cn, ("0.2.16", "0.2.17"))
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        real = [k for k in dd if not (k in ma and k in mb and k.startswith("m ") and nsn(ma[k], ns_a) == nsn(mb[k], ns_b))]
        if len(real) != len(dd):
            nsonly[cn[len(PKG):]] = sorted(k.split("(")[0] for k in dd if k not in real)
        if real:
            diffs[cn[len(PKG):]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in real]
    K.notes.append("C: NS-only members (int[NS] sizes, nothing else): %s" % nsonly)
    add = sorted(c[len(PKG):] for c in set(nb) - set(na))
    gone = sorted(c[len(PKG):] for c in set(na) - set(nb))
    print("C. class compare 0.2.16 -> 0.2.17: + %s - %s" % (add, gone))
    for k in sorted(diffs):
        print("   %-16s %s" % (k, ", ".join(diffs[k])[:900]))
    K.check(not add and not gone, "C: no class added or removed: + %s - %s" % (add, gone))
    unexpected = sorted(set(diffs) - EXPECT_CHANGED)
    missing = sorted(EXPECT_CHANGED - set(diffs))
    K.check(not unexpected and not missing, "C: exactly the listed classes changed (unexpected %s, listed but unchanged %s)" % (unexpected, missing))
    want = {"GearData": {"+m toolFam", "+m toolRolls", "+m forgeable", "+m toolRolled"},
            "GearRoll": {"~m allowed", "~m pool", "+m boundsX", "+m spare", "~m rollMods", "~m newDoc", "~m craftDoc", "~m craftXp", "~m payCraft",
                         "~m reforge", "~m identify", "+f TX_ID", "+f TX_PCT", "+m toolXpPct", "~m craftable", "~<clinit>"},
            "GearTool": {"+m modv", "+m powKey", "+m fortKey", "+m wisKey", "+m eff", "~m stats", "~m held", "~m lines", "~m statusText"},
            "GearView": {"+m toolDead", "~m statLines", "~m lines", "~m apply"},
            "GearForge": {"+m docOf", "~m refuse", "~m rows", "~m reforge", "~m levelUp"},
            "ReforgePage": {"~m pick", "~m anvil", "~m list", "~m build"}, "GearIdent": {"~m refuse"},
            "GearDefs": {"+f S_TMASK", "+f T_FAM", "~<clinit>"}}
    bad = {}
    for k, v in want.items():
        got = set(diffs.get(k, []))
        if got != v:
            bad[k] = (sorted(v - got), sorted(got - v))
    K.check(not bad, "C: the classes changed exactly where the patch says (missing / extra): %s" % bad)
    cfg = set(diffs.get("GearCfg", []))
    K.check({"+m migrate0217", "+m trUpdate", "+m boostOf", "+m checkBoost", "+m toolBoost", "~m apply", "+f TOOL_RAR", "+f TOOL_RBT", "+f TR_GL",
             "~<clinit>", "~m defaultsText"} <= cfg and all(x.startswith("+") or x in ("~m apply", "~<clinit>", "~m defaultsText") for x in cfg),
            "C: GearCfg gains the update, the boost row, the fields (only apply + clinit change): %s" % sorted(cfg))
    K.check(set(diffs.get("CfgRows", [])) == {"~<clinit>"} and set(diffs.get("CfgFile", [])) == {"~<clinit>"}, "C: CfgRows / CfgFile: only the row tables")
    pl = set(diffs.get("SkyyGearPlugin", []))
    K.check(pl and all(x.startswith("~") for x in pl), "C: SkyyGearPlugin: the version + the migrate0217 call only: %s" % sorted(pl))
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
    K.check(Cfg.trUpdate(fresh) is None and Cfg.ubUpdate(fresh) is None and Cfg.gmUpdate(fresh) is None and Cfg.guUpdate(fresh) is None,
            "D: a fresh 0.2.17 file carries the 0.2.14 - 0.2.17 markers")
    old = open(os.path.join(home, "config.properties"), "rb").read().decode("latin-1")
    BLOCK = fresh[fresh.index("# ---- Tool rarity: crafted gathering tools roll a rarity and tool modifiers (SkyyGear 0.2.17) ----"):]
    K.check("part.toolRarity" not in old and "stats.mpow" not in old, "D: the live copy has no 0.2.17 key yet")
    base = old
    for nm in ("guUpdate", "gmUpdate", "ubUpdate"):
        rr = getattr(Cfg, nm)(base)
        if rr is not None:
            base = str(rr[0])
            K.notes.append("D: the live copy lacked the %s block (added first, like the setup order)" % nm)

    def upd(text):
        r = Cfg.trUpdate(text)
        return None if r is None else (str(r[0]), [str(x) for x in r[1]], str(r[2]))
    r = upd(base)
    exp = base + "\n" + BLOCK if base.endswith("\n") else None
    K.check(r is not None and exp is not None and r[0] == exp and r[1] == [] and r[2].startswith("part.toolRarity, tool.rarityBoost")
            and r[2].endswith("stats.awis") and r[2].count(",") == 14,
            "D: the live file: the block appended = exactly the fresh file's block (15 keys), nothing else changed: %s" % (r[2][:80] if r else None))
    K.check(upd(r[0]) is None, "D: the updated text carries the marker (run once)")
    rc = upd(base.replace("\n", "\r\n"))
    K.check(rc is not None and rc[0] == exp.replace("\n", "\r\n"), "D: a CRLF file keeps CRLF on every line (block included)")
    rn = upd(base.rstrip("\n"))
    K.check(rn is not None and rn[0] == exp.rstrip("\n"), "D: a file without a final newline: the block after its last line, still no final newline")
    hand = base + "tool.xpCraft=40\nstats.mpow=50,3\n"
    rh = upd(hand)
    K.check(rh is not None and rh[0].count("tool.xpCraft=") == 1 and "tool.xpCraft=40" in rh[0] and rh[0].count("stats.mpow=") == 1 and "stats.mpow=50,3" in rh[0]
            and len(rh[1]) == 2 and "stats.awis=10,8" in rh[0], "D: keys already in the file are KEPT + noted (2), the rest added: %s" % (rh[1] if rh else None))
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    files0 = sorted(os.path.relpath(os.path.join(a, f), home) for a, d, fs in os.walk(home) for f in fs)
    log0 = open(os.path.join(home, "config-changes.log"), "rb").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else b""
    snaps = []
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214",
                  "migrate0215", "migrate0216", "migrate0217"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(os.path.join(home, "config.properties"), "rb").read())
        K.check(bool(Cfg.TOOL_RAR) and str(Cfg.TOOL_RBT) == "0 5 10 15 20 25" and int(Cfg.TOOL_XPC) == 100
                and int(Cfg.S_MAX[int(JClass(PKG + "GearDefs").sIndex("mpow"))]) == 30, "D start %d: the loaded tool rows" % step)
    K.check(snaps[0] == exp.encode("latin-1"), "D start 1: the live copy = the expected text byte for byte")
    K.check(snaps[1] == snaps[0], "D start 2: nothing changes")
    files1 = sorted(os.path.relpath(os.path.join(a, f), home) for a, d, fs in os.walk(home) for f in fs)
    newf = sorted(set(files1) - set(files0))
    hb = [open(os.path.join(home, f), "rb").read() for f in newf if f.startswith("config-history")]
    K.check(any(b == base.encode("latin-1") for b in hb) and all(f.startswith("config-history") for f in newf)
            and all(f.startswith("config-history") for f in set(files0) - set(files1)),
            "D: the History copy before 0.2.17 holds the bytes it saw; only config-history files were added (the kit prunes past KEEP): %s" % newf)
    log1 = open(os.path.join(home, "config-changes.log"), "rb").read() if os.path.isfile(os.path.join(home, "config-changes.log")) else b""
    addl = [x for x in log1[len(log0):].decode("utf-8", "replace").split("\n") if x.strip()]
    K.check(log1.startswith(log0) and not [x for x in addl if "0.2.17" in x],
            "D: no config-changes.log row from 0.2.17 (a pure addition - no value changed): %s" % addl)
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
        assert '"Version": "0.2.16"' in z_.read("manifest.json").decode("utf-8"), "the old jar is not 0.2.16"
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
