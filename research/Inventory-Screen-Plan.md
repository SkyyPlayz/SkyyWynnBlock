# Inventory Screen Plan - SkyWynn's own inventory-key screen

*Plan 2026-11-12, paper only (nothing built). Owner: Skyy (they/them). Where this goes: research/ (INDEX.md "research"). Answers go to
`docs/answered/ui.md`. Input: `research/Runetaria-Study.md` (what Runeteria does + how a Hytale server can do it).*

Skyy 2026-11-12: "lets do our own version of that. but before we do, we need a full plan on how to work everything in right. lets start by
studying there server more." -> then "Plan first" (before the CORE mod check and the probe).

## 1. Goal in one line
Pressing the inventory key opens ONE SkyWynn screen: your character, your real inventory and hotbar, quick crafting and your progress on the
first page, and every SkyWynn system one tab away - so the separate SkyWynn Menu (ALT) and the vanilla inventory become the same place.

## 2. What we have today (2026-11-12)
- Vanilla inventory (Tab): drawn by the client, cannot be edited; vanilla Pocket Crafting inside it.
- SkyWynn Menu (ALT, SkyyMenu): Home + 7 hub sections, each with tabs (owner mod in brackets):
  - Character: Skills (Skills), Trees (Trees), Pets (Pets), Void Charms (Accessories), Collections (Collections), Profiles (Profiles); Stats + Class merged in.
  - Storage: Pocket (Sacks), Supplies (Cooking), Requip (Wardrobe), Vault (Vault), Bank (Bank).
  - Market: Bazaar (Bazaar, Auctions merged), Merchants (Merchants).
  - Crafting: Gear (Gear), Recipes (Sacks - Crafting / Gear / Farming / Campfire / Furnace / Tannery / Collections), Reforge, Upgrade, Multitool (Gear).
  - World: Teleport (Menu), Island (Islands), Explore (Exploration), Quests (Quests).
  - Social: Players (Menu), Party (Party), Guild (Guilds).
  - Settings: Settings, Menu layout, Mods, Server Setup (Menu), HUD (Hud).
- Not in the hub yet: Shards (own pages from the shard portal), Combat Shard, Pets Hatchery tabs inside Pets, Fishing Bench, Anvil.
- HUD (SkyyHud): minimap, skills widget, quest tracker, stats; ability keys (SkyyClasses).
- Rules that bind this plan: one menu pattern (research/Menu-Pattern.md), vanilla look via the kit (tools/skyyui.py, Style Guide), merged menus
  (fewer tabs, no duplicates), sort by tier, rarity colours + sectioned tooltips, one page answer per click, never an ItemGridSlot with item
  metadata (HANDOFF 2: disconnect), no page update from hover, InfoDisplay None on grids.

## 3. The screen (layout draft, 1080 fit, vanilla-look kit - NOT Runeteria's gold style)
```
+------------------------------------------------------------------------------------------------------+
| [Home][Character][Storage][Market][Crafting][World][Social][Settings]   coins  bank  mail  [?] [X]    |  <- the hub row we already have
+-----------------------------+--------------------------------------------+---------------------------+
| CHARACTER                   | INVENTORY                                  | QUICK PANEL (switchable)  |
| head/chest/hands/legs       | bag tabs: Inventory | Mining | Foraging... |  Crafting | Skills | Pets  |
| off-hand, utility, tools    | 9 x 4 real grid (drag, shift, 1-9, drop)   |  - Crafting: tier-sorted   |
| Void Charms (equipped)      |                                            |    recipe list, Craft /    |
| pet slots + mount           | HOTBAR 1-9 (+ utility)                      |    x10 / All (Sacks rules) |
| class + level + XP bar      |                                            |  - Skills: icon grid with  |
| Health Mana Stamina Defense | key hints: Take One - Shift Move - 1-9 -   |    levels, total, next lvl |
| [Stats by source]           |            Drop One - Drop Stack - Sort     |  - Pets: summon slots      |
+-----------------------------+--------------------------------------------+---------------------------+
```
- First page = the new "Inventory" page of the Home section (Home keeps its big tiles one click away as "Menu").
- Bag tabs: the Void bags (Pocket) shown in the same grid area, so moving between inventory and bags is one screen (today: Storage > Pocket).
- Character column reads existing data: armour (vanilla slots), Void Charms (Accessories), pets (Pets), class + level (Classes / Skills),
  stats with the Four power sources breakdown (Menu Stats by source).
- Quick panel: Crafting (the Sacks Recipes list, compact) replaces vanilla Pocket Crafting; Skills = Runeteria-style icon grid; Pets = summon.

## 4. Every system's place (nothing lost)
| Today | In the new screen |
|---|---|
| Vanilla inventory + Pocket Crafting | Inventory page: real grid + hotbar + quick Crafting panel |
| SkyWynn Menu Home tiles | Home tab (unchanged), opened by ALT or the Home tab |
| Character > Skills / Trees / Pets / Void Charms / Collections / Profiles | Character tab, same sub-tabs; Skills also as the quick panel grid |
| Storage > Pocket | Bag tabs on the Inventory page + Storage tab for the full page |
| Storage > Supplies / Requip / Vault / Bank | Storage tab (unchanged) |
| Market, Crafting, World, Social, Settings | same tabs (unchanged pages) |
| Shards, Combat Shard | World tab gets a Shards sub-tab (opens the shard you own; portal still works) |
| HUD ideas from Runeteria (locked ability slots with level + key, class XP bar, objective under the compass) | separate HUD round, after this |
| Class pick at first join (Runeteria's "Create your character") | separate round: SkyyClasses / SkyyProfiles first-join picker |

## 5. How it is built (from the study, section 3)
- SkyyMenu owns the screen (it already owns the hub row and the page contract `tools/HUBS-CONTRACT.md`); other mods give panels through the
  existing hub tab bridges - no mod draws another mod's data.
- Tab key: SkyyMenu catches the client's ClientOpenWindow(PocketCrafting) with a PacketAdapters inbound filter and opens our page instead.
  Server Setup switch `menu.inventory.replace` (default ON once proven; OFF = vanilla Tab back).
- Real slots: page ItemGrids bound to the inventory sections (-1 hotbar, -2 storage, -5 utility, armour section) so the client moves items
  itself (MoveItemStack etc.). If 0.7 still draws nothing there (as in our 10-02 probes on 0.6), fallback B below.
- Fallback B (if real slots fail): our page with server-drawn slots (ItemGridSlot without metadata + names / descriptions), every move done by
  our code - more work and slower to feel; or fallback C: keep vanilla Tab, and make ALT open the new layout without the grid.
- Vanilla Pocket Crafting goes away when the screen replaces Tab, so the quick Crafting panel must cover its recipes (Sacks already lists
  inventory / Fieldcraft recipes).

## 6. Phases (each its own round; a probe gates the rest)
- **P0 Check + probe (gate).** Mod check of CurseForge "CORE - Custom Inventory" (SupremoSama, All Rights Reserved): pack it, learn from
  it, or skip. Then SkyyUiProbe 0.10 (op-only, one Skyy session): Tab is caught, our page opens, real grids move items (drag, shift, 1-9,
  drop, sort), Esc / Tab close it cleanly, no vanilla flash, no client WARN. Result decides real slots vs fallback B / C.
- **P1 Shell.** Tab opens the Inventory page with the hub row, the real grid + hotbar, the character column (read-only) and key hints;
  the setting to turn it off; ALT still opens Home.
- **P2 Bags.** Void bag tabs in the grid area (Sacks), deposit / withdraw by drag or shift.
- **P3 Quick panel.** Crafting (replaces Pocket Crafting), Skills grid, Pets.
- **P4 Character column live.** Equip armour / Void Charms / pets from the column; stats by source.
- **P5 Clean-up.** Remove duplicates the screen makes (e.g. a second Pocket entry), Shards sub-tab in World, tooltips per the rarity rule.
- Later, separate: HUD ideas (P6), first-join class picker (P7).

## 7. Risks
- Client disconnect: any ItemGridSlot carrying gear metadata (our rolled gear) - real-section grids may avoid it; server slots must strip it.
- Tab / Esc fights, a flash of the vanilla screen, stuck tooltips, crash on hover updates (known kit rules).
- A game update can change the window types, section ids or ItemGrid properties: re-run the probe after every Hytale update.
- Page size: the 0.7 radial probe showed ~1,600 elements open fine (docs/log/2026-10.md:1025-1031), so one big page is OK.
- Pack mods that add inventory UI (none packed today) would clash; check at P0.

## 8. Questions for Skyy (defaults in brackets)
1. Tab opens the new screen and fully replaces the vanilla inventory? [yes, with a Server Setup switch to turn it off]
2. Keep our 8 hub sections as the top tabs (not Runeteria's 12)? [yes - merged menus rule]
3. Quick panel on the first page: Crafting, Skills grid, Pets - which by default? [Crafting]
4. ALT keeps opening Home, or also the Inventory page? [Home]
5. Vanilla look (our kit) or a custom look like Runeteria's gold? [vanilla look - standing rule; art pass later if you want]
6. HUD ideas and the class picker: after this, in that order? [yes]
