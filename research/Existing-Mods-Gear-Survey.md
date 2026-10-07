# Existing Hytale mods vs. our gear plans (survey 2026-10-07)

Skyy: "Before we spend a ton or time and effort making our own armor, lets see if there are already mods that add some or all of what
we need". Two read-only scans: every archive in Skyy's `UserData/Mods` folder, and the CurseForge Hytale section (Modrinth / Nexus /
GitHub not searched). Licence rule (PACK.md): we may react to other mods' item ids at runtime; copying models / textures / recipes needs
the author's OK.

## Licences

- Installed mods: **none** ships a licence file or a manifest `License` field = all rights reserved by default.
- CurseForge: almost all "All Rights Reserved"; open ones: Bracken's Rebalanced Gear (MIT, stats only), Cosmetic Pack: Modular Armor
  (Creative Commons 4.0, variant not shown). No page states modpack permission.
- Enabled in Skyy's test world today: BetterMap, Saplings From Trees, NoCube Orchard, More Crossbow Tiers, HyFishing, DynamicSeasons.

## What exists, per need

| Need | Closest existing | Notes |
|---|---|---|
| Light leather armor per metal tier | nothing | Vanilla+ Armors (Shini9966, ARR: Chieftain / Scout variants of the vanilla metals), Improved Crafting (andzejsw, ARR: unlocks 18 creative-only vanilla sets) - neither is our look |
| Heavy armor ladder, gathering armor | nothing | TheArmoryMod (LadyPaladra, 1,338 items: Iron armor in 10+ colours, shields, axes, maces, cosmetic helms) = reference only |
| Cloth ladder + spellbooks | SLVR Arcane Robes & Spells (SlverSkull: Wool/Cotton/Linen/Silk/Cindercloth/Raven x 4 slots, 5 spellbooks), Arcane Power (Tayko: 2 cloth sets, 9 element spellbooks), TheLostWorlds (cloth names) | closest fit; ask before reuse |
| Metal staffs | Hexcode (Riprod: Hexstaff in 9 metal tiers, no own models), EndgameAndQoL (Lewai: Staff Copper..Prisma 8 tiers, mostly vanilla reuse; also overrides vanilla Armor_* ids), HyboardsPack (metal staffs + Bo Wood/Bamboo) | ours (R1 recolour like the wands) is still needed for the look |
| Spellbook plus / custom spells | Spellbook Plus (Hexora, custom licence, 5 staff tiers, node-graph spells) | mechanics idea only |
| Kunai | Zephyr (narwhals: one kunai + karambit), Kunai With Ammo (recipe for the unused vanilla kunai) | vanilla has a kunai model - check |
| Soul cage / orb, bo staff tiers, gauntlets, claws, hand wraps | nothing (StarTale Beskar Gauntlets, Armory Demon Gauntlets, FL's Radiant Fists = single items) | ours |
| Booster accessories | HyBaubles (Gameboy612, ARR: 8 slots, stat API, addons, v0.6), Accessories (Adkyn, ARR: 6 slots, models do not render), Aetherhaven (Hexvane: ~30 gold/silver gem rings + necklaces), TerrariaAddons (boots, charms), FlyRing | slot libraries could be a DEPENDENCY; Aetherhaven gem x metal grid = layout reference |
| Fishing rods / parts | HyFishing (in pack, 1 rod), Anglers' Almanac (RM20, 5 rods: Crude/Iron/Cobalt/Reef/Saltworn, contact in manifest), Cozy Tales - Fishing (Hexvane, ARR: rods to Adamantite, bobbers) | no reels / hooks / lines / sinkers anywhere |

## Verdict

1. Nothing covers tiered black-leather light armor, heavy / gathering ladders, soul cage, monk weapons or fishing parts - build our own.
2. Worth an author message if Skyy wants to build on them: SlverSkull / Tayko (cloth + spellbooks), Riprod / Lewai (metal staffs),
   RM20 (rod ladder), Gameboy612 (HyBaubles accessory slots).
3. Conflicts to remember: PJ-HyperGlowingArmors and EndgameAndQoL override vanilla armor ids - do not enable them next to our
   re-leathered vanilla sets.
