"""Derive SkyySkills/build_skyyskills_0.4.15.py from the LIVE generated SkyySkills/build_skyyskills_0.4.14.py (= the tools/deploy_set.py SET
pin; 0.4.14 came from 0.4.13 by tools/skills_0_4_14_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). Same style as skills_0_4_14_patch.py: rep(old, new) with asserted single anchors, newline-agnostic;
0.4.14 stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_15_patch.py   then   python SkyySkills/build_skyyskills_0.4.15.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.15.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/skills0415/, deleted afterwards)

0.4.15 = THE SKYYSKILLS PART OF THE ARMORY ROUND (research/SkyyArmory-Spec.md section 15 "Staffs, Mana pools and heal caps"; Skyy's
answers OPEN-QUESTIONS.md "ANSWERED 2026-10-03 morning": "PRIEST MANA: +5 max Mana per Divinity level, Priest-only row (next SkyySkills)",
"MAGE STAFFS get their Mana / damage ladder WITH the wands" -> "Mages get the matching Mage-only row (per Sorcery level)"):

(1) MAX MANA PER CLASS LEVEL (spec 15.4). New Server Setup table mana.classPerLevel ("Max Mana per class level", Overall and Mana, right
    under "Base Mana by class"; dec 0-100 per level, live, check= ClassMana.checkEntry = a known class name). Default Priest 5 (Skyy's
    lock) and Mage 10 (the spec's number: the staff ladder costs twice the wand's Mana; the smallest whole number that keeps every staff's
    charged shot <= 40% of a fighter Mage's pool at its band start - the Mithril / Onyxium staff needs 9.855). ONE Python table
    CLASS_MANA_DEF holds both (Skyy's question S4 changes one number there). A class not listed gains nothing.
    ClassMana.amount(u, data) = entry[the ACTIVE profile's class] x the level of THAT class's own skill (SkillClass.slotOfClass: Priest ->
    Divinity, Mage -> Sorcery), 0 for no class / an unlisted class / an unknown class, 0 while "Base Mana" (mana.base.enabled) is off.
    Applied through the EXISTING max-Mana path: Perks.ovl (the 1 s world-thread tick of every online player) posts it as its own
    MAX / ADDITIVE StaticModifier skyyskill_classmana right after skyyskill_basemana, through the same Perks.mod (amount 0 = the modifier is
    REMOVED), behind the same session hold (Overall.hold). Computed from scratch every second from the class + the class skill level, so
    a class switch or a profile switch changes or removes it within a second and nothing ever stacks (one key, putModifier replaces).
    Current Mana is never written (no refill on a level up or a switch - like Base Mana). OVL_KEYS gains the key. SkyyAccessories' Mana %
    already counts every other ADDITIVE MAX modifier (flatMax), so the row is boosted with no change there.
    SHOWN: the class skill's Stats page ("+50 max Mana (5 per Divinity level, Priest only)" under Boosts right now, "+5 max Mana" under
    Level N adds) and the admin /skills mana (one more line: "Max Mana 80.2 = base 30 + class level 50 (Priest 5 x Divinity 10) + Overall
    0.2 + skill perks 0" - the live modifiers, plus "other mods" for trees / accessories / armor).
    SAVED DATA: nothing new in players/<pkey>.properties. The new modifier is saved with the player by the engine (like the 0.4.6 ones):
    ROLLBACK below 0.4.15 = switch Base Mana off in Server Setup and let players log in once first (0.4.14 never removes skyyskill_classmana).
    CONFIG FILE: a fresh xp.properties holds the block at its end (CMAN_L). An existing file gets it ONCE from ClassManaMig.run (setup,
    after DocMig, BEFORE SkillCfg.load and the kit's start - PROJECT-RULES one-time migration): only when the file has NO mana.classPerLevel
    line and no comment line holding the block marker (an admin's table - even an emptied one - is never touched again); appended after
    the file's last line in its OWN line ending (ISO-8859-1 bytes, nothing before it changes; a last line ending in a continuation
    backslash gets one more blank line; a Properties check: every old key keeps its value, exactly the default entries are new; keep
    CMAN_MARK_ID's text stable in later versions or old files get the block again), the file before it becomes a verified config-history copy first (HealMig.mgKit +
    CfgHist.snapshot + mgSaved - no write unless the copy is there), the kit's atomicWrite, one config-changes.log line per entry
    (mana.classPerLevel[Priest] (none) -> 5: Server Setup > Changes > Undo takes it out again), one INFO line. Failure = WARN, file
    untouched, retried at the next start (until then the table is empty = no class level Mana).
(2) THE STAFF HANDOVER (spec 15.3 (a)-(g)). The 8 ladder staffs Weapon_Staff_Wood / _Copper / _Iron / _Thorium / _Cobalt / _Adamantite /
    _Mithril / _Onyxium (ARMORY_OWNED) get their own Charging root and Mana per metal from SkyyArmory 0.1+, which ships their item files.
    (a) They leave SPELL_ITEMS before spell_plan: no override is generated, the gate simulation never sees them; 24 item overrides remain
        (14 other staff-folder items, 2 guns, 5 spellbooks, 3 wands - the len(SPELL_PLAN) >= 20 guard holds). The build refuses an item
        that inherits from one of them by Parent (none in Assets.zip today).
    (b) The 8 interaction overrides stay byte-identical: Staff_Cast_Summon_Charged still checks 10 for the other staff-folder items (all
        spend 10) and Crystal_Red / Crystal_Ice (spend 0) - asserted (SPELL_FAMS), and the harness compares the files with 0.4.14's jar.
    (c) The two Wood-staff asserts are replaced: the wand asserts stay; when SkyyArmory is pinned in tools/deploy_set.py SET and its jar is
        built, its SkyyArmory_Staff_Cast_Wood must check 10 (StatsCondition Costs Mana) and SkyyArmory_Staff_Cast_Cost_Wood spend 10
        (ChangeStat Mana -10) - the kit numbers Skyy's "Mage 30 = 3 staff casts" was set for.
    (d) _spell_clash refuses the 8 item files in every live-set jar and pack mod EXCEPT SkyyArmory; a pinned SkyyArmory jar must ship all
        8 (a missing one would leave the vanilla file behind this jar's 10-Mana check: it spends 50). Installed mods that are not in the
        set stay a NOTE (HyBoards / Skyys-HyMax ship staff files today - off in the test world). A deployed SkyyArmory in the Mods folder
        is not reported for the 8.
    (e) Kit lookup (ManaGuard via ManaCost.costOf / spendOf): an ARMORY_OWNED id asks armory:fn:info {"staff", id} (index 0 = its charged
        Mana = its check = its spend); without an answer it reports what the VANILLA file does behind this jar's interactions (computed by
        the SPELL GEN gate simulation at build time: check 10, spend 50 - so a missing SkyyArmory shows up in the Base Mana check line too).
    (f) The pack check (ManaGuard.packTick, one INFO or WARN at start) also reads which asset pack the game's item assets take the 8
        staffs from: INFO when every one comes from a "Skyy:<ver> SkyyArmory" pack, else WARN "... run on their vanilla files - install
        SkyyArmory 0.1+ together with this SkyySkills".
    (g) Texts that say "staff 10" stay true (the Wood staff's charged shot still costs 10).
    DEPLOY AND ROLL BACK TOGETHER WITH SkyyArmory 0.1 (and SkyyClasses 0.1.11): SkyyArmory 0.1 with SkyySkills 0.4.14 = two packs ship the
    8 files (load order decides); SkyySkills 0.4.15 without SkyyArmory = the staffs spend 50 behind a 10 check (the pool drains). The
    tools/deploy_set.py pair note + floor note are the main session's (this builder may not edit that file).
FIX ROUND (review of the Armory round, 2026-10-03):
(3) HEAL XP PAYS WHAT FITS: HealXp.grant pays min(the heal XP of one call, the room left in the Priest's 60 s window) instead of refusing a
    call that crosses divinity.healXpMaxPerMinute (SkyyClasses 0.1.11 sends one call per hit with up to 170 HP per member: 3 hurt members
    reached only 80% of the cap, 6+ members - a party size raised in Server Setup - were refused forever). The cap stays 900 a minute; a
    partly paid call logs "paid N of M" (the existing once-a-minute WARN). take (all or nothing) stays for other callers.
(4) PAIR GUARD: the build STOPS when tools/deploy_set.py pins SkyySkills 0.4.15+ without SkyyArmory (a partial pin passed every check);
    before the pin bump it stays the NOTE. tools/deploy_set.py needs the same assert (the main session's file).
(5) Stale text: the spell.manaDivisor row help no longer reads as every spell's cost (SkyyArmory sets its own); the fresh-file comment stays
    (it is also the 0.4.8 ManaMig text, and still true for this jar's own overrides).
NOT in this build: the SkyyTrees 0.3 reader flags (a later SkyySkills - the main session numbers it); SPELL_INTS / the 8 interaction
overrides are unchanged (the spec assigns SkyySkills no interaction change for the staff ladder); the other staffs / wands / spellbooks keep
today's costs (Skyy's question S6: later); regen that grows with max Mana (S7: later).
CHECKED (SkyySkills/test_skyyskills_0.4.15.py, 430 checks; fix round + HX heal XP grant / offer, + HB partial pin): every 0.4.14 section carried; CM the real Perks.ovl on a real EntityStatMap
(Priest / Mage / Warrior at 0 / 1 / 10 / 20 / 40 = the spec's fighter pools; class + profile switch; part switch; hold; error kept);
HO costOf / spendOf / the Base Mana check line / armReport / armCheck through a real DefaultAssetMap / packTick; M15 ClassManaMig on 13
file shapes; KC the row through the real config kit (keys op, Undo, check= hook, bounds, reload, an emptied table); HB the jar's assets vs
0.4.14 + the build's clash code exec'd on 11 fake set-ups; M start twice on a copy of the live data; F class compare 0.4.14 -> 0.4.15;
A -Xverify:all; Z engine-access audit (0 refused).
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.14.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.15.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.14"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
# the source must be the generated 0.4.14 of the edited lineage
assert 'VERSION = "0.4.14"' in s and "derived from the generated 0.4.13 by tools/skills_0_4_14_patch.py" in s, "not the live generated 0.4.14"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
for _x in ('".ClassMana"', '".ClassManaMig"', "ClassMana.", "mana.classPerLevel", "skyyskill_classmana", "ARMORY_OWNED", "armory:fn:info",
           "CLASS_MANA_DEF", "CMAN_L", "ARM_IDS"):
    assert _x not in s, "0.4.14 already has " + _x
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]
OLDS = []   # every 0.4.14 text a rep() replaced (the whole-diff check below allows exactly their lines to change)


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    i = s.index(old)
    j = s.find(LF, i + len(old))
    OLDS.append(s[s.rfind(LF, 0, i) + 1:(j if j >= 0 else len(s))])   # the WHOLE lines the anchor touches
    s = s.replace(old, new)


def after(anchor, add):
    """insert add right after the (single) anchor"""
    rep(anchor, anchor + add)


def before(anchor, add):
    """insert add right before the (single) anchor"""
    rep(anchor, add + anchor)


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1 and s.index(a) < s.index(b), (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# blocks that must come out of this patch byte-identical (each still occurs exactly once afterwards)
KEEP = [block("# >>> SPELL GEN", "# <<< SPELL GEN"),
        block("# ================= ManaRegen (0.4.12)", "# AcroSys: EntityTickingSystem on Player entities"),
        block("# ================= SkillDefs: names, icons, level table", "# ================= SkillCfg: xp.properties"),
        block("# ================= Xbow part 1 (0.4.5)", "# ================= ClassCurve (0.4.12)"),
        block("# ================= ClassCurve (0.4.12)", "# ================= SkillXp: award + level-up (world thread)"),
        block("# ================= 0.4.2 FELLED TREES", "# FellCredit (spec 2.6)"),
        block("# ================= skill:fn:addxp (0.4)", "# ================= /skills page (inline"),
        block("# ================= OverallPage (0.4.6)", "# ================= 0.4.3 ADMIN CONFIG"),
        block("# ================= SkillKit (0.4.3)", "# ================= commands ================="),
        block("# ---- 0.4.5 Xbow part 2", "# ================= ManaRegen (0.4.12)"),
        block("# ================= CombatDmgSys (0.3)", "# ================= PlacedStore"),
        block("# ================= PlacedStore", "# ================= 0.4.2 FELLED TREES"),
        block("# ================= EnvSys (0.4.2, Tree-Fall-Spec 2.4)", "# ================= trees bridge Functions"),
        block("# ================= SKILLS PAGES LOOK (0.4.7)", "# ================= StatsPage (0.3)"),
        # 0.4.15: + the 0.4.14 systems, the store / class / Overall sections and HealMig + DocMig (all untouched here)
        block("# ================= RollSys (0.4.14)", "# ================= CombatDmgSys (0.3)"),
        block("# ================= Sickle (0.4.14, research/Tool-Levels-Spec.md question 3)", "# ================= Brew.extraPotion (0.4)"),
        block("# ================= MobXp maths (0.4.14)", "# ================= PartyXp (0.4.2 stage 2"),
        block("# ================= SkillStore: per-player XP", "# ================= SkillClass (0.3)"),
        block("# ================= SkillClass (0.3)", "# ================= Overall (0.4.6)"),
        block("# ================= Overall (0.4.6)", "# ================= skill:fn:overall (0.4.6, spec 4.8)"),
        block("# ---- HealMig (0.4.11 point 5)", "# ---- ManaGuard (point 3)"),
        block("# ================= OverallCfg (0.4.6)", "# ================= 0.4.14 config readers")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.14 - build script (derived from the generated 0.4.13 by tools/skills_0_4_14_patch.py - edit the patch, not this file;
0.4.13 was derived''', '''"""SkyySkills 0.4.15 - build script (derived from the generated 0.4.14 by tools/skills_0_4_15_patch.py - edit the patch, not this file;
0.4.14 was derived from the generated 0.4.13 by tools/skills_0_4_14_patch.py; 0.4.13 was derived''')
HEAD_0415 = '''0.4.15: MAX MANA PER CLASS LEVEL + THE STAFF HANDOVER (Skyy 2026-10-03; research/SkyyArmory-Spec.md section 15; full notes in
  tools/skills_0_4_15_patch.py).
  MAX MANA PER CLASS LEVEL: config table mana.classPerLevel (Server Setup > Skills > Overall and Mana > "Max Mana per class level", right
     under Base Mana by class; default Priest 5 (Skyy: "+5 max Mana per Divinity level"), Mage 10 (the staff ladder costs twice the wand's
     Mana); a class not listed gains none). A listed class gains that much max Mana per level of ITS OWN class skill (Priest: Divinity,
     Mage: Sorcery): MAX / ADDITIVE StaticModifier skyyskill_classmana, computed from scratch every second in Perks.ovl right after
     skyyskill_basemana (same world-thread tick, same "Base Mana" part switch, same session hold; the ACTIVE profile's class and its own
     class skill level - a class or profile switch changes or removes it within a second, it never stacks). SkyyAccessories' Mana % counts
     it. Shown on the class skill's Stats page and in the admin /skills mana (max Mana by source). An existing xp.properties gets the
     default lines ONCE (ClassManaMig, setup, before the file is read: only without any mana.classPerLevel line and without the block
     marker; History copy first, one change-log line per entry, the file's own line ending, nothing else changes).
  STAFF HANDOVER: the 8 ladder staffs (Weapon_Staff_Wood ... _Onyxium) belong to SkyyArmory 0.1+ (its own Charging root and Mana per metal
     - the staff ladder). This jar no longer ships their item overrides (24 remain; the 8 interaction overrides are byte-identical:
     Staff_Cast_Summon_Charged still checks 10 for the other staffs). The build refuses any live-set jar or pack mod but SkyyArmory that
     ships one of the 8; a pinned SkyyArmory must ship all 8, its Wood staff checking and spending 10. The kit check asks armory:fn:info
     for their cost (else what the vanilla file would do: check 10, spend 50); the pack check WARNs when they do not come from SkyyArmory.
     DEPLOY + ROLL BACK TOGETHER WITH SkyyArmory 0.1 (without it the 8 staffs spend 50 Mana behind a 10-Mana check).
  ROLLBACK below 0.4.15: switch Base Mana off in Server Setup and let players log in once (skyyskill_classmana is saved with the player).
  FIX ROUND: heal XP pays what still fits in the minute (HealXp.grant - SkyyClasses 0.1.11's big heals were refused whole when they
     crossed divinity.healXpMaxPerMinute, and forever above it); the build stops when SkyySkills 0.4.15+ is pinned without SkyyArmory;
     the spell.manaDivisor help names SkyyArmory's own costs.
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.15.py, -Xverify:all, scratch under tools/dev/scratch deleted afterwards).
'''
before("0.4.14: SKYY'S LOCKS OF 2026-10-02 (OPEN-QUESTIONS Q&A; full notes in tools/skills_0_4_14_patch.py).\n", HEAD_0415)
rep('VERSION = "0.4.14"\n', 'VERSION = "0.4.15"\n')

# ---------------------------------------------------------------------------------------------------------------- default xp.properties
CMAN_BLOCK = r'''# 0.4.15 (research/SkyyArmory-Spec.md 15.4, Skyy 2026-10-03): max Mana per level of the class's own skill - ONE block at the end of a fresh
# file; ClassManaMig appends it ONCE to an existing file (only when it has no mana.classPerLevel line and no comment line holding CMAN_MARK_ID).
# CLASS_MANA_DEF = the defaults in SkillDefs.CLASSES order (Mage before Priest; checked at the config rows): Priest 5 = Skyy's lock ("+5 max
# Mana per Divinity level"), Mage 10 = the spec's number for the staff ladder (staffs cost twice the wand's Mana) - one place for both.
CLASS_MANA_DEF = [("Mage", 10), ("Priest", 5)]
CMAN_MARK_ID = "Max Mana per class level (SkyySkills 0.4.15)"
CMAN_L = []
CMAN_L.append("# ---------- " + CMAN_MARK_ID + " ----------")
CMAN_L.append("# Comments must stay on their own lines.")
CMAN_L.append("# A class listed here (one line per class: mana.classPerLevel.<Class>=<Mana>) gains that much max Mana per level of its own")
CMAN_L.append("# class skill (Priest: Divinity, Mage: Sorcery), on top of its Base Mana by class. A class not listed gains none. Skyy")
CMAN_L.append("# 2026-10-03: Priest 5 (the metal wands); Mage 10 (the staffs cost twice the wand's Mana). 0 to 100 per level. The Base Mana")
CMAN_L.append("# switch (mana.base.enabled) turns this off too.")
for _cc, _cv in CLASS_MANA_DEF:
    CMAN_L.append("mana.classPerLevel.%s=%d" % (_cc, _cv))
L.append("")
L.extend(CMAN_L)
CMAN_DEFAULTS = "\n".join(CMAN_L) + "\n"
assert all(ord(ch) < 128 for ch in CMAN_DEFAULTS) and '"' not in CMAN_DEFAULTS and "\\" not in CMAN_DEFAULTS
assert not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in CMAN_L), "a comment looks like a template line"
CMAN_KEYS = [_ln.split("=", 1)[0] for _ln in CMAN_L if not _ln.startswith("#")]
assert CMAN_KEYS == ["mana.classPerLevel." + _c for _c, _v in CLASS_MANA_DEF] and len(set(CMAN_KEYS)) == len(CMAN_KEYS)
assert sum(1 for _ln in CMAN_L if CMAN_MARK_ID in _ln) == 1 and CMAN_L[0].startswith("# ") and all(0 <= _v <= 100 for _c, _v in CLASS_MANA_DEF)
assert dict(CLASS_MANA_DEF).get("Priest") == 5, "Skyy's lock 2026-10-03: Priest +5 max Mana per Divinity level"
CMAN_LIT = json.dumps(CMAN_DEFAULTS)
'''
after("N14_LIT = json.dumps(N14_DEFAULTS)\n", CMAN_BLOCK)

# ---------------------------------------------------------------------------------------------------------------- SPELL GEN usage: the staff handover
after("assert spell_new(3, 5) == 1 and spell_new(-2, 5) == -1 and spell_new(12, 5) == 2 and spell_new(13, 5) == 3 and spell_new(1, 5) == 1\n",
      r'''# 0.4.15 STAFF HANDOVER (research/SkyyArmory-Spec.md 15.3; Skyy 2026-10-03: "MAGE STAFFS get their Mana / damage ladder WITH the wands"):
# the 8 ladder staffs get their own Charging root and Mana per metal from SkyyArmory 0.1+, which ships their item files. This jar no longer
# generates an override for them - they leave SPELL_ITEMS before spell_plan, so the gate simulation never sees them; their vanilla files
# stay in memory (ARMORY_ITEMS) for the kit lookup's fallback (what a cast checks / spends on the vanilla file behind this jar's
# interactions). SkyySkills 0.4.15 and SkyyArmory 0.1 deploy and roll back TOGETHER.
ARMORY_OWNED = ["Weapon_Staff_Wood", "Weapon_Staff_Copper", "Weapon_Staff_Iron", "Weapon_Staff_Thorium", "Weapon_Staff_Cobalt",
                "Weapon_Staff_Adamantite", "Weapon_Staff_Mithril", "Weapon_Staff_Onyxium"]
ARMORY_ITEMS = {}   # id -> (asset path, vanilla JSON)
''')
after("    SPELL_ITEMS = dict((k, (v[0], _sread(v[0]))) for k, v in _si.items())\n",
      '''    # 0.4.15 (spec 15.3 (a)): the SkyyArmory-owned staffs leave the plan; nothing may inherit from them by Parent (none in Assets.zip today)
    for _aid in ARMORY_OWNED:
        if _aid not in SPELL_ITEMS:
            spell_fail("%s (owned by SkyyArmory since SkyySkills 0.4.15) is not in Assets.zip any more - the staff handover list needs a look" % _aid)
        ARMORY_ITEMS[_aid] = SPELL_ITEMS.pop(_aid)
    _aheirs = sorted(_k for _k, _v in SPELL_ITEMS.items() if isinstance(_v[1], dict) and _v[1].get("Parent") in ARMORY_OWNED)
    if _aheirs:
        spell_fail("%s inherit(s) a SkyyArmory-owned staff by Parent - the staff handover would change them too" % _aheirs)
''')
rep('''assert _sk["Weapon_Staff_Wood"][2] == 10 and _sk["Weapon_Wand_Wood"][2] == 5, (_sk.get("Weapon_Staff_Wood"), _sk.get("Weapon_Wand_Wood"))
''', '''# 0.4.15: the Mage kit staff is SkyyArmory's now (its Wood staff is checked against the pinned SkyyArmory jar below: check 10, spend 10)
assert _sk["Weapon_Wand_Wood"][2] == 5 and not set(ARMORY_OWNED) & set(_sk), (_sk.get("Weapon_Wand_Wood"), sorted(set(ARMORY_OWNED) & set(_sk)))
assert len(SPELL_PLAN) == len(SPELL_TABLE) and all(_t[0] not in ARMORY_OWNED for _t in SPELL_TABLE)
''')
rep('''assert _sg["Weapon_Staff_Wood"][1:] == ("Staff_Cast_Summon_Charged", 0, 10, 50, 10), _sg.get("Weapon_Staff_Wood")
''', r'''# 0.4.15 (spec 15.3 (b)): the staff check still serves the other staff-folder items (all spend 10) and Crystal_Red / Crystal_Ice (0) - its
# number stays 10, so the 8 interaction overrides are 0.4.14's; none of the SkyyArmory-owned staffs is in the gate table
_sfam = SPELL_FAMS["Staff_Cast_Summon_Charged"]
assert _sfam[0] == 10 and len(_sfam[1]) >= 10 and set(_sfam[2]) == set(["Weapon_Staff_Crystal_Ice", "Weapon_Staff_Crystal_Red"]), _sfam
assert not set(ARMORY_OWNED) & set(_sg) and not set(ARMORY_OWNED) & set(_sfam[1] + _sfam[2]), sorted(set(ARMORY_OWNED) & set(_sg))
# the kit lookup's fallback (ManaCost.ARM_CHECK / ARM_SPEND): what a cast of a SkyyArmory-owned staff checks and spends on its VANILLA file
# behind this jar's interactions (SkyyArmory missing) - the same gate simulation: vanilla Staff_Primary -> this jar's Staff_Cast_Summon_Charged
# (check 10), the vanilla item var spends 50. That is why the two mods deploy together.
ARMORY_GATES = []
for _aid in ARMORY_OWNED:
    _aitems = dict(_s_items_old)
    _aitems[_aid] = ARMORY_ITEMS[_aid][1]
    _ar = spell_casts(_spell_eff_item(_aitems, _aid, 0), _s_ints_new, SPELL_ROOTS)
    if _ar["free"] or _ar["fail"] or _ar["gain"] or len(_ar["casts"]) != 1 or _ar["casts"][0][1] != ("int", "Staff_Cast_Summon_Charged"):
        spell_fail("the vanilla %s no longer casts through Staff_Cast_Summon_Charged (the handover fallback needs a look): %s" % (_aid, _ar))
    ARMORY_GATES.append((_aid, _ar["casts"][0][0], -sum(_v for _v, _src in _ar["casts"][0][2])))
assert [_g[0] for _g in ARMORY_GATES] == ARMORY_OWNED and all(_g[1] == 10 and _g[2] == 50 for _g in ARMORY_GATES), ARMORY_GATES
''')
rep('''def _spell_clash(names):
    return sorted(n for n in names if n in SPELL_FILES or (n.startswith("Server/Item/Items/") and n.endswith(".json")
                                                           and os.path.basename(n)[:-5] in _sk)
                  or (n.startswith("Server/Item/Interactions/") and n.endswith(".json") and os.path.basename(n)[:-5] in SPELL_INT_IDS))
_checked = []
for _mod, _ver in _pins:
    if _mod == "SkyySkills":
        continue
    _jp = os.path.join(os.path.dirname(HERE), _mod, "%s-%s.jar" % (_mod, _ver))
    if not os.path.isfile(_jp):
        print("spell costs: NOTE %s %s is not built here - its items were not checked" % (_mod, _ver))
        continue
    with zipfile.ZipFile(_jp) as _jz:
        _cl = _spell_clash(_jz.namelist())
    if _cl:
        spell_fail("%s %s (live set) also ships %s" % (_mod, _ver, _cl[:5]))
    _checked.append(_mod)
''', r'''def _spell_clash(names, armory=False):
    """the files of a jar / mod listing that would fight with this jar: one of its generated files, the item file of one of its overridden
    items, the interaction file of one of its 8 overridden interactions - and (0.4.15, spec 15.3 (d)) the item file of a SkyyArmory-owned
    staff, except in SkyyArmory itself (armory=True: it must ship them)"""
    return sorted(n for n in names if n in SPELL_FILES or (n.startswith("Server/Item/Items/") and n.endswith(".json")
                                                           and (os.path.basename(n)[:-5] in _sk
                                                                or (not armory and os.path.basename(n)[:-5] in ARMORY_OWNED)))
                  or (n.startswith("Server/Item/Interactions/") and n.endswith(".json") and os.path.basename(n)[:-5] in SPELL_INT_IDS))


def _armory_jar_check(jz, ver):
    """0.4.15 (spec 15.3 (c) + (d)): a pinned SkyyArmory jar ships all 8 staffs it owns (a missing one would leave the vanilla file behind
    this jar's 10-Mana check: it spends 50) and its Wood staff checks AND spends 10 - the kit number Skyy's "Mage 30 = 3 staff casts" was
    set for. Returns (check, spend) of the Wood staff."""
    _nm = jz.namelist()
    _miss = [_a for _a in ARMORY_OWNED if not any(_n.startswith("Server/Item/Items/") and _n.endswith("/%s.json" % _a) for _n in _nm)]
    if _miss:
        spell_fail("SkyyArmory %s does not ship %s - the 8 ladder staffs moved from SkyySkills to SkyyArmory in SkyySkills 0.4.15 (a missing "
                   "staff runs on its vanilla file: it spends 50 Mana behind a 10-Mana check)" % (ver, _miss))

    def _one(base):
        _h = [_n for _n in _nm if _n.startswith("Server/Item/Interactions/") and _n.endswith("/%s.json" % base)]
        if len(_h) != 1:
            spell_fail("SkyyArmory %s ships %d x %s.json under Server/Item/Interactions (want exactly one)" % (ver, len(_h), base))
        return json.loads(jz.read(_h[0]).decode("utf-8-sig"))
    _c, _d = _one("SkyyArmory_Staff_Cast_Wood"), _one("SkyyArmory_Staff_Cast_Cost_Wood")
    _cm = (_c.get("Costs") or {}).get("Mana") if _c.get("Type") == "StatsCondition" else None
    _dm = (_d.get("StatModifiers") or {}).get("Mana") if _d.get("Type") == "ChangeStat" else None
    if _cm != 10 or _dm != -10:
        spell_fail("SkyyArmory %s: its Wood staff checks %r and spends %r Mana - the Mage kit staff must check and spend 10 (SkyyArmory-Spec "
                   "15.2; Base Mana Mage 30 = 3 casts)" % (ver, _cm, (-_dm if isinstance(_dm, (int, float)) and not isinstance(_dm, bool) else _dm)))
    return (_cm, -_dm)
_checked = []
_armory_pin = None
for _mod, _ver in _pins:
    if _mod == "SkyySkills":
        continue
    if _mod == "SkyyArmory":
        _armory_pin = _ver
    _jp = os.path.join(os.path.dirname(HERE), _mod, "%s-%s.jar" % (_mod, _ver))
    if not os.path.isfile(_jp):
        print("spell costs: NOTE %s %s is not built here - its items were not checked" % (_mod, _ver))
        continue
    with zipfile.ZipFile(_jp) as _jz:
        _cl = _spell_clash(_jz.namelist(), armory=(_mod == "SkyyArmory"))
        if _mod == "SkyyArmory":
            _aw = _armory_jar_check(_jz, _ver)
            print("staff handover: SkyyArmory %s ships the %d ladder staffs; its Wood staff checks %d and spends %d Mana (the kit number)" % (
                _ver, len(ARMORY_OWNED), _aw[0], _aw[1]))
    if _cl:
        spell_fail("%s %s (live set) also ships %s" % (_mod, _ver, _cl[:5]))
    _checked.append(_mod)
_skills_pin = dict(_pins).get("SkyySkills", "0")
if _armory_pin is None and tuple(int(_x) for _x in _skills_pin.split(".")) >= tuple(int(_x) for _x in VERSION.split(".")):
    # fix round (review: a partial pin passed every check): once SkyySkills 0.4.15+ is pinned, SkyyArmory must be pinned beside it
    spell_fail("SkyySkills %s is pinned in tools/deploy_set.py SET without SkyyArmory - pin SkyyArmory 0.1+ (and SkyyClasses 0.1.11) in the "
               "same deploy: without it the %d ladder staffs run on their vanilla files (a cast spends 50 Mana behind a 10-Mana check)" % (
                   _skills_pin, len(ARMORY_OWNED)))
if _armory_pin is None:
    print("staff handover: NOTE SkyyArmory is not in tools/deploy_set.py SET yet - SkyySkills %s must be pinned and deployed TOGETHER with "
          "SkyyArmory 0.1+ (without it the %d ladder staffs run on their vanilla files: a cast spends 50 Mana behind a 10-Mana check)" % (
              VERSION, len(ARMORY_OWNED)))
''')
rep('''    _key = "%s:%s" % (_man.get("Group"), _man.get("Name"))
    _cl = _spell_clash(_nm)
''', '''    _key = "%s:%s" % (_man.get("Group"), _man.get("Name"))
    _cl = _spell_clash(_nm, armory=(_man.get("Group") == "Skyy" and str(_man.get("Name", "")).endswith(" SkyyArmory")))   # 0.4.15: it owns the 8
''')
before("# the modifier keys (spec 4.12): our own prefix, distinct, never SkyyAccessories' skyyacc_* or the coming SkyyGear's skyygear*\n",
       '''print("staff handover (0.4.15): %d ladder staffs left to SkyyArmory (%s) - %d item overrides remain; a vanilla ladder staff behind this "
      "jar's interactions would check %d and spend %d Mana (the kit lookup's fallback, used only while SkyyArmory does not answer)" % (
          len(ARMORY_OWNED), ", ".join(_a[13:] for _a in ARMORY_OWNED), len(SPELL_PLAN), ARMORY_GATES[0][1], ARMORY_GATES[0][2]))
''')
rep('''OVL_KEYS = ["skyyskill_basemana", "skyyskill_overallhp", "skyyskill_overallmana"]
assert len(set(OVL_KEYS)) == 3 and all(k.startswith("skyyskill_") for k in OVL_KEYS)
''', '''OVL_KEYS = ["skyyskill_basemana", "skyyskill_overallhp", "skyyskill_overallmana", "skyyskill_classmana"]   # 0.4.15: + max Mana per class level
assert len(set(OVL_KEYS)) == 4 and all(k.startswith("skyyskill_") for k in OVL_KEYS)
''')

# ---------------------------------------------------------------------------------------------------------------- the new classes
after('dmig = pool.makeClass(PKG + ".DocMig")\n', '''# 0.4.15: max Mana per class level (ClassMana: the mana.classPerLevel table + the per-player amount / texts) and its one-time default lines in an
# existing xp.properties (ClassManaMig)
cman = pool.makeClass(PKG + ".ClassMana")
cmig = pool.makeClass(PKG + ".ClassManaMig")
''')

# ---------------------------------------------------------------------------------------------------------------- ClassMana part 1: the table (before SkillCfg.load)
CMAN_CFG = r'''# ================= ClassMana part 1 (0.4.15, research/SkyyArmory-Spec.md 15.4): the mana.classPerLevel table (before SkillCfg.load) =================
# mana.classPerLevel.<Class>=<Mana per level>: entries are class names in any case, stored and shown in the SkillDefs.CLASSES spelling and
# order (OverallCfg.mkTable, the Base Mana by class rules); values clamped to 0-100 like the row bounds; a line that is not a class or not
# a number is left out with one WARN per new problem text. TBL = ONE snapshot Object[]{String[] classes, double[] per level, String text}
# (null = not read yet = the default table; a file without the lines = an empty table = no class level Mana).
cman.addField(CtField.make('public static final String TABLE_PREFIX = "mana.classPerLevel.";', cman))
cman.addField(CtField.make("public static final String[] DEF_CLS = %s;" % jarr([_c for _c, _v in CLASS_MANA_DEF]), cman))
cman.addField(CtField.make("public static final double[] DEF_PER = new double[] { %s };" % ", ".join("%d.0" % _v for _c, _v in CLASS_MANA_DEF), cman))
cman.addField(CtField.make("public static final double MAX_PER = 100.0;", cman))
cman.addField(CtField.make("public static volatile Object[] TBL = null;", cman))
cman.addField(CtField.make('public static volatile String WARNED = "";', cman))
cman.addField(CtField.make("public static boolean FAILED_ONCE = false;", cman))
cman.addMethod(CtNewMethod.make(J14(r"""
public static Object[] defTable() {
  return @PKG@.OverallCfg.mkTable(DEF_CLS, DEF_PER);
}"""), cman))
cman.addMethod(CtNewMethod.make(J14(r"""
public static Object[] tbl() {
  Object[] t = TBL;
  if (t == null) {
    t = defTable();
    TBL = t;
  }
  return t;
}"""), cman))
# the table lines -> {String[], double[], String text, String problems ("" = none)}; keys in sorted order (of two spellings of one class the
# exact SkillDefs.CLASSES spelling wins - capital letters sort first - and the other is reported)
cman.addMethod(CtNewMethod.make(J14(r"""
public static Object[] parseTable(java.util.Properties p) {
  java.util.ArrayList cs = new java.util.ArrayList();
  java.util.ArrayList bs = new java.util.ArrayList();
  StringBuilder bad = new StringBuilder();
  java.util.Iterator it = new java.util.TreeSet(p.stringPropertyNames()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith(TABLE_PREFIX)) continue;
    String e = k.substring(TABLE_PREFIX.length()).trim();
    String c = @PKG@.OverallCfg.canonClass(e);
    String raw = p.getProperty(k);
    String shown = e.length() > 40 ? e.substring(0, 40) + "..." : e;
    if (c == null) { if (bad.length() > 0) bad.append("; "); bad.append(shown + " is not a class (left out)"); continue; }
    if (cs.contains(c)) { if (bad.length() > 0) bad.append("; "); bad.append(c + " is listed twice (" + shown + " left out)"); continue; }
    double v = Double.NaN;
    try { v = Double.parseDouble(raw.trim()); } catch (Throwable t) { v = Double.NaN; }
    if (Double.isNaN(v) || Double.isInfinite(v)) {
      if (bad.length() > 0) bad.append("; ");
      String rv = raw == null ? "" : raw.trim();
      bad.append(shown + "=" + (rv.length() > 20 ? rv.substring(0, 20) + "..." : rv) + " is not a number (left out)");
      continue;
    }
    cs.add(c);
    bs.add(Double.valueOf(@PKG@.OverallCfg.clampD(v, 0.0, 0.0, MAX_PER)));
  }
  String[] c2 = new String[cs.size()];
  double[] b2 = new double[cs.size()];
  for (int i = 0; i < c2.length; i++) { c2[i] = (String) cs.get(i); b2[i] = ((Double) bs.get(i)).doubleValue(); }
  Object[] t = @PKG@.OverallCfg.mkTable(c2, b2);
  return new Object[] { t[0], t[1], t[2], bad.toString() };
}"""), cman))
cman.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  Object[] t = parseTable(p);
  TBL = new Object[] { t[0], t[1], t[2] };
  String w = ((String) t[3]).length() > 0 ? "Max Mana per class level: " + (String) t[3] : "";
  if (w.length() > 0 && !w.equals(WARNED)) @PKG@.SkillCfg.warn(w);
  WARNED = w;
}"""), cman))
# the entry of a class (any case), 0 = not listed
cman.addMethod(CtNewMethod.make(J14(r"""
public static double perLevel(String cls) {
  if (cls == null) return 0.0;
  String x = cls.trim();
  Object[] t = tbl();
  String[] c = (String[]) t[0];
  double[] b = (double[]) t[1];
  for (int i = 0; i < c.length && i < b.length; i++) if (c[i].equalsIgnoreCase(x)) return b[i];
  return 0.0;
}"""), cman))
cman.addMethod(CtNewMethod.make(J14(r"""
public static String tableText() {
  return (String) tbl()[2];
}"""), cman))
# load text / ready line: "Mage 10, Priest 5 per level of the class skill" / "none listed" / "off (Base Mana is off)"
cman.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  if (!@PKG@.OverallCfg.MANA_ON) return "off (Base Mana is off)";
  String tt = tableText();
  return tt.length() > 0 ? tt + " per level of the class skill" : "none listed";
}"""), cman))
# check= hook of the table (CONFIG-CONTRACT: key = "mana.classPerLevel[<entry>]", value = the canonical text or null for a removal; also run
# for hand-edited lines, kit 1.1): the entry must be a class name (the 0-100 bounds are the row's own)
cman.addMethod(CtNewMethod.make(J14(r"""
public static String checkEntry(String key, String value) {
  if (value == null || key == null) return null;
  String e = key;
  int a = key.indexOf('[');
  int b = key.lastIndexOf(']');
  if (a >= 0 && b > a) e = key.substring(a + 1, b);
  if (@PKG@.OverallCfg.canonClass(e) != null) return null;
  if (e.length() > 40) e = e.substring(0, 40) + "...";
  return "Unknown class " + e + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Shaman.";
}"""), cman))

'''
before("# ================= BridgeCfg (0.4): bridge.* keys (skill:fn:addxp / skill:fn:craftxp) =================\n", CMAN_CFG)
after("    {PKG}.Sickle.read(p);       // 0.4.14: sickle swings\n", "    {PKG}.ClassMana.read(p);    // 0.4.15: max Mana per class level (the mana.classPerLevel table)\n")
rep('''", sickle swings " + {PKG}.Sickle.text() + (bad > 0 ?''', '''", sickle swings " + {PKG}.Sickle.text() + ", max Mana per class level " + {PKG}.ClassMana.text() + (bad > 0 ?''')

# ---------------------------------------------------------------------------------------------------------------- ClassMana part 2: per player (after Overall)
CMAN_PLAYER = r'''# ================= ClassMana part 2 (0.4.15): the per-player amount (Perks.ovl), the Stats page line, the /skills mana line =================
# Pure (any thread) except breakdown (world thread: ManaCmd reads the live stat map). amountFor = entry x the level of THAT class's own skill
# (SkillClass.slotOfClass: Priest -> Divinity, Mage -> Sorcery) in the profile data d; 0 while Base Mana is off, for no class, an unlisted
# or unknown class or level 0. amount = the ACTIVE profile's class (Overall.classOf: profile:class:<uuid> first, else class:<uuid>);
# -1 = an error (Perks.ovl then leaves the saved modifier alone instead of removing it: no dip of max Mana).
cman.addMethod(CtNewMethod.make(J14(r"""
public static float amountFor(String cls, long[] d) {
  if (!@PKG@.OverallCfg.MANA_ON || cls == null || d == null) return 0.0f;
  double per = perLevel(cls);
  if (!(per > 0.0)) return 0.0f;
  int s = @PKG@.SkillClass.slotOfClass(cls);
  if (s < 0 || s >= @PKG@.SkillDefs.N || s >= d.length) return 0.0f;
  int lv = @PKG@.SkillDefs.levelOf(s, d[s]);
  if (lv <= 0) return 0.0f;
  return @PKG@.Overall.round2(per * (double) lv);
}"""), cman))
cman.addMethod(CtNewMethod.make(J14(r"""
public static float amount(java.util.UUID u, long[] d) {
  try {
    return amountFor(@PKG@.Overall.classOf(u), d);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("max Mana per class level failed (logged once, the saved value is kept): " + t); }
    return -1.0f;
  }
}"""), cman))
# the class skill's Stats page (StatsPage.lines): now "+50 max Mana (5 per Divinity level, Priest only)", next level "+5 max Mana"; null = no
# line (not a class skill, the class is not listed, Base Mana off, level 0)
cman.addMethod(CtNewMethod.make(J14(r"""
public static String statsLine(int s, int lv, boolean next) {
  if (!@PKG@.OverallCfg.MANA_ON || !@PKG@.SkillDefs.isClass(s)) return null;
  int ci = @PKG@.SkillDefs.classIdx(s);
  if (ci < 0 || ci >= @PKG@.SkillDefs.CLASSES.length) return null;
  String cls = @PKG@.SkillDefs.CLASSES[ci];
  double per = perLevel(cls);
  if (!(per > 0.0)) return null;
  if (next) return "+" + @PKG@.Overall.num((double) @PKG@.Overall.round2(per)) + " max Mana";
  if (lv <= 0) return null;
  return "+" + @PKG@.Overall.num((double) @PKG@.Overall.round2(per * (double) lv)) + " max Mana (" + @PKG@.Overall.num(per) + " per " + @PKG@.SkillDefs.LABELS[s] + " level, " + cls + " only)";
}"""), cman))
# one of our MAX modifiers on the stat, as posted (0 = none)
cman.addMethod(CtNewMethod.make(J14(r"""
public static float modAmt(@ESM@ m, int idx, String key) {
  try {
    @MOD@ x = m.getModifier(idx, key);
    if (x instanceof @SMO@) return ((@SMO@) x).getAmount();
  } catch (Throwable t) { }
  return 0.0f;
}"""), cman))
# the admin /skills mana line: the live max Mana by source - "Max Mana 80.2 = base 30 + class level 50 (Priest 5 x Divinity 10) + Overall 0.2
# + skill perks 0" (+ "other mods N" for trees, accessories and armor; + "vanilla N" if the stat type's own max is not 0)
cman.addMethod(CtNewMethod.make(J14(r"""
public static String breakdown(java.util.UUID u, @ESM@ m, int mi, float max) {
  if (m == null || mi < 0) return "Max Mana: no Mana value";
  float tm = @PKG@.Overall.typeMax(mi);
  float b = modAmt(m, mi, "skyyskill_basemana");
  float c = modAmt(m, mi, "skyyskill_classmana");
  float o = modAmt(m, mi, "skyyskill_overallmana");
  float k = modAmt(m, mi, "skyyskill_mana");
  float rest = max - tm - b - c - o - k;
  String cls = @PKG@.Overall.classOf(u);
  double per = perLevel(cls);
  int s = cls == null ? -1 : @PKG@.SkillClass.slotOfClass(cls);
  String why = "";
  if (!@PKG@.OverallCfg.MANA_ON) why = " (Base Mana is off)";
  else if (per > 0.0 && s >= 0) {
    long[] d = @PKG@.SkillStore.data(u);
    why = " (" + @PKG@.OverallCfg.canonClass(cls) + " " + @PKG@.Overall.num(per) + " x " + @PKG@.SkillDefs.LABELS[s] + " " + @PKG@.SkillDefs.levelOf(s, d[s]) + ")";
  } else why = " (" + (cls == null ? "no class" : cls + " gains none") + ")";
  StringBuilder sb = new StringBuilder("Max Mana ");
  sb.append(@PKG@.Overall.num((double) max)).append(" = ");
  if (tm != 0.0f) sb.append("vanilla ").append(@PKG@.Overall.num((double) tm)).append(" + ");
  sb.append("base ").append(@PKG@.Overall.num((double) b));
  sb.append(" + class level ").append(@PKG@.Overall.num((double) c)).append(why);
  sb.append(" + Overall ").append(@PKG@.Overall.num((double) o));
  sb.append(" + skill perks ").append(@PKG@.Overall.num((double) k));
  if (Math.abs(rest) >= 0.005f) sb.append(" + other mods ").append(@PKG@.Overall.num((double) rest)).append(" (trees, accessories, armor)");
  return sb.toString();
}"""), cman))

'''
before("# ================= skill:fn:overall (0.4.6, spec 4.8): apply(UUID) or apply(Object[]{UUID}) -> Object[]{Integer level, Integer averageTenths,\n",
       CMAN_PLAYER)

# ---------------------------------------------------------------------------------------------------------------- Perks.ovl, the Stats page, /skills mana
after('''    mod(m, mi, "skyyskill_basemana", {PKG}.Overall.baseMana(u, {PKG}.Overall.typeMax(mi)));
''', '''    float cmn = {PKG}.ClassMana.amount(u, {PKG}.SkillStore.data(u));   // 0.4.15: max Mana per class level (Priest x Divinity, Mage x Sorcery)
    if (cmn >= 0.0f) mod(m, mi, "skyyskill_classmana", cmn);           // 0 = removed (no class level Mana); -1 = an error: the saved one stays
''')
after('''  stat(out, {PKG}.PerkCfg.MANA[row], lv, next, "max Mana");
''', '''  String cmn = {PKG}.ClassMana.statsLine(s, lv, next);   // 0.4.15: max Mana per class level (Priest 5 per Divinity level, Mage 10 per Sorcery level)
  if (cmn != null) out.add(cmn);
''')
after('''      pr.sendMessage({MSG}.raw("[Skills] Mana " + {PKG}.Overall.num((double) v.get()) + " / " + {PKG}.Overall.num((double) v.getMax()) + " - " + st + hit).color("#c8b070"));
''', '''      pr.sendMessage({MSG}.raw("[Skills] " + {PKG}.ClassMana.breakdown(u, m, mi, v.getMax())).color("#c8b070"));   // 0.4.15: max Mana by source
''')

# ---------------------------------------------------------------------------------------------------------------- the config row (+ its checks)
after('''    ("mana.classBase", "Base Mana by class", "overall", "table", "", "0", "10000", "dec;type;Base Mana", "", "live",
     "Max Mana a listed class starts with, instead of the base above (Mage 30 = 3 staff casts).", "reload;check=OverallCfg.checkClassBase"),
''', '''    # 0.4.15 (research/SkyyArmory-Spec.md 15.4, Skyy 2026-10-03): max Mana per level of the class's own skill (Priest 5, Mage 10)
    ("mana.classPerLevel", "Max Mana per class level", "overall", "table", "", "0", "100", "dec;type;Mana per level", "", "live",
     "Max Mana a listed class gains per level of its own class skill (Priest: Divinity, Mage: Sorcery).", "reload;check=ClassMana.checkEntry"),
''')
rep('''for _tk, _pfx in (("block", "block."), ("prefix", "prefix."), ("suffix", "suffix."), ("alchemy.xp", "alchemy.xp."), ("smithing.xp", "smithing.xp."),
                 ("mana.classBase", "mana.classBase.")):
''', '''for _tk, _pfx in (("block", "block."), ("prefix", "prefix."), ("suffix", "suffix."), ("alchemy.xp", "alchemy.xp."), ("smithing.xp", "smithing.xp."),
                 ("mana.classBase", "mana.classBase."), ("mana.classPerLevel", "mana.classPerLevel.")):   # 0.4.15: + the class level table
''')
rep('''assert len(CFG_ROWS) == 195, ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows (Overall-Level-Spec 4.9) + divinity.healXpPerHpSelf + "
                              "3 crossbow extras (meter, sound, hint); 0.4.8: - mana.magicBase / mana.magicClasses + the mana.classBase "
                              "table + the read-only spell.manaDivisor; 0.4.10: + classSkill.xpMultiplier; 0.4.12: + the 4 class curve "
                              "rows + mana.regen.inCombat + the mana.regen.show action; 0.4.14: + the 15 rows of N14_L, got %d" % len(CFG_ROWS))   # 0.4.6 / 0.4.8 / 0.4.10 / 0.4.12 / 0.4.14
''', '''assert len(CFG_ROWS) == 196, ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows (Overall-Level-Spec 4.9) + divinity.healXpPerHpSelf + "
                              "3 crossbow extras (meter, sound, hint); 0.4.8: - mana.magicBase / mana.magicClasses + the mana.classBase "
                              "table + the read-only spell.manaDivisor; 0.4.10: + classSkill.xpMultiplier; 0.4.12: + the 4 class curve "
                              "rows + mana.regen.inCombat + the mana.regen.show action; 0.4.14: + the 15 rows of N14_L; 0.4.15: + the "
                              "mana.classPerLevel table, got %d" % len(CFG_ROWS))   # 0.4.6 / 0.4.8 / 0.4.10 / 0.4.12 / 0.4.14 / 0.4.15
''')
after('''assert sum(1 for _r in CFG_ROWS if _r[0] == "mana.classBase") == 1 and sum(1 for _r in CFG_ROWS if _r[0] == "spell.manaDivisor") == 1
''', '''# 0.4.15: the class level table - its default entries in the default file AND in the CMAN block (ClassManaMig appends it to an old file), right
# after mana.classBase in the rows, its classes real classes in SkillDefs.CLASSES order; no other row or table key inside its family
for _cc, _cv in CLASS_MANA_DEF:
    assert _dp.get("mana.classPerLevel." + _cc) == str(_cv) and ("\\nmana.classPerLevel.%s=%d\\n" % (_cc, _cv)) in ("\\n" + CMAN_DEFAULTS), _cc
assert sorted(_k for _k in _dp if _k.startswith("mana.classPerLevel.")) == sorted(CMAN_KEYS)
_k15 = [_r[0] for _r in CFG_ROWS]
assert _k15.count("mana.classPerLevel") == 1 and _k15[_k15.index("mana.classBase") + 1] == "mana.classPerLevel"
assert [_r for _r in CFG_ROWS if _r[0] == "mana.classPerLevel"][0][2:10] == ("overall", "table", "", "0", "100", "dec;type;Mana per level", "", "live")
assert not any(_k.startswith("mana.classPerLevel") for _k in _k15 if _k != "mana.classPerLevel")
assert [_c for _c, _v in CLASS_MANA_DEF] == [_c[0] for _c in CLASS_ROWS if _c[0] in dict(CLASS_MANA_DEF)], "CLASS_MANA_DEF must follow SkillDefs.CLASSES order"
''')
rep('''                  ("CLS", CLS_DEFAULTS), ("CURVE", CURVE_DEFAULTS), ("MREG", MREG_DEFAULTS), ("N14", N14_DEFAULTS)):
''', '''                  ("CLS", CLS_DEFAULTS), ("CURVE", CURVE_DEFAULTS), ("MREG", MREG_DEFAULTS), ("N14", N14_DEFAULTS), ("CMAN", CMAN_DEFAULTS)):
''')

# ---------------------------------------------------------------------------------------------------------------- ManaCost: the kit lookup of the 8 staffs
after('''mcost.addField(CtField.make("public static final int[] INT_NEW = new int[] { %s };" % ", ".join(str(_x[4]) for _x in SPELL_INT_PLAN), mcost))
''', r'''# 0.4.15 (spec 15.3 (e)): the 8 SkyyArmory-owned staffs are not in GIDS any more (no override here). costOf / spendOf ask SkyyArmory
# (armory:fn:info {"staff", id} -> Object[]{Integer charged Mana, ...}: its check = its spend); without an answer ARM_CHECK / ARM_SPEND = what
# the VANILLA file does behind this jar's interactions (the SPELL GEN gate simulation: check 10, spend 50 - SkyyArmory missing)
mcost.addField(CtField.make("public static final String[] ARM_IDS = %s;" % jarr([_g[0] for _g in ARMORY_GATES]), mcost))
mcost.addField(CtField.make("public static final int[] ARM_CHECK = new int[] { %s };" % ", ".join(str(_g[1]) for _g in ARMORY_GATES), mcost))
mcost.addField(CtField.make("public static final int[] ARM_SPEND = new int[] { %s };" % ", ".join(str(_g[2]) for _g in ARMORY_GATES), mcost))
mcost.addMethod(CtNewMethod.make(J14(r"""
public static int ai(String id) {
  if (id == null) return -1;
  for (int i = 0; i < ARM_IDS.length; i++) if (ARM_IDS[i].equals(id)) return i;
  return -1;
}"""), mcost))
# SkyyArmory's charged Mana for a staff it owns (> 0), -1 = no answer (no SkyyArmory, no such staff, anything else); any thread, never throws
mcost.addMethod(CtNewMethod.make(J14(r"""
public static int armory(String id) {
  try {
    Object f = @PKG@.SkillStore.bridge().get("armory:fn:info");
    if (!(f instanceof java.util.function.Function)) return -1;
    Object r = ((java.util.function.Function) f).apply(new Object[] { "staff", id });
    if (!(r instanceof Object[])) return -1;
    Object[] a = (Object[]) r;
    if (a.length < 1 || !(a[0] instanceof Number)) return -1;
    int c = ((Number) a[0]).intValue();
    return c > 0 ? c : -1;
  } catch (Throwable t) { return -1; }
}"""), mcost))
''')
rep('''mcost.addMethod(CtNewMethod.make("""
public static int costOf(String id) {
  int i = gi(id);
  return i < 0 ? -1 : GATE[i];
}""", mcost))
''', '''mcost.addMethod(CtNewMethod.make("""
public static int costOf(String id) {
  int i = gi(id);
  if (i >= 0) return GATE[i];
  int a = ai(id);
  if (a < 0) return -1;
  int c = armory(id);
  return c > 0 ? c : ARM_CHECK[a];
}""", mcost))
''')
rep('''mcost.addMethod(CtNewMethod.make("""
public static int spendOf(String id) {
  int i = gi(id);
  return i < 0 ? -1 : SPEND[i];
}""", mcost))
''', '''mcost.addMethod(CtNewMethod.make("""
public static int spendOf(String id) {
  int i = gi(id);
  if (i >= 0) return SPEND[i];
  int a = ai(id);
  if (a < 0) return -1;
  int c = armory(id);
  return c > 0 ? c : ARM_SPEND[a];
}""", mcost))
''')

# ---------------------------------------------------------------------------------------------------------------- ManaGuard: the staff handover pack check
after('''mgd.addField(CtField.make('public static volatile String INT_LAST = "";', mgd))
''', '''mgd.addField(CtField.make("public static volatile boolean ARM_DONE = false;", mgd))   # 0.4.15: the staff handover pack check
mgd.addField(CtField.make('public static volatile String ARM_LAST = "";', mgd))
''')
before('''# 0.4.9: both checks (the items as in 0.4.8, the interactions new), each logged once as soon as it is readable; after PACK_MAX tries the
''', r'''# ---- 0.4.15 staff handover (spec 15.3 (f)): which asset pack the game's item assets take the 8 SkyyArmory-owned staffs from - every one from
# a "Skyy:<version> SkyyArmory" pack = INFO, else WARN (they run on another pack's file: the vanilla one spends 50 Mana behind this jar's
# 10-Mana check). packs[i] for ManaCost.ARM_IDS[i] (null = not there / not readable) -> {level "info" / "warn" / "" (nothing readable - try
# again) / "skip" (no staff to check), message}
mgd.addMethod(CtNewMethod.make(J14(r"""
public static boolean armoryPack(String p) {
  return p != null && p.startsWith("Skyy:") && p.endsWith(" SkyyArmory");
}"""), mgd))
mgd.addMethod(CtNewMethod.make(J14(r"""
public static String[] armReport(String[] packs) {
  String[] ids = @PKG@.ManaCost.ARM_IDS;
  if (ids.length == 0) return new String[] { "skip", "" };
  int mine = 0;
  int other = 0;
  int miss = 0;
  String pk = null;
  StringBuilder ot = new StringBuilder();
  for (int i = 0; i < ids.length; i++) {
    String p = (packs != null && i < packs.length) ? packs[i] : null;
    if (p == null) { miss++; continue; }
    if (armoryPack(p)) { mine++; pk = p; continue; }
    other++;
    if (ot.length() > 0) ot.append(", ");
    ot.append(ids[i]).append(" (").append(p).append(")");
  }
  if (mine + other == 0) return new String[] { "", "the game's item assets could not be read" };
  String pre = "Staff handover: ";
  String mt = miss > 0 ? "; " + miss + " not in the game's item assets" : "";
  if (other == 0) return new String[] { "info", pre + (miss == 0 ? "all " + mine : mine + " of " + ids.length) + " ladder staffs (Wood to Onyxium) come from " + pk + " - their Mana and orbs are SkyyArmory's staff ladder" + mt };
  return new String[] { "warn", pre + other + " of " + ids.length + " ladder staffs do NOT come from SkyyArmory: " + ot.toString() + ". SkyySkills @VERSION@ no longer ships them, so they run on that pack's file - the vanilla one spends 50 Mana behind SkyySkills' 10-Mana check. Install SkyyArmory 0.1+ together with this SkyySkills (they deploy and roll back as a pair)" + mt + "." };
}"""), mgd))
mgd.addMethod(CtNewMethod.make(J14(r"""
public static String[] armCheck() {
  String[] ids = @PKG@.ManaCost.ARM_IDS;
  String[] ps = new String[ids.length];
  try {
    com.hypixel.hytale.assetstore.map.DefaultAssetMap m = @ITM@.getAssetMap();
    if (m != null) {
      for (int i = 0; i < ids.length; i++) {
        try { ps[i] = m.getAssetPack(ids[i]); } catch (Throwable t) { ps[i] = null; }
      }
    }
  } catch (Throwable t) { }
  return armReport(ps);
}"""), mgd))
''')
rep('''  if (ITEMS_DONE && INT_DONE) {{
    PACK_DONE = true;
    return;
  }}
  if (PACK_TRIES >= PACK_MAX) {{
    PACK_DONE = true;
''', '''  if (!ARM_DONE) {{   // 0.4.15: the staff handover - which pack the 8 SkyyArmory-owned staffs come from
    String[] a = armCheck();
    if (a[0].length() > 0) {{
      ARM_DONE = true;
      ARM_LAST = a[1];
      if ("warn".equals(a[0])) {PKG}.SkillCfg.warn(a[1]);
      else if ("info".equals(a[0])) {PKG}.SkillCfg.info(a[1]);
    }}
  }}
  if (ITEMS_DONE && INT_DONE && ARM_DONE) {{
    PACK_DONE = true;
    return;
  }}
  if (PACK_TRIES >= PACK_MAX) {{
    PACK_DONE = true;
    if (!ARM_DONE) {{
      ARM_LAST = "Staff handover: the game's item assets could not be read to see which pack the " + {PKG}.ManaCost.ARM_IDS.length + " SkyyArmory-owned staffs come from - not checked";
      {PKG}.SkillCfg.info(ARM_LAST);
    }}
''')

# ---------------------------------------------------------------------------------------------------------------- ClassManaMig: the default lines, once
CMIG = r'''# ---- ClassManaMig (0.4.15, spec 15.4 "The config file"): the max Mana per class level lines reach an EXISTING xp.properties ONCE. setup() only,
# after DocMig.run, BEFORE SkillCfg.load and CfgPub.start (the kit owns every write after that). Nothing to do = no file (load() writes the
# 0.4.15 default with the block), a mana.classPerLevel line in the file (an admin's table is never merged into), or a comment line holding
# MARK_ID (the block was added before - an emptied table stays empty). Else the block is appended after the last line in the file's OWN line
# ending (ISO-8859-1 bytes; one blank line before it like SkillCfg.appendBlock); a Properties check (every old key keeps its value, exactly
# the default entries are new); config-history must hold the old bytes first (HealMig.mgKit + CfgHist.snapshot + mgSaved); the kit's
# atomicWrite; one config-changes.log line per entry in the kit's table format (Server Setup -> Changes -> Undo removes that entry); one
# INFO line. A failure = WARN, the file untouched, retried at the next start.
cmig.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(CMAN_MARK_ID), cmig))
cmig.addField(CtField.make("public static final String BLOCK = " + CMAN_LIT + ";", cmig))
cmig.addField(CtField.make("public static final String[] KEYS = %s;" % jarr([_c for _c, _v in CLASS_MANA_DEF]), cmig))
cmig.addField(CtField.make("public static final String[] VALS = %s;" % jarr([str(_v) for _c, _v in CLASS_MANA_DEF]), cmig))
cmig.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.15";', cmig))
cmig.addMethod(CtNewMethod.make(J14(r"""
public static boolean hasTableKey(java.util.Properties p) {
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) if (((String) it.next()).startsWith(@PKG@.ClassMana.TABLE_PREFIX)) return true;
  return false;
}"""), cmig))
# a comment line (per logical line - a continued value's tail is never taken for a comment) holding MARK_ID
cmig.addMethod(CtNewMethod.make(J14(r"""
public static boolean marked(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return true;
      k++;
      continue;
    }
    k = @PKG@.CfgFile.end(l, k) + 1;
  }
  return false;
}"""), cmig))
# pure text step (ISO-8859-1 chars in and out): null = nothing to do; else { new text, String[] { "mana.classPerLevel[<Class>]", "(none)",
# value }* } (the change-log rows). Never throws for any text.
cmig.addMethod(CtNewMethod.make(J14(r"""
public static Object[] plan(String text) {
  if (text == null) return null;
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }
  if (hasTableKey(p) || marked(text)) return null;
  boolean crlf = text.indexOf("\r\n") >= 0;
  String nl = crlf ? "\r\n" : "\n";
  String b = crlf ? BLOCK.replace("\n", "\r\n") : BLOCK;
  String pre = (text.length() == 0 || text.endsWith("\n")) ? nl : nl + nl;
  // a last line that ends in an odd number of backslashes continues onto the next line: one more blank line, so the block's header is
  // never read as part of that value
  String last = text.endsWith("\n") ? text.substring(0, text.length() - 1) : text;
  if (last.endsWith("\r")) last = last.substring(0, last.length() - 1);
  int bs = 0;
  for (int i = last.length() - 1; i >= 0 && last.charAt(i) == '\\'; i--) bs++;
  if (bs % 2 == 1 && text.endsWith("\n")) pre = pre + nl;
  String[] rows = new String[KEYS.length * 3];
  for (int i = 0; i < KEYS.length; i++) {
    rows[3 * i] = "mana.classPerLevel[" + KEYS[i] + "]";
    rows[3 * i + 1] = "(none)";
    rows[3 * i + 2] = VALS[i];
  }
  return new Object[] { text + pre + b, rows };
}"""), cmig))
cmig.addMethod(CtNewMethod.make(J14(r"""
public static boolean sameAfterAdd(byte[] old, byte[] nb) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties b = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    b.load(new java.io.ByteArrayInputStream(nb));
    if (b.size() != a.size() + KEYS.length) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String y = b.getProperty(k);
      if (y == null || !y.equals(a.getProperty(k))) return false;
    }
    for (int i = 0; i < KEYS.length; i++) {
      String y = b.getProperty(@PKG@.ClassMana.TABLE_PREFIX + KEYS[i]);
      if (y == null || !y.equals(VALS[i])) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}"""), cmig))
# one config-changes.log line in the kit's table format (key "tableKey[entry]", "(none)" for the side that did not exist), status ok
cmig.addMethod(CtNewMethod.make(J14(r"""
public static String logLine(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}"""), cmig))
cmig.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    if (!sameAfterAdd(old, data)) {
      @PKG@.SkillCfg.warn("xp.properties: the max Mana per class level lines were NOT added - appending them would change another setting (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = @PKG@.HealMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.HealMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.15 max Mana per class level lines");
    if (!@PKG@.HealMig.mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties: the max Mana per class level lines were NOT added - the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[1];
    StringBuilder what = new StringBuilder();
    for (int i = 0; i + 2 < rows.length; i += 3) {
      @PKG@.CfgLog.enqueue(logLine(rows[i], rows[i + 1], rows[i + 2]));
      if (what.length() > 0) what.append(", ");
      what.append(KEYS[i / 3]).append(" ").append(rows[i + 2]);
    }
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String msg = "xp.properties: added Max Mana per class level " + what.toString() + " per level of the class's own skill (Priest: Divinity, Mage: Sorcery) - nothing else changed; the old file is in config-history and Server Setup -> Changes can undo each entry";
    @PKG@.SkillCfg.info(msg);
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not add the max Mana per class level lines to xp.properties (the file is used as it is): " + t);
    return "";
  }
}"""), cmig))

'''
before("# ---- ManaGuard (point 3): WARN once per class whose base Mana is below the Mana cost of a weapon in its class kit. Scheduler thread\n", CMIG)

# ---------------------------------------------------------------------------------------------------------------- the plugin
after("  {PKG}.DocMig.run();    // 0.4.14: the stale Mana regen comment ('never while charging'), once; History first\n",
      "  {PKG}.ClassManaMig.run();   // 0.4.15: the max Mana per class level lines into an existing xp.properties, once; History first\n")
rep('''"; sickle swings " + {PKG}.Sickle.text() + "; bridge''',
    '''"; sickle swings " + {PKG}.Sickle.text() + "; max Mana per class level " + {PKG}.ClassMana.text() + "; staff handover: the " + {PKG}.ManaCost.ARM_IDS.length + " ladder staffs come from SkyyArmory 0.1+" + "; bridge''')
rep('''          mxp, rsy, gpc, skl, sksy, sktk, dmig):   # 0.4.11: + HealMig; 0.4.12: + ClassCurve, ManaRegen, ManaRegenFn, ManaCmd; 0.4.13: + CombatFn; 0.4.14: + MobXp, RollSys, GatherPace, Sickle, SickleSys, SickleTask, DocMig''',
    '''          mxp, rsy, gpc, skl, sksy, sktk, dmig,
          cman, cmig):   # 0.4.11: + HealMig; 0.4.12: + ClassCurve, ManaRegen, ManaRegenFn, ManaCmd; 0.4.13: + CombatFn; 0.4.14: + MobXp, RollSys, GatherPace, Sickle, SickleSys, SickleTask, DocMig; 0.4.15: + ClassMana, ClassManaMig''')
rep('''Uninstall / downgrade: switch Base Mana and Overall Level off in Server Setup first.''',
    '''Priests gain +5 max Mana per Divinity level and Mages +10 per Sorcery level (Server Setup: Max Mana per class level); the 8 ladder staffs (Wood to Onyxium) come from SkyyArmory 0.1+ (its staff ladder - install both together). Uninstall / downgrade: switch Base Mana and Overall Level off in Server Setup first.''')

# ---------------------------------------------------------------------------------------------------------------- FIX ROUND (review 2026-10-03)
# (1) HEAL XP PAYS WHAT FITS (review: all or nothing with bigger chunks): SkyyClasses 0.1.11 heals up to 170 per party member and sends ONE
#     heal XP call per hit (all members together), so a call that crosses divinity.healXpMaxPerMinute was refused whole although most of it
#     fit (3 hurt members at 170 reached only 80% of the 900 a minute), and a call over the whole cap (6+ hurt members at 170 - party size
#     raised in Server Setup) was refused forever. HealXp.grant pays min(the call, the room left in this player's 60 s window); take (the
#     all-or-nothing rule) stays for any other caller. The cap itself is unchanged: at most 900 a minute.
before("# a refused offer gives its share back\n", r'''# 0.4.15 fix round: what still fits in this player's 60 s window is paid - min(want, room); 0 = nothing fits (the window is full). The call
# never fails just because it is bigger than the room (SkyyClasses 0.1.11's charged heals reach 170 per member, sent as one call per hit).
# cap <= 0 = no limit, nothing recorded. take() above keeps the all-or-nothing rule for any other caller.
hxp.addMethod(CtNewMethod.make("""
public static synchronized long grant(java.util.UUID u, long want, long cap, long now) {
  if (want <= 0L) return 0L;
  if (cap <= 0L) return want;
  long[] w = (long[]) HWIN.get(u);
  if (w == null || now - w[0] >= 60000L || now < w[0]) { w = new long[] { now, 0L }; HWIN.put(u, w); }
  long room = cap - w[1];
  if (room <= 0L) return 0L;
  long got = want < room ? want : room;
  w[1] = w[1] + got;
  return got;
}""", hxp))
''')
rep('''    long cap = {PKG}.DivCfg.MAX_MIN;
    if (!take(u, base, cap, System.currentTimeMillis())) {{ warnLimited(u, "divinity.healXpMaxPerMinute " + cap + " reached - refused " + base + " XP from " + source); return false; }}
    long r = -1L;
    try {{ r = {PKG}.BridgeXp.offerX(u, {PKG}.SkillDefs.DIVINITY, base, source, expect, null, 0, false, false); }} catch (Throwable t) {{ r = -1L; }}
    if (r < 0L) {{ if (cap > 0L) give(u, base); return false; }}
''', '''    long cap = {PKG}.DivCfg.MAX_MIN;
    long pay = grant(u, base, cap, System.currentTimeMillis());   // 0.4.15 fix round: what fits in the minute is paid (was all or nothing)
    if (pay <= 0L) {{ warnLimited(u, "divinity.healXpMaxPerMinute " + cap + " reached - refused " + base + " XP from " + source); return false; }}
    if (pay < base) warnLimited(u, "divinity.healXpMaxPerMinute " + cap + " reached - paid " + pay + " of " + base + " XP from " + source);
    long r = -1L;
    try {{ r = {PKG}.BridgeXp.offerX(u, {PKG}.SkillDefs.DIVINITY, pay, source, expect, null, 0, false, false); }} catch (Throwable t) {{ r = -1L; }}
    if (r < 0L) {{ if (cap > 0L) give(u, pay); return false; }}
''')
rep('''# a Priest (class skill Divinity = slot 15), class still following a profile switch, heal would cross the cap (all or nothing),''',
    '''# a Priest (class skill Divinity = slot 15), class still following a profile switch, the cap's window is full (0.4.15 fix round: a heal
# bigger than the room left pays the room - it was all or nothing),''')
# (2) STALE TEXT (review): "wand 5, staff 10, spellbook 20" read as every spell's cost - SkyyArmory's metal wands and ladder staffs have their
#     own (they are never divided). The read-only row help says so. The fresh-file comment line stays: those 4 comment lines are also the
#     0.4.8 ManaMig's DOC_NEW (the text it writes into old files) - and it stays true for this jar's own overrides.
rep('''     "Fixed in the jar at build time: vanilla spell Mana costs / this (wand 5, staff 10, spellbook 20).", "custom:SkillKit"),''',
    '''     "Fixed in the jar: vanilla Mana / this (wand 5, staff 10, spellbook 20). SkyyArmory sets its own.", "custom:SkillKit"),''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands: 0.4.15 adds none"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
_ix = lambda t: s.index(t)
# methods before callers (javassist compiles each method body when it is added)
assert _ix("public static void read(java.util.Properties p) {\n  Object[] t = parseTable(p);") < _ix("public static synchronized String load()")
assert _ix("public static Object[] mkTable(String[] c, double[] b)") < _ix("public static Object[] defTable() {\n  return @PKG@.OverallCfg.mkTable(DEF_CLS, DEF_PER);")
assert _ix("public static String classOf(java.util.UUID u)") < _ix("public static float amountFor(String cls, long[] d)") < _ix("public static float amount(java.util.UUID u, long[] d)")
assert _ix("public static float amount(java.util.UUID u, long[] d)") < _ix("public static void ovl(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref, {ESM} m)")
assert _ix("public static String statsLine(int s, int lv, boolean next)") < _ix("public static java.util.ArrayList lines(java.util.UUID u, int s, int lv, boolean next)")
assert _ix("public static String breakdown(java.util.UUID u, @ESM@ m, int mi, float max)") < _ix("mcmd.addMethod(CtNewMethod.make(")
assert _ix("public static int armory(String id)") < _ix("public static int costOf(String id)") < _ix("public static int spendOf(String id)")
assert _ix("public static String[] armCheck()") < _ix("public static void packTick()")
assert s.count("public static synchronized long grant(java.util.UUID u, long want, long cap, long now)") == 1 and \
    _ix("public static synchronized long grant(") < _ix("public static boolean offer(java.util.UUID u, double hp, String source, String expect, boolean self)")
assert s.count("long pay = grant(u, base, cap, System.currentTimeMillis());") == 1 and s.count("if (!take(u, base, cap,") == 0
assert _ix("public static int fileIdx()") < _ix("public static synchronized String run() {\n  java.nio.file.Path f = @PKG@.SkillCfg.FILE;\n  if (f == null) return \"\";\n  try {\n    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return \"\";\n    byte[] old = java.nio.file.Files.readAllBytes(f);\n    Object[] r = plan(")
assert _ix("public static Object[] plan(String text)") < _ix("public void setup() {{")
assert s.count("{PKG}.ClassManaMig.run();") == 1 and s.index("{PKG}.DocMig.run();") < s.index("{PKG}.ClassManaMig.run();") < s.index("String rules = {PKG}.SkillCfg.load();")
assert s.count("{PKG}.ClassMana.read(p);") == 1 and s.index("{PKG}.Sickle.read(p);") < s.index("{PKG}.ClassMana.read(p);")
assert s.count('mod(m, mi, "skyyskill_classmana", cmn);') == 1 and s.index('mod(m, mi, "skyyskill_basemana"') < s.index('mod(m, mi, "skyyskill_classmana"') < s.index('mod(m, hi, "skyyskill_overallhp"')
assert s.count("{PKG}.ClassMana.statsLine(s, lv, next)") == 1 and s.count("{PKG}.ClassMana.breakdown(u, m, mi, v.getMax())") == 1
assert s.count("ARMORY_ITEMS[_aid] = SPELL_ITEMS.pop(_aid)") == 1 and s.index("ARMORY_ITEMS[_aid] = SPELL_ITEMS.pop(_aid)") < s.index("SPELL_PLAN, SPELL_INHERITS, SPELL_UNCHANGED = spell_plan(SPELL_ITEMS, SPELL_DIVISOR)")
assert s.count("L.extend(CMAN_L)") == 1 and s.index("L.extend(N14_L)") < s.index("L.extend(CMAN_L)") < s.index('DEFAULTS = "\\n".join(L) + "\\n"')
assert s.count('assert _sk["Weapon_Staff_Wood"]') == 0 and s.count('assert _sg["Weapon_Staff_Wood"]') == 0
# the WHOLE diff against 0.4.14: every 0.4.14 line that changed belongs to one of the replaced anchors above
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed]
assert not _bad, "0.4.14 lines changed outside the planned places: %r" % _bad[:5]
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.14,", len(_gone), "0.4.14 lines replaced,",
      sum(op[4] - op[3] for op in _hunks) - len(_gone), "lines added net;", len(OLDS), "anchors")
