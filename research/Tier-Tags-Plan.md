# Tier tags on item tooltips - plan (2026-10-15)

Skyy 2026-10-15: "(make sure we add the T1 and T2 and so on tags to the flavor text of every item we give a tire. to make it easy". It came
right after "id make the bag upgrade count all wood types of the right tier, not just oak." (docs/answered/bags.md 2026-10-15).
Same day Skyy set the watering can ladder: "a T1 crude watering can, (made of wood.) upgrades to a T2 copper T3 iron and so no"
(docs/answered/gear.md 2026-10-15).

Sources read: research/Gathering-Progression-Spec.md (2, 3.4), research/Gathering-Shards-Spec.md (4, 5, 6, 7, 9), research/Watering-Can-Harvester-Spec.md,
research/SkyyArmory-Spec.md (1.1), research/Cooking-Skill-Spec.md (2.3), research/cloud/SkyyFishing-Spec-Draft.md (4), docs/answered/economy.md + bags.md + gear.md,
PACK.md, the generated SkyyGear 0.3.10 script (GearLevel tables), and the 33 SET jars (language files counted, nothing written).

> **Decided 2026-10-15 (Skyy popups, docs/answered/gear.md TIER TAGS):** materials match their tool (T1 = Crude), format `T3 Iron - text`, own ladders tagged,
> mob drops / gems / stone untagged. Built T0 + T1: **hides / leathers are NOT tagged** (their order was a placeholder; a wrong tag is worse than none).
> **Seeds:** DynamicSeasons 7.0.2 (pack mod) overrides all 28 seed items with its own description key, so their tags come later via SkyyGear's tooltip (path c).
> Standing rule: PROJECT-RULES 4 'Tier tags'.

## 0. Short version

- ONE ladder, ONE table: **T1 Crude, T2 Copper, T3 Iron, T4 Thorium, T5 Cobalt, T6 Adamantite, T7 Mithril, T8 Onyxium.** Materials take the tier of the
  tool / set that works them (Copper ore T2, Oak T2, Wheat T2). Only Crude / Wood starter things are T1.
- Shown as a first phrase of the item's flavour text: **`T3 Iron`**. About **750 items** get it (about 495 vanilla ids through OUR jars' lang keys, about 255 of ours).
- Owners: **SkyyGear = every vanilla tool / weapon / armor key, SkyyCollections = every vanilla material key (ore, bar, log, crop, seed, hide);**
  a mod that already writes a description key keeps it and adds the tag itself. One generated table `tools/tier_tags.py` feeds every build.
- Most of this needs NO tooltip code: SkyyGear's tooltip already prints the item's own description key as the grey italic flavour line
  (`GearView.descMsg`, FLAVOR slot). VERIFIED in the 0.3.10 script. about 80% of the vanilla ids we would tag have NO vanilla description at all, so the tag
  is the whole text (checked against Assets.zip: of about 495 vanilla ids, about 100 already have one).

## 1. The tier list

### 1.1 Recommended numbering and the conflicts it settles

| # | Conflict | Sources | Recommendation |
|---|---|---|---|
| C1 | Tool ladder is **0-based** (T0 Crude, T1 Copper ... T7 Onyxium) in specs and code; Skyy says **T1 Crude, T2 Copper, T3 Iron** | Shards 4.1 / 6.1, GearTool `TOOL_TIERS`, GearSpeed `tierOf`, doc field `tier` 0-7; Fishing spec rods "T0 Crude"; Progression 3.4 armor "tier 0 = vanilla Wood" vs Skyy's can quote | **T1 = Crude everywhere in what players SEE.** Code keeps its 0-based integer; ONE function `display = internal + 1` in tier_tags.py. No saved data changes. |
| C2 | Material tiers are named **M1 Copper / M1 Grove / M1 Wheat** (first real step), tools are T2 Copper | Progression 2.1-2.3, Shards 7.1-7.3 (gate: tool T vs block M, "M <= T normal") | Materials show the SAME number as the tool that matches them: Copper ore **T2**, Oak **T2**, Wheat **T2**. The rule becomes learnable: "tool tier >= material tier". Cost: T1 holds nothing but Crude / Wood starter items. |
| C3 | Crude (T1) vs Copper ore (now T2): live gate counts Crude as gate level 1, SAME as Copper (Gear 0.3.1, Skyy 10-13 "if crude is also T1 it should take the normal amount of hits") | Gear 0.3.1 header + `decideI`; Shards 4.2 (original: Crude on Copper = 8 hits) | Gate stays as built (numbers are internal). Crude tool tooltip keeps one hand-written line: "Starter tool - works Tier 2 materials at full speed." Question 1. |
| C4 | Log tiers: **zone tiers F1-F5** (key log carries unlocks) vs **price tiers T1-T5** (economy.md 10-04: Dry = T1 but Zone 2, Redwood T3 but F4, Sallow T2 but F5) | Progression 2.2, economy.md, Gear armor ids `F1..F5`, bag "Tier N logs" (sacks088) | **Zone tier is the tier** (F1 Grove = T2 ... F5 Wastes = T6). Price tiers stay inside SkyyBazaar, never shown. |
| C5 | Crop tiers: bench **pairs P1-P7** vs price tiers **T1-T4** vs hoe steps (Progression 2.3: Carrot = Thorium hoe; Shards 7.3: Carrot = T2 Iron hoe) | Progression 2.3, economy.md, Shards 7.3 | Pair order (P1 = T2 ... P7 = T8). Shards 7.3 is newer and lifelong tools have no recipes, so its hoe steps win. |
| C6 | "Tier N logs" in the bag upgrade text (sacks088, in flight) counts Oak = tier-1 logs; the new numbering makes Oak T2 | docs/answered/bags.md 2026-10-15 | Sacks 0.8.8 text: "T2 logs" (or "T2 Copper logs"). The text is generated from tier_tags.py so it cannot drift. Needs Sacks builder told BEFORE it ships. |
| C7 | "T1" in rebirth text means the first gathering-armor piece (Copper piece) | Gear 0.3.x `GATHERING ARMOR back to T1`, Rebirth spec D9 | Gathering armor has no Crude piece, so its first set is T2. Reword "back to its first tier" in docs / tooltips; no code change. |
| C8 | Accessory ids carry `_T1.._T4` (talismans) and `_T1.._T7` (bench accessories, Farming bench) but Skyy's rule is "same rarity tiers as weapons and armor" (bags.md 09-30) | SkyyAccessories 0.5.16 ids | Their `T` is a different ladder (bench level / talisman strength). Tag with the ladder noun: `T2 Bench`, `T3 Talisman`, so it never reads as the metal tier. Question 3. |
| C9 | Totems: "T1 harvest spirit totem" = tier I-V (Totem Pole II ...), ONE item id for all tiers | Shards 9.3, 9.3.1 | Own ladder: `T2 Totem` (tag comes from the tier document, tooltip code). |

### 1.2 The list (counts from Assets.zip 0.7.2 and the SET jars)

Tier column is the shown number. "Internal" is the 0-based number code uses today.

| Family | Items (count) | Tier rule | Source of the tier |
|---|---|---|---|
| **Pickaxe / shovel / hatchet / hoe / sickle** (vanilla ids) | 32 (+ hammers 2) | Crude / Wood **T1**, Copper / Scrap **T2**, Bronze / Iron / Steel **T3**, Thorium T4, Cobalt T5, Adamantite T6, Mithril T7, Onyxium T8 | Gear `TOOL_TIERS` (+1); Shards 4.1 |
| **Lifelong tool documents** (same ids, tier changes on the Anvil) | no new items | follows the item id | Shards 4 / 6.1 |
| **Watering can** (new, SkyyGear next round) | 8 planned (one id per tier) | T1 Crude (wood) 1x1, T2 Copper 3x3, T3 Iron 5x5, T4 Thorium 7x7 ... | Watering-Can spec; Skyy 10-15 |
| **Harvester** (hoe + sickle merge, after rebirth 1) | 8 planned | tier of the merged hoe / sickle | Watering-Can spec |
| **Weapons** (vanilla Weapon_*) | 244 | tier from the item's SkyyGear level band: Lv 0-9 **T1**, 10-14 T2, 15-19 T3, 20-24 T4, 25-34 T5, 35-39 T6, 40+ **T7**; ids with `Onyxium` **T8** (Mithril and Onyxium share Lv 40) | Gear `MATERIALS` + `FAMILIES` tables (Stone / Trork / Fishbone 5 = T1, Scrap / Rusty 10 = T2, Tribal 15 = T3 ...) |
| **Armor** (vanilla Armor_*: metal, cloth, leather, Kweebec, Trork ...) | 111 | same band rule (Wool / Soft 5 T1, Linen / Light 10 T2, Cotton / Medium 15 T3, Silk / Heavy / Raven 20 T4, Cindercloth 30 T5) | same Gear tables |
| **Class weapons** (SkyyArmory: wands, staffs, spellbooks, kunai, bo staffs, gauntlets, wraps, soul cages, crossbows) | about 56 own + 11 vanilla ids it already describes | metal in the id, wraps by cloth row | Armory spec 1; Gear tables |
| **Gathering armor** (SkyyGear 0.3.9: Foraging F1-F5, Farming P1-P7, Fishing A1-A5) | 68 | F1 Grove bark = **T2** ... F5 = T6; P1 = T2 ... P7 = T8; A1 Copper angler = T2 ... A5 = T6; Mining set: Copper T2 ... Onyxium T8 (built later) | Progression 3.4; Gear ids |
| **Ores (drop items)** | 7 (Copper ... Onyxium); Silver / Gold / Prisma have no tier | Copper **T2**, Iron T3, Thorium T4, Cobalt T5, Adamantite T6, Mithril T7, Onyxium T8 | Progression 2.1 (M1-M7) |
| **Bars / ingots** | 8 (the 7 + Bronze T3) | same as their ore | same |
| **Enchanted materials** (SkyyCollections, 19 live) | 19 | same as the base: Ench Copper T2, Ench Oak T2, Ench Wheat T2 ... (Cobblestone / Rubble: no tier, untagged) | Progression 4.x; Collections |
| **Logs** (Wood_*_Trunk) | 34 | F1 Grove (Oak, Birch, Beech, Ash, Aspen) **T2**; F2 Autumn / Azure (Maple, Azure) T3; F3 Savanna (Gumboab, Dry, Bottletree, Palo) T4; F4 Northern (Redwood, Fir, Cedar, Poisoned, Spiral) T5; F5 Wastes (Sallow, Burnt, Petrified, Bamboo, Camphor, Banyan, Jungle, Blue Fig, Fire, Crystal) T6; Orchard side group (Apple, Amber, Stormbark, Windwillow, Wisteria, Palm, Ice, Sadwillow) T2; Zone 5 woods T7 / T8 later | Progression 2.2; Shards 7.2 (Orchard = M1) |
| **Crops** (harvest items) | 14 | pair order: Wheat, Lettuce T2; Carrot, Corn T3; Cauliflower, Turnip T4; Pumpkin, Aubergine T5; Tomato, Chilli T6; Cotton, Rice T7; Potato, Onion T8 | Progression 2.3 (LOCKED pairs) |
| **Seeds + eternal seeds** | 28 | same as their crop | same |
| **Hides + leathers** | 16 | Soft T1, Light T2, Medium T3, Heavy T4, Scaled T5, Storm T6, Dark T7, Prismic T8 (**PLACEHOLDER**: economy.md price order, matches the leather armor rows) | economy.md 10-04; Gear tables |
| **Fishing rods** (SkyyFishing) | 8 (Bamboo T1, Copper T2 ... Onyxium T8) | rod ladder | SkyyFishing spec 4.1; Shards 5.4 |
| **Reels** | 3 live (Bamboo, Copper, Iron) | same | same |
| **Fish** (our 10 Zone 1 species) | 10 | by zone water: Pond (Z1) **T2**; Dune T4, Frost T5, Lava T6, Cave T7 when built (**PLACEHOLDER**, follows the zone's wood tier) | Fish catalog; Shards 4.1 |
| **Fishing parts** (hooks, lines, sinkers I-II) | 14 | own ladder "Part I-II" - keep as is, NOT tagged | Fishing spec 4.2 |
| **Totems** (items; blocks reuse them) | 21 types | own ladder `T1..T5 Totem` from the tier document | Shards 9.3 |
| **Accessories with `_T` ids** | 50 (bench accessories 28, talismans 22) | own ladders: `T3 Bench`, `T2 Talisman` (number = the id suffix) | SkyyAccessories 0.5.16 |
| **Lost Loot chests** | 5 (`Skyy_LootChest_T1..T5`) | `T3 Loot` | Exploration; economy.md 10-15 "T3 T3-T4" |

Left alone (no tier in our design, so nothing to tag): stone / dirt / sand blocks (M0), Silver / Gold / Prisma, gems, mob drops, food, potions,
Cooking grades (they use "Grade N"), rarity-only items (accessories by rarity, sigils, Unid bags, sacks), class abilities, Menu / Vault icons, UT specials ("Untiered").
If Skyy wants mob drops tiered, the zone of the mob is the only existing source (Combat has no drop ladder yet).

Total tagged: 32 + 2 + 244 + 111 + 56 + 68 + 7 + 8 + 19 + 34 + 14 + 28 + 16 + 8 + 3 + 10 + 21 + 50 + 5 = **about 735**, plus 16 coming with the can / Harvester = **about 750**.

### 1.3 Pack mods (rule: never ship a file or key that touches their ids)

Pack items that are clearly on the ladder: Multitools 8 (Crude ... Onyxium) and More Crossbow Tiers 4 (Thorium, Cobalt, Adamantite, Mithril). Others (The Armory 1,338 items, NoCube Orchard 37, Saplings From Trees 44, AdvancedFarming 17) carry no tier of ours.
**Pack items get NO lang tag.** The 12 ladder items that SkyyGear already documents (multitools, crossbows) get their tag at runtime through the tooltip path (c) below,
because that is per-stack metadata and ships no file over their ids. That leaves about **1,430 pack items untouched** (everything else in The Armory etc.).

## 2. How it is shown

### 2.1 Tag format (pick one; the tag is always the FIRST phrase of the flavour text)

| Option | Looks like | Pros / cons |
|---|---|---|
| **A (recommended)** | `T3 Iron - <vanilla or our text>` | one ladder word list (Crude ... Onyxium); the same text on a Maple Log, an Iron pickaxe and a Carrot ("T3 Iron" = Iron-class); short; works as plain lang text |
| B | `[T3] <text>` | shortest; loses the metal word players already know |
| C | `T3 Foraging - <text>` (skill word) | clear for gatherables, ambiguous for weapons / armor / fish; one more word table to keep right |

In the tooltips built by SkyyGear / our own code (path c) the tag can be a separate first line in the vanilla Rare-blue / label colour; in a plain lang
description it is the same colour as the flavour line (grey italic). A lang value is one line (a newline inside a value is UNVERIFIED, probe P2).
Own-ladder tags use the noun instead of the metal: `T2 Totem`, `T3 Loot`, `T2 Bench`, `T3 Talisman`.

### 2.2 How each kind of item gets it

| Kind | Mechanism | Notes |
|---|---|---|
| (a) **Vanilla items** (tools, weapons, armor, ores, bars, logs, crops, seeds, hides) | A description key `items.<id>.description` (and the `server.items.<id>.description` twin, as Accessories writes both) in the lang file of the OWNER mod's jar, generated at build time by `tier_tags.py` | The engine falls back to `server.items.<id>.description` (VERIFIED, Armory spec 1.1; SkyyArmory already does this for 11 vanilla staffs / wands). The item JSON is not touched. For the ~100 vanilla ids that already have a vanilla description the build reads the vanilla `server.lang` line (as `vname()` does in SkyyAccessories) and writes `T3 Iron - <vanilla text>` into OUR jar. Never committed (generated into the jar). That puts vanilla text in our jars, like Cooking already does: part of the release-packaging question, not new. Whether a mod key BEATS an existing vanilla key is UNVERIFIED (probe P1). |
| (b) **Our own items** | The item's own mod lang line gets the tag in front of its text, from the same table | Armory, Fishing, Collections, Accessories, Exploration, Gear (gathering armor), future can / Harvester |
| (c) **Items with a metadata tooltip** (SkyyGear documents, lifelong tools, totems, pack items SkyyGear documents) | Gear documents: nothing extra - `descMsg` already prints the description key in the FLAVOR slot, so the tag from (a) / (b) shows. Totems (one id for all tiers): SkyyShards' tooltip builder adds `T<n> Totem` from the tier document. Pack ladder items: SkyyGear's tooltip adds the tag by id from the same table | Server Setup switch "Show tier tags" can only hide the code-added ones (lang text is static like a name). Default on |
| (d) **Pack mods' items** | not touched; see 1.3 | about 1,430 items left out |

## 3. Ownership: one writer per key

Today (counted in the 33 SET jars): 2,178 lang keys, 1,017 of them `*.description`. **No description key is written by two jars.** The only duplicate
key pair is `benchCategories.workbench.skyyaccessories` (and its `server.` twin) written by SkyySacks AND SkyyAccessories with the same text (harmless, but proves the engine accepts it).

| Mod | Description keys today | Is there a conflict risk |
|---|---|---|
| SkyyCooking | 360 (own Cook items) | none - Grade, not tier |
| SkyyAccessories | 194 (own) | owns its `_T` tags |
| SkyyGear | 97 (own: Unid bags, Sigils, gathering armor, UT specials) | owns vanilla tool / weapon / armor keys from now on |
| SkyyFishing | 84 (own) | owns rods, reels, fish |
| SkyyShards | 76 (own) | owns totems (tag via tooltip, key text unchanged) |
| SkyyArmory | 65 (54 own + **11 vanilla ids**: Weapon_Staff_<7 metals + Wood>, Weapon_Wand_Wood / Wood_Rotten / Tribal) | keeps those 11 keys and prefixes the tag itself; Gear's generator must SKIP them |
| SkyySacks | 44 | no tier tags |
| SkyyCollections | 38 (Enchanted + collection items) | owns Enchanted + all vanilla MATERIAL keys |
| SkyyClasses / Vault / Exploration / Islands / Menu | 38 / 12 / 5 / 2 / 2 | Exploration owns `Skyy_LootChest_T*` |
| SkyySkills | 0 lang keys, but overrides 24 vanilla item JSONs (old wands / staffs) | no lang change |

**Recommendation**

| Keys | Owner | Why |
|---|---|---|
| vanilla tools, weapons, armor (about 389, minus Armory's 11) | **SkyyGear** | it already owns every vanilla tool override (Progression F20), the level tables, and the tooltip that prints the key |
| vanilla ores, bars, logs, crops, seeds, hides, leathers (about 107) | **SkyyCollections** | the ladder owner: Enchanted items, `coll:locked`, per-tier rows; no other mod writes these ids |
| own items | their own mod | unchanged |
| any id already in a mod's lang | that mod, tag added there | one key can have one writer; the table says which |
| SkyyCore | none in v1 | the merge keeps moving jars; keys follow their owner into Core later |

Generator: `tools/tier_tags.py` is the ONLY tier table: rows `id-pattern -> (internal tier 0-7, ladder)`, `display(id)`, `tag(id)` (the text `T3 Iron`),
`owner(id)` (which mod's lang carries it), `ids_for(mod)`. Every build script imports it (`import tier_tags as TT`) and asserts: every id it
tags exists in Assets.zip or its own mod; the owner is itself; Gear's `MATERIALS` / `FAMILIES` band agrees with the table's tier. Bag text, Anvil text and Bazaar
labels use `TT.tag()` too, so a renumbering is one edit.

## 4. Build rounds (smallest safe order)

| Round | Mods touched | What | Size |
|---|---|---|---|
| T0 | none (tools only) | `tools/tier_tags.py` + test, `tools/ci/langdup.py` (reads every `*.lang` of the SET jars, fails on a key with two different values, warns on identical ones; today it would warn on the 2 benchCategories keys) | no agents; docs-grade |
| T1 | SkyyCollections (next), SkyySacks 0.8.8 | all vanilla MATERIAL keys + the 19 Enchanted + the bag "T2 logs" text; includes the three **probe items** (P1 / P2) so Skyy can look | Lean round (one builder + one review), no saved data |
| T2 | SkyyGear (same round as the can / Harvester, after 0.3.10 lands - one writer per mod), SkyyArmory | vanilla tool / weapon / armor keys, gathering armor, can + Harvester born with tags, Armory's 11 + own items | Full round (several mods, items players hold) - but text only |
| T3 | SkyyFishing, SkyyAccessories, SkyyExploration, SkyyShards | own ladders (`T2 Totem`, `T3 Loot`, `T2 Bench`), rods / reels / fish | Lean round each, can ride on their next feature round |
| T4 | SkyyGear tooltip | pack ladder items (12) | with T2 |

Checks every round: `python tools/ci/crosscheck.py --jar <new jars> --baseline`, `python tools/ci/lint.py` (0 fails), `python tools/ci/langdup.py` over ALL SET jars
(new), a build assert that no id is tagged by two jars, `tools/smoke_test.py` (no asset-validation failure). In-game: Skyy checks the probe items before T2.

**Probes (UNVERIFIED, put in T1):** P1 does a key in our lang BEAT a vanilla `items.<id>.description` that already exists (test: Copper Ingot, Oak Log, Copper Hoe)?
P2 does a `\n` inside a lang value break the line (so the tag could be its own line)? P3 does the SkyyGear flavour line show the tag on a vanilla Iron Pickaxe document?

## 5. Questions for Skyy (defaults in brackets)

1. Numbering: materials show the tier of the tool that matches them, so **Copper ore, Oak, Wheat are T2** and T1 is only Crude / Wood starter things; the bag line reads "T2 logs" for Oak. OK? [yes; the alternative is every family starts at T1, which breaks "a T3 axe chops T3 wood"]
2. Format: `T3 Iron - text` (A), `[T3] text` (B) or `T3 Foraging - text` (C)? [A]
3. Should totems, Lost Loot chests, benches and talismans (their own ladders) also get a tag, written `T2 Totem` / `T3 Loot`? [yes]
4. Mob drops, gems and stone have no tier in the design. Leave them untagged for now? [leave untagged]
