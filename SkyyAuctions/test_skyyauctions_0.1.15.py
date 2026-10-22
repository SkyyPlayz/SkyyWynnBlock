"""Harness for SkyyAuctions 0.1.15 (BALANCE PASS P7: gathering gear off the AH, row blockGatheringGear; tools/auctions_0_1_15_patch.py).
Build first: python tools/auctions_0_1_15_patch.py && python SkyyAuctions/build_skyyauctions_0.1.15.py

    python SkyyAuctions/test_skyyauctions_0.1.15.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, -Xverify:all, tools/harness_kit.py):
  A   verify   every class loads + initialises
  C   compare  0.1.14 -> 0.1.15: AhCfg (+ BLOCK_GATHER / RULES_TEXT / GATHER_REASON / GATHER_IDS / loadRules), AhItem (+ isGatherGear,
               blockedReason), the kit (third file + row), the plugin setup only
  X   exec     EXECUTES AhItem.blockedReason on the real class: a Mining armor piece (zone + vanilla metal), Foraging / Farming / Fishing armor,
               a lifelong pickaxe / hatchet / multitool / watering can / Harvester -> refused with the reason text; a combat weapon, a pack
               combat armor piece, an ore, a Magic Bag (bag reason) as before; the switch off -> they list; GATHER_IDS = the build-time
               tools/tier_tags.py list (sorted: binarySearch works); loadRules fresh (default file) / typed false / junk; the kit row end to
               end (cmdSetConsole -> field + rules.properties line)
  D   live     a scratch COPY of the live NewBetaTest Skyy_SkyyAuctions: loadRules + the kit start TWICE: the first adds rules.properties (+ kit
               history / change files) and changes no existing file; the second changes nothing
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

VERSION = "0.1.15"
PKG = "com.skyy.auctions."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-0.1.14.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "balp7", "ah")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyAuctions")
EXPECT = {"AhCfg": ["+f BLOCK_GATHER", "+f GATHER_IDS", "+f GATHER_REASON", "+f RULES_TEXT", "+m loadRules", "~<clinit>"],
          "AhItem": ["+m isGatherGear", "~m blockedReason", "~m ttMap"],   # ttMap: the TT_SPEC bake now holds tier_tags' newer bucket row (7bfbf658, sort only)
          "AhCmds": ["~m status"], "CfgFn": ["~m opExport"], "CfgRows": ["+f DL2", "~<clinit>", "~m defLines", "~m header"],
          "CfgFile": ["~<clinit>", "~m init"], "SkyyAuctionsPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
FAMS = ("mining_armor", "foraging_armor", "farming_armor", "fishing_armor", "tool", "forever_tool", "can", "harvester")


def loader(jar):
    from jpype import JClass, JArray
    arr = JArray(JClass("java.net.URL"))(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    L = loader(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Itm = J("AhCfg"), J("AhItem")
    want = sorted(set(i for i in TT.ROWS if TT.family(i) in FAMS) | set("Armor_%s_%s" % (t, s) for t in ("Copper", "Iron", "Bronze", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")
                                                                       for s in ("Head", "Chest", "Hands", "Legs")))
    have = [str(x) for x in Cfg.GATHER_IDS]
    K.check(have == want and have == sorted(have), "LIST GATHER_IDS = tools/tier_tags.py gathering families + the vanilla Mining armor, sorted (%d)" % len(have))
    reason = str(Cfg.GATHER_REASON)
    K.check("gathering gear is not for sale" in reason, "LIST the reason says gathering gear is not for sale: %s" % reason)
    blocked = ["Armor_Mining_Lead_Chest", "Armor_Mining_Lumen_Hands", "Armor_Copper_Head", "Armor_Adamantite_Legs", "Armor_Bronze_Chest",
               sorted(i for i in want if i.startswith("Armor_Foraging_"))[0], sorted(i for i in want if i.startswith("Armor_Farming_"))[0],
               sorted(i for i in want if i.startswith("Armor_Fishing_"))[0], "Tool_Pickaxe_Copper", "Tool_Hatchet_Lumen_SkyWynn",
               "Tool_Hatchet_Pickaxe_Multitool_Dusk_SkyWynn", "Tool_WaterCan_Copper", "Tool_Sickle_Harvester_Cobalt"]
    for i in blocked:
        K.check(i in want and str(Itm.blockedReason(i)) == reason, "BLOCK %s refused: %s" % (i, Itm.blockedReason(i)))
    armory = sorted(i for i in TT.ROWS if TT.family(i) == "armory_metal")
    free = ["Weapon_Sword_Iron", "Weapon_Longsword_Adamantite", "Ore_Copper", "Ingredient_Bar_Iron", armory[0], armory[-1]]
    for i in free:
        K.check(Itm.blockedReason(i) is None, "FREE %s lists (a combat item / material): %s" % (i, Itm.blockedReason(i)))
    K.check(str(Itm.blockedReason("Skyy_Sack_Small")) == str(Cfg.BAG_REASON), "BAGS the Magic Bag reason is unchanged")
    Cfg.BLOCK_GATHER = False
    K.check(all(Itm.blockedReason(i) is None for i in blocked), "SWITCH blockGatheringGear off: gathering gear lists again")
    Cfg.BLOCK_GATHER = True
    K.check(not bool(Itm.isGatherGear(None)) and not bool(Itm.isGatherGear("")) and not bool(Itm.isGatherGear("Armor_Mining_")), "LIST null / empty / a prefix is no id")
    # ---- the file
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    d = os.path.join(scratch, "x1", "mods", "Skyy_SkyyAuctions")
    os.makedirs(d, exist_ok=True)
    t = str(Cfg.loadRules(P(d)))
    txt = open(os.path.join(d, "rules.properties"), encoding="latin-1").read()
    K.check(txt == str(Cfg.RULES_TEXT) and "blockGatheringGear=true" in txt and bool(Cfg.BLOCK_GATHER) and "OFF the AH" in t, "FILE fresh: the default file, ON: %s" % t)
    open(os.path.join(d, "rules.properties"), "w", encoding="latin-1").write("blockGatheringGear=false\n")
    Cfg.loadRules(P(d))
    K.check(not bool(Cfg.BLOCK_GATHER), "FILE a typed false is read")
    open(os.path.join(d, "rules.properties"), "w", encoding="latin-1").write("blockGatheringGear=maybe\n")
    Cfg.loadRules(P(d))
    K.check(bool(Cfg.BLOCK_GATHER), "FILE junk = the default (true)")
    os.remove(os.path.join(d, "rules.properties"))
    Cfg.loadRules(P(d))
    # ---- the kit end to end (the row is live)
    CP, Fn = J("CfgPub"), J("CfgFn")
    CP.start(P(os.path.dirname(d)), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyAuctions"))
    r = str(Fn.cmdSetConsole("blockGatheringGear", "false"))
    K.check(not bool(Cfg.BLOCK_GATHER) and Itm.blockedReason("Armor_Mining_Lead_Chest") is None, "KIT the row off applies at once: %s" % r[:60])
    CP.shutdown()
    K.check("blockGatheringGear=false" in open(os.path.join(d, "rules.properties"), encoding="latin-1").read(), "KIT the line is written to rules.properties")
    gen = open(os.path.join(HERE, "build_skyyauctions_%s.py" % VERSION), encoding="utf8").read()
    K.check(gen.index("@PKG@.AhCfg.loadRules(dir);") < gen.index("@PKG@.CfgPub.start(") if "@PKG@.CfgPub.start(" in gen else True, "STATIC rules.properties is read before the kit starts")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Paths = JClass("java.nio.file.Paths")
    P = lambda p_: Paths.get(p_, JArray(JClass("java.lang.String"))([]))
    h0 = HK.tree_hash(home)
    snaps = []
    for start in (1, 2):
        L = loader(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        t = str(J("AhCfg").loadRules(P(home)))
        J("AhSnd").load(P(home))
        J("AhCfg").loadRebirth(P(home))
        J("CfgPub").start(P(os.path.dirname(home)), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyAuctions"))
        K.check(bool(J("AhCfg").BLOCK_GATHER) and "OFF the AH" in t, "D%d the live copy runs with gathering gear off the AH: %s" % (start, t))
        J("CfgPub").shutdown()
        snaps.append(HK.tree_hash(home))
    new = sorted(set(snaps[0]) - set(h0))
    changed = sorted(k for k in h0 if snaps[0].get(k) != h0[k])
    K.check("rules.properties" in new and all(n == "rules.properties" or n.startswith(("config-history", "config-changes")) for n in new) and not changed,
            "D the first start adds rules.properties (+ kit files) only, no existing file changes: new %s changed %s" % (new, changed))
    K.check(snaps[0] == snaps[1], "D the second start changes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAuctions", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyAuctions"))
