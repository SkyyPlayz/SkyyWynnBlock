# Class trees v4 - every node's new place (generated: python tools/trees_v3_data.py --v4md; do not edit by hand)

Made by round R0 of `research/Combat-Into-Class-Spec.md` (SkyyTrees 0.6.0). Where answers go: Skyy's changes to a placement ->
`docs/answered/classes.md`; the data -> `tools/trees_v3_data.py` (V4_PLACE / V4_RENAME / V4_FREE_PASSIVE). Every node keeps its
saved key (column Key); 1 point a class level; a row of a branch opens at 5 points spent IN THAT BRANCH per row + 3 in the row
above + class level 5 per row. Modifiers: 1 point unlocks one for its ability, then it levels by use.

| Class | Branch 1 | Branch 2 | Branch 3 | Ranks | Modifier unlocks | Share of the tree at Lv 100 (100 points) |
|---|---|---|---|---|---|---|
| Archer | Huntmaster 24 nodes / 37 ranks | Stormvolley 17 nodes / 31 ranks | Weaponcraft 30 nodes / 98 ranks | 166 | 22 | 60 % |
| Assassin | Shadowstep 19 nodes / 38 ranks | Venomcraft 20 nodes / 36 ranks | Weaponcraft 31 nodes / 102 ranks | 176 | 17 | 57 % |
| Berserker | Bloodlust 20 nodes / 31 ranks | Warpath 17 nodes / 31 ranks | Weaponcraft 25 nodes / 87 ranks | 149 | 23 | 67 % |
| Mage | Cosmos 25 nodes / 39 ranks | Spellward 20 nodes / 36 ranks | Weaponcraft 26 nodes / 87 ranks | 162 | 22 | 62 % |
| Monk | Flow 23 nodes / 43 ranks | Fist 14 nodes / 27 ranks | Weaponcraft 23 nodes / 80 ranks | 150 | 22 | 67 % |
| Priest | Devotion 31 nodes / 53 ranks | Bulwark 21 nodes / 37 ranks | Weaponcraft 24 nodes / 83 ranks | 173 | 23 | 58 % |
| Spellblade | Rift Cleave 22 nodes / 40 ranks | Imbue 15 nodes / 31 ranks | Weaponcraft 24 nodes / 81 ranks | 152 | 22 | 66 % |
| Warrior | Bulwark 17 nodes / 30 ranks | Shockwave 19 nodes / 40 ranks | Weaponcraft 28 nodes / 95 ranks | 165 | 20 | 61 % |

## Warrior

### Branch 1 - Bulwark (mitigation, max HP, standing your ground)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Rallying Guard** | ABILITY (free) | - | Warrior.b1.r1.free |  |
| 1 | Rallying Guard: Power | 1 | `Class.Warrior.b2.r1b` | Warrior.b2.r1b | Unlocks the Power modifier for Rallying Guard: put it in one of its 2 modifier slots - it levels up as you use Rallying Guard |
| 1 | Rallying Guard: Duration | 1 | `Class.Warrior.m.RallyingGuard.Duration` | new | Unlocks the Duration modifier for Rallying Guard: put it in one of its 2 modifier slots - it levels up as you use Rallying Guard |
| 1 | Rallying Guard: Echo | 1 | `Class.Warrior.m.RallyingGuard.Echo` | new | Unlocks the Echo modifier for Rallying Guard: put it in one of its 2 modifier slots - it levels up as you use Rallying Guard |
| 1 | Shield Allies | 5 | `Class.Warrior.b3.r1a` | Warrior.b3.r1a | Rallying Guard also shields allies 3% max HP per rank |
| 2 | **Challenge** | ABILITY (free) | - | Warrior.b1.r2.free |  |
| 2 | **Guardian's Oath** | ABILITY (free) | - | Warrior.b1.r5.free |  |
| 2 | Iron Skin | 5 | `Class.Warrior.b1.r1a` | Warrior.b1.r1a | -6% melee damage taken per rank |
| 2 | Rallying Guard: Radius | 1 | `Class.Warrior.b2.r1a` | Warrior.b2.r1a | Unlocks the Radius modifier for Rallying Guard: put it in one of its 2 modifier slots - it levels up as you use Rallying Guard |
| 2 | Last Stand | 3 | `Class.Warrior.b1.r1b` | Warrior.b1.r1b | +6% max HP per rank |
| 3 | Challenge: Duration | 1 | `Class.Warrior.b1.r2a` | Warrior.b1.r2a | Unlocks the Duration modifier for Challenge: put it in one of its 2 modifier slots - it levels up as you use Challenge |
| 3 | Challenge: Ward | 1 | `Class.Warrior.b1.r2b` | Warrior.b1.r2b | Unlocks the Ward modifier for Challenge: put it in one of its 2 modifier slots - it levels up as you use Challenge |
| 3 | Challenge: Power | 1 | `Class.Warrior.m.Challenge.Power` | new | Unlocks the Power modifier for Challenge: put it in one of its 2 modifier slots - it levels up as you use Challenge |
| 4 | Challenge: Chain | 1 | `Class.Warrior.m.Challenge.Chain` | new | Unlocks the Chain modifier for Challenge: put it in one of its 2 modifier slots - it levels up as you use Challenge |
| 4 | Guardian's Oath: Power | 1 | `Class.Warrior.m.GuardiansOath.Power` | new | Unlocks the Power modifier for Guardian's Oath: put it in one of its 2 modifier slots - it levels up as you use Guardian's Oath |
| 4 | Guardian's Oath: Radius | 1 | `Class.Warrior.m.GuardiansOath.Radius` | new | Unlocks the Radius modifier for Guardian's Oath: put it in one of its 2 modifier slots - it levels up as you use Guardian's Oath |
| 5 | Guardian's Oath: Ward | 1 | `Class.Warrior.m.GuardiansOath.Ward` | new | Unlocks the Ward modifier for Guardian's Oath: put it in one of its 2 modifier slots - it levels up as you use Guardian's Oath |
| 5 | Guardian's Oath: Duration | 1 | `Class.Warrior.b1.r5a` | Warrior.b1.r5a | Unlocks the Duration modifier for Guardian's Oath: put it in one of its 2 modifier slots - it levels up as you use Guardian's Oath |
| 5 | Warden's Aegis | 4 | `Class.Warrior.b3.r4b` | Warrior.b3.r4b | party wards from your abilities +4% per rank |
| 6 | Aegis Eternal | 1 | `Class.Warrior.b1.r6` | Warrior.b1.r6 | Challenge holds until its target dies (30s at most); while it holds, players within 6 blocks of you take 10% less damage, and your blocks slow attackers 40% for 2s |

### Branch 2 - Shockwave (AoE stuns and knockback)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | Concussion | 3 | `Class.Warrior.b2.r2b` | Warrior.b2.r2b | 12% chance per rank that a Shockwave hit stuns 1s longer |
| 1 | Daze | 5 | `Class.Warrior.b2.r3a` | Warrior.b2.r3a | Shockwave slows enemies 10% per rank for 3s |
| 1 | Arc Wave | 2 | `Class.Warrior.b2.r3b` | Warrior.b2.r3b | Shockwave arcs to 1 extra enemy per rank at 50% damage |
| 2 | **Shield Shockwave** | ABILITY (free) | - | Warrior.b2.r2.free |  |
| 2 | Shield Shockwave: Knockback | 1 | `Class.Warrior.b2.r2a` | Warrior.b2.r2a | Unlocks the Knockback modifier for Shield Shockwave: put it in one of its 2 modifier slots - it levels up as you use Shield Shockwave |
| 2 | Shield Shockwave: Radius | 1 | `Class.Warrior.m.ShieldShockwave.Radius` | new | Unlocks the Radius modifier for Shield Shockwave: put it in one of its 2 modifier slots - it levels up as you use Shield Shockwave |
| 2 | Shield Shockwave: Echo | 1 | `Class.Warrior.m.ShieldShockwave.Echo` | new | Unlocks the Echo modifier for Shield Shockwave: put it in one of its 2 modifier slots - it levels up as you use Shield Shockwave |
| 3 | Draining Links | 4 | `Class.Warrior.b3.r3b` | Warrior.b3.r3b | Iron Chain hits heal you 2% max HP per rank |
| 3 | Shield Shockwave: Power | 1 | `Class.Warrior.b2.r4b` | Warrior.b2.r4b | Unlocks the Power modifier for Shield Shockwave: put it in one of its 2 modifier slots - it levels up as you use Shield Shockwave |
| 3 | Long Stun | 4 | `Class.Warrior.b2.r4a` | Warrior.b2.r4a | Shockwave stuns +0.25s per rank |
| 4 | Fissure | 3 | `Class.Warrior.b2.r5a` | Warrior.b2.r5a | Shockwave radius +1 block per rank |
| 4 | Tremor | 2 | `Class.Warrior.b2.r5b` | Warrior.b2.r5b | shocked enemies take 15% of the hit per second per rank for 3s |
| 4 | Heavy Links | 4 | `Class.Warrior.b3.r5a` | Warrior.b3.r5a | Iron Chain damage +5% per rank |
| 5 | **Iron Chain** | ABILITY (free) | - | Warrior.b3.r2.free |  |
| 5 | Binding Grip | 3 | `Class.Warrior.b3.r5b` | Warrior.b3.r5b | Iron Chain stuns +0.3s per rank |
| 5 | Iron Chain: Chain | 1 | `Class.Warrior.b3.r1b` | Warrior.b3.r1b | Unlocks the Chain modifier for Iron Chain: put it in one of its 2 modifier slots - it levels up as you use Iron Chain |
| 5 | Iron Chain: Pull | 1 | `Class.Warrior.b3.r2a` | Warrior.b3.r2a | Unlocks the Pull modifier for Iron Chain: put it in one of its 2 modifier slots - it levels up as you use Iron Chain |
| 5 | Iron Chain: Slow | 1 | `Class.Warrior.b3.r4a` | Warrior.b3.r4a | Unlocks the Slow modifier for Iron Chain: put it in one of its 2 modifier slots - it levels up as you use Iron Chain |
| 5 | Iron Chain: Power | 1 | `Class.Warrior.m.IronChain.Power` | new | Unlocks the Power modifier for Iron Chain: put it in one of its 2 modifier slots - it levels up as you use Iron Chain |
| 5 | Warden's Grip | 1 | `Class.Warrior.b3.r6` | Warrior.b3.r6 | Iron Chain also yanks every enemy within 8 blocks to you and roots them 2s, and wards your party for 10% of max Health |
| 6 | Rumble | 1 | `Class.Warrior.b2.r6` | Warrior.b2.r6 | while your Challenge holds, Shield Shockwave fires by itself every 5s for free (a shield in hand or off-hand) and stuns at least 1.5s |

### Branch 3 - Weaponcraft (weapons, defence, loot)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Combat Focus** | free passive | - | Combat.b1.r1.free | +3% damage |
| 1 | Hone Edge | 5 | `Skill.Combat.b1.r1a` | Combat.b1.r1a | +2% weapon damage/rank |
| 1 | Toughness | 5 | `Skill.Combat.b2.r1a` | Combat.b2.r1a | +0.5% max Health/rank |
| 1 | Scavenger | 5 | `Skill.Combat.b3.r1a` | Combat.b3.r1a | +2% chance/rank a kill drops 1 more item of its loot (never gear) |
| 1 | Coin Purse | 3 | `Skill.Combat.b3.r1b` | Combat.b3.r1b | 3% chance/rank a kill also pays coins (the mob's level) |
| 2 | **Hardy** | free passive | - | Warrior.b1.r1a | -2% melee damage taken (always on) |
| 2 | Weak Spot | 3 | `Skill.Combat.b1.r1b` | Combat.b1.r1b | +2% crit chance/rank |
| 2 | Iron Will | 3 | `Skill.Combat.b2.r1b` | Combat.b2.r1b | +3% knockback resistance/rank |
| 2 | Momentum | 4 | `Skill.Combat.b1.r3b` | Combat.b1.r3b | +1% move speed/rank |
| 2 | Rally | 3 | `Skill.Combat.b2.r4b` | Combat.b2.r4b | +3% Health regen out of combat per rank |
| 2 | Stone Guard | 3 | `Class.Warrior.b1.r3b` | Warrior.b1.r3b | -4.5% ranged damage taken per rank |
| 3 | Finisher | 3 | `Skill.Combat.b1.r3a` | Combat.b1.r3a | +4% damage/rank to enemies below 30% Health |
| 3 | Thick Skin | 4 | `Skill.Combat.b2.r3a` | Combat.b2.r3a | +2% damage reduction/rank |
| 3 | Pet Fang | 5 | `Skill.Combat.b3.r3a` | Combat.b3.r3a | +2% combat XP and +1% damage per equipped Combat pet tier, per rank |
| 3 | Rare Drop | 3 | `Skill.Combat.b3.r3b` | Combat.b3.r3b | +1% chance/rank a kill drops 1 more of its rarest loot (never gear) |
| 3 | Reprisal | 3 | `Skill.Combat.b2.r3b` | Combat.b2.r3b | 3% of the melee damage you take is dealt back to the attacker per rank |
| 3 | Heavy Blows | 3 | `Class.Warrior.b1.r3a` | Warrior.b1.r3a | melee hits knock enemies back 0.5 blocks per rank |
| 4 | Crit Mastery | 3 | `Skill.Combat.b1.r4a` | Combat.b1.r4a | +3% crit damage/rank |
| 4 | Gear Resonance | 3 | `Skill.Combat.b1.r4b` | Combat.b1.r4b | +2% damage per combat-tagged armor piece/rank |
| 4 | Accessory Plates | 3 | `Skill.Combat.b2.r4a` | Combat.b2.r4a | +0.5% max health per filled accessory slot, per rank |
| 4 | Boss Hunter | 3 | `Skill.Combat.b3.r4a` | Combat.b3.r4a | +3% chance/rank a boss or mini boss drops its loot once more (never gear) |
| 4 | Shield Bash | 4 | `Class.Warrior.b1.r4a` | Warrior.b1.r4a | an enemy whose hit you block is slowed 12% per rank for 2s |
| 4 | Mending Guard | 2 | `Class.Warrior.b1.r4b` | Warrior.b1.r4b | blocking a hit heals 1% max HP per rank |
| 5 | **Stalwart** | free passive | - | Warrior.b1.r1b | +3% max Health (always on) |
| 5 | Trophy Hunter | 3 | `Skill.Combat.b1.r5a` | Combat.b1.r5a | +3% damage/rank to bosses and mini bosses |
| 5 | Weapon Tempering | 4 | `Skill.Combat.b1.r5b` | Combat.b1.r5b | +1% damage per metal tier above Iron per rank (max +20%) |
| 5 | Lucky Kill | 3 | `Skill.Combat.b3.r5a` | Combat.b3.r5a | 2% chance/rank a kill drops its whole loot twice (never gear) |
| 5 | Battle Insight | 5 | `Skill.Combat.b3.r5b` | Combat.b3.r5b | +2% class XP/rank |
| 5 | Second Wind | 3 | `Skill.Combat.b2.r3c` | Combat.b2.r3c | once a fight, a hit that drops you below 20% Health heals you 5% of max Health per rank |
| 5 | Anchor | 3 | `Class.Warrior.b1.r5b` | Warrior.b1.r5b | -4.5% damage taken per rank while you stand still |
| 6 | Edge of the Legend | 1 | `Skill.Combat.b1.r6` | Combat.b1.r6 | +10% damage to enemies below 30% Health |

Second modifier nodes folded into the one unlock node (their ranks are refunded; the modifier level they gave is kept by its use count): `Class.Warrior.b3.r3a` (IronChain Chain, 2 ranks)

## Berserker

### Branch 1 - Bloodlust (leech, adrenaline, self-sustain)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Enrage** | ABILITY (free) | - | Berserker.b1.r1.free |  |
| 1 | Enrage: Leech | 1 | `Class.Berserker.b1.r1a` | Berserker.b1.r1a | Unlocks the Leech modifier for Enrage: put it in one of its 2 modifier slots - it levels up as you use Enrage |
| 1 | Enrage: Radius | 1 | `Class.Berserker.b2.r1b` | Berserker.b2.r1b | Unlocks the Radius modifier for Enrage: put it in one of its 2 modifier slots - it levels up as you use Enrage |
| 1 | Enrage: Duration | 1 | `Class.Berserker.m.Enrage.Duration` | new | Unlocks the Duration modifier for Enrage: put it in one of its 2 modifier slots - it levels up as you use Enrage |
| 1 | Brute Force | 5 | `Class.Berserker.b3.r1b` | Berserker.b3.r1b | +4.5% melee damage per rank |
| 2 | **Blood Frenzy** | ABILITY (free) | - | Berserker.b1.r2.free |  |
| 2 | **Warlord's Banner** | ABILITY (free) | - | Berserker.b2.r2.free |  |
| 2 | Blood Frenzy: Duration | 1 | `Class.Berserker.b1.r2a` | Berserker.b1.r2a | Unlocks the Duration modifier for Blood Frenzy: put it in one of its 2 modifier slots - it levels up as you use Blood Frenzy |
| 2 | Blood Frenzy: Leech | 1 | `Class.Berserker.b1.r2b` | Berserker.b1.r2b | Unlocks the Leech modifier for Blood Frenzy: put it in one of its 2 modifier slots - it levels up as you use Blood Frenzy |
| 2 | Warlord's Banner: Duration | 1 | `Class.Berserker.b2.r2a` | Berserker.b2.r2a | Unlocks the Duration modifier for Warlord's Banner: put it in one of its 2 modifier slots - it levels up as you use Warlord's Banner |
| 2 | Warlord's Banner: Power | 1 | `Class.Berserker.b2.r2b` | Berserker.b2.r2b | Unlocks the Power modifier for Warlord's Banner: put it in one of its 2 modifier slots - it levels up as you use Warlord's Banner |
| 3 | Blood Frenzy: Floor | 1 | `Class.Berserker.m.BloodFrenzy.Floor` | new | Unlocks the Floor modifier for Blood Frenzy: put it in one of its 2 modifier slots - it levels up as you use Blood Frenzy |
| 3 | Blood Frenzy: Power | 1 | `Class.Berserker.m.BloodFrenzy.Power` | new | Unlocks the Power modifier for Blood Frenzy: put it in one of its 2 modifier slots - it levels up as you use Blood Frenzy |
| 3 | Warlord's Banner: Ward | 1 | `Class.Berserker.b2.r3b` | Berserker.b2.r3b | Unlocks the Ward modifier for Warlord's Banner: put it in one of its 2 modifier slots - it levels up as you use Warlord's Banner |
| 3 | War March | 4 | `Class.Berserker.b2.r3a` | Berserker.b2.r3a | your banner gives everyone inside +3% move speed per rank (swing speed is fixed per weapon) |
| 4 | Enrage: Power | 1 | `Class.Berserker.b1.r4a` | Berserker.b1.r4a | Unlocks the Power modifier for Enrage: put it in one of its 2 modifier slots - it levels up as you use Enrage |
| 4 | Blood Frenzy: Haste | 1 | `Class.Berserker.b1.r4b` | Berserker.b1.r4b | Unlocks the Haste modifier for Blood Frenzy: put it in one of its 2 modifier slots - it levels up as you use Blood Frenzy |
| 4 | Warlord's Banner: Radius | 1 | `Class.Berserker.b2.r4a` | Berserker.b2.r4a | Unlocks the Radius modifier for Warlord's Banner: put it in one of its 2 modifier slots - it levels up as you use Warlord's Banner |
| 4 | Rending Rhythm | 2 | `Class.Berserker.b1.r3a` | Berserker.b1.r3a | every 5th melee hit repeats at 40% damage per rank |
| 5 | Blood Price | 4 | `Class.Berserker.b2.r5a` | Berserker.b2.r5a | allies inside Banner leech 1% of damage dealt per rank |
| 5 | Warlord's Banner: Echo | 1 | `Class.Berserker.b2.r4b` | Berserker.b2.r4b | Unlocks the Echo modifier for Warlord's Banner: put it in one of its 2 modifier slots - it levels up as you use Warlord's Banner |
| 5 | Warlord's Domain | 1 | `Class.Berserker.b2.r6` | Berserker.b2.r6 | your banner follows you and never falls (60% strength); kills inside it add 2s to your Enrage and Blood Frenzy |
| 6 | Crimson Eternal | 1 | `Class.Berserker.b1.r6` | Berserker.b1.r6 | Blood Frenzy's stacks never fade while you hit something every 3s; leech that would overheal becomes a ward (up to 10% max Health) |

### Branch 2 - Warpath (AoE melee, spin-to-win, stamina)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | Adrenaline | 3 | `Class.Berserker.b1.r1b` | Berserker.b1.r1b | +6% damage per rank while below 60% Health (swing speed is fixed per weapon) |
| 1 | Cleaving Blows | 3 | `Class.Berserker.b3.r1a` | Berserker.b3.r1a | melee hits cleave the nearest other enemy within 3 blocks for 15% damage per rank |
| 1 | Lashing Spin | 2 | `Class.Berserker.b3.r2b` | Berserker.b3.r2b | each Whirlwind pulse also strikes 1 more enemy per rank within 6 blocks at 50% |
| 2 | **Whirlwind** | ABILITY (free) | - | Berserker.b3.r2.free |  |
| 2 | Whirlwind: Radius | 1 | `Class.Berserker.b3.r2a` | Berserker.b3.r2a | Unlocks the Radius modifier for Whirlwind: put it in one of its 2 modifier slots - it levels up as you use Whirlwind |
| 2 | Whirlwind: Pull | 1 | `Class.Berserker.m.Whirlwind.Pull` | new | Unlocks the Pull modifier for Whirlwind: put it in one of its 2 modifier slots - it levels up as you use Whirlwind |
| 2 | Whirlwind: Leech | 1 | `Class.Berserker.m.Whirlwind.Leech` | new | Unlocks the Leech modifier for Whirlwind: put it in one of its 2 modifier slots - it levels up as you use Whirlwind |
| 3 | Whirlwind: Echo | 1 | `Class.Berserker.m.Whirlwind.Echo` | new | Unlocks the Echo modifier for Whirlwind: put it in one of its 2 modifier slots - it levels up as you use Whirlwind |
| 3 | Fierce Spin | 4 | `Class.Berserker.b3.r3a` | Berserker.b3.r3a | Whirlwind spins harder: +8% damage per rank |
| 4 | Whirlwind: Duration | 1 | `Class.Berserker.b3.r4b` | Berserker.b3.r4b | Unlocks the Duration modifier for Whirlwind: put it in one of its 2 modifier slots - it levels up as you use Whirlwind |
| 4 | Dizzying Spin | 3 | `Class.Berserker.b3.r3b` | Berserker.b3.r3b | Whirlwind hits slow 8% per rank |
| 5 | **Earthsplitter** | ABILITY (free) | - | Berserker.b3.r5.free |  |
| 5 | Bleeding Edge | 3 | `Class.Berserker.b3.r4a` | Berserker.b3.r4a | Whirlwind hits make enemies bleed 15% of the hit per second per rank for 3s |
| 5 | Earthsplitter: Knockback | 1 | `Class.Berserker.b3.r5a` | Berserker.b3.r5a | Unlocks the Knockback modifier for Earthsplitter: put it in one of its 2 modifier slots - it levels up as you use Earthsplitter |
| 5 | Earthsplitter: Power | 1 | `Class.Berserker.m.Earthsplitter.Power` | new | Unlocks the Power modifier for Earthsplitter: put it in one of its 2 modifier slots - it levels up as you use Earthsplitter |
| 5 | Earthsplitter: Split | 1 | `Class.Berserker.m.Earthsplitter.Split` | new | Unlocks the Split modifier for Earthsplitter: put it in one of its 2 modifier slots - it levels up as you use Earthsplitter |
| 5 | Earthsplitter: Slow | 1 | `Class.Berserker.m.Earthsplitter.Slow` | new | Unlocks the Slow modifier for Earthsplitter: put it in one of its 2 modifier slots - it levels up as you use Earthsplitter |
| 5 | Earthblood | 3 | `Class.Berserker.b3.r5b` | Berserker.b3.r5b | Earthsplitter hits heal 2% max HP per rank |
| 6 | Endless Fury | 1 | `Class.Berserker.b3.r6` | Berserker.b3.r6 | Whirlwind becomes a toggle (cast again to stop, 30s max): it moves with you at 70% speed, and each full spin that hits gives back 5 Stamina |

### Branch 3 - Weaponcraft (weapons, defence, loot)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Combat Focus** | free passive | - | Combat.b1.r1.free | +3% damage |
| 1 | Hone Edge | 5 | `Skill.Combat.b1.r1a` | Combat.b1.r1a | +2% weapon damage/rank |
| 1 | Toughness | 5 | `Skill.Combat.b2.r1a` | Combat.b2.r1a | +0.5% max Health/rank |
| 1 | Scavenger | 5 | `Skill.Combat.b3.r1a` | Combat.b3.r1a | +2% chance/rank a kill drops 1 more item of its loot (never gear) |
| 1 | Coin Purse | 3 | `Skill.Combat.b3.r1b` | Combat.b3.r1b | 3% chance/rank a kill also pays coins (the mob's level) |
| 2 | **Bloodied** | free passive | - | Berserker.b1.r1b | +3% damage while below 60% Health (always on) |
| 2 | Weak Spot | 3 | `Skill.Combat.b1.r1b` | Combat.b1.r1b | +2% crit chance/rank |
| 2 | Iron Will | 3 | `Skill.Combat.b2.r1b` | Combat.b2.r1b | +3% knockback resistance/rank |
| 2 | Momentum | 4 | `Skill.Combat.b1.r3b` | Combat.b1.r3b | +1% move speed/rank |
| 2 | Rally | 3 | `Skill.Combat.b2.r4b` | Combat.b2.r4b | +3% Health regen out of combat per rank |
| 3 | Finisher | 3 | `Skill.Combat.b1.r3a` | Combat.b1.r3a | +4% damage/rank to enemies below 30% Health |
| 3 | Thick Skin | 4 | `Skill.Combat.b2.r3a` | Combat.b2.r3a | +2% damage reduction/rank |
| 3 | Pet Fang | 5 | `Skill.Combat.b3.r3a` | Combat.b3.r3a | +2% combat XP and +1% damage per equipped Combat pet tier, per rank |
| 3 | Rare Drop | 3 | `Skill.Combat.b3.r3b` | Combat.b3.r3b | +1% chance/rank a kill drops 1 more of its rarest loot (never gear) |
| 3 | Reprisal | 3 | `Skill.Combat.b2.r3b` | Combat.b2.r3b | 3% of the melee damage you take is dealt back to the attacker per rank |
| 3 | Thirst | 3 | `Class.Berserker.b1.r3b` | Berserker.b1.r3b | kills heal 2% max HP per rank |
| 4 | Crit Mastery | 3 | `Skill.Combat.b1.r4a` | Combat.b1.r4a | +3% crit damage/rank |
| 4 | Gear Resonance | 3 | `Skill.Combat.b1.r4b` | Combat.b1.r4b | +2% damage per combat-tagged armor piece/rank |
| 4 | Accessory Plates | 3 | `Skill.Combat.b2.r4a` | Combat.b2.r4a | +0.5% max health per filled accessory slot, per rank |
| 4 | Boss Hunter | 3 | `Skill.Combat.b3.r4a` | Combat.b3.r4a | +3% chance/rank a boss or mini boss drops its loot once more (never gear) |
| 5 | **Brutal** | free passive | - | Berserker.b3.r1b | +3% melee damage (always on) |
| 5 | Trophy Hunter | 3 | `Skill.Combat.b1.r5a` | Combat.b1.r5a | +3% damage/rank to bosses and mini bosses |
| 5 | Weapon Tempering | 4 | `Skill.Combat.b1.r5b` | Combat.b1.r5b | +1% damage per metal tier above Iron per rank (max +20%) |
| 5 | Lucky Kill | 3 | `Skill.Combat.b3.r5a` | Combat.b3.r5a | 2% chance/rank a kill drops its whole loot twice (never gear) |
| 5 | Battle Insight | 5 | `Skill.Combat.b3.r5b` | Combat.b3.r5b | +2% class XP/rank |
| 5 | Second Wind | 3 | `Skill.Combat.b2.r3c` | Combat.b2.r3c | once a fight, a hit that drops you below 20% Health heals you 5% of max Health per rank |
| 5 | Red Mist | 4 | `Class.Berserker.b1.r5a` | Berserker.b1.r5a | leech effectiveness +50% per rank below 30% HP |
| 6 | Edge of the Legend | 1 | `Skill.Combat.b1.r6` | Combat.b1.r6 | +10% damage to enemies below 30% Health |

Second modifier nodes folded into the one unlock node (their ranks are refunded; the modifier level they gave is kept by its use count): `Class.Berserker.b1.r5b` (BloodFrenzy Duration, 1 ranks), `Class.Berserker.b2.r1a` (Enrage Power, 1 ranks), `Class.Berserker.b2.r5b` (WarlordsBanner Power, 2 ranks)

## Spellblade

### Branch 1 - Rift Cleave (close-range elemental arcs)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Arcane Breach** | ABILITY (free) | - | Spellblade.b1.r1.free |  |
| 1 | Arcane Breach: Power | 1 | `Class.Spellblade.b1.r1a` | Spellblade.b1.r1a | Unlocks the Power modifier for Arcane Breach: put it in one of its 2 modifier slots - it levels up as you use Arcane Breach |
| 1 | Arcane Breach: Radius | 1 | `Class.Spellblade.b1.r1b` | Spellblade.b1.r1b | Unlocks the Radius modifier for Arcane Breach: put it in one of its 2 modifier slots - it levels up as you use Arcane Breach |
| 1 | Arcane Breach: Duration | 1 | `Class.Spellblade.b2.r1b` | Spellblade.b2.r1b | Unlocks the Duration modifier for Arcane Breach: put it in one of its 2 modifier slots - it levels up as you use Arcane Breach |
| 1 | Arcane Breach: Chain | 1 | `Class.Spellblade.m.ArcaneBreach.Chain` | new | Unlocks the Chain modifier for Arcane Breach: put it in one of its 2 modifier slots - it levels up as you use Arcane Breach |
| 1 | Arcing Rift | 3 | `Class.Spellblade.b1.r2b` | Spellblade.b1.r2b | Cleave arcs to 1 extra enemy per rank at 50% damage |
| 2 | **Rift Cleave** | ABILITY (free) | - | Spellblade.b1.r2.free |  |
| 2 | **Shattering Arc** | ABILITY (free) | - | Spellblade.b2.r2.free |  |
| 2 | Rift Cleave: Radius | 1 | `Class.Spellblade.b1.r2a` | Spellblade.b1.r2a | Unlocks the Radius modifier for Rift Cleave: put it in one of its 2 modifier slots - it levels up as you use Rift Cleave |
| 2 | Shattering Arc: Power | 1 | `Class.Spellblade.b2.r2a` | Spellblade.b2.r2a | Unlocks the Power modifier for Shattering Arc: put it in one of its 2 modifier slots - it levels up as you use Shattering Arc |
| 2 | Rift Cleave: Echo | 1 | `Class.Spellblade.m.RiftCleave.Echo` | new | Unlocks the Echo modifier for Rift Cleave: put it in one of its 2 modifier slots - it levels up as you use Rift Cleave |
| 2 | Shattering Arc: Radius | 1 | `Class.Spellblade.m.ShatteringArc.Radius` | new | Unlocks the Radius modifier for Shattering Arc: put it in one of its 2 modifier slots - it levels up as you use Shattering Arc |
| 3 | Shattering Arc: Knockback | 1 | `Class.Spellblade.m.ShatteringArc.Knockback` | new | Unlocks the Knockback modifier for Shattering Arc: put it in one of its 2 modifier slots - it levels up as you use Shattering Arc |
| 3 | Shattering Arc: Echo | 1 | `Class.Spellblade.m.ShatteringArc.Echo` | new | Unlocks the Echo modifier for Shattering Arc: put it in one of its 2 modifier slots - it levels up as you use Shattering Arc |
| 3 | Rift Cleave: Slow | 1 | `Class.Spellblade.b1.r3a` | Spellblade.b1.r3a | Unlocks the Slow modifier for Rift Cleave: put it in one of its 2 modifier slots - it levels up as you use Rift Cleave |
| 3 | Lasting Arc | 5 | `Class.Spellblade.b2.r2b` | Spellblade.b2.r2b | Arc debuff lasts +1s per rank |
| 4 | Rift Cleave: Power | 1 | `Class.Spellblade.b1.r3b` | Spellblade.b1.r3b | Unlocks the Power modifier for Rift Cleave: put it in one of its 2 modifier slots - it levels up as you use Rift Cleave |
| 4 | Shattering Arc: Leech | 1 | `Class.Spellblade.b2.r3b` | Spellblade.b2.r3b | Unlocks the Leech modifier for Shattering Arc: put it in one of its 2 modifier slots - it levels up as you use Shattering Arc |
| 4 | Rift Cleave: Duration | 1 | `Class.Spellblade.b1.r4a` | Spellblade.b1.r4a | Unlocks the Duration modifier for Rift Cleave: put it in one of its 2 modifier slots - it levels up as you use Rift Cleave |
| 4 | Wide Arc | 3 | `Class.Spellblade.b3.r3b` | Spellblade.b3.r3b | Shattering Arc reaches +0.5 blocks per rank |
| 5 | Lean Rifts | 3 | `Class.Spellblade.b1.r4b` | Spellblade.b1.r4b | Rift Cleave mana cost -5% per rank |
| 5 | Rift Push | 3 | `Class.Spellblade.b1.r5a` | Spellblade.b1.r5a | rifts push enemies 0.5 blocks per rank |
| 5 | Riptide | 3 | `Class.Spellblade.b1.r5b` | Spellblade.b1.r5b | rifts grant +1 Momentum per cast per rank |
| 5 | Resonant Arc | 5 | `Class.Spellblade.b3.r5a` | Spellblade.b3.r5a | Shattering Arc hits strike again for 10% per rank |
| 6 | Riftmaw | 1 | `Class.Spellblade.b1.r6` | Spellblade.b1.r6 | Rift Cleave always tears a second rift right after the first (60% strength); each cast grants +2 Momentum |

### Branch 2 - Imbue (Momentum engine)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | Momentum Strikes | 5 | `Class.Spellblade.b3.r1a` | Spellblade.b3.r1a | melee hits grant 1 Momentum at 12% chance per rank |
| 2 | **Elemental Imbue** | ABILITY (free) | - | Spellblade.b3.r2.free |  |
| 2 | Elemental Imbue: Duration | 1 | `Class.Spellblade.b3.r2a` | Spellblade.b3.r2a | Unlocks the Duration modifier for Elemental Imbue: put it in one of its 2 modifier slots - it levels up as you use Elemental Imbue |
| 2 | Frost Edge | 4 | `Class.Spellblade.b3.r4a` | Spellblade.b3.r4a | imbued hits slow 10% per rank for 2s |
| 3 | Elemental Imbue: Chain | 1 | `Class.Spellblade.m.ElementalImbue.Chain` | new | Unlocks the Chain modifier for Elemental Imbue: put it in one of its 2 modifier slots - it levels up as you use Elemental Imbue |
| 3 | Elemental Imbue: Efficiency | 1 | `Class.Spellblade.b3.r3a` | Spellblade.b3.r3a | Unlocks the Efficiency modifier for Elemental Imbue: put it in one of its 2 modifier slots - it levels up as you use Elemental Imbue |
| 3 | Sapping Mark | 4 | `Class.Spellblade.b2.r3a` | Spellblade.b2.r3a | Breached or Weakened enemies deal 4% less damage to you per rank |
| 4 | Elemental Imbue: Power | 1 | `Class.Spellblade.b3.r1b` | Spellblade.b3.r1b | Unlocks the Power modifier for Elemental Imbue: put it in one of its 2 modifier slots - it levels up as you use Elemental Imbue |
| 4 | Vital Edge | 3 | `Class.Spellblade.b3.r4b` | Spellblade.b3.r4b | imbued hits heal 1% max HP per rank |
| 5 | **Sunder** | ABILITY (free) | - | Spellblade.b2.r5.free |  |
| 5 | Contagious Mark | 3 | `Class.Spellblade.b2.r4a` | Spellblade.b2.r4a | on death the debuff spreads to 1 extra enemy per rank |
| 5 | Sunder: Power | 1 | `Class.Spellblade.b2.r5a` | Spellblade.b2.r5a | Unlocks the Power modifier for Sunder: put it in one of its 2 modifier slots - it levels up as you use Sunder |
| 5 | Sunder: Duration | 1 | `Class.Spellblade.b2.r5b` | Spellblade.b2.r5b | Unlocks the Duration modifier for Sunder: put it in one of its 2 modifier slots - it levels up as you use Sunder |
| 5 | Sunder: Chain | 1 | `Class.Spellblade.m.Sunder.Chain` | new | Unlocks the Chain modifier for Sunder: put it in one of its 2 modifier slots - it levels up as you use Sunder |
| 5 | Sunder: Echo | 1 | `Class.Spellblade.m.Sunder.Echo` | new | Unlocks the Echo modifier for Sunder: put it in one of its 2 modifier slots - it levels up as you use Sunder |
| 5 | Long Fractures | 3 | `Class.Spellblade.b2.r4b` | Spellblade.b2.r4b | Arcane Breach, Shattering Arc and Sunder last +2s per rank |
| 6 | Fracture | 1 | `Class.Spellblade.b2.r6` | Spellblade.b2.r6 | Sunder's cooldown is halved, and Shattering Arc deals +50% to Sundered enemies |

### Branch 3 - Weaponcraft (weapons, defence, loot)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Combat Focus** | free passive | - | Combat.b1.r1.free | +3% damage |
| 1 | Hone Edge | 5 | `Skill.Combat.b1.r1a` | Combat.b1.r1a | +2% weapon damage/rank |
| 1 | Toughness | 5 | `Skill.Combat.b2.r1a` | Combat.b2.r1a | +0.5% max Health/rank |
| 1 | Scavenger | 5 | `Skill.Combat.b3.r1a` | Combat.b3.r1a | +2% chance/rank a kill drops 1 more item of its loot (never gear) |
| 1 | Coin Purse | 3 | `Skill.Combat.b3.r1b` | Combat.b3.r1b | 3% chance/rank a kill also pays coins (the mob's level) |
| 2 | **Battle Rhythm** | free passive | - | Spellblade.b3.r1a | melee hits grant 1 Momentum at a 6% chance (always on) |
| 2 | Weak Spot | 3 | `Skill.Combat.b1.r1b` | Combat.b1.r1b | +2% crit chance/rank |
| 2 | Iron Will | 3 | `Skill.Combat.b2.r1b` | Combat.b2.r1b | +3% knockback resistance/rank |
| 2 | Momentum | 4 | `Skill.Combat.b1.r3b` | Combat.b1.r3b | +1% move speed/rank |
| 2 | Rally | 3 | `Skill.Combat.b2.r4b` | Combat.b2.r4b | +3% Health regen out of combat per rank |
| 3 | Finisher | 3 | `Skill.Combat.b1.r3a` | Combat.b1.r3a | +4% damage/rank to enemies below 30% Health |
| 3 | Thick Skin | 4 | `Skill.Combat.b2.r3a` | Combat.b2.r3a | +2% damage reduction/rank |
| 3 | Pet Fang | 5 | `Skill.Combat.b3.r3a` | Combat.b3.r3a | +2% combat XP and +1% damage per equipped Combat pet tier, per rank |
| 3 | Rare Drop | 3 | `Skill.Combat.b3.r3b` | Combat.b3.r3b | +1% chance/rank a kill drops 1 more of its rarest loot (never gear) |
| 3 | Reprisal | 3 | `Skill.Combat.b2.r3b` | Combat.b2.r3b | 3% of the melee damage you take is dealt back to the attacker per rank |
| 4 | Crit Mastery | 3 | `Skill.Combat.b1.r4a` | Combat.b1.r4a | +3% crit damage/rank |
| 4 | Gear Resonance | 3 | `Skill.Combat.b1.r4b` | Combat.b1.r4b | +2% damage per combat-tagged armor piece/rank |
| 4 | Accessory Plates | 3 | `Skill.Combat.b2.r4a` | Combat.b2.r4a | +0.5% max health per filled accessory slot, per rank |
| 4 | Boss Hunter | 3 | `Skill.Combat.b3.r4a` | Combat.b3.r4a | +3% chance/rank a boss or mini boss drops its loot once more (never gear) |
| 5 | **Arcane Ward** | free passive | - | Spellblade.b2.r3a | Breached or Weakened enemies deal 2% less damage to you (always on) |
| 5 | Trophy Hunter | 3 | `Skill.Combat.b1.r5a` | Combat.b1.r5a | +3% damage/rank to bosses and mini bosses |
| 5 | Weapon Tempering | 4 | `Skill.Combat.b1.r5b` | Combat.b1.r5b | +1% damage per metal tier above Iron per rank (max +20%) |
| 5 | Lucky Kill | 3 | `Skill.Combat.b3.r5a` | Combat.b3.r5a | 2% chance/rank a kill drops its whole loot twice (never gear) |
| 5 | Battle Insight | 5 | `Skill.Combat.b3.r5b` | Combat.b3.r5b | +2% class XP/rank |
| 5 | Second Wind | 3 | `Skill.Combat.b2.r3c` | Combat.b2.r3c | once a fight, a hit that drops you below 20% Health heals you 5% of max Health per rank |
| 5 | Edge of the Legend | 1 | `Skill.Combat.b1.r6` | Combat.b1.r6 | +10% damage to enemies below 30% Health |
| 6 | Arc Cascade | 1 | `Class.Spellblade.b3.r6` | Spellblade.b3.r6 | at full Momentum (20) your next ability is free, reaches +2 blocks and releases a 5-block nova of 10% of a hit per Momentum (all Momentum spent) |

Second modifier nodes folded into the one unlock node (their ranks are refunded; the modifier level they gave is kept by its use count): `Class.Spellblade.b2.r1a` (ArcaneBreach Power, 1 ranks), `Class.Spellblade.b3.r2b` (ElementalImbue Power, 1 ranks), `Class.Spellblade.b3.r5b` (ElementalImbue Power, 1 ranks)

## Monk

### Branch 1 - Flow (movement, stamina, afterimages)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Flowing Form** | ABILITY (free) | - | Monk.b1.r1.free |  |
| 1 | Calm Shell | 4 | `Class.Monk.b3.r1a` | Monk.b3.r1a | gain a 4% max HP ward when Flowing Form ends per rank |
| 1 | Flowing Form: Efficiency | 1 | `Class.Monk.m.FlowingForm.Efficiency` | new | Unlocks the Efficiency modifier for Flowing Form: put it in one of its 2 modifier slots - it levels up as you use Flowing Form |
| 1 | Flowing Form: Power | 1 | `Class.Monk.m.FlowingForm.Power` | new | Unlocks the Power modifier for Flowing Form: put it in one of its 2 modifier slots - it levels up as you use Flowing Form |
| 1 | Heavy Hands | 4 | `Class.Monk.b3.r1b` | Monk.b3.r1b | enemies you hit during Still Water are 10% slower per rank for 2s |
| 1 | Iron Knuckles | 4 | `Class.Monk.b1.r2a` | Monk.b1.r2a | +7.5% damage per rank while Hundred Fists runs (punch speed is fixed per weapon) |
| 2 | **Hundred Fists** | ABILITY (free) | - | Monk.b1.r2.free |  |
| 2 | **Still Water** | ABILITY (free) | - | Monk.b3.r2.free |  |
| 2 | Hundred Fists: Efficiency | 1 | `Class.Monk.b1.r2b` | Monk.b1.r2b | Unlocks the Efficiency modifier for Hundred Fists: put it in one of its 2 modifier slots - it levels up as you use Hundred Fists |
| 2 | Still Water: Duration | 1 | `Class.Monk.b3.r2a` | Monk.b3.r2a | Unlocks the Duration modifier for Still Water: put it in one of its 2 modifier slots - it levels up as you use Still Water |
| 2 | Still Water: Ward | 1 | `Class.Monk.b3.r2b` | Monk.b3.r2b | Unlocks the Ward modifier for Still Water: put it in one of its 2 modifier slots - it levels up as you use Still Water |
| 2 | Hundred Fists: Radius | 1 | `Class.Monk.m.HundredFists.Radius` | new | Unlocks the Radius modifier for Hundred Fists: put it in one of its 2 modifier slots - it levels up as you use Hundred Fists |
| 2 | Hundred Fists: Echo | 1 | `Class.Monk.b1.r3a` | Monk.b1.r3a | Unlocks the Echo modifier for Hundred Fists: put it in one of its 2 modifier slots - it levels up as you use Hundred Fists |
| 3 | Quiet Mind | 4 | `Class.Monk.b3.r3a` | Monk.b3.r3a | Still Water mana cost -8% per rank |
| 3 | Flowing Form: Duration | 1 | `Class.Monk.b1.r3b` | Monk.b1.r3b | Unlocks the Duration modifier for Flowing Form: put it in one of its 2 modifier slots - it levels up as you use Flowing Form |
| 3 | Hundred Fists: Power | 1 | `Class.Monk.b1.r4a` | Monk.b1.r4a | Unlocks the Power modifier for Hundred Fists: put it in one of its 2 modifier slots - it levels up as you use Hundred Fists |
| 3 | Return Volley | 3 | `Class.Monk.b3.r3b` | Monk.b3.r3b | a deflected projectile hits its shooter for 20% of its damage per rank |
| 4 | Flowing Form: Radius | 1 | `Class.Monk.b1.r4b` | Monk.b1.r4b | Unlocks the Radius modifier for Flowing Form: put it in one of its 2 modifier slots - it levels up as you use Flowing Form |
| 4 | Still Water: Knockback | 1 | `Class.Monk.b3.r4a` | Monk.b3.r4a | Unlocks the Knockback modifier for Still Water: put it in one of its 2 modifier slots - it levels up as you use Still Water |
| 4 | Still Water: Echo | 1 | `Class.Monk.b3.r5a` | Monk.b3.r5a | Unlocks the Echo modifier for Still Water: put it in one of its 2 modifier slots - it levels up as you use Still Water |
| 4 | Still Water: Power | 1 | `Class.Monk.b3.r5b` | Monk.b3.r5b | Unlocks the Power modifier for Still Water: put it in one of its 2 modifier slots - it levels up as you use Still Water |
| 5 | Fluid Stride | 3 | `Class.Monk.b1.r5b` | Monk.b1.r5b | Flowing Form grants +5% speed per rank |
| 5 | Steady Breath | 3 | `Class.Monk.b2.r5a` | Monk.b2.r5a | every 5th combo stack gives back 3 Stamina per rank |
| 5 | Flurry | 3 | `Class.Monk.b2.r5b` | Monk.b2.r5b | Flowing Form's combo cap +2 per rank |
| 5 | No Mind | 1 | `Class.Monk.b3.r6` | Monk.b3.r6 | a counter resets your other Monk cooldowns and keeps Still Water up 3s longer (once every 6s) |
| 6 | Untouchable | 1 | `Class.Monk.b1.r6` | Monk.b1.r6 | during Flowing Form an afterimage strikes every enemy within 2.5 blocks each second (30% of a hit) and gives back 1 Stamina per enemy hit |

### Branch 2 - Fist (combo pressure, ricochet)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | Swift Feet | 5 | `Class.Monk.b1.r1a` | Monk.b1.r1a | +3% movement speed per rank |
| 1 | Deep Breath | 4 | `Class.Monk.b1.r1b` | Monk.b1.r1b | stamina regen +10% per rank |
| 2 | **Palm Strike** | ABILITY (free) | - | Monk.b2.r2.free |  |
| 2 | Slipstream | 3 | `Class.Monk.b1.r5a` | Monk.b1.r5a | a dodge roll stuns enemies it passes (within 1.5 blocks) for 0.3s per rank |
| 3 | Palm Strike: Knockback | 1 | `Class.Monk.b2.r2a` | Monk.b2.r2a | Unlocks the Knockback modifier for Palm Strike: put it in one of its 2 modifier slots - it levels up as you use Palm Strike |
| 3 | Palm Strike: Ricochet | 1 | `Class.Monk.b2.r3a` | Monk.b2.r3a | Unlocks the Ricochet modifier for Palm Strike: put it in one of its 2 modifier slots - it levels up as you use Palm Strike |
| 3 | Palm Strike: Echo | 1 | `Class.Monk.b2.r1b` | Monk.b2.r1b | Unlocks the Echo modifier for Palm Strike: put it in one of its 2 modifier slots - it levels up as you use Palm Strike |
| 4 | Palm Strike: Slow | 1 | `Class.Monk.b2.r3b` | Monk.b2.r3b | Unlocks the Slow modifier for Palm Strike: put it in one of its 2 modifier slots - it levels up as you use Palm Strike |
| 4 | Stunning Palm | 5 | `Class.Monk.b2.r4a` | Monk.b2.r4a | Palm Strike stuns +0.25s per rank |
| 5 | **Cyclone Kick** | ABILITY (free) | - | Monk.b2.r5.free |  |
| 5 | Cyclone Kick: Radius | 1 | `Class.Monk.m.CycloneKick.Radius` | new | Unlocks the Radius modifier for Cyclone Kick: put it in one of its 2 modifier slots - it levels up as you use Cyclone Kick |
| 5 | Cyclone Kick: Knockback | 1 | `Class.Monk.m.CycloneKick.Knockback` | new | Unlocks the Knockback modifier for Cyclone Kick: put it in one of its 2 modifier slots - it levels up as you use Cyclone Kick |
| 5 | Cyclone Kick: Slow | 1 | `Class.Monk.m.CycloneKick.Slow` | new | Unlocks the Slow modifier for Cyclone Kick: put it in one of its 2 modifier slots - it levels up as you use Cyclone Kick |
| 5 | Cyclone Kick: Haste | 1 | `Class.Monk.m.CycloneKick.Haste` | new | Unlocks the Haste modifier for Cyclone Kick: put it in one of its 2 modifier slots - it levels up as you use Cyclone Kick |
| 5 | Palm Strike: Power | 1 | `Class.Monk.b2.r1a` | Monk.b2.r1a | Unlocks the Power modifier for Palm Strike: put it in one of its 2 modifier slots - it levels up as you use Palm Strike |
| 6 | Thousand Palms | 1 | `Class.Monk.b2.r6` | Monk.b2.r6 | at 10+ combo Palm Strike has (almost) no cooldown, and every 5th weapon hit in a row strikes every enemy within 3 blocks for 40% |

### Branch 3 - Weaponcraft (weapons, defence, loot)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Combat Focus** | free passive | - | Combat.b1.r1.free | +3% damage |
| 1 | Hone Edge | 5 | `Skill.Combat.b1.r1a` | Combat.b1.r1a | +2% weapon damage/rank |
| 1 | Toughness | 5 | `Skill.Combat.b2.r1a` | Combat.b2.r1a | +0.5% max Health/rank |
| 1 | Scavenger | 5 | `Skill.Combat.b3.r1a` | Combat.b3.r1a | +2% chance/rank a kill drops 1 more item of its loot (never gear) |
| 1 | Coin Purse | 3 | `Skill.Combat.b3.r1b` | Combat.b3.r1b | 3% chance/rank a kill also pays coins (the mob's level) |
| 2 | **Light Step** | free passive | - | Monk.b1.r1a | +2% movement speed (always on) |
| 2 | Weak Spot | 3 | `Skill.Combat.b1.r1b` | Combat.b1.r1b | +2% crit chance/rank |
| 2 | Iron Will | 3 | `Skill.Combat.b2.r1b` | Combat.b2.r1b | +3% knockback resistance/rank |
| 2 | Momentum | 4 | `Skill.Combat.b1.r3b` | Combat.b1.r3b | +1% move speed/rank |
| 2 | Rally | 3 | `Skill.Combat.b2.r4b` | Combat.b2.r4b | +3% Health regen out of combat per rank |
| 3 | Finisher | 3 | `Skill.Combat.b1.r3a` | Combat.b1.r3a | +4% damage/rank to enemies below 30% Health |
| 3 | Thick Skin | 4 | `Skill.Combat.b2.r3a` | Combat.b2.r3a | +2% damage reduction/rank |
| 3 | Pet Fang | 5 | `Skill.Combat.b3.r3a` | Combat.b3.r3a | +2% combat XP and +1% damage per equipped Combat pet tier, per rank |
| 3 | Rare Drop | 3 | `Skill.Combat.b3.r3b` | Combat.b3.r3b | +1% chance/rank a kill drops 1 more of its rarest loot (never gear) |
| 3 | Reprisal | 3 | `Skill.Combat.b2.r3b` | Combat.b2.r3b | 3% of the melee damage you take is dealt back to the attacker per rank |
| 4 | Crit Mastery | 3 | `Skill.Combat.b1.r4a` | Combat.b1.r4a | +3% crit damage/rank |
| 4 | Gear Resonance | 3 | `Skill.Combat.b1.r4b` | Combat.b1.r4b | +2% damage per combat-tagged armor piece/rank |
| 4 | Accessory Plates | 3 | `Skill.Combat.b2.r4a` | Combat.b2.r4a | +0.5% max health per filled accessory slot, per rank |
| 4 | Boss Hunter | 3 | `Skill.Combat.b3.r4a` | Combat.b3.r4a | +3% chance/rank a boss or mini boss drops its loot once more (never gear) |
| 5 | **Still Mind** | free passive | - | Monk.b3.r1b | enemies you hit during Still Water are 4% slower for 2s (always on) |
| 5 | Trophy Hunter | 3 | `Skill.Combat.b1.r5a` | Combat.b1.r5a | +3% damage/rank to bosses and mini bosses |
| 5 | Weapon Tempering | 4 | `Skill.Combat.b1.r5b` | Combat.b1.r5b | +1% damage per metal tier above Iron per rank (max +20%) |
| 5 | Lucky Kill | 3 | `Skill.Combat.b3.r5a` | Combat.b3.r5a | 2% chance/rank a kill drops its whole loot twice (never gear) |
| 5 | Battle Insight | 5 | `Skill.Combat.b3.r5b` | Combat.b3.r5b | +2% class XP/rank |
| 5 | Second Wind | 3 | `Skill.Combat.b2.r3c` | Combat.b2.r3c | once a fight, a hit that drops you below 20% Health heals you 5% of max Health per rank |
| 6 | Edge of the Legend | 1 | `Skill.Combat.b1.r6` | Combat.b1.r6 | +10% damage to enemies below 30% Health |

Second modifier nodes folded into the one unlock node (their ranks are refunded; the modifier level they gave is kept by its use count): `Class.Monk.b2.r2b` (PalmStrike Power, 1 ranks), `Class.Monk.b2.r4b` (PalmStrike Power, 1 ranks), `Class.Monk.b3.r4b` (StillWater Duration, 1 ranks)

## Assassin

### Branch 1 - Shadowstep (stealth, openers, escapes)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Cloak + First Strike** | ABILITY (free) | - | Assassin.b1.r1.free |  |
| 1 | Ambush | 3 | `Class.Assassin.b1.r1b` | Assassin.b1.r1b | First Strike +5% dmg per rank; a First Strike kill cuts Cloak CD by 1s per rank |
| 1 | Cloak + First Strike: Duration | 1 | `Class.Assassin.b1.r1a` | Assassin.b1.r1a | Unlocks the Duration modifier for Cloak + First Strike: put it in one of its 2 modifier slots - it levels up as you use Cloak + First Strike |
| 1 | Cloak + First Strike: Power | 1 | `Class.Assassin.m.CloakFirstStrike.Power` | new | Unlocks the Power modifier for Cloak + First Strike: put it in one of its 2 modifier slots - it levels up as you use Cloak + First Strike |
| 1 | Keen Blades | 5 | `Class.Assassin.b2.r1a` | Assassin.b2.r1a | +4.5% weapon damage per rank |
| 2 | **Vanishing Act** | ABILITY (free) | - | Assassin.b1.r2.free |  |
| 2 | Cloak + First Strike: Haste | 1 | `Class.Assassin.b1.r2a` | Assassin.b1.r2a | Unlocks the Haste modifier for Cloak + First Strike: put it in one of its 2 modifier slots - it levels up as you use Cloak + First Strike |
| 2 | Vanishing Act: Radius | 1 | `Class.Assassin.m.VanishingAct.Radius` | new | Unlocks the Radius modifier for Vanishing Act: put it in one of its 2 modifier slots - it levels up as you use Vanishing Act |
| 2 | Vanishing Act: Duration | 1 | `Class.Assassin.m.VanishingAct.Duration` | new | Unlocks the Duration modifier for Vanishing Act: put it in one of its 2 modifier slots - it levels up as you use Vanishing Act |
| 2 | Vanishing Act: Slow | 1 | `Class.Assassin.m.VanishingAct.Slow` | new | Unlocks the Slow modifier for Vanishing Act: put it in one of its 2 modifier slots - it levels up as you use Vanishing Act |
| 3 | Fleetfoot | 3 | `Class.Assassin.b1.r2b` | Assassin.b1.r2b | +3% move speed per rank, doubled while Cloaked |
| 3 | Vanishing Act: Efficiency | 1 | `Class.Assassin.m.VanishingAct.Efficiency` | new | Unlocks the Efficiency modifier for Vanishing Act: put it in one of its 2 modifier slots - it levels up as you use Vanishing Act |
| 3 | Cloak + First Strike: Efficiency | 1 | `Class.Assassin.b1.r3a` | Assassin.b1.r3a | Unlocks the Efficiency modifier for Cloak + First Strike: put it in one of its 2 modifier slots - it levels up as you use Cloak + First Strike |
| 3 | Bloodthirst | 2 | `Class.Assassin.b2.r3c` | Assassin.b2.r3c | a First Strike or God Killer hit gives +3% damage per rank for 4s (crits are your gear's) |
| 4 | Double Smoke | 1 | `Class.Assassin.b1.r4a` | Assassin.b1.r4a | Vanishing Act leaves a second, half-size smoke where you stand 2s later |
| 4 | Smoke Veil | 3 | `Class.Assassin.b1.r4b` | Assassin.b1.r4b | breaking your Cloak with an attack stuns enemies within 3 blocks for 0.3s per rank |
| 4 | Shadow Snare | 1 | `Class.Assassin.b2.r4a` | Assassin.b2.r4a | First Strike pulls its target 3 blocks toward your Shadow Clone and the clone strikes it once (40% of the hit) |
| 5 | Lethality | 5 | `Class.Assassin.b2.r4b` | Assassin.b2.r4b | +3% chance per rank that a weapon hit is Lethal (+50% damage) |
| 5 | Phantom Edge | 3 | `Class.Assassin.b1.r5a` | Assassin.b1.r5a | your first weapon hit within 6s after Vanishing Act deals +6% per rank |
| 5 | Slipstream | 3 | `Class.Assassin.b1.r5b` | Assassin.b1.r5b | a kill while Cloaked (or with the hit that broke it) cloaks you 1s per rank |
| 6 | Ghost Protocol | 1 | `Class.Assassin.b1.r6` | Assassin.b1.r6 | a First Strike kill cloaks you again for 3s at once (once every 8s) |

### Branch 2 - Venomcraft (poisons, debuffs, attrition)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | Thick Fumes | 3 | `Class.Assassin.b3.r1a` | Assassin.b3.r1a | Toxin's cloud lasts +1s per rank |
| 1 | Potent Venom | 4 | `Class.Assassin.b3.r2a` | Assassin.b3.r2a | Toxin ticks +5% dmg per rank |
| 1 | Numbing Venom | 2 | `Class.Assassin.b3.r3a` | Assassin.b3.r3a | Toxin slows 6% per rank |
| 2 | **Toxin** | ABILITY (free) | - | Assassin.b3.r2.free |  |
| 2 | Toxin: Radius | 1 | `Class.Assassin.b3.r2b` | Assassin.b3.r2b | Unlocks the Radius modifier for Toxin: put it in one of its 2 modifier slots - it levels up as you use Toxin |
| 2 | Toxin: Duration | 1 | `Class.Assassin.m.Toxin.Duration` | new | Unlocks the Duration modifier for Toxin: put it in one of its 2 modifier slots - it levels up as you use Toxin |
| 2 | Toxin: Chain | 1 | `Class.Assassin.m.Toxin.Chain` | new | Unlocks the Chain modifier for Toxin: put it in one of its 2 modifier slots - it levels up as you use Toxin |
| 3 | Neurotoxin | 2 | `Class.Assassin.b3.r4b` | Assassin.b3.r4b | poisoned enemies deal 5% less damage per rank (mobs do not heal) |
| 3 | Toxin: Echo | 1 | `Class.Assassin.b3.r4a` | Assassin.b3.r4a | Unlocks the Echo modifier for Toxin: put it in one of its 2 modifier slots - it levels up as you use Toxin |
| 3 | Venom Rush | 3 | `Class.Assassin.b3.r4c` | Assassin.b3.r4c | +4% max Stamina per rank; a poisoned enemy's death gives back 1 Stamina per rank |
| 4 | Nightrunner | 2 | `Class.Assassin.b1.r4c` | Assassin.b1.r4c | +4% Stamina regen per rank |
| 4 | Deicide | 1 | `Class.Assassin.b2.r6` | Assassin.b2.r6 | God Killer deals +1% dmg per 1% of the target's missing HP (max +60%), and a kill resets its CD |
| 4 | Cheap Brew | 3 | `Class.Assassin.b3.r5a` | Assassin.b3.r5a | Toxin costs -8% Mana per rank |
| 4 | Contagion | 3 | `Class.Assassin.b3.r5b` | Assassin.b3.r5b | a poisoned enemy that dies spreads 1 Toxin stack to 1 nearby enemy per rank |
| 5 | **God Killer** | ABILITY (free) | - | Assassin.b2.r5.free |  |
| 5 | God Killer: Haste | 1 | `Class.Assassin.b2.r5a` | Assassin.b2.r5a | Unlocks the Haste modifier for God Killer: put it in one of its 2 modifier slots - it levels up as you use God Killer |
| 5 | God Killer: Power | 1 | `Class.Assassin.m.GodKiller.Power` | new | Unlocks the Power modifier for God Killer: put it in one of its 2 modifier slots - it levels up as you use God Killer |
| 5 | God Killer: Duration | 1 | `Class.Assassin.m.GodKiller.Duration` | new | Unlocks the Duration modifier for God Killer: put it in one of its 2 modifier slots - it levels up as you use God Killer |
| 5 | God Killer: Efficiency | 1 | `Class.Assassin.m.GodKiller.Efficiency` | new | Unlocks the Efficiency modifier for God Killer: put it in one of its 2 modifier slots - it levels up as you use God Killer |
| 5 | God Killer: Echo | 1 | `Class.Assassin.m.GodKiller.Echo` | new | Unlocks the Echo modifier for God Killer: put it in one of its 2 modifier slots - it levels up as you use God Killer |
| 5 | Bounty Sense | 3 | `Class.Assassin.b2.r5b` | Assassin.b2.r5b | +4.5% dmg per rank vs elites and bosses |
| 6 | Black Lotus | 1 | `Class.Assassin.b3.r6` | Assassin.b3.r6 | Toxin stacks on one enemy: every 3rd poison tick from you detonates for 200% of a tick |

### Branch 3 - Weaponcraft (weapons, defence, loot)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Combat Focus** | free passive | - | Combat.b1.r1.free | +3% damage |
| 1 | Hone Edge | 5 | `Skill.Combat.b1.r1a` | Combat.b1.r1a | +2% weapon damage/rank |
| 1 | Toughness | 5 | `Skill.Combat.b2.r1a` | Combat.b2.r1a | +0.5% max Health/rank |
| 1 | Scavenger | 5 | `Skill.Combat.b3.r1a` | Combat.b3.r1a | +2% chance/rank a kill drops 1 more item of its loot (never gear) |
| 1 | Coin Purse | 3 | `Skill.Combat.b3.r1b` | Combat.b3.r1b | 3% chance/rank a kill also pays coins (the mob's level) |
| 1 | Kunai Mark | 1 | `Class.Assassin.b2.r1b` | Assassin.b2.r1b | a kunai hit marks the target; your next melee hit on it deals +15% |
| 1 | Coated Kunai | 3 | `Class.Assassin.b3.r1b` | Assassin.b3.r1b | kunai hits reduce the target's dmg by 2% per rank for 4s |
| 2 | **Shadow Clone** | free passive | - | Assassin.b2.r2.free | Cloak / Vanishing Act leave a clone: nearby enemies lose you; then it hits one (60%) |
| 2 | Weak Spot | 3 | `Skill.Combat.b1.r1b` | Combat.b1.r1b | +2% crit chance/rank |
| 2 | Iron Will | 3 | `Skill.Combat.b2.r1b` | Combat.b2.r1b | +3% knockback resistance/rank |
| 2 | Momentum | 4 | `Skill.Combat.b1.r3b` | Combat.b1.r3b | +1% move speed/rank |
| 2 | Rally | 3 | `Skill.Combat.b2.r4b` | Combat.b2.r4b | +3% Health regen out of combat per rank |
| 2 | Many Shadows | 2 | `Class.Assassin.b2.r2a` | Assassin.b2.r2a | +1 Shadow Clone per rank (each strikes one enemy for 40% of a hit) |
| 2 | Lasting Shades | 4 | `Class.Assassin.b2.r2b` | Assassin.b2.r2b | clones last +1s per rank |
| 3 | Finisher | 3 | `Skill.Combat.b1.r3a` | Combat.b1.r3a | +4% damage/rank to enemies below 30% Health |
| 3 | Thick Skin | 4 | `Skill.Combat.b2.r3a` | Combat.b2.r3a | +2% damage reduction/rank |
| 3 | Pet Fang | 5 | `Skill.Combat.b3.r3a` | Combat.b3.r3a | +2% combat XP and +1% damage per equipped Combat pet tier, per rank |
| 3 | Rare Drop | 3 | `Skill.Combat.b3.r3b` | Combat.b3.r3b | +1% chance/rank a kill drops 1 more of its rarest loot (never gear) |
| 3 | Reprisal | 3 | `Skill.Combat.b2.r3b` | Combat.b2.r3b | 3% of the melee damage you take is dealt back to the attacker per rank |
| 3 | Backstab | 4 | `Class.Assassin.b1.r3b` | Assassin.b1.r3b | hits from behind +6% dmg per rank |
| 4 | Crit Mastery | 3 | `Skill.Combat.b1.r4a` | Combat.b1.r4a | +3% crit damage/rank |
| 4 | Gear Resonance | 3 | `Skill.Combat.b1.r4b` | Combat.b1.r4b | +2% damage per combat-tagged armor piece/rank |
| 4 | Accessory Plates | 3 | `Skill.Combat.b2.r4a` | Combat.b2.r4a | +0.5% max health per filled accessory slot, per rank |
| 4 | Boss Hunter | 3 | `Skill.Combat.b3.r4a` | Combat.b3.r4a | +3% chance/rank a boss or mini boss drops its loot once more (never gear) |
| 4 | Bouncing Kunai | 1 | `Class.Assassin.b2.r3a` | Assassin.b2.r3a | kunai bounce to 1 extra target at 50% dmg |
| 4 | Mirror Strike | 3 | `Class.Assassin.b2.r3b` | Assassin.b2.r3b | while a Shadow Clone stands, your ability hits strike again from it for 15% +5% per rank |
| 5 | **Killer Instinct** | free passive | - | Assassin.b1.r3b | hits from behind deal +3% damage (always on) |
| 5 | Trophy Hunter | 3 | `Skill.Combat.b1.r5a` | Combat.b1.r5a | +3% damage/rank to bosses and mini bosses |
| 5 | Weapon Tempering | 4 | `Skill.Combat.b1.r5b` | Combat.b1.r5b | +1% damage per metal tier above Iron per rank (max +20%) |
| 5 | Lucky Kill | 3 | `Skill.Combat.b3.r5a` | Combat.b3.r5a | 2% chance/rank a kill drops its whole loot twice (never gear) |
| 5 | Battle Insight | 5 | `Skill.Combat.b3.r5b` | Combat.b3.r5b | +2% class XP/rank |
| 5 | Second Wind | 3 | `Skill.Combat.b2.r3c` | Combat.b2.r3c | once a fight, a hit that drops you below 20% Health heals you 5% of max Health per rank |
| 5 | Exploit | 4 | `Class.Assassin.b3.r3b` | Assassin.b3.r3b | +4.5% dmg per rank for each debuff on the target (max 3 debuffs) |
| 6 | Edge of the Legend | 1 | `Skill.Combat.b1.r6` | Combat.b1.r6 | +10% damage to enemies below 30% Health |

## Archer

### Branch 1 - Huntmaster (marking, precision, focus fire)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Pinning Shot** | ABILITY (free) | - | Archer.b1.r1.free |  |
| 1 | Pinning Shot: Duration | 1 | `Class.Archer.b1.r1a` | Archer.b1.r1a | Unlocks the Duration modifier for Pinning Shot: put it in one of its 2 modifier slots - it levels up as you use Pinning Shot |
| 1 | Pinning Shot: Pierce | 1 | `Class.Archer.m.PinningShot.Pierce` | new | Unlocks the Pierce modifier for Pinning Shot: put it in one of its 2 modifier slots - it levels up as you use Pinning Shot |
| 1 | Pinning Shot: Split | 1 | `Class.Archer.m.PinningShot.Split` | new | Unlocks the Split modifier for Pinning Shot: put it in one of its 2 modifier slots - it levels up as you use Pinning Shot |
| 1 | Pinning Shot: Power | 1 | `Class.Archer.m.PinningShot.Power` | new | Unlocks the Power modifier for Pinning Shot: put it in one of its 2 modifier slots - it levels up as you use Pinning Shot |
| 1 | Hunter's Mark | 3 | `Class.Archer.b1.r1b` | Archer.b1.r1b | Pinned targets take +4% dmg from all allies per rank for 5s |
| 2 | **Arrow Rain** | ABILITY (free) | - | Archer.b3.r2.free |  |
| 2 | **Hunter's Net** | ABILITY (free) | - | Archer.b2.r2.free |  |
| 2 | Hunter's Net: Radius | 1 | `Class.Archer.b2.r2a` | Archer.b2.r2a | Unlocks the Radius modifier for Hunter's Net: put it in one of its 2 modifier slots - it levels up as you use Hunter's Net |
| 2 | Hunter's Net: Pull | 1 | `Class.Archer.b2.r2b` | Archer.b2.r2b | Unlocks the Pull modifier for Hunter's Net: put it in one of its 2 modifier slots - it levels up as you use Hunter's Net |
| 2 | Arrow Rain: Radius | 1 | `Class.Archer.b3.r2a` | Archer.b3.r2a | Unlocks the Radius modifier for Arrow Rain: put it in one of its 2 modifier slots - it levels up as you use Arrow Rain |
| 2 | Arrow Rain: Duration | 1 | `Class.Archer.b3.r2b` | Archer.b3.r2b | Unlocks the Duration modifier for Arrow Rain: put it in one of its 2 modifier slots - it levels up as you use Arrow Rain |
| 2 | Arrow Rain: Lingering | 1 | `Class.Archer.m.ArrowRain.Lingering` | new | Unlocks the Lingering modifier for Arrow Rain: put it in one of its 2 modifier slots - it levels up as you use Arrow Rain |
| 3 | Barbed Mesh | 2 | `Class.Archer.b2.r2c` | Archer.b2.r2c | netted enemies take +5% dmg per rank |
| 3 | Arrow Rain: Echo | 1 | `Class.Archer.m.ArrowRain.Echo` | new | Unlocks the Echo modifier for Arrow Rain: put it in one of its 2 modifier slots - it levels up as you use Arrow Rain |
| 3 | Hunter's Net: Split | 1 | `Class.Archer.m.HuntersNet.Split` | new | Unlocks the Split modifier for Hunter's Net: put it in one of its 2 modifier slots - it levels up as you use Hunter's Net |
| 3 | Hunter's Net: Duration | 1 | `Class.Archer.b2.r3b` | Archer.b2.r3b | Unlocks the Duration modifier for Hunter's Net: put it in one of its 2 modifier slots - it levels up as you use Hunter's Net |
| 3 | Skipping Pin | 1 | `Class.Archer.b1.r3b` | Archer.b1.r3b | Pinning Shot bounces to 1 more target at 60% root duration |
| 4 | Pinfall | 1 | `Class.Archer.b3.r3a` | Archer.b3.r3a | Arrow Rain hits have a 10% chance to Pin (root) for 0.5s |
| 4 | Deep Quiver | 3 | `Class.Archer.b3.r3b` | Archer.b3.r3b | +4% max Stamina per rank; Arrow Rain costs -5% per rank |
| 4 | Skipping Rain | 2 | `Class.Archer.b3.r3c` | Archer.b3.r3c | Arrow Rain arrows bounce once at 20% dmg per rank |
| 4 | Eagle Eye | 3 | `Class.Archer.b1.r3a` | Archer.b1.r3a | bow hits from 15+ blocks away deal +7.5% per rank (arrow speed is fixed per bow) |
| 5 | Clinging Mesh | 3 | `Class.Archer.b2.r4a` | Archer.b2.r4a | after Hunter's Net's root, netted enemies stay 15% slower for 1s per rank |
| 5 | Arrow Rain: Power | 1 | `Class.Archer.b3.r4a` | Archer.b3.r4a | Unlocks the Power modifier for Arrow Rain: put it in one of its 2 modifier slots - it levels up as you use Arrow Rain |
| 5 | Downdraft | 2 | `Class.Archer.b3.r4b` | Archer.b3.r4b | Arrow Rain's centre drags enemies inward at 0.5 block/s per rank |
| 5 | Lockdown | 3 | `Class.Archer.b2.r5a` | Archer.b2.r5a | Hunter's Net CD -6% per rank |
| 6 | Spider's Den | 1 | `Class.Archer.b2.r6` | Archer.b2.r6 | Hunter's Net holds 2 charges, and an enemy netted twice within 6s is stunned 1.5s |

### Branch 2 - Stormvolley (area denial, barrages)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | Volley Training | 4 | `Class.Archer.b3.r1b` | Archer.b3.r1b | Arrow Rain, Explosive Arrow and Hunter's Net +3% damage per rank |
| 1 | Hobbling Shots | 4 | `Class.Archer.b2.r1a` | Archer.b2.r1a | arrows slow 3% per rank for 2s |
| 2 | **Rapid Fire** | ABILITY (free) | - | Archer.b1.r2.free |  |
| 2 | Rapid Fire: Pierce | 1 | `Class.Archer.b1.r2a` | Archer.b1.r2a | Unlocks the Pierce modifier for Rapid Fire: put it in one of its 2 modifier slots - it levels up as you use Rapid Fire |
| 2 | Rapid Fire: Ricochet | 1 | `Class.Archer.m.RapidFire.Ricochet` | new | Unlocks the Ricochet modifier for Rapid Fire: put it in one of its 2 modifier slots - it levels up as you use Rapid Fire |
| 2 | Rapid Fire: Duration | 1 | `Class.Archer.m.RapidFire.Duration` | new | Unlocks the Duration modifier for Rapid Fire: put it in one of its 2 modifier slots - it levels up as you use Rapid Fire |
| 3 | Rapid Fire: Slow | 1 | `Class.Archer.m.RapidFire.Slow` | new | Unlocks the Slow modifier for Rapid Fire: put it in one of its 2 modifier slots - it levels up as you use Rapid Fire |
| 3 | Rapid Fire: Seeker | 1 | `Class.Archer.m.RapidFire.Seeker` | new | Unlocks the Seeker modifier for Rapid Fire: put it in one of its 2 modifier slots - it levels up as you use Rapid Fire |
| 3 | Tripwire | 2 | `Class.Archer.b2.r1b` | Archer.b2.r1b | a dodge roll leaves a snare (6s): the first enemy to touch it is rooted 0.5s per rank |
| 4 | Steady Draw | 4 | `Class.Archer.b1.r2b` | Archer.b1.r2b | +4.5% bow dmg per rank |
| 4 | Quickdraw | 2 | `Class.Archer.b1.r3c` | Archer.b1.r3c | each bow hit takes 0.2s per rank off Rapid Fire's cooldown (draw speed is fixed per bow) |
| 5 | **Explosive Arrow** | ABILITY (free) | - | Archer.b3.r5.free |  |
| 5 | Heavy Volley | 4 | `Class.Archer.b1.r4a` | Archer.b1.r4a | Rapid Fire +4% dmg per arrow per rank |
| 5 | Explosive Arrow: Radius | 1 | `Class.Archer.b3.r5a` | Archer.b3.r5a | Unlocks the Radius modifier for Explosive Arrow: put it in one of its 2 modifier slots - it levels up as you use Explosive Arrow |
| 5 | Explosive Arrow: Knockback | 1 | `Class.Archer.b3.r5b` | Archer.b3.r5b | Unlocks the Knockback modifier for Explosive Arrow: put it in one of its 2 modifier slots - it levels up as you use Explosive Arrow |
| 5 | Explosive Arrow: Split | 1 | `Class.Archer.m.ExplosiveArrow.Split` | new | Unlocks the Split modifier for Explosive Arrow: put it in one of its 2 modifier slots - it levels up as you use Explosive Arrow |
| 5 | Explosive Arrow: Echo | 1 | `Class.Archer.m.ExplosiveArrow.Echo` | new | Unlocks the Echo modifier for Explosive Arrow: put it in one of its 2 modifier slots - it levels up as you use Explosive Arrow |
| 5 | Firestorm | 1 | `Class.Archer.b3.r6` | Archer.b3.r6 | an Explosive Arrow that explodes inside your Arrow Rain detonates the whole rain: everything inside takes 150% of the blast (once per rain) |
| 6 | Dead Eye | 1 | `Class.Archer.b1.r6` | Archer.b1.r6 | Rapid Fire deals +50% to rooted (Pinned) enemies, and its hits keep Hunter's Mark on them |

### Branch 3 - Weaponcraft (weapons, defence, loot)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Combat Focus** | free passive | - | Combat.b1.r1.free | +3% damage |
| 1 | Hone Edge | 5 | `Skill.Combat.b1.r1a` | Combat.b1.r1a | +2% weapon damage/rank |
| 1 | Toughness | 5 | `Skill.Combat.b2.r1a` | Combat.b2.r1a | +0.5% max Health/rank |
| 1 | Scavenger | 5 | `Skill.Combat.b3.r1a` | Combat.b3.r1a | +2% chance/rank a kill drops 1 more item of its loot (never gear) |
| 1 | Coin Purse | 3 | `Skill.Combat.b3.r1b` | Combat.b3.r1b | 3% chance/rank a kill also pays coins (the mob's level) |
| 1 | Splinter Shots | 2 | `Class.Archer.b3.r1a` | Archer.b3.r1a | bow hits splash 35% to 1 more enemy per rank within 4 blocks |
| 2 | **Keen Eye** | free passive | - | Archer.b1.r2b | +2% bow damage (always on) |
| 2 | Weak Spot | 3 | `Skill.Combat.b1.r1b` | Combat.b1.r1b | +2% crit chance/rank |
| 2 | Iron Will | 3 | `Skill.Combat.b2.r1b` | Combat.b2.r1b | +3% knockback resistance/rank |
| 2 | Momentum | 4 | `Skill.Combat.b1.r3b` | Combat.b1.r3b | +1% move speed/rank |
| 2 | Rally | 3 | `Skill.Combat.b2.r4b` | Combat.b2.r4b | +3% Health regen out of combat per rank |
| 2 | Focus Fire | 3 | `Class.Archer.b1.r5b` | Archer.b1.r5b | each consecutive hit on the same target +1% dmg per rank (max 5 stacks) |
| 2 | Thick Hide | 3 | `Class.Archer.b2.r5b` | Archer.b2.r5b | -4.5% damage taken per rank while an enemy within 8 blocks is rooted |
| 3 | Finisher | 3 | `Skill.Combat.b1.r3a` | Combat.b1.r3a | +4% damage/rank to enemies below 30% Health |
| 3 | Thick Skin | 4 | `Skill.Combat.b2.r3a` | Combat.b2.r3a | +2% damage reduction/rank |
| 3 | Pet Fang | 5 | `Skill.Combat.b3.r3a` | Combat.b3.r3a | +2% combat XP and +1% damage per equipped Combat pet tier, per rank |
| 3 | Rare Drop | 3 | `Skill.Combat.b3.r3b` | Combat.b3.r3b | +1% chance/rank a kill drops 1 more of its rarest loot (never gear) |
| 3 | Reprisal | 3 | `Skill.Combat.b2.r3b` | Combat.b2.r3b | 3% of the melee damage you take is dealt back to the attacker per rank |
| 3 | Driving Shots | 2 | `Class.Archer.b2.r3a` | Archer.b2.r3a | bow hits knock enemies back 0.75 blocks per rank |
| 4 | Crit Mastery | 3 | `Skill.Combat.b1.r4a` | Combat.b1.r4a | +3% crit damage/rank |
| 4 | Gear Resonance | 3 | `Skill.Combat.b1.r4b` | Combat.b1.r4b | +2% damage per combat-tagged armor piece/rank |
| 4 | Accessory Plates | 3 | `Skill.Combat.b2.r4a` | Combat.b2.r4a | +0.5% max health per filled accessory slot, per rank |
| 4 | Boss Hunter | 3 | `Skill.Combat.b3.r4a` | Combat.b3.r4a | +3% chance/rank a boss or mini boss drops its loot once more (never gear) |
| 4 | Called Shot | 2 | `Class.Archer.b1.r4b` | Archer.b1.r4b | hits on Marked enemies deal +7.5% per rank |
| 4 | Clinch | 3 | `Class.Archer.b2.r4b` | Archer.b2.r4b | rooted enemies deal 5% less damage to you per rank (mob skills cannot be silenced) |
| 5 | **Fleet Ranger** | free passive | - | Archer.b1.r5a | +2% movement speed (always on) |
| 5 | Trophy Hunter | 3 | `Skill.Combat.b1.r5a` | Combat.b1.r5a | +3% damage/rank to bosses and mini bosses |
| 5 | Weapon Tempering | 4 | `Skill.Combat.b1.r5b` | Combat.b1.r5b | +1% damage per metal tier above Iron per rank (max +20%) |
| 5 | Lucky Kill | 3 | `Skill.Combat.b3.r5a` | Combat.b3.r5a | 2% chance/rank a kill drops its whole loot twice (never gear) |
| 5 | Battle Insight | 5 | `Skill.Combat.b3.r5b` | Combat.b3.r5b | +2% class XP/rank |
| 5 | Second Wind | 3 | `Skill.Combat.b2.r3c` | Combat.b2.r3c | once a fight, a hit that drops you below 20% Health heals you 5% of max Health per rank |
| 5 | Fleet Ranger | 3 | `Class.Archer.b1.r5a` | Archer.b1.r5a | +3% move speed per rank; a kill gives back 5 Stamina per rank |
| 6 | Edge of the Legend | 1 | `Skill.Combat.b1.r6` | Combat.b1.r6 | +10% damage to enemies below 30% Health |

## Mage

### Branch 1 - Cosmos (Meteor and Starfall burst)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Meteor** | ABILITY (free) | - | Mage.b1.r1.free |  |
| 1 | More Stars | 2 | `Class.Mage.b1.r2a` | Mage.b1.r2a | Starfall drops +2 stars per rank |
| 1 | Meteor: Radius | 1 | `Class.Mage.b1.r1a` | Mage.b1.r1a | Unlocks the Radius modifier for Meteor: put it in one of its 2 modifier slots - it levels up as you use Meteor |
| 1 | Meteor: Power | 1 | `Class.Mage.b1.r1b` | Mage.b1.r1b | Unlocks the Power modifier for Meteor: put it in one of its 2 modifier slots - it levels up as you use Meteor |
| 1 | Meteor: Split | 1 | `Class.Mage.m.Meteor.Split` | new | Unlocks the Split modifier for Meteor: put it in one of its 2 modifier slots - it levels up as you use Meteor |
| 1 | Homing Stars | 1 | `Class.Mage.b1.r2b` | Mage.b1.r2b | stars home onto the nearest enemy within 4 blocks |
| 2 | **Starfall** | ABILITY (free) | - | Mage.b1.r2.free |  |
| 2 | **Arcane Beam** | ABILITY (free) | - | Mage.b2.r2.free |  |
| 2 | Arcane Beam: Pierce | 1 | `Class.Mage.b2.r2a` | Mage.b2.r2a | Unlocks the Pierce modifier for Arcane Beam: put it in one of its 2 modifier slots - it levels up as you use Arcane Beam |
| 2 | Arcane Beam: Duration | 1 | `Class.Mage.b2.r2b` | Mage.b2.r2b | Unlocks the Duration modifier for Arcane Beam: put it in one of its 2 modifier slots - it levels up as you use Arcane Beam |
| 2 | Starfall: Power | 1 | `Class.Mage.m.Starfall.Power` | new | Unlocks the Power modifier for Starfall: put it in one of its 2 modifier slots - it levels up as you use Starfall |
| 2 | Starfall: Radius | 1 | `Class.Mage.m.Starfall.Radius` | new | Unlocks the Radius modifier for Starfall: put it in one of its 2 modifier slots - it levels up as you use Starfall |
| 2 | Starfall: Duration | 1 | `Class.Mage.m.Starfall.Duration` | new | Unlocks the Duration modifier for Starfall: put it in one of its 2 modifier slots - it levels up as you use Starfall |
| 3 | Starfall: Echo | 1 | `Class.Mage.m.Starfall.Echo` | new | Unlocks the Echo modifier for Starfall: put it in one of its 2 modifier slots - it levels up as you use Starfall |
| 3 | Meteor: Lingering | 1 | `Class.Mage.b1.r3a` | Mage.b1.r3a | Unlocks the Lingering modifier for Meteor: put it in one of its 2 modifier slots - it levels up as you use Meteor |
| 3 | Meteor: Echo | 1 | `Class.Mage.b1.r3b` | Mage.b1.r3b | Unlocks the Echo modifier for Meteor: put it in one of its 2 modifier slots - it levels up as you use Meteor |
| 3 | Arcane Beam: Power | 1 | `Class.Mage.b2.r3a` | Mage.b2.r3a | Unlocks the Power modifier for Arcane Beam: put it in one of its 2 modifier slots - it levels up as you use Arcane Beam |
| 3 | Arcane Beam: Slow | 1 | `Class.Mage.b2.r3b` | Mage.b2.r3b | Unlocks the Slow modifier for Arcane Beam: put it in one of its 2 modifier slots - it levels up as you use Arcane Beam |
| 4 | Shockfall | 2 | `Class.Mage.b1.r4a` | Mage.b1.r4a | Meteor knocks enemies outward +1.5 blocks per rank |
| 4 | Shooting Star | 4 | `Class.Mage.b1.r4b` | Mage.b1.r4b | each Starfall hit cuts Meteor CD by 0.1s per rank |
| 4 | Forked Beam | 1 | `Class.Mage.b2.r4a` | Mage.b2.r4a | beam hits fork to 1 more enemy within 6 blocks for 60% |
| 4 | Feedback | 2 | `Class.Mage.b2.r4c` | Mage.b2.r4c | a beam kill refunds 3% Mana per rank |
| 4 | Focusing Lens | 3 | `Class.Mage.b2.r4b` | Mage.b2.r4b | +6% spell range per rank |
| 5 | Comet Tail | 3 | `Class.Mage.b1.r5b` | Mage.b1.r5b | casting Meteor grants +4% move speed per rank for 3s |
| 5 | Beam Resonance | 2 | `Class.Mage.b2.r5a` | Mage.b2.r5a | beam hits strike again for 10% per rank |
| 5 | Arcane Haste | 4 | `Class.Mage.b2.r5b` | Mage.b2.r5b | +3% move speed per rank while channelling Arcane Beam |
| 5 | Prism Overload | 1 | `Class.Mage.b2.r6` | Mage.b2.r6 | Arcane Beam lasts twice as long (4% max Mana a second after its normal time) and gains +2% damage a second held (max +40%) |
| 6 | Cataclysm | 1 | `Class.Mage.b1.r6` | Mage.b1.r6 | Meteor's impact radius is doubled and it calls down 3 stars of Starfall on the spot |

### Branch 2 - Spellward (mana-fuelled survival (no HP/Def stacking))

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | Mana Well | 4 | `Class.Mage.b2.r1a` | Mage.b2.r1a | +4% max Mana per rank |
| 1 | Overflow | 2 | `Class.Mage.b2.r1b` | Mage.b2.r1b | at full Mana, your next spell deals +6% dmg per rank |
| 1 | Astral Focus | 3 | `Class.Mage.b1.r2c` | Mage.b1.r2c | +6% spell dmg per rank |
| 2 | **Mana Barrier** | ABILITY (free) | - | Mage.b3.r2.free |  |
| 2 | Mana Barrier: Ward | 1 | `Class.Mage.b3.r2a` | Mage.b3.r2a | Unlocks the Ward modifier for Mana Barrier: put it in one of its 2 modifier slots - it levels up as you use Mana Barrier |
| 2 | Mana Barrier: Duration | 1 | `Class.Mage.b3.r2b` | Mage.b3.r2b | Unlocks the Duration modifier for Mana Barrier: put it in one of its 2 modifier slots - it levels up as you use Mana Barrier |
| 2 | Mana Barrier: Power | 1 | `Class.Mage.m.ManaBarrier.Power` | new | Unlocks the Power modifier for Mana Barrier: put it in one of its 2 modifier slots - it levels up as you use Mana Barrier |
| 3 | Mana Barrier: Follow | 1 | `Class.Mage.m.ManaBarrier.Follow` | new | Unlocks the Follow modifier for Mana Barrier: put it in one of its 2 modifier slots - it levels up as you use Mana Barrier |
| 3 | Mana Barrier: Knockback | 1 | `Class.Mage.b3.r3b` | Mage.b3.r3b | Unlocks the Knockback modifier for Mana Barrier: put it in one of its 2 modifier slots - it levels up as you use Mana Barrier |
| 3 | Conduit | 3 | `Class.Mage.b3.r3a` | Mage.b3.r3a | Mana Barrier soaks 5% more damage per Mana per rank |
| 4 | Mana Tide | 2 | `Class.Mage.b3.r3c` | Mage.b3.r3c | +5% Mana regen per rank while the barrier is up |
| 4 | Swift Casting | 2 | `Class.Mage.b1.r3c` | Mage.b1.r3c | -4% cooldown on every Mage ability per rank (cast speed is fixed in Hytale) |
| 4 | Attunement | 2 | `Class.Mage.b2.r3c` | Mage.b2.r3c | +5% Mana regen per rank |
| 4 | Frost Barrier | 3 | `Class.Mage.b3.r4a` | Mage.b3.r4a | enemies that hit your barrier are slowed 8% per rank for 2s |
| 5 | **Frost Nova** | ABILITY (free) | - | Mage.b3.r5.free |  |
| 5 | Clear Mind | 2 | `Class.Mage.b3.r4c` | Mage.b3.r4c | Mana Barrier CD -5% per rank |
| 5 | Frost Nova: Radius | 1 | `Class.Mage.b3.r5a` | Mage.b3.r5a | Unlocks the Radius modifier for Frost Nova: put it in one of its 2 modifier slots - it levels up as you use Frost Nova |
| 5 | Frost Nova: Duration | 1 | `Class.Mage.b3.r5b` | Mage.b3.r5b | Unlocks the Duration modifier for Frost Nova: put it in one of its 2 modifier slots - it levels up as you use Frost Nova |
| 5 | Frost Nova: Power | 1 | `Class.Mage.m.FrostNova.Power` | new | Unlocks the Power modifier for Frost Nova: put it in one of its 2 modifier slots - it levels up as you use Frost Nova |
| 5 | Frost Nova: Slow | 1 | `Class.Mage.m.FrostNova.Slow` | new | Unlocks the Slow modifier for Frost Nova: put it in one of its 2 modifier slots - it levels up as you use Frost Nova |
| 5 | Critical Mass | 3 | `Class.Mage.b1.r5a` | Mage.b1.r5a | +5% damage per rank on enemies hit by 2 different spells within 3s |
| 6 | Glacial Aegis | 1 | `Class.Mage.b3.r6` | Mage.b3.r6 | Frost Nova fires by itself when your Mana Barrier breaks (once per 10s), and frozen enemies take +20% spell damage |

### Branch 3 - Weaponcraft (weapons, defence, loot)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Combat Focus** | free passive | - | Combat.b1.r1.free | +3% damage |
| 1 | Hone Edge | 5 | `Skill.Combat.b1.r1a` | Combat.b1.r1a | +2% weapon damage/rank |
| 1 | Toughness | 5 | `Skill.Combat.b2.r1a` | Combat.b2.r1a | +0.5% max Health/rank |
| 1 | Scavenger | 5 | `Skill.Combat.b3.r1a` | Combat.b3.r1a | +2% chance/rank a kill drops 1 more item of its loot (never gear) |
| 1 | Coin Purse | 3 | `Skill.Combat.b3.r1b` | Combat.b3.r1b | 3% chance/rank a kill also pays coins (the mob's level) |
| 1 | Blink Step | 1 | `Class.Mage.b3.r1a` | Mage.b3.r1a | your dodge roll blinks you 4 blocks on and costs Mana instead of Stamina |
| 1 | Arcane Skin | 5 | `Class.Mage.b3.r1b` | Mage.b3.r1b | take 3% less damage from projectiles and magic per rank |
| 2 | **Spell Ward** | free passive | - | Mage.b3.r1b | take 2% less damage from projectiles and magic (always on) |
| 2 | Weak Spot | 3 | `Skill.Combat.b1.r1b` | Combat.b1.r1b | +2% crit chance/rank |
| 2 | Iron Will | 3 | `Skill.Combat.b2.r1b` | Combat.b2.r1b | +3% knockback resistance/rank |
| 2 | Momentum | 4 | `Skill.Combat.b1.r3b` | Combat.b1.r3b | +1% move speed/rank |
| 2 | Rally | 3 | `Skill.Combat.b2.r4b` | Combat.b2.r4b | +3% Health regen out of combat per rank |
| 3 | Finisher | 3 | `Skill.Combat.b1.r3a` | Combat.b1.r3a | +4% damage/rank to enemies below 30% Health |
| 3 | Thick Skin | 4 | `Skill.Combat.b2.r3a` | Combat.b2.r3a | +2% damage reduction/rank |
| 3 | Pet Fang | 5 | `Skill.Combat.b3.r3a` | Combat.b3.r3a | +2% combat XP and +1% damage per equipped Combat pet tier, per rank |
| 3 | Rare Drop | 3 | `Skill.Combat.b3.r3b` | Combat.b3.r3b | +1% chance/rank a kill drops 1 more of its rarest loot (never gear) |
| 3 | Reprisal | 3 | `Skill.Combat.b2.r3b` | Combat.b2.r3b | 3% of the melee damage you take is dealt back to the attacker per rank |
| 4 | Crit Mastery | 3 | `Skill.Combat.b1.r4a` | Combat.b1.r4a | +3% crit damage/rank |
| 4 | Gear Resonance | 3 | `Skill.Combat.b1.r4b` | Combat.b1.r4b | +2% damage per combat-tagged armor piece/rank |
| 4 | Accessory Plates | 3 | `Skill.Combat.b2.r4a` | Combat.b2.r4a | +0.5% max health per filled accessory slot, per rank |
| 4 | Boss Hunter | 3 | `Skill.Combat.b3.r4a` | Combat.b3.r4a | +3% chance/rank a boss or mini boss drops its loot once more (never gear) |
| 4 | Last Ward | 1 | `Class.Mage.b3.r4b` | Mage.b3.r4b | once per 60s, a killing blow is cancelled and you get a 1s ward |
| 5 | **Deep Focus** | free passive | - | Mage.b2.r1a | +4% max Mana (always on) |
| 5 | Trophy Hunter | 3 | `Skill.Combat.b1.r5a` | Combat.b1.r5a | +3% damage/rank to bosses and mini bosses |
| 5 | Weapon Tempering | 4 | `Skill.Combat.b1.r5b` | Combat.b1.r5b | +1% damage per metal tier above Iron per rank (max +20%) |
| 5 | Lucky Kill | 3 | `Skill.Combat.b3.r5a` | Combat.b3.r5a | 2% chance/rank a kill drops its whole loot twice (never gear) |
| 5 | Battle Insight | 5 | `Skill.Combat.b3.r5b` | Combat.b3.r5b | +2% class XP/rank |
| 5 | Second Wind | 3 | `Skill.Combat.b2.r3c` | Combat.b2.r3c | once a fight, a hit that drops you below 20% Health heals you 5% of max Health per rank |
| 6 | Edge of the Legend | 1 | `Skill.Combat.b1.r6` | Combat.b1.r6 | +10% damage to enemies below 30% Health |

## Priest

### Branch 1 - Devotion (direct healing, triage)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Sacred Heal** | ABILITY (free) | - | Priest.b1.r1.free |  |
| 1 | Far Mercy | 2 | `Class.Priest.b1.r1b` | Priest.b1.r1b | Sacred Heal also reaches 1 more ally per rank up to 20 blocks away at 60% |
| 1 | Sacred Heal: Power | 1 | `Class.Priest.b1.r1a` | Priest.b1.r1a | Unlocks the Power modifier for Sacred Heal: put it in one of its 2 modifier slots - it levels up as you use Sacred Heal |
| 1 | Sacred Heal: Efficiency | 1 | `Class.Priest.b1.r1c` | Priest.b1.r1c | Unlocks the Efficiency modifier for Sacred Heal: put it in one of its 2 modifier slots - it levels up as you use Sacred Heal |
| 1 | Sacred Heal: Radius | 1 | `Class.Priest.m.SacredHeal.Radius` | new | Unlocks the Radius modifier for Sacred Heal: put it in one of its 2 modifier slots - it levels up as you use Sacred Heal |
| 1 | Sacred Heal: Duration | 1 | `Class.Priest.m.SacredHeal.Duration` | new | Unlocks the Duration modifier for Sacred Heal: put it in one of its 2 modifier slots - it levels up as you use Sacred Heal |
| 1 | Blood Covenant | 3 | `Class.Priest.b1.r2a` | Priest.b1.r2a | Martyr's Grace heals 6% more per rank |
| 2 | **Sanctuary** | ABILITY (free) | - | Priest.b3.r2.free |  |
| 2 | **Martyr's Grace** | ABILITY (free) | - | Priest.b1.r2.free |  |
| 2 | Sanctuary: Radius | 1 | `Class.Priest.b3.r1a` | Priest.b3.r1a | Unlocks the Radius modifier for Sanctuary: put it in one of its 2 modifier slots - it levels up as you use Sanctuary |
| 2 | Sanctuary: Duration | 1 | `Class.Priest.b3.r2a` | Priest.b3.r2a | Unlocks the Duration modifier for Sanctuary: put it in one of its 2 modifier slots - it levels up as you use Sanctuary |
| 2 | Sanctuary: Power | 1 | `Class.Priest.b3.r2b` | Priest.b3.r2b | Unlocks the Power modifier for Sanctuary: put it in one of its 2 modifier slots - it levels up as you use Sanctuary |
| 2 | Martyr's Grace: Power | 1 | `Class.Priest.m.MartyrsGrace.Power` | new | Unlocks the Power modifier for Martyr's Grace: put it in one of its 2 modifier slots - it levels up as you use Martyr's Grace |
| 2 | Martyr's Grace: Chain | 1 | `Class.Priest.m.MartyrsGrace.Chain` | new | Unlocks the Chain modifier for Martyr's Grace: put it in one of its 2 modifier slots - it levels up as you use Martyr's Grace |
| 2 | Martyr's Grace: Efficiency | 1 | `Class.Priest.m.MartyrsGrace.Efficiency` | new | Unlocks the Efficiency modifier for Martyr's Grace: put it in one of its 2 modifier slots - it levels up as you use Martyr's Grace |
| 3 | Renewal | 3 | `Class.Priest.b1.r3b` | Priest.b1.r3b | Sacred Heal's heal-over-time +3% of the heal per rank |
| 3 | Martyr's Grace: Ward | 1 | `Class.Priest.m.MartyrsGrace.Ward` | new | Unlocks the Ward modifier for Martyr's Grace: put it in one of its 2 modifier slots - it levels up as you use Martyr's Grace |
| 3 | Martyr's Grace: Echo | 1 | `Class.Priest.m.MartyrsGrace.Echo` | new | Unlocks the Echo modifier for Martyr's Grace: put it in one of its 2 modifier slots - it levels up as you use Martyr's Grace |
| 3 | Sacred Heal: Echo | 1 | `Class.Priest.b1.r3a` | Priest.b1.r3a | Unlocks the Echo modifier for Sacred Heal: put it in one of its 2 modifier slots - it levels up as you use Sacred Heal |
| 3 | Sanctuary: Follow | 1 | `Class.Priest.b3.r3c` | Priest.b3.r3c | Unlocks the Follow modifier for Sanctuary: put it in one of its 2 modifier slots - it levels up as you use Sanctuary |
| 3 | Long Reach | 2 | `Class.Priest.b1.r3c` | Priest.b1.r3c | +8% heal range per rank |
| 4 | Consecrate | 2 | `Class.Priest.b3.r3a` | Priest.b3.r3a | enemies inside Sanctuary deal 4% less dmg per rank |
| 4 | Pilgrim | 3 | `Class.Priest.b3.r3b` | Priest.b3.r3b | allies in your zones gain +3% move speed per rank |
| 4 | Seek the Hurt | 1 | `Class.Priest.b1.r4a` | Priest.b1.r4a | Sacred Heal centres on the most hurt party member within 20 blocks |
| 4 | Triage | 3 | `Class.Priest.b1.r4b` | Priest.b1.r4b | allies below 40% Health get an extra 2% of max Health per rank from Sacred Heal |
| 4 | Shared Grace | 1 | `Class.Priest.b3.r4a` | Priest.b3.r4a | Sacred Heal on an ally inside Sanctuary also heals everyone else inside for 25% |
| 4 | Sanctified Mana | 3 | `Class.Priest.b3.r4b` | Priest.b3.r4b | allies inside your Sanctuary refill Mana 4% faster per rank |
| 5 | Parting Ward | 2 | `Class.Priest.b3.r4c` | Priest.b3.r4c | when Sanctuary ends, everyone inside keeps a ward of 3% of max Health per rank (5s) |
| 5 | Overheal | 3 | `Class.Priest.b1.r5a` | Priest.b1.r5a | Sacred Heal on a full-Health ally gives a ward of 4% of max Health per rank (5s) |
| 5 | Benediction | 3 | `Class.Priest.b1.r5b` | Priest.b1.r5b | healed allies gain +3% move speed per rank for 3s |
| 5 | Humble Ground | 3 | `Class.Priest.b3.r5a` | Priest.b3.r5a | Sanctuary costs -8% Mana per rank |
| 5 | Radiant Beacon | 3 | `Class.Priest.b3.r5b` | Priest.b3.r5b | allies inside your Sanctuary deal +2% damage per rank |
| 5 | Holy Land | 1 | `Class.Priest.b3.r6` | Priest.b3.r6 | Sanctuary holds 2 charges, so 2 can stand at once; allies where they overlap heal 150%, and nobody inside can be knocked back |
| 6 | Miracle | 1 | `Class.Priest.b1.r6` | Priest.b1.r6 | Sacred Heal on an ally below 20% Health heals them again in full and cleanses them (8s per ally) |

### Branch 2 - Bulwark (shields, damage prevention)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | Stronger Shields | 3 | `Class.Priest.b2.r1a` | Priest.b2.r1a | your shields absorb +5% more per rank |
| 1 | Steadfast | 3 | `Class.Priest.b2.r1b` | Priest.b2.r1b | -4.5% damage taken per rank while your Shield Bubble is up or you have a ward |
| 1 | Smite | 3 | `Class.Priest.b3.r1b` | Priest.b3.r1b | your wand bolts deal +4.5% per rank and keep full damage 2 blocks farther per rank (they already pierce every enemy) |
| 1 | Rebound | 1 | `Class.Priest.b2.r2c` | Priest.b2.r2c | when the bubble breaks, it pushes enemies back 3 blocks |
| 2 | **Shield Bubble** | ABILITY (free) | - | Priest.b2.r2.free |  |
| 2 | Shield Bubble: Duration | 1 | `Class.Priest.b2.r2a` | Priest.b2.r2a | Unlocks the Duration modifier for Shield Bubble: put it in one of its 2 modifier slots - it levels up as you use Shield Bubble |
| 2 | Shield Bubble: Radius | 1 | `Class.Priest.b2.r2b` | Priest.b2.r2b | Unlocks the Radius modifier for Shield Bubble: put it in one of its 2 modifier slots - it levels up as you use Shield Bubble |
| 2 | Shield Bubble: Power | 1 | `Class.Priest.m.ShieldBubble.Power` | new | Unlocks the Power modifier for Shield Bubble: put it in one of its 2 modifier slots - it levels up as you use Shield Bubble |
| 3 | Swift Prayer | 3 | `Class.Priest.b1.r2b` | Priest.b1.r2b | -4% cooldown on every Priest ability per rank (cast speed is fixed in Hytale) |
| 3 | Shield Bubble: Follow | 1 | `Class.Priest.m.ShieldBubble.Follow` | new | Unlocks the Follow modifier for Shield Bubble: put it in one of its 2 modifier slots - it levels up as you use Shield Bubble |
| 3 | Light Bubble | 3 | `Class.Priest.b2.r3a` | Priest.b2.r3a | Shield Bubble costs -6% Mana per rank |
| 4 | Aegis Link | 3 | `Class.Priest.b2.r3b` | Priest.b2.r3b | players inside your Shield Bubble take 4% less damage per rank |
| 4 | Shield Bubble: Echo | 1 | `Class.Priest.b2.r4a` | Priest.b2.r4a | Unlocks the Echo modifier for Shield Bubble: put it in one of its 2 modifier slots - it levels up as you use Shield Bubble |
| 4 | Hold the Line | 2 | `Class.Priest.b2.r4c` | Priest.b2.r4c | after the bubble breaks, allies who were inside take 4% less dmg per rank for 3s |
| 4 | Clarity | 2 | `Class.Priest.b1.r4c` | Priest.b1.r4c | +5% Mana regen per rank |
| 5 | **Guardian Spirit** | ABILITY (free) | - | Priest.b2.r5.free |  |
| 5 | Spirit's Shelter | 3 | `Class.Priest.b2.r5a` | Priest.b2.r5a | a player Guardian Spirit saves takes 50% less damage for 0.5s per rank |
| 5 | Guardian Spirit: Power | 1 | `Class.Priest.b2.r5b` | Priest.b2.r5b | Unlocks the Power modifier for Guardian Spirit: put it in one of its 2 modifier slots - it levels up as you use Guardian Spirit |
| 5 | Guardian Spirit: Radius | 1 | `Class.Priest.m.GuardianSpirit.Radius` | new | Unlocks the Radius modifier for Guardian Spirit: put it in one of its 2 modifier slots - it levels up as you use Guardian Spirit |
| 5 | Guardian Spirit: Efficiency | 1 | `Class.Priest.m.GuardianSpirit.Efficiency` | new | Unlocks the Efficiency modifier for Guardian Spirit: put it in one of its 2 modifier slots - it levels up as you use Guardian Spirit |
| 5 | Guardian Spirit: Ward | 1 | `Class.Priest.m.GuardianSpirit.Ward` | new | Unlocks the Ward modifier for Guardian Spirit: put it in one of its 2 modifier slots - it levels up as you use Guardian Spirit |
| 5 | Spirit's Reach | 1 | `Class.Priest.b2.r5c` | Priest.b2.r5c | Guardian Spirit reaches 4 blocks farther |
| 6 | Undying Vigil | 1 | `Class.Priest.b2.r6` | Priest.b2.r6 | a Guardian Spirit save also raises a free Shield Bubble on the saved player; the save's wait is 30% shorter |

### Branch 3 - Weaponcraft (weapons, defence, loot)

| Row | Node | Ranks | Key | Was | What it does |
|---|---|---|---|---|---|
| 1 | **Combat Focus** | free passive | - | Combat.b1.r1.free | +3% damage |
| 1 | Hone Edge | 5 | `Skill.Combat.b1.r1a` | Combat.b1.r1a | +2% weapon damage/rank |
| 1 | Toughness | 5 | `Skill.Combat.b2.r1a` | Combat.b2.r1a | +0.5% max Health/rank |
| 1 | Scavenger | 5 | `Skill.Combat.b3.r1a` | Combat.b3.r1a | +2% chance/rank a kill drops 1 more item of its loot (never gear) |
| 1 | Coin Purse | 3 | `Skill.Combat.b3.r1b` | Combat.b3.r1b | 3% chance/rank a kill also pays coins (the mob's level) |
| 2 | **Blessed Wand** | free passive | - | Priest.b3.r1b | your wand bolts deal +2% damage (always on) |
| 2 | Weak Spot | 3 | `Skill.Combat.b1.r1b` | Combat.b1.r1b | +2% crit chance/rank |
| 2 | Iron Will | 3 | `Skill.Combat.b2.r1b` | Combat.b2.r1b | +3% knockback resistance/rank |
| 2 | Momentum | 4 | `Skill.Combat.b1.r3b` | Combat.b1.r3b | +1% move speed/rank |
| 2 | Rally | 3 | `Skill.Combat.b2.r4b` | Combat.b2.r4b | +3% Health regen out of combat per rank |
| 3 | Finisher | 3 | `Skill.Combat.b1.r3a` | Combat.b1.r3a | +4% damage/rank to enemies below 30% Health |
| 3 | Thick Skin | 4 | `Skill.Combat.b2.r3a` | Combat.b2.r3a | +2% damage reduction/rank |
| 3 | Pet Fang | 5 | `Skill.Combat.b3.r3a` | Combat.b3.r3a | +2% combat XP and +1% damage per equipped Combat pet tier, per rank |
| 3 | Rare Drop | 3 | `Skill.Combat.b3.r3b` | Combat.b3.r3b | +1% chance/rank a kill drops 1 more of its rarest loot (never gear) |
| 3 | Reprisal | 3 | `Skill.Combat.b2.r3b` | Combat.b2.r3b | 3% of the melee damage you take is dealt back to the attacker per rank |
| 4 | Crit Mastery | 3 | `Skill.Combat.b1.r4a` | Combat.b1.r4a | +3% crit damage/rank |
| 4 | Gear Resonance | 3 | `Skill.Combat.b1.r4b` | Combat.b1.r4b | +2% damage per combat-tagged armor piece/rank |
| 4 | Accessory Plates | 3 | `Skill.Combat.b2.r4a` | Combat.b2.r4a | +0.5% max health per filled accessory slot, per rank |
| 4 | Boss Hunter | 3 | `Skill.Combat.b3.r4a` | Combat.b3.r4a | +3% chance/rank a boss or mini boss drops its loot once more (never gear) |
| 4 | Bastion | 3 | `Class.Priest.b2.r4b` | Priest.b2.r4b | +3% max HP per rank |
| 5 | **Vigor** | free passive | - | Priest.b2.r4b | +3% max Health (always on) |
| 5 | Trophy Hunter | 3 | `Skill.Combat.b1.r5a` | Combat.b1.r5a | +3% damage/rank to bosses and mini bosses |
| 5 | Weapon Tempering | 4 | `Skill.Combat.b1.r5b` | Combat.b1.r5b | +1% damage per metal tier above Iron per rank (max +20%) |
| 5 | Lucky Kill | 3 | `Skill.Combat.b3.r5a` | Combat.b3.r5a | 2% chance/rank a kill drops its whole loot twice (never gear) |
| 5 | Battle Insight | 5 | `Skill.Combat.b3.r5b` | Combat.b3.r5b | +2% class XP/rank |
| 5 | Second Wind | 3 | `Skill.Combat.b2.r3c` | Combat.b2.r3c | once a fight, a hit that drops you below 20% Health heals you 5% of max Health per rank |
| 6 | Edge of the Legend | 1 | `Skill.Combat.b1.r6` | Combat.b1.r6 | +10% damage to enemies below 30% Health |

## Combat parts dropped (never buildable: coming soon, no applier)

`Combat.b1.r2.free`, `Combat.b1.r2a`, `Combat.b1.r2b`, `Combat.b1.r2c`, `Combat.b1.r3c`, `Combat.b1.r5c`, `Combat.b2.r2.free`, `Combat.b2.r2a`, `Combat.b2.r2b`, `Combat.b2.r5a`, `Combat.b2.r5b`, `Combat.b2.r6`, `Combat.b3.r2.free`, `Combat.b3.r2a`, `Combat.b3.r2b`, `Combat.b3.r3c`, `Combat.b3.r4b`, `Combat.b3.r6`

## Per-rank numbers raised (four power sources, x1.5)

`Class.Warrior.b1.r1a` drMelee 4 -> 6, `Class.Warrior.b1.r3b` drRanged 3 -> 4.5, `Class.Warrior.b1.r5b` drStill 3 -> 4.5, `Class.Berserker.b3.r1b` dmgMelee 3 -> 4.5, `Class.Berserker.b1.r1b` dmgLowHp 4 -> 6, `Class.Monk.b1.r2a` fistsDmg 5 -> 7.5, `Class.Assassin.b2.r1a` dmgWeapon 3 -> 4.5, `Class.Assassin.b2.r5b` dmgElite 3 -> 4.5, `Class.Assassin.b1.r3b` dmgBehind 4 -> 6, `Class.Assassin.b3.r3b` dmgDebuff 3 -> 4.5, `Class.Archer.b1.r3a` dmgFar 5 -> 7.5, `Class.Archer.b1.r2b` dmgBow 3 -> 4.5, `Class.Archer.b2.r5b` drRooted 3 -> 4.5, `Class.Archer.b1.r4b` dmgMarked 5 -> 7.5, `Class.Mage.b1.r2c` spellPow 4 -> 6, `Class.Mage.b3.r1b` drMagic 2 -> 3, `Class.Priest.b2.r1b` drShieldUp 3 -> 4.5, `Class.Priest.b3.r1b` dmgWeapon 3 -> 4.5
