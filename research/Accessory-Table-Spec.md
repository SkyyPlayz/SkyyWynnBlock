# Accessory Table: build spec (SkyyAccessories 0.5.4 + SkyySacks 0.7.13)

> **PAUSED DRAFT (2026-10-02):** the three critics never finished and nothing was built. Ask Skyy whether the pack still wants the table (RESUME "Also queued") before reviewing or building from it; version numbers below are from 2026-10-02.

> **Skyy's words win over this draft:** OPEN-QUESTIONS.md, "Q&A with Skyy 2026-10-02", the two LOCKED 2026-10-02 lines quoted below.
> Where an older lock still applies it is named where it bites (the 2026-10-01 Workbench-tab lock is replaced by this one, except the
> order rule, which carries over).

*Written 2026-10-02 (spec writer, Fable) from three researchers' verified findings (A = engine benches, B = SkyySacks + /craft, C =
SkyyAccessories) plus my own read-only checks of the same files on this PC. Nothing is built, committed or deployed; this file is the
only thing written. Sources, all read only: **A53** = `SkyyAccessories/build_skyyaccessories_0.5.3.py` (the SET pin as of tonight:
`tools/deploy_set.py` L21 says 0.5.3 - the Night Vision round pinned it while the research ran; the table build is a patch on the
GENERATED 0.5.3 script, never a re-run of `tools/acc_0_5_3_patch.py`), **S** = `SkyySacks/build_skyysacks_0.7.12.py` (SET pin,
`deploy_set.py` L19), **WB** = `tools/skyywbtab.py` (the shared Workbench-tab kit, protocol "1"), **ART** = `tools/skyyart.py` (kit 1.0),
`HytaleServer.jar` bytecode and `Assets.zip` (read in place), the two test harnesses `test_skyyaccessories_0.5.3.py` / `test_skyysacks_0.7.12.py`.
Line numbers are from those files tonight; the builders anchor on class + method names first.*

**Legend.** VERIFIED = seen in bytecode (class + method named), in Assets.zip (path named) or in a build script (function + line named).
INFERRED = strongly implied, not proven. UNVERIFIED = needs the game. **PLACEHOLDER** = a number or text Skyy has not picked (section 12).

**Skyy (2026-10-02, verbatim, LOCKED):** "instead of rolling it all into the normal crafting table, we should make our accessory's their
own crafting table. (and an accessory for /craft. + added to omni. (and make sure your memory crafting limiters work on /craft. so you cant
bypass vanilla progression with / craft." Picked answer (OPEN-QUESTIONS L163-169): EVERYTHING moves to the new table - every accessory
(stat lines, bench accessories, the Omni), the Accessory Bag + its upgrades AND every Magic Bag; the Workbench "Accessories & Bags" tab goes
away; the table itself is crafted at the Workbench; a new bench accessory unlocks its recipes in /craft like the other bench accessories;
the Omni covers it (grant + recipe). Order inside the table as before (Skyy 2026-10-01): "list them in the order you would craft them. low
levels first. with legendries and omnis at the bottom." Both mods stay STANDALONE. Vanilla look.

---

## 0. Plain words (for Skyy)

- **A new block, the Accessory Table.** You craft it at a Workbench (cheap, early), place it, and open it like any bench. It uses the
  normal Hytale crafting window - no custom UI. It looks like the Arcanist's Workbench (the little table with a gem, book, hourglass and
  candle) with its own colours, so you never mistake one for the other. One tab inside, "Accessories and Bags", listing everything in
  crafting order: Accessory Bag and the Normal bags first, then Normal, Unique, Rare, Legendary, and the Omni Accessory + Mythic Omni Bag
  last. 69 recipes (70 if you say yes to Farming VIII, question 4).
- **Everything moves.** All 47 accessory recipes (stat lines, bench accessories, the Omni) and all 21 bag recipes (20 Magic Bags + the Mythic
  Omni Bag) leave the Workbench tab and live only at the table. The Workbench tab disappears. The Accessory Bag has no upgrade items of its
  own (its size is the "slots" setting), so "its upgrades" means the Magic Bag chain, which moves too. By default the Accessory Bag also stays
  craftable from your inventory, like today (question 3).
- **The bags you carry count as materials at the table** without any new code - the 0.7.12 bench link already feeds every crafting-type bench.
- **A new /craft accessory: the "Accessory Table Accessory"** (table + 4 copper, like every other bench accessory). With it in your Accessory
  Bag, /craft gets an **Accessories** tab with the table's recipes in the same order. The Omni now covers it too, and **Omnis people already
  own get the new bench automatically** (the Omni's grants are computed from the bench list, not stored on the item).
- **Vanilla progression holds in /craft.** Today /craft already refuses recipes you have not learned, but ignores the world's **Memories
  level** (38 vanilla recipes need level 2-6: themed chests, portal keys, Eternal seeds, Backpack 3 ...) - so a Furniture Bench accessory
  could make every chest on day one. 0.7.13 checks the Memories level exactly as the real bench does, hides what is locked with a line
  "N recipes need a higher world Memories level (this world: M)", shows the world's level on the page, and re-checks bench tiers against the
  real bench maximums. Pocket crafting and real benches already go through the engine and need nothing.
- **Both mods still work alone.** Each jar ships an identical copy of the table (one shared generator makes both); the game keeps one copy.
  SkyyAccessories alone: the table with its 48 recipes. SkyySacks alone: the table with its 21 bag recipes. Deploy both together.
- **Nothing is lost.** Item ids and recipe ids do not change; owned accessories, bags, Omnis, learned recipes and Collections rewards keep
  working. Only WHERE you craft changes. Players who used a Workbench Accessory for accessories in /craft now need the table accessory (or
  an Omni); the texts say so.

---

## 1. The table

### 1.1 Ids and names (PLACEHOLDER names - question 1)

| What | Value | Why |
|---|---|---|
| Item id | `Bench_Accessory` | vanilla style `Bench_<Name>` (`Server/Item/Items/Bench/*.json`); must NOT start with `Skyy_Accessory_` / `Skyy_Talisman_` (A53:1007 `AccDefs.isAccessory` would make it equippable and publish it to acc:has; SkyyAuctions 0.1.2 L1658 files such ids under Accessories) nor `Skyy_Sack_` (SkyyEssentials / SkyyAuctions trade blocks, SkyyGear `NEVER_GEAR` L727) |
| Display name | **Accessory Table** | Skyy's word; vanilla names are "<Role>'s Workbench" (server.lang `items.Bench_Arcane.name = Arcanist's Workbench`) - alternative "Jeweler's Workbench", question 1 |
| Bench id (`BlockType.Bench.Id`) | `Accessorybench` | vanilla lowercase style (`Arcanebench`, `Farmingbench`, `Loombench`, `Salvagebench`); unique (a clash merges recipes: `CraftingPlugin.registries` is one HashMap keyed by `BenchRequirement.id`, `String.equals` - researcher A B.4); contains no `_T` (SkyySacks `accessories()` S:4756-4785 and A53:1032 `benchOf` split at the LAST `_T`); not one of SkyySacks' special ids (Alchemybench, Cookingbench, Campfire, Furnace, Tannery, Salvagebench; S:4675 / 5051 / 5058) |
| Tab id | `Accessorybench_All` | vanilla pattern `<Bench>_<Tab>` (`Workbench_Crafting`, `Arcane_Portals`) |
| Tab name key / text | `server.benchCategories.accessorybench.all` = **Accessories and Bags** | vanilla key pattern + a server.lang line `benchCategories.accessorybench.all=...` (keys in server.lang get the `server.` prefix: `I18nModule.getPrefix`, researcher A D.4). "and" instead of "&": the deployed tab's "&" is still untested in the client and SkyyMenu already avoids raw `&` in sent text (`build_skyymenu_0.3.5.py` L998 assert) |
| /craft accessory id | `Skyy_Accessory_Accessorybench_T1` | the `Skyy_Accessory_<BenchId>_T<n>` family (section 4) |
| Shared file paths (both jars) | `Server/Item/Items/Bench/Bench_Accessory.json`; `Common/Blocks/Benches/SkyyAccessoryTable_Texture.png`; `Common/Icons/ItemsGenerated/Bench_Accessory.png`; `Common/Icons/CraftingCategories/Accessorybench/All.png`; the lang lines | the engine's path validators (`CommonAssetValidator.<clinit>`, researcher A A.5): textures under `Blocks/`, item icons under `Icons/ItemsGenerated/`, tab icons under `Icons/CraftingCategories/`. ONE shared path per file, not per-mod folders (section 3) |

### 1.2 The asset (VERIFIED shape: Assets.zip `Server/Item/Items/Bench/Bench_Arcane.json`, read tonight; decode proof: researcher A E3)

A bench is an Item JSON with an embedded `BlockType` that holds a `Bench` object (`Item.<clinit>`: "BlockType" is a ContainedAssetCodec,
Mode INHERIT_ID_AND_PARENT - the block takes the item's id). The generator (section 3) writes this, every key copied from the Arcane bench
except the marked lines:

```
TranslationProperties {Name server.items.Bench_Accessory.name, Description server.items.Bench_Accessory.description}
Icon "Icons/ItemsGenerated/Bench_Accessory.png"                       <- OURS (generated, 1.4)
Categories ["Furniture.Benches"]      Tags {Type ["Bench"]}      MaxStack 1      ItemLevel 2 (Arcane: 10)      ItemSoundSetId "ISS_Blocks_Wood"
PlayerAnimationsId "Block"            IconProperties {Scale 0.35, Rotation [22.5, 45, 22.5], Translation [11.4, -18.6]}   (Arcane's)
Recipe {TimeSeconds 3, Input <1.3>, BenchRequirement [{Type Crafting, Id Workbench, Categories [Workbench_Crafting]}]}   <- no RequiredTierLevel
BlockType {
  Material Solid, DrawType Model, Opacity Transparent, VariantRotation NESW, HitboxType "Bench_Alchemy" (2 blocks wide, the Arcane's)
  CustomModel "Blocks/Benches/ArcaneTable.blockymodel"                 <- vanilla model referenced in place (156 vanilla block models are shared
                                                                          by items with different textures, e.g. Temple_Light/Bench.blockymodel)
  CustomModelTexture [{Texture "Blocks/Benches/SkyyAccessoryTable_Texture.png", Weight 1}]     <- OURS (generated, 1.4)
  Bench {Type "Crafting", Id "Accessorybench",
         Categories [{Id "Accessorybench_All", Name "server.benchCategories.accessorybench.all", Icon "Icons/CraftingCategories/Accessorybench/All.png"}],
         LocalOpenSoundEventId "SFX_Arcane_Workbench_Open_Local", LocalCloseSoundEventId "SFX_Arcane_Workbench_Close_Local",
         CompletedSoundEventId "SFX_Arcane_Workbench_Craft"}          <- no TierLevels (one tier, like Arcane / Loom)
  BlockEntity {Components {BenchBlock {}}}                            <- MANDATORY: OpenBenchPageInteraction.interactWithBlock returns silently without it
  State {Definitions {CraftCompleted {CustomModelAnimation "Blocks/Benches/Alchemy_Crafting.blockyanim", Looping true},
                      CraftCompletedInstant {CustomModelAnimation "Blocks/Benches/Alchemy_Crafting.blockyanim"}}}
  Gathering {Breaking {GatherType "Benches"}}, BlockParticleSetId "Wood", ParticleColor "#6e4a2f", Support {Down [{FaceType Full}]},
  BlockSoundSetId "Stone", PhysicalMaterialId "Stone", TextureComputedColor <average opaque colour of OUR texture, computed by the generator>
}
```

- No `Interactions` block: `BlockType.processConfig` sets `Use` to `*Simple_Crafting_Default` for a Crafting bench and the hint
  `server.interactionHints.open` ("Press [{key}] to open {name}", server.lang) - researcher A A.4, proven in E3.
- `Type "Crafting"` opens the vanilla `SimpleCraftingWindow` (`CraftingPlugin.setup` fills `Bench.BENCH_INTERACTIONS`; `OpenBenchPageInteraction.interactWithBlock`
  SIMPLE_CRAFTING branch) - the same panel as the Workbench / Alchemy / Cooking benches. Researcher A C.1-C.2, E4.
- The window title is `server.items.Bench_Accessory.name`; the tab label is the raw `Name` the server sends (UNVERIFIED which key the client
  shows - the vanilla key + lang line is what the deployed Workbench tab does, so it is the safe choice).
- A recipe naming a tab the bench does not define is INVISIBLE (`getAvailableRecipesForCategory` -> `categoryMap`, researcher A D.2, E2) - the
  kit's `recipe_checks` enforces `[TAB_ID]` on every moved recipe.

### 1.3 Recipe at the Workbench (PLACEHOLDER cost - question 2)

Every vanilla bench is crafted at the Workbench in its **Crafting** tab (`Workbench_Crafting`; Assets.zip, all 11 bench recipes read
tonight: Armorer's / Blacksmith's / Chef's = 2 Copper Ingots + 10 Wood_Trunk + 5 Rock; Farmer's = 6 Wood_Trunk + 20 Fibre; Furniture = 6
Wood_Trunk + 4 Rock; Arcane / Alchemy / Salvage need Workbench tier 2; every one has `TimeSeconds 3`). The table must be EARLY, because its
first recipes are early items (Accessory Bag = 4 Wood_Trunk + 4 Cotton Scraps; Normal bags = 3 Bolt of Wool + 4 copper / logs / ...).

Default: **6 Wood_Trunk (resource type) + 4 Rock (resource type) + 2 Ingredient_Bar_Copper + 4 Ingredient_Fabric_Scrap_Cotton**, any
Workbench tier, 3 seconds, `Workbench_Crafting`. Written with `mat()`-style ids checked against Assets.zip at build time (A53:4080 `mat`
writes an ItemId for vanilla items and a ResourceTypeId otherwise).

This is the ONE recipe of ours allowed in a vanilla Workbench tab: today's `WB.recipe_checks` (WB:601-631) forbids `Workbench_Crafting` on
every item - the new kit's check allows it for `TABLE_ID` only (section 3.4).

### 1.4 Look: the Arcane model, our texture, our icon (generated at build time, never committed)

- **Model:** `Blocks/Benches/ArcaneTable.blockymodel` (VERIFIED nodes read tonight: BenchMain, several unnamed `Node` boxes / quads = the cloth
  drape and legs, Hourglass + sand, Book + BookCover + Gem + BookLatch + BookBack, Candle + Flame). Texture `ArcaneTable_Texture.png` is
  192x128, 14,258 opaque texels, 6,022 colours; **~2,142 texels (15 %) are the red drape**; the dominant colour `#361b0a` (1,409 texels) is the
  dark wood.
- **Texture (both jars, byte-identical):** `ART.recolor()` over a **hue-selected point set**: the red band (hue within about +-25 deg of red,
  saturation above ~0.35) - the drape and the red book cover - mapped onto a gradient; the gem recoloured to the same family. The wood,
  candle, flame, hourglass glass and sand stay vanilla. Two styles for the preview sheet (stage 0): **A** deep violet drape + violet gem
  (default), **B** teal drape + teal gem. The kit's gradient comes from vanilla pixels (`ART.palette_from`, e.g. the Blue / Cyan crystal
  textures the stat lines already use), so nothing is hand-painted.
- **Kit addition needed (ART):** `recolor()` only takes rectangles (`regions`; ART:338 `_region_points`). Researcher A: the drape shares
  rectangles with the wood (nodes BenchMain / Node), so a colour-selective mask is required. Add `hue_points(png, hue_lo, hue_hi, min_sat,
  min_alpha=1, regions=None) -> [(x, y)]` and a `points=` argument on `recolor()` (and `shade()`), plus a check in `verify()` / `_verify`:
  on `ArcaneTable_Texture.png` the red mask selects between 1,500 and 3,000 texels and NEVER a `#361b0a` texel; the output keeps size and
  every alpha byte. KIT_VERSION 1.0 -> 1.1.
- **Icon:** `ART.render_icon` is NOT proven for the block view (Rotation [22.5, 45, 22.5]: colour error 6.51 on Arcane against verify's 4.0 -
  researcher A I.4; ART module notes say the same for the Ingot view). So: `ART.recolor_icon(vanilla Bench_Arcane.png, grad, weights)` with
  weights = which icon pixels show drape texels. `icon_weights()` (ART:682) weights by NODE NAME, which cannot isolate unnamed drape nodes ->
  add `icon_weights_points(model, props, texture, points)` (same raster, a sample counts when its texel is in the hue mask; `_raster` ART:590
  already knows the texel of every sample). Fallback if the preview looks wrong: `recolor_icon` on the whole icon at low `rank` (a gentle
  tint). Icon file = `Icons/ItemsGenerated/Bench_Accessory.png`, 64x64.
- **Tab icon:** `Common/Icons/CraftingCategories/Accessorybench/All.png` = Assets.zip `Icons/ItemsGenerated/Utility_Bag_Seed.png` (the Accessory
  Bag's icon, 64x64 like the vanilla tab icons - `WB.icon_png` WB:273-284 already checks the size against `Workbench/Processing.png`). Same
  icon as the deployed tab, new shared path.
- **Preview for Skyy (stage 0):** a PNG sheet in the art agent's scratch with the texture, a 256 px render and the 64 px icon of styles A and
  B next to the vanilla Arcane bench (the wand ART-PROOF pattern), sent with SendUserFile. UNVERIFIED until Skyy sees it.

### 1.5 Tabs, order, tiers

- **One tab** (vanilla precedent: Bench_Loom / Bench_Trough have a single tab `All`). Reasons: it is what Skyy asked for ("list them in the
  order ..."); it is NEVER EMPTY with either mod alone (an empty tab is still sent to the client - `CraftingWindow.<init>` sends a tab without
  `craftableRecipes`; whether the client hides it is UNVERIFIED); one icon, no label ambiguity.
- **Order inside the tab** = the deployed mechanism: the recipe set `CraftingPlugin.registries["Accessorybench"].categoryMap["Accessorybench_All"]`
  is replaced by a `java.util.TreeSet(TabRank)` (today `WbTab.sort`, WB:528-549, on the Workbench registry; `BenchRecipeRegistry.addRecipe`
  uses `categoryMap.computeIfAbsent(...).add` through `java.util.Set` only - WB:15-19 and the WB.probe checks, which carry over). The server
  then sends Skyy's order in `craftableRecipes`. **UNVERIFIED: whether the client keeps the server's order** (WB:19-21; HANDOFF L560) - Skyy's
  first in-game look at the 0.5.2 Workbench tab answers it for free. **Fallback if the client re-sorts:** the kit holds the tab list as data;
  switch to five tier tabs (Normal / Unique / Rare / Legendary / Omni, each never empty with either mod alone, tab icons = the bag icon tinted
  per rarity with `recolor_icon`) and rebuild both mods. Not the default: five icons that must read at a glance is more art risk than one.
- **Tiers:** none. A `TierLevels` chain would gate rarities later (Unique at tier 2 ...) - possible, not asked for. `RequiredTierLevel` stays
  absent on every moved recipe (omitted = 0 = any tier: `CraftingManager.isValidBenchForRecipe`, researcher A E.3).

---

## 2. What moves - the full ordered list

**Rule (Skyy 2026-10-01, carried over):** Accessory Bag first, then the Normal bags, then tier by tier (Normal, Unique, Rare, Legendary):
stat accessories, bench accessories, bags; Omni Accessory next to last, Mythic Omni Bag last. Implemented by `rank_py` / `WbRank.rank`
(WB:112-147 / 355-386): key = tier x 1e6 + kind x 1e5 + sub x 100 + numeral; ids the tables do not know sort into their tier with sub 99;
ties by name. The new kit keeps this code and adds the 12th bench (`Accessorybench`, 1 tier) to `BENCHES` / `BENCH_TIERS` and the names.

The 69 recipes in the table (70 with Farming VIII, question 4; `*` = new):

```
 1 Accessory Bag                                   (SkyyAccessories; pocket-craftable too by default, question 3)
 2-6   Normal Mining / Foraging / Farming / Combat / Smithing Bag        (SkyySacks, KnowledgeRequired)
 7-11  Normal Health / Stamina / Mana / Regeneration / Speed Accessory   (stat lines; ids Skyy_Talisman_<Vitality|Endurance|Intelligence|Regeneration|Speed>_Common)
12-22  Workbench Accessory I, Armor Bench Accessory I, Weapon Bench Accessory I, Farming Bench Accessory I, Furnace Accessory I,
       Tannery Accessory I, Arcane Bench Accessory, Furniture Bench Accessory, Loom Accessory, Salvage Bench Accessory, Campfire Accessory
23 *   Accessory Table Accessory                   (Skyy_Accessory_Accessorybench_T1 - section 4)
24-28  Unique Health / Stamina / Mana / Regeneration / Speed Accessory   (_Uncommon)
29-34  Workbench II, Armor Bench II, Weapon Bench II, Farming Bench II, Furnace II, Tannery II
35-39  Unique Mining / Foraging / Farming / Combat / Smithing Bag       (_Medium)
40-44  Rare Health / Stamina / Mana / Regeneration / Speed Accessory     (_Rare)
45-48  Workbench III, Armor Bench III, Weapon Bench III, Farming Bench III
49-53  Rare Mining / Foraging / Farming / Combat / Smithing Bag         (_Rare)
54-58  Legendary Health / Stamina / Mana / Regeneration / Speed Accessory (_Epic)
59-62  Farming Bench Accessory IV, V, VI, VII     (+ 63 * Farming Bench Accessory VIII if question 4 = yes)
63-67  Legendary Mining / Foraging / Farming / Combat / Smithing Bag    (_Large)
68 Omni Accessory                                  (recipe: the top tier of every active bench, now 12 inputs)
69 Mythic Omni Bag                                 (SkyySacks; one Legendary bag of each type, no knowledge)
```

- **Every recipe's BenchRequirement becomes** `[{"Type":"Crafting","Id":"Accessorybench","Categories":["Accessorybench_All"]}]` (the kit's
  `TABLE_REQ`). The Accessory Bag keeps `Fieldcraft / Tools` FIRST and adds the table (the vanilla two-requirement pattern of
  `Bench_Builders.json` / `Bench_Campfire.json`; `PocketCraftWindow` only knows Fieldcraft recipes - researcher A H.4) unless Skyy picks
  table-only (question 3).
- **SkyyAccessories (48 recipes):** `WB_REQ` (A53:4060) becomes `ACT.TABLE_REQ` at every use: bench accessories (A53:4191), boosters (4283),
  legacy / hidden ids (4297; they delete the Recipe anyway), the Omni (4315), `BAG_REQ` (4115), the Campfire check (4376), the Night Vision node
  (4325 - it deletes its Recipe at 4326, so nothing of it moves; the constant reference just follows the rename). No recipe for the 5 part-2
  lines, 20 legacy ids, 5 retired bench accessories, Night Vision (A53:4199 / 4285 / 4298 / 4368 delete them) - unchanged.
- **SkyySacks (21 recipes):** `sack_item()` S:6335 writes the requirement; the 20 tiered bags keep `KnowledgeRequired true`, the Omni Bag
  `false` (S:6326-6342, 6348-6370). Recipe inputs unchanged (table S:262-292: Normal = 3 Bolt of Wool + 4 of the bag's material; each next
  rarity = the previous bag + 6 Linen / Shadoweave / Cindercloth scraps; Omni Bag = one Legendary bag of each type).
- **Recipe ids do not change:** `<ItemId>_Recipe_Generated_<n>` (`CraftingRecipe.generateIdFromItemRecipe(Item,int)`, pack "Hytale:Hytale"
  via `CraftingPlugin.onItemAssetLoad`) - independent of the bench. So SkyyCollections' rewards and `coll:recipes`, KnowSync's MANAGED list
  and every player's known-recipe set keep working (section 7).
- **Not in the table:** the table itself (Workbench, 1.3).

---

## 3. STANDALONE strategy: one shared kit, two identical copies

### 3.1 How the engine treats the same asset id in two packs (VERIFIED, researcher A J + E1)

- A mod's pack is `"Group:Name"` (`PluginManager.registerAssetPackIfNeeded`; `skyybuild.manifest` L92-95 writes Group "Skyy", Name
  "<version> <Mod>"), so today the packs are `Skyy:0.5.3 SkyyAccessories` and `Skyy:0.7.12 SkyySacks`. Packs with no dependency between them
  load in text order of that name (`Mod.calculateLoadOrder`) - Accessories first, Sacks last today; **the winner flips with version numbers**
  (Accessories 1.0 vs Sacks 0.9) and a dependency cannot be pinned because the identifier changes every version.
- `DefaultAssetMap.putAll` keeps a (pack, value) list per key; the LIVE value is the last entry; removing the later pack restores the
  earlier one (E1). `AssetStore.DETECT_DUPLICATE_ASSETS = false`: no warning. Identical copies are still both loaded (Item / BlockType /
  CraftingRecipe do not override `equals`), the loaded-assets event fires again and the recipe is regenerated under the same id - end state
  identical. Common files (PNG, model): the last pack's bytes are served; each duplicate bumps the harmless "Duplicated Asset Count" (already
  921-925 on every boot). Lang lines: same text silent; DIFFERENT text logs "'%s' has multiple definitions" and the later pack wins.
- **Consequence:** both jars must ship **byte-identical** table JSON, texture, icon, tab icon and lang lines **at the same paths**. If the
  copies drift, the copy that loads last silently wins and a recipe naming a tab that copy lacks vanishes from the table.

### 3.2 The kit: `tools/skyyacctable.py` (new; `skyywbtab.py` stays untouched for the older build scripts that import it)

Imported by both build scripts (`import skyyacctable as ACT`) and both test harnesses, like `skyywbtab` today (A53:183, S:117). Protocol
`ACT_VERSION = "2"`. Pure Python + the same javassist `emit` pattern as WB:287-580.

| Part | Content |
|---|---|
| Constants | `TABLE_ID`, `BENCH_ID`, `TAB_ID`, `NAME_KEY`, `TAB_TEXT`, `TABLE_NAME`, `TABLE_DESC`, `TEX_PATH`, `ICON_PATH`, `TAB_ICON`, `ACC_ID` (`Skyy_Accessory_Accessorybench_T1`), `TABLE_REQ`, `TABLE_RECIPE` (1.3), `FIELD_REQ` |
| Order tables | `LINES`, `BENCHES` (12: WB's 11 + `Accessorybench`), `BENCH_TIERS` (+ `Accessorybench: 1`; `Farmingbench` 7 -> 8 if question 4), `SACKS`, `TIER_WORDS`, `EXPECTED` (69 / 70, asserted like WB:85-86), `rank_py`, `sort_py`, `default_names`, `order_print` - ported from WB with the 12th bench |
| `table_files(assets_zip, style) -> {path: bytes}` | the item JSON (1.2, `json.dumps(indent=2)`, sorted keys for determinism), the texture (1.4 via ART), the icon, the tab icon. Deterministic: ART is clock-free and fixed-zlib (ART module notes); the JSON is text. Both builds call it with the SAME style constant |
| `lang_lines()` | `items.Bench_Accessory.name=Accessory Table`, `.description=...`, `benchCategories.accessorybench.all=Accessories and Bags` + the four `server.` twins (the SkyySacks / SkyyVault twin pattern, WB:41-42) |
| `table_sha(files)` | sha256 over the sorted (path, bytes) of the shared files + lang lines; a constant baked into each jar (`TabSort.SHA`) and printed by both builds |
| `probe(pool)` | WB.probe's registry / CraftingWindow checks (WB:173-270) minus the Workbench-specific `CraftingBench.categories` field and the `BenchCategory` constructor (no runtime tab any more), PLUS: `BlockTypeModule.setup` registers `BenchType.Crafting` with `Bench.CODEC.register`; `CraftingPlugin.registries` is a `java.util.Map` keyed by requirement id; the `isValidBenchForRecipe` and `getMemoriesLevel` needles of section 5.5 (SkyySacks also re-checks them in its own `_engine_facts`) |
| `emit(pool, CtField, CtNewMethod, CtNewConstructor, pkg, owner, mod)` | `<pkg>.TabRank` (= WbRank with 12 benches, Python mirror `rank_py`), `<pkg>.TabSort` (the TreeSet swap on `registries[BENCH_ID].categoryMap[TAB_ID]`, owner / fallback rule as WB:526-549: SkyyAccessories always installs its TreeSet, SkyySacks only sorts an unsorted set; `start()` logs `"Accessory Table: <n> recipes in crafting order; shared files <sha8>"`; `publishSha()` puts `acctable:sha:<Mod>` = SHA on the bridge and WARNs once when the other mod's value differs: "the two copies of the Accessory Table differ - the copy that loaded last is live; rebuild both mods from the same tools/skyyacctable.py"), `<pkg>.TabAssetL` (LoadedAssetsEvent for `CraftingRecipe` only -> `sort()`; the BlockType listener and `scan` / `applyTo` of WB are DROPPED - the table's asset declares its own tab) |
| `setup_java(pkg)`, `start_java(pkg)` | the plugin lines, as WB:584-598 (SkyySacks keeps appending its `BenchLink.start()` statement to the start text exactly as S:6290-6295 does today) |
| `recipe_checks(files, own_ids, bag_req_id=None)` | every recipe of ours names exactly `[{Crafting, Accessorybench, [TAB_ID]}]` with no `RequiredTierLevel`; the bag (if given) has Fieldcraft/Tools first; **`TABLE_ID` is the one item allowed `Workbench / Workbench_Crafting`**; nothing names `Workbench_SkyyAccessories` any more; `own_ids` == the recipes found, all in `EXPECTED` |
| `harness_checks(check, server_jar, mods)` | section 9.1 |

`tools/skyyacctable_test.py` (bare JVM, the `skyycfg_test.py` pattern): decode of the generated JSON through the real codecs, determinism,
the SHA, rank mirror on `EXPECTED` + `WB.EDGE_IDS`, the hue-mask bounds (section 9).

### 3.3 Each mod with the other missing (both VERIFIED paths)

| Situation | Table | Recipes in the table | /craft (SkyySacks) |
|---|---|---|---|
| Both new jars | one copy live (identical) | 69 / 70 in crafting order | Accessories tab with the table accessory or an Omni (section 4-5) |
| SkyyAccessories 0.5.4 alone | its copy | 48 | n/a (no /craft) |
| SkyySacks 0.7.13 alone | its copy | 21 bags | no accessory exists, so no Accessories tab; Fieldcraft + Collections as today |
| New Accessories + OLD Sacks 0.7.12 (skew) | Accessories' copy | 48; the 21 bags stay in the OLD Workbench tab, which 0.7.12's fallback `WbTab` still adds (S:6237 owner=False) | Workbench Accessory still unlocks the bags |
| OLD Accessories 0.5.3 + new Sacks (skew) | Sacks' copy | 21 bags; the 47 accessory recipes stay in the Workbench tab 0.5.3 owns | the table accessory does not exist yet; the bags need the Accessory Table Accessory (not craftable) -> bags only via Collections / real table |

Skew is never an item loss - recipes just sit in two places. Pin and deploy 0.5.4 + 0.7.13 (+ SkyyMenu 0.3.6) together, as 0.5.2 + 0.7.10 were.
The `knownBench` warning (S:4737) cannot fire for `Accessorybench` with any new jar present, because every table recipe names it.

### 3.4 Build checks that keep the copies identical

1. Both builds import ACT and write `ACT.table_files(...)` + `ACT.lang_lines()` into `files` (the kit asserts the four paths + lang are exactly
   what it generated: a build cannot edit them afterwards).
2. Both print `ACT.table_sha(...)`; the cross-check agent opens both jars and asserts the four shared entries and the lang lines are
   byte-identical (section 9.4) - this is the real guard, since both builds read the same Assets.zip on the same PC.
3. Runtime WARN on SHA mismatch (3.2 `publishSha`) for a server that mixes jars from different builds.
4. `SkyySacks._wbtab_checks` (S:6455-6482) today asserts the newest SkyyAccessories script imports the same module and owns the tab; its
   successor asserts the newest SkyyAccessories script imports `skyyacctable` with the same `ACT_VERSION` (else prints the NOTE).

---

## 4. The /craft accessory and the Omni

### 4.1 Accessory Table Accessory (`Skyy_Accessory_Accessorybench_T1`)

- **One new BENCHES row** in A53:404-427: `("Accessorybench", "Bench_Accessory", "Accessory Table", 1, [])`, placed after Campfire (the order
  of ACTIVE drives acc:has, the Omni recipe, the Omni text and `BENCH_IDS` / `BENCH_NAMES` / `BENCH_MAX`, all derived - researcher C 8). The
  hard-coded counts change: `len(ACTIVE) == 11` (A53:439, 4313 and the `== 11` near 4381-4400) -> 12; `WB.BENCHES` / `BENCH_TIERS` equality
  (A53:3983) -> `ACT.*`; recipes 47 -> 48 (A53:4346); harness "68 current items" (test L1035) -> 69 (70 with Farming VIII).
- **Recipe:** 1 `Bench_Accessory` + 4 `Ingredient_Bar_Copper` **at the table** (`TABLE_REQ`), like every T1 bench accessory ("the vanilla bench item
  + 4 Copper", A53:4187). Chicken-and-egg is the same as the Workbench Accessory today: craft two tables, place one.
- **Build fix:** `need_item(bench_item)` (A53:4186) only accepts vanilla ids -> accept `ACT.TABLE_ID` when its JSON is in `files`; the icon line
  (A53:4190, `Icons/ItemsGenerated/<bench item>.png`) resolves to our generated `ICON_PATH`, which must be checked to exist in `files`.
- **Rarity / name / text:** tier I = Normal (`QUAL[1]`); single tier so no numeral: "Accessory Table Accessory" (question 1 if Skyy wants another
  table name). Description: "Put it in your Accessory Bag to craft Accessory Table recipes - every accessory and Magic Bag - from your
  inventory with /craft." (the A53:4192-4195 template gives "craft Accessory Table recipes from your inventory with /craft" - add the gloss).
- **acc:has:** published by `benchList` (A53:1396-1420) like any bench accessory: `..._Accessorybench_T1`; `tierOf` reads `_T1`; `benchOf` gives
  `Accessorybench`; SkyySacks `accessories()` (S:4756-4785) parses it to bench `Accessorybench`, tier 1 - no SkyySacks parser change.
- **Slot rule:** one per bench (`groupOf`), unchanged.
- **Admin give:** `/accessories give <player> Skyy_Accessory_Accessorybench_T1` works through `giveable` (derived from BENCHES).

### 4.2 The Omni (`Skyy_Accessory_Omni`)

- **Grant:** `benchList` adds one synthetic `Skyy_Accessory_<id>_T<max>` per entry of `BENCH_IDS` / `BENCH_MAX` when the Omni is in the bag
  (A53:1396-1420, the `if (omni)` loop) and `acc:fn:has` answers true for exactly those ids (A53:1609). Both tables are built from BENCHES at
  class-init -> **an Omni already in a player's bag grants `Skyy_Accessory_Accessorybench_T1` the moment 0.5.4 runs.** Nothing is stored on
  the item; nothing to migrate. (With Farming VIII, the Omni's Farming grant becomes T8.)
- **Recipe:** one top-tier accessory per active bench, BENCHES order (A53:4307-4313) -> 12 inputs, the new one last. Only new crafts see it.
- **Text** (A53:4316-4319): the bench list gains "Accessory Table"; "Crafted at a Workbench from all 11 top-tier bench accessories" becomes
  "Crafted at an Accessory Table from all 12 top-tier bench accessories" (`len(ACTIVE)` is already interpolated).
- **/craft:** SkyySacks sees the Omni only through the synthetic acc:has entries (the Omni's own id is never published) - the table accessory
  entry arrives like the others; nothing to add.

### 4.3 Other texts that name the Workbench (all become "an Accessory Table" / "the Accessory Table (made at a Workbench)")

- SkyyAccessories: `ACC_NONE` A53:2849 ("None - craft accessories at a Workbench"); booster tooltips A53:4252 "(upgrade it at a Workbench)" =
  50 lang lines; the Omni text (4.2); the `_READY` log line (A53:3990) names the table instead of the tab; header comments.
- SkyySacks: S:3149, 3152, 3203, 3207, 3208 ("craft it at a Workbench ..."), the comment S:6368, the ready log line S:6286 (the long INFO),
  the bag page's "how to craft the missing bag" line (S:3203).
- SkyyMenu 0.3.5 L387 "Craft them in the Workbench tab Accessories and Bags." + its check L995 -> **SkyyMenu 0.3.6** (lean round, section 11),
  which also bumps `MODS_VERSIONS` (L318-321 still says Accessories 0.5.2).

---

## 5. /craft limiters: Memories level, bench tiers, knowledge

### 5.1 What the real bench refuses (VERIFIED, `CraftingManager.isValidBenchForRecipe(Ref, ComponentAccessor, CraftingRecipe)`, private; researcher B 5 / A F.3)

In this order: (a) **knowledge** - `isKnowledgeRequired()` and the player's known recipes do not contain the primary output id (offsets
63-112); (b) **Memories** - `getRequiredMemoriesLevel() > 1` and `MemoriesPlugin.get().getMemoriesLevel(world.getGameplayConfig()) <` it
(offsets 113-175; world = `((EntityStore) acc.getExternalData()).getWorld()`); (c) **bench** - some requirement with `type == bench type`,
`id.equals(bench id)` (no bench: Crafting / "Fieldcraft", tier 0), `requiredTierLevel <= BenchBlock tier`, and its augment tags granted
(empty = ok); (d) a Crafting bench other than Fieldcraft allows one queued recipe. Categories are never checked. Only `craftItem` and
`queueCraft` call it (caller scan), so /craft's instant craft (S:5884) and the Furnace / Tannery queue (S:5390) must COPY the rule.

**The Memories level** (`MemoriesPlugin.getMemoriesLevel(GameplayConfig)`): `MemoriesGameplayConfig.get(gc)` missing -> 1; else the count of
`getRecordedMemories()` against `MemoriesAmountPerLevel` (`Server/GameplayConfigs/Default.json`: [10, 25, 50, 100, 200]) -> highest step
reached + 2, else 1: under 10 -> 1, 10 -> 2, 25 -> 3, 50 -> 4, 100 -> 5, 200 -> 6. **Server-wide, not per player** (the recorded set is a
universe resource; `PlayerMemories` only holds catches until `recordPlayerMemories` moves them in). The bench and pocket windows DISPLAY it as
`windowData "worldMemoriesLevel"` (`BenchWindow.onOpen0`, `FieldCraftingWindow.onOpen0`). Every `CraftingRecipe` constructor defaults
`requiredMemoriesLevel` to 1. Vanilla: 38 recipes above 1, 19 with KnowledgeRequired (none inherited through Parent).

**What /craft lets players skip today (researcher B 7, simulated against Assets.zip):** 31 of the 38 - 14 themed chests (Furniture Bench,
levels 2-6), 3 portal keys + Portal_Device (Arcane Bench, 5), 12 Eternal seeds (Farming II-VII, 2-5), Upgrade_Backpack_3 (Workbench III, 5).

### 5.2 One gate for every path: `CraftGate` (new class in SkyySacks 0.7.13)

```java
// all javassist-legal (no generics / lambdas / enhanced-for)
public static int memLevel(Store st)                 // 1 on ANY failure (plugin missing, no world, exception): the strict answer
public static boolean memOk(CraftingRecipe r, int lvl) { int n = r.getRequiredMemoriesLevel(); return n <= 1 || lvl >= n; }
public static int capTier(String bench, int t)       // min(t, BENCH_MAX[bench]) ; unknown bench -> 1
public static int benchFit(CraftingRecipe r, HashMap acc, String only, boolean merged)   // 0 = ok, else NO_BENCH / TIER / AUGMENT / TYPE
public static int check(CraftingRecipe r, UUID u, Set known, Set coll, HashMap acc, int lvl, String tab)   // 0 ok | 1 KNOWLEDGE | 2 MEMORIES | 3 NO_BENCH | 4 TIER | 5 AUGMENT | 6 NO_OUTPUT
public static String why(int code, CraftingRecipe r, int lvl, HashMap acc)              // the player text (5.4)
```

- `memLevel`: researcher B's code - `st.getExternalData()` instanceof `EntityStore` -> `getWorld()` -> `MemoriesPlugin.get()` (may be null) ->
  `getMemoriesLevel(w.getGameplayConfig())`; public calls only (`CraftingRecipe.getRequiredMemoriesLevel`, `MemoriesPlugin.get`,
  `MemoriesPlugin.getMemoriesLevel`, `World.getGameplayConfig`, `Store.getExternalData`, `EntityStore.getWorld`). Computed ONCE per page
  build and once per click / queue (fresh), never per row. INFERRED: `build()` has the Store at hand through the page factory's call (the
  click path `handleDataEvent(ref, st, ...)` and `procQueue(p, st, ...)` S:5358 already carry it); the builder confirms with
  `tools/dev/reflect.py` and falls back to the Player's world if the page is built without a store.
- `benchFit` = today's `benchRecipes` test (S:5079-5101: retired skipped; merged tabs skip Furnace / Tannery / Processing-except-Salvagebench;
  `max(1, requiredTierLevel) <= accTier`) **plus**: tier CAPPED at the real bench maximum; `requiredAugmentTags` non-empty -> not satisfiable
  (no vanilla recipe uses them); only `Crafting` (or Processing + `instantProc`) types in the merged tabs, Processing Furnace / Tannery in the
  P: tabs, never Diagram / Structural; the `only` form for P:, K:camp (unchanged rule) and the new Accessories tab.
- **BENCH_MAX** (Java constant, computed at BUILD time from Assets.zip and re-derived by the harness): max tier = 1 + the number of
  `TierLevels` entries that carry an `UpgradeRequirement`; no `TierLevels` = 1. VERIFIED tonight from `Server/Item/Items/Bench/*.json`:
  Workbench 3 (3 entries, upgrades at 1-2), Armor_Bench 3, Weapon_Bench 3, **Farmingbench 8** (7 entries, ALL with an upgrade - tier 8 is
  reachable, and 3 vanilla recipes need it), Alchemybench 5, Furnace 2, Tannery 2, the rest 1 (`Bench.getUpgradeRequirement(n) =
  tierLevels[n-1].UpgradeRequirement` = the cost from n to n+1; `CraftingManager.startTierUpgrade` needs it, `finishTierUpgrade` sets
  tier+1 - researcher A E.1-2). Today's accessory maximums never exceed these (Farming stops at VII - question 4), so the cap only bites a
  hand-made acc:has entry such as `..._Furnace_T9` (today it would unlock tier 9).
- `check` order = the engine's: knowledge (existing `KnowSync.allowed`, S:1651-1663: unlocked bags / known output), then Memories, then bench,
  then `hasItemOutput` (existing review fix). **Collections tab (`C:`)**: knowledge + Memories apply; the bench test is SKIPPED (Skyy's rule:
  Collections "crafts there without its bench") - question 4 confirms. **Campfire tab**: the existing `campfireTier` rule + Memories.
- **Where it is called (every path, no exceptions):** `recipesFor` (S:5145-5180) for EVERY tab (today the knowledge gate only runs for
  `grp >= 0`, S:5177); `searchRecipes` (S:5192); the click in `handleDataEvent` (S:5859-5866, replacing the A:/C: special cases with one call,
  fresh `KnowSync.known(p)`, fresh `accessories()`, fresh `memLevel(st)`); `procQueue` (S:5358, before any material moves - today the P: tabs
  only check tier > 0 at click time). `build()` stores `this.memLvl = memLevel(st)` next to `this.known` (S:5706-5708).

### 5.3 The Accessories tab in /craft

- `buildTabs` (S:5128-5143): after Farming, before Campfire: `if (accTier(acc, "Accessorybench") > 0) t.add(new String[]{"A:acc", "Accessories"})`
  (`A:` prefix = instant, knowledge-gated like Crafting / Smithing / Farming).
- `recipesFor("A:acc")` = `benchRecipes(u, "Accessorybench")` through the gate; rows ordered by **`TabRank`** (the kit class emitted into
  SkyySacks' package), so /craft shows Skyy's table order, not `RecipeCmp` (S:2826-2845, which sorts bags Large, Medium, Rare, Small). The
  merged Crafting / Smithing / Farming tabs EXCLUDE requirements naming `Accessorybench` (add it to a `separateBench`-style test for the merged
  set only) so nothing is listed twice; search covers the Accessories tab too (search labels S:5803-5804).
- Server Setup `craft.accTab` OFF (section 8) = no separate tab: the table's recipes merge into Crafting like any other bench's.
- The Omni Bag recipe keeps its Collections-tab path (all five Legendary bags carried, S:5160-5161) AND appears in the Accessories tab.

### 5.4 What the player sees

- Page header gains a small line **"World Memories level M"** (the vanilla bench window shows the same number).
- Locked recipes are HIDDEN from every list (today's behaviour for unknown recipes), and when the Memories gate hid anything the tab ends with
  **"N more recipes need a higher world Memories level (this world: M)."**
- Click / queue refusals (the `info` line, existing style, nothing moves): knowledge **"You have not unlocked this recipe"** (existing);
  Memories **"This needs world Memories level N - this world is at M. Record more memories first."**; bench **"You need the <Bench name>
  Accessory in your Accessory Bag for this"** / tier **"You need the <Bench name> Accessory III or better for this (you have II)"**; augment
  **"This recipe needs a bench upgrade /craft cannot provide"**.
- No vanilla text is reused for these (the engine's refusal is a server log line only: "doesn't have the required world memories level!").

### 5.5 Build-time proof (SkyySacks `_engine_facts` + the kit probe; needles in order, researcher B 5)

- `CraftingManager.isValidBenchForRecipe`: `isKnowledgeRequired`, `getKnownRecipes`, `getRequiredMemoriesLevel`, `if_icmple`, `MemoriesPlugin.get(`,
  `World.getGameplayConfig`, `MemoriesPlugin.getMemoriesLevel`, `getRequiredMemoriesLevel`, `if_icmpge`, `getBenchTierLevel`, `requiredTierLevel`,
  `benchHasRequiredAugmentTags`.
- `MemoriesPlugin.getMemoriesLevel`: `MemoriesGameplayConfig.get`, `getRecordedMemories`, `Set.size`, `getMemoriesAmountPerLevel`, `iconst_2`, `iadd`.
- A count of vanilla recipes with `RequiredMemoriesLevel > 1` from Assets.zip (38 tonight) is PRINTED, not asserted (a game update may change it).
- In-game test commands (TEST-CHECKLIST): `/memories level`, `/memories setCount <n>`, `/memories unlockAll`, `/memories clear`. **Warning
  for Skyy:** `setCount` REPLACES the world's recorded memories (clears, refills with the first n, saves) - test it in a throwaway world or
  accept that the HUD-mod world's memory progress changes.

---

## 6. Removing the Workbench tab safely

- The tab exists ONLY at runtime: `WbTab.scan` / `applyTo` append a `BenchCategory` to every Workbench `CraftingBench.categories` array at
  `start()` and after asset reloads (WB:464-525, 583-598). Nothing is saved anywhere. With 0.5.4 + 0.7.13 no code appends it, so the Workbench
  shows its four vanilla tabs again (Survival, Tools, Crafting, Tinkering - `Bench_WorkBench.json`).
- **Drop** from both builds: the `WB` import (A53:183, S:117), `WB.probe` / `emit` / write-out (A53:3982-3985, S:6236-6237, 6316-6317), the
  `@WBSETUP@` lines (BlockType + CraftingRecipe listeners, A53:4018, S:6285), `WB.start_java` (A53:4019; S:6290-6295 keeps its appended
  `BenchLink.start()` on the ACT start text), `WB.LANG_LINES` (A53:4322, S:6394), the per-mod icon copies (A53:4337, S:6397), `_wbtab_checks`
  (A53:4344-4355, S:6455-6482), `WB_REQ`. **Replace** with the ACT equivalents (3.2).
- **Keep** (ported into ACT): WbRank's order and the TreeSet swap (now on the table's registry), the CraftingRecipe-reload listener (a reload
  rebuilds recipe sets: `onRecipeLoad` reuses `registries` / `categoryMap` via `computeIfAbsent`, so a reload ADDS INTO our TreeSet and keeps
  it sorted - WB:17-19 and the probe lines that guard it).
- **`tools/skyywbtab.py` stays in the repo** - the generated 0.5.2 / 0.5.3 / 0.7.10-0.7.12 scripts import it and must keep building.
- **Harness:** section W of both tests (`WB.harness_checks`, test L1277-1278 / L1429) is replaced by `ACT.harness_checks`; a new check asserts
  no class of either jar references `Workbench_SkyyAccessories` or `CraftingBench.categories` (constant-pool scan, `tools/dev/cpstrings.py`).
- **Skew** (3.3): an old jar still appends its tab for its own recipes; harmless.

---

## 7. Existing items and saved data: nothing lost

| Thing | What happens |
|---|---|
| Owned accessories, bags, Omnis, Accessory Bags | ids unchanged; they keep working; the Omni grants the new bench by computation (4.2) |
| Learned recipes (the engine's per-player known set; KnowSync teaches bag recipes from Collections) | recipe ids unchanged -> still learned; KnowSync's MANAGED list unchanged |
| SkyyCollections rewards / `coll:recipes` / `coll:fn:where` | recipe ids unchanged; its default excluded-bench list does not name the table; the Collections tab still crafts them bench-free (question 4) |
| The Workbench tab | runtime-only, nothing saved; simply gone |
| Placed Accessory Tables | none exist before this build |
| Players holding a Workbench Accessory for /craft accessories | lose that access until they craft the table + its accessory or hold an Omni - the texts (4.3) and the TEST-CHECKLIST say so; no item is taken |
| SkyyIslands 0.5.5 starter kit `Skyy_Accessory_Bag:1` (L473) | unchanged |
| SkyyAccessories config | no new keys |
| SkyySacks config | two new rows (section 8); a missing key = its default, the kit adds the line on first change; no migration, no rewrite of existing files |
| Rollback | to 0.5.3 + 0.7.12: safe (no data change); the Workbench tab comes back; the table item disappears from inventories only if someone crafted one in between (it is a plain item: unknown ids are kept by the engine but render as missing) - deploy, test, then let people craft tables |

---

## 8. Server Setup rows (config kit `tools/skyycfg.py`, `tools/CONFIG-CONTRACT.md`)

| Mod | Key | Label | Type / default | Live? | What |
|---|---|---|---|---|---|
| SkyySacks | `craft.memoriesGate` | Memories level check in /craft | bool, **on** | yes (read per page build) | off = the 0.7.12 behaviour (an owner who runs a creative server may want it); the header line and the "N more recipes" line follow it |
| SkyySacks | `craft.accTab` | Accessories tab in /craft | bool, **on** | yes | off = the table's recipes merge into Crafting like other benches (5.3) |
| SkyyAccessories | - | - | - | - | no new rows: the table and its recipes are assets, not settings |
| SkyyMenu 0.3.6 | - | - | - | - | `MODS_VERSIONS` + the SkyyAccessories help text (4.3) |

Both rows go in the existing /craft category of `SACK_CFG_ROWS` (the builder reuses the category the other `craft.*` / `bags.*` rows use);
times are not involved. Recipe inputs are NOT settings (assets are baked at build time) - question 2 fixes the table's cost.

---

## 9. Tests - the harnesses must EXECUTE these (bare JVM: the game's JRE, `-Xverify:all`, `-XX:-UsePerfData`, TEMP in scratch, HytaleServer.jar read-only + the jars + tools/javassist.jar; the pattern of both existing harnesses, test L184 / L194)

Existing machinery to reuse (VERIFIED in the harnesses): `Item.CODEC.decodeJsonAsset` with a stand-in asset store (acc test N1, L1929);
a fake `SimpleCraftingWindow` subclass whose `getExtraResourcesSection()` feeds a chest container (sacks test L2034-2050), `bench_craft` =
the window's combined container + counted removal (L2142-2155), `BenchLink.start()` + the outbound filter recorder (L2220), the
item-conservation fuzz (section Z), both mods' start sequences alone / together on scratch copies of live data (section L, L1281+),
`WB.harness_checks` on real engine objects incl. a REAL `CraftingWindow`'s windowData (WB:690+).

### 9.1 Kit test `tools/skyyacctable_test.py` + `ACT.harness_checks` (run inside both harnesses)
1. **Bench asset decode:** `ACT.table_files()` JSON through `Item.CODEC` (and the embedded BlockType through `BlockType.CODEC`): 0 validation
   failures, 0 unknown keys; `processConfig` gives `Use = *Simple_Crafting_Default`; `getBench()` is a `CraftingBench` with id `Accessorybench`
   and one category `Accessorybench_All`; `getItem()` non-null (else `BenchWindow.<init>` throws). Control: a texture under a wrong root, a tab
   icon under `Icons/ItemsGenerated/`, an unknown hitbox and an unknown key are each refused (researcher A E3 reproduced as a permanent test).
2. **Window data:** a real `SimpleCraftingWindow` on the decoded BlockType (researcher A E4): windowData `type 0`, `id Accessorybench`, one
   category, `craftableRecipes` = exactly the ids of the jars on the classpath (48 / 21 / 69-70) in `EXPECTED` order; a recipe naming
   `Workbench_SkyyAccessories` or an unknown tab never appears.
3. **Order on real registries:** TreeSet installed in both start orders and alone; a recipe reload (`onRecipeLoad` with a bag recipe) keeps
   it sorted; `TabRank.rank` == `rank_py` on `EXPECTED` + `WB.EDGE_IDS` + 200 random ids; vanilla Workbench tabs untouched (4 categories,
   `VANILLA_WB` unchanged).
4. **Determinism + SHA:** two `table_files()` calls give identical bytes; `table_sha` equals the constant each jar carries; the texture keeps
   192x128 and every alpha byte of the vanilla texture; the hue mask selects 1,500-3,000 texels and no `#361b0a` texel; the icon is 64x64.
5. **One mod missing:** with only one jar on the classpath the table decodes from that jar and (2) lists only that mod's recipes; the bridge
   SHA compare WARNs only when the two constants differ (fed a fake value).

### 9.2 SkyyAccessories 0.5.4 harness (`test_skyyaccessories_0.5.4.py`: every 0.5.3 check + section T + compare with 0.5.3)
1. 69 (70) current items listed, 48 recipes; every recipe = `TABLE_REQ` (the bag: Fieldcraft first + the table), `Bench_Accessory` the one item
   at `Workbench / Workbench_Crafting`; `ACT.recipe_checks` passes; no `WB_REQ`, no `Workbench_SkyyAccessories` anywhere in the jar.
2. **Omni grant:** `AccDefs.benchList({Omni})` has 12 entries incl. `Skyy_Accessory_Accessorybench_T1`; `AccStore.has` (acc:fn:has) answers
   true for it and false for `..._T2`; `publish()` writes it into `acc:has:<uuid>` on the real bridge (section B's publishing paths, L1469).
3. **The table is not an accessory:** `isAccessory("Bench_Accessory")` false; the bag's Equip list (`carried`) skips it; `benchOf` null.
4. The Omni recipe = 12 inputs; the table accessory recipe = table + 4 copper at the table; 50 booster tooltips say "Accessory Table".
5. `ACT.harness_checks` (9.1); the compare-with-0.5.3 section lists exactly the expected class / method changes (no `WbTab` / `WbAssetL`
   classes, `TabRank` / `TabSort` / `TabAssetL` added).

### 9.3 SkyySacks 0.7.13 harness (`test_skyysacks_0.7.13.py`: every 0.7.12 check + sections G (gate), A (Accessories tab), T2 (table craft))
1. **A craft at the new bench:** the T-section fake bench built on the decoded table BlockType; player inventory holds 3 Bolt of Wool, the
   Mining bag pool holds 4 Copper Ingots; `BenchLink.onExtras` merges the bag counts into the window's `ExtraResources` (**bag link at the new
   bench** - `BenchLink.isBench` accepts any `SimpleCraftingWindow`, S:~3850); `bench_craft(Skyy_Sack_Mining_Small)` succeeds, the inventory loses
   3 bolts, the pool drops by exactly 4 copper (the Z-style conservation audit), the pocket window does NOT offer the recipe (Fieldcraft-only).
   A recipe naming only `Accessorybench` fails `isValidBenchForRecipe` (private; called by reflection with a `Ref` + `ComponentAccessor` built
   the way researcher A's E2 / E4 built theirs - INFERRED feasible; if the bare JVM cannot feed it, the needle proof of 5.5 plus a Python
   mirror of rule (c) stand in) against a Workbench `BenchBlock` and passes against the table's at tier 1; `RequiredTierLevel 2` fails at tier 1.
2. **/craft tab:** `CraftPage.buildTabs` with `acc:has = Skyy_Accessory_Accessorybench_T1` shows "Accessories"; `recipesFor("A:acc")` = the table
   recipes allowed by knowledge (free mode / coll:recipes) in `TabRank` order; Crafting / Smithing / Farming list none of them; search finds
   "Mining Bag" there; with the Omni's synthetic entry the same; without any entry no tab and no table recipe anywhere; `craft.accTab` off ->
   merged.
3. **Limiters:** `memOk` against the vanilla recipes with `RequiredMemoriesLevel > 1` (loaded from Assets.zip) at levels 1..6 - visible counts
   match the level thresholds (level 1 hides all 38, level 6 shows all given bench access); the Python mirror of `getMemoriesLevel` for recorded
   counts 0, 9, 10, 24, 25, 49, 50, 99, 100, 199, 200, 500 -> 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6; `memLevel(st)` returns 1 in the bare JVM
   (no MemoriesPlugin) and the gate hides level-2+ recipes; tier cap `..._Furnace_T9` -> 2, `..._Workbench_T3` -> 3, `..._Farmingbench_T9` -> 8;
   a synthetic recipe with an augment tag is refused; Diagram / Structural requirements never list; a page built at level 6 (injected) then
   clicked at level 1 is refused with the exact text and moves nothing; `procQueue` refuses a tier-2 Furnace recipe with a T1 accessory; the
   Collections tab applies knowledge + Memories but not the bench; `craft.memoriesGate` off restores 0.7.12 listing (header line gone).
4. **Bytecode needles** of 5.5 (also run at build time in `_engine_facts`).
5. Sections L (both start orders, alone, no file churn) extended: the four shared files + lang lines are byte-identical in the two jars on the
   classpath; `_bag_assets_check` scoped to `Server/Item/Items/Utility/` still counts 21 bags and reads `KnowledgeRequired` only there.
6. Rows `craft.memoriesGate` / `craft.accTab` through the kit set path (like `bags.pocketCraft`, test L435-441).

### 9.4 Cross-check (one agent, after both reviews)
All SET jars in one JVM `-Xverify:all`; the Adventurer permission audit (`tools/dev/permscan.py`); `python tools/ci/lint.py` 0 fails; both
jars opened and the shared entries compared byte for byte; the two builds' printed SHA equal; `python tools/deploy_set.py --check`; no class
in either jar references `Workbench_SkyyAccessories`.

### 9.5 In-game (TEST-CHECKLIST, numbered for Skyy)
1. Workbench: the Accessories & Bags tab is gone; Crafting tab shows "Accessory Table" (cost per question 2). 2. Craft two tables, place one:
"Press [key] to open Accessory Table"; one tab "Accessories and Bags"; order = section 2 (this answers the client-order question; report if the
Omni items are not last). 3. Craft a Normal Mining Bag at the table with copper only in the Mining bag (bag link). 4. Craft the Accessory Table
Accessory from the second table; put it in the bag; /craft shows an Accessories tab in the same order. 5. Take it out; the tab is gone; an Omni
brings it back. 6. `/memories level`; with a Furniture Bench accessory the themed chests are hidden and the page says "N more recipes need a
higher world Memories level"; `/memories unlockAll` (throwaway world!) shows them; crafting one works. 7. Accessory Bag still crafts from
the inventory (question 3). 8. Upgrade a Farming Bench to tier 2 in the world and compare its recipe list with /craft at Farming II (parity).

---

## 10. Risks

| # | Risk | Status | Mitigation |
|---|---|---|---|
| 1 | The client re-sorts recipes inside a tab | UNVERIFIED (both benches) | Skyy's first look at the deployed 0.5.2 tab or test step 2; fallback = tier tabs (1.5), a kit-table switch + rebuild |
| 2 | The client hides / shows an empty tab, shows the tab name or only the icon | UNVERIFIED | one tab, never empty; vanilla key + lang line |
| 3 | The two copies drift (a build on a different Assets.zip or kit version) | mitigated | one generator, SHA printed, cross-check byte compare, runtime WARN |
| 4 | Load-order winner flips with version numbers | VERIFIED, harmless while identical | (3) |
| 5 | The recoloured Arcane bench looks wrong / too close to the Arcanist's Workbench | UNVERIFIED | stage 0 preview sheet, Skyy picks A / B or asks for another colour; a texture-only change later needs no code |
| 6 | `render_icon` unproven for the block view | VERIFIED limit (6.51 vs 4.0) | `recolor_icon` on the vanilla icon with hue-mask weights; whole-icon tint fallback |
| 7 | Memories level is server-wide; a creative server never records memories | VERIFIED | `craft.memoriesGate` row; `/memories` commands for testing |
| 8 | Players lose /craft access to accessories until they craft the table accessory | by design | texts (4.3), TEST-CHECKLIST note, the Omni covers it |
| 9 | `_bag_assets_check` / `recipe_checks` break on the new JSON | VERIFIED (S:6400-6452, WB:601-631) | scoped / replaced (3.4, 6) |
| 10 | `need_item` refuses our own bench item; the icon path is never checked | VERIFIED (A53:4186, 4190) | 4.1 |
| 11 | Harness counts (68 items, 47 recipes, 11 benches) | VERIFIED | 4.1; the builders grep `== 11`, `47`, `68` |
| 12 | A hand-edited acc:has entry unlocking tier 9 | VERIFIED gap | BENCH_MAX cap (5.2) |
| 13 | The Collections tab can craft a memory-gated reward an admin added | VERIFIED (SkyyCollections `validate()` only checks the recipe exists and the bench is not excluded) | knowledge + Memories gates apply there (question 4) |
| 14 | "Duplicated Asset Count" grows by 4 | VERIFIED harmless | note in the log line |
| 15 | Both jars reload the identical asset twice at boot (recipe regenerated under the same id) | VERIFIED harmless | - |
| 16 | `TabSort` sorts before SkyySacks' recipes are registered when Accessories starts first | handled today (owner / fallback + reload listener) | kept |

---

## 11. Build stages and agents (FULL round: a new system, two mods, items that must not be lost; PROJECT-RULES section 4 / 8)

| Stage | Who | Does | Done when |
|---|---|---|---|
| 0 Art proof + decode proof (can start now, read-only game files) | **Opus** (art + engine), local | ART 1.1 hue mask + icon weights (+ `verify` checks); styles A / B of the table texture + icons; preview sheet for Skyy (SendUserFile); the kit skeleton with `table_files` and the decode / window-data test (9.1 items 1-2, 4) | `python tools/skyyacctable_test.py` passes; Skyy has the sheet |
| 1 Kit | **Fable or Opus**, local | `tools/skyyacctable.py` complete (3.2: tables, emit, probe, recipe_checks, harness_checks, SHA, bridge warn) + its test | kit test passes incl. 9.1 items 3 and 5 |
| 2a SkyyAccessories 0.5.4 | **Opus**, local | `tools/acc_0_5_4_patch.py` on the GENERATED 0.5.3 script (header; BENCHES row; counts; `ACT` wiring; texts; `need_item`; icon check; the Omni; Farming VIII if yes); `test_skyyaccessories_0.5.4.py` (9.2); build ends `assembled ...jar`; lint 0 | harness green |
| 2b SkyySacks 0.7.13 | **Opus**, local, parallel with 2a | `tools/sacks_0_7_13_patch.py` on the generated 0.7.12 script (header; `ACT` wiring; `sack_item` requirement; `CraftGate` + hooks 5.2; Accessories tab 5.3; texts 5.4 / 4.3; rows 8; `_engine_facts` needles; scoped asset check); `test_skyysacks_0.7.13.py` (9.3) | harness green |
| 3 Review x2 + an adversarial limiter critic | **Sonnet** | one review per mod; the critic enumerates every vanilla recipe (38 memory-gated, 19 knowledge, every tiered one) against /craft's lists and clicks in the harness and tries to craft what the bench refuses | PASS or findings -> the builders fix |
| 4 Cross-check | **Sonnet** | 9.4 on all SET jars | READY |
| 5 SkyyMenu 0.3.6 (lean) | **Sonnet** | `MODS_VERSIONS` (Accessories 0.5.4, Sacks 0.7.13), the help text + its check (4.3) | build + its harness + one review |
| 6 Pin, commit, deploy | main session | pin 0.5.4 + 0.7.13 + 0.3.6 TOGETHER in `tools/deploy_set.py`; commit + push; backup; `python tools/deploy_set.py --yes` with the game closed; TEST-CHECKLIST (9.5), HANDOFF row + log line, RESUME, OPEN-QUESTIONS answers | live |

Rules every agent follows: `tools/AGENT-BRIEF.md` (no `--deploy`, scratch only under `tools/dev/scratch/<task>/` and delete only your own,
TEMP in scratch, `-XX:-UsePerfData`, never write in AppData, never commit vanilla pixels - the texture / icons are generated into the jars).
0.5.4 waits for the Night Vision round's 0.5.3 to be final (it is the SET pin already); never re-run `acc_0_5_3_patch.py`.

---

## 12. Questions for Skyy (each with the default the build uses if you say nothing)

1. **Name and look.** Default: the block is the **"Accessory Table"** (id `Bench_Accessory`, bench id `Accessorybench`), the Arcanist's
   Workbench model with a **deep violet drape and violet gem** (style A; B = teal) - you pick from the preview sheet. Its /craft accessory
   is then called **"Accessory Table Accessory"**. If that name grates, say a table name in the vanilla style ("Jeweler's Workbench" ->
   "Jeweler Accessory") and we use it everywhere.
2. **What the table costs at the Workbench.** Default: **6 logs (Wood_Trunk) + 4 Rock + 2 Copper Ingots + 4 Cotton Scraps**, any Workbench
   tier, in the Workbench's Crafting tab next to the other benches (vanilla benches cost 2 copper + 10 logs + 5 rock and up). It must stay
   cheap: the Accessory Bag and the Normal bags are early items.
3. **Accessory Bag from the inventory.** Default: **keep it pocket-craftable AND list it at the table** (the vanilla two-requirement pattern,
   as today) - a new player needs the bag before anything else. Alternative: table only (strictly "everything moves").
4. **Limiter scope + Farming VIII.** Default: (a) the knowledge and Memories checks also apply to /craft's **Collections** tab, while Collections
   recipes still need **no bench** there (your earlier rule); (b) add **Farming Bench Accessory VIII** in this round (the real bench reaches
   tier 8 and 3 vanilla recipes need it; the Omni then grants VIII; one more item + recipe, +1 to every count) so /craft matches the real bench
   exactly. Say no to (b) to keep Farming at VII.

Still UNVERIFIED after this spec (in game only): the client keeping the server's order; empty-tab and tab-name display; how the recoloured
table looks; the Memories lock texts in the vanilla table window for KnowledgeRequired bags you have not unlocked (expected: the vanilla
"unknown recipe" lock, as at the Workbench today).
