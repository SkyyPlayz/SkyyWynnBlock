# Class ability drafts (Archer, Warrior, Mage, Berserker, Priest)

Cloud draft, 2026-10-03. Paper design; nothing built. The engine side is Hytale 0.7's **rune system** (`research/Hytale-Runes-Research.md`, VERIFIED there from the pre-release jar):
ability runestones (Primary) + modifier runestones (Support), **2 ability lines per player, 2 modifier slots each**, cast with "Use Ability 2 / 3", cost Mana, have cooldowns, need a weapon in hand.
Wynncraft side (spell names, archetypes) comes from web search snippets, because the wiki pages could not be fetched here. Everything about balance numbers is a placeholder.

## 0. Wynncraft model (what we borrow)

| Class | Wynncraft spells | Archetypes | Source |
|---|---|---|---|
| Archer | Arrow Storm, Escape, Arrow Bomb, Arrow Shield | Boltslinger, Sharpshooter, Trapper | search snippet, [Wynncraft wiki Archer](https://wynncraft.wiki.gg/wiki/Archer) |
| Warrior | Bash, Charge, Uppercut, War Scream | Fallen, Battle Monk, Paladin | [Warrior](https://wynncraft.wiki.gg/wiki/Warrior) |
| Mage | Heal, Teleport, Meteor, Ice Snake | Riftwalker, Light Bender, Arcanist | [Class](https://wynncraft.wiki.gg/wiki/Class) |
| Assassin | Spin Attack, Dash, Multihit, Smoke Bomb | Shadestepper, Trickster, Acrobat | [Assassin](https://wynncraft.wiki.gg/wiki/Assassin) |
| Shaman | Totem, Haul, Aura, Uproot | Summoner, Ritualist, Acolyte | [Shaman](https://wynncraft.wiki.gg/wiki/Shaman) |
| Tree size | 70+ upgrade nodes per class (Ability Points) | | [Ability Tree](https://wynncraft.wiki.gg/wiki/Ability_Tree) |

Our rules already locked: **Class Level spends into the ability tree** (not the weapon skill); ~25 nodes per class in v1 (Decisions row 6.3, still open); no click-combos; gear = who you are, runes = what your spells do;
the five engine elements (Fire, Water, Earth, Wind, Lightning) match Wynn's five (Fire, Water, Earth, Air, Thunder).

## 1. How it works (engine fit, proposal)

| Piece | Design |
|---|---|
| Slots | Wynn has 4 spells; the engine gives **2 active lines + the weapon's Signature (Ability 1)**. So each class has **4 spells** in its tree, the player **slots 2** (a "build" choice) and swaps at the Runebinder's Lattice / a Runes button in SkyyMenu |
| Ability runestone | one per spell, tagged `class.<name>`, `Weapons` = the class's weapon families (Archer: Bow, Crossbow; Warrior: Sword, Longsword, Spear; Mage: Staff, Magic; Berserker: Axe, Battleaxe, Mace, Club; Priest: Wand, Spellbook) |
| Modifier runestones | the tree gives them: each spell has 2 class modifiers (`AppliesTo: ["class.<name>"]`) |
| Tree unlock | spending Class Level points unlocks (a) the spell rune item, (b) modifier runes, (c) passives (stat nodes through our own systems). SkyyClasses checks slotted runes against the tree |
| Mana | spells cost Mana. Vanilla 0.7 Mana is 100 with vanilla runes at 10-50; SkyySkills now posts class base Mana (Mage/Priest 30). **Open (for Skyy, from the runes report):** keep our small base and price class spells 2-12, or move base to the vanilla scale. Costs below are written on the **vanilla 100 scale** so either choice scales by one number (`mana.scale`) |
| Damage | spell damage = a coefficient x the **level damage** D(L) (the gear spec's per-level base) plus Magical Power for spells / Strength for melee; elements use the engine damage causes, so SkyyGear's element damage % and defence apply |
| Cooldowns | per spell, 6-30 s; shorter with a modifier |
| Class XP | spell kills pay the class weapon skill XP (class kill rule); heals pay Divinity XP (the live bridge) |

Placeholder damage coefficients are "x D(L)" where D(L) is the average weapon hit at that level (Gear-Levels-Wynn-Spec). Rough target: a spell used on cooldown adds about 20-35% to a class's damage output, never doubling it.

## 2. Archer (Bow, Crossbow) - weapon skill Archery

| # | Spell | Element | Engine building block | Cost / CD (vanilla scale) | Effect |
|---|---|---|---|---|---|
| 1 | **Arrow Storm** | Wind | Wind Strike / Charged Shot (projectile volley) | 20 / 10 s | Fires 6 arrows in a fan; each x0.5 D |
| 2 | **Escape** | - | Chain Hook (reversed) + effect | 15 / 8 s | Back-flip away 8 blocks + 2 s speed boost; breaks a root |
| 3 | **Arrow Bomb** | Fire | Fireball | 25 / 12 s | One explosive arrow, AoE radius 3, x2.2 D |
| 4 | **Arrow Shield** | - | buff + effect | 20 / 18 s | 4 orbiting arrows absorb the next 4 hits (each blocks one hit), 8 s |

Modifiers (class): *Fork Volley* (Arrow Storm +2 arrows), *Long Flight* (Escape +3 blocks), *Cluster* (Arrow Bomb splits 3 mini bombs), *Thorned Guard* (Arrow Shield returns arrows).

Archetypes (tree branches, about 3 nodes each, Wynn-style):
| Branch | Idea | Nodes (examples) |
|---|---|---|
| **Boltslinger** | Crit and speed | +Crit Chance, "Rapid Draw" (+8% attack speed), "Overcrit window" (after a crit, next arrow +20%) |
| **Sharpshooter** | Long range, focus | "Focus" (consecutive hits +3% each, up to 5), "Far Sight" (+damage at range), Arrow Storm becomes one piercing shot |
| **Trapper** | Traps and control | Arrow Bomb leaves a Trap (damage over time), "Pull" (arrows pull enemies into the trap), "Mana Trap" (a trap restores Mana) |
Archer already has the Crossbows-stay-loaded perk (Archery 5); the big-arrow meter stays the Signature.

## 3. Warrior (Sword, Longsword, Spear) - Swordsmanship

| # | Spell | Element | Block | Cost / CD | Effect |
|---|---|---|---|---|---|
| 1 | **Bash** | Earth | Ground Slam | 30 / 18 s | Slams the ground: wave x1.2 D, spike x2.5 D + launch up |
| 2 | **Charge** | - | dash + AoE | 20 / 10 s | Dash 10 blocks forward, hit all enemies in the path x1.4 D; ends with a shield bash |
| 3 | **Uppercut** | - | launch + follow-up | 25 / 12 s | Launch the target skyward; a second press (3 s) pulls you up for an aerial strike |
| 4 | **War Scream** | - | Enrage-style buff | 25 / 20 s | AoE buff for you and party within 6 blocks: +15% damage, +20% Defence, 8 s; taunts nearby enemies |

Modifiers: *Tremor* (Bash AoE x2), *Unstoppable* (Charge ignores knockback), *Skybreaker* (Uppercut chains 2 targets), *Battle Hymn* (War Scream +3 s).
| Branch | Idea | Nodes |
|---|---|---|
| **Fallen** | Gets stronger as you hurt | "Berserk Heart" (+damage below 50% Health), "Rage Reaction" (a hit taken charges Bash), "Last Stand" (survive at 1 Health once per fight) |
| **Battle Monk** | Fast, holy, close combat | "Flurry" (+attack speed), "Radiant Strike" (every 4th hit heals you), "Sacred Dash" (Charge heals allies it passes) |
| **Paladin** | Tank and support | "Bulwark" (+Defence), "Guardian's Shield" (Wood Shield block reduces more), "Rally" (War Scream also heals) |
Warrior keeps its kit: Crude sword + Wood Shield (live in 0.1.10).

## 4. Mage (Staff, Magic) - Sorcery

| # | Spell | Element | Block | Cost / CD | Effect |
|---|---|---|---|---|---|
| 1 | **Heal** | - | self heal effect | 25 / 12 s | Restores 25% max Health over 2 s to you and 8% to allies nearby (Priest does much more) |
| 2 | **Teleport** | - | blink | 20 / 8 s | Blink 12 blocks along your aim, clears fall damage |
| 3 | **Meteor** | Fire | Fireball (delayed) | 35 / 20 s | After 1.2 s a meteor hits the target area: AoE radius 4, x3.0 D |
| 4 | **Ice Snake** | Water | Charged Shot | 25 / 12 s | Frost projectile that follows the ground; x1.6 D + chill; 2 s freeze at the end |

Modifiers: *Warm Hands* (Heal +10%), *Far Step* (Teleport +4 blocks), *Fallen Star* (Meteor drops 3 smaller ones), *Deep Freeze* (Ice Snake splits into 2).
| Branch | Idea | Nodes |
|---|---|---|
| **Arcanist** | Raw spell power | +Magical Power, "Overcharge" (a spell used at full Mana +15%), "Mana Siphon" (kills give Mana) |
| **Riftwalker** | Teleport and chaining | "Blink Slash" (Teleport damages those it passes), "Rift Echo" (a second Teleport free within 2 s), "Meteor from the Rift" (teleport into a Meteor target) |
| **Light Bender** | Light, healing and range | "Prism" (Ice Snake splits to lasers), "Heal Beam" (Heal chains to 3 allies), "Brilliance" (cooldown -10%) |
Mage uses the live base Mana and the Mana regen rules (50% in combat, `/skills mana`).

## 5. Berserker (Axe, Battleaxe, Mace, Club) - Fury

| # | Spell | Element | Block | Cost / CD | Effect |
|---|---|---|---|---|---|
| 1 | **Enrage** (vanilla rune) | - | Enrage | 20 / 16 s | 10 s: +30% damage dealt, +20% damage taken (vanilla numbers) |
| 2 | **Ground Slam** (vanilla rune) | Earth | Ground Slam | 30 / 18 s | Wave 15 Earth, stone spike 35 Earth + launch (vanilla numbers) |
| 3 | **Hook And Crush** | - | Chain Hook | 15 / 6 s | Chain pulls the target to you; your next swing within 2 s x1.5 |
| 4 | **Whirlwind** | - | spin AoE | 25 / 12 s | Spin 2 s, hit all around x0.4 D per half second; you take slightly less knockback |

Modifiers: *Bloodlust* (Enrage +5 s), *Aftershock* (Ground Slam x2 AoE; vanilla Expansion), *Long Chain* (Hook range +4), *Cyclone* (Whirlwind lasts +1 s).
Branches (Fury): **Bloodbound** (damage when hurt, life steal), **Smasher** (Ground Slam / stun synergy), **Warbringer** (buff your party).
Reuse of vanilla runes keeps the build cheap (they exist as engine assets).

## 6. Priest (Wand, Spellbook) - Divinity (healing support; Divinity XP from heals is live)

| # | Spell | Element | Block | Cost / CD | Effect |
|---|---|---|---|---|---|
| 1 | **Mend** | - | AoE heal effect | 20 / 8 s | Heals everyone in 5 blocks: 20% of the Priest's Magical Power-scaled amount (self 100% per the 0.1.10 lock) |
| 2 | **Sanctuary** | - | AoE zone entity | 30 / 20 s | A glowing circle for 8 s: heals allies in it each second; enemies inside are slowed |
| 3 | **Smite** | Light (use Fire/Wind placeholder) | Fireball-like | 20 / 10 s | A holy bolt x1.8 D; heals the lowest ally by 20% of the damage |
| 4 | **Blessing** | - | buff | 25 / 18 s | Party buff: +10% Health regen and +10% resist for 12 s |

Modifiers: *Wide Mend* (Mend radius +3), *Lingering Light* (Sanctuary +4 s), *Holy Wrath* (Smite +30% vs undead), *Prolonged Grace* (Blessing +6 s).
Branches: **Healer** (stronger heals, revive the downed), **Smiter** (damage focus), **Guardian** (shields and protection).
Heal XP: every heal the Priest does goes through the live bridge `skill:fn:healxp` (1 XP/HP on others, 1.25 on self, capped at 900 a minute).
(Light as an element does not exist in the five engine elements; use a Light dragon-only element later or Wind/Fire placeholder - open question below.)

## 7. Assassin and Shaman (later, stubs)

| Class | Spells (borrow names) | Notes |
|---|---|---|
| Assassin (Daggers, Kunai) | Spin Attack, Dash, Multihit (Backstab), Smoke Bomb | Archetypes Shadestepper / Trickster / Acrobat |
| Shaman | Totem, Haul, Aura, Uproot | Archetypes Summoner / Ritualist / Acolyte; the Shaman skill slot already exists as a placeholder |

## 8. Tree shape (v1: about 25 nodes per class)

| Node type | Count | Example |
|---|---|---|
| Spell unlock (rune) | 4 | Arrow Storm, Escape, Arrow Bomb, Arrow Shield |
| Spell modifier (rune) | 8 | the 8 listed per class |
| Archetype passives | 9 (3 per branch) | Boltslinger nodes |
| Capstone | 4 (one per archetype x ...) -> use 3 + 1 shared | a final upgrade per branch + one shared |
| Total | about 25 | matches Decisions 6.3 default |

Costs: Class Level points; early nodes 1 point, capstones 3 points. A player cannot afford every branch - the build choice is the Wynn feeling.
Respec: free to swap slotted spells; node refunds cost coins (a coin sink; setting).

## 9. For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | All rune behaviour is from the 0.7 pre-release report; the live game is 0.6.8 without runes. Nothing can be built until 0.7 ships; confirm the rune system is unchanged then. |
| 2 | Can the engine heal (Mend / Heal / Sanctuary) allies? The report says one new heal composition (Selector AOECircle + ApplyEffect) is "INFERRED doable in JSON". Verify in game. |
| 3 | Are 2 ability lines really the cap? (Report section 0.) If so, spell loadout swap is essential. |
| 4 | Can ability damage credit the class weapon skill for XP (report check 10)? |
| 5 | Which engine effects exist for knockback immunity, taunt, dash, blink, orbiting shield (probably need `SpawnAbilityEntity` + custom JSON). |
| 6 | Base Mana scale decision (section 1) is open: Skyy's call. |
| 7 | Light element: not in the engine list; choose a placeholder or add a custom damage cause. |

## 10. Questions for Skyy

1. Keep Wynn's names (Bash, Charge, Heal, Meteor...) or give our own silly names (to match the lore voice)? Recommended: keep Wynn names for the first four per class for familiarity, add our own names later.
2. Mana scale: keep our small base Mana and cheap spells (2-12), or move to Hytale's 100 scale? Recommended: the vanilla 100 scale so vanilla runes still work.
3. Is "4 spells, slot 2" the right build choice, or do you want the tree to give 2 fixed spells per class?
4. Light element for the Priest: placeholder Fire/Wind, a new damage cause, or just "no element"?
