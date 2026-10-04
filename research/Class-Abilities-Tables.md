# Class abilities - option tables (draft for Skyy to refine)

*2026-10-04. Built from Skyy's locks (OPEN-QUESTIONS "LOCKED 2026-10-04", research/Class-Roles-Ideas.md top block). Rows marked
**LOCKED** are Skyy's; rows marked *proposed* are first drafts to refine. All numbers are placeholders.*

**How a class works (locked):** 2 weapon types (no sharing), each with its own traversal (the charged attack). Abilities: A1 first, then
A2, then the A2 swap-out, and later ONE of two improved A1 alternatives (pick one, the other is locked out) - 5 designed, 4 owned, 2
equipped. Each ability levels up by use (a little stronger per level) and its levels buy and level its own modifiers: 4 per ability, 2
equipped, no doubling the same modifier, one shared modifier pool. The class tree adds choose-one PATHS that change how an ability
works (example: the Priest shield damages enemies that touch it, then pick 1 of 5 elements).

## Shared modifier pool (~18)

| Modifier | What it does | Levels add |
|---|---|---|
| Duration+ | lasts longer | more time |
| Radius+ | bigger area | more blocks |
| Power+ | stronger main effect (damage, heal, shield, buff) | more % |
| Efficiency | costs less Mana / Stamina | less cost |
| Split | splits into 3 weaker copies (projectiles, lines) | stronger copies |
| Ricochet | bounces to more targets | +1 bounce |
| Pierce | passes through enemies | +1 enemy |
| Chain | jumps between nearby enemies or allies | +1 jump |
| Lingering | leaves a zone behind (fire, poison, light) | longer zone |
| Slow | adds a slow | stronger slow |
| Knockback+ | pushes enemies away | farther |
| Pull | draws enemies in | stronger pull |
| Follow | a placed zone moves with you instead | bigger zone |
| Leech | heals you for part of the damage | more % |
| Ward | adds a small shield (you, or allies for support abilities) | bigger shield |
| Haste | attack + move speed for a few seconds after use | longer |
| Echo | repeats once after 1 s at reduced strength | stronger echo |

## Warrior - tank (swords + spears; vanilla traversals)

| Slot | Ability | What it does | Modifier options |
|---|---|---|---|
| A1 **LOCKED** | **Rallying Guard** | You + party within 6 blocks take less damage for 6 s; mobs within 8 blocks turn to attack you | Duration+, Radius+, Power+, Ward |
| A1-alt A *proposed* | **Bulwark Stance** | Stance: you take far less damage from the front and block projectiles, move slower; allies behind you take less too | Duration+, Power+, Knockback+, Ward |
| A1-alt B *proposed* | **Unbreakable** | Taunt + for 5 s you cannot drop below 1 HP, then heal 20% of the damage you took during it | Duration+, Radius+, Leech, Power+ |
| A2 **LOCKED** | **Shield Shockwave** | Cone slam that stuns enemies ~1.5 s | Radius+, Knockback+, Slow, Power+ |
| A2-alt *proposed* | **Iron Chain** | Hook an enemy and drag it to you + short stun (peel mobs off allies, pull archers) | Pull, Chain, Slow, Power+ |

## Archer - crowd control (shortbows + crossbows; vanilla traversals)

| Slot | Ability | What it does | Modifier options |
|---|---|---|---|
| A1 **LOCKED** | **Pinning Shot** | Piercing arrow: enemies hit are Rooted ~2 s and Marked (take more damage) | Pierce, Split, Duration+, Power+ |
| A1-alt A *proposed* | **Arrow Rain** | Arrows rain on an area: enemies inside are Slowed, then Rooted + Marked if they stay | Radius+, Duration+, Lingering, Power+ |
| A1-alt B *proposed* | **Hunter's Net** | A net shot that bursts into a root zone for 3 s and Marks for 8 s | Radius+, Duration+, Pull, Split |
| A2 **LOCKED** | **Rapid Fire** | 15 arrows in 3 s | Ricochet, Pierce, Duration+, Slow |
| A2-alt **LOCKED** | **Explosive Arrow** | Your next charged shot does 2x damage in an explosive AoE | Radius+, Split, Lingering, Knockback+ |

## Mage - burst damage, glass cannon (staffs + spellbooks; Teleport + light trail / Levitate)

| Slot | Ability | What it does | Modifier options |
|---|---|---|---|
| A1 **LOCKED** | **Meteor** | After 1 s, a big blast at the target (radius ~4) | Radius+, Power+, Lingering, Split |
| A1-alt A *proposed* | **Starfall** | 3 s barrage of falling stars over an area - more total damage, spread out | Duration+, Radius+, Echo, Power+ |
| A1-alt B *proposed* | **Arcane Beam** | Channel a beam that ramps up for 3 s - huge single-target burst, pierces | Pierce, Duration+, Power+, Slow |
| A2 **LOCKED** | **Mana Barrier** | For 6 s damage you take drains Mana instead of Health | Duration+, Power+, Ward, Knockback+ |
| A2-alt *proposed* | **Frost Nova** | Freeze enemies around you ~2 s, then Chill them (an escape by control) | Radius+, Duration+, Slow, Power+ |

## Priest - healer (wands + soul orb; backward hop + healing orb / Wings of Fate)

| Slot | Ability | What it does | Modifier options |
|---|---|---|---|
| A1 **LOCKED** | **Sacred Heal** | AoE heal (9 blocks); you heal 20% more; everyone inside gets a heal-over-time worth a % of the heal (Cleanse = a class-tree upgrade) | Radius+, Power+, Duration+, Efficiency |
| A1-alt A *proposed* | **Sanctuary** | A holy zone for 8 s: allies inside heal every second and take less damage | Radius+, Duration+, Follow, Power+ |
| A1-alt B *proposed* | **Martyr's Grace** | Big instant heal on the lowest-health ally in range that chains to more allies | Chain, Power+, Ward, Efficiency |
| A2 **LOCKED** | **Shield Bubble** | A placed bubble with HP that protects everyone inside; it can break | Follow (LOCKED), Radius+, Power+, Duration+ |
| A2-alt *proposed* | **Guardian Spirit** | Mark an ally: if they would die in the next 10 s, they survive at 30% HP instead | Duration+, Power+, Chain, Efficiency |

## Berserker - damage buffer (axes + maces / clubs; vanilla traversals)

| Slot | Ability | What it does | Modifier options |
|---|---|---|---|
| A1 **LOCKED** | **Enrage** | Party damage buff, yours bigger; grows 10 s, holds 5 s, ends abruptly | Duration+, Radius+, Power+, Leech |
| A1-alt A *proposed* | **Blood Frenzy** | The rage grows with every hit you land instead of over time; ends 5 s after your last hit | Duration+, Power+, Leech, Haste |
| A1-alt B *proposed* | **Warlord's Banner** | Plant a banner for 15 s: the party near it gets the damage buff, you get more near it | Radius+, Duration+, Power+, Ward |
| A2 **LOCKED** | **Whirlwind** | Spinning AoE with life steal | Duration+, Radius+, Pull, Leech |
| A2-alt *proposed* | **Earthsplitter** | Slam a shockwave line forward that knocks up enemies; hits harder the lower your health | Power+, Split, Slow, Knockback+ |

## Monk - self-speed disruptor (Bo staff + fist weapons; pole-vault skipping / Rising Strike)

| Slot | Ability | What it does | Modifier options |
|---|---|---|---|
| A1 **LOCKED** | **Flowing Form** | You gain flat speed + attack speed; enemies in your aura are Awed; each hit = a combo that slows them and lowers their defence; at 15 combo your buff doubles; 30 s, drains Mana + Stamina | Duration+, Radius+, Efficiency, Power+ |
| A1-alt A *proposed* | **Hundred Fists** | Flowing Form where every 10 combo releases a shockwave on all Awed enemies | Power+, Radius+, Echo, Efficiency |
| A1-alt B *proposed* | **Still Water** | A calm stance: you deflect projectiles and counter melee hits; Awe still builds | Duration+, Power+, Knockback+, Ward |
| A2 **LOCKED** | **Palm Strike** | Cheap quick single-target stun with knockback - spammable | Knockback+, Ricochet, Slow, Power+ |
| A2-alt *proposed* | **Cyclone Kick** | A quick spinning kick that hits everything around you and pushes it out | Radius+, Knockback+, Slow, Haste |

## Assassin - priority killer (daggers + kunai; vanilla dagger move / kunai throw-teleport + return)

| Slot | Ability | What it does | Modifier options |
|---|---|---|---|
| A1 **LOCKED** | **Cloak + First Strike** | Invisible for a while; your next hit gets +100% crit chance even after the cloak ends (crit cap 150%, triple crit above 200%) | Duration+, Efficiency, Power+, Haste |
| A1-alt A *proposed* | **Shadow Clone** | Cloak and leave a decoy that mobs attack (needs mob targeting - engine check) | Duration+, Power+, Split, Knockback+ |
| A1-alt B *proposed* | **Vanishing Act** | Instant short cloak + a smoke cloud that makes enemies lose track of you; First Strike | Radius+, Duration+, Slow, Efficiency |
| A2 **LOCKED** | **Toxin** | Poison cloud that Weakens enemies | Radius+, Duration+, Lingering, Chain |
| A2-alt **LOCKED** | **God Killer** | Next attack on a boss / mini-boss does 2x, 3x as a backstab; stacks with First Strike | Power+, Duration+, Efficiency, Haste |

## Next to refine

- Skyy picks / renames the *proposed* rows (Warrior, Archer, Mage, Priest, Berserker, Monk A1-alt pairs + A2-alts).
- Class-tree PATHS per class (Wynncraft-style, locking) once the abilities settle.
- Engine checks for the ideas that need them: Shadow Clone (mob targeting), Unbreakable (no-death window), Guardian Spirit (death
  prevention), Iron Chain (pulling a mob), Mana Barrier (damage to Mana), beams / zones / shields.
