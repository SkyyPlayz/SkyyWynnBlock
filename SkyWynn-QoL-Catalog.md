# SKYWYNN QoL CATALOG — from Skyy's Lunar SkyBlock profile
*Cataloged 2026-09-22 from `hypixel-skyblock-for-lunar-client` (mods + configs).*

## The one big insight first
Every mod below is a CLIENT mod that exists because Hypixel's server can't change the player's UI.
**Hytale gives us server-driven custom UI — so on SkyWynn, all of this becomes BUILT-IN.**
No player installs anything; the QoL that takes Hypixel players 5 mods to get is just... how SkyWynn works.
(And like Hypixel's `HypixelModAPI` mod in this folder: we should still expose a clean data API so community client mods can exist.)

**UI lock (2026-09-23 batch 2):** build the best placeholders we can and keep refining them. Do not add buttons or custom UI on the **inventory screen** — Hytale will change that screen, so it waits. HUD, sack pages, accessory pages, and other windows are in scope. F5/F6/F7 stay as already locked in `SkyWynn-Decisions.md`. Magic Bags and the accessory bag are core QoL, not a later pass.

---

## What's installed (the QoL stack)
| Mod | What it is |
|---|---|
| **SkyHanni 9.0** | The QoL kitchen sink — hundreds of toggles across every SkyBlock system |
| **Firmament 44.3** | NEU's modern successor: inventory buttons, slot locking, storage overlay, price tooltips |
| **Skyblocker 6.10** | All-in-one: equipment slots in inventory, radial menu, search, AH/bazaar reskins, solvers |
| **Catharsis 1.0β** | New-generation SkyBlock GUI reskin (custom menu/entity/area textures, color profiles) |
| **aaron-mod 3.0** | Misc QoL/visual extras |
| **InventorySorter** | One-key sorting of any container |
| **REI + Searchables** | Recipe viewer: item panel beside inventory, search, recipe/usage lookup |
| **Controlling** | Searchable keybind screen |
| **HypixelModAPI** | Official Hypixel→mod data channel (the "expose an API" lesson) |
| Sodium/Lithium/Iris/FerriteCore/MoreCulling | performance/shaders (not gameplay) |

---

## The features, grouped the way we'd build them
*(✔ = confirmed present in Skyy's configs)*

### A. INVENTORY CORE (the "changes how inventory works" part)
- ✔ **Extra slots visible in inventory** (Skyblocker `skyblockInventoryScreen`): equipment/accessory slots shown right in the inventory screen → SkyWynn: native **gear + accessory + pet slots** on our own pages. **Not on the inventory screen** until that screen can change (Decisions 10.1 / 10.22)
- ✔ **Slot locking** (Firmament): lock a slot so it can't be dropped/sold/misclicked; **item protection** (Skyblocker) marks whole items un-sellable/un-droppable
- ✔ **One-key container sorting** (InventorySorter)
- ✔ **Inventory search** (Skyblocker): type to highlight matching items across open UI
- ✔ **Page scrolling** (SkyHanni): scroll-wheel to flip pages in paged menus
- ✔ **Save cursor position** (Firmament): cursor stays put across menu page changes
- ✔ **Hide not-clickable** (SkyHanni): gray out items that aren't valid for the current UI
- ✔ **Shift-click helpers** (SkyHanni): shift-click to equip/sell/brew without dragging
- ✔ **Middle-click fix / quick-move conventions**
- ✔ **Focus mode** (SkyHanni): declutter items' names to essentials

### B. QUICK ACCESS (the "buttons for quick accessing things" part)
- ✔ **Inventory buttons** (Firmament, hover-text ON, shown on ALL screens): a configurable strip of buttons around every inventory/menu — one click to open storage, wardrobe, crafting, AH, bazaar, etc. → SkyWynn: native **edge-button rail on our pages and other windows, player-configurable**. The inventory screen itself still waits (10.22)
- ✔ **Radial menu** (Skyblocker): hold-key wheel for quick actions
- ✔ **Item hotkeys** (Firmament): press a key to use/open a specific item from anywhere
- ✔ **Wardrobe keybinds** (Firmament) + **custom wardrobe UI** + **loadouts** (SkyHanni) → SkyWynn **locked 2026-09-24**: wardrobe + loadouts, SkyBlock style (save a set, quick-swap). Placeholders on our pages. Nothing on the inventory screen (10.22). **Open:** armor only vs weapons, accessories, and HUD (`SkyyGear-Plan.md`)
- ✔ **GFS — "get from sack"** (SkyHanni): pull materials from bulk storage via command/hotkey without opening anything
- ✔ **Quick commands / command shortcuts** (Firmament + Skyblocker)
- ✔ **Storage overlay** (Firmament + SkyHanni + Skyblocker): ALL storage pages (ender chest + backpacks) on one screen, searchable, click-through

### C. INFO ON ITEMS (tooltips++)
- ✔ **Live price in tooltips** (Firmament price-data; Skyblocker itemTooltip): bazaar/AH value on hover
- ✔ **Estimated item value** (SkyHanni): full appraisal of an item (reforge/enchants/stars) in one overlay
- ✔ **Chest value** (SkyHanni + Skyblocker): total worth of any opened container
- ✔ **Slot text** (Skyblocker): tiny numbers on slots — pet level, item tier, attribute levels
- ✔ **Item number as stack size** (SkyHanni): show the ONE number you care about as the stack count
- ✔ **Missing enchantments** (Firmament), **enchant parsing/coloring** (SkyHanni), **ultimate enchant star**
- ✔ **Lore timers** (Firmament): live countdowns inside tooltips (cooldowns, forge timers)
- ✔ **Wiki lookup** (Skyblocker): key on hover → open the item's wiki page

### D. ECONOMY UI (AH/bazaar — direct spec for OUR native AH/bazaar)
- ✔ **Fancy Auction House** (Skyblocker): grid reskin of AH browsing
- ✔ **Bazaar quick quantities** (Skyblocker) + **input calculator** (type `5*64+32` in amount fields)
- ✔ **Search overlay** with suggestions/history for AH + bazaar (Skyblocker)
- ✔ **Bazaar/AH helpers** (SkyHanni): order price undercutting info, best-flip displays
- ✔ **Sack display + sack value** (SkyHanni): contents/worth of bulk storage at a glance
- → SkyWynn: our AH/Bazaar UIs ship LIKE THE MODDED VERSION, not like Hypixel's chest menus

### E. CRAFTING UI
- ✔ **Super crafting / craftable item list** (SkyHanni): list of everything you CAN craft right now from inv+sacks, click to craft — this + our vault→bench link = Quickcraft v2 spec
- ✔ **Quick-craft confirmation** (SkyHanni): guard against fat-finger crafts
- ✔ **Recipe viewer** (REI/Firmament item list): browsable item DB with recipes + usages, searchable
- ✔ **Anvil combine helper** (SkyHanni)

### F. HUD & WORLD OVERLAYS
- ✔ **Custom scoreboard** (SkyHanni): fully re-drawn, player-configured sidebar
- ✔ **Compact tab list**, custom **hotbar/XP/action bar**, held-item tooltip
- ✔ **Trackers** (SkyHanni `tracker`): profit/drop trackers for every activity
- ✔ **Item pickup log**: floating +/− feed of what entered/left inventory
- ✔ **Waypoints** (fairy souls, navigation, teleport pads, patcher coords), **etherwarp/teleport overlay** (target preview)
- ✔ **Attribute/stat overlays**, **RNG meter**, **magical power display**, skill progress bars
- ✔ **Reminders** (SkyHanni), calendar/mayor overlays, **Discord RPC**
- ✔ **Compact damage numbers**, custom **health bars**, marked players
- ✔ **Dungeon map + puzzle solvers + leap overlay** (Skyblocker) — for OUR dungeons: build the map/solver-friendly data in, don't make modders reverse-engineer it

### G. MENU/VISUAL RESKINS
- ✔ **Improved SB menus** (SkyHanni) + **Catharsis full GUI reskin** with per-menu textures + color profiles → SkyWynn: our menus are custom anyway — steal the AESTHETIC lessons (dark panels, clear grids, big readable numbers)
- ✔ Custom item names/models/dyes/trims/glint (Skyblocker cosmetics suite)
- ✔ Rarity cosmetics (Firmament): background tint by rarity on every slot → native: rarity-colored slot frames everywhere

---

## Distilled: the SkyWynn "QoL bill of rights" (build-in from day one)
1. Equipment/accessory/pet **slots on our own pages** (the inventory screen waits — 10.1 / 10.22)
2. **Button rail** on our pages and other windows (storage, wardrobe, crafting, AH, bazaar, island) — configurable. Not on the inventory screen (10.22)
3. **Slot locking + item protection** as a first-class server feature (protects from OUR sell/drop UIs too)
4. **Search everywhere**: inventory highlight-search, storage overlay search, AH/bazaar search with history
5. **Sort button / sort key** on every container
6. **All bulk storage on one screen** (vault pages unified, searchable)
7. **Prices + appraisals in tooltips** (we own the bazaar — live data is free)
8. **Craftable-now list** + craft-from-storage + confirmations = Quickcraft v2
9. **Rarity-tinted slots, slot-text numbers, live cooldown timers in tooltips**
10. **Loadouts + wardrobe hotswap** — locked 2026-09-24 as placeholders on our pages, not on the inventory screen. What a loadout saves is still open
11. **Per-activity profit/drop trackers** + item pickup log as native HUD widgets
12. **Player-movable HUD**: scoreboard, bars, trackers all draggable/scalable (our /packsettings window pattern, generalized)
13. **Data API for client modders** (the HypixelModAPI lesson)
14. NOTE: all UI built behind the abstraction layer (NoesisGUI rework incoming — see Part 4 of master plan)

---

## SKYY'S HOTKEY + UNLOCK SPEC (locked, 2026-09-22)
*The Booster Cookie inversion: what Hypixel sells as a 4-day paid boost, SkyWynn makes permanent progression.*

**Hover hotkeys (work on any item, in any inventory/menu):**
| Key | Action | Notes |
|---|---|---|
| **F6** | Search this item in the market | Smart-routed: opens Bazaar if it's a commodity, Auction House if it's a unique — like the cookie's AH search, but DEFAULT for everyone, no boost required |
| **F5** | "How do I make this?" | Opens the recipe view for the hovered item |
| **F7** | "What can I make WITH this?" | Opens the usages view (everything the item is an ingredient for) |

*(F5/F7 = the REI/NEU recipe+usages pattern, promoted to first-class keys. Exact key choices adjustable — F5 is often screenshot/perspective in games; final binds decided in playtest, all rebindable.)*

**Quick-access facilities (the rest of the cookie perks):**
- A menu slot at the **end of the hotbar** (SkyBlock-Menu style) opens quick access to: **Enchanting • Anvil • Auction House • Bank • Bazaar** — use them from anywhere, no NPC run.
- Each facility's remote access is **permanently unlocked via quests** — not paid, not temporary. One unlock quest per facility (natural fit: the early quest chain that teaches each facility ends by granting its remote access).
- Every unlocked facility also appears in the window button-rail (B-family above) and radial menu, so hotbar menu / rail / wheel are three routes to the same unlocks.

**Design principle this sets:** convenience is CONTENT on SkyWynn — earned once, kept forever. Paid/cosmetic monetization (if any, later) never gates QoL.

---

## FEASIBILITY NOTES (verified against the engine, 2026-09-22)
**Server-driven UI is first-class.** `CustomUIPage`/`InteractiveCustomUIPage` + `CustomUIHud` (our Void Vault and /packsettings already run on it). Event bindings include **`KeyDown`** and per-slot hover (`SlotMouseEntered/Exited`) — so:
- **Hover-search hotkeys: fully server-side.** In OUR windows, the server knows the hovered slot and can listen for chosen keys. Keys are per-player rebindable in our settings (stored server-side). No client mod needed. NOT possible: global hotkeys in the open world or inside the vanilla E-screen.
- **Vanilla inventory screen (E)**: client-built today; cannot be edited server-side. Plan: our own richer inventory page; re-evaluate replacing the E-screen after the NoesisGUI server-UI rework ships (1–2 mo).
- **UI BUILD FREEZE (Skyy):** don't build UI layouts until the NoesisGUI rework lands. Locked layout preference for then: **all facility buttons live IN the inventory screen** (enchanting/anvil/AH/bank/bazaar/storage/wardrobe...), each opening its menu; hotbar-end menu is the fallback only if the E-screen can't be replaced. **Until then (10.22, and the 2026-09-24 wardrobe lock):** placeholders on our pages. Wardrobe and loadouts are locked now, and they stay off the inventory screen.
- **HUD (Skyy, locked):** sidebar/HUD widgets (location, balance, quest info, skill bars, trackers) are server-composed per player → ship a Lunar-style **HUD edit mode**: every widget individually movable/scalable/toggleable; a few preset bundles offered, with "split bundle into individual widgets" always available. `CustomUIHud` z-order + per-player state makes this pure data.
- **Vanilla HUD elements** (health, hotbar, crosshair) are NOT server-movable. A standalone client-side "Hytale HUD editor" mod (works on ANY server, Lunar-style) is feasible later via the official Mod Browser — good advertising for SkyWynn, but off the critical path until client-mod APIs stabilize.
- **Skyy sign-offs (2026-09-22):** hover-search keys only need to work in inventory/menus (which is exactly what the engine allows) ✔ · custom HUD instead of vanilla-HUD editing is fine ✔ · **HUD layout sharing (export/import codes) is locked in** ✔

---

## HUD WIDGET WISHLIST (from Minecraft HUD-mod ecosystem, researched 2026-09-22)
*Sources: Lunar/Badlion/Feather client modules + Better HUD (40 widgets), HudBase, Better Huds (has profile sharing — precedent for our layout codes), CustomHud (variable/template system), Inventory HUD+, Simple HUD Enhanced, AppleSkin, Jade/WAILA, MiniHUD, Xaero's, ToroHealth.*

**SkyWynn-native widgets (our data, server-side):**
- Location/zone name + coordinates + direction/compass
- Purse/bank balance • bits-style secondary currency (if any)
- Current quest objective tracker • chapter/season progress
- Skill XP bar(s): active skill popup + pinned skill(s) with % and actions-to-next-level
- Class/mana bar • ability cooldown row (E/R + signature) • active effects w/ timers
- Collection progress popup (gather an item → "+3 Oak: 1,204/2,000 to Recipe X")
- Profit/drop session trackers (per activity: farming, slayer, dungeon...) • item pickup log
- Minion status ("2 full, 1 out of fuel") • island visitors alert
- Bazaar order alerts (filled/outbid) • AH sold/ended alerts • bank interest notice
- Party list w/ HP • guild/territory ticker (late-game)
- Slayer boss HP + phase • dungeon: keys/secrets/score • event timers (mayor, festivals, world events)
- Pet display (name, level, XP share) • accessory MP total
- Speed/stat readout (SkyBlock stat sheet style)

**Generic widgets (every HUD mod has these; cheap to add):**
- Clock (game + real time), day counter, FPS, ping, session playtime
- Armor/tool durability (if durability enabled — see 5.12), arrow/ammo count
- Held-item info card, item counter (chosen block/mat in inventory)
- Target health plate (ToroHealth-style) + damage numbers config (compact/off)
- Keystrokes/CPS (PvP crowd), combo counter
- "What am I looking at" plate (Jade-style: block/entity name + mod-source) — pairs with our collections ("looking at Oak Log — Collection VII")
- Chat position/size presets, boss-bar repositioning (ours), title/subtitle position

**Editor features locked:** per-widget move/scale/toggle • preset bundles that split apart • export/import layout codes • (idea) server-hosted "popular layouts" gallery voted by players

---

## THE WYNNTILS STACK (from Skyy's Wynncraft Lunar profile, 2026-09-22)
*"I never play Wynncraft without this." Mods: **Wynntils** (the everything-mod), **Voices of Wynn** (community NPC voice acting), WynnVentory (market prices), Wynncraft Spell Caster, WynnVista, wynnlodgrabber + perf mods.*

**What Skyy singled out (in his priority order):**
1. **The map** — Wynntils' full map + minimap: waypoints, POIs, territories, and **party members visible live on the map** (his favorite integration). → SkyWynn: our map (BetterMap heritage) must ship with party-position integration from day one, not bolted on.
2. **Quest tracking** — auto-tracked objective w/ beacon beam at the destination + compass point.
3. **NPC voiceovers** — Voices of Wynn adds full voice acting to quest dialogue. → SkyWynn aspiration for the content phase: voice our quest NPCs (AI voice gen makes this cheap now — VoW needed a volunteer army).
4. Also in the stack, already covered by our catalog: custom HP/mana bars & overlays (HUD sections above), item price tooltips (WynnVentory ≈ our native bazaar tooltips), spell-cast helper (moot — our casting is ability-keys).

### LOCKED DESIGN — Quest navigation (Skyy, 2026-09-22)
- **Default: a marker on your compass/minimap** pointing at the tracked objective. Quiet, always there.
- **On demand (BL4-style "V"):** temporarily light up the world — a **beacon beam at the objective + a followable trail** (line of light on the ground, or particles in the air) from you toward it. Temporary flash, and **toggleable on/off entirely** in settings.
- Engine note: in-world global keys aren't server-receivable yet, so the "V press" ships as a **usable Quest Compass item / hotbar utility** (click = flash the beacon+trail) until engine or companion-mod keybinds exist. Same behavior, RPG-flavored trigger.
- Trail tech: server-side particles are proven (our ported mods use ParticleUtil); beacon = tall beam VFX or particle column; compass/map markers = proven (BetterMap/PingPoint patterns).

### LOCKED DESIGN — Party HUD widget (Skyy, 2026-09-22)
Shows each party member: **name, HP, stamina, mana** (bars). Ties into the same party system that feeds map positions. One of the most important SkyWynn-native widgets — spec'd in SkyyHud plan v0.3.

---

*Screenshots welcome — especially of your inventory-buttons layout and radial menu, so we can copy the exact ergonomics you like.*
