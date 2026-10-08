# Class tree paths - Wynncraft-style locked paths for the 7 classes

Cloud draft, 2026-10-06. Locks (docs/answered/classes.md, 2026-10-04): the **class tree** sells upgrades that **change how an ability works** (not just buff it); they are **paths**: choosing a path **locks out the other two**; the example is the Priest's Shield Bubble
(a node makes it damage enemies that touch or hit it, then pick **1 of 5 elements**); **Cleanse is a Sacred Heal upgrade** in the class tree. **Modifiers live in the ability tree, not here** (`Modifier-Pool-Spec.md`).
Path names come from the "tree path ideas" at the bottom of each class file. Numbers are placeholders; every node has a **trade-off** (that is what keeps it a sidegrade).

## 0. Shape of every class tree

| Part | Rule |
|---|---|
| **Trunk** (shared, 6 nodes) | class-wide upgrades every path gets: weapon / traversal / survival basics. Not locked |
| **3 paths x 5 nodes** | pick **one path** at its first node (**N1**); the other two lock; nodes in a path are taken in order |
| Points | **1 class-tree point per 3 class-skill levels** (33 by Lv 99); costs below; a full tree (trunk + one path) costs **25 points**, reached at class level 75 (8 spare for respec or a later extra node) |
| Level gates | Trunk: Lv 5 / 10 / 15 / 25 / 40 / 55 (cost 1 / 1 / 2 / 2 / 2 / 3) (updated 2026-10-06: Archer T6 Holster Reload is Lv 75; other classes' T6 stay at 55). Path nodes: Lv **20 / 30 / 45 / 65 / 75** (cost 2 / 2 / 3 / 3 / 4). Check: points available at a gate always cover the cumulative cost (script-checked) |
| Respec | swapping paths costs coins (a sink; row `tree.respecCoins`) and refunds all path points; trunk stays |
| Balance | one **power ledger slot** of about +20% (Class-Ability-Spec-Draft section 4); a node that adds a behaviour also carries a downside (listed) |
The five elements for elemental nodes = the engine's **Fire, Water, Earth, Wind, Lightning** (the same five as SkyyGear's element damage).

## 1. 🛡️ Warrior

**Trunk**
| Node | Lv | Pts | Effect |
|---|---|---|---|
| T1 Shield Training | 5 | 1 | Shield Shockwave stun +0.25 s; blocking costs 15% less Stamina |
| T2 Fortitude | 10 | 1 | +8% max Health |
| T3 Longer Thrust | 15 | 2 | the sword's Thrust dash goes 20% farther and costs 10% less Stamina |
| T4 Second Wind | 25 | 2 | once per 60 s, below 30% Health you heal 15% |
| T5 Tempered Steel | 40 | 2 | +5% damage with swords and spears |
| T6 Veteran | 55 | 3 | all Warrior ability cooldowns -5% |

**Path A - Guardian** (party protection)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| G1 Shield Wall | 20 | 2 | Rallying Guard | party radius +2 blocks; allies inside **cannot be knocked back** | your own damage reduction -4 points |
| G2 Interpose | 30 | 2 | Rallying Guard | while active, allies standing **behind you** take 25% less damage from the front | you move 10% slower while active |
| G3 Guardian's Oath | 45 | 3 | A1 / passive | when an ally within 8 blocks drops below 25% Health, you **intercept 30% of the damage** they would take for 3 s (once per 45 s) | you cannot be healed above 80% during it |
| G4 Bastion | 65 | 3 | Bulwark Stance | the stance becomes a **stationary 5-block shield wall** for 8 s (replaces the moving stance) | no movement while it holds; front-only |
| G5 Aegis Core | 75 | 4 | Rallying Guard | +3 s duration and heals the party **3% max Health per second** while active | your damage dealt -15% while active |

**Path B - Warlord** (taunt + counter damage)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| W1 Thorns of Command | 20 | 2 | Rallying Guard | enemies that hit you take **15% of the hit back** while it is active | you take +5% damage during it |
| W2 Battle Cry | 30 | 2 | Rallying Guard | ends with a **shockwave** (1.0 H) on all taunted enemies | cooldown +3 s |
| W3 Barbed Chain | 45 | 3 | Iron Chain | dragged enemies take **25% of the damage dealt to you** for 5 s | chain range -3 blocks |
| W4 Retribution | 65 | 3 | Shield Shockwave | after taking 20% max Health in 5 s, your next Shockwave is **free and stuns twice as long** | only usable once per 20 s |
| W5 Presence | 75 | 4 | Rallying Guard | taunt range +4; taunted mobs deal **-20% damage to everyone else** | you take +10% damage from taunted mobs |

**Path C - Juggernaut** (self sustain)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| J1 Stalwart | 20 | 2 | passive | each blocked hit heals **2% max Health** (max 4 times per 10 s) | -3% move speed |
| J2 Last Stand | 30 | 2 | Unbreakable | end heal +15 points | the 1 HP window is 1 s shorter |
| J3 Plate Mastery | 45 | 3 | passive | full **Plate** armor (the Heavy type): Defence x1.15 | -5% move speed |
| J4 Shockwave Surge | 65 | 3 | Shield Shockwave | heals you **3% max Health per enemy hit** (max 5) | damage -20% |
| J5 Juggernaut | 75 | 4 | passive | damage below 20% max Health is **halved** (once per 30 s) | Stamina regen -20% |

## 2. 🏹 Archer

**Trunk**
| Node | Lv | Pts | Effect |
|---|---|---|---|
| T1 Steady Hands | 5 | 1 | draw strength 4 reached 8% faster |
| T2 Quiver Craft | 10 | 1 | 10% chance to recover a fired arrow |
| T3 Extra Bolts | 15 | 2 | crossbows hold **+1 bolt** (up to +4 more at Lv 55; LOCKED 2026-09-25 "up to +4") (updated 2026-10-06: "extra bolts" = the magazine cap goes **6 -> 10** in four ranks at Lv 15 / 30 / 42 / 55, not a bigger reload - see Archer-Bolts-Holster.md section 2) |
| T4 Light Step | 25 | 2 | +4% move speed while holding a bow / crossbow |
| T5 Eagle Eye | 40 | 2 | +6% crit chance at range over 15 blocks |
| T6 Holster Reload | **75** | 3 | a holstered crossbow **reloads in 30 s** (LOCKED 2026-09-25, late game) (updated 2026-10-06: moved from Lv 55 to **Lv 75**, near the top of the tree - Archer-Bolts-Holster.md Q2 default; the trunk gate is now Lv 75; points still fit: 25 of 25 at Lv 75, and at Lv 55 the Archer needs only 15 of 18) |

**Path A - Trapper** (roots and nets)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| A1 Lasting Roots | 20 | 2 | Pinning Shot | root +1 s; rooted enemies take **+10% damage from you** | Mark bonus -5 points |
| A2 Trap Arrows | 30 | 2 | Pinning Shot | the arrow leaves a **trap** at the impact (roots anyone who steps in for 2 s, 8 s lifetime) | cost +2 Mana |
| A3 Deep Net | 45 | 3 | Hunter's Net | the net **drags enemies toward its centre** over 2 s and roots them 1 s longer | net radius -1 block |
| A4 Marksman's Snare | 65 | 3 | Arrow Rain | enemies still in the rain after 1.5 s are rooted (was 2 s) | rain damage -15% |
| A5 Grand Trapper | 75 | 4 | all roots | roots on bosses last **half** (instead of immune), rooted enemies take +15% damage from the whole party | cooldowns +10% |

**Path B - Sharpshooter** (long range, single target)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| S1 Far Sight | 20 | 2 | Pinning Shot | range 30 -> 45 blocks; damage +10% beyond 20 blocks | -10% damage closer than 8 blocks |
| S2 Focus Mark | 30 | 2 | Pinning Shot | the Mark **stacks per hit** (up to 3 stacks, +5% each) | one target at a time (no pierce) |
| S3 Deadeye | 45 | 3 | passive | the first shot at a Marked target is an **auto-crit** (max once per 6 s per target) | -5% attack speed |
| S4 Piercing Aim | 65 | 3 | Rapid Fire | arrows become **a single focused shot every 0.4 s** (still 15 arrows) hitting the Marked target for +25% | no AoE or ricochet |
| S5 Executioner | 75 | 4 | passive | +30% damage to targets below 25% Health | -10% damage above 75% Health |

**Path C - Stormbow** (multi-target firepower)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| B1 Wide Volley | 20 | 2 | Rapid Fire | arrows spread in a 20-degree fan (hits several enemies) | -10% damage per arrow |
| B2 Chain Reaction | 30 | 2 | Explosive Arrow | the blast leaves a **burning patch** (3 s) and triggers a second small blast on a Marked target | cooldown +2 s |
| B3 Quick Hands | 45 | 3 | Rapid Fire | 18 arrows in 3 s | each arrow -8% damage |
| B4 Storm Cloud | 65 | 3 | Explosive Arrow | blast radius +1.5 blocks; **knock-up 0.5 s** | -15% single-target damage |
| B5 Arrow Tempest | 75 | 4 | Rapid Fire + Explosive | using one **refreshes** the other's cooldown by 30% | both cost +20% Mana |

## 3. 🔮 Mage

**Trunk**
| Node | Lv | Pts | Effect |
|---|---|---|---|
| T1 Mana Flow | 5 | 1 | +10% Mana regen out of combat |
| T2 Spell Focus | 10 | 1 | staff / spellbook charged shots +5% damage |
| T3 Long Blink | 15 | 2 | **Teleport distance +2 blocks** (10 -> 12; max at Lv 55: 20 blocks) and the trail lasts +1 s |
| T4 Barrier Lore | 25 | 2 | Mana Barrier ratio +0.2 HP per Mana |
| T5 Arcane Reserve | 40 | 2 | +10% max Mana |
| T6 Quick Hands | 55 | 3 | all Mage ability cooldowns -5% |

**Path A - Riftwalker** (mobility)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| R1 Blink Slash | 20 | 2 | Teleport | the trail damage **+50%** | the blink costs +20% Mana |
| R2 Rift Echo | 30 | 2 | Teleport | a second blink within 2 s is **free** (no Mana, half Stamina) | longer cooldown after the second (+3 s) |
| R3 Phase Step | 45 | 3 | Mana Barrier | on cast you **blink 5 blocks** back and the barrier appears there | barrier -1 s |
| R4 Meteor from the Rift | 65 | 3 | Meteor | Meteor can be cast **at your blink destination** while teleporting | Meteor damage -10% |
| R5 Rift Master | 75 | 4 | Teleport | blink through thin walls (1 block) and the trail slows enemies 25% | max Mana -10% |

**Path B - Light Bender** (radiant / spread)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| L1 Radiant Trail | 20 | 2 | Teleport | the trail turns to **Light**: it also heals allies 5% max Health/s | trail damage -25% |
| L2 Prism | 30 | 2 | Starfall | stars split into 2 beams each (more targets hit) | star damage -15% |
| L3 Beam Focus | 45 | 3 | Arcane Beam | the beam **refracts** to a second target within 6 blocks at 60% | channel starts 0.3 s later |
| L4 Brilliance | 65 | 3 | all | spells that hit 3+ enemies refund **10% of their Mana** | single-target spells cost +5% |
| L5 Sunburst | 75 | 4 | Starfall | a final burst at the end (1.5 H in the area) | cooldown +4 s |

**Path C - Arcanist** (raw power)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| C1 Overcharge | 20 | 2 | all | a spell cast at **full Mana** deals +15% | -10% damage under 25% Mana |
| C2 Siphon | 30 | 2 | all | kills restore 3 Mana | -5% max Health |
| C3 Heavy Barrier | 45 | 3 | Mana Barrier | absorb cap 100% -> 150% max Health | cost +10 Mana |
| C4 Deep Beam | 65 | 3 | Arcane Beam | ramp goes to **4x**, channel +0.5 s | cost +10 Mana |
| C5 Arch-Mage | 75 | 4 | Meteor | the blast leaves a 2-second **star well** that pulls enemies in | +4 s cooldown |

## 4. ✨ Priest

**Trunk**
| Node | Lv | Pts | Effect |
|---|---|---|---|
| T1 Gentle Hands | 5 | 1 | wand quick shots heal 10% more |
| T2 Faith | 10 | 1 | +5% max Mana |
| T3 Wide Prayer | 15 | 2 | **Sacred Heal radius 9 -> 10.5** and the instant heal +2 points (LOCKED idea: radius upgrades in the tree) |
| T4 Warm Light | 25 | 2 | Sacred Heal's heal-over-time **+10% of the instant heal** (separate upgrade) |
| T5 Sustained | 40 | 2 | Mana regen +10% while not casting for 4 s |
| T6 Patient Spirit | 55 | 3 | all Priest ability cooldowns -5% |

**Path A - Lightbringer** (big heals, Cleanse)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| LB1 **Cleanse** | 20 | 2 | Sacred Heal | **removes debuffs** from everyone healed (poison, slow, root, weaken) | cost +5 Mana; heal -10% |
| LB2 Radiant Pulse | 30 | 2 | Sacred Heal | the heal **pulses again after 2 s** at 50% | cooldown +3 s |
| LB3 Beacon | 45 | 3 | Martyr's Grace | target within 15 blocks also gets a **15 s regen** (2% / s) | the big heal -10% |
| LB4 Dawnlight | 65 | 3 | Sanctuary | zone also **cleanses** every 2 s and its radius +2 blocks | duration -2 s |
| LB5 Lightbringer | 75 | 4 | Sacred Heal | the Priest's own bonus 20% -> **40%** and allies **below 30%** are healed 25% more | cooldown +4 s |

**Path B - Aegis** (shields: bubble damage + element)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| A1 **Thorned Bubble** | 20 | 2 | Shield Bubble | enemies that **touch or hit** the bubble take damage (0.5 H per hit) | bubble HP -15% |
| A2 **Elemental Bubble** | 30 | 2 | Shield Bubble | pick **1 of 5 elements** (Fire, Water, Earth, Wind, Lightning): the bubble damage takes that element (burn, chill, stagger, push, shock) | cannot change without respec |
| A3 Layered Ward | 45 | 3 | Shield Bubble | the bubble has **two layers** (outer takes damage first, inner regenerates 3% / s) | duration -2 s |
| A4 Spirit Shield | 65 | 3 | Guardian Spirit | the save also gives a **bubble** around the ally for 4 s | save Health -10% |
| A5 Aegis | 75 | 4 | Shield Bubble | bubble **explodes** when it breaks (1.5 H element damage, 4 blocks) | duration -1 s |

**Path C - Soulweaver** (soul Bindings + Wings of Fate; needs the Soul Orb weapon)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| S1 Soul Link | 20 | 2 | Soul Orb | Bindings **stabilize 0.4 s faster** | Mana drain +10% |
| S2 Stored Light | 30 | 2 | Soul Orb | stored soul healing cap +25% | stored healing decays 3% / s after you release |
| S3 Wings of Mercy | 45 | 3 | Wings of Fate | arrival heal +50% and **cleanses** the ally | the glide costs +20% Stamina |
| S4 Soul Harvest | 65 | 3 | Soul Orb | Binding kills grant **+2 Mana** each and +5% damage per Binding (max 5) | wand damage -10% |
| S5 Soulweaver | 75 | 4 | Soul Orb | Wings of Fate can **carry one ally** back to you | longer cooldown (+8 s) |

## 5. 🪓 Berserker

**Trunk**
| Node | Lv | Pts | Effect |
|---|---|---|---|
| T1 Thick Skin | 5 | 1 | +6% max Health |
| T2 Heavy Hands | 10 | 1 | charged swings +5% damage |
| T3 Battle Lungs | 15 | 2 | Stamina regen +10% in combat |
| T4 Rage Reserve | 25 | 2 | Enrage's peak +3% |
| T5 Bloodied | 40 | 2 | +5% damage below 50% Health |
| T6 Unyielding | 55 | 3 | all Berserker cooldowns -5% |

**Path A - Warbringer** (party rage)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| W1 War Horn | 20 | 2 | Enrage | party radius +3 and the buff starts at **+15%** (instead of +10%) | your own peak -5 points |
| W2 Shared Fury | 30 | 2 | Enrage | allies who kill an enemy during it **extend** it by 1 s (max +5 s) | cooldown +3 s |
| W3 Banner Bearer | 45 | 3 | Warlord's Banner | the banner also restores 1% max Health per second to allies | duration -3 s |
| W4 Rally | 65 | 3 | Enrage | at the peak a **war cry** gives the party a 10% max Health shield | the cast costs +6 Mana |
| W5 Warbringer | 75 | 4 | Enrage | **ends gently** (the buff fades over 3 s instead of dropping) | peak -10% |

**Path B - Bloodbound** (life steal, low-Health power)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| B1 Hunger | 20 | 2 | passive | heal **4% of damage dealt** while below 50% Health | -4% max Health |
| B2 Bleed | 30 | 2 | Whirlwind | hits cause a **bleed** (0.2 H per second, 4 s) | Whirlwind damage -10% |
| B3 Crimson Frenzy | 45 | 3 | Blood Frenzy | stacks +2.5% (was +2%) and each stack heals 0.5% | needs 3 hits to start |
| B4 Blood Pact | 65 | 3 | Earthsplitter | pay **10% of current Health** to add +30% damage | cannot kill you |
| B5 Bloodbound | 75 | 4 | passive | first lethal hit leaves you at 1 HP with a 3 s damage boost (+40%) (once per 90 s) | healing received -20% |

**Path C - Smasher** (stuns and knock-ups)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| M1 Crushing Blows | 20 | 2 | passive | heavy charged hits stun 0.4 s | attack speed -5% |
| M2 Seismic | 30 | 2 | Earthsplitter | line becomes a **wide wave** (3 blocks wide) | length 12 -> 9 |
| M3 Staggering Spin | 45 | 3 | Whirlwind | spin **knocks enemies back** 1 block each tick | no lifesteal |
| M4 Ground Pound | 65 | 3 | Earthsplitter | the end of the line **slams** (1.5 H, 1 s stun) | cooldown +3 s |
| M5 Smasher | 75 | 4 | passive | every 5th heavy hit sends enemies flying (3 blocks) | -10% damage on other hits |

## 6. 🥋 Monk (class skill name still open)

**Trunk**
| Node | Lv | Pts | Effect |
|---|---|---|---|
| T1 Light Step | 5 | 1 | +3% move speed |
| T2 Soft Landing | 10 | 1 | fall damage -10% (stacks with the Flowing fall) |
| T3 Vault Mastery | 15 | 2 | the Pole-Vault goes 10% higher and farther |
| T4 Skipping Rhythm | 25 | 2 | the **skipping-bound** timing window is 0.1 s wider |
| T5 Calm Breath | 40 | 2 | Stamina regen +10% |
| T6 Master's Poise | 55 | 3 | all Monk cooldowns -5% |

**Path A - Wind Dancer** (skipping, vaults, air combos)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| D1 Airborne | 20 | 2 | traversal | a second free mid-air jump after a vault | +10% Stamina cost |
| D2 Skip Chain | 30 | 2 | traversal | skipping bounds can chain **+2 more** | bounds do no fall resist |
| D3 Aerial Palm | 45 | 3 | Palm Strike | usable **in the air**: sends the target upward | -10% stun |
| D4 Wind Step | 65 | 3 | Flowing Form | the aura **follows** your air movement; speed +10% while airborne | -5% attack speed |
| D5 Wind Master | 75 | 4 | traversal | Rising Strike / Pole-Vault can be **chained** into a vault twice | cooldown +4 s |

**Path B - Iron Fist** (fist damage, Plunge Punch, Palm stuns)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| F1 Hard Knuckles | 20 | 2 | fists | +8% damage with fist weapons | -3% move speed |
| F2 Plunge Power | 30 | 2 | Plunge Punch | the slam damages the area (1.5 H, 3 blocks) | 0.3 s landing lag |
| F3 Concussive Palm | 45 | 3 | Palm Strike | stun 0.75 -> **1.0 s** and a 2 s damage-taken +10% | cost +3 Mana |
| F4 Iron Skin | 65 | 3 | passive | -10% damage taken while at 10+ combo | -5% move speed |
| F5 Iron Fist | 75 | 4 | Palm Strike | each **third** Palm Strike on one target is a guaranteed crit | cooldown +1 s |

**Path C - Serene** (Still Water / Awe defence and control)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| E1 Calm Aura | 20 | 2 | Flowing Form | Awe also **lowers enemy damage** by 8% | your speed buff -5 points |
| E2 Reflexes | 30 | 2 | Still Water | counters also **stun** 0.5 s | stance duration -2 s |
| E3 Deep Breath | 45 | 3 | Flowing Form | combo decays 50% slower | start cost +2 Mana |
| E4 Tranquility | 65 | 3 | Still Water | while it holds you regenerate 1% max Health / s | 20% slower movement |
| E5 Serenity | 75 | 4 | Flowing Form | Awed enemies **hesitate** (attack speed -15%) | the buff doubles at 20 combo, not 15 |

## 7. 🗡️ Assassin

**Trunk**
| Node | Lv | Pts | Effect |
|---|---|---|---|
| T1 Quiet Feet | 5 | 1 | crouch walking is 10% faster |
| T2 Sharp Eye | 10 | 1 | +4% crit chance |
| T3 Kunai Reach | 15 | 2 | thrown kunai range +3 blocks (teleport up to 23) |
| T4 Nimble | 25 | 2 | fall damage -15% |
| T5 Deadly Focus | 40 | 2 | +10% damage from behind (backstab bonus) |
| T6 Shadow's Patience | 55 | 3 | all Assassin cooldowns -5% |

**Path A - Shadow** (cloak, First Strike, God Killer)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| H1 Longer Cloak | 20 | 2 | Cloak | cloak +2 s; the break-on-hit grace 0.3 s | cooldown +4 s |
| H2 Lethal Opener | 30 | 2 | First Strike | crit damage +15%; a second hit within 2 s also gets +50% crit chance | window -2 s |
| H3 Boss Hunter | 45 | 3 | God Killer | multiplier 2x -> **2.3x**; works on **elites** too | cooldown +10 s |
| H4 Slip Away | 65 | 3 | Cloak | after a kill you recloak for 2 s (max once per 20 s) | cost +4 Mana |
| H5 Death Mark | 75 | 4 | First Strike | marks the target: your next hit within 5 s is **x1.5** more | the first strike -10% |

**Path B - Venom** (poison stacks, spreading Toxin, Weaken)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| V1 Potent Mix | 20 | 2 | Toxin | poison **stacks** (3 stacks, +30% each) | cloud radius -1 block |
| V2 Cripple | 30 | 2 | Toxin | Weaken 15% -> 25% | cloud 1 s shorter |
| V3 Contagion | 45 | 3 | Toxin | poisoned enemies **spread poison** to those within 2 blocks | poison damage -15% |
| V4 Venom Blade | 65 | 3 | daggers | daggers apply 1 poison stack per hit (max 3) | -5% dagger damage |
| V5 Plague | 75 | 4 | Toxin | **double** the cloud duration and Weakened enemies take +10% from you | cooldown +6 s |

**Path C - Blink** (kunai range, return knockback, extra teleports)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| K1 Long Throw | 20 | 2 | Kunai | teleport range 20 -> 26 | -10% kunai damage |
| K2 Hard Return | 30 | 2 | Return | return knockback doubles and **stuns 0.4 s** | return window 8 -> 6 s |
| K3 Double Step | 45 | 3 | Kunai | a **second** teleport within 3 s (half Stamina, no Mana) | cooldown +3 s |
| K4 Blink Strike | 65 | 3 | Kunai | arriving next to an enemy within 3 blocks hits it for 1.0 H | cost +10% |
| K5 Shadow Blink | 75 | 4 | Kunai | cloaks you for 1.5 s on arrival | teleport range -4 |

## 8. Checks and findings
| # | Finding |
|---|---|
| 1 | Points: floor(class level / 3) = 33 at Lv 99; trunk (11) + one path (14) = **25** points; the level gates were chosen so cumulative cost never exceeds the points available (checked: Lv 5 -> 1, Lv 10 -> 2, Lv 15 -> 4, Lv 20 -> 6, Lv 25 -> 8, Lv 30 -> 10, Lv 40 -> 12, Lv 45 -> 15, Lv 55 -> 18, Lv 65 -> 21, Lv 75 -> 25). |
| 2 | Each class path locks the other two at its first node (N1); respec costs coins. |
| 3 | The LOCKED examples are in: Priest **Thorned Bubble -> Elemental Bubble (1 of 5 elements)** and **Cleanse as a Sacred Heal upgrade**. |
| 4 | LOCKED "up to +4 bolts" and "holstered crossbow reload ~30 s late-game" are the Archer trunk nodes T3 and T6. |
| 5 | Mage Teleport distance / custom shorter distance: trunk T3 ("10 blocks to start, upgradable in the tree"). |
| 6 | A few nodes depend on systems not built (Soul Orb, Plunge Punch, kunai return, traversal chains); those are marked by ability name. |

## 9. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Whether the per-class tree can reuse SkyyTrees' structure (nodes + points) as an extra tree type, and how "locked path" exclusivity maps to the existing node state. |
| 2 | "Intercept damage" (Guardian's Oath), "damage reflect", "bleed", "stack" effects need damage-event hooks; they are code, not rune data. |
| 3 | The Priest element choice stores 1 of 5 per profile; the Bubble then needs five damage skins (engine damage causes exist). |
| 4 | Class level points: confirm the source ("Class Level" in SkyySkills = class skill level or the Overall Level?). |

## 10. Questions for Skyy
1. Points: 1 per 3 class levels (25 for trunk + path by Lv 75), or more generous?
2. Are 3 paths x 5 nodes + a 6-node trunk the right size (21 nodes per class; the earlier decision said about 25)?
3. Should a respec cost coins, a rare item, or be free on a long cooldown?
