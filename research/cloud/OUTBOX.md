# OUTBOX - cloud session -> local session

The local session's `cloud-link` mod polls this file on `origin/main` every 3 minutes and wakes the local session with every NEW block.
Cloud sessions: to answer the local session (a question, "done", a blocker), APPEND one block and push to main:

```
## <YYYY-MM-DD HH:MM> <short title>
<what you did / found / need, plain text, a few lines; name files by path>
```

Never edit or delete older blocks (their titles are how the mod knows what is new). Keep each block short; details go in the files.

## 2026-10-08 03:50 OUTBOX test
Cloud session got the new two-way channel message and will report done / blocked here from now on.

## 2026-10-08 03:58 Cloud list started
Working the CLOUD-RESUME list now: ability refresh, engine spec, Monk probe plan, class review prep, consistency pass + questions digest, and the 3 art tasks, all running in parallel. Class-Tree-Paths.md and Class-Tree-Build-Map.md are not touched. One OUTBOX block per finished task.

## 2026-10-08 04:04 Class review prep
Done: research/cloud/Class-Review-Prep-1008.md - Archer, Warrior, Mage, Assassin (Mage + Assassin were only partly reviewed 2026-10-07), abilities + modifiers, Echo candidates, gaps, 3 yes/no suggestions each.
Top questions: Meteor / God Killer Echo = 5th modifier or replace one [replace one]; drop the 'no Echo on stances' rule (Still Water) [yes]; A1-alt picks Hunter's Net / Bulwark Stance / Starfall / Vanishing Act [all four].
Stale for local: research/classes/Assassin.md:23 still says Pounce (now Shadow Step).

## 2026-10-08 04:04 Consistency pass 2026-10-07
Done: research/cloud/Consistency-Pass-1007.md. Fixed stale cloud lines: Zone 4-5 ore prices marked 'proposed 4,300 / 9,300 / 23,000', kunai void rule dropped (floorCheck 12 -> 0, no void protection), Monk colour Q closed (Saffron), Sushi seaweed, Sanctuary locked numbers in the old draft.
Open: does 'no void protection' also cover the dragon catching you over void (research/cloud/Dragon-Quest-Spec.md:82) and the Knockback+ void check (research/cloud/Modifier-Pool-Spec.md:35)?

## 2026-10-08 04:04 Questions digest 2026-10-07
Done: research/cloud/Questions-Digest-1007.md - 40 open questions not in the 1006 digest, top 10 = build blockers (Mana for physical classes, ability cap 15 / 14 points, tree size, Shadow Step +10%, Block +4.5%, Ember 4,300, Amberite 9,300 / Drakonite 23,000, Bazaar buy floor 0.9, ore regrow, fishing grade). Skyy can answer by row numbers.

## 2026-10-08 04:05 Enchanted v2 (rest)
Done: research/cloud/enchanted-art/enchanted-sheet-v2.png now 43 icons (+14: Onyxium / Silver / Gold ingots, Sand, Clay, Sandstone / Slate / Basalt cobble, Birch / Ash / Azure / Crystal logs, Fibre, Hay Bundle). 13 v1 icons left out on purpose (metal + wood blocks, Pumpkin Block) - README section 7.1.
Questions: Enchanted forms for Sand / Clay / stone cobbles [no, only Cobblestone + Rubble]; Hay Bundle as a 2nd Wheat step [not at launch]. All 14 base ids UNVERIFIED.

## 2026-10-08 04:06 Class emblems v2 (other 5)
Done: research/cloud/class-art/class-sheet.png - Warrior (sword + spear), Berserker (battleaxe + mace), Archer (recurve bow + arrow), Assassin (kunai + dagger), Mage (crystal staff + spellbook) at the Monk / Priest v2 detail; Monk + Priest bytes unchanged.
Questions: Archer bow only [yes]; locked = grey emblem [yes]; Mage crystal violet [yes]. Weak spots: Berserker axe busy at 64 px, kunai hides the dagger grip.

## 2026-10-08 04:08 Fishing UI mockup v2
Done: research/cloud/Fishing-UI-Mockup.png (v1 kept as research/cloud/Fishing-UI-Mockup-v1.png), generator research/cloud/fishing-ui/make_fishing_ui_v2.py, notes in research/cloud/Fishing-UI-Mockup.md v2 section. Shows the fight screen, minigame HUD bar (5 states), catch cards, Bench Rig tab and a new Pond Fish collection page; colours / sizes from tools/skyyui.py.
Questions: pack rarity ladder for fish [yes]; catch card 3 s + one chat line [yes]; species grid on the collection page now [yes].

## 2026-10-08 04:10 Class ability spec refresh
Done: research/cloud/Class-Ability-Spec-Draft.md + research/cloud/Modifier-Pool-Spec.md now follow every classes.md 2026-10-07 line (L111-L148); change list research/cloud/Ability-Refresh-1007.md. Floor = 18th modifier, Echo on 11 abilities, Follow on Mana Barrier, stunlock breakout section 2.8.
Budget fix PROPOSED: Echo 20-30% (was 30-70%) or Meteor / Palm Strike / Whirlwind break the caps. Questions: Echo 30% at L5 [yes]; Banner cooldown from the fall [yes]; Blood Frenzy per-swing cost [yes].
Local: research/classes/README.md pool needs --sync-pool (no Floor, 'offers 4'); research/cloud/Class-Tree-Paths.md stale nodes listed in the refresh file (E5, B3, LB2, W1, W2, no Mana Barrier Follow node).

## 2026-10-08 04:11 Class ability ENGINE spec
Done: research/cloud/Class-Ability-Engine-Spec.md - cast pipeline, 9 ability kinds, cooldowns in memory, Mana / Stamina rules, modifiers + Echo as data, zones / toggles / passives / chains, Server Setup rows, HUD (vanilla ability HUD or SkyyHud widget), 8-step build plan (E0 probe mod first). SkyyClasses 0.1.13 has no ability code yet; hooks cited by line.
Questions: 0.7 rune keys as main cast input + /cast backup [yes]; block vanilla runes for class players [yes]; Guardian Spirit cooldown shared across Priests [yes]. 15 engine probes (P1-P15) for the local session.

## 2026-10-08 04:18 Monk moves probe plan
Done: research/cloud/Monk-Probe-Plan.md - 13 probes as /mprobe commands (what each measures, pass / fail, fallback), 12-step in-game test script for Skyy. Draft probe jar SkyyMonkProbe/build_skyymonkprobe_0.1.py + test script come in a [cloud] pull request (UNTESTED, never pin before your build + review).
New APIs: holding / dragging mobs in mid-air (probes 7-8), slow effect id, self-sourced fall damage, melee damage cause. Findings: vault '7 blocks in 0.8 s' lands ~1.06 s; SkyySkills RollSys can pay roll XP on a Plunge landing (breaks 'no Acrobatics XP').
Questions: crouch as the free air jump [yes]; short slow if mobs can't hang [yes]; keep only -15% fall damage if slow-fall stutters [yes].

## 2026-10-08 04:19 Cloud list done
All 10 tasks from tonight's CLOUD-RESUME are done and pushed (one OUTBOX block each above). Draft probe jar: https://github.com/SkyyPlayz/SkyyWynnBlock/pull/11 - UNTESTED, left open for you to build + review before merging.
Refilled CLOUD-RESUME with 3: Ability engine probe plan (E0), Echo options page, Class tree stale nodes (waits until you say research/cloud/Class-Tree-Paths.md is free).

## 2026-10-08 04:25 PR 11 review round
Copilot reviewed https://github.com/SkyyPlayz/SkyyWynnBlock/pull/11: 2 fixes pushed (a64674e: plain rise speed used apex time and flew 2x; manifest IncludesAssetPack false + harness check). Left open on purpose: 'enemy() hits any NPC with stats (merchants, pets)' - same filter as live SkyyArmory 0.1.7 ArmoryTrav.kind; if the probes catch merchants/pets, fix it in a shared filter for Armory + Monk. Your call.

## 2026-10-08 06:35 Class tree stale nodes started
Got it - starting the Class tree stale nodes fix against live SkyyTrees 0.3.3 / SkyyArmory 0.1.9 (node ids kept; shipped text changes listed for your next SkyyTrees build). Echo options page running in parallel. Thanks for taking PR 11.

## 2026-10-08 06:38 Echo options for Skyy
Done: research/cloud/Echo-Options.md (one page). A = Echo 20-30% for all (every budget passes) [default]; B = per-ability caps (4 damage abilities 20-30%, heals / God Killer keep 30-70%); C = keep 30-70% but Echo costs more Mana / cooldown (Meteor 30 -> 37.4 Mana, Whirlwind 14 -> 16.9 s). Starfall breaks like Meteor; Hundred Fists breaks the Monk pair rule at 70%. Numbers use the draft model, UNVERIFIED vs real SkyyGear damage.

## 2026-10-08 06:41 Class tree stale nodes
Done: research/cloud/Class-Tree-Stale-Fix-1008.md + edits in research/cloud/Class-Tree-Paths.md and research/cloud/Class-Tree-Build-Map.md (new section 9 = text changes for the next SkyyTrees build; ids kept, no migration). W1 War Horn + B3 Crimson Frenzy already match live 0.3.3. Proposed: Mage PA3 Phase Step = Mana Barrier Follow upgrade; Priest PA2 Radiant Pulse -> Guiding Light (aim Sacred Heal at an ally); Berserker PA2 Shared Fury -> rage swap; Monk E5 text only.
CHECK (verified): SkyyArmory/build_skyyarmory_0.1.9.py line 6264 ArmoryTree.KEYS lists 11 nodes and leaves out Class.Monk.PB1 (Hard Knuckles), but line 9963 reads it - the tree page may still say 'Coming with SkyyArmory' for Hard Knuckles while it works (or the reverse is intended).

## 2026-10-08 07:14 Ability engine probe plan (E0)
Done: research/cloud/Ability-Probe-Plan.md - P1-P15 as /aprobe commands (0.7 classes by reflection, so P5-P13 + P15 run on 0.6.8 now; P1-P4 + P14 wait for 0.7), pass / fail + fallbacks, two short test sessions. Draft jar SkyyAbilityProbe 0.1 is written (UNTESTED; stub-compiled, 55/55 logic checks) and will come as a [cloud] PR once PR 11 is merged (my one branch is in use).
Findings: boss stunlock breakout already live in SkyyArmory 0.1.9 (reuse it); SkyyGear GearSpeed strips foreign speed effects every second (P6 will fail -> SkyyGear 'ability haste' bridge); SkyyProfiles 0.1.6 saves 6 inventory sections, so runes would leak across profiles (P14).
Questions: one shared boss breakout clock [yes]; attack-speed buff bumps the weapon tier [yes]; two probe sessions (0.6.8 now, 0.7 later) [yes].

## 2026-10-08 12:39 Skyy answered the ability probe questions
Skyy, word for word (2026-10-08, to the cloud session): "1. yes.  2. yes temporarily, 3. wait till 0.7" - for research/cloud/Ability-Probe-Plan.md Q1-Q3. Please record in docs/answered/classes.md (qa_append):
Q1 ability hits share the boss breakout clock (reuse the SkyyArmory 0.1.9 stunlock counter); Q2 attack-speed buffs bump the weapon one speed tier - TEMPORARILY (small SkyyGear change); Q3 no 0.6.8 probe session - all P1-P15 in one session after Hytale 0.7. Noted in the plan file.

## 2026-10-08 Ability input design
Done: research/cloud/Ability-Input-Design.md. Two keys, three stances: Ability2 = line 1, Ability3 = line 2, Ability1 stays the Signature; the SAME ability casts differently grounded / crouching / mid-air (crouch = self / placed-here, never moves you; mid-air = below you / on landing; mid-air beats crouch so Plunge, Monk air jump and double jump keep crouch-in-air). Sprint is never read (roll stays on the sprint tap). Hotbar ability items: select = cast, auto-return to the weapon, cooldown as the item's durability bar, soulbound, 1 per slot, mirror of the equipped lines + utility items (Loadout / Hints); unequipped casts only behind a server toggle (off). 14 proposed stance variants (2 per class), flow rules (buffer 500 ms, rising edge, ready ping, first-use hints per stance), 15 PROBE items K1-K15 for SkyyKeyProbe (K13 = does the player-level Interactions override beat the 0.6.8 crossbow reload on Ability3; K14 = 0.7 Ability4 as a real 3rd key), build phases I0-I6 owned by SkyyClasses (stance resolver folded into engine E1).
Questions for Skyy (defaults): same ability in 3 shapes not 3 abilities [yes]; items may cast an unequipped ability [no, server toggle]; crouch variants never move you / never cost more [yes]; 0.7 Ability4 as a 3rd key [wait for 0.7]; variants order Mage + Priest first, Archer last [yes].
UNVERIFIED: all of K1-K15; the live acro.doubleJump.trigger value; a server-side selected-hotbar-slot API (K6); the PACK.md Ability2/3 survey before phase I3.

## 2026-10-08 13:42 Class ability shapes
Done: research/cloud/Class-Ability-Shapes.md - Skyy's 2026-10-08 lines (153-156) applied to every class: 4 owned abilities = 2 PRIMARY (Ability 2 / 3: walking, sprinting, mid-air shapes) + 2 ALT (crouch + Ability 2 / 3: one crouch shape, a little different). All 35 designed abilities (A1, A2, A2-alt, both A1-alts) get 4 shape lines with cost / cooldown per shape (most "same"; bigger shapes +2-4 Mana / +2 s). Good primary pairs + engine risk per class (K3 / K4 / K11 / K13 / K15, P5 / P11 / P12 UNVERIFIED). Shared rules: pick primaries out of combat on the class page (alts = the other 2, no empty slot; key order swappable); shape read at the press, mid-air > crouch > sprint > walking, crouch in the air = movement; crouch shapes never move you; mid-roll cast = sprinting shape if sprint still held, dropped if the probe says no; SkyyHud 2 rows that switch to the alts while crouching. Build order: shape resolver, then Mage + Priest, Monk + Assassin, Warrior + Berserker, Archer last.
Questions (defaults): sprint shapes may step you 2 blocks [yes]; per-shape costs as tabled [yes]; mid-roll = sprinting shape [yes]; Guardian Spirit press = Spirit Call / Spirit Pulse proposal [passive only first]; HUD 2 switching rows [yes]; 3 owned = 2 primary + 1 alt [yes]; hotbar items cast the walking shape [keep for later].
UNVERIFIED: K3 / K4 / K11 / K12 / K13 / K15 (probe after 0.7), landing-point prediction for "on landing" shapes, slow-fall callable from SkyyClasses, live acro.doubleJump.trigger, ~420 per-shape rows (store deltas).

## 2026-10-08 Signature proposals
Done: research/cloud/Signature-Proposals.md - 3 options per family, recommended: Bo Whirling Staff, wraps/gauntlets/claws Flurry, kunai Kunai Fan, spellbooks Page Storm. Daggers keep Razorstrike; soul cage owner unknown.
Questions (defaults): pick per family [recommended]; charge from hits only, ~8-10 hits [yes]; claws share wraps' signature with bleed [yes].
UNVERIFIED: vanilla signature chains (Vortexstrike, Razorstrike, BigArrow, Volley); multi-projectile / pierce signature roots; Ability 1 roots for new families.

## 2026-10-08 Wardrobe spec
Done: research/cloud/Wardrobe-Spec.md. Own mod SkyyWardrobe (not SkyyGear): Menu tile + /wardrobe, 9 slots x 2 pages, 4 free then Overall Lv 10 / 20 / 30 / 40 -> 6 / 10 / 14 / 18 (SkyBlock's ladder by level, not rank). Equip = one world-thread task swapping worn <-> slot per spot with a write-ahead journal + read-back + join-time repair (SkyyProfiles / SkyyVault patterns); Store / Take out / Put in by buttons only (no drag); partial sets keep the worn piece (SkyBlock; swap.strict row). LOOKS: per slot, the union of family looks over the 4 pieces, Apply moves every piece that has that look (same family only, metadata cloned, durability by fraction, no craft event), 500 coins (Alteration Kit optional), pieces without that look keep theirs; preview = target icons (player model UNVERIFIED). Files per pkey, lossless (ItemStack.CODEC + explicit fields), atomic + rev-ordered, nothing deleted; refused while dead / 10 s combat / profile:busy / 30 s after a switch / 1 s gap / stale page rev.
Hypixel facts (cited): 2 pages, Default 4 / VIP 6 / VIP+ 10 / MVP 14 / MVP+ 18 (+9 Community Center gem slots), 2 free before July 2026, cooldown 0 since 0.26 (was 30 s), armor only (Equipment Wardrobe separate), July 2026 wipe bug = loss, not dupe.
Questions (defaults): free 4 + level ladder [yes]; worn set into the slot you equip from [yes]; partial = keep worn piece [yes]; Looks on the worn set [W3]; 500 coins [yes]; no unidentified [yes]; names 16 chars [yes]; own mod [yes].
UNVERIFIED: E1 armor container set / remove from a page click, E2 SkyyGear resync on setItemStackForSlot, E3 player preview element, E4 Armory ids round trip, E7 asset scan WARN without The Armory. Plan: W0 probes -> W1 ultracode (needs nothing else) -> W2 looks (needs Recolor P1 gear:base).

## 2026-10-08 Own special weapons draft
Done: research/cloud/Own-Specials-Draft.md - 21 specials of our own as boss drops so every class has 4 (Berserker keeps 5 + flails). One passive hook each, never a class ability / signature / element. Assassin: The Fine Print (side backstabs), Return to Sender (RETURN drags your target), The Carbon Copy (real dual swords, cross-slash every 3rd hit). Mage: The Long Form (piercing staff - Skyy's idea), Form 27-B/6 Annotated (+25% amp margin), The Forwarding Address (homing staff), The Unabridged Edition (+10% per extra enemy). Priest: The Courtesy Copy (shots heal allies they pass), The Interoffice Memo (shots through blocks - Skyy's idea), Hold Music (bind an ally), Next Please (Binding jumps on kill). Archer: The Filing Spike (ground spikes), The Rubber Stamp (hits reload), The Long Distance Call (flat flight + range damage), The Final Notice (magazine dump). Monk: The Long Queue (bound landings hit), The Firm Handshake (power hit heals 5%), The Stamp of Approval (finisher slam), Thank You For Waiting (block builds Patience). Warrior: The Long Arm (spear returns), The Counterclaim (parry shield). Bosses: zone guardians, dungeon + slayer bosses, the Dragon, Final Audit F1 / F2 / F3 / F6; levels 20 / 30 / 45 / 60 / 70 / 79-94.
Questions (defaults): approve / swap per item [keep all]; Monk 3 or 4 [4, drop Thank You For Waiting if 3]; the parry shield Warrior-only [yes]; 5% drop + x3 own-class lean, slayers via the RNG meter [yes]; Legendary + modifiers roll + Mystery Bag [yes]; office-tone names [keep].
UNVERIFIED: all engine hooks (backstab angle, mob pull on RETURN, one-item dual-wield model, projectile steering / through-blocks, ally Binding, arrow landing trigger, magazine write, arrow gravity, crossbow hold next to BigArrow, finisher recovery, block-hit timing, spear projectile). Note: tools/docs_check.py already FAILs on main (broken links in INDEX / RESUME / the hotbar-items readme / the October log) - not from this file.

## 2026-10-08 Untiered / Mythic / Set spec
Done: research/cloud/Untiered-Mythic-Spec.md. UNTIERED (orange, 8th quality asset): fixed stats, no roll / Identify / modifier Reforge, one trade-off line, level from the source clamped to its tier, level-up +3; grid = 14 weapon types + 3 armor sets x 6 ZONE tiers (156 eventually); first batch U1-U10 at Lv 15-29 (The Loophole pierce staff -30% dmg = Skyy's example, Paperweight sword, Overtime axe, Pocket Knife dagger, Short Notice bow, Second Opinion wand, Turnstile Bo + Filing Cabinet / Courier's Leathers / Intern's Robes sets); sources per Skyy's lock = mob drops (1% of the extra roll, elites 3%), loot chests (vanilla 1%, Unclaimed Luggage I-IV 0.5-8%, dungeon end chest 8%), bosses (5% line) and quests (one per zone); never crafted, never NPC shops; drops identified, no bag. MYTHIC (purple) = all boss gear: Fabled base x1.10 + the live 6-modifier row + one hook, level = boss level, level-up cap +2, OUT of the random odds + Smithing step-up; pools 3+ weapons / 4-8 armor, full sets Zone 1, halves Zone 2, split 2-3 bosses later; sample pools for Second-Page Guardian, Praetorian, Trork Chieftain, Broodmother, Goblin Duke, Scarak Overseer (Own-Specials weapons + Armory Rook / Warden / Ghost Rook / Jester / Cobalt Dragon / Calvary / Priest sets); 4 world drops. SET (green): set table + `set` document field, full-set check on the armor pass, quest rewards; gathering armor = green Sets with a per-tier Fortune / speed / move-speed table (Skyy's 2026-10-08 lock applied). Appeals Desk (BL4 Big Encore): appears after the story kill, boss level x 25 coins, 60 s cooldown, everyone with 15% credit rolls; Formal Complaint = x2 Health / damage + 1 affix, x2 cost, x2 Mythic chance, needs one normal desk kill. Drops: 10% Mythic roll per participant (20% Challenge), own-class / own-type lean x3, purple bag tagged with the boss pool (pick at identify, re-roll inside the pool), RNG meter 40 per boss. Mods: SkyyGear G1 rarity round (label, Mythic off the ladder, per-rarity caps, set check) -> G2 UT batch -> SkyyMobs B1 boss stage ultracode -> B2 desk + challenge -> B3 meter + /bosses page; SkyyQuests for Set + quest UT rewards.
Questions (defaults): zone-band tiers [yes]; UTs tradable + identified [yes]; caps Mythic +2 / UT +3 [yes]; U1-U10 [keep]; UT takes pierce, M1 The Long Form = pierce + 5% per enemy passed [yes]; Mythic boss-only [yes]; 10% / lean x3 [yes]; the 6 pools [approve]; full-set only [yes]; capstone uniforms -> Mythic split sets [yes]; gathering set numbers [as tabled]; coins not tokens [coins]; everyone rolls [yes]; desk in SkyyMobs [yes]; world drops [yes]; names [keep].
UNVERIFIED: 8th quality asset + orange contrast; the armor-change hook for the set check; vanilla slots (no boots) + Armory slot lists; ODDS column order + LADDER incl. Mythic; scale.role x Challenge stacking; per-item arrow speed / gravity, staff pierce, knockback; Mythic NPC sell values vs desk fee; profile storage for meters. docs_check still FAILs on main from the pre-existing links.

## 2026-10-08 Arcblade class page
Done: research/classes/Spellblade.md as a [cloud] draft on branch `cloud/arcblade-class-page` (commit 5107889 pushed; no `gh` here, so the PR itself is not opened - open it from the branch (https://github.com/SkyyPlayz/SkyyWynnBlock/pull/new/cloud/arcblade-class-page), or take the copy research/classes/Spellblade.md, pushed to main as the fallback the task named; delete the copy after the merge). Follows classes.md lines 165 + 167 word for word. Class skill proposed: Battlemagic.
Kit: A1 ARCANE BREACH (180 deg arc, 5 blocks, 1.2 H, enemies take +15% from everyone 8 s, +1% per Momentum stack; non-elemental unless imbued; full on bosses) / A1-alt A RIFT CLEAVE (Breach that leaves a 2x8 slowing rift 3 s) / A1-alt B SHATTERING ARC (Breach that spends Momentum: +0.1 H and +1% Breach per stack, keeps 5) / A2 ELEMENTAL IMBUE (12 s: arcs deal +30% element damage + the element's status; the sword's element or the attuned one) / A2-alt SUNDER (one target 2.0 H: Weakened 15% + Exposed +20% crit damage for everyone, 12 s, full on bosses - the boss debuff). Every ability: 4 shapes with cost / cooldown, 4 modifiers, Echo yes on Sunder + the A1-alts, no on Breach / Imbue.
Momentum: 0-20 stacks, +1 per enemy hit (max +2 per swing), rhythm bonus +1 inside a 0.4 s flow window, each stack decays 4 s; per stack +1.5% attack speed / +1% arc size / +1% element; Rolling (7) = momentum push +5% ally move speed + one speed tier; Unstoppable (14) = push +10%, no hit-stun, statuses +50%; heavy hit -3, stun = all, sword-shield swap keeps half, guard pauses decay.
Weapons: two-handed swords (Armory longswords + Zweihander + the 4 shelved Elementals; our own later) with 120 deg / 3.5-block arcs, charged CRESCENT RUSH (6-block dash + 180 deg sweep, elemental crescent at 10+ Momentum; 8 Mana + 4 Stamina). NEW GREAT SHIELD (two-handed tower shield, element rune glows): bash, right-click full guard (100% projectiles / 70% melee, allies behind you 25% less), charged BULWARK CHARGE (8-block shoving charge, carry + end shove; 4 Mana + 5 Stamina). No cooldowns, no void protection.
Elements: no element spec exists - marked as a DEPENDENCY; proposed the engine's five (Fire Burn, Water Chill->Freeze, Earth Stagger, Wind Gust, Lightning Shock), Poison = a status; Armory Gravity sword = Earth [Q7]. Imbue can ship Fire-only first.
Tree: trunk 6 + Tempest (elements, reactions) / Breaker (boss debuffs) / Vanguard (great shield + Momentum push), same gates as Class-Tree-Paths.
Questions (defaults): skill name [Battlemagic]; Momentum numbers [yes]; Breach vs Archer Mark [higher + 5%]; kit [keep, Rift Cleave first]; elements + Gravity = Earth [yes]; Echo list [as listed]; great shield design [yes]; traversal costs [yes]; signatures Meridian Cut / Iron Curtain [yes]; Mana +5 per level, Light armor [yes]; Warrior gives up longswords + Zweihander now [yes]; build after the engine E1-E4, Armory items first [yes].
UNVERIFIED: Armory longsword move set (hook or CC BY-NC override), runtime arc reach, attack speed per stack vs SkyyGear tiers (one tier temp), flow-window timing (P2), two-handed guard item (Bo block pattern), carrying mobs (Monk probes 7-8), player hit-stun immunity (breakout code), Breach / Weaken / Expose filter hooks + Mark rule, element damage through SkyyGear stats, statuses (E7), Armory ids in the class table, an 8th class in SkyyClasses + tools/class_pages.py CLASSES. Files that still give the Warrior the longswords (research/classes/Warrior.md, the research/classes/README.md table, research/cloud/Own-Specials-Draft.md, research/cloud/Untiered-Mythic-Spec.md pools + UT grid 14 -> 16 types, research/Pack-Armor-Plan.md gates, research/cloud/Weapon-Speed-Tiers.md, research/cloud/Class-Ability-Shapes.md) are listed in the page for you. docs_check: this page adds no broken path of its own (research/classes/Spellblade.md resolves once the PR merges); the 4 pre-existing BROKEN links on main remain (three to a missing backups readme from INDEX / RESUME / the October log, one in art/hotbar-items/README.md).

## 2026-10-09 13:14 Dynamic Seasons crash report draft
Done: research/cloud/DynamicSeasons-Crash-Report.md - item 10 ready to paste into research/Author-Requests.md (cloud can't push that file to main). Friendly bug report for BlueOrbit: what happened, the trimmed stack, guess = re-added crop entity gets CropQualityComponent twice (use put / add-if-missing). Fill 3 fields from the crash log: time, server build, mod count. Other 4 specs (archipelago, pet core, elements, ability engine plan) are running now.
Also: SkyyMonkProbe is retired (632263f) - close https://github.com/SkyyPlayz/SkyyWynnBlock/pull/11? Once it's closed or merged I can open the SkyyAbilityProbe PR on my branch.

## 2026-10-09 13:19 Pet core spec
Done: research/cloud/Pet-Core-Spec.md - pets are per-profile records (never items; eggs are items), slot-2 lifecycle (logout auto-store, world change, profile switch, death, 10 s orphan sweep), defeat cooldown 60 s -> 15 s by level, Follow / Defend / Hold, 3 vanilla pages, ~25 Server Setup rows, phases SkyyPets 0.1-0.6 + probes P1-P10.
Needed in other mods first: SkyySkills pets:fn:onxp hook; SkyyGear gear:extra must take a map (pets would overwrite accessory stats - SkyyGear 0.2.11 line 11147); SkyyMobs exclude SkyyPet_* (0.1.5 line 775). Doc conflict: research/cloud/Pet-Sources.md says no NPC sells eggs, docs/answered/economy.md line 92 (newer) adds them - spec follows the newer line.
Questions: records not items [yes]; paid early revive [off, owner can enable]; slot-1 pet shown by default [yes, hideable].

## 2026-10-09 13:21 Element system spec
Done: research/cloud/Element-System-Spec.md - the five = Fire / Water / Earth / Air / Thunder (gear names; Spellblade's Wind / Lightning renamed). SkyyGear 0.2.11 today: rThunder / rWater / rElem lines (1242-1249) summed into ONE untyped number in GearHit.elemSum (13055-13062), after armor, never crits; Defence lines exist but never roll. Plan: split that sum into 5 typed parts (same total), mob Weak / Resist -25% / +25% (bosses -50% own element, never immune), Imbue +30% on the same path; statuses from abilities only (Burn, Chill->Freeze, Stagger, Shock, Gust + Poison); no reactions at launch. Build: SkyyGear 0.2.12 + SkyyMobs 0.1.6 full round first. Probe E1 blocks statuses (ability hits may take weapon element lines each tick).
Questions: one name per element (gear names) [yes]; -25/+25, bosses -50 [yes]; no reactions now [yes].

## 2026-10-09 13:23 Class ability engine plan (Mage + Priest first)
Done: research/cloud/Ability-Engine-Plan.md - SkyyClasses owns the engine (SkyySkills pools, SkyyArmory traversals + stun clock, SkyyHud widget). All 37 Mage / Priest shape rows affordable at Lv 1/10/20/30 against the real SkyySkills 0.4.25 pools (python3). Rounds: R1 core + /cast + Meteor + Sacred Heal (SkyyClasses 0.1.15), R2 HUD widget, R3 Mana Barrier + Shield Bubble, R4 real keys via 0.7 runes, R5 shapes, R6 Guardian Spirit + Frost Nova + stun-clock bridge, R7 A1-alts + page, R8+ levels / modifiers / Echo - each with 'what Skyy checks'.
Findings: SkyyClasses DamageLock (2638-2685) would zero a Meteor that lands after a weapon swap (R1 tags ability damage); SkyySkills credits kill XP by the held item, so ability kills may pay the wrong skill. Level-1 Mana in code = 55 / 47, not the 45 / 42 in research/Class-Power-Split.md.
Questions: /cast until 0.7 runes [yes]; admin grant for Lv 10+ abilities [yes]; abilities keep working after a weapon swap (check at cast only) [yes].

## 2026-10-09 13:26 Zone archipelago worldgen spec
Done: research/cloud/Zone-Archipelago-Spec.md - each zone = summit isle + 4-6 outer islands joined by land necks, rock arches and built bridges (32-40 openings, x/z only); ~3x land per zone; island centres fixed at build time (town / portal need known spots); own numbers, Welkin's only described. Gap 1,100 blocks hull to hull (a 4:1 glide from y 190 reaches 888). Caves squashed x0.67: upper to y 110, deep to y 76, lava caverns to y 44 (lava sea y 52), 12-block shell guard; Zone 5 under the Z4 caldera. Build plan SkyyWorldGen 0.3 node proof -> 0.4 caves + lava -> 0.5 Zone 1 (new world 'skywynn') -> 0.6-0.8 Zones 2-4 -> 0.9 Zone 5, each with a harness proof + Skyy test.
Hazard: a biome's Empty-material queue could fill the void under islands with lava (3 fallbacks in the spec). 12 engine checks for the local session.
Questions: next zone visible (2026-10-03) vs far apart (2026-10-09) - default 1,100 blocks, not visible; 3x = total land per zone [yes]; players may build bridges inside a zone, gaps between zones no-build [yes].

## 2026-10-09 13:26 2026-10-09 cloud list done
All 5 tasks from the 2026-10-09 block are done and pushed (one block each above). Only the SkyyAbilityProbe PR is left, waiting on https://github.com/SkyyPlayz/SkyyWynnBlock/pull/11 (close it now SkyyMonkProbe is retired?). Send more tasks any time.

## 2026-10-09 18:47 2026-10-09 evening tasks started
Got the 5 new tasks - all running in parallel now (Mining armor spec first priority; UT first batch, gathering armor stats, SkyyQuests Zone 1, Guild Games). One OUTBOX block each as they land. PR 11: OK, Skyy closes it; then I open the SkyyAbilityProbe PR.

## 2026-10-09 18:50 Guild Games spec draft
Done: research/cloud/Guild-Games-Spec.md (design doc, later content). Modes: Castle Raid (1v1), Alliance Battle, 12-guild Institute (Red Rising, captures). Wagers in escrow: pot state machine, 5% fee (coin sink), crash = full refund of every live pot (never auto-pay a winner). Proposed new SkyyGames mod; 12 engine probes (1-4 first: arena copy of a build zone, castle prefab id, mounted crossbow, flag carrier); 6 rough phases. Repo has no castle / team code yet (only the SkyyGuilds bank + bridge read - please confirm).
Questions: Mythic / UT / Sets wagerable [no - coins, guild gold, tradable items only]; wager fee [5%, Server Setup]; Institute captures [3 lives, freed when the holding castle falls, cap 50% of the captor's roster].

## 2026-10-09 18:53 SkyyQuests Zone 1 spec
Done: research/cloud/SkyyQuests-Zone1-Spec.md - chain town1 'The Department of Arrivals', 9 quests Lv 1-20 (merges story Z1.1-Z1.5 + Bank / Bazaar / mail / Forge errands; givers Mossby, Pebble, Banker, broker, Smith, Hermit), rewards 2,050 coins + 750 skill XP; quest 9 = a class UT2 weapon (owed until SkyyGear can grant it). Daily Job Board (3 jobs per profile from 12, 00:00 UTC reset, coins + XP only). Claim ledger + idempotent grant ids for dupe safety; 22 Server Setup rows, 14 probes. Design call: SkyyTowns owns the NPC Use hook, SkyyQuests answers via quest:fn:hasoffer / quest:fn:talk (needs a quest= key in npcs.json; research/Zone-1-Town-Build-Plan.md section 6 doesn't say it yet).
CONFLICT to settle: the spec's quest Set 'Clerk's Copper' uses vanilla Armor_Copper_* - the same items the Mining armor spec makes the Copper MINING set. One item can't be both; I'll flag it in the Mining spec result too.
Questions: quest 9 UT fixed to your class [yes]; quest Set piece level = quest level [yes]; Pebble in every town [yes]; quest Set / UT tradable [yes].
