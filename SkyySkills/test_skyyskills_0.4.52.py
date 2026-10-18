"""SkyySkills 0.4.52 - harness for LESS MANA (tools/skills_0_4_52_patch.py; research/Mana-Budget-2026-10-18.md): lower max Mana per class
level, a little less Mana regen (in combat 65 %, per class level 5 %, on-hit wait 750 ms) and the one-time Mn52Mig update of an existing
xp.properties. Build first: python tools/skills_0_4_52_patch.py && python SkyySkills/build_skyyskills_0.4.52.py

    python SkyySkills/test_skyyskills_0.4.52.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.51 -> 0.4.52: + Mn52Mig; only the planned members (the default constants, the setup call, the version texts)
  FO / MG / ZO / FL / LIVE50  the 0.4.48 - 0.4.50 phases unchanged on this jar (older migrations + their live-copy runs)
  MN  the new defaults (file, code fields, rows), Mn52Mig.plan + run (old defaults migrate, hand edits kept, a line already at the new
      default not reported, other spellings untouched, CRLF, last entry wins, multi-line untouched, marker, History, change log + Undo
      line, second run nothing, fresh file untouched, no file nothing), SkillCfg.load reads the new numbers (ClassMana / ManaRegen /
      ManaHit), PerkMig's old 50 -> today's 65 on a pre-0.4.25 file, then Mn52Mig quiet; the Mana budget checks (SkyyArmory 0.1.34's
      Mana check formula stays within 40 % for every wand / staff band; the dearest A1 + A2 pair fits every pool at its unlock level)
  LIVE52  every one-time update in setup() order on a scratch COPY of the live data, twice
  PK / PG  0.4.47's asset-pack + page phases on this jar (skip with --no-old)
  AA  engine-access audit
NOT COVERED: the feel in game (Skyy's test: run dry after 2-3 rotations), Server Setup pages (rows unchanged apart from defaults / help).
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


T50 = _mod("test_skyyskills_0.4.50.py", "test_skyyskills_0_4_50")
T49, T48 = T50.T49, T50.T48
VERSION = "0.4.52"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.51.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "mana", "sk")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyySkills")   # the current test world (read only - HK.run copies it)
ADDED = ["Mn52Mig"]
EXPECT = {"ClassMana": ["~<clinit>"], "ManaRegen": ["~<clinit>"], "ManaHit": ["~<clinit>", "~m read"],      # the new default numbers
          "PerkMig": ["~<clinit>"], "ClassManaMig": ["~<clinit>", "~m plan"], "KillXpMig": ["~m plan", "~m run", "~m sameAfter"],   # their appended blocks
          "SkillCfg": ["~m ensureManaRegen", "~m load"], "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],
          "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"], "SkyySkillsPlugin": ["~m setup"]}   # + version texts, Mn52Mig.run
jpath, loader_for = T48.jpath, T48.loader_for

PER = [("Archer", "2", "1"), ("Warrior", "2", "1"), ("Assassin", "2", "1"), ("Monk", "2", "1"), ("Mage", "10", "9.5"), ("Berserker", "2", "1"),
       ("Priest", "5", "4.5"), ("Spellblade", "4", "3")]
REGEN = [("mana.regen.inCombat", "75", "65"), ("mana.regen.perLevel", "7", "5"), ("mana.onHitCooldownMs", "500", "750")]
MN_KEYS = [("mana.classPerLevel." + c, o, n) for c, o, n in PER] + REGEN
OLD_TXT = "".join("%s=%s\n" % (k, o) for k, o, n in MN_KEYS)
NEW_TXT = "".join("%s=%s\n" % (k, n) for k, o, n in MN_KEYS)
# SkyyArmory 0.1.34 (read only): WANDS + band starts; staff = 2 x wand; its manaCheck(): pool = base + per x L + overall x floor(L / 9)
WANDS = [("Wood", 5, 1), ("Copper", 10, 10), ("Iron", 15, 15), ("Thorium", 25, 20), ("Cobalt", 40, 25), ("Adamantite", 60, 35), ("Mithril", 85, 40),
         ("Onyxium", 85, 40)]
# SkyyClasses 0.1.38 PLAN_43 (mana of the 4 shapes) per class, ABILS order (0 A1, 1 A2, 2 A2-alt, 3-4 A1-alts); unlock levels _UNL 1 / 10 / 20 / 30 / 30
AB = {"Mage": [[23, 23, 23, 20], [16, 16, 16, 14], [19, 19, 19, 20], [28, 28, 28, 31], [23, 22, 23, 27]],
      "Priest": [[18, 18, 18, 20], [20, 20, 20, 20], [15, 15, 15, 15], [26, 26, 26, 26], [22, 22, 22, 25]],
      "Monk": [[2] * 4, [3, 3, 3, 3], [4, 4, 4, 4], [3] * 4, [7, 6, 7, 8]],
      "Assassin": [[6, 6, 6, 5], [5, 5, 5, 5], [6, 6, 6, 6], [7, 7, 7, 7]],
      "Warrior": [[5, 5, 5, 3], [4, 5, 4, 4], [5, 5, 5, 5], [5, 5, 5, 6], [5, 5, 5, 6]],
      "Berserker": [[3, 3, 3, 2], [3, 3, 3, 3], [3, 3, 3, 4], [1, 1, 1, 1], [9, 9, 9, 10]],
      "Archer": [[4, 4, 5, 4], [6, 6, 7, 6], [5, 4, 5, 5], [7, 7, 7, 9], [6, 6, 6, 5]],
      "Spellblade": [[8, 8, 8, 7], [7, 8, 8, 8], [9, 9, 9, 10], [10, 10, 10, 10], [9, 9, 9, 8]]}
UNL = [1, 10, 20, 30, 30]
BASE = {"Archer": 24, "Warrior": 21, "Assassin": 24, "Monk": 21, "Mage": 45, "Berserker": 12, "Priest": 42, "Spellblade": 33}


# ============================================================================================ MN: less Mana
def run_mn(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    M, Cfg, Hist, CLog, Rows = J("Mn52Mig"), J("SkillCfg"), J("CfgHist"), J("CfgLog"), J("CfgRows")
    CM, MR, MH = J("ClassMana"), J("ManaRegen"), J("ManaHit")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    S = lambda x: JString(x)
    D = str(Cfg.DEFAULTS)
    MARK_ID = str(M.MARK_ID)
    # ---- defaults: file, code fields, rows
    for k, o, n in MN_KEYS:
        K.check(("\n%s=%s\n" % (k, n)) in ("\n" + D) and ("\n" + D).count("\n" + k + "=") == 1, "MN default file: %s=%s" % (k, n))
    K.check(D.count(MARK_ID) == 1 and M.plan(S(D)) is None, "MN default file carries the Mn52Mig marker -> never migrated")
    K.eq([str(x) for x in CM.DEF_CLS], [c for c, o, n in PER], "MN ClassMana.DEF_CLS order kept")
    K.eq([float(x) for x in CM.DEF_PER], [float(n) for c, o, n in PER], "MN ClassMana.DEF_PER = the new per-level numbers")
    K.check(int(MR.IN_COMBAT) == 65 and float(MR.PER_LEVEL) == 5.0 and int(MR.FROM_LEVEL) == 20 and int(MH.CD) == 750,
            "MN code defaults: in combat 65, per level 5, from level 20, on-hit wait 750 (%s %s %s %s)" % (MR.IN_COMBAT, MR.PER_LEVEL, MR.FROM_LEVEL, MH.CD))
    K.eq([str(x) for x in M.KEYS], [k for k, o, n in MN_KEYS], "MN Mn52Mig.KEYS")
    K.eq([str(x) for x in M.OLDS], [o for k, o, n in MN_KEYS], "MN Mn52Mig.OLDS")
    K.eq([str(x) for x in M.NEWS], [n for k, o, n in MN_KEYS], "MN Mn52Mig.NEWS")
    # ---- plan (pure)
    old = "a=1\n# keep me\n" + OLD_TXT + "mana.classBase.Mage=45\nz=2\n"
    want = "a=1\n# keep me\n" + NEW_TXT + "mana.classBase.Mage=45\nz=2\n" + str(M.MARK) + "\n"
    r = M.plan(S(old))
    K.check(str(r[0]) == want, "MN plan: the 11 old defaults -> new, every other byte kept, the marker at the end: %r" % str(r[0])[-240:])
    K.eq([str(x) for x in r[1]], [x for k, o, n in MN_KEYS for x in (k, o, n)], "MN plan: one change-log row per key")
    K.check(str(r[3]) == "", "MN plan: nothing reported as kept")
    K.check(bool(M.sameAfter(S(old).getBytes("ISO-8859-1"), S(str(r[0])).getBytes("ISO-8859-1"), r[2])), "MN sameAfter accepts the plan")
    K.check(not bool(M.sameAfter(S(old).getBytes("ISO-8859-1"), S(str(r[0]).replace("z=2", "z=3")).getBytes("ISO-8859-1"), r[2])), "MN sameAfter refuses another change (control)")
    hand = old.replace("mana.classPerLevel.Mage=10", "mana.classPerLevel.Mage = 12").replace("mana.regen.inCombat=75", "mana.regen.inCombat=80")
    r = M.plan(S(hand))
    b2 = str(r[0])
    K.check("mana.classPerLevel.Mage = 12\n" in b2 and "mana.regen.inCombat=80\n" in b2 and "mana.classPerLevel.Priest=4.5\n" in b2
            and "mana.regen.perLevel=5\n" in b2 and "mana.classPerLevel.Mage=12 kept" in str(r[3]) and "mana.regen.inCombat=80 kept" in str(r[3]),
            "MN plan: an admin's own values (Mage 12, in combat 80) are kept + reported, the others migrate: %s" % str(r[3])[:200])
    r = M.plan(S("mana.regen.inCombat=65\nmana.classPerLevel.Mage=10\n"))
    K.check(str(r[0]).startswith("mana.regen.inCombat=65\nmana.classPerLevel.Mage=9.5\n") and str(r[3]) == "",
            "MN plan: a line already at the new default is left and not reported as an admin value: %r" % str(r[3]))
    r = M.plan(S("mana.classPerLevel.mage=10\nmana.classPerLevel.MAGE=10\n"))
    K.check(str(r[0]).startswith("mana.classPerLevel.mage=10\nmana.classPerLevel.MAGE=10\n") and len(r[1]) == 0,
            "MN plan: other spellings of a table entry are never touched (exact keys only)")
    r = M.plan(S(old.replace("\n", "\r\n")))
    K.check(str(r[0]) == want.replace("\n", "\r\n"), "MN plan: a CRLF file stays CRLF")
    K.check(M.plan(S(old + "# " + MARK_ID + " x\n")) is None, "MN plan: the marker -> nothing (run once)")
    r = M.plan(S("mana.regen.perLevel=7\nmana.regen.perLevel=6\n"))
    K.check(str(r[0]).startswith("mana.regen.perLevel=7\nmana.regen.perLevel=6\n") and len(r[1]) == 0, "MN plan: the LAST entry decides (an admin's later 6 wins)")
    r = M.plan(S("mana.regen.perLevel=6\nmana.regen.perLevel=7\n"))
    K.check(str(r[0]).startswith("mana.regen.perLevel=6\nmana.regen.perLevel=5\n"), "MN plan: the last entry at the old default migrates, the earlier one stays")
    r = M.plan(S("mana.onHitCooldownMs=5\\\n00\n"))
    K.check(str(r[0]).startswith("mana.onHitCooldownMs=5\\\n00\n") and len(r[1]) == 0, "MN plan: a continued (multi-line) value is never touched")
    r = M.plan(S("a=1\n"))
    K.check(len(r[1]) == 0 and str(r[0]) == "a=1\n" + str(M.MARK) + "\n", "MN plan: no Mana lines -> only the marker (the new code defaults apply)")

    # ---- run, end to end
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
    for tag, txt in (("lf", old), ("crlf", old.replace("\n", "\r\n"))):
        d = os.path.join(scratch, "mn", tag)
        os.makedirs(d)
        open(os.path.join(d, "xp.properties"), "wb").write(txt.encode("latin-1"))
        s0 = snap(d)
        r1 = start(d)
        s1 = snap(d)
        nl = "\r\n" if tag == "crlf" else "\n"
        K.check(s1["xp.properties"].decode("latin-1") == want.replace("\n", nl), "MN run %s: the file = the plan" % tag)
        K.check(any(k.startswith("config-history/") and v == s0["xp.properties"] for k, v in s1.items()), "MN run %s: the old file is in config-history" % tag)
        logs = [v.decode("latin-1") for k, v in s1.items() if k.endswith("config-changes.log")]
        K.check(logs and all(k in logs[0] for k, o, n in MN_KEYS), "MN run %s: a change-log line per key (Undo): %s" % (tag, [k for k in s1 if "change" in k]))
        K.check("Undo" in r1 and "config-history" in r1 and "0.4.52" in r1, "MN run %s: the INFO line: %s" % (tag, r1[:200]))
        K.check(start(d) == "" and snap(d) == s1, "MN run %s: a second start changes nothing" % tag)
        Cfg.FILE = jpath(os.path.join(d, "xp.properties"))
        Cfg.load()
        K.check(float(CM.perLevel("Mage")) == 9.5 and float(CM.perLevel("Priest")) == 4.5 and float(CM.perLevel("Warrior")) == 1.0
                and float(CM.perLevel("Spellblade")) == 3.0, "MN run %s: SkillCfg.load -> ClassMana Mage 9.5, Priest 4.5, Warrior 1, Spellblade 3" % tag)
        K.check(int(MR.IN_COMBAT) == 65 and float(MR.PER_LEVEL) == 5.0 and int(MH.CD) == 750, "MN run %s: SkillCfg.load -> ManaRegen 65 / 5, ManaHit 750" % tag)
        K.check("9.5" in str(CM.text()) and "4.5" in str(CM.text()), "MN run %s: the class Mana text shows 9.5 / 4.5: %s" % (tag, CM.text()))
    d = os.path.join(scratch, "mn", "fresh")
    os.makedirs(d)
    open(os.path.join(d, "xp.properties"), "wb").write(D.encode("latin-1"))
    s0 = snap(d)
    K.check(start(d) == "" and snap(d) == s0, "MN run fresh: a fresh default file is untouched")
    d = os.path.join(scratch, "mn", "none")
    os.makedirs(d)
    K.check(start(d) == "" and snap(d) == {}, "MN run none: no file -> nothing")

    # ---- a pre-0.4.25 file: PerkMig rewrites its untouched 50 to today's 65, then Mn52Mig is quiet about it
    PM = J("PerkMig")
    K.eq([str(x) for x in PM.RW_KEY][-1:] + [str(x) for x in PM.RW_OLD][-1:] + [str(x) for x in PM.RW_NEW][-1:], ["mana.regen.inCombat", "50", "65"],
         "MN PerkMig's 0.4.25 rewrite of mana.regen.inCombat 50 lands on 65")

    # ---- the Mana budget checks (research/Mana-Budget-2026-10-18.md)
    per = dict((c, float(n)) for c, o, n in PER)
    worst = []
    for ci, cls in enumerate(("Priest", "Mage")):
        for m, w, L in WANDS:
            cost = w * (2 if cls == "Mage" else 1)
            pool = BASE[cls] + per[cls] * L + 0.2 * (L // 9)
            worst.append((cost * 100.0 / pool, cls, m, L))
    bad = [x for x in worst if x[0] > 40.0]
    K.check(not bad, "MN SkyyArmory 0.1.34 Mana check: every charged shot <= 40 %% of its band-start pool (worst %s)" % (max(worst),))
    rot = []
    for cls, ab in AB.items():
        for L in sorted(set(UNL)):
            pool = BASE[cls] + per[cls] * L
            a1 = [a for i, a in enumerate(ab) if UNL[i] <= L and i in (0, 3, 4)]
            a2 = [a for i, a in enumerate(ab) if UNL[i] <= L and i in (1, 2)]
            need = (max(max(a) for a in a1) if a1 else 0) + (max(max(a) for a in a2) if a2 else 0)
            rot.append((pool - need, cls, L, pool, need))
    K.check(all(x[0] >= 0 for x in rot), "MN one rotation (dearest A1 + A2 shape at the unlock level) fits every pool (tightest %s)" % (min(rot),))
    K.notes.append("MN tightest rotation fit: %s; worst Armory share: %.1f%% (%s %s at %d)" % (min(rot), max(worst)[0], max(worst)[1], max(worst)[2], max(worst)[3]))
    K.save()


# ============================================================================================ LIVE52: every update in setup() order on a COPY of the live data
def run_live52(out, jar, scratch, home):
    import shutil
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    lc = os.path.join(os.path.dirname(home), "copy52")
    shutil.copytree(home, lc)
    L = loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Cfg, Sto, Hist, CLog, Rows, CM, MR, MH = J("SkillCfg"), J("SkillStore"), J("CfgHist"), J("CfgLog"), J("CfgRows"), J("ClassMana"), J("ManaRegen"), J("ManaHit")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    migs = T49.OLD_MIGS + ["Zo49Mig", "Fl50Mig", "Mn52Mig"]

    def snap(d):
        return dict((os.path.relpath(os.path.join(r, fn), d).replace(os.sep, "/"), open(os.path.join(r, fn), "rb").read())
                    for r, ds, fs in os.walk(d) for fn in fs)

    def start():
        Cfg.FILE = jpath(os.path.join(lc, "xp.properties"))
        Sto.DATA.clear()
        Sto.DIR = jpath(os.path.join(lc, "players"))
        Hist.DIR = None
        Rows.HOME = None
        CLog.FILE = None
        CLog.Q.clear()
        r = dict((nm, str(J(nm).run())) for nm in migs)
        r["load"] = str(Cfg.load())
        return r
    s0 = snap(lc)
    r1 = start()
    s1 = snap(lc)
    vals = (str(CM.text()), int(MR.IN_COMBAT), float(MR.PER_LEVEL), int(MH.CD))
    r2 = start()
    s2 = snap(lc)
    xp0 = s0.get("xp.properties", b"").decode("latin-1").replace("\r", "")
    K.notes.append("LIVE52: Mn52Mig: %s; live Mana values now %s" % (r1.get("Mn52Mig", "")[:400], vals))
    for k, o, n in MN_KEYS:
        lines = [ln for ln in xp0.split("\n") if ln.split("=", 1)[0].strip() == k]
        if lines and lines[-1].split("=", 1)[1].strip() == o:
            nowv = [ln for ln in s1["xp.properties"].decode("latin-1").replace("\r", "").split("\n") if ln.split("=", 1)[0].strip() == k][-1]
            K.check(nowv == "%s=%s" % (k, n), "LIVE52: the live copy's untouched %s=%s is now %s" % (k, o, n))
    K.check(all(s1.get(k) == s2.get(k) for k in set(s1) | set(s2)) and r2.get("Mn52Mig") == "", "LIVE52: start 2 changes nothing")
    K.check(all(s0.get(k) == s1.get(k) for k in s0 if k.startswith("players/")), "LIVE52: player files untouched")
    K.save()


if __name__ == "__main__":
    # LIVE49 left out: it needs SkyySkills-0.4.48.jar (tidied away); LIVE50 + LIVE52 run every older update on the live copy
    phases = [("fo", T48.run_fo), ("mg", T48.run_mg), ("zo", T49.run_zo), ("fl", T50.run_fl), ("live50", T50.run_live50),
              ("mn", run_mn), ("live52", run_live52)]
    if "--no-old" not in sys.argv:
        T47 = _mod("test_skyyskills_0.4.47.py", "test_skyyskills_0_4_47")
        phases += [("pack", T47.T46.run_pack), ("pages", T47.run_pages)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
