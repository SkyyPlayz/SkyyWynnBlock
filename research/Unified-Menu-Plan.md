# Unified Menu - one menu for everything (DECIDED 2026-10-15: A + D combined)

Skyy 2026-10-15 (docs/answered/ui.md ONE UNIFIED MENU): "unless you have a better way to tie all these together into one menu! so the
menu item in my hand opens to an overview page. and all the pages and menus are all tied together in there, so we have 1 unified menu for
everything. (draft a planned layout before building". Builds on research/Hubs-Spec.md (7 hubs + tab strips, live since Menu 0.3.28 / H3a).
Round menu0329 (layout editor add / remove, hubs replace old tiles, Character opens on Skills) is PAUSED until Skyy picks a layout here.

## 0. Decision (Skyy 2026-10-15, docs/answered/ui.md UNIFIED MENU LAYOUT)

"combined D and A ... lets use a customizable grid in the center for the shortcuts. and build the overview around it, with the bub row up
top. (so i can still place the teleports at the center so i open it, click teleport, then make island the center of that so i can open
it, click twice, and be at my island without moving the mouse." Tabs: "Icon first, themed later".

```
+-- row 1: [Home*] [Character] [Storage] [Market] [Smithing] [World] [Social] [Settings]                (X) +
|-----------------------------------------------------------------------------------------------------------|
| YOU               |            SHORTCUT GRID (7 x 5, customizable)              | RIGHT NOW             |
| name - class      |   [ ] [ ] [Social] [ ] [Character] [ ] [Settings]           | ! 3 AP to spend  >    |
| profile, level    |   [ ] [ ] [Storage] [Teleport*] [Smithing] [ ] [ ]  <- the  | ! 2 unidentified >    |
| coins, bank       |   [ ] [ ] [ ] [Market] [ ] [ ] [ ]      centre slot sits     | Quest ...        >    |
| health, mana      |   ...                                   under the mouse      | Party ...        >    |
|-----------------------------------------------------------------------------------------------------------|
| info line (hover text of the tile under the mouse)              [Edit shortcuts]               [Close]   |
+-----------------------------------------------------------------------------------------------------------+
```

- The grid's CENTRE slot is exactly where the mouse is when the menu opens (as slot 13 is today). Default centre = Teleport.
- The Teleport page's centre slot is customizable the same way (Skyy: My Island there) -> open, click, click = home, no mouse move.
- Edit shortcuts: Remove on a tile, + Add on an empty slot (every hub, every page, every old tile, every teleport), click-swap move,
  Reset, admin Save as server default. Per account. Old saved layouts migrate once: hubs replace the tiles they cover (Smithing for
  Identify + Reforge), the rest stay put (round menu0329's work, now inside U1).
- Character hub opens on Skills; every page keeps its own (hidden by default) shortcut tile.
- Tabs: a small faded icon behind each tab's word now (section 5, first style); themed tabs later, hub by hub.

## 1. The idea: two rows on every page, Home in front

Every SkyWynn page gets the same header. Nothing else on the pages moves.

```
+--------------------------------------------------------------------------------------+
| [Home] [Character] [Storage] [Market] [Smithing] [World] [Social] [Settings]      (X) |  row 1 = hubs (replaces "< MENU" + title)
| [Stats] [Skills] [Trees] [Class] [Pets] [Collections] [Profiles]                     |  row 2 = this hub's tabs (as today)
|--------------------------------------------------------------------------------------|
|                          the page itself (unchanged)                                  |
+--------------------------------------------------------------------------------------+
```

- Any page -> any other page in at most 2 clicks. No more "< Menu" back to a tile grid.
- Row 1 takes the place of today's title row ("< MENU", "CHARACTER", X), so pages do NOT get taller.
- The current hub is highlighted in row 1, the current page in row 2.
- The SkyWynn Menu item in your hand (and the double-tap crouch hotkey) opens **Home**.

## 2. Home (the overview page)

```
+-- row 1: [Home*] [Character] [Storage] ... --------------------------------------- (X) +
| row 2: [Overview*] [All pages]                                                         |
|----------------------------------------------------------------------------------------|
| YOU                          | PINNED (your shortcuts, 2 x 4)    | RIGHT NOW              |
| SkyLordPlayz - Mage          | [My Island] [Hub]   [Skills] [Bags]| ! 3 AP to spend  > Trees |
| profile Gandalf              | [Smithing] [Bazaar] [Pets]  [ + ] | ! 2 unidentified > Ident.|
| Overall Level 4  ||||---     |                                    | Quest: Mine 10 iron  >  |
| Coins 1,240  Bank 5,000      |                                    | Party: 2 online      >  |
| Health 149  Mana 139         |                                    | Shard ready to collect  |
| Skill avg 6.2  Coll. 12%     |                                    |                         |
|----------------------------------------------------------------------------------------|
| [My Island]   [Hub]   [Spawn]                                         [Edit pins] [Close] |
+----------------------------------------------------------------------------------------+
```

- **You:** the numbers players check most (from Stats / Profiles / Bank). Click -> Character > Stats.
- **Pinned:** Skyy's add / remove ask lives here. 8 slots; [+] on an empty one lists every page (all hubs, all tabs, the old
  tiles); Edit pins = remove / move (click a pin, click a slot - no dragging). Defaults: My Island, Hub, Skills, Bags, Smithing, Bazaar,
  Pets. Saved per account; admins can save a server default (like the layout editor today).
- **Right now:** short alerts from the mods (skill points / AP to spend, unidentified items, active quest, party, a shard to collect,
  a rankup ready). Each line opens the page that fixes it. Hidden when there is nothing to say.
- **Teleport row:** the 3 most-used teleports, one click as today.
- **All pages** tab: one grid of every page in the pack, grouped by hub (the old tile menu, kept as a launcher). Nothing is ever lost.

## 3. Options for Skyy

| | Layout | Cost |
|---|---|---|
| **A (recommended)** | Hubs as a top row (section 1) + Home overview (section 2) | Kit skyyui 1.6 hub row; every hub mod picks it up on its next round (pages without it still show "< Menu" -> Home, so nothing breaks mid-way); SkyyMenu Home page |
| B | Hubs as a left side rail (icons + names) + the same Home | Every page loses ~140 px width; the Island page (already at the size limit) needs a redesign |
| C | Keep the tile grid as the home (today's menu, reduced to 7 hubs) + add / remove tiles | Smallest (round menu0329 as launched); no overview, still "< Menu" to switch hubs |

| **D (new recommendation, after Skyy: "i really like this, but it doesn't fit super well. with the rest of the flow now")** | Home = today's icon grid, kept, in the Sky Window frame with the hub row on top (section 4) | Like A, but the grid IS the pinned area - the editor's add / remove / move works on it directly |

## 4. Option D - the icon grid as Home

```
+-- row 1: [Home*] [Character] [Storage] [Market] [Smithing] [World] [Social] [Settings] (X) +
|  INFO BOX: hover = the tile's text (as today). Nothing hovered = YOU + RIGHT NOW:          |
|  SkyLordPlayz - Mage - Gandalf - Overall Level 4 - Coins 1,240     ! 3 AP to spend (Trees)  |
|--------------------------------------------------------------------------------------------|
|  the icon grid (9 x 5): the 7 hubs in the plus shape by default, the rest of the slots     |
|  free for YOUR tiles - any page, any old tile (+ on an empty slot, Remove on a tile)       |
|--------------------------------------------------------------------------------------------|
|  [Edit layout]                                                                   [Close]   |
+--------------------------------------------------------------------------------------------+
```

- The grid stays the heart of the menu (what Skyy likes); it just gets the same hub row as every other page, so Home -> Character ->
  Home feels like one menu. Every page's "< MENU" becomes the Home button in row 1.
- Default grid = the 7 hubs (Hubs-Spec 1.1). Old tiles + one tile per page wait in "+ Add" (round menu0329's editor work, unchanged).
- The info box keeps the hover text and, when nothing is hovered, shows the You / Right now lines from section 2.

## 5. Tab designs (all hubs, Character first)

Each tab keeps its word, with a small faded icon of its own behind the word (Skyy: "the pet tab still says pets, but also shows a
little pet icon behind the word"). Stats = a heart / bar chart, Skills = a star medal, Trees = a branching tree, Class = crossed staff
and sword, Pets = a pet, Collections = an open book, Profiles = a portrait. Our own art (menu-icons family, cloud draws, local review),
shipped once under Common/UI/Custom by SkyyMenu and referenced by the kit's tab strip; the active tab shows the icon brighter. A mod
without the new kit simply shows the plain tab.

Two styles (Skyy then added: "or the tab is stylized to whatever it is"):
- **Icon behind the word** - the same tab shape for all, a small faded icon behind the word.
- **Themed tab** - the whole tab is styled after what it is: Pets a soft grassy tab with paw prints, Skills a gold medal ribbon edge,
  Trees a bark / leaf edge, Class a rune-etched stone, Collections a book-spine leather, Profiles a portrait frame, Stats a parchment.
  Still the same size and the word stays readable; the active tab glows. More art (one 9-slice texture per tab + its active version).

## 6. Build rounds (option A / D)

1. **U1 kit + Home** - skyyui 1.6: `HubBar` draws row 1 from the existing `hub:def:*` keys (title, icon, command, plus a default tab: Character
   -> Skills); "Home" = SkyyMenu. SkyyMenu 0.3.29: Home (Overview + All pages), Pinned (+ / Edit pins), Right-now alerts through a new
   bridge list `home:alert:<mod>` (Function UUID -> String lines + target tab), menu item + hotkey open Home. One-time migration of saved
   tile layouts -> pins (the first 7 covered hubs / tiles become pins; old layout kept as a backup line).
2. **U2 ride-along** - each hub mod's next round switches to kit 1.6 (row 1 appears there). A final sweep for mods with no round coming.
3. **U3 alerts** - mods publish their `home:alert` lines (Skills / Trees AP, Gear unidentified, Quests, Party, Shards, Collections rankup).

## 7. Questions (default in brackets)

1. Layout A, B, C or D? [D]
2. Home keeps a Teleport row, or teleports only through World > Teleport and pins? [keep the row]
3. Pinned slots: 8 or 12? [8] (option A only)
4. Tab style: icon behind the word, or the whole tab themed? [icon behind the word first; themed later per hub if liked]
