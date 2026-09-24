# SkyWynn pack contents

> **Temporary:** Skyy's goal is that EVERY mod in the pack is our own. Each third-party mod below is a stopgap until we build our own version (our own items, stats and recipes - never copies of the author's files unless their license allows it).

The SkyWynn pack = the Skyy* mods in this repo (built from their build scripts, deployed with `python tools/deploy_set.py`) plus the
third-party mods below. Third-party mods are NOT stored in this repo: install them from their authors. `tools/deploy_set.py` enables
them in the world (PACK_THIRD_PARTY) but never copies their files.

## Third-party mods

| Mod (manifest key) | Author | Version tested | File in Skyy's Mods folder | Why |
|---|---|---|---|---|
| More Crossbow Tiers (`Serj:More Crossbow Tiers`) | Serj (SergioGMN) | 1.1.0 | More_Crossbow_Tiers.zip | Cobalt, Thorium, Mithril and Adamantite crossbows at the Weapon Bench (Skyy, 2026-09-24). SkyyClasses already treats every `Weapon_Crossbow_*` as an Archer weapon, and the /craft Smithing tab lists them. No dependencies. |
| Saplings From Trees (`Helios:Saplings From Trees`) | Helios | 1.0.4 | SaplingFromTrees-1.0.4.zip | Leaves of Ash, Azure, Beech, Birch, Cedar, Dry and Oak trees can drop their sapling (plus sapling recipes) - a sky island needs replantable trees (Skyy, 2026-09-24). Overrides the vanilla leaf item files; no other pack mod touches leaves. No dependencies. |

Not included: "Endgame&QoL expansion - Crossbow Tiers" (adds Onyxium + Prisma crossbows) needs the large Endgame&QoL mod.
Also not included (yet): SaplingOnLog (Helios; only tweaks two sapling items); Seed Drops (Familiar) - not needed, Hytale has its own seed system (Skyy, 2026-09-24).

Saplings: vanilla already crafts 31 of the 33 saplings at the Farming Bench from Life Essence (5-35; Apple = concentrated essence + 4 apples); only Crystal and Poisoned have no recipe. Saplings From Trees adds leaf drops plus Oak sapling -> Ash / Azure / Beech / Birch / Cedar / Dry at the Farming Bench.
