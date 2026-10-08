# Class tree paths - Wynncraft-style locked paths for the 7 classes

Cloud draft, 2026-10-06. Locks (docs/answered/classes.md, 2026-10-04): the **class tree** sells upgrades that **change how an ability works** (not just buff it); they are **paths**: choosing a path **locks out the other two**; the example is the Priest's Shield Bubble
(a node makes it damage enemies that touch or hit it, then pick **1 of 5 elements**); **Cleanse is a Sacred Heal upgrade** in the class tree. **Modifiers live in the ability tree, not here** (`Modifier-Pool-Spec.md`).
Path names come from the "tree path ideas" at the bottom of each class file. Numbers are placeholders; every node has a **trade-off** (that is what keeps it a sidegrade).

**Updated 2026-10-07** to Skyy's locks of that day (docs/answered/classes.md lines dated 2026-10-07 + the class files' change logs): **Monk and Assassin are playable classes** (SkyyClasses 0.1.14; Monk's class skill = **Discipline**, name still open); Mana Barrier = a **placed dome** (12 s, Mana instead of Health; **Follow is a modifier** - and, corrected 2026-10-08 per L113, also ONE class-tree upgrade: Mage R3, see below); Guardian Spirit = a **passive 30-block aura** whose "party only / every player" choice is a **class-tree switch** (Priest trunk **TS**); Flowing Form = **combo stacks** (1 per hit, max 20, 5 s decay each, the 15-combo doubling is gone); Blood Frenzy = a **toggle aura** (25 stacks, 6 s decay, Mana + Stamina per attack; **Floor** is a modifier); Warlord's Banner reworked (30 s, 12 blocks, damage + defence + attack speed, kill extensions, falls when you leave); Enrage picks its targets **once at activation** (players 8 / party 16, not an aura); dagger charged = **Shadow Step**; Berserker traversals (battleaxe **Lunge**, axe **Whirlwind Dash**, proposed club **Bull Rush** / mace **Earthshaker**); fist attacks (wraps multi-jab + power hit, gauntlets chain of 4); Sanctuary 12 s / 8 blocks / 5% per s; Martyr's Grace 30 blocks, 75% first heal, chain -15 points per jump; Shield Bubble 6 blocks / 12 s with 4 heal pulses tied to its HP; soul tethers are now **Bindings**. **No void protection anywhere**: no node shortens, halves, blocks or redirects a move because of the void (walls / inside-block / arena safety stay). **Echo, Follow, Floor, Chain and every other modifier stay in the ability tree** - no node below copies one (one exception since 2026-10-08: Mage R3, below).

**Stale-node fix 2026-10-08** (research/cloud/Class-Tree-Stale-Fix-1008.md; checked against the LIVE SkyyTrees 0.3.3 texts in SkyyTrees/build_skyytrees_0.3.3.py): docs/answered/classes.md L113 says Mana Barrier's Follow is "a Follow modifier / skill-tree upgrade" - so Mage **R3 Phase Step** becomes the dome-follows-you node (the modifier stays for everyone else); Priest **LB2** overlapped Sacred Heal's Echo (L141) -> proposed **Guiding Light**; Berserker **W2** copied the Warlord's Banner kill extension (L133) -> proposed **Shared Fury = rage swap**; Monk **E5** trade-off no longer mentions the removed doubling. W1 War Horn and B3 Crimson Frenzy were already fixed on 2026-10-07 (no "radius +3", no "+2.5%") and match the live text. Node ids never change (saved files hold ids); rows whose live 0.3.3 text differs are marked and listed in research/cloud/Class-Tree-Build-Map.md section 9. All of them are waiting ("Comes with the class abilities") nodes, so nobody owns them.

## 0. Shape of every class tree

| Part | Rule |
|---|---|
| **Trunk** (shared, 6 nodes) | class-wide upgrades every path gets: weapon / traversal / survival basics. Not locked |
| **3 paths x 5 nodes** | pick **one path** at its first node (**N1**); the other two lock; nodes in a path are taken in order |
| Points | (updated 2026-10-07) the tree spends the **live Ability Points** of SkyyTrees (LOCKED 2026-10-02: 1 at class skill 1, +1 every 2 levels, max 50) - the draft's "1 per 3 levels" is dropped. Trunk (11) + one path (14) = **25 points**; with the Root of the stat spine (1) that is 26 AP, reached at class skill 50; at every level gate below the AP available stay above the cumulative cost (Lv 5: 2 of 3 ... Lv 75: 26 of 38) |
| Switches | (2026-10-07) a **switch node** costs 0 points and can be flipped on / off in the tree at any time (no respec). Only one so far: Priest **TS** (Guardian Spirit reach) |
| Level gates | Trunk: Lv 5 / 10 / 15 / 25 / 40 / 55 (cost 1 / 1 / 2 / 2 / 2 / 3) (updated 2026-10-06: Archer T6 Holster Reload is Lv 75; other classes' T6 stay at 55). Path nodes: Lv **20 / 30 / 45 / 65 / 75** (cost 2 / 2 / 3 / 3 / 4). Check: points available at a gate always cover the cumulative cost (script-checked) |
| Respec | swapping paths costs coins (a sink; row `tree.respecCoins`) and refunds all path points; trunk stays (2026-10-07: until a path-only respec is built, the live whole-tree respec of SkyyTrees is used - class skill level x 100 coins; see Class-Tree-Build-Map.md) |
| Balance | one **power ledger slot** of about +20% (Class-Ability-Spec-Draft section 4); a node that adds a behaviour also carries a downside (listed) |
The five elements for elemental nodes = the engine's **Fire, Water, Earth, Wind, Lightning** (the same five as SkyyGear's element damage).

## 1. 🛡️ Warrior

(2026-10-07: no node for a shield traversal - Skyy SHELVED it until a new shield weapon type exists.)

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
| T3 Long Blink | 15 | 2 | **Teleport distance +2 blocks** (updated 2026-10-07: the live staff blink is 16 blocks since SkyyArmory 0.1.4, so 16 -> 18 at Lv 15, +1 more at Lv 30 / 42 / 55 = 22 max) and the trail lasts +1 s; no void check (falling is the player's problem) |
| T4 Barrier Lore | 25 | 2 | Mana Barrier ratio +0.2 HP per Mana (the dome takes 1 Mana per 2 HP -> 1 per 2.2 HP) |
| T5 Arcane Reserve | 40 | 2 | +10% max Mana |
| T6 Quick Hands | 55 | 3 | all Mage ability cooldowns -5% |

**Path A - Riftwalker** (mobility)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| R1 Blink Slash | 20 | 2 | Teleport | the trail damage **+50%** | the blink costs +20% Mana |
| R2 Rift Echo | 30 | 2 | Teleport | a second blink within 2 s is **free** (no Mana, half Stamina) | longer cooldown after the second (+3 s) |
| R3 Phase Step | 45 | 3 | Mana Barrier | (rewritten 2026-10-08, L113: Follow is also a skill-tree upgrade - this is it) on cast you **blink 5 blocks** back and the dome **moves with you** for its whole run at **full strength** (the Follow modifier gives 80-100%); the Follow modifier then cannot be equipped on Mana Barrier (pick another) - **proposed, default** (live 0.3.3 text differs - change in the next SkyyTrees build) | dome 12 -> 10 s |
| R4 Meteor from the Rift | 65 | 3 | Meteor | Meteor can be cast **at your blink destination** while teleporting | Meteor damage -10% |
| R5 Rift Master | 75 | 4 | Teleport | blink through thin walls (1 block; it still never lands inside a block) and the trail slows enemies 25% | max Mana -10% |

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
| C3 Charged Dome | 45 | 3 | Mana Barrier | (rewritten 2026-10-07: the dome has no absorb cap any more - it drains Mana until it ends or your Mana runs out) the dome **stores** the damage it turns into Mana drain; when it ends it **bursts** for 50% of the stored damage on enemies within 4 blocks (damage, unlike the Knockback+ modifier's push) | worse ratio: 1 Mana per 1.5 HP |
| C4 Deep Beam | 65 | 3 | Arcane Beam | ramp goes to **4x**, channel +0.5 s | cost +10 Mana |
| C5 Arch-Mage | 75 | 4 | Meteor | the blast leaves a 2-second **star well** that pulls enemies in | +4 s cooldown |

## 4. ✨ Priest

**Trunk**
| Node | Lv | Pts | Effect |
|---|---|---|---|
| T1 Gentle Hands | 5 | 1 | the wand's **healing orb** heals 10% more (updated 2026-10-07: quick shots do not heal - the charged orb's healing circle does) |
| T2 Faith | 10 | 1 | +5% max Mana |
| T3 Wide Prayer | 15 | 2 | **Sacred Heal radius 9 -> 10.5** and the instant heal +2 points (LOCKED idea: radius upgrades in the tree) |
| T4 Warm Light | 25 | 2 | Sacred Heal's heal-over-time **+10% of the instant heal** (separate upgrade) |
| T5 Sustained | 40 | 2 | Mana regen +10% while not casting for 4 s |
| T6 Patient Spirit | 55 | 3 | all Priest ability cooldowns -5% |
| **TS Open Aura** (switch, added 2026-10-07) | 1 | **0** | **Guardian Spirit reach** (LOCKED 2026-10-07: "priest can turn on and off weather it heals players, or just party members in the skill tree"): OFF (default) = the passive saves **party members only** (and you); ON = it saves **every player** in its 30-block aura. Flip it any time in the tree - no respec. Trade-off: strangers' saves spend your Mana and start their own doubling per-player cooldowns (12 / 24 / 48 s ...). Needs Guardian Spirit (A2-alt) to do anything |

**Path A - Lightbringer** (big heals, Cleanse)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| LB1 **Cleanse** | 20 | 2 | Sacred Heal | **removes debuffs** from everyone healed (poison, slow, root, weaken) | cost +5 Mana; heal -10% |
| LB2 **Guiding Light** (was Radiant Pulse) | 30 | 2 | Sacred Heal | (replaced 2026-10-08 - proposed, default: "pulses again after 2 s at 50%" copied Sacred Heal's **Echo** modifier, L141, and beat it 50% vs 30%) Sacred Heal can be **aimed at an ally you look at within 20 blocks**: the 9-block circle forms around them instead of you (you are healed only if you stand in it; Echo pulses in that circle) (live 0.3.3 text differs - change in the next SkyyTrees build) | cast 0.5 s slower |
| LB3 Beacon | 45 | 3 | Martyr's Grace | (updated 2026-10-07: Martyr's Grace now reaches 30 blocks and chains 75 / 60 / 45 / 30 / 15%) every target the chain heals also gets a **10 s regen** (2% / s) | first heal 75% -> 65% (the chain drops from there) |
| LB4 Dawnlight | 65 | 3 | Sanctuary | zone also **cleanses** every 2 s and its radius +2 blocks (8 -> 10) | duration -2 s (12 -> 10) |
| LB5 Lightbringer | 75 | 4 | Sacred Heal | the Priest's own bonus 20% -> **40%** and allies **below 30%** are healed 25% more | cooldown +4 s |

**Path B - Aegis** (shields: bubble damage + element)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| A1 **Thorned Bubble** | 20 | 2 | Shield Bubble | enemies that **touch or hit** the bubble take damage (0.5 H per hit) | bubble HP -15% |
| A2 **Elemental Bubble** | 30 | 2 | Shield Bubble | pick **1 of 5 elements** (Fire, Water, Earth, Wind, Lightning): the bubble damage takes that element (burn, chill, stagger, push, shock) | cannot change without respec |
| A3 Layered Ward | 45 | 3 | Shield Bubble | the bubble has **two layers** (outer takes damage first, inner regenerates 3% / s); the 4 heal pulses (75 / 50 / 25 / 0% HP, LOCKED 2026-10-07) count the two layers as one HP bar | duration -2 s (12 -> 10) |
| A4 Spirit Shield | 65 | 3 | Guardian Spirit | (updated 2026-10-07: Guardian Spirit is a passive aura save) every save also puts a small **bubble** (blocks projectiles) around the saved player for 4 s | they are saved at 20% Health instead of 30% |
| A5 Aegis | 75 | 4 | Shield Bubble | bubble **explodes** when it breaks (1.5 H element damage, 4 blocks; the last heal pulse still fires) | duration -1 s |

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
| T3 Warpath | 15 | 2 | (rewritten 2026-10-07 for the one-traversal-per-weapon lock) the weapon traversals go **15% farther** and cost **10% less Stamina**: battleaxe **Lunge**, axe **Whirlwind Dash**, club **Bull Rush** and mace **Earthshaker** (the last two still proposed) - the old Battle Lungs Stamina idea is folded in here |
| T4 Rage Reserve | 25 | 2 | Enrage's peak +3% |
| T5 Bloodied | 40 | 2 | +5% damage below 50% Health |
| T6 Unyielding | 55 | 3 | all Berserker cooldowns -5% |

**Path A - Warbringer** (party rage)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| W1 War Horn | 20 | 2 | Enrage | (rewritten 2026-10-07: Enrage picks players within 8 / party within 16 ONCE at activation - a bigger circle is the Radius+ modifier) a **second call 3 s after activation** picks up anyone who walked into range late; allies start at **+15%** (instead of +10%) | your own peak -5 points |
| W2 Shared Fury | 30 | 2 | Enrage | (replaced 2026-10-08 - proposed, default: "kills extend it" copied the Warlord's Banner kill extension, L133, one node before W3 Banner Bearer) **rage swap**: the ally you look at when you cast (within 16 blocks, picked once like the rest) gets **your doubled buff** (+20% -> +40%, self cap +60%) and you get the ally buff; no ally in sight = normal Enrage (live 0.3.3 text differs - change in the next SkyyTrees build) | cooldown +3 s |
| W3 Banner Bearer | 45 | 3 | Warlord's Banner | (banner reworked 2026-10-07: 30 s, 12 blocks, damage + defence + attack speed, kills extend it) the banner also restores 1% max Health per second to everyone in its range | base duration 30 -> 25 s (kill extensions and the 60 s cap unchanged) |
| W4 Rally | 65 | 3 | Enrage | at the peak a **war cry** gives the party a 10% max Health shield | the cast costs +6 Mana |
| W5 Warbringer | 75 | 4 | Enrage | **ends gently** (the buff fades over 3 s instead of dropping) | peak -10% |

**Path B - Bloodbound** (life steal, low-Health power)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| B1 Hunger | 20 | 2 | passive | heal **4% of damage dealt** while below 50% Health | -4% max Health |
| B2 Bleed | 30 | 2 | Whirlwind | hits cause a **bleed** (0.2 H per second, 4 s) | Whirlwind damage -10% |
| B3 Crimson Frenzy | 45 | 3 | Blood Frenzy | (rewritten 2026-10-07: Blood Frenzy is a toggle aura - +1.5% damage / +1% attack speed / +0.5% move per stack, 25 max, 6 s decay; a bigger per-stack bonus is Power+ and a minimum stack is the Floor modifier) every stack you gain **heals you 0.5% max Health** and allies inside the aura 0.25% | Mana + Stamina per attack +20% |
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

## 6. 🥋 Monk (playable since SkyyClasses 0.1.14; class skill **Discipline** - the name is still open for Skyy)

**Trunk**
| Node | Lv | Pts | Effect |
|---|---|---|---|
| T1 Light Step | 5 | 1 | +3% move speed |
| T2 Soft Landing | 10 | 1 | fall damage -10% (stacks with the Flowing fall) |
| T3 Vault Mastery | 15 | 2 | the bo **Pole-Vault** and the fist **Rising Strike** go 10% higher and farther (one traversal per weapon family) |
| T4 Skipping Rhythm | 25 | 2 | the **skipping-bound** timing window is 0.1 s wider |
| T5 Calm Breath | 40 | 2 | Stamina regen +10% |
| T6 Master's Poise | 55 | 3 | all Monk cooldowns -5% |

**Path A - Wind Dancer** (skipping, vaults, air combos)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| D1 Airborne | 20 | 2 | traversal | a second free mid-air jump after a vault | +10% Stamina cost |
| D2 Skip Chain | 30 | 2 | traversal | skipping bounds can chain **+2 more** | bounds do no fall resist |
| D3 Aerial Palm | 45 | 3 | Palm Strike | usable **in the air**: sends the target upward | -10% stun |
| D4 Wind Step | 65 | 3 | Flowing Form | (rewritten 2026-10-07: the aura is always around you, and Flowing Form is now combo stacks) hits you land **while airborne** (vault kick, Rising Strike, an air Palm Strike) give **2 combo stacks** | each stack decays after 4 s instead of 5 |
| D5 Wind Master | 75 | 4 | traversal | Rising Strike / Pole-Vault can be **chained** into a vault twice | cooldown +4 s |

**Path B - Iron Fist** (fist damage, Plunge Punch, Palm stuns)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| F1 Hard Knuckles | 20 | 2 | fists | (rewritten 2026-10-07 for the fist attacks) the **wraps' power hit** and the **gauntlets' 4th-jab finisher** deal **+20%** | the other jabs deal -5% |
| F2 Plunge Power | 30 | 2 | Plunge Punch | the slam damages the area (1.5 H, 3 blocks) | 0.3 s landing lag |
| F3 Concussive Palm | 45 | 3 | Palm Strike | stun 0.75 -> **1.0 s** and a 2 s damage-taken +10% | cost +3 Mana |
| F4 Iron Skin | 65 | 3 | Flowing Form | -10% damage taken while Flowing Form holds **10+ combo stacks** | -5% move speed |
| F5 Iron Fist | 75 | 4 | Palm Strike | each **third** Palm Strike on one target is a guaranteed crit | cooldown +1 s |

**Path C - Serene** (Still Water / Awe defence and control)
| Node | Lv | Pts | Ability | What changes | Trade-off |
|---|---|---|---|---|---|
| E1 Calm Aura | 20 | 2 | Flowing Form | Awed enemies also **deal less damage**: -0.4% per total combo of the ability (cap -8%), on top of the locked defence / move debuff | your move speed per stack +2% -> +1.5% |
| E2 Reflexes | 30 | 2 | Still Water | counters also **stun** 0.5 s | stance duration -2 s |
| E3 Deep Breath | 45 | 3 | Flowing Form | each combo stack decays after **7.5 s** instead of 5 s | start cost +2 Mana |
| E4 Tranquility | 65 | 3 | Still Water | while it holds you regenerate 1% max Health / s | 20% slower movement |
| E5 Serenity | 75 | 4 | Flowing Form | Awed enemies **hesitate** (attack speed -15%) and the "distracted" moment lasts 2 s instead of ~1 s | max combo stacks 20 -> 18 (trade-off text cleaned 2026-10-08; the live 0.3.3 text "max combo 18" already matches) |

## 7. 🗡️ Assassin (playable since SkyyClasses 0.1.14; class skill Assassination)

**Trunk**
| Node | Lv | Pts | Effect |
|---|---|---|---|
| T1 Quiet Feet | 5 | 1 | crouch walking is 10% faster |
| T2 Sharp Eye | 10 | 1 | +4% crit chance |
| T3 Long Reach | 15 | 2 | thrown kunai range +3 blocks (teleport up to 23) and (added 2026-10-07) the dagger **Shadow Step** reaches 24 -> 27 blocks (no-target step 18 -> 20; it may end in the air or over the void - no void protection) |
| T4 Nimble | 25 | 2 | fall damage -15% |
| T5 Deadly Focus | 40 | 2 | +10% damage from behind (backstab bonus; it also adds to Shadow Step's guaranteed backstab) |
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
| K4 Blink Strike | 65 | 3 | Kunai + Shadow Step | arriving next to an enemy within 3 blocks hits it for 1.0 H - after a kunai teleport and (added 2026-10-07) after a Shadow Step, whose next backstab stays guaranteed | cost +10% (Stamina for Shadow Step) |
| K5 Shadow Blink | 75 | 4 | Kunai | cloaks you for 1.5 s on arrival | teleport range -4 |

## 8. Checks and findings
| # | Finding |
|---|---|
| 1 | Points: floor(class level / 3) = 33 at Lv 99; trunk (11) + one path (14) = **25** points; the level gates were chosen so cumulative cost never exceeds the points available (checked: Lv 5 -> 1, Lv 10 -> 2, Lv 15 -> 4, Lv 20 -> 6, Lv 25 -> 8, Lv 30 -> 10, Lv 40 -> 12, Lv 45 -> 15, Lv 55 -> 18, Lv 65 -> 21, Lv 75 -> 25). (2026-10-07: re-checked against the LIVE Ability Points 1 + floor(L / 2) with the spine Root (1 AP) on top: needed 2 / 3 / 5 / 7 / 9 / 11 / 13 / 16 / 19 / 22 / 26 vs available 3 / 6 / 8 / 11 / 13 / 16 / 21 / 23 / 28 / 33 / 38 - always fits.) |
| 2 | Each class path locks the other two at its first node (N1); respec costs coins. |
| 3 | The LOCKED examples are in: Priest **Thorned Bubble -> Elemental Bubble (1 of 5 elements)** and **Cleanse as a Sacred Heal upgrade**. |
| 4 | LOCKED "up to +4 bolts" and "holstered crossbow reload ~30 s late-game" are the Archer trunk nodes T3 and T6. |
| 5 | Mage Teleport distance / custom shorter distance: trunk T3 ("10 blocks to start, upgradable in the tree"). |
| 6 | A few nodes depend on systems not built (Soul Orb, Plunge Punch, kunai return, traversal chains); those are marked by ability name. (2026-10-07: kunai throw + teleport + return, the fist / bo items and the staff blink are LIVE in SkyyArmory 0.1.7; Shadow Step is being built; Pole-Vault, Rising Strike, the Berserker traversals and every class ability are not built - the per-node status is in Class-Tree-Build-Map.md.) |
| 7 | (2026-10-07) No node adds or removes void protection, and no node is a copy of a modifier (Echo, Follow, Floor, Chain, Duration+ ... live in the ability tree). Nodes that clashed with the day's locks were rewritten in place (marked "updated / rewritten 2026-10-07"): Mage T3 / R3 / C3, Priest T1 / LB3 / LB4 / A3 / A4, Berserker T3 / W1 / W3 / B3, Monk T3 / D4 / F1 / F4 / E1 / E3 / E5, Assassin T3 / T5 / K4; Priest TS is new. (2026-10-08: Mage R3 is the one Follow exception - L113 makes Follow also a tree upgrade; Priest LB2 and Berserker W2 replaced because they copied Echo / the Banner kill extension - research/cloud/Class-Tree-Stale-Fix-1008.md.) |

## 9. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Whether the per-class tree can reuse SkyyTrees' structure (nodes + points) as an extra tree type, and how "locked path" exclusivity maps to the existing node state. (2026-10-07: answered in Class-Tree-Build-Map.md - page 2 of the live class tree becomes trunk + paths; the path lock is a new "one path per tree" rule on the lane field.) |
| 2 | "Intercept damage" (Guardian's Oath), "damage reflect", "bleed", "stack" effects need damage-event hooks; they are code, not rune data. |
| 3 | The Priest element choice stores 1 of 5 per profile; the Bubble then needs five damage skins (engine damage causes exist). |
| 4 | Class level points: confirm the source ("Class Level" in SkyySkills = class skill level or the Overall Level?). (2026-10-07: the class SKILL level - skill:fn:level(uuid, "Archery" ... "Discipline"), as the live Ability Points already do.) |

## 10. Questions for Skyy
1. Points: 1 per 3 class levels (25 for trunk + path by Lv 75), or more generous? (2026-10-07: settled by the earlier lock - the live Ability Points, 1 + 1 per 2 levels, max 50.)
2. Are 3 paths x 5 nodes + a 6-node trunk the right size (21 nodes per class; the earlier decision said about 25)?
3. Should a respec cost coins, a rare item, or be free on a long cooldown?
4. (2026-10-07) Mage: the locked "set a shorter custom distance" for the staff teleport - a tree switch, or a /settings player row? [a /settings row in SkyyArmory - a switch node cannot hold a number]

## 11. Change log
- 2026-10-06: cloud draft (trunk 6 + 3 paths x 5 per class, trade-offs, points 1 per 3 levels).
- 2026-10-07: matched to Skyy's 2026-10-07 locks - Monk + Assassin playable (Discipline / Assassination), Mana Barrier placed dome (Follow = modifier), Guardian Spirit passive + new Priest switch TS (party only / every player), Flowing Form combo stacks, Blood Frenzy toggle aura (Floor = modifier), Warlord's Banner rework, Enrage picked once at activation, Shadow Step, Berserker one-traversal-per-weapon (trunk T3 Warpath), fist attacks, Sanctuary / Martyr's Grace / Shield Bubble numbers, no void protection anywhere; points = the live Ability Points; build plan in Class-Tree-Build-Map.md.
- 2026-10-08: stale-node fix against the live SkyyTrees 0.3.3 texts - Mage R3 Phase Step = the Mana Barrier Follow tree upgrade (L113), Priest LB2 Radiant Pulse -> Guiding Light (Echo overlap, L141), Berserker W2 Shared Fury -> rage swap (Banner kill-extension overlap, L133), Monk E5 trade-off text; W1 / B3 checked, already right. Ids unchanged; text changes queued in research/cloud/Class-Tree-Build-Map.md section 9; details research/cloud/Class-Tree-Stale-Fix-1008.md.
