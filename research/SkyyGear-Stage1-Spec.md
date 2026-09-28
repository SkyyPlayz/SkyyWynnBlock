# SkyyGear 0.1 (stage 1: combat weapons + armor): build spec

*Written 2026-09-25 from Skyy's answers of the same day (SkyWynn-Decisions.md "Change notes (2026-09-25)" #5 and #6, HANDOFF
BUILDER / STATUS block), SkyyGear-Plan.md locks 1-126 plus the tooltip note, SkyyGear-Stat-Catalog.md (Keep rows), and the live
build scripts (SkyyRolls 0.1.5, SkyyClasses 0.1.6, SkyySkills 0.4.5, SkyyAccessories 0.4.4, SkyyExploration 0.2.1, SkyySacks 0.7.6,
SkyyAuctions 0.1.1, SkyyMenu 0.3.2). Engine facts were checked read-only against `HytaleServer.jar` bytecode and `Assets.zip` JSON on
this machine (tools/dev helpers, scratch under `tools/dev/scratch/gear-spec/`, deleted afterwards). Nothing here is built yet.
The design docs (SkyyGear-Plan.md, SkyyGear-Stat-Catalog.md) were only read.*

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
- **The level checks your class weapon skill.** Archer = Archery, Warrior = Swordsmanship, Mage = Sorcery, Berserker = Fury,
  Priest = Divinity.
  - A weapon above your level deals no damage, and a popup says why. SkyyClasses' weapon lock works the same way. Hytale lets nobody
    cancel a swing itself, so "blocked" means the hit does nothing.
  - Armor above your level still goes on, but gives **no stats at all**. That includes Hytale's own health and protection on the
    piece (section 3.5).
- **Gear you already own stays Normal with no modifiers** until you reforge it. **Crafted** gear rolls its rarity and modifiers when
  you craft it. Your Smithing level raises the chance of a higher rarity.
- **Weapons and armor from mobs and world loot chests drop unidentified.** Their rarity is already set and visible. An unidentified
  weapon cannot hurt anything, and unidentified armor gives nothing. `/identify` opens a page where you pay coins to reveal the
  modifiers. The cost grows with rarity and level.
- **The live stats in 0.1:**
  - Damage %, Strength, Magical Power (spells), Crit Chance, Crit Damage and Overcrit.
  - Flat Earth, Thunder, Water, Fire and Air damage, and True Damage.
  - Defense, Speed, Health Regen, Health Regen %, Stamina Regen, Life Steal and Mana Steal.
  - Attack Speed, Ferocity, Thorns, Poison, Exploding, Knockback, Slow, Weaken, elemental defences and Combat Wisdom are shown on
    items with "(coming later)". They never silently do nothing.
- **Your numbers are still open**, so every number in this spec is a clearly marked **placeholder** you can change in SkyWynn Menu ->
  Server Setup -> Gear:
  - how many modifiers each rarity gets, and how strong they roll;
  - drop and craft odds, and the Smithing bonus;
  - level per material;
  - identify and reforge costs.
- **Other mods this round:**
  - SkyyAuctions 0.1.2: rarity filter + roll line.
  - SkyyMenu 0.3.3: the Mods page text and a new Identify tile.
  - SkyySacks 0.7.7: gear crafted in `/craft` rolls too.
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
| `kind` | string | gear type: `combat` in 0.1; later `mining`, `foraging`, `farming`, `tool`, `equipment`, `accessory`. It picks the modifier pool and the default gate skill | always |
| `r` | string | rarity id: `normal`, `unique`, `rare`, `legendary`, `fabled`, `mythic`, `set` | always |
| `id` | bool | identified. `false` = unidentified: `mods` is empty and is rolled at identify time (5.7) | always |
| `mods` | array of `{s, v}` | modifiers in display order. `s` = stat key (section 4), `v` = int value (percent stats in whole %). Unknown keys are kept and shown by name. A future per-modifier field (`src:"powder"`, `lock:true`) fits inside each entry | always (may be empty) |
| `rf` | string | cosmetic reforge name, shown as a name prefix. Absent = none | on reforge / migration |
| `rfN` | int | how many times it was reforged (anti-exploit log, later Smithing hooks) | on reforge |
| `src` | string | where the data came from: `craft`, `drop` (mob), `chest`, `legacy` (owned before SkyyGear), `rolls` (migrated from SkyyRolls), `admin` | always |
| `at` | long | millis of the last roll, identify or stamp | always |
| `lvl` | int or absent | **explicit** level override (custom items, set items later). Absent = the level table decides at read time (3.1), so tuning the table updates every item | never in 0.1 (admin `/gear level` only) |
| `gate` | string | gate skill: `class` = the owner's class weapon skill (LOCKED for combat gear); later a skill name (`Mining`, `Foraging`, `Farming`, ...) for gathering gear (HANDOFF "GEAR LEVEL CAP BY GEAR TYPE") | always `class` |
| `set` | string or null | set id placeholder. Set bonuses are a later stage | never (null) |
| `old` | document | the original SkyyRolls document, kept for a manual rollback tool (1.6) | migration only |
| `idAt`, `idBy` | long, string | identify time + identifier uuid (log/anti-exploit) | on identify |

**Reserved names (never used for anything else):** `pw` (powder list), `pwMax` (powder slots), `eq` (Equipment slot id), `load`
(loadout tag), `ap` (Accessory Power), `tune`. Stage 1 does not write them.

**Reading rules (every reader: SkyyGear, the bridge, other mods through the bridge):**
1. No `SkyyGear` key and no `SkyyRolls` key -> **Normal, identified, no modifiers, level from the table** (LOCKED: gear players
   already own stays the lowest rarity with no modifiers).
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
- **Never:** `Skyy_*` ids, `Tool_*` (gathering gear is later), and anything else.
- A modifier pool is chosen by slot: "weapon" = a gear `Weapon_*`, "armor" = a gear `Armor_*`. **Spell weapons** = `Weapon_Staff_*`,
  `Weapon_Wand_*` and `Weapon_Spellbook_*`. That is SkyyClasses' prefix idea: the engine has no damage-type flag (VERIFIED, research
  2026-09-25).

### 1.4 How later stages fit (nothing below is built)

| Later stage | How it fits the document |
|---|---|
| Equipment bar (necklace, cloak, ring, belt) | new item ids with `kind:"equipment"` and the reserved `eq` slot. Same rarity, level and `mods`. The pool table gets an "equipment" slot (Earth Damage % and the other Equipment-only rows go there). The gate stays `class` |
| Sets + set bonuses | `r:"set"` + `set:"<setId>"`. A bonus system counts worn pieces with the same `set`. Drop-only and craft-only sets are a per-set flag in a later set table, not on the item |
| Powders | `pw:[...]` + `pwMax`, each powder a flat element line applied like `fFire` (section 4) |
| Gathering gear and tools | `kind:"mining"` (etc.) + `gate:"Mining"`. The level check in 3.3 is already generic: `level(owner, gate) >= requirement` |
| Loadouts / wardrobe | loadouts save item stacks. The document travels with the stack (SkyyProfiles / SkyyVault already copy metadata as an opaque blob, VERIFIED) |
| Accessory Power | accessories are their own mod. `kind:"accessory"` stays free for a later merge |
| Identify NPC | the identify code is a static `Gear.identify(...)` the NPC calls later. `/identify` gets a Server Setup switch `identify.command` |

### 1.5 The "legacy stamp" (why every gear item a player holds gets a document)

SkyyGear must write an `ItemDisplayMetadata` to show the rarity and level lines on any gear item. That is metadata anyway. So the
first time SkyyGear sees an undocumented gear stack **in a player's inventory**, it writes `{v:1, kind:"combat", r:"normal", id:true,
mods:[], src:"legacy", at, gate:"class"}` plus the tooltip. This is the same Normal state as reading rule 1, now written down.

It also closes an exploit. Unidentified tagging (5.5) only touches gear stacks with **no** document. An item that ever sat in a player
inventory under SkyyGear can never be laundered into a random-rarity unidentified drop by throwing it on a dying mob or feeding it to
a looting mob.

When it runs:
- `PlayerReadyEvent` (fires on every world switch): the SkyyRolls `RollsReady -> RollsRefreshTask` shape. It waits out `profile:busy`,
  then makes up to 15 tries 2 s apart.
- `InventoryChangeEvent` (the ECS event SkyySkills' SmeltSys uses): marks the player dirty. One coalesced `world.execute` scan at most
  every 250 ms.
- The scan covers the 6 sections in SkyyRolls' order (hotbar, armor, tools, utility, storage, backpack). It rewrites a stack only when
  its `SkyyGearView.sig` differs.
- Never while `profile:busy:<uuid>` is set.
- Never for a player with a pending craft roll (5.1): the craft task runs first.

### 1.6 Migration of SkyyRolls items (LOCKED: already-rolled items keep their rolls)

SkyyRolls 0.1.5 wrote `"SkyyRolls": {reforge, dmg 0-30, str 0-25, crit 0-15, quality 0-100, rolledAt}` and `"SkyyRollsView": {v,
sig, disp, prev}` (VERIFIED, `build_skyyrolls_0.1.5.py` L587-600, L574-581). SkyyRolls stored **no rarity** of its own. Its colours
came from the item's engine quality. Its `quality` is a 0-100 "Roll Quality".

Migration, on the first stamp scan that sees the stack (1.5), and in memory for any bridge read:

| SkyyRolls field | SkyyGear |
|---|---|
| `quality` (Roll Quality 0-100) | `r` from the table `migrate.map` (**PLACEHOLDER**, section 9): quality >= 90 -> `fabled`, >= 75 -> `legendary`, >= 50 -> `rare`, >= 25 -> `unique`, else `normal`. Never `mythic` or `set`. A config choice `migrate.by` = `roll` (default) or `item` switches to the item's engine quality instead: Junk/Common -> normal, Uncommon -> unique, Rare -> rare, Epic -> legendary, Legendary -> fabled, anything else -> normal (open question Q2) |
| `dmg` | `{s:"dmg", v}` (Damage %) |
| `str` | `{s:"str", v}` (Strength) |
| `crit` | `{s:"cc", v}` (Crit Chance %; SkyyRolls' tooltip label was plain "Crit") |
| a stat that is 0 | dropped |
| `reforge` | `rf`, **except** `Legendary` and `Fabled`, which are now rarity names: those become no prefix |
| whole document | copied into `old` |
| - | `id:true`, `src:"rolls"`, `kind:"combat"` (a rolled `Tool_*` gets `kind:"tool"`, see below), `gate:"class"`, `at` = now |

- The modifier **count and values are kept as they are**, even above the rarity's placeholder count or range ("grandfathered"). A
  reforge replaces them with a normal roll for that rarity.
- The top-level `SkyyRolls` and `SkyyRollsView` keys are removed. SkyyGear's view `prev` = the old `SkyyRollsView.prev` (the vanilla
  display from before SkyyRolls).
- Tools rolled by SkyyRolls keep their document with `kind:"tool"`. Their lines are shown with "(coming later: gathering gear)"
  because tools are not stage-1 gear. `/reforge` refuses tools until gathering gear exists (Q10).
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
- `QualityValue` = the # column. It is only used by inventory sorting (`SortType`, VERIFIED: the only caller of `getQualityValue`).
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

**Stat base values** (the value at 100 % power, **PLACEHOLDER**, config table `stat`, columns `max | weight`). The SkyyRolls maxima
anchor dmg 30, str 25 and cc 15, so migrated items sit inside the new ranges. Full list with weights in section 4.2.

### 2.3 How a roll works (craft, reforge, identify, admin give)

1. Pool = the section 4 stats allowed on this slot (weapon or armor, and for `mp` / `msteal` spell weapons only), with `weight > 0`.
   If the switch `pool.later` is OFF, "coming later" stats are left out too.
2. Pick `count` distinct stats from the pool, weighted, without repeats. The count is capped by the pool size.
3. For each stat: `v = randInt(max(1, round(max * low/100)), max(1, round(max * high/100)))`.
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

### 3.3 The gate skill and the check (LOCKED: the class weapon skill, for weapons AND armor)

- `gate:"class"`: the skill name comes from bridge `class:skill:<uuid>` (SkyyClasses, e.g. `"Swordsmanship"`). The number comes from
  `skill:fn:level` `apply(Object[]{UUID, name}) -> Integer` (SkyySkills).
  - If `class:skill` is absent, SkyyGear asks SkyySkills for the pseudo-skill `"Combat"`. SkyySkills resolves it to the active class
    row (VERIFIED, `SkillFn` L3540-3551).
  - SkyyGear keeps its own copy of the class -> skill map (Archer -> Archery, Warrior -> Swordsmanship, Mage -> Sorcery,
    Berserker -> Fury, Priest -> Divinity, Assassin -> Assassination) only for tooltip text when SkyyClasses is absent.
- **No class** (SkyyClasses present, player classless): level 0. Only level-0 gear works, and the tooltip says "Pick a class" (Q13).
- **No SkyySkills** (the bridge function is missing): the gate cannot be evaluated. `level.noSkills` = `pass` (default: never block;
  the level line is shown grey "Level 20") or `block`.
- The check is generic for later gathering gear: `have = level(owner, gate == "class" ? classSkill : gate)`, `ok = have >= need`.
- Cached per player on the world thread. The cache is refreshed by the 1 Hz GearTick and on profile epoch change. Damage handlers read
  the cache; they never call the bridge per hit.

### 3.4 Weapon above your level (or unidentified): blocked with a popup

The same mechanism as SkyyClasses 0.1.6 `DamageLock` (VERIFIED, docstring L85-110):
- It runs in `GearHitSys`, a `DamageEventSystem` in `DamageModule.get().getFilterDamageGroup()`, `Query.any()`.
- The attacker resolves to a player:
  - melee `Damage$EntitySource` -> `InventoryComponent.getItemInHand(buf, ref)`;
  - projectiles -> SkyyGear's own copy of SkyyClasses' `ShotTrack` (the launch record, so a bow swapped mid-flight is judged by the
    bow; SkyyClasses' shot-window rules are copied verbatim).
- The weapon is gear and (unidentified, or `!ok`) -> `d.setAmount(0)` + `d.setCancelled(true)` + remove the target's
  `KnockbackComponent` (SkyyClasses does all three).
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

- On a hit: the cached skill level.
- Every GearTick (1 s): skill levels are re-read. A change re-renders the level line (6.3).
- On an armor change (`InventoryChangeEvent`): the inactive set is recomputed at once for the resistance path. The Health counter
  catches up on the next 1 s tick.

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
| `def` | Defense | armor | flat | 25 | 10 | **LIVE** | GearArmorSys, player victims, damage with an entity source (mob, player, projectile): `x 100 / (100 + def)` (`combat.defScale` 100 = SkyBlock's curve, **PLACEHOLDER**). Applied after Hytale's armor. Environment damage is untouched (Q18) |
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
   - `T` = the held weapon's modifiers + the modifiers of every active armor piece (weapon-only stats only from the weapon);
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
2. Set `pendingCraft[uuid]`.
3. `world.execute(CraftRollTask)`. It runs after `giveOutput` returns, in the same world task queue (FIFO).
4. The task finds stacks of that id that were not in the snapshot and have no `SkyyGear` document, at most `outputQty x quantity`.
5. Each one is rolled: rarity by the Smithing odds (5.3), `id:true`, `src:"craft"`, modifiers by 2.3.
6. Written into the same slot; `pendingCraft` cleared.

- An output that overflowed to the ground stays undocumented and becomes a Normal item when picked up. That is a loss for the player,
  never a gain; one log line.
- Crafts in creative mode are not rolled (the stamp makes them Normal).

### 5.2 SkyySacks `/craft` (never goes through CraftingManager)

- VERIFIED: SkyySacks gives outputs itself with `SimpleItemContainer.addOrDropItemStack(..., new ItemStack(gid, total))`
  (`build_skyysacks_0.7.6.py` L3370-3386), then reports `skill:fn:craftxp`.
- SkyyGear publishes `gear:fn:roll` (7.1). **SkyySacks 0.7.7** calls it for every output entry that SkyyGear calls gear and gives the
  returned stacks one by one. The `cook:fn:campfire` precedent works the same way.
- Without SkyyGear, or when the call returns null, SkyySacks gives the plain stack exactly as today.
- Until 0.7.7 is deployed, `/craft` gear comes out Normal through the legacy stamp. No exploit, just no roll.

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
  - re-rolls the whole modifier set: count by rarity, values by the rarity's power range (2.3);
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
3. The window is exactly one tick. Items thrown by players carry a document (1.5) and are never touched.

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

### 5.8 Pages (HANDOFF section 2 rules)

- Inline pages only; root Group anchor Width/Height only.
- Page size: Reforge 1100 x 880, Identify 1100 x 880 (inside the verified 1120 x 952).
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
- A tool migrated from SkyyRolls shows its lines with "(coming later: gathering gear)".

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
  the player whose inventory holds the item. The `sig` includes `ok`, the gate skill name and `have`. GearTick re-renders items whose
  flag flipped (level-up, profile switch).
- Items elsewhere keep the text of their last owner. The AH and Trade show their own text via `gear:fn:describe`.
- `sig` = hash of: item id, stack quality, gear document JSON, resolved level, base damage text, owner flag + skill name, config epoch.
  A table change in Server Setup re-renders on the next scan.

### 6.4 Writing rules

- `VIEW_V = 1`. A higher future value forces a re-render.
- `prev` keeps the pre-SkyyGear display, so `/gear clear` restores it.
- The Name line falls back to the item's translation Message when the en-US text has `{params}` (SkyyRolls `nameMsg`, VERIFIED
  L332-341).
- All text is built as `Message.raw(...).color(hex)` children (SkyyRolls `statLine`). Nothing goes through the inline UI parser.

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
| `gear:fn:sig` | `apply(X)` | `String` fingerprint of rarity + identify state + modifiers (AH "rolls differ" caveat) |
| `gear:fn:gate` | `apply(Object[]{UUID, X})` | `Object[]{Boolean ok, String skill, Integer need, Integer have}` (from the cache; a cold cache asks SkyySkills) |
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
| `class:skill:<uuid>`, `class:fn:allowed` | SkyyClasses | gate skill name; skip items the class lock already blocks |
| `skill:fn:level`, `skill:fn:addxp` | SkyySkills | gate levels, Smithing rarity, reforge Smithing XP |
| `coins:fn:get/take/add` | SkyyCoins | identify and reforge |
| `profile:fn:key`, `profile:busy:<uuid>`, `profile:epoch:<uuid>` | SkyyProfiles | per-profile notice flag, write refusal, epoch checks |
| `move:<uuid>` map | skyymove protocol v1 | Speed |
| `settings:fn:get`, `settings:fn:register` | SkyyMenu | player switches |

### 7.3 Compat patches this round

| Mod (live -> next) | Why | Exact change |
|---|---|---|
| **SkyyAuctions 0.1.1 -> 0.1.2** | Its roll line reads the literal key `"SkyyRolls"` (`AhItem.reforge/hasRolls/statLabel/rollsLine`, L1373-1417, 6 call sites). Without a patch the AH shows no roll line and the "rolls are not compared" caveat disappears (cosmetic, not a crash) | 1. `rollsLine(meta)` -> `gear:fn:rollsLine(Object[]{itemId, meta})` when the bridge function exists; else the old SkyyRolls parse (servers without SkyyGear keep working). 2. `hasRolls` -> `gear:fn:sig != null`, and the duplicate-listing caveat compares `gear:fn:sig`. 3. `statLabel` / `reforge` removed (describe covers them). 4. **Rarity filter:** `tiers()` takes the Wynn ladder from `gear:tiers` when present. A listing's tier = `gear:fn:rarity` for gear, else the engine quality as today. `qColor` already reads the stack quality's TextColor, so the new quality assets colour AH rows with no change (VERIFIED L1318-1323). 5. Item page: the unidentified state shows as "Unidentified (Rare, Lv 20)". Listing snapshots stay opaque; nothing to migrate |
| **SkyyMenu 0.3.2 -> 0.3.3** | The Mods page entry describes SkyyRolls (a static dict, L459-464). There is no Identify tile | 1. Replace the SkyyRolls dict with SkyyGear: version 0.1, commands `/reforge`, `/identify`, `/gear`, `/gear give ... (admin)`; config `Skyy_SkyyGear/config.properties`; setup `("0.1", "Gear", "rarities, levels, costs and odds")`. 2. Reforge tile #25 keeps `cmdc:reforge` (same command name). Its text becomes "Put in a weapon or armor piece and pay coins to reroll its modifiers." 3. A new tile "Identify" -> `cmdc:identify` on a free main slot, with an existing Assets icon checked at build like the others. Server Setup -> Gear appears by itself (the menu scans `config:def:*`, VERIFIED) |
| **SkyySacks 0.7.6 -> 0.7.7** | `/craft` hands out plain gear (no `CraftingManager`, VERIFIED), which breaks the LOCKED "crafted gear rolls on craft" for SkyWynn's main crafting path | In the output loop (L3370-3386): when `gear:fn:roll` exists and returns non-null for an entry, give each returned stack with `addOrDropItemStack`. Count `given` from them, log `gear=<n>` in `crafts.log`. Otherwise unchanged. Page grids keep `new ItemStack(id, qty)` |
| SkyyExploration 0.2.1 -> 0.2.2 (optional) | The chest-luck extra roll puts gear straight into the opener's inventory (Normal via the stamp) | Wrap each stack with `gear:fn:unid(Object[]{stack, "chest"})` before `addOrDropItemStack` (L3834-3844) |

SkyyGear 0.1 works without any of them. It only loses the features in the "Why" column.

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
| - | `/gear rarity <id>`, `/gear unid`, `/gear identify`, `/gear level <n or clear>`, `/gear migrate [player]` (runs the stamp/migration scan now and prints counts) | admin |

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
- **Deploy together:** SkyyGear 0.1 + SkyyAuctions 0.1.2 + SkyyMenu 0.3.3 + SkyySacks 0.7.7 (+ SkyyExploration 0.2.2 if built).
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
  RELOAD="GearCfg.load", KEEP=20, DEFAULTS={...})`.
- Publish at the end of `setup()` after `GearCfg.load`. Every row is `live` unless marked. Tables use `reload@` bindings on key prefixes,
  the SkyyRolls 0.1.5 form. Kit 1.1 checks hand-edited table lines too.

### 9.2 Rows

Categories: `general` General, `rarity` Rarity, `levels` Levels, `stats` Stats, `costs` Costs, `drops` Drops + craft, `combat` Combat,
`migrate` Migration. Every number below is a PLACEHOLDER default. Each row's help line (max 100 characters) says "placeholder - Skyy
tunes this" where that applies.

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
| `rarity` | Modifiers and roll power by rarity | rarity | table | 2.2 | 0-1000 | `int;none;Mods|Low %|High %` | |
| `stat` | Stat max and weight | stats | table | 4.2 | 0-100000 | `int;none;Max at 100%|Weight` | |
| `odds` | Rarity odds (weights) | drops | table | 5.3 / 5.5 | 0-1000000 | `dec;none;Craft|Mob|Chest` | |
| `smith.perLevel` | Smithing rarity per level | drops | dec | 0.5 | 0-100 | `%` | |
| `smith.cap` | Smithing rarity cap | drops | dec | 50 | 0-100 | `%` | |
| `craft.maxRarity` | Best rarity from crafting | drops | choice | fabled | | `normal|Normal,unique|Unique,rare|Rare,legendary|Legendary,fabled|Fabled,mythic|Mythic` | |
| `level.material` | Level by material | levels | table | 3.2 | 0-100 | `int;type;Level` | |
| `level.item` | Level by item | levels | table | (empty) | 0-100 | `int;held;Level` | |
| `level.vanilla` | Use Hytale item level otherwise | levels | bool | true | | | |
| `level.default` | Level when nothing matches | levels | int | 0 | 0-100 | | |
| `level.noSkills` | Without SkyySkills | levels | choice | pass | | `pass|Allow all,block|Block` | |
| `level.armorNative` | Under-level armor loses Hytale stats | levels | bool | true | | | |
| `cost.reforge` | Reforge cost | costs | table | 5.4 | 0-1e12 | `int;none;Base|Per level` / coins | |
| `cost.identify` | Identify cost | costs | table | 5.7 | 0-1e12 | `int;none;Base|Per level` / coins | |
| `xp.reforge` | Smithing XP per reforge | costs | table | 5.4 | 0-100000 | `int;none;XP` | |
| `reforge.names` | Reforge names | costs | text | `Sharp,Heroic,Spicy,Gentle,Odd,Fast,Epic,Withered` | 0-2000 | | (check: no rarity name) |
| `combat.strPer` | Damage per Strength | combat | dec | 1.0 | 0-100 | `%` | |
| `combat.mpPer` | Spell damage per Magical Power | combat | dec | 1.0 | 0-100 | `%` | |
| `combat.defScale` | Defense curve (100 = SkyBlock) | combat | int | 100 | 1-100000 | | |
| `crit.base` | Base Crit Chance | combat | dec | 0 | 0-1000 | `%` | |
| `crit.baseDamage` | Base Crit Damage | combat | dec | 0 | 0-10000 | `%` | |
| `steal.windowS` | Life / Mana Steal window | combat | int | 3 | 1-60 | `s` | |
| `regen.periodMs` | Regen tick | combat | int | 2000 | 250-60000 | `ms` | |
| `speed.per` | Speed per point | combat | dec | 1.0 | 0-100 | `%` | |
| `migrate.by` | Old SkyyRolls rarity from | migrate | choice | roll | | `roll|Roll quality,item|Item colour` | `new` |
| `migrate.map` | Roll quality needed per rarity | migrate | table | 1.6 | 0-100 | `int;none;Min roll quality` | `new` |

- The kit build checks row keys, label lengths and help lengths.
- `GearCfg.check*` hooks refuse:
  - unknown rarity ids in the rarity tables;
  - unknown stat keys in `stat`;
  - `high < low` in `rarity`;
  - a rarity name in `reforge.names`.

### 9.3 Player switches (research/Settings-Spec.md 1.2-1.3; category `combat`; all default ON; only the message is gated)

| key | label | help |
|---|---|---|
| `gear.blockedPopup` | Gear level popups | Popup when a weapon is too high level or unidentified |
| `gear.armorWarn` | Armor level warning | Chat line when armor gives no stats because of its level |
| `gear.notices` | Gear update notices | One-time line when your old rolled items move to the new gear system |

- Registered with `regSetting(...)` in `setup()`, and read with `notifyOn(u, key)`.
- The check sits before the message's own throttle timestamp (Settings-Spec 1.3). Blocks, rolls and refunds never depend on a switch.

---

## 10. Anti-exploit

| Risk | Defence |
|---|---|
| Reroll farming | Every reforge costs coins (rarity + level table). Rarity never changes on reforge. There is no free preview and no undo. 400 ms click guard. Smithing XP per reforge goes through SkyySkills' per-call and per-minute caps. The log records `rfN` and each coin TAKE |
| Identify / reforge dupes | World thread only. The page never holds an item copy; it re-reads the slot at click time. Same id + same fingerprint + stack size 1 + profile epoch unchanged + not `profile:busy`, else refused. The new stack replaces the old one in the **same slot** in one `setItemStackForSlot`. Coins first, refund on failure, both logged |
| Identify scumming | Modifiers roll only when paid, with SecureRandom. Nothing is stored before identify (and nothing leaks to modded clients). Identify is final |
| Laundering plain gear into unidentified random rarity | Tagging only touches gear stacks with **no** document. Every gear stack a player ever held carries one (legacy stamp, 1.5). The mob window is one tick at the death spot. Chest tagging happens at generation inside the engine's own add. Player-thrown items are never tagged |
| Crafting loops (craft, salvage, craft for a high rarity) | Every craft consumes the full recipe. Salvage returns less (vanilla). `craft.maxRarity` = Fabled (no crafted Mythic). Smithing only steps one tier. Gear is not on the bazaar, so SkyyBazaar's no-money-loop proof is untouched |
| Crafted-roll theft (a legacy item moved into the diff window) | The diff counts only stacks absent from the pre-craft identity snapshot, with no document, capped at the job's output count. The stamp waits for a pending craft task |
| Unidentified items traded or sold | Allowed by default (Wynn-style). The rarity and level are visible, so the buyer knows what they pay for. The AH shows "Unidentified" (Q6) |
| Mob farming | SkyyGear adds **no** drops. Rates are Hytale's drop lists. It only tags what already drops. Identify costs coins that scale with rarity and level (a coin sink) |
| Bow / weapon swap tricks | ShotTrack launch record plus SkyyClasses' shot window. Stats and the gate come from the weapon that launched the projectile |
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
     `CraftRecipeEvent$Post`, `EntityStatMap.putModifier`.
3. Bare-JVM harness (scratch under `tools/dev/scratch/gear-<part>/`, TEMP/TMP there, `-XX:-UsePerfData`, deleted after):
   - document round trip through `ItemStack.CODEC`, including quality;
   - the migration table on 12 sample SkyyRolls documents (zero stats dropped, clashing reforge names removed, `old` kept);
   - 100,000 rolls per rarity inside the configured count and range;
   - odds histogram within 1 % of the weights;
   - identify and reforge cost formulas;
   - `gear:fn:describe` lines for identified, unidentified, legacy and migrated items;
   - the copied armor-reduction formula equals the engine's `ArmorDamageReduction` for the full container on 50 random armor sets;
   - `python tools/skyycfg_test.py` still passes and the SkyyGear schema builds.

### 11.2 In game, solo (Skyy)

1. Join with SkyyRolls retired. Old rolled items show SkyyGear lines, a rarity frame and a level. The migration notice appears once.
   `/gear read` shows `src:"rolls"` and `old`.
2. Plain old gear shows "Normal", a level line and no modifiers. `/reforge` gives it one modifier and takes coins. Smithing XP shows up
   on `/skills`.
3. Craft an iron sword at a Weapon Bench: rolled rarity and modifiers. Repeat with `/craft` (SkyySacks 0.7.7).
4. Level gate:
   - a Crude kit weapon works at skill 0;
   - `/gear level 99` on the held sword: hits do nothing, the popup appears, and the throttle holds at 1.5 s;
   - wear Mithril armor at a low level: the chat line appears, max Health drops by the piece's Health, and a mob's hit hurts as much as
     without the piece.
5. Kill mobs until gear drops: it is unidentified with its rarity visible. It cannot hurt anything, and worn it gives nothing.
   `/identify` reveals it and charges coins. "Identify all" works.
6. Open a fresh world loot chest (new chunk): its gear is unidentified.
7. Live stats:
   - a Strength and a Crit Chance roll change the damage done to a training mob (log line in debug mode);
   - Speed changes the walk speed;
   - Health Regen heals every 2 s;
   - Life Steal heals after hits.
8. Server Setup -> Gear: change the Iron level to 5. The tooltip updates on the next scan and the gate opens.
9. SkyyMenu: the Reforge and Identify tiles work, and the Mods page lists SkyyGear.

### 11.3 Only the game can prove (INFERRED items)

1. Plugin-added ItemQuality assets render (frame + label colour). Otherwise the fallback: Name colour only.
2. `ItemGridSlot` with `new ItemStack(id,1).withQuality(idx)` does not disconnect. Until proven, keep it OFF.
3. The crafted-output diff finds the new stack on both the instant and the queued bench path.
4. The death-drop mark and match happen in the same tick, including a corpse that drops after its death animation.
5. The chest AFTER-Stash tag sees the rolled items.
6. The negative Health counter exactly cancels an armor piece's Health (max Health readout).
7. The skyymove source `gear.armor` stacks with Acrobatics and talismans as HANDOFF's layer rule says.

### 11.4 Two players (Skyy + a NON-op friend)

1. The friend can run `/reforge`, `/identify` and `/gear`, and cannot run `/gear give` or `/gear reroll`.
2. `/trade` an unidentified item: it arrives unidentified with the same rarity. List it on the AH: filtered under its rarity, shown as
   "Unidentified".
3. Two players kill the same mob: its drops are tagged once, and each drop only once.
4. Profile switch mid-page (Reforge open): the forge is refused with the epoch message and no coins are lost.

---

## 12. Open questions for Skyy (each has a working default)

| # | Question | Default in 0.1 |
|---|---|---|
| Q1 | All placeholder numbers: modifier count and power per rarity, stat max values, odds, Smithing curve, level table, identify and reforge costs, Smithing XP per reforge, Strength / Magical Power / Defense / Speed per point | the tables in sections 2-5, editable in Server Setup -> Gear |
| Q2 | Old SkyyRolls items: rarity from their Roll Quality or from the item's old colour (tier)? | Roll Quality (`migrate.by = roll`) |
| Q3 | Should a rolled Normal have 1 modifier (so reforging plain gear gives something), or 0 like Wynn? | 1 |
| Q4 | Should "coming later" stats roll now (shown greyed), or only live stats until they work? | they roll (`pool.later = true`) |
| Q5 | Can crafting ever make a Mythic? | no, best is Fabled |
| Q6 | Unidentified items: tradeable and sellable on the AH? | yes |
| Q7 | Hide what an unidentified item is (a generic mystery icon, Wynn-style) instead of showing the real icon? | no: real icon, "Unidentified <item>" name |
| Q8 | Slots the catalog does not name: True Damage, Exploding, Poison, Knockback on weapons only? Defense on armor only? Life Steal and Health Regen on both? | as written in 4.2 |
| Q9 | Are shields gear (rarity + level)? | no, not in 0.1 |
| Q10 | Rolled tools from SkyyRolls: keep lines greyed "(coming later)" and refuse `/reforge` on tools until gathering gear? | yes |
| Q11 | Level table: Bronze below Iron (your order) although Hytale ranks Bronze higher? Onyxium equal to Mithril (both 50)? | yes and yes |
| Q12 | Can a reforge ever raise rarity? | no |
| Q13 | Players without a class count as level 0 for gear | yes |
| Q14 | Gear from breakable pots and barrels: unidentified too? | no (stays Normal) |
| Q15 | Loot Bonus, Loot Quality, Stealing, Trophy Hunter, XP Bonus: which gear do they roll on? | not in the 0.1 pool |
| Q16 | Mana Steal and Magical Power on non-spell weapons (a Warrior has no spells yet)? | spell weapons only; armor can roll Magical Power "(spells)" |
| Q17 | Should SkyyGear Defense also reduce fall, fire and drowning damage? | no, only hits from mobs and players |

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
     1 s), `GearInvSys` (InventoryChangeEvent), `GearCraftSys` (CraftRecipeEvent$Post), `GearDeathMark` (EntityTickingSystem, before
     DropDeathItems), `GearDropSys` (RefSystem ItemComponent), `GearChestMark` / `GearChestTag` (ChunkStore RefSystems around
     StashSystem);
  4. `GearReady` (PlayerReadyEvent -> refresh task on the world thread);
  5. pages `ReforgePage` and `IdentifyPage`;
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
