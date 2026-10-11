# Hubs - the SkyWynn Menu as a few hubs with tabs (+ Accessory Bag v2, + the Sky Window look)

*Local spec 2026-10-10. Spec only: nothing is built. Owner: Skyy (they/them). Hubs reuse today's pages. Each mod adds its own tab
through the bridge, so nothing is rewritten centrally.*

## 0. Decisions this spec follows

| Source | Skyy said (trimmed) | Means here |
|---|---|---|
| `docs/answered/ui.md` 2026-10-10 (HUBS) | picked ALL: /market hub, /storage hub, /character hub, Accessory Bag v2, + "could we tidy and simplify them any more from here?" | sections 1-4 |
| `docs/answered/ui.md` 2026-10-10 (layout D) | "go with D" - Teleport under the mouse, most used around it, social left, admin right | the hub menu keeps D's shape: World / Teleport in the centre |
| `docs/answered/ui.md` 2026-10-10 (visibility) | "can we control what's visible in the menu with permissions?" | ONE menu. Each tile and each TAB has a rule (perm / unlock / mod loaded) |
| `docs/answered/ui.md` 2026-10-10 (editor) | menu editor, click-to-swap, "doesn't support dragging" | the editor stays. Old tiles become optional shortcuts (1.3) |
| `docs/answered/ui.md` 2026-10-10 (Sky Window) | "I like 2 the best" + (coordinator relay) "beautiful! can we design it all with the new theme" | section 7: every hub page uses the Sky Window kit look |
| `docs/answered/gear.md` 157-159 | "combind the upgrade into the reforge", "one command, one location ... /smithing" | the Smithing hub = `research/Requip-Smithing-Spec.md` section 4 |
| `docs/answered/gear.md` 153-154 | Requip: one pool, loadouts pick from it | Storage hub has a Requip tab |
| `docs/answered/bags.md` 87-88 | Bags v2: storage level x rarity multiplier, upgrade button, one Pocket Dimension | Accessory Bag v2 copies this shape (section 4) |
| `docs/answered/bags.md` 28 | "all accessories and bags cost the last rarity/size to craft the next one" | accessory tier-up keeps this rule (4.4) |
| `docs/answered/bags.md` 52 | boosters go Normal -> Legendary, Fabled / Mythic cannot be upgraded; bag 18 slots to start, up to 60 | v2 never gives fewer slots than today |

## 1. The final shape

### 1.1 The menu after hubs (7 tiles, 2 of them admin only)

```
 col:  0          1   2   3            4            5            6   7   8
row 0  [Social]               .          [Character]       .                  [Settings]
row 1                     [Storage]      [WORLD/Teleport]  [Smithing]
row 2                         .          [Market]          .
row 3                                                                          [Mods]*
row 4                                                                          [Server Setup]*
       Close 49, Edit layout 53                       * admin only (Mods also while menu.modsHelp is on)
```

- The centre stays where the mouse is (slot 13). It opens the World hub on its **Teleport** tab, so one click still teleports.
- The 4 corners of the plus (3, 5, 21, 23) and every other slot are **free**. Players fill them with shortcuts through the editor (1.3).
- The Hover Tooltips tile goes. The same switch already lives in Settings > General.

### 1.2 Hubs, tabs, and which page each tab is

"As-is" means the page content stays the same and only gets the hub tab bar on top, which replaces its own title row (section 2.4).
"Work" means the page changes for another reason, and that reason is named.

| Hub (command) | Tab (order) | Owner mod | Page today | Reuse | Shortcuts that open this tab |
|---|---|---|---|---|---|
| **Character** `/character` (`/char`) | Stats (10) | SkyyMenu | Stats page | as-is | `/stats`, `/profilestats` |
| | Skills (20) | SkyySkills | skills page | as-is (960 wide: the bar fits its width) | `/skills`, `/skill` |
| | Trees (30) | SkyyTrees | tree page | as-is | `/tree`, `/trees` |
| | Class (40) | SkyyClasses | class page (abilities, kit) | as-is | `/class`, `/classes` |
| | Pets (50) | SkyyPets | pets page | as-is | `/pets`, `/pet` |
| | Accessories (60) | SkyyAccessories | Accessory Bag page | **work**: Bag v2 (section 4) | `/accessories`, `/acc`, `/accbag` |
| | Collections (70) | SkyyCollections | collections page | as-is | `/collections`, `/coll`, `/recipes`* |
| | Profiles (80) | SkyyProfiles | profiles page | as-is | `/profiles`, `/profile` |
| **Storage** `/storage` | Pocket (10) | SkyySacks | Pocket Dimension | **work**: Bags v2 page (header added in that round) | `/sacks`, `/pd`, `/bags` |
| | Requip (20) | SkyyWardrobe | Requip page (0.2) | **work**: Requip round | `/requip`, `/wardrobe`, `/wd`, `/loadout` |
| | Vault (30) | SkyyVault | vault page | as-is (old dark style: restyled with the theme, section 7) | `/vault` |
| | Bank (40) | SkyyBank | bank page | as-is; tab hidden until `bank:fn:unlocked` says yes | `/bank` |
| **Market** `/market` | Bazaar (10) | SkyyBazaar | bazaar page | as-is | `/bazaar`, `/bz` |
| | Auctions (20) | SkyyAuctions | AH page | as-is (Manage stays a button inside it) | `/ah`, `/auction`, `/auctionhouse` |
| | Merchants (30) | SkyyMerchants | rumours page | as-is; NPC shops join this tab later | `/merchants`, `/rumours` |
| **Smithing** `/smithing` (`/smith`) | Gear (10) | SkyyGear | set cards (Requip-Smithing spec 4.2) | **work**: SkyyGear 0.2.23 | `/smithing` |
| | Recipes (20) | SkyySacks | `/craft` page (every bench recipe from your bags) | as-is | `/craft` |
| | Reforge (30) | SkyyGear | Reforge page | as-is | `/reforge` |
| | Upgrade (40) | SkyyGear | Reforge page, Upgrade mode | as-is | `/upgrade` |
| | Multitool (50) | SkyyGear | /multitool page; only while it is switched on | as-is | `/multitool` |
| | Identify (60) | SkyyGear | identify page | as-is (+ "Identify all", 3.5) | `/identify` |
| **World** `/travel` | Teleport (10) | SkyyMenu | the menu's Teleport view (island, hub, spawn, warps) | as-is | none (menu centre) |
| | Island (20) | SkyyIslands | `/island menu` page (1240 x 980) | **work**: must drop ~50 px (2.4) | `/island menu` (`/island` alone still teleports) |
| | Explore (30) | SkyyExploration | explore page (discoveries, zones, titles) | as-is | `/explore`, `/discoveries`, `/titles` |
| | Quests (40) | SkyyQuests (later) | job board | later | `/quests` |
| **Social** `/social` | Players (10) | SkyyMenu | the menu's Players view | as-is | none |
| | Party (20) | SkyyParty | party page | as-is | `/party`, `/p` |
| | Guild (30) | SkyyGuilds | guild page | as-is | `/guild` |
| **Settings** `/settings` | Settings (10) | SkyyMenu | Settings page | as-is | `/settings`, `/skysettings` |
| | HUD (20) | SkyyHud | launcher row, then the HUD editor opens (it is a full-screen editor, not a page) | as-is | `/skyyhud`, `/shud` |
| | Menu layout (30) | SkyyMenu | the 0.3.17 editor | as-is | Edit layout tile |
| | Mods (40) | SkyyMenu | Mods list (admin, or everyone while menu.modsHelp is on) | as-is | none |
| | Server Setup (50) | SkyyMenu | Server Setup (admin only) | as-is | `/modconfig`, `/serversetup` |

\* `/recipes` is an alias in BOTH SkyySacks and SkyyCollections today, and the last one registered wins. Collections keeps it; SkyySacks
drops it in its hub round.

Commands that stay chat-only (no tab): `/fishing`, `/cooking` (their numbers already show on the Skills tab's per-skill Stats page),
`/title <name>`, `/balance`, `/pay`, `/tpa...`, `/hub`, `/island`, `/pc`, `/gc`, `/msg`, and every admin command.

### 1.3 Before / after for every tile today (SkyyMenu 0.3.17, layout D)

| Tile today (slot) | Command | After |
|---|---|---|
| Teleport (13) | menu view | World hub, Teleport tab - still the centre tile |
| Your Profile (33) | `/stats` | Character > Stats |
| Pets (3) | `/pets` | Character > Pets |
| Skills (4) | `/skills` | Character > Skills |
| Accessory Bag (5) | `/acc` | Character > Accessories |
| Collections (40) | `/collections` | Character > Collections |
| Island Menu (12) | `/island menu` | World > Island |
| Crafting (14) | `/craft` | Smithing > Recipes |
| Reforge (30) | `/reforge` | Smithing > Reforge |
| Identify (31) | `/identify` | Smithing > Identify |
| Bank (21) | `/bank` | Storage > Bank (unlock rule kept) |
| Vault (29) | `/vault` | Storage > Vault |
| Pocket Dimension (32) | `/sacks` | Storage > Pocket |
| Wardrobe (36) | bridge `wardrobe:fn:open` | Storage > Requip |
| Bazaar (22) | `/bz` | Market > Bazaar |
| Auction House (23) | `/ah` | Market > Auctions |
| Players (0) | menu view | Social > Players |
| Party (9) | `/party` | Social > Party |
| Guild (18) | `/guild` | Social > Guild |
| Hover Tooltips (8) | switch | **removed** (Settings > General has it) |
| Settings (17) | `/settings` | Settings hub tile (slot 8) |
| HUD Editor (26) | `/skyyhud` | Settings > HUD |
| Mods (35) | menu view | stays a tile (admin) + Settings > Mods |
| Server Setup (44) | `/modconfig` | stays a tile (admin) + Settings > Server Setup |
| Edit layout (53) | editor | stays |
| (none) Classes, Trees, Profiles, Explore, Merchants | typed only | now tabs: Character > Class / Trees / Profiles, World > Explore, Market > Merchants |

**Old tiles do not disappear from the code. They become optional shortcut tiles.** The editor's "empty slot" click offers "Add
shortcut", which lists every hub tab. The default layout shows only the hubs. A player who saved a layout with 0.3.17 keeps it, with the
same tiles in the same slots, and the new hub tiles go to the first free slots (the 0.3.17 rule). Nothing that a player arranged breaks.

## 2. How a hub works (technical)

### 2.1 The registry on `skyy.bridge`

Each tab is ONE bridge key, put by the mod that owns the page and removed in its `shutdown()`. There is no shared list, so two mods
never edit the same object, and a mod that is not loaded simply has no tab.

| Key | Value (java.lang / java.util types only) |
|---|---|
| `hub:tab:<hub>:<tabId>` | `Object[]{ String mod, String label, Integer order, String command, java.util.function.Function open, java.util.function.Function visible }` |
| `hub:def:<hub>` (SkyyMenu) | `Object[]{ String title, String command, String iconItemId }` |
| `hub:last:<uuid>` (SkyyMenu, memory only) | `java.util.Map<String hub, String tabId>` - the last tab used per hub, so `/character` reopens it. Never saved |

- `<hub>` is one of `character`, `storage`, `market`, `smithing`, `world`, `social`, `settings`. `<tabId>` is a short lowercase word.
- `open.apply(UUID)` opens that tab's page for the player and answers `Boolean.TRUE`. It runs on the player's world thread (the caller
  is always a page event, which is already there).
- `visible.apply(UUID)` returns `Boolean`, or the slot holds `null` (= always visible). It is used for bank unlock, admin tabs,
  `part.multitool`, and tabs whose mod part is switched off.
- `command` is the fallback when `open` is missing or throws: `CommandManager.get().handleCommand(playerRef, command)`. This is the
  proven "command from a page" trick (SkyyMenu's tiles and the SkyyGear 0.2.22 /multitool page's `tabEvent`). Permission checks apply
  as if the player typed it.
- The tab orders in the 1.2 table are the contract. Later tabs pick numbers between them.

### 2.2 The shared tab bar in `tools/skyyui.py`

The pattern is the SkyyGear 0.2.22 Reforge page's `tabs()` (`SkyyGear/build_skyygear_0.2.22.py`): it decides at runtime which tabs
show, gives each tab an equal width, makes the active one Primary and the others Secondary, puts them 5 px apart, binds Activating, and
sends EventData `a = "mode:<n>"`. The kit's existing `tab_row()` only works at build time, which is not enough here.

New in the kit:

| Kit piece | What it is |
|---|---|
| `hub_bar_markup(parent, w)` | the static group: `< Menu` button (left, 120), title label "Character", tab strip (flex), Close X. Height `HUB_BAR_H = 52` (tabs 44 + 8 gap) |
| `HUB_BAR_JAVA` | one Java source string that every mod pastes into its own package as class `HubBar` (each jar gets its own copy of the same code, because cross-jar classes are not allowed). `HubBar.build(b, ev, parent, hub, myTabId, w, uuid)` reads the `hub:tab:<hub>:*` keys, filters by `visible`, sorts by `order`, and draws the tabs. `HubBar.handle(playerRef, uuid, data)` returns true when the click was a hub click |
| events | `a = "hub:<tabId>"`, `a = "hub:back"`. Each page's `handleDataEvent` calls `HubBar.handle` first (the SkyyGear `insertBefore` pattern) |
| `assert_hub_page(w, h)` | `assert_page_size(w, h + HUB_BAR_H - old_title_h)`, so no page grows past `MAX_PAGE_H` 980 |
| tab width rule | `tw = (w - 5 x (n - 1)) / n`. The minimum is 110 px, which needs the Sky tab texture (HorizontalBorder 20, section 7). The vanilla Primary texture squashes below about 160 px. The builder asserts that the largest hub (Character, 8 tabs) fits the narrowest page in it (Skills, 960: 8 x 115 + 35 = 955) |

A click on a tab works like this:
1. Same mod, same page class: switch in place (like Reforge to Upgrade today). Nothing else opens.
2. Another tab: `open.apply(uuid)`, or else the fallback `command`. The new page replaces the current one, the same as the menu does.
   No page stack is kept.
3. `hub:last:<uuid>` is updated.

**Back:** `< Menu` runs `/skymenu` (the existing Back pattern). Esc / Close closes the page. Sub-pages inside a tab (a skill's stats
page, the Smithing piece page, the AH Manage page) keep their own `< Back`, which returns to their tab. The hub bar stays visible on
them, so the player can always jump to a sibling tab.

### 2.3 Hub commands (SkyyMenu)

SkyyMenu registers `/character` (`/char`), `/storage`, `/market`, `/travel`, `/social` (player commands with `hytale:Adventurer` on the
root and every variant, per HANDOFF section 3). Each one opens `hub:last` or else the lowest-order visible tab, and it says
"Nothing here yet" if no tab is visible. `/smithing` stays SkyyGear's, as the Requip-Smithing spec says. `/settings` already exists.
Each hub tile in the menu does the same as its command.

### 2.4 Page heights

Every tab page drops its own title row, and the hub title takes its place. Net cost: +52 bar - about 38 title = **+14 px**. Most pages
have room. SkyyIslands' 1240 x 980 page is already at the limit, so its round trims its tab row by 14 px or more. Each builder runs
`assert_hub_page`.

### 2.5 One page size (recommended, not forced)

Hub pages today are 960 - 1400 px wide, so the bar would jump when the player switches tabs. Target: **every hub page 1200 x 900**. Each
page moves to that size the next time its mod gets a round. Until then, the bar simply fits the width of whatever page it is on.

## 3. Further simplification (only the good ones)

| # | Idea | Where | Cost |
|---|---|---|---|
| 3.1 | **Find item across storage**: a search box in the Storage bar. Each storage mod answers `storage:fn:find` `apply(Object[]{UUID, String query}) -> Object[]{ String tabId, Long count }[]`. Results show as "Oak Log - Pocket 2,340 - Vault 64", and a click opens that tab filtered | SkyySacks, SkyyWardrobe, SkyyVault | small per mod |
| 3.2 | **Deposit all** in the Storage bar: one click routes materials to the Pocket Dimension (`sacks:fn:deposit`) and gear to Requip (Deposit all gear). It never touches the hotbar and never auto-fills the Vault | Storage bar (SkyyMenu calls both bridges) | small |
| 3.3 | **Coins in the bar** for Market and Storage: "Purse 12,400 - Bank 50,000" (`coins:fn:get`, `bank:<uuid>`) | hub bar option | tiny |
| 3.4 | **Remember the last tab** per hub (`hub:last`) | SkyyMenu | tiny |
| 3.5 | **Identify all** button on the Identify tab: identify every unidentified item you carry, one cost total shown first | SkyyGear | small |
| 3.6 | **Profile switch lives in Character** only: the Stats tab's Change Profile button + the Profiles tab. No separate profile tile | SkyyMenu | none |
| 3.7 | **Fishing / Cooking info on the Skills tab** (the per-skill Stats page), instead of separate pages | already there | none |
| 3.8 | **Shortcut tiles from any tab** through the editor (1.3), so power users rebuild their old menu while new players see 7 tiles | SkyyMenu | small |
| 3.9 | **One /recipes owner** (1.2 footnote) | SkyySacks | tiny |

Not recommended: merging Vault into the Pocket Dimension (the Vault is shared across profiles on purpose), merging Bazaar and AH into one
page (their order books differ), and auto-deposit into the Vault.

## 4. Accessory Bag v2

### 4.1 Today (SkyyAccessories 0.5.11)

- 18 slots (Server Setup `slots`, 1-60).
- About 10 booster lines: Health, Stamina, Mana, Regeneration, Speed, Strength, Magic Power, Defense, Crit, Feather. Plus the Lantern, the
  bench accessories and the Omni.
- **Only the best rarity of each line counts.** So today at most about 22 different items are useful in the bag (about 12 with the Omni).

### 4.2 The v2 shape: room from progress, strength from upgrades (the Bags v2 pattern)

| Part | Bags v2 | Accessory Bag v2 |
|---|---|---|
| grows by itself | storage LEVEL from items collected | **slots** from the Accessory collection + Overall Level |
| upgrade button | RARITY raises a storage multiplier | bag RARITY raises an **accessory power multiplier** |
| result | capacity = level x multiplier | every booster number x multiplier |

**Slots:** `slots = 18 + Accessory collection tier (0-10) + floor(Overall Level / 10)`. The result is capped by Server Setup
`slots.max` (default 33, editable up to 60).
- The **Accessory collection** is new: the number of DIFFERENT accessories (line x rarity) ever placed in this profile's bag. It is
  owned by SkyyAccessories (per profile, under the profile key, `tools/PROFILES-CONTRACT.md`). Tier thresholds:
  I 3, II 6, III 10, IV 15, V 20, VI 26, VII 33, VIII 41, IX 50, X 60 (Server Setup rows).
- The tier shows on the Accessories tab, and as a read-only row on the Collections tab (`acc:album:<uuid>` = "tier,count").
- **Overall Level** comes from SkyySkills (`skill:overall:<uuid>`, `research/Overall-Level-Spec.md`).

**Why the multiplier goes on POWER, not on slots:** because only the best item of a line counts, extra slots past about 22 sit empty
and do nothing. A slot multiplier would hand out room nobody can use. A power multiplier makes every upgrade felt, and it rewards the
same collection grind as Bags v2. Slots still grow, so new lines and Fabled / Mythic finds always have room.

**Upgrade button** (on the Accessories tab):

| Bag rarity | Multiplier* | Needs | Cost* (taken from inventory, then the Pocket Dimension) |
|---|---|---|---|
| Normal | x1.00 | - | - |
| Unique | x1.10 | Accessory collection II | 500 of each of 4 category collections' items + 10,000 coins |
| Rare | x1.20 | IV | 2,000 each + 50,000 |
| Legendary | x1.35 | VI | 8,000 each + 250,000 |
| Mythic | x1.50 | IX + every line at Legendary once | 25,000 each + 1,000,000 |

\* Placeholders. These are Server Setup rows. They go through the Class Balance Workbench refresh before the build.

- The multiplier touches booster NUMBERS only: Health, Stamina, Mana, Regeneration, Speed, Strength, Magic Power, Defense, Crit.
- It never touches on/off effects: bench accessories, the Omni, the Lantern reach, Feather.
- The cost uses the same category list and the same `sacks:fn:take` / `put` / `commit` payment as Bags v2, so the two upgrade pages
  share one look and one transaction model.

### 4.3 Migration from today's bag (one time, per profile, at first load)

1. Contents stay in the same slots.
2. Slots become `max(old configured slots, v2 formula)`, so nobody ever gets fewer. Items in slots above the count stay and keep
   counting (the 0.5 rule).
3. The Accessory collection is back-filled from every accessory in the bag + inventory now.
4. Bag rarity starts at Normal (x1.00), so the numbers do not change on update day.
5. The config row `slots` stays and now means "starting slots". `slots.max` is appended. No value is rewritten (PROJECT-RULES 4).
   There is a run-once marker and one log line.
6. Rollback: v2 -> 0.5.11 is safe. Old builds ignore the new file. The bag simply shows the configured slots and loses the multiplier.

### 4.4 Tier-up: on the Character > Accessories tab

- **Tier up** (main path) keeps Skyy's locked rule (bags.md 28): the next rarity costs the previous one + the Workbench recipe's
  materials. It is the same recipe, run from the bag page and paid from inventory + bags. The Workbench recipes stay.
- **Merge 3 duplicates** (extra path, for drops later): 3 of the same line and rarity make 1 of the next rarity, with no materials.
  Today duplicates are dead weight, because only the best one counts.
- Fabled / Mythic never tier up (bags.md 52). Recipe knowledge gates still apply (for example the Lantern via Tree Sap).

**Why this tab and not Smithing > Upgrade:** Upgrade carries ROLLED gear up a ladder and keeps its lines. Accessories have no rolls,
live in the bag, and you look at them on this tab. Putting tier-up here keeps "accessories in one place".

## 5. Build plan

| Round | Mod(s) | What | Size | Waits for |
|---|---|---|---|---|
| H0 | SkyyUiProbe | Probes. K1: Sky kit textures (path root, 9-slice frame / buttons / tabs / scrollbar, one texture path shipped by two jars). H1: a tab in jar A opens jar B's page through a bridge Function (no flicker, Esc OK) | lean + one Skyy test | - |
| H1 | `tools/skyyui.py` + a hubs contract file in `tools/` | `hub_bar_markup`, `HUB_BAR_JAVA`, `assert_hub_page`, the registry contract (2.1), the theme table (7.2, vanilla textures until the art lands) | lean (kit + self-test page) | H0 |
| H2 | SkyyMenu 0.3.18 | `hub:def:*`, the hub commands (2.3), `hub:last`, its own tabs (Stats, Teleport, Players, Settings, Menu layout, Mods, Server Setup). The menu is unchanged for now | Full (commands, permissions) | H1 |
| H3a | SkyySkills, SkyyTrees, SkyyClasses, SkyyPets, SkyyCollections, SkyyProfiles | Character tabs (bar + key + page title swap) | lean each, 2-3 at a time | H2 |
| H3b | SkyyBazaar, SkyyAuctions, SkyyMerchants | Market tabs | lean each | H2 |
| H3c | SkyyParty, SkyyGuilds, SkyyIslands (-14 px), SkyyExploration, SkyyHud | Social / World / Settings tabs | lean each | H2 |
| H3d | SkyyVault, SkyyBank | Storage tabs + `storage:fn:find` (Vault) | lean each | H2 |
| H4 | SkyySacks (Bags v2 round) | Pocket + Recipes tabs, `storage:fn:find`, drop `/recipes` | inside the Bags v2 round | Bags v2 spec + H2 |
| H5 | SkyyWardrobe 0.2 Requip | Requip tab + `storage:fn:find` | inside the Requip round (R1) | Requip R1 + H2 |
| H6 | SkyyGear 0.2.23 | the Smithing hub moves its 0.2.22 tab row to the shared bar + Identify tab + Identify all | inside the Smithing round (R3) | Requip-Smithing R3 + H2 |
| H7 | SkyyAccessories 0.6 (+ SkyyCollections row) | Accessory Bag v2 (section 4) + the Accessories tab | **Full** (saved data, numbers, migration) | H2. Can run beside H3 |
| H8 | SkyyMenu 0.3.19 | the reduced default menu (1.1), shortcut tiles, Storage bar Deposit all / Find | Full | at least one live tab per hub (H3a-c + one of H4/H5) |
| H9 | every hub mod, riding along | Sky Window kit textures switched on (section 7) | rides each mod's next round; a final sweep for the rest | art approved + K1 |

- **In parallel:** H3a, H3b, H3c, H3d and H7 (about 4-5 heavy at once - the usage-budget rule; lean rounds count light).
- **Wait:** H4 for Bags v2, H5 for Requip, H6 for the Smithing round. H8 last.
- Every round runs the usual cross-check + lint + smoke test. Pin and deploy the hub mods together with H2 in one SET.
- Rollback: each mod's tab key simply disappears. Old commands work throughout.

## 6. Questions for Skyy (recommended default in [brackets])

| # | Question | Default |
|---|---|---|
| 1 | Hub commands: `/character` `/storage` `/market` `/travel` (World) `/social`? (`/world` is likely taken by vanilla) | [yes, as listed; World hub opened by `/travel`] |
| 2 | `/craft` as the Smithing hub's "Recipes" tab, so crafting lives in one place? | [yes; tabs Gear - Recipes - Reforge - Upgrade - Multitool - Identify] |
| 3 | Accessory Bag v2 upgrade multiplies accessory POWER (not slots)? | [power; slots grow by themselves] |
| 4 | Accessory tier-up: craft rule on the bag tab + "merge 3 duplicates"? | [both] |
| 5 | Players' saved custom menu layouts: keep them (old tiles become shortcuts) or reset everyone to the hub menu once? | [keep] |
| 6 | Theme: one page frame for every hub, or each hub its own sky mood in the corner windows (7 frames)? | [one frame first (Clear Day); hub moods in a later art batch] |

## 7. The Sky Window look for every hub page

The look is Skyy's pick "approach 2 SKY WINDOW" (`art/ui-sky-mockups/README.md`, finals in `art/tooltip-sky/README.md`): a thin
ornate gold frame in the emblem gold, a round corner window onto a tiny sky scene, glowing gold star points, and dark readable panels.
Every hub page, the shared tab bar, panels, buttons and frames use it. The kit art is drawn in parallel under `art/ui-kit-sky/`.

### 7.1 Engine limits (verified unless marked)

| Limit | Rule | Source |
|---|---|---|
| Texture root | inline custom pages resolve `TexturePath` **relative to `Common/UI/Custom/`**. Paths are written without `@2x`, and the client loads the `@2x` file | `research/Vanilla-UI-Research.md` facts 8 + 3.4 |
| Density | `@2x` is the top: 2 texture px per UI unit. There is no @3x / @4x. A 1x twin is optional (vanilla ships @2x only) | same + `art/tooltip-sky/README.md` |
| 9-slice | `Background: (TexturePath: ..., Border: N)` or `HorizontalBorder` / `VerticalBorder`. N is in **UI units** (= @2x px / 2). Corners stay fixed. Edges and centre are **stretched, not tiled**, so edge art must look the same along its length, and ornaments go only in the corners | `art/ui-sky-mockups/README.md` |
| Min size | an element smaller than 2 x Border squashes its corners. Vanilla Primary (HorizontalBorder 80) breaks below about 160 px, which is why the Sky tabs use 20 | 3.5 Buttons |
| Ornaments outside the box | not part of a 9-slice: separate fixed-size groups (the vanilla header decoration is a 236 x 11 group at Top -12) | 3.1.1 |
| Text | text colours are fixed (white, grey, green, red, gold, aqua, rarity), so every text area stays DARK (98 % opaque twilight panel, the tooltip-sky contrast check) | tooltip-sky contrast table |
| Scrollbars | the inline `ScrollbarStyle` takes textures (SkyyGear `GearUi.scroll()` already does it) | 3.x scrollbars |
| UNVERIFIED (probe K1) | (a) a path outside the Custom root such as `"../SkyyKit/X.png"`; (b) two jars shipping the same texture path with identical bytes (any warning?); (c) whether ItemGrid slot backgrounds take a texture | probe H0 |

**Path decision:** the art is named `SkyyKit/<Element>@2x.png`. Because of the texture root, the jar location is
**`Common/UI/Custom/SkyyKit/<Element>@2x.png`**, and the markup writes `TexturePath: "SkyyKit/<Element>.png"`. This is the same element
name as the requested `Common/UI/SkyyKit/<Element>@2x.png` with one folder added. If probe K1(a) proves that `../SkyyKit/` works, the art
can stay at `Common/UI/SkyyKit/` and only the kit's path prefix changes. The art agent should keep `<Element>` names exactly as in 7.3.

**Which jar ships them:** every mod jar ships the same bytes at the same path (the mods are standalone). If K1(b) shows a warning, the
fallback is `SkyyKit/<Mod>/<Element>.png`, a kit prefix change only.

### 7.2 How it plugs into `tools/skyyui.py`

- One table `THEME = {"vanilla": {...}, "sky": {...}}` maps each kit element to its texture path + borders.
- `button_style`, `tab_row` + `hub_bar_markup`, the page frame / header helpers, `row_style`, `text_field`, `checkbox_style`, a new
  `scrollbar_style()` and `section` / separator all read from it.
- The build constant `KIT_THEME = "sky"` switches every page built with the kit at once.
- The kit's `require_verified()` / `_need()` checks stay for the vanilla set. The sky set is checked against the art `manifest.json`
  (sizes, borders, sha256) instead.
- The kit also copies the PNGs into each jar (one helper, like the SkyyAccessories Lantern texture copy).
- Content padding goes from 16 to 24 so the corner windows never sit under text. `assert_page_size` sees the change.
- Text colours, fonts and sounds stay vanilla.

### 7.3 Art list for `art/ui-kit-sky/` (all `@2x`, borders in UI units = half the px)

| `<Element>` (+ states) | @2x size (px) | Border (UI) | Notes |
|---|---|---|---|
| `Frame` | 160 x 160 | 32 | page body. Corners = round sky window (Clear Day) + star point. Uniform gold double line + sky ribbon along the edges. Dark centre 98 % |
| `Frame_<Mood>` (later: Sunny, Storm, Night, Sunset, Dawn, Pink) | 160 x 160 | 32 | only if Q6 picks hub moods |
| `Header` | 600 x 76 | HorizontalBorder 60, VerticalBorder 0 | title bar, 38 UI high. Uniform centre |
| `HeaderOrnament` | 472 x 44 | none (fixed 236 x 22) | centre crest with the gold star, sits over the header like vanilla's decoration |
| `Tab`, `Tab_Hovered`, `Tab_Pressed`, `Tab_Selected` | 240 x 88 | HorizontalBorder 20, VerticalBorder 12 | hub bar tabs, 44 high. Selected = gold rim + soft sky glow. Good down to 110 UI wide |
| `Primary`, `Primary_Hovered`, `Primary_Pressed`, `Primary_Disabled` | 440 x 88 | HorizontalBorder 24, VerticalBorder 12 | main action, 44 high |
| `Secondary` (+ same 3 states) | 440 x 88 | 12 | most buttons |
| `Tertiary` (+ `_Hovered`, `_Pressed`, `_Active`) | 256 x 64 | 12 | small 32-high toggles / ON-OFF / pagers |
| `Danger` (+ `_Hovered`, `_Pressed`) | 440 x 88 | 12 | delete / confirm-loss, red-gold |
| `Close` (+ `_Hovered`) | 64 x 64 | none (32 UI) | the X, a gold star point |
| `Panel` | 64 x 64 | 12 | inner wells (lists, info boxes), dark, thin gold line |
| `PanelInset` | 48 x 48 | 8 | sub-boxes inside a panel |
| `Row`, `Row_Hovered`, `Row_Selected` | 64 x 48 | 8 | list rows. Selected = gold left bar + faint sky tint. Replaces the colour rows |
| `InputBox` (+ `_Hovered`, `_Selected`) | 96 x 64 | 16 | text / search fields |
| `CheckBox`, `CheckMark` | 44 x 44, 32 x 32 | 7, none | settings switches |
| `ScrollTrack`, `ScrollHandle` (+ `_Hovered`, `_Dragged`) | 12 x 24 | 3 | 6 UI wide gold-thread bar |
| `Separator` | 64 x 4 | HorizontalBorder 8 | thin gold line (stretches) |
| `SlotEmpty` | 148 x 148 | none (74 UI) | empty item well, if K1(c) allows. Matches the tooltip-sky `Slot_<R>` family |
| `CardFrame` | 160 x 160 | 32 | Smithing set cards / Profiles cards (smaller windows than `Frame`) |

Every texture has original pixels only, uses the tooltip-sky generator style (deterministic, a validator with a contrast check and a
uniform stretch strip check), and comes with a review sheet showing each element at 1:1 in a mock hub page (Character > Skills) with the
hub bar.
