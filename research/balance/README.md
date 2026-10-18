# research/balance - P0 inventory of every current balance number (2026-10-18)

What is here: the "dump every current number" step (P0) of `research/Balance-Pass-Spec.md` section 8. Later phases (P1-P9) edit numbers;
this is the before-picture. Read-only inventory: nothing here changes the game.

| File | Area |
|---|---|
| xp.md | level curves (general, class, Mining / Farming lists), XP per action per skill + class, perks, class boosts, mana/stamina bases, rebirth caps, skill-tree points, Exploration |
| combat.md | mob level curve (hp / dmg per level, 3 difficulties), level bands + zone biomes, strength per level, class ability costs / cooldowns / power |
| gear.md | SkyyGear config (stats, rarity, odds, UT, soul, level-up/reforge costs, benches), SkyyArmory, Shards/Wardrobe, tier ladder + level bands (tier_tags.py) |
| accessories-pets.md | booster charm tables, Accessory Power, Lantern, Furnace Charm costs, pet kinds / rarity / level curves / hatch |
| gathering.md | collection curves + rewards, fishing, cooking, Exploration spots, design-spec hits-per-block / smelting |
| economy.md | Bazaar base prices + pricing modes, Auction House, coins, bank, vault, sacks, merchants, quest rewards |

Each file: Part 1 = live configs (`UserData/Saves/NewBetaTest/mods/Skyy_<Mod>/*.properties`, row = key | value | line in that file; what the
server runs today). Part 2 = defaults found only in the pinned build scripts (`<Mod>/build_<mod>_<ver>.py`, versions = `tools/deploy_set.py` SET),
extracted by a free OpenRouter model and spot-checked; its line column is approximate - grep the key in the named script.

Known gaps / uncertain: hits per block, crop growth times and smelting times are vanilla asset data or live in code not reached by the
extraction - the gathering.md rows from `research/*Spec.md` are DESIGN values, not verified against the build. Per-class Health / Defense
curves are the `classBoost.*`, `overall.healthPerLevel`, `perk.*` and `mana.*` / `stamina.*` rows (xp.md); target roles are in
`research/Class-Roles-Sheet.md`. Pet level stats beyond `kind.*` rows and charm craft costs are only as complete as the extraction.
Regenerate Part 1 by re-reading the live configs (the generator was scratch and is deleted).
