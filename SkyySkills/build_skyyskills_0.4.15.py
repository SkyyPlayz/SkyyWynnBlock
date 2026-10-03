"""SkyySkills 0.4.15 - build script (derived from the generated 0.4.14 by tools/skills_0_4_15_patch.py - edit the patch, not this file;
0.4.14 was derived from the generated 0.4.13 by tools/skills_0_4_14_patch.py; 0.4.13 was derived from the generated 0.4.12 by tools/skills_0_4_13_patch.py; 0.4.12 was derived from the generated 0.4.11 by tools/skills_0_4_12_patch.py; 0.4.11 was derived from the generated 0.4.10 by tools/skills_0_4_11_patch.py; 0.4.10 was derived from the generated 0.4.9 by tools/skills_0_4_10_patch.py; 0.4.9 was derived from the generated 0.4.8 by tools/skills_0_4_9_patch.py; 0.4.8 was derived from the generated 0.4.7 by tools/skills_0_4_8_patch.py; 0.4.7 was derived from the generated 0.4.6 by tools/skills_0_4_7_patch.py; 0.4.6 was derived from the EDITED 0.4.5 by tools/skills_0_4_6_patch.py; 0.4.5 was derived from 0.4.4 by tools/skills_0_4_5_patch.py and then edited by Skyy in commit ab75b6c - never re-run that patch;
0.4.4 was derived from 0.4.3 by tools/skills_0_4_4_patch.py, 0.4.3 from 0.4.2 by tools/skills_0_4_3_patch.py, 0.4.2 from 0.4.1 by
tools/skills_0_4_2_patch.py, 0.4.1 from 0.4 by tools/skills_0_4_1_patch.py, 0.4 from 0.3.2 by tools/skills_0_4_patch.py, 0.3.2 from 0.3.1
by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.15: MAX MANA PER CLASS LEVEL + THE STAFF HANDOVER (Skyy 2026-10-03; research/SkyyArmory-Spec.md section 15; full notes in
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
0.4.14: SKYY'S LOCKS OF 2026-10-02 (OPEN-QUESTIONS Q&A; full notes in tools/skills_0_4_14_patch.py).
  KILL XP BY MOB LEVEL: kill XP (max health x combat.perHealth, kept between combat.min / combat.max, x the class skill XP multiplier) x
     (1 + combat.levelBonus x (mob level - 1)) x the level gap against your class skill (more than combat.gap.free levels above: +gap.above
     a level, at most x gap.max = +250%; below: -gap.below a level, at least x gap.min). Mob level = SkyyMobs mob:fn:level; no level = the
     0.4.13 XP exactly. Party members use their own class skill for the gap. Lv 33 Skeleton_Scout (178 HP) at Divinity 11 = ~520 XP.
  ROLL LANDINGS: RollSys (before the engine's FallDamagePlayers, reading the same PlayerInput queue) notes a landing whose roll engaged
     (MovementStates.rolling, speed between MinFallSpeedToEngageRoll and MaxFallSpeedToEngageRoll); it pays the UNREDUCED fall XP x (1 +
     acro.rollBonus) 0.4 s later (alive, not in water), inside acro.fallXpMax / acro.fallMaxXpPerMinute. A full roll paid 0 before.
     Only in a world with fall damage on (WorldConfig.isFallDamageEnabled - the engine skips every landing of the others).
  GATHERING PACE: earned Mining / Foraging / Farming XP x gather.boost.early (3) up to level gather.boost.earlyUntil (10), easing in a
     straight line to x gather.boost.late (1.5) at gather.boost.lateFrom (20), x1.5 after - before the tree Wisdom bonus; grants from
     other mods stay exact. Shown on the Stats page.
  SICKLE SWINGS: InteractivelyPickupItemEvent (SickleSys) with a sickle in hand, outside an F-harvest window and an F-pickup: one Farming
     award + one double-drop roll per RIPE crop - the StageFinal state of a crop with growth states, like an F-harvest (each crop's produce
     item starts it; a pickup has no position, so plants without growth states pay through breaking only). SickleTask pays on the world
     thread. No skill:on:gather for sickle swings (its listeners need the crop block and position).
  FIXES: the stale "never while charging" xp.properties comment (DocMig, once, History first); the Stats line "Bonuses (trees + tools)".
  FIX ROUND (reviews 2026-10-03): sickle swings pay StageFinal crops only (a placed stateless plant that hands back its own item looped XP
     and double drops); RollSys only where fall damage is on; the party texts (each member's own class skill level); gather.boost.early /
     late at least 0.1.
  New keys reach an existing xp.properties through one appended block (only the lines it lacks). CHECKED in a bare JVM
  (SkyySkills/test_skyyskills_0.4.14.py, -Xverify:all, scratch under tools/dev/scratch deleted afterwards).
0.4.13: THE COMBAT STATE ON THE BRIDGE for the SkyyHud 0.3.12 Combat widget (Skyy 2026-10-02; full notes in tools/skills_0_4_13_patch.py).
  skill:fn:combat (CombatFn): apply(UUID) -> Long ms left in combat (0 = out of combat); apply("window") -> Long the whole window in ms
  (vanilla 6000; 0 until somebody was in combat since the start). In combat = EXACTLY the in-combat test of the Mana regen above: a
  NoDamageTaken condition of a positive Additive Mana regen entry fails on the world's clock (6 s after TAKING damage), read on the world
  thread at the Mana regen's own 0.2 s pulse (ManaRegen.tick -> combat, before any of its returns); the countdown = the condition's Delay
  (asked from the condition itself: the field is protected) minus the time since the last hit; between pulses it counts down on the wall
  clock and never reaches 0 before the next pulse says so. Memory only, any thread.
  FIX ROUND before the first deploy (cross-check 2026-10-02 NOT READY; the version stays 0.4.13):
  F1 every world keeps its own clock (TimeResource "Now", saved per world: live default ~09:12, islands 03:13 - 08:24) and the player's
     hit / combat / charge stamps (DamageDataComponent) travelled to the next world unchanged: a smaller clock kept you in combat (and
     "charging") for hours, a bigger one cleared combat at once. Now every Mana regen pulse records the world, its clock, the stamps and
     System.nanoTime() (ManaRegen.CARRY); the first pulse in another world rewrites a stamp that is still the old world's (the same
     Instant, or a hit there after its last pulse) to now - the REAL time since it (old clock time / old dilation + the wall time since
     that pulse, x this world's dilation: a world's clock = real time x its time dilation - TickingThread / World.tick / TimeSystem
     bytecode, asserted below); over 1 hour = Instant.MIN (never hit); a fresh hit in the new world is left alone; a stamp in the future
     of the world's clock = now.
  F2 Acro.retainOnline prunes ManaRegen.CMB (and CARRY) like CLK.
  MANA WHILE CHARGING (Skyy 2026-10-02, LOCKED): vanilla's Mana entry pauses while Charging; when the only failing conditions are an
     inverse Charging (out of combat) or Charging + NoDamageTaken (in combat), SkyySkills refills what vanilla withholds: the whole
     out-of-combat rate (vanilla's +1 / 0.2 s + the same boosts) or the in-combat rate. Never while dead, never on top of vanilla's own
     refill; /skills mana says "charging - Mana still regenerates".
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.13.py, -Xverify:all, scratch under tools/dev/scratch deleted afterwards).
0.4.12: THE CLASS SKILL CURVE + MANA REGEN IN COMBAT (Skyy's Q&A 2026-10-02 rounds 1-2; full notes in tools/skills_0_4_12_patch.py).
  CLASS SKILLS level on their OWN table (research/cloud/Class-Skill-Curve-Proposal.md, approved as written): XP for level L = 50 x L +
  0.25 x L^3 rounded (10 / 50 / 500 / 5,000 steps, half to even) = the proposal's section 5 table, asserted here (20 at 21,540 XP, 40 at
  209,090, 100 at 6,627,590; 0.4.11: 522,425 / 25.5m / 637.7m). Every level comes from SkillDefs.levelOf(slot, total) (+ intoLevel /
  needFor / progress / maxOf per slot) - the one global lookup is gone. Class level = max(general table, class table) up to the class max
  (levels only go up; the default class table is at or below the general one at every level). Rows (Levels tab): levels.class (list),
  levels.class.scale (%), levels.class.max (1-100), levels.class.sameAsOthers (off). Gathering and every other skill keep their table.
  Existing XP is kept: the first 0.4.12 start records once (class-curve.properties) which profiles' class levels rose; each gets one
  "Class skill curve updated" chat line + the level-up coins of the gained levels (paid marker = exactly once) the next time it plays.
  MANA REGEN IN COMBAT (rounds 1-2): vanilla refills 0 for 6 s after taking damage; SkyySkills now refills Mana there at mana.regen.inCombat
  % (Server Setup "In-combat Mana regen", default 50, 0 = vanilla) of (vanilla rate + Mana Regen boosts); out of combat it adds the boost
  part (vanilla rate x Mana Regen %) on top of vanilla. Never above max Mana, never while charging, nothing without Mana. Boosts are
  percents other mods register per player on skill:fn:manaregen (nothing registers yet); see them in Server Setup ("Mana Regen: show
  mine") or with the admin /skills mana.
  CHECKED in a bare JVM (SkyySkills/test_skyyskills_0.4.12.py, -Xverify:all, scratch under tools/dev/scratch/skills0412 deleted afterwards):
  the table = the proposal, per-slot levels everywhere (pages, bridge, rewards, Overall), the guard, ClassCurve on copies of the live data
  (nobody to tell on Skyy's world; edited copies: told + paid once, start twice = once), the Mana regen maths on real engine conditions, the
  bridge, the loader, the rows, class bytes vs 0.4.11. UNVERIFIED (needs the game): the in-combat refill feel, /skills mana, the notice line.
  REVIEW FIXES: the Overall page without counted skills is not "max"; the Mana refill runs first in AcroSys.tick (no other call can skip
  it); the "Mana Regen: show mine" answer fits SkyyMenu's one-line status (<= 110 characters); the class curve size message shows the
  effective class totals; skill:<uuid> is republished within 5 s after any live curve change (SkillStore.republishAll).
0.4.11: PRIEST HEAL XP IS THE XP THE PLAYER GETS (Skyy 2026-10-01: "make healing others give 1xp per hp, and self gives 1.25 xp per hp
  healed."; full notes in tools/skills_0_4_11_patch.py). The three heal rows are the FINAL heal XP - healing no longer goes through the
  class skill XP multiplier: divinity.healXpPerHp 0.2 -> 1, divinity.healXpPerHpSelf 0.25 -> 1.25, divinity.healXpMaxPerMinute 300 -> 900
  (what a Priest gets at the defaults, any class skill XP multiplier). BridgeXp.paidX / offerX (cls switch; paid / offer = cls true, the
  0.4.10 maths for grants / crafting); HealXp.offer -> offerX(..., false). Kills, the party share and grants keep the class skill XP
  multiplier. The Divinity Stats line: "Healing pays 1 Divinity XP per HP on others, 1.25 on yourself (max 900 a minute)" (effective
  numbers only when the general XP multiplier is not 1). Row help / default comments say healing is not multiplied. One-time update of
  an existing xp.properties (HealMig.run before SkillCfg.load): untouched 0.2 / 0.25 / 300 lines -> 1 / 1.25 / 900, an admin's values
  kept and logged, the 0.4.10 default comment lines rewritten (exact matches), History version first (verified), one change-log line
  per key (Undo), marker comment = runs once, ISO-8859-1 / CRLF byte-safe.
0.4.10: CLASS SKILL XP MULTIPLIER (Skyy 2026-10-01: "increase the class skill xp you get by a good bit, it levels slower than everything
  else."; full notes in tools/skills_0_4_10_patch.py). ONE new Server Setup row, Combat tab: "Class skill XP multiplier" =
  classSkill.xpMultiplier (dec 0-100, default 3, live; appended once to an xp.properties without it, nothing else in the file changes).
  ONE helper, SkillCfg.classXp(slot, xp), multiplies every XP gain into a class skill (SkillDefs.isClass: Archery, Swordsmanship,
  Assassination, Shaman skill, Sorcery, Fury, Divinity; a fraction is paid by chance): kills (KillSys - AFTER combat.min / combat.max /
  combat.role / combat.default and the xp multiplier, so every kill pays exactly 3 x, a 500 XP kill 1,500; before the tree bonus), the
  party share (a fraction of that same kill XP - multiplied once) and every bridge award into a class skill (BridgeXp.paid inside
  BridgeXp.offer: Priest heal XP on others and on yourself, skill:fn:addxp grants if an admin lists a class skill; before the tree bonus
  and bridge.maxXpPerMinute). divinity.healXpMaxPerMinute keeps counting the BASE heal XP (Skyy's lock "cap stays 300 a minute", counted
  before the xp multiplier): it limits the healing, so a capped Priest earns 900 a minute at x3. Not multiplied: gathering, Acrobatics,
  Alchemy, Smithing, Cooking, Exploration, the admin /skills xp (raw), the legacy Combat move. Shown in SkillCfg.load's text (ready line,
  /skills reload), the class how-to line of the Stats page and the Divinity heal line (effective rates). Row help of multiplier /
  combat.max / divinity.healXpMaxPerMinute says where they sit.
0.4.9: EVERY CAST CHECKS WHAT IT SPENDS (Skyy 2026-09-30 play test of 0.4.8: "the wand spell only costs 5 mana. but you still have to be
  above 25 mana to actually cast it."; full notes in tools/skills_0_4_9_patch.py, research/Mana-Cost-And-Regen-Research.md). The Mana CHECK of
  a charged cast is the StatsCondition interaction the weapon's Charging step names (the engine resolves that name in the global interaction
  assets; an item's InteractionVars are read only by a Replace naming the var), so the item vars 0.4.8 cut were dead data. This jar now
  also carries GENERATED overrides of those interactions (Assets.zip read in memory at every build, never checked into git):
    Wand_Cast_Left_Charged 25 -> 5, Spellbook_Cast_Hurl_Charged 25 -> 20, Gun_Shoot_Flintlock_Charged 50 -> 10, Staff_Cast_Summon_Charged
    no check (Simple: staffs cast for free at 0 Mana) -> a StatsCondition checking 10; the default drains Wand / Staff / Spellbook_Cast_Cost
    -25 -> -5 and Gun_Shoot_Cost -75 -> -15. The check number = the one number the items behind it spend (so it cannot drift). Crystal_Red
    and Crystal_Ice spend 0 but now need 10 Mana present (they sit behind the staff check), and so does the plain Weapon_Gun_Blunderbuss
    (behind the flintlock check; vanilla needed 50). Self-checked (SPELL GEN): only that number
    changes, the eight ids / shapes, no Mana number anywhere else in the interactions, nothing outside Server/Item names them (mobs keep
    their attacks), no clash with another Skyy mod or pack mod, and a GATE SIMULATION of every item on vanilla and on the final assets
    (every spend behind a check, check = spend = vanilla spend / 5). The 32 item overrides of 0.4.8 stay as they were.
  GUARD: ManaCost holds the REAL check and spend per item (34 items, from the simulation); ManaGuard compares base Mana with the real check.
    Pack check: also which pack the game's interaction assets take the 8 overrides from + the live Mana check of each cast check (the
    engine's resolved costs entry, what the gate compares).
  Mana regen unchanged (vanilla +1 every 0.2 s after 6 s without damage, not while charging).
0.4.8: MAGIC THAT WORKS AT LEVEL 1 (Skyy 2026-09-30; full notes in tools/skills_0_4_8_patch.py). Found in game: vanilla casters cost Mana
  per charged cast (wands 25, staffs 50, spellbooks 100, Halloween_Broomstick 50, blunderbusses 50) while 0.4.7 gave 10 (Mage / Priest 20).
  Skyy: "make priest start at like 30 mana. (they need at least enough mana to use the starter weapon.)" + "lets also take your
  recommendation 1" (spell costs / 5) + "so at level 1 when you start, you can get a few shots off with your magic".
  SPELL COSTS / 5: this jar is now an asset pack (IncludesAssetPack true) carrying GENERATED overrides of the vanilla items whose
    InteractionVars cost Mana (read from Assets.zip in memory at every build, never checked into git): only the cast check Costs.Mana and
    the drain StatModifiers.Mana change (/ SPELL_DIVISOR 5, rounded half up, at least 1, 0 stays 0): wand 25 -> 5, staff 50 -> 10,
    spellbook 100 -> 20, broomstick / blunderbuss 50 -> 10 (the plain blunderbuss drains 0 in vanilla and still does). Self-checked
    (SPELL GEN block): the one known var shape, JSON = vanilla except those numbers, item Parent rules, no vanilla default cost reachable
    without the item's own override, no clash with another Skyy mod of the live set or a pack mod. Items with only 0 costs are left alone.
    The divisor is fixed in the jar: Server Setup shows it read-only ("Spell Mana costs divided by"). Known limit: an override is a full
    copy of the item, so after a Hytale update that changes one of these items, rebuild SkyySkills (the build re-derives them).
  BASE MANA BY CLASS: config table mana.classBase (Server Setup > Skills > Overall and Mana > "Base Mana by class"; default Mage 30,
    Priest 30) replaces mana.magicBase + mana.magicClasses; other classes (and no class) start at mana.base 10. ManaMig.run (setup, before
    the file is read): the untouched 0.4.7 pair (20 + Mage,Priest) becomes the default table, an admin's pair is kept as the table (INFO);
    only those lines change (plus the untouched 0.4.7 comment about them, which becomes the 0.4.8 one; another comment naming the old
    keys gets a note), byte-safe, atomic (the kit's CfgRows.atomicWrite), once (the old lines are gone afterwards); the file as it
    was goes into the kit's History (restorable in Server Setup). If the move cannot run, the old pair is read as the table (WARN) and
    the next start retries.
  GUARD: ManaGuard WARNs once per class whose base Mana is below its kit weapon's (new) Mana cost (kit from SkyyClasses via config:fn:
    SkyyClasses, else the built-in table; nothing to check while SkyyClasses' Class kits are off) + one INFO summary with the casts from
    full Mana; it never changes a number. Pack check: one INFO when the game's item assets take every override from this jar's pack,
    else one WARN naming the items another pack wins (the pack loaded last wins a clash).
  Max Mana: the same Perks.tick modifier as 0.4.6 (world thread); current Mana is never written (no refill on a switch, the session hold
    keeps a relog from dipping it).
0.4.7: THE VANILLA LOOK for /skills (+ Top 10), the Stats page and the Overall page (Skyy 2026-09-28: "the new goal for any and all UI
  added in the game is for them to look and feel vanilla"; research/Vanilla-UI-Style-Guide.md; full notes in tools/skills_0_4_7_patch.py).
  ONLY THE LOOK CHANGED:
  - the pages are built from the shared kit tools/skyyui.py when this script runs (SUI.verify() first proves every style value,
    texture and sound against Assets.zip, read-only); the kit id is in the ready log line.
  - one look for the Skills family: the vanilla plain window (title bar + ContainerPatch body), wells for lists and info boxes, vanilla
    list rows, the vanilla progress track, Secondary buttons (Back with the cancel sound), footers right-aligned. /skills 960 x 786,
    Stats 960 x 848, Overall 960 x 689; skill colours stay on the skill name and the XP bar. Top 10 = a RANK / PLAYER / LEVEL / XP table.
  - every element id of 0.4.6, every event binding + EventData (skstatov, sktree<slot>, skstat<slot>, skback, stback, sttop, sttree,
    ovback), every text (the same Java expressions; b.set, so commas show again), the leaderboard data, the Overall / class-row / legacy
    / max-level rules and every handleDataEvent are 0.4.6's; nothing else in the jar changed (commands, config, files, bridge keys).
  - review fixes: the boost lines shrink to fit their well (vanilla ShrinkTextToFit, 15 px floor) instead of running past its edge;
    the /skills rows (SkillDefs.ROW_SLOTS / ACROBATICS) and the list-well height budget come from ONE Python list (SKILL_ROW_SLOTS).
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
0.4.5: Crossbows stay loaded (research/Crossbow-Loaded-Spec.md) - the ARCHERY LEVEL-5 REWARD (Skyy's ask 2026-09-25: "the crossbow should
  stay loaded when you scroll off it and scroll back"). Everything 0.4.4 does is unchanged; no saved data changes (0.4.4 <-> 0.4.5 both
  ways is safe: nothing is written to players/<pkey>.properties, only 5 perk.archery.keepLoaded.* lines to xp.properties).
  WHAT VANILLA DOES (spec 1, VERIFIED): "loaded" is the player's Ammo stat (0-6, EntityStatMap), never item data. Scrolling AWAY from a
    loaded crossbow runs its SwapFrom ladder: Adventure only, it refunds min(Ammo, 6) Crude Arrows and does NOT spend Ammo. Scrolling ONTO
    any crossbow queues a clear of Ammo that the next EntityStatsSystems$Recalculate pass applies (cap 6, value 0). So you never lose
    arrows, but you always reload.
  WHO (spec 2.2): an Archer (SkillClass.slot = slotOfClass("Archer") and SkillClass.consistent) whose Archery level on the ACTIVE profile is
    at least perk.archery.keepLoaded.level (5; 0 = every Archer), perk.archery.keepLoaded.enabled on, profile:busy not set, and a crossbow
    whose id starts with an entry of perk.archery.keepLoaded.items (Weapon_Crossbow_ = Iron, Ancient Steel + More Crossbow Tiers) that
    SkyyClasses allows (class:fn:allowed). Nothing new is saved: the flag is computed from the profile's own Archery level and cached per
    UUID (Xbow.ON), refreshed every second (Perks.tick), right after a level up (SkillXp.gain4) and after a profile switch
    (Perks.switched). The cache only decides when to remember and arm; it NEVER decides a payout.
  HOW (spec 2.3-2.5): XbowSlotSys (EntityEventSystem on InventorySetActiveSlotEvent, section -1 = hotbar, Player query; the event is
    dispatched synchronously inside setActiveSlot, so Ammo still equals the refund there). Leaving a crossbow slot that was held for at
    least delayTicks: remember k = min(Ammo, cap, 6) and the exact stack (per hotbar slot, 16 slots). Arriving at a slot whose kept stack
    is still there (ItemStack.isEquivalentType = same id + metadata): arm a restore. Xbow.tick (inside AcroSys, EVERY tick, before its
    1 s gate) lands it delayTicks (3, about 0.1 s) of its own ticks later, after vanilla's wipe: active slot + stack re-checked, waits for
    the Ammo cap (gives up after 60 ticks), target = min(kept, cap), need = target - current (a vanilla reload in the gap is never paid
    twice), live eligibility re-checked UNCACHED (Xbow.eligibleNow), then Crude Arrows are taken from hotbar + storage + backpack with
    vanilla's own call (getCombined(HOTBAR_STORAGE_BACKPACK).removeItemStack(stack, true, true), all or nothing) and re-counted, and only
    then Ammo is set to current + paid. Creative: free only when both the leave and the return were in Creative (vanilla loads free there
    and refunds nothing). Every entry is cleared after the attempt, whatever the outcome.
  ANTI-DUPE (spec 2.6): vanilla refund on leave + our payment on return = net zero; pay first, set second (a failure never gives a bolt);
    no item data is ever written (a dropped / traded / stored / sold crossbow carries nothing); rapid scrolling cancels the armed restore
    and keeps the count (never re-read); a leave within delayTicks of arriving is never recorded (Ammo may still be the previous
    crossbow's). PER-TICK EPOCH CHECK (review 7.4): each XbowState keeps the profile:epoch it was built under (Perks.epoch, one bridge
    read); a different live value wipes it on the next slot event or tick, before any payment (the 1 s Perks.switched is not relied on).
    Relog / world change (new Ref), death (DeathComponent) and a false cached flag also wipe; profile:busy only pauses.
    LOCKED Skyy 2026-09-25: loaded bolts survive teleports. This build still wipes on a world change. Relog, death, and profile switch still drop the load.
  CONFIG (spec 3.2 / 3.3): XbowCfg, the Crossbows-stay-loaded block of xp.properties (a fresh file has it; an existing one without
    perk.archery.keepLoaded.enabled gets it appended ONCE), read by SkillCfg.load (/skills reload and the kit's reload routine). 5 rows,
    159 in total: perk.archery.keepLoaded.enabled (Parts, live,part,danger - asks when switched OFF), .level (Perks, 0-100), .items
    (Perks, adv, text up to 500; its check= hook XbowCfg.checkItems refuses an empty list, an entry that is not an id start and one no
    loaded item id starts with, and asks first when an entry also matches ids without "Crossbow" - Weapon_ would count swords), .delayTicks
    (Perks, adv, 3-20), .debug (Perks, adv; admins with skyyskills.admin see one chat line per kept / restored / dropped load).
  TEXTS (spec 3.7): level-up chat "  Unlocked: Crossbows stay loaded when you switch slots" under SKILL LEVEL UP Archery 4 -> 5 (gated by
    the skills.levelUp setting like the level-up lines); Stats page (Archery) "Crossbows stay loaded when you switch slots" under Boosts
    right now from the unlock level, and under "Level 5 adds" one level before; the xp.properties load summary, ready line and manifest.
  BUILD CHECKS (spec 3.9): API probes + exact signatures of every call; Weapon_Arrow_Crude / Weapon_Crossbow_Iron exist; every
    Weapon_Crossbow_* item of Assets.zip AND of More Crossbow Tiers (PACK.md; found in the Mods folder by its manifest Serj:More Crossbow
    Tiers and read in memory, missing or installed twice = the build fails) has Parent Template_Weapon_Crossbow and no Weapon or
    Interactions block of its own, and the pack ships no copy of the template or the SwapFrom files (review of 0.4.5: the pack's 4
    crossbows were not checked before); the template clears Ammo, its Ammo modifier is exactly +6 Additive and its
    SwapFrom root is Root_Weapon_Crossbow_Swap_From = ["Weapon_Crossbow_Swap_From"]; the ladder is walked node by node (Condition
    Adventure -> StatsCondition Ammo 6..1 -> ModifyInventory Weapon_Arrow_Crude x k -> ChangeActiveSlot, no other node type): if Hytale
    changes the crossbow the build fails instead of the perk going quiet.
  CHECKED in a bare JVM (2026-09-25, scratch harness under tools/dev/scratch/r7-skills, deleted afterwards; 83 checks): all 87 classes
    load + initialise under -Xverify:all; XbowCfg.read defaults, custom values, clamps (level -5 -> 0, 500 -> 100, delay 1 -> 3, 99 -> 20,
    bad text -> defaults), the item list (blanks dropped, empty -> Weapon_Crossbow_), isCrossbow; SkillCfg.load: a fresh xp.properties =
    DEFAULTS with one block, a 0.4.4 file gets the block appended once at the end (custom values kept, a second load adds nothing), a hand
    edit is read; the flag against a mock bridge + player file: no class / Warrior / Archer 4 off, Archer 5 on, level 0 = every Archer,
    part off, profile:class mismatch, busy, refresh on / off (off drops the state), the weapon rule with and without class:fn:allowed,
    eligibleNow ignores the cache; fresh (absent epoch, baseline, same, change = wipe + flag off), drop, reset; Xbow.line and the Stats
    page (Archery 5 now / 4 next, right after the class damage line, not at 4 now / 5 next, not on other skills, part off, level 0; the
    Divinity heal line kept); retain / forget; the kit: 159 rows, the 5 rows (category, type, default, bounds, flags, position), get,
    part OFF asks / ON does not, level 101 and delay 2 refused, the file lines change in place and the reload routine applies them.
  UNVERIFIED (needs the game, spec section 4): XbowSlotSys + Xbow.onSlot / Xbow.tick on real hotbar switches (the event, the held-long-
    enough guard, the 3-tick restore after vanilla's wipe, the arrow payment through getCombined inside AcroSys, the client's bolt counter
    and its ~0.1 s gap), the level-up unlock line, the 5 rows in SkyyMenu's Server Setup; go/no-go tests 5, 9, 10 and 12.
  NOT HERE (spec 2.9 / 6): shortbows (LOCKED Skyy 2026-09-25: crossbows only), the off-hand slot.
    LOCKED Skyy 2026-09-25, not in this build: keep the Signature meter, a sound and a chat hint when bolts return, and /settings switches for the meter, the sound, and the hint. This build still resets the meter and stays quiet.
    Keeping loads across teleports is LOCKED yes (2026-09-25); this build still drops them on a world change.
    Planned, not built: Archery 15+ bolt capacity up to +4 extra bolts, and a late-game holstered reload of about 30 s.
0.4.4 (research/Classes-Berserker-Priest-Spec.md section 3 - BERSERKER + PRIEST; Skyy's decisions 2026-09-25, SkyWynn-Decisions.md change
  notes 1-2). Pairs with SkyyClasses 0.1.6 (class:list + class:weapons:Berserker|Priest, and the placeholder Priest heal that calls
  skill:fn:healxp) and SkyyProfiles 0.1.2; every mix loads and is safe (spec 5): with SkyyClasses 0.1.5 the two new slots simply stay
  empty and skill:fn:healxp is never called. NEVER DOWNGRADE to 0.4.3 once 0.4.4 has saved Fury or Divinity XP: 0.4.3's snap() drops the
  two unknown keys on its next save.
  SLOTS 14 Fury (key Combat.Berserker, icon Weapon_Battleaxe_Iron, #d9443f) and 15 Divinity (key Combat.Priest, icon Weapon_Wand_Wood,
    #f2e6a0), APPENDED after Exploration: N = 16, slots 0-13 keep their index and key (build-asserted against the 0.4.3 list), player
    files gain Combat.Berserker / Combat.Priest (+ .paid) on the next save (0 for everyone). An old Combat.Berserker line from the 0.3
    spike would become Fury XP (only a file untouched since 0.3 can still hold one - accepted, spec 3.1). The Shaman placeholder row's
    icon is Weapon_Deployable_Slowness_Totem (the wand belongs to the Priest now).
  CLASS SLOT TABLE (spec 3.2): class slots are no longer contiguous, so the SkillDefs fields CLASS0 / CLASS_END are GONE (nothing may do slot
    arithmetic any more; javassist would refuse a leftover reference) and SkillDefs.CLASS_SLOT = {5, 6, 7, 8, 9, 14, 15} follows the order
    of SkillDefs.CLASSES = Archer, Warrior, Assassin, Shaman, Mage, Berserker, Priest (FURY = 14, DIVINITY = 15), with isClass / classIdx /
    classSlot. The 11 sites use them: indexOf (exact and 3+ letter class names), SkillClass.slotOfClass, skillName, weaponOk, the killSlot
    hint, SkillStore.levelsOf (skill:<uuid>), moveLegacy (the legacy Combat move needs ALL seven class slots at 0), Perks.tick (as 0.4.3
    was, a Berserker = slot 14 threw ArrayIndexOutOfBounds inside the try: no health / stamina / mana perks, no republish), StatsPage
    lines / how / build. Everything class-based then follows class:<uuid> as for Archery: kills (KillSys -> killSlot -> weaponOk with
    class:weapons:Berserker|Priest from SkyyClasses 0.1.6; a wand-orb kill is judged by the main hand at death, the staff rule), the
    party share (PartyXp pays THEIR class slot), the combat perk row (health per class level, perk.combat.damagePerLevel), skill:<uuid>
    ("Fury:3", "Divinity:7"), skill:fn:level / skill:fn:xp ("Fury", "Divinity", "Berserker", "Priest", "Combat.Berserker",
    "Combat.Priest"; prefixes fur / div / ber / pri), /skills top | stats | xp. No per-skill rows: combat.* and perk.combat.* already apply
    to every class skill.
  DIVINITY XP FROM HEALING (spec 3.4): bridge skill:fn:healxp = Function apply(Object[]{UUID healer, Number hpHealedOnOthers, String
    source [, String expectKey]}) -> Boolean (SkillHealFn -> HealXp.offer; put in setup, removed in shutdown with the other functions).
    Only SkyyClasses 0.1.6 calls it (source "classes:heal", right after its placeholder Priest heal; self-heals are never sent). FALSE =
    refused: divinity.healXp.enabled off (or healXpPerHp 0), hp not a positive finite number, the healer's class skill is not Divinity
    (SkillClass.slot != 15), their class still follows a profile switch (SkillClass.consistent), the per-minute cap is used up, or
    BridgeXp.offer refuses (offline, profile key differs from expectKey, bridge.maxXpPerCall / maxXpPerMinute). XP = hp x
    divinity.healXpPerHp (0.2: a healed point is worth a damaged point, combat XP = monster max health x 0.2), the fraction paid by
    chance; 0 XP -> TRUE (nothing to pay). Cap: HealXp.HWIN, a 60 s window per player, divinity.healXpMaxPerMinute (300, 0 = no limit),
    counted in heal XP BEFORE the xp multiplier (the same with the default multiplier 1), not reset by a profile switch (the
    BridgeXp.WIN rule); ALL OR NOTHING (spec 3.4 "over the cap -> FALSE", the BridgeXp.allow rule): a grant that would cross it is
    refused whole = FALSE (nothing recorded; a later, smaller heal may still fit) + at most one WARN per player per minute
    (HealXp.warnLimited). Then BridgeXp.offer(u, 15, xp, source, expectKey, null, 0, false) queues a BridgeTask on the player's world
    thread (profile key + creative re-checked there), applies the xp multiplier like a kill, counts toward bridge.maxXpPerMinute and
    prints the normal "+2 Divinity XP" line (skills.xpGain); a refused offer gives its share of the cap back. A task the world thread
    drops later (creative - SkyyClasses' HealTask already skips creative Priests, spec 2.4 -, logged off or profile switched in between)
    keeps its share until the 60 s window ends: it fails closed (no XP is ever paid that way, the healer's own budget is only smaller for
    the rest of that minute), the same as BridgeXp.WIN for skill:fn:addxp / craftxp; the game mode is not read here because this
    function runs on any thread (components only on the world thread). Never throws, no file I/O, any thread.
  CONFIG (spec 3.5): 3 rows, 154 in total - divinity.healXp.enabled (parts, live,part,danger), divinity.healXpPerHp (combat, dec 0-100),
    divinity.healXpMaxPerMinute (combat, int 0-1000000000); reload: binding like every row. The "Divinity" block is in a fresh
    xp.properties and appended ONCE to an existing file without divinity.healXp.enabled (DivCfg.ensureDefaults, the PartyCfg pattern,
    inside SkillCfg.load = before CfgPub.start); the code defaults are the same numbers; the loader clamps to the row bounds.
  PAGES (spec 3.6): /skills is unchanged (the class row already shows the ACTIVE class's skill: a Berserker sees Fury with the battleaxe,
    a Priest Divinity with the wand; still 9 rows, 640 x 690). Stats page: Fury / Divinity show level, bar, class perks ("+X% damage with
    Berserker weapons (against monsters)"), next level, how-to "Earn XP by defeating monsters with Priest weapons - Spellbook / Wand" + the
    party text; for Divinity one more "Boosts right now" line: "Healing party members pays 0.2 Divinity XP per HP (up to 300 a minute)",
    or "Divinity XP from healing is off on this server" (a line, not the how-to: the how-to label is 45 px high).
  TEXTS: the unknown-skill message, the /skills stats | top | xp skill helps, the /skills xp no-class line, how(Combat) ("... / Berserker
    Fury / Priest Divinity (Assassin and Shaman later)"), the xp.properties load summary, the ready line and the manifest description.
  CHECKED in a bare JVM (2026-09-25, scratch harness under tools/dev/scratch/r6-skyyskills, deleted afterwards; 175 checks): all 83
    classes load + initialise under -Xverify:all; N = 16, slots 0-13 keep their keys, NAMES / LABELS / ICONS / COLORS of 14 / 15, the
    Shaman icon, CLASSES order, CLASS_SLOT / FURY / DIVINITY, isClass / classIdx / classSlot over -1..17, perkRow 14 / 15 = the combat
    row; indexOf (fury, divinity, berserker, priest, fur / div / ber / pri, Combat.Berserker / Combat.Priest, the old names, unknown =
    -1); a hand-written 0.4.3 player file loads with Fury / Divinity 0 (paid 0) and saves every old key + paid marker unchanged plus the
    two new keys; levelsOf for a Priest (Divinity with XP), a Berserker (Fury at 0 = the current class) and an Archer; moveLegacy refuses
    while slot 14 or 15 has XP and for a non-class slot, then moves into Divinity; slotOfClass, skillName, weaponOk(slot 14) answers
    false without throwing, weaponsText; Perks.tick for a Berserker reaches LASTCLS + the republish (skill:<uuid> with Fury:0); Stats
    page how(14) / how(15) / how(Combat), the Divinity heal line (on, off, no cap), no heal line under "Level L+1 adds", the Berserker
    damage line; DivCfg: fresh file = DEFAULTS, a 0.4.3 file gets the block appended once at the end (a second load adds nothing),
    custom values + clamps (500 -> 100, -5 -> 0, abc -> 0.2, 5e9 -> 1e9), the load summary; HealXp.amount (exact, the fraction by chance:
    mean 0.2 over 20000 rolls, edges), take / give (partial pay up to the cap, used up, give back, new window, cap 0 = no limit;
    take is all or nothing since the 2026-09-25 review fix, see REVIEW FIXES);
    skill:fn:healxp gates (bad arguments, no class, Warrior, part off, rate 0, 0 XP -> TRUE, NaN / negative / infinite / 0 hp, class
    still following a profile switch, cap used up) and a refused offer (no Universe in a bare JVM) giving its cap share back; the kit:
    config:def 154 rows / 8 categories, the three Divinity rows (category, type, default, bounds, flags), get, typed values outside the
    bounds refused, part OFF asks / ON does not, the file lines change in place and the reload routine applies the new values.
  REVIEW FIXES (2026-09-25): the heal cap is ALL OR NOTHING (spec 3.4; take returns boolean, offer sends the whole base); a SkyyClasses
    0.1.6+ build script whose CLASSES roster cannot be parsed now FAILS the build (it matched the real 0.1.6 roster); /skills xp lists
    the same skills as stats / top. Re-checked in a bare JVM (-Xverify:all, 106 checks, scratch deleted): all classes load; take (fits,
    crossing refused with nothing recorded, exact fit, used up, new window, want > cap, cap 0, want 0), give; offer (no class, Warrior,
    over the cap = FALSE with nothing recorded, a refused offer gives the share back, bad hp, rate 0, 0 XP = TRUE, no cap, switch off),
    SkillHealFn, statsLine.
  UNVERIFIED (needs the game): a real Priest heal from SkyyClasses 0.1.6 through skill:fn:healxp -> BridgeXp.offer -> BridgeTask (TRUE,
    the "+N Divinity XP" line, the cap in practice); Fury / Divinity kill XP with real axes / maces / wands (class:weapons:* published by
    SkyyClasses 0.1.6; a wand-orb kill judged by the main hand at death); the party share into Fury / Divinity; the /skills class row
    (battleaxe / wand icon) and the Stats page note "You are not a Berserker right now" on a client; the three rows in SkyyMenu's Server
    Setup (Parts and Combat tabs).
  NOT HERE (other mods / later): the Priest heal itself, class kits and the Create Profile cards (SkyyClasses 0.1.6, SkyyProfiles
    0.1.2); SkyyGuilds' xpSkills default without Fury / Divinity (spec F1); Mana for Priests / Mages (spec Q6).
0.4.3 (research/Server-Setup-Spec.md 4.9 + 5.7 - SERVER SETUP IN GAME; research/Settings-Spec.md 1.3 + 3.1 - PLAYER SETTINGS). Builds on
  0.4.2 and changes NO default behaviour: every number, switch and message is the same until an admin changes something.
  ADMIN CONFIG (tools/skyycfg.py, contract tools/CONFIG-CONTRACT.md; SkyyMenu 0.3 Server Setup shows it as "Skills"):
    config:def:SkyySkills / config:fn:SkyySkills / config:epoch:SkyySkills, published at the END of setup() after SkillCfg.load().
    File Skyy_SkyySkills/xp.properties (names and keys unchanged), node skyyskills.admin, categories parts / general / levels /
    gathering / combat / acrobatics / perks / crafting. Rows bind reload: - the kit changes only that line of xp.properties (comments and
    order kept), versions the file (config-history/, 20 copies), logs config-changes.log, then runs SkillKit.reload (= SkillCfg.load +
    Acro.djPublish, exactly what /skills reload does). Tables (key families, reload:): block. / prefix. / suffix. (column Skill:XP or none,
    check= SkillKit.checkRule = the loader's own parseRule / explRule), combat.role. (XP), alchemy.xp. / smithing.xp. (XP, entries must be
    item ids, add by typing or holding the item). Parts (live,part,danger - confirm only when switched OFF): acro.enabled,
    acro.doubleJump.enabled, perk.enabled, alchemy.enabled, smithing.smelt.enabled, exploration.enabled, fell.enabled,
    party.combatShare.enabled, bridge.bonus.enabled. Typed values are refused outside the loader's clamp ranges (files are still clamped
    by the loader as before). A build assert compares every row default with the default xp.properties text; the 21 per-skill perk
    stats that are NOT in the default file (they read 0) are adv rows with default 0 (PerkCfg's own defaults).
    Level curve (spec 5.7): "Level curve size" (int %, custom: SkillKit) = the levels= list as a percent of the default curve over the
    same number of levels; setting N rescales every level to N% (so it can be undone by setting the old value) - "Max level" (int 1-100,
    custom: SkillKit) cuts the list or extends it along the default curve's shape (joined at the last kept level; the default list
    extends back to exactly the default). A cut remembers the full list in memory (SkillKit.TAIL / LAST, this server run): raising Max
    level again while the list is still what the last Max level change left (Undo included) gives the cut levels back EXACTLY, also for a
    hand-edited or imported curve; after a restart or any other change of the list, History restores an exact older list. Both read the
    kit's current levels= value (pending edits included), apply the new table at once (SkillDefs.setTable), hand the levels= line to the
    kit and arm the kit's reload routine (CfgFile.addReloads; again 200 ms later through SkillKitArm on the scheduler, which also sets
    CfgFile.force so a save + reload cycle runs even when no save is due - a save that took the first arm before the line existed, or
    that wrote the line before the re-arm, can never leave the running table behind the file; kit gap: wants() ignores a pure arm).
    Players keep their XP; a lower max shows MAX, raising it again gives the levels back.
    upgradeLevels (0.3 migration of the old 50-level default) now runs only for a file without perk.* keys (written by 0.1 / 0.2), so
    "Max level 50" from the default list (identical to the old table) is not silently undone at the next load.
    /skills reload keeps its reply and effect: it first runs the kit's reload op (hand edits logged via=file, pending in-game changes
    written), then SkillCfg.load() + Acro.djPublish() as before. The file is read twice ON PURPOSE: the kit's reload op merges on the
    caller thread and, only when it found hand edits (or in-game edits were pending), runs SkillKit.reload once more on its save task
    shortly after the reply; the synchronous load keeps the 0.4.2 reply text. Both are idempotent (SkillCfg.load is synchronized).
    Plugin shutdown flushes the kit (CfgPub.shutdown) first.
    Row help: combat.min / combat.max say that an inverted pair pays every kill the maximum (no cross-check: an import that raises both
    must not be refused); perk.exploration.staminaPerLevel says SkyyExploration 0.2.1+ shows it on /explore (read over config:fn get).
  PLAYER SETTINGS (Settings-Spec 3.1): SkillStore.moveQuiet / notifyOn / regSetting. setup() registers skills.xpGain, skills.levelUp,
    skills.doubleDrop, skills.extraPotion, skills.combatHints (tab skills) and rewards.late (tab coins, shared with SkyyCollections,
    identical label / help). Gates (only the chat send; XP, coins, drops, throttles and latches run as before): SkillMsg.note +XP line,
    gain4 SKILL LEVEL UP + next: lines (levelUp) and the late coin line (rewards.late), SkillClass.tellOnce before claimTold (combatHints),
    Perks.doubled (doubleDrop), Brew.extraPotion (extraPotion), and the two 0.4.2 lines /skills quiet hid: the "Tree felled" summary and
    the "[Party] +N XP" line (skills.xpGain). Without SkyyMenu every switch reads ON and /skills quiet works as before; with it the
    first message check moves an old quiet=true profile flag to the three switches (onlyIfUnset) and /skills quiet flips them.
    Admin master switches still win (feedback, perk.doubleDropMessage, fell.message, party.combatShare.message).
  CHECKED in a bare JVM (2026-09-25, scratch harness under tools/dev/scratch/r4-skyyskills, deleted afterwards): all 80 classes load +
    initialise under -Xverify:all; SkillCfg.load writes the default file; CfgPub.start publishes config:def (contract 1, 151 rows, 8
    categories) + config:fn; every scalar row reads its default on a fresh file; status ok; the prefix table lists 47 entries; levels.max
    60 asks first (danger), cuts the file list to the first 60 default levels, max 60 at once and after the reload routine; levels.scale
    110 -> level 1 = 55 (x1.1 in file + table), back to 100 = the list exactly, the same value twice = "already" (no compounding); max 100
    extends back to exactly the default; a 200% list extends at 200%; max 50 survives SkillCfg.load; a 0.1-era file (no perk.*) with the
    old 50 table still upgrades, a 0.3+ one keeps 50; multiplier 2 / trigger jump (skill:dj:key republished) / fell.enabled applied by the
    reload routine; part OFF asks, ON does not; ignorePlaced OFF and creativeXp ON ask; typed values outside the clamps refused
    (feedbackMs 100, fell.radius 17, 1.5 in an int row); check hooks (levels 0,5 / 101 entries refused, 10,20,30 accepted then Default;
    Exploration and unknown skills refused in the bonus lists, allowed in bridge.addxp.skills; alchemy.tierXp with 6 entries or a word);
    tables: block add (the loader's EXACT has it) / remove, Exploration and Combat rules refused, prefix tset, combat.role add (ROLE has
    it); export code; config-changes.log, config-history copies, versions; History restore preview lists no "not restored" curve row;
    comments kept; notifyOn without SkyyMenu (all ON; quiet hides only xpGain / doubleDrop / extraPotion) and with a fake registry
    (its answers used, quiet moved once with onlyIfUnset); regSetting writes settings:def.
  FIX ROUND (2026-09-25, review findings; second scratch harness, 26 checks, deleted afterwards): 80 classes under -Xverify:all; fresh
    file byte-identical; max 50 survives SkillCfg.load; a NON-uniform 100-level list: max 60 -> 40 -> 100 and 40 -> 60 -> 50 -> 100 give
    the exact list back; after a curve-size change or a hand edit (kit reload op) the raise follows the default shape; an 80 list cut to
    50 and raised to 90 = 51-80 exact + 81-90 along the default; the default list 60 -> 100 = exactly the default. Race replayed
    deterministically: an unrelated dirty save taking the arm between customSet and the kit's levels= edit puts the 100 table back, the
    levels= save then runs no reload, a plain re-arm (no force) leaves the table behind the file, SkillKitArm.run (force) brings table ==
    file; a spare forced re-arm changes nothing. Help texts of combat.min / combat.max / perk.exploration.staminaPerLevel / levels.max.
  UNVERIFIED (needs the game): the "Skills" page in SkyyMenu 0.3 Server Setup (8 tabs, 151 rows, table views, the curve rows' TextField +
    Set / Less / More); entry=item on alchemy.xp / smithing.xp against the live item map (the bare JVM has none); the kit saves and
    SkillKitArm on HytaleServer.SCHEDULED_EXECUTOR; /skills reload's kit reload op with a real admin; every Settings gate with SkyyMenu 0.3
    (level-up / next / late-coin lines, combat hints, double drop, extra potion, Tree felled, [Party]), the /skills quiet shortcut and the
    quiet move on a real profile.
0.4.2 (research/Tree-Fall-Spec.md sections 2, 3.1 and 4 - FELLED TREES; + the Stats page 1.5x). Pairs with SkyyCollections 0.2.1
  (source skills:felled) and SkyyTrees 0.2.1 (same-Y Tree Feller, per-log nodes on skill:on:felled); every mix loads and is safe (spec 3.4).
  WHY: only the block a player breaks fires BreakBlockEvent; Hytale's block physics then removes the rest of the tree one pass at a time
  with no event and no player, so a felled tree paid 1 log (6 XP, Collections +1). Now every log that FALLS is paid to the feller.
  1 SNAPSHOT (BreakSys handler, synchronous, the tree is still standing): trigger TRUNK (a TreeWood _Trunk / _Trunk_Full id), BRANCH
    (_Branch_Short/_Long/_Corner) or UNDER (any other block - not leaves / roots - with a TreeWood trunk right above it, fell.underTrunk).
    Breadth-first search over the 26-neighbourhood: same-family wood (FellDefs: TreeWood.json / TreeLeaves.json generated from Assets.zip
    at build time), natural only (not in PlacedStore, not BlockPhysics.isDeco), |dx|,|dz| <= fell.radius, y <= y0 + fell.height; trunks
    y >= y0, branches / roots y >= y0 - 1 (BRANCH trigger: branches only). Trunks ON y0 are the LAYER (the other base logs of a thick
    tree: only cut, never claimed) but stay search nodes. Leaves: 26 neighbours of accepted wood, then up to 4 leaf steps, y >= y0 - 1
    (claims only with fell.leaves; always used for the natural-tree test fell.needLeaves). Caps fell.maxLogs / fell.maxLeaves /
    fell.maxReads (per-section cache), fell.maxSnapshotsPerSecond per player. Creative / fell.disabledWorlds: no snapshot.
    Fallback (spec 3.1): if a block read inside the handler throws, the log warns once and every later snapshot is taken in BreakTask
    instead, stepping through up to 2 empty cells straight above the seed.
  2 COMMIT (BreakTask, first thing after the cancel check, BEFORE XP and skill:on:gather - the Tree Feller breaks inside gather):
    dropped without natural leaves (needLeaves), without claims, over fell.maxWatchesPerPlayer / fell.maxWatches. Claim takeover
    (spec 2.4): a claim is taken when free / dead / the same player's, or from another player when this cut was not itself on their
    falling part (the last-support rule); the layer keys map to the new watch. A cancelled break (island protection) puts back a claim
    its handler removed and discards the snapshot.
  HAND BREAKS: a break on a claimed position unclaims it (paid by the normal hand path, never also as felled); the same player's break
    on their own claim / layer only touches that watch (no new search) - so the Tree Feller's extra base breaks never search again.
  3 WATCH (FellWatch, HarvestTask hop pattern every fell.pollMs): a claimed position whose block index turned 0 (air) and is still
    held by this watch = FELLED; -1 (chunk gone) = lost, another block = replaced (no credit). Ends when all resolved, fell.quietMs
    without a change (touch() counts), fell.maxWatchMs, or the owner went offline; releases its claims / layer entries; optional
    "Tree felled: 19 logs, 42 leaves (+156 Foraging XP)" line (fell.message, hidden by /skills quiet); fell.debug = one log line per
    watch (claims, credited, hand, env, lost, other, replaced, skipped, dropped, collections, xp, ms) and one per snapshot (reads, us).
  4 CREDIT (FellCredit.one, world thread) only while the owner is online, on the snapshot's profile (pkey), not profile:busy, in the
    tree's world and not in creative: Foraging XP = the hand-break table (SkillCfg.classifyBreak, global multiplier) x fell.xpFactor
    (leaves x fell.leafXpFactor), + the skill-tree XP bonus (Foraging Wisdom) through the normal award path ("+XP" lines, level ups,
    coins); Perks.breakDouble (fell.doubleDrops; perk.foraging.doubleDropOnly=_Trunk keeps it to trunks); SkyyCollections: the
    ENGINE's physics drop selection (Physics, else Breaking (quantity), else Soft, else Harvest) re-rolled with BlockHarvestUtils.getDrops,
    each stack -> coll:fn:add Object[]{UUID, itemId, Long qty, "skills:felled", pkey} (fell.collections; SkyyCollections 0.2.1 accepts
    the source by default, 0.2 only if an admin adds it to bridge.add.sources); skill:on:felled listeners (fell.nodes, only for blocks
    the XP table knows); the "felled by" memory. A rule-less block still counts in Collections, gets no XP / double drop / nodes.
  EXPLOSIONS / FIRE: EnvSys (WorldEventSystem, EnvironmentBreakBlockEvent - fired by explosions before the removal and by fire right
    after its setBlock, both on the entity store, bytecode-checked) removes a claimed position: never paid as felled. If EnvSys cannot
    be registered the log warns and the fell feature stays OFF until the next restart (FellCfg.BROKEN; /skills reload does not help).
  BRIDGE: skill:on:felled = ConcurrentHashMap name -> Function (putIfAbsent in setup, left in place at shutdown), called once per
    credited position with Object[]{PlayerRef, Integer row, BlockType, String world, Integer x, Integer y, Integer z, String pkey}, each
    listener in its own try/catch, a failure logged once per listener; a SEPARATE map from skill:on:gather, so SkyyTrees 0.1 / 0.2 never
    see felled logs. skill:fn:felledBy apply(Object[]{String world, Integer x, Integer y, Integer z}) -> Object[]{UUID owner, String
    pkey, Long atMillis, String "falling" | "felled"} or null (any thread; "felled" is remembered fell.memoryMs, 8192 per world).
  CONFIG: the "Felled trees" block (fell.* + placed.skipSaplings + collections.doubleDrops) is in a fresh xp.properties and appended
    ONCE to an existing file without fell.enabled (FellCfg.ensureDefaults); /skills reload re-reads it; clamps pollMs 50-1000,
    quietMs 500-10000, radius 1-16, height 1-128, maxLogs 1-1024, maxLeaves 0-2048, factors 0-5 (+ sane bounds for the rest).
    Skyy decisions left as switches (spec section 6): fell.extraTrees=false (apple fruit trees + the Bamboo / Ice Trunk_Full blocks
    that Hytale's tree lists miss), placed.skipSaplings=true (a planted sapling is not recorded as placed, so the base log of a replanted
    tree pays - the spec's recommended fix), collections.doubleDrops=false (double-drop items counted in Collections, hand breaks too).
  STATS PAGE 1.5x: root 960 x 795 (fits a 1080-high screen), title 24 pt, sub 17, headers 20, lines 18 (28 high), how-to 15 pt wrapped,
    bar 600 x 18, buttons 195 x 45 (18 pt). The Foraging how-to says felled trees pay every falling log (while the feature is on).
  CHECKED in a bare JVM (2026-09-24, scratch harness under tools/dev/scratch, deleted afterwards): all 68 classes pass -Xverify:all;
    FellCfg defaults / clamps / disabledWorlds / ensureDefaults (appends once, no-op when fell.enabled exists); FellDefs ids (apple only
    with fell.extraTrees); the search through the FellRead test seam: 1-wide birch (19 logs + every leaf claimed, the cut log not),
    leaves off, a mid-trunk cut, UNDER (20 logs incl. the seed), UNDER without a trunk, a deco tower (nothing, no natural leaves), a
    PlacedStore log never claimed, 2x2 (layer 3, 64 logs above), a flared base (wood above a far base log claimed through layer nodes),
    BRANCH trigger (branches only), the read budget, touching same-family trees join / another family excluded, the late fallback (up
    to 2 empty cells), the 10/s rate limit; claims: commit, a hand break by another player (inOther) and by the owner (reuse), layer
    reuse, cancelled-break restore, a cut inside another player's fall keeps their claims, the last-support cut takes them, EnvSys
    unclaim, felledBy falling / felled / null, end releases, the needLeaves drop, maxWatchesPerPlayer 4, endAll; the Stats page markup
    for 9 skills (root 960 x 795, unique ids without underscores, content <= 752 px incl. padding).
    Test seams (harness only; null / false in the game): FellRead.TEST, FellRead.TESTDECO, Fell.TEST_NO_SCHEDULE.
  UNVERIFIED (needs the game): block reads inside the BreakBlockEvent handler (spec T1; a throw switches to the late fallback), the
    cascade timing vs fell.quietMs (T14), EnvSys registration and delivery (T17), FellCredit end to end with a real player (XP, double
    drops, coll:fn:add, skill:on:felled), the scheduler hop, the Stats page on a real client at 1.5x.
0.4.2 stage 2 (same version; tools/skills_0_4_2_patch.py STAGE 2 - the stage 1 felled trees + Stats page 1.5x above are kept):
  DOUBLE JUMP (research/Double-Jump-Spec.md 3.2, the SkyySkills part). The node is SkyyTrees 0.2.1 "Double Jump" (RDouble, Acrobatics
    tier II slot 5): skill:bonus doublejump.acrobatics = the air-jump height as a fraction of the player's own jump height (0.55-1.0).
    Acro.airJump runs in AcroSys.tick on the world thread EVERY tick (right after Acro.move, before Acro.dodge). airTrack (pure) keeps
    the edges and the airtime: crouch press, jump press, extraJumpsUsed change; ground / climbing / fluid / swimming / mantling = charge
    reset (spec 2.3 rule 2); mounted / flying / gliding / sitting / sleeping (the rest of Acro.excludedState) restart the airtime clock
    but keep the charge, so minAirMs counts from the end of the glide / flight and a mid-air glide never refills the jump. airTry (pure)
    decides: trigger acro.doubleJump.trigger = crouch (rising edge of MovementStates.crouching while airborne -
    DEFAULT, copied from TerrariaAddons' Cloud in a Bottle) | jump (rising edge of MovementStates.jumping while airborne; never when the
    client jumped itself: upward speed above fallJumpForce / 2 = a coyote or buffered jump) | both; minAirMs after leaving the ground,
    maxJumps per airtime, cooldownMs, the node (0 = none, clamped to maxFraction), not falling faster than maxFallSpeed (0 = the world's
    MovementConfig MinFallSpeedToEngageRoll, vanilla 21 b/s = before a landing would hurt). airJump (engine glue): acro.enabled +
    acro.doubleJump.enabled, not mounted / flying / gliding / sitting / sleeping / climbing / in fluid / swimming / mantling
    (Acro.excludedState), not creative (the REAL game mode), Stamina (acro.doubleJump.stamina, taken only when the jump happens; too
    little = no jump and the charge is kept; StaminaRegenDelay set to -staminaRegenDelay like vanilla Double_Jump.json), then ONE
    Velocity Set instruction: vy = min(jumpForce x sqrt(V), sqrt(2 g maxBlocks)), horizontal = the client's own + forwardPush along it.
    0 Acrobatics XP by default (acro.doubleJump.xp -> the capped pending pool) and the push never pays ground-jump XP (s[9] = now).
    Optional FX (acro.doubleJump.fx): SFX_Player_Jump + Impact_Feathers_Black. acro.doubleJump.debug=true: players with skyyskills.admin
    get a "[Skills] DJ debug: crouch edge in air - vy .. - air .. ms - used .." chat line per airborne crouch / jump / extraJumpsUsed
    edge (spec test 5.0 decides the trigger; the probe also works with acro.doubleJump.enabled=false, it only needs acro.enabled).
    Only an edge of the configured trigger goes on to the node / movement-settings lookups. Charges reset on a world change and a
    profile switch (Acro.reset / profileReset).
    Bridge skill:dj:key = "crouch" / "jump" / "jump or crouch" (setup + /skills reload, removed at shutdown) = the %K of the SkyyTrees
    card. Stats page: "double jump 55%" in the Acrobatics "Skill tree:" line + "Double Jump: press crouch in mid-air for a 55% jump -
    2 Stamina" while the node is owned. STATE double[292] (281-287 used, see the layout comment).
  PARTY COMBAT XP (beta backlog 6, Skyy: "party should share combat XP"). KillSys pays the killer exactly as before (class, class weapon,
    not creative; the killer keeps 100 %), then PartyXp.share: every OTHER member of the killer's party (bridge party:fn:members,
    SkyyParty 0.1.3: String[] member UUIDs) who is online, in the SAME world (same entity store = the same world thread), ready, alive,
    not in creative (creativeXp rule) and within party.combatShare.radius (48) blocks of the killer gets party.combatShare.fraction
    (0.5) of the killer's base kill XP (after the xp multiplier, before the killer's tree bonus; a fraction is paid by chance) into
    THEIR OWN current class skill on THEIR active profile (needs a class; no weapon rule for them; skipped while their class is still
    following a profile switch - SkillClass.consistent), + their own tree XP bonus (party.combatShare.treeBonus). Level ups, coins and
    SkyyGuilds guild XP follow the normal award path. Chat: "[Party] +6 Archery XP (340/500) from Skyy's kill" - batched per member
    and throttled like the other XP lines (feedbackMs, flushed by the 1 s ticker; /skills quiet, feedback=false and
    party.combatShare.message=false hide it). The share goes through SkillXp.gain4 (= gain3 + the party note right after the XP is
    added, like SkillMsg.note), and a level up flushes the pending [Party] line first, so it always prints BEFORE the SKILL LEVEL UP it
    causes, like every other XP line. Without SkyyParty (no party:fn:members) nothing changes. The class how-to line on the
    Stats page mentions the share while it is on and SkyyParty is loaded.
  CONFIG: the "Double Jump" (acro.doubleJump.*) and "Party combat XP" (party.combatShare.*) blocks are in a fresh xp.properties and
    appended ONCE each to an existing file without acro.doubleJump.enabled / party.combatShare.enabled (AcroCfg.ensureDj,
    PartyCfg.ensureDefaults); /skills reload re-reads both and republishes skill:dj:key. Clamps: maxJumps 1-5, maxFraction 0-1.5,
    maxBlocks 0.5-10, forwardPush 0-10, cooldownMs 0-60000, minAirMs 0-5000, fraction 0-1, radius 1-512.
  COMMANDS / UI: no new command. Stats page lines only (no new element ids).
  CHECKED in a bare JVM (2026-09-24, scratch harness under tools/dev/scratch, deleted afterwards): all 71 classes load + initialise
    under -Xverify:all; the compiled call targets (SoundUtil.playSoundEvent3d(int, SoundCategory, Vector3d, ComponentAccessor),
    ParticleUtil.spawnParticleEffect(String, Vector3dc, List, ComponentAccessor), Velocity.addInstruction(.., Set), the MovementConfig
    chain, EntityStatMap subtract / set, PartyXp.share after SkillXp.gain in KillSys) read back from the bytecode; config: both blocks
    once in a fresh file, appended once each to a 0.4.1-style file and to a 0.1-era file (no duplicate keys after two loads), every
    default, the trigger parse (Jump / both / unknown -> crouch), every clamp, djText / PartyCfg.text / the load summary; airTrack
    (ground / climbing reset, airtime start, crouch / jump / extraJumpsUsed edges, holding = no edge) and airTry (-1 .. -7 reasons:
    trigger per mode, minAirMs, one charge, cooldown, no node, falling 25 > 21, rule J in jump mode only, both = crouch skips rule J; vy =
    11.8 x sqrt(0.55) = 8.75; cap 14.97); reset / profileReset zero 281 / 282 / 284 / 285; STATE double[292]; djFraction from
    skill:bonus (clamped by maxFraction, 0 with bridge.bonus.enabled=false); djLine / the tree line "double jump 55%" / 6 Acrobatics
    lines (cap 7); skill:dj:key crouch / "jump or crouch"; djMaxFall without a world = 21; PartyXp.amount (10 x 0.5 = 5, 7 x 0.5 = 3 or 4
    with mean 3.5, 1 x 0.5 = 0 or 1 with mean 0.5); members() from a fake party:fn:members; slotFor (no SkyyClasses / no class / Archer /
    class still switching -> -1); the chat batching ("from Skyy's kill", "from 2 kills by Skyy", "from 2 party kills", the SkyyClasses
    skill display name, throttle, drop); the class how-to text only while SkyyParty is loaded.
  UNVERIFIED (needs the game): spec test 5.0 - whether the client reports MovementStates.crouching (and jumping) while airborne; the
    Velocity Set push feel + latency; the Stamina cost / regen pause; the world MovementConfig lookup (21 in vanilla); the FX; the
    SkyyTrees 0.2.1 node -> skill:bonus doublejump.acrobatics path in game; PartyXp.share end to end with two real players (member
    PlayerRef -> Ref in the killer's store, positions, level ups on the member's profile, the chat line); the Stats page lines on a client.
0.4.1 (research/Exploration-Build-Spec.md section 3 - the Exploration row; deploy with SkyyExploration 0.1 + SkyyTrees 0.2, each loads alone):
  SLOT 13 Exploration (N = 14, append-only: slots 0-12 unchanged; >= CLASS0 but not a class). /skills = 9 rows: Mining, Foraging,
  Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration, class skill (ROW_SLOTS); perk row 8 = exploration (PERK_SLOT; PerkCfg.KEYS
  has 9 entries and so does EVERY perk array - the HP / STA / MANA / DD / ONLY statics AND the dhp / dsta / dmana / ddd / donly fallbacks
  inside PerkCfg.read(), whose loop indexes them up to KEYS.length). skill:<uuid> = "...,Cooking:3,Exploration:12,<class skills>";
  skill:fn:level / skill:fn:xp answer "Exploration" through indexOf. Player files gain Exploration=<xp> / Exploration.paid=<level> (old
  files load 0). NEVER DOWNGRADE to 0.4 once Exploration XP exists: 0.4's snap() drops the unknown keys on its next save.
  XP: ONLY through skill:fn:addxp (skill "Exploration"; SkyyExploration sends Object[]{UUID, "Exploration", Long, "exploration", pkey}).
  NO BOOSTERS (Skyy Q3), enforced in code: SkillDefs.boostable(EXPLORATION) = false -> BridgeXp.offer pays the base XP (no xp multiplier)
  and never adds a skill-tree bonus, SkillBonus.xpBonus returns 0 for it; BridgeCfg.read sets GRANT[EXPLORATION] = exploration.enabled
  (grantable whatever an old 0.4 bridge.addxp.skills line says) and forces BONUS_XP / BONUS_ADDXP[EXPLORATION] = false (one WARN
  "Exploration never gets XP bonuses (Skyy) - ignored" when bridge.bonus.xpSkills / addxpSkills name it). A block. / prefix. / suffix.
  rule naming Exploration is ignored with a WARN. bridge.maxXpPerMinute still counts Exploration (a safety bound, not a booster). The
  admin /skills xp exploration <n> stays raw. Exploration grants post no "+N Exploration XP" line of their own (BridgeTask note = false
  for this slot): SkyyExploration writes its own chest / zone / aggregated chunk lines and /explore quiet hides them; level-up lines
  and the level coins show as for every skill.
  PERK: +0.1 max Stamina per level (perk.exploration.staminaPerLevel, summed into the skyyskill_stamina MAX modifier by the 1 s
  Perks.tick) + the generic coinsPerLevel x level. CONFIG: the Exploration block (exploration.enabled, perk.exploration.staminaPerLevel,
  acro.treeDodgeMax) is in a fresh xp.properties and appended ONCE to an existing file without exploration.enabled (ExplCfg.ensureDefaults,
  the AlchCfg pattern); /skills reload re-reads it; the code defaults are the same numbers.
  ACROBATICS TREE (SkyyTrees 0.2): Acro.boost pushes dodgeBonus(level) + Acro.treeDodge(u) = skill:bonus:<uuid> "dodge.acrobatics" summed
  over sources, clamped 0..acro.treeDodgeMax (0.25), only while acro.enabled and acro.dodgeBoost (a level-0 player with tree points
  still gets the tree part). Speed / jump / fall nodes need no Skills change: they arrive as the movement source "trees.acrobatics",
  which MoveSync and the stat:owner:fallDamage owner (SkyySkills) already sum.
  UI: /skills root Height 690 (8 x 58 + Acrobatics 72 + 4 px gaps), footer "- explore". Tree buttons (row "Tree", Stats "Skill tree")
  only when SkillBonus.treeAvailable(slot): SkyyTrees running (tree:fn:level) AND bridge tree:names (SkyyTrees 0.2, comma list of tree
  labels) lists the skill - or, without tree:names (SkyyTrees 0.1), Mining / Foraging / Farming / Cooking exactly as in 0.4;
  treeName(Acrobatics) = "acrobatics", treeName(Exploration) = "exploration". Stats page Exploration: how-to text (wrapped label), "+X max
  Stamina", the skill:stats:Exploration hook lines (SkyyExploration) or "Install SkyyExploration to earn Exploration XP", and "Exploration
  XP ignores the xp multiplier and every skill-tree or booster bonus"; Stats page Acrobatics: "Skill tree: +5% speed, +0.2 blocks jump,
  -5% fall damage, +10% dodge push" from move:<uuid>["trees.acrobatics"] + the tree dodge. /skills stats|top|xp help and the unknown-skill
  message list exploration (the 3+ letter prefix "exp" resolves).
  Known edge (0.4 bridge behaviour, unchanged): BridgeTask still drops a grant it accepted when the player is in creative (creativeXp=
  false) or the profile changed between offer and task; SkyyExploration never grants in creative with its defaults.
0.4 (research/Alchemy-Skill-Spec.md, research/Smithing-Smelting-Spec.md SkyySkills parts, orchestrator decisions of the 0.4 round):
  SLOTS: 10 Alchemy, 11 Smithing, 12 Cooking (N = 13, append-only; CLASS_END = 10 bounds every class loop - slots 10-12 are >= CLASS0
  but are not classes). Slot 3 "Combat" is kept in NAMES (snap() drops unknown keys, so removing it would delete unmigrated legacy
  XP) but has no /skills row any more: the class row shows the class weapon skill by name, or "Class skill - choose a class with
  /class" (+ the old Combat XP line). /skills = 8 rows: Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, class
  skill (ROW_SLOTS); perk rows = mining, foraging, farming, combat (= current class), acrobatics, alchemy, smithing, cooking
  (PERK_SLOT; Perks.rowLevel reads through it). Bridge skill:<uuid> drops the Combat entry and gains Alchemy / Smithing / Cooking.
  ALCHEMY: the vanilla Alchemy Bench fires CraftRecipeEvent$Post on the crafter for every finished unit (queued path: one Post per
  unit but getQuantity() = the whole batch, so 1 unit per Post when TimeSeconds > 0; instant path: quantity). CraftSys (Archetype.empty
  query, like BreakSys) defers to CraftTask on the world thread: dropped when the event was cancelled, the player left, or the profile
  key changed between craft and award; creative pays nothing. XP per craft by primary output id (alchemy.xp.<id>, unlisted
  Alchemybench recipes -> alchemy.tierXp by bench tier, logged once). Perks: potion effects you DRINK last +1%/level (cap +100%) -
  Brew.tick (every tick from AcroSys) extends each fresh application of a whitelisted effect ONCE by base x bonus with
  EffectControllerComponent.addEffect(..., OverlapBehavior.EXTEND, ...) (no restart, no extra pulse); +0.2 max Mana per level
  (skyyskill_mana); 0.2%/level (cap 25%) chance to brew one extra potion (Potion_* / Weapon_Bomb_*, never Potion_Empty*). The build
  fails if an Alchemybench output worth more than 10 XP feeds a recipe that returns one of its own inputs (craft/uncraft loop).
  SMITHING: vanilla Furnace = SmeltSys (InventoryChangeEvent, Player query): a MOVE_TO_SELF move whose other container is the
  combined container of a Furnace ProcessingBenchWindow the player has open, removed from its OUTPUT part (container 2), pays the
  items that landed in the player's inventory (add side, once per container) x SmithCfg.forOutput(id) -> SmeltTask on the world
  thread (pkey re-check; offline -> silent addK). smithing.xp.<id> table (bars = 1.0 x the ore's Mining XP, glass vial 2, charcoal 0),
  unknown Ingredient_Bar_* = the Mining XP of its Furnace recipe's ore x smithing.oreFactor (min 1), else smithing.smeltDefault.
  Salvagebench / Tannery / Campfire windows pay nothing here.
  COOKING: row + Stats page only. Cooking XP arrives ONLY through skill:fn:addxp from SkyyCooking; the craft hook IGNORES Cookingbench
  and Campfire recipes (RecipeXp.classify -> null), so SkyyCooking's crafts are never double counted.
  BRIDGE (plain java.util.function.Function objects, published in setup, removed in shutdown):
    skill:fn:addxp  apply(Object[]{UUID, String skill, Number baseXp, String source [, String expectKey]}) -> Boolean. skill = an exact
                    NAMES/LABELS entry listed in bridge.addxp.skills (default Mining,Foraging,Farming,Alchemy,Smithing,Cooking);
                    TRUE = accepted and queued on the player's world thread (creative / profile re-check there can still drop it),
                    FALSE = refused (unknown or not grantable skill, bad amount, over bridge.maxXpPerCall, per-minute cap, offline,
                    expectKey differs). Never blocks, never does file I/O, any thread.
    skill:fn:craftxp apply(Object[]{UUID, String recipeId, Number crafts, String source [, String expectKey]}) -> Long or null. For crafts
                    the caller completed WITHOUT CraftingManager (SkyySacks /craft + Furnace tab). Skill and XP come from the same
                    RecipeXp.classify table as the vanilla bench (Alchemybench -> Alchemy, Furnace -> Smithing, Cookingbench /
                    Campfire / everything else -> 0). Long = accepted (0 = this recipe pays nothing, OR the call can never be
                    paid because recipe XP x crafts is over bridge.maxXpPerCall - drop it from your ledger either way; so send
                    big ledgers in parts: SkyySacks 0.7.3 sends at most 1,000 units per call); null = refused for now (offline,
                    per-minute cap, profile key differs) - keep the ledger and retry later.
    skill:stats:<SkillName> (OPTIONAL, published by other mods, e.g. SkyyCooking for "Cooking"): Function apply(Object[]{UUID,
                    Integer level, Boolean next}) -> java.util.List of String; up to 5 lines are shown on that skill's Stats page
                    ("Boosts right now" when next=false, "Level L+1 adds" when next=true).
    Caps: bridge.maxXpPerCall = the caller's base XP, checked BEFORE the multiplier and the skill-tree bonus on purpose (a guard
    against a broken caller: a Wisdom node must never turn a valid grant into a permanent refusal); bridge.maxXpPerMinute = the XP
    actually queued (after the multiplier and the tree bonus), per player, all bridge sources together, not reset by a profile
    switch - it is the real bound. The vanilla bench / furnace paths are not capped (every event is a real, paid, non-creative craft).
  ACROBATICS FALLS (Skyy): the further you fall WITHOUT dying the more XP. Only a fall whose damage really applied pays: AcroFallSeenSys
  (DamageEventSystem in the INSPECT group = after ApplyDamage) notes FALL damage that is not cancelled and still >= 1 after
  ApplyDamage's rounding, and not while in fluid/swimming; falls() pays it 0.4 s later if the player is alive, not in creative and
  not in water: XP = unreduced fall damage (Damage.getInitialAmount, before armor and the Acrobatics reduction) x 100 / max health
  (vanilla fall damage = percent of max health, so extra max health changes nothing) x acro.fallDamageXp (10), capped per landing
  (acro.fallXpMax 2000) and per 60 s (acro.fallMaxXpPerMinute 3000, its own ring, outside acro.maxXpPerMinute which now only
  covers running, jumping and dodging). Safe no-damage drops pay 0 (acro.fallXpPerBlock / acro.fallMinBlocks are gone). An existing
  xp.properties without acro.fallMaxXpPerMinute is migrated once: the old default fall lines are rewritten (custom values kept).
  COMMANDS: /skills xp <skill> <amount> (admin test helper, requirePermission skyyskills.admin + no groups; raw XP, no multiplier);
  skill args gain alchemy, smithing, cooking. CONFIG: alchemy.*, perk.alchemy.*, smithing.*, bridge.* blocks appended once to an
  existing xp.properties (AlchCfg / SmithCfg / BridgeCfg.ensureDefaults); /skills reload re-reads them.
  TREES BRIDGE (research/Skill-Trees-Spec.md 9.3 / 10; built for SkyyTrees 0.1, generic): skill:fn:xp apply(Object[]{UUID, skill})
  -> Long (total XP, active profile). skill:bonus:<uuid> is read on every award: xp.<skill> (summed over sources, clamped 0..5, the
  fraction paid by chance) raises the XP of bridge.bonus.xpSkills (default Mining, Foraging, Farming, Cooking) that the player EARNS:
  blocks, F-harvest, vanilla bench / furnace crafts, skill:fn:craftxp. XP another mod GRANTS through skill:fn:addxp gets it only for
  bridge.bonus.addxpSkills (default Cooking = SkyyCooking's per-dish XP, which the Cooking tree's Wisdom node boosts); SkyyCollections'
  Mining / Foraging / Farming tier rewards stay exact (Skill-Trees-Spec 9.3 item 2: Wisdom = gathering XP). Never the admin /skills
  xp. Bridge XP gets the bonus in BridgeXp.offer, so bridge.maxXpPerMinute counts it. dd.<skill> adds to the Mining / Foraging
  / Farming double-drop chance (Perks.chanceU, still capped by perk.doubleDropMax). skill:on:gather (ConcurrentHashMap name ->
  Function, created here with putIfAbsent) is called on the world thread after a gathering block / F-harvest paid XP and rolled its
  double drop: Object[]{PlayerRef, Integer row, BlockType, String world, Boolean harvest, Integer x, Integer y, Integer z}.
  skill:fn:drops apply(Object[]{BlockType, Boolean harvest}) -> List (a fresh roll = Perks.breakDrops / harvestDrops; null = cannot be
  reproduced). skill:fn:placed apply(Object[]{String world, Integer x, Integer y, Integer z}) -> Boolean (PlacedStore.contains; null
  = unknown, tracker off). UI: while tree:fn:level is on the bridge, a "Tree" button on the Mining / Foraging / Farming / Cooking rows
  of /skills and "Skill tree" on their Stats pages run /tree <skill> as the player (the tree page replaces ours); Stats line "Skill
  tree: +X% double drops, +Y% XP". Config: bridge.bonus.enabled, bridge.bonus.xpSkills, bridge.bonus.addxpSkills (bridge block of
  xp.properties).
  NOT in 0.4 (on purpose): Cooking grades / graded dishes / cook:fn:* and the Cooking tree's grade bonuses (SkyyCooking reads
  tree:fn:level / tree:fn:bonus itself; SkyyTrees 0.1 publishes no tree:cook:<uuid> map).
0.3.2: per-profile storage (tools/PROFILES-CONTRACT.md). XP, paid markers, the per-class combat XP (Combat.<Class>), perks,
  Acrobatics level and the /skills quiet flag belong to the ACTIVE profile: players/<pkey>.properties, pkey = the contract's pkey()
  helper (SkillStore.pkey: bridge profile:fn:key applied to the UUID). Without SkyyProfiles (or when it answers nothing) pkey =
  uuid.toString() = profile 1, and profile 1's file is the existing players/<uuid>.properties (no migration, behaviour identical to
  0.3.1). In-memory caches DATA / QUIET / DIRTY are keyed by the pkey String (OWNER maps a key back to its UUID for the saved name);
  NAMES (username), PUBLISHED, the chat throttle, the once-per-session hints (TOLD) and the Acrobatics movement tracker stay per
  player (UUID). Bridge values stay UUID keys describing the active profile: skill:<uuid>, skill:fn:level. Every level read goes
  through pkey, so the per-second skyyskill_health / stamina / mana MAX modifiers and the "skills.acrobatics" movement source follow
  the active profile. EPOCH CHECK in the existing once-per-second AcroSys player tick (world thread), BEFORE the Acrobatics flush,
  movement sync and perk tick: profile:epoch:<uuid> differs from the last value seen for that UUID (Perks.EPOCH) -> republish
  skill:<uuid>, drop the Acrobatics tracker's unpaid XP fraction, pending landing / fall note and unshown chat XP (earned on the old
  profile, never credited to the new one), forget the pending +XP chat line and the hints; the same tick then recomputes the
  movement source and the MAX modifiers from the new profile's levels. The class for combat is still class:<uuid> (SkyyClasses
  publishes the active profile's class); while profile:class:<uuid> is published and class:<uuid> does not match it yet (SkyyClasses
  has not caught up with a switch), no combat XP (one hint), no class damage perk and no legacy Combat migration, so nothing lands
  in the wrong class slot. That pause is BOUNDED: a mismatch still there after SkillClass.GRACE_MS (10 s; SkyyClasses 0.1.3
  republishes every 2 s) fails open - one warning in the server log per player per switch, then combat XP, the damage perk and the
  legacy move follow class:<uuid> again (0.3.1 behaviour), so SkyyClasses 0.1.2 (never reads profile:class) or a SkyyClasses bug
  can never pause them forever. DEPLOY PAIRING: with SkyyProfiles, ship SkyyClasses 0.1.3+ (0.1.2 would make every profile switch
  run on the class of the class file after the 10 s grace). /skills top: one row per profile file, profile N >= 2 rows show
  "(profile N)", your rank is your active profile's. The vanilla inventory is never touched for a switch (contract rule 5; double
  drops still go to the live inventory). The first read of a switched-to profile's file happens on the player's world thread in
  that 1 s tick (same as PublishTask: the shared SCHEDULED_EXECUTOR never does player-file I/O); one small file per manual switch.
  Skill args: "shaman" replaces the removed "berserking" in the /skills top|stats help and the unknown-skill message.
  Profiles integration check (2026-09-23, "Semantics of SkyyProfiles 0.1"): an absent profile:epoch is never recorded (absent ->
  value = baseline, not a switch); skill:<uuid> publishes are serialized (SkillStore.PUB, state read inside the lock); player-file
  saves are atomic (ATOMIC_MOVE, retried 5x 20 ms on Windows sharing errors), a failed save stays dirty, and the leaderboard scan
  reads through NIO under the IO lock (java.io.FileInputStream blocked the save's rename on Windows).
0.3.1 (design lock 2026-09-23 night): the Berserker/Berserking class slot becomes the Shaman placeholder (Combat.Shaman, 'Shaman skill');
  slot count stays 10 so saved files and slot indices are unchanged. Old Combat.Berserker XP stays in the file, unread.
Run:   python build_skyyskills_0.4.6.py            -> SkyySkills/SkyySkills-0.4.6.jar
       python build_skyyskills_0.4.6.py --deploy   -> also copies to Mods/SkyySkills.jar and enables it in the HUD mod world
       Deploy with SkyyAccessories 0.3 (movement protocol) and SkyyClasses 0.1.1+ (combat = class skill; without it no combat XP
       at all). SkyyClasses 0.1.1 enables Mage with skill "Sorcery" = CLASS_ROWS below (0.1 had Mage disabled, skill "Magic").
0.3: MAX LEVEL 100 for every skill (Skyy). Levels 1-60 = Hypixel SkyBlock's table, 61-100 continue its +300k step (level 100
     needs 19M XP, 0 -> 100 = 637.7M). An xp.properties whose levels= line is still the old 50-level default is rewritten to the
     100-level table on load (a custom levels= line is kept; at most 100 entries). Player files keep their XP (levels 1-50 are
     unchanged, so nobody's level moves); level-up coins (coinsPerLevel x level) keep paying up to 100. Acrobatics already hits
     Skyy's level-100 targets (x2 speed, +1.5 blocks jump, -50% fall damage) with the 0.2 per-level keys - unchanged.
     STATS PAGE: the "Top 10" button of every /skills row is now "Stats" -> StatsPage: level / 100, XP to next, the boosts the
     skill gives right now (numbers) and what the next level adds (+ its coins), how to earn XP, "< Back" (to /skills) and
     "Top 10" (the old leaderboard view). Also /skills stats <skill>. /skills top <skill> still prints the top 10 in chat.
     GATHERING PERKS (flat layer, perk.* keys appended once to an existing xp.properties): max Health / Stamina / Mana per level
     for any skill (defaults: Mining +0.05 Stamina, Foraging +0.1 Health, Farming +0.25 Health, Combat +0.1 Health per level =
     +5 Stamina / +10 / +25 / +10 Health at 100), applied once per second on the world thread by the Acrobatics player tick as
     EntityStatMap StaticModifier(MAX, ADDITIVE) keys skyyskill_health / skyyskill_stamina / skyyskill_mana (SkyyAccessories
     AccEffects pattern; the modifiers are saved with the player - they are removed again when their amount becomes 0, e.g.
     perk.enabled=false, but NOT when the mod is uninstalled). DOUBLE DROPS: Mining (every block that pays Mining XP), Foraging
     (logs: doubleDropOnly=_Trunk) and Farming (ripe crops, broken or F-harvested) roll level x 0.5% (50% at 100, capped by
     perk.doubleDropMax) to give the block's drops once more, straight into the player's storage/hotbar/backpack
     (Inventory.getCombinedStorageHotbarBackpack + SimpleItemContainer.addOrDropItemStack, dropped at the feet when full).
     The drops are computed exactly like the engine (bytecode 2026-09-23): break = BlockHarvestUtils.getDrops(blockType,
     Breaking.Quantity, Breaking.ItemId, Breaking.DropListId) (BlockHarvestUtils.damageSingleBlock -> performBlockBreak ->
     naturallyRemoveBlock), soft blocks (crops) = getDrops(bt, 1, Soft.ItemId, Soft.DropListId), F-harvest = getDrops(bt, 1,
     Harvest.ItemId, Harvest.DropListId) (FarmingUtil.giveDrops). A drop LIST is rolled again (same odds, not a copy of the
     first roll's result). Never doubled: placed blocks (needs ignorePlaced=true - the placed-block tracker), blocks whose drops
     depend on the tool (a Gathering.Tools entry without State, e.g. Soil_Gravel + pickaxe, shears on plants), blocks with both
     Soft and Breaking drops. "Double drop!" chat line at most once per feedbackMs (perk.doubleDropMessage, /skills quiet).
     CLASS COMBAT (Skyy: "combat will be based on your class"): the Combat row shows your class skill (class:<uuid> /
     class:skill:<uuid> from SkyyClasses; "Combat - choose a class with /class" without one). Combat XP only with a class AND a
     kill made with a weapon SkyyClasses allows for it (bridge class:fn:allowed on the attacker's main-hand item, then the active
     utility item - the Kunai), plus (combat.classWeaponOnly=true) one of the class's own weapons (class:weapons:<Class>), so
     tools / fists / shields earn nothing. No class:fn:allowed (SkyyClasses missing) = no combat XP; each reason is told to the
     player once per session. XP is stored PER CLASS (players/<uuid>.properties "Combat.Archer" .. "Combat.Mage", slots 5-9 with
     their own paid markers), so switching class keeps every class's level. Legacy "Combat" XP (0.1/0.2) moves ONCE to the class
     the player has when 0.3 first sees him with a class while every class slot is still 0 (chat line); after that slot 3 stays 0.
     Combat perk: +0.2% damage per class level with class weapons (CombatDmgSys = DamageEventSystem in the Filter group, Query.any;
     skips cancelled damage - SkyyClasses' DamageLock cancels AND zeroes, so either system order is safe; monsters only unless
     perk.combat.damageVsPlayers=true) and +0.1 max Health per class level. Known edge (same as SkyyClasses): an arrow is judged
     by what the shooter holds when it lands.
     BRIDGE: skill:<uuid> = "Mining:12,Foraging:3,Farming:0,Combat:5,Acrobatics:2,Archery:5" (the five rows, Combat = current class
     skill level, then every class skill that is current or has XP); skill:fn:level also answers class skill names, class names
     and "Combat" (= current class skill). Republished on the player's first Acrobatics tick of a session (SkyyClasses may publish
     class:<uuid> after our 5 s publishOnline already published him, and publishOnline never republishes a published player) and
     whenever the player's class changes.
     COMMANDS (HANDOFF command rules): /skills (alias /skill) + stats <skill> + top <skill> + quiet carry
     setPermissionGroups({"hytale:Adventurer"}); reload = requirePermission("skyyskills.admin") + setPermissionGroups(new String[0])
     (does not inherit the Adventurer group). Skill args: mining foraging farming acrobatics combat archery swordsmanship
     assassination berserking sorcery (or a class name; 3+ letter prefixes work).
0.2 notes:
0.2: ACROBATICS (mcMMO style) as the 5th skill: XP for running (per block, sprint > run > walk), jumping (edge + cooldown + must have
     moved), falling (drop height, or unreduced fall damage survived) and the vanilla dodge (Dodge_Left/Right effect edge); bonuses
     per level: movement speed, jump height, less fall damage, a longer/faster dodge. All rates and bonuses are acro.* keys in
     xp.properties. Anti-exploit: teleport/launch guard, world-change reset, no XP (dodges included) and no dodge push while
     mounted/flying/gliding/climbing/swimming/in fluid/sitting/sleeping/mantling, no XP in creative, no XP for jumping in place,
     cap on all Acrobatics XP in any 60 s (sliding).
     SHARED SKYY MOVEMENT PROTOCOL v1 (tools/skyymove.py has the full spec; SkyyAccessories 0.3 implements the same code):
       bridge "move:<uuid>" -> ConcurrentHashMap source -> Map{layer "flat"|"pct", speed, jump, fallDamage}; each mod posts ONLY its
       own source ("skills.acrobatics" = flat) and every applier sets baseSpeed = default x clamp((1+sum flat)(1+sum pct), 0.3, 5),
       jump height = (h0 + sum flat blocks)(1 + sum pct) -> jumpForce = sqrt(2 g h); fall damage x clamp((1+flat)(1+pct), 0, 2)
       applied ONLY by the owner of "stat:owner:fallDamage" (putIfAbsent; SkyySkills). Idempotent, so several appliers agree;
       5-strike pause only against writers outside the protocol (logged once per player); nothing written while mounted.
       Non-Skyy mods that write MovementSettings directly are NOT coordinated (they win for the player they reset): do not enable
       them in a SkyWynn world; the known ones are named in the server log on the first sync (skyymove.KNOWN_WRITERS).
     Fall reduction = DamageEventSystem in the Filter damage group (runs before ApplyDamage). Dodge boost = Velocity.addInstruction Add.
     Player data array long[2*N]; old player files load with Acrobatics 0. Page: Acrobatics row shows the current bonuses.
0.1 notes:
SkyySkills 0.1 - build script (javassist via jpype). Hypixel-SkyBlock-style skills: Mining, Foraging, Farming, Combat.
Design:
 - XP from BreakBlockEvent (Collections CollSystem pattern). The award is DEFERRED with world.execute(Runnable) and only paid when
   event.isCancelled() is still false (World.execute always queues, so every other system - e.g. SkyyIslands' GuardSystem, whose
   order relative to ours is unknown - has run by then). The engine creates a new BreakBlockEvent per break (BlockHarvestUtils).
 - Block -> skill/xp from Skyy_SkyySkills/xp.properties (written with defaults on first run): block.<id>, prefix.<start>,
   suffix.<end> rules; exact wins, then the longest prefix/suffix. Growth-stage crops resolve to their item id
   (BlockType.getItem().getId(), e.g. Plant_Crop_Wheat_Block) and only pay when the broken state is "StageFinal".
 - Anti-exploit (Hypixel does the same): positions of blocks placed by players (PlaceBlockEvent, also deferred + cancel-checked)
   are remembered per world (Skyy_SkyySkills/placed/<world>.bin, LRU capped); breaking such a block pays no XP. Ripe-checked
   crops are exempt (they are always planted). Creative mode pays no XP (creativeXp=false).
 - Farming also counts F-harvesting a ripe crop (UseBlockEvent.Post on a StageFinal block with a Harvest drop list: eternal
   crops, berry bushes). Post is NOT proof of a harvest: UseBlockInteraction fires it right after InteractionContext.execute(),
   which only pushes the HarvestCrop root onto the chain, and it fires even when the harvest then fails (world gathering
   disabled, broken tool, ...). So HarvestTask polls the block at that position on the world thread (next tick, then every
   100 ms for up to 2 s) and pays only once it has left the ripe state (HarvestCrop resets it to the after-harvest stage or
   EMPTY). One pending check per position; a position pays at most once per harvestCooldownMs (default 5 s, breaking a ripe
   crop shares that gate). Sickle-swing harvesting fires no event and is NOT counted.
 - Combat: DeathSystems.OnDeathSystem subclass (vanilla KillFeed / EndlessLeveling XpEventSystem pattern): onComponentAdded
   (DeathComponent) on an NPCEntity whose DeathComponent.getDeathInfo().getSource() is a Damage.EntitySource (ProjectileSource
   extends it) whose ref has a PlayerRef. XP = NPC max health (EntityStatMap/DefaultEntityStatTypes.getHealth) x perHealth,
   clamped; combat.role.<RoleName>=xp overrides.
 - Levels 0..50, Hypixel per-level XP table (levels= in xp.properties overrides). Level-up: gold chat line + coins through the
   SkyyCoins bridge coins:fn:add (coinsPerLevel x level). Rewards are paid once per level: <Skill>.paid (highest PAID level)
   only moves past a level after coins:fn:add really paid it, so a reward that could not be paid (SkyyCoins missing or
   failing) stays owed and is retried on that skill's next XP gain (a chat line reports the late coins). XP earned before a
   paid marker existed is not back-paid. XP feedback aggregated, at most one chat line per feedbackMs (2s) per player,
   leftovers flushed by a 1s ticker via world.execute; /skills quiet toggles it.
 - /skills (/skill) opens an inline page (row per skill: item icon, name + level, 2-Group progress bar, xp / next, Top 10 button);
   /skills top <skill> prints the top 10 in chat; /skills reload (perm skyyskills.admin) re-reads xp.properties.
 - Persistence Skyy_SkyySkills/players/<uuid>.properties (name, quiet, <Skill>=xp, <Skill>.paid=level), dirty-flush every 10s
   and on shutdown (Collections saver pattern). Bridge: skill:<uuid> = "Mining:12,Foraging:3,Farming:0,Combat:5",
   skill:fn:level = Function apply(Object[]{UUID, String skill}) -> Integer.
 - Threads/locks: no disk I/O runs while the global SkillStore lock is held (files are read before it and written after a
   snapshot taken under it; coin payouts hold only that player's own lock). HytaleServer.SCHEDULED_EXECUTOR is ONE shared
   thread, so the ticker never loads a player file there: an online player whose data is not in memory yet is handed to his
   world thread (PublishTask, FlushTask pattern) to be loaded and published. The 10s dirty-flush still writes on the ticker.
"""
import sys, os, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyymove as MV   # shared Skyy movement protocol (MoveSync class source; also used by SkyyAccessories 0.3)
import skyycfg as CFG   # 0.4.3: the admin config registry kit (tools/CONFIG-CONTRACT.md), generated into this jar
import skyyui as SUI    # 0.4.7: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"
SUI.verify()            # proves every vanilla value / texture / sound the pages use against Assets.zip (read-only); stops the build on drift
KIT_ID = SUI.kit_id()   # "skyyui <version> <blob12>" - in the ready log line

VERSION = "0.4.15"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
CMP = "com.hypixel.hytale.component.Component"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
EST = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
PAGE= "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE= "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EVD = "com.hypixel.hytale.server.core.ui.builder.EventData"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
GM  = "com.hypixel.hytale.protocol.GameMode"
EES = "com.hypixel.hytale.component.system.EntityEventSystem"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB  = "com.hypixel.hytale.component.CommandBuffer"
EV  = "com.hypixel.hytale.component.system.EcsEvent"
CEV = "com.hypixel.hytale.component.system.CancellableEcsEvent"
QRY = "com.hypixel.hytale.component.query.Query"
BBE = "com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent"
PBE = "com.hypixel.hytale.server.core.event.events.ecs.PlaceBlockEvent"
UBE = "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent"
UBP = "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Post"
BTY = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType"
SDT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.StateData"
BGA = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
V3I = "org.joml.Vector3i"
ODS = "com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$OnDeathSystem"
DTH = "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent"
DMG = "com.hypixel.hytale.server.core.modules.entity.damage.Damage"
DES = "com.hypixel.hytale.server.core.modules.entity.damage.Damage.EntitySource"   # javassist source name (dotted nested)
NPC = "com.hypixel.hytale.server.npc.entities.NPCEntity"
ESM = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"
ESV = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue"
DST = "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes"
CHS = "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore"
BSC = "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection"
BTM = "com.hypixel.hytale.assetstore.map.BlockTypeAssetMap"
# 0.2 Acrobatics API (verified with reflect.py / bcfull.py against HytaleServer.jar, see tools/skills_0_2_patch.py)
ETS = "com.hypixel.hytale.component.system.tick.EntityTickingSystem"
MSC = "com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent"
MVT = "com.hypixel.hytale.protocol.MovementStates"
TRC = "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent"
V3D = "org.joml.Vector3d"
VEL = "com.hypixel.hytale.server.core.modules.physics.component.Velocity"
VCF = "com.hypixel.hytale.server.core.modules.splitvelocity.VelocityConfig"
CVT = "com.hypixel.hytale.protocol.ChangeVelocityType"
ECC = "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent"
EFX = "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect"
DCS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageCause"
DEVS= "com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem"
DMM = "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule"
SYG = "com.hypixel.hytale.component.SystemGroup"
# 0.3 perks / class combat API (verified with reflect.py / bcfull.py against HytaleServer.jar 2026-09-23, see tools/skills_0_3_patch.py)
BHU = "com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils"
BBD = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockBreakingDropType"
SBD = "com.hypixel.hytale.server.core.asset.type.blocktype.config.SoftBlockDropType"
HDT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.HarvestingDropType"
BTD = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering$BlockToolData"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
INVC= "com.hypixel.hytale.server.core.inventory.InventoryComponent"
UTIL= "com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility"
SIC = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
CAC = "com.hypixel.hytale.component.ComponentAccessor"
MOD = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier"
SMO = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier"
MTG = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget"
CAL = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType"
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
# 0.4 Alchemy / Smithing API (verified with tools/dev reflect.py + bcfull.py against HytaleServer.jar, 2026-09-24)
CRE = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent"
CREP= "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Post"   # '$' form for the class literal, like UBP
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
BRQ = "com.hypixel.hytale.protocol.BenchRequirement"          # public fields id, requiredTierLevel, type
MQ  = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"
AEE = "com.hypixel.hytale.server.core.entity.effect.ActiveEntityEffect"
OVB = "com.hypixel.hytale.server.core.asset.type.entityeffect.config.OverlapBehavior"
ICE = "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent"
MVTX= "com.hypixel.hytale.server.core.inventory.transaction.MoveTransaction"   # (MVT is MovementStates)
MVY = "com.hypixel.hytale.server.core.inventory.transaction.MoveType"
LTX = "com.hypixel.hytale.server.core.inventory.transaction.ListTransaction"
IST = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction"
SLT = "com.hypixel.hytale.server.core.inventory.transaction.SlotTransaction"
CIC = "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer"
PBW = "com.hypixel.hytale.builtin.crafting.window.ProcessingBenchWindow"
BWN = "com.hypixel.hytale.server.core.entity.entities.player.windows.BlockWindow"
WMG = "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager"
BEN = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench"
CRPL= "com.hypixel.hytale.builtin.crafting.CraftingPlugin"
BTP = "com.hypixel.hytale.protocol.BenchType"
CMGR= "com.hypixel.hytale.server.core.command.system.CommandManager"      # 0.4 trees bridge: the Tree buttons run /tree <skill>
# 0.4.2 felled trees (tools/dev reflect.py + bcfull.py against HytaleServer.jar 2026-09-24; research/Tree-Fall-Spec.md 1.3 / 2.4 / 3.1)
WES = "com.hypixel.hytale.component.system.WorldEventSystem"                  # C(Class), handle(Store, CommandBuffer, EcsEvent)
EBE = "com.hypixel.hytale.server.core.event.events.ecs.EnvironmentBreakBlockEvent"   # getTargetBlock(), getBlockType()
BPH = "com.hypixel.hytale.server.core.blocktype.component.BlockPhysics"       # chunk-section component: isDeco(x, y, z)
PDT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.PhysicsDropType"
CKU = "com.hypixel.hytale.math.util.ChunkUtil"                                # BITS = 5 (32-block sections), HEIGHT = 320

for c, m in ((BBE, "getBlockType"), (BBE, "getTargetBlock"), (PBE, "getTargetBlock"), (UBE, "getBlockType"), (CEV, "isCancelled"),
             (BTY, "getId"), (BTY, "getItem"), (BTY, "getStateForBlock"), (BTY, "getState"), (BTY, "getGathering"), (SDT, "getStateNames"),
             (BGA, "getHarvest"), (ITM, "getId"), (V3I, "x"), (V3I, "y"), (V3I, "z"),
             (ACH, "getReferenceTo"), (ST, "getExternalData"), (ST, "getComponent"), (EST, "getWorld"), (WLD, "execute"), (WLD, "getName"),
             (ODS, "componentType"), (ODS, "onComponentSet"), (ODS, "onComponentRemoved"), ("com.hypixel.hytale.component.system.RefChangeSystem", "onComponentAdded"),
             (DTH, "getDeathInfo"), (DMG, "getSource"), ("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource", "getRef"),
             (REF, "isValid"), (REF, "getStore"), (NPC, "getComponentType"), (NPC, "getRoleName"),
             (ESM, "getComponentType"), (ESM, "get"), (ESV, "getMax"), (DST, "getHealth"),
             (PLA, "getGameMode"), (PLA, "getPageManager"), (GM, "Creative"),
             (UNI, "getPlayers"), (UNI, "getPlayer"), (UNI, "getWorld"), (PR, "getWorldUuid"), (PR, "getUsername"), (PR, "hasPermission"),
             (MSG, "raw"), (MSG, "color"), (PAGE, "rebuild"), (EVD, "of"), (HSV, "SCHEDULED_EXECUTOR"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "addSubCommand"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "addAliases"),
             ("com.hypixel.hytale.component.Archetype", "empty"),
             (UBE, "getTargetBlock"), (WLD, "getChunkStore"), (CHS, "getChunkSectionReferenceAtBlock"), (CHS, "getStore"),
             (BSC, "get"), (BSC, "getComponentType"), (BTY, "getAssetMap"), (BTM, "getAsset"),
             ("java.util.concurrent.ScheduledExecutorService", "schedule"), ("java.util.concurrent.ConcurrentHashMap", "putIfAbsent"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)
for c, m in ((ETS, "tick"), (MSC, "getComponentType"), (MSC, "getMovementStates"), (MVT, "jumping"), (MVT, "onGround"), (MVT, "sprinting"),
             (MVT, "running"), (MVT, "walking"), (MVT, "horizontalIdle"), (MVT, "idle"), (MVT, "crouching"), (MVT, "sliding"), (MVT, "mounting"), (MVT, "flying"), (MVT, "gliding"),
             (MVT, "climbing"), (MVT, "inFluid"), (MVT, "swimming"), (MVT, "sitting"), (MVT, "sleeping"), (MVT, "mantling"),
             (TRC, "getComponentType"), (TRC, "getPosition"), (V3D, "x"), (V3D, "y"), (V3D, "z"),
             (VEL, "getComponentType"), (VEL, "getClientVelocity"), (VEL, "addInstruction"), (CVT, "Add"),
             (ECC, "getComponentType"), (ECC, "hasEffect"), (EFX, "getAssetMap"), ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getIndex"),
             (DMG, "getCause"), (DMG, "getAmount"), (DMG, "setAmount"), (DMG, "getInitialAmount"), (DCS, "FALL"), (DCS, "getId"),
             (DMM, "get"), (DMM, "getFilterDamageGroup"), (ESV, "get"), (PLA, "isWaitingForClientReady"), (CB, "getComponent"),
             ("com.hypixel.hytale.component.system.ISystem", "getGroup")):
    B.probe(pool, c, m)
MV.probe(B, pool)
for c, m in ((BHU, "getDrops"), (BGA, "getBreaking"), (BGA, "getSoft"), (BGA, "isSoft"), (BGA, "getToolData"), (BGA, "getHarvest"),
             (BBD, "getQuantity"), (BBD, "getItemId"), (BBD, "getDropListId"), (SBD, "getItemId"), (SBD, "getDropListId"),
             (HDT, "getItemId"), (HDT, "getDropListId"), (BTD, "getStateId"), (IS, "getItemId"), (IS, "isEmpty"), (IS, "getQuantity"),
             (INVC, "getItemInHand"), (UTIL, "getComponentType"), (UTIL, "getActiveItem"), (PLA, "getInventory"),
             (INV, "getCombinedStorageHotbarBackpack"), (SIC, "addOrDropItemStack"), (PR, "getReference"), (REF, "getStore"),
             (ESM, "putModifier"), (ESM, "removeModifier"), (ESM, "getModifier"), (DST, "getStamina"), (DST, "getMana"),
             (SMO, "getAmount"), (MTG, "MAX"), (CAL, "ADDITIVE"), (QRY, "any"), (DMG, "isCancelled"), (CAC, "getComponent"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"),
             (AC, "setPermissionGroups"), (AC, "requirePermission"), (AC, "addSubCommand"), (AC, "withRequiredArg"), (AC, "addAliases")):
    B.probe(pool, c, m)

for c, m in ((CRE, "getCraftedRecipe"), (CRE, "getQuantity"), (CRE, "isCancelled"), (CRR, "getTimeSeconds"), (CRR, "getPrimaryOutput"),
             (CRR, "getBenchRequirement"), (CRR, "getId"), (CRR, "getAssetMap"), (CRR, "getInput"), (MQ, "getItemId"), (MQ, "getQuantity"),
             (BRQ, "id"), (BRQ, "requiredTierLevel"), (ECC, "getActiveEffects"), (ECC, "addEffect"), (AEE, "getRemainingDuration"),
             (AEE, "isInfinite"), (EFX, "getDuration"), (EFX, "isDebuff"), (EFX, "getAssetMap"),
             ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getAsset"), (OVB, "EXTEND"),
             ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset"), (ICE, "getTransaction"), (MVTX, "getMoveType"),
             (MVTX, "getOtherContainer"), (MVTX, "getRemoveTransaction"), (MVTX, "getAddTransaction"), (MVTX, "succeeded"),
             (MVY, "MOVE_TO_SELF"), (LTX, "getList"), (IST, "getSlotTransactions"), (SLT, "getSlot"), (SLT, "getSlotBefore"),
             (SLT, "getSlotAfter"), (CIC, "getContainer"), (CIC, "getContainerForSlot"), (CIC, "getContainersSize"),
             (PBW, "getItemContainer"), (BWN, "getBlockType"), (WMG, "getWindows"), (PLA, "getWindowManager"), (BTY, "getBench"),
             (BEN, "getId"), (CRPL, "getBenchRecipes"), (BTP, "Processing"), (DMM, "getInspectDamageGroup"), (IS, "isEmpty")):
    B.probe(pool, c, m)
# 0.4 trees bridge (CommandManager.handleCommand(CommandSender, String) - PlayerRef is a CommandSender, reflect.py)
for c, m in ((CMGR, "get"), (CMGR, "handleCommand"), ("java.util.Map", "putIfAbsent"), ("java.lang.Double", "isNaN")):
    B.probe(pool, c, m)
for c, m in ((WES, "handle"), (EBE, "getTargetBlock"), (EBE, "getBlockType"), (BPH, "getComponentType"), (BPH, "isDeco"),
             (BGA, "getPhysics"), (PDT, "getItemId"), (PDT, "getDropListId"), (CKU, "BITS"), (CKU, "HEIGHT"), (PBE, "getItemInHand"),
             (BHU, "getDrops"), (WLD, "getChunkStore"), (PR, "getWorldUuid"), (UNI, "getWorld"), ("java.util.concurrent.ConcurrentHashMap", "remove"),
             ("java.lang.System", "arraycopy"), ("java.util.Arrays", "asList")):
    B.probe(pool, c, m)
# 0.4.2 stage 2: double jump (research/Double-Jump-Spec.md 1.4 / 3.2). MMG / MVS / PHC are tools/skyymove.py's names.
MMG = MV.MMG
MVS = MV.MVS
PHC = MV.PHC
MCF = "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementConfig"   # asset: getMinFallSpeedToEngageRoll()
GPC = "com.hypixel.hytale.server.core.asset.type.gameplay.GameplayConfig"
PCF = "com.hypixel.hytale.server.core.asset.type.gameplay.PlayerConfig"
ESTT= "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType"
SEV = "com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent"
SNU = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
SCAT= "com.hypixel.hytale.protocol.SoundCategory"
PTU = "com.hypixel.hytale.server.core.universe.world.ParticleUtil"
ILT = "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap"
for c, m in ((MVT, "extraJumpsUsed"), (MVT, "crouching"), (MVT, "jumping"), (MVT, "onGround"), (CVT, "Set"), (MMG, "getComponentType"),
             (MMG, "getSettings"), (MVS, "jumpForce"), (MVS, "fallJumpForce"), (PHC, "GRAVITY_ACCELERATION"), (MCF, "getAssetMap"),
             (MCF, "getMinFallSpeedToEngageRoll"), (WLD, "getGameplayConfig"), (GPC, "getPlayerConfig"), (PCF, "getMovementConfigIndex"),
             (ESM, "subtractStatValue"), (ESM, "setStatValue"), (DST, "getStamina"), (ESTT, "getAssetMap"), (SEV, "getAssetMap"),
             (SNU, "playSoundEvent3d"), (PTU, "spawnParticleEffect"), (SCAT, "SFX"), (ILT, "getAsset"), (ILT, "getIndex"),
             (VEL, "addInstruction"), (VEL, "getClientVelocity"), (PLA, "getGameMode"), (PR, "hasPermission"),
             # party combat XP: members by UUID -> PlayerRef -> Ref in the killer's store, their position
             (UNI, "getPlayer"), (PR, "getReference"), (PR, "isValid"), (REF, "getStore"), (TRC, "getPosition"), (PLA, "isWaitingForClientReady")):
    B.probe(pool, c, m)
# 0.4.5 crossbows stay loaded (research/Crossbow-Loaded-Spec.md 1.8 / 3.9; tools/dev reflect.py + bcfull.py against HytaleServer.jar
# 2026-09-25): the hotbar switch event, the Ammo stat, the hotbar and the arrow payment (vanilla ModifyInventoryInteraction's call)
ISAS = "com.hypixel.hytale.server.core.event.events.ecs.InventorySetActiveSlotEvent"
HOTB = "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar"
STOR = "com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage"
BKPK = "com.hypixel.hytale.server.core.inventory.InventoryComponent$Backpack"
ASIC = "com.hypixel.hytale.server.core.inventory.ActiveSlotInventoryComponent"
ICON = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
for c, m in ((ISAS, "getInventorySectionId"), (ISAS, "getPreviousSlot"), (ISAS, "getNewSlot"), (ESM, "get"), (ESM, "setStatValue"),
             (ESV, "get"), (ESV, "getMax"), (DST, "getAmmo"), (INVC, "getCombined"), (INVC, "HOTBAR_STORAGE_BACKPACK"),
             (INVC, "HOTBAR_SECTION_ID"), (INVC, "DEFAULT_HOTBAR_CAPACITY"), (HOTB, "getComponentType"), (STOR, "getComponentType"),
             (BKPK, "getComponentType"), (ASIC, "getActiveSlot"), (HOTB, "getActiveSlot"), (HOTB, "getInventory"),
             (ICON, "removeItemStack"), (ICON, "getItemStack"), (ICON, "getCapacity"), (CIC, "getCapacity"), (CIC, "getItemStack"),
             (IS, "isEquivalentType"), (IS, "getItemId"), (IS, "getQuantity"), (IS, "isEmpty"), (IST, "succeeded"),
             (DTH, "getComponentType"), (PLA, "getGameMode"), (GM, "Creative"), (PR, "hasPermission"), (ACH, "getReferenceTo"),
             (ITM, "getAssetMap"), ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAssetMap")):
    B.probe(pool, c, m)
# exact signatures (a renamed or re-typed parameter fails here, not in game)
for c, m, d in ((ISAS, "getInventorySectionId", "()I"), (ISAS, "getPreviousSlot", "()I"), (ISAS, "getNewSlot", "()B"),
                (ESM, "get", "(I)L" + ESV.replace(".", "/") + ";"), (ESM, "setStatValue", "(IF)F"), (ESV, "get", "()F"), (ESV, "getMax", "()F"),
                (DST, "getAmmo", "()I"), (ASIC, "getActiveSlot", "()B"),
                (INVC, "getCombined", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";[Lcom/hypixel/hytale/component/ComponentType;)L" + CIC.replace(".", "/") + ";"),
                (ICON, "removeItemStack", "(L" + IS.replace(".", "/") + ";ZZ)L" + IST.replace(".", "/") + ";"),
                (ICON, "getItemStack", "(S)L" + IS.replace(".", "/") + ";"), (ICON, "getCapacity", "()S"),
                (IS, "isEquivalentType", "(L" + IS.replace(".", "/") + ";)Z"),
                (ITM, "getAssetMap", "()Lcom/hypixel/hytale/assetstore/map/DefaultAssetMap;"),
                ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAssetMap", "()Ljava/util/Map;")):
    try:
        pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
# the event's hotbar section id is -1 (spec 1.5) and the hotbar fits the 16 kept-load slots (spec 2.3)
_hsid = pool.get(INVC).getField("HOTBAR_SECTION_ID").getConstantValue()
_hcap = pool.get(INVC).getField("DEFAULT_HOTBAR_CAPACITY").getConstantValue()
assert _hsid is not None and int(_hsid) == -1, "InventoryComponent.HOTBAR_SECTION_ID is %r, not -1" % (_hsid,)
assert _hcap is not None and 1 <= int(_hcap) <= 16, "InventoryComponent.DEFAULT_HOTBAR_CAPACITY is %r (Xbow keeps 16 slots)" % (_hcap,)
# 0.4.6 (research/Overall-Level-Spec.md 4.12 + the crossbow extras; tools/dev reflect.py + bcfull.py against HytaleServer.jar 2026-09-28):
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
# 0.4.12 Mana regen in combat (research/Mana-Cost-And-Regen-Research.md 2.1-2.2; the SkyyAccessories 0.5 Stamina Regen calls + the single
# condition, read in HytaleServer.jar bytecode 2026-10-02): the Mana value's regen entries, each condition evaluated on its own
# (Condition.eval = eval0 != inverse; NoDamageTakenCondition.eval0 = now - DamageDataComponent.lastDamageTime >= Delay), the store's clock
RGV = "com.hypixel.hytale.server.core.modules.entitystats.RegeneratingValue"
RGN = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating"
RGT = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType$Regenerating$RegenType"
CND = "com.hypixel.hytale.server.core.modules.entity.condition.Condition"
NDT = "com.hypixel.hytale.server.core.modules.entity.condition.NoDamageTakenCondition"
TMR = "com.hypixel.hytale.server.core.modules.time.TimeResource"
DDC = "com.hypixel.hytale.server.core.entity.damage.DamageDataComponent"
CHG = "com.hypixel.hytale.server.core.modules.entity.condition.ChargingCondition"   # 0.4.13 fix: Mana keeps regenerating while charging
# 0.4.14 (tools/skills_0_4_14_patch.py): roll landings, kill XP by mob level, sickle swings
PIN  = "com.hypixel.hytale.server.core.modules.entity.player.PlayerInput"
PISM = "com.hypixel.hytale.server.core.modules.entity.player.PlayerInput$SetMovementStates"
PISV = "com.hypixel.hytale.server.core.modules.entity.player.PlayerInput$SetClientVelocity"
FDP  = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$FallDamagePlayers"
SDEP = "com.hypixel.hytale.component.dependency.SystemDependency"
DORD = "com.hypixel.hytale.component.dependency.Order"
UUC  = "com.hypixel.hytale.server.core.entity.UUIDComponent"
IPE  = "com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent"
IDL  = "com.hypixel.hytale.server.core.asset.type.item.config.ItemDropList"
IDR  = "com.hypixel.hytale.server.core.asset.type.item.config.ItemDrop"
IDC  = "com.hypixel.hytale.server.core.asset.type.item.config.container.ItemDropContainer"
FUT  = "com.hypixel.hytale.builtin.adventure.farming.FarmingUtil"
WCFG = "com.hypixel.hytale.server.core.universe.world.WorldConfig"   # fix round F2: the per-world fall damage switch (World.getWorldConfig)
for c, m in ((ESV, "getRegeneratingValues"), (RGV, "getRegenerating"), (RGN, "getRegenType"), (RGN, "getAmount"), (RGN, "getInterval"),
             (RGN, "getConditions"), (RGT, "ADDITIVE"), (CND, "eval"), (NDT, "eval0"), (TMR, "getResourceType"), (TMR, "getNow"),
             (ST, "getResource"), (ESV, "get"), (ESV, "getMax"), (ESM, "addStatValue"), (ESTT, "getRegenerating"), (DDC, "getLastDamageTime"),
             (DDC, "getComponentType"), (DST, "getMana")):
    B.probe(pool, c, m)
for c, m, d in ((CND, "eval", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";Ljava/time/Instant;)Z"),
                (RGN, "getConditions", "()[L" + CND.replace(".", "/") + ";"),
                (ESV, "getRegeneratingValues", "()[L" + RGV.replace(".", "/") + ";"),
                (RGV, "getRegenerating", "()L" + RGN.replace(".", "/") + ";"),
                (TMR, "getNow", "()Ljava/time/Instant;"), (DDC, "getLastDamageTime", "()Ljava/time/Instant;"),
                (ESTT, "getRegenerating", "()[L" + RGN.replace(".", "/") + ";")):
    try:
        pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
assert pool.get(NDT).subclassOf(pool.get(CND)), "NoDamageTakenCondition is no longer a Condition"
# 0.4.13 (skill:fn:combat): the Delay is asked from the condition (eval0 at last hit + d), the countdown = Delay - (now - last hit); both rest
# on NoDamageTakenCondition.eval0 = TimeUtil.compareDifference(DamageDataComponent.getLastDamageTime(), now, this.delay) >= 0 (bytecode,
# HytaleServer.jar 2026-10-02) and on the hit being stamped with the world's TimeResource clock (DamageSystems$TrackLastDamage)
for c, m, d in ((CND, "eval0", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";Ljava/time/Instant;)Z"),
                (NDT, "eval0", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";Ljava/time/Instant;)Z")):
    try:
        pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
import jpype as _jp
def _bc_lines(cls, meth):
    """the instructions of every declared method of cls named meth (bridge methods included), as InstructionPrinter text"""
    _ip, _out = _jp.JClass("javassist.bytecode.InstructionPrinter"), []
    for _mm in pool.get(cls).getDeclaredMethods():
        if str(_mm.getName()) != meth or _mm.getMethodInfo().getCodeAttribute() is None:
            continue
        _it, _cp = _mm.getMethodInfo().getCodeAttribute().iterator(), _mm.getMethodInfo().getConstPool()
        while _it.hasNext():
            _out.append(str(_ip.instructionString(_it, _it.next(), _cp)))
    return _out
_ndl = _bc_lines(NDT, "eval0")
assert (any(DDC + ".getLastDamageTime" in x for x in _ndl) and any("com.hypixel.hytale.common.util.TimeUtil.compareDifference" in x for x in _ndl)
        and any(NDT + ".delay" in x for x in _ndl) and any(x.startswith("iflt") for x in _ndl)), \
    "NoDamageTakenCondition.eval0 is no longer compareDifference(lastDamageTime, now, delay) >= 0 - re-check skill:fn:combat's countdown"
_tll = _bc_lines("com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$TrackLastDamage", "handle")
assert any(TMR + ".getNow" in x for x in _tll) and any(DDC + ".setLastDamageTime" in x for x in _tll), \
    "DamageSystems$TrackLastDamage no longer stamps the hit with TimeResource.getNow - the combat clock would differ"
# 0.4.13 FIX F1 (cross-check 2026-10-02): a world's clock = real time x its time dilation, so a stamp from another world is carried as REAL
# time: TickingThread.run hands tick() the measured System.nanoTime() step / 1e9, World.tick multiplies it by
# TimeResource.getTimeDilationModifier() before Store.tick, TimeSystem.tick adds (long) (dt x 1e9) ns to TimeResource.now (bytecode,
# HytaleServer.jar 2026-10-02; the dilation is not saved: 1.0 after a restart). Every engine member the carry calls must stay public.
_ttr = _bc_lines("com.hypixel.hytale.server.core.util.thread.TickingThread", "run")
assert (any("java.lang.System.nanoTime" in x for x in _ttr) and any("float 1.0E9" in x for x in _ttr) and any(x.strip() == "fdiv" for x in _ttr)
        and any("com.hypixel.hytale.server.core.util.thread.TickingThread.tick((F)V)" in x for x in _ttr)), \
    "TickingThread.run no longer ticks with the measured System.nanoTime() step - re-check the clock rate the stamp carry converts with"
_wtk = _bc_lines(WLD, "tick")
assert (any(TMR + ".getTimeDilationModifier" in x for x in _wtk) and any(x.strip() == "fmul" for x in _wtk)
        and any("com.hypixel.hytale.component.Store.tick((F)V)" in x for x in _wtk)), \
    "World.tick no longer scales dt by TimeResource's time dilation - re-check the stamp carry's conversion"
_tsk = _bc_lines("com.hypixel.hytale.server.core.modules.time.TimeSystem", "tick")
assert (any("float 1.0E9" in x for x in _tsk) and any(TMR + ".add((JLjava/time/temporal/TemporalUnit;)V)" in x for x in _tsk)
        and any("java.time.temporal.ChronoUnit.NANOS" in x for x in _tsk)), \
    "TimeSystem.tick no longer adds dt x 1e9 ns to TimeResource.now - re-check the world clock"
# the Charging condition (Mana.json: Charging, Inverse) reads the charge stamp the same way: eval0 = a charging interaction runs, or
# TimeUtil.compareDifference(lastChargeTime, now, delay) <= 0 - its stamp is carried too; while an INVERSE Charging is the only failing
# condition (with or without NoDamageTaken) SkyySkills refills what vanilla withholds
assert pool.get(CHG).subclassOf(pool.get(CND)), "ChargingCondition is no longer a Condition"
_chl = _bc_lines(CHG, "eval0")
assert any(DDC + ".getLastChargeTime" in x for x in _chl) and any("com.hypixel.hytale.common.util.TimeUtil.compareDifference" in x for x in _chl), \
    "ChargingCondition.eval0 no longer reads DamageDataComponent.lastChargeTime - re-check the charging refill and the stamp carry"
_JMd = _jp.JClass("javassist.Modifier")
for c, m, d in ((DDC, "getLastDamageTime", "()Ljava/time/Instant;"), (DDC, "setLastDamageTime", "(Ljava/time/Instant;)V"),
                (DDC, "getLastCombatAction", "()Ljava/time/Instant;"), (DDC, "setLastCombatAction", "(Ljava/time/Instant;)V"),
                (DDC, "getLastChargeTime", "()Ljava/time/Instant;"), (DDC, "setLastChargeTime", "(Ljava/time/Instant;)V"),
                (TMR, "getNow", "()Ljava/time/Instant;"), (TMR, "getTimeDilationModifier", "()F"),
                (CND, "eval0", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";Ljava/time/Instant;)Z"),
                (CHG, "eval0", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";Ljava/time/Instant;)Z"),
                (ST, "getExternalData", "()Ljava/lang/Object;"), (EST, "getWorld", "()L" + WLD.replace(".", "/") + ";"),
                (WLD, "getName", "()Ljava/lang/String;")):
    try:
        _mm = pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
    assert _JMd.isPublic(_mm.getModifiers()) and _JMd.isPublic(pool.get(c).getModifiers()), \
        "%s.%s is no longer public - the stamp carry / charging refill may not call it (protected engine members only from a subclass)" % (c, m)
# 0.4.14 (tools/skills_0_4_14_patch.py): the engine facts the four new features rest on - HytaleServer.jar bytecode, read 2026-10-03; any
# drift stops the build instead of a feature going quiet. Every engine member the new code calls must be public (the engine-access rule).
for c, m in ((PIN, "getComponentType"), (PIN, "getMovementUpdateQueue"), (PISM, "movementStates"), (PISV, "getVelocity"), (MVT, "rolling"),
             (MVT, "onGround"), (MVT, "inFluid"), (MCF, "getMinFallSpeedToEngageRoll"), (MCF, "getMaxFallSpeedRollFullMitigation"),
             (MCF, "getMaxFallSpeedToEngageRoll"), (MCF, "getFallDamagePartialMitigationPercent"), (MCF, "getAssetMap"), (PLA, "getCurrentFallDistance"),
             (SDEP, "getSystemClass"), (DORD, "BEFORE"), (UUC, "getComponentType"), (UUC, "getUuid"), (IPE, "getItemStack"), (IPE, "isCancelled"),
             (IDL, "getAssetMap"), (IDL, "getContainer"), (IDR, "getItemId"), (IDC, "getAllDrops"), (BTM, "getNextIndex"), (BTM, "getAsset"),
             (HDT, "getDropListId"), (HDT, "getItemId"), (BBE, "getItemInHand"), (INVC, "getItemInHand"), (QRY, "and"), (WLD, "getGameplayConfig"),
             (GPC, "getPlayerConfig"), (PCF, "getMovementConfigIndex"), (WLD, "getWorldConfig"), (WCFG, "isFallDamageEnabled")):
    B.probe(pool, c, m)
_JM14 = _jp.JClass("javassist.Modifier")
for c, m, d in ((PIN, "getMovementUpdateQueue", "()Ljava/util/List;"), (PIN, "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"),
                (PISM, "movementStates", "()L" + MVT.replace(".", "/") + ";"), (PISV, "getVelocity", "()L" + V3D.replace(".", "/") + ";"),
                (PLA, "getCurrentFallDistance", "()D"), (MCF, "getMinFallSpeedToEngageRoll", "()F"), (MCF, "getMaxFallSpeedRollFullMitigation", "()F"),
                (MCF, "getMaxFallSpeedToEngageRoll", "()F"), (MCF, "getFallDamagePartialMitigationPercent", "()F"),
                (UUC, "getUuid", "()Ljava/util/UUID;"), (UUC, "getComponentType", "()Lcom/hypixel/hytale/component/ComponentType;"),
                (IPE, "getItemStack", "()L" + IS.replace(".", "/") + ";"), (IPE, "isCancelled", "()Z"),
                (IDL, "getContainer", "()L" + IDC.replace(".", "/") + ";"), (IDC, "getAllDrops", "(Ljava/util/List;)Ljava/util/List;"),
                (IDR, "getItemId", "()Ljava/lang/String;"), (BTM, "getNextIndex", "()I"), (BBE, "getItemInHand", "()L" + IS.replace(".", "/") + ";"),
                (INVC, "getItemInHand", "(L" + CAC.replace(".", "/") + ";L" + REF.replace(".", "/") + ";)L" + IS.replace(".", "/") + ";"),
                (QRY, "and", "([L" + QRY.replace(".", "/") + ";)Lcom/hypixel/hytale/component/query/AndQuery;"),
                (WLD, "getWorldConfig", "()L" + WCFG.replace(".", "/") + ";"), (WCFG, "isFallDamageEnabled", "()Z")):
    try:
        _mm = pool.get(c).getMethod(m, d)
    except Exception as _e:
        raise SystemExit("API signature probe failed: %s.%s%s (%s)" % (c, m, d, _e))
    assert _JM14.isPublic(_mm.getModifiers()) and _JM14.isPublic(pool.get(c).getModifiers()), "%s.%s is no longer public" % (c, m)
for c, f in ((MVT, "rolling"), (MVT, "onGround"), (MVT, "inFluid"), (DORD, "BEFORE")):
    assert _JM14.isPublic(pool.get(c).getField(f).getModifiers()), "%s.%s is no longer a public field" % (c, f)
assert _JM14.isPublic(pool.get(SDEP).getConstructor("(L" + DORD.replace(".", "/") + ";Ljava/lang/Class;)V").getModifiers()), "SystemDependency(Order, Class) is not public"
assert pool.get("com.hypixel.hytale.component.ComponentType").subtypeOf(pool.get(QRY)), "ComponentType is no longer a Query"
def _ci_lines(cls):
    """the instructions of the class initializer of cls"""
    _ip, _out = _jp.JClass("javassist.bytecode.InstructionPrinter"), []
    _ci = pool.get(cls).getClassInitializer()
    if _ci is None:
        return _out
    _it, _cp = _ci.getMethodInfo().getCodeAttribute().iterator(), _ci.getMethodInfo().getConstPool()
    while _it.hasNext():
        _out.append(str(_ip.instructionString(_it, _it.next(), _cp)))
    return _out
# (2) ROLL LANDINGS: FallDamagePlayers.tick = the queue walk RollSys replays (speed from SetClientVelocity, the first onGround landing while
# falling, min speed, not in fluid, floor(maxHealth / 100 x ((0.58f x (speed - min))^2 + 10)), the rolling mitigation, the fall distance reset)
_fdp = _bc_lines(FDP, "tick")
for _need in (PIN + ".getMovementUpdateQueue", PISV + ".getVelocity", PISM + ".movementStates", MVT + ".onGround", MVT + ".inFluid", MVT + ".rolling",
              PLA + ".getCurrentFallDistance", PLA + ".setCurrentFallDistance", MCF + ".getMinFallSpeedToEngageRoll",
              MCF + ".getMaxFallSpeedRollFullMitigation", MCF + ".getMaxFallSpeedToEngageRoll", MCF + ".getFallDamagePartialMitigationPercent",
              "double 0.5799999833106995", "double 2.0", "double 10.0", "double 100.0", "java.lang.Math.pow", "java.lang.Math.floor",
              "DamageSystems.executeDamage", "Velocity.getClientVelocity", "EntityStatValue.getMax"):
    assert any(_need in x for x in _fdp), "DamageSystems$FallDamagePlayers.tick no longer has %s - re-check RollSys (roll landings)" % _need
_fdc = _ci_lines(FDP)
assert (any(DORD + ".BEFORE" in x for x in _fdc) and any("PlayerSystems$ProcessPlayerInput" in x for x in _fdc)
        and any(SDEP + ".<init>" in x for x in _fdc) and any(PIN + ".getComponentType" in x for x in _fdc)), \
    "FallDamagePlayers no longer runs BEFORE ProcessPlayerInput on PlayerInput - RollSys could see a consumed queue"
assert any("getGatherDamageGroup" in x for x in _bc_lines(FDP, "getGroup")), "FallDamagePlayers left the gather damage group"
# fix round F2: the store-level FallDamagePlayers.tick(F, I, Store) = World.getWorldConfig().isFallDamageEnabled() first, return when it is off,
# else the per-entity ticks - a world with fall damage off processes NO landing; RollSys.fallDamageOn asks the same switch
_fds = [_mm for _mm in pool.get(FDP).getDeclaredMethods() if str(_mm.getName()) == "tick" and str(_mm.getSignature()) == "(FILcom/hypixel/hytale/component/Store;)V"]
assert len(_fds) == 1 and _fds[0].getMethodInfo().getCodeAttribute() is not None, "FallDamagePlayers no longer declares tick(float, int, Store)"
_fdsi, _fdsc, _fdsl = _fds[0].getMethodInfo().getCodeAttribute().iterator(), _fds[0].getMethodInfo().getConstPool(), []
while _fdsi.hasNext():
    _fdsl.append(str(_jp.JClass("javassist.bytecode.InstructionPrinter").instructionString(_fdsi, _fdsi.next(), _fdsc)))
_fdsw = [i for i, x in enumerate(_fdsl) if WCFG + ".isFallDamageEnabled" in x]
assert (len(_fdsw) == 1 and any(WLD + ".getWorldConfig" in x for x in _fdsl[:_fdsw[0]]) and _fdsl[_fdsw[0] + 1].split(":")[-1].strip().startswith("ifne")
        and _fdsl[_fdsw[0] + 2].split(":")[-1].strip() == "return" and any("EntityTickingSystem.tick" in x for x in _fdsl[_fdsw[0]:])), \
    "FallDamagePlayers.tick(float, int, Store) no longer returns at once in a world with fall damage off - re-check RollSys.fallDamageOn (roll landings)"
# (4) SICKLE SWINGS: the only paths that hand drops over through InteractivelyPickupItemEvent: ItemUtils.interactivelyPickupItem (new event,
# invoke on the player, isCancelled, getItemStack), FarmingUtil.giveDrops (HarvestCrop: F-harvest AND the sickle selector) and the F pickup of
# a loose block (BlockHarvestUtils.performPickupByInteraction: a BreakBlockEvent with a NULL item first, then the drops)
_iup = _bc_lines("com.hypixel.hytale.server.core.entity.ItemUtils", "interactivelyPickupItem")
assert (any(IPE + ".<init>" in x for x in _iup) and any(IPE + ".isCancelled" in x for x in _iup) and any(IPE + ".getItemStack" in x for x in _iup)
        and any("ComponentAccessor.invoke" in x for x in _iup)), "ItemUtils.interactivelyPickupItem changed - re-check SickleSys"
_gdr = _bc_lines(FUT, "giveDrops")
assert any("ItemUtils.interactivelyPickupItem" in x for x in _gdr) and any(BHU + ".getDrops" in x for x in _gdr), "FarmingUtil.giveDrops changed"
assert any(FUT + ".giveDrops" in x for x in _bc_lines(FUT, "harvest0")), "FarmingUtil.harvest0 no longer gives the drops"
assert any(FUT + ".harvest" in x for x in _bc_lines("com.hypixel.hytale.builtin.adventure.farming.interactions.HarvestCropInteraction", "interactWithBlock")), \
    "HarvestCropInteraction.interactWithBlock no longer calls FarmingUtil.harvest"
_ppi = _bc_lines(BHU, "performPickupByInteraction")
_bbi = [i for i, x in enumerate(_ppi) if BBE + ".<init>" in x]
assert len(_bbi) == 1 and any(x.strip() == "aconst_null" for x in _ppi[max(0, _bbi[0] - 3):_bbi[0]]) and \
    any("ItemUtils.interactivelyPickupItem" in x for x in _ppi[_bbi[0]:]), \
    "BlockHarvestUtils.performPickupByInteraction no longer fires BreakBlockEvent(null item) before its pickups - re-check the F-pickup context"
print("0.4.14 engine checks: FallDamagePlayers (BEFORE ProcessPlayerInput, rolling mitigation, 0.58 / 10 / 100, no landing in a world with fall "
      "damage off), InteractivelyPickupItemEvent from ItemUtils <- FarmingUtil.giveDrops <- harvest0 <- HarvestCropInteraction and the F pickup "
      "(BreakBlockEvent(null) first)")
# 0.4.8 (Skyy 2026-09-30): every vanilla spell's Mana cost / SPELL_DIVISOR (the SPELL GEN block builds the item overrides)
SPELL_DIVISOR = 5
# ================= default xp.properties (generated here, every id checked against Assets.zip) =================
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
with zipfile.ZipFile(ASSETS) as z:
    ITEM_IDS = set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
def must(i):
    if i not in ITEM_IDS: raise SystemExit("unknown item id in defaults: " + i)
    return i
def must_prefix(p):
    if not any(i.startswith(p) for i in ITEM_IDS): raise SystemExit("prefix matches no item: " + p)
    return p
def must_suffix(s):
    if not any(i.endswith(s) for i in ITEM_IDS): raise SystemExit("suffix matches no item: " + s)
    return s

LEVELS = [50, 125, 200, 300, 500, 750, 1000, 1500, 2000, 3500, 5000, 7500, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 200000,
          300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1100000, 1200000, 1300000, 1400000, 1500000, 1600000,
          1700000, 1800000, 1900000, 2000000, 2100000, 2200000, 2300000, 2400000, 2500000, 2600000, 2750000, 2900000, 3100000,
          3400000, 3700000, 4000000]
assert len(LEVELS) == 50
LEVELS_OLD50 = list(LEVELS)   # the 0.1/0.2 default: an xp.properties still carrying exactly this levels= line is upgraded on load
# 0.3: max level 100 (Skyy). Levels 51-60 = Hypixel SkyBlock's own 51-60 (4.3M .. 7.0M, +300k per level); 61-100 continue that
# +300k step (level 100 needs 19,000,000 XP; 0 -> 60 = Hypixel's 111,672,425, 0 -> 100 = 637,672,425).
LEVELS = LEVELS + [4300000 + 300000 * i for i in range(50)]
assert len(LEVELS) == 100 and LEVELS[59] == 7000000 and sum(LEVELS[:60]) == 111672425 and LEVELS[99] == 19000000
# 0.4.12 (Skyy 2026-10-02 Q&A round 1: "the cloud proposal as written"): the CLASS skill table - research/cloud/Class-Skill-Curve-Proposal.md
# section 5 "XP for level", verbatim (tools/skills_0_4_12_patch.py checked it against the proposal file when it wrote this script)
CLASS_LEVELS_REF = [50, 100, 160, 220, 280, 350, 440, 530, 630, 750, 880, 1050, 1200, 1400, 1600, 1800, 2100, 2350, 2650, 3000, 3350, 3750, 4200, 4650, 5150, 5700, 6250, 6900, 7550, 8250, 9000, 9800, 10500, 11500, 12500, 13500, 14500, 15500, 17000, 18000, 19500, 20500, 22000, 23500, 25000, 26500, 28500, 30000, 32000, 34000, 35500, 38000, 40000, 42000, 44500, 46500, 49000, 51500, 54500, 57000, 60000, 62500, 65500, 68500, 72000, 75000, 78500, 82000, 85500, 89000, 93000, 97000, 100000, 105000, 110000, 115000, 120000, 125000, 125000, 130000, 135000, 140000, 145000, 150000, 160000, 165000, 170000, 175000, 180000, 185000, 195000, 200000, 205000, 210000, 220000, 225000, 235000, 240000, 250000, 255000]
from fractions import Fraction as _Fr
def _cls_xp(L):
    """XP for class level L = round(50 x L + 0.25 x L^3) to a step of 10 below 1,000, 50 below 10,000, 500 below 100,000, 5,000 above
    (the step is picked on the unrounded value; round half to even = the proposal's Python round(): level 70 = 89,250 -> 89,000)"""
    x = _Fr(50 * L) + _Fr(L ** 3, 4)
    st = 10 if x < 1000 else 50 if x < 10000 else 500 if x < 100000 else 5000
    return round(x / st) * st
CLASS_LEVELS = [_cls_xp(_L) for _L in range(1, 101)]
assert CLASS_LEVELS == CLASS_LEVELS_REF, "the class curve formula does not give the proposal's section 5 table"
_cc, _oc = 0, 0
for _i in range(100):
    _cc += CLASS_LEVELS[_i]
    _oc += LEVELS[_i]
    # Skyy: never below today at any level - the class total for every level is at or below the 0.4.11 (general) total
    assert _cc <= _oc, "class level %d needs %d XP in total, more than the general table's %d" % (_i + 1, _cc, _oc)
assert [sum(CLASS_LEVELS[:_n]) for _n in (10, 20, 30, 40, 60, 100)] == [3510, 21540, 77290, 209090, 929090, 6627590], "proposal section 2 totals"
CLASS_LEVELS_TEXT = ",".join(str(x) for x in CLASS_LEVELS)
ICONS = ["Tool_Pickaxe_Iron", "Tool_Hatchet_Iron", "Tool_Hoe_Iron", "Weapon_Sword_Iron", "Armor_Leather_Light_Legs"]
for i in ICONS: must(i)

L = []
L.append("# SkyySkills %s - XP rules. Edit, then /skills reload (permission skyyskills.admin) or restart the server." % VERSION)
L.append("# Block ids are the ids /collections shows. Growth-stage crops use their item id, e.g. Plant_Crop_Wheat_Block.")
L.append("#   block.<exact id>=<Skill>:<xp>      exact id, beats every other rule")
L.append("#   prefix.<start of id>=<Skill>:<xp>  the LONGEST matching prefix or suffix wins")
L.append("#   suffix.<end of id>=<Skill>:<xp>")
L.append("#   <Skill>:0 or none = no XP.  Skill = Mining | Foraging | Farming   (Combat = your class skill, from kills, see combat.*)")
L.append("# ignorePlaced=true : blocks a player placed pay no XP (crops that must ripen are exempt; they only pay when fully grown)")
L.append("multiplier=1.0")
L.append("coinsPerLevel=100")
L.append("feedback=true")
L.append("feedbackMs=2000")
L.append("creativeXp=false")
L.append("ignorePlaced=true")
L.append("farmingNeedsRipe=true")
L.append("# F-harvest (eternal crops, berry bushes) pays only after the crop really was harvested, and one block pays at most once")
L.append("# per harvestCooldownMs (minimum 3000). Breaking a ripe crop uses the same per-block gate.")
L.append("harvestCooldownMs=5000")
L.append("# Combat XP per NPC kill = NPC max health x combat.perHealth, clamped to combat.min..combat.max (combat.default if the")
L.append("# health is unknown). Exact overrides by NPC role name: combat.role.<RoleName>=<xp>  (the server log prints unknown roles once)")
L.append("combat.perHealth=0.2")
L.append("combat.min=1")
L.append("combat.max=500")
L.append("combat.default=5")
L.append("# XP needed for each level, level 1 first (Hypixel SkyBlock table to 60, then +300k per level; the number of entries")
L.append("# is the max level, at most 100). Every skill but the class skills - they level on levels.class (Class skill levels, below).")
L.append("levels=" + ",".join(str(x) for x in LEVELS))
L.append("")
L.append("# ---------- Mining ----------")
L.append("prefix.%s=Mining:1" % must_prefix("Rock_"))
L.append("prefix.%s=Mining:1" % must_prefix("Rubble_"))
L.append("prefix.%s=Mining:8" % must_prefix("Rock_Crystal_"))
L.append("prefix.%s=Mining:40" % must_prefix("Rock_Gem_"))
L.append("block.%s=none" % must("Rock_Bedrock"))
L.append("prefix.%s=Mining:2" % must_prefix("Soil_Sand"))
L.append("prefix.%s=Mining:2" % must_prefix("Soil_Gravel"))
L.append("suffix.%s=Mining:2" % must_suffix("_Gravel"))
L.append("prefix.%s=Mining:5" % must_prefix("Ore_"))
for ore, xp in (("Copper", 5), ("Iron", 8), ("Silver", 10), ("Gold", 12), ("Cobalt", 15), ("Thorium", 18), ("Mithril", 25),
                ("Adamantite", 30), ("Onyxium", 40), ("Prisma", 50)):
    L.append("prefix.%s=Mining:%d" % (must_prefix("Ore_" + ore), xp))
L.append("")
L.append("# ---------- Foraging ----------")
L.append("prefix.%s=Foraging:1" % must_prefix("Plant_Leaves_"))
L.append("suffix.%s=Foraging:6" % must_suffix("_Trunk"))
L.append("suffix.%s=Foraging:6" % must_suffix("_Trunk_Full"))
L.append("suffix.%s=Foraging:2" % must_suffix("_Roots"))
for s in ("_Branch_Short", "_Branch_Long", "_Branch_Corner"):
    L.append("suffix.%s=Foraging:1" % must_suffix(s))
WOOD_TIERS = [(3, ["Bamboo"]),
              (10, ["Redwood", "Banyan", "Bottletree", "Gumboab", "Wisteria_Wild", "Windwillow", "Fig_Blue", "Spiral", "Petrified", "Poisoned"]),
              (15, ["Azure", "Amber", "Stormbark"]), (20, ["Fire", "Ice"]), (30, ["Crystal"])]
for xp, woods in WOOD_TIERS:
    for w in woods:
        for suf in ("_Trunk", "_Trunk_Full"):
            iid = "Wood_%s%s" % (w, suf)
            if suf == "_Trunk": must(iid)
            if iid in ITEM_IDS: L.append("block.%s=Foraging:%d" % (iid, xp))
L.append("")
L.append("# ---------- Farming (crops pay only when fully grown) ----------")
L.append("prefix.%s=Farming:3" % must_prefix("Plant_Crop_"))
for crop, xp in (("Wheat", 4), ("Carrot", 4), ("Potato", 4), ("Lettuce", 4), ("Onion", 5), ("Turnip", 5), ("Cotton", 5), ("Rice", 5),
                 ("Corn", 6), ("Cauliflower", 6), ("Tomato", 6), ("Chilli", 7), ("Aubergine", 7), ("Pumpkin", 8), ("Berry", 3),
                 ("Apple", 5), ("Mushroom", 3), ("Wild_Grass", 1), ("Health1", 10), ("Health2", 15), ("Health3", 20),
                 ("Mana1", 10), ("Mana2", 15), ("Mana3", 20), ("Stamina1", 10), ("Stamina2", 15), ("Stamina3", 20)):
    L.append("prefix.%s=Farming:%d" % (must_prefix("Plant_Crop_" + crop), xp))
L.append("prefix.%s=Farming:2" % must_prefix("Plant_Cactus"))
# 0.2: Acrobatics - also appended once to an existing xp.properties that has no acro.* key (AcroCfg.ensureDefaults)
ACRO_L = []
ACRO_L.append("# ---------- Acrobatics (run, jump, fall, dodge) - SkyySkills 0.2 ----------")
ACRO_L.append("# Comments must stay on their own lines (a # after a value becomes part of the value).")
ACRO_L.append("# acro.enabled=false turns off Acrobatics XP AND its movement bonuses.")
ACRO_L.append("acro.enabled=true")
ACRO_L.append("# XP per block moved on the ground (sprint / run / walk or sneak), measured from the server position. A move of more than")
ACRO_L.append("# acro.teleportBlocks in one tick or faster than acro.maxSpeed blocks per second (teleport, launch, lag burst) pays nothing.")
ACRO_L.append("# No Acrobatics XP (running, jumping, falling or dodging) and no dodge push while mounted, flying, gliding, climbing,")
ACRO_L.append("# swimming, in fluid, sitting, sleeping or mantling; no Acrobatics XP in creative (see creativeXp).")
ACRO_L.append("acro.sprintXpPerBlock=0.25")
ACRO_L.append("acro.runXpPerBlock=0.15")
ACRO_L.append("acro.walkXpPerBlock=0.05")
ACRO_L.append("acro.maxSpeed=30")
ACRO_L.append("acro.teleportBlocks=8")
ACRO_L.append("# Jumps: acro.jumpXp per jump, at most one paid jump per acro.jumpCooldownMs, and only after moving acro.jumpMinMove blocks")
ACRO_L.append("# since the last paid jump (jumping in place pays nothing).")
ACRO_L.append("acro.jumpXp=2")
ACRO_L.append("acro.jumpCooldownMs=800")
ACRO_L.append("acro.jumpMinMove=2.0")
# 0.4 (Skyy): only a fall that really hurt you and that you survived pays - the higher the fall, the more XP. The pre-0.4 lines below
# (ACRO_FALL_OLD) are what 0.2 / 0.3 wrote; AcroCfg.migrateFall rewrites them once in an existing xp.properties.
ACRO_FALL_OLD = ["# Falls: landing after a drop of at least acro.fallMinBlocks pays acro.fallXpPerBlock per block from there on; a fall that hurt",
                 "# pays acro.fallDamageXp per point of fall damage (before the Acrobatics reduction) instead, only if you survived it.",
                 "# One landing pays at most acro.fallXpMax. Landing in water pays nothing."]
ACRO_FALL_NEW = ["# Falls (SkyySkills 0.4): only a fall that really HURT you and that you SURVIVED pays - the higher the fall, the more XP.",
                 "# Safe drops (no fall damage), water landings and falls whose damage was cancelled or fully negated pay nothing.",
                 "# acro.fallDamageXp = XP per point of fall damage BEFORE armor and the Acrobatics reduction, counted as if you had 100 max",
                 "# health (vanilla fall damage is a percent of max health, so extra max health does not change the XP). One landing pays",
                 "# at most acro.fallXpMax; all fall XP together at most acro.fallMaxXpPerMinute in any 60 seconds (0 = no fall XP), a cap",
                 "# of its own outside acro.maxXpPerMinute."]
ACRO_CAP_OLD = "# All Acrobatics XP together pays at most this much in ANY 60 seconds (sliding window; movement is easy to macro)."
ACRO_CAP_NEW = "# Running, jumping and dodging XP together pays at most this much in ANY 60 seconds (sliding window; movement is easy to macro)."
FALL_DMG_DEF, FALL_MAX_DEF, FALL_PM_DEF = "10", "2000", "3000"
ACRO_L.extend(ACRO_FALL_NEW)
ACRO_L.append("acro.fallDamageXp=" + FALL_DMG_DEF)
ACRO_L.append("acro.fallXpMax=" + FALL_MAX_DEF)
ACRO_L.append("acro.fallMaxXpPerMinute=" + FALL_PM_DEF)
ACRO_L.append("# Dodge (the vanilla strafe left/right dodge): XP per dodge, at most one per acro.dodgeCooldownMs.")
ACRO_L.append("acro.dodgeXp=3")
ACRO_L.append("acro.dodgeCooldownMs=400")
ACRO_L.append(ACRO_CAP_NEW)
ACRO_L.append("acro.maxXpPerMinute=240")
ACRO_L.append("# The +Acrobatics XP chat line shows at most once per this many ms (level ups always show; /skills quiet hides it).")
ACRO_L.append("acro.feedbackMs=30000")
ACRO_L.append("# Bonuses per Acrobatics level (linear). speedPerLevel = fraction of vanilla speed (0.01 = +1% per level);")
ACRO_L.append("# jumpBlocksPerLevel = extra jump height in blocks; fallReductionPerLevel = less fall damage per level, capped at fallReductionMax.")
ACRO_L.append("acro.speedPerLevel=0.01")
ACRO_L.append("acro.jumpBlocksPerLevel=0.015")
ACRO_L.append("acro.fallReductionPerLevel=0.005")
ACRO_L.append("acro.fallReductionMax=0.8")
ACRO_L.append("# Dodge boost: every dodge gets an extra push of dodgeForce x (level x dodgeBoostPerLevel, at most dodgeBoostMax) in the")
ACRO_L.append("# direction you are moving (the vanilla dodge force is 13). acro.dodgeBoost=false turns the push off (dodge XP stays).")
ACRO_L.append("acro.dodgeBoost=true")
ACRO_L.append("acro.dodgeForce=13")
ACRO_L.append("acro.dodgeBoostPerLevel=0.004")
ACRO_L.append("acro.dodgeBoostMax=0.5")
L.append("")
L.extend(ACRO_L)
ACRO_DEFAULTS = "\n".join(ACRO_L) + "\n"
assert all(ord(ch) < 128 for ch in ACRO_DEFAULTS)
ACRO_LIT = json.dumps(ACRO_DEFAULTS)
# 0.3: perks + class combat - also appended once to an existing xp.properties that has no perk.* key (PerkCfg.ensureDefaults)
PERK_L = []
PERK_L.append("# ---------- Perks (SkyySkills 0.3) - the FLAT layer: skills add flat amounts to the default stats ----------")
PERK_L.append("# Comments must stay on their own lines. Every skill (mining, foraging, farming, combat, acrobatics) accepts")
PERK_L.append("#   perk.<skill>.healthPerLevel / staminaPerLevel / manaPerLevel = max stat added per level (summed over all skills and")
PERK_L.append("#   applied as MAX modifiers skyyskill_health / skyyskill_stamina / skyyskill_mana; vanilla max: 100 health, 10 stamina)")
PERK_L.append("#   perk.<skill>.doubleDropPerLevel = chance per level (0.005 = 0.5 percent, 50 percent at level 100) that a block which paid")
PERK_L.append("#   that skill's XP gives its drops a second time, straight into your inventory (mining, foraging, farming; capped by")
PERK_L.append("#   perk.doubleDropMax). perk.<skill>.doubleDropOnly = comma list of id parts: only blocks whose id contains one can double")
PERK_L.append("#   (empty = every block of that skill). Placed blocks never double (needs ignorePlaced=true), neither do blocks whose")
PERK_L.append("#   drops depend on the tool (gravel + pickaxe, shears on plants).")
PERK_L.append("perk.enabled=true")
PERK_L.append("perk.doubleDropMax=1.0")
PERK_L.append("perk.doubleDropMessage=true")
PERK_L.append("perk.mining.staminaPerLevel=0.05")
PERK_L.append("perk.mining.doubleDropPerLevel=0.005")
PERK_L.append("perk.mining.doubleDropOnly=")
PERK_L.append("perk.foraging.healthPerLevel=0.1")
PERK_L.append("perk.foraging.doubleDropPerLevel=0.005")
PERK_L.append("perk.foraging.doubleDropOnly=_Trunk")
PERK_L.append("perk.farming.healthPerLevel=0.25")
PERK_L.append("perk.farming.doubleDropPerLevel=0.005")
PERK_L.append("perk.farming.doubleDropOnly=")
PERK_L.append("# Combat = your CLASS skill (needs SkyyClasses); perk.combat.* uses the level of your current class. damagePerLevel = extra")
PERK_L.append("# damage with your class weapons (0.002 = +0.2 percent per level, +20 percent at 100), vs monsters only unless damageVsPlayers=true.")
PERK_L.append("perk.combat.healthPerLevel=0.1")
PERK_L.append("perk.combat.damagePerLevel=0.002")
PERK_L.append("perk.combat.damageVsPlayers=false")
PERK_L.append("# Combat XP only with a class (/class) and only for kills with a weapon SkyyClasses allows for it (bridge class:fn:allowed);")
PERK_L.append("# classWeaponOnly=true also needs one of the class's own weapons (class:weapons:<Class>), so tools and fists earn nothing.")
PERK_L.append("# Each class keeps its own level (Combat.<Class> in players/<uuid>.properties).")
PERK_L.append("combat.classWeaponOnly=true")
L.append("")
L.extend(PERK_L)
PERK_DEFAULTS = "\n".join(PERK_L) + "\n"
assert all(ord(ch) < 128 for ch in PERK_DEFAULTS)
PERK_LIT = json.dumps(PERK_DEFAULTS)
# 0.4: Alchemy + Smithing + cross-mod XP. Each block is also appended once to an existing xp.properties that has none of its keys
# (AlchCfg / SmithCfg / BridgeCfg.ensureDefaults, the AcroCfg pattern); the code defaults below are the same numbers, so a file that
# lacks a key still gets them. Every item id goes through must(), every effect id through must_effect().
ALCH_XP = [("Potion_Health_Lesser", 50), ("Potion_Signature_Lesser", 50), ("Potion_Stamina_Lesser", 50), ("Potion_Antidote", 80),
           ("Weapon_Bomb_Popberry", 10), ("Potion_Morph_Dog", 800), ("Potion_Morph_Frog", 800), ("Potion_Morph_Mouse", 800),
           ("Potion_Morph_Pigeon", 800), ("Potion_Empty_Small", 0), ("Potion_Empty_Large", 0), ("Plant_Seeds_Health1", 60),
           ("Plant_Seeds_Mana1", 60), ("Plant_Seeds_Stamina1", 60), ("Tool_Fertilizer_Crystal", 300), ("Potion_Health_Small", 850),
           ("Potion_Signature_Small", 850), ("Potion_Stamina_Small", 850), ("Potion_Health", 8000), ("Potion_Signature", 8000),
           ("Potion_Stamina", 8000), ("Plant_Seeds_Health2", 300), ("Plant_Seeds_Mana2", 300), ("Plant_Seeds_Stamina2", 300),
           ("Potion_Health_Greater", 18000), ("Potion_Signature_Greater", 18000), ("Potion_Stamina_Greater", 18000),
           ("Plant_Seeds_Health3", 1200), ("Plant_Seeds_Mana3", 1200), ("Plant_Seeds_Stamina3", 1200)]
ALCH_TIER = [50, 850, 8000, 18000, 18000]
ALCH_EXTEND = ["Potion_Health_Regen", "Potion_Health_Regen_Lesser", "Potion_Health_Regen_Small", "Potion_Health_Regen_Large",
               "Potion_Health_Regen_Greater", "Potion_Signature_Regen", "Potion_Signature_Regen_Lesser", "Potion_Signature_Regen_Small",
               "Potion_Signature_Regen_Large", "Potion_Signature_Regen_Greater", "Potion_Morph_Dog", "Potion_Morph_Frog",
               "Potion_Morph_Mouse", "Potion_Morph_Pigeon", "Antidote"]
SMITH_XP = [("Ingredient_Bar_Copper", 5), ("Ingredient_Bar_Iron", 8), ("Ingredient_Bar_Silver", 10), ("Ingredient_Bar_Gold", 12),
            ("Ingredient_Bar_Cobalt", 15), ("Ingredient_Bar_Thorium", 18), ("Ingredient_Bar_Mithril", 25), ("Ingredient_Bar_Adamantite", 30),
            ("Ingredient_Bar_Onyxium", 40), ("Ingredient_Bar_Prisma", 50), ("Potion_Empty", 2), ("Ingredient_Charcoal", 0)]
BRIDGE_SKILLS = "Mining,Foraging,Farming,Alchemy,Smithing,Cooking"
BONUS_XP_SKILLS = "Mining,Foraging,Farming,Cooking"   # 0.4 trees bridge: skills whose XP the skill:bonus xp.<skill> entries raise
BONUS_ADDXP_SKILLS = "Cooking"   # ... and whose skill:fn:addxp GRANTS (XP other mods grant) get it too; SkyyCollections rewards stay exact
EFFECTS = {}
RECIPES = []   # (source file, primary output id, set of input item ids, set of output item ids, [bench ids])
def _mat_ids(v):
    out = set()
    if isinstance(v, dict): v = [v]
    if isinstance(v, list):
        for x in v:
            if isinstance(x, dict) and isinstance(x.get("ItemId"), str): out.add(x["ItemId"])
    return out
def _benches(r):
    br = r.get("BenchRequirement") or []
    if isinstance(br, dict): br = [br]
    return [b.get("Id") for b in br if isinstance(b, dict)]
with zipfile.ZipFile(ASSETS) as z:
    for n in z.namelist():
        if not n.endswith(".json"): continue
        if n.startswith("Server/Entity/Effects/"):
            try: d = json.loads(z.read(n).decode("utf-8-sig"))
            except Exception: d = {}
            EFFECTS[os.path.basename(n)[:-5]] = d if isinstance(d, dict) else {}
        elif n.startswith("Server/Item/Items/"):
            try: d = json.loads(z.read(n).decode("utf-8-sig"))
            except Exception: continue
            r = d.get("Recipe") if isinstance(d, dict) else None
            if isinstance(r, dict):
                iid = os.path.basename(n)[:-5]
                RECIPES.append((n, iid, _mat_ids(r.get("Input")), {iid} | _mat_ids(r.get("Output")), _benches(r)))
        elif n.startswith("Server/Item/Recipes/"):
            try: d = json.loads(z.read(n).decode("utf-8-sig"))
            except Exception: continue
            if not isinstance(d, dict): continue
            po = _mat_ids(d.get("PrimaryOutput"))
            outs = po | _mat_ids(d.get("Output"))
            prim = sorted(po)[0] if po else (sorted(outs)[0] if outs else None)
            RECIPES.append((n, prim, _mat_ids(d.get("Input")), outs, _benches(d)))
def must_effect(e):
    if e not in EFFECTS: raise SystemExit("unknown effect id in defaults: " + e)
    return e
for _i, _x in ALCH_XP: must(_i)
for _i, _x in SMITH_XP: must(_i)
for _e in ALCH_EXTEND: must_effect(_e)
_alch = [r for r in RECIPES if "Alchemybench" in r[4]]
assert len(_alch) >= 30, "expected the 30 vanilla Alchemybench recipes, found %d" % len(_alch)
_axp = dict(ALCH_XP)
for _r in _alch:
    if _r[1] not in _axp: print("note: Alchemybench recipe %s (%s) is not in alchemy.xp.* - it pays alchemy.tierXp" % (_r[1], _r[0]))
# craft / uncraft loop check (Alchemy spec 6.4): an Alchemybench output worth more than 10 XP must not be the input of any recipe
# that gives back one of the inputs it was made from (the bomb -> salvage loop is why the bomb pays 10). Reruns on every build.
for _r in _alch:
    if _axp.get(_r[1], ALCH_TIER[-1]) <= 10: continue
    for _q in RECIPES:
        if _r[1] in _q[2] and (_q[3] & _r[2]):
            raise SystemExit("craft loop: %s (%d Alchemy XP) -> %s gives back %s" % (_r[1], _axp.get(_r[1], 0), _q[0], sorted(_q[3] & _r[2])))
# base durations for the Stats page pulse text (floor(duration x (1 + bonus) / pulse cooldown))
def _eff(e, k, d):
    v = EFFECTS[must_effect(e)].get(k)
    return float(v) if isinstance(v, (int, float)) else float(d)
SIG_DUR, SIG_CD = _eff("Potion_Signature_Regen_Lesser", "Duration", 30.05), _eff("Potion_Signature_Regen_Lesser", "DamageCalculatorCooldown", 5)
HPR_DUR, HPR_CD = _eff("Potion_Health_Regen_Lesser", "Duration", 5.05), _eff("Potion_Health_Regen_Lesser", "DamageCalculatorCooldown", 5)
MORPH_DUR, ANTI_DUR = _eff("Potion_Morph_Dog", "Duration", 60), _eff("Antidote", "Duration", 120)
ALCH_L = []
ALCH_L.append("# ---------- Alchemy (SkyySkills 0.4) ----------")
ALCH_L.append("# Comments must stay on their own lines.")
ALCH_L.append("alchemy.enabled=true")
ALCH_L.append("# Base XP per finished craft at the vanilla Alchemy Bench, keyed by the craft's primary OUTPUT item id (0 = no XP). Alchemy")
ALCH_L.append("# Bench recipes another Skyy mod crafts itself (bridge skill:fn:craftxp) use the same table. Unlisted Alchemy Bench recipes pay")
ALCH_L.append("# alchemy.tierXp by the recipe's bench tier I..V (the server log names each one once).")
for _i, _x in ALCH_XP:
    ALCH_L.append("alchemy.xp.%s=%d" % (_i, _x))
ALCH_L.append("alchemy.tierXp=" + ",".join(str(x) for x in ALCH_TIER))
ALCH_L.append("# Brewer perks (Alchemy level of your active profile). Potion effects you DRINK last longer: durationPerLevel 0.01 = +1 percent per")
ALCH_L.append("# level (x2 at level 100), capped at durationMax; only the effect ids in perk.alchemy.extend grow (instant heals cannot).")
ALCH_L.append("perk.alchemy.durationPerLevel=0.01")
ALCH_L.append("perk.alchemy.durationMax=1.0")
ALCH_L.append("perk.alchemy.extend=" + ",".join(ALCH_EXTEND))
ALCH_L.append("perk.alchemy.manaPerLevel=0.2")
ALCH_L.append("# Chance per level to brew one extra potion (only outputs starting with an extraPotionOnly part, never an extraPotionNever part).")
ALCH_L.append("perk.alchemy.extraPotionPerLevel=0.002")
ALCH_L.append("perk.alchemy.extraPotionMax=0.25")
ALCH_L.append("perk.alchemy.extraPotionOnly=Potion_,Weapon_Bomb_")
ALCH_L.append("perk.alchemy.extraPotionNever=Potion_Empty")
ALCH_L.append("# perk.smithing.* and perk.cooking.* accept healthPerLevel / staminaPerLevel / manaPerLevel like every other skill (default 0).")
SMITH_L = []
SMITH_L.append("# ---------- Smithing (SkyySkills 0.4) ----------")
SMITH_L.append("# Comments must stay on their own lines.")
SMITH_L.append("# Smithing XP per finished smelted item. Placed vanilla Furnace: paid when YOU take items out of its output slots into your")
SMITH_L.append("# inventory (drag, shift-click or double-click; whoever collects gets the XP). SkyySacks /craft Furnace tab: paid when a unit")
SMITH_L.append("# finishes (bridge skill:fn:craftxp). Reforging / powders will add Smithing XP later (bridge skill:fn:addxp).")
SMITH_L.append("smithing.smelt.enabled=true")
SMITH_L.append("smithing.vanillaFurnace=true")
for _i, _x in SMITH_XP:
    SMITH_L.append("smithing.xp.%s=%d" % (_i, _x))
SMITH_L.append("# an Ingredient_Bar_* not listed: Mining XP of the ore its Furnace recipe uses x this (at least 1)")
SMITH_L.append("smithing.oreFactor=1.0")
SMITH_L.append("# every other Furnace output (smoothed rock, bricks, clay): this much per item (0 = none)")
SMITH_L.append("smithing.smeltDefault=1")
BRIDGE_L = []
BRIDGE_L.append("# ---------- Cross-mod XP (SkyySkills 0.4) ----------")
BRIDGE_L.append("# Comments must stay on their own lines.")
BRIDGE_L.append("# Skills other Skyy mods may grant through skill:fn:addxp (SkyyCollections tier rewards, SkyyCooking, later reforging / powders).")
BRIDGE_L.append("# Exact skill names; Acrobatics, the class skills and the old Combat slot are not in the default list.")
BRIDGE_L.append("bridge.addxp.skills=" + BRIDGE_SKILLS)
BRIDGE_L.append("# One call may ask for at most maxXpPerCall XP: the caller's base XP, before the xp multiplier and skill-tree bonuses (a guard")
BRIDGE_L.append("# against a broken caller). All bridge XP of one player: at most maxXpPerMinute per minute, counted as actually paid (after")
BRIDGE_L.append("# the multiplier and tree bonuses; 0 = no per-minute cap). The vanilla Alchemy Bench and Furnace paths are not capped.")
BRIDGE_L.append("bridge.maxXpPerCall=500000")
BRIDGE_L.append("bridge.maxXpPerMinute=3000000")
BRIDGE_L.append("# Skill tree bonuses (SkyyTrees posts them in skill:bonus:<uuid>). Wisdom nodes raise the XP you earn yourself in the skills")
BRIDGE_L.append("# of bridge.bonus.xpSkills (blocks, crops, crafts; at most x6). XP another mod grants through skill:fn:addxp gets the Wisdom")
BRIDGE_L.append("# bonus only for the skills in bridge.bonus.addxpSkills (Cooking: SkyyCooking pays your cooking XP that way); rewards such")
BRIDGE_L.append("# as the SkyyCollections tier XP stay exact. The admin /skills xp never gets it. Fortune nodes add to the double-drop chance")
BRIDGE_L.append("# of Mining / Foraging / Farming (the total stays capped at perk.doubleDropMax). bridge.bonus.enabled=false ignores them all.")
BRIDGE_L.append("bridge.bonus.enabled=true")
BRIDGE_L.append("bridge.bonus.xpSkills=" + BONUS_XP_SKILLS)
BRIDGE_L.append("bridge.bonus.addxpSkills=" + BONUS_ADDXP_SKILLS)
for _blk in (ALCH_L, SMITH_L, BRIDGE_L):
    L.append("")
    L.extend(_blk)
ALCH_DEFAULTS = "\n".join(ALCH_L) + "\n"
SMITH_DEFAULTS = "\n".join(SMITH_L) + "\n"
BRIDGE_DEFAULTS = "\n".join(BRIDGE_L) + "\n"
for _t in (ALCH_DEFAULTS, SMITH_DEFAULTS, BRIDGE_DEFAULTS): assert all(ord(ch) < 128 for ch in _t)
ALCH_LIT, SMITH_LIT, BRIDGE_LIT = json.dumps(ALCH_DEFAULTS), json.dumps(SMITH_DEFAULTS), json.dumps(BRIDGE_DEFAULTS)
# 0.4.1: Exploration (research/Exploration-Build-Spec.md 3.3). Also appended once to an existing xp.properties that has no
# exploration.enabled key (ExplCfg.ensureDefaults); the code defaults (ExplCfg.ENABLED, PerkCfg STA[8], AcroCfg.TREE_DODGE_MAX) are the
# same numbers, so a file that lacks a key still gets them.
EXPL_STA_DEF, EXPL_DODGE_DEF = "0.1", "0.25"
EXPL_L = []
EXPL_L.append("# ---------- Exploration (SkyySkills 0.4.1) ----------")
EXPL_L.append("# Comments must stay on their own lines.")
EXPL_L.append("# Exploration XP only comes from other mods through skill:fn:addxp (SkyyExploration: loot chests, new chunks, zones).")
EXPL_L.append("# It never gets the xp multiplier or any skill-tree / booster bonus (Skyy). exploration.enabled=false refuses it.")
EXPL_L.append("exploration.enabled=true")
EXPL_L.append("perk.exploration.staminaPerLevel=" + EXPL_STA_DEF)
EXPL_L.append("# Acrobatics skill-tree dodge nodes (SkyyTrees 0.2, skill:bonus dodge.acrobatics) add at most this much dodge push.")
EXPL_L.append("acro.treeDodgeMax=" + EXPL_DODGE_DEF)
L.append("")
L.extend(EXPL_L)
EXPL_DEFAULTS = "\n".join(EXPL_L) + "\n"
assert all(ord(ch) < 128 for ch in EXPL_DEFAULTS)
EXPL_LIT = json.dumps(EXPL_DEFAULTS)
# 0.4.2: felled trees (research/Tree-Fall-Spec.md 3.1). Also appended once to an existing xp.properties that has no fell.enabled key
# (FellCfg.ensureDefaults); the code defaults in FellCfg are the same numbers.
FELL_L = []
FELL_L.append("# ---------- Felled trees (SkyySkills 0.4.2): every log that falls because you cut the tree pays like a hand-broken log ----------")
FELL_L.append("# Comments must stay on their own lines.")
FELL_L.append("# Hytale fells a tree when its base is cut, but only the block you break fires an event. SkyySkills remembers the natural")
FELL_L.append("# tree at that moment and pays each log (and leaf) that then falls to the player who cut it: Foraging XP x fell.xpFactor")
FELL_L.append("# (leaves x fell.leafXpFactor), a double-drop roll, a SkyyCollections count (source skills:felled) and the per-log")
FELL_L.append("# skill-tree rolls (skill:on:felled). Placed logs never fall and never pay. Explosions and fire never pay as felled.")
FELL_L.append("fell.enabled=true")
FELL_L.append("fell.xpFactor=1.0")
FELL_L.append("fell.leaves=true")
FELL_L.append("fell.leafXpFactor=1.0")
FELL_L.append("# needLeaves: only a tree that touches natural leaves pays (a log wall or a placed log tower never does)")
FELL_L.append("fell.needLeaves=true")
FELL_L.append("# underTrunk: digging out the block under a trunk fells the tree too - it pays the same")
FELL_L.append("fell.underTrunk=true")
FELL_L.append("fell.doubleDrops=true")
FELL_L.append("fell.collections=true")
FELL_L.append("fell.nodes=true")
FELL_L.append("# message: one 'Tree felled: 19 logs, 42 leaves (+156 Foraging XP)' line per tree (/skills quiet hides it)")
FELL_L.append("fell.message=true")
FELL_L.append("# worlds where felled trees never pay, comma separated exact world names")
FELL_L.append("fell.disabledWorlds=")
FELL_L.append("# search limits: blocks sideways from the cut, blocks above it, logs, leaves, block reads per tree")
FELL_L.append("fell.radius=8")
FELL_L.append("fell.height=64")
FELL_L.append("fell.maxLogs=256")
FELL_L.append("fell.maxLeaves=384")
FELL_L.append("fell.maxReads=8000")
FELL_L.append("fell.maxSnapshotsPerSecond=10")
FELL_L.append("fell.maxWatchesPerPlayer=4")
FELL_L.append("fell.maxWatches=64")
FELL_L.append("# milliseconds: how often a falling tree is checked, how long it may stay still before the watch ends, the longest watch,")
FELL_L.append("# how long 'who felled this' is remembered for other mods (skill:fn:felledBy)")
FELL_L.append("fell.pollMs=200")
FELL_L.append("fell.quietMs=3000")
FELL_L.append("fell.maxWatchMs=60000")
FELL_L.append("fell.memoryMs=60000")
FELL_L.append("# debug: one server-log line per snapshot and per felled tree (claims, credited, hand, env, lost, ms) - measures the fall timing")
FELL_L.append("fell.debug=false")
FELL_L.append("# Skyy decisions (research/Tree-Fall-Spec.md section 6):")
FELL_L.append("# extraTrees: also pay felled apple fruit trees and the Bamboo / Ice Trunk_Full blocks (Hytale's tree lists miss them)")
FELL_L.append("fell.extraTrees=false")
FELL_L.append("# skipSaplings: a sapling you plant is not recorded as a placed block, so the base log of a replanted tree pays when broken")
FELL_L.append("placed.skipSaplings=true")
FELL_L.append("# doubleDrops: items from the double-drop perk also count in SkyyCollections (source skills:double) - hand breaks too")
FELL_L.append("collections.doubleDrops=false")
L.append("")
L.extend(FELL_L)
FELL_DEFAULTS = "\n".join(FELL_L) + "\n"
assert all(ord(ch) < 128 for ch in FELL_DEFAULTS) and '"' not in FELL_DEFAULTS
FELL_LIT = json.dumps(FELL_DEFAULTS)
# the engine's own tree lists (spec 2.2): Server/BlockTypeList/TreeWood.json (Wood_<W>_<Trunk|Trunk_Full|Branch_*|Roots>) and TreeLeaves.json
with zipfile.ZipFile(ASSETS) as z:
    TREE_WOOD = sorted(json.loads(z.read("Server/BlockTypeList/TreeWood.json").decode("utf8"))["Blocks"])
    TREE_LEAVES = sorted(json.loads(z.read("Server/BlockTypeList/TreeLeaves.json").decode("utf8"))["Blocks"])
FELL_SUFFIXES = ["_Trunk_Full", "_Trunk", "_Branch_Short", "_Branch_Long", "_Branch_Corner", "_Roots"]
assert len(TREE_WOOD) >= 150 and len(TREE_LEAVES) >= 30, (len(TREE_WOOD), len(TREE_LEAVES))
for _i in TREE_WOOD:
    assert _i.startswith("Wood_") and any(_i.endswith(_x) for _x in FELL_SUFFIXES), "unexpected TreeWood id " + _i
for _i in TREE_LEAVES:
    assert _i.startswith("Plant_Leaves_"), "unexpected TreeLeaves id " + _i
for _i in TREE_WOOD + TREE_LEAVES:
    assert all(ord(ch) < 128 for ch in _i) and '"' not in _i and "\\" not in _i
# fell.extraTrees (Skyy decision, spec 2.2 / 6.7): ids the engine lists miss - only those that really exist as block items
FELL_EXTRA_WOOD = [i for i in ("Wood_Apple_Trunk", "Wood_Apple_Trunk_Full", "Wood_Apple_Branch_Short", "Wood_Apple_Branch_Long",
                               "Wood_Apple_Branch_Corner", "Wood_Apple_Roots", "Wood_Bamboo_Trunk_Full", "Wood_Ice_Trunk_Full")
                   if i in ITEM_IDS and i not in TREE_WOOD]
FELL_EXTRA_LEAVES = [i for i in ("Plant_Leaves_Apple",) if i in ITEM_IDS and i not in TREE_LEAVES]
assert "Wood_Apple_Trunk" in FELL_EXTRA_WOOD and FELL_EXTRA_LEAVES == ["Plant_Leaves_Apple"], (FELL_EXTRA_WOOD, FELL_EXTRA_LEAVES)
print("felled trees: %d wood ids, %d leaf ids (+ extraTrees %d / %d)" % (len(TREE_WOOD), len(TREE_LEAVES), len(FELL_EXTRA_WOOD), len(FELL_EXTRA_LEAVES)))
# 0.4.2 stage 2: Double Jump (research/Double-Jump-Spec.md 3.2). NOT part of ACRO_L on purpose: AcroCfg.ensureDefaults appends ACRO_L to a
# 0.1-era file, AcroCfg.ensureDj appends this block to any file without acro.doubleJump.enabled - both in the same load, never twice.
DJ_L = []
DJ_L.append("# ---------- Double Jump (SkyySkills 0.4.2) - the Acrobatics skill-tree node (SkyyTrees 0.2.1, skill:bonus doublejump.acrobatics) ----------")
DJ_L.append("# Comments must stay on their own lines.")
DJ_L.append("# LOCKED Skyy 2026-09-25 (research/Double-Jump-Spec.md): jump again while already in mid-air. Not crouch.")
DJ_L.append("# trigger: jump = the jump key in mid-air (default); crouch = press crouch in mid-air; both = either one.")
DJ_L.append("# A file that already has acro.doubleJump.trigger=crouch keeps crouch until that line is set to jump.")
DJ_L.append("# Stamina stays 2. Tier III does not name a different cost.")
DJ_L.append("acro.doubleJump.enabled=true")
DJ_L.append("acro.doubleJump.trigger=jump")
DJ_L.append("# extra jumps per airtime (1-5); they recharge when you land, climb, swim or touch water")
DJ_L.append("acro.doubleJump.maxJumps=1")
DJ_L.append("# Air jump height = the node value (a fraction of your own jump height), capped at maxFraction and at maxBlocks.")
DJ_L.append("acro.doubleJump.maxFraction=1.0")
DJ_L.append("acro.doubleJump.maxBlocks=3.5")
DJ_L.append("# forwardPush: extra blocks per second along the way you are moving (only while moving)")
DJ_L.append("acro.doubleJump.forwardPush=2.0")
DJ_L.append("# Stamina per double jump (too little = no double jump, the charge is kept); staminaRegenDelay pauses regen briefly (0 = off)")
DJ_L.append("acro.doubleJump.stamina=2.0")
DJ_L.append("acro.doubleJump.staminaRegenDelay=0.3")
DJ_L.append("# milliseconds between two double jumps, and after leaving the ground before a press counts")
DJ_L.append("acro.doubleJump.cooldownMs=250")
DJ_L.append("acro.doubleJump.minAirMs=100")
DJ_L.append("# 0 = the world's MovementConfig MinFallSpeedToEngageRoll (vanilla 21 - the speed where landings start to hurt); below 0 = no limit.")
DJ_L.append("acro.doubleJump.maxFallSpeed=0")
DJ_L.append("# Acrobatics XP per double jump (0 = none; it counts against acro.maxXpPerMinute)")
DJ_L.append("acro.doubleJump.xp=0")
DJ_L.append("# fx: jump sound + feather particles at your feet")
DJ_L.append("acro.doubleJump.fx=true")
DJ_L.append("# debug=true: players with skyyskills.admin see a chat line for every crouch / jump / extra-jump edge while airborne (test 5.0).")
DJ_L.append("acro.doubleJump.debug=false")
L.append("")
L.extend(DJ_L)
DJ_DEFAULTS = "\n".join(DJ_L) + "\n"
assert all(ord(ch) < 128 for ch in DJ_DEFAULTS) and '"' not in DJ_DEFAULTS
DJ_LIT = json.dumps(DJ_DEFAULTS)
# 0.4.2 stage 2: party combat XP (beta backlog 6). Appended once to a file without party.combatShare.enabled (PartyCfg.ensureDefaults).
PARTY_L = []
PARTY_L.append("# ---------- Party combat XP (SkyySkills 0.4.2) - needs SkyyParty 0.1.3+ (bridge party:fn:members) ----------")
PARTY_L.append("# Comments must stay on their own lines.")
PARTY_L.append("# When a kill pays you class combat XP, every other member of your party who is online, in the same world, within radius")
PARTY_L.append("# blocks of you and not in creative also gets fraction of that XP in THEIR OWN current class skill. The killer keeps 100 percent.")
PARTY_L.append("# Only the killer needs a class weapon; the others need a class. treeBonus: their own skill-tree XP bonus applies to the share.")
PARTY_L.append("party.combatShare.enabled=true")
PARTY_L.append("party.combatShare.fraction=0.5")
PARTY_L.append("party.combatShare.radius=48")
PARTY_L.append("party.combatShare.treeBonus=true")
PARTY_L.append("# message: a '[Party] +6 Archery XP (340/500) from Skyy's kill' chat line, throttled like the other XP lines (/skills quiet hides it)")
PARTY_L.append("party.combatShare.message=true")
L.append("")
L.extend(PARTY_L)
PARTY_DEFAULTS = "\n".join(PARTY_L) + "\n"
assert all(ord(ch) < 128 for ch in PARTY_DEFAULTS) and '"' not in PARTY_DEFAULTS
PARTY_LIT = json.dumps(PARTY_DEFAULTS)
# 0.4.11 (Skyy 2026-10-01: "make healing others give 1xp per hp, and self gives 1.25 xp per hp healed."): the heal rows are the FINAL heal
# XP (not multiplied by classSkill.xpMultiplier). Defaults shared by the file, the rows, DivCfg and HealMig.
HEAL_PER_HP_DEF, HEAL_SELF_DEF, HEAL_MAX_DEF = "1", "1.25", "900"
assert (float(HEAL_PER_HP_DEF), float(HEAL_SELF_DEF), int(HEAL_MAX_DEF)) == (1.0, 1.25, 900)
# HealMig's one-time update: (key, the 0.4.10 default text, the 0.4.11 default text, what the value means now)
HEAL_MG = [("divinity.healXpPerHp", "0.2", HEAL_PER_HP_DEF, "the Divinity XP per HP healed on others the Priest gets"),
           ("divinity.healXpPerHpSelf", "0.25", HEAL_SELF_DEF, "the Divinity XP per HP healed on themself the Priest gets"),
           ("divinity.healXpMaxPerMinute", "300", HEAL_MAX_DEF, "the most heal XP the Priest gets in a minute")]
# the marker comment (in the 0.4.11 default file above the Divinity block and in every updated file): a doc comment with spaces and no "=",
# so the config kit never takes it for a "#key=value" template line; HealMig looks for HEAL_MARK_ID in comment lines only
HEAL_MARK_ID = "SkyySkills 0.4.11 heal XP update"
HEAL_MARK = ("# %s (Skyy 2026-10-01): divinity.healXpPerHp, divinity.healXpPerHpSelf and divinity.healXpMaxPerMinute are the Divinity XP "
             "the Priest gets (defaults 1, 1.25 and 900 a minute) - the class skill XP multiplier no longer applies to healing" % HEAL_MARK_ID)
# the 0.4.10 default comment lines 0.4.11 rewrote (old, new): HealMig replaces an EXACT old line of an existing file with the new one
HEAL_DOC = [('# LOCKED Skyy 2026-09-25: healing themself pays 0.25 XP per HP (was 0). Others stay 0.2. Cap stays 300 a minute.', '# LOCKED Skyy 2026-10-01 (SkyySkills 0.4.11): 1 XP per HP on others, 1.25 on yourself, at most 900 a minute - what the Priest gets.'), ('# healXpMaxPerMinute: most heal XP per Priest in one 60 second window, counted before the xp', '# healXpMaxPerMinute: most heal XP per Priest in one 60 second window. Heal XP is NOT multiplied by classSkill.xpMultiplier;'), ('# multiplier (0 = no limit). Kills pay Divinity XP like every class skill (combat.* keys) and are not counted here.', '# the xp multiplier comes after the cap (0 = no limit). Kills pay Divinity XP like every class skill and are not counted here.'), ('# Both count against divinity.healXpMaxPerMinute.', '# Both count against divinity.healXpMaxPerMinute. Both are the XP the Priest gets (0.4.11: not multiplied by classSkill.xpMultiplier).'), ('# The class skill XP multiplier: every XP gain into a class skill (Archery, Swordsmanship, Sorcery, Fury, Divinity, later', '# The class skill XP multiplier: XP gains into a class skill (Archery, Swordsmanship, Sorcery, Fury, Divinity, later'), ('# Assassination and the Shaman skill) is multiplied by it - kills, the party share, Priest heal XP (on others and on yourself)', '# Assassination and the Shaman skill) are multiplied by it - kills, the party share and class skill XP another mod grants.'), ("# and class skill XP another mod grants. It comes after each source's own numbers: after combat.min, combat.max and", '# Priest heal XP is NOT multiplied (SkyySkills 0.4.11): the divinity heal XP numbers above are what the Priest gets.'), ('# combat.role (a 500 XP kill pays 1500 at 3) and after divinity.healXpMaxPerMinute (that cap counts the healing, before any', "# It comes after each kill's own numbers: after combat.min, combat.max and combat.role (a 500 XP kill pays 1500 at 3)."), ('# multiplier). It stacks with the XP multiplier at the top of this file; bridge.maxXpPerMinute counts the multiplied XP.', '# It stacks with the XP multiplier at the top of this file; bridge.maxXpPerMinute counts the multiplied XP.'), ('# A fraction is paid by chance (2.5 times 1 XP = 2 or 3 XP). 0 = no class skill XP at all. Gathering, Acrobatics, Alchemy,', '# A fraction is paid by chance (2.5 times 1 XP = 2 or 3 XP). 0 = no class skill XP from kills. Gathering, Acrobatics, Alchemy,')]
assert all(32 <= ord(_c) < 127 for _c in HEAL_MARK) and "=" not in HEAL_MARK and HEAL_MARK.startswith("# ") and '"' not in HEAL_MARK
assert not any(HEAL_MARK_ID in _n for _o, _n in HEAL_DOC) and len(set(_o for _o, _n in HEAL_DOC)) == len(HEAL_DOC)
# 0.4.4: Divinity XP from Priest heals (research/Classes-Berserker-Priest-Spec.md 3.4 / 3.5). Appended once to a file without
# divinity.healXp.enabled (DivCfg.ensureDefaults).
DIV_L = []
DIV_L.append("# ---------- Divinity (SkyySkills 0.4.4) - Priest heals from SkyyClasses 0.1.6 (skill:fn:healxp) ----------")
DIV_L.append("# Comments must stay on their own lines.")
DIV_L.append("# A Priest (class skill Divinity) earns healXpPerHp Divinity XP for every 1 HP their weapon hits heal on OTHER party members.")
DIV_L.append("# LOCKED Skyy 2026-10-01 (SkyySkills 0.4.11): 1 XP per HP on others, 1.25 on yourself, at most 900 a minute - what the Priest gets.")
DIV_L.append("# SkyySkills 0.4.6+ reads the self-heal rate from divinity.healXpPerHpSelf (its own block below).")
DIV_L.append("# healXpMaxPerMinute: most heal XP per Priest in one 60 second window. Heal XP is NOT multiplied by classSkill.xpMultiplier;")
DIV_L.append("# the xp multiplier comes after the cap (0 = no limit). Kills pay Divinity XP like every class skill and are not counted here.")
DIV_L.append("divinity.healXp.enabled=true")
DIV_L.append("divinity.healXpPerHp=" + HEAL_PER_HP_DEF)
DIV_L.append("divinity.healXpMaxPerMinute=" + HEAL_MAX_DEF)
L.append("")
L.append(HEAL_MARK)   # 0.4.11: the default file carries the heal XP update marker (HealMig never touches a fresh file); NOT in DIV_L
L.extend(DIV_L)
DIV_DEFAULTS = "\n".join(DIV_L) + "\n"
assert all(ord(ch) < 128 for ch in DIV_DEFAULTS) and '"' not in DIV_DEFAULTS
DIV_LIT = json.dumps(DIV_DEFAULTS)
# 0.4.6 (LOCKED Skyy 2026-09-25): Divinity XP for healing YOURSELF. Its own block (NOT part of DIV_L): DivCfg.ensureDefaults appends DIV_L
# to a file without divinity.healXp.enabled, DivCfg.ensureSelf appends this block to any file without divinity.healXpPerHpSelf - both in
# the same load, never twice (the AcroCfg.ensureDj pattern).
DIVS_L = []
DIVS_L.append("# ---------- Divinity self-heal XP (SkyySkills 0.4.6) - LOCKED Skyy 2026-09-25 ----------")
DIVS_L.append("# Comments must stay on their own lines.")
DIVS_L.append("# healXpPerHpSelf: Divinity XP for every 1 HP a Priest heals on THEMSELF (divinity.healXpPerHp is for other party members).")
DIVS_L.append("# Both count against divinity.healXpMaxPerMinute. Both are the XP the Priest gets (0.4.11: not multiplied by classSkill.xpMultiplier).")
DIVS_L.append("divinity.healXpPerHpSelf=" + HEAL_SELF_DEF)
L.append("")
L.extend(DIVS_L)
DIVS_DEFAULTS = "\n".join(DIVS_L) + "\n"
assert all(ord(ch) < 128 for ch in DIVS_DEFAULTS) and '"' not in DIVS_DEFAULTS
DIVS_LIT = json.dumps(DIVS_DEFAULTS)
# 0.4.5: Crossbows stay loaded, the Archery level-5 reward (research/Crossbow-Loaded-Spec.md 3.2). Appended once to a file without
# perk.archery.keepLoaded.enabled (XbowCfg.ensureDefaults).
XBOW_L = []
XBOW_L.append("# ---------- Crossbows stay loaded (SkyySkills 0.4.5) - the Archery level-5 reward, research/Crossbow-Loaded-Spec.md ----------")
XBOW_L.append("# Comments must stay on their own lines.")
XBOW_L.append("# LOCKED Skyy 2026-09-25: Archery level 5, Archer class only, crossbows only (not shortbows).")
XBOW_L.append("# An Archer whose Archery level is at least 'level' keeps a crossbow's loaded bolts when switching hotbar slots and back.")
XBOW_L.append("# Vanilla gives the bolts back as Crude Arrows when you switch away; switching back loads them again, paid with those arrows.")
XBOW_L.append("# LOCKED Skyy 2026-09-25: loaded bolts survive teleports (SkyySkills 0.4.6+; relog, death and a profile switch drop them).")
XBOW_L.append("# LOCKED Skyy 2026-09-25: keep the big-arrow meter, and play a sound plus a chat hint when bolts return (0.4.6+, block below).")
XBOW_L.append("# Players can turn the meter, the sound, and the hint off in /settings.")
XBOW_L.append("# Planned, not in this build: Archery 15+ can add up to 4 extra bolts. A late-game node reloads a holstered crossbow in about 30 s.")
XBOW_L.append("perk.archery.keepLoaded.enabled=true")
XBOW_L.append("perk.archery.keepLoaded.level=5")
XBOW_L.append("# item id starts that count as crossbows, comma separated")
XBOW_L.append("perk.archery.keepLoaded.items=Weapon_Crossbow_")
XBOW_L.append("# server ticks after switching back before the bolts return (3-20; 3 = about 0.1 s)")
XBOW_L.append("perk.archery.keepLoaded.delayTicks=3")
XBOW_L.append("# debug=true: players with skyyskills.admin see a chat line for every kept / restored load")
XBOW_L.append("perk.archery.keepLoaded.debug=false")
L.append("")
L.extend(XBOW_L)
XBOW_DEFAULTS = "\n".join(XBOW_L) + "\n"
assert all(ord(ch) < 128 for ch in XBOW_DEFAULTS) and '"' not in XBOW_DEFAULTS
XBOW_LIT = json.dumps(XBOW_DEFAULTS)
# 0.4.6 (LOCKED Skyy 2026-09-25): the crossbow extras. Own block, appended once to a file without perk.archery.keepLoaded.meter
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
OVL_L.append("# Base Mana: every player's max Mana starts at mana.base. A class listed below (Base Mana by class, one line per class:")
OVL_L.append("# mana.classBase.<Class>=<Mana>) starts at its own number instead - that number IS its base, not mana.base plus it (SkyySkills")
OVL_L.append("# 0.4.8, replaced mana.magicBase / mana.magicClasses). Vanilla max Mana is 0; Mana refills by itself (+1 every 0.2 s after 6 s")
OVL_L.append("# without taking damage). Spells cost the vanilla Mana / %d (wand 5, staff 10, spellbook 20 - fixed in the jar)." % SPELL_DIVISOR)
OVL_L.append("mana.base.enabled=true")
OVL_L.append("mana.base=10")
CLASS_BASE_DEF = [('Mage', 30), ('Priest', 30)]   # 0.4.8 (Skyy 2026-09-30): enough Mana for the starter weapons (Mage staff 10 a cast, Priest wand 5)
for _cb, _cv in CLASS_BASE_DEF:
    OVL_L.append("mana.classBase.%s=%d" % (_cb, _cv))
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
# 0.4.10 (Skyy 2026-10-01: "increase the class skill xp you get by a good bit"): the class skill XP multiplier. Appended once to a file
# without classSkill.xpMultiplier (SkillCfg.ensureClass, the DivCfg.ensureSelf pattern); the code default (SkillCfg.CLASS_MULT) is the
# same number. No comment line here may look like a "#key=value" template line (the config kit uncomments those in place).
import re as _cre
CLS_MULT_DEF = "3.0"
CLS_L = []
CLS_L.append("# ---------- Class skill XP (SkyySkills 0.4.10) ----------")
CLS_L.append("# Comments must stay on their own lines.")
CLS_L.append("# The class skill XP multiplier: XP gains into a class skill (Archery, Swordsmanship, Sorcery, Fury, Divinity, later")
CLS_L.append("# Assassination and the Shaman skill) are multiplied by it - kills, the party share and class skill XP another mod grants.")
CLS_L.append("# Priest heal XP is NOT multiplied (SkyySkills 0.4.11): the divinity heal XP numbers above are what the Priest gets.")
CLS_L.append("# It comes after each kill's own numbers: after combat.min, combat.max and combat.role (a 500 XP kill pays 1500 at 3).")
CLS_L.append("# It stacks with the XP multiplier at the top of this file; bridge.maxXpPerMinute counts the multiplied XP.")
CLS_L.append("# A fraction is paid by chance (2.5 times 1 XP = 2 or 3 XP). 0 = no class skill XP from kills. Gathering, Acrobatics, Alchemy,")
CLS_L.append("# Smithing, Cooking and Exploration XP are not changed by it, and the admin /skills xp stays raw.")
CLS_L.append("classSkill.xpMultiplier=" + CLS_MULT_DEF)
L.append("")
L.extend(CLS_L)
CLS_DEFAULTS = "\n".join(CLS_L) + "\n"
# 0.4.11: every rewritten comment line is in a 0.4.11 default block, no old one is left in them
assert all(_n in DIV_L + DIVS_L + CLS_L and _o not in DIV_L + DIVS_L + CLS_L for _o, _n in HEAL_DOC)
assert all(ord(ch) < 128 for ch in CLS_DEFAULTS) and '"' not in CLS_DEFAULTS
assert [_ln for _ln in CLS_L if not _ln.startswith("#")] == ["classSkill.xpMultiplier=" + CLS_MULT_DEF]
assert not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in CLS_L), "a comment looks like a template line"
CLS_LIT = json.dumps(CLS_DEFAULTS)
# 0.4.12 (Skyy 2026-10-02 Q&A round 1): the class skill table. Appended once to a file without levels.class (SkillCfg.ensureCurve, the
# ensureClass pattern, in the file's own line ending); the code default (SkillDefs.DEFAULT_CPER) is the same list.
CURVE_L = []
CURVE_L.append("# ---------- Class skill levels (SkyySkills 0.4.12) ----------")
CURVE_L.append("# Comments must stay on their own lines.")
CURVE_L.append("# Class skills (Archery, Swordsmanship, Sorcery, Fury, Divinity, later Assassination and the Shaman skill) level on their own")
CURVE_L.append("# table (Skyy 2026-10-02): XP for level L = 50 x L + 0.25 x L^3, rounded to 10 below 1000, 50 below 10000, 500 below 100000")
CURVE_L.append("# and 5000 above - class skill 20 after 21540 XP in total, 40 after 209090, 100 after 6627590. levels= is for every other skill.")
CURVE_L.append("# A class level never needs more total XP than levels= asks for the same level, so class levels never drop below that table.")
CURVE_L.append("# Set levels.class.sameAsOthers to true and class skills use levels= again (the old, slower curve; levels drop back, coins stay).")
CURVE_L.append("# Server Setup - Skills - Levels: the class curve size in percent and the class max level rewrite levels.class.")
CURVE_L.append("levels.class=" + CLASS_LEVELS_TEXT)
CURVE_L.append("levels.class.sameAsOthers=false")
L.append("")
L.extend(CURVE_L)
CURVE_DEFAULTS = "\n".join(CURVE_L) + "\n"
assert all(ord(ch) < 128 for ch in CURVE_DEFAULTS) and '"' not in CURVE_DEFAULTS
assert [_ln for _ln in CURVE_L if not _ln.startswith("#")] == ["levels.class=" + CLASS_LEVELS_TEXT, "levels.class.sameAsOthers=false"]
assert not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in CURVE_L), "a comment looks like a template line"
assert CURVE_DEFAULTS.count("\nlevels.class.sameAsOthers=false\n") == 1   # SkillCfg.ensureCurve drops that line when the file has the key
CURVE_LIT = json.dumps(CURVE_DEFAULTS)
# 0.4.12 (Skyy 2026-10-02 Q&A rounds 1-2): Mana refills in combat at this percent of (vanilla + Mana Regen boosts). Appended once to a file
# without mana.regen.inCombat (SkillCfg.ensureManaRegen); the code default (ManaRegen.IN_COMBAT) is the same number.
MREG_DEF = "50"
MREG_L = []
MREG_L.append("# ---------- Mana regen in combat (SkyySkills 0.4.12) ----------")
MREG_L.append("# Comments must stay on their own lines.")
MREG_L.append("# Vanilla Mana refills 5 per second, but not at all for 6 seconds after you take damage (in combat) and never while you hold")
MREG_L.append("# a charge. mana.regen.inCombat (Skyy 2026-10-02: 50) is how fast Mana refills in combat, as a percent of the normal refill;")
MREG_L.append("# 0 = vanilla (nothing in combat). Mana Regen boosts from other mods (skill:fn:manaregen) are percents of the vanilla refill:")
MREG_L.append("# out of combat +20 percent = 6 per second, in combat the whole refill (vanilla + boosts) runs at mana.regen.inCombat percent.")
# 0.4.14 (fix (5)): Mana keeps regenerating while charging since 0.4.13 - the old line is the text DocMig rewrites once in an existing file
MREG_DOC_OLD = "# Never above max Mana, never while charging, nothing for a player without Mana (max Mana 0)."
MREG_DOC_NEW = "# Never above max Mana, nothing for a player without Mana (max Mana 0). Charging no longer pauses it (SkyySkills 0.4.13+)."
MREG_L.append(MREG_DOC_NEW)
MREG_L.append("mana.regen.inCombat=" + MREG_DEF)
L.append("")
L.extend(MREG_L)
MREG_DEFAULTS = "\n".join(MREG_L) + "\n"
assert all(ord(ch) < 128 for ch in MREG_DEFAULTS) and '"' not in MREG_DEFAULTS
assert [_ln for _ln in MREG_L if not _ln.startswith("#")] == ["mana.regen.inCombat=" + MREG_DEF]
assert not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in MREG_L), "a comment looks like a template line"
MREG_LIT = json.dumps(MREG_DEFAULTS)
# 0.4.14 (Skyy 2026-10-02 locks): kill XP by mob level, roll landings, the gathering pace, sickle swings - ONE block at the end of a fresh file;
# SkillCfg.ensure14 appends it to an existing file (only the key lines the file lacks, its own line ending). The code defaults (MobXp,
# AcroCfg.ROLL, GatherPace, Sickle) are the same numbers. No comment line may look like a "#key=value" template line.
N14_L = []
N14_L.append("# ---------- Kill XP by mob level, roll landings, gathering pace, sickle swings (SkyySkills 0.4.14) ----------")
N14_L.append("# Comments must stay on their own lines.")
N14_L.append("# KILL XP BY MOB LEVEL (Skyy 2026-10-02, needs SkyyMobs levels): kill XP (max health x combat.perHealth, kept between combat.min and")
N14_L.append("# combat.max, times the class skill XP multiplier) x (1 + combat.levelBonus x (mob level - 1)) x the level gap. A mob more than")
N14_L.append("# combat.gap.free levels ABOVE your class skill adds combat.gap.above per extra level (at most combat.gap.max times, 3.5 = +250 percent);")
N14_L.append("# more than combat.gap.free levels BELOW takes combat.gap.below per level away (at least combat.gap.min, 0.1 = 10 percent). A mob")
N14_L.append("# without a level (no SkyyMobs, an animal it does not level) pays as before. Party members get party.combatShare.fraction of what")
N14_L.append("# the kill pays THEM: the gap uses each member's own class skill level.")
N14_L.append("# A Lv 33 Skeleton Scout (178 HP) at Divinity 11 pays 36 x 3 x 2.6 x 1.85 = about 520 XP.")
N14_L.append("combat.levelXp.enabled=true")
N14_L.append("combat.levelBonus=0.05")
N14_L.append("combat.gap.free=5")
N14_L.append("combat.gap.above=0.05")
N14_L.append("combat.gap.max=3.5")
N14_L.append("combat.gap.below=0.05")
N14_L.append("combat.gap.min=0.1")
N14_L.append("# ROLL LANDINGS (Skyy 2026-10-02): crouch as you land and Hytale rolls - less or no fall damage. A rolled landing pays the")
N14_L.append("# Acrobatics XP the fall would have paid without the roll plus acro.rollBonus of it (0.5 = +50 percent; 0 = rolls pay as before).")
N14_L.append("# acro.fallXpMax and acro.fallMaxXpPerMinute still cap it.")
N14_L.append("acro.rollBonus=0.5")
N14_L.append("# GATHERING PACE (Skyy 2026-10-02): XP you earn in these skills (blocks, felled logs, F-harvests, sickle swings) times early up")
N14_L.append("# to level earlyUntil, easing in a straight line to times late at level lateFrom, times late after. Rewards other mods grant")
N14_L.append("# (SkyyCollections tiers) stay exact. The skill-tree Wisdom bonus comes on top.")
N14_L.append("gather.boost.skills=Mining,Foraging,Farming")
N14_L.append("gather.boost.early=3")
N14_L.append("gather.boost.earlyUntil=10")
N14_L.append("gather.boost.late=1.5")
N14_L.append("gather.boost.lateFrom=20")
N14_L.append("# SICKLE SWINGS (Skyy 2026-10-02): a ripe crop a sickle swing harvests pays its Farming XP and rolls the Farming double drop like a")
N14_L.append("# broken ripe crop, once per crop. Hytale only says which items you picked up, so the crop is found from its produce item. An F")
N14_L.append("# on a ripe crop (paid by the F-harvest) and an F pickup of a loose block are never paid twice. Items = id starts of sickles.")
N14_L.append("# A ripe crop is the final growth stage of a crop that grows (like an F-harvest); plants without growth stages (Health,")
N14_L.append("# Mana and Stamina plants, cactus flowers, boomshrooms) pay only when broken - a sickle swing cannot tell a placed one.")
N14_L.append("farming.sickle.enabled=true")
N14_L.append("farming.sickle.items=Tool_Sickle_")
L.append("")
L.extend(N14_L)
N14_DEFAULTS = "\n".join(N14_L) + "\n"
assert all(ord(ch) < 128 for ch in N14_DEFAULTS) and '"' not in N14_DEFAULTS and "\\" not in N14_DEFAULTS
assert not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in N14_L), "a comment looks like a template line"
N14_KEYS = [_ln.split("=", 1)[0] for _ln in N14_L if not _ln.startswith("#")]
assert len(N14_KEYS) == len(set(N14_KEYS)) == 15, N14_KEYS
N14_LIT = json.dumps(N14_DEFAULTS)
# 0.4.15 (research/SkyyArmory-Spec.md 15.4, Skyy 2026-10-03): max Mana per level of the class's own skill - ONE block at the end of a fresh
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
assert MREG_DOC_OLD != MREG_DOC_NEW and MREG_DOC_NEW in MREG_L and MREG_DOC_OLD not in MREG_L and "charging" not in MREG_DOC_OLD.replace("never while charging", "")
# the sickle items and the selectors whose HitBlock harvests (Assets.zip, read in memory); vanilla's roll numbers for the log
must_prefix("Tool_Sickle_")
with zipfile.ZipFile(ASSETS) as _sz:
    _szn = _sz.namelist()
    for _sel in ("Sickle_Swing_Left_Selector.json", "Sickle_Swing_Right_Selector.json"):
        _sh = [n for n in _szn if n.startswith("Server/Item/Interactions/") and n.endswith("/" + _sel)]
        assert len(_sh) == 1, "Assets.zip: %d x %s" % (len(_sh), _sel)
        _sj = json.loads(_sz.read(_sh[0]).decode("utf-8-sig"))
        assert any(isinstance(_x, dict) and _x.get("Type") == "HarvestCrop" for _x in ((_sj.get("HitBlock") or {}).get("Interactions") or [])), \
            "%s: HitBlock no longer runs HarvestCrop - sickle swings would not harvest" % _sel
    _smc = [n for n in _szn if n.startswith("Server/Entity/MovementConfig/") and n.endswith("/Default.json")]
    _smd = json.loads(_sz.read(_smc[0]).decode("utf-8-sig")) if len(_smc) == 1 else {}
print("sickle swings (0.4.14): %d Tool_Sickle_ items, both swing selectors harvest; roll landings: vanilla MovementConfig Default roll from %s, "
      "no damage to %s, -%s%% to %s blocks a second" % (len([i for i in ITEM_IDS if i.startswith("Tool_Sickle_")]), _smd.get("MinFallSpeedToEngageRoll"),
                                                      _smd.get("MaxFallSpeedRollFullMitigation"), _smd.get("FallDamagePartialMitigationPercent"),
                                                      _smd.get("MaxFallSpeedToEngageRoll")))
import re as _re14
def J14(src_):
    """0.4.14: Java source with @NAME@ tokens = module constants (PKG, BTY, IS, ...) - single braces, no f-string brace doubling"""
    def _tok(m_):
        v_ = globals().get(m_.group(1))
        if not isinstance(v_, str):
            raise SystemExit("J14: unknown token @%s@" % m_.group(1))
        return v_
    return _re14.sub(r"@([A-Z][A-Z0-9_]*)@", _tok, src_)
# 0.4.5 build checks (spec 3.9): the crossbow facts the stay-loaded perk rests on, read in memory from Assets.zip. The cap of 6, the 1:1
# Crude refund and "the ladder checks Ammo but never spends it" are what the anti-dupe argument (spec 2.6) needs; any change fails here.
must("Weapon_Arrow_Crude")
must("Weapon_Crossbow_Iron")
XBOW_TYPES = ("Condition", "StatsCondition", "ModifyInventory", "ChangeActiveSlot")
def _xbow_types(o, out):
    if isinstance(o, dict):
        if "Type" in o: out.append(o["Type"])
        for _v in o.values(): _xbow_types(_v, out)
    elif isinstance(o, list):
        for _v in o: _xbow_types(_v, out)
    return out
# every crossbow the perk covers must unload exactly like the template checked below: Parent = Template_Weapon_Crossbow and no Weapon
# block (the Ammo cap / clear) and no Interactions block (the SwapFrom root) of its own (spec 1.7: true for all 6 crossbows today)
def _xbow_item(where, n, d):
    assert isinstance(d, dict) and d.get("Parent") == "Template_Weapon_Crossbow", \
        "%s %s: Parent %r, not Template_Weapon_Crossbow (it may unload differently)" % (where, n, d.get("Parent") if isinstance(d, dict) else d)
    _ov = [k for k in ("Weapon", "Interactions") if k in d]
    assert not _ov, "%s %s: its own %s block overrides Template_Weapon_Crossbow (the Ammo cap / clear or the SwapFrom refund may differ)" % (where, n, "/".join(_ov))
# the files the checks below read; a pack that ships its own copy would replace them
XBOW_CORE = ("Template_Weapon_Crossbow.json", "Root_Weapon_Crossbow_Swap_From.json", "Weapon_Crossbow_Swap_From.json")
with zipfile.ZipFile(ASSETS) as _xz:
    _xn = _xz.namelist()
    def _xone(pre, base):
        _hits = [n for n in _xn if n.startswith(pre) and n.endswith("/" + base)]
        assert len(_hits) == 1, "Assets.zip: %d x %s under %s" % (len(_hits), base, pre)
        return json.loads(_xz.read(_hits[0]).decode("utf-8-sig"))
    _xitems = [n for n in _xn if n.startswith("Server/Item/Items/") and n.endswith(".json") and os.path.basename(n).startswith("Weapon_Crossbow_")]
    assert _xitems, "no Weapon_Crossbow_* item in Assets.zip"
    for _n in _xitems:
        _xbow_item("Assets.zip", _n, json.loads(_xz.read(_n).decode("utf-8-sig")))
    _xt = _xone("Server/Item/Items/", "Template_Weapon_Crossbow.json")
    _xw = _xt.get("Weapon") or {}
    assert "Ammo" in (_xw.get("EntityStatsToClear") or []), "Template_Weapon_Crossbow no longer clears Ammo on a switch"
    assert (_xw.get("StatModifiers") or {}).get("Ammo") == [{"Amount": 6, "CalculationType": "Additive"}], "crossbow Ammo cap is not +6 Additive"
    assert (_xt.get("Interactions") or {}).get("SwapFrom") == "Root_Weapon_Crossbow_Swap_From", "crossbow SwapFrom root changed"
    _xr = _xone("Server/Item/RootInteractions/", "Root_Weapon_Crossbow_Swap_From.json")
    assert _xr.get("Interactions") == ["Weapon_Crossbow_Swap_From"], "Root_Weapon_Crossbow_Swap_From.Interactions changed: %r" % (_xr.get("Interactions"),)
    _xl = _xone("Server/Item/Interactions/", "Weapon_Crossbow_Swap_From.json")
assert set(_xl.keys()) == {"Type", "RequiredGameMode", "Failed", "Next"}, "SwapFrom ladder root keys changed: %r" % (sorted(_xl.keys()),)
assert _xl["Type"] == "Condition" and _xl["RequiredGameMode"] == "Adventure" and _xl["Failed"] == {"Type": "ChangeActiveSlot"}, "SwapFrom ladder root changed"
_xnode = _xl["Next"]
for _k in (6, 5, 4, 3, 2, 1):
    assert isinstance(_xnode, dict) and set(_xnode.keys()) == {"Type", "Costs", "Next", "Failed"}, "SwapFrom ladder step %d changed: %r" % (_k, _xnode)
    assert _xnode["Type"] == "StatsCondition" and _xnode["Costs"] == {"Ammo": _k}, "SwapFrom ladder step %d is not StatsCondition Ammo %d" % (_k, _k)
    assert _xnode["Next"] == {"Type": "ModifyInventory", "ItemToAdd": {"Id": "Weapon_Arrow_Crude", "Quantity": _k}, "Next": {"Type": "ChangeActiveSlot"}}, \
        "SwapFrom ladder step %d no longer refunds exactly %d Crude Arrows: %r" % (_k, _k, _xnode["Next"])
    _xnode = _xnode["Failed"]
assert _xnode == {"Type": "ChangeActiveSlot"}, "SwapFrom ladder end changed: %r" % (_xnode,)
_xtypes = _xbow_types(_xl, [])
assert "ChangeStat" not in _xtypes and all(t in XBOW_TYPES for t in _xtypes), "SwapFrom ladder has a node type the design does not know: %r" % (sorted(set(_xtypes)),)
assert _xtypes.count("StatsCondition") == 6 and _xtypes.count("ModifyInventory") == 6
# More Crossbow Tiers (PACK.md, Serj): the perk covers its crossbows through the same Weapon_Crossbow_ prefix, so they get the same item
# rule, read in memory from the Mods folder (never written). The pack is found by its manifest (Group + Name), not its file name; the
# "Endgame&QoL expansion - Crossbow Tiers" pack (not in PACK.md, it overrides Weapon) is never read. Missing or twice = the build fails:
# PACK.md ships it and the Server Setup help names it, so dropping it means updating XBOW_PACK and that help text on purpose.
XBOW_PACK = ("Serj", "More Crossbow Tiers")
def _xpack_find():
    _out = []
    _fs = sorted(os.listdir(B.MODS_DIR)) if os.path.isdir(B.MODS_DIR) else []
    for _f in _fs:
        _p = os.path.join(B.MODS_DIR, _f)
        try:
            if os.path.isdir(_p):
                with open(os.path.join(_p, "manifest.json"), "rb") as _mf:
                    _man = json.loads(_mf.read().decode("utf-8-sig"))
            elif _f.lower().endswith((".zip", ".jar")):
                with zipfile.ZipFile(_p) as _mz:
                    _man = json.loads(_mz.read("manifest.json").decode("utf-8-sig"))
            else:
                continue
        except Exception:
            continue
        if isinstance(_man, dict) and (_man.get("Group"), _man.get("Name")) == XBOW_PACK:
            _out.append((_p, str(_man.get("Version"))))
    return _out
_xpk = _xpack_find()
assert len(_xpk) == 1, ("%s:%s must be in %s exactly once, found %d %r: PACK.md ships it and the stay-loaded perk covers its crossbows "
                        "(install it, or change XBOW_PACK and the perk.archery.keepLoaded.items help)" % (XBOW_PACK + (B.MODS_DIR, len(_xpk), [os.path.basename(_x[0]) for _x in _xpk])))
_xpp, _xpv = _xpk[0]
def _xpack_items(p):
    if os.path.isdir(p):
        _names = [os.path.relpath(os.path.join(_r, _f), p).replace(os.sep, "/") for _r, _ds, _fl in os.walk(p) for _f in _fl]
        def _read(n):
            with open(os.path.join(p, *n.split("/")), "rb") as _fh:
                return _fh.read()
        _its = [n for n in _names if n.startswith("Server/Item/Items/") and n.endswith(".json") and os.path.basename(n).startswith("Weapon_Crossbow_")]
        return _names, [(n, json.loads(_read(n).decode("utf-8-sig"))) for n in _its]
    with zipfile.ZipFile(p) as _pz:
        _names = _pz.namelist()
        _its = [n for n in _names if n.startswith("Server/Item/Items/") and n.endswith(".json") and os.path.basename(n).startswith("Weapon_Crossbow_")]
        return _names, [(n, json.loads(_pz.read(n).decode("utf-8-sig"))) for n in _its]
_xpn, _xpitems = _xpack_items(_xpp)
assert _xpitems, "%s %s has no Server/Item/Items/**/Weapon_Crossbow_*.json any more (check the pack, PACK.md and the Server Setup help)" % (os.path.basename(_xpp), _xpv)
for _n, _d in _xpitems:
    _xbow_item("More Crossbow Tiers " + _xpv, _n, _d)
_xpcore = [n for n in _xpn if os.path.basename(n) in XBOW_CORE]
assert not _xpcore, "More Crossbow Tiers %s ships %r: it would replace the crossbow template / SwapFrom ladder checked from Assets.zip" % (_xpv, _xpcore)
print("crossbows stay loaded: %d crossbow item(s) on Template_Weapon_Crossbow with no Weapon / Interactions override (%d Assets.zip: %s; %d More Crossbow Tiers %s: %s), "
      "SwapFrom ladder = 6 x (StatsCondition Ammo k -> +k Weapon_Arrow_Crude), Ammo cap +6" % (
          len(_xitems) + len(_xpitems), len(_xitems), ", ".join(sorted(os.path.basename(n)[16:-5] for n in _xitems)),
          len(_xpitems), _xpv, ", ".join(sorted(os.path.basename(n)[16:-5] for n, _d in _xpitems))))
# 0.4.6 build checks (Overall-Level-Spec 4.12 + the crossbow extras), read in memory from Assets.zip
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
# 0.4.12: in-combat Mana regen rests on vanilla's combat pause = a NoDamageTaken condition on a positive Additive Mana regen entry
_mpause = [r for r in _mreg if str(r.get("RegenType", "")).lower() == "additive" and float(r.get("Amount") or 0) > 0 and float(r.get("Interval") or 0) > 0
           and any(c.get("Id") == "NoDamageTaken" and not c.get("Inverse") for c in (r.get("Conditions") or []))]
assert _mpause, "vanilla Mana.json has no Additive regen entry paused by NoDamageTaken any more - the in-combat Mana regen would never run"
print("combat state (skill:fn:combat, 0.4.13): in combat while that pause runs - its Delay is read from the engine condition at run time (Mana.json: %s s)"
      % ",".join(str(c.get("Delay")) for r in _mpause for c in r.get("Conditions") or [] if c.get("Id") == "NoDamageTaken"))
# 0.4.13 fix (Skyy 2026-10-02): Mana keeps regenerating while charging - the entries that also pause while Charging (inverse)
_mchg = [r for r in _mpause if any(c.get("Id") == "Charging" and c.get("Inverse") for c in (r.get("Conditions") or []))]
print("Mana regen while charging (0.4.13): %d of the %d paused Mana regen entries also pause while Charging (inverse) - SkyySkills refills "
      "there (out of combat the whole rate + boosts, in combat the in-combat rate)" % (len(_mchg), len(_mpause)))
if not _mchg:
    print("NOTE: vanilla Mana.json no longer pauses its regen while charging - the charging refill has nothing to add")
print("in-combat Mana regen: vanilla refills %s Mana a second, paused %s s after taking damage; SkyySkills refills %s%% of (vanilla + boosts) there" % (
    sum(float(r["Amount"]) / float(r["Interval"]) for r in _mpause), ",".join(str(c.get("Delay")) for r in _mpause for c in r.get("Conditions") or []
                                                                               if c.get("Id") == "NoDamageTaken"), MREG_DEF))
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
# ================= 0.4.8 SPELL COSTS / SPELL_DIVISOR (Skyy 2026-09-30; tools/skills_0_4_8_patch.py point 1) =================
# Found in game 2026-09-30: vanilla casters cost Mana per charged cast through their InteractionVars - a StatsCondition "Costs": {"Mana": N}
# (the cast check) and a ChangeStat "StatModifiers": {"Mana": -N} (the drain): wands 25, staffs 50 (Crystal_Red 0), spellbooks 100,
# Halloween_Broomstick 50, blunderbusses 50 (the plain one drains 0). This block GENERATES, from Assets.zip read in memory (read-only), an
# override of each such item for this jar's asset pack (same path = same id, it replaces the vanilla item for server and client) whose ONLY
# difference is those Mana numbers / SPELL_DIVISOR. No game file is checked into git; every self-check fails the build.
# 0.4.9 (tools/skills_0_4_9_patch.py point 1): those item vars only set what a cast SPENDS - the cast CHECK is the charged cast step's own
# interaction asset (Wand_Cast_Left_Charged ...; the engine resolves a string in the global interaction assets, an item var is read only by a
# Replace naming it). spell_int_plan overrides those interactions too (check = the one number the items behind it spend; the Simple staff
# step becomes a StatsCondition; the default drains / SPELL_DIVISOR) and spell_verify simulates every cast on vanilla and on the final assets.
# >>> SPELL GEN (pure Python: SkyySkills/test_skyyskills_0.4.8.py execs this block on synthetic items to prove the Parent / shape rules)
import copy as _scopy
import math as _smath
SPELL_COST_PARENTS = ("Wand_Cast_Left_Charged", "Spellbook_Cast_Hurl_Charged", "Staff_Cast_Summon_Charged", "Gun_Shoot_Flintlock_Charged")
SPELL_DRAIN_PARENTS = ("Wand_Cast_Cost", "Spellbook_Cast_Cost", "Staff_Cast_Cost", "Gun_Shoot_Cost")
SPELL_SKIP_BLOCKS = ("InteractionVars", "Armor", "Weapon")   # Armor / Weapon StatModifiers Mana are max-Mana bonuses, not costs
# 0.4.9: the keys a Simple charged cast step may have to be turned into a Mana check - exactly the keys of the vanilla wand check
# Wand_Cast_Left_Charged (a StatsCondition with RunTime / Next / Failed), so the converted step runs like the wand's
SPELL_GATE_KEYS = ("Type", "Costs", "$Comment", "RunTime", "Next", "Failed")
# 0.4.9: vanilla test interactions that carry a Mana number and that nothing references - left alone (checked unreferenced every build)
SPELL_INT_TESTS = ("StatsCondition",)
# 0.4.9: keys of an interaction that never name another interaction (not walked by spell_casts)
_SPELL_WALK_SKIP = ("Type", "$Comment", "Var", "Effects", "Parent", "Tags", "Config", "ItemToRemove", "ItemToAdd", "Cooldown", "Costs",
                    "StatModifiers", "DefaultValue", "DefaultOk", "RunTime", "Behaviour")


def spell_fail(msg):
    raise SystemExit("spell costs: " + msg)


def spell_new(v, div):
    """the new Mana number: |v| / div rounded half up, at least 1; 0 stays 0; the sign is kept (a drain stays negative)"""
    if isinstance(v, bool) or not isinstance(v, int):
        spell_fail("a Mana number %r is not a whole number" % (v,))
    if v == 0:
        return 0
    m = int(_smath.floor(abs(v) / float(div) + 0.5))
    if m < 1:
        m = 1
    return m if v > 0 else -m


def _spell_hits(x, path, out):
    if isinstance(x, dict):
        for f in ("Costs", "StatModifiers"):
            if isinstance(x.get(f), dict) and "Mana" in x[f]:
                out.append((tuple(path), f, x[f]["Mana"]))
        for k in x:
            _spell_hits(x[k], path + [k], out)
    elif isinstance(x, list):
        for i in range(len(x)):
            _spell_hits(x[i], path + [i], out)
    return out


def _spell_at(d, path):
    for p in path:
        d = d[p]
    return d


def _spell_diff(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        if list(a.keys()) != list(b.keys()):
            out.append((tuple(path), "keys"))
            return out
        for k in a:
            _spell_diff(a[k], b[k], path + [k], out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((tuple(path), "len"))
            return out
        for i in range(len(a)):
            _spell_diff(a[i], b[i], path + [i], out)
    elif type(a) != type(b) or a != b:
        out.append((tuple(path), "value"))
    return out


def spell_plan(items, div):
    """items = {item id: (asset path, parsed JSON)} of Server/Item/Items/**. Returns (plan, inherits, unchanged):
    plan = [(id, path, [(entry path, field, old, new)], new JSON)] for every item whose Mana numbers change (sorted by id);
    inherits = {item id: the ancestor whose InteractionVars - and so Mana cost - it takes by Parent}; unchanged = ids whose Mana numbers
    are all 0. Anything this build does not know the meaning of stops the build (spell_fail)."""
    own = {}
    for iid in sorted(items):
        path, d = items[iid]
        if not isinstance(d, dict):
            spell_fail("%s is not a JSON object" % iid)
        outside = _spell_hits(dict((k, v) for k, v in d.items() if k not in SPELL_SKIP_BLOCKS), [], [])
        for (hp, f, v) in outside:
            if f == "Costs" or (isinstance(v, (int, float)) and not isinstance(v, bool) and v < 0):
                spell_fail("%s has a Mana %s outside InteractionVars at %s - not a pattern this build knows" % (iid, f, "/".join(str(x) for x in hp)))
        iv = d.get("InteractionVars")
        if iv is None:
            continue
        if not isinstance(iv, dict):
            spell_fail("%s: InteractionVars is not an object" % iid)
        hits = _spell_hits(iv, ["InteractionVars"], [])
        if not hits:
            continue
        ents = []
        for (hp, f, v) in hits:
            where = "/".join(str(x) for x in hp)
            if len(hp) != 4 or hp[0] != "InteractionVars" or hp[2] != "Interactions" or not isinstance(hp[3], int):
                spell_fail("%s: a Mana %s at %s (expected InteractionVars/<var>/Interactions/<n>)" % (iid, f, where))
            var = iv[hp[1]]
            ent = _spell_at(d, hp)
            if not isinstance(var, dict) or sorted(var.keys()) != ["Interactions"] or len(var["Interactions"]) != 1:
                spell_fail("%s: var %s is not {\"Interactions\": [one entry]}: %s" % (iid, hp[1], json.dumps(var)[:200]))
            if sorted(ent.keys()) != sorted(["Parent", f]):
                spell_fail("%s: var %s entry has keys %s (expected Parent + %s only)" % (iid, hp[1], sorted(ent.keys()), f))
            if list(ent[f].keys()) != ["Mana"]:
                spell_fail("%s: var %s %s names more than Mana: %s" % (iid, hp[1], f, json.dumps(ent[f])))
            parents = SPELL_COST_PARENTS if f == "Costs" else SPELL_DRAIN_PARENTS
            if ent["Parent"] not in parents:
                spell_fail("%s: var %s %s has Parent %r - not a known Mana %s interaction %s" % (
                    iid, hp[1], f, ent["Parent"], "cast check" if f == "Costs" else "drain", list(parents)))
            if isinstance(v, bool) or not isinstance(v, int):
                spell_fail("%s: var %s %s Mana %r is not a whole number" % (iid, hp[1], f, v))
            if (f == "Costs" and v < 0) or (f == "StatModifiers" and v > 0):
                spell_fail("%s: var %s %s Mana %r has the wrong sign (a cast check is >= 0, a drain <= 0)" % (iid, hp[1], f, v))
            ents.append((hp, f, v, spell_new(v, div)))
        own[iid] = ents

    def chain(iid):
        out, seen = [iid], set([iid])
        while True:
            p = items[out[-1]][1].get("Parent")
            if p is None:
                return out
            if not isinstance(p, str):
                spell_fail("%s: Parent %r is not an id" % (out[-1], p))
            if p not in items:
                return out          # a Parent outside Server/Item/Items (none today): nothing to inherit from here
            if p in seen:
                spell_fail("Parent loop at %s" % p)
            seen.add(p)
            out.append(p)
    inherits = {}
    for iid in sorted(items):
        if iid in own:
            continue            # its own Mana entries are overridden in its own file (a Mana parent of it is overridden too)
        ch = chain(iid)
        if not any(a in own for a in ch[1:]):
            continue
        first = [a for a in ch if "InteractionVars" in items[a][1]][0]
        if first not in own:
            spell_fail("%s inherits a Mana cost by Parent (%s), but %s has its own InteractionVars without one - whether the engine merges "
                       "the two is not known, so this build cannot tell which cost %s pays" % (iid, " -> ".join(ch), first, iid))
        inherits[iid] = first   # its own file stays vanilla and names the overridden parent: it gets the new cost from there
    plan, unchanged = [], []
    for iid in sorted(own):
        ents = own[iid]
        path, d = items[iid]
        if all(e[2] == 0 for e in ents):
            unchanged.append(iid)
            continue
        nc = [e for e in ents if e[1] == "Costs"]
        nd = [e for e in ents if e[1] == "StatModifiers"]
        if len(nc) != 1 or len(nd) != 1:
            spell_fail("%s has %d Mana cast check(s) and %d drain(s) - expected exactly one of each" % (iid, len(nc), len(nd)))
        new = _scopy.deepcopy(d)
        for (hp, f, v, nv) in ents:
            _spell_at(new, hp)[f]["Mana"] = nv
        diff = _spell_diff(d, new, [], [])
        want = sorted(tuple(list(hp) + [f, "Mana"]) for (hp, f, v, nv) in ents if v != nv)
        if any(why != "value" for p, why in diff) or sorted(p for p, why in diff) != want:
            spell_fail("%s: the generated item differs from vanilla in more than its Mana numbers: %s" % (iid, diff[:6]))
        back = _scopy.deepcopy(new)
        for (hp, f, v, nv) in ents:
            _spell_at(back, hp)[f]["Mana"] = v
        if back != d or json.dumps(back) != json.dumps(d):
            spell_fail("%s: putting the old numbers back does not give the vanilla item" % iid)
        plan.append((iid, path, list(ents), new))
    return plan, inherits, unchanged


def _spell_eff(x, ints, src, depth):
    """(fields, source of each field) of interaction x with what it inherits from its Parent interaction chain: a field it sets itself
    wins (the asset codec's field-level inheritance). A Costs / StatModifiers block without Mana over a parent block WITH Mana is refused
    (whether the engine merges the two blocks is not known)."""
    p = x.get("Parent")
    if not (isinstance(p, str) and p in ints):
        return dict(x), dict((k, src) for k in x)
    if depth > 30:
        spell_fail("interaction Parent chain too long (a loop?) at %s" % p)
    pf, ps = _spell_eff(ints[p], ints, ("int", p), depth + 1)
    for f in ("Costs", "StatModifiers"):
        if isinstance(x.get(f), dict) and "Mana" not in x[f] and isinstance(pf.get(f), dict) and "Mana" in pf[f]:
            spell_fail("%s sets %s without Mana over its Parent %s's Mana %s - whether the engine merges the two is not known" % (
                src, f, p, pf[f]["Mana"]))
    pf.update(x)
    for k in x:
        ps[k] = src
    return pf, ps


def spell_casts(item, ints, roots):
    """0.4.9 GATE SIMULATION of one item: what its interactions check and spend in Mana, by the ENGINE's rules (research/Mana-Cost-And-
    Regen-Research.md 1.2, HytaleServer 0.6.8 bytecode - 0.4.8 assumed an item var named like an interaction replaced it, which is false):
      - a string names the global interaction asset (ChargingInteraction.compile -> Interaction.getInteractionOrUnknown): an item
        InteractionVars entry of the same name is never used; an item slot / a var value names a root interaction (its Interactions);
      - an item's InteractionVars are read only by a Replace naming that Var (ReplaceInteraction.doReplace), else its DefaultValue;
      - an inline interaction inherits every field of its Parent interaction it does not set (Type, Costs, Next, ...);
      - a StatsCondition checks its OWN Costs (fails when Mana < cost, drains nothing; Failed runs); a ChangeStat never fails.
    item = the item JSON (Parent already resolved). Returns {"casts": [[check Mana, check source, [(spend, source)], where]], "free":
    [(spend, source, where)] (a Mana drain with no Mana check before it), "fail": [...] (a drain on a check's Failed branch), "gain":
    [...] (a Mana gain)}. Sources: ("int", asset id) / ("var", var name) / ("inline", owner). A spend is the (negative) Mana number."""
    iv = item.get("InteractionVars") or {}
    if not isinstance(iv, dict):
        iv = {}
    out = {"casts": [], "free": [], "fail": [], "gain": []}
    seen = set()

    def ckey(ctx):
        return id(ctx) if isinstance(ctx, list) else ctx

    def root_ref(sid, ctx, depth, stack):
        if sid in roots:
            key = ("root", sid, ckey(ctx))
            if key in seen:
                return
            seen.add(key)
            node(roots[sid].get("Interactions"), ctx, depth + 1, sid, stack)
        elif sid in ints:
            int_ref(sid, ctx, depth, stack)

    def int_ref(sid, ctx, depth, stack):
        if sid in ints:
            if sid in stack:
                return
            key = ("int", sid, ckey(ctx))
            if key in seen:
                return
            seen.add(key)
            inter(ints[sid], ctx, depth + 1, ("int", sid), stack + (sid,))
        elif sid in roots:
            root_ref(sid, ctx, depth, stack)

    def var_value(v, ctx, depth, stack, var):
        if isinstance(v, str):
            root_ref(v, ctx, depth, stack)
        elif isinstance(v, dict):
            for e in (v.get("Interactions") or []):
                if isinstance(e, str):
                    int_ref(e, ctx, depth, stack)
                elif isinstance(e, dict):
                    inter(e, ctx, depth + 1, ("var", var), stack)

    def record(val, src, ctx, where):
        if isinstance(ctx, list):
            ctx[2].append((val, src))
        elif ctx == "fail":
            out["fail"].append((val, src, where))
        else:
            out["free"].append((val, src, where))

    def inter(x, ctx, depth, src, stack):
        if depth > 200:
            spell_fail("interaction nesting deeper than 200 at %s" % (src,))
        f, fs = _spell_eff(x, ints, src, 0)
        t = f.get("Type")
        if t == "Replace" and "Var" in f:
            if f["Var"] in iv:
                var_value(iv[f["Var"]], ctx, depth + 1, stack, f["Var"])
            else:
                var_value(f.get("DefaultValue"), ctx, depth + 1, stack, "(default of %s)" % f["Var"])
            return
        costs, mods = f.get("Costs"), f.get("StatModifiers")
        gate = None
        if t == "StatsCondition" and isinstance(costs, dict) and "Mana" in costs:
            gate = [costs["Mana"], fs.get("Costs"), [], src]
            out["casts"].append(gate)
        elif isinstance(costs, dict) and "Mana" in costs:
            spell_fail("%s has a Mana Costs on a %s interaction (only a StatsCondition checks it)" % (src, t))
        if isinstance(mods, dict) and "Mana" in mods:
            v = mods["Mana"]
            if t != "ChangeStat" or isinstance(v, bool) or not isinstance(v, (int, float)):
                spell_fail("%s has a Mana StatModifiers %r on a %s interaction - not a pattern this build knows" % (src, v, t))
            if v < 0:
                record(v, fs.get("StatModifiers"), ctx, src)
            elif v > 0:
                out["gain"].append((v, fs.get("StatModifiers"), src))
        for k in f:
            if k in _SPELL_WALK_SKIP:
                continue
            if gate is not None and k == "Next":
                node(f[k], gate, depth + 1, src, stack)
            elif gate is not None and k == "Failed":
                node(f[k], "fail", depth + 1, src, stack)
            else:
                node(f[k], ctx, depth + 1, src, stack)

    def node(x, ctx, depth, owner, stack):
        if isinstance(x, str):
            int_ref(x, ctx, depth, stack)
        elif isinstance(x, list):
            for e in x:
                node(e, ctx, depth + 1, owner, stack)
        elif isinstance(x, dict):
            if "Type" in x or "Parent" in x:
                inter(x, ctx, depth + 1, ("inline", owner[1] if isinstance(owner, tuple) else owner), stack)
            else:
                for k in x:
                    if k not in _SPELL_WALK_SKIP:
                        node(x[k], ctx, depth + 1, owner, stack)
    slots = item.get("Interactions")
    if isinstance(slots, dict):
        for k in slots:
            v = slots[k]
            if isinstance(v, str):
                root_ref(v, None, 0, ())
            else:
                var_value(v, None, 0, (), "(slot %s)" % k)
    return out


def _spell_refs(x, sid, key):
    """how often the string sid appears in x as a value (not as a Type)"""
    n = 0
    if isinstance(x, dict):
        for k in x:
            if k != "Type":
                n += _spell_refs(x[k], sid, k)
    elif isinstance(x, list):
        for e in x:
            n += _spell_refs(e, sid, key)
    elif isinstance(x, str) and x == sid and key != "Type":
        n += 1
    return n


def _spell_eff_item(items, iid, depth):
    x = items[iid]
    p = x.get("Parent")
    if isinstance(p, str) and p in items and depth < 30:
        m = dict(_spell_eff_item(items, p, depth + 1))
        m.update(x)
        return m
    return x


def spell_int_plan(items, ints, int_paths, roots, div):
    """0.4.9: the charged cast checks and default drains (Server/Item/Interactions) that must change so a cast CHECKS what it SPENDS.
    items = {item id: JSON} AFTER the item overrides (spell_plan); ints / roots = vanilla {id: JSON}; int_paths = {id: asset path}.
    Returns (plan, fams, heirs, tests): plan = [(id, path, kind, old, new, new JSON)] sorted by id - kind "check" (Costs.Mana set to what
    the items behind it spend), "check+" (a Simple charged step turned into a StatsCondition with the Mana check it never had; old None),
    "drain" (StatModifiers.Mana / div); fams = {check id: (new check, [items that spend it], [items behind it that spend 0])}; heirs =
    [(interaction, the overridden one it inherits by Parent)]; tests = the unreferenced test assets left alone. Anything unknown stops."""
    for sid in SPELL_COST_PARENTS + SPELL_DRAIN_PARENTS:
        if sid not in ints:
            spell_fail("the interaction %s is not in Assets.zip any more - the cast check / drain list needs a look" % sid)
        if "Parent" in ints[sid]:
            spell_fail("the interaction %s has a Parent (%r) - not a pattern this build knows" % (sid, ints[sid]["Parent"]))
    for rid in sorted(roots):
        h = _spell_hits(roots[rid], [], [])
        if h:
            spell_fail("the root interaction %s carries a Mana number %s - not a pattern this build knows" % (rid, h[:3]))
    gates, drains, tests = {}, {}, []
    for sid in sorted(ints):
        d = ints[sid]
        for (hp, f, v) in _spell_hits(d, [], []):
            where = "%s %s" % (sid, "/".join(str(x) for x in hp) or "(top)")
            if sid in SPELL_INT_TESTS:
                if sid not in tests:
                    tests.append(sid)
                continue
            if hp != ():
                spell_fail("%s: a Mana %s inside the interaction (not at its top) - not a pattern this build knows" % (where, f))
            if list(d[f].keys()) != ["Mana"]:
                spell_fail("%s: %s names more than Mana: %s" % (where, f, json.dumps(d[f])))
            if isinstance(v, bool) or not isinstance(v, int):
                spell_fail("%s: Mana %r is not a whole number" % (where, v))
            if f == "Costs" and sid in SPELL_COST_PARENTS and d.get("Type") == "StatsCondition" and v >= 0:
                gates[sid] = v
            elif f == "StatModifiers" and sid in SPELL_DRAIN_PARENTS and d.get("Type") == "ChangeStat" and v <= 0:
                drains[sid] = v
            else:
                spell_fail("%s: a Mana %s %r on a %s interaction that is not a known cast check %s or default drain %s" % (
                    where, f, v, d.get("Type"), list(SPELL_COST_PARENTS), list(SPELL_DRAIN_PARENTS)))
    for sid in SPELL_DRAIN_PARENTS:
        if sid not in drains:
            spell_fail("the default drain %s has no Mana number any more" % sid)
    # a Simple charged step without Costs becomes a StatsCondition (the Mana check it never had) - only with the wand check's keys
    conv = []
    for sid in SPELL_COST_PARENTS:
        if sid in gates:
            continue
        d = ints[sid]
        if d.get("Type") != "Simple" or "Costs" in d or not all(k in SPELL_GATE_KEYS for k in d) or "Next" not in d or "Failed" not in d:
            spell_fail("the charged cast step %s is neither a StatsCondition with a Mana cost nor a plain Simple step with Next + Failed "
                       "(keys %s) - not a pattern this build knows" % (sid, list(d.keys())))
        if list(d.keys())[0] != "Type":
            spell_fail("%s: Type is not its first key" % sid)
        conv.append(sid)
    for sid in tests:
        refs = sum(_spell_refs(x, sid, None) for x in list(items.values()) + list(ints.values()) + list(roots.values()))
        if refs:
            spell_fail("the test interaction %s (Mana %s) is referenced %d time(s) - it is no longer a test asset" % (
                sid, _spell_hits(ints[sid], [], []), refs))
    # interactions that inherit one of these by Parent get the new number too; one that inherits a converted step would become a check
    heirs = []
    for sid in sorted(ints):
        p, seen = ints[sid].get("Parent"), set()
        while isinstance(p, str) and p in ints and p not in seen:
            seen.add(p)
            if p in SPELL_COST_PARENTS + SPELL_DRAIN_PARENTS:
                heirs.append((sid, p))
                if p in conv:
                    spell_fail("the interaction %s inherits %s by Parent - turning %s into a Mana check would change it too" % (sid, p, p))
                break
            p = ints[p].get("Parent")
    # planning world: the default drains / div, every charged step a check - which spends each check guards, item by item
    probe = dict(ints)
    for sid, v in drains.items():
        nd = _scopy.deepcopy(ints[sid])
        nd["StatModifiers"]["Mana"] = spell_new(v, div)
        probe[sid] = nd
    for sid in SPELL_COST_PARENTS:
        nd = _scopy.deepcopy(ints[sid])
        nd["Type"] = "StatsCondition"
        nd["Costs"] = {"Mana": gates.get(sid, 1)}
        probe[sid] = nd
    spend = dict((sid, {}) for sid in SPELL_COST_PARENTS)
    for iid in sorted(items):
        r = spell_casts(_spell_eff_item(items, iid, 0), probe, roots)
        if r["free"] or r["fail"] or r["gain"]:
            spell_fail("%s spends / gains Mana outside a known cast check: free %s, on a Failed branch %s, gains %s" % (
                iid, r["free"][:3], r["fail"][:3], r["gain"][:3]))
        for c in r["casts"]:
            if c[1] is None or c[1][0] != "int" or c[1][1] not in SPELL_COST_PARENTS:
                spell_fail("%s: a Mana check from %s - only the known charged cast steps check Mana" % (iid, c[1]))
            spend[c[1][1]][iid] = -sum(v for v, src in c[2])
    fams = {}
    for sid in SPELL_COST_PARENTS:
        pos = sorted(set(v for v in spend[sid].values() if v > 0))
        if len(pos) != 1:
            spell_fail("the items behind the cast check %s spend %s Mana - one check serves them all, so they must spend one number: %s" % (
                sid, pos or "no", sorted(spend[sid].items())[:8]))
        fams[sid] = (pos[0], sorted(i for i, v in spend[sid].items() if v > 0), sorted(i for i, v in spend[sid].items() if v == 0))
    plan = []
    for sid in sorted(set(SPELL_COST_PARENTS + SPELL_DRAIN_PARENTS)):
        d = ints[sid]
        new = _scopy.deepcopy(d)
        if sid in drains:
            kind, old, nv = "drain", drains[sid], spell_new(drains[sid], div)
            new["StatModifiers"]["Mana"] = nv
            want = [("StatModifiers", "Mana")] if nv != old else []
        elif sid in gates:
            kind, old, nv = "check", gates[sid], fams[sid][0]
            new["Costs"]["Mana"] = nv
            want = [("Costs", "Mana")] if nv != old else []
        else:
            kind, old, nv = "check+", None, fams[sid][0]
            new = dict([("Type", "StatsCondition"), ("Costs", {"Mana": nv})] + [(k, _scopy.deepcopy(d[k])) for k in list(d.keys())[1:]])
            want = None
        if want is not None:
            diff = _spell_diff(d, new, [], [])
            if any(why != "value" for p, why in diff) or sorted(p for p, why in diff) != sorted(want):
                spell_fail("%s: the generated interaction differs from vanilla in more than its Mana number: %s" % (sid, diff[:6]))
            back = _scopy.deepcopy(new)
            back["StatModifiers" if kind == "drain" else "Costs"]["Mana"] = old
        else:
            if list(new.keys()) != ["Type", "Costs"] + list(d.keys())[1:] or new["Type"] != "StatsCondition":
                spell_fail("%s: the converted check does not have the vanilla keys + Costs after Type" % sid)
            back = dict((k, _scopy.deepcopy(new[k])) for k in new if k != "Costs")
            back["Type"] = d["Type"]
        if back != d or json.dumps(back) != json.dumps(d):
            spell_fail("%s: putting the old number back does not give the vanilla interaction" % sid)
        if not (int_paths[sid].startswith("Server/Item/Interactions/") and int_paths[sid].endswith("/%s.json" % sid)):
            spell_fail("%s: unexpected asset path %s" % (sid, int_paths[sid]))
        plan.append((sid, int_paths[sid], kind, old, nv, new))
    return plan, fams, heirs, tests


def spell_verify(items_old, items_new, ints_old, ints_new, roots, div):
    """0.4.9 gate simulation on the FINAL assets (items + interactions as this jar ships them) against vanilla, item by item: every Mana
    spend is behind a Mana check, the check = what the cast spends = the vanilla spend / div (rounded like spell_new), a Mana check only
    comes from a charged cast step asset (an item var named like one is never used - it stays dead data), one check per item, nothing
    that cost Mana in vanilla became free. Returns [(item id, check id, old check (0 = vanilla had none), new check, old spend, new
    spend)] sorted by id (spends as positive numbers)."""
    rows = []
    for iid in sorted(items_new):
        rn = spell_casts(_spell_eff_item(items_new, iid, 0), ints_new, roots)
        ro = spell_casts(_spell_eff_item(items_old, iid, 0), ints_old, roots)
        if rn["free"] or rn["fail"] or rn["gain"]:
            spell_fail("gate simulation: %s spends Mana without a check first (%s), on a Failed branch (%s) or gains Mana (%s)" % (
                iid, rn["free"][:3], rn["fail"][:3], rn["gain"][:3]))
        if not rn["casts"]:
            if ro["casts"] or ro["free"]:
                spell_fail("gate simulation: %s had a Mana cost in vanilla and has none now" % iid)
            continue
        gids = sorted(set(c[1][1] for c in rn["casts"] if c[1] and c[1][0] == "int"))
        if len(gids) != 1 or any(c[1] is None or c[1][0] != "int" or c[1][1] not in SPELL_COST_PARENTS for c in rn["casts"]):
            spell_fail("gate simulation: %s has Mana checks %s - expected exactly one known charged cast step" % (
                iid, [c[1] for c in rn["casts"]]))
        spend_new = sorted(v for c in rn["casts"] for v, src in c[2])
        spend_old = sorted(v for c in ro["casts"] for v, src in c[2]) + sorted(v for v, src, w in ro["free"])
        if sorted(spend_new) != sorted(spell_new(v, div) for v in spend_old):
            spell_fail("gate simulation: %s spends %s now, vanilla %s - expected vanilla / %d" % (iid, spend_new, spend_old, div))
        for c in rn["casts"]:
            sp = -sum(v for v, src in c[2])
            if sp != 0 and c[0] != sp:
                spell_fail("gate simulation: %s checks %s Mana but spends %s" % (iid, c[0], sp))
            if sp == 0 and spend_old:
                spell_fail("gate simulation: %s spent %s in vanilla and spends 0 now" % (iid, spend_old))
        oc = [c[0] for c in ro["casts"] if c[1] == ("int", gids[0])]
        rows.append((iid, gids[0], oc[0] if oc else 0, rn["casts"][0][0], -sum(spend_old), -sum(spend_new)))
    return rows
# <<< SPELL GEN
assert SPELL_DIVISOR == 5 and spell_new(25, 5) == 5 and spell_new(-50, 5) == -10 and spell_new(100, 5) == 20 and spell_new(0, 5) == 0
assert spell_new(3, 5) == 1 and spell_new(-2, 5) == -1 and spell_new(12, 5) == 2 and spell_new(13, 5) == 3 and spell_new(1, 5) == 1
# 0.4.15 STAFF HANDOVER (research/SkyyArmory-Spec.md 15.3; Skyy 2026-10-03: "MAGE STAFFS get their Mana / damage ladder WITH the wands"):
# the 8 ladder staffs get their own Charging root and Mana per metal from SkyyArmory 0.1+, which ships their item files. This jar no longer
# generates an override for them - they leave SPELL_ITEMS before spell_plan, so the gate simulation never sees them; their vanilla files
# stay in memory (ARMORY_ITEMS) for the kit lookup's fallback (what a cast checks / spends on the vanilla file behind this jar's
# interactions). SkyySkills 0.4.15 and SkyyArmory 0.1 deploy and roll back TOGETHER.
ARMORY_OWNED = ["Weapon_Staff_Wood", "Weapon_Staff_Copper", "Weapon_Staff_Iron", "Weapon_Staff_Thorium", "Weapon_Staff_Cobalt",
                "Weapon_Staff_Adamantite", "Weapon_Staff_Mithril", "Weapon_Staff_Onyxium"]
ARMORY_ITEMS = {}   # id -> (asset path, vanilla JSON)
with zipfile.ZipFile(ASSETS) as _sz:
    _snames = _sz.namelist()

    def _sids(prefix):
        out = {}
        for n in _snames:
            if n.startswith(prefix) and n.endswith(".json"):
                out.setdefault(os.path.basename(n)[:-5], []).append(n)
        return out
    _si, _sn, _sr = _sids("Server/Item/Items/"), _sids("Server/Item/Interactions/"), _sids("Server/Item/RootInteractions/")
    for _m, _w in ((_si, "item"), (_sn, "interaction"), (_sr, "root interaction")):
        _dup = sorted(k for k, v in _m.items() if len(v) > 1)
        if _dup:
            spell_fail("Assets.zip has %d %s id(s) more than once: %s" % (len(_dup), _w, _dup[:5]))

    def _sread(n, strict=False):
        t = _sz.read(n).decode("utf-8-sig")
        if not strict:
            return json.loads(t)

        def _hook(pairs):
            ks = [k for k, v in pairs]
            if len(set(ks)) != len(ks):
                spell_fail("%s has a duplicate JSON key %s" % (n, sorted(set(k for k in ks if ks.count(k) > 1))))
            return dict(pairs)
        return json.loads(t, object_pairs_hook=_hook)
    SPELL_ITEMS = dict((k, (v[0], _sread(v[0]))) for k, v in _si.items())
    # 0.4.15 (spec 15.3 (a)): the SkyyArmory-owned staffs leave the plan; nothing may inherit from them by Parent (none in Assets.zip today)
    for _aid in ARMORY_OWNED:
        if _aid not in SPELL_ITEMS:
            spell_fail("%s (owned by SkyyArmory since SkyySkills 0.4.15) is not in Assets.zip any more - the staff handover list needs a look" % _aid)
        ARMORY_ITEMS[_aid] = SPELL_ITEMS.pop(_aid)
    _aheirs = sorted(_k for _k, _v in SPELL_ITEMS.items() if isinstance(_v[1], dict) and _v[1].get("Parent") in ARMORY_OWNED)
    if _aheirs:
        spell_fail("%s inherit(s) a SkyyArmory-owned staff by Parent - the staff handover would change them too" % _aheirs)
    SPELL_INTS = dict((k, _sread(v[0])) for k, v in _sn.items())
    SPELL_ROOTS = dict((k, _sread(v[0])) for k, v in _sr.items())
    SPELL_PLAN, SPELL_INHERITS, SPELL_UNCHANGED = spell_plan(SPELL_ITEMS, SPELL_DIVISOR)
    for _iid, _p, _e, _nj in SPELL_PLAN:       # the overridden files have no duplicate key (json.loads would have kept only the last)
        if _sread(_p, strict=True) != SPELL_ITEMS[_iid][1]:
            spell_fail("%s parses differently with the duplicate-key check" % _iid)
if len(SPELL_PLAN) < 20:
    spell_fail("only %d Mana-costing items found in Assets.zip (32 on 2026-09-30) - check the scan" % len(SPELL_PLAN))
SPELL_FILES = {}
SPELL_TABLE = []    # (id, old cast check, new, old drain, new drain) - sorted by id
for _iid, _p, _e, _nj in SPELL_PLAN:
    _txt = json.dumps(_nj, indent=2, ensure_ascii=True) + "\n"
    assert _p.startswith("Server/Item/Items/") and _p.endswith("/%s.json" % _iid) and _p not in SPELL_FILES
    assert json.loads(_txt) == _nj and all(ord(ch) < 128 for ch in _txt)
    SPELL_FILES[_p] = _txt
    _c = [x for x in _e if x[1] == "Costs"][0]
    _dr = [x for x in _e if x[1] == "StatModifiers"][0]
    SPELL_TABLE.append((_iid, _c[2], _c[3], -_dr[2], -_dr[3]))
SPELL_IDS = [x[0] for x in SPELL_TABLE]
# the kit weapons Skyy's numbers were chosen for (Mage 30 = 3 staff casts, Priest 30 = 6 wand casts)
_sk = dict((x[0], x) for x in SPELL_TABLE)
# 0.4.15: the Mage kit staff is SkyyArmory's now (its Wood staff is checked against the pinned SkyyArmory jar below: check 10, spend 10)
assert _sk["Weapon_Wand_Wood"][2] == 5 and not set(ARMORY_OWNED) & set(_sk), (_sk.get("Weapon_Wand_Wood"), sorted(set(ARMORY_OWNED) & set(_sk)))
assert len(SPELL_PLAN) == len(SPELL_TABLE) and all(_t[0] not in ARMORY_OWNED for _t in SPELL_TABLE)
# ---- 0.4.9 (tools/skills_0_4_9_patch.py point 1): the cast CHECKS (charged cast step interactions) + the default drains, then the gate
# simulation of every item on vanilla and on the final assets
_s_items_old = dict((k, v[1]) for k, v in SPELL_ITEMS.items())
_s_items_new = dict(_s_items_old)
for _iid, _p, _e, _nj in SPELL_PLAN:
    _s_items_new[_iid] = _nj
_s_int_paths = dict((k, v[0]) for k, v in _sn.items())
SPELL_INT_PLAN, SPELL_FAMS, SPELL_HEIRS, SPELL_TESTS = spell_int_plan(_s_items_new, SPELL_INTS, _s_int_paths, SPELL_ROOTS, SPELL_DIVISOR)
_s_dups = []


def _s_hook(pairs):
    _ks = [k for k, v in pairs]
    _s_dups.extend(sorted(set(k for k in _ks if _ks.count(k) > 1)))
    return dict(pairs)
with zipfile.ZipFile(ASSETS) as _sz:     # the overridden interaction files have no duplicate key either
    for _sid, _p, _k, _o, _n, _nj in SPELL_INT_PLAN:
        del _s_dups[:]
        if json.loads(_sz.read(_p).decode("utf-8-sig"), object_pairs_hook=_s_hook) != SPELL_INTS[_sid] or _s_dups:
            spell_fail("%s has a duplicate JSON key %s" % (_p, _s_dups))
    # nothing outside Server/Item (NPC roles, entities, drops, ...) names an overridden interaction or a Charging step leading to one: mobs
    # attack with their own interactions, so these overrides cannot change a mob (research 1.4); World/ and Prefabs/ hold no interactions
    _s_lead = sorted(set(SPELL_COST_PARENTS + SPELL_DRAIN_PARENTS) | set(
        _k for _k, _v in SPELL_INTS.items() if isinstance(_v, dict) and _v.get("Type") == "Charging"
        and any(_x in SPELL_COST_PARENTS for _x in (_v.get("Next") or {}).values() if isinstance(_x, str))))
    _s_needles = [('"%s"' % _x).encode("utf-8") for _x in _s_lead]
    _s_out = []
    _s_nscan = 0
    for _n in _sz.namelist():
        if _n.startswith("Server/") and _n.endswith(".json") and not _n.startswith(("Server/Item/", "Server/World/", "Server/Prefabs/")):
            _s_nscan += 1
            _b = _sz.read(_n)
            for _nd in _s_needles:
                if _nd in _b:
                    _s_out.append("%s names %s" % (_n, _nd.decode()))
    if _s_out:
        spell_fail("assets outside Server/Item name an overridden interaction or its Charging step (a mob or another system would change "
                   "too): %s" % _s_out[:6])
_s_ints_new = dict(SPELL_INTS)
for _sid, _p, _k, _o, _n, _nj in SPELL_INT_PLAN:
    _s_ints_new[_sid] = _nj
SPELL_GATES = spell_verify(_s_items_old, _s_items_new, SPELL_INTS, _s_ints_new, SPELL_ROOTS, SPELL_DIVISOR)
SPELL_INT_IDS = [x[0] for x in SPELL_INT_PLAN]
for _sid, _p, _k, _o, _n, _nj in SPELL_INT_PLAN:
    _txt = json.dumps(_nj, indent=2, ensure_ascii=True) + "\n"
    assert _p.startswith("Server/Item/Interactions/") and _p.endswith("/%s.json" % _sid) and _p not in SPELL_FILES
    assert json.loads(_txt) == _nj and all(ord(ch) < 128 for ch in _txt)
    SPELL_FILES[_p] = _txt
_sg = dict((x[0], x) for x in SPELL_GATES)
# the kit weapons: the Priest wand checks 5 and spends 5 (vanilla 25 / 25), the Mage staff checks 10 (vanilla: no check) and spends 10
assert _sg["Weapon_Wand_Wood"][1:] == ("Wand_Cast_Left_Charged", 25, 5, 25, 5), _sg.get("Weapon_Wand_Wood")
# 0.4.15 (spec 15.3 (b)): the staff check still serves the other staff-folder items (all spend 10) and Crystal_Red / Crystal_Ice (0) - its
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
assert len(SPELL_INT_PLAN) == 8 and sorted(SPELL_FAMS) == sorted(SPELL_COST_PARENTS) and len(SPELL_GATES) >= len(SPELL_PLAN), (
    len(SPELL_INT_PLAN), len(SPELL_GATES))
assert all(x[0] in _sg for x in SPELL_TABLE if x[4] > 0), "an overridden item that spends Mana is missing from the gate table"
SPELL_FREE = sorted(x[0] for x in SPELL_GATES if x[5] == 0)     # items that spend 0 behind a check (need the check's Mana present)
# no other Skyy mod of the live set (tools/deploy_set.py SET, its pinned jars) and no pack mod (PACK_THIRD_PARTY, found in the Mods folder by
# its manifest, read only) ships one of these item files or ids - two overrides of one item would fight over it
import re as _sre
_dst = open(os.path.join(os.path.dirname(HERE), "tools", "deploy_set.py"), encoding="utf-8").read()
_s0 = _dst.index("SET = [")
_pins = _sre.findall(r'\("(Skyy\w+)", "([0-9][0-9.]*)"\)', _dst[_s0:_dst.index("\n]\n", _s0)])
_packs = _sre.findall(r'"([^"]+:[^"]+)"', _sre.search(r"PACK_THIRD_PARTY = \[(.*?)\]", _dst).group(1))
# any SkyySkills pin, not a fixed version: once the SET pin is bumped to this version the build must still run (e.g. after a Hytale update)
assert any(m == "SkyySkills" for m, v in _pins) and len(_pins) >= 20 and _packs, (_pins, _packs)


def _spell_clash(names, armory=False):
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
_pk_found, _other, _pk_mana = [], [], []
for _f in (sorted(os.listdir(B.MODS_DIR)) if os.path.isdir(B.MODS_DIR) else []):
    _p = os.path.join(B.MODS_DIR, _f)
    try:
        if os.path.isdir(_p):
            with open(os.path.join(_p, "manifest.json"), "rb") as _mf:
                _man = json.loads(_mf.read().decode("utf-8-sig"))
            _nm = [os.path.relpath(os.path.join(_r, _x), _p).replace(os.sep, "/") for _r, _ds, _fl in os.walk(_p) for _x in _fl]
        elif _f.lower().endswith((".zip", ".jar")):
            with zipfile.ZipFile(_p) as _mz:
                _man = json.loads(_mz.read("manifest.json").decode("utf-8-sig"))
                _nm = _mz.namelist()
        else:
            continue
    except Exception:
        continue
    if not isinstance(_man, dict):
        continue
    _key = "%s:%s" % (_man.get("Group"), _man.get("Name"))
    _cl = _spell_clash(_nm, armory=(_man.get("Group") == "Skyy" and str(_man.get("Name", "")).endswith(" SkyyArmory")))   # 0.4.15: it owns the 8
    if _key in _packs:
        _pk_found.append(_key)
        if _cl:
            spell_fail("pack mod %s (%s) also ships %s" % (_key, _f, _cl[:5]))
        # its own items keep their full Mana cost (only vanilla items are divided) - say so if one has a Mana cost or inherits one
        for _n in _nm:
            if not (_n.startswith("Server/Item/Items/") and _n.endswith(".json")):
                continue
            try:
                if os.path.isdir(_p):
                    _raw = open(os.path.join(_p, *_n.split("/")), "rb").read()
                else:
                    with zipfile.ZipFile(_p) as _mz:
                        _raw = _mz.read(_n)
                _pj = json.loads(_raw.decode("utf-8-sig"))
            except Exception:
                continue
            if isinstance(_pj, dict) and (_spell_hits(_pj.get("InteractionVars") or {}, [], [])
                                          or (isinstance(_pj.get("Parent"), str) and _pj["Parent"] in _sk)):
                _pk_mana.append("%s %s" % (_key, os.path.basename(_n)[:-5]))
    elif _cl and not str(_man.get("Name", "")).endswith("SkyySkills"):   # every other mod, Skyy-named or not (not our own deployed jar)
        _other.append("%s (%d)" % (_f, len(_cl)))
print("spell costs /%d: %d item overrides generated from Assets.zip (%d with only 0 costs left alone: %s; Parent: %d item(s) inherit a cost%s); "
      "no clash with %d live-set jars or the pack mods %s" % (
          SPELL_DIVISOR, len(SPELL_PLAN), len(SPELL_UNCHANGED), ", ".join(SPELL_UNCHANGED) or "none", len(SPELL_INHERITS),
          (" " + ", ".join("%s <- %s" % kv for kv in sorted(SPELL_INHERITS.items()))) if SPELL_INHERITS else "", len(_checked),
          ", ".join(sorted(_pk_found)) or "(none installed)"))
for _t in SPELL_TABLE:
    print("  %-34s cast check %3d -> %2d   drain %3d -> %2d" % _t)
print("  (0.4.9: an item's cast check var above is dead data - the engine checks the charged cast step's own interaction, below)")
print("cast checks /%d (0.4.9): %d interaction overrides generated from Assets.zip (test assets left alone: %s; interactions inheriting "
      "one by Parent: %s)" % (SPELL_DIVISOR, len(SPELL_INT_PLAN), ", ".join(SPELL_TESTS) or "none",
                              ", ".join("%s <- %s" % kv for kv in SPELL_HEIRS) or "none"))
for _sid, _p, _k, _o, _n, _nj in SPELL_INT_PLAN:
    if _k == "drain":
        print("  %-30s default drain %4d -> %3d" % (_sid, _o, _n))
    else:
        _f = SPELL_FAMS[_sid]
        print("  %-30s cast check    %4s -> %3d  (%s; %d item(s) spend %d%s)" % (
            _sid, "none" if _o is None else _o, _n, "Simple -> StatsCondition" if _k == "check+" else "StatsCondition", len(_f[1]), _f[0],
            ("; spend 0 and now need %d Mana present: %s" % (_n, ", ".join(_f[2]))) if _f[2] else ""))
print("gate simulation (the engine's rules, every item, vanilla vs this jar): %d items cast with Mana - each checks what it spends "
      "(vanilla spend / %d); %d spend 0 behind a check (%s); no Mana spend without a check; none of the %d assets outside Server/Item "
      "(NPC roles, entities, drops ...) names an overridden interaction or its Charging step (%s)" % (
          len(SPELL_GATES), SPELL_DIVISOR, len(SPELL_FREE), ", ".join(SPELL_FREE) or "none", _s_nscan, ", ".join(_s_lead)))
_fam_rows = {}
for _g in SPELL_GATES:
    _fam_rows.setdefault(_g[1:], []).append(_g[0])
for _key in sorted(_fam_rows, key=lambda k: (k[0], k[3])):
    print("  %-28s check %4s -> %2d   spend %3d -> %2d : %d item(s) %s" % (
        _key[0], "none" if _key[1] == 0 else _key[1], _key[2], _key[3], _key[4], len(_fam_rows[_key]),
        ", ".join(_fam_rows[_key]) if len(_fam_rows[_key]) <= 3 else ", ".join(_fam_rows[_key][:2]) + ", ..."))
if _other:
    print("spell costs: NOTE mods in the Mods folder that are NOT in the live set also replace some of these items (only a problem if "
          "they are ever enabled): %s" % ", ".join(_other))
if _pk_mana:
    print("spell costs: NOTE pack mod items with their own Mana cost (or a Parent overridden here) are NOT divided: %s" % ", ".join(_pk_mana))
    print("spell costs: NOTE if such an item casts through one of the overridden cast checks above, it is now checked at that number")
print("staff handover (0.4.15): %d ladder staffs left to SkyyArmory (%s) - %d item overrides remain; a vanilla ladder staff behind this "
      "jar's interactions would check %d and spend %d Mana (the kit lookup's fallback, used only while SkyyArmory does not answer)" % (
          len(ARMORY_OWNED), ", ".join(_a[13:] for _a in ARMORY_OWNED), len(SPELL_PLAN), ARMORY_GATES[0][1], ARMORY_GATES[0][2]))
# the modifier keys (spec 4.12): our own prefix, distinct, never SkyyAccessories' skyyacc_* or the coming SkyyGear's skyygear*
OVL_KEYS = ["skyyskill_basemana", "skyyskill_overallhp", "skyyskill_overallmana", "skyyskill_classmana"]   # 0.4.15: + max Mana per class level
assert len(set(OVL_KEYS)) == 4 and all(k.startswith("skyyskill_") for k in OVL_KEYS)
assert not set(OVL_KEYS) & {"skyyskill_health", "skyyskill_stamina", "skyyskill_mana"}
assert not any(k.startswith("skyyacc_") or k.startswith("skyygear") for k in OVL_KEYS)
ALCH_PUTS = "\n".join('  m.put("%s", Long.valueOf(%dL));' % (i, x) for i, x in ALCH_XP)
SMITH_PUTS = "\n".join('  m.put("%s", Long.valueOf(%dL));' % (i, x) for i, x in SMITH_XP)
DEFAULTS = "\n".join(L) + "\n"
assert all(ord(ch) < 128 for ch in DEFAULTS)
DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\n \" \\ escapes)

PKG = "com.skyy.skills"
defs = pool.makeClass(PKG + ".SkillDefs")
cfg  = pool.makeClass(PKG + ".SkillCfg")
sto  = pool.makeClass(PKG + ".SkillStore")
fn   = pool.makeClass(PKG + ".SkillFn")
msg  = pool.makeClass(PKG + ".SkillMsg")
fl   = pool.makeClass(PKG + ".FlushTask")
pub  = pool.makeClass(PKG + ".PublishTask")
xp   = pool.makeClass(PKG + ".SkillXp")
plc  = pool.makeClass(PKG + ".PlacedStore")
hg   = pool.makeClass(PKG + ".HarvestGate")
btk  = pool.makeClass(PKG + ".BreakTask")
ptk  = pool.makeClass(PKG + ".PlaceTask")
htk  = pool.makeClass(PKG + ".HarvestTask")
bsy  = pool.makeClass(PKG + ".BreakSys", pool.get(EES))
psy  = pool.makeClass(PKG + ".PlaceSys", pool.get(EES))
usy  = pool.makeClass(PKG + ".HarvestSys", pool.get(EES))
ksy  = pool.makeClass(PKG + ".KillSys", pool.get(ODS))
tcm  = pool.makeClass(PKG + ".TopCmp")
top  = pool.makeClass(PKG + ".SkillTop")
page = pool.makeClass(PKG + ".SkillsPage", pool.get(PAGE))
tcmd = pool.makeClass(PKG + ".TopCmd", pool.get(APC))
qcmd = pool.makeClass(PKG + ".QuietCmd", pool.get(APC))
rcmd = pool.makeClass(PKG + ".ReloadCmd", pool.get(APC))
cmd  = pool.makeClass(PKG + ".SkillsCmd", pool.get(APC))
tick = pool.makeClass(PKG + ".SkillTick")
pl   = pool.makeClass(PKG + ".SkyySkillsPlugin", pool.get(JP))
acfg = pool.makeClass(PKG + ".AcroCfg")
mvs_ = pool.makeClass(PKG + ".MoveSync")
acro = pool.makeClass(PKG + ".Acro")
asy  = pool.makeClass(PKG + ".AcroSys", pool.get(ETS))
afs  = pool.makeClass(PKG + ".AcroFallSys", pool.get(DEVS))
pcfg = pool.makeClass(PKG + ".PerkCfg")
scls = pool.makeClass(PKG + ".SkillClass")
perk = pool.makeClass(PKG + ".Perks")
cds  = pool.makeClass(PKG + ".CombatDmgSys", pool.get(DEVS))
spg  = pool.makeClass(PKG + ".StatsPage", pool.get(PAGE))
scmd = pool.makeClass(PKG + ".StatsCmd", pool.get(APC))
# 0.4
alc  = pool.makeClass(PKG + ".AlchCfg")
smc  = pool.makeClass(PKG + ".SmithCfg")
bgc  = pool.makeClass(PKG + ".BridgeCfg")
rxp  = pool.makeClass(PKG + ".RecipeXp")
brew = pool.makeClass(PKG + ".Brew")
bxp  = pool.makeClass(PKG + ".BridgeXp")
ctk  = pool.makeClass(PKG + ".CraftTask")
stk  = pool.makeClass(PKG + ".SmeltTask")
btsk = pool.makeClass(PKG + ".BridgeTask")
csy  = pool.makeClass(PKG + ".CraftSys", pool.get(EES))
sxu  = pool.makeClass(PKG + ".SmeltXp")
ssy  = pool.makeClass(PKG + ".SmeltSys", pool.get(EES))
afss = pool.makeClass(PKG + ".AcroFallSeenSys", pool.get(DEVS))
afn  = pool.makeClass(PKG + ".SkillAddFn")
cfn  = pool.makeClass(PKG + ".SkillCraftFn")
xcmd = pool.makeClass(PKG + ".XpCmd", pool.get(APC))
# 0.4 trees bridge
sbn  = pool.makeClass(PKG + ".SkillBonus")
xfn  = pool.makeClass(PKG + ".SkillXpFn")
dfn  = pool.makeClass(PKG + ".SkillDropsFn")
pfn  = pool.makeClass(PKG + ".SkillPlacedFn")
# 0.4.1
exc  = pool.makeClass(PKG + ".ExplCfg")
# 0.4.2 felled trees (research/Tree-Fall-Spec.md 3.1)
fcf  = pool.makeClass(PKG + ".FellCfg")
fdf  = pool.makeClass(PKG + ".FellDefs")
frd  = pool.makeClass(PKG + ".FellRead")
fsn  = pool.makeClass(PKG + ".FellSnap")
fwt  = pool.makeClass(PKG + ".FellWatch")
fel  = pool.makeClass(PKG + ".Fell")
fdr  = pool.makeClass(PKG + ".FellDrops")
fcr  = pool.makeClass(PKG + ".FellCredit")
ffn  = pool.makeClass(PKG + ".FelledByFn")
esy  = pool.makeClass(PKG + ".EnvSys", pool.get(WES))
# 0.4.2 stage 2: party combat XP (beta backlog 6)
pcg  = pool.makeClass(PKG + ".PartyCfg")
pxp  = pool.makeClass(PKG + ".PartyXp")
pft  = pool.makeClass(PKG + ".PartyFlushTask")
# 0.4.3: admin config hooks (reload routine, check= hooks, the custom: curve rows) - compiled after CFG.emit (they call CfgFn)
skit = pool.makeClass(PKG + ".SkillKit")
karm = pool.makeClass(PKG + ".SkillKitArm")
# 0.4.4: Divinity XP from Priest heals (research/Classes-Berserker-Priest-Spec.md 3.4): config, cap ring + offer, bridge Function
dvc  = pool.makeClass(PKG + ".DivCfg")
hxp  = pool.makeClass(PKG + ".HealXp")
hfn  = pool.makeClass(PKG + ".SkillHealFn")
# 0.4.5: crossbows stay loaded (research/Crossbow-Loaded-Spec.md 3.2-3.5): config, per-player state, logic, the hotbar switch event system
xcf  = pool.makeClass(PKG + ".XbowCfg")
xst  = pool.makeClass(PKG + ".XbowState")
xbw  = pool.makeClass(PKG + ".Xbow")
xss  = pool.makeClass(PKG + ".XbowSlotSys", pool.get(EES))
# 0.4.6: base Mana + Overall Level (research/Overall-Level-Spec.md 4.3-4.8): config, logic, bridge Function, the Overall page
ovc  = pool.makeClass(PKG + ".OverallCfg")
ovl  = pool.makeClass(PKG + ".Overall")
ofn  = pool.makeClass(PKG + ".OverallFn")
opg  = pool.makeClass(PKG + ".OverallPage", pool.get(PAGE))
# 0.4.12: the class skill curve notice (ClassCurve), Mana regen in combat + the Mana Regen % registry (ManaRegen, its bridge Function
# ManaRegenFn) and the admin /skills mana sub-command (ManaCmd)
ccv  = pool.makeClass(PKG + ".ClassCurve")
mrg  = pool.makeClass(PKG + ".ManaRegen")
mrfn = pool.makeClass(PKG + ".ManaRegenFn")
mcmd = pool.makeClass(PKG + ".ManaCmd", pool.get(APC))
# 0.4.13: the combat state for other mods (skill:fn:combat - SkyyHud's Combat widget); "cfn" is SkillCraftFn
cmbf = pool.makeClass(PKG + ".CombatFn")
# 0.4.14: kill XP by mob level (MobXp), roll landings (RollSys, before the engine's FallDamagePlayers), the gathering pace (GatherPace),
# sickle swings (Sickle + SickleSys on InteractivelyPickupItemEvent + SickleTask on the world thread), the Mana comment fix (DocMig)
mxp  = pool.makeClass(PKG + ".MobXp")
rsy  = pool.makeClass(PKG + ".RollSys", pool.get(ETS))
gpc  = pool.makeClass(PKG + ".GatherPace")
skl  = pool.makeClass(PKG + ".Sickle")
sksy = pool.makeClass(PKG + ".SickleSys", pool.get(EES))
sktk = pool.makeClass(PKG + ".SickleTask")
dmig = pool.makeClass(PKG + ".DocMig")
# 0.4.15: max Mana per class level (ClassMana: the mana.classPerLevel table + the per-player amount / texts) and its one-time default lines in an
# existing xp.properties (ClassManaMig)
cman = pool.makeClass(PKG + ".ClassMana")
cmig = pool.makeClass(PKG + ".ClassManaMig")
mrg.addField(CtField.make("public static volatile int IN_COMBAT = " + MREG_DEF + ";", mrg))   # mana.regen.inCombat (0-100 %)
mrg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CLK = new java.util.concurrent.ConcurrentHashMap();", mrg))   # UUID -> float[]{s}
mrg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SRC = new java.util.concurrent.ConcurrentHashMap();", mrg))   # UUID -> CHM source -> Double %
mrg.addField(CtField.make("public static boolean FAILED_ONCE = false;", mrg))
mrg.addField(CtField.make("public static final double MAX_PCT = 1000.0;", mrg))
mrg.addField(CtField.make("public static final float PULSE = 0.2f;", mrg))   # = vanilla Mana.json's 0.2 s regen interval
# 0.4.13 (skill:fn:combat): CMB = UUID -> long[]{ms left at the last pulse, wall ms of that pulse} (players IN combat only); NDLY =
# NoDamageTakenCondition -> Long its Delay in ns (asked from the condition, once per condition object); WINDOW = the Delay in ms
mrg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CMB = new java.util.concurrent.ConcurrentHashMap();", mrg))
mrg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap NDLY = new java.util.concurrent.ConcurrentHashMap();", mrg))
mrg.addField(CtField.make("public static volatile long WINDOW = 0L;", mrg))   # vanilla 6000; 0 = nobody in combat since the start
mrg.addField(CtField.make("public static boolean CFAILED_ONCE = false;", mrg))
mrg.addField(CtField.make("public static final long STALE_MS = 1000L;", mrg))   # a pulse older than this no longer holds the countdown at >= 1
mrg.addField(CtField.make("public static final long NDLY_CAP = 3600000000000L;", mrg))   # the Delay search stops at 1 hour (ns)
# 0.4.13 fix F1: CARRY = UUID -> Object[]{world name, that world's clock (Instant), Long System.nanoTime() of the pulse, Float its time
# dilation, the stamps after the pulse: lastDamageTime, lastCombatAction, lastChargeTime} (pruned to online players by Acro.retainOnline)
mrg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CARRY = new java.util.concurrent.ConcurrentHashMap();", mrg))
mrg.addField(CtField.make("public static boolean KFAILED_ONCE = false;", mrg))
mrg.addField(CtField.make("public static final long CARRY_CAP = 3600000000000L;", mrg))   # over 1 hour (ns, real) since a stamp = Instant.MIN
mrg.addField(CtField.make("public static final long CARRY_SLACK = 1000000000L;", mrg))   # 1 s of slack on the late-hit / fresh-hit windows (ns)

# ================= SkillDefs: names, icons, level table =================
# 0.3 storage slots: 0-4 as in 0.2 (slot 3 "Combat" = legacy classless XP, no longer earned), 5-9 = one combat skill per class
# (SkyyClasses roster, HANDOFF "Skills + classes design"). NAMES = keys in players/<uuid>.properties, LABELS = what players see,
# N = storage slots (data array long[2*N], paid markers at N+slot), ROWS = rows on /skills (row 3 shows the current class slot).
# 0.4.4 (research/Classes-Berserker-Priest-Spec.md 3.1): Berserker / Fury and Priest / Divinity are APPENDED after Exploration = storage
# slots 14 and 15 (saved keys Combat.Berserker / Combat.Priest). The Shaman placeholder icon is the Slowness Totem (the wand is Priest's).
CLASS_ROWS = [("Archer", "Archery", "Weapon_Shortbow_Iron", "#8fd67a"), ("Warrior", "Swordsmanship", "Weapon_Sword_Iron", "#e0b060"),
              ("Assassin", "Assassination", "Weapon_Daggers_Iron", "#b58cff"),
              ("Shaman", "Shaman skill", "Weapon_Deployable_Slowness_Totem", "#ff7a5c"),
              ("Mage", "Sorcery", "Weapon_Staff_Iron", "#7fb0e0"),
              ("Berserker", "Fury", "Weapon_Battleaxe_Iron", "#d9443f"), ("Priest", "Divinity", "Weapon_Wand_Wood", "#f2e6a0")]
for _c in CLASS_ROWS: must(_c[2])
# 0.4.4 (spec 3.2): the storage slot of each CLASS_ROWS entry (same order = SkillDefs.CLASSES). Class slots are NOT contiguous any more
# (5-9, then 14-15 after the four extra rows): every class loop / index goes through SkillDefs.CLASS_SLOT / isClass / classIdx /
# classSlot - the SkillDefs fields CLASS0 / CLASS_END are gone, so no code can do slot arithmetic with them.
CLASS_SLOT = [5, 6, 7, 8, 9, 14, 15]
assert len(CLASS_SLOT) == len(CLASS_ROWS) and len(set(CLASS_SLOT)) == len(CLASS_SLOT)
# the class roster SkyyClasses 0.1.6 publishes (spec 2.1; display order there is different, names must match)
_ROSTER = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Shaman"]
assert sorted(c[0] for c in CLASS_ROWS) == sorted(_ROSTER), "CLASS_ROWS names != the SkyyClasses 0.1.6 roster"
def _classes_roster():
    """names in the newest SkyyClasses build script's CLASSES list (read only), or (version, None) when it cannot be parsed
    (for a 0.1.6+ script that fails the build below)"""
    import glob, re as _re
    best, path = None, None
    for f in glob.glob(os.path.join(HERE, "..", "SkyyClasses", "build_skyyclasses_*.py")):
        m = _re.search(r"build_skyyclasses_(\d+(?:\.\d+)*)\.py$", f.replace("\\", "/"))
        if m:
            v = tuple(int(x) for x in m.group(1).split("."))
            if best is None or v > best: best, path = v, f
    if path is None: return None, None
    t = open(path, encoding="utf8").read()
    m = _re.search(r"^CLASSES = \[(.*?)^\]", t, _re.M | _re.S)
    if not m: return best, None
    names = _re.findall(r'"name":\s*"([A-Za-z]+)"', m.group(1))
    return best, (names or None)
_cv, _cn = _classes_roster()
if _cv is not None and _cv >= (0, 1, 6):
    # a 0.1.6+ script whose CLASSES list cannot be parsed must FAIL the build (never look like "nothing to compare yet")
    if _cn is None:
        raise SystemExit("could not parse the SkyyClasses %s roster (CLASSES = [ ... ] with 'name' entries) - update _classes_roster()"
                         % ".".join(map(str, _cv)))
    assert sorted(_cn) == sorted(c[0] for c in CLASS_ROWS), "SkyyClasses %s roster %s != SkyySkills CLASS_ROWS" % (".".join(map(str, _cv)), _cn)
    print("class roster = SkyyClasses %s: %s" % (".".join(map(str, _cv)), ", ".join(_cn)))
else:
    print("class roster checked against the spec (newest SkyyClasses build script %s is older than 0.1.6 - nothing to compare yet)" % (".".join(map(str, _cv)) if _cv else "none"))
# 0.4: slots 10-12, 0.4.1: slot 13 Exploration = slots 10-13 (append-only; NOT classes)
EXTRA_ROWS = [("Alchemy", "Alchemy", "Potion_Health", "#7fe0d0"), ("Smithing", "Smithing", "Ingredient_Bar_Iron", "#c0c8d0"),
              ("Cooking", "Cooking", "Food_Pie_Apple", "#ffb070"), ("Exploration", "Exploration", "Tool_Map", "#e0a040")]
for _c in EXTRA_ROWS: must(_c[2])
_SL = [None] * (5 + len(CLASS_ROWS) + len(EXTRA_ROWS))
_B5 = ["Mining", "Foraging", "Farming", "Combat", "Acrobatics"]
_B5C = ["#8fc8ff", "#8fe08a", "#f0d060", "#ff8a7a", "#c8a0ff"]
for _i in range(5):
    _SL[_i] = (_B5[_i], _B5[_i], ICONS[_i], _B5C[_i])
for _i, _c in enumerate(CLASS_ROWS):
    assert _SL[CLASS_SLOT[_i]] is None, "slot %d used twice" % CLASS_SLOT[_i]
    _SL[CLASS_SLOT[_i]] = ("Combat." + _c[0], _c[1], _c[2], _c[3])
_FREE = [_i for _i, _x in enumerate(_SL) if _x is None]
assert _FREE == [10, 11, 12, 13], _FREE
for _j, _c in zip(_FREE, EXTRA_ROWS):
    _SL[_j] = (_c[0], _c[1], _c[2], _c[3])
SLOT_NAMES = [_x[0] for _x in _SL]
SLOT_LABELS = [_x[1] for _x in _SL]
SLOT_ICONS = [_x[2] for _x in _SL]
SLOT_COLORS = [_x[3] for _x in _SL]
assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 16
# append-only: every 0.4.3 slot keeps its index and saved key (player files store slots by NAMES; snap() writes only NAMES)
assert SLOT_NAMES[:14] == ["Mining", "Foraging", "Farming", "Combat", "Acrobatics", "Combat.Archer", "Combat.Warrior", "Combat.Assassin",
                           "Combat.Shaman", "Combat.Mage", "Alchemy", "Smithing", "Cooking", "Exploration"], SLOT_NAMES
assert SLOT_NAMES[10:14] == ["Alchemy", "Smithing", "Cooking", "Exploration"] and SLOT_NAMES[14:] == ["Combat.Berserker", "Combat.Priest"]
assert SLOT_LABELS[14:] == ["Fury", "Divinity"] and SLOT_LABELS[8] == "Shaman skill"
assert len(set(l.lower() for l in SLOT_LABELS)) == len(SLOT_LABELS) and len(set(n.lower() for n in SLOT_NAMES)) == len(SLOT_NAMES)
FURY_SLOT = CLASS_SLOT[[c[0] for c in CLASS_ROWS].index("Berserker")]
DIVINITY_SLOT = CLASS_SLOT[[c[0] for c in CLASS_ROWS].index("Priest")]
assert (FURY_SLOT, DIVINITY_SLOT) == (14, 15)
# 0.4.7: the /skills row order, the Acrobatics slot and the class-row slot as ONE set of Python values - formatted into
# SkillDefs.ROW_SLOTS / ACROBATICS below (the same Java text as 0.4.6) AND read by the SKILLS PAGES LOOK block (the /skills list-well
# height budget SK_ROW_SLOTS / SK_LIST_H: one 62 px row per slot, the Acrobatics row 82 px), so the rows and the budget cannot drift
SKILL_ROW_SLOTS = [0, 1, 2, 10, 11, 12, 4, 13, 3]
ACRO_SLOT, COMBAT_SLOT = 4, 3
assert SLOT_NAMES[ACRO_SLOT] == "Acrobatics" and SLOT_NAMES[COMBAT_SLOT] == "Combat", (ACRO_SLOT, COMBAT_SLOT)
assert SKILL_ROW_SLOTS.count(ACRO_SLOT) == 1 and SKILL_ROW_SLOTS.count(COMBAT_SLOT) == 1 and len(set(SKILL_ROW_SLOTS)) == len(SKILL_ROW_SLOTS)
def jarr(xs): return "new String[] { " + ", ".join('"%s"' % x for x in xs) + " }"
defs.addField(CtField.make("public static final String[] NAMES = %s;" % jarr(SLOT_NAMES), defs))
defs.addField(CtField.make("public static final String[] LABELS = %s;" % jarr(SLOT_LABELS), defs))
defs.addField(CtField.make("public static final String[] ICONS = %s;" % jarr(SLOT_ICONS), defs))
defs.addField(CtField.make("public static final String[] COLORS = %s;" % jarr(SLOT_COLORS), defs))
defs.addField(CtField.make("public static final String[] CLASSES = %s;" % jarr([c[0] for c in CLASS_ROWS]), defs))
defs.addField(CtField.make("public static final int N = %d;" % len(SLOT_NAMES), defs))
defs.addField(CtField.make("public static final int ROWS = 5;", defs))
defs.addField(CtField.make("public static final int[] CLASS_SLOT = new int[] { %s };" % ", ".join(str(x) for x in CLASS_SLOT), defs))   # 0.4.4
defs.addField(CtField.make("public static final int MINING = 0;", defs))
defs.addField(CtField.make("public static final int FORAGING = 1;", defs))
defs.addField(CtField.make("public static final int FARMING = 2;", defs))
defs.addField(CtField.make("public static final int COMBAT = 3;", defs))
defs.addField(CtField.make("public static final int ACROBATICS = %d;" % ACRO_SLOT, defs))
defs.addField(CtField.make("public static final int ALCHEMY = 10;", defs))
defs.addField(CtField.make("public static final int SMITHING = 11;", defs))
defs.addField(CtField.make("public static final int COOKING = 12;", defs))
defs.addField(CtField.make("public static final int EXPLORATION = 13;", defs))   # 0.4.1
defs.addField(CtField.make("public static final int FURY = %d;" % FURY_SLOT, defs))           # 0.4.4 Berserker
defs.addField(CtField.make("public static final int DIVINITY = %d;" % DIVINITY_SLOT, defs))   # 0.4.4 Priest
# /skills rows (3 = the class row: the current class's weapon skill, or the "choose a class" row) - 0.4.7: from SKILL_ROW_SLOTS
defs.addField(CtField.make("public static final int[] ROW_SLOTS = new int[] { %s };" % ", ".join(str(x) for x in SKILL_ROW_SLOTS), defs))   # 0.4.1: Exploration after Acrobatics
# perk row -> storage slot (row 3 = the current class, see Perks.rowLevel); PerkCfg.KEYS has the same order
defs.addField(CtField.make("public static final int[] PERK_SLOT = new int[] { 0, 1, 2, 3, 4, 10, 11, 12, 13 };", defs))
# 0.4.4 (spec 3.2): class slots come from the table (5-9, 14, 15) - methods before their callers (perkRow, indexOf)
defs.addMethod(CtNewMethod.make("""
public static boolean isClass(int s) {
  for (int i = 0; i < CLASS_SLOT.length; i++) if (CLASS_SLOT[i] == s) return true;
  return false;
}""", defs))
# storage slot -> index into CLASSES, -1 = not a class slot
defs.addMethod(CtNewMethod.make("""
public static int classIdx(int s) {
  for (int i = 0; i < CLASS_SLOT.length; i++) if (CLASS_SLOT[i] == s) return i;
  return -1;
}""", defs))
# index into CLASSES -> storage slot, -1 = out of range
defs.addMethod(CtNewMethod.make("""
public static int classSlot(int i) {
  return i >= 0 && i < CLASS_SLOT.length ? CLASS_SLOT[i] : -1;
}""", defs))
# storage slot -> perk row (class slots and the legacy Combat slot -> the combat row 3), -1 = none
defs.addMethod(CtNewMethod.make("""
public static int perkRow(int s) {
  if (s >= 0 && s <= 2) return s;
  if (s == COMBAT || isClass(s)) return COMBAT;
  if (s == ACROBATICS) return ACROBATICS;
  if (s == ALCHEMY) return 5;
  if (s == SMITHING) return 6;
  if (s == COOKING) return 7;
  if (s == EXPLORATION) return 8;
  return -1;
}""", defs))
# 0.4.1 (Skyy Q3: no XP boosters for Exploration): false = the xp multiplier and every skill-tree / booster bonus are skipped for this
# slot, in code (BridgeXp.offer, SkillBonus.xpBonus), whatever xp.properties says
defs.addMethod(CtNewMethod.make("""
public static boolean boostable(int s) {
  return s != EXPLORATION;
}""", defs))
defs.addField(CtField.make("public static final long[] DEFAULT_PER = new long[] { %s };" % ", ".join("%dL" % x for x in LEVELS), defs))
defs.addField(CtField.make("public static volatile long[] PER = DEFAULT_PER;", defs))
defs.addField(CtField.make("public static volatile long[] CUM = new long[] { 0L };", defs))
defs.addField(CtField.make("public static volatile int MAX = 100;", defs))
# 0.4.12 (Skyy 2026-10-02 Q&A round 1, research/cloud/Class-Skill-Curve-Proposal.md): the CLASS skill table (levels.class) - CPER / CCUM /
# CMAX like PER / CUM / MAX - and levels.class.sameAsOthers (SAME). ECUM = the EFFECTIVE class table every class slot levels on:
# ECUM[L] = min(CCUM[L], CUM[L]) for L up to CMAX (a class level never needs more total XP than the general table asks for the same
# level = level max(general, class): levels only go up; capped by the class max), or CUM itself while SAME. recalc() rebuilds it whenever
# either table changes (setTable / setClassTable, both under the SkillDefs lock).
defs.addField(CtField.make("public static final long[] DEFAULT_CPER = new long[] { %s };" % ", ".join("%dL" % x for x in CLASS_LEVELS), defs))
defs.addField(CtField.make("public static volatile long[] CPER = DEFAULT_CPER;", defs))
defs.addField(CtField.make("public static volatile long[] CCUM = new long[] { 0L };", defs))
defs.addField(CtField.make("public static volatile int CMAX = 100;", defs))
defs.addField(CtField.make("public static volatile boolean SAME = false;", defs))
defs.addField(CtField.make("public static volatile long[] ECUM = new long[] { 0L };", defs))
defs.addMethod(CtNewMethod.make("""
public static synchronized void recalc() {
  long[] g = CUM;
  if (SAME) { ECUM = g; return; }
  long[] c = CCUM;
  long[] e = new long[c.length];
  for (int i = 0; i < c.length; i++) {
    long x = c[i];
    if (i < g.length && g[i] < x) x = g[i];
    e[i] = x;
  }
  ECUM = e;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static synchronized void setTable(long[] per) {
  if (per == null || per.length == 0) return;
  long[] cum = new long[per.length + 1];
  cum[0] = 0L;
  for (int i = 0; i < per.length; i++) cum[i + 1] = cum[i] + per[i];
  PER = per; CUM = cum; MAX = per.length;
  recalc();
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static synchronized void setClassTable(long[] per, boolean same) {
  if (per == null || per.length == 0) return;
  long[] cum = new long[per.length + 1];
  cum[0] = 0L;
  for (int i = 0; i < per.length; i++) cum[i + 1] = cum[i] + per[i];
  CPER = per; CCUM = cum; CMAX = per.length; SAME = same;
  recalc();
}""", defs))
# 0.4.12: THE per-slot lookup - the cumulative table a storage slot levels on (class slots: ECUM, every other slot: the general CUM)
defs.addMethod(CtNewMethod.make("""
public static long[] cumOf(int s) {
  return isClass(s) ? ECUM : CUM;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int maxOf(int s) {
  return cumOf(s).length - 1;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int levelIn(long[] cum, long total) {
  int max = cum.length - 1;
  int l = 0;
  while (l < max && total >= cum[l + 1]) l++;
  return l;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int levelOf(int s, long total) {
  return levelIn(cumOf(s), total);
}""", defs))
# the level on the GENERAL table (= what 0.4.11 showed for any slot) - ClassCurve's "was" level
defs.addMethod(CtNewMethod.make("""
public static int generalLevel(long total) {
  return levelIn(CUM, total);
}""", defs))
# XP into the current level of slot s
defs.addMethod(CtNewMethod.make("""
public static long intoLevel(int s, long total) {
  long[] c = cumOf(s);
  return total - c[levelIn(c, total)];
}""", defs))
# XP the current level of slot s needs in total (0 at its max level)
defs.addMethod(CtNewMethod.make("""
public static long needFor(int s, long total) {
  long[] c = cumOf(s);
  int l = levelIn(c, total);
  return l + 1 < c.length ? c[l + 1] - c[l] : 0L;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int indexOf(String s) {
  if (s == null) return -1;
  String t = s.trim().toLowerCase();
  if (t.length() == 0) return -1;
  for (int i = 0; i < LABELS.length; i++) if (LABELS[i].toLowerCase().equals(t) || NAMES[i].toLowerCase().equals(t)) return i;
  for (int i = 0; i < CLASSES.length; i++) if (CLASSES[i].toLowerCase().equals(t)) return classSlot(i);
  if (t.length() >= 3) {
    for (int i = 0; i < LABELS.length; i++) if (LABELS[i].toLowerCase().startsWith(t)) return i;
    for (int i = 0; i < CLASSES.length; i++) if (CLASSES[i].toLowerCase().startsWith(t)) return classSlot(i);
  }
  return -1;
}""", defs))
# compact number: 950, 12.3k, 1.25m, 3.10b (no commas: UI text is sanitized)
defs.addMethod(CtNewMethod.make("""
public static String fmt(long n) {
  if (n < 0L) return "-" + fmt(n == Long.MIN_VALUE ? Long.MAX_VALUE : -n);
  if (n < 10000L) return String.valueOf(n);
  if (n < 1000000L) { long t = n / 100L; return (t / 10L) + "." + (t % 10L) + "k"; }
  if (n < 1000000000L) { long h = n / 10000L; return (h / 100L) + "." + ((h % 100L) < 10L ? "0" : "") + (h % 100L) + "m"; }
  long g = n / 10000000L;
  return (g / 100L) + "." + ((g % 100L) < 10L ? "0" : "") + (g % 100L) + "b";
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static String progress(int s, long total) {
  long need = needFor(s, total);
  if (need <= 0L) return "MAX";
  return fmt(intoLevel(s, total)) + "/" + fmt(need);
}""", defs))

# ================= SkillCfg: xp.properties =================
cfg.addField(CtField.make("public static java.nio.file.Path FILE;", cfg))
cfg.addField(CtField.make(f"public static {LOG} LOG;", cfg))
cfg.addField(CtField.make("public static final String DEFAULTS = " + DEFAULTS_LIT + ";", cfg))
cfg.addField(CtField.make("public static volatile double MULT = 1.0;", cfg))
# 0.4.10: classSkill.xpMultiplier (the loader clamps it to the row bounds 0-100) and the block ensureClass appends to an old file
cfg.addField(CtField.make("public static volatile double CLASS_MULT = " + CLS_MULT_DEF + ";", cfg))
cfg.addField(CtField.make("public static final String CLASS_DEFAULTS = " + CLS_LIT + ";", cfg))
# 0.4.12: the class skill levels block and the Mana regen in combat block (ensureCurve / ensureManaRegen append them once)
cfg.addField(CtField.make("public static final String CURVE_DEFAULTS = " + CURVE_LIT + ";", cfg))
cfg.addField(CtField.make("public static final String MREG_DEFAULTS = " + MREG_LIT + ";", cfg))
cfg.addField(CtField.make("public static volatile long COINS_PER_LEVEL = 100L;", cfg))
cfg.addField(CtField.make("public static volatile boolean FEEDBACK = true;", cfg))
cfg.addField(CtField.make("public static volatile long FEEDBACK_MS = 2000L;", cfg))
cfg.addField(CtField.make("public static volatile boolean CREATIVE = false;", cfg))
cfg.addField(CtField.make("public static volatile boolean IGNORE_PLACED = true;", cfg))
cfg.addField(CtField.make("public static volatile boolean NEED_RIPE = true;", cfg))
cfg.addField(CtField.make("public static volatile long HARVEST_GATE_MS = 5000L;", cfg))
cfg.addField(CtField.make("public static volatile double C_PER_HP = 0.2;", cfg))
cfg.addField(CtField.make("public static volatile long C_MIN = 1L;", cfg))
cfg.addField(CtField.make("public static volatile long C_MAX = 500L;", cfg))
cfg.addField(CtField.make("public static volatile long C_DEFAULT = 5L;", cfg))
cfg.addField(CtField.make("public static volatile java.util.HashMap EXACT = new java.util.HashMap();", cfg))
cfg.addField(CtField.make("public static volatile java.util.ArrayList PFX = new java.util.ArrayList();", cfg))
cfg.addField(CtField.make("public static volatile java.util.ArrayList SFX = new java.util.ArrayList();", cfg))
cfg.addField(CtField.make("public static volatile java.util.HashMap ROLE = new java.util.HashMap();", cfg))
cfg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();", cfg))
cfg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEEN_ROLES = new java.util.concurrent.ConcurrentHashMap();", cfg))
cfg.addField(CtField.make("public static final long[] NONE = new long[] { -1L, 0L };", cfg))
cfg.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyySkills] " + msg); } catch (Throwable t) { }
}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyySkills] " + msg); } catch (Throwable t) { }
}""", cfg))
# "Mining:5" -> {0, 5}; "none" / ":0" -> NONE; bad -> null
cfg.addMethod(CtNewMethod.make(f"""
public static long[] parseRule(String v) {{
  if (v == null) return null;
  String s = v.trim();
  if (s.equalsIgnoreCase("none") || s.length() == 0) return NONE;
  int c = s.indexOf(':');
  if (c <= 0) return null;
  int sk = {PKG}.SkillDefs.indexOf(s.substring(0, c));
  if (sk < 0 || sk > {PKG}.SkillDefs.FARMING) return null;
  try {{
    long x = Long.parseLong(s.substring(c + 1).trim());
    if (x <= 0L) return NONE;
    return new long[] {{ (long) sk, x }};
  }} catch (Throwable t) {{ return null; }}
}}""", cfg))
# 0.4.1: a block. / prefix. / suffix. rule naming Exploration ("Exploration:5") is ignored with a WARN - Exploration XP only comes from
# other mods through skill:fn:addxp (parseRule would call it a bad rule anyway; this names the reason and does not count it as bad)
cfg.addMethod(CtNewMethod.make(f"""
public static boolean explRule(String v) {{
  if (v == null) return false;
  String s = v.trim();
  int c = s.indexOf(':');
  if (c <= 0) return false;
  return {PKG}.SkillDefs.indexOf(s.substring(0, c)) == {PKG}.SkillDefs.EXPLORATION;
}}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static double dbl(java.util.Properties p, String k, double d) {
  try { String v = p.getProperty(k); return v == null ? d : Double.parseDouble(v.trim()); } catch (Throwable t) { return d; }
}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static long lng(java.util.Properties p, String k, long d) {
  try { String v = p.getProperty(k); return v == null ? d : Long.parseLong(v.trim()); } catch (Throwable t) { return d; }
}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static boolean bool(java.util.Properties p, String k, boolean d) {
  String v = p.getProperty(k);
  if (v == null) return d;
  v = v.trim();
  if (v.equalsIgnoreCase("true")) return true;
  if (v.equalsIgnoreCase("false")) return false;
  return d;
}""", cfg))
# ================= AcroCfg: acro.* keys of xp.properties (0.2) =================
acfg.addField(CtField.make("public static final String DEFAULTS = " + ACRO_LIT + ";", acfg))
for _decl in ("boolean ENABLED = true", "double SPRINT = 0.25", "double RUN = 0.15", "double WALK = 0.05", "double MAX_SPEED = 30.0",
              "double TELEPORT = 8.0", "double JUMP_XP = 2.0", "long JUMP_CD = 800L", "double JUMP_MOVE = 2.0", "double FALL_MIN = 4.0",
              "double FALL_DMG_XP = 10.0", "double FALL_MAX = 2000.0", "double FALL_PER_MIN = 3000.0", "double DODGE_XP = 3.0", "long DODGE_CD = 400L",
              "double MAX_PER_MIN = 240.0", "long FEEDBACK_MS = 30000L", "double SPEED_PER_LVL = 0.01", "double JUMP_PER_LVL = 0.015",
              "double FALL_PER_LVL = 0.005", "double FALL_RED_MAX = 0.8", "boolean DODGE_BOOST = true", "double DODGE_FORCE = 13.0",
              "double DODGE_PER_LVL = 0.004", "double DODGE_MAX = 0.5", "double TREE_DODGE_MAX = 0.25"):
    acfg.addField(CtField.make("public static volatile %s;" % _decl, acfg))
# 0.4.2 stage 2: acro.doubleJump.* (research/Double-Jump-Spec.md 3.2) - read by readDj from SkillCfg.load, so /skills reload re-reads them
for _decl in ("boolean DJ_ON = true", "int DJ_TRIGGER = 1", 'String DJ_KEY = "jump"', "int DJ_MAX_JUMPS = 1", "double DJ_MAX_FRAC = 1.0",
              "double DJ_MAX_BLOCKS = 3.5", "double DJ_FORWARD = 2.0", "double DJ_STAMINA = 2.0", "double DJ_REGEN_DELAY = 0.3",
              "long DJ_CD = 250L", "long DJ_MIN_AIR = 100L", "double DJ_MAX_FALL = 0.0", "double DJ_XP = 0.0", "boolean DJ_FX = true",
              "boolean DJ_DEBUG = false"):
    acfg.addField(CtField.make("public static volatile %s;" % _decl, acfg))
acfg.addField(CtField.make("public static final String DJ_DEFAULTS = " + DJ_LIT + ";", acfg))
acfg.addMethod(CtNewMethod.make("""
public static double nn(double v) {
  if (Double.isNaN(v) || v < 0.0) return 0.0;
  return v;
}""", acfg))
acfg.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ENABLED = {PKG}.SkillCfg.bool(p, "acro.enabled", true);
  SPRINT = nn({PKG}.SkillCfg.dbl(p, "acro.sprintXpPerBlock", 0.25));
  RUN = nn({PKG}.SkillCfg.dbl(p, "acro.runXpPerBlock", 0.15));
  WALK = nn({PKG}.SkillCfg.dbl(p, "acro.walkXpPerBlock", 0.05));
  MAX_SPEED = Math.max(5.0, {PKG}.SkillCfg.dbl(p, "acro.maxSpeed", 30.0));
  TELEPORT = Math.max(2.0, {PKG}.SkillCfg.dbl(p, "acro.teleportBlocks", 8.0));
  JUMP_XP = nn({PKG}.SkillCfg.dbl(p, "acro.jumpXp", 2.0));
  JUMP_CD = Math.max(200L, {PKG}.SkillCfg.lng(p, "acro.jumpCooldownMs", 800L));
  JUMP_MOVE = nn({PKG}.SkillCfg.dbl(p, "acro.jumpMinMove", 2.0));
  FALL_MIN = Math.max(1.0, {PKG}.SkillCfg.dbl(p, "acro.fallMinBlocks", 4.0));
  FALL_DMG_XP = nn({PKG}.SkillCfg.dbl(p, "acro.fallDamageXp", 10.0));
  FALL_MAX = nn({PKG}.SkillCfg.dbl(p, "acro.fallXpMax", 2000.0));
  FALL_PER_MIN = nn({PKG}.SkillCfg.dbl(p, "acro.fallMaxXpPerMinute", 3000.0));
  DODGE_XP = nn({PKG}.SkillCfg.dbl(p, "acro.dodgeXp", 3.0));
  DODGE_CD = Math.max(100L, {PKG}.SkillCfg.lng(p, "acro.dodgeCooldownMs", 400L));
  MAX_PER_MIN = nn({PKG}.SkillCfg.dbl(p, "acro.maxXpPerMinute", 240.0));
  FEEDBACK_MS = Math.max(2000L, {PKG}.SkillCfg.lng(p, "acro.feedbackMs", 30000L));
  SPEED_PER_LVL = nn({PKG}.SkillCfg.dbl(p, "acro.speedPerLevel", 0.01));
  JUMP_PER_LVL = nn({PKG}.SkillCfg.dbl(p, "acro.jumpBlocksPerLevel", 0.015));
  FALL_PER_LVL = nn({PKG}.SkillCfg.dbl(p, "acro.fallReductionPerLevel", 0.005));
  FALL_RED_MAX = Math.min(1.0, nn({PKG}.SkillCfg.dbl(p, "acro.fallReductionMax", 0.8)));
  DODGE_BOOST = {PKG}.SkillCfg.bool(p, "acro.dodgeBoost", true);
  DODGE_FORCE = nn({PKG}.SkillCfg.dbl(p, "acro.dodgeForce", 13.0));
  DODGE_PER_LVL = nn({PKG}.SkillCfg.dbl(p, "acro.dodgeBoostPerLevel", 0.004));
  DODGE_MAX = Math.min(2.0, nn({PKG}.SkillCfg.dbl(p, "acro.dodgeBoostMax", 0.5)));
  TREE_DODGE_MAX = Math.min(2.0, nn({PKG}.SkillCfg.dbl(p, "acro.treeDodgeMax", 0.25)));
}}""", acfg))
# 0.4.2 stage 2 (Double-Jump-Spec 3.2): trigger 0 crouch, 1 jump, 2 both.
# LOCKED 2026-09-25: missing or unknown = jump (a second jump in mid-air). An explicit crouch line is still honored.
# DJ_KEY = the words the SkyyTrees card (bridge skill:dj:key, Acro.djPublish) and the Stats page show.
acfg.addMethod(CtNewMethod.make("""
public static double clampD(double v, double lo, double hi) {
  if (Double.isNaN(v) || v < lo) return lo;
  if (v > hi) return hi;
  return v;
}""", acfg))
acfg.addMethod(CtNewMethod.make(f"""
public static void readDj(java.util.Properties p) {{
  DJ_ON = {PKG}.SkillCfg.bool(p, "acro.doubleJump.enabled", true);
  int tr = 1;
  String t = p.getProperty("acro.doubleJump.trigger");
  if (t != null) {{
    String x = t.trim().toLowerCase(java.util.Locale.ROOT);
    if (x.equals("crouch")) tr = 0;
    else if (x.equals("both")) tr = 2;
    else if (x.length() > 0 && !x.equals("jump")) {{ {PKG}.SkillCfg.warn("acro.doubleJump.trigger=" + t.trim() + " is not crouch, jump or both - using jump"); tr = 1; }}
  }}
  DJ_TRIGGER = tr;
  DJ_KEY = tr == 1 ? "jump" : (tr == 2 ? "jump or crouch" : "crouch");
  DJ_MAX_JUMPS = (int) clampD((double) {PKG}.SkillCfg.lng(p, "acro.doubleJump.maxJumps", 1L), 1.0, 5.0);
  DJ_MAX_FRAC = clampD({PKG}.SkillCfg.dbl(p, "acro.doubleJump.maxFraction", 1.0), 0.0, 1.5);
  DJ_MAX_BLOCKS = clampD({PKG}.SkillCfg.dbl(p, "acro.doubleJump.maxBlocks", 3.5), 0.5, 10.0);
  DJ_FORWARD = clampD({PKG}.SkillCfg.dbl(p, "acro.doubleJump.forwardPush", 2.0), 0.0, 10.0);
  DJ_STAMINA = clampD({PKG}.SkillCfg.dbl(p, "acro.doubleJump.stamina", 2.0), 0.0, 1000.0);
  DJ_REGEN_DELAY = clampD({PKG}.SkillCfg.dbl(p, "acro.doubleJump.staminaRegenDelay", 0.3), 0.0, 10.0);
  DJ_CD = (long) clampD((double) {PKG}.SkillCfg.lng(p, "acro.doubleJump.cooldownMs", 250L), 0.0, 60000.0);
  DJ_MIN_AIR = (long) clampD((double) {PKG}.SkillCfg.lng(p, "acro.doubleJump.minAirMs", 100L), 0.0, 5000.0);
  double mf = {PKG}.SkillCfg.dbl(p, "acro.doubleJump.maxFallSpeed", 0.0);
  DJ_MAX_FALL = Double.isNaN(mf) ? 0.0 : (mf > 1000.0 ? 1000.0 : mf);
  DJ_XP = clampD({PKG}.SkillCfg.dbl(p, "acro.doubleJump.xp", 0.0), 0.0, 1000.0);
  DJ_FX = {PKG}.SkillCfg.bool(p, "acro.doubleJump.fx", true);
  DJ_DEBUG = {PKG}.SkillCfg.bool(p, "acro.doubleJump.debug", false);
}}""", acfg))
acfg.addMethod(CtNewMethod.make(f"""
public static void ensureDj(java.util.Properties p) {{
  if (p.getProperty("acro.doubleJump.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DJ_DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Double Jump section (acro.doubleJump.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Double Jump section to xp.properties: " + t); }}
}}""", acfg))
acfg.addMethod(CtNewMethod.make("""
public static String djText() {
  if (!ENABLED) return "off (acro.enabled=false)";
  if (!DJ_ON) return "off (acro.doubleJump.enabled=false)";
  return "on (" + DJ_KEY + " in mid-air" + (DJ_DEBUG ? ", DEBUG chat lines on" : "") + ")";
}""", acfg))
# an xp.properties written by 0.1 has no acro.* key: append the documented section once (the code defaults apply either way)
acfg.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    if (String.valueOf(en.nextElement()).startsWith("acro.")) return;
  }}
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Acrobatics section (acro.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the acro.* section to xp.properties: " + t); }}
}}""", acfg))
# ================= PerkCfg: perk.* keys (+ combat.classWeaponOnly) of xp.properties (0.3) =================
pcfg.addField(CtField.make("public static final String DEFAULTS = " + PERK_LIT + ";", pcfg))
pcfg.addField(CtField.make('public static final String[] KEYS = new String[] { "mining", "foraging", "farming", "combat", "acrobatics", "alchemy", "smithing", "cooking", "exploration" };', pcfg))
for _decl in ("boolean ENABLED = true", "double DD_MAX = 1.0", "boolean DD_MSG = true", "double DMG = 0.002", "boolean DMG_PVP = false",
              "boolean WEAPON_ONLY = true", "double[] HP = new double[] { 0.0, 0.1, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0 }",
              "double[] STA = new double[] { 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1 }", "double[] MANA = new double[] { 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0 }",
              "double[] DD = new double[] { 0.005, 0.005, 0.005, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }", 'String[] ONLY = new String[] { "", "_Trunk", "", "", "", "", "", "", "" }'):
    pcfg.addField(CtField.make("public static volatile %s;" % _decl, pcfg))
# a rate is never negative (skills only ADD in the flat layer; gear will carry the trade-offs); bad / negative -> 0
pcfg.addMethod(CtNewMethod.make(f"""
public static double rate(java.util.Properties p, String k, double d) {{
  double v = {PKG}.SkillCfg.dbl(p, k, d);
  if (Double.isNaN(v) || Double.isInfinite(v) || v < 0.0) return 0.0;
  return v;
}}""", pcfg))
pcfg.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ENABLED = {PKG}.SkillCfg.bool(p, "perk.enabled", true);
  DD_MAX = Math.min(1.0, rate(p, "perk.doubleDropMax", 1.0));
  DD_MSG = {PKG}.SkillCfg.bool(p, "perk.doubleDropMessage", true);
  double[] dhp = new double[] {{ 0.0, 0.1, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0 }};
  double[] dsta = new double[] {{ 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1 }};
  double[] dmana = new double[] {{ 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0 }};
  double[] ddd = new double[] {{ 0.005, 0.005, 0.005, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }};
  String[] donly = new String[] {{ "", "_Trunk", "", "", "", "", "", "", "" }};
  int nk = KEYS.length;
  double[] hp = new double[nk];
  double[] sta = new double[nk];
  double[] mana = new double[nk];
  double[] dd = new double[nk];
  String[] only = new String[nk];
  for (int i = 0; i < nk; i++) {{
    String k = "perk." + KEYS[i] + ".";
    hp[i] = rate(p, k + "healthPerLevel", dhp[i]);
    sta[i] = rate(p, k + "staminaPerLevel", dsta[i]);
    mana[i] = rate(p, k + "manaPerLevel", dmana[i]);
    dd[i] = i <= 2 ? rate(p, k + "doubleDropPerLevel", ddd[i]) : 0.0;
    String o = p.getProperty(k + "doubleDropOnly");
    only[i] = o == null ? donly[i] : o.trim();
  }}
  HP = hp; STA = sta; MANA = mana; DD = dd; ONLY = only;
  DMG = rate(p, "perk.combat.damagePerLevel", 0.002);
  DMG_PVP = {PKG}.SkillCfg.bool(p, "perk.combat.damageVsPlayers", false);
  WEAPON_ONLY = {PKG}.SkillCfg.bool(p, "combat.classWeaponOnly", true);
}}""", pcfg))
# an xp.properties written by 0.1 / 0.2 has no perk.* key: append the documented section once (the code defaults apply either way)
pcfg.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    if (String.valueOf(en.nextElement()).startsWith("perk.")) return;
  }}
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the perks + class combat section (perk.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the perk.* section to xp.properties: " + t); }}
}}""", pcfg))
# ================= AlchCfg (0.4): alchemy.* + perk.alchemy.* keys of xp.properties =================
alc.addField(CtField.make("public static final String DEFAULTS = " + ALCH_LIT + ";", alc))
alc.addField(CtField.make('public static final String DEFAULT_EXTEND = "%s";' % ",".join(ALCH_EXTEND), alc))
for _decl in ("boolean ENABLED = true", "java.util.HashMap XP = new java.util.HashMap()",
              "long[] TIER = new long[] { %s }" % ", ".join("%dL" % x for x in ALCH_TIER),
              "double DUR_PER = 0.01", "double DUR_MAX = 1.0", "String[] EXTEND = new String[0]", "double EXTRA_PER = 0.002",
              "double EXTRA_MAX = 0.25", 'String[] EXTRA_ONLY = new String[] { "Potion_", "Weapon_Bomb_" }',
              'String[] EXTRA_NEVER = new String[] { "Potion_Empty" }', "int[] EXT_IDX = null", "long EXT_NEXT = 0L",
              "boolean EXT_WARNED = false"):
    alc.addField(CtField.make("public static volatile %s;" % _decl, alc))
alc.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap UNLISTED = new java.util.concurrent.ConcurrentHashMap();", alc))
alc.addMethod(CtNewMethod.make(f"""
public static java.util.HashMap defaultsMap() {{
  java.util.HashMap m = new java.util.HashMap();
{ALCH_PUTS}
  return m;
}}""", alc))
# "a, b,,c" -> {"a", "b", "c"}
alc.addMethod(CtNewMethod.make("""
public static String[] split(String v) {
  java.util.ArrayList l = new java.util.ArrayList();
  if (v != null) {
    String[] ps = v.split(",");
    for (int i = 0; i < ps.length; i++) { String t = ps[i].trim(); if (t.length() > 0) l.add(t); }
  }
  return (String[]) l.toArray(new String[0]);
}""", alc))
alc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ENABLED = {PKG}.SkillCfg.bool(p, "alchemy.enabled", true);
  java.util.HashMap m = defaultsMap();
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    String k = String.valueOf(en.nextElement()).trim();
    if (!k.startsWith("alchemy.xp.") || k.length() <= 11) continue;
    try {{
      long v = Long.parseLong(p.getProperty(k).trim());
      m.put(k.substring(11), Long.valueOf(v < 0L ? 0L : v));
    }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("bad line " + k + "=" + p.getProperty(k) + " (want a whole number)"); }}
  }}
  XP = m;
  long[] tier = new long[] {{ {", ".join("%dL" % x for x in ALCH_TIER)} }};
  String tv = p.getProperty("alchemy.tierXp");
  if (tv != null) {{
    String[] ps = tv.split(",");
    for (int i = 0; i < ps.length && i < tier.length; i++) {{
      try {{ long v = Long.parseLong(ps[i].trim()); tier[i] = v < 0L ? 0L : v; }} catch (Throwable t) {{ }}
    }}
  }}
  TIER = tier;
  DUR_PER = {PKG}.PerkCfg.rate(p, "perk.alchemy.durationPerLevel", 0.01);
  DUR_MAX = Math.min(10.0, {PKG}.PerkCfg.rate(p, "perk.alchemy.durationMax", 1.0));
  EXTEND = split(p.getProperty("perk.alchemy.extend", DEFAULT_EXTEND));
  EXT_IDX = null;
  EXT_NEXT = 0L;
  EXT_WARNED = false;
  EXTRA_PER = {PKG}.PerkCfg.rate(p, "perk.alchemy.extraPotionPerLevel", 0.002);
  EXTRA_MAX = Math.min(1.0, {PKG}.PerkCfg.rate(p, "perk.alchemy.extraPotionMax", 0.25));
  EXTRA_ONLY = split(p.getProperty("perk.alchemy.extraPotionOnly", "Potion_,Weapon_Bomb_"));
  EXTRA_NEVER = split(p.getProperty("perk.alchemy.extraPotionNever", "Potion_Empty"));
  UNLISTED.clear();
}}""", alc))
alc.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    if (String.valueOf(en.nextElement()).startsWith("alchemy.")) return;
  }}
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Alchemy section (alchemy.* + perk.alchemy.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the alchemy.* section to xp.properties: " + t); }}
}}""", alc))
# base XP of one finished Alchemy Bench craft (table by output id, else alchemy.tierXp by bench tier - named once in the log)
alc.addMethod(CtNewMethod.make(f"""
public static long xpFor(String id, int tier) {{
  if (id == null) return 0L;
  Object x = XP.get(id);
  if (x instanceof Long) return ((Long) x).longValue();
  long[] tt = TIER;
  int t = tier < 1 ? 1 : (tier > tt.length ? tt.length : tier);
  long v = tt[t - 1];
  if (UNLISTED.putIfAbsent(id, Boolean.TRUE) == null) {PKG}.SkillCfg.info("alchemy: " + id + " (bench tier " + t + ") is not in alchemy.xp.* - it pays alchemy.tierXp " + v + " per craft; add alchemy.xp." + id + "=<xp> to change that");
  return v;
}}""", alc))
alc.addMethod(CtNewMethod.make("""
public static boolean extraOk(String id) {
  if (id == null) return false;
  String[] nv = EXTRA_NEVER;
  for (int i = 0; i < nv.length; i++) if (id.startsWith(nv[i])) return false;
  String[] on = EXTRA_ONLY;
  if (on.length == 0) return true;
  for (int i = 0; i < on.length; i++) if (id.startsWith(on[i])) return true;
  return false;
}""", alc))
# effect ids of perk.alchemy.extend -> asset indexes (lazy: the asset map is ready once players are in; retried every 10 s while none
# resolves; reset by read())
alc.addMethod(CtNewMethod.make(f"""
public static int[] extIdx() {{
  int[] c = EXT_IDX;
  if (c != null) return c;
  long now = System.currentTimeMillis();
  if (now < EXT_NEXT) return null;
  EXT_NEXT = now + 10000L;
  String[] ids = EXTEND;
  int[] tmp = new int[ids.length];
  int n = 0;
  StringBuilder miss = new StringBuilder();
  for (int i = 0; i < ids.length; i++) {{
    int x = Integer.MIN_VALUE;
    try {{ x = {EFX}.getAssetMap().getIndex(ids[i]); }} catch (Throwable t) {{ }}
    if (x == Integer.MIN_VALUE || x < 0) {{ miss.append(' ').append(ids[i]); continue; }}
    tmp[n] = x;
    n++;
  }}
  int[] r = new int[n];
  for (int i = 0; i < n; i++) r[i] = tmp[i];
  if (miss.length() > 0 && !EXT_WARNED) {{ EXT_WARNED = true; {PKG}.SkillCfg.warn("perk.alchemy.extend: unknown effect id(s)" + miss + " - ignored"); }}
  if (n > 0 || ids.length == 0) EXT_IDX = r;
  return r;
}}""", alc))

# ================= SmithCfg (0.4): smithing.* keys (Smithing-Smelting spec 2.6; forOutput is added after SkillCfg.resolve) =================
smc.addField(CtField.make("public static final String DEFAULTS = " + SMITH_LIT + ";", smc))
for _decl in ("boolean ENABLED = true", "boolean VANILLA = true", "double ORE_FACTOR = 1.0", "long DEFAULT = 1L",
              "java.util.HashMap XP = new java.util.HashMap()"):
    smc.addField(CtField.make("public static volatile %s;" % _decl, smc))
smc.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();", smc))
smc.addMethod(CtNewMethod.make(f"""
public static java.util.HashMap defaultsMap() {{
  java.util.HashMap m = new java.util.HashMap();
{SMITH_PUTS}
  return m;
}}""", smc))
smc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ENABLED = {PKG}.SkillCfg.bool(p, "smithing.smelt.enabled", true);
  VANILLA = {PKG}.SkillCfg.bool(p, "smithing.vanillaFurnace", true);
  double f = {PKG}.SkillCfg.dbl(p, "smithing.oreFactor", 1.0);
  ORE_FACTOR = (Double.isNaN(f) || f < 0.0) ? 0.0 : f;
  long d = {PKG}.SkillCfg.lng(p, "smithing.smeltDefault", 1L);
  DEFAULT = d < 0L ? 0L : d;
  java.util.HashMap m = defaultsMap();
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    String k = String.valueOf(en.nextElement()).trim();
    if (!k.startsWith("smithing.xp.") || k.length() <= 12) continue;
    try {{
      long v = Long.parseLong(p.getProperty(k).trim());
      m.put(k.substring(12), Long.valueOf(v < 0L ? 0L : v));
    }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("bad line " + k + "=" + p.getProperty(k) + " (want a whole number)"); }}
  }}
  XP = m;
  CACHE.clear();
}}""", smc))
smc.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    if (String.valueOf(en.nextElement()).startsWith("smithing.")) return;
  }}
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Smithing section (smithing.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the smithing.* section to xp.properties: " + t); }}
}}""", smc))

# ================= ExplCfg (0.4.1): the Exploration block of xp.properties (research/Exploration-Build-Spec.md 3.2 / 3.3) =================
# exploration.enabled=false refuses every Exploration grant (BridgeCfg.read sets GRANT[EXPLORATION] from it, so ExplCfg.read runs first).
# perk.exploration.staminaPerLevel is read by PerkCfg like every perk.* key, acro.treeDodgeMax by AcroCfg. Appended ONCE to an existing
# xp.properties that has no exploration.enabled key (the AlchCfg pattern; a restart finds the key and appends nothing).
exc.addField(CtField.make("public static final String DEFAULTS = " + EXPL_LIT + ";", exc))
exc.addField(CtField.make("public static volatile boolean ENABLED = true;", exc))
exc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ENABLED = {PKG}.SkillCfg.bool(p, "exploration.enabled", true);
}}""", exc))
exc.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  if (p.getProperty("exploration.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Exploration section (exploration.enabled, perk.exploration.staminaPerLevel, acro.treeDodgeMax - default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Exploration section to xp.properties: " + t); }}
}}""", exc))

# ================= FellCfg (0.4.2): the Felled trees block of xp.properties (research/Tree-Fall-Spec.md 3.1) =================
# Read by SkillCfg.load (so /skills reload re-reads it), appended ONCE to an existing file without fell.enabled (the AlchCfg pattern; the
# code defaults are the same numbers). BROKEN = EnvSys could not be registered: the feature stays off until the next restart (spec 2.4).
# CODE / FAM (block index -> kind / family) and IDCODE / IDFAM (block id -> kind / family) are FellDefs' caches; cleared by read()
# because fell.extraTrees changes what counts as a tree.
fcf.addField(CtField.make("public static final String DEFAULTS = " + FELL_LIT + ";", fcf))
for decl in ("boolean ENABLED = true", "boolean BROKEN = false", "double XP_FACTOR = 1.0", "boolean LEAVES = true", "double LEAF_XP_FACTOR = 1.0",
             "boolean NEED_LEAVES = true", "boolean UNDER_TRUNK = true", "boolean DOUBLE_DROPS = true", "boolean COLLECTIONS = true",
             "boolean NODES = true", "boolean MESSAGE = true", "int RADIUS = 8", "int HEIGHT = 64", "int MAX_LOGS = 256", "int MAX_LEAVES = 384",
             "int MAX_READS = 8000", "int MAX_SNAPS = 10", "int MAX_PER_PLAYER = 4", "int MAX_WATCHES = 64", "long POLL_MS = 200L",
             "long QUIET_MS = 3000L", "long MAX_WATCH_MS = 60000L", "long MEMORY_MS = 60000L", "boolean DEBUG = false",
             "boolean EXTRA_TREES = false", "boolean SKIP_SAPLINGS = true", "boolean DD_COLLECTIONS = false",
             "java.util.HashSet DISABLED = new java.util.HashSet()"):
    fcf.addField(CtField.make("public static volatile " + decl + ";", fcf))
for nm in ("CODE", "FAM", "IDCODE", "IDFAM"):
    fcf.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap " + nm + " = new java.util.concurrent.ConcurrentHashMap();", fcf))
fcf.addMethod(CtNewMethod.make("""
public static boolean on() {
  return ENABLED && !BROKEN;
}""", fcf))
fcf.addMethod(CtNewMethod.make("""
public static long clampL(long v, long lo, long hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}""", fcf))
fcf.addMethod(CtNewMethod.make("""
public static double clampD(double v, double lo, double hi) {
  if (Double.isNaN(v) || v < lo) return lo;
  if (v > hi) return hi;
  return v;
}""", fcf))
fcf.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ENABLED = {PKG}.SkillCfg.bool(p, "fell.enabled", true);
  XP_FACTOR = clampD({PKG}.SkillCfg.dbl(p, "fell.xpFactor", 1.0), 0.0, 5.0);
  LEAVES = {PKG}.SkillCfg.bool(p, "fell.leaves", true);
  LEAF_XP_FACTOR = clampD({PKG}.SkillCfg.dbl(p, "fell.leafXpFactor", 1.0), 0.0, 5.0);
  NEED_LEAVES = {PKG}.SkillCfg.bool(p, "fell.needLeaves", true);
  UNDER_TRUNK = {PKG}.SkillCfg.bool(p, "fell.underTrunk", true);
  DOUBLE_DROPS = {PKG}.SkillCfg.bool(p, "fell.doubleDrops", true);
  COLLECTIONS = {PKG}.SkillCfg.bool(p, "fell.collections", true);
  NODES = {PKG}.SkillCfg.bool(p, "fell.nodes", true);
  MESSAGE = {PKG}.SkillCfg.bool(p, "fell.message", true);
  RADIUS = (int) clampL({PKG}.SkillCfg.lng(p, "fell.radius", 8L), 1L, 16L);
  HEIGHT = (int) clampL({PKG}.SkillCfg.lng(p, "fell.height", 64L), 1L, 128L);
  MAX_LOGS = (int) clampL({PKG}.SkillCfg.lng(p, "fell.maxLogs", 256L), 1L, 1024L);
  MAX_LEAVES = (int) clampL({PKG}.SkillCfg.lng(p, "fell.maxLeaves", 384L), 0L, 2048L);
  MAX_READS = (int) clampL({PKG}.SkillCfg.lng(p, "fell.maxReads", 8000L), 100L, 100000L);
  MAX_SNAPS = (int) clampL({PKG}.SkillCfg.lng(p, "fell.maxSnapshotsPerSecond", 10L), 1L, 100L);
  MAX_PER_PLAYER = (int) clampL({PKG}.SkillCfg.lng(p, "fell.maxWatchesPerPlayer", 4L), 1L, 64L);
  MAX_WATCHES = (int) clampL({PKG}.SkillCfg.lng(p, "fell.maxWatches", 64L), 1L, 1024L);
  POLL_MS = clampL({PKG}.SkillCfg.lng(p, "fell.pollMs", 200L), 50L, 1000L);
  QUIET_MS = clampL({PKG}.SkillCfg.lng(p, "fell.quietMs", 3000L), 500L, 10000L);
  MAX_WATCH_MS = clampL({PKG}.SkillCfg.lng(p, "fell.maxWatchMs", 60000L), 1000L, 600000L);
  MEMORY_MS = clampL({PKG}.SkillCfg.lng(p, "fell.memoryMs", 60000L), 0L, 600000L);
  DEBUG = {PKG}.SkillCfg.bool(p, "fell.debug", false);
  EXTRA_TREES = {PKG}.SkillCfg.bool(p, "fell.extraTrees", false);
  SKIP_SAPLINGS = {PKG}.SkillCfg.bool(p, "placed.skipSaplings", true);
  DD_COLLECTIONS = {PKG}.SkillCfg.bool(p, "collections.doubleDrops", false);
  java.util.HashSet ds = new java.util.HashSet();
  String dw = p.getProperty("fell.disabledWorlds");
  if (dw != null) {{
    String[] ps = dw.split(",");
    for (int i = 0; i < ps.length; i++) {{
      String t = ps[i].trim().toLowerCase(java.util.Locale.ROOT);
      if (t.length() > 0) ds.add(t);
    }}
  }}
  DISABLED = ds;
  CODE.clear();
  FAM.clear();
  IDCODE.clear();
  IDFAM.clear();
}}""", fcf))
fcf.addMethod(CtNewMethod.make("""
public static boolean worldOk(String w) {
  if (w == null) return false;
  java.util.HashSet d = DISABLED;
  return d.isEmpty() || !d.contains(w.toLowerCase(java.util.Locale.ROOT));
}""", fcf))
fcf.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  if (p.getProperty("fell.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Felled trees section (fell.*, placed.skipSaplings, collections.doubleDrops - default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Felled trees section to xp.properties: " + t); }}
}}""", fcf))
fcf.addMethod(CtNewMethod.make("""
public static String text() {
  if (BROKEN) return "OFF (the explosion / fire guard EnvSys could not be registered - see the warning above)";
  if (!ENABLED) return "off (fell.enabled=false)";
  return "on (XP x" + XP_FACTOR + (LEAVES ? ", leaves x" + LEAF_XP_FACTOR : ", leaves not paid") + (DOUBLE_DROPS ? ", double drops" : "") + (COLLECTIONS ? ", collections" : "") + (EXTRA_TREES ? ", + apple trees" : "") + ")";
}""", fcf))

# ================= PartyCfg (0.4.2 stage 2): party.combatShare.* of xp.properties (beta backlog 6: "party should share combat XP") ======
# Read by SkillCfg.load (/skills reload re-reads it); appended ONCE to an existing file without party.combatShare.enabled (the FellCfg
# pattern; the code defaults are the same numbers).
pcg.addField(CtField.make("public static final String DEFAULTS = " + PARTY_LIT + ";", pcg))
for decl in ("boolean ON = true", "double FRACTION = 0.5", "double RADIUS = 48.0", "boolean TREE_BONUS = true", "boolean MESSAGE = true"):
    pcg.addField(CtField.make("public static volatile " + decl + ";", pcg))
pcg.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ON = {PKG}.SkillCfg.bool(p, "party.combatShare.enabled", true);
  double f = {PKG}.SkillCfg.dbl(p, "party.combatShare.fraction", 0.5);
  FRACTION = (Double.isNaN(f) || f < 0.0) ? 0.0 : (f > 1.0 ? 1.0 : f);
  double r = {PKG}.SkillCfg.dbl(p, "party.combatShare.radius", 48.0);
  RADIUS = (Double.isNaN(r) || r < 1.0) ? 1.0 : (r > 512.0 ? 512.0 : r);
  TREE_BONUS = {PKG}.SkillCfg.bool(p, "party.combatShare.treeBonus", true);
  MESSAGE = {PKG}.SkillCfg.bool(p, "party.combatShare.message", true);
}}""", pcg))
pcg.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  if (p.getProperty("party.combatShare.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Party combat XP section (party.combatShare.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Party combat XP section to xp.properties: " + t); }}
}}""", pcg))
pcg.addMethod(CtNewMethod.make("""
public static boolean on() {
  return ON && FRACTION > 0.0;
}""", pcg))
pcg.addMethod(CtNewMethod.make("""
public static String pct() {
  return String.valueOf(Math.round(FRACTION * 100.0)) + "%";
}""", pcg))
pcg.addMethod(CtNewMethod.make("""
public static String blocks() {
  double r = RADIUS;
  if (r == Math.floor(r)) return String.valueOf((long) r);
  return String.valueOf(Math.round(r * 10.0) / 10.0);
}""", pcg))
pcg.addMethod(CtNewMethod.make("""
public static String text() {
  if (!on()) return "off";
  return "on (" + pct() + " to party members within " + blocks() + " blocks" + (TREE_BONUS ? " + their tree XP bonus" : "") + ")";
}""", pcg))

# ================= DivCfg (0.4.4): divinity.* of xp.properties - Divinity XP from Priest heals (Classes-Berserker-Priest-Spec 3.4 / 3.5) ==
# Read by SkillCfg.load (/skills reload and the kit's reload routine re-read it); appended ONCE to an existing file without
# divinity.healXp.enabled (the PartyCfg pattern; the code defaults are the same numbers). Clamps = the Server Setup row bounds.
dvc.addField(CtField.make("public static final String DEFAULTS = " + DIV_LIT + ";", dvc))
# 0.4.11: the FINAL heal XP defaults (= HEAL_PER_HP_DEF / HEAL_MAX_DEF / HEAL_SELF_DEF; asserted)
assert (HEAL_PER_HP_DEF, HEAL_MAX_DEF, HEAL_SELF_DEF) == ("1", "900", "1.25")
for decl in ("boolean ON = true", "double PER_HP = 1.0", "long MAX_MIN = 900L", "double PER_HP_SELF = 1.25"):
    dvc.addField(CtField.make("public static volatile " + decl + ";", dvc))
dvc.addField(CtField.make("public static final String SELF_DEFAULTS = " + DIVS_LIT + ";", dvc))   # 0.4.6
dvc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ON = {PKG}.SkillCfg.bool(p, "divinity.healXp.enabled", true);
  double r = {PKG}.SkillCfg.dbl(p, "divinity.healXpPerHp", 1.0);
  PER_HP = (Double.isNaN(r) || r < 0.0) ? 0.0 : (r > 100.0 ? 100.0 : r);
  double rs = {PKG}.SkillCfg.dbl(p, "divinity.healXpPerHpSelf", 1.25);
  PER_HP_SELF = (Double.isNaN(rs) || rs < 0.0) ? 0.0 : (rs > 100.0 ? 100.0 : rs);
  long m = {PKG}.SkillCfg.lng(p, "divinity.healXpMaxPerMinute", 900L);
  MAX_MIN = m < 0L ? 0L : (m > 1000000000L ? 1000000000L : m);
}}""", dvc))
dvc.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  if (p.getProperty("divinity.healXp.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Divinity section (divinity.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Divinity section to xp.properties: " + t); }}
}}""", dvc))
# 0.4.6: ensureSelf appends the self-heal block once to a file without divinity.healXpPerHpSelf (the ensureDefaults pattern)
dvc.addMethod(CtNewMethod.make(f"""
public static void ensureSelf(java.util.Properties p) {{
  if (p.getProperty("divinity.healXpPerHpSelf") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + SELF_DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Divinity self-heal section (divinity.healXpPerHpSelf={HEAL_SELF_DEF})");
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
}""", dvc))
# 0.2 -> "0.2", 1.0 -> "1", 0.125 -> "0.125" (3 decimals at most)
dvc.addMethod(CtNewMethod.make("""
public static String num(double v) {
  if (Double.isNaN(v) || Double.isInfinite(v)) return "0";
  if (v == Math.floor(v) && Math.abs(v) < 1.0E15) return String.valueOf((long) v);
  return String.valueOf(Math.round(v * 1000.0) / 1000.0);
}""", dvc))
dvc.addMethod(CtNewMethod.make("""
public static String text() {
  if (!on()) return "off";
  return "on (" + num(PER_HP) + " XP per HP healed on others, " + num(PER_HP_SELF) + " on yourself" + (MAX_MIN > 0L ? ", up to " + MAX_MIN + " a minute" : "") + ")";
}""", dvc))
# the Stats page's Divinity "Boosts right now" line (spec 3.6). 0.4.11: heal XP is not multiplied by the class skill XP multiplier, so the
# rows ARE what the Priest gets: "Healing pays 1 Divinity XP per HP on others, 1.25 on yourself (max 900 a minute)" (the 0.4.9 text) at
# any class skill XP multiplier. Only the general XP multiplier (SkillCfg.MULT, after the cap) shows effective numbers when it is not 1.
dvc.addMethod(CtNewMethod.make(f"""
public static String statsLine() {{
  if (!on()) return "Divinity XP from healing is off on this server";
  double m = {PKG}.SkillCfg.MULT;
  if (m == 1.0) return "Healing pays " + num(PER_HP) + " Divinity XP per HP on others, " + num(PER_HP_SELF) + " on yourself" + (MAX_MIN > 0L ? " (max " + MAX_MIN + " a minute)" : "");
  if (!(m > 0.0)) return "Healing pays no Divinity XP on this server (XP multiplier x0)";
  return "Healing pays " + num(PER_HP * m) + " Divinity XP per HP on others, " + num(PER_HP_SELF * m) + " on yourself (XP multiplier x" + num(m) + (MAX_MIN > 0L ? ", max " + num((double) MAX_MIN * m) + " a minute" : "") + ")";
}}""", dvc))

# ================= XbowCfg (0.4.5): perk.archery.keepLoaded.* of xp.properties - crossbows stay loaded (Crossbow-Loaded-Spec 3.2) =========
# Read by SkillCfg.load (/skills reload and the kit's reload routine re-read it); appended ONCE to an existing file without
# perk.archery.keepLoaded.enabled (the FellCfg / PartyCfg pattern; the code defaults are the same values). Clamps = the Server Setup rows.
xcf.addField(CtField.make("public static final String DEFAULTS = " + XBOW_LIT + ";", xcf))
for decl in ("boolean ON = true", "int LEVEL = 5", 'String[] ITEMS = new String[] { "Weapon_Crossbow_" }', "int DELAY = 3", "boolean DEBUG = false",
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
}}""", xcf))
xcf.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ON = {PKG}.SkillCfg.bool(p, "perk.archery.keepLoaded.enabled", true);
  long lv = {PKG}.SkillCfg.lng(p, "perk.archery.keepLoaded.level", 5L);
  LEVEL = (int) (lv < 0L ? 0L : (lv > 100L ? 100L : lv));
  java.util.ArrayList l = new java.util.ArrayList();
  String raw = p.getProperty("perk.archery.keepLoaded.items", "Weapon_Crossbow_");
  String[] ps = raw == null ? new String[0] : raw.split(",");
  for (int i = 0; i < ps.length; i++) {{
    String t = ps[i].trim();
    if (t.length() > 0) l.add(t);
  }}
  String[] it = new String[l.size()];
  for (int i = 0; i < it.length; i++) it[i] = (String) l.get(i);
  if (it.length == 0) it = new String[] {{ "Weapon_Crossbow_" }};
  ITEMS = it;
  long d = {PKG}.SkillCfg.lng(p, "perk.archery.keepLoaded.delayTicks", 3L);
  DELAY = (int) (d < 3L ? 3L : (d > 20L ? 20L : d));
  DEBUG = {PKG}.SkillCfg.bool(p, "perk.archery.keepLoaded.debug", false);
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
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + EXTRA_DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Crossbows stay loaded extras section (perk.archery.keepLoaded.meter / sound / hint)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Crossbows stay loaded extras section to xp.properties: " + t); }}
}}""", xcf))
# 0.4.6: check= hook of the perk.archery.keepLoaded.sound row (CONFIG-CONTRACT check=: null = fine, text = refuse)
xcf.addMethod(CtNewMethod.make("""
public static String checkSound(String key, String v) {
  return soundProblem(v);
}""", xcf))
xcf.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  if (p.getProperty("perk.archery.keepLoaded.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Crossbows stay loaded section (perk.archery.keepLoaded.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Crossbows stay loaded section to xp.properties: " + t); }}
}}""", xcf))
# id starts with one of ITEMS (default Weapon_Crossbow_: Iron, Ancient Steel and the four More Crossbow Tiers crossbows)
xcf.addMethod(CtNewMethod.make("""
public static boolean isCrossbow(String id) {
  if (id == null || id.length() == 0) return false;
  String[] a = ITEMS;
  for (int i = 0; i < a.length; i++) if (a[i] != null && a[i].length() > 0 && id.startsWith(a[i])) return true;
  return false;
}""", xcf))
# check= hook of the perk.archery.keepLoaded.items row (CONFIG-CONTRACT check=, kit runs it before saving an in-game edit, no kit lock
# held): refuses an empty list, an entry that is not an id start (no * : or spaces) and an entry no loaded item id starts with (a typo);
# asks first when an entry also matches ids without "Crossbow" (Weapon_ would count swords and bows). The engine's item map is the one
# the kit's own item check reads; unreadable or empty (bare JVM) = the ids are not checked.
xcf.addMethod(CtNewMethod.make(f"""
public static String checkItems(String key, String v) {{
  if (v == null) return null;
  java.util.Set ids = null;
  try {{
    java.util.Map m = {ITM}.getAssetMap().getAssetMap();
    if (m != null && !m.isEmpty()) ids = m.keySet();
  }} catch (Throwable t) {{ ids = null; }}
  String[] ps = v.split(",");
  int n = 0;
  String wide = null;
  String wideEx = null;
  int wideN = 0;
  for (int i = 0; i < ps.length; i++) {{
    String t = ps[i].trim();
    if (t.length() == 0) continue;
    n++;
    if (t.length() > 120) return "An id start is at most 120 characters: " + t.substring(0, 40) + "...";
    for (int k = 0; k < t.length(); k++) {{
      char c = t.charAt(k);
      if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-' || c == '.'))
        return "Write item id starts like Weapon_Crossbow_, separated by commas (no *, : or spaces): " + t;
    }}
    if (ids == null) continue;
    int hit = 0;
    int other = 0;
    String ex = null;
    boolean read = true;
    try {{
      java.util.Iterator it = ids.iterator();
      while (it.hasNext()) {{
        String id = String.valueOf(it.next());
        if (id.startsWith(t)) {{
          hit++;
          if (id.indexOf("Crossbow") < 0) {{ other++; if (ex == null) ex = id; }}
        }}
      }}
    }} catch (Throwable x) {{ read = false; }}
    if (!read) continue;
    if (hit == 0) return "No item id starts with " + t + ".";
    if (other > 0 && wide == null) {{ wide = t; wideN = other; wideEx = ex; }}
  }}
  if (n == 0) return "List at least one item id start, like Weapon_Crossbow_.";
  if (wide != null) {{
    if (wideEx.length() > 40) wideEx = wideEx.substring(0, 40) + "...";
    String w = wide.length() > 40 ? wide.substring(0, 40) + "..." : wide;
    return "?" + w + " also matches " + wideN + " item(s) without Crossbow in the id, like " + wideEx + ". Count them as crossbows?";
  }}
  return null;
}}""", xcf))
xcf.addMethod(CtNewMethod.make("""
public static String text() {
  if (!ON) return "off";
  return "on (Archers from Archery " + LEVEL + ", bolts back after " + DELAY + " ticks, loads survive teleports" + (METER ? ", big-arrow meter kept" : "") + (SOUND.length() > 0 ? ", sound " + SOUND : ", no sound") + (HINT ? ", chat hint" : "") + (DEBUG ? ", DEBUG chat lines on" : "") + ")";
}""", xcf))

# XbowState (spec 2.3): one per online player, world thread only. n / stk / cre = the kept load per hotbar slot (bolts, the stack seen at
# the switch away, Creative then); enterAt = ticks at the last switch onto the current slot (a fresh state = "long ago": no switch was
# seen while the perk was on, so the held item was not just switched onto); pendSlot / pendAt = the armed restore (-1 = none).
xst.addField(CtField.make("public " + REF + " ref;", xst))
xst.addField(CtField.make("public " + PR + " pr;", xst))        # 0.4.6: the connection this state belongs to (world change vs relog)
xst.addField(CtField.make("public float[] sig;", xst))         # 0.4.6: kept SignatureEnergy per hotbar slot (the big-arrow meter)
xst.addField(CtField.make("public float[] chg;", xst))         # 0.4.6: kept SignatureCharges per hotbar slot (an armed big arrow)
xst.addField(CtField.make("public long epoch;", xst))
xst.addField(CtField.make("public long ticks;", xst))
xst.addField(CtField.make("public int[] n;", xst))
xst.addField(CtField.make("public " + IS + "[] stk;", xst))
xst.addField(CtField.make("public boolean[] cre;", xst))
xst.addField(CtField.make("public long enterAt;", xst))
xst.addField(CtField.make("public int pendSlot;", xst))
xst.addField(CtField.make("public long pendAt;", xst))
xst.addConstructor(CtNewConstructor.make(f"""
public XbowState() {{
  this.ref = null;
  this.pr = null;
  this.sig = new float[16];
  this.chg = new float[16];
  this.epoch = -1L;
  this.ticks = 0L;
  this.n = new int[16];
  this.stk = new {IS}[16];
  this.cre = new boolean[16];
  this.enterAt = -1000000L;
  this.pendSlot = -1;
  this.pendAt = 0L;
}}""", xst))

# ================= OverallCfg (0.4.6): the Overall Level + base Mana block of xp.properties (research/Overall-Level-Spec.md 4.3) =================
# Read by SkillCfg.load (/skills reload and the kit's reload routine); appended ONCE to an existing file without overall.enabled (the
# DivCfg / XbowCfg pattern; the code defaults are the same numbers). Clamps = the Server Setup row bounds.
ovc.addField(CtField.make("public static final String DEFAULTS = " + OVL_LIT + ";", ovc))
ovc.addField(CtField.make('public static final String SKILLS_DEFAULT = "%s";' % OVL_SKILLS_DEF, ovc))
for _decl in ("boolean MANA_ON = true", "double BASE = 10.0", "boolean ON = true", "int[] SLOTS = new int[] { 0, 1, 2, 4, 10, 11, 12, 13 }",
              "boolean CLASS = true", "double HP = 0.5", "double MANA = 0.2", "boolean HEAL = true", "boolean CHAT = true",
              # 0.4.8 Base Mana by class: TBL = the table as ONE snapshot Object[]{String[] classes (SkillDefs.CLASSES spelling and order),
              # double[] base, String text "Mage 30, Priest 30"} (null = not read yet = the default table); LEGACY = it came from the 0.4.7
              # pair because ManaMig could not move it; GUARD_DIRTY = ManaGuard runs on the next tick; WARNED = the last table WARN
              "Object[] TBL = null", "boolean LEGACY = false", "boolean GUARD_DIRTY = true", 'String WARNED = ""'):
    ovc.addField(CtField.make("public static volatile " + _decl + ";", ovc))
ovc.addField(CtField.make('public static final String TABLE_PREFIX = "mana.classBase.";', ovc))
ovc.addField(CtField.make("public static final String[] DEF_CLS = %s;" % jarr([_c for _c, _v in CLASS_BASE_DEF]), ovc))
ovc.addField(CtField.make("public static final double[] DEF_BASE = new double[] { %s };" % ", ".join("%d.0" % _v for _c, _v in CLASS_BASE_DEF), ovc))
ovc.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  if (p.getProperty("overall.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Overall Level + base Mana section (mana.* / overall.* keys, default values)");
    java.util.Properties d = new java.util.Properties();
    d.load(new java.io.StringReader(DEFAULTS));
    java.util.Iterator it = d.stringPropertyNames().iterator();
    while (it.hasNext()) {{
      String k = (String) it.next();
      if (p.getProperty(k) == null) p.setProperty(k, d.getProperty(k));
    }}
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
# 0.4.8 Base Mana by class (tools/skills_0_4_8_patch.py point 2). Table entries are class names in any case, stored and shown with the
# SkillDefs.CLASSES spelling and in that order.
ovc.addMethod(CtNewMethod.make(f"""
public static String canonClass(String t) {{
  if (t == null) return null;
  String x = t.trim();
  for (int k = 0; k < {PKG}.SkillDefs.CLASSES.length; k++) if ({PKG}.SkillDefs.CLASSES[k].equalsIgnoreCase(x)) return {PKG}.SkillDefs.CLASSES[k];
  return null;
}}""", ovc))
# {String[] classes, double[] base, String text} in SkillDefs.CLASSES order; entries that are not a class are dropped, the first of a class wins
ovc.addMethod(CtNewMethod.make(f"""
public static Object[] mkTable(String[] c, double[] b) {{
  int n = {PKG}.SkillDefs.CLASSES.length;
  boolean[] has = new boolean[n];
  double[] v = new double[n];
  int cnt = 0;
  for (int i = 0; i < c.length && i < b.length; i++) {{
    String x = canonClass(c[i]);
    if (x == null) continue;
    for (int k = 0; k < n; k++) {{
      if ({PKG}.SkillDefs.CLASSES[k].equals(x) && !has[k]) {{ has[k] = true; v[k] = b[i]; cnt++; }}
    }}
  }}
  String[] oc = new String[cnt];
  double[] ob = new double[cnt];
  StringBuilder sb = new StringBuilder();
  int j = 0;
  for (int k = 0; k < n; k++) {{
    if (!has[k]) continue;
    oc[j] = {PKG}.SkillDefs.CLASSES[k];
    ob[j] = v[k];
    if (j > 0) sb.append(", ");
    sb.append(oc[j]).append(" ").append({PKG}.DivCfg.num(v[k]));
    j++;
  }}
  return new Object[] {{ oc, ob, sb.toString() }};
}}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static Object[] defTable() {
  return mkTable(DEF_CLS, DEF_BASE);
}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static Object[] tbl() {
  Object[] t = TBL;
  if (t == null) {
    t = defTable();
    TBL = t;
  }
  return t;
}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static boolean anyTableKey(java.util.Properties p) {
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) if (((String) it.next()).startsWith(TABLE_PREFIX)) return true;
  return false;
}""", ovc))
# the mana.classBase.<Class>=<Mana> lines -> {String[], double[], String text, String problems ("" = none)}. Keys are read in sorted order,
# so of two spellings of one class the exact SkillDefs.CLASSES spelling wins (it sorts first: capital letters come before small ones)
# and the other is reported; a line that is not a class or not a number is left out and reported; values are clamped to 0-10000 like
# the row bounds (the kit refuses them when typed).
ovc.addMethod(CtNewMethod.make(f"""
public static Object[] parseTable(java.util.Properties p) {{
  java.util.ArrayList cs = new java.util.ArrayList();
  java.util.ArrayList bs = new java.util.ArrayList();
  StringBuilder bad = new StringBuilder();
  java.util.Iterator it = new java.util.TreeSet(p.stringPropertyNames()).iterator();
  while (it.hasNext()) {{
    String k = (String) it.next();
    if (!k.startsWith(TABLE_PREFIX)) continue;
    String e = k.substring(TABLE_PREFIX.length()).trim();
    String c = canonClass(e);
    String raw = p.getProperty(k);
    String shown = e.length() > 40 ? e.substring(0, 40) + "..." : e;
    if (c == null) {{ if (bad.length() > 0) bad.append("; "); bad.append(shown + " is not a class (left out)"); continue; }}
    if (cs.contains(c)) {{ if (bad.length() > 0) bad.append("; "); bad.append(c + " is listed twice (" + shown + " left out)"); continue; }}
    double v = Double.NaN;
    try {{ v = Double.parseDouble(raw.trim()); }} catch (Throwable t) {{ v = Double.NaN; }}
    if (Double.isNaN(v) || Double.isInfinite(v)) {{
      if (bad.length() > 0) bad.append("; ");
      String rv = raw == null ? "" : raw.trim();
      bad.append(shown + "=" + (rv.length() > 20 ? rv.substring(0, 20) + "..." : rv) + " is not a number (left out)");
      continue;
    }}
    cs.add(c);
    bs.add(Double.valueOf(clampD(v, 0.0, 0.0, 10000.0)));
  }}
  String[] c2 = new String[cs.size()];
  double[] b2 = new double[cs.size()];
  for (int i = 0; i < c2.length; i++) {{ c2[i] = (String) cs.get(i); b2[i] = ((Double) bs.get(i)).doubleValue(); }}
  Object[] t = mkTable(c2, b2);
  return new Object[] {{ t[0], t[1], t[2], bad.toString() }};
}}""", ovc))
# the 0.4.7 pair read as the table (only while ManaMig could not move it): every class of mana.magicClasses (default Mage,Priest) gets
# mana.magicBase (default 20), exactly what 0.4.7 gave them
ovc.addMethod(CtNewMethod.make(f"""
public static Object[] legacyTable(java.util.Properties p) {{
  double b = clampD({PKG}.SkillCfg.dbl(p, "mana.magicBase", 20.0), 20.0, 0.0, 10000.0);
  String mc = p.getProperty("mana.magicClasses");
  String[] c = parseClasses(mc == null ? "Mage,Priest" : mc);
  double[] v = new double[c.length];
  for (int i = 0; i < v.length; i++) v[i] = b;
  return mkTable(c, v);
}}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static double baseFor(String cls) {
  if (cls != null) {
    String x = cls.trim();
    Object[] t = tbl();
    String[] c = (String[]) t[0];
    double[] b = (double[]) t[1];
    for (int i = 0; i < c.length && i < b.length; i++) if (c[i].equalsIgnoreCase(x)) return b[i];
  }
  return BASE;
}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static boolean listed(String cls) {
  if (cls == null) return false;
  String x = cls.trim();
  String[] c = (String[]) tbl()[0];
  for (int i = 0; i < c.length; i++) if (c[i].equalsIgnoreCase(x)) return true;
  return false;
}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static String tableText() {
  return (String) tbl()[2];
}""", ovc))
# check= hook of the mana.classBase table (CONFIG-CONTRACT: key = "mana.classBase[<entry>]", value = the canonical Mana text or null for a
# removal; also run for hand-edited lines, kit 1.1): the entry must be a class name (any case - the loader stores the canonical spelling)
ovc.addMethod(CtNewMethod.make("""
public static String checkClassBase(String key, String value) {
  if (value == null || key == null) return null;
  String e = key;
  int a = key.indexOf('[');
  int b = key.lastIndexOf(']');
  if (a >= 0 && b > a) e = key.substring(a + 1, b);
  if (canonClass(e) != null) return null;
  if (e.length() > 40) e = e.substring(0, 40) + "...";
  return "Unknown class " + e + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Shaman.";
}""", ovc))
ovc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  MANA_ON = {PKG}.SkillCfg.bool(p, "mana.base.enabled", true);
  BASE = clampD({PKG}.SkillCfg.dbl(p, "mana.base", 10.0), 10.0, 0.0, 10000.0);
  boolean tk = anyTableKey(p);
  boolean old = p.getProperty("mana.magicBase") != null || p.getProperty("mana.magicClasses") != null;
  Object[] t = null;
  String w = "";
  if (!tk && old) {{
    t = legacyTable(p);
    LEGACY = true;
    w = "xp.properties still has the 0.4.7 lines mana.magicBase / mana.magicClasses (their move to Base Mana by class did not happen - see the start log) - read as Base Mana by class: " + (((String) t[2]).length() > 0 ? (String) t[2] : "no class") + ". Set the table in Server Setup > Skills > Overall and Mana, or restart to retry the move.";
  }} else {{
    t = parseTable(p);
    LEGACY = false;
    if (((String) t[3]).length() > 0) w = "Base Mana by class: " + (String) t[3];
    if (tk && old) w = (w.length() > 0 ? w + "; " : "") + "mana.magicBase / mana.magicClasses in xp.properties are no longer used (0.4.8 reads Base Mana by class, mana.classBase.<Class>=<Mana>) - delete those lines";
  }}
  TBL = new Object[] {{ t[0], t[1], t[2] }};
  if (w.length() > 0 && !w.equals(WARNED)) {PKG}.SkillCfg.warn(w);
  WARNED = w;
  GUARD_DIRTY = true;
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
  String tt = tableText();
  String b = MANA_ON ? "base mana " + {PKG}.DivCfg.num(BASE) + ", class Mana table " + (tt.length() > 0 ? tt : "empty") + (LEGACY ? " (from the 0.4.7 lines)" : "") : "base mana off";
  return o + ", " + b;
}}""", ovc))

# ================= 0.4.14 config readers (before SkillCfg.load, which calls them): AcroCfg.ROLL, MobXp, GatherPace, Sickle =================
# acro.rollBonus (Skyy 2026-10-02: "if you crouch as you land you take less fall damage ... make that roll give extra acrobatic xp too")
acfg.addField(CtField.make("public static volatile double ROLL = 0.5;", acfg))
acfg.addMethod(CtNewMethod.make(J14(r"""
public static void readRoll(java.util.Properties p) {
  ROLL = clampD(@PKG@.SkillCfg.dbl(p, "acro.rollBonus", 0.5), 0.0, 10.0);
}"""), acfg))
acfg.addMethod(CtNewMethod.make(J14(r"""
public static String rollText() {
  if (!ENABLED) return "off (acro.enabled=false)";
  if (!(ROLL > 0.0)) return "off (rolls pay as before)";
  return "+" + @PKG@.DivCfg.num(ROLL * 100.0) + "% Acrobatics XP for a rolled landing";
}"""), acfg))
# MobXp (Skyy 2026-10-02 KILL XP = "level bonus + gap rule max +250%"): combat.levelXp.enabled / combat.levelBonus / combat.gap.*
for _d in ("public static volatile boolean ON = true;", "public static volatile double BONUS = 0.05;", "public static volatile int FREE = 5;",
           "public static volatile double ABOVE = 0.05;", "public static volatile double MAX = 3.5;", "public static volatile double BELOW = 0.05;",
           "public static volatile double MIN = 0.1;", "public static boolean FAILED_ONCE = false;"):
    mxp.addField(CtField.make(_d, mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "combat.levelXp.enabled", true);
  BONUS = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.levelBonus", 0.05), 0.0, 10.0);
  FREE = (int) @PKG@.AcroCfg.clampD((double) @PKG@.SkillCfg.lng(p, "combat.gap.free", 5L), 0.0, 100.0);
  ABOVE = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.gap.above", 0.05), 0.0, 10.0);
  MAX = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.gap.max", 3.5), 1.0, 100.0);
  BELOW = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.gap.below", 0.05), 0.0, 10.0);
  MIN = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "combat.gap.min", 0.1), 0.0, 1.0);
}"""), mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  if (!ON) return "off";
  return "on (+" + @PKG@.DivCfg.num(BONUS * 100.0) + "% a mob level; more than " + FREE + " levels above your class skill +" + @PKG@.DivCfg.num(ABOVE * 100.0) + "% a level up to x" + @PKG@.DivCfg.num(MAX) + ", below -" + @PKG@.DivCfg.num(BELOW * 100.0) + "% a level down to x" + @PKG@.DivCfg.num(MIN) + "; SkyyMobs levels)";
}"""), mxp))
# GatherPace (Skyy 2026-10-02 tool levels answer (4): "Bigger boost for all 3") - gather.boost.*; SLOTS indexed by storage slot
gpc.addField(CtField.make('public static final String DEFAULT_SKILLS = "Mining,Foraging,Farming";', gpc))
# fix round F4: early / late are never below this (0 = a skill that can never earn XP from gathering; the rows' min is the same)
gpc.addField(CtField.make("public static final double MIN_MULT = 0.1;", gpc))
for _d in ("public static volatile boolean[] SLOTS = new boolean[] { true, true, true };", 'public static volatile String TEXT = "Mining,Foraging,Farming";',
           "public static volatile double EARLY = 3.0;", "public static volatile int UNTIL = 10;", "public static volatile double LATE = 1.5;",
           "public static volatile int FROM = 20;"):
    gpc.addField(CtField.make(_d, gpc))
# a gathering skill name -> its slot (Mining / Foraging / Farming), -1 = blank, -2 = anything else
gpc.addMethod(CtNewMethod.make(J14(r"""
public static int slotOf(String t) {
  if (t == null) return -1;
  String x = t.trim();
  if (x.length() == 0) return -1;
  for (int s = 0; s <= @PKG@.SkillDefs.FARMING; s++) if (@PKG@.SkillDefs.NAMES[s].equalsIgnoreCase(x) || @PKG@.SkillDefs.LABELS[s].equalsIgnoreCase(x)) return s;
  return -2;
}"""), gpc))
gpc.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  String v = p.getProperty("gather.boost.skills", DEFAULT_SKILLS);
  boolean[] on = new boolean[@PKG@.SkillDefs.N];
  StringBuilder sb = new StringBuilder();
  String[] ps = (v == null ? "" : v).split(",");
  for (int i = 0; i < ps.length; i++) {
    int s = slotOf(ps[i]);
    if (s == -1) continue;
    if (s < 0) { @PKG@.SkillCfg.warn("gather.boost.skills: '" + ps[i].trim() + "' is not Mining, Foraging or Farming - ignored"); continue; }
    if (on[s]) continue;
    on[s] = true;
    if (sb.length() > 0) sb.append(',');
    sb.append(@PKG@.SkillDefs.LABELS[s]);
  }
  SLOTS = on;
  TEXT = sb.toString();
  EARLY = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "gather.boost.early", 3.0), MIN_MULT, 100.0);
  UNTIL = (int) @PKG@.AcroCfg.clampD((double) @PKG@.SkillCfg.lng(p, "gather.boost.earlyUntil", 10L), 0.0, 100.0);
  LATE = @PKG@.AcroCfg.clampD(@PKG@.SkillCfg.dbl(p, "gather.boost.late", 1.5), MIN_MULT, 100.0);
  FROM = (int) @PKG@.AcroCfg.clampD((double) @PKG@.SkillCfg.lng(p, "gather.boost.lateFrom", 20L), 0.0, 100.0);
}"""), gpc))
gpc.addMethod(CtNewMethod.make(J14(r"""
public static boolean on(int slot) {
  boolean[] s = SLOTS;
  return slot >= 0 && slot < s.length && s[slot];
}"""), gpc))
# the multiplier at a level: EARLY through UNTIL, LATE from FROM, a straight line between
gpc.addMethod(CtNewMethod.make(J14(r"""
public static double mult(int lv) {
  if (lv <= UNTIL) return EARLY;
  if (lv >= FROM) return LATE;
  return EARLY + (LATE - EARLY) * (double) (lv - UNTIL) / (double) (FROM - UNTIL);
}"""), gpc))
gpc.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  if (TEXT.length() == 0) return "off (no skill listed)";
  return "x" + @PKG@.DivCfg.num(EARLY) + " to level " + UNTIL + ", x" + @PKG@.DivCfg.num(LATE) + " from level " + FROM + " (" + TEXT + ")";
}"""), gpc))
gpc.addMethod(CtNewMethod.make(J14(r"""
public static String checkSkills(String key, String v) {
  if (v == null) return null;
  String[] ps = v.split(",");
  for (int i = 0; i < ps.length; i++) {
    if (slotOf(ps[i]) == -2) return "Only Mining, Foraging and Farming have a gathering pace (" + ps[i].trim() + " is not one).";
  }
  return null;
}"""), gpc))
# Sickle (research/Tool-Levels-Spec.md question 3): farming.sickle.*; the per-player contexts (BRK: an F pickup's BreakBlockEvent, USE: an
# F-harvest, PEND: this tick's pickups) are pruned by Acro.retainOnline; KEYS (produce item -> {Long xp, Boolean multi, String family}) is
# built on first use on a world thread and dropped by every load (the rules may have changed)
skl.addField(CtField.make('public static final String DEFAULT_ITEMS = "Tool_Sickle_";', skl))
for _d in ("public static volatile boolean ON = true;", 'public static volatile String[] ITEMS = new String[] { "Tool_Sickle_" };',
           'public static volatile String ITEMS_TEXT = "Tool_Sickle_";', "public static volatile java.util.HashMap KEYS = null;",
           "public static final java.util.concurrent.ConcurrentHashMap BRK = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap USE = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile boolean SEEN = false;", "public static boolean FAILED_ONCE = false;",
           "public static final long BREAK_NS = 250000000L;", "public static final long WINDOW_MS = 2000L;"):
    skl.addField(CtField.make(_d, skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static String[] parse(String v) {
  java.util.ArrayList l = new java.util.ArrayList();
  String[] ps = (v == null ? "" : v).split(",");
  for (int i = 0; i < ps.length; i++) {
    String t = ps[i].trim();
    if (t.length() > 0 && !l.contains(t)) l.add(t);
  }
  return (String[]) l.toArray(new String[0]);
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static void read(java.util.Properties p) {
  ON = @PKG@.SkillCfg.bool(p, "farming.sickle.enabled", true);
  String[] it = parse(p.getProperty("farming.sickle.items", DEFAULT_ITEMS));
  if (it.length == 0) { @PKG@.SkillCfg.warn("farming.sickle.items is empty - using " + DEFAULT_ITEMS); it = new String[] { DEFAULT_ITEMS }; }
  ITEMS = it;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < it.length; i++) { if (i > 0) sb.append(','); sb.append(it[i]); }
  ITEMS_TEXT = sb.toString();
  KEYS = null;
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static String text() {
  return ON ? "on (" + ITEMS_TEXT + ", one award per crop)" : "off";
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static String checkItems(String key, String v) {
  if (v == null) return null;
  if (parse(v).length == 0) return "Write at least one item id start, like Tool_Sickle_.";
  return null;
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static void retain(java.util.Set online) {
  BRK.keySet().retainAll(online);
  USE.keySet().retainAll(online);
  PEND.keySet().retainAll(online);
}"""), skl))
# ================= ClassMana part 1 (0.4.15, research/SkyyArmory-Spec.md 15.4): the mana.classPerLevel table (before SkillCfg.load) =================
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

# ================= BridgeCfg (0.4): bridge.* keys (skill:fn:addxp / skill:fn:craftxp) =================
bgc.addField(CtField.make("public static final String DEFAULTS = " + BRIDGE_LIT + ";", bgc))
bgc.addField(CtField.make('public static final String DEFAULT_SKILLS = "%s";' % BRIDGE_SKILLS, bgc))
bgc.addField(CtField.make('public static final String DEFAULT_BONUS_XP = "%s";' % BONUS_XP_SKILLS, bgc))
bgc.addField(CtField.make('public static final String DEFAULT_BONUS_ADDXP = "%s";' % BONUS_ADDXP_SKILLS, bgc))
for _decl in ("boolean[] GRANT = new boolean[0]", 'String GRANT_TEXT = ""', "long PER_CALL = 500000L", "long PER_MIN = 3000000L",
              "boolean BONUS = true", "boolean[] BONUS_XP = new boolean[0]", 'String BONUS_TEXT = ""',
              "boolean[] BONUS_ADDXP = new boolean[0]", 'String BONUS_ADDXP_TEXT = ""'):
    bgc.addField(CtField.make("public static volatile %s;" % _decl, bgc))
bgc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  boolean[] g = new boolean[{PKG}.SkillDefs.N];
  StringBuilder sb = new StringBuilder();
  String[] ps = p.getProperty("bridge.addxp.skills", DEFAULT_SKILLS).split(",");
  for (int i = 0; i < ps.length; i++) {{
    String t = ps[i].trim();
    if (t.length() == 0) continue;
    int hit = -1;
    for (int s = 0; s < {PKG}.SkillDefs.N; s++) if ({PKG}.SkillDefs.NAMES[s].equalsIgnoreCase(t) || {PKG}.SkillDefs.LABELS[s].equalsIgnoreCase(t)) hit = s;
    if (hit < 0 || hit == {PKG}.SkillDefs.COMBAT) {{ {PKG}.SkillCfg.warn("bridge.addxp.skills: unknown or not grantable skill '" + t + "' - ignored"); continue; }}
    if (hit == {PKG}.SkillDefs.EXPLORATION) continue;
    g[hit] = true;
    if (sb.length() > 0) sb.append(',');
    sb.append({PKG}.SkillDefs.LABELS[hit]);
  }}
  g[{PKG}.SkillDefs.EXPLORATION] = {PKG}.ExplCfg.ENABLED;
  if ({PKG}.ExplCfg.ENABLED) {{
    if (sb.length() > 0) sb.append(',');
    sb.append({PKG}.SkillDefs.LABELS[{PKG}.SkillDefs.EXPLORATION]);
  }}
  GRANT = g;
  GRANT_TEXT = sb.toString();
  long c = {PKG}.SkillCfg.lng(p, "bridge.maxXpPerCall", 500000L);
  PER_CALL = c < 1L ? 1L : c;
  long m = {PKG}.SkillCfg.lng(p, "bridge.maxXpPerMinute", 3000000L);
  PER_MIN = m < 0L ? 0L : m;
  BONUS = {PKG}.SkillCfg.bool(p, "bridge.bonus.enabled", true);
  boolean named = false;
  boolean[] bx = new boolean[{PKG}.SkillDefs.N];
  StringBuilder bsb = new StringBuilder();
  String[] bps = p.getProperty("bridge.bonus.xpSkills", DEFAULT_BONUS_XP).split(",");
  for (int j = 0; j < bps.length; j++) {{
    String bt = bps[j].trim();
    if (bt.length() == 0) continue;
    int bh = -1;
    for (int s = 0; s < {PKG}.SkillDefs.N; s++) if ({PKG}.SkillDefs.NAMES[s].equalsIgnoreCase(bt) || {PKG}.SkillDefs.LABELS[s].equalsIgnoreCase(bt)) bh = s;
    if (bh < 0 || bh == {PKG}.SkillDefs.COMBAT) {{ {PKG}.SkillCfg.warn("bridge.bonus.xpSkills: unknown skill '" + bt + "' - ignored"); continue; }}
    if (bh == {PKG}.SkillDefs.EXPLORATION) {{ named = true; continue; }}
    bx[bh] = true;
    if (bsb.length() > 0) bsb.append(',');
    bsb.append({PKG}.SkillDefs.LABELS[bh]);
  }}
  bx[{PKG}.SkillDefs.EXPLORATION] = false;
  BONUS_XP = bx;
  BONUS_TEXT = bsb.toString();
  boolean[] gx = new boolean[{PKG}.SkillDefs.N];
  StringBuilder gsb = new StringBuilder();
  String[] gps = p.getProperty("bridge.bonus.addxpSkills", DEFAULT_BONUS_ADDXP).split(",");
  for (int k = 0; k < gps.length; k++) {{
    String gt = gps[k].trim();
    if (gt.length() == 0) continue;
    int gh = -1;
    for (int s = 0; s < {PKG}.SkillDefs.N; s++) if ({PKG}.SkillDefs.NAMES[s].equalsIgnoreCase(gt) || {PKG}.SkillDefs.LABELS[s].equalsIgnoreCase(gt)) gh = s;
    if (gh < 0 || gh == {PKG}.SkillDefs.COMBAT) {{ {PKG}.SkillCfg.warn("bridge.bonus.addxpSkills: unknown skill '" + gt + "' - ignored"); continue; }}
    if (gh == {PKG}.SkillDefs.EXPLORATION) {{ named = true; continue; }}
    if (!bx[gh]) {PKG}.SkillCfg.warn("bridge.bonus.addxpSkills: " + {PKG}.SkillDefs.LABELS[gh] + " is not in bridge.bonus.xpSkills, so it gets no tree XP bonus anyway");
    gx[gh] = true;
    if (gsb.length() > 0) gsb.append(',');
    gsb.append({PKG}.SkillDefs.LABELS[gh]);
  }}
  gx[{PKG}.SkillDefs.EXPLORATION] = false;
  if (named) {PKG}.SkillCfg.warn("bridge.bonus.xpSkills / bridge.bonus.addxpSkills: Exploration never gets XP bonuses (Skyy) - ignored");
  BONUS_ADDXP = gx;
  BONUS_ADDXP_TEXT = gsb.toString();
}}""", bgc))
bgc.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    if (String.valueOf(en.nextElement()).startsWith("bridge.")) return;
  }}
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the cross-mod XP section (bridge.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the bridge.* section to xp.properties: " + t); }}
}}""", bgc))
# 0.3: the 0.1/0.2 default levels= line (50 levels) -> the 100-level table, in memory AND in the file (custom tables are kept)
cfg.addField(CtField.make('public static final String OLD_LEVELS = "%s";' % ",".join(str(x) for x in LEVELS_OLD50), cfg))
cfg.addField(CtField.make('public static final String NEW_LEVELS = "%s";' % ",".join(str(x) for x in LEVELS), cfg))
cfg.addMethod(CtNewMethod.make("""
public static String squash(String v) {
  if (v == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < v.length(); i++) { char c = v.charAt(i); if (c != ' ' && c != '\\t') sb.append(c); }
  return sb.toString();
}""", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static void upgradeLevels(java.util.Properties p) {{
  if (!OLD_LEVELS.equals(squash(p.getProperty("levels")))) return;
  java.util.Enumeration pe = p.propertyNames();
  while (pe.hasMoreElements()) {{
    if (String.valueOf(pe.nextElement()).startsWith("perk.")) return;
  }}
  p.setProperty("levels", NEW_LEVELS);
  try {{
    java.util.List lines = java.nio.file.Files.readAllLines(FILE, java.nio.charset.StandardCharsets.UTF_8);
    StringBuilder sb = new StringBuilder();
    boolean done = false;
    for (int i = 0; i < lines.size(); i++) {{
      String ln = (String) lines.get(i);
      String t = ln.trim();
      if (!done && t.startsWith("levels=") && OLD_LEVELS.equals(squash(t.substring(7)))) {{
        sb.append("# SkyySkills 0.3: max level 100 - the old 50-level default table was extended (levels 1-50 unchanged)\\n");
        sb.append("levels=").append(NEW_LEVELS).append("\\n");
        done = true;
      }} else {{
        sb.append(ln).append("\\n");
      }}
    }}
    if (!done) return;
    java.nio.file.Path tmp = FILE.resolveSibling("xp.properties.tmp");
    java.nio.file.Files.write(tmp, sb.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
    info("xp.properties: levels= upgraded from the old 50-level default to the 100-level table (levels 1-50 unchanged)");
  }} catch (Throwable t) {{ warn("could not rewrite the levels= line of xp.properties (the 100-level table is used anyway): " + t); }}
}}""", cfg))
# 0.4 (Skyy's fall rule): an xp.properties written by 0.2 / 0.3 carries the old fall lines (safe drops paid per block, 2 XP per damage
# point, 50 per landing, falls inside the 240/min cap). Rewritten ONCE (marker: acro.fallMaxXpPerMinute missing while acro.* keys exist):
# the old comments -> the new ones, acro.fallMinBlocks / acro.fallXpPerBlock removed (a custom value leaves a comment line), the DEFAULT
# acro.fallDamageXp=2 / acro.fallXpMax=50 -> the 0.4 defaults (custom values are kept), acro.fallMaxXpPerMinute added after
# acro.fallXpMax. The loaded Properties get the same changes, so this load already uses them.
acfg.addField(CtField.make("public static final String[] FALL_OLD = new String[] { %s };" % ", ".join(json.dumps(x) for x in ACRO_FALL_OLD), acfg))
acfg.addField(CtField.make("public static final String[] FALL_NEW = new String[] { %s };" % ", ".join(json.dumps(x) for x in ACRO_FALL_NEW), acfg))
acfg.addField(CtField.make("public static final String CAP_OLD = %s;" % json.dumps(ACRO_CAP_OLD), acfg))
acfg.addField(CtField.make("public static final String CAP_NEW = %s;" % json.dumps(ACRO_CAP_NEW), acfg))
acfg.addMethod(CtNewMethod.make(f"""
public static void migrateFall(java.util.Properties p) {{
  if (p.getProperty("acro.fallMaxXpPerMinute") != null) return;
  boolean any = false;
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    if (String.valueOf(en.nextElement()).startsWith("acro.")) any = true;
  }}
  if (!any) return;
  boolean hadPer = p.getProperty("acro.fallXpPerBlock") != null;
  p.remove("acro.fallXpPerBlock");
  p.remove("acro.fallMinBlocks");
  if ("2".equals({PKG}.SkillCfg.squash(p.getProperty("acro.fallDamageXp")))) p.setProperty("acro.fallDamageXp", "{FALL_DMG_DEF}");
  if ("50".equals({PKG}.SkillCfg.squash(p.getProperty("acro.fallXpMax")))) p.setProperty("acro.fallXpMax", "{FALL_MAX_DEF}");
  p.setProperty("acro.fallMaxXpPerMinute", "{FALL_PM_DEF}");
  try {{
    java.util.List lines = java.nio.file.Files.readAllLines({PKG}.SkillCfg.FILE, java.nio.charset.StandardCharsets.UTF_8);
    StringBuilder sb = new StringBuilder();
    boolean wroteNew = false;
    boolean perMin = false;
    for (int i = 0; i < lines.size(); i++) {{
      String ln = (String) lines.get(i);
      String t = ln.trim();
      String q = {PKG}.SkillCfg.squash(t);
      boolean oldComment = false;
      for (int k = 0; k < FALL_OLD.length; k++) if (t.equals(FALL_OLD[k])) oldComment = true;
      if (oldComment) {{
        if (!wroteNew) {{
          for (int k = 0; k < FALL_NEW.length; k++) sb.append(FALL_NEW[k]).append("\\n");
          wroteNew = true;
        }}
        continue;
      }}
      if (q.startsWith("acro.fallMinBlocks=") || q.startsWith("acro.fallXpPerBlock=")) {{
        if (!q.equals("acro.fallMinBlocks=4") && !q.equals("acro.fallXpPerBlock=2")) sb.append("# SkyySkills 0.4 removed: ").append(t).append(" (safe drops pay no Acrobatics XP any more)\\n");
        continue;
      }}
      if (q.equals("acro.fallDamageXp=2")) {{ sb.append("acro.fallDamageXp={FALL_DMG_DEF}\\n"); continue; }}
      if (q.startsWith("acro.fallXpMax=")) {{
        if (q.equals("acro.fallXpMax=50")) sb.append("acro.fallXpMax={FALL_MAX_DEF}\\n"); else sb.append(ln).append("\\n");
        if (!perMin) {{ sb.append("acro.fallMaxXpPerMinute={FALL_PM_DEF}\\n"); perMin = true; }}
        continue;
      }}
      if (t.equals(CAP_OLD)) {{ sb.append(CAP_NEW).append("\\n"); continue; }}
      sb.append(ln).append("\\n");
    }}
    if (!perMin) {{
      sb.append("# SkyySkills 0.4: all fall XP together pays at most this much in any 60 seconds (its own cap, outside acro.maxXpPerMinute)\\n");
      sb.append("acro.fallMaxXpPerMinute={FALL_PM_DEF}\\n");
    }}
    java.nio.file.Path tmp = {PKG}.SkillCfg.FILE.resolveSibling("xp.properties.tmp");
    java.nio.file.Files.write(tmp, sb.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, {PKG}.SkillCfg.FILE, new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
    {PKG}.SkillCfg.info("xp.properties: Acrobatics falls moved to the 0.4 rules - only survived falls that hurt pay (acro.fallDamageXp=" + p.getProperty("acro.fallDamageXp") + ", acro.fallXpMax=" + p.getProperty("acro.fallXpMax") + ", acro.fallMaxXpPerMinute=" + p.getProperty("acro.fallMaxXpPerMinute") + ")" + (hadPer ? "; acro.fallXpPerBlock removed" : ""));
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not rewrite the Acrobatics fall lines of xp.properties (the 0.4 fall rules apply anyway): " + t); }}
}}""", acfg))
# 0.4.10 (tools/skills_0_4_10_patch.py point 1): append the class skill XP block once to a file without classSkill.xpMultiplier (the
# DivCfg.ensureSelf pattern; this load reads the code default 3.0 for the missing key, the next load reads the appended line)
cfg.addMethod(CtNewMethod.make(f"""
public static void ensureClass(java.util.Properties p) {{
  if (p.getProperty("classSkill.xpMultiplier") != null) return;
  try {{
    java.nio.file.Files.write(FILE, ("\\n" + CLASS_DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    info("xp.properties: appended the class skill XP section (classSkill.xpMultiplier={CLS_MULT_DEF})");
  }} catch (Throwable t) {{ warn("could not append the class skill XP section to xp.properties: " + t); }}
}}""", cfg))
# 0.4.12: append a block once at the end of xp.properties in the file's OWN line ending (CRLF when the file has CRLF; ensureClass and the
# older blocks always wrote LF), after one blank line; ISO-8859-1 in and out (the blocks are ASCII). Nothing before it changes.
cfg.addMethod(CtNewMethod.make(f"""
public static void appendBlock(String key, String block, String what) {{
  try {{
    byte[] old = java.nio.file.Files.readAllBytes(FILE);
    String t = new String(old, "ISO-8859-1");
    boolean crlf = t.indexOf("\\r\\n") >= 0;
    String nl = crlf ? "\\r\\n" : "\\n";
    String b = crlf ? block.replace("\\n", "\\r\\n") : block;
    String pre = (t.length() == 0 || t.endsWith("\\n")) ? nl : nl + nl;
    java.nio.file.Files.write(FILE, (pre + b).getBytes("ISO-8859-1"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    info("xp.properties: appended the " + what + " section (" + key + ")");
  }} catch (Throwable t) {{ warn("could not append the " + what + " section to xp.properties: " + t); }}
}}""", cfg))
# 0.4.12: the class skill levels block once to a file without levels.class (this load reads the code default class table for the missing
# key, the next load reads the appended line); a file that already holds levels.class.sameAsOthers (an admin's line) gets only the list
cfg.addMethod(CtNewMethod.make(f"""
public static void ensureCurve(java.util.Properties p) {{
  if (p.getProperty("levels.class") != null) return;
  String b = CURVE_DEFAULTS;
  if (p.getProperty("levels.class.sameAsOthers") != null) b = b.replace("\\nlevels.class.sameAsOthers=false\\n", "\\n");
  appendBlock("levels.class", b, "class skill levels");
}}""", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static void ensureManaRegen(java.util.Properties p) {{
  if (p.getProperty("mana.regen.inCombat") != null) return;
  appendBlock("mana.regen.inCombat", MREG_DEFAULTS, "Mana regen in combat");
}}""", cfg))
# 0.4.14: the kill XP / roll / gathering pace / sickle block, appended once: its comment lines + only the key lines the file does not have yet
# (an admin's line is never duplicated or rewritten; nothing to add = nothing written), in the file's own line ending (appendBlock)
cfg.addField(CtField.make("public static final String N14_DEFAULTS = " + N14_LIT + ";", cfg))
cfg.addMethod(CtNewMethod.make(J14(r"""
public static String block14(java.util.Properties p) {
  String[] ls = N14_DEFAULTS.split("\n");
  StringBuilder sb = new StringBuilder();
  boolean any = false;
  for (int i = 0; i < ls.length; i++) {
    String ln = ls[i];
    if (ln.length() == 0) continue;
    if (ln.startsWith("#")) { sb.append(ln).append("\n"); continue; }
    int eq = ln.indexOf('=');
    String k = eq > 0 ? ln.substring(0, eq) : ln;
    if (p != null && p.getProperty(k) != null) continue;
    any = true;
    sb.append(ln).append("\n");
  }
  return any ? sb.toString() : null;
}"""), cfg))
cfg.addMethod(CtNewMethod.make(J14(r"""
public static void ensure14(java.util.Properties p) {
  String b = block14(p);
  if (b == null) return;
  appendBlock("combat.levelXp.enabled, acro.rollBonus, gather.boost.*, farming.sickle.*", b, "kill XP by mob level / roll landings / gathering pace / sickle swings");
}"""), cfg))
# "own table, max level 100" / "on the other skills' table (levels.class.sameAsOthers)" (load text, ready line)
cfg.addMethod(CtNewMethod.make(f"""
public static String curveText() {{
  if ({PKG}.SkillDefs.SAME) return "on the other skills' table (levels.class.sameAsOthers)";
  return "own table, max level " + {PKG}.SkillDefs.CMAX;
}}""", cfg))
# 0.4.10 point 2: THE class skill XP multiplier - every XP gain into a class skill goes through here (KillSys for kills and so the party
# share, BridgeXp.paid for grants; 0.4.11: NOT Priest heal XP - HealXp.offer -> BridgeXp.offerX(..., cls false)). xp x CLASS_MULT for a class slot, the fraction paid by chance (PartyXp.amount rule; a product
# within 1e-9 of a whole number counts as that number, so 1.1 x 10 is 11, never 12); any other slot, or xp <= 0, unchanged / 0.
cfg.addMethod(CtNewMethod.make(f"""
public static long classXp(int slot, long xp) {{
  if (xp <= 0L) return 0L;
  if (!{PKG}.SkillDefs.isClass(slot)) return xp;
  double m = CLASS_MULT;
  if (m == 1.0) return xp;
  if (!(m > 0.0)) return 0L;
  double x = (double) xp * m;
  if (x >= 9.0E15) return 9000000000000000L;
  double r = Math.rint(x);
  if (Math.abs(x - r) < 1.0E-9) x = r;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}}""", cfg))
# "x3" / "x2.5" / "x0" (load text, ready line)
cfg.addMethod(CtNewMethod.make(f"""
public static String classText() {{
  return "x" + {PKG}.DivCfg.num(CLASS_MULT);
}}""", cfg))
# the Stats page's class how-to line ends with this: "" at x1, ". Class skill XP x3 on this server", ". Class skill XP is off on this server"
cfg.addMethod(CtNewMethod.make(f"""
public static String classHow() {{
  double m = CLASS_MULT;
  if (m == 1.0) return "";
  if (!(m > 0.0)) return ". Class skill XP is off on this server";
  return ". Class skill XP x" + {PKG}.DivCfg.num(m) + " on this server";
}}""", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static synchronized String load() {{
  int bad = 0;
  try {{
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {{
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Files.write(FILE, DEFAULTS.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    }}
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try {{ p.load(in); }} finally {{ in.close(); }}
    upgradeLevels(p);
    {PKG}.AcroCfg.migrateFall(p);
    {PKG}.AcroCfg.ensureDefaults(p);
    {PKG}.PerkCfg.ensureDefaults(p);
    {PKG}.AlchCfg.ensureDefaults(p);
    {PKG}.SmithCfg.ensureDefaults(p);
    {PKG}.BridgeCfg.ensureDefaults(p);
    {PKG}.ExplCfg.ensureDefaults(p);
    {PKG}.FellCfg.ensureDefaults(p);
    {PKG}.AcroCfg.ensureDj(p);
    {PKG}.PartyCfg.ensureDefaults(p);
    {PKG}.DivCfg.ensureDefaults(p);
    {PKG}.XbowCfg.ensureDefaults(p);
    {PKG}.DivCfg.ensureSelf(p);
    {PKG}.XbowCfg.ensureExtras(p);
    {PKG}.OverallCfg.ensureDefaults(p);
    ensureClass(p);
    ensureCurve(p);       // 0.4.12: the class skill levels block, once
    ensureManaRegen(p);   // 0.4.12: the Mana regen in combat block, once
    ensure14(p);          // 0.4.14: the kill XP / roll / gathering pace / sickle block, once (only the keys the file lacks)
    {PKG}.SkillDefs.setTable({PKG}.SkillDefs.DEFAULT_PER);
    java.util.HashMap ex = new java.util.HashMap();
    java.util.ArrayList pf = new java.util.ArrayList();
    java.util.ArrayList sf = new java.util.ArrayList();
    java.util.HashMap ro = new java.util.HashMap();
    java.util.Enumeration en = p.propertyNames();
    while (en.hasMoreElements()) {{
      String k = ((String) en.nextElement()).trim();
      String v = p.getProperty(k);
      if (k.startsWith("combat.role.")) {{
        try {{ ro.put(k.substring(12), Long.valueOf(Long.parseLong(v.trim()))); }} catch (Throwable t) {{ bad++; }}
        continue;
      }}
      int kind = k.startsWith("block.") ? 0 : (k.startsWith("prefix.") ? 1 : (k.startsWith("suffix.") ? 2 : -1));
      if (kind < 0) continue;
      String id = k.substring(kind == 0 ? 6 : 7);
      if (id.length() == 0) {{ bad++; continue; }}
      if (explRule(v)) {{ warn("rule " + k + "=" + v + " ignored - Exploration XP only comes from other mods (skill:fn:addxp, SkyyExploration), never from blocks"); continue; }}
      long[] r = parseRule(v);
      if (r == null) {{ bad++; warn("bad rule " + k + "=" + v + " (want <Skill>:<xp> or none)"); continue; }}
      if (kind == 0) ex.put(id, r);
      else if (kind == 1) pf.add(new Object[] {{ id, r }});
      else sf.add(new Object[] {{ id, r }});
    }}
    MULT = dbl(p, "multiplier", 1.0);
    if (MULT < 0.0) MULT = 0.0;
    COINS_PER_LEVEL = lng(p, "coinsPerLevel", 100L);
    FEEDBACK = bool(p, "feedback", true);
    FEEDBACK_MS = lng(p, "feedbackMs", 2000L);
    if (FEEDBACK_MS < 500L) FEEDBACK_MS = 500L;
    CREATIVE = bool(p, "creativeXp", false);
    IGNORE_PLACED = bool(p, "ignorePlaced", true);
    NEED_RIPE = bool(p, "farmingNeedsRipe", true);
    HARVEST_GATE_MS = lng(p, "harvestCooldownMs", 5000L);
    if (HARVEST_GATE_MS < 3000L) HARVEST_GATE_MS = 3000L;
    C_PER_HP = dbl(p, "combat.perHealth", 0.2);
    C_MIN = lng(p, "combat.min", 1L);
    C_MAX = lng(p, "combat.max", 500L);
    C_DEFAULT = lng(p, "combat.default", 5L);
    double cm = dbl(p, "classSkill.xpMultiplier", {CLS_MULT_DEF});
    CLASS_MULT = (Double.isNaN(cm) || cm < 0.0) ? 0.0 : (cm > 100.0 ? 100.0 : cm);
    {PKG}.AcroCfg.read(p);
    {PKG}.PerkCfg.read(p);
    {PKG}.AlchCfg.read(p);
    {PKG}.SmithCfg.read(p);
    {PKG}.ExplCfg.read(p);
    {PKG}.FellCfg.read(p);
    {PKG}.AcroCfg.readDj(p);
    {PKG}.PartyCfg.read(p);
    {PKG}.DivCfg.read(p);
    {PKG}.BridgeCfg.read(p);
    {PKG}.XbowCfg.read(p);
    {PKG}.OverallCfg.read(p);
    String lv = p.getProperty("levels");
    if (lv != null && lv.trim().length() > 0) {{
      String[] parts = lv.split(",");
      long[] per = new long[parts.length];
      boolean ok = parts.length >= 1 && parts.length <= 100;
      for (int i = 0; i < parts.length && ok; i++) {{
        try {{ per[i] = Long.parseLong(parts[i].trim()); if (per[i] <= 0L) ok = false; }} catch (Throwable t) {{ ok = false; }}
      }}
      if (ok) {PKG}.SkillDefs.setTable(per); else {{ bad++; warn("bad levels= line, using the default table"); }}
    }}
    // 0.4.12: the class skill table (levels.class, the levels= rules: 1-100 numbers above 0, else the default class table) and
    // levels.class.sameAsOthers; setClassTable rebuilds the effective class table against the general one loaded just above
    long[] cper = {PKG}.SkillDefs.DEFAULT_CPER;
    String lc = p.getProperty("levels.class");
    if (lc != null && lc.trim().length() > 0) {{
      String[] cps = lc.split(",");
      long[] cp = new long[cps.length];
      boolean cok = cps.length >= 1 && cps.length <= 100;
      for (int i = 0; i < cps.length && cok; i++) {{
        try {{ cp[i] = Long.parseLong(cps[i].trim()); if (cp[i] <= 0L) cok = false; }} catch (Throwable t) {{ cok = false; }}
      }}
      if (cok) cper = cp; else {{ bad++; warn("bad levels.class= line, using the default class skill table"); }}
    }}
    {PKG}.SkillDefs.setClassTable(cper, bool(p, "levels.class.sameAsOthers", false));
    // 0.4.12: mana.regen.inCombat, clamped to the row bounds 0-100 (a bad number = the default)
    long mrc = lng(p, "mana.regen.inCombat", {MREG_DEF}L);
    {PKG}.ManaRegen.IN_COMBAT = (int) (mrc < 0L ? 0L : (mrc > 100L ? 100L : mrc));
    {PKG}.MobXp.read(p);        // 0.4.14: kill XP by mob level
    {PKG}.AcroCfg.readRoll(p);  // 0.4.14: roll landings
    {PKG}.GatherPace.read(p);   // 0.4.14: the gathering pace
    {PKG}.Sickle.read(p);       // 0.4.14: sickle swings
    {PKG}.ClassMana.read(p);    // 0.4.15: max Mana per class level (the mana.classPerLevel table)
    EXACT = ex; PFX = pf; SFX = sf; ROLE = ro;
    CACHE.clear();
    {PKG}.SmithCfg.CACHE.clear();
    return ex.size() + " exact, " + pf.size() + " prefix, " + sf.size() + " suffix, " + ro.size() + " role rule(s), class skill XP " + classText() + ", acrobatics " + ({PKG}.AcroCfg.ENABLED ? "on" : "off") + ", perks " + ({PKG}.PerkCfg.ENABLED ? "on" : "off") + ", alchemy " + ({PKG}.AlchCfg.ENABLED ? "on" : "off") + ", smithing " + ({PKG}.SmithCfg.ENABLED ? ({PKG}.SmithCfg.VANILLA ? "on" : "on (Furnace tab only)") : "off") + ", exploration " + ({PKG}.ExplCfg.ENABLED ? "on (no boosters)" : "off") + ", felled trees " + {PKG}.FellCfg.text() + ", double jump " + {PKG}.AcroCfg.djText() + ", party combat XP " + {PKG}.PartyCfg.text() + ", divinity heal XP " + {PKG}.DivCfg.text() + ", crossbows stay loaded " + {PKG}.XbowCfg.text() + ", overall level " + {PKG}.OverallCfg.text() + ", bridge skills " + {PKG}.BridgeCfg.GRANT_TEXT + ", max level " + {PKG}.SkillDefs.MAX + ", class skills " + curveText() + ", in-combat Mana regen " + {PKG}.ManaRegen.IN_COMBAT + "%" + ", kill XP by mob level " + {PKG}.MobXp.text() + ", roll landings " + {PKG}.AcroCfg.rollText() + ", gathering pace " + {PKG}.GatherPace.text() + ", sickle swings " + {PKG}.Sickle.text() + ", max Mana per class level " + {PKG}.ClassMana.text() + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");
  }} catch (Throwable t) {{
    warn("could not load xp.properties: " + t);
    return "load failed: " + t;
  }}
}}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static long[] resolve(String id) {
  if (id == null) return NONE;
  long[] c = (long[]) CACHE.get(id);
  if (c != null) return c;
  long[] best = (long[]) EXACT.get(id);
  if (best == null) {
    int bestLen = -1;
    java.util.ArrayList pf = PFX;
    for (int i = 0; i < pf.size(); i++) {
      Object[] e = (Object[]) pf.get(i);
      String p = (String) e[0];
      if (p.length() > bestLen && id.startsWith(p)) { bestLen = p.length(); best = (long[]) e[1]; }
    }
    java.util.ArrayList sf = SFX;
    for (int i = 0; i < sf.size(); i++) {
      Object[] e = (Object[]) sf.get(i);
      String p = (String) e[0];
      if (p.length() > bestLen && id.endsWith(p)) { bestLen = p.length(); best = (long[]) e[1]; }
    }
  }
  if (best == null) best = NONE;
  CACHE.put(id, best);
  return best;
}""", cfg))
# the id rules match: the item id for a block (state variants share the base item), else the raw id without '*'/_State_ suffix
cfg.addMethod(CtNewMethod.make(f"""
public static String familyId({BTY} bt) {{
  try {{
    {ITM} it = bt.getItem();
    if (it != null) {{ String iid = it.getId(); if (iid != null && iid.length() > 0) return iid; }}
  }} catch (Throwable t) {{ }}
  String id = bt.getId();
  if (id == null) return null;
  if (id.startsWith("*")) id = id.substring(1);
  int s = id.indexOf("_State_");
  if (s > 0) id = id.substring(0, s);
  return id;
}}""", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static String stateOf({BTY} bt) {{
  try {{ return bt.getStateForBlock(bt.getId()); }} catch (Throwable t) {{ return null; }}
}}""", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static boolean hasFinalStage({BTY} bt) {{
  try {{
    {SDT} sd = bt.getState();
    if (sd == null) return false;
    java.util.Set names = sd.getStateNames();
    return names != null && names.contains("StageFinal");
  }} catch (Throwable t) {{ return false; }}
}}""", cfg))
# current block id at a position (world thread), "" for an unknown block, null when the section is not loaded.
# Same read path the engine uses in UseBlockInteraction.doInteraction / FarmingUtil.harvest (never loads a chunk).
cfg.addMethod(CtNewMethod.make(f"""
public static String blockIdAt({WLD} w, int x, int y, int z) {{
  try {{
    {CHS} cs = w.getChunkStore();
    if (cs == null) return null;
    {REF} sr = cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (sr == null || !sr.isValid()) return null;
    {BSC} sec = ({BSC}) cs.getStore().getComponent(sr, {BSC}.getComponentType());
    if (sec == null) return null;
    {BTY} bt = ({BTY}) {BTY}.getAssetMap().getAsset(sec.get(x, y, z));
    if (bt == null) return "";
    String id = bt.getId();
    return id == null ? "" : id;
  }} catch (Throwable t) {{ return null; }}
}}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static long scaled(long base) {
  if (base <= 0L) return 0L;
  double m = MULT;
  if (m == 1.0) return base;
  long v = Math.round(base * m);
  return v < 0L ? 0L : v;
}""", cfg))
# block break -> {skill, xp, placedCheck 1/0} or null (no XP)
cfg.addMethod(CtNewMethod.make(f"""
public static long[] classifyBreak({BTY} bt) {{
  if (bt == null) return null;
  long[] r = resolve(familyId(bt));
  if (r == null || r[0] < 0L || r[1] <= 0L) return null;
  boolean ripeCrop = hasFinalStage(bt);
  if (ripeCrop && NEED_RIPE && !"StageFinal".equals(stateOf(bt))) return null;
  long x = scaled(r[1]);
  if (x <= 0L) return null;
  return new long[] {{ r[0], x, ripeCrop ? 0L : 1L }};
}}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static long combatXp(String role, float maxHp) {
  if (role != null) {
    Long o = (Long) ROLE.get(role);
    if (o != null) return scaled(o.longValue());
    if (SEEN_ROLES.putIfAbsent(role, Boolean.TRUE) == null) info("combat: first kill of NPC role " + role + " (max health " + maxHp + ") - override with combat.role." + role + "=<xp>");
  }
  long x;
  if (maxHp > 0.0f) x = Math.round(maxHp * C_PER_HP); else x = C_DEFAULT;
  if (x < C_MIN) x = C_MIN;
  if (x > C_MAX) x = C_MAX;
  return scaled(x);
}""", cfg))

# ================= SmithCfg.forOutput (0.4): Smithing XP per smelted item (Smithing-Smelting spec 2.3) =================
# 1. smithing.xp.<exact id> (0 = none; code defaults include Ingredient_Charcoal=0)  2. Ingredient_Bar_*: the Mining XP of the ore its
# Furnace recipe uses (CraftingPlugin.getBenchRecipes(Processing, "Furnace"), input 0 -> SkillCfg.resolve) x oreFactor, at least 1
# 3. smithing.smeltDefault. Cached per id; cleared by SmithCfg.read and SkillCfg.load (the ore rules may have changed).
smc.addMethod(CtNewMethod.make(f"""
public static long fromOre(String id) {{
  try {{
    java.util.List l = {CRPL}.getBenchRecipes({BTP}.Processing, "Furnace");
    for (int i = 0; l != null && i < l.size(); i++) {{
      Object o = l.get(i);
      if (!(o instanceof {CRR})) continue;
      {CRR} r = ({CRR}) o;
      {MQ} po = r.getPrimaryOutput();
      if (po == null || !id.equals(po.getItemId())) continue;
      {MQ}[] in = r.getInput();
      if (in == null || in.length == 0 || in[0] == null || in[0].getItemId() == null) continue;
      long[] rule = {PKG}.SkillCfg.resolve(in[0].getItemId());
      if (rule != null && rule[0] == (long) {PKG}.SkillDefs.MINING && rule[1] > 0L) return Math.max(1L, Math.round(rule[1] * ORE_FACTOR));
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("smithing: could not look up the Furnace recipe of " + id + ": " + t); }}
  return -1L;
}}""", smc))
smc.addMethod(CtNewMethod.make("""
public static long forOutput(String id) {
  if (id == null) return 0L;
  Object c = CACHE.get(id);
  if (c instanceof Long) return ((Long) c).longValue();
  long v;
  Object x = XP.get(id);
  if (x instanceof Long) v = ((Long) x).longValue();
  else {
    v = -1L;
    if (id.startsWith("Ingredient_Bar_")) v = fromOre(id);
    if (v < 0L) v = DEFAULT;
  }
  CACHE.put(id, Long.valueOf(v));
  return v;
}""", smc))
# ================= RecipeXp (0.4): which skill a finished craft pays and how much (one table for the bench, the furnace tab and the bridge) =====
# -> {slot, base XP per craft} or null. Cookingbench / Campfire recipes -> null (SkyyCooking owns Cooking and pays it through
# skill:fn:addxp; 0.4 decision), Alchemybench -> Alchemy, Furnace -> Smithing (only while smithing.smelt.enabled), anything else null.
# No cache of its own (SmithCfg.CACHE is the only one, so /skills reload takes effect at once).
rxp.addMethod(CtNewMethod.make(f"""
public static long[] classify({CRR} rc) {{
  if (rc == null) return null;
  {BRQ}[] br = rc.getBenchRequirement();
  if (br == null || br.length == 0) return null;
  for (int i = 0; i < br.length; i++) {{
    if (br[i] == null || br[i].id == null) continue;
    if (br[i].id.equalsIgnoreCase("Cookingbench") || br[i].id.equalsIgnoreCase("Campfire")) return null;
  }}
  for (int i = 0; i < br.length; i++) {{
    if (br[i] == null || br[i].id == null) continue;
    String b = br[i].id;
    if (b.equalsIgnoreCase("Alchemybench")) {{
      if (!{PKG}.AlchCfg.ENABLED) return null;
      {MQ} po = rc.getPrimaryOutput();
      if (po == null || po.getItemId() == null) return null;
      long xp = {PKG}.AlchCfg.xpFor(po.getItemId(), br[i].requiredTierLevel);
      if (xp <= 0L) return null;
      return new long[] {{ (long) {PKG}.SkillDefs.ALCHEMY, xp }};
    }}
    if (b.equalsIgnoreCase("Furnace")) {{
      if (!{PKG}.SmithCfg.ENABLED) return null;
      {MQ} po = rc.getPrimaryOutput();
      if (po == null || po.getItemId() == null) return null;
      long per = {PKG}.SmithCfg.forOutput(po.getItemId());
      long xp = per * (long) Math.max(1, po.getQuantity());
      if (xp <= 0L) return null;
      return new long[] {{ (long) {PKG}.SkillDefs.SMITHING, xp }};
    }}
  }}
  return null;
}}""", rxp))
# ================= SkillStore: per-player XP, persistence, bridge =================
# data layout: long[2*N] = xp[0..N-1], paid level[N..2N-1]   (0.2: N = 5; 0.1 hard-coded long[8] / offset 4)
# 0.3.2 (tools/PROFILES-CONTRACT.md): DATA / QUIET / DIRTY / OWNER are keyed by the profile storage key pkey(u) (a String:
# "<uuid>" = profile 1, "<uuid>-pN" = profile N); NAMES (username) and PUBLISHED (bridge state) stay keyed by the player's UUID.
sto.addField(CtField.make("public static java.nio.file.Path DIR;", sto))
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DATA = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap QUIET = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap OWNER = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", sto))
# 0.3.2: storage key of the player's ACTIVE profile - the contract's helper, verbatim (tools/PROFILES-CONTRACT.md)
sto.addMethod(CtNewMethod.make("""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""", sto))
# /skills quiet is stored in the profile file, so it is per profile like everything else in that file
sto.addMethod(CtNewMethod.make("""
public static boolean quiet(java.util.UUID u) {
  return QUIET.containsKey(pkey(u));
}""", sto))
# 0.4.3 player Settings registry (SkyyMenu 0.2+, research/Settings-Spec.md 1.3 / 3.1). No SkyyMenu = no answer = today's behaviour:
# every switch ON except the three /skills quiet always hid (quiet still hides them). With SkyyMenu the old per-profile quiet flag is
# moved ONCE to the three switches (onlyIfUnset) at the first message check.
sto.addMethod(CtNewMethod.make(f"""
public static void moveQuiet(java.util.UUID u) {{
  String k = pkey(u);
  if (!QUIET.containsKey(k)) return;
  Object f = bridge().get("settings:fn:set");
  if (!(f instanceof java.util.function.Function)) return;
  java.util.function.Function sf = (java.util.function.Function) f;
  int ok = 0;
  if (Boolean.TRUE.equals(sf.apply(new Object[] {{ u, "skills.xpGain", Boolean.FALSE, Boolean.TRUE }}))) ok++;
  if (Boolean.TRUE.equals(sf.apply(new Object[] {{ u, "skills.doubleDrop", Boolean.FALSE, Boolean.TRUE }}))) ok++;
  if (Boolean.TRUE.equals(sf.apply(new Object[] {{ u, "skills.extraPotion", Boolean.FALSE, Boolean.TRUE }}))) ok++;
  if (ok == 3 && QUIET.remove(k) != null) {{ DIRTY.put(k, Boolean.TRUE); {PKG}.SkillCfg.info("moved /skills quiet of " + k + " to /settings"); }}
}}""", sto))
sto.addMethod(CtNewMethod.make("""
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      moveQuiet(u);
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  if (key.equals("skills.xpGain") || key.equals("skills.doubleDrop") || key.equals("skills.extraPotion")) return !quiet(u);
  return true;
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyySkills", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""", sto))
# ================= SkillClass (0.3): the player's class from SkyyClasses (bridge), class combat rules =================
scls.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap TOLD = new java.util.concurrent.ConcurrentHashMap();", scls))
scls.addMethod(CtNewMethod.make(f"""
public static int slotOfClass(String c) {{
  if (c == null) return -1;
  String t = c.trim();
  for (int i = 0; i < {PKG}.SkillDefs.CLASSES.length; i++) if ({PKG}.SkillDefs.CLASSES[i].equalsIgnoreCase(t)) return {PKG}.SkillDefs.classSlot(i);
  return -1;
}}""", scls))
scls.addMethod(CtNewMethod.make(f"""
public static String className(java.util.UUID u) {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("class:" + u.toString());
    if (!(o instanceof String)) return null;
    String c = ((String) o).trim();
    return c.length() == 0 ? null : c;
  }} catch (Throwable t) {{ return null; }}
}}""", scls))
scls.addMethod(CtNewMethod.make("""
public static int slot(java.util.UUID u) {
  return slotOfClass(className(u));
}""", scls))
# 0.3.2: false only while SkyyProfiles publishes the active profile's class (profile:class:<uuid>) and SkyyClasses' class:<uuid> does not
# match it yet (right after a profile switch) - then nothing class-based may write into the (new) profile. No profile:class key (no
# SkyyProfiles, or a profile without a class) = true, exactly the 0.3.1 behaviour.
# BOUNDED (review fix): SINCE = UUID -> Long ms the current mismatch was first seen (Perks.tick asks every second, so it starts within
# 1 s of a switch); after GRACE_MS it fails OPEN (true = class:<uuid> decides again, the 0.3.1 behaviour) and warns once per mismatch
# (GAVEUP). A match, a new epoch (Perks.switched) or a disconnect (Acro.retainOnline) resets both, so every switch gets a fresh grace.
scls.addField(CtField.make("public static final long GRACE_MS = 10000L;", scls))
scls.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SINCE = new java.util.concurrent.ConcurrentHashMap();", scls))
scls.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap GAVEUP = new java.util.concurrent.ConcurrentHashMap();", scls))
scls.addMethod(CtNewMethod.make("""
public static void resync(java.util.UUID u) {
  if (SINCE.isEmpty() && GAVEUP.isEmpty()) return;
  SINCE.remove(u);
  GAVEUP.remove(u);
}""", scls))
scls.addMethod(CtNewMethod.make(f"""
public static boolean overdue(java.util.UUID u, String pc, String c) {{
  long now = System.currentTimeMillis();
  Object first = SINCE.putIfAbsent(u, Long.valueOf(now));
  if (first == null) return false;
  if (now - ((Long) first).longValue() < GRACE_MS) return false;
  if (GAVEUP.putIfAbsent(u, Boolean.TRUE) == null) {{
    {PKG}.SkillCfg.warn("class:" + u + " (SkyyClasses) is " + (c == null ? "not set" : c) + " but profile:class:" + u + " (SkyyProfiles) is " + pc
      + " for " + (GRACE_MS / 1000L) + " s - SkyyClasses is not following the profile (SkyyProfiles needs SkyyClasses 0.1.3+). Combat XP, the class"
      + " damage perk and the legacy Combat move follow class:" + u + " again for this player until the next profile switch.");
  }}
  return true;
}}""", scls))
scls.addMethod(CtNewMethod.make(f"""
public static boolean consistent(java.util.UUID u) {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("profile:class:" + u.toString());
    if (!(o instanceof String)) {{ resync(u); return true; }}
    String pc = ((String) o).trim();
    if (pc.length() == 0) {{ resync(u); return true; }}
    String c = className(u);
    if (c != null && c.equalsIgnoreCase(pc)) {{ resync(u); return true; }}
    return overdue(u, pc, c);
  }} catch (Throwable t) {{ return true; }}
}}""", scls))
# storage slot a /skills row shows: the Combat row = the current class's skill (legacy slot 3 without a class)
scls.addMethod(CtNewMethod.make(f"""
public static int rowSlot(java.util.UUID u, int row) {{
  if (row != {PKG}.SkillDefs.COMBAT) return row;
  int c = slot(u);
  return c >= 0 ? c : {PKG}.SkillDefs.COMBAT;
}}""", scls))
# display name of a slot: the class skill name SkyyClasses publishes for the CURRENT class (class:skill:<uuid>), else our label
scls.addMethod(CtNewMethod.make(f"""
public static String skillName(java.util.UUID u, int s) {{
  if (s < 0 || s >= {PKG}.SkillDefs.N) return "?";
  if ({PKG}.SkillDefs.isClass(s) && s == slot(u)) {{
    try {{
      Object o = {PKG}.SkillStore.bridge().get("class:skill:" + u.toString());
      if (o instanceof String && ((String) o).trim().length() > 0) return ((String) o).trim();
    }} catch (Throwable t) {{ }}
  }}
  return {PKG}.SkillDefs.LABELS[s];
}}""", scls))
# "Weapon_Shortbow_,Weapon_Crossbow_" (bridge class:weapons:<Class>) -> "Shortbow / Crossbow"; null when not published
scls.addMethod(CtNewMethod.make(f"""
public static String weaponsText(String cls) {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("class:weapons:" + cls);
    if (!(o instanceof String)) return null;
    String[] ps = ((String) o).split(",");
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < ps.length; i++) {{
      String w = ps[i].trim();
      if (w.startsWith("Weapon_")) w = w.substring(7);
      while (w.endsWith("_")) w = w.substring(0, w.length() - 1);
      w = w.replace('_', ' ').trim();
      if (w.length() == 0) continue;
      if (sb.length() > 0) sb.append(" / ");
      sb.append(w);
    }}
    return sb.length() == 0 ? null : sb.toString();
  }} catch (Throwable t) {{ return null; }}
}}""", scls))
# one chat line per reason (bit) per player per session; TOLD is pruned to online players by Acro.retainOnline
scls.addMethod(CtNewMethod.make("""
public static synchronized boolean claimTold(java.util.UUID u, int bit) {
  Integer m = (Integer) TOLD.get(u);
  int v = m == null ? 0 : m.intValue();
  if ((v & bit) != 0) return false;
  TOLD.put(u, Integer.valueOf(v | bit));
  return true;
}""", scls))
scls.addMethod(CtNewMethod.make(f"""
public static void tellOnce({PR} pr, int bit, String text) {{
  try {{
    if (!{PKG}.SkillStore.notifyOn(pr.getUuid(), "skills.combatHints")) return;
    if (claimTold(pr.getUuid(), bit)) pr.sendMessage({MSG}.raw("[Skills] " + text).color("#ffb080"));
  }} catch (Throwable t) {{ }}
}}""", scls))
scls.addMethod(CtNewMethod.make(f"""
public static java.util.function.Function allowedFn() {{
  Object f = {PKG}.SkillStore.bridge().get("class:fn:allowed");
  return f instanceof java.util.function.Function ? (java.util.function.Function) f : null;
}}""", scls))
# may this item earn / boost class combat: SkyyClasses allows it for this player AND (classWeaponOnly) it is one of the class's own
# weapons (prefix list class:weapons:<Class>; when that key is missing the allowed answer alone decides)
scls.addMethod(CtNewMethod.make(f"""
public static boolean itemOk(java.util.UUID u, {IS} it, java.util.function.Function f, String prefixes) {{
  if (it == null || it.isEmpty()) return false;
  String id = it.getItemId();
  if (id == null || id.length() == 0) return false;
  Object r = null;
  try {{ r = f.apply(new Object[] {{ u, id }}); }} catch (Throwable t) {{ return false; }}
  if (!Boolean.TRUE.equals(r)) return false;
  if (!{PKG}.PerkCfg.WEAPON_ONLY || prefixes == null) return true;
  String[] ps = prefixes.split(",");
  for (int i = 0; i < ps.length; i++) {{
    String p = ps[i].trim();
    if (p.length() > 0 && id.startsWith(p)) return true;
  }}
  return false;
}}""", scls))
# the weapon a hit / kill was made with = the attacker's main-hand item, else the active utility item (the Kunai is thrown from the
# utility slot) - the same two places SkyyClasses' DamageLock judges (InventoryComponent.getItemInHand, vanilla DamageAttackerTool)
scls.addMethod(CtNewMethod.make(f"""
public static boolean weaponOk(java.util.UUID u, int slot, java.util.function.Function f, {CAC} acc, {REF} att) {{
  if (!{PKG}.SkillDefs.isClass(slot)) return false;
  Object po = {PKG}.SkillStore.bridge().get("class:weapons:" + {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(slot)]);
  String prefixes = po instanceof String ? (String) po : null;
  try {{ if (itemOk(u, {INVC}.getItemInHand(acc, att), f, prefixes)) return true; }} catch (Throwable t) {{ }}
  try {{
    {UTIL} ut = ({UTIL}) acc.getComponent(att, {UTIL}.getComponentType());
    if (ut != null && itemOk(u, ut.getActiveItem(), f, prefixes)) return true;
  }} catch (Throwable t) {{ }}
  return false;
}}""", scls))
# storage slot that earns this kill's combat XP, or -1 (and the reason is told once): SkyyClasses present, a class, a known class,
# a class weapon
scls.addMethod(CtNewMethod.make(f"""
public static int killSlot({PR} pr, {CAC} acc, {REF} att) {{
  java.util.UUID u = pr.getUuid();
  java.util.function.Function f = allowedFn();
  if (f == null) {{ tellOnce(pr, 1, "Combat XP comes from your class skill, but SkyyClasses is not installed on this server - no combat XP is awarded."); return -1; }}
  if (!consistent(u)) {{ tellOnce(pr, 16, "Your class is still switching to this profile's class - combat XP resumes in a moment."); return -1; }}
  String c = className(u);
  if (c == null) {{ tellOnce(pr, 2, "Choose a class with /class to earn combat XP - your combat skill is your class skill."); return -1; }}
  int s = slotOfClass(c);
  if (s < 0) {{ tellOnce(pr, 4, "Your class " + c + " has no combat skill in SkyySkills yet - no combat XP."); return -1; }}
  if (!weaponOk(u, s, f, acc, att)) {{
    String w = weaponsText({PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)]);
    tellOnce(pr, 8, "Only kills with your " + c + " weapons" + (w == null ? "" : " (" + w + ")") + " earn " + skillName(u, s) + " XP.");
    return -1;
  }}
  return s;
}}""", scls))
# /skills top|stats <skill>: "combat" = your class skill (the legacy Combat slot without a class)
scls.addMethod(CtNewMethod.make(f"""
public static int argSlot({PR} pr, String arg) {{
  int s = {PKG}.SkillDefs.indexOf(arg);
  if (s < 0) {{
    pr.sendMessage({MSG}.raw("[Skills] Unknown skill. Use mining, foraging, farming, alchemy, smithing, cooking, acrobatics, exploration, combat (your class skill) or a class skill: archery, swordsmanship, sorcery, fury, divinity, assassination, shaman. /skills stats also opens overall."));
    return -1;
  }}
  if (s == {PKG}.SkillDefs.COMBAT) {{ int c = slot(pr.getUuid()); if (c >= 0) return c; }}
  return s;
}}""", scls))
sto.addField(CtField.make("public static final Object IO = new Object();", sto))
sto.addField(CtField.make("public static volatile long WARNED = 0L;", sto))
# player file (players/<pkey>.properties, 0.3.2) -> {long[2*N] data, String name, Boolean quiet}. Runs WITHOUT any lock (no disk I/O
# under the SkillStore lock).
sto.addMethod(CtNewMethod.make(f"""
public static Object[] readFile(String k, java.util.UUID u) {{
  long[] d = new long[2 * {PKG}.SkillDefs.N];
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) d[{PKG}.SkillDefs.N + i] = -1L;
  String nm = null;
  boolean quiet = false;
  try {{
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {{
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try {{ p.load(in); }} finally {{ in.close(); }}
      for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
        String n = {PKG}.SkillDefs.NAMES[i];
        try {{ String v = p.getProperty(n); if (v != null) d[i] = Math.max(0L, Long.parseLong(v.trim())); }} catch (Throwable t) {{ }}
        try {{ String v = p.getProperty(n + ".paid"); if (v != null) d[{PKG}.SkillDefs.N + i] = Long.parseLong(v.trim()); }} catch (Throwable t) {{ d[{PKG}.SkillDefs.N + i] = -1L; }}
      }}
      String s = p.getProperty("name");
      if (s != null && s.trim().length() > 0) nm = s.trim();
      quiet = "true".equalsIgnoreCase(String.valueOf(p.getProperty("quiet")).trim());
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not load skills for " + k + ": " + t); }}
  // no paid marker yet -> current level counts as paid (no retroactive rewards)
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) if (d[{PKG}.SkillDefs.N + i] < 0L) d[{PKG}.SkillDefs.N + i] = (long) {PKG}.SkillDefs.levelOf(i, d[i]);
  return new Object[] {{ d, nm, Boolean.valueOf(quiet) }};
}}""", sto))
# cached data; a first load reads the file BEFORE taking the lock, the lock only decides whose copy is installed.
# 0.3.2: keyed by the profile storage key k = pkey(u) (contract rule 2); OWNER k -> UUID (for the name saved in the file).
sto.addMethod(CtNewMethod.make("""
public static synchronized long[] install(String k, java.util.UUID u, Object[] got) {
  long[] d = (long[]) DATA.get(k);
  if (d != null) return d;
  d = (long[]) got[0];
  if (got[1] != null) NAMES.putIfAbsent(u, got[1]);
  if (((Boolean) got[2]).booleanValue()) QUIET.put(k, Boolean.TRUE);
  OWNER.put(k, u);
  DATA.put(k, d);
  return d;
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static long[] dataK(String k, java.util.UUID u) {
  long[] d = (long[]) DATA.get(k);
  if (d != null) return d;
  Object[] got = readFile(k, u);
  return install(k, u, got);
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static long[] data(java.util.UUID u) {
  return dataK(pkey(u), u);
}""", sto))
# element read/write under the SkillStore lock (keeps snap() consistent with add() and payOwed())
sto.addMethod(CtNewMethod.make("""
public static synchronized long rd(long[] d, int i) {
  return d[i];
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static synchronized void wr(long[] d, int i, long v) {
  d[i] = v;
}""", sto))
sto.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.Properties snap(String k) {{
  long[] d = (long[]) DATA.get(k);
  if (d == null) return null;
  java.util.Properties p = new java.util.Properties();
  Object ou = OWNER.get(k);
  String nm = ou == null ? null : (String) NAMES.get(ou);
  if (nm != null) p.setProperty("name", nm);
  p.setProperty("quiet", QUIET.containsKey(k) ? "true" : "false");
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
    p.setProperty({PKG}.SkillDefs.NAMES[i], String.valueOf(d[i]));
    p.setProperty({PKG}.SkillDefs.NAMES[i] + ".paid", String.valueOf(d[{PKG}.SkillDefs.N + i]));
  }}
  return p;
}}""", sto))
# snapshot under the SkillStore lock, write outside it; IO keeps two saves of the same file (ticker + shutdown) ordered
sto.addMethod(CtNewMethod.make(f"""
public static void moveRetry(java.nio.file.Path from, java.nio.file.Path to) throws java.io.IOException {{
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {{
    try {{
      java.nio.file.Files.move(from, to, new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
      return;
    }} catch (java.nio.file.AtomicMoveNotSupportedException e) {{
      java.nio.file.Files.move(from, to, new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
      return;
    }} catch (java.nio.file.FileSystemException e) {{
      last = e;
    }}
    try {{ Thread.sleep(20L); }} catch (InterruptedException ie) {{ }}
  }}
  throw last;
}}""", sto))
# true = written (or nothing to write); false = the file on disk is older than memory (the caller keeps the key dirty)
sto.addMethod(CtNewMethod.make(f"""
public static boolean saveNow(String k) {{
  try {{
    java.util.Properties p = snap(k);
    if (p == null) return true;
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try {{ p.store(out, "SkyySkills"); }} finally {{ out.close(); }}
    moveRetry(tmp, DIR.resolve(k + ".properties"));
    return true;
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("could not save skills for " + k + " (kept dirty, retried on the next save): " + t);
    return false;
  }}
}}""", sto))
sto.addMethod(CtNewMethod.make("""
public static boolean save(String k) {
  boolean r;
  synchronized (IO) { r = saveNow(k); }
  return r;
}""", sto))
# a key whose save failed goes back into DIRTY AFTER the pass (never retried inside the same pass)
sto.addMethod(CtNewMethod.make("""
public static void flushDirty() {
  java.util.ArrayList failed = new java.util.ArrayList();
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    it.remove();
    if (!save(k)) failed.add(k);
  }
  for (int i = 0; i < failed.size(); i++) DIRTY.put(failed.get(i), Boolean.TRUE);
}""", sto))
# leaderboard reads (SkillTop.all): NIO stream under the IO lock. java.io.FileInputStream opens without FILE_SHARE_DELETE, and on
# Windows any open handle makes the ATOMIC_MOVE of a save fail (tested on the game JRE), so our own reads never overlap our saves.
sto.addMethod(CtNewMethod.make("""
public static java.util.Properties readProps(java.nio.file.Path f) throws java.io.IOException {
  java.util.Properties p = new java.util.Properties();
  java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
  try { p.load(in); } finally { in.close(); }
  return p;
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static java.util.Properties readLocked(java.nio.file.Path f) throws java.io.IOException {
  java.util.Properties p;
  synchronized (IO) { p = readProps(f); }
  return p;
}""", sto))
sto.addMethod(CtNewMethod.make(f"""
public static int level(java.util.UUID u, int skill) {{
  if (skill < 0 || skill >= {PKG}.SkillDefs.N) return 0;
  return {PKG}.SkillDefs.levelOf(skill, data(u)[skill]);
}}""", sto))
sto.addMethod(CtNewMethod.make(f"""
public static String levelsOf(java.util.UUID u, long[] d) {{
  int cs = {PKG}.SkillClass.slot(u);
  int[] order = new int[] {{ {PKG}.SkillDefs.MINING, {PKG}.SkillDefs.FORAGING, {PKG}.SkillDefs.FARMING, {PKG}.SkillDefs.ACROBATICS, {PKG}.SkillDefs.ALCHEMY, {PKG}.SkillDefs.SMITHING, {PKG}.SkillDefs.COOKING, {PKG}.SkillDefs.EXPLORATION }};
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < order.length; i++) {{
    if (i > 0) sb.append(',');
    sb.append({PKG}.SkillDefs.LABELS[order[i]]).append(':').append({PKG}.SkillDefs.levelOf(order[i], d[order[i]]));
  }}
  for (int j = 0; j < {PKG}.SkillDefs.CLASS_SLOT.length; j++) {{
    int s = {PKG}.SkillDefs.CLASS_SLOT[j];
    if (s != cs && d[s] <= 0L) continue;
    sb.append(',').append({PKG}.SkillDefs.LABELS[s]).append(':').append({PKG}.SkillDefs.levelOf(s, d[s]));
  }}
  return sb.toString();
}}""", sto))
sto.addMethod(CtNewMethod.make("""
public static String levelsString(java.util.UUID u) {
  return levelsOf(u, data(u));
}""", sto))
sto.addField(CtField.make("public static final Object PUB = new Object();", sto))
# false = the active profile's data is not in memory and load was false (nothing published)
sto.addMethod(CtNewMethod.make("""
public static boolean publishNow(java.util.UUID u, boolean load) {
  try {
    String k = pkey(u);
    long[] d = (long[]) DATA.get(k);
    if (d == null) {
      if (!load) return false;
      d = dataK(k, u);
    }
    bridge().put("skill:" + u.toString(), levelsOf(u, d));
    PUBLISHED.put(u, Boolean.TRUE);
  } catch (Throwable t) { }
  return true;
}""", sto))
# the file (if any) is loaded BEFORE taking PUB; inside, publishNow only loads when the key flipped in between
sto.addMethod(CtNewMethod.make("""
public static void publish(java.util.UUID u) {
  try { data(u); } catch (Throwable t) { }
  synchronized (PUB) { publishNow(u, true); }
}""", sto))
# scheduler thread (publishOnline): memory only - never reads a player file
sto.addMethod(CtNewMethod.make("""
public static boolean publishIfLoaded(java.util.UUID u) {
  boolean r;
  synchronized (PUB) { r = publishNow(u, false); }
  return r;
}""", sto))
# world thread: load a player's file and publish it (handed over by publishOnline, FlushTask pattern)
pub.addInterface(pool.get("java.lang.Runnable"))
pub.addField(CtField.make("public java.util.UUID u;", pub))
pub.addConstructor(CtNewConstructor.make("public PublishTask(java.util.UUID u) { this.u = u; }", pub))
pub.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    {PKG}.SkillStore.data(this.u);
    {PKG}.SkillStore.publish(this.u);
  }} catch (Throwable t) {{ }}
}}""", pub))
# scheduler thread (shared, single thread): memory only. Players not loaded yet go to their world thread.
sto.addMethod(CtNewMethod.make(f"""
public static void publishOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      if (PUBLISHED.containsKey(u)) continue;
      try {{ String n = pr.getUsername(); if (n != null) NAMES.put(u, n); }} catch (Throwable t) {{ }}
      if (publishIfLoaded(u)) continue;
      try {{
        {WLD} w = {UNI}.get().getWorld(pr.getWorldUuid());
        if (w != null) w.execute(new {PKG}.PublishTask(u));
      }} catch (Throwable t) {{ }}
    }}
    PUBLISHED.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", sto))
# review fix R9 (0.4.12): forget who is published after a live level table change - publishOnline republishes everyone within 5 s
sto.addMethod(CtNewMethod.make("""
public static void republishAll() {
  synchronized (PUB) { PUBLISHED.clear(); }
}""", sto))
# add xp; returns {{oldLevel, newLevel, total}}. The paid marker is NOT touched here (payOwed moves it after a real payout).
sto.addMethod(CtNewMethod.make("""
public static synchronized long[] bump(long[] d, int skill, long amount) {
  long before = d[skill];
  long after = before + amount;
  if (after < before) after = Long.MAX_VALUE;
  d[skill] = after;
  return new long[] { before, after };
}""", sto))
# 0.3: legacy "Combat" XP (slot 3) -> the class slot, only while every class slot is still 0; returns the XP moved or -1
sto.addMethod(CtNewMethod.make(f"""
public static synchronized long moveLegacy(long[] d, int slot) {{
  int c = {PKG}.SkillDefs.COMBAT;
  int n = {PKG}.SkillDefs.N;
  if (!{PKG}.SkillDefs.isClass(slot) || d[c] <= 0L) return -1L;
  for (int j = 0; j < {PKG}.SkillDefs.CLASS_SLOT.length; j++) if (d[{PKG}.SkillDefs.CLASS_SLOT[j]] > 0L) return -1L;
  long x = d[c];
  d[slot] = x;
  d[n + slot] = d[n + c] < 0L ? 0L : d[n + c];
  d[c] = 0L;
  d[n + c] = 0L;
  return x;
}}""", sto))
sto.addMethod(CtNewMethod.make(f"""
public static long[] addK(String k, java.util.UUID u, String name, int skill, long amount) {{
  long[] d = dataK(k, u);
  long[] ba = bump(d, skill, amount);
  if (name != null) NAMES.put(u, name);
  DIRTY.put(k, Boolean.TRUE);
  return new long[] {{ (long) {PKG}.SkillDefs.levelOf(skill, ba[0]), (long) {PKG}.SkillDefs.levelOf(skill, ba[1]), ba[1] }};
}}""", sto))
# true only when SkyyCoins really paid (its add fn returns the new balance, or null when nothing was changed)
sto.addMethod(CtNewMethod.make(f"""
public static boolean coinsAdd(java.util.UUID u, long n) {{
  Object f = null;
  try {{
    f = bridge().get("coins:fn:add");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] {{ u, Long.valueOf(n) }});
    if (r instanceof Number) return true;
  }} catch (Throwable t) {{ }}
  long now = System.currentTimeMillis();
  if (f != null && now - WARNED > 60000L) {{
    WARNED = now;
    {PKG}.SkillCfg.warn("coins:fn:add did not pay " + n + " coins to " + u + " - that level reward stays owed and is retried on the next XP gain");
  }}
  return false;
}}""", sto))
sto.addMethod(CtNewMethod.make(f"""
public static boolean owesK(String k, java.util.UUID u, int skill) {{
  long[] d = dataK(k, u);
  return rd(d, {PKG}.SkillDefs.N + skill) < (long) {PKG}.SkillDefs.levelOf(skill, rd(d, skill));
}}""", sto))
# pay every owed level of one skill, lowest first; the paid marker only moves past a level whose coins really arrived.
# Caller holds the player's own lock (his data array), never the global one, while SkyyCoins writes its file.
# -> {{first paid level (-1 none), last, coins sum, perLevel, changed 1/0}}; payOwed returns null when nothing was paid
sto.addMethod(CtNewMethod.make(f"""
public static long[] payLocked(java.util.UUID u, int skill, long[] d) {{
  long first = -1L;
  long last = -1L;
  long sum = 0L;
  long per = {PKG}.SkillCfg.COINS_PER_LEVEL;
  long changed = 0L;
  int lv = {PKG}.SkillDefs.levelOf(skill, rd(d, skill));
  boolean stop = false;
  while (!stop && rd(d, {PKG}.SkillDefs.N + skill) < (long) lv) {{
    long next = rd(d, {PKG}.SkillDefs.N + skill) + 1L;
    long coins = per * next;
    if (per <= 0L || coins / next != per) {{
      wr(d, {PKG}.SkillDefs.N + skill, next);
      changed = 1L;
    }} else if (coinsAdd(u, coins)) {{
      wr(d, {PKG}.SkillDefs.N + skill, next);
      changed = 1L;
      if (first < 0L) first = next;
      last = next;
      sum += coins;
    }} else {{
      stop = true;
    }}
  }}
  return new long[] {{ first, last, sum, per, changed }};
}}""", sto))
sto.addMethod(CtNewMethod.make("""
public static long[] payGuarded(java.util.UUID u, int skill, long[] d) {
  synchronized (d) { return payLocked(u, skill, d); }
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static long[] payOwedK(String k, java.util.UUID u, int skill) {
  long[] d = dataK(k, u);
  long[] res = payGuarded(u, skill, d);
  if (res == null) return null;
  if (res[4] != 0L) DIRTY.put(k, Boolean.TRUE);
  if (res[0] < 0L) return null;
  return res;
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static boolean toggleQuiet(java.util.UUID u) {
  String k = pkey(u);
  dataK(k, u);
  boolean q;
  if (QUIET.remove(k) != null) q = false; else { QUIET.put(k, Boolean.TRUE); q = true; }
  DIRTY.put(k, Boolean.TRUE);
  return q;
}""", sto))

# ================= Overall (0.4.6): base Mana + the Overall Level (research/Overall-Level-Spec.md 2 / 4.4) =================
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
  return {PKG}.OverallCfg.listed(classOf(u));
}}""", ovl))
ovl.addMethod(CtNewMethod.make(f"""
public static float typeMax(int idx) {{
  try {{
    {ESTT} t = ({ESTT}) {ESTT}.getAssetMap().getAsset(idx);
    if (t != null) return t.getMax();
  }} catch (Throwable e) {{ }}
  return 0.0f;
}}""", ovl))
# the TOTAL base this player has (0.4.8: the class's Base Mana by class entry, else mana.base; 0 when the part is off)
ovl.addMethod(CtNewMethod.make(f"""
public static float baseTarget(java.util.UUID u) {{
  if (!{PKG}.OverallCfg.MANA_ON) return 0.0f;
  return round2({PKG}.OverallCfg.baseFor(classOf(u)));
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
    sum += {PKG}.SkillDefs.levelOf(s, d[s]);
    n++;
  }}
  if ({PKG}.OverallCfg.CLASS && classesOn()) {{
    String c = classOf(u);
    if (c == null) n++;
    else {{
      int cs = {PKG}.SkillClass.slotOfClass(c);
      if (cs >= 0) {{ sum += {PKG}.SkillDefs.levelOf(cs, d[cs]); n++; }}
      else if (BADCLS.putIfAbsent(c.toLowerCase(), Boolean.TRUE) == null) {PKG}.SkillCfg.warn("class " + c + " has no class skill in SkyySkills - it is left out of the Overall Level");
    }}
  }}
  return new int[] {{ sum, n }};
}}""", ovl))
ovl.addMethod(CtNewMethod.make("""
public static int level(int[] sc) {
  return sc[1] <= 0 ? 0 : sc[0] / sc[1];
}""", ovl))
# 0.4.12: the highest Overall Level this player can reach = every skill sums() counts at ITS OWN max level (class skills have their own
# max, levels.class.max); no class yet counts the class skill max (the potential), an unknown class is left out like in sums()
ovl.addMethod(CtNewMethod.make(f"""
public static int maxLevel(java.util.UUID u) {{
  int sum = 0;
  int n = 0;
  int[] sl = {PKG}.OverallCfg.SLOTS;
  for (int i = 0; i < sl.length; i++) {{
    int s = sl[i];
    if (s < 0 || s >= {PKG}.SkillDefs.N) continue;
    sum += {PKG}.SkillDefs.maxOf(s);
    n++;
  }}
  if ({PKG}.OverallCfg.CLASS && classesOn()) {{
    String c = classOf(u);
    int cs = c == null ? {PKG}.SkillDefs.CLASS_SLOT[0] : {PKG}.SkillClass.slotOfClass(c);
    if (cs >= 0) {{ sum += {PKG}.SkillDefs.maxOf(cs); n++; }}
  }}
  return n <= 0 ? 0 : sum / n;
}}""", ovl))
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
  return {PKG}.OverallCfg.tableText();
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
    sb.append({PKG}.SkillDefs.LABELS[s]).append(" ").append({PKG}.SkillDefs.levelOf(s, d[s]));
  }}
  if ({PKG}.OverallCfg.CLASS && classesOn()) {{
    String c = classOf(u);
    String part = null;
    if (c == null) part = "Class skill 0 (choose a class with /class)";
    else {{
      int cs = {PKG}.SkillClass.slotOfClass(c);
      if (cs >= 0) part = {PKG}.SkillClass.skillName(u, cs) + " " + {PKG}.SkillDefs.levelOf(cs, d[cs]) + " (your class)";
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
  else if (magic(u)) out.add("Base Mana " + num((double) baseTarget(u)) + " - the " + {PKG}.OverallCfg.canonClass(classOf(u)) + " base (Base Mana by class)");
  else out.add("Base Mana " + num((double) round2({PKG}.OverallCfg.BASE)) + (magicText().length() > 0 ? " (by class: " + magicText() + ")" : ""));
  return out;
}}""", ovl))
ovl.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList nextLines(int lv, int top) {{
  java.util.ArrayList out = new java.util.ArrayList();
  if (top <= 0) {{ out.add("Nothing - no skill counts toward the Overall Level"); return out; }}
  if (lv >= top) return out;
  if (!{PKG}.OverallCfg.ON) {{ out.add("Nothing - Overall Level Health and Mana are off"); return out; }}
  if ({PKG}.OverallCfg.HP > 0.0) out.add("+" + num((double) round2({PKG}.OverallCfg.HP)) + " max Health");
  if ({PKG}.OverallCfg.MANA > 0.0) out.add("+" + num((double) round2({PKG}.OverallCfg.MANA)) + " max Mana");
  if (out.isEmpty()) out.add("Nothing - both amounts are 0 on this server");
  return out;
}}""", ovl))
# ================= ClassMana part 2 (0.4.15): the per-player amount (Perks.ovl), the Stats page line, the /skills mana line =================
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

# ================= SkillFn: bridge skill:fn:level =================
fn.addInterface(pool.get("java.util.function.Function"))
fn.addConstructor(CtNewConstructor.make("public SkillFn() { }", fn))
fn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    Object[] a = (Object[]) arg;
    if ("overall".equalsIgnoreCase(String.valueOf(a[1]).trim())) return Integer.valueOf({PKG}.Overall.levelOf((java.util.UUID) a[0]));
    int i = {PKG}.SkillDefs.indexOf(String.valueOf(a[1]));
    if (i < 0) return Integer.valueOf(0);
    java.util.UUID u = (java.util.UUID) a[0];
    if (i == {PKG}.SkillDefs.COMBAT) i = {PKG}.SkillClass.rowSlot(u, i);
    return Integer.valueOf({PKG}.SkillStore.level(u, i));
  }} catch (Throwable t) {{ return Integer.valueOf(0); }}
}}""", fn))

# ================= SkillMsg: throttled "+12 Mining XP (340/500)" =================
msg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();", msg))
msg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();", msg))
msg.addMethod(CtNewMethod.make(f"""
public static synchronized String take(java.util.UUID u) {{
  long[] p = (long[]) PEND.get(u);
  if (p == null) return null;
  long[] d = {PKG}.SkillStore.data(u);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < p.length; i++) {{
    if (p[i] <= 0L) continue;
    if (sb.length() > 0) sb.append("    ");
    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillDefs.LABELS[i]).append(" XP (").append({PKG}.SkillDefs.progress(i, d[i])).append(")");
  }}
  PEND.remove(u);
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  return sb.length() == 0 ? null : sb.toString();
}}""", msg))
msg.addMethod(CtNewMethod.make(f"""
public static void send({PR} pr) {{
  try {{
    String s = take(pr.getUuid());
    if (s != null) pr.sendMessage({MSG}.raw(s).color("#9fd8ff"));
  }} catch (Throwable t) {{ }}
}}""", msg))
msg.addMethod(CtNewMethod.make(f"""
public static void note({PR} pr, int skill, long amount) {{
  if (!{PKG}.SkillCfg.FEEDBACK) return;
  java.util.UUID u = pr.getUuid();
  if (!{PKG}.SkillStore.notifyOn(u, "skills.xpGain")) return;
  boolean due;
  synchronized ({PKG}.SkillMsg.class) {{
    long[] p = (long[]) PEND.get(u);
    if (p == null) {{ p = new long[{PKG}.SkillDefs.N]; PEND.put(u, p); }}
    p[skill] += amount;
    Long last = (Long) LAST.get(u);
    due = last == null || System.currentTimeMillis() - last.longValue() >= {PKG}.SkillCfg.FEEDBACK_MS;
  }}
  if (due) send(pr);
}}""", msg))

fl.addInterface(pool.get("java.lang.Runnable"))
fl.addField(CtField.make("public java.util.UUID u;", fl))
fl.addConstructor(CtNewConstructor.make("public FlushTask(java.util.UUID u) { this.u = u; }", fl))
fl.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) {{ {PKG}.SkillMsg.PEND.remove(this.u); return; }}
    {PKG}.SkillMsg.send(pr);
  }} catch (Throwable t) {{ }}
}}""", fl))
# scheduler thread: hand leftover feedback to each player's world thread
msg.addMethod(CtNewMethod.make(f"""
public static void flushDue() {{
  try {{
    long now = System.currentTimeMillis();
    java.util.Iterator it = new java.util.ArrayList(PEND.keySet()).iterator();
    while (it.hasNext()) {{
      java.util.UUID u = (java.util.UUID) it.next();
      Long last = (Long) LAST.get(u);
      if (last != null && now - last.longValue() < {PKG}.SkillCfg.FEEDBACK_MS) continue;
      {PR} pr = {UNI}.get().getPlayer(u);
      if (pr == null || !pr.isValid()) {{ PEND.remove(u); LAST.remove(u); continue; }}
      {WLD} w = {UNI}.get().getWorld(pr.getWorldUuid());
      if (w == null) continue;
      LAST.put(u, Long.valueOf(now));
      try {{ w.execute(new {PKG}.FlushTask(u)); }} catch (Throwable t) {{ }}
    }}
  }} catch (Throwable t) {{ }}
}}""", msg))

# ================= SkillBonus (0.4 trees bridge, Skill-Trees-Spec 9.3): skill:bonus:<uuid>, skill:on:gather, the Tree buttons =================
# skill:bonus:<uuid> = ConcurrentHashMap source -> immutable Map{"xp.mining": 0.15, "dd.farming": 0.2, ...} (fractions). Read live on every
# award (UUID-keyed = the ACTIVE profile, PROFILES-CONTRACT rule 3; SkyyTrees republishes it within 1 s of a switch). Non-numbers, NaN
# and infinities are skipped; the key is xp. / dd. + the slot NAME in lower case (mining, foraging, farming, cooking, alchemy, ...).
sbn.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap FAILED = new java.util.concurrent.ConcurrentHashMap();", sbn))
sbn.addMethod(CtNewMethod.make(f"""
public static java.util.Map sources(java.util.UUID u) {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("skill:bonus:" + u.toString());
    if (o instanceof java.util.Map) return (java.util.Map) o;
  }} catch (Throwable t) {{ }}
  return null;
}}""", sbn))
sbn.addMethod(CtNewMethod.make(f"""
public static double sum(java.util.UUID u, String key) {{
  if (u == null || !{PKG}.BridgeCfg.BONUS) return 0.0;
  java.util.Map m = sources(u);
  if (m == null) return 0.0;
  double s = 0.0;
  try {{
    java.util.Iterator it = m.values().iterator();
    while (it.hasNext()) {{
      Object v = it.next();
      if (!(v instanceof java.util.Map)) continue;
      Object n = ((java.util.Map) v).get(key);
      if (!(n instanceof Number)) continue;
      double d = ((Number) n).doubleValue();
      if (Double.isNaN(d) || Double.isInfinite(d)) continue;
      s = s + d;
    }}
  }} catch (Throwable t) {{ return 0.0; }}
  return s;
}}""", sbn))
sbn.addMethod(CtNewMethod.make(f"""
public static String key(int slot) {{
  return {PKG}.SkillDefs.NAMES[slot].toLowerCase(java.util.Locale.ROOT);
}}""", sbn))
# XP bonus fraction of one slot: only slots listed in bridge.bonus.xpSkills, sum over all sources clamped 0..5 (spec 9.3)
sbn.addMethod(CtNewMethod.make(f"""
public static double xpBonus(java.util.UUID u, int slot) {{
  if (slot < 0 || slot >= {PKG}.SkillDefs.N) return 0.0;
  if (!{PKG}.SkillDefs.boostable(slot)) return 0.0;
  boolean[] on = {PKG}.BridgeCfg.BONUS_XP;
  if (slot >= on.length || !on[slot]) return 0.0;
  double s = sum(u, "xp." + key(slot));
  if (s <= 0.0) return 0.0;
  return s > 5.0 ? 5.0 : s;
}}""", sbn))
# amount x (1 + bonus); the fraction is paid by chance (stone pays 1 XP: +15% must still add 0.15 XP per block on average)
sbn.addMethod(CtNewMethod.make(f"""
public static long boost(java.util.UUID u, int slot, long amt) {{
  if (amt <= 0L) return amt;
  double b = xpBonus(u, slot);
  if (b <= 0.0) return amt;
  double x = (double) amt * (1.0 + b);
  if (x >= 9.0E15) return amt;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w < amt ? amt : w;
}}""", sbn))
# skill:fn:addxp = XP another mod GRANTS (SkyyCollections tier rewards, SkyyCooking dishes): the tree XP bonus only for the skills in
# bridge.bonus.addxpSkills (default Cooking). XP the player earns (gain2, skill:fn:craftxp) follows bridge.bonus.xpSkills alone.
sbn.addMethod(CtNewMethod.make(f"""
public static boolean grantBonus(int slot) {{
  boolean[] g = {PKG}.BridgeCfg.BONUS_ADDXP;
  return slot >= 0 && slot < g.length && g[slot];
}}""", sbn))
# double-drop fraction the trees add for a gathering row (0 = Mining, 1 = Foraging, 2 = Farming), clamped 0..1
sbn.addMethod(CtNewMethod.make(f"""
public static double dd(java.util.UUID u, int row) {{
  if (row < 0 || row > {PKG}.SkillDefs.FARMING) return 0.0;
  double s = sum(u, "dd." + key(row));
  if (s <= 0.0) return 0.0;
  return s > 1.0 ? 1.0 : s;
}}""", sbn))
# SkyyTrees publishes tree:fn:level in its setup and removes it in its shutdown: its presence = the trees are installed
sbn.addMethod(CtNewMethod.make(f"""
public static boolean treesOn() {{
  try {{ return {PKG}.SkillStore.bridge().get("tree:fn:level") instanceof java.util.function.Function; }} catch (Throwable t) {{ return false; }}
}}""", sbn))
# /tree argument of a slot (SkyyTrees 0.1 trees: mining, foraging, farming, cooking; SkyyTrees 0.2 adds acrobatics, exploration);
# null = no tree for that skill. Whether the RUNNING SkyyTrees has that tree = treeAvailable (0.4.1, below).
sbn.addMethod(CtNewMethod.make(f"""
public static String treeName(int slot) {{
  if (slot == {PKG}.SkillDefs.MINING) return "mining";
  if (slot == {PKG}.SkillDefs.FORAGING) return "foraging";
  if (slot == {PKG}.SkillDefs.FARMING) return "farming";
  if (slot == {PKG}.SkillDefs.COOKING) return "cooking";
  if (slot == {PKG}.SkillDefs.ACROBATICS) return "acrobatics";
  if (slot == {PKG}.SkillDefs.EXPLORATION) return "exploration";
  return null;
}}""", sbn))
# 0.4.1: a Tree button for this slot? SkyyTrees running (tree:fn:level) AND its bridge tree:names (SkyyTrees 0.2: comma list of tree
# labels) lists the slot; without tree:names (SkyyTrees 0.1) only its four trees - exactly the 0.4 buttons
sbn.addMethod(CtNewMethod.make(f"""
public static boolean treeAvailable(int slot) {{
  if (slot < 0 || slot >= {PKG}.SkillDefs.N || treeName(slot) == null || !treesOn()) return false;
  Object o = null;
  try {{ o = {PKG}.SkillStore.bridge().get("tree:names"); }} catch (Throwable t) {{ }}
  if (!(o instanceof String)) return slot == {PKG}.SkillDefs.MINING || slot == {PKG}.SkillDefs.FORAGING || slot == {PKG}.SkillDefs.FARMING || slot == {PKG}.SkillDefs.COOKING;
  String[] ps = ((String) o).split(",");
  for (int i = 0; i < ps.length; i++) {{
    String nm = ps[i].trim();
    if (nm.equalsIgnoreCase({PKG}.SkillDefs.LABELS[slot]) || nm.equalsIgnoreCase({PKG}.SkillDefs.NAMES[slot])) return true;
  }}
  return false;
}}""", sbn))
# page click (world thread): run /tree <skill> as the player; the tree page replaces this page (never close a page first)
sbn.addMethod(CtNewMethod.make(f"""
public static void openTree({PR} pr, String tree) {{
  if (pr == null || tree == null) return;
  if (!treesOn()) {{ pr.sendMessage({MSG}.raw("[Skills] Skill trees need SkyyTrees - it is not running on this server").color("#ffb080")); return; }}
  try {{
    {CMGR}.get().handleCommand(pr, "tree " + tree);
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("could not run /tree " + tree + ": " + t);
    pr.sendMessage({MSG}.raw("[Skills] Could not open the skill tree - try /tree " + tree).color("#ffb080"));
  }}
}}""", sbn))
sbn.addMethod(CtNewMethod.make(f"""
public static void failed(Object name, Throwable t) {{
  String n = String.valueOf(name);
  if (FAILED.putIfAbsent(n, Boolean.TRUE) == null) {PKG}.SkillCfg.warn("skill:on:gather listener '" + n + "' failed (logged once per listener): " + t);
}}""", sbn))
# world thread, right after a gathering block (row 0-2) or an F-harvest (harvest = true) PAID XP; every listener gets its own argument
# array and its own try/catch, so one broken listener never stops the others or the award
sbn.addMethod(CtNewMethod.make(f"""
public static void gather({PR} pr, int row, {BTY} bt, String world, boolean harvest, int x, int y, int z) {{
  if (pr == null || row < 0 || row > {PKG}.SkillDefs.FARMING) return;
  java.util.ArrayList names = new java.util.ArrayList();
  java.util.ArrayList fns = new java.util.ArrayList();
  try {{
    Object o = {PKG}.SkillStore.bridge().get("skill:on:gather");
    if (!(o instanceof java.util.Map)) return;
    java.util.Iterator it = ((java.util.Map) o).entrySet().iterator();
    while (it.hasNext()) {{
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      if (e.getValue() instanceof java.util.function.Function) {{ names.add(e.getKey()); fns.add(e.getValue()); }}
    }}
  }} catch (Throwable t) {{ return; }}
  for (int i = 0; i < fns.size(); i++) {{
    try {{
      ((java.util.function.Function) fns.get(i)).apply(new Object[] {{ pr, Integer.valueOf(row), bt, world, Boolean.valueOf(harvest), Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z) }});
    }} catch (Throwable t) {{ failed(names.get(i), t); }}
  }}
}}""", sbn))
# 0.4.2 (Tree-Fall-Spec 2.8): skill:on:felled - a SEPARATE map from skill:on:gather (an old SkyyTrees never sees felled logs and can never
# start an ability from one). World thread, once per credited felled position, after its XP and double drop; every listener gets its own
# argument array Object[]{PlayerRef, Integer row, BlockType, String world, Integer x, Integer y, Integer z, String pkey} and its own
# try/catch; a failure is logged once per listener.
sbn.addMethod(CtNewMethod.make(f"""
public static void failedFelled(Object name, Throwable t) {{
  String n = String.valueOf(name);
  if (FAILED.putIfAbsent("felled:" + n, Boolean.TRUE) == null) {PKG}.SkillCfg.warn("skill:on:felled listener '" + n + "' failed (logged once per listener): " + t);
}}""", sbn))
sbn.addMethod(CtNewMethod.make(f"""
public static void felled({PR} pr, int row, {BTY} bt, String world, int x, int y, int z, String pkey) {{
  if (pr == null) return;
  java.util.ArrayList names = new java.util.ArrayList();
  java.util.ArrayList fns = new java.util.ArrayList();
  try {{
    Object o = {PKG}.SkillStore.bridge().get("skill:on:felled");
    if (!(o instanceof java.util.Map)) return;
    java.util.Iterator it = ((java.util.Map) o).entrySet().iterator();
    while (it.hasNext()) {{
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      if (e.getValue() instanceof java.util.function.Function) {{ names.add(e.getKey()); fns.add(e.getValue()); }}
    }}
  }} catch (Throwable t) {{ return; }}
  for (int i = 0; i < fns.size(); i++) {{
    try {{
      ((java.util.function.Function) fns.get(i)).apply(new Object[] {{ pr, Integer.valueOf(row), bt, world, Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z), pkey }});
    }} catch (Throwable t) {{ failedFelled(names.get(i), t); }}
  }}
}}""", sbn))

# ================= PartyXp chat (0.4.2 stage 2) - BEFORE SkillXp: SkillXp.gain4 calls PartyXp.note and its level-up branch PartyXp.send =================
# Chat: PEND uuid -> long[N + 1] (XP per slot, [N] = number of shares), WHO uuid -> killer name ("" = several), LAST uuid -> ms of the last
# line: "[Party] +6 Archery XP (340/500) from Skyy's kill", sent at most once per feedbackMs (SkillMsg's throttle), leftovers by the
# 1 s ticker (flushDue -> PartyFlushTask on the member's world thread). /skills quiet, feedback=false, party.combatShare.message=false hide it.
# Review fix (level-up order): gain4 notes the share right after the XP is added (exactly where gain3 calls SkillMsg.note) and a level up
# flushes this queue right after SkillMsg's, so the "[Party] +N ... XP" line always prints BEFORE the SKILL LEVEL UP it causes.
pxp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();", pxp))
pxp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap WHO = new java.util.concurrent.ConcurrentHashMap();", pxp))
pxp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();", pxp))
# chat batching (synchronized methods, never a multi-statement synchronized block)
pxp.addMethod(CtNewMethod.make(f"""
public static synchronized boolean add(java.util.UUID u, int slot, long amt, String from) {{
  String fr = from == null ? "" : from;
  long[] p = (long[]) PEND.get(u);
  if (p == null) {{
    p = new long[{PKG}.SkillDefs.N + 1];
    PEND.put(u, p);
    WHO.put(u, fr);
  }} else {{
    Object w = WHO.get(u);
    if (!(w instanceof String) || !((String) w).equals(fr)) WHO.put(u, "");
  }}
  p[slot] += amt;
  p[{PKG}.SkillDefs.N] += 1L;
  Long last = (Long) LAST.get(u);
  return last == null || System.currentTimeMillis() - last.longValue() >= {PKG}.SkillCfg.FEEDBACK_MS;
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static synchronized String take(java.util.UUID u) {{
  long[] p = (long[]) PEND.get(u);
  if (p == null) return null;
  Object wo = WHO.get(u);
  String who = wo instanceof String ? (String) wo : "";
  PEND.remove(u);
  WHO.remove(u);
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  long[] d = {PKG}.SkillStore.data(u);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
    if (p[i] <= 0L) continue;
    if (sb.length() > 0) sb.append("    ");
    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillClass.skillName(u, i)).append(" XP (").append({PKG}.SkillDefs.progress(i, d[i])).append(")");
  }}
  if (sb.length() == 0) return null;
  long n = p[{PKG}.SkillDefs.N];
  String src;
  if (who.length() > 0) src = n > 1L ? n + " kills by " + who : who + "'s kill";
  else src = n + " party kills";
  return "[Party] " + sb.toString() + " from " + src;
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static void send({PR} pr) {{
  try {{
    String s = take(pr.getUuid());
    if (s != null) pr.sendMessage({MSG}.raw(s).color("#a8e8c0"));
  }} catch (Throwable t) {{ }}
}}""", pxp))
pxp.addMethod(CtNewMethod.make("""
public static synchronized void drop(java.util.UUID u) {
  PEND.remove(u);
  WHO.remove(u);
  LAST.remove(u);
}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static void note({PR} pr, int slot, long amt, String from) {{
  if (!{PKG}.PartyCfg.MESSAGE || !{PKG}.SkillCfg.FEEDBACK || pr == null || amt <= 0L) return;
  if (slot < 0 || slot >= {PKG}.SkillDefs.N) return;
  java.util.UUID u = pr.getUuid();
  if (!{PKG}.SkillStore.notifyOn(u, "skills.xpGain")) return;
  if (add(u, slot, amt, from)) send(pr);
}}""", pxp))

# ================= Xbow part 1 (0.4.5): crossbows stay loaded - the flag, config helpers, texts (research/Crossbow-Loaded-Spec.md 2.2 / 3.4) ==
# S: UUID -> XbowState (memory only). ON: UUID -> Boolean, the CACHED perk flag (spec 2.2 rules 1-3) - it only decides when to remember and
# arm, never a payout (Xbow.eligibleNow is computed live right before arrows are taken). Both pruned to online players by Acro.retainOnline.
xbw.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap S = new java.util.concurrent.ConcurrentHashMap();", xbw))
xbw.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ON = new java.util.concurrent.ConcurrentHashMap();", xbw))
xbw.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap FAILED = new java.util.concurrent.ConcurrentHashMap();", xbw))
xbw.addField(CtField.make('public static final String ARROW = "Weapon_Arrow_Crude";', xbw))
xbw.addField(CtField.make('public static final String TEXT = "Crossbows stay loaded when you switch slots";', xbw))
xbw.addField(CtField.make('public static final String UNLOCK = "Unlocked: Crossbows stay loaded when you switch slots";', xbw))
xbw.addField(CtField.make('public static final String CHARGES = "SignatureCharges";', xbw))   # 0.4.6: no DefaultEntityStatTypes getter for it
# one server-log warning per failing method (the AcroSys FAILED_ONCE rule)
xbw.addMethod(CtNewMethod.make(f"""
public static void failed(String what, Throwable t) {{
  if (FAILED.putIfAbsent(what, Boolean.TRUE) == null) {PKG}.SkillCfg.warn("crossbows stay loaded: " + what + " failed (logged once): " + t);
}}""", xbw))
xbw.addMethod(CtNewMethod.make(f"""
public static {PKG}.XbowState state(java.util.UUID u) {{
  {PKG}.XbowState s = ({PKG}.XbowState) S.get(u);
  if (s != null) return s;
  {PKG}.XbowState n = new {PKG}.XbowState();
  Object o = S.putIfAbsent(u, n);
  return o == null ? n : ({PKG}.XbowState) o;
}}""", xbw))
xbw.addMethod(CtNewMethod.make("""
public static void forget(java.util.UUID u) {
  if (u != null) S.remove(u);
}""", xbw))
xbw.addMethod(CtNewMethod.make("""
public static void retain(java.util.Set online) {
  S.keySet().retainAll(online);
  ON.keySet().retainAll(online);
}""", xbw))
# PROFILES-CONTRACT rule 5: no item moves while the live inventory may belong to another profile (an unreadable bridge = busy)
xbw.addMethod(CtNewMethod.make(f"""
public static boolean busy(java.util.UUID u) {{
  try {{
    return Boolean.TRUE.equals({PKG}.SkillStore.bridge().get("profile:busy:" + u.toString()));
  }} catch (Throwable t) {{ return true; }}
}}""", xbw))
# spec 2.2 rules 1-3, uncached: part switch on, class Archer (and SkyyClasses follows the profile), Archery on the ACTIVE profile >= level
xbw.addMethod(CtNewMethod.make(f"""
public static boolean rules(java.util.UUID u) {{
  try {{
    if (u == null || !{PKG}.XbowCfg.ON) return false;
    int a = {PKG}.SkillClass.slotOfClass("Archer");
    if (a < 0 || {PKG}.SkillClass.slot(u) != a) return false;
    if (!{PKG}.SkillClass.consistent(u)) return false;
    return {PKG}.SkillStore.level(u, a) >= {PKG}.XbowCfg.LEVEL;
  }} catch (Throwable t) {{ failed("rules", t); return false; }}
}}""", xbw))
# the cached flag: every second (Perks.tick), after a level up (SkillXp.gain4), after a profile switch (Perks.switched); off = state dropped
xbw.addMethod(CtNewMethod.make("""
public static void refresh(java.util.UUID u) {
  if (u == null) return;
  boolean on = rules(u);
  ON.put(u, on ? Boolean.TRUE : Boolean.FALSE);
  if (!on) forget(u);
}""", xbw))
xbw.addMethod(CtNewMethod.make("""
public static boolean active(java.util.UUID u) {
  return u != null && Boolean.TRUE.equals(ON.get(u)) && !busy(u);
}""", xbw))
# the weapon rule: a crossbow id (perk.archery.keepLoaded.items) that SkyyClasses allows this player (class:fn:allowed, SkillClass.itemOk)
xbw.addMethod(CtNewMethod.make(f"""
public static boolean allowed(java.util.UUID u, String id) {{
  try {{
    if (!{PKG}.XbowCfg.isCrossbow(id)) return false;
    java.util.function.Function f = {PKG}.SkillClass.allowedFn();
    if (f == null) return true;
    return Boolean.TRUE.equals(f.apply(new Object[] {{ u, id }}));
  }} catch (Throwable t) {{ return false; }}
}}""", xbw))
# right before arrows are taken (spec 2.5 step 3): rules 1-4 + the weapon rule, never the cache
xbw.addMethod(CtNewMethod.make("""
public static boolean eligibleNow(java.util.UUID u, String id) {
  return rules(u) && !busy(u) && allowed(u, id);
}""", xbw))
# Stats page (spec 3.7): the Archery "Boosts right now" line from the unlock level, the "Level L adds" line one level before
xbw.addMethod(CtNewMethod.make(f"""
public static String line(java.util.UUID u, int s, int lv, boolean next) {{
  try {{
    if (!{PKG}.XbowCfg.ON || s < 0 || s != {PKG}.SkillClass.slotOfClass("Archer")) return null;
    String tx = ({PKG}.XbowCfg.METER && {PKG}.SkillStore.notifyOn(u, "skills.xbowMeter")) ? TEXT + " (bolts and big-arrow meter)" : TEXT;
    if (!next && lv >= {PKG}.XbowCfg.LEVEL) return tx;
    if (next && lv + 1 == {PKG}.XbowCfg.LEVEL) return tx;
  }} catch (Throwable t) {{ failed("stats line", t); }}
  return null;
}}""", xbw))
# wipe every kept load and the armed restore; a later leave must first be held delayTicks again (the Ammo read may be stale right after)
xbw.addMethod(CtNewMethod.make(f"""
public static void reset({PKG}.XbowState s) {{
  for (int i = 0; i < s.n.length; i++) {{ s.n[i] = 0; s.stk[i] = null; s.cre[i] = false; s.sig[i] = 0.0f; s.chg[i] = 0.0f; }}
  s.pendSlot = -1;
  s.pendAt = 0L;
  s.enterAt = s.ticks;
}}""", xbw))
xbw.addMethod(CtNewMethod.make(f"""
public static void drop({PKG}.XbowState s, int slot) {{
  if (slot >= 0 && slot < s.n.length) {{ s.n[slot] = 0; s.stk[slot] = null; s.cre[slot] = false; s.sig[slot] = 0.0f; s.chg[slot] = 0.0f; }}
  s.pendSlot = -1;
}}""", xbw))
# perk.archery.keepLoaded.debug: admins only (the acro.doubleJump.debug rule), at most one line per event
xbw.addMethod(CtNewMethod.make(f"""
public static void dbg({PR} pr, String text) {{
  if (!{PKG}.XbowCfg.DEBUG || pr == null) return;
  try {{
    if (!pr.hasPermission("skyyskills.admin")) return;
    pr.sendMessage({MSG}.raw("[Skills debug] " + text).color("#c8a0ff"));
  }} catch (Throwable t) {{ }}
}}""", xbw))
# ---- 0.4.6 (LOCKED Skyy 2026-09-25): loads survive world changes, the big-arrow meter, the sound + chat hint ----
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

# ================= ClassCurve (0.4.12): the one-time class skill curve notice + the level-up rewards of the levels the new curve gave ==========
# FILE = Skyy_SkyySkills/class-curve.properties. The FIRST start of 0.4.12 (no file) scans every players/*.properties once (read-only) and
# records pending.<profile key>=<slot>:<level before>:<level now> for each class slot whose level on the class table is above its level on
# the general table (= what 0.4.11 showed); later starts read the file. PENDING / DONE = the records in memory; READY = the file is on
# disk (only then is anybody told); DIRTY = the file must be rewritten (SkillTick flush); SAVE = delivered profile keys whose player file
# is saved before that rewrite (so "done" is never on disk before their paid markers).
ccv.addField(CtField.make("public static java.nio.file.Path FILE;", ccv))
ccv.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();", ccv))
ccv.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DONE = new java.util.concurrent.ConcurrentHashMap();", ccv))
ccv.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SAVE = new java.util.concurrent.ConcurrentHashMap();", ccv))
ccv.addField(CtField.make("public static volatile boolean READY = false;", ccv))
ccv.addField(CtField.make("public static volatile boolean DIRTY = false;", ccv))
ccv.addField(CtField.make("public static volatile String SCANNED = null;", ccv))
ccv.addField(CtField.make('public static final String NAME = "class-curve.properties";', ccv))
ccv.addField(CtField.make('public static final String HEAD1 = "# SkyySkills class skill curve update (0.4.12, Skyy 2026-10-02) - written once at the first start of 0.4.12; do not edit (deleted = the next start scans again: the line again, never the coins)";', ccv))
ccv.addField(CtField.make('public static final String HEAD2 = "# pending.<profile key> = class slot:level before:level now - told and paid the next time that profile plays; done.<profile key> = told";', ccv))
ccv.addMethod(CtNewMethod.make("""
public static String stamp() {
  return new java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss").format(new java.util.Date());
}""", ccv))
ccv.addMethod(CtNewMethod.make("""
public static String one(Object v) {
  return String.valueOf(v).replace('\\n', ' ').replace('\\r', ' ');
}""", ccv))
# one player file -> "slot:old:new,..." for every class slot whose level on the effective class table is above its level on the general
# table, "" = none. Pure (reads only the Properties and the loaded tables), any thread.
ccv.addMethod(CtNewMethod.make(f"""
public static String rises(java.util.Properties p) {{
  StringBuilder sb = new StringBuilder();
  for (int j = 0; j < {PKG}.SkillDefs.CLASS_SLOT.length; j++) {{
    int s = {PKG}.SkillDefs.CLASS_SLOT[j];
    long x = 0L;
    try {{ x = Long.parseLong(String.valueOf(p.getProperty({PKG}.SkillDefs.NAMES[s], "0")).trim()); }} catch (Throwable t) {{ x = 0L; }}
    if (x <= 0L) continue;
    int old = {PKG}.SkillDefs.generalLevel(x);
    int nw = {PKG}.SkillDefs.levelOf(s, x);
    if (nw <= old) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(s).append(':').append(old).append(':').append(nw);
  }}
  return sb.toString();
}}""", ccv))
# the whole file, atomically (tmp + the SkillStore move). DIRTY is cleared BEFORE the snapshot, so a change made while this runs is written
# by the next flush; a failure sets it again.
ccv.addMethod(CtNewMethod.make(f"""
public static synchronized boolean write() {{
  DIRTY = false;
  try {{
    StringBuilder sb = new StringBuilder();
    sb.append(HEAD1).append('\\n').append(HEAD2).append('\\n');
    sb.append("scanned=").append(one(SCANNED == null ? "" : SCANNED)).append('\\n');
    java.util.Iterator it = new java.util.TreeMap(PENDING).entrySet().iterator();
    while (it.hasNext()) {{
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      sb.append("pending.").append(e.getKey()).append('=').append(one(e.getValue())).append('\\n');
    }}
    it = new java.util.TreeMap(DONE).entrySet().iterator();
    while (it.hasNext()) {{
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      sb.append("done.").append(e.getKey()).append('=').append(one(e.getValue())).append('\\n');
    }}
    java.nio.file.Path tmp = FILE.resolveSibling(NAME + ".tmp");
    java.nio.file.Files.write(tmp, sb.toString().getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    {PKG}.SkillStore.moveRetry(tmp, FILE);
    return true;
  }} catch (Throwable t) {{
    DIRTY = true;
    {PKG}.SkillCfg.warn("could not write " + NAME + " (retried): " + t);
    return false;
  }}
}}""", ccv))
# setup(), right after SkillCfg.load (the tables are loaded) and before any player joins. Returns the INFO text ("" = nothing to say).
ccv.addMethod(CtNewMethod.make(f"""
public static synchronized String start(java.nio.file.Path base) {{
  PENDING.clear();
  DONE.clear();
  SAVE.clear();
  READY = false;
  DIRTY = false;
  SCANNED = null;
  if (base == null) return "";
  FILE = base.resolve(NAME);
  try {{
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {{
      java.util.Properties p = {PKG}.SkillStore.readLocked(FILE);
      java.util.Iterator it = p.stringPropertyNames().iterator();
      while (it.hasNext()) {{
        String k = (String) it.next();
        String v = p.getProperty(k);
        if (k.startsWith("pending.") && k.length() > 8) PENDING.put(k.substring(8), v);
        else if (k.startsWith("done.") && k.length() > 5) DONE.put(k.substring(5), v);
      }}
      SCANNED = p.getProperty("scanned");
      if (SCANNED == null || SCANNED.trim().length() == 0) {{
        PENDING.clear();
        {PKG}.SkillCfg.warn(NAME + " has no scanned= line - nobody is told about the class skill curve (delete the file to scan again)");
        return "";
      }}
      READY = true;
      return PENDING.isEmpty() ? "" : "class skill curve: " + PENDING.size() + " profile(s) still to be told";
    }}
    int files = 0;
    int bad = 0;
    java.io.File[] fs = null;
    if ({PKG}.SkillStore.DIR != null) fs = {PKG}.SkillStore.DIR.toFile().listFiles();
    if (fs != null) for (int i = 0; i < fs.length; i++) {{
      String fn = fs[i].getName();
      if (!fn.endsWith(".properties") || !fs[i].isFile()) continue;
      String k = fn.substring(0, fn.length() - 11);
      try {{
        java.util.Properties p = {PKG}.SkillStore.readLocked(fs[i].toPath());
        files++;
        String r = rises(p);
        if (r.length() > 0) PENDING.put(k, r);
      }} catch (Throwable t) {{
        bad++;
        {PKG}.SkillCfg.warn("class skill curve: could not read " + fn + " (" + t + ") - that profile is not told");
      }}
    }}
    SCANNED = stamp() + " " + files + " profile file(s)" + (bad > 0 ? ", " + bad + " unreadable" : "");
    if (!write()) {{
      PENDING.clear();
      DIRTY = false;
      {PKG}.SkillCfg.warn("class skill curve: " + NAME + " could not be written - nobody is told this run; the next start scans again");
      return "";
    }}
    READY = true;
    String msg = "class skill curve (first start of 0.4.12): " + files + " profile file(s) scanned, " + PENDING.size() + " with a higher class level now - each is told and paid once, the next time it plays";
    {PKG}.SkillCfg.info(msg);
    return msg;
  }} catch (Throwable t) {{
    READY = false;
    DIRTY = false;
    {PKG}.SkillCfg.warn("class skill curve: start failed (nobody is told this run): " + t);
    return "";
  }}
}}""", ccv))
# world thread, the profile's first second on 0.4.12 (Perks.tick) or right before a class skill XP award (SkillXp.gain4): claim the entry
# (PENDING.remove = exactly once), then: the level-up coin rewards of the gained levels through the paid marker (payOwedK - coins only
# move the marker once SkyyCoins paid, so nothing is ever paid twice; unpaid levels stay owed for the normal late payout), ONE chat line,
# the crossbow unlock line (Archery passing its unlock level), the Overall level up (chat + heal, Overall.levelUp), a republish.
ccv.addMethod(CtNewMethod.make(f"""
public static void deliver({PR} pr, java.util.UUID u, String k, String e) {{
  try {{
    long[] d = {PKG}.SkillStore.dataK(k, u);
    String[] parts = e.split(",");
    int[] sl = new int[parts.length];
    int[] was = new int[parts.length];
    int[] now = new int[parts.length];
    int n = 0;
    StringBuilder lines = new StringBuilder();
    StringBuilder sum = new StringBuilder();
    long coins = 0L;
    long first = -1L;
    long last = -1L;
    for (int i = 0; i < parts.length; i++) {{
      String[] f = parts[i].trim().split(":");
      if (f.length < 3) continue;
      int s = -1;
      int old = 0;
      try {{ s = Integer.parseInt(f[0].trim()); old = Integer.parseInt(f[1].trim()); }} catch (Throwable t) {{ s = -1; }}
      if (!{PKG}.SkillDefs.isClass(s)) continue;
      int lv = {PKG}.SkillDefs.levelOf(s, {PKG}.SkillStore.rd(d, s));
      if (lv <= old) continue;
      long[] paid = null;
      if ({PKG}.SkillStore.owesK(k, u, s)) paid = {PKG}.SkillStore.payOwedK(k, u, s);
      if (paid != null) {{
        coins += paid[2];
        if (first < 0L || paid[0] < first) first = paid[0];
        if (paid[1] > last) last = paid[1];
      }}
      if (lines.length() > 0) lines.append(", ");
      lines.append({PKG}.SkillClass.skillName(u, s)).append(" is now level ").append(lv).append(" (was ").append(old).append(")");
      if (sum.length() > 0) sum.append(", ");
      sum.append({PKG}.SkillDefs.NAMES[s]).append(' ').append(old).append(" -> ").append(lv);
      sl[n] = s;
      was[n] = old;
      now[n] = lv;
      n++;
    }}
    if (n == 0) {{
      DONE.put(k, stamp() + " nothing to tell (no class level above its old level any more)");
      DIRTY = true;
      return;
    }}
    String c = "";
    if (coins > 0L) c = n == 1 ? " - +" + {PKG}.SkillDefs.fmt(coins) + " coins for " + (first == last ? "level " + first : "levels " + first + " to " + last) : " - +" + {PKG}.SkillDefs.fmt(coins) + " coins for the new levels";
    pr.sendMessage({MSG}.raw("[Skills] Class skill curve updated: " + lines.toString() + c).color("#ffc800"));
    boolean lvOn = {PKG}.SkillStore.notifyOn(u, "skills.levelUp");
    int archer = {PKG}.SkillClass.slotOfClass("Archer");
    for (int i = 0; i < n; i++) {{
      if (lvOn && sl[i] == archer && {PKG}.XbowCfg.ON && {PKG}.XbowCfg.LEVEL >= 1 && was[i] < {PKG}.XbowCfg.LEVEL && now[i] >= {PKG}.XbowCfg.LEVEL) pr.sendMessage({MSG}.raw("  " + {PKG}.Xbow.UNLOCK).color("#ffc800"));
      {PKG}.Overall.levelUp(pr, u, sl[i], (long) was[i], (long) now[i]);
    }}
    {PKG}.Xbow.refresh(u);
    {PKG}.SkillStore.publish(u);
    {PKG}.SkillStore.DIRTY.put(k, Boolean.TRUE);
    SAVE.put(k, Boolean.TRUE);
    DONE.put(k, stamp() + " " + sum.toString() + (coins > 0L ? " +" + coins + " coins" : ""));
    DIRTY = true;
    {PKG}.SkillCfg.info("class skill curve: told " + k + " - " + sum.toString() + (coins > 0L ? ", paid " + coins + " coins" : ""));
  }} catch (Throwable t) {{
    DONE.put(k, stamp() + " failed: " + t);
    DIRTY = true;
    {PKG}.SkillCfg.warn("class skill curve notice failed for " + k + ": " + t);
  }}
}}""", ccv))
# world thread: nothing pending (every second for every player after the first ones: one isEmpty) / not ready / another profile -> return;
# waits while profile:busy (a profile switch moves the live inventory and purse: PROFILES-CONTRACT rule 5) and while Overall's session hold
# runs (the first seconds of a session before SkyyClasses published the class - Overall.levelUp needs it)
ccv.addMethod(CtNewMethod.make(f"""
public static void tick({PR} pr, java.util.UUID u) {{
  if (!READY || PENDING.isEmpty() || pr == null || u == null) return;
  String k = {PKG}.SkillStore.pkey(u);
  Object e = PENDING.get(k);
  if (!(e instanceof String)) return;
  if ({PKG}.Xbow.busy(u)) return;
  if ({PKG}.Overall.hold(u, pr, System.currentTimeMillis())) return;
  if (PENDING.remove(k) == null) return;
  deliver(pr, u, k, (String) e);
}}""", ccv))
# scheduler thread (SkillTick, every second) + shutdown: the delivered profiles' player files first, then the record
ccv.addMethod(CtNewMethod.make(f"""
public static void flush() {{
  if (!READY || !DIRTY) return;
  java.util.Iterator it = new java.util.ArrayList(SAVE.keySet()).iterator();
  boolean ok = true;
  while (it.hasNext()) {{
    String k = (String) it.next();
    SAVE.remove(k);
    if (!{PKG}.SkillStore.save(k)) {{ SAVE.put(k, Boolean.TRUE); ok = false; }}
  }}
  if (ok) write();
}}""", ccv))

# ================= GatherPace.apply (0.4.14): earned gathering XP x the pace multiplier of the skill's CURRENT level (world thread: SkillXp.gain4's
# bonus path - blocks, F-harvests, sickle swings - and FellCredit.one - felled logs), BEFORE the tree Wisdom bonus. Any other slot, or a
# multiplier of exactly 1, returns amt unchanged (no rounding); the fraction is paid by chance (a product within 1e-9 of a whole number
# counts as that number: 2.55 x 20 = 51, never 52)
gpc.addMethod(CtNewMethod.make(J14(r"""
public static long apply(java.util.UUID u, int slot, long amt) {
  if (amt <= 0L || u == null || !on(slot)) return amt;
  double m = mult(@PKG@.SkillStore.level(u, slot));
  if (m == 1.0) return amt;
  if (!(m > 0.0)) return 0L;
  double x = (double) amt * m;
  if (x >= 9.0E15) return 9000000000000000L;
  double r = Math.rint(x);
  if (Math.abs(x - r) < 1.0E-9) x = r;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}"""), gpc))
# the Stats page's "Boosts right now" line of a paced skill (null = no line: not listed, or x1 at this level)
gpc.addMethod(CtNewMethod.make(J14(r"""
public static String statsLine(int slot, int lv) {
  if (!on(slot)) return null;
  double m = mult(lv);
  if (m == 1.0) return null;
  String x = @PKG@.DivCfg.num(m);
  if (lv <= UNTIL) {
    if (LATE == EARLY) return "Gathering XP x" + x;
    if (FROM > UNTIL + 1) return "Gathering XP x" + x + " up to level " + UNTIL + ", then easing to x" + @PKG@.DivCfg.num(LATE) + " by level " + FROM;
    return "Gathering XP x" + x + " up to level " + UNTIL + ", then x" + @PKG@.DivCfg.num(LATE);
  }
  if (lv < FROM) return "Gathering XP x" + x + " now - easing to x" + @PKG@.DivCfg.num(LATE) + " by level " + FROM;
  return "Gathering XP x" + x + " (gathering pace)";
}"""), gpc))

# ================= SkillXp: award + level-up (world thread) =================
xp.addMethod(CtNewMethod.make(f"""
public static boolean creative({ST} st, {REF} r) {{
  if ({PKG}.SkillCfg.CREATIVE) return false;
  try {{
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    return p != null && p.getGameMode() == {GM}.Creative;
  }} catch (Throwable t) {{ return false; }}
}}""", xp))
xp.addMethod(CtNewMethod.make(f"""
public static void gain4({PR} pr, int skill, long amount, boolean note, boolean bonus, String party) {{
  if (pr == null || amount <= 0L || skill < 0 || skill >= {PKG}.SkillDefs.N) return;
  java.util.UUID u = pr.getUuid();
  if ({PKG}.SkillDefs.isClass(skill)) {PKG}.ClassCurve.tick(pr, u);   // 0.4.12: a pending class skill curve notice comes first (once)
  if (bonus) amount = {PKG}.SkillBonus.boost(u, skill, {PKG}.GatherPace.apply(u, skill, amount));   // 0.4.14: the gathering pace, then the tree Wisdom
  if (amount <= 0L) return;
  String k = {PKG}.SkillStore.pkey(u);
  String name = null;
  try {{ name = pr.getUsername(); }} catch (Throwable t) {{ }}
  long[] r = {PKG}.SkillStore.addK(k, u, name, skill, amount);
  if (note) {PKG}.SkillMsg.note(pr, skill, amount);
  if (party != null) {PKG}.PartyXp.note(pr, skill, amount, party);
  long[] paid = null;
  if ({PKG}.SkillStore.owesK(k, u, skill)) paid = {PKG}.SkillStore.payOwedK(k, u, skill);
  String sk = {PKG}.SkillDefs.LABELS[skill];
  long shown = 0L;
  if (r[1] > r[0]) {{
    {PKG}.SkillMsg.send(pr);
    {PKG}.PartyXp.send(pr);
    boolean lvOn = {PKG}.SkillStore.notifyOn(u, "skills.levelUp");
    for (long lv = r[0] + 1L; lv <= r[1]; lv++) {{
      String reward = "";
      if (paid != null && lv >= paid[0] && lv <= paid[1]) {{
        long coins = paid[3] * lv;
        shown += coins;
        reward = "   +" + {PKG}.SkillDefs.fmt(coins) + " coins";
      }}
      if (lvOn) pr.sendMessage({MSG}.raw("SKILL LEVEL UP  " + sk + " " + (lv - 1L) + " -> " + lv + reward).color("#ffc800"));
      if (lvOn && skill == {PKG}.SkillClass.slotOfClass("Archer") && {PKG}.XbowCfg.ON && {PKG}.XbowCfg.LEVEL >= 1 && lv == (long) {PKG}.XbowCfg.LEVEL) pr.sendMessage({MSG}.raw("  " + {PKG}.Xbow.UNLOCK).color("#ffc800"));
    }}
    {PKG}.Xbow.refresh(u);
    long need = {PKG}.SkillDefs.needFor(skill, r[2]);
    if (lvOn) pr.sendMessage({MSG}.raw(need > 0L ? "  next: " + sk + " " + (r[1] + 1L) + " at " + {PKG}.SkillDefs.progress(skill, r[2]) + " XP - /skills" : "  " + sk + " is now MAX level!").color("#c8b070"));
    {PKG}.Overall.levelUp(pr, u, skill, r[0], r[1]);
    {PKG}.SkillStore.publish(u);
  }}
  if (paid != null && paid[2] > shown && {PKG}.SkillStore.notifyOn(u, "rewards.late")) pr.sendMessage({MSG}.raw("[Skills] +" + {PKG}.SkillDefs.fmt(paid[2] - shown) + " coins for earlier " + sk + " level ups that could not be paid at the time").color("#ffc800"));
}}""", xp))
# 0.4.2 stage 2: gain3 = gain4 without a party note (every caller before 0.4.2 is unchanged); PartyXp.one calls gain4 with the killer's name
xp.addMethod(CtNewMethod.make(f"""
public static void gain3({PR} pr, int skill, long amount, boolean note, boolean bonus) {{
  gain4(pr, skill, amount, note, bonus, null);
}}""", xp))
# 0.4 trees bridge: gain2 = gain3 WITH the skill-tree XP bonus (every normal award). gain3(..., false) pays exactly the amount: the
# admin /skills xp (raw) and BridgeTask (BridgeXp.offer already added the bonus, so the per-minute bridge cap counts it)
xp.addMethod(CtNewMethod.make(f"""
public static void gain2({PR} pr, int skill, long amount, boolean note) {{
  gain3(pr, skill, amount, note, true);
}}""", xp))
xp.addMethod(CtNewMethod.make(f"""
public static void gain({PR} pr, int skill, long amount) {{
  gain2(pr, skill, amount, true);
}}""", xp))

# ================= Brew (0.4): Alchemy perks - longer potion effects for the DRINKER, extra potion for the BREWER =================
# BONUS: UUID -> Float duration bonus of the active profile's Alchemy level (set once per second by Perks.tick). SEEN: UUID ->
# Object[2k] last ActiveEntityEffect seen for whitelist effect k, [2k+1] its remaining duration after our last look. Each application
# is extended ONCE by base x bonus (EXTEND adds to remainingDuration without a restart or an extra pulse - bytecode), so drinking again
# can never stack past base x (1 + bonus). Cleared on a profile switch (Perks.switched) and on disconnect (Acro.retainOnline).
brew.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BONUS = new java.util.concurrent.ConcurrentHashMap();", brew))
brew.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();", brew))
brew.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap MSGT = new java.util.concurrent.ConcurrentHashMap();", brew))
brew.addField(CtField.make("public static boolean FAILED_ONCE = false;", brew))
brew.addField(CtField.make("public static final double SIG_DUR = %r;" % SIG_DUR, brew))
brew.addField(CtField.make("public static final double SIG_CD = %r;" % SIG_CD, brew))
brew.addField(CtField.make("public static final double HPR_DUR = %r;" % HPR_DUR, brew))
brew.addField(CtField.make("public static final double HPR_CD = %r;" % HPR_CD, brew))
brew.addField(CtField.make("public static final double MORPH_DUR = %r;" % MORPH_DUR, brew))
brew.addField(CtField.make("public static final double ANTI_DUR = %r;" % ANTI_DUR, brew))
brew.addMethod(CtNewMethod.make(f"""
public static double bonusFor(int lvl) {{
  if (!{PKG}.AlchCfg.ENABLED || !{PKG}.PerkCfg.ENABLED || lvl <= 0) return 0.0;
  double v = lvl * {PKG}.AlchCfg.DUR_PER;
  return v > {PKG}.AlchCfg.DUR_MAX ? {PKG}.AlchCfg.DUR_MAX : v;
}}""", brew))
brew.addMethod(CtNewMethod.make(f"""
public static double extraChance(int lvl) {{
  if (!{PKG}.AlchCfg.ENABLED || !{PKG}.PerkCfg.ENABLED || lvl <= 0) return 0.0;
  double v = lvl * {PKG}.AlchCfg.EXTRA_PER;
  return v > {PKG}.AlchCfg.EXTRA_MAX ? {PKG}.AlchCfg.EXTRA_MAX : v;
}}""", brew))
brew.addMethod(CtNewMethod.make("""
public static void setBonus(java.util.UUID u, int lvl) {
  float b = (float) bonusFor(lvl);
  if (b <= 0.0f) { BONUS.remove(u); SEEN.remove(u); return; }
  BONUS.put(u, Float.valueOf(b));
}""", brew))
brew.addMethod(CtNewMethod.make("""
public static void forget(java.util.UUID u) {
  BONUS.remove(u);
  SEEN.remove(u);
  MSGT.remove(u);
}""", brew))
brew.addMethod(CtNewMethod.make("""
public static int pulses(double dur, double cd, double b) {
  if (cd <= 0.0) return 1;
  return (int) Math.floor(dur * (1.0 + b) / cd);
}""", brew))
# "Signature potions 7 pulses instead of 6 - morphs 75s" (+ " - Health regen 2 pulses" from +98%); its own Stats line (length)
brew.addMethod(CtNewMethod.make("""
public static String pulseText(int lvl) {
  double b = bonusFor(lvl);
  String t = "Signature potions " + pulses(SIG_DUR, SIG_CD, b) + " pulses instead of " + pulses(SIG_DUR, SIG_CD, 0.0) + " - morphs " + Math.round(MORPH_DUR * (1.0 + b)) + "s";
  int hp = pulses(HPR_DUR, HPR_CD, b);
  if (hp > pulses(HPR_DUR, HPR_CD, 0.0)) t = t + " - Health regen " + hp + " pulses";
  return t;
}""", brew))
# every tick per player from AcroSys (world thread, before its 1 s gate): extend each fresh application of a whitelisted effect once
brew.addMethod(CtNewMethod.make(f"""
public static void tick(java.util.UUID u, {ST} store, {CB} cb, {REF} ref, float dt) {{
  try {{
    Object bo = BONUS.get(u);
    if (bo == null) return;
    float b = ((Float) bo).floatValue();
    if (b <= 0.0f) return;
    int[] ids = {PKG}.AlchCfg.extIdx();
    if (ids == null || ids.length == 0) return;
    {ECC} ecc = ({ECC}) store.getComponent(ref, {ECC}.getComponentType());
    if (ecc == null) return;
    Object[] seen = (Object[]) SEEN.get(u);
    if (seen == null || seen.length != 2 * ids.length) {{ seen = new Object[2 * ids.length]; SEEN.put(u, seen); }}
    it.unimi.dsi.fastutil.ints.Int2ObjectMap m = ecc.getActiveEffects();
    for (int k = 0; k < ids.length; k++) {{
      Object o = null;
      if (m != null) o = m.get(ids[k]);
      if (!(o instanceof {AEE})) {{ seen[2 * k] = null; seen[2 * k + 1] = null; continue; }}
      {AEE} a = ({AEE}) o;
      if (a.isInfinite()) continue;
      {EFX} fx = ({EFX}) {EFX}.getAssetMap().getAsset(ids[k]);
      if (fx == null || fx.isDebuff()) continue;
      float rem = a.getRemainingDuration();
      boolean fresh = seen[2 * k] != a;
      if (!fresh && seen[2 * k + 1] instanceof Float) {{
        float last = ((Float) seen[2 * k + 1]).floatValue();
        if (rem > last + 0.01f) fresh = true;
        else if (rem < last - dt - 0.25f && Math.abs(rem - fx.getDuration()) < 0.5f) fresh = true;
      }}
      if (fresh) {{
        float extra = fx.getDuration() * b;
        if (extra >= 0.05f && ecc.addEffect(ref, ids[k], fx, extra, {OVB}.EXTEND, cb)) rem = rem + extra;
      }}
      seen[2 * k] = a;
      seen[2 * k + 1] = Float.valueOf(rem);
    }}
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("alchemy potion duration perk failed (logged once): " + t); }}
  }}
}}""", brew))

# ================= BridgeXp part 1 (0.4): per-minute cap of cross-mod XP, grantable skills =================
# WIN: UUID -> long[]{window start ms, XP accepted in it} (after the multiplier). Per physical player, NOT reset by a profile switch
# (a switch must not reset a rate cap). WARN: UUID -> Long last warning ms (one server-log line per player per minute).
bxp.addField(CtField.make("public static final java.util.HashMap WIN = new java.util.HashMap();", bxp))
bxp.addField(CtField.make("public static final java.util.HashMap WARN = new java.util.HashMap();", bxp))
bxp.addMethod(CtNewMethod.make(f"""
public static synchronized void warnLimited(java.util.UUID u, String text) {{
  long now = System.currentTimeMillis();
  Object last = WARN.get(u);
  if (last instanceof Long && now - ((Long) last).longValue() < 60000L) return;
  WARN.put(u, Long.valueOf(now));
  {PKG}.SkillCfg.warn("bridge XP for " + u + ": " + text);
}}""", bxp))
bxp.addMethod(CtNewMethod.make(f"""
public static synchronized boolean allow(java.util.UUID u, long amt) {{
  long cap = {PKG}.BridgeCfg.PER_MIN;
  if (cap <= 0L) return true;
  long now = System.currentTimeMillis();
  long[] w = (long[]) WIN.get(u);
  if (w == null || now - w[0] >= 60000L) {{ w = new long[] {{ now, 0L }}; WIN.put(u, w); }}
  if (w[1] + amt > cap) return false;
  w[1] = w[1] + amt;
  return true;
}}""", bxp))
bxp.addMethod(CtNewMethod.make("""
public static synchronized void retain(java.util.Set online) {
  WIN.keySet().retainAll(online);
  WARN.keySet().retainAll(online);
}""", bxp))
# exact NAMES / LABELS entry (no prefix match) that bridge.addxp.skills allows, else -1 (never the legacy Combat slot)
bxp.addMethod(CtNewMethod.make(f"""
public static int grantSlot(String skill) {{
  if (skill == null) return -1;
  String t = skill.trim();
  boolean[] g = {PKG}.BridgeCfg.GRANT;
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
    if ({PKG}.SkillDefs.NAMES[i].equalsIgnoreCase(t) || {PKG}.SkillDefs.LABELS[i].equalsIgnoreCase(t)) {{
      if (i == {PKG}.SkillDefs.COMBAT || g == null || i >= g.length || !g[i]) return -1;
      return i;
    }}
  }}
  return -1;
}}""", bxp))
# ================= HealXp part 1 (0.4.4): the Divinity heal XP cap (research/Classes-Berserker-Priest-Spec.md 3.4) =================
# HWIN: UUID -> long[]{window start ms, heal XP granted in it} - base heal XP, BEFORE the xp multiplier. Per physical player, NOT reset by
# a profile switch (the BridgeXp.WIN rule); pruned to online players by Acro.retainOnline. HWARN: UUID -> Long last warning ms (one
# server-log line per player per minute).
hxp.addField(CtField.make("public static final java.util.HashMap HWIN = new java.util.HashMap();", hxp))
hxp.addField(CtField.make("public static final java.util.HashMap HWARN = new java.util.HashMap();", hxp))
hxp.addMethod(CtNewMethod.make(f"""
public static synchronized void warnLimited(java.util.UUID u, String text) {{
  long now = System.currentTimeMillis();
  Object last = HWARN.get(u);
  if (last instanceof Long && now - ((Long) last).longValue() < 60000L) return;
  HWARN.put(u, Long.valueOf(now));
  {PKG}.SkillCfg.warn("Divinity heal XP for " + u + ": " + text);
}}""", hxp))
# all or nothing (spec 3.4 "over the cap -> FALSE", the BridgeXp.allow rule): true = the whole `want` fits in this player's 60 s window
# and is recorded; false = it would cross divinity.healXpMaxPerMinute, nothing recorded (a later, smaller heal may still fit). cap <= 0 =
# no limit, nothing recorded.
hxp.addMethod(CtNewMethod.make("""
public static synchronized boolean take(java.util.UUID u, long want, long cap, long now) {
  if (want <= 0L) return false;
  if (cap <= 0L) return true;
  long[] w = (long[]) HWIN.get(u);
  if (w == null || now - w[0] >= 60000L || now < w[0]) { w = new long[] { now, 0L }; HWIN.put(u, w); }
  if (want > cap - w[1]) return false;
  w[1] = w[1] + want;
  return true;
}""", hxp))
# 0.4.15 fix round: what still fits in this player's 60 s window is paid - min(want, room); 0 = nothing fits (the window is full). The call
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
# a refused offer gives its share back
hxp.addMethod(CtNewMethod.make("""
public static synchronized void give(java.util.UUID u, long amt) {
  if (amt <= 0L) return;
  long[] w = (long[]) HWIN.get(u);
  if (w == null) return;
  w[1] = w[1] > amt ? w[1] - amt : 0L;
}""", hxp))
hxp.addMethod(CtNewMethod.make("""
public static synchronized void retain(java.util.Set online) {
  HWIN.keySet().retainAll(online);
  HWARN.keySet().retainAll(online);
}""", hxp))
# hp x rate, the fraction paid by chance (PartyXp.amount style: 1 HP x 0.2 = 1 XP a fifth of the time); 0 for a non-positive / NaN input
hxp.addMethod(CtNewMethod.make("""
public static long amount(double hp, double rate) {
  if (Double.isNaN(hp) || Double.isNaN(rate) || !(hp > 0.0) || !(rate > 0.0)) return 0L;
  double x = hp * rate;
  if (x >= 9.0E15) return 9000000000000000L;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}""", hxp))
# ================= Perks (0.3): flat stat perks, legacy combat migration, double drops =================
perk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LASTCLS = new java.util.concurrent.ConcurrentHashMap();", perk))
perk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DDMSG = new java.util.concurrent.ConcurrentHashMap();", perk))
perk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();", perk))   # 0.3.2: UUID -> Long last profile:epoch seen
perk.addField(CtField.make("public static boolean FAILED_ONCE = false;", perk))
perk.addField(CtField.make("public static boolean DD_FAILED_ONCE = false;", perk))
# level a perk row uses: Combat = the current class's level (no class = no combat perks)
perk.addMethod(CtNewMethod.make(f"""
public static int rowLevel(java.util.UUID u, int row) {{
  if (row == {PKG}.SkillDefs.COMBAT) {{
    int s = {PKG}.SkillClass.slot(u);
    return s < 0 ? 0 : {PKG}.SkillStore.level(u, s);
  }}
  if (row < 0 || row >= {PKG}.SkillDefs.PERK_SLOT.length) return 0;
  return {PKG}.SkillStore.level(u, {PKG}.SkillDefs.PERK_SLOT[row]);
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static float flat(double per, int lvl) {{
  if (!{PKG}.PerkCfg.ENABLED || lvl <= 0 || per <= 0.0) return 0.0f;
  return (float) (Math.round(per * lvl * 100.0) / 100.0);
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static float total(double[] per, int[] lv) {{
  double sum = 0.0;
  for (int r = 0; r < lv.length && r < per.length; r++) sum = sum + flat(per[r], lv[r]);
  return (float) (Math.round(sum * 100.0) / 100.0);
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static int[] levels(java.util.UUID u) {{
  int[] lv = new int[{PKG}.PerkCfg.KEYS.length];
  for (int r = 0; r < lv.length; r++) lv[r] = rowLevel(u, r);
  return lv;
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static double chance(int row, int lvl) {{
  if (!{PKG}.PerkCfg.ENABLED || row < 0 || row > {PKG}.SkillDefs.FARMING || lvl <= 0) return 0.0;
  double c = lvl * {PKG}.PerkCfg.DD[row];
  return c > {PKG}.PerkCfg.DD_MAX ? {PKG}.PerkCfg.DD_MAX : c;
}}""", perk))
# 0.4 trees bridge: the level perk + the summed dd.<skill> of skill:bonus:<uuid> (SkyyTrees Fortune nodes); the total is still capped at
# perk.doubleDropMax. perk.enabled=false only turns off SkyySkills' own level perk, not the tree bonus (bridge.bonus.enabled does that).
perk.addMethod(CtNewMethod.make(f"""
public static double chanceU(java.util.UUID u, int row, int lvl) {{
  if (row < 0 || row > {PKG}.SkillDefs.FARMING) return 0.0;
  double c = chance(row, lvl) + {PKG}.SkillBonus.dd(u, row);
  if (c > {PKG}.PerkCfg.DD_MAX) c = {PKG}.PerkCfg.DD_MAX;
  return c < 0.0 ? 0.0 : c;
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static double damage(int lvl) {{
  if (!{PKG}.PerkCfg.ENABLED || lvl <= 0) return 0.0;
  return lvl * {PKG}.PerkCfg.DMG;
}}""", perk))
# set (amt != 0) or remove (amt == 0) our MAX modifier on one stat - SkyyAccessories AccEffects.mod (TerrariaAddons pattern)
perk.addMethod(CtNewMethod.make(f"""
public static void mod({ESM} m, int idx, String key, float amt) {{
  if (idx < 0) return;
  try {{
    if (m.get(idx) == null) return;
    {MOD} cur = m.getModifier(idx, key);
    if (amt == 0.0f) {{ if (cur != null) m.removeModifier(idx, key); return; }}
    {SMO} want = new {SMO}({MTG}.MAX, {CAL}.ADDITIVE, amt);
    if (cur != null && cur.equals(want)) return;
    m.putModifier(idx, key, want);
  }} catch (Throwable t) {{ }}
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static void migrate({PR} pr, java.util.UUID u, int slot) {{
  String k = {PKG}.SkillStore.pkey(u);
  long x = {PKG}.SkillStore.moveLegacy({PKG}.SkillStore.dataK(k, u), slot);
  if (x <= 0L) return;
  {PKG}.SkillStore.DIRTY.put(k, Boolean.TRUE);
  {PKG}.SkillStore.publish(u);
  {PKG}.SkillCfg.info("moved legacy Combat XP " + x + " of " + k + " to " + {PKG}.SkillDefs.NAMES[slot]);
  pr.sendMessage({MSG}.raw("[Skills] Your old Combat XP (level " + {PKG}.SkillDefs.levelOf(slot, x) + ") now counts for " + {PKG}.SkillClass.skillName(u, slot) + ". Each class keeps its own combat level.").color("#ffc800"));
}}""", perk))
# 0.3.2 contract rule 3: profile:epoch:<uuid> (Long, +1 on every profile switch / creation; -1 here = no SkyyProfiles)
perk.addMethod(CtNewMethod.make(f"""
public static long epoch(java.util.UUID u) {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("profile:epoch:" + u.toString());
    if (o instanceof Number) return ((Number) o).longValue();
  }} catch (Throwable t) {{ }}
  return -1L;
}}""", perk))
# true when the epoch differs from the one seen on this player's previous 1 s tick (the first tick of a session only records it:
# Perks.tick republishes on a session's first tick anyway). Without SkyyProfiles the epoch is always -1 -> never true.
# Integration check (PROFILES-CONTRACT semantics 4.2): an ABSENT epoch carries no information, so it is never recorded - absent ->
# value is a baseline like the first value of a session (the draft recorded -1 and treated absent -> value as a switch), and
# value -> absent keeps the last value. Data never depends on this: every read/write resolves pkey itself.
perk.addMethod(CtNewMethod.make("""
public static boolean epochChanged(java.util.UUID u) {
  long e = epoch(u);
  if (e < 0L) return false;
  Object last = EPOCH.put(u, Long.valueOf(e));
  return last != null && ((Long) last).longValue() != e;
}""", perk))
# world thread, right after an epoch change (AcroSys, before the flush / movement sync / perk tick of the same second): skill:<uuid>
# now describes the new profile (data(u) resolves the new pkey; its file is loaded here on first use); the +XP line still pending
# and the once-per-session hints belonged to the old profile; the class-sync grace (SkillClass.SINCE / GAVEUP) starts over.
# Review note (kept on purpose): that first load of the new profile's small players/<pkey>.properties is a synchronous read on this
# world thread, exactly like PublishTask for a new session. It cannot move to the ticker (HytaleServer.SCHEDULED_EXECUTOR is ONE
# thread shared by every mod - no player-file I/O there, 0.2 design), and deferring only this publish would not help: the flush /
# movement sync / MAX modifiers of the same second read the new profile's levels anyway, and a non-blocking read would show level 0
# for a moment (health MAX modifier drop). Profile switches are manual and rare; revisit only if they become frequent.
perk.addMethod(CtNewMethod.make(f"""
public static void switched(java.util.UUID u) {{
  {PKG}.SkillMsg.PEND.remove(u);
  {PKG}.SkillClass.TOLD.remove(u);
  {PKG}.SkillClass.resync(u);
  {PKG}.Brew.forget(u);
  {PKG}.SkillStore.publish(u);
  {PKG}.SkillCfg.info("profile switch: " + u + " now uses skills of " + {PKG}.SkillStore.pkey(u));
  {PKG}.Xbow.forget(u);
  {PKG}.Xbow.refresh(u);
  {PKG}.Overall.forget(u);
}}""", perk))
# once per second per player from AcroSys (world thread): first tick of the session or class change -> republish skill:<uuid>,
# legacy combat move, stat modifiers. The first tick (LASTCLS has no entry: new session / plugin start) always republishes:
# SkyyClasses publishes class:<uuid> from its ReadyTask (scheduler thread), possibly AFTER our 5 s publishOnline already put a
# classless skill:<uuid>, and publishOnline never republishes a player it has published (PUBLISHED) -> the Combat entry would stay
# stale until the next level up. Cheap: one bridge put per player per session.
# 0.4.6 (Overall-Level-Spec 4.5): base Mana + the Overall Level Health / Mana, each under its own key, computed from scratch (never from the
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
    float cmn = {PKG}.ClassMana.amount(u, {PKG}.SkillStore.data(u));   // 0.4.15: max Mana per class level (Priest x Divinity, Mage x Sorcery)
    if (cmn >= 0.0f) mod(m, mi, "skyyskill_classmana", cmn);           // 0 = removed (no class level Mana); -1 = an error: the saved one stays
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
perk.addMethod(CtNewMethod.make(f"""
public static void tick(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref) {{
  try {{
    int cs = {PKG}.SkillClass.slot(u);
    String cn = cs < 0 ? "" : {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(cs)];
    Object last = LASTCLS.put(u, cn);
    boolean repub = last == null || !last.equals(cn);
    boolean synced = {PKG}.SkillClass.consistent(u);
    if (cs >= 0 && synced) migrate(pr, u, cs);
    if (repub) {PKG}.SkillStore.publish(u);
    {PKG}.ClassCurve.tick(pr, u);   // 0.4.12: the one-time class skill curve notice + its level-up rewards (only while one is pending)
    {PKG}.Xbow.refresh(u);
    int[] lv = levels(u);
    {PKG}.Brew.setBonus(u, lv[5]);
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());
    if (m == null) return;
    mod(m, {DST}.getHealth(), "skyyskill_health", total({PKG}.PerkCfg.HP, lv));
    mod(m, {DST}.getStamina(), "skyyskill_stamina", total({PKG}.PerkCfg.STA, lv));
    mod(m, {DST}.getMana(), "skyyskill_mana", total({PKG}.PerkCfg.MANA, lv));
    ovl(u, pr, cb, ref, m);
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("perk tick failed (logged once): " + t); }}
  }}
}}""", perk))
# drops that depend on the held tool (a Gathering.Tools entry WITHOUT State breaks the block with the tool's own drop list,
# BlockHarvestUtils.damageSingleBlock) cannot be reproduced from the event -> such blocks never double. Tools entries WITH a State
# (Scraper -> Stripped on oak trunks) change the block instead of breaking it and fire no BreakBlockEvent.
perk.addMethod(CtNewMethod.make(f"""
public static boolean toolDependent({BGA} g) {{
  try {{
    java.util.Map td = g.getToolData();
    if (td == null || td.isEmpty()) return false;
    java.util.Iterator it = td.values().iterator();
    while (it.hasNext()) {{
      Object o = it.next();
      if (o instanceof {BTD} && (({BTD}) o).getStateId() == null) return true;
    }}
    return false;
  }} catch (Throwable t) {{ return true; }}
}}""", perk))
# the engine's break drops (verified bytecode, see the 0.3 notes): Breaking -> getDrops(bt, quantity, itemId, dropListId); a soft
# block (crops) -> getDrops(bt, 1, soft itemId, soft dropListId); both kinds on one block = which one applied is unknown -> none
perk.addMethod(CtNewMethod.make(f"""
public static java.util.List breakDrops({BTY} bt) {{
  if (bt == null) return null;
  {BGA} g = bt.getGathering();
  if (g == null || toolDependent(g)) return null;
  {BBD} br = g.getBreaking();
  if (g.isSoft()) {{
    if (br != null) return null;
    {SBD} so = g.getSoft();
    if (so == null) return null;
    return {BHU}.getDrops(bt, 1, so.getItemId(), so.getDropListId());
  }}
  if (br == null) return null;
  int q = br.getQuantity();
  if (q <= 0) return null;
  return {BHU}.getDrops(bt, q, br.getItemId(), br.getDropListId());
}}""", perk))
# F-harvest drops = FarmingUtil.giveDrops: getDrops(bt, 1, harvest itemId, harvest dropListId)
perk.addMethod(CtNewMethod.make(f"""
public static java.util.List harvestDrops({BTY} bt) {{
  if (bt == null) return null;
  {BGA} g = bt.getGathering();
  if (g == null) return null;
  {HDT} h = g.getHarvest();
  if (h == null) return null;
  return {BHU}.getDrops(bt, 1, h.getItemId(), h.getDropListId());
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static boolean matches(int row, String fam) {{
  String o = {PKG}.PerkCfg.ONLY[row];
  if (o == null || o.trim().length() == 0) return true;
  if (fam == null) return false;
  String[] ps = o.split(",");
  for (int i = 0; i < ps.length; i++) {{
    String p = ps[i].trim();
    if (p.length() > 0 && fam.indexOf(p) >= 0) return true;
  }}
  return false;
}}""", perk))
# world thread (BreakTask / HarvestTask run through world.execute): the extra copy goes into storage > hotbar > backpack, dropped at
# the player's feet when full (SkyySacks 0.6.5 craft output path). Only while the player is still in the world of the block.
perk.addMethod(CtNewMethod.make(f"""
public static String give({PR} pr, java.util.List drops, String world) {{
  if (drops == null || drops.isEmpty() || world == null) return null;
  {REF} r = pr.getReference();
  if (r == null || !r.isValid()) return null;
  {ST} st = r.getStore();
  Object ext = st.getExternalData();
  if (!(ext instanceof {EST})) return null;
  {WLD} w = (({EST}) ext).getWorld();
  if (w == null || !world.equals(w.getName())) return null;
  {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
  if (p == null) return null;
  StringBuilder sb = new StringBuilder();
  int n = 0;
  for (int i = 0; i < drops.size(); i++) {{
    Object o = drops.get(i);
    if (!(o instanceof {IS})) continue;
    {IS} is = ({IS}) o;
    if (is.isEmpty() || is.getItemId() == null) continue;
    {SIC}.addOrDropItemStack(st, r, p.getInventory().getCombinedStorageHotbarBackpack(), is);
    n++;
    if (n <= 3) sb.append(" +").append(is.getQuantity()).append(' ').append(is.getItemId().replace('_', ' '));
  }}
  if (n == 0) return null;
  if (n > 3) sb.append(" ...");
  return sb.toString();
}}""", perk))
# 0.4.2 (Tree-Fall-Spec 2.8, optional; collections.doubleDrops, default OFF - Skyy decides): the items the double-drop perk GAVE also
# count in SkyyCollections (source skills:double, accepted by SkyyCollections 0.2 by default). Hand breaks, F-harvests and felled logs alike.
perk.addMethod(CtNewMethod.make(f"""
public static void collDouble({PR} pr, java.util.List drops) {{
  try {{
    if (!{PKG}.FellCfg.DD_COLLECTIONS || pr == null || drops == null) return;
    Object f = {PKG}.SkillStore.bridge().get("coll:fn:add");
    if (!(f instanceof java.util.function.Function)) return;
    java.util.UUID u = pr.getUuid();
    String k = {PKG}.SkillStore.pkey(u);
    for (int i = 0; i < drops.size(); i++) {{
      Object o = drops.get(i);
      if (!(o instanceof {IS})) continue;
      {IS} is = ({IS}) o;
      if (is.isEmpty() || is.getItemId() == null || is.getQuantity() <= 0) continue;
      ((java.util.function.Function) f).apply(new Object[] {{ u, is.getItemId(), Long.valueOf((long) is.getQuantity()), "skills:double", k }});
    }}
  }} catch (Throwable t) {{ }}
}}""", perk))
# "Double drop!" chat line: at most one per feedbackMs per player (count of doubles since the last line), hidden by /skills quiet
perk.addMethod(CtNewMethod.make(f"""
public static void doubled({PR} pr, java.util.List drops, int row, String world) {{
  String what = give(pr, drops, world);
  if (what != null) collDouble(pr, drops);
  if (what == null || !{PKG}.PerkCfg.DD_MSG) return;
  java.util.UUID u = pr.getUuid();
  if (!{PKG}.SkillStore.notifyOn(u, "skills.doubleDrop")) return;
  long now = System.currentTimeMillis();
  long[] c = (long[]) DDMSG.get(u);
  if (c == null) {{ c = new long[2]; DDMSG.put(u, c); }}
  c[0] = c[0] + 1L;
  if (now - c[1] < {PKG}.SkillCfg.FEEDBACK_MS) return;
  pr.sendMessage({MSG}.raw("Double drop" + (c[0] > 1L ? " x" + c[0] : "") + "!" + what + "  (" + {PKG}.SkillDefs.LABELS[row] + " perk)").color("#b8f0a0"));
  c[0] = 0L;
  c[1] = now;
}}""", perk))
# tracked = the block cannot have been placed by a player (ripe crops, or the placed-block tracker is on and cleared it)
perk.addMethod(CtNewMethod.make(f"""
public static void breakDouble({PR} pr, int row, {BTY} bt, String world, boolean tracked) {{
  try {{
    if (!tracked || row < 0 || row > {PKG}.SkillDefs.FARMING || bt == null) return;
    double c = chanceU(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row));
    if (c <= 0.0 || !matches(row, {PKG}.SkillCfg.familyId(bt))) return;
    if (java.util.concurrent.ThreadLocalRandom.current().nextDouble() >= c) return;
    doubled(pr, breakDrops(bt), row, world);
  }} catch (Throwable t) {{
    if (!DD_FAILED_ONCE) {{ DD_FAILED_ONCE = true; {PKG}.SkillCfg.warn("double drop failed (logged once): " + t); }}
  }}
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static void harvestDouble({PR} pr, {BTY} bt, String world) {{
  try {{
    int row = {PKG}.SkillDefs.FARMING;
    if (bt == null) return;
    double c = chanceU(pr.getUuid(), row, {PKG}.SkillStore.level(pr.getUuid(), row));
    if (c <= 0.0 || !matches(row, {PKG}.SkillCfg.familyId(bt))) return;
    if (java.util.concurrent.ThreadLocalRandom.current().nextDouble() >= c) return;
    doubled(pr, harvestDrops(bt), row, world);
  }} catch (Throwable t) {{
    if (!DD_FAILED_ONCE) {{ DD_FAILED_ONCE = true; {PKG}.SkillCfg.warn("double drop failed (logged once): " + t); }}
  }}
}}""", perk))

# ================= Sickle (0.4.14, research/Tool-Levels-Spec.md question 3): sickle swing harvests pay Farming XP + roll double drops =================
# A sickle swing's HitBlock runs HarvestCrop -> FarmingUtil.harvest0 -> giveDrops -> ItemUtils.interactivelyPickupItem: one
# InteractivelyPickupItemEvent per drop stack, no break event, no position (bytecode asserted above). SickleSys collects the stacks of one tick
# (PEND) unless they belong to an F pickup (BRK) or an F-harvest (USE); SickleTask pays them on the world thread after every other system.
skl.addMethod(CtNewMethod.make(J14(r"""
public static boolean isSickle(String id) {
  if (id == null) return false;
  String[] it = ITEMS;
  for (int i = 0; i < it.length; i++) if (id.startsWith(it[i])) return true;
  return false;
}"""), skl))
# BreakSys, synchronously: a BreakBlockEvent with a NULL item = BlockHarvestUtils.performPickupByInteraction (the F pickup of a loose block), whose
# drops arrive as pickups right after it on the same thread; its BreakTask closes the context (breakDone) after the dispatch
skl.addMethod(CtNewMethod.make(J14(r"""
public static void breakOpen(java.util.UUID u, Object ev) {
  if (u == null) return;
  BRK.put(u, new Object[] { Thread.currentThread(), Long.valueOf(System.nanoTime()), ev });
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static void breakDone(java.util.UUID u, Object ev) {
  if (u == null || BRK.isEmpty()) return;
  Object o = BRK.get(u);
  if (o instanceof Object[] && ((Object[]) o).length > 2 && ((Object[]) o)[2] == ev) BRK.remove(u, o);
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static boolean inBreak(java.util.UUID u, long nanos) {
  Object o = BRK.get(u);
  if (!(o instanceof Object[])) return false;
  Object[] a = (Object[]) o;
  if (a.length < 2 || a[0] != Thread.currentThread() || !(a[1] instanceof Long)) return false;
  long d = nanos - ((Long) a[1]).longValue();
  return d >= 0L && d < BREAK_NS;
}"""), skl))
# HarvestSys, synchronously: UseBlockEvent$Post on a ripe harvestable block = an F-harvest (HarvestTask pays it); its drops come later, within
# WINDOW_MS (the SkyyCollections rule) - never paid as sickle swings
skl.addMethod(CtNewMethod.make(J14(r"""
public static void useOpen(@ACH@ chunk, int idx, @ST@ st) {
  try {
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    USE.put(pr.getUuid(), Long.valueOf(System.currentTimeMillis()));
  } catch (Throwable t) { }
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static boolean inUse(java.util.UUID u, long now) {
  Object o = USE.get(u);
  return o instanceof Long && now - ((Long) o).longValue() <= WINDOW_MS;
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static void failed(Throwable t) {
  if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("sickle swing harvest XP failed (logged once): " + t); }
}"""), skl))
# the crop map: produce item -> {Long the LOWEST Farming XP of its crops, Boolean a crop can drop it twice in one harvest, String the
# alphabetically first crop family (Perks.matches), HashSet every item id those crops' harvests can drop (the produce included)}
skl.addMethod(CtNewMethod.make(J14(r"""
public static void put(java.util.HashMap m, String key, long xp, boolean multi, String fam, java.util.Set ids) {
  Object o = m.get(key);
  if (o instanceof Object[]) {
    Object[] e = (Object[]) o;
    if (xp < ((Long) e[0]).longValue()) e[0] = Long.valueOf(xp);
    if (multi) e[1] = Boolean.TRUE;
    if (fam != null && (e[2] == null || fam.compareTo((String) e[2]) < 0)) e[2] = fam;
    if (ids != null) ((java.util.HashSet) e[3]).addAll(ids);
    return;
  }
  java.util.HashSet s = new java.util.HashSet();
  if (ids != null) s.addAll(ids);
  s.add(key);
  m.put(key, new Object[] { Long.valueOf(xp), Boolean.valueOf(multi), fam, s });
}"""), skl))
# one block type: a RIPE crop (the StageFinal state of a block with growth states) with a Harvest drop whose block rule pays Farming XP ->
# its produce = the first item its harvest drops emit (giveDrops -> BlockHarvestUtils.getDrops: the drop list's items in container order,
# then the Harvest ItemId); multi = that item can be emitted twice by one harvest (berry bushes).
# FIX ROUND F1 (reviews 2026-10-03): ONLY StageFinal. FarmingUtil.harvest0 harvests any block with a Harvest drop at once (no ripeness, no
# placed check), and a pickup carries no position, so a sickle swing cannot tell a placed block: a stateless Health / Mana / Stamina plant
# or cactus flower hands back its own item -> place, swing, place paid Farming XP forever and the double drop copied the plant. StageFinal =
# what HarvestSys pays for an F-harvest and what classifyBreak never place-checks (a crop only gets there by growing); everything else pays
# through breaking only (BreakTask: placed blocks pay nothing under ignorePlaced; with it off they pay but never double)
skl.addMethod(CtNewMethod.make(J14(r"""
public static void addCrop(java.util.HashMap m, @BTY@ bt) {
  if (bt == null) return;
  @BGA@ g = bt.getGathering();
  if (g == null) return;
  @HDT@ h = g.getHarvest();
  if (h == null) return;
  if (!@PKG@.SkillCfg.hasFinalStage(bt) || !"StageFinal".equals(@PKG@.SkillCfg.stateOf(bt))) return;
  String fam = @PKG@.SkillCfg.familyId(bt);
  long[] r = @PKG@.SkillCfg.resolve(fam);
  if (r == null || r[0] != (long) @PKG@.SkillDefs.FARMING || r[1] <= 0L) return;
  String key = null;
  int cnt = 0;
  java.util.HashSet ids = new java.util.HashSet();
  String dl = h.getDropListId();
  if (dl != null) {
    @IDL@ l = (@IDL@) @IDL@.getAssetMap().getAsset(dl);
    if (l != null && l.getContainer() != null) {
      java.util.List ds = l.getContainer().getAllDrops(new java.util.ArrayList());
      for (int j = 0; ds != null && j < ds.size(); j++) {
        Object o = ds.get(j);
        if (!(o instanceof @IDR@)) continue;
        String id = ((@IDR@) o).getItemId();
        if (id == null) continue;
        ids.add(id);
        if (key == null) key = id;
        if (key.equals(id)) cnt++;
      }
    }
  }
  String iid = h.getItemId();
  if (iid != null) {
    ids.add(iid);
    if (key == null) key = iid;
    if (key.equals(iid)) cnt++;
  }
  if (key == null) return;
  put(m, key, r[1], cnt > 1, fam, ids);
}"""), skl))
skl.addMethod(CtNewMethod.make(J14(r"""
public static java.util.HashMap keys() {
  java.util.HashMap k = KEYS;
  if (k != null) return k;
  java.util.HashMap m = new java.util.HashMap();
  try {
    @BTM@ am = @BTY@.getAssetMap();
    int n = am.getNextIndex();
    for (int i = 0; i < n; i++) {
      try { addCrop(m, (@BTY@) am.getAsset(i)); } catch (Throwable t) { }
    }
  } catch (Throwable t) { failed(t); }
  KEYS = m;
  return m;
}"""), skl))
# PURE: one tick's stacks (in pickup order) -> crops Object[]{String produce, ArrayList its stacks}: a produce stack starts a crop (its harvest
# emits the produce first), the stacks after it belong to it when that crop can drop them (anything else the same swing harvested - sap, a
# flower - is left out, so the double drop copies only the crop's own items); a multi-source produce directly after a stack of the same
# produce joins it
skl.addMethod(CtNewMethod.make(J14(r"""
public static java.util.ArrayList segments(java.util.List stacks, java.util.Map keys) {
  java.util.ArrayList segs = new java.util.ArrayList();
  Object[] cur = null;
  java.util.Set own = null;
  String prev = null;
  for (int i = 0; stacks != null && i < stacks.size(); i++) {
    Object o = stacks.get(i);
    if (!(o instanceof @IS@)) continue;
    @IS@ is = (@IS@) o;
    String id = is.getItemId();
    if (id == null) continue;
    Object info = keys == null ? null : keys.get(id);
    if (info instanceof Object[]) {
      Object[] in = (Object[]) info;
      boolean multi = Boolean.TRUE.equals(in[1]);
      if (!(multi && cur != null && id.equals(prev) && id.equals(cur[0]))) {
        cur = new Object[] { id, new java.util.ArrayList() };
        segs.add(cur);
        own = in.length > 3 && in[3] instanceof java.util.Set ? (java.util.Set) in[3] : null;
      }
    } else if (cur != null && own != null && !own.contains(id)) {
      prev = id;
      continue;
    }
    if (cur != null) ((java.util.ArrayList) cur[1]).add(is);
    prev = id;
  }
  return segs;
}"""), skl))
# metadata-free copies (the double drop gives the crop's items once more)
skl.addMethod(CtNewMethod.make(J14(r"""
public static java.util.ArrayList copies(java.util.List l) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; l != null && i < l.size(); i++) {
    Object o = l.get(i);
    if (!(o instanceof @IS@)) continue;
    @IS@ is = (@IS@) o;
    if (is.isEmpty() || is.getItemId() == null || is.getQuantity() <= 0) continue;
    out.add(new @IS@(is.getItemId(), is.getQuantity()));
  }
  return out;
}"""), skl))
# world thread (SickleTask): the final stacks of the not-cancelled pickups -> crops; each crop: its Farming XP once (SkillXp.gain = the pace +
# Wisdom, the chat line, level ups) and one Farming double-drop roll (the level after the award, like BreakTask). Returns the crops paid.
skl.addMethod(CtNewMethod.make(J14(r"""
public static int award(@PR@ pr, java.util.List evs, String wn) {
  if (pr == null || evs == null) return 0;
  java.util.ArrayList st = new java.util.ArrayList();
  for (int i = 0; i < evs.size(); i++) {
    Object o = evs.get(i);
    if (!(o instanceof @IPE@)) continue;
    @IPE@ e = (@IPE@) o;
    if (e.isCancelled()) continue;
    @IS@ is = e.getItemStack();
    if (is == null || is.isEmpty() || is.getItemId() == null) continue;
    st.add(is);
  }
  if (st.isEmpty()) return 0;
  java.util.HashMap ks = keys();
  if (ks == null || ks.isEmpty()) return 0;
  java.util.ArrayList segs = segments(st, ks);
  java.util.UUID u = pr.getUuid();
  int n = 0;
  for (int i = 0; i < segs.size(); i++) {
    Object[] sg = (Object[]) segs.get(i);
    Object io = ks.get(sg[0]);
    if (!(io instanceof Object[])) continue;
    Object[] info = (Object[]) io;
    long amt = @PKG@.SkillCfg.scaled(((Long) info[0]).longValue());
    if (amt > 0L) @PKG@.SkillXp.gain(pr, @PKG@.SkillDefs.FARMING, amt);
    try {
      double c = @PKG@.Perks.chanceU(u, @PKG@.SkillDefs.FARMING, @PKG@.SkillStore.level(u, @PKG@.SkillDefs.FARMING));
      if (c > 0.0 && @PKG@.Perks.matches(@PKG@.SkillDefs.FARMING, (String) info[2]) && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < c)
        @PKG@.Perks.doubled(pr, copies((java.util.List) sg[1]), @PKG@.SkillDefs.FARMING, wn);
    } catch (Throwable t) {
      if (!@PKG@.Perks.DD_FAILED_ONCE) { @PKG@.Perks.DD_FAILED_ONCE = true; @PKG@.SkillCfg.warn("double drop failed (logged once): " + t); }
    }
    n++;
  }
  if (n > 0 && !SEEN) { SEEN = true; @PKG@.SkillCfg.info("sickle swing harvests reach SkyySkills - they pay Farming XP and roll double drops (one award per crop)"); }
  return n;
}"""), skl))
# SickleTask: this tick's pickups of one player, on the world thread after every system saw them (a cancelled pickup pays nothing)
sktk.addInterface(pool.get("java.lang.Runnable"))
sktk.addField(CtField.make("public java.util.UUID u;", sktk))
sktk.addField(CtField.make("public String wn;", sktk))
sktk.addConstructor(CtNewConstructor.make("public SickleTask(java.util.UUID u, String wn) { this.u = u; this.wn = wn; }", sktk))
sktk.addMethod(CtNewMethod.make(J14(r"""
public void run() {
  try {
    Object o = @PKG@.Sickle.PEND.remove(this.u);
    if (!(o instanceof java.util.List)) return;
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    if (@PKG@.SkillStore.bridge().get("profile:busy:" + this.u.toString()) != null) return;
    @PKG@.Sickle.award(pr, (java.util.List) o, this.wn);
  } catch (Throwable t) { @PKG@.Sickle.failed(t); }
}"""), sktk))
# SickleSys (world thread): one pickup into this tick's burst; the first of a burst queues the SickleTask
skl.addMethod(CtNewMethod.make(J14(r"""
public static void add(java.util.UUID u, Object e, @WLD@ w) {
  if (u == null || e == null || w == null) return;
  Object o = PEND.get(u);
  if (o instanceof java.util.ArrayList) { ((java.util.ArrayList) o).add(e); return; }
  java.util.ArrayList l = new java.util.ArrayList();
  l.add(e);
  PEND.put(u, l);
  try { w.execute(new @PKG@.SickleTask(u, w.getName())); } catch (Throwable t) { PEND.remove(u); }
}"""), skl))

# ================= Brew.extraPotion (0.4): the brewer's extra-potion perk (world thread) =================
# one roll per finished unit (vanilla bench) or per reported craft (bridge); a hit gives the recipe's primary output once more through
# Perks.give (storage > hotbar > backpack, dropped at the feet when full). "Extra potion!" line throttled like "Double drop!".
brew.addMethod(CtNewMethod.make(f"""
public static void extraPotion({PR} pr, {CRR} rc, int units, String world) {{
  try {{
    if (pr == null || rc == null || units <= 0) return;
    java.util.UUID u = pr.getUuid();
    double c = extraChance({PKG}.SkillStore.level(u, {PKG}.SkillDefs.ALCHEMY));
    if (c <= 0.0) return;
    {MQ} po = rc.getPrimaryOutput();
    if (po == null) return;
    String id = po.getItemId();
    if (!{PKG}.AlchCfg.extraOk(id)) return;
    int n = units > 10000 ? 10000 : units;
    int hits = 0;
    java.util.concurrent.ThreadLocalRandom rnd = java.util.concurrent.ThreadLocalRandom.current();
    for (int i = 0; i < n; i++) {{ if (rnd.nextDouble() < c) hits++; }}
    if (hits <= 0) return;
    int q = po.getQuantity() > 0 ? po.getQuantity() : 1;
    java.util.ArrayList l = new java.util.ArrayList();
    l.add(new {IS}(id, q * hits));
    if ({PKG}.SkillStore.bridge().get("profile:busy:" + u.toString()) != null) return;
    String what = {PKG}.Perks.give(pr, l, world);
    if (what == null || !{PKG}.SkillStore.notifyOn(u, "skills.extraPotion")) return;
    long now = System.currentTimeMillis();
    long[] tm = (long[]) MSGT.get(u);
    if (tm == null) {{ tm = new long[2]; MSGT.put(u, tm); }}
    tm[0] = tm[0] + (long) hits;
    if (now - tm[1] < {PKG}.SkillCfg.FEEDBACK_MS) return;
    pr.sendMessage({MSG}.raw("Extra potion" + (tm[0] > 1L ? " x" + tm[0] : "") + "!" + what + "  (Alchemy perk)").color("#a0f0e0"));
    tm[0] = 0L;
    tm[1] = now;
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("extra potion perk failed: " + t); }}
}}""", brew))
# ================= 0.2 ACROBATICS =================
# MoveSync = the shared Skyy movement protocol (tools/skyymove.py; identical code in SkyyAccessories 0.3)
MV.add_move_sync(mvs_, CtField, CtNewMethod, PKG + ".SkillCfg.warn")

# Acro: per-player tracker (in memory only). STATE uuid -> double[152]:
#  0-2 last position, 3 has position, 4 prev onGround, 5 prev jumping, 6 prev dodging, 7 peak Y while airborne, 8 has peak,
#  9 last paid jump ms, 10 blocks moved since the last paid jump, 11 pending (fractional) XP, 12-13 unused (were the fixed per-minute
#  window, replaced by the sliding ring 24-151 in the review fix), 14 seconds since the last 1 s sync, 15 unresolved fall damage ms
#  (0 once it has been paid - review fix, a stale timestamp swallowed the next safe landing), 16 its unreduced amount, 17 fall damage
#  resolved, 18 pending landing ms, 19 its drop in blocks, 20 last dodge ms, 21 XP not shown in chat yet, 22 last chat line ms,
#  (0.4: 16 = the noted fall damage normalised to 100 max health; 18/19 landing bookkeeping only - safe drops pay nothing; 152 pending
#  fall XP; 153-216 fall XP paid per wall-clock second (ring, own cap acro.fallMaxXpPerMinute), 217-280 the second each slot holds)
#  23 pending dodge boost ms (the push is sent 100 ms after the Dodge effect appears so it lands AFTER the dodge's own ApplyForce "Set"
#  instruction, which would erase it), 24-87 Acrobatics XP paid per wall-clock second (ring slot = second % 64), 88-151 the second
#  each ring slot holds. acro.maxXpPerMinute caps the XP of ANY 61 consecutive whole seconds, which covers every real 60 s interval
#  (review fix: the 0.2 draft reset a fixed 60 s window, so a burst across the reset paid ~2x the cap).
# 0.4.2 stage 2 (Double-Jump-Spec 3.2): double[292]: 281 prev crouching, 282 air jumps used since the last ground contact, 283 last double
#  jump ms, 284 airborne-since ms (0 = grounded), 285 prev jumping (own copy; s[5] belongs to move()), 286 last debug line ms,
#  287 prev extraJumpsUsed, 288-291 spare. reset (world change) and profileReset also zero 281, 282, 284 and 285.
# 0.4.14 (roll landings): 288 rolled landing ms (RollSys.land, 0 = none pending), 289 its fall damage WITHOUT the roll normalised to 100 max
#  health, 290 resolved; falls() pays it 400 ms later x (1 + acro.rollBonus); profileReset zeroes them; 291 spare.
acro.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap STATE = new java.util.concurrent.ConcurrentHashMap();", acro))
acro.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap WORLD = new java.util.concurrent.ConcurrentHashMap();", acro))
acro.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap MOVE = new java.util.concurrent.ConcurrentHashMap();", acro))
acro.addField(CtField.make('public static final String SOURCE = "skills.acrobatics";', acro))
acro.addField(CtField.make('public static final String MOD = "SkyySkills";', acro))
acro.addMethod(CtNewMethod.make("""
public static double[] state(java.util.UUID u) {
  double[] s = (double[]) STATE.get(u);
  if (s != null) return s;
  double[] n = new double[292];
  Object o = STATE.putIfAbsent(u, n);
  return o == null ? n : (double[]) o;
}""", acro))
acro.addMethod(CtNewMethod.make("""
public static void reset(double[] s) {
  s[3] = 0.0; s[5] = 0.0; s[6] = 0.0; s[8] = 0.0; s[18] = 0.0; s[23] = 0.0;
  s[281] = 0.0; s[282] = 0.0; s[284] = 0.0; s[285] = 0.0;
}""", acro))
# 0.3.2 profile switch: XP earned on the old profile but not paid yet is dropped (at most one second of movement / one landing) so it
# never lands on the new profile; the position is re-seeded (a switch usually teleports to the profile's island). The jump / dodge
# edges and the per-minute cap ring stay: they describe the physical player, not the save.
acro.addMethod(CtNewMethod.make("""
public static void profileReset(double[] s) {
  s[3] = 0.0; s[8] = 0.0; s[10] = 0.0; s[11] = 0.0;
  s[15] = 0.0; s[16] = 0.0; s[17] = 0.0; s[18] = 0.0; s[21] = 0.0; s[152] = 0.0;
  s[288] = 0.0; s[289] = 0.0; s[290] = 0.0;   // 0.4.14: a rolled landing not paid yet
  s[281] = 0.0; s[282] = 0.0; s[284] = 0.0; s[285] = 0.0;
}""", acro))
acro.addMethod(CtNewMethod.make("""
public static boolean worldChanged(java.util.UUID u, String wn) {
  if (wn == null) return false;
  Object o = WORLD.put(u, wn);
  return o != null && !o.equals(wn);
}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static void retainOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr != null) online.add(pr.getUuid());
    }}
    STATE.keySet().retainAll(online);
    WORLD.keySet().retainAll(online);
    MOVE.keySet().retainAll(online);
    {PKG}.SkillClass.TOLD.keySet().retainAll(online);
    {PKG}.Perks.LASTCLS.keySet().retainAll(online);
    {PKG}.Perks.DDMSG.keySet().retainAll(online);
    {PKG}.Perks.EPOCH.keySet().retainAll(online);
    {PKG}.SkillClass.SINCE.keySet().retainAll(online);
    {PKG}.SkillClass.GAVEUP.keySet().retainAll(online);
    {PKG}.Brew.BONUS.keySet().retainAll(online);
    {PKG}.Brew.SEEN.keySet().retainAll(online);
    {PKG}.Brew.MSGT.keySet().retainAll(online);
    {PKG}.BridgeXp.retain(online);
    {PKG}.HealXp.retain(online);
    {PKG}.Xbow.retain(online);
    {PKG}.Overall.retain(online);
    {PKG}.ManaRegen.CLK.keySet().retainAll(online);   // 0.4.12 (the Mana Regen % entries belong to the mods that registered them)
    {PKG}.ManaRegen.CMB.keySet().retainAll(online);   // 0.4.13 fix F2: a player who left in combat
    {PKG}.ManaRegen.CARRY.keySet().retainAll(online);   // 0.4.13 fix F1's per-player record
    {PKG}.Sickle.retain(online);   // 0.4.14: the sickle swing contexts and this tick's pickups
  }} catch (Throwable t) {{ }}
}}""", acro))
acro.addMethod(CtNewMethod.make("""
public static boolean isFall(com.hypixel.hytale.server.core.modules.entity.damage.DamageCause c) {
  if (c == null) return false;
  com.hypixel.hytale.server.core.modules.entity.damage.DamageCause f = com.hypixel.hytale.server.core.modules.entity.damage.DamageCause.FALL;
  if (c == f) return true;
  String a = c.getId();
  if (a == null) return false;
  if (f == null) return a.equals("Fall");
  return a.equals(f.getId());
}""", acro))
# bonuses of one Acrobatics level (fractions / blocks)
acro.addMethod(CtNewMethod.make(f"""
public static double speedBonus(int lvl) {{
  return lvl <= 0 ? 0.0 : lvl * {PKG}.AcroCfg.SPEED_PER_LVL;
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static double jumpBonus(int lvl) {{
  return lvl <= 0 ? 0.0 : lvl * {PKG}.AcroCfg.JUMP_PER_LVL;
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static double fallBonus(int lvl) {{
  if (lvl <= 0) return 0.0;
  double f = lvl * {PKG}.AcroCfg.FALL_PER_LVL;
  return f > {PKG}.AcroCfg.FALL_RED_MAX ? {PKG}.AcroCfg.FALL_RED_MAX : f;
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static double dodgeBonus(int lvl) {{
  if (lvl <= 0 || !{PKG}.AcroCfg.DODGE_BOOST) return 0.0;
  double f = lvl * {PKG}.AcroCfg.DODGE_PER_LVL;
  return f > {PKG}.AcroCfg.DODGE_MAX ? {PKG}.AcroCfg.DODGE_MAX : f;
}}""", acro))
# 0.123 -> "+12.3" (percent, signed), 0.5 -> "+50"
acro.addMethod(CtNewMethod.make("""
public static String pct(double v) {
  long t = Math.round(v * 1000.0);
  String sign = t < 0L ? "-" : "+";
  if (t < 0L) t = -t;
  if (t % 10L == 0L) return sign + (t / 10L);
  return sign + (t / 10L) + "." + (t % 10L);
}""", acro))
# 0.75 -> "+0.75" (blocks, signed)
acro.addMethod(CtNewMethod.make("""
public static String blocks(double v) {
  long t = Math.round(v * 100.0);
  String sign = t < 0L ? "-" : "+";
  if (t < 0L) t = -t;
  return sign + (t / 100L) + "." + ((t % 100L) < 10L ? "0" : "") + (t % 100L);
}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static String bonusText(int lvl) {{
  if (!{PKG}.AcroCfg.ENABLED) return "Acrobatics bonuses are turned off on this server";
  if (lvl <= 0) return "Level up to run faster - jump higher - take less fall damage - dodge further";
  String t = "Speed " + pct(speedBonus(lvl)) + "%   Jump " + blocks(jumpBonus(lvl)) + " blocks   Fall damage " + pct(0.0 - fallBonus(lvl)) + "%";
  double db = dodgeBonus(lvl);
  if (db > 0.0) t = t + "   Dodge " + pct(db) + "%";
  return t;
}}""", acro))
# fall Damage seen by AcroFallSys (world thread): remembered, paid by falls() once the player is still alive 0.4 s later
acro.addMethod(CtNewMethod.make("""
public static void noteFall(java.util.UUID u, float amount) {
  double[] s = state(u);
  if (s[288] > 0.0 && (double) System.currentTimeMillis() - s[288] < 1000.0) return;   // 0.4.14: this landing was a roll (RollSys noted it unreduced)
  s[15] = (double) System.currentTimeMillis();
  s[16] = (double) amount;
  s[17] = 0.0;
}""", acro))
# 0.4.14 (roll landings): RollSys.land (world thread, before the engine's FallDamagePlayers) - a landing whose roll engaged; amount = the fall
# damage WITHOUT the roll normalised to 100 max health (AcroFallSeenSys' scale); falls() pays it 400 ms later
acro.addMethod(CtNewMethod.make("""
public static void noteRoll(java.util.UUID u, float amount) {
  double[] s = state(u);
  s[288] = (double) System.currentTimeMillis();
  s[289] = (double) amount;
  s[290] = 0.0;
}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static boolean alive({ST} store, {REF} ref) {{
  try {{
    if (!ref.isValid()) return false;
    {ESM} m = ({ESM}) store.getComponent(ref, {ESM}.getComponentType());
    if (m == null) return true;
    int hi = {DST}.getHealth();
    if (hi < 0) return true;
    {ESV} hv = m.get(hi);
    return hv == null || hv.get() > 0.0f;
  }} catch (Throwable t) {{ return false; }}
}}""", acro))
# 0.4: in water / swimming (no fall XP there - the engine applies no fall damage in fluid either)
acro.addMethod(CtNewMethod.make(f"""
public static boolean inWater({ST} store, {REF} ref) {{
  try {{
    {MSC} msc = ({MSC}) store.getComponent(ref, {MSC}.getComponentType());
    if (msc == null) return false;
    {MVT} ms = msc.getMovementStates();
    return ms != null && (ms.inFluid || ms.swimming);
  }} catch (Throwable t) {{ return false; }}
}}""", acro))
# the ONE anti-exploit movement-state set (review fix: move() AND dodge() use it - the 0.2 draft only checked it in move())
acro.addMethod(CtNewMethod.make(f"""
public static boolean excludedState({MVT} ms) {{
  if (ms == null) return true;
  return ms.mounting || ms.flying || ms.gliding || ms.sitting || ms.sleeping || ms.climbing || ms.inFluid || ms.swimming || ms.mantling;
}}""", acro))
# running / jumping / landing detection for one tick
acro.addMethod(CtNewMethod.make(f"""
public static void move(double[] s, {MVT} ms, {V3D} pos, float dt, long now, boolean creative) {{
  double x = pos.x();
  double y = pos.y();
  double z = pos.z();
  boolean excluded = excludedState(ms);
  boolean tele = false;
  double hd = 0.0;
  if (s[3] > 0.5) {{
    double dx = x - s[0];
    double dy = y - s[1];
    double dz = z - s[2];
    hd = Math.sqrt(dx * dx + dz * dz);
    if (Math.sqrt(dx * dx + dy * dy + dz * dz) > {PKG}.AcroCfg.TELEPORT) tele = true;
    else if (dt > 0.0f && hd / (double) dt > {PKG}.AcroCfg.MAX_SPEED) tele = true;
  }}
  s[0] = x; s[1] = y; s[2] = z; s[3] = 1.0;
  if (tele) {{ hd = 0.0; s[8] = 0.0; s[18] = 0.0; }}
  boolean ground = ms.onGround;
  if (!tele && !excluded && !creative && ground && hd > 0.0) {{
    double rate = {PKG}.AcroCfg.RUN;
    if (ms.horizontalIdle || ms.idle) rate = 0.0;
    else if (ms.sprinting) rate = {PKG}.AcroCfg.SPRINT;
    else if (ms.walking || ms.crouching) rate = {PKG}.AcroCfg.WALK;
    s[11] = s[11] + hd * rate;
  }}
  if (!excluded) s[10] = s[10] + hd;
  boolean jmp = ms.jumping;
  if (jmp && s[5] < 0.5 && !excluded && !creative && !tele) {{
    if ((double) now - s[9] >= (double) {PKG}.AcroCfg.JUMP_CD && s[10] >= {PKG}.AcroCfg.JUMP_MOVE) {{
      s[11] = s[11] + {PKG}.AcroCfg.JUMP_XP;
      s[9] = (double) now;
      s[10] = 0.0;
    }}
  }}
  s[5] = jmp ? 1.0 : 0.0;
  if (excluded || tele) {{
    s[8] = 0.0;
  }} else if (!ground) {{
    if (s[8] < 0.5 || y > s[7]) s[7] = y;
    s[8] = 1.0;
  }} else {{
    if (s[4] < 0.5 && s[8] > 0.5) {{
      double drop = s[7] - y;
      if (drop >= {PKG}.AcroCfg.FALL_MIN && !creative) {{ s[18] = (double) now; s[19] = drop; }}
    }}
    s[8] = 0.0;
  }}
  s[4] = ground ? 1.0 : 0.0;
}}""", acro))
# 0.4 pay landings: ONLY a FALL damage that really applied (noted by AcroFallSeenSys in the Inspect damage group) pays, by its unreduced
# amount normalised to 100 max health, 0.4 s later if the player is alive and not in water; safe drops (no damage) pay nothing.
# (pre-0.4: a FALL damage event near the landing paid by damage (if alive), otherwise the drop paid per block.)
# Timing (verified in HytaleServer.jar): DamageSystems$FallDamagePlayers creates the FALL Damage from the SAME queued client
# SetMovementStates update (onGround) that PlayerSystems$ProcessPlayerInput applies to MovementStatesComponent, in the same world
# tick, so the damage note and the landing AcroSys sees are at most a tick apart; the note is paid at +400 ms, the landing at +700 ms.
# Review fix: a paid note is cleared (s[15] = 0) and the landing check only counts an UNRESOLVED note, so the timestamp of an
# earlier, already paid fall can no longer swallow the XP of the next safe landing within 1.5 s.
acro.addMethod(CtNewMethod.make(f"""
public static void falls(double[] s, {ST} store, {REF} ref, long now, boolean creative) {{
  double t = (double) now;
  if (s[15] > 0.0 && s[17] < 0.5 && t - s[15] >= 400.0) {{
    s[17] = 1.0;
    if (!creative && alive(store, ref) && !inWater(store, ref)) {{
      double x = s[16] * {PKG}.AcroCfg.FALL_DMG_XP;
      if (x > {PKG}.AcroCfg.FALL_MAX) x = {PKG}.AcroCfg.FALL_MAX;
      if (x > 0.0) s[152] = s[152] + x;
    }}
    s[15] = 0.0;
  }}
  // 0.4.14: a rolled landing pays the fall's UNREDUCED XP + acro.rollBonus of it (alive, not in water, not creative; acro.fallXpMax per landing,
  // acro.fallMaxXpPerMinute through takeFall in flush - the existing caps)
  if (s[288] > 0.0 && s[290] < 0.5 && t - s[288] >= 400.0) {{
    s[290] = 1.0;
    if (!creative && alive(store, ref) && !inWater(store, ref)) {{
      double x = s[289] * {PKG}.AcroCfg.FALL_DMG_XP * (1.0 + {PKG}.AcroCfg.ROLL);
      if (x > {PKG}.AcroCfg.FALL_MAX) x = {PKG}.AcroCfg.FALL_MAX;
      if (x > 0.0) s[152] = s[152] + x;
    }}
    s[288] = 0.0;
  }}
  if (s[18] > 0.0 && t - s[18] >= 700.0) s[18] = 0.0;
}}""", acro))
# 0.4.1 (Exploration-Build-Spec 3.4): the Acrobatics skill tree's dodge nodes - SkyyTrees 0.2 posts skill:bonus:<uuid> "dodge.acrobatics"
# (a fraction, like dodgeBonus); summed over every source, clamped 0..acro.treeDodgeMax; only while acro.enabled and acro.dodgeBoost
acro.addMethod(CtNewMethod.make(f"""
public static double treeDodge(java.util.UUID u) {{
  if (u == null || !{PKG}.AcroCfg.ENABLED || !{PKG}.AcroCfg.DODGE_BOOST) return 0.0;
  double t = {PKG}.SkillBonus.sum(u, "dodge.acrobatics");
  if (Double.isNaN(t) || t <= 0.0) return 0.0;
  double mx = {PKG}.AcroCfg.TREE_DODGE_MAX;
  return t > mx ? mx : t;
}}""", acro))
# dodge boost: extra push along the client's horizontal velocity (vanilla LaunchPadInteraction / knockback path: Velocity instruction ->
# PlayerVelocityInstructionSystem -> ChangeVelocity packet, VelocityConfig null like the launch pad)
acro.addMethod(CtNewMethod.make(f"""
public static void boost({CB} cb, {REF} ref, java.util.UUID u) {{
  double f = dodgeBonus({PKG}.SkillStore.level(u, {PKG}.SkillDefs.ACROBATICS)) + treeDodge(u);
  if (f <= 0.0) return;
  {VEL} v = ({VEL}) cb.getComponent(ref, {VEL}.getComponentType());
  if (v == null) return;
  {V3D} cv = v.getClientVelocity();
  if (cv == null) return;
  double hx = cv.x();
  double hz = cv.z();
  double hl = Math.sqrt(hx * hx + hz * hz);
  if (hl < 1.0) return;
  double add = {PKG}.AcroCfg.DODGE_FORCE * f;
  v.addInstruction(new {V3D}(hx / hl * add, 0.0, hz / hl * add), ({VCF}) null, {CVT}.Add);
}}""", acro))
# excluded = excludedState(MovementStates) of this tick (true when the component is missing): review fix - a dodge in an excluded
# state (mounted, flying, gliding, sitting, sleeping, climbing, in fluid, swimming, mantling) pays no XP and gets no push, exactly
# like running / jumping / falling in move(); a push still pending when the player enters such a state is dropped. The edge (s[6])
# is tracked in every state, so a Dodge effect that began while excluded is not counted when the state ends mid-effect.
acro.addMethod(CtNewMethod.make(f"""
public static void dodge(double[] s, {ST} store, {CB} cb, {REF} ref, java.util.UUID u, long now, boolean creative, boolean excluded) {{
  {ECC} ecc = ({ECC}) store.getComponent(ref, {ECC}.getComponentType());
  boolean on = false;
  if (ecc != null) {{
    int li = {EFX}.getAssetMap().getIndex("Dodge_Left");
    int ri = {EFX}.getAssetMap().getIndex("Dodge_Right");
    if (li != Integer.MIN_VALUE && ecc.hasEffect(li)) on = true;
    if (ri != Integer.MIN_VALUE && ecc.hasEffect(ri)) on = true;
  }}
  if (on && s[6] < 0.5 && !excluded && (double) now - s[20] >= (double) {PKG}.AcroCfg.DODGE_CD) {{
    s[20] = (double) now;
    if (!creative) s[11] = s[11] + {PKG}.AcroCfg.DODGE_XP;
    if ({PKG}.AcroCfg.DODGE_BOOST) s[23] = (double) (now + 100L);
  }}
  s[6] = on ? 1.0 : 0.0;
  if (s[23] > 0.0 && (double) now >= s[23]) {{
    s[23] = 0.0;
    if (on && !excluded) boost(cb, ref, u);
  }}
}}""", acro))
# sliding XP cap (review fix): per-second ring, see the STATE layout above
acro.addMethod(CtNewMethod.make("""
public static double paidRecently(double[] s, long sec) {
  double sum = 0.0;
  double lo = (double) (sec - 60L);
  double hi = (double) sec;
  for (int k = 0; k < 64; k++) {
    double at = s[88 + k];
    if (at >= lo && at <= hi) sum = sum + s[24 + k];
  }
  return sum;
}""", acro))
acro.addMethod(CtNewMethod.make("""
public static void addPaid(double[] s, long sec, double amt) {
  int k = (int) (sec % 64L);
  if (s[88 + k] != (double) sec) { s[88 + k] = (double) sec; s[24 + k] = 0.0; }
  s[24 + k] = s[24 + k] + amt;
}""", acro))
# whole XP that may be paid now under acro.maxXpPerMinute (0 = none); records what it allows
acro.addMethod(CtNewMethod.make(f"""
public static double take(double[] s, long now, double whole) {{
  long sec = now / 1000L;
  double room = {PKG}.AcroCfg.MAX_PER_MIN - paidRecently(s, sec);
  if (whole > room) whole = Math.floor(room);
  if (whole < 1.0) return 0.0;
  addPaid(s, sec, whole);
  return whole;
}}""", acro))
# 0.4: the fall XP ring (153-216 amounts, 217-280 seconds) - same sliding 61-second rule as the movement ring, own cap
acro.addMethod(CtNewMethod.make("""
public static double ringSum(double[] s, long sec, int a, int b) {
  double sum = 0.0;
  double lo = (double) (sec - 60L);
  double hi = (double) sec;
  for (int k = 0; k < 64; k++) {
    double at = s[b + k];
    if (at >= lo && at <= hi) sum = sum + s[a + k];
  }
  return sum;
}""", acro))
acro.addMethod(CtNewMethod.make("""
public static void ringAdd(double[] s, long sec, double amt, int a, int b) {
  int k = (int) (sec % 64L);
  if (s[b + k] != (double) sec) { s[b + k] = (double) sec; s[a + k] = 0.0; }
  s[a + k] = s[a + k] + amt;
}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static double takeFall(double[] s, long now, double whole) {{
  long sec = now / 1000L;
  double room = {PKG}.AcroCfg.FALL_PER_MIN - ringSum(s, sec, 153, 217);
  if (whole > room) whole = Math.floor(room);
  if (whole < 1.0) return 0.0;
  ringAdd(s, sec, whole, 153, 217);
  return whole;
}}""", acro))
# once per second: pay whole XP (sliding per-minute cap, global multiplier), throttled chat line
acro.addMethod(CtNewMethod.make(f"""
public static void flush({PR} pr, double[] s, long now) {{
  if (pr == null) return;
  double t = (double) now;
  double whole = Math.floor(s[11]);
  if (whole >= 1.0) {{
    s[11] = s[11] - whole;
    whole = take(s, now, whole);
    if (whole >= 1.0) {{
      long amt = {PKG}.SkillCfg.scaled((long) whole);
      if (amt > 0L) {{
        {PKG}.SkillXp.gain2(pr, {PKG}.SkillDefs.ACROBATICS, amt, false);
        s[21] = s[21] + (double) amt;
      }}
    }}
  }}
  double fw = Math.floor(s[152]);
  if (fw >= 1.0) {{
    s[152] = s[152] - fw;
    fw = takeFall(s, now, fw);
    if (fw >= 1.0) {{
      long famt = {PKG}.SkillCfg.scaled((long) fw);
      if (famt > 0L) {PKG}.SkillXp.gain2(pr, {PKG}.SkillDefs.ACROBATICS, famt, true);
    }}
  }}
  if (s[21] >= 1.0 && t - s[22] >= (double) {PKG}.AcroCfg.FEEDBACK_MS) {{
    long shown = (long) s[21];
    s[21] = 0.0;
    s[22] = t;
    {PKG}.SkillMsg.note(pr, {PKG}.SkillDefs.ACROBATICS, shown);
  }}
}}""", acro))
# once per second: publish this player's Acrobatics bonus (flat layer) and apply the protocol total
acro.addMethod(CtNewMethod.make(f"""
public static void bonuses(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref) {{
  int lvl = {PKG}.AcroCfg.ENABLED ? {PKG}.SkillStore.level(u, {PKG}.SkillDefs.ACROBATICS) : 0;
  {PKG}.MoveSync.post(u, SOURCE, "flat", (float) speedBonus(lvl), (float) jumpBonus(lvl), (float) (0.0 - fallBonus(lvl)));
  {PKG}.MoveSync.sync(u, pr, cb, ref, MOVE, MOD);
}}""", acro))

# ---- 0.4.2 stage 2: DOUBLE JUMP (research/Double-Jump-Spec.md 3.2). All of it runs in AcroSys.tick on the world thread. ----
acro.addField(CtField.make("public static volatile boolean DJ_WARNED = false;", acro))
# the node value = air-jump height as a fraction of the player's own jump height (SkyyTrees 0.2.1 skill:bonus doublejump.acrobatics,
# 0.55-1.0), clamped to acro.doubleJump.maxFraction; 0 = no node (also: node toggled off in /tree, bridge.bonus.enabled=false)
acro.addMethod(CtNewMethod.make(f"""
public static double djFraction(java.util.UUID u) {{
  if (u == null) return 0.0;
  double f = {PKG}.SkillBonus.sum(u, "doublejump.acrobatics");
  if (!(f > 0.0)) return 0.0;
  return f > {PKG}.AcroCfg.DJ_MAX_FRAC ? {PKG}.AcroCfg.DJ_MAX_FRAC : f;
}}""", acro))
# the REAL game mode (SkillXp.creative returns false when creativeXp=true, so it must not be reused here)
acro.addMethod(CtNewMethod.make(f"""
public static boolean creativeMode({ST} st, {REF} r) {{
  try {{
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    return p != null && p.getGameMode() == {GM}.Creative;
  }} catch (Throwable t) {{ return false; }}
}}""", acro))
# rule 7 falling-speed gate, 0 = no limit. Reads the WORLD's MovementConfig asset exactly like DamageSystems$FallDamagePlayers does for
# real fall damage. Do NOT "simplify" this to djSettings(...).minFallSpeedToEngageRoll: that per-player protocol MovementSettings is a
# toPacket() copy that movement mods rewrite, and fall damage never reads it, so the two can drift apart.
acro.addMethod(CtNewMethod.make(f"""
public static double djMaxFall({ST} store) {{
  double c = {PKG}.AcroCfg.DJ_MAX_FALL;
  if (c < 0.0) return 0.0;
  if (c > 0.0) return c;
  try {{
    {WLD} w = (({EST}) store.getExternalData()).getWorld();
    int mi = w.getGameplayConfig().getPlayerConfig().getMovementConfigIndex();
    {MCF} mc = ({MCF}) {MCF}.getAssetMap().getAsset(mi);
    if (mc != null && mc.getMinFallSpeedToEngageRoll() > 0.0f) return (double) mc.getMinFallSpeedToEngageRoll();
  }} catch (Throwable t) {{ }}
  return 21.0;
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static {MVS} djSettings({ST} store, {REF} ref) {{
  try {{
    {MMG} mm = ({MMG}) store.getComponent(ref, {MMG}.getComponentType());
    if (mm == null) return null;
    return mm.getSettings();
  }} catch (Throwable t) {{ return null; }}
}}""", acro))
# rule 5: false = not enough Stamina (no jump, the charge is kept); the cost is taken only when the jump really happens. The regen
# pause is its own try: a missing StaminaRegenDelay stat never cancels a jump that was already paid for.
acro.addMethod(CtNewMethod.make(f"""
public static boolean djStamina({CB} cb, {REF} ref) {{
  double cost = {PKG}.AcroCfg.DJ_STAMINA;
  if (cost <= 0.0) return true;
  try {{
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());
    if (m == null) return true;
    int si = {DST}.getStamina();
    {ESV} sv = m.get(si);
    if (sv == null) return true;
    if ((double) sv.get() < cost) return false;
    m.subtractStatValue(si, (float) cost);
    if ({PKG}.AcroCfg.DJ_REGEN_DELAY > 0.0) {{
      try {{
        int di = {ESTT}.getAssetMap().getIndex("StaminaRegenDelay");
        if (di >= 0) m.setStatValue(di, (float) (0.0 - {PKG}.AcroCfg.DJ_REGEN_DELAY));
      }} catch (Throwable t2) {{ }}
    }}
    return true;
  }} catch (Throwable t) {{
    if (!DJ_WARNED) {{ DJ_WARNED = true; {PKG}.SkillCfg.warn("double jump stamina failed (logged once): " + t); }}
    return false;
  }}
}}""", acro))
# optional polish (acro.doubleJump.fx), never throws: the native extra-jump sound of Debug_Movement_Boots + vanilla Double_Jump.json's
# particle at the feet (target list = the jumper, the TerrariaAddons pattern)
acro.addMethod(CtNewMethod.make(f"""
public static void djFx({ST} store, {REF} ref) {{
  if (!{PKG}.AcroCfg.DJ_FX) return;
  {V3D} p = null;
  try {{
    {TRC} tc = ({TRC}) store.getComponent(ref, {TRC}.getComponentType());
    if (tc != null) p = tc.getPosition();
  }} catch (Throwable t) {{ p = null; }}
  if (p == null) return;
  try {{
    int si = {SEV}.getAssetMap().getIndex("SFX_Player_Jump");
    if (si >= 0) {SNU}.playSoundEvent3d(si, {SCAT}.SFX, p, store);
  }} catch (Throwable t) {{ }}
  try {{
    {PTU}.spawnParticleEffect("Impact_Feathers_Black", p, java.util.Collections.singletonList(ref), store);
  }} catch (Throwable t) {{ }}
}}""", acro))
# acro.doubleJump.debug (spec test 5.0): one chat line per airborne edge, admins only, at most one per 200 ms
acro.addMethod(CtNewMethod.make(f"""
public static void djDebug(double[] s, {PR} pr, String what, double vy, long now) {{
  if (pr == null || (double) now - s[286] < 200.0) return;
  try {{ if (!pr.hasPermission("skyyskills.admin")) return; }} catch (Throwable t) {{ return; }}
  s[286] = (double) now;
  long air = 0L;
  if (s[284] > 0.0) air = now - (long) s[284];
  pr.sendMessage({MSG}.raw("[Skills] DJ debug: " + what + " in air - vy " + (Math.round(vy * 10.0) / 10.0) + " - air " + air + " ms - used " + (int) s[282]).color("#c8a0ff"));
}}""", acro))
# PURE (no engine object, bare-JVM tested): the edges of this tick and the airtime. Returns bits 1 = crouch press, 2 = jump press,
# 4 = extraJumpsUsed changed; 0 = on the ground / climbing / in fluid / swimming / mantling (charge + airtime reset, spec 2.3 rule 2),
# in any other Acro.excludedState (mounted / flying / gliding / sitting / sleeping: airtime restarts, the charge is KEPT - review fix:
# time spent flying or gliding no longer counts toward minAirMs, and a mid-air glide toggle can never refill the jump) or no edge.
acro.addMethod(CtNewMethod.make(f"""
public static int airTrack(double[] s, {MVT} ms, long now) {{
  boolean cEdge = ms.crouching && s[281] < 0.5;
  boolean jEdge = ms.jumping && s[285] < 0.5;
  int xj = (int) ms.extraJumpsUsed;
  boolean xEdge = (double) xj != s[287];
  s[281] = ms.crouching ? 1.0 : 0.0;
  s[285] = ms.jumping ? 1.0 : 0.0;
  s[287] = (double) xj;
  if (ms.onGround || ms.climbing || ms.inFluid || ms.swimming || ms.mantling) {{ s[282] = 0.0; s[284] = 0.0; return 0; }}
  if (excludedState(ms)) {{ s[284] = 0.0; return 0; }}
  if (s[284] <= 0.0) s[284] = (double) now;
  int bits = 0;
  if (cEdge) bits = bits | 1;
  if (jEdge) bits = bits | 2;
  if (xEdge) bits = bits | 4;
  return bits;
}}""", acro))
# PURE: true = this tick has an edge of the configured trigger (acro.doubleJump.trigger crouch 0 / jump 1 / both 2). airJump's coarse
# gate (review fix: a stray edge of the other key no longer runs the node / movement-settings / MovementConfig lookups); airTry keeps
# its own byCrouch / byJump (rule J needs them).
acro.addMethod(CtNewMethod.make(f"""
public static boolean djTrig(int bits) {{
  int trig = {PKG}.AcroCfg.DJ_TRIGGER;
  if (trig != 1 && (bits & 1) != 0) return true;
  return trig != 0 && (bits & 2) != 0;
}}""", acro))
# PURE: the gates of spec 2.3 that need no engine object + the push speed. f = node fraction, vy0 = the client's vertical speed now,
# mf = falling-speed limit (0 = none), jf / fj = the player's jumpForce / fallJumpForce. Returns vy > 0 = jump now, else a reason:
# -1 no trigger edge, -2 too soon after leaving the ground, -3 no charge left, -4 cooldown, -5 no node, -6 falling too fast,
# -7 jump mode: the client jumped itself (coyote / buffered jump, rule J), -8 no push.
acro.addMethod(CtNewMethod.make(f"""
public static double airTry(double[] s, int bits, long now, double f, double vy0, double mf, double jf, double fj) {{
  int trig = {PKG}.AcroCfg.DJ_TRIGGER;
  boolean byCrouch = trig != 1 && (bits & 1) != 0;
  boolean byJump = trig != 0 && (bits & 2) != 0;
  if (!byCrouch && !byJump) return -1.0;
  if ((double) now - s[284] < (double) {PKG}.AcroCfg.DJ_MIN_AIR) return -2.0;
  if (s[282] >= (double) {PKG}.AcroCfg.DJ_MAX_JUMPS) return -3.0;
  if ((double) now - s[283] < (double) {PKG}.AcroCfg.DJ_CD) return -4.0;
  if (!(f > 0.0)) return -5.0;
  if (mf > 0.0 && vy0 < 0.0 - mf) return -6.0;
  if (!byCrouch && vy0 > 0.5 * fj) return -7.0;
  double vy = jf * Math.sqrt(f);
  double cap = Math.sqrt(2.0 * {PHC}.GRAVITY_ACCELERATION * {PKG}.AcroCfg.DJ_MAX_BLOCKS);
  if (vy > cap) vy = cap;
  if (!(vy > 0.0)) return -8.0;
  return vy;
}}""", acro))
# the engine glue (world thread, every tick). Stamina is taken AFTER every other gate, so a refused jump never costs Stamina or a charge.
# Review fix: the debug probe (spec test 5.0) runs BEFORE the acro.doubleJump.enabled check, so it also reports edges while the double
# jump itself is off (it still needs acro.enabled: AcroSys only calls airJump then).
acro.addMethod(CtNewMethod.make(f"""
public static void airJump(double[] s, {ST} store, {CB} cb, {REF} ref, {PR} pr, java.util.UUID u, {MVT} ms, long now) {{
  if (ms == null) return;
  int bits = airTrack(s, ms, now);
  if (bits == 0) return;
  if (!{PKG}.AcroCfg.DJ_ON && !{PKG}.AcroCfg.DJ_DEBUG) return;
  {VEL} v = ({VEL}) cb.getComponent(ref, {VEL}.getComponentType());
  {V3D} cv = null;
  if (v != null) cv = v.getClientVelocity();
  double vy0 = 0.0;
  if (cv != null) vy0 = cv.y();
  if ({PKG}.AcroCfg.DJ_DEBUG) {{
    String what = "extraJumpsUsed " + (int) ms.extraJumpsUsed;
    if ((bits & 2) != 0) what = "jump edge";
    if ((bits & 1) != 0) what = "crouch edge";
    djDebug(s, pr, what, vy0, now);
  }}
  if (!{PKG}.AcroCfg.DJ_ON || !djTrig(bits) || v == null || cv == null) return;
  if (excludedState(ms) || creativeMode(store, ref)) return;
  double f = djFraction(u);
  if (f <= 0.0) return;
  {MVS} st = djSettings(store, ref);
  double jf = 11.8;
  double fj = 7.0;
  if (st != null && st.jumpForce > 0.0f) jf = (double) st.jumpForce;
  if (st != null && st.fallJumpForce > 0.0f) fj = (double) st.fallJumpForce;
  double vy = airTry(s, bits, now, f, vy0, djMaxFall(store), jf, fj);
  if (vy <= 0.0) return;
  if (!djStamina(cb, ref)) return;
  double hx = cv.x();
  double hz = cv.z();
  double hl = Math.sqrt(hx * hx + hz * hz);
  double fw = {PKG}.AcroCfg.DJ_FORWARD;
  if (hl >= 1.0 && fw > 0.0) {{ hx = hx + hx / hl * fw; hz = hz + hz / hl * fw; }}
  v.addInstruction(new {V3D}(hx, vy, hz), ({VCF}) null, {CVT}.Set);
  s[282] = s[282] + 1.0;
  s[283] = (double) now;
  s[9] = (double) now;
  if ({PKG}.AcroCfg.DJ_XP > 0.0 && !{PKG}.SkillXp.creative(store, ref)) s[11] = s[11] + {PKG}.AcroCfg.DJ_XP;
  djFx(store, ref);
}}""", acro))
# Stats page line while the node is owned (null = no node); the key words follow acro.doubleJump.trigger
acro.addMethod(CtNewMethod.make(f"""
public static String djLine(java.util.UUID u) {{
  double f = djFraction(u);
  if (f <= 0.0) return null;
  if (!{PKG}.AcroCfg.DJ_ON) return "Double Jump (skill tree) is turned off on this server";
  double st = {PKG}.AcroCfg.DJ_STAMINA;
  String sc = String.valueOf(st);
  if (st == Math.floor(st)) sc = String.valueOf((long) st);
  String cost = "";
  if (st > 0.0) cost = " - " + sc + " Stamina";
  return "Double Jump: press " + {PKG}.AcroCfg.DJ_KEY + " in mid-air for a " + Math.round(f * 100.0) + "% jump" + cost;
}}""", acro))
# bridge skill:dj:key (spec 3.3) for the SkyyTrees 0.2.1 card "Press %K in mid-air": setup + /skills reload; removed in shutdown
acro.addMethod(CtNewMethod.make(f"""
public static void djPublish() {{
  try {{ {PKG}.SkillStore.bridge().put("skill:dj:key", {PKG}.AcroCfg.DJ_KEY); }} catch (Throwable t) {{ }}
}}""", acro))

# ---- 0.4.5 Xbow part 2: crossbows stay loaded - the epoch check, the hotbar switch and the restore (Crossbow-Loaded-Spec 2.4 / 2.5) ----
# spec 2.4 / review 7.4: the profile epoch this state was built under. Absent = no information; the first value is a baseline (the
# Perks.epochChanged rule); a different value wipes the state and turns the cached flag off (Perks.switched -> refresh brings it back
# within 1 s, so no profile file is loaded here). false = wiped now.
xbw.addMethod(CtNewMethod.make(f"""
public static boolean fresh({PKG}.XbowState s, java.util.UUID u) {{
  long e = {PKG}.Perks.epoch(u);
  if (e < 0L) return true;
  if (s.epoch < 0L) {{ s.epoch = e; return true; }}
  if (s.epoch == e) return true;
  reset(s);
  s.epoch = e;
  ON.put(u, Boolean.FALSE);
  return false;
}}""", xbw))
# spec 2.4, from XbowSlotSys (world thread, inside setActiveSlot: the hotbar already shows `neu`, Ammo is still the load vanilla's SwapFrom
# ladder just refunded). A. leaving `prev`, B. arriving at `neu`. No state is created for a player without the perk.
xbw.addMethod(CtNewMethod.make(f"""
public static void onSlot({ST} st, {REF} ref, {PR} pr, java.util.UUID u, int prev, int neu) {{
  try {{
    if (u == null || ref == null) return;
    {PKG}.XbowState s = ({PKG}.XbowState) S.get(u);
    if (s == null) {{
      if (!{PKG}.XbowCfg.ON || !active(u)) return;
      s = state(u);
    }}
    if (rebind(s, ref, pr) == 1) dbg(pr, "kept loads survive the world change");
    fresh(s, u);
    boolean act = {PKG}.XbowCfg.ON && active(u);
    {HOTB} hb = ({HOTB}) st.getComponent(ref, {HOTB}.getComponentType());
    if (hb == null) return;
    {ICON} c = hb.getInventory();
    if (c == null) return;
    int cap = c.getCapacity();
    String msg = null;
    if (prev >= 0 && prev < s.n.length) {{
      if (s.pendSlot != prev) {{
        boolean kept = false;
        {IS} is = prev < cap ? c.getItemStack((short) prev) : null;
        if (act && is != null && !is.isEmpty() && s.ticks - s.enterAt >= (long) {PKG}.XbowCfg.DELAY && allowed(u, is.getItemId())) {{
          {ESM} esm = ({ESM}) st.getComponent(ref, {ESM}.getComponentType());
          {ESV} v = esm == null ? null : esm.get({DST}.getAmmo());
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
        if (!kept) clearSlot(s, prev);
      }}
    }}
    s.pendSlot = -1;
    s.enterAt = s.ticks;
    if (hasKept(s, neu)) {{
      {IS} ns = neu < cap ? c.getItemStack((short) neu) : null;
      if (act && ns != null && !ns.isEmpty() && s.stk[neu] != null && ns.isEquivalentType(s.stk[neu])) {{
        s.pendSlot = neu;
        s.pendAt = s.ticks;
      }} else {{
        if (msg == null) msg = act ? "load dropped - crossbow left slot " + (neu + 1) : "load dropped - the perk is not active right now";
        clearSlot(s, neu);
      }}
    }}
    if (msg != null) dbg(pr, msg);
  }} catch (Throwable t) {{ failed("slot switch", t); }}
}}""", xbw))
# spec 2.5, every AcroSys tick (world thread, before its 1 s gate). Nearly every player / tick: no state -> return at once.
xbw.addMethod(CtNewMethod.make(f"""
public static void tick({ST} st, {REF} ref, {PR} pr, java.util.UUID u) {{
  {PKG}.XbowState s = ({PKG}.XbowState) S.get(u);
  if (s == null) return;
  try {{
    s.ticks = s.ticks + 1L;
    int rb = rebind(s, ref, pr);
    if (rb == 2) return;
    if (rb == 1) dbg(pr, "kept loads survive the world change");
    if (!fresh(s, u)) return;
    if (st.getComponent(ref, {DTH}.getComponentType()) != null) {{ reset(s); return; }}
    if (!{PKG}.XbowCfg.ON || !Boolean.TRUE.equals(ON.get(u))) {{ forget(u); return; }}
    int slot = s.pendSlot;
    if (slot < 0 || slot >= s.n.length) return;
    if (s.ticks - s.pendAt > 60L) {{ drop(s, slot); dbg(pr, "load dropped - the bolt counter did not come back within 60 ticks"); return; }}
    if (busy(u)) return;
    if (s.ticks < s.pendAt + (long) {PKG}.XbowCfg.DELAY) return;
    {HOTB} hb = ({HOTB}) st.getComponent(ref, {HOTB}.getComponentType());
    if (hb == null || hb.getActiveSlot() != slot) {{ drop(s, slot); dbg(pr, "load dropped - crossbow left slot " + (slot + 1)); return; }}
    {ICON} c = hb.getInventory();
    {IS} is = (c == null || slot >= c.getCapacity()) ? null : c.getItemStack((short) slot);
    if (is == null || is.isEmpty() || s.stk[slot] == null || !is.isEquivalentType(s.stk[slot])) {{ drop(s, slot); dbg(pr, "load dropped - crossbow left slot " + (slot + 1)); return; }}
    {ESM} esm = ({ESM}) st.getComponent(ref, {ESM}.getComponentType());
    int ai = {DST}.getAmmo();
    {ESV} v = esm == null ? null : esm.get(ai);
    if (v == null || v.getMax() < 1.0f) return;
    int mx = (int) Math.floor((double) v.getMax());
    int want = s.n[slot];
    int target = want < mx ? want : mx;
    int cur = (int) Math.floor((double) v.get());
    if (cur < 0) cur = 0;
    int need = target - cur;
    boolean mw = (s.sig[slot] > 0.0f || s.chg[slot] > 0.0f) && meterOn(u);
    if (need <= 0 && !mw) {{ drop(s, slot); dbg(pr, "nothing to put back - " + cur + " bolts already loaded"); return; }}
    String id = is.getItemId();
    if (!eligibleNow(u, id)) {{
      drop(s, slot);
      ON.put(u, rules(u) ? Boolean.TRUE : Boolean.FALSE);
      dbg(pr, "load dropped - not allowed right now (class, Archery level or weapon)");
      return;
    }}
    boolean free = s.cre[slot] && {PKG}.Acro.creativeMode(st, ref);
    int pay = 0;
    int have = 0;
    if (need <= 0) {{
      pay = 0;
    }} else if (free) {{
      pay = need;
    }} else {{
      {CIC} comb = {INVC}.getCombined(st, ref, {INVC}.HOTBAR_STORAGE_BACKPACK);
      if (comb != null) {{
        int cc = comb.getCapacity();
        for (int i = 0; i < cc; i++) {{
          {IS} a = comb.getItemStack((short) i);
          if (a != null && !a.isEmpty() && ARROW.equals(a.getItemId())) have = have + a.getQuantity();
        }}
        pay = need < have ? need : have;
        if (pay > 0) {{
          {IST} tx = comb.removeItemStack(new {IS}(ARROW, pay), true, true);
          if (tx == null || !tx.succeeded()) {{
            pay = 0;
          }} else {{
            int left = 0;
            for (int i = 0; i < cc; i++) {{
              {IS} a = comb.getItemStack((short) i);
              if (a != null && !a.isEmpty() && ARROW.equals(a.getItemId())) left = left + a.getQuantity();
            }}
            int took = have - left;
            if (took < pay) pay = took < 0 ? 0 : took;
          }}
        }}
      }}
    }}
    float sg = s.sig[slot];
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
    else dbg(pr, "put back " + pay + " of " + need + " bolts - only " + pay + " Crude Arrows" + mt);
  }} catch (Throwable t) {{
    s.pendSlot = -1;
    failed("restore", t);
  }}
}}""", xbw))

# ================= ManaRegen (0.4.12): Mana regen in combat + the Mana Regen % registry (Skyy 2026-10-02 Q&A rounds 1-2) =================
# research/Mana-Cost-And-Regen-Research.md 2.1-2.3: vanilla Mana.json = every 0.2 s +1 Additive while Alive, NoDamageTaken (6 s) and not
# Charging (inverse) - 5 a second out of combat, 0 for 6 s after taking damage, 0 while holding a charge. SRC = UUID -> ConcurrentHashMap
# source -> Double Mana Regen % (other mods, skill:fn:manaregen; memory only: providers register live like move:<uuid>); CLK = UUID ->
# float[]{seconds since the last pulse} (pruned to online players by Acro.retainOnline).
mrg.addMethod(CtNewMethod.make("""
public static double clampTotal(double sum) {
  if (!(sum > 0.0)) return 0.0;
  return sum > MAX_PCT ? MAX_PCT : sum;
}""", mrg))
# the % that applies to this player: the sum of every source, below 0 = 0 (no drain), at most MAX_PCT; NaN / infinite entries skipped
mrg.addMethod(CtNewMethod.make("""
public static double total(java.util.UUID u) {
  if (u == null) return 0.0;
  Object o = SRC.get(u);
  if (!(o instanceof java.util.Map)) return 0.0;
  double sum = 0.0;
  java.util.Iterator it = ((java.util.Map) o).values().iterator();
  while (it.hasNext()) {
    Object v = it.next();
    if (!(v instanceof Number)) continue;
    double x = ((Number) v).doubleValue();
    if (Double.isNaN(x) || Double.isInfinite(x)) continue;
    sum = sum + x;
  }
  return clampTotal(sum);
}""", mrg))
# set (replace) one source's % for a player; 0 removes it; false = bad arguments (no player, source 1-64 characters, a finite number)
mrg.addMethod(CtNewMethod.make("""
public static boolean put(java.util.UUID u, String src, double pct) {
  if (u == null || src == null) return false;
  String s = src.trim();
  if (s.length() == 0 || s.length() > 64 || Double.isNaN(pct) || Double.isInfinite(pct)) return false;
  double v = pct < -1000.0 ? -1000.0 : (pct > 1000.0 ? 1000.0 : pct);
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) SRC.get(u);
  if (v == 0.0) {
    if (m != null) m.remove(s);
    return true;
  }
  if (m == null) {
    java.util.concurrent.ConcurrentHashMap nm = new java.util.concurrent.ConcurrentHashMap();
    Object o = SRC.putIfAbsent(u, nm);
    m = o == null ? nm : (java.util.concurrent.ConcurrentHashMap) o;
  }
  m.put(s, Double.valueOf(v));
  return true;
}""", mrg))
mrg.addMethod(CtNewMethod.make("""
public static boolean remove(java.util.UUID u, String src) {
  if (u == null || src == null) return false;
  Object o = SRC.get(u);
  if (!(o instanceof java.util.Map)) return false;
  return ((java.util.Map) o).remove(src.trim()) != null;
}""", mrg))
# "source=+20" for every source of this player, sorted by source
mrg.addMethod(CtNewMethod.make(f"""
public static String[] sources(java.util.UUID u) {{
  Object o = u == null ? null : SRC.get(u);
  if (!(o instanceof java.util.Map)) return new String[0];
  java.util.TreeMap t = new java.util.TreeMap((java.util.Map) o);
  String[] r = new String[t.size()];
  int i = 0;
  java.util.Iterator it = t.entrySet().iterator();
  while (it.hasNext() && i < r.length) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    double v = ((Number) e.getValue()).doubleValue();
    r[i] = e.getKey() + "=" + (v >= 0.0 ? "+" : "") + {PKG}.Overall.num(v);
    i++;
  }}
  return r;
}}""", mrg))
# remove a source from every player (a provider's shutdown); returns how many players had it
mrg.addMethod(CtNewMethod.make("""
public static int clear(String src) {
  if (src == null) return 0;
  String s = src.trim();
  int n = 0;
  java.util.Iterator it = SRC.values().iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (o instanceof java.util.Map && ((java.util.Map) o).remove(s) != null) n++;
  }
  return n;
}""", mrg))
# per second of one regen entry: Additive with a positive amount and interval -> amount / interval (vanilla Mana: 1 / 0.2 s = 5), else 0
# (the Creative Percentage entry, drains)
mrg.addMethod(CtNewMethod.make(f"""
public static float baseOf({RGN} rg) {{
  if (rg == null || rg.getRegenType() != {RGT}.ADDITIVE) return 0.0f;
  float a = rg.getAmount();
  float iv = rg.getInterval();
  if (!(a > 0.0f) || !(iv > 0.0f)) return 0.0f;
  return a / iv;
}}""", mrg))
# the entry's OWN engine conditions, one by one (Condition.eval = eval0 with the inverse flag; exactly what RegeneratingValue.shouldRegenerate
# checks after its timer step - we never call shouldRegenerate / regenerate, they advance the engine's timer): 0 = all pass (vanilla
# regenerates: OUT of combat), 1 = only NoDamageTaken fails (vanilla's in-combat pause), 2 = anything else fails (dead, ...).
# 0.4.13 (Skyy: Mana keeps regenerating while you charge): 3 = only Charging fails - an INVERSE Charging, its eval0 says the player IS
# charging (vanilla withholds its refill: out of combat), 4 = NoDamageTaken + that Charging (charging in combat). A non-inverse Charging
# that fails (eval0 false) is "anything else" (2), and so is dead (Alive fails) whatever else fails with it.
mrg.addMethod(CtNewMethod.make(f"""
public static int state({CAC} acc, {REF} ref, java.time.Instant now, {RGN} rg) {{
  {CND}[] cs = rg.getConditions();
  if (cs == null) return 0;
  boolean nd = false;
  boolean ch = false;
  for (int i = 0; i < cs.length; i++) {{
    if (cs[i] == null) continue;
    if (cs[i].eval(acc, ref, now)) continue;
    if (cs[i] instanceof {NDT}) nd = true;
    else if (cs[i] instanceof {CHG} && cs[i].eval0(acc, ref, now)) ch = true;
    else return 2;
  }}
  if (ch) return nd ? 4 : 3;
  return nd ? 1 : 0;
}}""", mrg))
# {{base, out, in, chargeOut, chargeIn}} per second over the Mana value's regen entries: base = every positive Additive entry (vanilla 5),
# out = the ones running now, in = the ones vanilla's combat pause stops (charging or not - 0.4.13), chargeOut = the ones only charging
# stops (out of combat: SkyySkills refills them whole, 0.4.13), chargeIn = the part of in that is also charging (texts only)
mrg.addMethod(CtNewMethod.make(f"""
public static float[] rates({CAC} acc, {REF} ref, java.time.Instant now, {RGV}[] rv) {{
  float[] r = new float[] {{ 0.0f, 0.0f, 0.0f, 0.0f, 0.0f }};
  if (rv == null) return r;
  for (int i = 0; i < rv.length; i++) {{
    if (rv[i] == null) continue;
    {RGN} rg = rv[i].getRegenerating();
    float b = baseOf(rg);
    if (!(b > 0.0f)) continue;
    r[0] = r[0] + b;
    int st = state(acc, ref, now, rg);
    if (st == 0) r[1] = r[1] + b;
    else if (st == 1) r[2] = r[2] + b;
    else if (st == 3) r[3] = r[3] + b;
    else if (st == 4) {{ r[2] = r[2] + b; r[4] = r[4] + b; }}
  }}
  return r;
}}""", mrg))
# THE maths (pure): Mana SkyySkills adds now = (out x MR / 100 + in x (1 + MR / 100) x F / 100) x seconds, never past max, 0 without a
# Mana pool (max 0) or at max. MR = Mana Regen % (below 0 = 0, at most MAX_PCT), F = mana.regen.inCombat (0-100).
# 0.4.13: + chargeOut x (1 + MR / 100) when r has a 4th entry (rates' chargeOut): the refill vanilla withholds while charging out of
# combat, whole, + the boosts the out-of-combat path adds; charging in combat is in r[2] (the in-combat amount).
mrg.addMethod(CtNewMethod.make("""
public static float amount(float[] r, double pct, int factor, float secs, float cur, float max) {
  if (r == null || r.length < 3 || !(max > 0.0f) || !(cur < max) || !(secs > 0.0f)) return 0.0f;
  double p = pct > 0.0 ? (pct > MAX_PCT ? MAX_PCT : pct) : 0.0;
  int f = factor < 0 ? 0 : (factor > 100 ? 100 : factor);
  double per = (double) r[1] * p / 100.0 + (double) r[2] * (1.0 + p / 100.0) * (double) f / 100.0;
  if (r.length > 3) per = per + (double) r[3] * (1.0 + p / 100.0);
  double a = per * (double) secs;
  if (!(a > 0.0)) return 0.0f;
  double room = (double) (max - cur);
  if (a > room) a = room;
  return (float) a;
}""", mrg))
# ================= 0.4.13: the combat state for skill:fn:combat (SkyyHud's Combat widget) - ONE source of truth with the Mana regen
# In combat = vanilla's combat pause on the Mana regen: a NoDamageTaken condition of one of the positive Additive Mana regen entries (the
# entries rates() counts, the conditions state() keys on) FAILS at the world's own clock - the test the in-combat refill runs.
# The condition's Delay (NoDamageTakenCondition.delay is protected): the smallest d with eval0 true d after the last hit (eval0 =
# TimeUtil.compareDifference(last, last + d, Delay) >= 0) - doubling from 1 ms, then halving to the nanosecond; at most NDLY_CAP. Cached
# per condition object. -1 = unknown (no real hit yet, or not found).
mrg.addMethod(CtNewMethod.make(f"""
public static long delayOf({CND} c, {CAC} acc, {REF} ref, java.time.Instant last) {{
  Object k = NDLY.get(c);
  if (k != null) return ((Long) k).longValue();
  if (last == null || last.equals(java.time.Instant.MIN)) return -1L;
  long d = -1L;
  if (c.eval0(acc, ref, last)) d = 0L;
  else {{
    long lo = 0L;
    long hi = 1000000L;
    while (hi <= NDLY_CAP && !c.eval0(acc, ref, last.plusNanos(hi))) {{ lo = hi; hi = hi * 2L; }}
    if (hi <= NDLY_CAP) {{
      while (hi - lo > 1L) {{
        long mid = lo + (hi - lo) / 2L;
        if (c.eval0(acc, ref, last.plusNanos(mid))) hi = mid;
        else lo = mid;
      }}
      d = hi;
    }}
  }}
  if (d >= 0L) {{
    if (NDLY.size() > 64) NDLY.clear();
    NDLY.put(c, Long.valueOf(d));
  }}
  return d;
}}""", mrg))
# ms until the combat pause ends: every NoDamageTaken condition (of those entries) that FAILS now -> its Delay minus the time since the
# last hit (the DamageDataComponent the condition reads, the same instant), rounded UP, at least 1 and at most the Delay while the engine
# says in combat; the largest; 0 = none fails = out of combat. Sets WINDOW. Any accessor (the harness drives it with real conditions).
mrg.addMethod(CtNewMethod.make(f"""
public static long combatLeft({CAC} acc, {REF} ref, java.time.Instant now, {RGV}[] rv) {{
  if (rv == null || now == null) return 0L;
  long best = 0L;
  long win = 0L;
  java.time.Instant last = null;
  boolean got = false;
  for (int i = 0; i < rv.length; i++) {{
    if (rv[i] == null) continue;
    {RGN} rg = rv[i].getRegenerating();
    if (!(baseOf(rg) > 0.0f)) continue;
    {CND}[] cs = rg.getConditions();
    if (cs == null) continue;
    for (int j = 0; j < cs.length; j++) {{
      if (!(cs[j] instanceof {NDT})) continue;
      if (cs[j].eval(acc, ref, now)) continue;
      if (!got) {{
        got = true;
        {DDC} dd = ({DDC}) acc.getComponent(ref, {DDC}.getComponentType());
        if (dd != null) last = dd.getLastDamageTime();
      }}
      long d = delayOf(cs[j], acc, ref, last);
      long w = d > 0L ? (d + 999999L) / 1000000L : 0L;
      long l = 1L;
      if (d > 0L && last != null) {{
        long el = -1L;
        try {{ el = last.until(now, java.time.temporal.ChronoUnit.NANOS); }} catch (Throwable t) {{ el = -1L; }}
        if (el < 0L) l = w;
        else if (el < d) l = (d - el + 999999L) / 1000000L;
      }}
      if (l < 1L) l = 1L;
      if (w > 0L && l > w) l = w;
      if (l > best) {{ best = l; win = w; }}
    }}
  }}
  if (win > 0L) WINDOW = win;
  return best;
}}""", mrg))
# world thread, every Mana regen pulse (ManaRegen.tick, before any of its returns): remember the state; out of combat = no entry. Own try.
mrg.addMethod(CtNewMethod.make(f"""
public static void combat(java.util.UUID u, {CAC} acc, {REF} ref, java.time.Instant now, {RGV}[] rv) {{
  if (u == null) return;
  try {{
    long l = combatLeft(acc, ref, now, rv);
    if (l > 0L) CMB.put(u, new long[] {{ l, System.currentTimeMillis() }});
    else CMB.remove(u);
  }} catch (Throwable t) {{
    CMB.remove(u);
    if (!CFAILED_ONCE) {{ CFAILED_ONCE = true; {PKG}.SkillCfg.warn("combat state (skill:fn:combat) failed (logged once): " + t); }}
  }}
}}""", mrg))
# skill:fn:combat's answer at wall time w (ANY thread, memory only): the last pulse's ms counted down on the wall clock; while that pulse
# is at most STALE_MS old it stays >= 1 (only the next pulse - the Mana regen's own test - ends combat); a player no longer ticked runs out
# on the wall clock (and the entry is dropped). 0 = out of combat / unknown.
mrg.addMethod(CtNewMethod.make("""
public static long combatNow(java.util.UUID u, long w) {
  if (u == null) return 0L;
  Object o = CMB.get(u);
  if (o == null) return 0L;
  long[] e = (long[]) o;
  if (e.length < 2 || e[0] <= 0L) return 0L;
  long age = w - e[1];
  if (age < 0L) age = 0L;
  long l = e[0] - age;
  if (age <= STALE_MS) return l < 1L ? 1L : l;
  if (l > 0L) return l;
  CMB.remove(u, o);
  return 0L;
}""", mrg))
# ================= 0.4.13 fix F1: stamps from another world's clock (every world saves its own TimeResource clock; the player's
# DamageDataComponent travels with its Holder). ns from a to b on the world clock, never throwing (an overflow = the far end of a long).
mrg.addMethod(CtNewMethod.make("""
public static long nsBetween(java.time.Instant a, java.time.Instant b) {
  try {
    return a.until(b, java.time.temporal.ChronoUnit.NANOS);
  } catch (Throwable t) {
    return b.isAfter(a) ? Long.MAX_VALUE : Long.MIN_VALUE;
  }
}""", mrg))
# THE carry rule (pure, any thread; the harness drives it with records it builds): the stamp to write instead of s, null = keep s.
# s = one stamp now (i: 0 lastDamageTime, 1 lastCombatAction, 2 lastChargeTime), wn / now / dil / wall = this pulse's world name, clock,
# time dilation and System.nanoTime(); rec = the last pulse's CARRY record. In ANOTHER world (wn differs from the record's): s is still
# the old world's stamp when it equals the recorded one, or when it lies after the recorded clock by at most the wall gap x the old
# dilation + CARRY_SLACK (a hit there after its last pulse) and NOT in this world's own window (now - gap x dil - CARRY_SLACK .. now =
# where a fresh hit here lies: left alone). Then real ns since s = (old clock - s) / old dilation + gap, and the new stamp = now - real x
# dil (a world's clock = real time x its dilation); real over CARRY_CAP = Instant.MIN (never hit: passes every NoDamageTaken Delay).
# Always: a stamp in the future of this world's clock (nothing else can make one: the clock only moves forward) = now. Instant.MIN stays.
mrg.addMethod(CtNewMethod.make("""
public static java.time.Instant carried(java.time.Instant s, String wn, java.time.Instant now, float dil, long wall, Object[] rec, int i) {
  if (s == null || now == null || s.equals(java.time.Instant.MIN)) return null;
  java.time.Instant out = null;
  if (wn != null && rec != null && rec.length >= 7 && i >= 0 && i < 3 && rec[0] instanceof String && !wn.equals(rec[0])
      && rec[1] instanceof java.time.Instant && rec[2] instanceof Long && rec[3] instanceof Float) {
    java.time.Instant rn = (java.time.Instant) rec[1];
    long gap = wall - ((Long) rec[2]).longValue();
    if (gap < 0L) gap = 0L;
    double od = (double) ((Float) rec[3]).floatValue();
    if (!(od > 0.0)) od = 1.0;
    double nd = (double) dil;
    if (!(nd > 0.0)) nd = 1.0;
    boolean take = s.equals(rec[4 + i]);
    if (!take && s.isAfter(rn)) {
      boolean fresh = !s.isAfter(now) && (double) nsBetween(s, now) <= (double) gap * nd + (double) CARRY_SLACK;
      take = !fresh && (double) nsBetween(rn, s) <= (double) gap * od + (double) CARRY_SLACK;
    }
    if (take) {
      double el = (double) nsBetween(s, rn) / od + (double) gap;
      if (el < 0.0) el = 0.0;
      if (el > (double) CARRY_CAP) out = java.time.Instant.MIN;
      else out = now.minusNanos((long) (el * nd));
    }
  }
  if (out == null && s.isAfter(now)) out = now;
  return out;
}""", mrg))
# world thread, every Mana regen pulse (ManaRegen.tick, first after the clock): the three stamps through carried() against the last
# pulse's record, then this pulse's record. Own try: a failure drops the record and can never stop the combat state or the refill.
mrg.addMethod(CtNewMethod.make(f"""
public static void carry(java.util.UUID u, {ST} store, {CB} cb, {REF} ref, java.time.Instant now, float dil) {{
  if (u == null) return;
  try {{
    {DDC} dd = ({DDC}) cb.getComponent(ref, {DDC}.getComponentType());
    if (dd == null || now == null) {{ CARRY.remove(u); return; }}
    String wn = null;
    Object ext = store.getExternalData();
    if (ext instanceof {EST}) {{
      {WLD} w = (({EST}) ext).getWorld();
      if (w != null) wn = w.getName();
    }}
    float d = dil > 0.0f ? dil : 1.0f;
    long wall = System.nanoTime();
    Object o = CARRY.get(u);
    Object[] rec = null;
    if (o instanceof Object[]) rec = (Object[]) o;
    java.time.Instant a = dd.getLastDamageTime();
    java.time.Instant x = carried(a, wn, now, d, wall, rec, 0);
    if (x != null) {{ dd.setLastDamageTime(x); a = x; }}
    java.time.Instant b = dd.getLastCombatAction();
    x = carried(b, wn, now, d, wall, rec, 1);
    if (x != null) {{ dd.setLastCombatAction(x); b = x; }}
    java.time.Instant c = dd.getLastChargeTime();
    x = carried(c, wn, now, d, wall, rec, 2);
    if (x != null) {{ dd.setLastChargeTime(x); c = x; }}
    CARRY.put(u, new Object[] {{ wn, now, Long.valueOf(wall), Float.valueOf(d), a, b, c }});
  }} catch (Throwable t) {{
    CARRY.remove(u);
    if (!KFAILED_ONCE) {{ KFAILED_ONCE = true; {PKG}.SkillCfg.warn("combat stamp carry (world switch) failed (logged once): " + t); }}
  }}
}}""", mrg))
# /skills mana's state line (pure, any thread; ManaCmd's 0.4.12 lines + the charging cases): r = rates(...), pct = Mana Regen %, factor =
# mana.regen.inCombat, max = the Mana max
mrg.addMethod(CtNewMethod.make(f"""
public static String stateLine(float[] r, double pct, int factor, float max) {{
  if (!(max > 0.0f)) return "no Mana pool (max 0) - nothing refills";
  if (r == null || r.length < 3) return "no refill right now";
  double p = pct > 0.0 ? (pct > MAX_PCT ? MAX_PCT : pct) : 0.0;
  int f = factor < 0 ? 0 : (factor > 100 ? 100 : factor);
  float co = r.length > 3 ? r[3] : 0.0f;
  float ci = r.length > 4 ? r[4] : 0.0f;
  if (r[1] > 0.0f) return "out of combat - vanilla refills " + {PKG}.Overall.num((double) r[1]) + "/s" + (p > 0.0 ? ", SkyySkills adds " + {PKG}.Overall.num((double) r[1] * p / 100.0) + "/s" : "");
  if (co > 0.0f) return "charging - Mana still regenerates: SkyySkills refills " + {PKG}.Overall.num((double) co * (1.0 + p / 100.0)) + "/s (vanilla pauses while you charge)";
  if (r[2] > 0.0f) return "IN COMBAT (vanilla's 6 s pause)" + (ci > 0.0f ? ", charging - Mana still regenerates" : "") + " - SkyySkills refills " + {PKG}.Overall.num((double) r[2] * (1.0 + p / 100.0) * (double) f / 100.0) + "/s (" + f + "% of " + {PKG}.Overall.num((double) r[2] * (1.0 + p / 100.0)) + "/s)";
  return "no refill right now (dead, or another regen condition stops it)";
}}""", mrg))
# world thread, every tick from AcroSys (before its 1 s gate): one pulse per PULSE seconds (vanilla's own interval), at most 1 s at a time
# 0.4.13: each pulse reads the world's clock first and carries stamps from another world's clock (carry, fix F1), then reads the Mana value
# and the regen entries and records the combat state (combat - before every return below, so it works at full Mana and without a Mana
# pool), then the refill runs on the same now / entries (the 0.4.12 "0 % and no boosts" return is gone: charging still refills there)
mrg.addMethod(CtNewMethod.make(f"""
public static void tick(java.util.UUID u, {ST} store, {CB} cb, {REF} ref, float dt) {{
  try {{
    float[] c = (float[]) CLK.get(u);
    if (c == null) {{ c = new float[] {{ 0.0f }}; CLK.put(u, c); }}
    c[0] = c[0] + dt;
    if (c[0] < PULSE) return;
    float secs = c[0];
    c[0] = 0.0f;
    if (secs > 1.0f) secs = 1.0f;
    {TMR} tr = ({TMR}) store.getResource({TMR}.getResourceType());
    java.time.Instant now = tr.getNow();
    carry(u, store, cb, ref, now, tr.getTimeDilationModifier());   // 0.4.13 fix F1: stamps from another world's clock (own try)
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());
    int mi = {DST}.getMana();
    {ESV} v = null;
    if (m != null && mi >= 0) v = m.get(mi);
    if (v == null) {{ CMB.remove(u); return; }}
    {RGV}[] rv = v.getRegeneratingValues();
    combat(u, cb, ref, now, rv);   // 0.4.13: skill:fn:combat - the entries, conditions and clock the refill below uses (own try)
    int f = IN_COMBAT;
    double pct = total(u);
    float max = v.getMax();
    float cur = v.get();
    if (!(max > 0.0f) || !(cur < max)) return;
    float a = amount(rates(cb, ref, now, rv), pct, f, secs, cur, max);   // 0.4.13: + what vanilla withholds while charging
    if (a > 0.0f) m.addStatValue(mi, a);
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("Mana regen in combat failed (logged once): " + t); }}
  }}
}}""", mrg))
# vanilla's base Mana refill per second from the Mana stat asset (5 in vanilla; 0 when it cannot be read) - texts only
mrg.addMethod(CtNewMethod.make(f"""
public static float vanillaRate() {{
  try {{
    {ESTT} t = ({ESTT}) {ESTT}.getAssetMap().getAsset({DST}.getMana());
    if (t == null) return 0.0f;
    {RGN}[] rs = t.getRegenerating();
    if (rs == null) return 0.0f;
    float b = 0.0f;
    for (int i = 0; i < rs.length; i++) b = b + baseOf(rs[i]);
    return b;
  }} catch (Throwable e) {{ return 0.0f; }}
}}""", mrg))
# one text line (no ECS: any thread) - the Server Setup action and /skills mana
mrg.addMethod(CtNewMethod.make(f"""
public static String text(java.util.UUID u) {{
  double p = total(u);
  String[] src = sources(u);
  float base = vanillaRate();
  int f = IN_COMBAT;
  StringBuilder sb = new StringBuilder();
  sb.append("Mana Regen boosts +").append({PKG}.Overall.num(p)).append("%");
  if (src.length == 0) sb.append(" (none registered)");
  else {{
    sb.append(" (");
    for (int i = 0; i < src.length; i++) {{
      if (i > 0) sb.append(", ");
      sb.append(src[i]);
    }}
    sb.append(")");
  }}
  sb.append(". Out of combat: vanilla ").append(base > 0.0f ? {PKG}.Overall.num((double) base) + "/s" : "refill");
  if (p > 0.0 && base > 0.0f) sb.append(" + ").append({PKG}.Overall.num((double) base * p / 100.0)).append("/s");
  if (f <= 0) sb.append(". In combat: vanilla (no refill for 6 s after a hit)");
  else {{
    sb.append(". In combat: ").append(f).append("% of (vanilla + boosts)");
    if (base > 0.0f) sb.append(" = ").append({PKG}.Overall.num((double) base * (1.0 + p / 100.0) * (double) f / 100.0)).append("/s");
  }}
  sb.append(f <= 0 ? ". Charging - Mana still regenerates out of combat (the normal refill)." : ". Charging - Mana still regenerates (the normal refill out of combat, the in-combat refill in combat).");   // 0.4.13
  return sb.toString();
}}""", mrg))
# review fix R4: the action answer is shown by SkyyMenu in ONE status line (firstLine into a 30 px label, about 110 characters fit), so it
# gets its own compact line of at most 110 characters (99 sources or fewer): the numbers first, then as many sources as the rest of the
# 110 leaves, then "+N more" ("N sources" when not even one fits); /skills mana keeps text() in chat.
# Pure (any thread): p = Mana Regen % (total), src = sources(), base = vanilla's refill per second (vanillaRate, 0 = unknown), f = mana.regen.inCombat.
mrg.addMethod(CtNewMethod.make(f"""
public static String compact(double p, String[] src, float base, int f) {{
  String head = "Mana Regen +" + {PKG}.Overall.num(p) + "%";
  double all = (double) base * (1.0 + p / 100.0);
  String tail = "";
  if (base > 0.0f) tail = ". Refill " + {PKG}.Overall.num(all) + "/s, in combat " + (f <= 0 ? "none (vanilla)" : {PKG}.Overall.num(all * (double) f / 100.0) + "/s (" + f + "%)") + ".";
  else tail = ". In combat " + (f <= 0 ? "no refill (vanilla)" : f + "% of the normal refill") + ".";
  int n = src == null ? 0 : src.length;
  String mid = " (no boosts)";
  if (n > 0) {{
    int room = 110 - head.length() - tail.length() - 13;
    StringBuilder l = new StringBuilder();
    int shown = 0;
    for (int i = 0; i < n; i++) {{
      String x = String.valueOf(src[i]);
      if (l.length() + x.length() + 2 > room) break;
      if (shown > 0) l.append(", ");
      l.append(x);
      shown++;
    }}
    if (shown == 0) mid = " (" + n + (n == 1 ? " source)" : " sources)");
    else mid = " (" + l.toString() + (shown < n ? ", +" + (n - shown) + " more)" : ")");
  }}
  return head + mid + tail;
}}""", mrg))
# Server Setup -> Skills -> Overall and Mana -> "Mana Regen: show mine" (an action row: the admin's own numbers; the kit re-checked the node)
mrg.addMethod(CtNewMethod.make("""
public static Object[] showAction(java.util.UUID who, String name) {
  String t = compact(total(who), sources(who), vanillaRate(), IN_COMBAT);
  if (who == null) t = "In game: your own. " + t;
  if (t.length() > 120) t = t.substring(0, 117) + "...";
  return new Object[] { "ok", "", t };
}""", mrg))
# ================= skill:fn:manaregen (0.4.12): the Mana Regen % registry for other mods - java.lang types only, never throws, any thread
#   {"add", UUID, String source, Number percent} -> Boolean  set / replace that source's % (0 removes; clamped -1000..1000)
#   {"remove", UUID, String source} -> Boolean              TRUE = there was an entry
#   {"get", UUID} -> Double                                 the total that applies (0..1000)
#   {"sources", UUID} -> String[]                           "source=+20" entries, sorted
#   {"clear", String source} -> Integer                     that source removed from every player
#   anything else -> null
mrfn.addInterface(pool.get("java.util.function.Function"))
mrfn.addConstructor(CtNewConstructor.make("public ManaRegenFn() { }", mrfn))
mrfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 2 || !(a[0] instanceof String)) return null;
    String op = ((String) a[0]).trim().toLowerCase();
    if (op.equals("clear")) {{
      if (!(a[1] instanceof String)) return Integer.valueOf(0);
      return Integer.valueOf({PKG}.ManaRegen.clear((String) a[1]));
    }}
    java.util.UUID u = null;
    if (a[1] instanceof java.util.UUID) u = (java.util.UUID) a[1];
    if (op.equals("get")) return Double.valueOf({PKG}.ManaRegen.total(u));
    if (op.equals("sources")) return {PKG}.ManaRegen.sources(u);
    if (op.equals("add")) {{
      if (u == null || a.length < 4 || !(a[2] instanceof String) || !(a[3] instanceof Number)) return Boolean.FALSE;
      return Boolean.valueOf({PKG}.ManaRegen.put(u, (String) a[2], ((Number) a[3]).doubleValue()));
    }}
    if (op.equals("remove")) {{
      if (u == null || a.length < 3 || !(a[2] instanceof String)) return Boolean.FALSE;
      return Boolean.valueOf({PKG}.ManaRegen.remove(u, (String) a[2]));
    }}
    return null;
  }} catch (Throwable t) {{ return null; }}
}}""", mrfn))

# ================= skill:fn:combat (0.4.13): the combat state for other mods (SkyyHud's Combat widget) - java.lang types only, memory only,
# never throws, any thread (one ConcurrentHashMap read: cheap enough for every HUD refresh of every online player)
#   apply(java.util.UUID player) -> Long  ms left in combat; 0 = out of combat (unknown / offline players 0)  = ManaRegen.combatNow
#   apply("window")              -> Long  the whole combat window in ms (vanilla 6000 = the Mana regen's NoDamageTaken Delay, read from
#                                         the engine condition); 0 until somebody was in combat since the start. A bar = left / window
#   apply(new Object[] { x })    -> the same as apply(x);   anything else -> null
cmbf.addInterface(pool.get("java.util.function.Function"))
cmbf.addConstructor(CtNewConstructor.make("public CombatFn() { }", cmbf))
cmbf.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  Object x = arg;
  try {{
    if (x instanceof Object[]) {{
      Object[] a = (Object[]) x;
      x = a.length > 0 ? a[0] : null;
    }}
    if (x instanceof java.util.UUID) return Long.valueOf({PKG}.ManaRegen.combatNow((java.util.UUID) x, System.currentTimeMillis()));
    if (x instanceof String && ((String) x).trim().equalsIgnoreCase("window")) return Long.valueOf({PKG}.ManaRegen.WINDOW);
    return null;
  }} catch (Throwable t) {{
    if (x instanceof java.util.UUID) return Long.valueOf(0L);
    return null;
  }}
}}""", cmbf))

# AcroSys: EntityTickingSystem on Player entities (AccEffects pattern; runs on the world thread, not parallel)
asy.addConstructor(CtNewConstructor.make("public AcroSys() { super(); }", asy))
asy.addField(CtField.make("public static boolean FAILED_ONCE = false;", asy))
asy.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", asy))
asy.addMethod(CtNewMethod.make(f"""
public void tick(float dt, int idx, {ACH} chunk, {ST} store, {CB} cb) {{
  try {{
    {REF} ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    {PLA} p = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    {PR} pr = ({PR}) store.getComponent(ref, {PR}.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    {PKG}.ManaRegen.tick(u, store, cb, ref, dt);   // 0.4.12: Mana regen in combat (own 0.2 s clock, own try; first, so no call below can skip it)
    double[] s = {PKG}.Acro.state(u);
    long now = System.currentTimeMillis();
    String wn = null;
    Object ext = store.getExternalData();
    if (ext instanceof {EST}) {{
      {WLD} w = (({EST}) ext).getWorld();
      if (w != null) wn = w.getName();
    }}
    if ({PKG}.Acro.worldChanged(u, wn)) {PKG}.Acro.reset(s);
    if ({PKG}.AcroCfg.ENABLED) {{
      boolean creative = {PKG}.SkillXp.creative(store, ref);
      {MSC} msc = ({MSC}) store.getComponent(ref, {MSC}.getComponentType());
      {TRC} tc = ({TRC}) store.getComponent(ref, {TRC}.getComponentType());
      {MVT} ms = null;
      if (msc != null) ms = msc.getMovementStates();
      {V3D} pos = null;
      if (tc != null) pos = tc.getPosition();
      if (ms != null && pos != null) {PKG}.Acro.move(s, ms, pos, dt, now, creative);
      {PKG}.Acro.airJump(s, store, cb, ref, pr, u, ms, now);
      {PKG}.Acro.dodge(s, store, cb, ref, u, now, creative, {PKG}.Acro.excludedState(ms));
      {PKG}.Acro.falls(s, store, ref, now, creative);
    }}
    {PKG}.Brew.tick(u, store, cb, ref, dt);
    {PKG}.Xbow.tick(store, ref, pr, u);
    s[14] = s[14] + (double) dt;
    if (s[14] < 1.0) return;
    s[14] = 0.0;
    if ({PKG}.Perks.epochChanged(u)) {{ {PKG}.Acro.profileReset(s); {PKG}.Perks.switched(u); }}
    {PKG}.Acro.flush(pr, s, now);
    {PKG}.Acro.bonuses(u, pr, cb, ref);
    {PKG}.Perks.tick(u, pr, cb, ref);
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("acrobatics tick failed (logged once): " + t); }}
  }}
}}""", asy))

# AcroFallSys: DamageEventSystem in the FILTER group (vanilla DamageSystems$ArmorDamageReduction pattern; ApplyDamage declares
# AFTER Gather, AFTER Filter, BEFORE Inspect). Remembers every player fall for XP; as the elected fall-damage applier it scales the
# damage by the summed fallDamage multiplier of all protocol sources (never below 0, never cancels).
afs.addConstructor(CtNewConstructor.make("public AcroFallSys() { super(); }", afs))
afs.addField(CtField.make("public static boolean FAILED_ONCE = false;", afs))
afs.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", afs))
afs.addMethod(CtNewMethod.make(f"""
public {SYG} getGroup() {{
  return {DMM}.get().getFilterDamageGroup();
}}""", afs))
afs.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
    {DMG} d = ({DMG}) ev;
    if (d.isCancelled()) return;
    if (!{PKG}.Acro.isFall(d.getCause())) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    if (!{PKG}.MoveSync.ownsFall({PKG}.Acro.MOD)) return;
    float m = {PKG}.MoveSync.fallMultiplier({PKG}.MoveSync.sums(u));
    if ({PKG}.MoveSync.near(m, 1.0f)) return;
    float a = d.getAmount() * m;
    if (a < 0.0f) a = 0.0f;
    d.setAmount(a);
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("acrobatics fall damage handler failed (logged once): " + t); }}
  }}
}}""", afs))

# AcroFallSeenSys (0.4): DamageEventSystem in the INSPECT group (after ApplyDamage - vanilla DamageSystems$ApplyParticles uses the same
# group). ApplyDamage rounds the amount, subtracts it and cancels when the entity is already dead, so a FALL Damage that reaches this
# group uncancelled with amount >= 1 was really applied (not negated by armor / our reduction / another mod). Noted as the unreduced
# amount (getInitialAmount, before the Filter group) normalised to 100 max health; falls() pays it 0.4 s later if still alive.
afss.addConstructor(CtNewConstructor.make("public AcroFallSeenSys() { super(); }", afss))
afss.addField(CtField.make("public static boolean FAILED_ONCE = false;", afss))
afss.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", afss))
afss.addMethod(CtNewMethod.make(f"""
public {SYG} getGroup() {{
  return {DMM}.get().getInspectDamageGroup();
}}""", afss))
afss.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
    if (!(ev instanceof {DMG})) return;
    {DMG} d = ({DMG}) ev;
    if (d.isCancelled()) return;
    if (!{PKG}.Acro.isFall(d.getCause())) return;
    if (d.getAmount() < 0.5f) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    if ({PKG}.Acro.inWater(st, r)) return;
    float mx = 100.0f;
    {ESM} m = ({ESM}) st.getComponent(r, {ESM}.getComponentType());
    if (m != null) {{
      {ESV} hv = m.get({DST}.getHealth());
      if (hv != null && hv.getMax() > 0.0f) mx = hv.getMax();
    }}
    float init = d.getInitialAmount();
    if (init <= 0.0f) return;
    {PKG}.Acro.noteFall(pr.getUuid(), init * 100.0f / mx);
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("acrobatics fall XP handler failed (logged once): " + t); }}
  }}
}}""", afss))

# ================= RollSys (0.4.14): roll landings (Skyy 2026-10-02) - an EntityTickingSystem BEFORE the engine's DamageSystems$FallDamagePlayers
# (SystemDependency BEFORE: the engine sorts every system of the store in one dependency graph; FallDamagePlayers itself runs BEFORE
# ProcessPlayerInput, which consumes the queue). It reads the player's PlayerInput movement update queue READ-ONLY and replays the engine's
# landing rule (bytecode asserted above): speed = |the client velocity y| (each SetClientVelocity updates it), the first SetMovementStates
# with onGround while the fall distance is > 0 is the landing; speed > MinFallSpeedToEngageRoll and not inFluid -> damage; rolling + speed
# <= MaxFallSpeedToEngageRoll = the roll engaged (full or partial mitigation) -> Acro.noteRoll(the UNREDUCED damage x 100 / max health).
# Non-rolled landings are left to AcroFallSeenSys (as before). Never writes a component, never throws (logged once).
rsy.addConstructor(CtNewConstructor.make("public RollSys() { super(); }", rsy))
rsy.addField(CtField.make("public static boolean FAILED_ONCE = false;", rsy))
rsy.addField(CtField.make("public static volatile java.util.Set DEPS = null;", rsy))
rsy.addField(CtField.make("public static volatile long NOTED = 0L;", rsy))   # rolled landings noted since the start (diagnostics)
rsy.addMethod(CtNewMethod.make(J14(r"""
public @QRY@ getQuery() {
  return @QRY@.and(new @QRY@[] { (@QRY@) @PLA@.getComponentType(), (@QRY@) @PR@.getComponentType(), (@QRY@) @PIN@.getComponentType(), (@QRY@) @ESM@.getComponentType() });
}"""), rsy))
rsy.addMethod(CtNewMethod.make(J14(r"""
public java.util.Set getDependencies() {
  java.util.Set d = DEPS;
  if (d == null) {
    d = java.util.Collections.singleton(new @SDEP@(@DORD@.BEFORE, @FDP@.class));
    DEPS = d;
  }
  return d;
}"""), rsy))
# PURE = FallDamagePlayers' arithmetic: {damage without the roll, the engine's damage, 1 = the roll engaged (mitigated)}; 0 / 0 / 0 when the
# landing makes no fall damage (not faster than min, or in fluid)
rsy.addMethod(CtNewMethod.make(J14(r"""
public static int[] damage(double sp, float min, float full, float eng, float pct, float mx, boolean rolling, boolean fluid) {
  if (!(sp > (double) min) || fluid) return new int[] { 0, 0, 0 };
  double base = Math.pow(0.5799999833106995 * (sp - (double) min), 2.0) + 10.0;
  int d0 = (int) Math.floor((double) mx / 100.0 * base);
  int d1 = d0;
  int rolled = 0;
  if (rolling) {
    if (sp <= (double) full) { d1 = 0; rolled = 1; }
    else if (sp <= (double) eng) { d1 = (int) ((double) d0 * (1.0 - (double) pct / 100.0)); rolled = 1; }
  }
  return new int[] { d0, d1, rolled };
}"""), rsy))
# the world's MovementConfig asset (the lookup FallDamagePlayers and Acro.djMaxFall make)
rsy.addMethod(CtNewMethod.make(J14(r"""
public static @MCF@ movementConfig(@ST@ store) {
  try {
    @WLD@ w = ((@EST@) store.getExternalData()).getWorld();
    int mi = w.getGameplayConfig().getPlayerConfig().getMovementConfigIndex();
    return (@MCF@) @MCF@.getAssetMap().getAsset(mi);
  } catch (Throwable t) { return null; }
}"""), rsy))
# FIX ROUND F2 (reviews 2026-10-03): the store's world has fall damage on - the switch the engine's FallDamagePlayers.tick(F, I, Store) tests
# before it looks at ANY landing (bytecode asserted above); off (or no world / config) = no roll note, like 0.4.13 (no Damage, no fall XP)
rsy.addMethod(CtNewMethod.make(J14(r"""
public static boolean fallDamageOn(@ST@ store) {
  try {
    if (store == null) return false;
    Object ext = store.getExternalData();
    if (!(ext instanceof @EST@)) return false;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return false;
    @WCFG@ wc = w.getWorldConfig();
    return wc != null && wc.isFallDamageEnabled();
  } catch (Throwable t) { return false; }
}"""), rsy))
# one landing: the roll's note, or nothing; returns the unreduced damage noted (0 = nothing noted)
rsy.addMethod(CtNewMethod.make(J14(r"""
public static int land(@ACH@ chunk, int idx, @ST@ store, @MVT@ ms, double sp) {
  if (ms == null || !ms.rolling) return 0;
  @MCF@ mc = movementConfig(store);
  if (mc == null) return 0;
  float mx = 100.0f;
  @ESM@ m = (@ESM@) chunk.getComponent(idx, @ESM@.getComponentType());
  if (m != null) {
    @ESV@ hv = m.get(@DST@.getHealth());
    if (hv != null && hv.getMax() > 0.0f) mx = hv.getMax();
  }
  int[] d = damage(sp, mc.getMinFallSpeedToEngageRoll(), mc.getMaxFallSpeedRollFullMitigation(), mc.getMaxFallSpeedToEngageRoll(), mc.getFallDamagePartialMitigationPercent(), mx, true, ms.inFluid);
  if (d[2] == 0 || d[0] <= 0) return 0;
  @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
  if (pr == null) return 0;
  @PKG@.Acro.noteRoll(pr.getUuid(), (float) d[0] * 100.0f / mx);
  NOTED = NOTED + 1L;
  return d[0];
}"""), rsy))
rsy.addMethod(CtNewMethod.make(J14(r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (!@PKG@.AcroCfg.ENABLED || !(@PKG@.AcroCfg.ROLL > 0.0)) return;
    @PIN@ in = (@PIN@) chunk.getComponent(idx, @PIN@.getComponentType());
    if (in == null) return;
    java.util.List q = in.getMovementUpdateQueue();
    if (q == null || q.isEmpty()) return;
    @PLA@ p = (@PLA@) chunk.getComponent(idx, @PLA@.getComponentType());
    if (p == null || !(p.getCurrentFallDistance() > 0.0)) return;
    if (!fallDamageOn(store)) return;   // fix round F2: a world with fall damage off - the engine skips every landing there
    double sp = 0.0;
    @VEL@ v = (@VEL@) chunk.getComponent(idx, @VEL@.getComponentType());
    if (v != null && v.getClientVelocity() != null) sp = Math.abs(v.getClientVelocity().y());
    for (int i = 0; i < q.size(); i++) {
      Object o = q.get(i);
      if (o instanceof @PISV@) {
        @V3D@ cv = ((@PISV@) o).getVelocity();
        if (cv != null) sp = Math.abs(cv.y());
        continue;
      }
      if (!(o instanceof @PISM@)) continue;
      @MVT@ ms = ((@PISM@) o).movementStates();
      if (ms == null || !ms.onGround) continue;
      land(chunk, idx, store, ms, sp);
      return;
    }
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("roll landing check failed (logged once): " + t); }
  }
}"""), rsy))

# ================= CombatDmgSys (0.3): combat perk = more damage with your class weapons =================
# DamageEventSystem in the FILTER group (like AcroFallSys / SkyyClasses DamageLock), Query.any (the target is usually an NPC).
# Skips cancelled damage; SkyyClasses' DamageLock sets amount 0 AND cancels, so the result is right whichever of the two runs first.
cds.addConstructor(CtNewConstructor.make("public CombatDmgSys() { super(); }", cds))
cds.addField(CtField.make("public static boolean FAILED_ONCE = false;", cds))
cds.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return {QRY}.any();
}}""", cds))
cds.addMethod(CtNewMethod.make(f"""
public {SYG} getGroup() {{
  return {DMM}.get().getFilterDamageGroup();
}}""", cds))
cds.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
    if (!(ev instanceof {DMG})) return;
    {DMG} d = ({DMG}) ev;
    if (d.isCancelled()) return;
    if (!{PKG}.PerkCfg.ENABLED || {PKG}.PerkCfg.DMG <= 0.0) return;
    Object src = d.getSource();
    if (!(src instanceof {DES})) return;
    {REF} att = (({DES}) src).getRef();
    if (att == null || !att.isValid()) return;
    {PR} pr = ({PR}) buf.getComponent(att, {PR}.getComponentType());
    if (pr == null) return;
    if (!{PKG}.PerkCfg.DMG_PVP) {{
      {REF} tr = chunk.getReferenceTo(idx);
      if (tr != null && st.getComponent(tr, {PR}.getComponentType()) != null) return;
    }}
    java.util.UUID u = pr.getUuid();
    int slot = {PKG}.SkillClass.slot(u);
    if (slot < 0) return;
    if (!{PKG}.SkillClass.consistent(u)) return;
    java.util.function.Function f = {PKG}.SkillClass.allowedFn();
    if (f == null) return;
    double bonus = {PKG}.Perks.damage({PKG}.SkillStore.level(u, slot));
    if (bonus <= 0.0) return;
    if (!{PKG}.SkillClass.weaponOk(u, slot, f, buf, att)) return;
    float a = d.getAmount();
    if (a <= 0.0f) return;
    d.setAmount((float) (a * (1.0 + bonus)));
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("combat damage perk failed (logged once): " + t); }}
  }}
}}""", cds))

# ================= PlacedStore: positions of player-placed blocks, per world =================
plc.addField(CtField.make("public static java.nio.file.Path DIR;", plc))
plc.addField(CtField.make("public static final int CAP = 400000;", plc))
plc.addField(CtField.make("public static final java.util.HashMap WORLDS = new java.util.HashMap();", plc))
plc.addField(CtField.make("public static final java.util.HashSet DIRTY = new java.util.HashSet();", plc))
plc.addMethod(CtNewMethod.make("""
public static long key(int x, int y, int z) {
  return ((((long) x) & 67108863L) << 38) | ((((long) z) & 67108863L) << 12) | (((long) y) & 4095L);
}""", plc))
plc.addMethod(CtNewMethod.make("""
public static String fileName(String w) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < w.length(); i++) {
    char c = w.charAt(i);
    sb.append(Character.isLetterOrDigit(c) || c == '-' || c == '_' ? c : '_');
  }
  return sb.toString() + ".bin";
}""", plc))
plc.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.LinkedHashSet set(String w) {{
  java.util.LinkedHashSet s = (java.util.LinkedHashSet) WORLDS.get(w);
  if (s != null) return s;
  s = new java.util.LinkedHashSet();
  try {{
    java.nio.file.Path f = DIR.resolve(fileName(w));
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {{
      java.io.DataInputStream in = new java.io.DataInputStream(new java.io.BufferedInputStream(java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0])));
      try {{
        int n = in.readInt();
        for (int i = 0; i < n; i++) s.add(Long.valueOf(in.readLong()));
      }} finally {{ in.close(); }}
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not load placed blocks for " + w + ": " + t); }}
  WORLDS.put(w, s);
  return s;
}}""", plc))
plc.addMethod(CtNewMethod.make("""
public static synchronized void add(String w, long k) {
  java.util.LinkedHashSet s = set(w);
  Long v = Long.valueOf(k);
  s.remove(v);
  s.add(v);
  if (s.size() > CAP) { java.util.Iterator it = s.iterator(); it.next(); it.remove(); }
  DIRTY.add(w);
}""", plc))
plc.addMethod(CtNewMethod.make("""
public static synchronized boolean remove(String w, long k) {
  boolean r = set(w).remove(Long.valueOf(k));
  if (r) DIRTY.add(w);
  return r;
}""", plc))
# 0.4 trees bridge (skill:fn:placed): was this position placed by a player? LRU-capped at CAP per world, so a very old placement can be
# forgotten (Skill-Trees-Spec 9.3 accepts that). The first call for a world loads its file, like remove() in BreakTask.
plc.addMethod(CtNewMethod.make("""
public static synchronized boolean contains(String w, long k) {
  return set(w).contains(Long.valueOf(k));
}""", plc))
plc.addMethod(CtNewMethod.make("""
public static synchronized void snapshot(java.util.ArrayList names, java.util.ArrayList snaps) {
  java.util.Iterator it = DIRTY.iterator();
  while (it.hasNext()) {
    String w = (String) it.next();
    java.util.LinkedHashSet s = (java.util.LinkedHashSet) WORLDS.get(w);
    if (s != null) {
      long[] a = new long[s.size()];
      int i = 0;
      java.util.Iterator si = s.iterator();
      while (si.hasNext() && i < a.length) { a[i] = ((Long) si.next()).longValue(); i++; }
      names.add(w); snaps.add(a);
    }
  }
  DIRTY.clear();
}""", plc))
plc.addMethod(CtNewMethod.make(f"""
public static void flush() {{
  java.util.ArrayList names = new java.util.ArrayList();
  java.util.ArrayList snaps = new java.util.ArrayList();
  snapshot(names, snaps);
  for (int j = 0; j < names.size(); j++) {{
    String w = (String) names.get(j);
    long[] a = (long[]) snaps.get(j);
    try {{
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Path tmp = DIR.resolve(fileName(w) + ".tmp");
      java.io.DataOutputStream out = new java.io.DataOutputStream(new java.io.BufferedOutputStream(java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0])));
      try {{
        out.writeInt(a.length);
        for (int i = 0; i < a.length; i++) out.writeLong(a[i]);
      }} finally {{ out.close(); }}
      java.nio.file.Files.move(tmp, DIR.resolve(fileName(w)), new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
    }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not save placed blocks for " + w + ": " + t); }}
  }}
}}""", plc))

# ================= HarvestGate: one pending harvest check per block, one payout per block per harvestCooldownMs =================
hg.addField(CtField.make("public static final java.util.HashMap LAST = new java.util.HashMap();", hg))
hg.addField(CtField.make("public static final java.util.HashMap PENDING = new java.util.HashMap();", hg))
hg.addMethod(CtNewMethod.make("""
public static String id(String w, long k) {
  return w + "|" + k;
}""", hg))
hg.addMethod(CtNewMethod.make("""
public static void prune(java.util.HashMap m, long now, long keep) {
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) { Long t = (Long) it.next(); if (now - t.longValue() >= keep) it.remove(); }
}""", hg))
hg.addMethod(CtNewMethod.make("""
public static synchronized boolean claim(String w, long k, long now, long gap) {
  String id = id(w, k);
  Long t = (Long) LAST.get(id);
  if (t != null && now - t.longValue() < gap) return false;
  LAST.put(id, Long.valueOf(now));
  if (LAST.size() > 20000) prune(LAST, now, gap);
  return true;
}""", hg))
# a pending entry older than 10 s is stale (its task died with a world), so it never blocks a block forever
hg.addMethod(CtNewMethod.make("""
public static synchronized boolean begin(String w, long k, long now) {
  String id = id(w, k);
  Long t = (Long) PENDING.get(id);
  if (t != null && now - t.longValue() < 10000L) return false;
  PENDING.put(id, Long.valueOf(now));
  if (PENDING.size() > 5000) prune(PENDING, now, 10000L);
  return true;
}""", hg))
hg.addMethod(CtNewMethod.make("""
public static synchronized void end(String w, long k) {
  PENDING.remove(id(w, k));
}""", hg))

# ================= 0.4.2 FELLED TREES (research/Tree-Fall-Spec.md sections 2 / 3.1 / 4) =================
# FellDefs: which block ids are tree wood / leaves - Hytale's own lists (Assets.zip Server/BlockTypeList/TreeWood.json, TreeLeaves.json)
# generated at build time, + the fell.extraTrees ids. Codes: 0 none, 1 trunk (_Trunk / _Trunk_Full), 2 branch, 3 roots, 4 leaves.
# family = the wood id without its suffix (Wood_Birch_Trunk -> Wood_Birch). Cached per block id and per block index (FellCfg maps).
fdf.addField(CtField.make("public static final java.util.HashSet WOOD = new java.util.HashSet(java.util.Arrays.asList(" + jarr(TREE_WOOD) + "));", fdf))
fdf.addField(CtField.make("public static final java.util.HashSet LEAVES = new java.util.HashSet(java.util.Arrays.asList(" + jarr(TREE_LEAVES) + "));", fdf))
fdf.addField(CtField.make("public static final java.util.HashSet WOODX = new java.util.HashSet(java.util.Arrays.asList(" + jarr(FELL_EXTRA_WOOD) + "));", fdf))
fdf.addField(CtField.make("public static final java.util.HashSet LEAVESX = new java.util.HashSet(java.util.Arrays.asList(" + jarr(FELL_EXTRA_LEAVES) + "));", fdf))
fdf.addField(CtField.make("public static final String[] SUFFIXES = " + jarr(FELL_SUFFIXES) + ";", fdf))
fdf.addMethod(CtNewMethod.make(f"""
public static int kindOfId(String id) {{
  if (id == null) return 0;
  boolean x = {PKG}.FellCfg.EXTRA_TREES;
  if (WOOD.contains(id) || (x && WOODX.contains(id))) {{
    if (id.endsWith("_Trunk") || id.endsWith("_Trunk_Full")) return 1;
    if (id.endsWith("_Branch_Short") || id.endsWith("_Branch_Long") || id.endsWith("_Branch_Corner")) return 2;
    if (id.endsWith("_Roots")) return 3;
    return 0;
  }}
  if (LEAVES.contains(id) || (x && LEAVESX.contains(id))) return 4;
  return 0;
}}""", fdf))
fdf.addMethod(CtNewMethod.make("""
public static String familyOfId(String id) {
  if (id == null) return "";
  for (int i = 0; i < SUFFIXES.length; i++) {
    if (id.endsWith(SUFFIXES[i])) return id.substring(0, id.length() - SUFFIXES[i].length());
  }
  return id;
}""", fdf))
fdf.addMethod(CtNewMethod.make("""
public static String rawId(String id) {
  if (id == null) return null;
  String r = id;
  if (r.startsWith("*")) r = r.substring(1);
  int s = r.indexOf("_State_");
  if (s > 0) r = r.substring(0, s);
  return r;
}""", fdf))
fdf.addMethod(CtNewMethod.make(f"""
public static int code({BTY} bt) {{
  if (bt == null) return 0;
  String id = bt.getId();
  if (id == null) return 0;
  Object c = {PKG}.FellCfg.IDCODE.get(id);
  if (c instanceof Integer) return ((Integer) c).intValue();
  String n = rawId(id);
  int k = kindOfId(n);
  String f = n;
  if (k == 0) {{
    String g = {PKG}.SkillCfg.familyId(bt);
    if (g != null && !g.equals(n)) {{ k = kindOfId(g); f = g; }}
  }}
  {PKG}.FellCfg.IDFAM.put(id, (k == 0 || k == 4) ? "" : familyOfId(f));
  {PKG}.FellCfg.IDCODE.put(id, Integer.valueOf(k));
  return k;
}}""", fdf))
fdf.addMethod(CtNewMethod.make(f"""
public static String fam({BTY} bt) {{
  if (bt == null || bt.getId() == null) return "";
  code(bt);
  Object f = {PKG}.FellCfg.IDFAM.get(bt.getId());
  return f instanceof String ? (String) f : "";
}}""", fdf))
fdf.addMethod(CtNewMethod.make(f"""
public static int codeIdx(int idx) {{
  if (idx <= 0) return 0;
  Integer key = Integer.valueOf(idx);
  Object c = {PKG}.FellCfg.CODE.get(key);
  if (c instanceof Integer) return ((Integer) c).intValue();
  {BTY} bt = null;
  try {{ bt = ({BTY}) {BTY}.getAssetMap().getAsset(idx); }} catch (Throwable t) {{ bt = null; }}
  int k = code(bt);
  {PKG}.FellCfg.FAM.put(key, k == 0 ? "" : fam(bt));
  {PKG}.FellCfg.CODE.put(key, Integer.valueOf(k));
  return k;
}}""", fdf))
fdf.addMethod(CtNewMethod.make(f"""
public static String famIdx(int idx) {{
  if (codeIdx(idx) == 0) return "";
  Object f = {PKG}.FellCfg.FAM.get(Integer.valueOf(idx));
  return f instanceof String ? (String) f : "";
}}""", fdf))

# FellRead: block reads for one snapshot or one watch poll (world thread). The SkillCfg.blockIdAt read path (never loads a chunk), with the
# chunk section (BlockSection + BlockPhysics) cached per 32-block section, so each read is an array lookup. idx: the block index,
# 0 = empty, -1 = not loaded / out of the world / over the read budget (over = true); deco = BlockPhysics.isDeco (player-placed logs and
# leaves, spec 1.4). err = the first exception a read threw (the handler-read fallback, spec 3.1). TEST / TESTDECO = test seam for the
# bare-JVM harness (packed PlacedStore key -> index / deco); always null in the game.
frd.addField(CtField.make("public static volatile java.util.function.Function TEST = null;", frd))
frd.addField(CtField.make("public static volatile java.util.function.Function TESTDECO = null;", frd))
frd.addField(CtField.make(f"public {WLD} w;", frd))
frd.addField(CtField.make(f"public {CHS} cs;", frd))
frd.addField(CtField.make(f"public {ST} st;", frd))
frd.addField(CtField.make("public java.util.HashMap secs;", frd))
frd.addField(CtField.make("public int reads;", frd))
frd.addField(CtField.make("public int max;", frd))
frd.addField(CtField.make("public boolean over;", frd))
frd.addField(CtField.make("public Throwable err;", frd))
frd.addConstructor(CtNewConstructor.make(f"""
public FellRead({WLD} w, int max) {{
  this.w = w; this.max = max; this.reads = 0; this.over = false; this.err = null;
  this.secs = new java.util.HashMap();
  this.cs = null; this.st = null;
  try {{
    if (w != null) {{
      this.cs = w.getChunkStore();
      if (this.cs != null) this.st = this.cs.getStore();
    }}
  }} catch (Throwable t) {{ this.err = t; }}
}}""", frd))
frd.addMethod(CtNewMethod.make(f"""
public Object[] sec(int x, int y, int z) {{
  int b = {CKU}.BITS;
  Long sk = Long.valueOf(((((long) (x >> b)) & 2097151L) << 42) | ((((long) (z >> b)) & 2097151L) << 21) | (((long) (y >> b)) & 2097151L));
  Object o = this.secs.get(sk);
  if (o != null) return (Object[]) o;
  Object[] e = new Object[3];
  try {{
    if (this.cs != null && this.st != null) {{
      {REF} sr = this.cs.getChunkSectionReferenceAtBlock(x, y, z);
      if (sr != null && sr.isValid()) {{
        e[0] = this.st.getComponent(sr, {BSC}.getComponentType());
        e[1] = sr;
      }}
    }}
  }} catch (Throwable t) {{ if (this.err == null) this.err = t; e[0] = null; e[1] = null; }}
  this.secs.put(sk, e);
  return e;
}}""", frd))
frd.addMethod(CtNewMethod.make(f"""
public int idx(int x, int y, int z) {{
  if (y < 0 || y >= {CKU}.HEIGHT) return -1;
  if (this.reads >= this.max) {{ this.over = true; return -1; }}
  this.reads++;
  java.util.function.Function tf = TEST;
  if (tf != null) {{
    Object r = tf.apply(Long.valueOf({PKG}.PlacedStore.key(x, y, z)));
    if (r instanceof Number) return ((Number) r).intValue();
    return 0;
  }}
  Object[] e = sec(x, y, z);
  if (e[0] == null) return -1;
  try {{ return (({BSC}) e[0]).get(x, y, z); }} catch (Throwable t) {{ if (this.err == null) this.err = t; return -1; }}
}}""", frd))
frd.addMethod(CtNewMethod.make(f"""
public boolean deco(int x, int y, int z) {{
  java.util.function.Function tf = TESTDECO;
  if (tf != null) return Boolean.TRUE.equals(tf.apply(Long.valueOf({PKG}.PlacedStore.key(x, y, z))));
  if (TEST != null) return false;
  Object[] e = sec(x, y, z);
  if (e[1] == null) return false;
  try {{
    if (e[2] == null) {{
      Object bp = this.st.getComponent(({REF}) e[1], {BPH}.getComponentType());
      if (bp == null) e[2] = Boolean.FALSE;
      else e[2] = bp;
    }}
    if (!(e[2] instanceof {BPH})) return false;
    return (({BPH}) e[2]).isDeco(x, y, z);
  }} catch (Throwable t) {{ if (this.err == null) this.err = t; return false; }}
}}""", frd))

# FellSnap: one snapshot (spec 2.3). trig 1 TRUNK, 2 BRANCH, 3 UNDER. b* = the broken block (y0 = by). Claims = x/y/z/idx/key/leaf[0..n),
# layer = lkey[0..ln) (trunks ON y0: cut, never claimed). late = the handler could not read blocks: search again in BreakTask (spec 3.1).
for decl in (f"{WLD} w", "String wn", "java.util.UUID u", "String pk", "long created", "long took", "int trig", "int bx", "int by", "int bz",
             f"{BTY} bt", "String fam", "boolean inOther", "boolean late", "boolean leafSeen", "int n", "int[] x", "int[] y", "int[] z",
             "int[] idx", "long[] key", "boolean[] leaf", "int ln", "long[] lkey", "int logs", "int leaves", "int reads"):
    fsn.addField(CtField.make("public " + decl + ";", fsn))
fsn.addConstructor(CtNewConstructor.make("public FellSnap() { this.n = 0; this.ln = 0; this.fam = null; }", fsn))

# FellWatch (spec 2.5): the claimed positions of one snapshot, polled every fell.pollMs (run() is added after Fell / FellCredit, which it
# calls). Counters for the debug line: hand (hand-broken while claimed), env (explosion / fire), other (taken over by a newer claim),
# lost (chunk gone), replaced (another block), skipped (another player's claim at commit), dropped (credit preconditions failed).
fwt.addInterface(pool.get("java.lang.Runnable"))
for decl in (f"{WLD} w", "String wn", "java.util.UUID u", "String pk", "int trig", "long created", "long lastChange", "boolean hop",
             "volatile boolean ended", "int n", "int[] x", "int[] y", "int[] z", "int[] idx", "long[] key", "boolean[] leaf", "boolean[] done",
             "int left", "int ln", "long[] lkey", "long took", "int reads", "int sLogs", "int sLeaves", "int credited", "int cLogs",
             "int cLeaves", "int hand", "int env", "int other", "int lost", "int replaced", "int skipped", "int dropped", "int collYes",
             "int collNo", "long xp", "int row"):
    fwt.addField(CtField.make("public " + decl + ";", fwt))
fwt.addConstructor(CtNewConstructor.make(f"""
public FellWatch({PKG}.FellSnap s) {{
  this.w = s.w; this.wn = s.wn; this.u = s.u; this.pk = s.pk; this.trig = s.trig;
  this.n = s.n;
  this.x = new int[this.n]; System.arraycopy(s.x, 0, this.x, 0, this.n);
  this.y = new int[this.n]; System.arraycopy(s.y, 0, this.y, 0, this.n);
  this.z = new int[this.n]; System.arraycopy(s.z, 0, this.z, 0, this.n);
  this.idx = new int[this.n]; System.arraycopy(s.idx, 0, this.idx, 0, this.n);
  this.key = new long[this.n]; System.arraycopy(s.key, 0, this.key, 0, this.n);
  this.leaf = new boolean[this.n]; System.arraycopy(s.leaf, 0, this.leaf, 0, this.n);
  this.done = new boolean[this.n];
  this.left = this.n;
  this.ln = s.ln;
  this.lkey = new long[this.ln]; System.arraycopy(s.lkey, 0, this.lkey, 0, this.ln);
  this.created = s.created;
  this.lastChange = System.currentTimeMillis();
  this.hop = false; this.ended = false; this.row = -1;
  this.took = s.took; this.reads = s.reads; this.sLogs = s.logs; this.sLeaves = s.leaves;
}}""", fwt))
fwt.addMethod(CtNewMethod.make("""
public boolean live() {
  return !this.ended;
}""", fwt))
fwt.addMethod(CtNewMethod.make("""
public void touch() {
  this.lastChange = System.currentTimeMillis();
}""", fwt))

# Fell: the per-world claim maps and the snapshot / commit / release logic (spec 2.3 / 2.4 / 2.5). CLAIMS / LAYER: world name ->
# ConcurrentHashMap(Long PlacedStore.key -> FellWatch); read and written on that world's thread (the bridge only reads). FELLED: world ->
# LinkedHashMap(Long key -> Object[]{UUID, pkey, Long at, String blockId}), 8192 per world, fell.memoryMs TTL (synchronized statics).
fel.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CLAIMS = new java.util.concurrent.ConcurrentHashMap();", fel))
fel.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LAYER = new java.util.concurrent.ConcurrentHashMap();", fel))
fel.addField(CtField.make("public static final java.util.HashMap FELLED = new java.util.HashMap();", fel))
fel.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap WATCHES = new java.util.concurrent.ConcurrentHashMap();", fel))
fel.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap RATE = new java.util.concurrent.ConcurrentHashMap();", fel))
fel.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap FAILED = new java.util.concurrent.ConcurrentHashMap();", fel))
fel.addField(CtField.make("public static volatile boolean HANDLER_FAILED = false;", fel))
fel.addField(CtField.make("public static volatile boolean TEST_NO_SCHEDULE = false;", fel))   # test seam (bare-JVM harness): commit without scheduling; always false in the game
fel.addMethod(CtNewMethod.make(f"""
public static void failed(String tag, Throwable t) {{
  if (FAILED.putIfAbsent(tag, Boolean.TRUE) == null) {PKG}.SkillCfg.warn("felled trees: " + tag + " failed (logged once): " + t);
}}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static long key(int x, int y, int z) {{
  return {PKG}.PlacedStore.key(x, y, z);
}}""", fel))
fel.addMethod(CtNewMethod.make("""
public static java.util.concurrent.ConcurrentHashMap claims(String wn) {
  Object m = CLAIMS.get(wn);
  if (m == null) { CLAIMS.putIfAbsent(wn, new java.util.concurrent.ConcurrentHashMap()); m = CLAIMS.get(wn); }
  return (java.util.concurrent.ConcurrentHashMap) m;
}""", fel))
fel.addMethod(CtNewMethod.make("""
public static java.util.concurrent.ConcurrentHashMap layer(String wn) {
  Object m = LAYER.get(wn);
  if (m == null) { LAYER.putIfAbsent(wn, new java.util.concurrent.ConcurrentHashMap()); m = LAYER.get(wn); }
  return (java.util.concurrent.ConcurrentHashMap) m;
}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static boolean online(java.util.UUID u) {{
  try {{
    {PR} pr = {UNI}.get().getPlayer(u);
    return pr != null && pr.isValid();
  }} catch (Throwable t) {{ return false; }}
}}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static synchronized void felledPut(String wn, long k, Object[] v) {{
  java.util.LinkedHashMap m = (java.util.LinkedHashMap) FELLED.get(wn);
  if (m == null) {{ m = new java.util.LinkedHashMap(); FELLED.put(wn, m); }}
  Long kk = Long.valueOf(k);
  m.remove(kk);
  m.put(kk, v);
  long now = System.currentTimeMillis();
  long ttl = {PKG}.FellCfg.MEMORY_MS;
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) {{
    Object[] e = (Object[]) it.next();
    if (m.size() > 8192 || now - ((Long) e[2]).longValue() >= ttl) it.remove();
    else break;
  }}
}}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static synchronized Object[] felledGet(String wn, long k) {{
  java.util.LinkedHashMap m = (java.util.LinkedHashMap) FELLED.get(wn);
  if (m == null) return null;
  Object o = m.get(Long.valueOf(k));
  if (o == null) return null;
  Object[] e = (Object[]) o;
  if (System.currentTimeMillis() - ((Long) e[2]).longValue() >= {PKG}.FellCfg.MEMORY_MS) return null;
  return e;
}}""", fel))
fel.addMethod(CtNewMethod.make("""
public static synchronized void clearFelled() {
  FELLED.clear();
}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static void handlerFailed(Throwable t) {{
  if (!HANDLER_FAILED) {{
    HANDLER_FAILED = true;
    {PKG}.SkillCfg.warn("felled trees: reading blocks inside the break event failed (" + t + ") - snapshots are taken a moment later from now on (fallback, research/Tree-Fall-Spec.md 3.1)");
  }}
}}""", fel))
# natural = not in the placed-block tracker and not deco (spec 2.3)
fel.addMethod(CtNewMethod.make(f"""
public static boolean natural(String wn, {PKG}.FellRead R, int x, int y, int z) {{
  if ({PKG}.PlacedStore.contains(wn, key(x, y, z))) return false;
  return !R.deco(x, y, z);
}}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static void addClaim({PKG}.FellSnap s, int x, int y, int z, int idx, boolean leaf) {{
  int i = s.n;
  s.x[i] = x; s.y[i] = y; s.z[i] = z; s.idx[i] = idx; s.key[i] = key(x, y, z); s.leaf[i] = leaf;
  s.n = i + 1;
  if (leaf) s.leaves = s.leaves + 1;
  else s.logs = s.logs + 1;
}}""", fel))
# fell.maxSnapshotsPerSecond per player (world thread of the player; a player is in one world at a time)
fel.addMethod(CtNewMethod.make(f"""
public static boolean rate(java.util.UUID u) {{
  long sec = System.currentTimeMillis() / 1000L;
  long[] c = (long[]) RATE.get(u);
  if (c == null) {{
    if (RATE.size() > 2000) RATE.clear();
    c = new long[2];
    RATE.put(u, c);
  }}
  if (c[0] != sec) {{ c[0] = sec; c[1] = 0L; }}
  if (c[1] >= (long) {PKG}.FellCfg.MAX_SNAPS) return false;
  c[1] = c[1] + 1L;
  return true;
}}""", fel))
# the search (spec 2.3): breadth-first over the 26-neighbourhood from the seed(s). Every read cell is marked seen once. Wood: same family,
# natural, radius / height, trunks y >= y0 (BRANCH trigger: branches only), branches / roots y >= y0 - 1; trunks ON y0 -> layer (still
# expanded, so the first cut of a thick tree records the wood above EVERY base log); others -> claims. Leaves next to accepted wood are
# candidates; the leaf phase accepts natural ones (leafSeen) and walks up to 4 leaf steps (claims only with fell.leaves).
fel.addMethod(CtNewMethod.make(f"""
public static void search({PKG}.FellSnap s, {PKG}.FellRead R, int[] sx, int[] sy, int[] sz, int[] si, boolean[] sc, int ns) {{
  int maxW = {PKG}.FellCfg.MAX_LOGS + ns;
  int maxL = {PKG}.FellCfg.MAX_LEAVES;
  int rad = {PKG}.FellCfg.RADIUS;
  int y0 = s.by;
  int top = y0 + {PKG}.FellCfg.HEIGHT;
  int cap = maxW + maxL + 2;
  s.x = new int[cap]; s.y = new int[cap]; s.z = new int[cap]; s.idx = new int[cap]; s.key = new long[cap]; s.leaf = new boolean[cap];
  s.n = 0; s.logs = 0; s.leaves = 0;
  s.lkey = new long[maxW + 2]; s.ln = 0;
  s.leafSeen = false;
  int[] wx = new int[maxW + 2]; int[] wy = new int[maxW + 2]; int[] wz = new int[maxW + 2];
  int wc = 0;
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < ns; i++) {{
    wx[wc] = sx[i]; wy[wc] = sy[i]; wz[wc] = sz[i]; wc++;
    seen.add(Long.valueOf(key(sx[i], sy[i], sz[i])));
    if (sc[i]) addClaim(s, sx[i], sy[i], sz[i], si[i], false);
  }}
  java.util.ArrayList cand = new java.util.ArrayList();
  boolean full = wc >= maxW;
  int head = 0;
  while (head < wc && !R.over) {{
    int cx = wx[head]; int cy = wy[head]; int cz = wz[head];
    head++;
    for (int dx = -1; dx <= 1; dx++) {{
      for (int dy = -1; dy <= 1; dy++) {{
        for (int dz = -1; dz <= 1; dz++) {{
          if (dx == 0 && dy == 0 && dz == 0) continue;
          int nx = cx + dx; int ny = cy + dy; int nz = cz + dz;
          if (nx - s.bx > rad || s.bx - nx > rad || nz - s.bz > rad || s.bz - nz > rad) continue;
          if (ny > top || ny < y0 - 1) continue;
          Long kk = Long.valueOf(key(nx, ny, nz));
          if (seen.contains(kk)) continue;
          seen.add(kk);
          int id = R.idx(nx, ny, nz);
          if (id <= 0) continue;
          int c = {PKG}.FellDefs.codeIdx(id);
          if (c == 0) continue;
          if (c == 4) {{ cand.add(new int[] {{ nx, ny, nz, id }}); continue; }}
          if (full) continue;
          if (!s.fam.equals({PKG}.FellDefs.famIdx(id))) continue;
          if (s.trig == 2) {{
            if (c != 2) continue;
          }} else if (c == 1 && ny < y0) continue;
          if (!natural(s.wn, R, nx, ny, nz)) continue;
          wx[wc] = nx; wy[wc] = ny; wz[wc] = nz; wc++;
          if (c == 1 && ny == y0) {{ s.lkey[s.ln] = kk.longValue(); s.ln = s.ln + 1; }}
          else addClaim(s, nx, ny, nz, id, false);
          if (wc >= maxW) full = true;
        }}
      }}
    }}
  }}
  boolean claimLeaves = {PKG}.FellCfg.LEAVES && maxL > 0;
  int[] qx = new int[maxL + 1]; int[] qy = new int[maxL + 1]; int[] qz = new int[maxL + 1]; int[] qd = new int[maxL + 1];
  int qc = 0;
  java.util.HashSet lseen = new java.util.HashSet();
  for (int i = 0; i < cand.size(); i++) {{
    int[] cd = (int[]) cand.get(i);
    if (!natural(s.wn, R, cd[0], cd[1], cd[2])) continue;
    s.leafSeen = true;
    if (!claimLeaves || qc >= maxL) break;
    lseen.add(Long.valueOf(key(cd[0], cd[1], cd[2])));
    qx[qc] = cd[0]; qy[qc] = cd[1]; qz[qc] = cd[2]; qd[qc] = 1; qc++;
    addClaim(s, cd[0], cd[1], cd[2], cd[3], true);
  }}
  int lh = 0;
  while (claimLeaves && lh < qc && qc < maxL && !R.over) {{
    int cx = qx[lh]; int cy = qy[lh]; int cz = qz[lh]; int cdp = qd[lh];
    lh++;
    if (cdp >= 4) continue;
    for (int dx = -1; dx <= 1; dx++) {{
      for (int dy = -1; dy <= 1; dy++) {{
        for (int dz = -1; dz <= 1; dz++) {{
          if (dx == 0 && dy == 0 && dz == 0) continue;
          if (qc >= maxL) continue;
          int nx = cx + dx; int ny = cy + dy; int nz = cz + dz;
          if (nx - s.bx > rad || s.bx - nx > rad || nz - s.bz > rad || s.bz - nz > rad) continue;
          if (ny > top || ny < y0 - 1) continue;
          Long kk = Long.valueOf(key(nx, ny, nz));
          if (seen.contains(kk) || lseen.contains(kk)) continue;
          lseen.add(kk);
          int id = R.idx(nx, ny, nz);
          if (id <= 0 || {PKG}.FellDefs.codeIdx(id) != 4) continue;
          if (!natural(s.wn, R, nx, ny, nz)) continue;
          qx[qc] = nx; qy[qc] = ny; qz[qc] = nz; qd[qc] = cdp + 1; qc++;
          addClaim(s, nx, ny, nz, id, true);
        }}
      }}
    }}
  }}
}}""", fel))
# seeds + search (spec 2.3): TRUNK / BRANCH = the broken block (a search node, never a claim); UNDER = the natural trunk right above the
# broken block (a claim). late (the handler-read fallback, spec 3.1): the broken block is gone and physics may already have removed the
# next logs, so the search may step through up to 2 empty cells straight above the seed to reach the rest of the tree.
fel.addMethod(CtNewMethod.make(f"""
public static void run({PKG}.FellSnap s, {PKG}.FellRead R, boolean late) {{
  long t0 = System.nanoTime();
  int[] sx = new int[2]; int[] sy = new int[2]; int[] sz = new int[2]; int[] si = new int[2]; boolean[] sc = new boolean[2];
  int ns = 0;
  s.n = 0; s.ln = 0; s.leafSeen = false;
  if (s.trig == 3) {{
    int yy = s.by + 1;
    int empt = 0;
    boolean stop = false;
    while (!stop && yy <= s.by + 3) {{
      int id = R.idx(s.bx, yy, s.bz);
      if (id > 0 && {PKG}.FellDefs.codeIdx(id) == 1) {{
        if (natural(s.wn, R, s.bx, yy, s.bz)) {{
          s.fam = {PKG}.FellDefs.famIdx(id);
          sx[0] = s.bx; sy[0] = yy; sz[0] = s.bz; si[0] = id; sc[0] = true; ns = 1;
        }}
        stop = true;
      }} else if (id == 0 && late && empt < 2) {{
        empt++;
        yy++;
      }} else stop = true;
    }}
  }} else if (s.fam != null && s.fam.length() > 0) {{
    sx[0] = s.bx; sy[0] = s.by; sz[0] = s.bz; si[0] = 0; sc[0] = false; ns = 1;
    if (late) {{
      int yy = s.by + 1;
      int empt = 0;
      boolean stop = false;
      while (!stop && yy <= s.by + 3) {{
        int id = R.idx(s.bx, yy, s.bz);
        if (id == 0 && empt < 2) {{ empt++; yy++; continue; }}
        if (id > 0) {{
          int c = {PKG}.FellDefs.codeIdx(id);
          boolean ok = s.fam.equals({PKG}.FellDefs.famIdx(id)) && (s.trig == 2 ? c == 2 : (c == 1 || c == 2 || c == 3));
          if (ok && natural(s.wn, R, s.bx, yy, s.bz)) {{ sx[1] = s.bx; sy[1] = yy; sz[1] = s.bz; si[1] = id; sc[1] = true; ns = 2; }}
        }}
        stop = true;
      }}
    }}
  }}
  if (ns == 0 || s.fam == null) {{ s.n = 0; return; }}
  if (!rate(s.u)) {{ s.n = 0; if ({PKG}.FellCfg.DEBUG) {PKG}.SkillCfg.info("fell: snapshot skipped - over fell.maxSnapshotsPerSecond for " + s.u); return; }}
  search(s, R, sx, sy, sz, si, sc, ns);
  s.reads = R.reads;
  s.took = System.nanoTime() - t0;
}}""", fel))
# handler (spec 2.2 / 3.1 hook 1): trigger test (cheap for non-tree blocks: one read above), then the search while the tree still stands.
# Returns null (no snapshot), a FellSnap, or a FellSnap with late = true (reads failed in the handler: BreakTask searches instead).
fel.addMethod(CtNewMethod.make(f"""
public static {PKG}.FellSnap snapshot({WLD} w, java.util.UUID u, String pk, {BTY} bt, int x, int y, int z, boolean inOther) {{
  if (!{PKG}.FellCfg.on() || w == null || bt == null) return null;
  int c = {PKG}.FellDefs.code(bt);
  int trig;
  if (c == 1) trig = 1;
  else if (c == 2) trig = 2;
  else if (c == 3 || c == 4) return null;
  else if ({PKG}.FellCfg.UNDER_TRUNK) trig = 3;
  else return null;
  {PKG}.FellSnap s = new {PKG}.FellSnap();
  s.w = w; s.wn = w.getName(); s.u = u; s.pk = pk; s.created = System.currentTimeMillis();
  s.trig = trig; s.bx = x; s.by = y; s.bz = z; s.bt = bt; s.inOther = inOther;
  s.fam = null;
  if (trig != 3) s.fam = {PKG}.FellDefs.fam(bt);
  if (HANDLER_FAILED) {{ s.late = true; return s; }}
  {PKG}.FellRead R = new {PKG}.FellRead(w, {PKG}.FellCfg.MAX_READS);
  if (trig == 3) {{
    int above = R.idx(x, y + 1, z);
    if (R.err != null) {{ handlerFailed(R.err); s.late = true; return s; }}
    if (above <= 0 || {PKG}.FellDefs.codeIdx(above) != 1) return null;
  }}
  run(s, R, false);
  if (R.err != null) {{
    handlerFailed(R.err);
    s.late = true; s.n = 0; s.ln = 0; s.fam = null;
    if (trig != 3) s.fam = {PKG}.FellDefs.fam(bt);
    return s;
  }}
  if (s.n <= 0) return null;
  return s;
}}""", fel))
# the fallback search in BreakTask (world thread, the broken block is gone)
fel.addMethod(CtNewMethod.make(f"""
public static {PKG}.FellSnap snapshotLate({PKG}.FellSnap s) {{
  if (s == null || s.w == null || !{PKG}.FellCfg.on()) return null;
  {PKG}.FellRead R = new {PKG}.FellRead(s.w, {PKG}.FellCfg.MAX_READS);
  run(s, R, true);
  s.late = false;
  if (R.err != null) failed("late snapshot read", R.err);
  if (s.n <= 0) return null;
  return s;
}}""", fel))
# hand break (spec 2.4 handler steps 1-2) -> Object[]{watch it was unclaimed from (or null), Boolean inOther, Boolean reused}
fel.addMethod(CtNewMethod.make(f"""
public static Object[] onBreak(String wn, java.util.UUID u, int x, int y, int z) {{
  Object[] r = new Object[3];
  r[1] = Boolean.FALSE;
  r[2] = Boolean.FALSE;
  Long k = Long.valueOf(key(x, y, z));
  Object cm0 = CLAIMS.get(wn);
  if (cm0 != null) {{
    java.util.concurrent.ConcurrentHashMap cm = (java.util.concurrent.ConcurrentHashMap) cm0;
    Object h = cm.get(k);
    if (h instanceof {PKG}.FellWatch) {{
      {PKG}.FellWatch o = ({PKG}.FellWatch) h;
      cm.remove(k, o);
      if (o.live()) {{
        o.hand = o.hand + 1;
        r[0] = o;
        if (o.u.equals(u)) {{ o.touch(); r[2] = Boolean.TRUE; }}
        else r[1] = Boolean.TRUE;
        return r;
      }}
    }}
  }}
  Object lm0 = LAYER.get(wn);
  if (lm0 != null) {{
    Object lw = ((java.util.concurrent.ConcurrentHashMap) lm0).get(k);
    if (lw instanceof {PKG}.FellWatch) {{
      {PKG}.FellWatch o = ({PKG}.FellWatch) lw;
      if (o.live() && o.u.equals(u)) {{ o.touch(); r[2] = Boolean.TRUE; }}
    }}
  }}
  return r;
}}""", fel))
# a cancelled break puts back the claim its handler removed (spec 3.1 hook 2)
fel.addMethod(CtNewMethod.make(f"""
public static void restore(String wn, {BBE} ev, Object unclaimed) {{
  if (!(unclaimed instanceof {PKG}.FellWatch) || ev == null) return;
  {PKG}.FellWatch o = ({PKG}.FellWatch) unclaimed;
  if (!o.live()) return;
  {V3I} t = ev.getTargetBlock();
  if (t == null) return;
  if (claims(wn).putIfAbsent(Long.valueOf(key(t.x(), t.y(), t.z())), o) == null && o.hand > 0) o.hand = o.hand - 1;
}}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static int countFor(java.util.UUID u) {{
  int c = 0;
  java.util.Iterator it = WATCHES.keySet().iterator();
  while (it.hasNext()) {{
    {PKG}.FellWatch W = ({PKG}.FellWatch) it.next();
    if (W.live() && W.u.equals(u)) c++;
  }}
  return c;
}}""", fel))
# end a watch: release its claims / layer entries (only where they still point at it), optional chat summary, debug line (spec 2.5 / 2.9)
fel.addMethod(CtNewMethod.make(f"""
public static void end({PKG}.FellWatch W, boolean fromWorld) {{
  if (W == null || W.ended) return;
  W.ended = true;
  WATCHES.remove(W);
  try {{
    java.util.concurrent.ConcurrentHashMap cm = claims(W.wn);
    for (int i = 0; i < W.n; i++) cm.remove(Long.valueOf(W.key[i]), W);
    java.util.concurrent.ConcurrentHashMap lm = layer(W.wn);
    for (int j = 0; j < W.ln; j++) lm.remove(Long.valueOf(W.lkey[j]), W);
  }} catch (Throwable t) {{ failed("release", t); }}
  long now = System.currentTimeMillis();
  try {{
    if (fromWorld && {PKG}.FellCfg.MESSAGE && W.credited > 0 && {PKG}.SkillStore.notifyOn(W.u, "skills.xpGain")) {{
      {PR} pr = {UNI}.get().getPlayer(W.u);
      if (pr != null && pr.isValid()) {{
        StringBuilder sb = new StringBuilder("Tree felled: ");
        sb.append(W.cLogs).append(W.cLogs == 1 ? " log" : " logs");
        if (W.cLeaves > 0) sb.append(", ").append(W.cLeaves).append(W.cLeaves == 1 ? " leaf" : " leaves");
        if (W.xp > 0L && W.row >= 0 && W.row < {PKG}.SkillDefs.N) sb.append(" (+").append({PKG}.SkillDefs.fmt(W.xp)).append(" ").append({PKG}.SkillDefs.LABELS[W.row]).append(" XP)");
        pr.sendMessage({MSG}.raw(sb.toString()).color("#9fe0a0"));
      }}
    }}
  }} catch (Throwable t) {{ failed("summary", t); }}
  if ({PKG}.FellCfg.DEBUG) {PKG}.SkillCfg.info("fell: watch end " + W.u + " world " + W.wn + " claims " + W.n + " (logs " + W.sLogs + ", leaves " + W.sLeaves + ", layer " + W.ln + ") credited " + W.credited + " (logs " + W.cLogs + ", leaves " + W.cLeaves + ") hand " + W.hand + " env " + W.env + " lost " + W.lost + " other " + W.other + " replaced " + W.replaced + " skipped " + W.skipped + " dropped " + W.dropped + " collections " + W.collYes + "/" + (W.collYes + W.collNo) + " xp " + W.xp + " ms " + (now - W.created));
}}""", fel))
# watches whose world stopped running tasks never end by themselves: drop them after maxWatchMs + 30 s
fel.addMethod(CtNewMethod.make(f"""
public static void pruneStale() {{
  long now = System.currentTimeMillis();
  java.util.ArrayList old = new java.util.ArrayList();
  java.util.Iterator it = WATCHES.keySet().iterator();
  while (it.hasNext()) {{
    {PKG}.FellWatch W = ({PKG}.FellWatch) it.next();
    if (now - W.created >= {PKG}.FellCfg.MAX_WATCH_MS + 30000L) old.add(W);
  }}
  for (int i = 0; i < old.size(); i++) end(({PKG}.FellWatch) old.get(i), false);
}}""", fel))
# commit (spec 2.4 commit steps 1-3; BreakTask, world thread, not cancelled)
fel.addMethod(CtNewMethod.make(f"""
public static void commit({PKG}.FellSnap s0) {{
  {PKG}.FellSnap s = s0;
  if (s == null) return;
  if (s.late) s = snapshotLate(s);
  if (s == null || s.n <= 0) return;
  boolean dbg = {PKG}.FellCfg.DEBUG;
  if ({PKG}.FellCfg.NEED_LEAVES && !s.leafSeen) {{ if (dbg) {PKG}.SkillCfg.info("fell: snapshot dropped - no natural leaves (" + s.logs + " logs) at " + s.bx + " " + s.by + " " + s.bz); return; }}
  pruneStale();
  if (countFor(s.u) >= {PKG}.FellCfg.MAX_PER_PLAYER) {{ if (dbg) {PKG}.SkillCfg.info("fell: snapshot dropped - fell.maxWatchesPerPlayer reached for " + s.u); return; }}
  if (WATCHES.size() >= {PKG}.FellCfg.MAX_WATCHES) {{ if (dbg) {PKG}.SkillCfg.info("fell: snapshot dropped - fell.maxWatches reached"); return; }}
  {PKG}.FellWatch W = new {PKG}.FellWatch(s);
  java.util.concurrent.ConcurrentHashMap cm = claims(s.wn);
  int held = 0;
  for (int i = 0; i < W.n; i++) {{
    Long k = Long.valueOf(W.key[i]);
    Object h = cm.get(k);
    boolean take = h == null;
    if (!take) {{
      {PKG}.FellWatch o = ({PKG}.FellWatch) h;
      if (!o.live() || o.u.equals(s.u) || !s.inOther) {{
        take = true;
        if (o.live() && o != W) o.other = o.other + 1;
      }}
    }}
    if (take) {{ cm.put(k, W); held++; }}
    else {{ W.done[i] = true; W.left = W.left - 1; W.skipped = W.skipped + 1; }}
  }}
  if (held == 0) {{ if (dbg) {PKG}.SkillCfg.info("fell: snapshot dropped - every position is claimed by another player's falling tree"); return; }}
  java.util.concurrent.ConcurrentHashMap lm = layer(s.wn);
  for (int j = 0; j < W.ln; j++) lm.put(Long.valueOf(W.lkey[j]), W);
  WATCHES.put(W, Boolean.TRUE);
  if (dbg) {PKG}.SkillCfg.info("fell: snapshot " + s.u + " world " + s.wn + " trigger " + (s.trig == 1 ? "trunk" : (s.trig == 2 ? "branch" : "under")) + " at " + s.bx + " " + s.by + " " + s.bz + " logs " + s.logs + " leaves " + s.leaves + " layer " + s.ln + " held " + held + " reads " + s.reads + " took " + (s.took / 1000L) + " us" + (s.inOther ? " (cut inside another player's fall)" : ""));
  W.hop = true;
  if (TEST_NO_SCHEDULE) return;
  try {{ {HSV}.SCHEDULED_EXECUTOR.schedule(W, {PKG}.FellCfg.POLL_MS, java.util.concurrent.TimeUnit.MILLISECONDS); }} catch (Throwable t) {{ failed("schedule", t); end(W, false); }}
}}""", fel))
# EnvSys: an explosion / fire removed a position -> unclaim it (never paid as felled, spec 2.4 "Environment breaks")
fel.addMethod(CtNewMethod.make(f"""
public static void envBreak(String wn, {V3I} t) {{
  if (t == null || wn == null) return;
  Object m = CLAIMS.get(wn);
  if (m == null) return;
  Object o = ((java.util.concurrent.ConcurrentHashMap) m).remove(Long.valueOf(key(t.x(), t.y(), t.z())));
  if (o instanceof {PKG}.FellWatch) {{
    {PKG}.FellWatch W = ({PKG}.FellWatch) o;
    W.env = W.env + 1;
  }}
}}""", fel))
# skill:fn:felledBy (spec 2.8): "falling" = claimed by a live watch (atMillis = snapshot time), "felled" = credited within fell.memoryMs
fel.addMethod(CtNewMethod.make(f"""
public static Object[] felledBy(String wn, int x, int y, int z) {{
  long k = key(x, y, z);
  Object m = CLAIMS.get(wn);
  if (m != null) {{
    Object o = ((java.util.concurrent.ConcurrentHashMap) m).get(Long.valueOf(k));
    if (o instanceof {PKG}.FellWatch) {{
      {PKG}.FellWatch W = ({PKG}.FellWatch) o;
      if (W.live()) return new Object[] {{ W.u, W.pk, Long.valueOf(W.created), "falling" }};
    }}
  }}
  Object[] f = felledGet(wn, k);
  if (f == null) return null;
  return new Object[] {{ f[0], f[1], f[2], "felled" }};
}}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static void endAll() {{
  java.util.ArrayList all = new java.util.ArrayList(WATCHES.keySet());
  for (int i = 0; i < all.size(); i++) end(({PKG}.FellWatch) all.get(i), false);
  CLAIMS.clear();
  LAYER.clear();
  WATCHES.clear();
  clearFelled();
}}""", fel))

# FellDrops: the engine's physics drop selection (BlockHarvestUtils.naturallyRemoveBlockByPhysics, bytecode 2026-09-24): Physics
# (quantity 1), else Breaking (its quantity), else Soft, else Harvest -> getDrops(bt, quantity, itemId, dropListId). A fresh roll.
fdr.addMethod(CtNewMethod.make(f"""
public static java.util.List roll({BTY} bt) {{
  if (bt == null) return null;
  int q = 1;
  String item = null;
  String list = null;
  {BGA} g = bt.getGathering();
  if (g != null) {{
    {PDT} ph = g.getPhysics();
    {BBD} br = g.getBreaking();
    {SBD} so = g.getSoft();
    {HDT} hv = g.getHarvest();
    if (ph != null) {{ item = ph.getItemId(); list = ph.getDropListId(); }}
    else if (br != null) {{ q = br.getQuantity(); item = br.getItemId(); list = br.getDropListId(); }}
    else if (so != null) {{ item = so.getItemId(); list = so.getDropListId(); }}
    else if (hv != null) {{ item = hv.getItemId(); list = hv.getDropListId(); }}
  }}
  return {BHU}.getDrops(bt, q, item, list);
}}""", fdr))

# FellCredit (spec 2.6): one felled position, world thread of the tree's world
fcr.addMethod(CtNewMethod.make(f"""
public static void coll({PKG}.FellWatch W, {BTY} bt) {{
  Object f = {PKG}.SkillStore.bridge().get("coll:fn:add");
  if (!(f instanceof java.util.function.Function)) return;
  java.util.List drops = null;
  try {{ drops = {PKG}.FellDrops.roll(bt); }} catch (Throwable t) {{ {PKG}.Fell.failed("drop roll", t); return; }}
  if (drops == null) return;
  for (int j = 0; j < drops.size(); j++) {{
    Object o = drops.get(j);
    if (!(o instanceof {IS})) continue;
    {IS} is = ({IS}) o;
    if (is.isEmpty() || is.getItemId() == null || is.getQuantity() <= 0) continue;
    Object r = null;
    try {{ r = ((java.util.function.Function) f).apply(new Object[] {{ W.u, is.getItemId(), Long.valueOf((long) is.getQuantity()), "skills:felled", W.pk }}); }} catch (Throwable t) {{ r = null; }}
    if (Boolean.TRUE.equals(r)) W.collYes = W.collYes + 1;
    else W.collNo = W.collNo + 1;
  }}
}}""", fcr))
fcr.addMethod(CtNewMethod.make(f"""
public static void one({PKG}.FellWatch W, int i) {{
  try {{
    {PR} pr = {UNI}.get().getPlayer(W.u);
    if (pr == null || !pr.isValid()) {{ W.dropped = W.dropped + 1; return; }}
    if (!W.pk.equals({PKG}.SkillStore.pkey(W.u))) {{ W.dropped = W.dropped + 1; return; }}
    if ({PKG}.SkillStore.bridge().get("profile:busy:" + W.u.toString()) != null) {{ W.dropped = W.dropped + 1; return; }}
    {WLD} pw = {UNI}.get().getWorld(pr.getWorldUuid());
    if (pw == null || !W.wn.equals(pw.getName())) {{ W.dropped = W.dropped + 1; return; }}
    {REF} r = pr.getReference();
    if (r == null || !r.isValid()) {{ W.dropped = W.dropped + 1; return; }}
    if ({PKG}.SkillXp.creative(r.getStore(), r)) {{ W.dropped = W.dropped + 1; return; }}
    {BTY} bt = ({BTY}) {BTY}.getAssetMap().getAsset(W.idx[i]);
    if (bt == null) {{ W.dropped = W.dropped + 1; return; }}
    long[] rule = {PKG}.SkillCfg.classifyBreak(bt);
    int row = rule == null ? -1 : (int) rule[0];
    if (rule != null && rule[2] == 1L) {{
      double fct = W.leaf[i] ? {PKG}.FellCfg.LEAF_XP_FACTOR : {PKG}.FellCfg.XP_FACTOR;
      long xp = Math.round((double) rule[1] * fct);
      if (xp > 0L) {{
        long amt = {PKG}.SkillBonus.boost(W.u, row, {PKG}.GatherPace.apply(W.u, row, xp));   // 0.4.14: the gathering pace first
        {PKG}.SkillXp.gain3(pr, row, amt, true, false);
        W.xp = W.xp + amt;
        W.row = row;
      }}
    }}
    if ({PKG}.FellCfg.DOUBLE_DROPS && rule != null) {PKG}.Perks.breakDouble(pr, row, bt, W.wn, true);
    if ({PKG}.FellCfg.COLLECTIONS) coll(W, bt);
    if ({PKG}.FellCfg.NODES && rule != null) {PKG}.SkillBonus.felled(pr, row, bt, W.wn, W.x[i], W.y[i], W.z[i], W.pk);
    {PKG}.Fell.felledPut(W.wn, W.key[i], new Object[] {{ W.u, W.pk, Long.valueOf(System.currentTimeMillis()), bt.getId() }});
    W.credited = W.credited + 1;
    if (W.leaf[i]) W.cLeaves = W.cLeaves + 1;
    else W.cLogs = W.cLogs + 1;
  }} catch (Throwable t) {{ {PKG}.Fell.failed("credit", t); }}
}}""", fcr))

# FellWatch.run (spec 2.5; the HarvestTask hop pattern: scheduler -> world.execute -> poll)
fwt.addMethod(CtNewMethod.make(f"""
public void run() {{
  if (this.ended) return;
  long now = System.currentTimeMillis();
  if (this.hop) {{
    this.hop = false;
    if (now - this.created >= {PKG}.FellCfg.MAX_WATCH_MS + 30000L) {{ {PKG}.Fell.end(this, false); return; }}
    try {{ this.w.execute(this); }} catch (Throwable t) {{ {PKG}.Fell.end(this, false); }}
    return;
  }}
  try {{
    {PKG}.FellRead R = new {PKG}.FellRead(this.w, 2147483647);
    java.util.concurrent.ConcurrentHashMap cm = {PKG}.Fell.claims(this.wn);
    for (int i = 0; i < this.n; i++) {{
      if (this.done[i]) continue;
      int cur = R.idx(this.x[i], this.y[i], this.z[i]);
      if (cur == this.idx[i]) continue;
      this.done[i] = true;
      this.left--;
      this.lastChange = now;
      if (cur != 0) {{
        if (cur < 0) this.lost++;
        else this.replaced++;
        continue;
      }}
      Long k = Long.valueOf(this.key[i]);
      if (cm.get(k) != this) continue;
      cm.remove(k, this);
      {PKG}.FellCredit.one(this, i);
    }}
    if (R.err != null) {PKG}.Fell.failed("watch read", R.err);
  }} catch (Throwable t) {{ {PKG}.Fell.failed("watch", t); {PKG}.Fell.end(this, true); return; }}
  if (this.left <= 0 || now - this.lastChange >= {PKG}.FellCfg.QUIET_MS || now - this.created >= {PKG}.FellCfg.MAX_WATCH_MS || !{PKG}.Fell.online(this.u)) {{ {PKG}.Fell.end(this, true); return; }}
  this.hop = true;
  try {{ {HSV}.SCHEDULED_EXECUTOR.schedule(this, {PKG}.FellCfg.POLL_MS, java.util.concurrent.TimeUnit.MILLISECONDS); }} catch (Throwable t) {{ {PKG}.Fell.end(this, true); }}
}}""", fwt))

# skill:fn:felledBy (spec 2.8): apply(Object[]{String world, Integer x, Integer y, Integer z}) -> Object[]{UUID, pkey, Long at, state} | null
ffn.addInterface(pool.get("java.util.function.Function"))
ffn.addConstructor(CtNewConstructor.make("public FelledByFn() { }", ffn))
ffn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 4 || a[0] == null || !(a[1] instanceof Number) || !(a[2] instanceof Number) || !(a[3] instanceof Number)) return null;
    return {PKG}.Fell.felledBy(String.valueOf(a[0]), ((Number) a[1]).intValue(), ((Number) a[2]).intValue(), ((Number) a[3]).intValue());
  }} catch (Throwable t) {{ return null; }}
}}""", ffn))

# ================= deferred tasks (run on the world thread after every system saw the event) =================
btk.addInterface(pool.get("java.lang.Runnable"))
btk.addField(CtField.make(f"public {BBE} ev;", btk))
btk.addField(CtField.make("public java.util.UUID u;", btk))
btk.addField(CtField.make("public String world;", btk))
btk.addField(CtField.make("public long[] rule;", btk))
btk.addField(CtField.make("public Object fs;", btk))          # 0.4.2: the FellSnap taken in the handler (null = none)
btk.addField(CtField.make("public Object unclaimed;", btk))   # 0.4.2: the FellWatch whose claim this break removed (put back if cancelled)
btk.addConstructor(CtNewConstructor.make(f"""
public BreakTask({BBE} ev, java.util.UUID u, String world, long[] rule) {{
  this.ev = ev; this.u = u; this.world = world; this.rule = rule;
}}""", btk))
btk.addConstructor(CtNewConstructor.make(f"""
public BreakTask({BBE} ev, java.util.UUID u, String world, long[] rule, Object fs, Object unclaimed) {{
  this.ev = ev; this.u = u; this.world = world; this.rule = rule; this.fs = fs; this.unclaimed = unclaimed;
}}""", btk))
btk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PKG}.Sickle.breakDone(this.u, this.ev);   // 0.4.14: the F-pickup context ends with its break's task
    if (this.ev.isCancelled()) {{
      try {{ {PKG}.Fell.restore(this.world, this.ev, this.unclaimed); }} catch (Throwable ft) {{ {PKG}.Fell.failed("restore", ft); }}
      return;
    }}
    if (this.fs != null) {{
      try {{ {PKG}.Fell.commit(({PKG}.FellSnap) this.fs); }} catch (Throwable ft) {{ {PKG}.Fell.failed("commit", ft); }}
    }}
    boolean wasPlaced = false;
    if ({PKG}.SkillCfg.IGNORE_PLACED) {{
      {V3I} t = this.ev.getTargetBlock();
      if (t != null) wasPlaced = {PKG}.PlacedStore.remove(this.world, {PKG}.PlacedStore.key(t.x(), t.y(), t.z()));
    }}
    if (this.rule == null) return;
    if (wasPlaced && this.rule[2] == 1L) return;
    if (this.rule[2] == 0L) {{
      {V3I} c = this.ev.getTargetBlock();
      if (c != null && !{PKG}.HarvestGate.claim(this.world, {PKG}.PlacedStore.key(c.x(), c.y(), c.z()), System.currentTimeMillis(), {PKG}.SkillCfg.HARVEST_GATE_MS)) return;
    }}
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    {PKG}.SkillXp.gain(pr, (int) this.rule[0], this.rule[1]);
    {PKG}.Perks.breakDouble(pr, (int) this.rule[0], this.ev.getBlockType(), this.world, this.rule[2] == 0L || {PKG}.SkillCfg.IGNORE_PLACED);
    if (this.rule[2] == 0L || {PKG}.SkillCfg.IGNORE_PLACED) {{
      {V3I} g = this.ev.getTargetBlock();
      if (g != null) {PKG}.SkillBonus.gather(pr, (int) this.rule[0], this.ev.getBlockType(), this.world, false, g.x(), g.y(), g.z());
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("break award failed: " + t); }}
}}""", btk))

ptk.addInterface(pool.get("java.lang.Runnable"))
ptk.addField(CtField.make(f"public {PBE} ev;", ptk))
ptk.addField(CtField.make("public String world;", ptk))
ptk.addConstructor(CtNewConstructor.make(f"public PlaceTask({PBE} ev, String world) {{ this.ev = ev; this.world = world; }}", ptk))
ptk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (this.ev.isCancelled()) return;
    {V3I} t = this.ev.getTargetBlock();
    if (t == null) return;
    if ({PKG}.FellCfg.SKIP_SAPLINGS) {{
      {IS} hand = this.ev.getItemInHand();
      String hid = hand == null ? null : hand.getItemId();
      if (hid != null && hid.startsWith("Plant_Sapling_")) return;
    }}
    {PKG}.PlacedStore.add(this.world, {PKG}.PlacedStore.key(t.x(), t.y(), t.z()));
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("place record failed: " + t); }}
}}""", ptk))

# F-harvest verification (world thread): pay only once the block at the position is no longer the ripe block the player used.
# UseBlockEvent.Post fires before the pushed HarvestCrop root runs and also when it fails, so poll: next tick, then every
# 100 ms (scheduler hop -> world.execute, FlushTask pattern) for up to 20 retries; still ripe after that = no harvest, no XP.
htk.addInterface(pool.get("java.lang.Runnable"))
htk.addField(CtField.make("public java.util.UUID u;", htk))
htk.addField(CtField.make(f"public {WLD} w;", htk))
htk.addField(CtField.make("public String wn;", htk))
htk.addField(CtField.make("public int x;", htk))
htk.addField(CtField.make("public int y;", htk))
htk.addField(CtField.make("public int z;", htk))
htk.addField(CtField.make("public String ripe;", htk))
htk.addField(CtField.make("public long amount;", htk))
htk.addField(CtField.make("public int tries;", htk))
htk.addField(CtField.make("public boolean hop;", htk))
htk.addField(CtField.make(f"public {BTY} bt;", htk))   # 0.3: the ripe block type, for the Farming double drop
htk.addConstructor(CtNewConstructor.make(f"""
public HarvestTask(java.util.UUID u, {WLD} w, String wn, int x, int y, int z, String ripe, long amount) {{
  this.u = u; this.w = w; this.wn = wn; this.x = x; this.y = y; this.z = z; this.ripe = ripe; this.amount = amount;
  this.tries = 0; this.hop = false;
}}""", htk))
htk.addMethod(CtNewMethod.make(f"""
public void run() {{
  long k = {PKG}.PlacedStore.key(this.x, this.y, this.z);
  if (this.hop) {{
    this.hop = false;
    try {{ this.w.execute(this); }} catch (Throwable t) {{ {PKG}.HarvestGate.end(this.wn, k); }}
    return;
  }}
  try {{
    String cur = {PKG}.SkillCfg.blockIdAt(this.w, this.x, this.y, this.z);
    if (cur == null) {{ {PKG}.HarvestGate.end(this.wn, k); return; }}
    if (!cur.equals(this.ripe)) {{
      {PKG}.HarvestGate.end(this.wn, k);
      if (!{PKG}.HarvestGate.claim(this.wn, k, System.currentTimeMillis(), {PKG}.SkillCfg.HARVEST_GATE_MS)) return;
      {PR} pr = {UNI}.get().getPlayer(this.u);
      if (pr == null || !pr.isValid()) return;
      {PKG}.SkillXp.gain(pr, {PKG}.SkillDefs.FARMING, this.amount);
      {PKG}.Perks.harvestDouble(pr, this.bt, this.wn);
      {PKG}.SkillBonus.gather(pr, {PKG}.SkillDefs.FARMING, this.bt, this.wn, true, this.x, this.y, this.z);
      return;
    }}
    this.tries++;
    if (this.tries > 20) {{ {PKG}.HarvestGate.end(this.wn, k); return; }}
    this.hop = true;
    {HSV}.SCHEDULED_EXECUTOR.schedule(this, 100L, java.util.concurrent.TimeUnit.MILLISECONDS);
  }} catch (Throwable t) {{
    {PKG}.HarvestGate.end(this.wn, k);
    {PKG}.SkillCfg.warn("harvest award failed: " + t);
  }}
}}""", htk))

# ================= CraftTask (0.4): vanilla Alchemy Bench award, after every other system saw the Post event =================
ctk.addInterface(pool.get("java.lang.Runnable"))
ctk.addField(CtField.make(f"public {CRE} ev;", ctk))
ctk.addField(CtField.make("public java.util.UUID u;", ctk))
ctk.addField(CtField.make("public String world;", ctk))
ctk.addField(CtField.make(f"public {CRR} rc;", ctk))
ctk.addField(CtField.make("public long[] rule;", ctk))
ctk.addField(CtField.make("public int units;", ctk))
ctk.addField(CtField.make("public String key;", ctk))
ctk.addConstructor(CtNewConstructor.make(f"""
public CraftTask({CRE} ev, java.util.UUID u, String world, {CRR} rc, long[] rule, int units, String key) {{
  this.ev = ev; this.u = u; this.world = world; this.rc = rc; this.rule = rule; this.units = units; this.key = key;
}}""", ctk))
ctk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (this.ev.isCancelled()) return;
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    if (!this.key.equals({PKG}.SkillStore.pkey(this.u))) return;
    long amt = {PKG}.SkillCfg.scaled(this.rule[1] * (long) this.units);
    if (amt > 0L) {PKG}.SkillXp.gain(pr, (int) this.rule[0], amt);
    if (this.rule[0] == (long) {PKG}.SkillDefs.ALCHEMY) {PKG}.Brew.extraPotion(pr, this.rc, this.units, this.world);
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("craft award failed: " + t); }}
}}""", ctk))
# ================= SmeltTask (0.4): vanilla Furnace award (world thread); offline -> silent write, owed coins paid on the next gain =====
stk.addInterface(pool.get("java.lang.Runnable"))
stk.addField(CtField.make("public java.util.UUID u;", stk))
stk.addField(CtField.make("public int slot;", stk))
stk.addField(CtField.make("public long amt;", stk))
stk.addField(CtField.make("public String key;", stk))
stk.addConstructor(CtNewConstructor.make("""
public SmeltTask(java.util.UUID u, int slot, long amt, String key) {
  this.u = u; this.slot = slot; this.amt = amt; this.key = key;
}""", stk))
stk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (this.amt <= 0L) return;
    if (!this.key.equals({PKG}.SkillStore.pkey(this.u))) return;
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr != null && pr.isValid()) {PKG}.SkillXp.gain(pr, this.slot, this.amt);
    else {PKG}.SkillStore.addK(this.key, this.u, null, this.slot, this.amt);
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("smelt award failed: " + t); }}
}}""", stk))
# ================= BridgeTask (0.4): cross-mod XP award on the player's world thread =================
# 0.4.1: Exploration grants add no "+N Exploration XP" chat line (note = false): SkyyExploration writes its own chest / zone /
# aggregated chunk lines (hidden by /explore quiet); level-up lines and coins show as usual.
btsk.addInterface(pool.get("java.lang.Runnable"))
btsk.addField(CtField.make("public java.util.UUID u;", btsk))
btsk.addField(CtField.make("public int slot;", btsk))
btsk.addField(CtField.make("public long amt;", btsk))
btsk.addField(CtField.make("public String key;", btsk))
btsk.addField(CtField.make("public String source;", btsk))
btsk.addField(CtField.make(f"public {CRR} rc;", btsk))
btsk.addField(CtField.make("public int units;", btsk))
btsk.addConstructor(CtNewConstructor.make(f"""
public BridgeTask(java.util.UUID u, int slot, long amt, String key, String source, {CRR} rc, int units) {{
  this.u = u; this.slot = slot; this.amt = amt; this.key = key; this.source = source; this.rc = rc; this.units = units;
}}""", btsk))
btsk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    if (!this.key.equals({PKG}.SkillStore.pkey(this.u))) return;
    String wn = null;
    {REF} r = pr.getReference();
    if (r != null && r.isValid()) {{
      {ST} st = r.getStore();
      if ({PKG}.SkillXp.creative(st, r)) return;
      Object ext = st.getExternalData();
      if (ext instanceof {EST}) {{
        {WLD} w = (({EST}) ext).getWorld();
        if (w != null) wn = w.getName();
      }}
    }}
    {PKG}.SkillXp.gain3(pr, this.slot, this.amt, this.slot != {PKG}.SkillDefs.EXPLORATION, false);
    if (this.rc != null && this.slot == {PKG}.SkillDefs.ALCHEMY && wn != null) {PKG}.Brew.extraPotion(pr, this.rc, this.units, wn);
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("bridge XP award (" + this.source + ") failed: " + t); }}
}}""", btsk))
# BridgeXp.offer (0.4): >= 0 = accepted (scaled XP queued; 0 = nothing to pay), -1 = refused for now (offline, profile key differs,
# per-minute cap), -2 = refused for good (bad slot, over bridge.maxXpPerCall = the caller's base XP, before multiplier and tree bonus).
# grant = true for skill:fn:addxp (tree XP bonus only for bridge.bonus.addxpSkills), false for skill:fn:craftxp (bridge.bonus.xpSkills).
# Any thread; no I/O; never blocks. 0.4.1: a slot that is not SkillDefs.boostable (Exploration) is paid its base XP exactly - no xp
# multiplier, no tree bonus (still inside bridge.maxXpPerMinute).
# 0.4.10: what an accepted offer pays = paid(): the xp multiplier, then the class skill XP multiplier (SkillCfg.classXp: grants into a class
# skill; any other slot unchanged), then the tree bonus. bridge.maxXpPerMinute (allow) counts this paid number; bridge.maxXpPerCall and
# divinity.healXpMaxPerMinute (HealXp.take, before this call) count the base. Any thread, no I/O.
# 0.4.11: paidX(..., cls) - cls false skips the class skill XP multiplier (Priest heal XP: HealXp.offer -> offerX(..., false)); paid = cls true
bxp.addMethod(CtNewMethod.make(f"""
public static long paidX(java.util.UUID u, int slot, long base, boolean grant, boolean cls) {{
  if (base <= 0L || slot < 0 || slot >= {PKG}.SkillDefs.N) return 0L;
  boolean canBoost = {PKG}.SkillDefs.boostable(slot);
  long amt = canBoost ? {PKG}.SkillCfg.scaled(base) : base;
  if (canBoost && cls) amt = {PKG}.SkillCfg.classXp(slot, amt);
  if (canBoost && (!grant || {PKG}.SkillBonus.grantBonus(slot))) amt = {PKG}.SkillBonus.boost(u, slot, amt);
  return amt;
}}""", bxp))
bxp.addMethod(CtNewMethod.make("""
public static long paid(java.util.UUID u, int slot, long base, boolean grant) {
  return paidX(u, slot, base, grant, true);
}""", bxp))
# 0.4.11: offerX = 0.4.10's offer with the cls switch (paidX); offer(...) = offerX(..., true) for every caller but HealXp.offer
bxp.addMethod(CtNewMethod.make(f"""
public static long offerX(java.util.UUID u, int slot, long base, String source, String expect, {CRR} rc, int units, boolean grant, boolean cls) {{
  if (u == null || slot < 0 || slot >= {PKG}.SkillDefs.N || slot == {PKG}.SkillDefs.COMBAT) return -2L;
  if (base <= 0L) return 0L;
  if (base > {PKG}.BridgeCfg.PER_CALL) {{ warnLimited(u, "refused " + base + " XP from " + source + " (over bridge.maxXpPerCall " + {PKG}.BridgeCfg.PER_CALL + ")"); return -2L; }}
  {PR} pr = {UNI}.get().getPlayer(u);
  if (pr == null || !pr.isValid()) return -1L;
  String k = {PKG}.SkillStore.pkey(u);
  if (expect != null && expect.length() > 0 && !expect.equals(k)) return -1L;
  {WLD} w = {UNI}.get().getWorld(pr.getWorldUuid());
  if (w == null) return -1L;
  long amt = paidX(u, slot, base, grant, cls);
  if (amt <= 0L) return 0L;
  if (!allow(u, amt)) {{ warnLimited(u, "bridge.maxXpPerMinute " + {PKG}.BridgeCfg.PER_MIN + " reached - refused " + amt + " XP from " + source); return -1L; }}
  w.execute(new {PKG}.BridgeTask(u, slot, amt, k, source == null ? "?" : source, rc, units));
  return amt;
}}""", bxp))
bxp.addMethod(CtNewMethod.make(f"""
public static long offer(java.util.UUID u, int slot, long base, String source, String expect, {CRR} rc, int units, boolean grant) {{
  return offerX(u, slot, base, source, expect, rc, units, grant, true);
}}""", bxp))
# ================= HealXp part 2 (0.4.4): skill:fn:healxp -> Divinity XP (research/Classes-Berserker-Priest-Spec.md 3.4) =================
# true = accepted (queued on the player's world thread) or nothing to pay; false = refused (see the header: part off / rate 0, bad hp, not
# a Priest (class skill Divinity = slot 15), class still following a profile switch, the cap's window is full (0.4.15 fix round: a heal
# bigger than the room left pays the room - it was all or nothing),
# BridgeXp.offer refused). The cap ring counts the base heal XP; a refused offer gives its share back (a task the world thread drops later
# keeps it for the rest of the window - fails closed, see the header). Any thread, no I/O, never throws.
# 0.4.11: heal XP is FINAL - BridgeXp.offerX(..., cls false) skips the class skill XP multiplier; the cap counts the heal XP before the
# general xp multiplier and the tree bonus (= what the Priest gets at the defaults: 1 / 1.25 per HP, at most 900 a minute)
hxp.addMethod(CtNewMethod.make(f"""
public static boolean offer(java.util.UUID u, double hp, String source, String expect, boolean self) {{
  try {{
    if (u == null || !{PKG}.DivCfg.onFor(self)) return false;
    if (Double.isNaN(hp) || Double.isInfinite(hp) || hp <= 0.0) return false;
    if ({PKG}.SkillClass.slot(u) != {PKG}.SkillDefs.DIVINITY || !{PKG}.SkillClass.consistent(u)) return false;
    long base = amount(hp, {PKG}.DivCfg.rate(self));
    if (base <= 0L) return true;
    long cap = {PKG}.DivCfg.MAX_MIN;
    long pay = grant(u, base, cap, System.currentTimeMillis());   // 0.4.15 fix round: what fits in the minute is paid (was all or nothing)
    if (pay <= 0L) {{ warnLimited(u, "divinity.healXpMaxPerMinute " + cap + " reached - refused " + base + " XP from " + source); return false; }}
    if (pay < base) warnLimited(u, "divinity.healXpMaxPerMinute " + cap + " reached - paid " + pay + " of " + base + " XP from " + source);
    long r = -1L;
    try {{ r = {PKG}.BridgeXp.offerX(u, {PKG}.SkillDefs.DIVINITY, pay, source, expect, null, 0, false, false); }} catch (Throwable t) {{ r = -1L; }}
    if (r < 0L) {{ if (cap > 0L) give(u, pay); return false; }}
    return true;
  }} catch (Throwable t) {{ return false; }}
}}""", hxp))
# ================= MobXp maths (0.4.14) - compiled before PartyXp (one2 uses them) =================
# levelFactor = 1 + BONUS x (L - 1) (1 without a level or with the part off); gapFactor(L, S): d = L - S, above FREE +ABOVE a level up to MAX,
# below -FREE -BELOW a level down to MIN; factor = both; pay = SkillCfg.classXp's rule with the factor (one chance rounding, the 1e-9 rule)
mxp.addMethod(CtNewMethod.make(J14(r"""
public static double levelFactor(int L) {
  if (!ON || L < 1) return 1.0;
  double f = 1.0 + BONUS * (double) (L - 1);
  return f > 0.0 ? f : 0.0;
}"""), mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static double gapFactor(int L, int S) {
  if (!ON || L < 1) return 1.0;
  int d = L - (S < 0 ? 0 : S);
  if (d > FREE) {
    double g = 1.0 + ABOVE * (double) (d - FREE);
    return g > MAX ? MAX : g;
  }
  if (d < -FREE) {
    double g = 1.0 - BELOW * (double) (-d - FREE);
    return g < MIN ? MIN : g;
  }
  return 1.0;
}"""), mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static double factor(int L, int S) {
  return levelFactor(L) * gapFactor(L, S);
}"""), mxp))
mxp.addMethod(CtNewMethod.make(J14(r"""
public static long pay(int slot, long base, double factor) {
  if (base <= 0L || !(factor > 0.0)) return 0L;
  double m = @PKG@.SkillDefs.isClass(slot) ? @PKG@.SkillCfg.CLASS_MULT : 1.0;
  if (!(m > 0.0)) return 0L;
  double x = (double) base * m * factor;
  if (x >= 9.0E15) return 9000000000000000L;
  double r = Math.rint(x);
  if (Math.abs(x - r) < 1.0E-9) x = r;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}"""), mxp))
# the dead mob's level from SkyyMobs (bridge mob:fn:level, Object[]{world name, the entity's UUIDComponent uuid} -> Integer, -1 = none); its
# MOBS entry is removed only when the entity leaves the store, so it still answers at the DeathComponent. -1 = no level (any failure too)
mxp.addMethod(CtNewMethod.make(J14(r"""
public static int levelOf(@ST@ s, @REF@ r) {
  try {
    if (s == null || r == null) return -1;
    Object f = @PKG@.SkillStore.bridge().get("mob:fn:level");
    if (!(f instanceof java.util.function.Function)) return -1;
    @UUC@ uc = (@UUC@) s.getComponent(r, @UUC@.getComponentType());
    if (uc == null || uc.getUuid() == null) return -1;
    String wn = null;
    Object ext = s.getExternalData();
    if (ext instanceof @EST@) {
      @WLD@ w = ((@EST@) ext).getWorld();
      if (w != null) wn = w.getName();
    }
    Object o = ((java.util.function.Function) f).apply(new Object[] { wn, uc.getUuid() });
    if (!(o instanceof Number)) return -1;
    int L = ((Number) o).intValue();
    return L >= 1 ? L : -1;
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.SkillCfg.warn("mob level lookup (mob:fn:level) failed (logged once): " + t); }
    return -1;
  }
}"""), mxp))

# ================= PartyXp (0.4.2 stage 2, beta backlog 6: "party should share combat XP") =================
# World thread (called by KillSys after the killer's own award). Every OTHER member of the killer's SkyyParty party (party:fn:members,
# String[] of member UUIDs, leader first; empty when not in a party) who is online, in the SAME world (their Ref lives in the killer's
# entity store = this world thread, so their components may be read here), ready, alive, not in creative (the creativeXp rule of a
# normal kill) and within party.combatShare.radius blocks of the killer gets amount(base, fraction) into THEIR OWN current class skill:
# SkillClass.slot of THEIR class (needs SkyyClasses + a class; skipped while their class still follows a profile switch - consistent()),
# written through SkillXp.gain4 = THEIR active profile (pkey). Only the killer needs a class weapon (KillSys.killSlot). base = the
# killer's kill XP after the xp multiplier and BEFORE the killer's tree bonus; the member's own tree XP bonus applies with
# party.combatShare.treeBonus. The killer keeps 100 % (KillSys pays them first, unchanged).
# Chat batching (PEND / WHO / LAST, add / take / send / drop / note) is the "PartyXp chat" block before SkillXp (gain4 calls it).
pxp.addField(CtField.make("public static volatile boolean FAILED_ONCE = false;", pxp))
# base x fraction, the fractional part paid by chance (1 XP x 50 % = 1 XP half of the time)
pxp.addMethod(CtNewMethod.make("""
public static long amount(long base, double fr) {
  if (base <= 0L || !(fr > 0.0)) return 0L;
  if (fr > 1.0) fr = 1.0;
  double x = (double) base * fr;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}""", pxp))
# party:fn:members as String[] (null = SkyyParty missing or no answer)
pxp.addMethod(CtNewMethod.make(f"""
public static String[] members(java.util.UUID u) {{
  try {{
    Object f = {PKG}.SkillStore.bridge().get("party:fn:members");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(u);
    if (!(r instanceof Object[])) return null;
    Object[] a = (Object[]) r;
    String[] out = new String[a.length];
    for (int i = 0; i < a.length; i++) out[i] = a[i] == null ? null : String.valueOf(a[i]);
    return out;
  }} catch (Throwable t) {{ return null; }}
}}""", pxp))
# the receiving member's class skill slot, -1 = none (SkyyClasses missing, no / unknown class, class still following a profile switch)
pxp.addMethod(CtNewMethod.make(f"""
public static int slotFor(java.util.UUID u) {{
  if ({PKG}.SkillClass.allowedFn() == null) return -1;
  if (!{PKG}.SkillClass.consistent(u)) return -1;
  return {PKG}.SkillClass.slot(u);
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static {V3D} pos({ST} s, {REF} r) {{
  try {{
    {TRC} tc = ({TRC}) s.getComponent(r, {TRC}.getComponentType());
    if (tc == null) return null;
    return tc.getPosition();
  }} catch (Throwable t) {{ return null; }}
}}""", pxp))
# leftovers: the 1 s ticker hands each due line to the member's world thread (SkillMsg.flushDue pattern)
pft.addInterface(pool.get("java.lang.Runnable"))
pft.addField(CtField.make("public java.util.UUID u;", pft))
pft.addConstructor(CtNewConstructor.make("public PartyFlushTask(java.util.UUID u) { this.u = u; }", pft))
pft.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) {{ {PKG}.PartyXp.drop(this.u); return; }}
    {PKG}.PartyXp.send(pr);
  }} catch (Throwable t) {{ }}
}}""", pft))
pxp.addMethod(CtNewMethod.make(f"""
public static void flushDue() {{
  try {{
    if (PEND.isEmpty()) return;
    long now = System.currentTimeMillis();
    java.util.Iterator it = new java.util.ArrayList(PEND.keySet()).iterator();
    while (it.hasNext()) {{
      java.util.UUID u = (java.util.UUID) it.next();
      Long last = (Long) LAST.get(u);
      if (last != null && now - last.longValue() < {PKG}.SkillCfg.FEEDBACK_MS) continue;
      {PR} pr = {UNI}.get().getPlayer(u);
      if (pr == null || !pr.isValid()) {{ drop(u); continue; }}
      {WLD} w = {UNI}.get().getWorld(pr.getWorldUuid());
      if (w == null) continue;
      LAST.put(u, Long.valueOf(now));
      try {{ w.execute(new {PKG}.PartyFlushTask(u)); }} catch (Throwable t) {{ }}
    }}
  }} catch (Throwable t) {{ }}
}}""", pxp))
# every 30 s (SkillTick): forget players who left (LAST outlives PEND)
pxp.addMethod(CtNewMethod.make(f"""
public static void retainOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr != null) online.add(pr.getUuid());
    }}
    LAST.keySet().retainAll(online);
    PEND.keySet().retainAll(online);
    WHO.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", pxp))
# one member: every rule of the header comment; returns the XP paid (0 = skipped). 0.4.14: with a mob level (ml >= 1) the member's base is
# MobXp.pay(the killer's slot, the raw kill XP, levelFactor x the gap against THIS member's class skill) - Skyy: "the party share uses each
# member's own skill"; without one (ml -1) the killer's base, exactly 0.4.13
pxp.addMethod(CtNewMethod.make(f"""
public static long one2(java.util.UUID ku, String kn, {V3D} kpos, {ST} s, String mid, long base, double fr, double r2, int ks, long raw, int ml) {{
  if (mid == null || mid.trim().length() == 0) return 0L;
  java.util.UUID mu = java.util.UUID.fromString(mid.trim());
  if (mu.equals(ku)) return 0L;
  {PR} mp = {UNI}.get().getPlayer(mu);
  if (mp == null || !mp.isValid()) return 0L;
  {REF} mr = mp.getReference();
  if (mr == null || !mr.isValid() || mr.getStore() != s) return 0L;
  {PLA} pl = ({PLA}) s.getComponent(mr, {PLA}.getComponentType());
  if (pl == null || pl.isWaitingForClientReady()) return 0L;
  if ({PKG}.SkillXp.creative(s, mr) || !{PKG}.Acro.alive(s, mr)) return 0L;
  {V3D} mpos = pos(s, mr);
  if (mpos == null) return 0L;
  double dx = mpos.x() - kpos.x();
  double dy = mpos.y() - kpos.y();
  double dz = mpos.z() - kpos.z();
  if (dx * dx + dy * dy + dz * dz > r2) return 0L;
  int slot = slotFor(mu);
  if (slot < 0) return 0L;
  long b = base;
  if (ml >= 1) b = {PKG}.MobXp.pay(ks, raw, {PKG}.MobXp.factor(ml, {PKG}.SkillStore.level(mu, slot)));   // 0.4.14
  long amt = amount(b, fr);
  if (amt <= 0L) return 0L;
  if ({PKG}.PartyCfg.TREE_BONUS) amt = {PKG}.SkillBonus.boost(mu, slot, amt);
  {PKG}.SkillXp.gain4(mp, slot, amt, false, false, kn == null ? "" : kn);
  return amt;
}}""", pxp))
# 0.4.13's one (no mob level), kept for any caller of the old signature
pxp.addMethod(CtNewMethod.make(f"""
public static long one(java.util.UUID ku, String kn, {V3D} kpos, {ST} s, String mid, long base, double fr, double r2) {{
  return one2(ku, kn, kpos, s, mid, base, fr, r2, -1, 0L, -1);
}}""", pxp))
# 0.4.14: share2 = 0.4.13's share + the mob level (ks = the killer's class slot, raw = the kill XP before the class multiplier, ml = the mob level
# or -1); members are skipped only when nothing could be shared (no level: the killer's cx is 0; with a level: the raw kill XP is 0)
pxp.addMethod(CtNewMethod.make(f"""
public static void share2({PR} kp, {REF} kr, {ST} s, long base, int ks, long raw, int ml) {{
  if (!{PKG}.PartyCfg.on() || (ml >= 1 ? raw <= 0L : base <= 0L) || kp == null || kr == null || s == null) return;
  double fr = {PKG}.PartyCfg.FRACTION;
  java.util.UUID ku = kp.getUuid();
  String[] ms = members(ku);
  if (ms == null || ms.length < 2) return;
  {V3D} kpos = pos(s, kr);
  if (kpos == null) return;
  double rad = {PKG}.PartyCfg.RADIUS;
  double r2 = rad * rad;
  String kn = null;
  try {{ kn = kp.getUsername(); }} catch (Throwable t) {{ kn = null; }}
  for (int i = 0; i < ms.length; i++) {{
    try {{
      one2(ku, kn, kpos, s, ms[i], base, fr, r2, ks, raw, ml);
    }} catch (Throwable t) {{
      if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("party combat XP share failed (logged once): " + t); }}
    }}
  }}
}}""", pxp))
# 0.4.13's share (no mob level), kept for any caller of the old signature
pxp.addMethod(CtNewMethod.make(f"""
public static void share({PR} kp, {REF} kr, {ST} s, long base) {{
  share2(kp, kr, s, base, -1, 0L, -1);
}}""", pxp))
# the class how-to line of the Stats page ("" while off or SkyyParty is not loaded)
pxp.addMethod(CtNewMethod.make(f"""
public static String howText() {{
  if (!{PKG}.PartyCfg.on()) return "";
  try {{
    if (!({PKG}.SkillStore.bridge().get("party:fn:members") instanceof java.util.function.Function)) return "";
  }} catch (Throwable t) {{ return ""; }}
  boolean lv = false;
  try {{ lv = {PKG}.MobXp.ON && ({PKG}.SkillStore.bridge().get("mob:fn:level") instanceof java.util.function.Function); }} catch (Throwable t) {{ lv = false; }}
  if (lv) return ". Party members within " + {PKG}.PartyCfg.blocks() + " blocks get " + {PKG}.PartyCfg.pct() + " of the kill XP at their own class skill level";   // 0.4.14 fix round
  return ". Party members within " + {PKG}.PartyCfg.blocks() + " blocks get " + {PKG}.PartyCfg.pct() + " of your kill XP (in their own class skill)";
}}""", pxp))

# ================= ECS systems =================
def event_system(cls, ctor_name, event_cls, body):
    cls.addConstructor(CtNewConstructor.make(f"public {ctor_name}() {{ super({event_cls}.class); }}", cls))
    cls.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return com.hypixel.hytale.component.Archetype.empty();
}}""", cls))
    cls.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
{body}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("{ctor_name} failed: " + t); }}
}}""", cls))

event_system(bsy, "BreakSys", BBE, f"""
    {BBE} e = ({BBE}) ev;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    if (e.getItemInHand() == null) {PKG}.Sickle.breakOpen(pr.getUuid(), e);   // 0.4.14: an F pickup of a loose block - its pickups are no sickle swing
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    Object fs = null;
    Object unclaimed = null;
    try {{
      if ({PKG}.FellCfg.on()) {{
        {V3I} t = e.getTargetBlock();
        if (t != null) {{
          String fwn = w.getName();
          Object[] hc = {PKG}.Fell.onBreak(fwn, pr.getUuid(), t.x(), t.y(), t.z());
          unclaimed = hc[0];
          if (!((Boolean) hc[2]).booleanValue() && {PKG}.FellCfg.worldOk(fwn) && !{PKG}.SkillXp.creative(st, r))
            fs = {PKG}.Fell.snapshot(w, pr.getUuid(), {PKG}.SkillStore.pkey(pr.getUuid()), e.getBlockType(), t.x(), t.y(), t.z(), ((Boolean) hc[1]).booleanValue());
        }}
      }}
    }} catch (Throwable ft) {{ {PKG}.Fell.failed("snapshot", ft); }}
    long[] rule = {PKG}.SkillCfg.classifyBreak(e.getBlockType());
    if (rule != null && {PKG}.SkillXp.creative(st, r)) rule = null;
    if (rule == null && !{PKG}.SkillCfg.IGNORE_PLACED && fs == null && unclaimed == null) return;
    w.execute(new {PKG}.BreakTask(e, pr.getUuid(), w.getName(), rule, fs, unclaimed));""")

event_system(psy, "PlaceSys", PBE, f"""
    if (!{PKG}.SkillCfg.IGNORE_PLACED) return;
    {PBE} e = ({PBE}) ev;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    w.execute(new {PKG}.PlaceTask(e, w.getName()));""")

# F-harvest of a ripe crop (eternal crops, berry bushes): UseBlockEvent.Post is not cancellable and is NOT proof of a harvest
# (fires before the HarvestCrop root runs, and also when it fails) -> HarvestTask verifies the block really changed.
event_system(usy, "HarvestSys", UBP, f"""
    {UBE} e = ({UBE}) ev;
    {BTY} bt = e.getBlockType();
    if (bt == null) return;
    if (!"StageFinal".equals({PKG}.SkillCfg.stateOf(bt))) return;
    {BGA} g = bt.getGathering();
    if (g == null || g.getHarvest() == null) return;
    {PKG}.Sickle.useOpen(chunk, idx, st);   // 0.4.14: an F-harvest - its pickups are no sickle swing (HarvestTask pays it)
    long[] rr = {PKG}.SkillCfg.resolve({PKG}.SkillCfg.familyId(bt));
    if (rr == null || rr[0] != (long) {PKG}.SkillDefs.FARMING || rr[1] <= 0L) return;
    long amt = {PKG}.SkillCfg.scaled(rr[1]);
    String ripe = bt.getId();
    {V3I} tb = e.getTargetBlock();
    if (amt <= 0L || ripe == null || tb == null) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null || {PKG}.SkillXp.creative(st, r)) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    String wn = w.getName();
    int bx = tb.x();
    int by = tb.y();
    int bz = tb.z();
    if (!{PKG}.HarvestGate.begin(wn, {PKG}.PlacedStore.key(bx, by, bz), System.currentTimeMillis())) return;
    {PKG}.HarvestTask ht = new {PKG}.HarvestTask(pr.getUuid(), w, wn, bx, by, bz, ripe, amt);
    ht.bt = bt;
    w.execute(ht);""")

# 0.4.14: sickle swing harvests (Tool-Levels-Spec question 3) - InteractivelyPickupItemEvent on the player (ItemUtils.interactivelyPickupItem:
# F pickups, F-harvests and sickle swings; ground pickups never fire it). Not an F pickup (BRK), not an F-harvest (USE), not creative, the main
# hand holds a sickle (farming.sickle.items) -> this tick's burst (Sickle.add); SickleTask pays it on the world thread after the dispatch.
event_system(sksy, "SickleSys", IPE, f"""
    {IPE} e = ({IPE}) ev;
    if (!{PKG}.Sickle.ON) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    if ({PKG}.Sickle.inBreak(u, System.nanoTime())) return;
    if ({PKG}.Sickle.inUse(u, System.currentTimeMillis())) return;
    if ({PKG}.SkillXp.creative(st, r)) return;
    {IS} h = {INVC}.getItemInHand(st, r);
    if (h == null || h.isEmpty() || !{PKG}.Sickle.isSickle(h.getItemId())) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    {PKG}.Sickle.add(u, e, w);""")

# 0.4.14 kill XP by mob level (world thread, KillSys): x levelFactor x the gap against the killer's class skill (before this kill) when SkyyMobs
# knows the mob's level, else EXACTLY 0.4.13 (SkillCfg.classXp); then the award and the party share (each member's own gap)
mxp.addMethod(CtNewMethod.make(J14(r"""
public static long kill(@PR@ pr, @REF@ k, @ST@ s, int slot, long base, @REF@ npc) {
  int L = levelOf(s, npc);
  long cx;
  if (ON && L >= 1) cx = pay(slot, base, factor(L, @PKG@.SkillStore.level(pr.getUuid(), slot)));
  else cx = @PKG@.SkillCfg.classXp(slot, base);
  @PKG@.SkillXp.gain(pr, slot, cx);
  @PKG@.PartyXp.share2(pr, k, s, cx, slot, base, ON ? L : -1);
  return cx;
}"""), mxp))

# Combat: DeathComponent added to an NPC killed by a player
# 0.4.10: cx = the kill XP (combat.* clamps, then the xp multiplier) x the class skill XP multiplier (SkillCfg.classXp; slot is always a
# class slot - killSlot); the party share is a fraction of this same cx, so it is multiplied exactly once
ksy.addConstructor(CtNewConstructor.make("public KillSys() { super(); }", ksy))
ksy.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return com.hypixel.hytale.component.Archetype.empty();
}}""", ksy))
ksy.addMethod(CtNewMethod.make(f"""
public void onComponentAdded({REF} r, {CMP} c, {ST} s, {CB} b) {{
  try {{
    if (r == null || !(c instanceof {DTH})) return;
    {NPC} npc = ({NPC}) s.getComponent(r, {NPC}.getComponentType());
    if (npc == null) return;
    {DMG} d = (({DTH}) c).getDeathInfo();
    if (d == null) return;
    Object src = d.getSource();
    if (!(src instanceof {DES})) return;
    {REF} k = (({DES}) src).getRef();
    if (k == null || !k.isValid() || k.getStore() != s) return;
    {PR} pr = ({PR}) s.getComponent(k, {PR}.getComponentType());
    if (pr == null || !pr.isValid()) return;
    if ({PKG}.SkillXp.creative(s, k)) return;
    int slot = {PKG}.SkillClass.killSlot(pr, b, k);
    if (slot < 0) return;
    float maxHp = -1.0f;
    try {{
      {ESM} sm = ({ESM}) s.getComponent(r, {ESM}.getComponentType());
      if (sm != null) {{ {ESV} hv = sm.get({DST}.getHealth()); if (hv != null) maxHp = hv.getMax(); }}
    }} catch (Throwable t) {{ }}
    String role = null;
    try {{ role = npc.getRoleName(); }} catch (Throwable t) {{ }}
    {PKG}.MobXp.kill(pr, k, s, slot, {PKG}.SkillCfg.combatXp(role, maxHp), r);   // 0.4.14: x the mob level bonus and the level gap (SkyyMobs)
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("kill handler failed: " + t); }}
}}""", ksy))

# ================= EnvSys (0.4.2, Tree-Fall-Spec 2.4): explosions + fire fire EnvironmentBreakBlockEvent on the ENTITY store =================
# (ExplosionUtils -> performBlockDamage with a null breaker -> performBlockBreak's else branch, before the removal; FireFluidTicker.
# applyBurnResult -> World.getEntityStore().getStore().invoke(...) right after its setBlock - both bytecode-checked). The physics cascade
# fires no event, so "an EnvironmentBreakBlockEvent named this claimed position" = an explosion or fire took it: unclaim, never pay as
# felled. A WorldEventSystem (no query), like the engine's TriggerVolumeBlockEventSystems$EnvironmentBlockBroken.
esy.addField(CtField.make("public static boolean FAILED_ONCE = false;", esy))
esy.addConstructor(CtNewConstructor.make(f"public EnvSys() {{ super({EBE}.class); }}", esy))
esy.addMethod(CtNewMethod.make(f"""
public void handle({ST} st, {CB} buf, {EV} ev) {{
  try {{
    if (!(ev instanceof {EBE})) return;
    if ({PKG}.Fell.CLAIMS.isEmpty()) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    {PKG}.Fell.envBreak(w.getName(), (({EBE}) ev).getTargetBlock());
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("EnvSys failed (logged once): " + t); }}
  }}
}}""", esy))

# ================= CraftSys (0.4): CraftRecipeEvent$Post = one finished craft unit at a vanilla crafting bench (Alchemy spec 3.1) ======
# Queued path (TimeSeconds > 0): one Post per unit but getQuantity() = the whole batch -> count 1. Instant path: quantity.
# RecipeXp.classify ignores Cookingbench / Campfire recipes (SkyyCooking owns them) and everything that is not Alchemybench / Furnace.
event_system(csy, "CraftSys", CREP, f"""
    {CRE} e = ({CRE}) ev;
    if (e.isCancelled()) return;
    {CRR} rc = e.getCraftedRecipe();
    if (rc == null) return;
    long[] rule = {PKG}.RecipeXp.classify(rc);
    if (rule == null) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null || {PKG}.SkillXp.creative(st, r)) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    int units = rc.getTimeSeconds() > 0.0f ? 1 : Math.max(1, e.getQuantity());
    if (units > 10000) units = 10000;
    java.util.UUID u = pr.getUuid();
    w.execute(new {PKG}.CraftTask(e, u, w.getName(), rc, rule, units, {PKG}.SkillStore.pkey(u)));""")

# ================= SmeltXp (0.4): helpers for the vanilla Furnace hook (Smithing-Smelting spec 3.3) =================
# MOVE_TO_SELF moves whose source is a combined container (a bench window); ListTransaction recursed
sxu.addMethod(CtNewMethod.make(f"""
public static void moves(Object tx, java.util.ArrayList out) {{
  if (tx instanceof {LTX}) {{
    java.util.List l = (({LTX}) tx).getList();
    for (int i = 0; l != null && i < l.size(); i++) moves(l.get(i), out);
    return;
  }}
  if (!(tx instanceof {MVTX})) return;
  {MVTX} mt = ({MVTX}) tx;
  if (!mt.succeeded() || mt.getMoveType() != {MVY}.MOVE_TO_SELF) return;
  if (!(mt.getOtherContainer() instanceof {CIC})) return;
  out.add(mt);
}}""", sxu))
sxu.addMethod(CtNewMethod.make(f"""
public static int qty({IS} s, String id) {{
  if (s == null || s.isEmpty() || id == null || !id.equals(s.getItemId())) return 0;
  return s.getQuantity();
}}""", sxu))
# items of `id` that landed in THIS container (a move split over hotbar + storage arrives once per container, each with the full
# remove transaction - so only the add side counts)
sxu.addMethod(CtNewMethod.make(f"""
public static int added(Object at, String id) {{
  if (at == null) return 0;
  if (at instanceof {LTX}) {{
    int n = 0;
    java.util.List l = (({LTX}) at).getList();
    for (int i = 0; l != null && i < l.size(); i++) n += added(l.get(i), id);
    return n;
  }}
  if (at instanceof {IST}) {{
    int n = 0;
    java.util.List l = (({IST}) at).getSlotTransactions();
    for (int i = 0; l != null && i < l.size(); i++) n += added(l.get(i), id);
    return n;
  }}
  if (at instanceof {SLT}) {{
    {SLT} s = ({SLT}) at;
    int d = qty(s.getSlotAfter(), id) - qty(s.getSlotBefore(), id);
    return d > 0 ? d : 0;
  }}
  return 0;
}}""", sxu))
# bench id of the player's open processing window whose container is `src`, else null
sxu.addMethod(CtNewMethod.make(f"""
public static String benchOf(java.util.List wins, Object src) {{
  for (int i = 0; wins != null && i < wins.size(); i++) {{
    Object w = wins.get(i);
    if (!(w instanceof {PBW})) continue;
    Object ic = (({PBW}) w).getItemContainer();
    if (ic != src) continue;
    {BTY} bt = (({BWN}) w).getBlockType();
    if (bt == null) return null;
    {BEN} b = bt.getBench();
    if (b == null) return null;
    return b.getId();
  }}
  return null;
}}""", sxu))
# ================= SmeltSys (0.4): InventoryChangeEvent on the player (vanilla ObjectiveInventoryChangeSystem pattern, Player query) =====
ssy.addConstructor(CtNewConstructor.make(f"public SmeltSys() {{ super({ICE}.class); }}", ssy))
ssy.addField(CtField.make("public static boolean FAILED_ONCE = false;", ssy))
ssy.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", ssy))
ssy.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
    {ICE} e = ({ICE}) ev;
    Object tx = e.getTransaction();
    if (!(tx instanceof {MVTX}) && !(tx instanceof {LTX})) return;
    if (!{PKG}.SmithCfg.ENABLED || !{PKG}.SmithCfg.VANILLA) return;
    java.util.ArrayList mv = new java.util.ArrayList();
    {PKG}.SmeltXp.moves(tx, mv);
    if (mv.isEmpty()) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (pr == null || p == null || p.getWindowManager() == null) return;
    if ({PKG}.SkillXp.creative(st, r)) return;
    java.util.List wins = p.getWindowManager().getWindows();
    long smith = 0L;
    for (int m = 0; m < mv.size(); m++) {{
      {MVTX} mt = ({MVTX}) mv.get(m);
      {CIC} src = ({CIC}) mt.getOtherContainer();
      String bench = {PKG}.SmeltXp.benchOf(wins, src);
      if (bench == null || !"Furnace".equalsIgnoreCase(bench) || src.getContainersSize() < 3) continue;
      {SLT} rt = mt.getRemoveTransaction();
      if (rt == null || src.getContainerForSlot(rt.getSlot()) != src.getContainer(2)) continue;
      {IS} before = rt.getSlotBefore();
      if (before == null || before.isEmpty()) continue;
      String id = before.getItemId();
      int got = {PKG}.SmeltXp.added(mt.getAddTransaction(), id);
      if (got <= 0) continue;
      long per = {PKG}.SmithCfg.forOutput(id);
      if (per > 0L) smith = smith + per * (long) got;
    }}
    if (smith <= 0L) return;
    if (smith > 1000000L) smith = 1000000L;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    java.util.UUID u = pr.getUuid();
    w.execute(new {PKG}.SmeltTask(u, {PKG}.SkillDefs.SMITHING, {PKG}.SkillCfg.scaled(smith), {PKG}.SkillStore.pkey(u)));
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("vanilla furnace Smithing hook failed (logged once): " + t); }}
  }}
}}""", ssy))

# ================= XbowSlotSys (0.4.5): InventorySetActiveSlotEvent on the player (Crossbow-Loaded-Spec 1.5 / 3.5, the SmeltSys pattern) =====
# Fired synchronously by ActiveSlotInventoryComponent.setActiveSlot (after the slot changed; never for a no-op switch). Hotbar only (-1).
xss.addConstructor(CtNewConstructor.make(f"public XbowSlotSys() {{ super({ISAS}.class); }}", xss))
xss.addField(CtField.make("public static boolean FAILED_ONCE = false;", xss))
xss.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", xss))
xss.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
    {ISAS} e = ({ISAS}) ev;
    if (e.getInventorySectionId() != {INVC}.HOTBAR_SECTION_ID) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    {PKG}.Xbow.onSlot(st, r, pr, pr.getUuid(), e.getPreviousSlot(), (int) e.getNewSlot());
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("crossbow hotbar hook failed (logged once): " + t); }}
  }}
}}""", xss))

# ================= trees bridge Functions (0.4, Skill-Trees-Spec 9.3 / 10): skill:fn:xp, skill:fn:drops, skill:fn:placed =================
# skill:fn:xp  apply(Object[]{UUID, String skill}) -> Long = total XP of that skill on the ACTIVE profile (SkillFn's rules: exact or
# 3+ letter prefix names, "Combat" = the current class skill; unknown -> 0). SkyyTrees computes Dust from it. Any thread.
xfn.addInterface(pool.get("java.util.function.Function"))
xfn.addConstructor(CtNewConstructor.make("public SkillXpFn() { }", xfn))
xfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    Object[] a = (Object[]) arg;
    int i = {PKG}.SkillDefs.indexOf(String.valueOf(a[1]));
    if (i < 0) return Long.valueOf(0L);
    java.util.UUID u = (java.util.UUID) a[0];
    if (i == {PKG}.SkillDefs.COMBAT) i = {PKG}.SkillClass.rowSlot(u, i);
    long x = {PKG}.SkillStore.rd({PKG}.SkillStore.data(u), i);
    return Long.valueOf(x < 0L ? 0L : x);
  }} catch (Throwable t) {{ return Long.valueOf(0L); }}
}}""", xfn))
# skill:fn:drops  apply(Object[]{BlockType, Boolean harvest}) -> java.util.List = a FRESH roll of the block's own drops, the same
# reproduction as the double drop (break: Perks.breakDrops; F-harvest: Perks.harvestDrops); null when it cannot be reproduced
# (tool-dependent drops, blocks with both Soft and Breaking drops, no harvest data). World thread (BlockHarvestUtils.getDrops).
dfn.addInterface(pool.get("java.util.function.Function"))
dfn.addConstructor(CtNewConstructor.make("public SkillDropsFn() { }", dfn))
dfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    Object[] a = (Object[]) arg;
    if (a.length < 1 || !(a[0] instanceof {BTY})) return null;
    {BTY} bt = ({BTY}) a[0];
    boolean h = a.length > 1 && Boolean.TRUE.equals(a[1]);
    if (h) return {PKG}.Perks.harvestDrops(bt);
    return {PKG}.Perks.breakDrops(bt);
  }} catch (Throwable t) {{ return null; }}
}}""", dfn))
# skill:fn:placed  apply(Object[]{String world, Integer x, Integer y, Integer z}) -> Boolean: TRUE = a player placed the block there,
# FALSE = not placed (as far as the LRU tracker knows); null = unknown (ignorePlaced=false: the tracker records nothing) - SkyyTrees
# treats anything but FALSE as placed and skips that position.
pfn.addInterface(pool.get("java.util.function.Function"))
pfn.addConstructor(CtNewConstructor.make("public SkillPlacedFn() { }", pfn))
pfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!{PKG}.SkillCfg.IGNORE_PLACED) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 4 || a[0] == null) return null;
    int x = ((Number) a[1]).intValue();
    int y = ((Number) a[2]).intValue();
    int z = ((Number) a[3]).intValue();
    return Boolean.valueOf({PKG}.PlacedStore.contains(String.valueOf(a[0]), {PKG}.PlacedStore.key(x, y, z)));
  }} catch (Throwable t) {{ return null; }}
}}""", pfn))
# ================= skill:fn:addxp (0.4): apply(Object[]{UUID, String skill, Number baseXp, String source [, String expectKey]}) -> Boolean =====
afn.addInterface(pool.get("java.util.function.Function"))
afn.addConstructor(CtNewConstructor.make("public SkillAddFn() { }", afn))
afn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || !(a[2] instanceof Number)) return Boolean.FALSE;
    int slot = {PKG}.BridgeXp.grantSlot(String.valueOf(a[1]));
    if (slot < 0) return Boolean.FALSE;
    long base = ((Number) a[2]).longValue();
    if (base <= 0L) return Boolean.FALSE;
    String src = a.length > 3 && a[3] != null ? String.valueOf(a[3]) : "?";
    String expect = a.length > 4 && a[4] instanceof String ? (String) a[4] : null;
    return {PKG}.BridgeXp.offer((java.util.UUID) a[0], slot, base, src, expect, null, 0, true) >= 0L ? Boolean.TRUE : Boolean.FALSE;
  }} catch (Throwable t) {{ return Boolean.FALSE; }}
}}""", afn))
# ================= skill:fn:healxp (0.4.4): apply(Object[]{UUID healer, Number hpHealedOnOthers, String source [, String expectKey]}) -> Boolean
# Published for SkyyClasses 0.1.6 (source "classes:heal"); HealXp.offer has every rule.
# 0.4.6 (LOCKED Skyy 2026-09-25): an OPTIONAL trailing Boolean self - apply(Object[]{UUID healer, Number hp, String source, String expectKey,
# Boolean self}); the LAST element when it is a Boolean and the array has at least 4 elements ({u, hp, src, Boolean} works too). TRUE = the
# HP was healed on the healer themself (divinity.healXpPerHpSelf, 0.25; 0.4.11: 1.25 final); absent / FALSE = on others (divinity.healXpPerHp,
# 0.2; 0.4.11: 1 final). One cap (0.4.11: 900 final a minute).
hfn.addInterface(pool.get("java.util.function.Function"))
hfn.addConstructor(CtNewConstructor.make("public SkillHealFn() { }", hfn))
hfn.addMethod(CtNewMethod.make("""
public static boolean selfArg(Object[] a) {
  if (a == null || a.length < 4) return false;
  Object o = a[a.length - 1];
  return o instanceof Boolean && ((Boolean) o).booleanValue();
}""", hfn))
hfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) arg;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof Number)) return Boolean.FALSE;
    String src = a.length > 2 && a[2] != null ? String.valueOf(a[2]) : "?";
    String expect = a.length > 3 && a[3] instanceof String ? (String) a[3] : null;
    return {PKG}.HealXp.offer((java.util.UUID) a[0], ((Number) a[1]).doubleValue(), src, expect, selfArg(a)) ? Boolean.TRUE : Boolean.FALSE;
  }} catch (Throwable t) {{ return Boolean.FALSE; }}
}}""", hfn))
# ================= skill:fn:craftxp (0.4): apply(Object[]{UUID, String recipeId, Number crafts, String source [, String expectKey]}) -> Long | null
cfn.addInterface(pool.get("java.util.function.Function"))
cfn.addConstructor(CtNewConstructor.make("public SkillCraftFn() { }", cfn))
cfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return Long.valueOf(0L);
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || a[1] == null || !(a[2] instanceof Number)) return Long.valueOf(0L);
    {CRR} rc = ({CRR}) {CRR}.getAssetMap().getAsset(String.valueOf(a[1]));
    if (rc == null) return Long.valueOf(0L);
    long[] rule = {PKG}.RecipeXp.classify(rc);
    if (rule == null) return Long.valueOf(0L);
    int crafts = ((Number) a[2]).intValue();
    if (crafts < 1) crafts = 1;
    if (crafts > 10000) crafts = 10000;
    String src = a.length > 3 && a[3] != null ? String.valueOf(a[3]) : "?";
    String expect = a.length > 4 && a[4] instanceof String ? (String) a[4] : null;
    int slot = (int) rule[0];
    long got = {PKG}.BridgeXp.offer((java.util.UUID) a[0], slot, rule[1] * (long) crafts, src, expect, slot == {PKG}.SkillDefs.ALCHEMY ? rc : null, crafts, false);
    if (got == -1L) return null;
    return Long.valueOf(got < 0L ? 0L : got);
  }} catch (Throwable t) {{ return Long.valueOf(0L); }}
}}""", cfn))

# ================= leaderboard =================
tcm.addInterface(pool.get("java.util.Comparator"))
tcm.addConstructor(CtNewConstructor.make("public TopCmp() { }", tcm))
tcm.addMethod(CtNewMethod.make("""
public int compare(Object a, Object b) {
  long x = ((Long) ((Object[]) a)[1]).longValue();
  long y = ((Long) ((Object[]) b)[1]).longValue();
  if (x != y) return x > y ? -1 : 1;
  return String.valueOf(((Object[]) a)[0]).compareToIgnoreCase(String.valueOf(((Object[]) b)[0]));
}""", tcm))
top.addField(CtField.make("public static final long[] AT = new long[%d];" % len(SLOT_NAMES), top))   # = SkillDefs.N
top.addField(CtField.make("public static final Object[] CACHE = new Object[%d];" % len(SLOT_NAMES), top))
# 0.3.2: a row per profile file / profile key; profile N >= 2 ("<uuid>-pN") shows "name (profile N)" (a UUID string never contains "-p")
top.addMethod(CtNewMethod.make("""
public static String label(String nm, String key) {
  if (key == null) return nm;
  int p = key.indexOf("-p");
  if (p <= 0 || p + 2 >= key.length()) return nm;
  return nm + " (profile " + key.substring(p + 2) + ")";
}""", top))
# rows: Object[]{name, Long xp, profile key (0.3.2; = uuidString for profile 1)}, sorted, all profiles on disk + in memory; cached 30s
top.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.ArrayList all(int skill) {{
  long now = System.currentTimeMillis();
  if (CACHE[skill] != null && now - AT[skill] < 30000L) return (java.util.ArrayList) CACHE[skill];
  java.util.HashMap m = new java.util.HashMap();
  try {{
    java.io.File[] fs = {PKG}.SkillStore.DIR.toFile().listFiles();
    if (fs != null) for (int i = 0; i < fs.length; i++) {{
      String fn = fs[i].getName();
      if (!fn.endsWith(".properties")) continue;
      String us = fn.substring(0, fn.length() - 11);
      try {{
        java.util.Properties p = {PKG}.SkillStore.readLocked(fs[i].toPath());
        long x = 0L;
        try {{ x = Long.parseLong(String.valueOf(p.getProperty({PKG}.SkillDefs.NAMES[skill], "0")).trim()); }} catch (Throwable t) {{ }}
        String nm = p.getProperty("name");
        m.put(us, new Object[] {{ label(nm == null ? us.substring(0, 8) : nm, us), Long.valueOf(x), us }});
      }} catch (Throwable t) {{ }}
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("leaderboard scan failed: " + t); }}
  java.util.Iterator it = {PKG}.SkillStore.DATA.entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String k = (String) e.getKey();
    long[] d = (long[]) e.getValue();
    Object ou = {PKG}.SkillStore.OWNER.get(k);
    String nm = ou == null ? null : (String) {PKG}.SkillStore.NAMES.get(ou);
    m.put(k, new Object[] {{ label(nm == null ? (k.length() > 8 ? k.substring(0, 8) : k) : nm, k), Long.valueOf(d[skill]), k }});
  }}
  java.util.ArrayList rows = new java.util.ArrayList(m.values());
  java.util.Collections.sort(rows, new {PKG}.TopCmp());
  CACHE[skill] = rows; AT[skill] = now;
  return rows;
}}""", top))
top.addMethod(CtNewMethod.make(f"""
public static int rankOf(java.util.ArrayList rows, java.util.UUID u) {{
  String s = {PKG}.SkillStore.pkey(u);
  for (int i = 0; i < rows.size(); i++) if (s.equals(((Object[]) rows.get(i))[2])) return i + 1;
  return 0;
}}""", top))

# ================= /skills page (inline, TextButtons; syntax copied from AccPage / SacksPage) =================
# ================= SKILLS PAGES LOOK (0.4.7): the vanilla UI kit tools/skyyui.py, called when THIS script runs =================
# research/Vanilla-UI-Style-Guide.md sections 7, 8c, 12 and 13 (the LIST page recipe). The sk_* / st_* / ov_* functions build the markup
# of /skills (+ its Top 10 view), the Stats page and the Overall page from kit calls; the Java the kit emits gets a name (SK_*_JAVA,
# ST_*_JAVA, OV_*_JAVA) and is interpolated into the three build() f-strings below as {..._JAVA}: interpolated text is never re-parsed
# by Python, so the kit's Java string literals reach javassist exactly as the kit wrote them (no brace doubling, no escaping).
# Proven properties only (LayoutMode Left / Top, fixed widths / heights, Anchor margins, Padding, colour backgrounds, the kit's
# textures and sounds, Wrap): no FlexWeight, no LayoutMode Center / Right / Full, no WrapMaxLines / LetterSpacing, nothing UNVERIFIED
# (SUI.assert_proven on every sample state below). Every page body is filled exactly: each part has a fixed height, a spacer stands in
# for a part that is off (no note, no next level, no Tree), so nothing moves between states.
# ---- SKILLS PAGE BLOCK START (SkyySkills/test_skyyskills_0.4.7.py builds every page state with the 0.4.6 and 0.4.7 jars)
UI_PAGE_COLORS = _B5C + CLASS_ROWS + EXTRA_ROWS   # the 16 skill / class colours (= SkillDefs.COLORS): the ONLY data colours a page may
#   show (the skill name + the XP bar); SkyySkills/test_skyyskills_0.4.7.py allows exactly these (+ kit colours) in page markup
UI_CHAT_COLORS = ["#ffb080", "#ffe08a", "#9fd8ff", "#a8e8c0", "#b8f0a0", "#ffc800", "#c8b070", "#a0f0e0", "#9fe0a0"]   # chat lines only
#   (Message.color) - never on a page; listed so the kit lint (tools/ci/lint.py) knows them
UI_DATA_COLORS = UI_PAGE_COLORS + UI_CHAT_COLORS   # what tools/ci/lint.py reads (page + chat data colours)
assert sorted(_B5C + [_x[3] for _x in CLASS_ROWS + EXTRA_ROWS]) == sorted(SLOT_COLORS), "UI_PAGE_COLORS != SkillDefs.COLORS"
assert not set(c.lower() for c in UI_CHAT_COLORS) & set(c.lower() for c in SLOT_COLORS), "a chat colour is also a skill colour"
_SK_LF = chr(10)
_SK_COL = SLOT_COLORS[0]              # the colour sample of a runtime skill colour (SkillDefs.COLORS[sl]): Mining
# ---- sizes (every page 960 wide; the plain window: 38 px title bar + padding 17)
SK_W = 960
SK_IN_W = SK_W - 2 * SUI.CONTENT_PAD                                   # 926: the body's inner width
SK_LIST_IN = SK_IN_W - 2 * SUI.WELL_LIST_PAD                           # 918: a row inside a list well
SK_ACT_W = SUI.ROW_ACTION_W                                            # 92: TREE / STATS (WorldEventListRow #ActionA, small Secondary)
SK_ACT = 4 + SK_ACT_W                                                  # an action + its 4 px gap
SK_ROW_PAD, SK_ICON, SK_ICON_BOX = 8, 40, 52                           # static_row's geometry: padding 8, a 40 px icon in a 52 px box
SK_NAME_H, SK_PROG_H = SUI.fs(14) + 6, SUI.fs(12) + 5                  # 24 + 20: the kit's row text heights (18 px bold, 15 px)
SK_XP_H, SK_XP_M = 10, 2                                               # the XP bar (10 px as in 0.4.6) and its 2 px margins
SK_TEXT_H = SK_NAME_H + SK_XP_M + SK_XP_H + SK_XP_M + SK_PROG_H        # 58
SK_TEXT_TOP = 2
SK_ROW_H = SK_TEXT_H + 2 * SK_TEXT_TOP                                 # 62: a skill row
SK_ACRO_H = SK_ROW_H + SK_PROG_H                                       # 82: the Acrobatics row (+ its bonus line)
SK_PANEL_W = {True: SK_LIST_IN - 2 * SK_ACT, False: SK_LIST_IN - SK_ACT}   # the row panel: 726 with the TREE column, 822 without
SK_TEXT_W = dict((k, v - 2 * SK_ROW_PAD - SK_ICON_BOX) for k, v in SK_PANEL_W.items())   # 658 / 754
SK_XP_W = dict((k, v - 8) for k, v in SK_TEXT_W.items())                # 650 / 746: the XP bar (fill maths: bw)
SK_ROW_SLOTS = SKILL_ROW_SLOTS                                         # = SkillDefs.ROW_SLOTS (formatted from the same list): 9 rows
assert SK_ROW_SLOTS.count(ACRO_SLOT) == 1, "the list well budgets exactly ONE 82 px Acrobatics row (SK_ACRO_H)"
SK_LIST_H = 2 * SUI.WELL_LIST_PAD + sum((SK_ACRO_H if sl == ACRO_SLOT else SK_ROW_H) + SUI.ROW_GAP for sl in SK_ROW_SLOTS)   # 613: one
#   slot of each row's height (+ its gap) per SkillDefs.ROW_SLOTS entry - SkillsPage.build() gives the Acrobatics row 82 px, the rest 62
SK_OV_H, SK_OV_M = SUI.BTN_H + 2 * SUI.WELL_PAD, 8                     # the Overall well (60) + 8 under it
SK_OV_LABEL_W = SK_IN_W - 2 * SUI.WELL_PAD - SUI.BTN_MIN_W - 8          # 730
SK_HINT_H, SK_HINT_M = SUI.fs(12) + 10, 8                              # the caption line under the list
SK_BODY_H = SK_OV_H + SK_OV_M + SK_LIST_H + SK_HINT_M + SK_HINT_H       # 714
SK_H = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + SK_BODY_H                    # 786
SK_HINT = "Gather - brew - smelt - cook - fight - move - explore.  Stats shows every boost - level ups pay coins"
# Top 10 view (the same window): column heads + a list well of table rows + the rank line + the footer
SK_TOP_HEAD_H, SK_TOP_ROW_H = 30, 55
SK_RANK_H, SK_RANK_M = 30, 8
SK_FOOT_H = SUI.BTN_H + 8                                              # a button row: 44 + its top 8
SK_TOP_LIST_H = SK_BODY_H - SK_TOP_HEAD_H - (SK_RANK_M + SK_RANK_H) - SK_FOOT_H   # 594: the well takes the rest
SK_TOP_SPEC = SUI.column_spec([("Rank", 100), ("Player", 444), ("Level", 150), ("XP", 200)], avail=SK_LIST_IN, pad_left=12)
# Stats page: fixed slots (title, XP line, bar, note, now / next wells of 7 lines, how-to, footer)
ST_TITLE_H, ST_SUB_H = 42, 28                                          # the 32 px display line, the 16 px XP line
SK_BIG_BAR_W, ST_BAR_M = 600, 6                                        # the 600 px bar (= STBARW / OVBARW, asserted there; 18 high) + margins
ST_NOTE_H, ST_SEP_H = 28, 1 + 2 * SUI.SEP_MARGIN                        # the note slot, a content separator (17)
ST_HEAD_H, ST_HEAD_B, ST_HEAD_T = SUI.fs(14) + 10, 4, 10               # an uppercase section head (28) + 4 under it (+ 10 over the 2nd)
ST_LINE_H, ST_LINES = 28, 7                                            # a boost line (18 px) and at most 7 per list (0.4.6)
ST_LINE_MIN = SUI.fs(12)                                               # 15: a boost line longer than its well shrinks to this floor
ST_BOX_H = ST_LINES * ST_LINE_H + 2 * SUI.WELL_PAD                      # 212: one list well
ST_HOW_H = 64                                                          # the how-to caption: 3 lines of 15 px (1.364 em)
STATS_W = SK_W
ST_BODY = (ST_TITLE_H + ST_SUB_H + (18 + 2 * ST_BAR_M) + ST_NOTE_H + ST_SEP_H + (ST_HEAD_H + ST_HEAD_B) + ST_BOX_H
           + (ST_HEAD_T + ST_HEAD_H + ST_HEAD_B) + ST_BOX_H + ST_SEP_H + ST_HOW_H + SK_FOOT_H)                 # 776
STATS_H = SUI.TITLE_H + 2 * SUI.CONTENT_PAD + ST_BODY                   # 848
ST_NAV_GAP = {True: SK_IN_W - (3 * SUI.BTN_MIN_W + 2 * 6), False: SK_IN_W - (2 * SUI.BTN_MIN_W + 6)}   # the footer's left padding
# Overall page: the same slots with 3 / 2 lines and the wrapped list of counted skills
OV_LIST_H = 76                                                         # the counted skills: up to 3 wrapped 18 px lines
OV_NOW_N, OV_NEXT_N = 3, 2                                             # 0.4.6: at most 3 boost lines, 2 next-level lines
OV_HOW_H = 44                                                          # the how-to caption: 2 lines of 15 px
OV_BODY = (ST_TITLE_H + ST_SUB_H + (18 + 2 * ST_BAR_M) + ST_SEP_H + (ST_HEAD_H + ST_HEAD_B) + (OV_LIST_H + 2 * SUI.WELL_PAD)
           + ST_SEP_H + (ST_HEAD_H + ST_HEAD_B) + (OV_NOW_N * ST_LINE_H + 2 * SUI.WELL_PAD)
           + (ST_HEAD_T + ST_HEAD_H + ST_HEAD_B) + (OV_NEXT_N * ST_LINE_H + 2 * SUI.WELL_PAD) + ST_SEP_H + OV_HOW_H + SK_FOOT_H)   # 617
OV_W, OV_H = SK_W, SUI.TITLE_H + 2 * SUI.CONTENT_PAD + OV_BODY          # 960 x 689
OV_HOW = ("The Overall Level is the average of the skills above, rounded down - level any of them to raise it. Other classes' skills "
          "never count (a new class is a new profile).")
assert (SK_H, STATS_H, OV_H) == (786, 848, 689) and SK_LIST_H == 613 and SK_TOP_LIST_H == 594, (SK_H, STATS_H, OV_H, SK_LIST_H, SK_TOP_LIST_H)
assert SK_TEXT_W == {True: 658, False: 754}, SK_TEXT_W
assert SK_TOP_LIST_H >= SUI.list_well_h(10, SK_TOP_ROW_H), "the Top 10 well holds its 10 rows"
assert SK_ACT_W - 2 * SUI.BTN_SMALL_PAD >= SUI.text_width("Stats", 14, True, upper=True), "STATS fits the small row action"


def sk_shell():
    """/skills (both views): the plain window SkyySkF (960 x 786); 0.4.6's root #SkyySkills is the body. The title is set at runtime:
    SKILLS on the overview, TOP 10 - <SKILL> on the leaderboard view (0.4.6's two title labels)."""
    title = SUI.J('this.view < 0 || this.view >= ' + PKG + '.SkillDefs.N ? "Skills" : "Top 10 - " + ' + PKG + '.SkillDefs.LABELS[this.view]',
                  "Skills")
    return SUI.page_shell("SkyySkF", SK_W, SK_H, title, kind="plain", body_id="SkyySkills")


def sk_overview(ap, body):
    """The overview's static parts: the Overall well (#SkyySkOvRow: #SkyySkOv + the OVERALL button #SkyySkOvStat), the list well
    #SkyySkList (the rows go in there) and the hint caption. #SkyySkOv's text is b.set by the kept 0.4.6 line."""
    ap.add(body, SUI.panel("SkyySkOvRow", "well", h=SK_OV_H, layout="Left", anchor={"bottom": SK_OV_M}))
    ap.add("SkyySkOvRow", SUI.label("SkyySkOv", "", "rowName", w=SK_OV_LABEL_W, h=SUI.BTN_H))
    ap.add("SkyySkOvRow", SUI.button("SkyySkOvStat", "Overall", "secondary", anchor={"left": 8}))
    ap.add(body, SUI.list_well("SkyySkList", w=SK_IN_W, h=SK_LIST_H))
    ap.text(body, "SkyySkHint", SK_HINT, "caption", h=SK_HINT_H, align="Center", anchor={"top": SK_HINT_M})


def sk_row(i, rh, pw, tw, bw, fill, col, icon, title, prog):
    """One skill row #SkyySkRow<i> in #SkyySkList (i = an id suffix: SUI.J("i") in the build, digits in the checks): the vanilla row
    panel #SkyySkRow<i>P (static_row's geometry: padding 8, the 40 px item icon #SkyySkRow<i>Ic in a 52 px box), the text column
    #SkyySkTxt<i> (0.4.6's id) with the name #SkyySkRow<i>Nm (18 px bold, the skill colour), the XP bar #SkyySkBar<i> (0.4.6's id;
    the vanilla track, the fill in the skill colour, no fill Group at 0) and the progress line #SkyySkRow<i>Pg (15 px). The row
    actions come after (sk_tree / sk_tree_gap / sk_stat). Texts: title / prog = b.set values."""
    ap = SUI.Appends()
    r, t = "SkyySkRow" + i, "SkyySkTxt" + i
    ap.add("SkyySkList", SUI.group(r, "Left", h=rh, anchor={"bottom": SUI.ROW_GAP}))
    ap.add(r, SUI.panel(r + "P", "row", w=pw, h=rh, layout="Left", pad={"left": SK_ROW_PAD, "right": SK_ROW_PAD}))
    ap.add(r + "P", SUI.group(r + "Ib", None, w=SK_ICON_BOX, h=rh))
    top = SUI.J("(rh - %d) / 2" % SK_ICON, str((SK_ROW_H - SK_ICON) // 2)) if SUI.has_j(rh) else (rh - SK_ICON) // 2
    ap.add(r + "Ib", SUI.item_icon(r + "Ic", icon, SK_ICON, anchor={"left": 0, "top": top}))
    ap.add(r + "P", SUI.group(t, "Top", w=tw, h=rh, pad={"top": SK_TEXT_TOP}))
    ap.text(t, r + "Nm", title, "rowName", h=SK_NAME_H, col=col)
    bar = SUI.stat_bar("SkyySkBar" + i, bw, SK_XP_H, fill, col=col, anchor={"top": SK_XP_M, "bottom": SK_XP_M})
    ap.add(t, bar.choose() if SUI.has_j(fill) else bar.pick())
    ap.text(t, r + "Pg", prog, "rowSub", h=SK_PROG_H)
    return ap


def sk_bonus(i):
    """The Acrobatics row's bonus line #SkyySkBonus (0.4.6's id; info blue, 15 px) under the progress line; its text is b.set by the
    kept 0.4.6 line (Acro.bonusText)."""
    return SUI.Appends([("SkyySkTxt" + i, SUI.label("SkyySkBonus", "", "rowSub", h=SK_PROG_H, col="info"))])


def sk_tree(i, rh):
    return SUI.Appends([("SkyySkRow" + i, SUI.row_action("SkyySkTree" + i, "Tree", w=SK_ACT_W, h=rh))])


def sk_tree_gap(i, rh):
    """SkyyTrees runs but has no tree for this skill: a blank as wide as TREE, so STATS lines up (0.4.6: an empty 70 px label)."""
    return SUI.Appends([("SkyySkRow" + i, SUI.group(None, None, w=SK_ACT_W, h=rh, anchor={"left": 4}))])


def sk_stat(i, rh):
    return SUI.Appends([("SkyySkRow" + i, SUI.row_action("SkyySkStat" + i, "Stats", w=SK_ACT_W, h=rh))])


def sk_top(ap, body):
    """The Top 10 view's static parts: RANK / PLAYER / LEVEL / XP heads (vanilla section labels over the columns) and the list
    well #SkyySkTop."""
    ap.add(body, SK_TOP_SPEC.heads("SkyySkTopHead", outside=SUI.WELL_LIST_PAD))
    ap.add(body, SUI.list_well("SkyySkTop", w=SK_IN_W, h=SK_TOP_LIST_H))


def sk_top_row(i, me, cells):
    """One leaderboard row #SkyySkTopRow<i> (a vanilla table row, cells C0-C3 under the heads; texts b.set); your own row (me) in
    white bold: a J("me") picks it at runtime (both looks create the same ids and set the same texts)."""
    mine = SK_TOP_SPEC.row("SkyySkTopRow" + i, cells, h=SK_TOP_ROW_H, kinds="strong")
    other = SK_TOP_SPEC.row("SkyySkTopRow" + i, cells, h=SK_TOP_ROW_H, kinds="default")
    if SUI.has_j(me):
        return SUI.choose(me, mine, other)
    return mine if me else other


def sk_top_empty():
    ap = SUI.Appends()
    ap.text("SkyySkTop", "SkyySkTopNone", "Nobody has any XP yet.", "caption", h=30, anchor={"left": 8})
    return ap


def sk_top_foot(ap, body, rank_text):
    """The rank line #SkyySkRank (b.set) and the footer #SkyySkNav (0.4.6's id) with BACK #SkyySkBack right-aligned."""
    ap.text(body, "SkyySkRank", rank_text, "default", h=SK_RANK_H, align="Center", anchor={"top": SK_RANK_M})
    ap.add(body, SUI.button_row("SkyySkNav", align="right", used=SUI.BTN_MIN_W, avail=SK_IN_W))
    ap.add("SkyySkNav", SUI.button("SkyySkBack", "Back", "secondary", sound="cancel"))


def _sk_head(ap, parent, ident, text, top=0, col=None):
    """An uppercase section head over a well (18 px bold #96a9be: the settingHead kind; KIT-GAP 3)."""
    anc = {"bottom": ST_HEAD_B}
    if top:
        anc["top"] = top
    kw = {"h": ST_HEAD_H, "anchor": anc}
    if col is not None:
        kw["col"] = col
    if text:
        ap.text(parent, ident, text, "settingHead", **kw)
    else:
        ap.add(parent, SUI.label(ident, "", "settingHead", **kw))


def _sk_bar_row(ap, parent, row_id, bar_id, fill, col=None):
    """A centred 600 px bar (STBARW / OVBARW) on the vanilla track: row #row_id (LayoutMode Left, Padding Left centres it) + the
    stat_bar #bar_id (no fill Group at 0)."""
    ap.add(parent, SUI.group(row_id, "Left", h=18, anchor={"top": ST_BAR_M, "bottom": ST_BAR_M},
                             pad={"left": SUI.centre_margin(SK_IN_W, SK_BIG_BAR_W)}))
    kw = {"col": col} if col is not None else {}
    bar = SUI.stat_bar(bar_id, SK_BIG_BAR_W, 18, fill, **kw)
    ap.add(row_id, bar.choose() if SUI.has_j(fill) else bar.pick())


def st_shell(name):
    """The Stats page: the plain window SkyyStF (960 x 848), the title bar = the skill name; 0.4.6's root #SkyySkStats is the body."""
    return SUI.page_shell("SkyyStF", STATS_W, STATS_H, name, kind="plain", body_id="SkyySkStats")


def st_top(ap, body):
    """#SkyyStTitle (32 px in the skill colour), #SkyyStSub (the XP line) and the bar row #SkyyStBarRow - texts b.set by kept lines."""
    ap.add(body, SUI.label("SkyyStTitle", "", "display", h=ST_TITLE_H, align="Center", col=SUI.J("col", _SK_COL)))
    ap.add(body, SUI.label("SkyyStSub", "", "default", h=ST_SUB_H, align="Center"))
    ap.add(body, SUI.group("SkyyStBarRow", "Left", h=18, anchor={"top": ST_BAR_M, "bottom": ST_BAR_M},
                           pad={"left": SUI.centre_margin(SK_IN_W, SK_BIG_BAR_W)}))


def st_bar(fill):
    """The 600 px XP bar #SkyyStBar in #SkyyStBarRow (the vanilla track, the fill in the skill colour; no fill Group at 0)."""
    bar = SUI.stat_bar("SkyyStBar", SK_BIG_BAR_W, 18, fill, col=SUI.J("col", _SK_COL))
    return SUI.Appends([("SkyyStBarRow", bar.choose() if SUI.has_j(fill) else bar.pick())])


def st_note():
    """#SkyyStNote: 'You are not a Mage right now - ...' (bold, the vanilla warning yellow, centred); b.set by the kept expression."""
    return SUI.Appends([("SkyySkStats", SUI.label("SkyyStNote", "", "bold", h=ST_NOTE_H, align="Center", col="warning"))])


def st_note_gap():
    return SUI.Appends([("SkyySkStats", SUI.spacer(h=ST_NOTE_H))])


def st_mid(ap, body):
    """The separator, the BOOSTS RIGHT NOW head #SkyyStNowHd and its well #SkyyStNowBox."""
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    _sk_head(ap, body, "SkyyStNowHd", "")
    ap.add(body, SUI.panel("SkyyStNowBox", "well", h=ST_BOX_H))


def st_line(parent, ident, text, col):
    """One boost line (18 px, the setting kind) in a well: the text b.set. The vanilla ShrinkTextToFit with a 15 px floor (vanilla
    plain labels do it on PlaySoundPage / ParticleSpawnPage / PortalDeviceSummon #Title0): a line longer than the well (the
    Acrobatics "Skill tree:" line with every node, a long SkyyCooking / SkyyExploration hook line) shrinks instead of running past
    the well edge; a line that fits is drawn exactly as before. KIT-GAP 4: label() has no shrink= option, so the kind's own style
    (the kit's text_style with the setting kind's values) is swapped for the kit's text_style(..., shrink=ST_LINE_MIN), asserted once."""
    ap = SUI.Appends()
    ap.text(parent, ident, text, "setting", h=ST_LINE_H, col=col)
    par, mk = ap[-1]
    vs, _kc, kb, ku, ka, kw, ki, _where = SUI.LABELS["setting"]
    plain = "Style: %s; " % SUI.text_style(SUI.fs(vs), col, bold=kb, upper=ku, italic=ki, halign=ka, valign="Center", wrap=kw)
    shrunk = "Style: %s; " % SUI.text_style(SUI.fs(vs), col, bold=kb, upper=ku, italic=ki, halign=ka, valign="Center", wrap=kw,
                                            shrink=ST_LINE_MIN)
    assert isinstance(mk, str) and mk.count(plain) == 1 and "ShrinkTextToFit" in shrunk, (plain, mk)
    ap[-1] = (par, mk.replace(plain, shrunk))
    return ap


def st_next_head(ap, body, text="", col=None):
    """The LEVEL n+1 ADDS head #SkyyStNextHd (10 px over it)."""
    _sk_head(ap, body, "SkyyStNextHd", text, top=ST_HEAD_T, col=col)


def st_how(ap, body, text):
    """The separator and the how-to caption #SkyyStHow (wraps; b.set)."""
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    ap.text(body, "SkyyStHow", text, "caption", h=ST_HOW_H, wrap=True)


def st_nav(ap, body, gap):
    """The footer #SkyyStNav right-aligned (its left padding = the room the buttons leave: gap = an int or J()) with < BACK and TOP 10;
    SKILL TREE is appended by st_tree when that skill has a tree."""
    ap.add(body, SUI.button_row("SkyyStNav", align="right", left_margin=gap))
    ap.add("SkyyStNav", SUI.button("SkyyStBack", "< Back", "secondary", sound="cancel"))
    ap.add("SkyyStNav", SUI.button("SkyyStTop", "Top 10", "secondary", anchor={"left": 6}))


def st_tree():
    return SUI.Appends([("SkyyStNav", SUI.button("SkyyStTree", "Skill tree", "secondary", anchor={"left": 6}))])


def ov_shell():
    """The Overall page: the plain window, 0.4.6's ids kept for every frame part (root #SkyyOvPage, title bar #SkyyOvHead, title
    #SkyyOvHeadTxt, body #SkyyOvBody)."""
    return SUI.page_shell("SkyyOvF", OV_W, OV_H, "Overall Level", kind="plain", root_id="SkyyOvPage", bar_id="SkyyOvHead",
                          title_id="SkyyOvHeadTxt", body_id="SkyyOvBody")


def ov_top(ap, body, title, sub, fill, count_text, list_text):
    """Level line, average line, the bar, the SKILLS THAT COUNT head + the counted skills in a well."""
    ap.text(body, "SkyyOvTitle", title, "display", h=ST_TITLE_H, align="Center")
    ap.text(body, "SkyyOvSub", sub, "default", h=ST_SUB_H, align="Center")
    _sk_bar_row(ap, body, "SkyyOvBarRow", "SkyyOvBar", fill)
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    _sk_head(ap, body, "SkyyOvSkHd", count_text)
    ap.add(body, SUI.panel("SkyyOvSkBox", "well", h=OV_LIST_H + 2 * SUI.WELL_PAD))
    ap.text("SkyyOvSkBox", "SkyyOvSk", list_text, "setting", h=OV_LIST_H, col="white", wrap=True)
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    _sk_head(ap, body, "SkyyOvNowHd", "Boosts right now")
    ap.add(body, SUI.panel("SkyyOvNowBox", "well", h=OV_NOW_N * ST_LINE_H + 2 * SUI.WELL_PAD))


def ov_next(ap, body, text, col=None, box=True):
    """The OVERALL LEVEL n+1 ADDS head #SkyyOvNextHd and its well #SkyyOvNextBox (box=False: a spacer of its height - max level)."""
    _sk_head(ap, body, "SkyyOvNextHd", text, top=ST_HEAD_T, col=col)
    h = OV_NEXT_N * ST_LINE_H + 2 * SUI.WELL_PAD
    ap.add(body, SUI.panel("SkyyOvNextBox", "well", h=h) if box else SUI.spacer(h=h))


def ov_foot(ap, body):
    ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN}))
    ap.text(body, "SkyyOvHow", OV_HOW, "caption", h=OV_HOW_H, wrap=True)
    ap.add(body, SUI.button_row("SkyyOvNav", align="right", used=SUI.BTN_MIN_W, avail=SK_IN_W))
    ap.add("SkyyOvNav", SUI.button("SkyyOvBack", "Back", "secondary", sound="cancel"))


def _sk_java(ap, prefix, indent, known=()):
    """The Java statements of one Appends (appends, then its b.set lines), checked first, indented for a build() source."""
    SUI.check_page(ap, prefix, known_parents=[SUI.render(k) for k in known])
    SUI.assert_proven(ap)
    return _SK_LF.join(indent + ln for ln in ap.java("b").split(_SK_LF))


def _sk_shell_java(sh, prefix, indent):
    SUI.check_page(sh.appends, prefix)
    SUI.assert_proven(sh)
    return _SK_LF.join(indent + ln for ln in sh.java("b").split(_SK_LF))


# ---- the Java pieces (J() = a local of the build() below; samples = what the checks read)
_I = SUI.J("i", "0")
_RH = SUI.J("rh", str(SK_ROW_H))
SK_SH = sk_shell()
SK_SHELL_JAVA = _sk_shell_java(SK_SH, "SkyySk", "  ")
_ap = SUI.Appends()
sk_overview(_ap, "SkyySkills")
SK_OVERVIEW_JAVA = _sk_java(_ap, "SkyySk", "    ", known=["SkyySkills"])
SK_ROW_JAVA = _sk_java(sk_row(_I, _RH, SUI.J("pw", str(SK_PANEL_W[True])), SUI.J("tw", str(SK_TEXT_W[True])),
                              SUI.J("bw", str(SK_XP_W[True])), SUI.J("fill", "320"), SUI.J("col", _SK_COL),
                              SUI.J(PKG + ".SkillDefs.ICONS[sl]", "Tool_Pickaxe_Iron"), SUI.J("title", "Mining  12"),
                              SUI.J("prog", "1234 / 5000 XP to level 13")), "SkyySk", "      ", known=["SkyySkList"])
SK_BONUS_JAVA = _sk_java(sk_bonus(_I), "SkyySk", "        ", known=["SkyySkTxt" + _I])
SK_TREE_JAVA = _sk_java(sk_tree(_I, _RH), "SkyySk", "          ", known=["SkyySkRow" + _I])
SK_TREE_GAP_JAVA = _sk_java(sk_tree_gap(_I, _RH), "SkyySk", "          ", known=["SkyySkRow" + _I])
SK_STAT_JAVA = _sk_java(sk_stat(_I, _RH), "SkyySk", "      ", known=["SkyySkRow" + _I])
_ap = SUI.Appends()
sk_top(_ap, "SkyySkills")
SK_TOP_JAVA = _sk_java(_ap, "SkyySk", "  ", known=["SkyySkills"])
SK_TOP_EMPTY_JAVA = _sk_java(sk_top_empty(), "SkyySk", "    ", known=["SkyySkTop"])
_row = sk_top_row(_I, SUI.J("me"), [SUI.J('(i + 1) + "."', "1."), SUI.J("e[0]", "Skyy"),
                                     SUI.J('"Level " + ' + PKG + '.SkillDefs.levelOf(s, x)', "Level 12"),
                                     SUI.J(PKG + '.SkillDefs.fmt(x) + " XP"', "12.3k XP")])
_ap = SUI.Appends()
_ap.add("SkyySkTop", _row)
SK_TOP_ROW_JAVA = _sk_java(_ap, "SkyySk", "    ", known=["SkyySkTop"])
_ap = SUI.Appends()
sk_top_foot(_ap, "SkyySkills", SUI.J('rank > 0 ? "Your rank #" + rank + " of " + rows.size() + " - level " + ' + PKG
                                     + '.SkillDefs.levelOf(s, d[s]) + " - " + ' + PKG + '.SkillDefs.fmt(d[s]) + " XP" : "You are not ranked yet"',
                                     "Your rank #1 of 3 - level 12 - 12.3k XP"))
SK_TOP_FOOT_JAVA = _sk_java(_ap, "SkyySk", "  ", known=["SkyySkills"])
ST_SH = st_shell(SUI.J("name", "Mining"))
ST_SHELL_JAVA = _sk_shell_java(ST_SH, "SkyyS", "  ")
_ap = SUI.Appends()
st_top(_ap, "SkyySkStats")
ST_TOP_JAVA = _sk_java(_ap, "SkyyS", "  ", known=["SkyySkStats"])
ST_BAR_JAVA = _sk_java(st_bar(SUI.J("fill", "300")), "SkyyS", "  ", known=["SkyyStBarRow"])
ST_NOTE_JAVA = _sk_java(st_note(), "SkyyS", "    ", known=["SkyySkStats"])
ST_NOTE_GAP_JAVA = _sk_java(st_note_gap(), "SkyyS", "    ", known=["SkyySkStats"])
_ap = SUI.Appends()
st_mid(_ap, "SkyySkStats")
ST_MID_JAVA = _sk_java(_ap, "SkyyS", "  ", known=["SkyySkStats"])
ST_NOW_JAVA = _sk_java(st_line("SkyyStNowBox", "SkyyStNow" + _I, SUI.J("(String) now.get(i)", "+5 max Health"), "white"), "SkyyS",
                       "    ", known=["SkyyStNowBox"])
_ap = SUI.Appends()
st_next_head(_ap, "SkyySkStats")
_ap.add("SkyySkStats", SUI.panel("SkyyStNextBox", "well", h=ST_BOX_H))
ST_NEXT_HD_JAVA = _sk_java(_ap, "SkyyS", "      ", known=["SkyySkStats"])
ST_NEXT_JAVA = _sk_java(st_line("SkyyStNextBox", "SkyyStNext" + _I, SUI.J("(String) nx.get(i)", "+0.1 max Health"), "buttonText"),
                        "SkyyS", "        ", known=["SkyyStNextBox"])
_ap = SUI.Appends()
st_next_head(_ap, "SkyySkStats", "Max level reached - nothing more to unlock", col="gold")
_ap.add("SkyySkStats", SUI.spacer(h=ST_BOX_H))
ST_MAX_JAVA = _sk_java(_ap, "SkyyS", "      ", known=["SkyySkStats"])
ST_LEGACY_GAP_JAVA = _sk_java(SUI.Appends([("SkyySkStats", SUI.spacer(h=ST_HEAD_T + ST_HEAD_H + ST_HEAD_B + ST_BOX_H))]), "SkyyS", "    ",
                              known=["SkyySkStats"])
_ap = SUI.Appends()
st_how(_ap, "SkyySkStats", SUI.J("how(s)", "Earn XP by mining stone and ores - rarer ores pay more"))
ST_HOW_JAVA = _sk_java(_ap, "SkyyS", "  ", known=["SkyySkStats"])
_ap = SUI.Appends()
st_nav(_ap, "SkyySkStats", SUI.J("tree != null ? %d : %d" % (ST_NAV_GAP[True], ST_NAV_GAP[False]), str(ST_NAV_GAP[True])))
ST_NAV_JAVA = _sk_java(_ap, "SkyyS", "  ", known=["SkyySkStats"])
ST_TREE_JAVA = _sk_java(st_tree(), "SkyyS", "    ", known=["SkyyStNav"])
OV_SH = ov_shell()
OV_SHELL_JAVA = _sk_shell_java(OV_SH, "SkyyOv", "  ")
_ap = SUI.Appends()
ov_top(_ap, "SkyyOvBody", SUI.J('"Level " + lv + " of " + omax', "Level 12 of 100"), SUI.J("sub", "Average of your skills 12.4"),
       SUI.J("fill", "240"), SUI.J('"Skills that count (" + sc[1] + ")"', "Skills that count (9)"),
       SUI.J(PKG + ".Overall.listText(u, d)", "Mining 14 - Foraging 9 - Farming 3"))
OV_TOP_JAVA = _sk_java(_ap, "SkyyOv", "  ", known=["SkyyOvBody"])
OV_NOW_JAVA = _sk_java(st_line("SkyyOvNowBox", "SkyyOvNow" + _I, SUI.J("(String) now.get(i)", "+6 max Health"), "white"), "SkyyOv", "    ",
                       known=["SkyyOvNowBox"])
_ap = SUI.Appends()
ov_next(_ap, "SkyyOvBody", "Max Overall Level reached", col="gold", box=False)
OV_MAX_JAVA = _sk_java(_ap, "SkyyOv", "  ", known=["SkyyOvBody"])
_ap = SUI.Appends()
ov_next(_ap, "SkyyOvBody", SUI.J('"Overall Level " + (lv + 1) + " adds"', "Overall Level 13 adds"))
OV_NEXT_HD_JAVA = _sk_java(_ap, "SkyyOv", "    ", known=["SkyyOvBody"])
OV_NEXT_JAVA = _sk_java(st_line("SkyyOvNextBox", "SkyyOvNext" + _I, SUI.J("(String) nx.get(i)", "+0.5 max Health"), "buttonText"), "SkyyOv",
                        "      ", known=["SkyyOvNextBox"])
_ap = SUI.Appends()
ov_foot(_ap, "SkyyOvBody")
OV_FOOT_JAVA = _sk_java(_ap, "SkyyOv", "  ", known=["SkyyOvBody"])


# ---- build-time check of whole sample states: the pieces put together the way the build() methods emit them, with concrete values
def _sk_whole(parts, prefix, body, inner_h, lists=()):
    whole = SUI.Appends()
    for p in parts:
        whole += p
    SUI.check_page(whole, prefix)
    SUI.assert_proven(whole)
    left = SUI.fit([SUI.used_height(whole, body)], inner_h, body)
    assert left == 0, "#%s is not filled exactly: %d px left" % (body, left)
    for lid, lh in lists:
        SUI.fit([SUI.used_height(whole, lid)], lh - 2 * SUI.WELL_LIST_PAD, lid)
    return whole


def sk_state_overview(trees, rows):
    """rows = [(slot, title, prog, fill, tree)]; trees = SkyyTrees running."""
    sh = sk_shell()
    parts = [sh.appends]
    ap = SUI.Appends()
    sk_overview(ap, sh.body)
    ap.sets.append(("SkyySkOv", "Text", "Overall Level 12  -  average 12.4 of 9 skills"))
    parts.append(ap)
    for i, (sl, title, prog, fill, tree) in enumerate(rows):
        acro = sl == ACRO_SLOT
        rh = SK_ACRO_H if acro else SK_ROW_H
        parts.append(sk_row(str(i), rh, SK_PANEL_W[trees], SK_TEXT_W[trees], SK_XP_W[trees], fill, SLOT_COLORS[sl], SLOT_ICONS[sl], title,
                            prog))
        if acro:
            b = sk_bonus(str(i))
            b.sets.append(("SkyySkBonus", "Text", "Speed 5%   Jump 0.3 blocks   Fall damage -10%"))
            parts.append(b)
        if trees:
            parts.append(sk_tree(str(i), rh) if tree else sk_tree_gap(str(i), rh))
        parts.append(sk_stat(str(i), rh))
    whole = _sk_whole(parts, "SkyySk", sh.body, sh.inner_h, [("SkyySkList", SK_LIST_H)])
    for i in range(len(rows)):
        assert SUI.used_width(whole, "SkyySkRow%d" % i) == SK_LIST_IN, "row %d is %d px of %d" % (i, SUI.used_width(whole, "SkyySkRow%d" % i),
                                                                                            SK_LIST_IN)
    return whole


def sk_state_top(rows, me_at, rank_text):
    sh = sk_shell()
    parts = [sh.appends]
    ap = SUI.Appends()
    sk_top(ap, sh.body)
    parts.append(ap)
    if not rows:
        parts.append(sk_top_empty())
    for i, (nm, lv, xp) in enumerate(rows[:10]):
        a = SUI.Appends()
        a.add("SkyySkTop", sk_top_row(str(i), i == me_at, ["%d." % (i + 1), nm, "Level %d" % lv, xp + " XP"]))
        parts.append(a)
    ap = SUI.Appends()
    sk_top_foot(ap, sh.body, rank_text)
    parts.append(ap)
    return _sk_whole(parts, "SkyySk", sh.body, sh.inner_h, [("SkyySkTop", SK_TOP_LIST_H)])


def st_state(name, fill, note, now, nxt, legacy, maxed, tree):
    sh = st_shell(name)
    parts = [sh.appends]
    ap = SUI.Appends()
    st_top(ap, sh.body)
    ap.sets += [("SkyyStTitle", "Text", name + " - level 12 of 100"), ("SkyyStSub", "Text", "1.2k / 5k XP to level 13  (3.8k to go)")]
    parts += [ap, st_bar(fill)]
    if note:
        n = st_note()
        n.sets.append(("SkyyStNote", "Text", "You are not a Mage right now - these boosts work while you are one"))
        parts.append(n)
    else:
        parts.append(st_note_gap())
    ap = SUI.Appends()
    st_mid(ap, sh.body)
    ap.sets.append(("SkyyStNowHd", "Text", "Boosts right now (level 12)"))
    parts.append(ap)
    for i, t in enumerate(now[:ST_LINES]):
        parts.append(st_line("SkyyStNowBox", "SkyyStNow%d" % i, t, "white"))
    if legacy:
        parts.append(SUI.Appends([(sh.body, SUI.spacer(h=ST_HEAD_T + ST_HEAD_H + ST_HEAD_B + ST_BOX_H))]))
    elif maxed:
        ap = SUI.Appends()
        st_next_head(ap, sh.body, "Max level reached - nothing more to unlock", col="gold")
        ap.add(sh.body, SUI.spacer(h=ST_BOX_H))
        parts.append(ap)
    else:
        ap = SUI.Appends()
        st_next_head(ap, sh.body)
        ap.add(sh.body, SUI.panel("SkyyStNextBox", "well", h=ST_BOX_H))
        ap.sets.append(("SkyyStNextHd", "Text", "Level 13 adds"))
        parts.append(ap)
        for i, t in enumerate(nxt[:ST_LINES]):
            parts.append(st_line("SkyyStNextBox", "SkyyStNext%d" % i, t, "buttonText"))
    ap = SUI.Appends()
    st_how(ap, sh.body, "Earn XP by mining stone and ores - rarer ores pay more")
    st_nav(ap, sh.body, ST_NAV_GAP[bool(tree)])
    parts.append(ap)
    if tree:
        parts.append(st_tree())
    whole = _sk_whole(parts, "SkyyS", sh.body, sh.inner_h, [("SkyyStNowBox", ST_BOX_H + 2 * SUI.WELL_LIST_PAD - 2 * SUI.WELL_PAD)])
    nav_want = 3 * SUI.BTN_MIN_W + 12 if tree else 2 * SUI.BTN_MIN_W + 6     # < BACK / TOP 10 (/ SKILL TREE) + their 6 px gaps
    assert SUI.used_width(whole, "SkyyStNav") == nav_want, (tree, SUI.used_width(whole, "SkyyStNav"), nav_want)
    assert ST_NAV_GAP[bool(tree)] + nav_want == SK_IN_W, "the footer's left padding right-aligns it in the body"
    return whole


def ov_state(maxed, now, nxt):
    sh = ov_shell()
    parts = [sh.appends]
    ap = SUI.Appends()
    ov_top(ap, sh.body, "Level 12 of 100", "Average of your skills 12.4 - Overall Level 13 at an average of 13.0", 0 if maxed else 240,
           "Skills that count (9)", "Mining 14 - Foraging 9 - Farming 3 - Acrobatics 20 - Alchemy 1 - Smithing 2 - Cooking 0 - Exploration 5 "
           "- Divinity 18 (your class)")
    parts.append(ap)
    for i, t in enumerate(now[:OV_NOW_N]):
        parts.append(st_line("SkyyOvNowBox", "SkyyOvNow%d" % i, t, "white"))
    ap = SUI.Appends()
    if maxed:
        ov_next(ap, sh.body, "Max Overall Level reached", col="gold", box=False)
    else:
        ov_next(ap, sh.body, "Overall Level 13 adds")
    parts.append(ap)
    if not maxed:
        for i, t in enumerate(nxt[:OV_NEXT_N]):
            parts.append(st_line("SkyyOvNextBox", "SkyyOvNext%d" % i, t, "buttonText"))
    ap = SUI.Appends()
    ov_foot(ap, sh.body)
    parts.append(ap)
    return _sk_whole(parts, "SkyyOv", sh.body, sh.inner_h)


_rows9 = [(sl, "Class skill - choose a class with /class", "Your combat skill is your class skill", 0, False) if sl == COMBAT_SLOT
          else (sl, SLOT_LABELS[sl] + "  12", "1.2k / 5k XP to level 13", 200, sl in (0, 1, 2, 12)) for sl in SK_ROW_SLOTS]
_sk_checked = [sk_state_overview(True, _rows9), sk_state_overview(False, _rows9),
               sk_state_top([("Skyy", 40, "1.2m"), ("Alex, the 2nd", 12, "12.3k"), ("Sam (profile 2)", 1, "55")], 0,
                            "Your rank #1 of 3 - level 40 - 1.2m XP"),
               sk_state_top([("P%d" % n, 50 - n, "%dk" % (99 - n)) for n in range(12)], -1, "Your rank #11 of 12 - level 39 - 88k XP"),
               sk_state_top([], -1, "You are not ranked yet"),
               st_state("Mining", 300, False, ["+0.25% chance to double the drops of mined blocks"] * 7, ["+0.005% chance"] * 7, False, False, True),
               st_state("Fury", 0, True, ["+1 max Health"], ["+0.2% damage with Berserker weapons"], False, False, False),
               st_state("Combat", 0, False, ["No class yet - choose one with /class to start leveling combat"], [], True, False, False),
               st_state("Cooking", 600, False, ["Food you cook gets stronger"], [], False, True, True),
               ov_state(False, ["+6 max Health (0.5 per Overall Level)", "+2.4 max Mana (0.2 per Overall Level)", "Base Mana 10"],
                        ["+0.5 max Health", "+0.2 max Mana"]),
               ov_state(True, ["+50 max Health (0.5 per Overall Level)"], [])]
print("skills pages: /skills %d x %d, Stats %d x %d, Overall %d x %d on %s - %d sample states checked (check_page, assert_proven, heights)"
      % (SK_W, SK_H, STATS_W, STATS_H, OV_W, OV_H, KIT_ID, len(_sk_checked)))
# ---- SKILLS PAGE BLOCK END
page.addField(CtField.make("public int view;", page))
page.addConstructor(CtNewConstructor.make(f"""
public SkillsPage({PR} pr) {{
  super(pr, {LIFE}.CanDismiss);
  this.view = -1;
}}""", page))
page.addMethod(CtNewMethod.make("""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ');
}""", page))
SK_BUILD_SRC = f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  // 0.4.7: the plain vanilla window (title SKILLS / TOP 10 - <SKILL>), body = 0.4.6's root #SkyySkills - kit markup
{SK_SHELL_JAVA}
  if (this.view < 0 || this.view >= {PKG}.SkillDefs.N) {{
    int cs = {PKG}.SkillClass.slot(u);
    int[] rows = {PKG}.SkillDefs.ROW_SLOTS;
    int[] osc = {PKG}.Overall.sums(u, d);
    // the Overall well + OVERALL button, the list well, the hint caption
{SK_OVERVIEW_JAVA}
    b.set("#SkyySkOv.Text", "Overall Level " + {PKG}.Overall.level(osc) + "  -  average " + {PKG}.Overall.avg({PKG}.Overall.tenths(osc)) + " of " + osc[1] + " skills");
    ev.addEventBinding({BT}.Activating, "#SkyySkOvStat", {EVD}.of("a", "skstatov"));
    boolean trees = {PKG}.SkillBonus.treesOn();
    int pw = trees ? {SK_PANEL_W[True]} : {SK_PANEL_W[False]};
    int tw = trees ? {SK_TEXT_W[True]} : {SK_TEXT_W[False]};
    int bw = trees ? {SK_XP_W[True]} : {SK_XP_W[False]};
    for (int i = 0; i < rows.length; i++) {{
      int sl = rows[i];
      boolean classRow = sl == {PKG}.SkillDefs.COMBAT;
      if (classRow && cs >= 0) sl = cs;
      long total = d[sl];
      int lv = {PKG}.SkillDefs.levelOf(sl, total);
      long cur = {PKG}.SkillDefs.intoLevel(sl, total);
      long need = {PKG}.SkillDefs.needFor(sl, total);
      int fill = need > 0L ? (int) ((long) bw * cur / need) : bw;
      if (fill < 0) fill = 0;
      if (fill > bw) fill = bw;
      String prog = need > 0L ? ({PKG}.SkillDefs.fmt(cur) + " / " + {PKG}.SkillDefs.fmt(need) + " XP to level " + (lv + 1)) : ("MAX LEVEL - " + {PKG}.SkillDefs.fmt(total) + " XP");
      String col = {PKG}.SkillDefs.COLORS[sl];
      String title = {PKG}.SkillDefs.LABELS[sl] + "  " + lv;
      if (classRow) {{
        if (cs >= 0) title = {PKG}.SkillClass.skillName(u, cs) + "  " + lv;
        else {{
          title = "Class skill - choose a class with /class";
          prog = total > 0L ? "Old Combat XP (level " + lv + ") moves to the first class you choose" : "Your combat skill is your class skill";
          fill = 0;
        }}
      }}
      boolean acroRow = sl == {PKG}.SkillDefs.ACROBATICS;
      int rh = acroRow ? {SK_ACRO_H} : {SK_ROW_H};
      // the row: panel, icon, name, XP bar, progress line (texts b.set)
{SK_ROW_JAVA}
      if (acroRow) {{
{SK_BONUS_JAVA}
        b.set("#SkyySkBonus.Text", {PKG}.Acro.bonusText(lv));
      }}
      if (trees) {{
        if ({PKG}.SkillBonus.treeAvailable(sl)) {{
{SK_TREE_JAVA}
          ev.addEventBinding({BT}.Activating, "#SkyySkTree" + i, {EVD}.of("a", "sktree" + sl));
        }} else {{
{SK_TREE_GAP_JAVA}
        }}
      }}
{SK_STAT_JAVA}
      ev.addEventBinding({BT}.Activating, "#SkyySkStat" + i, {EVD}.of("a", "skstat" + sl));
    }}
    return;
  }}
  int s = this.view;
  java.util.ArrayList rows = {PKG}.SkillTop.all(s);
  // the column heads + the list well
{SK_TOP_JAVA}
  int n = rows.size() < 10 ? rows.size() : 10;
  if (n == 0) {{
{SK_TOP_EMPTY_JAVA}
  }}
  for (int i = 0; i < n; i++) {{
    Object[] e = (Object[]) rows.get(i);
    long x = ((Long) e[1]).longValue();
    boolean me = {PKG}.SkillStore.pkey(u).equals(e[2]);
{SK_TOP_ROW_JAVA}
  }}
  int rank = {PKG}.SkillTop.rankOf(rows, u);
  // the rank line + the footer (BACK)
{SK_TOP_FOOT_JAVA}
  ev.addEventBinding({BT}.Activating, "#SkyySkBack", {EVD}.of("a", "skback"));
}}"""
for _piece in (SK_SHELL_JAVA, SK_OVERVIEW_JAVA, SK_ROW_JAVA, SK_BONUS_JAVA, SK_TREE_JAVA, SK_TREE_GAP_JAVA, SK_STAT_JAVA, SK_TOP_JAVA,
               SK_TOP_EMPTY_JAVA, SK_TOP_ROW_JAVA, SK_TOP_FOOT_JAVA):
    assert _piece in SK_BUILD_SRC, "kit Java changed on its way into the build() source"   # the f-string recipe: verbatim
page.addMethod(CtNewMethod.make(SK_BUILD_SRC, page))
# ================= StatsPage (0.3): one skill - level, XP to next, boosts now (numbers), what the next level adds =================
# 0.4.2: scaled ~1.5x (Skyy): root 960 x 795 (was 640 x 530; fits a 1080-high screen), fonts 24 / 17 / 20 / 18 / 15, bar 600 x 18,
# buttons 195 x 45 with 18 pt labels, the how-to line always wraps (2 lines). Content height at most 752 (7 + 7 lines).
STBARW = 600
# Inline page like SkillsPage (root Group with Width/Height only, no underscores in ids, TextButton + EventData with a trailing-quote
# match); every dynamic text goes through b.set("#Id.Text", ...), which is safe for any character.
spg.addField(CtField.make("public int slot;", spg))
spg.addConstructor(CtNewConstructor.make(f"""
public StatsPage({PR} pr, int slot) {{
  super(pr, {LIFE}.CanDismiss);
  this.slot = slot;
}}""", spg))
# at most 3 decimals, trailing zeros cut, no Locale (String.format could print a decimal comma): 2.5 -> "2.5", 0.015 -> "0.015",
# 10.0 -> "10"
spg.addMethod(CtNewMethod.make("""
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
}""", spg))
spg.addMethod(CtNewMethod.make("""
public static String pc(double frac) {
  return num(frac * 100.0) + "%";
}""", spg))
# a flat stat perk: now = per x level, next level adds per (linear)
spg.addMethod(CtNewMethod.make(f"""
public static void stat(java.util.ArrayList out, double per, int lv, boolean next, String what) {{
  if (per <= 0.0 || !{PKG}.PerkCfg.ENABLED) return;
  double v = next ? per : per * lv;
  if (v <= 0.0) return;
  out.add("+" + num(v) + " " + what);
}}""", spg))
# 0.4: optional lines from another mod (bridge skill:stats:<SkillName>, e.g. SkyyCooking for "Cooking"): Function apply(Object[]{UUID,
# Integer level, Boolean next}) -> java.util.List of String; at most 5 lines; -1 = no hook
spg.addMethod(CtNewMethod.make(f"""
public static int hook(java.util.UUID u, int s, int lv, boolean next, java.util.ArrayList out) {{
  try {{
    Object f = {PKG}.SkillStore.bridge().get("skill:stats:" + {PKG}.SkillDefs.NAMES[s]);
    if (!(f instanceof java.util.function.Function)) return -1;
    Object r = ((java.util.function.Function) f).apply(new Object[] {{ u, Integer.valueOf(lv), Boolean.valueOf(next) }});
    if (!(r instanceof java.util.List)) return 0;
    java.util.List l = (java.util.List) r;
    int n = 0;
    for (int i = 0; i < l.size() && n < 5; i++) {{
      Object o = l.get(i);
      if (o == null) continue;
      String t = String.valueOf(o).trim();
      if (t.length() == 0) continue;
      out.add(t);
      n++;
    }}
    return n;
  }} catch (Throwable t) {{ return -1; }}
}}""", spg))
# 0.4.1 (Exploration-Build-Spec 3.5): the Acrobatics "Skill tree:" line - SkyyTrees 0.2 posts its speed / jump / fall nodes as the movement
# source move:<uuid>["trees.acrobatics"] (flat layer: speed = fraction of vanilla speed, jump = blocks, fallDamage = negative fraction) and
# its dodge nodes as skill:bonus dodge.acrobatics (Acro.treeDodge, clamped), plus the XP bonus if an admin lists Acrobatics; null = nothing
spg.addMethod(CtNewMethod.make(f"""
public static String acroTreeLine(java.util.UUID u) {{
  java.util.ArrayList parts = new java.util.ArrayList();
  try {{
    java.util.Map m = {PKG}.MoveSync.sources(u, false);
    Object o = null;
    if (m != null) o = m.get("trees.acrobatics");
    if (o instanceof java.util.Map) {{
      java.util.Map e = (java.util.Map) o;
      double sp = (double) {PKG}.MoveSync.num(e.get("speed"));
      double jp = (double) {PKG}.MoveSync.num(e.get("jump"));
      double fd = (double) {PKG}.MoveSync.num(e.get("fallDamage"));
      if (sp > 0.00001) parts.add("+" + pc(sp) + " speed");
      if (jp > 0.00001) parts.add("+" + num(jp) + " blocks jump");
      if (fd < -0.00001) parts.add("-" + pc(0.0 - fd) + " fall damage");
    }}
  }} catch (Throwable t) {{ }}
  double dg = {PKG}.Acro.treeDodge(u);
  if (dg > 0.00001) parts.add("+" + pc(dg) + " dodge push");
  double djf = {PKG}.Acro.djFraction(u);
  if (djf > 0.00001) parts.add("double jump " + pc(djf));
  double xb = {PKG}.SkillBonus.xpBonus(u, {PKG}.SkillDefs.ACROBATICS);
  if (xb > 0.00001) parts.add("+" + pc(xb) + " XP");
  if (parts.isEmpty()) return null;
  StringBuilder sb = new StringBuilder("Skill tree: ");
  for (int i = 0; i < parts.size(); i++) {{
    if (i > 0) sb.append(", ");
    sb.append((String) parts.get(i));
  }}
  return sb.toString();
}}""", spg))
# 0.4 trees bridge: "Skill tree: +X% double drops, +Y% XP" from skill:bonus:<uuid> (SkyyTrees); null when both are 0
spg.addMethod(CtNewMethod.make(f"""
public static String treeLine(java.util.UUID u, int s) {{
  if (s == {PKG}.SkillDefs.ACROBATICS) return acroTreeLine(u);
  double dd = {PKG}.SkillBonus.dd(u, s);
  double xb = {PKG}.SkillBonus.xpBonus(u, s);
  if (dd <= 0.00001 && xb <= 0.00001) return null;
  StringBuilder sb = new StringBuilder("Bonuses (trees + tools): ");   // 0.4.14: SkyyGear 0.2.2 posts the held tool as source "gear"
  if (dd > 0.00001) sb.append("+").append(pc(dd)).append(" double drops");
  if (xb > 0.00001) {{
    if (dd > 0.00001) sb.append(", ");
    sb.append("+").append(pc(xb)).append(" XP");
  }}
  return sb.toString();
}}""", spg))
spg.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList lines(java.util.UUID u, int s, int lv, boolean next) {{
  java.util.ArrayList out = new java.util.ArrayList();
  if (s == {PKG}.SkillDefs.COMBAT) {{
    if (!next) {{
      out.add("No class yet - choose one with /class to start leveling combat");
      if ({PKG}.SkillStore.data(u)[s] > 0L) out.add("Old Combat XP - level " + lv + " - moves to the first class you choose");
    }}
    return out;
  }}
  int row = {PKG}.SkillDefs.perkRow(s);
  if (row < 0) return out;
  int b = next ? lv + 1 : lv;
  if (row == {PKG}.SkillDefs.ACROBATICS) {{
    if (!{PKG}.AcroCfg.ENABLED) {{
      if (!next) out.add("Acrobatics bonuses are turned off on this server");
    }} else {{
      double sp = {PKG}.Acro.speedBonus(b) - (next ? {PKG}.Acro.speedBonus(lv) : 0.0);
      double jp = {PKG}.Acro.jumpBonus(b) - (next ? {PKG}.Acro.jumpBonus(lv) : 0.0);
      double fb = {PKG}.Acro.fallBonus(b) - (next ? {PKG}.Acro.fallBonus(lv) : 0.0);
      double db = {PKG}.Acro.dodgeBonus(b) - (next ? {PKG}.Acro.dodgeBonus(lv) : 0.0);
      if (sp > 0.00001) out.add("+" + pc(sp) + " movement speed (of vanilla speed)");
      if (jp > 0.00001) out.add("+" + num(jp) + " blocks jump height");
      if (fb > 0.00001) out.add("-" + pc(fb) + " fall damage");
      if (db > 0.00001) out.add("+" + pc(db) + " dodge push");
      if (!next) {{
        String dj = {PKG}.Acro.djLine(u);
        if (dj != null) out.add(dj);
      }}
    }}
  }}
  if (s == {PKG}.SkillDefs.ALCHEMY) {{
    if (!{PKG}.AlchCfg.ENABLED) {{
      if (!next) out.add("Alchemy is turned off on this server");
    }} else {{
      double du = {PKG}.Brew.bonusFor(b) - (next ? {PKG}.Brew.bonusFor(lv) : 0.0);
      if (du > 0.00001) {{
        out.add("+" + pc(du) + " longer potion effects");
        if (!next) out.add("   " + {PKG}.Brew.pulseText(b));
      }}
    }}
  }}
  stat(out, {PKG}.PerkCfg.HP[row], lv, next, "max Health");
  stat(out, {PKG}.PerkCfg.STA[row], lv, next, "max Stamina");
  stat(out, {PKG}.PerkCfg.MANA[row], lv, next, "max Mana");
  String cmn = {PKG}.ClassMana.statsLine(s, lv, next);   // 0.4.15: max Mana per class level (Priest 5 per Divinity level, Mage 10 per Sorcery level)
  if (cmn != null) out.add(cmn);
  if (s == {PKG}.SkillDefs.ALCHEMY && {PKG}.AlchCfg.ENABLED) {{
    double ex = {PKG}.Brew.extraChance(b) - (next ? {PKG}.Brew.extraChance(lv) : 0.0);
    if (ex > 0.00001) out.add((next ? "+" : "") + pc(ex) + " chance to brew an extra potion");
  }}
  if (row <= {PKG}.SkillDefs.FARMING) {{
    String[] what = new String[] {{ "mined blocks", "chopped logs", "harvested crops" }};
    double c = {PKG}.Perks.chance(row, b) - (next ? {PKG}.Perks.chance(row, lv) : 0.0);
    if (c > 0.00001) out.add((next ? "+" : "") + pc(c) + " chance to double the drops of " + what[row]);
  }}
  if (!next) {{ String gp = {PKG}.GatherPace.statsLine(s, lv); if (gp != null) out.add(gp); }}   // 0.4.14: the gathering pace
  if (row == {PKG}.SkillDefs.COMBAT && {PKG}.SkillDefs.isClass(s) && {PKG}.PerkCfg.ENABLED && {PKG}.PerkCfg.DMG > 0.0) {{
    double dm = next ? {PKG}.PerkCfg.DMG : {PKG}.Perks.damage(lv);
    if (dm > 0.0) out.add("+" + pc(dm) + " damage with " + {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)] + " weapons" + ({PKG}.PerkCfg.DMG_PVP ? "" : " (against monsters)"));
  }}
  String xl = {PKG}.Xbow.line(u, s, lv, next);
  if (xl != null) out.add(xl);
  if (s == {PKG}.SkillDefs.DIVINITY && !next) out.add({PKG}.DivCfg.statsLine());
  if (!next) {{
    String tl = treeLine(u, s);
    if (tl != null) out.add(tl);
  }}
  int hooked = hook(u, s, lv, next, out);
  if (s == {PKG}.SkillDefs.EXPLORATION && !next) {{
    if (!{PKG}.ExplCfg.ENABLED) out.add("Exploration XP is turned off on this server (exploration.enabled=false)");
    else if (hooked < 0) out.add("Install SkyyExploration to earn Exploration XP");
    out.add("Exploration XP ignores the xp multiplier and every skill-tree or booster bonus");
  }}
  if (s == {PKG}.SkillDefs.COOKING && !next && hooked < 0) out.add("Food you cook gets stronger with your Cooking level (shown here when SkyyCooking is installed)");
  if (s == {PKG}.SkillDefs.SMITHING && !next && out.isEmpty()) out.add("No boosts yet - they arrive with reforging and powders");
  if (next && {PKG}.SkillCfg.COINS_PER_LEVEL > 0L) out.add("+" + {PKG}.SkillDefs.fmt({PKG}.SkillCfg.COINS_PER_LEVEL * (long) b) + " coins when you reach level " + b);
  if (!next && out.isEmpty()) out.add(lv <= 0 ? "Nothing yet - level up to unlock boosts" : "This skill gives no boosts on this server");
  return out;
}}""", spg))
spg.addMethod(CtNewMethod.make(f"""
public static String how(int s) {{
  if (s == {PKG}.SkillDefs.MINING) return "Earn XP by mining stone and ores - rarer ores pay more";
  if (s == {PKG}.SkillDefs.FORAGING) return "Earn XP by chopping trees - rare woods pay more" + ({PKG}.FellCfg.on() ? " - fell a tree and every log" + ({PKG}.FellCfg.LEAVES ? " and leaf" : "") + " that comes down pays you too" : "");
  if (s == {PKG}.SkillDefs.FARMING) return "Earn XP by harvesting fully grown crops - break them or press F on eternal crops and bushes" + ({PKG}.Sickle.ON ? " - or swing a sickle through them" : "");
  if (s == {PKG}.SkillDefs.ACROBATICS) return "Earn XP by running - jumping - dodging - and surviving falls that hurt (higher falls pay more - safe drops and water pay 0)" + ({PKG}.AcroCfg.ENABLED && {PKG}.AcroCfg.ROLL > 0.0 ? " - crouch as you land to roll: +" + Math.round({PKG}.AcroCfg.ROLL * 100.0) + "%" : "");
  if (s == {PKG}.SkillDefs.ALCHEMY) return "Earn XP by brewing at the Alchemy Bench - stronger potions and higher bench tiers pay more (Greater potions pay the most)";
  if (s == {PKG}.SkillDefs.SMITHING) return "Earn XP by smelting - take the bars out of a Furnace yourself or use the Furnace tab of /craft (reforging and powders later)";
  if (s == {PKG}.SkillDefs.COOKING) return "Cook at a Cooking Bench - food you cook gets stronger with your level";
  if (s == {PKG}.SkillDefs.EXPLORATION) return "Earn XP by exploring - open loot chests for the first time - walk into new chunks (not while flying) - discover Hytale's zones. Once each per profile. XP boosters never apply";
  if (s == {PKG}.SkillDefs.COMBAT) return "Your combat skill is your class skill - Archer Archery / Warrior Swordsmanship / Mage Sorcery / Berserker Fury / Priest Divinity (Assassin and Shaman later)";
  if (!{PKG}.SkillDefs.isClass(s)) return "";
  String c = {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)];
  String w = {PKG}.SkillClass.weaponsText(c);
  return "Earn XP by defeating monsters with " + c + " weapons" + (w == null ? "" : " - " + w) + {PKG}.PartyXp.howText() + {PKG}.SkillCfg.classHow();
}}""", spg))
assert STBARW == SK_BIG_BAR_W, "the Stats bar is the 600 px bar the look block budgets"
ST_BUILD_SRC = f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  int s = this.slot;
  if (s < 0 || s >= {PKG}.SkillDefs.N) s = 0;
  int cs = {PKG}.SkillClass.slot(u);
  if (s == {PKG}.SkillDefs.COMBAT && cs >= 0) s = cs;
  long total = d[s];
  int lv = {PKG}.SkillDefs.levelOf(s, total);
  long cur = {PKG}.SkillDefs.intoLevel(s, total);
  long need = {PKG}.SkillDefs.needFor(s, total);
  int fill = need > 0L ? (int) ({STBARW}L * cur / need) : {STBARW};
  if (fill < 0) fill = 0;
  if (fill > {STBARW}) fill = {STBARW};
  boolean legacy = s == {PKG}.SkillDefs.COMBAT;
  if (legacy) fill = 0;
  String col = {PKG}.SkillDefs.COLORS[s];
  String name = legacy ? "Combat" : {PKG}.SkillClass.skillName(u, s);
  // 0.4.7: the plain vanilla window (title = the skill name), body = 0.4.6's root #SkyySkStats; the title, XP line and bar row
{ST_SHELL_JAVA}
{ST_TOP_JAVA}
  b.set("#SkyyStTitle.Text", legacy ? "Combat - no class" : name + " - level " + lv + " of " + {PKG}.SkillDefs.maxOf(s));
  String sub;
  if (legacy) sub = "Choose a class with /class - each class has its own combat skill";
  else if (need > 0L) sub = {PKG}.SkillDefs.fmt(cur) + " / " + {PKG}.SkillDefs.fmt(need) + " XP to level " + (lv + 1) + "  (" + {PKG}.SkillDefs.fmt(need - cur) + " to go)";
  else sub = "MAX LEVEL - " + {PKG}.SkillDefs.fmt(total) + " XP";
  b.set("#SkyyStSub.Text", sub);
{ST_BAR_JAVA}
  if ({PKG}.SkillDefs.isClass(s) && s != cs) {{
    String cn = {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)];
    String art = (cn.startsWith("A") || cn.startsWith("E") || cn.startsWith("I") || cn.startsWith("O") || cn.startsWith("U")) ? "an " : "a ";
{ST_NOTE_JAVA}
    b.set("#SkyyStNote.Text", "You are not " + art + cn + " right now - these boosts work while you are one");
  }} else {{
{ST_NOTE_GAP_JAVA}
  }}
  // the separator, BOOSTS RIGHT NOW + its well
{ST_MID_JAVA}
  b.set("#SkyyStNowHd.Text", legacy ? "Your combat" : "Boosts right now (level " + lv + ")");
  java.util.ArrayList now = lines(u, s, lv, false);
  for (int i = 0; i < now.size() && i < {ST_LINES}; i++) {{
{ST_NOW_JAVA}
  }}
  if (!legacy) {{
    if (need > 0L) {{
{ST_NEXT_HD_JAVA}
      b.set("#SkyyStNextHd.Text", "Level " + (lv + 1) + " adds");
      java.util.ArrayList nx = lines(u, s, lv, true);
      for (int i = 0; i < nx.size() && i < {ST_LINES}; i++) {{
{ST_NEXT_JAVA}
      }}
    }} else {{
{ST_MAX_JAVA}
    }}
  }} else {{
{ST_LEGACY_GAP_JAVA}
  }}
  // the separator + the how-to caption, the footer (< BACK, TOP 10, SKILL TREE when that skill has a tree)
{ST_HOW_JAVA}
  String tree = {PKG}.SkillBonus.treeAvailable(s) ? {PKG}.SkillBonus.treeName(s) : null;
{ST_NAV_JAVA}
  ev.addEventBinding({BT}.Activating, "#SkyyStBack", {EVD}.of("a", "stback"));
  ev.addEventBinding({BT}.Activating, "#SkyyStTop", {EVD}.of("a", "sttop"));
  if (tree != null) {{
{ST_TREE_JAVA}
    ev.addEventBinding({BT}.Activating, "#SkyyStTree", {EVD}.of("a", "sttree"));
  }}
}}"""
for _piece in (ST_SHELL_JAVA, ST_TOP_JAVA, ST_BAR_JAVA, ST_NOTE_JAVA, ST_NOTE_GAP_JAVA, ST_MID_JAVA, ST_NOW_JAVA, ST_NEXT_HD_JAVA, ST_NEXT_JAVA,
               ST_MAX_JAVA, ST_LEGACY_GAP_JAVA, ST_HOW_JAVA, ST_NAV_JAVA, ST_TREE_JAVA):
    assert _piece in ST_BUILD_SRC, "kit Java changed on its way into the build() source"
spg.addMethod(CtNewMethod.make(ST_BUILD_SRC, spg))
spg.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (p == null) return;
    if (data.indexOf("stback\\"") >= 0) {{ p.getPageManager().openCustomPage(ref, st, new {PKG}.SkillsPage(this.playerRef)); return; }}
    if (data.indexOf("sttree\\"") >= 0) {{ {PKG}.SkillBonus.openTree(this.playerRef, {PKG}.SkillBonus.treeName(this.slot)); return; }}
    if (data.indexOf("sttop\\"") >= 0) {{
      int s = this.slot;
      if (s == {PKG}.SkillDefs.COMBAT) {{ int c = {PKG}.SkillClass.slot(this.playerRef.getUuid()); if (c >= 0) s = c; }}
      {PKG}.SkillsPage sp = new {PKG}.SkillsPage(this.playerRef);
      sp.view = s;
      p.getPageManager().openCustomPage(ref, st, sp);
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("stats page event failed: " + t); }}
}}""", spg))
# ================= OverallPage (0.4.6): the Overall Level page (research/Overall-Level-Spec.md 2.8.2 / 4.7) =================
# 0.4.7: its vanilla look (0.4.6: hand-copied style strings + a client-folder texture check) comes from the shared kit now - the
# SKILLS PAGES LOOK block above (ov_* functions, OV_*_JAVA pieces); every value is proven against Assets.zip by SUI.verify().
OVBARW = 600
assert OVBARW == SK_BIG_BAR_W, "the Overall bar is the 600 px bar the look block budgets"
opg.addConstructor(CtNewConstructor.make(f"""
public OverallPage({PR} pr) {{
  super(pr, {LIFE}.CanDismiss);
}}""", opg))
OV_BUILD_SRC = f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  int[] sc = {PKG}.Overall.sums(u, d);
  int lv = {PKG}.Overall.level(sc);
  int t = {PKG}.Overall.tenths(sc);
  int omax = {PKG}.Overall.maxLevel(u);
  boolean max = omax > 0 && lv >= omax;
  int fill = max ? {OVBARW} : (t % 10) * ({OVBARW} / 10);
  if (fill < 0) fill = 0;
  if (fill > {OVBARW}) fill = {OVBARW};
  String sub = max ? "Average of your skills " + {PKG}.Overall.avg(t) + " - the highest Overall Level" : "Average of your skills " + {PKG}.Overall.avg(t) + " - Overall Level " + (lv + 1) + " at an average of " + (lv + 1) + ".0";
  if (omax <= 0) sub = "No skill counts toward the Overall Level on this server";
  // 0.4.7: the plain vanilla window (0.4.6's ids), the level + average lines, the bar, SKILLS THAT COUNT, BOOSTS RIGHT NOW - kit markup
{OV_SHELL_JAVA}
{OV_TOP_JAVA}
  java.util.ArrayList now = {PKG}.Overall.nowLines(u, lv);
  for (int i = 0; i < now.size() && i < {OV_NOW_N}; i++) {{
{OV_NOW_JAVA}
  }}
  if (max) {{
{OV_MAX_JAVA}
  }} else {{
{OV_NEXT_HD_JAVA}
    java.util.ArrayList nx = {PKG}.Overall.nextLines(lv, omax);
    for (int i = 0; i < nx.size() && i < {OV_NEXT_N}; i++) {{
{OV_NEXT_JAVA}
    }}
  }}
  // the separator, the how-to caption, the footer (BACK)
{OV_FOOT_JAVA}
  ev.addEventBinding({BT}.Activating, "#SkyyOvBack", {EVD}.of("a", "ovback"));
}}"""
for _piece in (OV_SHELL_JAVA, OV_TOP_JAVA, OV_NOW_JAVA, OV_MAX_JAVA, OV_NEXT_HD_JAVA, OV_NEXT_JAVA, OV_FOOT_JAVA):
    assert _piece in OV_BUILD_SRC, "kit Java changed on its way into the build() source"
opg.addMethod(CtNewMethod.make(OV_BUILD_SRC, opg))
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
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    if (data.indexOf("skstatov\\"") >= 0) {{
      {PLA} po = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
      if (po != null) po.getPageManager().openCustomPage(ref, st, new {PKG}.OverallPage(this.playerRef));
      return;
    }}
    for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
      if (data.indexOf("skstat" + i + "\\"") >= 0) {{
        {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
        if (p != null) p.getPageManager().openCustomPage(ref, st, new {PKG}.StatsPage(this.playerRef, i));
        return;
      }}
    }}
    for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
      if (data.indexOf("sktree" + i + "\\"") >= 0) {{ {PKG}.SkillBonus.openTree(this.playerRef, {PKG}.SkillBonus.treeName(i)); return; }}
    }}
    if (data.indexOf("skback\\"") >= 0) {{ this.view = -1; rebuild(); return; }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("skills page event failed: " + t); }}
}}""", page))

# ================= 0.4.3 ADMIN CONFIG (research/Server-Setup-Spec.md 4.9 + 5.7; tools/CONFIG-CONTRACT.md; kit = tools/skyycfg.py) =================
# Row = (key, label, category, type, default, min, max, opts, unit, flags, help, binding). Row key = file key of xp.properties (never
# renamed). Every scalar binds reload: (file line, then SkillKit.reload = the /skills reload path); min / max = the loader's clamps (typed
# values outside are refused; hand-edited files are still clamped by the loader). Defaults = what the loader uses today: checked below
# against the default xp.properties text (DEFAULTS), and the rows absent from it against PerkCfg's code defaults (0).
LEVELS_TEXT = ",".join(str(x) for x in LEVELS)
CFG_CATS = [("parts", "Parts"), ("general", "General"), ("levels", "Levels"), ("gathering", "Gathering"), ("combat", "Combat"),
            ("acrobatics", "Acrobatics"), ("perks", "Perks"), ("overall", "Overall and Mana"), ("crafting", "Crafting")]
_LP = "live,part,danger"
CFG_ROWS = [
    # ---- parts (spec 3: the existing master keys; confirm only when switched OFF)
    ("acro.enabled", "Acrobatics", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: no Acrobatics XP and no movement bonuses (speed, jump, fall, dodge). Levels are kept.", "reload"),
    ("acro.doubleJump.enabled", "Double Jump", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: the Acrobatics tree's Double Jump node does nothing. Tree points are kept.", "reload"),
    ("perk.enabled", "Skill perks", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: no max health / stamina / mana, double drops or class damage from skill levels.", "reload"),
    ("alchemy.enabled", "Alchemy", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: the Alchemy Bench pays no Alchemy XP and the brewer perks stop. Levels are kept.", "reload"),
    ("smithing.smelt.enabled", "Smithing from smelting", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: the Furnace and the /craft Furnace tab pay no Smithing XP. Levels are kept.", "reload"),
    ("exploration.enabled", "Exploration XP", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: Exploration XP from SkyyExploration is refused. Levels are kept.", "reload"),
    ("fell.enabled", "Felled trees", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: only the log you break pays; logs that fall with the tree pay nothing.", "reload"),
    ("party.combatShare.enabled", "Party combat XP share", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: party members no longer get a share of a kill's class XP.", "reload"),
    ("bridge.bonus.enabled", "Skill tree bonuses", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: SkyyTrees Wisdom (more XP) and Fortune (double drops) nodes are ignored.", "reload"),
    ("perk.archery.keepLoaded.enabled", "Crossbows stay loaded", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: a crossbow unloads when you switch slots, as in vanilla (its bolts come back as arrows).", "reload"),
    # 0.4.6 (research/Overall-Level-Spec.md 4.9): part switch = bool + live,part,danger; asks only when switched OFF
    ("mana.base.enabled", "Base Mana", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: no base Mana from Skills (vanilla max Mana is 0). Alchemy and Overall Level Mana stay.", "reload"),
    ("overall.enabled", "Overall Level Health and Mana", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: the Overall Level adds no max Health or Mana. It is still shown on /skills.", "reload"),
    ("divinity.healXp.enabled", "Divinity XP from healing", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: Priest heals pay no Divinity XP (kills still do). Levels are kept.", "reload"),
    # 0.4.14 (Skyy 2026-10-02 "level bonus + gap rule max +250%"): needs SkyyMobs levels; off = 0.4.13's kill XP
    ("combat.levelXp.enabled", "Kill XP by mob level", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: kills pay no mob level bonus or level gap (needs SkyyMobs levels). Levels are kept.", "reload"),
    # ---- general
    ("multiplier", "XP multiplier", "general", "dec", "1.0", "0", "100", "", "x", "live,danger",
     "Every skill's XP times this - kills, heals and other mods' grants too (not Exploration).", "reload"),
    ("coinsPerLevel", "Coins per level up", "general", "int", "100", "0", "1000000000", "step=50", "coins", "live,danger",
     "A level up pays this x the new level in coins (needs SkyyCoins).", "reload"),
    ("feedback", "XP chat lines", "general", "bool", "true", "", "", "", "", "live",
     "Off: no '+12 Mining XP' lines for anyone. Each player can also hide them in /settings.", "reload"),
    ("feedbackMs", "XP line at most every", "general", "int", "2000", "500", "600000", "", "ms", "live,adv",
     "One combined +XP chat line per player per this many ms.", "reload"),
    ("creativeXp", "XP in creative mode", "general", "bool", "false", "", "", "", "", "live,danger",
     "On: players in creative mode earn skill XP too (easy to farm).", "reload;confirm=on"),
    ("ignorePlaced", "No XP from placed blocks", "general", "bool", "true", "", "", "", "", "live,danger",
     "Off lets players farm XP by placing and breaking blocks. Crops always pay when ripe.", "reload;confirm=off"),
    ("farmingNeedsRipe", "Crops pay only when ripe", "general", "bool", "true", "", "", "", "", "live",
     "Off: breaking a crop at any growth stage pays Farming XP.", "reload"),
    ("harvestCooldownMs", "Harvest XP per block every", "general", "int", "5000", "3000", "600000", "", "ms", "live,adv",
     "F-harvest and ripe crops: one block pays at most once per this many ms.", "reload"),
    ("party.combatShare.fraction", "Party share of kill XP", "general", "dec", "0.5", "0", "1", "", "", "live",
     "Share of the kill XP each nearby party member gets (0.5 = half), at their own class skill level.", "reload"),
    ("party.combatShare.radius", "Party share range", "general", "dec", "48", "1", "512", "", "blocks", "live",
     "Members within this many blocks of the killer, in the same world, get the share.", "reload"),
    ("party.combatShare.treeBonus", "Party share gets tree bonus", "general", "bool", "true", "", "", "", "", "live",
     "The member's own skill-tree XP bonus applies to their share.", "reload"),
    ("party.combatShare.message", "Party share chat line", "general", "bool", "true", "", "", "", "", "live",
     "The '[Party] +6 Archery XP from Skyy's kill' line. Players can also hide it in /settings.", "reload"),
    ("bridge.bonus.xpSkills", "Skills Wisdom nodes boost", "general", "text", BONUS_XP_SKILLS, "", "500", "", "", "live",
     "Skills whose XP SkyyTrees Wisdom nodes raise, comma separated. Never Exploration.", "reload;check=SkillKit.checkSkills"),
    ("bridge.bonus.addxpSkills", "Granted XP that gets Wisdom", "general", "text", BONUS_ADDXP_SKILLS, "", "500", "", "", "live,adv",
     "XP other mods grant gets the Wisdom bonus only in these skills (Cooking).", "reload;check=SkillKit.checkSkills"),
    ("bridge.addxp.skills", "Skills other mods may grant", "general", "text", BRIDGE_SKILLS, "", "500", "", "", "live,adv",
     "Skills skill:fn:addxp may pay (Collections rewards, Cooking). Exploration is always allowed.", "reload;check=SkillKit.checkSkills"),
    ("bridge.maxXpPerCall", "Largest XP grant per call", "general", "int", "500000", "1", "1000000000000", "", "", "live,adv",
     "A guard against a broken mod: one grant from another mod asks for at most this much.", "reload"),
    ("bridge.maxXpPerMinute", "Granted XP per player per minute", "general", "int", "3000000", "0", "1000000000000000", "", "", "live,adv",
     "All XP other mods grant to one player in a minute (0 = no cap).", "reload"),
    # ---- levels (the list first: import / restore apply rows in this order, the two curve rows read it)
    ("levels", "XP per level, other skills (list)", "levels", "text", LEVELS_TEXT, "1", "2000", "", "", "live,danger,adv",
     "XP each level of every skill but the class skills needs, level 1 first; the count is the max level.",
     "reload;check=SkillKit.checkLevels"),
    ("levels.scale", "Level curve size, other skills", "levels", "int", "100", "10", "1000", "step=5", "%", "live,danger",
     "XP every non-class level needs as % of the default curve (110 = 10% more). Rewrites the list above.", "custom:SkillKit"),
    ("levels.max", "Max level, other skills", "levels", "int", "100", "1", "100", "step=5", "", "live,danger",
     "Cuts or extends the list (new levels follow the default curve, cut ones come back until a restart).", "custom:SkillKit"),
    # 0.4.12 (Skyy 2026-10-02 Q&A round 1, research/cloud/Class-Skill-Curve-Proposal.md section 4): the class skill table - the list first
    # (import / restore apply rows in this order, the two class curve rows read it)
    ("levels.class", "Class skill XP per level (list)", "levels", "text", CLASS_LEVELS_TEXT, "1", "2000", "", "", "live,danger,adv",
     "XP each class skill level needs (Archery, Sorcery...), level 1 first; the count is the class max.",
     "reload;check=SkillKit.checkLevels"),
    ("levels.class.scale", "Class level curve size", "levels", "int", "100", "10", "1000", "step=5", "%", "live,danger",
     "Class skill XP per level as % of Skyy's class curve. Never more than the other list asks.", "custom:SkillKit"),
    ("levels.class.max", "Class max level", "levels", "int", "100", "1", "100", "step=5", "", "live,danger",
     "Cuts or extends the class list (new levels follow the class curve; cut ones return until a restart).",
     "custom:SkillKit"),
    ("levels.class.sameAsOthers", "Class skills use the other list", "levels", "bool", "false", "", "", "", "", "live,danger",
     "On: class skills use the list of the other skills again (the old, slower curve; levels drop back).",
     "reload;confirm=on"),
    # ---- gathering: the XP rules (key families) + felled trees
    # 0.4.14 (Skyy 2026-10-02 tool levels answer (4): "Bigger boost for all 3") - the gathering pace; sickle swings (Tool-Levels-Spec question 3)
    ("gather.boost.skills", "Gathering pace skills", "gathering", "text", "Mining,Foraging,Farming", "", "300", "", "", "live",
     "Skills whose earned XP gets the early boost below (Mining, Foraging, Farming), comma separated.", "reload;check=GatherPace.checkSkills"),
    ("gather.boost.early", "Early gathering XP boost", "gathering", "dec", "3", "0.1", "100", "", "x", "live",
     "Earned XP x this up to the level below (Skyy: x3 to level 10). At least 0.1.", "reload"),
    ("gather.boost.earlyUntil", "Full boost up to level", "gathering", "int", "10", "0", "100", "", "", "live",
     "The early boost holds through this level, then eases off in a straight line.", "reload"),
    ("gather.boost.late", "Later gathering XP boost", "gathering", "dec", "1.5", "0.1", "100", "", "x", "live",
     "Earned XP x this from the level below on (Skyy: x1.5 from level 20). At least 0.1.", "reload"),
    ("gather.boost.lateFrom", "Later boost from level", "gathering", "int", "20", "0", "100", "", "", "live",
     "From this level on the later boost holds. Granted XP (Collections rewards) never gets a boost.", "reload"),
    ("farming.sickle.enabled", "Sickle swings pay Farming XP", "gathering", "bool", "true", "", "", "", "", "live",
     "A crop in its final growth stage that a sickle harvests pays Farming XP + a double-drop roll, once.", "reload"),
    ("farming.sickle.items", "Sickle item ids", "gathering", "text", "Tool_Sickle_", "", "500", "", "", "live,adv",
     "Item id starts that count as sickles, comma separated.", "reload;check=Sickle.checkItems"),
    ("block", "XP by exact block id", "gathering", "table", "", "", "", "text;type;Skill:XP or none", "", "live",
     "Exact id -> Mining:5 (Mining, Foraging or Farming) or none. Beats every other rule.", "reload;check=SkillKit.checkRule"),
    ("prefix", "XP by start of block id", "gathering", "table", "", "", "", "text;type;Skill:XP or none", "", "live",
     "Ore_Iron -> Mining:8. The longest matching start or end of an id wins.", "reload;check=SkillKit.checkRule"),
    ("suffix", "XP by end of block id", "gathering", "table", "", "", "", "text;type;Skill:XP or none", "", "live",
     "_Trunk -> Foraging:6. The longest matching start or end of an id wins.", "reload;check=SkillKit.checkRule"),
    ("fell.xpFactor", "Felled log XP", "gathering", "dec", "1.0", "0", "5", "", "x", "live",
     "A log that falls with the tree pays its hand-break Foraging XP times this.", "reload"),
    ("fell.leaves", "Felled leaves pay", "gathering", "bool", "true", "", "", "", "", "live",
     "Leaves that fall with the tree pay too (their XP times the leaf factor).", "reload"),
    ("fell.leafXpFactor", "Felled leaf XP", "gathering", "dec", "1.0", "0", "5", "", "x", "live",
     "A falling leaf pays its hand-break XP times this.", "reload"),
    ("fell.needLeaves", "Felled tree needs leaves", "gathering", "bool", "true", "", "", "", "", "live",
     "Only a tree touching natural leaves pays (never a log wall or a placed log tower).", "reload"),
    ("fell.underTrunk", "Digging under a trunk fells", "gathering", "bool", "true", "", "", "", "", "live",
     "Breaking the block under a trunk fells the tree and pays the same.", "reload"),
    ("fell.doubleDrops", "Felled logs roll double drops", "gathering", "bool", "true", "", "", "", "", "live",
     "Each falling log rolls the Foraging double-drop perk.", "reload"),
    ("fell.collections", "Felled logs count in Collections", "gathering", "bool", "true", "", "", "", "", "live",
     "Each falling log counts in SkyyCollections (source skills:felled).", "reload"),
    ("fell.nodes", "Felled logs roll tree nodes", "gathering", "bool", "true", "", "", "", "", "live",
     "Each falling log rolls the SkyyTrees per-log nodes (skill:on:felled).", "reload"),
    ("fell.message", "Tree felled chat line", "gathering", "bool", "true", "", "", "", "", "live",
     "'Tree felled: 19 logs (+156 Foraging XP)'. Players can hide it in /settings (Skill XP gains).", "reload"),
    ("fell.disabledWorlds", "No felled XP in these worlds", "gathering", "text", "", "", "2000", "", "", "live",
     "Comma list of exact world names where felled trees never pay.", "reload"),
    ("fell.extraTrees", "Also apple trees + extra trunks", "gathering", "bool", "false", "", "", "", "", "live",
     "Also pay apple fruit trees and the Bamboo / Ice Trunk_Full blocks Hytale's tree lists miss.", "reload"),
    ("placed.skipSaplings", "Planted saplings count as natural", "gathering", "bool", "true", "", "", "", "", "live",
     "A planted sapling is not marked as placed, so a replanted tree's base log pays.", "reload"),
    ("collections.doubleDrops", "Double drops count in Collections", "gathering", "bool", "false", "", "", "", "", "live",
     "Items from the double-drop perk also count in SkyyCollections (source skills:double).", "reload"),
    ("fell.radius", "Felled search: sideways", "gathering", "int", "8", "1", "16", "", "blocks", "live,adv",
     "How far sideways from the cut a tree's logs are searched.", "reload"),
    ("fell.height", "Felled search: height", "gathering", "int", "64", "1", "128", "", "blocks", "live,adv",
     "How far above the cut a tree's logs are searched.", "reload"),
    ("fell.maxLogs", "Felled search: most logs", "gathering", "int", "256", "1", "1024", "", "", "live,adv",
     "Most logs one felled tree can pay.", "reload"),
    ("fell.maxLeaves", "Felled search: most leaves", "gathering", "int", "384", "0", "2048", "", "", "live,adv",
     "Most leaves one felled tree can pay.", "reload"),
    ("fell.maxReads", "Felled search: block reads", "gathering", "int", "8000", "100", "100000", "", "", "live,adv",
     "Block reads per tree search (a server-load guard).", "reload"),
    ("fell.maxSnapshotsPerSecond", "Tree searches per second", "gathering", "int", "10", "1", "100", "", "", "live,adv",
     "Per player (a server-load guard).", "reload"),
    ("fell.maxWatchesPerPlayer", "Falling trees per player", "gathering", "int", "4", "1", "64", "", "", "live,adv",
     "Trees one player can have falling at the same time.", "reload"),
    ("fell.maxWatches", "Falling trees on the server", "gathering", "int", "64", "1", "1024", "", "", "live,adv",
     "Trees falling at the same time, all players together.", "reload"),
    ("fell.pollMs", "Falling tree checked every", "gathering", "int", "200", "50", "1000", "", "ms", "live,adv",
     "How often a falling tree is checked.", "reload"),
    ("fell.quietMs", "Falling tree done when still for", "gathering", "int", "3000", "500", "10000", "", "ms", "live,adv",
     "A falling tree that stays still this long is finished.", "reload"),
    ("fell.maxWatchMs", "Falling tree longest watch", "gathering", "int", "60000", "1000", "600000", "", "ms", "live,adv",
     "A falling tree is never watched longer than this.", "reload"),
    ("fell.memoryMs", "Remember who felled a tree", "gathering", "int", "60000", "0", "600000", "", "ms", "live,adv",
     "For other mods (skill:fn:felledBy).", "reload"),
    ("fell.debug", "Felled trees debug log", "gathering", "bool", "false", "", "", "", "", "live,adv",
     "One server-log line per tree search and per felled tree.", "reload"),
    # ---- combat (class skill XP per kill)
    # 0.4.10 (Skyy 2026-10-01): every XP gain into a class skill x this (SkillCfg.classXp) - after combat.max and the heal cap
    ("classSkill.xpMultiplier", "Class skill XP multiplier", "combat", "dec", CLS_MULT_DEF, "0", "100", "", "x", "live",
     "Kill and party-share class skill XP times this, on top of the XP multiplier. Not Priest heals.", "reload"),
    ("combat.perHealth", "Combat XP per max health", "combat", "dec", "0.2", "0", "1000", "", "", "live",
     "Class XP per NPC kill = its max health x this, kept between the minimum and maximum below.", "reload"),
    ("combat.min", "Combat XP minimum", "combat", "int", "1", "0", "1000000000", "", "", "live",
     "Least class XP one kill pays. Keep it at or below the maximum, or every kill pays the maximum.", "reload"),
    ("combat.max", "Combat XP maximum", "combat", "int", "500", "0", "1000000000", "", "", "live",
     "Most class XP one kill pays before the class skill XP multiplier (an NPC role's own XP beats it).", "reload"),
    ("combat.default", "Combat XP if health unknown", "combat", "int", "5", "0", "1000000000", "", "", "live",
     "Used when the NPC's max health cannot be read.", "reload"),
    ("combat.role", "Combat XP by NPC role", "combat", "table", "", "0", "1000000000", "int;type;XP", "", "live",
     "Exact XP for one NPC role. The server log names each new role on its first kill.", "reload"),
    ("combat.classWeaponOnly", "Only class weapons earn XP", "combat", "bool", "true", "", "", "", "", "live",
     "On: only the class's own weapons earn combat XP. Off: anything SkyyClasses lets the class use.", "reload"),
    # 0.4.14 kill XP by mob level (SkyyMobs mob:fn:level): x (1 + levelBonus x (level - 1)) x the gap against your class skill
    ("combat.levelBonus", "Kill XP per mob level", "combat", "dec", "0.05", "0", "10", "", "", "live",
     "Kill XP x (1 + this x (mob level - 1)) with SkyyMobs levels. 0.05 = +5% a level.", "reload"),
    ("combat.gap.free", "Level gap with no change", "combat", "int", "5", "0", "100", "", "", "live",
     "A mob up to this many levels above or below your class skill pays no gap change.", "reload"),
    ("combat.gap.above", "Higher mob: extra XP a level", "combat", "dec", "0.05", "0", "10", "", "", "live",
     "Each level a mob is past that gap above you adds this (0.05 = +5%).", "reload"),
    ("combat.gap.max", "Higher mob: XP cap", "combat", "dec", "3.5", "1", "100", "", "x", "live",
     "The gap never pays more than this times (3.5 = +250%).", "reload"),
    ("combat.gap.below", "Lower mob: XP lost a level", "combat", "dec", "0.05", "0", "10", "", "", "live",
     "Each level a mob is past that gap below you takes this away (0.05 = -5%).", "reload"),
    ("combat.gap.min", "Lower mob: least XP", "combat", "dec", "0.1", "0", "1", "", "x", "live",
     "The gap never pays less than this share (0.1 = 10%).", "reload"),
    # 0.4.4 Divinity XP from Priest heals (skill:fn:healxp, SkyyClasses 0.1.6); kills pay Fury / Divinity through the rows above
    # 0.4.11 (LOCKED Skyy 2026-10-01): the three heal rows are the FINAL heal XP (not multiplied by the class skill XP multiplier)
    ("divinity.healXpPerHp", "Divinity XP per HP healed on others", "combat", "dec", HEAL_PER_HP_DEF, "0", "100", "", "", "live",
     "XP the Priest gets per 1 HP healed on other party members. Not multiplied by class skill XP.", "reload"),
    # 0.4.6 (LOCKED Skyy 2026-09-25): self-heals pay their own rate, inside the same per-minute cap
    ("divinity.healXpPerHpSelf", "Divinity XP per HP healed on self", "combat", "dec", HEAL_SELF_DEF, "0", "100", "", "", "live",
     "XP the Priest gets per 1 HP healed on themself. Not multiplied by class skill XP. Counts in the cap.", "reload"),
    ("divinity.healXpMaxPerMinute", "Divinity heal XP per minute", "combat", "int", HEAL_MAX_DEF, "0", "1000000000", "", "", "live",
     "Most heal XP a Priest gets in 60 s (0 = no limit). Not multiplied by class skill XP. No kill XP.", "reload"),
    # ---- acrobatics (+ Double Jump)
    ("acro.sprintXpPerBlock", "XP per block sprinted", "acrobatics", "dec", "0.25", "0", "100", "", "", "live",
     "Measured from the server position; teleports and launches pay nothing.", "reload"),
    ("acro.runXpPerBlock", "XP per block run", "acrobatics", "dec", "0.15", "0", "100", "", "", "live", "", "reload"),
    ("acro.walkXpPerBlock", "XP per block walked", "acrobatics", "dec", "0.05", "0", "100", "", "", "live",
     "Walking or sneaking.", "reload"),
    ("acro.maxSpeed", "Fastest paid movement", "acrobatics", "dec", "30", "5", "1000", "", "", "live,adv",
     "Blocks per second; a faster move (launch, lag burst) pays nothing.", "reload"),
    ("acro.teleportBlocks", "Teleport guard", "acrobatics", "dec", "8", "2", "1000", "", "blocks", "live,adv",
     "A move longer than this in one tick pays nothing.", "reload"),
    ("acro.jumpXp", "XP per jump", "acrobatics", "dec", "2", "0", "100000", "", "", "live",
     "At most one paid jump per cooldown, and only after moving (no XP for jumping in place).", "reload"),
    ("acro.jumpCooldownMs", "Paid jump cooldown", "acrobatics", "int", "800", "200", "600000", "", "ms", "live,adv", "", "reload"),
    ("acro.jumpMinMove", "Move between paid jumps", "acrobatics", "dec", "2.0", "0", "1000", "", "blocks", "live,adv", "", "reload"),
    ("acro.fallDamageXp", "XP per point of fall damage", "acrobatics", "dec", "10", "0", "100000", "", "", "live",
     "Only survived falls that hurt pay (counted as if you had 100 max health).", "reload"),
    ("acro.fallXpMax", "Most XP per landing", "acrobatics", "dec", "2000", "0", "1000000000", "", "", "live", "", "reload"),
    ("acro.fallMaxXpPerMinute", "Fall XP per minute cap", "acrobatics", "dec", "3000", "0", "1000000000", "", "", "live",
     "All fall XP in any 60 seconds (0 = no fall XP). Its own cap.", "reload"),
    # 0.4.14 roll landings (Skyy 2026-10-02): the fall's unreduced XP + this share; 0 = 0.4.13 (a full roll paid nothing)
    ("acro.rollBonus", "Extra XP for a rolled landing", "acrobatics", "dec", "0.5", "0", "10", "", "", "live",
     "Crouch to roll as you land: the fall's XP + this share (0.5 = +50%). 0 = rolls pay as before.", "reload"),
    ("acro.dodgeXp", "XP per dodge", "acrobatics", "dec", "3", "0", "100000", "", "", "live", "", "reload"),
    ("acro.dodgeCooldownMs", "Paid dodge cooldown", "acrobatics", "int", "400", "100", "600000", "", "ms", "live,adv", "", "reload"),
    ("acro.maxXpPerMinute", "Move XP per minute cap", "acrobatics", "dec", "240", "0", "1000000000", "", "", "live",
     "Running, jumping and dodging XP together in any 60 seconds.", "reload"),
    ("acro.feedbackMs", "Acrobatics XP line every", "acrobatics", "int", "30000", "2000", "3600000", "", "ms", "live,adv",
     "The +Acrobatics XP chat line shows at most once per this many ms.", "reload"),
    ("acro.speedPerLevel", "Speed per level", "acrobatics", "dec", "0.01", "0", "10", "", "", "live",
     "Share of vanilla speed added per Acrobatics level (0.01 = +1%).", "reload"),
    ("acro.jumpBlocksPerLevel", "Jump height per level", "acrobatics", "dec", "0.015", "0", "10", "", "blocks", "live", "", "reload"),
    ("acro.fallReductionPerLevel", "Less fall damage per level", "acrobatics", "dec", "0.005", "0", "1", "", "", "live",
     "0.005 = 0.5% less fall damage per level, up to the cap below.", "reload"),
    ("acro.fallReductionMax", "Fall damage reduction cap", "acrobatics", "dec", "0.8", "0", "1", "", "", "live", "", "reload"),
    ("acro.dodgeBoost", "Dodge push bonus", "acrobatics", "bool", "true", "", "", "", "", "live",
     "Off: no extra dodge push (dodge XP stays).", "reload"),
    ("acro.dodgeForce", "Dodge push force", "acrobatics", "dec", "13", "0", "1000", "", "", "live,adv",
     "The vanilla dodge force is 13.", "reload"),
    ("acro.dodgeBoostPerLevel", "Dodge push per level", "acrobatics", "dec", "0.004", "0", "1", "", "", "live", "", "reload"),
    ("acro.dodgeBoostMax", "Dodge push cap", "acrobatics", "dec", "0.5", "0", "2", "", "", "live", "", "reload"),
    ("acro.treeDodgeMax", "Tree dodge nodes cap", "acrobatics", "dec", "0.25", "0", "2", "", "", "live",
     "Most dodge push the Acrobatics tree's dodge nodes can add.", "reload"),
    ("acro.doubleJump.trigger", "Double Jump key", "acrobatics", "choice", "jump", "", "", "crouch|Crouch,jump|Jump,both|Both", "",
     "live", "LOCKED 2026-09-25: jump again in mid-air. Crouch stays a choice. Jump needs the client to report it.", "reload"),
    ("acro.doubleJump.maxJumps", "Air jumps per airtime", "acrobatics", "int", "1", "1", "5", "", "", "live",
     "They recharge when you land, climb, swim or touch water.", "reload"),
    ("acro.doubleJump.maxFraction", "Air jump height cap", "acrobatics", "dec", "1.0", "0", "1.5", "", "", "live",
     "A share of the player's own jump height; the tree node's value is capped here.", "reload"),
    ("acro.doubleJump.maxBlocks", "Air jump height cap in blocks", "acrobatics", "dec", "3.5", "0.5", "10", "", "blocks", "live",
     "", "reload"),
    ("acro.doubleJump.forwardPush", "Air jump forward push", "acrobatics", "dec", "2.0", "0", "10", "", "", "live",
     "Extra blocks per second along the way you are moving.", "reload"),
    ("acro.doubleJump.stamina", "Air jump Stamina cost", "acrobatics", "dec", "2.0", "0", "1000", "", "", "live",
     "Too little Stamina = no air jump (the charge is kept).", "reload"),
    ("acro.doubleJump.staminaRegenDelay", "Stamina regen pause", "acrobatics", "dec", "0.3", "0", "10", "", "s", "live,adv",
     "0 = off.", "reload"),
    ("acro.doubleJump.cooldownMs", "Air jump cooldown", "acrobatics", "int", "250", "0", "60000", "", "ms", "live,adv", "", "reload"),
    ("acro.doubleJump.minAirMs", "Air time before an air jump", "acrobatics", "int", "100", "0", "5000", "", "ms", "live,adv",
     "", "reload"),
    ("acro.doubleJump.maxFallSpeed", "No air jump falling faster than", "acrobatics", "dec", "0", "-1000", "1000", "", "", "live,adv",
     "Blocks per second. 0 = the world's roll speed (vanilla 21), below 0 = no limit.", "reload"),
    ("acro.doubleJump.xp", "Acrobatics XP per air jump", "acrobatics", "dec", "0", "0", "1000", "", "", "live",
     "Counts against the move XP per minute cap.", "reload"),
    ("acro.doubleJump.fx", "Air jump sound + particles", "acrobatics", "bool", "true", "", "", "", "", "live", "", "reload"),
    ("acro.doubleJump.debug", "Double Jump debug chat", "acrobatics", "bool", "false", "", "", "", "", "live,adv",
     "Admins (skyyskills.admin) see a chat line per crouch / jump edge in mid-air.", "reload"),
    # ---- perks (the per-level flat layer)
    ("perk.doubleDropMax", "Double drop chance cap", "perks", "dec", "1.0", "0", "1", "", "", "live",
     "The double-drop chance never goes above this (1 = 100%), tree Fortune included.", "reload"),
    ("perk.doubleDropMessage", "Double drop chat line", "perks", "bool", "true", "", "", "", "", "live",
     "'Double drop x3!'. Players can also hide it in /settings.", "reload"),
]
# perk.<skill>.healthPerLevel / staminaPerLevel / manaPerLevel for all nine perk rows (PerkCfg.KEYS order, PerkCfg defaults), then the
# double-drop pair for the three gathering skills and the class damage pair; rows whose key is not in the default file (default 0) are adv
_PK = [("mining", "Mining"), ("foraging", "Foraging"), ("farming", "Farming"), ("combat", "Combat"), ("acrobatics", "Acrobatics"),
       ("alchemy", "Alchemy"), ("smithing", "Smithing"), ("cooking", "Cooking"), ("exploration", "Exploration")]
_PDEF = {"healthPerLevel": ["0", "0.1", "0.25", "0.1", "0", "0", "0", "0", "0"],
         "staminaPerLevel": ["0.05", "0", "0", "0", "0", "0", "0", "0", EXPL_STA_DEF],
         "manaPerLevel": ["0", "0", "0", "0", "0", "0.2", "0", "0", "0"]}
_PWORD = {"healthPerLevel": "health", "staminaPerLevel": "stamina", "manaPerLevel": "mana"}
_PDD = {"mining": ("0.005", ""), "foraging": ("0.005", "_Trunk"), "farming": ("0.005", "")}
for _i, (_k, _lab) in enumerate(_PK):
    _who = "your class skill" if _k == "combat" else _lab
    for _st in ("healthPerLevel", "staminaPerLevel", "manaPerLevel"):
        _key = "perk.%s.%s" % (_k, _st)
        _d = _PDEF[_st][_i]
        _in = ("\n" + _key + "=") in ("\n" + DEFAULTS)
        _help = "Max %s added per %s level (all skills add up)." % (_PWORD[_st], _who)
        if _key == "perk.exploration.staminaPerLevel":   # SkyyExploration 0.2.1+ reads this row over config:fn:SkyySkills op get (spec 4.18;
            # 0.2 still shows its own display.staminaPerLevel copy): the help must hold for both until the coordinator pins 0.2.1
            _help = "Max stamina per Exploration level. SkyyExploration 0.2.1+ shows this value on its /explore card."
        CFG_ROWS.append((_key, "%s: max %s per level" % (_lab, _PWORD[_st]), "perks", "dec", _d, "0", "10", "", "", "live" if _in else "live,adv",
                         _help, "reload"))
    if _k in _PDD:
        CFG_ROWS.append(("perk.%s.doubleDropPerLevel" % _k, "%s: double drop per level" % _lab, "perks", "dec", _PDD[_k][0], "0", "1", "", "",
                         "live", "Chance per level that a block paying %s XP drops twice (0.005 = 0.5%%)." % _lab, "reload"))
        CFG_ROWS.append(("perk.%s.doubleDropOnly" % _k, "%s: double drops only for" % _lab, "perks", "text", _PDD[_k][1], "", "2000", "", "",
                         "live", "Comma list of id parts: only blocks whose id contains one can double. Empty = all.", "reload"))
    if _k == "combat":
        CFG_ROWS.append(("perk.combat.damagePerLevel", "Class weapon damage per level", "perks", "dec", "0.002", "0", "1", "", "", "live",
                         "Extra damage with class weapons per class level (0.002 = +0.2%, +20% at 100).", "reload"))
        CFG_ROWS.append(("perk.combat.damageVsPlayers", "Class damage bonus vs players", "perks", "bool", "false", "", "", "", "",
                         "live,danger", "On: the class damage bonus also applies when hitting players.", "reload;confirm=on"))
        # 0.4.5 crossbows stay loaded (research/Crossbow-Loaded-Spec.md 3.3), the Archery level-5 reward
        CFG_ROWS.append(("perk.archery.keepLoaded.level", "Crossbows stay loaded from Archery", "perks", "int", "5", "0", "100", "", "", "live",
                         "Archery level that unlocks it (5 = the level-5 reward, 0 = every Archer).", "reload"))
        CFG_ROWS.append(("perk.archery.keepLoaded.items", "Crossbow ids (stay loaded)", "perks", "text", "Weapon_Crossbow_", "", "500", "", "",
                         "live,adv", "Item id starts that count as crossbows, comma separated. More Crossbow Tiers is included.",
                         "reload;check=XbowCfg.checkItems"))
        CFG_ROWS.append(("perk.archery.keepLoaded.delayTicks", "Stay-loaded restore delay", "perks", "int", "3", "3", "20", "", "", "live,adv",
                         "Server ticks after switching back before the bolts return (3 = about 0.1 s).", "reload"))
        CFG_ROWS.append(("perk.archery.keepLoaded.debug", "Stay-loaded debug lines", "perks", "bool", "false", "", "", "", "", "live,adv",
                         "On: admins see a chat line each time a crossbow load is kept or put back (for testing).", "reload"))
        # 0.4.6 (LOCKED Skyy 2026-09-25): the big-arrow meter, the load sound and the chat hint (each player can turn them off in /settings)
        CFG_ROWS.append(("perk.archery.keepLoaded.meter", "Stay-loaded keeps the big-arrow meter", "perks", "bool", "true", "", "", "", "", "live",
                         "On: the big-arrow (Signature) meter comes back with the bolts. Players can turn it off in /settings.", "reload"))
        CFG_ROWS.append(("perk.archery.keepLoaded.sound", "Sound when the bolts go back in", "perks", "text", XBOW_SOUND_DEF, "", "120", "", "",
                         "live,adv", "A sound event id (default: the vanilla crossbow load). Empty = no sound.",
                         "reload;check=XbowCfg.checkSound"))
        CFG_ROWS.append(("perk.archery.keepLoaded.hint", "Chat hint when the bolts go back in", "perks", "bool", "true", "", "", "", "", "live",
                         "'Crossbow reloaded - 6 bolts back in'. Players can turn it off in /settings.", "reload"))
# 0.4.6 (research/Overall-Level-Spec.md 4.9): the "Overall and Mana" category
CFG_ROWS += [
    ("mana.base", "Base Mana for everyone", "overall", "dec", "10", "0", "10000", "", "", "live",
     "Max Mana every player starts with, unless Base Mana by class lists their class (vanilla gives 0).", "reload"),
    # 0.4.8 (Skyy 2026-09-30): the per-class table replaces mana.magicBase + mana.magicClasses (ManaMig moves an existing file once)
    ("mana.classBase", "Base Mana by class", "overall", "table", "", "0", "10000", "dec;type;Base Mana", "", "live",
     "Max Mana a listed class starts with, instead of the base above (Mage 30 = 3 staff casts).", "reload;check=OverallCfg.checkClassBase"),
    # 0.4.15 (research/SkyyArmory-Spec.md 15.4, Skyy 2026-10-03): max Mana per level of the class's own skill (Priest 5, Mage 10)
    ("mana.classPerLevel", "Max Mana per class level", "overall", "table", "", "0", "100", "dec;type;Mana per level", "", "live",
     "Max Mana a listed class gains per level of its own class skill (Priest: Divinity, Mage: Sorcery).", "reload;check=ClassMana.checkEntry"),
    # 0.4.8: the spell cost divisor is fixed in the jar (the item overrides are generated at build time) - shown, never edited
    ("spell.manaDivisor", "Spell Mana costs divided by", "overall", "int", str(SPELL_DIVISOR), "", "", "", "x", "ro",
     "Fixed in the jar: vanilla Mana / this (wand 5, staff 10, spellbook 20). SkyyArmory sets its own.", "custom:SkillKit"),
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
    # 0.4.12 (Skyy 2026-10-02 Q&A rounds 1-2): Mana refills in combat at this % of (vanilla + Mana Regen boosts); 0 = vanilla
    ("mana.regen.inCombat", "In-combat Mana regen", "overall", "int", MREG_DEF, "0", "100", "step=5", "%", "live",
     "Mana refill for 6 s after you take damage, as % of the normal refill + boosts. 0 = vanilla (none).", "reload"),
    ("mana.regen.show", "Mana Regen: show mine", "overall", "action", "", "", "", "Show my Mana Regen", "", "live",
     "Your Mana Regen boosts (other mods register them, none yet) and the refill in and out of combat.",
     "action:ManaRegen.showAction"),
]
CFG_ROWS += [
    # ---- crafting: alchemy + smithing
    ("alchemy.xp", "Alchemy XP per brew", "crafting", "table", "", "0", "1000000000000", "int;both;XP", "", "live",
     "Alchemy XP per finished Alchemy Bench craft, by output item (0 = none).", "reload;entry=item"),
    ("alchemy.tierXp", "Alchemy XP, unlisted recipes", "crafting", "text", ",".join(str(x) for x in ALCH_TIER), "1", "200", "", "", "live",
     "By bench tier I to V, comma separated, for Alchemy Bench recipes not in the table.", "reload;check=SkillKit.checkTier"),
    ("perk.alchemy.durationPerLevel", "Potion duration per level", "crafting", "dec", "0.01", "0", "10", "", "", "live",
     "Potion effects you drink last longer per Alchemy level (0.01 = +1%).", "reload"),
    ("perk.alchemy.durationMax", "Potion duration cap", "crafting", "dec", "1.0", "0", "10", "", "", "live",
     "The duration bonus never goes above this (1 = +100%).", "reload"),
    ("perk.alchemy.extend", "Effects that last longer", "crafting", "text", ",".join(ALCH_EXTEND), "", "2000", "", "", "live,adv",
     "Effect ids the duration perk may grow (instant heals cannot), comma separated.", "reload"),
    ("perk.alchemy.extraPotionPerLevel", "Extra potion chance per level", "crafting", "dec", "0.002", "0", "1", "", "", "live",
     "Chance per Alchemy level to brew one extra potion (0.002 = 0.2%).", "reload"),
    ("perk.alchemy.extraPotionMax", "Extra potion chance cap", "crafting", "dec", "0.25", "0", "1", "", "", "live", "", "reload"),
    ("perk.alchemy.extraPotionOnly", "Extra potion only for", "crafting", "text", "Potion_,Weapon_Bomb_", "", "2000", "", "", "live,adv",
     "Output id starts that can give an extra potion, comma separated.", "reload"),
    ("perk.alchemy.extraPotionNever", "Never an extra potion for", "crafting", "text", "Potion_Empty", "", "2000", "", "", "live,adv",
     "Output id starts that never give one, comma separated.", "reload"),
    ("smithing.vanillaFurnace", "Vanilla Furnace pays Smithing", "crafting", "bool", "true", "", "", "", "", "live",
     "Off: only the /craft Furnace tab (SkyySacks) pays Smithing XP.", "reload"),
    ("smithing.xp", "Smithing XP per smelted item", "crafting", "table", "", "0", "1000000000000", "int;both;XP", "", "live",
     "Smithing XP per finished smelted item, by output item (0 = none).", "reload;entry=item"),
    ("smithing.oreFactor", "Unlisted bar: ore XP factor", "crafting", "dec", "1.0", "0", "100", "", "x", "live",
     "An unlisted Ingredient_Bar_* pays the Mining XP of its ore times this (at least 1).", "reload"),
    ("smithing.smeltDefault", "Other smelted items", "crafting", "int", "1", "0", "1000000000", "", "", "live",
     "Smithing XP per item for every other Furnace output (0 = none).", "reload"),
]
# defaults = today's behaviour: every scalar row's default equals the default xp.properties line; the rows absent from it are exactly the
# 21 zero perk stats (PerkCfg's code default for them is 0.0)
from decimal import Decimal as _Dec
_dp = {}
for _ln in DEFAULTS.split("\n"):
    _t = _ln.strip()
    if _t and not _t.startswith("#") and "=" in _t:
        _dp[_t.split("=", 1)[0].strip()] = _t.split("=", 1)[1].strip()
_absent = []
for _r in CFG_ROWS:
    if _r[3] in ("table", "link", "action") or not _r[11].startswith("reload"):
        continue
    if _r[0] not in _dp:
        _absent.append(_r[0])
        assert _r[3] == "dec" and _r[4] == "0" and _r[0].startswith("perk.") and "adv" in _r[9], "row %s: not in the default file" % _r[0]
        continue
    _fv = _dp[_r[0]]
    if _r[3] in ("int", "dec"):
        assert _Dec(_fv) == _Dec(_r[4]), "row %s default %s != file %s" % (_r[0], _r[4], _fv)
    else:
        assert _fv == _r[4], "row %s default %r != file %r" % (_r[0], _r[4], _fv)
assert len(_absent) == 21, _absent
for _tk, _pfx in (("block", "block."), ("prefix", "prefix."), ("suffix", "suffix."), ("alchemy.xp", "alchemy.xp."), ("smithing.xp", "smithing.xp."),
                 ("mana.classBase", "mana.classBase."), ("mana.classPerLevel", "mana.classPerLevel.")):   # 0.4.15: + the class level table
    assert any(_k.startswith(_pfx) for _k in _dp), "table %s has no default entries" % _tk
print("config rows: %d (%d tables), %d not in the default file (zero perk stats, adv)" % (len(CFG_ROWS), sum(1 for _r in CFG_ROWS if _r[3] == "table"), len(_absent)))
assert len(CFG_ROWS) == 196, ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows (Overall-Level-Spec 4.9) + divinity.healXpPerHpSelf + "
                              "3 crossbow extras (meter, sound, hint); 0.4.8: - mana.magicBase / mana.magicClasses + the mana.classBase "
                              "table + the read-only spell.manaDivisor; 0.4.10: + classSkill.xpMultiplier; 0.4.12: + the 4 class curve "
                              "rows + mana.regen.inCombat + the mana.regen.show action; 0.4.14: + the 15 rows of N14_L; 0.4.15: + the "
                              "mana.classPerLevel table, got %d" % len(CFG_ROWS))   # 0.4.6 / 0.4.8 / 0.4.10 / 0.4.12 / 0.4.14 / 0.4.15
# 0.4.14: every N14_L key is a row once, its default = the default file = the appended block; their categories / places
_r14 = dict((_r[0], _r) for _r in CFG_ROWS)
for _k in N14_KEYS:
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _dp.get(_k) is not None and ("\n" + _k + "=" + _dp[_k] + "\n") in ("\n" + N14_DEFAULTS), _k
    assert _r14[_k][4] == _dp[_k] or _Dec(_r14[_k][4]) == _Dec(_dp[_k]), _k
assert [_r14[_k][2] for _k in N14_KEYS] == ["parts", "combat", "combat", "combat", "combat", "combat", "combat", "acrobatics"] + ["gathering"] * 7
_kk14 = [_r[0] for _r in CFG_ROWS]
assert _kk14[_kk14.index("combat.classWeaponOnly") + 1:_kk14.index("combat.classWeaponOnly") + 7] == N14_KEYS[1:7]
assert _kk14[_kk14.index("acro.fallMaxXpPerMinute") + 1] == "acro.rollBonus" and _kk14[_kk14.index("divinity.healXp.enabled") + 1] == "combat.levelXp.enabled"
assert _kk14[_kk14.index("block") - 7:_kk14.index("block")] == N14_KEYS[8:]
# 0.4.12: the new keys once each; levels.class / sameAsOthers / mana.regen.inCombat in the default file (= the row default) and in their
# appended blocks; the class rows right after the three general curve rows, the list first
_k12 = [_r[0] for _r in CFG_ROWS]
assert _k12[_k12.index("levels"):_k12.index("levels") + 7] == ["levels", "levels.scale", "levels.max", "levels.class", "levels.class.scale",
                                                                 "levels.class.max", "levels.class.sameAsOthers"], _k12[_k12.index("levels"):][:7]
for _k, _blk12 in (("levels.class", CURVE_DEFAULTS), ("levels.class.sameAsOthers", CURVE_DEFAULTS), ("mana.regen.inCombat", MREG_DEFAULTS)):
    _rw = [_r for _r in CFG_ROWS if _r[0] == _k]
    assert len(_rw) == 1 and _dp.get(_k) == _rw[0][4] and ("\n" + _k + "=" + _rw[0][4] + "\n") in ("\n" + _blk12), _k
assert sum(1 for _r in CFG_ROWS if _r[0] in ("levels.class.scale", "levels.class.max", "mana.regen.show")) == 3
assert [_r for _r in CFG_ROWS if _r[0] == "levels.class"][0][4] == CLASS_LEVELS_TEXT and _dp.get("levels.class") == CLASS_LEVELS_TEXT
# 0.4.10: the new key once in CFG_ROWS (Combat tab, the first combat row), in the default file and in its own appended block (an old file
# gets it too), and nowhere else; row / code / file default agree
assert sum(1 for _r in CFG_ROWS if _r[0] == "classSkill.xpMultiplier") == 1 and _dp.get("classSkill.xpMultiplier") == CLS_MULT_DEF \
    and ("\nclassSkill.xpMultiplier=" + CLS_MULT_DEF + "\n") in ("\n" + CLS_DEFAULTS)
assert [_r[0] for _r in CFG_ROWS if _r[2] == "combat"][0] == "classSkill.xpMultiplier"
assert [_r for _r in CFG_ROWS if _r[0] == "classSkill.xpMultiplier"][0][3:10] == ("dec", CLS_MULT_DEF, "0", "100", "", "x", "live")
for _k in ("perk.archery.keepLoaded.enabled", "perk.archery.keepLoaded.level", "perk.archery.keepLoaded.items",
           "perk.archery.keepLoaded.delayTicks", "perk.archery.keepLoaded.debug"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp and ("\n" + _k + "=") in ("\n" + XBOW_DEFAULTS), _k
for _k in ("divinity.healXp.enabled", "divinity.healXpPerHp", "divinity.healXpMaxPerMinute"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp, _k
# 0.4.11: row default = file default = HealMig's new value for each heal key; the default file holds the marker once, above the Divinity block
for _k, _o, _n, _w in HEAL_MG:
    assert [_r[4] for _r in CFG_ROWS if _r[0] == _k] == [_n] and _dp.get(_k) == _n and _o != _n, _k
assert L.count(HEAL_MARK) == 1 and L[L.index(HEAL_MARK) + 1] == DIV_L[0] and HEAL_MARK not in DIV_L + DIVS_L + CLS_L
# 0.4.6: every new key once in CFG_ROWS, in the default file and in its own appended block (so an old file gets it too)
for _k in ("mana.base.enabled", "mana.base", "overall.enabled", "overall.skills", "overall.healthPerLevel",
           "overall.manaPerLevel", "overall.healOnLevelUp", "overall.chat"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp and ("\n" + _k + "=") in ("\n" + OVL_DEFAULTS), _k
# 0.4.8: the old pair is gone from the rows and the default file; the table's default entries are in the default file AND in the block
# appended to a pre-0.4.6 file; the read-only divisor row has no file line
for _k in ("mana.magicBase", "mana.magicClasses"):
    assert not any(_r[0] == _k for _r in CFG_ROWS) and _k not in _dp and ("\n" + _k + "=") not in ("\n" + OVL_DEFAULTS), _k
for _cb, _cv in CLASS_BASE_DEF:
    assert _dp.get("mana.classBase." + _cb) == str(_cv) and ("\nmana.classBase.%s=%d\n" % (_cb, _cv)) in ("\n" + OVL_DEFAULTS), _cb
assert sorted(_k for _k in _dp if _k.startswith("mana.classBase.")) == sorted("mana.classBase." + _c for _c, _v in CLASS_BASE_DEF)
assert sum(1 for _r in CFG_ROWS if _r[0] == "mana.classBase") == 1 and sum(1 for _r in CFG_ROWS if _r[0] == "spell.manaDivisor") == 1
# 0.4.15: the class level table - its default entries in the default file AND in the CMAN block (ClassManaMig appends it to an old file), right
# after mana.classBase in the rows, its classes real classes in SkillDefs.CLASSES order; no other row or table key inside its family
for _cc, _cv in CLASS_MANA_DEF:
    assert _dp.get("mana.classPerLevel." + _cc) == str(_cv) and ("\nmana.classPerLevel.%s=%d\n" % (_cc, _cv)) in ("\n" + CMAN_DEFAULTS), _cc
assert sorted(_k for _k in _dp if _k.startswith("mana.classPerLevel.")) == sorted(CMAN_KEYS)
_k15 = [_r[0] for _r in CFG_ROWS]
assert _k15.count("mana.classPerLevel") == 1 and _k15[_k15.index("mana.classBase") + 1] == "mana.classPerLevel"
assert [_r for _r in CFG_ROWS if _r[0] == "mana.classPerLevel"][0][2:10] == ("overall", "table", "", "0", "100", "dec;type;Mana per level", "", "live")
assert not any(_k.startswith("mana.classPerLevel") for _k in _k15 if _k != "mana.classPerLevel")
assert [_c for _c, _v in CLASS_MANA_DEF] == [_c[0] for _c in CLASS_ROWS if _c[0] in dict(CLASS_MANA_DEF)], "CLASS_MANA_DEF must follow SkillDefs.CLASSES order"
assert "spell.manaDivisor" not in _dp and all(len(_r[10]) <= 100 and len(_r[1]) <= 40 for _r in CFG_ROWS)
assert sum(1 for _r in CFG_ROWS if _r[0] == "divinity.healXpPerHpSelf") == 1 and "divinity.healXpPerHpSelf" in _dp \
    and "\ndivinity.healXpPerHpSelf=" in "\n" + DIVS_DEFAULTS and "\ndivinity.healXpPerHpSelf=" not in "\n" + DIV_DEFAULTS
for _k in ("perk.archery.keepLoaded.meter", "perk.archery.keepLoaded.sound", "perk.archery.keepLoaded.hint"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp and ("\n" + _k + "=") in ("\n" + XBOWX_DEFAULTS) \
        and ("\n" + _k + "=") not in ("\n" + XBOW_DEFAULTS), _k
# the appended blocks never share a key with each other or with the blocks appended before them (DIV_L, XBOW_L)
_blk = {}
for _nm, _txt in (("DIV", DIV_DEFAULTS), ("DIVS", DIVS_DEFAULTS), ("XBOW", XBOW_DEFAULTS), ("XBOWX", XBOWX_DEFAULTS), ("OVL", OVL_DEFAULTS),
                  ("CLS", CLS_DEFAULTS), ("CURVE", CURVE_DEFAULTS), ("MREG", MREG_DEFAULTS), ("N14", N14_DEFAULTS), ("CMAN", CMAN_DEFAULTS)):
    for _ln in _txt.split("\n"):
        if _ln and not _ln.startswith("#") and "=" in _ln:
            _kk = _ln.split("=", 1)[0]
            assert _kk not in _blk, "%s in both %s and %s" % (_kk, _blk.get(_kk), _nm)
            _blk[_kk] = _nm
# the Overall skill list default = LABELS of slots 0, 1, 2, 4, 10, 11, 12, 13 + Class, exactly the OverallCfg.SLOTS default
_ovt = OVL_SKILLS_DEF.split(",")
assert _ovt[-1] == "Class" and [SLOT_LABELS.index(_x) for _x in _ovt[:-1]] == [0, 1, 2, 4, 10, 11, 12, 13], _ovt
assert all(_c in [_r[0] for _r in CLASS_ROWS] for _c, _v in CLASS_BASE_DEF)
kit = CFG.emit(pool, PKG, MOD="SkyySkills", TITLE="Skills", VERSION=VERSION, NODE="skyyskills.admin", CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=["Skyy_SkyySkills/xp.properties"], RELOAD="SkillKit.reload", KEEP=10, DEFAULTS={"xp.properties": DEFAULTS},
               NOTE="Hand edits of xp.properties: /skills reload. Levels tab: class and other skills' curves.")

# ================= 0.4.8 ManaCost / ManaMig / ManaGuard (tools/skills_0_4_8_patch.py points 1-3) =================
# compiled after the config kit (ManaMig writes with its CfgRows.atomicWrite) and before SkillKit's custom rows / SkillTick / setup (callers)
KIT_FALLBACK = [('Archer', 'Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64'), ('Warrior', 'Weapon_Sword_Crude:1'), ('Assassin', 'Weapon_Daggers_Crude:1'), ('Shaman', ''), ('Mage', 'Weapon_Staff_Wood:1'), ('Berserker', 'Weapon_Battleaxe_Crude:1'), ('Priest', 'Weapon_Wand_Wood:1')]
assert [_c for _c, _k in KIT_FALLBACK] == [_c[0] for _c in CLASS_ROWS], "KIT_FALLBACK must follow SkillDefs.CLASSES"
for _c, _k in KIT_FALLBACK:
    for _e in [x for x in _k.split(",") if x]:
        must(_e.split(":")[0])
# cross-check: the SET-pinned SkyyClasses script still ships these default kits (a note, not a stop: SkyyClasses may change them on purpose;
# the guard reads the live kit from SkyyClasses whenever it runs)
_cpin = [v for m, v in _pins if m == "SkyyClasses"]
_cps = os.path.join(os.path.dirname(HERE), "SkyyClasses", "build_skyyclasses_%s.py" % (_cpin[0] if _cpin else "?"))
if os.path.isfile(_cps):
    _ctxt = open(_cps, encoding="utf-8").read()
    _cdiff = [c for c, k in KIT_FALLBACK if not _sre.search(r'"name": "%s",.*?"kit": "%s"' % (c, _sre.escape(k)), _ctxt, _sre.S)]
    print("mana guard: built-in kit table %s SkyyClasses %s's default kits%s" % (
        "matches" if not _cdiff else "DIFFERS from", _cpin[0], (" (" + ", ".join(_cdiff) + ")") if _cdiff else ""))
else:
    print("mana guard: NOTE SkyyClasses script %s not found - built-in kit table not cross-checked" % _cps)
mcost = pool.makeClass(PKG + ".ManaCost")
mcost.addField(CtField.make("public static final int DIVISOR = %d;" % SPELL_DIVISOR, mcost))
mcost.addField(CtField.make("public static final int N = %d;" % len(SPELL_TABLE), mcost))
mcost.addField(CtField.make("public static final String[] IDS = %s;" % jarr(SPELL_IDS), mcost))
for _nm, _ix in (("OLD", 1), ("COST", 2), ("OLD_DRAIN", 3), ("DRAIN", 4)):
    mcost.addField(CtField.make("public static final int[] %s = new int[] { %s };" % (_nm, ", ".join(str(_t[_ix]) for _t in SPELL_TABLE)), mcost))
# 0.4.9: the REAL gate table from the build's gate simulation (SPELL GEN spell_verify): per item that casts with Mana, the charged cast step
# that checks it (GCHECK), the Mana it must have to cast (GATE) and what a cast spends (SPEND), with the vanilla numbers (GATE_OLD 0 = vanilla
# had no check). OLD / COST above are the item vars 0.4.8 generated (COST = the dead cast check var; DRAIN = what the item spends).
mcost.addField(CtField.make("public static final int GN = %d;" % len(SPELL_GATES), mcost))
mcost.addField(CtField.make("public static final String[] GIDS = %s;" % jarr([_g[0] for _g in SPELL_GATES]), mcost))
mcost.addField(CtField.make("public static final String[] GCHECK = %s;" % jarr([_g[1] for _g in SPELL_GATES]), mcost))
for _nm, _ix in (("GATE_OLD", 2), ("GATE", 3), ("SPEND_OLD", 4), ("SPEND", 5)):
    mcost.addField(CtField.make("public static final int[] %s = new int[] { %s };" % (_nm, ", ".join(str(_g[_ix]) for _g in SPELL_GATES)), mcost))
# the 8 interaction overrides (the pack check reads them in the game's interaction assets): kind "check" / "check+" / "drain", old (-1 = none)
mcost.addField(CtField.make("public static final int INT_N = %d;" % len(SPELL_INT_PLAN), mcost))
mcost.addField(CtField.make("public static final String[] INT_IDS = %s;" % jarr(SPELL_INT_IDS), mcost))
mcost.addField(CtField.make("public static final String[] INT_KIND = %s;" % jarr([_x[2] for _x in SPELL_INT_PLAN]), mcost))
mcost.addField(CtField.make("public static final int[] INT_OLD = new int[] { %s };" % ", ".join(str(-1 if _x[3] is None else _x[3]) for _x in SPELL_INT_PLAN), mcost))
mcost.addField(CtField.make("public static final int[] INT_NEW = new int[] { %s };" % ", ".join(str(_x[4]) for _x in SPELL_INT_PLAN), mcost))
# 0.4.15 (spec 15.3 (e)): the 8 SkyyArmory-owned staffs are not in GIDS any more (no override here). costOf / spendOf ask SkyyArmory
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
mcost.addMethod(CtNewMethod.make("""
public static int gi(String id) {
  if (id == null) return -1;
  for (int i = 0; i < GIDS.length; i++) if (GIDS[i].equals(id)) return i;
  return -1;
}""", mcost))
# the Mana a cast of this item CHECKS for (0.4.9: the real check of its charged cast step - 0.4.8 returned the dead var); -1 = no Mana cast
mcost.addMethod(CtNewMethod.make("""
public static int costOf(String id) {
  int i = gi(id);
  if (i >= 0) return GATE[i];
  int a = ai(id);
  if (a < 0) return -1;
  int c = armory(id);
  return c > 0 ? c : ARM_CHECK[a];
}""", mcost))
# what one cast of this item spends (0 for Crystal_Red / Crystal_Ice / the plain Blunderbuss); -1 = no Mana cast
mcost.addMethod(CtNewMethod.make("""
public static int spendOf(String id) {
  int i = gi(id);
  if (i >= 0) return SPEND[i];
  int a = ai(id);
  if (a < 0) return -1;
  int c = armory(id);
  return c > 0 ? c : ARM_SPEND[a];
}""", mcost))

# ---- ManaMig (point 2): the one-time move of mana.magicBase / mana.magicClasses to Base Mana by class. setup() only, BEFORE SkillCfg.load
# and CfgPub.start (the kit owns every write after that). Returns {level "info" / "warn" / "" (nothing to do), message}; logs the message.
mmig = pool.makeClass(PKG + ".ManaMig")
mmig.addField(CtField.make('public static final String OLD_BASE = "mana.magicBase";', mmig))
mmig.addField(CtField.make('public static final String OLD_CLS = "mana.magicClasses";', mmig))
# the file as it was before a move (set only after the move was written); keepCopy puts it into the kit's history once the kit started
mmig.addField(CtField.make("public static volatile byte[] BEFORE = null;", mmig))
mmig.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.8";', mmig))
mmig.addField(CtField.make('public static final String WHAT = "xp.properties before mana.magicBase / mana.magicClasses moved to Base Mana by class";', mmig))
# the 0.4.6 / 0.4.7 default comment above the old pair: while it is still exactly this text (3 whole lines, any line ending) the move
# replaces it with the 0.4.8 default comment (the 4 comment lines of the default file above mana.base.enabled); any other comment that
# names the old keys stays and the move adds STALE_NOTE under its own comment line (review 2026-09-30 finding 2)
MANA_DOC_OLD = ["# Base Mana: every player's max Mana starts at mana.base; players whose class is listed in mana.magicClasses start at mana.magicBase", '# instead (their base is that number, not mana.base plus it). Vanilla max Mana is 0; Mana refills by itself (+1 every 0.2 s after', '# 6 s without taking damage).']
_ds = OVL_L.index("mana.base.enabled=true")
MANA_DOC_NEW = OVL_L[_ds - 4:_ds]
assert MANA_DOC_NEW[0].startswith("# Base Mana: every player's max Mana starts at mana.base. A class listed below") and \
    MANA_DOC_NEW[3].startswith("# without taking damage). Spells cost the vanilla Mana / %d " % SPELL_DIVISOR) and \
    all(_l.startswith("# ") and '"' not in _l and "\\" not in _l for _l in MANA_DOC_NEW + MANA_DOC_OLD), MANA_DOC_NEW
assert not any(("mana.magicBase" in _l or "mana.magicClasses" in _l) and "replaced" not in _l for _l in MANA_DOC_NEW)
mmig.addField(CtField.make("public static final String[] DOC_OLD = %s;" % jarr(MANA_DOC_OLD), mmig))
mmig.addField(CtField.make("public static final String[] DOC_NEW = %s;" % jarr(MANA_DOC_NEW), mmig))
mmig.addField(CtField.make('public static final String STALE_NOTE = "# (other comments in this file that name mana.magicBase / mana.magicClasses describe those old keys - 0.4.8 no longer reads them)";', mmig))
mmig.addMethod(CtNewMethod.make("""
public static boolean isWs(char c) {
  return c == ' ' || c == '\\t' || c == 12;
}""", mmig))
# lines[i..] are exactly DOC_OLD (each line without its CR)
mmig.addMethod(CtNewMethod.make("""
public static boolean docAt(String[] lines, int i) {
  if (i + DOC_OLD.length > lines.length) return false;
  for (int k = 0; k < DOC_OLD.length; k++) {
    String l = lines[i + k];
    if (l.endsWith("\\r")) l = l.substring(0, l.length() - 1);
    if (!l.equals(DOC_OLD[k])) return false;
  }
  return true;
}""", mmig))
# a live line of this key (Properties syntax: white space, the key, then white space, = or : or the end); body = the line without its CR
mmig.addMethod(CtNewMethod.make("""
public static boolean keyAt(String body, String key) {
  int n = body.length();
  int i = 0;
  while (i < n && isWs(body.charAt(i))) i++;
  if (!body.startsWith(key, i)) return false;
  int j = i + key.length();
  if (j >= n) return true;
  char c = body.charAt(j);
  return c == '=' || c == ':' || isWs(c);
}""", mmig))
mmig.addMethod(CtNewMethod.make("""
public static boolean contLine(String body) {
  int k = 0;
  int i = body.length() - 1;
  while (i >= 0 && body.charAt(i) == '\\\\') { k++; i--; }
  return k % 2 == 1;
}""", mmig))
mmig.addMethod(CtNewMethod.make("""
public static boolean commentOrBlank(String body) {
  int n = body.length();
  int i = 0;
  while (i < n && isWs(body.charAt(i))) i++;
  return i >= n || body.charAt(i) == '#' || body.charAt(i) == '!';
}""", mmig))
# the untouched 0.4.7 pair: mana.magicBase absent or exactly 20, mana.magicClasses absent or exactly the classes Mage and Priest (any order /
# case, nothing else - an unknown name counts as an admin's edit)
mmig.addMethod(CtNewMethod.make(f"""
public static boolean untouched(String mb, String mc) {{
  if (mb != null) {{
    double v = Double.NaN;
    try {{ v = Double.parseDouble(mb.trim()); }} catch (Throwable t) {{ return false; }}
    if (v != 20.0) return false;
  }}
  if (mc != null) {{
    if ({PKG}.OverallCfg.badClass(mc) != null) return false;
    String[] c = {PKG}.OverallCfg.parseClasses(mc);
    if (c.length != 2) return false;
    boolean m = false;
    boolean pr = false;
    for (int i = 0; i < c.length; i++) {{ if (c[i].equals("Mage")) m = true; if (c[i].equals("Priest")) pr = true; }}
    if (!m || !pr) return false;
  }}
  return true;
}}""", mmig))
# after = before without the old keys + exactly the table entries
mmig.addMethod(CtNewMethod.make(f"""
public static boolean sameAfterMove(java.util.Properties before, java.util.Properties after, Object[] t) {{
  String[] c = (String[]) t[0];
  double[] b = (double[]) t[1];
  int gone = (before.getProperty(OLD_BASE) != null ? 1 : 0) + (before.getProperty(OLD_CLS) != null ? 1 : 0);
  if (after.size() != before.size() - gone + c.length) return false;
  if (after.getProperty(OLD_BASE) != null || after.getProperty(OLD_CLS) != null) return false;
  java.util.Iterator it = before.stringPropertyNames().iterator();
  while (it.hasNext()) {{
    String k = (String) it.next();
    if (k.equals(OLD_BASE) || k.equals(OLD_CLS)) continue;
    String y = after.getProperty(k);
    if (y == null || !y.equals(before.getProperty(k))) return false;
  }}
  for (int i = 0; i < c.length; i++) {{
    String y = after.getProperty({PKG}.OverallCfg.TABLE_PREFIX + c[i]);
    if (y == null || !y.equals({PKG}.DivCfg.num(b[i]))) return false;
  }}
  return true;
}}""", mmig))
mmig.addMethod(CtNewMethod.make(f"""
public static String[] res(String level, String msg) {{
  if ("info".equals(level)) {PKG}.SkillCfg.info(msg);
  else if ("warn".equals(level)) {PKG}.SkillCfg.warn(msg);
  return new String[] {{ level, msg }};
}}""", mmig))
mmig.addMethod(CtNewMethod.make(f"""
public static String cut(String v, int n) {{
  String t = v.trim();
  return t.length() > n ? t.substring(0, n) + "..." : t;
}}""", mmig))
mmig.addMethod(CtNewMethod.make(f"""
public static String[] run() {{
  java.nio.file.Path f = {PKG}.SkillCfg.FILE;
  if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return new String[] {{ "", "no xp.properties yet" }};
  byte[] old = null;
  java.util.Properties before = new java.util.Properties();
  try {{
    old = java.nio.file.Files.readAllBytes(f);
    before.load(new java.io.ByteArrayInputStream(old));
  }} catch (Throwable t) {{
    return res("warn", "could not read " + f + " to move mana.magicBase / mana.magicClasses to Base Mana by class: " + t + " - the next start tries again");
  }}
  String mb = before.getProperty(OLD_BASE);
  String mc = before.getProperty(OLD_CLS);
  if (mb == null && mc == null) return new String[] {{ "", "nothing to move" }};
  if ({PKG}.OverallCfg.anyTableKey(before)) return new String[] {{ "", "Base Mana by class is already in the file - the old lines are left alone" }};
  boolean keep0 = untouched(mb, mc);
  Object[] t = null;
  if (keep0) t = {PKG}.OverallCfg.defTable();
  else t = {PKG}.OverallCfg.legacyTable(before);
  String tt = ((String) t[2]).length() > 0 ? (String) t[2] : "no class (every class starts at mana.base)";
  String pair = OLD_BASE + "=" + (mb == null ? "(no line)" : cut(mb, 40)) + " + " + OLD_CLS + "=" + (mc == null ? "(no line)" : cut(mc, 80));
  String badc = mc == null ? null : {PKG}.OverallCfg.badClass(mc);
  String keep = " - until then they are read as Base Mana by class " + ((String) {PKG}.OverallCfg.legacyTable(before)[2]) + " and the next start tries again";
  try {{
    String text = new String(old, "ISO-8859-1");
    String[] lines = text.split("\\n", -1);
    java.util.ArrayList out = new java.util.ArrayList();
    int hits = 0;
    int docs = 0;
    boolean stale = false;
    int headAt = -1;
    String headE = "";
    boolean cont = false;
    boolean contHit = false;
    String[] tc = (String[]) t[0];
    double[] tb = (double[]) t[1];
    for (int i = 0; i < lines.length; i++) {{
      String l = lines[i];
      boolean cr = l.endsWith("\\r");
      String body = cr ? l.substring(0, l.length() - 1) : l;
      if (cont) {{ cont = contLine(body); out.add(l); continue; }}
      if (docAt(lines, i)) {{
        // the untouched 0.4.6 / 0.4.7 comment about the old keys -> the 0.4.8 comment (line ending of its first line)
        String de = cr ? "\\r" : "";
        for (int k = 0; k < DOC_NEW.length; k++) out.add(DOC_NEW[k] + de);
        docs++;
        i += DOC_OLD.length - 1;
        continue;
      }}
      if (commentOrBlank(body)) {{
        if (body.indexOf(OLD_BASE) >= 0 || body.indexOf(OLD_CLS) >= 0) stale = true;
        out.add(l);
        continue;
      }}
      boolean hit = keyAt(body, OLD_BASE) || keyAt(body, OLD_CLS);
      cont = contLine(body);
      if (!hit) {{ out.add(l); continue; }}
      if (cont) contHit = true;
      if (hits == 0) {{
        String e = cr ? "\\r" : "";
        String why = keep0 ? "the old defaults, now Skyy's 0.4.8 default" : "an admin's values, kept";
        String[] ec = {PKG}.OverallCfg.parseClasses(mc == null ? "Mage,Priest" : mc);
        double eb = {PKG}.OverallCfg.clampD({PKG}.SkillCfg.dbl(before, OLD_BASE, 20.0), 20.0, 0.0, 10000.0);
        out.add("# Base Mana by class (SkyySkills 0.4.8) replaced " + OLD_BASE + "=" + {PKG}.DivCfg.num(eb) + " + " + OLD_CLS + "=" + {PKG}.OverallCfg.join(ec, ",") + " (" + why + "):" + e);
        headAt = out.size() - 1;
        headE = e;
        for (int k = 0; k < tc.length; k++) out.add({PKG}.OverallCfg.TABLE_PREFIX + tc[k] + "=" + {PKG}.DivCfg.num(tb[k]) + e);
        if (tc.length == 0) out.add("# (no class listed - every class starts at mana.base)" + e);
      }}
      hits++;
    }}
    if (contHit) return res("warn", "xp.properties: a " + OLD_BASE + " / " + OLD_CLS + " line continues on the next line (a trailing backslash) - not moved to Base Mana by class" + keep);
    if (hits == 0) return res("warn", "xp.properties: the " + OLD_BASE + " / " + OLD_CLS + " lines could not be found to rewrite" + keep);
    // an admin's own comment (or an edited copy of the old one) still names the old keys: say under the new comment line that it is stale
    if (stale && headAt >= 0) out.add(headAt + 1, STALE_NOTE + headE);
    String chg = "only those lines" + (docs > 0 ? " and the 0.4.7 Base Mana comment" : "") + " changed" + (stale ? " (a note under the new comment says other comments naming the old keys are stale)" : "");
    StringBuilder sb = new StringBuilder(text.length() + 256);
    for (int i = 0; i < out.size(); i++) {{
      if (i > 0) sb.append('\\n');
      sb.append((String) out.get(i));
    }}
    byte[] nb = sb.toString().getBytes("ISO-8859-1");
    java.util.Properties after = new java.util.Properties();
    after.load(new java.io.ByteArrayInputStream(nb));
    if (!sameAfterMove(before, after, t)) return res("warn", "xp.properties: moving " + OLD_BASE + " / " + OLD_CLS + " would change more than those lines - nothing written" + keep);
    {PKG}.CfgRows.atomicWrite(f, nb);
    BEFORE = old;
    if (keep0) return res("info", "xp.properties: " + pair + " (the untouched 0.4.7 defaults) became Base Mana by class " + tt + " (the 0.4.8 default); " + chg + ".");
    return res("info", "xp.properties: " + pair + " had been changed by an admin - kept as Base Mana by class " + tt + (badc != null ? " (" + cut(badc, 40) + " is not a class - left out)" : "") + "; the 0.4.8 default " + (String) {PKG}.OverallCfg.defTable()[2] + " was NOT applied (Server Setup > Skills > Overall and Mana > Base Mana by class). " + chg.substring(0, 1).toUpperCase() + chg.substring(1) + ".");
  }} catch (Throwable x) {{
    return res("warn", "could not move " + OLD_BASE + " / " + OLD_CLS + " in " + f + " to Base Mana by class: " + x + keep);
  }}
}}""", mmig))
# setup(), right after CfgPub.start: the pre-move file becomes one entry of the kit's own history (config-history/, the Server Setup
# History view - restorable there like any in-game change; KEEP 10 per file). Under the kit's save monitor like its own snapshots; no
# kit monitor is held. Returns the history file name ("" = nothing to keep or it failed - the move itself stays done either way).
mmig.addMethod(CtNewMethod.make(f"""
public static String keepCopy() {{
  byte[] b = BEFORE;
  BEFORE = null;
  if (b == null) return "";
  try {{
    int fi = -1;
    for (int k = 0; k < {PKG}.CfgRows.FILES.length; k++) if ({PKG}.CfgRows.FILES[k].endsWith("/xp.properties")) fi = k;
    if (fi < 0 || {PKG}.CfgHist.DIR == null) return "";
    String st = {PKG}.CfgHist.stamp();
    synchronized ({PKG}.CfgSaveTask.class) {{
      {PKG}.CfgHist.snapshot(fi, b, st, WHO, WHAT);
    }}
    String[] have = {PKG}.CfgHist.list(fi);
    for (int k = have.length - 1; k >= 0; k--) {{
      byte[] c = java.nio.file.Files.readAllBytes({PKG}.CfgHist.bak(fi, have[k]));
      if (java.util.Arrays.equals(c, b)) {{
        String n = {PKG}.CfgHist.bak(fi, have[k]).getFileName().toString();
        {PKG}.SkillCfg.info("xp.properties: the file as it was before the Base Mana by class move is kept in the config history (" + n + ") - Server Setup > Skills > History can restore it.");
        return n;
      }}
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not keep a history copy of xp.properties from before the Base Mana by class move: " + t); }}
  return "";
}}""", mmig))

# ---- HealMig (0.4.11 point 5): the one-time heal XP update of an existing xp.properties (Skyy 2026-10-01). setup() only, after ManaMig.run
# and BEFORE SkillCfg.load and CfgPub.start. The SkyyClasses 0.1.10 migrate0110 machinery method for method (reviewed + live): pure text
# step mgUpdate on the config kit's own parser (CfgFile.isComment / key / value / end / valStart), a Properties check (only the updated
# keys differ), CfgHist.snapshot + mgSaved (no rewrite unless config-history really holds the old bytes), CfgRows.atomicWrite, one
# config-changes.log line per changed key (Server Setup -> Changes -> Undo), one INFO line (+ one per kept value).
hmig = pool.makeClass(PKG + ".HealMig")
for _d in ("public static final String[] MG_KEY = %s;" % jarr([t[0] for t in HEAL_MG]),
           "public static final String[] MG_OLD = %s;" % jarr([t[1] for t in HEAL_MG]),
           "public static final String[] MG_NEW = %s;" % jarr([t[2] for t in HEAL_MG]),
           "public static final String[] MG_WHY = %s;" % jarr([t[3] for t in HEAL_MG]),
           "public static final String[] DOC_OLD = %s;" % jarr([t[0] for t in HEAL_DOC]),
           "public static final String[] DOC_NEW = %s;" % jarr([t[1] for t in HEAL_DOC]),
           "public static final String MG_MARK = %s;" % json.dumps(HEAL_MARK),
           "public static final String MG_MARK_ID = %s;" % json.dumps(HEAL_MARK_ID),
           'public static final String MG_WHO = "SkyySkills 0.4.11";',
           'public static final String ANCHOR = "divinity.healXp.enabled";'):
    hmig.addField(CtField.make(_d, hmig))
assert all('"' not in x and "\\" not in x for t in HEAL_MG + HEAL_DOC for x in t)
HMIG_JAVA = [r"""
public static int mgIdx(String k) {
  if (k == null) return -1;
  for (int i = 0; i < MG_KEY.length; i++) if (MG_KEY[i].equals(k)) return i;
  return -1;
}""", r"""
public static int docIdx(String body) {
  for (int i = 0; i < DOC_OLD.length; i++) if (DOC_OLD[i].equals(body)) return i;
  return -1;
}""",
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser). null = the marker is already in a comment line
# (nothing to do). Else { new text, "divinity.healXpPerHp 0.2 -> 1, ...", String[] kept notes, String[] { key, old, new }*, Integer docs }.
# A heal key whose LAST live line (the one Properties keeps) is a one-line entry holding exactly the old text is updated: every one-line
# entry of it holding the old text gets the new value (value text only: key, separator and CR stay). Anything else is kept: an admin's
# value (noted unless it already is the new default), a continued entry (noted), a missing line (silent). A comment line that is exactly
# a DOC_OLD line becomes its DOC_NEW line (CR kept). Marker: on its own line above the first divinity.healXp.enabled / heal key entry -
# above the whole run of comment lines directly on top of it - else above line 0. Lines are scanned from the start of a logical line, so a
# continued entry's tail is never taken for a comment. Never throws for any text.
r"""
public static Object[] mgUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = MG_KEY.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int first = -1;
  int above = -1;
  int run = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MG_MARK_ID) >= 0) return null;
      if (s.trim().length() == 0) run = -1;
      else if (run < 0) run = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    String key = @PKG@.CfgFile.key(s);
    int m = mgIdx(key);
    if (first < 0 && (m >= 0 || ANCHOR.equals(key))) { first = k; above = run >= 0 ? run : k; }
    if (m >= 0) {
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      multi[m] = e > k;
    }
    run = -1;
    k = e + 1;
  }
  boolean[] mig = new boolean[n];
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    if (eff[i] == null) continue;
    if (!multi[i] && eff[i].equals(MG_OLD[i])) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append(MG_KEY[i]).append(' ').append(MG_OLD[i]).append(" -> ").append(MG_NEW[i]);
      rows.add(MG_KEY[i]);
      rows.add(MG_OLD[i]);
      rows.add(MG_NEW[i]);
    } else if (multi[i] || !eff[i].equals(MG_NEW[i])) {
      kept.add(MG_KEY[i] + "=" + @PKG@.CfgRows.oneLine(eff[i]) + " kept (an admin's value) - it now counts as " + MG_WHY[i] + " (0.4.10 multiplied it by the class skill XP multiplier); the 0.4.11 default is " + MG_NEW[i]);
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  int docs = 0;
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) {
      int d = docIdx(s2);
      if (d >= 0) {
        out.add(DOC_NEW[d] + (raw[k].endsWith("\r") ? "\r" : ""));
        docs++;
      } else out.add(raw[k]);
      k++;
      continue;
    }
    int e2 = @PKG@.CfgFile.end(l, k);
    int m2 = mgIdx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(MG_OLD[m2])) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + MG_NEW[m2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  int at = first >= 0 ? above : 0;
  String crA = at + 1 < raw.length ? (raw[at].endsWith("\r") ? "\r" : "") : cr;
  out.add(at, MG_MARK + crA);
  StringBuilder sb = new StringBuilder(text.length() + MG_MARK.length() + 256);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]), Integer.valueOf(docs) };
}""",
# the update may change nothing but the updated keys' values: both texts as java.util.Properties - same keys, same values, the updated keys
# exactly their new value (a marker / comment line can never change a value; this guards the parser corner cases)
r"""
public static boolean sameAfter(byte[] old, byte[] nb, String[] rows) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties b = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    b.load(new java.io.ByteArrayInputStream(nb));
    if (a.size() != b.size()) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String want = a.getProperty(k);
      for (int i = 0; i + 2 < rows.length; i += 3) if (rows[i].equals(k)) want = rows[i + 2];
      String got = b.getProperty(k);
      if (got == null || !got.equals(want)) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}""",
r"""
public static int fileIdx() {
  for (int k = 0; k < @PKG@.CfgRows.FILES.length; k++) if (@PKG@.CfgRows.FILES[k].endsWith("/xp.properties")) return k;
  return -1;
}""",
# the config kit's own files for the update, before CfgPub.start (which sets the same values again): history + change log live in the
# folder of xp.properties (the kit's HOME, Skyy_SkyySkills)
r"""
public static void mgKit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = @PKG@.SkillCfg.LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}""",
# CfgHist.snapshot swallows its own errors, so after it the update checks that config-history really holds a copy with exactly these
# bytes (the new copy, or the newest one when snapshot skipped an equal file) - the copies themselves, not index.log
r"""
public static boolean mgSaved(int f, byte[] old) {
  String[] have = @PKG@.CfgHist.list(f);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(f, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}""",
# one config-changes.log line in the kit's scalar-row format (CfgLog.add without its per-line INFO; the key column = the row key, so
# Server Setup -> Changes undoes it with a plain set back to the old value)
r"""
public static String mgLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + MG_WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""",
# setup(): the file before this update becomes a History version (KEEP 10, verified by mgSaved before the rewrite), the new text is
# written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log line per updated key, one INFO line (+ one per kept value).
# Returns the INFO line(s) joined by \n ("" = nothing done: no file - load() writes the 0.4.11 default with the marker -, marker already
# there, or a failure - WARN, file untouched, retried at the next start)
r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = mgUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    String[] rows = (String[]) r[3];
    if (!sameAfter(old, data, rows)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for the 0.4.11 heal XP: the update would change more than the heal XP lines (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = fileIdx();
    if (fi < 0) return "";
    mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), MG_WHO, "before the 0.4.11 heal XP update");
    if (!mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for the 0.4.11 heal XP: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(mgLog(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    int docs = ((Integer) r[4]).intValue();
    String dt = docs > 0 ? "; " + docs + " outdated default comment line(s) updated" : "";
    String msg = null;
    if (chg.length() > 0) msg = "xp.properties updated for the 0.4.11 heal XP (Priest heal XP is what the Priest gets - no class skill XP multiplier): " + chg + dt + " (the old file is in config-history; Server Setup -> Changes can undo each line)";
    else msg = "xp.properties: no divinity heal XP line still had its 0.4.10 default - no value changed" + dt + " (0.4.11 heal XP marker added; the old file is in config-history)";
    @PKG@.SkillCfg.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { @PKG@.SkillCfg.info(kept[i]); all.append('\n').append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update xp.properties for the 0.4.11 heal XP (the file is used as it is): " + t);
    return "";
  }
}"""]
for _src in HMIG_JAVA:
    hmig.addMethod(CtNewMethod.make(_src.replace("@PKG@", PKG), hmig))

# ---- DocMig (0.4.14, fix (5)): the stale Mana regen comment of an existing xp.properties ("Never above max Mana, never while charging, ..."),
# rewritten ONCE: setup() after HealMig.run, BEFORE SkillCfg.load and CfgPub.start. Only that EXACT comment line (CR kept; a hand-edited one is
# left alone); lines are scanned per logical line (a continued entry's tail is never taken for a comment); the "(SkyySkills 0.4.12)" block
# header stays. HealMig's machinery: the values must stay equal (sameAfter), config-history must hold the old bytes first (mgKit + snapshot
# + mgSaved), the kit's atomicWrite (ISO-8859-1 bytes, line endings kept). The new line is its own marker (no old line = nothing to do); no
# value changes, so there is no change-log line to undo - Server Setup -> History restores the old file.
dmig.addField(CtField.make("public static final String OLD = %s;" % json.dumps(MREG_DOC_OLD), dmig))
dmig.addField(CtField.make("public static final String NEW = %s;" % json.dumps(MREG_DOC_NEW), dmig))
dmig.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.14";', dmig))
dmig.addMethod(CtNewMethod.make(J14(r"""
public static Object[] docUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  java.util.ArrayList out = new java.util.ArrayList();
  int n = 0;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.equals(OLD)) { out.add(NEW + (raw[k].endsWith("\r") ? "\r" : "")); n++; }
      else out.add(raw[k]);
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    for (int q = k; q <= e; q++) out.add(raw[q]);
    k = e + 1;
  }
  if (n == 0) return null;
  StringBuilder sb = new StringBuilder(text.length() + 64);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  return new Object[] { sb.toString(), Integer.valueOf(n) };
}"""), dmig))
dmig.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = docUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    if (!@PKG@.HealMig.sameAfter(old, data, new String[0])) {
      @PKG@.SkillCfg.warn("xp.properties: the Mana regen comment was NOT updated (the update would change a value; the file is used as it is)");
      return "";
    }
    int fi = @PKG@.HealMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.HealMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.14 Mana regen comment fix");
    if (!@PKG@.HealMig.mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties: the Mana regen comment was NOT updated - the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String msg = "xp.properties: the outdated Mana regen comment ('never while charging') now says charging no longer pauses it (SkyySkills 0.4.13+) - " + ((Integer) r[1]).intValue() + " line, no setting changed (the old file is in config-history)";
    @PKG@.SkillCfg.info(msg);
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update the Mana regen comment of xp.properties (the file is used as it is): " + t);
    return "";
  }
}"""), dmig))

# ---- ClassManaMig (0.4.15, spec 15.4 "The config file"): the max Mana per class level lines reach an EXISTING xp.properties ONCE. setup() only,
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

# ---- ManaGuard (point 3): WARN once per class whose base Mana is below the Mana cost of a weapon in its class kit. Scheduler thread
# (SkillTick) - bridge reads, the config kit's read-only "get" op of SkyyClasses and logging only; never a number changed, never the world.
mgd = pool.makeClass(PKG + ".ManaGuard")
mgd.addField(CtField.make("public static final String[] FB_CLS = %s;" % jarr([_c for _c, _k in KIT_FALLBACK]), mgd))
mgd.addField(CtField.make("public static final String[] FB_KIT = %s;" % jarr([_k for _c, _k in KIT_FALLBACK]), mgd))
mgd.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();", mgd))
mgd.addField(CtField.make('public static volatile String LAST = "";', mgd))
mgd.addField(CtField.make("public static volatile long EPOCH = -2L;", mgd))
mgd.addField(CtField.make("public static volatile boolean STARTED = false;", mgd))
mgd.addField(CtField.make("public static final long START_S = 10L;", mgd))   # every other plugin has published its bridge keys by then
mgd.addMethod(CtNewMethod.make(f"""
public static java.util.function.Function classesFn() {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("config:fn:SkyyClasses");
    if (o instanceof java.util.function.Function) return (java.util.function.Function) o;
  }} catch (Throwable t) {{ }}
  return null;
}}""", mgd))
# a SkyyClasses setting's current value text through the config kit's read-only "get" op (CONFIG-CONTRACT), null = no SkyyClasses /
# no such row / any error. Rows used: kit.<Class> (items text "Weapon_Staff_Wood:1") and kits.enabled (the Class kits part switch)
mgd.addMethod(CtNewMethod.make("""
public static String liveGet(java.util.function.Function f, String key) {
  if (f == null) return null;
  try {
    Object o = f.apply(new Object[] { "get", key });
    if (o instanceof String) return (String) o;
  } catch (Throwable t) { }
  return null;
}""", mgd))
mgd.addMethod(CtNewMethod.make("""
public static String liveKit(java.util.function.Function f, String cls) {
  return liveGet(f, "kit." + cls);
}""", mgd))
mgd.addMethod(CtNewMethod.make("""
public static String fbKit(String cls) {
  for (int i = 0; i < FB_CLS.length; i++) if (FB_CLS[i].equals(cls)) return FB_KIT[i];
  return "";
}""", mgd))
mgd.addMethod(CtNewMethod.make(f"""
public static long classesEpoch() {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("config:epoch:SkyyClasses");
    if (o instanceof Number) return ((Number) o).longValue();
  }} catch (Throwable t) {{ }}
  return -1L;
}}""", mgd))
# ---- pack check (review 2026-09-30 finding 3): which asset pack the game's item assets take each overridden item from. Of two packs
# with the same item the one loaded last wins (DefaultAssetMap keeps a chain of packs per id; getAssetPack = the winner, read under its
# own StampedLock). Once, from START_S on; retried every 10 s up to PACK_MAX times while the item assets cannot be read (a bare JVM, or
# not loaded yet). One INFO (all active) or one WARN (another pack wins for some); it never changes anything.
B.probe(pool, "com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAssetPack")
_pkm = B.manifest("SkyySkills", VERSION, "", "")
SKILLS_PACK = "%s:%s" % (_pkm["Group"], _pkm["Name"])   # the pack key the engine gives this jar (PluginIdentifier = Group:Name)
mgd.addField(CtField.make('public static final String PACK = "%s";' % SKILLS_PACK, mgd))
mgd.addField(CtField.make("public static volatile boolean PACK_DONE = false;", mgd))
mgd.addField(CtField.make("public static volatile int PACK_TRIES = 0;", mgd))
mgd.addField(CtField.make("public static final int PACK_MAX = 6;", mgd))
mgd.addField(CtField.make('public static volatile String PACK_LAST = "";', mgd))
# packs[i] = the pack the item assets name for ManaCost.IDS[i] (null = not there / not readable) -> {level "info" / "warn" / "" (nothing
# readable - try again), message}
mgd.addMethod(CtNewMethod.make(f"""
public static String[] packReport(String[] packs) {{
  String[] ids = {PKG}.ManaCost.IDS;
  int mine = 0;
  int other = 0;
  int miss = 0;
  StringBuilder ot = new StringBuilder();
  StringBuilder ms = new StringBuilder();
  for (int i = 0; i < ids.length; i++) {{
    String p = (packs != null && i < packs.length) ? packs[i] : null;
    if (p == null) {{
      miss++;
      if (miss <= 8) {{ if (ms.length() > 0) ms.append(", "); ms.append(ids[i]); }}
      continue;
    }}
    if (p.equals(PACK)) {{ mine++; continue; }}
    other++;
    if (other <= 8) {{ if (ot.length() > 0) ot.append(", "); ot.append(ids[i]).append(" (").append(p).append(")"); }}
  }}
  if (mine + other == 0) return new String[] {{ "", "the game's item assets could not be read" }};
  String pre = "Spell costs /" + {PKG}.ManaCost.DIVISOR + ": ";
  String mt = miss > 0 ? "; " + miss + " not in the game's item assets (" + ms.toString() + (miss > 8 ? ", ..." : "") + ")" : "";
  if (other == 0) return new String[] {{ "info", pre + (miss == 0 ? "all " + mine : mine + " of " + ids.length) + " item overrides are active (the game's item assets take them from " + PACK + ")" + mt }};
  return new String[] {{ "warn", pre + other + " of " + ids.length + " item overrides are NOT active - another asset pack wins for " + ot.toString() + (other > 8 ? ", ..." : "") + ". Those items keep that pack's Mana cost (of two packs with the same item, the one loaded last wins); " + mine + " active" + mt + "." }};
}}""", mgd))
mgd.addMethod(CtNewMethod.make(f"""
public static String[] packCheck() {{
  String[] ids = {PKG}.ManaCost.IDS;
  String[] ps = new String[ids.length];
  try {{
    com.hypixel.hytale.assetstore.map.DefaultAssetMap m = {ITM}.getAssetMap();
    if (m != null) {{
      for (int i = 0; i < ids.length; i++) {{
        try {{ ps[i] = m.getAssetPack(ids[i]); }} catch (Throwable t) {{ ps[i] = null; }}
      }}
    }}
  }} catch (Throwable t) {{ }}
  return packReport(ps);
}}""", mgd))
# ---- 0.4.9 interaction check (tools/skills_0_4_9_patch.py point 2): which pack the game's INTERACTION assets take each of the 8 overridden
# interactions from, and the live Mana check of each cast check as the engine's gate uses it. StatsConditionBaseInteraction.rawCosts = the
# stat id -> cost map of its own Costs as decoded; its afterDecode puts EntityStatsModule.resolveEntityStats(rawCosts) into costs (stat
# index -> cost), and StatsConditionInteraction.canAfford reads ONLY costs (null costs = canAfford false = every cast refused). So the number
# reported is costs' entry for DefaultEntityStatTypes.getMana() (0.4.9 review finding 4; rawCosts only tells "no Mana cost" apart).
# Every Interaction load rebuilds every root (InteractionModule.handledLoadedInteractions ->
# RootInteraction.build), so the compiled Charging steps use the asset map's winner. Same tick and retries as the item pack check.
B.probe(pool, "com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction", "getAssetMap")
assert pool.get("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionBaseInteraction").getDeclaredField("rawCosts") is not None
assert str(pool.get("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionBaseInteraction").getDeclaredField("costs").getType().getName()) == "it.unimi.dsi.fastutil.ints.Int2FloatMap"
B.probe(pool, "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes", "getMana")
mgd.addField(CtField.make("public static volatile boolean ITEMS_DONE = false;", mgd))
mgd.addField(CtField.make("public static volatile boolean INT_DONE = false;", mgd))
mgd.addField(CtField.make('public static volatile String INT_LAST = "";', mgd))
mgd.addField(CtField.make("public static volatile boolean ARM_DONE = false;", mgd))   # 0.4.15: the staff handover pack check
mgd.addField(CtField.make('public static volatile String ARM_LAST = "";', mgd))
mgd.addField(CtField.make("public static volatile java.lang.reflect.Field RAW = null;", mgd))
mgd.addField(CtField.make("public static volatile java.lang.reflect.Field RES = null;", mgd))
# the live Mana check of an interaction asset: the resolved costs entry of the Mana stat (what the gate compares); -2 = not a
# StatsCondition, -3 = a StatsCondition without a Mana cost, -4 = a Mana cost the engine did not resolve (no costs entry for the Mana
# index: the gate does not check it as decoded), -1 = not readable
mgd.addMethod(CtNewMethod.make("""
public static float liveCheck(Object a) {
  try {
    if (a == null) return -1.0f;
    if (!(a instanceof com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionBaseInteraction)) return -2.0f;
    java.lang.reflect.Field f = RAW;
    if (f == null) {
      f = Class.forName("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionBaseInteraction").getDeclaredField("rawCosts");
      f.setAccessible(true);
      RAW = f;
    }
    java.lang.reflect.Field g = RES;
    if (g == null) {
      g = Class.forName("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionBaseInteraction").getDeclaredField("costs");
      g.setAccessible(true);
      RES = g;
    }
    Object m = f.get(a);
    if (!(m instanceof java.util.Map)) return -1.0f;
    Object v = ((java.util.Map) m).get("Mana");
    if (!(v instanceof Number)) return -3.0f;
    Object c = g.get(a);
    if (!(c instanceof it.unimi.dsi.fastutil.ints.Int2FloatMap)) return -4.0f;
    it.unimi.dsi.fastutil.ints.Int2FloatMap cm = (it.unimi.dsi.fastutil.ints.Int2FloatMap) c;
    int mi = com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes.getMana();
    if (!cm.containsKey(mi)) return -4.0f;
    return cm.get(mi);
  } catch (Throwable t) { return -1.0f; }
}""", mgd))
# packs[i] / live[i] for ManaCost.INT_IDS[i] (null / -1 = not there / not readable) -> {level "info" / "warn" / "" (nothing readable - try
# again), message}
mgd.addMethod(CtNewMethod.make(f"""
public static String[] intReport(String[] packs, float[] live) {{
  String[] ids = {PKG}.ManaCost.INT_IDS;
  int mine = 0;
  int other = 0;
  int miss = 0;
  int unread = 0;
  StringBuilder ot = new StringBuilder();
  StringBuilder ms = new StringBuilder();
  StringBuilder bad = new StringBuilder();
  StringBuilder ck = new StringBuilder();
  for (int i = 0; i < ids.length; i++) {{
    String p = (packs != null && i < packs.length) ? packs[i] : null;
    if (p == null) {{
      miss++;
      if (ms.length() > 0) ms.append(", ");
      ms.append(ids[i]);
      continue;
    }}
    if (!p.equals(PACK)) {{
      other++;
      if (ot.length() > 0) ot.append(", ");
      ot.append(ids[i]).append(" (").append(p).append(")");
      continue;
    }}
    mine++;
    if ({PKG}.ManaCost.INT_KIND[i].startsWith("check")) {{
      float v = (live != null && i < live.length) ? live[i] : -1.0f;
      int want = {PKG}.ManaCost.INT_NEW[i];
      if (v == -1.0f) {{ unread++; continue; }}
      if (v == -2.0f || v == -3.0f || v == -4.0f || Math.abs(v - (float) want) > 0.001f) {{
        if (bad.length() > 0) bad.append(", ");
        if (v == -2.0f) bad.append(ids[i]).append(" is not a Mana check (not a StatsCondition; it should check ").append(want).append(")");
        else if (v == -3.0f) bad.append(ids[i]).append(" checks no Mana (it should check ").append(want).append(")");
        else if (v == -4.0f) bad.append(ids[i]).append(" has a Mana cost the engine did not resolve to the Mana stat (its gate does not check it; it should check ").append(want).append(")");
        else bad.append(ids[i]).append(" checks ").append({PKG}.DivCfg.num((double) v)).append(" instead of ").append(want);
        continue;
      }}
      if (ck.length() > 0) ck.append(", ");
      ck.append(ids[i]).append(" ").append(want);
    }}
  }}
  if (mine + other == 0) return new String[] {{ "", "the game's interaction assets could not be read" }};
  String pre = "Cast checks /" + {PKG}.ManaCost.DIVISOR + ": ";
  String mt = miss > 0 ? "; " + miss + " not in the game's interaction assets (" + ms.toString() + ")" : "";
  String lv = ck.length() > 0 ? "; live cast checks " + ck.toString() + " (= what each cast spends)" : "";
  String ur = unread > 0 ? "; " + unread + " live cast check(s) not readable" : "";
  if (other == 0 && bad.length() == 0) return new String[] {{ "info", pre + (miss == 0 ? "all " + mine : mine + " of " + ids.length) + " interaction overrides are active (the game's interaction assets take them from " + PACK + ")" + lv + ur + mt }};
  String w = pre;
  if (other > 0) w = w + other + " of " + ids.length + " interaction overrides are NOT active - another asset pack wins for " + ot.toString() + ". Those casts keep that pack's Mana check / spend (of two packs with the same interaction, the one loaded last wins); " + mine + " active";
  else w = w + "all " + mine + " interaction overrides come from " + PACK;
  if (bad.length() > 0) w = w + "; the live cast check differs: " + bad.toString() + " - the Mana a cast needs is not what it spends";
  return new String[] {{ "warn", w + lv + ur + mt + "." }};
}}""", mgd))
mgd.addMethod(CtNewMethod.make(f"""
public static String[] intCheck() {{
  String[] ids = {PKG}.ManaCost.INT_IDS;
  String[] ps = new String[ids.length];
  float[] lv = new float[ids.length];
  for (int i = 0; i < lv.length; i++) lv[i] = -1.0f;
  try {{
    com.hypixel.hytale.assetstore.map.DefaultAssetMap m = com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction.getAssetMap();
    if (m != null) {{
      for (int i = 0; i < ids.length; i++) {{
        try {{ ps[i] = m.getAssetPack(ids[i]); }} catch (Throwable t) {{ ps[i] = null; }}
        try {{ lv[i] = liveCheck(m.getAsset(ids[i])); }} catch (Throwable t) {{ lv[i] = -1.0f; }}
      }}
    }}
  }} catch (Throwable t) {{ }}
  return intReport(ps, lv);
}}""", mgd))
# ---- 0.4.15 staff handover (spec 15.3 (f)): which asset pack the game's item assets take the 8 SkyyArmory-owned staffs from - every one from
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
# 0.4.9: both checks (the items as in 0.4.8, the interactions new), each logged once as soon as it is readable; after PACK_MAX tries the
# unreadable one says so
mgd.addMethod(CtNewMethod.make(f"""
public static void packTick() {{
  PACK_TRIES++;
  if (!ITEMS_DONE) {{
    String[] r = packCheck();
    if (r[0].length() > 0) {{
      ITEMS_DONE = true;
      PACK_LAST = r[1];
      if ("warn".equals(r[0])) {PKG}.SkillCfg.warn(r[1]);
      else {PKG}.SkillCfg.info(r[1]);
    }}
  }}
  if (!INT_DONE) {{
    String[] q = intCheck();
    if (q[0].length() > 0) {{
      INT_DONE = true;
      INT_LAST = q[1];
      if ("warn".equals(q[0])) {PKG}.SkillCfg.warn(q[1]);
      else {PKG}.SkillCfg.info(q[1]);
    }}
  }}
  if (!ARM_DONE) {{   // 0.4.15: the staff handover - which pack the 8 SkyyArmory-owned staffs come from
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
    if (!ITEMS_DONE) {{
      PACK_LAST = "Spell costs /" + {PKG}.ManaCost.DIVISOR + ": the game's item assets could not be read to see which pack each of the " + {PKG}.ManaCost.N + " overridden items comes from - not checked";
      {PKG}.SkillCfg.info(PACK_LAST);
    }}
    if (!INT_DONE) {{
      INT_LAST = "Cast checks /" + {PKG}.ManaCost.DIVISOR + ": the game's interaction assets could not be read to see which pack each of the " + {PKG}.ManaCost.INT_N + " overridden interactions comes from - not checked";
      {PKG}.SkillCfg.info(INT_LAST);
    }}
  }}
}}""", mgd))
# the lines it logged this call (WARNs first, then the INFO summary when it changed); tests call it directly
mgd.addMethod(CtNewMethod.make(f"""
public static String[] run() {{
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.function.Function f = classesFn();
  if ("false".equals(liveGet(f, "kits.enabled"))) {{
    // SkyyClasses gives no class kit at all: no kit weapon to check (checked again when SkyyClasses' config changes)
    WARNED.clear();
    String off = "Base Mana check (kits from SkyyClasses, spell costs /" + {PKG}.ManaCost.DIVISOR + "): class kits are off in SkyyClasses (Server Setup > Classes > Class kits) - no kit weapon to check";
    if (!off.equals(LAST)) {{
      LAST = off;
      {PKG}.SkillCfg.info(off);
      out.add(off);
    }}
    String[] r0 = new String[out.size()];
    for (int i = 0; i < r0.length; i++) r0[i] = (String) out.get(i);
    return r0;
  }}
  StringBuilder ok = new StringBuilder();
  int failed = 0;
  int weapons = 0;
  for (int k = 0; k < {PKG}.SkillDefs.CLASSES.length; k++) {{
    String cls = {PKG}.SkillDefs.CLASSES[k];
    String kit = liveKit(f, cls);
    boolean live = kit != null;
    if (kit == null) kit = fbKit(cls);
    double base = {PKG}.OverallCfg.MANA_ON ? {PKG}.OverallCfg.baseFor(cls) : 0.0;
    String[] ps = kit.split(",");
    StringBuilder badW = new StringBuilder();
    StringBuilder okW = new StringBuilder();
    StringBuilder sig = new StringBuilder();
    for (int i = 0; i < ps.length; i++) {{
      String id = ps[i].trim();
      int c = id.indexOf(':');
      if (c >= 0) id = id.substring(0, c).trim();
      if (id.length() == 0) continue;
      int cost = {PKG}.ManaCost.costOf(id);
      if (cost <= 0) continue;
      int spend = {PKG}.ManaCost.spendOf(id);
      weapons++;
      if (base + 0.000001 < (double) cost) {{
        if (badW.length() > 0) badW.append(", ");
        if (spend == cost) badW.append(id).append(" costs ").append(cost).append(" Mana per cast");
        else badW.append(id).append(" needs ").append(cost).append(" Mana to cast (it spends ").append(spend).append(")");
        sig.append(id).append(':').append(cost).append(':').append(spend).append(',');
      }} else {{
        if (okW.length() > 0) okW.append(", ");
        if (spend == cost) {{
          long casts = (long) Math.floor(base / (double) cost + 0.000001);
          okW.append(id).append(" ").append(cost).append(" (").append(casts).append(casts == 1L ? " cast)" : " casts)");
        }} else if (spend <= 0) {{
          okW.append(id).append(" ").append(cost).append(" (spends 0: free while Mana is ").append(cost).append("+)");
        }} else {{
          long casts2 = (long) Math.floor((base - (double) cost) / (double) spend + 0.000001) + 1L;
          okW.append(id).append(" ").append(cost).append(" (spends ").append(spend).append(": ").append(casts2).append(casts2 == 1L ? " cast)" : " casts)");
        }}
      }}
    }}
    if (badW.length() > 0) {{
      failed++;
      String s = {PKG}.DivCfg.num(base) + "|" + sig.toString() + ({PKG}.OverallCfg.MANA_ON ? "on" : "off");
      Object prev = WARNED.put(cls, s);
      if (prev == null || !prev.equals(s)) {{
        String m = "Base Mana check: " + cls + ({PKG}.OverallCfg.MANA_ON ? " starts with " + {PKG}.DivCfg.num(base) + " max Mana" : " starts with 0 max Mana (the Base Mana part is off)") + ", but the kit weapon " + badW.toString() + " (kit from " + (live ? "SkyyClasses" : "the built-in table") + ") - a new " + cls + " cannot cast it. Raise " + cls + " in Server Setup > Skills > Overall and Mana > Base Mana by class. Nothing was changed automatically.";
        {PKG}.SkillCfg.warn(m);
        out.add(m);
      }}
    }} else {{
      WARNED.remove(cls);
      if (okW.length() > 0) {{
        if (ok.length() > 0) ok.append(", ");
        ok.append(cls).append(" ").append({PKG}.DivCfg.num(base)).append(" Mana >= ").append(okW.toString());
      }}
    }}
  }}
  String body = ok.length() > 0 ? ok.toString() : (weapons == 0 ? "no class kit holds a Mana weapon" : "none");
  String info = "Base Mana check (" + (f != null ? "kits from SkyyClasses" : "built-in kit table - SkyyClasses not found") + ", spell costs /" + {PKG}.ManaCost.DIVISOR + "): " + body + (failed > 0 ? "; " + failed + " class(es) below their kit weapon's Mana cost (see the WARN)" : "");
  if (!info.equals(LAST)) {{
    LAST = info;
    {PKG}.SkillCfg.info(info);
    out.add(info);
  }}
  String[] r = new String[out.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) out.get(i);
  return r;
}}""", mgd))
# SkillTick (every second): from START_S on, once at start, then whenever a config load marked it dirty or SkyyClasses' config changed;
# the pack check runs first, at START_S and every 10 s after until it has an answer (at most PACK_MAX tries)
mgd.addMethod(CtNewMethod.make(f"""
public static void tick(long n) {{
  if (n < START_S) return;
  if (!PACK_DONE && (n - START_S) % 10L == 0L) packTick();
  long e = classesEpoch();
  if (STARTED && !{PKG}.OverallCfg.GUARD_DIRTY && e == EPOCH) return;
  {PKG}.OverallCfg.GUARD_DIRTY = false;
  STARTED = true;
  EPOCH = e;
  run();
}}""", mgd))

# ================= SkillKit (0.4.3): reload routine, check= hooks, the custom: level-curve rows (spec 5.7) =================
# The kit calls these by reflection with no kit lock held (tools/CONFIG-CONTRACT.md guarantee 6); SkillKit takes no lock of its own
# except SkillDefs.setTable's (SkillCfg.load takes SkillCfg then SkillDefs, never the other way round) and its class lock around TAIL
# (tailFor / keepTail call nothing else, so no lock is ever taken inside it).
skit.addMethod(CtNewMethod.make(f"""
public static String reload() {{
  String r = {PKG}.SkillCfg.load();
  {PKG}.SkillStore.republishAll();   // review fix R9 (0.4.12): a curve change in the file reaches skill:<uuid> within 5 s
  {PKG}.Acro.djPublish();
  return r;
}}""", skit))
# a levels= value -> long[] (1-100 entries, each > 0), else null (the loader's own rule: a bad list = the default table)
skit.addMethod(CtNewMethod.make("""
public static long[] parseList(String v) {
  if (v == null) return null;
  String t = v.trim();
  if (t.length() == 0) return null;
  String[] ps = t.split(",");
  if (ps.length < 1 || ps.length > 100) return null;
  long[] r = new long[ps.length];
  for (int i = 0; i < ps.length; i++) {
    long x = 0L;
    try { x = Long.parseLong(ps[i].trim()); } catch (Throwable e) { return null; }
    if (x <= 0L) return null;
    r[i] = x;
  }
  return r;
}""", skit))
# the list the curve rows start from: the kit's current levels= value (in-game edits still waiting for the 500 ms save included), else
# the running table
skit.addMethod(CtNewMethod.make(f"""
public static long[] curList() {{
  try {{
    Object o = new {PKG}.CfgFn().apply(new Object[] {{ "get", "levels" }});
    if (o instanceof String) {{
      long[] r = parseList((String) o);
      if (r != null) return r;
    }}
  }} catch (Throwable t) {{ }}
  long[] p = {PKG}.SkillDefs.PER;
  long[] c = new long[p.length];
  for (int i = 0; i < p.length; i++) c[i] = p[i];
  return c;
}}""", skit))
# total XP of the list as a percent of the default table over the same number of levels
skit.addMethod(CtNewMethod.make(f"""
public static long pctOf(long[] l) {{
  long[] d = {PKG}.SkillDefs.DEFAULT_PER;
  double a = 0.0;
  double b = 0.0;
  for (int i = 0; i < l.length; i++) {{
    a += (double) l[i];
    b += (double) (i < d.length ? d[i] : d[d.length - 1]);
  }}
  if (b <= 0.0) return 100L;
  return Math.round(a * 100.0 / b);
}}""", skit))
skit.addMethod(CtNewMethod.make("""
public static String join(long[] l) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < l.length; i++) {
    if (i > 0) sb.append(',');
    sb.append(l[i]);
  }
  return sb.toString();
}""", skit))
# cut to n levels, or extend: level i (0-based) = default[i] x (last kept level / default of that level) - the default list extends back
# to exactly the default
skit.addMethod(CtNewMethod.make(f"""
public static long[] withMax(long[] cur, int n) {{
  long[] d = {PKG}.SkillDefs.DEFAULT_PER;
  int len = cur.length;
  long[] r = new long[n];
  int li = len - 1 < d.length ? len - 1 : d.length - 1;
  double base = (double) d[li];
  double f = base > 0.0 ? (double) cur[len - 1] / base : 1.0;
  for (int i = 0; i < n; i++) {{
    if (i < len) {{ r[i] = cur[i]; continue; }}
    long di = i < d.length ? d[i] : d[d.length - 1];
    long v = Math.round((double) di * f);
    r[i] = v < 1L ? 1L : v;
  }}
  return r;
}}""", skit))
# TAIL = the full list before the last "Max level" cut, LAST = the list the last "Max level" change left (this server run only, in
# memory). While the list is still exactly LAST (so it starts with the kept levels), raising Max level again - Undo included - gives the
# cut levels back with their real values (a hand-edited or imported curve is not reshaped along the default curve); successive cuts
# (100 -> 60 -> 40) keep the longest list. Any other change of the list (curve size, the list row, a hand edit, History, an import) makes
# it differ from LAST, so the memory is ignored and the next cut starts a new one. SkillKit's class lock guards only these two arrays
# (no other lock is taken inside).
skit.addField(CtField.make("public static long[] TAIL = null;", skit))
skit.addField(CtField.make("public static long[] LAST = null;", skit))
skit.addMethod(CtNewMethod.make("""
public static boolean sameList(long[] a, long[] b) {
  if (a == null || b == null || a.length != b.length) return false;
  for (int i = 0; i < a.length; i++) if (a[i] != b[i]) return false;
  return true;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static synchronized long[] tailFor(long[] cur) {
  long[] t = TAIL;
  if (t == null || t.length <= cur.length || !sameList(cur, LAST)) return cur;
  for (int i = 0; i < cur.length; i++) if (t[i] != cur[i]) return cur;
  return t;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static synchronized void keepTail(long[] cur) {
  if (tailFor(cur) != cur) return;
  long[] c = new long[cur.length];
  for (int i = 0; i < cur.length; i++) c[i] = cur[i];
  TAIL = c;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static synchronized void setLast(long[] l) {
  long[] c = new long[l.length];
  for (int i = 0; i < l.length; i++) c[i] = l[i];
  LAST = c;
}""", skit))
# every level x (pct / current percent): the list's size becomes pct % of the default, its shape is kept; null = an entry above 1e15
skit.addMethod(CtNewMethod.make(f"""
public static long[] scaledTo(long[] cur, long pct) {{
  long[] d = {PKG}.SkillDefs.DEFAULT_PER;
  double a = 0.0;
  double b = 0.0;
  for (int i = 0; i < cur.length; i++) {{
    a += (double) cur[i];
    b += (double) (i < d.length ? d[i] : d[d.length - 1]);
  }}
  if (a <= 0.0 || b <= 0.0) return null;
  double f = ((double) pct / 100.0) * b / a;
  long[] r = new long[cur.length];
  for (int i = 0; i < cur.length; i++) {{
    double v = (double) cur[i] * f;
    if (v > 1.0E15) return null;
    long x = Math.round(v);
    r[i] = x < 1L ? 1L : x;
  }}
  return r;
}}""", skit))
# a custom: row's file lines never run a reload routine by themselves (kit v1), so the curve rows arm the global one for the next save of
# xp.properties: after the atomic write SkillCfg.load re-reads the file, so the running table always ends up equal to the file
skit.addMethod(CtNewMethod.make(f"""
public static void armReload() {{
  try {{
    java.util.HashSet s = new java.util.HashSet();
    s.add({PKG}.CfgRows.RELOAD);
    {PKG}.CfgFile.addReloads(0, s);
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not arm the xp.properties reload: " + t); }}
}}""", skit))
# ... and once more 200 ms later (after the kit has put the levels= line in memory): a save that happened to take the first arm before
# the line existed cannot leave the running table behind the file (set add is idempotent; saveSoon does nothing while a save is due).
# force: the kit's CfgFile.wants() ignores a pure reload arm (RLD without a dirty line - kit gap, reported), so if the dirty save that
# wrote the levels= line already ran before this re-arm (an unrelated save was due, or the scheduler ran this late), a plain saveSoon
# would find nothing to do and leave the arm waiting for the next unrelated edit. force makes that save run (the same force + reload arm
# the kit's own reload op uses): it merges the disk file (no diff = no log line), takes the arm and runs SkillKit.reload after the write.
# When the levels= save is still due, force just joins it (one save, one reload).
karm.addInterface(pool.get("java.lang.Runnable"))
karm.addConstructor(CtNewConstructor.make("public SkillKitArm() { }", karm))
karm.addMethod(CtNewMethod.make(f"""
public void run() {{
  {PKG}.SkillKit.armReload();
  try {{
    {PKG}.CfgFile.force(0);
    {PKG}.CfgFile.saveSoon(0);
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not re-arm the xp.properties reload: " + t); }}
}}""", karm))
skit.addMethod(CtNewMethod.make(f"""
public static void armLater() {{
  try {{ {HSV}.SCHEDULED_EXECUTOR.schedule(new {PKG}.SkillKitArm(), 200L, java.util.concurrent.TimeUnit.MILLISECONDS); }}
  catch (Throwable t) {{ }}
}}""", skit))
# 0.4.12: the class curve rows - the same helpers against the default CLASS table (the d argument) and their own TAIL / LAST memory
skit.addField(CtField.make("public static long[] CTAIL = null;", skit))
skit.addField(CtField.make("public static long[] CLAST = null;", skit))
skit.addMethod(CtNewMethod.make(f"""
public static long[] curListC() {{
  try {{
    Object o = new {PKG}.CfgFn().apply(new Object[] {{ "get", "levels.class" }});
    if (o instanceof String) {{
      long[] r = parseList((String) o);
      if (r != null) return r;
    }}
  }} catch (Throwable t) {{ }}
  long[] p = {PKG}.SkillDefs.CPER;
  long[] c = new long[p.length];
  for (int i = 0; i < p.length; i++) c[i] = p[i];
  return c;
}}""", skit))
skit.addMethod(CtNewMethod.make("""
public static long pctOfD(long[] l, long[] d) {
  double a = 0.0;
  double b = 0.0;
  for (int i = 0; i < l.length; i++) {
    a += (double) l[i];
    b += (double) (i < d.length ? d[i] : d[d.length - 1]);
  }
  if (b <= 0.0) return 100L;
  return Math.round(a * 100.0 / b);
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static long[] withMaxD(long[] cur, int n, long[] d) {
  int len = cur.length;
  long[] r = new long[n];
  int li = len - 1 < d.length ? len - 1 : d.length - 1;
  double base = (double) d[li];
  double f = base > 0.0 ? (double) cur[len - 1] / base : 1.0;
  for (int i = 0; i < n; i++) {
    if (i < len) { r[i] = cur[i]; continue; }
    long di = i < d.length ? d[i] : d[d.length - 1];
    long v = Math.round((double) di * f);
    r[i] = v < 1L ? 1L : v;
  }
  return r;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static long[] scaledToD(long[] cur, long pct, long[] d) {
  double a = 0.0;
  double b = 0.0;
  for (int i = 0; i < cur.length; i++) {
    a += (double) cur[i];
    b += (double) (i < d.length ? d[i] : d[d.length - 1]);
  }
  if (a <= 0.0 || b <= 0.0) return null;
  double f = ((double) pct / 100.0) * b / a;
  long[] r = new long[cur.length];
  for (int i = 0; i < cur.length; i++) {
    double v = (double) cur[i] * f;
    if (v > 1.0E15) return null;
    long x = Math.round(v);
    r[i] = x < 1L ? 1L : x;
  }
  return r;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static synchronized long[] tailForC(long[] cur) {
  long[] t = CTAIL;
  if (t == null || t.length <= cur.length || !sameList(cur, CLAST)) return cur;
  for (int i = 0; i < cur.length; i++) if (t[i] != cur[i]) return cur;
  return t;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static synchronized void keepTailC(long[] cur) {
  if (tailForC(cur) != cur) return;
  long[] c = new long[cur.length];
  for (int i = 0; i < cur.length; i++) c[i] = cur[i];
  CTAIL = c;
}""", skit))
skit.addMethod(CtNewMethod.make("""
public static synchronized void setLastC(long[] l) {
  long[] c = new long[l.length];
  for (int i = 0; i < l.length; i++) c[i] = l[i];
  CLAST = c;
}""", skit))
# review fix R5: what class skills need NOW = the EFFECTIVE class table (SkillDefs.ECUM = min(class list, other list) up to the class max),
# not the raw list a curve row wrote ("level 1 needs 75 XP" at 150% while class skill 1 still comes at 50) - total XP for class skill 1,
# 20 and the class max; nothing while levels.class.sameAsOthers is on (class skills then level on the other list)
skit.addMethod(CtNewMethod.make(f"""
public static String classTotals() {{
  if ({PKG}.SkillDefs.SAME) return "not in use while Class skills use the other list is on";
  long[] e = {PKG}.SkillDefs.ECUM;
  int top = e.length - 1;
  if (top < 1) return "no class levels";
  StringBuilder sb = new StringBuilder();
  sb.append("class skill 1 at ").append({PKG}.SkillDefs.fmt(e[1])).append(" XP");
  if (top > 20) sb.append(", 20 at ").append({PKG}.SkillDefs.fmt(e[20]));
  if (top > 1) sb.append(", ").append(top).append(" at ").append({PKG}.SkillDefs.fmt(e[top]));
  return sb.append(" in total").toString();
}}""", skit))
skit.addMethod(CtNewMethod.make("""
public static String customGet(String key) {
  if ("spell.manaDivisor".equals(key)) return String.valueOf(""" + PKG + """.ManaCost.DIVISOR);
  if ("levels.class.max".equals(key)) return String.valueOf(curListC().length);
  if ("levels.class.scale".equals(key)) return String.valueOf(pctOfD(curListC(), """ + PKG + """.SkillDefs.DEFAULT_CPER));
  long[] l = curList();
  if ("levels.max".equals(key)) return String.valueOf(l.length);
  if ("levels.scale".equals(key)) return String.valueOf(pctOf(l));
  return null;
}""", skit))
skit.addMethod(CtNewMethod.make(f"""
public static Object[] customSet(String key, String value) {{
  long n = -1L;
  try {{ n = Long.parseLong(value.trim()); }} catch (Throwable t) {{ return new Object[] {{ "bad", null, "Must be a whole number." }}; }}
  long[] cur = curList();
  int len = cur.length;
  long[] nl = null;
  String msg = "";
  boolean cls = false;
  if ("levels.max".equals(key)) {{
    if (n < 1L || n > 100L) return new Object[] {{ "bad", null, "Must be a whole number from 1 to 100." }};
    long[] src = cur;
    if (n < (long) len) keepTail(cur);
    else if (n > (long) len) src = tailFor(cur);
    nl = withMax(src, (int) n);
    setLast(nl);
    int back = src.length < (int) n ? src.length : (int) n;
    if (n < (long) len) msg = "Max level: " + n + " (was " + len + ") - levels above " + n + " removed; players keep their XP; raising it again gives them back exactly (until a restart or another curve change). Saved (applies now).";
    else if (n > (long) len && back > len) msg = "Max level: " + n + " (was " + len + ") - levels " + (len + 1) + " to " + back + " back with the XP they had before the cut" + (back < (int) n ? ", " + (back + 1) + " to " + n + " added along the default curve" : "") + ". Saved (applies now).";
    else if (n > (long) len) msg = "Max level: " + n + " (was " + len + ") - levels " + (len + 1) + " to " + n + " added along the default curve. Saved (applies now).";
    else msg = "Max level is already " + n + ".";
  }} else if ("levels.scale".equals(key)) {{
    if (n < 10L || n > 1000L) return new Object[] {{ "bad", null, "Must be a whole number from 10 to 1000%." }};
    nl = scaledTo(cur, n);
    if (nl == null) return new Object[] {{ "bad", null, "That would make a level need more than 1000000000000000 XP." }};
    msg = "Level curve size: " + pctOf(nl) + "% of the default - level 1 needs " + {PKG}.SkillDefs.fmt(nl[0]) + " XP, level " + nl.length + " needs " + {PKG}.SkillDefs.fmt(nl[nl.length - 1]) + ". Saved (applies now).";
  }} else if ("levels.class.max".equals(key)) {{
    // 0.4.12: the class skill list, the levels.max rules against the default CLASS table (own CTAIL / CLAST memory)
    if (n < 1L || n > 100L) return new Object[] {{ "bad", null, "Must be a whole number from 1 to 100." }};
    long[] cc = curListC();
    int clen = cc.length;
    long[] src = cc;
    if (n < (long) clen) keepTailC(cc);
    else if (n > (long) clen) src = tailForC(cc);
    nl = withMaxD(src, (int) n, {PKG}.SkillDefs.DEFAULT_CPER);
    setLastC(nl);
    int back = src.length < (int) n ? src.length : (int) n;
    if (n < (long) clen) msg = "Class max level: " + n + " (was " + clen + ") - class skill levels above " + n + " removed; players keep their XP; raising it again gives them back exactly (until a restart or another class curve change). Saved (applies now).";
    else if (n > (long) clen && back > clen) msg = "Class max level: " + n + " (was " + clen + ") - class levels " + (clen + 1) + " to " + back + " back with the XP they had before the cut" + (back < (int) n ? ", " + (back + 1) + " to " + n + " added along the class curve" : "") + ". Saved (applies now).";
    else if (n > (long) clen) msg = "Class max level: " + n + " (was " + clen + ") - class levels " + (clen + 1) + " to " + n + " added along the class curve. Saved (applies now).";
    else msg = "Class max level is already " + n + ".";
    cls = true;
  }} else if ("levels.class.scale".equals(key)) {{
    if (n < 10L || n > 1000L) return new Object[] {{ "bad", null, "Must be a whole number from 10 to 1000%." }};
    nl = scaledToD(curListC(), n, {PKG}.SkillDefs.DEFAULT_CPER);
    if (nl == null) return new Object[] {{ "bad", null, "That would make a level need more than 1000000000000000 XP." }};
    msg = null;   // review fix R5: written below from the EFFECTIVE class table, once setClassTable has rebuilt it
    cls = true;
  }} else {{
    return new Object[] {{ "unknown", null, "Unknown setting: " + key + "." }};
  }}
  if (cls) {PKG}.SkillDefs.setClassTable(nl, {PKG}.SkillDefs.SAME);
  else {PKG}.SkillDefs.setTable(nl);
  if (msg == null) msg = "Class level curve size: " + pctOfD(nl, {PKG}.SkillDefs.DEFAULT_CPER) + "% - " + classTotals() + ". Saved (applies now).";
  {PKG}.SkillStore.republishAll();   // review fix R9: skill:<uuid> (SkyyHud) follows the new curve at the next 5 s publish
  armReload();
  armLater();
  String val = ("levels.max".equals(key) || "levels.class.max".equals(key)) ? String.valueOf(nl.length) : String.valueOf(cls ? pctOfD(nl, {PKG}.SkillDefs.DEFAULT_CPER) : pctOf(nl));
  return new Object[] {{ "ok", val, msg, new String[] {{ cls ? "levels.class" : "levels", join(nl) }} }};
}}""", skit))
# History restore: the two curve rows follow the restored copy's levels= line (the levels row itself is restored first, row order)
skit.addMethod(CtNewMethod.make(f"""
public static String customRead(String key, java.util.Map vals) {{
  boolean c = key != null && key.startsWith("levels.class.");
  long[] l = null;
  try {{
    Object o = vals == null ? null : vals.get(c ? "levels.class" : "levels");
    if (o instanceof String) l = parseList((String) o);
  }} catch (Throwable t) {{ l = null; }}
  if (l == null) l = c ? {PKG}.SkillDefs.DEFAULT_CPER : {PKG}.SkillDefs.DEFAULT_PER;
  if ("levels.max".equals(key) || "levels.class.max".equals(key)) return String.valueOf(l.length);
  if ("levels.scale".equals(key)) return String.valueOf(pctOf(l));
  if ("levels.class.scale".equals(key)) return String.valueOf(pctOfD(l, {PKG}.SkillDefs.DEFAULT_CPER));
  return null;
}}""", skit))
# ---- check= hooks: null = fine, text = refused with that reason (the kit keeps what the admin typed)
skit.addMethod(CtNewMethod.make("""
public static String checkLevels(String key, String v) {
  if (v == null) return null;
  String t = v.trim();
  String[] ps = t.split(",");
  if (t.length() == 0 || ps.length > 100) return "Write 1 to 100 numbers separated by commas: the XP for level 1, level 2, ...";
  long[] l = parseList(t);
  if (l == null) return "Every entry must be a whole number above 0, separated by commas.";
  for (int i = 0; i < l.length; i++) if (l[i] > 1000000000000000L) return "Level " + (i + 1) + " asks for more than 1000000000000000 XP.";
  return null;
}""", skit))
skit.addMethod(CtNewMethod.make(f"""
public static String checkRule(String key, String v) {{
  if (v == null) return null;
  if ({PKG}.SkillCfg.explRule(v)) return "Exploration XP only comes from other mods (SkyyExploration), never from blocks.";
  if ({PKG}.SkillCfg.parseRule(v) == null) return "Write Skill:XP with Mining, Foraging or Farming (like Mining:5), or none.";
  return null;
}}""", skit))
skit.addMethod(CtNewMethod.make(f"""
public static String checkSkills(String key, String v) {{
  if (v == null) return null;
  boolean bonus = key != null && key.startsWith("bridge.bonus.");
  String[] ps = v.split(",");
  for (int i = 0; i < ps.length; i++) {{
    String t = ps[i].trim();
    if (t.length() == 0) continue;
    int hit = -1;
    for (int s = 0; s < {PKG}.SkillDefs.N; s++) if ({PKG}.SkillDefs.NAMES[s].equalsIgnoreCase(t) || {PKG}.SkillDefs.LABELS[s].equalsIgnoreCase(t)) hit = s;
    if (hit < 0 || hit == {PKG}.SkillDefs.COMBAT) return "Unknown skill: " + t + ". Use names like Mining, Foraging, Farming, Alchemy, Smithing, Cooking.";
    if (bonus && hit == {PKG}.SkillDefs.EXPLORATION) return "Exploration never gets XP bonuses (Skyy's rule) - leave it out.";
  }}
  return null;
}}""", skit))
skit.addMethod(CtNewMethod.make("""
public static String checkTier(String key, String v) {
  if (v == null) return null;
  String t = v.trim();
  String[] ps = t.split(",");
  if (t.length() == 0 || ps.length > 5) return "Write 1 to 5 whole numbers separated by commas (bench tier I to V).";
  for (int i = 0; i < ps.length; i++) {
    long x = -1L;
    try { x = Long.parseLong(ps[i].trim()); } catch (Throwable e) { return "Every entry must be a whole number (0 or more)."; }
    if (x < 0L) return "Every entry must be a whole number (0 or more).";
  }
  return null;
}""", skit))

# ================= commands =================
tcmd.addField(CtField.make(f"public {RA} skillArg;", tcmd))
tcmd.addConstructor(CtNewConstructor.make(f"""
public TopCmd() {{
  super("top", "Top 10 players of a skill: /skills top mining");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | sorcery | fury | divinity | assassination | shaman", {ATY}.STRING);
  setPermissionGroups(new String[] {{ "hytale:Adventurer" }});
}}""", tcmd))
tcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    int s = {PKG}.SkillClass.argSlot(pr, String.valueOf(ctx.get(this.skillArg)));
    if (s < 0) return;
    java.util.ArrayList rows = {PKG}.SkillTop.all(s);
    pr.sendMessage({MSG}.raw("[Skills] Top 10 " + {PKG}.SkillDefs.LABELS[s] + ":").color("#ffc800"));
    int n = rows.size() < 10 ? rows.size() : 10;
    if (n == 0) pr.sendMessage({MSG}.raw("  nobody has any XP yet"));
    for (int i = 0; i < n; i++) {{
      Object[] e = (Object[]) rows.get(i);
      long x = ((Long) e[1]).longValue();
      pr.sendMessage({MSG}.raw("  " + (i + 1) + ". " + e[0] + " - level " + {PKG}.SkillDefs.levelOf(s, x) + " (" + {PKG}.SkillDefs.fmt(x) + " XP)"));
    }}
    int rank = {PKG}.SkillTop.rankOf(rows, pr.getUuid());
    if (rank > 10) pr.sendMessage({MSG}.raw("  you: #" + rank + " of " + rows.size()));
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("/skills top failed: " + t); pr.sendMessage({MSG}.raw("[Skills] could not read the leaderboard")); }}
}}""", tcmd))

qcmd.addConstructor(CtNewConstructor.make('public QuietCmd() { super("quiet", "Toggle the +XP chat messages (level ups always show)"); setPermissionGroups(new String[] { "hytale:Adventurer" }); }', qcmd))
qcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  java.util.UUID u = pr.getUuid();
  Object f = {PKG}.SkillStore.bridge().get("settings:fn:set");
  if (f instanceof java.util.function.Function) {{
    java.util.function.Function sf = (java.util.function.Function) f;
    boolean anyOn = {PKG}.SkillStore.notifyOn(u, "skills.xpGain") || {PKG}.SkillStore.notifyOn(u, "skills.doubleDrop") || {PKG}.SkillStore.notifyOn(u, "skills.extraPotion");
    Boolean nv = anyOn ? Boolean.FALSE : Boolean.TRUE;
    int ok = 0;
    if (Boolean.TRUE.equals(sf.apply(new Object[] {{ u, "skills.xpGain", nv }}))) ok++;
    if (Boolean.TRUE.equals(sf.apply(new Object[] {{ u, "skills.doubleDrop", nv }}))) ok++;
    if (Boolean.TRUE.equals(sf.apply(new Object[] {{ u, "skills.extraPotion", nv }}))) ok++;
    if (ok < 3) {{ pr.sendMessage({MSG}.raw("[Skills] Could not save your settings - try again or tell an admin.")); return; }}
    pr.sendMessage({MSG}.raw(anyOn ? "[Skills] XP, double-drop and extra-potion messages hidden (level ups still show). One switch per message: /settings" : "[Skills] XP, double-drop and extra-potion messages shown. One switch per message: /settings"));
    return;
  }}
  boolean q = {PKG}.SkillStore.toggleQuiet(pr.getUuid());
  pr.sendMessage({MSG}.raw(q ? "[Skills] XP messages hidden (level ups still show). /skills quiet again to show them." : "[Skills] XP messages shown."));
}}""", qcmd))

rcmd.addConstructor(CtNewConstructor.make('public ReloadCmd() { super("reload", "(admin) Re-read Skyy_SkyySkills/xp.properties"); requirePermission("skyyskills.admin"); setPermissionGroups(new String[0]); }', rcmd))
rcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  if (!pr.hasPermission("skyyskills.admin")) {{ pr.sendMessage({MSG}.raw("[Skills] no permission (skyyskills.admin)")); return; }}
  // 0.4.3: xp.properties is read twice ON PURPOSE. The kit's reload op merges hand edits (logged via=file) and, only when it found some
  // or in-game edits were pending, runs SkillKit.reload again on its save task right after this reply; the synchronous load below keeps
  // the 0.4.2 reply text. Both passes are idempotent (SkillCfg.load is synchronized) - not an oversight.
  String kr = "";
  try {{
    Object o = new {PKG}.CfgFn().apply(new Object[] {{ "reload", pr.getUuid(), pr.getUsername(), "command" }});
    if (o instanceof Object[] && ((Object[]) o).length > 2 && ((Object[]) o)[2] != null) kr = " (" + String.valueOf(((Object[]) o)[2]) + ")";
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("config kit reload failed: " + t); }}
  String res = {PKG}.SkillCfg.load();
  {PKG}.SkillStore.republishAll();   // review fix R9 (0.4.12)
  {PKG}.Acro.djPublish();
  pr.sendMessage({MSG}.raw("[Skills] xp.properties reloaded: " + res + kr));
}}""", rcmd))

# /skills stats <skill> (0.3): a subcommand with a required arg (optional args are not positional - HANDOFF command rules)
scmd.addField(CtField.make(f"public {RA} skillArg;", scmd))
scmd.addConstructor(CtNewConstructor.make(f"""
public StatsCmd() {{
  super("stats", "Open the Stats page of a skill: /skills stats mining (or /skills stats overall)");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | sorcery | fury | divinity | assassination | shaman | overall (the Overall Level page)", {ATY}.STRING);
  setPermissionGroups(new String[] {{ "hytale:Adventurer" }});
}}""", scmd))
scmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    String arg = String.valueOf(ctx.get(this.skillArg)).trim();
    if (arg.equalsIgnoreCase("overall")) {{
      {PLA} po = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
      if (po != null) po.getPageManager().openCustomPage(ref, store, new {PKG}.OverallPage(pr));
      return;
    }}
    int s = {PKG}.SkillClass.argSlot(pr, arg);
    if (s < 0) return;
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.StatsPage(pr, s));
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("/skills stats failed: " + t);
    pr.sendMessage({MSG}.raw("[Skills] could not open the stats page"));
  }}
}}""", scmd))
# /skills xp <skill> <amount> (0.4 admin test helper): gives yourself RAW XP (no multiplier, no cap, creative allowed) through the normal
# award path (chat line, level ups, coins, publish). Two required args (optional args are not positional - HANDOFF command rules).
xcmd.addField(CtField.make(f"public {RA} skillArg;", xcmd))
xcmd.addField(CtField.make(f"public {RA} amountArg;", xcmd))
xcmd.addConstructor(CtNewConstructor.make(f"""
public XpCmd() {{
  super("xp", "(admin) Give yourself skill XP for testing: /skills xp alchemy 3100000 (also 500k, 3.1m)");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | sorcery | fury | divinity | assassination | shaman", {ATY}.STRING);
  this.amountArg = withRequiredArg("amount", "raw XP, e.g. 3100000 or 3.1m", {ATY}.STRING);
  requirePermission("skyyskills.admin");
  setPermissionGroups(new String[0]);
}}""", xcmd))
xcmd.addMethod(CtNewMethod.make("""
public static long parseAmount(String v) {
  if (v == null) return -1L;
  String t = v.trim().toLowerCase().replace(",", "").replace("_", "");
  double mul = 1.0;
  if (t.endsWith("k")) { mul = 1000.0; t = t.substring(0, t.length() - 1); }
  else if (t.endsWith("m")) { mul = 1000000.0; t = t.substring(0, t.length() - 1); }
  else if (t.endsWith("b")) { mul = 1000000000.0; t = t.substring(0, t.length() - 1); }
  try {
    double x = Double.parseDouble(t) * mul;
    if (Double.isNaN(x) || x < 1.0 || x > 1000000000.0) return -1L;
    return Math.round(x);
  } catch (Throwable e) { return -1L; }
}""", xcmd))
xcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    if (!pr.hasPermission("skyyskills.admin")) {{ pr.sendMessage({MSG}.raw("[Skills] no permission (skyyskills.admin)")); return; }}
    int s = {PKG}.SkillClass.argSlot(pr, String.valueOf(ctx.get(this.skillArg)));
    if (s < 0) return;
    if (s == {PKG}.SkillDefs.COMBAT) {{ pr.sendMessage({MSG}.raw("[Skills] You have no class - choose one with /class, or name a class skill (archery, swordsmanship, sorcery, fury, divinity).")); return; }}
    long amt = parseAmount(String.valueOf(ctx.get(this.amountArg)));
    if (amt <= 0L) {{ pr.sendMessage({MSG}.raw("[Skills] amount must be 1 .. 1000000000 (e.g. 3100000, 500k, 3.1m)")); return; }}
    {PKG}.SkillXp.gain3(pr, s, amt, true, false);
    {PKG}.SkillCfg.info("admin /skills xp: " + pr.getUsername() + " gave themself " + amt + " " + {PKG}.SkillDefs.NAMES[s] + " XP (" + {PKG}.SkillStore.pkey(pr.getUuid()) + ")");
    pr.sendMessage({MSG}.raw("[Skills] +" + amt + " " + {PKG}.SkillClass.skillName(pr.getUuid(), s) + " XP (admin test, raw - no multiplier, no tree bonus). Level now " + {PKG}.SkillStore.level(pr.getUuid(), s) + ".").color("#ffc800"));
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("/skills xp failed: " + t);
    pr.sendMessage({MSG}.raw("[Skills] could not give the XP"));
  }}
}}""", xcmd))
# /skills mana (0.4.12 admin debug): the caller's LIVE Mana regen - Mana now / max, in or out of combat (the regen entry's own conditions,
# like ManaRegen.tick), the last hit, what SkyySkills adds right now, the Mana Regen boosts. World thread (AbstractPlayerCommand runs execute
# on the player's world); admin only: requirePermission + no groups (HANDOFF command rules, lint perm_group_leaks).
mcmd.addConstructor(CtNewConstructor.make('public ManaCmd() { super("mana", "(admin) Your live Mana regen: in or out of combat, boosts, rates"); requirePermission("skyyskills.admin"); setPermissionGroups(new String[0]); }', mcmd))
mcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    if (!pr.hasPermission("skyyskills.admin")) {{ pr.sendMessage({MSG}.raw("[Skills] no permission (skyyskills.admin)")); return; }}
    java.util.UUID u = pr.getUuid();
    {ESM} m = ({ESM}) store.getComponent(ref, {ESM}.getComponentType());
    int mi = {DST}.getMana();
    {ESV} v = null;
    if (m != null && mi >= 0) v = m.get(mi);
    if (v == null) pr.sendMessage({MSG}.raw("[Skills] Mana: this player has no Mana value").color("#c8b070"));
    else {{
      java.time.Instant now = (({TMR}) store.getResource({TMR}.getResourceType())).getNow();
      float[] r = {PKG}.ManaRegen.rates(store, ref, now, v.getRegeneratingValues());
      double p = {PKG}.ManaRegen.total(u);
      int f = {PKG}.ManaRegen.IN_COMBAT;
      String st = {PKG}.ManaRegen.stateLine(r, p, f, v.getMax());   // 0.4.13: 0.4.12's lines + "charging - Mana still regenerates"
      String hit = "";
      try {{
        {DDC} dd = ({DDC}) store.getComponent(ref, {DDC}.getComponentType());
        if (dd != null && dd.getLastDamageTime() != null) {{
          long ms = java.time.Duration.between(dd.getLastDamageTime(), now).toMillis();
          if (ms >= 0L && ms < 86400000L) hit = " - last hit " + {PKG}.Overall.num((double) ms / 1000.0) + " s ago";
        }}
      }} catch (Throwable t) {{ }}
      pr.sendMessage({MSG}.raw("[Skills] Mana " + {PKG}.Overall.num((double) v.get()) + " / " + {PKG}.Overall.num((double) v.getMax()) + " - " + st + hit).color("#c8b070"));
      pr.sendMessage({MSG}.raw("[Skills] " + {PKG}.ClassMana.breakdown(u, m, mi, v.getMax())).color("#c8b070"));   // 0.4.15: max Mana by source
    }}
    pr.sendMessage({MSG}.raw("[Skills] " + {PKG}.ManaRegen.text(u)).color("#c8b070"));
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("/skills mana failed: " + t);
    pr.sendMessage({MSG}.raw("[Skills] could not read your Mana regen"));
  }}
}}""", mcmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public SkillsCmd() {{
  super("skills", "Open your skills page; /skills stats <skill>, /skills top <skill>, /skills quiet (admins: /skills mana)");
  addAliases(new String[] {{ "skill" }});
  setPermissionGroups(new String[] {{ "hytale:Adventurer" }});
  addSubCommand(new {PKG}.StatsCmd());
  addSubCommand(new {PKG}.TopCmd());
  addSubCommand(new {PKG}.QuietCmd());
  addSubCommand(new {PKG}.ReloadCmd());
  addSubCommand(new {PKG}.XpCmd());
  addSubCommand(new {PKG}.ManaCmd());
}}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.SkillsPage(pr));
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("/skills failed: " + t);
    pr.sendMessage({MSG}.raw("[Skills] could not open the page: " + {PKG}.SkillStore.levelsString(pr.getUuid())));
  }}
}}""", cmd))

# ================= 1s ticker: feedback leftovers, bridge publish (5s), save (10s), placed blocks (60s) =================
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addField(CtField.make("public long n;", tick))
tick.addConstructor(CtNewConstructor.make("public SkillTick() { this.n = 0L; }", tick))
tick.addMethod(CtNewMethod.make(f"""
public void run() {{
  this.n++;
  try {{ {PKG}.SkillMsg.flushDue(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.PartyXp.flushDue(); }} catch (Throwable t) {{ }}
  if (this.n % 5L == 0L) {{ try {{ {PKG}.SkillStore.publishOnline(); }} catch (Throwable t) {{ }} }}
  if (this.n % 10L == 0L) {{ try {{ {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }} }}
  if (this.n % 60L == 0L) {{ try {{ {PKG}.PlacedStore.flush(); }} catch (Throwable t) {{ }} }}
  if (this.n % 30L == 0L) {{ try {{ {PKG}.Acro.retainOnline(); }} catch (Throwable t) {{ }} try {{ {PKG}.PartyXp.retainOnline(); }} catch (Throwable t) {{ }} }}
  try {{ {PKG}.ManaGuard.tick(this.n); }} catch (Throwable t) {{ }}
  try {{ {PKG}.ClassCurve.flush(); }} catch (Throwable t) {{ }}   // 0.4.12: the class skill curve record (only after a notice was told)
}}""", tick))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyySkillsPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.SkillCfg.LOG = getLogger();
  java.nio.file.Path base = getDataDirectory().resolveSibling("Skyy_SkyySkills");
  {PKG}.SkillStore.DIR = base.resolve("players");
  {PKG}.PlacedStore.DIR = base.resolve("placed");
  {PKG}.SkillCfg.FILE = base.resolve("xp.properties");
  {PKG}.ManaMig.run();   // 0.4.8: mana.magicBase / mana.magicClasses -> Base Mana by class, once, before the file is read and the kit starts
  {PKG}.HealMig.run();   // 0.4.11: untouched heal XP lines 0.2 / 0.25 / 300 -> 1 / 1.25 / 900 (final heal XP), once; History first
  {PKG}.DocMig.run();    // 0.4.14: the stale Mana regen comment ('never while charging'), once; History first
  {PKG}.ClassManaMig.run();   // 0.4.15: the max Mana per class level lines into an existing xp.properties, once; History first
  String rules = {PKG}.SkillCfg.load();
  String curve = {PKG}.ClassCurve.start(base);   // 0.4.12: the first 0.4.12 start records once which profiles' class levels rose
  {PKG}.Acro.djPublish();
  getEntityStoreRegistry().registerSystem(new {PKG}.BreakSys());
  try {{
    getEntityStoreRegistry().registerSystem(new {PKG}.EnvSys());
  }} catch (Throwable t) {{
    {PKG}.FellCfg.BROKEN = true;
    {PKG}.SkillCfg.warn("could not register EnvSys (explosion / fire guard for felled trees): " + t + " - felled trees stay OFF until the next restart");
  }}
  getEntityStoreRegistry().registerSystem(new {PKG}.PlaceSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.HarvestSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.KillSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.AcroSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.AcroFallSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.CombatDmgSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.AcroFallSeenSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.CraftSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.SmeltSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.XbowSlotSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.SickleSys());   // 0.4.14: sickle swing harvests (InteractivelyPickupItemEvent)
  try {{
    getEntityStoreRegistry().registerSystem(new {PKG}.RollSys());   // 0.4.14: roll landings, BEFORE the engine's FallDamagePlayers
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("could not register RollSys (roll landings): " + t + " - rolled landings pay as before until the next restart");
  }}
  {PKG}.MoveSync.checkProto({PKG}.Acro.MOD);
  boolean fallOwner = {PKG}.MoveSync.ownsFall({PKG}.Acro.MOD);
  getCommandRegistry().registerCommand(new {PKG}.SkillsCmd());
  {PKG}.SkillStore.bridge().put("skill:fn:level", new {PKG}.SkillFn());
  {PKG}.SkillStore.bridge().put("skill:fn:addxp", new {PKG}.SkillAddFn());
  {PKG}.SkillStore.bridge().put("skill:fn:craftxp", new {PKG}.SkillCraftFn());
  {PKG}.SkillStore.bridge().put("skill:fn:xp", new {PKG}.SkillXpFn());
  {PKG}.SkillStore.bridge().put("skill:fn:drops", new {PKG}.SkillDropsFn());
  {PKG}.SkillStore.bridge().put("skill:fn:placed", new {PKG}.SkillPlacedFn());
  {PKG}.SkillStore.bridge().putIfAbsent("skill:on:gather", new java.util.concurrent.ConcurrentHashMap());
  {PKG}.SkillStore.bridge().putIfAbsent("skill:on:felled", new java.util.concurrent.ConcurrentHashMap());
  {PKG}.SkillStore.bridge().put("skill:fn:felledBy", new {PKG}.FelledByFn());
  {PKG}.SkillStore.bridge().put("skill:fn:healxp", new {PKG}.SkillHealFn());
  {PKG}.SkillStore.bridge().put("skill:fn:overall", new {PKG}.OverallFn());
  {PKG}.SkillStore.bridge().put("skill:fn:manaregen", new {PKG}.ManaRegenFn());   // 0.4.12: the Mana Regen % registry
  {PKG}.SkillStore.bridge().put("skill:fn:combat", new {PKG}.CombatFn());   // 0.4.13: the combat state (SkyyHud's Combat widget)
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SkillTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyySkills] {VERSION} ready ({KIT_ID}) - /skills; rows Alchemy (Alchemy Bench) / Smithing (Furnace) / Cooking (via SkyyCooking) / Exploration (via SkyyExploration, no boosters); felled trees " + {PKG}.FellCfg.text() + "; double jump " + {PKG}.AcroCfg.djText() + " (bridge skill:dj:key); party combat XP " + {PKG}.PartyCfg.text() + "; divinity heal XP " + {PKG}.DivCfg.text() + "; crossbows stay loaded " + {PKG}.XbowCfg.text() + "; overall level " + {PKG}.OverallCfg.text() + "; spell costs /" + {PKG}.ManaCost.DIVISOR + " (" + {PKG}.ManaCost.N + " items + " + {PKG}.ManaCost.INT_N + " interactions: every paid cast checks what it spends, " + {PKG}.ManaCost.GN + " casters)" + "; class skills level on " + {PKG}.SkillCfg.curveText() + (curve.length() > 0 ? " (" + curve + ")" : "") + "; in-combat Mana regen " + {PKG}.ManaRegen.IN_COMBAT + "% of (vanilla + Mana Regen boosts)" + "; kill XP by mob level " + {PKG}.MobXp.text() + "; roll landings " + {PKG}.AcroCfg.rollText() + "; gathering pace " + {PKG}.GatherPace.text() + "; sickle swings " + {PKG}.Sickle.text() + "; max Mana per class level " + {PKG}.ClassMana.text() + "; staff handover: the " + {PKG}.ManaCost.ARM_IDS.length + " ladder staffs come from SkyyArmory 0.1+" + "; bridge skill:fn:addxp + skill:fn:craftxp + skill:fn:healxp (optional Boolean self) + skill:fn:overall + skill:overall:<uuid> + skill:fn:manaregen + skill:fn:combat; trees bridge on (tree bonuses " + ({PKG}.BridgeCfg.BONUS ? "XP for " + {PKG}.BridgeCfg.BONUS_TEXT + " (grants from other mods: " + ({PKG}.BridgeCfg.BONUS_ADDXP_TEXT.length() > 0 ? {PKG}.BridgeCfg.BONUS_ADDXP_TEXT : "none") + ") + double drops" : "off") + ", SkyyTrees " + ({PKG}.SkillBonus.treesOn() ? "found" : "not loaded yet") + "); xp rules: " + rules + "; combat = class skill (SkyyClasses " + ({PKG}.SkillClass.allowedFn() != null ? "found" : "not loaded yet - no combat XP without it") + ")" + (fallOwner ? "" : "; fall damage bonuses are applied by " + {PKG}.MoveSync.bridge().get({PKG}.MoveSync.OWNER_FALL)));
  {PKG}.SkillStore.regSetting("skills.xpGain", "Skill XP gains", "skills", true, "+12 Mining XP (340/500) while you gather, fight, smelt, brew and move");
  {PKG}.SkillStore.regSetting("skills.levelUp", "Skill level-ups", "skills", true, "SKILL LEVEL UP with the coins it paid and the XP for the next level");
  {PKG}.SkillStore.regSetting("skills.doubleDrop", "Double drops", "skills", true, "Double drop x3! from the Mining, Foraging and Farming perks");
  {PKG}.SkillStore.regSetting("skills.extraPotion", "Extra potions", "skills", true, "Extra potion! from the Alchemy perk");
  {PKG}.SkillStore.regSetting("skills.combatHints", "No combat XP hints", "skills", true, "Why a kill gave no combat XP - once per reason each session");
  {PKG}.SkillStore.regSetting("rewards.late", "Late reward payouts", "coins", true, "Coins and XP paid later because another mod was not ready");
  {PKG}.SkillStore.regSetting("skills.overallUp", "Overall Level ups", "skills", true, "OVERALL LEVEL UP 12 -> 13 with the max Health and Mana it added");
  {PKG}.SkillStore.regSetting("skills.xbowMeter", "Crossbows keep the big-arrow meter", "combat", true, "Your crossbow's big-arrow meter comes back with its bolts when you switch back to it");
  {PKG}.SkillStore.regSetting("skills.xbowSound", "Crossbow reload sound", "combat", true, "The crossbow load sound when your kept bolts go back in (Archery perk)");
  {PKG}.SkillStore.regSetting("skills.xbowHint", "Crossbow reload chat line", "combat", true, "Crossbow reloaded - 6 bolts back in - when your kept bolts return");
  {PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());
  {PKG}.ManaMig.keepCopy();   // 0.4.8: the pre-move xp.properties into the kit's history (only after a move this start)
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{
  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ if (!{PKG}.SkillStore.DIRTY.isEmpty()) {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.ClassCurve.flush(); }} catch (Throwable t) {{ }}   // 0.4.12
  try {{ {PKG}.PlacedStore.flush(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:level"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:addxp"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:craftxp"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:xp"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:drops"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:placed"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:felledBy"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:healxp"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:overall"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:manaregen"); }} catch (Throwable t) {{ }}   // 0.4.12
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:combat"); }} catch (Throwable t) {{ }}   // 0.4.13
  try {{ {PKG}.SkillStore.bridge().remove("skill:dj:key"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.Fell.endAll(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.MoveSync.releaseFall({PKG}.Acro.MOD); }} catch (Throwable t) {{ }}
  super.shutdown();
}}""", pl))

for c in (defs, cfg, sto, pub, fn, msg, fl, xp, plc, hg, btk, ptk, htk, bsy, psy, usy, ksy, tcm, top, page, tcmd, qcmd, rcmd, cmd, tick, pl, acfg, mvs_, acro, asy, afs,
          pcfg, scls, perk, cds, spg, scmd, alc, smc, bgc, rxp, brew, bxp, ctk, stk, btsk, csy, sxu, ssy, afss, afn, cfn, xcmd, sbn, xfn, dfn, pfn, exc,
          fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft, skit, karm, dvc, hxp, hfn, xcf, xst, xbw, xss, ovc, ovl, ofn, opg,
          mcost, mmig, mgd, hmig, ccv, mrg, mrfn, mcmd, cmbf,
          mxp, rsy, gpc, skl, sksy, sktk, dmig,
          cman, cmig):   # 0.4.11: + HealMig; 0.4.12: + ClassCurve, ManaRegen, ManaRegenFn, ManaCmd; 0.4.13: + CombatFn; 0.4.14: + MobXp, RollSys, GatherPace, Sickle, SickleSys, SickleTask, DocMig; 0.4.15: + ClassMana, ClassManaMig
    c.writeFile(OUT)
kit.write(OUT)   # 0.4.3: the kit's deferred checks (SkillKit hooks) + its 7 classes
print("classes written")

jar = os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)
m = B.manifest("SkyySkills", VERSION, "SkyWynn skills (Hypixel SkyBlock style): Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class combat skill (SkyyClasses: Archery, Swordsmanship, Sorcery, Fury, Divinity) to level 100. XP from breaking blocks (a felled tree pays every log that falls), ripe crops, brewing at the Alchemy Bench, smelting at a Furnace, cooking (SkyyCooking), exploring (SkyyExploration - never boosted), kills with class weapons (nearby SkyyParty members get a share in their own class skill), Priest heals on party members (Divinity, from SkyyClasses) and running / jumping / big survived falls / dodging (+ the Acrobatics tree Double Jump: jump again in mid-air). Alchemy makes potion effects last longer and adds max Mana; Exploration adds max Stamina; crossbows stay loaded from Archery 5 by default (the level is set in Server Setup; Archers keep their bolts and the big-arrow meter across hotbar switches and teleports, paid with the arrows vanilla refunds, with the load sound and a chat hint). Spells cost the vanilla Mana / 5 and every paid cast checks exactly what it spends (wand 5, staff 10, spellbook 20: item + cast check overrides generated at build time) and Mages and Priests can cast their starter weapons from level 1 (Base Mana 10, Mage and Priest 30 - Base Mana by class in Server Setup); an Overall Level - the average of your skills - that adds max Health and Mana (Server Setup). Priests earn Divinity XP for healing others and themselves. Class skills earn 3x XP from kills by default (Class skill XP multiplier in Server Setup: kills and party shares; gathering skills unchanged). Priest heal XP is what the Priest gets: 1 per HP on others, 1.25 on yourself, up to 900 a minute (Server Setup). Class skills level on their own, flatter table (class skill 20 at 21,540 XP, 40 at 209,090; never slower than the other skills' table; Server Setup Levels tab) - existing XP is kept and players are told once, with the coins of the levels they gained. Mana refills in combat at 50% (Server Setup: In-combat Mana regen; vanilla stops it for 6 s after a hit), boosts other mods register count in and out of combat. Kill XP grows with the SkyyMobs level and the level gap to your class skill (up to +250%; party members use their own class skill); a crouch-roll landing pays +50% Acrobatics XP; Mining, Foraging and Farming XP x3 to level 10, easing to x1.5 by level 20; sickle swings pay Farming XP and roll double drops (Server Setup). Priests gain +5 max Mana per Divinity level and Mages +10 per Sorcery level (Server Setup: Max Mana per class level); the 8 ladder staffs (Wood to Onyxium) come from SkyyArmory 0.1+ (its staff ladder - install both together). Uninstall / downgrade: switch Base Mana and Overall Level off in Server Setup first. Perks: max health / stamina, double drops, class weapon damage; Acrobatics raises speed, jump height and dodge push and lowers fall damage (shared Skyy movement protocol). Stats page per skill. Every setting editable in game (SkyWynn Menu Server Setup, optional) and per-player chat switches (/settings, optional). Skill tree bonuses and Tree buttons with SkyyTrees (optional). Level ups pay SkyyCoins. /skills. Per profile with SkyyProfiles (optional). Zero dependencies.", PKG + ".SkyySkillsPlugin")
m["IncludesAssetPack"] = True   # 0.4.8: the spell cost item overrides (SPELL_FILES; 0.4.9 + the cast check interactions); pages stay inline
assert SPELL_FILES and all(_p.startswith(("Server/Item/Items/", "Server/Item/Interactions/")) for _p in SPELL_FILES) and not any(_p.endswith(".ui") for _p in SPELL_FILES)
assert len(SPELL_FILES) == len(SPELL_PLAN) + len(SPELL_INT_PLAN), (len(SPELL_FILES), len(SPELL_PLAN), len(SPELL_INT_PLAN))
assert "%s:%s" % (m["Group"], m["Name"]) == SKILLS_PACK, (m["Group"], m["Name"], SKILLS_PACK)   # the pack ManaGuard's pack check expects
B.assemble(jar, m, OUT, SPELL_FILES)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyySkills.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyySkills" % VERSION, disable_prefix="Skyy:")
