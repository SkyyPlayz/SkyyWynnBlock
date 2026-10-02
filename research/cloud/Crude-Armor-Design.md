# Crude armor set - design (the new Lv 1 starter armor)

Cloud draft, 2026-10-02. Paper design; asset work (models, textures, recipes JSON) is local. Skyy 2026-10-01: vanilla has crude weapons but
no crude armor, so we add a Crude set as the first Lv 1 gear of the starter shard chain (`research/Isles-of-the-Void-Lore.md`,
Story-Script-Draft quest 8 "Crude Awakening"). Numbers follow `research/Gear-Levels-Wynn-Spec.md` section 3.4 (armor base stats).

## 1. The comparison: vanilla's weakest armors

| Set (vanilla) | Health, full set | Physical / Projectile resist | Source |
|---|---|---|---|
| **Copper** (the weakest vanilla set) | **25** (head 5, chest 9, legs 7, hands 4) | about 18% (head 3.6, chest 6.48, legs 5.04, hands 2.88) | Gear-Levels-Wynn-Spec 3.4, VERIFIED there; a web guide agrees (Copper greaves +7 HP, +5% resist) |
| Wool / Leather / Iron / Bronze | 46 | about 25% | Gear-Levels-Wynn-Spec |
| Thorium / Cobalt | 61 | about 32% (Thorium also poison resist) | Gear-Levels-Wynn-Spec; web: Thorium cuirass +22 HP +12% |
| Adamantite / Mithril | 68 | about 40% | same |

There is no Feet slot: the four pieces are Head, Chest, Legs, Hands.

## 2. The Crude set (proposal)

Rule: Crude has to be **clearly weaker than Copper**, so the player wants to leave it, and it must not break the "same level = about the same stats" rule.
How: Crude is its own material with a **material factor 0.8** on the Lv 1 base (the opposite of a material bonus), and a short level band.

| Piece (working names) | Slot | Health at Lv 1 | Resist at Lv 1 (Physical = Projectile) |
|---|---|---|---|
| Crude Cap | Head | 4 | 2.9% |
| Crude Vest | Chest | 7 | 5.2% |
| Crude Leggings | Legs | 6 | 4.0% |
| Crude Wraps | Hands | 3 | 2.3% |
| **Full set** | | **20** | **14.4%** |

That is 80% of Copper at Lv 1 (25 HP, 18%). Crude has no extra lines (no poison, mana or fire), no set bonus, and low durability (placeholder: 60% of Copper's).

### Level band and growth
| Item | Value |
|---|---|
| Entry key (Server Setup -> Gear -> Levels) | `Armor_Crude` = **1** (the Lv 1 start, like `Armor_Copper` = 1) |
| Band | **1-8**. Crafting above the cap makes it AT the cap (Gear spec rule). At Lv 8: F(8) is about 1.85 -> 37 HP, R(8) is about 1.32 -> 19% for a set |
| Overlap with Copper | Copper armor band is 1-18. At Lv 8 a Crude set (37 HP, 19%) is weaker than a Lv 8 Copper set (46 HP, 24% with the same curves and no bonus) - the 0.8 factor keeps that true at every level |
| Gate | Your class skill (Gear spec); the gate floor is 1, so a new character with skill 0 can wear Lv 1 gear |
| Reforge/identify | Crafted pieces are not unidentified (only chest finds are). Reforge allowed (Gear spec stage 3) |

## 3. Recipe from starter-shard materials

The starter shard has trees, bushes, a small cave with stone and copper (Lore). Fibre and sticks come from bushes (SkyyCollections: `Plant_Bush*` drop Plant Fibre and Stick),
stone rubble from rocks/gravel. Item ids below are from the SkyyCollections spec; the **rubble item id and the bench are UNVERIFIED**.

| Piece | Plant Fibre (`Ingredient_Fibre`) | Stick (`Ingredient_Stick`) | Stone Rubble | Log |
|---|---|---|---|---|
| Crude Cap | 6 | 2 | 2 | - |
| Crude Vest | 12 | 4 | 4 | 2 (any, for the frame) |
| Crude Leggings | 9 | 3 | 3 | - |
| Crude Wraps | 4 | 2 | 1 | - |
| **Whole set** | 31 | 11 | 10 | 2 |

Why this fits: the whole set is collected from things the quest chain already makes you do (bushes, a cave, trees) in about 5-10 minutes; no ore or smelting needed.
Station: the Workbench the player crafts in quest 3 (armor tab) - UNVERIFIED that the Workbench can hold armor recipes; fallback: a pocket craft in the Accessory Bag's crafting grid.
Collections hook: crafting a Crude set gives the first Smithing-like unlock (the recipe appears after "Plant Fibre I" - Collections reward, matches Collections-Spec 'Plant Fiber tier I unlocks recipes'). Auto-unlock is off by default, so unlock it explicitly with the tier.

## 4. What it looks like (for the asset work)

| Idea | Details |
|---|---|
| Look | Rough bark-brown tunic bound with fibre cord, stone studs on the shoulders; plain cap. Obviously "made without paying attention" (Pebble's joke) |
| Cheap way | Reuse a vanilla light armor model (the Wool/Leather one) with a retexture generated at build time from the vanilla texture (never commit vanilla assets - PROJECT-RULES 2) |
| Icon | Same model icon, tinted brown; name `Crude Cap` etc. |
| Sound | Same as the vanilla cloth/leather equip sounds |

## 5. Server Setup rows (sketch; config kit)

`level.item.Armor_Crude` = 1 (already the pattern for `Armor_Copper`), `band.Armor_Crude` = 1-8, `mat.factor.Armor_Crude` = 0.8 (new row),
`base.armor.<slot>` stays; recipes are asset JSON (not Server Setup).

## 6. For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Does SkyyGear's material table allow a factor below 1 (a "material penalty")? The spec describes only a bonus up to +12%. If not, set Crude's bonus to 0 and give Copper a +15% bonus instead (then Crude Lv 1 = 25 HP and Copper = 29 HP). |
| 2 | Recipe JSON: which bench/category holds armor (Workbench vs Armorsmith) and what a minimal vanilla armor recipe looks like (see Copper armor). |
| 3 | Exact item ids: rubble (`Rock_Stone_Rubble`?), the Armor_* ids, and which armor model + texture to derive. Generate at build time, never commit. |
| 4 | Whether the starter shards will have bushes (fibre/sticks). If not, add them to the island prefabs or use leaves. |
| 5 | Vanilla stat numbers I quoted come from the Gear spec (VERIFIED there from Assets.zip) and a web guide; recheck Wool/Leather HP if the balance matters. |

## 7. Questions for Skyy

1. OK for Crude to be a bit weaker than Copper (factor 0.8) so it feels like a stepping stone?
2. Crude band 1-8: do you want Crude to stay useful longer (cap 12) or retire fast?
3. Should Crude armor be craftable later by anyone, or only during the starter chain (it is the Lv 1 gear for new characters, never sold)?
