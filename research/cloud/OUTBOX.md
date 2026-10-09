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
