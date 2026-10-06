# Gathering armor - Mining and Farming sets (draft)

Cloud draft, 2026-10-06. Paper design; nothing built.
Inputs read: `docs/answered/gear.md` (LOCKED 2026-10-05 Foraging armor set + "Mining / Farming later"; armor types; tool levels), `research/cloud/Gathering-Tiers-Draft.md`, `Collection-Unlocks-Draft.md`, `Enchanted-Materials-Draft.md`, `research/Tool-Levels-Spec.md` (Fortune curve 4.1, double-drop totals 4.3), `research/Skill-Trees-Spec.md` (Vein Burst S12, Tree Feller, Rich Veins), `research/Swing-Speed-Spec.md` (+40% swing cap), `research/Booster-Accessories-Spec.md`.
`research/cloud/Foraging-Armor-Design.md` did not exist yet when this was written; naming below copies the locked Foraging wording (tier 1 vanilla-style start, then 7 tiers echoing Copper..Onyxium). Align when it lands.
Every number is a placeholder and a Server Setup row (times in seconds). Anything that needs game files is **UNVERIFIED**.
Reconciled 2026-10-06, see research/cloud/Gathering-Numbers-Reconciled.md (sections 1.2, 1.3, 2.2, 3.1, 3.2, 5 and question 6 changed).

## 0. The rule for all three gathering sets

- A set = 4 pieces (Head, Chest, Legs, Feet). Low Defense, no class bonus; any class can wear it. It is a **gathering** set, so it checks the matching skill (Mining / Farming level), like gathering tools (LOCKED 2026-10-02). Under-level pieces give no gathering stats.
- **8 tiers per set**: tier 0 = the starter (like Foraging's vanilla Wood armor), tiers 1-7 echo Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium (the 7-tier spine). Level bands are the live metal bands (Copper armor 1-18 stays as locked).
- Each tier is an **upgrade of the previous piece** (Skyy's Light-armor idea: keep the look, add the new material), so a set costs the lower tier's piece plus the new tier's material. R3 holds: recipes appear only through collections (VI row of Collection-Unlocks), no shop sells them.
- Rarity, rolls and Reforge work like tools (Normal..Mythic); the reforge pool is the skill's own (below). Gathering armor never drops unidentified.
- The three sets share one stat language: **Fortune** (extra drops), **Speed**, **Wisdom** (XP), plus one **signature perk**.

## 1. MINING set - "Miner's gear"

### 1.1 Tiers (levels, materials, recipes)
Material bulk = the key ore's Enchanted form (Enchanted-Materials 1.1); stone bulk = S1 / S2 / S3 groups (Gathering-Tiers 1.3). Ore per piece: Head 5, Chest 8, Legs 7, Feet 4 bars (placeholder: 24 per set).

| T | Set name | Level band | Look (vanilla feel) | Recipe core | Unlocked by (collection) |
|---|---|---|---|---|---|
| 0 | Miner's Leather | 1-13 | plain dark leather, stone-grey strap, no metal | Leather + 20 Cobblestone per set | start |
| 1 | Copper Miner | 5-18 | leather + copper rivets, copper lamp-helmet | T0 piece + Copper bars | Copper VI |
| 2 | Iron Miner | 15-23 | iron cap with a small lamp, iron shoulder plates | T1 piece + Iron bars + Enchanted Cobblestone | Iron VI |
| 3 | Thorium Miner | 20-28 | thorium helmet, bright lamp, sandstone-coloured wraps | T2 piece + Thorium bars | Thorium VI |
| 4 | Cobalt Miner | 25-38 | blue-steel helm, lens visor, shale-grey cloak | T3 piece + Cobalt bars + Enchanted Slate | Cobalt VI |
| 5 | Adamantite Miner | 35-43 | heavy green-tinted plates over leather, strong lamp | T4 piece + Adamantite bars | Adamantite V (E curve) |
| 6 | Mithril Miner | 40-49 | pale mithril crest, glowing lamp lens | T5 piece + Mithril bars + Enchanted Mithril | Mithril V |
| 7 | Onyxium Miner | 40-49 (50+ later) | black onyx plates, violet lamp glow | T6 piece + Onyxium bars | later (hidden collection) |

The metal shapes echo the vanilla Copper..Onyxium armor but keep a leather body, like the SkyyArmory wands (wood handle + metal tip). Chest is a leather vest with ore pouches; the lamp sits on the helmet (cosmetic glow only, no light mechanic unless Skyy wants one - question 4).

### 1.2 Stats (full set, Normal rarity)
Pieces share the set total: Head 25%, Chest 35%, Legs 25%, Feet 15%.

| T | Mining Fortune | Mining Speed (swing) | Mining XP | Defense |
|---|---|---|---|---|
| 0 | +1.0% | +1% | - | very low |
| 1 | +1.5% | +2% | - | very low |
| 2 | +2.5% | +3% | - | low |
| 3 | +4.0% | +4% | - | low |
| 4 | +5.5% | +6% | +2% | low |
| 5 | +7.5% | +8% | +4% | low |
| 6 | +10% | +10% | +6% | low |
| 7 | +12% | +12% | +8% | low |
(T1-T6 Fortune follows the 1.0 / 1.5 / 2.5 / 4 / 5.5 / 7.5 / 10 ladder with T0 = 1.0 and T7 = 12; real Defense / Health come from SkyyGear's armor curve.) Rarity multiplies Fortune and Wisdom only (not swing, not range): Normal x1.0, Unique x1.1, Rare x1.2, Legendary x1.3, Fabled x1.3, Mythic x1.3 (placeholder).
- **Mining Speed** is the swing-speed layer (shares the 40% swing cap with the Mining tree and tools; armor swing cap 12 (`armor.swing.cap`), no rarity multiplier), not Mining Power.
- Reforge pool: Mining Fortune, Mining Wisdom, Mining Speed, Defense (small).

### 1.3 Signature perks
| Perk | Tier | What | Reuse |
|---|---|---|---|
| **Vein Burst** (set bonus 2 / 4 pieces) | T5+ (Adamantite) | Full set breaks up to **N** touching ore blocks of the same id (N = 4 at T5, 6 at T6, 8 at T7). Cooldown 40 s | reuses the SkyyTrees Vein Burst (S12 "BREAK" hook, never chains); armor only grants levels of it, the tree can still add its own (the higher wins, they do not add) |
| **Rich Seam** | T3+ | 2 pieces: +2% chance a paid ore drops once more (the Rich Veins EXTRA hook) | reuse S6 |
| **Tunnel Runner** | T1+ | 2 pieces: +1% move speed while holding a pickaxe (Skyy's S9 idea) | reuse S9 MOVE |
| **Set bonus** | all | 4 pieces: the tier's Fortune is multiplied x1.15 (applied before the 15 cap; same rule in all three sets) when held tool = pickaxe or shovel | - |

## 2. FARMING set - "Farmer's clothes"

### 2.1 Tiers
Crop groups A-D + eternal seeds I-III (Gathering-Tiers 3.2); cloth from Cotton / Fibre. The look is farm clothing, not plate: straw hat, linen shirt, apron, boots, with small metal buckles in each tier's colour.

| T | Set name | Level band | Look | Recipe core | Unlocked by |
|---|---|---|---|---|---|
| 0 | Straw Farmer | 1-13 | straw hat, fibre shirt, rope belt | Plant Fiber + Wheat | start |
| 1 | Copper Farmer | 5-18 | + copper buckles, linen apron | T0 + Copper bars + Enchanted Wheat | Wheat VI |
| 2 | Iron Farmer | 15-23 | iron-bound boots, wide hat | T1 + Iron bars + Enchanted Carrot | Carrot VI |
| 3 | Thorium Farmer | 20-28 | cotton shirt, thorium clasps, scarf | T2 + Thorium bars + Enchanted Corn | Corn VI |
| 4 | Cobalt Farmer | 25-38 | blue-dyed cotton, cobalt trim | T3 + Cobalt bars + Enchanted Pumpkin | Pumpkin VI |
| 5 | Adamantite Farmer | 35-43 | silk-lined coat, green adamantite fasteners | T4 + Adamantite bars + Enchanted Tomato | Tomato V |
| 6 | Mithril Farmer | 40-49 | pale silk, mithril thread, flower crown | T5 + Mithril bars + Enchanted Cotton | Cotton V |
| 7 | Onyxium Farmer | 40-49 (50+ later) | black-and-gold harvest regalia | T6 + Onyxium bars + Enchanted Eternal Crop | later |

### 2.2 Stats (full set, Normal)
| T | Farming Fortune | Sickle Range | Farming XP | Crop-growth help |
|---|---|---|---|---|
| 0 | +1.0% | - | - | - |
| 1 | +1.5% | 0 | - | - |
| 2 | +2.5% | 0 | - | - |
| 3 | +4.0% | +1 block (3x3 -> row of 3) | - | - |
| 4 | +5.5% | +1 | +2% | - |
| 5 | +7.5% | +1 | +4% | auto-replant chance 25% |
| 6 | +10% | +2 | +6% | 50% |
| 7 | +12% | +2 | +8% | 75% |
- **Sickle Range** is the same modifier as the tool's (Tool-Levels-Spec SICKLE RANGE); armor adds to it, total capped by ONE row shared with the tool: **min(4, 1 + floor(Farming / 25))** blocks (tool part max 3, armor part max 2) so one swing cannot clear a field.
- Farming Wisdom is the XP column. Reforge pool: Farming Fortune, Farming Wisdom, Sickle Range (small), Defense.
- Fortune stays Fortune-only for hoes and sickles (LOCKED); armor Fortune works with any held tool except bare hands (rule 3.3).

### 2.3 Signature perk: **Green Thumb** (auto-replant)
- T5+ (2 pieces): when a crop is harvested by hoe / sickle, a chance (table above) to leave the crop one growth stage younger instead of fully removed, i.e. it replants itself with no seed cost. Never gives an extra seed item.
- Tied to the Skill-Trees note that auto-replant is **later** and UNVERIFIED (placing a block + stage in one flow); vanilla crops already regrow after F-harvest, so the perk may reduce to "harvest does not reset the stage" once the engine call is checked.
- Never works on eternal-seed crops (they already regrow) or in a crop farm bought with coins (R3).

## 3. Stacking and caps

### 3.1 Fortune against the double-drop cap (`perk.doubleDropMax` 1.0)
Tool-Levels-Spec 4.3 totals: Mining 63.5% at skill 50 / 88.5% at 100; Foraging and Farming already hit 100% at skill 84-85. Armor is an extra source of the same `dd.<skill>` bonus map (source `gear.armor`).

| Skill | Skill perk (50 / 100) | Tree max | Tool (cap `tool.fortune.cap`) | Armor T7 (Mythic, capped) | Total at skill 50 | at skill 100 |
|---|---|---|---|---|---|---|
| Mining | 25 / 50 | 20 | 25 | 15 | 85 | 110 -> **cap 100** |
| Farming | 25 / 50 | 45 | 25 | 15 | 110 -> **cap 100** | cap 100 |

(Sums: Mining at 50: 25+20+25+15 = 85, before pets, accessories and collections; at 100: 50+20+25+15 = 110 -> cap 100; Farming at 50: 25+45+25+15 = 110 -> cap 100.) Armor still pushes top players to the 100% cap early, so keep two caps: **`armor.fortune.cap` 15 total from all worn gathering armor** and the global 100. T7 Mythic = min(15, 12 x 1.3 x 1.15 = 17.9) = 15; only the best Mythic Onyxium set wastes 2.9. Mythic armor multiplier lowered to x1.3 (adopted, was a recommendation).
- Armor Fortune is **additive** with the tree and tool (no multiplication), except the 4-piece set bonus x1.15 on the armor's own share.
- The multiplicative total never exceeds the cap; excess is simply not rolled (no refund, no extra coins).

### 3.2 Speed
Mining Speed (armor) adds to the Mining tree's swing speed and the pickaxe's roll; all three share the +40% swing cap (Swing-Speed-Spec 3.4). Armor swing cap 12 (no rarity multiplier, T7 = 12); the Mining tree gives up to 40% (1.6% x 25), so tree + armor reaches the +40% ceiling by itself. No tool-power change: armor never touches Mining Power.

### 3.3 Mixing sets
- Wearing one set (Mining) and one other-skill set at once is allowed (hat from one, chest from another): each piece pays 1/4 of its own set's total, and its stats only count while **the matching tool is held** (pickaxe -> Mining, hatchet -> Foraging, hoe / sickle -> Farming). No stat leaks between skills.
- A set bonus needs 2 or 4 pieces of the **same** set (any tier counts as the lowest tier worn).

## 4. Exploits and counters
| Exploit | Counter |
|---|---|
| Swap armor sets mid-gather for instant XP / Fortune | stats bind to the held tool (3.3); switching has a 0.5 s swap delay row |
| Vein Burst + Mining Spread chain through a whole vein | never chains (existing rule); armor and tree perks do not stack, the higher level wins |
| Crafting armor chain loops (Enchanted -> Bazaar -> armor) | premium 10% < spread 22.2%; armor pieces are not sold on the Bazaar (R3: unlocks / accessories never sold) |
| Skipping tiers with a Mythic low tier | rarity multiplier max 1.3; T7 Normal beats T0 Mythic at every level |
| Farming auto-replant giving infinite seeds | no seed item is ever created; capped 75% |
| Player-placed ore / crops for XP | existing rule: placed blocks never count for gathering XP or collections; armor adds no new path |
| Under-level wear (low-level player in high set) | pieces above your level give no gathering stats, and Defense also off (like weapons) |

## 5. Server Setup rows (new, under Gear -> Gathering armor)
| Row | Default |
|---|---|
| `garmor.enabled` (mining / farming each) | on |
| Per-tier Fortune, Speed, XP, Range tables (editable, 8 values each) | sections 1.2 and 2.2 |
| Set pieces share (Head / Chest / Legs / Feet) | 25 / 35 / 25 / 15 |
| Rarity multipliers | 1 / 1.1 / 1.2 / 1.3 / 1.3 / 1.3 (recommended) |
| `armor.fortune.cap` (all gathering armor) | 15% |
| `armor.swing.cap` | 12 |
| Vein Burst: blocks per tier, cooldown (40 s) | 4 / 6 / 8, 40 |
| Green Thumb chance per tier | 25 / 50 / 75 % |
| Swap delay between sets (seconds) | 0.5 |
| Recipe unlock tier per set (collection tier) | VI / V |
| Under-level rule on / off | on |

## 6. Look notes (art, build time only)
Mining: dark leather body (black-leather look Skyy picked for Light armor) + each metal as small plates; lamp helmets brighten each tier. Farming: cloth look, straw to silk, buckles in metal colour; Wood / Fibre starts; textures generated at build time on vanilla armor models (no vanilla assets committed); Foraging keeps its bark-and-vine look so three sets read as different at a glance (grey-metal, golden-green, brown-wood).

## For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Whether vanilla has a leather / light armor at tier 0 usable as Miner's Leather and straw / fibre cloth models for Farmer (names, slots, Defense); else new art. |
| 2 | Armor slots and the item-type ids the stats can bind to (Armor_* naming) and whether an equipped-piece event exists for "only while the matching tool is held". |
| 3 | The Vein Burst BREAK hook (`BlockHarvestUtils.performBlockBreak`) can take a level from armor as well as the tree (the Skill-Trees-Spec says the hook is verified; armor source not). |
| 4 | Auto-replant: can a harvest leave the crop at an earlier stage (placement + stage flow). |
| 5 | Sickle Range: how a swing can harvest an area (Tool-Levels-Spec 2.3 says a swing harvest fires no event; the range modifier may not be possible yet). |
| 6 | Whether `skill:bonus:<uuid>` accepts another source `gear.armor` for `dd.mining`, `dd.farming`, `xp.*`. |
| 7 | Lamp as a real light source (cosmetic glow vs a held light). |
| 8 | Whether Leather Light armor is used by the Light armor type and conflicts with the Miner's Leather ids. |

## Questions for Skyy
| # | Question | Default |
|---|---|---|
| 1 | Ship Mining and Farming armor together, or one at a time after Foraging? | one at a time: Foraging, Mining, Farming |
| 2 | 8 tiers (starter + 7 metals) each, or only 7 with Crude as T1? | 8 |
| 3 | Is the Mining set a leather-body miner kit with metal plates, or a full metal set? | leather body + metal plates |
| 4 | Should the helmet lamp give real light (night / caves), not just a glow? | glow only |
| 5 | Name the armor stat "Mining Speed" (swing) or "Mining Power" (fewer hits)? | Mining Speed (swing), per the Power / Speed split |
| 6 | Is a total armor Fortune cap of 15% right, or let top sets reach more because the economy cap (100%) already limits? (confirmed 2026-10-06 in `research/cloud/Gathering-Numbers-Reconciled.md` 1.1 F5; still Skyy's call) | 15% |
| 7 | Is Vein Burst on armor OK (reuses the tree perk), or armor only boosts it? | armor gives the perk at T5+, higher level wins |
| 8 | Is auto-replant (Green Thumb) wanted at all, since crops regrow in vanilla? | yes, T5+, if the engine allows |
| 9 | May Mining / Farming sets also have a rare Onyxium variant at Lv 50+ now, or wait for Cindersteel+? | wait |
