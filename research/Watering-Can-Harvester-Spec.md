# Lifelong Watering Can + the Harvester (hoe + sickle) - short spec

Skyy 2026-10-15 (docs/answered/gear.md WATERING CAN + HARVESTER): "we need a watering can too. and i want it to spawn with you and upgrade
like the forever tools. (at least tier up for more watering range ...) and id like to make a new kind of multitool the combines the hoe
and the sickle." Picked: name "Harvester", all four can upgrades, Harvester unlock "Same as multitool: rebirth 1".
Builds on research/Gathering-Shards-Spec.md sections 5 (lifelong tools) and 6 (Anvil); owner mod SkyyGear (+ SkyySkills Farming XP hooks).

## Survey (PROJECT-RULES 2)
- Vanilla 0.7.2 has NO watering-can item, but the engine keeps the farming interaction (`UseWateringCanInteraction`,
  `Watering_Can_Use` / `Watering_Can_Use_3x3` - research/Durability-Switch-Research.md) and the `Soil_Dirt_Tilled_Watered` block state.
- Installed mods with cans: AdvancedFarming 1.3.1 (metal tiers, bigger cans - ideas only, licence none), Farming_Overhaul 2.4.0
  (kept OFF - clashes with our sickle gate), NoCube_Cultivation 0.1.0 (Copper / Thorium cans), ProjectCivicCore, Aetherhaven (sprinklers).
  Builder checks PACK.md licences: fold only MIT / PD / CC BY art; otherwise our own model / icon, learning from how they wire the
  interaction + the per-state water level (read only).
- Duplicates rule: if any pack mod adds a watering can item players can get, ours is the one that stays (the lifelong one); note it in PACK.md.

## Watering Can (lifelong kind `can`)
- Every new profile spawns with a T1 Crude (wooden) Watering Can (like pickaxe / hatchet / hoe / sickle; existing profiles get one once, on next login,
  through the same lifelong issue path; `/gearadmin lifelong <player> can` re-issues). One per profile, Reclaim on loss, no recipe.
- Level follows Farming (avg) like the hoe / sickle. Rarity + Sigils + Reforge as every lifelong tool.
- **Tiers (Skyy: "a T1 crude watering can, (made of wood.) upgrades to a T2 copper T3 iron and so no"):** T1 Crude (wooden can),
  T2 Copper, T3 Iron, then the next metals of the lifelong tool ladder. **Tier-up = watering area:** T1 1x1, T2 3x3, T3 5x5, T4 7x7
  (higher tiers: more reach / range, numbers in Server Setup). Each tier its own look (wood, copper, iron, ...).
- **Point upgrades (Tools tab):**
  | Upgrade | Effect (defaults, editable) |
  |---|---|
  | Capacity / refill | +uses before a refill per point; top step = never runs dry (refills slowly by itself, fast in rain) |
  | Growth boost | crops watered by this can grow +X% faster (stacks with rain's x2.5 farming modifier, capped) |
  | Lasting water | watered soil stays wet +X% longer |
  | Bloom | chance per watering to also fertilize the block; small bonus-crop chance at harvest of a Bloomed crop |
- Refill: right-click water (as vanilla cans did); a T-gated or upgraded can may refill anywhere (top Capacity step).

## Harvester (hoe + sickle)
- After rebirth 1, the Anvil offers "Merge into Harvester" for the lifelong hoe + sickle (multitool rules: best rarity, merged lines,
  points kept). One tool tills (right-click) and reaps (swing) - both vanilla interactions on one item.
- Name per tier: Crude / Copper / Iron / ... Harvester. Lifelong kind `harvester` replaces `hoe` + `sickle` for that profile; undo =
  none (like the multitool).

## Build (after SkyyGear 0.3.10 lands - one writer per mod)
Full round (saved data: a new lifelong kind, a one-time issue to existing profiles). SkyyGear + SkyySkills (Farming XP for watering? -
default no XP, only crops) + SkyyMenu text. Icons / model: our own (menu-icons family), or licence-allowed fold.

## Questions (default in brackets)
1. Watering gives Farming XP? [no - only harvested crops do]
2. Harvester art: our own new model, or the multitool look? [our own]
