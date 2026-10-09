# Signature proposals for the new weapon families

Follows: `docs/answered/gear.md` 2026-10-08 lines 108-110 (every weapon keeps its vanilla SIGNATURE on Ability 1, charged by use into the
SignatureEnergy meter, charge kept per weapon across swaps; wands get a ricochet shot through 8 enemies - built in SkyyArmory 0.1.14:
first target nearest the crosshair, then 7 bounces, -10% per bounce). Bo, wraps / gauntlets, kunai and spellbooks have none yet. Draft, no code.

## Rules used for every option

- A signature is a **weapon move**, not a class ability: it never costs mana / energy, is charged only by hitting things, and is not the
  family's charged move (Pole-Vault, Rising Strike, Throw + Teleport, Levitate) or any class ability (Monk: Flowing Form, Hundred Fists,
  Still Water, Palm Strike, Cyclone Kick; Assassin: Cloak, Shadow Clone, Vanishing Act, Toxin, God Killer; Mage: Meteor, Starfall,
  Arcane Beam, Mana Barrier, Frost Nova).
- Damage is told as a multiple of one normal light hit ("1 hit"). Vanilla signatures are tagged `Signature` damage and never count as
  Charged (`research/Charged-Attack-Research.md`) - ours should reuse that tag.
- Vanilla notes (all **UNVERIFIED** here, no game files in the cloud): the sword signature is Vortexstrike (spin 12 / stab 35 in
  `research/Gear-Levels-Wynn-Spec.md`), daggers Razorstrike, crossbow BigArrow (kept across slot switch), shortbow Volley (charges
  0.75 / 1.5 s, volley of arrows). Pattern: one big, readable burst that shows the weapon's identity.

## Bo staff (Monk) - charged move is Pole-Vault (lunge + vault, kick 2x)

| | Option | Damage idea | Why it fits |
|---|---|---|---|
| A | **Sweep the Legs**: a low spinning sweep, hits all around you in 3 blocks and knocks enemies down for ~1 s | ~2 hits each | Classic staff move; crowd control without leaving the ground (Pole-Vault leaves it). |
| B | **Whirling Staff** (recommended): spin the staff overhead for ~1.5 s, 3-4 hits on everything within 3 blocks, you may walk slowly | 4 x 0.6 hit | Reads as a martial-arts flourish; ticks reward a Monk who is already surrounded; not Cyclone Kick (a kick, one burst). |
| C | **Vault Strike**: slam the staff down in front, a 4-block line of shock | ~3 hits in a line | Long reach for a disruptor; close to Palm Strike in feel, so weakest. |

Engine risk: B needs a timed multi-hit (like vanilla Whirlwind / Vortexstrike - reuse that chain, UNVERIFIED); movement while spinning is the only new part.

## Hand wraps and gauntlets (Monk) - charged move is Rising Strike / Plunge Punch

| | Option | Damage idea | Why it fits |
|---|---|---|---|
| A | **Flurry** (recommended): 6 very fast jabs at the nearest enemy in front, the last one knocks back | 6 x 0.5 hit (~3 hits) | The fist fantasy (Hundred Fists is a class ability with Awed; Flurry is plain damage, no Awed). |
| B | **Shockwave Palm**: a ground-hugging wave 6 blocks forward, passes through enemies | ~2 hits each, no falloff | Ranged option for fists; differs from Rising Strike (vertical) and Palm Strike (single target). |
| C | **Counter Stance**: 1 s guard, any hit taken in it is returned as a strike at the attacker | 2 x the hit taken (cap) | Fits "single-target control"; harder to build (needs a damage-taken hook). |

Engine risk: A is a chain of short melee steps (low). B needs a projectile or ray with pierce (medium). C needs an incoming-damage hook (high).
Gauntlets use the same options, heavier numbers (+25%, slower).
Claws (later, Monk fist family): same list; claws could swap A for a bleeding Flurry (bleed 3 s) - decide when claws are built.

## Kunai (Assassin) - charged move is Throw + Teleport (hold = return)

| | Option | Damage idea | Why it fits |
|---|---|---|---|
| A | **Kunai Fan** (recommended): throw 5 kunai in a narrow fan, each 0.8 hit, a target hit by 3+ takes a bonus 1 hit | up to ~5 hits on one target | Straight "many sharp things" assassin identity; no teleport, so it stays apart from the charged throw. |
| B | **Chain Throw**: one kunai that pins its target for 1 s, then you pull it 3 blocks to you | 2 hits + short root | Control kit for a single target; slightly overlaps Toxin utility, fine. |
| C | **Smoke Bomb**: a kunai that bursts into smoke at the target, enemies in 3 blocks lose aim for 2 s | 1 hit + blind | Stealth flavour, but close to Vanishing Act / Cloak. |

Engine risk: A is several projectiles from one use (vanilla Volley already does this, UNVERIFIED); B needs a pull (knockback toward the player) - medium; C needs a mob-targeting debuff - high.
Daggers: Shadow Step is the charged move (planned to replace Pounce), the vanilla Razorstrike signature stays - nothing new needed.

## Spellbooks (Mage) - charged move is Levitate (float up 8 blocks); Page Burst is the basic attack

| | Option | Damage idea | Why it fits |
|---|---|---|---|
| A | **Page Storm** (recommended): throw a swirl of pages in a 5-block circle around you for 2 s, each page ticks | ~4 hits over 2 s to everything inside | A book's fantasy, short range balances against staffs; unlike Starfall (sky) and Frost Nova (freeze, class). |
| B | **Tome Slam**: close the book, a shockwave out to 4 blocks, knocks back | ~2.5 hits | Simple and reliable; a panic button. |
| C | **Forbidden Page**: read a page that marks the nearest enemy; 2 s later it takes a hit scaled by mana spent while marked | 3-5 hits | Mage identity, but a mana hook makes it fiddly. |

Engine risk: A is a timed area tick centred on the player (low-medium, like Frost Nova / Arcane Beam ticks); B low; C needs a mana-spent tracker - high.

## Later families

Soul cage (Mage? Summoner? - no class file settles this): **UNVERIFIED** which class owns it; propose one line when it is designed. Suggest the signature
**Soul Harvest** (burst that heals / charges based on enemies hit), decide later.

## Cross-cutting notes

- All new signatures reuse the same charge meter and the existing "kept per weapon" rule, so the charge is the same code path as the wand.
- Charge rate: the wand charges on hits; keep every new family on hits too (not time), tuned so a signature is ready every ~8-10 hits.
- Wand ricochet is the benchmark: ~5 hits of damage in total over 8 targets. Keep new signatures near ~3-5 hits of single-target damage.

## Questions for Skyy (default = recommended)

1. Bo staff signature: A Sweep the Legs / B Whirling Staff / C Vault Strike? [B]
2. Wraps + gauntlets (and later claws): A Flurry / B Shockwave Palm / C Counter Stance? [A]
3. Kunai: A Kunai Fan / B Chain Throw / C Smoke Bomb? [A]
4. Spellbooks: A Page Storm / B Tome Slam / C Forbidden Page? [A]
5. Charge from hits only, ~8-10 hits per signature? [yes]
6. Claws get the same signature as the wraps, with bleed? [yes]

## For the local session

- UNVERIFIED: the vanilla signature chains (Vortexstrike, Razorstrike, BigArrow, Volley) - read them in Assets.zip and reuse for Whirling Staff, Flurry, Kunai Fan.
- UNVERIFIED: can one signature root hold a multi-projectile spawn and a pierce ray (options Kunai Fan A, Shockwave Palm B)?
- UNVERIFIED: whether an Ability 1 root can be defined for a new weapon family in SkyyArmory the same way as the wand did (0.1.14).
- Soul cage owner class: ask Skyy when it is scheduled.
