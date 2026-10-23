"""SkyySkills 0.4.63 - harness for PLAYERS WHO LEFT DROP OUT OF THE LAST PER-PLAYER MAPS (tools/skills_0_4_63_patch.py).
Build first: python tools/skills_0_4_63_patch.py && python SkyySkills/build_skyyskills_0.4.63.py

    python SkyySkills/test_skyyskills_0.4.63.py [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, line endings kept, no new class / system / command, retainOnline = set + retainSet
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.4.62 -> 0.4.63: only ClassStat + retain, Acro + retainSet / ~ retainOnline (and the version text)
  LV    EXECUTED the leave path (Acro.retainSet = what retainOnline runs every 30 s): two players fill ClassStat DRY / CAST / LAST through the
        real dry() / cast() calls, SkillMsg.LAST, and three maps the sweep already pruned (Acro.STATE, ManaRegen.CMB, Perks.LASTCLS); player A
        leaves -> all of A's entries gone, B's entries untouched (same objects); a cast that lands after the sweep (a leave during a cast) is
        dropped by the next sweep; a re-join right away starts with no dry latch / last cast and keeps its new entries on the next sweep;
        retainSet(null) and retainOnline() with no Universe change nothing and throw nothing
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "skills063", "sk")]
VERSION = "0.4.63"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.62.py")
PATCH = os.path.join(TOOLS, "skills_0_4_63_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.62.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
ADDED = []
EXPECT = {}   # filled in below (checked by hand)


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyySkills 0.4.63 - build script') and g.count('VERSION = "0.4.63"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    ro = g[g.index("public static void retainOnline() {{"):]
    ro = ro[:ro.index('""", acro))')]
    K.check("retainSet(online);" in ro and "retainAll" not in ro and "getPlayers()" in ro, "S retainOnline = the Universe set + retainSet(online), nothing else")
    rs = g[g.index("public static void retainSet(java.util.Set online) {{"):]
    rs = rs[:rs.index('""", acro))')]
    ors = o[o.index("public static void retainOnline() {{"):]
    ors = ors[:ors.index('""", acro))')]
    old_lines = [ln for ln in ors.split("\n") if "retain" in ln and "retainOnline" not in ln]
    new_lines = [ln for ln in rs.split("\n") if "retain" in ln and "retainSet" not in ln]
    K.check(new_lines[:len(old_lines)] == old_lines and len(new_lines) == len(old_lines) + 2
            and "ClassStat.retain(online)" in new_lines[-2] and "SkillMsg.LAST.keySet().retainAll(online)" in new_lines[-1],
            "S retainSet runs every prune 0.4.62's retainOnline ran (%d, same order) + ClassStat.retain + SkillMsg.LAST" % len(old_lines))
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_lv(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg = J("SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    CS, MSG, AC, MR, PK = J("ClassStat"), J("SkillMsg"), J("Acro"), J("ManaRegen"), J("Perks")
    UUID, Long, HashSet = JClass("java.util.UUID"), JClass("java.lang.Long"), JClass("java.util.HashSet")
    A = UUID.fromString("00000000-0000-0000-0000-000000063001")
    Bp = UUID.fromString("00000000-0000-0000-0000-000000063002")
    now = 1000000

    def fill(u, n):
        K.check(bool(CS.dry(u, 100.0, 5.0)), "LV setup: dry() latches %s (5 of 100 < refill.below)" % n)
        CS.cast(u, now)
        CS.LAST.put(u, JClass("java.lang.Double").valueOf(12.5))
        MSG.LAST.put(u, Long.valueOf(now))
        AC.STATE.put(u, JArray(JClass("double"))(304))
        MR.CMB.put(u, JArray(JClass("long"))(2))
        PK.LASTCLS.put(u, "Mage")

    maps = [("ClassStat.DRY", CS.DRY), ("ClassStat.CAST", CS.CAST), ("ClassStat.LAST", CS.LAST), ("SkillMsg.LAST", MSG.LAST),
            ("Acro.STATE", AC.STATE), ("ManaRegen.CMB", MR.CMB), ("Perks.LASTCLS", PK.LASTCLS)]
    fill(A, "A")
    fill(Bp, "B")
    K.check(all(m.containsKey(A) and m.containsKey(Bp) for n, m in maps), "LV both players in all %d maps" % len(maps))
    before = dict((n, m.get(Bp)) for n, m in maps)
    # retainOnline() with no Universe (bare JVM): caught, nothing removed
    AC.retainOnline()
    K.check(all(m.containsKey(A) and m.containsKey(Bp) for n, m in maps), "LV retainOnline() without a Universe throws nothing and removes nothing")
    AC.retainSet(None)
    K.check(all(m.containsKey(A) and m.containsKey(Bp) for n, m in maps), "LV retainSet(null) changes nothing")
    # A leaves: the sweep sees only B online
    on = HashSet()
    on.add(Bp)
    AC.retainSet(on)
    K.check(not any(m.containsKey(A) for n, m in maps), "LV A left: gone from every map: %s" % [n for n, m in maps if m.containsKey(A)])
    K.check(all(m.containsKey(Bp) and m.get(Bp) is not None and (m.get(Bp) == before[n] if isinstance(before[n], str) else m.get(Bp).equals(before[n])) for n, m in maps), "LV B (online) keeps every entry untouched")
    K.check(int(CS.sinceCast(Bp, now + 500)) == 500 and int(CS.sinceCast(A, now + 500)) == -1, "LV sinceCast: B 500 ms, A none (-1)")
    K.check(bool(CS.dry(Bp, 100.0, 50.0)), "LV B's dry latch still on (50 of 100, latched until full)")
    # a leave during a cast: the world thread's cast lands after the sweep -> one stray entry, the next sweep drops it
    CS.cast(A, now + 10)
    K.check(CS.CAST.containsKey(A), "LV a cast landing after the sweep re-adds A (stray)")
    AC.retainSet(on)
    K.check(not CS.CAST.containsKey(A) and CS.CAST.containsKey(Bp), "LV the next sweep drops the stray, B kept")
    # a re-join right away: A starts without the old latch / cast, then fills again and stays on the next sweep
    K.check(not bool(CS.dry(A, 100.0, 50.0)) and not CS.DRY.containsKey(A), "LV A re-joins at 50 of 100: no old dry latch (needs < refill.below again)")
    K.check(int(CS.sinceCast(A, now)) == -1, "LV A re-joins: no old last cast")
    CS.cast(A, now + 20)
    CS.dry(A, 100.0, 5.0)
    MSG.LAST.put(A, Long.valueOf(now + 20))
    on.add(A)
    AC.retainSet(on)
    K.check(CS.CAST.containsKey(A) and CS.DRY.containsKey(A) and MSG.LAST.containsKey(A) and CS.CAST.containsKey(Bp), "LV re-joined A (online again) keeps its new entries")
    # everyone leaves
    AC.retainSet(HashSet())
    K.check(all(m.isEmpty() for n, m in maps), "LV nobody online: every map empty")
    # profile switch path unchanged (forget)
    fill(A, "A")
    CS.forget(A)
    K.check(not CS.DRY.containsKey(A) and not CS.CAST.containsKey(A) and not CS.LAST.containsKey(A) and MSG.LAST.containsKey(A), "LV ClassStat.forget (profile switch) as before")
    K.save()


# checked by hand 2026-10-23 (first run): the members this round changes on purpose; CfgFn / CfgRows / CurveP9Mig / ManaGuard / SkillCfg /
# SkyySkillsPlugin differ only by the version text (0.4.62 -> 0.4.63 in the xp.properties header, the pack id, the ready line)
EXPECT.update({'Acro': ['+m retainSet', '~m retainOnline'], 'ClassStat': ['+m retain'], 'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'],
               'CurveP9Mig': ['~m run'], 'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'], 'SkillCfg': ['~m load'],
               'SkyySkillsPlugin': ['~m setup']})

if __name__ == "__main__":
    phases = [("static", run_static), ("lv", run_lv)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__)
