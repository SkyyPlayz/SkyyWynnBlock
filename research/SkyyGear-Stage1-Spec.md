# SkyyGear 0.1 (stage 1: combat weapons + armor): build spec

*Written 2026-09-25 from Skyy's answers of the same day (SkyWynn-Decisions.md "Change notes (2026-09-25)" #5 and #6, HANDOFF
BUILDER / STATUS block), SkyyGear-Plan.md locks 1-126 plus the tooltip note, SkyyGear-Stat-Catalog.md (Keep rows), and the live
build scripts (SkyyRolls 0.1.5, SkyyClasses 0.1.6, SkyySkills 0.4.5, SkyyAccessories 0.4.4, SkyyExploration 0.2.1, SkyySacks 0.7.6,
SkyyAuctions 0.1.1, SkyyMenu 0.3.2). Engine facts were checked read-only against `HytaleServer.jar` bytecode and `Assets.zip` JSON on
this machine (tools/dev helpers, scratch under `tools/dev/scratch/gear-spec/`, deleted afterwards). Nothing here is built yet.
The design docs (SkyyGear-Plan.md, SkyyGear-Stat-Catalog.md) were only read.*

*Revised 2026-09-28: the 13 review findings of 2026-09-25 were checked against the live scripts, the server jar and Assets.zip and
applied (section 13 "Review notes" lists each verdict and what was rejected). Also added: Skyy's gate-skill-per-gear-type rule
(Decisions change note 2026-09-25 #6, HANDOFF "GEAR LEVEL CAP BY GEAR TYPE"), Skyy's Auction House locks (OPEN-QUESTIONS Auction
House 2, 4 and 15), the Player Settings locks (Settings icon at slot 39, permission-based visibility), the Server Setup lock "10 old
file versions", and the vanilla-look rule for every page (Decisions change note 2026-09-25 #9, HANDOFF section 2 rule 0). Engine
checks of this revision used scratch `tools/dev/scratch/ra-gearspec/` (deleted afterwards).*

**Legend.** LOCKED = Skyy's decision (source named). VERIFIED = seen in bytecode, Assets.zip or a live Skyy script. INFERRED = strongly
implied, not proven; the test plan (section 11) proves it. **PLACEHOLDER** = a number or formula Skyy has NOT picked. Every placeholder
is a Server Setup row (section 9), so Skyy tunes it in game without a rebuild. No placeholder is a design lock.

---

## 0. Plain words (for Skyy)

- **SkyyGear 0.1 replaces SkyyRolls.** Same `/reforge` command and the same Reforge tile in the SkyWynn Menu. SkyyRolls is switched off
  in the same deploy. Items SkyyRolls already rolled keep their rolls. They are moved onto the new system the first time their owner
  logs in.
- **Every weapon and armor piece now has a rarity and a level.** Rarities are Wynn's: Normal (white), Unique (yellow), Rare (pink),
  Legendary (aqua), Fabled (red), Mythic (purple), plus Set (green). The item's frame in the inventory takes the rarity colour.
  Hytale supports a per-item quality (VERIFIED), so SkyyGear ships 7 quality styles of its own.
- **Every gear piece has a gate skill, and its level checks that skill** (your rule of 2026-09-25):
  - **combat** gear (weapons and armor) -> your class weapon skill: Archer = Archery, Warrior = Swordsmanship, Mage = Sorcery,
    Berserker = Fury, Priest = Divinity;
  - **mining** gear -> Mining; **foraging** gear -> Foraging; **farming** gear -> Farming (fishing and the rest later).
  - 0.1 builds **combat gear only**, but the item data and the level check are already generic, so gathering gear only adds items.
  - A weapon above your level deals no damage, and a popup says why. SkyyClasses' weapon lock works the same way. Hytale lets nobody
    cancel a swing itself, so "blocked" means the hit does nothing. Both hands count: a weapon in the off-hand (utility) slot is
    checked too.
  - Armor above your level still goes on, but gives **no stats at all**. That includes Hytale's own health and protection on the
    piece (section 3.5). **Your call (Q18):** should "no stats" also switch off Hytale's own health and protection, or only
    SkyyGear's modifiers? The default is "everything".
- **Gear you already own stays Normal with no modifiers** until you reforge it. **Crafted** gear rolls its rarity and modifiers when
  you craft it. Your Smithing level raises the chance of a higher rarity.
- **Items SkyyRolls already rolled keep their rolls.** Their new rarity comes from how strong those rolls are (section 1.6).
- **Modifier strength grows with the item's level** (placeholder, Q19): a level-0 Crude sword rolls weaker lines than a level-50
  Mithril sword of the same rarity. So mass-crafting the cheapest recipe cannot farm top-power gear.
- **Weapons and armor from mobs and world loot chests drop unidentified.** Their rarity is already set and visible. An unidentified
  weapon cannot hurt anything, and unidentified armor gives nothing. `/identify` opens a page where you pay coins to reveal the
  modifiers. The cost grows with rarity and level.
- **The live stats in 0.1:**
  - Damage %, Strength, Magical Power (spells), Crit Chance, Crit Damage and Overcrit.
  - Flat Earth, Thunder, Water, Fire and Air damage, and True Damage.
  - Raw Thunder Damage, Raw Water Damage and Raw Elemental Damage (added once per element).
  - Defense, Speed, Health Regen, Health Regen %, Stamina Regen, Life Steal and Mana Steal.
  - Attack Speed, Ferocity, Thorns, Poison, Exploding, Knockback, Slow, Weaken, elemental defences and Combat Wisdom are shown on
    items with "(coming later)". They never silently do nothing.
- **Your numbers are still open**, so every number in this spec is a clearly marked **placeholder** you can change in SkyWynn Menu ->
  Server Setup -> Gear:
  - how many modifiers each rarity gets, and how strong they roll (also by item level);
  - drop and craft odds, and the Smithing bonus;
  - level per material;
  - identify and reforge costs;
  - how old SkyyRolls items get their rarity.
- **Pages look like vanilla Hytale.** The Reforge and Identify pages copy the game's own item-repair page and its shared styles
  (frame, title bar, buttons, list rows, colours, sounds). The only colours of our own are your 7 rarity colours.
- **Other mods this round (section 7.3):**
  - SkyyAuctions 0.1.2: gear names, rarity and modifier lines come from SkyyGear, plus your AH locks: a 48h listing pays double
    the listing fee (instead of a flat 1,200), another of your profiles may buy your listing (the same profile may not), and
    Magic Bags and the Accessory Bag cannot be listed or bought.
  - SkyyMenu 0.3.3: an Identify tile, new Reforge text, SkyyGear replaces SkyyRolls in the Mods list, the Settings icon moves next
    to Mods (slot 39), and players only see the settings they are allowed to change.
  - SkyySacks: gear crafted in `/craft` rolls too (a small hook; SkyySacks 0.7.7 is being built at the same time for the bag
    rarities).
  - Optional, SkyyExploration 0.2.2: the Exploration chest-luck bonus item drops unidentified too.
  - Everything else keeps working unchanged (section 7.4).
- **Not in 0.1:** gathering gear and tools, the Equipment bar, loadouts, set bonuses, powders, Accessory Power, and an identify NPC.
  The item data already has room for them (section 1.4).

---

## 1. Data model

### 1.1 What an item carries (all in `ItemStack` metadata + the stack's own quality)

| Where | What | Notes |
|---|---|---|
| metadata key `"SkyyGear"` (BsonDocument) | the gear document (1.2) | the only source of truth for rarity, identify state and modifiers |
| metadata key `"SkyyGearView"` (BsonDocument) | `{ v:int, sig:string, prev:BsonValue? }` | tooltip marker, same idea as SkyyRolls' `SkyyRollsView`: `v` = VIEW_V, `sig` = fingerprint of everything the tooltip shows, `prev` = the ItemDisplayMetadata that existed before SkyyGear wrote its own |
| engine key `ItemDisplayMetadata` (`IDM.KEYED_CODEC`) | Name + Description the client shows | written by SkyyGear (section 6). Trade, AH and vanilla all read it |
| stack quality index (`ItemStack.withQuality(int)`) | the rarity's quality asset `Skyy_Gear_<Rarity>` | VERIFIED: `ItemStack.qualityIndex` is a per-stack field. `Integer.MIN_VALUE` means "use the item's own quality". It is saved by `ItemStack.CODEC` (key `Quality`) and sent to the client in `toPacket()` (`ItemWithAllMetadata.quality`) |

Every write returns a new stack (`withMetadata` / `withQuality` are immutable). The new stack goes back into the **same slot** with
`ItemContainer.setItemStackForSlot`, on the world thread, and only after the slot was re-read and is still the same item (1.7).

### 1.2 The `SkyyGear` document (schema v1)

```json
{ "v": 1, "kind": "combat", "r": "rare", "id": true,
  "mods": [ { "s": "str", "v": 12 }, { "s": "cc", "v": 5 }, { "s": "fFire", "v": 6 } ],
  "rf": "Sharp", "rfN": 2, "src": "craft", "at": 1790000000000,
  "lvl": null, "gate": "class", "set": null }
```

| Field | Type | Meaning | 0.1 writes it? |
|---|---|---|---|
| `v` | int | schema version (1). A reader that sees a higher `v` shows the item read-only and never rewrites it | always |
| `kind` | string | gear type: `combat` for every stage-1 item; `mining`, `foraging`, `farming` and `tool` (a tool with no gathering skill yet) - 0.1 writes these four only on tools migrated from SkyyRolls (1.6); later `fishing` and other gathering types, `equipment`, `accessory`. It picks the modifier pool and the default gate skill (3.3) | always |
| `r` | string | rarity id: `normal`, `unique`, `rare`, `legendary`, `fabled`, `mythic`, `set` | always |
| `id` | bool | identified. `false` = unidentified: `mods` is empty and is rolled at identify time (5.7) | always |
| `mods` | array of `{s, v}` | modifiers in display order. `s` = stat key (section 4), `v` = int value (percent stats in whole %). Unknown keys are kept and shown by name. A future per-modifier field (`src:"powder"`, `lock:true`) fits inside each entry | always (may be empty) |
| `rf` | string | cosmetic reforge name, shown as a name prefix. Absent = none | on reforge / migration |
| `rfN` | int | how many times it was reforged (anti-exploit log, later Smithing hooks) | on reforge |
| `src` | string | where the data came from: `craft`, `drop` (mob), `chest`, `legacy` (owned before SkyyGear), `rolls` (migrated from SkyyRolls), `admin` | always |
| `at` | long | millis of the last roll, identify or stamp | always |
| `lvl` | int or absent | **explicit** level override (custom items, set items later). Absent = the level table decides at read time (3.1), so tuning the table updates every item | never in 0.1 (admin `/gear level` only) |
| `gate` | string | the piece's **gate skill** (LOCKED: every gear piece carries one, Decisions change note 2026-09-25 #6). `class` = the owner's class weapon skill (combat gear); otherwise a SkyySkills skill name: `Mining`, `Foraging`, `Farming`, later `Fishing` and others. Written from the kind table in 3.3 when the document is created; `/gear gate <skill or class>` (admin) sets a custom one | always: `class` on combat gear, the gathering skill on migrated tools |
| `set` | string or null | set id placeholder. Set bonuses are a later stage | never (null) |
| `old` | document | the original SkyyRolls document, kept for a manual rollback tool (1.6) | migration only |
| `idAt`, `idBy` | long, string | identify time + identifier uuid (log/anti-exploit) | on identify |

**Reserved names (never used for anything else):** `pw` (powder list), `pwMax` (powder slots), `eq` (Equipment slot id), `load`
(loadout tag), `ap` (Accessory Power), `tune`. Stage 1 does not write them.

**Reading rules (every reader: SkyyGear, the bridge, other mods through the bridge):**
1. No `SkyyGear` key and no `SkyyRolls` key -> **Normal, identified, no modifiers, level from the table, gate from the kind table**
   (LOCKED: gear players already own stays the lowest rarity with no modifiers).
   A document without `gate` (hand edits, a future writer) takes the kind table's gate; a document without `kind` counts as `combat`.
2. A `SkyyRolls` key but no `SkyyGear` key -> the migration (1.6) is applied in memory for display. The real rewrite happens in the
   owner's inventory.
3. Unknown fields and unknown stat keys are preserved on every rewrite. SkyyGear edits the document in place (clone, change, put back),
   never rebuilding it from scratch.
4. A document that fails to parse is left untouched. It is shown as "Gear data unreadable" and logged once per item fingerprint.

### 1.3 What counts as gear in 0.1

- **Weapons:** every `Weapon_*` id except:
  - ammo: the SkyyRolls `AMMO` token list (arrow, bolt, bomb, dart, grenade, ...);
  - `Weapon_Shield_*`;
  - SkyyClasses' UNASSIGNED families: bombs, grenades, guns, flamethrower, deployables, darts, claws, blowgun, minigame guns.
  The list is config row `gear.exclude` (prefixes). Modded weapons are included automatically, including More Crossbow Tiers'
  `Weapon_Crossbow_Thorium/Cobalt/Adamantite/Mithril` (VERIFIED in the installed mod).
- **Armor:** every `Armor_*` id.
- **Never:** `Skyy_*` ids, `Tool_*` (gathering gear is later; only tools SkyyRolls already rolled keep a document, 1.6), and anything
  else.
- A modifier pool is chosen by slot: "weapon" = a gear `Weapon_*`, "armor" = a gear `Armor_*`. **Spell weapons** = `Weapon_Staff_*`,
  `Weapon_Wand_*` and `Weapon_Spellbook_*`. That is SkyyClasses' prefix idea: the engine has no damage-type flag (VERIFIED, research
  2026-09-25).
- **Off-hand (utility slot):** VERIFIED in Assets.zip, the only `Weapon_*` items with `"Utility": { "Usable": true }` are the shields
  (`Template_Weapon_Shield`, not gear) and `Weapon_Kunai` (gear). Every other weapon only says `Compatible` (it may be held next to a
  utility item). So a gear Kunai can deal damage from the utility slot; 3.4 checks that slot too.

### 1.4 How later stages fit (nothing below is built)

| Later stage | How it fits the document |
|---|---|
| Equipment bar (necklace, cloak, ring, belt) | new item ids with `kind:"equipment"` and the reserved `eq` slot. Same rarity, level and `mods`. The pool table gets an "equipment" slot (Earth Damage % and the other Equipment-only rows go there). The gate stays `class` |
| Sets + set bonuses | `r:"set"` + `set:"<setId>"`. A bonus system counts worn pieces with the same `set`. Drop-only and craft-only sets are a per-set flag in a later set table, not on the item |
| Powders | `pw:[...]` + `pwMax`, each powder a flat element line applied like `fFire` (section 4) |
| Gathering gear and tools | `kind:"mining"` + `gate:"Mining"`, `kind:"foraging"` + `gate:"Foraging"`, `kind:"farming"` + `gate:"Farming"` (the kind table in 3.3). The level check in 3.3 is already generic: `level(owner, gate) >= requirement`. Gathering gear only adds its items, its pools and its enforcement hooks (block break, harvest) |
| Loadouts / wardrobe | loadouts save item stacks. The document travels with the stack (SkyyProfiles / SkyyVault already copy metadata as an opaque blob, VERIFIED) |
| Accessory Power | accessories are their own mod. `kind:"accessory"` stays free for a later merge |
| Identify NPC | the identify code is a static `Gear.identify(...)` the NPC calls later. `/identify` gets a Server Setup switch `identify.command` |

### 1.5 The "legacy stamp" (why every gear item a player holds gets a document)

SkyyGear must write an `ItemDisplayMetadata` to show the rarity and level lines on any gear item. That is metadata anyway. So the
first time SkyyGear sees an undocumented gear stack **in a player's inventory**, it writes `{v:1, kind:"combat", r:"normal", id:true,
mods:[], src:"legacy", at, gate:"class"}` plus the tooltip. This is the same Normal state as reading rule 1, now written down.

It also closes an exploit. Unidentified tagging (5.5) only touches gear stacks with **no** document. An item that ever sat in a player
inventory under SkyyGear, or that a player threw (GearThrowSys below), can never be laundered into a random-rarity unidentified drop by
throwing it on a dying mob or feeding it to a looting mob.

When it runs:
- `PlayerReadyEvent` (fires on every world switch): the SkyyRolls `RollsReady -> RollsRefreshTask` shape. It waits out `profile:busy`,
  then makes up to 15 tries 2 s apart.
- `InventoryChangeEvent` (the ECS event SkyySkills' SmeltSys uses): marks the player dirty. One coalesced `world.execute` scan at most
  every 250 ms.
- The scan covers the 6 sections in SkyyRolls' order (hotbar, armor, tools, utility, storage, backpack). It rewrites a stack only when
  its `SkyyGearView.sig` differs.
- Never while `profile:busy:<uuid>` is set.
- **Pending crafts (5.1) only hold back stacks of the item ids being crafted**, never the whole scan. Every other gear stack is
  stamped as usual. A pending craft older than `PENDING_MAX_MS` (1,000 ms, a technical constant, not a balance number) is dropped
  and its item id is stamped too, so spamming crafts can never keep items undocumented.
- **When a player drops an item (GearThrowSys).** VERIFIED in the server jar: the player's drop packet goes through
  `InventoryPacketHandler` -> `ItemUtils.throwItem(...)`, which fires the cancellable ECS event `DropItemEvent$Drop` (`getItemStack` /
  `setItemStack`) on the dropping entity and then spawns whatever stack the event holds. `GearThrowSys` = an ECS event system for
  `DropItemEvent$Drop`: when the dropping entity is a player and the stack is undocumented gear, it stamps the stack (the same Normal
  document + tooltip) with `setItemStack` before the item entity exists. So a player-thrown gear item carries a document **every
  time**, however new it is in the inventory (a trade that finished a moment ago, a vault withdraw, a pending craft). NPC drops through
  the same method (`ActionDropItem`) are not players and are left alone. INFERRED (test 11.3 #8): the event is dispatched to the
  player's entity store like the other ECS events SkyySkills handles.

### 1.6 Migration of SkyyRolls items (LOCKED: already-rolled items keep their rolls)

SkyyRolls 0.1.5 wrote `"SkyyRolls": {reforge, dmg 0-30, str 0-25, crit 0-15, quality 0-100, rolledAt}` and `"SkyyRollsView": {v,
sig, disp, prev}` (VERIFIED, `build_skyyrolls_0.1.5.py` L587-600, L574-581). SkyyRolls stored **no rarity** of its own. Its colours
came from the item's engine quality. Its `quality` is a 0-100 "Roll Quality".

**The Roll Quality says nothing about the item's power.** VERIFIED `roll()` in every SkyyRolls version 0.1-0.1.5: `dmg =
nextInt(31)`, `str = nextInt(26)`, `crit = nextInt(16)` and `quality = nextInt(101)` are four independent draws. A max-stat item can
have quality 3, and a zero-stat item quality 100. Mapping rarity from it would (a) show the wrong colour for the real power (review
finding E6) and (b) make every SkyyRolls reforge a 10.9 % shot at Fabled right up to the swap (finding E8), and a migrated Fabled
reforges into a full Fabled roll forever after (rarity never changes on reforge). So the default maps rarity from the **stats**.

Migration, on the first stamp scan that sees the stack (1.5), and in memory for any bridge read:

| SkyyRolls field | SkyyGear |
|---|---|
| `dmg`, `str`, `crit` -> rarity | **`migrate.by = stats` (default):** score = the average of `dmg/30`, `str/25`, `crit/15` in % (SkyyRolls' own maxima, VERIFIED; a missing key counts 0). `r` from the table `migrate.map` (**PLACEHOLDER**, section 9): score >= 90 -> `fabled`, >= 75 -> `legendary`, >= 50 -> `rare`, >= 25 -> `unique`, else `normal`. With SkyyRolls' uniform rolls that gives about Fabled 0.7 %, Legendary 7.3 %, Rare 42.2 %, Unique 41.7 %, Normal 8.0 % (computed over all 12,896 combinations). Then capped at `migrate.maxRarity` (**PLACEHOLDER**, default `fabled`, Q20). Never `mythic` or `set`. **Other choices (Q2):** `roll` = the same table over the old Roll Quality; `item` = the item's engine quality: Junk/Common -> normal, Uncommon -> unique, Rare -> rare, Epic -> legendary, Legendary -> fabled, anything else -> normal |
| `dmg` | `{s:"dmg", v}` (Damage %) |
| `str` | `{s:"str", v}` (Strength) |
| `crit` | `{s:"cc", v}` (Crit Chance %; SkyyRolls' tooltip label was plain "Crit") |
| a stat that is 0 | dropped |
| `reforge` | `rf`, **except** `Legendary` and `Fabled`, which are now rarity names: those become no prefix |
| `quality` | not a stat: dropped from the lines (kept inside `old`) |
| whole document | copied into `old` |
| - | `id:true`, `src:"rolls"`, `kind` + `gate` (combat gear: `combat` + `class`; tools: see below), `at` = now |

- The modifier **count and values are kept as they are**, even above the rarity's placeholder count or range, and even above the
  item level's range (2.3) ("grandfathered", LOCKED "rolled items keep their rolls"). The tooltip shows them all. A reforge replaces
  them with a normal roll for that rarity and level.
- The migrated rarity is computed from the stored document, so the in-memory view (rule 2) and the written document agree. A
  `migrate.*` change in Server Setup only affects items that have not been rewritten yet.
- The top-level `SkyyRolls` and `SkyyRollsView` keys are removed. SkyyGear's view `prev` = the old `SkyyRollsView.prev` (the vanilla
  display from before SkyyRolls).
- Tools rolled by SkyyRolls keep their document. Their kind and gate follow the gate-skill rule (3.3), by tool family (VERIFIED
  families in Assets.zip): `Tool_Pickaxe_*` -> `mining` / `Mining`; `Tool_Hatchet_*` -> `foraging` / `Foraging`; `Tool_Hoe_*` and
  `Tool_Sickle_*` -> `farming` / `Farming`; `Tool_Shovel_*` -> `mining` / `Mining` (**PLACEHOLDER**, Q10); every other tool
  (shears, hammers, repair kits, ...) -> `tool` with no gate yet. Their lines and their gate line are shown with "(coming later:
  gathering gear)" because tools are not stage-1 gear: nothing on a tool is enforced or applied in 0.1. `/reforge` refuses tools until
  gathering gear exists (Q10).
- Items outside player inventories (chests, AH listings, vault) migrate when a player next holds them. Until then the bridge shows them
  migrated in memory (rule 2).
- **Reforge costs:** on its first start, if `Skyy_SkyyGear/config.properties` has no `cost.reforge.` lines and
  `Skyy_SkyyRolls/reforge.properties` exists, SkyyGear imports the old costs once:
  - the old per-quality costs map across: Common -> Normal, Uncommon -> Unique, Rare -> Rare, Epic -> Legendary,
    Legendary -> Fabled;
  - Mythic and Set take their placeholders;
  - one INFO line is logged. `Skyy_SkyyRolls/` itself is never written.

### 1.7 Item write safety (every path that rewrites a stack)

Rules copied from SkyyRolls' `ReforgePage.forge()` (VERIFIED L1427-1477):
- world thread only;
- refuse while `profile:busy`;
- the profile epoch must be unchanged since the page read the item;
- the slot must still hold the same item id and the same fingerprint (`Reforge.same()/fp()`: id + quality + metadata JSON);
- stack size must be 1;
- coins are taken first and refunded on any failure (logged `TAKE / REFUND`);
- a 400 ms click guard.
Gear items do not stack (MaxStack 1), but the check stays.

---

## 2. Rarity ladder

### 2.1 The ladder (LOCKED names and colours, Skyy 2026-09-25)

| # | id | Name | Colour (Skyy) | Hex (Wynncraft's Minecraft colour code) | Quality asset | Frame art reused (vanilla path) |
|---|---|---|---|---|---|---|
| 1 | `normal` | Normal | white | `#FFFFFF` | `Skyy_Gear_Normal` | Common |
| 2 | `unique` | Unique | yellow | `#FFFF55` | `Skyy_Gear_Unique` | Legendary (gold) |
| 3 | `rare` | Rare | pink | `#FF55FF` | `Skyy_Gear_Rare` | Epic (closest to pink) |
| 4 | `legendary` | Legendary | aqua | `#55FFFF` | `Skyy_Gear_Legendary` | Rare (blue) |
| 5 | `fabled` | Fabled | red | `#FF5555` | `Skyy_Gear_Fabled` | Developer slot + Common tooltip (red) |
| 6 | `mythic` | Mythic | purple | `#AA00AA` | `Skyy_Gear_Mythic` | Epic |
| 7 | `set` | Set | green | `#55FF55` | `Skyy_Gear_Set` | Uncommon (green) |

- The quality assets ship in the jar's asset pack (`B.manifest` already sets `IncludesAssetPack: true`; SkyyCooking ships items the
  same way). Path: `Server/Item/Qualities/Skyy_Gear_<Name>.json`. Fields: the vanilla `Common.json` field set (VERIFIED: QualityValue,
  TextColor, LocalizationKey, VisibleQualityLabel, RenderSpecialSlot, ItemTooltipTexture, ItemTooltipArrowTexture, SlotTexture,
  BlockSlotTexture, SpecialSlotTexture, ItemEntityConfig), with the texture paths of the "frame art" column. Only vanilla paths are
  referenced; no file is copied.
- `QualityValue` = the # column. In the engine it is only used by inventory sorting (`SortType`, VERIFIED: the only engine caller of
  `getQualityValue`). SkyyAuctions 0.1.1 reads it too (rarity tiers = values 1-5, "technical" = 8 and up, VERIFIED `AhItem.tiers /
  technical`): Set at 7 is never technical, and 7.3.1 A4 keeps the `Skyy_` qualities out of the vanilla tier list.
- `LocalizationKey` = `server.general.qualities.Skyy_Gear_<Name>`, with `general.qualities.Skyy_Gear_<Name> = <Name>` in the jar's
  `Server/Languages/en-US/server.lang`. Vanilla uses the same key form (VERIFIED).
- Build check: all 7 assets exist in the built jar; the TextColor = the hex column; every texture path exists in Assets.zip.
- INFERRED (test 11.3 #1): a plugin asset pack can add ItemQuality assets like it adds items. **Fallback:** if
  `ItemQuality.getAssetMap().getIndex(id)` does not find them at start, SkyyGear keeps the item's own quality, colours the Name line
  by rarity, and logs one WARN.
- The frame textures are vanilla placeholders. Pink and purple both use the Epic frame. The text colour is exact.

### 2.2 What rarity drives (LOCKED qualitatively: count and power; numbers PLACEHOLDER)

| Rarity | Modifiers (count) | Roll power low | Roll power high | Why this placeholder |
|---|---|---|---|---|
| Normal | 1 | 30 % | 60 % | Wynn's Normal has 0 IDs, but Skyy said plain gear gets modifiers when reforged, so a rolled Normal needs at least 1 (Q3) |
| Unique | 2 | 35 % | 70 % | |
| Rare | 3 | 40 % | 80 % | |
| Legendary | 4 | 45 % | 95 % | |
| Fabled | 5 | 50 % | 110 % | |
| Mythic | 6 | 60 % | 130 % | |
| Set | 3 | 45 % | 95 % | no set items exist in 0.1 (odds 0) |

The range gets **wider and higher** with rarity. That is LOCKED (Plan lock 3). The numbers are not. Config table `rarity` (3 columns:
mods | low % | high %).

**Stat base values** (the value at 100 % power on a full-level item, **PLACEHOLDER**, config table `stat`, columns `max | weight`).
The SkyyRolls maxima anchor dmg 30, str 25 and cc 15, so migrated items on full-level gear sit inside the new ranges (lower-level
items keep their grandfathered values, 1.6). Full list with weights in section 4.2.

**Item level scales the power (PLACEHOLDER formula, Q19; review finding E9).** Without it a level-0 Crude sword (2 rubble, 2 fibre,
2 sticks, Fieldcraft, 0 s: VERIFIED recipe) rolls exactly the same lines as a level-50 Mithril sword, so mass-crafting the cheapest
recipe would be the best way to fish for a Fabled. Wynn's own items give higher-level items bigger IDs. Level factor:
`f = stat.levelFloor + (100 - stat.levelFloor) x min(level, stat.levelFull) / stat.levelFull` (in %), with `stat.levelFloor` 25 %
and `stat.levelFull` 50 (the top Hytale materials, Mithril and Onyxium, 3.2) as **PLACEHOLDERS**. So Crude and Wood gear rolls at
25 %, Iron (20) at 55 %, Mithril at 100 %. `stat.levelFloor = 100` switches the scaling off. The level is the one resolved by 3.1 at
roll time; a later level-table change moves the gate, never the stored values.

### 2.3 How a roll works (craft, reforge, identify, admin give)

1. Pool = the section 4 stats allowed on this slot (weapon or armor, and for `mp` / `msteal` spell weapons only), with `weight > 0`.
   If the switch `pool.later` is OFF, "coming later" stats are left out too.
2. Pick `count` distinct stats from the pool, weighted, without repeats. The count is capped by the pool size.
3. For each stat: `v = randInt(max(1, round(max * low/100 * f/100)), max(1, round(max * high/100 * f/100)))`, where `f` is the item
   level factor above (100 when `stat.levelFloor` = 100).
4. Display order = section 4 table order (damage lines first, then offence, defence, movement, coming-later last).
5. Random source: one `java.security.SecureRandom` per JVM. Rolls are never seeded from the item, player or time, so they cannot be
   predicted.

---

## 3. Level requirement

### 3.1 Lookup (first match wins; nothing is stored on the item unless `lvl` is set)

1. `SkyyGear.lvl` on the item (explicit override; admin or future custom items).
2. Config table `level.item`: exact item id -> level. Add mode `held`, so an admin holds the item and types a level.
3. Config table `level.material`: the first `_`-separated token of the id that is a key (see 3.2).
4. If `level.vanilla` is ON (default): the item's own Hytale `ItemLevel` (`Item.getItemLevel()`, VERIFIED on 325 of 345 vanilla
   weapons and armor). It is clamped to 0..`levels.max` (100, SkyySkills' cap).
5. Else `level.default` (0).

### 3.2 Default material table (**PLACEHOLDER**, Server Setup table `level.material`)

The order is the one Skyy gave: Crude, Copper, Bronze, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium. The numbers are Hytale's
own `ItemLevel` where the order agrees. Where it does not, the item gets the smallest change that keeps Skyy's order.

| Token | Hytale ItemLevel (VERIFIED) | Default requirement | Note |
|---|---|---|---|
| Crude | 3-9 on weapons (diving armor 25-30) | **0** | class kit weapons (`Weapon_Shortbow_Crude`, `Weapon_Sword_Crude`, `Weapon_Battleaxe_Crude`, `Weapon_Daggers_Crude`) must work at skill 0 |
| Wood | 5-60 (`Weapon_Staff_Wood` 40, `Weapon_Wand_Wood` 40) | **0** | Mage and Priest kit weapons are Wood. Hytale's own level would lock a new Mage out of their kit staff |
| Copper | 10 | 10 | |
| Bronze | 25-28 | 15 | Hytale puts Bronze above Iron. Skyy's order puts it below, so it sits between Copper and Iron (Q11) |
| Iron | 15-20 | 20 | |
| Thorium | 30 | 30 | More Crossbow Tiers: `Weapon_Crossbow_Thorium` |
| Cobalt | 35 | 35 | `Weapon_Crossbow_Cobalt` (mod level 30) |
| Adamantite | 40 | 40 | `Weapon_Crossbow_Adamantite` |
| Mithril | 50 | 50 | `Weapon_Crossbow_Mithril` (45 in More Crossbow Tiers, 60 in the EndgameAndQoL crossbow pack; the table makes it 50 either way) |
| Onyxium | 50 | 50 | Skyy lists it after Mithril. Hytale gives both 50. Kept equal (Q11) |

**Special items** (no tier token) use their Hytale `ItemLevel` through step 4. Examples:
- Steel 20-30; Bone 25; Doomed 30; Frost 30; Flame Longsword 30; Spectral 40; Silversteel 45; Scarab 60; Prisma armor 75.
- Cloth: Wool 10, Linen 15, Cotton 25, Silk 35, Cindercloth 45.
- Leather: Soft 10, Light 15, Medium 25, Raven 32, Heavy 35.
- Staffs, wands and spellbooks mostly 40.
Every one of these is a `level.item` row away from a different value.

### 3.3 The gate skill and the check (LOCKED: every gear piece has a gate skill; combat = the class weapon skill, weapons AND armor)

**Kind -> gate skill** (LOCKED, Decisions change note 2026-09-25 #6 and HANDOFF "GEAR LEVEL CAP BY GEAR TYPE"; a code table
`GATE_BY_KIND`, written into `gate` when a document is created):

| Gear kind | Gate skill | Enforced in 0.1? |
|---|---|---|
| `combat` (weapons + armor) | `class` = the owner's class weapon skill: Archer -> Archery, Warrior -> Swordsmanship, Mage -> Sorcery, Berserker -> Fury, Priest -> Divinity (Assassin -> Assassination when that class opens) | **yes** (3.4, 3.5) |
| `mining` | `Mining` | no: shown "(coming later: gathering gear)" |
| `foraging` | `Foraging` | no, same |
| `farming` | `Farming` | no, same |
| later: `fishing`, other gathering kinds | that skill | - |
| `tool`, `equipment`, `accessory` | `tool`: none yet; `equipment`: `class` (1.4); `accessory`: its own mod | - |

Stage 1 builds combat gear only. The check below never looks at the kind: it reads `gate` and asks SkyySkills for that skill, so
gathering gear only has to add its items and its enforcement hooks.

- `gate:"class"`: the skill name comes from bridge `class:skill:<uuid>` (SkyyClasses, e.g. `"Swordsmanship"`). The number comes from
  `skill:fn:level` `apply(Object[]{UUID, name}) -> Integer` (SkyySkills).
  - If `class:skill` is absent, SkyyGear asks SkyySkills for the pseudo-skill `"Combat"`. SkyySkills resolves it to the active class
    row (VERIFIED, `SkillFn` L3540-3551).
  - SkyyGear keeps its own copy of the class -> skill map (Archer -> Archery, Warrior -> Swordsmanship, Mage -> Sorcery,
    Berserker -> Fury, Priest -> Divinity, Assassin -> Assassination) only for tooltip text when SkyyClasses is absent.
- Any other `gate` value is the SkyySkills skill name itself (`"Mining"`, ...). An unknown name (SkyySkills answers null) counts as
  level 0 and logs one WARN per name.
- **No class** (SkyyClasses present, player classless): level 0. Only level-0 gear works, and the tooltip says "Pick a class" (Q13).
- **No SkyySkills** (the bridge function is missing): the gate cannot be evaluated. `level.noSkills` = `pass` (default: never block;
  the level line is shown grey "Level 20") or `block`.
- The check is generic for later gathering gear: `have = level(owner, gate == "class" ? classSkill : gate)`, `ok = have >= need`.
- **Cache (review finding E2).** Per player, on the world thread: `{profile epoch, class skill name, skill -> level}`. Every lookup
  (every hit, every armor recompute) first reads `profile:epoch:<uuid>` and `class:skill:<uuid>` from the bridge map (two plain map
  reads, no Function call) and compares them with the cached pair. Any difference throws the cached levels away and re-reads them at
  once with `skill:fn:level` (the damage systems run on the world thread, so this is allowed), before the hit is judged. The 1 Hz
  GearTick re-reads the levels too (level-ups). Damage handlers never call `skill:fn:level` per hit otherwise. The GearReady refresh
  (1.5) warms the cache at join, because `skill:fn:level` may read the player's skill file on its first call (Overall-Level-Spec 4.8).
  - Why: a class change without a profile switch must never be judged with the old class's skill for even one hit. In the live set a
    player cannot switch class (SkyyClasses 0.1.6 `ALLOW_SWITCH = false`, a new class = a new profile, VERIFIED); `/classadmin set`
    (admin) and a future quest unlock (OPEN-QUESTIONS Server Setup 13) can, and SkyyClasses republishes `class:skill` within 2 s of a
    profile switch (ClassTick, VERIFIED), which the compare also catches the moment it lands.

### 3.4 Weapon above your level (or unidentified): blocked with a popup

The same mechanism as SkyyClasses 0.1.6 `DamageLock` (VERIFIED, docstring L85-110):
- It runs in `GearHitSys`, a `DamageEventSystem` in `DamageModule.get().getFilterDamageGroup()`, `Query.any()`.
- The attacker resolves to a player:
  - melee `Damage$EntitySource` -> the main hand `InventoryComponent.getItemInHand(buf, ref)` **and** the active utility (off-hand)
    item `InventoryComponent$Utility.getActiveItem()` (review finding E7: the Kunai is `Utility.Usable` and is thrown with right-click
    from the utility slot, 1.3). This is exactly SkyyClasses 0.1.6 `DamageLock` (VERIFIED docstring L85-86, code L1906-1918);
  - projectiles -> SkyyGear's own copy of SkyyClasses' `ShotTrack` (the launch record of main hand + utility item, so a bow swapped
    mid-flight is judged by the bow; SkyyClasses' shot-window rules are copied verbatim).
- Either of those items is gear and (unidentified, or `!ok`) -> `d.setAmount(0)` + `d.setCancelled(true)` + remove the target's
  `KnockbackComponent` (SkyyClasses does all three). The popup names the item that failed, with "(it is in your utility slot)" for
  the off-hand item (SkyyClasses' wording).
- **Stats** (4.3) come from the main-hand weapon only. A gear Kunai in the utility slot is gated but adds no weapon modifiers in 0.1
  (known limit). With SkyyClasses loaded it cannot hurt anyone today anyway: Assassin is not a playable class, and SkyyClasses blocks
  the weapons of a class that is not enabled for everyone (VERIFIED docstring L30-33).
- If `class:fn:allowed` already says the class may not use this item, SkyyGear does nothing. SkyyClasses blocks it and shows its own
  popup, so the player never sees two popups.
- **Popup:** copy `ClassRules.popup` (SkyyClasses L1678-1694) into SkyyGear:
  - `NotificationUtil.sendNotification(packetHandler, title, body, icon, NotificationStyle.Warning)`;
  - icon = `(ItemWithAllMetadata) new ItemStack(id, 1).toPacket()`, which is metadata-free;
  - throttled 1500 ms per player;
  - gated by the player switch `gear.blockedPopup`. Only the popup is gated, never the block.
  - Title "Level too low". Body "Iron Sword needs Swordsmanship 20 - you are 12".
  - Unidentified: title "Unidentified", body "Identify it first: /identify".
- Known limit (engine, same as SkyyClasses): deployables deal damage as their own entity and are not judged. Gear never includes them
  anyway (1.3).

### 3.5 Armor above your level (or unidentified): equips, gives no stats

Skyy's words (Decisions change note 2026-09-25 #5): "too-high armor gives no stats until the level is reached". This spec reads that
as **everything**, including Hytale's own health and protection on the piece (Wynn-faithful). That costs a hand-kept copy of the
engine's armor formula (part 3). The narrower reading, "only SkyyGear's own modifiers", is open question **Q18** (review finding F1).
The default stays "everything"; `level.armorNative = false` gives the narrow reading in game without a rebuild.

"No stats" means all of these while the piece is inactive:

1. **None of its SkyyGear modifiers count.** Totals (4.3) only sum active pieces.
2. **Hytale's own stat modifiers on the piece are cancelled.**
   - Vanilla armor `StatModifiers` are all Additive (VERIFIED over 120 armor items): Health on 117 pieces, Mana on 15, Oxygen on 4,
     Stamina on 1, SignatureEnergy on 1.
   - GearTick sums `ItemArmor.getStatModifiers()` of the inactive pieces per stat and puts a **negative**
     `StaticModifier(MAX, ADDITIVE, -sum)` under its own key `skyygear_lock_<stat>`. The SkyyAccessories `AccEffects` pattern
     (`EntityStatMap.putModifier/removeModifier`) handles it. MAX modifiers sum (VERIFIED `EntityStatValue.computeModifiers`), so this
     exactly cancels them. The key is removed at 0.
3. **Hytale's own damage resistance on the piece is cancelled.**
   - The engine applies armor in `DamageSystems$ArmorDamageReduction` (VERIFIED: a `DamageEventSystem` in the same Filter group) through
     the public static `getResistanceModifiers(World, ItemContainer armor, boolean canApplyPenalties, EffectControllerComponent)`,
     then `max(0, amount - flat)` and the multiplier, following `inheritedParentId`.
   - `GearHitSys` (ordered BEFORE `ArmorDamageReduction`) records the pre-armor amount for a player victim who wears an inactive piece.
     It keys the amount by the `Damage` object in an identity map.
   - `GearArmorSys` (ordered AFTER it) recomputes the result with the engine's formula over a temporary `SimpleItemContainer` copy
     that holds only the active pieces, then sets that amount.
   - The formula is copied from the `handle` bytecode. A bare-JVM test proves it equals the engine for the full container (11.1).
4. **Known limit (INFERRED rare):** `DamageClassEnhancement` (12 vanilla pieces), `KnockbackResistances` / `KnockbackEnhancements` /
   `DamageEnhancement` / `Regenerating` (2 each) and `MovementSettings` (1) are not cancelled in 0.1. They are listed in the build log
   at start.

- One chat line tells the player: "Your Mithril Chestplate gives no stats until Archery 50 (you: 12)". It is shown once each time a
  piece becomes inactive, and gated by `gear.armorWarn`.
- Switch `level.armorNative` (default ON) turns parts 2 and 3 off (safety valve).

### 3.6 When the gate re-checks

- On a hit: the cached skill level, after the epoch + class-skill compare (3.3). A mismatch re-reads the levels before the hit is
  judged.
- Every GearTick (1 s): skill levels are re-read. Any change of what an item's gate line shows (the colour, the skill name, or the
  "(you: N)" number) re-renders that item (6.3).
- On an armor change (`InventoryChangeEvent`): the inactive set is recomputed at once for the resistance path. The Health counter
  catches up on the next 1 s tick.
- On a class-skill or profile-epoch change seen by GearTick: the inactive armor set is recomputed at once too (not only on the next
  armor change).

---

## 4. Modifier pool for stage 1

### 4.1 Placement applied (LOCKED, Plan lock 125)

- Combat modifiers go on combat gear only. Movement modifiers go on any gear. Skill-specific modifiers go only on that skill's gear.
- A catalog row that names a tighter slot keeps that slot.
- Where the catalog names no slot, lock 125's general rule applies (any combat gear). A stat whose own text is about a hit (Exploding,
  Poison, Knockback) or about damage like Damage (True Damage) defaults to **weapon**. Defense defaults to **armor** (the catalog groups
  it with Health, which is "not weapons"). These defaults are open question Q8.

### 4.2 The pool (only Keep rows; status per stat)

Weights and max are **PLACEHOLDERS** (config table `stat`). "Live" says exactly what 0.1 does. "Later" = shown as
`<Name>: +v (coming later)` in grey. It rolls while `pool.later` is ON (Q4).

| Key | Stat (catalog name) | Slot | Unit | max @100% | weight | 0.1 | Mechanism |
|---|---|---|---|---|---|---|---|
| `dmg` | Damage | weapon | % | 30 | 10 | **LIVE** | GearHitSys: `amount x (1 + dmg/100)` on the weapon's own hits. The base is Hytale's damage (lock 15) |
| `str` | Strength | weapon, armor | flat | 25 | 10 | **LIVE** | `x (1 + str x combat.strPer/100)` on physical hits: melee, arrows, thrown, staff melee (lock 102). `combat.strPer` = 1.0 (**PLACEHOLDER**, SkyBlock's own rule, not a SkyWynn number) |
| `mp` | Magical Power | spell weapon, armor | flat | 25 | 10 | **LIVE** | same formula (`combat.mpPer` 1.0) on **spell** hits: a projectile launched from a staff, wand or spellbook (ShotTrack). The tooltip adds "(spells)" |
| `cc` | Crit Chance | weapon, armor | % | 15 | 10 | **LIVE** | crit roll per hit, no cap. Over 100 % = overcrit chance (lock 15) |
| `cd` | Crit Damage | weapon, armor | % | 30 | 10 | **LIVE** | crit = `x 2 x (1 + cd/100)`. 0 = double, +100 % = 4x (lock 15) |
| - | Overcrit | - | mechanic | - | - | **LIVE** | when a crit lands and CC > 100 %: a second roll at `CC - 100` %. On success `x 2` more (lock 15). At most one overcrit per hit |
| `tdmg` | True Damage | weapon | flat | 5 | 5 | **LIVE** | GearTrueSys adds it AFTER Hytale armor and SkyyGear Defense, so nothing reduces it (lock 15) |
| `fEarth` `fThunder` `fWater` `fFire` `fAir` | Earth / Thunder / Water / Fire / Air damage (base) | weapon | flat | 6 each | 4 each | **LIVE** | added to the hit as flat damage before the crit roll. Mobs have no element affinity or elemental defence yet, so the value lands in full (lock 17's model; affinities are a later stage) |
| `rThunder` `rWater` | Raw Thunder / Raw Water Damage | weapon | flat | 6 | 3 | **LIVE** | same as the base element lines |
| `rElem` | Raw Elemental damage | weapon | flat, each element | 3 | 3 | **LIVE** | adds its value once per element (5 x) |
| `msteal` | Mana Steal | spell weapon | flat mana per 3 s | 3 | 5 | **LIVE** | GearLeechSys (Inspect group, like SkyyClasses `PriestHealSys`): when a hit lands and 3 s (`steal.windowS`) passed since the last payout, `EntityStatMap.addStatValue(mana, v)`. Spell weapons only in 0.1, because only casters use Mana today (Q16) |
| `lsteal` | Life Steal | weapon, armor | % | 5 | 5 | **LIVE** | the preferred shape from lock 20: landed damage is summed per player, and every `steal.windowS` (3 s) the player heals `lsteal %` of it. The numbers are **PLACEHOLDER** (lock 20 says open) |
| `hpr` | Raw Health Regen | weapon, armor | flat per tick | 2 | 5 | **LIVE** | GearTick heals `hpr x (1 + hprp/100)` every `regen.periodMs` (2000, the SkyyAccessories Regeneration talisman period). Never above max, never when dead |
| `hprp` | Health Regen % | weapon, armor | % | 20 | 5 | **LIVE** | scales `hpr` only. Shown "(boosts Health Regen)" |
| `def` | Defense | armor | flat | 25 | 10 | **LIVE** | GearArmorSys, player victims, damage with an entity source (mob, player, projectile): `x 100 / (100 + def)` (`combat.defScale` 100 = SkyBlock's curve, **PLACEHOLDER**). Applied after Hytale's armor. Environment damage is untouched (Q17) |
| `spd` | Speed | armor | flat | 5 | 10 | **LIVE** | skyymove protocol v1 (`tools/skyymove.py`), source `gear.armor`, flat layer, `spd x speed.per/100` of default (`speed.per` 1.0 %). Never writes MovementSettings itself |
| `stam` | Stamina Regen | armor | flat per tick | 2 | 5 | **LIVE** | GearTick `addStatValue(stamina, stam)` every `regen.periodMs` while below max (lock 27: armor only) |
| `as` | Attack Speed | weapon, armor | % | 10 | 5 | later | needs per-weapon-family root interaction overrides (the research/Swing-Speed-Spec.md mechanism). The cap of **150 %** (LOCKED) is enforced on the total when it goes live |
| `fer` | Ferocity | weapon, armor | flat | 10 | 5 | later | extra strikes need code-dealt damage (`ComponentAccessor.invoke(ref, new Damage(...))`, INFERRED from CraftingManager's own `invoke`). Caps **300 enchant / 600 total** (LOCKED) |
| `thorns` | Thorns | armor | % | 10 | 5 | later | same code-dealt damage |
| `expl` | Exploding | weapon | % chance | 10 | 5 | later | area damage, same mechanism |
| `poison` | Poison | weapon | flat DoT | 20 | 5 | later | vanilla `Poison_T1..T3` effects exist (VERIFIED Assets). Mapping the value onto them is a later design |
| `kb` | Knockback | weapon | % | 20 | 5 | later | `Damage.KNOCKBACK_COMPONENT` meta key (VERIFIED) |
| `slow` | Slow Enemy | weapon | % chance | 10 | 5 | later | vanilla `Slow` effect (VERIFIED Assets), `EffectControllerComponent.addEffect` (SkyySkills pattern) |
| `weak` | Weaken Enemy | weapon | % | 10 | 5 | later | cuts a marked mob's outgoing damage in GearHitSys |
| `dEarth` `dThunder` `dWater` `dFire` `dAir` | Earth / Thunder / Water / Fire / Air Defence | armor | flat | 10 each | 3 each | later | mobs deal no element damage yet (lock 17: armor only) |
| `cwis` | Combat Wisdom | weapon, armor | % XP | 10 | 5 | later | SkyySkills must read `gear:fn:stats` (a SkyySkills patch, not this round) |

**Not in the 0.1 pool, and why:**
- Not separate IDs: the catalog's "Intelligence" (SB) and "Mana" (SB) Keep rows describe Hytale's mana system ("our modifiers add to
  Hytale's pool"), not rollable stats. Change note 18 says "No Intelligence ID". The mana lines that roll on gear are Max Mana and
  Mana Regen (both Equipment only, next line) and Mana Steal (in the pool). Review finding F3.
- Equipment-only: Earth/Thunder/Water/Fire/Air Damage %, Max Mana, Mana Regen, Health (ID).
- Skill trees only: Elemental Damage %, Elemental Defence, Reach.
- Skill trees + accessories: every Raw ... Spell Damage row, Jump Height.
- Accessory only: Spell Cost %.
- Acrobatics + accessories: Dodge Chance.
- Not on weapons or armor: Ability Damage.
- Gathering gear (later): every gathering stat, and every Wisdom except Combat Wisdom.
- Placement not stated anywhere: Loot Bonus, Loot Quality, Stealing, Trophy Hunter, XP Bonus (Q15).
- Blank or Open decisions: Major IDs, stone powers, tuning, Reflection, per-element main-attack and spell lines.

**Base lines (not rolls):**
- A weapon shows its engine base damage (SkyyRolls' `damageText`, from `ItemWeapon.getBasicDamageBreakdown`).
- Armor shows Hytale's native `Health: 17` and `Armor: 9% physical, 9% projectile` (native resistances).
- Armor never rolls Health: the catalog says armor uses its base Health (Health (ID) is Equipment/accessories only).

### 4.3 Combat math, in order (all numbers placeholders except the crit rules)

Attacker = a player whose hit comes from a gear weapon or bare hands. Victim side = a player target.

1. **GearHitSys** (Filter, BEFORE `ArmorDamageReduction`):
   - gate (3.4);
   - `T` = the main-hand weapon's modifiers + the modifiers of every active armor piece (weapon-only stats only from the weapon);
   - `a = amount x (1 + T.dmg/100) x (1 + T.str_or_mp x per/100)`;
   - `a += fEarth + fThunder + fWater + fFire + fAir + rThunder + rWater + 5 x rElem`;
   - crit: with chance `(crit.base + T.cc)/100`, `a x= 2 x (1 + (crit.baseDamage + T.cd)/100)`;
   - overcrit (a second roll at `chance - 1` when chance > 1) `x 2`;
   - then the pre-armor capture for victims with inactive armor.
   `crit.base` and `crit.baseDamage` are **PLACEHOLDERS**, default 0 (no crits without gear).
2. Engine `ArmorDamageReduction` (Hytale armor of the victim).
3. **GearArmorSys** (Filter, AFTER `ArmorDamageReduction`): the inactive-armor correction (3.5), then Defense (`def`).
4. **GearTrueSys** (Filter, AFTER `GearArmorSys`): `+ tdmg`.
5. **GearLeechSys** (Inspect group, the landed amount): life steal accumulator, mana steal.

- Every system returns at once when `d.isCancelled()`.
- SkyySkills' `CombatDmgSys` (+0.2 %/level) and SkyyClasses' `DamageLock` share the group, unordered. Multiplication does not care
  about order, and a cancel is honoured everywhere.
- PvP: the same rules on both sides.

---

## 5. Where gear gets rolled

### 5.1 Vanilla benches (all `CraftingManager` paths)

- VERIFIED order in `CraftingManager.craftItem`: `CraftRecipeEvent$Pre` -> remove inputs -> `CraftRecipeEvent$Post` -> `giveOutput`
  -> (deprecated) `PlayerCraftEvent`.
- The queued path (`CraftingManager.tick`) fires `$Post` then `giveOutput` too, and never fires `PlayerCraftEvent`.
- `giveOutput` puts each output stack into `InventoryUtils.getContainerForItemPickup(...)` via
  `SimpleItemContainer.addOrDropItemStack`. So the output lands in the player inventory, or at their feet when full.
- The events carry no output stack (VERIFIED: `getCraftedRecipe()`, `getQuantity()` only).

**GearCraftSys** = an ECS event system for `CraftRecipeEvent$Post` (SkyySkills `CraftSys` pattern). When the recipe's primary output is
gear:
1. Snapshot the **identity** of every stack of that item id in the 6 sections.
2. Add `{item id, time}` to `pendingCraft[uuid]` (per item id, so the stamp only holds back that id, 1.5).
3. `world.execute(CraftRollTask)`. It runs after `giveOutput` returns, in the same world task queue (FIFO).
4. The task finds stacks of that id that were not in the snapshot, have no `SkyyGear` document, **and look exactly like a fresh
   craft output**: metadata equal to the recipe output's (normally none at all) and durability at the item's maximum. At most
   `outputQty x quantity` of them.
5. Each one is rolled: rarity by the Smithing odds (5.3), `id:true`, `src:"craft"`, modifiers by 2.3.
6. Written into the same slot; that `pendingCraft` entry cleared. An entry older than `PENDING_MAX_MS` is dropped unrolled (1.5).

**Why the candidate rule (review finding E1).** The events carry no output stack, and `giveOutput` adds the stacks straight into the
container (VERIFIED above; the deprecated `PlayerCraftEvent` is skipped on the queued path), so the task cannot tag the literal
output object. Something else could arrive in the inventory between the snapshot and
the task (a vault withdraw, a finished trade, a pickup). The cap already means a craft never yields **more** rolls than it made
items. The candidate rule makes sure the roll can only land on a stack that is identical to what the bench just made: an old worn
copy, a copy carrying other metadata or an unmigrated SkyyRolls item is never picked. If an identical pristine copy slips in instead,
the player ends up with the same two items either way (one rolled, one stamped Normal). INFERRED (test 11.3 #3): a bench output has no
metadata and full durability.

- An output that overflowed to the ground becomes a Normal item (the stamp, 1.5: when it is picked up, or at once if the overflow drop
  goes through `ItemUtils.throwItem`). That is a loss for the player, never a gain; one log line.
- Crafts in creative mode are not rolled (the stamp makes them Normal).

### 5.2 SkyySacks `/craft` (never goes through CraftingManager)

- VERIFIED: SkyySacks gives outputs itself with `SimpleItemContainer.addOrDropItemStack(..., new ItemStack(gid, total))`
  (`build_skyysacks_0.7.6.py` L3370-3386), then reports `skill:fn:craftxp`.
- SkyyGear publishes `gear:fn:roll` (7.1). **The SkyySacks /craft hook** calls it for every output entry that SkyyGear calls gear and
  gives the returned stacks one by one. The `cook:fn:campfire` precedent works the same way.
- **Which SkyySacks version:** SkyySacks 0.7.7 is being built at the same time from `research/Bag-Restructure-Spec.md` (bag
  rarities, the Mythic Omni Bag). That spec does not list this hook (its header says it does not touch SkyyGear). The hook is small
  and self-contained (7.3.3), so it should go into 0.7.7; if 0.7.7 ships without it, it is the first item of SkyySacks 0.7.8.
- Without SkyyGear, or when the call returns null, SkyySacks gives the plain stack exactly as today.
- Until the hook is deployed, `/craft` gear comes out Normal through the legacy stamp. No exploit, just no roll.

### 5.3 Smithing rarity on craft (LOCKED concept; curve PLACEHOLDER)

1. **Base rarity** from the `odds` table, column `craft` (**PLACEHOLDER** weights): Normal 60, Unique 25, Rare 10, Legendary 4,
   Fabled 1, Mythic 0, Set 0.
2. **Smithing rarity** = `skill:fn:level(uuid, "Smithing") x smith.perLevel` %. The default `smith.perLevel` is 0.5, so 50 % at
   level 100, capped by `smith.cap` (50 %).
3. With that chance the rolled rarity **steps up one tier**. Never above `craft.maxRarity` (default `fabled`: no crafted Mythic, Q5).
   Never to Set.

- Shown on the item as nothing extra.
- `/gear` prints "Your Smithing rarity: +x % chance of a better rarity".
- SkyySkills needs no change (plain `skill:fn:level`). Without SkyySkills the bonus is 0.

### 5.4 Reforge (`/reforge` moves from SkyyRolls; LOCKED: higher rarity = wider, higher range)

- **Page:** a port of SkyyRolls' `ReforgePage`:
  - "Your gear" list in the SCAN order; preselects the held item;
  - "anvil" panel with the item's name in its rarity colour, rarity, level, current lines and cost;
  - a Reforge button.
  After a reforge the same page rebuilds and shows **Before** and **After** lines. It never closes and reopens (HANDOFF section 2).
- **What a reforge does:**
  - re-rolls the whole modifier set: count by rarity, values by the rarity's power range and the item's level factor (2.2, 2.3);
  - picks a new cosmetic `rf` name (not the current one) from `reforge.names`;
  - `rfN++`;
  - rarity, level, `set`, `id` and `src` never change (Q12).
- **Which items:**
  - identified gear only;
  - a legacy Normal with 0 modifiers gets Normal's count, the LOCKED "plain until reforged";
  - migrated SkyyRolls items lose their grandfathered lines and get a normal roll;
  - refused: unidentified ("identify it first"), `Tool_*` ("tools get their own modifiers with gathering gear"), non-gear, and stacks
    above 1.
- **Cost:** table `cost.reforge` (rarity -> `base | perLevel`), `cost = base + perLevel x level`. **PLACEHOLDER** defaults are the
  SkyyRolls 0.1.5 live costs mapped as in 1.6: Normal 250, Unique 500, Rare 1,000, Legendary 2,500, Fabled 5,000, Mythic 10,000,
  Set 2,500, perLevel 0.
- **Payment:** `coins:fn:take` first, refund with `coins:fn:add` on any failure. SkyyRolls' `Reforge.take/refund` code moves as is.
  A missing coin bridge with cost > 0 refuses, like SkyyRolls.
- **Smithing XP** (Plan: Smithing levels from reforging): `skill:fn:addxp` `apply(Object[]{uuid, "Smithing", xp, "gear:reforge",
  pkey})`. `xp` comes from table `xp.reforge` (**PLACEHOLDER**: Normal 5, Unique 10, Rare 20, Legendary 40, Fabled 80, Mythic 160,
  Set 40). "Smithing" is grantable by default (VERIFIED `bridge.addxp.skills`). SkyySkills' per-call and per-minute caps apply.

### 5.5 Unidentified drops: mobs AND world chests (LOCKED)

**Mobs (NPC death drops).**
- VERIFIED: `NPCDamageSystems$DropDeathItems` is an `EntityTickingSystem` on dying NPCs. When `!role.hasDroppedDeathItems()` and
  (`role.isDropDeathItemsInstantly()` or `DeferredCorpseRemoval.shouldRemove()`), it collects:
  - the NPC's own inventory items (`isPickupDropOnDeath`);
  - `ItemModule.getRandomItemDrops(role.getDropListId())`.
  Then `ItemComponent.generateItemDrops(accessor, list, position + offset, rotation)` -> `CommandBuffer.addEntities(holders,
  AddReason.SPAWN)`.
- `ItemComponent` has `getItemStack/setItemStack`. `setItemStack` marks it network-outdated (VERIFIED).
- 45 vanilla NPC drop lists contain `Weapon_` or `Armor_` items (VERIFIED).

1. **GearDeathMark** = an `EntityTickingSystem` with the same query, `SystemDependency(Order.BEFORE, DropDeathItems.class)`. Using the
   same condition, it records `{world, position}` of every NPC that drops **this tick**, and clears last tick's marks first.
2. **GearDropSys** = an EntityStore `RefSystem` on `ItemComponent` (the `ShotTrack` RefSystem pattern). In `onEntityAdded` with
   `AddReason.SPAWN`, it tags the stack when all of these hold:
   - it is gear;
   - it has **no** `SkyyGear` document;
   - it spawned within 2 blocks of a current mark in the same world.
   Tagging = `{r: odds.mob roll, id:false, mods:[], src:"drop"}` + the rarity quality + the unidentified tooltip, via `setItemStack`.
3. The window is exactly one tick. Items thrown by players always carry a document (the stamp and GearThrowSys, 1.5) and are never
   touched.

INFERRED (test 11.3 #4): the command buffer adds the holders within the same tick, so the mark is still valid. **Fallback if not:**
- nothing is tagged;
- drops stay Normal after pickup (no exploit);
- one WARN "death drops could not be matched".
If the ordered registration throws (NPC plugin not loaded), SkyyGear registers without the dependency and logs one WARN
(SkyyExploration's `ChestSpawnLateSys` pattern).

**World loot chests.**
- VERIFIED: `StashPlugin$StashSystem.onEntityAdded` rolls `ItemContainerBlock.getDroplist()` into `getItemContainer()` through
  `StashPlugin.stash(...)` the moment the chest's block entity is added, then clears the drop list (config
  `isClearContainerDropList`).
- Players can never create a drop list (SkyyExploration 0.2.1 docstring, VERIFIED).
- 49 prefab drop lists contain gear (VERIFIED).

1. **GearChestMark** = a ChunkStore `RefSystem` (query `ItemContainerBlock + BlockModule$BlockStateInfo`),
   `Order.BEFORE StashPlugin$StashSystem`. When `onEntityAdded` sees a non-empty drop list, it remembers the ref.
2. **GearChestTag** = the same query, `Order.AFTER StashPlugin$StashSystem`. When `onEntityAdded` sees a remembered ref, it rewrites
   every undocumented gear stack in the container to unidentified (`odds.chest`, `src:"chest"`) via `setItemStackForSlot`, then forgets
   the ref.
3. Tagging happens at generation, before any player can touch the chest.
4. It is independent of SkyyExploration (standalone rule) and works whether or not SkyyExploration is installed.
5. Unordered fallback + one WARN if Hytale:Stash is not loaded (the SkyyExploration pattern).

**Drop rarity odds** (table `odds`, **PLACEHOLDER** weights; "drops can be any rarity" is LOCKED, so Mythic > 0):

| Rarity | mob | chest |
|---|---|---|
| Normal | 50 | 45 |
| Unique | 30 | 30 |
| Rare | 13 | 15 |
| Legendary | 5 | 7 |
| Fabled | 1.5 | 2.4 |
| Mythic | 0.5 | 0.6 |
| Set | 0 | 0 |

Loot Quality and Trophy Hunter shift these later; they are not in 0.1.

**Other sources:**
- **SkyyExploration chest luck** (its extra drop-list roll goes straight into the opener's inventory, VERIFIED L136, L3834-3844):
  without a patch those items get the legacy stamp (Normal). SkyyExploration 0.2.2 (optional this round) wraps each gear stack with
  `gear:fn:unid` before giving it.
- **Breakable pots and barrels** with gear in their drop lists: block drops, not mobs or chests. They stay Normal in 0.1 (Q14).
- **Player death drops, class kits, island starter kits, admin `/give`:** Normal (stamp).

### 5.6 Unidentified rules

- Rarity is set and shown before identify (LOCKED): quality frame, Name colour, "Rarity: Rare" line.
- **Weapon:** cannot be used. Every hit is blocked by GearHitSys with the "Unidentified" popup (3.4).
- **Armor:** gives nothing: no modifiers, and native health and resistance are cancelled (3.5).
- Cannot be reforged. Can be dropped, stored, traded (`/trade`) and sold on the AH (default yes, Q6). The AH shows it as
  "Unidentified", filtered by its visible rarity.
- **Modifiers are rolled at identify time, not at drop time.** The item metadata JSON reaches every client (`toPacket` sends
  `metadata.toJson()`, VERIFIED), so rolls stored at drop time could be read early by a modded client. Nothing is stored until paid.
- The icon still shows the real item. Hiding it completely (Wynn's generic "unidentified" icon) needs placeholder items and is Q7.

### 5.7 `/identify` (LOCKED: coins, scales with rarity and level; formula PLACEHOLDER)

- **Command:** `/identify` (player, `hytale:Adventurer`) opens the Identify page. Later an NPC calls the same code and `/identify` can be
  switched off (`identify.command`, default ON).
- **Page:**
  - left: every unidentified item in the 6 sections (icon + "Unidentified Iron Sword" in rarity colour + level);
  - right: the selected item's rarity, level, cost and an **Identify** button;
  - top: **Identify all (N) - X coins**.
  After identifying, the page rebuilds with the revealed lines ("Revealed: Strength +12, Crit Chance +5%").
- **Cost:** table `cost.identify` (rarity -> `base | perLevel`), `cost = base + perLevel x level`. **PLACEHOLDER**:

| Rarity | base | perLevel |
|---|---|---|
| Normal | 50 | 5 |
| Unique | 100 | 10 |
| Rare | 250 | 20 |
| Legendary | 500 | 40 |
| Fabled | 1,000 | 80 |
| Mythic | 2,500 | 150 |
| Set | 500 | 40 |

- **Flow:** the 1.7 write safety applies. Coins are taken, then the modifiers roll (2.3, the item's rarity), then `id:true`, `idAt`,
  `idBy`, the tooltip is rewritten, and the stack goes back into the same slot. Any failure refunds.
- "Identify all" runs the items one by one, each paid separately, and stops at the first refusal with a summary line.
- No Smithing XP for identifying (none is designed).

### 5.8 Pages (HANDOFF section 2 rules + the vanilla look)

**Vanilla look (LOCKED, Skyy 2026-09-28; HANDOFF section 2 rule 0, tools/AGENT-BRIEF.md "UI LOOK").** Both pages must look and feel
like Hytale's own UI, not like our old dark-blue panels:
- **Model:** the vanilla item-repair page is the closest vanilla page to Reforge and Identify (pick an item from a list, act on it).
  Mirror `Common/UI/Custom/Pages/ItemRepairPage.ui` and `ItemRepairElement.ui` from Assets.zip (VERIFIED present): a
  `@DecoratedContainer` frame with the `@Title` header, a scrolling item list (`@DefaultScrollbarStyle`), rows = a 32 x 32 item icon,
  a bold name label, a secondary value label in `#ffffff(0.6)`, a 2 px `#ffffff(0.6)` divider, row hover `#000000(0.2)`.
- **Shared styles** from `Common/UI/Custom/Common.ui` (VERIFIED values): the frame textures `Common/ContainerHeader.png`,
  `Common/ContainerPatch.png` (border 23), `Common/ContainerDecorationTop.png` / `Bottom.png`; buttons `@DefaultTextButtonStyle`
  (Reforge, Identify), `@SecondaryTextButtonStyle` (Identify all), `@CancelTextButtonStyle` / `@BackButton` (back to the SkyWynn
  Menu), with the vanilla `ButtonSounds`; colours `@ColorDefault #ffffff`, `@ColorDefaultLabel #96a9be`, `@ColorGrayCaption
  #878e9c`, `@ColorGoldHighlight #E8A93B` (costs), `@ColorDisabled #797b7c` (a refused button).
- **How:** through the shared vanilla style helper for build scripts (RESUME step 5). If that helper does not exist yet when SkyyGear
  is built, copy these values inline in the build script and mark them for the helper. Never ship a `.ui` file (HANDOFF rule 2).
  Whether an inline page may reference the client's own `Common.ui` directly is part of the step-5 research, not assumed here.
- **Our own colours:** only Skyy's 7 rarity colours (2.1), on item names and the rarity line. Mythic `#AA00AA` may be hard to read on
  the vanilla panel: if so, the page (never the tooltip) uses the readable variant `#CC66CC`, the same choice SkyySacks makes for bag
  pages (`research/Bag-Restructure-Spec.md` 3.2), so both mods look the same.
- **Popups** already are vanilla (`NotificationUtil`, `NotificationStyle.Warning`, 3.4). **Tooltips** use the engine's own
  `ItemDisplayMetadata` and the quality frame (6.1); text colours other than the rarity colours come from the vanilla palette above.

**Layout rules (HANDOFF section 2):**
- Inline pages only; root Group anchor Width/Height only.
- Page size: Reforge 1100 x 880, Identify 1100 x 880 (inside the verified 1120 x 952). The vanilla repair page is 600 x 400; the pages
  stay big for readability (brief: "BIG readable pages") but keep the vanilla frame, spacing and fonts.
- Ids without underscores (`#SkyyGRoot`, `#SkyyGList`, `#SkyyGRow0`, `#SkyyGBtnForge`, `#SkyyGBtnId`, `#SkyyGBtnAll`).
- `TextButton` + `EventData.of("a", "sel:3")`.
- No periodic updates, no MouseEntered/Exited updates, never close-then-open. Nothing on the vanilla inventory screen.
- **Item icons:** `new ItemGridSlot(new ItemStack(id, 1))`, **never** the real stack (metadata disconnect). Rolls, rarity and level are
  shown as text.
- `setSkipItemQualityBackground(true)` on those slots. Tinting the icon's frame with `.withQuality(idx)` (a plain int, not metadata)
  is allowed only after an in-game check (11.3 #2). Default OFF.

---

## 6. Tooltips (SkyBlock style: base value, then the roll in brackets; Skyy 2026-09-24)

### 6.1 Identified item

`ItemDisplayMetadata` Name = `"<rf> <item name>"` in the rarity hex (no prefix when `rf` is absent). Description, top to bottom:

```
<vanilla description, grey>

Damage: 10-18 (+24%)           <- base from ItemWeapon damage data, roll in brackets (dmg)
Fire: +6
Strength: +12
Magical Power: +8 (spells)
Crit Chance: +5%
Life Steal: +3% (every 3s)
Ferocity: +8 (coming later)    <- grey, every "later" stat

Swordsmanship Lv. 20           <- green when the owner has it, red otherwise: "Swordsmanship Lv. 20 (you: 12)"
RARE WEAPON                    <- rarity hex, Wynn style
Reforge: Sharp (2x)
```

- Armor base lines: `Health: 17` and `Armor: 9% physical, 9% projectile` (native).
- An inactive armor piece gets one extra red line: "Gives no stats until Archery 50".
- A stat with a base value prints `Base (+roll)`, e.g. `Damage: 11-48 (+24%)`. A stat without a base prints `+roll`.
- Migrated items with more lines than the rarity allows show them all.
- A tool migrated from SkyyRolls shows its lines and its gate line ("Mining Lv. 20", grey, no "you" check) with "(coming later:
  gathering gear)": nothing on a tool is enforced in 0.1 (3.3).

### 6.2 Unidentified item

```
Name:  Unidentified Iron Sword                (rarity hex)
       Rarity: Rare
       Swordsmanship Lv. 20                   (green / red as above)
       Unidentified - its modifiers appear when you identify it.
       Cannot be used until identified.       (armor: "Gives no stats until identified.")
       Identify: /identify - 1,150 coins
```

### 6.3 Owner-specific lines and refresh

- Level colour, the "(you: 12)" text, the class skill name and the "no stats" line depend on the **owner**. SkyyGear renders them for
  the player whose inventory holds the item.
- `sig` = hash of: item id, stack quality, gear document JSON, resolved level, base damage text, **the rendered owner lines** (the
  gate line exactly as shown, including the colour and the "(you: N)" number, and the "no stats" line), config epoch. So any change
  the player can see re-renders the item: a level-up that keeps them below the requirement (12 -> 18 of 20) updates "(you: 18)", not
  only a flip between red and green (review finding E5). A level-up while the line is green changes nothing shown and writes nothing.
  A table change in Server Setup re-renders on the next scan.
- GearTick compares each held item's sig with the cached one after the 1 s level re-read and rewrites only the items whose sig
  changed (levels change rarely, so this is a handful of writes per level-up).
- Items elsewhere keep the text of their last owner. The AH and Trade show their own text via `gear:fn:describe`.

### 6.4 Writing rules

- `VIEW_V = 1`. A higher future value forces a re-render.
- `prev` keeps the pre-SkyyGear display, so `/gear clear` restores it.
- The Name line falls back to the item's translation Message when the en-US text has `{params}` (SkyyRolls `nameMsg`, VERIFIED
  L332-341).
- All text is built as `Message.raw(...).color(hex)` children (SkyyRolls `statLine`). Nothing goes through the inline UI parser.
- **Colours (vanilla look, 5.8):** the Name line and the rarity line use Skyy's rarity hex (2.1). Every other line uses the vanilla
  palette: no colour set (the client's default tooltip text) for base and modifier lines, `#878e9c` (vanilla `@ColorGrayCaption`) for
  the vanilla description and every "(coming later)" line. The gate line keeps green `#55FF55` / red `#FF5555` (Wynn's) until the
  RESUME step-5 style research names vanilla success / warning colours; the style helper then replaces them in one place.

---

## 7. Bridge contract and other mods

### 7.1 SkyyGear publishes (`System.getProperties().get("skyy.bridge")`, put in `setup()`, never removed)

All functions: `java.util.function.Function`. They never throw, never touch ECS, never write files, and are safe from any thread.
`X` = an `ItemStack`, or `Object[]{String itemId, org.bson.BsonDocument metadata}`. Engine and BSON classes come from the server
classloader shared by every plugin; a mod's own classes never cross.

| Key | Call | Returns |
|---|---|---|
| `gear:fn:describe` | `apply(X)` | `String[]` plain lines (name, rarity, level, base + modifier lines, "Unidentified" state). `null` = not gear. SkyyRolls documents are migrated in memory first |
| `gear:fn:rollsLine` | `apply(X)` | one-line `String` summary for the AH: `"Rare - Lv 20 - Strength +12 - Crit Chance +5%"`; `""` for a Normal with no modifiers; `null` = not gear |
| `gear:fn:rarity` | `apply(X)` | rarity id `String` (`"normal"`..`"set"`), `null` = not gear |
| `gear:fn:level` | `apply(X)` | `Integer` required level (3.1) |
| `gear:fn:identified` | `apply(X)` | `Boolean` |
| `gear:fn:sig` | `apply(X)` | `String` fingerprint of **item id + stack quality index** + rarity + identify state + modifiers (AH "rolls differ" caveat). The id and quality are in the hash so two different items of the same rarity (an unidentified Rare Iron Sword and an unidentified Rare Wood Wand) never share a sig (review finding E4). `null` = not gear |
| `gear:fn:gate` | `apply(Object[]{UUID, X})` | `Object[]{Boolean ok, String skill, Integer need, Integer have, Boolean enforced}` (from the cache; a cold cache asks SkyySkills). `skill` = the resolved gate skill (the class weapon skill for `class`); `enforced` = false for kinds 0.1 does not enforce yet (3.3) |
| `gear:gates` | plain value | the kind -> gate table: `"combat:class,mining:Mining,foraging:Foraging,farming:Farming"` (later mods read it instead of copying it) |
| `gear:fn:stats` | `apply(UUID)` | `String` `"str:12,cc:5,def:25,..."`: the player's current active totals (later: SkyySkills Combat Wisdom, HUD stats) |
| `gear:fn:roll` | `apply(Object[]{UUID player, String itemId, Integer count, String source, String recipeId})` | `Object[]` of `ItemStack`, `count` long: rolled, identified, Smithing odds for `source = "craft"`. `null` = not gear / crafting rolls off |
| `gear:fn:unid` | `apply(Object[]{ItemStack, String source})` | the stack tagged unidentified (`odds.<source>`, `source` = `mob` or `chest`); unchanged when not gear or already documented |
| `gear:tiers` | plain value | `"normal:Normal:#FFFFFF,unique:Unique:#FFFF55,rare:Rare:#FF55FF,legendary:Legendary:#55FFFF,fabled:Fabled:#FF5555,mythic:Mythic:#AA00AA,set:Set:#55FF55"` |
| `gear:stats:<uuid>` | plain value | same string as `gear:fn:stats`, republished by GearTick on change |
| `config:def:SkyyGear`, `config:fn:SkyyGear`, `config:epoch:SkyyGear` | config kit (section 9) | |
| `settings:def:gear.*` | player switches (9.3) | |

### 7.2 SkyyGear reads

| Key | From | Used for |
|---|---|---|
| `class:skill:<uuid>`, `class:fn:allowed` | SkyyClasses | gate skill name (compared on every gate lookup, 3.3); skip items the class lock already blocks |
| `skill:fn:level`, `skill:fn:addxp` | SkyySkills | gate levels, Smithing rarity, reforge Smithing XP |
| `coins:fn:get/take/add` | SkyyCoins | identify and reforge |
| `profile:fn:key`, `profile:busy:<uuid>`, `profile:epoch:<uuid>` | SkyyProfiles | per-profile notice flag, write refusal, epoch checks, gate cache (3.3) |
| `move:<uuid>` map | skyymove protocol v1 | Speed |
| `settings:fn:get`, `settings:fn:register` | SkyyMenu | player switches (6-element registration, visible to every player, 7.3.2) |

### 7.3 Compat patches this round

SkyyGear 0.1 works without any of them. It only loses the feature each one names. Every page these patches add or change follows
the vanilla look (5.8): new elements use the vanilla styles; the full vanilla pass of the existing AH and menu pages is RESUME step 5
and is not a condition for these versions.

#### 7.3.1 SkyyAuctions 0.1.1 -> 0.1.2 (gear text and rarity through the bridge + Skyy's AH locks)

**A. Gear names, rarity and modifier lines.** Why: the roll line reads the literal key `"SkyyRolls"` (`AhItem.reforge / hasRolls /
statLabel / rollsLine`, L1373-1417, 6 call sites). Without a patch the AH shows no roll line and the "rolls are not compared" caveat
disappears (cosmetic, not a crash).
1. `rollsLine(meta)` -> `gear:fn:rollsLine(Object[]{itemId, meta})` when the bridge function exists; else the old SkyyRolls parse
   (servers without SkyyGear keep working).
2. `hasRolls` -> `gear:fn:sig != null`. The "a cheaper one is listed" caveat already groups by item id (`AhStore.lowestBin(iid, ...)`,
   VERIFIED L3146); with SkyyGear it says "- rolls differ" when the cheaper listing's `gear:fn:sig` differs, and nothing when it is the
   same.
3. `statLabel` / `reforge` removed (`gear:fn:describe` covers them). The item page's text lines come from `gear:fn:describe` when
   present.
4. **Rarity filter:** `tiers()` takes the Wynn ladder from `gear:tiers` when present. A listing's tier = `gear:fn:rarity` for gear,
   else the engine quality as today. The fallback scan (QualityValue 1-5) skips quality ids that start with `Skyy_`, so SkyyGear's and
   SkyySacks' own qualities never double the vanilla tiers. `qColor` already reads the stack quality's TextColor, so the new quality
   assets colour AH rows with no change (VERIFIED L1318-1323).
5. Item page: the unidentified state shows as "Unidentified (Rare, Lv 20)". Listing snapshots stay opaque; nothing to migrate.

**B. 48h costs double the listing fee** (LOCKED, OPEN-QUESTIONS Auction House 2; HANDOFF log 2026-09-25). Why: 0.1.1 adds a flat
1,200 coins for 48h (`durations=...,48h:1200`, `DUR_FEE`, fee = `listingFee(price) + DUR_FEE[i]`, VERIFIED L499, L565, L2017-2019).
1. A duration preset's fee may be written `x<N>`: the listing fee is multiplied by N and no flat fee is added. The new default is
   `durations=1h:20,6h:45,12h:100,24h:350,48h:x2`. So 48h = twice the 1 % / 2 % / 2.5 % tier fee; 1h-24h keep their flat adds.
2. Fee = `listingFee(price) x N` for an `x` preset, else `listingFee(price) + flat` as today. The Create page shows the total and says
   "(48h: double listing fee)".
3. `config.properties` on Skyy's server still holds the 0.1.1 stock line. On start, when the `durations` line is exactly the old stock
   default `1h:20,6h:45,12h:100,24h:350,48h:1200`, 0.1.2 rewrites that one line to the new default (atomic write, one INFO line). A
   hand-edited line is kept and logged once as "custom durations kept".

**C. A different profile may buy your listing; the same profile may not** (LOCKED, OPEN-QUESTIONS Auction House 4). Why: 0.1.1 refuses
every profile of the seller's account unless `sameAccountBuy=true` (VERIFIED L2175, L3175).
1. The own-listing check by profile key stays (`key == seller.key` -> "That is your own listing.", VERIFIED L2174).
2. The account-wide refusal goes. New key `otherProfileBuy=true` (default): another profile of the same account may buy. `false`
   restores the old refusal for servers that want it.
3. `sameAccountBuy` is retired: an old line is ignored and logged once ("replaced by otherProfileBuy"). Its admin status text and the
   "solo testing only" warnings go with it.
4. The listing page note "Listed by your profile X - you cannot buy from yourself" is shown only for the same profile key.

**D. Magic Bags and the Accessory Bag are off the market** (LOCKED, OPEN-QUESTIONS Auction House 15). Why: 0.1.1 only lists them as
commented examples in `blocked.txt` (VERIFIED L546-547), so they can be listed and bought.
1. Built-in block entries (owner `builtin`, not written into `blocked.txt`): `Skyy_Sack_*` (every Magic Bag, including SkyySacks
   0.7.7's new `Skyy_Sack_<Type>_Rare` and `Skyy_Sack_Omni`) and `Skyy_Accessory_Bag`, reason "Magic Bags and the Accessory Bag open
   their owner's own storage - they cannot be sold". `AhItem.isBag(id)` already matches exactly these ids (VERIFIED L1429-1431).
2. Listing is refused. Buying is refused through the existing `blockedReason(iid)` check (VERIFIED L2167), so a bag listed before
   0.1.2 can no longer be bought; its seller cancels or lets it expire and claims it back as usual.
3. Config switch `blockBags=true` (default) for servers that want bags tradeable. The "Contents not included" notes stay for that case.

#### 7.3.2 SkyyMenu 0.3.2 -> 0.3.3 (Identify tile, Reforge text, Mods list, Settings at slot 39, settings by permission)

1. **Mods list: SkyyGear replaces SkyyRolls.** Replace the SkyyRolls dict (static, L459-464) with SkyyGear: version 0.1, a gear weapon
   icon, check `gear`, commands `/reforge`, `/identify`, `/gear` and the admin `/gear give | read | reroll | clear | rarity | unid |
   identify | level | gate | migrate` lines; config `Skyy_SkyyGear/config.properties`; setup `("0.1", "Gear", "rarities, levels,
   costs and odds")`; desc "Rarity, level and modifiers on every weapon and armor piece: crafted gear rolls, mob and chest gear drops
   unidentified, /identify reveals it, /reforge rerolls it." Server Setup -> Gear appears by itself (the menu scans `config:def:*`,
   VERIFIED).
2. **Reforge tile** (main slot 25) keeps `cmdc:reforge` (same command name). New text: "Put in a weapon or armor piece and pay coins to
   reroll its modifiers." (tools are refused in 0.1, 5.4).
3. **Identify tile:** main slot **26**, right of Reforge (free in 0.3.2: the main view uses 4, 8, 10-16, 20-25, 30-32, 40, 41, 51; nav
   45, 48, 49, 50; VERIFIED L166-232, L640). Icon `Ingredient_Crystal_Purple` (VERIFIED in Assets.zip; the build checks it like the
   other icons). Text: "Reveal the modifiers of unidentified weapons and armor from mobs and loot chests. Costs coins by rarity and
   level." + "Command: /identify". Action `cmdc:identify`.
4. **Settings icon to slot 39** (LOCKED, OPEN-QUESTIONS Player Settings; research/Settings-Spec.md 4.1): the torch entry moves from
   main slot 51 to **39**, immediately left of Mods (40); Server Setup stays at 41; slot 51 becomes free. Entry:
   `("main", 39, "Furniture_Crude_Torch", "Settings", [...unchanged lines...], "Click to open!", "settings")`.
5. **Settings visibility by permission** (LOCKED, OPEN-QUESTIONS Player Settings; Settings-Spec 4.4 "Who sees a row"):
   - `settings:fn:register` and `settings:def:<key>` accept an optional **7th element** `String perm` (a permission node). Six-element
     registrations work as before (= every player may change it).
   - The Settings page draws a row only when the viewer has that node (the same permission check the menu uses for Server Setup).
     Rows the player may not change are **hidden**: no greyed-out or disabled entry. Tab paging counts only visible rows; a tab with no
     visible row is not drawn.
   - `settings:fn:set` refuses a key whose node the player lacks (a stale page click).
   - SkyyGear's three switches (9.3) carry no node: every player sees them.
6. The MENU DATA help lines mention `/identify` next to `/reforge`.

#### 7.3.3 SkyySacks /craft hook: `gear:fn:roll` (SkyySacks 0.7.7, else 0.7.8)

Why: `/craft` hands out plain gear (no `CraftingManager`, VERIFIED), which breaks the LOCKED "crafted gear rolls on craft" for
SkyWynn's main crafting path. SkyySacks 0.7.7 is being built in parallel from `research/Bag-Restructure-Spec.md`, which does not list
this hook (5.2).
1. In the output loop (0.7.6 L3370-3386): when the bridge has `gear:fn:roll` and it returns non-null for an entry
   (`apply(Object[]{uuid, itemId, count, "craft", recipeId})`), give each returned stack with `addOrDropItemStack` instead of the plain
   `new ItemStack(gid, total)`.
2. Count `given` from the returned stacks (count before and after, the engine rule) and log `gear=<n>` in `crafts.log`.
3. Otherwise unchanged. Page grids keep `new ItemStack(id, qty)` (never a stack with metadata in an `ItemGridSlot`).

#### 7.3.4 SkyyExploration 0.2.1 -> 0.2.2 (optional)

The chest-luck extra roll puts gear straight into the opener's inventory (Normal via the stamp). Wrap each stack with
`gear:fn:unid(Object[]{stack, "chest"})` before `addOrDropItemStack` (L3834-3844).

### 7.4 Keep working unchanged (checked in the live scripts)

- **SkyyEssentials 0.1.4 `/trade`:** fingerprints by metadata JSON; the grid is metadata-free and shows `getDisplayName/Description`.
  That is SkyyGear's own tooltip.
- **SkyyProfiles 0.1.2, SkyyVault 0.1.2:** copy metadata as an opaque blob; quality is saved by `ItemStack.CODEC`.
- **SkyyClasses 0.1.6:** reuse target only. Its kits give plain stacks, which become Normal via the stamp; Crude/Wood are level 0.
- **SkyySkills 0.4.5:** SkyyGear only calls its existing functions. `CombatDmgSys` multiplies alongside.
- **SkyyAccessories 0.4.4:** different stat keys (`skyyacc_*` vs `skyygear_*`). The Speed layers follow HANDOFF: armor flat,
  accessories %.
- **SkyyTrees, SkyyCollections, SkyyCooking, SkyyBazaar** (no gear on the bazaar), **SkyyHud, SkyyParty, SkyyGuilds, SkyyIslands,
  SkyyRanks, SkyyBank, SkyyCoins:** no gear coupling.
- **SkyyExploration 0.2.1:** keeps working. SkyyGear's chest tagging is its own system.
- **Rounds 8 and 9 (built before SkyyGear, RESUME steps 2-3):** SkyySkills 0.4.6, SkyyClasses 0.1.7 (kits straight into the hotbar:
  still plain stacks, so still Normal via the stamp), SkyyEssentials 0.1.5, SkyyVault 0.1.3, SkyySacks 0.7.7, SkyyCollections 0.2.3,
  SkyyParty 0.1.5, SkyyTrees 0.2.4, SkyyIslands 0.5.3, SkyyRanks 0.1.1. As their changes are listed in RESUME and their specs, none
  removes or reshapes a bridge key SkyyGear uses: `research/Overall-Level-Spec.md` only adds the name "Overall" to `skill:fn:level`,
  and `research/Bag-Restructure-Spec.md` leaves the `/craft` output loop alone. The SkyyGear build re-checks them against the versions
  pinned in `tools/deploy_set.py` SET at that time (the round's cross-check).

---

## 8. Retiring SkyyRolls

### 8.1 Commands

| SkyyRolls 0.1.5 | SkyyGear 0.1 | Permission |
|---|---|---|
| `/reforge` | `/reforge` (same page, moved) | player: `setPermissionGroups(new String[] { "hytale:Adventurer" })` |
| - | `/identify` | player (same) |
| - | `/gear`: held item's gear lines, your active totals, your Smithing rarity (chat) | player root (same) |
| `/rolls give [item]` | `/gear give <item> [--rarity <id>] [--unid true]` (item as a usage variant, SkyyRolls 0.1.1 pattern) | admin: `requirePermission("skyygear.admin")` + `setPermissionGroups(new String[0])` on the sub-command and the variant (lint `perm_group_leaks`) |
| `/rolls read` | `/gear read`: parsed document + raw metadata JSON | admin (same) |
| `/rolls reroll` | `/gear reroll`: free reforge of the held item | admin |
| `/rolls clear` | `/gear clear`: removes SkyyGear data, restores `prev` (the item is Normal again) | admin |
| - | `/gear rarity <id>`, `/gear unid`, `/gear identify`, `/gear level <n or clear>`, `/gear gate <skill or class>` (sets the held item's gate skill, 1.2), `/gear migrate [player]` (runs the stamp/migration scan now and prints counts) | admin |

- There is no `/rolls` alias. The retired mod's name stays free, and a leftover SkyyRolls would otherwise collide.
- The config kit re-checks the same node, `skyygear.admin`, for every Server Setup change. SkyyRanks can grant it.
- lint: no `ADMIN_ONLY_OK` entry is needed. Every command sets groups or `requirePermission` with empty groups. If lint still warns,
  that is a main-session follow-up (`tools/ci/lint.py` is off limits here).

### 8.2 Data

- `Skyy_SkyyRolls/` stays on disk untouched. SkyyGear reads `reforge.properties` once for the cost import (1.6).
- SkyyGear's folder is `Skyy_SkyyGear/` via `getDataDirectory().resolveSibling("Skyy_SkyyGear")`:
  - `config.properties`: every section 9 row, written by the kit;
  - `config-changes.log` + `config-history/`: the kit's;
  - `players/<pkey>.properties`: `noticeShown`, the migration notice;
  - `gear.log`: identify, reforge, admin give, coin TAKE/REFUND, migration counts, WARN lines; rotated at 5 MB.
- Items migrate lazily (1.6). There is no bulk world rewrite.

### 8.3 Deploy note (for the main session; `tools/deploy_set.py` is not edited here)

- In `SET`: add `("SkyyGear", "0.1")`, remove `("SkyyRolls", "0.1.5")`, and put `"SkyyRolls"` in `RETIRED`. deploy_set already stops
  if a retired name is still in SET, and switches the retired world key off (VERIFIED L52-54, L108, L146).
- **Deploy together:** SkyyGear 0.1 + SkyyAuctions 0.1.2 + SkyyMenu 0.3.3 + the SkyySacks version that carries the `/craft` hook
  (0.7.7 if its builder added it, else 0.7.8; 7.3.3) (+ SkyyExploration 0.2.2 if built). SkyySacks without the hook may still deploy:
  `/craft` gear is then Normal until the hook lands.
- **Never go back to SkyyRolls after SkyyGear ran:** migrated items no longer carry the `SkyyRolls` key, so SkyyRolls would show them
  unrolled. The original document is kept in `SkyyGear.old` for a manual rollback tool if one is ever needed.
- HANDOFF section 3, TEST-CHECKLIST and DESIGN-STATUS updates are main-session work.

### 8.4 If SkyyRolls is still loaded next to SkyyGear

- Both register `/reforge`, and the engine silently keeps the last one.
- At `start()` and at the first join, SkyyGear checks the bridge for `config:def:SkyyRolls`. When it finds it, SkyyGear logs one WARN
  and tells admins at join: "SkyyRolls is still enabled - retire it (tools/deploy_set.py RETIRED)".
- SkyyGear keeps working. SkyyRolls ignores migrated items because they have no `SkyyRolls` key.

---

## 9. Config rows (tools/skyycfg.py kit 1.1) and player switches

### 9.1 Kit call

- `CFG.emit(pool, PKG, MOD="SkyyGear", TITLE="Gear", VERSION, NODE="skyygear.admin", CATS, ROWS, FILES=["Skyy_SkyyGear/config.properties"],
  RELOAD="GearCfg.load", KEEP=10, DEFAULTS={...})`. `KEEP=10` = LOCKED 2026-09-25 (OPEN-QUESTIONS Server Setup 3: 10 old file versions;
  the kit default is still 20 until RESUME step 6).
- Publish at the end of `setup()` after `GearCfg.load`. Every row is `live` unless marked. Tables use `reload@` bindings on key prefixes,
  the SkyyRolls 0.1.5 form. Kit 1.1 checks hand-edited table lines too.

### 9.2 Rows

Categories: `general` General, `rarity` Rarity, `levels` Levels, `stats` Stats, `costs` Costs, `drops` Drops + craft, `combat` Combat,
`migrate` Migration. Every number below is a PLACEHOLDER default. Each row's help line (max 100 characters) says "placeholder - Skyy
tunes this" where that applies. `danger` = the kit's confirm step. It is set on money, rates, caps and curves, the LOCKED list of
changes that ask for a confirm (OPEN-QUESTIONS Server Setup 2), and on every `part.*` switch.

| key | label | cat | type | default | min-max | opts / unit | flags |
|---|---|---|---|---|---|---|---|
| `part.gate` | Level requirement check | general | bool | true | | | `part,danger` |
| `part.stats` | Gear stats in combat | general | bool | true | | | `part,danger` |
| `part.craft` | Roll crafted gear | general | bool | true | | | `part,danger` |
| `part.drops` | Unidentified mob drops | general | bool | true | | | `part,danger` |
| `part.chests` | Unidentified chest loot | general | bool | true | | | `part,danger` |
| `identify.command` | /identify command | general | bool | true | | | |
| `gear.exclude` | Weapon prefixes that are not gear | general | text | the 1.3 list | 0-2000 | | `adv` |
| `pool.later` | Roll coming-later stats | stats | bool | true | | | |
| `rarity` | Modifiers and roll power by rarity | rarity | table | 2.2 | 0-1000 | `int;none;Mods|Low %|High %` | `danger` |
| `stat` | Stat max and weight | stats | table | 4.2 | 0-100000 | `int;none;Max at 100%|Weight` | `danger`, `check=GearCfg.checkStat` (soft question, below) |
| `stat.levelFloor` | Modifier power at item level 0 | stats | int | 25 | 1-100 | `%` (100 = no level scaling) | `danger` |
| `stat.levelFull` | Item level with full modifier power | stats | int | 50 | 1-100 | | `danger` |
| `odds` | Rarity odds (weights) | drops | table | 5.3 / 5.5 | 0-1000000 | `dec;none;Craft|Mob|Chest` | `danger` |
| `smith.perLevel` | Smithing rarity per level | drops | dec | 0.5 | 0-100 | `%` | `danger` |
| `smith.cap` | Smithing rarity cap | drops | dec | 50 | 0-100 | `%` | `danger` |
| `craft.maxRarity` | Best rarity from crafting | drops | choice | fabled | | `normal|Normal,unique|Unique,rare|Rare,legendary|Legendary,fabled|Fabled,mythic|Mythic` | `danger` |
| `level.material` | Level by material | levels | table | 3.2 | 0-100 | `int;type;Level` | |
| `level.item` | Level by item | levels | table | (empty) | 0-100 | `int;held;Level` | |
| `level.vanilla` | Use Hytale item level otherwise | levels | bool | true | | | |
| `level.default` | Level when nothing matches | levels | int | 0 | 0-100 | | |
| `level.noSkills` | Without SkyySkills | levels | choice | pass | | `pass|Allow all,block|Block` | |
| `level.armorNative` | Under-level armor loses Hytale stats | levels | bool | true | | | |
| `cost.reforge` | Reforge cost | costs | table | 5.4 | 0-1e12 | `int;none;Base|Per level` / coins | `danger` |
| `cost.identify` | Identify cost | costs | table | 5.7 | 0-1e12 | `int;none;Base|Per level` / coins | `danger` |
| `xp.reforge` | Smithing XP per reforge | costs | table | 5.4 | 0-100000 | `int;none;XP` | `danger` |
| `reforge.names` | Reforge names | costs | text | `Sharp,Heroic,Spicy,Gentle,Odd,Fast,Epic,Withered` | 0-2000 | | (check: no rarity name) |
| `combat.strPer` | Damage per Strength | combat | dec | 1.0 | 0-100 | `%` | `danger` |
| `combat.mpPer` | Spell damage per Magical Power | combat | dec | 1.0 | 0-100 | `%` | `danger` |
| `combat.defScale` | Defense curve (100 = SkyBlock) | combat | int | 100 | 1-100000 | | `danger` |
| `crit.base` | Base Crit Chance | combat | dec | 0 | 0-1000 | `%` | `danger` |
| `crit.baseDamage` | Base Crit Damage | combat | dec | 0 | 0-10000 | `%` | `danger` |
| `steal.windowS` | Life / Mana Steal window | combat | int | 3 | 1-60 | `s` | |
| `regen.periodMs` | Regen tick | combat | int | 2000 | 250-60000 | `ms` | |
| `speed.per` | Speed per point | combat | dec | 1.0 | 0-100 | `%` | `danger` |
| `migrate.by` | Old SkyyRolls rarity from | migrate | choice | stats | | `stats|Roll strength,roll|Roll quality,item|Item colour` | `new,danger` |
| `migrate.map` | Score needed per rarity | migrate | table | 1.6 | 0-100 | `int;none;Min score %` | `new,danger` |
| `migrate.maxRarity` | Best rarity for old SkyyRolls items | migrate | choice | fabled | | `normal|Normal,unique|Unique,rare|Rare,legendary|Legendary,fabled|Fabled` | `new,danger` |

- The kit build checks row keys, label lengths and help lengths.
- `GearCfg.check*` hooks refuse:
  - unknown rarity ids in the rarity tables;
  - unknown stat keys in `stat`;
  - `high < low` in `rarity`;
  - a rarity name in `reforge.names`.
- **Typo guard for `stat` (review finding E10), a soft warning, never a block:** `GearCfg.checkStat` answers the kit's `?<question>`
  form when a `max` is more than 4 x its built-in default, or 0 while the default is above 0 (4 x is a technical constant, not a
  balance number): "Strength max 2500 is 100 x the default 25 - every Strength roll on new items changes. Save anyway?". In game the
  admin confirms or fixes the typo. A hand-edited line has nobody to ask, and the kit then accepts it (VERIFIED `tools/skyycfg.py`
  `handChecks`: a `?` answer counts as passed), so `GearCfg.load` logs one WARN per such stat instead.

### 9.3 Player switches (research/Settings-Spec.md 1.2-1.3; category `combat`; all default ON; only the message is gated)

| key | label | help |
|---|---|---|
| `gear.blockedPopup` | Gear level popups | Popup when a weapon is too high level or unidentified |
| `gear.armorWarn` | Armor level warning | Chat line when armor gives no stats because of its level |
| `gear.notices` | Gear update notices | One-time line when your old rolled items move to the new gear system |

- Registered with `regSetting(...)` in `setup()`, and read with `notifyOn(u, key)`.
- They are registered with 6 elements (no permission node), so SkyyMenu 0.3.3's permission-based visibility (7.3.2 item 5) shows them
  to every player.
- The check sits before the message's own throttle timestamp (Settings-Spec 1.3). Blocks, rolls and refunds never depend on a switch.

---

## 10. Anti-exploit

| Risk | Defence |
|---|---|
| Reroll farming | Every reforge costs coins (rarity + level table). Rarity never changes on reforge. There is no free preview and no undo. 400 ms click guard. Smithing XP per reforge goes through SkyySkills' per-call and per-minute caps. The log records `rfN` and each coin TAKE |
| Identify / reforge dupes | World thread only. The page never holds an item copy; it re-reads the slot at click time. Same id + same fingerprint + stack size 1 + profile epoch unchanged + not `profile:busy`, else refused. The new stack replaces the old one in the **same slot** in one `setItemStackForSlot`. Coins first, refund on failure, both logged |
| Identify scumming | Modifiers roll only when paid, with SecureRandom. Nothing is stored before identify (and nothing leaks to modded clients). Identify is final |
| Laundering plain gear into unidentified random rarity | Tagging only touches gear stacks with **no** document. Every gear stack a player ever held carries one (legacy stamp, 1.5), and every stack a player throws is stamped in the drop event itself (GearThrowSys, VERIFIED `ItemUtils.throwItem` -> `DropItemEvent$Drop`), so even an item received a moment ago cannot be thrown undocumented. A pending craft only holds back its own item id, for at most `PENDING_MAX_MS` (review finding E3). The mob window is one tick at the death spot. Chest tagging happens at generation inside the engine's own add |
| Crafting loops (craft, salvage, craft for a high rarity) | Every craft consumes the full recipe. Salvage returns far less: VERIFIED `Salvage_Weapon_Sword_Iron` gives 2 Iron **Ore** + 1 Light Hide + 1 Linen Scrap for a sword that costs 6 Iron **Bars** + 3 Light Leather + 3 Linen Scrap (187 gear salvage recipes in Assets.zip). Modifier power scales with item level (2.2, `stat.levelFloor`), so the cheap recipes (Crude, Wood: level 0) roll weak lines at any rarity and are not worth farming; the recipes worth farming cost real materials (review finding E9). `craft.maxRarity` = Fabled (no crafted Mythic). Smithing only steps one tier. Gear is not on the bazaar, so SkyyBazaar's no-money-loop proof is untouched |
| Crafted-roll theft (another item moved into the diff window) | The diff counts only stacks absent from the pre-craft identity snapshot, with no document, **that look exactly like a fresh output** (no metadata beyond the recipe output's, full durability), capped at the job's output count, so a craft never gives more rolls than items and a roll can only land on a stack identical to the crafted one (review finding E1). The stamp holds back only that item id, for at most `PENDING_MAX_MS` |
| Unidentified items traded or sold | Allowed by default (Wynn-style). The rarity and level are visible, so the buyer knows what they pay for. The AH shows "Unidentified" (Q6) |
| Mob farming | SkyyGear adds **no** drops. Rates are Hytale's drop lists. It only tags what already drops. Identify costs coins that scale with rarity and level (a coin sink) |
| Bow / weapon swap tricks | ShotTrack launch record plus SkyyClasses' shot window. Stats and the gate come from the weapon that launched the projectile |
| Off-hand weapon | The gate checks the main hand AND the active utility item (the Kunai is `Utility.Usable`, VERIFIED), the SkyyClasses DamageLock rule (review finding E7). Only the main hand gives stats |
| Class change mid-fight | Every gate lookup compares `profile:epoch` and `class:skill` with the cached pair and re-reads the levels at once on a change; no stale window (review finding E2) |
| Old SkyyRolls items: rush reforges before the swap for a high rarity | Migrated rarity comes from the stats, not the independent Roll Quality (VERIFIED `nextInt(101)`): about 0.7 % Fabled per SkyyRolls reforge instead of 10.9 %, plus the `migrate.maxRarity` cap (Q20; review findings E6, E8) |
| Config typo blows up a stat | `danger` confirm on money, rate, cap and curve rows (LOCKED list), plus a soft question when a `stat` max is more than 4 x its default; a hand-edited line logs a WARN (review finding E10) |
| AH rolls caveat mixing items | `gear:fn:sig` hashes the item id and quality too (review finding E4); the AH caveat already groups by item id |
| Under-level armor timing | Resistance is recomputed per hit from the live armor container. Only the Health counter waits for the 1 s tick (harmless: it can only lower max Health) |
| Crit abuse | Overcrit at most once per hit (LOCKED "always doubles the crit"). Attack Speed and Ferocity caps are enforced when those go live |
| Profile switch / crash recovery dupes | No inventory write while `profile:busy`. Every change is in place in the same slot. SkyyProfiles snapshots copy metadata opaquely |
| Admin tools | `/gear give/reroll/identify/rarity` need `skyygear.admin` and are logged with the admin's name |

---

## 11. Test plan

### 11.1 Static and bare JVM (before any deploy)

1. `python SkyyGear/build_skyygear_0.1.py` ends with `assembled ...SkyyGear-0.1.jar`, and `python tools/ci/lint.py` reports 0 fails.
   No `--deploy`; `tools/deploy_set.py --check` only.
2. Build asserts:
   - the 7 quality JSONs and lang lines are in the jar and every texture path exists in Assets.zip;
   - every `level.material` token matches at least one Assets item;
   - the class kit items resolve to level 0;
   - the stat table keys are unique and match section 4;
   - `reforge.names` holds no rarity name;
   - UI ids have no underscores;
   - no `ItemGridSlot` takes anything but `new ItemStack(id, qty)` (grep assert);
   - every probe (`B.probe`) passes: `ItemStack.withQuality`, `Item.getItemLevel`, `ItemComponent.setItemStack`,
     `DamageSystems$ArmorDamageReduction.getResistanceModifiers`, `NPCDamageSystems$DropDeathItems`, `StashPlugin$StashSystem`,
     `CraftRecipeEvent$Post`, `DropItemEvent$Drop.setItemStack`, `InventoryComponent$Utility.getActiveItem`,
     `EntityStatMap.putModifier`;
   - `GATE_BY_KIND` holds combat -> class, mining -> Mining, foraging -> Foraging, farming -> Farming, and every tool family of 1.6
     maps to a kind;
   - the vanilla style names and textures 5.8 uses exist in Assets.zip (`Common.ui` constants, `Common/ContainerPatch.png`, ...);
   - every row flagged by the LOCKED confirm list carries `danger` (9.2).
3. Bare-JVM harness (scratch under `tools/dev/scratch/gear-<part>/`, TEMP/TMP there, `-XX:-UsePerfData`, deleted after):
   - document round trip through `ItemStack.CODEC`, including quality;
   - the migration table on 12 sample SkyyRolls documents (zero stats dropped, clashing reforge names removed, `old` kept, rarity from
     the stat score for `stats`, from quality for `roll`, capped by `migrate.maxRarity`; a max-stat item with quality 3 maps to Fabled
     under `stats`, a zero-stat item with quality 100 maps to Normal);
   - 100,000 rolls per rarity inside the configured count and range, at item levels 0, 20 and 50 (the level factor, 2.2);
   - odds histogram within 1 % of the weights;
   - identify and reforge cost formulas;
   - `gear:fn:describe` lines for identified, unidentified, legacy and migrated items (including a migrated pickaxe: kind `mining`,
     gate line "Mining Lv. N (coming later: gathering gear)");
   - `gear:fn:sig` differs for an unidentified Rare Iron Sword and an unidentified Rare Wood Wand;
   - the tooltip sig changes when the owner's level goes 12 -> 18 below a requirement of 20, and not when it goes 25 -> 30 above it;
   - the craft candidate rule: a worn copy or a copy with metadata is never picked, and the count never exceeds the output count;
   - the copied armor-reduction formula equals the engine's `ArmorDamageReduction` for the full container on 50 random armor sets;
   - `python tools/skyycfg_test.py` still passes and the SkyyGear schema builds.

### 11.2 In game, solo (Skyy)

1. Join with SkyyRolls retired. Old rolled items show SkyyGear lines, a rarity frame and a level. The migration notice appears once.
   `/gear read` shows `src:"rolls"` and `old`.
2. Plain old gear shows "Normal", a level line and no modifiers. `/reforge` gives it one modifier and takes coins. Smithing XP shows up
   on `/skills`.
3. Craft an iron sword at a Weapon Bench: rolled rarity and modifiers. Repeat with `/craft` (the SkyySacks version with the hook,
   7.3.3). Craft a Crude sword several times: its lines are clearly weaker than the iron sword's at the same rarity (level factor).
4. Level gate:
   - a Crude kit weapon works at skill 0;
   - `/gear level 99` on the held sword: hits do nothing, the popup appears, and the throttle holds at 1.5 s;
   - wear Mithril armor at a low level: the chat line appears, max Health drops by the piece's Health, and a mob's hit hurts as much as
     without the piece;
   - level the gate skill while still below a requirement (e.g. with `/skills xp`): the tooltip's "(you: N)" follows within 1 s;
   - `/classadmin set` to another class (test world without SkyyProfiles, or a profile with no class): the very next hit is judged by
     the new class's skill.
5. Kill mobs until gear drops: it is unidentified with its rarity visible. It cannot hurt anything, and worn it gives nothing.
   `/identify` reveals it and charges coins. "Identify all" works.
6. Open a fresh world loot chest (new chunk): its gear is unidentified.
7. Live stats:
   - a Strength and a Crit Chance roll change the damage done to a training mob (log line in debug mode);
   - Speed changes the walk speed;
   - Health Regen heals every 2 s;
   - Life Steal heals after hits.
8. Server Setup -> Gear: change the Iron level to 5. The tooltip updates on the next scan and the gate opens.
9. SkyyMenu 0.3.3: the Reforge (25) and Identify (26) tiles work; the Settings torch sits at slot 39 left of Mods (40); slot 51 is
   empty; the Mods page lists SkyyGear and no SkyyRolls.
10. The Reforge and Identify pages look like the vanilla item-repair page (frame, title bar, buttons, row style, button sounds), fit
    the screen at 1080 high, and Mythic names are readable.
11. SkyyAuctions 0.1.2: a 48h listing charges twice the listing fee (a 50,000 listing for 48h costs 1,000 = twice the 1 % fee of 500,
    not 500 + 1,200); a 24h listing still costs 500 + 350. A Magic Bag and the Accessory Bag cannot be listed ("off the market").
    Gear rows show the rarity colour, the rarity filter lists Normal to Mythic + Set, and an unidentified item says "Unidentified
    (Rare, Lv 20)".

### 11.3 Only the game can prove (INFERRED items)

1. Plugin-added ItemQuality assets render (frame + label colour). Otherwise the fallback: Name colour only.
2. `ItemGridSlot` with `new ItemStack(id,1).withQuality(idx)` does not disconnect. Until proven, keep it OFF.
3. The crafted-output diff finds the new stack on both the instant and the queued bench path.
4. The death-drop mark and match happen in the same tick, including a corpse that drops after its death animation.
5. The chest AFTER-Stash tag sees the rolled items.
6. The negative Health counter exactly cancels an armor piece's Health (max Health readout).
7. The skyymove source `gear.armor` stacks with Acrobatics and talismans as HANDOFF's layer rule says.
8. `DropItemEvent$Drop` reaches SkyyGear's event system when a player drops an item (Q-key drop and dragging out of the inventory):
   a freshly traded undocumented gear item lands on the ground stamped Normal (`/gear read` after picking it up).
9. A gear Kunai in the utility slot is gated (SkyyClasses off or an Assassin-enabled test config).

### 11.4 Two players (Skyy + a NON-op friend)

1. The friend can run `/reforge`, `/identify` and `/gear`, and cannot run `/gear give` or `/gear reroll`.
2. `/trade` an unidentified item: it arrives unidentified with the same rarity. List it on the AH: filtered under its rarity, shown as
   "Unidentified".
3. Two players kill the same mob: its drops are tagged once, and each drop only once.
4. Profile switch mid-page (Reforge open): the forge is refused with the epoch message and no coins are lost.
5. Laundering attempt: the friend kills a mob while Skyy spam-crafts gear at a bench and, in the same moment, throws a gear item
   received by `/trade` a second earlier onto the dying mob. The thrown item stays Normal (never unidentified); the mob's own drops
   are tagged as usual.
6. AH profiles: Skyy lists an item on profile 1, switches to profile 2 and buys it (allowed, LOCKED); on profile 1 the buy is refused
   ("That is your own listing"). The friend buys another listing normally.
7. Settings visibility: the non-op friend's `/settings` shows no admin-only rows (none greyed out); Skyy (op) sees them. Both see the
   three Gear switches.

---

## 12. Open questions for Skyy (each has a working default)

| # | Question | Default in 0.1 |
|---|---|---|
| Q1 | All placeholder numbers: modifier count and power per rarity, stat max values, odds, Smithing curve, level table, identify and reforge costs, Smithing XP per reforge, Strength / Magical Power / Defense / Speed per point, the migration score table | the tables in sections 2-5 and 1.6, editable in Server Setup -> Gear |
| Q2 | Old SkyyRolls items: rarity from how strong their rolls are, from their old "Roll Quality" number, or from the item's old colour (tier)? The Roll Quality was a separate random number that says nothing about the item's power (1.6) | roll strength (`migrate.by = stats`; was Roll Quality before the review) |
| Q3 | Should a rolled Normal have 1 modifier (so reforging plain gear gives something), or 0 like Wynn? | 1 |
| Q4 | Should "coming later" stats roll now (shown greyed), or only live stats until they work? | they roll (`pool.later = true`) |
| Q5 | Can crafting ever make a Mythic? | no, best is Fabled |
| Q6 | Unidentified items: tradeable and sellable on the AH? | yes |
| Q7 | Hide what an unidentified item is (a generic mystery icon, Wynn-style) instead of showing the real icon? | no: real icon, "Unidentified <item>" name |
| Q8 | Slots the catalog does not name: True Damage, Exploding, Poison, Knockback on weapons only? Defense on armor only? Life Steal and Health Regen on both? | as written in 4.2 |
| Q9 | Are shields gear (rarity + level)? | no, not in 0.1 |
| Q10 | Rolled tools from SkyyRolls: keep lines greyed "(coming later)" and refuse `/reforge` on tools until gathering gear? And is a shovel mining gear (gate Mining)? | yes; shovel = mining |
| Q11 | Level table: Bronze below Iron (your order) although Hytale ranks Bronze higher? Onyxium equal to Mithril (both 50)? | yes and yes |
| Q12 | Can a reforge ever raise rarity? | no |
| Q13 | Players without a class count as level 0 for gear | yes |
| Q14 | Gear from breakable pots and barrels: unidentified too? | no (stays Normal) |
| Q15 | Loot Bonus, Loot Quality, Stealing, Trophy Hunter, XP Bonus: which gear do they roll on? | not in the 0.1 pool |
| Q16 | Mana Steal and Magical Power on non-spell weapons (a Warrior has no spells yet)? | spell weapons only; armor can roll Magical Power "(spells)" |
| Q17 | Should SkyyGear Defense also reduce fall, fire and drowning damage? | no, only hits from mobs and players |
| Q18 | Armor above your level "gives no stats": does that also switch off Hytale's own Health and protection on the piece, or only SkyyGear's modifiers? "Everything" needs a hand-kept copy of the engine's armor formula and still misses 6 rarely used vanilla armor effects (3.5 part 4) | everything (`level.armorNative = true`; `false` = modifiers only) |
| Q19 | Should modifier strength grow with the item's level, so a level-0 Crude sword rolls weaker lines than a Mithril sword of the same rarity? How weak at level 0, and at which level is it full? | yes: 25 % at level 0, full at level 50 (`stat.levelFloor`, `stat.levelFull`; 100 % turns it off) |
| Q20 | Best rarity an old SkyyRolls item can get when it moves over | Fabled (`migrate.maxRarity`) |
| Q21 | Identify tile at menu slot 26 (right of Reforge) with a purple crystal icon? | yes |

---

## 13. Review notes (2026-09-28)

Two reviews of this spec ran on 2026-09-25 (workflow `skywynn-skygear-stage1`: a feasibility + faithfulness review, F1-F3, and an
exploit + economy review, E1-E10). Each finding was checked on 2026-09-28 against the live scripts, `HytaleServer.jar` and Assets.zip
before it was applied. Verdicts:

| # | Finding (short) | Verdict | What changed / why not |
|---|---|---|---|
| F1 | "No stats" on under-level armor also cancels Hytale's own Health and armor, a big commitment that was not an open question | **Applied** | Q18 added; the default stays "everything" (3.5 intro, section 0). `level.armorNative` already gives the narrow reading in game |
| F2 | Section 0 missed Raw Thunder / Raw Water / Raw Elemental Damage | **Applied** | Added to the live-stats bullet |
| F3 | The catalog's Intelligence (SB) and Mana (SB) Keep rows are not mentioned | **Applied** | One note in 4.2: they describe Hytale's mana system, not rollable IDs (catalog L134, L136; change note 18) |
| E1 | Craft rolls found by diffing; another item moved in during the window gets the roll "for free" | **Applied in part** | Rejected: "for free". The cap (`outputQty x quantity`) already means a craft never yields more rolls than items. Real gap: the roll could land on a different stack (a worn copy, an unmigrated SkyyRolls item). Applied: a candidate must look exactly like a fresh output (no metadata beyond the recipe output's, full durability), plus `PENDING_MAX_MS` (5.1). Rejected: tagging the literal output stack (no hook inside `giveOutput`, and the events carry no stack, VERIFIED) and blocking trade / vault / pickup during a pending craft (needs patches to SkyyEssentials, SkyyVault and a pickup hook, and the candidate rule already makes a swap worthless) |
| E2 | Gate cache refreshed only by the 1 Hz tick and the epoch; a class change leaves a stale window | **Applied** | Every lookup compares `profile:epoch` and `class:skill` with the cached pair and re-reads at once (3.3). Note: players cannot switch class in the live set (`ALLOW_SWITCH = false`, VERIFIED), so only an admin change or a future unlock could use it |
| E3 | Spamming crafts keeps the stamp away from all items, so a new item can be thrown onto a dying mob and tagged | **Applied, extended** | Pending crafts now hold back only their own item id, for at most `PENDING_MAX_MS` (1.5). New: GearThrowSys stamps every player-thrown gear stack in `DropItemEvent$Drop` (VERIFIED: `ItemUtils.throwItem` fires it, `setItemStack` exists), which also closes the ordinary 250 ms scan gap. Test 11.4 #5 |
| E4 | `gear:fn:sig` lacks the item id and quality, so different items can share a sig | **Applied** | Id + quality added (7.1). Severity lower than stated: the AH caveat already groups by item id (`lowestBin(iid, ...)`, VERIFIED) |
| E5 | The tooltip "(you: 12)" goes stale while the player levels below the requirement | **Applied** | The spec contradicted itself (6.3 said `have` was in the sig, the hash list did not). The sig now hashes the rendered owner lines (6.3) |
| E6 | Migrated rarity comes from the Roll Quality, not from the actual stats | **Applied** | VERIFIED: Roll Quality is an independent `nextInt(101)` in every SkyyRolls version. Default `migrate.by = stats` (1.6, Q2) |
| E7 | Off-hand weapon not checked | **Applied** | VERIFIED: the Kunai is `Utility.Usable`; SkyyClasses already checks `Utility.getActiveItem()`. SkyyGear's gate now does the same (3.4) |
| E8 | Rushing SkyyRolls reforges before the swap to fish quality >= 90 = Fabled | **Applied in part** | The stats mapping cuts the Fabled chance per SkyyRolls reforge from 10.9 % to about 0.7 %, and `migrate.maxRarity` (Q20) can cap it. Rejected: switching SkyyRolls' `/reforge` off before the swap (a SkyyRolls 0.1.6 build for a retiring mod, on a private server, after the stats mapping already removed the incentive) |
| E9 | Craft-reroll farming relies on an unverified vanilla salvage ratio and has no SkyyGear-owned guard | **Applied, different fix** | Salvage VERIFIED (iron sword: 6 bars + 3 leather + 3 linen in, 2 ore + 1 hide + 1 linen out). SkyyGear-owned guard: modifier power scales with item level (2.2, Q19), so the cheap level-0 recipes are worthless to farm. Rejected: a per-recipe craft cooldown or a shrinking Smithing bonus (punishes normal crafting and leaves the root cause: a cheap recipe rolling the same power as an expensive one) |
| E10 | A Server Setup typo in `stat` could reshape every roll | **Applied** | `danger` confirm on money / rate / cap / curve rows (the LOCKED confirm list) and a soft `?` question in `GearCfg.checkStat`; hand-edited lines are accepted by the kit (VERIFIED `handChecks`), so the loader logs a WARN (9.2) |

Other fixes found while checking: the `def` row pointed to Q18 for environment damage (it is Q17); the kit call now uses `KEEP=10`
(LOCKED); the AH rarity-filter fallback must skip `Skyy_` qualities (7.3.1 A4).

---

## Appendix A. Build notes (javassist, engine rules)

- **Script:** `SkyyGear/build_skyygear_0.1.py`, `VERSION = "0.1"`, `B.manifest("SkyyGear", VERSION, ...)` -> display name
  `"0.1 SkyyGear"`, package `com.skyy.gear`, main `SkyyGearPlugin`. Start from SkyyRolls 0.1.5's skeleton: the `@NAME@` placeholder
  helper `J()`, `M/F/C` helpers, and the STATS-table-drives-everything idea.
- **Class order** (methods before callers, one `registerSystem` per class):
  1. pure helpers: `GearCfg` (config + tables), `GearData` (document read, write, migration), `GearRoll`, `GearLevel`, `GearCoins`,
     `GearView` (tooltip + sig), `GearBridge` functions;
  2. `GearGate` (skill cache, popup);
  3. systems: `GearShotTrack` (RefSystem), `GearHitSys` / `GearArmorSys` / `GearTrueSys` (Filter group, ordered around
     `DamageSystems$ArmorDamageReduction` and each other), `GearLeechSys` (Inspect group), `GearTick` (EntityTickingSystem, Player,
     1 s), `GearInvSys` (InventoryChangeEvent), `GearThrowSys` (DropItemEvent$Drop, 1.5), `GearCraftSys` (CraftRecipeEvent$Post),
     `GearDeathMark` (EntityTickingSystem, before DropDeathItems), `GearDropSys` (RefSystem ItemComponent), `GearChestMark` /
     `GearChestTag` (ChunkStore RefSystems around StashSystem);
  4. `GearReady` (PlayerReadyEvent -> refresh task on the world thread);
  5. pages `ReforgePage` and `IdentifyPage` (vanilla look through the shared style helper, 5.8);
  6. commands `ReforgeCmd`, `IdentifyCmd`, `GearCmd` + admin sub-commands;
  7. `SkyyGearPlugin`.
- **javassist limits:** no lambdas, generics, varargs, autoboxing, enhanced-for, inner classes, String switch or
  try-with-resources. A `synchronized` block holds one call. f-string braces are doubled.
- **Engine rules:**
  - components, inventory and stats only on the world thread;
  - `PlayerReadyEvent` fires on every world switch, so the refresh must be idempotent;
  - count before and after every item move;
  - ordered registrations fall back to unordered + one WARN when the other plugin is missing.
- **StaticModifier keys** `skyygear_*` are saved with the player, like SkyyAccessories' keys. SkyyGear removes them at 0. Uninstalling
  SkyyGear leaves them (known limit, same as SkyyAccessories and SkyySkills).
- **`setup()` order:**
  1. data dir + `GearCfg.load` (+ the one-time SkyyRolls cost import);
  2. the SkyyRolls-present check;
  3. register systems;
  4. commands;
  5. bridge functions;
  6. `regSetting` x3;
  7. `CFG.emit(...)` publish last;
  8. log `[SkyyGear] ready`.
