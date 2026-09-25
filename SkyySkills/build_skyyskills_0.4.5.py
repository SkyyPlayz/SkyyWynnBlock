"""SkyySkills 0.4.5 - build script (derived from 0.4.4 by tools/skills_0_4_5_patch.py - edit the patch, not this file;
0.4.4 was derived from 0.4.3 by tools/skills_0_4_4_patch.py, 0.4.3 from 0.4.2 by tools/skills_0_4_3_patch.py, 0.4.2 from 0.4.1 by
tools/skills_0_4_2_patch.py, 0.4.1 from 0.4 by tools/skills_0_4_1_patch.py, 0.4 from 0.3.2 by tools/skills_0_4_patch.py, 0.3.2 from 0.3.1
by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
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
  NOT HERE (spec 2.9 / 6): shortbows (LOCKED Skyy 2026-09-25: crossbows only), the Signature meter, the off-hand slot.
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
Run:   python build_skyyskills_0.4.5.py            -> SkyySkills/SkyySkills-0.4.5.jar
       python build_skyyskills_0.4.5.py --deploy   -> also copies to Mods/SkyySkills.jar and enables it in the HUD mod world
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

VERSION = "0.4.5"
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
L.append("# is the max level, at most 100)")
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
# 0.4.4: Divinity XP from Priest heals (research/Classes-Berserker-Priest-Spec.md 3.4 / 3.5). Appended once to a file without
# divinity.healXp.enabled (DivCfg.ensureDefaults).
DIV_L = []
DIV_L.append("# ---------- Divinity (SkyySkills 0.4.4) - Priest heals from SkyyClasses 0.1.6 (skill:fn:healxp) ----------")
DIV_L.append("# Comments must stay on their own lines.")
DIV_L.append("# A Priest (class skill Divinity) earns healXpPerHp Divinity XP for every 1 HP their weapon hits heal on OTHER party members.")
DIV_L.append("# LOCKED Skyy 2026-09-25: healing themself pays 0.25 XP per HP (was 0). Others stay 0.2. Cap stays 300 a minute.")
DIV_L.append("# This build still pays nothing for a self-heal. The next Skills build reads that 0.25.")
DIV_L.append("# healXpMaxPerMinute: most heal XP per Priest in one 60 second window, counted before the xp")
DIV_L.append("# multiplier (0 = no limit). Kills pay Divinity XP like every class skill (combat.* keys) and are not counted here.")
DIV_L.append("divinity.healXp.enabled=true")
DIV_L.append("divinity.healXpPerHp=0.2")
DIV_L.append("divinity.healXpMaxPerMinute=300")
L.append("")
L.extend(DIV_L)
DIV_DEFAULTS = "\n".join(DIV_L) + "\n"
assert all(ord(ch) < 128 for ch in DIV_DEFAULTS) and '"' not in DIV_DEFAULTS
DIV_LIT = json.dumps(DIV_DEFAULTS)
# 0.4.5: Crossbows stay loaded, the Archery level-5 reward (research/Crossbow-Loaded-Spec.md 3.2). Appended once to a file without
# perk.archery.keepLoaded.enabled (XbowCfg.ensureDefaults).
XBOW_L = []
XBOW_L.append("# ---------- Crossbows stay loaded (SkyySkills 0.4.5) - the Archery level-5 reward, research/Crossbow-Loaded-Spec.md ----------")
XBOW_L.append("# Comments must stay on their own lines.")
XBOW_L.append("# LOCKED Skyy 2026-09-25: Archery level 5, Archer class only, crossbows only (not shortbows).")
XBOW_L.append("# An Archer whose Archery level is at least 'level' keeps a crossbow's loaded bolts when switching hotbar slots and back.")
XBOW_L.append("# Vanilla gives the bolts back as Crude Arrows when you switch away; switching back loads them again, paid with those arrows.")
XBOW_L.append("# LOCKED Skyy 2026-09-25: loaded bolts survive teleports. This build still wipes them on a world change.")
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
defs.addField(CtField.make("public static final int ACROBATICS = 4;", defs))
defs.addField(CtField.make("public static final int ALCHEMY = 10;", defs))
defs.addField(CtField.make("public static final int SMITHING = 11;", defs))
defs.addField(CtField.make("public static final int COOKING = 12;", defs))
defs.addField(CtField.make("public static final int EXPLORATION = 13;", defs))   # 0.4.1
defs.addField(CtField.make("public static final int FURY = %d;" % FURY_SLOT, defs))           # 0.4.4 Berserker
defs.addField(CtField.make("public static final int DIVINITY = %d;" % DIVINITY_SLOT, defs))   # 0.4.4 Priest
# /skills rows (3 = the class row: the current class's weapon skill, or the "choose a class" row)
defs.addField(CtField.make("public static final int[] ROW_SLOTS = new int[] { 0, 1, 2, 10, 11, 12, 4, 13, 3 };", defs))   # 0.4.1: Exploration after Acrobatics
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
defs.addMethod(CtNewMethod.make("""
public static synchronized void setTable(long[] per) {
  if (per == null || per.length == 0) return;
  long[] cum = new long[per.length + 1];
  cum[0] = 0L;
  for (int i = 0; i < per.length; i++) cum[i + 1] = cum[i] + per[i];
  PER = per; CUM = cum; MAX = per.length;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int levelOf(long total) {
  long[] cum = CUM;
  int max = cum.length - 1;
  int l = 0;
  while (l < max && total >= cum[l + 1]) l++;
  return l;
}""", defs))
# XP into the current level
defs.addMethod(CtNewMethod.make("""
public static long intoLevel(long total) {
  int l = levelOf(total);
  return total - CUM[l];
}""", defs))
# XP the current level needs in total (0 at max level)
defs.addMethod(CtNewMethod.make("""
public static long needFor(long total) {
  int l = levelOf(total);
  long[] per = PER;
  return l < per.length ? per[l] : 0L;
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
public static String progress(long total) {
  long need = needFor(total);
  if (need <= 0L) return "MAX";
  return fmt(intoLevel(total)) + "/" + fmt(need);
}""", defs))

# ================= SkillCfg: xp.properties =================
cfg.addField(CtField.make("public static java.nio.file.Path FILE;", cfg))
cfg.addField(CtField.make(f"public static {LOG} LOG;", cfg))
cfg.addField(CtField.make("public static final String DEFAULTS = " + DEFAULTS_LIT + ";", cfg))
cfg.addField(CtField.make("public static volatile double MULT = 1.0;", cfg))
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
for decl in ("boolean ON = true", "double PER_HP = 0.2", "long MAX_MIN = 300L"):
    dvc.addField(CtField.make("public static volatile " + decl + ";", dvc))
dvc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ON = {PKG}.SkillCfg.bool(p, "divinity.healXp.enabled", true);
  double r = {PKG}.SkillCfg.dbl(p, "divinity.healXpPerHp", 0.2);
  PER_HP = (Double.isNaN(r) || r < 0.0) ? 0.0 : (r > 100.0 ? 100.0 : r);
  long m = {PKG}.SkillCfg.lng(p, "divinity.healXpMaxPerMinute", 300L);
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
dvc.addMethod(CtNewMethod.make("""
public static boolean on() {
  return ON && PER_HP > 0.0;
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
  return "on (" + num(PER_HP) + " XP per HP healed on others" + (MAX_MIN > 0L ? ", up to " + MAX_MIN + " a minute" : "") + ")";
}""", dvc))
# the Stats page's Divinity "Boosts right now" line (spec 3.6)
dvc.addMethod(CtNewMethod.make("""
public static String statsLine() {
  if (!on()) return "Divinity XP from healing is off on this server";
  return "Healing party members pays " + num(PER_HP) + " Divinity XP per HP" + (MAX_MIN > 0L ? " (up to " + MAX_MIN + " a minute)" : "");
}""", dvc))

# ================= XbowCfg (0.4.5): perk.archery.keepLoaded.* of xp.properties - crossbows stay loaded (Crossbow-Loaded-Spec 3.2) =========
# Read by SkillCfg.load (/skills reload and the kit's reload routine re-read it); appended ONCE to an existing file without
# perk.archery.keepLoaded.enabled (the FellCfg / PartyCfg pattern; the code defaults are the same values). Clamps = the Server Setup rows.
xcf.addField(CtField.make("public static final String DEFAULTS = " + XBOW_LIT + ";", xcf))
for decl in ("boolean ON = true", "int LEVEL = 5", 'String[] ITEMS = new String[] { "Weapon_Crossbow_" }', "int DELAY = 3", "boolean DEBUG = false"):
    xcf.addField(CtField.make("public static volatile " + decl + ";", xcf))
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
}}""", xcf))
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
  return "on (Archers from Archery " + LEVEL + ", bolts back after " + DELAY + " ticks" + (DEBUG ? ", DEBUG chat lines on" : "") + ")";
}""", xcf))

# XbowState (spec 2.3): one per online player, world thread only. n / stk / cre = the kept load per hotbar slot (bolts, the stack seen at
# the switch away, Creative then); enterAt = ticks at the last switch onto the current slot (a fresh state = "long ago": no switch was
# seen while the perk was on, so the held item was not just switched onto); pendSlot / pendAt = the armed restore (-1 = none).
xst.addField(CtField.make("public " + REF + " ref;", xst))
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
  this.epoch = -1L;
  this.ticks = 0L;
  this.n = new int[16];
  this.stk = new {IS}[16];
  this.cre = new boolean[16];
  this.enterAt = -1000000L;
  this.pendSlot = -1;
  this.pendAt = 0L;
}}""", xst))

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
    EXACT = ex; PFX = pf; SFX = sf; ROLE = ro;
    CACHE.clear();
    {PKG}.SmithCfg.CACHE.clear();
    return ex.size() + " exact, " + pf.size() + " prefix, " + sf.size() + " suffix, " + ro.size() + " role rule(s), acrobatics " + ({PKG}.AcroCfg.ENABLED ? "on" : "off") + ", perks " + ({PKG}.PerkCfg.ENABLED ? "on" : "off") + ", alchemy " + ({PKG}.AlchCfg.ENABLED ? "on" : "off") + ", smithing " + ({PKG}.SmithCfg.ENABLED ? ({PKG}.SmithCfg.VANILLA ? "on" : "on (Furnace tab only)") : "off") + ", exploration " + ({PKG}.ExplCfg.ENABLED ? "on (no boosters)" : "off") + ", felled trees " + {PKG}.FellCfg.text() + ", double jump " + {PKG}.AcroCfg.djText() + ", party combat XP " + {PKG}.PartyCfg.text() + ", divinity heal XP " + {PKG}.DivCfg.text() + ", crossbows stay loaded " + {PKG}.XbowCfg.text() + ", bridge skills " + {PKG}.BridgeCfg.GRANT_TEXT + ", max level " + {PKG}.SkillDefs.MAX + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");
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
    pr.sendMessage({MSG}.raw("[Skills] Unknown skill. Use mining, foraging, farming, alchemy, smithing, cooking, acrobatics, exploration, combat (your class skill) or a class skill: archery, swordsmanship, sorcery, fury, divinity, assassination, shaman."));
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
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) if (d[{PKG}.SkillDefs.N + i] < 0L) d[{PKG}.SkillDefs.N + i] = (long) {PKG}.SkillDefs.levelOf(d[i]);
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
  return {PKG}.SkillDefs.levelOf(data(u)[skill]);
}}""", sto))
sto.addMethod(CtNewMethod.make(f"""
public static String levelsOf(java.util.UUID u, long[] d) {{
  int cs = {PKG}.SkillClass.slot(u);
  int[] order = new int[] {{ {PKG}.SkillDefs.MINING, {PKG}.SkillDefs.FORAGING, {PKG}.SkillDefs.FARMING, {PKG}.SkillDefs.ACROBATICS, {PKG}.SkillDefs.ALCHEMY, {PKG}.SkillDefs.SMITHING, {PKG}.SkillDefs.COOKING, {PKG}.SkillDefs.EXPLORATION }};
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < order.length; i++) {{
    if (i > 0) sb.append(',');
    sb.append({PKG}.SkillDefs.LABELS[order[i]]).append(':').append({PKG}.SkillDefs.levelOf(d[order[i]]));
  }}
  for (int j = 0; j < {PKG}.SkillDefs.CLASS_SLOT.length; j++) {{
    int s = {PKG}.SkillDefs.CLASS_SLOT[j];
    if (s != cs && d[s] <= 0L) continue;
    sb.append(',').append({PKG}.SkillDefs.LABELS[s]).append(':').append({PKG}.SkillDefs.levelOf(d[s]));
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
  return new long[] {{ (long) {PKG}.SkillDefs.levelOf(ba[0]), (long) {PKG}.SkillDefs.levelOf(ba[1]), ba[1] }};
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
  return rd(d, {PKG}.SkillDefs.N + skill) < (long) {PKG}.SkillDefs.levelOf(rd(d, skill));
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
  int lv = {PKG}.SkillDefs.levelOf(rd(d, skill));
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

# ================= SkillFn: bridge skill:fn:level =================
fn.addInterface(pool.get("java.util.function.Function"))
fn.addConstructor(CtNewConstructor.make("public SkillFn() { }", fn))
fn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    Object[] a = (Object[]) arg;
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
    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillDefs.LABELS[i]).append(" XP (").append({PKG}.SkillDefs.progress(d[i])).append(")");
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
    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillClass.skillName(u, i)).append(" XP (").append({PKG}.SkillDefs.progress(d[i])).append(")");
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
    if (!next && lv >= {PKG}.XbowCfg.LEVEL) return TEXT;
    if (next && lv + 1 == {PKG}.XbowCfg.LEVEL) return TEXT;
  }} catch (Throwable t) {{ failed("stats line", t); }}
  return null;
}}""", xbw))
# wipe every kept load and the armed restore; a later leave must first be held delayTicks again (the Ammo read may be stale right after)
xbw.addMethod(CtNewMethod.make(f"""
public static void reset({PKG}.XbowState s) {{
  for (int i = 0; i < s.n.length; i++) {{ s.n[i] = 0; s.stk[i] = null; s.cre[i] = false; }}
  s.pendSlot = -1;
  s.pendAt = 0L;
  s.enterAt = s.ticks;
}}""", xbw))
xbw.addMethod(CtNewMethod.make(f"""
public static void drop({PKG}.XbowState s, int slot) {{
  if (slot >= 0 && slot < s.n.length) {{ s.n[slot] = 0; s.stk[slot] = null; s.cre[slot] = false; }}
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
  if (bonus) amount = {PKG}.SkillBonus.boost(u, skill, amount);
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
    long need = {PKG}.SkillDefs.needFor(r[2]);
    if (lvOn) pr.sendMessage({MSG}.raw(need > 0L ? "  next: " + sk + " " + (r[1] + 1L) + " at " + {PKG}.SkillDefs.progress(r[2]) + " XP - /skills" : "  " + sk + " is now MAX level!").color("#c8b070"));
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
  pr.sendMessage({MSG}.raw("[Skills] Your old Combat XP (level " + {PKG}.SkillDefs.levelOf(x) + ") now counts for " + {PKG}.SkillClass.skillName(u, slot) + ". Each class keeps its own combat level.").color("#ffc800"));
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
}}""", perk))
# once per second per player from AcroSys (world thread): first tick of the session or class change -> republish skill:<uuid>,
# legacy combat move, stat modifiers. The first tick (LASTCLS has no entry: new session / plugin start) always republishes:
# SkyyClasses publishes class:<uuid> from its ReadyTask (scheduler thread), possibly AFTER our 5 s publishOnline already put a
# classless skill:<uuid>, and publishOnline never republishes a player it has published (PUBLISHED) -> the Combat entry would stay
# stale until the next level up. Cheap: one bridge put per player per session.
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
    {PKG}.Xbow.refresh(u);
    int[] lv = levels(u);
    {PKG}.Brew.setBonus(u, lv[5]);
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());
    if (m == null) return;
    mod(m, {DST}.getHealth(), "skyyskill_health", total({PKG}.PerkCfg.HP, lv));
    mod(m, {DST}.getStamina(), "skyyskill_stamina", total({PKG}.PerkCfg.STA, lv));
    mod(m, {DST}.getMana(), "skyyskill_mana", total({PKG}.PerkCfg.MANA, lv));
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
  s[15] = (double) System.currentTimeMillis();
  s[16] = (double) amount;
  s[17] = 0.0;
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
    if (s.ref == null) s.ref = ref;
    else if (s.ref != ref) {{ reset(s); s.ref = ref; }}
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
            if (k > 0) {{
              s.n[prev] = k;
              s.stk[prev] = is;
              s.cre[prev] = {PKG}.Acro.creativeMode(st, ref);
              kept = true;
              msg = "kept " + k + " bolts - " + is.getItemId() + ", slot " + (prev + 1);
            }}
          }}
        }}
        if (!kept) {{ s.n[prev] = 0; s.stk[prev] = null; s.cre[prev] = false; }}
      }}
    }}
    s.pendSlot = -1;
    s.enterAt = s.ticks;
    if (neu >= 0 && neu < s.n.length && s.n[neu] > 0) {{
      {IS} ns = neu < cap ? c.getItemStack((short) neu) : null;
      if (act && ns != null && !ns.isEmpty() && s.stk[neu] != null && ns.isEquivalentType(s.stk[neu])) {{
        s.pendSlot = neu;
        s.pendAt = s.ticks;
      }} else {{
        if (msg == null) msg = act ? "load dropped - crossbow left slot " + (neu + 1) : "load dropped - the perk is not active right now";
        s.n[neu] = 0; s.stk[neu] = null; s.cre[neu] = false;
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
    if (s.ref != ref) {{ reset(s); s.ref = ref; return; }}
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
    if (need <= 0) {{ drop(s, slot); dbg(pr, "nothing to put back - " + cur + " bolts already loaded"); return; }}
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
    if (free) {{
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
    drop(s, slot);
    if (pay > 0) esm.setStatValue(ai, (float) (cur + pay));
    if (free) dbg(pr, "put back " + pay + " bolts (creative, free)");
    else if (pay >= need) dbg(pr, "put back " + pay + " bolts, paid " + pay + " Crude Arrows");
    else dbg(pr, "put back " + pay + " of " + need + " bolts - only " + pay + " Crude Arrows");
  }} catch (Throwable t) {{
    s.pendSlot = -1;
    failed("restore", t);
  }}
}}""", xbw))

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
        long amt = {PKG}.SkillBonus.boost(W.u, row, xp);
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
bxp.addMethod(CtNewMethod.make(f"""
public static long offer(java.util.UUID u, int slot, long base, String source, String expect, {CRR} rc, int units, boolean grant) {{
  if (u == null || slot < 0 || slot >= {PKG}.SkillDefs.N || slot == {PKG}.SkillDefs.COMBAT) return -2L;
  if (base <= 0L) return 0L;
  if (base > {PKG}.BridgeCfg.PER_CALL) {{ warnLimited(u, "refused " + base + " XP from " + source + " (over bridge.maxXpPerCall " + {PKG}.BridgeCfg.PER_CALL + ")"); return -2L; }}
  {PR} pr = {UNI}.get().getPlayer(u);
  if (pr == null || !pr.isValid()) return -1L;
  String k = {PKG}.SkillStore.pkey(u);
  if (expect != null && expect.length() > 0 && !expect.equals(k)) return -1L;
  {WLD} w = {UNI}.get().getWorld(pr.getWorldUuid());
  if (w == null) return -1L;
  boolean canBoost = {PKG}.SkillDefs.boostable(slot);
  long amt = canBoost ? {PKG}.SkillCfg.scaled(base) : base;
  if (canBoost && (!grant || {PKG}.SkillBonus.grantBonus(slot))) amt = {PKG}.SkillBonus.boost(u, slot, amt);
  if (amt <= 0L) return 0L;
  if (!allow(u, amt)) {{ warnLimited(u, "bridge.maxXpPerMinute " + {PKG}.BridgeCfg.PER_MIN + " reached - refused " + amt + " XP from " + source); return -1L; }}
  w.execute(new {PKG}.BridgeTask(u, slot, amt, k, source == null ? "?" : source, rc, units));
  return amt;
}}""", bxp))
# ================= HealXp part 2 (0.4.4): skill:fn:healxp -> Divinity XP (research/Classes-Berserker-Priest-Spec.md 3.4) =================
# true = accepted (queued on the player's world thread) or nothing to pay; false = refused (see the header: part off / rate 0, bad hp, not
# a Priest (class skill Divinity = slot 15), class still following a profile switch, heal would cross the cap (all or nothing),
# BridgeXp.offer refused). The cap ring counts the base heal XP; a refused offer gives its share back (a task the world thread drops later
# keeps it for the rest of the window - fails closed, see the header). Any thread, no I/O, never throws.
hxp.addMethod(CtNewMethod.make(f"""
public static boolean offer(java.util.UUID u, double hp, String source, String expect) {{
  try {{
    if (u == null || !{PKG}.DivCfg.on()) return false;
    if (Double.isNaN(hp) || Double.isInfinite(hp) || hp <= 0.0) return false;
    if ({PKG}.SkillClass.slot(u) != {PKG}.SkillDefs.DIVINITY || !{PKG}.SkillClass.consistent(u)) return false;
    long base = amount(hp, {PKG}.DivCfg.PER_HP);
    if (base <= 0L) return true;
    long cap = {PKG}.DivCfg.MAX_MIN;
    if (!take(u, base, cap, System.currentTimeMillis())) {{ warnLimited(u, "divinity.healXpMaxPerMinute " + cap + " reached - refused " + base + " XP from " + source); return false; }}
    long r = -1L;
    try {{ r = {PKG}.BridgeXp.offer(u, {PKG}.SkillDefs.DIVINITY, base, source, expect, null, 0, false); }} catch (Throwable t) {{ r = -1L; }}
    if (r < 0L) {{ if (cap > 0L) give(u, base); return false; }}
    return true;
  }} catch (Throwable t) {{ return false; }}
}}""", hxp))
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
# one member: every rule of the header comment; returns the XP paid (0 = skipped)
pxp.addMethod(CtNewMethod.make(f"""
public static long one(java.util.UUID ku, String kn, {V3D} kpos, {ST} s, String mid, long base, double fr, double r2) {{
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
  long amt = amount(base, fr);
  if (amt <= 0L) return 0L;
  if ({PKG}.PartyCfg.TREE_BONUS) amt = {PKG}.SkillBonus.boost(mu, slot, amt);
  {PKG}.SkillXp.gain4(mp, slot, amt, false, false, kn == null ? "" : kn);
  return amt;
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static void share({PR} kp, {REF} kr, {ST} s, long base) {{
  if (!{PKG}.PartyCfg.on() || base <= 0L || kp == null || kr == null || s == null) return;
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
      one(ku, kn, kpos, s, ms[i], base, fr, r2);
    }} catch (Throwable t) {{
      if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("party combat XP share failed (logged once): " + t); }}
    }}
  }}
}}""", pxp))
# the class how-to line of the Stats page ("" while off or SkyyParty is not loaded)
pxp.addMethod(CtNewMethod.make(f"""
public static String howText() {{
  if (!{PKG}.PartyCfg.on()) return "";
  try {{
    if (!({PKG}.SkillStore.bridge().get("party:fn:members") instanceof java.util.function.Function)) return "";
  }} catch (Throwable t) {{ return ""; }}
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

# Combat: DeathComponent added to an NPC killed by a player
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
    long cx = {PKG}.SkillCfg.combatXp(role, maxHp);
    {PKG}.SkillXp.gain(pr, slot, cx);
    {PKG}.PartyXp.share(pr, k, s, cx);
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
hfn.addInterface(pool.get("java.util.function.Function"))
hfn.addConstructor(CtNewConstructor.make("public SkillHealFn() { }", hfn))
hfn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) arg;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof Number)) return Boolean.FALSE;
    String src = a.length > 2 && a[2] != null ? String.valueOf(a[2]) : "?";
    String expect = a.length > 3 && a[3] instanceof String ? (String) a[3] : null;
    return {PKG}.HealXp.offer((java.util.UUID) a[0], ((Number) a[1]).doubleValue(), src, expect) ? Boolean.TRUE : Boolean.FALSE;
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
BARW = 400
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
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  String bs = "Style: TextButtonStyle(Default: (Background: #27463a, LabelStyle: (FontSize: 12, TextColor: #dcffe8, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #3b6b54, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #172a22, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyySkills {{ Anchor: (Width: 640, Height: 690); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyySkills", "Group {{ Anchor: (Height: 2); Background: #9fe0a0; }}");
  if (this.view < 0 || this.view >= {PKG}.SkillDefs.N) {{
    int cs = {PKG}.SkillClass.slot(u);
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
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 30); Text: \\"Skills\\"; Style: (FontSize: 16, RenderBold: true, TextColor: #e6fff0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 18); Text: \\"" + safe("Skill average " + (avg10 / 10L) + "." + (avg10 % 10L) + " - every level up pays coins") + "\\"; Style: (FontSize: 11, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 6); Text: \\"\\"; }}");
    boolean trees = {PKG}.SkillBonus.treesOn();
    int tw = trees ? 356 : 430;
    int bw = trees ? 330 : {BARW};
    for (int i = 0; i < rows.length; i++) {{
      int sl = rows[i];
      boolean classRow = sl == {PKG}.SkillDefs.COMBAT;
      if (classRow && cs >= 0) sl = cs;
      long total = d[sl];
      int lv = {PKG}.SkillDefs.levelOf(total);
      long cur = {PKG}.SkillDefs.intoLevel(total);
      long need = {PKG}.SkillDefs.needFor(total);
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
      int rh = acroRow ? 72 : 58;
      b.appendInline("#SkyySkills", "Group #SkyySkRow" + i + " {{ Anchor: (Height: " + rh + "); LayoutMode: Left; Padding: (Top: 4); Background: #142030(0.9); }}");
      b.appendInline("#SkyySkRow" + i, "Group {{ Anchor: (Width: 60, Height: 50); ItemIcon {{ Anchor: (Width: 44, Height: 44, Left: 8, Top: 3); ItemId: \\"" + {PKG}.SkillDefs.ICONS[sl] + "\\"; }} }}");
      b.appendInline("#SkyySkRow" + i, "Group #SkyySkTxt" + i + " {{ Anchor: (Width: " + tw + ", Height: " + (rh - 8) + "); LayoutMode: Top; }}");
      b.appendInline("#SkyySkTxt" + i, "Label {{ Anchor: (Height: 20); Text: \\"" + safe(title) + "\\"; Style: (FontSize: 14, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }}");
      b.appendInline("#SkyySkTxt" + i, "Group #SkyySkBar" + i + " {{ Anchor: (Width: " + bw + ", Height: 10); Background: #22324a; }}");
      if (fill > 0) b.appendInline("#SkyySkBar" + i, "Group {{ Anchor: (Left: 0, Top: 0, Width: " + fill + ", Height: 10); Background: " + col + "; }}");
      b.appendInline("#SkyySkTxt" + i, "Label {{ Anchor: (Height: 18); Text: \\"" + safe(prog) + "\\"; Style: (FontSize: 11, TextColor: #b8c8d8, VerticalAlignment: Center); }}");
      if (acroRow) {{
        b.appendInline("#SkyySkTxt" + i, "Label #SkyySkBonus {{ Anchor: (Height: 14); Text: \\"\\"; Style: (FontSize: 10, RenderBold: true, TextColor: #d8c0ff, VerticalAlignment: Center); }}");
        b.set("#SkyySkBonus.Text", {PKG}.Acro.bonusText(lv));
      }}
      if (trees) {{
        if ({PKG}.SkillBonus.treeAvailable(sl)) {{
          b.appendInline("#SkyySkRow" + i, "TextButton #SkyySkTree" + i + " {{ Anchor: (Width: 70, Height: 28); Text: \\"Tree\\"; " + bs + " }}");
          ev.addEventBinding({BT}.Activating, "#SkyySkTree" + i, {EVD}.of("a", "sktree" + sl));
        }} else {{
          b.appendInline("#SkyySkRow" + i, "Label {{ Anchor: (Width: 70, Height: 28); Text: \\"\\"; }}");
        }}
        b.appendInline("#SkyySkRow" + i, "Label {{ Anchor: (Width: 4, Height: 28); Text: \\"\\"; }}");
      }}
      b.appendInline("#SkyySkRow" + i, "TextButton #SkyySkStat" + i + " {{ Anchor: (Width: 100, Height: 28); Text: \\"Stats\\"; " + bs + " }}");
      ev.addEventBinding({BT}.Activating, "#SkyySkStat" + i, {EVD}.of("a", "skstat" + sl));
      b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 4); Text: \\"\\"; }}");
    }}
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 18); Text: \\"Gather - brew - smelt - cook - class weapons - run jump fall dodge - explore.  Stats shows every boost\\"; Style: (FontSize: 10, TextColor: #7f94a8, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    return;
  }}
  int s = this.view;
  java.util.ArrayList rows = {PKG}.SkillTop.all(s);
  b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 30); Text: \\"" + safe("Top 10 - " + {PKG}.SkillDefs.LABELS[s]) + "\\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + {PKG}.SkillDefs.COLORS[s] + ", HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 8); Text: \\"\\"; }}");
  int n = rows.size() < 10 ? rows.size() : 10;
  if (n == 0) b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 24); Text: \\"Nobody has any XP yet.\\"; Style: (FontSize: 12, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  for (int i = 0; i < n; i++) {{
    Object[] e = (Object[]) rows.get(i);
    long x = ((Long) e[1]).longValue();
    boolean me = {PKG}.SkillStore.pkey(u).equals(e[2]);
    String line = (i + 1) + ".   " + e[0] + "     Level " + {PKG}.SkillDefs.levelOf(x) + "     " + {PKG}.SkillDefs.fmt(x) + " XP";
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 26); Text: \\"" + safe(line) + "\\"; Style: (FontSize: 13, " + (me ? "RenderBold: true, TextColor: #ffe08a" : "TextColor: #e6f0ff") + ", VerticalAlignment: Center); }}");
  }}
  int rank = {PKG}.SkillTop.rankOf(rows, u);
  b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 8); Text: \\"\\"; }}");
  b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 20); Text: \\"" + safe(rank > 0 ? "Your rank #" + rank + " of " + rows.size() + " - level " + {PKG}.SkillDefs.levelOf(d[s]) + " - " + {PKG}.SkillDefs.fmt(d[s]) + " XP" : "You are not ranked yet") + "\\"; Style: (FontSize: 12, TextColor: #c9dff0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySkills", "Group #SkyySkNav {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 8); }}");
  b.appendInline("#SkyySkNav", "Label {{ Anchor: (Width: 250, Height: 30); Text: \\"\\"; }}");
  b.appendInline("#SkyySkNav", "TextButton #SkyySkBack {{ Anchor: (Width: 106, Height: 30); Text: \\"Back\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyySkBack", {EVD}.of("a", "skback"));
}}""", page))
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
  StringBuilder sb = new StringBuilder("Skill tree: ");
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
  if (s == {PKG}.SkillDefs.ALCHEMY && {PKG}.AlchCfg.ENABLED) {{
    double ex = {PKG}.Brew.extraChance(b) - (next ? {PKG}.Brew.extraChance(lv) : 0.0);
    if (ex > 0.00001) out.add((next ? "+" : "") + pc(ex) + " chance to brew an extra potion");
  }}
  if (row <= {PKG}.SkillDefs.FARMING) {{
    String[] what = new String[] {{ "mined blocks", "chopped logs", "harvested crops" }};
    double c = {PKG}.Perks.chance(row, b) - (next ? {PKG}.Perks.chance(row, lv) : 0.0);
    if (c > 0.00001) out.add((next ? "+" : "") + pc(c) + " chance to double the drops of " + what[row]);
  }}
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
  if (s == {PKG}.SkillDefs.FARMING) return "Earn XP by harvesting fully grown crops - break them or press F on eternal crops and bushes";
  if (s == {PKG}.SkillDefs.ACROBATICS) return "Earn XP by running - jumping - dodging - and surviving falls that hurt (higher falls pay more - safe drops and water pay 0)";
  if (s == {PKG}.SkillDefs.ALCHEMY) return "Earn XP by brewing at the Alchemy Bench - stronger potions and higher bench tiers pay more (Greater potions pay the most)";
  if (s == {PKG}.SkillDefs.SMITHING) return "Earn XP by smelting - take the bars out of a Furnace yourself or use the Furnace tab of /craft (reforging and powders later)";
  if (s == {PKG}.SkillDefs.COOKING) return "Cook at a Cooking Bench - food you cook gets stronger with your level";
  if (s == {PKG}.SkillDefs.EXPLORATION) return "Earn XP by exploring - open loot chests for the first time - walk into new chunks (not while flying) - discover Hytale's zones. Once each per profile. XP boosters never apply";
  if (s == {PKG}.SkillDefs.COMBAT) return "Your combat skill is your class skill - Archer Archery / Warrior Swordsmanship / Mage Sorcery / Berserker Fury / Priest Divinity (Assassin and Shaman later)";
  if (!{PKG}.SkillDefs.isClass(s)) return "";
  String c = {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)];
  String w = {PKG}.SkillClass.weaponsText(c);
  return "Earn XP by defeating monsters with " + c + " weapons" + (w == null ? "" : " - " + w) + {PKG}.PartyXp.howText();
}}""", spg))
spg.addMethod(CtNewMethod.make(f"""
public static void line({UCB} b, String id, String text, String color, int size, boolean bold, int h) {{
  b.appendInline("#SkyySkStats", "Label #" + id + " {{ Anchor: (Height: " + h + "); Text: \\"\\"; Style: (FontSize: " + size + ", " + (bold ? "RenderBold: true, " : "") + "TextColor: " + color + ", VerticalAlignment: Center); }}");
  b.set("#" + id + ".Text", text);
}}""", spg))
# 0.4.1: the same line with Wrap: true (the Exploration how-to text is longer than one line)
spg.addMethod(CtNewMethod.make(f"""
public static void wrapLine({UCB} b, String id, String text, String color, int size, int h) {{
  b.appendInline("#SkyySkStats", "Label #" + id + " {{ Anchor: (Height: " + h + "); Text: \\"\\"; Style: (FontSize: " + size + ", TextColor: " + color + ", VerticalAlignment: Center, Wrap: true); }}");
  b.set("#" + id + ".Text", text);
}}""", spg))
spg.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  int s = this.slot;
  if (s < 0 || s >= {PKG}.SkillDefs.N) s = 0;
  int cs = {PKG}.SkillClass.slot(u);
  if (s == {PKG}.SkillDefs.COMBAT && cs >= 0) s = cs;
  long total = d[s];
  int lv = {PKG}.SkillDefs.levelOf(total);
  long cur = {PKG}.SkillDefs.intoLevel(total);
  long need = {PKG}.SkillDefs.needFor(total);
  int fill = need > 0L ? (int) ({STBARW}L * cur / need) : {STBARW};
  if (fill < 0) fill = 0;
  if (fill > {STBARW}) fill = {STBARW};
  boolean legacy = s == {PKG}.SkillDefs.COMBAT;
  if (legacy) fill = 0;
  String col = {PKG}.SkillDefs.COLORS[s];
  String name = legacy ? "Combat" : {PKG}.SkillClass.skillName(u, s);
  String bs = "Style: TextButtonStyle(Default: (Background: #27463a, LabelStyle: (FontSize: 18, TextColor: #dcffe8, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #3b6b54, LabelStyle: (FontSize: 18, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #172a22, LabelStyle: (FontSize: 18, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyySkStats {{ Anchor: (Width: 960, Height: 795); Background: #0b1524(0.96); Padding: (Horizontal: 24, Vertical: 15); LayoutMode: Top; }}");
  b.appendInline("#SkyySkStats", "Group {{ Anchor: (Height: 3); Background: #9fe0a0; }}");
  b.appendInline("#SkyySkStats", "Label #SkyyStTitle {{ Anchor: (Height: 45); Text: \\"\\"; Style: (FontSize: 24, RenderBold: true, TextColor: " + col + ", HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.set("#SkyyStTitle.Text", legacy ? "Combat - no class" : name + " - level " + lv + " of " + {PKG}.SkillDefs.MAX);
  b.appendInline("#SkyySkStats", "Label #SkyyStSub {{ Anchor: (Height: 27); Text: \\"\\"; Style: (FontSize: 17, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  String sub;
  if (legacy) sub = "Choose a class with /class - each class has its own combat skill";
  else if (need > 0L) sub = {PKG}.SkillDefs.fmt(cur) + " / " + {PKG}.SkillDefs.fmt(need) + " XP to level " + (lv + 1) + "  (" + {PKG}.SkillDefs.fmt(need - cur) + " to go)";
  else sub = "MAX LEVEL - " + {PKG}.SkillDefs.fmt(total) + " XP";
  b.set("#SkyyStSub.Text", sub);
  b.appendInline("#SkyySkStats", "Group #SkyyStBarRow {{ Anchor: (Height: 24); LayoutMode: Left; Padding: (Top: 3); }}");
  b.appendInline("#SkyyStBarRow", "Label {{ Anchor: (Width: 156, Height: 18); Text: \\"\\"; }}");
  b.appendInline("#SkyyStBarRow", "Group #SkyyStBar {{ Anchor: (Width: {STBARW}, Height: 18); Background: #22324a; }}");
  if (fill > 0) b.appendInline("#SkyyStBar", "Group {{ Anchor: (Left: 0, Top: 0, Width: " + fill + ", Height: 18); Background: " + col + "; }}");
  if ({PKG}.SkillDefs.isClass(s) && s != cs) {{
    String cn = {PKG}.SkillDefs.CLASSES[{PKG}.SkillDefs.classIdx(s)];
    String art = (cn.startsWith("A") || cn.startsWith("E") || cn.startsWith("I") || cn.startsWith("O") || cn.startsWith("U")) ? "an " : "a ";
    line(b, "SkyyStNote", "You are not " + art + cn + " right now - these boosts work while you are one", "#ffb080", 17, true, 30);
  }} else {{
    b.appendInline("#SkyySkStats", "Label {{ Anchor: (Height: 12); Text: \\"\\"; }}");
  }}
  line(b, "SkyyStNowHd", legacy ? "Your combat" : "Boosts right now (level " + lv + ")", "#e6fff0", 20, true, 36);
  java.util.ArrayList now = lines(u, s, lv, false);
  for (int i = 0; i < now.size() && i < 7; i++) line(b, "SkyyStNow" + i, "   " + (String) now.get(i), "#dfe8f0", 18, false, 28);
  b.appendInline("#SkyySkStats", "Label {{ Anchor: (Height: 12); Text: \\"\\"; }}");
  if (!legacy) {{
    if (need > 0L) {{
      line(b, "SkyyStNextHd", "Level " + (lv + 1) + " adds", "#e6fff0", 20, true, 36);
      java.util.ArrayList nx = lines(u, s, lv, true);
      for (int i = 0; i < nx.size() && i < 7; i++) line(b, "SkyyStNext" + i, "   " + (String) nx.get(i), "#bfe8c8", 18, false, 28);
    }} else {{
      line(b, "SkyyStNextHd", "Max level reached - nothing more to unlock", "#ffe08a", 20, true, 36);
    }}
    b.appendInline("#SkyySkStats", "Label {{ Anchor: (Height: 12); Text: \\"\\"; }}");
  }}
  wrapLine(b, "SkyyStHow", how(s), "#8fa6ba", 15, 45);
  b.appendInline("#SkyySkStats", "Group #SkyyStNav {{ Anchor: (Height: 60); LayoutMode: Left; Padding: (Top: 12); }}");
  String tree = {PKG}.SkillBonus.treeAvailable(s) ? {PKG}.SkillBonus.treeName(s) : null;
  b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: " + (tree != null ? 133 : 246) + ", Height: 45); Text: \\"\\"; }}");
  b.appendInline("#SkyyStNav", "TextButton #SkyyStBack {{ Anchor: (Width: 195, Height: 45); Text: \\"< Back\\"; " + bs + " }}");
  b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: 30, Height: 45); Text: \\"\\"; }}");
  b.appendInline("#SkyyStNav", "TextButton #SkyyStTop {{ Anchor: (Width: 195, Height: 45); Text: \\"Top 10\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyStBack", {EVD}.of("a", "stback"));
  ev.addEventBinding({BT}.Activating, "#SkyyStTop", {EVD}.of("a", "sttop"));
  if (tree != null) {{
    b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: 30, Height: 45); Text: \\"\\"; }}");
    b.appendInline("#SkyyStNav", "TextButton #SkyyStTree {{ Anchor: (Width: 195, Height: 45); Text: \\"Skill tree\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyStTree", {EVD}.of("a", "sttree"));
  }}
}}""", spg))
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
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
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
            ("acrobatics", "Acrobatics"), ("perks", "Perks"), ("crafting", "Crafting")]
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
    ("divinity.healXp.enabled", "Divinity XP from healing", "parts", "bool", "true", "", "", "", "", _LP,
     "Off: Priest heals pay no Divinity XP (kills still do). Levels are kept.", "reload"),
    # ---- general
    ("multiplier", "XP multiplier", "general", "dec", "1.0", "0", "100", "", "x", "live,danger",
     "Gathering, Acrobatics, Alchemy and Smithing XP times this (not XP from other mods, not Exploration).", "reload"),
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
     "Share of the killer's class XP each nearby party member gets (0.5 = half). The killer keeps all.", "reload"),
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
    ("levels", "XP per level (list)", "levels", "text", LEVELS_TEXT, "1", "2000", "", "", "live,danger,adv",
     "XP each level needs, level 1 first; the count is the max level (1-100). Easier: the two rows below.",
     "reload;check=SkillKit.checkLevels"),
    ("levels.scale", "Level curve size", "levels", "int", "100", "10", "1000", "step=5", "%", "live,danger",
     "XP every level needs as % of the default curve (110 = 10% more). Rewrites the XP per level list.", "custom:SkillKit"),
    ("levels.max", "Max level", "levels", "int", "100", "1", "100", "step=5", "", "live,danger",
     "Cuts or extends the list (new levels follow the default curve, cut ones come back until a restart).", "custom:SkillKit"),
    # ---- gathering: the XP rules (key families) + felled trees
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
    ("combat.perHealth", "Combat XP per max health", "combat", "dec", "0.2", "0", "1000", "", "", "live",
     "Class XP per NPC kill = its max health x this, kept between the minimum and maximum below.", "reload"),
    ("combat.min", "Combat XP minimum", "combat", "int", "1", "0", "1000000000", "", "", "live",
     "Least class XP one kill pays. Keep it at or below the maximum, or every kill pays the maximum.", "reload"),
    ("combat.max", "Combat XP maximum", "combat", "int", "500", "0", "1000000000", "", "", "live",
     "Most class XP one kill pays (an NPC role's own XP beats it). Under the minimum, every kill pays it.", "reload"),
    ("combat.default", "Combat XP if health unknown", "combat", "int", "5", "0", "1000000000", "", "", "live",
     "Used when the NPC's max health cannot be read.", "reload"),
    ("combat.role", "Combat XP by NPC role", "combat", "table", "", "0", "1000000000", "int;type;XP", "", "live",
     "Exact XP for one NPC role. The server log names each new role on its first kill.", "reload"),
    ("combat.classWeaponOnly", "Only class weapons earn XP", "combat", "bool", "true", "", "", "", "", "live",
     "On: only the class's own weapons earn combat XP. Off: anything SkyyClasses lets the class use.", "reload"),
    # 0.4.4 Divinity XP from Priest heals (skill:fn:healxp, SkyyClasses 0.1.6); kills pay Fury / Divinity through the rows above
    ("divinity.healXpPerHp", "Divinity XP per HP healed", "combat", "dec", "0.2", "0", "100", "", "", "live",
     "XP per 1 HP a Priest heals on OTHER party members (healing themself pays nothing).", "reload"),
    ("divinity.healXpMaxPerMinute", "Divinity heal XP per minute", "combat", "int", "300", "0", "1000000000", "", "", "live",
     "Most Divinity XP healing pays one Priest in 60 s (0 = no limit). Kills are not counted.", "reload"),
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
     "live", "LOCKED 2026-09-25: jump again while already in mid-air. Crouch remains a choice. Jump only works if the client reports it (spec test 5.0).", "reload"),
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
for _tk, _pfx in (("block", "block."), ("prefix", "prefix."), ("suffix", "suffix."), ("alchemy.xp", "alchemy.xp."), ("smithing.xp", "smithing.xp.")):
    assert any(_k.startswith(_pfx) for _k in _dp), "table %s has no default entries" % _tk
print("config rows: %d (%d tables), %d not in the default file (zero perk stats, adv)" % (len(CFG_ROWS), sum(1 for _r in CFG_ROWS if _r[3] == "table"), len(_absent)))
assert len(CFG_ROWS) == 159, "0.4.4 had 154 rows + 5 crossbows-stay-loaded rows (Crossbow-Loaded-Spec 3.9), got %d" % len(CFG_ROWS)   # 0.4.5
for _k in ("perk.archery.keepLoaded.enabled", "perk.archery.keepLoaded.level", "perk.archery.keepLoaded.items",
           "perk.archery.keepLoaded.delayTicks", "perk.archery.keepLoaded.debug"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp and ("\n" + _k + "=") in ("\n" + XBOW_DEFAULTS), _k
for _k in ("divinity.healXp.enabled", "divinity.healXpPerHp", "divinity.healXpMaxPerMinute"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp, _k
kit = CFG.emit(pool, PKG, MOD="SkyySkills", TITLE="Skills", VERSION=VERSION, NODE="skyyskills.admin", CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=["Skyy_SkyySkills/xp.properties"], RELOAD="SkillKit.reload", KEEP=20, DEFAULTS={"xp.properties": DEFAULTS},
               NOTE="Hand edits of xp.properties: /skills reload. Levels tab: curve size % and max level.")

# ================= SkillKit (0.4.3): reload routine, check= hooks, the custom: level-curve rows (spec 5.7) =================
# The kit calls these by reflection with no kit lock held (tools/CONFIG-CONTRACT.md guarantee 6); SkillKit takes no lock of its own
# except SkillDefs.setTable's (SkillCfg.load takes SkillCfg then SkillDefs, never the other way round) and its class lock around TAIL
# (tailFor / keepTail call nothing else, so no lock is ever taken inside it).
skit.addMethod(CtNewMethod.make(f"""
public static String reload() {{
  String r = {PKG}.SkillCfg.load();
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
skit.addMethod(CtNewMethod.make("""
public static String customGet(String key) {
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
  }} else {{
    return new Object[] {{ "unknown", null, "Unknown setting: " + key + "." }};
  }}
  {PKG}.SkillDefs.setTable(nl);
  armReload();
  armLater();
  String val = "levels.max".equals(key) ? String.valueOf(nl.length) : String.valueOf(pctOf(nl));
  return new Object[] {{ "ok", val, msg, new String[] {{ "levels", join(nl) }} }};
}}""", skit))
# History restore: the two curve rows follow the restored copy's levels= line (the levels row itself is restored first, row order)
skit.addMethod(CtNewMethod.make(f"""
public static String customRead(String key, java.util.Map vals) {{
  long[] l = null;
  try {{
    Object o = vals == null ? null : vals.get("levels");
    if (o instanceof String) l = parseList((String) o);
  }} catch (Throwable t) {{ l = null; }}
  if (l == null) l = {PKG}.SkillDefs.DEFAULT_PER;
  if ("levels.max".equals(key)) return String.valueOf(l.length);
  if ("levels.scale".equals(key)) return String.valueOf(pctOf(l));
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
      pr.sendMessage({MSG}.raw("  " + (i + 1) + ". " + e[0] + " - level " + {PKG}.SkillDefs.levelOf(x) + " (" + {PKG}.SkillDefs.fmt(x) + " XP)"));
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
  {PKG}.Acro.djPublish();
  pr.sendMessage({MSG}.raw("[Skills] xp.properties reloaded: " + res + kr));
}}""", rcmd))

# /skills stats <skill> (0.3): a subcommand with a required arg (optional args are not positional - HANDOFF command rules)
scmd.addField(CtField.make(f"public {RA} skillArg;", scmd))
scmd.addConstructor(CtNewConstructor.make(f"""
public StatsCmd() {{
  super("stats", "Open the Stats page of a skill: /skills stats mining");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | sorcery | fury | divinity | assassination | shaman", {ATY}.STRING);
  setPermissionGroups(new String[] {{ "hytale:Adventurer" }});
}}""", scmd))
scmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    int s = {PKG}.SkillClass.argSlot(pr, String.valueOf(ctx.get(this.skillArg)));
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
cmd.addConstructor(CtNewConstructor.make(f"""
public SkillsCmd() {{
  super("skills", "Open your skills page; /skills stats <skill>, /skills top <skill>, /skills quiet");
  addAliases(new String[] {{ "skill" }});
  setPermissionGroups(new String[] {{ "hytale:Adventurer" }});
  addSubCommand(new {PKG}.StatsCmd());
  addSubCommand(new {PKG}.TopCmd());
  addSubCommand(new {PKG}.QuietCmd());
  addSubCommand(new {PKG}.ReloadCmd());
  addSubCommand(new {PKG}.XpCmd());
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
  String rules = {PKG}.SkillCfg.load();
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
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SkillTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyySkills] {VERSION} ready - /skills; rows Alchemy (Alchemy Bench) / Smithing (Furnace) / Cooking (via SkyyCooking) / Exploration (via SkyyExploration, no boosters); felled trees " + {PKG}.FellCfg.text() + "; double jump " + {PKG}.AcroCfg.djText() + " (bridge skill:dj:key); party combat XP " + {PKG}.PartyCfg.text() + "; divinity heal XP " + {PKG}.DivCfg.text() + "; crossbows stay loaded at Archery " + {PKG}.XbowCfg.LEVEL + " (" + ({PKG}.XbowCfg.ON ? "on" : "off") + ")" + "; bridge skill:fn:addxp + skill:fn:craftxp + skill:fn:healxp; trees bridge on (tree bonuses " + ({PKG}.BridgeCfg.BONUS ? "XP for " + {PKG}.BridgeCfg.BONUS_TEXT + " (grants from other mods: " + ({PKG}.BridgeCfg.BONUS_ADDXP_TEXT.length() > 0 ? {PKG}.BridgeCfg.BONUS_ADDXP_TEXT : "none") + ") + double drops" : "off") + ", SkyyTrees " + ({PKG}.SkillBonus.treesOn() ? "found" : "not loaded yet") + "); xp rules: " + rules + "; combat = class skill (SkyyClasses " + ({PKG}.SkillClass.allowedFn() != null ? "found" : "not loaded yet - no combat XP without it") + ")" + (fallOwner ? "" : "; fall damage bonuses are applied by " + {PKG}.MoveSync.bridge().get({PKG}.MoveSync.OWNER_FALL)));
  {PKG}.SkillStore.regSetting("skills.xpGain", "Skill XP gains", "skills", true, "+12 Mining XP (340/500) while you gather, fight, smelt, brew and move");
  {PKG}.SkillStore.regSetting("skills.levelUp", "Skill level-ups", "skills", true, "SKILL LEVEL UP with the coins it paid and the XP for the next level");
  {PKG}.SkillStore.regSetting("skills.doubleDrop", "Double drops", "skills", true, "Double drop x3! from the Mining, Foraging and Farming perks");
  {PKG}.SkillStore.regSetting("skills.extraPotion", "Extra potions", "skills", true, "Extra potion! from the Alchemy perk");
  {PKG}.SkillStore.regSetting("skills.combatHints", "No combat XP hints", "skills", true, "Why a kill gave no combat XP - once per reason each session");
  {PKG}.SkillStore.regSetting("rewards.late", "Late reward payouts", "coins", true, "Coins and XP paid later because another mod was not ready");
  {PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{
  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ if (!{PKG}.SkillStore.DIRTY.isEmpty()) {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.PlacedStore.flush(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:level"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:addxp"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:craftxp"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:xp"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:drops"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:placed"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:felledBy"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:healxp"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:dj:key"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.Fell.endAll(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.MoveSync.releaseFall({PKG}.Acro.MOD); }} catch (Throwable t) {{ }}
  super.shutdown();
}}""", pl))

for c in (defs, cfg, sto, pub, fn, msg, fl, xp, plc, hg, btk, ptk, htk, bsy, psy, usy, ksy, tcm, top, page, tcmd, qcmd, rcmd, cmd, tick, pl, acfg, mvs_, acro, asy, afs,
          pcfg, scls, perk, cds, spg, scmd, alc, smc, bgc, rxp, brew, bxp, ctk, stk, btsk, csy, sxu, ssy, afss, afn, cfn, xcmd, sbn, xfn, dfn, pfn, exc,
          fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft, skit, karm, dvc, hxp, hfn, xcf, xst, xbw, xss):
    c.writeFile(OUT)
kit.write(OUT)   # 0.4.3: the kit's deferred checks (SkillKit hooks) + its 7 classes
print("classes written")

jar = os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)
m = B.manifest("SkyySkills", VERSION, "SkyWynn skills (Hypixel SkyBlock style): Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class combat skill (SkyyClasses: Archery, Swordsmanship, Sorcery, Fury, Divinity) to level 100. XP from breaking blocks (a felled tree pays every log that falls), ripe crops, brewing at the Alchemy Bench, smelting at a Furnace, cooking (SkyyCooking), exploring (SkyyExploration - never boosted), kills with class weapons (nearby SkyyParty members get a share in their own class skill), Priest heals on party members (Divinity, from SkyyClasses) and running / jumping / big survived falls / dodging (+ the Acrobatics tree Double Jump: jump again in mid-air). Alchemy makes potion effects last longer and adds max Mana; Exploration adds max Stamina; crossbows stay loaded from Archery 5 by default (the level is set in Server Setup; Archers keep their bolts across hotbar switches, paid with the arrows vanilla refunds). Perks: max health / stamina, double drops, class weapon damage; Acrobatics raises speed, jump height and dodge push and lowers fall damage (shared Skyy movement protocol). Stats page per skill. Every setting editable in game (SkyWynn Menu Server Setup, optional) and per-player chat switches (/settings, optional). Skill tree bonuses and Tree buttons with SkyyTrees (optional). Level ups pay SkyyCoins. /skills. Per profile with SkyyProfiles (optional). Zero dependencies.", PKG + ".SkyySkillsPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT, {})  # no assets: page built inline (see memory hytale-ui-rules)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyySkills.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyySkills" % VERSION, disable_prefix="Skyy:")
