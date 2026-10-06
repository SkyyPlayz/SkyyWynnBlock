# Crop Armor (Wheat to Onion) - stats and recipes

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `docs/answered/gear.md` lines 70 and 77 (the crop-armor locks), `research/cloud/gathering-armor-art/README.md` (section 3, the 7-set crop table and look), `research/cloud/Gathering-Armor-Mining-Farming.md` (section 2, the metal Farming set this REPLACES; sections 3 to 5 stay), `research/cloud/Gathering-Numbers-Reconciled.md` (sections 1.1 to 1.5, 3), `research/cloud/Enchanted-Materials-Draft.md` (sections 1.3, 4, 5), `research/cloud/Foraging-Armor-Design.md` (section 3 recipe pattern), `research/cloud/Gathering-Tiers-Draft.md` (crop groups), `research/Collections-Spec.md` (section 2.2 crop ids, 4.1 curves). Every number is a placeholder and a Server Setup row (times in seconds). Arithmetic checked in python3.

## 0. Decisions followed (LOCKED, not re-decided)

| Lock | Source | Used here |
|---|---|---|
| "Start with wheat armor and work up through the food tiers making food armor, like in skyblock": 7 steps on the vanilla Farming Bench order (Wheat, Carrot, Cauliflower, Pumpkin, Chilli, Cotton, Onion as drawn); each set made from and looking like its crop | `docs/answered/gear.md:70`, `:77` | The 7 sets in section 1; the metal Farming set (T0 Straw Farmer ... T7 Onyxium Farmer) is retired |
| Farmer v2 look approved ("i love the looks") | `docs/answered/gear.md:77` | Look stays as the sheet; only stats and recipes here |
| ONE armor ladder for all gathering sets: Fortune 1 / 1.5 / 2.5 / 4 / 5.5 / 7.5 / 10 / 12, rarity x1 / 1.1 / 1.2 / 1.3 / 1.3 / 1.3 (Fortune and Wisdom only), 4-piece set bonus x1.15 before the cap, no 2-piece Fortune; `armor.fortune.cap` 15; Wisdom ladder 2 / 4 / 6 / 8 (cap 10); Sickle Range armor part 0 / 0 / 0 / 1 / 1 / 1 / 2 / 2 (cap 2, shared row min(4, 1 + floor(Farming / 25))); Farming has no swing | Reconciled 1.1 (F5), 1.4 (R2, R3), 1.5 (X3), edits 4.3 | Section 2 |
| Gathering armor checks the matching skill (Farming level); stats bind to the held tool (hoe / sickle); under-level pieces give nothing | `Gathering-Armor-Mining-Farming.md` sections 0, 3.3 | Section 2 notes |
| R3: coins never skip a collection unlock; NPC shops never sell unlocks; armor is never sold on the Bazaar | economy rules | Sections 4 and 5 |
| Enchanted X = 160 X, counts for collections only when OBTAINED, never when crafted; tier-up recipes use the previous tier's Enchanted; armor set = 24 Enchanted + the base parts | `Enchanted-Materials-Draft.md` sections 0, 4, 5 | Section 3 |
| Bazaar buy = base x 1.10, sell = base x 0.90 (spread 22.2%); Enchanted premium 10% | economy rules | Section 5 |
| Crops follow the vanilla Farming Bench price order 2 / 6 / 16 / 40 | `docs/answered/economy.md:79` | Section 5 |

## 1. The seven sets (levels and the old metal tiers they replace)

Bands copy the metal bands the sheet echoes (Crude 1-13 ... Mithril / Onyxium 40-49). Gate = **Farming level** at the band start.

| # | Set | Crop (item id, UNVERIFIED sets) | Band / Farming gate | Old tier it replaces | Bench pair (the crop not used) |
|---|---|---|---|---|---|
| 1 | **Wheat Armor** | `Plant_Crop_Wheat_Item` | 1-13 / 1 | T0 Straw Farmer | Lettuce |
| 2 | **Carrot Armor** | `Plant_Crop_Carrot_Item` | 10-18 / 10 | T1 Copper Farmer | Corn |
| 3 | **Cauliflower Armor** | `Plant_Crop_Cauliflower_Item` | 15-23 / 15 | T2 Iron Farmer | Turnip |
| 4 | **Pumpkin Armor** | `Plant_Crop_Pumpkin_Item` | 20-28 / 20 | T3 Thorium Farmer | Aubergine |
| 5 | **Chilli Armor** | `Plant_Crop_Chilli_Item` | 25-38 / 25 | T4 Cobalt Farmer | Tomato |
| 6 | **Cotton Armor** | `Plant_Crop_Cotton_Item` | 35-43 / 35 | T5 Adamantite Farmer | Rice |
| 7 | **Onion Armor** | `Plant_Crop_Onion_Item` | 40-49 / 40 | T6 Mithril Farmer | Potato |

The old T7 (Onyxium Farmer, 12 Fortune, 50+) has no crop set. Onion takes the old T6 numbers (Q1); a later 8th set (e.g. an "Eternal Crop" set at 50+) could take the 12 rung.

## 2. Stats (full set of 4 pieces, Normal)

Piece split Head 25% / Chest 35% / Legs 25% / last slot 15% (the Foraging set says Hands, the Mining sheet says Feet; UNVERIFIED which slot the base armor has). "Stats" below are the set total; the pieces pay their share.

| Set | Farming Fortune | Sickle Range (armor part) | Farming Wisdom (XP) | Green Thumb (auto-replant) | Defense |
|---|---|---|---|---|---|
| Wheat | +1.0 | 0 | - | - | very low |
| Carrot | +1.5 | 0 | - | - | very low |
| Cauliflower | +2.5 | 0 | - | - | low |
| Pumpkin | +4.0 | +1 | - | - | low |
| Chilli | +5.5 | +1 | +2% | - | low |
| Cotton | +7.5 | +1 | +4% | 25% | low |
| Onion | +10.0 | +2 | +6% | 50% | low |

- Real Defense / Health come from SkyyGear's armor curve (placeholder "very low / low", as for the old sets).
- Fortune pieces (Normal): Wheat 0.25 / 0.35 / 0.25 / 0.15; Carrot 0.375 / 0.525 / 0.375 / 0.225; Cauliflower 0.625 / 0.875 / 0.625 / 0.375; Pumpkin 1.0 / 1.4 / 1.0 / 0.6; Chilli 1.375 / 1.925 / 1.375 / 0.825; Cotton 1.875 / 2.625 / 1.875 / 1.125; Onion 2.5 / 3.5 / 2.5 / 1.5.
- **Caps respected (python3).** Full set with the 4-piece x1.15 and the rarity multiplier, clamped at `armor.fortune.cap` 15:

| Set | Normal | Unique | Rare | Legendary | Fabled | Mythic |
|---|---|---|---|---|---|---|
| Wheat | 1.15 | 1.26 | 1.38 | 1.49 | 1.49 | 1.49 |
| Carrot | 1.72 | 1.90 | 2.07 | 2.24 | 2.24 | 2.24 |
| Cauliflower | 2.88 | 3.16 | 3.45 | 3.74 | 3.74 | 3.74 |
| Pumpkin | 4.60 | 5.06 | 5.52 | 5.98 | 5.98 | 5.98 |
| Chilli | 6.32 | 6.96 | 7.59 | 8.22 | 8.22 | 8.22 |
| Cotton | 8.62 | 9.49 | 10.35 | 11.21 | 11.21 | 11.21 |
| Onion | 11.50 | 12.65 | 13.80 | 14.95 | 14.95 | 14.95 |

  The top Mythic set is 14.95, just under the 15 cap, so nothing is wasted and no set needs a special case (a later 12-rung set would waste 2.9, as the Reconciled file already notes). Mixed with other gathering armor the 15 cap is for all worn gathering armor together (additive with tree, tool, pets, accessories, collections, all under the global 100 `perk.doubleDropMax`).
- Wisdom with rarity (x1 .. x1.3): Chilli 2 to 2.6, Cotton 4 to 5.2, Onion 6 to 7.8, all under `armor.wisdom.cap` 10.
- Sickle Range: armor part max 2 (Onion). The total is `min(4, 1 + floor(Farming / 25))` shared with the sickle, so one swing never clears a field. No rarity multiplier on range.
- **No swing line** for Farming (hoe / sickle have none). Armor never touches the tool's power.
- Rarity, rolls and Reforge as for tools; reforge pool: Farming Fortune, Farming Wisdom, Sickle Range (small), Defense. Crop armor is crafted (Normal) and never drops unidentified.
- Under-level pieces give no Farming stats and no Defense; stats count only with a **hoe or sickle** held (armor Fortune never works bare-handed). Swap delay row `garmor.swapDelay` 0.5 s.

## 3. Set bonuses

| Bonus | Pieces | Sets | What |
|---|---|---|---|
| **Full harvest** | 4 | all 7 | Fortune x1.15 (before the 15 cap, only on the armor's own share) |
| **Field Runner** (the Mining "Tunnel Runner" idea) | 2 | Carrot to Onion | +1% move speed while a hoe or sickle is held (reuses the S9 MOVE hook; does not stack across sets) |
| **Green Thumb** | 2 | Cotton, Onion | 25% / 50% chance a harvested crop is left one growth stage younger (replants with no seed cost, never creates a seed item; never on eternal-seed crops; UNVERIFIED engine hook, as in the old section 2.3) |
| **Hearty Gourd** (optional, later) | 2 | Pumpkin | food you eat heals +5% more (needs a SkyyCooking hook, UNVERIFIED; drop if not cheap) |
| **Spice** (optional, later) | 2 | Chilli | food buffs last +5% longer (same hook, UNVERIFIED) |

Wheat has no extra perk (the starter). Perks use only hooks the Mining / Foraging sets already need; no new Fortune sources (so the cap table above is the whole truth). Green Thumb moves from the old T5+ / T6 / T7 (25 / 50 / 75%) to Cotton / Onion (25 / 50%); the 75% rung goes with the retired T7.

## 4. Recipes (crops + Enchanted crops)

Recipes follow the Foraging pattern: the set needs **its own crop**, raw early and Enchanted later, plus **a little of the previous crop's Enchanted** (the ladder rule), so no tier can be skipped by buying the lower one. Piece split of the Enchanted (Enchanted draft section 4: Head 5 / Chest 8 / Legs 7 / last slot 4 of 24) scales down: 8 = 1.7 / 2.7 / 2.3 / 1.3, 16 = 3.3 / 5.3 / 4.7 / 2.7 (round up the chest; the build sets the exact split).

| Set | Own crop, raw | Own crop, Enchanted | Previous crop, Enchanted | Base parts (UNVERIFIED ids) | Base crops (own + previous, python3) | Feel at 1,000 crops / h (row) |
|---|---|---|---|---|---|---|
| Wheat | 200 | 0 | - | Plant Fibre 30 (rope band) | 200 | 0.2 h |
| Carrot | 100 | 8 | 2 Ench. Wheat | Plant Fibre 10, Light Leather 2 | 1,380 + 320 = 1,700 | 1.7 h |
| Cauliflower | 0 | 16 | 2 Ench. Carrot | Plant Fibre 10, Light Leather 4 | 2,560 + 320 = 2,880 | 2.9 h |
| Pumpkin | 0 | 24 | 2 Ench. Cauliflower | Plant Fibre 15, Medium Leather 4 | 3,840 + 320 = 4,160 | 4.2 h |
| Chilli | 0 | 24 | 2 Ench. Pumpkin | Plant Fibre 15, Medium Leather 4, Tree Sap 5 | 4,160 | 4.2 h |
| Cotton | 0 | 24 | 2 Ench. Chilli | Linen Scrap 12, Heavy Leather 4 | 4,160 | 4.2 h |
| Onion | 0 | 24 | 2 Ench. Cotton | Shadoweave Scrap 12, Heavy Leather 4, Tree Sap 8 | 4,160 | 4.2 h |

- 24 Enchanted = 24 x 160 = 3,840 crops (python3), the same "about 4 hours" feel as the Foraging and Mining sets; hours are crops per hour only. **Growth time is the real limit** (a field has to ripen), so the real time is longer; the Farming skill's Fortune adds extra drops.
- **Enchanted forms needed:** Enchanted Wheat, Carrot, Pumpkin, Cotton, Onion exist in the Enchanted draft; **Enchanted Cauliflower and Enchanted Chilli do not** (the draft only lists "others per crop" and "Tomato / Cotton / Rice"). Add both to its group B / C lists (Q3). Chilli's group C key is Tomato in the draft; here Chilli is its own Enchanted form.
- Vanilla leather and scrap names are copied from the Mining / spellbook recipe style (UNVERIFIED ids, the build reads the Farming Bench's real ingredients; the farmer clothes should mirror what vanilla gives that crop-bench step if a vanilla farmer armor exists).
- Bench: the Farming Bench is where crop tools are made; armor goes where the other gathering armor goes (Armor Bench tab "Gathering"); UNVERIFIED, local session picks.
- Upgrade option (as Foraging Q4): tier N + 1 could also eat the same piece of tier N (default **off**). Salvage must not return Enchanted items (dupe class).
- Craft level = your Farming level clamped to the band (the Gear "crafted at your level" rule).

## 5. Collections gates, coins and loops

Recipes appear only through collections (R3): no shop sells them, coins never skip a tier, Enchanted crops bought on the Bazaar do not count as collected.

| Set | Recipe shows at (own crop collection, curve S) | Crops collected to reach it | Seed route (Gathering-Tiers) |
|---|---|---|---|
| Wheat | start (Wheat I, 50) | 50 | group A seeds: wild |
| Carrot | Carrot VI | 2,500 | group A: wild |
| Cauliflower | Cauliflower VI | 2,500 | group B seeds: Wheat IV + Carrot IV (500 each) |
| Pumpkin | Pumpkin VI | 2,500 | group B (same) |
| Chilli | Chilli VI | 2,500 | group C: Corn V + Pumpkin IV |
| Cotton | Cotton V | 1,000 | group C |
| Onion | Onion V | 1,000 | group D: Cotton IV + Rice IV |

(Thresholds from `Collections-Spec.md` 4.1: S curve 50 / 100 / 250 / 500 / 1,000 / 2,500 / 5,000 / 10,000 / 20,000; tier V = 1,000, VI = 2,500.) Cotton / Onion use tier V like Adamantite / Mithril in the Mining set. The gate rarely binds a player who farms the crop (the recipe needs 2,560 to 4,160 base crops, more than the gate), which is the point: it stops a buyer. The old placeholder cells "Farm armor T1..T4" in `Collection-Unlocks-Draft.md` (Wheat, Pumpkin, Tomato / Cotton, Potato / Onion) are replaced by this table.

**Money checks (python3):**
- Base crop value per set at the vanilla price order (2 / 6 / 16 / 40 coins per crop): Wheat 400, Carrot 2,760 own + 640 previous, Cauliflower 15,360 own, Pumpkin 23,040 own, Chilli 61,440, Cotton 61,440, Onion 153,600 coins of crops at base. The coin value of a set therefore climbs with the crop group, as the economy locks want ("cheapest early, dearer later").
- Enchanted premium 10% is below the 22.2% Bazaar spread, so buy -> craft -> sell never gains; armor is not sold on the Bazaar, so the loop has no exit; salvage returns no Enchanted items.
- No coins are created by crafting; the armor adds only Fortune (+ at most 15 total), so crop supply grows slowly and the Bazaar sell side (base x 0.90) stays the sink.

## 6. Server Setup rows (SkyWynn Menu -> Server Setup -> Gear -> Gathering armor -> Farming)

| Row | Default |
|---|---|
| `garmor.farming.enabled` | on |
| Level band + Farming gate per set (7 rows) | section 1 |
| Fortune per set (7 values) | 1 / 1.5 / 2.5 / 4 / 5.5 / 7.5 / 10 |
| Wisdom per set | 0 / 0 / 0 / 0 / 2 / 4 / 6 |
| Sickle Range per set (armor part) | 0 / 0 / 0 / 1 / 1 / 1 / 2 |
| Green Thumb chance per set | Cotton 25, Onion 50 |
| Field Runner move speed (%) | 1 |
| Set bonus Fortune multiplier (4 pieces) | 1.15 |
| Piece shares Head / Chest / Legs / last slot | 25 / 35 / 25 / 15 |
| Rarity multipliers (Fortune, Wisdom) | 1 / 1.1 / 1.2 / 1.3 / 1.3 / 1.3 |
| `armor.fortune.cap`, `armor.wisdom.cap` | 15, 10 |
| Recipe amounts per set (raw, Enchanted, previous Enchanted) | section 4 |
| Recipe unlock tier per set | start / VI / VI / VI / VI / V / V |
| Crops per hour used for the "feel" estimate (info only) | 1,000 |
| Swap delay between sets (seconds) | 0.5 |

## For the local session (UNVERIFIED)

1. Whether vanilla already has a farmer / crop armor or Farming Bench clothes to mirror (then recipes and bench copy vanilla, as for Mining / spellbooks).
2. The real armor model slots: Head / Chest / Legs and Hands or Feet (Foraging draft says Hands, the sheet draws boots), and the texture size for the straw hat brim / coat skirt.
3. Item ids: `Plant_Crop_<Crop>_Item` for all 7, the Enchanted ids (`Skyy_Ench_*` rule), and that Chilli / Cauliflower collections exist as standalone (they do in the registry, Collections-Spec 2.2).
4. Whether Farming Fortune stats can bind to "hoe / sickle held" (the held-tool check used for Mining) and the Green Thumb stage hook (place a block at a younger stage), as in the old section 2.3.
5. Whether the SkyyCooking hooks for Hearty Gourd / Spice are cheap (else drop them).
6. The real crops-per-hour and growth times, to replace the 1,000 / h feel row.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Onion (band 40-49) takes the old T6 numbers (10 Fortune), and the old T7 (12) waits for a later 50+ "Eternal" set. Or give Onion the 12? | [10; 12 for a later set] |
| 2 | Recipe size: 24 Enchanted crops (about 4 hours) per set from Pumpkin up, as for Foraging / Mining? | [yes] |
| 3 | Add Enchanted Cauliflower and Enchanted Chilli to the Enchanted list (they are not there)? | [yes] |
| 4 | Small food perks Hearty Gourd (Pumpkin) and Spice (Chilli), if SkyyCooking can do them cheaply - or leave those sets with the x1.15 only? | [try them, drop if costly] |
| 5 | Unlock tier: VI for Carrot to Chilli, V for Cotton and Onion (as the Mining set)? | [yes] |
| 6 | Also eat 2 Enchanted of the previous crop in every recipe (no skipping), or only the own crop? | [yes, 2] |
