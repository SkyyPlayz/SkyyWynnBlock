# Accessory pack inventory: what a booster accessory can really do today

*Research, 2026-09-30. Nothing was built, committed or deployed. Written for Skyy's request of 2026-09-30: booster accessories
(+Strength, +% movement speed, +Stamina, +Health, +Mana, and more) that start basic and upgrade, found as mob drops and in world loot
chests. This file answers one question: which stats and effects already work in the current pack, so every planned booster works on
day one. It does not design the boosters or pick numbers.*

**Legend.** VERIFIED = read in the live build scripts (the `tools/deploy_set.py` pins) or in Assets.zip on this machine. INFERRED =
strongly implied, not proven. UNVERIFIED = needs a test in the game. Status words used in the tables:

- **LIVE-FED**: works today and an accessory already uses it.
- **LIVE-READY**: the receiving code works today, but no accessory publishes to it yet. A booster must do that.
- **LATER**: not applied anywhere yet (the game does nothing with the number).
- **UNVERIFIED**: the engine path is unproven.

---

## 0. Plain summary

1. **Live today** (SET pins): SkyyAccessories 0.4.5 (live since 2026-09-30 05:55), SkyyGear 0.1, SkyySkills 0.4.7, SkyyTrees 0.2.5,
   SkyyCollections 0.2.4, SkyyExploration 0.2.2, SkyyMenu 0.3.3. An unreleased SkyyGear 0.1.1 script sits in the folder; nothing in this
   file changes with it except where noted.
2. The accessory bag has **9 slots**, one bag per profile. Today's accessories: 25 bench accessories (11 benches), the Omni, and **25
   talismans** (5 families x 5 rarities: Vitality, Endurance, Intelligence, Regeneration, Speed). Only the five talisman families change
   stats. Bench accessories unlock `/craft` recipes and do nothing else (the Campfire one also allows quick inventory cooking).
3. **Working stats a booster can use on day one:** max Health, max Stamina, max Mana, Health regen, movement speed %, jump height %,
   fall damage reduction, Strength, Magical Power (spell hits), Crit Chance, Crit Damage, Damage %, True Damage, flat Earth / Thunder /
   Water / Fire / Air damage, Defense, Life Steal, Mana Steal, and XP % and double-drop % for Mining, Foraging, Farming (Wisdom and
   Fortune). Section 2 has the exact status and where each one is applied.
4. **Not working yet, so boosters must not use them** (Skyy's 2026-09-30 lock: "if its not in the game yet, dont leave it in the list"):
   Attack Speed, Ferocity, Thorns, Exploding, Poison, Knockback, Slow and Weaken Enemy, elemental Defence, Combat Wisdom, Loot Bonus,
   Loot Quality, Stealing, Trophy Hunter, XP Bonus, charged-attack damage, Mana Regen, Stamina Regen on accessories (also locked
   armor-only), Dodge Chance, Spell Cost %, Ability Damage, oxygen, swim speed, Mining Speed and Breaking Power from accessories.
5. **Combat stats (Strength, crits, Defense, steals...) have exactly one door:** the bridge string `gear:extra:<uuid>` that SkyyGear 0.1
   reads (`"str:40,cc:10"`). **Nobody publishes it yet.** SkyyAccessories would be the first publisher.
6. **Biggest gaps:** only 9 bag slots (the plan wants up to 60); the effect code is hard-wired to the 5 existing families; there is no
   Accessory Power code at all; no mod adds items to mob or chest drops; `gear:extra` is one string per player, so two publishers would
   overwrite each other; percent boosters are tiny on the small base pools (Stamina about 10, Mana 10 to 20).
7. **Conflicts to settle with Skyy** (section 5): accessory Speed flat vs percent, Stamina Regen on accessories, what "one per family"
   means for many Strength accessories, the rarity ladder (accessories use vanilla Common to Legendary, gear uses Wynn's ladder), and
   whether accessories need a level requirement.

---

## 1. What exists today

### 1.1 The bag (SkyyAccessories 0.4.5, VERIFIED in `SkyyAccessories/build_skyyaccessories_0.4.5.py`)

| Fact | Value |
|---|---|
| Open it | right-click the Accessory Bag item, or `/accessories` (aliases `acc`, `accbag`; Adventurer permission) |
| Bag item | `Skyy_Accessory_Bag`, Uncommon, Fieldcraft recipe 4 Wood_Trunk + 4 Cotton Scrap, in the SkyyIslands starter kit; blocked on the Auction House |
| Slots | `CAP = 9` storage slots (`slot0..slot8`), config row `slots` 1 to 9, it only limits NEW equips (accessories already in a higher slot stay and count) |
| Storage | `Skyy_SkyyAccessories/bags/<pkey>.properties` (one bag per SkyyProfiles profile, profile 1 = the old `<uuid>` file) |
| How you equip | the bag page lists up to **6** accessories from your inventory (`INV_ROWS = 6`, buttons `eq:0..eq:5`); Equip moves the item into the bag, Unequip gives it back. An item only counts while it is IN the bag |
| One per group | `AccDefs.groupOf`: a talisman family (`T:<family>`) or a bench id. Equipping a higher rarity or tier swaps it in place and hands the lower one back; an equal or lower one is refused. Different groups stack |
| Refusals | retired items, a full bag, `profile:busy` or an unknown profile state (the item never leaves the inventory) |
| Rarity | `AccDefs.rarityOf` 1 to 5 = Common, Uncommon, Rare, Epic, Legendary (vanilla item qualities; colours read from Assets.zip `Server/Item/Qualities`). Bench accessories T1 Common ... T5 and up Legendary. Omni Legendary. Retired items 0 |
| Accessory Power | **not built.** `rarityOf` exists so it can read it later. No `acc:power`, `acc:pct`, `acc:slots`, crystal, tuning or enrichment code or keys exist |
| Admin give command | none (a vanilla `/give` exists, INFERRED from the Collections notes that name it) |

### 1.2 The items (72 item ids in the jar)

| Group | Ids | What it does |
|---|---|---|
| Bench accessories | 25 active (Workbench T1-3, Armor Bench T1-3, Weapon Bench T1-3, Farming Bench T1-7, Furnace T1-2, Tannery T1-2, Arcane Bench, Furniture Bench, Loom, Salvage Bench, Campfire) + 5 retired (Alchemy Bench T1-4, Cooking Bench: kept as items that do nothing) | unlock that bench's recipes in SkyySacks `/craft` via bridge `acc:has`; the Campfire one is quick inventory cooking |
| Omni | `Skyy_Accessory_Omni`, Legendary, recipe = the 11 top-tier bench accessories | counts as every active bench at its top tier |
| Talismans | `Skyy_Talisman_<Family>_<Rarity>`: 5 families x 5 rarities = 25, plus 15 old ids (`_Talisman`, `_Ring`, `_Artifact`, no recipe, count as Uncommon / Rare / Epic) | the only accessories that change stats |

Talisman numbers (defaults, config `bonus.<Family>`, per rarity Common, Uncommon, Rare, Epic, Legendary):

| Family | Effect | Numbers |
|---|---|---|
| Vitality | % of your flat max Health | 2, 4, 6, 8, 10 |
| Endurance | % of your flat max Stamina | 2, 4, 6, 8, 10 |
| Intelligence | % of your flat max Mana | 2, 4, 6, 8, 10 |
| Regeneration | % of max Health healed every `regenEverySeconds` (2 s) | 0.5, 1, 1.5, 2, 3 |
| Speed | % movement speed (accessory percent layer) | 2, 4, 6, 8, 10 |

Upgrade ladder = previous rarity + materials at a Workbench (Common uses 2 crystals + family materials; Rare to Legendary add gems,
bars, essence, and for Legendary one Voidheart). There is no collection gate on these recipes (see section 5, C8).

---

## 2. Stat and effect table: LIVE or COMING LATER

"Where applied" names the class or system that does the work. "Booster feed" says how an accessory would deliver it. Section 3.4 has
the exact formats.

### 2.1 Health, Stamina, Mana, regen

| Stat | Status | Where applied | Booster feed and limits |
|---|---|---|---|
| Max Health | LIVE-FED | `AccEffects.tick` (SkyyAccessories, world thread, once a second per player): an ADDITIVE MAX `StaticModifier` under key `skyyacc_health` = `round(flatMax x pct) / 100`. `flatMax` = the stat type's max + every OTHER additive MAX modifier (skills, trees, armor, Overall Level, gear locks). Vanilla player max is 100 | Vitality uses it. A flat "+N Health" booster can use the same call with its own key. **Catch:** a second accessory key is itself an additive MAX modifier, so Vitality's percent would multiply it (see gap G5) |
| Max Stamina | LIVE-FED | same code, key `skyyacc_stamina`. Vanilla max is 10 | Endurance uses it. 10% of 10 is +1, so percent boosters feel tiny |
| Max Mana | LIVE-FED | same code, key `skyyacc_mana`. Base Mana is 10 (Mage and Priest 20), posted by SkyySkills 0.4.6+ as `skyyskill_basemana`; vanilla type max is 0 | Intelligence uses it. 10% of 10 to 20 is +1 to +2. Casts cost 25 (wand), 50 (Mage staff summon), 100 (spellbook), so any booster below that cannot make a cast work alone |
| Health regen (percent of max) | LIVE-FED | `AccEffects.tick`: every `regenEverySeconds`, `addStatValue(Health, max x pct / 100)` only while 0 < Health < max | Regeneration uses it |
| Health regen (raw points) | LIVE-READY | SkyyGear `GearFx.second`: `hpr x (1 + hprp/100)` every `regen.periodMs` (2000) while alive and below max | `gear:extra` keys `hpr`, `hprp` |
| Stamina Regen | LIVE-READY in code, **locked armor-only** | SkyyGear `GearFx.second` `addStatValue(Stamina, stam)` per period | key `stam` would work, but Decisions row 6.16 says armor only (also Acrobatics and Exploration trees) unless Skyy says otherwise. See C1 |
| Mana Regen | LATER | nothing writes it; vanilla regen is +1 every 0.2 s, paused while charging and for 6 s after damage. SkyyGear has no `mana regen` key | needs new code (the Regeneration pattern: `addStatValue` on a timer). Catalog allows it on accessories and Equipment |
| Mana Steal | LIVE-READY | SkyyGear `GearLeechSys` then `GearFx.manaSteal` (paid out per `steal.windowS`, 3 s) | `msteal`. Only useful to spell users |
| Life Steal | LIVE-READY | SkyyGear `GearLeechSys`: percent of landed damage, healed every 3 s | `lsteal` (whole percent) |
| Oxygen (breath) | UNVERIFIED | the stat exists in Assets (`Server/Entity/Stats/Oxygen.json`); no Skyy code touches it | locked as an accessory effect (change note 16); a MAX modifier like the other pools is INFERRED, not proven |

### 2.2 Movement

| Stat | Status | Where applied | Booster feed and limits |
|---|---|---|---|
| Movement speed, percent layer | LIVE-FED | shared protocol `tools/skyymove.py` (MoveSync appliers in SkyyAccessories, SkyySkills and SkyyGear; SkyyTrees only posts). Accessories post source `accessories.talismans`, layer `pct`. Any mod's applier sums all sources: `factor = clamp((1 + sum flat) x (1 + sum pct), 0.3, 5)`; only `baseSpeed` and `jumpForce` are written | Speed talisman uses it. Acrobatics (+100% at level 100) is the flat layer, so Acrobatics 100 plus a Legendary Speed talisman = x2.2 |
| Movement speed, flat layer | LIVE-READY | SkyyGear posts `gear.armor` (flat) from armor `spd` plus `gear:extra`; `spd x speed.per / 100` of default, `speed.per` = 1.0 | works through `gear:extra spd`, but it lands in the flat layer next to armor, not the accessory percent layer (C2) |
| Jump height | LIVE-READY | MoveSync `jump` field: pct layer = height x (1 + value), clamped to default + 20 blocks | accessories post `jump` 0 today. Locked to skill trees and accessories (row 6.17) |
| Fall damage | LIVE-READY | `fallDamage` field in the same protocol, applied ONCE by the elected owner of `stat:owner:fallDamage` (SkyySkills) in its damage filter; factor clamped 0 to 2, never heals | accessories post none today |
| Swim speed | UNVERIFIED | nothing in the pack touches swimming settings | locked as a separate accessory (note 16); needs an engine check of `MovementSettings` |
| Dodge Chance | LATER | Acrobatics has a dodge PUSH node (`skill:bonus dodge.acrobatics`), not a chance stat | locked "also on dodge accessories", not built |
| Double Jump, Quick Dodge, Sprinter | LIVE, owned by Trees | SkyyTrees nodes through SkyySkills Acrobatics | no accessory input; a booster cannot grant them |

### 2.3 Combat (SkyyGear 0.1, all through one totals function)

Offence stats apply to hits from a gear weapon or bare hands (a held tool or block gives `ok = false` and no offence stats). Hits must
be Physical or Projectile family, or a spell shot. Defense applies to player victims hit by an entity source. A weapon under the
player's level or unidentified does zero damage whatever the accessory says. Master switch: Server Setup "Gear stats in combat"
(`part.stats`, default on). VERIFIED in `build_skyygear_0.1.py` and `research/SkyyGear-Stage1-Spec.md` 4.2-4.3.

| Key | Stat | Status | Where applied | Units and formula (numbers are PLACEHOLDERS) |
|---|---|---|---|---|
| `dmg` | Damage % | LIVE-READY | `GearHitSys` (before Hytale armor) | `x (1 + dmg/100)`, floor -100 |
| `str` | Strength | LIVE-READY | `GearHitSys` | `x (1 + str x combat.strPer/100)`, strPer 1.0: 1 point = +1% on melee, arrows, thrown, staff melee |
| `mp` | Magical Power | LIVE-READY | `GearHitSys` | same with `combat.mpPer`, only on spell shots (wand, staff, spellbook projectiles) |
| `cc` | Crit Chance | LIVE-READY | `GearHitSys` | whole percent, no cap; over 100 = overcrit chance. `crit.base` is 0, so nobody crits without gear or accessories |
| `cd` | Crit Damage | LIVE-READY | `GearHitSys` | crit = `x 2 x (1 + cd/100)`: 0 = double, +100 = 4x |
| - | Overcrit | LIVE (mechanic) | `GearHitSys` | automatic when Crit Chance is over 100 |
| `tdmg` | True Damage | LIVE-READY | `GearTrueSys` (after Defense) | flat, nothing reduces it |
| `fEarth` `fThunder` `fWater` `fFire` `fAir` | flat element damage | LIVE-READY | `GearTrueSys` (after armor, not crit-multiplied) | flat; mobs have no element defence yet, so it lands in full |
| `rThunder` `rWater` `rElem` | raw Thunder, raw Water, raw Elemental | LIVE-READY | same | `rElem` adds its value once per element (5x) |
| `def` | Defense | LIVE-READY | `GearArmorSys` (after Hytale armor) | `x 100 / (100 + def)`; environment damage untouched |
| `lsteal` `msteal` `hpr` `hprp` `stam` | steals and regen | LIVE-READY | see 2.1 | |
| `spd` | Speed | LIVE-READY | see 2.2 | |
| `as` | Attack Speed | LATER | needs the swing-speed mechanism (research/Swing-Speed-Spec.md); cap 150% locked | grey "coming later" |
| `fer` | Ferocity | LATER | needs code-dealt extra hits; caps 300 / 600 locked | |
| `thorns` `expl` `poison` `kb` `slow` `weak` | Thorns, Exploding, Poison, Knockback, Slow Enemy, Weaken Enemy | LATER | | |
| `dEarth` `dThunder` `dWater` `dFire` `dAir` | element Defence | LATER | mobs deal no element damage yet | |
| `cwis` `lbonus` `lquality` `stealing` `trophy` `xpb` | Combat Wisdom, Loot Bonus, Loot Quality, Stealing, Trophy Hunter, XP Bonus | LATER | no reader in SkyySkills or any drop code | |
| - | charged-attack damage | LATER | Skyy's new lock (2026-09-30), SkyyGear 0.1.2, needs a way to detect a charged hit | |
| - | Ability Damage, raw spell damage family, Spell Cost %, Reach, Breaking Power, Mining Spread, Auto Smelt | LATER / no system | no spell or ability system; gathering stats are tree-only or gathering-gear-later | |

**Trap:** `gear:extra` accepts every key in the table, including the LATER ones. They are summed and then ignored (shown "(later)" in
`/gear`). A booster that publishes `as:5` does nothing and says nothing.

### 2.4 Gathering, XP, luck

| Stat | Status | Where applied | Booster feed and limits |
|---|---|---|---|
| Wisdom (XP %) for Mining, Foraging, Farming, Cooking | LIVE-READY | SkyySkills `SkillXp.gain2` reads `skill:bonus:<uuid>` key `xp.<skill>` summed over sources, clamped 0..5, for the skills in `bridge.bonus.xpSkills` (default Mining, Foraging, Farming, Cooking) | post `xp.mining` etc. as a fraction (0.05 = +5%) under an accessory source name. Only XP the player earns counts |
| Fortune (double-drop %) for Mining, Foraging, Farming | LIVE-READY | `Perks.chanceU` reads `dd.<skill>` from the same map, capped by `perk.doubleDropMax` (1.0) | key `dd.mining` etc. (fraction). Foraging doubles only logs |
| Combat, Exploration, Acrobatics, Alchemy, Smithing Wisdom | LATER | not in `bridge.bonus.xpSkills` by default and no feed exists | the skill list is a config row, but other skills are not wired or tested for this; the Combat Wisdom lock expects SkyySkills to read `gear:fn:stats`, not built |
| Mining Speed, Chopping Speed (faster swings) | LIVE, tree-only | SkyyTrees 0.2.3+ swing speed from `tree:fn:bonus`; no external source map | needs a SkyyTrees patch before an accessory can add to it |
| Tree Feller, Vein Burst, Spread | LIVE, tree-only | SkyyTrees abilities | no accessory input |
| Chest luck | LIVE, level-based | SkyyExploration `ExpSkill.luck` = Exploration level x 0.003 + `tree:fn:bonus Exploration.ELuck`, max 0.5 | no accessory input |
| Coins, Magic Find, Trophy Hunter, Pet Luck | LATER | | |

### 2.5 Accessory-system features (locked, not built)

Accessory Power (flat +10 to +25 per accessory by rarity, exact table not set), powers (Tank, Balance, Slayer, Lucky, Fast, Magical,
Combat 15 ladder), tuning, enrichments, more than 9 slots, the crystal table and the old 3/5/8/12/16 draft: **none of it exists in
0.4.5.** Boosters can carry an AP value as data, but nothing adds it up.

### 2.6 Scale reference, so boosters fit the rest of the pack

| Source | Current numbers (most are PLACEHOLDERS) |
|---|---|
| Gear modifier maximum at full power | Damage 30%, Strength 25, Magical Power 25, Crit Chance 15%, Crit Damage 30%, True Damage 5, element 6 each, raw Elemental 3, Mana Steal 3, Life Steal 5%, Raw Health Regen 2, Health Regen 20%, Defense 25, Speed 5, Stamina Regen 2. A rolled value is 30 to 60% (Normal) up to 60 to 130% (Mythic) of that; 1 to 6 modifiers per item by rarity; level 0 gear rolls at 25% power, full power from item level 50 |
| Skill perks per level (defaults) | Foraging +0.1 Health, Farming +0.25 Health, Combat +0.1 Health, Mining +0.05 Stamina, Exploration +0.1 Stamina, Alchemy +0.2 Mana, Overall Level +0.5 Health and +0.2 Mana |
| Tree nodes (max) | Forest Vigor +10 Health, Hearty Harvest +10 Health, Exploration hearts +20 Health, Miner Stamina +3, Acrobatics stamina nodes +8 |
| Flat pools, roughly at level 100 | Health about 185 to 235, Stamina about 35, Mana about 50 to 60 before armor (vanilla cloth armor adds 60 to 100 Mana per set). Derived by adding the defaults above at skill level 100 (the locked cap), not measured; a fresh character has Health 100, Stamina 10, Mana 10 (Mage and Priest 20) |

---

## 3. How a new booster accessory plugs in

### 3.1 Which mod owns it, and where it lives

- **Owner: SkyyAccessories** (bag, item ids, equip rules, per-second effect code, config rows). The stat math stays in the receiving
  mod: SkyyGear for combat, the skyymove protocol for movement, SkyySkills for XP and double drops, the engine for Health, Stamina and
  Mana. The accessory only **publishes** its numbers.
- Booster accessories belong in the **Accessory Bag**. The Equipment bar (necklace, cloak, ring, belt) is a different locked system in
  SkyyGear (`kind:"equipment"`, rolled stats, not built). Do not mix them.
- Accessories are fixed-stat items (no roll, no identify, no reforge). SkyyGear never treats `Skyy_*` ids as gear unless an admin lists
  them in `gear.include`, and the bag item is on SkyyGear's never-gear list.
- Next version rule: SkyyAccessories uses patch scripts. Write `tools/acc_0_5_patch.py` (or the next number) that reads the generated
  `SkyyAccessories/build_skyyaccessories_0.4.5.py` and writes the new script. Edit the patch, never the generated file. Pin the version
  in `tools/deploy_set.py`, run lint, never pass `--deploy`.

### 3.2 Item id rules (important)

- Use **`Skyy_Talisman_<Family>_<Rarity>`** with Rarity one of Common, Uncommon, Rare, Epic, Legendary. `AccDefs.isAccessory`,
  `isTalisman`, `familyOf`, `tierOf`, `groupOf` (`T:<family>`) and `rarityOf` already handle any family name. They publish into
  `acc:tal:<uuid>`, show in the bag, count in SkyyMenu's "N talismans", and SkyyAuctions already files them under ACCESSORIES.
- Do **not** use `Skyy_Accessory_<Name>` for stat items. That prefix is parsed as a bench: `AccDefs.benchOf` turns the tail into a
  bogus bench id, it is published in `acc:has`, and SkyySacks would make a bogus `/craft` tab. (0.2 had exactly this bug.)
- Family names: CamelCase, no underscore, not ending in a rarity word. The family is also the config key `bonus.<Family>`.
- Because of the one-per-family rule, **each booster line is one family**; upgrades replace the lower rarity.
- A family that the code does not know is still equipped and still shown, but `AccDefs.bestTiers` ignores it, so **it silently does
  nothing**. Adding the item is not enough.

### 3.3 Code touch points (today the five families are hard-wired)

| Place | What to change |
|---|---|
| `TALISMANS` table in the build script | one row per family: name, effect word, crystal colour, gem, 5 numbers, 5 recipes. Needs an effect kind (pool, regen, speed, combat, xp...) instead of the fixed five |
| `AccDefs` arrays `VIT END INT REG SPD` and `bonusText` | one numbers array per family (or one table), and the bag page "Bonuses" line, which lists only the five |
| `AccCfg` loader and `BONUS_DEF` | parses `bonus.<Family>` for the five names; new families need loader lines, defaults and the float check |
| `AccEffects.tick` | reads `best[FAM[...]]` for the five; needs a generic loop: sum per stat, then post |
| `CFG_ROWS` `bonus` table | kit row for the new families so admins can tune in Server Setup |
| Tooltip text (`EFFECT` lambdas) | generated from the built-in numbers; config changes never update item text (known, 0.4.4 note) |
| Bag page | 9 slot rows and 6 inventory rows are fixed; more accessories need paging (gap G1) |

### 3.4 Feed paths (what a booster publishes, exact format)

| Effect | Publish to | Format and rules |
|---|---|---|
| Max Health / Stamina / Mana | engine `EntityStatMap` | `putModifier(statIndex, "skyyacc_<key>", new StaticModifier(MAX, ADDITIVE, amount))`, remove at 0. Do NOT use MULTIPLICATIVE: the engine sums all multiplicative amounts (vanilla Meat_Buff 1.05 + ours 1.10 = x2.15). Modifiers are saved with the player, so keys must be removed when unused or the mod is retired. Runs on the world thread, 1 s per player |
| Health regen percent | `addStatValue` | as Regeneration does |
| Speed, jump, fall | `move:<uuid>` map | `MoveSync.post(u, source, "pct", speed, jump, fall)` then `sync`. One entry per source name, one layer per entry, replaced whole each second; all zeros removes it. Sum every bag family into the ONE `accessories.talismans` entry (or a second source name). Fractions: 0.10 = +10%. Fall: -0.25 = 25% less. Skills is the only fall-damage applier |
| Strength, Crit, Defense, Damage %, steals, elements, raw regen, Speed (flat) | `gear:extra:<uuid>` | one `String` value `"str:12,cc:5,def:8"`. Keys = SkyyGear stat keys (2.3). **Whole numbers only**: each part is floored, so `str:2.5` is 2 and a negative part floors toward minus infinity. Publish one summed, rounded part per key. Negative values work (debuffs); each part and each stat total is clamped to +-1,000,000; Damage % floors at -100 and a hit never goes below 0. Unknown keys and bad parts are skipped. SkyyGear parses it once per distinct text and reads it live on every hit, tick and Defense check. Publish the ACTIVE profile (`AccStore.pkey`, republish on `profile:epoch`), remove the key when the total is empty and when the player leaves |
| Wisdom and Fortune | `skill:bonus:<uuid>` | a `ConcurrentHashMap` source name to an immutable `Map{"xp.mining": 0.05, "dd.farming": 0.10}` (fractions). Create the outer map with `putIfAbsent`, replace the source's map when it changes |
| Accessory Power (later) | `acc:power:<uuid>` | planned in SkyyAccessories-Plan technical notes; not built |

All cross-mod calls go through `System.getProperties().get("skyy.bridge")` with `java.lang` types only. `gear:fn:stats` and
`gear:stats:<uuid>` do NOT include `gear:extra` on purpose, so a HUD reading them will not show accessory stats; `/gear` prints them
on a separate "From other mods (gear:extra)" line.

### 3.5 How the existing items and icons are made (VERIFIED)

- Everything is **generated at build time** from Python tables in the build script and written into the jar as plain JSON:
  `Server/Item/Items/Utility/<id>.json` plus lines in `Server/Languages/en-US/server.lang` (`items.<id>.name`,
  `server.items.<id>.name`, and the two `description` keys). No image, model or texture file is copied or shipped.
- Each item JSON holds: `TranslationProperties`, `Categories ["Items.Tools"]`, `Icon`, `Quality`, `Recipe` (inputs plus
  `BenchRequirement` Workbench), `Model`, `Texture`, `IconProperties`, `Tags`, `MaxStack 1`.
- **Talisman look = the vanilla crystal it is made from, by reference.** `visual_of("Ingredient_Crystal_<Colour>")` reads that vanilla
  item and copies only its `Model`, `Texture`, `IconProperties`, `Scale`, `PlayerAnimationsId`, `ItemSoundSetId` as path strings.
  `icon_of` returns the vanilla item's own icon path (crystal icon for Common and Uncommon, gem icon for Rare and up). The build
  asserts every referenced file exists in Assets.zip `Common/` and fails on a typo.
- The bag and bench accessories use a vanilla backpack model and icon; the Omni uses the diamond gem icon.
- `Quality` is a vanilla quality name (Common, Uncommon, Rare, Epic, Legendary), so frames and colours come from the game.
- Recipe inputs are checked against Assets.zip (`need_item`, `mat`: an item id or a resource type id).
- **Visuals still free** (Assets.zip): crystal colours Pink, Purple, White (Red, Yellow, Blue, Green, Cyan are used); gems Diamond
  (Omni icon) and Voidstone (Ruby, Topaz, Sapphire, Emerald, Zephyr are used). More than 3 new families need other vanilla items
  (essences, ingredients, other gems) referenced the same way, or art we make ourselves later.
- Pages follow the vanilla UI kit (`tools/skyyui.py`). No item with metadata may go into an `ItemGridSlot`; accessories have no
  metadata, so they are safe.

### 3.6 Upgrades, config, tooltips

- Upgrade = previous rarity item + materials at a Workbench (same as the talismans). This fits "start basic and upgrade".
- Config: every tunable number gets a kit row (tools/CONFIG-CONTRACT.md); the `bonus` table row is the pattern. A new stat family
  means new table entries, defaults and a loader line (3.3).
- Item text is static at build time; the bag page shows the live numbers.

### 3.7 Getting them: crafted, mob drops, world chests

| Source | What exists today | What a booster needs |
|---|---|---|
| Crafted | Workbench recipes work today. Collection gating of craft tiers (lock 64) is **not wired** to the vanilla Workbench; `coll:recipes` only lists recipes in the `/craft` Collections tab (explicit table rows `<Coll>.<tier>=<RecipeId>`; the auto rule is off) | optional: explicit rows, plus a decision on whether Workbench recipes stay open |
| Mob drops | **No Skyy mod adds items to a mob drop table.** Vanilla tables are JSON in `Server/Drops/NPCs` (270 files). Two proven hook patterns exist: SkyyCollections `CollKillSys` (DeathComponent on an NPC, killer = player behind `Damage.EntitySource`, `Role.getDropListId` then `ItemModule.getRandomItemDrops`) and SkyyGear `GearDeathMark` + `GearDropSys` (runs before `NPCDamageSystems$DropDeathItems`, tags items spawned at the death spot) | a new kill system (SkyyAccessories or a small shared loot mod) with a config table: mob id or group to accessory id, chance, rarity. Give with `addOrDropItemStack` storage first. The same roll is where Loot Bonus and Trophy Hunter would hook later |
| World loot chests | SkyyExploration registers world loot chests and their drop list (`ChestReg`), detects the first open per player, and rolls ONE extra copy of the chest's own drop list into the opener's inventory (chance = level x 0.003, cap 0.5). SkyyGear's chest hook only tags gear that the stash roll already put in; it adds nothing | a second, Skyy-made drop list (new asset file listing accessory ids) rolled at that first-open moment, or a hook in the engine stash system. A mod-shipped drop list resolving through `ItemModule.getRandomItemDrops` is INFERRED, **UNVERIFIED**. Replacing vanilla drop tables would mean shipping edited copies of game data, which the copy rule discourages |
| Testing | SkyyAccessories has no give command | vanilla `/give <item id>`, or add an admin `/acc give` (admin sub-command rules: `requirePermission` + `setPermissionGroups(new String[0])`) |

---

## 4. Gaps a booster system needs

Priority: **B** = blocks a real booster system, **I** = important, **N** = nice to have.

| # | Pri | Gap | Detail |
|---|---|---|---|
| G1 | B | **Bag capacity and UI** | 9 slots, `CAP = 9`, config max 9. One per family means N booster stats need N slots, and 16 families (11 bench + 5 talisman) already exceed 9. The plan wants 9 to 60 (collections, skills, coins, quests); none of it is built. The equip list shows 6 inventory rows and the window is sized for 9; needs paging and a new size |
| G2 | B | **Effect code hard-wired to 5 families** | see 3.3; needs a generic stat table (family, stat kind, target key, 5 values) before adding more than a couple of lines |
| G3 | B | **No publisher for `gear:extra`** | the only door for Strength, crits, Defense, steals. Needs: publish per second for the active profile, remove when empty, prune on leave, whole-number rounding, LATER-key guard (build-time assert that a booster only uses the 21 live keys) |
| G4 | I | **`gear:extra` is ONE string per player** | two publishers overwrite each other (Accessory Power powers, Equipment bar, class trees "raise base Strength", powders are all named as future publishers). Fix in SkyyGear: also accept a map source-to-string like `move:<uuid>` and `skill:bonus:<uuid>`. Until then only SkyyAccessories may write it |
| G5 | I | **Flat vs percent on the small pools** | Stamina about 10, Mana 10 to 20, so percent boosters give +1. A flat modifier is easy, but `flatMax` counts every other additive modifier, so Vitality would multiply a flat accessory key. Needs a rule (exclude `skyyacc_` flat keys from `flatMax`, or accept it). HANDOFF open decision 2 was never answered |
| G6 | I | **No Accessory Power code** | boosters cannot add AP on day one; carry the locked +10 to +25 per rarity as data only. No `acc:power`, powers, tuning, enrichments |
| G7 | B | **No drop hooks** | see 3.7: nothing adds items to mob or chest drops; a custom drop list asset is UNVERIFIED |
| G8 | I | **Stat visibility** | the bag "Bonuses" line lists five families; `gear:fn:stats` excludes extras, so HUD and stat screens will not show accessory Strength |
| G9 | I | **Mana Regen, Stamina Regen, Dodge, Spell Cost %, oxygen, swim speed** | requested-type stats that do not work yet (2.1, 2.2). Mana Regen is a small build (Regeneration pattern); the rest need engine checks or new systems |
| G10 | I | **Mining Speed, Breaking Power, Tree stats** | SkyyTrees has no external source map; needs a Trees patch before accessories can add swing speed |
| G11 | N | **Icons and visuals** | 3 free crystal colours, 2 free gems; more lines need other vanilla references or new art |
| G12 | N | **Item text drifts from config** | tooltips keep build numbers; more tunable lines make it more visible |
| G13 | N | **Admin give command** | testing boosters needs one, or vanilla `/give` |
| G14 | N | **Collection gating of craft tiers** | lock 64 not wired (see 3.7) |
| G15 | N | **SkyyGear 0.1.1 and 0.1.2** | coming-later stats never roll (default flip) and the charged-attack modifier are still to come; the live 0.1 lets coming-later stats roll on gear. Boosters are unaffected if they use only the live keys |

---

## 5. Conflicts with locked decisions, and open decisions

| # | Topic | Source | What clashes | Suggested way out (Skyy decides) |
|---|---|---|---|---|
| C1 | Stamina on accessories | Decisions row 6.16, Plan lock 27: Stamina Regen is armor only "unless Skyy says later" | Skyy asked for "+ stamina". Max Stamina (Endurance, exists) is fine; Stamina Regen on an accessory breaks the lock | ship max Stamina now; ask Skyy before any Stamina Regen accessory |
| C2 | Accessory Speed: flat or percent | change note 10 / row 6.14 ("flat +Speed on armor, Equipment, accessories") against the 2026-09-23 layer model (accessories are a percent layer), the live Speed talisman, and Skyy's "+% movement speed" | a `gear:extra spd` booster lands in the flat layer beside armor | keep percent through the accessory pct source; treat "flat +Speed" as the armor and Equipment shape; confirm with Skyy |
| C3 | What "one per family" means | 2026-09-23 layer model: "only ONE accessory per kind/family counts (no stacking 6 speed rings)" | Hypixel has many different accessories giving Strength. If family means stat, only one Strength accessory ever counts; if family means accessory line, many can stack | decide: strict one-per-stat, or one-per-line with a per-stat cap |
| C4 | Mana shape | notes 18 and 20: dedicated mana accessories use +% mana, powers use flat mana; base pool 10 / 20 | +% Mana on 10 is +1; a dedicated mana accessory would feel dead | Skyy picks flat, percent, or percent plus a flat floor; the pools grow later with armor and Overall Level |
| C5 | Coming-later stats | OPEN-QUESTIONS 2026-09-30 LOCK: nothing not in the game yet stays in the list | boosters may only use the LIVE stats of section 2; `gear:extra` would accept LATER keys silently | build-time check; keep a written "allowed stats" list in the booster spec |
| C6 | Accessory Power | change note 23, Plan locks 111-115: every accessory adds flat +10 to +25 | not built; the old 3/5/8/12/16 table in the Plan is obsolete | give each booster an AP value as data; no code depends on it yet |
| C7 | Rarity ladder | Skyy 2026-09-25: gear rarities are Wynn (Normal, Unique, Rare, Legendary, Fabled, Mythic, Set), and the Magic Bags use the same. Accessories use vanilla Common to Legendary, and "Rare" is a different colour on each. DESIGN-STATUS question 13 asked it for gear; nothing was said for accessories | a Rare sword is pink, a Rare accessory is blue | ask Skyy whether accessories move to the Wynn ladder before many items are made |
| C8 | Craft tiers by collection | change note 17 / lock 64 | not wired; talisman recipes are open at the Workbench | add explicit collection rows, or accept open recipes for now |
| C9 | Level requirement | change note 6: "every gear item" has a level requirement; SkyyGear spec keeps `Skyy_*` out of gear and reserves `kind:"accessory"` with no gate | accessories have no level; a strong Strength accessory has no gate | ask Skyy whether accessories are "gear items" for this rule |
| C10 | Oxygen and swim speed | note 16 | locked as accessory effects but unbuilt and unproven | keep out of the first booster set |
| C11 | Two competing plans for combat feed | SkyyAccessories-Plan technical notes (`acc:pct` map, one elected applier per stat) against SkyyGear's shipped `gear:extra` | the Plan's design was never built; `gear:extra` is live | treat `gear:extra` as the path; update the Plan text later |
| C12 | Loadouts | lock 12: a loadout saves armor, Equipment, and the chosen power, not the bag | no clash; bag contents are not in loadouts | none |
| C13 | Tooltips vs "files always match" | Server Setup contract | item text cannot follow config | accept, or add a live-numbers line to the bag page (already there) |

Not conflicts (checked): "coming-later stats never roll" only governs gear rolls, and accessories do not roll; AH rules block the
Accessory Bag but not the accessories; the vanilla-assets-by-reference rule is already how the talismans are made.

## 6. Questions for Skyy (each has a default in brackets)

1. Does "+ stamina" mean max Stamina only? [yes: max Stamina, no Stamina Regen on accessories]
2. Accessory Speed: percent through the accessory layer? [yes, percent]
3. One accessory per stat, or one per accessory line? [one per line, each line one stat, several lines may share a stat]
4. Mana boosters: flat, percent, or both? [flat for early lines, percent later, pools are tiny today]
5. Do accessories move to the Wynn rarity ladder? [not yet, keep Common to Legendary]
6. Do accessories get a level requirement? [no]
7. Bag slots first: build the 9 to 60 slot growth before the boosters? [yes, it blocks them]

## 7. Sources read

Skyy's design files (read only): `tools/AGENT-BRIEF.md`, `HANDOFF.md` (status block, sections 1 to 3, newest log lines),
`OPEN-QUESTIONS.md`, `RESUME.md`, `SkyyAccessories-Plan.md`, `SkyyGear-Stat-Catalog.md`, `SkyWynn-Decisions.md` (accessory rows),
`SkyyGear-Plan.md` (accessory locks). Build scripts: `SkyyAccessories/build_skyyaccessories_0.4.5.py`,
`SkyyGear/build_skyygear_0.1.py` and `0.1.1.py`, `SkyySkills/build_skyyskills_0.4.7.py`, `SkyyTrees/build_skyytrees_0.2.5.py`,
`SkyyCollections/build_skyycollections_0.2.4.py`, `SkyyExploration/build_skyyexploration_0.2.2.py`, `SkyySacks/build_skyysacks_0.7.7.py`,
`SkyyMenu/build_skyymenu_0.3.3.py`, `SkyyAuctions/build_skyyauctions_0.1.2.py`, `tools/skyymove.py`, `tools/deploy_set.py`. Specs: `research/SkyyGear-Stage1-Spec.md`, `research/SkyyGear-0.1-Review-Findings.md`,
`research/Skill-Trees-Spec.md`, `research/Overall-Level-Spec.md`, `research/Classes-Berserker-Priest-Spec.md`,
`research/Bag-Restructure-Spec.md`. Assets.zip was read (read only) for vanilla crystals, gems, qualities, stat assets and the drop
table layout.
