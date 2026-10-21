"""SkyySkills 0.4.56 - harness for Skill Trees 3 R3b, the SkyySkills part (tools/skills_0_4_56_patch.py, tools/trees_v3_effects.py).
Build first: python tools/skills_0_4_56_patch.py && python SkyySkills/build_skyyskills_0.4.56.py

    python SkyySkills/test_skyyskills_0.4.56.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.55 -> 0.4.56: + Xp56Mig, SkillV3; only the planned members differ
  XP  EXECUTED SkillBonus.xpBonus / boost (the path every earned XP takes) with a fake SkyyTrees tree:fn:level + skill:bonus sources:
      Combat Insight rank 0 = 0.4.55's numbers; rank 3 = +6 % on EVERY class slot (Archery ... Battlemagic), never on Mining / Alchemy / the
      old Combat slot; clamped to its max 5; xp.combat (SkyyPets Pet Fang) adds to the class slots; bridge.bonus.enabled=false = nothing;
      a bad / throwing answer = 0; the 0..5 clamp holds; Alchemy / Smithing take xp.alchemy / xp.smithing with the 0.4.56 default list and
      did NOT with the 0.4.55 list (the reason for the update); Fishing still takes nothing (not in the list); tree:reads:SkyySkills
  XM  Xp56Mig.plan (old default / with spaces -> the new list; an admin's list kept + INFO; continued entry never rewritten; LAST entry
      decides; marker = run once; CRLF kept; the fresh default file carries the marker) and Xp56Mig.run end to end (History copy, one
      change-log row with Undo, second run nothing, admin value kept, fresh file untouched, no file = nothing)
  LIVE56  every one-time update in setup() order + SkillCfg.load on a scratch COPY of the live data (NewBetaTest), twice: start 1 changes
      only xp.properties (+ History / change log), start 2 changes nothing, player files untouched, the live list reads with Alchemy
  LC / MG  0.4.53's level-cap + 0.4.48's Fm48Mig phases on this jar
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import trees_v3_effects as V3E


def _mod(fn, name):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


T54 = _mod("test_skyyskills_0.4.54.py", "test_skyyskills_0_4_54")
T53, T49, T48 = T54.T53, T54.T49, T54.T48
VERSION = "0.4.56"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.55.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "st3r3b", "sk")))
LIVE_DIR = T54.LIVE_DIR
ADDED = ["Xp56Mig", "SkillV3"]
EXPECT = {"SkillBonus": ["~m xpBonus"],
          "BridgeCfg": ["~m ensureDefaults", "~m read"],          # the DEFAULT_BONUS_XP constant (inlined) = the 0.4.56 list
          "SkillCfg": ["~m load"], "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],
          "SkyySkillsPlugin": ["~m setup", "~m shutdown"], "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"]}
jpath, snapd, boot, fresh_load = T48.jpath, T53.snapd, T53.boot, T53.fresh_load
OLD_XS = "Mining,Foraging,Farming,Cooking"
NEW_XS = "Mining,Foraging,Farming,Cooking,Alchemy,Smithing"
MIGS = T49.OLD_MIGS + ["Zo49Mig", "Fl50Mig", "Mn52Mig", "Nc53Mig", "Fa53Mig", "En54Mig", "Xp56Mig"]


def run_xp(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = boot(K)
    fresh_load(J, Cfg, os.path.join(scratch, "xp"))
    SB, SD, V3, BC, ST = J("SkillBonus"), J("SkillDefs"), J("SkillV3"), J("BridgeCfg"), J("SkillStore")
    br = ST.bridge()
    UUID, HM, CHM, D = JClass("java.util.UUID"), JClass("java.util.HashMap"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.Double")
    u = UUID.fromString("00000000-0000-0000-0000-0000000456a1")
    K.eq(str(BC.BONUS_TEXT), "Mining,Foraging,Farming,Cooking,Alchemy,Smithing", "XP the fresh file's xpSkills = the 0.4.56 list")
    K.eq(str(V3.KEY_CI), V3E.key("Combat", 3, "r5b"), "XP Combat Insight's saved key")
    RANK = {}

    @JImplements("java.util.function.Function")
    class Tr(object):
        @JOverride
        def apply(self, a):
            v = RANK.get(str(a[1]), 0)
            if v == "boom":
                raise RuntimeError("boom")
            return JString(v) if isinstance(v, str) else JObject(v, "java.lang.Integer")
    br.put("tree:fn:level", Tr())
    classes = [int(x) for x in SD.CLASS_SLOT]
    others = [int(SD.MINING), int(SD.ALCHEMY), int(SD.COMBAT), int(SD.FISHING), int(SD.EXPLORATION)]
    base = dict((s, float(SB.xpBonus(u, s))) for s in classes + others)
    K.check(all(v == 0.0 for v in base.values()), "XP rank 0, no sources: every slot 0 (0.4.55): %s" % base)
    RANK[str(V3.KEY_CI)] = 3
    got = dict((s, float(SB.xpBonus(u, s))) for s in classes + others)
    K.check(all(abs(got[s] - 0.06) < 1e-9 for s in classes) and all(got[s] == 0.0 for s in others),
            "XP Combat Insight rank 3 = +6 %% on every class slot, nothing on Mining / Alchemy / the old Combat slot / Fishing / Exploration: %s" % got)
    K.check(int(SB.boost(u, classes[0], 1000)) in (1060,), "XP ... boost() pays 1000 -> 1060 on a class slot")
    RANK[str(V3.KEY_CI)] = 50
    K.check(abs(float(SB.xpBonus(u, classes[1])) - 0.10) < 1e-9, "XP a rank of 50 is clamped to the max 5 (+10 %%)")
    RANK[str(V3.KEY_CI)] = "boom"
    K.eq(float(SB.xpBonus(u, classes[1])), 0.0, "XP a throwing SkyyTrees = rank 0")
    RANK[str(V3.KEY_CI)] = "x"
    K.eq(float(SB.xpBonus(u, classes[1])), 0.0, "XP a non-number = rank 0")
    RANK[str(V3.KEY_CI)] = 1
    src = CHM()
    br.put("skill:bonus:" + str(u), src)
    pets = HM()
    pets.put("xp.combat", D(0.10))
    pets.put("xp.alchemy", D(0.04))
    pets.put("xp.smithing", D(0.06))
    pets.put("xp.fishing", D(0.08))
    src.put("pets", pets)
    K.check(abs(float(SB.xpBonus(u, classes[2])) - 0.12) < 1e-9, "XP xp.combat (Pet Fang) 10 %% + Combat Insight rank 1 2 %% = 12 %% on a class slot: %s" % SB.xpBonus(u, classes[2]))
    K.check(abs(float(SB.xpBonus(u, int(SD.ALCHEMY))) - 0.04) < 1e-9 and abs(float(SB.xpBonus(u, int(SD.SMITHING))) - 0.06) < 1e-9,
            "XP Alchemy / Smithing take xp.alchemy / xp.smithing with the 0.4.56 list")
    K.eq(float(SB.xpBonus(u, int(SD.FISHING))), 0.0, "XP Fishing is not in the list (its XP is all grants) - xp.fishing ignored")
    p = JClass("java.util.Properties")()
    p.setProperty("bridge.bonus.xpSkills", OLD_XS)
    BC.read(p) if hasattr(BC, "read") else None
    if str(BC.BONUS_TEXT) == OLD_XS:
        K.check(float(SB.xpBonus(u, int(SD.ALCHEMY))) == 0.0 and float(SB.xpBonus(u, int(SD.SMITHING))) == 0.0,
                "XP with the 0.4.55 list Alchemy / Smithing take nothing (why Xp56Mig moves the old default)")
        p.setProperty("bridge.bonus.xpSkills", NEW_XS)
        BC.read(p)
    else:
        K.notes.append("XP: BridgeCfg has no read(Properties) - the old-list control is covered by XM (the migrated file reads the new list)")
    BC.BONUS = False
    K.check(float(SB.xpBonus(u, classes[2])) == 0.0, "XP bridge.bonus.enabled=false: no Combat Insight, no xp.combat")
    BC.BONUS = True
    pets.put("xp.combat", D(40.0))
    K.eq(float(SB.xpBonus(u, classes[2])), 5.0, "XP the 0..5 clamp holds")
    pets.put("xp.combat", D(-1.0))
    K.eq(float(SB.xpBonus(u, classes[2])), 0.0, "XP a big debuff never goes below 0")
    V3.reads(True)
    K.eq(str(br.get("tree:reads:SkyySkills")), V3E.reads_csv("SkyySkills"), "XP tree:reads:SkyySkills = Combat Insight + Alchemy.PWisdom")
    br.put("tree:reads:SkyySkills", "x")
    V3.reads(False)
    K.eq(str(br.get("tree:reads:SkyySkills")), "x", "XP shutdown removes only our own value")
    br.put("tree:reads:SkyySkills", V3.READS)
    V3.reads(False)
    K.check(br.get("tree:reads:SkyySkills") is None, "XP ... ours goes")
    br.remove("tree:fn:level")
    K.eq(int(V3.rank(u, V3.KEY_CI, 5)), 0, "XP no SkyyTrees = rank 0")
    K.save()


def run_xm(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J, Cfg = boot(K)
    M, Hist, CLog, Rows = J("Xp56Mig"), J("CfgHist"), J("CfgLog"), J("CfgRows")
    S = lambda x: JString(x)
    MARK = str(M.MARK)
    K = K
    for old in (OLD_XS, OLD_XS.replace(",", ", ")):
        t1 = "a=1\nbridge.bonus.xpSkills=%s\nbridge.bonus.addxpSkills=Cooking\n" % old
        r = M.plan(S(t1))
        body = str(r[0])
        K.check(body == "a=1\nbridge.bonus.xpSkills=%s\nbridge.bonus.addxpSkills=Cooking\n" % NEW_XS + MARK + "\n", "XM plan: untouched %r -> the 0.4.56 list, marker at the end" % old)
        K.eq([str(x) for x in r[1]], ["bridge.bonus.xpSkills", old, NEW_XS], "XM plan: the change-log row (%r)" % old)
        K.check(bool(M.sameAfter(JString(t1).getBytes("ISO-8859-1"), JString(body).getBytes("ISO-8859-1"), r[2])), "XM sameAfter accepts the plan")
    K.check(not bool(M.sameAfter(JString(t1).getBytes("ISO-8859-1"), JString(body.replace("a=1", "a=2")).getBytes("ISO-8859-1"), r[2])), "XM sameAfter refuses another changed key (control)")
    r = M.plan(S("bridge.bonus.xpSkills=Mining,Farming\n"))
    K.check(str(r[0]) == "bridge.bonus.xpSkills=Mining,Farming\n" + MARK + "\n" and len(r[1]) == 0 and "kept" in str(r[3]), "XM plan: an admin's list kept (INFO): %s" % str(r[3]))
    r = M.plan(S("a=1\n"))
    K.check(str(r[0]) == "a=1\n" + MARK + "\n" and len(r[1]) == 0, "XM plan: no line -> only the marker")
    K.check(M.plan(S("a=1\n" + MARK + "\nbridge.bonus.xpSkills=%s\n" % OLD_XS)) is None, "XM plan: the marker -> nothing again (run once)")
    r = M.plan(S("x=1\r\nbridge.bonus.xpSkills=%s\r\n" % OLD_XS))
    K.check(str(r[0]) == "x=1\r\nbridge.bonus.xpSkills=%s\r\n" % NEW_XS + MARK + "\r\n", "XM plan: a CRLF file keeps CRLF")
    r = M.plan(S("bridge.bonus.xpSkills=Mining,\\\nForaging,Farming,Cooking\n"))
    K.check(len(r[1]) == 0, "XM plan: a continued entry is never rewritten")
    r = M.plan(S("bridge.bonus.xpSkills=%s\nbridge.bonus.xpSkills=Mining\n" % OLD_XS))
    K.check(len(r[1]) == 0, "XM plan: the LAST entry decides")
    K.check(str(Cfg.DEFAULTS).count(str(M.MARK_ID)) == 1 and M.plan(Cfg.DEFAULTS) is None, "XM plan: the fresh default file carries the marker -> never migrated")

    def start(d):
        Cfg.FILE = jpath(os.path.join(d, "xp.properties"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        return str(M.run())
    base = os.path.join(scratch, "xm")
    old_txt = str(Cfg.DEFAULTS).replace(MARK + "\n", "").replace("bridge.bonus.xpSkills=%s\n" % NEW_XS, "bridge.bonus.xpSkills=%s\n" % OLD_XS)
    assert old_txt.count("bridge.bonus.xpSkills=%s\n" % OLD_XS) == 1 and str(M.MARK_ID) not in old_txt
    for tag, txt, nl in (("lf", old_txt, "\n"), ("crlf", old_txt.replace("\n", "\r\n"), "\r\n")):
        d = os.path.join(base, tag)
        os.makedirs(d)
        open(os.path.join(d, "xp.properties"), "wb").write(txt.encode("latin-1"))
        s0 = snapd(d)
        r1 = start(d)
        s1 = snapd(d)
        new = s1["xp.properties"].decode("latin-1")
        K.check(new == txt.replace("bridge.bonus.xpSkills=%s%s" % (OLD_XS, nl), "bridge.bonus.xpSkills=%s%s" % (NEW_XS, nl)) + MARK + nl,
                "XM run %s: the list + the marker, every other byte kept" % tag)
        hist = [k for k in s1 if k.startswith("config-history/") and s1[k] == s0["xp.properties"]]
        K.check(len(hist) == 1, "XM run %s: the old file is in config-history (%s)" % (tag, hist))
        lg = s1.get("config-changes.log", b"").decode("latin-1")
        K.check(lg.count("bridge.bonus.xpSkills") == 1 and "SkyySkills 0.4.56" in lg, "XM run %s: one config-changes.log row: %r" % (tag, lg.strip()[-200:]))
        K.check("Undo" in r1 and "0.4.56" in r1, "XM run %s: the INFO line: %s" % (tag, r1[:200]))
        r2 = start(d)
        K.check(r2 == "" and snapd(d) == s1, "XM run %s: a second start changes nothing" % tag)
        fresh_load(J, Cfg, d)
        K.eq(str(J("BridgeCfg").BONUS_TEXT), NEW_XS, "XM run %s: the migrated file loads the 0.4.56 list" % tag)
    d = os.path.join(base, "hand")
    os.makedirs(d)
    ht = old_txt.replace("bridge.bonus.xpSkills=%s\n" % OLD_XS, "bridge.bonus.xpSkills=Mining\n")
    open(os.path.join(d, "xp.properties"), "wb").write(ht.encode("latin-1"))
    r1 = start(d)
    s1 = snapd(d)
    K.check(s1["xp.properties"].decode("latin-1") == ht + MARK + "\n" and "kept" in r1 and "bridge.bonus.xpSkills" not in s1.get("config-changes.log", b"").decode("latin-1"),
            "XM run hand: an admin's list kept, only the marker, no change-log row: %s" % r1[:200])
    d = os.path.join(base, "fresh")
    os.makedirs(d)
    open(os.path.join(d, "xp.properties"), "wb").write(str(Cfg.DEFAULTS).encode("latin-1"))
    s0 = snapd(d)
    K.check(start(d) == "" and snapd(d) == s0, "XM run fresh: a fresh default file is untouched")
    d = os.path.join(base, "none")
    os.makedirs(d)
    K.check(start(d) == "" and snapd(d) == {}, "XM run none: no xp.properties -> nothing")
    K.save()


def run_live56(out, jar, scratch, home):
    import shutil
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    lc = os.path.join(os.path.dirname(home), "copy56")
    shutil.copytree(home, lc)
    L = T48.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, LF, BC = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("LvFloor"), J("BridgeCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")

    def start():
        Cfg.FILE = jpath(os.path.join(lc, "xp.properties"))
        Sto.DATA.clear()
        Sto.DIR = jpath(os.path.join(lc, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        LF.NEW_FARM = False
        r = dict((nm, str(J(nm).run())) for nm in MIGS)
        r["load"] = str(Cfg.load())
        return r
    s0 = snapd(lc)
    r1 = start()
    s1 = snapd(lc)
    lst = str(BC.BONUS_TEXT)
    r2 = start()
    s2 = snapd(lc)
    K.notes.append("LIVE56: Xp56Mig: %s | the list now %s" % (r1.get("Xp56Mig", "")[:300], lst))
    ch = sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))
    K.check(all(k == "xp.properties" or k == "config-changes.log" or k.startswith("config-history/") for k in ch), "LIVE56: start 1 changes only xp.properties / History / change log: %s" % ch)
    xp0 = s0.get("xp.properties", b"").decode("latin-1")
    K.check(lst == NEW_XS or ("bridge.bonus.xpSkills=%s" % OLD_XS) not in xp0, "LIVE56: the live copy reads the 0.4.56 list (or an admin's own): %s" % lst)
    K.check(all(s1.get(k) == s2.get(k) for k in set(s1) | set(s2)) and r2.get("Xp56Mig") == "", "LIVE56: start 2 changes nothing")
    K.check(all(s0.get(k) == s1.get(k) for k in s0 if k.startswith("players/")), "LIVE56: player files untouched")
    K.save()


if __name__ == "__main__":
    phases = [("xp", run_xp), ("xm", run_xm), ("live56", run_live56), ("lc", T53.run_lc), ("mg", T48.run_mg)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
