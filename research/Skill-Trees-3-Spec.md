# Skill Trees 3 - Borderlands-style trees, dust removal, Void Particles (spec)

Status: DRAFT for Skyy, 2026-10-18. Replaces the token + Dust trees (Skill-Trees-Spec.md / Skill-Trees-2-Spec.md) and the 44-node class tree
(Ability-Tree-Redesign-Spec.md) with ONE pattern. The rebirth currency changes to Void Particles (research/cloud/Rebirth-Spec.md 2.3 / 3.4 / 3.5).
Where this file and those disagree, this file wins once Skyy approves. Index: INDEX.md. Questions: section 8. Answers go to docs/answered/skills.md.

Skyy (docs/answered/skills.md, last line, 2026-10-18): "the biggest thing right now is the skill tree ... no free upgrades. (i want borderlands
style where you have a few upgrades each row, you have to spend an so many points total to unlock each row, and the ability's come free with
the row they unlock in (you start with the first ability.) (look into all the borderlands games and how they build their classes for ideas on
what to put in each classes tree.) i want all the skill trees to follow the same general pattern. drop the dust, then we can make the rebirth,
and rebirth upgrades boost the skill xp ... void particles from rebirthing, spend them on upgrades, but the rebirth particles also give you a
small buff. probably overall xp gain. so you have to balance how much you spend on what upgrades with how much you keep."

Method: the Borderlands facts and the class / skill tree drafts below were drafted by Jev / free models (tools/llm.py), then checked against
the repo (ability names, ratings, existing node names). Numbers in the trees are first-pass; the balance pass (Balance-Pass-Spec.md) tunes them.

## 1. Borderlands research (BL1, BL2, Pre-Sequel, BL3, Wonderlands) - what to copy

| Topic | What the games do | SkyWynn takes |
|---|---|---|
| Row gating | BL1/BL2/TPS: 3 trees per class, 6 tiers; a tier opens after 5 points per tier are already spent IN THAT TREE (0/5/10/15/20/25). BL3/Wonderlands gate by total points in the tree (lets you dip) | BL2 rule: points spent in the SAME branch (forces real specialising); no dip loophole |
| Points | 1 per level, cap 50 (BL1/2/3), 40 Wonderlands; nobody fits every tree, so builds differ | 1 per level; tree capacity ~130 vs 50-100 points, so nobody has it all |
| Capstone | BL2 tier 6 = build-defining, often mandatory (Money Shot); BL3/Wonderlands weaker, outclassed by gear | Capstone changes how the ability plays, costs 3 points, never a mandatory tax |
| Action skill | BL1/BL2: one fixed skill, skills tune it (cooldown, duration, damage); BL2 / TPS "augment" skills change what it does (Maya Thoughtlock); BL3: 3 action skills + 2 augment slots; Wonderlands: 2 + class feats | Our 5 designed abilities per class stay; each upgrade modifies ONE ability (= our modifiers); capstones act like BL2 augments |
| Roles | One tree per playstyle (Maya: Motion control / Harmony heal / Cataclysm damage; Axton: turret / dps / tank; Salvador: gunzerk / guns / tank; Gaige: chaos / pet / support) | 3 branches per class, one per part of its role in research/Class-Roles-Sheet.md |
| Respec | Cheap at a vendor (coins in BL1/2/TPS, free in BL3/Wonderlands) | Coins that scale and then cap, plus one free per rebirth (2.6) |
| Mistakes | Dead 5-point "tax" nodes (Fleet, Prepared), mandatory capstones, stat-stick rows, passive-only trees | Every row has an interesting pick; capstones optional; no row is only stats |

Spot-check: row thresholds, 1 point per level, 6 tiers and cap 50 are the standard published facts. The models flagged their own doubt on BL1
exact tier costs and Wonderlands' current cap - not used here. (No web check was run; WebSearch not needed for the used facts.)

## 2. THE ONE PATTERN (every class tree and every skill tree)

### 2.1 Shape
- A tree = 3 branches (all 8 classes; Mining, Foraging, Combat, Beastmastery, Farming, Cooking, Alchemy) or 2 branches (Fishing, Exploration,
  Acrobatics, Smithing - light).
- A branch = 6 rows (light skills: 4). Row r opens when `5 x (r-1)` points are already spent IN THAT BRANCH: 0 / 5 / 10 / 15 / 20 / 25 (light: 0 / 5 / 10 / 15).
- Rows 1-5 hold 2-3 upgrades; an upgrade has 1-5 ranks, each rank costs 1 point. Row 6 = ONE capstone, rank 1, costs 3 points.
- Branch capacity ~43 points (rows 1-5 about 8.7 each) + 3; tree capacity ~130. Reaching a capstone costs 25 (gate) + 3 = 28 in that branch.

### 2.2 Free abilities (no point cost)
- Opening a row gives its ability free (class ability, or a skill's perk). Row 1 of branch 1 = the starting ability, owned at level 1.
- Class: Row 2 of each branch = one ability (3), and Row 5 of one branch = the fifth (5 designed: primary, 2 alts, secondary, secondary alt). Own 5,
  equip 2 (SkyyClasses unchanged). Skill: Row 1 of branch 1 = start perk, Row 2 = an active perk, others passive.
- Branches 2 and 3 Row 1 are upgrade-only, so a fresh player owns exactly one ability.

### 2.3 Points
- 1 point per level, class and skills alike, from level 1. No other source: no tokens, no Dust, no free ranks.
- Class points = class level; skill points = that skill's level. Cap 50 on the first run, +10 per rebirth.

| Level | 50 (run 1) | 60 | 70 | 80 | 90 | 100 (rebirth 5) |
|---|---|---|---|---|---|---|
| Points | 50 | 60 | 70 | 80 | 90 | 100 |
| Reaches | 1 capstone branch (28) + 22 in a 2nd | +10 | 2 capstones + a bit | 2 capstones + deep 3rd | 2.5 branches | 3 capstones (84) + 16 |

Nobody fills a tree (130 capacity). A tree is only part of power: it stacks with weapon / tool, gear, accessories and pets (four power sources).

### 2.4 Class vs skill trees
- Class upgrades: modifiers of that branch's ability (existing names: Power, Radius, Duration, Efficiency, Pierce, Chain, Slow, Knockback, Ricochet,
  Pull, Leech, Split, Lingering, Follow, Ward, Echo, Haste, Floor), plus class resource (Momentum, combo) and defence. A modifier needs only its row
  (Ability-Tree-Redesign 4.1 already dropped the ability-level gate).
- Skill upgrades: speed / fortune / XP, tool-tier scaling, accessory and pet synergy. Perks are active or passive.
- Depth by importance (Skyy 10-18): Mining, Foraging, Combat, Beastmastery essential (richest rows); Farming, Cooking, Alchemy useful (full trees, milder
  numbers); Fishing nice-to-have (light, until its rework). Every skill has a row with gear / accessory / pet scaling.

### 2.5 No free upgrades
No levelling of upgrades from XP, Dust or Tokens. Every rank is bought with a point. Abilities that come with a row are the only free thing.

### 2.6 Respec
- One tree at a time (class, or one skill). Refunds ALL points, abilities re-lock, equips on locked rows clear. Blocked in combat.
- Coin cost `100 x level x min(n, 5)`, n = respecs of that tree this run (first = `100 x level`). One free respec per tree per rebirth.
- Journal the old picks in History for Undo (PROJECT-RULES 4).

### 2.7 UI
research/Menu-Pattern.md: tab row = 3 branches, scroll list of rows, each upgrade a button `Name  rank/max  cost`; a locked row shows "needs 10 points in
Bulwark - you have 6". Lattice slot panel stays for abilities. No radiating tree here (only the Nexus).

## 3. Class trees (8)

Notation: `[free: X]` = ability the row unlocks, `(max N)` = ranks, R6 = capstone. Roles/ratings: research/Class-Roles-Sheet.md (Skyy-approved
10-18); abilities: research/classes/*.md (names checked). Each branch buffs the class's strong stats, never its weak ones. Numbers are placeholders.

TREE Warrior (Tank / crowd control)
 Branch 1 Bulwark: mitigation, max HP, standing your ground
  R1 [free: Rallying Guard]: Iron Skin (max 5): -4% melee damage taken per rank | Last Stand (max 3): +6% max HP per rank
  R2 [free: Bulwark Stance]: Duration (max 5): Bulwark Stance lasts +2s per rank | Ward (max 3): Stance shields you for 4% max HP per rank
  R3: Knockback (max 3): melee hits knock enemies back 0.5 blocks per rank | Stone Guard (max 3): -3% ranged damage taken per rank
  R4: Slow (max 4): enemies you block are slowed 12% per rank for 2s | Leech (max 2): blocking a hit heals 1% max HP per rank
  R5 [free: Unbreakable]: Duration (max 4): Unbreakable lasts +2s per rank | Anchor (max 3): -5% damage while standing still per rank
  R6 capstone: Aegis Eternal: Bulwark Stance is permanent; allies within 6 blocks gain 50% of its ward and your blocks slow attackers 40% for 2s
 Branch 2 Shockwave: AoE stuns and knockback
  R1: Radius (max 4): Rallying Guard taunt/ward radius +1 block per rank | Power (max 5): Rallying Guard ward +5% per rank
  R2 [free: Shield Shockwave]: Knockback (max 5): Shockwave knockback +0.5 blocks per rank | Concussion (max 3): 12% chance to stun 1s per rank
  R3: Slow (max 5): Shockwave slows enemies 10% per rank for 3s | Chain (max 2): Shockwave arcs to 1 extra enemy per rank at 50% damage
  R4: Duration (max 4): Shockwave slow/stun +0.5s per rank | Power (max 3): Shockwave damage +6% per rank
  R5: Fissure (max 3): Shockwave radius +1 block per rank | Tremor (max 2): shocked ground deals 15% damage/s per rank for 3s
  R6 capstone: Rumble: while Bulwark Stance is active, Shield Shockwave auto-fires every 5s and always stuns 1.5s
 Branch 3 Iron Chain: pulls, grouping, party warding
  R1: Ward (max 5): Rallying Guard also shields allies 3% max HP per rank | Chain (max 3): taunted enemies take +4% damage from you per rank
  R2 [free: Iron Chain]: Pull (max 4): Iron Chain drags enemies 1 block closer per rank
  R3: Chain (max 3): Iron Chain binds 1 extra enemy per rank | Leech (max 3): Iron Chain hits heal you 2% max HP per rank
  R4: Slow (max 3): chained enemies lose 10% attack speed per rank | Ward (max 4): party wards from your abilities +4% per rank
  R5: Heavy Links (max 4): Iron Chain damage +5% per rank | Duration (max 3): chain bind/slow +1s per rank
  R6 capstone: Warden's Grip: Iron Chain yanks every enemy in 8 blocks to a point, roots them 2s, and refreshes all party wards to full

TREE Berserker (party damage buffer / sustained melee)
 Branch 1 Bloodlust: leech, adrenaline, self-sustain
  R1 [free: Enrage]: Leech (max 5): heal 1.5% of damage dealt per rank | Adrenaline (max 3): +4% attack speed per rank below 60% HP
  R2 [free: Blood Frenzy]: Duration (max 5): Blood Frenzy lasts +2s per rank | Leech (max 3): Frenzy leech +1% per rank
  R3: Echo (max 2): every 5th melee hit repeats at 40% damage per rank | Thirst (max 3): kills heal 2% max HP per rank
  R4: Power (max 5): +3% melee damage per rank while Enraged | Haste (max 4): +3% movement speed per rank during Frenzy
  R5: Red Mist (max 2): leech effectiveness +50% per rank below 30% HP | Duration (max 3): Frenzy refreshes 1s per kill per rank
  R6 capstone: Crimson Eternal: Blood Frenzy never expires while you've hit an enemy in the last 3s; leech overheal becomes a 10% max HP ward
 Branch 2 Warlord's Banner: ally damage buffing
  R1: Power (max 5): Enrage also grants nearby allies +2% damage per rank | Radius (max 4): Enrage ally radius +1 block per rank
  R2 [free: Warlord's Banner]: Duration (max 5): Banner lasts +2s per rank | Power (max 3): Banner grants +3% damage per rank
  R3: Haste (max 4): Banner grants +3% attack speed per rank | Ward (max 3): Banner shields allies 3% max HP per rank
  R4: Radius (max 4): Banner radius +1 block per rank | Echo (max 2): Banner re-pulses its full buff every 4s per rank
  R5: Blood Price (max 3): allies inside Banner leech 1% of damage dealt per rank | Power (max 3): Banner damage buff +5% per rank
  R6 capstone: Warlord's Domain: Banner becomes a permanent aura at 60% effect; kills inside it extend all active buffs by 2s
 Branch 3 Warpath: AoE melee, spin-to-win, stamina
  R1: Split (max 3): melee cleaves 1 extra target at 40% damage per rank | Power (max 5): +3% melee damage per rank
  R2 [free: Whirlwind]: Radius (max 4): Whirlwind radius +0.5 blocks per rank | Split (max 2): Whirlwind hits 1 extra target per rank
  R3: Haste (max 4): Whirlwind spin speed +10% per rank | Slow (max 3): Whirlwind hits slow 8% per rank
  R4: Floor (max 3): Whirlwind leaves a bleed floor, 15% damage/s per rank | Duration (max 3): Whirlwind lasts +1s per rank
  R5 [free: Earthsplitter]: Knockback (max 3): Earthsplitter launches enemies 1 block per rank | Leech (max 3): Earthsplitter hits heal 2% max HP per rank
  R6 capstone: Endless Fury: Whirlwind becomes a holdable toggle that moves with you at 70% speed; each full spin refunds 5 stamina

TREE Spellblade (frontline AoE / boss debuffs, Momentum 0-20)
 Branch 1 Rift Cleave: close-range elemental arcs
  R1 [free: Arcane Breach]: Power (max 5): +3% spell damage per rank | Radius (max 4): Breach blast radius +0.5 blocks per rank
  R2 [free: Rift Cleave]: Radius (max 4): Rift Cleave arc width +0.5 blocks per rank | Chain (max 3): Cleave arcs to 1 extra enemy per rank at 50% damage
  R3: Slow (max 4): rift hits slow 10% per rank for 2s | Power (max 3): rift damage +5% per rank
  R4: Duration (max 4): rift slow +1s per rank | Efficiency (max 3): Rift Cleave mana cost -5% per rank
  R5: Knockback (max 3): rifts push enemies 0.5 blocks per rank | Riptide (max 3): rifts grant +1 Momentum per cast per rank
  R6 capstone: Riftmaw: Rift Cleave fires a second rift behind you; each rift cast grants +2 Momentum
 Branch 2 Sunder: vulnerability stacking
  R1: Power (max 5): Arcane Breach applies +2% vulnerability (all sources, 6s) per rank | Duration (max 3): Breach vulnerability +1s per rank
  R2 [free: Shattering Arc]: Power (max 3): Arc applies +3% vulnerability per rank | Duration (max 5): Arc debuff lasts +1s per rank
  R3: Slow (max 4): debuffed enemies lose 8% attack speed per rank | Leech (max 3): hitting debuffed enemies heals 1% max HP per rank
  R4: Chain (max 3): on death the debuff spreads to 1 extra enemy per rank | Duration (max 3): all your debuffs +2s per rank
  R5 [free: Sunder]: Power (max 4): Sunder shreds -4% enemy defense per rank | Duration (max 3): Sunder lasts +2s per rank
  R6 capstone: Fracture: Sundered enemies take double damage from Momentum-spent hits and Sunder's cooldown is halved
 Branch 3 Imbue: Momentum engine
  R1: Momentum (max 5): melee hits grant 1 Momentum at 20% chance per rank | Power (max 3): +4% elemental damage per rank
  R2 [free: Elemental Imbue]: Duration (max 5): Imbue lasts +3s per rank | Power (max 3): Imbue adds +5% elemental damage per rank
  R3: Efficiency (max 4): spending Momentum refunds 10% mana per rank | Radius (max 3): Momentum-spent hits gain +0.5 block radius per rank
  R4: Slow (max 4): imbued hits slow 10% per rank for 2s | Leech (max 3): imbued hits heal 1% max HP per rank
  R5: Echo (max 3): each Momentum spent above the echo threshold repeats 5% of the hit per rank | Power (max 3): Momentum-spent hits +6% damage per rank
  R6 capstone: Arc Cascade: at 20 Momentum your next ability is free, doubles radius, and detonates the stacks as a nova dealing 10% damage per stack

TREE Monk (speed disruptor / single-target control)
 Branch 1 Flow: movement, stamina, afterimages
  R1 [free: Flowing Form]: Haste (max 5): +4% movement speed per rank | Second Wind (max 4): stamina regen +10% per rank
  R2 [free: Hundred Fists]: Haste (max 4): Hundred Fists attack speed +5% per rank | Efficiency (max 3): Fists stamina cost -8% per rank
  R3: Echo (max 3): every 4th hit repeats at 35% damage per rank | Duration (max 4): Flowing Form lasts +2s per rank
  R4: Power (max 5): +4% damage per rank while at full move speed | Radius (max 3): Flowing Form afterimage pulse +0.5 blocks per rank
  R5: Slipstream (max 3): dodging through enemies stuns 0.3s per rank | Haste (max 3): Flowing Form grants +5% speed per rank
  R6 capstone: Untouchable: during Flowing Form you drop a striking afterimage every 0.5s (30% damage each) and gain +20% stamina regen
 Branch 2 Fist: combo pressure, ricochet
  R1: Power (max 5): +3% damage per rank | Echo (max 4): combo finishers echo at 25% damage per rank
  R2 [free: Palm Strike]: Knockback (max 5): Palm Strike launches enemies 1 block per rank | Power (max 3): Palm Strike damage +6% per rank
  R3: Ricochet (max 3): Palm Strike bounces to 1 extra enemy at 50% damage per rank | Slow (max 3): Palm Strike slows 10% per rank
  R4: Duration (max 4): Palm Strike stun/slow +0.5s per rank | Power (max 4): each combo step deals +4% damage per rank
  R5: Efficiency (max 3): finishers refund 10% stamina per rank | Flurry (max 3): +1 combo step allowed per rank
  R6 capstone: Thousand Palms: Palm Strike has no cooldown above 10 combo hits, and every 5 consecutive hits ricochet to all enemies within 3 blocks
 Branch 3 Still Water: counters and control
  R1: Ward (max 4): gain a 4% max HP ward when Flowing Form ends per rank | Slow (max 4): enemies hit during Still Water lose 10% speed per rank
  R2 [free: Still Water]: Duration (max 5): counter window +0.5s per rank | Ward (max 3): successful counters ward you 3% max HP per rank
  R3: Efficiency (max 4): Still Water mana cost -8% per rank | Ricochet (max 3): countered projectiles return at 60% damage per rank
  R4: Knockback (max 3): counters knock enemies back 0.5 blocks per rank | Duration (max 3): counter stun +0.2s per rank
  R5: Echo (max 3): counters emit a shockwave at 40% damage per rank | Power (max 3): counter damage +8% per rank
  R6 capstone: No Mind: countering an attack resets all Monk cooldowns and grants 3s of free-cast Still Water; failed counters cost nothing
TREE Assassin (Priority Killer / Debuffer)
 Branch 1 Shadowstep: stealth, openers, escapes
  R1 [free: Cloak + First Strike]: Duration (max 3): Cloak lasts +1s per rank | Ambush (max 3): First Strike +5% dmg per rank; a First Strike kill cuts Cloak CD by 1s per rank
  R2 [free: Vanishing Act]: Haste (max 3): Cloak and Vanishing Act CD -6% per rank | Fleetfoot (max 3): +3% move speed per rank, doubled while Cloaked
  R3: Efficiency (max 2): Cloak and Vanishing Act cost -10% Stamina per rank | Backstab (max 4): hits from behind +4% dmg per rank
  R4: Echo (max 1): Vanishing Act can be recast within 2s for a second blink at 50% distance | Smoke Veil (max 3): breaking Cloak blinds enemies within 3 blocks for 0.5s per rank | Nightrunner (max 2): +4% Stamina regen per rank
  R5: Phantom Edge (max 3): first hit after Vanishing Act +6% crit dmg per rank | Slipstream (max 3): a kill while Cloaked extends Cloak by 1s per rank
  R6 capstone: Ghost Protocol: a First Strike kill instantly re-Cloaks you (once per 8s) and makes you untargetable for 0.5s
 Branch 2 Executioner: single-target burst, clones
  R1: Power (max 5): +3% single-target dmg per rank | Kunai Mark (max 1): a kunai hit marks the target; your next melee hit on it deals +15%
  R2 [free: Shadow Clone]: Split (max 2): +1 extra clone per rank at 40% dmg | Duration (max 4): clones last +1s per rank
  R3: Chain (max 1): kunai bounce to 1 extra target at 50% dmg | Mirror Strike (max 3): clones copy your next ability hit at 20% power, +5% per rank | Bloodthirst (max 2): a crit grants +3% attack speed per rank for 4s
  R4: Knockback (max 1): First Strike launches the target 3 blocks toward your clones, and each clone strikes once | Lethality (max 5): +3% crit chance per rank
  R5 [free: God Killer]: Haste (max 3): God Killer CD -6% per rank | Bounty Sense (max 3): +5% dmg per rank vs elites and bosses
  R6 capstone: Deicide: God Killer deals +1% dmg per 1% of the target's missing HP (max +60%), and a kill resets its CD
 Branch 3 Venomcraft: poisons, debuffs, attrition
  R1: Lingering (max 3): poisons and DoTs last +1s per rank | Coated Kunai (max 3): kunai hits reduce the target's dmg by 2% per rank for 4s
  R2 [free: Toxin]: Power (max 4): Toxin ticks +5% dmg per rank | Radius (max 2): Toxin cloud +1 block radius per rank
  R3: Slow (max 2): Toxin slows 6% per rank | Exploit (max 4): +3% dmg per rank for each debuff on the target (max 3 debuffs)
  R4: Echo (max 1): Toxin pulses again 2s after it ends | Neurotoxin (max 2): poisoned targets receive -10% healing per rank | Second Wind (max 3): +4% max Stamina per rank; poison kills refund 3 Stamina
  R5: Efficiency (max 3): Toxin costs -8% Mana per rank | Contagion (max 3): a poisoned enemy that dies spreads 1 Toxin stack to 1 nearby enemy per rank
  R6 capstone: Black Lotus: Toxin stacks up to 3 times on one target; at 3 stacks it detonates for 200% of the remaining poison dmg

TREE Archer (Crowd Control / Focus Marker)
 Branch 1 Huntmaster: marking, precision, focus fire
  R1 [free: Pinning Shot]: Duration (max 3): Pinning Shot root +0.5s per rank | Hunter's Mark (max 3): Pinned targets take +4% dmg from all allies per rank for 5s
  R2 [free: Rapid Fire]: Pierce (max 2): Rapid Fire arrows pierce +1 enemy per rank | Steady Draw (max 4): +3% bow dmg per rank
  R3: Eagle Eye (max 3): +5% range and projectile speed per rank | Ricochet (max 1): Pinning Shot bounces to 1 more target at 60% root duration | Quickdraw (max 2): +4% draw speed per rank
  R4: Power (max 4): Rapid Fire +4% dmg per arrow per rank | Called Shot (max 2): marked targets show a weak point; hitting it deals +10% dmg per rank
  R5: Fleet Ranger (max 3): +3% move speed per rank; a kill grants 1s of Stamina-free sprint per rank | Focus Fire (max 3): each consecutive hit on the same target +2% dmg per rank (max 5 stacks)
  R6 capstone: Dead Eye: Rapid Fire on a Pinned target fires 50% more arrows, and each hit refreshes Hunter's Mark
 Branch 2 Trapper: roots, snares, lockdown
  R1: Slow (max 4): arrows slow 3% per rank for 2s | Tripwire (max 2): dodge-rolling leaves a snare that roots for 0.5s per rank
  R2 [free: Hunter's Net]: Radius (max 3): net +0.75 block radius per rank | Pull (max 1): Hunter's Net drags caught enemies 3 blocks toward its centre | Barbed Mesh (max 2): netted enemies take +5% dmg per rank
  R3: Knockback (max 2): charged shots knock back +1.5 blocks per rank | Duration (max 4): all roots and snares +6% duration per rank
  R4: Lingering (max 3): Hunter's Net leaves sticky ground that slows 15% for 1s per rank | Clinch (max 3): rooted enemies cannot use abilities for 0.3s per rank
  R5: Lockdown (max 3): Hunter's Net CD -6% per rank | Thick Hide (max 3): +3% Def per rank while any enemy within 8 blocks is rooted
  R6 capstone: Spider's Den: Hunter's Net gains 2 charges; an enemy netted twice within 6s is stunned for 1.5s
 Branch 3 Stormvolley: area denial, barrages
  R1: Split (max 2): basic shots split into +1 arrow per rank at 35% dmg | Volley Training (max 4): +3% AoE dmg per rank
  R2 [free: Arrow Rain]: Radius (max 3): Arrow Rain +1 block per rank | Duration (max 3): Arrow Rain lasts +0.5s per rank
  R3: Pinfall (max 1): Arrow Rain arrows have a 10% chance to Pin for 0.5s | Deep Quiver (max 3): +4% max Stamina per rank; Arrow Rain costs -5% per rank | Ricochet (max 2): Arrow Rain arrows bounce once at 20% dmg per rank
  R4: Power (max 4): Arrow Rain +5% dmg per rank | Pull (max 2): Arrow Rain's centre drags enemies inward at 0.5 block/s per rank
  R5 [free: Explosive Arrow]: Radius (max 3): Explosive Arrow blast +0.75 blocks per rank | Knockback (max 3): the blast knocks back +1 block per rank and staggers for 0.2s per rank
  R6 capstone: Firestorm: an Explosive Arrow fired into Arrow Rain detonates every falling arrow for 30% dmg each

TREE Mage (Burst Damage / Survival)
 Branch 1 Cosmos: Meteor and Starfall burst
  R1 [free: Meteor]: Radius (max 3): Meteor impact +0.75 blocks per rank | Power (max 3): Meteor +5% dmg per rank
  R2 [free: Starfall]: Split (max 2): Starfall drops +2 stars per rank | Follow (max 1): stars home onto the nearest enemy within 4 blocks | Astral Focus (max 3): +4% spell dmg per rank
  R3: Lingering (max 3): Meteor leaves a burning crater for 3s that deals 4% of Meteor's dmg per second per rank | Echo (max 1): a second Meteor at 40% dmg lands 1s later | Swift Casting (max 2): +4% cast speed per rank
  R4: Knockback (max 2): Meteor knocks enemies outward +1.5 blocks per rank | Shooting Star (max 4): each Starfall hit cuts Meteor CD by 0.1s per rank
  R5: Critical Mass (max 3): +5% crit dmg per rank on targets hit by 2 different spells within 3s | Comet Tail (max 3): casting Meteor grants +4% move speed per rank for 3s
  R6 capstone: Cataclysm: Meteor can be charged for 1.5s; a full charge triples its radius and pulls Starfall onto the impact point
 Branch 2 Arcanist: Arcane Beam, mana flow
  R1: Mana Well (max 4): +4% max Mana per rank | Overflow (max 2): at full Mana, your next spell deals +6% dmg per rank
  R2 [free: Arcane Beam]: Pierce (max 2): the beam passes through +1 enemy per rank | Duration (max 4): the beam channels +0.4s longer per rank
  R3: Power (max 3): beam dmg ramps +3% per rank for each second channelled | Slow (max 1): the beam slows targets 25% | Attunement (max 2): +5% Mana regen per rank
  R4: Split (max 1): after the first target, the beam forks into 2 beams at 60% dmg each | Focusing Lens (max 3): +6% spell range per rank | Feedback (max 2): a beam kill refunds 3% Mana per rank
  R5: Echo (max 2): the beam leaves an afterimage that repeats 10% of its dmg per rank 1s later | Arcane Haste (max 4): +3% cast and move speed per rank while channelling
  R6 capstone: Prism Overload: Arcane Beam has no max duration; it drains 4% Mana/s and gains +2% dmg per second held (max +40%)
 Branch 3 Spellward: mana-fuelled survival (no HP/Def stacking)
  R1: Blink Step (max 1): your dodge becomes a 4-block blink that costs Mana instead of Stamina | Arcane Skin (max 5): take 2% less spell dmg per rank
  R2 [free: Mana Barrier]: Ward (max 3): Mana Barrier absorbs +6% more per rank | Duration (max 3): the barrier lasts +1s per rank
  R3: Conduit (max 3): Mana Barrier converts dmg to Mana cost at a 5% better ratio per rank | Knockback (max 1): when the barrier breaks, it blasts enemies 4 blocks away | Mana Tide (max 2): +5% Mana regen per rank while the barrier is up
  R4: Slow (max 3): enemies that hit your barrier are slowed 8% per rank for 2s | Last Ward (max 1): once per 60s, lethal dmg instead triggers a free 1s Mana Barrier | Clear Mind (max 2): Mana Barrier CD -5% per rank
  R5 [free: Frost Nova]: Radius (max 3): Frost Nova +0.75 blocks per rank | Duration (max 3): the freeze lasts +0.3s per rank
  R6 capstone: Glacial Aegis: Frost Nova casts automatically when your Mana Barrier breaks (once per 10s), and frozen enemies take +20% spell dmg

TREE Priest (Healer / Protector)
 Branch 1 Devotion: direct healing, triage
  R1 [free: Sacred Heal]: Power (max 3): Sacred Heal +5% healing per rank | Chain (max 2): Sacred Heal jumps to +1 ally per rank at 60% healing | Efficiency (max 1): Sacred Heal costs -10% Mana
  R2 [free: Martyr's Grace]: Blood Covenant (max 3): Martyr's Grace heals allies for +6% more of the HP you sacrifice per rank | Swift Prayer (max 3): +4% cast speed per rank
  R3: Echo (max 1): Sacred Heal repeats at 30% healing after 2s | Renewal (max 3): Sacred Heal leaves a 3s heal-over-time worth 3% of the heal per rank | Long Reach (max 2): +8% heal range per rank
  R4: Follow (max 1): Sacred Heal homes onto the lowest-HP ally within 20 blocks | Triage (max 3): +5% healing per rank on allies below 40% HP | Clarity (max 2): +5% Mana regen per rank
  R5: Overheal (max 3): excess healing becomes a shield worth up to 4% of the ally's max HP per rank | Benediction (max 3): healed allies gain +3% move speed per rank for 3s
  R6 capstone: Miracle: Sacred Heal on an ally below 20% HP heals for 200% and cleanses all debuffs (8s cooldown per ally)
 Branch 2 Bulwark: shields, damage prevention
  R1: Ward (max 3): your shields absorb +5% more per rank | Steadfast (max 3): +3% Def per rank while any ally is shielded
  R2 [free: Shield Bubble]: Duration (max 3): Shield Bubble lasts +1s per rank | Radius (max 2): the bubble covers +1 block per rank | Rebound (max 1): when the bubble breaks, it pushes enemies back 3 blocks
  R3: Efficiency (max 3): Shield Bubble costs -6% Mana per rank | Aegis Link (max 3): 4% of the dmg taken by shielded allies is redirected to you per rank
  R4: Echo (max 1): Shield Bubble reforms once at 30% strength after breaking | Bastion (max 3): +3% max HP per rank | Hold the Line (max 2): after the bubble breaks, allies who were inside take 4% less dmg per rank for 3s
  R5 [free: Guardian Spirit]: Duration (max 3): Guardian Spirit lasts +1.5s per rank | Power (max 2): Guardian Spirit's protection +5% per rank | Follow (max 1): Guardian Spirit moves to the lowest-HP ally every 3s
  R6 capstone: Undying Vigil: when the ally under Guardian Spirit would die, it prevents the death and grants them a Shield Bubble; Guardian Spirit CD -30%
 Branch 3 Hallowed Ground: zones, group sustain, light utility
  R1: Radius (max 3): healing zones +0.5 blocks per rank | Smite (max 3): holy bolts deal +3% dmg per rank and pierce 1 enemy
  R2 [free: Sanctuary]: Duration (max 3): Sanctuary lasts +1s per rank | Power (max 3): Sanctuary heals +5% more per rank
  R3: Consecrate (max 2): enemies inside Sanctuary deal 4% less dmg per rank | Pilgrim (max 3): allies in your zones gain +3% move speed per rank | Follow (max 1): Sanctuary moves with you at half speed
  R4: Chain (max 1): Sacred Heal on an ally inside Sanctuary also heals everyone else inside for 25% | Sanctified Mana (max 3): allies inside Sanctuary gain +4% Mana regen per rank | Ward (max 2): allies leaving Sanctuary keep a shield worth 3% of max HP per rank
  R5: Efficiency (max 3): Sanctuary costs -8% Mana per rank | Radiant Beacon (max 3): Sanctuary reveals invisible enemies and grants allies +2% crit chance per rank
  R6 capstone: Holy Land: you can keep 2 Sanctuaries active; allies in the overlap receive 150% healing and are immune to knockback

## 4. Skill trees (11)

Same notation. Essentials (Mining, Foraging, Combat, Beastmastery) deepest; useful (Farming, Cooking, Alchemy) full; light skills 2 branches x 4 rows.
Each skill has a gear / accessory / pet scaling upgrade (four power sources). Model-drafted; check that the old node names (Mining Speed, Fortune, Wisdom, Vein Burst ...) survive.

TREE Mining (ESSENTIAL)
 Branch 1 Vein Delver: ore yield
  R1 [free: Prospector's Eye, ore glints through walls within 8 blocks]: Quick Swing (max 5): +2% mining speed/rank | Rich Seams (max 3): +2% double-ore chance/rank
  R2 [free: Vein Burst, active, breaks a connected ore vein of up to 6 blocks, 40s cd]: Wide Burst (max 3): +2 vein size/rank | Burst Recovery (max 3): -3s cd/rank | Chain Fortune (max 2): Burst ores have +3% double-drop chance/rank
  R3: Gem Eye (max 3): +2% gem drop chance/rank | Smelter's Touch (max 1): 10% chance to auto-smelt ore | Steady Pick (max 4): +1% mining speed per 5 ore mined in a row, resets after 10s idle
  R4: Motherlode (max 3): 1% chance/rank for a node to drop x3 | Vein Sense (max 3): Prospector's Eye range +2 blocks/rank
  R5: Seismic Pulse (max 3): Burst also stuns nearby cave mobs for 1s/rank | Overclock (max 5): +2% mining XP/rank | Bottomless Pockets (max 2): +5 ore stack-size bonus/rank
  R6 capstone: Heart of the Mountain: Vein Burst has no cooldown for 8s after mining a rare node (gem or mythic ore).
 Branch 2 Forgehand: tool and gear
  R1: Tool Mastery (max 5): +2% mining speed per tool tier above Stone, per rank | Durable Grip (max 3): -3% tool durability loss/rank
  R2 [free: Stoneskin, passive, -10% fall and cave-in damage while holding a pick]: Rockhide (max 3): +2% damage reduction underground/rank | Echo Step (max 2): +3% move speed in caves/rank
  R3: Gear Resonance (max 5): +1% mining speed per mining-tagged armor piece worn, per rank (max 4 pieces) | Quick Repair (max 3): kills and ore breaks restore 0.5 durability/rank | Emergency Pick (max 1): at 10% durability, +25% speed
  R4: Trinket Seams (max 3): +2% ore yield per filled accessory slot, per rank | Hardened Edge (max 3): +3% damage to rock mobs/rank
  R5: Tool Tempering (max 4): +1 effective tool tier for hardness checks every 2 ranks | Lucky Strike (max 3): 2% chance/rank to refund durability | Blast Hammer (max 2): Burst gains +1 radius/rank
  R6 capstone: Masterwork Pick: your pick gains +25% speed and +10% ore yield, doubled while held tool is the highest tier in your inventory.
 Branch 3 Deepdweller: depth and pets
  R1: Cave Sense (max 3): +3% cave-mob loot/rank | Lantern Lore (max 3): light radius +1 block/rank
  R2 [free: Depth Charge, active, place a charge that clears a 3x3x3 area and drops all blocks, 60s cd]: Bigger Bang (max 3): +1 block radius per 2 ranks | Safe Fuse (max 3): no self-damage at rank 3, -3s cd/rank
  R3: Pet Digger (max 5): +2% mining XP and +1% ore yield per equipped Mining pet level tier, per rank | Deep Bounty (max 3): +2% yield per 20 blocks below sea level (cap 10%) | Cave Stalker (max 2): see cave mobs through walls for 2s/rank after Burst
  R4: Miner's Fortune (max 3): +1% rare-ore chance/rank | Geode Cracker (max 2): geodes give +1 extra roll/rank | Dust Sweep (max 3): auto-pickup radius +2 blocks/rank
  R5: Pet Synergy (max 3): Mining pet ability effects +4%/rank | Abyss Walker (max 3): immune to darkness debuff at rank 1, +3% speed in the dark/rank
  R6 capstone: Core Tap: once per hour, mine a Deep Core that drops 3-5 rare gems and gives your Mining pet 500 XP.

TREE Foraging (ESSENTIAL)
 Branch 1 Woodcutter: speed and yield
  R1 [free: Timber Sense, trees show fell-direction and log count]: Sharp Axe (max 5): +2% chopping speed/rank | Heartwood (max 3): +2% double-log chance/rank
  R2 [free: Timber!, active, fells the entire tree in one swing, 30s cd]: Clean Cut (max 3): +10% saplings from felled trees/rank | Quick Fell (max 3): -3s cd/rank | Giant Reach (max 2): works on trees up to +8 logs/rank
  R3: Bark Collector (max 3): +3% bark/resin drops/rank | Steady Rhythm (max 4): +1% speed per consecutive tree, up to 4 stacks | Replanter (max 1): auto-replant 1 sapling
  R4: Rare Grain (max 3): +1% rare-wood chance/rank | Splinter Shield (max 3): +2% block chance while chopping/rank
  R5: Lumber Surge (max 5): +2% foraging XP/rank | Forest Fortune (max 3): +3% log yield during Timber! cooldown/rank | Echo Fell (max 2): 10% chance/rank for Timber! to reset
  R6 capstone: World Tree's Blessing: felling a rare tree triggers a 20s zone where all gathering is +30% faster and yields +15%.
 Branch 2 Wildkeeper: plants and critters
  R1: Green Thumb (max 3): +3% herb/berry yield/rank | Forager's Pouch (max 3): +4 gathering stack slots/rank
  R2 [free: Pollen Cloud, active, 12s zone, nearby plants regrow 2x faster, 45s cd]: Wide Bloom (max 3): +1 block radius/rank | Lingering Spores (max 3): +2s duration/rank
  R3: Mushroom Hunter (max 3): +4% fungus/rare-herb chance/rank | Beast Trails (max 3): see animal tracks within +5 blocks/rank | Wild Taste (max 2): foraged food gives +5% effect duration/rank
  R4: Pet Companion (max 5): +2% foraging XP and +1% yield per equipped Foraging pet tier, per rank | Camouflage (max 3): -5% mob aggro range in forests/rank
  R5: Seasonal Bounty (max 3): +3% yield for the in-season plant type/rank | Fey Bargain (max 2): 3% chance/rank to find fey items
  R6 capstone: Heart of the Grove: while Pollen Cloud is active, foraging pets gain +50% XP and grant their ability twice.
 Branch 3 Trailblazer: gear and movement
  R1: Light Foot (max 3): +2% move speed in forests/rank | Tool Tier Bonus (max 4): +2% chopping speed per axe tier, per rank
  R2 [free: Grapple Vine, active, quick-travel to nearest tree up to 20 blocks, 15s cd]: Long Vine (max 3): +4 blocks range/rank | Vine Recovery (max 3): -2s cd/rank
  R3: Gear Resonance (max 5): +1% foraging yield per forest-tagged armor piece, per rank | Sturdy Hide (max 3): +2% damage reduction vs. forest mobs/rank | Wind Walker (max 2): +5% fall damage reduction
  R4: Accessory Boughs (max 3): +2% foraging fortune per filled accessory slot, per rank | Hawk Eye (max 3): +4% rare-find notice range/rank
  R5: Hardwood Axe (max 3): axe durability +8%/rank | Vine Swing (max 2): swing-attack while Grappling, +10% dmg/rank
  R6 capstone: Pathfinder's Mantle: Grapple Vine has no cooldown for 5s after felling a tree, and its landing gives a free harvest tick.

TREE Combat (ESSENTIAL)
 Branch 1 Duelist: damage
  R1 [free: Combat Focus, +5% damage after 3 hits within 5s]: Hone Edge (max 5): +2% weapon damage/rank | Weak Spot (max 3): +2% crit chance/rank
  R2 [free: Flurry, active, 4 rapid strikes at +25% damage, 20s cd]: Extra Strike (max 2): +1 strike per 2 ranks | Flurry Recovery (max 3): -2s cd/rank | Rending (max 3): Flurry applies bleed 2%/s/rank
  R3: Finisher (max 3): +4% damage to enemies below 30% health/rank | Momentum (max 4): +1% move speed per consecutive hit, up to 4 stacks | Parry Reflex (max 1): perfect block grants a free Flurry
  R4: Crit Mastery (max 3): +3% crit damage/rank | Gear Resonance (max 3): +2% damage per combat-tagged armor piece/rank
  R5: Trophy Hunter (max 3): +3% damage vs. bosses/rank | Weapon Tempering (max 4): +2% damage per weapon tier above Iron, per rank | Bloodlust (max 2): kills extend Combat Focus by 1s/rank
  R6 capstone: Edge of the Legend: Flurry resets on kill, and its strikes always crit against bleeding targets.
 Branch 2 Bulwark: defense
  R1: Toughness (max 5): +2% max health/rank | Iron Will (max 3): +3% knockback resistance/rank
  R2 [free: Shield Wall, active, 40% damage reduction for 5s, 45s cd]: Longer Wall (max 3): +1s duration/rank | Quick Draw (max 3): -3s cd/rank
  R3: Thick Skin (max 4): +2% damage reduction/rank | Reprisal (max 3): +5% thorns damage/rank | Second Wind (max 1): once per fight, heal 15% at 20% health
  R4: Accessory Plates (max 3): +2% max health per filled accessory slot, per rank | Rally (max 3): +3% regen out of combat/rank
  R5: Bastion (max 3): +3% damage reduction while Shield Wall is active/rank | Ward Pulse (max 2): Shield Wall pushes enemies back 2 blocks/rank
  R6 capstone: Unbreakable: survive a killing blow once per 5 min with 1 HP and 3s of invulnerability.
 Branch 3 Spoils: loot and pets
  R1: Scavenger (max 5): +2% mob drop chance/rank | Coin Purse (max 3): +3% coin drops/rank
  R2 [free: Mark the Prey, active, marked target takes +15% damage and drops +20% loot, 30s cd]: Wide Mark (max 3): +1 target per 2 ranks | Lingering Mark (max 3): +3s duration/rank
  R3: Pet Fang (max 5): +2% combat XP and +1% damage per equipped Combat pet tier, per rank | Rare Drop (max 3): +1% rare drop chance/rank | Salvage (max 2): 5% chance/rank for armor/weapon scrap
  R4: Boss Hunter (max 3): +3% boss loot rolls/rank | Treasure Sense (max 3): see loot beams within +6 blocks/rank
  R5: Lucky Kill (max 3): 2% chance/rank to double a mob's drops | Combat Insight (max 5): +2% combat XP/rank
  R6 capstone: Master Looter: kills while Marked drop a bonus loot roll; the first boss kill each day drops +1 guaranteed rare.

TREE Beastmastery (ESSENTIAL, pet-category branches)
 Branch 1 Bonded Fangs: Combat pets (root)
  R1 [free: Bond of Beasts, +10 flat pet XP per pet-active kill]: Whistle Training (max 5): +2 flat pet XP/rank | Fang Familiar (max 3): +3% Combat pet XP/rank
  R2 [free: Rally Cry, active, call all pets to attack your target for 8s, 40s cd]: Long Rally (max 3): +2s duration/rank | Pack Speed (max 3): +4% pet attack speed/rank
  R3: Battle Bond (max 4): +1% all stats from Combat pets per rank | Pack Instinct (max 3): +2% damage per additional active pet/rank | Guard Dog (max 1): pet absorbs 10% of damage you take
  R4: Alpha's Mark (max 3): +3% pet crit chance/rank | Fang Tempering (max 3): +4% Combat pet XP/rank
  R5: Predator's Gift (max 3): +2% all stats from Combat pets/rank | Rapid Learner (max 3): +2% all-pet XP/rank
  R6 capstone: Apex Bond: Combat pets gain +15% all stats and Rally Cry also heals you for 5% max health per second.
 Branch 2 Deep Burrow: Mining pets
  R1: Digger's Calling (max 5): +3% Mining pet XP/rank | Cave Nose (max 3): +2 ore detection blocks/rank
  R2 [free: Pet Dig, active, pet digs a small cache, 3-5 ore, 90s cd]: Deeper Dig (max 3): +1 ore/rank | Quick Dig (max 3): -5s cd/rank
  R3: Stone Bond (max 4): +1% all stats from Mining pets/rank | Ore Sniffer (max 3): +2% ore yield while a Mining pet is out/rank | Glimmering Coat (max 1): pet glows to light caves
  R4: Gem Hound (max 3): +2% gem chance/rank | Deep Tempering (max 3): +4% Mining pet XP/rank
  R5: Earthen Gift (max 3): +2% all stats from Mining pets/rank | Burrow Rush (max 3): +3% mining speed with Mining pets out/rank
  R6 capstone: Heart of Stone: Mining pets gain +15% all stats; Pet Dig always yields at least one rare gem.
 Branch 3 Wild Roots: Farming and Foraging pets
  R1: Green Companion (max 5): +3% Farming/Foraging pet XP/rank | Gentle Hand (max 3): +3% pet happiness/rank
  R2 [free: Pet Harvest, active, pet harvests nearby ripe crops or logs, 60s cd]: Wide Harvest (max 3): +1 block radius/rank | Quick Harvest (max 3): -4s cd/rank
  R3: Verdant Bond (max 4): +1% all stats from Farming pets/rank | Wild Bond (max 4): +1% all stats from Foraging pets/rank | Pet Picnic (max 1): feeding any pet gives +20% XP for 5 min
  R4: Fertile Trail (max 3): +2% farm and forage yield while a matching pet is out/rank | Roots Tempering (max 3): +4% Farming/Foraging pet XP/rank
  R5: Nature's Gift (max 3): +2% all stats from Farming and Foraging pets/rank | Gentle Giant (max 2): +10% pet bonus from rare pets/rank
  R6 capstone: Kinship of the Wild: equip one extra pet slot; all equipped pets gain +10% all stats (+20% for Farming and Foraging).

TREE Farming (USEFUL)
 Branch 1 Harvester: yield
  R1 [free: Green Eye, ripe crops glow]: Bountiful Rows (max 5): +2% crop yield/rank | Quick Scythe (max 3): +3% harvest speed/rank
  R2 [free: Sweep Harvest, active, harvest a 5x5 area, 20s cd]: Wide Sweep (max 3): +1 radius per 2 ranks | Swift Sweep (max 3): -2s cd/rank
  R3: Double Reap (max 3): +2% double-crop chance/rank | Auto-Seed (max 1): replant crops on harvest | Fertile Soil (max 3): +4% crop growth speed/rank
  R4: Golden Harvest (max 3): +1% golden crop chance/rank | Bumper Crop (max 3): +3% yield for full-field harvests/rank
  R5: Harvest Frenzy (max 5): +2% farming XP/rank | Scythe Tempering (max 3): +2% yield per hoe tier/rank
  R6 capstone: Cornucopia: Sweep Harvest also grants a 25% chance of a free replant and doubles drops of golden crops.
 Branch 2 Rancher: animals and pets
  R1: Animal Friend (max 3): +3% animal product yield/rank | Gentle Touch (max 3): +4% breeding success/rank
  R2 [free: Animal Call, active, lures animals to you for 20s, 40s cd]: Wide Call (max 3): +4 blocks range/rank | Calm Presence (max 2): animals stay calm for +3s/rank
  R3: Pet Farmer (max 5): +2% farming XP and +1% yield per equipped Farming pet tier, per rank | Quality Feed (max 3): +3% rare animal product chance/rank | Twin Birth (max 2): +3% twin offspring/rank
  R4: Barn Aura (max 3): +2% animal product yield per filled accessory slot/rank | Shearing Master (max 3): +4% wool/leather quality/rank
  R5: Golden Egg (max 3): +1% golden egg/milk chance/rank | Beast Whisperer (max 2): +5% pet happiness/rank
  R6 capstone: Prize Herd: animals within your pen produce +30% and one random animal per day yields a rare drop.
 Branch 3 Alchemist's Garden: special crops
  R1: Herb Lore (max 3): +3% herb yield/rank | Pest Control (max 3): +4% crop-loss reduction/rank
  R2 [free: Compost Boost, active, fertilize a 5x5 patch for 2x growth and yield for 60s, 90s cd]: Rich Compost (max 3): +4s duration/rank | Quick Mix (max 3): -5s cd/rank
  R3: Rare Seed (max 3): +2% rare-seed chance/rank | Watering Can (max 3): +4% water efficiency/rank | Gear Resonance (max 3): +2% yield per farming-tagged armor piece/rank
  R4: Hothouse (max 3): +3% crop growth speed indoors/rank | Seed Broker (max 3): +4% seed refund/rank
  R5: Mutation (max 3): +1% mutated-crop chance/rank | Bundling (max 2): +5% stack bonus for crop bundles/rank
  R6 capstone: Eden Patch: your best plot grows 2x faster and yields +20% of all crops grown there.

TREE Cooking (USEFUL)
 Branch 1 Line Cook: buffs
  R1 [free: Taste Test, see buff values of food]: Seasoned (max 5): +3% food buff strength/rank | Long Simmer (max 3): +4% food buff duration/rank
  R2 [free: Flash Fry, active, cook any food instantly, 30s cd]: Hot Pan (max 3): -3s cd/rank | Double Skillet (max 2): +1 item per Flash Fry/rank
  R3: Hearty Meals (max 3): +3% healing from food/rank | Spice Rack (max 3): +2% chance for double buff/rank | Leftovers (max 1): 10% chance to not consume food
  R4: Comfort Food (max 3): +2% max health for 5 min after eating/rank | Chef's Pride (max 3): +4% buff duration per filled accessory slot/rank
  R5: Feast Mode (max 4): +2% cooking XP/rank | Gourmet Touch (max 3): +2% food rarity chance/rank
  R6 capstone: Signature Dish: one chosen recipe gives double effect and shares its buff with nearby allies.
 Branch 2 Pantry: ingredients and yield
  R1: Forager's Larder (max 3): +3% ingredient yield/rank | Fresh Catch (max 3): +3% fish/meat quality/rank
  R2 [free: Pantry Pouch, passive, 12 extra slots for food only]: Deep Pantry (max 3): +4 slots/rank | Preserves (max 3): +5% food shelf life/rank
  R3: Thrifty Cook (max 4): 3% chance/rank to save an ingredient | Pet Sous-Chef (max 5): +1% cooking yield and +2% XP per equipped Farming pet tier, per rank | Spice Trader (max 2): +4% spice drop/rank
  R4: Cauldron Master (max 3): +4% batch size/rank | Master Butcher (max 3): +3% meat yield/rank
  R5: Seasonal Harvest (max 3): +3% buff for in-season food/rank | Bulk Prep (max 2): +1 batch slot/rank
  R6 capstone: Bottomless Larder: once per day, cook a full feast with no ingredients consumed.
 Branch 3 Festival: party food
  R1: Big Batch (max 3): +1 serving per cook/rank | Plate Presentation (max 3): +3% buff strength for shared meals/rank
  R2 [free: Banquet, active, place a table that gives allies a food buff for 3 min, 120s cd]: Long Feast (max 3): +20s duration/rank | Wide Table (max 3): +2 blocks radius/rank
  R3: Sweet Tooth (max 3): +3% buff from desserts/rank | Pet Tasting (max 3): +3% pet XP from fed food/rank | Gear Resonance (max 3): +2% buff strength per cooking-tagged armor piece/rank
  R4: Hospitality (max 3): +3% regen to allies at Banquet/rank | Rare Vintage (max 2): +3% rare drink chance/rank
  R5: Chef's Kiss (max 3): +2% chance for crit-meal (+50% buff)/rank | Lasting Impression (max 3): +4% buff duration after leaving the table/rank
  R6 capstone: Royal Feast: Banquet applies a second random buff and doubles pet XP from food for 5 min.

TREE Alchemy (USEFUL)
 Branch 1 Brewer: potency
  R1 [free: Steady Hand, potions brew 10% faster]: Potent Brew (max 5): +3% potion effect strength/rank | Extended Vial (max 3): +4% potion duration/rank
  R2 [free: Splash Mix, active, convert a held potion into a splash potion, 30s cd]: Wide Splash (max 3): +1 block radius/rank | Quick Mix (max 3): -3s cd/rank
  R3: Double Dose (max 3): +3% chance a potion gives two charges/rank | Clean Distill (max 3): +3% fewer ingredients used/rank | Stable Brew (max 1): potions don't expire early
  R4: Tier Up (max 3): +2% chance to upgrade potion tier/rank | Alembic Resonance (max 3): +2% potency per filled accessory slot/rank
  R5: Master Distiller (max 5): +2% alchemy XP/rank | Catalyst (max 3): +3% effect strength to buffs from rare ingredients/rank
  R6 capstone: Philosopher's Draught: one brewed potion per day becomes a Perfect potion with +50% potency and duration.
 Branch 2 Herbalist: ingredients and gear
  R1: Herb Eye (max 3): +3% herb yield/rank | Mortar & Pestle (max 3): +3% extraction yield/rank
  R2 [free: Quick Gather, passive, harvesting herbs gives a 10% chance for a double yield]: Trained Hands (max 3): +3% double chance/rank | Careful Cut (max 3): +4% rare herb chance/rank
  R3: Pet Herbalist (max 5): +2% alchemy XP and +1% rare herb chance per equipped Foraging pet tier, per rank | Rare Drops (max 3): +2% rare ingredient chance/rank | Dried Herbs (max 2): +5% shelf life/rank
  R4: Alchemy Set Resonance (max 3): +3% brewing speed per alchemy-tagged armor piece/rank | Sensitive Nose (max 3): see rare ingredients within +4 blocks/rank
  R5: Wild Mix (max 3): +3% chance for a free random ingredient/rank | Greenhouse (max 2): +5% herb regrow speed/rank
  R6 capstone: Heart of the Wild Garden: foraged rare herbs count as 2 ingredients and have a 10% chance to be refunded.
 Branch 3 Mutagen: utility and risk
  R1: Resist Tonic (max 3): +3% potion resistance effect/rank | Sip Quick (max 3): +4% potion drink speed/rank
  R2 [free: Mutagen Flask, active, +30% damage and -10% defense for 20s, 60s cd]: Stable Flask (max 3): reduce defense penalty by 3%/rank | Quick Chill (max 3): -4s cd/rank
  R3: Antidote (max 3): +5% debuff resistance/rank | Volatile Vial (max 3): +3% damage from thrown potions/rank | Poison Master (max 2): +4% poison potency/rank
  R4: Potion Belt (max 3): +1 quickslot potion/rank | Overdose (max 3): +4% potion strength under 50% health/rank
  R5: Transmute (max 3): +3% chance to turn a failed brew into a lesser potion/rank | Lingering Cloud (max 3): +2s zone duration/rank
  R6 capstone: Elixir of Becoming: drink a potion to gain all its effects at +25% for 30s, once per 10 min.

TREE Fishing (NICE-TO-HAVE, 2 branches x 4 rows)
 Branch 1 Angler: catch
  R1 [free: Tug Sense, bite indicator]: Sharp Hook (max 4): +3% bite speed/rank | Fish Fortune (max 3): +2% double-catch chance/rank
  R2 [free: Chum Cast, active, lures fish for 30s, 60s cd]: Rich Chum (max 3): +4% rare fish chance/rank | Long Chum (max 3): +5s duration/rank
  R3: Rod Tempering (max 4): +2% catch speed per rod tier/rank | Pet Angler (max 3): +2% fishing XP per equipped Foraging pet tier/rank
  R4 capstone: Legend of the Deep: Chum Cast also draws one treasure or boss fish per cast.
 Branch 2 Mariner: sea utility
  R1: Sea Legs (max 3): +4% swim speed/rank | Waterproof (max 3): +2 breath seconds/rank
  R2 [free: Tide Call, passive, calm water around your boat]: Calm Waters (max 3): +3% boat speed/rank | Hook Line (max 2): +3% line strength/rank
  R3: Salvage Hook (max 3): +2% chance to reel in sunken loot/rank | Gear Resonance (max 3): +2% fishing luck per fishing-tagged armor piece/rank
  R4 capstone: Kraken's Favor: once per day, reel in a Sunken Chest with guaranteed rare loot.

TREE Exploration (NICE-TO-HAVE, 2 branches x 4 rows)
 Branch 1 Pathfinder: discovery
  R1 [free: Map Sense, reveals nearby points of interest on the map]: Wanderer (max 5): +2% exploration XP/rank | Trail Mix (max 3): +3% sprint stamina/rank
  R2 [free: Scout Pulse, active, reveals structures within 60 blocks for 10s, 90s cd]: Far Sight (max 3): +10 blocks range/rank | Quick Scout (max 3): -5s cd/rank
  R3: Cartographer (max 3): +3% map-discovery XP/rank | Chest Finder (max 3): +2% chest loot quality/rank | Pet Scout (max 3): +2% discovery radius per equipped pet tier/rank
  R4 capstone: Worldwalker: discovering a new biome grants a one-time chest and +10% move speed for 5 min.
 Branch 2 Wayfarer: travel
  R1: Light Packer (max 3): +4% carry weight/rank | Camp Craft (max 3): +4% rest regen/rank
  R2 [free: Waystone Recall, active, teleport to your last waystone, 10-minute cd]: Faster Recall (max 3): -45s cd/rank | Safe Landing (max 2): -10% fall damage/rank
  R3: Accessory Compass (max 3): +2% move speed per filled accessory slot/rank | Weatherproof (max 3): +4% weather resistance/rank
  R4 capstone: Wind at Your Back: sprinting for 10s grants +20% move speed for 15s.

TREE Acrobatics (NICE-TO-HAVE, 2 branches x 4 rows)
 Branch 1 Tumbler: mobility
  R1 [free: Roll, active, dodge-roll with brief i-frames, 8s cd]: Quick Roll (max 3): -1s cd/rank | Long Leap (max 3): +4% jump height/rank
  R2 [free: Wall Grip, passive, slow slide on walls]: Strong Grip (max 3): +10% wall slide time/rank | Chain Jump (max 2): +1 midair jump per 2 ranks
  R3: Light Feet (max 4): -5% fall damage/rank | Combat Flip (max 3): +3% dodge chance/rank | Gear Resonance (max 3): +2% agility per light armor piece/rank
  R4 capstone: Phantom Step: Roll leaves a decoy and resets on a perfect dodge.
 Branch 2 Daredevil: risk and reward
  R1: Adrenaline (max 3): +3% speed at low health/rank | Close Call (max 3): +4% damage after a dodge/rank
  R2 [free: Parkour Rush, passive, +10% speed after 3 consecutive jumps]: Rush Time (max 3): +1s duration/rank | Steady Land (max 3): -4% landing slowdown/rank
  R3: Accessory Sprint (max 3): +2% stamina per filled accessory slot/rank | Evade Master (max 3): +2% dodge chance while sprinting/rank | Fearless (max 2): -5% fall damage taken at low health/rank
  R4 capstone: Cat's Nine Lives: once per hour, a lethal fall leaves you at 1 HP and grants 5s of speed.

TREE Smithing (NICE-TO-HAVE, 2 branches x 4 rows)
 Branch 1 Forgemaster: crafting
  R1 [free: Hammer Time, smithing crafts 10% faster]: Steady Strikes (max 4): +3% craft speed/rank | Thrift (max 3): +3% chance to save materials/rank
  R2 [free: Quench, active, instant-finish an item, 90s cd]: Quick Quench (max 3): -8s cd/rank | Perfect Quench (max 3): +4% chance for a bonus stat/rank
  R3: Gear Resonance (max 3): +2% item quality per smithing-tagged armor piece/rank | Tool Lore (max 3): +3% tool durability crafted/rank | Masterwork (max 3): +2% chance for a +1 upgrade/rank
  R4 capstone: Legendary Forge: once per day, craft an item with +1 tier of quality.
 Branch 2 Tinkerer: repair and upgrade
  R1: Quick Repair (max 4): +4% repair speed/rank | Salvager (max 3): +3% scrap recovery/rank
  R2 [free: Field Repair, active, repair held item by 20% anywhere, 120s cd]: Better Repair (max 3): +4% repair per use/rank | Quick Kit (max 3): -8s cd/rank
  R3: Accessory Anvil (max 3): +2% enchant strength per filled accessory slot/rank | Pet Hammer (max 3): +2% smithing XP per equipped Mining pet tier/rank | Reinforce (max 3): +3% item durability on repair/rank
  R4 capstone: Eternal Edge: once per day, fully repair and give an item 10 minutes of unbreakable status.

Notes: row gates are 0/5/10/15/20/25 for full trees and 0/5/10/15 for the 4-row trees. The Mining node names you mentioned were removed from the file, so these are new designs and may not match existing names. Beastmastery uses 3 branches, with Farming and Foraging pets sharing Branch 3.
## 5. Dust removal

**What Dust does today** (Skill-Trees-Spec 3.2, Skill-Trees-2-Spec 2): per tree, `dust = floor(total skill XP / xpPerDust)` (10; Mining 5, Acrobatics 2,
Exploration 5; computed, never stored), spent on node levels 2+; Tokens (`1 + floor(level/5)`) buy the node first. Class trees spend AP (`1 + level/2`,
max 50). Rebirth-Spec 3.4 adds a 2x Dust multiplier per rebirth and a Dust node per arm. All of that goes: Tokens, Dust, `dust.perTree`,
`debug.extraDust`, the Dust node in the rebirth arms, and the Dust label on the tree pages.

**One-time conversion** (PROJECT-RULES 4 "one-time setting migrations"; only SkyyTrees saved data changes, `Skyy_SkyyTrees/players/<pkey>.properties`):
1. Verified History snapshot of every player file first; a change-log line with Undo; run-once marker `treesV3=1`; keep the file's bytes and line endings.
2. Every old node level is cleared. All new points are granted from level (1 per level), so nobody loses anything - they gain points up to their level
   (old Mining at level 40 had 9 tokens + millions of Dust; now it has 40 points, spent fresh).
3. Refund: **points only, no coins** (Dust at level 50 is ~5.5M; converting to coins would break the economy - Q3). Optionally, a one-time "Void Dust Relic"
   cosmetic title for players who spent more than 1M Dust (decorative, no stats) - skip by default.
4. Nobody loses an ability they owned: the migration auto-buys the cheapest branch path to each owned class ability (Row 2 = 5 points in that branch;
   Row 5 = 20) and marks it "grandfathered" if the player lacks the points (stays owned and equipped until their first respec). Skill perks likewise.
5. Hand-edited values (a server owner changed `dust.perTree`) are kept in a log line, then the setting becomes unused.

## 6. Rebirth Void Particles (VP)

Replaces the per-arm rebirth points (Rebirth-Spec 3.5) with ONE currency, per profile. It is spent at the Nexus of the Void (the radiating tree);
unspent VP also gives an overall XP buff.

### 6.1 Earn
`VP(n) = 20 + 10 x n + 2 x (skills at or past their cap, max 11) + overflow`, n = the rebirth number (1-10).
overflow = `floor(12 x (sqrt(min(r, 16)) - 1))` for the class, r = class XP this run / XP to cap (XP past max counts, same sqrt curve as Rebirth-Spec 3.5; r=1 -> 0, r=4 -> +12, r=16 -> +36).
Typical: rebirth 1 ~38, 2 ~50, 3 ~60, 4 ~70, 5 ~80 (all skills maxed ~ +22 each time).

### 6.2 Spend (Nexus arms; costs are per rank, 5 ranks per arm)
| Arm | Effect per rank | Ladder cost (VP) |
|---|---|---|
| Void Insight | +2% XP to everything | 12, 20, 32, 48, 72 (184) |
| Class Echo | +3% class XP | 4, 6, 10, 16, 24 (60) |
| Mining / Foraging / Combat / Beastmastery Echo | +3% that skill's XP (4 arms) | 4, 6, 10, 16, 24 each (60) |
| Hand Echo (Farming, Cooking, Alchemy, Fishing, Smithing, Acrobatics) | +3% XP to one chosen skill per rank | 4, 6, 10, 16, 24 |
| Head Start | begin each run with +1 skill point per rank (skills + class) | 20, 30, 45 (3 ranks) |
| Tool Rebirth modifiers | pickaxe / axe / hoe / rod modifiers (Rebirth-Ideas) | per Rebirth-Spec 2.3, now paid in VP |

"Skill XP boost" is the main use (Skyy). Costs rise fast so the cheap early ranks are great and the last ranks are a real choice against keeping.

### 6.3 Keep (the buff)
Unspent VP held `h`: **XP bonus = 30% x h / (h + 120)** on all XP gained (class, skills, Beastmastery). Diminishing: 50 VP held = +8.8%, 120 = +15%,
300 = +21.4%, cap +30%. Marginal rate falls from 0.25%/VP at h=0 to 0.06%/VP at h=120.
Compare: the upgrade ladders pay 0.2-0.6% of the relevant XP per VP at first, but the last ranks pay under 0.1%, so late ranks lose to keeping.
Spent VP is gone for good (no refund), unless a Nexus respec (cost: a Void Charm or coins - Q7).

### 6.4 Spend vs keep, worked (python-checked, tools/dev/scratch/st3 - model: a focused player buys the best-value ranks of Class Echo + 2 skill Echoes + Void Insight; arm bonuses weighted 50% of overall XP since they boost only one stream)
| After rebirth | VP earned total | Best split (spend / keep) | XP bonus: spend + keep | All keep | Target* |
|---|---|---|---|---|---|
| 1 | 38 | 30 / 8 | +9.0 + 1.9 = **10.9%** | 7.2% | 9% |
| 2 | 88 | 52 / 36 | +12.5 + 6.9 = **19.4%** | 12.7% | 19% |
| 3 | 148 | 72 / 76 | +15.5 + 11.6 = **27.1%** | 16.6% | 31% |
| 4 | 218 | 140 / 78 | +22.0 + 11.8 = **33.8%** | 19.3% | 46% |
| 5 | 298 | 188 / 110 | +25.0 + 14.3% = **39.3%** | 21.4% | - |

*Target = half of the speed-up needed for "each rebirth 15% shorter" (run 2 38 h, run 3 32 h, run 4 28 h, run 5 24 h vs 45 h). Needed speed-up
vs run 1: +18%, +38%, +63%, +92%. VP covers about half (9 / 19 / 31 / 46%); the rest comes from what rebirth already keeps (island, shards, gear
tiers, route knowledge, +3% all stats per rebirth). Runs 4-5 fall short of the target by 8-12 points: raise the ladder strength a bit, or add
another small XP source; flagged as Q8. Lazy play (all keep) still gives 7-21%, so skipping the Nexus never hurts badly.
Caveat: run 2+ also raises the cap (+10 levels), so XP needed grows; the balance pass must scale XP curves with the cap.

### 6.5 Fit to the Nexus of the Void
The radiating tree (Rebirth-Ideas.md / Rebirth-Spec 2.3) keeps its look: black hole centre, arms = Class, Mining, Foraging, Combat, Beastmastery, Hand Echo
(plus the tool rebirth modifiers on their arms), Void Insight and Head Start close to the Nexus. One VP counter at the top, the "kept" buff shown beside it
("Holding 76 VP: +11.6% XP"). Hover a node: cost, what it gives, and what keeping that VP would give instead (the dilemma shown). VP arms are plain ranked ladders (no row gating), to keep the Nexus simple.

## 7. Build plan (starts after the weekly reset, 2026-10-20)

Mods touched: SkyyTrees (tree engine, pages, migration), SkyySkills (levels -> points bridge; remove Tokens / Dust fns), SkyyClasses (read the
new nodes, ability grants via rows), SkyyRebirth (VP, Nexus arms, keep buff, XP multiplier hook), SkyyMenu (Server Setup rows: respec cost,
VP earn / ladders; remove dust rows). Others that read nodes (Skill-Trees-2 section 12: SkyyCollections, SkyyGear, SkyyFishing/Cooking/Exploration) get a node-id
bridge update. Config through skycfg per CONFIG-CONTRACT.

| Round | Contents | Size |
|---|---|---|
| R0 | Balance data table: one new data file trees_v3_data.py in tools with all 19 trees (this spec's section 3-4, after Skyy's answers) | docs, no agents |
| R1 | SkyyTrees engine: branch gating, ranks, row grants, respec, point counts; **replace** old node tables (classes first: they have the 5 abilities) | Full |
| R2 | Migration (section 5) + Dust / Token removal in SkyyTrees + SkyySkills + Menu rows; smoke on a scratch copy | Full (saved data) |
| R3 | 11 skill trees: perks + upgrades hooked to the existing hook codes (DMG, DD, XP, EXTRA, BREAK ...) one skill per commit; Beastmastery last (needs pet XP) | Full, split |
| R4 | SkyyRebirth VP + Nexus arms + keep buff + migration (Rebirth-Spec 3.5 points replaced); rebirth stays OFF until tested | Full |
| R5 | Balance pass over numbers, Class Balance Workbench refresh (memory: republish when class/skill numbers change) | Lean |
Saved data: SkyyTrees `players/<pkey>.properties` (new `v=3`, `Class.<C>.b<n>.<id>=rank`, `Skill.<S>...`, `treesV3`), SkyyRebirth `vp=<int>`, `nexus.<id>=rank`. Version steps:
SkyyTrees 0.4.0, SkyySkills 0.4.53 (already patching), SkyyClasses 0.1.40, SkyyRebirth 0.4.0, SkyyMenu 0.3.41. Respect rollback floors (deploy_set.py) - after v3 no rollback below the new floor.
Order matters: R1+R2 deploy together (no half state), R4 after R1-R3 are tested by Skyy.

## 8. Questions for Skyy (default in [brackets])

1. Row gate: points in the SAME branch (BL2 style, 0/5/10/15/20/25) or total points in the tree (BL3 style, lets you dip)? [same branch]
2. Points per level: 1 per level for class and every skill (100 at rebirth 5, tree capacity ~130)? [yes]
3. Dust refund: points only (everyone gets full points for their level), no coins? [points only; nothing converted to coins]
4. Capstone cost: 3 points (rank 1), after 25 in that branch? [yes]
5. Respec price `100 x level x n` (max x5) plus one free per rebirth? [yes]
6. Light skills (Fishing, Exploration, Acrobatics, Smithing): 2 branches x 4 rows? [yes]
7. Spent Void Particles: permanent, or a respec at the Nexus (cost: a Void Charm)? [permanent; respec costs 1 Void Charm]
8. Void Particle strength: current ladder falls 8-12 points short of the "15% shorter per rebirth" goal for rebirths 4-5; raise the ranks to +4% (Echoes) and +3% (Insight)? [yes]
9. Keep buff: +30% x h/(h+120) (cap +30%) on ALL XP? [yes]
10. Replace the 8-arm per-skill rebirth points with the one VP currency (Hand Echo covers the minor skills)? [yes]

## Skyy's answers (2026-10-18, popups; docs/answered/skills.md) - these WIN over the defaults above
1 total points in the tree (BL3) | 2 one point per level | 3 full points + a coin refund for leftover dust | 4 capstone 1 point after 25 | 5 rising coin respec + 1 free per rebirth | 6 light skills 2 x 4 | 7 VP respec costs a Void Charm | 8 stronger XP ranks (~15% shorter each rebirth) | 9 keep buff flat +0.25% per unspent VP, no cap (re-run the spend-vs-keep math) | 10 one shared VP currency
