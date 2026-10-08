# Rod + reel look: one rod item, many reels (research 2026-10-07)

Skyy: "regarding rods, how does swapping reels work with the item look? can we make it show a cobalt rod with an adamantine reel? or will
we have to make an item for every combination?" (rod icon pick: "second row for the rod" = the 3D renders.)

## Engine facts (VERIFIED in Assets.zip / HytaleServer.jar, 2026-10-07)

- No vanilla held item switches its model through item `State` (only blocks do).
- `ItemAppearanceConditions` on an item JSON maps an **entity stat name** to a list of `{Condition: [min, max], ConditionValueType?,
  Model?, Texture?, ModelVFXId?, Particles?, FirstPersonParticles?, LocalSoundEventId?, WorldSoundEventId?}`. While the holder's stat is
  in range, the item shows that Model / Texture. Examples: `Weapon_Axe_Iron.json` swaps model + texture on `Health` ranges;
  `Template_Glider.json` swaps the glider model on its OWN stat `GlidingActive` (`Server/Entity/Stats/GlidingActive.json`) - so a mod can
  add a stat just to drive a look. Classes: `server/core/asset/type/item/config/ItemAppearanceCondition`.

## Plan (default until Skyy says otherwise)

- **8 rod items** (one per rod tier), not 64. The reel is stored on the rod (SkyyFishing data, not a new item id).
- A new stat `SkyyFishing_Reel` (0 = none, 1..8 = reel tier). When a player holds a rod, SkyyFishing sets the stat to that rod's reel
  (on hotbar change / reel swap), 0 otherwise.
- Each rod JSON carries 9 `ItemAppearanceConditions` entries on `SkyyFishing_Reel` -> the rod model with that reel's texture (or a model
  variant if reel shapes differ). `tools/art/make_fishing.py` generates the 8 x 8 textures automatically (cheap).

## Limits (UNVERIFIED until tested in game)

- The inventory ICON is per item id: it shows the rod's default reel; the tooltip names the fitted reel.
- A dropped rod / a rod in a chest shows the default reel (no holder stat).
- Whether OTHER players see the swapped look depends on the stat being synced to them (likely - Health swaps are visible - but test).
- Alternative if this fails: one item per rod x reel combo (64 ids, correct icons, clutters recipes / the Bazaar).
