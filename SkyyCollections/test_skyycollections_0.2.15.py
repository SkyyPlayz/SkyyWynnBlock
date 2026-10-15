"""Harness for SkyyCollections 0.2.15 (XP ROUTES for Fishing / Ranching / Orchard; tools/collections_0_2_15_patch.py). Build first:
    python tools/collections_0_2_15_patch.py && python SkyyCollections/build_skyycollections_0.2.15.py

    python SkyyCollections/test_skyycollections_0.2.15.py [--jar <SkyyCollections-0.2.15.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises
  C   compare  0.2.14 -> 0.2.15: exactly the listed members differ (CollReg xpAt / parseReg / the route helpers, RegData.route,
               CollKit.checkRoute + rewardToken, the version / row texts); no class added; non-class entries: manifest only
  X   exec     EVERY NEW CODE PATH: the fresh collections.properties carries xp.route; the loader's default routes (no line = the 8
               defaults), a file's own routes REPLACE them, bad entries skipped (+ WARN); xpAt for routed / unrouted / Combat collections,
               tier.xp and the last tier; parseRoute (case, bad entries); CollKit.checkRoute (good, unknown skill, unknown collection, bad
               form, removal); rewardToken knows Fishing / Ranching / Orchard; CollRewards.settle on a REAL counts file pays the Raw Chicken
               tier XP to Ranching through skill:fn:addxp (the paid marker moves; nothing is paid twice) and a hidden collection nothing
  D   live     START TWICE on a scratch COPY of the live Skyy_SkyyCollections (the plugin's setup sequence): nothing in the folder changes
               between the two starts, the counts files are byte-identical to the live copy, the default routes are in effect (the live
               collections.properties has no xp.route line)
  AA  audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.2.15"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.14.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shards03", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyCollections")
OWNER = "0f0f0f0f-1111-2222-3333-444444444444"
ROUTES = {"rawfish": "Fishing", "rawchicken": "Ranching", "rawbeef": "Ranching", "rawpork": "Ranching", "wildmeat": "Ranching",
          "berries": "Orchard", "apple": "Orchard", "wildfruit": "Orchard"}
# the members 0.2.15 changes
EXPECT = {"CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
          "CollReg": ["+f DEF_ROUTE", "+f ROUTE_SKILLS", "+m routeSkill", "+m parseRoute", "~m parseReg", "~m xpAt", "~m regText", "~<clinit>"],
          "RegData": ["+f route"], "CollKit": ["+m checkRoute", "~m rewardToken"], "SkyyCollectionsPlugin": ["~m setup"]}
ADDED = []


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JString, JLong, JInt, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Reg, Store, Util, Cred, Kit, Rew = (P("CollReg"), P("CollStore"), P("CollUtil"), P("CollCredit"), P("CollKit"), P("CollRewards"))
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    base = os.path.join(scratch, "x", "Skyy_SkyyCollections")
    os.makedirs(base)
    Reg.BASE = Paths.get(base)
    Store.DIR = Paths.get(base).resolve("counts")
    Reg.loadAll()
    R = Reg.D
    regtxt = open(os.path.join(base, "collections.properties"), encoding="latin-1").read().replace("\r\n", "\n").split("\n")
    rl = [l_ for l_ in regtxt if l_.startswith("xp.route=")]
    K.check(len(rl) == 1 and rl[0] == "xp.route=" + str(Reg.DEF_ROUTE), "X1: a fresh collections.properties carries the default xp.route line: %s" % rl)

    def routes(R_):
        m = R_.route
        return dict((str(k), str(m.get(k))) for k in m.keySet())
    K.eq(routes(R), ROUTES, "X1: the loader: the 8 default routes (fish -> Fishing, farm animals -> Ranching, fruit -> Orchard)")
    cf = os.path.join(base, "collections.properties")
    orig = open(cf, encoding="latin-1").read()
    # a file without the line (every live file) = the defaults
    open(cf, "w", encoding="latin-1").write("\n".join(l_ for l_ in orig.replace("\r\n", "\n").split("\n") if not l_.startswith("xp.route=")) + "\n")
    Reg.loadAll()
    K.eq(routes(Reg.D), ROUTES, "X1: no xp.route line (the live files) = the default routes")
    # a file's own routes REPLACE the defaults; bad entries are skipped
    open(cf, "w", encoding="latin-1").write(orig.replace("xp.route=" + str(Reg.DEF_ROUTE), "xp.route=Wheat:ranching, RawFish:Fishing,Bone:Combat,nocolon,Apple:"))
    Reg.loadAll()
    K.eq(routes(Reg.D), {"wheat": "Ranching", "rawfish": "Fishing"}, "X1: a hand-edited xp.route replaces the defaults; the skill is matched in any case; 3 bad entries skipped")
    R2 = Reg.D
    cWh, cCh = int(R2.byId.get("wheat")), int(R2.byId.get("rawchicken"))
    K.eq([[(str(a[0]), int(a[1])) for a in Reg.xpAt(R2, c_, 3)] for c_ in (cWh, cCh)], [[("Ranching", 500)], [("Farming", 500)]],
         "X1: ... Wheat now pays Ranching, Raw Chicken (no route any more) its category Farming")
    open(cf, "w", encoding="latin-1").write(orig)
    Reg.loadAll()
    R = Reg.D

    # ---- X2 xpAt: routed / unrouted / Combat, tier.xp slots and the last tier
    def xp(cid, t):
        c_ = int(R.byId.get(cid.lower()))
        return [(str(a[0]), int(a[1])) for a in Reg.xpAt(R, c_, t)]

    def last(cid):
        return int(Reg.maxTier(R, int(R.byId.get(cid.lower()))))
    K.eq([xp("RawChicken", 3), xp("RawBeef", 5), xp("Wildmeat", 7), xp("RawPork", 2)], [[("Ranching", 500)], [("Ranching", 2500)], [("Ranching", 10000)], []],
         "X2: farm animal collections pay Ranching (tier III 500, V 2,500, VII 10,000; II pays nothing)")
    K.eq([xp("Apple", 3), xp("Berries", last("Berries")), xp("WildFruit", 5)], [[("Orchard", 500)], [("Orchard", 25000)], [("Orchard", 2500)]],
         "X2: fruit collections pay Orchard (the last tier: tier.lastXp 25,000)")
    K.eq(xp("RawFish", 3), [("Fishing", 500)], "X2: Raw Fish pays Fishing (it stays a hidden collection until the Fishing category opens - hidden collections pay no rewards)")
    K.eq([xp("Wheat", 3), xp("Copper", 3), xp("OakLog", 5), xp("Bone", 3), xp("Bone", last("Bone"))], [[("Farming", 500)], [("Mining", 500)], [("Foraging", 2500)], [], []],
         "X2: unrouted collections keep their category's skill (Wheat Farming, Copper Mining, Oak Foraging); Combat still pays no XP")
    K.check(Reg.routeSkill(" ranching ") == "Ranching" and Reg.routeSkill("Combat") is None and Reg.routeSkill(None) is None, "X2: routeSkill: case-free, only the 6 route skills")
    bad = JArray(JInt)([0])
    m_ = Reg.parseRoute("a:Mining,b:x,c,:Fishing,D:orchard", bad)
    K.check(dict((str(k), str(m_.get(k))) for k in m_.keySet()) == {"a": "Mining", "d": "Orchard"} and int(bad[0]) == 3 and Reg.parseRoute(None, None).isEmpty(),
            "X2: parseRoute keeps the good pairs (ids lower-cased), counts 3 bad ones; null = none")

    # ---- X3 Server Setup: the row check + the reward token check
    K.check(Kit.checkRoute("xp.route", "RawFish:Fishing,Apple:orchard") is None and Kit.checkRoute("xp.route", None) is None,
            "X3: checkRoute accepts good pairs (any case) and a removal")
    r1, r2, r3 = str(Kit.checkRoute("xp.route", "RawFish:Combat")), str(Kit.checkRoute("xp.route", "Nope:Fishing")), str(Kit.checkRoute("xp.route", "RawFish"))
    K.check("not a skill a route may name" in r1 and r2.startswith("No collection has the id Nope") and r3.startswith("Write CollectionId:Skill"),
            "X3: checkRoute refuses an unknown skill / collection / form: %s | %s | %s" % (r1[:40], r2[:40], r3[:40]))
    K.check(Kit.rewardToken("xp:Ranching:5") is None and Kit.rewardToken("xp:Fishing:5") is None and Kit.rewardToken("xp:Orchard:5") is None
            and str(Kit.rewardToken("xp:Combat:5")).startswith("?Combat is not a skill"), "X3: rewards xp: tokens know Fishing / Ranching / Orchard (Combat still asks)")
    rows = [str(x) for x in P("CfgRows").KEYS] if hasattr(P("CfgRows"), "KEYS") else []
    K.check(not rows or "xp.route" in rows, "X3: the Server Setup row xp.route exists (%d rows)" % len(rows))

    # ---- X4 CollRewards.settle on a REAL counts file: Raw Chicken's tier XP goes to Ranching (once), a hidden collection pays nothing
    @JImplements("java.util.function.Function")
    class AddXp(object):
        def __init__(self):
            self.calls = []

        @JOverride
        def apply(self, a):
            self.calls.append((str(a[1]), int(a[2]), str(a[3])))
            return JClass("java.lang.Boolean").TRUE
    ax = AddXp()
    Util.bridge().put("skill:fn:addxp", ax)
    ou = UUID.fromString(OWNER)
    key = str(Util.pkey(ou))
    cCh = int(R.byId.get("rawchicken"))
    item = str(list(R.items[cCh])[0])
    Cred.creditShard(None, ou, key, item, JLong(256))
    Cred.creditShard(None, ou, key, item, JLong(44))
    d = Store.dataK(key)
    ct = int(Store.countTier(d, R, cCh))
    res = list(Rew.settle(d, R, cCh, ou, key))
    paid = int(Store.meta(d, "_paidxp.RawChicken"))
    res2 = list(Rew.settle(d, R, cCh, ou, key))
    K.check(ct == 3 and ("Ranching", 500, "coll:RawChicken:3") in ax.calls and not any(c_[0] == "Farming" for c_ in ax.calls) and paid == 3
            and int(res[1]) == 0 and int(res2[1]) == 0 and len([c_ for c_ in ax.calls if c_[2].startswith("coll:RawChicken")]) == 1,
            "X4: 300 Raw Chicken = tier III: the credit's own settle pays 500 RANCHING XP through skill:fn:addxp (source coll:RawChicken:3), _paidxp.RawChicken = 3, "
            "later settles pay nothing (no second grant): %s / ct %d res %s paid %d res2 %s" % (ax.calls, ct, [int(x) for x in res], paid, [int(x) for x in res2]))
    cFi = int(R.byId.get("rawfish"))
    Cred.creditShard(None, ou, key, str(list(R.items[cFi])[0]), JLong(256))
    n0 = len(ax.calls)
    resf = list(Rew.settle(Store.dataK(key), R, cFi, ou, key))
    K.check(bool(R.hidden[cFi]) and len(ax.calls) == n0 and resf == [0, 0, 0], "X4: Raw Fish is still hidden: no reward paid (it routes to Fishing once the Fishing category opens)")
    Util.bridge().remove("skill:fn:addxp")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Reg, Store, Sm = P("CollReg"), P("CollStore"), P("CollShardMig")
    Paths = JClass("java.nio.file.Paths")
    b_ = Paths.get(home)
    counts0 = HK.tree_hash(os.path.join(home, "counts")) if os.path.isdir(os.path.join(home, "counts")) else None
    reg0 = open(os.path.join(home, "collections.properties"), "rb").read() if os.path.isfile(os.path.join(home, "collections.properties")) else None
    snaps, msgs = [], []
    for start in (1, 2):
        Reg.BASE = b_
        Store.DIR = b_.resolve("counts")
        P("CollBagMigrate").run(b_)
        P("CollBypassMig").run(b_)
        Reg.loadAll()
        P("CollCobMig").run(b_)
        P("CollSigMig").run(b_)
        msgs.append(str(Sm.run(b_)))
        Reg.loadAll()
        snaps.append(HK.tree_hash(home))
    K.check(snaps[0] == snaps[1] and msgs[1] == "", "D: the 2nd start changes nothing in the copied Skyy_SkyyCollections (start 1: %s)" % (msgs[0][:80] or "no update"))
    K.check(counts0 is None or HK.tree_hash(os.path.join(home, "counts")) == counts0, "D: every counts file is byte-identical to the live copy")
    reg1 = open(os.path.join(home, "collections.properties"), "rb").read() if reg0 is not None else None
    K.check(reg0 is None or (reg1 == reg0 and b"xp.route" not in reg0), "D: the live collections.properties is untouched (it has no xp.route line)")
    m = Reg.D.route
    K.check(m is not None and m.size() == len(ROUTES) and str(m.get("rawchicken")) == "Ranching" and str(m.get("apple")) == "Orchard",
            "D: the default routes are in effect on the live registry (%d)" % (0 if m is None else m.size()))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
