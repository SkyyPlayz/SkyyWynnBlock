"""Derive SkyySkills/build_skyyskills_0.4.22.py from the LIVE generated SkyySkills/build_skyyskills_0.4.21.py (= the tools/deploy_set.py SET
pin; 0.4.21 came from 0.4.20 by tools/skills_0_4_21_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_21_patch.py: rep(old, new) with asserted single anchors, newline-agnostic; 0.4.21
stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_22_patch.py   then   python SkyySkills/build_skyyskills_0.4.22.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.22.py --dir tools/dev/scratch/<task>/skills0422   (bare JVM, -Xverify:all; the folder is deleted)

0.4.22 = THE MONK MOVES' SKYYSKILLS PART (Skyy 2026-10-08 "start building the monk moves"; SkyyArmory 0.1.12 builds the moves; docs/answered/
classes.md 2026-10-08 REQUEST + the LOCKED Monk lines: the plunge's ground slam "gives NO Acrobatics XP"; probe M11 saw +2 / +3 Acrobatics XP
paid for the move landings). Deploy WITH SkyyArmory 0.1.12 (alone it is harmless: the flag below is simply never set; the Bo handover then
needs SkyyArmory 0.1.11+ - the build refuses a pinned SkyyArmory that does not ship both vanilla Bo staffs).
(a) THE BO HANDOVER (like the 0.4.15 staff handover): this jar no longer ships the vanilla Weapon_Staff_Bo_Wood / _Bamboo item overrides
    (its 0.4.21 copies only scaled their 50-Mana orb cast, and they WON over SkyyArmory 0.1.11's no-orb copies by pack order - the Bo staffs
    kept the magic shot Skyy removed: docs/log 2026-10-08 06:43). SkyyArmory 0.1.11+ owns both (its 0.1.12 hold = Pole-Vault). They leave
    SPELL_ITEMS before spell_plan (the gate simulation never sees them); a SET jar or pack mod that ships one now clashes (SkyyArmory
    excepted); a pinned SkyyArmory must ship both (STOP rule: SkyySkills 0.4.22+ requires SkyyArmory 0.1.11+ - also for tools/deploy_set.py).
(b) NO ACROBATICS XP DURING A MONK MOVE: SkyyArmory 0.1.12 sets the plain java.lang bridge key armory:monkmove:<uuid> -> Long (epoch ms until)
    while a Pole-Vault / bound / Rising Strike / Plunge runs and ~0.5 s after it. Acro.monkMove(u, now) reads it; while it is on:
      - AcroSys.tick treats the player like a creative-mode one for Acrobatics XP (no run / jump / roll-gate XP, no fall-drop note, falls()
        clears a pending fall note without paying - creative's existing path), and
      - Acro.noteFall / noteRoll (the Inspect-group fall note and RollSys' rolled landing) note nothing, and
      - Acro.airJump keeps tracking the crouch / jump edges but fires NO Double Jump (the Monk's crouch is its free air jump / Plunge Punch;
        both would push at once otherwise).
    Nothing else changes: movement bonuses, the dodge roll itself, Mana regen, perks, every other skill.
NOT in this build: no migration, no new row / key / asset / system / command, no saved-data change.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.21.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.22.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.21"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
assert 'VERSION = "0.4.21"' in s and "derived from the generated 0.4.20 by tools/skills_0_4_21_patch.py" in s, "not the live generated 0.4.21"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "monkMove" not in s and "BO_OWNED" not in s, "0.4.21 already has the 0.4.22 parts"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyySkills 0.4.21 - build script (derived from the generated 0.4.20 by tools/skills_0_4_21_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.22 - build script (derived from the generated 0.4.21 by tools/skills_0_4_22_patch.py - edit the patch, not this file;
0.4.21 was derived from the generated 0.4.20 by tools/skills_0_4_21_patch.py; ''')
rep('''0.4.21: THE MONK + ASSASSIN CLASS SKILLS (Skyy LOCKED 2026-10-07 "make the classes"; full notes in tools/skills_0_4_21_patch.py). Deploy''',
    '''0.4.22: THE MONK MOVES' SKYYSKILLS PART (Skyy 2026-10-08 "start building the monk moves"; full notes in tools/skills_0_4_22_patch.py). Deploy
  WITH SkyyArmory 0.1.12. (a) THE BO HANDOVER: the vanilla Weapon_Staff_Bo_Wood / _Bamboo item overrides are no longer shipped - SkyyArmory
  0.1.11+ owns them (STOP: SkyySkills 0.4.22+ requires SkyyArmory 0.1.11+; a pinned SkyyArmory must ship both). (b) NO ACROBATICS XP while
  SkyyArmory's bridge key armory:monkmove:<uuid> (Long, epoch ms until) is on: no run / jump / fall / roll XP, no fall / roll note, and no
  Double Jump push (the Monk's crouch is its own air jump / Plunge Punch). No migration, no new row / key / asset / system.
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.22.py, -Xverify:all, scratch under tools/dev/scratch deleted afterwards).
0.4.21: THE MONK + ASSASSIN CLASS SKILLS (Skyy LOCKED 2026-10-07 "make the classes"; full notes in tools/skills_0_4_21_patch.py). Deploy''')
rep('VERSION = "0.4.21"', 'VERSION = "0.4.22"')

# ---------------------------------------------------------------------------------------------------------------- (a) the Bo handover
rep('''ARMORY_ITEMS = {}   # id -> (asset path, vanilla JSON)
''', '''ARMORY_ITEMS = {}   # id -> (asset path, vanilla JSON)
# 0.4.22 (the Bo handover, like 0.4.15's staffs): the 2 vanilla Bo staffs belong to SkyyArmory 0.1.11+ (no orb; 0.1.12: the hold = Pole-Vault).
# Their 0.4.21 overrides only scaled the 50-Mana orb cast - and won over SkyyArmory's copies by pack order. They leave the plan here.
BO_OWNED = ["Weapon_Staff_Bo_Bamboo", "Weapon_Staff_Bo_Wood"]
BO_ITEMS = {}       # id -> (asset path, vanilla JSON)
''')
rep('''    _aheirs = sorted(_k for _k, _v in SPELL_ITEMS.items() if isinstance(_v[1], dict) and _v[1].get("Parent") in ARMORY_OWNED)
    if _aheirs:
        spell_fail("%s inherit(s) a SkyyArmory-owned staff by Parent - the staff handover would change them too" % _aheirs)
''', '''    _aheirs = sorted(_k for _k, _v in SPELL_ITEMS.items() if isinstance(_v[1], dict) and _v[1].get("Parent") in ARMORY_OWNED)
    if _aheirs:
        spell_fail("%s inherit(s) a SkyyArmory-owned staff by Parent - the staff handover would change them too" % _aheirs)
    for _aid in BO_OWNED:          # 0.4.22: the 2 vanilla Bo staffs go to SkyyArmory 0.1.11+
        if _aid not in SPELL_ITEMS:
            spell_fail("%s (owned by SkyyArmory 0.1.11+ since SkyySkills 0.4.22) is not in Assets.zip any more - the Bo handover list needs a look" % _aid)
        BO_ITEMS[_aid] = SPELL_ITEMS.pop(_aid)
    _bheirs = sorted(_k for _k, _v in SPELL_ITEMS.items() if isinstance(_v[1], dict) and _v[1].get("Parent") in BO_OWNED)
    if _bheirs:
        spell_fail("%s inherit(s) a vanilla Bo staff by Parent - the Bo handover would change them too" % _bheirs)
''')
rep('''                                                                or (not armory and os.path.basename(n)[:-5] in ARMORY_OWNED)))''',
    '''                                                                or (not armory and os.path.basename(n)[:-5] in ARMORY_OWNED + BO_OWNED)))''')
rep('''    _nm = jz.namelist()
    _miss = [_a for _a in ARMORY_OWNED if not any(_n.startswith("Server/Item/Items/") and _n.endswith("/%s.json" % _a) for _n in _nm)]
''', '''    _nm = jz.namelist()
    _bmiss = [_a for _a in BO_OWNED if not any(_n.startswith("Server/Item/Items/") and _n.endswith("/%s.json" % _a) for _n in _nm)]
    if _bmiss:          # 0.4.22 STOP rule: SkyySkills 0.4.22+ requires SkyyArmory 0.1.11+ (the vanilla Bo staffs' owner)
        spell_fail("SkyyArmory %s does not ship %s - SkyySkills 0.4.22+ requires SkyyArmory 0.1.11+ (the Bo handover: without it the vanilla "
                   "Bo staffs run on their vanilla files - the 50-Mana orb behind this jar's 10-Mana staff check)" % (ver, _bmiss))
    _miss = [_a for _a in ARMORY_OWNED if not any(_n.startswith("Server/Item/Items/") and _n.endswith("/%s.json" % _a) for _n in _nm)]
''')
rep('''            print("staff handover: SkyyArmory %s ships the %d ladder staffs; its Wood staff checks %d and spends %d Mana (the kit number)" % (
                _ver, len(ARMORY_OWNED), _aw[0], _aw[1]))''', '''            print("staff handover: SkyyArmory %s ships the %d ladder staffs + the %d vanilla Bo staffs (0.4.22); its Wood staff checks %d and "
                  "spends %d Mana (the kit number)" % (_ver, len(ARMORY_OWNED), len(BO_OWNED), _aw[0], _aw[1]))''')
rep('''+ "; staff handover: the " + {PKG}.ManaCost.ARM_IDS.length + " ladder staffs come from SkyyArmory 0.1+" + "''',
    '''+ "; staff handover: the " + {PKG}.ManaCost.ARM_IDS.length + " ladder staffs come from SkyyArmory 0.1+, the 2 vanilla Bo staffs from SkyyArmory 0.1.11+" + "; no Acrobatics XP during a Monk move (bridge armory:monkmove:<uuid>)" + "''')

# ---------------------------------------------------------------------------------------------------------------- (b) the Monk move flag
rep('''# fall Damage seen by AcroFallSys (world thread): remembered, paid by falls() once the player is still alive 0.4 s later
acro.addMethod(CtNewMethod.make("""
public static void noteFall(java.util.UUID u, float amount) {
  double[] s = state(u);''', '''# 0.4.22: SkyyArmory 0.1.12's Monk move flag - bridge armory:monkmove:<uuid> -> Long (epoch ms until; plain java.lang). True = no Acrobatics
# XP and no Double Jump for that player now (the Monk moves' landings / bounds / plunge pay none - Skyy LOCKED; probe M11 saw +2 / +3)
acro.addMethod(CtNewMethod.make("""
public static boolean monkMove(java.util.UUID u, long now) {
  if (u == null) return false;
  try {
    Object o = {PKG}.SkillStore.bridge().get("armory:monkmove:" + u.toString());
    return o instanceof Long && now <= ((Long) o).longValue();
  } catch (Throwable t) { return false; }
}""".replace("{PKG}", PKG), acro))
# fall Damage seen by AcroFallSys (world thread): remembered, paid by falls() once the player is still alive 0.4 s later
acro.addMethod(CtNewMethod.make("""
public static void noteFall(java.util.UUID u, float amount) {
  if (monkMove(u, System.currentTimeMillis())) return;   // 0.4.22: a Monk move's landing pays no Acrobatics XP
  double[] s = state(u);''')
rep('''public static void noteRoll(java.util.UUID u, float amount) {
  double[] s = state(u);''', '''public static void noteRoll(java.util.UUID u, float amount) {
  if (monkMove(u, System.currentTimeMillis())) return;   // 0.4.22: a Monk move's landing pays no Acrobatics XP
  double[] s = state(u);''')
rep('''  int bits = airTrack(s, ms, now);
  if (bits == 0) return;
''', '''  int bits = airTrack(s, ms, now);
  if (bits == 0) return;
  if (monkMove(u, now)) return;   // 0.4.22: during a Monk move its crouch is the free air jump / Plunge Punch - no Double Jump push (edges still tracked)
''')
rep('''      boolean creative = {PKG}.SkillXp.creative(store, ref);
''', '''      boolean creative = {PKG}.SkillXp.creative(store, ref) || {PKG}.Acro.monkMove(u, now);   // 0.4.22: a Monk move pays no Acrobatics XP (the creative path)
''')

assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "0.4.22 adds no system / command"
with open(dst, "w", encoding="utf8", newline="") as f:
    f.write(s.replace(LF, NL))
print("wrote %s" % os.path.relpath(dst, ROOT))
