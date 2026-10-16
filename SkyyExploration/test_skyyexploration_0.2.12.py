"""Harness for SkyyExploration 0.2.12 (EXPLORATION NAMES: Lost Loot -> Loot Bag, Supply Drop -> Magic Box, Lost Treasure stays; ids
unchanged; tools/exploration_0_2_12_patch.py) = the 0.2.11 harness (LOST LOOT GEAR CAP) carried forward. Build first:
python tools/exploration_0_2_12_patch.py && python SkyyExploration/build_skyyexploration_0.2.12.py

    python SkyyExploration/test_skyyexploration_0.2.12.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.2.11 -> 0.2.12 (the 0.2.8 harness's compare; non-class entries: manifest.json + server.lang only): text constants
              only - no field / method added or removed
  RN          0.2.12 NAMES: the lang block names = Loot Bag (I)-(III), Lost Treasure (IV), Magic Box under the SAME ids Skyy_LootChest_T1-T5;
              no "Lost Loot" / "supply drop" / "Supply Drop" left in any class constant, lang or manifest; every jar entry name = 0.2.11's
              (no id / file renamed); the 0.2.8 X + CAP phases below run with the 0.2.8 harness's own texts renamed the same way
  CAP         EXECUTED: the REAL LgCore.loot (the 0.2.8 LgApi stand-in world, stand-in SkyyGear / coins bridges, a stand-in vanilla roll
              of 5 gear + 3 other stacks, 2 bags per pile) over many claims per tier: tier I-II exactly 1 gear, tier III-IV 2-4 (each of
              2, 3, 4 seen), tier 5 (supply drop) uncapped (all 7); the number of finds never changes; SkyyGear (gear:fn:box) is never
              asked for a capped gear find; replacements come from the same list (never a weapon / armor); a list with only gear or no
              list -> coin finds; the rows / defaults / clamps; isGear (ammo is not gear); static: the chest luck roll keeps its own call
  X, D        the 0.2.8 phases carried forward on the 0.2.11 jar (run_exec; run_live = START TWICE on a scratch COPY of the live
              Skyy_SkyyExploration, 0.2.10 vs 0.2.11)
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, io, tokenize, types, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import soundpass_kit as SK

# 0.2.12: the 0.2.8 harness with the SAME rename applied to its string literals (its own copy of the rule, independent of the patch):
# its texts ("This supply drop was already claimed.", "Lost Loot (I)" ...) become the 0.2.12 ones; ids are never in these words
NAMES = [("Lost Loot", "Loot Bag"), ("lost loot", "loot bag"), ("Supply Drop", "Magic Box"), ("Supply drops", "Magic boxes"),
         ("Supply drop", "Magic box"), ("supply drops", "magic boxes"), ("supply drop", "magic box")]


def renamed(text):
    text = text.replace(chr(13) + chr(10), chr(10))
    offs = [0]
    for ln in text.split(chr(10)):
        offs.append(offs[-1] + len(ln) + 1)
    parts, last = [], 0
    for t in tokenize.generate_tokens(io.StringIO(text).readline):
        if t.type == tokenize.STRING or t.type == getattr(tokenize, "FSTRING_MIDDLE", -1):
            a, b = offs[t.start[0] - 1] + t.start[1], offs[t.end[0] - 1] + t.end[1]
            seg = text[a:b]
            for o, n in NAMES:
                seg = seg.replace(o, n)
            parts.append(text[last:a])
            parts.append(seg)
            last = b
    parts.append(text[last:])
    return "".join(parts)


_p28 = os.path.join(HERE, "test_skyyexploration_0.2.8.py")
T28 = types.ModuleType("test_skyyexploration_0_2_8")
T28.__file__ = _p28
_s28 = renamed(open(_p28, encoding="utf8").read())
for _o, _n in (('"build_skyyexploration_0.2.8.py"', '"build_skyyexploration_0.2.12.py"'),   # the FIX-rename scan reads the 0.2.12 script
               ("""'("luggage", "Loot Bag")' in src""", """'("luggage", "Loot Bags")' in src"""),     # 0.2.12 plural tab / stats texts
               ('st.startswith("Loot Bag on")', 'st.startswith("Loot Bags on")')):
    assert _s28.count(_o) == 1, _o
    _s28 = _s28.replace(_o, _n)
exec(compile(_s28, _p28, "exec"), T28.__dict__)
T28.NONCLASS = ["Server/Languages/en-US/server.lang", "manifest.json"]   # 0.2.11 -> 0.2.12: the asset files are the same bytes, lang renamed
T28.OLD_JAR = os.path.join(HERE, "SkyyExploration-0.2.11.jar")   # run_live: the live records read by the SET pin and the new jar
_cmp28 = T28.run_compare
HK.run_compare = lambda out, jar, old_jar, pkg, expect, added, removed=(): _cmp28(out, jar, old_jar, pkg, expect, added)   # the kit now passes removed


class _Child28(HK.Child):
    """the 0.2.8 X phase's 'no texture in the jar' check predates 0.2.10's hub shell: since 0.2.10 the jar ships the kit's 59 Sky Window
    files (Common/UI/Custom/SkyyKit/ only, sha256-pinned by the kit). That ONE check is re-asked here: no vanilla path copied, and every
    .png / .blockymodel in the jar is kit art under Common/UI/Custom/SkyyKit/."""
    JAR = None

    def check(self, cond, what):
        if not cond and what.startswith("X assets: no vanilla file copied or shadowed") and _Child28.JAR:
            import zipfile
            names = zipfile.ZipFile(_Child28.JAR).namelist()
            art = [n for n in names if n.endswith((".png", ".blockymodel"))]
            cond = len(art) == 59 and all(n.startswith("Common/UI/Custom/SkyyKit/") for n in art)
            what += " (0.2.10+: only the kit's 59 SkyyKit files: %s)" % cond
        return HK.Child.check(self, cond, what)


def run_exec28(out, jar, scratch, home):
    import types
    _Child28.JAR = jar
    T28.HK = types.SimpleNamespace(**dict(vars(HK), Child=_Child28))
    T28.run_exec(out, jar, scratch, home)

VERSION = "0.2.12"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)))
OLD_JAR = T28.OLD_JAR
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "small01", "expl")))
PKG = T28.PKG
CAPS = [("loot.gearCapLow", "GEAR_LO", "1"), ("loot.gearCapMidMin", "GEAR_MID_MIN", "2"), ("loot.gearCapMidMax", "GEAR_MID_MAX", "4")]
EXPECT = {   # 0.2.12: text constants only (the renamed texts + the version)
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "ExAdminOps": ["~m help"], "ExAirdropCmd": ["~c "],
    "ExLuggageClearCmd": ["~c "], "ExLuggageCmd": ["~c "], "ExLuggageListCmd": ["~c "], "ExLuggageTierCmd": ["~c "], "ExpCfg": ["~m load"],
    "ExpLgMig": ["~m logLine", "~m migrate"], "LgAir": ["~m adminClear", "~m adminDrop", "~m announce", "~m clearNear"],
    "LgCore": ["~<clinit>", "~m adminPlace", "~m listNear", "~m name", "~m placeNear", "~m refuse", "~m statsText", "~m use", "~m worldPass"],
    "SkyyExplorationPlugin": ["~m setup"],
}
ADDED = []
GEAR = ["Weapon_Sword_Iron", "Armor_Iron_Chest", "Weapon_Shortbow_Iron", "Weapon_Mace_Iron", "Armor_Iron_Head"]
OTHER = [("Food_Kebab_Meat", 2), ("Ore_Iron", 3), ("Weapon_Arrow_Crude", 20)]   # the arrows: ammo (not gear, not capped, never a spare)


def run_cap(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JString, JInt, JLong, JDouble
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Cfg, Core, Site, Eng, EIO, Rows = P("ExpCfg"), P("LgCore"), P("LgSite"), P("LgEng"), P("ExpIO"), P("CfgRows")
    Props, UUID, AL, Sys = JClass("java.util.Properties"), JClass("java.util.UUID"), JClass("java.util.ArrayList"), JClass("java.lang.System")
    # ---------------- config + rows
    Cfg.apply(Props())
    K.check([int(getattr(Cfg, f)) for _k, f, _d in CAPS] == [1, 2, 4], "CFG an old file without the lines = Skyy's numbers (1, 2-4)")
    pp = Props()
    for k, v in (("loot.gearCapLow", "99"), ("loot.gearCapMidMin", "7"), ("loot.gearCapMidMax", "3")):
        pp.setProperty(k, v)
    Cfg.apply(pp)
    K.check(int(Cfg.GEAR_LO) == 20 and int(Cfg.GEAR_MID_MIN) == 7 and int(Cfg.GEAR_MID_MAX) == 7, "CFG clamps: at most 20; max below min reads as min")
    pp = Props()
    pp.setProperty("loot.gearCapLow", "-3")
    Cfg.apply(pp)
    K.check(int(Cfg.GEAR_LO) == 0, "CFG clamps: at least 0")
    Cfg.apply(Props())
    defs = str(Cfg.DEFAULTS)
    K.check(all(("%s=%s" % (k, d)) in defs for k, _f, d in CAPS), "CFG a fresh config.properties lists the three lines with Skyy's numbers")
    rows = SK.kit_rows(Rows)
    for k, _f, d in CAPS:
        r = rows.get(k)
        K.check(r is not None and r[2] == "luggage" and r[3] == "int" and r[4] == d and r[5] == "0" and r[6] == "20" and "live" in r[9],
                "ROW %s: Server Setup -> Exploration -> Lost Loot, a live int 0-20, default %s: %s" % (k, d, r))
    K.check(str(Cfg.live("loot.gearCapMidMax")) == "4", "CFG live value (what /exploreadmin get shows)")
    # ---------------- isGear
    yes = ["Weapon_Sword_Iron", "Weapon_Shortbow_Bomb", "Weapon_Battleaxe_Crude", "Weapon_Shield_Wood", "Armor_Iron_Chest", "Skyy_Unid_Bag_Rare"]
    no = ["Weapon_Arrow_Crude", "Weapon_Bomb_Fire", "Weapon_Bangstick", "Weapon_Dart_Tribal", "Weapon_Grenade_Frag", "Food_Kebab_Meat",
          "Tool_Pickaxe_Iron", "Ore_Iron", "Weapon_", None]
    K.check(all(Core.isGear(x) for x in yes) and not any(Core.isGear(x) for x in no), "isGear %s %s" % ([x for x in yes if not Core.isGear(x)], [x for x in no if Core.isGear(x)]) + ": isGear: weapons / armor / mystery bags yes; ammo, tools, food no")
    # ---------------- gearCap
    caps = dict((t, set(int(Core.gearCap(t)) for _ in range(600))) for t in (1, 2, 3, 4, 5))
    K.check(caps[1] == {1} and caps[2] == {1} and caps[3] == {2, 3, 4} and caps[4] == {2, 3, 4} and caps[5] == {-1},
            "gearCap: I-II 1, III-IV a roll of 2..4 (all seen), supply drop none: %s" % caps)
    # ---------------- the stand-in world + bridges
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    EIO.BRIDGE = None
    state = {"placed": {}, "log": [], "ground": "Soil_Grass", "given": []}
    Eng.API = T28.sim(state)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    Unsafe = JClass("sun.misc.Unsafe")
    fu = Unsafe.class_.getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    us = fu.get(None)

    def mk(id_, n):
        try:
            return IS(id_, JInt(n))
        except Exception:
            st_ = us.allocateInstance(IS.class_)
            for fn_, v_ in (("itemId", JString(id_)), ("quantity", JInt(n))):
                f_ = IS.class_.getDeclaredField(fn_)
                f_.setAccessible(True)
                f_.set(st_, v_)
            return st_
    K.check(not mk("Ore_Iron", 3).isEmpty() and str(mk("Ore_Iron", 3).getItemId()) == "Ore_Iron", "stand-in stacks work (getItemId / isEmpty)")
    ROLL_MODE = {"m": "mixed", "n": 0}

    @JImplements("java.util.function.Function")
    class Roll:
        @JOverride
        def apply(self, table):
            ROLL_MODE["n"] += 1
            state["log"].append(("roll", str(table)))
            l = AL()
            for g in GEAR:
                l.add(mk(g, 1))
            if ROLL_MODE["m"] == "mixed":
                for o, n in OTHER:
                    l.add(mk(o, n))
            return l

    @JImplements("java.util.function.Function")
    class CoinAdd:
        @JOverride
        def apply(self, a):
            state["log"].append(("coins", int(a[1])))
            return JLong(1)

    @JImplements("java.util.function.Function")
    class Box:
        @JOverride
        def apply(self, a):
            state["log"].append(("box", int(a[3]), None if a[0] is None else str(a[0].getItemId())))
            return mk("Skyy_Unid_Bag_Rare", 1)

    @JImplements("java.util.function.Function")
    class Describe:
        @JOverride
        def apply(self, b_):
            return JArray(JString)([str(b_.getItemId()).replace("_", " ")])

    @JImplements("java.util.function.Function")
    class Rarity:
        @JOverride
        def apply(self, b_):
            return JString("rare") if str(b_.getItemId()).startswith("Skyy_Unid_") else None
    br.put("coins:fn:add", CoinAdd())
    br.put("gear:fn:box", Box())
    br.put("gear:fn:describe", Describe())
    br.put("gear:fn:rarity", Rarity())
    Core.ROLL = Roll()
    Dbl = JArray(JDouble)
    Cfg.LG_BAGS = Dbl([2.0, 2.0, 2.0, 2.0])          # 2 bags per pile (deterministic)
    Cfg.LG_XP = Dbl([0.0, 0.0, 0.0, 0.0])            # no XP card (no profile store here)
    Cfg.LG_COIN_MIN = Dbl([10.0, 10.0, 10.0, 10.0])
    Cfg.LG_COIN_MAX = Dbl([10.0, 10.0, 10.0, 10.0])
    Cfg.AIR_BAGS, Cfg.AIR_XP, Cfg.AIR_COIN_MIN, Cfg.AIR_COIN_MAX = 2.0, 0, 10, 10
    Cfg.LG_VANILLA = True
    u = UUID.fromString("00000000-0000-4000-8000-0000000000c1")

    def claim(tier):
        s1 = Site.parse("1\t65\t1\t%d\t23\t0\t10\t0\t10\t7\t" % tier)
        cards = AL()
        n0, g0 = len(state["log"]), len(state["given"])
        got = str(Core.loot(None, None, None, None, u, s1, cards))
        ids = [str(c[0]) for c in cards]
        given = [x[0] for x in state["given"][g0:]]
        log = state["log"][n0:]
        return {"ids": ids, "gear": sum(1 for i in ids if i.startswith("Skyy_Unid_")), "coins": sum(1 for i in ids if i == "Ingredient_Bar_Gold"),
                "given": given, "box": [e for e in log if e[0] == "box"], "rolls": [e[1] for e in log if e[0] == "roll"], "got": got}
    NAT = 1 + 2 + len(GEAR) + len(OTHER)              # coins + 2 bags + the list = 11 finds without a cap
    N = 250
    for tier, want, label in ((1, {1}, "Lost Loot (I)"), (2, {1}, "Lost Loot (II)"), (3, {2, 3, 4}, "Lost Loot (III)"),
                              (4, {2, 3, 4}, "Lost Treasure (IV)"), (5, {7}, "Supply Drop")):
        res = [claim(tier) for _ in range(N)]
        gears = set(r["gear"] for r in res)
        K.check(gears == want, "CAP %s over %d claims: gear finds per claim %s (want %s)" % (label, N, sorted(gears), sorted(want)))
        K.check(all(len(r["ids"]) == NAT for r in res), "CAP %s: every claim keeps its %d finds (%s)" % (label, NAT, sorted(set(len(r["ids"]) for r in res))))
        K.check(all(len(r["box"]) == r["gear"] for r in res), "CAP %s: SkyyGear (gear:fn:box) asked only for the gear given" % label)
        K.check(all(len(r["given"]) == len(r["ids"]) - 1 for r in res), "CAP %s: every find but the coins is given as an item" % label)
        spares = [i for r in res for i in r["ids"][1 + r["gear"] + len(OTHER):]] if tier < 5 else []
        K.check(all(i in ("Food_Kebab_Meat", "Ore_Iron") for i in spares) and (tier == 5 or len(spares) > 0),
                "CAP %s: the replacements come from the same list and are never a weapon / armor / ammo (%d: %s)" % (label, len(spares), sorted(set(spares))))
        tb = "Zone2_Encounters_Tier4" if tier == 5 else "Zone2_Encounters_Tier%d" % tier
        K.check(all(all(t == tb for t in r["rolls"]) for r in res), "CAP %s: every roll is the pile's own list (%s)" % (label, tb))
        K.check(all(r["coins"] == 1 for r in res), "CAP %s: coins once (the list had other finds)" % label)
        if tier == 1:
            r0 = res[0]
            K.check("Food Kebab Meat" in r0["got"] or "Ore Iron" in r0["got"], "CAP the chat line names the replacements: %s" % r0["got"])
    # tier 1: the two bags come first, so the cap is spent there: 1 bag + 0 list gear
    r1 = claim(1)
    K.check([b[2] for b in r1["box"]] == [None], "CAP order: the bag rolls are counted first (one bag, no vanilla gear turned into a bag)")
    # a list of gear only -> coin finds
    ROLL_MODE["m"] = "gear"
    r = claim(1)
    K.check(len(r["ids"]) == 1 + 2 + len(GEAR) and r["gear"] == 1 and r["coins"] == 1 + 6 and len(r["rolls"]) == 1 + 6 * 8,
            "CAP a list with only gear: each capped find = a coin find after 8 tries (finds %d, coins %d, rolls %d)" % (len(r["ids"]), r["coins"], len(r["rolls"])))
    ROLL_MODE["m"] = "mixed"
    # no vanilla roll (luggage.vanillaRoll off) and the bags alone over the cap -> coins
    Cfg.LG_VANILLA = False
    r = claim(1)
    K.check(len(r["ids"]) == 3 and r["gear"] == 1 and r["coins"] == 2 and r["rolls"] == [], "CAP no vanilla roll: the 2nd bag becomes a coin find (%s)" % r["ids"])
    r = claim(4)
    K.check(len(r["ids"]) == 3 and r["gear"] == 2 and r["coins"] == 1, "CAP no vanilla roll, tier IV: 2 bags <= the cap 2-4 = unchanged")
    Cfg.LG_VANILLA = True
    # the rows change it live
    Cfg.GEAR_LO = 0
    r = claim(2)
    K.check(r["gear"] == 0 and len(r["ids"]) == NAT and r["box"] == [], "CAP loot.gearCapLow 0: no gear at all, still %d finds" % NAT)
    Cfg.GEAR_LO = 20
    r = claim(1)
    K.check(r["gear"] == 7 and len(r["ids"]) == NAT, "CAP loot.gearCapLow 20: nothing capped (7 gear)")
    Cfg.GEAR_MID_MIN, Cfg.GEAR_MID_MAX = 3, 3
    K.check(set(claim(3)["gear"] for _ in range(40)) == {3}, "CAP loot.gearCapMidMin = Max = 3: exactly 3")
    Cfg.apply(Props())
    Core.ROLL = None
    Eng.API = None
    # ---------------- static
    g = PW.calls(jar)
    lc = g.get("LgCore.loot", set())
    K.check(PKG + "LgCore.gearCap" in lc and PKG + "LgCore.spare" in lc and PKG + "LgCore.drops" in lc and PKG + "LgCore.isGear" in lc,
            "STATIC loot -> gearCap / isGear / drops / spare")
    users = sorted(m for m, cs in g.items() if any(c.endswith("ItemModule.getRandomItemDrops") for c in cs))
    K.check(len(users) == 2 and "LgCore.drops" in users and "LgCore.loot" not in users,
            "STATIC the vanilla roll: LgCore.drops (Lost Loot / supply drops) + the chest luck roll's own (unchanged): %s" % users)
    K.save()


def run_names(out, jar, scratch, _home):
    K = HK.Child(out)
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(T28.OLD_JAR)
    K.check(sorted(zn.namelist()) == sorted(zo.namelist()), "RN: every jar entry name = 0.2.11's (no id / file renamed)")
    lang = dict(l.split(" = ", 1) for l in zn.read("Server/Languages/en-US/server.lang").decode("utf8").splitlines() if " = " in l)
    want = ["Loot Bag (I)", "Loot Bag (II)", "Loot Bag (III)", "Lost Treasure (IV)", "Magic Box"]
    got = [lang.get("items.Skyy_LootChest_T%d.name" % t) for t in (1, 2, 3, 4, 5)]
    K.check(got == want, "RN: block names under the same ids Skyy_LootChest_T1-T5: %s" % got)
    left = []
    for n in zn.namelist():
        b = zn.read(n)
        for w in (b"Lost Loot", b"lost loot", b"upply drop", b"upply Drop", b"Airdrops"):
            if w in b:
                left.append((n, w))
    K.check(not left, "RN: no old name left in any class constant / lang / manifest: %s" % left[:5])
    rows = zn.read("com/skyy/explore/CfgRows.class")
    K.check(b"Loot Bags" in rows and b"Magic Boxes" in rows and b"luggage.enabled" in rows and b"airdrop.enabled" in rows,
            "RN: Server Setup: the 'Loot Bags' / 'Magic Boxes' tabs, keys luggage.* / airdrop.* unchanged")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyExploration", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("names", run_names), ("cap", run_cap), ("exec", run_exec28), ("live", T28.run_live)], script=__file__,
           live=(T28.LIVE_DIR, "Skyy_SkyyExploration"))
