"""Derive SkyySkills/build_skyyskills_0.4.29.py from the LIVE generated SkyySkills/build_skyyskills_0.4.28.py (= the tools/deploy_set.py SET
pin; 0.4.28 came from 0.4.27 by tools/skills_0_4_28_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_28_patch.py: rep(old, new) with asserted single anchors, newline-agnostic; 0.4.28
stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_29_patch.py   then   python SkyySkills/build_skyyskills_0.4.29.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.29.py --dir tools/dev/scratch/<yours>/h   (bare JVM, -Xverify:all)

0.4.29 = THE PET XP HOOK (research/cloud/Pet-Core-Spec.md 1 "XP in" + section 8 next steps 2; SkyyPets 0.1 build notes point 4).
  - SkillXp.petXp(UUID u, int skill, long amount): bridge pets:fn:onxp (SkyyPets) is called with
    Object[] { UUID player, String NAMES[skill], Long amount, "SkyySkills" } - null-safe (no SkyyPets / not a Function = nothing),
    exception-safe (a throwing SkyyPets = one WARN per JVM, the award itself is untouched), on the caller's thread (the world thread of
    the award), no I/O, one small array per award (no batching needed: every award is already one gain4 call with its own chat note).
  - WHERE: SkillXp.gain4 right after SkillStore.addK stored the XP (+ the chat / party notes) - EVERY award funnels through gain4 (gain,
    gain2, gain3: gathering, felled trees, crops, sickle, Acrobatics, crafting / Alchemy / smelting, bridge grants: Exploration,
    Cooking, Fishing, Divinity heals, class kills + party shares, admin /skills xp). The ONE other writer of XP, SmeltTask's offline
    branch (a furnace finishes after the smelter logged out: SkillStore.addK straight), calls it too (SkyyPets then has no loaded record
    and gives nothing - harmless). `amount` = the XP really added (after the gathering pace / tree bonus / multipliers).
  - The UUID is the PLAYER's UUID (SkyyPets' PetXpFn needs a[0] instanceof UUID and resolves the ACTIVE profile itself with
    PetStore.pkey = tools/PROFILES-CONTRACT.md profile:fn:key, the same key gain4 just stored the XP under, on the same thread).
  - Skill name = SkillDefs.NAMES[slot] (the saved key: Mining, Foraging, ..., Combat.Archer ... Combat.Shaman (Zen) ... Combat.Priest,
    Alchemy, Smithing, Cooking, Exploration) = the names SkyyPets' own fallback reads (POLL_SKILLS) and its skillMatch knows
    ("Combat" pets match every Combat.<class>).
  - DECISION (4th element): the task text said "NO 4th element", but the SET pin SkyyPets 0.1 (build_skyypets_0.1.py point 4 +
    PetXpFn.apply) switches its 10-second skill:fn:xp fallback poll off ONLY when the 4th element is "SkyySkills" ("SKYYSKILLS MUST PASS
    "SkyySkills" AS THE 4TH ELEMENT; a call without a 4th element ... gives XP but leaves the poll on"). Without it pets would get every
    award TWICE (the hook + the poll's growth). The 4th element "SkyySkills" is passed; the harness runs the REAL SkyyPets 0.1 PetXpFn
    and checks PetXp.HOOKED flips on.
  No config key, no saved data, no migration, no new class / system / command. Without SkyyPets every path is 0.4.28's. Rolling back
  to 0.4.28 is safe (SkyyPets' fallback poll is then off until SkyyPets restarts - pets get no XP in between; restart the server after
  a rollback).
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.28.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.29.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.28"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.28"' in s and "derived from the generated 0.4.27 by tools/skills_0_4_28_patch.py" in s, "not the live generated 0.4.28"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "pets:fn:onxp" not in s, "0.4.28 already calls pets:fn:onxp"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
OLDS = []


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    i = s.index(old)
    j = s.find(LF, i + len(old))
    OLDS.append(s[s.rfind(LF, 0, i) + 1:(j if j >= 0 else len(s))])
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyySkills 0.4.28 - build script (derived from the generated 0.4.27 by tools/skills_0_4_28_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.29 - build script (derived from the generated 0.4.28 by tools/skills_0_4_29_patch.py - edit the patch, not this file;
0.4.28 was derived from the generated 0.4.27 by tools/skills_0_4_28_patch.py; ''')
rep('''0.4.28: ABILITY DAMAGE COUNTS AS CLASS DAMAGE (SkyyClasses 0.1.16 ability engine R1; full notes in tools/skills_0_4_28_patch.py). Damage
''', '''0.4.29: THE PET XP HOOK (research/cloud/Pet-Core-Spec.md 1 "XP in"; full notes in tools/skills_0_4_29_patch.py). After every XP award
  (SkillXp.gain4, + SmeltTask's offline write) SkillXp.petXp calls the bridge function pets:fn:onxp (SkyyPets) with
  Object[] { player UUID, saved skill name, Long XP added, "SkyySkills" } - the 4th element switches SkyyPets 0.1's fallback poll off.
  Null-safe, exception-safe (one WARN), same thread, no I/O. No config key, saved data, migration, class, system or command.
  CHECKED: SkyySkills/test_skyyskills_0.4.29.py.
0.4.28: ABILITY DAMAGE COUNTS AS CLASS DAMAGE (SkyyClasses 0.1.16 ability engine R1; full notes in tools/skills_0_4_28_patch.py). Damage
''')
rep('VERSION = "0.4.28"', 'VERSION = "0.4.29"')

# ---------------------------------------------------------------------------------------------------------------- the hook
rep('''# ================= SkillXp: award + level-up (world thread) =================
xp.addMethod(CtNewMethod.make(f"""
public static boolean creative({ST} st, {REF} r) {{''', '''# ================= SkillXp: award + level-up (world thread) =================
# 0.4.29 THE PET XP HOOK: after every award, SkyyPets' bridge function pets:fn:onxp gets { player UUID, saved skill name, Long XP added,
# "SkyySkills" } (the 4th element tells SkyyPets 0.1 the real hook is live -> its skill:fn:xp fallback poll stops). No SkyyPets = nothing;
# a throwing SkyyPets = one WARN per JVM; the award is never touched. Caller's thread, no I/O.
xp.addField(CtField.make("public static volatile boolean PET_WARNED = false;", xp))
xp.addMethod(CtNewMethod.make(f"""
public static void petXp(java.util.UUID u, int skill, long amount) {{
  if (u == null || amount <= 0L || skill < 0 || skill >= {PKG}.SkillDefs.N) return;
  try {{
    Object f = {PKG}.SkillStore.bridge().get("pets:fn:onxp");
    if (!(f instanceof java.util.function.Function)) return;
    ((java.util.function.Function) f).apply(new Object[] {{ u, {PKG}.SkillDefs.NAMES[skill], Long.valueOf(amount), "SkyySkills" }});
  }} catch (Throwable t) {{
    if (!PET_WARNED) {{ PET_WARNED = true; {PKG}.SkillCfg.warn("pets:fn:onxp (SkyyPets) failed - pets miss that XP (logged once): " + t); }}
  }}
}}""", xp))
xp.addMethod(CtNewMethod.make(f"""
public static boolean creative({ST} st, {REF} r) {{''')
rep('''  long[] r = {PKG}.SkillStore.addK(k, u, name, skill, amount);
  if (note) {PKG}.SkillMsg.note(pr, skill, amount);
  if (party != null) {PKG}.PartyXp.note(pr, skill, amount, party);
''', '''  long[] r = {PKG}.SkillStore.addK(k, u, name, skill, amount);
  if (note) {PKG}.SkillMsg.note(pr, skill, amount);
  if (party != null) {PKG}.PartyXp.note(pr, skill, amount, party);
  petXp(u, skill, amount);   // 0.4.29: SkyyPets' pets:fn:onxp (every award passes here)
''')
rep('''    if (pr != null && pr.isValid()) {PKG}.SkillXp.gain(pr, this.slot, this.amt);
    else {PKG}.SkillStore.addK(this.key, this.u, null, this.slot, this.amt);
''', '''    if (pr != null && pr.isValid()) {PKG}.SkillXp.gain(pr, this.slot, this.amt);
    else {{ {PKG}.SkillStore.addK(this.key, this.u, null, this.slot, this.amt); {PKG}.SkillXp.petXp(this.u, this.slot, this.amt); }}   // 0.4.29
''')
rep('''"; bridge skill:fn:addxp + skill:fn:craftxp''', '''"; pet XP hook (pets:fn:onxp " + ({PKG}.SkillStore.bridge().get("pets:fn:onxp") instanceof java.util.function.Function ? "found" : "not loaded yet - SkyyPets reads XP itself") + ")" + "; bridge skill:fn:addxp + skill:fn:craftxp''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "0.4.29 adds no system and no command"
assert s.count("SkillStore.addK(") == 2 and s.count("petXp(") == 3, "every addK caller calls petXp"
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.28 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.28,", len(_gone), "0.4.28 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
