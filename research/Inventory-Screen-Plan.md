# Inventory Screen Plan v2 - SkyWynn's own inventory-key screen

*Plan v2 2026-11-14 (v1 2026-11-12), paper only - nothing built. Owner: Skyy (they/them). Where this goes: research/ (INDEX.md "research").
Answers go to `docs/answered/ui.md`. Inputs: `research/Runetaria-Study.md` + `research/Runetaria-Video-Notes.md` (what Runeteria does and how a
Hytale 0.7 server can do it). Ideas and layout only - never Runeteria's art, text or code.*

## 0. Skyy's words (docs/answered/ui.md)
- 11-12: "lets do our own version of that. but before we do, we need a full plan on how to work everything in right."
- 11-12 popups: Tab opens the new screen "Yes, with off switch"; top tabs "Split into more tabs" -> the 12 below; quick panel "Crafting";
  look "Custom look" for "Every SkyWynn menu".
- 11-14: "instead of the backpacks they have in their inventory, lets put our pocket dimensions bags there, so you access them in your
  inventory like a backpack. and see if you can make the crafting talismans add all the normal vanilla crating to the inventory crafting.
  (using their own pages to keep it easy, and keep the toggle for the (can craft.) so its easy to navigate. this should make it a little
  simpler. you use the inventory crafting for 99% of it, and our crating page for the smithing, cooking, smelting, tanning, upgrading
  identifying and so on. (and try to make the menus simple and easy to understand, look good, but also contain as much as makes sense, so
  we can keep the number of menus down."

## 1. Design principles (apply to every page of the new screen)
1. **Few menus, full pages.** One screen, 12 tabs; each page holds everything that belongs together, so no system needs its own window.
2. **Simple to read.** One clear title, at most three columns, big readable text (our bigger flavour text rule), labels in plain words,
   key hints shown where keys work. Nothing important only on hover.
3. **One colour language.** Dark panels + ONE accent colour for selected / primary action; green = ready / complete, red = missing /
   danger; rarity colours on every item frame and tooltip title (standing rules). Theme drawn by us in the art round (P0b).
4. **Teach by doing.** The tutorial / first quests point at the exact tab to open (arrow on the tab) and wait until the player does it.
5. **Same pattern everywhere.** Every crafting station uses ONE station layout; every list uses the same row, filter and Craftable-only
   toggle; every collection uses the same card grid.

## 2. The screen
```
+----------------------------------------------------------------------------------------------------------------+
| Inventory  Skills  Class  Pets  Collections  Storage  Crafting  Market  Quests  World  Social  Settings  | coins bank mail [X] |
+------------------------------+------------------------------------------------+----------------------------------+
| CHARACTER                    | CRAFTING (inventory crafting)                  | SKILLS (compact)                 |
| armour 4 + off-hand          | pages: All | Hand | Workbench | Armor | Weapon | | icon grid: name + level under    |
| utility + tool slots         |        Alchemy | Arcane | Farming | ...         | each, total level, hover = XP    |
| Void Charms (equipped row)   | [Craftable only]  search                       | (click = Skills tab)             |
| summoned pet + mount         | recipe grid (tier-sorted)  |  detail: inputs   |                                  |
| class, level, class XP bar   |                            |  have / need,     |                                  |
| Health Mana Stamina Defense  |                            |  Craft / x10 / All|                                  |
| [Stats by source]            +------------------------------------------------+                                  |
|                              | INVENTORY   bags: [Inventory][Mining][Foraging]|                                  |
|                              |   [Farming][Fishing][Combat][Smithing]         |                                  |
|                              | 9 x 4 real grid (or the chosen bag's items)    |                                  |
|                              | HOTBAR 1-9 (+ utility)                         |                                  |
|                              | Take One - Shift Move - 1-9 - Drop - Sort      |                                  |
+------------------------------+------------------------------------------------+----------------------------------+
```
- **Bag tabs = our Pocket Dimension bags** (Skyy 11-14), not Runeteria's backpacks: the tab row above the grid switches the grid between
  the player's inventory and each Void bag (Mining, Foraging, Farming, Fishing, Combat, Smithing, + Supplies if fitting). Moving items is
  the same drag / shift-click as between inventory and a chest; the bag page shows its space bar and Withdraw / Deposit / Sell / Unpack
  for the selected item (today's Pocket right panel, condensed). Storage > Pocket stays only as the full management page (upgrades,
  auto-compact, stack refill) - or folds into this view if it fits (decide at P2).
- **Inventory crafting covers ~99 % of crafting** (Skyy 11-14): it lists hand / Fieldcraft recipes plus, for every EQUIPPED crafting
  talisman (the bench accessories in Void Charms: Workbench, Armor, Weapon, Alchemy, Arcane, Farming ... benches; Accessories BENCHES table),
  that bench's normal vanilla recipes - each bench on its OWN page (tab) so it stays easy, with the Craftable-only toggle kept.
  Today this already half-exists: SkyySacks' Crafting tab merges "Fieldcraft + equipped non-timed benches" (craftSet) - the new screen
  shows it per bench instead of merged. Tier-sorted, opens Enchanted items, pays from inventory + Void (current rules).
- **Crafting tab = processing and gear work only**: Smithing (Gear), Cooking, Smelting (Furnace), Tanning (Tannery), Upgrade, Identify,
  Reforge, Anvil, Multitool, Collections recipes - each a page in the ONE station layout (section 4).
- **Skills column**: Runeteria's professions column idea with names visible (their weak spot: icons only), total level, click = Skills tab.
- **Right now panel** (Skyy 11-14: "i like this right now tab ... lets keep these in the empty space to the right of the inventory"): the
  Home tab's Right now rows (current quest, unspent tree points ...) sit to the right of the inventory grid, under the Skills column.
- **Teleport row** (Skyy 11-14: "below the hot bar, add buttons for teleports. by default have island and hub there with a way to edit it so
  you can add more"): buttons under the hotbar, default Island + Hub, an Edit button adds / removes / reorders (like Edit shortcuts).

## 3. The 12 tabs and what each holds (nothing lost, as few windows as possible)
| Tab | Pages inside (today's owner mod) |
|---|---|
| Inventory | the screen above (Menu draws it; Sacks bags + crafting, Accessories charms, Pets, Skills data) |
| Skills | every skill with level, XP, how-to-level line, perks + its Tree (Skills, Trees) |
| Class | your build: loadout (Signature + ability slots + utility, key, unlock level), ability list with locked level pills and stat-table tooltips, class tree + capstones, switch class (Classes, Trees) |
| Pets | pets, eggs, hatchery, summon, dragon settings; card grid + 3D preview + Summon (Pets) |
| Collections | collections, bestiary / drops codex (Runeteria's lootbag codex idea: every bag and mob's drops with %), memories-style milestones (Collections, Mobs, Gear loot) |
| Storage | Pocket management, Supplies, Requip (loadouts), Vault, Bank (Sacks, Cooking, Wardrobe, Vault, Bank) |
| Upgrade (replaces Crafting, Skyy 11-14) | ONE page = Smithing + Anvil + Upgrade: icon buttons Combat / Mining / Farming / Foraging / Fishing; the family's tool + its upgrade points / tier up, worn armor pieces each with Upgrade, Upgrade full set, Reforge, Apply Sigil, hover stats (Gear, Trees tools). All crafting = inventory crafting. |
| Market | Bazaar, Auctions, Merchants (Bazaar, Auctions, Merchants) |
| Quests | log left (story chapters, side, dailies, weeklies, achievements; follow filter), details right (steps, rewards, reset timers) (Quests) |
| World | Teleport, Island, Shards (all kinds incl. Combat), Explore - travel as cards with danger + cost (Menu, Islands, Shards, Exploration) |
| Social | players (right-click actions: trade, whisper, party, guild), Party, Guild (Menu, Party, Guilds) |
| Settings | settings, HUD layout, menu layout, mods, Server Setup (Menu, Hud) |
- ALT: opens the Inventory tab too (one screen) [default, still open]. Home's big tiles retire into the tabs (no separate hub page).

## 4. Shared page layouts (one pattern each)
- **Station layout** (every Crafting-tab page): header card (skill icon, skill level, XP bar, next unlock) - left: search, Craftable-only,
  collapsible categories - centre: big result preview, rarity odds before crafting (ties to Gear rarity rolls), possible bonus rolls,
  required materials have / need - right: "Your materials" (only items this recipe uses) - bottom: amount (1 / x10 / All), time + XP per
  craft, green "Ready" or red "Missing ..." bar, one accent Craft button; timed jobs show a queue with Collect (today's Furnace queue).
- **Craft result popup** (gear crafts): item in its rarity frame, rarity word in its colour, rarity track, rolled stats.
- **List page** (Quests, Market lists, Players): list left with filters, details right, one primary button.
- **Card grid** (Pets, Collections, World travel): cards with icon / picture, name, one line, progress or level; selected card's details.
- **Tooltip**: the approved sectioned tooltip with rarity colours (standing rule); ability tooltips as a small table.

## 5. How it is built (study section 3)
- SkyyMenu owns the screen and the tab row; each mod gives its panel / page through hub bridges (tools/HUBS-CONTRACT.md) - no mod draws
  another mod's data.
- Tab key: SkyyMenu catches ClientOpenWindow(PocketCrafting) with a PacketAdapters inbound filter and opens our page; Server Setup switch
  `menu.inventory.replace` (OFF = vanilla Tab back).
- Real slots: ItemGrids bound to inventory sections (-1 hotbar, -2 storage, -5 utility, armour) so the client moves items itself - TO PROVE
  in P0 (our 0.6 probes drew nothing). Bag tabs: the bag grid is server-drawn (ItemGridSlot without metadata, names + descriptions; never
  item metadata - disconnect rule) with clicks / drags handled by Sacks, unless P0 finds a container-window way.
- Fallbacks if real slots fail: B = server-drawn slots for the inventory too (all moves by our code); C = keep vanilla Tab and open the new
  screen on ALT without the inventory grid.

## 6. Phases
- **P0 Check + probe (gate).** Mod check of CurseForge "CORE - Custom Inventory" (SupremoSama, All Rights Reserved: learn-only unless its
  licence allows packing). SkyyUiProbe 0.10 (op-only, one Skyy session): Tab caught, page opens, real grids move items (drag, shift, 1-9,
  drop, sort), a server-drawn bag grid with drag in / out, Esc / Tab close cleanly, no vanilla flash, no client WARN.
- **P0b Theme art.** Our SkyWynn theme (panel frame, tab bar, buttons, item cells with rarity frames, fonts available to custom UI,
  accent colour) drawn and approved (skill skywynn-art); the kit (tools/skyyui.py) gets the theme.
- **P1 Shell.** Tab opens the Inventory tab: tab row, real grid + hotbar, character column (read-only), key hints, off switch.
- **P2 Bags.** Void bag tabs on the grid; condensed Withdraw / Deposit / Sell / Unpack.
- **P3 Inventory crafting.** Hand + one page per equipped crafting talisman's bench, Craftable-only, Craft / x10 / All (Sacks + Accessories).
- **P4 Character column live** + Skills column.
- **P5 Crafting tab** pages in the station layout + craft result popup (Gear, Sacks, Cooking).
- **P6 Other tabs** moved to the theme one by one (Class, Pets, Collections + drops codex, Quests, World, Market, Social, Settings).
- **P7 HUD** (locked ability slots with level + key, class XP bar, objective + distance under the compass, portrait frame).
- **P8 First-join class picker** (Runeteria's "Create your character" idea: preview, crests, what you'll do, first ability).

## 7. Risks
- Disconnect from item metadata in a server-drawn slot (our rolled gear): strip metadata, show stats in the name / description.
- Tab / Esc fights, a flash of the vanilla screen, stuck tooltips, crash on hover updates (known kit rules).
- A game update can change window types / section ids / ItemGrid properties: re-run the probe after every Hytale update.
- Page size: ~1,600 elements opened fine in the 0.7 radial probe; the Inventory tab must stay under that with all panels.
- Removing vanilla Pocket Crafting: inventory crafting must cover every recipe it had before the switch goes on.

## 8. Decisions log
- 2026-11-12: Tab replaced with off switch; 12 tabs; quick panel Crafting; custom look for every SkyWynn menu (PROJECT-RULES 4 updated).
- 2026-11-14: bag tabs = Pocket Dimension bags; crafting talismans add their bench's vanilla recipes to inventory crafting, one page per
  bench, Craftable-only kept; inventory crafting = ~99 %; Crafting tab = processing (smithing, cooking, smelting, tanning, upgrade,
  identify ...); simple, good-looking, full pages, fewest menus.
- 2026-11-14: Right now panel right of the inventory; teleport row under the hotbar (Island + Hub, editable); P0 probe PASS (TEST 282); P0b art started.
- 2026-11-14 (v3 review): Character header = Requip presets (Combat, Mining, Farming, Foraging, Fishing); Crafting tab removed -> Upgrade tab; charms / pets keep their own crafting pages; Fishing table -> Smithing; teleport row = icon mini hotbar; art v3 in research/ui-theme-art/.
- Open (defaults): ALT opens the Inventory tab [yes]; Home tiles retire into the tabs [yes]; Supplies as a bag tab [if it fits].
