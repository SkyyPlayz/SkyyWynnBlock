"""Derive SkyyArmory/build_skyyarmory_0.1.23.py (+ its harness SkyyArmory/test_skyyarmory_0.1.23.py) from the GENERATED FULL 0.1.21 build
script (SkyyArmory/build_skyyarmory_0.1.21.py, made by tools/armory_0_1_21_patch.py) plus the 0.1.22 SoulDrop change (tools/armory_0_1_22_patch.py
rep blocks, carried below word for word). 0.1.22 (the SET pin) was a PORT BUILD (the 0.1.21 jar re-compiled, only SoulDrop changed); 0.1.23 is
built FROM SOURCE again, on the Hytale 0.7.0 Assets.zip. Every anchor is asserted (rep = exactly the given number of hits). Edit THIS file,
never the generated scripts.
Run:  python tools/armory_0_1_23_patch.py   then   python SkyyArmory/build_skyyarmory_0.1.23.py   then
      python SkyyArmory/test_skyyarmory_0.1.23.py --dir tools/dev/scratch/<task>/harness      (never --deploy)

0.1.23 (2026-10-13; Skyy: "hytale 0.7.0  is out!" + "work through your whole list, so everything is ready to play when i get off work." +
"During/ before we consolidate the mods together, lets audit the code structure, and make sure they are working together in the smoothest
easiest lag free way possible"):
WHAT 0.1.23 IS
  1. THE FULL BUILD AGAIN, ON HYTALE 0.7.0. 0.1.22 was a port build (the 0.1.21 jar re-compiled, only SoulDrop changed) because the full
     script stopped on the 0.7 vanilla files it copies / checks. This patch ports every stop (A1-A10, E1-E2 below) and carries 0.1.22's
     SoulDrop change. RULE (Skyy-tested feel - docs/answered/classes.md, research/classes/Priest.md + Mage.md): where 0.7 changed a vanilla
     NUMBER our weapons copy, OUR tested value is kept (and the 0.7 number is asserted, so a further move stops the build); where a vanilla
     field disappeared / was renamed, the 0.7 equivalent is used. RESULT (harness C): every one of the 845 non-class files is byte-identical
     to the 0.1.22 jar except manifest.json (Version / Name). FIX ROUND: the dagger Pounce override does NOT take 0.7's new Rules.
       A1 vanilla staffs lost the dead Staff_Cast_Summon_Charged var (Thorium keeps a bare one)   -> checks updated; our files never had it
       A2 particle system Spectre_Void_Head renamed Void_Spectre_Head (same body)                 -> the blue copy is built from the 0.7 name
       A3 wand tap 0.346 -> 0.329 s (vanilla)                                                    -> our quick shot keeps its tested 0.35 s
       A4 crossbow reload key Ability3 -> Ability4 (template)                                    -> our crossbows inherit it (vanilla key)
       A5 Iron crossbow: combo 27 -> 13, durability 120 -> 250, wear 0.28 -> 0.17                -> our Wynn crossbow table + wear 0.28 kept
       A6 Goblin_Ogre role gone; new bosses                                                      -> checks name the 0.7 roles; words unchanged
       A7 sword chain 0.334/0.334/0.75 -> 0.318/0.318/0.625, dagger 0.207 -> 0.198               -> Bo / gauntlet / wrap numbers use the tested cadence
       A8 new dagger Weapon_Daggers_Void_Crystal (no damage vars)                                -> Shadow Step reaches it (every vanilla dagger)
       A9 dagger Charging gained Rules                                                           -> our fist hold (our file) unchanged
       A10 Sword GuardBash Speed 1.15; Pounce hold slow 0.5 -> 0.85                              -> our anim sets keep 1.0; Shadow Step hold keeps 0.5
       E1 ProjectileModule.spawnProjectile overload + long (probe only)    E2 a 3rd onImpact path for PIERCING projectiles (our bolt has none)
     SKYYSKILLS 0.4.31 (live) owns Mana.json + the vanilla staff / wand cast interactions (Wand_Cast_* / Staff_Cast_* / Spellbook_Cast_*);
     SkyyArmory ships none of those files (the build's SKILLS_INTS + clash scan check it: no file both jars ship, only manifest.json), our
     metal wands / staffs spend through OUR SkyyArmory_* chains (W_C / S_C, unchanged), the Soul Orb drains through Java (soul.manaPerSecond).
     No double override.
  2. THE TRAVTICK LAG FIX (research/Code-Structure-Audit.md finding 19 + the Armory sub-audit):
       L8/L9 TravTick ran Grapple.tickPlayer + Soul.tickPlayer for EVERY player EVERY tick (component reads + a hand read). Now a per-body gate
             (ArmoryHold): the hand is read once, then only after a hotbar / active-slot / inventory change (2 new EntityEventSystems that
             only MARK the body: ArmorySlotSys on InventorySetActiveSlotEvent, ArmoryInvSys on InventoryChangeEvent) + a safety re-read every
             64 ticks. Grapple runs only for a crossbow in hand / a grapple record, Soul only for a Soul Orb / Cage in hand / a Binding / stored
             healing / the latch. A new body (join, world switch) runs every check for 30 ticks = the stale grapple-effect cleanup once, there.
             No event system = the old per-tick read. Idle players still drive the grapple / soul sweeps while records exist.
       L1 lock-free bridge() in ArmoryDefs + ArmoryTree (the kit's CfgRows already).   L2 ArmoryTree.gen: the epoch key string cached per player.
       L3 Monk.flag: the bridge written only when the until time (rounded UP to 250 ms) moves - never shorter than before.
       L4 Soul.publish: only a changed value is written; a removal only when one was written.
       L5 ArmoryCheck stops re-scheduling once the pack check is done and the Mana check has run (it ran every 30 s forever).
  Saved data: none touched. The 0.1.21 soul tether migration marker / texts and every earlier marker stay exactly as they are. No config row,
  no command, no item, no recipe changed. Rolling back to 0.1.22 is safe (same files; only the gate goes).
"""
import os, ast, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.21.py")
DST = os.path.join(ROOT, "SkyyArmory", "build_skyyarmory_0.1.23.py")
TDST = os.path.join(ROOT, "SkyyArmory", "test_skyyarmory_0.1.23.py")

CR, LF = chr(13), chr(10)
raw = open(SRC, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.21"\nMOD = "SkyyArmory"' in s and s.startswith('"""SkyyArmory 0.1.21 - build script'), "build_skyyarmory_0.1.21.py is not the full 0.1.21 script"
assert "0.1.22" not in s and "0.1.23" not in s, "0.1.21 already has 0.1.22 / 0.1.23 parts"
SYS0, CMD0 = s.count("registerSystem("), s.count("registerCommand(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyArmory 0.1.21 - build script (javassist via jpype). GENERATED by tools/armory_0_1_21_patch.py from the GENERATED 0.1.20 - edit the
patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.21.py -> SkyyArmory/SkyyArmory-0.1.21.jar (never --deploy). Harness:
python SkyyArmory/test_skyyarmory_0.1.21.py --dir tools/dev/scratch/<task>/harness.
''', '''"""SkyyArmory 0.1.23 - build script (javassist via jpype). GENERATED by tools/armory_0_1_23_patch.py from the GENERATED FULL 0.1.21 script
(+ the 0.1.22 SoulDrop change) - edit the patch, never this file. Run: python SkyyArmory/build_skyyarmory_0.1.23.py ->
SkyyArmory/SkyyArmory-0.1.23.jar (never --deploy). Harness: python SkyyArmory/test_skyyarmory_0.1.23.py --dir tools/dev/scratch/<task>/harness.

0.1.23 = THE FULL BUILD ON THE HYTALE 0.7.0 ASSETS + THE TRAVTICK LAG FIX (2026-10-13; full notes in tools/armory_0_1_23_patch.py):
@HEADNOTES@

0.1.22 (the SET pin before 0.1.23) = the 0.1.21 jar re-compiled for Hytale 0.7 (a port build): SoulDrop.envOf's block fallback reads the
0.7 EnvironmentSection through the new SoulDrop.blockEnv instead of the removed BlockChunk.getEnvironment(III). Carried here from source.

0.1.21 (the base, everything below is still true unless 0.1.23 / 0.1.22 above say otherwise):
''')
rep('VERSION = "0.1.21"\nMOD = "SkyyArmory"', 'VERSION = "0.1.23"\nMOD = "SkyyArmory"')

# ================================================================================================ 0.1.22 SoulDrop (copied verbatim from
# tools/armory_0_1_22_patch.py - the change the 0.1.22 port build compiled into the 0.1.21 jar)
# ---------------------------------------------------------------------------------------------------------------- tokens + probes
rep('''          "BCH": "com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk",
''', '''          "BCH": "com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk",
          "ESEC": "com.hypixel.hytale.server.core.universe.world.chunk.section.EnvironmentSection",   # 0.1.22 (Hytale 0.7)
''')
rep('''                       (T["BCH"], "getComponentType", T["CTYPE"], []), (T["BCH"], "getEnvironment", "int", ["int", "int", "int"]),
''', '''                       # 0.1.22 (Hytale 0.7.0 release): BlockChunk.getEnvironment is gone - chunk Ref + section Ref + EnvironmentSection
                       (T["CHS"], "getChunkReference", T["REF"], ["long"]), (T["CHS"], "getChunkSectionReferenceAtBlock", T["REF"], ["int", "int", "int"]),
                       (T["CHS"], "getStore", T["ST"], []), (T["REF"], "isValid", "boolean", []),
                       (T["ESEC"], "getComponentType", T["CTYPE"], []), (T["ESEC"], "get", "int", ["int", "int", "int"]),
''')

# ---------------------------------------------------------------------------------------------------------------- SoulDrop.blockEnv + envOf
rep('''M(sdrop, r"""
public static String envOf(@CAC@ acc, @REF@ r, Object npc, @VEC@ p, @WLD@ w) {''', '''# 0.1.22 (Hytale 0.7): the environment index of a block - the chunk loaded (its Ref) -> y outside 0..319 = 0 (the old BlockChunk rule) ->
# the section Ref at the block -> its EnvironmentSection.get (WorldSupport.getEnvironmentId). MIN_VALUE = not loaded. Never loads anything.
M(sdrop, r"""
public static int blockEnv(@WLD@ w, int x, int y, int z) {
  if (w == null) return Integer.MIN_VALUE;
  try {
    @CHS@ cs = w.getChunkStore();
    @REF@ c = cs.getChunkReference(@CHU@.indexChunkFromBlock(x, z));
    if (c == null || !c.isValid()) return Integer.MIN_VALUE;
    if (y < 0 || y >= 320) return 0;
    @REF@ s = cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (s == null || !s.isValid()) return Integer.MIN_VALUE;
    Object e = cs.getStore().getComponent(s, @ESEC@.getComponentType());
    if (e instanceof @ESEC@) return ((@ESEC@) e).get(x, y, z);
  } catch (Throwable t) { }
  return Integer.MIN_VALUE;
}""")
M(sdrop, r"""
public static String envOf(@CAC@ acc, @REF@ r, Object npc, @VEC@ p, @WLD@ w) {''')
rep('''      Object c = w.getChunkStore().getChunkComponent(@CHU@.indexChunkFromBlock(x, z), @BCH@.getComponentType());
      if (c instanceof @BCH@) ei = ((@BCH@) c).getEnvironment(x, y, z);
''', '''      ei = blockEnv(w, x, y, z);
''')
assert ").getEnvironment(x, y, z)" not in s, "a BlockChunk.getEnvironment call is left"

# ================================================================================================ 0.7 ASSETS

# ---- (A1) the vanilla staffs lost the DEAD cast-check var Staff_Cast_Summon_Charged (0.7.0; SkyySkills 0.4.31 notes the same: it never
# mattered - the charged step interaction itself checks). Our 8 metal staffs drop every InteractionVar anyway (STAFF_TAP "quick") and the
# 2 vanilla Bo copies delete the cast vars they have, so nothing we ship changes; the build now expects the 0.7 var list.
rep('''STAFF_VARS = ["Staff_Cast_Summon_Charged", "Staff_Cast_Summon_Cost", "Staff_Cast_Summon_Launch", "Staff_Cast_Summon_Effect", "Staff_Cast_Summon_Fail",
              "Spear_Swing_Left_Damage", "Spear_Swing_Right_Damage", "Spear_Swing_Left_Effect", "Spear_Swing_Right_Effect"]
''', '''STAFF_VARS = ["Staff_Cast_Summon_Cost", "Staff_Cast_Summon_Launch", "Staff_Cast_Summon_Effect", "Staff_Cast_Summon_Fail",          # 0.1.23: Hytale 0.7
              "Spear_Swing_Left_Damage", "Spear_Swing_Right_Damage", "Spear_Swing_Left_Effect", "Spear_Swing_Right_Effect"]          # dropped the dead Staff_Cast_Summon_Charged var
''')
rep('''# Monk-Kit-Spec 8.3 (VERIFIED): the vanilla Bo staffs' hold = the vanilla staff cast (Staff_Cast_Summon_Charged, 50 Mana in their vars) - no traversal
assert VBO["InteractionVars"]["Staff_Cast_Summon_Charged"]["Interactions"][0]["Costs"] == {"Mana": 50}
''', '''# Monk-Kit-Spec 8.3 (VERIFIED): the vanilla Bo staffs' hold = the vanilla staff cast - no traversal. 0.1.23: Hytale 0.7 dropped the dead
# Staff_Cast_Summon_Charged var (its 50 Mana check); the spend var stays (50 Mana) - our Bo root casts nothing either way
assert "Staff_Cast_Summon_Charged" not in VBO["InteractionVars"] and VBO["InteractionVars"]["Staff_Cast_Summon_Cost"]["Interactions"][0]["StatModifiers"] == {"Mana": -50}
''')
rep('''assert sorted(_d.get("InteractionVars", {})) == sorted(STAFF_VARS), (_m, sorted(_d.get("InteractionVars", {})))
''', '''assert sorted(k for k in _d.get("InteractionVars", {}) if k != "Staff_Cast_Summon_Charged") == sorted(STAFF_VARS), (_m, sorted(_d.get("InteractionVars", {})))
    # 0.1.23 (Hytale 0.7): the dead check var is gone from 7 metal staffs, Thorium keeps a bare one (Parent only) - dropped in our copy either way
''')
rep('''assert BO_CAST_VARS == sorted(["Staff_Cast_Summon_Charged", "Staff_Cast_Summon_Cost", "Staff_Cast_Summon_Launch", "Staff_Cast_Summon_Effect",
                               "Staff_Cast_Summon_Fail"]), BO_CAST_VARS
''', '''assert BO_CAST_VARS == sorted(["Staff_Cast_Summon_Cost", "Staff_Cast_Summon_Launch", "Staff_Cast_Summon_Effect",          # 0.1.23: Hytale 0.7
                               "Staff_Cast_Summon_Fail"]), BO_CAST_VARS
''')

# ---- (A2) the corruption orb's head particle system was RENAMED Spectre_Void_Head -> Void_Spectre_Head (0.7.0 moved the Void Spectre set to
# Server/Particles/NPC/Void_Spectre/); same body (one Void_Sparks_Eyes spawner, the same rotation). Our blue copy keeps its id
# SkyyArmory_Orb_Head_Blue and is built from the 0.7 file (the same bytes as 0.1.22's copy - asset parity checks it).
rep('''PSYS = {"GreenOrbTrail": PS_GLOW, "GreenOrbImpact": PS_IMPACT, "Spectre_Void_Head": PS_HEAD}''',
    '''PSYS = {"GreenOrbTrail": PS_GLOW, "GreenOrbImpact": PS_IMPACT, "Void_Spectre_Head": PS_HEAD}          # 0.1.23: Hytale 0.7 renamed Spectre_Void_Head''')
rep('''assert [p["SystemId"] for p in VORBM["Particles"]] == ["GreenOrbTrail", "Spectre_Void_Head"] and''',
    '''assert [p["SystemId"] for p in VORBM["Particles"]] == ["GreenOrbTrail", "Void_Spectre_Head"] and''')

# ---- (A3) the vanilla wand tap (the Sword_Swing_*_Fast chain the Wood wand's "0" key ran before our quick shot replaced it) is faster in 0.7:
# 0.346 -> 0.329 s (Sword_Swing_Left_Fast prepare 0.171). It only feeds the "our taps are never faster than vanilla" check: OUR tested wand
# quick-shot cadence stays 0.35 s (0.1 + the 0.25 launch, Skyy-tested), still >= 0.329. Nothing we ship changes.
rep('''assert abs(VAN_TAP_W - 0.346) < 1e-9 and abs(VAN_TAP_S - 0.557) < 1e-9, (VAN_TAP_W, VAN_TAP_S)''',
    '''assert abs(VAN_TAP_W - 0.329) < 1e-9 and abs(VAN_TAP_S - 0.557) < 1e-9, (VAN_TAP_W, VAN_TAP_S)          # 0.1.23: Hytale 0.7 wand tap 0.346 -> 0.329 (ours stays 0.35)''')

# ---- (A4) the crossbow template's reload moved from Ability3 to Ability4 (0.7.0 key layout). Our 2 Wynn crossbows inherit the template
# (Parent) and never name a reload key, so they follow vanilla; the grapple keeps the right click (Secondary).
rep('''                               "Ability3": "Root_Common_StatAmmoReload_Entry"}, _xt["Interactions"]''',
    '''                               "Ability4": "Root_Common_StatAmmoReload_Entry"}, _xt["Interactions"]          # 0.1.23: Hytale 0.7 reload Ability3 -> Ability4''')

# ---- (A5) the vanilla Iron crossbow (the template of our 2 Wynn crossbows) changed in 0.7: combo bolt 27 -> 13, durability 120 -> 250, wear
# per hit 0.28 -> 0.17. Our tier numbers are OUR tested table (XSTAT: Copper 8 / 22 / 62, 90 durability; Onyxium 31 / 85 / 244, 260) - kept.
# The copy took the wear per hit from the vanilla file: kept at OUR tested 0.28 (the 0.6 value) so a Wynn crossbow wears exactly as before.
# The build still stops if the vanilla file moves again (the 0.7 numbers asserted); the "Copper sits below the 0.6 Iron" relation is kept
# against the 0.6 numbers it was tuned on (10 / 27 / 78, 120).
rep('''assert VXI["Parent"] == "Template_Weapon_Crossbow" and (_xd(_vxiv, "Standard_Projectile_Damage"), _xd(_vxiv, "Combo_Projectile_Damage"),
       _xd(_vxiv, "Signature_BigArrow_Damage"), VXI["MaxDurability"]) == (10, 27, 78, 120), "the vanilla Iron crossbow changed"''',
    '''assert VXI["Parent"] == "Template_Weapon_Crossbow" and (_xd(_vxiv, "Standard_Projectile_Damage"), _xd(_vxiv, "Combo_Projectile_Damage"),
       _xd(_vxiv, "Signature_BigArrow_Damage"), VXI["MaxDurability"], VXI["DurabilityLossOnHit"]) == (10, 13, 78, 250, 0.17), "the vanilla Iron crossbow changed"
XBOW_WEAR = 0.28          # 0.1.23: OUR tested wear per hit (the 0.6 Iron crossbow's); Hytale 0.7's Iron is 0.17 - not copied''')
rep('''    _it["MaxDurability"] = _st["dur"]
''', '''    _it["MaxDurability"] = _st["dur"]
    _it["DurabilityLossOnHit"] = XBOW_WEAR          # 0.1.23: keep the tested 0.28 (0.7 vanilla: 0.17)
''')

# ---- (A6) the Goblin_Ogre role is gone in 0.7.0 (the stunlock breakout's mini-boss list was checked against it). The default words are
# unchanged (a default change would need a migration); the checks now name the 0.7 roles instead: Goblin_Ogre out, the new 0.7 bosses the
# words already catch in (Dragon_Frost, Dungeon_Feastmaster_Boss, Goblin_Duke, Skeleton_Elite). NOT caught by the default words: the new
# Goblin_Gobliterator phases (no word in their names) - a server owner can add "Gobliterator" to stun.bossWords in Server Setup.
rep('''for _r in ("Goblin_Ogre", "Golem_Firesteel", "Golem_Crystal_Earth", "Golem_Crystal_Flame", "Golem_Crystal_Frost", "Golem_Crystal_Sand",
           "Golem_Crystal_Thunder", "Yeti", "Trork_Chieftain", "Hedera", "Rex_Cave", "Dragon_Fire", "Golem_Guardian_Void"):''',
    '''for _r in ("Golem_Firesteel", "Golem_Crystal_Earth", "Golem_Crystal_Flame", "Golem_Crystal_Frost", "Golem_Crystal_Sand",          # 0.1.23: Goblin_Ogre gone in 0.7
           "Golem_Crystal_Thunder", "Yeti", "Trork_Chieftain", "Hedera", "Rex_Cave", "Dragon_Fire", "Golem_Guardian_Void",
           "Dragon_Frost", "Dungeon_Feastmaster_Boss", "Goblin_Duke", "Skeleton_Elite"):          # 0.1.23: 0.7 bosses the words catch''', count=2)
rep('''for _r in ("Skeleton_Fighter", "Trork_Warrior", "Goblin_Scrapper", "Trork_Shaman", "Snapdragon"):
    assert _r in _stroles and not stun_boss_role(_r, STUN_DEF_WORDS), "stun.bossWords catches the plain mob %s" % _r''',
    '''for _r in ("Skeleton_Fighter", "Trork_Warrior", "Goblin_Scrapper", "Trork_Shaman", "Snapdragon"):
    assert _r in _stroles and not stun_boss_role(_r, STUN_DEF_WORDS), "stun.bossWords catches the plain mob %s" % _r
assert "Goblin_Ogre" not in _stroles and not stun_boss_role("Goblin_Gobliterator_Phase1", STUN_DEF_WORDS)          # 0.1.23: the 0.7 facts above''')

# ---- (A7) the vanilla sword / dagger swings are faster in 0.7 (sword chain 0.334 / 0.334 / 0.75 -> 0.318 / 0.318 / 0.625 s, dagger hit
# 0.207 -> 0.198 s; hit damages unchanged). The Monk weapons' damage (Bo 0.82 / gauntlets 0.90 / wraps 0.95 x the same-metal sword's DPS) and
# the gauntlet jab time (0.27 s) were tuned and tested on the 0.6 cadence: KEEP them - the DPS references use OUR tested 0.6 cadence (the
# 0.7 numbers are asserted, so a further vanilla move still stops the build). Result: every Bo / gauntlet / wrap number = 0.1.22's.
rep('''SWORD_T = (SWORD["Iron"]["t"][0] + SWORD["Iron"]["t"][1]) / 2.0
DAGGER_T = sum(dur(x_, item_resolved("Weapon_Daggers_Iron").get("InteractionVars") or {}) for x_ in _dgc["Next"]) / float(len(_dgc["Next"]))
GAUNT_T = round((SWORD_T + DAGGER_T) / 2.0, 2)
''', '''# 0.1.23 (Hytale 0.7): the vanilla cadence moved (asserted here); the Monk numbers keep OUR tested 0.6 cadence references below
SWORD_T07 = [round(x_, 9) for x_ in SWORD["Iron"]["t"]]
DAGGER_T07 = [round(dur(x_, item_resolved("Weapon_Daggers_Iron").get("InteractionVars") or {}), 9) for x_ in _dgc["Next"]]
assert all(SWORD[m_]["t"] == SWORD["Iron"]["t"] for m_ in SWORD) and SWORD_T07 == [0.318, 0.318, 0.625] and DAGGER_T07 == [0.198] * 4, \\
    ("the vanilla sword / dagger cadence moved again - re-check the Monk numbers", SWORD_T07, DAGGER_T07)
SWORD_TESTED_T = [0.334, 0.334, 0.75]          # the 0.6 vanilla sword chain the Monk DPS shares were tuned + tested on (Skyy-tested)
DAGGER_TESTED_T = 0.207                        # the 0.6 vanilla dagger hit (the gauntlet jab = halfway: 0.27 s)
for _m in SWORD:
    SWORD[_m] = dict(hits=SWORD[_m]["hits"], t=list(SWORD_TESTED_T), dps=sum(SWORD[_m]["hits"]) / sum(SWORD_TESTED_T))
SWORD_T = (SWORD["Iron"]["t"][0] + SWORD["Iron"]["t"][1]) / 2.0
DAGGER_T = DAGGER_TESTED_T
GAUNT_T = round((SWORD_T + DAGGER_T) / 2.0, 2)
''')

# ---- (A8) NEW 0.7 dagger Weapon_Daggers_Void_Crystal (a goblin dagger) names NO damage vars (it runs the template's defaults). It is a normal
# vanilla dagger (the vanilla primary root), so Shadow Step reaches it like every other dagger (the rule "every dagger"); the backstab survey
# reads only daggers that carry the damage vars (all 16 others - the same x1.5 result).
rep('''for _di in SS_REACH:
    _dv = item_resolved(_di).get("InteractionVars") or {}
    _sig_calc = 0
''', '''SS_NOVARS = []          # 0.1.23: Hytale 0.7's Weapon_Daggers_Void_Crystal carries no damage vars (template defaults)
for _di in SS_REACH:
    _dv = item_resolved(_di).get("InteractionVars") or {}
    if not [k_ for k_ in _dv if k_.endswith("_Damage")]:
        SS_NOVARS.append(_di)
        continue
    _sig_calc = 0
''')
rep('''assert len(_bx) >= 50 and all(1.45 <= x <= 1.56 for x in _bx), (len(_bx), min(_bx), max(_bx))''',
    '''assert len(_bx) >= 50 and all(1.45 <= x <= 1.56 for x in _bx), (len(_bx), min(_bx), max(_bx))
assert SS_NOVARS == ["Weapon_Daggers_Void_Crystal"], SS_NOVARS          # 0.1.23: the one 0.7 dagger without vars''')

# ---- (A9) 0.7 gave the vanilla dagger Charging step Rules {InterruptedBy: [Secondary]} (a right click cancels the hold). Our fist hold is
# OUR file (its tested shape: no Rules) - the shape check accepts the new key, the fist files do not copy it.
rep('''assert _vdgp["Type"] == "Charging" and _vdgp.get("DisplayProgress") is False and sorted(_vdgp) == ["DisplayProgress", "Next", "Type"], _vdgp''',
    '''assert _vdgp["Type"] == "Charging" and _vdgp.get("DisplayProgress") is False and sorted(_vdgp) == ["DisplayProgress", "Next", "Rules", "Type"] \\
    and _vdgp["Rules"] == {"InterruptedBy": ["Secondary"]}, _vdgp          # 0.1.23: Hytale 0.7 added Rules (not copied into our fist hold)''')

# ---- (A10) ASSET PARITY vs the 0.1.22 jar (the 0.6-built files Skyy tested; harness P): after (A1)-(A9) only 2 things differ, both 0.7
# vanilla number moves our files copied:
#   - the vanilla Sword set's GuardBash plays at Speed 1.15 in 0.7 (0.6: none = 1.0); our Staff / Spellbook / Wand sets copy Sword's Guard +
#     GuardBash -> KEEP the tested 1.0 (the Speed key dropped from our copies).
#   - the dagger Pounce charge (the ONE vanilla dagger interaction we override - Shadow Step's hold) slows you less while held: Horizontal
#     SpeedMultiplier 0.5 -> 0.85 -> KEEP the tested 0.5. Its NEW 0.7 field Rules {InterruptedBy: [Secondary]} (a right click cancels the
#     hold) is DROPPED too (FIX ROUND, critic: research/Shadow-Step-Spec.md - "right-click stays BLOCK"; a block must not cancel the
#     Shadow Step charge; untested feel change). The override = the 0.1.22 tested file byte for byte; matches our fist hold (A9, no Rules).
rep('''        assert _k not in ANIMS[_a]["Animations"], (_a, _k)
        ANIMS[_a]["Animations"][_k] = json.loads(json.dumps(_pose[_k]))
''', '''        assert _k not in ANIMS[_a]["Animations"], (_a, _k)
        ANIMS[_a]["Animations"][_k] = json.loads(json.dumps(_pose[_k]))
        if _k == "GuardBash":          # 0.1.23: Hytale 0.7 plays Sword's GuardBash at Speed 1.15 - ours keep the tested 1.0
            assert ANIMS[_a]["Animations"][_k].pop("Speed", None) == 1.15, (_a, "the vanilla GuardBash speed moved again")
''')
rep('''SS_POUNCE_JSON["AllowIndefiniteHold"] = True
assert dict((k, v) for k, v in SS_POUNCE_JSON.items() if k not in ("Next", "AllowIndefiniteHold")) == dict(
    (k, v) for k, v in VPOUNCE.items() if k not in ("Next", "AllowIndefiniteHold")) and sorted(SS_POUNCE_JSON["Next"]) == ["0", "0.4"]''',
    '''SS_POUNCE_JSON["AllowIndefiniteHold"] = True
# 0.1.23 (Hytale 0.7): the vanilla Pounce hold slows you less (0.5 -> 0.85) - Shadow Step keeps the tested 0.5; the new 0.7 Rules (a right
# click / block cancels the hold) are NOT copied (FIX ROUND: Shadow-Step-Spec "right-click stays BLOCK" - the 0.1.22 tested hold)
assert VPOUNCE["HorizontalSpeedMultiplier"] == 0.85 and VPOUNCE["Rules"] == {"InterruptedBy": ["Secondary"]}, VPOUNCE
SS_POUNCE_JSON["HorizontalSpeedMultiplier"] = 0.5
assert SS_POUNCE_JSON.pop("Rules") == {"InterruptedBy": ["Secondary"]} and "Rules" not in SS_POUNCE_JSON
assert dict((k, v) for k, v in SS_POUNCE_JSON.items() if k not in ("Next", "AllowIndefiniteHold", "HorizontalSpeedMultiplier")) == dict(
    (k, v) for k, v in VPOUNCE.items() if k not in ("Next", "AllowIndefiniteHold", "HorizontalSpeedMultiplier", "Rules")) and sorted(SS_POUNCE_JSON["Next"]) == ["0", "0.4"]''')

# ================================================================================================ 0.7 ENGINE PROBES (build-time evidence only)
# ---- (E1) ProjectileModule.spawnProjectile(UUID, Long, Ref, CommandBuffer, ProjectileConfig, Vector3d, Vector3d) is gone in 0.7: the same
# call takes a trailing long now (+ float / float variants). Our Java never calls it (the probe is evidence for the grapple's SPAWN rule:
# the vanilla launch adds the projectile with AddReason.SPAWN) - the probe names the 0.7 overload; the bytecode shape check is unchanged.
rep('''     ["java.util.UUID", "java.lang.Long", T["REF"], T["CB"], "com.hypixel.hytale.server.core.modules.projectile.config.ProjectileConfig", T["VEC"], T["VEC"]]),''',
    '''     ["java.util.UUID", "java.lang.Long", T["REF"], T["CB"], "com.hypixel.hytale.server.core.modules.projectile.config.ProjectileConfig", T["VEC"], T["VEC"], "long"]),          # 0.1.23: Hytale 0.7 + long''')

# ---- (E2) StandardPhysicsTickSystem#tick has a THIRD onImpact call in 0.7: a PIERCING projectile (the new PierceProjectile component,
# PierceProjectile.markHit) reports each entity it passes without going INACTIVE. Our grapple bolt has no PierceProjectile (its config
# names no Pierce), so it still takes the two old paths: an entity hit = INACTIVE + onImpact(entity), a block = RESTING + rest + onImpact(null).
rep('''assert _tk.count("onImpact") == 2 and ".RESTING" in _tk and ".INACTIVE" in _tk and "rest" in _tk and "getImpactConsumer" in _tk, "StandardPhysicsTickSystem#tick changed"''',
    '''assert _tk.count("onImpact") == 3 and "markHit" in _tk and _tk.index("markHit") < _tk.index("onImpact") < len(_tk) - 1 - _tk[::-1].index(".INACTIVE") \\
    and ".RESTING" in _tk and ".INACTIVE" in _tk and "rest" in _tk and "getImpactConsumer" in _tk, "StandardPhysicsTickSystem#tick changed"          # 0.1.23: + the 0.7 pierce path''')
rep('''assert not az_has("pcfg", _i) and not az_has("efx", _i) and not az_has("model", _i) and not az_has("trail", _i) and _i not in _IDX["psys"], _i''',
    '''assert not az_has("pcfg", _i) and not az_has("efx", _i) and not az_has("model", _i) and not az_has("trail", _i) and _i not in _IDX["psys"], _i
assert "Pierce" not in json.dumps(_pb) and "Pierce" not in json.dumps(_pxb), "0.1.23: the arrow configs our bolt copies have no Pierce (the 0.7 pierce path stays off)"''')

# ================================================================================================ LAG (TravTick gating etc.)
# research/Code-Structure-Audit.md finding 19 (Armory, TravTick) + the Armory sub-audit + the pack-wide bridge lock pattern.

# ---- (L1) lock-free bridge (pack-wide pattern 1; the tools/skyycfg.py kit's CfgRows already has it): ArmoryDefs.bridge + ArmoryTree.bridge
# cache the shared map in a static volatile after the first call; the first call creates it exactly like before, under the same monitor.
_OLD_BRIDGE = r'''public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")'''
_NEW_BRIDGE = r'''public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""")
# 0.1.23 (Code-Structure-Audit pack-wide pattern 1): lock-free after the first call (the skyycfg kit's CfgRows.bridge way)
M(@CLS@, r"""
public static java.util.Map bridge() {
  java.util.Map m = BRIDGE;
  if (m != null) return m;
  synchronized (java.lang.System.class) { m = bridge0(); }
  BRIDGE = m;
  return m;
}""")'''
for _cls in ("dfs", "atree"):
    rep('M(%s, r"""\n' % _cls + _OLD_BRIDGE, 'F(%s, "public static volatile java.util.Map BRIDGE;")          # 0.1.23\nM(%s, r"""\n' % (_cls, _cls)
        + _NEW_BRIDGE.replace("@CLS@", _cls))
assert "synchronized (java.lang.System.class) {\n    Object o" not in s, "a locking bridge() is left"

# ---- (L2) ArmoryTree.gen string churn: "profile:epoch:" + u.toString() was built on every call (Soul / Wings / Kunai every tick of a
# player with state). The key string is made once per player (EKEY, u -> String; cleared with the tree cache) + ArmoryTree.ustr(u) (u ->
# u.toString(), the same cache) for the Monk / Soul bridge keys below.
rep('''          "public static volatile long SWITCHES = 0L;"):
    F(atree, f)''', '''          "public static volatile long SWITCHES = 0L;",
          # 0.1.23 (Armory sub-audit): u -> "profile:epoch:<uuid>" and u -> u.toString(), made once per player (no string churn per tick)
          "public static final java.util.concurrent.ConcurrentHashMap EKEY = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap USTR = new java.util.concurrent.ConcurrentHashMap();"):
    F(atree, f)''')
rep('''M(atree, r"""
public static long gen(java.util.UUID u) {
  if (u == null) return 0L;
  Object g = GEN.get(u);
  long gv = g instanceof Long ? ((Long) g).longValue() : 0L;
  Object e = null;
  try { e = bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { e = null; }''', '''# 0.1.23: the player's uuid text + epoch key, made once (EKEY / USTR; cleared with clear(), capped at 4096 players)
M(atree, r"""
public static String ustr(java.util.UUID u) {
  if (u == null) return "null";
  Object o = USTR.get(u);
  if (o instanceof String) return (String) o;
  String v = u.toString();
  if (USTR.size() > 4096) USTR.clear();
  USTR.put(u, v);
  return v;
}""")
M(atree, r"""
public static String ekey(java.util.UUID u) {
  Object o = EKEY.get(u);
  if (o instanceof String) return (String) o;
  String v = "profile:epoch:" + ustr(u);
  if (EKEY.size() > 4096) EKEY.clear();
  EKEY.put(u, v);
  return v;
}""")
M(atree, r"""
public static long gen(java.util.UUID u) {
  if (u == null) return 0L;
  Object g = GEN.get(u);
  long gv = g instanceof Long ? ((Long) g).longValue() : 0L;
  Object e = null;
  try { e = bridge().get(ekey(u)); } catch (Throwable t) { e = null; }          // 0.1.23: the cached key (was a new string per call)''')
rep('''public static void clear() {
  CACHE.clear();
  ECHO.clear();
  EPOCH.clear();
  GEN.clear();
}''', '''public static void clear() {
  CACHE.clear();
  ECHO.clear();
  EPOCH.clear();
  GEN.clear();
  EKEY.clear();          // 0.1.23
  USTR.clear();
}''')

# ---- (L3) Monk.flag wrote armory:monkmove:<uuid> on EVERY active tick of a Monk move (a new Long + a key string each tick). Now the value is
# the "until" time rounded UP to 250 ms and written only when that rounded value moves (about 4 writes a second instead of 30): the flag
# never ends earlier than before (still >= 0.5 s after the last active tick, at most 0.25 s later). SkyySkills reads it as before (Long ms).
rep('''          "public static final java.util.concurrent.ConcurrentHashMap FLAGGED = new java.util.concurrent.ConcurrentHashMap();",''',
    '''          "public static final java.util.concurrent.ConcurrentHashMap FLAGGED = new java.util.concurrent.ConcurrentHashMap();",          # 0.1.23: u -> Long the value written
          "public static final long FLAG_STEP = 250L;", "public static volatile long FLAG_WRITES = 0L;", "public static volatile long FLAG_SKIPS = 0L;",          # 0.1.23''')
rep('''public static void flag(java.util.UUID u, long until) {
  if (u == null) return;
  try {
    @PKG@.ArmoryDefs.bridge().put(KEY + u.toString(), Long.valueOf(until));
    FLAGGED.put(u, Boolean.TRUE);
  } catch (Throwable t) { }
}''', '''public static long flagBucket(long until) { return ((until + FLAG_STEP - 1L) / FLAG_STEP) * FLAG_STEP; }''' + '''""")
M(monk, r"""
public static void flag(java.util.UUID u, long until) {
  if (u == null) return;
  long b = flagBucket(until);          // 0.1.23: written only when the rounded-up time moves (never earlier than until)
  Object last = FLAGGED.get(u);
  if (last instanceof Long && ((Long) last).longValue() >= b) { FLAG_SKIPS = FLAG_SKIPS + 1L; return; }
  try {
    @PKG@.ArmoryDefs.bridge().put(KEY + @PKG@.ArmoryTree.ustr(u), Long.valueOf(b));
    FLAGGED.put(u, Long.valueOf(b));
    FLAG_WRITES = FLAG_WRITES + 1L;
  } catch (Throwable t) { }
}''')

# ---- (L4) Soul.publish wrote armory:soul:<uuid> twice a second while stored healing exists, even when the rounded value had not changed
# (e.g. a paused fade): now only a CHANGED value is written (PUBV = u -> the Double last written), and a removal only when one was written.
rep('''          "public static final long PUB_MS = 500L;", "public static final int MAX_BINDS = 32;", "public static final String KEY = \\"armory:soul:\\";",''',
    '''          "public static final long PUB_MS = 500L;", "public static final int MAX_BINDS = 32;", "public static final String KEY = \\"armory:soul:\\";",
          # 0.1.23 (Armory sub-audit): u -> the Double last written to armory:soul:<uuid> (publish writes only a change); the counters
          "public static final java.util.concurrent.ConcurrentHashMap PUBV = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile long PUB_WRITES = 0L;", "public static volatile long PUB_SKIPS = 0L;",''')
rep('''public static void publish(java.util.UUID u, double hp) {
  try {
    java.util.Map b = @PKG@.ArmoryDefs.bridge();
    if (hp > 0.005) b.put(KEY + u.toString(), Double.valueOf(Math.floor(hp * 100.0 + 0.5) / 100.0));
    else b.remove(KEY + u.toString());
  } catch (Throwable t) { }
}''', '''public static void publish(java.util.UUID u, double hp) {
  if (u == null) return;
  try {
    java.util.Map b = @PKG@.ArmoryDefs.bridge();
    if (hp > 0.005) {
      Double v = Double.valueOf(Math.floor(hp * 100.0 + 0.5) / 100.0);
      if (v.equals(PUBV.get(u))) { PUB_SKIPS = PUB_SKIPS + 1L; return; }          // 0.1.23: unchanged - no bridge write
      b.put(KEY + @PKG@.ArmoryTree.ustr(u), v);
      PUBV.put(u, v);
      PUB_WRITES = PUB_WRITES + 1L;
    } else if (PUBV.remove(u) != null) {
      b.remove(KEY + @PKG@.ArmoryTree.ustr(u));
      PUB_WRITES = PUB_WRITES + 1L;
    }
  } catch (Throwable t) { }
}''')
rep('''  POOL.clear();
  LATCH.clear();
  SEEN.clear();
}''', '''  POOL.clear();
  LATCH.clear();
  SEEN.clear();
  java.util.Iterator pv = PUBV.keySet().iterator();          // 0.1.23: a value still written without a pool entry goes too
  while (pv.hasNext()) { Object k = pv.next(); try { @PKG@.ArmoryDefs.bridge().remove(KEY + String.valueOf(k)); } catch (Throwable t) { } }
  PUBV.clear();
}''')

# ---- (L5) ArmoryCheck re-scheduled itself every 30 s FOREVER after the pack check (a Mana-check epoch read each time). Now it stops once the
# pack check is done AND the Mana check has run with SkyySkills' settings readable (or is off, or gave up after PACK_MAX tries 10 s apart).
# FIX ROUND (critics): the Mana advisory (armory:check + its log line) refreshes again after a SkyySkills / SkyyGear / Armory Mana-row change
# (the spec's "whenever SkyySkills' or our settings change"): the done ArmoryCheck PARKS in ArmoryHold.WATCHER; the gate's prune pass (every
# 2048 gate calls, players online) hands it to the scheduler at most every 30 s; that run re-reads the 3 epochs and parks again. No chain.
rep('''          "public static final int PACK_MAX = 6;", "public int gen;"):
    F(chk, f)''', '''          "public static final int PACK_MAX = 6;", "public int gen;",
          # 0.1.23 (Armory sub-audit): the Mana check's last level ("info" / "warn" / "skip"), its tries, DONE = no more re-scheduling
          "public static volatile String MANA_LVL = \\"\\";", "public static volatile int MANA_TRIES = 0;", "public static volatile boolean DONE = false;",
          "public static volatile int RUNS = 0;", "public static volatile int WATCHES = 0;"):          # FIX ROUND: parked refresh runs
    F(chk, f)''')
rep('''  String[] r = manaCheck();
  MANA_LAST = r[1];''', '''  String[] r = manaCheck();
  MANA_LVL = r[0];          // 0.1.23
  MANA_LAST = r[1];''')
rep('''M(chk, r"""
public void run() {
  if (STOP || this.gen != GEN) return;
  try {''', '''# 0.1.23: true = nothing left to watch (the Mana check is off, ran with SkyySkills readable, or gave up after PACK_MAX tries)
M(chk, r"""
public static boolean manaSettled() {
  if (!@PKG@.ArmoryCfg.CHECK_ON) return true;
  if (MANA_LVL.length() > 0 && !"skip".equals(MANA_LVL)) return true;
  MANA_TRIES = MANA_TRIES + 1;
  return MANA_TRIES >= PACK_MAX;
}""")
M(chk, r"""
public void run() {
  if (STOP || this.gen != GEN) return;
  if (DONE) {          // FIX ROUND: a parked refresh (handed over by ArmoryHold.watch): the epochs only, the check when one moved; park again
    WATCHES = WATCHES + 1;
    try { manaTick(false); } catch (Throwable tw) { @PKG@.ArmoryLog.warnOnce("checkw:" + tw.getClass().getName(), "Mana check refresh failed: " + tw); }
    if (!STOP && this.gen == GEN) @PKG@.ArmoryHold.WATCHER = this;
    return;
  }
  RUNS = RUNS + 1;
  try {''')
rep('''  if (!STOP && this.gen == GEN) schedule(this, PACK_DONE ? WATCH_S : RETRY_S);
}''', '''  if (STOP || this.gen != GEN) return;
  if (PACK_DONE && manaSettled()) { DONE = true; @PKG@.ArmoryHold.WATCHER = this; return; }          // 0.1.23: done - no more re-scheduling
  // FIX ROUND: parked - the gate's prune pass hands it back to the scheduler at most every 30 s while players are online (Mana-row changes)
  schedule(this, RETRY_S);
}''')
rep('''  TRIES = 0;
  PACK_DONE = false;
  MANA_SIG = "";''', '''  TRIES = 0;
  PACK_DONE = false;
  MANA_SIG = "";
  MANA_LVL = "";          // 0.1.23
  MANA_TRIES = 0;
  DONE = false;''')

# ---- (L6) Grapple: the sweep trigger split out (sweepTick) so an idle player's skipped tick still drives it while any grapple record
# exists; busy(u) = this player has a grapple record
rep('''M(grap, r"""
public static void tickPlayer(@REF@ r, @ST@ st, @CB@ buf) {
  if (r == null) return;
  SWEEP_N = SWEEP_N + 1;
  if (SWEEP_N >= SWEEP_EVERY) {
    SWEEP_N = 0;
    try { sweep(st, buf, System.currentTimeMillis()); } catch (Throwable ts) { warn("sweep", "the grapple sweep failed (" + ts + ")"); }
  }
''', '''# 0.1.23: the sweep trigger (every SWEEP_EVERY player ticks) + busy(u) + idle (a gated-off player's tick: only the sweep, only while any
# grapple record / grace / cooldown entry exists)
M(grap, r"""
public static void sweepTick(@ST@ st, @CB@ buf) {
  SWEEP_N = SWEEP_N + 1;
  if (SWEEP_N >= SWEEP_EVERY) {
    SWEEP_N = 0;
    try { sweep(st, buf, System.currentTimeMillis()); } catch (Throwable ts) { warn("sweep", "the grapple sweep failed (" + ts + ")"); }
  }
}""")
M(grap, "public static boolean busy(java.util.UUID u) { return u != null && STATES.containsKey(u); }")
M(grap, r"""
public static void idle(@ST@ st, @CB@ buf) {
  if (!STATES.isEmpty() || !GRACE.isEmpty() || !LASTEND.isEmpty()) sweepTick(st, buf);
}""")
M(grap, r"""
public static void tickPlayer(@REF@ r, @ST@ st, @CB@ buf) {
  if (r == null) return;
  sweepTick(st, buf);          // 0.1.23: split out (same rule)
''')

# ---- (L7) Soul: the same split (sweepTick, busy, idle)
rep('''  long now = now();
  @PKG@.SoulState s = (@PKG@.SoulState) STATES.get(u);
  if (s != null || POOL.containsKey(u) || LATCH.containsKey(u)) SEEN.put(u, Long.valueOf(now));          // FIX ROUND: the sweep's "still here"
  if (now - SWEEP_AT >= SWEEP_MS) { SWEEP_AT = now; try { sweep(now); } catch (Throwable ts) { warn("sweep", "the soul sweep failed (" + ts + ")"); } }
''', '''  long now = now();
  @PKG@.SoulState s = (@PKG@.SoulState) STATES.get(u);
  if (s != null || POOL.containsKey(u) || LATCH.containsKey(u)) SEEN.put(u, Long.valueOf(now));          // FIX ROUND: the sweep's "still here"
  sweepTick(now);          // 0.1.23: split out (same rule)
''')
rep('''# TravTick, every tick of every player (world thread): the release reasons first (off, world change, death, profile switch, the weapon left
# the hand, let go), then the hold (class lock at its start)
M(soul, r"""''', '''# 0.1.23: the sweep trigger (every SWEEP_MS) + busy(u) (a Binding, stored healing or the out-of-Mana latch) + idle (a gated-off player's tick:
# only the sweep, only while any soul record exists)
M(soul, r"""
public static void sweepTick(long now) {
  if (now - SWEEP_AT >= SWEEP_MS) { SWEEP_AT = now; try { sweep(now); } catch (Throwable ts) { warn("sweep", "the soul sweep failed (" + ts + ")"); } }
}""")
M(soul, r"""
public static boolean busy(java.util.UUID u) {
  return u != null && (STATES.containsKey(u) || POOL.containsKey(u) || LATCH.containsKey(u));
}""")
M(soul, r"""
public static void idle() {
  if (!STATES.isEmpty() || !POOL.isEmpty() || !LATCH.isEmpty() || !SEEN.isEmpty()) sweepTick(now());
}""")
# TravTick, every tick of every player (world thread): the release reasons first (off, world change, death, profile switch, the weapon left
# the hand, let go), then the hold (class lock at its start)
M(soul, r"""''')

# ---- (L8) THE GATE (finding 19): ArmoryHold keeps, per player body (Ref), what that player holds - the hand item read ONCE and then only
# when the hotbar / active slot / inventory changes (ArmorySlotSys on InventorySetActiveSlotEvent, ArmoryInvSys on InventoryChangeEvent: they
# only mark the Ref; TravTick re-reads the hand on that player's next tick, world thread) plus a safety re-read every RECHECK (64) ticks.
# TravTick runs Grapple.tickPlayer only for a player holding a crossbow / with a grapple record, and Soul.tickPlayer only for a player
# holding a Soul Orb / Cage / with a Binding, stored healing or the latch. A NEW body (join, world switch, respawn = a new Ref) runs every
# check for its first WARM (30) ticks = the stale-effect cleanup (a left-over grapple OUT / CLICK effect after a restart / relog) happens
# once there, not every tick forever. Unknown uuid / a failed gate = every check runs (the old way). If either event system could not be
# registered the hand is re-read every tick (the old cost, the old behaviour).
rep('''C(ttick, "public TravTick() { super(); }")''', '''# ---------------------------------------------------------------- 0.1.23 ArmoryHold: the held-weapon gate for TravTick (finding 19)
hrec = pool.makeClass(PKG + ".ArmoryHoldRec")
hold = pool.makeClass(PKG + ".ArmoryHold")
slotsys = pool.makeClass(PKG + ".ArmorySlotSys", pool.get(T["EES"]))
invsys = pool.makeClass(PKG + ".ArmoryInvSys", pool.get(T["EES"]))
ALL += [hrec, hold, slotsys, invsys]
for f in ("public java.util.UUID u;", "public String item;", "public boolean xbow;", "public boolean soul;", "public int warm;", "public int ticks;"):
    F(hrec, f)
C(hrec, "public ArmoryHoldRec() { }")
for f in ("public static final java.util.concurrent.ConcurrentHashMap REC = new java.util.concurrent.ConcurrentHashMap();",          # Ref -> ArmoryHoldRec
          "public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();",        # Ref -> TRUE (re-read)
          "public static final int WARM = 30;", "public static final int RECHECK = 64;", "public static final int PRUNE_EVERY = 2048;",
          "public static volatile int CALLS = 0;", "public static volatile boolean SYS_SLOT = false;", "public static volatile boolean SYS_INV = false;",
          "public static volatile long READS = 0L;", "public static volatile long NEW_BODIES = 0L;", "public static volatile long EVENTS = 0L;",
          "public static volatile long PRUNED = 0L;",
          # FIX ROUND: the parked ArmoryCheck (a Runnable, set when its start checks are done) + when it last ran (the Mana advisory refresh)
          "public static volatile Runnable WATCHER = null;", "public static volatile long WATCH_AT = 0L;", "public static final long WATCH_MS = 30000L;",
          "public static volatile long WATCH_RUNS = 0L;",
          # per-tick counters: plain fields (no volatile write per player per tick; read only for the info / harness)
          "public static long G_RUNS = 0L;", "public static long G_SKIPS = 0L;", "public static long S_RUNS = 0L;", "public static long S_SKIPS = 0L;"):
    F(hold, f)
M(hold, "public static void warn(String k, String m) { @PKG@.ArmoryLog.warnOnce(\\"hold:\\" + k, m); }")
M(hold, r"""
public static Class cls(String n) {
  try { return Class.forName(n); } catch (Throwable t) { return null; }
}""")
# FIX ROUND (critic): the SAME rule as Grapple.onShot ("an item whose id names a crossbow") - another pack's crossbow on the shared
# Root_Weapon_Crossbow_Secondary_Guard (e.g. VC_Weapon_Crossbow_Void) is gated in like ours (only read on a hand read, never per tick)
M(hold, "public static boolean xbowItem(String it) { return it != null && it.toLowerCase().indexOf(\\"crossbow\\") >= 0; }")
# an inventory / active-slot event: mark the body (any thread the store runs on; the hand is read on its next TravTick)
M(hold, r"""
public static void dirty(@REF@ r) {
  if (r == null) return;
  DIRTY.put(r, Boolean.TRUE);
  EVENTS = EVENTS + 1L;
}""")
M(hold, r"""
public static void read(@CAC@ acc, @REF@ r, @PKG@.ArmoryHoldRec h) {
  String it = @PKG@.Leap.hand(acc, r, h.u);
  h.item = it;
  h.xbow = xbowItem(it);
  h.soul = @PKG@.Soul.tierOf(it) >= 0;
  h.ticks = 0;
  READS = READS + 1L;
}""")
# bodies that are gone (quit, world switch, death -> a new Ref) are dropped every PRUNE_EVERY gate calls
M(hold, r"""
public static int prune() {
  int n = 0;
  java.util.Iterator it = REC.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    boolean gone = true;
    try { gone = !(k instanceof @REF@) || !((@REF@) k).isValid(); } catch (Throwable t) { gone = true; }
    if (gone) { it.remove(); n++; }
  }
  java.util.Iterator id = DIRTY.keySet().iterator();
  while (id.hasNext()) {
    Object k = id.next();
    boolean gone = true;
    try { gone = !(k instanceof @REF@) || !((@REF@) k).isValid(); } catch (Throwable t) { gone = true; }
    if (gone) id.remove();
  }
  PRUNED = PRUNED + (long) n;
  return n;
}""")
# FIX ROUND: hand the parked ArmoryCheck to the scheduler (never runs it here - world thread); at most every WATCH_MS; true = handed over
M(hold, r"""
public static boolean watch(long now) {
  Runnable w = WATCHER;
  if (w == null || now - WATCH_AT < WATCH_MS) return false;
  WATCHER = null;
  WATCH_AT = now;
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(w, 0L, java.util.concurrent.TimeUnit.SECONDS); }
  catch (Throwable t) { WATCHER = w; warn("watch", "the Mana check refresh could not be scheduled (" + t + ")"); return false; }
  WATCH_RUNS = WATCH_RUNS + 1L;
  return true;
}""")
# the gate record of this body (world thread, TravTick): new = read now + WARM full ticks; marked / RECHECK ticks old = read again
M(hold, r"""
public static @PKG@.ArmoryHoldRec rec(@REF@ r, @CB@ cb) {
  if (r == null) return null;
  CALLS = CALLS + 1;
  if (CALLS >= PRUNE_EVERY) { CALLS = 0; prune(); watch(System.currentTimeMillis()); }          // FIX ROUND: + the Mana advisory refresh
  Object o = REC.get(r);
  if (!(o instanceof @PKG@.ArmoryHoldRec)) {
    @PKG@.ArmoryHoldRec n = new @PKG@.ArmoryHoldRec();
    n.u = @PKG@.Leap.uuidOf(cb, r);
    n.warm = WARM;
    DIRTY.remove(r);
    read(cb, r, n);
    REC.put(r, n);
    NEW_BODIES = NEW_BODIES + 1L;
    return n;
  }
  @PKG@.ArmoryHoldRec h = (@PKG@.ArmoryHoldRec) o;
  if (h.warm > 0) h.warm = h.warm - 1;
  if (h.u == null) h.u = @PKG@.Leap.uuidOf(cb, r);
  h.ticks = h.ticks + 1;
  int every = (SYS_SLOT && SYS_INV) ? RECHECK : 1;          // no event system = the old per-tick read
  if (DIRTY.remove(r) != null || h.ticks >= every) read(cb, r, h);
  return h;
}""")
M(hold, r"""
public static boolean runGrapple(@PKG@.ArmoryHoldRec h) {
  boolean run = h == null || h.u == null || h.warm > 0 || h.xbow || @PKG@.Grapple.busy(h.u);
  if (run) G_RUNS = G_RUNS + 1L; else G_SKIPS = G_SKIPS + 1L;
  return run;
}""")
M(hold, r"""
public static boolean runSoul(@PKG@.ArmoryHoldRec h) {
  boolean run = h == null || h.u == null || h.warm > 0 || h.soul || @PKG@.Soul.busy(h.u);
  if (run) S_RUNS = S_RUNS + 1L; else S_SKIPS = S_SKIPS + 1L;
  return run;
}""")
M(hold, "public static void clear() { REC.clear(); DIRTY.clear(); WATCHER = null; WATCH_AT = 0L; }")
M(hold, r"""
public static String text() {
  return "held-weapon gate: " + REC.size() + " bodies, " + READS + " hand reads (" + NEW_BODIES + " new bodies, " + EVENTS + " inventory / slot events), grapple ticks "
    + G_RUNS + " run / " + G_SKIPS + " skipped, soul ticks " + S_RUNS + " run / " + S_SKIPS + " skipped" + (SYS_SLOT && SYS_INV ? "" : " (event systems missing: hand read every tick)");
}""")
for _sys, _sn, _ev in ((slotsys, "ArmorySlotSys", "ISAS"), (invsys, "ArmoryInvSys", "IVCE")):
    C(_sys, "public %s() { super(@PKG@.ArmoryHold.cls(\\"%s\\")); }" % (_sn, T[_ev]))
    M(_sys, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
    M(_sys, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try { if (chunk != null) @PKG@.ArmoryHold.dirty(chunk.getReferenceTo(idx)); }
  catch (Throwable t) { @PKG@.ArmoryHold.warn("ev:" + t.getClass().getName(), "the held-weapon event failed (" + t + ")"); }
}""")
C(ttick, "public TravTick() { super(); }")''')

# ---- (L9) TravTick.tick: the gate in front of Grapple + Soul; the Ref read once per player tick
rep('''  if (chunk != null) {          // 0.1.2: the crossbow grapple, per player (world thread)
    try { @PKG@.Grapple.tickPlayer(chunk.getReferenceTo(idx), store, cb); }
    catch (Throwable tg) { @PKG@.Grapple.warn("tick:" + tg.getClass().getName(), "grapple tick failed (" + tg + ")"); }
    try { @PKG@.Leap.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.3: the leap's rise / hang / shot
    catch (Throwable tl) { @PKG@.Leap.warn("tick:" + tl.getClass().getName(), "leap tick failed (" + tl + ")"); }
    try { @PKG@.Levitate.tickPlayer(chunk.getReferenceTo(idx), store, cb); }      // 0.1.6: the spellbook Levitate (rise / hover / float)
    catch (Throwable tv) { @PKG@.Levitate.warn("tick:" + tv.getClass().getName(), "Levitate tick failed (" + tv + ")"); }
    try { @PKG@.Kunai.tickPlayer(chunk.getReferenceTo(idx), store, cb); }         // 0.1.6: the kunai flight / landing / return knockback
    catch (Throwable tk) { @PKG@.Kunai.warn("tick:" + tk.getClass().getName(), "kunai tick failed (" + tk + ")"); }
    try { @PKG@.Monk.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.12: the Monk moves (vault, bounds, rise, plunge, flowing fall)
    catch (Throwable tm) { @PKG@.Monk.warn("tick:" + tm.getClass().getName(), "Monk move tick failed (" + tm + ")"); }
    try { @PKG@.Soul.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.19: the Soul Orb / Cage Bindings (hold right click)
    catch (Throwable ts) { @PKG@.Soul.warn("tick:" + ts.getClass().getName(), "Soul Binding tick failed (" + ts + ")"); }
    try { @PKG@.Wings.tickPlayer(chunk.getReferenceTo(idx), store, cb); }          // 0.1.21: Wings of Fate (bounds, arrival, the wings)
    catch (Throwable tw) { @PKG@.Wings.warn("tick:" + tw.getClass().getName(), "Wings of Fate tick failed (" + tw + ")"); }
  }''', '''  if (chunk != null) {
    @REF@ pr0 = chunk.getReferenceTo(idx);          // 0.1.23: read once per player tick
    @PKG@.ArmoryHoldRec hr = null;          // 0.1.23 (finding 19): the held-weapon gate (null = every check runs)
    try { hr = @PKG@.ArmoryHold.rec(pr0, cb); }
    catch (Throwable th) { hr = null; @PKG@.ArmoryHold.warn("rec:" + th.getClass().getName(), "the held-weapon gate failed (" + th + ") - every check runs"); }
    if (@PKG@.ArmoryHold.runGrapple(hr)) {          // 0.1.2: the crossbow grapple, per player (world thread) - 0.1.23: crossbow / grapple / new body only
      try { @PKG@.Grapple.tickPlayer(pr0, store, cb); }
      catch (Throwable tg) { @PKG@.Grapple.warn("tick:" + tg.getClass().getName(), "grapple tick failed (" + tg + ")"); }
    } else {
      try { @PKG@.Grapple.idle(store, cb); }
      catch (Throwable tg2) { @PKG@.Grapple.warn("idle:" + tg2.getClass().getName(), "grapple sweep failed (" + tg2 + ")"); }
    }
    try { @PKG@.Leap.tickPlayer(pr0, store, cb); }          // 0.1.3: the leap's rise / hang / shot
    catch (Throwable tl) { @PKG@.Leap.warn("tick:" + tl.getClass().getName(), "leap tick failed (" + tl + ")"); }
    try { @PKG@.Levitate.tickPlayer(pr0, store, cb); }      // 0.1.6: the spellbook Levitate (rise / hover / float)
    catch (Throwable tv) { @PKG@.Levitate.warn("tick:" + tv.getClass().getName(), "Levitate tick failed (" + tv + ")"); }
    try { @PKG@.Kunai.tickPlayer(pr0, store, cb); }         // 0.1.6: the kunai flight / landing / return knockback
    catch (Throwable tk) { @PKG@.Kunai.warn("tick:" + tk.getClass().getName(), "kunai tick failed (" + tk + ")"); }
    try { @PKG@.Monk.tickPlayer(pr0, store, cb); }          // 0.1.12: the Monk moves (vault, bounds, rise, plunge, flowing fall)
    catch (Throwable tm) { @PKG@.Monk.warn("tick:" + tm.getClass().getName(), "Monk move tick failed (" + tm + ")"); }
    if (@PKG@.ArmoryHold.runSoul(hr)) {          // 0.1.19: the Soul Orb / Cage Bindings - 0.1.23: soul weapon / soul state / new body only
      try { @PKG@.Soul.tickPlayer(pr0, store, cb); }
      catch (Throwable ts) { @PKG@.Soul.warn("tick:" + ts.getClass().getName(), "Soul Binding tick failed (" + ts + ")"); }
    } else {
      try { @PKG@.Soul.idle(); }
      catch (Throwable ts2) { @PKG@.Soul.warn("idle:" + ts2.getClass().getName(), "soul sweep failed (" + ts2 + ")"); }
    }
    try { @PKG@.Wings.tickPlayer(pr0, store, cb); }          // 0.1.21: Wings of Fate (bounds, arrival, the wings)
    catch (Throwable tw) { @PKG@.Wings.warn("tick:" + tw.getClass().getName(), "Wings of Fate tick failed (" + tw + ")"); }
  }''')

# ---- (L10) the plugin: the 2 event systems (one registerSystem per class), the gate cleared with the other per-player maps
rep('''  catch (Throwable t10) { SYS_DROP = false; @PKG@.ArmoryLog.warn("SoulDropSys could not be registered: " + t10 + " - no zone essence drops this start"); }
''', '''  catch (Throwable t10) { SYS_DROP = false; @PKG@.ArmoryLog.warn("SoulDropSys could not be registered: " + t10 + " - no zone essence drops this start"); }
  // 0.1.23 (finding 19): the held-weapon gate's events - without them TravTick re-reads the hand every tick (the old cost)
  try { getEntityStoreRegistry().registerSystem(new @PKG@.ArmorySlotSys()); @PKG@.ArmoryHold.SYS_SLOT = true; }
  catch (Throwable t11) { @PKG@.ArmoryHold.SYS_SLOT = false; @PKG@.ArmoryLog.warn("ArmorySlotSys could not be registered: " + t11 + " - held weapons are read every tick"); }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.ArmoryInvSys()); @PKG@.ArmoryHold.SYS_INV = true; }
  catch (Throwable t12) { @PKG@.ArmoryHold.SYS_INV = false; @PKG@.ArmoryLog.warn("ArmoryInvSys could not be registered: " + t12 + " - held weapons are read every tick"); }
''')
rep('''  @PKG@.Wings.clear();          // 0.1.21
}""" % jarr(BRIDGE_KEYS))''', '''  @PKG@.Wings.clear();          // 0.1.21
  @PKG@.ArmoryHold.clear();          // 0.1.23
}""" % jarr(BRIDGE_KEYS))''')
rep('''  @PKG@.Wings.clear();          // 0.1.21
  systems();''', '''  @PKG@.Wings.clear();          // 0.1.21
  @PKG@.ArmoryHold.clear();          // 0.1.23
  systems();''')

# ---- (L11) tokens + the engine members the gate uses (probed at build time; the harness runs them)
rep('''    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",''',
    '''    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "EES": "com.hypixel.hytale.component.system.EntityEventSystem",          # 0.1.23: the held-weapon gate's events
    "ISAS": "com.hypixel.hytale.server.core.event.events.ecs.InventorySetActiveSlotEvent",
    "IVCE": "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent",''')
rep('''# ================================================================= classes (all top-level; methods before callers)''',
    '''# ---- 0.1.23: the held-weapon gate (finding 19) - EntityEventSystem(Class) + handle, the two ECS events (both EcsEvents), the vanilla systems
# that raise them (ActiveSlotInventoryComponent.setActiveSlot -> InventorySetActiveSlotEvent; InventorySystems$InventoryChangeEventSystem ->
# InventoryChangeEvent, per container change) and the hand read (InventoryComponent.getItemInHand = the Tool section's item or the hotbar's)
probe_sig(T["EES"], "<init>", "void", ["java.lang.Class"])
probe_sig(T["EES"], "handle", "void", ["int", T["ACH"], T["ST"], T["CB"], T["EV"]])
probe_sig(T["ACH"], "getReferenceTo", T["REF"], ["int"])
for _ev in ("ISAS", "IVCE"):
    assert str(pool.get(T[_ev]).getSuperclass().getName()) == T["EV"], "%s is no EcsEvent" % T[_ev]
    PROBED.append("%s extends EcsEvent" % T[_ev].rsplit(".", 1)[1])
for _cm, _mm, _need in (("com.hypixel.hytale.server.core.inventory.ActiveSlotInventoryComponent", "setActiveSlot", "invoke"),
                        ("com.hypixel.hytale.server.core.inventory.InventorySystems$InventoryChangeEventSystem", "tick", "invoke")):
    assert _need in _calls(_cm, _mm), "%s.%s no longer raises its ECS event" % (_cm, _mm)
    PROBED.append("%s.%s raises its ECS event (bytecode)" % (_cm.rsplit(".", 1)[1], _mm))
_gih = _calls("com.hypixel.hytale.server.core.inventory.InventoryComponent", "getItemInHand", "ComponentAccessor")
assert "isUsingToolsItem" in _gih and _gih.count("getActiveItem") == 2, "InventoryComponent.getItemInHand changed: %s" % _gih
PROBED.append("InventoryComponent.getItemInHand = Tool or Hotbar active item (bytecode)")

# ================================================================= classes (all top-level; methods before callers)''')

# ================================================================================================ the harness (written below)
# test_skyyarmory_0.1.23.py = the shared 0.7 port harness (tools/merchants_0_1_2_patch.py PORT_HARNESS, read as text - that patch is not run)
# against the 0.1.22 jar (the SET pin) with:
#   A  every class loads, links + initialises (-Xverify:all) on the 0.7 server jar
#   X  the 0.1.22 SoulDrop checks (real 0.7 ChunkStore fixture) + EVERY NEW 0.1.23 PATH EXECUTED: the gate (new body / warm-up / idle skip /
#      no read without a change / both REAL event systems' handle on a real ArchetypeChunk / the RECHECK safety net / busy players / the
#      per-tick fallback without event systems / prune / TravTick.tick itself gated and not), Grapple.idle + sweepTick, Soul.idle + busy +
#      sweepTick, Monk.flag (rounded, change-only), Soul.publish (change-only + clear), ArmoryTree ustr / ekey / gen, the lock-free bridges,
#      ArmoryCheck's stop (manaSettled, run -> DONE)
#   C  CLASS COMPARE 0.1.22 -> 0.1.23 member by member: only the planned members differ (ALLOWED below), 4 classes added; NON-CLASS FILES =
#      ASSET PARITY: every file byte-identical to 0.1.22 except manifest.json (Version + Name) (FIX ROUND: the Pounce override too)
#   AA the engine-access audit on 0.7
ARMORY_X = r'''
def mod_x(K, F):
    """SkyyArmory 0.1.23: the 0.1.22 SoulDrop checks + every new 0.1.23 path."""
    from jpype import JClass, JByte, JInt, JDouble, JLong
    Sd = JClass(PKG + "SoulDrop")
    V3 = JClass("org.joml.Vector3d")
    w = F["world"]
    MIN = -2147483648
    got = [int(Sd.blockEnv(w, *p)) for p in ((3, 65, 3), (3, 100, 3), (40, 65, 3), (3, 200, 3), (3, -5, 3), (3, 320, 3))]
    K.check(got == [1, 2, MIN, MIN, 0, 0], "X: SoulDrop.blockEnv on the real ChunkStore (0.1.22, built from source now): %s" % got)
    K.check(int(Sd.blockEnv(None, 1, 1, 1)) == MIN, "X: blockEnv(null world) = MIN, never throws")
    Sd.ENV = None
    e = [Sd.envOf(None, None, None, V3(3.5, 65.2, 3.5), w), Sd.envOf(None, None, None, V3(3.9, 100.0, 3.1), w),
         Sd.envOf(None, None, None, V3(40.5, 65.0, 3.5), w), Sd.envOf(None, None, "not an npc", V3(3.5, 200.5, 3.5), w), Sd.envOf(None, None, None, None, w)]
    K.check([None if x is None else str(x) for x in e] == ["Env_Zone1_Plains", "Env_Zone2_Savanna", None, None, None],
            "X: SoulDrop.envOf block fallback: %s" % [None if x is None else str(x) for x in e])

    # ---------------------------------------------------------------- the held-weapon gate (finding 19)
    Hd, HR, Lp = JClass(PKG + "ArmoryHold"), JClass(PKG + "ArmoryHoldRec"), JClass(PKG + "Leap")
    Gr, So, Tt = JClass(PKG + "Grapple"), JClass(PKG + "Soul"), JClass(PKG + "TravTick")
    U, HM = JClass("java.util.UUID"), JClass("java.util.HashMap")
    st = F["store"]
    hand = HM()
    Lp.HAND = hand          # the harness seam every hand read goes through (Leap.hand)
    Hd.clear()
    Hd.SYS_SLOT = True
    Hd.SYS_INV = True
    r0, r1 = F["sections"][0], F["sections"][1]          # real, valid Refs of the fixture store (stand-in player bodies)
    # the real ArchetypeChunk + index of r0 (Store's own chunk array)
    chunk, idx = None, -1
    for f_ in st.getClass().getDeclaredFields():
        if f_.getType().isArray() and "ArchetypeChunk" in str(f_.getType().getComponentType().getName()):
            f_.setAccessible(True)
            arr = f_.get(st)
            for c_ in (arr or []):
                if c_ is None:
                    continue
                for i_ in range(64):
                    try:
                        if c_.getReferenceTo(i_) == r0:
                            chunk, idx = c_, i_
                    except Exception:
                        break
    K.check(chunk is not None and idx >= 0, "X fixture: the real ArchetypeChunk holding the stand-in body found (index %d)" % idx)
    h = Hd.rec(r0, None)
    K.check(h is not None and h.u is None and int(h.warm) == 30 and int(Hd.NEW_BODIES) == 1 and int(Hd.READS) == 1 and Hd.REC.get(r0) == h,
            "X gate: a NEW body = one hand read now + 30 warm-up ticks (uuid unknown here)")
    K.check(bool(Hd.runGrapple(h)) and bool(Hd.runSoul(h)), "X gate: a new body / unknown uuid runs every check (the stale-effect cleanup)")
    u0 = U.randomUUID()
    h.u = u0
    hand.put(u0, "Weapon_Sword_Iron")
    for i_ in range(30):
        Hd.rec(r0, None)
    K.check(int(h.warm) == 0, "X gate: the warm-up ends after 30 ticks")
    g0, s0 = int(Hd.G_SKIPS), int(Hd.S_SKIPS)
    K.check(not bool(Hd.runGrapple(h)) and not bool(Hd.runSoul(h)) and int(Hd.G_SKIPS) == g0 + 1 and int(Hd.S_SKIPS) == s0 + 1,
            "X gate: an idle player (a sword in hand, no state) skips the grapple AND the soul tick")
    rd = int(Hd.READS)
    for i_ in range(20):
        Hd.rec(r0, None)
    K.check(int(Hd.READS) == rd, "X gate: no hand read while nothing changed (20 ticks)")
    hand.put(u0, "Weapon_Crossbow_Iron")
    Hd.rec(r0, None)
    K.check(not bool(h.xbow), "X gate: a hand change with no event is not read at once (event / recheck)")
    Slot, Inv = JClass(PKG + "ArmorySlotSys"), JClass(PKG + "ArmoryInvSys")
    ss, iv = Slot(), Inv()
    K.check(str(ss.getEventType().getName()).endswith("InventorySetActiveSlotEvent") and str(iv.getEventType().getName()).endswith("InventoryChangeEvent"),
            "X events: the two real EntityEventSystems listen to InventorySetActiveSlotEvent / InventoryChangeEvent")
    ev = JClass("com.hypixel.hytale.server.core.event.events.ecs.InventorySetActiveSlotEvent")(JInt(-1), JInt(0), JByte(2))
    n0 = int(Hd.EVENTS)
    ss.handle(JInt(idx), chunk, st, None, ev)
    K.check(Hd.DIRTY.containsKey(r0) and int(Hd.EVENTS) == n0 + 1, "X events: ArmorySlotSys.handle (a real event, the real chunk) marks the body")
    Hd.rec(r0, None)
    K.check(bool(h.xbow) and not bool(h.soul) and not Hd.DIRTY.containsKey(r0) and bool(Hd.runGrapple(h)) and not bool(Hd.runSoul(h)),
            "X gate: after the slot event the crossbow is read -> the grapple tick runs, the soul tick still skips")
    hand.put(u0, "Weapon_Wand_SoulCage_Iron")
    ice = JClass("com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent")(None, None, None, None)
    iv.handle(JInt(idx), chunk, st, None, ice)
    Hd.rec(r0, None)
    K.check(bool(h.soul) and not bool(h.xbow) and bool(Hd.runSoul(h)) and not bool(Hd.runGrapple(h)) and str(h.item) == "Weapon_Wand_SoulCage_Iron",
            "X gate: an inventory-change event (ArmoryInvSys.handle) -> the Soul Cage is read -> the soul tick runs")
    hand.put(u0, "Weapon_Sword_Iron")
    for i_ in range(int(Hd.RECHECK) - 1 - int(h.ticks)):
        Hd.rec(r0, None)
    still = bool(h.soul)
    Hd.rec(r0, None)
    K.check(still and not bool(h.soul), "X gate: the safety re-read every RECHECK (%d) ticks catches a change no event reported" % int(Hd.RECHECK))
    So.POOL.put(u0, JClass("java.lang.Object")())
    K.check(bool(So.busy(u0)) and bool(Hd.runSoul(h)), "X gate: stored healing (Soul.busy) keeps the soul tick running without the weapon")
    So.POOL.clear()
    Gr.STATES.put(u0, JClass("java.lang.Object")())
    K.check(bool(Gr.busy(u0)) and bool(Hd.runGrapple(h)), "X gate: a grapple record (Grapple.busy) keeps the grapple tick running")
    Gr.STATES.clear()
    Hd.SYS_INV = False
    hand.put(u0, "Weapon_Crossbow_Iron")
    Hd.rec(r0, None)
    K.check(bool(h.xbow), "X gate: an event system missing -> the hand is read every tick (the old behaviour)")
    Hd.SYS_INV = True
    K.check(Hd.rec(None, None) is None and bool(Hd.runGrapple(None)) and bool(Hd.runSoul(None)), "X gate: no Ref / no record = every check runs")
    bad = JClass("com.hypixel.hytale.component.Ref")(st, JInt(-2147483648))
    Hd.REC.put(bad, HR())
    Hd.DIRTY.put(bad, JClass("java.lang.Boolean").TRUE)
    p = int(Hd.prune())
    K.check(p == 1 and not Hd.REC.containsKey(bad) and not Hd.DIRTY.containsKey(bad) and Hd.REC.containsKey(r0),
            "X gate: prune drops a gone body (invalid Ref) and keeps live ones (pruned %d)" % p)
    K.check("held-weapon gate:" in str(Hd.text()), "X gate: the info text: %s" % str(Hd.text())[:160])
    # TravTick.tick itself: gated (sword) and not (crossbow); the idle paths drive the sweeps only while records exist
    tt = Tt()
    hand.put(u0, "Weapon_Sword_Iron")
    Hd.dirty(r0)
    gs, ssk, gr = int(Hd.G_SKIPS), int(Hd.S_SKIPS), int(Hd.G_RUNS)
    Gr.LASTEND.put(u0, JLong(0))
    sw0 = int(Gr.SWEEP_N)
    tt.tick(0.033, JInt(idx), chunk, st, None)
    moved = int(Gr.SWEEP_N) != sw0
    K.check(int(Hd.G_SKIPS) == gs + 1 and int(Hd.S_SKIPS) == ssk + 1 and moved,
            "X TravTick.tick: an idle player skips grapple + soul; Grapple.idle drives the sweep while a record exists")
    Gr.LASTEND.clear()
    hand.put(u0, "Weapon_Crossbow_Iron")
    Hd.dirty(r0)
    tt.tick(0.033, JInt(idx), chunk, st, None)
    K.check(int(Hd.G_RUNS) == gr + 1, "X TravTick.tick: a crossbow in hand runs the grapple tick")
    So.SEEN.put(u0, JLong(0))
    So.SWEEP_AT = JLong(0)
    So.idle()
    K.check(int(So.SWEEP_AT) > 0 and not So.SEEN.containsKey(u0), "X Soul.idle -> sweepTick swept a long-gone player's record")
    Gr.idle(st, None)
    So.sweepTick(JLong(0))
    try:
        q = tt.getQuery()
        K.notes.append("X: TravTick.getQuery on the bare fixture: %s" % q)
    except Exception as ex:
        K.notes.append("X: getQuery needs the booted EntityModule (bare fixture: %s) - same as 0.1.22's TravTick" % str(ex)[:80])
    for sys_ in (ss, iv):
        try:
            sys_.getQuery()
        except Exception:
            pass

    # ---------------------------------------------------------------- bridge writes only on change
    D, Tr, Mk = JClass(PKG + "ArmoryDefs"), JClass(PKG + "ArmoryTree"), JClass(PKG + "Monk")
    Sysp = JClass("java.lang.System").getProperties()
    b = D.bridge()
    K.check(b == Sysp.get("skyy.bridge") and D.BRIDGE == b and Tr.bridge() == b and Tr.BRIDGE == b,
            "X bridge: ArmoryDefs / ArmoryTree bridge() = the one shared map, cached (lock-free after the first call)")
    u1 = U.randomUUID()
    k1 = "armory:monkmove:" + str(u1)
    t0 = 1000000000123
    Mk.flag(u1, JLong(t0))
    w1 = int(Mk.FLAG_WRITES)
    Mk.flag(u1, JLong(t0 + 50))
    Mk.flag(u1, JLong(t0 + 100))
    v1 = int(b.get(k1))
    K.check(v1 == int(Mk.flagBucket(JLong(t0))) and v1 >= t0 + 100 and v1 - t0 < 250 + 1 and int(Mk.FLAG_WRITES) == w1 and int(Mk.FLAG_SKIPS) >= 2,
            "X Monk.flag: the until time rounded UP to 250 ms, the same bucket again = no write (value %d for %d)" % (v1, t0))
    Mk.flag(u1, JLong(t0 + 300))
    K.check(int(b.get(k1)) == int(Mk.flagBucket(JLong(t0 + 300))) and int(b.get(k1)) >= t0 + 300 and int(Mk.FLAG_WRITES) == w1 + 1,
            "X Monk.flag: a later bucket is written (never earlier than until)")
    Mk.unflagAll()
    K.check(b.get(k1) is None and Mk.FLAGGED.isEmpty(), "X Monk.unflagAll removes the flag")
    k2 = "armory:soul:" + str(u1)
    pw = int(So.PUB_WRITES)
    So.publish(u1, JDouble(3.14159))
    So.publish(u1, JDouble(3.141))
    K.check(float(b.get(k2)) == 3.14 and int(So.PUB_WRITES) == pw + 1 and int(So.PUB_SKIPS) >= 1, "X Soul.publish: an unchanged rounded value is not written again")
    So.publish(u1, JDouble(2.5))
    K.check(float(b.get(k2)) == 2.5 and int(So.PUB_WRITES) == pw + 2, "X Soul.publish: a change is written")
    So.publish(u1, JDouble(0.0))
    So.publish(u1, JDouble(0.0))
    K.check(b.get(k2) is None and int(So.PUB_WRITES) == pw + 3 and not So.PUBV.containsKey(u1), "X Soul.publish: 0 removes once, a second 0 writes nothing")
    So.publish(u1, JDouble(1.25))
    So.clear()
    K.check(b.get(k2) is None and So.PUBV.isEmpty(), "X Soul.clear removes a written value that has no pool entry")
    Tr.clear()
    b.put("profile:epoch:" + str(u1), JLong(5))
    g_a = int(Tr.gen(u1))
    g_b = int(Tr.gen(u1))
    b.put("profile:epoch:" + str(u1), JLong(6))
    g_c = int(Tr.gen(u1))
    K.check((g_a, g_b, g_c) == (0, 0, 1) and str(Tr.EKEY.get(u1)) == "profile:epoch:" + str(u1) and Tr.EKEY.size() == 1
            and str(Tr.ustr(u1)) == str(u1) and Tr.USTR.size() == 1, "X ArmoryTree.gen with the cached key: baseline, same, +1 on a new epoch (%s)" % [g_a, g_b, g_c])
    Tr.clear()
    K.check(Tr.EKEY.isEmpty() and Tr.USTR.isEmpty(), "X ArmoryTree.clear drops the cached keys")
    b.remove("profile:epoch:" + str(u1))

    # ---------------------------------------------------------------- ArmoryCheck stops once done
    Ck, Cf = JClass(PKG + "ArmoryCheck"), JClass(PKG + "ArmoryCfg")
    on0 = bool(Cf.CHECK_ON)
    Cf.CHECK_ON = True
    Ck.MANA_LVL = ""
    Ck.MANA_TRIES = 0
    a1 = bool(Ck.manaSettled())
    Ck.MANA_LVL = "skip"
    a2 = [bool(Ck.manaSettled()) for i_ in range(int(Ck.PACK_MAX))]
    Ck.MANA_LVL = "info"
    a3 = bool(Ck.manaSettled())
    Cf.CHECK_ON = False
    a4 = bool(Ck.manaSettled())
    K.check(not a1 and a2[-1] and not a2[0] and a3 and a4, "X ArmoryCheck.manaSettled: not yet / gives up after PACK_MAX / ran / off: %s" % [a1, a2, a3, a4])
    Ck.STOP = False
    Ck.GEN = 7
    Ck.PACK_DONE = True
    Ck.DONE = False
    c_ = Ck(JInt(7))
    c_.run()
    K.check(bool(Ck.DONE) and int(Ck.RUNS) >= 1, "X ArmoryCheck.run: pack check done + Mana check settled -> DONE, not scheduled again")
    # FIX ROUND: the done check PARKS (no chain); a parked run re-reads the epochs (the check only on a change) and parks again; the gate's
    # prune pass hands it to the scheduler at most every 30 s
    K.check(Hd.WATCHER == c_, "X FIX Mana refresh: the done ArmoryCheck parks in ArmoryHold.WATCHER (no re-scheduling chain)")
    Cf.CHECK_ON = True
    Hd.WATCH_AT = JLong(0)
    nowm = int(JClass("java.lang.System").currentTimeMillis())
    Hd.WATCH_AT = JLong(nowm)
    K.check(not bool(Hd.watch(JLong(nowm + 1000))) and Hd.WATCHER == c_, "X FIX Mana refresh: not handed over again within 30 s")
    Hd.WATCHER = None
    sig0 = str(Ck.MANA_SIG)
    w0 = int(Ck.WATCHES)
    r0n = int(Ck.RUNS)
    b.put("config:epoch:SkyySkills", JLong(424242))
    c_.run()
    sig1 = str(Ck.MANA_SIG)
    K.check(int(Ck.WATCHES) == w0 + 1 and int(Ck.RUNS) == r0n and sig1 != sig0 and "424242" in sig1 and Hd.WATCHER == c_ and len(str(Ck.MANA_LAST)) > 0,
            "X FIX Mana refresh: a parked run sees the changed SkyySkills epoch, re-runs the Mana check (%s) and parks again" % sig1)
    c_.run()
    K.check(str(Ck.MANA_SIG) == sig1 and int(Ck.WATCHES) == w0 + 2, "X FIX Mana refresh: no epoch change = no new check (only the 3 epoch reads)")
    b.remove("config:epoch:SkyySkills")
    Hd.WATCH_AT = JLong(0)
    handed = bool(Hd.watch(JLong(nowm + 60000)))
    K.check((handed and Hd.WATCHER is None and int(Hd.WATCH_AT) == nowm + 60000) or (not handed and Hd.WATCHER == c_),
            "X FIX Mana refresh: ArmoryHold.watch after 30 s hands the parked check to the scheduler (or keeps it parked if none: %s)" % handed)
    Hd.WATCHER = c_
    Hd.WATCH_AT = JLong(0)
    Hd.CALLS = JInt(int(Hd.PRUNE_EVERY) - 1)
    Hd.rec(r0, None)
    K.check(int(Hd.CALLS) == 0 and int(Hd.WATCH_AT) > 0,
            "X FIX Mana refresh: the gate's prune pass (every PRUNE_EVERY calls) calls watch")
    Ck.STOP = True
    Hd.WATCHER = None
    c_.run()
    K.check(Hd.WATCHER is None, "X FIX Mana refresh: a stopped check (shutdown) never parks again")
    Ck.STOP = False
    Hd.clear()
    K.check(Hd.WATCHER is None and int(Hd.WATCH_AT) == 0, "X FIX: ArmoryHold.clear drops the parked check")
    Cf.CHECK_ON = on0
    # FIX ROUND: the gate's crossbow test = Grapple.onShot's rule (any id naming a crossbow)
    xs = [bool(Hd.xbowItem(x_)) for x_ in ("Weapon_Crossbow_Iron", "VC_Weapon_Crossbow_Void", "SkyyArmory_Crossbow_Onyxium", "Weapon_Sword_Iron", None)]
    K.check(xs == [True, True, True, False, False], "X FIX gate: a crossbow = an id naming a crossbow, the grapple's own rule (VC_Weapon_Crossbow_Void in): %s" % xs)
    Hd.SYS_SLOT = True
    Hd.SYS_INV = True
    uv = U.randomUUID()
    hand.put(uv, "VC_Weapon_Crossbow_Void")
    hv = Hd.rec(r1, None)
    hv.u = uv
    hv.warm = 0
    Hd.dirty(r1)
    Hd.rec(r1, None)
    K.check(bool(hv.xbow) and bool(Hd.runGrapple(hv)) and not bool(Hd.runSoul(hv)), "X FIX gate: another pack's crossbow in hand runs the grapple tick")
    Hd.clear()
'''


def _port_harness():
    src = open(os.path.join(ROOT, "tools", "merchants_0_1_2_patch.py"), encoding="utf8").read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "PORT_HARNESS":
            return ast.literal_eval(node.value)
    raise SystemExit("PORT_HARNESS not found in tools/merchants_0_1_2_patch.py")


# the members the source build changes vs the 0.1.22 port build (C fails on any other difference)
ALLOWED = {
    # the 0.1.23 changes (L1-L10 above)
    "ArmoryCheck": ["~<clinit>", "+f DONE", "+f MANA_LVL", "+f MANA_TRIES", "+f RUNS", "+f WATCHES", "+m manaSettled", "~m manaTick", "~m run", "~m start",
                    "~m wantLaunch"],          # FIX ROUND: wantLaunch = encoding only (one string constant moved ldc -> ldc_w past the 256th pool slot; every branch +1, reviewed instruction diff)
    "ArmoryDefs": ["+f BRIDGE", "~m bridge", "+m bridge0"],
    "ArmoryTree": ["~<clinit>", "+f BRIDGE", "+f EKEY", "+f USTR", "~m bridge", "+m bridge0", "~m clear", "+m ekey", "~m gen", "+m ustr"],
    "Grapple": ["+m busy", "+m idle", "+m sweepTick", "~m tickPlayer"],
    "Monk": ["~<clinit>", "+f FLAG_SKIPS", "+f FLAG_STEP", "+f FLAG_WRITES", "~m flag", "+m flagBucket"],
    "SkyyArmoryPlugin": ["~m publish", "~m setup", "~m systems", "~m unpublish"],          # publish: only an ldc -> ldc_w constant-pool encoding
    "Soul": ["~<clinit>", "+f PUBV", "+f PUB_SKIPS", "+f PUB_WRITES", "+m busy", "~m clear", "+m idle", "~m publish", "+m sweepTick", "~m tickPlayer"],
    "TravTick": ["~m tick"],
    # the config kit's lock-free bridge (tools/skyycfg.py since 2026-10-13; every rebuilt mod picks it up)
    "CfgRows": ["+f BRIDGE", "~m bridge", "+m bridge0"],
    # NOT code changes (reviewed with a javassist instruction diff): SoulDrop's two methods differ only in ldc / ldc_w encoding (the 0.1.22
    # port build compiled them into the 0.1.21 constant pool); WorldGrid names the 0.7 owner of getStore / getChunkSectionReferenceAtBlock
    # (ChunkStore now extends ChunkGrid - javassist resolves to the declaring class on 0.7; the JVM resolves 0.1.22's the same way)
    "SoulDrop": ["~m blockEnv", "~m envOf"],
    "WorldGrid": ["~c ", "~m at"],
}
ADDED = ["ArmoryHoldRec", "ArmoryHold", "ArmorySlotSys", "ArmoryInvSys"]
H = _port_harness()
H = H.replace('''"""Port harness for @MOD@ @VER@ (Hytale 0.7.0 port).''', '''"""Harness for @MOD@ @VER@ (the full build on the Hytale 0.7.0 assets + the TravTick gate) - the shared 0.7 port harness with
0.1.23's X part (every new code path) and the asset parity check (C).''', 1)
_PAR_OLD = '''    K.check(ed == ["manifest.json"] and ma_ == mb_ and mb_.get("Version") == VERSION and mb_.get("Name") == "%s %s" % (VERSION, MOD),
            "C: non-class entries: only manifest.json changed, and only its Version + Name (%s, %s): %s" % (mb_.get("Version"), mb_.get("Name"), ed[:8]))'''
_PAR_NEW = '''    # 0.1.23 ASSET PARITY: the full build on the 0.7 assets = the 0.1.22 files byte for byte (only manifest.json differs). FIX ROUND: the
    # dagger Pounce override no longer takes 0.7's Rules (Shadow Step's hold = the tested 0.1.22 file, block does not cancel it)
    _pp = "Server/Item/Interactions/Weapons/Daggers/Primary/Pounce/Weapon_Daggers_Primary_Pounce.json"
    K.check(ed == ["manifest.json"] and ma_ == mb_ and mb_.get("Version") == VERSION and mb_.get("Name") == "%s %s" % (VERSION, MOD),
            "C: non-class entries (%d files): only manifest.json changed, and only its Version + Name: %s" % (len(set(za.namelist()) | set(zb.namelist())), ed[:8]))
    _pb = json.loads(zb.read(_pp))
    K.check(za.read(_pp) == zb.read(_pp) and "Rules" not in _pb and _pb["HorizontalSpeedMultiplier"] == 0.5,
            "C FIX: the Pounce override (Shadow Step hold) = 0.1.22's byte for byte: no 0.7 Rules (block never cancels it), the tested 0.5 slow")
    _n = 0
    for _f in sorted(set(za.namelist()) & set(zb.namelist())):
        if not _f.endswith(".class") and _f not in ed:
            _n += 1
    K.notes.append("C: %d non-class files byte-identical to 0.1.22 (items, interactions, particles, models, art, lang, config defaults)" % _n)'''
assert H.count(_PAR_OLD) == 1
H = H.replace(_PAR_OLD, _PAR_NEW)
for k, v in (("@MOD@", "SkyyArmory"), ("@VER@", "0.1.23"), ("@OLD@", "0.1.22"), ("@PKG@", "com.skyy.armory."), ("@SCRATCH@", "armory0123"),
             ("@PATCH@", "tools/armory_0_1_23_patch.py"), ("@ALLOWED@", repr(ALLOWED)), ("@ADDED@", repr(ADDED)), ("@MODX@", ARMORY_X)):
    assert k in H, k
    H = H.replace(k, v)
with open(TDST, "w", encoding="utf8", newline="") as f:
    f.write(H.replace(LF, NL))
print("wrote", os.path.relpath(TDST, ROOT))

# ================================================================================================ write
assert s.count("registerSystem(") == SYS0 + 2 and s.count("registerCommand(") == CMD0, "0.1.23 adds the 2 gate event systems, no command"
HEADNOTES = """the full script ported to the 0.7 vanilla files (every generated item / interaction / particle / icon = the 0.1.22 jar's byte for byte,
the dagger Pounce override included - 0.7's new Rules not copied; where 0.7 moved a vanilla number we copy, our tested value is kept - list in the
patch) + the TravTick lag fix (ArmoryHold: Grapple / Soul ticks only for a player holding their weapon or with their state; the hand read
again only on a hotbar / slot / inventory change: ArmorySlotSys + ArmoryInvSys) + lock-free bridge, cached epoch key, Monk flag / Soul pool
bridge writes only on change, ArmoryCheck stops when done. No saved data, config row, item or command changed."""
rep("@HEADNOTES@", HEADNOTES)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(s.replace(LF, NL))
print("wrote", os.path.relpath(DST, ROOT))
