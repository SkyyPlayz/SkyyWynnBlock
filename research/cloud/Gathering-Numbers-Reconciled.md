# Gathering numbers - reconciled (Fortune, speed, Tree Feller, Sickle Range, gathering XP)

Cloud draft, 2026-10-06. Paper design; nothing built. One master table so the cloud drafts stop disagreeing. It changes NO file by itself: section 4 lists the exact edits for the local session / the draft owners.
Inputs read: `/home/user/SkyyWynnBlock/research/cloud/Tool-Levels-Revision.md` (the base), `/home/user/SkyyWynnBlock/research/cloud/Foraging-Armor-Design.md`, `/home/user/SkyyWynnBlock/research/cloud/Gathering-Armor-Mining-Farming.md`, `/home/user/SkyyWynnBlock/research/cloud/Pets-Spec.md`, `/home/user/SkyyWynnBlock/research/cloud/Collection-Unlocks-Draft.md`, `/home/user/SkyyWynnBlock/research/cloud/Accessory-Acquisition.md`, `/home/user/SkyyWynnBlock/research/Booster-Accessories-Spec.md` (section 3 wave 2), `/home/user/SkyyWynnBlock/research/Tool-Levels-Spec.md` (4.1-4.3), `/home/user/SkyyWynnBlock/research/Skill-Trees-Spec.md` (6.x node rows, 3.3 tokens), `/home/user/SkyyWynnBlock/research/Swing-Speed-Spec.md`, `/home/user/SkyyWynnBlock/docs/answered/skills.md`, `/home/user/SkyyWynnBlock/docs/answered/gear.md`, `/home/user/SkyyWynnBlock/SkyyTrees/build_skyytrees_0.3.py` (Feller rows).
Every number is a placeholder and a Server Setup row (times in seconds). All arithmetic and the progression tables are python-checked (`prog.py` + `extra.py`, scratch only).

## 0. The decisions this follows (not re-decided)

| Source | Skyy's words (short) | What it fixes here |
|---|---|---|
| `/home/user/SkyyWynnBlock/docs/answered/skills.md` (live perk, `perk.<skill>.doubleDropPerLevel` 0.005, `perk.doubleDropMax` 1.0) | "0.5% per level, 50% at level 100" | unit = 1 point = +1% double drop; global cap 100 stays |
| `/home/user/SkyyWynnBlock/docs/answered/skills.md` LOCKED 2026-09-25 swing speed | "Mining Speed max is +40% faster pickaxe swings"; Chopping Speed swing stays +25%; Heavy Hatchet is wood **power**, not swing; hatchet swing never touches combat | the +40% swing ceiling; swing and power are separate lines |
| `/home/user/SkyyWynnBlock/docs/answered/skills.md` LOCKED 2026-09-25 Tree Feller | "1 / 2 / 4 / 5 / 6 / 10 at levels 1-6 ... Cooldown 3 s" | the only Feller table |
| `/home/user/SkyyWynnBlock/docs/answered/gear.md` LOCKED 2026-10-02 tool levels + 2026-10-03 + 2026-10-05 | level raises speed AND Fortune; "hoes / sickles get Fortune only"; "+treefeller on the higher tiers. axes should also get tree feller"; "boost the range of the sickle" | tool lines, axe Feller, Sickle Range |
| `/home/user/SkyyWynnBlock/research/Booster-Accessories-Spec.md` section 1 rule 3 | "Only your best accessory of a line counts. Copies never stack." | one Prospector / Woodsman / Harvester counts |
| R3 / Bazaar spread 22.2% | coins never skip a collection unlock | no shop route to any source below |

Base = `/home/user/SkyyWynnBlock/research/cloud/Tool-Levels-Revision.md` section 4 (one rule, per-source caps). This file only fills the gaps it left (pets, collections, swing for armor / pets / accessories, Feller + range timing) and lists what each other draft must change.

## 1. Master table (reconciled)

Fortune unit everywhere = points; 1 point = +1% double drop; the sum is clamped at `perk.doubleDropMax` 1.0 (= 100). Sources ADD, never multiply.

### 1.1 Fortune

| # | Source | Number in the drafts | Reconciled | Cap (row) |
|---|---|---|---|---|
| F1 | Skill level perk (SkyySkills, LIVE) | 0.5 per level | unchanged, 50 at skill 100 | 50 |
| F2 | Skill tree (SkyyTrees, LIVE) | Mining 20; Foraging 20+20; Farming 25+20 | unchanged | 20 / 40 / 45 |
| F3 | Tool level | old 0.1 x L (`Tool-Levels-Spec` 4.1); revision 0.2 (pick, shovel, hatchet) / 0.3 (hoe, sickle) x L x (1 + 2% x tier) | revision (Lv 100 = 24.4 / 36.6) | tool total 25 (`tool.fortune.cap`) |
| F4 | Tool roll (`mfort` `ffort` `afort`) | max 10 at 100%; old spec Mythic 13; spare-slot boost +10% per empty slot, max +30% | revision; theoretical Mythic max 10 x 1.3 x 1.3 = 16.9 | counts inside the 25 above |
| F5 | Worn gathering armor, all three sets | Foraging 4 / 8 / 12 / 16 / 22 / 28 / 34 / 40 (Wood to Goldenwood) + 2-piece +25%; Mining + Farming 1 / 1.5 / 2.5 / 4 / 5.5 / 7.5 / 10 / 12, rarity x1.0 ... x1.7 (section 1.2) / x1.3 (section 3.1 recommendation), 4-piece x1.15; revision cap 15 | ONE ladder 1 / 1.5 / 2.5 / 4 / 5.5 / 7.5 / 10 / 12 (T0-T7) for all three sets; rarity x1 / 1.1 / 1.2 / 1.3 / 1.3 / 1.3; 4-piece x1.15 (before the cap); no 2-piece Fortune | 15 (`armor.fortune.cap`) |
| F6 | Accessories Prospector / Woodsman / Harvester (wave 2) | Normal 0, Unique 0, Rare +3, Legendary +6; best of the line only | unchanged | 10 (`accessories.fortune.cap`; max real = 6) |
| F7 | Pets (one active slot) | Rabbit +60 and +5% crop double-drop, Goat +60, Bear +60; Chicken, Warthog, Turkey +40 (Legendary Lv 100) | "60" pets = +10, "40" pets = +7 at Legendary Lv 100; stat = value x rarity factor x L / 100 (as `Pets-Spec` section 2); Rabbit's extra +5% line is deleted (it IS Fortune) | 10 (`pets.fortune.cap`) |
| F8 | Maxed key collections (IX / top tier, per skill) | +2 / +2 / +3 / +3 / +4 / +5 = 19 (Mining, Foraging); Farming 2 / 2 / 2 / 3 / 3 / 4 = 16; revision "halve it" | 1 / 1 / 1.5 / 2 / 2 / 2.5 = 10 for all three skills | 10 (`coll.fortune.cap`) |
| F9 | Bonus blocks (Feller logs, Sickle Range crops) | revision 50%; armor draft "half rate" | 50% (`bonusBlock.fortuneRate`), never chain | - |
| F10 | `foraging.fortune.cap` | 200 (`Foraging-Armor-Design` section 9) | deleted; replaced by F1-F8 caps + the global 100 | - |

### 1.2 Gathering speed (swing) and power

Total swing = tree + tool + armor + pet, clamped at **+40%** (engine ceiling, `Swing-Speed-Spec`). Power (fewer hits per block) is NOT under the ceiling.

| # | Source | Number in the drafts | Reconciled | Cap (row) |
|---|---|---|---|---|
| S1 | Tree swing | Mining Speed 1.6% x 25 = 40; Chopping Speed 25; Farming none | unchanged (LIVE) | 40 / 25 / 0 |
| S2 | Tool level swing | pick + shovel 0.3 x L, max 15; hatchet 0.5 x L, max 20; hoe, sickle 0 | unchanged | 15 / 20 / 0 |
| S3 | Armor swing | Mining 1 / 2 / 3 / 4 / 6 / 8 / 10 / 12 (Mythic x1.3 = 15.6); Foraging 2 / 4 / 6 / 9 / 12 / 16 / 20 / 25; Farming none | ONE ladder 1 / 2 / 3 / 4 / 6 / 8 / 10 / 12 for Mining + Foraging armor; NO rarity multiplier on swing | 12 (`armor.swing.cap`) |
| S4 | Pets | Goat +10% Mining Speed; Bear "trees fall faster" | Goat +5, Bear +5 swing at Legendary Lv 100 (Bear UNVERIFIED how) | 5 (`pets.swing.cap`) |
| S5 | Accessories | Booster spec: no mechanism ("Mining Speed and Chopping Speed lines" LATER); Collections draft "Haste accessory I / II" (Cobblestone VII / VIII), no number | 0 until Skyy picks a number (Q3) | 0 |
| S6 | Power: tool `mpow` / `cpow` | roll max 30%; level ladder `Tool-Levels-Spec` 3.2; hatchet strength 50% | unchanged | per roll cap 30 |
| S7 | Power: armor | "armor never touches Mining Power" | unchanged | 0 |
| S8 | Heavy Pick / Heavy Hatchet (tree) | +40% ore / +100% wood power | unchanged (power, not swing) | - |

### 1.3 Tree Feller (effective level = MAX, never a sum; logs 1 / 2 / 4 / 5 / 6 / 10, 3 s, max 6 levels)

| # | Source | Number in the drafts | Reconciled | Cap |
|---|---|---|---|---|
| T1 | Skill-tree perk S12 (Foraging, tier VI = skill 60) | levels 1-6 | unchanged (node max is 6 in `SkyyTrees/build_skyytrees_0.3.py`) | 6 |
| T2 | Axe by tier | Iron 1, Thorium 2, Cobalt 3, Adamantite 4, Mithril / Onyxium 5, T8+ 6; +1 at Legendary+ | unchanged | 6 |
| T3 | Foraging armor, 4 pieces | Lightwood 1, Hardwood 2, Drywood 3, Darkwood 4, Redwood 5, Goldenwood 6; Wood / Softwood none | unchanged (same levels as the axe ladder) | 6 |
| T4 | Collection rewards "Tree Feller I (Birch VII) / II (Maple VII)" | Collection draft | DELETE; axes and armor give it (Q8 of the revision, default drop) | - |
| T5 | `feller.stackBonus` / `maxLogs` / cooldown | +1 if all three (default 0) / 10 / 3 s | unchanged | 0 / 10 / 3 |

### 1.4 Sickle Range (harvest N more crops each side along the swing)

| # | Source | Number in the drafts | Reconciled | Cap |
|---|---|---|---|---|
| R1 | Sickle roll `srng` | max 3, Mythic 2-3 at Lv 23 | max 3 | 3 (tool part) |
| R2 | Farming armor | T0 -, T1 0, T2 +1, T3 +1, T4 +2, T5 +2, T6 +3, T7 +3 | 0 / 0 / 0 / 1 / 1 / 1 / 2 / 2 (T0-T7) | 2 (armor part) |
| R3 | Total | `tool.range.cap` 4 and `farm.armor.rangeCap` 4 (two rows) | ONE row, by Farming level: min(4, 1 + floor(Farming / 25)) | 4 (row of 9) |

### 1.5 Gathering XP (Wisdom, % extra XP; SkySkills clamps the sum at 5.0)

| # | Source | Number in the drafts | Reconciled | Cap |
|---|---|---|---|---|
| X1 | Tree Wisdom | 15 | unchanged | 15 |
| X2 | Tool roll `mwis` `fwis` `awis` | max 10 (spare boost makes 16.9); old spec 13 | unchanged number, cap added | 15 (`tool.wisdom.cap`) |
| X3 | Armor XP | T4 +2, T5 +4, T6 +6, T7 +8 (all three sets); Mythic x1.3 | unchanged, same ladder in all three sets | 10 (`armor.wisdom.cap`) |
| X4 | Accessories | 3 / 6 / 9 / 12 (Normal to Legendary) | unchanged | 12 |
| X5 | Pets | no XP buff (pets only collect XP) | stays none | 0 |
| X6 | Collections | flat XP lumps (II, VIII, IX), not a percentage | unchanged | - |
| X7 | Pacing x3 to Lv 10, x1.5 by Lv 20 | `docs/answered/gear.md` 2026-10-02 (4) | separate multiplier, not a Wisdom source | - |

Worst case sum 15 + 15 + 10 + 12 = 52%: far below the clamp, so no total cap row is needed.

## 2. Progression check (python)

Model (all assumptions are plain rows): tool Lv = skill, material by band start (Copper 5, Iron 15, Thorium 20, Cobalt 25, Adamantite 35, Mithril 40, Cindersteel 50, Amberite 58, Drakonite 66, Voidglass 76, Aetherium 86); roll level factor 25% at Lv 0 to 100% at Lv 40; armor tier by band start (T7 at skill 50, no armor above T7); Fortune sources as in section 1.
**Typical** = half of the tree Fortune / swing nodes (reached linearly by skill 60), Rare tool (roll 50%), Normal armor one tier behind with the 4-piece x1.15, collections done at each band top, Rare accessory from skill 25 and Legendary from 60, Rare pet (factor 0.6) at pet Lv = skill.
**Maxed** = the best a player can have AT that skill: Fortune and swing tree nodes full by skill 35, Mythic tool with spare boost, Mythic armor at the best tier with the set bonus, collections done at each band start, Rare accessory 20 / Legendary 40, Legendary pet.
Sum = F1 + F2 + F3/4 + F5 + F6 + F7 + F8 before the 100 clamp; Swing = S1 + S2 + S3 + S4 before the 40 clamp.

| Skill | Skill lv | Typical Fortune | Maxed Fortune | Typical swing | Maxed swing |
|---|---|---|---|---|---|
| Mining | 10 | 12.6 | 24.4 | 7.6 | 17.5 |
| Mining | 25 | 36.8 | 63.6 | 20.6 | 45.1 -> 40 |
| Mining | 50 | 77.2 | 106.0 -> 100 | 43.2 -> 40 | 73.1 -> 40 |
| Mining | 75 | 102.2 -> 100 | 121.0 -> 100 | 47.2 -> 40 | 74.3 -> 40 |
| Mining | 100 | 118.5 -> 100 | 136.0 -> 100 | 48.0 -> 40 | 75.6 -> 40 |
| Foraging | 10 | 14.3 | 30.1 | 8.4 | 15.2 |
| Foraging | 25 | 40.9 | 77.8 | 22.5 | 39.4 |
| Foraging | 50 | 85.6 | 126.0 -> 100 | 41.9 -> 40 | 63.1 -> 40 |
| Foraging | 75 | 112.2 -> 100 | 141.0 -> 100 | 44.8 -> 40 | 64.3 -> 40 |
| Foraging | 100 | 128.5 -> 100 | 156.0 -> 100 | 45.5 -> 40 | 65.6 -> 40 |
| Farming | 10 | 15.7 | 32.6 | none | none |
| Farming | 25 | 44.7 | 84.1 | none | none |
| Farming | 50 | 93.3 | 131.0 -> 100 | none | none |
| Farming | 75 | 117.0 -> 100 | 146.0 -> 100 | none | none |
| Farming | 100 | 131.0 -> 100 | 161.0 -> 100 | none | none |

First skill where the 100 clamp is hit: Mining typical 73 / maxed **41**; Foraging typical 60 / maxed **35**; Farming typical 56 / maxed **32**. First skill where raw swing passes 40: Mining 49 / 24; Foraging 50 / 26.

Feller and range check (same model; Feller perk only from skill 60, typical +1 level per 8 skill levels, maxed per 4):

| Skill lv | Typical perk / axe / armor -> logs | Maxed perk / axe / armor -> logs | Sickle total, typical / maxed (new ladder, capped by section 1.4) |
|---|---|---|---|
| 10 | 0 / 0 / 0 -> 0 | 0 / 0 / 0 -> 0 | 1 / 1 |
| 25 | 0 / 3 / 2 -> 4 logs | 0 / 4 / 3 -> 5 logs | 2 / 2 |
| 50 | 0 / 6 / 5 -> 10 | 0 / 6 / 6 -> 10 | 3 / 3 |
| 75 | 2 / 6 / 5 -> 10 | 4 / 6 / 6 -> 10 | 4 / 4 |
| 100 | 6 / 6 / 5 -> 10 | 6 / 6 / 6 -> 10 | 4 / 4 |

## 3. What still breaks the cap early (flags)

1. **Fortune reaches 100 far too early for a maxed player** (skill 32-41, table above), and at skill 100 the unused gear is 36 points (Mining), 56 (Foraging), 61 (Farming). Cause: perk + tree alone is already 70 / 90 / 95 at skill 100, so the whole gear budget fits in 30 / 10 / 5 points. Per-source caps cannot fix that; the sum of caps (Mining 140, Foraging 160, Farming 165) is far above 100. Even a lean set (tool 15, armor 10, accessories 6, pets 6, collections 6) hits 100 at skill 77 / 42 / 40 (maxed). Needs Skyy's call (Q1); gear is a mid-game climb (skill 10-50) in every case.
2. **The Mining tree's +40% swing fills the whole ceiling by itself.** Tool +15, armor +12, pet +5 only matter until the tree is maxed (maxed player at skill 24). Foraging: tree 25 + tool 20 + armor 12 + pet 5 = 62 raw; ceiling at skill 26 (maxed). Not a bug, but the tool / armor swing lines are decoration for maxed players (Q2).
3. **Sickle Range at skill 25.** Old armor ladder (T4 +2) + a Mythic sickle (3) = 5, cap 4 (row of 9) in Zone 2. Fixed by the armor ladder 0 / 0 / 0 / 1 / 1 / 1 / 2 / 2 and the level-based cap (2 at skill 25, 3 at 50, 4 at 75).
4. **Armor Mythic + set bonus exceeds the 15 cap at T7:** 12 x 1.3 x 1.15 = 17.9 -> 15 (T6: 14.95 fits). The old x1.7 would be 23.5. Accepted: only the best Mythic Goldenwood / Onyxium set wastes 2.9.
5. **Tool cap 25 is hit from level alone only by hoes / sickles** (Lv 71: 0.3 x 71 x 1.18 = 25.1). Pick / shovel / hatchet Lv 100 = 24.4, so late hoe and sickle Fortune rolls are wasted. Suggest hoe / sickle `tool.fortune.perLevel` 0.25 (Lv 100 = 30.5, rolls still matter to ~Lv 60) - a number for Skyy, not applied.
6. **Pets:** Mythic factor 1.25 (dragons only) would give a gathering pet 12.5 -> cap 10; keep dragons out of the gathering list. Mount slot (50% buffs): no gathering pet is a mount, so no double-counting today.
7. **Feller arrives before the perk.** Axe and armor give Feller 1 at skill 15 and 10 logs at skill ~50 while the perk (tier VI) starts at 60, so the perk is a mid-late upgrade, not the gate. Keep MAX, `feller.stackBonus` 0 (no cap break).
8. **Accessory Fortune is 0 for Normal and Unique** (Booster spec: Rare +3, Legendary +6), so the early craft path gives only Wisdom. Fine for the cap, but check it is intended (Q5).

## 4. Exact edits per draft (old -> new)

### 4.1 `/home/user/SkyyWynnBlock/research/cloud/Tool-Levels-Revision.md`
| Section | Old | New |
|---|---|---|
| 2 "Swing %" line | "Total swing = tree + tool level + armor" | "tree + tool level + armor + pet, each source capped (tool 15 / 20, armor 12, pet 5), total +40%" |
| 3 table header | "60 (7)" tier | tier 8 at Lv 60 (Amberite starts 58): Pickaxe 13.9, Hoe / sickle 20.9 (was 13.7 / 20.5) |
| 4 rule 3 table, armor row | "one armor ladder 1 / 1.5 ... 12 for Mining, Foraging AND Farming (`research/cloud/Foraging-Armor-Design.md`'s 4 ... 40 becomes this; Q2)" | keep, add "rarity x1 / 1.1 / 1.2 / 1.3 x3, 4-piece x1.15 before the cap, no 2-piece Fortune" |
| 4 rule 3 table, pets + collections rows | "+40 / +60 would be cut to 10" and "sums to ~19; halve it" | pets: "Legendary Lv 100 +10 / +7"; collections: "ladder 1 / 1 / 1.5 / 2 / 2 / 2.5 = 10, same for Farming" |
| 4 rule 3 table | no swing / range / XP rows | add rows: armor swing 12, pets swing 5, accessories swing 0, tool Wisdom 15, armor Wisdom 10 |
| 4 last paragraph | "On-level player ... Mining 16 / 44 / 75 / 98 / 100 ..." | replace by the section 2 table here (typical vs maxed; clamp hit at skill 32-41 for maxed) |
| 9 "Cap:" | "tool + Farming armor <= `tool.range.cap` 4" | "<= min(4, 1 + floor(Farming / 25)); tool part max 3, armor part max 2" |
| 11 rows | `armor.fortune.cap`, `pets.fortune.cap`, `coll.fortune.cap` | add `armor.swing.cap` 12, `pets.swing.cap` 5, `tool.wisdom.cap` 15, `armor.wisdom.cap` 10, `tool.range.capPerFarming` 25 |
| 14 Q1 / Q2 | open | point to Q1 / Q2 here |

### 4.2 `/home/user/SkyyWynnBlock/research/cloud/Foraging-Armor-Design.md`
| Section | Old | New |
|---|---|---|
| 4 intro text | "100 = one guaranteed extra log ... armor target is about 30% of the Fortune budget, so a full Goldenwood set = 40" | "1 point = +1% double drop; armor cap 15; full Goldenwood = 12 (x1.15 set bonus, x rarity)" |
| 4 table, Fortune column | 4 / 8 / 12 / 16 / 22 / 28 / 34 / 40 | 1 / 1.5 / 2.5 / 4 / 5.5 / 7.5 / 10 / 12 |
| 4 table, chopping speed column | +2 / 4 / 6 / 9 / 12 / 16 / 20 / 25% | +1 / 2 / 3 / 4 / 6 / 8 / 10 / 12% (no rarity multiplier) |
| 4 bullet "Rarities" | "gathering armor is crafted, so it is Normal" | add "reforge / drops may raise it; Fortune x1 / 1.1 / 1.2 / 1.3 / 1.3 / 1.3" |
| 5 set-bonus table, 2 pieces | "+25% of the set's Fortune" | remove; 4 pieces: Fortune x1.15 plus Tree Feller + Sap Sense |
| 6 last sentence | "This matches the collection draft: Feller I appears at Birch ... II at Maple" | delete (collection rewards dropped, section 1.3 T4) |
| 8 rows | "2-piece Fortune bonus % 25" | "4-piece Fortune multiplier 1.15"; add `armor.fortune.cap` 15, `armor.swing.cap` 12 |
| 9 last row | "`foraging.fortune.cap` default 200" | "per-source caps + `perk.doubleDropMax` 1.0" |
| 9 first row | "Feller logs get Fortune at half rate" | "at `bonusBlock.fortuneRate` 50%" (same number, shared name) |
| Q3 / Q8 | "full Goldenwood = 40" / "Wood armor gives Fortune 4" | "= 12" / "yes, 1" |

### 4.3 `/home/user/SkyyWynnBlock/research/cloud/Gathering-Armor-Mining-Farming.md`
| Section | Old | New |
|---|---|---|
| 1.2 text "Rarity multiplies like tools: ... Legendary x1.35, Fabled x1.5, Mythic x1.7" | x1.0 / 1.1 / 1.2 / 1.35 / 1.5 / 1.7 | x1.0 / 1.1 / 1.2 / 1.3 / 1.3 / 1.3 (Fortune and Wisdom only; not swing, not range) |
| 1.2 Mining Speed bullet | speed shares the 40% cap | add "armor swing cap 12, no rarity multiplier" |
| 1.3 set bonus row | "the tier's Fortune is multiplied x1.15 when held tool = pickaxe or shovel" | "x1.15, applied before the 15 cap; same rule in all three sets" |
| 2.2 Sickle Range column | 0 / +0 / +1 / +1 / +2 / +2 / +3 / +3 | 0 / 0 / 0 / +1 / +1 / +1 / +2 / +2 (T0-T7) |
| 2.2 cap bullet | "total capped at +4 blocks (row `farm.armor.rangeCap`)" | "one row with the tool: min(4, 1 + floor(Farming / 25))" |
| 3.1 table | T7 Mythic x1.7 = 20.4; totals 83.9 / 108.9 / 103.4 | T7 Mythic = min(15, 17.9) = 15; totals Mining 25+20+25+15 = 85 at 50 (before pets, accessories, collections) |
| 3.1 "Recommendation: lower Mythic armor mult to x1.3" | recommendation | adopted (decision) |
| 3.2 | "tree 20% (per level 1% to 25) ... total 35.6%" | "tree up to 40% (1.6% x 25), armor 12 (no multiplier): the sum reaches the +40% ceiling" |
| 5 rows | `farm.armor.rangeCap` 4; rarity "1 / 1.1 / 1.2 / 1.3 / 1.3 / 1.3" | delete the first (merged into the tool row); keep the second; add `armor.swing.cap` 12 |
| Q6 | "15%" | confirmed (this file section 1.1 F5) |

### 4.4 `/home/user/SkyyWynnBlock/research/cloud/Pets-Spec.md` (section 5.1)
| Pet | Old | New |
|---|---|---|
| Rabbit | "+60 Farming Fortune; +5% crop double-drop; fast crops" | "+10 Farming Fortune; fast crops" |
| Chicken | "+40 Farming Fortune" | "+7 Farming Fortune" |
| Goat | "+60 Mining Fortune; +10% Mining Speed" | "+10 Mining Fortune; +5 swing" |
| Warthog | "+40 Mining Fortune" | "+7 Mining Fortune" |
| Bear | "+60 Foraging Fortune; trees fall faster" | "+10 Foraging Fortune; +5 swing (UNVERIFIED how)" |
| Turkey | "+40 Foraging Fortune" | "+7 Foraging Fortune" |
| Section 1 rules table | none | add rows `pets.fortune.cap` 10, `pets.swing.cap` 5; "no Mythic gathering pet" |
(Values shown are at Legendary Lv 100; the rarity factor x L / 100 rule of section 2 is unchanged.)

### 4.5 `/home/user/SkyyWynnBlock/research/cloud/Collection-Unlocks-Draft.md`
| Section | Old | New |
|---|---|---|
| 4 text | "+2 / +2 / +3 / +3 / +4 / +5 ... about +20 per skill" and "tools 40%, armor 30%, collections 15%, pets/accessories 15%" | "+1 / +1 / +1.5 / +2 / +2 / +2.5 = 10 per skill, same for all three"; budget line replaced by the section 1.1 caps |
| 3 Mining IX cells | Copper +2, Iron +2, Thorium +3, Cobalt +3, Adamantite +4, Mithril +5 | +1, +1, +1.5, +2, +2, +2.5 |
| 3 Foraging IX cells | Oak +2, Birch +2, Maple +3, Redwood +3, Azure +4, F5 +5 | same ladder |
| 3 Farming IX cells | Wheat +2, Carrot +2, Corn +2, Pumpkin +3, Tomato / Cotton / Rice +3, Potato +4 | +1, +1, +1.5, +2, +2, +2.5 |
| 3 Birch VII / Maple VII | "Tree Feller I", "Tree Feller II" | free slots (e.g. a Foraging XP lump or a Foraging Bag step; Skyy picks) |
| 3 line 63 "Tree Feller:" note | "tiers VII and later unlock Tree Feller levels on axes and armor" | delete |
| 3 Cobblestone VII / VIII | "Haste accessory I / II (Miner's Charm)" | "Prospector accessory recipe (Rare / Legendary, Fortune +3 / +6)" until Q3 gives swing a number |

### 4.6 `/home/user/SkyyWynnBlock/research/Booster-Accessories-Spec.md` and `/home/user/SkyyWynnBlock/research/cloud/Accessory-Acquisition.md`
| File | Section | Old | New |
|---|---|---|---|
| `/home/user/SkyyWynnBlock/research/Booster-Accessories-Spec.md` | 3 wave 2 bullet | "Before building, check the Fortune numbers against the skills' own double-drop perk" | "Checked 2026-10-06: Rare +3 / Legendary +6 stays; accessory Fortune cap 10 (`accessories.fortune.cap`); no swing line (see `/home/user/SkyyWynnBlock/research/cloud/Gathering-Numbers-Reconciled.md`)" |
| `/home/user/SkyyWynnBlock/research/cloud/Accessory-Acquisition.md` | wave 2 row (line 40) | no stat note | add "Normal / Unique Prospector give Wisdom only, Fortune starts at Rare" |

No edit needed: `/home/user/SkyyWynnBlock/research/cloud/Armor-Types-Spec-Draft.md` (line 121 only points at the Foraging draft) and `/home/user/SkyyWynnBlock/research/cloud/Gathering-Tiers-Draft.md` (hoe / sickle Fortune only, already right).

## For the local session (UNVERIFIED)

1. Whether SkyyGear can add `armor.swing`, `pets.swing` and `armor.fortune` as separate sources in `skill:bonus:<uuid>` and SkyyTrees can sum tree + tool + armor + pet swing into one of its 40 hidden tiers (revision UNVERIFIED 1).
2. How the Stats page should show "Mining Fortune 136 (cap 100)" and which source was clamped.
3. Whether SkyySkills clamps `dd` at 1.0 before or after the per-source caps (read `SkillBonus.sum`, `Perks.chanceU`).
4. Real gathering XP per hour at each tier, to check the typical-player model (tree share, collection timing) of section 2 and the pet XP curve.
5. Bear "trees fall faster": is there any swing hook for a pet, or is it only a flavour line?

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | A fully maxed player reaches 100 Fortune at skill 32-41, and at skill 100 perk + tree already give 70 / 90 / 95. Keep the hard 100 (gear is a mid-game climb), or let Fortune over 100 give a second extra-drop chance (every 100 = +1 drop, `perk.doubleDropMax` 2.0)? | keep 100, no overflow |
| 2 | Mining tree swing +40 fills the whole swing ceiling, so tool / armor / pet swing is wasted once the tree is maxed. Accept, or turn the armor / pet speed into Power (fewer hits)? | accept |
| 3 | Any accessory swing ("Haste accessory I / II")? | no, relabel as Prospector |
| 4 | Collection Fortune ladder 1 / 1 / 1.5 / 2 / 2 / 2.5 (10 per skill), same for Farming? | yes |
| 5 | Should Normal and Unique Prospector / Woodsman / Harvester give a small Fortune (1 / 2) or only Wisdom? | only Wisdom |
| 6 | Sickle Range cap by Farming level (2 at 25, 3 at 50, 4 at 75) and armor ladder 0 / 0 / 0 / 1 / 1 / 1 / 2 / 2? | yes |
| 7 | One armor set bonus: Fortune x1.15 at 4 pieces in all three sets, Foraging's 2-piece +25% removed? | yes |
| 8 | Hoe / sickle Fortune per level 0.3 -> 0.25, so rolls matter past Lv 71? | yes |
| 9 | Free the Birch VII / Maple VII collection slots (Feller I / II dropped) - what goes there? | Foraging XP lump |
