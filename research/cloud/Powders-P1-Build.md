# Powders P1 - build spec (items + sockets + Anvil Powders tab)

Cloud build spec, 2026-10-23. Paper only, nothing built. Source draft: `research/cloud/Powders-Spec-Draft.md` (its defaults are taken
unless a `docs/answered/` line says otherwise; every change from the draft is marked **CHANGED** with the reason).
Facts marked **SCRIPT** were read from the live generated scripts in this repo (`SkyyGear/build_skyygear_0.3.40.py`,
`SkyySacks/build_skyysacks_0.8.28.py`); facts that need `Assets.zip` / `HytaleServer.jar` / the game are **UNVERIFIED** and listed at the end.
Numbers are placeholders until `tools/balance_model.py` sets them (P0 below).

## 0. Decisions followed

| Source (file : line) | Line (short) | What it fixes here |
|---|---|---|
| `docs/answered/gear.md` : 284 | 2026-10-18 ELEMENTS Q10: "Powders (Wynncraft-style gem slots you put element powders into, to add element damage / defence to gear): write their spec right after the element system ships?" -> "Yes, next spec (Recommended)" | this spec exists; powders add element damage (weapon) / Defence (armor) |
| `docs/answered/gear.md` : 277 | Q3 PETS: pets "increase your damage (but only if you use its element" | the pet gate `W_e > 0`; a weapon powder opens it (Q4) |
| `docs/answered/gear.md` : 278 | Q4 DEFENCE NOW: armor element Defence lines -> "Now" | armor powders feed the live `dX` sum |
| `docs/answered/gear.md` : 166 | 2026-10-11 GEMS: "most gear has 1 gem slot. legendarys, UTs and specials have between 2 and 3 gem slots. slots cab be added and removed. (gems DO NOT have levels or rarities, they give a flat bonus" | socket counts by rarity (section 3); Add socket AND Remove (empty) socket (**CHANGED**: the draft offered no socket removal; Skyy's line says "added and removed") |
| `docs/answered/gear.md` : 161, 189 | ONE Anvil tab (Reforge + Upgrade), Identify its own view | Powders = a third Anvil sub-tab, no new page, no new command |
| `docs/answered/gear.md` : 176, 222 | Sigils raise rarity, skip tiers | socket count follows the CURRENT rarity, so a Sigil raises it with no extra code (section 3) |
| `docs/answered/ui.md` : 86, 144 | merged menus; every hub page 1600 x 980, row 2 big | page follows `research/Menu-Pattern.md` (M3: Anvil has sub-tabs) |
| `docs/answered/ui.md` (Style Guide 15 rule, 2026-10-18) | "color code everything" | lang `<color is=...>` spans, element colours = SkyyGear `GearView.elemCol` (SCRIPT: Earth `#5dbb4a`, Thunder `#ffd84d`, Water `#4fa8ff`, Fire `#ff6a3d`, Air `#c8f5ee`) |
| `PROJECT-RULES.md` section 4 | tier tags, sort by tier, Server Setup for everything, no dev gates, one-time migrations | own ladder "T3 Powder"; lists sorted tier then element; rows in section 6; default ON; no migration needed |
| `research/Alchemy-Skill-Spec.md` : 23, 342-384 | "Reforging and powders feed it later through `skill:fn:addxp`"; "Alchemy is table use only. The Alchemy Bench accessory and the /craft Alchemy tab go away" (line 32) | Smithing XP per powder added via `skill:fn:addxp`; recipes go on the VANILLA Alchemy Bench (**CHANGED**: the draft's "/craft Alchemy tab" no longer exists) |
| `research/Wynn-Elements-Build-Spec.md` 3.1-3.2 | `raw_e = W_e + C_e + (W_e > 0 ? P_e : 0) + I_e`; `D_e = gear:fn:elemDef` | powders join `W_e` / `D_e` once, inside SkyyGear's `totals0` (section 4) |
| `research/Skill-Trees-Spec.md` 26, 99 | "Powder" is reserved for gear powders | the word is free to use |

grep of `docs/answered/*.md` for powder / socket / anvil / element found no line that overrides a draft default other than the two marked CHANGED.

## 1. Scope of P1

In: the 25 powder items (assets, lang, icons, Alchemy Bench recipes), sockets on weapons + combat armor (saved on the item doc), powder
lines in the element sums, tooltip pips, the Anvil **Powders** sub-tab (add / replace / remove powder, add / remove socket), Smithing XP,
Server Setup rows, the Combat bag accepting powders, the tier ladder word.

Out (later rounds, unchanged from the draft split): mob / boss / chest drops (SkyyMobs, loot tables), Traveling Merchant stock
(SkyyMerchants), Bazaar products, a Powders collection, salvage / NPC-sale "this item has powders" confirms, the flat-element cap
(`powder.capPct`, **CHANGED**: left out of P1 - it needs a hit-path change; sockets x tier value is the bound, Q8), powder specials.
In P1 powders come only from crafting (and `/give` for testing).

## 2. Items

### 2.1 Ids, names, materials (25 items, owner SkyyGear)

Id pattern `Skyy_Powder_<Element>_<n>`, element in Wynn order, n = 1..5. Elements use the live spelling (Earth, Thunder, Water, Fire, Air).

| Element | Ids | Display names | Base material (Powder I recipe) | Bag of the material (SCRIPT, Sacks `homeOf`) |
|---|---|---|---|---|
| Earth | `Skyy_Powder_Earth_1` .. `_5` | Earth Powder I .. V | `Ingredient_Crystal_Green` (Green Crystal Shards) | Mining |
| Thunder | `Skyy_Powder_Thunder_1` .. `_5` | Thunder Powder I .. V | `Ingredient_Lightning_Essence` | Combat |
| Water | `Skyy_Powder_Water_1` .. `_5` | Water Powder I .. V | `Ingredient_Water_Essence` (**CHANGED**: the draft used Ice essence; a Water essence exists in the live Bazaar table) | Combat |
| Fire | `Skyy_Powder_Fire_1` .. `_5` | Fire Powder I .. V | `Ingredient_Fire_Essence` | Combat |
| Air | `Skyy_Powder_Air_1` .. `_5` | Air Powder I .. V | `Ingredient_Crystal_Cyan` (Cyan Crystal Shards) | Mining |

All five materials are rows of the live Bazaar product table (`research/balance/economy.md` 175-176, 529-532; prices 112.5 - 135), so
they are real item ids today; the build still asserts each against `Assets.zip` (UNVERIFIED here). The draft's Air (Wind / Zephyr essence)
and Earth (golem crystal) items are replaced by these two crystals (**CHANGED**: no unverified ids; same price band as the essences).

### 2.2 Item asset (one JSON per id) - copy the Sigil pattern

Template = the 0.3.4 Sigils block in `SkyyGear/build_skyygear_0.3.40.py` (SCRIPT: `SIG_ITEMS`, `SIG_FILES`, `SIG_LANG`, `EXTRA.update`):

| Field | Value |
|---|---|
| file | `Server/Item/Items/SkyyGear/Skyy_Powder_<E>_<n>.json` (jar path) |
| `TranslationProperties` | `{"Name": "server.items.<id>.name", "Description": "server.items.<id>.description"}` |
| `Quality` | by tier: I `QUAL_IDS[0]` (Common) .. V the Legendary quality - builder maps n -> the Gear quality ids it already uses (UNVERIFIED names) |
| `MaxStack` | the vanilla `Ingredient_Powder_Boom` MaxStack (read at build; UNVERIFIED value) |
| `Icon` | `Icons/ItemsGenerated/<id>.png` = `SA.recolor_icon(<Boom Powder icon>, <element ramp>)` made at build time from `Assets.zip` (nothing vanilla committed); one icon per element, the tier shows in the name. Cloud-drawn icons can replace them later (`skywynn-art` skill) |
| `Model` / `Texture` | the Boom Powder model BY PATH; texture `Items/SkyyGear/Powder/Powder_<E>.png` = `SA.recolor(<its texture>, <element ramp>)` |
| `IconProperties`, `Scale`, `ItemSoundSetId`, `PlayerAnimationsId` | copied from the Boom Powder JSON (as the Sigils copy the Rune Shard's) |
| `Tags` | `{"Type": ["Powder"]}` |
| `Recipe` | section 2.4 |

Build asserts (like the Sigils): no id is in `AZ_ITEMS`, no generated file shadows an `Assets.zip` name, the Boom Powder source paths exist.

### 2.3 Lang keys (50 keys, writer SkyyGear only)

Written into SkyyGear's `Server/Languages/en-US/server.lang` as `items.<id>.name` / `items.<id>.description` (SCRIPT: the file name is the
`server.` prefix, same as `SIG_LANG`). Values per tier n, element E, value table V (section 6 row `powder.value`, defaults section 4.3):

```
items.Skyy_Powder_Fire_3.name = Fire Powder III
items.Skyy_Powder_Fire_3.description = <color is="TAG">T3 Powder</color> - <color is="#ff6a3d">Fire</color> powder.
  Weapon socket: <color is="#7ee08a"><b>+3</b></color> <color is="#d6e4ee">Fire Damage</color>.
  Armor socket: <color is="#7ee08a"><b>+5</b></color> <color is="#d6e4ee">Fire Defence</color>.
  <color is="#ffcc00">Use: Crafting > Anvil > Powders.</color> <color is="#7f93a6">4 make the next tier at the Alchemy Bench.</color>
```
(one line in the file; shown wrapped here). Tier V drops the "4 make the next tier" phrase. `TAG` = the colour SkyyGear already uses for
tier tags in flavour text (UNVERIFIED constant name). The text is generated from `TT.described(...)`-style `TT.ladder_tag(n, "Powder") + TT.SEP + text`
so the tag is always the first phrase. The numbers in the lang text are the build-time defaults; the item TOOLTIP of a socketed weapon /
armor shows the live values (section 5), so a Server Setup change is never shown wrong where it matters. Run `python tools/ci/langdup.py
--jar SkyyGear/SkyyGear-<ver>.jar` - no other SET jar writes `Skyy_Powder_*` keys today.

### 2.4 Recipes (vanilla Alchemy Bench, in each item's `Recipe` block)

| Output | Input | Bench | `RequiredTierLevel` | TimeSeconds |
|---|---|---|---|---|
| 1 x `Skyy_Powder_<E>_1` | 2 x the element's base material (2.1) | `Alchemybench` | 1 | 2 |
| 1 x `Skyy_Powder_<E>_2` | 4 x `Skyy_Powder_<E>_1` | `Alchemybench` | 1 | 3 |
| 1 x `Skyy_Powder_<E>_3` | 4 x `Skyy_Powder_<E>_2` | `Alchemybench` | 2 | 4 |
| 1 x `Skyy_Powder_<E>_4` | 4 x `Skyy_Powder_<E>_3` | `Alchemybench` | 3 | 5 |
| 1 x `Skyy_Powder_<E>_5` | 4 x `Skyy_Powder_<E>_4` | `Alchemybench` | 4 | 6 |

25 recipes. The `BenchRequirement` shape (Type, Id, Categories) is copied at build time from a vanilla `Alchemybench` recipe in `Assets.zip`
(the way the Armory recipe copier reads `RECIPE_KEYS`, SCRIPT line ~4836); the category = the bench's ingredient / misc tab (UNVERIFIED
name). The bench draws inputs from the Magic Bags (Sacks pocket crafting, `research/Alchemy-Skill-Spec.md` 32). Value check: Powder I ~
225 coins of material, V ~ 57,600 (x4 per tier). Recipe counts are asset data (a rebuild changes them), like every bench recipe we ship (Q7).
Alchemy XP: none (the Alchemy XP table pays 0 for non-table recipes - SkyySkills unchanged).

### 2.5 Tier tags (`tools/tier_tags.py`)

Powders are an OWN ladder (like Totem / Loot / Bench / Talisman / Charm), so they are not ROWS of the metal table.

| Change | Exact edit |
|---|---|
| the table row to add | `OWN_LADDERS = ("Totem", "Loot", "Bench", "Talisman", "Charm", "Powder")      # powders P1: + Powder (SkyyGear <ver>, research/cloud/Powders-P1-Build.md)` |
| docstring API line | `ladder_tag(n, word) -> "T2 Totem" (own ladders: Totem, Loot, Bench, Talisman, Charm, Powder)` |
| `tools/test_tier_tags.py` | `ok(TT.ladder_tag(1, "Powder") == "T1 Powder" and TT.ladder_tag(5, "Powder") == "T5 Powder", "powders P1: the Powder ladder word")` |
| `TT_VERSION` | stays `"3"` (a new word renumbers nothing; old pins that assert "3" keep passing) |

Tag = `T<n> Powder` with n = the powder tier = its zone (I = Zone 1 ... V = Zone 5). The socketed ITEM's own tag never changes.

## 3. Sockets

### 3.1 Saved data (on the SkyyGear item doc, metadata key `"SkyyGear"`)

SCRIPT: the doc is a `BsonDocument` under `GearDefs.DOC_KEY = "SkyyGear"` with keys `mods`, `rf`, `rfN`, `lvl`, `lvl0`, `at`, `tr`...;
`reforge` / `levelUp` clone the doc and keep unknown fields. grep finds no `"pw"` / `"pwMax"` / `"pwAdd"` key in 0.3.40 - free.

| Key | Type | Meaning |
|---|---|---|
| `pw` | `BsonArray` of `BsonString` `"<Element>:<n>"` (e.g. `"Fire:3"`), index = socket order; `""` = an empty socket kept in place | the powders |
| `pwAdd` | `BsonInt32` 0..`powder.extraSockets` | sockets the player added (minus removed) |

**CHANGED** (draft had `pwMax`): the socket count is NOT stored. `sockets(item) = table[rarity][weapon|armor] + pwAdd` (row
`powder.sockets`), so a Sigil rarity upgrade or a Server Setup change applies at once with no data rewrite and no migration. If the count
falls below the number of filled entries (a table lowered), the extra powders stay saved, do not count, and show grey "(no socket)" on the
tooltip; raising the count brings them back. Nothing is ever deleted by a settings change.

Which items get sockets: identified items with `GearData.slotOf(id)` 0 / 1 (weapon) or 2 (armor) that are combat gear. Lifelong tools,
gathering armor (Mining / Foraging / Farming / Fishing sets), unidentified items and bags: 0 sockets (Q5). Untiered: the `untiered` row.

### 3.2 Socket table (defaults; row `powder.sockets`)

| Rarity key (SCRIPT `R_IDS`) | Weapon | Armor piece |
|---|---|---|
| `normal` | 1 | 0 |
| `unique` | 1 | 1 |
| `rare` | 2 | 1 |
| `legendary` | 2 | 2 |
| `fabled` | 3 | 2 |
| `mythic` | 3 | 3 |
| `set` | 1 | 1 |
| `untiered` | 2 | 1 |

`set` and `untiered` rows are new vs the draft (SCRIPT: Gear has 8 rarities incl. `set`); per-UT-line overrides wait for the UT batch.

## 4. Stats: where powders join (no double count)

### 4.1 One entry point

SCRIPT: `GearStats.totals0(u, weapon, armor, ok, withExtra)` adds each ACTIVE item's rolled lines through `addModsE(acc, id, d, armor)`
(value through `GearView.effVal` = value x slot power) and Untiered lines through `addUtE`. Both the pet gate (`totals(..., false)` = rolled
only) and the armour pass behind `gear:fn:elemDef` (`GearElem.note`, DEF from `t[DI[e]]`) read this sum.

New method `addPowE(acc, id, d, armor)` called right after `addModsE` in BOTH the weapon branch and the armor loop of `totals0`, inside the
same `active(u, id, d)` gate:
- weapon (armor = false): each counted powder adds `effVal(id, d, "f<E>", V[n].weapon)` to `acc[sIndex("f<E>")]`;
- armor (armor = true): each counted powder adds `effVal(id, d, "d<E>", V[n].armor)` to `acc[sIndex("d<E>")]`;
- `part.powders` off -> returns at once (adds nothing); counted = the first `sockets(item)` entries of `pw` that parse.

So a powder behaves EXACTLY like a rolled line of that key: same slot power, same `S/(S+D)` Defence curve, same pet gate (a weapon
powder makes `W_e > 0`), same mob Weak / Resist, same popups. Imbue (`I_e`, % of N) is untouched; charms and pets are untouched. Nothing
else reads powders. `GearSnap` caches `totals0` per weapon / armor: the builder confirms a metadata change on a worn piece or the held
weapon gives a new snapshot (UNVERIFIED; harness H6).

### 4.2 Element words

`pw` stores `Earth`, `Thunder`, `Water`, `Fire`, `Air` (the `f<E>` / `d<E>` key suffixes, SCRIPT `elemCol`). Unknown words or tiers outside
1..5 are skipped, never thrown.

### 4.3 Values (defaults; row `powder.value`; placeholders for the balance model)

| Tier (key) | Weapon (flat element damage, like `fX`) | Armor (flat element Defence, like `dX`) |
|---|---|---|
| 1 | 1 | 2 |
| 2 | 2 | 3 |
| 3 | 3 | 5 |
| 4 | 4 | 7 |
| 5 | 5 | 9 |

Bound: rolled `fX` max 6, `dX` max 10 (`research/balance/gear.md` 36, 59), so one powder never beats one top rolled line (draft rule).
Worst case per weapon: 3 + 1 sockets x 5 = +20 of one element; per 4-piece set 4 x 4 x 9 = 144 Defence of one element (S = 100 -> ~59% cut
of that element only). FLAG for P0: the balance model checks both and the gear-upgrade clock (`docs/answered/gear.md` 313).

## 5. Tooltip (SkyyGear item view)

Under the rolled lines, one group (Style Guide 15 order: gives first, minor info last):
```
Powders  [Fire III] [Fire III] [ empty ]          <- pips: element colour for a filled socket, dim grey #7f93a6 for empty
  +6 Fire Damage                                   <- one line per element: value green #7ee08a bold, name #d6e4ee (live values, x slot power)
  (1 powder with no socket)                        <- grey, only when the table was lowered
```
Weapons say Damage, armor says Defence. An item with 0 sockets shows no group (identical tooltip to 0.3.40). The view signature that decides
when the tooltip is rewritten must include `pw` and `pwAdd` (SCRIPT note at line ~1635: "The sig hashes every line"; harness H9).

## 6. Server Setup rows (SkyyGear; `tools/CONFIG-CONTRACT.md`, kit rows `Object[11]`)

SCRIPT: Gear's `CFG_CATS` already has 16 categories (the contract maximum), so the rows go into the existing `smithing` and `combat`
categories - no new category. No time or distance rows in P1 (nothing is timed; no blocks).

| Key | Label (<= 40) | Cat | Type | Default | Min / Max | Opts | Unit | Flags | Binding |
|---|---|---|---|---|---|---|---|---|---|
| `part.powders` | Powders | smithing | bool | `true` | - | - | - | `live,part,danger` | `field:GearCfg.PW_ON` (off: powders count 0, the Powders sub-tab says "Powders are switched off", items and data kept) |
| `powder.sockets` | Powder sockets by rarity | smithing | table | `""` (entries 3.2) | 0 / 3 | `int;none;Weapon|Armor` | - | `live,danger` | `reload@<CFG_FILE>:powder.sockets.;check=GearCfg.checkRarityKey` |
| `powder.extraSockets` | Extra sockets a player may add | smithing | int | `1` | 0 / 3 | - | - | `live` | `field:GearCfg.PW_EXTRA` |
| `powder.socketCost` | Add-socket cost by rarity | smithing | table | entries = 2 x `BM.P7_GEAR_BASE["reforge"][r]` (Lv-10 reforge base) | 0 / 1000000000000 | `int;none;Coins` | coins | `live,danger` | `reload@<CFG_FILE>:powder.socketCost.;check=GearCfg.checkRarityKey` |
| `powder.socketLevel` | Smithing level to add a socket | smithing | int | `10` | 0 / 100 | - | - | `live` | `field:GearCfg.PW_SOCKLV` |
| `powder.value` | Powder value by tier | combat | table | entries 4.3 (keys `1`..`5`) | 0 / 1000 | `int;none;Weapon|Armor` | - | `live,danger` | `reload@<CFG_FILE>:powder.value.;check=GearCfg.checkPowderTier` |
| `powder.xp` | Smithing XP per powder added | smithing | table | `1`=5 `2`=10 `3`=20 `4`=40 `5`=80 | 0 / 100000 | `int;none;XP` | - | `live,danger` | `reload@<CFG_FILE>:powder.xp.;check=GearCfg.checkPowderTier` |
| `powder.removeRefund` | Chance a removed powder returns | smithing | int | `0` | 0 / 100 | - | `%` | `live` | `field:GearCfg.PW_REFUND` |

Help texts (<= 100 chars), e.g. `powder.sockets`: "Sockets per item by rarity (Weapon / Armor piece). Lowering keeps powders saved." `GearCfg.checkPowderTier`
= new hook, accepts entry keys `1`..`5` only. XP sizes follow `xp.reforge` (SCRIPT `XP_R_DEF` 5 .. 160). Rows join `CFG_ROWS` and the
default text `DEFAULT_TEXT`; no migration (all new keys, a missing line = the default).

## 7. The Anvil Powders sub-tab (SkyyGear page, `research/Menu-Pattern.md`)

SCRIPT: the Anvil's one sub-row is "Reforge | Identify (kit small buttons, the active one Primary; mode:0 / mode:5 = the Anvil's own in-place
switch)", modes 0..6 are used, `mode:7` is free. Add **Powders** as the third button = `mode:7`. No new command, no new page; `/smithing` /
`/reforge` open the Anvil as today; Powders is one click on the sub row.

| Area | Content |
|---|---|
| frame | the kit 1.7 hub page (1600 x 980, rows 1 + 2, Crafting tab lit, Anvil lit), content group 1066 wide (as the Anvil today) |
| left | the Anvil item list (same scroll list and rows 46 / 66 / 92 as Reforge), filtered to items with `sockets(item) > 0`, sorted by tier then name |
| right top | held / picked item: name in rarity colour, level, the socket row: up to 6 squares 64 px, filled = `ItemGridSlot` with `new ItemStack("Skyy_Powder_<E>_<n>", 1)` (no metadata - HANDOFF UI rule), empty = frame; click a socket = select it |
| right middle | scroll list of the powders you have (inventory + Magic Bags via `sacks:fn:all`), sorted tier then Wynn element order (Earth, Thunder, Water, Fire, Air); each row: icon, name, "x12", what it gives on THIS item ("+3 Fire Damage") |
| buttons | ADD (into the selected socket, or the first empty one), REMOVE (confirm), ADD SOCKET (cost + Smithing level shown green / red), REMOVE SOCKET (only an empty last socket the player added; no refund) |
| footer | the result line `#SkyyGInfo` (e.g. "Fire Powder III added - +3 Fire Damage. +20 Smithing XP.") |

One packet per click (`TextButton` + `EventData`, ids without underscores, e.g. `pwAdd`, `pwRem`, `pwSock`, `pwUnsock`, `pwPick3`), no periodic
updates, the page re-reads the item at click time.

### 7.1 Click rules (anti-dupe / anti-loss; all on the world thread, one task per click)

| Action | Order |
|---|---|
| ADD | 1 re-read the item at its slot, check the fingerprint (Reforge / Identify "same slot + fingerprint", SCRIPT) - else refuse, nothing changes. 2 a filled target socket asks "Replace Fire Powder II? It will be destroyed." (confirm). 3 take ONE powder: inventory first (count before / after), else `sacks:fn:take {u, id, 1}`. 4 write the new doc (`pw` updated) to the same slot; for a stack of gear split ONE item off exactly like Reforge (never into the hotbar). 5 re-read: on any mismatch give the powder back (inventory give, or `sacks:fn:put` within its 60 s window) and refuse. 6 on success `sacks:fn:commit` (bag take), Smithing XP `skill:fn:addxp {u, "Smithing", Long xp, "powder:<powderId>"}` (row `powder.xp`), replaced powder handled like REMOVE |
| REMOVE | confirm "Remove Fire Powder III? It will be destroyed." (with refund > 0: "...returns with a N% chance"); write the doc (entry -> `""`); then roll the refund and give the powder storage-first; no XP |
| ADD SOCKET | checks: `pwAdd < powder.extraSockets`, `skill:fn:level` Smithing >= `powder.socketLevel`, coins >= cost. Order: `coins:fn:take` FIRST, write `pwAdd + 1`, re-read; on failure `coins:fn:add` the same amount back |
| REMOVE SOCKET | only when `pwAdd > 0` and the last socket is empty; write `pwAdd - 1`; no coins back |

Reforge, Level up, Upgrade, Sigils: keep `pw` and `pwAdd` (they clone the doc, SCRIPT) - verified by harness H8. Trade / AH / Vault / Requip
carry the whole metadata (UNVERIFIED, test steps 12-13).

## 8. SkyySacks change (Combat bag accepts powders)

SCRIPT: `homeOf(itemId)` in `SkyySacks/build_skyysacks_0.8.28.py` (~line 2365) returns `"Combat"` for `Ingredient_Bone*`, essences,
`Ingredient_Powder_Boom` ... and `null` for anything else - a `Skyy_Powder_*` would fit no bag today. One line before the Combat test:
`if (itemId.startsWith("Skyy_Powder_")) return "Combat";` - nothing else changes (catOf, pools, bridges unchanged).

## 9. Builder split (one mod per builder, Full round)

Round size: **Full round** (new saved item fields, item loss / dupe risk, damage sums, two mods, new items). Launch with the saved workflow
`.claude/workflows/skywynn-round.js` (args `quotes` = the Q10 popup line of section 0 + Skyy's GEMS line; `mods` SkyyGear, SkyySacks).
Versions = the next free version at build time (live pins `tools/deploy_set.py`: SkyyGear 0.3.40, SkyySacks 0.8.28).

| Builder | Model | Mod | Files it may edit | Content |
|---|---|---|---|---|
| A | Opus | SkyyGear 0.3.40 -> 0.3.41 | `tools/gear_0_3_41_patch.py` (new; reads the generated `SkyyGear/build_skyygear_0.3.40.py`), generated `SkyyGear/build_skyygear_0.3.41.py`, `SkyyGear/test_skyygear_0.3.41.py`, `tools/tier_tags.py` (the one OWN_LADDERS row + docstring), `tools/test_tier_tags.py` (one check) | sections 2, 3, 4, 5, 6, 7 |
| B | Opus | SkyySacks 0.8.28 -> 0.8.29 | `tools/sacks_0_8_29_patch.py` (new), generated `SkyySacks/build_skyysacks_0.8.29.py`, `SkyySacks/test_skyysacks_0.8.29.py` | section 8 |

Then: Sonnet review (both), fix, `python tools/ci/crosscheck.py --jar SkyyGear/SkyyGear-0.3.41.jar --jar SkyySacks/SkyySacks-0.8.29.jar --baseline`,
`python tools/ci/lint.py` (0 fails), `python tools/ci/langdup.py`, `python tools/test_tier_tags.py`, `python tools/smoke_test.py` (game
closed) - every `[SkyyGear] 0.3.41 ready` / `[SkyySacks] 0.8.29 ready` line, no asset-validation failure (25 new items + recipes), no SEVERE.

## 10. Harness checks

| # | Mod | Check |
|---|---|---|
| H1 | Gear | IDENTITY: for a fixture of weapons + armor with no `pw`, `totals0` / `totals(..., false)` / `GearElem.note` DEF are bit-identical to 0.3.40's methods |
| H2 | Gear | one `"Fire:3"` on a weapon adds exactly `effVal(id, d, "fFire", 3)` to `fFire` once, in `withExtra` false AND true; never to `dFire` |
| H3 | Gear | one `"Fire:3"` on an armor piece adds `effVal(.., "dFire", 5)` to `dFire` only; never to `fFire`; four pieces add four times |
| H4 | Gear | an inactive item (`active()` false: level / class lock) adds nothing; `part.powders` false adds nothing |
| H5 | Gear | `sockets()` = table + `pwAdd`; rarity change (Sigil fixture) raises it; lowering the table leaves `pw` untouched and counts only the first N |
| H6 | Gear | `GearSnap`: a changed `pw` on the held weapon / a worn piece gives a new snapshot (no stale sum) |
| H7 | Gear | bad `pw` entries (`"Foo:3"`, `"Fire:9"`, `""`, a non-string, a non-array `pw`, negative `pwAdd`) are skipped, never throw |
| H8 | Gear | `reforge`, `levelUp`, the Sigil upgrade and Upgrade keep `pw` + `pwAdd` byte-equal |
| H9 | Gear | tooltip: no group when sockets = 0 (text identical to 0.3.40); pips + per-element lines with `elemCol` hex; the view signature changes when `pw` changes |
| H10 | Gear | 25 item JSONs, 50 lang keys; every description starts with `TT.ladder_tag(n, "Powder") + TT.SEP`; no id in `AZ_ITEMS`; no file shadows Assets.zip |
| H11 | Gear | 25 recipes: inputs exist in Assets.zip, tier-up input = the same element one tier down, outputs 1, bench `Alchemybench` |
| H12 | Gear | kit build checks pass (labels, help <= 100, tables, hooks exist); still 16 categories; `checkPowderTier` refuses `0`, `6`, `x` |
| H13 | Gear | click handlers on fakes: fingerprint mismatch -> no take, no write; write failure -> powder back (inventory and `sacks:fn:put` paths), coins back on ADD SOCKET failure; ADD never leaves both the powder in the bag and in the socket |
| H14 | Gear | the Powders sub-tab markup: `mode:7`, ids without underscores, `ItemGridSlot` stacks built with `new ItemStack(id, 1)` only, sorted tier then Earth / Thunder / Water / Fire / Air |
| H15 | Sacks | `homeOf("Skyy_Powder_Fire_3") == "Combat"`, every other id's answer unchanged vs 0.8.28 (table of sample ids) |
| H16 | both | build ends "assembled ...jar"; lint 0 fails; langdup no FAIL; `tools/test_tier_tags.py` OK |

## 11. Rollback / FLOOR notes (line for `tools/deploy_set.py`, written by the main session)

- Gear 0.3.41 + Sacks 0.8.29 pin and deploy TOGETHER (Gear's page reads bag stock; Sacks' rule only matters with the items).
- FLOOR: never roll SkyyGear below 0.3.41 once any `Skyy_Powder_*` item exists (unknown item ids in 0.3.40). Before a rollback: switch
  `part.powders` off is NOT enough - players must sell / drop powders, or keep 0.3.41. Socketed gear itself is item-safe: 0.3.40 keeps the
  unknown `pw` / `pwAdd` fields (clone rule) and simply ignores them; rolling forward again brings them back.
- SkyySacks 0.8.29 -> 0.8.28: withdraw powders from the Combat bag first (0.8.28 maps them to no bag; behaviour of a stored id with no home
  is UNVERIFIED).
- Existing floors stay: elem1 (Gear 0.3.39+ set), packprep (Gear 0.3.38 + Sacks 0.8.28 + Coins 0.1.11 + Mobs 0.1.16), P7 economy (Gear 0.3.37+).
  P1 adds no saved-data migration and no settings rewrite.

## 12. In-game test steps (Skyy)

1. Server Setup -> Gear -> Smithing: "Powders" is ON; "Powder sockets by rarity" shows the 8 rarity rows of section 3.2.
2. `/give <you> Ingredient_Fire_Essence 16` and `/give <you> Ingredient_Crystal_Cyan 8`; open an Alchemy Bench: Fire Powder I (2 Fire
   essence) and Air Powder I (2 Cyan Crystal Shards) are listed; craft 8 Fire Powder I and 1 Air Powder I.
3. Hover Fire Powder I: the first words are "T1 Powder", Fire in orange, the weapon and armor values in green.
4. Craft 2 Fire Powder II (4 + 4 Fire Powder I); hover: "T2 Powder".
5. Put a few powders in your Combat Magic Bag: they go into the Combat tab.
6. Hold a Rare weapon, `/smithing` -> Anvil -> **Powders**: the weapon shows 2 empty sockets; the list shows your powders (from the bag
   too), sorted by tier then element.
7. ADD Fire Powder II: the socket fills, chat / footer shows "+2 Fire Damage" and Smithing XP; the weapon tooltip shows
   `Powders [Fire II] [ empty ]` and "+2 Fire Damage".
8. Hit a mob: the orange Fire number appears on hits (it did not before if the weapon had no Fire line). With a Fire pet out, the pet's Fire
   line now works too.
9. Put Fire Powder I into a worn armor piece (Unique or better): Stats page shows Fire Defence up by 2 within a second.
10. REMOVE a powder: confirm text says it will be destroyed; after, the socket is empty and the powder is gone.
11. ADD SOCKET on the weapon: cost and Smithing 10 shown; pay; 3 sockets now; a second ADD SOCKET is refused (max 1 extra); REMOVE SOCKET
    on the empty added socket works.
12. Reforge the socketed weapon, then Level it up: the powders stay.
13. Move the socketed weapon through the Vault and a trade / AH listing with an alt or a friend: the powders stay.
14. Use a Sigil on a Unique armor piece -> Legendary: it now has 2 sockets, the filled one kept.
15. Server Setup: set rare Weapon sockets to 1: the weapon shows one powder grey "(no socket)" and it stops counting; set it back: it counts again.
16. Switch "Powders" OFF: hits lose the powder Fire, the Powders tab says switched off; switch it ON: all back.
17. A Normal armor piece and a Mining set piece do not appear in the Powders list (0 sockets).

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | One shared socket pool for powders AND the later Gems (`research/Gems-Ideas.md`)? | [shared pool] |
| 2 | Powder tiers I-V (one per zone), not Wynn's six? | [5 tiers; VI waits for Zone 6] |
| 3 | Removing (or replacing) a powder destroys it, like Wynncraft? | [destroys; "Chance a removed powder returns" row can change it] |
| 4 | A powder on a weapon opens a pet's element (pet Fire works once the weapon deals Fire)? | [yes] |
| 5 | Gathering armor (Mining / Foraging / Farming / Fishing sets) and lifelong tools get no powder sockets? | [none - powders are combat gear only] |
| 6 | Your gem line says slots can be "added and removed": allow removing an EMPTY added socket (no coins back)? | [yes] |
| 7 | Recipes at the vanilla Alchemy Bench: 2 essence / crystal -> 1 Powder I, 4 of a tier -> 1 of the next? | [yes; Air uses Cyan Crystal Shards, Earth Green Crystal Shards] |
| 8 | No extra cap on total flat element in v1 (the socket count x powder value is the limit)? | [no cap in v1] |
| 9 | Socket counts by rarity as in section 3.2 (Normal weapon 1 / armor 0 ... Mythic 3 / 3)? | [yes] |
| 10 | Should crafting powders at the Alchemy Bench also give Alchemy XP? | [no in P1; Smithing XP when you socket them] |

## For the local session (every UNVERIFIED item)

| # | Item | How to check |
|---|---|---|
| 1 | P0 not done: CurseForge survey for Hytale gem / socket / enchant / powder mods (`PROJECT-RULES.md` section 2) | survey before the round (Jev via `tools/llm.py`) |
| 2 | P0 balance: `powder.value` defaults, `powder.socketCost` (2 x Lv-10 reforge base), socket counts, the gear-upgrade clock re-run | `tools/balance_model.py` rows; `research/balance/targets.md` |
| 3 | `Ingredient_Fire_Essence`, `Ingredient_Water_Essence`, `Ingredient_Lightning_Essence`, `Ingredient_Crystal_Green`, `Ingredient_Crystal_Cyan` exist in Assets.zip | build asserts (they are live Bazaar rows, so very likely) |
| 4 | `Ingredient_Powder_Boom` item JSON path, Model, Texture, Icon, MaxStack, IconProperties, sound set (the icon / texture recolour source) | `Assets.zip` `Server/Item/Items/**/Ingredient_Powder_Boom.json` |
| 5 | A vanilla `Alchemybench` recipe's `BenchRequirement` shape, its category name, and the bench's highest `RequiredTierLevel` (4 assumed) | `Server/Item/Items/Bench/Bench_Alchemy.json` + a potion JSON |
| 6 | The Alchemy Bench pocket crafting draws crystals from the Mining bag and essences / lower powders from the Combat bag | in game, step 2 / 4 |
| 7 | `GearSnap` gives a fresh snapshot when the held weapon's or a worn piece's metadata changes | harness H6 against the 0.3.40 code |
| 8 | Does the Anvil item list include worn armor and hotbar items; the exact Reforge "split one off a stack" helper name | `SkyyGear/build_skyygear_0.3.40.py` (Anvil list, `GearIdent` write safety) |
| 9 | The colour constant Gear uses for the tier tag in flavour text; the Gear quality ids per powder tier (`QUAL_IDS`) | same script |
| 10 | Trade, AH, Vault, Requip, Wardrobe keep the whole item metadata (`pw`, `pwAdd`) | test steps 12-13 |
| 11 | SkyySacks 0.8.28 behaviour for a stored id whose `homeOf` is null (rollback note) | `SkyySacks/build_skyysacks_0.8.28.py` pool code |
| 12 | `mode:7` is free in every Gear page handler (grep shows modes 0-6 in 0.3.40), and 16 categories is the real kit maximum for `CFG_CATS` | grep + `tools/skyycfg.py` build check |
| 13 | `sacks:fn:put` 60 s refund window covers the ADD rollback path in one world task | `SkyySacks/build_skyysacks_0.8.28.py` header (SCRIPT says 60 s) |
| 14 | After P1: queue P2 (Mobs / loot drops + Merchants + Bazaar products + salvage / sale confirms) in `RESUME.md` "Next" | main session |
