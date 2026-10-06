# Skyy's Pocket Dimension - CurseForge release kit (page text, features, config, FAQ, changelog, shot-list, licence note)

Cloud draft, 2026-10-06. Skyy posts the Magic Bags mod standalone (LOCKED 2026-10-03, docs/answered/project.md): bag types + tiers, `/sacks`, auto-pickup, benches and pocket crafting pull from bags, auto-refill, the Workbench tab; **no /craft**; bag tiers unlock by crafting the previous tier when SkyyCollections is absent.
Source of truth: `SkyySacks/build_skyysacks_0.7.12.py` (the docstring history, bag table, config rows). Everything marked ⚠ is a fact the standalone build still has to make true (see "For the local session"). Paste-ready sections are in code blocks.

## 0. Name, summary, categories

| Field | Value |
|---|---|
| Project name | **Skyy's Pocket Dimension** |
| Short summary (about 250 characters) | `Magic bags with a pocket dimension inside: your ores, logs, crops and drops are collected automatically, your benches and crafting use them without you digging through chests, and your hotbar refills itself. Five bag types, five rarities.` |
| Category / tags | QoL, Inventory, Storage, Crafting (CurseForge Hytale categories: pick "Utility / Quality of Life" + "Inventory") |
| Game version | Hytale server 0.6.8 (release). 0.7 pre-release **not tested** |
| Dependencies | none required; optional: SkyyProfiles (separate bag pools per profile), SkyyCollections (bag recipes by collection) |
| Type | server plugin (jar) + asset pack parts inside the jar |

## 1. The page (description) - paste-ready

```
# Skyy's Pocket Dimension

Your inventory, but with a pocket dimension attached.

Craft a Magic Bag and the things you collect start flowing into it by themselves: ores, logs, crops, drops, bars and more.
Open your pocket dimension with /sacks (or /pd or /bags) to see everything you hold, take out any amount, or put items back.

## Why you will like it
- No more full inventory. Mining, chopping and farming drop straight into your bags.
- Your benches use your bags. Open a Workbench, an Armor Bench, a Furnace... and the materials in your bags count as if they were in the chest next to you.
- Inventory crafting uses your bags too.
- Your hotbar refills itself. Run out of arrows, blocks or torches in your hotbar? The stack tops up from the bag.
- Five bag types, five rarities: Mining, Foraging, Farming, Combat, Smithing; Normal, Unique, Rare, Legendary, and the Mythic Omni Bag that holds a hundred thousand of EVERYTHING.
- Each bag holds a lot of each item (not a few slots): a Normal bag holds up to 640 of each item, a Legendary bag 20,160.
- Everything is yours. Bags and pools belong to the player who owns them, so nothing leaks to other players.
- Works with other mods' items. Anything the bag types recognise (Ore_, Wood_, Plant_, Food_ ... and the item groups below) is collected, the rest stays in your inventory.

## How it works
1. Craft a Normal bag at the Workbench (tab "Accessories & Bags"). Carry it in your inventory.
2. Collect things the normal way. Every 2 seconds the bag takes what you picked up (it never takes your hotbar stacks or what you chose to keep).
3. Press /sacks to open the page: one tab per bag type, a grid of every item, Withdraw, Put back, Deposit all.
4. Craft: open any bench, the bag materials are there. Pocket crafting (the grid in your inventory) uses them too.
5. Upgrade: a better bag is crafted FROM the previous one (Normal -> Unique -> Rare -> Legendary), so you always keep progressing.

## The bag types
| Bag | Collects |
| Mining | stone, ores, rubble, gems, clay, sand, coal |
| Foraging | logs, sticks, fibre, bark, sap |
| Farming | crops, raw meat and fish, eggs, essences of life |
| Combat | bones, feathers, venom sacs, chitin, essences |
| Smithing | bars, leather, hides, cloth scraps, straps, studs, charcoal |

## Rarity and capacity (per item)
Normal 640 - Unique 2,240 - Rare 6,720 - Legendary 20,160 - Mythic Omni 100,000 of every type. Bags of the same type ADD UP.

## For servers
Everything is configurable: bag capacities, free recipes, cooked food routing, refill settings. Works with or without a permissions plugin (commands are open to players by default; admin settings use the skyysacks.admin node).
Pools are saved per player (and per profile when SkyyProfiles is installed). Saves are atomic; a crash never loses your pool.
```

## 2. Feature list (for the page's "Features" section and the changelog source)

| Feature | In the standalone? | Notes |
|---|---|---|
| 5 bag types (Mining, Foraging, Farming, Combat, Smithing) x 4 rarities + Mythic Omni Bag | yes | 21 bag items, crafted at the Workbench tab |
| Auto-pickup sweep (every 2 s) | yes | leaves hotbar / backpack stacks and "kept" counts |
| Withdraw any amount, Put back, Pick up all, Deposit all | yes | "kept counts" stop the sweep re-taking what you took out |
| **Benches use your bags** (OpenWindow/UpdateWindow merge) | yes | 0.7.12 |
| **Inventory (pocket) crafting uses your bags** | yes (switch `bags.pocketCraft`) | |
| **Stack auto-refill** (Hotbar only / Full inventory / Off per player) | yes | switch `bags.refill`, default `bags.refillDefault` |
| Bags add up (carried bags of a type sum) | yes | |
| Workbench tab "Accessories & Bags" | yes (fallback copy) | in the full pack SkyyAccessories owns the tab |
| Per-profile pools | yes, when SkyyProfiles is installed | else one pool per player |
| Cooked food stays out of the Farming bag | yes (default) | switch `bags.cookedFood` |
| In-game settings | **config file in the standalone**; full Server Setup page only with SkyyMenu | ⚠ see section 8 |
| `/craft` page with tabs (Smithing, Farming, Furnace, Tannery, Campfire, Collections) | **no (removed, Skyy's lock)** | ⚠ Furnace / Tannery queue tabs go with it |
| Collections tab, Campfire / Cooking hooks, gear roll for crafted gear | no | pack-only (SkyyCollections / SkyyCooking / SkyyGear) |

## 3. Commands and permissions

| Command | Who | What |
|---|---|---|
| `/sacks` (aliases `/pd`, `/bags`) | every player (default group) | opens your pocket dimension; needs a magic bag of the type on you |
| `/craft` | **not in the standalone** | (full pack only) |
| Permission `skyysacks.admin` | admins | Server Setup rows when SkyyMenu is installed; ⚠ standalone needs a config-file route |
Commands are open to the default player group (the "Adventurer" group); the admin commands (none in the player build) follow the project's rule "requirePermission + empty group list".

## 4. Configuration (`config.properties` in `Skyy_SkyySacks/`)

| Key | Default | What it does |
|---|---|---|
| `bag.small` | 640 | most of each item a **Normal** bag holds |
| `bag.medium` | 2240 | **Unique** bag |
| `bag.rare` | 6720 | **Rare** bag |
| `bag.large` | 20160 | **Legendary** bag |
| `bag.omni` | 100000 | **Mythic Omni Bag**: most of each item of EVERY type |
| `bags.freeRecipes` | false | on = every player knows every bag recipe; off = bag recipes unlock by crafting the previous bag (or collections, with SkyyCollections) |
| `bags.cookedFood` | false | on = cooked food goes to the Farming bag as well |
| `bags.refill` | true | master switch for stack auto-refill |
| `bags.refillDefault` | hotbar | players who never chose use this (`hotbar` / `full` / `off`) |
| `bags.pocketCraft` | true | inventory (pocket) crafting uses the bags |
| `bags.benchChests` | false | fallback: a bench with bags linked reports 1 nearby chest (only if benches ignore bag items) |
| `craftSearch`, `bench.*Cap` | n/a | belong to /craft; removed in the standalone |
Player settings (refill mode) live in `refill.properties` and the bag page. Config changes are validated and clamped (an order-breaking change like Unique < Normal asks first with the SkyyMenu page; in the file, an invalid line is clamped and logged).

## 5. Compatibility

| Topic | Notes |
|---|---|
| **Other inventory / storage mods** | bags only take **items by id group** (the bag types); items of mods that use the vanilla `Ore_` / `Wood_` / `Plant_` / `Ingredient_` id patterns are collected, anything else stays. Test with: backpack mods, sort mods |
| Mods that change crafting windows | the standalone swaps the vanilla pocket crafting window and merges extra materials into bench windows (a packet filter). Mods doing the same may conflict: switch `bags.pocketCraft` off first |
| Hytale updates | the bag item lists are derived from the live asset map at build time and rebuilt on update; a Hytale update that renames items makes unknown ids stay in the inventory (never deleted) |
| Multiplayer | all pools are per player; two players cannot see each other's bags; tested only with 2 accounts on a test world (TEST) |
| Creative mode | bags still work; nothing is created |
| SkyyProfiles | pools per profile; without it everything is profile 1 |

## 6. FAQ (paste-ready)

```
**Do I lose items if I uninstall the mod?** No item is ever deleted by the bags, but items inside a bag are stored in the mod's save folder (Skyy_SkyySacks). While the mod is missing you cannot take them out. Reinstall, or ask your server owner to restore the folder.

**Why did my hotbar stack not go into the bag?** Hotbar and backpack stacks are not swept; only items in your main inventory. Withdrawn items are also "kept" so they are not taken back at once.

**Can two players share a bag?** No. Each player has their own pools.

**How do I get the Mythic Omni Bag?** Craft it from one Legendary bag of every type (and the Omni ingredients) at the Workbench tab.

**Can I turn auto-pickup off?** Take the bag out of your inventory: the sweep only runs when you carry a bag of that type.

**Does it work with chests?** The bag is not a chest. For a bench, the "chest" count can be faked with bags.benchChests if your benches ignore bag items.

**Is it multiplayer safe?** Item moves run on the world thread, pools are saved atomically, and the bags log every move.

**Where is /craft?** In the Skyy pack only. This mod uses the vanilla benches and pocket crafting.
```

## 7. Install and screenshot shot-list

### Install
1. Close the server. 2. Copy `SkyyPocketDimension-<version>.jar` into the server's `Mods` folder. 3. Start the server once; the folder `Skyy_SkyySacks` appears. 4. In game: craft a bag at the Workbench tab **Accessories & Bags**, press `/sacks`.
Uninstall: stop the server, remove the jar; keep `Skyy_SkyySacks` if you will come back.

### Screenshot shot-list (about 10)
| # | Shot | Why |
|---|---|---|
| 1 | The /sacks page, Mining tab, full of items, one Rare Mining Bag in the hotbar | the hero image |
| 2 | The five tabs (Mining ... Smithing) with the grey "how to craft" tab visible | shows the bag types |
| 3 | The Workbench tab "Accessories & Bags" with the bag recipes | how to craft |
| 4 | A bench window (Armor Bench) crafting with materials from the bag, with a caption "materials come from your bags" | the main feature |
| 5 | Inventory crafting with bag counts | feature |
| 6 | The hotbar refilling (before / after of an arrow stack) | feature |
| 7 | The Mythic Omni Bag tooltip and its tabs | endgame |
| 8 | The rarity colours of the five bags side by side (dropped items on the ground) | looks |
| 9 | The bag page's refill setting (Hotbar only / Full / Off) | settings |
| 10 | A capacity tooltip ("Normal 640 / Legendary 20,160") | numbers |

## 8. Changelog template
```
## 1.0.0
- First public release.
- Five bag types (Mining, Foraging, Farming, Combat, Smithing) in Normal, Unique, Rare and Legendary, plus the Mythic Omni Bag.
- Auto-pickup, Deposit all, withdraw any amount.
- Benches and inventory crafting use the bags.
- Hotbar stack auto-refill (Hotbar only / Full inventory / Off).
- Workbench tab for the bag recipes.
### Known issues
- (list)
### Compatibility
- Hytale server 0.6.8.
```
Versioning suggestion: **1.0.0** for the first CurseForge file; patch = fixes, minor = new bag features (in the pack the numbering is 0.7.x; the release uses a fresh 1.x line so players are not confused).

## 9. Licence and asset note (answers the "licence / asset check" part of the lock)

| Question | Answer / what to check |
|---|---|
| Repo | the SkyyWynnBlock repo is **public** (PROJECT-RULES 2) |
| Vanilla assets | the mod must **not ship vanilla-derived files**; bag item art and textures are generated at build time from vanilla textures (art kit `tools/skyyart.py`) and **must be checked: a generated texture derived from a vanilla one is still a derivative** (⚠ review Hytale's mod licence / EULA; same rule as the pack: "generate them into the jars at build time instead of committing") |
| Other authors | no other author's code or assets in this mod (SkyySacks is Skyy's own); the design borrows **ideas** from SkyBlock sacks (Hypixel) - ideas only |
| Licence field on CurseForge | needs a choice by Skyy: **All Rights Reserved** (default, safest) or a permissive licence (MIT / Apache-2.0). Recommended: All Rights Reserved at first (the pack code stays Skyy's) with permission for server owners to use it freely |
| Third-party tools | javassist (used to build; check its licence MPL / LGPL / Apache for redistribution of the jar; the jar contains only compiled output) |
| Trademarks | name uses "Skyy's"; do not use Hypixel/Hytale logos in screenshots as the project icon |
| Hytale mod policy | follow Hypixel Studios' mod policy for monetisation (none: free) |

## 10. For the local session (UNVERIFIED / to make true before posting)
| # | Check |
|---|---|
| 1 | ⚠ The standalone **config route without SkyyMenu**: today the Server Setup page lives in SkyyMenu; without it the config is file-only. Decide: ship a tiny `/sacksadmin` or just document the file. |
| 2 | ⚠ **/craft removal**: the Furnace / Tannery queues, Campfire and Collections tabs, `bench.*Cap` rows and the `craftSearch` row are /craft features; check nothing else depends on them (processing store, the profile switch hooks). |
| 3 | ⚠ **Bag unlock rule without SkyyCollections**: the 0.7.12 code frees every bag recipe when SkyyCollections is missing (docstring: "free when bags.freeRecipes is on or SkyyCollections is missing"), while Skyy's lock says tiers unlock by **crafting the previous tier**; the recipes already need the previous bag as an ingredient, so the rule holds for tiers II+, but the **first (Normal) bag** needs a free recipe: confirm. |
| 4 | The Workbench tab "Accessories & Bags" is owned by SkyyAccessories in the pack; the standalone ships the fallback copy (tools/skyywbtab.py). Check no duplicate tab when both are installed. |
| 5 | The **permission group** audit (Adventurer) passes with only `/sacks` in the jar. |
| 6 | A **second-account multiplayer test** on a separate world (Skyy's rule) before posting; and a Hytale 0.7 pre-release smoke test. |
| 7 | Mod id / package name for the release (a new folder, `Skyy_SkyyPocketDimension`?) and the migration path from `Skyy_SkyySacks` (same save folder: keep). |
| 8 | CurseForge "Project ID" / File name conventions (`SkyyPocketDimension-1.0.0.jar`). |

## 11. Questions for Skyy
1. Licence: All Rights Reserved (recommended at first) or a permissive licence?
2. Name of the jar and the config folder: keep `Skyy_SkyySacks` (no migration) or rename to Pocket Dimension?
3. Should the first Normal bag be free-craftable (default free recipe) in the standalone, since there is no collection to unlock it?
