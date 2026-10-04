# Pets, combat companions and mounts - one system (IDEA, direction agreed 2026-10-01, not planned in detail yet)

> **Skyy's decisions 2026-10-02 win over this draft:** OPEN-QUESTIONS.md, section "Q&A with Skyy 2026-10-02", rounds 6, 7 and 9.

Related: research/Dragon-Pets-Idea.md (dragons = the top tier of this system), research/SkyyWorldGen-Plan.md.

## Agreed with Skyy (2026-10-01)

- **One pet system, not three.** Hypixel SkyBlock-style pets are the base, mixed with companions and mounts (instead of Wynncraft
  horses). Skyy: "sounds great!"
- **Every pet gives buffs** that grow as it levels (SkyBlock core).
- **Better pets can fight:** at higher rarity / level a pet is bigger, follows you and helps in combat.
- **Some pets can be ridden.** All mounts are pets, but not all pets are mounts.
- **Two slots:**
  - **Active pet slot** - any pet: its buffs, plus combat if it has it.
  - **Mount slot** - a second slot that has to be **unlocked**; **only mount pets** can go in it. A pet in the mount slot **still gives its
    buffs, but weaker** (see question 2).
- **Dragons** are the rarest pets with all three abilities (buffs, combat, flying mount), hatched through their own quest line and
  elements (Dragon-Pets-Idea.md).
- **Balance rule (main-session proposal, agreed with the direction):** a pet's buff strength comes from its rarity and level, not from
  whether it fights or can be ridden - fighting and riding are bonuses on top.

## Pet types (Skyy 2026-10-01: "mainly skyblock style")

| Type | What it boosts | At launch |
|---|---|---|
| Farming pets | Farming (crop fortune, farming XP, ...) | yes |
| Mining pets | Mining (mining speed / fortune, mining XP, ...) | yes |
| Foraging pets | Foraging (foraging fortune, tree felling, foraging XP, ...) | yes |
| General combat pets | combat for every class (damage, health, defense, ...) | yes |
| **Class pets** | geared towards one class's weapons / role | **at least ONE per class at launch**: Archer, Warrior, Mage, Berserker, Priest (Assassin / Shaman when those classes ship) |

Class pet examples (ideas only, models to check in Assets.zip): Archer - a hawk (ranged / crit; `Avian/Raptor/Hawk` exists); Warrior - a
guard-type beast (defense, block); Mage - an arcane / spirit creature (Magical Power, Mana); Berserker - a boar or bear (Strength, attack
speed); Priest - a gentle support creature (healing done, Mana regen). Later skill types can get pets too (Fishing, Cooking, Alchemy ...).

## Build order (when this gets planned)

1. Buff pets (stat modifiers, the same kind SkyyGear / SkyyAccessories already apply) - doable now.
2. Combat companions - needs research: an NPC that follows and fights for its owner, size growing with level.
3. Ground mounts - needs research: Hytale's mount system with our own creatures.
4. Flying mounts (dragons) - the biggest unknown.

## Open questions (recommended default in brackets)

1. **How is the mount slot unlocked?** [A quest at the Zone 2 town - you reach Zone 2, a stable master gives you the slot and your first
   mount pet. Alternatives: a skill level, coins, a rank perk.]
2. **Mount-slot buffs: always on at reduced strength, or only while the mount is summoned / ridden?** [Always on at 50% (Server Setup
   row). "Only while summoned" makes the slot do nothing most of the time and needs summon tracking. While riding, the mount can add its
   own travel perks (speed, stamina) on top.]
3. Pet XP: from the skill the pet belongs to (SkyBlock: a mining pet levels from Mining XP), or from everything you do? [Its skill, plus a
   small share of all XP.]
4. Pets per profile or per player? [Per profile, like the rest of SkyWynn's progression.]

- 2026-10-04: Skyy found the VANILLA item "Egg Spawner - Pet Lantern" (Epic) in game and liked it ("didnt realize these pet lantern things were in the game. thats pretty cool"). Vanilla already has spawnable pets - check its NPC (follow / light behaviour) before building our own pet code; a candidate first pet, and a natural partner for the Lantern accessory line.
