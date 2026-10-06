# Capstone sets - the Department's issued uniforms

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `research/cloud/Capstone-Dungeon-Spec.md` (floors, chest, rolls, "Set rarity only here"), `research/cloud/SkyyArmory-Roadmap.md` (T11 Voidglass 76-88, T12 Aetherium 86-100, "Aetherium = Voidglass x1.2"), `docs/answered/gear.md` (armor types LOCKED 2026-10-05; "if it is not in the game yet, do not leave it in the reforge list" 2026-09-30; unidentified loot; reforge level-up +6), `SkyyGear-Stat-Catalog.md` (read-only), `research/SkyyGear-Stage1-Spec.md` (the live stat list), `research/Isles-of-the-Void-Lore.md` voice. Every number is a placeholder and a Server Setup row.

**(updated 2026-10-06: slot fix)** Vanilla armor slots appear to be **Head / Chest / Hands / Legs** - no Boots slot (vanilla Mithril textures: Chest, Head, Legs, Hands - `docs/answered/gear.md` line 73; **UNVERIFIED**). The two Boots pieces are gone: boot looks (greaves, slippers) are now the lower part of the **Legs** piece, and the Light and Cloth sets take **Hands**. Each set still has 3 pieces, so every balance number is unchanged. Inputs added: `research/cloud/Capstone-Floors-4-7.md` (section 8, piece order per floor).

## 1. Rules this design follows

| Rule | Source | Effect here |
|---|---|---|
| Set rarity (green `#55FF55`) drops **only** in The Final Audit | capstone spec section 5.2 | no craft, no shop, no AH-only source (AH resale of a dropped piece is allowed) |
| A stat that does nothing is never listed | Skyy 2026-09-30 | every bonus carries a status (section 4); "later" stats are **hidden** until they work |
| Armor types are soft: anyone can wear any armor, class bonus only for the matching class | gear.md 2026-10-05 | the set bonus works for **everyone** wearing it (a Warrior in a Cloth set gets its bonus), the **type trade-offs** (speed, Defense) follow the armor, not the class |
| Item level = what the piece drops at | gear.md levels | Voidglass F1-F4 = 76 / 79 / 82 / 85; Aetherium F5-F7 = 88 / 91 / 94 (cap 100 with Master Mode later) |

## 2. The three sets (Voidglass and Aetherium versions)

Each set is **3 pieces**; the 4th armor slot is a normal piece (so a set never fills the whole body, and a Legendary can fill the gap). The free slot differs per type so the loot talks to the type. (updated 2026-10-06: slot fix) The 4 slots are Head / Chest / Hands / Legs; feet are drawn as part of the Legs piece. Recommended: **3 of 4** (below); the alternative "all 4 slots, 2 / 4-piece bonus" is costed in section 3.1 and kept as Question 1.

| Type | Class fit | Slots (3 of 4) | Free slot | Voidglass set (F1-F4) | Aetherium set (F5-F7) |
|---|---|---|---|---|---|
| **Heavy** | Warrior, Berserker | Head, Chest, Legs | Hands | **The Bailiff's Plate** | **The Chief Bailiff's Plate** |
| **Light** | Archer, Assassin, Monk | Head, Chest, Hands | Legs | **The Clerk's Leathers** | **The Senior Clerk's Leathers** |
| **Cloth** | Mage, Priest | Chest, Legs, Hands | Head | **The Notary's Robes** | **The High Notary's Robes** |

Why these (updated 2026-10-06: slot fix): Heavy keeps its stamp helm and moves the greaves into a full Legs piece (cuisses + knee cops + greaves + sabatons); Light swaps the trousers for **Hands** (bow grip, daggers, fists - the Light classes live in their hands) so all three sets leave a **different** slot free; Cloth folds the slippers into the skirts and gains gloves for signing. Old -> new: Bailiff Boots -> Legs; Clerk Legs -> Hands; Notary Boots -> merged into Legs, new Hands piece.

### 2.1 Pieces and lore lines (Department voice)

| Set | Piece | Name | Lore line (tooltip, italic grey) |
|---|---|---|---|
| Bailiff's Plate | Helmet | Bailiff's Stamped Visor | "Issued on Form 27-B/6. Shall not be removed during an objection." |
| | Chest | Bailiff's Overruling Cuirass | "Every dent is a filed complaint. All were denied." |
| | Legs | Bailiff's Footnote Greaves (cuisses, greaves and sabatons in one piece) | "Stands firmly on the small print." |
| Clerk's Leathers | Helmet | Clerk's Eyeshade | "Reading glasses sold separately. The reading is mandatory." |
| | Chest | Clerk's Filing Jerkin | "Forty pockets. Thirty-nine are for receipts." |
| | Hands | Clerk's Quick-Reference Mitts (fingerless, index tabs on the cuffs; was the Trousers) | "Cross-referenced, indexed and fast. Fingertips not included." |
| Notary's Robes | Chest | Notary's Sealed Robe | "Legally binding. Also warm." |
| | Legs | Notary's Margin Skirts (with the Waiting-Room Slippers sewn on) | "Written in the margins, as is tradition. Slippers worn soft by an eternity of queuing." |
| | Hands | Notary's Signing Gloves (new) | "Sign here. And here. Initial here. And here." |
| Aetherium versions | all | prefix "Chief", "Senior" or "High", e.g. "Chief Bailiff's Stamped Visor" | Same line plus a second: "Promoted. The pay is the same." (Bailiff), "Reclassified. Please take a new number." (Clerk), "Approved in triplicate by the Void itself." (Notary) |

Art: `research/cloud/capstone-set-art/capstone-sets-sheet.png` (slot-fixed; the old 3-pieces-with-Boots sheet is `capstone-sets-sheet-v1.png`). Look: Voidglass = dark smoked glass over the type's own base (Heavy plate, Light black leather + glass trim, Cloth robe with glass buttons); Aetherium = pale silver-blue with floating runes (roadmap T12). Set pieces share the green name colour and a small green "set stamp" badge.

## 3. Balance vs a normal Legendary piece (same level)

Unit B = the rolled-modifier value of one Legendary piece at that level (the Legendary has **4** rolled lines, placeholder; SkyyGear's real count: UNVERIFIED).

| Piece | Lines | Value | Why |
|---|---|---|---|
| Legendary, level L | 4 rolled | 1.00 B | the baseline |
| **Set piece, level L** | **3 rolled + 1 fixed type line** | **~0.95 B** alone | the fixed line is the type identity at average Legendary value; one fewer free roll |
| 2 set pieces | + 2-piece bonus | **~1.00 B** each | bonus ~ 10% of the pair (the pair equals Legendary) |
| 3 set pieces | + 3-piece bonus | **~1.08 B** each (+~13% total) | the set rewards the full farm: ~3 Legendary + 13% |
| 3 Mythic pieces | none | ~1.20 B each | a perfect Mythic still beats the set in raw numbers, the set wins in **certainty** (fixed lines, no reforge gamble) |

Rule of thumb for tuning: **a full 3-piece set must land between 3 Legendary and 3 Mythic pieces** (about 105-115%). The 4th slot is free for a Legendary or Mythic so players keep choosing. Aetherium = Voidglass x1.2 on every number (roadmap), rounded. (updated 2026-10-06: slot fix) Still 3 pieces per set, so nothing in this table or section 4 changes.

### 3.1 The alternative: all 4 slots, 2 / 4-piece bonus (not recommended; Question 1)

| Build (4 slots) | Value (python-checked) | Note |
|---|---|---|
| 3-piece set + Legendary (recommended design) | 3.24 + 1.00 = **4.24 B** | |
| 3-piece set + Mythic | 3.24 + 1.20 = **4.44 B** | the best mix today |
| 4-piece alternative: 2 set + 2 Mythic | 2.00 + 2.40 = **4.40 B** | the bar a full 4-set must clear |
| 4-piece alternative: full set at 112% of 4 Legendary | **4.48 B** | 4-piece bonus = 4.48 - 4 x 0.95 = 0.68 B = **1.74x** the 3-piece bonus (0.39 B) |

So under 2 / 4 the 4-piece line would be the 3-piece line x1.74, rounded: Bailiff Defense +26% / Crit Damage +35 / Life Steal +5 (Aetherium 31 / 42 / 6); Clerk Crit Chance +14 / Speed +9% / Strength +10% (17 / 10 / 13); Notary Magical Power +24% / Max Mana +35% / Mana Steal +5 (29 / 42 / 6); 2-piece lines unchanged. Costs: one more piece to farm (4 floors' worth per tier, the launch F1-F3 no longer complete a set), no free slot for a Legendary / Mythic choice, and a 4th piece name / art per set. Recommended: stay with **3 of 4**.

## 4. Set bonuses and stat status

Status key: **LIVE** = in the SkyyGear 0.1 live list (Stage1 spec: Damage %, Strength, Magical Power, Crit Chance, Crit Damage, Overcrit, elemental and True Damage, Defense, Speed, Health Regen, Health Regen %, Stamina Regen, Life Steal, Mana Steal; armor Health); **READY?** = in the catalog as Keep and wanted by the armor-type lock but SkyyGear status not confirmed (UNVERIFIED, section 9); **LATER** = shown "(coming later)" today, so **never listed** in a bonus until it works.

### 4.1 The Bailiff's Plate (Heavy)

| Bonus | Voidglass | Aetherium | Stat status |
|---|---|---|---|
| 2 pieces "Objection" | Defense +8%, Crit Damage +10 | Defense +10%, Crit Damage +12 | Defense LIVE, Crit Damage LIVE |
| 3 pieces "Overruled" (replaces the 2-piece line) | Defense +15%, Crit Damage +20, Life Steal +3 | Defense +18%, Crit Damage +24, Life Steal +4 | LIVE, LIVE, LIVE |
| Not used | Thorns (LATER) - a natural fit, joins when it works | | LATER, hidden |

### 4.2 The Clerk's Leathers (Light)

| Bonus | Voidglass | Aetherium | Stat status |
|---|---|---|---|
| 2 pieces "Fast Track" | Crit Chance +4, Speed +3% | Crit Chance +5, Speed +4% | LIVE, LIVE |
| 3 pieces "Express Lane" | Crit Chance +8, Speed +5%, Strength +6% | Crit Chance +10, Speed +6%, Strength +7% | LIVE, LIVE, LIVE |
| Not used | Attack Speed (LATER; Light's type stat) | | LATER, hidden: add as a **new row** the day SkyyGear ships it (never advertised before) |

### 4.3 The Notary's Robes (Cloth)

| Bonus | Voidglass | Aetherium | Stat status |
|---|---|---|---|
| 2 pieces "Seal" | Magical Power +8%, Max Mana +10% | Magical Power +10%, Max Mana +12% | Magical Power LIVE, Max Mana READY? |
| 3 pieces "Notarised" | Magical Power +14%, Max Mana +20%, Mana Steal +3 | Magical Power +17%, Max Mana +24%, Mana Steal +4 | LIVE, READY?, LIVE |
| If Max Mana is not live at ship | swap Max Mana for **Health Regen %** (+15% / +30%) so no line is dead | | Health Regen % LIVE |

Arithmetic check: x1.2 of 8 / 10 / 15 / 20 / 5 / 4 / 6 / 12 = 9.6 / 12 / 18 / 24 / 6 / 4.8 / 7.2 / 14.4, rounded to the table. A Warrior in the Notary's Robes still gets Magical Power (it does little for them); that is the soft-armor rule, not a bug.

## 5. Which floor drops which piece

| Tier | Floor (item level) | Drops | Slot rule |
|---|---|---|---|
| Voidglass | F1 Records Hall (76) | piece 1 of any type | the first slot of the set (Heavy Head, Light Head, Cloth Chest) |
| | F2 Archives (79) | piece 2 | second slot |
| | F3 Tab Office (82) | piece 3 | third slot |
| | F4 Dragon's Nest (85) | any piece (the "makeup exam") | the slot the player owns least of |
| Aetherium | F5 Lost & Found (88) | piece 1 | as above |
| | F6 Void Counter (91) | piece 2 | |
| | F7 Auditor's Chair (94) | piece 3 + any piece | the final boss always offers the missing piece |

Piece order per type (updated 2026-10-06: slot fix; same order for Voidglass F1-F3 and Aetherium F5-F7, see `research/cloud/Capstone-Floors-4-7.md` section 8):

| Piece | Heavy (Bailiff) | Light (Clerk) | Cloth (Notary) |
|---|---|---|---|
| 1 (F1 / F5) | Head - Stamped Visor | Head - Eyeshade | Chest - Sealed Robe |
| 2 (F2 / F6) | Chest - Overruling Cuirass | Chest - Filing Jerkin | Legs - Margin Skirts |
| 3 (F3 / F7) | Legs - Footnote Greaves | Hands - Quick-Reference Mitts | Hands - Signing Gloves |
| never | Hands (free) | Legs (free) | Head (free) |

- At launch only F1-F3 exist, so the Voidglass set is **fully collectable with the launch floors** (pieces 1-3). F4 and Aetherium come with the later floors.
- A set drop is one of the floor chest's **gear rolls** (`gear:fn:roll`), arriving **unidentified** like all dungeon gear. The type (Heavy / Light / Cloth) is chosen with the Loot-Box "class-lean" weight: **50%** the opener's class type, 25% each of the others (so a Priest sees Cloth most but can find Heavy to trade).
- Chance: **8% per gear roll** (`dungeon.setChancePercent`). Rolls by rank: D 1, C 1+, B 2, A 3, S 4. P(at least one set piece in a chest) = 8% / 15.4% / 22.1% / 28.4% for 1 / 2 / 3 / 4 rolls (computed).
- Sets drop from the **boss chest only** (not from secret rooms, which give pet eggs, fragments and titles) so the set is the rank reward.

## 6. Duplicate protection (bad-luck protection)

| Rule | Value |
|---|---|
| Missing-slot weighting | a set roll picks the slot per the table, then if the profile already **owns** (any storage it can see: inventory, vault, bags) that exact slot and type and tier, the roll is moved to a **missing** slot of the **same type** and tier |
| Complete set | when all 3 slots are owned, duplicates are allowed again (players chase better modifier rolls) |
| Pity | after **12** gear-roll chests without a set piece, the next chest **guarantees** one (`dungeon.setPityChests`); counter per profile, resets on a set drop; at 8% per roll and about 2 rolls a chest the expected wait is about 6 chests |
| Daily cap | the 12 chests per day limit still applies; pity counts chests actually opened |
| No cross-tier collecting | Voidglass pieces never count toward Aetherium |
| Unclaimed | a dropped set piece is created on chest **open** (capstone spec section 10), never twice |

## 7. How SkyyGear carries the set (UNVERIFIED)

SkyyGear already has a `set` rarity. Proposal: a set piece is an ordinary gear item with rarity `set`, its type and slot (Head / Chest / Hands / Legs) like any armor, plus **one string field `setId`** (e.g. `bailiff_voidglass`, `bailiff_aetherium`) in the same item metadata where rarity and level live. A tick (or the equip event) counts worn pieces per `setId` and adds the 2 / 3 piece rows to the player's stat total through the same path as armor modifiers. Other mods read it only through the bridge: `gear:fn:setCount` returns a `java.lang.Integer` for a given id (plain types, per the cross-mod rule). Both `setId` and the count are **UNVERIFIED** until the local session reads SkyyGear.

## 8. Identify, reforge, level-up, tooltips

| System | Set pieces |
|---|---|
| **Identify** | drops unidentified ("Unidentified Set Chestplate" / "... Helmet" / "... Leggings" / "... Gloves", Lv 79, green; slot names follow the vanilla slot words, UNVERIFIED); identify reveals **type, slot, name and the 3 rolled lines**; the fixed line and `setId` are visible at once only after identify (keeps the surprise). Identify cost uses a **Set multiplier** (placeholder x1.5 of Legendary) |
| **Reforge** | **allowed on the 3 rolled lines only**; the fixed type line and `setId` are locked and never rerolled; same coin cost as Legendary x1.5; the Smithing "better reforge rolls" node applies |
| **Reforge level-up** | allowed (+6 over the found level, never above 100); set bonuses use a **fixed table per tier**, not the item level, so levelling never changes a bonus |
| **Identify rarity-up node** (Smithing) | **cannot** step a Set piece (it is already at the top and is not on the Mythic path); Set is never crafted |
| **Mixed tiers** | 2 Voidglass + 1 Aetherium piece = the Voidglass bonus for 3 pieces (the lowest tier among the counted pieces) |
| **Tooltip** | green name; "Lv 82 - Requires class skill 82"; the lines; then the set block: "The Bailiff's Plate (2/3)", the three pieces listed (worn bright, missing grey, lore-style names), then "2 pieces: Objection - Defense +8%, Crit Damage +10" and "3 pieces: Overruled - ..." with the active ones in green and inactive grey. A LATER-stat line is never printed. Lore line last in italic |

## 9. Server Setup rows

`dungeon.setDropOnly` (on; from the dungeon spec), `dungeon.setChancePercent` (8), `dungeon.setPityChests` (12), `dungeon.setTypeLeanPercent` (50), `dungeon.setIdentifyMult` (1.5), `dungeon.setReforgeMult` (1.5), `gear.set.<setId>.2pc` and `.3pc` rows (one text row per set: `def=8,critDmg=10`), `gear.set.aetheriumMult` (1.2), `gear.set.enabled` (on), `gear.set.showLater` (off; never shows a LATER stat).

## For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | SkyyGear: how rarity `set` is stored today and whether a custom field (`setId`) can sit in the item metadata without breaking AH / sacks / trade. |
| 2 | How many modifier lines each rarity rolls today (the "Legendary = 4" assumption) and the Set rarity's current count. |
| 3 | **Max Mana and Mana Regen on armor**: the catalog says "Equipment only" and "Equipment and accessories" but the armor-type lock gives Cloth Mana and Mana Regen on armor; is Max Mana live? |
| 4 | Does Defense scale as a percent (the "+8% Defense" lines) or only flat; if flat, convert to a flat value per level. |
| 5 | Crit Damage / Life Steal / Strength: confirm all LIVE in the running SkyyGear (Stage1 list is from 0.1). |
| 6 | The equip event or tick cost for counting worn set pieces (every armor change vs every second). |
| 7 | Whether unidentified items can carry a hidden `setId` (the sealed real id covers the item, check the set tag survives). |
| 8 | Attack Speed and Thorns ship dates, to add the Light and Heavy "later" lines. |
| 9 | (updated 2026-10-06: slot fix) **The real armor slot list** in Assets.zip / HytaleServer.jar: confirm Head / Chest / Hands / Legs and **no Boots** (the fix rests on the vanilla Mithril texture list), whether the Legs model covers the feet (the sabatons / slippers are drawn as part of Legs), and the vanilla slot words for the unidentified names. If a Boots slot does exist, the v1 layout (`capstone-set-art/capstone-sets-sheet-v1.png`) still works. |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | (updated 2026-10-06: slot fix) Slots are Head / Chest / Hands / Legs (no Boots). Three set pieces with the 4th slot free, or all 4 slots with a 2 / 4-piece bonus (4-piece line = 3-piece x1.74, section 3.1)? | 3 of 4 (Heavy: Hands free, Light: Legs free, Cloth: Head free) |
| 2 | Does a set bonus work for every class, or only for the matching class? | everyone (soft armor rule); type trade-offs follow the armor |
| 3 | Is a full set about 105-115% of three Legendary pieces about right, or should sets beat Mythic? | between Legendary and Mythic |
| 4 | Set chance 8% per roll with a guaranteed piece after 12 chests? | yes |
| 5 | Set pieces from the boss chest only (not the secret rooms)? | boss chest only |
| 6 | Names (Bailiff / Clerk / Notary) and the "Chief / Senior / High" Aetherium prefixes OK? | yes |
| 7 | Add Thorns (Heavy) and Attack Speed (Light) to the bonuses the day they go live? | yes, as new rows |
| 8 | Can set pieces be traded or sold on the AH, or soulbound to the finder? | tradeable (it is a farming game; the daily cap limits flooding) |
| 9 | (updated 2026-10-06: slot fix) Clerk's Leathers: Hands (Quick-Reference Mitts, Legs free) so each set frees a different slot, or keep the Trousers (Legs) and leave Hands free like the Bailiff? | Hands |
| 10 | (updated 2026-10-06: slot fix) Boot looks folded into Legs (Bailiff greaves + sabatons, Notary slippers sewn to the skirts) - OK? | yes |
