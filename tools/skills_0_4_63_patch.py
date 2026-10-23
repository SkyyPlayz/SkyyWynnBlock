"""Derive SkyySkills/build_skyyskills_0.4.63.py from the GENERATED SkyySkills 0.4.62 (build_skyyskills_0.4.62.py = the tools/deploy_set.py SET
pin, made by tools/skills_0_4_62_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with
0.4.62 (tools/soundpass_gen.Patch). Line endings kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_63_patch.py   then   python SkyySkills/build_skyyskills_0.4.63.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.63.py
RESUME 'Small TODOs': the Skills DRY / CAST maps keyed by UUID never dropped players who quit (small leak). LEAN round, memory only.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.4.63 (2026-10-23) = PLAYERS WHO LEFT DROP OUT OF THE LAST PER-PLAYER MAPS (RESUME 'Small TODOs': "Skills DRY / CAST maps keyed by UUID
  never drop quit players (small leak)"; LEAN round, memory only - no saved data, no setting, no behaviour change for players online).
  1. ClassStat.retain(online): DRY (the quick-refill dry latch), CAST (the last charged shot / ability ms) and LAST (the class speed % last
     posted) keep only online players - they were cleared on a profile switch (ClassStat.forget) but never when a player quit.
  2. SkillMsg.LAST (the "+N XP" line's last-shown ms) is pruned too: SkillMsg.flushDue only dropped it while that player still had a pending
     line, so a player who quit with nothing pending stayed in it.
  3. Acro.retainOnline (SkillTick, every 30 s, scheduler thread; the mod's leave hook since 0.2) = the online set from Universe + the new
     Acro.retainSet(online), which holds every prune it already ran (same order, same try) plus 1 and 2 - the harness drives retainSet.
  The other UUID-keyed maps were already pruned there (or by PartyXp.retainOnline), are bounded caches (Fell.RATE 2000, P3Xp.RBN / SkillCap /
  MsgRoute 4096), or are kept on purpose: ManaRegen.SRC and HpRegen.FLAT / PCT (entries owned by the mods that posted them), SkillStore's
  profile cache (DATA / NAMES / OWNER / RBTX / ORE / TOPIDX / QUIET / DIRTY - saved data, leaderboards).
  ROLLBACK to 0.4.62: just the jar (nothing saved changes).
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.62.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.63.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.62"') and P.has("CurveP9Mig") and not P.has("retainSet("), "not the generated SkyySkills 0.4.62 script"
REG0, SYS0, CLS0 = P.s.count("registerCommand("), P.s.count("registerSystem("), P.s.count("makeClass(")

P.rep('''"""SkyySkills 0.4.62 - build script (derived from the generated 0.4.61 by tools/skills_0_4_62_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.63 - build script (derived from the generated 0.4.62 by tools/skills_0_4_63_patch.py - edit the patch, not this file;
''' + NOTE + '''0.4.62 was derived from the generated 0.4.61 by tools/skills_0_4_62_patch.py;
''')
P.rep('VERSION = "0.4.62"', 'VERSION = "0.4.63"')

# ---- 1. ClassStat.retain (right after forget; compiled long before Acro, its caller)
P.rep('''public static void forget(java.util.UUID u) {
  if (u == null) return;
  DRY.remove(u);
  CAST.remove(u);
  LAST.remove(u);
}"""), cst))
''', '''public static void forget(java.util.UUID u) {
  if (u == null) return;
  DRY.remove(u);
  CAST.remove(u);
  LAST.remove(u);
}"""), cst))
# 0.4.63: players who left (Acro.retainSet, every 30 s) drop out of the dry latch / last cast / class speed pct - forget only ran on a switch
cst.addMethod(CtNewMethod.make(J14(r"""
public static void retain(java.util.Set online) {
  DRY.keySet().retainAll(online);
  CAST.keySet().retainAll(online);
  LAST.keySet().retainAll(online);
}"""), cst))
''')

# ---- 2 + 3. Acro.retainOnline = the online set + retainSet(online) (every prune it ran, same order, + ClassStat + SkillMsg.LAST)
P.rep('''acro.addMethod(CtNewMethod.make(f"""
public static void retainOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr != null) online.add(pr.getUuid());
    }}
    STATE.keySet().retainAll(online);''', '''# 0.4.63: retainSet = every per-player prune for the players still online (the harness drives it); retainOnline builds the set from Universe
acro.addMethod(CtNewMethod.make(f"""
public static void retainSet(java.util.Set online) {{
  if (online == null) return;
  try {{
    STATE.keySet().retainAll(online);''')
P.rep('''    {PKG}.SkillDef.retain(online); // 0.4.25: skill Defense + its skill:def:<uuid> bridge key
  }} catch (Throwable t) {{ }}
}}""", acro))
''', '''    {PKG}.SkillDef.retain(online); // 0.4.25: skill Defense + its skill:def:<uuid> bridge key
    {PKG}.ClassStat.retain(online);   // 0.4.63: the Mana dry latch / last cast / class speed pct of players who left
    {PKG}.SkillMsg.LAST.keySet().retainAll(online);   // 0.4.63: the "+N XP" line's last-shown stamp (flushDue only drops it with a pending line)
  }} catch (Throwable t) {{ }}
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static void retainOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr != null) online.add(pr.getUuid());
    }}
    retainSet(online);
  }} catch (Throwable t) {{ }}
}}""", acro))
''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0 and P.s.count("makeClass(") == CLS0
_i = P.s.index
assert _i("public static void retain(java.util.Set online) {\n  DRY.keySet()") < _i("public static void retainSet(java.util.Set online)") \
    < _i("public static void retainOnline() {{") < _i("{PKG}.Acro.retainOnline();")   # methods before callers
assert _i("{PKG}.ClassStat.retain(online);") < _i("public static void retainOnline() {{")
P.finish()
