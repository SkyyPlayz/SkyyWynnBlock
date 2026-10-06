# Gathering reconciliation - applied edits

Cloud draft, 2026-10-06. Paper design; nothing built. Records the edits made from `research/cloud/Gathering-Numbers-Reconciled.md` section 4 to the cloud drafts. Each edited file got a one-line note "Reconciled 2026-10-06, see research/cloud/Gathering-Numbers-Reconciled.md" near its top. No commits. No file outside `research/cloud/` was touched.

## 1. `research/cloud/Tool-Levels-Revision.md`

| Section | Old -> new |
|---|---|
| top | added the Reconciled note |
| 2 Swing % | "tree + tool level + armor" -> "tree + tool level + armor + pet, each source capped (tool 15 / 20, armor 12, pet 5), total capped at +40 %" |
| 3 table header | tier "60 (7)" -> "60 (8)" |
| 3 table values (Lv 60) | pick / shovel / hatchet 13.7 -> 13.9; hoe / sickle 20.5 -> 20.9 (0.2 x 60 x 1.16 = 13.92; 0.3 x 60 x 1.16 = 20.88) |
| 4 rule 3 table, armor row | kept, added "Rarity x1 / 1.1 / 1.2 / 1.3 / 1.3 / 1.3, 4-piece x1.15 before the cap, no 2-piece Fortune" |
| 4 rule 3 table, pets row | "+40 / +60 would be cut to 10" -> "Legendary Lv 100 +10 / +7" |
| 4 rule 3 table, collections row | "sums to ~19; halve it" -> "ladder 1 / 1 / 1.5 / 2 / 2 / 2.5 = 10, same for Farming" |
| 4 rule 3 table, new rows | armor swing 12, pets swing 5, accessories swing 0, tool Wisdom 15, armor Wisdom 10 |
| 4 last paragraph | "On-level player ... 16 / 44 / 75 / 98 / 100" -> the typical vs maxed numbers of the reconciliation section 2 (clamp hit at skill 32-41 for maxed) |
| 9 Cap | "<= `tool.range.cap` 4" -> "<= min(4, 1 + floor(Farming / 25)); tool part max 3, armor part max 2" |
| 11 rows | added `armor.swing.cap` 12 / `pets.swing.cap` 5, `tool.wisdom.cap` 15 / `armor.wisdom.cap` 10, `tool.range.capPerFarming` 25 |
| Questions Q1 / Q2 | text unchanged, defaults unchanged, added pointers to the reconciliation Q1 / Q7 |

Left as is: the `tool.range.cap` 4 default in the section 11 row `tool.range.on / stats.srng / tool.range.cap` (still the absolute top of the new formula). The reconciliation edit list only names section 9; Skyy / local session may want to rename that row to the new formula.

## 2. `research/cloud/Foraging-Armor-Design.md`

| Section | Old -> new |
|---|---|
| top | added the Reconciled note |
| 4 intro | "100 = one guaranteed extra log ... full Goldenwood = 40" -> "1 point = +1% double drop; armor cap 15; full Goldenwood = 12 (x1.15 set bonus, x rarity)" |
| 4 table Fortune (Wood ... Goldenwood) | 4 / 8 / 12 / 16 / 22 / 28 / 34 / 40 -> 1 / 1.5 / 2.5 / 4 / 5.5 / 7.5 / 10 / 12 |
| 4 table chopping speed | +2 / 4 / 6 / 9 / 12 / 16 / 20 / 25% -> +1 / 2 / 3 / 4 / 6 / 8 / 10 / 12% (no rarity multiplier) |
| 4 "Rarities" bullet | added "reforge / drops may raise it; Fortune x1 / 1.1 / 1.2 / 1.3 / 1.3 / 1.3" (and no multiplier on chopping speed) |
| 5 set-bonus table | 2-piece row "+25% of the set's Fortune" removed; 4-piece row now "Fortune x1.15 (before the cap), Tree Feller level, Sap Sense" |
| 5 text under the table | "Wood and Softwood have only the 2-piece bonus" -> "have no set bonus (no 2-piece Fortune any more)" (follows from removing the 2-piece row) |
| 6 last sentence | "This matches the collection draft: Feller I appears at Birch ..." deleted |
| 8 rows | "2-piece Fortune bonus % 25" -> "4-piece Fortune multiplier 1.15"; added `armor.fortune.cap` 15 / `armor.swing.cap` 12 |
| 9 first row | "half rate (setting)" -> "`bonusBlock.fortuneRate` 50%" |
| 9 last row | `foraging.fortune.cap` 200 -> per-source caps + global `perk.doubleDropMax` 1.0 |
| Q3 default | "full Goldenwood = 40" -> "1 point = +1% double drop, full Goldenwood = 12" |
| Q8 default | "yes, 4" -> "yes, 1" |

Left as is: the section 9 risk text "10 extra x Fortune 40 x Foraging Bag" (an example of the exploit, now an old number; harmless, not on the edit list).

## 3. `research/cloud/Gathering-Armor-Mining-Farming.md`

| Section | Old -> new |
|---|---|
| top | added the Reconciled note |
| 1.2 rarity text | x1.0 / 1.1 / 1.2 / 1.35 / 1.5 / 1.7 -> x1.0 / 1.1 / 1.2 / 1.3 / 1.3 / 1.3, Fortune and Wisdom only (not swing, not range) |
| 1.2 Mining Speed bullet | added "armor swing cap 12 (`armor.swing.cap`), no rarity multiplier" |
| 1.3 set bonus row | "x1.15 when held tool = pickaxe or shovel" -> "... applied before the 15 cap; same rule in all three sets" |
| 2.2 Sickle Range column (T0-T7) | - / +0 / +1 / +1 / +2 / +2 / +3 / +3 -> - / 0 / 0 / +1 / +1 / +1 / +2 / +2 (T0 stays "-"; the "3x3 -> row of 3" note moved to T3, the first +1) |
| 2.2 cap bullet | "+4 blocks (row `farm.armor.rangeCap`)" -> "ONE row shared with the tool: min(4, 1 + floor(Farming / 25)), tool part max 3, armor part max 2" |
| 3.1 table | Tool column "18.5" -> "25" (tool cap); Armor T7 "20.4" -> "15"; Mining 83.9 / 108.9 -> 85 / 110 (cap 100); Farming 103.4 -> 110 (cap 100). Column headers renamed to match |
| 3.1 sums paragraph | rewritten to the new sums; T7 Mythic = min(15, 12 x 1.3 x 1.15 = 17.9) = 15; recommendation "lower Mythic armor mult to x1.3" marked adopted |
| 3.2 | "tree 20% ... total 35.6%" -> "tree up to 40% (1.6% x 25), armor 12 (no multiplier): the sum reaches the +40% ceiling" |
| 5 rows | `farm.armor.rangeCap` 4 deleted (merged into the tool row); rarity row kept; added `armor.swing.cap` 12 |
| Q6 | default 15% kept; text now notes "confirmed 2026-10-06 in the reconciliation 1.1 F5; still Skyy's call" |

## 4. `research/cloud/Pets-Spec.md`

| Section | Old -> new |
|---|---|
| top | added the Reconciled note |
| 1 rules table | added rows `pets.fortune.cap` 10, `pets.swing.cap` 5, "no Mythic gathering pet" |
| 5.1 Rabbit | "+60 Farming Fortune; +5% crop double-drop; fast crops" -> "+10 Farming Fortune; fast crops" |
| 5.1 Chicken | +40 -> +7 Farming Fortune |
| 5.1 Goat | "+60 Mining Fortune; +10% Mining Speed" -> "+10 Mining Fortune; +5 swing" |
| 5.1 Warthog | +40 -> +7 Mining Fortune |
| 5.1 Bear | "+60 Foraging Fortune; trees fall faster" -> "+10 Foraging Fortune; +5 swing (UNVERIFIED how)" |
| 5.1 Turkey | +40 -> +7 Foraging Fortune |
| 7 rows sketch | added `pets.fortune.cap` (10), `pets.swing.cap` (5) |

## 5. `research/cloud/Collection-Unlocks-Draft.md`

| Section | Old -> new |
|---|---|
| top | added the Reconciled note |
| 4 text | "+2 / +2 / +3 / +3 / +4 / +5 ... about +20 per skill" -> "+1 / +1 / +1.5 / +2 / +2 / +2.5 = 10 per skill, same for all three"; budget line "tools 40%, armor 30% ..." replaced by the per-source caps (tool 25, armor 15, accessories 10, pets 10, collections 10) |
| 3 Mining IX cells (Copper / Iron / Thorium / Cobalt / Adamantite / Mithril) | +2 / +2 / +3 / +3 / +4 / +5 -> +1 / +1 / +1.5 / +2 / +2 / +2.5 |
| 3 Foraging IX cells (Oak / Birch / Maple / Redwood / Azure / F5) | +2 / +2 / +3 / +3 / +4 / +5 -> +1 / +1 / +1.5 / +2 / +2 / +2.5 |
| 3 Farming IX cells (Wheat / Carrot / Corn / Pumpkin / Tomato-Cotton-Rice / Potato-Onion) | +2 / +2 / +2 / +3 / +3 / +4 -> +1 / +1 / +1.5 / +2 / +2 / +2.5 |
| 3 Birch VII | "Tree Feller I (axe / armor upgrade)" -> "free slot (e.g. a Foraging XP lump or a Foraging Bag step; Skyy picks)" |
| 3 Maple VII | "Tree Feller II" -> same free-slot text |
| 3 "Tree Feller:" note under the Foraging table | "tiers VII and later unlock Tree Feller levels on axes and armor" deleted |
| 3 Cobblestone VII / VIII | "Haste accessory I (Miner's Charm)" / "Haste accessory II" -> "Prospector accessory recipe (Rare, Fortune +3)" / "(Legendary, Fortune +6)" |
| 0 grammar row VII, 6 table row "Accessories" | "haste / lantern accessories" / "Accessories (Haste, Lantern)" -> "Prospector" in place of Haste (consistency edit, not on the list) |

## 6. `research/cloud/Accessory-Acquisition.md`

| Section | Old -> new |
|---|---|
| wave 2 row (the table after "Lantern"; line 40 in the original) | added a line under the table: "Normal / Unique Prospector / Woodsman / Harvester give Wisdom only, Fortune starts at Rare (+3, Legendary +6)" plus the Reconciled note. Put under the table, not inside the row, to keep the table columns intact |

## 7. Could not apply

- Nothing from the lists for the six cloud files was skipped.
- The reconciliation says "section 14 Q1 / Q2" for `Tool-Levels-Revision.md`; that file has 9 questions in an unnumbered "Questions for Skyy" section (its section 13 is the build stages). I added the pointers to Q1 and Q2 there.
- The Mythic armor rarity cap worry (reconciliation flag 4) and the hoe / sickle `tool.fortune.perLevel` 0.25 suggestion (flag 5, reconciliation Q8) are NOT applied anywhere: the list marks them as numbers for Skyy.

## 8. Needs a PR (outside research/cloud/)

| File | Section | Old -> new |
|---|---|---|
| `research/Booster-Accessories-Spec.md` | 3 wave 2 bullet | "Before building, check the Fortune numbers against the skills' own double-drop perk" -> "Checked 2026-10-06: Rare +3 / Legendary +6 stays; accessory Fortune cap 10 (`accessories.fortune.cap`); no swing line (see `research/cloud/Gathering-Numbers-Reconciled.md`)" |

## 9. Questions for Skyy

None new. Defaults that moved because of the reconciliation (text of the questions unchanged, Skyy still decides):

| Where | Question | New default |
|---|---|---|
| `Foraging-Armor-Design.md` Q3 | Foraging Fortune scale | points, 1 point = +1% double drop, full Goldenwood = 12 (was 40) |
| `Foraging-Armor-Design.md` Q8 | Wood armor Fortune | yes, 1 (was 4) |
| `Tool-Levels-Revision.md` Q1 / Q2, `Gathering-Armor-Mining-Farming.md` Q6 | Fortune cap, one armor ladder, armor cap 15 | unchanged; now cross-linked to the reconciliation Q1 / Q7 |
| `Collection-Unlocks-Draft.md` Q3 | collection Fortune perks | unchanged default; ladder is now 10 per skill (reconciliation Q4) |
