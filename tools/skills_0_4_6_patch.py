"""Derive SkyySkills/build_skyyskills_0.4.6.py from the EDITED SkyySkills/build_skyyskills_0.4.5.py (Skyy edited that generated script
directly in commit ab75b6c - NEVER re-run tools/skills_0_4_5_patch.py, it would drop those edits). Same style as skills_0_4_5_patch.py:
rep(old, new) with asserted single anchors, newline-agnostic; 0.4.5 stays untouched and its CRLF line endings are kept. Edit THIS file,
not the generated script.

0.4.6 = research/Overall-Level-Spec.md (base Mana 10 for everyone, Mage / Priest 20, the Overall Level with a small Health + Mana bonus
per level, /skills header + Overall page, bridge keys, the skills.overallUp switch) + Skyy's 2026-09-25 locks (OPEN-QUESTIONS.md):
 - Divinity: healing OTHERS stays divinity.healXpPerHp (0.2), healing YOURSELF pays divinity.healXpPerHpSelf (0.25), one cap (300/min).
   skill:fn:healxp takes an OPTIONAL trailing Boolean self (TRUE = the self rate; every old 2-4 element call = others).
 - Crossbows stay loaded: the kept loads SURVIVE a world change / teleport (same PlayerRef object + new entity Ref); relog (a new
   PlayerRef), death and a profile switch still drop them. The big-arrow (Signature) meter is kept with the bolts. A sound + a chat hint
   when the bolts go back in. /settings switches (default on): skills.xbowMeter / skills.xbowSound / skills.xbowHint; admin rows
   perk.archery.keepLoaded.meter / .sound / .hint.
 - FIX of the edited 0.4.5 (it does not build as-is): Skyy's new help text of the acro.doubleJump.trigger row is 138 characters and the
   config kit refuses help over 100 ("skyycfg: acro.doubleJump.trigger: help is longer than 100 characters (138)"). Shortened to 100
   characters with the same meaning. Nothing else of Skyy's edit is changed (Double Jump trigger jump, the Divinity / crossbow notes).
 - LOCKED 2026-09-25: config history keeps 10 old versions per file (KEEP 20 -> 10 for SkyySkills).
Run:  python tools/skills_0_4_6_patch.py   then   python SkyySkills/build_skyyskills_0.4.6.py   (NO --deploy: coordinated deploy)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.5.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.6.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.5"
s = raw.decode("utf8").replace("\r\n", "\n")
REG0 = s.count("registerSystem(")
# the EDITED 0.4.5 (commit ab75b6c) is the source: its locked defaults must be there, or this is the wrong file
for _a in ('DJ_L.append("acro.doubleJump.trigger=jump")', 'DIV_L.append("# LOCKED Skyy 2026-09-25: healing themself pays 0.25 XP per HP',
           'XBOW_L.append("# LOCKED Skyy 2026-09-25: loaded bolts survive teleports. This build still wipes them on a world change.")'):
    assert s.count(_a) == 1, "not the edited 0.4.5 (commit ab75b6c): missing %r" % _a


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    s = s.replace(old, new)


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


# ================================================================ header / version
rep('''"""SkyySkills 0.4.5 - build script (derived from 0.4.4 by tools/skills_0_4_5_patch.py - edit the patch, not this file;
0.4.4 was derived from 0.4.3 by tools/skills_0_4_4_patch.py, 0.4.3 from 0.4.2 by tools/skills_0_4_3_patch.py, 0.4.2 from 0.4.1 by
tools/skills_0_4_2_patch.py, 0.4.1 from 0.4 by tools/skills_0_4_1_patch.py, 0.4 from 0.3.2 by tools/skills_0_4_patch.py, 0.3.2 from 0.3.1
by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.5: Crossbows stay loaded''', '''"""SkyySkills 0.4.6 - build script (derived from the EDITED 0.4.5 by tools/skills_0_4_6_patch.py - edit the patch, not this file;
0.4.5 was derived from 0.4.4 by tools/skills_0_4_5_patch.py and then edited by Skyy in commit ab75b6c - never re-run that patch;
0.4.4 was derived from 0.4.3 by tools/skills_0_4_4_patch.py, 0.4.3 from 0.4.2 by tools/skills_0_4_3_patch.py, 0.4.2 from 0.4.1 by
tools/skills_0_4_2_patch.py, 0.4.1 from 0.4 by tools/skills_0_4_1_patch.py, 0.4 from 0.3.2 by tools/skills_0_4_patch.py, 0.3.2 from 0.3.1
by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.6: BASE MANA + OVERALL LEVEL (research/Overall-Level-Spec.md) + Skyy's 2026-09-25 locks (self-heal Divinity XP, crossbow extras).
  Everything 0.4.5 does is unchanged (Fury / Divinity, party XP, the crossbow perk, Double Jump trigger jump as Skyy edited it). Saved data:
  nothing new in players/<pkey>.properties; three blocks appended ONCE to an existing xp.properties (markers overall.enabled,
  divinity.healXpPerHpSelf, perk.archery.keepLoaded.meter). 0.4.5 <-> 0.4.6 is safe both ways for files. The three new MAX modifiers are
  saved with the player by the engine: before a downgrade switch "Base Mana" and "Overall Level Health and Mana" off in Server Setup and
  let players log in once (spec 2.5 / 4.14).
  BASE MANA (spec 2.1): every player's max Mana starts at mana.base (10); a profile whose class is in mana.magicClasses (Mage,Priest) starts
    at mana.magicBase (20) instead (the base IS 20, not 10 + 20). Posted as StaticModifier(MAX, ADDITIVE, base - EntityStatType(Mana).max)
    under its own key skyyskill_basemana (Perks.ovl inside the 1 s Perks.tick). Class = profile:class:<uuid> first, else class:<uuid>.
  OVERALL LEVEL (spec 2.2-2.4): floor(average level) of overall.skills (Mining, Foraging, Farming, Acrobatics, Alchemy, Smithing, Cooking,
    Exploration + Class = the ACTIVE profile's own class skill; other classes' skills and the legacy Combat slot never count; no class yet
    = 0 while SkyyClasses is installed, the row is skipped without SkyyClasses). Each Overall Level adds overall.healthPerLevel (0.5) max
    Health (key skyyskill_overallhp) and overall.manaPerLevel (0.2) max Mana (key skyyskill_overallmana) - PLACEHOLDER numbers, Server
    Setup rows. Keys never start with skyyacc_ (SkyyAccessories) or skyygear (SkyyGear); build-asserted. Amounts are computed from
    scratch every second (never from the current max), so nothing stacks. overall.healOnLevelUp heals the added Health on a real XP level
    up (players have no Health regen). Chat "OVERALL LEVEL UP 10 -> 11 +0.5 max Health +0.2 max Mana" (overall.chat admin master +
    player switch skills.overallUp, Skills tab).
  SHOWN (spec 2.8): /skills header "Overall Level N - average X.Y of M skills" + an Overall button (replaces the Skill average line);
    a new Overall page (button, /skills stats overall) in the VANILLA LOOK (Skyy 2026-09-28, tools/AGENT-BRIEF.md): the vanilla
    Common.ui container frame (Common/ContainerHeaderNoRunes.png + Common/ContainerPatch.png), title / subtitle / label colours and
    fonts, the vanilla Secondary text button (Common/Buttons/Secondary*.png, 17 pt bold uppercase #bdcbd3), the content separator
    #2b3542 and the vanilla progress colours #1a2030 / #aa7c4a - textures by their Common/ path in an inline page, the pattern Clay
    Factoria and Alec's Tamework ship (Mods folder, read only). Sizes stay BIG (1080-high rule). Button sounds / FontName left out (not
    proven in an inline page yet). Bridge: skill:overall:<uuid> = Integer, skill:fn:overall = Function(UUID | Object[]{UUID}) ->
    Object[]{Integer level, Integer averageTenths, Integer skillsCounted, Float maxHealthBonus, Float maxManaBonus, Float baseMana},
    skill:fn:level also answers "Overall". skill:<uuid> never gets an Overall entry (SkyyGuilds sums it).
  DIVINITY (LOCKED Skyy 2026-09-25): healing OTHERS pays divinity.healXpPerHp (0.2), healing YOURSELF divinity.healXpPerHpSelf (0.25),
    both inside the one divinity.healXpMaxPerMinute window (300). skill:fn:healxp = apply(Object[]{UUID healer, Number hp, String source
    [, String expectKey] [, Boolean self]}) - an OPTIONAL trailing Boolean (the last element, at index 3 or 4): TRUE = the self rate.
    Every old call (SkyyClasses 0.1.6: {u, hp, "classes:heal", pkey}) is a heal on others, exactly as before.
  CROSSBOWS STAY LOADED extras (LOCKED Skyy 2026-09-25, research/Crossbow-Loaded-Spec.md 2.8 / 2.9 / 6):
    - the kept loads SURVIVE teleports / world changes: XbowState remembers the PlayerRef object. VERIFIED (bytecode): a world change is
      PlayerRef.removeFromStore -> World.addPlayer -> addToStore (the same PlayerRef object and its Holder move in memory; PlayerRef.clone
      returns this); only Universe.addPlayer (a login) makes a new PlayerRef. Same PlayerRef + new Ref = world change: loads kept, the
      held-long-enough guard and an armed restore's delay restart in the new world. New PlayerRef = relog: wiped. Death (DeathComponent)
      and a profile switch (epoch) still wipe. INFERRED (bytecode, UNTESTED): a crossbow HELD while teleporting keeps its bolts in vanilla
      (nothing on the teleport path touches the EntityStatMap or the hotbar; EntityStatsSystems$Setup only creates a missing map).
    - the big-arrow meter: SignatureEnergy (the crossbow adds +5 max, +1 per combo hit) and SignatureCharges (the armed big arrow) are
      read at the switch away (with the bolts, same held-long-enough guard) and put back with them (never above the cap, never lowered);
      free (no item). An entry is kept when it has bolts OR meter. perk.archery.keepLoaded.meter (admin) + skills.xbowMeter (player).
    - when bolts go back in: the vanilla crossbow load sound (perk.archery.keepLoaded.sound, default SFX_Hand_Crossbow_T2_Load_Local,
      the reload step's own local sound) to that player only (SoundUtil.playSoundEvent2dToPlayer), and a chat hint "[Skills] Crossbow
      reloaded - 6 bolts back in (+ big-arrow meter)" (perk.archery.keepLoaded.hint). Player switches skills.xbowSound / skills.xbowHint
      (Combat tab, default on).
  CONFIG: 173 rows (0.4.5 had 159): + 2 part switches (Base Mana, Overall Level Health and Mana), 8 in the new "Overall and Mana"
    category, divinity.healXpPerHpSelf (Combat), perk.archery.keepLoaded.meter / .sound (check= XbowCfg.checkSound) / .hint (Perks).
    KEEP 10 old versions per file (LOCKED 2026-09-25, was 20).
  FIX: the edited 0.4.5 did not build as-is (acro.doubleJump.trigger help 138 > 100 characters); the help is now 100 characters.
  REVIEW FIXES (2026-09-28): (1) ONE banked big-arrow meter: the meter is still kept across a slot switch (Skyy's lock), but when onSlot
    banks a meter for the slot it leaves, every other slot's banked meter is zeroed (Xbow.keepOneMeter; their kept bolts stay), so two
    crossbows can no longer bank two full meters. (2) Session-start hold: for the first 10 s of a session (a new PlayerRef), while
    SkyyClasses is installed and no class is published yet (profile:class / class: - their ReadyTask may run after our first tick),
    Perks.ovl writes, publishes and heals nothing (Overall.hold), so the Base Mana / Overall modifiers the engine saved stay in place and a
    full-health player is not clamped by a dip to class skill 0; then it computes normally. (3) The Archery stats line says "(bolts and
    big-arrow meter)" only when the admin meter switch AND the player's skills.xbowMeter switch are on.
    Checked in a bare JVM (scratch tools/dev/scratch/fx-skills, deleted afterwards; 45 checks): 91 classes load + initialise under
    -Xverify:all; keepOneMeter (older meters zeroed, bolts kept, meter-only slots cleared, slot 15 reached); 3000 random switches keep at
    most one banked meter; Xbow.line x (no SkyyMenu / switch on / off / admin off); sessionAge (relog = new PlayerRef restarts, clock back);
    hold (no SkyyClasses, age 0 / 9999 / 10000, relog, class: / profile:class: published); Perks.ovl held = nothing published, heal kept,
    stat map untouched; after 10 s / with a class / without SkyyClasses it computes (8 / 12 / 10). UNVERIFIED (needs the game): whether
    the first tick really runs before SkyyClasses publishes on this server, and that the saved modifiers are back on the entity by then.
  CHECKED in a bare JVM (2026-09-28, scratch harness under tools/dev/scratch/ra-skills, deleted afterwards; 137 checks): all 91 classes
    load + initialise under -Xverify:all; a real 0.4.5 xp.properties (from the 0.4.5 jar) gets the three blocks appended exactly once,
    custom values kept, a second load appends nothing; a fresh file = DEFAULTS; clamps (base -5 -> 0, 20000 -> 10000, per level 200 ->
    100, NaN -> default, self rate 500 -> 100 / abc -> 0.25) and bad lists (skills -> default, magicClasses 'priest, mage, Druid' ->
    Priest, Mage); parseSkills / checkSkills / checkClasses / checkSound; sums on mock player files (spec 2.3 example 92 / 9 -> 10 /
    10.2, 116 / 9 -> 12 / 12.8, all 100, other class + legacy Combat ignored, no class -> n 9, no SkyyClasses -> n 8, profile:class beats
    class:, unknown class -> n 8); baseMana (no class 10, Mage / Priest / 'mage' 20, Warrior 10, typeMax 5 / 30, part off, empty list);
    Perks.ovl on a mock stat map (the 3 keys, MAX ADDITIVE, 20 / +5 / +2, the engine's own computeModifiers -> max Mana 22 / Health 105,
    no write in a steady second, parts off removes all three, Warrior base 10, the per-skill skyyskill_mana untouched, the pending heal
    +1.0 after the modifier, dropped at 0 Health / heal off, forget); levelUp (the exact line, HEAL, bridge, other class slot, no
    boundary, overall.chat off, skills.overallUp off); OverallFn / SkillFn "Overall"; skill:<uuid> without Overall; selfArg for every
    call shape; Xbow.rebind (first bind, same Ref, world change keeps loads + restarts the guard / delay, relog wipes); hasKept / clearSlot
    / drop; putStat (cap, never lowers); feedback texts + the admin / player switches; the Overall page texts; the player file round trip
    (no new keys); the kit's CfgRows (173 rows, KEEP 10, the new rows, Skyy's Double Jump default + help <= 100).
  UNVERIFIED (needs the game): the vanilla Mana bar showing at base 10 / 20 and regen; the Overall page's vanilla textures in an inline
    page; the load surviving /hub, /island and portals (and a held crossbow keeping its bolts through a teleport); the meter restore on
    real switches (SignatureEnergy / SignatureCharges timing after the Recalculate wipe); the 2D load sound; SkyyMenu showing the 4 new
    switches (Skills tab row 8, Combat tab rows 5-7).
0.4.5: Crossbows stay loaded''')
rep('''Run:   python build_skyyskills_0.4.5.py            -> SkyySkills/SkyySkills-0.4.5.jar
       python build_skyyskills_0.4.5.py --deploy   -> also copies''', '''Run:   python build_skyyskills_0.4.6.py            -> SkyySkills/SkyySkills-0.4.6.jar
       python build_skyyskills_0.4.6.py --deploy   -> also copies''')
rep('VERSION = "0.4.5"', 'VERSION = "0.4.6"')

# ================================================================ FIX: the edited 0.4.5 does not build (kit: help <= 100 characters)
_old_help = '"live", "LOCKED 2026-09-25: jump again while already in mid-air. Crouch remains a choice. Jump only works if the client reports it (spec test 5.0).", "reload"),'
_new_help = '"live", "LOCKED 2026-09-25: jump again in mid-air. Crouch stays a choice. Jump needs the client to report it.", "reload"),'
assert len("LOCKED 2026-09-25: jump again in mid-air. Crouch stays a choice. Jump needs the client to report it.") <= 100
rep(_old_help, _new_help)

# ================================================================ API probes (0.4.6)
before('''# ================= default xp.properties (generated here, every id checked against Assets.zip) =================
''', r'''# 0.4.6 (research/Overall-Level-Spec.md 4.12 + the crossbow extras; tools/dev reflect.py + bcfull.py against HytaleServer.jar 2026-09-28):
# the base Mana / Overall modifiers, the heal on an Overall level up, the Signature meter and the 2D sound to one player
for c, m in ((ESM, "addStatValue"), (ESM, "get"), (ESM, "putModifier"), (ESM, "removeModifier"), (ESM, "getModifier"), (ESM, "setStatValue"),
             (ESV, "getMax"), (ESV, "get"), (ESTT, "getMax"), (ESTT, "getAssetMap"), (DST, "getHealth"), (DST, "getMana"),
             (DST, "getSignatureEnergy"), (DTH, "getComponentType"), (SMO, "getAmount"), (MTG, "MAX"), (CAL, "ADDITIVE"), (ILT, "getIndex"),
             (ILT, "getAsset"), (ILT, "getNextIndex"), (SEV, "getAssetMap"), (SNU, "playSoundEvent2dToPlayer"), (SCAT, "SFX"),
             (PR, "sendMessage"), (PAGE, "rebuild")):
    B.probe(pool, c, m)
for c, m, d in ((ESM, "addStatValue", "(IF)F"), (ESTT, "getMax", "()F"), (DST, "getSignatureEnergy", "()I"), (DST, "getMana", "()I"),
                (DST, "getHealth", "()I"), (ILT, "getIndex", "(Ljava/lang/Object;)I"), (ILT, "getNextIndex", "()I"),
                (ESTT, "getAssetMap", "()L" + ILT.replace(".", "/") + ";"),
                (SNU, "playSoundEvent2dToPlayer", "(L" + PR.replace(".", "/") + ";IL" + SCAT.replace(".", "/") + ";)V")):
    try:
        pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
''')

# ================================================================ default xp.properties: Divinity self-heal block (DivCfg.ensureSelf)
# Skyy's DIV_L note said "This build still pays nothing ... the next Skills build reads that 0.25" - this IS that build: the note now
# names the new key (only fresh files and 0.4.3-era appends get the new DIV_L text; a file's existing comments stay as they are).
rep('''DIV_L.append("# LOCKED Skyy 2026-09-25: healing themself pays 0.25 XP per HP (was 0). Others stay 0.2. Cap stays 300 a minute.")
DIV_L.append("# This build still pays nothing for a self-heal. The next Skills build reads that 0.25.")''',
    '''DIV_L.append("# LOCKED Skyy 2026-09-25: healing themself pays 0.25 XP per HP (was 0). Others stay 0.2. Cap stays 300 a minute.")
DIV_L.append("# SkyySkills 0.4.6+ reads the self-heal rate from divinity.healXpPerHpSelf (its own block below).")''')
after('''DIV_LIT = json.dumps(DIV_DEFAULTS)
''', r'''# 0.4.6 (LOCKED Skyy 2026-09-25): Divinity XP for healing YOURSELF. Its own block (NOT part of DIV_L): DivCfg.ensureDefaults appends DIV_L
# to a file without divinity.healXp.enabled, DivCfg.ensureSelf appends this block to any file without divinity.healXpPerHpSelf - both in
# the same load, never twice (the AcroCfg.ensureDj pattern).
DIVS_L = []
DIVS_L.append("# ---------- Divinity self-heal XP (SkyySkills 0.4.6) - LOCKED Skyy 2026-09-25 ----------")
DIVS_L.append("# Comments must stay on their own lines.")
DIVS_L.append("# healXpPerHpSelf: Divinity XP for every 1 HP a Priest heals on THEMSELF (divinity.healXpPerHp is for other party members).")
DIVS_L.append("# Both count against divinity.healXpMaxPerMinute.")
DIVS_L.append("divinity.healXpPerHpSelf=0.25")
L.append("")
L.extend(DIVS_L)
DIVS_DEFAULTS = "\n".join(DIVS_L) + "\n"
assert all(ord(ch) < 128 for ch in DIVS_DEFAULTS) and '"' not in DIVS_DEFAULTS
DIVS_LIT = json.dumps(DIVS_DEFAULTS)
''')

# ================================================================ default xp.properties: crossbow extras + Overall Level / base Mana
rep('''XBOW_L.append("# LOCKED Skyy 2026-09-25: loaded bolts survive teleports. This build still wipes them on a world change.")
XBOW_L.append("# LOCKED Skyy 2026-09-25: keep the big-arrow meter, and play a sound plus a chat hint when bolts return.")
XBOW_L.append("# Players can turn the meter, the sound, and the hint off in /settings. This build does none of that yet.")''',
    '''XBOW_L.append("# LOCKED Skyy 2026-09-25: loaded bolts survive teleports (SkyySkills 0.4.6+; relog, death and a profile switch drop them).")
XBOW_L.append("# LOCKED Skyy 2026-09-25: keep the big-arrow meter, and play a sound plus a chat hint when bolts return (0.4.6+, block below).")
XBOW_L.append("# Players can turn the meter, the sound, and the hint off in /settings.")''')
after('''XBOW_LIT = json.dumps(XBOW_DEFAULTS)
''', r'''# 0.4.6 (LOCKED Skyy 2026-09-25): the crossbow extras. Own block, appended once to a file without perk.archery.keepLoaded.meter
# (XbowCfg.ensureExtras); XBOW_L above is unchanged in keys, so XbowCfg.ensureDefaults and this never write a key twice.
XBOW_SOUND_DEF = "SFX_Hand_Crossbow_T2_Load_Local"
XBOWX_L = []
XBOWX_L.append("# ---------- Crossbows stay loaded extras (SkyySkills 0.4.6) - LOCKED Skyy 2026-09-25 ----------")
XBOWX_L.append("# Comments must stay on their own lines.")
XBOWX_L.append("# meter=true: the big-arrow (Signature) meter comes back with the bolts (players can turn it off in /settings).")
XBOWX_L.append("perk.archery.keepLoaded.meter=true")
XBOWX_L.append("# sound: the sound event played to that player when the bolts go back in (vanilla crossbow load); empty = no sound")
XBOWX_L.append("perk.archery.keepLoaded.sound=" + XBOW_SOUND_DEF)
XBOWX_L.append("# hint=true: a chat line when the bolts go back in (players can turn it off in /settings)")
XBOWX_L.append("perk.archery.keepLoaded.hint=true")
L.append("")
L.extend(XBOWX_L)
XBOWX_DEFAULTS = "\n".join(XBOWX_L) + "\n"
assert all(ord(ch) < 128 for ch in XBOWX_DEFAULTS) and '"' not in XBOWX_DEFAULTS
XBOWX_LIT = json.dumps(XBOWX_DEFAULTS)
# 0.4.6 (research/Overall-Level-Spec.md 4.2): the Overall Level + base Mana block; appended once to a file without overall.enabled
OVL_SKILLS_DEF = "Mining,Foraging,Farming,Acrobatics,Alchemy,Smithing,Cooking,Exploration,Class"
OVL_L = []
OVL_L.append("# ---------- Overall Level + base Mana (SkyySkills 0.4.6) - research/Overall-Level-Spec.md ----------")
OVL_L.append("# Comments must stay on their own lines.")
OVL_L.append("# Base Mana: every player's max Mana starts at mana.base; players whose class is listed in mana.magicClasses start at mana.magicBase")
OVL_L.append("# instead (their base is that number, not mana.base plus it). Vanilla max Mana is 0; Mana refills by itself (+1 every 0.2 s after")
OVL_L.append("# 6 s without taking damage).")
OVL_L.append("mana.base.enabled=true")
OVL_L.append("mana.base=10")
OVL_L.append("mana.magicBase=20")
OVL_L.append("mana.magicClasses=Mage,Priest")
OVL_L.append("# Overall Level = the average level of the listed skills, rounded down. Class = the profile's own class skill (other classes' skills")
OVL_L.append("# never count). Each Overall Level adds healthPerLevel max Health and manaPerLevel max Mana (PLACEHOLDER numbers).")
OVL_L.append("overall.enabled=true")
OVL_L.append("overall.skills=" + OVL_SKILLS_DEF)
OVL_L.append("overall.healthPerLevel=0.5")
OVL_L.append("overall.manaPerLevel=0.2")
OVL_L.append("# healOnLevelUp=true: an Overall level up also heals the max Health it added (players have no Health regen)")
OVL_L.append("overall.healOnLevelUp=true")
OVL_L.append("# chat=false: nobody gets the OVERALL LEVEL UP line (players can also hide it for themselves in /settings)")
OVL_L.append("overall.chat=true")
L.append("")
L.extend(OVL_L)
OVL_DEFAULTS = "\n".join(OVL_L) + "\n"
assert all(ord(ch) < 128 for ch in OVL_DEFAULTS) and '"' not in OVL_DEFAULTS
OVL_LIT = json.dumps(OVL_DEFAULTS)
''')

# ================================================================ build checks (Assets.zip): Mana, the Signature meter, the load sound
before('''ALCH_PUTS = "\\n".join(''', r'''# 0.4.6 build checks (Overall-Level-Spec 4.12 + the crossbow extras), read in memory from Assets.zip
with zipfile.ZipFile(ASSETS) as _oz:
    _on = _oz.namelist()
    def _ostat(base):
        _h = [n for n in _on if n.startswith("Server/Entity/Stats/") and n.endswith("/" + base)]
        assert len(_h) == 1, "Assets.zip: %d x Server/Entity/Stats/**/%s" % (len(_h), base)
        return json.loads(_oz.read(_h[0]).decode("utf-8-sig"))
    _mana = _ostat("Mana.json")
    _sige = _ostat("SignatureEnergy.json")
    _sigc = _ostat("SignatureCharges.json")
    _snd = [n for n in _on if n.startswith("Server/Audio/SoundEvents/") and n.endswith("/" + XBOW_SOUND_DEF + ".json")]
    _xt6 = json.loads(_oz.read([n for n in _on if n.startswith("Server/Item/Items/") and n.endswith("/Template_Weapon_Crossbow.json")][0]).decode("utf-8-sig"))
_mreg = _mana.get("Regenerating") or []
print("vanilla Mana: Max %r, ResetType %r, Regenerating %s" % (_mana.get("Max"), _mana.get("ResetType"),
      "; ".join("every %s s +%s %s if %s" % (r.get("Interval"), r.get("Amount"), r.get("RegenType"),
                ",".join(("!" if c.get("Inverse") else "") + str(c.get("Id")) + ("(%ss)" % c.get("Delay") if c.get("Delay") else "") for c in (r.get("Conditions") or [])))
                for r in _mreg) or "none"))
if _mana.get("Max") not in (0, 0.0):
    print("NOTE FOR SKYY: vanilla max Mana is %r now (was 0) - base Mana still means a TOTAL base of 10 / 20 (spec 2.1, Q11)" % (_mana.get("Max"),))
assert len(_snd) == 1, "sound event %s not found (exactly once) under Server/Audio/SoundEvents in Assets.zip" % XBOW_SOUND_DEF
_xw6 = _xt6.get("Weapon") or {}
for _st in ("SignatureEnergy", "SignatureCharges"):
    assert _st in (_xw6.get("EntityStatsToClear") or []), "Template_Weapon_Crossbow no longer clears %s on a switch (the meter keep assumes it)" % _st
    assert _st in (_xw6.get("StatModifiers") or {}), "Template_Weapon_Crossbow no longer gives %s its cap (the meter restore waits for it)" % _st
print("crossbow meter: SignatureEnergy base max %r (+%r from the crossbow), SignatureCharges base max %r (+%r); load sound %s" % (
    _sige.get("Max"), (_xw6["StatModifiers"]["SignatureEnergy"][0] or {}).get("Amount"), _sigc.get("Max"),
    (_xw6["StatModifiers"]["SignatureCharges"][0] or {}).get("Amount"), XBOW_SOUND_DEF))
# the modifier keys (spec 4.12): our own prefix, distinct, never SkyyAccessories' skyyacc_* or the coming SkyyGear's skyygear*
OVL_KEYS = ["skyyskill_basemana", "skyyskill_overallhp", "skyyskill_overallmana"]
assert len(set(OVL_KEYS)) == 3 and all(k.startswith("skyyskill_") for k in OVL_KEYS)
assert not set(OVL_KEYS) & {"skyyskill_health", "skyyskill_stamina", "skyyskill_mana"}
assert not any(k.startswith("skyyacc_") or k.startswith("skyygear") for k in OVL_KEYS)
''')

# ================================================================ classes
after('''xss  = pool.makeClass(PKG + ".XbowSlotSys", pool.get(EES))
''', '''# 0.4.6: base Mana + Overall Level (research/Overall-Level-Spec.md 4.3-4.8): config, logic, bridge Function, the Overall page
ovc  = pool.makeClass(PKG + ".OverallCfg")
ovl  = pool.makeClass(PKG + ".Overall")
ofn  = pool.makeClass(PKG + ".OverallFn")
opg  = pool.makeClass(PKG + ".OverallPage", pool.get(PAGE))
''')

# ================================================================ DivCfg: the self-heal rate
rep('''for decl in ("boolean ON = true", "double PER_HP = 0.2", "long MAX_MIN = 300L"):
    dvc.addField(CtField.make("public static volatile " + decl + ";", dvc))''',
    '''for decl in ("boolean ON = true", "double PER_HP = 0.2", "long MAX_MIN = 300L", "double PER_HP_SELF = 0.25"):
    dvc.addField(CtField.make("public static volatile " + decl + ";", dvc))
dvc.addField(CtField.make("public static final String SELF_DEFAULTS = " + DIVS_LIT + ";", dvc))   # 0.4.6''')
rep('''  PER_HP = (Double.isNaN(r) || r < 0.0) ? 0.0 : (r > 100.0 ? 100.0 : r);
''', '''  PER_HP = (Double.isNaN(r) || r < 0.0) ? 0.0 : (r > 100.0 ? 100.0 : r);
  double rs = {PKG}.SkillCfg.dbl(p, "divinity.healXpPerHpSelf", 0.25);
  PER_HP_SELF = (Double.isNaN(rs) || rs < 0.0) ? 0.0 : (rs > 100.0 ? 100.0 : rs);
''')
rep('''dvc.addMethod(CtNewMethod.make("""
public static boolean on() {
  return ON && PER_HP > 0.0;
}""", dvc))''', r'''# 0.4.6: ensureSelf appends the self-heal block once to a file without divinity.healXpPerHpSelf (the ensureDefaults pattern)
dvc.addMethod(CtNewMethod.make(f"""
public static void ensureSelf(java.util.Properties p) {{
  if (p.getProperty("divinity.healXpPerHpSelf") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + SELF_DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Divinity self-heal section (divinity.healXpPerHpSelf=0.25)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Divinity self-heal section to xp.properties: " + t); }}
}}""", dvc))
# 0.4.6: on = heal XP can pay at all (the part switch and at least one rate above 0); onFor / rate = the rate of this heal
dvc.addMethod(CtNewMethod.make("""
public static boolean on() {
  return ON && (PER_HP > 0.0 || PER_HP_SELF > 0.0);
}""", dvc))
dvc.addMethod(CtNewMethod.make("""
public static double rate(boolean self) {
  return self ? PER_HP_SELF : PER_HP;
}""", dvc))
dvc.addMethod(CtNewMethod.make("""
public static boolean onFor(boolean self) {
  return ON && rate(self) > 0.0;
}""", dvc))''')
rep('''  return "on (" + num(PER_HP) + " XP per HP healed on others" + (MAX_MIN > 0L ? ", up to " + MAX_MIN + " a minute" : "") + ")";''',
    '''  return "on (" + num(PER_HP) + " XP per HP healed on others, " + num(PER_HP_SELF) + " on yourself" + (MAX_MIN > 0L ? ", up to " + MAX_MIN + " a minute" : "") + ")";''')
rep('''  return "Healing party members pays " + num(PER_HP) + " Divinity XP per HP" + (MAX_MIN > 0L ? " (up to " + MAX_MIN + " a minute)" : "");''',
    '''  return "Healing pays " + num(PER_HP) + " Divinity XP per HP on others, " + num(PER_HP_SELF) + " on yourself" + (MAX_MIN > 0L ? " (max " + MAX_MIN + " a minute)" : "");''')

# ================================================================ XbowCfg: meter / sound / hint + XbowState: PlayerRef, meter per slot
rep('''for decl in ("boolean ON = true", "int LEVEL = 5", 'String[] ITEMS = new String[] { "Weapon_Crossbow_" }', "int DELAY = 3", "boolean DEBUG = false"):
    xcf.addField(CtField.make("public static volatile " + decl + ";", xcf))''',
    '''for decl in ("boolean ON = true", "int LEVEL = 5", 'String[] ITEMS = new String[] { "Weapon_Crossbow_" }', "int DELAY = 3", "boolean DEBUG = false",
             "boolean METER = true", 'String SOUND = "%s"' % XBOW_SOUND_DEF, "boolean HINT = true"):
    xcf.addField(CtField.make("public static volatile " + decl + ";", xcf))
xcf.addField(CtField.make("public static final String EXTRA_DEFAULTS = " + XBOWX_LIT + ";", xcf))   # 0.4.6
xcf.addField(CtField.make('public static final String SOUND_DEFAULT = "%s";' % XBOW_SOUND_DEF, xcf))
# 0.4.6: problem text for a sound event id, or null (fine / empty = no sound / the engine's sound map unreadable or empty = not checked,
# e.g. a bare JVM). The kit's check= hook and the loader's warning share it.
xcf.addMethod(CtNewMethod.make(f"""
public static String soundProblem(String v) {{
  if (v == null) return null;
  String t = v.trim();
  if (t.length() == 0) return null;
  if (t.length() > 120) return "A sound event id is at most 120 characters.";
  for (int k = 0; k < t.length(); k++) {{
    char c = t.charAt(k);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-' || c == '.'))
      return "Write one sound event id like " + SOUND_DEFAULT + " (letters, digits and _ only), or leave it empty for no sound.";
  }}
  try {{
    {ILT} m = {SEV}.getAssetMap();
    if (m == null || m.getNextIndex() <= 0) return null;
    if (m.getIndex(t) < 0) return "No sound event is called " + t + ". The vanilla crossbow load is " + SOUND_DEFAULT + ".";
  }} catch (Throwable x) {{ return null; }}
  return null;
}}""", xcf))''')
rep('''  DEBUG = {PKG}.SkillCfg.bool(p, "perk.archery.keepLoaded.debug", false);
}}""", xcf))''', '''  DEBUG = {PKG}.SkillCfg.bool(p, "perk.archery.keepLoaded.debug", false);
  METER = {PKG}.SkillCfg.bool(p, "perk.archery.keepLoaded.meter", true);
  String so = p.getProperty("perk.archery.keepLoaded.sound");
  SOUND = so == null ? SOUND_DEFAULT : so.trim();
  String sp = soundProblem(SOUND);
  if (sp != null) {PKG}.SkillCfg.warn("perk.archery.keepLoaded.sound=" + SOUND + ": " + sp + " (no sound until it is fixed)");
  HINT = {PKG}.SkillCfg.bool(p, "perk.archery.keepLoaded.hint", true);
}}""", xcf))
# 0.4.6: the extras block, appended once to a file without perk.archery.keepLoaded.meter (the ensureDefaults pattern)
xcf.addMethod(CtNewMethod.make(f"""
public static void ensureExtras(java.util.Properties p) {{
  if (p.getProperty("perk.archery.keepLoaded.meter") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\\\n" + EXTRA_DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Crossbows stay loaded extras section (perk.archery.keepLoaded.meter / sound / hint)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Crossbows stay loaded extras section to xp.properties: " + t); }}
}}""", xcf))
# 0.4.6: check= hook of the perk.archery.keepLoaded.sound row (CONFIG-CONTRACT check=: null = fine, text = refuse)
xcf.addMethod(CtNewMethod.make("""
public static String checkSound(String key, String v) {
  return soundProblem(v);
}""", xcf))''')
rep('''  return "on (Archers from Archery " + LEVEL + ", bolts back after " + DELAY + " ticks" + (DEBUG ? ", DEBUG chat lines on" : "") + ")";''',
    '''  return "on (Archers from Archery " + LEVEL + ", bolts back after " + DELAY + " ticks, loads survive teleports" + (METER ? ", big-arrow meter kept" : "") + (SOUND.length() > 0 ? ", sound " + SOUND : ", no sound") + (HINT ? ", chat hint" : "") + (DEBUG ? ", DEBUG chat lines on" : "") + ")";''')
rep('''xst.addField(CtField.make("public " + REF + " ref;", xst))
''', '''xst.addField(CtField.make("public " + REF + " ref;", xst))
xst.addField(CtField.make("public " + PR + " pr;", xst))        # 0.4.6: the connection this state belongs to (world change vs relog)
xst.addField(CtField.make("public float[] sig;", xst))         # 0.4.6: kept SignatureEnergy per hotbar slot (the big-arrow meter)
xst.addField(CtField.make("public float[] chg;", xst))         # 0.4.6: kept SignatureCharges per hotbar slot (an armed big arrow)
''')
rep('''  this.ref = null;
  this.epoch = -1L;''', '''  this.ref = null;
  this.pr = null;
  this.sig = new float[16];
  this.chg = new float[16];
  this.epoch = -1L;''')

# ================================================================ OverallCfg (spec 4.3) - before BridgeCfg; SkillCfg.load (its caller) comes later
before('''# ================= BridgeCfg (0.4): bridge.* keys (skill:fn:addxp / skill:fn:craftxp) =================
''', r'''# ================= OverallCfg (0.4.6): the Overall Level + base Mana block of xp.properties (research/Overall-Level-Spec.md 4.3) =================
# Read by SkillCfg.load (/skills reload and the kit's reload routine); appended ONCE to an existing file without overall.enabled (the
# DivCfg / XbowCfg pattern; the code defaults are the same numbers). Clamps = the Server Setup row bounds.
ovc.addField(CtField.make("public static final String DEFAULTS = " + OVL_LIT + ";", ovc))
ovc.addField(CtField.make('public static final String SKILLS_DEFAULT = "%s";' % OVL_SKILLS_DEF, ovc))
for _decl in ("boolean MANA_ON = true", "double BASE = 10.0", "double MAGIC_BASE = 20.0", 'String[] MAGIC = new String[] { "Mage", "Priest" }',
              'String MAGIC_TEXT = "Mage,Priest"', "boolean ON = true", "int[] SLOTS = new int[] { 0, 1, 2, 4, 10, 11, 12, 13 }",
              "boolean CLASS = true", "double HP = 0.5", "double MANA = 0.2", "boolean HEAL = true", "boolean CHAT = true"):
    ovc.addField(CtField.make("public static volatile " + _decl + ";", ovc))
ovc.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  if (p.getProperty("overall.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Overall Level + base Mana section (mana.* / overall.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Overall Level + base Mana section to xp.properties: " + t); }}
}}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static double clampD(double v, double d, double lo, double hi) {
  if (Double.isNaN(v) || Double.isInfinite(v)) return d;
  return v < lo ? lo : (v > hi ? hi : v);
}""", ovc))
# the slots overall.skills may name (spec 2.2): Mining, Foraging, Farming, Acrobatics, Alchemy, Smithing, Cooking, Exploration
ovc.addMethod(CtNewMethod.make(f"""
public static boolean allowedSlot(int s) {{
  return s == {PKG}.SkillDefs.MINING || s == {PKG}.SkillDefs.FORAGING || s == {PKG}.SkillDefs.FARMING || s == {PKG}.SkillDefs.ACROBATICS
      || s == {PKG}.SkillDefs.ALCHEMY || s == {PKG}.SkillDefs.SMITHING || s == {PKG}.SkillDefs.COOKING || s == {PKG}.SkillDefs.EXPLORATION;
}}""", ovc))
# exact LABELS / NAMES match (no prefix), -1 = none
ovc.addMethod(CtNewMethod.make(f"""
public static int exactSlot(String t) {{
  for (int k = 0; k < {PKG}.SkillDefs.N; k++) if ({PKG}.SkillDefs.LABELS[k].equalsIgnoreCase(t) || {PKG}.SkillDefs.NAMES[k].equalsIgnoreCase(t)) return k;
  return -1;
}}""", ovc))
# "Mining, Class" -> Object[]{ int[] slots, Boolean class }; a name outside the allowed slots, a duplicate or an empty list -> null
ovc.addMethod(CtNewMethod.make("""
public static Object[] parseSkills(String v) {
  if (v == null) return null;
  String[] ps = v.split(",");
  int[] tmp = new int[16];
  int n = 0;
  int seen = 0;
  boolean cls = false;
  for (int i = 0; i < ps.length; i++) {
    String t = ps[i].trim();
    if (t.length() == 0) continue;
    seen++;
    if (t.equalsIgnoreCase("class")) {
      if (cls) return null;
      cls = true;
      continue;
    }
    int s = exactSlot(t);
    if (!allowedSlot(s)) return null;
    for (int j = 0; j < n; j++) if (tmp[j] == s) return null;
    if (n >= tmp.length) return null;
    tmp[n] = s;
    n++;
  }
  if (seen == 0) return null;
  int[] out = new int[n];
  System.arraycopy(tmp, 0, out, 0, n);
  return new Object[] { out, Boolean.valueOf(cls) };
}""", ovc))
# class names matched (any case) against SkillDefs.CLASSES, stored with that spelling, duplicates and unknown names dropped
ovc.addMethod(CtNewMethod.make(f"""
public static String[] parseClasses(String v) {{
  java.util.ArrayList l = new java.util.ArrayList();
  if (v != null) {{
    String[] ps = v.split(",");
    for (int i = 0; i < ps.length; i++) {{
      String t = ps[i].trim();
      if (t.length() == 0) continue;
      for (int k = 0; k < {PKG}.SkillDefs.CLASSES.length; k++) {{
        String c = {PKG}.SkillDefs.CLASSES[k];
        if (c.equalsIgnoreCase(t) && !l.contains(c)) l.add(c);
      }}
    }}
  }}
  String[] out = new String[l.size()];
  for (int i = 0; i < out.length; i++) out[i] = (String) l.get(i);
  return out;
}}""", ovc))
# the first name that is not a class, or null
ovc.addMethod(CtNewMethod.make(f"""
public static String badClass(String v) {{
  if (v == null) return null;
  String[] ps = v.split(",");
  for (int i = 0; i < ps.length; i++) {{
    String t = ps[i].trim();
    if (t.length() == 0) continue;
    boolean ok = false;
    for (int k = 0; k < {PKG}.SkillDefs.CLASSES.length; k++) if ({PKG}.SkillDefs.CLASSES[k].equalsIgnoreCase(t)) ok = true;
    if (!ok) return t;
  }}
  return null;
}}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static String join(String[] a, String sep) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < a.length; i++) {
    if (i > 0) sb.append(sep);
    sb.append(a[i]);
  }
  return sb.toString();
}""", ovc))
# check= hooks (CONFIG-CONTRACT: null = fine, text = refuse)
ovc.addMethod(CtNewMethod.make(f"""
public static String checkSkills(String key, String value) {{
  if (parseSkills(value) != null) return null;
  if (value != null) {{
    String[] ps = value.split(",");
    for (int i = 0; i < ps.length; i++) {{
      int s = exactSlot(ps[i].trim());
      if (s >= 0 && {PKG}.SkillDefs.isClass(s)) return "Use Class - it means the profile's own class skill; other classes never count.";
    }}
  }}
  return "Use a comma list of Mining, Foraging, Farming, Acrobatics, Alchemy, Smithing, Cooking, Exploration and Class (the profile's own class skill), each once.";
}}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static String checkClasses(String key, String value) {
  String b = badClass(value);
  if (b == null) return null;
  if (b.length() > 40) b = b.substring(0, 40) + "...";
  return "Unknown class " + b + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Shaman.";
}""", ovc))
ovc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  MANA_ON = {PKG}.SkillCfg.bool(p, "mana.base.enabled", true);
  BASE = clampD({PKG}.SkillCfg.dbl(p, "mana.base", 10.0), 10.0, 0.0, 10000.0);
  MAGIC_BASE = clampD({PKG}.SkillCfg.dbl(p, "mana.magicBase", 20.0), 20.0, 0.0, 10000.0);
  String mc = p.getProperty("mana.magicClasses");
  if (mc == null) mc = "Mage,Priest";
  String bad = badClass(mc);
  if (bad != null) {PKG}.SkillCfg.warn("mana.magicClasses: " + bad + " is not a class - left out (classes: Archer, Warrior, Mage, Berserker, Priest, Assassin, Shaman)");
  String[] m = parseClasses(mc);
  MAGIC = m;
  MAGIC_TEXT = join(m, ",");
  ON = {PKG}.SkillCfg.bool(p, "overall.enabled", true);
  String sk = p.getProperty("overall.skills");
  Object[] ps = parseSkills(sk == null ? SKILLS_DEFAULT : sk);
  if (ps == null) {{
    {PKG}.SkillCfg.warn("overall.skills=" + sk + " is not a comma list of Mining, Foraging, Farming, Acrobatics, Alchemy, Smithing, Cooking, Exploration and Class (each once) - using " + SKILLS_DEFAULT);
    ps = parseSkills(SKILLS_DEFAULT);
  }}
  SLOTS = (int[]) ps[0];
  CLASS = ((Boolean) ps[1]).booleanValue();
  HP = clampD({PKG}.SkillCfg.dbl(p, "overall.healthPerLevel", 0.5), 0.5, 0.0, 100.0);
  MANA = clampD({PKG}.SkillCfg.dbl(p, "overall.manaPerLevel", 0.2), 0.2, 0.0, 100.0);
  HEAL = {PKG}.SkillCfg.bool(p, "overall.healOnLevelUp", true);
  CHAT = {PKG}.SkillCfg.bool(p, "overall.chat", true);
}}""", ovc))
ovc.addMethod(CtNewMethod.make(f"""
public static String text() {{
  int n = SLOTS.length + (CLASS ? 1 : 0);
  String o = ON ? "on (" + n + " skills, +" + {PKG}.DivCfg.num(HP) + " health / +" + {PKG}.DivCfg.num(MANA) + " mana per level)" : "off (" + n + " skills, shown only)";
  String b = MANA_ON ? "base mana " + {PKG}.DivCfg.num(BASE) + " / " + {PKG}.DivCfg.num(MAGIC_BASE) + " for " + (MAGIC.length > 0 ? MAGIC_TEXT : "nobody") : "base mana off";
  return o + ", " + b;
}}""", ovc))

''')

# ================================================================ SkillCfg.load: ensure + read + summary
rep('''    {PKG}.XbowCfg.ensureDefaults(p);
''', '''    {PKG}.XbowCfg.ensureDefaults(p);
    {PKG}.DivCfg.ensureSelf(p);
    {PKG}.XbowCfg.ensureExtras(p);
    {PKG}.OverallCfg.ensureDefaults(p);
''')
rep('''    {PKG}.XbowCfg.read(p);
''', '''    {PKG}.XbowCfg.read(p);
    {PKG}.OverallCfg.read(p);
''')
rep('''+ ", crossbows stay loaded " + {PKG}.XbowCfg.text() + ", bridge skills "''',
    '''+ ", crossbows stay loaded " + {PKG}.XbowCfg.text() + ", overall level " + {PKG}.OverallCfg.text() + ", bridge skills "''')

# ================================================================ Overall (spec 4.4) + OverallFn (4.8) - after SkillStore / SkillClass, before SkillFn
before('''# ================= SkillFn: bridge skill:fn:level =================
''', r'''# ================= Overall (0.4.6): base Mana + the Overall Level (research/Overall-Level-Spec.md 2 / 4.4) =================
# Pure parts are safe on any thread; levelUp runs on the world thread (SkillXp.gain4). HEAL: UUID -> Integer Overall levels whose Health
# is still to be healed (Perks.ovl takes it at the next 1 s tick); BADCLS: class names warned once per JVM. No lock but its own short
# synchronized addHeal / takeHeal (one map operation each, nothing called inside).
ovl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap HEAL = new java.util.concurrent.ConcurrentHashMap();", ovl))
ovl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BADCLS = new java.util.concurrent.ConcurrentHashMap();", ovl))
# review fix (LOW, 2026-09-28): the session-start hold (see hold below). SESS = UUID -> Object[]{PlayerRef, Long ms of the first Perks.ovl of
# this session}; HOLD_MS = how long a missing class is waited for.
ovl.addField(CtField.make("public static final long HOLD_MS = 10000L;", ovl))
ovl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SESS = new java.util.concurrent.ConcurrentHashMap();", ovl))
ovl.addMethod(CtNewMethod.make("""
public static float round2(double v) {
  return (float) (Math.round(v * 100.0) / 100.0);
}""", ovl))
# a copy of StatsPage.num (StatsPage is compiled later): 0.5 -> "0.5", 10.0 -> "10", at most 3 decimals, no Locale
ovl.addMethod(CtNewMethod.make("""
public static String num(double v) {
  long t = Math.round(v * 1000.0);
  String sign = t < 0L ? "-" : "";
  if (t < 0L) t = -t;
  long w = t / 1000L;
  long f = t % 1000L;
  if (f == 0L) return sign + w;
  String fs = String.valueOf(f + 1000L).substring(1);
  while (fs.endsWith("0")) fs = fs.substring(0, fs.length() - 1);
  return sign + w + "." + fs;
}""", ovl))
# the ACTIVE profile's class: profile:class:<uuid> (SkyyProfiles, authoritative, flips with the epoch) first, else class:<uuid>
ovl.addMethod(CtNewMethod.make(f"""
public static String classOf(java.util.UUID u) {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("profile:class:" + u.toString());
    if (o instanceof String && ((String) o).trim().length() > 0) return ((String) o).trim();
  }} catch (Throwable t) {{ }}
  return {PKG}.SkillClass.className(u);
}}""", ovl))
ovl.addMethod(CtNewMethod.make(f"""
public static boolean magic(java.util.UUID u) {{
  String c = classOf(u);
  if (c == null) return false;
  String[] m = {PKG}.OverallCfg.MAGIC;
  for (int i = 0; i < m.length; i++) if (m[i].equalsIgnoreCase(c)) return true;
  return false;
}}""", ovl))
ovl.addMethod(CtNewMethod.make(f"""
public static float typeMax(int idx) {{
  try {{
    {ESTT} t = ({ESTT}) {ESTT}.getAssetMap().getAsset(idx);
    if (t != null) return t.getMax();
  }} catch (Throwable e) {{ }}
  return 0.0f;
}}""", ovl))
# the TOTAL base this player has (10, 20 for a magic user, 0 when the part is off)
ovl.addMethod(CtNewMethod.make(f"""
public static float baseTarget(java.util.UUID u) {{
  if (!{PKG}.OverallCfg.MANA_ON) return 0.0f;
  return round2(magic(u) ? {PKG}.OverallCfg.MAGIC_BASE : {PKG}.OverallCfg.BASE);
}}""", ovl))
# the modifier amount: the base minus the stat type's own max (vanilla 0), never below 0 (spec 2.1, Q11: a TOTAL base)
ovl.addMethod(CtNewMethod.make("""
public static float baseMana(java.util.UUID u, float tmax) {
  float a = baseTarget(u) - tmax;
  return a > 0.0f ? round2((double) a) : 0.0f;
}""", ovl))
ovl.addMethod(CtNewMethod.make(f"""
public static boolean classesOn() {{
  return {PKG}.SkillClass.allowedFn() != null;
}}""", ovl))
# ms since this session's first Perks.ovl (0 = this call starts the session). A new session = no entry or a different PlayerRef object (a
# relog makes a new PlayerRef; a world change keeps it - the Xbow.rebind rule, verified bytecode), so a relog inside the 30 s
# retainOnline window still starts a fresh hold.
ovl.addMethod(CtNewMethod.make("""
public static long sessionAge(java.util.UUID u, Object pr, long now) {
  Object[] e = (Object[]) SESS.get(u);
  if (e == null || e[0] != pr) {
    SESS.put(u, new Object[] { pr, Long.valueOf(now) });
    return 0L;
  }
  long a = now - ((Long) e[1]).longValue();
  return a < 0L ? 0L : a;
}""", ovl))
# review fix (LOW, 2026-09-28): SkyyClasses / SkyyProfiles publish the class from their own ReadyTask, maybe AFTER our first 1 s tick. With
# no class yet the class skill counts 0 (the Overall Level dips) and a magic user gets the plain base Mana, so max Health / Mana would
# shrink for a moment and a full-health player would be clamped down. true = Perks.ovl writes nothing this second (the Base Mana / Overall
# modifiers the engine saved with the player stay in place): the session is younger than HOLD_MS, SkyyClasses is installed and no class
# is published. After HOLD_MS a still classless player is computed normally (class skill 0, plain base).
ovl.addMethod(CtNewMethod.make("""
public static boolean hold(java.util.UUID u, Object pr, long now) {
  long a = sessionAge(u, pr, now);
  return a < HOLD_MS && classesOn() && classOf(u) == null;
}""", ovl))
# {sum, n} (spec 2.2 / 2.3): the listed slots + the profile's own class skill (0 without a class while SkyyClasses is loaded, skipped
# without SkyyClasses or for a class SkyySkills does not know - one WARN per class name)
ovl.addMethod(CtNewMethod.make(f"""
public static int[] sums(java.util.UUID u, long[] d) {{
  int sum = 0;
  int n = 0;
  int[] sl = {PKG}.OverallCfg.SLOTS;
  for (int i = 0; i < sl.length; i++) {{
    int s = sl[i];
    if (s < 0 || s >= {PKG}.SkillDefs.N) continue;
    sum += {PKG}.SkillDefs.levelOf(d[s]);
    n++;
  }}
  if ({PKG}.OverallCfg.CLASS && classesOn()) {{
    String c = classOf(u);
    if (c == null) n++;
    else {{
      int cs = {PKG}.SkillClass.slotOfClass(c);
      if (cs >= 0) {{ sum += {PKG}.SkillDefs.levelOf(d[cs]); n++; }}
      else if (BADCLS.putIfAbsent(c.toLowerCase(), Boolean.TRUE) == null) {PKG}.SkillCfg.warn("class " + c + " has no class skill in SkyySkills - it is left out of the Overall Level");
    }}
  }}
  return new int[] {{ sum, n }};
}}""", ovl))
ovl.addMethod(CtNewMethod.make("""
public static int level(int[] sc) {
  return sc[1] <= 0 ? 0 : sc[0] / sc[1];
}""", ovl))
ovl.addMethod(CtNewMethod.make("""
public static int tenths(int[] sc) {
  return sc[1] <= 0 ? 0 : (int) (((long) sc[0] * 10L) / (long) sc[1]);
}""", ovl))
ovl.addMethod(CtNewMethod.make("""
public static String avg(int t) {
  return (t / 10) + "." + (t % 10);
}""", ovl))
ovl.addMethod(CtNewMethod.make(f"""
public static float hp(int lv) {{
  return !{PKG}.OverallCfg.ON || lv <= 0 ? 0.0f : round2(lv * {PKG}.OverallCfg.HP);
}}""", ovl))
ovl.addMethod(CtNewMethod.make(f"""
public static float mana(int lv) {{
  return !{PKG}.OverallCfg.ON || lv <= 0 ? 0.0f : round2(lv * {PKG}.OverallCfg.MANA);
}}""", ovl))
ovl.addMethod(CtNewMethod.make(f"""
public static int levelOf(java.util.UUID u) {{
  return level(sums(u, {PKG}.SkillStore.data(u)));
}}""", ovl))
# does XP in this slot move the Overall Level?
ovl.addMethod(CtNewMethod.make(f"""
public static boolean counts(java.util.UUID u, int skill) {{
  int[] sl = {PKG}.OverallCfg.SLOTS;
  for (int i = 0; i < sl.length; i++) if (sl[i] == skill) return true;
  return {PKG}.OverallCfg.CLASS && classesOn() && skill >= 0 && skill == {PKG}.SkillClass.slotOfClass(classOf(u));
}}""", ovl))
# skill:overall:<uuid> = Integer, re-put only when it differs (never removed, like skill:<uuid>)
ovl.addMethod(CtNewMethod.make(f"""
public static void publish(java.util.UUID u, int lv) {{
  try {{
    java.util.Map br = {PKG}.SkillStore.bridge();
    String k = "skill:overall:" + u.toString();
    Object o = br.get(k);
    if (!(o instanceof Integer) || ((Integer) o).intValue() != lv) br.put(k, Integer.valueOf(lv));
  }} catch (Throwable t) {{ }}
}}""", ovl))
ovl.addMethod(CtNewMethod.make("""
public static synchronized void addHeal(java.util.UUID u, int n) {
  if (n <= 0) return;
  Integer c = (Integer) HEAL.get(u);
  HEAL.put(u, Integer.valueOf((c == null ? 0 : c.intValue()) + n));
}""", ovl))
ovl.addMethod(CtNewMethod.make("""
public static synchronized int takeHeal(java.util.UUID u) {
  Integer c = (Integer) HEAL.remove(u);
  return c == null ? 0 : c.intValue();
}""", ovl))
ovl.addMethod(CtNewMethod.make("""
public static void forget(java.util.UUID u) {
  if (u != null) HEAL.remove(u);
}""", ovl))
ovl.addMethod(CtNewMethod.make("""
public static void retain(java.util.Set online) {
  HEAL.keySet().retainAll(online);
  SESS.keySet().retainAll(online);
}""", ovl))
# world thread, SkillXp.gain4 after the SKILL LEVEL UP lines (oldLv / newLv = this award's level before / after): bridge + pending heal
# always; the chat line only with overall.chat AND the player's skills.overallUp switch (Settings-Spec 1.3: gate only the send)
ovl.addMethod(CtNewMethod.make(f"""
public static void levelUp({PR} pr, java.util.UUID u, int skill, long oldLv, long newLv) {{
  try {{
    if (newLv <= oldLv || !counts(u, skill)) return;
    int[] sc = sums(u, {PKG}.SkillStore.data(u));
    int after = level(sc);
    int before = sc[1] <= 0 ? 0 : (sc[0] - (int) (newLv - oldLv)) / sc[1];
    if (before < 0) before = 0;
    publish(u, after);
    if (after <= before) return;
    int g = after - before;
    addHeal(u, g);
    if (!{PKG}.OverallCfg.CHAT || pr == null || !{PKG}.SkillStore.notifyOn(u, "skills.overallUp")) return;
    String bonus = "";
    float h = hp(g);
    float m = mana(g);
    if (h > 0.0f) bonus = bonus + "  +" + num((double) h) + " max Health";
    if (m > 0.0f) bonus = bonus + "  +" + num((double) m) + " max Mana";
    pr.sendMessage({MSG}.raw("OVERALL LEVEL UP  " + before + " -> " + after + (bonus.length() > 0 ? " " + bonus : "")).color("#ffe08a"));
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("overall level up failed: " + t); }}
}}""", ovl))
ovl.addMethod(CtNewMethod.make(f"""
public static String magicText() {{
  return {PKG}.OverallCfg.join({PKG}.OverallCfg.MAGIC, ", ");
}}""", ovl))
# Overall page: "Mining 14 - Foraging 9 - ... - Divinity 18 (your class)"
ovl.addMethod(CtNewMethod.make(f"""
public static String listText(java.util.UUID u, long[] d) {{
  StringBuilder sb = new StringBuilder();
  int[] sl = {PKG}.OverallCfg.SLOTS;
  for (int i = 0; i < sl.length; i++) {{
    int s = sl[i];
    if (s < 0 || s >= {PKG}.SkillDefs.N) continue;
    if (sb.length() > 0) sb.append(" - ");
    sb.append({PKG}.SkillDefs.LABELS[s]).append(" ").append({PKG}.SkillDefs.levelOf(d[s]));
  }}
  if ({PKG}.OverallCfg.CLASS && classesOn()) {{
    String c = classOf(u);
    String part = null;
    if (c == null) part = "Class skill 0 (choose a class with /class)";
    else {{
      int cs = {PKG}.SkillClass.slotOfClass(c);
      if (cs >= 0) part = {PKG}.SkillClass.skillName(u, cs) + " " + {PKG}.SkillDefs.levelOf(d[cs]) + " (your class)";
    }}
    if (part != null) {{
      if (sb.length() > 0) sb.append(" - ");
      sb.append(part);
    }}
  }}
  return sb.length() == 0 ? "none" : sb.toString();
}}""", ovl))
ovl.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList nowLines(java.util.UUID u, int lv) {{
  java.util.ArrayList out = new java.util.ArrayList();
  if (!{PKG}.OverallCfg.ON) out.add("Overall Level Health and Mana are off on this server");
  else {{
    out.add("+" + num((double) hp(lv)) + " max Health (" + num({PKG}.OverallCfg.HP) + " per Overall Level)");
    out.add("+" + num((double) mana(lv)) + " max Mana (" + num({PKG}.OverallCfg.MANA) + " per Overall Level)");
  }}
  if (!{PKG}.OverallCfg.MANA_ON) out.add("Base Mana from Skills is off on this server");
  else if (magic(u)) out.add("Base Mana " + num((double) baseTarget(u)) + " - " + classOf(u) + " is a magic user");
  else out.add("Base Mana " + num((double) round2({PKG}.OverallCfg.BASE)) + ({PKG}.OverallCfg.MAGIC.length > 0 ? " (magic users - " + magicText() + " - start at " + num((double) round2({PKG}.OverallCfg.MAGIC_BASE)) + ")" : ""));
  return out;
}}""", ovl))
ovl.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList nextLines(int lv) {{
  java.util.ArrayList out = new java.util.ArrayList();
  if (lv >= {PKG}.SkillDefs.MAX) return out;
  if (!{PKG}.OverallCfg.ON) {{ out.add("Nothing - Overall Level Health and Mana are off"); return out; }}
  if ({PKG}.OverallCfg.HP > 0.0) out.add("+" + num((double) round2({PKG}.OverallCfg.HP)) + " max Health");
  if ({PKG}.OverallCfg.MANA > 0.0) out.add("+" + num((double) round2({PKG}.OverallCfg.MANA)) + " max Mana");
  if (out.isEmpty()) out.add("Nothing - both amounts are 0 on this server");
  return out;
}}""", ovl))
# ================= skill:fn:overall (0.4.6, spec 4.8): apply(UUID) or apply(Object[]{UUID}) -> Object[]{Integer level, Integer averageTenths,
# Integer skillsCounted, Float maxHealthBonus, Float maxManaBonus, Float baseMana}; null on a bad argument or any error. Any thread, may load
# the player's file (like skill:fn:level), never touches ECS, never throws.
ofn.addInterface(pool.get("java.util.function.Function"))
ofn.addConstructor(CtNewConstructor.make("public OverallFn() { }", ofn))
ofn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    java.util.UUID u = null;
    if (arg instanceof java.util.UUID) u = (java.util.UUID) arg;
    else if (arg instanceof Object[]) {{
      Object[] a = (Object[]) arg;
      if (a.length >= 1 && a[0] instanceof java.util.UUID) u = (java.util.UUID) a[0];
    }}
    if (u == null) return null;
    int[] sc = {PKG}.Overall.sums(u, {PKG}.SkillStore.data(u));
    int lv = {PKG}.Overall.level(sc);
    return new Object[] {{ Integer.valueOf(lv), Integer.valueOf({PKG}.Overall.tenths(sc)), Integer.valueOf(sc[1]), Float.valueOf({PKG}.Overall.hp(lv)), Float.valueOf({PKG}.Overall.mana(lv)), Float.valueOf({PKG}.Overall.baseTarget(u)) }};
  }} catch (Throwable t) {{ return null; }}
}}""", ofn))

''')

# ================================================================ SkillFn: skill:fn:level also answers "Overall" (spec 4.8)
rep('''    Object[] a = (Object[]) arg;
    int i = {PKG}.SkillDefs.indexOf(String.valueOf(a[1]));
    if (i < 0) return Integer.valueOf(0);''', '''    Object[] a = (Object[]) arg;
    if ("overall".equalsIgnoreCase(String.valueOf(a[1]).trim())) return Integer.valueOf({PKG}.Overall.levelOf((java.util.UUID) a[0]));
    int i = {PKG}.SkillDefs.indexOf(String.valueOf(a[1]));
    if (i < 0) return Integer.valueOf(0);''')

# ================================================================ Xbow part 1: meter / feedback helpers, rebind, clear
rep('''xbw.addField(CtField.make('public static final String UNLOCK = "Unlocked: Crossbows stay loaded when you switch slots";', xbw))
''', '''xbw.addField(CtField.make('public static final String UNLOCK = "Unlocked: Crossbows stay loaded when you switch slots";', xbw))
xbw.addField(CtField.make('public static final String CHARGES = "SignatureCharges";', xbw))   # 0.4.6: no DefaultEntityStatTypes getter for it
''')
rep('''    if (!{PKG}.XbowCfg.ON || s < 0 || s != {PKG}.SkillClass.slotOfClass("Archer")) return null;
    if (!next && lv >= {PKG}.XbowCfg.LEVEL) return TEXT;
    if (next && lv + 1 == {PKG}.XbowCfg.LEVEL) return TEXT;''', '''    if (!{PKG}.XbowCfg.ON || s < 0 || s != {PKG}.SkillClass.slotOfClass("Archer")) return null;
    String tx = ({PKG}.XbowCfg.METER && {PKG}.SkillStore.notifyOn(u, "skills.xbowMeter")) ? TEXT + " (bolts and big-arrow meter)" : TEXT;
    if (!next && lv >= {PKG}.XbowCfg.LEVEL) return tx;
    if (next && lv + 1 == {PKG}.XbowCfg.LEVEL) return tx;''')
rep('''public static void reset({PKG}.XbowState s) {{
  for (int i = 0; i < s.n.length; i++) {{ s.n[i] = 0; s.stk[i] = null; s.cre[i] = false; }}''',
    '''public static void reset({PKG}.XbowState s) {{
  for (int i = 0; i < s.n.length; i++) {{ s.n[i] = 0; s.stk[i] = null; s.cre[i] = false; s.sig[i] = 0.0f; s.chg[i] = 0.0f; }}''')
rep('''  if (slot >= 0 && slot < s.n.length) {{ s.n[slot] = 0; s.stk[slot] = null; s.cre[slot] = false; }}
  s.pendSlot = -1;''', '''  if (slot >= 0 && slot < s.n.length) {{ s.n[slot] = 0; s.stk[slot] = null; s.cre[slot] = false; s.sig[slot] = 0.0f; s.chg[slot] = 0.0f; }}
  s.pendSlot = -1;''')
after('''public static void dbg({PR} pr, String text) {{
  if (!{PKG}.XbowCfg.DEBUG || pr == null) return;
  try {{
    if (!pr.hasPermission("skyyskills.admin")) return;
    pr.sendMessage({MSG}.raw("[Skills debug] " + text).color("#c8a0ff"));
  }} catch (Throwable t) {{ }}
}}""", xbw))
''', r'''# ---- 0.4.6 (LOCKED Skyy 2026-09-25): loads survive world changes, the big-arrow meter, the sound + chat hint ----
# one kept slot cleared (bolts, meter, stack, creative flag) - the armed restore is left alone (drop() cancels it)
xbw.addMethod(CtNewMethod.make(f"""
public static void clearSlot({PKG}.XbowState s, int i) {{
  if (i < 0 || i >= s.n.length) return;
  s.n[i] = 0; s.stk[i] = null; s.cre[i] = false; s.sig[i] = 0.0f; s.chg[i] = 0.0f;
}}""", xbw))
xbw.addMethod(CtNewMethod.make(f"""
public static boolean hasKept({PKG}.XbowState s, int i) {{
  return i >= 0 && i < s.n.length && (s.n[i] > 0 || s.sig[i] > 0.0f || s.chg[i] > 0.0f);
}}""", xbw))
# review fix (LOW, 2026-09-28): at most ONE banked big-arrow meter. Skyy locked "keep the meter across a slot switch", but banked per slot
# two crossbows could bank two full meters (up to nine). onSlot calls this right after it banks a meter (SignatureEnergy or
# SignatureCharges above 0) for `keep`: every other slot's banked meter is zeroed; its kept bolts stay (a slot left with no bolts is
# cleared, so it is no longer a kept entry). Returns how many older meters were dropped.
xbw.addMethod(CtNewMethod.make(f"""
public static int keepOneMeter({PKG}.XbowState s, int keep) {{
  int d = 0;
  for (int j = 0; j < s.n.length; j++) {{
    if (j == keep || !(s.sig[j] > 0.0f || s.chg[j] > 0.0f)) continue;
    s.sig[j] = 0.0f;
    s.chg[j] = 0.0f;
    if (s.n[j] <= 0) clearSlot(s, j);
    d++;
  }}
  return d;
}}""", xbw))
# Which entity / connection this state belongs to. VERIFIED (bytecode 2026-09-28): a world change / teleport is
# PlayerRef.removeFromStore -> World.addPlayer -> PlayerRef.addToStore - the SAME PlayerRef object (and its Holder) moves, only the entity
# Ref is new; PlayerRef.clone() returns this; a login is Universe.addPlayer -> new PlayerRef. So: same Ref = 0; same PlayerRef + new Ref =
# 1 (world change: the kept loads stay, the held-long-enough guard and an armed restore's delay start over in the new world); a new
# PlayerRef = 2 (relog: everything wiped). The first bind of a fresh state keeps enterAt "long ago" (the 0.4.5 rule).
xbw.addMethod(CtNewMethod.make(f"""
public static int rebind({PKG}.XbowState s, {REF} ref, {PR} pr) {{
  if (s.ref == null) {{ s.ref = ref; s.pr = pr; return 0; }}
  if (s.ref == ref) {{ if (s.pr == null) s.pr = pr; return 0; }}
  if (s.pr != null && s.pr == pr) {{
    s.ref = ref;
    s.enterAt = s.ticks;
    if (s.pendSlot >= 0) s.pendAt = s.ticks;
    return 1;
  }}
  reset(s);
  s.ref = ref;
  s.pr = pr;
  return 2;
}}""", xbw))
# the meter part (admin perk.archery.keepLoaded.meter AND the player's skills.xbowMeter switch)
xbw.addMethod(CtNewMethod.make(f"""
public static boolean meterOn(java.util.UUID u) {{
  return {PKG}.XbowCfg.METER && {PKG}.SkillStore.notifyOn(u, "skills.xbowMeter");
}}""", xbw))
xbw.addMethod(CtNewMethod.make(f"""
public static int chargesIdx() {{
  try {{ return {ESTT}.getAssetMap().getIndex(CHARGES); }} catch (Throwable t) {{ return -1; }}
}}""", xbw))
xbw.addMethod(CtNewMethod.make(f"""
public static float statNow({ESM} esm, int idx) {{
  if (esm == null || idx < 0) return 0.0f;
  {ESV} v = esm.get(idx);
  if (v == null) return 0.0f;
  float x = v.get();
  return x > 0.0f ? x : 0.0f;
}}""", xbw))
# put a kept stat value back: at most the current cap, never lowers what is there now (true = written)
xbw.addMethod(CtNewMethod.make(f"""
public static boolean putStat({ESM} esm, int idx, float want) {{
  if (esm == null || idx < 0 || !(want > 0.0f)) return false;
  {ESV} v = esm.get(idx);
  if (v == null) return false;
  float mx = v.getMax();
  float t = want < mx ? want : mx;
  if (!(t > v.get())) return false;
  esm.setStatValue(idx, t);
  return true;
}}""", xbw))
# "3" / "2.5" for the debug lines
xbw.addMethod(CtNewMethod.make("""
public static String f1(float v) {
  long t = Math.round((double) v * 10.0);
  return (t % 10L == 0L) ? String.valueOf(t / 10L) : (t / 10L) + "." + (t % 10L);
}""", xbw))
# world thread, after a restore: the vanilla crossbow load sound to this player only (perk.archery.keepLoaded.sound + skills.xbowSound)
# when bolts went back in, and one chat hint (perk.archery.keepLoaded.hint + skills.xbowHint) when bolts or the meter came back
xbw.addMethod(CtNewMethod.make(f"""
public static void feedback({PR} pr, java.util.UUID u, int pay, int need, boolean met) {{
  if (pr == null) return;
  try {{
    String snd = {PKG}.XbowCfg.SOUND;
    if (pay > 0 && snd != null && snd.length() > 0 && {PKG}.SkillStore.notifyOn(u, "skills.xbowSound")) {{
      int si = {SEV}.getAssetMap().getIndex(snd);
      if (si >= 0) {SNU}.playSoundEvent2dToPlayer(pr, si, {SCAT}.SFX);
    }}
  }} catch (Throwable t) {{ failed("sound", t); }}
  try {{
    if ((pay > 0 || met) && {PKG}.XbowCfg.HINT && {PKG}.SkillStore.notifyOn(u, "skills.xbowHint")) {{
      String tx;
      if (pay <= 0) tx = "Crossbow ready - big-arrow meter kept" + (need > 0 ? " (no Crude Arrows for the bolts)" : "");
      else tx = "Crossbow reloaded - " + (pay < need ? pay + " of " + need : String.valueOf(pay)) + (pay == 1 && need <= 1 ? " bolt" : " bolts") + " back in" + (met ? " + big-arrow meter" : "") + (pay < need ? " (not enough Crude Arrows)" : "");
      pr.sendMessage({MSG}.raw("[Skills] " + tx).color("#b8f0a0"));
    }}
  }} catch (Throwable t) {{ failed("hint", t); }}
}}""", xbw))
''')

# ================================================================ SkillXp.gain4: the Overall level-up (spec 4.6)
rep('''    if (lvOn) pr.sendMessage({MSG}.raw(need > 0L ? "  next: " + sk + " " + (r[1] + 1L) + " at " + {PKG}.SkillDefs.progress(r[2]) + " XP - /skills" : "  " + sk + " is now MAX level!").color("#c8b070"));
    {PKG}.SkillStore.publish(u);''', '''    if (lvOn) pr.sendMessage({MSG}.raw(need > 0L ? "  next: " + sk + " " + (r[1] + 1L) + " at " + {PKG}.SkillDefs.progress(r[2]) + " XP - /skills" : "  " + sk + " is now MAX level!").color("#c8b070"));
    {PKG}.Overall.levelUp(pr, u, skill, r[0], r[1]);
    {PKG}.SkillStore.publish(u);''')

# ================================================================ HealXp.offer: the self rate (LOCKED 2026-09-25)
rep('''public static boolean offer(java.util.UUID u, double hp, String source, String expect) {{
  try {{
    if (u == null || !{PKG}.DivCfg.on()) return false;''', '''public static boolean offer(java.util.UUID u, double hp, String source, String expect, boolean self) {{
  try {{
    if (u == null || !{PKG}.DivCfg.onFor(self)) return false;''')
rep('''    long base = amount(hp, {PKG}.DivCfg.PER_HP);''', '''    long base = amount(hp, {PKG}.DivCfg.rate(self));''')
rep('''# ================= skill:fn:healxp (0.4.4): apply(Object[]{UUID healer, Number hpHealedOnOthers, String source [, String expectKey]}) -> Boolean
# Published for SkyyClasses 0.1.6 (source "classes:heal"); HealXp.offer has every rule.''', '''# ================= skill:fn:healxp (0.4.4): apply(Object[]{UUID healer, Number hpHealedOnOthers, String source [, String expectKey]}) -> Boolean
# Published for SkyyClasses 0.1.6 (source "classes:heal"); HealXp.offer has every rule.
# 0.4.6 (LOCKED Skyy 2026-09-25): an OPTIONAL trailing Boolean self - apply(Object[]{UUID healer, Number hp, String source, String expectKey,
# Boolean self}); the LAST element when it is a Boolean and the array has at least 4 elements ({u, hp, src, Boolean} works too). TRUE = the
# HP was healed on the healer themself (divinity.healXpPerHpSelf, 0.25); absent / FALSE = on others (divinity.healXpPerHp, 0.2). One cap.''')
rep('''hfn.addConstructor(CtNewConstructor.make("public SkillHealFn() { }", hfn))
''', '''hfn.addConstructor(CtNewConstructor.make("public SkillHealFn() { }", hfn))
hfn.addMethod(CtNewMethod.make("""
public static boolean selfArg(Object[] a) {
  if (a == null || a.length < 4) return false;
  Object o = a[a.length - 1];
  return o instanceof Boolean && ((Boolean) o).booleanValue();
}""", hfn))
''')
rep('''    return {PKG}.HealXp.offer((java.util.UUID) a[0], ((Number) a[1]).doubleValue(), src, expect) ? Boolean.TRUE : Boolean.FALSE;''',
    '''    return {PKG}.HealXp.offer((java.util.UUID) a[0], ((Number) a[1]).doubleValue(), src, expect, selfArg(a)) ? Boolean.TRUE : Boolean.FALSE;''')

# ================================================================ Perks: the three new MAX modifiers + heal (spec 4.5), switch / retain hooks
before('''perk.addMethod(CtNewMethod.make(f"""
public static void tick(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref) {{''', r'''# 0.4.6 (Overall-Level-Spec 4.5): base Mana + the Overall Level Health / Mana, each under its own key, computed from scratch (never from the
# current max) every second; its own try so an Overall failure never stops the per-skill perks; NOT gated by perk.enabled. A pending
# Overall level-up heal (SkillXp.gain4 -> Overall.addHeal) is applied right AFTER the new Health modifier; skipped (dropped) while dead
# or at 0 Health.
perk.addField(CtField.make("public static boolean OVL_FAILED_ONCE = false;", perk))
# dead = a DeathComponent is on the entity; an unreadable check counts as alive (the heal below also needs Health above 0, and a dead
# player is at 0), so a failing check never costs the Base Mana / Overall modifiers of that second
perk.addMethod(CtNewMethod.make(f"""
public static boolean dead({CB} cb, {REF} ref) {{
  try {{ return cb != null && cb.getComponent(ref, {DTH}.getComponentType()) != null; }} catch (Throwable t) {{ return false; }}
}}""", perk))
# review fix (LOW, 2026-09-28): while Overall.hold (first 10 s of a session, SkyyClasses installed, no class published yet) nothing is written,
# published or healed - the saved modifiers stay, a pending level-up heal waits for the first normal second.
perk.addMethod(CtNewMethod.make(f"""
public static void ovl(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref, {ESM} m) {{
  try {{
    if ({PKG}.Overall.hold(u, pr, System.currentTimeMillis())) return;
    int[] sc = {PKG}.Overall.sums(u, {PKG}.SkillStore.data(u));
    int ol = {PKG}.Overall.level(sc);
    int mi = {DST}.getMana();
    int hi = {DST}.getHealth();
    mod(m, mi, "skyyskill_basemana", {PKG}.Overall.baseMana(u, {PKG}.Overall.typeMax(mi)));
    mod(m, hi, "skyyskill_overallhp", {PKG}.Overall.hp(ol));
    mod(m, mi, "skyyskill_overallmana", {PKG}.Overall.mana(ol));
    {PKG}.Overall.publish(u, ol);
    int g = {PKG}.Overall.takeHeal(u);
    if (g > 0 && {PKG}.OverallCfg.ON && {PKG}.OverallCfg.HEAL && !dead(cb, ref)) {{
      {ESV} hv = m.get(hi);
      float amt = {PKG}.Overall.round2(g * {PKG}.OverallCfg.HP);
      if (hv != null && hv.get() > 0.0f && amt > 0.0f) m.addStatValue(hi, amt);
    }}
  }} catch (Throwable t) {{
    if (!OVL_FAILED_ONCE) {{ OVL_FAILED_ONCE = true; {PKG}.SkillCfg.warn("overall level tick failed (logged once): " + t); }}
  }}
}}""", perk))
''')
rep('''    mod(m, {DST}.getMana(), "skyyskill_mana", total({PKG}.PerkCfg.MANA, lv));
''', '''    mod(m, {DST}.getMana(), "skyyskill_mana", total({PKG}.PerkCfg.MANA, lv));
    ovl(u, pr, cb, ref, m);
''')
rep('''  {PKG}.Xbow.forget(u);
  {PKG}.Xbow.refresh(u);
}}""", perk))''', '''  {PKG}.Xbow.forget(u);
  {PKG}.Xbow.refresh(u);
  {PKG}.Overall.forget(u);
}}""", perk))''')
rep('''    {PKG}.Xbow.retain(online);
''', '''    {PKG}.Xbow.retain(online);
    {PKG}.Overall.retain(online);
''')

# ================================================================ Xbow part 2: world changes, the meter, feedback
rep('''    if (s.ref == null) s.ref = ref;
    else if (s.ref != ref) {{ reset(s); s.ref = ref; }}
    fresh(s, u);''', '''    if (rebind(s, ref, pr) == 1) dbg(pr, "kept loads survive the world change");
    fresh(s, u);''')
rep('''          {ESV} v = esm == null ? null : esm.get({DST}.getAmmo());
          if (v != null) {{
            int k = (int) Math.floor((double) v.get());
            int mx = (int) Math.floor((double) v.getMax());
            if (k > mx) k = mx;
            if (k > 6) k = 6;
            if (k > 0) {{
              s.n[prev] = k;
              s.stk[prev] = is;
              s.cre[prev] = {PKG}.Acro.creativeMode(st, ref);
              kept = true;
              msg = "kept " + k + " bolts - " + is.getItemId() + ", slot " + (prev + 1);
            }}
          }}
        }}
        if (!kept) {{ s.n[prev] = 0; s.stk[prev] = null; s.cre[prev] = false; }}''', '''          {ESV} v = esm == null ? null : esm.get({DST}.getAmmo());
          if (v != null) {{
            int k = (int) Math.floor((double) v.get());
            int mx = (int) Math.floor((double) v.getMax());
            if (k > mx) k = mx;
            if (k > 6) k = 6;
            if (k < 0) k = 0;
            float sg = {PKG}.XbowCfg.METER ? statNow(esm, {DST}.getSignatureEnergy()) : 0.0f;
            float ch = {PKG}.XbowCfg.METER ? statNow(esm, chargesIdx()) : 0.0f;
            if (k > 0 || sg > 0.0f || ch > 0.0f) {{
              s.n[prev] = k;
              s.sig[prev] = sg;
              s.chg[prev] = ch;
              s.stk[prev] = is;
              s.cre[prev] = {PKG}.Acro.creativeMode(st, ref);
              kept = true;
              msg = "kept " + k + " bolts" + (sg > 0.0f || ch > 0.0f ? " + meter " + f1(sg) + "/" + f1(ch) : "") + " - " + is.getItemId() + ", slot " + (prev + 1);
              if ((sg > 0.0f || ch > 0.0f) && keepOneMeter(s, prev) > 0) msg = msg + " (the older banked meter is dropped - one at a time)";
            }}
          }}
        }}
        if (!kept) clearSlot(s, prev);''')
rep('''    if (neu >= 0 && neu < s.n.length && s.n[neu] > 0) {{
      {IS} ns = neu < cap ? c.getItemStack((short) neu) : null;
      if (act && ns != null && !ns.isEmpty() && s.stk[neu] != null && ns.isEquivalentType(s.stk[neu])) {{
        s.pendSlot = neu;
        s.pendAt = s.ticks;
      }} else {{
        if (msg == null) msg = act ? "load dropped - crossbow left slot " + (neu + 1) : "load dropped - the perk is not active right now";
        s.n[neu] = 0; s.stk[neu] = null; s.cre[neu] = false;
      }}
    }}''', '''    if (hasKept(s, neu)) {{
      {IS} ns = neu < cap ? c.getItemStack((short) neu) : null;
      if (act && ns != null && !ns.isEmpty() && s.stk[neu] != null && ns.isEquivalentType(s.stk[neu])) {{
        s.pendSlot = neu;
        s.pendAt = s.ticks;
      }} else {{
        if (msg == null) msg = act ? "load dropped - crossbow left slot " + (neu + 1) : "load dropped - the perk is not active right now";
        clearSlot(s, neu);
      }}
    }}''')
rep('''    s.ticks = s.ticks + 1L;
    if (s.ref != ref) {{ reset(s); s.ref = ref; return; }}
    if (!fresh(s, u)) return;''', '''    s.ticks = s.ticks + 1L;
    int rb = rebind(s, ref, pr);
    if (rb == 2) return;
    if (rb == 1) dbg(pr, "kept loads survive the world change");
    if (!fresh(s, u)) return;''')
rep('''    int need = target - cur;
    if (need <= 0) {{ drop(s, slot); dbg(pr, "nothing to put back - " + cur + " bolts already loaded"); return; }}
    String id = is.getItemId();''', '''    int need = target - cur;
    boolean mw = (s.sig[slot] > 0.0f || s.chg[slot] > 0.0f) && meterOn(u);
    if (need <= 0 && !mw) {{ drop(s, slot); dbg(pr, "nothing to put back - " + cur + " bolts already loaded"); return; }}
    String id = is.getItemId();''')
rep('''    boolean free = s.cre[slot] && {PKG}.Acro.creativeMode(st, ref);
    int pay = 0;
    int have = 0;
    if (free) {{
      pay = need;
    }} else {{''', '''    boolean free = s.cre[slot] && {PKG}.Acro.creativeMode(st, ref);
    int pay = 0;
    int have = 0;
    if (need <= 0) {{
      pay = 0;
    }} else if (free) {{
      pay = need;
    }} else {{''')
rep('''    drop(s, slot);
    if (pay > 0) esm.setStatValue(ai, (float) (cur + pay));
    if (free) dbg(pr, "put back " + pay + " bolts (creative, free)");
    else if (pay >= need) dbg(pr, "put back " + pay + " bolts, paid " + pay + " Crude Arrows");
    else dbg(pr, "put back " + pay + " of " + need + " bolts - only " + pay + " Crude Arrows");''', '''    float sg = s.sig[slot];
    float ch = s.chg[slot];
    drop(s, slot);
    if (pay > 0) esm.setStatValue(ai, (float) (cur + pay));
    boolean met = false;
    if (mw) {{
      if (putStat(esm, {DST}.getSignatureEnergy(), sg)) met = true;
      if (putStat(esm, chargesIdx(), ch)) met = true;
    }}
    feedback(pr, u, pay, need, met);
    String mt = met ? " + meter " + f1(sg) + "/" + f1(ch) : "";
    if (need <= 0) dbg(pr, "bolts already loaded (" + cur + ")" + mt);
    else if (free) dbg(pr, "put back " + pay + " bolts (creative, free)" + mt);
    else if (pay >= need) dbg(pr, "put back " + pay + " bolts, paid " + pay + " Crude Arrows" + mt);
    else dbg(pr, "put back " + pay + " of " + need + " bolts - only " + pay + " Crude Arrows" + mt);''')

# ================================================================ /skills header: the Overall Level row (spec 4.7)
rep('''    int cs = {PKG}.SkillClass.slot(u);
    int[] rows = {PKG}.SkillDefs.ROW_SLOTS;
    int sum = 0;
    int shown = 0;
    for (int i = 0; i < rows.length; i++) {{
      int sl = rows[i];
      if (sl == {PKG}.SkillDefs.COMBAT) {{
        if (cs < 0) continue;
        sl = cs;
      }}
      sum += {PKG}.SkillDefs.levelOf(d[sl]);
      shown++;
    }}
    long avg10 = shown > 0 ? Math.round(sum * 10.0 / shown) : 0L;
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 30); Text: \\\\"Skills\\\\"; Style: (FontSize: 16, RenderBold: true, TextColor: #e6fff0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 18); Text: \\\\"" + safe("Skill average " + (avg10 / 10L) + "." + (avg10 % 10L) + " - every level up pays coins") + "\\\\"; Style: (FontSize: 11, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");''',
    '''    int cs = {PKG}.SkillClass.slot(u);
    int[] rows = {PKG}.SkillDefs.ROW_SLOTS;
    int[] osc = {PKG}.Overall.sums(u, d);
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 30); Text: \\\\"Skills\\\\"; Style: (FontSize: 16, RenderBold: true, TextColor: #e6fff0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.appendInline("#SkyySkills", "Group #SkyySkOvRow {{ Anchor: (Height: 28); LayoutMode: Left; }}");
    b.appendInline("#SkyySkOvRow", "Label #SkyySkOv {{ Anchor: (Width: 490, Height: 28); Text: \\\\"\\\\"; Style: (FontSize: 14, RenderBold: true, TextColor: #E8A93B, VerticalAlignment: Center); }}");
    b.set("#SkyySkOv.Text", "Overall Level " + {PKG}.Overall.level(osc) + "  -  average " + {PKG}.Overall.avg({PKG}.Overall.tenths(osc)) + " of " + osc[1] + " skills");
    b.appendInline("#SkyySkOvRow", "TextButton #SkyySkOvStat {{ Anchor: (Width: 110, Height: 26); Text: \\\\"Overall\\\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyySkOvStat", {EVD}.of("a", "skstatov"));''')
# the coin hint moves from the replaced header line to the footer (spec 4.7); the footer is shortened so it keeps 0.4.5's width (~100
# characters at 10 pt fit the 608 px row)
rep('''Text: \\\\"Gather - brew - smelt - cook - class weapons - run jump fall dodge - explore.  Stats shows every boost\\\\"; Style: (FontSize: 10''',
    '''Text: \\\\"Gather - brew - smelt - cook - fight - move - explore.  Stats shows every boost - level ups pay coins\\\\"; Style: (FontSize: 10''')
assert len("Gather - brew - smelt - cook - fight - move - explore.  Stats shows every boost - level ups pay coins") <= \
    len("Gather - brew - smelt - cook - class weapons - run jump fall dodge - explore.  Stats shows every boost")

# ================================================================ OverallPage (spec 4.7, VANILLA LOOK) - after StatsPage, before SkillsPage.handleDataEvent
before('''page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
      if (data.indexOf("skstat" + i + "\\\\"") >= 0) {{''', r'''# ================= OverallPage (0.4.6): the Overall Level page (research/Overall-Level-Spec.md 2.8.2 / 4.7) - VANILLA LOOK =================
# Skyy 2026-09-28 (tools/AGENT-BRIEF.md UI LOOK): mirror the game's own UI styles. Every value below is from Assets.zip
# Common/UI/Custom/Common.ui: @Container (#Title = Common/ContainerHeaderNoRunes.png HorizontalBorder 35 / VerticalBorder 0, height 38,
# Padding Top 7; #Content = Common/ContainerPatch.png Border 23, padding 9 + 8), @TitleStyle (#b4c8c9, bold, uppercase; 15 pt there),
# @SubtitleStyle (#96a9be bold uppercase), @DefaultLabelStyle (#96a9be), @ColorDefault #ffffff, @ColorGrayCaption #878e9c,
# @ContentSeparator (1 px #2b3542), @CircularProgressBar (#1a2030 / #aa7c4a), @SecondaryTextButtonStyle (Common/Buttons/Secondary*.png
# Border 12, label 17 pt bold uppercase #bdcbd3, button height 44). The textures live in the client (Client/Data/Game/Interface/Common,
# verified on this PC) and are named by their Common/ path in an inline page the way Clay Factoria (BrushLegend) and Alec's Tamework
# (CreditsPage) do. Font sizes are raised for the BIG readable rule (fits 1080). Left out on purpose (not proven in an inline page yet):
# FontName "Secondary" and the button Sounds.
VAN_HEAD = 'Background: (TexturePath: "Common/ContainerHeaderNoRunes.png", HorizontalBorder: 35, VerticalBorder: 0)'
VAN_PANEL = 'Background: (TexturePath: "Common/ContainerPatch.png", Border: 23)'
VAN_TITLE = "Style: (FontSize: 20, RenderBold: true, RenderUppercase: true, TextColor: #b4c8c9, HorizontalAlignment: Center, VerticalAlignment: Center)"
_VAN_BTN_LABEL = "LabelStyle: (FontSize: 17, TextColor: #bdcbd3, RenderBold: true, RenderUppercase: true, HorizontalAlignment: Center, VerticalAlignment: Center)"
VAN_BTN = ("Style: TextButtonStyle(Default: (Background: (TexturePath: \"Common/Buttons/Secondary.png\", Border: 12), %s), "
           "Hovered: (Background: (TexturePath: \"Common/Buttons/Secondary_Hovered.png\", Border: 12), %s), "
           "Pressed: (Background: (TexturePath: \"Common/Buttons/Secondary_Pressed.png\", Border: 12), %s));") % (_VAN_BTN_LABEL, _VAN_BTN_LABEL, _VAN_BTN_LABEL)
for _v in (VAN_HEAD, VAN_PANEL, VAN_TITLE, VAN_BTN):
    assert all(ord(ch) < 128 for ch in _v) and "{" not in _v and "}" not in _v
# every texture the page names exists in the client (read only)
_VAN_TEX = os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Client", "Data", "Game", "Interface")
if os.path.isdir(_VAN_TEX):
    for _t in ("Common/ContainerHeaderNoRunes", "Common/ContainerPatch", "Common/Buttons/Secondary", "Common/Buttons/Secondary_Hovered",
               "Common/Buttons/Secondary_Pressed"):
        assert os.path.exists(os.path.join(_VAN_TEX, *(_t + ".png").split("/"))) or os.path.exists(os.path.join(_VAN_TEX, *(_t + "@2x.png").split("/"))), \
            "vanilla texture %s not found under %s" % (_t, _VAN_TEX)
    print("overall page: vanilla textures found in %s" % _VAN_TEX)
else:
    print("overall page: client folder not found (%s) - vanilla texture paths not checked" % _VAN_TEX)
OVBARW = 600
opg.addField(CtField.make("public static final String HEAD = " + json.dumps(VAN_HEAD) + ";", opg))
opg.addField(CtField.make("public static final String PANEL = " + json.dumps(VAN_PANEL) + ";", opg))
opg.addField(CtField.make("public static final String TITLE = " + json.dumps(VAN_TITLE) + ";", opg))
opg.addField(CtField.make("public static final String BTN = " + json.dumps(VAN_BTN) + ";", opg))
opg.addConstructor(CtNewConstructor.make(f"""
public OverallPage({PR} pr) {{
  super(pr, {LIFE}.CanDismiss);
}}""", opg))
# a label in the page body; every dynamic text goes through b.set (safe for any character)
opg.addMethod(CtNewMethod.make(f"""
public static void line({UCB} b, String id, String text, String color, int size, boolean bold, boolean upper, boolean center, int h) {{
  b.appendInline("#SkyyOvBody", "Label #" + id + " {{ Anchor: (Height: " + h + "); Text: \\"\\"; Style: (FontSize: " + size + ", " + (bold ? "RenderBold: true, " : "") + (upper ? "RenderUppercase: true, " : "") + "TextColor: " + color + ", " + (center ? "HorizontalAlignment: Center, " : "") + "VerticalAlignment: Center); }}");
  b.set("#" + id + ".Text", text);
}}""", opg))
opg.addMethod(CtNewMethod.make(f"""
public static void wrapLine({UCB} b, String id, String text, String color, int size, int h) {{
  b.appendInline("#SkyyOvBody", "Label #" + id + " {{ Anchor: (Height: " + h + "); Text: \\"\\"; Style: (FontSize: " + size + ", TextColor: " + color + ", VerticalAlignment: Center, Wrap: true); }}");
  b.set("#" + id + ".Text", text);
}}""", opg))
opg.addMethod(CtNewMethod.make(f"""
public static void gap({UCB} b, int h) {{
  b.appendInline("#SkyyOvBody", "Label {{ Anchor: (Height: " + h + "); Text: \\"\\"; }}");
}}""", opg))
opg.addMethod(CtNewMethod.make(f"""
public static void sep({UCB} b) {{
  b.appendInline("#SkyyOvBody", "Group {{ Anchor: (Height: 1); Background: #2b3542; }}");
}}""", opg))
opg.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  int[] sc = {PKG}.Overall.sums(u, d);
  int lv = {PKG}.Overall.level(sc);
  int t = {PKG}.Overall.tenths(sc);
  boolean max = lv >= {PKG}.SkillDefs.MAX;
  int fill = max ? {OVBARW} : (t % 10) * ({OVBARW} / 10);
  if (fill < 0) fill = 0;
  if (fill > {OVBARW}) fill = {OVBARW};
  b.appendInline((String) null, "Group #SkyyOvPage {{ Anchor: (Width: 960, Height: 795); LayoutMode: Top; }}");
  b.appendInline("#SkyyOvPage", "Group #SkyyOvHead {{ Anchor: (Height: 44); LayoutMode: Top; Padding: (Top: 7); " + HEAD + "; }}");
  b.appendInline("#SkyyOvHead", "Label #SkyyOvHeadTxt {{ Anchor: (Height: 30); Text: \\"\\"; " + TITLE + "; }}");
  b.set("#SkyyOvHeadTxt.Text", "Overall Level");
  b.appendInline("#SkyyOvPage", "Group #SkyyOvBody {{ Anchor: (Height: 751); LayoutMode: Top; Padding: (Horizontal: 24, Top: 14, Bottom: 17); " + PANEL + "; }}");
  line(b, "SkyyOvTitle", "Level " + lv + " of " + {PKG}.SkillDefs.MAX, "#ffffff", 30, true, false, true, 48);
  String sub = max ? "Average of your skills " + {PKG}.Overall.avg(t) + " - the highest Overall Level" : "Average of your skills " + {PKG}.Overall.avg(t) + " - Overall Level " + (lv + 1) + " at an average of " + (lv + 1) + ".0";
  line(b, "SkyyOvSub", sub, "#96a9be", 18, false, false, true, 28);
  b.appendInline("#SkyyOvBody", "Group #SkyyOvBarRow {{ Anchor: (Height: 24); LayoutMode: Left; Padding: (Top: 3); }}");
  b.appendInline("#SkyyOvBarRow", "Label {{ Anchor: (Width: 156, Height: 18); Text: \\"\\"; }}");
  b.appendInline("#SkyyOvBarRow", "Group #SkyyOvBar {{ Anchor: (Width: {OVBARW}, Height: 18); Background: #1a2030; }}");
  if (fill > 0) b.appendInline("#SkyyOvBar", "Group {{ Anchor: (Left: 0, Top: 0, Width: " + fill + ", Height: 18); Background: #aa7c4a; }}");
  gap(b, 12);
  sep(b);
  gap(b, 10);
  line(b, "SkyyOvSkHd", "Skills that count (" + sc[1] + ")", "#96a9be", 18, true, true, false, 32);
  wrapLine(b, "SkyyOvSk", {PKG}.Overall.listText(u, d), "#ffffff", 17, 60);
  gap(b, 10);
  sep(b);
  gap(b, 10);
  line(b, "SkyyOvNowHd", "Boosts right now", "#96a9be", 18, true, true, false, 32);
  java.util.ArrayList now = {PKG}.Overall.nowLines(u, lv);
  for (int i = 0; i < now.size() && i < 3; i++) line(b, "SkyyOvNow" + i, "   " + (String) now.get(i), "#ffffff", 18, false, false, false, 28);
  gap(b, 10);
  if (max) line(b, "SkyyOvNextHd", "Max Overall Level reached", "#E8A93B", 18, true, true, false, 32);
  else {{
    line(b, "SkyyOvNextHd", "Overall Level " + (lv + 1) + " adds", "#96a9be", 18, true, true, false, 32);
    java.util.ArrayList nx = {PKG}.Overall.nextLines(lv);
    for (int i = 0; i < nx.size() && i < 2; i++) line(b, "SkyyOvNext" + i, "   " + (String) nx.get(i), "#bfcdd5", 18, false, false, false, 28);
  }}
  gap(b, 12);
  sep(b);
  gap(b, 8);
  wrapLine(b, "SkyyOvHow", "The Overall Level is the average of the skills above, rounded down - level any of them to raise it. Other classes' skills never count (a new class is a new profile).", "#878e9c", 15, 48);
  b.appendInline("#SkyyOvBody", "Group #SkyyOvNav {{ Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 12); }}");
  b.appendInline("#SkyyOvNav", "Label {{ Anchor: (Width: 358, Height: 44); Text: \\"\\"; }}");
  b.appendInline("#SkyyOvNav", "TextButton #SkyyOvBack {{ Anchor: (Width: 195, Height: 44); Text: \\"Back\\"; " + BTN + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyOvBack", {EVD}.of("a", "ovback"));
}}""", opg))
opg.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    if (data.indexOf("ovback\\"") >= 0) {{
      {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
      if (p != null) p.getPageManager().openCustomPage(ref, st, new {PKG}.SkillsPage(this.playerRef));
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("overall page event failed: " + t); }}
}}""", opg))
''')
rep('''public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
      if (data.indexOf("skstat" + i + "\\\\"") >= 0) {{''', '''public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    if (data.indexOf("skstatov\\\\"") >= 0) {{
      {PLA} po = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
      if (po != null) po.getPageManager().openCustomPage(ref, st, new {PKG}.OverallPage(this.playerRef));
      return;
    }}
    for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
      if (data.indexOf("skstat" + i + "\\\\"") >= 0) {{''')

# ================================================================ /skills stats overall (spec 4.7)
rep('''    int s = {PKG}.SkillClass.argSlot(pr, String.valueOf(ctx.get(this.skillArg)));
    if (s < 0) return;
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.StatsPage(pr, s));''', '''    String arg = String.valueOf(ctx.get(this.skillArg)).trim();
    if (arg.equalsIgnoreCase("overall")) {{
      {PLA} po = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
      if (po != null) po.getPageManager().openCustomPage(ref, store, new {PKG}.OverallPage(pr));
      return;
    }}
    int s = {PKG}.SkillClass.argSlot(pr, arg);
    if (s < 0) return;
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.StatsPage(pr, s));''')
rep('''  super("stats", "Open the Stats page of a skill: /skills stats mining");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | sorcery | fury | divinity | assassination | shaman", {ATY}.STRING);''',
    '''  super("stats", "Open the Stats page of a skill: /skills stats mining (or /skills stats overall)");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | sorcery | fury | divinity | assassination | shaman | overall (the Overall Level page)", {ATY}.STRING);''')
rep('''fury, divinity, assassination, shaman."));''', '''fury, divinity, assassination, shaman. /skills stats also opens overall."));''')

# ================================================================ Server Setup rows (spec 4.9 + the crossbow / Divinity rows)
rep('''            ("acrobatics", "Acrobatics"), ("perks", "Perks"), ("crafting", "Crafting")]''',
    '''            ("acrobatics", "Acrobatics"), ("perks", "Perks"), ("overall", "Overall and Mana"), ("crafting", "Crafting")]''')
rep('''    ("perk.archery.keepLoaded.enabled", "Crossbows stay loaded", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: a crossbow unloads when you switch slots, as in vanilla (its bolts come back as arrows).", "reload"),
''', '''    ("perk.archery.keepLoaded.enabled", "Crossbows stay loaded", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: a crossbow unloads when you switch slots, as in vanilla (its bolts come back as arrows).", "reload"),
    # 0.4.6 (research/Overall-Level-Spec.md 4.9): part switch = bool + live,part,danger; asks only when switched OFF
    ("mana.base.enabled", "Base Mana", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: no base Mana from Skills (vanilla max Mana is 0). Alchemy and Overall Level Mana stay.", "reload"),
    ("overall.enabled", "Overall Level Health and Mana", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: the Overall Level adds no max Health or Mana. It is still shown on /skills.", "reload"),
''')
rep('''    ("divinity.healXpPerHp", "Divinity XP per HP healed", "combat", "dec", "0.2", "0", "100", "", "", "live",
     "XP per 1 HP a Priest heals on OTHER party members (healing themself pays nothing).", "reload"),
''', '''    ("divinity.healXpPerHp", "Divinity XP per HP healed", "combat", "dec", "0.2", "0", "100", "", "", "live",
     "XP per 1 HP a Priest heals on OTHER party members (healing themself: the next row).", "reload"),
    # 0.4.6 (LOCKED Skyy 2026-09-25): self-heals pay their own rate, inside the same per-minute cap
    ("divinity.healXpPerHpSelf", "Divinity XP per HP healed on self", "combat", "dec", "0.25", "0", "100", "", "", "live",
     "XP per 1 HP a Priest heals on themself (locked default 0.25). Counts against the cap below too.", "reload"),
''')
rep('''        CFG_ROWS.append(("perk.archery.keepLoaded.debug", "Stay-loaded debug lines", "perks", "bool", "false", "", "", "", "", "live,adv",
                         "On: admins see a chat line each time a crossbow load is kept or put back (for testing).", "reload"))
''', '''        CFG_ROWS.append(("perk.archery.keepLoaded.debug", "Stay-loaded debug lines", "perks", "bool", "false", "", "", "", "", "live,adv",
                         "On: admins see a chat line each time a crossbow load is kept or put back (for testing).", "reload"))
        # 0.4.6 (LOCKED Skyy 2026-09-25): the big-arrow meter, the load sound and the chat hint (each player can turn them off in /settings)
        CFG_ROWS.append(("perk.archery.keepLoaded.meter", "Stay-loaded keeps the big-arrow meter", "perks", "bool", "true", "", "", "", "", "live",
                         "On: the big-arrow (Signature) meter comes back with the bolts. Players can turn it off in /settings.", "reload"))
        CFG_ROWS.append(("perk.archery.keepLoaded.sound", "Sound when the bolts go back in", "perks", "text", XBOW_SOUND_DEF, "", "120", "", "",
                         "live,adv", "A sound event id (default: the vanilla crossbow load). Empty = no sound.",
                         "reload;check=XbowCfg.checkSound"))
        CFG_ROWS.append(("perk.archery.keepLoaded.hint", "Chat hint when the bolts go back in", "perks", "bool", "true", "", "", "", "", "live",
                         "'Crossbow reloaded - 6 bolts back in'. Players can turn it off in /settings.", "reload"))
''')
rep('''CFG_ROWS += [
    # ---- crafting: alchemy + smithing''', '''# 0.4.6 (research/Overall-Level-Spec.md 4.9): the "Overall and Mana" category
CFG_ROWS += [
    ("mana.base", "Base Mana for everyone", "overall", "dec", "10", "0", "10000", "", "", "live",
     "Max Mana every player starts with (vanilla gives 0).", "reload"),
    ("mana.magicBase", "Base Mana for magic users", "overall", "dec", "20", "0", "10000", "", "", "live",
     "Replaces the base above for the classes below: their base is this, not base + this.", "reload"),
    ("mana.magicClasses", "Magic user classes", "overall", "text", "Mage,Priest", "", "200", "", "", "live",
     "Class names, comma separated (Mage, Priest, Archer, Warrior, Berserker, Assassin, Shaman).", "reload;check=OverallCfg.checkClasses"),
    ("overall.skills", "Skills in the Overall Level", "overall", "text", OVL_SKILLS_DEF, "", "300", "", "", "live",
     "Comma list. Class = the profile's own class skill; other classes' skills never count.", "reload;check=OverallCfg.checkSkills"),
    ("overall.healthPerLevel", "Max Health per Overall Level", "overall", "dec", "0.5", "0", "100", "", "", "live",
     "Placeholder. 0.5 = +50 max Health at Overall Level 100.", "reload"),
    ("overall.manaPerLevel", "Max Mana per Overall Level", "overall", "dec", "0.2", "0", "100", "", "", "live",
     "Placeholder. 0.2 = +20 max Mana at Overall Level 100.", "reload"),
    ("overall.healOnLevelUp", "Fill the new Health on level up", "overall", "bool", "true", "", "", "", "", "live,adv",
     "On: an Overall level up also heals the max Health it added (players have no Health regen).", "reload"),
    ("overall.chat", "Overall level-up chat line", "overall", "bool", "true", "", "", "", "", "live",
     "Off: nobody gets the line. On: each player can still hide theirs in /settings.", "reload"),
]
CFG_ROWS += [
    # ---- crafting: alchemy + smithing''')
rep('''assert len(CFG_ROWS) == 159, "0.4.4 had 154 rows + 5 crossbows-stay-loaded rows (Crossbow-Loaded-Spec 3.9), got %d" % len(CFG_ROWS)   # 0.4.5''',
    '''assert len(CFG_ROWS) == 173, ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows (Overall-Level-Spec 4.9) + divinity.healXpPerHpSelf + "
                              "3 crossbow extras (meter, sound, hint), got %d" % len(CFG_ROWS))   # 0.4.6''')
rep('''for _k in ("divinity.healXp.enabled", "divinity.healXpPerHp", "divinity.healXpMaxPerMinute"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp, _k
''', '''for _k in ("divinity.healXp.enabled", "divinity.healXpPerHp", "divinity.healXpMaxPerMinute"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp, _k
# 0.4.6: every new key once in CFG_ROWS, in the default file and in its own appended block (so an old file gets it too)
for _k in ("mana.base.enabled", "mana.base", "mana.magicBase", "mana.magicClasses", "overall.enabled", "overall.skills", "overall.healthPerLevel",
           "overall.manaPerLevel", "overall.healOnLevelUp", "overall.chat"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp and ("\\n" + _k + "=") in ("\\n" + OVL_DEFAULTS), _k
assert sum(1 for _r in CFG_ROWS if _r[0] == "divinity.healXpPerHpSelf") == 1 and "divinity.healXpPerHpSelf" in _dp \\
    and "\\ndivinity.healXpPerHpSelf=" in "\\n" + DIVS_DEFAULTS and "\\ndivinity.healXpPerHpSelf=" not in "\\n" + DIV_DEFAULTS
for _k in ("perk.archery.keepLoaded.meter", "perk.archery.keepLoaded.sound", "perk.archery.keepLoaded.hint"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp and ("\\n" + _k + "=") in ("\\n" + XBOWX_DEFAULTS) \\
        and ("\\n" + _k + "=") not in ("\\n" + XBOW_DEFAULTS), _k
# the appended blocks never share a key with each other or with the blocks appended before them (DIV_L, XBOW_L)
_blk = {}
for _nm, _txt in (("DIV", DIV_DEFAULTS), ("DIVS", DIVS_DEFAULTS), ("XBOW", XBOW_DEFAULTS), ("XBOWX", XBOWX_DEFAULTS), ("OVL", OVL_DEFAULTS)):
    for _ln in _txt.split("\\n"):
        if _ln and not _ln.startswith("#") and "=" in _ln:
            _kk = _ln.split("=", 1)[0]
            assert _kk not in _blk, "%s in both %s and %s" % (_kk, _blk.get(_kk), _nm)
            _blk[_kk] = _nm
# the Overall skill list default = LABELS of slots 0, 1, 2, 4, 10, 11, 12, 13 + Class, exactly the OverallCfg.SLOTS default
_ovt = OVL_SKILLS_DEF.split(",")
assert _ovt[-1] == "Class" and [SLOT_LABELS.index(_x) for _x in _ovt[:-1]] == [0, 1, 2, 4, 10, 11, 12, 13], _ovt
assert all(_c in [_r[0] for _r in CLASS_ROWS] for _c in "Mage,Priest".split(","))
''')
rep('''FILES=["Skyy_SkyySkills/xp.properties"], RELOAD="SkillKit.reload", KEEP=20,''',
    '''FILES=["Skyy_SkyySkills/xp.properties"], RELOAD="SkillKit.reload", KEEP=10,''')

# ================================================================ setup / shutdown / texts (spec 4.10 / 4.11)
rep('''  {PKG}.SkillStore.bridge().put("skill:fn:healxp", new {PKG}.SkillHealFn());
''', '''  {PKG}.SkillStore.bridge().put("skill:fn:healxp", new {PKG}.SkillHealFn());
  {PKG}.SkillStore.bridge().put("skill:fn:overall", new {PKG}.OverallFn());
''')
rep('''"; crossbows stay loaded at Archery " + {PKG}.XbowCfg.LEVEL + " (" + ({PKG}.XbowCfg.ON ? "on" : "off") + ")" + "; bridge skill:fn:addxp + skill:fn:craftxp + skill:fn:healxp; trees bridge on''',
    '''"; crossbows stay loaded " + {PKG}.XbowCfg.text() + "; overall level " + {PKG}.OverallCfg.text() + "; bridge skill:fn:addxp + skill:fn:craftxp + skill:fn:healxp (optional Boolean self) + skill:fn:overall + skill:overall:<uuid>; trees bridge on''')
rep('''  {PKG}.SkillStore.regSetting("rewards.late", "Late reward payouts", "coins", true, "Coins and XP paid later because another mod was not ready");
''', '''  {PKG}.SkillStore.regSetting("rewards.late", "Late reward payouts", "coins", true, "Coins and XP paid later because another mod was not ready");
  {PKG}.SkillStore.regSetting("skills.overallUp", "Overall Level ups", "skills", true, "OVERALL LEVEL UP 12 -> 13 with the max Health and Mana it added");
  {PKG}.SkillStore.regSetting("skills.xbowMeter", "Crossbows keep the big-arrow meter", "combat", true, "Your crossbow's big-arrow meter comes back with its bolts when you switch back to it");
  {PKG}.SkillStore.regSetting("skills.xbowSound", "Crossbow reload sound", "combat", true, "The crossbow load sound when your kept bolts go back in (Archery perk)");
  {PKG}.SkillStore.regSetting("skills.xbowHint", "Crossbow reload chat line", "combat", true, "Crossbow reloaded - 6 bolts back in - when your kept bolts return");
''')
rep('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:healxp"); }} catch (Throwable t) {{ }}
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:healxp"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:overall"); }} catch (Throwable t) {{ }}
''')
rep('''          fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft, skit, karm, dvc, hxp, hfn, xcf, xst, xbw, xss):''',
    '''          fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft, skit, karm, dvc, hxp, hfn, xcf, xst, xbw, xss, ovc, ovl, ofn, opg):''')
rep('''crossbows stay loaded from Archery 5 by default (the level is set in Server Setup; Archers keep their bolts across hotbar switches, paid with the arrows vanilla refunds).''',
    '''crossbows stay loaded from Archery 5 by default (the level is set in Server Setup; Archers keep their bolts and the big-arrow meter across hotbar switches and teleports, paid with the arrows vanilla refunds, with the load sound and a chat hint). Base Mana for every player (magic users more) and an Overall Level - the average of your skills - that adds max Health and Mana (Server Setup). Priests earn Divinity XP for healing others and themselves. Uninstall / downgrade: switch Base Mana and Overall Level off in Server Setup first.''')

# ================================================================ settings-key sanity (Settings-Spec 1.2: key format, label <= 40 / help <= 90)
import re as _re
for _key, _lab, _help in (("skills.overallUp", "Overall Level ups", "OVERALL LEVEL UP 12 -> 13 with the max Health and Mana it added"),
                          ("skills.xbowMeter", "Crossbows keep the big-arrow meter", "Your crossbow's big-arrow meter comes back with its bolts when you switch back to it"),
                          ("skills.xbowSound", "Crossbow reload sound", "The crossbow load sound when your kept bolts go back in (Archery perk)"),
                          ("skills.xbowHint", "Crossbow reload chat line", "Crossbow reloaded - 6 bolts back in - when your kept bolts return")):
    assert _re.match(r"^[a-z][A-Za-z0-9.]{2,47}$", _key) and len(_lab) <= 40 and len(_help) <= 90, (_key, len(_lab), len(_help))
    assert s.count('"%s"' % _key) >= 1

# ================================================================ final checks + write
assert s.count("registerSystem(") == REG0, "0.4.6 adds no system (one registerSystem per class)"
open(dst, "wb").write(s.replace("\n", NL).encode("utf8"))
print("wrote", dst, len(s), "chars")
