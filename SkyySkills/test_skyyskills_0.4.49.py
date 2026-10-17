"""SkyySkills 0.4.49 - harness for round ores01, the SkyySkills part: Mining XP for the zone ores + Smithing XP for their ingots and the
alloys (tools/skills_0_4_49_patch.py). Build first: python tools/skills_0_4_49_patch.py && python SkyySkills/build_skyyskills_0.4.49.py

    python SkyySkills/test_skyyskills_0.4.49.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.48 -> 0.4.49: + Zo49Mig; only the planned members (the default file text, the version texts, setup)
  FO / MG  0.4.48's Fortune maths + Fm48Mig phases unchanged on this jar
  ZO  the default file (13 lines in their sections + the marker, XP as the spec's table, alloy = (A + B) x 1.25), Zo49Mig.plan (all keys
      missing -> one block; one key present -> kept, 12 added; the marker -> nothing; CRLF kept; continued last line) and Zo49Mig.run end
      to end on scratch files (History copy, marker, second run nothing, fresh default file untouched, no file -> nothing); the rules
      read back: SkillCfg.resolve of an ore block / raw ore = Mining XP, SmithCfg.forOutput of the ingots + alloys
  LIVE49  every one-time update in setup() order + SkillCfg.load, twice, 0.4.48 vs 0.4.49, each on its own scratch COPY of the live data
  PK / PG  0.4.47's asset-pack + page phases on this jar (skip with --no-old)
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

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


T48 = _mod("test_skyyskills_0.4.48.py", "test_skyyskills_0_4_48")
VERSION = "0.4.49"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.48.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "ores-b5", "sk")))
LIVE_DIR = T48.LIVE_DIR
ADDED = ["Zo49Mig"]
EXPECT = {"SkillCfg": ["~m load"], "SmithCfg": ["~m defaultsMap", "~m ensureDefaults"], "CfgRows": ["~<clinit>", "~m header"],
          "CfgFn": ["~m opExport"], "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"], "SkyySkillsPlugin": ["~m setup"]}
OLD_MIGS = T48.OLD_MIGS + ["Fm48Mig"]
MINING = {"Lead": 18, "Chromium": 15, "Slag": 30, "Titanium": 25}
SMITH = {"Ingredient_Bar_Lead_SkyWynn": 18, "Ingredient_Bar_Chromium_SkyWynn": 15, "Ingredient_Bar_Slag_SkyWynn": 30, "Ingredient_Bar_Titanium_SkyWynn": 25,
         "Ingredient_Bar_Bronze": 16, "Ingredient_Bar_Dusk_SkyWynn": 45, "Ingredient_Bar_Azurvane_SkyWynn": 38, "Ingredient_Bar_Cinder_SkyWynn": 75,
         "Ingredient_Bar_Lumen_SkyWynn": 63, "Ingredient_Bar_Electrum_SkyWynn": 28}
LINES = [("prefix.Ore_%s" % k, "Mining:%d" % x) for k, x in MINING.items()] + [("smithing.xp.%s" % i, str(x)) for i, x in SMITH.items()]
jpath, loader_for = T48.jpath, T48.loader_for


# ============================================================================================ ZO: the default file + Zo49Mig
def run_zo(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    M, Cfg, Hist, CLog, Rows, SC = J("Zo49Mig"), J("SkillCfg"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("SmithCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    S = lambda x: JString(x)
    D = str(Cfg.DEFAULTS)
    MARK_ID = str(M.MARK_ID)
    # ---- the numbers of the spec (section 3 table): alloy XP = (A + B) x 1.25, rounded half up
    base = {"Copper": 5, "Iron": 8, "Thorium": 18, "Cobalt": 15, "Adamantite": 30, "Mithril": 25, "Gold": 12, "Silver": 10, "Lead": 18, "Chromium": 15, "Slag": 30, "Titanium": 25}
    for nm, a, b in (("Bronze", "Copper", "Iron"), ("Dusk", "Thorium", "Lead"), ("Azurvane", "Cobalt", "Chromium"), ("Cinder", "Adamantite", "Slag"), ("Lumen", "Mithril", "Titanium"), ("Electrum", "Gold", "Silver")):
        iid = "Ingredient_Bar_Bronze" if nm == "Bronze" else "Ingredient_Bar_%s_SkyWynn" % nm
        K.eq(SMITH[iid], int((base[a] + base[b]) * 1.25 + 0.5), "ZO alloy %s XP = (%s + %s) x 1.25" % (nm, a, b))
    for k, x in MINING.items():
        K.check(x == {"Lead": base["Thorium"], "Chromium": base["Cobalt"], "Slag": base["Adamantite"], "Titanium": base["Mithril"]}[k], "ZO %s Mining XP = its zone partner's" % k)
    # ---- the fresh default file
    for k, v in LINES:
        K.check(("\n" + k + "=" + v + "\n") in ("\n" + D), "ZO default file: %s=%s" % (k, v))
    K.check(D.count(MARK_ID) == 1 and M.plan(S(D)) is None, "ZO default file: carries the Zo49Mig marker once -> never migrated")
    # the rows sit in their sections (Mining prefixes after the Onyxium / Prisma ones; Smithing right with the other bars)
    K.check(D.index("prefix.Ore_Prisma=") < D.index("prefix.Ore_Lead=") < D.index("# ---------- Foraging"), "ZO default file: the Mining rows sit in the Mining section")
    K.check(D.index("smithing.xp.Ingredient_Bar_Prisma=") < D.index("smithing.xp.Ingredient_Bar_Lead_SkyWynn="), "ZO default file: the Smithing rows follow the other bars")
    # ---- plan (pure)
    old_txt = "a=1\nprefix.Ore_=Mining:5\nsmithing.oreFactor=1.0\n"
    r = M.plan(S(old_txt))
    body, added = str(r[0]), [str(x) for x in r[1]]
    want = old_txt + "\n" + str(M.HEAD) + "".join("%s=%s\n" % kv for kv in LINES)
    K.check(body == want, "ZO plan: one block after the last line (blank line, header + marker, the 14 lines): %r" % body[len(old_txt):len(old_txt) + 120])
    K.eq(added, [k for k, v in LINES], "ZO plan: the 14 added keys")
    K.check(bool(M.sameAfter(S(old_txt).getBytes("ISO-8859-1"), S(body).getBytes("ISO-8859-1"), r[1])), "ZO sameAfter accepts the plan")
    K.check(not bool(M.sameAfter(S(old_txt).getBytes("ISO-8859-1"), S(body.replace("a=1", "a=2")).getBytes("ISO-8859-1"), r[1])), "ZO sameAfter refuses another changed key (control)")
    K.check(not bool(M.sameAfter(S(old_txt).getBytes("ISO-8859-1"), S(body.replace("Mining:18", "Mining:19")).getBytes("ISO-8859-1"), r[1])), "ZO sameAfter refuses a changed new value (control)")
    ht = old_txt + "smithing.xp.Ingredient_Bar_Bronze=40\nprefix.Ore_Slag=Mining:99\n"
    r = M.plan(S(ht))
    b2 = str(r[0])
    K.check(len(r[1]) == 12 and b2.startswith(ht) and b2.count("smithing.xp.Ingredient_Bar_Bronze=") == 1 and b2.count("prefix.Ore_Slag=") == 1
            and "Mining:30" not in b2, "ZO plan: an admin's own Bronze 40 / Slag 99 lines are kept, not doubled (12 added)")
    r = M.plan(S("".join("%s=%s\n" % kv for kv in LINES)))
    K.check(len(r[1]) == 0 and str(r[0]).endswith(str(M.HEAD)), "ZO plan: every line already there -> only the header + marker")
    K.check(M.plan(S("a=1\n# " + MARK_ID + " x\n")) is None, "ZO plan: a comment holding the marker -> nothing (run once)")
    r = M.plan(S("x=1\r\ny=2\r\n"))
    K.check("\n" not in str(r[0]).replace("\r\n", "") and str(r[0]).startswith("x=1\r\ny=2\r\n\r\n"), "ZO plan: a CRLF file keeps CRLF only")
    r = M.plan(S("x=1\ny=2"))
    K.check(str(r[0]).startswith("x=1\ny=2\n\n"), "ZO plan: no final newline -> a blank line is added first")
    r = M.plan(S("x=1\ny=2\\\n"))
    K.check(str(r[0]).startswith("x=1\ny=2\\\n\n\n"), "ZO plan: a last line ending in a backslash is not continued into the block")
    # ---- run, end to end (scratch files)
    def start(d):
        Cfg.FILE = jpath(os.path.join(d, "xp.properties"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        return str(M.run())

    def snap(d):
        return dict((os.path.relpath(os.path.join(r_, fn), d).replace(os.sep, "/"), open(os.path.join(r_, fn), "rb").read())
                    for r_, ds, fs in os.walk(d) for fn in fs)
    base_d = os.path.join(scratch, "zo")
    stripped = D
    for k, v in LINES:
        stripped = stripped.replace(k + "=" + v + "\n", "")
    stripped = "".join(ln for ln in stripped.splitlines(True) if MARK_ID not in ln)
    assert MARK_ID not in stripped and all(k + "=" not in stripped for k, v in LINES)
    for tag, txt, nl in (("lf", stripped, "\n"), ("crlf", stripped.replace("\n", "\r\n"), "\r\n")):
        d = os.path.join(base_d, tag)
        os.makedirs(d)
        open(os.path.join(d, "xp.properties"), "wb").write(txt.encode("latin-1"))
        s0 = snap(d)
        r1 = start(d)
        s1 = snap(d)
        new = s1["xp.properties"].decode("latin-1")
        tail = (nl + str(M.HEAD).replace("\n", nl) + "".join("%s=%s%s" % (k, v, nl) for k, v in LINES))
        K.check(new == txt + tail, "ZO run %s: the old file + ONE block, every other byte kept" % tag)
        hist = [k for k in s1 if k.startswith("config-history/") and s1[k] == s0["xp.properties"]]
        K.check(len(hist) == 1, "ZO run %s: the old file is in config-history (%s)" % (tag, hist))
        K.check("added 14 line(s)" in r1 and "config-history" in r1, "ZO run %s: the INFO line: %s" % (tag, r1[:160]))
        r2 = start(d)
        s2 = snap(d)
        K.check(r2 == "" and s2 == s1, "ZO run %s: a second start changes nothing" % tag)
        # the rules read back
        p = JClass("java.util.Properties")()
        p.load(JClass("java.io.StringReader")(new))
        Cfg.FILE = jpath(os.path.join(d, "xp.properties"))
        Cfg.load()
        for k, x in MINING.items():
            for iid in ("Ore_%s_SkyWynn" % k, "Ore_%s_Sandstone_SkyWynn" % k, "Ore_%s_Shale_SkyWynn" % k, "Ore_%s_Volcanic_SkyWynn" % k, "Ore_%s_Basalt_SkyWynn" % k):
                rl = Cfg.resolve(S(iid))
                K.check(rl is not None and int(rl[0]) == int(J("SkillDefs").MINING) and int(rl[1]) == x, "ZO run %s: %s pays Mining %d (got %s)" % (tag, iid, x, None if rl is None else (int(rl[0]), int(rl[1]))))
        rl = Cfg.resolve(S("Ore_Iron_Stone"))
        K.check(rl is not None and int(rl[1]) == 8, "ZO run %s: a vanilla ore block still pays its own XP (Iron 8)" % tag)
        for iid, x in SMITH.items():
            K.eq(int(SC.forOutput(S(iid))), x, "ZO run %s: SmithCfg.forOutput(%s)" % (tag, iid))
    d = os.path.join(base_d, "hand")
    os.makedirs(d)
    open(os.path.join(d, "xp.properties"), "wb").write(ht.encode("latin-1"))
    r1 = start(d)
    s1 = snap(d)
    K.check(s1["xp.properties"].decode("latin-1").startswith(ht) and s1["xp.properties"].decode("latin-1").count("prefix.Ore_Slag=") == 1 and "added 12 line(s)" in r1,
            "ZO run hand: an admin's two lines kept untouched, 11 added: %s" % r1[:120])
    d = os.path.join(base_d, "fresh")
    os.makedirs(d)
    open(os.path.join(d, "xp.properties"), "wb").write(D.encode("latin-1"))
    s0 = snap(d)
    K.check(start(d) == "" and snap(d) == s0, "ZO run fresh: a fresh default file is untouched")
    d = os.path.join(base_d, "none")
    os.makedirs(d)
    K.check(start(d) == "" and snap(d) == {}, "ZO run none: no xp.properties -> nothing")
    K.save()


# ============================================================================================ LIVE49: start twice on a scratch COPY of the live data
def run_live49(out, jar, scratch, home):
    import shutil
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    res = {}
    lc_root = os.path.dirname(home)

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)
    for tag, jr, mg in (("old", OLD_JAR, OLD_MIGS), ("new", jar, OLD_MIGS + ["Zo49Mig"])):
        lc = os.path.join(lc_root, "copy49-" + tag)
        shutil.copytree(home, lc)
        L = loader_for(jr)
        J = lambda n: JClass(PKG + n, loader=L)
        Cfg, Sto, Hist, CLog, Rows = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows")
        Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")

        def start():
            Cfg.FILE = jpath(os.path.join(lc, "xp.properties"))
            Sto.DATA.clear()
            Sto.DIRTY.clear()
            Sto.DIR = jpath(os.path.join(lc, "players"))
            Hist.DIR = None
            Rows.HOME = None
            CLog.FILE = None
            CLog.Q.clear()
            r = {}
            for nm in mg:
                r[nm] = str(J(nm).run())
            r["load"] = str(Cfg.load())
            return r
        s0 = snap(lc)
        r1 = start()
        s1 = snap(lc)
        r2 = start()
        s2 = snap(lc)
        rs = {}
        if tag == "new":
            for k, x in MINING.items():
                q = Cfg.resolve("Ore_%s_Sandstone_SkyWynn" % k) if hasattr(Cfg, "resolve") else None
                rs[k] = None if q is None else int(q[1])
            rs["smith"] = dict((i, int(J("SmithCfg").forOutput(i))) for i in SMITH)
        res[tag] = {"r1": r1, "r2": r2, "s0": s0, "s1": s1, "s2": s2, "rs": rs, "mark": str(J("Zo49Mig").MARK_ID) if tag == "new" else None}
    o, n = res["old"], res["new"]
    ch_o = sorted(k for k in set(o["s0"]) | set(o["s1"]) if o["s0"].get(k) != o["s1"].get(k))
    ch_n = sorted(k for k in set(n["s0"]) | set(n["s1"]) if n["s0"].get(k) != n["s1"].get(k))
    extra = sorted(set(ch_n) - set(ch_o))
    K.notes.append("LIVE49: 0.4.48 start 1 changed %s; 0.4.49 changed %s; Zo49Mig: %s" % (ch_o, ch_n, n["r1"].get("Zo49Mig", "")[:300]))
    K.check(set(extra) <= {"xp.properties", "config-changes.log"} | set(k for k in extra if k.startswith("config-history/")),
            "LIVE49: 0.4.49 start 1 changes what 0.4.48 changes + only xp.properties / its History copy / the change log: %s" % extra)
    xp1 = n["s1"].get("xp.properties", b"").decode("latin-1")
    ox1 = o["s1"].get("xp.properties", b"").decode("latin-1")
    add = [ln for ln in xp1.splitlines() if ln not in ox1.splitlines()]
    gone = [ln for ln in ox1.splitlines() if ln not in xp1.splitlines()]
    K.check(not gone and all(("%s=%s" % kv) in add for kv in LINES if ("%s=%s" % kv) not in ox1.splitlines()), "LIVE49: the live xp.properties = 0.4.48's result + the zone lines / header / marker only: +%d -%s" % (len(add), gone[:4]))
    K.check(all(n["rs"].get(k) == x for k, x in MINING.items()), "LIVE49: the live copy pays the zone ores their Mining XP: %s" % {k: n["rs"].get(k) for k in MINING})
    K.check(n["rs"].get("smith") == SMITH, "LIVE49: the live copy pays the ingots + alloys their Smithing XP: %s" % n["rs"].get("smith"))
    K.check(any(k.startswith("config-history/") and v == n["s0"]["xp.properties"] for k, v in n["s1"].items() if k not in n["s0"]) or n["s0"].get("xp.properties") == n["s1"].get("xp.properties"),
            "LIVE49: the live xp.properties before the update is in config-history")
    K.check(all(n["s1"].get(k) == n["s2"].get(k) for k in set(n["s1"]) | set(n["s2"])) and n["r2"].get("Zo49Mig") == "", "LIVE49: 0.4.49 start 2 changes nothing")
    K.check(all(n["s0"].get(k) == n["s1"].get(k) for k in n["s0"] if k.startswith("players/")), "LIVE49: player files untouched")
    K.save()


if __name__ == "__main__":
    phases = [("fo", T48.run_fo), ("mg", T48.run_mg), ("zo", run_zo), ("live49", run_live49)]
    if "--no-old" not in sys.argv:
        T47 = _mod("test_skyyskills_0.4.47.py", "test_skyyskills_0_4_47")
        phases += [("pack", T47.T46.run_pack), ("pages", T47.run_pages)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
