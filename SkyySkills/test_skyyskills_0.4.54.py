"""SkyySkills 0.4.54 - harness for the ENCHANTED ALLOY SMITHING XP ROWS (tools/skills_0_4_54_patch.py).
Build first: python tools/skills_0_4_54_patch.py && python SkyySkills/build_skyyskills_0.4.54.py

    python SkyySkills/test_skyyskills_0.4.54.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.53 -> 0.4.54: + En54Mig; only the planned members differ
  MG / ZO / FL / LIVE50 / MN / LIVE52 / LC / FA  the 0.4.48 - 0.4.53 phases on this jar. LIVE53 is left out: the live data now HAS
      level-floors.properties (0.4.53 is deployed), so its "written once" check cannot hold any more (LIVE54 runs every update incl. Nc53 /
      Fa53 on the live copy). NC (0.4.53) is left out: its one check
      "Enchanted alloy -> smithing.smeltDefault once" is replaced by design (EN below re-runs every NC alloy check with the new rule); no
      other class NC covers changed (compare phase)
  EN  the 6 rows: default file + marker, SmithCfg loaded values, RecipeXp.classify - each SkyyAlloy Enchanted smelt pays its row once (NOT
      smeltDefault), the plain alloy / Furnace / Workbench controls; an OLD file without the lines still pays them (defaults map); an admin's
      own value wins; En54Mig plan + run (LF / CRLF, admin line kept, marker, History, second run nothing, fresh file untouched, no file)
  LIVE54  every one-time update in setup() order on a scratch COPY of the live data, twice
  PK / PG  0.4.47's asset-pack + page phases on this jar (skip with --no-old)
  AA  engine-access audit
NOT COVERED: SkyySacks' real /craft Furnace call (skill:fn:craftxp -> the same RecipeXp.classify), the feel in game.
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK


def _mod(fn, name):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


T53 = _mod("test_skyyskills_0.4.53.py", "test_skyyskills_0_4_53")
T52, T50, T49, T48 = T53.T52, T53.T50, T53.T49, T53.T48
VERSION = "0.4.54"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.53.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "s454", "h")))
LIVE_DIR = T53.LIVE_DIR
ADDED = ["En54Mig"]
EXPECT = {"SmithCfg": ["~m defaultsMap", "~m ensureDefaults"],   # the 6 rows in the defaults map + the Smithing section literal
          "SkillCfg": ["~m load"], "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],   # the default file text / version texts
          "SkyySkillsPlugin": ["~m setup"], "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"]}   # En54Mig.run in setup; version texts
jpath, snapd, boot, fresh_load = T48.jpath, T53.snapd, T53.boot, T53.fresh_load
EN = [("Skyy_Ench_Bronze", 800), ("Skyy_Ench_Dusk", 2250), ("Skyy_Ench_Azurvane", 1900), ("Skyy_Ench_Cinder", 3750),
      ("Skyy_Ench_Lumen", 3150), ("Skyy_Ench_Electrum", 1400)]
BAR = {"Bronze": 16, "Dusk": 45, "Azurvane": 38, "Cinder": 75, "Lumen": 63, "Electrum": 28}
assert all(x == BAR[i[len("Skyy_Ench_"):]] * 100 // 2 for i, x in EN)   # 100 bars x bar XP x 0.5


# ============================================================================================ EN: the Enchanted alloy rows + En54Mig
def run_en(out, jar, scratch, _home):
    from jpype import JClass, JString, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = boot(K)
    S = lambda x: JString(x)
    M = J("En54Mig")
    D = str(Cfg.DEFAULTS)
    for i, x in EN:
        K.check(("\nsmithing.xp.%s=%d\n" % (i, x)) in ("\n" + D) and ("\n" + D).count("\nsmithing.xp.%s=" % i) == 1, "EN default file: smithing.xp.%s=%d" % (i, x))
    K.check(D.count(str(M.MARK_ID)) == 1 and M.plan(S(D)) is None, "EN the default file carries the En54Mig marker -> never migrated")
    K.eq([str(k) for k in M.KEYS], ["smithing.xp." + i for i, x in EN], "EN En54Mig.KEYS")
    K.eq([str(v) for v in M.VALS], [str(x) for i, x in EN], "EN En54Mig.VALS")
    fresh_load(J, Cfg, os.path.join(scratch, "en", "fresh"))
    SC, SD = J("SmithCfg"), J("SkillDefs")
    for i, x in EN:
        K.check(int(SC.forOutput(i)) == x, "EN loaded: SmithCfg.forOutput(%s) = %d (got %s)" % (i, x, SC.forOutput(i)))
    # ---- RecipeXp.classify: each Enchanted alloy smelt pays its row once, not smithing.smeltDefault
    try:
        MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
        BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
        BT = JClass("com.hypixel.hytale.protocol.BenchType")
        CR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
        RX = J("RecipeXp")

        def rec(bench, out_id, qty, a="Skyy_Ench_Thorium", b="Skyy_Ench_Lead"):
            po = MQ(out_id, None, None, qty, None)
            ins = JArray(MQ)([MQ(a, None, None, 1, None), MQ(b, None, None, 1, None)])
            br = JArray(BR)([BR(BT.Processing, bench, None, 1, None)])
            return CR(ins, po, JArray(MQ)([po]), qty, br, 5.0, False, 0)
        dflt = int(SC.DEFAULT)
        for i, x in EN:
            r = RX.classify(rec("SkyyAlloy", i, 2))
            K.check(r is not None and int(r[0]) == int(SD.SMITHING) and int(r[1]) == x and x != dflt,
                    "EN SkyyAlloy %s smelt (2 out) pays its row %d once, not smeltDefault %d: %s" % (i, x, dflt, list(r) if r is not None else None))
        r = RX.classify(rec("SkyyAlloy", "Ingredient_Bar_Dusk_SkyWynn", 2, "Ingredient_Bar_Thorium", "Ingredient_Bar_Lead_SkyWynn"))
        K.check(r is not None and int(r[1]) == 45, "EN control: a plain Dusk smelt still pays 45 once")
        r = RX.classify(rec("SkyyAlloy", "Ingredient_Bar_Bronze", 2, "Ingredient_Bar_Copper", "Ingredient_Bar_Iron"))
        K.check(r is not None and int(r[1]) == 16, "EN control: a plain Bronze smelt still pays 16 once")
        r = RX.classify(rec("Furnace", "Ingredient_Bar_Dusk_SkyWynn", 2))
        K.check(r is not None and int(r[1]) == 90, "EN control: a Furnace recipe with 2 out still pays per bar (90)")
        r = RX.classify(rec("Workbench", "Skyy_Ench_Dusk", 2))
        K.check(r is None, "EN control: a Workbench recipe (compressing) pays no Smithing")
        r = RX.classify(rec("SkyyAlloy", "Skyy_Ench_Iron", 2))
        K.check(r is not None and int(r[1]) == dflt, "EN control: an unlisted SkyyAlloy output still pays smeltDefault (%s)" % (list(r) if r is not None else None))
        # an OLD file (no Enchanted lines, no marker) still pays the rows: SmithCfg.defaultsMap
        P = JClass("java.util.Properties")()
        P.setProperty("smithing.xp.Ingredient_Bar_Iron", "8")
        SC.read(P)
        K.check(all(int(SC.forOutput(i)) == x for i, x in EN), "EN an old file without the lines pays the rows (defaults map)")
        P.setProperty("smithing.xp.Skyy_Ench_Dusk", "5")
        SC.read(P)
        r = RX.classify(rec("SkyyAlloy", "Skyy_Ench_Dusk", 2))
        K.check(r is not None and int(r[1]) == 5, "EN an admin's smithing.xp.Skyy_Ench_Dusk=5 wins")
        P.setProperty("smithing.xp.Skyy_Ench_Dusk", "0")
        SC.read(P)
        K.check(RX.classify(rec("SkyyAlloy", "Skyy_Ench_Dusk", 2)) is None, "EN an admin's 0 = no Smithing XP for that alloy")
    except Exception as e:
        K.check(False, "EN classify: could not build a CraftingRecipe: %s" % e)
    # ---- En54Mig plan
    head = str(M.HEAD)
    block = head + "".join("smithing.xp.%s=%d\n" % (i, x) for i, x in EN)
    old = "a=1\nsmithing.xp.Ingredient_Bar_Iron=8\n"
    r = M.plan(S(old))
    K.check(str(r[0]) == old + "\n" + block and list(r[1]) == ["smithing.xp." + i for i, x in EN], "EN plan: the block (head + 6 rows) after a blank line: %r" % str(r[0])[-200:])
    K.check(bool(M.sameAfter(S(old).getBytes("ISO-8859-1"), S(str(r[0])).getBytes("ISO-8859-1"), r[1])), "EN sameAfter accepts the plan")
    K.check(not bool(M.sameAfter(S(old).getBytes("ISO-8859-1"), S(str(r[0]).replace("a=1", "a=2")).getBytes("ISO-8859-1"), r[1])), "EN sameAfter refuses another change")
    r = M.plan(S(old.replace("\n", "\r\n")))
    K.check(str(r[0]) == (old + "\n" + block).replace("\n", "\r\n"), "EN plan: CRLF kept")
    hand = old + "smithing.xp.Skyy_Ench_Cinder = 7\n"
    r = M.plan(S(hand))
    K.check(len(r[1]) == 5 and "smithing.xp.Skyy_Ench_Cinder" not in list(r[1]) and str(r[0]).count("Skyy_Ench_Cinder") == 1 and "smithing.xp.Skyy_Ench_Cinder = 7\n" in str(r[0]),
            "EN plan: an admin's own Cinder line is kept, never doubled (5 lines added)")
    K.check(M.plan(S(old + "# " + str(M.MARK_ID) + "\n")) is None, "EN plan: the marker -> nothing (run once)")
    Hist, Rows, CLog = J("CfgHist"), J("CfgRows"), J("CfgLog")

    def start(d):
        Cfg.FILE = jpath(os.path.join(d, "xp.properties"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        return str(M.run())
    for tag, txt in (("lf", old), ("crlf", old.replace("\n", "\r\n"))):
        d = os.path.join(scratch, "en", tag)
        os.makedirs(d)
        open(os.path.join(d, "xp.properties"), "wb").write(txt.encode("latin-1"))
        s0 = snapd(d)
        r1 = start(d)
        s1 = snapd(d)
        nl = "\r\n" if tag == "crlf" else "\n"
        K.check(s1["xp.properties"].decode("latin-1") == (old + "\n" + block).replace("\n", nl), "EN run %s: the file = the plan" % tag)
        K.check(any(k.startswith("config-history/") and v == s0["xp.properties"] for k, v in s1.items()), "EN run %s: the old file is in config-history" % tag)
        K.check("0.4.54" in r1 and "added 6" in r1, "EN run %s: the INFO line: %s" % (tag, r1[:160]))
        K.check(start(d) == "" and snapd(d) == s1, "EN run %s: a second start changes nothing" % tag)
    d = os.path.join(scratch, "en", "fresh2")
    os.makedirs(d)
    open(os.path.join(d, "xp.properties"), "wb").write(D.encode("latin-1"))
    s0 = snapd(d)
    K.check(start(d) == "" and snapd(d) == s0, "EN run fresh: a fresh default file is untouched")
    d = os.path.join(scratch, "en", "none")
    os.makedirs(d)
    K.check(start(d) == "" and snapd(d) == {}, "EN run none: no file -> nothing")
    K.save()


# ============================================================================================ LIVE54: every update in setup() order on a COPY of the live data
def run_live54(out, jar, scratch, home):
    import shutil
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    lc = os.path.join(os.path.dirname(home), "copy54")
    shutil.copytree(home, lc)
    L = T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, LF, SC = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("LvFloor"), J("SmithCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    migs = T49.OLD_MIGS + ["Zo49Mig", "Fl50Mig", "Mn52Mig", "Nc53Mig", "Fa53Mig", "En54Mig"]

    def start():
        Cfg.FILE = jpath(os.path.join(lc, "xp.properties"))
        Sto.DATA.clear()
        Sto.DIR = jpath(os.path.join(lc, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        LF.NEW_FARM = False
        r = dict((nm, str(J(nm).run())) for nm in migs)
        r["load"] = str(Cfg.load())
        return r
    s0 = snapd(lc)
    r1 = start()
    s1 = snapd(lc)
    vals = [int(SC.forOutput(i)) for i, x in EN]
    r2 = start()
    s2 = snapd(lc)
    K.notes.append("LIVE54: En54Mig: %s | Enchanted alloy rows now %s" % (r1.get("En54Mig", "")[:300], vals))
    xp0 = s0.get("xp.properties", b"").decode("latin-1").replace("\r", "")
    xp1 = s1["xp.properties"].decode("latin-1").replace("\r", "")
    for i, x in EN:
        k = "smithing.xp." + i
        had = [ln for ln in xp0.split("\n") if ln.split("=", 1)[0].strip() == k]
        now = [ln for ln in xp1.split("\n") if ln.split("=", 1)[0].strip() == k]
        K.check(len(now) == 1 and (had == now if had else now[0] == "%s=%d" % (k, x)), "LIVE54: %s present once (%s)" % (k, now))
    K.check(vals == [x for i, x in EN] or "smithing.xp.Skyy_Ench" in xp0, "LIVE54: the rows load: %s" % vals)
    K.check(all(s1.get(k) == s2.get(k) for k in set(s1) | set(s2)) and r2.get("En54Mig") == "", "LIVE54: start 2 changes nothing")
    K.check(all(s0.get(k) == s1.get(k) for k in s0 if k.startswith("players/")), "LIVE54: player files untouched")
    K.save()


if __name__ == "__main__":
    phases = [("mg", T48.run_mg), ("zo", T49.run_zo), ("fl", T50.run_fl), ("live50", T50.run_live50),
              ("mn", T52.run_mn), ("live52", T52.run_live52), ("lc", T53.run_lc), ("fa", T53.run_fa),
              ("en", run_en), ("live54", run_live54)]
    if "--no-old" not in sys.argv:
        T47 = _mod("test_skyyskills_0.4.47.py", "test_skyyskills_0_4_47")
        phases += [("pack", T47.T46.run_pack), ("pages", T47.run_pages)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
