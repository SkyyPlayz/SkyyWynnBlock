"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.39: the Storage > Supplies tab picture pair (art/hub-tab-icons storage_supplies, notes: tools/menu_0_3_39_patch.py) - TAB_NO_ART
       dropped; MODS_VERSIONS = tools/deploy_set.py SET of 2026-10-18.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.39.py.
0.3.38: the Void Charms rename (notes: tools/menu_0_3_38_patch.py): the SkyyAccessories Mods entry (Server Setup title, blurb, text);
       the Supplies tab icon item (the approved satchel, art/accessory-bag-icon); Teleport Arrange takes warp names with '.' and pages
       with < Prev / Next >.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.38.py.
0.3.37: round tp37 (notes: tools/menu_0_3_37_patch.py): World > Teleport lists island homes (island:fn:homes), homes (essentials:fn:homes)
       and warps (with their SkyyEssentials 0.1.14 icons, essentials:fn:warps) after the fixed spots; Arrange (was Edit) also picks up the
       auto tiles; the art/warp-icons icon items; the Void Charms icon item + Character tab pair = art/void-charms-icon.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.37.py.
0.3.36: MENU PATTERN leftovers (notes: tools/menu_0_3_36_patch.py; research/Menu-Pattern.md rules 7-8, M8, M16): the Admin page on the kit
       1.7 hub page under Settings (sub-tabs, one scroll list), Server Setup's row pages as scroll lists with grow rows, a mod's categories
       in the sub-tab row, in-page pickers for the change log / history filters, crumb texts fitted to their buttons (SkyyAdmCrumb ids).
  CHECKED: see SkyyMenu/test_skyymenu_0.3.36.py.
0.3.35: MENU PATTERN round K (notes: tools/menu_0_3_35_patch.py; research/Menu-Pattern.md; kit skyyui 1.7 hub_page): every Menu page on the
       1600 x 980 kit shell (row 1 + row 2 from HubBar.page17), no back buttons, Your Stats one scroll list, Settings one scroll list per
       category (categories = the sub-tab row), Server Setup's view crumbs as the sub-tab row, Settings drops Edit shortcuts, hub:art.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.35.py.
0.3.34: SMITHHUB (notes: tools/menu_0_3_34_patch.py): saved shortcuts of merged-away tabs open where their page went (tab:storage:bank ->
       the Vault tab, tab:market:auctions -> /ah); the Storage / Crafting blurbs; stand-ins follow the kit's merge data + labels.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.34.py.
0.3.33: HUBCHAR (notes: tools/menu_0_3_33_patch.py; docs/answered/ui.md 2026-10-16 HUB MERGES NOW): Stats is part of the Skills tab (a
       merged tab - kit skyyui HUB_MERGED: still published for shortcuts / commands, never drawn in a strip); the Stats page shows Skills
       selected + the sub-tabs YOUR STATS / SKILLS; + Add keeps Stats and Class; merged pages open through HubBar.openSub.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.33.py.
0.3.32: LIFE01 (notes: tools/menu_0_3_32_patch.py; docs/answered/gear.md 2026-10-16 LIFELONG BAG / POCKET / MENU ITEM): the SkyWynn Menu item
       is lifelong (tools/skyyonce.py MenuOnce*: never dropped / stored / sold, one per profile, extra copies removed with a history line
       first, never in a starter kit); /menuitem (alias of /skymenu) brings it back; Server Setup -> Menu -> Menu item stays with you.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.32.py.
0.3.31: CRAFT01 (notes: tools/menu_0_3_31_patch.py; docs/answered/ui.md 2026-10-16 CRAFTING HUB): the hub row's Smithing is CRAFTING (id
       "smithing" kept), its tabs Crafting (/craft, SkyySacks 0.8.11) + Smithing (/smithing) + Reforge / Upgrade / Identify; /crafting.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.31.py.
0.3.30: MENU0330 (notes: tools/menu_0_3_30_patch.py; docs/answered/ui.md 2026-10-16): no duplicate icons / pages (17 new icon items painted
       at build time; one entry per page, hub:def world -> teleport), the 5 x 5 shortcut grid (+ the one-time update of saved grids), Home
       + Teleport scaled up (120 px slots, big row 1 / row 2), the Right now panel (quest:fn:hud, mystery bags, home:alert:*), stand-in hub
       tabs for contract tabs nobody put (Smithing opens /smithing), hub tab icons, Invite to Guild, Stats Health Regen, Battlemagic.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.30.py.
0.3.29: UNIFIED MENU U1 (notes: tools/menu_0_3_29_patch.py; research/Unified-Menu-Plan.md; kit skyyui 1.6 tools/HUBS-CONTRACT.md; Skyy
       2026-10-15 "1 unified menu for everything" + "combined D and A ... a customizable grid in the center for the shortcuts ... with the
       bub row up top"): Home (row 1 hubs, You, the 7 x 5 shortcut grid whose centre is the old slot 13 screen spot, Right now, Edit
       shortcuts / Close) replaces the 9 x 6 main view; Edit shortcuts (pick up / swap / Remove / + Add / Reset / server default / Old tiles
       back); the one-time layout update (hubs replace covered tiles, History copy, _old, run-once _home); the Teleport page on the same
       grid geometry with its own customizable layout; every Menu page in the kit 1.6 row shell; hub:def default tabs + hub:def:home;
       home:alert:SkyyMenu. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.29.py.
0.3.28: HUBS H2 (notes: tools/menu_0_3_28_patch.py; research/Hubs-Spec.md 1.2 / 2 / 7; kit skyyui 1.5 tools/HUBS-CONTRACT.md; Skyy
       2026-10-10 picked ALL hubs + "can we design it all with the new theme"): the kit's HubBar in this jar; hub:def:<hub> for the 7
       hubs; SkyyMenu's own tabs (character:stats, world:teleport, social:players, settings:settings / layout / mods / setup) with open
       (+ visible) Functions; hub:last:<uuid> in memory (removed on disconnect); /character (/char), /storage, /market, /travel, /social
       open the hub's last / first tab (coming soon while a hub has none); Stats, Settings, Server Setup and the menu's Teleport /
       Players / Mods / layout-editor views draw in the Sky Window hub shell with the shared tab bar (only their title row goes); the
       main menu view is unchanged; the 59 kit textures ship under Common/UI/Custom/SkyyKit/. No saved data. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.28.py.
0.3.27: THE SHARDS TILE GOES (notes: tools/menu_0_3_27_patch.py; Skyy 2026-10-15 SHARD MENUS "make it so the shard menu can only be
       opened on your island. and its hidden everywhere else"): the main-view tile "Shards" (slot 11) is removed with its TILE_RULES
       rule (SkyyShards 0.4 opens each shard's menu only from its portal on your island and publishes no shard:fn:open); the Island
       Menu tile says "Shards: right-click one on your island to open its menu." No saved data. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.27.py.
0.3.26: OUR OWN ICONS, WAVE 1 (notes: tools/menu_0_3_26_patch.py; Skyy 2026-10-15 "lets do our own icons in every menu too."): the 14
       art/menu-icons-2 icons as hidden icon items Skyy_Menu_Icon_<Name> (MENU_ICONS_2): Teleport My Island / Hub / Spawn, every warp,
       a locked warp (NEW ICON_WARP_LOCKED), "No warps yet" (NEW ICON_NO_WARPS); Back / Prev / Next / Close on every page; the player
       head (ICON_PLAYER); Accept / Deny; the Shards tile; player actions 29 / 30 / 31 reuse Hub / Spawn / My Island. Assets.zip = the
       cached copy (tools/serverjar.py). No saved data. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.26.py.
0.3.25: SEARCH BARS + THE SOUND SWITCH + THE SHARDS ADMIN BUTTONS (notes: tools/menu_0_3_25_patch.py): Server Setup's search lists the
       matching SETTINGS of every mod (label / help / key, every word; "Go to" opens the mod on that tab + page); /settings gets a search
       box over every tab (results keep their ON / OFF buttons); the player switch menu.sounds ("Mod sounds", ON) published as
       settings:sounds:<uuid> = Boolean on the bridge (absent / TRUE = on); Admin page Players: + Give Farming Shard / Shard info / Clear
       shard portal / Unload shard world (SkyyShards 0.3 sub-commands). No new saved data. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.25.py.
0.3.24: SOUND PASS ROUND 1 + THE REBIRTH ADMIN BUTTONS (notes: tools/menu_0_3_24_patch.py; research/Sound-Pass-Plan.md): /soundtest
       (skyymenu.modconfig) plays any vanilla sound event 2D to the admin - list (the ids this round's mods use, with where), more (the
       plan's candidates), <n>, next, prev, <SFX id>. The Admin page: + Rebirth crash test / test points / wipe arm / refund arm (SkyyRebirth
       0.3.1 sub-commands, depth 1) on Players, + Sound list / Next sound / Play sound on Diagnostics. No saved data. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.24.py.
0.3.23: THE ADMIN PAGE (notes: tools/menu_0_3_23_patch.py; research/Admin-Page-Plan.md): OpsPage - one kit page (tools/skyyui.py), tabs
       Server / Economy / Players / Diagnostics, a button per admin command of the SET mods (table OPS). A button DISPATCHES the existing
       command as the admin (CommandManager.handleCommand, never re-implemented) and is drawn only while the engine's own
       hasPermission of that exact command node passes; the page needs skyymenu.modconfig. Danger buttons: the same button again
       within 10 s. Player picker (< >) + one Text box. Status text from the bridge (auction:count, bazaar:products). Opened by
       /modconfig admin and Server Setup's "Admin" button. No saved data. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.23.py.
0.3.22: THE SHARDS TILE (notes: tools/menu_0_3_22_patch.py; Gathering-Shards-Spec phase 5 "SkyyMenu (hub button)"): main-view tile "Shards"
       at row 1, col 2 (slot 11), drawn only while SkyyShards publishes shard:fn:open (TILE_RULES "need"); the click = apply(UUID) on the
       world thread = SkyyShards' shard menu. Icon: the vanilla Portal_Device. No saved-data change. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.22.py.
0.3.21: THE MESSAGES TAB (notes: tools/menu_0_3_21_patch.py; Skyy 2026-10-12 CHAT OVERFLOW): a ninth /settings tab "Messages" (category
       messages, before General) for SkyyHud's 22 Chat / Feed / Off switches (msg.<kind> + msg.<kind>.feed), in SkyyHud's kind order
       (SET_ORDER_MSG); General is back to its own rows. With 9 visible tabs the strip draws 5 per row at 206 px (else 0.3.20's 4 x 252).
       No saved-data change. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.21.py.
0.3.20: THE PROFILE NAME FOLLOW-UP (notes: tools/menu_0_3_20_patch.py; Skyy 2026-10-13 "have the name show (Class) (profile name."; for
       SkyyProfiles 0.1.12's profile:name = "<Class> <name>" + profile:pname = the bare name): the Pets tile shows the whole "<Class>
       <name>" (cut at 27 instead of 24; longer = 24 + "..."); the Stats page's Profile row + header show the bare name (profile:pname,
       else profile:name) next to the class. No saved-data change. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.20.py.
0.3.19: LAG FIXES + THE HUB HOTKEY (notes: tools/menu_0_3_19_patch.py; Skyy 2026-10-13 "lets audit the code structure, and make sure they
       are working together in the smoothest easiest lag free way possible" + the popup "Hotkey now + probe the icon panel"): lock-free
       bridge; one private writer thread SkyyMenu-IO (MenuIO) for every settings / layout / Server Setup / menu-item file and the 30 s
       upkeep (never HytaleServer.SCHEDULED_EXECUTOR); the menu item grant checks its files on SkyyMenu-IO and only counts / gives on the
       world thread; the profile watch acts on profile:epoch changes; the menu's safety net backs off (1 -> 2 s while healthy);
       Settings / Server Setup read a small index (MenuIdx) instead of scanning the bridge; DOUBLE-TAP CROUCH opens the SkyWynn Menu
       (MenuHotkey, player switch menu.hotkey ON by default; not over an open window; timing in Server Setup). No saved-data
       format change. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.19.py.
0.3.18: THE HYTALE 0.7.0 PORT (notes: tools/menu_0_3_18_patch.py; Skyy 2026-10-13 "hytale 0.7.0  is out!"; research/Hytale-0.7-Port.md):
       PageManager.handleEvent -> handleLegacyCustomPageEvent, clearCustomPageAcknowledgements -> clearLegacyCustomPageAcknowledgements
       (same engine bodies), the Spawn tile: ISpawnProvider.getSpawnPoint -> getSpawnPointAsync (a future, never waited for: SpawnTask
       finishes the teleport on the player's world thread - MenuPage.spawnResolved). Nothing else changed. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.18.py (CC 0.3.17 -> 0.3.18, A -Xverify:all on the 0.7.0 jar, E the page check + the Spawn
  tile executed through the 0.7.0 engine's own PageManager / spawn providers, ST two starts on a copy of the live data, AA the audit).
0.3.17: THE MENU LAYOUT EDITOR (notes: tools/menu_0_3_17_patch.py; Skyy 2026-10-10 "can you make a menu editor that allows users to
       rearrange the menu?", "make sure the flavor text of the edit button explains that it doesn't support dragging."): an Edit layout
       tile (main slot 53) - no dragging: click a tile, click its new slot, they swap; click it again = cancel; Reset to default; admins:
       Save as server default / back to layout D; Done. Saved per player (account uuid) in Skyy_SkyyMenu/layouts/<uuid>.properties, the
       server default in Skyy_SkyyMenu/layout-default.properties (MenuLayout + LayoutSaveTask). Hidden tiles keep their slot, unknown tile
       keys are ignored, new tiles go to the first free slot, an unreadable file = the default + one warning. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.17.py (every 0.3.16 check carried forward + CC 0.3.16 -> 0.3.17 + E the editor executed
  through the engine's PageManager: swap, cancel, reset, per-player files, server default, kept slots, unknown / new tiles, corrupt
  files, two starts on a copy of the live data + AA the engine-access audit).
0.3.16: LAYOUT D + OWN TILE ICONS + PER-TILE VISIBILITY RULES (notes: tools/menu_0_3_16_patch.py; Skyy 2026-10-10 "go with D",
       "beautiful! i love it", "can we control what's visible in the menu with permissions?"): the main view = layout D (Teleport on
       slot 13 under the mouse, the plus around it, social bar left, admin bar right, MAIN_D); every main tile wears its art/menu-icons
       icon (22 new hidden icon items Skyy_Menu_Icon_<Name>, MENU_ICONS); TILE_RULES (perm node / Server Setup switch / bridge Function
       needed / bridge unlock Function) decide which tiles are drawn - a hidden tile leaves its slot empty; a Wardrobe tile (slot 36)
       appears only while SkyyWardrobe publishes wardrobe:fn:open (click = apply(UUID)). No saved data; ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.16.py (every 0.3.15 check carried forward + CC 0.3.15 -> 0.3.16 + JT the icon items + D the
  layout, admin vs player, hidden-tile gaps, unlock / need / Wardrobe executed through the engine's PageManager + AA the engine-access audit).
0.3.15: THE MENU ITEM WEARS THE NEW SKYWYNN EMBLEM (art only; notes: tools/menu_0_3_15_patch.py; Skyy "lets make a new icon for the menu",
       "perfect! use it"): Skyy_Menu's look = our own art/menu-emblem/ (a floating sky island + a gold compass star): fixed item fields
       MENU_ITEM_FIELDS (Model / Texture / Icon shipped in this jar, checked against the art manifest; Scale / animations / icon framing
       / glow radius = the vanilla Voidheart's, glow colour warm gold) instead of the borrowed Voidheart look; the Mods list's SkyyMenu
       row shows it. Same item id - players' menu items just change look. No code change, no saved data; ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.15.py (every 0.3.14 check carried forward + CC 0.3.14 -> 0.3.15 + JT the emblem assets + MR the
  Mods row executed + V the engine's asset validators on the jar).
0.3.14: THE PETS TILE IN THE TOP BAR (notes: tools/menu_0_3_14_patch.py; Skyy 2026-10-10 "add pets to the top bar of the menu by profile.
       (like everything else, pets are per profile. they dont transfer.)"): main slot 5 (right of Your Profile) runs /pets as the player
       (the Accessory Bag pattern); hidden unless SkyyPets is loaded (pets:fn:onxp + /pets). Hover "Pets - <pet> Lv N" + the pet slot,
       summon slot, pets owned - read from SkyyPets' own per-PROFILE record Skyy_SkyyPets/pets/<storage key>.properties (read only,
       cached by modified time + size). Icon = the pet-slot pet's art (15 launch pets, our icon items Skyy_Menu_Icon_Pet_<Pet>) else the
       vanilla Farming_Collar. ROUND_PINS = {}. No saved data, no other tile moves.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.14.py (every 0.3.13 check carried forward + CC 0.3.13 -> 0.3.14 + PT the Pets tile flows).
0.3.13: THE MONK SKILL IS ZEN + CLASS BALANCE DAMAGE ON THE STATS PAGE (notes: tools/menu_0_3_13_patch.py; Skyy LOCKED 2026-10-08 Monk
       skill "Zen"; "Show skill Defense and the class-balance damage % on the Stats page ... -> Yes, next (Recommended)"): CLASS_SKILLS
       Monk = Zen (Mods texts, Skills tile); Stats page Class Weapon Damage = level part + SkyySkills 0.4.26's skill:dmg:<uuid> (a
       Double percent), breakdown "Class balance +X%"; without it (older / no SkyySkills, any other type) the row is exactly 0.3.12's.
       ROUND_PINS = SkyySkills 0.4.27, SkyyClasses 0.1.15, SkyyTrees 0.3.5, SkyyProfiles 0.1.8 (deploy together). No saved data.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.13.py (every 0.3.12 check carried forward + K7 0.3.12 -> 0.3.13 + ZN the Zen texts + DM the
  Class Weapon Damage row).
0.3.12: THE STATS PAGE DEFENSE ROW COUNTS THE SKILL DEFENSE (notes: tools/menu_0_3_12_patch.py; Skyy "Show skill Defense and the
       class-balance damage % on the Stats page (a small SkyyMenu build)? -> Yes, next (Recommended)"): Main tab Defense = gear +
       accessories + SkyySkills 0.4.25's skill:def:<uuid> (Foraging + class balance Defense, a Double), breakdown "Skills +X"; without
       it (older / no SkyySkills, any other type) the row is exactly 0.3.11's. Class Weapon Damage unchanged (SkyySkills 0.4.25 publishes
       no class balance damage %). No saved data, no layout change; ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.12.py (every 0.3.11 check carried forward + K6 0.3.11 -> 0.3.12 + SD the Defense row).
0.3.11: THE ACCESSORY BAG TILE SHOWS OUR OWN ICON (art only; notes: tools/menu_0_3_11_patch.py; Skyy 2026-10-08 "Yes, the bag icon looks
       good, commit it"): the jar ships the icon-only item Skyy_Menu_Icon_AccessoryBag (hidden from the creative library) whose Icon is
       art/accessory-bag-icon/.../SkyyAccessories_Bag_Menu.png (shipped at Common/Icons/ItemsGenerated/), and the main menu's Accessory Bag
       tile uses it (was the vanilla Utility_Bag_Seed). No code change; ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.11.py (every 0.3.10 check carried forward + K5 0.3.10 -> 0.3.11 + IC the icon item + V the
  engine's asset validators on the jar).
0.3.10: THE STATS PAGE, phase 1 (research/cloud/Stats-Page-Spec.md P1; notes: tools/menu_0_3_10_patch.py): the Your Profile tile and
       /stats (/profilestats) open StatsPage - a vanilla-kit inline page (tools/skyyui.py) with every LIVE stat of the active profile
       (Health / Mana / Stamina from the EntityStatMap split by modifier source, gear + accessory stats, speed / jump / fall damage,
       Mana Regen, Fortune as double-drop %, Wisdom, skills, Overall, class, purse, bank, bags) in five tabs, and a Change Profile
       button (runs the player's own /profiles; hidden without it). The Your Profile hover text is short lines. No saved data, no
       setting, no other mod changed; ROUND_PINS = {} (deploys on its own).
  CHECKED: see SkyyMenu/test_skyymenu_0.3.10.py (every 0.3.9 check carried forward + S the Stats page flows + K4 0.3.9 -> 0.3.10).
0.3.9: CLASS TEXTS ONLY (no behaviour change; notes: tools/menu_0_3_9_patch.py): Assassin + Monk are playable (SkyyClasses 0.1.14,
       SkyySkills 0.4.21 Discipline, SkyyProfiles 0.1.6 - ROUND_PINS, deploy together): CLASS_PLAYABLE = all seven, CLASS_LATER = none,
       CLASS_SKILLS + Assassination + Discipline; the Classes / Profiles / Skills Mods texts + the main menu Skills tile name them. Every
       other Mods version stays 0.3.8's (a version catch-up is a later round).
  CHECKED: see SkyyMenu/test_skyymenu_0.3.9.py (every 0.3.8 check carried forward + F4 the 0.3.9 class texts + K4 0.3.8 -> 0.3.9 data only).
0.3.8: DATA / TEXT ONLY (no behaviour change; notes: tools/menu_0_3_8_patch.py): the Mods list = tools/deploy_set.py SET of 2026-10-05
       evening + this round (ROUND_PINS: SkyyTrees 0.3.2, class trees ON by default) - Collections 0.2.6, Party 0.1.7, Bazaar 0.1.4, Gear
       0.2.3, Skills 0.4.16, Essentials 0.1.8 (26 mods); help texts: Gear crafting Smithing XP, Skills own XP list per skill, Party TPA /
       Accept TPA buttons, Bazaar progression prices, Trees Alchemy / Smithing + the class tree (/tree class, /tree probe for admins).
  CHECKED: see SkyyMenu/test_skyymenu_0.3.8.py (every 0.3.7 check carried forward + F3 the 0.3.8 texts + K3 0.3.7 -> 0.3.8 data only).
0.3.7: DATA / TEXT ONLY (no behaviour change; notes: tools/menu_0_3_7_patch.py): the Night Vision help texts are gone (SkyyAccessories
       0.5.4 retired it for the Lantern line); the Mods list = tools/deploy_set.py SET of 2026-10-05 + this round (ROUND_PINS: SkyyExploration
       0.2.3, SkyyAccessories 0.5.5, SkyyCooking 0.1.6) + the missing SkyyArmory 0.1 entry (26 mods); SkyyUiProbe 0.4 /skyprobe map line;
       the live-set check's two differences fixed (SkyyBazaar 0.1.3's Server Setup page Bazaar, SkyyGear 0.2.2's gear.critFx switch).
  CHECKED 2026-10-05 with SkyyMenu/test_skyymenu_0.3.7.py (needs SkyyMenu-0.3.5.jar + SkyyMenu-0.3.6.jar): 975 checks, 0 fail -
    every 0.3.6 check carried forward (P: 0.3.5 still reproduces the stuck page, 0.3.7 fixes it), F2 the 0.3.7 texts (no Night
    Vision anywhere, the Lantern, SkyyArmory, /skyprobe map, Bazaar Server Setup, gear.critFx), K2 0.3.6 -> 0.3.7 data / version only.
0.3.6: THE STUCK-PAGE FIX (root cause proven 2026-10-03 by the SkyyBank 0.1.6 round, re-read from the release HytaleServer.jar bytecode)
       + the Mods list = tools/deploy_set.py SET of 2026-10-03 (25 mods). Notes: tools/menu_0_3_6_patch.py.
  ENGINE: PageManager.handleEvent drops every page click (Data) while customPageRequiredAcknowledgments != 0 - silently; Dismiss only
    runs customPage.onDismiss(ref, store) + customPage = null (no packet, no counter change). Every page packet adds 1 (openCustomPage,
    rebuild, sendUpdate; setPage / close / setPageWithWindows only while a custom page is open), every client acknowledgement takes 1
    off. World.addPlayer - the one way into a world - dispatches AddPlayerToWorldEvent (the player in no world store yet; a teleport
    does it on the old world's thread right after PlayerRef.removeFromStore), then onSetupPlayerJoining clears the counter but keeps
    PageManager.customPage, and only later adds the player to the new world's store. The client drops its page at a world change. So
    a page open across a world change stayed "open" on the server, and SkyyMenu 0.3.5's CloseTask (~150 ms after the Island / Hub tile,
    on the new world) closed it with setPage(None): +1 the client never acknowledges -> EVERY custom page (Bank, Vault, Menu, Sacks,
    Server Setup ...) ignored clicks until the next world change. A bench after a world change did the same.
  1. CloseTask / RefreshTask never close or redraw a menu the client no longer shows: if the player changed world since the menu was
     opened (MenuPage.changedWorld - its first build's world differs, or PageGuard counted a world join since), the menu is forgotten
     on the server the way Esc does it (PageGuard.forget = PageManager.handleEvent Dismiss: no packet, counter unchanged).
  2. PageGuard (AddPlayerToWorldEvent, every page of every mod): the page a player still has on the server when the engine adds them
     to a world is from before the world change. A page with the engine's empty onDismiss (the menu, Settings, Server Setup and most
     pages) is forgotten right there (handleEvent Dismiss, no page code runs, no packet) - before the counter reset and before anything
     of the new world can run, so no later setPage can add an unacknowledged count because of it. A page with its own onDismiss (Bank,
     Vault, trades, Profiles, vanilla Respawn ...) is forgotten by StaleTask on the new world's thread as soon as the player is in its
     store, with the player's real ref / store, and only while it is still that exact page.
  3. MenuWatch, the safety net (BankWatch's pattern, the menu page only): 1 s checks while a menu is open; a world change -> forget; 1 s
     after the menu's last packet a test click through the engine's gate; dropped -> clearCustomPageAcknowledgements + an answer (at most
     3 per menu, later heals reset silently). A healthy menu sends nothing. A generic net is left out on purpose: it would need test
     clicks into other mods' pages or the engine's private counter. A healed counter frees every page.
  4. Mods list texts = the 2026-10-03 SET: NEW SkyyWorldGen 0.1 (every /zone command admin-only, Server Setup -> World Gen); Hud 0.3.12
     combat indicator, Bank 0.1.6, Gear 0.2.1 damage + armor by level, Skills 0.4.14 kill XP by mob level / early gathering / roll
     landings, Accessories 0.5.3 Night Vision, Cooking 0.1.4 +32% per Grade, UiProbe 0.3.1, Mobs 0.1.2 difficulty ladder + health floor.
  CHECKED with SkyyMenu/test_skyymenu_0.3.6.py (committed - re-run it, it needs SkyyMenu-0.3.5.jar too) - 2026-10-03, 938 checks,
    0 fail; ONE JVM, -Xverify:all, the 0.3.6 and 0.3.5 jars each in their own class loader over HytaleServer.jar: A all 40 + 37 classes
    load, verify, initialise. B - J every 0.3.5 check on 0.3.6 (permissions, registry, Settings page, the round's rows, review fixes,
    seconds rows, the item per profile, two starts on copies of the live Skyy_SkyyMenu data - as it is and as 0.3.3 left it: the second
    start writes nothing). F the 25-mod Mods list = SET and the 0.3.6 texts. P on the engine's own PageManager with a model client:
    THE ISLAND TILE (the real grid click -> MenuPage.click / runCmd -> /island -> a world change in the engine's order -> the CloseTask the
    menu chained on the command): 0.3.5 sends setPage(None) on the new world, 1 acknowledgement pending, the next SkyWynn Menu and a
    stand-in Bank page drop every click (the bug); 0.3.6 forgets the menu at the world join (no packet, counter untouched), the CloseTask
    sends nothing, 0 pending, both next pages work - also without the event (the CloseTask's own world check) and on a re-join of the
    same world; the other CloseTask timings are safe on both jars. RefreshTask and a bench after a world change: 0.3.5 stuck, 0.3.6
    healthy. Unchanged on both jars: the Close button, a same-world CloseTask / RefreshTask, Esc. No packet to a player without a page.
    PageGuard: the menu, Settings, Server Setup and a stand-in page forgotten at the event; pages with their own onDismiss forgotten by
    StaleTask on the new world's thread with the NEW ref / store (replaced, throwing and leaving cases); joins counted, dropped at
    disconnect. MenuWatch: healthy = silent, a stray packet healed once (one WARNING, one answer, the next click works), at most 3
    answers per menu, a world change forgotten, the real timer chains (scheduler -> World.execute), no scheduler = still works.
    K 29 of 37 classes byte-identical; MenuPage changed only build / clearGrid / handleDataEvent (+ who / changedWorld / watchFail /
    watchTick), CloseTask / RefreshTask only run, MenuQuit only accept, SkyyMenuPlugin only setup / shutdown, CfgRows / CfgFn /
    manifest only the version. X 12846 references pass MethodHandles.Lookup in their own class, 0 refused (control: an outside
    MenuPage.rebuild is refused and throws IllegalAccessError). Also (scratch): the whole SET with 0.3.6 - 25 jars, 1101 classes,
    -Xverify:all, 0 failures; lint 0 fails (26 warnings, all SkyySacks 0.7.12); tools/skyyui_test.py 10060 ok + the 1 known stale fail
    (base-gated WrapMaxLines); tools/skyycfg_test.py PASS; tools/deploy_set.py --check all 25 jars present.
  UNVERIFIED (needs the game): the client dropping its page at JoinWorld (the 0.1.6 bank round's model, matches Skyy's client log); the
    menu's heal answer clearing a "Loading..." box (the bank's answer is the same kind of page update); the real timing of the 1 s checks
    for a remote player (a client slower than 1 s to acknowledge can make a check reset early - the engine's own "unexpected
    acknowledgement" line follows, harmless).
0.3.5: DATA / TEXT REFRESH ONLY (no behaviour change): the Mods list = tools/deploy_set.py SET of 2026-10-02 (24 Skyy mods: the NEW
       SkyyMobs 0.1 entry, SkyyUiProbe 0.3 still a dev mod) through ONE version table, MODS_VERSIONS in MENU DATA (every MODS entry
       reads it; the build prints the table for the live SET when a version differs); help texts for what shipped on 2026-10-01 /
       2026-10-02 - Sacks stack refill / bags add up / benches + inventory crafting use the bags, Collections coins never buy tiers,
       Essentials no Magic Bags in /trade, Hud Skills widget, Skills class curve + in-combat Mana + /skills mana, Gear item levels +
       /gear relevel, Mobs /mobs, UiProbe win / secgrid, Accessories Workbench tab, Guilds leave refund; the live-set check reads a
       config kit emit with MOD=<module constant> (SkyyMobs). Notes: tools/menu_0_3_5_patch.py.
0.3.4: Skyy's 2026-10-01 decisions: the SkyWynn Menu item once PER PROFILE (records given-profile/<storage key>.txt; the old
       per-player flags given/<uuid>.txt only read: the profile active at the first 0.3.4 sight counts as given; never a second copy
       while one is anywhere in the inventory incl. utility / tools; waits while profile:busy; PlayerReadyEvent + a 2 s profile
       watch); Server Setup shows and takes millisecond rows (unit ms) in SECONDS with decimals (0.24 = 240 ms, rounded to whole ms,
       the file keeps ms; log, undo and kit messages in seconds too); MODS data = tools/deploy_set.py SET of 2026-10-01 (Profiles
       0.1.5 delete / restore / archive, Accessories 0.5.1, Gear 0.1.2, SkyyUiProbe as a dev mod). Notes: tools/menu_0_3_4_patch.py.
0.3.3: SkyyGear compat + Skyy's Settings locks (research/SkyyGear-Stage1-Spec.md 7.3.2, research/Settings-Spec.md 4.1 / 4.4): an
       Identify tile (main slot 26, /identify, greyed while SkyyGear is absent), Reforge text for SkyyGear, SkyyGear 0.1 replaces SkyyRolls
       in the Mods list; the Settings torch at main slot 39 (left of Mods); settings visibility by permission (optional 7th registration
       element = a node; rows the player may not change are hidden, never greyed; settings:fn:set refuses them); the refusing General
       switches party.invites / tpa.requests / msg.private, skills.overallUp, the crossbow switches and SkyyGear's three in the known
       list; Mods texts of rounds 8 + 9; the live-set check also accepts this round's SET (ROUND_PINS / ROUND_RETIRED); kit KEEP 10.
       Review fixes: a bad node refuses the key for good (hidden, set refused, get = its default), plain nodes only, the stricter
       node wins when two mods register one key; (admin) / (staff) Commands lines only in the admins' Mods text; /rank set <player> <rank>.
       Notes: tools/menu_0_3_3_patch.py.
0.3.2: menu data for round 6 (Berserker / Fury, Priest / Divinity, class kits): every class text names the 7-class roster (Archer,
       Warrior, Mage, Berserker, Priest playable; Assassin, Shaman later) and the weapon skills; SkyyClasses /class kit + the admin
       line /classadmin kit; Mods list versions = tools/deploy_set.py SET (SkyySkills 0.4.5 + SkyyGuilds 0.1.3 = the round's pins,
       ROUND_PINS); the Priest heal switches classes.healGiven / healTaken in the known list and the defaults template; roster checks.
       Notes: tools/menu_0_3_2_patch.py.
0.3.1: menu data brought up to the live set (tools/deploy_set.py SET, round 4): Mods list versions, config files, reload commands and
       a description of each mod's Server Setup page (the list itself still comes from the config:def: scan); SkyyRanks in the list;
       admin-only command lines for admins (Essentials /warpadmin, Party /partyadmin, Hud /skyyhud default, Islands, ...); the guild
       switches in the known list and the defaults template; Settings tabs hold 8 rows per page (paging stays); a build-time
       cross-check against the live scripts. Notes: tools/menu_0_3_1_patch.py.
0.3:   Server Setup, the admin Mods section (research/Server-Setup-Spec.md section 2): a book at menu slot 41 and /modconfig
       (alias /serversetup, node skyymenu.modconfig) open one 1120 x 930 page with seven views - the mod list (every installed Skyy
       mod; mods on the config registry first, the rest file only with their path and reload command; search), a mod's settings
       (tabs, a widget per type, Default, drafts), table / list editor, confirm, Changes (log + undo), History (preview + restore),
       Export / Import (codes + files). One guard() re-checks the node first in every build and click. SkyyMenu's own settings
       (menu item, Mods tile, tooltip default, player settings defaults table) go through tools/skyycfg.py. Notes: tools/menu_0_3_patch.py.
0.2:   the player Settings page (research/Settings-Spec.md): a settings registry on the skyy.bridge map (settings:fn:register / get /
       set; settings:def:<key> drained at start and at every page open), per-player files Skyy_SkyyMenu/settings/<uuid>.properties
       (saved 500 ms after a change, atomic writes, never overwritten when unreadable), server-wide defaults in
       settings-defaults.properties (commented template written once, re-read within 30 s), /settings (alias /skysettings) and a torch
       at menu slot 51 opening a 1120 x 930 page: 8 tabs, ON/OFF rows, Reset all (two clicks), < SkyWynn Menu, Close. SkyyMenu's own
       switch menu.tooltips = the 0.1.3 Hover Tooltips book (0.1.3 notips/<uuid>.txt files move into it at the next join). New
       Auction House entry (/ah, SkyyAuctions) + SkyyAuctions in the Mods list. Notes: tools/menu_0_2_patch.py.
0.1.3: new entries Island Menu (/island menu), Vault (/vault), Reforge (/reforge), Guild (/guild); Party opens the /party page and Bank
       the /bank page (all page commands keep the 0.1.2 open-over-the-menu rule; the Bank + Party submenus are gone); a per-player
       Hover Tooltips switch (the only sure stuck-tooltip fix; saved off the world thread); stuck-tooltip mitigations (every server-side
       close empties the grid first, an experimental Esc hook on the page root); Mods list = the live 19-mod set; Islands wording follows
       the installed SkyyIslands; the menu item grant waits out profile:busy; a runtime check that /menu, /sbmenu, /skymenu are ours.
       Notes + the tooltip investigation: tools/menu_0_1_3_patch.py.
0.1.2: pages opened from the menu no longer hang on Loading... (the menu is not closed before a page command; CloseTask closes it
       afterwards only if it is still open) and the page is 1.4x bigger. Notes: tools/menu_0_1_2_patch.py.
0.1.1: menu commands switched to the short positional forms (/bank deposit all, /island visit <p>, /skyyhud export ...) now that the mods have usage variants/subcommands.
Run:   python build_skyymenu_0.1.py            -> SkyyMenu/SkyyMenu-0.1.jar
       python build_skyymenu_0.1.py --deploy   -> also copies to Mods/SkyyMenu.jar and enables it in the HUD mod world

A Hypixel SkyBlock style menu ("SkyBlock Menu" = a Nether Star in hotbar slot 9 + /sbmenu) for everything the Skyy mods add.
Skyy's request: an item you right-click to open, plus /skymenu if you lose it. First entry Teleport (island, hub, spawn, every
warp that is set), then Pocket Dimension, Accessory Bag, HUD editor, ... and Mods (every mod with what it does and its commands,
shown as items with flavor text like Minecraft).

EDIT THE MENU HERE: everything a player sees (entries, icons, texts, the mod catalog) is Python data in the "MENU DATA" section
right below. The Java is generated from it. Every icon id is checked against Assets.zip when you build.

How it works (all patterns copied from working code, see the notes next to each class):
 - Item Skyy_Menu ("SkyWynn Menu", our own SkyWynn emblem look since 0.3.15 - was the Voidheart's -, glows): right-click -> OpenCustomUI page "SkyyMenu"
   (item JSON Interactions.Secondary + OpenCustomUIInteraction.registerSimple, the SkyySacks / SkyyAccessories pattern).
 - Given once per PROFILE (0.3.4; once per player before): PlayerReadyEvent (fires on EVERY world switch) or the 2 s profile watch
   (GivenTick) -> in-memory once-per-session guard keyed by the profile's storage key -> GrantTask polls
   until the player's world resolves, re-runs itself on that world's thread (world.execute, SkyySacks GrantTask pattern), skips
   if the player already holds the item, puts it in the LAST hotbar slot if free (Hypixel slot 9), else hotbar / storage /
   backpack, count-verified. Persisted flag = Skyy_SkyyMenu/given/<uuid>.txt (atomic tmp + move) so it is never re-given
   after a restart. Inventory full -> message, retried on the next login (PlayerDisconnectEvent clears the session guard).
   0.3.4: the persisted record is Skyy_SkyyMenu/given-profile/<storage key>.txt (profile:fn:key; <uuid> = profile 1 or no SkyyProfiles);
   the old given/<uuid>.txt flags are only read (Given.migrate: the profile active at the first 0.3.4 sight counts as given).
 - /skymenu (+ /menu and /sbmenu when no vanilla or Skyy command uses them - checked at build time below) opens the page and
   gives the item back if the player has none. Everyone may use it: setPermissionGroups({"hytale:Adventurer"}), the vanilla
   /help /who /ping pattern (SkyyEssentials does the same).
 - Page: ONE inline CustomUIPage, views switched with rebuild(). A 9 x 6 ItemGrid (AreItemsDraggable: false) of item icons;
   every slot is an ItemGridSlot with setName + setDescription (the tooltip; multi-line, "Click to open!" footer in yellow
   markup) and clicks arrive through the SlotClicking binding with "SlotIndex" in the payload. Proof it works on a non-draggable
   grid: TheArmoryMod 1.22.0 ScribingPage (ItemGrid #PickerGrid AreItemsDraggable false + SlotClicking + regex on "SlotIndex",
   ItemGridSlot.setDescription with <color>/<b>/<i> markup) and our own SkyyHud 0.3.x editor. Like TheArmoryMod the grid binding
   does not lock the interface (addEventBinding(..., false)), so a click on an empty slot never leaves the UI waiting. Under the grid an info box
   repeats the name + text of the last clicked entry (fallback if tooltips do not render), a status line, and a footer with
   Back / Prev / Next / Close TextButtons (proven Activating binding) as a second way to navigate.
 - Actions run the other mods' commands AS THE CLICKING PLAYER with CommandManager.get().handleCommand(playerRef, "cmd args")
   (exactly what vanilla /su does; permission checks apply as if the player typed it). Before that the menu checks
   resolveCommand(name) (mod installed?) and AbstractCommand.hasPermission(playerRef) and says what is wrong instead of failing.
   (0.1.2+) The command runs with the menu still open: a page command replaces the menu, anything else closes it ~150 ms later.
 - Warps: listed live from the vanilla TeleportPlugin.get().getWarps(); a click teleports with the exact vanilla WarpCommand.tryGo
   calls (Warp.toTeleport() + Store.addComponent(Teleport)) instead of dispatching /warp, because vanilla gates /warp go to
   hytale:Builder (normal players would get "no permission"). Per-warp locks later: MenuUtil.isWarpUnlocked(player, warpId).
   Spawn: the default world's spawn point, same calls as vanilla SpawnCommand / SkyyIslands /hub fallback.
 - Profile tooltip reads the JVM bridge: coins:fn:get (or coins:<uuid>), bank:<uuid>, skill:<uuid>, acc:has/acc:tal, coll:recipes.

FOUND WHILE BUILDING THIS (affects other mods, NOT fixed here - see the report):
 1. Optional command arguments need "--name value". `/bank deposit all` fails with "wrong number of required parameters"
    (verified live against the engine parser with the SkyyBank 0.1 jar); `/bank --action deposit --amount all` works. Same for
    /island visit|invite|info, /skyyhud export|import|reset|profile|preview, /collections unlocks|reload, /rolls, /deathpenalty,
    /bankconfig, /bazaaradmin. The menu dispatches the working "--name value" form and the Mods list shows that form.
 2. Commands without requirePermission get an auto-generated node "<group>.<name>.command.<cmd>" lower-cased with spaces -> "_"
    (e.g. skyy.0.6.1_skyysacks.command.sacks - it changes with every version bump). Normal players (hytale:Adventurer) have no
    permissions, so they cannot run /sacks /skills /island ... at all, typed or from the menu, until those mods call
    setPermissionGroups(new String[] { "hytale:Adventurer" }) like SkyyEssentials, or Skyy grants the nodes. Admins ("*") are fine.
"""
import sys, os, json, re, struct, zipfile, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG        # 0.3: the admin config kit (SkyyMenu's own settings, research/Server-Setup-Spec.md 1.4)
import skyyui as SUI         # 0.3.10: the shared vanilla UI kit - the Stats page only (the older menu pages keep their own look)
import serverjar as _SJ      # 0.3.26: the CACHED Assets.zip (tools/serverjar.py) - never the installed game file
import skyyonce as ONCE      # 0.3.32: the lifelong SkyWynn Menu item (one shared generator with SkyyAccessories 0.5.20 / SkyySacks 0.8.12)
ASSETS_ZIP = _SJ.assets_zip()   # read-only

VERSION = "0.3.39"
HERE = os.path.dirname(os.path.abspath(__file__))

# 0.3.1: the config kit this jar carries (tools/menu_0_3_1_patch.py pins it, 0.3.2 and 0.3.3 keep the pin - change it with a rep in
# tools/menu_0_3_3_patch.py; see the "config kit" lines of the build output)
import hashlib, subprocess
EXPECTED_KIT = "1.1"
def kit_blob(path):
    """git blob id of the kit source (= git rev-parse HEAD:tools/skyycfg.py when the file is the committed one)"""
    d = open(path, "rb").read()
    return hashlib.sha1(("blob %d" % len(d)).encode("ascii") + b"\x00" + d).hexdigest()
KIT_FILE = os.path.abspath(CFG.__file__)
KIT_NOW = getattr(CFG, "KIT_VERSION", "1.0")      # the committed kit 1.0 has no KIT_VERSION constant
assert KIT_NOW == EXPECTED_KIT, ("tools/skyycfg.py is config kit %s, SkyyMenu %s pins kit %s - pick a kit change up on purpose: "
                                 "set EXPECTED_KIT through tools/menu_0_3_10_patch.py (or its successor), regenerate, re-test" % (KIT_NOW, VERSION, EXPECTED_KIT))
KIT_BLOB = kit_blob(KIT_FILE)
try:
    _head = subprocess.run(["git", "-C", os.path.dirname(os.path.dirname(KIT_FILE)), "rev-parse", "HEAD:tools/skyycfg.py"],
                           capture_output=True, text=True, timeout=30).stdout.strip()
except Exception:
    _head = ""
KIT_STATE = ("the committed file" if _head == KIT_BLOB else "NOT the committed file (git HEAD has %s)" % _head[:12]) if _head else "git not available"
KIT_ID = "%s %s" % (KIT_NOW, KIT_BLOB[:12])
print("config kit %s: tools/skyycfg.py blob %s, %s" % (KIT_NOW, KIT_BLOB[:12], KIT_STATE))
if _head and _head != KIT_BLOB:
    print("WARNING config kit: tools/skyycfg.py has uncommitted edits - this jar carries that exact revision (blob %s); "
          "rebuild once the kit is committed" % KIT_BLOB[:12])

# =====================================================================================================================
# ================================================  MENU DATA (edit me)  ==============================================
# =====================================================================================================================
# Text rules: no double quotes, braces, semicolons or backslashes. Write command arguments as <player> - they are shown as
# [player] because < > is tooltip markup. Each entry's text is a list of lines: the FIRST line is the description paragraph,
# the others are detail lines. Slots: 0-53, row by row (9 per row, 6 rows). Row 5: 45 = Back, 48 = Prev, 49 = Close, 50 = Next.
#
# Actions:  view:<main|tp|players|mods>  open a submenu                   cmdc:<command line>  run it, then close the menu (a page
#           cmd:<command line>  run it, keep the menu open (refreshes)         command simply replaces the menu)
#           profile  open the Stats page (0.3.10; was: show stats in the box)  info   just show the text in the info box
#           spawn  teleport to the main world spawn                       tips   switch this player's hover tooltips on / off
#           settings  open the player Settings page (0.2, same as /settings)
#           admin  open Server Setup (0.3; only admins see this entry - players never do)

MENU_ITEM_ID = "Skyy_Menu"
MENU_ITEM_NAME = "SkyWynn Menu"
# 0.3.15: THE MENU ITEM'S OWN LOOK (Skyy "lets make a new icon for the menu", "perfect! use it"): the SkyWynn emblem art/menu-emblem/
# (README + manifest.json; check python tools/art/validate_menu_emblem.py). Fixed fields = the manifest's "suggested_item_fields"; Scale /
# PlayerAnimationsId / IconProperties / Light.Radius = the vanilla Ingredient_Voidheart's (the look 0.3.14 borrowed: same hand pose, size,
# icon framing, glow radius), the glow colour a faint warm gold. Every key is checked against the Voidheart's JSON at build.
MENU_ITEM_FIELDS = {
    "Icon": "Icons/ItemsGenerated/Skyy_Menu.png",
    "Model": "Items/SkyyMenu/Skyy_Menu.blockymodel",
    "Texture": "Items/SkyyMenu/Skyy_Menu_Texture.png",
    "Scale": 1.2,
    "PlayerAnimationsId": "Item",
    "IconProperties": {"Scale": 0.9, "Rotation": [0, 0, 0], "Translation": [0, -13]},
    "Light": {"Color": "#432", "Radius": 1},
}
MENU_ITEM_KEYS_FROM = "Ingredient_Voidheart"   # 0.3.15: the vanilla item the fields' keys (and the pose values) are checked against - never copied
MENU_ART_DIR = "art/menu-emblem"               # 0.3.15: the art folder (its manifest.json lists every file with bytes + sha256)
MENU_ART_FILES = ("Model", "Texture", "Icon")   # 0.3.15: the item fields whose file ships in this jar at Common/<field value>
MENU_ART_PNG = {"Texture": (128, 64), "Icon": (64, 64)}   # 0.3.15: the PNG sizes (RGBA8)


def menu_art_file(field):
    """0.3.15: the menu item's own art file for a field (Model / Texture / Icon), checked: = art/menu-emblem/manifest.json (sha256 +
    bytes, the icon_item_png way); a PNG = its size, RGBA8; the model = JSON with nodes"""
    import hashlib
    rel = "Common/" + MENU_ITEM_FIELDS[field]
    data = open(os.path.join(HERE, "..", *(MENU_ART_DIR + "/" + rel).split("/")), "rb").read()
    ent = [f for f in json.load(open(os.path.join(HERE, "..", *(MENU_ART_DIR + "/manifest.json").split("/")), encoding="utf8"))["files"]
           if f["path"] == rel]
    assert len(ent) == 1 and hashlib.sha256(data).hexdigest() == ent[0]["sha256"] and len(data) == ent[0]["bytes"], \
        "menu item %s: %s/%s is not the art manifest's file" % (field, MENU_ART_DIR, rel)
    if field in MENU_ART_PNG:
        assert data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR" and struct.unpack(">II", data[16:24]) == MENU_ART_PNG[field] \
            and data[24:26] == b"\x08\x06", "menu item %s: not a %d x %d RGBA8 PNG" % ((field,) + MENU_ART_PNG[field])
    else:
        _m = json.loads(data.decode("utf8"))
        assert isinstance(_m, dict) and isinstance(_m.get("nodes"), list) and _m["nodes"], "menu item %s: not a blockymodel" % field
    return data
MENU_ITEM_QUALITY = "Epic"
MENU_ITEM_DESC = ("Right-click to open the SkyWynn Menu: teleports, your island menu, bags, vault, the HUD editor, skills, the bazaar, "
                  "the auction house, the bank, reforging and identifying gear, your party and guild, your settings and a list of every mod with "
                  "its commands."
                  "\\n\\nIt stays with you: it can't be dropped, stored or sold. Lost it anyway? Type /menuitem (or /skymenu) to get a new one.")
PAGE_ID = "SkyyMenu"                          # OpenCustomUI page id used by the item
# 0.3.11: OWN ICON ITEMS. A tile's icon is an ITEM id (MenuPage.put: new ItemGridSlot(new ItemStack(icon, 1))), so our own icon art rides
# on an icon-only item this jar ships: id -> (the art file in the repo, its path under Common/ in the jar = the item's Icon, the
# art folder's manifest.json, the item's name, the vanilla item whose held look it borrows). Hidden from the creative library (Variant
# true, no Categories), no recipe, no interaction.
ICON_ITEMS = {
    # 0.3.37: the same id (saved shortcuts keep working), the approved void amulet (art/void-charms-icon A, Skyy 2026-10-17)
    "Skyy_Menu_Icon_AccessoryBag": ("art/void-charms-icon/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png",
                                    "Icons/ItemsGenerated/Skyy_Menu_Icon_VoidCharms.png", "art/void-charms-icon/manifest.json",
                                    "Void Charms", "Utility_Bag_Seed"),     # 0.3.36: the icon item's name (was Accessory Bag)
}
# 0.3.38: the Supplies tab (Storage > Supplies, SkyyCooking 0.1.11) wears the approved satchel (art/accessory-bag-icon, free since 0.3.37)
ICON_ITEMS["Skyy_Menu_Icon_Supplies"] = ("art/accessory-bag-icon/Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png",
                                         "Icons/ItemsGenerated/Skyy_Menu_Icon_Supplies.png", "art/accessory-bag-icon/manifest.json",
                                         "Supplies", "Farming_Collar")
ICON_BAG = "Skyy_Menu_Icon_AccessoryBag"      # 0.3.11: the Accessory Bag tile (Skyy 2026-10-08: "Yes, the bag icon looks good, commit it")
# 0.3.14: THE PETS TILE's icons. The 15 launch pet icons (art/pets, ART-RESUME Done #7, Skyy "Yes, the pets look good, commit them") as OUR
# icon-only items Skyy_Menu_Icon_Pet_<Pet>, shipped under our own file name (never SkyyPets' proposed SkyyPets_Pet_* ids / files). The tile
# shows the pet-slot pet's kind; a kind without art, no pet or an unreadable pet file = ICON_PETS (the vanilla dog collar).
PET_ART = ['Bear', 'Boar', 'Camel', 'Chicken', 'Goat', 'Hawk', 'Horse', 'Mouflon', 'Rabbit', 'Ram', 'Skrill', 'Turkey', 'Tusker', 'Warthog', 'Wolf']
ICON_SHA = {'Skyy_Menu_Icon_Pet_Bear': '1c8672db8a12ce3ce7c45ae3ed7140189f8b0075dc73fb61e33955d7562d8372', 'Skyy_Menu_Icon_Pet_Boar': '44dea38e4494de6919160e3be289f2a6fd03e51901f5874bd192d19d61a6e9a5', 'Skyy_Menu_Icon_Pet_Camel': 'fa3e60b797fa579dcee46584cced1c01ccf3b2c05569fb5df9e018c2605cd403', 'Skyy_Menu_Icon_Pet_Chicken': 'c4d25a4f886405b4d478c3b0c42158e985e6b24d4e2d4785e3b508e74c699a2b', 'Skyy_Menu_Icon_Pet_Goat': 'cd1c464260cf2c3510fd2e6b76b0b4355c8d9e13448c908d6b9590c4947b2ea9', 'Skyy_Menu_Icon_Pet_Hawk': '0df89dc0e8adab5b5163279fce85fc5724a5db9f7cddab274cdec4da4942a6cb', 'Skyy_Menu_Icon_Pet_Horse': '1b1d4ed2810a84651c6d663a619249c72b71e4f8e86f9cc68f78ad8c0702bd36', 'Skyy_Menu_Icon_Pet_Mouflon': 'c601caa048fde912d58fe229d93ffb39c0d74986f5f9b9fb27a2a5aa9cc159c6', 'Skyy_Menu_Icon_Pet_Rabbit': '5153bb048d1f4580598c0288492c184ac34ccb5a620249d71bd7ae61f9548134', 'Skyy_Menu_Icon_Pet_Ram': 'd4192a837f7d35874abaeb0e7a67b938fa0fe771fd4a02cd630a88b175787a2c', 'Skyy_Menu_Icon_Pet_Skrill': 'e2468d304a262ae786a84e4464a01a7b6f853c1101ae2fb584b7ccdc6865bd09', 'Skyy_Menu_Icon_Pet_Turkey': 'dad6ad5fbd523da22c2cf24be70316ec284f2860cefdb95243805b4ecdfaa702', 'Skyy_Menu_Icon_Pet_Tusker': '7095f6728065069ef0cef1757277294c8930b661f8760346eadb0019b4aaa742', 'Skyy_Menu_Icon_Pet_Warthog': '82f9c66928c04b910f36224bcfc7fec687c9555a9478fb657a91095f973ef577', 'Skyy_Menu_Icon_Pet_Wolf': '81449e84248d8f2ce1fba8c63475abfd34b11f7279c2e7a5cd689641c08d41c4'}     # art/pets/manifest.json has no sha256: pinned by tools/menu_0_3_14_patch.py from the committed files
for _p in PET_ART:
    ICON_ITEMS["Skyy_Menu_Icon_Pet_" + _p] = ("art/pets/Common/Icons/ItemsGenerated/SkyyPets_Pet_%s.png" % _p,
                                              "Icons/ItemsGenerated/SkyyMenu_Pet_%s.png" % _p, "art/pets/manifest.json", _p, "Farming_Collar")
# 0.3.16: THE OWN TILE ICONS (Skyy 2026-10-10 on art/menu-icons/sheet.png: "beautiful! i love it"): one icon-only item per main tile,
# Skyy_Menu_Icon_<Name>, picture = art/menu-icons/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_<Name>.png (shipped at the same path under
# Common/, checked against art/menu-icons/manifest.json sha256 + bytes); held look = the vanilla Farming_Collar (like the pet icons - these
# items are never held). AccessoryBag is 0.3.11's item (the art folder's copy is checked to be byte-identical to it).
MENU_ICON_DIR = "art/menu-icons"
MENU_ICONS = [('YourProfile', 'Your Profile'), ('Pets', 'Pets'), ('HoverTooltips', 'Hover Tooltips'), ('Teleport', 'Teleport'), ('PocketDimension', 'Pocket Dimension'), ('AccessoryBag', 'Void Charms'), ('HudEditor', 'HUD Editor'), ('Crafting', 'Crafting'), ('Skills', 'Skills'), ('Collections', 'Collections'), ('IslandMenu', 'Island Menu'), ('Bank', 'Bank'), ('Vault', 'Vault'), ('Bazaar', 'Bazaar'), ('AuctionHouse', 'Auction House'), ('Reforge', 'Reforge'), ('Identify', 'Identify'), ('Players', 'Players'), ('Party', 'Party'), ('Guild', 'Guild'), ('Settings', 'Settings'), ('Mods', 'Mods'), ('ServerSetup', 'Server Setup')]
for _nm, _tile in MENU_ICONS:
    if _nm != "AccessoryBag":
        ICON_ITEMS["Skyy_Menu_Icon_" + _nm] = ("%s/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % (MENU_ICON_DIR, _nm),
                                             "Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % _nm, MENU_ICON_DIR + "/manifest.json", _tile,
                                             "Farming_Collar")
MENU_ICON_OF = dict((_tile, "Skyy_Menu_Icon_" + _nm) for _nm, _tile in MENU_ICONS)   # 0.3.16: tile name -> its icon item
# 0.3.26: OUR OWN ICONS, WAVE 1 (Skyy 2026-10-15: "lets do our own icons in every menu too."; research/Menu-Icons-Plan.md): the 14 icons of
# art/menu-icons-2 (tools/art/make_menu_icons_2.py, original pixels; README there) as icon-only items Skyy_Menu_Icon_<Name>, shipped at
# the same Common/ path, checked against art/menu-icons-2/manifest.json (sha256 + bytes); held look = Farming_Collar like the tile icons.
# (name, item name, the vanilla id it replaces - the manifest's replaces_vanilla_id, checked at the end of the build)
MENU_ICON_DIR_2 = "art/menu-icons-2"
MENU_ICONS_2 = [("MyIsland", "My Island", "Soil_Grass"), ("Hub", "Hub", "Hub_Portal_Default"), ("Spawn", "Spawn", "Spawn_Portal"),
                ("Warp", "Warp", "Tool_Map"), ("WarpLocked", "Warp (locked)", "Tool_Map"), ("NoWarps", "No warps yet", "Tool_Map"),
                ("Shards", "Shards", "Portal_Device"), ("Back", "Go Back", "Weapon_Arrow_Iron"), ("Prev", "Previous Page", "Weapon_Arrow_Crude"),   # menu-pattern-ok: old icon names
                ("Next", "Next Page", "Weapon_Arrow_Iron"), ("Close", "Close", "Furniture_Flag_Small_Red"),
                ("Player", "Player", "Armor_Leather_Light_Head"), ("Accept", "Accept Request", "Ingredient_Crystal_Green"),
                ("Deny", "Deny Request", "Ingredient_Crystal_Red")]
for _nm, _lab, _was in MENU_ICONS_2:
    assert "Skyy_Menu_Icon_" + _nm not in ICON_ITEMS, "0.3.26: %s clashes with an icon item we already ship" % _nm
    ICON_ITEMS["Skyy_Menu_Icon_" + _nm] = ("%s/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % (MENU_ICON_DIR_2, _nm),
                                         "Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % _nm, MENU_ICON_DIR_2 + "/manifest.json", _lab,
                                         "Farming_Collar")
MENU_ICON_OF["Void Charms"] = "Skyy_Menu_Icon_AccessoryBag"   # 0.3.36: the renamed tile keeps the bag icon (art manifest: Accessory Bag)
# ---- 0.3.37: THE WARP ICONS (round tp37; art/warp-icons, tools/art/make_warp_icons.py, DRAFT until Skyy approves the sheet): one icon-only
# item per new theme (Skyy_Menu_Icon_Warp<Name>, checked against the manifest's sha256 + bytes like menu-icons-2); the theme table =
# the manifest's reused themes (warp = the signpost default, hub, spawn) + the new ones. SkyyEssentials 0.1.14 saves a theme per warp.
MENU_ICON_DIR_W = "art/warp-icons"
_WIM = json.load(open(os.path.join(HERE, "..", *(MENU_ICON_DIR_W + "/manifest.json").split("/")), encoding="utf8"))
MENU_ICONS_W = [(_i["name"], _i["label"], _i["theme"]) for _i in _WIM["icons"]]
for _nm, _lab, _th in MENU_ICONS_W:
    assert "Skyy_Menu_Icon_" + _nm not in ICON_ITEMS and _nm.startswith("Warp"), "0.3.37: %s clashes with an icon item we already ship" % _nm
    ICON_ITEMS["Skyy_Menu_Icon_" + _nm] = ("%s/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % (MENU_ICON_DIR_W, _nm),
                                         "Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % _nm, MENU_ICON_DIR_W + "/manifest.json",
                                         "%s (warp icon)" % _lab, "Farming_Collar")
WI_THEME = [_r["theme"] for _r in _WIM["reused"]] + [_t for _n, _l, _t in MENU_ICONS_W]
WI_ICON = [_r["id"] for _r in _WIM["reused"]] + ["Skyy_Menu_Icon_" + _n for _n, _l, _t in MENU_ICONS_W]
ICON_ZHOME = "Skyy_Menu_Icon_WarpHome"       # 0.3.37: a home (/sethome) tile
ICON_IHOME = "Skyy_Menu_Icon_MyIsland"       # 0.3.37: an island home tile (the My Island picture)
assert WI_THEME[0] == "warp" and WI_ICON[0] == "Skyy_Menu_Icon_Warp" and len(set(WI_THEME)) == len(WI_THEME) and all(_i in ICON_ITEMS for _i in WI_ICON) \
    and ICON_ZHOME in ICON_ITEMS and ICON_IHOME in ICON_ITEMS, "0.3.37: every warp theme has a shipped icon item"
MENU_ICON_OF["Shards"] = "Skyy_Menu_Icon_Shards"    # 0.3.26: the Shards tile wears its own icon too (was the vanilla Portal_Device)
# ---- 0.3.30: OUR OWN ICONS, WAVE 3 - no icon item used by two pages (Skyy 2026-10-16: "storage and pocket dimension look the same",
# "we have world and teleport that look the same", "class tree and profile have the same icon."). Painted HERE, at build time, with the
# sheet-1 painter (tools/art/make_menu_icons.py: palette ramps, top-left light, bevels, 1 px tinted outline, hard alpha) on its 64 px grid,
# from the approved motifs of art/hub-tab-icons (tools/art/make_hub_tab_icons.py builders, imported, not edited; drawn for a 72 px square,
# so every sample point is scaled 72 / 64 - each pixel is still painted and ramp-snapped at 64 px, then centred). Original pixels only.
# (name, item name, motif hub, motif tab)
MENU_ICONS_3 = [("HubCharacter", "Character", "hubrow", "character"), ("HubStorage", "Storage", "hubrow", "storage"),
                ("HubMarket", "Market", "hubrow", "market"), ("HubSmithing", "Smithing", "hubrow", "smithing"),
                ("HubWorld", "World", "hubrow", "world"), ("HubSocial", "Social", "hubrow", "social"),
                ("HubSettings", "Settings", "settings", "settings"),   # the sliders: the Settings tile keeps its two cogs
                ("Trees", "Trees", "character", "trees"), ("Class", "Class", "character", "class"),
                ("Profiles", "Profiles", "character", "profiles"), ("Requip", "Requip", "storage", "requip"),
                ("Gear", "Gear", "smithing", "gear"), ("Upgrade", "Upgrade", "smithing", "upgrade"),
                ("Explore", "Explore", "world", "explore"), ("Quests", "Quests", "world", "quests"),
                ("Merchants", "Merchants", "market", "merchants"), ("Layout", "Edit shortcuts", "settings", "layout")]


def _paint_wave3():
    """{item id: 64 x 64 RGBA8 PNG bytes} - deterministic (checked: one icon painted twice is byte-identical)"""
    _art_dir = os.path.join(HERE, "..", "tools", "art")
    if _art_dir not in sys.path:
        sys.path.insert(0, _art_dir)
    import make_hub_tab_icons as _HT
    _M, _P = _HT.M, _HT.P
    _k = 72.0 / 64.0

    class _SShape(object):
        def __init__(self, sh):
            self.sh = sh
            self.bb = tuple(v / _k for v in sh.bb)

        def __call__(self, x, y):
            return self.sh(x * _k, y * _k)

    class _SLayer(object):
        def __init__(self, ly):
            self.ly, self.shape = ly, _SShape(ly.shape)
            self.pal, self.cast, self.line, self.rim = ly.pal, ly.cast, ly.line, ly.rim

        def t(self, x, y):
            return self.ly.t(x * _k, y * _k)

    _fn = dict(((h, t), f) for h, t, _l, f, _w in _HT.ALL)

    def _one(h, t):
        ic = _fn[(h, t)]()
        ic.layers = [_SLayer(l) for l in ic.layers]
        ic.pix = [(int(round(x / _k)), int(round(y / _k)), c) for (x, y, c) in ic.pix]
        _old = _M.N
        _M.N = 64
        try:
            img = ic.render()
        finally:
            _M.N = _old
        pts = [(x, y) for y in range(64) for x in range(64) if img[y][x][3]]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        dx, dy = int(round((63 - max(xs) - min(xs)) / 2.0)), int(round((63 - max(ys) - min(ys)) / 2.0))
        out = _P.new(64, 64)
        for x, y in pts:
            if 0 <= x + dx < 64 and 0 <= y + dy < 64:
                out[y + dy][x + dx] = list(img[y][x])
        return _M.png_bytes(out)
    out = {}
    for _nm, _lab, _h, _t in MENU_ICONS_3:
        out["Skyy_Menu_Icon_" + _nm] = _one(_h, _t)
    assert _one(MENU_ICONS_3[0][2], MENU_ICONS_3[0][3]) == out["Skyy_Menu_Icon_" + MENU_ICONS_3[0][0]], "0.3.30: the wave-3 painter is deterministic"
    return out


GEN_ICON_PNG = _paint_wave3()
for _nm, _lab, _h, _t in MENU_ICONS_3:
    assert "Skyy_Menu_Icon_" + _nm not in ICON_ITEMS, "0.3.30: %s clashes with an icon item we already ship" % _nm
    ICON_ITEMS["Skyy_Menu_Icon_" + _nm] = ("gen:%s_%s" % (_h, _t), "Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % _nm, None, _lab, "Farming_Collar")
assert len(set(GEN_ICON_PNG.values())) == len(GEN_ICON_PNG), "0.3.30: every wave-3 icon is its own picture"
print("0.3.30 wave-3 icons painted at build time:", ", ".join("%s (%d bytes)" % (n, len(GEN_ICON_PNG["Skyy_Menu_Icon_" + n])) for n, _l, _h, _t in MENU_ICONS_3))
ICON_PETS = "Skyy_Menu_Icon_Pets"             # 0.3.14: the Pets tile without a pet icon (0.3.16: our own collar icon, was the vanilla Farming_Collar)


def icon_item_png(iid):
    """0.3.11: the icon item's PNG, checked: = its art manifest (sha256 + bytes), a 64 x 64 RGBA8 PNG
    0.3.14: the manifest entry is the art file's path inside the manifest's folder (the bag: = Common/<rel>, as before; the pet icons
    ship under our own name); a manifest entry without sha256 (art/pets) is checked against ICON_SHA"""
    import hashlib, struct
    if iid in GEN_ICON_PNG:    # 0.3.30: wave 3 is painted by this build (no art file / manifest): checked for the same PNG shape
        data = GEN_ICON_PNG[iid]
        assert data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR" and struct.unpack(">II", data[16:24]) == (64, 64) \
            and data[24:26] == b"\x08\x06", "icon item %s: not a 64 x 64 RGBA8 PNG" % iid
        return data
    art, rel, man, _nm, _look = ICON_ITEMS[iid]
    data = open(os.path.join(HERE, "..", *art.split("/")), "rb").read()
    _mdir = man.rsplit("/", 1)[0] + "/"
    assert art.startswith(_mdir), "icon item %s: %s is not in its manifest's folder" % (iid, art)
    ent = [f for f in json.load(open(os.path.join(HERE, "..", *man.split("/")), encoding="utf8"))["files"] if f["path"] == art[len(_mdir):]]
    _sha = (ent[0].get("sha256") or ICON_SHA.get(iid)) if len(ent) == 1 else None
    assert len(ent) == 1 and _sha and hashlib.sha256(data).hexdigest() == _sha and len(data) == ent[0]["bytes"], \
        "icon item %s: %s is not the art manifest's file" % (iid, art)
    assert data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR" and struct.unpack(">II", data[16:24]) == (64, 64) \
        and data[24:26] == b"\x08\x06", "icon item %s: not a 64 x 64 RGBA8 PNG" % iid
    return data

# 0.3.26: our own art/menu-icons-2 icons (were Weapon_Arrow_Iron / Weapon_Arrow_Crude / Weapon_Arrow_Iron / Furniture_Flag_Small_Red /
# Tool_Map / Armor_Leather_Light_Head); ICON_WARP_LOCKED + ICON_NO_WARPS are new (both were ICON_WARP)
ICON_BACK   = "Skyy_Menu_Icon_Back"           # a steel return arrow
ICON_PREV   = "Skyy_Menu_Icon_Prev"           # a steel double chevron, left
ICON_NEXT   = "Skyy_Menu_Icon_Next"           # the same, right
ICON_CLOSE  = "Skyy_Menu_Icon_Close"          # a riveted steel plate with a red X
ICON_WARP   = "Skyy_Menu_Icon_Warp"           # a wooden signpost (every unlocked warp)
ICON_WARP_LOCKED = "Skyy_Menu_Icon_WarpLocked"   # 0.3.26: the dim signpost + a padlock (a warp you have not unlocked)
ICON_NO_WARPS    = "Skyy_Menu_Icon_NoWarps"      # 0.3.26: a bare signpost ("No warps yet")
ICON_PLAYER = "Skyy_Menu_Icon_Player"         # a blocky player head
FILLER_ICON = None                            # None = empty grid slots; e.g. "Editor_Empty" for a Hypixel glass-pane look

USE_MARKUP  = True                            # tooltip footer colors (<color is=...>); set False if raw tags show in game
FOOT_COLOR  = "#ffff55"
DIM_COLOR   = "#ff5555"

# (view, title, intro lines) - the intro fills the info box until something is clicked
VIEWS = [
    ("main",    "SkyWynn Menu",   ["Everything the server adds, in one place. Hover an item to read about it and click it to use it.",
                                   "Lost your menu item? Type /skymenu to get a new one."]),
    ("tp",      "Teleport",       ["Your island, your island homes, your homes, the hub, the server spawn and every warp.",
                                   "Admins add warps (and pick their icons) on /warpadmin."]),
    ("players", "Players Online", ["Click a player to send a teleport request, visit their island or invite them to your party.",
                                   "Teleport requests you receive can be accepted or denied at the bottom."]),
    ("player",  "Player",         ["What do you want to do with this player?"]),
    ("mods",    "Mods",           ["Every SkyWynn mod, what it does and all of its commands.",
                                   "Click a mod to show its commands here - hovering shows the same text."]),
]

# (view, slot, icon item id, name, text lines, tooltip footer or None, action)
ENTRIES = [
    # ---- main menu. 0.3.16: LAYOUT D (Skyy 2026-10-10 "go with D"; MAIN_D below is the map, checked at build): Teleport on slot 13 (the
    # slot under the mouse when the menu opens), the most used tiles in a plus around it, the social bar down the LEFT edge, the admin /
    # options bar down the RIGHT edge; every tile wears its own art/menu-icons icon (MENU_ICON_OF). Before 0.3.16: the 0.1.3 rows.
    # 0.3.10: the tile opens the Stats page (StatsPage, also /stats); its hover text is MenuPage.profileBody (short lines)
    ("main", 33, "Skyy_Menu_Icon_YourProfile", "Your Profile", ["All your stats: health, mana, strength, crit, fortune, skills and more."],
        "Click to open your Stats page", "profile"),
    # 0.3.14: Pets right of Your Profile (Skyy 2026-10-10 "add pets to the top bar of the menu by profile"). Drawn ONLY while SkyyPets is
    # loaded (PetTile.installed); name / text / icon come from the active PROFILE's pet record (PetTile) - this text is the fallback.
    ("main", 3, ICON_PETS, "Pets", ["Your pets on this profile: the pet slot, the summon slot and every pet you own.",
                                     "Pets stay on this profile - every profile has its own.", "Command: /pets (or /pet)"],
        "Click to open!", "cmdc:pets"),
    ("main", 8, "Skyy_Menu_Icon_HoverTooltips", "Hover Tooltips",
        ["Switch the pop-up text of this menu on or off (saved for you).",
         "Off: nothing pops up when you hover an item. Click an item to use it",
         "and read what it does in this box.",
         "The same switch is in Settings (/settings, General tab)."], "Click to switch", "tips"),
    ("main", 13, "Skyy_Menu_Icon_Teleport", "Teleport", ["Travel to your island, the hub, the server spawn and every warp that is set."], "Click to open!", "view:tp"),
    ("main", 32, "Skyy_Menu_Icon_PocketDimension", "Pocket Dimension",
        ["Everything your Magic Bags swept up lives here. Pick items up or deposit them.",
         "Carry a bag to use its tab. A bag you lack shows how to craft it.",
         "Stack refill: Hotbar only, Full inventory or Off - pick it on that page.",
         "Command: /sacks (or /pd, /bags)"], "Click to open!", "cmdc:sacks"),
    ("main", 5, "Skyy_Menu_Icon_AccessoryBag", "Void Charms",                    # 0.3.11: our own icon; 0.3.36: Void Charms (/charms)
        ["Equip bench accessories and booster accessories - they work while they sit in Void Charms.", "Command: /charms (or /charm, /ch)"],
        "Click to open!", "cmdc:charms"),
    ("main", 26, "Skyy_Menu_Icon_HudEditor", "HUD Editor",
        ["Move, resize and switch every widget of your on-screen HUD.", "Save layouts as profiles or share them as a code.",
         "Command: /skyyhud (or /shud)"], "Click to open!", "cmdc:skyyhud"),
    ("main", 14, "Skyy_Menu_Icon_Crafting", "Crafting",
        ["Craft from your inventory and your Magic Bags.", "Bench accessories in your Void Charms unlock that bench's recipes.",
         "Vanilla benches and inventory crafting use the bags you carry too.",
         "Command: /craft"], "Click to open!", "cmdc:craft"),
    ("main", 4, "Skyy_Menu_Icon_Skills", "Skills",
        ["Your skill levels and XP: gathering, your class weapon skill (Archery, Swordsmanship, Sorcery, Fury, Divinity, Assassination, "
         "Zen or Battlemagic) and more. "   # 0.3.30: + the Spellblade's Battlemagic
         "Every level up pays coins.", "Command: /skills"],
        "Click to open!", "cmdc:skills"),
    ("main", 40, "Skyy_Menu_Icon_Collections", "Collections",
        ["Everything you have gathered, your milestones and the recipes they unlock.", "Command: /collections"], "Click to open!", "cmdc:collections"),
    ("main", 12, "Skyy_Menu_Icon_IslandMenu", "Island Menu",
        ["Your island in one page: members, visitors and island settings.", "Command: /island menu (or /is menu)",
         "Shards: right-click one on your island to open its menu."],    # 0.3.27
        "Click to open!", "cmdc:island menu"),
    ("main", 21, "Skyy_Menu_Icon_Bank", "Bank",
        ["Deposit coins to earn interest. Bank coins are safe when you die.", "Deposit all, withdraw all or type any amount.",
         "Command: /bank"], "Click to open!", "cmdc:bank"),
    ("main", 29, "Skyy_Menu_Icon_Vault", "Vault",
        ["Item storage shared by ALL of your profiles - move items from one profile to another.", "Command: /vault"],
        "Click to open!", "cmdc:vault"),
    ("main", 22, "Skyy_Menu_Icon_Bazaar", "Bazaar",
        ["Instantly buy and sell resources. Prices move as players trade.", "Command: /bazaar (or /bz)"], "Click to open!", "cmdc:bazaar"),
    # 0.2: the Auction House (SkyyAuctions 0.1, /ah) sits next to the Bazaar; Reforge moved one slot right
    ("main", 23, "Skyy_Menu_Icon_AuctionHouse", "Auction House",
        ["Buy items other players listed and sell your own for a fixed price (Buy It Now).",
         "Claim the coins and items you are owed on the Manage page.",
         "Command: /ah (or /auction, /auctionhouse)"], "Click to open!", "cmdc:ah"),
    # 0.3.3: SkyyGear 0.1 owns /reforge (the same command SkyyRolls had): weapons and armor, tools are refused (SkyyGear spec 5.4)
    ("main", 30, "Skyy_Menu_Icon_Reforge", "Reforge",
        ["Put in a weapon or armor piece and pay coins to reroll its modifiers.", "Command: /reforge"], "Click to open!", "cmdc:reforge"),
    # 0.3.3: Identify right of Reforge (SkyyGear 0.1 /identify, spec 7.3.2); greyed "(not installed)" while no /identify command is loaded
    ("main", 31, "Skyy_Menu_Icon_Identify", "Identify",
        ["Reveal the modifiers of unidentified weapons and armor from mobs and loot chests. Costs coins by rarity and level.",
         "Command: /identify"], "Click to open!", "cmdc:identify"),
    ("main", 0, "Skyy_Menu_Icon_Players", "Players",
        ["Everyone who is online: send teleport requests, visit islands, invite to your party."], "Click to open!", "view:players"),
    ("main", 9, "Skyy_Menu_Icon_Party", "Party",
        ["Your party page: invite players, answer invites, see your party or leave it.", "Party chat: /pc <message>",
         "Command: /party (or /p)"], "Click to open!", "cmdc:party"),
    ("main", 18, "Skyy_Menu_Icon_Guild", "Guild",
        ["Your guild page: members and ranks, the guild bank and guild XP.", "Not in a guild? Create one or accept an invite there.",
         "Guild chat: /gc <message>", "Command: /guild"], "Click to open!", "cmdc:guild"),
    ("main", 35, "Skyy_Menu_Icon_Mods", "Mods",
        ["Every SkyWynn mod on the server, what it does and all of its commands."], "Click to open!", "view:mods"),
    # 0.3: Server Setup right of Mods (research/Server-Setup-Spec.md 2.2) - drawn ONLY for players with skyymenu.modconfig
    ("main", 44, "Skyy_Menu_Icon_ServerSetup", "Server Setup",
        ["Change every Skyy mod's settings in game - only admins see this.",
         "Every change is saved to the mod's own file, logged and can be undone.",
         "Command: /modconfig (or /serversetup)"], "Click to open!", "admin"),
    # 0.3.3: Settings immediately LEFT of Mods (LOCKED 2026-09-25, research/Settings-Spec.md 4.1). 0.2 - 0.3.2 had it at slot 51 next to Close
    ("main", 17, "Skyy_Menu_Icon_Settings", "Settings",
        ["Turn chat messages on or off - one switch per message, for every mod.",
         "Your settings are the same on every profile.", "Command: /settings (or /skysettings)"], "Click to open!", "settings"),
    # 0.3.16: THE WARDROBE TILE (left bar, row 4; Skyy's layout D "Players, Party, Guild + future Quests, Wardrobe") - drawn ONLY while
    # SkyyWardrobe publishes the bridge Function wardrobe:fn:open (TILE_RULES "need"); the click calls apply(UUID player) on the world
    # thread, which opens SkyyWardrobe's page (TRUE = opened). Stand-in icon = the vanilla Village Wardrobe until its own art exists.
    ("main", 36, "Skyy_Menu_Icon_Requip", "Wardrobe",     # 0.3.30: our own Requip icon (was the vanilla Village Wardrobe)
        ["Your saved loadouts - one click swaps between them.", "Command: /wardrobe"],
        "Click to open!", "bridge:wardrobe:fn:open"),
    # 0.3.27: the 0.3.22 SHARDS TILE (slot 11) is gone - Skyy 2026-10-15: each shard's menu opens only from its portal on your island
    # ---- Teleport (warps are added automatically in rows 2-4, see WARP_SLOTS)
    ("tp", 11, "Skyy_Menu_Icon_MyIsland", "My Island",    # 0.3.26: our own icons on the Teleport page (were Soil_Grass /
        ["Teleport to your own island. It is created the first time you go.", "Command: /island (or /is)"], "Click to teleport!", "cmdc:island"),
    ("tp", 13, "Skyy_Menu_Icon_Hub", "Hub",               # Hub_Portal_Default / Spawn_Portal)
        ["Go back to the hub from anywhere, including your island.", "Command: /hub (or /lobby)"], "Click to teleport!", "cmdc:hub"),
    ("tp", 15, "Skyy_Menu_Icon_Spawn", "Spawn", ["Teleport to the spawn point of the main world."], "Click to teleport!", "spawn"),
    # ---- Players (online players are added automatically, see PLAYER_SLOTS)
    # cmdc (close first): accepting a /tpahere request teleports YOU (SkyyEssentials accept(): mover = r.here ? r.to : r.from)
    ("players", 47, "Skyy_Menu_Icon_Accept", "Accept Teleport Request",    # 0.3.26: our own (was Ingredient_Crystal_Green)
        ["Accept the newest teleport request someone sent you.", "Command: /tpaccept"], "Click to accept", "cmdc:tpaccept"),
    ("players", 51, "Skyy_Menu_Icon_Deny", "Deny Teleport Request",        # 0.3.26: our own (was Ingredient_Crystal_Red)
        ["Refuse the newest teleport request someone sent you.", "Command: /tpdeny"], "Click to deny", "cmd:tpdeny"),
]

# Entries whose command is a SUBCOMMAND of another mod's command (0.1.3): (command, subcommand, what the server needs). The entry is
# greyed "(update needed)" while that command exists WITHOUT the subcommand (checked live with AbstractCommand.getSubCommand).
NEEDS_SUB = [("island", "menu", "SkyyIslands 0.5")]

# Player actions whose WORDING depends on the installed version (review 2026-09-24): (player-action slot, NEEDS_SUB command line, old name,
# old lines, old footer). While MenuUtil.needOf(line) says the server's mod is older, the old text is shown; the command is the same.
# SkyyIslands 0.4.5's /island invite only gives build rights; 0.5 makes the invitee a member of your island.
PA_LEGACY = [
    (33, "island menu", "Give Island Build Rights", ["Let %P build on YOUR island. Only do this for friends.", "Command: /island invite %P"],
        "Click to give build rights"),
]

# Things you can do with a selected player. %P = their name (letters, digits, _ only). (slot, icon, name, lines, footer, command, close menu first)
PLAYER_ACTIONS = [
    # 0.3.26: the teleport actions reuse our Hub / Spawn / My Island icons. 0.3.30: they moved one slot left (28 - 31) so Invite to Guild
    # (RESUME queue, Menu 0.3.30) sits right of Invite to Party; the island actions keep 33 / 34 (PA_LEGACY names 33)
    (28, "Skyy_Menu_Icon_Hub", "Send Teleport Request", ["Ask %P if you may teleport to them. They have 60 seconds to accept.", "Command: /tpa %P"],
        "Click to send", "tpa %P", False),
    (29, "Skyy_Menu_Icon_Spawn", "Invite Them Here", ["Ask %P to teleport to you.", "Command: /tpahere %P"], "Click to send", "tpahere %P", False),
    (30, "Skyy_Menu_Icon_MyIsland", "Visit Their Island", ["Teleport to the island of %P and look around (you can only build with their build rights).",
        "Command: /island visit %P"], "Click to visit", "island visit %P", True),
    (31, "Deco_Scroll", "Invite to Party", ["Invite %P to your party.", "Command: /party invite %P"], "Click to invite", "party invite %P", False),
    (32, "Furniture_Human_Ruins_Banner", "Invite to Guild", ["Invite %P to your guild (guild leaders and officers who may invite).",
        "They answer it on their Guild page.", "Command: /guild invite %P"], "Click to invite", "guild invite %P", False),
    (33, "Tool_Hammer_Iron", "Invite to Your Island", ["Invite %P to join your island as a co-op member. Only do this for friends.",
        "They join with /island accept.", "Command: /island invite %P"], "Click to invite", "island invite %P", False),
    (34, "Tool_Pickaxe_Iron", "Let Them Build", ["Let %P build on YOUR island without making them a member.",
        "Undo with /island untrust.", "Command: /island trust %P"], "Click to trust", "island trust %P", False),
]

WARP_SLOTS   = list(range(19, 26)) + list(range(28, 35)) + list(range(37, 44))                       # 21 warps per page
PLAYER_SLOTS = list(range(10, 17)) + list(range(19, 26)) + list(range(28, 35)) + list(range(37, 44))  # 28 players per page
MOD_SLOTS    = list(range(10, 17)) + list(range(19, 26)) + list(range(28, 35)) + list(range(37, 44))  # 28 mods per page (0.3.1: 22 mods)
NO_WARPS_SLOT, NO_PLAYERS_SLOT, PLAYER_HEAD_SLOT = 31, 22, 13

# The Mods submenu: one item per mod (icon = the item that represents it, tooltip = what it does + every command).
# "check" = a command of that mod; the mod counts as installed when its plugin or that command is loaded. The live version is
# read from the loaded plugin's manifest; "version" is only shown when the mod is not installed.
# Commands use the short positional forms (SkyyIslands 0.4.3, SkyyHud 0.3.6, SkyyBank 0.1.1, ... added usage variants / subcommands).
# ---- 0.3.5: THE ONE VERSION TABLE of the Mods list = tools/deploy_set.py SET (SET order; SkyyMenu's own entry is VERSION). Every MODS
# entry below reads its "version" from here (asserted). To bump: the next tools/menu_<ver>_patch.py rewrites this one block (the table
# line down to its closing brace - tools/menu_0_3_5_patch.py bump_table), regenerate, rebuild; the build's live-set check names every
# difference and prints this table for the live SET.
MODS_VERSIONS = {   # 0.3.39: = tools/deploy_set.py SET of 2026-10-18
    "SkyyHud": "0.3.32", "SkyySacks": "0.8.22", "SkyyCoins": "0.1.9", "SkyyCollections": "0.2.26", "SkyyParty": "0.1.10",
    "SkyyBank": "0.1.16", "SkyyIslands": "0.5.19", "SkyyBazaar": "0.1.21", "SkyyGear": "0.3.24", "SkyySkills": "0.4.51",
    "SkyyAccessories": "0.5.26", "SkyyClasses": "0.1.38", "SkyyEssentials": "0.1.15", "SkyyProfiles": "0.1.17", "SkyyCooking": "0.1.11",
    "SkyyTrees": "0.3.23", "SkyyExploration": "0.2.14", "SkyyGuilds": "0.1.11", "SkyyVault": "0.1.9", "SkyyAuctions": "0.1.13",
    "SkyyRanks": "0.1.2", "SkyyUiProbe": "0.6", "SkyyMobs": "0.1.10", "SkyyWorldGen": "0.7.4", "SkyyArmory": "0.1.34",
}
MODS = [
    {"mod": "SkyyMenu", "version": VERSION, "icon": MENU_ITEM_ID, "check": "skymenu",     # 0.3.15: our own emblem (was Ingredient_Voidheart)
     "config": "Skyy_SkyyMenu/config.properties,Skyy_SkyyMenu/settings-defaults.properties", "reload": "", "note": "Set up in game - Server Setup, Menu.",
     "setup": ("0.3", "Menu", "the menu item, the Mods tile, player settings defaults"),
     # 0.3.10: the Stats page (/stats)
     "desc": "The all-in-one SkyWynn menu: teleports, your island menu, Pocket Dimension, Vault, Void Charms, the HUD editor, crafting, skills, collections, the bazaar, the auction house, the bank, reforging and identifying gear, players, your party and guild, your stats, your settings, this list of mods and Server Setup for admins.",
     "commands": ["/skymenu%ALIASES% - open the menu or get the item back",   # 0.3.32: shorter (+ /menuitem fits 80)
                  "Double-tap crouch while standing - open the menu (switch: /settings)",
                  "/stats (or /profilestats) - all your stats on one page",
                  "/character (/char), /crafting, /travel, /social, /storage, /market - open a hub",   # 0.3.28; 0.3.31: /crafting
                  "/settings (or /skysettings) - turn chat messages on or off",
                  "/modconfig (or /serversetup) - (admin) change every mod's settings in game",
                  "/modconfig admin - (admin) the Admin page: buttons for the admin commands",   # 0.3.23
                  "/soundtest - (admin) hear any vanilla sound by id or number (list)"]},   # 0.3.24
    {"mod": "SkyyProfiles", "version": MODS_VERSIONS["SkyyProfiles"], "icon": "Deco_Book_Pile_Large", "check": "profiles",
     "config": "Skyy_SkyyProfiles/config.properties", "reload": "profileadmin reload", "note": "",
     # 0.3.4: SkyyProfiles 0.1.5 - profile delete (confirm, then a 6-hour undo window by default), restore, the admin archive;
     # /profileadmin reload joins the config line (the info box shows 8 Commands lines at most)
     "setup": ("0.1.1", "Profiles", "profile slots, switching, inventory, delete undo hours"),
     "admin": ["/profileadmin config | set <setting> <value> | reload - (admin)",
               "/profileadmin archive list <player> - (admin) deleted and archived profiles",
               "/profileadmin archive restore <player> <profile> - (admin) bring one back"],
     "desc": "SkyBlock-style profiles: each profile is its own save with its own class (Archer, Warrior, Mage, Berserker, Priest, Assassin, Monk or Spellblade), island, inventory, coins, bank, bags, skills and collections. A new profile starts with its class kit. A deleted profile can be restored for a few hours (6 by default).",
     "commands": ["/profiles (or /profile) - open your profiles", "/profiles create (or new) - a new profile: pick its class, get its kit",
                  "/profiles switch <number or name> - switch to another profile", "/profiles list - your profiles in chat",
                  "/profiles delete <number or name> - delete a profile (type it again to confirm)",
                  "/profiles restore <number or name> - bring back a profile you deleted",
                  "/profileadmin info <player> - (admin) a player's profiles",
                  "/profileadmin setclass <player> <n> <class> - (admin) fix a class"]},
    # 0.3.3: SkyyIslands 0.5.3 (round 9): island admins may invite co-op members, visitor limit 10, beds stay member-only
    {"mod": "SkyyIslands", "version": MODS_VERSIONS["SkyyIslands"], "icon": "Soil_Grass", "check": "island",
     "config": "Skyy_SkyyIslands/config.properties", "reload": "island reload", "note": "",
     "setup": ("0.5.2", "Islands", "island defaults, visitors, co-op, limits, starter kit, hub"),
     "admin": ["/modconfig islands - (admin) island defaults, starter kit from your hotbar",
               "/island reload - (admin) re-read config.properties and every island file",
               "/sethub - (admin) set the hub where you stand (also in Server Setup)"],
     "desc": "Your own private island in the sky: teleport home any time, invite friends as co-op members and choose who may visit or build in the island menu.",
     "commands": ["/island (or /is) - go to your island", "/island menu - members, visitors and island settings",
                  "/island visit <player> - visit a player's island",
                  "/island invite <player> - (owner or island admin) invite a co-op member",
                  "/island trust <player> - give a player build rights only",
                  "/island leave | kick <player> - leave a co-op | (owner) remove one",
                  "/island reset - (owner) rebuild your island from scratch", "/hub (or /lobby) - back to the hub"],
     "old": {"need": "island menu",
             "desc": "Your own private island in the sky: teleport home any time (built with a starter chest the first time), give friends build rights or let anyone visit.",
             "commands": ["/island (or /is) - go to your island", "/island visit <player> - visit a player's island",
                          "/island invite <player> - give a player build rights", "/island info - about your island",
                          "/hub (or /lobby) - back to the hub", "/sethub - (admin) set the hub point"]}},
    # 0.3.3: SkyySacks 0.7.7 (round 8): Magic Bags by rarity + the Mythic Omni Bag, bag recipes unlocked by collections
    {"mod": "SkyySacks", "version": MODS_VERSIONS["SkyySacks"], "icon": "Tool_Feedbag", "check": "sacks",
     "config": "Skyy_SkyySacks/config.properties", "reload": "", "note": "It is read again by itself within about 10 seconds.",
     # 0.3.5: SkyySacks 0.7.11 - 0.7.12 - the stack refill (a per-player choice on the bag page: Hotbar only = default / Full inventory /
     # Off; Server Setup bags.refill + bags.refillDefault), bags of one type ADD UP (the Omni adds to every type), vanilla benches and
     # inventory (pocket) crafting use the bags you carry (bags.pocketCraft, on); Charcoal goes in the Smithing bag (0.7.10)
     "setup": ("0.7.6", "Bags and Crafting", "bag caps, free recipes, stack refill, benches, Furnace"),
     "desc": "Magic Bags in four rarities (Normal, Unique, Rare, Legendary) send what you gather of their type - Mining, Foraging, Farming, Combat or Smithing - into your Pocket Dimension, and the Mythic Omni Bag does it for every type. Bags of one type add up. Collections unlock the bag recipes. Benches, inventory crafting and /craft use the bags you carry.",
     "commands": ["/sacks (or /pd, /bags) - your Pocket Dimension, missing bags show recipes",
                  "Stack refill (on the /sacks page): Hotbar only, Full inventory or Off",
                  "/craft (or /recipes) - craft from your inventory and bags", "/craft <words> - open crafting with a search"]},
    {"mod": "SkyyAccessories", "version": MODS_VERSIONS["SkyyAccessories"], "icon": "Utility_Bag_Seed", "check": "charms",
     "config": "Skyy_SkyyAccessories/config.properties", "reload": "charms reload", "note": "",   # 0.3.36: /charms (SkyyAccessories 0.5.22)
     # 0.3.4: SkyyAccessories 0.5 / 0.5.1 - booster accessories (one table, ten lines), 18 bag slots to start, /accessories lines,
     # admin give / givetier (requirePermission skyyaccessories.admin)
     # 0.3.6: SkyyAccessories 0.5.3 - the Night Vision accessory (Rare, admin give only; its Server Setup rows under Accessories)
     # 0.3.7: SkyyAccessories 0.5.4 - the Lantern line REPLACES Night Vision (retired: it does nothing, cannot be equipped); Server
     # Setup -> Accessories -> Lantern (on / off, glow and reach per rarity, the highest helper, shared reach)
     "setup": ("0.4.4", "Void Charms", "charm slots, booster lines, notices, Lantern"),   # 0.3.38: = SkyyAccessories 0.5.24's TITLE
     "admin": ["/charms reload - (admin) re-read config.properties after hand edits",
               "/charms give <player> <item> [amount] - (admin) give an accessory",
               "/charms givetier <player> <line> <rarity> [amount] - (admin)"],
     # 0.3.5: SkyyAccessories 0.5.2 - every accessory and bag recipe in the Workbench tab "Accessories & Bags" (no & in tooltip text)
     "desc": "Void Charms: 18 slots to start for bench accessories (each unlocks its bench tab in /craft, the Campfire one cooks on the go) and booster accessories - Health, Stamina, Mana, Regeneration, Speed, the Lantern (you glow like a torch) and more - that work while they sit in Void Charms. Only the best rarity of each line counts. Craft them in the Craft tab of Void Charms.",
     "commands": ["/charms (or /charm, /ch) - open Void Charms",
                  "/charms lines - every accessory line, its rarities and numbers",
                  "/charms power [name] - your Accessory Power, or pick a Power"]},
    {"mod": "SkyyHud", "version": MODS_VERSIONS["SkyyHud"], "icon": "Deco_Map", "check": "skyyhud",
     "config": "Skyy_SkyyHud/config.properties", "reload": "", "note": "Hand edits are read at the next server start.",
     "setup": ("0.3.10", "HUD", "the HUD layout new players start with"),
     "admin": ["/skyyhud default - (admin) which layout new players start with",
               "/skyyhud default use | clear - (admin) set it to your layout | the built-in one"],
     # 0.3.5: SkyyHud 0.3.11 - the Skills widget (Overall Level + any skills, each line on / off in the widget's Settings; Overall + class
     # skill by default) - no new command, player switch or Server Setup title
     # 0.3.6: SkyyHud 0.3.12 - the Combat Indicator widget (red In combat + countdown + a shrinking bar; hidden out of combat by default)
     "desc": "A customizable on-screen HUD: coordinates, zone, clocks, day counter, session timer, players online, coins, party, guild, skills (your Overall Level and the skills you pick in its Settings) and a combat indicator (red with a countdown while you are in combat). Move, resize and colour every widget, save profiles or share your layout as a code.",
     "commands": ["/skyyhud (or /shud) - open the HUD editor", "/skyyhud export - print your layout as a code",
                  "/skyyhud import <code> - load a layout code", "/skyyhud reset - back to the server's default layout",
                  "/skyyhud profile save|load|delete <name> - named layouts", "/skyyhud profile list - your saved layouts"]},
    # 0.3.3: SkyySkills 0.4.6 (round 8, pinned): base Mana, the Overall Level (skills.overallUp), crossbow extras (skills.xbow* switches)
    {"mod": "SkyySkills", "version": MODS_VERSIONS["SkyySkills"], "icon": "Weapon_Sword_Iron", "check": "skills",
     "config": "Skyy_SkyySkills/xp.properties", "reload": "skills reload", "note": "",
     # 0.3.5: SkyySkills 0.4.12 - class skills level on their OWN XP table (levels.class rows), in-combat Mana regen (default 50%,
     # row mana.regen.inCombat), the admin /skills mana (requirePermission skyyskills.admin); 0.4.11 Priest heal XP - no new player switch
     # 0.3.8: SkyySkills 0.4.16 - Server Setup -> Skills -> Levels -> 'Own XP list per skill' (levels.skill; Mining by default)
     "setup": ("0.4.3", "Skills", "own XP list per skill, XP rates, perks, Overall Level, Mana"),
     # 0.3.6: SkyySkills 0.4.13 - 0.4.14 - kill XP by mob level + the level gap, gathering XP x3 to level 10, a rolled landing pays
     # fall XP, sickle swings pay Farming XP; Mana keeps refilling while charging - no new command, player switch or Server Setup title
     # 0.3.9: SkyySkills 0.4.21 - Assassination + Discipline ("Hypixel-style" + "as you play" dropped: the 390-character tooltip limit)
     "desc": "Skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill (Archery, Swordsmanship, Sorcery, Fury, Divinity, Assassination, Zen or Battlemagic, on its own XP curve) - level up and pay coins. Stronger mobs pay more kill XP. Your Overall Level adds Health and Mana, and Mana refills in combat at half speed.",
     "commands": ["/skills (or /skill) - open your Skills", "/skills stats <skill> - the Stats page of a skill (or overall)",
                  "/skills top <skill> - the top 10 players of a skill", "/skills quiet - hide the +XP chat messages",
                  "/skills reload - (admin) re-read the XP settings", "/skills xp <skill> <amount> - (admin) test XP",
                  "/skills mana - (admin) your live Mana regen: in or out of combat, boosts"]},
    # 0.3.3: SkyyTrees 0.2.4 (round 9): Tree Feller 1/2/4/5/6/10, Double Jump in tier III - no new command, switch or page title
    {"mod": "SkyyTrees", "version": MODS_VERSIONS["SkyyTrees"], "icon": "Plant_Sapling_Maple", "check": "tree",
     "config": "Skyy_SkyyTrees/trees.properties", "reload": "tree reload", "note": "",
     # 0.3.8: SkyyTrees 0.3 - 0.3.2 - the Alchemy + Smithing trees, the class tree (Ability Points from the class skill; ON by default
     # since 0.3.2, Skyy LOCKED 2026-10-05; Server Setup -> Trees -> Class trees), /tree class, the admin /tree probe page
     "setup": ("0.2.2", "Trees", "nodes, Dust, Tree Feller, Vein Burst, swings, class trees"),
     "desc": "Skill trees: spend the points your skill levels earn on nodes for Mining, Foraging, Farming, Cooking, Alchemy, Smithing, Acrobatics and Exploration - and a class tree that spends the Ability Points your class skill earns.",
     "commands": ["/tree (or /trees) - open your skill trees", "/tree <skill> - open one tree, for example /tree mining",
                  "/tree class - your class tree (Ability Points from your class skill)",
                  "/tree quiet - hide the Tree bonus chat line", "/tree reload - (admin) re-read the tree settings",
                  "/tree probe - (admin) the class tree probe page (nothing saved)"]},
    # 0.3.3: SkyyCollections 0.2.3 (round 8): the Magic Bag ladder - each bag type unlocks from one collection at tiers I / III / V / VII
    {"mod": "SkyyCollections", "version": MODS_VERSIONS["SkyyCollections"], "icon": "Furniture_Village_Painting_1x1", "check": "collections",
     "config": "Skyy_SkyyCollections/config.properties,Skyy_SkyyCollections/collections.properties,Skyy_SkyyCollections/rewards.properties", "reload": "collections reload", "note": "",
     "setup": ("0.2.2", "Collections", "curves, tier rewards, bag ladder, coin unlocks, rules"),
     # 0.3.5: SkyyCollections 0.2.5 - coins never buy a collection tier, a recipe unlock or a bag (Coin unlocks OFF by default; tiers
     # already bought stay) - no new command, switch or Server Setup title
     "desc": "Hypixel-style Collections: everything you gather counts toward tiers. Tiers unlock crafting recipes and pay rewards - each Magic Bag type climbs one collection: Normal, Unique, Rare and Legendary at tiers I, III, V and VII. Coins never buy a tier, recipe or bag.",
     "commands": ["/collections (or /coll) - open your Collections", "/collections <name> - the tiers of one collection",
                  "/collections unlocks (or recipes) - the recipes you unlocked",
                  "/collections top <collection|score> - the top 10 players",
                  "/collections give <collection> <amount> - (admin) test credit",
                  "/collections reload - (admin) re-read the collection rules"]},
    {"mod": "SkyyCooking", "version": MODS_VERSIONS["SkyyCooking"], "icon": "Food_Pie_Meat", "check": "cooking",
     "config": "Skyy_SkyyCooking/cooking.properties", "reload": "cookadmin reload", "note": "",
     "setup": ("0.1.2", "Cooking", "graded cooking, grades, Cooking XP, campfire, tree"),
     # 0.3.6: SkyyCooking 0.1.4 - food strength +32% per Grade, buff durations as before (2^(Grade/5)), Cooking XP default x0.5
     "desc": "Cooking: dishes you cook at a Cooking Bench get a Grade from your Cooking level and skill tree - every Grade makes the food 32% stronger and its buffs last longer.",
     "commands": ["/cooking - your Cooking level, Grade and tree chances",
                  "/cookadmin give <dish> <grade> - (admin) test dishes",
                  "/cookadmin campfire <dish> <count> - (admin) test the Campfire cook",
                  "/cookadmin reload - (admin) re-read the cooking settings"]},
    {"mod": "SkyyExploration", "version": MODS_VERSIONS["SkyyExploration"], "icon": "Furniture_Human_Ruins_Chest_Small", "check": "explore",
     "config": "Skyy_SkyyExploration/config.properties", "reload": "exploreadmin reload", "note": "Any key also in game: /exploreadmin set. titles.chatPriority needs a restart.",
     "setup": ("0.2.1", "Exploration", "XP sources, chest luck, spots, checklists, titles"),
     "admin": ["/exploreadmin set <key> <value> | get <key> - (admin) change or read a key"],
     "desc": "Exploration: loot chests out in the world, uncover the map, discover zones, find discovery spots and finish each island's checklist - all of it pays Exploration XP and earns titles.",
     "commands": ["/explore (or /exploration, /discoveries) - your exploration page",
                  "/explore quiet - hide the chunk XP chat line (also in /settings)", "/title (or /titles) - your titles",
                  "/title <name> or /title off - wear a title or none",
                  "/exploreadmin - (admin) place discovery spots, edit island checklists",
                  "/exploreadmin reload|stats|resetme - (admin)"]},
    # 0.3.2: SkyyClasses 0.1.6 (round 6): Berserker (Fury) + Priest (Divinity) playable, class kits (/class kit, /classadmin kit)
    # 0.3.3: SkyyClasses 0.1.7 (round 9): kits land in the hotbar at once (no wait), /class arrows (daily Archer arrows), Healing Totem = Priest
    {"mod": "SkyyClasses", "version": MODS_VERSIONS["SkyyClasses"], "icon": "Weapon_Shortbow_Iron", "check": "class",
     "config": "Skyy_SkyyClasses/config.properties", "reload": "classadmin reload", "note": "",
     "setup": ("0.1.5", "Classes", "weapon lock, class picker, kits, Priest heal, Archer arrows"),
     "admin": ["/classadmin kit <player> [class] - (admin) give a player a class kit now"],
     # 0.3.9: SkyyClasses 0.1.14 - Assassin + Monk playable
     "desc": "Classes: Archer, Warrior, Mage, Berserker, Priest (the party healer), Assassin, Monk or Spellblade (a melee mage). Each class has its own weapons and weapon skill and a kit with its basic weapon that lands in your hotbar at once. With SkyyProfiles the class is picked when you create a profile.",
     "commands": ["/class (or /classes) - open the class page",
                  "/class kit - collect kit items that did not fit your hotbar (or see your kit)",
                  "/class arrows - (Archers) claim your free daily arrows",
                  "/classadmin set <player> <class> - (admin) give a class",
                  "/classadmin reset <player> - (admin) remove a class", "/classadmin info <player> - (admin) class and kit data",
                  "/classadmin reload - (admin) re-read the settings"]},
    {"mod": "SkyyBazaar", "version": MODS_VERSIONS["SkyyBazaar"], "icon": "Rock_Gem_Emerald", "check": "bazaar",
     "config": "Skyy_SkyyBazaar/products.properties,Skyy_SkyyBazaar/market.properties,Skyy_SkyyBazaar/config.properties",
     "reload": "bazaaradmin reload", "note": "",
     # 0.3.7: SkyyBazaar 0.1.3 - its Server Setup page (Bazaar -> Market: the processed goods premium, config.properties)
     "setup": ("0.1.3", "Bazaar", "the processed goods premium"),
     # 0.3.8: SkyyBazaar 0.1.4 - progression prices (default prices only: about x2 per material tier step)
     "desc": "A Hypixel-style Bazaar: instantly buy or sell dozens of resources against the server. Prices move as people trade, and each higher material tier is worth about twice the one before.",
     "commands": ["/bazaar (or /bz) - open the Bazaar",
                  "/bazaaradmin price <itemId> <price> - (admin) set a price",
                  "/bazaaradmin reset|info <itemId|all> - (admin) reset or show prices",
                  "/bazaaradmin reload - (admin) re-read the product list"]},
    # 0.3.3: SkyyAuctions 0.1.2 = this round's pin (SkyyGear spec 7.3.1: gear rarity + modifiers through the bridge, 48h = double listing
    # fee, other profiles may buy, Magic Bags blocked) - same commands and files
    {"mod": "SkyyAuctions", "version": MODS_VERSIONS["SkyyAuctions"], "icon": "Ingredient_Bar_Gold", "check": "ah",
     "config": "Skyy_SkyyAuctions/config.properties,Skyy_Market/blocked.txt", "reload": "ahadmin reload", "note": "",
     "desc": "A Hypixel-style Auction House (Buy It Now): list an item for a fixed price, buy what other players list and claim the coins and items you are owed. Gear shows its rarity and modifiers. Magic Bags cannot be sold.",
     "commands": ["/ah (or /auction, /auctionhouse) - open the Auction House",
                  "/ah sell <price> [duration] - sell the item in your hand",
                  "/ah claim - claim your coins and items", "/ah manage - your listings and claims",
                  "/ah search <words> - search the listings",
                  "/ahadmin list|info|remove|reload|pause|resume|regrant - (admin)"]},
    {"mod": "SkyyBank", "version": MODS_VERSIONS["SkyyBank"], "icon": "Furniture_Ancient_Chest_Large", "check": "bank",
     "config": "Skyy_SkyyBank/config.properties", "reload": "", "note": "Change the interest in chat with /bankconfig - saved at once.",
     "desc": "A SkyBlock-style bank next to your coin purse: deposit coins to earn interest and withdraw them any time. Bank coins are never lost when you die.",
     "commands": ["/bank - open the bank page", "/bank deposit <n|all> - put coins in (500, 2k, 1.5m or all)",
                  "/bank withdraw <n|all> - take coins out", "/bank status - your bank and purse in chat",
                  "/bankconfig <percent> <minutes> - (admin) interest"]},
    {"mod": "SkyyCoins", "version": MODS_VERSIONS["SkyyCoins"], "icon": "Rock_Gem_Ruby", "check": "balance",
     "config": "Skyy_SkyyCoins/config.properties", "reload": "", "note": "Change the death penalty in chat with /deathpenalty - saved at once.",
     "desc": "The server's coins. Check your balance and pay other players. When you die you lose a set share of the coins in your purse (bank coins are safe).",
     "commands": ["/balance (or /bal, /coins, /purse) - your coins", "/pay <player> <amount> - send coins to a player",
                  "/coinsgive <amount> - (admin) give yourself coins", "/deathpenalty 5% or 5%-10% - (admin) coins lost on death"]},
    # 0.3.3: SkyyVault 0.1.3 (round 9): pages from buyConfirmCoins up ask in a confirm window (the 0.1.2 second-click buy is gone)
    {"mod": "SkyyVault", "version": MODS_VERSIONS["SkyyVault"], "icon": "Furniture_Royal_Magic_Chest_Large", "check": "vault",
     "config": "Skyy_SkyyVault/config.properties", "reload": "vaultadmin reload", "note": "",
     "setup": ("0.1.1", "Vault", "free pages, prices, buy confirm, page size, arrows, waits"),
     "admin": ["/vaultadmin config | config <key> <value> - (admin) settings in chat",
               "/vaultadmin reload - (admin) re-read config.properties"],
     "desc": "Your Vault: item storage shared by every profile you have, so you can move items from one profile to another. Buy more pages with coins.",
     "commands": ["/vault - open your Vault", "/vault <page> - open one vault page", "/vault buy - buy the next page (a window may ask you to confirm)",
                  "/vault info - your pages, slots used and the next price",
                  "/vaultadmin open|info|setpages <player> - (admin)"]},
    # 0.3.3: SkyyParty 0.1.5 (round 8, pinned): the party.invites switch refuses invites; staff bypass row privacy.staffBypass
    {"mod": "SkyyParty", "version": MODS_VERSIONS["SkyyParty"], "icon": "Deco_Scroll", "check": "party",
     "config": "Skyy_SkyyParty/config.properties", "reload": "partyadmin reload", "note": "",
     "setup": ("0.1.4", "Party", "party size, invite time, staff bypass"),
     "admin": ["/partyadmin - (admin) the party settings and how to change them",
               "/partyadmin set <maxSize|inviteSeconds|privacy.staffBypass> <value> - (admin)",
               "/partyadmin reload - (admin) re-read config.properties"],
     # 0.3.8: SkyyParty 0.1.7 - TPA / Accept TPA buttons on the party page (SkyyEssentials 0.1.8's tpa bridge); no new command or switch
     "desc": "Team up with friends: invite players to a party, chat privately and see your party on the HUD. The party page's TPA and Accept TPA buttons send or answer a teleport request in one click. Turn party invites off in /settings to refuse them (staff get through while privacy.staffBypass is on).",
     "commands": ["/party (or /p) - open the party page", "/party invite <player> - invite a player",
                  "/party accept | decline - answer an invite", "/party leave - leave your party", "/party list - list your party",
                  "/party kick | promote <player> - (leader)", "/party disband - (leader) end the party", "/pc <message> - chat with your party"]},
    # 0.3.2: SkyyGuilds 0.1.3 (pinned since round 7): Fury + Divinity count for guild XP; same commands, switches and page title
    {"mod": "SkyyGuilds", "version": MODS_VERSIONS["SkyyGuilds"], "icon": "Furniture_Outlander_Banner", "check": "guild",
     "config": "Skyy_SkyyGuilds/config.properties", "reload": "guildadmin reload", "note": "",
     "setup": ("0.1.2", "Guilds", "guild size, guild XP, levels, the guild bank"),
     "admin": ["/guildadmin config | set <key> <value> - (admin) settings in chat",
               "/guildadmin reload - (admin) re-read config.properties", "/guildadmin xp <amount> <guild> - (admin) test guild XP"],
     # 0.3.4: SkyyGuilds 0.1.5 (deployed 2026-10-01): a disband pays the guild bank back by each member's share of the deposits
     # (net = deposited - withdrawn), the member list shows that Contribution - no new command, switch or Server Setup title
     # 0.3.5: SkyyGuilds 0.1.6 - a member who leaves or is kicked gets back part of their contribution (Server Setup Leave refund, 35%)
     "desc": "Guilds: found a guild with your friends - ranks, a shared guild bank, guild XP from your skills, guild levels and seasons. If a guild disbands, its bank goes back to the members by what each put in, and a member who leaves or is kicked gets part of theirs back (35% by default).",
     "commands": ["/guild - open the guild page", "/guild create <name> - start a guild", "/guild invite <player> - (leader, admin) invite",
                  "/guild accept | decline | leave - answer an invite or leave",
                  "/guild bank deposit | withdraw <amount> | log - guild coins",
                  "/guild bank limit admin|member <n|0|none> - (leader) daily withdraw limit",
                  "/guild info | list - your guild | the top guilds", "/gc <message> - guild chat"]},
    # 0.3.3: SkyyEssentials 0.1.5 (round 8, pinned): tpa.requests + msg.private refuse the sender, staff bypass row privacy.staffBypass,
    # Server Setup parts / teleports / messages / privacy / warps / trade - the world-spawn rows are gone, /warpadmin is the Warps page
    {"mod": "SkyyEssentials", "version": MODS_VERSIONS["SkyyEssentials"], "icon": "Tool_Map", "check": "tpa",
     "config": "Skyy_SkyyEssentials/config.properties", "reload": "tradeadmin reload", "note": "Also in game: /tradeadmin config, /warpadmin. replyShortcut needs a restart.",
     "setup": ("0.1.3", "Essentials", "parts, teleports, messages, staff bypass, warps, trade"),
     "admin": ["/warpadmin - (admin) the Warps page: add, move, rename, remove and visit warps",
               "/tradeadmin config - (admin) the trade settings page",
               "/tradeadmin log [player] | return <player> - (admin) trade log, items back"],
     # 0.3.5: SkyyEssentials 0.1.7 - Magic Bags + the Accessory Bag are blocked in /trade (Server Setup Essentials -> Trade list
     # tradeBlockedItems, the AH's list); 0.1.6 item durability switch (Server Setup only)
     # 0.3.8: SkyyEssentials 0.1.8 - the tpa bridge behind SkyyParty's TPA buttons; same commands, switches and Server Setup page
     "desc": "Everyday commands the base game is missing: teleport requests between players (also from the party page), private messages and safe trades of items and coins (Magic Bags and Void Charms can't be traded). Turn teleport requests or private messages off in /settings (staff get through while privacy.staffBypass is on).",
     "commands": ["/tpa <player> - ask to teleport to a player", "/tpahere <player> - ask a player to teleport to you",
                  "/tpaccept | /tpdeny [player] - answer a teleport request", "/tpacancel - cancel your requests",
                  "/msg <player> <message> (or /tell, /w) - private message", "/reply <message> (or /r) - answer your last message",
                  "/trade <player> | claim - trade items and coins safely (no Magic Bags)", "/fly - (staff) toggle flight"]},
    # 0.3.3: SkyyGear 0.1 REPLACES SkyyRolls (research/SkyyGear-Stage1-Spec.md 7.3.2 + 8; ROUND_RETIRED below): /reforge moved, /identify,
    # /gear and the admin /gear lines (every /gear sub-command needs skyygear.admin). Server Setup -> Gear comes from its config:def:SkyyGear
    {"mod": "SkyyGear", "version": MODS_VERSIONS["SkyyGear"], "icon": "Weapon_Longsword_Copper", "check": "gear",
     "config": "Skyy_SkyyGear/config.properties", "reload": "", "note": "Set up in game - Server Setup, Gear.",
     # 0.3.5: SkyyGear 0.2 (stage 1 of the Wynn-style levels) - every item stores its own level = its requirement, crafted at your level
     # inside overlapping material bands; the admin /gear relevel [player]; 0.1.3 every world chest's gear unidentified
     # 0.3.6: SkyyGear 0.2.1 (stages 2-3) - weapon damage and armor Health / resistance grow with the item's level
     # 0.3.8: SkyyGear 0.2.3 - crafted gear pays Smithing XP (Server Setup -> Gear rows 'Smithing XP per crafted gear', 'Craft XP tier factor')
     "setup": ("0.1", "Gear", "level bands, damage and armor by level, crafting Smithing XP"),
     "admin": ["/gear give <item> [--rarity <id>] [--unid true] - (admin) a gear item",
               "/gear read | reroll | clear - (admin) the item in your hand",
               "/gear rarity <id> | unid | identify - (admin) the item in your hand",
               "/gear level <n|clear> | gate <skill|class> - (admin) the item in your hand",
               "/gear migrate [player] - (admin) run the old rolled items scan now",
               "/gear charged - (admin) charged attack probe for the held weapon",
               "/gear relevel [player] - (admin) move stamped gear into today's level bands"],
     "desc": "Rarity, level and modifiers on every weapon and armor piece. Each item has its own level - the class weapon skill you need to use it - and its damage or armor grows with that level. Crafted gear comes out at your level within its material's band, rolls and pays Smithing XP. Mob and chest gear drops unidentified, /identify reveals it, /reforge rerolls it.",
     "commands": ["/reforge - reroll the modifiers of a weapon or armor piece for coins",
                  "/identify - reveal the modifiers of unidentified gear for coins",
                  "/gear - the held item's gear lines, your totals and your Smithing rarity"]},
    # 0.3.7: SkyyArmory 0.1 (live since 2026-10-03, missing from 0.3.6's list): Priest wands in every metal + the Mage staff ladder (tap =
    # quick shot, hold = charged shot, both cost Mana); no command at all (check "" - the Mods view finds it by its plugin name); Server
    # Setup -> Armory (config kit, MOD=MOD constant); no player switch
    {"mod": "SkyyArmory", "version": MODS_VERSIONS["SkyyArmory"], "icon": "Weapon_Wand_Wood", "check": "",
     "config": "Skyy_SkyyArmory/config.properties", "reload": "", "note": "Change it in game: Server Setup -> Armory.",
     "setup": ("0.1", "Armory", "wand and staff damage, quick shots, Mana check"),
     "desc": "Wands and staffs: Priest wands in every metal from Copper to Onyxium and the Mage staff ladder. Tap for a quick shot, hold for a charged shot - both cost Mana, and better metals hit harder. Craft the metal wands at the Weapon Bench (Bow tab).",
     "commands": ["No commands - hold a wand or staff: tap for a quick shot, hold to charge."]},
    # 0.3.5: SkyyMobs 0.1 (NEW, deployed 2026-10-02): mob levels by zone / biome. /mobs + /mobs info for every player (hytale:Adventurer);
    # /mobs inspect | set | platetest | reload need skyymobs.admin; Server Setup -> Mobs (config kit, MOD=MOD constant); no player switch
    {"mod": "SkyyMobs", "version": MODS_VERSIONS["SkyyMobs"], "icon": "Armor_Trork_Head", "check": "mobs",
     "config": "Skyy_SkyyMobs/config.properties,Skyy_SkyyMobs/bands.properties", "reload": "mobs reload", "note": "",
     # 0.3.6: SkyyMobs 0.1.1 - 0.1.2 - Difficulty Easy / Normal / Hard / Custom, the level health floor (row strength.floor, 50 HP)
     "setup": ("0.1", "Mobs", "difficulty, health floor, who gets levels, bands, plates"),
     "admin": ["/mobs inspect - (admin) level, band and lookup of the mob you look at",
               "/mobs set <level> - (admin) the level of the mob you look at (0 removes it)",
               "/mobs platetest - (admin) try the three nameplate colour markups",
               "/mobs reload - (admin) re-read config.properties and bands.properties"],
     "desc": "Mob levels: hostile mobs and neutral fighters get a level from the zone and biome they spawn in (Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60). Each level adds health and damage (Difficulty Easy, Normal or Hard in Server Setup), weak mobs get a health floor, and the nameplate shows it, like [Lv 9] Trork Warrior. Animals, traders, pets and bosses never get one.",
     "commands": ["/mobs (or /mobs info) - the mob level band where you stand"]},
    # 0.3.6: SkyyWorldGen 0.1 (NEW, deployed 2026-10-03): the World Gen V2 Zone 1 TEST island (world skywynn_z1). Every /zone command is
    # admin-only in this test version (requirePermission skyyworldgen.admin + setPermissionGroups(new String[0])); Server Setup -> World Gen
    # (config kit, MOD=MOD constant); no player switch; no menu tile (its own notes: no SkyyMenu tile in 0.1)
    {"mod": "SkyyWorldGen", "version": MODS_VERSIONS["SkyyWorldGen"], "icon": "Plant_Sapling_Azure", "check": "zone",
     "config": "Skyy_SkyyWorldGen/config.properties", "reload": "zone reload", "note": "",
     "setup": ("0.1", "World Gen", "zone islands on or off, the Zone 1 landing point"),
     "admin": ["/zone - (admin) the zone islands and their status",
               "/zone 1 - (admin) go to the Zone 1 test island (made the first time)",
               "/zone info | leave - (admin) where you stand | back to where you came from",
               "/zone setlanding - (admin) the landing point = where you stand",
               "/zone reload - (admin) re-read config.properties"],
     "desc": "Zone islands made with World Gen V2: a floating Zone 1 test island with void all around - a meadow rim, a birch forest and an azure core, with mob levels rising toward the middle. Test version: only admins can go there for now.",
     "commands": ["No commands for players yet - the zone islands are an admin test."]},
    # 0.3.1: SkyyRanks 0.1 (live since round 3) - every command is admin only, so players read the description alone
    # 0.3.3: SkyyRanks 0.1.1 (round 9): seeds Member / Admin / Developer + the protected Owner rank; the editor = ops + the Owner rank
    {"mod": "SkyyRanks", "version": MODS_VERSIONS["SkyyRanks"], "icon": "Furniture_Royal_Magic_Chair", "check": "rankadmin",
     "config": "Skyy_SkyyRanks/config.properties,Skyy_SkyyRanks/ranks.properties", "reload": "rankadmin reload", "note": "",
     "setup": ("0.1", "Ranks", "the ranks editor, the default rank, the chat prefix"),
     "admin": ["/rankadmin - (admin) the ranks editor: ranks, prefixes, grants, members",
               "/rankadmin player <player> - (admin) one player's rank and denies",
               "/rank set <player> <rank> | clear <player> - (admin) give or take a rank in chat",
               "/rankadmin reload | sync - (admin) re-read the files, fix the groups"],
     "desc": "Server ranks with a chat prefix in front of your name - Member, Admin, Developer and Owner to start. Ops and the Owner rank make the ranks and what each rank may do, all in game.",
     "commands": ["No commands for players - your rank shows in front of your name in chat."]},
    # 0.3.4: SkyyUiProbe 0.2 is in tools/deploy_set.py SET as a DEVELOPER / TEST mod (the vanilla UI kit's probe pages, admins only:
    # requirePermission skyyuiprobe.admin). It moves to RETIRED once the probe results are in - then drop this entry.
    # 0.3.5: SkyyUiProbe 0.3 - + the two vault window probes P1 /skyprobe win and P2 /skyprobe secgrid (probe pages 23 and 24)
    {"mod": "SkyyUiProbe", "version": MODS_VERSIONS["SkyyUiProbe"], "icon": "Ingredient_Crystal_Cyan", "check": "skyprobe",
     "config": "", "reload": "", "note": "A developer test mod - nothing to set up.",
     "admin": ["/skyprobe [n | name | list] - (admin) open the UI kit probe pages",
               "/skyprobe win | secgrid - (admin) the two vault window probes (23, 24)",
               # 0.3.7: SkyyUiProbe 0.4 - the minimap probe steps (each off by default, started only by an op for that player)
               "/skyprobe map [step] - (admin) the minimap probe steps (off by default)"],
     "desc": "Developer test mod, not a game feature: admins open the UI kit's probe pages and two vault window probes to check what works in game.",
     "commands": ["No commands for players - this is a developer test mod."]},
]
# ---- Settings (0.2, research/Settings-Spec.md sections 2 + 4): the player Settings page (/settings, the torch at main slot 39 since 0.3.3).
# Rows are NOT made from this list: a row appears only when its mod REGISTERS the key (settings:fn:register or a settings:def:<key>
# fallback on the bridge). This list gives the known keys their order inside a tab (SET_ORDER), fills the commented
# settings-defaults.properties template and is checked when you build (key format, label <= 40, help <= 90 characters).
# Tabs, in display order: (category id, tab button text = ONE word, header, "always shown" line under the rows)
SET_TABS = [
    ("skills",      "Skills",      "Skills",             "Always shown: the one-time note when your old Combat XP moves to your class skill."),
    ("collections", "Collections", "Collections",        "Always shown: the one-time note about how collections count items."),
    ("sacks",       "Sacks",       "Sacks & Crafting",   "Always shown: the profile-changed notice on an open bag or craft page."),
    ("combat",      "Combat",      "Combat & Classes",   "Always shown: the reminder to pick a class, your class kit and admin changes to your class. Blocked hits stay blocked."),
    ("coins",       "Coins",       "Coins & Bank",       "Always shown: coins you lose when you die, and your starter coins."),
    ("profiles",    "Profiles",    "Profiles & Islands", "Always shown: profile setup, switch problems, crash repairs and items that did not fit back."),
    ("cooking",     "Cooking",     "Cooking & Trees",    "Everything on this tab can be switched off."),
    # 0.3.21: SkyyHud's message routes (category "messages", registered by SkyyHud 0.3.20+; SET_ORDER_MSG gives their order)
    ("messages",    "Messages",    "Messages (chat, feed or off)",
     "Each message type: the first switch shows or hides it, the second puts it in the feed above chat. Errors stay in chat."),
    ("general",     "General",     "General (party, guild, teleports, menu)",
     "Always shown: accepted teleports, party or guild disbanded, lines about you, and replies to your own commands and clicks."),
]
# Every known switch, all default ON: (key, tab id, label, help line, registered by). Settings-Spec 2.2 order. 0.3.3: WITH the three
# refusing General switches (party.invites, tpa.requests, msg.private) - Skyy answered "block" on 2026-09-25 (SkyyParty 0.1.5 and
# SkyyEssentials 0.1.5 register them). A switch whose mod registers a permission node (7th element, 0.3.3) is shown only to holders.
# Where a mod already ships its registration, its exact label / help is copied here (explore.* = SkyyExploration 0.2's regSetting,
# research/Exploration-0.2-Spec.md 9). The page always shows the registering mod's own text and the defaults template lists keys
# only, so for other mods' keys the label / help here are only length-checked documentation - keep them in step anyway.
# Rows registered by "SkyyMenu" are this mod's own switches (registered at setup like any adopter).
SET_KNOWN = [
    ("skills.xpGain",        "skills",      "Skill XP gains",               "+12 Mining XP (340/500) while you gather, fight, smelt, brew and move", "SkyySkills"),
    ("skills.levelUp",       "skills",      "Skill level-ups",              "SKILL LEVEL UP with the coins it paid and the XP for the next level", "SkyySkills"),
    ("skills.doubleDrop",    "skills",      "Double drops",                 "Double drop x3! from the Mining, Foraging and Farming perks", "SkyySkills"),
    ("skills.extraPotion",   "skills",      "Extra potions",                "Extra potion! from the Alchemy perk", "SkyySkills"),
    ("skills.combatHints",   "skills",      "No combat XP hints",           "Why a kill gave no combat XP - once per reason each session", "SkyySkills"),
    ("explore.chunkXp",      "skills",      "Exploration map XP",           "+1,240 Exploration XP from 18 new chunks - at most every 30 s", "SkyyExploration"),
    ("explore.finds",        "skills",      "Exploration finds",            "Loot chests, chest luck, new zones, discoveries, checklists and new titles", "SkyyExploration"),
    # 0.3.3: SkyySkills 0.4.6 (research/Overall-Level-Spec.md): the Overall Level line, Skills tab row 8
    ("skills.overallUp",     "skills",      "Overall Level ups",            "OVERALL LEVEL UP 12 -> 13 with the max Health and Mana it added", "SkyySkills"),
    ("coll.newCollection",   "collections", "New collections",              "New collection: Copper Ore! - the first item of a kind you gather", "SkyyCollections"),
    ("coll.tierUp",          "collections", "Collection tier-ups",          "COLLECTION UP with its rewards and the recipes it unlocked", "SkyyCollections"),
    ("sacks.benchDone",      "sacks",       "Furnace and Tannery done",     "Your Furnace is done - open /craft to collect", "SkyySacks"),
    ("sacks.benchFuel",      "sacks",       "Furnace out of fuel",          "Your Furnace ran out of fuel - once until you add more", "SkyySacks"),
    ("classes.blockedChat",  "combat",      "Blocked weapon - chat line",   "Only Archers can use bows... - at most every 3 s. The hit is blocked either way", "SkyyClasses"),
    ("classes.blockedPopup", "combat",      "Blocked weapon - popup",       "The popup with the weapon's icon - at most every 1.5 s", "SkyyClasses"),
    # 0.3.2: SkyyClasses 0.1.6's two Priest heal lines (its regSetting texts, category combat, default ON; the heal itself always happens)
    # 0.3.3: SkyyClasses 0.1.7 texts: one line every 10 s (Skyy's edited priestHeal.feedbackMs default)
    ("classes.healGiven",    "combat",      "Priest heals - your heals",    "Your heals: +23 HP to 2 party members and +6 HP to you - one line every 10 s at most", "SkyyClasses"),
    ("classes.healTaken",    "combat",      "Priest heals - healed by others", "Skyy healed you +12 HP - one line every 10 s at most. The heal happens either way", "SkyyClasses"),
    # 0.3.3: SkyyGear 0.1's three switches (spec 9.3, no permission node = every player sees them)
    ("gear.blockedPopup",    "combat",      "Gear level popups",            "Popup when a weapon is too high level or unidentified", "SkyyGear"),
    ("gear.armorWarn",       "combat",      "Armor level warning",          "Chat line when armor gives no stats because of its level", "SkyyGear"),
    ("gear.notices",         "combat",      "Gear update notices",          "One-time line when your old rolled items move to the new gear system", "SkyyGear"),
    # 0.3.7: SkyyGear 0.2.2 - the crit effects switch
    ("gear.critFx",          "combat",      "Crit effects",                 "CRIT! popup, sparks and the red number on your critical hits", "SkyyGear"),
    # 0.3.3: SkyySkills 0.4.6's crossbow switches (LOCKED 2026-09-25: meter, sound and hint each switchable)
    ("skills.xbowMeter",     "combat",      "Crossbows keep the big-arrow meter", "Your crossbow's big-arrow meter comes back with its bolts when you switch back to it", "SkyySkills"),
    ("skills.xbowSound",     "combat",      "Crossbow reload sound",        "The crossbow load sound when your kept bolts go back in (Archery perk)", "SkyySkills"),
    ("skills.xbowHint",      "combat",      "Crossbow reload chat line",    "Crossbow reloaded - 6 bolts back in - when your kept bolts return", "SkyySkills"),
    ("coins.payReceived",    "coins",       "Payments from players",        "Steve paid you 500 coins - the coins arrive either way", "SkyyCoins"),
    ("bank.interest",        "coins",       "Bank interest",                "You earned 120 coins interest - one line per payout", "SkyyBank"),
    ("rewards.late",         "coins",       "Late reward payouts",          "Coins and XP paid later because another mod was not ready", "SkyySkills + SkyyCollections"),
    ("profiles.loginStatus", "profiles",    "Profile on login",             "Playing profile Strawberry (Archer) - when you join", "SkyyProfiles"),
    ("islands.protection",   "profiles",    "Island protection warnings",   "You can only build on islands you are a member of - at most every 3 s", "SkyyIslands"),
    ("islands.hubOnLogin",   "profiles",    "Hub on login",                 "Welcome back! You start in the hub - when you log in on an island", "SkyyIslands"),
    ("islands.buildRights",  "profiles",    "Build rights given to you",    "Steve gave you build rights on their island", "SkyyIslands"),
    ("islands.visitPing",    "profiles",    "Visitors on your island",      "Steve is visiting your island - the island's Visit ping must be on too", "SkyyIslands"),
    ("islands.visitWelcome", "profiles",    "Welcome when you visit",       "What visitors may do, when you arrive on someone's island", "SkyyIslands"),
    ("cooking.grade",        "cooking",     "Food Grade changes",           "Your food now comes out Grade 3 - and the campfire accessory hint", "SkyyCooking"),
    ("cooking.procs",        "cooking",     "Cooking bonus procs",          "Gourmet!, Signature Dish!, Batch Cook!, Prep Cook! and Frugal!", "SkyyCooking"),
    ("trees.bonus",          "cooking",     "Tree bonus totals",            "Tree bonus: +2 Copper Ore, extra drops x1, +3 coins", "SkyyTrees"),
    ("trees.abilities",      "cooking",     "Vein Burst and Tree Feller",   "Vein Burst! +6 ore (ready again in 40 s)", "SkyyTrees"),
    # 0.3.3: SkyyParty 0.1.5 - the FIRST General row (Settings-Spec 2.2); OFF refuses the inviter
    ("party.invites",        "general",     "Party invites",                "OFF: other players can't invite you - they are told so", "SkyyParty"),
    ("party.members",        "general",     "Party join, leave and leader", "Steve joined, left, disconnected or is now the party leader", "SkyyParty"),
    ("party.chat",           "general",     "Party chat",                   "[Party] lines from other members - your own lines always show", "SkyyParty"),
    # 0.3.1: SkyyGuilds 0.1.2's three hide-only switches (its regSetting texts, category general, all default ON)
    ("guild.online",         "general",     "Guild members online/offline", "Steve is online / went offline - the server's guild online notices must be on too", "SkyyGuilds"),
    ("guild.members",        "general",     "Guild join, leave and ranks",  "Steve joined, left, was removed or got a new rank - lines about you always show", "SkyyGuilds"),
    ("guild.chat",           "general",     "Guild chat",                   "[Guild] lines from other members - your own lines always show", "SkyyGuilds"),
    # 0.3.3: SkyyEssentials 0.1.5's refusing switches around tpa.updates (Settings-Spec 2.2 order)
    ("tpa.requests",         "general",     "Teleport requests",            "OFF: nobody can send you /tpa or /tpahere - they are told (staff may still)", "SkyyEssentials"),
    ("tpa.updates",          "general",     "Teleport request updates",     "Denied, expired and cancelled requests - accepted ones always show", "SkyyEssentials"),
    ("msg.private",          "general",     "Private messages",             "OFF: /msg and /reply to you are refused and the sender is told (staff may still)", "SkyyEssentials"),
    ("menu.tooltips",        "general",     "Menu hover tooltips",          "Pop-up text when you hover an item in the SkyWynn Menu - OFF stops stuck tooltips", "SkyyMenu"),
    # 0.3.19: the hub hotkey (Skyy 2026-10-13 "Hotkey now"): double-tap crouch while standing opens the SkyWynn Menu - ON by default
    ("menu.hotkey",          "general",     "Hub hotkey: double-tap crouch", "Tap crouch twice quickly while standing on the ground to open the SkyWynn Menu", "SkyyMenu"),
    # 0.3.25: the per-player sound switch (Skyy 2026-10-14 "do ... 6."): published as settings:sounds:<uuid> = Boolean (SoundSw)
    ("menu.sounds",          "general",     "Mod sounds",                   "Sounds the SkyWynn mods play for you (quests, bank, pets) - OFF mutes them for you only", "SkyyMenu"),
]
TIPS_KEY = "menu.tooltips"      # the 0.1.3 Hover Tooltips book (slot 8) and the Settings row are this one key
HOTKEY_KEY = "menu.hotkey"      # 0.3.19: the hub hotkey's player switch (MenuHotkey / HotkeyOpen)
SOUNDS_KEY = "menu.sounds"      # 0.3.25: the per-player sound switch (SoundSw -> bridge settings:sounds:<uuid>)
SOUNDS_BRIDGE = "settings:sounds:"   # 0.3.25: + <uuid> = java.lang.Boolean (absent or TRUE = on, FALSE = muted) - the sound rounds' contract
HOTKEY_GAP_MS = 400             # 0.3.19: the second crouch press must come within this many ms of the first (default; Server Setup)
HOTKEY_COOLDOWN_MS = 1500       # 0.3.19: at most one open per this many ms per player (default; Server Setup)
# ---- 0.3.2: the class roster every class text names (SkyyClasses 0.1.6 CLASSES, in its display order; the build checks the texts
# against these lists and the live-set cross-check checks these lists against the SkyyClasses build script SET pins)
# 0.3.9: SkyyClasses 0.1.14 - Assassin + Monk playable (the Shaman slot is the Monk; its skill name Discipline is OPEN for Skyy)
CLASS_PLAYABLE = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"]   # 0.3.30: + the Spellblade (SkyyClasses 0.1.25+)
CLASS_LATER    = []
# 0.3.13: the Monk's skill is Zen (Skyy LOCKED 2026-10-08; SkyyClasses 0.1.15, SkyySkills 0.4.27)
CLASS_SKILLS   = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity", "Assassination", "Zen", "Battlemagic"]   # 0.3.30: + Battlemagic      # the weapon skill of each CLASS_PLAYABLE class
# 0.3.13: OLD class skill labels a SkyySkills before 0.4.27 still publishes in skill:<uuid> (StatsCalc.isClassSkill only - never shown by us)
CLASS_SKILLS_OLD = ["Discipline"]
# ---- the round this SkyyMenu deploys WITH: mod: (the SET version the round replaces - None for a mod the round ADDS -, the round's
# version). MODS names the round's version; the live-set check accepts it while SET still pins the replaced version and runs a second time
# on the SET the main session pins when the round deploys (see menu_check). Inert once SET pins it.
# 0.3.4 / 0.3.5 / 0.3.6: EMPTY - this SkyyMenu deploys on its own; MODS names exactly what tools/deploy_set.py SET pins (the
# MODS_VERSIONS table above). To ship it together with e.g. SkyyGear 0.2.1: {"SkyyGear": ("0.2", "0.2.1")} + that version in MODS_VERSIONS.
# 0.3.7: deploys WITH SkyyExploration 0.2.3 (page guard), SkyyAccessories 0.5.5 and SkyyCooking 0.1.6 (tools/menu_0_3_7_patch.py ROUND).
# If one of them does not ship, set its MODS_VERSIONS entry back and drop it here (the live-set check names it).
# 0.3.8: deploys WITH SkyyTrees 0.3.2 (class trees ON by default; tools/menu_0_3_8_patch.py ROUND). 0.3.7's round is pinned in SET now.
# 0.3.9: deploys WITH SkyyClasses 0.1.14 + SkyySkills 0.4.21 + SkyyProfiles 0.1.6 (Assassin + Monk; tools/menu_0_3_9_patch.py ROUND).
# 0.3.8's round (SkyyTrees 0.3.2) is pinned in SET now.
# 0.3.10: EMPTY - deploys on its own (the Stats page reads only what the live mods already publish). 0.3.9's round (SkyyClasses
# 0.1.14, SkyySkills 0.4.21, SkyyProfiles 0.1.6) is pinned in SET now.
# 0.3.11: EMPTY - ships with SkyyAccessories 0.5.9 (same icon on the Workbench tab) but needs nothing from it; the Mods list version
# catch-up (SkyyAccessories 0.5.5 there) stays a later round.
# 0.3.12: EMPTY - reads SkyySkills 0.4.25's skill:def:<uuid> (already the SET pin); without it the Defense row is 0.3.11's.
# 0.3.13: deploys WITH SkyySkills 0.4.27 + SkyyClasses 0.1.15 + SkyyTrees 0.3.5 + SkyyProfiles 0.1.8 (the Monk skill Zen;
# tools/menu_0_3_13_patch.py ROUND). If one of them does not ship, set its MODS_VERSIONS entry back and drop it here.
# 0.3.14: EMPTY - deploys on its own (the Pets tile reads SkyyPets 0.2's records, already the SET pin). 0.3.13's round is pinned in SET now.
# 0.3.15: EMPTY - art only (the menu item's own emblem), deploys on its own.
# 0.3.16: EMPTY - layout D + icons + tile rules, no other mod needed (the Wardrobe tile waits for SkyyWardrobe's wardrobe:fn:open).
# 0.3.17: EMPTY - the layout editor, SkyyMenu's own files only.
# 0.3.18: EMPTY - the Hytale 0.7.0 port (every port build works on its own with the 0.7.0 engine).
ROUND_PINS = {}   # 0.3.39: none (0.3.36's SkyyAccessories 0.5.21 -> 0.5.22 pin is deployed; MODS_VERSIONS = the live SET)
# mods a round RETIRES: mod: (the SET version that leaves, the MODS entry that replaces it). 0.3.3 retired SkyyRolls (in RETIRED now).
ROUND_RETIRED = {}
SET_ROWS = 8                    # rows per tab page (Prev / Next appear only when a tab has more; 0.3.1: 8, was 7)
SET_TXT = {
    "HINT":   "Your own settings - the same on every profile. Click ON or OFF, it saves at once.",
    "EMPTY":  "Nothing to switch here yet - the mods for this tab are not installed or not updated.",
    "BROKEN": "Your settings file could not be read - changes are not saved. Tell an admin.",
    "ARM":    "Click Reset again within 10 seconds to reset EVERY tab to its default.",
    "RESET":  "Every setting is back to its default.",
    "GONE":   "You can no longer change that setting.",      # 0.3.3: a stale click on a row whose permission node the player lost
    # 0.3.25: the search box
    "SHORT":  "Type at least 2 letters to search.",
    "FIND":   "Results from every tab - click ON or OFF to change one, a tab to leave the search, or Clear.",
    "NOFIND": "Nothing matches - try other words, or click Clear.",
}
# ---- Server Setup (0.3, research/Server-Setup-Spec.md section 2): the admin Mods section (the book at main slot 41, /modconfig).
# Every Skyy mod that adopted the config registry (tools/CONFIG-CONTRACT.md) publishes config:def:<Mod> + config:fn:<Mod>; this page
# draws them and passes every click back to the mod, which validates, saves, logs and versions it. Other mods show their file (the
# "config" / "reload" / "note" / "admin" fields of MODS above).
ADMIN_NODE = "skyymenu.modconfig"   # who sees Server Setup (ops have it through hytale:Admin's built-in "*"); re-checked on every click
ADMIN_CMD, ADMIN_ALIAS = "modconfig", "serversetup"
ADM_CONTRACT = "1"                  # config contract this SkyyMenu reads (header element 0); a newer one shows "needs a newer SkyyMenu"
ADM_TXT = {
    "NOACCESS": "You no longer have access to Server Setup.",
    "NEWER":    "This mod needs a newer SkyyMenu to be changed in game.",
    "NOANSWER": "That mod did not answer - see the server log.",
    "CHANGED":  "Changed again since - open the mod to edit it.",
    "CANCEL":   "Cancelled - nothing was changed.",
    "LISTSUB":  "Every Skyy mod on this server. Click Open to change its settings in game.",
}
# SkyyMenu's OWN admin config (spec 4.7), compiled by tools/skyycfg.py like every adopter; it appears in Server Setup as "Menu".
MENU_CFG_NODE = "skyymenu.admin"    # who may change SkyyMenu's own settings (the kit re-checks it on every write)
MENU_CFG_FILES = ["Skyy_SkyyMenu/config.properties", "Skyy_SkyyMenu/settings-defaults.properties"]
MENU_CFG_CATS = [("menu", "Menu"), ("settings", "Player settings")]
MENU_CFG_NOTE = "Players still change their own switches in /settings - these are the server defaults."
MENU_CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, binding) - tools/CONFIG-CONTRACT.md
    ("menu.giveItem", "Give the menu item", "menu", "bool", "true", "", "", "", "", "live",
     "Every profile gets the SkyWynn Menu item the first time it is used. Off: only /skymenu gives one.",
     "field:MenuCfg.GIVE_ITEM@config.properties:giveItem"),
    ("menu.modsHelp", "Mods list for players", "menu", "bool", "true", "", "", "", "", "live",
     "Players see the Mods tile (every mod and its commands). Admins always see it.",
     "field:MenuCfg.MODS_HELP@config.properties:modsHelp"),
    # 0.3.32: the lifelong menu item (MenuOnce reads it live)
    ("menu.itemKeep", "Menu item stays with you", "menu", "bool", "true", "", "", "", "", "live",
     "Never dropped, stored or sold; one per profile (extras removed); /menuitem brings it back.",
     "field:MenuCfg.KEEP_ITEM@config.properties:itemKeep"),
    # FIX ROUND: the hub hotkey's timing (MenuHotkey.step reads the fields live)
    ("menu.hotkeyGapMs", "Hub hotkey: double-tap gap", "menu", "int", str(HOTKEY_GAP_MS), "200", "800", "step=50", "ms", "live,adv",
     "Most time between the two crouch presses that open the SkyWynn Menu (double-tap crouch).",
     "field:MenuCfg.HOTKEY_GAP_MS@config.properties:hotkeyGapMs"),
    ("menu.hotkeyCooldownMs", "Hub hotkey: cooldown", "menu", "int", str(HOTKEY_COOLDOWN_MS), "500", "10000", "step=100", "ms", "live,adv",
     "Least time between two menu opens by double-tap crouch, per player.",
     "field:MenuCfg.HOTKEY_COOLDOWN_MS@config.properties:hotkeyCooldownMs"),
    ("menu.tooltipsDefault", "Hover tooltips default", "settings", "bool", "true", "", "", "", "", "live",
     "For players who never chose. The same line as Menu hover tooltips in the defaults table below.",
     "custom:SetDefCfg@settings-defaults.properties:menu.tooltips"),
    ("settings.defaults", "Player settings defaults", "settings", "table", "", "", "", "text;none;Default", "", "live",
     "The server default of every /settings switch: on, off or unset. A player's own choice wins.",
     "custom:SetDefCfg@settings-defaults.properties;check=SetDefCfg.check"),
]
MENU_CFG_TEXT = "\n".join([
    "# SkyyMenu server settings. Change them in game (SkyWynn Menu - Server Setup - Menu, or /modconfig menu) or edit this file and",
    "# click Reload file there. The server defaults of the player switches (/settings) live in settings-defaults.properties.",
    "",
    "# giveItem = give new players the SkyWynn Menu item at their first join (true or false). /skymenu always gives a lost one back.",
    "giveItem=true",
    "",
    "# modsHelp = show players the Mods tile (every mod and its commands). Admins always see it.",
    "modsHelp=true",
    "",
    "# itemKeep = the SkyWynn Menu item stays with you: it can't be dropped, stored in a container or sold, one per profile (extra copies",
    "# are removed) and /menuitem gives it back (true or false).",
    "itemKeep=true",
    "",
    "# hotkeyGapMs = the hub hotkey: most milliseconds between the two crouch presses (200-800). hotkeyCooldownMs = least milliseconds",
    "# between two opens per player (500-10000). Players switch the hotkey itself in /settings (Hub hotkey: double-tap crouch).",
    "hotkeyGapMs=%d" % HOTKEY_GAP_MS,
    "hotkeyCooldownMs=%d" % HOTKEY_COOLDOWN_MS,
]) + "\n"
# =====================================================================================================================
# ==============================================  end of MENU DATA  ===================================================
# =====================================================================================================================

# ---- 0.3.28: HUBS H2 (research/Hubs-Spec.md 1.2 + 2.1-2.4; the contract tables live in tools/skyyui.py kit 1.5: HUBS, HUB_DEFS, HUB_TABS)
# SkyyMenu's OWN tabs = the HUB_TABS rows whose owner is SkyyMenu (same hub, tab id, order, label, fallback command - None = no command)
HUB_OWN = [(h, t, o, l, c) for h, t, o, m, l, c in SUI.HUB_TABS if m == "SkyyMenu"]
assert [(h, t) for h, t, _o, _l, _c in HUB_OWN] == [("character", "stats"), ("world", "teleport"), ("social", "players"), ("settings", "settings"),
                                                  ("settings", "layout"), ("settings", "mods"), ("settings", "setup")], "0.3.28: Menu's 7 tabs (spec 1.2)"
HUB_OWN = [_r for _r in HUB_OWN if (_r[0], _r[1]) not in SUI.HUB_RETIRED]   # 0.3.35: Settings drops Edit shortcuts (Skyy popup 5)
assert [(h, t) for h, t, _o, _l, _c in HUB_OWN] == [("character", "stats"), ("world", "teleport"), ("social", "players"), ("settings", "settings"),
                                                  ("settings", "mods"), ("settings", "setup")], "0.3.35: Menu puts 6 tabs (no Edit shortcuts)"
HUB_OWN_VIS = ("mods", "setup")      # the tabs with a visible Function: mods = admins or everyone while menu.modsHelp is on; setup = admins
# hub:def:<hub> = {title, command, icon item}: the icon is one of OUR tile icon items (the SkyWynn Menu's art/menu-icons set)
# 0.3.30: each hub wears its OWN wave-3 icon (0.3.28 - 0.3.29 reused a page's icon: Storage = Pocket Dimension, World = Teleport, ...)
HUB_ICON_ITEM = {"character": "Skyy_Menu_Icon_HubCharacter", "storage": "Skyy_Menu_Icon_HubStorage", "market": "Skyy_Menu_Icon_HubMarket",
                 "smithing": "Skyy_Menu_Icon_HubSmithing", "world": "Skyy_Menu_Icon_HubWorld", "social": "Skyy_Menu_Icon_HubSocial",
                 "settings": "Skyy_Menu_Icon_HubSettings"}
assert sorted(HUB_ICON_ITEM) == sorted(SUI.HUBS) and all(v in ICON_ITEMS for v in HUB_ICON_ITEM.values()), "0.3.28: every hub has our icon item"
# the chat line of a hub command while the hub has no tab yet (the other mods add theirs in the H3 rounds)
# 0.3.30 (Skyy 2026-10-16 "smithing still working"): no "coming soon" where a page exists - the stand-in tabs (MenuHub.register) give
# every hub its contract pages whose command is on this server; this line is only for a hub with truly nothing to open
# 0.3.31 (Skyy 2026-10-16 "we need a crafting tab at the top ... roll crafting and smithing into 1 page called crafting"): the hub with the id
# "smithing" is titled CRAFTING and opens with /crafting (the id stays: saved shortcuts hub:smithing / tab:smithing:<tab> keep working)
HUB_TITLE31 = {"smithing": "Crafting"}
HUB_CMD31 = {"smithing": "crafting"}
hub_title = lambda h: HUB_TITLE31.get(h, SUI.HUB_DEFS[h][0])
hub_cmd = lambda h: HUB_CMD31.get(h, SUI.HUB_DEFS[h][1])
assert all(len(hub_title(_h)) <= len(max(SUI.HUB_ROW_TITLES, key=len)) for _h in SUI.HUBS), "0.3.31: every hub title fits row 1 like the kit's"
HUB_SOON = dict((_h, "No %s pages are on this server right now." % hub_title(_h)) for _h in SUI.HUBS)
assert sorted(HUB_SOON) == sorted(SUI.HUBS)
# the hub commands SkyyMenu registers (spec 2.3; /smithing stays SkyyGear's, /settings is Menu's own page already): word, aliases, hub
HUB_CMDS = [("character", ("char",), "character"), ("storage", (), "storage"), ("market", (), "market"), ("crafting", (), "smithing"), ("travel", (), "world"),
            ("social", (), "social")]
assert all(hub_cmd(h) == w for w, _a, h in HUB_CMDS), "0.3.28 / 0.3.31: each hub command is the hub's command (SUI.HUB_DEFS; Crafting = /crafting)"
HUB_INFO_LINES = 8                   # the menu views in the hub shell: 8 info lines (the 980 px page; the main view keeps 9)
HUB_TXT_FAIL = "That tab could not open right now - try again."
ADM_SUBMAX = 140                     # Server Setup in the hub shell: "<view title>   -   <subtitle>" on one line, cut at 140 characters
                                     # (measured: ~1020 px of the 1080 px line at 16 px bold - the check below)
ADM_PREFIX = "Server Setup - "       # dropped from the view title in the hub shell (the active tab already says Server Setup)
assert all(len(HUB_SOON[_h]) <= 100 for _h in SUI.HUBS), "0.3.28: the coming-soon lines stay short"

# ---- 0.3.29: UNIFIED MENU U1 (research/Unified-Menu-Plan.md section 0; Skyy 2026-10-15 "combined D and A"). The Home page's 7 x 5 SHORTCUT
# GRID (centre slot 17 = the old 9 x 6 slot 13's screen spot) and the Teleport page's grid. A shortcut is a KEY (saved as text):
#   hub:<hub>            a hub (opens its default tab, else its last tab, else its first tab: kit 1.6 HubBar.pickTab)
#   tab:<hub>:<tab>      one hub tab (= one page: "every page keeps its own shortcut, hidden by default")
#   tile:<0.3.28 key>    an old menu tile (its 0.3.28 action, visibility rule and text)
#   tp:island|hub|spawn  a teleport target;  warp:<name>  a warp
HG_COLS, HG_ROWS = 5, 5                      # 0.3.30: 5 x 5 (Skyy 2026-10-16 "5x5 is big enough for the shortcuts."; 0.3.29: 7 x 5)
HG_N = HG_COLS * HG_ROWS
HG_CR, HG_CC = 2, 2                          # the centre: row 2, column 2 = slot 12
HG_CENTRE = HG_CR * HG_COLS + HG_CC
# 0.3.30: the saved files keep 0.3.29's 7 x 5 NUMBERING (g.<slot> / t.<slot> = row * 7 + column, 17 = the centre); the 5 x 5 grid is its
# columns 1 - 5 (G7_OFF), so a rollback to 0.3.29 reads every pin where it is. Pins in columns 0 / 6 move once (MenuLayout.fold).
G7_COLS, G7_ROWS, G7_CR, G7_CC, G7_OFF = 7, 5, 2, 3, 1
G7_N = G7_COLS * G7_ROWS
OLD_COLS, OLD_CR, OLD_CC = 9, 1, 4            # the 0.3.28 main view: 9 wide, its centre (the mouse spot) row 1 column 4 = slot 13
assert HG_CENTRE == 12 and G7_CR * G7_COLS + G7_CC == 17 and HG_CC + G7_OFF == G7_CC and HG_CR == G7_CR and HG_ROWS == G7_ROWS \
    and OLD_CR * OLD_COLS + OLD_CC == 13
HUB_DEFTAB = {"character": "skills",         # Skyy 2026-10-15 "id do skills as the default one for this" (hub:def element 3)
              "world": "teleport"}            # 0.3.30: World IS its Teleport page (Skyy 10-16 "world and teleport ... do the same thing"): one entry
HOME_TITLE, HOME_ICON = "Home", MENU_ITEM_ID  # hub:def:home - row 1's first button wears the SkyWynn Menu item itself
OWN_LABEL = {"layout": "Edit shortcuts"}      # Settings > Menu layout is now Edit shortcuts (it opens Home in edit mode)
HUB_BLURB = {"character": "Character hub: your stats, skills, trees, class, pets, Void Charms, collections and profiles.",
             "storage": "Storage hub: the Void, Requip and your Vault (the Bank's coins are in it).",   # 0.3.34
             "market": "Market hub: the Bazaar, the Auction House and Merchants.",
             "smithing": "Crafting hub: the crafter, Smithing, the Anvil (reforge, identify) and Upgrade (your tools).",   # 0.3.34
             "world": "World hub: teleports, your island, exploring and quests.",
             "social": "Social hub: players online, your party and your guild.",
             "settings": "Settings hub: your settings, the HUD, Edit shortcuts and (admins) Server Setup."}
assert sorted(HUB_BLURB) == sorted(SUI.HUBS) and all(len(v) <= 96 for v in HUB_BLURB.values())
# THE ONE-TIME UPDATE (Hubs-Spec 1.3 table): each 0.3.28 tile -> the hub that covers it ("" = not covered: keeps its place; "-" = retired;
# "=<key>" = becomes exactly that shortcut). Skyy 2026-10-15: "so instead of identify and reforge, you have smithing".
MIG = {"yourprofile": "character", "pets": "character", "skills": "character", "accessorybag": "character", "collections": "character",
       "islandmenu": "world", "crafting": "smithing", "reforge": "smithing", "identify": "smithing",
       "bank": "storage", "vault": "storage", "pocketdimension": "storage", "wardrobe": "storage",
       "bazaar": "market", "auctionhouse": "market", "players": "social", "party": "social", "guild": "social",
       "settings": "settings", "hudeditor": "settings", "teleport": "=tab:world:teleport", "hovertooltips": "-",
       "mods": "", "serversetup": ""}
# the tab each old tile IS (Hubs-Spec 1.3): a tab shortcut wears that tile's icon; other tabs wear their hub's icon
_EKEY_KEEP = {"Void Charms": "accessorybag"}   # 0.3.36: a renamed tile keeps its saved key (tile:accessorybag shortcuts stay valid)
_tilekey = lambda n: _EKEY_KEEP.get(n) or re.sub(r"[^a-z0-9]", "", n.lower())
TILE_TAB = {"yourprofile": "character:stats", "pets": "character:pets", "skills": "character:skills", "accessorybag": "character:accessories",
            "collections": "character:collections", "islandmenu": "world:island", "crafting": "smithing:recipes", "reforge": "smithing:reforge",
            "identify": "smithing:identify", "bank": "storage:bank", "vault": "storage:vault", "pocketdimension": "storage:pocket",
            "wardrobe": "storage:requip", "bazaar": "market:bazaar", "auctionhouse": "market:auctions", "players": "social:players",
            "party": "social:party", "guild": "social:guild", "settings": "settings:settings", "hudeditor": "settings:hud",
            "mods": "settings:mods", "serversetup": "settings:setup", "teleport": "world:teleport"}
# the default Home grid: the centre = Teleport (World > Teleport), the 7 hubs one step around it (Skyy: "the hub row" + "plus shape")
# 0.3.30: the 5 x 5 default - the same spots round the centre as 0.3.29; World left out (it opens the Teleport page that IS the centre)
BUILTIN_HOME = {12: "tab:world:teleport", 7: "hub:character", 17: "hub:market", 11: "hub:storage", 13: "hub:smithing",
                6: "hub:social", 8: "hub:settings"}
BUILTIN_TP = {11: "tp:island", 12: "tp:hub", 13: "tp:spawn"}        # the Teleport page: My Island | Hub (centre, as today) | Spawn
TP_KEYS = {"tp:island": "cmdc:island", "tp:hub": "cmdc:hub", "tp:spawn": "spawn"}   # -> the 0.3.28 Teleport view entry with that action
TP_AUTO = list(range(3 * HG_COLS, HG_N))      # warps nobody placed fill the free slots of rows 4 and 5 (paged)
HOME_TXT = {
    "HT_HINT": "Hover a shortcut to read it, click to use it. Edit shortcuts adds, moves and removes them (no dragging).",
    # fix round 2: the Hover Tooltips tile is gone, so the tooltips-off hint names where the switch is (Settings > General)
    "HT_HINT_OFF": "Tooltips are off - turn them on in Settings, General. Click a shortcut to use it. Edit shortcuts: no dragging.",
    "HT_EDIT": "EDITING - no dragging: click a tile, then a slot (they swap), or Remove. Click an empty slot to add one.",
    "HT_EDIT_START": "Edit mode - no dragging: click a tile, then click a slot (they swap). Empty slot = add. Done to finish.",
    "HT_ADD": "Pick what goes in this slot: any hub, page, old tile or teleport. Cancel goes back.",
    "HT_TP_HINT": "Click a place to go there. Arrange moves your tiles: click one, then the slot it goes to (no dragging).",
    "HT_MID": "Shortcuts", "HT_MID_EDIT": "Editing shortcuts - no dragging", "HT_MID_ADD": "Add a shortcut",
    "HT_TILE_BODY": "Click to pick it up, then click the slot where it should go (the two swap).\nNo dragging - click, then click. Remove takes it off.",
    "HT_PICK_FOOT": "Click to pick it up",
    "HT_SWAP_FOOT": "Click to swap it with the picked-up tile",
    "HT_SEL_BODY": "Picked up - now click the slot where it should go.\nClick it again to cancel, or press Remove.",
    "HT_SEL_FOOT": "Click again to cancel",
    "HT_EMPTY_NAME": "Empty slot",
    "HT_EMPTY_ADD": "A free slot. Click it to add a shortcut here:\nany hub, any page, an old tile or a teleport.",
    "HT_EMPTY_MOVE": "A free slot. Click it to move the picked-up tile here.",
    "HT_EMPTY_FOOT_ADD": "Click to add a shortcut",
    "HT_EMPTY_FOOT_MOVE": "Click to move it here",
    "HT_NONE_LEFT": "Every shortcut is on your grid already.",
    "HT_YOU_TITLE": "You", "HT_YOU_HINT": "Click for all your stats", "HT_NOW_TITLE": "Right now",
    "AL_MIG": "Menu updated: hubs replaced old tiles", "AL_SET": "Your settings could not be read",
    "HT_NOW_NONE": "Nothing waiting",                                 # 0.3.30: the Right now panel with nothing to do
    "AL_SPILL": "Some shortcuts did not fit",                         # 0.3.30: the 5 x 5 update had more pins than slots
}
assert "no dragging" in HOME_TXT["HT_EDIT"].lower() and "no dragging" in HOME_TXT["HT_TILE_BODY"].lower() \
    and "no dragging" in HOME_TXT["HT_EDIT_START"].lower() and "no dragging" in HOME_TXT["HT_MID_EDIT"].lower() \
    and all("no dragging" in HOME_TXT[_k].lower() for _k in ("HT_HINT", "HT_HINT_OFF", "HT_TP_HINT")), \
    "0.3.29 (Skyy LOCKED 2026-10-10): every edit text - and the hint beside the Edit button, before it is clicked - says dragging does not work"
AL_MAX, AL_SHOW = 40, 8                      # an alert line: at most 40 characters (fits its 252 px button at 11 px); at most 8 lines (3 per mod)
# ---- 0.3.30: ONE ICON PER PAGE. TAB_ICON = every contract tab's icon item: the old tile's icon where the tab IS an old tile (TILE_TAB),
# else its wave-3 icon. A page shown under several keys (tab / old tile / the hub whose default tab it is) is ONE entry with one icon.
VT_SKIP = ("smithing:multitool",)             # Skyy 2026-10-15 (art/hub-tab-icons README v1.1): "we scrapped the multitool menu"
TAB_ICON = {}
for _k, _t in TILE_TAB.items():
    TAB_ICON[_t] = [e[2] for e in ENTRIES if e[0] == "main" and _tilekey(e[3]) == _k][0]
TAB_ICON.update({"character:trees": "Skyy_Menu_Icon_Trees", "character:class": "Skyy_Menu_Icon_Class", "character:profiles": "Skyy_Menu_Icon_Profiles",
                 "smithing:gear": "Skyy_Menu_Icon_Gear", "smithing:upgrade": "Skyy_Menu_Icon_Upgrade", "world:explore": "Skyy_Menu_Icon_Explore",
                 "world:quests": "Skyy_Menu_Icon_Quests", "market:merchants": "Skyy_Menu_Icon_Merchants", "settings:layout": "Skyy_Menu_Icon_Layout",
                 "storage:supplies": "Skyy_Menu_Icon_Supplies"})   # 0.3.38
_ctabs = ["%s:%s" % (_r[0], _r[1]) for _r in SUI.HUB_TABS]
assert sorted(TAB_ICON) == sorted(_t for _t in _ctabs if _t not in VT_SKIP) and all(_v in ICON_ITEMS for _v in TAB_ICON.values()), \
    "0.3.30: every contract tab (but Multitool) has our icon item: %s" % sorted(set(TAB_ICON) ^ set(_ctabs))
# THE NO-DUPLICATE CHECK: the 7 hubs + every contract tab (the old tiles are those tabs) + the 3 teleports = one icon item each
_ICON_USE = [("hub:" + _h, HUB_ICON_ITEM[_h]) for _h in SUI.HUBS] + [("tab:" + _t, _i) for _t, _i in sorted(TAB_ICON.items())] + \
    [("tp:island", "Skyy_Menu_Icon_MyIsland"), ("tp:hub", "Skyy_Menu_Icon_Hub"), ("tp:spawn", "Skyy_Menu_Icon_Spawn")]
_dup = [(_i, [_e for _e, _j in _ICON_USE if _j == _i]) for _i in sorted(set(_j for _e, _j in _ICON_USE)) if [_j for _e, _j in _ICON_USE].count(_i) > 1]
assert not _dup and MENU_ITEM_ID not in [_j for _e, _j in _ICON_USE], "0.3.30: an icon item names two pages: %s" % _dup
print("0.3.30 one icon per page: %d entries, %d icon items, none shared" % (len(_ICON_USE), len(set(_j for _e, _j in _ICON_USE))))
# ---- 0.3.30: STAND-IN TABS (Skyy 2026-10-16 "smithing still working" - the Smithing hub said "coming soon"): every contract tab not owned by
# SkyyMenu, with a command, that its owner did not put (SkyyGear has no hub tabs) - put by SkyyMenu only while the key is free, visible only
# while the command exists; open = the owner's bridge Function where it has one (VT_FN), else the command as the player (kit HubBar.open)
VT = [(_h, _t, _o, _l, _c) for _h, _t, _o, _m, _l, _c in SUI.HUB_TABS if _m != "SkyyMenu" and _c and "%s:%s" % (_h, _t) not in VT_SKIP]
VT_FN = {"smithing:gear": ("gear:fn:smithing", "craft"), "smithing:reforge": ("gear:fn:smithing", "reforge"),
         "smithing:upgrade": ("gear:fn:smithing", "upgrade"), "smithing:identify": ("gear:fn:smithing", "identify")}
assert all(_k in ["%s:%s" % (_r[0], _r[1]) for _r in VT] for _k in VT_FN) and ("smithing", "gear", 10, "Gear", "smithing") in VT, \
    "0.3.30: the Smithing hub's first stand-in tab runs /smithing (SkyyGear's Craft / Anvil / Upgrade / Identify page)"
# 0.3.31: the Crafting hub's row 2 = Crafting (the /craft crafter; SkyySacks 0.8.11 puts the real tab with this label + order) + Smithing
VT_LABEL31 = {"smithing:recipes": "Crafting", "smithing:gear": "Smithing"}
VT_ORDER31 = {"smithing:recipes": 5}
VT = [(_h, _t, VT_ORDER31.get("%s:%s" % (_h, _t), _o), VT_LABEL31.get("%s:%s" % (_h, _t), _l), _c) for _h, _t, _o, _l, _c in VT]
assert ("smithing", "recipes", 5, "Crafting", "craft") in VT and ("smithing", "gear", 10, "Smithing", "smithing") in VT
# 0.3.33: a MERGED contract tab gets no stand-in (Class is part of Trees - SkyyClasses 0.1.33 puts its own merged tab)
VT = [_r for _r in VT if SUI.hub_merged_host(_r[0], _r[1]) is None]
assert ("character", "class") not in [(_r[0], _r[1]) for _r in VT]
# 0.3.34: Identify (part of the Anvil) and the Auction House (part of Market) get no stand-in; every stand-in wears the kit's label now
assert ("smithing", "identify") not in [(_r[0], _r[1]) for _r in VT] and ("market", "auctions") not in [(_r[0], _r[1]) for _r in VT]
VT = [(_h, _t, _o, SUI.hub_tab_label(_h, _t) or _l, _c) for _h, _t, _o, _l, _c in VT]
assert ("smithing", "reforge", 30, "Anvil", "reforge") in VT and ("smithing", "gear", 10, "Smithing", "smithing") in VT
assert len(set((_h, _o) for _h, _t, _o, _l, _c in VT)) == len(VT), "0.3.31: no two stand-in tabs of one hub share an order"
# the tab icon art (art/hub-tab-icons, our own; README there) shipped at the kit 1.6 hook path Common/UI/Custom/SkyyHubTabs/<hub>_<tab>@2x.png
TAB_ART_DIR = "art/hub-tab-icons"
_TAM = json.load(open(os.path.join(HERE, "..", *(TAB_ART_DIR + "/manifest.json").split("/")), encoding="utf8"))
TAB_ART = sorted("%s_%s" % (_i["hub"], _i["tab"]) for _i in _TAM["icons"] if _i["hub"] != "hubrow")
# 0.3.37: tab pictures drawn elsewhere (Skyy 2026-10-17 "Also use the new amulet on the Character hub Void Charms tab?" -> "Yes"):
# tab -> (art folder, its manifest); the pair is <folder>/hub-tab/<hub>_<tab>(_on).png
TAB_ART_OVER = {"character_accessories": ("art/void-charms-icon", json.load(open(os.path.join(HERE, "..", "art", "void-charms-icon", "manifest.json"), encoding="utf8")))}
assert all(_k in TAB_ART for _k in TAB_ART_OVER)
# 0.3.39: Supplies has its picture pair (art/hub-tab-icons storage_supplies) - the 0.3.38 TAB_NO_ART exemption is gone
assert TAB_ART == sorted(_t.replace(":", "_") for _t in TAB_ICON), "0.3.30: one tab icon picture per contract tab (no Multitool)"
assert "storage_supplies" in TAB_ART, "0.3.39: the Supplies tab picture"

# ================= build-time checks: icons exist, text is safe, slots are sane =================
ASSETS = zipfile.ZipFile(ASSETS_ZIP)   # 0.3.26: the cached copy
ITEMS = {}
for _n in ASSETS.namelist():
    if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
        ITEMS[os.path.basename(_n)[:-5]] = _n
COMMON = set(n for n in ASSETS.namelist() if n.startswith("Common/"))

def need_item(iid):
    if iid in ICON_ITEMS or iid == MENU_ITEM_ID:   # 0.3.11: our icon-only items; 0.3.15: the menu item (shipped by this jar, checked below)
        return
    assert iid in ITEMS, "unknown vanilla item id: %s (not in Assets.zip)" % iid
for _iid, (_art, _rel, _man, _nm, _lk) in ICON_ITEMS.items():
    assert _iid not in ITEMS and _iid.startswith("Skyy_Menu_Icon_"), "0.3.11: icon item id %s must be ours, never a vanilla id" % _iid
    assert "Common/" + _rel not in COMMON, "0.3.11: icon item %s would override the vanilla file %s" % (_iid, _rel)
    assert _lk in ITEMS, "0.3.11: icon item %s borrows the look of an unknown item %s" % (_iid, _lk)
    icon_item_png(_iid)
# 0.3.15: the menu item's own look - an id of ours, its files ours (the art manifest), never a vanilla path; its keys = vanilla item keys
assert MENU_ITEM_ID not in ITEMS and MENU_ITEM_ID not in ICON_ITEMS, "0.3.15: the menu item id %s must be ours" % MENU_ITEM_ID
for _f in MENU_ART_FILES:
    assert "Common/" + MENU_ITEM_FIELDS[_f] not in COMMON, "0.3.15: the menu item's %s would override the vanilla file %s" % (_f, MENU_ITEM_FIELDS[_f])
    assert MENU_ITEM_FIELDS[_f].split("/")[-1].startswith("Skyy_Menu"), "0.3.15: the menu item's %s file is named after it" % _f
    menu_art_file(_f)
_vh = json.loads(ASSETS.read(ITEMS[MENU_ITEM_KEYS_FROM]).decode("utf-8-sig"))
assert "Parent" not in _vh and set(MENU_ITEM_FIELDS) <= set(_vh), "0.3.15: every menu item field is a key of the vanilla %s: %s" % (
    MENU_ITEM_KEYS_FROM, sorted(set(MENU_ITEM_FIELDS) - set(_vh)))
for _k in ("Scale", "PlayerAnimationsId", "IconProperties"):
    assert MENU_ITEM_FIELDS[_k] == _vh[_k], "0.3.15: the menu item's %s = the Voidheart's (same pose / size / icon framing): %r" % (_k, _vh[_k])
assert set(MENU_ITEM_FIELDS["Light"]) == set(_vh["Light"]) and MENU_ITEM_FIELDS["Light"]["Radius"] == _vh["Light"]["Radius"], \
    "0.3.15: the menu item's Light = the Voidheart's keys + radius (only the colour is ours)"
assert re.match(r"^#[0-9a-fA-F]{3}$", MENU_ITEM_FIELDS["Light"]["Color"]) and re.match(r"^#[0-9a-fA-F]{3}$", _vh["Light"]["Color"]), \
    "0.3.15: the glow colour is written like the Voidheart's (#rgb)"

VISUAL_KEYS = ("Model", "Texture", "IconProperties", "Scale", "PlayerAnimationsId", "ItemSoundSetId", "Light")
def look_of(iid):
    """icon + held look of a vanilla item (follows Parent, the child's value wins); files checked to exist under Common/"""
    out, cur, seen = {}, iid, 0
    while cur and seen < 8:
        need_item(cur)
        d = json.loads(ASSETS.read(ITEMS[cur]).decode("utf-8-sig"))
        for k in VISUAL_KEYS + ("Icon",):
            if k in d and k not in out:
                out[k] = d[k]
        cur = d.get("Parent"); seen += 1
    for k in ("Model", "Texture", "Icon"):
        assert k in out, "no %s for %s" % (k, iid)
        assert "Common/" + out[k] in COMMON, "missing %s file for %s: %s" % (k, iid, out[k])
    return out

def txt(s):
    """player-facing text: < > become [ ] (tooltip markup), forbidden characters fail the build"""
    s = s.replace("<", "[").replace(">", "]")
    for bad in ('"', "{", "}", ";", "\\"):
        assert bad not in s, "character %r not allowed in menu text: %s" % (bad, s)
    return s

for ic in (ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_WARP_LOCKED, ICON_NO_WARPS, ICON_PLAYER) + ((FILLER_ICON,) if FILLER_ICON else ()):   # 0.3.15: the menu item look is ours (no vanilla look id here)
    need_item(ic)
VIEW_KEYS = [v[0] for v in VIEWS]
NAV = {45, 48, 49, 50}
used = {}
for view, slot, icon, name, lines, foot, act in ENTRIES:
    need_item(icon)
    assert view in VIEW_KEYS, view
    assert 0 <= slot < 54 and slot not in NAV, "slot %d of %s is reserved or out of range" % (slot, name)
    assert (view, slot) not in used, "two entries in slot %d of view %s" % (slot, view)
    used[(view, slot)] = name
    assert act in ("profile", "spawn", "info", "tips", "settings", "admin") or act.split(":", 1)[0] in ("view", "cmd", "cmdc", "bridge"), "bad action " + act
    if act.startswith("view:"):
        assert act[5:] in VIEW_KEYS, act
for view, slots in (("tp", WARP_SLOTS + [NO_WARPS_SLOT]), ("players", PLAYER_SLOTS + [NO_PLAYERS_SLOT]), ("mods", MOD_SLOTS)):
    for s in slots:
        assert (view, s) not in used and s not in NAV, "dynamic slot %d of view %s collides with an entry" % (s, view)
for slot, icon, name, lines, foot, cmd, close in PLAYER_ACTIONS:
    need_item(icon)
    assert slot not in NAV and slot != PLAYER_HEAD_SLOT and 0 <= slot < 54
for m in MODS:
    need_item(m["icon"])
    assert len(m["commands"]) <= 8, "the info box shows 8 command lines, %s has %d" % (m["mod"], len(m["commands"]))
# 0.1.3: the icon PICTURE must exist too (Icon follows Parent like look_of; the grid shows that file)
def need_icon(iid):
    if iid in ICON_ITEMS or iid == MENU_ITEM_ID:   # 0.3.11: the picture ships in this jar (icon_item_png / 0.3.15 menu_art_file checked it)
        return
    cur, hops, icon = iid, 0, None
    while cur and hops < 8 and icon is None:
        need_item(cur)
        d = json.loads(ASSETS.read(ITEMS[cur]).decode("utf-8-sig"))
        icon = d.get("Icon")
        cur = d.get("Parent"); hops += 1
    assert icon and "Common/" + icon in COMMON, "icon picture missing for %s: %s" % (iid, icon)
for _ic in sorted(set([e[2] for e in ENTRIES] + [a[1] for a in PLAYER_ACTIONS] + [m["icon"] for m in MODS] +
                      [ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_WARP_LOCKED, ICON_NO_WARPS, ICON_PLAYER])):
    need_icon(_ic)
_lines = [e[6].split(":", 1)[1] for e in ENTRIES if e[6].split(":", 1)[0] in ("cmd", "cmdc")] + [a[5] for a in PLAYER_ACTIONS]
for _c, _sub, _need in NEEDS_SUB:
    assert _c == _c.lower() and _sub == _sub.lower() and " " not in _c + _sub, "NEEDS_SUB words are single lower-case words"
    assert any(l.split(" ")[:2] == [_c, _sub] for l in _lines), "NEEDS_SUB %s %s matches no menu command" % (_c, _sub)
    txt(_need)
# review 2026-09-24: version-dependent wording (MODS "old", PA_LEGACY) hangs on a NEEDS_SUB line
_subs = [_c + " " + _sub for _c, _sub, _need in NEEDS_SUB]
assert len(set(m["mod"] for m in MODS)) == len(MODS), "a mod is listed twice in MODS"
for m in MODS:
    if "old" in m:
        assert m["old"]["need"] in _subs, "%s: old.need %s is no NEEDS_SUB line" % (m["mod"], m["old"]["need"])
        assert len(m["old"]["commands"]) <= 8, "the info box shows 8 command lines, %s (old) has %d" % (m["mod"], len(m["old"]["commands"]))
for _slot, _need, _name, _plines, _foot in PA_LEGACY:
    assert _slot in [a[0] for a in PLAYER_ACTIONS], "PA_LEGACY slot %d is no player action" % _slot
    assert _need in _subs, "PA_LEGACY need %s is no NEEDS_SUB line" % _need
    assert _plines, "PA_LEGACY slot %d has no text" % _slot
# 0.2 settings data (research/Settings-Spec.md 4.5): 8 tabs, valid unique keys, label <= 40, help <= 90, the torch at main slot 51
KEY_RE = re.compile(r"^[a-z][A-Za-z0-9.]{2,47}$")           # = SetReg.validKey (keys go into properties files: no = : or spaces)
SET_CAT_ID = [t[0] for t in SET_TABS]
assert len(SET_TABS) == 9 and len(set(SET_CAT_ID)) == 9 and SET_CAT_ID[-1] == "general", "9 tabs, general last (unknown ids go there)"
assert SET_CAT_ID[-2] == "messages", "0.3.21: Messages right before General"
for _t in SET_TABS:
    assert re.match(r"^[A-Za-z]+$", _t[1]), "tab button text must be one plain word (it is inline UI text): " + _t[1]
    assert _t[2] and _t[3], "tab %s needs a header and an always-shown line" % _t[0]
SET_ORDER = [k[0] for k in SET_KNOWN]
assert len(set(SET_ORDER)) == len(SET_ORDER), "a settings key is listed twice"
for _k, _cat, _label, _help, _by in SET_KNOWN:
    assert KEY_RE.match(_k), "bad settings key " + _k
    assert _cat in SET_CAT_ID, "settings key %s: unknown tab %s" % (_k, _cat)
    assert 0 < len(_label) <= 40, "label of %s is %d characters (max 40)" % (_k, len(_label))
    assert 0 < len(_help) <= 90, "help line of %s is %d characters (max 90)" % (_k, len(_help))
# 0.3.3: Skyy answered "block" (2026-09-25): the three refusing General switches are known, in Settings-Spec 2.2 order - party.invites is
# the FIRST General row, then tpa.requests before tpa.updates before msg.private
_gen = [k[0] for k in SET_KNOWN if k[1] == "general"]
assert _gen and _gen[0] == "party.invites", "party.invites is the first General row (Settings-Spec 2.2)"
assert _gen.index("tpa.requests") < _gen.index("tpa.updates") < _gen.index("msg.private"), "General order: tpa.requests, tpa.updates, msg.private"
# 0.3.21: SkyyHud's message-route switches, ranked after SET_ORDER (SetReg.rank): per kind the "shown" switch, then its "feed" switch
MSG_KINDS = ['pickup', 'drop', 'skillxp', 'levelup', 'coins', 'collection', 'rankup', 'quest', 'heal', 'petxp', 'ability']
SET_ORDER_MSG = [k for _mk in MSG_KINDS for k in ("msg." + _mk, "msg." + _mk + ".feed")]
assert len(SET_ORDER_MSG) == 22 and not (set(SET_ORDER_MSG) & set(SET_ORDER)) and all(KEY_RE.match(_k) for _k in SET_ORDER_MSG)
assert not [k for k in SET_KNOWN if k[1] == "messages"], "0.3.21: SkyyHud's rows are not SET_KNOWN entries"
SET_TAB_ROWS = [(t[0], len([k for k in SET_KNOWN if k[1] == t[0]]) + (len(SET_ORDER_MSG) if t[0] == "messages" else 0)) for t in SET_TABS]
assert all(n <= 3 * SET_ROWS for _c, n in SET_TAB_ROWS), "a tab would need more than 3 pages: %s" % SET_TAB_ROWS
OWN_SETTINGS = [k for k in SET_KNOWN if k[4] == "SkyyMenu"]
assert TIPS_KEY in [k[0] for k in OWN_SETTINGS], "the Hover Tooltips key must be one of SkyyMenu's own settings"
assert 1 <= SET_ROWS <= 8
for _n, _t in SET_TXT.items():
    assert _t and "\n" not in _t, "SET_TXT %s" % _n
# 0.3.16: layout D - Settings at main slot 17 (right bar, row 1; 0.3.3 - 0.3.15: slot 39 left of Mods), Mods at 35
assert used.get(("main", 17)) == "Settings" and used.get(("main", 35)) == "Mods", "0.3.16: layout D puts Settings at main 17 and Mods at 35"
assert ("main", 51) not in used, "main slot 51 is free since 0.3.3 (the torch moved to 39)"
# 0.3.3: Identify right of Reforge (SkyyGear spec 7.3.2)
assert used.get(("main", 30)) == "Reforge" and used.get(("main", 31)) == "Identify", "0.3.16: Reforge at main slot 30, Identify at 31 (layout D)"
assert [e for e in ENTRIES if e[:3] == ("main", 31, "Skyy_Menu_Icon_Identify") and e[6] == "cmdc:identify"], "Identify runs /identify"
assert [e for e in ENTRIES if e[:2] == ("main", 30) and e[6] == "cmdc:reforge" and "modifiers" in e[4][0] and "tool" not in e[4][0]], \
    "Reforge text is SkyyGear's (weapons and armor, modifiers)"
assert [e for e in ENTRIES if e[6] == "settings"] and all(e[0] == "main" for e in ENTRIES if e[6] == "settings")
assert [e for e in ENTRIES if e[6] == "cmdc:ah"], "the Auction House entry runs /ah"
# the defaults template (settings-defaults.properties, written once when missing): every known key commented out, grouped by tab
_tl = ["# Server-wide defaults for /settings (SkyyMenu). A player's own choice always wins; Reset all to defaults returns them here.",
       "# Remove the # in front of a line and set true or false. The file is read again within 30 s. Bad lines are ignored (see the log).",
       "# Only switches of installed, updated mods show up in game. Menu hover tooltips OFF for everyone: menu.tooltips=false"]
for _t in SET_TABS:
    _keys = [k for k in SET_KNOWN if k[1] == _t[0]]
    if not _keys:
        continue
    _tl.append("")
    _tl.append("# ---- " + _t[2])
    for _k in _keys:
        _tl.append("#%s=true" % _k[0])
SET_TEMPLATE = "\n".join(_tl) + "\n"
assert "@" not in SET_TEMPLATE
# 0.3 Server Setup data (research/Server-Setup-Spec.md 2.2, 2.11, 2.12)
assert used.get(("main", 44)) == "Server Setup", "0.3.16: Server Setup at main slot 44, under Mods on the right bar (layout D)"
assert [e for e in ENTRIES if e[6] == "admin"] and all(e[0] == "main" for e in ENTRIES if e[6] == "admin")
assert re.match(r"^[a-z][a-z0-9]*(\.[a-z0-9]+)+$", ADMIN_NODE) and re.match(r"^[a-z][a-z0-9]*(\.[a-z0-9]+)+$", MENU_CFG_NODE)
for _m in MODS:
    assert "config" in _m and "reload" in _m and "note" in _m, "%s: every MODS entry needs config / reload / note (spec 2.11)" % _m["mod"]
    for _f in [x for x in _m["config"].split(",") if x]:
        assert re.match(r"^Skyy_[A-Za-z]+/[A-Za-z0-9_.-]+$", _f), "%s: config path %r must be Skyy_<Folder>/<file>" % (_m["mod"], _f)
    assert _m["reload"] == "" or re.match(r"^[a-z]+( [a-z]+)*$", _m["reload"]), "%s: reload must be a command line like tree reload" % _m["mod"]
    assert _m["config"] or _m["note"], "%s: a mod without a config file needs a note that says so" % _m["mod"]
    assert len(_m["note"]) <= 90 and '"' not in _m["note"], "%s: note too long" % _m["mod"]
    for _a in _m.get("admin", []):
        assert "(admin)" in _a or "(staff)" in _a, "%s: admin lines say (admin)" % _m["mod"]
for _n, _t in ADM_TXT.items():
    assert _t and "\n" not in _t and '"' not in _t, "ADM_TXT " + _n
assert "@" not in MENU_CFG_TEXT and all(ord(c) < 127 for c in MENU_CFG_TEXT)
# the file-only lines of the Mods section (spec 2.4 / 2.11)
def adm_fline(m):
    fs = [x for x in m["config"].split(",") if x]
    if not fs:
        return m["note"]
    t = "File only: " + fs[0] + (" and %d more" % (len(fs) - 1) if len(fs) > 1 else "")
    if m["reload"]:
        return t + " - after editing: /" + m["reload"]
    return t + (" - " + m["note"] if m["note"] else "")
MOD_FLINE = [adm_fline(m) for m in MODS]
for _l in MOD_FLINE:
    assert len(_l) <= 120, "file-only line too long: " + _l
MOD_ADMIN = ["\n".join([c.replace("%ALIASES%", "") for c in m["commands"] if "(admin)" in c or "(staff)" in c] + m.get("admin", []))
             for m in MODS]

# 0.3.1: "setup" = (first version with a Server Setup page, its page title, what is on it) - the fallback text while that mod publishes
# no config:def (an older version, or it failed to start); "admin" = lines only admins see in the Mods view (and on the file-only page)
VER_RE = re.compile(r"^\d+(\.\d+){1,3}$")
def ver_t(v):
    return tuple(int(x) for x in v.split("."))
# 0.3.5: THE ONE VERSION TABLE - MODS_VERSIONS names exactly the MODS mods (SkyyMenu's own entry = VERSION) and every entry reads it
_tbl_mods = sorted(m["mod"] for m in MODS if m["mod"] != "SkyyMenu")
assert sorted(MODS_VERSIONS) == _tbl_mods, "MODS_VERSIONS and MODS name different mods: %s" % sorted(set(MODS_VERSIONS) ^ set(_tbl_mods))
for _m in MODS:
    _want = VERSION if _m["mod"] == "SkyyMenu" else MODS_VERSIONS[_m["mod"]]
    assert _m["version"] == _want and VER_RE.match(_want), "%s: version %r, the table says %r" % (_m["mod"], _m["version"], _want)
for _m in MODS:
    if "setup" in _m:
        _since, _title, _what = _m["setup"]
        assert VER_RE.match(_since), "%s: setup version %r" % (_m["mod"], _since)
        assert _m["mod"] == "SkyyMenu" or ver_t(_since) <= ver_t(_m["version"]), "%s: setup %s is newer than %s" % (_m["mod"], _since, _m["version"])
        assert 0 < len(_title) <= 24 and 0 < len(_what) <= 60, "%s: setup title <= 24 and what <= 60 characters" % _m["mod"]
        txt(_title); txt(_what)
        assert _m["config"], "%s: a mod with a Server Setup page names its file(s)" % _m["mod"]
    # "(admin)" / "(staff)" in every admin line: the 0.3 check above (MODS "admin" loop of the Server Setup data checks) still runs
    for _a in _m.get("admin", []):
        assert len(txt(_a.replace("%ALIASES%", ""))) <= 80, "%s: admin line longer than 80 characters: %s" % (_m["mod"], _a)
        assert _a not in _m["commands"], "%s: admin line is also a Commands line (admins would read it twice): %s" % (_m["mod"], _a)
    assert _m["commands"], "%s needs at least one line under Commands" % _m["mod"]
assert len(MODS) <= len(MOD_SLOTS), "every mod fits on one Mods page (%d mods, %d slots)" % (len(MODS), len(MOD_SLOTS))

# 0.3.2: every class text names the 7-class roster and the five weapon skills (CLASS_PLAYABLE / CLASS_LATER / CLASS_SKILLS)
assert len(CLASS_PLAYABLE) == len(CLASS_SKILLS) and not set(CLASS_PLAYABLE) & set(CLASS_LATER)
_bym = dict((m["mod"], m) for m in MODS)
for _n in CLASS_PLAYABLE + CLASS_LATER:
    assert _n in _bym["SkyyClasses"]["desc"], "SkyyClasses desc must name the class %s" % _n
# 0.3.9: "later" only while CLASS_LATER names a class (all seven are playable since SkyyClasses 0.1.14)
assert ("later" in _bym["SkyyClasses"]["desc"]) == bool(CLASS_LATER), "SkyyClasses desc says 'later' exactly when a class comes later"
assert "Shaman" not in " ".join(m["desc"] for m in MODS) + " ".join(" ".join(e[4]) for e in ENTRIES), "0.3.9: no Mods / menu text names the Shaman"
for _n in CLASS_PLAYABLE:
    assert _n in _bym["SkyyProfiles"]["desc"], "SkyyProfiles desc must name the playable class %s" % _n
_skills_entry = [e for e in ENTRIES if e[0] == "main" and e[3] == "Skills"]
assert len(_skills_entry) == 1, "one Skills entry in the main menu"
for _sk in CLASS_SKILLS:
    assert _sk in _bym["SkyySkills"]["desc"], "SkyySkills desc must name the class skill %s" % _sk
    assert _sk in _skills_entry[0][4][0], "the Skills menu entry must name the class skill %s" % _sk
assert [c for c in _bym["SkyyClasses"]["commands"] if c.startswith("/class kit ")], "SkyyClasses Commands list /class kit (players)"
assert [a for a in _bym["SkyyClasses"].get("admin", []) if a.startswith("/classadmin kit ")], "SkyyClasses admin lines list /classadmin kit"
assert not [c for c in _bym["SkyyClasses"]["commands"] if c.startswith("/classadmin kit")], "/classadmin kit is an admin-only line"
_alltext = " ".join([m["desc"] + " " + " ".join(m["commands"] + m.get("admin", [])) for m in MODS] +
                    [" ".join(e[4]) for e in ENTRIES] + [t[3] for t in SET_TABS] + [k[3] for k in SET_KNOWN])
assert "Warrior or Mage" not in _alltext, "the old 3-class wording is gone"
for _t in SET_TABS:
    assert len(_t[3]) <= 121, "always-shown line of tab %s is %d characters (one unwrapped label, max 121 = the General line of 0.3.1)" % (_t[0], len(_t[3]))
# 0.3.3: round data - MODS names every round version, a retired mod is out of MODS and replaced by a MODS entry
for _rm, (_rfrom, _rto) in ROUND_PINS.items():
    assert _rm in _bym and _bym[_rm]["version"] == _rto and VER_RE.match(_rto), "ROUND_PINS %s: MODS must name %s" % (_rm, _rto)
    assert _rfrom is None or (VER_RE.match(_rfrom) and ver_t(_rfrom) < ver_t(_rto)), "ROUND_PINS %s" % _rm
for _rm, (_rv, _by) in ROUND_RETIRED.items():
    assert _rm not in _bym and _by in _bym and VER_RE.match(_rv) and _rm not in ROUND_PINS, "ROUND_RETIRED %s" % _rm
# 0.3.3: the SkyyGear entry (spec 7.3.2 item 1) and the round 8 + 9 texts the notes named (tools/menu_0_3_3_patch.py 5)
_g = _bym["SkyyGear"]
for _c in ("/reforge ", "/identify ", "/gear "):
    assert [c for c in _g["commands"] if c.startswith(_c)], "SkyyGear Commands list %s" % _c.strip()
for _sub in ("give", "read", "reroll", "clear", "rarity", "unid", "identify", "level", "gate", "migrate"):
    assert [a for a in _g["admin"] if a.startswith("/gear ") and (" " + _sub + " " in a or " " + _sub + " |" in a)], "SkyyGear admin line /gear %s" % _sub
assert _g["setup"][1] == "Gear" and _g["config"] == "Skyy_SkyyGear/config.properties" and _g["check"] == "gear"
_ess = _bym["SkyyEssentials"]
_esst = " ".join([_ess["desc"], _ess["setup"][2]] + _ess["commands"] + _ess["admin"])
assert "spawn" not in _esst and [a for a in _ess["admin"] if a.startswith("/warpadmin ") and "Warps page" in a], "Essentials: no world spawn, /warpadmin = Warps"
assert "privacy.staffBypass" in _ess["desc"] and "staff bypass" in _ess["setup"][2], "Essentials names the staff bypass row"
assert [a for a in _bym["SkyyParty"]["admin"] if "privacy.staffBypass" in a] and "privacy.staffBypass" in _bym["SkyyParty"]["desc"], "Party names privacy.staffBypass"
assert [c for c in _bym["SkyyClasses"]["commands"] if c.startswith("/class arrows ")] and "hotbar at once" in _bym["SkyyClasses"]["desc"]
assert "Omni" in _bym["SkyySacks"]["desc"] and "Rare" in _bym["SkyySacks"]["desc"] and "Legendary" in _bym["SkyyCollections"]["desc"]
_alltext3 = " ".join([m["desc"] + " " + " ".join(m["commands"] + m.get("admin", [])) for m in MODS] + [" ".join(e[4]) for e in ENTRIES])
for _stale in ("type it twice", "on its way", "31 s", "world spawn", "SkyyRolls", "/rolls"):
    assert _stale not in _alltext3, "stale menu text: " + _stale
# 0.3.5: the help texts of the 2026-10-01 / 2026-10-02 builds (tools/menu_0_3_5_patch.py 3) - command names as their build scripts define them
_mb = _bym["SkyyMobs"]
assert _mb["check"] == "mobs" and _mb["setup"][1] == "Mobs" and _mb["reload"] == "mobs reload", "SkyyMobs: /mobs, Server Setup Mobs"
assert [c for c in _mb["commands"] if c.startswith("/mobs (or /mobs info) ")], "SkyyMobs Commands: /mobs (or /mobs info)"
for _sub in ("inspect", "set", "platetest", "reload"):
    assert [a for a in _mb["admin"] if a.startswith("/mobs " + _sub + " ")], "SkyyMobs admin line /mobs %s" % _sub
assert [a for a in _g["admin"] if a.startswith("/gear relevel ")] and "its own level" in _g["desc"], "SkyyGear 0.2: item levels, /gear relevel"
assert [c for c in _bym["SkyySkills"]["commands"] if c.startswith("/skills mana ") and "(admin)" in c], "SkyySkills 0.4.12: /skills mana (admin)"
assert "own XP curve" in _bym["SkyySkills"]["desc"] and "in combat" in _bym["SkyySkills"]["desc"], "SkyySkills 0.4.12: class curve, combat Mana"
_upb = _bym["SkyyUiProbe"]
assert [a for a in _upb["admin"] if a.startswith("/skyprobe win | secgrid ")] and not [c for c in _upb["commands"] if "/skyprobe" in c], \
    "SkyyUiProbe 0.3: /skyprobe win | secgrid, admins only"
_sk3 = _bym["SkyySacks"]
assert [c for c in _sk3["commands"] if c.startswith("Stack refill ")] and "add up" in _sk3["desc"] and "Benches, inventory crafting" in _sk3["desc"], \
    "SkyySacks 0.7.11 - 0.7.12: stack refill, bags add up, benches + inventory crafting"
assert "Coins never buy" in _bym["SkyyCollections"]["desc"], "SkyyCollections 0.2.5: coins never buy tiers"
assert "can't be traded" in _ess["desc"] and [c for c in _ess["commands"] if c.startswith("/trade ") and "no Magic Bags" in c], \
    "SkyyEssentials 0.1.7: no Magic Bags in /trade"
assert "skills" in _bym["SkyyHud"]["desc"] and "Overall Level" in _bym["SkyyHud"]["desc"], "SkyyHud 0.3.11: the Skills widget"
assert "Craft tab of Void Charms" in _bym["SkyyAccessories"]["desc"] and "leaves or is kicked" in _bym["SkyyGuilds"]["desc"], \
    "SkyyAccessories 0.5.2 Workbench tab, SkyyGuilds 0.1.6 leave refund"
assert "&" not in _alltext3, "no raw & in tooltip text (markup not proven)"
# 0.3.6: the help texts of the 2026-10-02 / 2026-10-03 builds (tools/menu_0_3_6_patch.py DATA / TEXT) - command names as SkyyWorldGen 0.1 defines them
_wg = _bym["SkyyWorldGen"]
assert _wg["check"] == "zone" and _wg["setup"][1] == "World Gen" and _wg["reload"] == "zone reload" \
    and _wg["config"] == "Skyy_SkyyWorldGen/config.properties", "SkyyWorldGen: /zone, Server Setup World Gen, its config file"
for _sub in ("- ", "1 ", "info ", "leave ", "setlanding ", "reload "):
    assert [a for a in _wg["admin"] if a.startswith("/zone " + _sub) or ("| " + _sub.strip() + " ") in a], "SkyyWorldGen admin line /zone %s" % _sub
assert not [c for c in _wg["commands"] if "/zone" in c], "SkyyWorldGen 0.1: every /zone command is admin-only (no player Commands line)"
assert [m["mod"] for m in MODS].index("SkyyWorldGen") == [m["mod"] for m in MODS].index("SkyyMobs") + 1, "SkyyWorldGen right after SkyyMobs"
assert "combat indicator" in _bym["SkyyHud"]["desc"], "SkyyHud 0.3.12: the combat indicator"
assert "grows with that level" in _g["desc"] and "damage and armor by level" in _g["setup"][2], "SkyyGear 0.2.1: damage and armor by level"
assert "Stronger mobs pay more kill XP" in _bym["SkyySkills"]["desc"], "SkyySkills 0.4.14: kill XP by mob level"
# 0.3.7: SkyyAccessories 0.5.4 retired Night Vision for the Lantern line - no Mods text names Night Vision any more
assert "the Lantern" in _bym["SkyyAccessories"]["desc"] and "Lantern" in _bym["SkyyAccessories"]["setup"][2], "SkyyAccessories 0.5.4: the Lantern"
assert "night vision" not in (_alltext3 + " " + " ".join(" ".join(m["setup"]) for m in MODS if "setup" in m)).lower(), \
    "0.3.7: no Mods text names Night Vision (retired by SkyyAccessories 0.5.4)"
_ar = _bym["SkyyArmory"]
assert _ar["check"] == "" and _ar["setup"][1] == "Armory" and _ar["reload"] == "" and _ar["config"] == "Skyy_SkyyArmory/config.properties" \
    and not _ar.get("admin") and not [c for c in _ar["commands"] if c.startswith("/")], "SkyyArmory 0.1: no command, Server Setup Armory"
assert [m["mod"] for m in MODS].index("SkyyArmory") == [m["mod"] for m in MODS].index("SkyyGear") + 1, "SkyyArmory right after SkyyGear"
assert [a for a in _bym["SkyyUiProbe"]["admin"] if a.startswith("/skyprobe map")], "SkyyUiProbe 0.4: the /skyprobe map line"
# 0.3.9: the class texts of SkyyClasses 0.1.14 / SkyySkills 0.4.21 / SkyyProfiles 0.1.6 (Assassin + Monk playable)
assert "Monk or Spellblade" in _bym["SkyyClasses"]["desc"] and "Monk or Spellblade" in _bym["SkyyProfiles"]["desc"], "0.3.30: + the Spellblade named"
assert "Zen or Battlemagic" in _bym["SkyySkills"]["desc"] and len(_bym["SkyySkills"]["desc"]) <= 390, "0.3.9: the Skills text (0.3.13: Zen; 0.3.30: Battlemagic)"
assert "Discipline" not in " ".join(m["desc"] for m in MODS) + " ".join(" ".join(e[4]) for e in ENTRIES), "0.3.13: no Mods / menu text names Discipline"
# 0.3.8: the texts of Gear 0.2.3, Skills 0.4.16, Party 0.1.7 / Essentials 0.1.8, Bazaar 0.1.4 and Trees 0.3 - 0.3.2
assert "pays Smithing XP" in _bym["SkyyGear"]["desc"] and "crafting Smithing XP" in _bym["SkyyGear"]["setup"][2], "SkyyGear 0.2.3: craft Smithing XP"
assert "own XP list per skill" in _bym["SkyySkills"]["setup"][2], "SkyySkills 0.4.16: Own XP list per skill"
assert "TPA and Accept TPA" in _bym["SkyyParty"]["desc"] and "also from the party page" in _bym["SkyyEssentials"]["desc"], "SkyyParty 0.1.7 TPA buttons"
assert "about twice" in _bym["SkyyBazaar"]["desc"], "SkyyBazaar 0.1.4: progression prices"
_tr = _bym["SkyyTrees"]
assert "Alchemy, Smithing" in _tr["desc"] and "class tree" in _tr["desc"] and "class trees" in _tr["setup"][2] \
    and [c for c in _tr["commands"] if c.startswith("/tree class ")] and [c for c in _tr["commands"] if c.startswith("/tree probe ") and "(admin)" in c], \
    "SkyyTrees 0.3 - 0.3.2: Alchemy / Smithing, the class tree, /tree class, /tree probe (admin)"
assert "32% stronger" in _bym["SkyyCooking"]["desc"], "SkyyCooking 0.1.4: +32% per Grade"
assert "Difficulty Easy, Normal or Hard" in _mb["desc"] and "health floor" in _mb["desc"] and "health floor" in _mb["setup"][2], \
    "SkyyMobs 0.1.1 - 0.1.2: difficulty ladder, health floor"
assert max(len(m["desc"]) for m in MODS) <= 390, "a Mods description is longer than 390 characters (the tooltip grows too tall; 0.3.5 max 350)"

# 0.3.1: the menu data must follow the live set (tools/deploy_set.py SET) and every live mod's own texts. Differences are printed as
# WARNINGs, never fail the build (a later SET bump must not stop this version from building) - read the build output: it ends the check
# with "menu data matches the live set" when MODS versions, MODS entries, the known switches (label / tab / help) and the Server Setup
# titles all agree with the newest build script of every mod SET pins.
# 0.3.3: the check is ONE function (menu_check) run twice - on SET as tools/deploy_set.py pins it NOW ("the live set") and on the SET the
# main session pins when this round deploys ("this round's set": SET with every ROUND_PINS version, the ROUND_PINS mods the round adds,
# SkyyMenu VERSION, the ROUND_RETIRED mods out of SET and in RETIRED). Both runs must end in "menu data matches". Mods the round adds are
# read too (their switches and Server Setup title), and a round version whose build script does not exist yet is checked against the
# version it replaces (a note).
import ast as _ast
_ds_src = open(os.path.join(B.PROJECT, "tools", "deploy_set.py"), encoding="utf-8").read()
_LIVE = None
_LIVE_RETIRED = []
for _n in _ast.parse(_ds_src).body:
    if isinstance(_n, _ast.Assign) and any(isinstance(_t, _ast.Name) and _t.id == "SET" for _t in _n.targets):
        _LIVE = _ast.literal_eval(_n.value)
    if isinstance(_n, _ast.Assign) and any(isinstance(_t, _ast.Name) and _t.id == "RETIRED" for _t in _n.targets):
        _LIVE_RETIRED = list(_ast.literal_eval(_n.value))
assert _LIVE, "tools/deploy_set.py has no SET list"
_modix = dict((m["mod"], m) for m in MODS)
_known = dict((k[0], k) for k in SET_KNOWN)
# 0.3.3: an optional 6th string argument (a permission node, the 7th registration element) is accepted
_REG = re.compile(r'regSetting\(\s*"([^"]+)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*(true|false|True|False)\s*,\s*"([^"]*)"\s*(?:,\s*"([^"]*)"\s*)?\)')
# 0.3.3 review: a registration node must be plain (= SetReg.validPerm, max 100 characters), else SkyyMenu refuses that key
_NODE_RE = re.compile(r"^[a-z][a-z0-9]*(\.[a-z0-9]+)+$")
_EMIT = re.compile(r'\.emit\(\s*pool\s*,\s*PKG\s*,\s*MOD\s*=\s*"(\w+)"\s*,\s*TITLE\s*=\s*"([^"]+)"')
# 0.3.5: SkyyMobs 0.1 passes its module constant (CFG.emit(pool, PKG, MOD=MOD, TITLE="Mobs"), MOD = "SkyyMobs"): read that constant
_EMIT_VAR = re.compile(r'\.emit\(\s*pool\s*,\s*PKG\s*,\s*MOD\s*=\s*([A-Za-z_]\w*)\s*,\s*TITLE\s*=\s*"([^"]+)"')
_PATCH = "tools/menu_0_3_18_patch.py"


def _emits(t):
    """(MOD, TITLE) of every config kit emit of a build script: MOD="Name", or MOD=<module constant> = "Name" ("?<constant>" if unclear)"""
    out = list(_EMIT.findall(t))
    for _var, _title in _EMIT_VAR.findall(t):
        _c = re.findall(r'^%s\s*=\s*"(\w+)"' % re.escape(_var), t, re.M)
        out.append((_c[0] if len(_c) == 1 else "?" + _var, _title))
    return out


def _script(mod, ver):
    return os.path.join(B.PROJECT, mod, "build_%s_%s.py" % (mod.lower(), ver))


def menu_check(live, retired):
    """the menu data against one SET (list of (mod, version)) + RETIRED list -> (drift, notes, registered switch keys)"""
    drift, notes, keys, cls = [], [], set(), [None]
    livemap = dict(live)
    menu_pin = livemap.get("SkyyMenu", "")
    pinned = bool(VER_RE.match(menu_pin)) and ver_t(menu_pin) >= ver_t(VERSION)     # SET pins this SkyyMenu = the round is pinned

    def scan(mod, m, vers):
        p = None
        for v in vers:
            if os.path.isfile(_script(mod, v)):
                p = _script(mod, v)
                break
        if p is None:
            drift.append("%s: no build script %s" % (mod, os.path.relpath(_script(mod, vers[0]), B.PROJECT)))
            return
        if p != _script(mod, vers[0]):
            notes.append("%s %s: no build script yet (%s) - its switches and Server Setup title are checked against %s" %
                         (mod, vers[0], os.path.relpath(_script(mod, vers[0]), B.PROJECT), os.path.basename(p)))
        t = open(p, encoding="utf-8", errors="ignore").read()
        if mod == "SkyyClasses":
            cls[0] = t
        for _k, _lab, _cat, _def, _hlp, _perm in _REG.findall(t):
            keys.add(_k)
            if _perm and not (len(_perm) <= 100 and _NODE_RE.match(_perm)):
                drift.append("%s: switch %s registers the node %r - not a plain node, SkyyMenu refuses the key" % (mod, _k, _perm))
            _kn = _known.get(_k)
            if _kn is None:
                drift.append("%s registers the player switch %s - not in SET_KNOWN" % (mod, _k))
                continue
            if (_kn[2], _kn[1], _kn[3]) != (_lab, _cat, _hlp):
                drift.append("%s: switch %s is %r / %s / %r in the mod, SET_KNOWN differs" % (mod, _k, _lab, _cat, _hlp))
            if _def.lower() != "true":
                drift.append("%s: switch %s defaults to OFF in the mod" % (mod, _k))
        _em = _emits(t)
        _st = m.get("setup")
        if _em and not _st:
            drift.append("%s has a Server Setup page (%s) but no MODS setup entry" % (mod, _em[0][1]))
        elif _st and not _em:
            drift.append("%s: MODS describes a Server Setup page, its build script publishes none" % mod)
        elif _st and _em and (_st[1] != _em[0][1] or _em[0][0] != mod):
            drift.append("%s: MODS setup page %r, the mod publishes %s %r" % (mod, _st[1], _em[0][0], _em[0][1]))

    for mod, ver in live:
        if mod == "SkyyMenu":
            continue    # its own entry carries VERSION; SET pins the SkyyMenu that is deployed now
        if mod in ROUND_RETIRED:
            rv, by = ROUND_RETIRED[mod]
            if pinned:
                drift.append("%s: SET pins SkyyMenu %s but still %s %s - this round retires it (%s replaces it): drop it from SET and add it "
                             "to RETIRED in tools/deploy_set.py" % (mod, menu_pin, mod, ver, by))
            elif ver == rv:
                notes.append("%s %s leaves SET with this round - %s %s replaces it (MODS lists %s; tools/deploy_set.py: drop %s from SET, "
                             "add it to RETIRED)" % (mod, ver, by, ROUND_PINS[by][1] if by in ROUND_PINS else _modix[by]["version"], by, mod))
            else:
                drift.append("%s: SET pins %s, this round retires %s %s" % (mod, ver, mod, rv))
            continue
        m = _modix.get(mod)
        if m is None:
            drift.append("%s %s is live but not in MODS" % (mod, ver))
            continue
        rp = ROUND_PINS.get(mod)
        vers = [ver]
        if m["version"] != ver:
            if rp and rp[0] == ver and m["version"] == rp[1] and not pinned:
                notes.append("%s: MODS says %s = this round's pin (tools/deploy_set.py SET pins %s until the round deploys; if the round does "
                             "not ship %s %s, set its MODS version back to %s and drop its ROUND_PINS entry in %s)" %
                             (mod, rp[1], ver, mod, rp[1], ver, _PATCH))
                vers = [rp[1], ver]
            elif rp and rp[0] == ver and m["version"] == rp[1]:
                drift.append("%s: SET pins SkyyMenu %s but still %s %s - the round went without %s %s: set its MODS version back to %s "
                             "and drop its ROUND_PINS entry in %s" % (mod, menu_pin, mod, ver, mod, rp[1], ver, _PATCH))
            else:
                drift.append("%s: MODS says %s, the live set runs %s" % (mod, m["version"], ver))
        elif rp and rp[0] is not None and ver == rp[1]:
            vers = [ver, rp[0]]     # the round's version is pinned: its own script, else the replaced version's (with a note)
        scan(mod, m, vers)
    for mod, (frm, to) in sorted(ROUND_PINS.items()):
        if frm is not None or mod in livemap:
            continue
        if pinned:
            drift.append("%s: SET pins SkyyMenu %s but not %s %s - this round adds it: add (%r, %r) to SET" % (mod, menu_pin, mod, to, mod, to))
        else:
            notes.append("%s %s is new with this round (not in SET yet) - its switches and Server Setup title are checked against its "
                         "build script" % (mod, to))
        scan(mod, _modix[mod], [to])
    for mod, (rv, by) in sorted(ROUND_RETIRED.items()):
        if mod not in livemap and mod not in retired:
            drift.append("%s left SET but is not in tools/deploy_set.py RETIRED - its world key would stay enabled next to %s" % (mod, by))
    # 0.3.2: the roster the class texts name = the CLASSES list of the SkyyClasses build script (name, weapon skill, enabled)
    _CL = re.findall(r'\{"name": "(\w+)", "skill": "([^"]+)", "color": "[^"]*", "enabled": (True|False)', cls[0] or "")
    if not _CL:
        drift.append("SkyyClasses: no CLASSES roster found in its build script - check CLASS_PLAYABLE / CLASS_LATER / CLASS_SKILLS by hand")
    else:
        _cp = [(_n, _sk) for _n, _sk, _en in _CL if _en == "True"]
        _cl = [_n for _n, _sk, _en in _CL if _en == "False"]
        if [_n for _n, _sk in _cp] != CLASS_PLAYABLE or [_sk for _n, _sk in _cp] != CLASS_SKILLS or _cl != CLASS_LATER:
            drift.append("SkyyClasses roster is playable %s, later %s - CLASS_PLAYABLE / CLASS_SKILLS / CLASS_LATER and the class texts differ" %
                         (", ".join("%s (%s)" % x for x in _cp), ", ".join(_cl)))
    return drift, notes, keys


def menu_report(label, live, retired):
    drift, notes, keys = menu_check(live, retired)
    for _k in SET_KNOWN:
        if _k[4] != "SkyyMenu" and _k[0] not in keys:
            print("note (%s): known switch %s (%s) is not registered by any mod of that set" % (label, _k[0], _k[4]))
    for _d in notes:
        print("note (%s): %s" % (label, _d))
    for _d in drift:
        print("WARNING menu data (%s): %s" % (label, _d))
    if drift:
        print("WARNING: %d menu data difference(s) with %s - update MENU DATA (%s or its successor)" % (len(drift), label, _PATCH))
    else:
        print("menu data matches %s (%d mods in that SET, %d player switches registered by them, roster %s; later %s)" %
              (label, len(live), len(keys), ", ".join(CLASS_PLAYABLE), ", ".join(CLASS_LATER)))
    return drift


DRIFT = menu_report("the live set", _LIVE, _LIVE_RETIRED)
# 0.3.5: a version differs -> the ONE table for the live SET, ready for the next tools/menu_<ver>_patch.py (nothing is written)
if [_d for _d in DRIFT if "the live set runs" in _d or "is live but not in MODS" in _d]:
    print("MODS_VERSIONS for the live set (paste into the next menu patch, then regenerate): {" +
          ", ".join('"%s": "%s"' % (_m, _v) for _m, _v in _LIVE if _m != "SkyyMenu") + "}")
# the SET the main session pins when this round deploys (tools/deploy_set.py is never edited here)
ROUND_SET = []
for _mod, _ver in _LIVE:
    if _mod in ROUND_RETIRED:
        continue
    if _mod == "SkyyMenu":
        _ver = VERSION
    elif _mod in ROUND_PINS and ROUND_PINS[_mod][0] == _ver:
        _ver = ROUND_PINS[_mod][1]
    ROUND_SET.append((_mod, _ver))
for _mod, (_frm, _to) in sorted(ROUND_PINS.items()):
    if _frm is None and _mod not in dict(ROUND_SET):
        ROUND_SET.append((_mod, _to))
ROUND_SET_RETIRED = sorted(set(_LIVE_RETIRED) | set(ROUND_RETIRED))
print("this round's set: " + ", ".join("%s %s" % x for x in ROUND_SET if dict(_LIVE).get(x[0]) != x[1]) +
      "; retired " + ", ".join(ROUND_SET_RETIRED) + " (everything else as SET pins it now)")
ROUND_DRIFT = menu_report("this round's set", ROUND_SET, ROUND_SET_RETIRED)
# 0.3.4: every MILLISECOND row of the live set (Skyy, LOCKED 2026-10-01: Server Setup shows and takes them in SECONDS, the file keeps ms).
# The jar finds them at run time by the row's unit column (element 8 = "ms" on an int / dec row, AdminPage.msRow); this is the same rule
# read off the live build scripts (kit rows = 11 / 12-element tuples and helper calls like SkyyExploration's crow(...)), plus a WARNING
# for a row whose key reads like milliseconds (..Ms, ..Millis, .._MS) but whose unit is not ms (the menu would show it unconverted).
_KIT_TYPES = {"bool", "int", "dec", "text", "choice", "items", "range", "table", "link", "action", "color"}
_MS_NAME = re.compile(r"(Ms|MS|Millis|MILLIS|millis|_ms)$")


def ms_rows(live):
    """(rows, odd) - rows = (mod, key, type, default, min, max) of every unit-ms kit row; odd = (mod, key, unit) named ms, other unit"""
    rows, odd = [], []
    for mod, ver in live:
        p = _script(mod, ver)
        if mod == "SkyyMenu" or not os.path.isfile(p):
            continue
        for node in _ast.walk(_ast.parse(open(p, encoding="utf-8", errors="ignore").read())):
            if isinstance(node, _ast.Tuple) and len(node.elts) in (11, 12):
                a = [e.value if isinstance(e, _ast.Constant) else None for e in node.elts]
                if not isinstance(a[0], str) or a[3] not in _KIT_TYPES:
                    continue
                key, typ, unit, d, lo, hi = a[0], a[3], a[8], a[4], a[5], a[6]
            elif isinstance(node, _ast.Call) and len(node.args) >= 4:
                a = [e.value if isinstance(e, _ast.Constant) else None for e in node.args]
                if not isinstance(a[0], str) or a[3] not in _KIT_TYPES or " " in a[0]:
                    continue
                kw = dict((k.arg, k.value.value) for k in node.keywords if isinstance(k.value, _ast.Constant))
                key, typ = a[0], a[3]
                unit = "ms" if ("ms" in a[4:] or kw.get("unit") == "ms") else ""
                nums = [x for x in a[4:] if isinstance(x, str) and re.match(r"^-?\d+$", x)]
                d, lo, hi = None, (nums[0] if nums else None), (nums[1] if len(nums) > 1 else None)
            else:
                continue
            if unit == "ms":
                rows.append((mod, key, typ, d, lo, hi))
            elif _MS_NAME.search(key) and typ in ("int", "dec", "range"):
                odd.append((mod, key, unit))
    return rows, odd


MS_ROWS, MS_ODD = ms_rows(_LIVE)
print("seconds rows (unit ms, shown and typed in seconds, the file keeps ms): %d - %s" % (len(MS_ROWS), "; ".join(
    "%s %s" % (m, ", ".join(r[1] for r in MS_ROWS if r[0] == m)) for m in sorted(set(r[0] for r in MS_ROWS)))))
for _m, _k, _u in MS_ODD:
    print("WARNING seconds rows: %s %s reads like milliseconds but its unit is %r - Server Setup shows it as it is" % (_m, _k, _u))
assert MS_ROWS and all(r[2] in ("int", "dec") for r in MS_ROWS), "every unit-ms row of the live set is an int / dec row (range rows keep ms)"
print("settings rows per tab (%d per page): %s" % (SET_ROWS, ", ".join("%s %d%s" % (c, n, " (2 pages)" if n > SET_ROWS else "")
                                                                  for c, n in SET_TAB_ROWS)))

# ================= /menu and /sbmenu only when nothing else uses them (vanilla jar + every Skyy build script) =================
def cp_utf8(data):
    """CONSTANT_Utf8 strings of a class file (minimal constant-pool reader)"""
    if data[:4] != b"\xca\xfe\xba\xbe":
        return set()
    n = struct.unpack(">H", data[8:10])[0]
    i, p, out = 1, 10, set()
    while i < n:
        tag = data[p]; p += 1
        if tag == 1:
            ln = struct.unpack(">H", data[p:p + 2])[0]; p += 2
            out.add(data[p:p + ln].decode("utf-8", "replace")); p += ln
        elif tag in (7, 8, 16, 19, 20): p += 2
        elif tag == 15: p += 3
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18): p += 4
        elif tag in (5, 6): p += 8; i += 1
        else: raise ValueError("bad constant pool tag %d" % tag)
        i += 1
    return out

WANT = ["skymenu", "menu", "sbmenu"]
TAKEN = set()
VANILLA_SKYSETTINGS = []
VANILLA_ADMINW = []
with zipfile.ZipFile(B.SERVER_JAR) as zj:
    for n in zj.namelist():
        if n.startswith("com/hypixel/") and n.endswith(".class"):
            try:
                _cp = cp_utf8(zj.read(n))
                TAKEN |= set(WANT) & _cp
                if "skysettings" in _cp:
                    VANILLA_SKYSETTINGS.append(n)
                if "modconfig" in _cp or "serversetup" in _cp:
                    VANILLA_ADMINW.append(n)
            except Exception:
                pass
# 0.1.3: a Skyy build script takes a word only as a ROOT command or an alias: addAliases(... <word> ...) or super(<word>, ...) in a class that
# is NOT passed to addSubCommand (SkyyIslands 0.5 has /island menu = a subcommand named "menu", which is no /menu command). The nearest
# "public ClassName(" before the super call is its constructor. 0.1.2 counted any quoted "menu" anywhere and would drop /menu.
# Review 2026-09-24: SkyyGuilds and SkyyVault write their super calls through a Python helper (super("%s", ...) % name), so the
# literal scan cannot see them: cmd("Class", "<word>", ...) is a root command unless that class is in some subs=(...) or
# variant="Class", and aliases=(... "<word>" ...) takes the word (even on a subcommand: that errs loud - the build prints "taken
# elsewhere"). SkyyIslands 0.5 builds its subcommands with sub("Class", "menu", ...), never a root. Best effort only - the plugin also
# checks the LIVE command map at the first PlayerReadyEvent and logs a WARNING when another command claims /menu, /sbmenu or /skymenu
# (MenuUtil.checkAliases).
SUB_RE = re.compile(r"addSubCommand\(\s*new\s+[^\s(]*?(\w+)\s*\(")
CTOR_RE = re.compile(r"public\s+(\w+)\s*\(")
HELPER_SUBS_RE = re.compile(r"(?:subs\s*=\s*\(([^)]*)\)|variant\s*=\s*(\"\w+\"))")
def takes(text, w):
    if re.search(r'addAliases\([^)]*"%s"' % re.escape(w), text):
        return True
    subs = set(SUB_RE.findall(text))
    for mm in re.finditer(r'super\(\s*"%s"' % re.escape(w), text):
        ctors = CTOR_RE.findall(text[:mm.start()])
        if not ctors or ctors[-1] not in subs:
            return True
    hsubs = set()
    for a, b in HELPER_SUBS_RE.findall(text):
        hsubs |= set(re.findall(r'"(\w+)"', a + " " + b))
    for mm in re.finditer(r'\bcmd\(\s*"(\w+)"\s*,\s*"%s"' % re.escape(w), text):
        if mm.group(1) not in hsubs:
            return True
    if re.search(r'aliases\s*=\s*\([^)]*"%s"' % re.escape(w), text):
        return True
    return False
# (the test strings are split after "super(" so tools/ci/lint.py does not read them as commands of this mod)
assert takes('public MenuCmd() { super(' + '"menu", "d"); }', "menu")
assert not takes('public IslandMenuCmd() { super(' + '"menu", "d"); } addSubCommand(new {PKG}.IslandMenuCmd());', "menu")
assert takes('addAliases(new String[] { "menu" });', "menu")
assert takes('cmd("GMenuCmd", "menu", "d", [], "")', "menu")
assert not takes('cmd("GMenuCmd", "menu", "d", [], "")\nroot = cmd("GuildCmd", "guild", "d", [], "",\n    subs=("GHelpCmd",\n          "GMenuCmd"))', "menu")
assert not takes('cmd("VMenuCmd", "menu", "d", [], "")\ncmd("VaultCmd", "vault", "d", [], "", variant="VMenuCmd")', "menu")
assert takes('cmd("GuildCmd", "guild", "d", [], "", aliases=("g", "menu"))', "menu")
assert not takes('cmd("GuildCmd", "guild", "d", [], "", aliases=("g",))', "menu")
for p in glob.glob(os.path.join(B.PROJECT, "*", "build_*.py")):
    if os.path.basename(os.path.dirname(p)) == "SkyyMenu":
        continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    for w in WANT:
        if takes(t, w):
            TAKEN.add(w)
assert "skymenu" not in TAKEN, "/skymenu is already used by another command"
ALIASES = [a for a in ("menu", "sbmenu", "menuitem") if a not in TAKEN]   # 0.3.32: + /menuitem (the lifelong recall)
print("aliases:", ALIASES, "(taken elsewhere: %s)" % (sorted(TAKEN) or "none"))
ALIAS_TEXT = (" (also " + ", ".join("/" + a for a in ALIASES) + ")") if ALIASES else ""
# 0.2: /settings + /skysettings (Settings-Spec 4.1) - no other Skyy build script may take them (same takes() rule as the menu words)
assert not VANILLA_SKYSETTINGS, "the vanilla jar already knows /skysettings: " + ", ".join(VANILLA_SKYSETTINGS[:3])
# takes() counts ANY aliases=(... "word" ...) on purpose (loud for the menu words). For these two words an alias given to the SkyyIslands
# sub("Class", ...) helper is a SUBCOMMAND alias (/island menu = /island settings), not a /settings command, so it is skipped here.
HELPER_CALL_RE = re.compile(r'\b(sub|cmd)\(\s*"\w+"')
def takes_root(text, w):
    if not takes(text, w):
        return False
    t2 = text
    for mm in reversed(list(re.finditer(r'aliases\s*=\s*\([^)]*"%s"' % re.escape(w), text))):
        calls = list(HELPER_CALL_RE.finditer(text, 0, mm.start()))
        if calls and calls[-1].group(1) == "sub":
            t2 = t2[:mm.start()] + t2[mm.end():]
    return takes(t2, w)
assert not takes_root('sub("IslandMenuCmd", "menu", "d", r"""x""", aliases=("settings", "options"))', "settings")
assert takes_root('cmd("SetCmd", "settings", "d", [], "")', "settings")
assert takes_root('cmd("XCmd", "x", "d", [], "", aliases=("settings",))', "settings")
SET_TAKEN = []
for p in glob.glob(os.path.join(B.PROJECT, "*", "build_*.py")):
    if os.path.basename(os.path.dirname(p)) == "SkyyMenu":
        continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    for w in ("settings", "skysettings"):
        if takes_root(t, w):
            SET_TAKEN.append((w, os.path.relpath(p, B.PROJECT)))
assert not [x for x in SET_TAKEN if x[0] == "skysettings"], "/skysettings is taken elsewhere: %s" % SET_TAKEN
if SET_TAKEN:
    print("WARNING: /settings is also registered by", SET_TAKEN, "- players keep /skysettings and the menu torch")
print("settings command: /settings /skysettings (taken elsewhere: %s)" % (SET_TAKEN or "none"))
# 0.3: /modconfig + /serversetup (spec 2.2): no vanilla class and no other Skyy build script may know either word
assert not VANILLA_ADMINW, "the vanilla jar already knows /modconfig or /serversetup: " + ", ".join(VANILLA_ADMINW[:3])
ADM_TAKEN = []
for p in glob.glob(os.path.join(B.PROJECT, "*", "build_*.py")):
    if os.path.basename(os.path.dirname(p)) == "SkyyMenu":
        continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    for w in (ADMIN_CMD, ADMIN_ALIAS):
        if takes_root(t, w):
            ADM_TAKEN.append((w, os.path.relpath(p, B.PROJECT)))
assert not ADM_TAKEN, "/%s or /%s is taken elsewhere: %s" % (ADMIN_CMD, ADMIN_ALIAS, ADM_TAKEN)
print("server setup command: /%s /%s (free)" % (ADMIN_CMD, ADMIN_ALIAS))
# 0.3.28: the hub commands (spec 2.3) - no other Skyy build script takes one of the words as a root command or alias, no vanilla command
# class is named after one (best effort; the plugin also logs a clash when it registers them and still loads)
HUB_WORDS = [w for w, _a, _h in HUB_CMDS] + [a for _w, al, _h in HUB_CMDS for a in al]
HUB_TAKEN = []
for p in glob.glob(os.path.join(B.PROJECT, "*", "build_*.py")):
    if os.path.basename(os.path.dirname(p)) == "SkyyMenu":
        continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    for w in HUB_WORDS:
        if takes_root(t, w):
            HUB_TAKEN.append((w, os.path.relpath(p, B.PROJECT)))
assert not HUB_TAKEN, "0.3.28: a hub command word is taken elsewhere: %s" % HUB_TAKEN
with zipfile.ZipFile(B.SERVER_JAR) as zj:
    _vh = [n for n in zj.namelist() if n.endswith("Command.class") and n.rsplit("/", 1)[-1][:-len("Command.class")].lower() in HUB_WORDS]
assert not _vh, "0.3.28: the vanilla jar has a command class named after a hub word: %s" % _vh
print("hub commands: %s (free)" % ", ".join("/" + w for w in HUB_WORDS))

# ================= inline UI strings (validated here: balanced, no underscores in element ids) =================
BS = ("Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 17, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
      "Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 17, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
      "Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 17, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));")
SLOT, COLS, ROWS = 84, 9, 6
GW, GH = SLOT * COLS, SLOT * ROWS
PW = GW + 44
PH = 952
UI = {
    "ROOT":     "Group #SkyyMenu { Anchor: (Width: %d, Height: %d); Background: #0b1524(0.96); Padding: (Horizontal: 22, Vertical: 14); LayoutMode: Top; }" % (PW, PH),
    "ACCENT":   "Group { Anchor: (Height: 3); Background: #e0b060; }",
    "TITLE":    'Label #SkyyMTitle { Anchor: (Height: 38); Text: ""; Style: (FontSize: 23, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "HINT":     'Label #SkyyMHint { Anchor: (Height: 22); Text: ""; Style: (FontSize: 14, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "GRIDWRAP": "Group #SkyyMGridWrap { Anchor: (Height: %d); }" % (GH + 6),
    "GRID":     "ItemGrid #SkyyMGrid { Anchor: (Horizontal: 0, Top: 3, Width: %d, Height: %d); SlotsPerRow: %d; AreItemsDraggable: false; Style: (SlotSize: %d, SlotIconSize: 62, SlotSpacing: 0); }" % (GW, GH, COLS, SLOT),
    # 0.1.3: the same grid without hover tooltips (per-player switch). InfoDisplay: None is the inline markup EyeSpy / Tamework ship.
    "GRIDNOTIPS": "ItemGrid #SkyyMGrid { Anchor: (Horizontal: 0, Top: 3, Width: %d, Height: %d); SlotsPerRow: %d; AreItemsDraggable: false; InfoDisplay: None; Style: (SlotSize: %d, SlotIconSize: 62, SlotSpacing: 0); }" % (GW, GH, COLS, SLOT),
    "GAP":      "Group { Anchor: (Height: 8); }",
    "INFOBOX":  "Group #SkyyMInfoBox { Anchor: (Height: 266); Background: #142030(0.9); Padding: (Horizontal: 14, Vertical: 8); LayoutMode: Top; }",
    "INFONAME": 'Label #SkyyMInfoName { Anchor: (Height: 26); Text: ""; Style: (FontSize: 18, RenderBold: true, TextColor: #ffe9a0, VerticalAlignment: Center); }',
    "INFODESC": 'Label #SkyyMInfoDesc { Anchor: (Height: 42); Text: ""; Style: (FontSize: 15, TextColor: #c9dff0, Wrap: true); }',
    "STATUS":   'Label #SkyyMStatus { Anchor: (Height: 28); Text: ""; Style: (FontSize: 15, RenderBold: true, TextColor: #ffd27f, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "FOOT":     "Group #SkyyMFoot { Anchor: (Height: 46); LayoutMode: Left; Padding: (Top: 3); }",
    "SPACER":   'Label { Anchor: (Width: 11, Height: 40); Text: ""; }',
    "LEAD":     'Label { Anchor: (Width: 28, Height: 40); Text: ""; }',
    # 0.3.35: the old classic footer's back / page buttons went (the kit 1.7 footer: UI35 below)
    "BTNCLOSE": 'TextButton #SkyyMClose { Anchor: (Width: 168, Height: 40); Text: "Close"; ' + BS + " }",
    # 0.3.28: the menu views in the hub shell (Teleport / Players / Mods / the layout editor): the status shows IN the hint row (same id,
    # the STATUS look) and the info box is 256 high (8 lines) - the shell's title bar + tab strip replace the accent + title row
    "HINTST":   'Label #SkyyMHint { Anchor: (Height: 22); Text: ""; Style: (FontSize: 15, RenderBold: true, TextColor: #ffd27f, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "INFOBOXH": "Group #SkyyMInfoBox { Anchor: (Height: 256); Background: #142030(0.9); Padding: (Horizontal: 14, Vertical: 8); LayoutMode: Top; }",
}
INFO_LINES = 9
UI_INFO = ['Label #SkyyMInfo%d { Anchor: (Height: 20); Text: ""; Style: (FontSize: 14, TextColor: #9fb8cc, VerticalAlignment: Center); }' % i for i in range(INFO_LINES)]
for s in list(UI.values()) + UI_INFO:
    assert s.count("{") == s.count("}") and s.count("(") == s.count(")"), "unbalanced inline UI: " + s
    for eid in re.findall(r"#([A-Za-z0-9_]+)\s*\{", s):
        assert "_" not in eid, "underscore in element id #" + eid
    assert "Anchow" not in s and ";;" not in s
_tall = 2 * 14 + 3 + 38 + 22 + (GH + 6) + 8 + 266 + 28 + 46
assert _tall <= PH, 'menu parts are %d px tall, page is %d' % (_tall, PH)
assert 26 + 42 + 20 * INFO_LINES + 16 <= 266, 'info box too small for its lines'
assert 26 + 42 + 20 * HUB_INFO_LINES + 16 <= 256 < 26 + 42 + 20 * (HUB_INFO_LINES + 1) + 16 and HUB_INFO_LINES <= INFO_LINES, '0.3.28: the hub info box holds its 8 lines'
assert "Width" in UI["ROOT"] and "Top:" not in UI["ROOT"].split("Anchor: (")[1].split(")")[0], "page root anchor must be Width/Height only"

# ================= 0.2 Settings page (research/Settings-Spec.md 4.2 + 4.3): 1120 x 930, every id starts with SkyyStg =================
def _tbs(bg, fg, hov, pre):
    lab = "LabelStyle: (FontSize: 18, TextColor: " + fg + ", RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)"
    return ("Style: TextButtonStyle(Default: (Background: " + bg + ", " + lab + "), Hovered: (Background: " + hov + ", " + lab + "), "
            "Pressed: (Background: " + pre + ", " + lab + "));")
SBS       = _tbs("#5a4420", "#ffe9c9", "#8a6a30", "#3a2a10")      # the menu's brown buttons at FontSize 18
ON_SEL    = _tbs("#7fe07f", "#062a06", "#a0f0a0", "#5fb05f")      # SkyyHud WidgetsPage green (verified "beautiful")
OFF_SEL   = _tbs("#e07070", "#2a0606", "#f09090", "#b05050")
TAB_SEL   = _tbs("#e0b060", "#2a1a00", "#f0c880", "#b08840")
RESET_ARM = _tbs("#a03030", "#ffffff", "#c04040", "#801818")
# 0.3.35 (kit 1.7, research/Menu-Pattern.md M8): Settings > Settings on the 1600 x 980 hub_page - the categories are the ONE sub-tab row
# (HubBar.subTab), the search row, the heading, ONE scroll list of every row of the category (no pages; Skyy rule 7: a short list gets
# bigger rows - HubBar.growSize over STG_ROW_H), the always-on line; the footer = the hint / status line, Reset all, Close (no menu button:
# row 1 Home). The ON / OFF looks stay the SkyyHud green / red Skyy approved; the frame, tabs, rows and buttons are the kit's.
SPW, SPH = SUI.HUB_PAGE_W, SUI.HUB_PAGE_H        # 1600 x 980
SPI = SUI.HUB_PAGE_IW                            # 1552
STG_CH = SPH - SUI.TITLE_H - 2 * 24 - SUI.HUB_BIG_ROW_H - SUI.HUB_BIG_TABS_H - SUI.SUB_ROW_H - SUI.FOOT_H     # 676: the content
SFIND_H, SFIND_BTN = 52, 150
SFIND_W = SPI - 2 * SFIND_BTN - 2 * 10
STG_HEAD_H, STG_ALWAYS_H = 40, 26
STG_LIST_H = STG_CH - SFIND_H - 8 - STG_HEAD_H - STG_ALWAYS_H                   # 550
STG_ROW_H = SUI.grow_row_sizes(STG_LIST_H - 2 * SUI.WELL_LIST_PAD, 61, gap=3)  # [61, 88, 122]
STG_TXT_W = SPI - 2 * SUI.WELL_LIST_PAD - 14 - 120 - 10 - 120 - 24              # the name / help column (24 = the scrollbar + a margin)
STG_TAB_W = SUI.SUB_TAB_W
STG_RESET_W, STG_CLOSE_W = 300, 170
STG_HINT_W = SPI - STG_RESET_W - STG_CLOSE_W - 2 * SUI.FOOT_GAP
_SKY = SUI.THEME["sky"]
UI_S = {
    "SFINDROW":  "Group #SkyyStgFindRow { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: 2); }" % SFIND_H,
    "SFIND":     SUI.text_field("SkyyStgFindBox", "SkyyStgFind", w=SFIND_W, h=SFIND_H - 4, placeholder="Search every tab by name or words",
                                max_length=40, size=19),
    "SFINDGO":   'TextButton #SkyyStgFindGo { Anchor: (Width: %d, Height: %d); Text: "Search"; %s }' % (SFIND_BTN, SFIND_H - 4, SUI.theme_button_style("secondary", "normal", theme="sky")),
    "SFINDCLR":  'TextButton #SkyyStgFindClr { Anchor: (Width: %d, Height: %d); Text: "Clear"; %s }' % (SFIND_BTN, SFIND_H - 4, SUI.theme_button_style("secondary", "normal", theme="sky")),
    "SSP10F":    SUI.spacer(w=10),
    "SGAP8":     "Group { Anchor: (Height: 8); }",
    "SHEAD":     SUI.label("SkyyStgHead", "", "heading", h=STG_HEAD_H, size=22, wrap=False),
    "SROWS":     SUI.scroll_list("SkyyStgRows", h=STG_LIST_H, well=True),
    "SEMPTY":    SUI.empty_state("SkyyStgEmpty", h=80),
    "SALWAYS":   SUI.label("SkyyStgAlways", "", "caption", h=STG_ALWAYS_H, size=15),
    "SHINT":     SUI.foot_info("SkyyStgHint", STG_HINT_W),
    "SHINTST":   SUI.label("SkyyStgHint", "", "gold", h=SUI.FOOT_BTN_H, w=STG_HINT_W, size=16, wrap=True, padding={"horizontal": 8}),
    "SFSP":      SUI.spacer(w=SUI.FOOT_GAP),
    "SRESET":    SUI.foot_button("SkyyStgReset", "Reset all to defaults", STG_RESET_W),
    "SRESETARM": SUI.foot_button("SkyyStgReset", "Click again to reset ALL", STG_RESET_W, kind="destructive"),
    "SCLOSE":    SUI.foot_button("SkyyStgClose", "Close", STG_CLOSE_W, sound="cancel"),
    "SSP14":     SUI.spacer(w=14),
    "SSP10":     SUI.spacer(w=10),
    # a row's pieces after its runtime id ("Group #SkyyStgRow" + r + UI_SROWB[size], "Label #SkyyStgName" + r + UI_SNAMEB, ...)
    "STXTB":     " { Anchor: (Width: %d, Height: 52); LayoutMode: Top; }" % STG_TXT_W,
    "SNAMEB":    ' { Anchor: (Height: 28); Text: ""; Style: %s; }' % SUI.text_style(19, "rowName", bold=True),
    "SDESCB":    ' { Anchor: (Height: 24); Text: ""; Style: %s; }' % SUI.text_style(15, "text"),
    "SONB":      ' { Anchor: (Width: 120, Height: 52); Text: "ON"; %s }' % SUI.theme_button_style("secondary", "normal", theme="sky"),
    "SONSELB":   ' { Anchor: (Width: 120, Height: 52); Text: "ON"; ' + ON_SEL + " }",
    "SOFFB":     ' { Anchor: (Width: 120, Height: 52); Text: "OFF"; %s }' % SUI.theme_button_style("secondary", "normal", theme="sky"),
    "SOFFSELB":  ' { Anchor: (Width: 120, Height: 52); Text: "OFF"; ' + OFF_SEL + " }",
}
UI_SARR = {
    "SROWB": [" { Anchor: (Height: %d, Bottom: 3); Background: %s; LayoutMode: Left; Padding: (Top: %d); }" % (h_, _SKY["row"], (h_ - 52) // 2)
              for h_ in STG_ROW_H],
}
SET_UI_ALL = list(UI_S.values()) + [x for v in UI_SARR.values() for x in v]
for s_ in SET_UI_ALL:
    assert s_.count("{") == s_.count("}") and s_.count("(") == s_.count(")"), "unbalanced inline UI: " + s_
    for eid in re.findall(r"#([A-Za-z0-9_]+)\s*\{", s_):
        assert "_" not in eid, "underscore in element id #" + eid
        assert eid.startswith("SkyyStg"), "settings page ids start with SkyyStg: #" + eid
    assert "Anchow" not in s_ and ";;" not in s_
    for txt_ in re.findall(r'Text: "([^"]*)"', s_):              # fixed inline text: only characters already proven inline
        assert re.match(r"^[A-Za-z0-9 <>/-]*$", txt_), "inline text with unproven characters (use b.set): " + txt_
assert len(SET_TABS) <= 10 and SUI.assert_sub_tabs_fit([t[1] for t in SET_TABS], STG_TAB_W), "0.3.35: every category fits the ONE sub-tab row"
assert SFIND_H + 8 + STG_HEAD_H + STG_LIST_H + STG_ALWAYS_H == STG_CH and STG_ROW_H[0] == 61 and 4 + 52 <= 61, "0.3.35: the settings content fits"
assert 14 + STG_TXT_W + 120 + 10 + 120 <= SPI - 2 * SUI.WELL_LIST_PAD and STG_HINT_W >= 600, "0.3.35: a settings row / the footer fits"
assert SFIND_W >= 600 and SFIND_W + 2 * SFIND_BTN + 2 * 10 <= SPI, "0.3.25: the search row is wider than the Settings page"

# ================= 0.3 Server Setup page (research/Server-Setup-Spec.md 2.3-2.12): 1120 x 930, every id starts with SkyyAdm =================
# Fixed parts are constants here (validated below and found again in MenuData.class after the build); parts that carry a mod's text are
# built at run time by AdminPage.btn / lab / spc / field from the SAME patterns (the harness validated their output) with the text
# reduced to letters, digits, space and < > / - (MenuUtil.inl); Labels get every mod text through b.set.
def _tbsz(bg, fg, hov, pre, fs):
    lab = "LabelStyle: (FontSize: %d, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)" % (fs, fg)
    return ("Style: TextButtonStyle(Default: (Background: " + bg + ", " + lab + "), Hovered: (Background: " + hov + ", " + lab + "), "
            "Pressed: (Background: " + pre + ", " + lab + "));")
APW, APH = 1128, 980                                 # 0.3.28: the hub shell (1080 inside + the sky padding 2 x 24)
A_INNER = APW - 2 * 24                               # 1080: the hub shell body has padding 24 (0.3.27: 1120 - 2 x 20)
# 0.3.35 (kit 1.7): the page is a 1600 x 980 hub_page - row 1, row 2, the sub-tab row (the view crumbs + the title line), the body (1080
# wide, centred) and the footer (the status line + the view's buttons); the body = what is left: 676 (the title line and status moved out)
A_BODY = SUI.HUB_PAGE_H - SUI.TITLE_H - 2 * 24 - SUI.HUB_BIG_ROW_H - SUI.HUB_BIG_TABS_H - SUI.SUB_ROW_H - SUI.FOOT_H
ADM_ROWS, ADM_LROWS, ADM_GROWS, ADM_HROWS = 6, 8, 10, 8           # 0.3.35: 6 mod rows a page (was 7)
ADM_INFOLINES, ADM_MSGLINES, ADM_PLINES, ADM_FROWS = 23, 16, 12, 3   # 0.3.35: 23 info lines (was 24), 3 import files (was 4)
ADM_STYLE = {
    "BS":    SBS,                                                        # brown, FontSize 18 (the Settings page buttons)
    "BS16":  _tbsz("#5a4420", "#ffe9c9", "#8a6a30", "#3a2a10", 16),     # tabs + choice buttons (longer texts)
    "SEL":   TAB_SEL,
    "SEL16": _tbsz("#e0b060", "#2a1a00", "#f0c880", "#b08840", 16),
    "ONSEL": ON_SEL,
    "OFFSEL": OFF_SEL,
    "RED":   RESET_ARM,
    # 0.3.35: the view crumbs (the sub-tab row: kit small buttons), the title line beside them, the footer status line (4 colours)
    "SUBSEL": SUI.theme_button_style("primary", "small", theme="sky"),
    "SUBN":   SUI.theme_button_style("secondary", "small", theme="sky"),
    "SUBSTYLE": SUI.text_style(16, "rowName", bold=True),
    "ST0":    "(FontSize: 17, RenderBold: true, TextColor: #ffd27f, VerticalAlignment: Center, Wrap: true)",
    "ST1":    "(FontSize: 17, RenderBold: true, TextColor: #7fe07f, VerticalAlignment: Center, Wrap: true)",
    "ST2":    "(FontSize: 17, RenderBold: true, TextColor: #ffb347, VerticalAlignment: Center, Wrap: true)",
    "ST3":    "(FontSize: 17, RenderBold: true, TextColor: #ff7a7a, VerticalAlignment: Center, Wrap: true)",
}
_TXT = lambda i, h, fs, col, bold=False, center=False, w=0: ('Label #%s { Anchor: (%sHeight: %d); Text: ""; Style: (FontSize: %d%s, TextColor: %s%s, VerticalAlignment: Center); }'
                                                            % (i, ("Width: %d, " % w) if w else "", h, fs, ", RenderBold: true" if bold else "", col, ", HorizontalAlignment: Center" if center else ""))
# 0.3.36 (research/Menu-Pattern.md M8 + rule 7): every row page is ONE scroll list (SUI.scroll_list, the well) of kit rows; a short list
# grows its rows (SUI.grow_row_sizes -> HubBar.growSize: the row taller, its content centred). A row's pieces are built at run time as
# <head> + <row number> + <tail> (UI_<NAME>A / UI_<NAME>B below, validated here with a sample number); a row group takes its tier's tail
# UI_<NAME>B[size]. The rows lose 24 px of width to the scrollbar (ADM_LW).
_ROWBG = SUI.THEME["sky"]["row"]                      # the kit row (the Settings rows' look; 0.3.35: #142030)
_BOXBG = SUI.THEME["sky"]["inset"]                    # the info / message / preview boxes
ADM_LW = A_INNER - 2 * SUI.WELL_LIST_PAD - 24         # 1048: what a scroll-list row may use
ADM_LH = {"list": A_BODY - 58, "mod": A_BODY - 26 - 40, "modp": A_BODY - 58 - 40, "tableadd": A_BODY - 58 - 40 - 30 - 62, "table": A_BODY - 58 - 40 - 30,
          "log": A_BODY - 58 - 40, "hist": A_BODY - 58 - 40, "histprev": A_BODY - 58 - 40 - 282, "files": ADM_FROWS * 48}
ADM_IN = dict((k, v - 2 * SUI.WELL_LIST_PAD) for k, v in ADM_LH.items())    # growSize's room
ADM_RH = {"L": SUI.grow_row_sizes(ADM_IN["list"], 70, gap=6), "M": SUI.grow_row_sizes(ADM_IN["mod"], 70, gap=6),
          "T": SUI.grow_row_sizes(ADM_IN["tableadd"], 70, gap=6), "G": SUI.grow_row_sizes(ADM_IN["log"], 46, gap=6),
          "H": SUI.grow_row_sizes(ADM_IN["hist"], 52, gap=6)}
ADM_TFIELDS, ADM_TMAX, ADM_GMAX, ADM_FMAX = 40, 200, 200, 50
ADM_MFIELDS, ADM_CATMIN = 40, 60   # critic fixes: a mod view's crumbs / footer carry at most 40 boxes; a category tab is >= 60 px   # an editable table: at most 40 text boxes; at most 200 table / log rows, 50 files
UI_A = {
    # 0.3.28: the page root, accent and title row are the kit's hub shell now (ADM_HUB_SH below: root SkyyAdmH, body = #SkyyAdm); the
    # view's title and subtitle share ONE line ("<title>   -   <subtitle>", cut at ADM_SUBMAX characters); 0.3.36: on a mod with
    # categories (they fill the sub-tab row) that line is the first line of the body (ASUB)
    "ASUB":     _TXT("SkyyAdmSub", 26, 16, "#ffe9c9", True, True),
    "ABODY":    "Group #SkyyAdmBody { Anchor: (Height: %d); LayoutMode: Top; }" % A_BODY,
    "AGAP6":    "Group { Anchor: (Height: 6); }",
    "AGAP8":    "Group { Anchor: (Height: 8); }",
    "AGAP12":   "Group { Anchor: (Height: 12); }",
    "AGAP20":   "Group { Anchor: (Height: 20); }",
    "AHEAD":    _TXT("SkyyAdmHead", 40, 24, "#e0b060", True),
    "AEMPTY":   _TXT("SkyyAdmEmpty", 80, 19, "#c9dff0", False, True),
    # list
    "ALSEARCH": "Group #SkyyAdmSearch { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "ALROWS":   SUI.scroll_list("SkyyAdmLRows", h=ADM_LH["list"], well=True),
    # mod
    "AROWS":    SUI.scroll_list("SkyyAdmRows", h=ADM_LH["mod"], well=True),
    "AROWSP":   SUI.scroll_list("SkyyAdmRows", h=ADM_LH["modp"], well=True),   # under the category picker
    "AINFO":    "Group #SkyyAdmInfo { Anchor: (Height: 670); Background: %s; Padding: (Horizontal: 24, Vertical: 12); LayoutMode: Top; }" % _BOXBG,
    # table
    "ATFIND":   "Group #SkyyAdmTFindRow { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "ATCOLS":   "Group #SkyyAdmCols { Anchor: (Height: 30); LayoutMode: Left; }",
    "ATROWSA":  SUI.scroll_list("SkyyAdmTRows", h=ADM_LH["tableadd"], well=True),
    "ATROWSB":  SUI.scroll_list("SkyyAdmTRows", h=ADM_LH["table"], well=True),
    "ATADD":    "Group #SkyyAdmTAdd { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 6); }",
    # confirm
    "AMSGBOX":  "Group #SkyyAdmMsgBox { Anchor: (Height: 560); Background: %s; Padding: (Horizontal: 24, Vertical: 12); LayoutMode: Top; }" % _BOXBG,
    "ACONF":    "Group #SkyyAdmConf { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 3); }",
    # log + history (the in-page picker: label, <, the picked name, >) + io
    "APICK":    "Group #SkyyAdmPick { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "APICKL":   _TXT("SkyyAdmPickL", 50, 18, "#e0b060", True, False, 240),
    "APICKV":   _TXT("SkyyAdmPickV", 50, 19, "#ffffff", True, True, 420),
    "AGROWS":   SUI.scroll_list("SkyyAdmGRows", h=ADM_LH["log"], well=True),
    "AHROWS":   SUI.scroll_list("SkyyAdmHRows", h=ADM_LH["hist"], well=True),
    "AHROWSP":  SUI.scroll_list("SkyyAdmHRows", h=ADM_LH["histprev"], well=True),
    "APREV":    "Group #SkyyAdmPrev { Anchor: (Height: 282); Background: %s; Padding: (Horizontal: 16, Vertical: 8); LayoutMode: Top; }" % _BOXBG,
    "APREVHEAD": _TXT("SkyyAdmPrevHead", 26, 17, "#e0b060", True),
    "AIOL1":    _TXT("SkyyAdmIoL1", 34, 18, "#e0b060", True),
    "AIOL2":    _TXT("SkyyAdmIoL2", 34, 18, "#e0b060", True),
    "AIOR1":    "Group #SkyyAdmIoR1 { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "AIOR2":    "Group #SkyyAdmIoR2 { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "AIOF":     _TXT("SkyyAdmIoF", 30, 17, "#9fb8cc"),
    "AIOFROWS": SUI.scroll_list("SkyyAdmIoFRows", h=ADM_LH["files"], well=True),
}
UI_AARR = {      # the fixed-count pieces (info / message / preview lines)
    "AINFOL":   [_TXT("SkyyAdmInfo%d" % i, 27, 18, "#e6f2ff") for i in range(ADM_INFOLINES)],
    "AINFOB":   [_TXT("SkyyAdmInfo%d" % i, 27, 19, "#e0b060", True) for i in range(ADM_INFOLINES)],
    "AMSGQ":    [_TXT("SkyyAdmMsg%d" % i, 33, 21, "#ffe9c9", True) for i in range(ADM_MSGLINES)],
    "AMSGL":    [_TXT("SkyyAdmMsg%d" % i, 33, 18, "#c9dff0") for i in range(ADM_MSGLINES)],
    "APL":      [_TXT("SkyyAdmPL%d" % i, 20, 15, "#c9dff0") for i in range(ADM_PLINES)],
}
# a row group per grow tier: " { Anchor: (Height: h); Background: <kit row>; LayoutMode: ...; Padding: (Top: content centred); }"
_rowb = lambda tiers, lay, content: [" { Anchor: (Height: %d); Background: %s; LayoutMode: %s; Padding: (Top: %d); }" % (h_, _ROWBG, lay, (h_ - content) // 2)
                                    for h_ in tiers]
UI_AROWB = {
    "ALROWB": _rowb(ADM_RH["L"], "Left", 52),       # Group #SkyyAdmLRow<r>: name + line 2 (52), Open, Reload
    "AROWB":  _rowb(ADM_RH["M"], "Top", 64),        # Group #SkyyAdmRow<r>: the line (42) + the help line (22)
    "ATROWB": _rowb(ADM_RH["T"], "Left", 52),       # Group #SkyyAdmTRow<r>: entry, its boxes, Set, Remove
    "AGROWB": _rowb(ADM_RH["G"], "Left", 40),       # Group #SkyyAdmGRow<r>: a change line + Undo
    "AHROWB": _rowb(ADM_RH["H"], "Left", 44),       # Group #SkyyAdmHRow<r>: a version + Preview + Restore
}
ADM_ROWHEAD = {"ALROWB": "Group #SkyyAdmLRow", "AROWB": "Group #SkyyAdmRow", "ATROWB": "Group #SkyyAdmTRow", "AGROWB": "Group #SkyyAdmGRow",
               "AHROWB": "Group #SkyyAdmHRow"}
# the per-row pieces: <head> + r + <tail> (the sample number 7777 marks the split)
_PIECE = {
    "ALTXT":    "Group #SkyyAdmLTxt%s { Anchor: (Width: 712, Height: 52); LayoutMode: Top; }",
    "ALNAME":   _TXT("SkyyAdmLName%s", 28, 21, "#ffffff", True),
    "ALDESC":   _TXT("SkyyAdmLDesc%s", 24, 16, "#b8c8d8"),
    "ALDESCRED": _TXT("SkyyAdmLDesc%s", 24, 16, "#ff8a8a", True),
    "ALINE":    "Group #SkyyAdmLine%s { Anchor: (Height: 42); LayoutMode: Left; }",
    "ANAME":    _TXT("SkyyAdmName%s", 42, 20, "#ffffff", True, False, 524),
    "AW":       "Group #SkyyAdmW%s { Anchor: (Width: 380, Height: 42); LayoutMode: Left; }",
    "AHELP":    "Group #SkyyAdmHelpRow%s { Anchor: (Height: 22); LayoutMode: Left; }",
    "ADESC":    _TXT("SkyyAdmDesc%s", 22, 15, "#b8c8d8", False, False, 1034),
    "ARO":      _TXT("SkyyAdmRo%s", 42, 19, "#ffe9a0", True, False, 380),
    "ACHV":     _TXT("SkyyAdmChv%s", 42, 18, "#ffe9a0", True, True, 268),
    "ATKEY":    _TXT("SkyyAdmTKey%s", 52, 18, "#ffffff", True, False, 300),
    "ATCELLS":  "Group #SkyyAdmTCols%s { Anchor: (Width: 450, Height: 52); LayoutMode: Left; }",
    "AGTXT":    _TXT("SkyyAdmGTxt%s", 40, 16, "#e6f2ff", False, False, 890),
    "AHTXT":    _TXT("SkyyAdmHTxt%s", 44, 16, "#e6f2ff", False, False, 776),
    "AFROW":    "Group #SkyyAdmFRow%s { Anchor: (Height: 42); LayoutMode: Left; }",
    "AFTXT":    _TXT("SkyyAdmFTxt%s", 42, 17, "#e6f2ff", False, False, 890),
}
UI_APIECE = {}
for _n, _t in _PIECE.items():
    _s = _t % "7777"
    assert _s.count("7777") == 1, _n
    UI_APIECE[_n + "A"], UI_APIECE[_n + "B"] = _s.split("7777")
ADM_ROW_SAMPLES = [_t % "7777" for _t in _PIECE.values()] + [ADM_ROWHEAD[_k] + "7777" + _b for _k, _v in UI_AROWB.items() for _b in _v]
# 0.3.36: the crumbs / categories (AdminPage.crumbBtn: the kit small button, its text fitted and set with b.set) + the title label beside them
ADM_CRUMB_PAD = SUI.SUB_TAB_PAD
# the client's glyph widths (x 100, rounded up) at the 12 px a small button label shrinks to, capitals (RenderUppercase): AdminPage.fit
ADM_CW = [int(-(-SUI.text_width(chr(_c), 12, bold=True, upper=True) * 100 // 1)) for _c in range(32, 127)]
ADM_CWMAX = max(ADM_CW)
# the run-time patterns (AdminPage.btn / spc / lab / field / crumbBtn) with sample values, so the validation below also covers them
def adm_btn(i, w, h, text, style):
    return 'TextButton #%s { Anchor: (Width: %d, Height: %d); Text: "%s"; %s }' % (i, w, h, text, style)
def adm_field(i, w, h, mx, ph):
    p = (' PlaceholderText: "%s"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 17);' % ph) if ph else ""
    return ["Group #%sBox { Anchor: (Width: %d, Height: %d); Background: #16263a; }" % (i, w, h),
            "TextField #%s { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: %d;%s Style: (TextColor: #ffffff, FontSize: 19); }" % (i, mx, p)]
def adm_crumb(i, w, sel):
    return 'TextButton #%s { Anchor: (Width: %d, Height: %d); Padding: (Horizontal: %d); Text: ""; %s }' % (
        i, w, SUI.SUB_TAB_H, ADM_CRUMB_PAD, ADM_STYLE["SUBSEL"] if sel else ADM_STYLE["SUBN"])
ADM_SAMPLES = ([adm_btn("SkyyAdmF0", 150, 48, "Changes", ADM_STYLE["BS"]), adm_btn("SkyyAdmPickPrev", 60, 50, "<", ADM_STYLE["BS"]),
                adm_crumb("SkyyAdmCrumb0", 150, True), adm_crumb("SkyyAdmCrumb1", 72, False),
                'Label { Anchor: (Width: 14, Height: 42); Text: ""; }', _TXT("SkyyAdmColv0x1", 52, 18, "#ffffff", False, False, 222)]
               + adm_field("SkyyAdmVal3", 196, 42, 2000, "") + adm_field("SkyyAdmFind", 660, 50, 60, "search settings and editors") + ADM_ROW_SAMPLES)
ADM_UI_ALL = (list(UI_A.values()) + [x for v in UI_AARR.values() for x in v] + list(ADM_STYLE.values()) + [x for v in UI_AROWB.values() for x in v]
              + list(UI_APIECE.values()))
for s_ in list(UI_A.values()) + [x for v in UI_AARR.values() for x in v] + ADM_SAMPLES:
    assert s_.count("{") == s_.count("}") and s_.count("(") == s_.count(")"), "unbalanced inline UI: " + s_
    for eid in re.findall(r"#([A-Za-z0-9_]+)\s*\{", s_):
        assert "_" not in eid, "underscore in element id #" + eid
        assert eid.startswith("SkyyAdm"), "server setup ids start with SkyyAdm: #" + eid
    assert "Anchow" not in s_ and ";;" not in s_
    for txt_ in re.findall(r'Text: "([^"]*)"', s_):
        assert re.match(r"^[A-Za-z0-9 <>/-]*$", txt_), "inline text with unproven characters (use b.set): " + txt_
for s_ in ADM_STYLE.values():
    assert s_.count("(") == s_.count(")") and "{" not in s_
# the scroll lists, the rows and the samples: the kit's markup rules + proven properties only (the kit row texture, the scrollbar)
_adm_chk = SUI.Appends([(None, "Group #SkyyAdmT { Anchor: (Width: 1080, Height: 676); LayoutMode: Top; }")])
for _k in ("ALROWS", "AROWS", "AGROWS", "AINFO", "APICK"):
    _adm_chk.append(("SkyyAdmT", UI_A[_k]))
_adm_chk.append(("SkyyAdmLRows", ADM_ROWHEAD["ALROWB"] + "0" + UI_AROWB["ALROWB"][-1]))
_adm_chk.append(("SkyyAdmLRow0", UI_APIECE["ALTXTA"] + "0" + UI_APIECE["ALTXTB"]))
_adm_chk.append(("SkyyAdmRows", ADM_ROWHEAD["AROWB"] + "0" + UI_AROWB["AROWB"][0]))
_adm_chk.append(("SkyyAdmRow0", UI_APIECE["ALINEA"] + "0" + UI_APIECE["ALINEB"]))
_adm_chk.append(("SkyyAdmGRows", ADM_ROWHEAD["AGROWB"] + "0" + UI_AROWB["AGROWB"][1]))
_adm_chk.append(("SkyyAdmPick", UI_A["APICKL"]))
_adm_chk.append(("SkyyAdmPick", UI_A["APICKV"]))
_adm_chk.check("SkyyAdm")
SUI.assert_proven(_adm_chk, what="server setup rows")
SUI.check_sky_paths(_adm_chk)
assert SUI.text_width("Show the versions of", 18, bold=True) <= 240 and SUI.text_width("Show the changes of", 18, bold=True) <= 240
# 0.3.28: the root is the kit's hub shell (its root anchor is checked by the kit: Width / Height only)
# height budgets (spec 2.4 / 2.5 asserts, like the menu's _tall): the body of every view fits the fixed body group
assert SUI.TITLE_H + 2 * 24 + SUI.HUB_BIG_ROW_H + SUI.HUB_BIG_TABS_H + SUI.SUB_ROW_H + A_BODY + SUI.FOOT_H == SUI.HUB_PAGE_H == 980 and A_BODY == 676, \
    "0.3.35: the server setup page is the 1600 x 980 hub page"
_abody = {"list": 58 + ADM_LH["list"], "mod": 26 + 40 + ADM_LH["mod"], "modp": 58 + 40 + ADM_LH["modp"], "file": 670, "table": 58 + 40 + 30 + ADM_LH["tableadd"] + 62,
          "tablero": 58 + 40 + 30 + ADM_LH["table"], "confirm": 560 + 20 + 62, "log": 58 + 40 + ADM_LH["log"], "hist": 58 + 40 + ADM_LH["hist"],
          "histprev": 58 + 40 + ADM_LH["histprev"] + 282, "io": 34 + 58 + 12 + 34 + 58 + 282 + 30 + ADM_LH["files"]}
for _v, _h in _abody.items():
    assert _h <= A_BODY, "server setup view %s needs %d px, the body has %d" % (_v, _h, A_BODY)
assert 24 + ADM_INFOLINES * 27 <= 670 and 24 + ADM_MSGLINES * 33 <= 560 and 16 + 26 + ADM_PLINES * 20 <= 282
assert ADM_LH["histprev"] >= 2 * 58 and all(len(v) == 3 and v[0] < v[1] < v[2] for v in ADM_RH.values()), "0.3.36: the row tiers"
# width budgets (a scroll-list row: ADM_LW = 1048)
assert 14 + 712 + 10 + 150 + 10 + 150 <= ADM_LW, "a list row is wider than its scroll list"
assert 14 + 524 + 10 + 380 + 10 + 110 <= ADM_LW and 14 + 1034 <= ADM_LW and 156 + 6 + 84 + 6 + 60 + 6 + 60 <= 380 and 270 + 6 + 104 <= 380, "a mod row is wider than its list"
assert 14 + 300 + 10 + 450 + 10 + 100 + 6 + 150 <= ADM_LW and 3 * 146 + 2 * 6 <= 450 and 2 * 222 + 6 <= 450, "a table row is wider than its list"
assert 14 + 890 + 10 + 120 <= ADM_LW and 14 + 776 + 10 + 120 + 6 + 120 <= ADM_LW and 14 + 890 + 10 + 130 <= ADM_LW and 830 + 10 + 200 <= A_INNER
assert 660 + 10 + 130 + 10 + 130 <= A_INNER and 14 + 240 + 60 + 6 + 420 + 6 + 60 <= A_INNER, "the search / picker rows fit"
assert 120 + 180 + 140 + 160 + 100 + 4 * 8 <= SUI.HUB_PAGE_IW - 200 and 150 + 150 + 130 + 120 + 3 * 8 <= SUI.HUB_PAGE_IW - 200, "the footers leave the status line room"

# ================= Java data (generated) =================
def jstr(s):
    if s is None:
        return "null"
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
def jarr(vals):
    return "new String[] { " + ", ".join(jstr(v) for v in vals) + " }"
def jints(vals):
    return "new int[] { " + ", ".join(str(int(v)) for v in vals) + " }"
def jbools(vals):
    return "new boolean[] { " + ", ".join("true" if v else "false" for v in vals) + " }"
def lines_of(lines):
    return "\n".join(txt(l) for l in lines)

# 0.3.16: LAYOUT D - tile -> (row, col) of the main view (slot = row * 9 + col); 39 / 41 (Classes / Fishing) and 27 (Quests) stay FREE
MAIN_D = {'Pets': (0, 3), 'Skills': (0, 4), 'Void Charms': (0, 5), 'Island Menu': (1, 3), 'Teleport': (1, 4), 'Crafting': (1, 5), 'Bank': (2, 3), 'Bazaar': (2, 4), 'Auction House': (2, 5), 'Vault': (3, 2), 'Reforge': (3, 3), 'Identify': (3, 4), 'Pocket Dimension': (3, 5), 'Your Profile': (3, 6), 'Collections': (4, 4), 'Players': (0, 0), 'Party': (1, 0), 'Guild': (2, 0), 'Wardrobe': (4, 0), 'Hover Tooltips': (0, 8), 'Settings': (1, 8), 'HUD Editor': (2, 8), 'Mods': (3, 8), 'Server Setup': (4, 8)}
MAIN_FREE = (11, 27, 39, 41)   # 0.3.27: slot 11 (the old Shards tile) is free again
# 0.3.16: PER-TILE VISIBILITY RULES (Skyy "can we control what's visible in the menu with permissions? or do we have to make several
# menus?" -> ONE menu, a rule per tile). tile name -> {"perm": node the player needs (ADMIN_NODE = the admin check MenuUtil.isAdmin),
# "open": a Server Setup switch that shows the tile to everyone anyway (only "modsHelp" = menu.modsHelp), "need": a bridge key that must
# hold a java.util.function.Function, "unlock": a bridge key - while it holds a Function, apply(UUID player) must answer Boolean.TRUE (an
# absent key = shown as today)}. A hidden tile leaves its slot empty. Ranks / earned unlocks plug in here later (data only).
TILE_RULES = {
    "Server Setup": {"perm": ADMIN_NODE},
    "Mods": {"perm": ADMIN_NODE, "open": "modsHelp"},
    "Bank": {"unlock": "bank:fn:unlocked"},
    "Wardrobe": {"need": "wardrobe:fn:open"},
}
TILE_OPEN = ("modsHelp",)                     # 0.3.16: the switches a rule may name (MenuPage.tileVisible knows each one)
_main = dict((e[3], e) for e in ENTRIES if e[0] == "main")
assert sorted(_main) == sorted(MAIN_D) and len(_main) == len([e for e in ENTRIES if e[0] == "main"]), "0.3.16: every main tile has a D slot"
for _t, (_r, _c) in MAIN_D.items():
    assert 0 <= _r < 5 and 0 <= _c < 9 and _main[_t][1] == _r * 9 + _c, "0.3.16: %s belongs at row %d col %d = slot %d" % (_t, _r, _c, _r * 9 + _c)
assert len(set(MAIN_D.values())) == len(MAIN_D) and not set(MAIN_FREE) & set(e[1] for e in _main.values()), "0.3.16: D slots unique, free slots free"
assert _main["Teleport"][1] == 13 and _main["Teleport"][6] == "view:tp", "0.3.16: Teleport on slot 13 (under the mouse when the menu opens)"
assert [_main[t][1] for t in ("Players", "Party", "Guild", "Wardrobe")] == [0, 9, 18, 36], "0.3.16: the social bar down the left edge"
assert [_main[t][1] for t in ("Hover Tooltips", "Settings", "HUD Editor", "Mods", "Server Setup")] == [8, 17, 26, 35, 44], "0.3.16: the right bar"
for _t, _e in _main.items():
    assert _e[2] == (MENU_ICON_OF.get(_t) if _t not in ("Pets", "Wardrobe") else _e[2]), "0.3.16: %s wears its own icon" % _t   # 0.3.26: Shards too
assert _main["Pets"][2] == ICON_PETS and _main["Wardrobe"][2] == "Skyy_Menu_Icon_Requip" and _main["Wardrobe"][6] == "bridge:wardrobe:fn:open"
# 0.3.27: the Shards tile is gone - no tile, no rule, no action names the shard menu (each shard's menu opens only from its portal)
assert "Shards" not in _main and "Shards" not in TILE_RULES and not [e for e in ENTRIES if "shard:fn:open" in e[6]], "0.3.27: the Shards tile is gone"
assert 11 in MAIN_FREE and 11 not in [e[1] for e in _main.values()], "0.3.27: slot 11 is free"
assert [l for l in _main["Island Menu"][4] if l.startswith("Shards: right-click")], "0.3.27: the Island Menu tile tells where shard menus open"
_BRK = re.compile(r"^[a-z][a-z0-9]*:fn:[A-Za-z][A-Za-z0-9]*$")
for _t, _rl in TILE_RULES.items():
    assert _t in _main and set(_rl) <= set(["perm", "open", "need", "unlock"]) and _rl, "0.3.16: rule of an unknown tile / key: %s %s" % (_t, _rl)
    assert "perm" not in _rl or re.match(r"^[a-z][a-z0-9]*(\.[a-z0-9]+)+$", _rl["perm"]), "0.3.16: %s perm node" % _t
    assert "open" not in _rl or ("perm" in _rl and _rl["open"] in TILE_OPEN), "0.3.16: %s open needs a perm + a known switch" % _t
    assert all(_BRK.match(_rl[_k]) for _k in ("need", "unlock") if _k in _rl), "0.3.16: %s bridge keys look like <mod>:fn:<name>" % _t
assert [e[3] for e in ENTRIES if e[6] == "admin"] == ["Server Setup"] and TILE_RULES["Server Setup"] == {"perm": ADMIN_NODE}, "0.3.16: Server Setup = admins"
assert [e[3] for e in ENTRIES if e[6] == "view:mods"] == ["Mods"] and TILE_RULES["Mods"] == {"perm": ADMIN_NODE, "open": "modsHelp"}, \
    "0.3.16: Mods = admins, or everyone while menu.modsHelp is on (0.3.15's rule)"
for _e in ENTRIES:
    assert not _e[6].startswith("bridge:") or (_e[0] == "main" and TILE_RULES.get(_e[3], {}).get("need") == _e[6][7:]), \
        "0.3.16: a bridge tile is drawn only while its Function exists: %s" % _e[3]
def _rule(e, k):
    return TILE_RULES.get(e[3], {}).get(k, "") if e[0] == "main" else ""
E_PERM = [_rule(e, "perm") for e in ENTRIES]; E_OPEN = [_rule(e, "open") for e in ENTRIES]
E_NEED = [_rule(e, "need") for e in ENTRIES]; E_UNLOCK = [_rule(e, "unlock") for e in ENTRIES]
E_VIEW = [e[0] for e in ENTRIES]; E_SLOT = [e[1] for e in ENTRIES]; E_ICON = [e[2] for e in ENTRIES]
# 0.3.17: THE MENU LAYOUT EDITOR's saved files (0.3.29: the 9 x 6 editor is retired - Home's Edit shortcuts replaces it). Tile keys (E_KEY) =
# the tile name, lower case, letters / digits only - the 0.3.28 tile lines of Skyy_SkyyMenu/layouts/<uuid>.properties and
# Skyy_SkyyMenu/layout-default.properties use them; rows 0 - 4 (slots 0 - 44) held the layout.
LAY_GRID = 45                                 # slots 0 - 44 can hold a tile
ICON_EMPTY = "Editor_Empty"                   # an empty slot in edit mode
EDIT_TXT = {
    # fix round: a hidden tile's slot is NOT marked in edit mode (no "Kept slot" - restricted tiles stay fully hidden, the 2026-09-25 rule);
    # it is simply not clickable. KEPT_MSG only answers a stale / forged click on it and names nothing.
    "KEPT_MSG": "That slot cannot be used - pick a tile or a slot with a glass marker.",
    "EDIT_WAIT": "Your saved layout cannot be read right now - nothing changed. Try again soon.",
}
for _k, _v in EDIT_TXT.items():
    for _ln in _v.split("\n"):
        assert txt(_ln) == _ln and len(_ln) <= 80, "0.3.17: editor text %s line too long / not safe: %s" % (_k, _ln)
need_item(ICON_EMPTY)
need_icon(ICON_EMPTY)
_ekey = _tilekey                     # 0.3.36: the saved keys stay (Void Charms = accessorybag)
E_KEY = [_ekey(e[3]) if e[0] == "main" else "" for e in ENTRIES]
_mk = [k for k in E_KEY if k]
assert len(_mk) == len(set(_mk)) == len([e for e in ENTRIES if e[0] == "main"]) and all(re.match(r"^[a-z][a-z0-9]{2,31}$", k) for k in _mk), \
    "0.3.17: every main tile has a unique saved-file key: %s" % _mk
assert all(e[1] < LAY_GRID for e in ENTRIES if e[0] == "main"), "0.3.17: the layout lives in rows 0 - 4"
print("0.3.17 layout tile keys", ", ".join(_mk))

# ---- 0.3.29: the shortcut tables against the 0.3.28 tiles (every main tile has its update rule; the defaults are valid keys)
for _k, _v in HOME_TXT.items():
    for _ln in _v.split("\n"):
        assert txt(_ln) == _ln and len(_ln) <= 110, "0.3.29: Home text %s not safe / too long: %s" % (_k, _ln)
assert all(txt(v) == v for v in HUB_BLURB.values())
_mk29 = [k for k in E_KEY if k]
assert sorted(MIG) == sorted(_mk29), "0.3.29: every 0.3.28 tile has an update rule: %s" % sorted(set(MIG) ^ set(_mk29))
assert all(v in ("", "-") or v.startswith("=") or v in SUI.HUBS for v in MIG.values())
assert sorted(set(v for v in MIG.values() if v in SUI.HUBS)) == sorted(h for h in SUI.HUBS), "0.3.29: every hub covers at least one tile"
assert sorted(TILE_TAB) == sorted(k for k in _mk29 if k != "hovertooltips")
_tabs29 = set("%s:%s" % (h, t) for h, t, _o, _m, _l, _c in SUI.HUB_TABS)
assert all(v in _tabs29 for v in TILE_TAB.values()), "0.3.29: TILE_TAB names contract tabs only"
assert BUILTIN_HOME[HG_CENTRE] == "tab:world:teleport" and sorted(v[4:] for v in BUILTIN_HOME.values() if v.startswith("hub:")) == \
    sorted(_h for _h in SUI.HUBS if _h != "world") and HUB_DEFTAB["world"] == "teleport", \
    "0.3.30: the default Home = Teleport in the centre + the 6 other hubs (World IS the centre's page)"
assert all(abs(s_ // HG_COLS - HG_CR) <= 1 and abs(s_ % HG_COLS - HG_CC) <= 1 for s_ in BUILTIN_HOME), "0.3.29: the hubs sit one step around the centre"
assert BUILTIN_TP[HG_CENTRE] == "tp:hub" and sorted(BUILTIN_TP.values()) == sorted(TP_KEYS)
TPK_E = [[i for i, e in enumerate(ENTRIES) if e[0] == "tp" and e[6] == TP_KEYS[k]] for k in sorted(TP_KEYS)]
assert all(len(x) == 1 for x in TPK_E), "0.3.29: each teleport key is one Teleport-view entry"
print("0.3.29 shortcuts: home default", BUILTIN_HOME, "- teleport default", BUILTIN_TP, "- update rules", len(MIG))
E_NAME = [txt(e[3]) for e in ENTRIES]; E_BODY = [lines_of(e[4]) for e in ENTRIES]
E_FOOT = [txt(e[5]) if e[5] else None for e in ENTRIES]; E_ACT = [e[6] for e in ENTRIES]
for a in E_ACT:
    assert '"' not in a and "\\" not in a
PA = PLAYER_ACTIONS
# 0.3.3 (review): a Commands line marked (admin) or (staff) is admin-only too - it is never in MOD_BODY / MOD_OLD_BODY (the Mods text
# every player reads); admins read it in the "Admin only:" block (MOD_AONLY below = exactly the lines MOD_ADMIN lists on the Server
# Setup page: those Commands lines, then the MODS "admin" lines)
def admin_line(c):
    return "(admin)" in c or "(staff)" in c
def player_lines(cmds):
    return [c for c in cmds if not admin_line(c)]
def admin_lines(m):
    return [c for c in m["commands"] if admin_line(c)] + m.get("admin", [])
for _m in MODS:
    assert player_lines(_m["commands"]) and ("old" not in _m or player_lines(_m["old"]["commands"])), \
        "%s: every Commands line is admin-only - players need one line (e.g. 'No commands for players - ...')" % _m["mod"]
MOD_BODY = [txt(m["desc"]) + "\nCommands:\n" + "\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in player_lines(m["commands"]))
            for m in MODS]
MOD_OLD_NEED = [m["old"]["need"] if "old" in m else "" for m in MODS]
MOD_OLD_BODY = [(txt(m["old"]["desc"]) + "\nCommands:\n" + "\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in player_lines(m["old"]["commands"])))
                if "old" in m else "" for m in MODS]
for _i, _m in enumerate(MODS):
    assert MOD_ADMIN[_i] == "\n".join(c.replace("%ALIASES%", "") for c in admin_lines(_m)), "%s: MOD_ADMIN lines" % _m["mod"]
for _b in MOD_BODY + MOD_OLD_BODY:
    assert "(admin)" not in _b and "(staff)" not in _b, "an admin line in the players' Mods text: " + _b[:80]
# 0.3.1: the admin-only lines of the Mods view (MODS "admin"): admins read them under MOD_AHEAD between the description and the
# commands (MenuUtil.modBodyFor builds exactly MOD_ABODY at run time), players never see them. The tooltip opens ABOVE the icon, so
# an admin tooltip keeps to 14 detail lines.
MOD_AHEAD = "Admin only:"
# 0.3.3 (review): + the (admin) / (staff) Commands lines (admin_lines = the MOD_ADMIN lines), which MOD_BODY no longer carries
MOD_AONLY = ["\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in admin_lines(m)) for m in MODS]
# review 2026-09-25: MenuUtil.modBodyFor puts the admin block after the FIRST line of the text, so a description is one line (the
# info box wraps it); MOD_ABODY is built from its parts and must equal what modBodyFor makes of MOD_BODY
for _m in MODS:
    for _d in [_m["desc"]] + ([_m["old"]["desc"]] if "old" in _m else []):
        assert "\n" not in _d and "\r" not in _d, "%s: desc must be one line (the admin lines go after the first line)" % _m["mod"]
MOD_ABODY = [(txt(m["desc"]) + "\n" + MOD_AHEAD + "\n" + MOD_AONLY[i] + "\nCommands:\n" +
              "\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in player_lines(m["commands"]))) if MOD_AONLY[i] else MOD_BODY[i]
             for i, m in enumerate(MODS)]
def java_abody(b, a):
    """= MenuUtil.modBodyFor(k, true) on the text b (no "old" wording)"""
    if not a:
        return b
    nl = b.find("\n")
    return b + "\n" + MOD_AHEAD + "\n" + a if nl < 0 else b[:nl] + "\n" + MOD_AHEAD + "\n" + a + b[nl:]
for _i, _b in enumerate(MOD_ABODY):
    assert _b == java_abody(MOD_BODY[_i], MOD_AONLY[_i]), "%s: admin text differs from MenuUtil.modBodyFor" % MODS[_i]["mod"]
    assert len(_b.split("\n")) - 1 <= 14, "%s: the admin tooltip has %d detail lines (max 14)" % (MODS[_i]["mod"], len(_b.split("\n")) - 1)
MOD_SINCE = [m["setup"][0] if "setup" in m else "" for m in MODS]
MOD_STITLE = [txt(m["setup"][1]) if "setup" in m else "" for m in MODS]
MOD_SWHAT = [txt(m["setup"][2]) if "setup" in m else "" for m in MODS]
# Info-box detail lines go into #SkyyMInfo0..8: fixed 14 px labels WITHOUT Wrap (a wrapped second row would spill into the next
# label), about 730 px wide at FontSize 14 (0.1.2: everything 1.4x, so the same characters fit). Keep every static detail line short enough to fit on one row. The first line of each
# body goes to #SkyyMInfoDesc (wraps) and the hover tooltips always carry the full text.
INFO_MAX = 80
for _body in (E_BODY + MOD_BODY + MOD_ABODY + [b for b in MOD_OLD_BODY if b] + [lines_of(v[2]) for v in VIEWS] +
              [lines_of(a[3]).replace("%P", "W" * 16) for a in PA] + [lines_of(a[3]).replace("%P", "W" * 16) for a in PA_LEGACY]):
    for _l in _body.split("\n")[1:]:
        assert len(_l) <= INFO_MAX, "info line longer than %d characters (unwrapped label, may be cut off - shorten it): %s" % (INFO_MAX, _l)

# ================= 0.3.10 THE STATS PAGE (research/cloud/Stats-Page-Spec.md P1): markup from the shared vanilla kit tools/skyyui.py =================
# Built when this script runs: SUI.verify() proves every vanilla value / texture / sound against Assets.zip (read-only) and stops the
# build on drift. Only properties the deployed kit pages use (SUI.assert_proven); every id starts with SkyyStat, no underscores.
SUI.verify(assets_zip=ASSETS_ZIP)   # 0.3.26: the cached copy
SUI_KIT_ID = SUI.kit_id()
ST_W, ST_H = SUI.HUB_PAGE_W, SUI.HUB_PAGE_H   # 0.3.35: the kit 1.7 hub page (0.3.28 - 0.3.34: 1114 x 974)
                                     # 0.3.33: + 8 (the sub-tab row 32 + 4 replaces the 24 px caption row and grows it)
ST_SUBTABS = ("Your Stats", "Skills")  # 0.3.33: the Skills tab's two sub-views (Skyy 2026-10-16 "Merge now": Stats + Skills = one tab)
ST_SUBTAB_W, ST_SUBROW_B, ST_SUBCAP_L = SUI.SUB_TAB_W, 4, 12   # 0.3.35: the kit's 150 px sub-tabs
ST_TABS = ["Main", "Combat", "Gathering", "Skills", "Profile"]
ST_NOTES = [
    "Health, Mana, Stamina: your max now. Base = the game's own part and armor.",
    "Gear = your held weapon and worn armor. Stats not built yet are hidden.",
    "Fortune = chance for a double drop (tools add more later). Wisdom = more XP.",
    "Your skill levels on this profile. /skills shows your XP and rewards.",
    "Each profile has its own class, skills and stats. Change Profile lists them.",
]
ST_SUB = "What applies to you right now. Click Refresh after you change your gear."
ST_LINE_MAX = 79                     # a stat row (name + total + source + 2) and every header / note line stays under 80 characters
ST_ROW_H, ST_ROW_GAP = 38, 2
ST_NAME_W, ST_VAL_W, ST_MID_W = 300, 200, 30
ST_NAME_FS, ST_VAL_FS, ST_SRC_FS = 18, 18, 15
ST_FOOT_PROF_W, ST_FOOT_GAP = 200, 6   # 0.3.35: the menu button went (row 1 Home)
# the gear stats the page shows: SkyyGear's LIVE rows (key, page label, short label, unit). spd (Speed) is shown from the movement
# map (what is applied), the "coming later" rows are hidden (spec default). Cross-checked against the SET SkyyGear script below.
ST_GEAR = [("def", "Defense", "Defense", ""), ("str", "Strength", "Strength", ""), ("cc", "Crit Chance", "Crit", "%"),
           ("cd", "Crit Damage", "Crit Dmg", "%"), ("mp", "Magical Power", "Magic", ""), ("stam", "Stamina Regen", "Stamina", ""),
           ("dmg", "Damage", "Damage", "%"), ("chg", "Charged Attack Damage", "Charged", "%"), ("tdmg", "True Damage", "True", ""),
           ("lsteal", "Life Steal", "Life Steal", "%"), ("msteal", "Mana Steal", "Mana Steal", ""),
           ("hpr", "Health Regen", "Regen", ""), ("hprp", "Health Regen %", "Regen", "%")]
ST_ELEM = [("fEarth", "Earth"), ("fThunder", "Thunder"), ("fWater", "Water"), ("fFire", "Fire"), ("fAir", "Air")]
ST_RAW = [("rThunder", "Thunder"), ("rWater", "Water"), ("rElem", "Elemental")]
ST_GROUPS = ["Gear", "Accessories", "Overall", "Class", "Base Mana", "Skills", "Trees"]   # short: a Health row holds five parts
ST_FORTUNE = [("Mining", "mining"), ("Foraging", "foraging"), ("Farming", "farming")]
ST_WISDOM = [("Mining", "mining"), ("Foraging", "foraging"), ("Farming", "farming"), ("Cooking", "cooking")]
for _t in ST_NOTES + [ST_SUB]:
    assert len(_t) <= ST_LINE_MAX, "stats line over %d characters: %s" % (ST_LINE_MAX, _t)
# the SET SkyyGear script's LIVE stat rows (key, label, unit, live) - a row this page shows must still be a LIVE row with the same unit
_gear_ver = dict(_LIVE).get("SkyyGear") if _LIVE else None
_gear_py = os.path.join(B.PROJECT, "SkyyGear", "build_skyygear_%s.py" % _gear_ver) if _gear_ver else None
if _gear_py and os.path.isfile(_gear_py):
    _gt = open(_gear_py, encoding="utf-8").read()
    _grows = dict((m.group(1), (m.group(2), m.group(3), m.group(4))) for m in
                  re.finditer(r'\("(\w+)", "([^"]+)", "[wsae]+", "(%?)", \d+, \d+, ([01]), "\w*"\)', _gt))
    for _k, _lab, _short, _u in ST_GEAR + [(k, l, l, "") for k, l in ST_ELEM + ST_RAW]:
        assert _k in _grows, "SkyyGear %s has no stat %s any more" % (_gear_ver, _k)
        assert _grows[_k][2] == "1", "SkyyGear %s: %s is not a LIVE stat (the Stats page hides planned stats)" % (_gear_ver, _k)
        if _k in [g[0] for g in ST_GEAR]:
            assert _grows[_k][1] == _u, "SkyyGear %s: %s unit %r, the page says %r" % (_gear_ver, _k, _grows[_k][1], _u)
    print("stats page: %d gear stats checked against SkyyGear %s (LIVE rows, units)" % (len(ST_GEAR) + len(ST_ELEM) + len(ST_RAW), _gear_ver))
else:
    print("WARNING stats page: no SET SkyyGear script found - the gear stat list was not cross-checked")


def stats_page():
    """0.3.35 (research/Menu-Pattern.md M4; Skyy popup 4 "Your Stats = one scroll list with headings": YES): the Skills tab's YOUR STATS view
    on the kit 1.7 hub_page - row 1, row 2 (Skills selected: Stats is part of it), the ONE sub-tab row YOUR STATS | SKILLS + the caption,
    the heading line, ONE scroll list (the Main / Combat / Gathering section heads + their stat rows; the old Skills and Profile tabs went -
    duplicates of the Skills list and Profiles), the footer: the message line, Refresh, Change Profile (Primary), Close.
    Returns (shell, stat row, head row, foot, sub-tab caption, source width)."""
    J = SUI.J
    sh = SUI.hub_page("SkyyStatF", "character", body_id="SkyyStatFB", content_id="SkyyStat", sub=True, footer=True)
    ap, body, IW = sh.appends, sh.content, sh.content_w
    subw = SUI.assert_sub_tabs_fit(list(ST_SUBTABS), ST_SUBTAB_W)
    capw = SUI.HUB_PAGE_IW - subw - ST_SUBCAP_L
    assert SUI.text_width(ST_SUB, ST_SRC_FS) <= capw, "0.3.35: the caption fits beside the sub-tabs"
    cap = SUI.label("SkyyStatSub", "", "caption", w=capw, h=SUI.SUB_TAB_H, size=ST_SRC_FS, anchor={"left": ST_SUBCAP_L})
    used = [ap.add(body, SUI.label("SkyyStatHead", "", "heading", h=30, size=20, wrap=False, anchor={"bottom": 6}))]
    list_h = sh.content_h - sum(used)
    used.append(ap.add(body, SUI.scroll_list("SkyyStatList", h=list_h, well=True)))
    left = sh.fit(used)
    assert left >= 0, "stats page parts do not fit"
    # one stat row: name | total (right-aligned) | gap | where it comes from; a section head: the section name | its note
    row_w = IW - 2 * SUI.WELL_LIST_PAD - 24
    src_w = row_w - ST_NAME_W - ST_VAL_W - ST_MID_W
    rid = J("i", "0")
    rows = [("SkyyStatList", SUI.group("SkyyStatR" + rid, "Left", h=ST_ROW_H, anchor={"bottom": ST_ROW_GAP})),
            ("SkyyStatR" + rid, SUI.label("SkyyStatN" + rid, "", "rowName", w=ST_NAME_W, h=ST_ROW_H, size=ST_NAME_FS, anchor={"left": 8})),
            ("SkyyStatR" + rid, SUI.label("SkyyStatV" + rid, "", "rowName", w=ST_VAL_W - 8, h=ST_ROW_H, size=ST_VAL_FS, align="End")),
            ("SkyyStatR" + rid, SUI.spacer(w=ST_MID_W, h=ST_ROW_H)),
            ("SkyyStatR" + rid, SUI.label("SkyyStatS" + rid, "", "rowSub", w=src_w, h=ST_ROW_H, size=ST_SRC_FS))]
    head = [("SkyyStatList", SUI.group("SkyyStatR" + rid, "Left", h=ST_HEAD_H, anchor={"top": 6, "bottom": ST_ROW_GAP})),
            ("SkyyStatR" + rid, SUI.label("SkyyStatN" + rid, "", "settingHead", w=ST_NAME_W + ST_VAL_W - 8, h=ST_HEAD_H, anchor={"left": 8})),
            ("SkyyStatR" + rid, SUI.label("SkyyStatS" + rid, "", "caption", w=row_w - ST_NAME_W - ST_VAL_W, h=ST_HEAD_H, size=ST_SRC_FS))]
    # the footer: the message line, Refresh, Change Profile (Primary; or a spacer of its width), Close - filled exactly
    g = SUI.FOOT_GAP
    msg_w = SUI.HUB_PAGE_IW - (g + SUI.BTN_MIN_W + g + ST_FOOT_PROF_W + g + SUI.BTN_MIN_W)
    foot = {
        "msg": SUI.label("SkyyStatMsg", "", "bold", w=msg_w, h=SUI.FOOT_BTN_H, size=16, col="info", wrap=True, padding={"horizontal": 8}),
        "gap": SUI.spacer(w=g),
        "refresh": SUI.foot_button("SkyyStatRefresh", "Refresh"),
        "profile": SUI.foot_button("SkyyStatProfile", "Change Profile", ST_FOOT_PROF_W, kind="primary"),
        "noprofile": SUI.spacer(w=ST_FOOT_PROF_W, h=SUI.FOOT_BTN_H),
        "close": SUI.foot_button("SkyyStatClose", "Close", sound="cancel"),
    }
    # every look this page can show, checked as one page (ids, parents, markup rules, proven properties only, the menu pattern)
    chk = SUI.hub_page_preview(sh, tabs=[(r[0], SUI.hub_tab_label("character", r[0])) for r in SUI.hub_page_tabs("character")], my_tab="skills")
    chk.extend(SUI.sub_tabs_preview("SkyyStatF", list(ST_SUBTABS), 0, ST_SUBTAB_W))
    chk.append(("SkyyStatFSub", cap))
    chk.extend(rows)
    hc = SUI.Appends([(p_.replace("SkyyStatR" + rid, "SkyyStatRh"), SUI.render(mk).replace("SkyyStatN" + SUI.render(rid), "SkyyStatNh")
                       .replace("SkyyStatS" + SUI.render(rid), "SkyyStatSh").replace("SkyyStatR" + SUI.render(rid), "SkyyStatRh")) for p_, mk in head])
    chk.extend(hc)
    for k in ("msg", "gap", "refresh", "gap", "profile", "gap", "close"):
        chk.append(("SkyyStatFFoot", foot[k]))
    chk.check("SkyyStat")
    SUI.assert_proven(chk, what="stats page")
    SUI.assert_proven([foot["noprofile"]], what="stats page footer spacer")
    SUI.check_sky_paths(chk, tab_icons=True)
    SUI.assert_menu_page(chk, sh)
    assert sum(SUI.outer_size(foot[k])[0] for k in ("msg", "gap", "refresh", "gap", "profile", "gap", "close")) == SUI.HUB_PAGE_IW, "footer not filled exactly"
    # every fixed text fits its label (the client's own font tables)
    for _t in ST_NOTES[:3]:
        assert SUI.text_width(_t, ST_SRC_FS) <= row_w - ST_NAME_W - ST_VAL_W, "stats note too wide: " + _t
    for _t in ("Charged Attack Damage", "Collection Recipes", "Other class skills", "Raw Elemental Damage"):
        assert SUI.text_width(_t, ST_NAME_FS, bold=True) <= ST_NAME_W - 8, "stat name too wide: " + _t
    for _t in ("1,000,000,000%", "999,999,999,999", "Level 100", "+1,000,000,000%"):
        assert SUI.text_width(_t, ST_VAL_FS, bold=True) <= ST_VAL_W - 8, "stat total too wide: " + _t
    return sh, rows, head, foot, cap, src_w, left


ST_ROWS = 14                         # (StatsCalc.ROWS: the class-skill packing rule; the page itself has no row limit any more)
ST_HEAD_H = 40
ST_SECTIONS = 3                      # 0.3.35: Main, Combat, Gathering (ST_TABS[:3]) - Skills and Profile went (duplicates)
ST_SH, ST_ROW_MK, ST_HEAD_MK, ST_FOOT_MK, ST_CAP_MK, ST_SRC_W, ST_LEFT = stats_page()
# a stat row's longest source text (the Java clips name + total + source to ST_LINE_MAX characters) fits its column
for _t in ("Gear +40, Accessories +12, Overall +7, Skills +18, Trees +5, base 9",
           "Accessories +4, Overall +2.8, Class +10, Base Mana +10, Skills +2.4, base 9",
           "W" * 8 + " level 100 +50%, Skill trees +50% (max 100%)",
           "some blocks only: Foraging level 100 +50%, Skill trees +50% (max 100%)",
           "Swordsmanship 100, Assassination 100, Zen 100, Sorcery 100",
           "Swordsmanship level 100 +20%, Class balance +12.5%"):   # 0.3.13: the Class Weapon Damage row with skill:dmg
    assert SUI.text_width(_t, ST_SRC_FS) <= ST_SRC_W, "source column too narrow for: " + _t
ST_SHELL_JAVA = ST_SH.java("b")
ST_ROW_JAVA = "\n".join(SUI.java_append(p, mk) for p, mk in ST_ROW_MK)
ST_HEAD_JAVA = "\n".join(SUI.java_append(p, mk) for p, mk in ST_HEAD_MK)
ST_FOOT_JAVA = dict((k, SUI.java_append("SkyyStatFFoot", mk)) for k, mk in ST_FOOT_MK.items())
ST_SUB_JAVA = "\n".join(['@PKG@.HubBar.subTab(b, ev, "SkyyStatF", 0, %s, true, "hub:stats", %d);' % (SUI.java_lit(ST_SUBTABS[0]), ST_SUBTAB_W),
                         '@PKG@.HubBar.subTab(b, ev, "SkyyStatF", 1, %s, false, "hub:skills", %d);' % (SUI.java_lit(ST_SUBTABS[1]), ST_SUBTAB_W),
                         SUI.java_append("SkyyStatFSub", ST_CAP_MK)])
ST_STATIC = [SUI.render(mk) for _p, mk in ST_SH.appends if not SUI.has_j(mk)]
print("stats page: %d x %d, one scroll list (%d sections), %d px left in the body, kit %s" % (ST_W, ST_H, ST_SECTIONS, ST_LEFT, SUI_KIT_ID))

# ================= 0.3.29 UNIFIED MENU: every Menu page in the kit 1.6 ROW SHELL + the Home page + the Teleport page =================
# kit 1.6 (tools/HUBS-CONTRACT.md "Kit 1.6"): row 1 = Home + the hubs in the 38 px title bar where "< Menu" + the title were, so no page
# grows (assert_hub_page as in 0.3.28); the tab strip stays row 2. Clicks: HubBar.route (MenuHub.click) - "hub:h:home" = Home in place.
assert SUI.HUB_THEME == "sky" and SUI.THEME_PAD["sky"] == 24 and SUI.KIT_VERSION == "1.5" and SUI.KIT_HUB_VERSION == "1.6", \
    "0.3.29: kit skyyui 1.6 (KIT_VERSION stays 1.5), hub pages in the sky theme"
HUB_PAD = SUI.THEME_PAD["sky"]
# 0.3.35 MENU PATTERN (research/Menu-Pattern.md 3; kit 1.7): every Menu page is the 1600 x 980 hub_page - row 1 (HubBar.bigRowFill), row 2
# (HubBar.bigTabsFill) and the X from HubBar.page17; no page draws its own bars or a back button any more.
assert SUI.KIT_PAGE_VERSION == "1.7" and SUI.HUB_PAGE_IW == 1552, "0.3.35: kit 1.7 (hub_page)"
MH_W, MH_H = SUI.HUB_PAGE_W, SUI.HUB_PAGE_H          # the classic menu views (Players, a player, Mods): 1600 x 980 (0.3.34: 804 x 980)
APW, APH = SUI.HUB_PAGE_W, SUI.HUB_PAGE_H            # Server Setup: 1600 x 980 (its body stays A_INNER = 1080 wide, centred)
MENU_HUB_SH =dict((h, SUI.hub_page("SkyyMenuH", h, body_id="SkyyMenuHB", content_id="SkyyMenu", content_layout="Left", footer=True))
                   for h in ("social", "settings"))
STG_HUB_SH = SUI.hub_page("SkyyStgH", "settings", body_id="SkyyStgHB", content_id="SkyyStg", sub=True, footer=True)
ADM_HUB_SH = SUI.hub_page("SkyyAdmH", "settings", body_id="SkyyAdmHB", content_id="SkyyAdm", content_w=A_INNER, sub=True, footer=True)
assert STG_HUB_SH.content_h == STG_CH and ADM_HUB_SH.content_h == A_BODY and ADM_HUB_SH.content_w == A_INNER, "0.3.35: the Settings / Server Setup content"
# THE CLASSIC VIEWS (Social > Players, a player's page, Settings > Mods): the 9 x 6 grid (96 px slots) on the left, the info panel on the
# right, the footer = the hint / status line, the grid's page arrows (a grid of slots keeps pages - menu-pattern-ok) and Close. The grid's
# Go Back / Close / page tiles went: row 2's Players tab leads back from a player's page, row 1 Home from everywhere.
CL_SLOT, CL_ICON = 96, 70
CL_GW, CL_GH = CL_SLOT * COLS, CL_SLOT * ROWS          # 864 x 576
CL_GAP = 20
CL_INFO_W = SUI.HUB_PAGE_IW - CL_GW - CL_GAP           # 668
CL_INFO_LINES = 18
CL_DESC_H = 84                                         # the wrapped first line: 4 lines of 16 px (0.3.34: 2 lines in a 728 px box)
CL_BTN_W, CL_CLOSE_W = 150, 170
CL_HINT_W = SUI.HUB_PAGE_IW - 2 * CL_BTN_W - CL_CLOSE_W - 3 * SUI.FOOT_GAP
_clgrid = lambda tips: ("ItemGrid #SkyyMGrid { Anchor: (Horizontal: 0, Top: 3, Width: %d, Height: %d); SlotsPerRow: %d; AreItemsDraggable: false; %s"
                        "Style: (SlotSize: %d, SlotIconSize: %d, SlotSpacing: 0); }" % (CL_GW, CL_GH, COLS, "" if tips else "InfoDisplay: None; ", CL_SLOT, CL_ICON))
UI35 = {
    "CGRIDWRAP": "Group #SkyyMGridWrap { Anchor: (Width: %d, Height: %d); }" % (CL_GW, CL_GH + 6),
    "CGRID": _clgrid(True),
    "CGRIDNT": _clgrid(False),
    "CGAP": SUI.spacer(w=CL_GAP),
    "CINFOBOX": "Group #SkyyMInfoBox { Anchor: (Width: %d, Height: %d); LayoutMode: Top; Padding: (Horizontal: 16, Vertical: 12); Background: %s; }" % (
        CL_INFO_W, CL_GH + 6, SUI.THEME["sky"]["inset"]),
    "CINFONAME": SUI.label("SkyyMInfoName", "", "heading", h=32, size=20, wrap=False),
    "CINFODESC": SUI.label("SkyyMInfoDesc", "", "default", h=CL_DESC_H, size=16, col="rowName", wrap=True),
    "CHINT": SUI.foot_info("SkyyMHint", CL_HINT_W),
    "CHINTST": SUI.label("SkyyMHint", "", "gold", h=SUI.FOOT_BTN_H, w=CL_HINT_W, size=16, wrap=True, padding={"horizontal": 8}),
    "CFSP": SUI.spacer(w=SUI.FOOT_GAP),
    "CNOPAGE": SUI.spacer(w=2 * CL_BTN_W + 2 * SUI.FOOT_GAP, h=SUI.FOOT_BTN_H),
    "CPREV": SUI.foot_button("SkyyMPrev", "< Prev", CL_BTN_W),    # menu-pattern-ok: the grid's slot pages
    "CNEXT": SUI.foot_button("SkyyMNext", "Next >", CL_BTN_W),    # menu-pattern-ok: the grid's slot pages
    "CCLOSE": SUI.foot_button("SkyyMClose", "Close", CL_CLOSE_W, sound="cancel"),
}
UI35_CINFO = [SUI.label("SkyyMInfo%d" % i, "", "default", h=22, size=15, wrap=False) for i in range(CL_INFO_LINES)]
assert 32 + CL_DESC_H + CL_INFO_LINES * 22 + 24 <= CL_GH + 6 and CL_GH + 6 <= MENU_HUB_SH["social"].content_h, "0.3.35: the classic info panel + grid fit"
assert CL_HINT_W + SUI.FOOT_GAP + 2 * (CL_BTN_W + SUI.FOOT_GAP) + CL_CLOSE_W == SUI.HUB_PAGE_IW, "0.3.35: the classic footer is filled exactly"
for _h, _sh in MENU_HUB_SH.items():
    _cv = SUI.hub_page_preview(_sh, tabs=[(r[0], SUI.hub_tab_label(_h, r[0])) for r in SUI.hub_page_tabs(_h)], my_tab="players" if _h == "social" else "mods")
    for _k in ("CGRIDWRAP", "CGAP", "CINFOBOX"):
        _cv.append(("SkyyMenu", UI35[_k]))
    _cv.append(("SkyyMGridWrap", UI35["CGRID"]))
    for _k in ("CINFONAME", "CINFODESC"):
        _cv.append(("SkyyMInfoBox", UI35[_k]))
    for _mk in UI35_CINFO:
        _cv.append(("SkyyMInfoBox", _mk))
    for _k in ("CHINT", "CFSP", "CPREV", "CFSP", "CNEXT", "CFSP", "CCLOSE"):
        _cv.append(("SkyyMenuHFoot", UI35[_k]))
    SUI.check_page(_cv, "SkyyM")
    SUI.assert_proven(_cv, what="classic %s view" % _h)
    SUI.check_sky_paths(_cv, tab_icons=True)
    SUI.assert_menu_page(_cv, _sh, pager_ok=True)       # the grid's slot pages (a page of real slots, like the Vault)
    assert SUI.used_width(SUI.Appends([(p_, mk) for p_, mk in _cv if p_ == "SkyyMenu"]), "SkyyMenu") <= SUI.HUB_PAGE_IW, "0.3.35: the classic content fits"

# ---- 0.3.30: HOME + TELEPORT SCALED UP (Skyy 2026-10-16 "scale up this menu a lot"): 120 px slots / 88 px icons (were 84 / 62), You and
# Right now 456 px wide (were 300) with 20 px lines, foot buttons in the normal size (48 px), and BOTH tab rows drawn big INSIDE the body:
# row 1 (Home + the hubs: 48 px buttons, 32 px item icons, 18 px labels) and, on Teleport, row 2 (the World tabs: 56 px, the 48 px tab icon
# behind each word, 20 px labels). The title bar keeps the kit's fixed 38 px Header (it holds the crest + the page title; the kit says
# never scale it). Ids start with SkyyM (the grid keeps #SkyyMGrid: the same slot binding, clearGrid and click path). Every page stays
# inside the kit's 1600 x 980 page (1080p with the vanilla UI scale); the centre slot keeps 0.3.28 slot 13's screen spot (asserted).
SLOT30, SLOT30_ICON = 120, 88
HG_W, HG_H = SLOT30 * HG_COLS, SLOT30 * HG_ROWS        # 600 x 600
HOME_W = SUI.MAX_PAGE_W                                  # 1600
HOME_GAP = 20
HOME_SIDE = (HOME_W - 2 * HUB_PAD - HG_W - 2 * HOME_GAP) // 2
YOU_PAD = 18
YOU_BAR_W = HOME_SIDE - 2 * YOU_PAD
# row 1 (big): BR_*; row 2 (big, Teleport): BT_*
BR_H, BR_GAP, BR_BELOW, BR_PAD, BR_PADV, BR_ICON, BR_ICON_GAP, BR_LAB, BR_LAB_MIN, BR_ICON_MIN = 48, 6, 8, 10, 6, 32, 6, 18, 12, 120
BT_H, BT_BELOW, BT_GAP, BT_ICON, BT_LAB, BT_LAB_MIN, BT_MIN, BT_PAD = 56, 8, 6, 48, 20, 14, 150, 8
BT_ICON_TOP = (BT_H - BT_ICON) // 2
BR_LABN = ("(FontSize: %d, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center, ShrinkTextToFit: true, "
           "MinShrinkTextToFitFontSize: %d)" % (BR_LAB, SUI.color("button2Text"), BR_LAB_MIN))
BR_LABSEL = ("(FontSize: %d, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center, ShrinkTextToFit: true, "
             "MinShrinkTextToFitFontSize: %d)" % (BR_LAB, SUI.color("buttonText"), BR_LAB_MIN))
BT_LAB = ("(FontSize: %d, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: %d, "
          "VerticalAlignment: Center)" % (BT_LAB, SUI.color("buttonText"), BT_LAB_MIN))
HOME_MIDT_H, HOME_MIDGAP, HOME_GRID_TOP = 40, 6, 3
HOME_MAIN_H = HOME_MIDT_H + HOME_MIDGAP + HOME_GRID_TOP + HG_H + 3
HOME_FOOT_H, HOME_FOOTGAP, FOOT_BTN_H = 56, 10, 48
HINFO_FS, HINFO_H = 16, 48                            # the Home info line: 16 px, wraps to TWO lines in its 48 px
HOME_H = SUI.HUB_PAGE_H                  # 0.3.35: 980 (the kit 1.7 hub page; 0.3.30 - 0.3.34: 926)
HOME_LEAD = (HOME_H - 926) // 2         # 0.3.35: 27 px above the Home body, so the grid's centre slot stays where it was on screen


# 0.3.35: big_shell (0.3.30 - 0.3.34) went - Home and Teleport are kit 1.7 hub pages (SUI.hub_page), their rows the kit's HubBar.page17


HOME_SH = SUI.hub_page("SkyyMHm", "home", title="SkyWynn Menu", body_id="SkyyMHmB", content_id="SkyyMHome")   # 0.3.35: kit 1.7
HOME_FOOT_W = HOME_ROW_W = HOME_SH.inner_w
assert (HOME_W, HOME_SH.inner_w, HOME_SIDE) == (1600, 1552, 456)
assert HOME_LEAD + HOME_MAIN_H + HOME_FOOTGAP + HOME_FOOT_H <= HOME_SH.inner_h and HOME_SH.w == HOME_W, "0.3.35: the Home body fits"
# ---- TELEPORT (World > Teleport): big row 1, big row 2 (the World tabs), the grid (centred by a lead), a two-line info box, the foot
TP_W, TP_H = SUI.HUB_PAGE_W, SUI.HUB_PAGE_H   # 0.3.35: 1600 x 980 (0.3.30 - 0.3.34: 1300 x 962)
TP_LEAD_Y = (TP_H - 962) // 2                 # 0.3.35: 9 px above the grid row (the centre slot keeps its screen spot)
TP_INFO_H, TP_GAP = 58, 8
TP_SH = SUI.hub_page("SkyyMTp", "world", body_id="SkyyMTpBody", content_id="SkyyMTpB")   # 0.3.35: kit 1.7
TP_FOOT_W = TP_ROW_W = TP_SH.inner_w
TP_LEAD = (TP_SH.inner_w - HG_W) // 2
assert TP_LEAD == 476 and TP_LEAD_Y + HG_H + HOME_GRID_TOP + TP_GAP + TP_INFO_H + TP_GAP + HOME_FOOT_H <= TP_SH.inner_h, \
    "0.3.30: the Teleport body fits"
# THE CENTRE SLOT UNDER THE MOUSE (Skyy: "open it, click twice, and be at my island without moving the mouse"). A page opens centred on the
# screen with the mouse at the screen centre; 0.3.28's slot 13 sat at the page centre + (0, +4) - computed from the 0.3.28 markup itself.
_hpx = lambda mk: int(re.search(r"Height: (\d+)", mk).group(1))
OLD_SLOT13 = (22 + OLD_CC * SLOT + SLOT // 2 - PW // 2,
              14 + _hpx(UI["ACCENT"]) + _hpx(UI["TITLE"]) + _hpx(UI["HINT"]) + _hpx(UI["INFOBOX"]) + _hpx(UI["GAP"]) + 3 + OLD_CR * SLOT + SLOT // 2 - PH // 2)
assert "Top: 3" in UI["GRID"] and "Padding: (Horizontal: 22, Vertical: 14)" in UI["ROOT"]
HOME_C = (HUB_PAD + HOME_SIDE + HOME_GAP + HG_CC * SLOT30 + SLOT30 // 2 - HOME_W // 2,
          SUI.TITLE_H + HUB_PAD + BR_H + BR_BELOW + HOME_LEAD + HOME_MIDT_H + HOME_MIDGAP + HOME_GRID_TOP + HG_CR * SLOT30 + SLOT30 // 2 - HOME_H // 2)
TP_C = (HUB_PAD + TP_LEAD + HG_CC * SLOT30 + SLOT30 // 2 - TP_W // 2,
        SUI.TITLE_H + HUB_PAD + BR_H + BR_BELOW + BT_H + BT_BELOW + TP_LEAD_Y + HOME_GRID_TOP + HG_CR * SLOT30 + SLOT30 // 2 - TP_H // 2)
assert OLD_SLOT13 == (0, 4) and HOME_C == OLD_SLOT13 and TP_C == OLD_SLOT13, "0.3.30: the centre slot keeps slot 13's screen spot %s / %s / %s" % (
    OLD_SLOT13, HOME_C, TP_C)
assert SUI.MAX_PAGE_H >= max(HOME_H, TP_H) and SUI.MAX_PAGE_W >= max(HOME_W, TP_W), "0.3.30: both pages fit 1080p"
_K = SUI.THEME["sky"]
_gridmk = lambda tips: ("ItemGrid #SkyyMGrid { Anchor: (Horizontal: 0, Top: %d, Width: %d, Height: %d); SlotsPerRow: %d; AreItemsDraggable: false; %s"
                        "Style: (SlotSize: %d, SlotIconSize: %d, SlotSpacing: 0); }" % (HOME_GRID_TOP, HG_W, HG_H, HG_COLS, "" if tips else "InfoDisplay: None; ",
                                                                                         SLOT30, SLOT30_ICON))
_ALAB = ("(FontSize: 17, TextColor: %s, RenderBold: true, HorizontalAlignment: Start, VerticalAlignment: Center, ShrinkTextToFit: true, "
         "MinShrinkTextToFitFontSize: 13)" % SUI.color("rowName"))
UI29 = {
    "HMAIN": SUI.group("SkyyMHmMain", "Left", h=HOME_MAIN_H),
    "HYOU": "Button #SkyyMHmYou { Anchor: (Width: %d, Height: %d); LayoutMode: Top; Padding: (Full: %d); Style: ButtonStyle(Default: (Background: %s), "
            "Hovered: (Background: %s), Pressed: (Background: %s), Sounds: %s); }" % (HOME_SIDE, HOME_MAIN_H, YOU_PAD, _K["panel"], _K["card"], _K["inset"],
                                                                                        SUI.sounds("light")),
    "HYT": SUI.label("SkyyMHmYT", HOME_TXT["HT_YOU_TITLE"], "panelTitle", h=32, size=20),
    "HYN": SUI.label("SkyyMHmYN", "", "heading", h=40, size=26, wrap=False),
    "HYBAR0": "Group #SkyyMHmYBar { Anchor: (Width: %d, Height: 12, Bottom: 8); Background: %s; Group #SkyyMHmYFill { Anchor: (Left: 0, Width: " % (
        YOU_BAR_W, SUI.color("progressTrack")),
    "HYBAR1": ", Height: 12); Background: %s; } }" % SUI.color("progressFill"),
    "HYH": SUI.label("SkyyMHmYH", HOME_TXT["HT_YOU_HINT"], "caption", h=30, size=17),
    "HSP16": SUI.spacer(w=HOME_GAP),
    "HMID": SUI.group("SkyyMHmMid", "Top", w=HG_W, h=HOME_MAIN_H),
    "HMIDT": SUI.label("SkyyMHmMidT", "", "heading", h=HOME_MIDT_H, size=22, align="Center", wrap=False),
    "HGAP5": SUI.spacer(h=HOME_MIDGAP),
    "HGW": "Group #SkyyMGW { Anchor: (Width: %d, Height: %d); }" % (HG_W, HG_H + HOME_GRID_TOP),
    "HGRID": _gridmk(True),
    "HGRIDNT": _gridmk(False),
    "HNOW": "Group #SkyyMHmNow { Anchor: (Width: %d, Height: %d); LayoutMode: Top; Padding: (Full: %d); Background: %s; }" % (HOME_SIDE, HOME_MAIN_H, YOU_PAD, _K["panel"]),
    "HNOWT": SUI.label("SkyyMHmNowT", HOME_TXT["HT_NOW_TITLE"], "panelTitle", h=32, size=20),
    "HNOWNONE": SUI.label("SkyyMHmNowE", HOME_TXT["HT_NOW_NONE"], "caption", h=34, size=18),
    "HGAP8": SUI.spacer(h=HOME_FOOTGAP),
    "HFOOT": "Group #SkyyMHmFoot { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: %d); }" % (HOME_FOOT_H, HOME_FOOT_H - FOOT_BTN_H - 4),
    "HINFO0": "Label #SkyyMHmInfo { Anchor: (Width: ",
    "HINFO1": ', Height: %d); Padding: (Horizontal: 8); Text: ""; Style: %s; }' % (HINFO_H, SUI.text_style(HINFO_FS, "rowName", wrap=True)),
    "FSP": SUI.spacer(w=10),
    "BROW": "Group #SkyyMBRow { Anchor: (Height: %d, Bottom: %d); LayoutMode: Left; }" % (BR_H, BR_BELOW),
    "BTABS": "Group #SkyyMBTabs { Anchor: (Height: %d, Bottom: %d); LayoutMode: Left; }" % (BT_H, BT_BELOW),
    "TROW": SUI.group("SkyyMTpRow", "Left", h=HG_H + HOME_GRID_TOP),
    "TLEAD": SUI.spacer(w=TP_LEAD),
    "TINFO": "Group #SkyyMTpInfo { Anchor: (Height: %d); LayoutMode: Top; Padding: (Horizontal: 16, Vertical: 4); Background: %s; }" % (TP_INFO_H, _K["inset"]),
    "TIN": SUI.label("SkyyMTpIN", "", "rowName", h=26, size=19, wrap=False),
    "TID": SUI.label("SkyyMTpID", "", "default", h=22, size=16, wrap=False),
    "TGAP": SUI.spacer(h=TP_GAP),
    "HLEAD": SUI.spacer(h=HOME_LEAD),        # 0.3.35
    "TLEADY": SUI.spacer(h=TP_LEAD_Y),       # 0.3.35
    "TFOOT": "Group #SkyyMTpFoot { Anchor: (Height: %d); LayoutMode: Left; Padding: (Top: %d); }" % (HOME_FOOT_H, HOME_FOOT_H - FOOT_BTN_H - 4),
}
UI29_HYL = [SUI.label("SkyyMHmYL%d" % i, "", "default", h=34, size=20, col="rowName", wrap=False) for i in range(7)]
UI29_HA = ['TextButton #SkyyMHmA%d { Anchor: (Height: 52, Bottom: 8); Padding: (Horizontal: 12); Text: ""; Style: TextButtonStyle(Default: (Background: %s, '
           'LabelStyle: %s), Hovered: (Background: %s, LabelStyle: %s), Pressed: (Background: %s, LabelStyle: %s), Sounds: %s); }' % (
               i, _K["row"], _ALAB, _K["rowHovered"], _ALAB, _K["rowSelected"], _ALAB, SUI.sounds("light")) for i in range(AL_SHOW)]
assert 32 + AL_SHOW * 60 + 2 * YOU_PAD <= HOME_MAIN_H and 32 + 40 + 7 * 34 + 20 + 30 + 2 * YOU_PAD <= HOME_MAIN_H, "0.3.30: You / Right now fit"
# the foot buttons (one table, both pages): word -> (label, width, kind, sound). The event is a = "f<word>". 0.3.30: the normal size, 48 px.
FB = [("hedit", "Edit shortcuts", 230, "secondary", None), ("close", "Close", 150, "secondary", "cancel"),
      ("prev", "< Prev", 130, "secondary", None), ("next", "Next >", 130, "secondary", None),   # menu-pattern-ok: the grid's slot pages
      ("eremove", "Remove", 130, "destructive", None), ("ereset", "Reset", 120, "secondary", None),
      ("esrv", "Set default", 170, "secondary", None), ("estd", "Clear default", 190, "secondary", None),
      ("eold", "Old tiles back", 200, "secondary", None), ("edone", "Done", 120, "primary", None),
      # fix round 2: an admin's in-game Undo of the SERVER DEFAULT's one-time update (PROJECT-RULES 4): the old default's tiles back
      # (shown on Home edit while the server default keeps an _old line and no tile is picked up)
      ("edold", "Old default", 170, "secondary", None),
      ("aprev", "< Prev", 130, "secondary", None), ("anext", "Next >", 130, "secondary", None), ("acancel", "Cancel", 140, "secondary", "cancel")]   # menu-pattern-ok
FB_GAP = 10
_fbmk = lambda pre, w_, lab, wid, kind, snd: 'TextButton #%sF%s { Anchor: (Width: %d, Height: %d); Padding: (Horizontal: 10); Text: "%s"; %s }' % (
    pre, w_, wid, FOOT_BTN_H, lab, SUI.theme_button_style(kind, "normal", theme="sky", sound=snd))
UI29_FBH = [_fbmk("SkyyMHm", w_, lab, wid, kind, snd) for w_, lab, wid, kind, snd in FB]
FB_TW = [130 if w_ == "hedit" else wid for w_, _l, wid, _k, _s in FB]
UI29_FBT = [_fbmk("SkyyMTp", w_, "Arrange" if w_ == "hedit" else lab, tw, kind, snd) for (w_, lab, _wid, kind, snd), tw in zip(FB, FB_TW)]   # 0.3.37: Arrange
for _w, _l, _wid, _k, _s in FB:
    assert SUI.text_width(_l, 17, bold=True, upper=True) <= _wid - 24, "0.3.30: foot button %s fits (%d px)" % (_l, SUI.text_width(_l, 17, bold=True, upper=True))
_mode_words = {"home": [["hedit", "close"], ["eremove", "ereset", "esrv", "estd", "eold", "edone"], ["ereset", "esrv", "estd", "eold", "edold", "edone"],
                        ["aprev", "anext", "acancel"]],
               "tp": [["hedit", "prev", "next", "close"], ["eremove", "ereset", "esrv", "estd", "prev", "next", "edone"], ["aprev", "anext", "acancel"]]}   # 0.3.38: Arrange + prev / next
_fbw = dict((w_, wid) for w_, _l, wid, _k, _s in FB)
for _ws in _mode_words["home"]:
    assert HOME_FOOT_W - sum(_fbw[w_] + FB_GAP for w_ in _ws) >= 400, "0.3.30: the Home info line keeps 400 px in every foot row"
# EVERY text the Home info line can show fits its TWO wrapped lines in the NARROWEST foot row - the hints, the edit texts, every status
# literal of the page code below (a name in it counted as the longest tile or hub name; the literals of both ternary branches added up,
# so this over-counts), the no-pages / fail / wait lines. 0.85 = the room a word wrap may waste. The Teleport info box shows the same
# texts on one line (16 px, cut at its end).
HINFO_ROOM = HOME_FOOT_W - max(sum(_fbw[w_] + FB_GAP for w_ in _ws) for _ws in _mode_words["home"]) - 16
TP_INFO_ROOM = TP_SH.inner_w - 32
_name24 = max([_n for _k, _n in zip(E_KEY, E_NAME) if _k] + [hub_title(_h) for _h in SUI.HUBS], key=len)   # the longest tile / hub name
_src29 = open(os.path.abspath(__file__), encoding="utf8").read()
_msgs29 = [HOME_TXT[k] for k in ("HT_HINT", "HT_HINT_OFF", "HT_EDIT", "HT_EDIT_START", "HT_ADD", "HT_TP_HINT")]
_msgs29 += [EDIT_TXT["KEPT_MSG"], EDIT_TXT["EDIT_WAIT"], HUB_TXT_FAIL] + ["[%s] %s" % (hub_title(_h), HUB_SOON[_h]) for _h in SUI.HUBS]
_stl29 = re.findall(r'this\.status = ([^;\n]*);', _src29)
assert len(_stl29) >= 30, "0.3.29: the status lines are found (%d)" % len(_stl29)
for _st in _stl29:
    _lits = re.findall(r'"((?:[^"\\]|\\.)*)"', _st)
    if _lits:
        _msgs29.append(_name24.join([_x for _x in _lits if _x]))
_tpcut = 0
for _m in _msgs29:
    assert SUI.text_width(_m, HINFO_FS) <= 2 * HINFO_ROOM * 0.85, "0.3.30: the Home info line fits 2 lines of %d px: %s (%d px)" % (
        HINFO_ROOM, _m, SUI.text_width(_m, HINFO_FS))
    if SUI.text_width(_m, 16) > TP_INFO_ROOM:
        _tpcut += 1
assert _tpcut <= 3, "0.3.30: at most a few over-counted texts reach the end of the Teleport info line (%d)" % _tpcut
# the Right now lines: an AL_MAX-character line in capitals + "  >" fits its button (the panel minus its padding and the button's) at 13 px
assert SUI.text_width(("Abcd Efgh " * 6)[:AL_MAX] + "  >", 13, bold=True) <= HOME_SIDE - 2 * YOU_PAD - 24, "0.3.30: an alert line fits its button"
assert all(SUI.text_width(HOME_TXT[_k] + "  >", 13, bold=True) <= HOME_SIDE - 2 * YOU_PAD - 24 and len(HOME_TXT[_k]) <= AL_MAX for _k in ("AL_MIG", "AL_SET")), \
    "0.3.30: SkyyMenu's own alerts fit"
print("0.3.30 info line: %d px (2 lines of %d px), %d texts checked; Teleport info line %d px (%d cut)" % (HINFO_ROOM, HINFO_FS, len(_msgs29), TP_INFO_ROOM, _tpcut))
_fbtw = dict(zip([f[0] for f in FB], FB_TW))
for _ws in _mode_words["tp"]:
    assert sum(_fbtw[w_] for w_ in _ws) + FB_GAP * (len(_ws) - 1) <= TP_FOOT_W, "0.3.30: the Teleport foot fits"


# ---- the big rows' Python twins (= MenuPage.bigRow / bigTabs, byte for byte - the harness compares the built pages with these)
def big_row_preview(parent, hubs, my, w):
    ap = SUI.Appends([(parent, UI29["BROW"])])
    n = len(hubs)
    bw = (w - BR_GAP * (n - 1)) // n
    icons = bw >= BR_ICON_MIN
    for i, (hid, title, icon) in enumerate(hubs):
        sel = hid == my
        if i > 0:
            ap.append(("SkyyMBRow", "Group { Anchor: (Width: %d); }" % BR_GAP))
        bid = "SkyyMBR%d" % i
        ap.append(("SkyyMBRow", "Button #%s { Anchor: (Width: %d, Height: %d); LayoutMode: Left; Padding: (Horizontal: %d, Vertical: %d); %s }" % (
            bid, bw, BR_H, BR_PAD, BR_PADV, SUI._row_style(sel, "sky"))))
        lw = bw - 2 * BR_PAD
        if icons:
            ap.append((bid, 'ItemIcon { Anchor: (Width: %d, Height: %d); ItemId: "%s"; }' % (BR_ICON, BR_ICON, icon)))
            ap.append((bid, "Group { Anchor: (Width: %d); }" % BR_ICON_GAP))
            lw = lw - BR_ICON - BR_ICON_GAP
        ap.append((bid, 'Label { Anchor: (Width: %d); Text: "%s"; Style: %s; }' % (lw, title, BR_LABSEL if sel else BR_LABN)))
    return ap


def big_tabs_preview(parent, hub, tabs, my, w):
    ap = SUI.Appends([(parent, UI29["BTABS"])])
    n = len(tabs)
    tw = (w - BT_GAP * (n - 1)) // n
    for i, (tid, lab) in enumerate(tabs):
        sel = tid == my
        if i > 0:
            ap.append(("SkyyMBTabs", "Group { Anchor: (Width: %d); }" % BT_GAP))
        bid = "SkyyMBT%d" % i
        ap.append(("SkyyMBTabs", "Button #%s { Anchor: (Width: %d, Height: %d); %s }" % (bid, tw, BT_H, SUI._tab_btn_style(sel, "sky"))))
        stem = "%s_%s" % (hub, tid)
        if stem in TAB_ART:
            ap.append((bid, 'Group { Anchor: (Left: %d, Top: %d, Width: %d, Height: %d); Background: "SkyyHubTabs/%s%s.png"; }' % (
                (tw - BT_ICON) // 2, BT_ICON_TOP, BT_ICON, BT_ICON, stem, "_on" if sel else "")))
        ap.append((bid, 'Label { Anchor: (Left: 0, Top: 0, Width: %d, Height: %d); Padding: (Horizontal: %d); Text: "%s"; Style: %s; }' % (
            tw, BT_H, BT_PAD, lab, BT_LAB)))
    return ap


_ROWHUBS = [(i, t if i == "home" else hub_title(i), "Skyy_Menu" if i == "home" else HUB_ICON_ITEM[i]) for i, t in zip(SUI.HUB_ROW_IDS, SUI.HUB_ROW_TITLES)]   # 0.3.31
for _rw in (HOME_ROW_W, TP_ROW_W):
    _bw = (_rw - BR_GAP * (len(_ROWHUBS) - 1)) // len(_ROWHUBS)
    assert _bw >= BR_ICON_MIN and all(SUI.text_width(_t, BR_LAB_MIN, bold=True) <= _bw - 2 * BR_PAD - BR_ICON - BR_ICON_GAP for _i, _t, _c in _ROWHUBS), \
        "0.3.30: every row-1 title fits its %d px button with the icon" % _bw
_wtabs = [(t, l) for t, o, _m, l, _c in SUI.hub_tabs("world")]
assert (TP_ROW_W - BT_GAP * (len(_wtabs) - 1)) // len(_wtabs) >= BT_MIN and TP_ROW_W // BT_MIN >= len(_wtabs)
for _t, _l in _wtabs:
    assert SUI.text_width(_l, BT_LAB_MIN, bold=True) <= BT_MIN - 2 * BT_PAD, "0.3.30: tab %s fits" % _l
# every look of both pages, checked as pages (markup rules, parents, no duplicate id, proven properties only, kit / tab-icon textures only)
_hp = SUI.hub_page_preview(HOME_SH, hubs=_ROWHUBS)          # 0.3.35: the kit 1.7 shell + row 1 (= HubBar.page17)
_hp.append(("SkyyMHome", UI29["HLEAD"]))
_hp.append(("SkyyMHome", UI29["HMAIN"]))
_hp.append(("SkyyMHmMain", UI29["HYOU"]))
for _k in ("HYT", "HYN"):
    _hp.append(("SkyyMHmYou", UI29[_k]))
for _mk in UI29_HYL:
    _hp.append(("SkyyMHmYou", _mk))
_hp.append(("SkyyMHmYou", UI29["HYBAR0"] + "136" + UI29["HYBAR1"]))
_hp.append(("SkyyMHmYou", UI29["HYH"]))
_hp.append(("SkyyMHmMain", UI29["HSP16"]))
_hp.append(("SkyyMHmMain", UI29["HMID"]))
for _k in ("HMIDT", "HGAP5", "HGW"):
    _hp.append(("SkyyMHmMid", UI29[_k]))
_hp.append(("SkyyMGW", UI29["HGRID"]))
_hp.append(("SkyyMHmMain", UI29["HSP16"]))
_hp.append(("SkyyMHmMain", UI29["HNOW"]))
_hp.append(("SkyyMHmNow", UI29["HNOWT"]))
for _mk in UI29_HA:
    _hp.append(("SkyyMHmNow", _mk))
_hp.append(("SkyyMHome", UI29["HGAP8"]))
_hp.append(("SkyyMHome", UI29["HFOOT"]))
_hp.append(("SkyyMHmFoot", UI29["HINFO0"] + "400" + UI29["HINFO1"]))
for _mk in UI29_FBH:
    _hp.append(("SkyyMHmFoot", UI29["FSP"]))
    _hp.append(("SkyyMHmFoot", _mk))
SUI.check_page(_hp, "SkyyM")
SUI.assert_proven(_hp, what="Home page")
_hels = SUI.check_sky_paths(_hp)
assert {"Frame", "Header", "HeaderOrnament", "Panel", "CardFrame", "PanelInset", "Row", "Close", "Primary", "Tertiary"} <= set(_hels), "0.3.30: Home uses the sky kit: %s" % _hels
assert SUI.used_height(SUI.Appends([(p_, mk) for p_, mk in _hp if p_ == "SkyyMHome"]), "SkyyMHome") <= HOME_SH.inner_h, "0.3.30: the Home body fits"
_hp2 = SUI.Appends(list(HOME_SH.appends) + [("SkyyMHome", UI29["HMAIN"]), ("SkyyMHmMain", UI29["HNOW"]), ("SkyyMHmNow", UI29["HNOWT"]),
                                            ("SkyyMHmNow", UI29["HNOWNONE"]), ("SkyyMHmMain", UI29["HMID"]), ("SkyyMHmMid", UI29["HGW"]),
                                            ("SkyyMGW", UI29["HGRIDNT"])])
SUI.check_page(_hp2, "SkyyM")
SUI.assert_proven(_hp2, what="Home page (nothing waiting, tooltips off)")
_tp = SUI.hub_page_preview(TP_SH, hubs=_ROWHUBS, tabs=_wtabs, my_tab="teleport", art=TAB_ART)   # 0.3.35: kit 1.7 rows 1 + 2
_tp.append(("SkyyMTpB", UI29["TLEADY"]))
_tp.append(("SkyyMTpB", UI29["TROW"]))
_tp.append(("SkyyMTpRow", UI29["TLEAD"]))
_tp.append(("SkyyMTpRow", UI29["HGW"]))
_tp.append(("SkyyMGW", UI29["HGRID"]))
_tp.append(("SkyyMTpB", UI29["TGAP"]))
_tp.append(("SkyyMTpB", UI29["TINFO"]))
_tp.append(("SkyyMTpInfo", UI29["TIN"]))
_tp.append(("SkyyMTpInfo", UI29["TID"]))
_tp.append(("SkyyMTpB", UI29["TGAP"]))
_tp.append(("SkyyMTpB", UI29["TFOOT"]))
for _mk in UI29_FBT:
    _tp.append(("SkyyMTpFoot", _mk))
SUI.check_page(_tp, "SkyyM")
SUI.assert_proven(_tp, what="Teleport page")
SUI.assert_menu_page(_hp, HOME_SH, pager_ok=True)     # 0.3.35: the menu pattern (the grid's slot pages keep their arrows)
SUI.assert_menu_page(_tp, TP_SH, pager_ok=True)
assert {"Frame_World", "Header", "HeaderOrnament", "PanelInset", "Tab_Selected", "Tab", "Close"} <= set(SUI.check_sky_paths(_tp, tab_icons=True))
assert SUI.used_height(SUI.Appends([(p_, mk) for p_, mk in _tp if p_ == "SkyyMTpB"]), "SkyyMTpB") <= TP_SH.inner_h, "0.3.30: Teleport fits"
for _mk in list(UI29.values()) + UI29_HYL + UI29_HA + UI29_FBH + UI29_FBT:
    assert not re.search(r"(Vertical|Horizontal)Alignment\s*:\s*(Top|Bottom|Left|Right)\b", _mk), "0.3.29: Start / Center / End alignments only"
    for _eid in re.findall(r"#([A-Za-z0-9_]+)\s*\{", _mk):
        assert "_" not in _eid
# every kit 1.6 hub page of SkyyMenu (Home / Teleport draw their own big rows): the bar-less height + the 52 px strip fits 1080p and the
# hub's FULL contract tab list fits (row 1 is in the title bar)
HUB_PAGES = [("stats", ST_SH, "character", "stats"), ("players", MENU_HUB_SH["social"], "social", "players"), ("mods", MENU_HUB_SH["settings"], "settings", "mods"),
             ("settings", STG_HUB_SH, "settings", "settings"), ("setup", ADM_HUB_SH, "settings", "setup")]
HUB_LABEL_FIT = {}
for _t, _sh, _h, _my in HUB_PAGES:      # 0.3.35: kit 1.7 hub pages - shell + rows 1 + 2 (Python twins of HubBar.page17), the menu pattern
    assert (_sh.w, _sh.h) == (1600, 980) and _sh.page, "0.3.35: %s is a 1600 x 980 hub page" % _t
    _pp = os.path.commonprefix([_sh.prefix, _sh.content])
    _sel = "skills" if _t == "stats" else _my       # Stats is part of the Skills tab (the strip shows Skills selected)
    _pv = SUI.hub_page_preview(_sh, hubs=_ROWHUBS, tabs=[(r[0], SUI.hub_tab_label(_h, r[0])) for r in SUI.hub_page_tabs(_h)], my_tab=_sel, art=TAB_ART)
    SUI.check_page(_pv, _pp)
    SUI.assert_proven(_pv, what="hub page " + _t)
    _els = SUI.check_sky_paths(_pv, tab_icons=True)
    assert {"Header", "HeaderOrnament", SUI.HUB_FRAME[_h], "Close", "Tab", "Tab_Selected"} <= set(_els), "0.3.35: %s: %s" % (_t, _els)
    SUI.assert_menu_page(_pv, _sh)
    HUB_LABEL_FIT[_t] = SUI.assert_big_tabs_fit(_h)
MH_JAVA = dict((h, MENU_HUB_SH[h].java("b")) for h in MENU_HUB_SH)
HOME_JAVA = HOME_SH.java("b")
TP_JAVA = TP_SH.java("b")
STG_HUB_JAVA = STG_HUB_SH.java("b")
ADM_HUB_JAVA = ADM_HUB_SH.java("b")
# 0.3.33: the strip shows the HOST selected (Skills) while Stats is a merged tab (HubBar.selOf; Stats itself when SkyySkills is not loaded)
ST_HUB_JAVA = SUI.java_hub_page(ST_SH, cls="@PKG@.HubBar", tab_expr='@PKG@.HubBar.selOf("character", "stats")')   # 0.3.35: kit 1.7
STG_HUB_BUILD = SUI.java_hub_page(STG_HUB_SH, "settings", cls="@PKG@.HubBar", uuid="u")
ADM_HUB_BUILD = SUI.java_hub_page(ADM_HUB_SH, "setup", cls="@PKG@.HubBar", uuid="me()")
MH_BUILD = '@PKG@.HubBar.page17(b, ev, "SkyyMenuH", hubName(), hubTab(), %d, this.playerRef.getUuid(), %d);' % (SUI.HUB_PAGE_IW, SUI.HUB_PART_CLOSE)
# Home / Teleport: rows 1 + 2 from the kit (their X keeps its own binding: parts 0)
HOME_PAGE17 = SUI.java_hub_page(HOME_SH, cls="@PKG@.HubBar", uuid="me").replace(", 2);", ", 0);")
TP_PAGE17 = SUI.java_hub_page(TP_SH, "teleport", cls="@PKG@.HubBar", uuid="me").replace(", 2);", ", 0);")
assert HOME_PAGE17.endswith('"home", null, 1552, me, 0);') and TP_PAGE17.endswith('"world", "teleport", 1552, me, 0);')
assert ST_HUB_JAVA == '@PKG@.HubBar.page17(b, ev, "SkyyStatF", "character", @PKG@.HubBar.selOf("character", "stats"), 1552, this.playerRef.getUuid(), 2);'
assert "HubRow" not in HOME_JAVA + TP_JAVA and "HubTabs" not in HOME_JAVA + TP_JAVA and "SkyyMHmHubClose" in HOME_JAVA and "SkyyMTpHubClose" in TP_JAVA
print("0.3.30 pages: Home %d x %d (grid %d x %d of %d px slots, sides %d px, centre slot at page centre %+d / %+d = 0.3.28 slot 13), Teleport %d x %d, row 1 %d px buttons, %s" % (
    HOME_W, HOME_H, HG_W, HG_H, SLOT30, HOME_SIDE, HOME_C[0], HOME_C[1], TP_W, TP_H, (HOME_ROW_W - BR_GAP * 7) // 8,
    ", ".join("%s %d px tabs" % (t, HUB_LABEL_FIT[t]) for t, _s, _h, _m in HUB_PAGES)))
# Server Setup: the one-line title (AdminPage.frame: the "Server Setup - " prefix dropped, "<title>   -   <subtitle>", MenuUtil.clip at
# ADM_SUBMAX). The real worst cases (a 24-character config TITLE - skyycfg's limit -, the longest mod id of the SET, a long version, the
# longest subtitles: View only / not running / saved / no page) show WHOLE and fit the 1080 px line; the longer fixed lines (History,
# Export) fit once cut. A_INNER at 16 px bold, the kit's own glyph widths.
def adm_line(t, s):
    if t.startswith(ADM_PREFIX):
        t = t[len(ADM_PREFIX):]
    j = t if not s else t + "   -   " + s
    return j if len(j) <= ADM_SUBMAX else j[:ADM_SUBMAX - 3] + "..."
_am = max([_m["mod"] for _m in MODS] + ["SkyyAbilityProbe"], key=len)     # the longest mod id the Mods list knows (16+ characters)
_at, _av = "Accessories and Talisman", "0.10.12"
assert len(_at) == 24
_whole = [("Server Setup - %s (%s %s)" % (_at, _am, _av), "View only - changing %s needs %s.admin." % (_am, _am.lower())),
          ("Server Setup - %s (%s %s)" % (_at, _am, _av), "%s is not running - its settings cannot be changed now." % _am),
          ("Server Setup - %s (%s %s)" % (_at, _am, _av), "Saved to config.properties - changes are written at once."),
          ("Server Setup - %s %s" % (_am, _av), "This version has no Server Setup page yet - edit its file, then reload it."),
          ("Server Setup - Changes", "Every change made in game, by command or by hand, newest first. Undo puts one value back."),
          ("Export / Import - %s (%s)" % (_at, _am), "A code copies this setup to another world. It never holds player data.")]
_cutok = [("History - config.properties (%s)" % _am,
           "Each config file keeps its newest versions. Preview one, then Restore it - a restore can be undone the same way.")]
for _t, _s in _whole + _cutok:
    _ln = adm_line(_t, _s)
    assert not _ln.startswith(ADM_PREFIX), "0.3.28: the Server Setup prefix stays off the line: " + _ln
    assert SUI.text_width(_ln, 16, bold=True) <= A_INNER - 40, "0.3.28: the Server Setup title line is too wide: %s (%d px)" % (_ln, SUI.text_width(_ln, 16, bold=True))
    assert (_t, _s) in _cutok or not _ln.endswith("..."), "0.3.28: a real Server Setup title line was cut: " + _ln
ADM_LINE_MAX = max(SUI.text_width(adm_line(_t, _s), 16, bold=True) for _t, _s in _whole + _cutok)
print("hub pages (kit %s, sky): %s; menu views %d x %d, settings %d x %d, server setup %d x %d (title line <= %d of %d px), stats %d x %d" % (
    SUI.kit_id(), ", ".join("%s %s:%s %d px tabs" % (t, h, m, HUB_LABEL_FIT[t]) for t, _s, h, m in HUB_PAGES), MH_W, MH_H, SPW, SPH, APW, APH,
    ADM_LINE_MAX, A_INNER, ST_W, ST_H))

# ================= 0.3.23 THE ADMIN PAGE (research/Admin-Page-Plan.md; tools/menu_0_3_23_patch.py): data + markup =================
# OPS = one row per button: (tab, button label, command line, permission node of the command, mod, confirm, Text box hint, bridge status
# key). {p} = the picked online player, {t} = the Text box. The line is DISPATCHED as the admin (CommandManager.handleCommand); the
# button shows only while the engine's hasPermission of that exact command (sub-commands walked, the usage variant by argument count)
# passes. Every row was read from the real command classes of the SET jars (harness phase O re-checks names, sub-commands, variants,
# nodes and runs every line through the engine's parser). mod "Hytale" = an engine command (its node is generated by the engine).
# Adding a button = one line here.
OPS_TABS = ["Server", "Economy", "Players", "Diagnostics"]
OPS_DIAG = 3
OPS = [
    # ---- Server
    (0, "Server Setup", "modconfig", "skyymenu.modconfig", "SkyyMenu", False, "", ""),
    (0, "Set hub here", "sethub", "skyyislands.admin", "SkyyIslands", True, "", ""),
    (0, "Warps editor", "warpadmin", "skyyessentials.admin", "SkyyEssentials", False, "", ""),
    (0, "Reload islands", "island reload", "skyyislands.admin", "SkyyIslands", False, "", ""),
    (0, "Zone info", "zone info", "skyyworldgen.admin", "SkyyWorldGen", False, "", ""),
    (0, "Reload zones", "zone reload", "skyyworldgen.admin", "SkyyWorldGen", False, "", ""),
    (0, "Go to zone", "zone {t}", "skyyworldgen.admin", "SkyyWorldGen", False, "zone id", ""),
    (0, "Leave zone", "zone leave", "skyyworldgen.admin", "SkyyWorldGen", False, "", ""),
    (0, "Zone landing here", "zone setlanding", "skyyworldgen.admin", "SkyyWorldGen", True, "", ""),
    (0, "Trade log", "tradeadmin log", "skyyessentials.tradeadmin", "SkyyEssentials", False, "", ""),
    (0, "Player trade log", "tradeadmin log {p}", "skyyessentials.tradeadmin", "SkyyEssentials", False, "", ""),
    (0, "Trade settings", "tradeadmin config", "skyyessentials.tradeadmin", "SkyyEssentials", False, "", ""),
    (0, "Reload trades", "tradeadmin reload", "skyyessentials.tradeadmin", "SkyyEssentials", False, "", ""),
    (0, "Return trade items", "tradeadmin return {p}", "skyyessentials.tradeadmin", "SkyyEssentials", True, "", ""),
    (0, "Player rank", "rankadmin player {p}", "skyyranks.admin", "SkyyRanks", False, "", ""),
    (0, "Sync ranks", "rankadmin sync", "skyyranks.admin", "SkyyRanks", False, "", ""),
    (0, "Reload ranks", "rankadmin reload", "skyyranks.admin", "SkyyRanks", False, "", ""),
    (0, "Death penalty", "deathpenalty", "skyycoins.admin", "SkyyCoins", False, "", ""),
    (0, "Bank interest", "bankconfig", "skyybank.admin", "SkyyBank", False, "", ""),
    (0, "Reload skills", "skills reload", "skyyskills.admin", "SkyySkills", False, "", ""),
    (0, "Reload trees", "tree reload", "skyytrees.admin", "SkyyTrees", False, "", ""),
    (0, "Reload collections", "collections reload", "skyycollections.admin", "SkyyCollections", False, "", ""),
    (0, "Reload charms", "charms reload", "skyyaccessories.admin", "SkyyAccessories", False, "", ""),   # 0.3.36: /charms
    (0, "Reload mobs", "mobs reload", "skyymobs.admin", "SkyyMobs", False, "", ""),
    # ---- Economy
    (1, "AH status", "ahadmin", "skyyauctions.admin", "SkyyAuctions", False, "", ""),
    (1, "AH listings", "ahadmin list", "skyyauctions.admin", "SkyyAuctions", False, "", "auction:count"),
    (1, "Player listings", "ahadmin list {p}", "skyyauctions.admin", "SkyyAuctions", False, "", ""),
    (1, "Pause AH", "ahadmin pause", "skyyauctions.admin", "SkyyAuctions", False, "", ""),
    (1, "Resume AH", "ahadmin resume", "skyyauctions.admin", "SkyyAuctions", False, "", ""),
    (1, "Reload AH", "ahadmin reload", "skyyauctions.admin", "SkyyAuctions", False, "", ""),
    (1, "Listing info", "ahadmin info {t}", "skyyauctions.admin", "SkyyAuctions", False, "listing id", ""),
    (1, "Remove listing", "ahadmin remove {t}", "skyyauctions.admin", "SkyyAuctions", True, "listing id", ""),
    (1, "My AH close preview", "ahadmin closeall", "skyyauctions.admin", "SkyyAuctions", False, "", ""),
    (1, "Close my AH listings", "ahadmin closeall confirm", "skyyauctions.admin", "SkyyAuctions", True, "", ""),
    (1, "Bazaar item info", "bazaaradmin info {t}", "skyybazaar.admin", "SkyyBazaar", False, "item id", "bazaar:products"),
    (1, "Reset item price", "bazaaradmin reset {t}", "skyybazaar.admin", "SkyyBazaar", True, "item id", ""),
    (1, "Reload bazaar", "bazaaradmin reload", "skyybazaar.admin", "SkyyBazaar", False, "", ""),
    (1, "Vault info", "vaultadmin info {p}", "skyyvault.admin", "SkyyVault", False, "", ""),
    (1, "Open vault", "vaultadmin open {p}", "skyyvault.admin", "SkyyVault", False, "", ""),
    (1, "Vault settings", "vaultadmin config", "skyyvault.admin", "SkyyVault", False, "", ""),
    (1, "Reload vault", "vaultadmin reload", "skyyvault.admin", "SkyyVault", False, "", ""),
    (1, "List merchants", "merchantadmin list", "skyymerchants.admin", "SkyyMerchants", False, "", ""),
    (1, "Move merchant", "merchantadmin move {t}", "skyymerchants.admin", "SkyyMerchants", False, "zone id", ""),
    (1, "Spawn merchant", "merchantadmin spawn {t}", "skyymerchants.admin", "SkyyMerchants", False, "zone id", ""),
    (1, "Remove merchant", "merchantadmin remove {t}", "skyymerchants.admin", "SkyyMerchants", True, "zone id", ""),
    (1, "Void bags resume", "pdadmin resume {p}", "skyysacks.admin", "SkyySacks", True, "", ""),
    # ---- Players
    (2, "Class info", "classadmin info {p}", "skyyclasses.admin", "SkyyClasses", False, "", ""),
    (2, "Class kit", "classadmin kit {p}", "skyyclasses.admin", "SkyyClasses", False, "", ""),
    (2, "Reset class", "classadmin reset {p}", "skyyclasses.admin", "SkyyClasses", True, "", ""),
    (2, "Reload classes", "classadmin reload", "skyyclasses.admin", "SkyyClasses", False, "", ""),
    (2, "Profile info", "profileadmin info {p}", "skyyprofiles.admin", "SkyyProfiles", False, "", ""),
    (2, "Archived profiles", "profileadmin archive list {p}", "skyyprofiles.admin", "SkyyProfiles", False, "", ""),
    (2, "Profile settings", "profileadmin config", "skyyprofiles.admin", "SkyyProfiles", False, "", ""),
    (2, "Reload profiles", "profileadmin reload", "skyyprofiles.admin", "SkyyProfiles", False, "", ""),
    (2, "Quest check", "questadmin check", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Player quests", "questadmin list {p}", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Repay quests", "questadmin repay {p}", "skyyquests.admin", "SkyyQuests", True, "", ""),
    (2, "Reload quests", "questadmin reload", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Quest NPCs", "questadmin npc list", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Quest Board here", "questadmin npc add board", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Marlow here", "questadmin npc add marlow", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Quest places", "questadmin place list", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Mining spot here", "questadmin place set hub.mining", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Foraging spot here", "questadmin place set hub.foraging", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Farming spot here", "questadmin place set hub.farming", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Fishing spot here", "questadmin place set hub.fishing", "skyyquests.admin", "SkyyQuests", False, "", ""),
    (2, "Explore stats", "exploreadmin stats", "skyyexploration.admin", "SkyyExploration", False, "", ""),
    (2, "Airdrop here", "exploreadmin airdrop", "skyyexploration.admin", "SkyyExploration", False, "", ""),
    (2, "Explore checklist", "exploreadmin check list", "skyyexploration.admin", "SkyyExploration", False, "", ""),
    (2, "Explore spots", "exploreadmin spot list", "skyyexploration.admin", "SkyyExploration", False, "", ""),
    (2, "Reload exploration", "exploreadmin reload", "skyyexploration.admin", "SkyyExploration", False, "", ""),
    (2, "Player pets", "petadmin list {p}", "skyypets.admin", "SkyyPets", False, "", ""),
    (2, "Pet kinds", "petadmin kinds", "skyypets.admin", "SkyyPets", False, "", ""),
    (2, "Pet sweep status", "petadmin sweep", "skyypets.admin", "SkyyPets", False, "", ""),
    (2, "Requip info", "requipadmin info {p}", "skyywardrobe.admin", "SkyyWardrobe", False, "", ""),
    (2, "Repair requip", "requipadmin repair {p}", "skyywardrobe.admin", "SkyyWardrobe", True, "", ""),
    (2, "Reload requip", "requipadmin reload", "skyywardrobe.admin", "SkyyWardrobe", False, "", ""),
    (2, "Fishing status", "fishadmin status", "skyyfishing.admin", "SkyyFishing", False, "", ""),
    (2, "Reload cooking", "cookadmin reload", "skyycooking.admin", "SkyyCooking", False, "", ""),
    (2, "Reload party", "partyadmin reload", "skyyparty.admin", "SkyyParty", False, "", ""),
    (2, "Guild info", "guildadmin info {t}", "skyyguilds.admin", "SkyyGuilds", False, "guild tag or id", ""),
    (2, "Guild settings", "guildadmin config", "skyyguilds.admin", "SkyyGuilds", False, "", ""),
    (2, "Reload guilds", "guildadmin reload", "skyyguilds.admin", "SkyyGuilds", False, "", ""),
    (2, "Rebirth status", "rebirthadmin status", "skyyrebirth.admin", "SkyyRebirth", False, "", ""),
    (2, "Rebirth dry run", "rebirthadmin dryrun", "skyyrebirth.admin", "SkyyRebirth", False, "", ""),
    (2, "Rebirth backups", "rebirthadmin backups", "skyyrebirth.admin", "SkyyRebirth", False, "", ""),
    (2, "Recover rebirths", "rebirthadmin recover", "skyyrebirth.admin", "SkyyRebirth", True, "", ""),
    # 0.3.24: SkyyRebirth 0.3.1's sub-commands (they parse now); crash test = a danger row (page confirm) on top of the command's own
    # type-it-twice confirm - it resets the admin's real active profile, so one stray page press must never start it
    (2, "Rebirth crash test", "rebirthadmin crashtest {t}", "skyyrebirth.admin", "SkyyRebirth", True, "point 0-7", ""),
    (2, "Rebirth test points", "rebirthadmin points {t} 100", "skyyrebirth.admin", "SkyyRebirth", False, "arm or all", ""),
    (2, "Wipe rebirth arm", "rebirthadmin points {t} reset", "skyyrebirth.admin", "SkyyRebirth", True, "arm or all", ""),
    (2, "Refund rebirth arm", "rebirthadmin refund {t}", "skyyrebirth.admin", "SkyyRebirth", True, "arm or all", ""),
    # 0.3.25: SkyyShards 0.3's sub-commands (give / info / unplace / unload <player>; no shard word = the Farming Shard). give hands out
    # a new shard item and unplace clears the portal record: danger rows (press twice)
    (2, "Give Farming Shard", "shardadmin give {p}", "skyyshards.admin", "SkyyShards", True, "", ""),
    (2, "Shard info", "shardadmin info {p}", "skyyshards.admin", "SkyyShards", False, "", ""),
    (2, "Clear shard portal", "shardadmin unplace {p}", "skyyshards.admin", "SkyyShards", True, "", ""),
    (2, "Unload shard world", "shardadmin unload {p}", "skyyshards.admin", "SkyyShards", False, "", ""),
    # ---- Diagnostics (engine commands; their nodes are the engine's own generated ones)
    (3, "CPU stats", "server stats cpu", "", "Hytale", False, "", ""),
    (3, "Memory stats", "server stats memory", "", "Hytale", False, "", ""),
    (3, "Server version", "version", "", "Hytale", False, "", ""),
    (3, "Who is online", "who", "", "Hytale", False, "", ""),
    (3, "Plugin list", "plugin list", "", "Hytale", False, "", ""),
    # 0.3.24: /soundtest (this jar; the Server Setup node)
    (3, "Sound list", "soundtest list", "skyymenu.modconfig", "SkyyMenu", False, "", ""),
    (3, "Next sound", "soundtest next", "skyymenu.modconfig", "SkyyMenu", False, "", ""),
    (3, "Play sound", "soundtest {t}", "skyymenu.modconfig", "SkyyMenu", False, "sound id or number", ""),
]
OPS_STATUS_KEYS = ("auction:count", "bazaar:products")
# how many literal words after the command name are SUB-COMMANDS (default: all of them); the rest of the line is arguments. The harness
# walks the real SET command trees and checks every row's depth. A missing sub-command (an older mod) hides the button.
OPS_DEPTH_EXCEPT = {
    "ahadmin closeall confirm": 1,
    "questadmin npc list": 1, "questadmin npc add board": 1, "questadmin npc add marlow": 1, "questadmin place list": 1,
    "questadmin place set hub.mining": 1, "questadmin place set hub.foraging": 1, "questadmin place set hub.farming": 1,
    "questadmin place set hub.fishing": 1,
    # 0.3.24: SkyyRebirth 0.3.1 sub-commands under an argument root (checked before OPS_ARG_ROOTS)
    "rebirthadmin crashtest {t}": 1, "rebirthadmin points {t} 100": 1, "rebirthadmin points {t} reset": 1, "rebirthadmin refund {t}": 1,
}


# commands that take their action as an ARGUMENT (/merchantadmin <action> [zone], not sub-commands): every literal word is an argument
OPS_ARG_ROOTS = ("merchantadmin", "pdadmin", "petadmin", "requipadmin", "fishadmin", "rebirthadmin", "soundtest")   # 0.3.24: + soundtest
# commands that read their own input line (setAllowsExtraArguments(true), fewer required arguments than the line has words; the harness
# checks this against the real field): the engine takes the line as long as it has at least the required words
OPS_EXTRA_ROOTS = ("pdadmin",)


def ops_depth(line):
    lit = [w for w in line.split(" ")[1:] if not w.startswith("{")]
    d = OPS_DEPTH_EXCEPT[line] if line in OPS_DEPTH_EXCEPT else (0 if line.split(" ")[0] in OPS_ARG_ROOTS else len(lit))   # 0.3.24: the exception first
    assert 0 <= d <= len(lit), line
    return d
OPS_SUB = "Each button runs the real admin command as you - the answer shows in your chat."
OPS_NOACCESS = "-You need the permission skyymenu.modconfig for the Admin page."
OPS_TEXT_HINT = "item zone listing or guild id"
OPS_TEXT_MAX = 64
OPS_CONFIRM_MS = 10000                 # the danger button's second click must come within 10 s (task text)
OPS_DOUBLE_MS = 400                    # a second click this fast is one double-click (or a duplicated event), not a confirm
OPS_W, OPS_H = SUI.HUB_PAGE_W, SUI.HUB_PAGE_H    # 0.3.36: the kit 1.7 hub page under Settings (0.3.23 - 0.3.35: a 1160 x 960 window)
OPS_SUBTABS = ["All mods"] + OPS_TABS          # 0.3.36: the ONE sub-tab row: Server Setup's mod list, then the Admin page's 4 tabs
OPS_BTN_PAD = 10
OPS_BTN_W = 252
OPS_ROW_GAP = 6
OPS_CELL_GAP = 12
OPS_HELP_FS = 15
OPS_LINE_H, OPS_LINE_GAP = 30, 4       # Diagnostics info lines
OPS_LINE_MAX = 104                     # an info line is cut into pieces of at most this many characters (at ", ")

# the table: labels / lines / nodes / mods; each command root + node against the SET script of its mod (the harness checks the real classes)
_ops_labels = [o[1] for o in OPS]
assert len(set(_ops_labels)) == len(_ops_labels), "OPS labels must be unique"
_set_live = dict(ROUND_SET)          # 0.3.36: this round's set (the /charms row needs SkyyAccessories 0.5.22)
for _o in OPS:
    _tab, _lab, _line, _node, _mod, _conf, _hint, _st = _o
    assert 0 <= _tab < len(OPS_TABS) and isinstance(_conf, bool), _o
    assert SUI.TEXT_OK.fullmatch(_lab), "OPS label with unproven characters: " + _lab
    assert re.match(r"^[a-z]+( [a-z0-9.]+| \{p\}| \{t\})*$", _line), "OPS line: " + _line
    assert _line.count("{p}") <= 1 and _line.count("{t}") <= 1 and not ("{p}" in _line and "{t}" in _line), _line
    assert ("{t}" in _line) == bool(_hint), "OPS: a {t} row needs its Text box hint (and only then): " + _line
    assert _st in ("",) + OPS_STATUS_KEYS, _o
    if _mod == "Hytale":
        assert _node == "" and _tab == OPS_DIAG, _o
        continue
    assert _NODE_RE.match(_node), "OPS node: " + _node
    assert _mod in _set_live, "OPS: %s is not in the SET" % _mod
    _sp = os.path.abspath(__file__) if _mod == "SkyyMenu" else _script(_mod, _set_live[_mod])   # 0.3.24: the menu's own rows = this script
    assert os.path.isfile(_sp), "OPS: no SET script for %s: %s" % (_mod, _sp)
    _stx = open(_sp, encoding="utf-8").read()
    _root = _line.split(" ")[0]
    assert ('super("%s"' % _root) in _stx or ('"%s", "' % _root) in _stx, "OPS: %s %s has no command /%s" % (_mod, _set_live[_mod], _root)
    assert ('"%s"' % _node) in _stx, "OPS: %s %s never names the node %s" % (_mod, _set_live[_mod], _node)
    for _w in _line.split(" ")[1:]:
        if not _w.startswith("{"):
            assert ('"%s"' % _w) in _stx or (" %s " % _w) in _stx or ("| %s" % _w) in _stx, "OPS: %s never mentions %r (%s)" % (_mod, _w, _line)


def ops_help(o):
    """the help text next to a button: the command it runs ({p} = <player>, {t} = <hint>)"""
    return "/" + o[2].replace("{p}", "<player>").replace("{t}", "<" + o[6] + ">")


def ops_btn(ident, h, kind):
    """0.3.36: one Admin page button (the sky button art), its label set with b.set (OpsPage.build)"""
    return 'TextButton #%s { Anchor: (Width: %d, Height: %s); Padding: (Horizontal: %d); Text: ""; %s }' % (
        ident, OPS_BTN_W, h, OPS_BTN_PAD, SUI.theme_button_style(kind, "normal", theme="sky"))


def ops_page():
    """0.3.36 (research/Menu-Pattern.md rule 8 + M16): the Admin page on the kit 1.7 hub_page under Settings - row 1, row 2 (Server Setup
    selected: the page is its sub view), the ONE sub-tab row (All mods = Server Setup's mod list, then Server / Economy / Players /
    Diagnostics), the content (the caption, the Player / Text picker row, ONE scroll list of the buttons, two a row, each with the command
    it runs; Diagnostics' info lines under them) and the footer (the result line, Close). No back button, no pages. Returns the pieces."""
    J = SUI.J
    sh = SUI.hub_page("SkyyOpsF", "settings", body_id="SkyyOpsFB", content_id="SkyyOps", sub=True, footer=True)
    IW, BH, LP = sh.content_w, SUI.BTN_H, SUI.WELL_LIST_PAD
    P = {}
    P["sub"] = ("SkyyOps", SUI.label("SkyyOpsSub", "", "caption", h=24, size=OPS_HELP_FS))
    P["pick"] = ("SkyyOps", SUI.group("SkyyOpsPick", "Left", h=BH, anchor={"top": 6, "bottom": 8}))
    list_h = sh.content_h - 24 - (6 + BH + 8)
    P["list"] = ("SkyyOps", SUI.scroll_list("SkyyOpsList", h=list_h, well=True))
    left = sh.content_h - sum(SUI.outer_size(P[k][1])[1] for k in ("sub", "pick", "list"))
    assert left == 0 and list_h >= 500, "admin page parts do not fill the content (%d left, list %d)" % (left, list_h)
    # the sub-tab row: All mods + the 4 tabs (kit small buttons, 150 px), the active tab Primary
    SUI.assert_sub_tabs_fit(OPS_SUBTABS)
    subn = [SUI.sub_tab_markup("SkyyOpsF", k, t, False) for k, t in enumerate(OPS_SUBTABS)]
    subs = [SUI.sub_tab_markup("SkyyOpsF", k, t, True) for k, t in enumerate(OPS_SUBTABS)]
    subgap = "Group { Anchor: (Width: %d); }" % SUI.SUB_TAB_GAP
    # the picker row: Player < name > | Text [box] Clear - filled exactly
    g = 6
    pw = {"plab": 80, "pprev": 72, "pname": 268, "pnext": 72, "gap": 24, "tlab": 56, "clr": 120}
    field_w = IW - (pw["plab"] + pw["pprev"] + g + pw["pname"] + g + pw["pnext"] + pw["gap"] + pw["tlab"] + pw["clr"] + g)
    assert field_w >= 600, "the Text box is too narrow: %d" % field_w
    sb = lambda i, t, w, anc=None: 'TextButton #%s { Anchor: (Width: %d, Height: %d%s); Padding: (Horizontal: %d); Text: "%s"; %s }' % (
        i, w, BH, "".join(", %s: %d" % (k.capitalize(), v) for k, v in sorted((anc or {}).items())), OPS_BTN_PAD, t,
        SUI.theme_button_style("secondary", "normal", theme="sky"))
    pick = [("SkyyOpsPick", SUI.label(None, "Player", "bold", w=pw["plab"], h=BH)),
            ("SkyyOpsPick", sb("SkyyOpsPPrev", "<", pw["pprev"], {"right": g})),
            ("SkyyOpsPick", SUI.label("SkyyOpsPName", "", "bold", w=pw["pname"], h=BH, align="Center")),
            ("SkyyOpsPick", sb("SkyyOpsPNext", ">", pw["pnext"], {"left": g})),
            ("SkyyOpsPick", SUI.spacer(w=pw["gap"], h=BH)),
            ("SkyyOpsPick", SUI.label(None, "Text", "bold", w=pw["tlab"], h=BH)),
            ("SkyyOpsPick", SUI.text_field("SkyyOpsArgBox", "SkyyOpsArg", w=field_w, h=BH, placeholder=OPS_TEXT_HINT, max_length=OPS_TEXT_MAX)),
            ("SkyyOpsPick", sb("SkyyOpsClr", "Clear", pw["clr"], {"left": g}))]
    assert sum(SUI.outer_size(mk)[0] for _p, mk in pick) == IW, "the picker row is not filled exactly"
    # the button list: rows of two cells (button | gap | help text); the row height bh = a grow tier (rule 7), the buttons as high as it
    row_w = IW - 2 * LP - 24
    cell_w = (row_w - OPS_CELL_GAP) // 2
    help_w = cell_w - OPS_BTN_W - 10
    rid, cid, bh = J("r", "0"), J("c", "0"), J("bh", str(BH))
    grid = {
        "row": ("SkyyOpsList", SUI.group("SkyyOpsR" + rid, "Left", h=bh, anchor={"bottom": OPS_ROW_GAP})),
        "cell": ("SkyyOpsR" + rid, SUI.choose(J("c % 2 == 0"), SUI.group("SkyyOpsC" + cid, "Left", w=cell_w, h=bh, anchor={"right": OPS_CELL_GAP}),
                                              SUI.group("SkyyOpsC" + cid, "Left", w=cell_w, h=bh))),
        "btn": ("SkyyOpsC" + cid, SUI.choose(J("dng"), ops_btn("SkyyOpsA" + J("i", "0"), bh, "destructive"), ops_btn("SkyyOpsA" + J("i", "0"), bh, "secondary"))),
        "gap": ("SkyyOpsC" + cid, SUI.spacer(w=10, h=bh)),
        "help": ("SkyyOpsC" + cid, SUI.label("SkyyOpsH" + cid, "", "caption", w=help_w, h=bh, size=OPS_HELP_FS)),
        "line": ("SkyyOpsList", SUI.label("SkyyOpsI" + J("k", "0"), "", "default", w=row_w, h=OPS_LINE_H, size=OPS_HELP_FS + 1,
                                          anchor={"bottom": OPS_LINE_GAP})),
    }
    # the footer: the result line (its colour by the result mark), Close - filled exactly
    fg = SUI.FOOT_GAP
    msg_w = IW - fg - SUI.BTN_MIN_W
    foot = [("SkyyOpsFFoot", SUI.label("SkyyOpsMsg", "", "default", w=msg_w, h=SUI.FOOT_BTN_H, size=16, bold=True,
                                       col=J("colorOf(this.info)", SUI.COLOR["success"]), wrap=True, padding={"horizontal": 8})),
            ("SkyyOpsFFoot", SUI.spacer(w=fg)),
            ("SkyyOpsFFoot", SUI.foot_button("SkyyOpsClose", "Close", sound="cancel"))]
    assert sum(SUI.outer_size(mk)[0] for _p, mk in foot) == IW, "the admin footer is not filled exactly"
    # every look this page can show, checked as one page (ids, parents, markup rules, proven properties only, the menu pattern)
    chk = SUI.hub_page_preview(sh, tabs=[(r[0], SUI.hub_tab_label("settings", r[0])) for r in SUI.hub_page_tabs("settings")], my_tab="setup")
    for k in range(len(OPS_SUBTABS)):
        if k > 0:
            chk.append(("SkyyOpsFSub", subgap))
        chk.append(("SkyyOpsFSub", subs[k] if k == 1 else subn[k]))
    for k in ("sub", "pick", "list"):
        chk.append(P[k])
    chk.extend(pick)
    for k in ("row", "cell", "btn", "gap", "help", "line"):
        chk.append(grid[k])
    chk.extend(foot)
    chk.check("SkyyOps")
    SUI.assert_proven(chk, what="admin page")
    SUI.assert_proven(subs + subn, what="admin page sub-tabs")
    SUI.check_sky_paths(chk, tab_icons=True)
    for _v in (0, 1):     # SUI.assert_menu_page renders each markup: one pass per variant of the choose() pieces (kit 1.7 takes no Choice)
        SUI.assert_menu_page(SUI.Appends([(p_, mk.variants()[_v] if isinstance(mk, SUI.Choice) else mk) for p_, mk in chk]), sh)
    # every fixed text fits: help lines (with the widest status), the sub line, the info lines
    for o in OPS:
        h_ = ops_help(o) + ((" - 99,999 open" if o[7] == "auction:count" else " - 9,999 items") if o[7] else "")
        assert SUI.text_width(h_, OPS_HELP_FS) <= help_w, "help text too wide for its cell: " + h_
        assert SUI.text_width(o[1], 12, bold=True, upper=True) <= OPS_BTN_W - 2 * OPS_BTN_PAD, "button label too wide: " + o[1]
    assert SUI.text_width("Press again", 12, bold=True, upper=True) <= OPS_BTN_W - 2 * OPS_BTN_PAD
    assert SUI.text_width(OPS_SUB, OPS_HELP_FS) <= IW, "sub line too wide"
    assert SUI.text_width("Not running: SkyyAccessories, SkyyCollections, SkyyExploration, SkyyMerchants, SkyyWardrobe,", OPS_HELP_FS + 1) <= row_w
    rows_h = SUI.grow_row_sizes(list_h - 2 * LP, BH, gap=OPS_ROW_GAP)
    return sh, P, (subn, subs, subgap), pick, grid, foot, list_h, rows_h, cell_w, help_w


OPS_SH, OPS_P, OPS_SUBMK, OPS_PICK_MK, OPS_GRID, OPS_FOOT, OPS_LIST_H, OPS_ROW_H, OPS_CELL_W, OPS_HELP_W = ops_page()
OPS_LIST_IN = OPS_LIST_H - 2 * SUI.WELL_LIST_PAD                           # the list well's inner height (growSize's room)
OPS_SHELL_JAVA = OPS_SH.java("b")
OPS_HUB_JAVA = SUI.java_hub_page(OPS_SH, "setup", cls="@PKG@.HubBar", uuid="me()")
assert OPS_HUB_JAVA == '@PKG@.HubBar.page17(b, ev, "SkyyOpsF", "settings", "setup", 1552, me(), 2);', OPS_HUB_JAVA
OPS_PART_JAVA = dict((k, SUI.java_append(p, mk)) for k, (p, mk) in OPS_P.items())
OPS_PICK_JAVA = "\n".join(SUI.java_append(p, mk) for p, mk in OPS_PICK_MK)
OPS_GRID_JAVA = dict((k, SUI.java_append(p, mk)) for k, (p, mk) in OPS_GRID.items())
OPS_FOOT_JAVA = "\n".join(SUI.java_append(p, mk) for p, mk in OPS_FOOT)
# the SET this menu is built with (Diagnostics compares the running versions with it; SkyyMenu = this build)
OPS_SET = [(m, (VERSION if m == "SkyyMenu" else v)) for m, v in _LIVE]
print("admin page: %d x %d (kit 1.7 hub page), %d buttons (%s), one scroll list (row sizes %s), kit %s"
      % (OPS_W, OPS_H, len(OPS), ", ".join("%s %d" % (t, len([o for o in OPS if o[0] == i])) for i, t in enumerate(OPS_TABS)), OPS_ROW_H, SUI_KIT_ID))

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
T = {  # @TOKEN@ -> class name, substituted into every Java block below
    "PR":   "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF":  "com.hypixel.hytale.component.Ref",
    "ST":   "com.hypixel.hytale.component.Store",
    "UNI":  "com.hypixel.hytale.server.core.universe.Universe",
    "WLD":  "com.hypixel.hytale.server.core.universe.world.World",
    "APC":  "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX":  "com.hypixel.hytale.server.core.command.system.CommandContext",
    "MSG":  "com.hypixel.hytale.server.core.Message",
    "HSV":  "com.hypixel.hytale.server.core.HytaleServer",
    "LOG":  "com.hypixel.hytale.logger.HytaleLogger",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "PGM":  "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "PGE":  "com.hypixel.hytale.protocol.packets.interface_.Page",
    "UCB":  "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB":  "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD":  "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":   "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "PLA":  "com.hypixel.hytale.server.core.entity.entities.Player",
    "INV":  "com.hypixel.hytale.server.core.inventory.Inventory",
    "IC":   "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "IS":   "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IGS":  "com.hypixel.hytale.server.core.ui.ItemGridSlot",
    "OCU":  "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction",
    "CMGR": "com.hypixel.hytale.server.core.command.system.CommandManager",
    "ACM":  "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "PLM":  "com.hypixel.hytale.server.core.plugin.PluginManager",
    "PLB":  "com.hypixel.hytale.server.core.plugin.PluginBase",
    "PMF":  "com.hypixel.hytale.common.plugin.PluginManifest",
    "TPP":  "com.hypixel.hytale.builtin.teleport.TeleportPlugin",
    "WRP":  "com.hypixel.hytale.builtin.teleport.Warp",
    "TRF":  "com.hypixel.hytale.math.vector.Transform",
    "V3D":  "org.joml.Vector3d",
    "R3F":  "com.hypixel.hytale.math.vector.Rotation3f",
    "TP":   "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport",
    "TPH":  "com.hypixel.hytale.builtin.teleport.components.TeleportHistory",
    "TC":   "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "HR":   "com.hypixel.hytale.server.core.modules.entity.component.HeadRotation",
    "PRE":  "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "PDE":  "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "PKG":  "com.skyy.menu",
    "MD":   "com.skyy.menu.MenuData",
    "MU":   "com.skyy.menu.MenuUtil",
    "RA":   "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "ATY":  "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    # 0.3.3: settings visibility by permission - PlayerRef.hasPermission(node) IS PermissionsModule.get().hasPermission(uuid, node)
    # (HytaleServer.jar bytecode), so the UUID form is the same check the menu uses for Server Setup
    "PERM": "com.hypixel.hytale.server.core.permissions.PermissionsModule",
    # 0.3.6: the stuck-page fix - the page event the engine itself handles (Dismiss / Data), the world of a store, the world-join event
    "EST":  "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "CPE":  "com.hypixel.hytale.protocol.packets.interface_.CustomPageEvent",
    "CPT":  "com.hypixel.hytale.protocol.packets.interface_.CustomPageEventType",
    "ATW":  "com.hypixel.hytale.server.core.event.events.player.AddPlayerToWorldEvent",
    "HLD":  "com.hypixel.hytale.component.Holder",
    # 0.3.10: the Stats page reads the player's Health / Mana / Stamina (max + the MAX modifiers by key) on the world thread
    "ESM":  "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV":  "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST":  "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "SMO":  "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier",
    "MTG":  "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget",
    "CAL":  "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType",
    # 0.3.19: the hub hotkey - an EntityTickingSystem on players reading the server's copy of the client's movement states
    "ETS":  "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "QRY":  "com.hypixel.hytale.component.query.Query",
    "ACH":  "com.hypixel.hytale.component.ArchetypeChunk",
    "CB":   "com.hypixel.hytale.component.CommandBuffer",
    "MSC":  "com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent",
    "MVS":  "com.hypixel.hytale.protocol.MovementStates",
}
def jv(src):
    for k, v in T.items():
        src = src.replace("@" + k + "@", v)
    assert "@" not in src, "unreplaced token in: " + src[:200]
    return src

# ================= javassist =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

for c, m in ((T["PLA"], "getInventory"), (T["PLA"], "getPageManager"), (T["PLA"], "getComponentType"),
             (T["PGM"], "openCustomPage"), (T["PGM"], "setPage"), (T["PGM"], "getCustomPage"), (T["PGE"], "None"),
             (T["INV"], "getStorage"), (T["INV"], "getHotbar"), (T["INV"], "getBackpack"), (T["INV"], "getUtility"), (T["INV"], "getTools"),
             (T["IC"], "getItemStack"), (T["IC"], "addItemStack"), (T["IC"], "addItemStackToSlot"), (T["IC"], "getCapacity"),
             (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "isEmpty"),
             (T["IGS"], "setName"), (T["IGS"], "setDescription"), (T["IGS"], "setActivatable"), (T["IGS"], "setItemIncompatible"),
             (T["IGS"], "setSkipItemQualityBackground"),
             (T["PR"], "getUuid"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"), (T["PR"], "getWorldUuid"), (T["PR"], "getReference"),
             (T["PR"], "isValid"), (T["PR"], "hasPermission"), (T["REF"], "isValid"), (T["REF"], "getStore"),
             (T["ST"], "getComponent"), (T["ST"], "addComponent"), (T["ST"], "ensureAndGetComponent"),
             (T["PAGE"], "rebuild"), (T["PAGE"], "build"), (T["PAGE"], "handleDataEvent"),
             (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"),
             (T["BT"], "Activating"), (T["BT"], "SlotClicking"), (T["BT"], "Dismissing"), (T["ACM"], "getSubCommand"), (T["PAGE"], "sendUpdate"),
             (T["ACM"], "getName"), (T["ACM"], "getAliases"), (T["CMGR"], "getCommandRegistration"), (T["LIFE"], "CanDismiss"), (T["OCU"], "registerSimple"),
             (T["CMGR"], "get"), (T["CMGR"], "resolveCommand"), (T["CMGR"], "handleCommand"),
             (T["ACM"], "hasPermission"), (T["ACM"], "getPermission"), (T["ACM"], "addAliases"), (T["ACM"], "setPermissionGroups"),
             (T["PLM"], "get"), (T["PLM"], "getPlugins"), (T["PLB"], "getManifest"), (T["PLB"], "isEnabled"),
             (T["PLB"], "getDataDirectory"), (T["PLB"], "getCommandRegistry"), (T["PLB"], "getEventRegistry"), (T["PLB"], "getLogger"),
             (T["PLB"], "shutdown"), (T["PMF"], "getName"), (T["PMF"], "getVersion"),
             (T["TPP"], "get"), (T["TPP"], "getWarps"), (T["TPP"], "isWarpsLoaded"),
             (T["WRP"], "getId"), (T["WRP"], "getWorld"), (T["WRP"], "getTransform"), (T["WRP"], "toTeleport"),
             (T["TRF"], "getPosition"), (T["TP"], "createForPlayer"), (T["TP"], "getComponentType"),
             (T["TPH"], "getComponentType"), (T["TPH"], "append"), (T["TC"], "getComponentType"), (T["TC"], "getPosition"),
             (T["HR"], "getComponentType"), (T["HR"], "getRotation"),
             (T["UNI"], "get"), (T["UNI"], "getWorld"), (T["UNI"], "getDefaultWorld"), (T["UNI"], "getPlayers"), (T["UNI"], "getPlayer"),
             (T["WLD"], "execute"), (T["WLD"], "getWorldConfig"), (T["WLD"], "getName"),
             ("com.hypixel.hytale.server.core.universe.world.WorldConfig", "getSpawnProvider"),
             ("com.hypixel.hytale.server.core.universe.world.spawn.ISpawnProvider", "getSpawnPointAsync"),
             (T["PRE"], "getPlayerRef"), (T["PDE"], "getPlayerRef"), (T["HSV"], "SCHEDULED_EXECUTOR"), (T["CTX"], "provided"),
             (T["BT"], "Validating"), (T["INV"], "getItemInHand"), (T["EVD"], "append"), (T["ACM"], "requirePermission"),
             (T["ACM"], "addUsageVariant"), (T["ACM"], "withRequiredArg"), (T["ATY"], "STRING"), (T["CTX"], "get"),
             (T["PERM"], "get"), (T["PERM"], "hasPermission")):
    B.probe(pool, c, m)
# 0.3.6: every engine member the stuck-page fix uses (all public; rebuild stays on 'this' inside MenuPage)
for c, m in ((T["PGM"], "handleLegacyCustomPageEvent"), (T["PGM"], "clearLegacyCustomPageAcknowledgements"), (T["PAGE"], "onDismiss"), (T["CPE"], "type"),
             (T["CPE"], "data"), (T["CPT"], "Dismiss"), (T["CPT"], "Data"), (T["EST"], "getWorld"), (T["ST"], "getExternalData"),
             (T["ATW"], "getHolder"), (T["ATW"], "getWorld"), (T["HLD"], "getComponent"), (T["PR"], "getComponentType")):
    B.probe(pool, c, m)
# 0.3.18 (Hytale 0.7.0): the exact signatures of the renamed page calls + the async spawn point
_PGM07 = pool.get(T["PGM"])
_PGM07.getMethod("handleLegacyCustomPageEvent", "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Store;L%s;)V" % T["CPE"].replace(".", "/"))
_PGM07.getMethod("clearLegacyCustomPageAcknowledgements", "()V")
pool.get("com.hypixel.hytale.server.core.universe.world.spawn.ISpawnProvider").getMethod(
    "getSpawnPointAsync", "(Lcom/hypixel/hytale/server/core/universe/world/World;Ljava/util/UUID;)Ljava/util/concurrent/CompletableFuture;")
# 0.3.19: every engine member the hub hotkey uses (the movement states are public fields of protocol.MovementStates)
for c, m in ((T["PLB"], "getEntityStoreRegistry"), (T["MSC"], "getComponentType"), (T["MSC"], "getMovementStates"), (T["ACH"], "getReferenceTo"),
             (T["MVS"], "crouching"), (T["MVS"], "onGround"), (T["MVS"], "sprinting"), (T["MVS"], "sliding"), (T["MVS"], "rolling"),
             (T["MVS"], "mantling"), (T["MVS"], "climbing"), (T["MVS"], "flying"), (T["MVS"], "gliding"), (T["MVS"], "swimming"),
             (T["MVS"], "inFluid"), (T["MVS"], "mounting"), (T["MVS"], "sitting"), (T["MVS"], "sleeping"), (T["ST"], "getExternalData"),
             (T["EST"], "getWorld"), (T["PGM"], "getCustomPage"), (T["PGM"], "openCustomPage"), (T["PLA"], "getWindowManager"),
             ("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager", "getWindows")):
    B.probe(pool, c, m)
assert str(pool.get("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager").getDeclaredMethod("getWindows").getReturnType().getName()) \
    == "java.util.List", "FIX ROUND: WindowManager.getWindows() returns a java.util.List (0.7.0)"
assert [str(m.getName()) for m in pool.get(T["ETS"]).getDeclaredMethods() if J["Modifier"].isAbstract(m.getModifiers())] == ["tick"], \
    "0.3.19: EntityTickingSystem's only abstract method is tick (getQuery comes from the system base)"
# 0.3.23: every engine member the Admin page uses (the command tree walk + the permission check of the exact node)
for c, m in ((T["ACM"], "getSubCommand"), (T["ACM"], "getVariantByArgCount"), (T["ACM"], "hasPermission"), (T["CMGR"], "handleCommand"),
             (T["CMGR"], "resolveCommand"), (T["ACM"], "getRequiredArguments"), (T["UNI"], "getPlayers"), (T["PR"], "getUsername")):
    B.probe(pool, c, m)
assert str(pool.get(T["ACM"]).getMethod("getVariantByArgCount", "(I)L%s;" % T["ACM"].replace(".", "/")).getName()) == "getVariantByArgCount"
assert str(pool.get(T["ACM"]).getMethod("hasPermission", "(Lcom/hypixel/hytale/server/core/command/system/CommandSender;)Z").getName()) == "hasPermission"
assert pool.get(T["PR"]).subtypeOf(pool.get("com.hypixel.hytale.server.core.command.system.CommandSender")), "0.3.23: PlayerRef is a CommandSender"
# 0.3.10: every engine member the Stats page uses
for c, m in ((T["ESM"], "getComponentType"), (T["ESM"], "get"), (T["ESV"], "getMax"), (T["ESV"], "getModifiers"),
             (T["DST"], "getHealth"), (T["DST"], "getMana"), (T["DST"], "getStamina"), (T["SMO"], "getAmount"),
             (T["SMO"], "getCalculationType"), (T["SMO"], "getTarget"), (T["MTG"], "MAX"), (T["CAL"], "ADDITIVE")):
    B.probe(pool, c, m)

PKG = T["PKG"]
# 0.2: every class goes through mk(), and the writeFile list below is checked against MADE (Settings-Spec 1.4: a class left out of
# that list is silently dead code - SkyySacks' self-test GrantTask). The 0.1.3 tooltip-file save task is gone (the switch lives in the registry).
MADE = []
def mk(name, sup=None):
    c = pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)
    MADE.append(c)
    return c
dat  = mk("MenuData")
utl  = mk("MenuUtil")
giv  = mk("Given")
mcfg = mk("MenuCfg")
sreg = mk("SetReg")
sst  = mk("SetStore")
ssv  = mk("SetSaveTask")
tip  = mk("Tips")
sld  = mk("SetLoadTask")
sgf  = mk("SetGetFn")
srf  = mk("SetRegFn")
ssf  = mk("SetSetFn")
sdc  = mk("SetDefCfg")
page = mk("MenuPage", T["PAGE"])
spg  = mk("SettingsPage", T["PAGE"])
apg  = mk("AdminPage", T["PAGE"])
ast  = mk("AdmSaveTask")
ref_ = mk("RefreshTask")
clo_ = mk("CloseTask")
guard = mk("PageGuard")     # 0.3.6: the world-join page guard (AddPlayerToWorldEvent) + forget / joins helpers
stale = mk("StaleTask")     # 0.3.6: forgets a page that has its own onDismiss on the new world's thread
mwat = mk("MenuWatch")      # 0.3.6: the menu page's safety net (BankWatch pattern)
fac  = mk("MenuPageFactory")
cmd  = mk("MenuCmd", T["APC"])
scmd = mk("SettingsCmd", T["APC"])
acmv = mk("AdminModCmd", T["APC"])
acmd = mk("AdminCmd", T["APC"])
snt  = mk("SoundTest")       # 0.3.24: /soundtest - the list + the 2D play (sound pass round 1)
ssw  = mk("SoundSw")         # 0.3.25: the per-player sound switch on the bridge (settings:sounds:<uuid>)
stv  = mk("SoundTestArgCmd", T["APC"])   # 0.3.24: the usage variant /soundtest <what>
stm  = mk("SoundTestCmd", T["APC"])      # 0.3.24: /soundtest
grt  = mk("GrantTask")
rdy  = mk("MenuReady")
seen = mk("SeenTick")
quit_ = mk("MenuQuit")
gtk  = mk("GivenTick")      # 0.3.4: the 2 s profile watch (a new profile gets its menu item without a world switch)
scl  = mk("StatsCalc")      # 0.3.10: the Stats page's numbers (bridge reads + the EntityStatMap of the player)
stp  = mk("StatsPage", T["PAGE"])
sta  = mk("StatsTask")      # 0.3.10: the one answer after Change Profile when /profiles did not open its page
stc  = mk("StatsCmd", T["APC"])
ops  = mk("OpsPage", T["PAGE"])     # 0.3.23: the Admin page (research/Admin-Page-Plan.md)
pet  = mk("PetTile")        # 0.3.14: the Pets tile's name / text / icon from the active profile's SkyyPets record (read only)
lay  = mk("MenuLayout")     # 0.3.17: the per-player menu layouts + the server default (files, cache, resolving)
lsv  = mk("LayoutSaveTask") # 0.3.17: the 300 ms delayed layout save on the server scheduler (never on the world thread)
spt  = mk("SpawnTask")      # 0.3.18: the Spawn tile's async spawn point (Hytale 0.7.0) -> the player's world thread -> spawnResolved
mio  = mk("MenuIO")         # 0.3.19: the private writer thread SkyyMenu-IO (every settings / layout / Server Setup / item-record file)
midx = mk("MenuIdx")        # 0.3.19: the small index of the bridge's settings:def:* keys + config:def:<Mod> names (Settings / Server Setup)
gsv  = mk("GivenSave")      # 0.3.19: writes a menu-item record on SkyyMenu-IO
mhk  = mk("MenuHotkey", T["ETS"])   # 0.3.19: the hub hotkey (double-tap crouch) - EntityTickingSystem on players
hko  = mk("HotkeyOpen")     # 0.3.19: opens the menu for the hotkey on the player's world thread
pl   = mk("SkyyMenuPlugin", JP)
# 0.3.28: hubs H2 - the kit's HubBar (kit skyyui 1.5, sky tabs) in OUR package (cross-jar classes are not allowed: every hub mod has its
# own copy of the same code), MenuHub (hub:last, the hub commands, Menu's own tab pages), the open / visible Functions, the 5 commands
hubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, sub=True, page=True)   # 0.3.29: kit 1.6; 0.3.33: + merged tabs; 0.3.35: kit 1.7
MADE.append(hubb)
mhh = SUI.install_hub_hide(pool, PKG + ".HubHide", CtField, CtNewMethod, CtNewConstructor)     # 0.3.33: a merged tab's hide Function
MADE.append(mhh)
mal  = mk("MenuAlert")      # 0.3.29: home:alert:SkyyMenu - what SkyyMenu itself knows for the Home page's Right now panel
mhub = mk("MenuHub")
mho  = mk("MenuHubOpen")
mhv  = mk("MenuHubVis")
mvo  = mk("MenuVtOpen")     # 0.3.30: a stand-in tab's open Function (the owner's bridge Function, e.g. gear:fn:smithing)
mvv  = mk("MenuVtVis")      # 0.3.30: a stand-in tab's visible Function (its command exists)
hcch = mk("HubCharCmd", T["APC"])
hcst = mk("HubStorageCmd", T["APC"])
hcmk = mk("HubMarketCmd", T["APC"])
hctr = mk("HubTravelCmd", T["APC"])
hcso = mk("HubSocialCmd", T["APC"])
hccr = mk("HubCraftCmd", T["APC"])   # 0.3.31: /crafting

def F(cls, src):
    cls.addField(CtField.make(jv(src), cls))
def M(cls, src):
    cls.addMethod(CtNewMethod.make(jv(src), cls))
def C(cls, src):
    cls.addConstructor(CtNewConstructor.make(jv(src), cls))

# ================= MenuData: everything from the MENU DATA section =================
for name, val in (("ITEM_ID", jstr(MENU_ITEM_ID)), ("PAGE_ID", jstr(PAGE_ID)), ("ICON_BACK", jstr(ICON_BACK)), ("ICON_PREV", jstr(ICON_PREV)),
                  ("ICON_NEXT", jstr(ICON_NEXT)), ("ICON_CLOSE", jstr(ICON_CLOSE)), ("ICON_WARP", jstr(ICON_WARP)),
                  ("ICON_WARP_LOCKED", jstr(ICON_WARP_LOCKED)), ("ICON_NO_WARPS", jstr(ICON_NO_WARPS)),   # 0.3.26
                  ("ICON_PLAYER", jstr(ICON_PLAYER)), ("FILLER", jstr(FILLER_ICON)), ("FOOT_COLOR", jstr(FOOT_COLOR)),
                  ("DIM_COLOR", jstr(DIM_COLOR)), ("Q", jstr('"'))):
    F(dat, "public static final String %s = %s;" % (name, val))
F(dat, "public static final boolean USE_MARKUP = %s;" % ("true" if USE_MARKUP else "false"))
F(dat, "public static final String[] V_KEY = %s;" % jarr([v[0] for v in VIEWS]))
F(dat, "public static final String[] V_TITLE = %s;" % jarr([txt(v[1]) for v in VIEWS]))
F(dat, "public static final String[] V_INTRO = %s;" % jarr([lines_of(v[2]) for v in VIEWS]))
F(dat, "public static final String[] E_VIEW = %s;" % jarr(E_VIEW))
F(dat, "public static final int[] E_SLOT = %s;" % jints(E_SLOT))
F(dat, "public static final String[] E_ICON = %s;" % jarr(E_ICON))
# 0.3.14: the Pets tile - SkyyPets kind id -> our icon item, and the icon without one
F(dat, "public static final String[] PET_KIND = %s;" % jarr(PET_ART))
F(dat, "public static final String[] PET_ICON = %s;" % jarr(["Skyy_Menu_Icon_Pet_" + _p for _p in PET_ART]))
F(dat, "public static final String ICON_PETS = %s;" % jstr(ICON_PETS))
F(dat, "public static final String[] E_NAME = %s;" % jarr(E_NAME))
F(dat, "public static final String[] E_BODY = %s;" % jarr(E_BODY))
F(dat, "public static final String[] E_FOOT = %s;" % jarr(E_FOOT))
F(dat, "public static final String[] E_ACT = %s;" % jarr(E_ACT))
# 0.3.16: per-tile visibility rules ("" = no rule) + the keys an unlock Function already failed for (one warning each)
F(dat, "public static final String[] E_PERM = %s;" % jarr(E_PERM))
F(dat, "public static final String[] E_OPEN = %s;" % jarr(E_OPEN))
F(dat, "public static final String[] E_NEED = %s;" % jarr(E_NEED))
F(dat, "public static final String[] E_UNLOCK = %s;" % jarr(E_UNLOCK))
F(dat, "public static final java.util.concurrent.ConcurrentHashMap TILE_WARNED = new java.util.concurrent.ConcurrentHashMap();")
# 0.3.17: the layout editor - tile keys of the saved files ("" = not a main tile), the grid size, the control slots, icons, texts
F(dat, "public static final String[] E_KEY = %s;" % jarr(E_KEY))
F(dat, "public static final int LAY_GRID = %d;" % LAY_GRID)
F(dat, "public static final String ICON_EMPTY = %s;" % jstr(ICON_EMPTY))   # simplify pass 1: the 9 x 6 editor's slots + icons went
for _k, _v in sorted(EDIT_TXT.items()):
    F(dat, "public static final String %s = %s;" % (_k, jstr(_v)))
F(dat, "public static final int[] PA_SLOT = %s;" % jints([a[0] for a in PA]))
F(dat, "public static final String[] PA_ICON = %s;" % jarr([a[1] for a in PA]))
F(dat, "public static final String[] PA_NAME = %s;" % jarr([txt(a[2]) for a in PA]))
F(dat, "public static final String[] PA_BODY = %s;" % jarr([lines_of(a[3]) for a in PA]))
F(dat, "public static final String[] PA_FOOT = %s;" % jarr([txt(a[4]) for a in PA]))
F(dat, "public static final String[] PA_CMD = %s;" % jarr([a[5] for a in PA]))
F(dat, "public static final boolean[] PA_CLOSE = %s;" % jbools([a[6] for a in PA]))
F(dat, "public static final int[] WARP_SLOTS = %s;" % jints(WARP_SLOTS))
F(dat, "public static final int[] PLAYER_SLOTS = %s;" % jints(PLAYER_SLOTS))
F(dat, "public static final int[] MOD_SLOTS = %s;" % jints(MOD_SLOTS))
F(dat, "public static final int NO_WARPS_SLOT = %d;" % NO_WARPS_SLOT)
F(dat, "public static final int NO_PLAYERS_SLOT = %d;" % NO_PLAYERS_SLOT)
F(dat, "public static final int PLAYER_HEAD_SLOT = %d;" % PLAYER_HEAD_SLOT)
F(dat, "public static final String[] MOD_NAME = %s;" % jarr([m["mod"] for m in MODS]))
F(dat, "public static final String[] MOD_VER = %s;" % jarr([m["version"] for m in MODS]))
F(dat, "public static final String[] MOD_ICON = %s;" % jarr([m["icon"] for m in MODS]))
F(dat, "public static final String[] MOD_CHECK = %s;" % jarr([m["check"] for m in MODS]))
F(dat, "public static final String[] MOD_BODY = %s;" % jarr(MOD_BODY))
for k, v in UI.items():
    F(dat, "public static final String UI_%s = %s;" % (k, jstr(v)))
F(dat, "public static final String[] UI_INFO = %s;" % jarr(UI_INFO))
F(dat, "public static final String[] ALIASES = %s;" % jarr(ALIASES))
F(dat, "public static final String[] SUB_CMD = %s;" % jarr([n[0] for n in NEEDS_SUB]))
F(dat, "public static final String[] SUB_SUB = %s;" % jarr([n[1] for n in NEEDS_SUB]))
F(dat, "public static final String[] SUB_NEED = %s;" % jarr([txt(n[2]) for n in NEEDS_SUB]))
F(dat, "public static final String[] MOD_OLD_NEED = %s;" % jarr(MOD_OLD_NEED))
F(dat, "public static final String[] MOD_OLD_BODY = %s;" % jarr(MOD_OLD_BODY))
F(dat, "public static final int[] PAL_SLOT = %s;" % jints([a[0] for a in PA_LEGACY]))
F(dat, "public static final String[] PAL_NEED = %s;" % jarr([a[1] for a in PA_LEGACY]))
F(dat, "public static final String[] PAL_NAME = %s;" % jarr([txt(a[2]) for a in PA_LEGACY]))
F(dat, "public static final String[] PAL_BODY = %s;" % jarr([lines_of(a[3]) for a in PA_LEGACY]))
F(dat, "public static final String[] PAL_FOOT = %s;" % jarr([txt(a[4]) for a in PA_LEGACY]))
# 0.2 settings data + page strings
F(dat, "public static final String[] SET_CAT_ID = %s;" % jarr([t[0] for t in SET_TABS]))
F(dat, "public static final String[] SET_TAB = %s;" % jarr([t[1] for t in SET_TABS]))
F(dat, "public static final String[] SET_HEAD = %s;" % jarr([t[2] for t in SET_TABS]))
F(dat, "public static final String[] SET_ALWAYS = %s;" % jarr([t[3] for t in SET_TABS]))
F(dat, "public static final String[] SET_ORDER = %s;" % jarr(SET_ORDER))
F(dat, "public static final String[] SET_ORDER_MSG = %s;" % jarr(SET_ORDER_MSG))      # 0.3.21
F(dat, "public static final int SET_ROWS = %d;" % SET_ROWS)
F(dat, "public static final String SET_TEMPLATE = %s;" % jstr(SET_TEMPLATE))
for _n, _t in SET_TXT.items():
    F(dat, "public static final String SET_TXT_%s = %s;" % (_n, jstr(_t)))
F(dat, "public static final String TIPS_KEY = %s;" % jstr(TIPS_KEY))
F(dat, "public static final String HOTKEY_KEY = %s;" % jstr(HOTKEY_KEY))          # 0.3.19
F(dat, "public static final String SOUNDS_KEY = %s;" % jstr(SOUNDS_KEY))          # 0.3.25
F(dat, "public static final String SOUNDS_BRIDGE = %s;" % jstr(SOUNDS_BRIDGE))    # 0.3.25
assert SOUNDS_KEY in [k[0] for k in OWN_SETTINGS] and SOUNDS_BRIDGE == "settings:sounds:", "0.3.25: the sound switch is SkyyMenu's own (ON by default); the bridge key is the task contract"
assert HOTKEY_KEY in [k[0] for k in OWN_SETTINGS], "0.3.19: the hotkey switch is one of SkyyMenu's own settings (ON by default)"
F(dat, "public static final String[] OWN_KEY = %s;" % jarr([k[0] for k in OWN_SETTINGS]))
F(dat, "public static final String[] OWN_CAT = %s;" % jarr([k[1] for k in OWN_SETTINGS]))
F(dat, "public static final String[] OWN_LABEL = %s;" % jarr([k[2] for k in OWN_SETTINGS]))
F(dat, "public static final String[] OWN_HELP = %s;" % jarr([k[3] for k in OWN_SETTINGS]))
F(dat, "public static final boolean[] OWN_DEF = %s;" % jbools([True for k in OWN_SETTINGS]))
for _n, _t in UI_S.items():
    F(dat, "public static final String UI_%s = %s;" % (_n, jstr(_t)))
for _n, _v in UI_SARR.items():
    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))
F(dat, "public static final int STG_LIST_H = %d;" % STG_LIST_H)           # 0.3.35: the settings list + its row sizes (rule 7)
F(dat, "public static final int[] STG_ROW_H = %s;" % jints(STG_ROW_H))
F(dat, "public static final int STG_TAB_W = %d;" % STG_TAB_W)
# 0.3 Server Setup data + page strings
F(dat, "public static final String ADMIN_NODE = %s;" % jstr(ADMIN_NODE))
F(dat, "public static final String ADM_CONTRACT = %s;" % jstr(ADM_CONTRACT))
for _n, _v in (("ADM_ROWS", ADM_ROWS), ("ADM_LROWS", ADM_LROWS), ("ADM_GROWS", ADM_GROWS), ("ADM_HROWS", ADM_HROWS), ("ADM_INFOLINES", ADM_INFOLINES),
               ("ADM_MSGLINES", ADM_MSGLINES), ("ADM_PLINES", ADM_PLINES), ("ADM_FROWS", ADM_FROWS), ("ADM_INNER", A_INNER),
               ("ADM_ROWW", SUI.HUB_PAGE_IW)):   # 0.3.35: the sub-tab row / footer width
    F(dat, "public static final int %s = %d;" % (_n, _v))
for _n, _t in ADM_TXT.items():
    F(dat, "public static final String ADM_%s = %s;" % (_n, jstr(_t)))
for _n, _t in ADM_STYLE.items():
    F(dat, "public static final String ADM_%s = %s;" % (_n, jstr(_t)))
F(dat, "public static final String[] MOD_CFG = %s;" % jarr([m["config"] for m in MODS]))
F(dat, "public static final String[] MOD_RELOAD = %s;" % jarr([m["reload"] for m in MODS]))
F(dat, "public static final String[] MOD_NOTE = %s;" % jarr([m["note"] for m in MODS]))
F(dat, "public static final String[] MOD_ADMIN = %s;" % jarr(MOD_ADMIN))
F(dat, "public static final String[] MOD_FLINE = %s;" % jarr(MOD_FLINE))
# 0.3.1: which config kit revision this jar carries ("<kit> <first 12 hex of the skyycfg.py git blob>"), shown in the ready line
F(dat, "public static final String CFG_KIT = %s;" % jstr(KIT_ID))
# 0.3.1: admin-only Mods view lines + the Server Setup page each mod has from which version (fallback texts)
F(dat, "public static final String MOD_AHEAD = %s;" % jstr(MOD_AHEAD))
F(dat, "public static final String[] MOD_AONLY = %s;" % jarr(MOD_AONLY))
F(dat, "public static final String[] MOD_SINCE = %s;" % jarr(MOD_SINCE))
F(dat, "public static final String[] MOD_STITLE = %s;" % jarr(MOD_STITLE))
F(dat, "public static final String[] MOD_SWHAT = %s;" % jarr(MOD_SWHAT))
F(dat, "public static final String MENU_CFG_TEXT = %s;" % jstr(MENU_CFG_TEXT))
for _n, _t in UI_A.items():
    F(dat, "public static final String UI_%s = %s;" % (_n, jstr(_t)))
for _n, _v in UI_AARR.items():
    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))
for _n, _v in UI_AROWB.items():            # 0.3.36: the row group tails per grow tier, the per-row piece heads / tails
    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))
for _n, _t in UI_APIECE.items():
    F(dat, "public static final String UI_%s = %s;" % (_n, jstr(_t)))
for _k, _v in ADM_IN.items():
    F(dat, "public static final int ADM_IN_%s = %d;" % (_k.upper(), _v))
for _k, _v in ADM_RH.items():
    F(dat, "public static final int[] ADM_RH_%s = %s;" % (_k, jints(_v)))
for _n, _v in (("ADM_MFIELDS", ADM_MFIELDS), ("ADM_CATMIN", ADM_CATMIN), ("ADM_TFIELDS", ADM_TFIELDS), ("ADM_TMAX", ADM_TMAX), ("ADM_GMAX", ADM_GMAX), ("ADM_FMAX", ADM_FMAX), ("ADM_CWMAX", ADM_CWMAX),
               ("ADM_CRPAD", ADM_CRUMB_PAD), ("ADM_SUBH", SUI.SUB_TAB_H)):
    F(dat, "public static final int %s = %d;" % (_n, _v))
F(dat, "public static final int[] ADM_CW = %s;" % jints(ADM_CW))
# 0.3.28: hubs H2 - the 7 hubs (SUI.HUBS order: hub:def:<hub> = {title, command, icon}), the "coming soon" lines, SkyyMenu's own tabs
F(dat, "public static final int HUB_INFO_LINES = %d;" % HUB_INFO_LINES)
F(dat, "public static final String HUB_TXT_FAIL = %s;" % jstr(HUB_TXT_FAIL))
F(dat, "public static final int ADM_SUBMAX = %d;" % ADM_SUBMAX)
F(dat, "public static final String ADM_PREFIX = %s;" % jstr(ADM_PREFIX))
F(dat, "public static final String[] HUB_ID = %s;" % jarr(list(SUI.HUBS)))
F(dat, "public static final String[] HUB_TITLE = %s;" % jarr([hub_title(_h) for _h in SUI.HUBS]))   # 0.3.31: smithing = Crafting
F(dat, "public static final String[] HUB_CMD = %s;" % jarr([hub_cmd(_h) for _h in SUI.HUBS]))
F(dat, "public static final String[] HUB_ICON = %s;" % jarr([HUB_ICON_ITEM[_h] for _h in SUI.HUBS]))
F(dat, "public static final String[] HUB_SOON = %s;" % jarr([HUB_SOON[_h] for _h in SUI.HUBS]))
F(dat, "public static final String[] HT_HUB = %s;" % jarr([r[0] for r in HUB_OWN]))
F(dat, "public static final String[] HT_TAB = %s;" % jarr([r[1] for r in HUB_OWN]))
F(dat, "public static final int[] HT_ORDER = %s;" % jints([r[2] for r in HUB_OWN]))
F(dat, "public static final String[] HT_LABEL = %s;" % jarr([OWN_LABEL.get(r[1], r[3]) for r in HUB_OWN]))   # 0.3.29: layout -> Edit shortcuts
HT_HOST = [SUI.hub_merged_host(r[0], r[1]) or "" for r in HUB_OWN]   # 0.3.33: "" = a tab of its own; else the tab it is part of
assert [(r[1], x) for r, x in zip(HUB_OWN, HT_HOST) if x] == [("stats", "skills")], "0.3.33: Stats is Menu's only merged tab (part of Skills)"
F(dat, "public static final String[] HT_HOST = %s;" % jarr(HT_HOST))
# 0.3.29: UNIFIED MENU U1 - the shortcut grids, the one-time update table, Home / Teleport markup, the foot buttons, the texts
for _n, _v in (("HG_N", HG_N), ("HG_COLS", HG_COLS), ("HG_ROWS", HG_ROWS), ("HG_CR", HG_CR), ("HG_CC", HG_CC), ("OLD_COLS", OLD_COLS),
               ("OLD_CR", OLD_CR), ("OLD_CC", OLD_CC), ("HOME_FOOT_W", HOME_FOOT_W), ("TP_FOOT_W", TP_FOOT_W), ("FB_GAP", FB_GAP),
               ("AL_MAX", AL_MAX), ("AL_SHOW", AL_SHOW), ("YOU_BAR_W", YOU_BAR_W),
               # 0.3.30: the 7 x 5 file numbering, the big row 1 / row 2 of Home and Teleport
               ("G7_N", G7_N), ("G7_COLS", G7_COLS), ("G7_ROWS", G7_ROWS), ("G7_OFF", G7_OFF), ("G7_CR", G7_CR), ("G7_CC", G7_CC), ("HOME_ROW_W", HOME_ROW_W),
               ("TP_ROW_W", TP_ROW_W), ("BR_H", BR_H), ("BR_GAP", BR_GAP), ("BR_PAD", BR_PAD), ("BR_PADV", BR_PADV), ("BR_ICON", BR_ICON),
               ("BR_ICON_GAP", BR_ICON_GAP), ("BR_ICON_MIN", BR_ICON_MIN), ("BT_H", BT_H), ("BT_GAP", BT_GAP), ("BT_ICON", BT_ICON),
               ("BT_ICON_TOP", BT_ICON_TOP), ("BT_MIN", BT_MIN), ("BT_PAD", BT_PAD)):
    F(dat, "public static final int %s = %d;" % (_n, _v))
for _n, _v in (("BR_LABN", BR_LABN), ("BR_LABSEL", BR_LABSEL), ("BT_LAB", BT_LAB), ("TAB_ART_DIR", "SkyyHubTabs/")):
    F(dat, "public static final String %s = %s;" % (_n, jstr(_v)))
assert SUI.HUB_TAB_ICON_DIR == "SkyyHubTabs/", "0.3.30: the kit 1.6 tab icon folder"
F(dat, "public static final String[] TAB_KEY = %s;" % jarr(sorted(TAB_ICON)))
F(dat, "public static final String[] TAB_ICON = %s;" % jarr([TAB_ICON[_k] for _k in sorted(TAB_ICON)]))
F(dat, "public static final String[] TAB_ART = %s;" % jarr(TAB_ART))
F(dat, "public static final String[] VT_HUB = %s;" % jarr([_r[0] for _r in VT]))
F(dat, "public static final String[] VT_TAB = %s;" % jarr([_r[1] for _r in VT]))
F(dat, "public static final int[] VT_ORDER = %s;" % jints([_r[2] for _r in VT]))
F(dat, "public static final String[] VT_LABEL = %s;" % jarr([_r[3] for _r in VT]))
F(dat, "public static final String[] VT_CMD = %s;" % jarr([_r[4] for _r in VT]))
F(dat, "public static final String[] VT_FN = %s;" % jarr([VT_FN.get("%s:%s" % (_r[0], _r[1]), ("", ""))[0] for _r in VT]))
F(dat, "public static final String[] VT_ARG = %s;" % jarr([VT_FN.get("%s:%s" % (_r[0], _r[1]), ("", ""))[1] for _r in VT]))
F(dat, "public static final String[] MIG = %s;" % jarr([MIG.get(k, "") if k else "" for k in E_KEY]))
F(dat, "public static final String[] MIG_TAB = %s;" % jarr([TILE_TAB.get(k, "") if k else "" for k in E_KEY]))   # fix round: the tile's own tab
F(dat, "public static final String[] BH_KEY = %s;" % jarr([BUILTIN_HOME[k] for k in sorted(BUILTIN_HOME)]))
F(dat, "public static final int[] BH_SLOT = %s;" % jints(sorted(BUILTIN_HOME)))
F(dat, "public static final String[] BT_KEY = %s;" % jarr([BUILTIN_TP[k] for k in sorted(BUILTIN_TP)]))
F(dat, "public static final int[] BT_SLOT = %s;" % jints(sorted(BUILTIN_TP)))
F(dat, "public static final int[] TP_AUTO = %s;" % jints(TP_AUTO))
F(dat, "public static final String[] TPK_KEY = %s;" % jarr(sorted(TP_KEYS)))
F(dat, "public static final String[] WI_THEME = %s;" % jarr(WI_THEME))      # 0.3.37: warp icon themes (SkyyEssentials 0.1.14) -> icon items
F(dat, "public static final String[] WI_ICON = %s;" % jarr(WI_ICON))
F(dat, "public static final String ICON_ZHOME = %s;" % jstr(ICON_ZHOME))
F(dat, "public static final String ICON_IHOME = %s;" % jstr(ICON_IHOME))
F(dat, "public static final int[] TPK_E = %s;" % jints([x[0] for x in TPK_E]))
F(dat, "public static final String[] HUB_DEFTAB = %s;" % jarr([HUB_DEFTAB.get(_h, "") for _h in SUI.HUBS]))
F(dat, "public static final String[] HUB_BLURB = %s;" % jarr([HUB_BLURB[_h] for _h in SUI.HUBS]))
# 0.3.34: a saved shortcut of a merged-away tab -> where its page went (MenuPage.redirect): key, target ("tab:..." or "cmd:<command>"), name, hover
REDIR = [('tab:storage:bank', 'tab:storage:vault', 'Bank', "the Vault tab - the Bank's coins are part of it now"), ('tab:market:auctions', 'cmd:ah', 'Auction House', 'the Auction House - part of the Market tab now')]
assert all(_f in ["tab:%s:%s" % (_r[0], _r[1]) for _r in SUI.HUB_TABS] and (_t.startswith("cmd:") or _t in ["tab:%s:%s" % (_r[0], _r[1]) for _r in SUI.HUB_TABS]) for _f, _t, _n, _w in REDIR)
F(dat, "public static final String[] REDIR_FROM = %s;" % jarr([_r[0] for _r in REDIR]))
F(dat, "public static final String[] REDIR_TO = %s;" % jarr([_r[1] for _r in REDIR]))
F(dat, "public static final String[] REDIR_NAME = %s;" % jarr([_r[2] for _r in REDIR]))
F(dat, "public static final String[] REDIR_WHY = %s;" % jarr([_r[3] for _r in REDIR]))
F(dat, "public static final String HOME_TITLE = %s;" % jstr(HOME_TITLE))
F(dat, "public static final String HOME_ICON = %s;" % jstr(HOME_ICON))
for _k, _v in sorted(HOME_TXT.items()):
    if _k in ("HT_YOU_TITLE", "HT_YOU_HINT", "HT_NOW_TITLE", "HT_NOW_NONE"):   # baked into the UI29 markup at build time; never read at runtime
        continue
    F(dat,"public static final String %s = %s;" % (_k, jstr(_v)))
for _k, _v in sorted(UI29.items()):
    F(dat, "public static final String UI_%s = %s;" % (_k, jstr(_v)))
F(dat, "public static final String[] UI_HYL = %s;" % jarr(UI29_HYL))
F(dat, "public static final String[] UI_HA = %s;" % jarr(UI29_HA))
F(dat, "public static final String[] UI_FBH = %s;" % jarr(UI29_FBH))
F(dat, "public static final String[] UI_FBT = %s;" % jarr(UI29_FBT))
for _k, _v in sorted(UI35.items()):        # 0.3.35: the classic views on the kit 1.7 page
    F(dat, "public static final String UI_%s = %s;" % (_k, jstr(_v)))
F(dat, "public static final String[] UI_CINFO = %s;" % jarr(UI35_CINFO))
F(dat, "public static final int CL_INFO_LINES = %d;" % CL_INFO_LINES)
F(dat, "public static final String[] FB_WORD = %s;" % jarr([f[0] for f in FB]))
F(dat, "public static final int[] FB_W = %s;" % jints([f[2] for f in FB]))
F(dat, "public static final int[] FB_TW = %s;" % jints(FB_TW))
F(dat, "public static final String[] HT_CMD = %s;" % jarr([r[4] or "" for r in HUB_OWN]))
F(dat, "public static final boolean[] HT_VIS = %s;" % jbools([r[1] in HUB_OWN_VIS for r in HUB_OWN]))
# tooltip = first line, blank line, detail lines, blank line, colored footer (ItemGridSlot.Description takes item-tooltip markup:
# TheArmoryMod wraps its slot descriptions in <color is=...>, <b>, <i>; vanilla item descriptions use the same tags)
M(dat, r"""
public static String tooltip(String body, String foot, boolean dim) {
  StringBuilder sb = new StringBuilder();
  String b0 = body == null ? "" : body;
  int nl = b0.indexOf('\n');
  if (nl >= 0) sb.append(b0.substring(0, nl)).append("\n\n").append(b0.substring(nl + 1));
  else sb.append(b0);
  if (foot != null && foot.length() > 0) {
    sb.append("\n\n");
    if (USE_MARKUP) sb.append("<color is=").append(Q).append(dim ? DIM_COLOR : FOOT_COLOR).append(Q).append(">").append(foot).append("</color>");
    else sb.append(foot);
  }
  return sb.toString();
}""")
M(dat, r"""
public static int viewIndex(String v) {
  for (int i = 0; i < V_KEY.length; i++) if (V_KEY[i].equals(v)) return i;
  return 0;
}""")

# ================= MenuUtil: logging, bridge, text, inventory, commands, plugins =================
F(utl, "public static @LOG@ LOG;")
# 0.3.19 A: lock-free bridge (research/Code-Structure-Audit.md pattern 1; the tools/skyycfg.py kit snippet): cached in BRIDGE after the
# first call; only that call takes the System.class monitor, to create the map exactly like before (same identity, same creation)
F(utl, "public static volatile java.util.Map BRIDGE;")
M(utl, r"""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""")
M(utl, r"""
public static java.util.Map bridge() {
  java.util.Map m = BRIDGE;
  if (m != null) return m;
  synchronized (java.lang.System.class) { m = bridge0(); }
  BRIDGE = m;
  return m;
}""")
M(utl, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyMenu] " + msg); } catch (Throwable t) { }
}""")
M(utl, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyMenu] " + msg); } catch (Throwable t) { }
}""")
# 0.2 (Settings-Spec 1.4): SkyyProfiles' ProfCfg.atomicWrite verbatim - tmp file + fsync + atomic rename (a plain replace only where the
# file system cannot rename atomically); Windows sharing violations are retried 5 x 20 ms before the write counts as failed.
M(utl, r"""
public static void atomicWrite(java.nio.file.Path f, byte[] data) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try {
    out.write(data);
    out.flush();
    out.getFD().sync();
  } finally { out.close(); }
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.AtomicMoveNotSupportedException e) {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""")
# dynamic text (player names, warp names, world names) -> one safe line, no markup
M(utl, r"""
public static String safe(String t) {
  if (t == null) return "";
  String s = t.replace('"', '\'').replace('\\', '/').replace('{', '(').replace('}', ')').replace(';', ',')
              .replace('<', '[').replace('>', ']').replace('\n', ' ').replace('\r', ' ');
  if (s.length() > 120) s = s.substring(0, 120);
  return s;
}""")
# a name that may be pasted into a command line: letters, digits and _ only
M(utl, r"""
public static String cleanName(String n) {
  if (n == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < n.length() && i < 32; i++) {
    char c = n.charAt(i);
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_') sb.append(c);
  }
  return sb.toString();
}""")
M(utl, r"""
public static String fmt(long v) {
  String s = String.valueOf(v < 0L ? -v : v);
  StringBuilder sb = new StringBuilder();
  int n = s.length();
  for (int i = 0; i < n; i++) {
    if (i > 0 && (n - i) % 3 == 0) sb.append(',');
    sb.append(s.charAt(i));
  }
  return (v < 0L ? "-" : "") + sb.toString();
}""")
# SlotClicking payload: {"a":"mslot","SlotIndex":3} (value may be quoted) - same helper as SkyyHud EditorPage.jsonInt
M(utl, r"""
public static int jsonInt(String data, String key) {
  int p = data.indexOf("\"" + key + "\"");
  if (p < 0) return -1;
  int c = data.indexOf(':', p);
  if (c < 0) return -1;
  int i = c + 1;
  while (i < data.length() && (data.charAt(i) == ' ' || data.charAt(i) == '"')) i++;
  int j = i;
  while (j < data.length() && (Character.isDigit(data.charAt(j)) || data.charAt(j) == '-')) j++;
  if (j == i) return -1;
  try { return Integer.parseInt(data.substring(i, j)); } catch (Throwable t) { return -1; }
}""")
# ---- bridge reads (all optional: -1 / null when the mod is not loaded)
M(utl, r"""
public static long purse(java.util.UUID u) {
  try {
    Object f = bridge().get("coins:fn:get");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof Number) return ((Number) r).longValue();
    }
    Object v = bridge().get("coins:" + u.toString());
    if (v instanceof Number) return ((Number) v).longValue();
  } catch (Throwable t) { }
  return -1L;
}""")
M(utl, r"""
public static long bank(java.util.UUID u) {
  try {
    Object v = bridge().get("bank:" + u.toString());
    if (v instanceof Number) return ((Number) v).longValue();
  } catch (Throwable t) { }
  return -1L;
}""")
M(utl, r"""
public static String skills(java.util.UUID u) {
  try {
    Object v = bridge().get("skill:" + u.toString());
    if (!(v instanceof String)) return null;
    String[] parts = ((String) v).split(",");
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < parts.length; i++) {
      String p = parts[i].trim();
      int c = p.indexOf(':');
      if (c <= 0) continue;
      if (sb.length() > 0) sb.append(", ");
      sb.append(safe(p.substring(0, c))).append(' ').append(safe(p.substring(c + 1)));
    }
    return sb.length() == 0 ? null : sb.toString();
  } catch (Throwable t) { return null; }
}""")
M(utl, r"""
public static int csvCount(Object o) {
  if (!(o instanceof String)) return 0;
  String s = ((String) o).trim();
  if (s.length() == 0) return 0;
  String[] parts = s.split(",");
  int n = 0;
  for (int i = 0; i < parts.length; i++) if (parts[i].trim().length() > 0) n++;
  return n;
}""")
# ---- inventory (world thread only; SkyyBazaar Inv pattern: every add is verified by re-counting)
# 0.3.4: count() = every container the item can sit in (hotbar, storage, backpack, utility, tools) - "never a second copy" (Skyy)
M(utl, r"""
public static int countIn(@IC@ c, String id) {
  if (c == null || id == null) return 0;
  int n = 0;
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = c.getItemStack(s);
    if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
    n += it.getQuantity();
  }
  return n;
}""")
M(utl, r"""
public static int count(@PLA@ p, String id) {
  @INV@ inv = p == null ? null : p.getInventory();
  if (inv == null) return 0;
  return countIn(inv.getStorage(), id) + countIn(inv.getHotbar(), id) + countIn(inv.getBackpack(), id)
       + countIn(inv.getUtility(), id) + countIn(inv.getTools(), id);
}""")
# 0.3.30: items whose id starts with a prefix (Right now: SkyyGear's mystery bags Skyy_Unid_Bag_<Rarity>) - world thread only
M(utl, r"""
public static int countInPrefix(@IC@ c, String pre) {
  if (c == null || pre == null) return 0;
  int n = 0;
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = c.getItemStack(s);
    if (it == null || it.isEmpty()) continue;
    String id = it.getItemId();
    if (id != null && id.startsWith(pre)) n += it.getQuantity();
  }
  return n;
}""")
M(utl, r"""
public static int countPrefix(@PLA@ p, String pre) {
  @INV@ inv = p == null ? null : p.getInventory();
  if (inv == null) return 0;
  return countInPrefix(inv.getStorage(), pre) + countInPrefix(inv.getHotbar(), pre) + countInPrefix(inv.getBackpack(), pre)
       + countInPrefix(inv.getUtility(), pre) + countInPrefix(inv.getTools(), pre);
}""")
# last hotbar slot if free (Hypixel keeps the menu in slot 9), else any hotbar slot, else storage, else backpack
M(utl, r"""
public static boolean giveMenuItem(@PLA@ p) {
  if (p == null) return false;
  @INV@ inv = p.getInventory();
  if (inv == null) return false;
  String id = @PKG@.MenuData.ITEM_ID;
  int before = count(p, id);
  @IC@ hb = inv.getHotbar();
  if (hb != null) {
    try {
      short last = (short) (hb.getCapacity() - 1);
      if (last >= 0) {
        @IS@ cur = hb.getItemStack(last);
        if (cur == null || cur.isEmpty()) hb.addItemStackToSlot(last, new @IS@(id, 1));
      }
    } catch (Throwable t) { warn("hotbar slot add failed: " + t); }
    if (count(p, id) > before) return true;
    try { hb.addItemStack(new @IS@(id, 1)); } catch (Throwable t) { warn("hotbar add failed: " + t); }
    if (count(p, id) > before) return true;
  }
  @IC@[] rest = new @IC@[] { inv.getStorage(), inv.getBackpack() };
  for (int i = 0; i < rest.length; i++) {
    if (rest[i] == null) continue;
    try { rest[i].addItemStack(new @IS@(id, 1)); } catch (Throwable t) { warn("storage add failed: " + t); }
    if (count(p, id) > before) return true;
  }
  return false;
}""")
# ---- commands / plugins
M(utl, r"""
public static @ACM@ cmd(String name) {
  try { return @CMGR@.get().resolveCommand(name.toLowerCase()); } catch (Throwable t) { return null; }
}""")
M(utl, r"""
public static String firstWord(String line) {
  if (line == null) return null;
  int sp = line.indexOf(' ');
  return sp > 0 ? line.substring(0, sp) : line;
}""")
# 0.1.3: "island menu" -> null when /island has that subcommand (or /island is missing: the normal "not installed" path) or the check
# fails (fail open: the command itself answers), else what the server needs ("SkyyIslands 0.5"). getSubCommand lower-cases + resolves aliases.
M(utl, r"""
public static String needOf(String line) {
  if (line == null) return null;
  String[] w = line.trim().split(" ");
  if (w.length < 2) return null;
  for (int i = 0; i < @PKG@.MenuData.SUB_CMD.length; i++) {
    if (!@PKG@.MenuData.SUB_CMD[i].equals(w[0]) || !@PKG@.MenuData.SUB_SUB[i].equals(w[1])) continue;
    @ACM@ c = cmd(w[0]);
    if (c == null) return null;
    try { if (c.getSubCommand(w[1]) != null) return null; } catch (Throwable t) { return null; }
    return @PKG@.MenuData.SUB_NEED[i];
  }
  return null;
}""")
# review 2026-09-24: version-dependent wording. Index into PAL_* when that player action must show its OLD text, else -1.
M(utl, r"""
public static int legacyPa(int slot) {
  for (int j = 0; j < @PKG@.MenuData.PAL_SLOT.length; j++) {
    if (@PKG@.MenuData.PAL_SLOT[j] == slot && needOf(@PKG@.MenuData.PAL_NEED[j]) != null) return j;
  }
  return -1;
}""")
# the Mods-list text of mod k: its "old" wording while the installed version lacks the subcommand, else the normal one
M(utl, r"""
public static String modBody(int k) {
  if (k < 0 || k >= @PKG@.MenuData.MOD_BODY.length) return "";
  String need = @PKG@.MenuData.MOD_OLD_NEED[k];
  if (need != null && need.length() > 0 && needOf(need) != null) return @PKG@.MenuData.MOD_OLD_BODY[k];
  return @PKG@.MenuData.MOD_BODY[k];
}""")
# 0.3.1: the Mods-list text for this viewer: admins also read the mod's admin-only lines (MODS "admin") right under the description;
# players get modBody unchanged. The "old" wording (an older installed version) carries its own lines only. = MOD_ABODY in Python.
M(utl, r"""
public static String modBodyFor(int k, boolean admin) {
  String body = modBody(k);
  if (!admin || k < 0 || k >= @PKG@.MenuData.MOD_AONLY.length) return body;
  String a = @PKG@.MenuData.MOD_AONLY[k];
  if (a == null || a.length() == 0) return body;
  String need = @PKG@.MenuData.MOD_OLD_NEED[k];
  if (need != null && need.length() > 0 && needOf(need) != null) return body;
  int nl = body.indexOf('\n');
  if (nl < 0) return body + "\n" + @PKG@.MenuData.MOD_AHEAD + "\n" + a;
  return body.substring(0, nl) + "\n" + @PKG@.MenuData.MOD_AHEAD + "\n" + a + body.substring(nl);
}""")
# 0.3.1: version order of two manifest versions ("0.3.10" > "0.3.9"): -1, 0 or 1; parts are the leading digits of each dot part
# (missing or non-numeric = 0), so an unknown "?" compares equal to "0" and never throws
M(utl, r"""
public static int verNum(String p) {
  int n = 0;
  if (p == null) return 0;
  for (int i = 0; i < p.length() && i < 9; i++) {
    char c = p.charAt(i);
    if (c < '0' || c > '9') break;
    n = n * 10 + (c - '0');
  }
  return n;
}""")
M(utl, r"""
public static int verCmp(String a, String b) {
  if (a == null || b == null) return 0;
  String[] x = a.trim().split("\\.");
  String[] y = b.trim().split("\\.");
  int n = x.length > y.length ? x.length : y.length;
  for (int i = 0; i < n; i++) {
    int p = i < x.length ? verNum(x[i]) : 0;
    int q = i < y.length ? verNum(y[i]) : 0;
    if (p < q) return -1;
    if (p > q) return 1;
  }
  return 0;
}""")
# tools/PROFILES-CONTRACT.md rule 5: while SkyyProfiles runs a crash recovery the live inventory may not belong to the active profile
M(utl, r"""
public static boolean profileBusy(java.util.UUID u) {
  if (u == null) return false;
  try { return Boolean.TRUE.equals(bridge().get("profile:busy:" + u.toString())); } catch (Throwable t) { return false; }
}""")
# once per server run (first PlayerReadyEvent - every plugin has registered its commands by then): every command word of the menu
# must resolve to OUR MenuCmd, and no other root command may carry it as its name or an alias. The engine keeps one owner per word
# (CommandManager.resolveCommand: root names first, then the alias map, where the last alias registered wins), so a clash is silent
# in game - this makes it one WARNING line in the server log naming the other command's class.
F(utl, "public static boolean CHECKED;")
M(utl, r"""
public static synchronized boolean firstCheck() {
  if (CHECKED) return false;
  CHECKED = true;
  return true;
}""")
M(utl, r"""
public static void checkAliases() {
  try {
    String mine = "@PKG@.MenuCmd";
    String[] want = new String[@PKG@.MenuData.ALIASES.length + 1];
    want[0] = "skymenu";
    for (int i = 0; i < @PKG@.MenuData.ALIASES.length; i++) want[i + 1] = @PKG@.MenuData.ALIASES[i];
    int bad = 0;
    java.util.Map reg = @CMGR@.get().getCommandRegistration();
    java.util.ArrayList all = reg == null ? new java.util.ArrayList() : new java.util.ArrayList(reg.values());
    for (int i = 0; i < all.size(); i++) {
      Object o = all.get(i);
      if (!(o instanceof @ACM@) || mine.equals(o.getClass().getName())) continue;
      @ACM@ c = (@ACM@) o;
      String n = c.getName();
      java.util.Set al = c.getAliases();
      for (int k = 0; k < want.length; k++) {
        boolean byName = n != null && n.equalsIgnoreCase(want[k]);
        boolean byAlias = al != null && al.contains(want[k]);
        if (!byName && !byAlias) continue;
        bad++;
        warn("/" + want[k] + " is also claimed by /" + n + " (" + o.getClass().getName() + ") - only one command can answer it. Remove it from one of the two mods.");
      }
    }
    StringBuilder ok = new StringBuilder();
    for (int k = 0; k < want.length; k++) {
      @ACM@ r = cmd(want[k]);
      if (r == null || !mine.equals(r.getClass().getName())) {
        bad++;
        warn("/" + want[k] + " does not open the SkyWynn Menu (" + (r == null ? "not registered" : "answered by " + r.getClass().getName()) + ").");
      } else {
        ok.append(" /").append(want[k]);
      }
    }
    if (bad == 0) info("command check: " + ok.toString().trim() + " all belong to SkyyMenu");
  } catch (Throwable t) { warn("command check failed: " + t); }
}""")
# 0.2: once per server run (first PlayerReadyEvent, all commands registered): /settings and /skysettings must answer with OUR SettingsCmd.
# Duplicate command names are silently last-wins, so a clash is one WARNING line; the menu torch works whoever owns the name.
M(utl, r"""
public static void checkSettingsCmd() {
  try {
    String mine = "@PKG@.SettingsCmd";
    @ACM@ a = cmd("settings");
    @ACM@ b = cmd("skysettings");
    boolean okA = a != null && mine.equals(a.getClass().getName());
    boolean okB = b != null && mine.equals(b.getClass().getName());
    if (!okA) warn("another mod owns /settings (" + (a == null ? "not registered" : a.getClass().getName()) + ") - players can use /skysettings or the SkyWynn Menu");
    if (!okB) warn("/skysettings does not open the SkyyMenu settings (" + (b == null ? "not registered" : "answered by " + b.getClass().getName()) + ")");
    if (okA && okB) info("command check: /settings /skysettings belong to SkyyMenu");
  } catch (Throwable t) { warn("settings command check failed: " + t); }
}""")
# 0.3: is this player allowed into Server Setup (skyymenu.modconfig; false on any error)
M(utl, r"""
public static boolean isAdmin(@PR@ pr) {
  try { return pr != null && pr.hasPermission(@PKG@.MenuData.ADMIN_NODE); } catch (Throwable t) { return false; }
}""")
# text a mod supplies that goes INTO inline markup (button texts): only the characters proven inline survive (letters, digits, space,
# < > / -); & reads "and", everything else becomes a space. Labels never need this - they get their text through b.set.
M(utl, r"""
public static String inl(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < 40; i++) {
    char c = s.charAt(i);
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == ' ' || c == '<' || c == '>' || c == '/' || c == '-') sb.append(c);
    else if (c == '&') sb.append("and");
    else sb.append(' ');
  }
  return sb.toString().trim();
}""")
M(utl, r"""
public static String clip(String s, int n) {
  if (s == null) return "";
  if (s.length() <= n) return s;
  if (n <= 3) return s.substring(0, n);
  return s.substring(0, n - 3) + "...";
}""")
# a string value of a page event (the SkyyBank jsonStr, with a length cap): the key must be a JSON KEY (followed by ':'), not the same
# text inside a value (values are JSON-escaped, so a quote inside one is preceded by a backslash)
M(utl, r"""
public static String jstr(String data, String key, int max) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  String pat = qt + key + qt;
  int from = 0;
  int i = -1;
  while (true) {
    int p = data.indexOf(pat, from);
    if (p < 0) return "";
    int q = p + pat.length();
    while (q < data.length() && Character.isWhitespace(data.charAt(q))) q++;
    if ((p == 0 || data.charAt(p - 1) != 92) && q < data.length() && data.charAt(q) == ':') { i = q + 1; break; }
    from = p + 1;
  }
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < max) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) {
      char n = data.charAt(i + 1);
      if (n == 'u' && i + 5 < data.length()) {
        try { sb.append((char) Integer.parseInt(data.substring(i + 2, i + 6), 16)); } catch (Throwable t) { }
        i += 6;
        continue;
      }
      if (n == 'n' || n == 'r' || n == 't' || n == 'b' || n == 'f') sb.append(' '); else sb.append(n);
      i += 2;
      continue;
    }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
# 0.3: once per server run (first PlayerReadyEvent): /modconfig and /serversetup must answer with OUR AdminCmd (duplicate names are
# silently last-wins); the book in the menu works whoever owns the words
M(utl, r"""
public static void checkAdminCmd() {
  try {
    String mine = "@PKG@.AdminCmd";
    @ACM@ a = cmd("modconfig");
    @ACM@ b = cmd("serversetup");
    boolean okA = a != null && mine.equals(a.getClass().getName());
    boolean okB = b != null && mine.equals(b.getClass().getName());
    if (!okA) warn("/modconfig does not open Server Setup (" + (a == null ? "not registered" : "answered by " + a.getClass().getName()) + ") - admins can use the Server Setup tile in the SkyWynn Menu");
    if (!okB) warn("/serversetup does not open Server Setup (" + (b == null ? "not registered" : "answered by " + b.getClass().getName()) + ")");
    if (okA && okB) info("command check: /modconfig /serversetup belong to SkyyMenu");
  } catch (Throwable t) { warn("server setup command check failed: " + t); }
}""")
# version of a loaded Skyy mod read from its manifest ("0.6.1 SkyySacks" -> "0.6.1"); null when not loaded / disabled
M(utl, r"""
public static String liveVersion(String mod) {
  try {
    java.util.List ps = @PLM@.get().getPlugins();
    for (int i = 0; i < ps.size(); i++) {
      @PLB@ p = (@PLB@) ps.get(i);
      if (p == null) continue;
      @PMF@ m = p.getManifest();
      if (m == null) continue;
      String n = m.getName();
      if (n == null || !(n.equals(mod) || n.endsWith(" " + mod))) continue;
      if (!p.isEnabled()) return null;
      Object v = m.getVersion();
      return v == null ? "?" : safe(String.valueOf(v));
    }
  } catch (Throwable t) { }
  return null;
}""")
# PERMISSIONS HOOK (Skyy: "we will figure out permissions later, to lock off warps till people unlock them").
# Return false to lock a warp for this player: it is then shown greyed out with a Locked footer and cannot be used from the menu.
# Ideas: return pr.hasPermission("skyymenu.warp." + warpId.toLowerCase());  or check an unlock list / collection tier / coins paid.
M(utl, r"""
public static boolean isWarpUnlocked(@PR@ pr, String warpId) {
  return true;
}""")

# ================= 0.3.19 B: MenuIO - the private writer thread "SkyyMenu-IO" =================
# One daemon thread (a one-thread ScheduledThreadPoolExecutor, made on first use) for every file SkyyMenu reads or writes after start
# and the 30 s upkeep - never HytaleServer.SCHEDULED_EXECUTOR (the engine's one scheduler thread that every mod and the engine share).
# schedule() = false when it cannot take the task (not running: before setup or after stop) - every caller then does what 0.3.18 did
# when the shared executor refused (runs it inline). stop(): no new tasks, the queued ones run (at most waitMs), then the rest is dropped
# (the shutdown flushes of setup()'s counterpart write everything still dirty right after, as in 0.3.18).
mio.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
F(mio, "public static volatile java.util.concurrent.ScheduledThreadPoolExecutor EX;")
F(mio, "public static volatile boolean STOPPED = false;")
F(mio, "public static final String NAME = \"SkyyMenu-IO\";")
F(mio, "public static final java.util.concurrent.atomic.AtomicLong TASKS = new java.util.concurrent.atomic.AtomicLong();")
C(mio, "public MenuIO() { }")
M(mio, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, NAME);
  t.setDaemon(true);
  return t;
}""")
M(mio, r"""
public static synchronized java.util.concurrent.ScheduledThreadPoolExecutor ex0() {
  if (STOPPED) return null;
  if (EX == null) {
    java.util.concurrent.ScheduledThreadPoolExecutor e = new java.util.concurrent.ScheduledThreadPoolExecutor(1, new @PKG@.MenuIO());
    e.setRemoveOnCancelPolicy(true);
    EX = e;
  }
  return EX;
}""")
M(mio, r"""
public static java.util.concurrent.ScheduledThreadPoolExecutor ex() {
  java.util.concurrent.ScheduledThreadPoolExecutor e = EX;
  if (e != null && !STOPPED) return e;
  return ex0();
}""")
M(mio, r"""
public static boolean schedule(Runnable r, long ms) {
  if (r == null) return false;
  java.util.concurrent.ScheduledThreadPoolExecutor e = ex();
  if (e == null) return false;
  try {
    e.schedule(r, ms < 0L ? 0L : ms, java.util.concurrent.TimeUnit.MILLISECONDS);
    TASKS.incrementAndGet();
    return true;
  } catch (Throwable t) { return false; }
}""")
M(mio, r"""
public static java.util.concurrent.ScheduledFuture every(Runnable r, long firstMs, long periodMs) {
  java.util.concurrent.ScheduledThreadPoolExecutor e = ex();
  if (e == null || r == null) return null;
  try { return e.scheduleWithFixedDelay(r, firstMs, periodMs, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { return null; }
}""")
M(mio, r"""
public static boolean onIO() {
  return NAME.equals(Thread.currentThread().getName());
}""")
M(mio, r"""
public static synchronized java.util.concurrent.ScheduledThreadPoolExecutor take() {
  STOPPED = true;
  java.util.concurrent.ScheduledThreadPoolExecutor e = EX;
  EX = null;
  return e;
}""")
M(mio, r"""
public static synchronized void begin() {
  STOPPED = false;
}""")
M(mio, r"""
public static void stop(long waitMs) {
  java.util.concurrent.ScheduledThreadPoolExecutor e = take();
  if (e == null) return;
  e.shutdown();
  try { if (!e.awaitTermination(waitMs, java.util.concurrent.TimeUnit.MILLISECONDS)) e.shutdownNow(); }
  catch (InterruptedException ie) { e.shutdownNow(); }
}""")

# ================= 0.3.19 F: MenuIdx - the small index of the bridge keys the Settings / Server Setup pages need =================
# SET = every "settings:def:<key>" key, CFG = every <Mod> of a "config:def:<Mod>" key (sorted, published as new arrays - readers never
# lock). Built by scan() (one pass over a copy of the bridge's key set): at start (setup's drain does its own scan as before), at the
# first player's arrival (prime, on SkyyMenu-IO) and again on SkyyMenu-IO whenever a page asks and the bridge size changed or the index
# is older than MAX_AGE (never more than once per MIN_GAP). Only the very first page of a run with no index yet builds it in place.
midx.addInterface(pool.get("java.lang.Runnable"))
F(midx, "public static volatile String[] SET;")
F(midx, "public static volatile String[] CFG;")
F(midx, "public static volatile int SIZE = -1;")
F(midx, "public static volatile long AT = 0L;")
F(midx, "public static volatile long SCANS = 0L;")
F(midx, "public static final long MAX_AGE = 60000L;")
F(midx, "public static final long MIN_GAP = 2000L;")
F(midx, "public static final java.util.concurrent.atomic.AtomicBoolean BUSY = new java.util.concurrent.atomic.AtomicBoolean(false);")
C(midx, "public MenuIdx() { }")
M(midx, r"""
public static void scan() {
  java.util.Map br = @PKG@.MenuUtil.bridge();
  int n = br.size();
  java.util.ArrayList st = new java.util.ArrayList();
  java.util.ArrayList cf = new java.util.ArrayList();
  java.util.Iterator it = new java.util.ArrayList(br.keySet()).iterator();
  while (it.hasNext()) {
    Object k = it.next();
    if (!(k instanceof String)) continue;
    String ks = (String) k;
    if (ks.startsWith("settings:def:")) st.add(ks);
    else if (ks.startsWith("config:def:")) {
      String m = ks.substring(11);
      if (!cf.contains(m)) cf.add(m);
    }
  }
  java.util.Collections.sort(st);
  java.util.Collections.sort(cf);
  SET = (String[]) st.toArray(new String[0]);
  CFG = (String[]) cf.toArray(new String[0]);
  SIZE = n;
  AT = System.currentTimeMillis();
  SCANS = SCANS + 1L;
}""")
M(midx, r"""
public void run() {
  try { scan(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings / Server Setup index scan failed: " + t); }
  BUSY.set(false);
}""")
M(midx, r"""
public static void later() {
  if (!BUSY.compareAndSet(false, true)) return;
  if (@PKG@.MenuIO.schedule(new @PKG@.MenuIdx(), 0L)) return;
  try { scan(); } catch (Throwable t) { }
  BUSY.set(false);
}""")
M(midx, r"""
public static void prime() {
  later();
}""")
M(midx, r"""
public static void fresh() {
  if (SET == null || CFG == null) {
    try { scan(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings / Server Setup index scan failed: " + t); }
    return;
  }
  long now = System.currentTimeMillis();
  if (now - AT < MIN_GAP && now >= AT) return;
  if (@PKG@.MenuUtil.bridge().size() == SIZE && now - AT < MAX_AGE && now >= AT) return;
  later();
}""")
M(midx, r"""
public static String[] settingsKeys() {
  fresh();
  String[] a = SET;
  return a == null ? new String[0] : a;
}""")
M(midx, r"""
public static String[] configMods() {
  fresh();
  String[] a = CFG;
  return a == null ? new String[0] : a;
}""")

# ================= Given: persisted "already got the menu item" records + session guards =================
# 0.3.4 (Skyy, OPEN-QUESTIONS 2026-10-01): ONE RECORD PER PROFILE - DIR = Skyy_SkyyMenu/given-profile/<storage key>.txt, the key being
# SkyyProfiles' profile:fn:key (tools/PROFILES-CONTRACT.md: <uuid> for profile 1, <uuid>-p<N> for profile N; <uuid> without SkyyProfiles).
# LEGACY = Skyy_SkyyMenu/given/<uuid>.txt, the 0.1 - 0.3.3 per-PLAYER flags: only READ (a rollback to 0.3.3 still finds them). migrate():
# a player with a legacy flag and no per-profile record gets ONE record for the profile active when 0.3.4 first sees them.
F(giv, "public static java.nio.file.Path DIR;")
F(giv, "public static java.nio.file.Path LEGACY;")
F(giv, "public static final java.util.concurrent.ConcurrentHashMap SESSION = new java.util.concurrent.ConcurrentHashMap();")   # storage key -> TRUE: done this session
F(giv, "public static final java.util.concurrent.ConcurrentHashMap INFLIGHT = new java.util.concurrent.ConcurrentHashMap();")  # UUID -> TRUE: a grant runs now
F(giv, "public static final java.util.concurrent.ConcurrentHashMap CHECKED = new java.util.concurrent.ConcurrentHashMap();")   # uuid text -> TRUE: legacy flag looked at
F(giv, "public static final java.util.concurrent.ConcurrentHashMap READY = new java.util.concurrent.ConcurrentHashMap();")     # UUID -> TRUE: past the first PlayerReadyEvent
F(giv, "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> Long: a GrantTask is scheduled
F(giv, "public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();")     # 0.3.19 D: UUID -> the last profile:epoch seen
# a storage key is used in a file name: SkyyProfiles keys are <uuid> or <uuid>-p<N>; anything else falls back to the UUID
M(giv, r"""
public static boolean validKey(String k) {
  if (k == null || k.length() < 1 || k.length() > 80) return false;
  for (int i = 0; i < k.length(); i++) {
    char c = k.charAt(i);
    if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '-')) return false;
  }
  return true;
}""")
# the storage key of the player's ACTIVE profile (tools/PROFILES-CONTRACT.md pkey helper: never throws, safe from any thread, no lock held)
M(giv, r"""
public static String key(java.util.UUID u) {
  if (u == null) return null;
  try {
    Object f = @PKG@.MenuUtil.bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && validKey((String) r)) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(giv, r"""
public static synchronized boolean isGiven(String key) {
  try { return DIR != null && validKey(key) && java.nio.file.Files.exists(DIR.resolve(key + ".txt"), new java.nio.file.LinkOption[0]); }
  catch (Throwable t) { return false; }
}""")
# written once (an existing record is never rewritten - no file churn), atomic tmp + move
M(giv, r"""
public static synchronized boolean markGiven(String key) {
  try {
    if (DIR == null || !validKey(key)) return false;
    java.nio.file.Path f = DIR.resolve(key + ".txt");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return true;
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(key + ".txt.tmp");
    byte[] data = ("menu item given " + System.currentTimeMillis() + "\n").getBytes("UTF-8");
    java.nio.file.Files.write(tmp, data, new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    return true;
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not save the menu-item record for " + key + ": " + t); return false; }
}""")
# a per-profile record of ANY profile of this player (<uuid>.txt or <uuid>-p<N>.txt); a read error answers true (= migrate nothing)
M(giv, r"""
public static synchronized boolean hasAnyFor(String us) {
  if (DIR == null) return false;
  try {
    if (java.nio.file.Files.exists(DIR.resolve(us + ".txt"), new java.nio.file.LinkOption[0])) return true;
    if (!java.nio.file.Files.isDirectory(DIR, new java.nio.file.LinkOption[0])) return false;
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(DIR, us + "-p*.txt");
    boolean any = false;
    try { any = ds.iterator().hasNext(); } finally { ds.close(); }
    return any;
  } catch (Throwable t) { return true; }
}""")
# the 0.1 - 0.3.3 per-PLAYER flag -> the profile active NOW counts as given (once per player and server run; true = recorded now)
M(giv, r"""
public static synchronized boolean migrate(java.util.UUID u, String key) {
  if (u == null || !validKey(key)) return false;
  String us = u.toString();
  if (CHECKED.putIfAbsent(us, Boolean.TRUE) != null) return false;
  try {
    if (LEGACY == null || !java.nio.file.Files.exists(LEGACY.resolve(us + ".txt"), new java.nio.file.LinkOption[0])) return false;
  } catch (Throwable t) { return false; }
  if (hasAnyFor(us)) return false;
  boolean ok = markGiven(key);
  if (ok) @PKG@.MenuUtil.info("menu item: " + us + " got it from an older SkyyMenu - their current profile (" + key + ") counts as given");
  return ok;
}""")
# the PlayerReadyEvent / profile watch question: does the player's CURRENT profile still need this session's check?
M(giv, r"""
public static boolean wants(java.util.UUID u) {
  String k = key(u);
  return k != null && !SESSION.containsKey(k);
}""")
# one scheduled GrantTask per player (an entry older than 90 s is stale: a task that died without releasing)
M(giv, r"""
public static boolean claim(java.util.UUID u, long now) {
  if (u == null) return false;
  Long nv = Long.valueOf(now);
  for (int i = 0; i < 16; i++) {
    Object o = PENDING.get(u);
    if (o == null) {
      if (PENDING.putIfAbsent(u, nv) == null) return true;
    } else {
      if (o instanceof Long && now - ((Long) o).longValue() < 90000L) return false;
      if (PENDING.replace(u, o, nv)) return true;
    }
  }
  return false;
}""")
M(giv, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  String us = u.toString();
  java.util.Iterator it = new java.util.ArrayList(SESSION.keySet()).iterator();
  while (it.hasNext()) {
    Object k = it.next();
    if (k instanceof String && ((String) k).startsWith(us)) SESSION.remove(k);
  }
  READY.remove(u);
  EPOCH.remove(u);
}""")
M(giv, r"""
public static void retainOnline(java.util.HashSet online, java.util.HashSet onlineK) {
  java.util.Iterator it = new java.util.ArrayList(SESSION.keySet()).iterator();
  while (it.hasNext()) {
    Object k = it.next();
    String ks = k instanceof String ? (String) k : "";
    if (ks.length() < 36 || !onlineK.contains(ks.substring(0, 36))) SESSION.remove(k);
  }
  READY.keySet().retainAll(online);
  EPOCH.keySet().retainAll(online);
}""")

# ================= 0.3 MenuCfg: SkyyMenu's own server settings (Skyy_SkyyMenu/config.properties), bound to the config kit =================
# Fields are public static volatile (the kit writes them with the primitive Field setters, spec 1.4.1); load() is the kit's RELOAD
# (hand edits + Reload file) and the start-up load. init() writes the commented default file once when it is missing.
F(mcfg, "public static java.nio.file.Path FILE;")
F(mcfg, "public static volatile boolean GIVE_ITEM = true;")
F(mcfg, "public static volatile boolean MODS_HELP = true;")
F(mcfg, "public static volatile boolean KEEP_ITEM = true;")       # 0.3.32: Server Setup (menu.itemKeep) - the lifelong menu item
F(mcfg, "public static volatile long HOTKEY_GAP_MS = %dL;" % HOTKEY_GAP_MS)            # FIX ROUND: Server Setup (menu.hotkeyGapMs)
F(mcfg, "public static volatile long HOTKEY_COOLDOWN_MS = %dL;" % HOTKEY_COOLDOWN_MS)  # FIX ROUND: Server Setup (menu.hotkeyCooldownMs)
M(mcfg, r"""
public static long num(java.util.Properties p, String k, long def, long lo, long hi) {
  String v = p.getProperty(k);
  if (v == null) return def;
  long x = def;
  try { x = Long.parseLong(v.trim()); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("config.properties: " + k + "=" + v + " is not a whole number - using " + def); return def; }
  if (x < lo) { @PKG@.MenuUtil.warn("config.properties: " + k + "=" + x + " is below " + lo + " - using " + lo); return lo; }
  if (x > hi) { @PKG@.MenuUtil.warn("config.properties: " + k + "=" + x + " is above " + hi + " - using " + hi); return hi; }
  return x;
}""")
M(mcfg, r"""
public static boolean flag(java.util.Properties p, String k, boolean def) {
  String v = p.getProperty(k);
  if (v == null) return def;
  v = v.trim().toLowerCase();
  if (v.equals("true") || v.equals("on") || v.equals("yes") || v.equals("1")) return true;
  if (v.equals("false") || v.equals("off") || v.equals("no") || v.equals("0")) return false;
  @PKG@.MenuUtil.warn("config.properties: " + k + "=" + v + " is not true or false - using " + def);
  return def;
}""")
M(mcfg, r"""
public static void load() {
  java.nio.file.Path f = FILE;
  if (f == null) return;
  try {
    if (!java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) { GIVE_ITEM = true; MODS_HELP = true; KEEP_ITEM = true; HOTKEY_GAP_MS = 400L; HOTKEY_COOLDOWN_MS = 1500L; return; }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    GIVE_ITEM = flag(p, "giveItem", true);
    MODS_HELP = flag(p, "modsHelp", true);
    KEEP_ITEM = flag(p, "itemKeep", true);   // 0.3.32
    HOTKEY_GAP_MS = num(p, "hotkeyGapMs", 400L, 200L, 800L);
    HOTKEY_COOLDOWN_MS = num(p, "hotkeyCooldownMs", 1500L, 500L, 10000L);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("config.properties cannot be read (" + t + ") - the previous values stay"); }
}""")
M(mcfg, r"""
public static void init() {
  try {
    if (FILE != null && !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      @PKG@.MenuUtil.atomicWrite(FILE, @PKG@.MenuData.MENU_CFG_TEXT.getBytes("ISO-8859-1"));
      @PKG@.MenuUtil.info("wrote config.properties (SkyyMenu server settings - change them in Server Setup or in the file)");
    }
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not write the config.properties template: " + t); }
  load();
}""")
# the kit: CfgRows, CfgLog, CfgHist, CfgSaveTask, CfgFile, CfgFn, CfgPub in this package (tools/CONFIG-CONTRACT.md). The hook class
# SetDefCfg is compiled later (the kit calls hooks by reflection; KIT.write checks them). Started in setup() after the file loads.
KIT = CFG.emit(pool, PKG, MOD="SkyyMenu", TITLE="Menu", VERSION=VERSION, NODE=MENU_CFG_NODE, CATS=MENU_CFG_CATS, ROWS=MENU_CFG_ROWS,
               FILES=MENU_CFG_FILES, NOTE=MENU_CFG_NOTE, RELOAD="MenuCfg.load", KEEP=10,
               DEFAULTS={"config.properties": MENU_CFG_TEXT, "settings-defaults.properties": SET_TEMPLATE})
assert KIT.info.get("kit", "1.0") == EXPECTED_KIT, "the emitted config kit is %s, SkyyMenu pins %s" % (KIT.info.get("kit", "1.0"), EXPECTED_KIT)
# 0.3.19 B: SkyyMenu's own Server Setup rows (config.properties, settings-defaults.properties) are saved by the kit's CfgSaveTask, which
# the kit schedules on HytaleServer.SCHEDULED_EXECUTOR (CfgFile.schedule). In THIS jar that one method hands the task to SkyyMenu-IO
# instead; the kit's own fallback (a daemon thread that sleeps first) stays for when MenuIO cannot take it. Same task, same delay.
_kcf = pool.get(PKG + ".CfgFile")
_ksm = [_m for _m in _kcf.getDeclaredMethods() if str(_m.getName()) == "schedule"]
assert len(_ksm) == 1 and str(_ksm[0].getSignature()) == "(IJ)V", "0.3.19: the kit's CfgFile.schedule(int, long)"
_ksm[0].setBody(jv(r"""{
  @PKG@.CfgSaveTask t = new @PKG@.CfgSaveTask($1, $2);
  if (@PKG@.MenuIO.schedule(t, $2)) return;
  t.sleepFirst = true;
  Thread th = new Thread(t, "SkyyCfg-" + @PKG@.CfgRows.MOD);
  th.setDaemon(true);
  th.start();
}"""))
print("config kit: %d rows (kit %s, skyycfg.py blob %s), files %s" % (KIT.info["rows"], KIT.info.get("kit", "1.0"), KIT_BLOB[:12], ", ".join(KIT.info["files"])))

# ================= 0.2 Settings registry (research/Settings-Spec.md 1.2-1.5) =================
# Bridge contract (never removed; java.lang types only - every mod has its own classloader):
#   settings:fn:register  apply(Object[] { String mod, String key, String label, String category, Boolean def, String help [, String perm] })
#                         -> Boolean. 0.3.3: the optional 7th element = a permission node: only players holding it see the row (hidden, never
#                         greyed) and may set it; null / "" / six elements = every player; any value that is not a plain node
#                         (SetReg.validPerm) REFUSES THE KEY for this run (fail closed: hidden for all, set FALSE, get = its default).
#                         Two mods on one key: the stricter wins (a node is never dropped; two different nodes refuse the key).
#   settings:fn:get       apply(Object[] { UUID player, String key }) -> Boolean (choice, else admin default, else registered default; null = unknown;
#                         0.3.3: a refused key answers its registered default - never a stored choice)
#   settings:fn:set       apply(Object[] { UUID player, String key, Boolean value [, Boolean onlyIfUnset] }) -> Boolean (TRUE = stored state matches;
#                         0.3.3: FALSE for a key whose permission node the player lacks)
#   settings:def:<key>    the same Object[6] (or Object[7]) as register, written by every adopter at setup (drained here, so load order never matters)
# Guarantees: never throws (bad input = null / FALSE); never calls another mod, never writes the bridge from get/set, never touches ECS or
# inventories; the only locks are SetReg.class (register, memory only), SetStore.class (memory only - never held during file I/O) and
# SetStore's 64 lock stripes (one player's own file read / write; a stripe holder never takes another lock or calls out), so calling it
# from inside a caller's own lock is safe and no lock cycle exists. get is four ConcurrentHashMap reads + a HashMap read after the
# player's first read (preloaded at join); set / resetAll of a loaded player never wait for any disk write, not even that player's own.
# ---- SetReg: the registered switches (fields first - javassist) + the admin defaults file
F(sreg, "public static final java.util.concurrent.ConcurrentHashMap DEFS = new java.util.concurrent.ConcurrentHashMap();")
F(sreg, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")
# 0.3.3 (review): keys refused for this server run (a registration with a node that is not plain, or two mods with two different nodes):
# key -> the Boolean default settings:fn:get answers. Never cleared: hidden for everyone, may() false, set refused, later registrations
# refused - load order never makes a refused key visible. PERM_MOD: key -> the mod whose node gates the key (DEFS stays Object[7]).
F(sreg, "public static final java.util.concurrent.ConcurrentHashMap REFUSED = new java.util.concurrent.ConcurrentHashMap();")
F(sreg, "public static final java.util.concurrent.ConcurrentHashMap PERM_MOD = new java.util.concurrent.ConcurrentHashMap();")
F(sreg, "public static volatile java.util.HashMap ADMIN = new java.util.HashMap();")
F(sreg, "public static java.nio.file.Path ADMIN_FILE = null;")
F(sreg, "public static volatile long ADMIN_MTIME = -1L;")
# 0.3: time of the last in-game edit of settings-defaults.properties (Server Setup -> Menu); the 30 s re-read waits 5 s after one
F(sreg, "public static volatile long EDIT_AT = 0L;")
M(sreg, r"""
public static boolean validKey(String k) {
  if (k == null || k.length() < 3 || k.length() > 48) return false;
  char c0 = k.charAt(0);
  if (c0 < 'a' || c0 > 'z') return false;
  for (int i = 0; i < k.length(); i++) {
    char c = k.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '.')) return false;
  }
  return true;
}""")
M(sreg, r"""
public static String clip(Object o, int max) {
  if (o == null) return "";
  String s = String.valueOf(o).replace('\n', ' ').replace('\r', ' ').trim();
  return s.length() > max ? s.substring(0, max) : s;
}""")
M(sreg, r"""
public static int catIndex(String c) {
  for (int i = 0; i < @PKG@.MenuData.SET_CAT_ID.length; i++) if (@PKG@.MenuData.SET_CAT_ID[i].equals(c)) return i;
  return @PKG@.MenuData.SET_CAT_ID.length - 1;
}""")
# 0.3.3 (review): a permission node of a registration (element 7) must be PLAIN - the menu's own node pattern
# ^[a-z][a-z0-9]*(\.[a-z0-9]+)+$ (ADMIN_NODE / MENU_CFG_NODE), 3-100 characters: no leading "-" (the engine's personal-deny syntax would
# invert the check), no *, :, _, - or spaces, no "..", no trailing dot. Every literal node a Skyy mod uses passes (the harness scans them).
# null / "" never reach this (= no node).
M(sreg, r"""
public static boolean validPerm(String p) {
  if (p == null || p.length() < 3 || p.length() > 100) return false;
  char prev = p.charAt(0);
  if (prev < 'a' || prev > 'z') return false;
  boolean dot = false;
  for (int i = 1; i < p.length(); i++) {
    char c = p.charAt(i);
    if (c == '.') {
      if (prev == '.') return false;
      dot = true;
    } else if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9'))) return false;
    prev = c;
  }
  return dot && prev != '.';
}""")
# 0.3.3 (review): refuse a key for this run (register holds the SetReg lock): its registration leaves DEFS (whoever made it), REFUSED keeps
# the default settings:fn:get answers (the kept first registration's, else this one's), one warning per key
M(sreg, r"""
public static void refuse(String key, Boolean def, String why) {
  Object[] old = (Object[]) DEFS.remove(key);
  PERM_MOD.remove(key);
  Boolean d = old != null && old[4] instanceof Boolean ? (Boolean) old[4] : def;
  if (d == null) d = Boolean.TRUE;
  REFUSED.putIfAbsent(key, d);
  if (WARNED.putIfAbsent("refused:" + key, Boolean.TRUE) == null)
    @PKG@.MenuUtil.warn("setting " + key + ": " + why + " - the switch is refused until the next restart (hidden for every player, nobody can change it, it answers its default " + d + ")");
}""")
# idempotent: the same mod registering again updates label / help / tab / default; a different mod registering the same key (shared keys
# such as rewards.late) is accepted and the FIRST registration's texts and default are kept - one warning if the defaults differ.
# 0.3.3: DEFS values are Object[7] { mod, key, label, cat, def, help, perm } (perm null = every player).
# 0.3.3 review fixes (fail closed, load order never matters):
#   - a refused key (REFUSED) refuses every later registration (FALSE)
#   - a 7th element that is neither null, "" nor a plain node refuses the KEY (refuse(): also an earlier weaker registration goes)
#   - the stricter node wins: a node is never dropped (another mod's node gates the first mod's registration, a registration without
#     a node keeps the node already there, one warning); two different nodes from two mods refuse the key; a mod may change its own node
M(sreg, r"""
public static synchronized boolean register(Object o) {
  try {
    if (!(o instanceof Object[])) return false;
    Object[] a = (Object[]) o;
    if (a.length < 5) return false;
    String key = a[1] == null ? null : String.valueOf(a[1]);
    if (!validKey(key)) return false;
    String mod = clip(a[0], 32);
    String label = clip(a[2], 48);
    if (label.length() == 0) label = key;
    String cat = @PKG@.MenuData.SET_CAT_ID[catIndex(a[3] == null ? "" : String.valueOf(a[3]))];
    Boolean def = a[4] instanceof Boolean ? (Boolean) a[4] : Boolean.TRUE;
    String help = a.length > 5 ? clip(a[5], 100) : "";
    if (REFUSED.containsKey(key)) return false;
    String perm = null;
    if (a.length > 6 && a[6] != null) {
      String p = a[6] instanceof String ? ((String) a[6]).trim() : null;
      if (p == null || (p.length() > 0 && !validPerm(p))) {
        refuse(key, def, mod + " gave '" + clip(a[6], 60) + "', which is not a plain permission node");
        return false;
      }
      if (p.length() > 0) perm = p;
    }
    Object[] old = (Object[]) DEFS.get(key);
    String op = old != null && old.length > 6 && old[6] instanceof String ? (String) old[6] : null;
    Object pmo = PERM_MOD.get(key);
    String om = pmo instanceof String ? (String) pmo : (old == null ? null : String.valueOf(old[0]));
    if (old != null && !mod.equals(old[0])) {
      if (!def.equals(old[4]) && WARNED.putIfAbsent(key, Boolean.TRUE) == null)
        @PKG@.MenuUtil.warn("setting " + key + ": " + mod + " wants default " + def + ", " + old[0] + " registered " + old[4] + " first - keeping " + old[4]);
      if (perm == null || perm.equals(op)) {
        if (perm == null && op != null && WARNED.putIfAbsent("node:" + key, Boolean.TRUE) == null)
          @PKG@.MenuUtil.warn("setting " + key + ": " + mod + " registers it for every player, " + om + " with the node " + op + " - keeping the node " + op);
        return true;
      }
      if (op == null) {
        DEFS.put(key, new Object[] { old[0], key, old[2], old[3], old[4], old[5], perm });
        PERM_MOD.put(key, mod);
        if (WARNED.putIfAbsent("node:" + key, Boolean.TRUE) == null)
          @PKG@.MenuUtil.warn("setting " + key + ": " + old[0] + " registered it for every player, " + mod + " with the node " + perm + " - only holders of " + perm + " see and change it");
        return true;
      }
      refuse(key, def, mod + " wants the node " + perm + ", " + om + " registered the node " + op);
      return false;
    }
    if (old != null && op != null) {
      if (perm == null) {
        perm = op;
        if (WARNED.putIfAbsent("node:" + key, Boolean.TRUE) == null)
          @PKG@.MenuUtil.warn("setting " + key + ": " + mod + " registers it again without a node - keeping the node " + op + " (from " + om + ")");
      } else if (!perm.equals(op) && !mod.equals(om)) {
        refuse(key, def, mod + " wants the node " + perm + ", " + om + " registered the node " + op);
        return false;
      }
    }
    DEFS.put(key, new Object[] { mod, key, label, cat, def, help, perm });
    if (perm == null) PERM_MOD.remove(key);
    else if (!perm.equals(op)) PERM_MOD.put(key, mod);
    return true;
  } catch (Throwable t) { return false; }
}""")
M(sreg, r"""
public static void drain() {
  try {
    java.util.Map br = @PKG@.MenuUtil.bridge();
    java.util.Iterator it = new java.util.ArrayList(br.keySet()).iterator();
    while (it.hasNext()) {
      Object k = it.next();
      if (!(k instanceof String) || !((String) k).startsWith("settings:def:")) continue;
      Object v = br.get(k);
      if (v != null) register(v);
    }
  } catch (Throwable t) { @PKG@.MenuUtil.warn("settings drain failed: " + t); }
}""")
# 0.3.19 F: the Settings page's per-open drain reads the index (MenuIdx) instead of scanning the whole bridge; setup keeps drain()
M(sreg, r"""
public static void drainIdx() {
  try {
    String[] ks = @PKG@.MenuIdx.settingsKeys();
    java.util.Map br = @PKG@.MenuUtil.bridge();
    for (int i = 0; i < ks.length; i++) {
      Object v = br.get(ks[i]);
      if (v != null) register(v);
    }
  } catch (Throwable t) { @PKG@.MenuUtil.warn("settings drain failed: " + t); }
}""")
M(sreg, r"""
public static Object[] info(String key) {
  if (key == null) return null;
  Object[] d = (Object[]) DEFS.get(key);
  if (d == null && !REFUSED.containsKey(key)) {
    Object v = @PKG@.MenuUtil.bridge().get("settings:def:" + key);
    if (v != null && register(v)) d = (Object[]) DEFS.get(key);
  }
  return d;
}""")
# 0.3.3: may the player change (and so see) this switch? No node = yes. The node check = PermissionsModule.get().hasPermission(uuid, node),
# exactly what PlayerRef.hasPermission(node) runs (the check MenuUtil.isAdmin uses for Server Setup). Fail closed (no module, an error,
# no player = hidden). Never called under a SetReg / SetStore lock: info() returns before the engine is asked.
# review fix: refusedDef = the default a REFUSED key answers (null = not refused). A key nobody drained yet is looked up first (info():
# its settings:def: registration is registered - or refused - now), so the first call already fails closed.
M(sreg, r"""
public static Boolean refusedDef(String key) {
  if (key == null) return null;
  Object r = REFUSED.get(key);
  if (r == null && DEFS.get(key) == null) {
    info(key);
    r = REFUSED.get(key);
  }
  return r instanceof Boolean ? (Boolean) r : null;
}""")
M(sreg, r"""
public static String permOf(String key) {
  Object[] d = info(key);
  if (d == null || d.length < 7 || !(d[6] instanceof String)) return null;
  return (String) d[6];
}""")
M(sreg, r"""
public static boolean allowed(java.util.UUID u, String perm) {
  if (perm == null) return true;
  if (u == null) return false;
  try {
    @PERM@ pm = @PERM@.get();
    return pm != null && pm.hasPermission(u, perm);
  } catch (Throwable t) { return false; }
}""")
M(sreg, r"""
public static boolean may(java.util.UUID u, String key) {
  if (refusedDef(key) != null) return false;
  return allowed(u, permOf(key));
}""")
M(sreg, r"""
public static Boolean def(String key) {
  Object a = ADMIN.get(key);
  if (a instanceof Boolean) return (Boolean) a;
  Object[] d = info(key);
  return d == null ? null : (Boolean) d[4];
}""")
M(sreg, r"""
public static int rank(String key) {
  for (int i = 0; i < @PKG@.MenuData.SET_ORDER.length; i++) if (@PKG@.MenuData.SET_ORDER[i].equals(key)) return i;
  for (int j = 0; j < @PKG@.MenuData.SET_ORDER_MSG.length; j++) if (@PKG@.MenuData.SET_ORDER_MSG[j].equals(key)) return @PKG@.MenuData.SET_ORDER.length + j;
  return 9000;
}""")
M(sreg, r"""
public static String[] keysOf(int cat) {
  if (cat < 0 || cat >= @PKG@.MenuData.SET_CAT_ID.length) return new String[0];
  String id = @PKG@.MenuData.SET_CAT_ID[cat];
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.Iterator it = DEFS.values().iterator();
  while (it.hasNext()) {
    Object[] d = (Object[]) it.next();
    if (id.equals(d[3])) rows.add(String.valueOf(10000 + rank((String) d[1])) + "\t" + (String) d[1]);
  }
  java.util.Collections.sort(rows);
  String[] out = new String[rows.size()];
  for (int i = 0; i < out.length; i++) { String s = (String) rows.get(i); out[i] = s.substring(s.indexOf('\t') + 1); }
  return out;
}""")
# 0.3.3: the rows of a tab this player may change (= sees), in SET_ORDER; the Settings page pages and counts only these
M(sreg, r"""
public static String[] visible(int cat, java.util.UUID u) {
  String[] all = keysOf(cat);
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < all.length; i++) if (may(u, all[i])) out.add(all[i]);
  return (String[]) out.toArray(new String[0]);
}""")
# 0.3: ADMIN is replaced wholesale under ONE lock by both writers: the file re-read (adminSwap, refused for 5 s after an in-game edit so
# it can never read the file between that edit and the kit's save 500 ms later) and Server Setup (adminPut, copy-on-write, at once)
M(sreg, r"""
public static synchronized boolean adminSwap(java.util.HashMap nx, boolean first) {
  if (!first && System.currentTimeMillis() - EDIT_AT < 5000L) return false;
  ADMIN = nx;
  return true;
}""")
M(sreg, r"""
public static synchronized void adminPut(String key, Boolean v) {
  java.util.HashMap nx = new java.util.HashMap(ADMIN);
  if (v == null) nx.remove(key); else nx.put(key, v);
  ADMIN = nx;
  EDIT_AT = System.currentTimeMillis();
}""")
# settings-defaults.properties: written as a commented template when missing (first = setup), re-read when lastModified changes
# (SeenTick, every 30 s). Only setup and the single scheduler thread call it, so it needs no lock; ADMIN is replaced wholesale.
M(sreg, r"""
public static void loadAdmin(boolean first) {
  java.nio.file.Path f = ADMIN_FILE;
  if (f == null) return;
  long mt = -1L;
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      if (first) {
        try {
          @PKG@.MenuUtil.atomicWrite(f, @PKG@.MenuData.SET_TEMPLATE.getBytes("UTF-8"));
          @PKG@.MenuUtil.info("wrote settings-defaults.properties (server-wide defaults for /settings, every line commented out)");
        } catch (Throwable tw) { @PKG@.MenuUtil.warn("could not write the settings-defaults.properties template: " + tw); }
      }
      if (ADMIN.size() > 0) { ADMIN = new java.util.HashMap(); @PKG@.MenuUtil.info("settings-defaults.properties is gone - the mods' own defaults apply"); }
      ADMIN_MTIME = -1L;
      return;
    }
    mt = java.nio.file.Files.getLastModifiedTime(f, new java.nio.file.LinkOption[0]).toMillis();
    if (!first && mt == ADMIN_MTIME) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(new java.io.InputStreamReader(in, "UTF-8")); } finally { in.close(); }
    java.util.HashMap nx = new java.util.HashMap();
    int bad = 0;
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String v = p.getProperty(k, "").trim();
      if (!validKey(k)) { bad++; @PKG@.MenuUtil.warn("settings-defaults.properties: '" + k + "' is not a setting key - line ignored"); continue; }
      if (v.equalsIgnoreCase("true")) nx.put(k, Boolean.TRUE);
      else if (v.equalsIgnoreCase("false")) nx.put(k, Boolean.FALSE);
      else { bad++; @PKG@.MenuUtil.warn("settings-defaults.properties: " + k + "=" + v + " is not true or false - line ignored"); }
    }
    if (!adminSwap(nx, first)) return;
    ADMIN_MTIME = mt;
    @PKG@.MenuUtil.info("settings defaults: " + nx.size() + " server-wide default(s) in use" + (bad > 0 ? ", " + bad + " bad line(s) ignored" : ""));
  } catch (Throwable t) {
    if (mt != -1L) ADMIN_MTIME = mt;
    @PKG@.MenuUtil.warn("settings-defaults.properties cannot be read (" + t + ") - the previous defaults stay until the file changes");
  }
}""")
# SkyyMenu's own switches (menu.tooltips), registered exactly like an adopter does it (def key + register)
M(sreg, r"""
public static void registerOwn() {
  for (int i = 0; i < @PKG@.MenuData.OWN_KEY.length; i++) {
    Object[] a = new Object[] { "SkyyMenu", @PKG@.MenuData.OWN_KEY[i], @PKG@.MenuData.OWN_LABEL[i], @PKG@.MenuData.OWN_CAT[i],
                                Boolean.valueOf(@PKG@.MenuData.OWN_DEF[i]), @PKG@.MenuData.OWN_HELP[i] };
    try { @PKG@.MenuUtil.bridge().put("settings:def:" + @PKG@.MenuData.OWN_KEY[i], a); } catch (Throwable t) { }
    register(a);
  }
}""")

# ---- SetStore: per-PLAYER values, <world>/mods/Skyy_SkyyMenu/settings/<uuid>.properties. VALS maps are copy-on-write (never changed
# after they are published), so readers need no lock. BROKEN = unreadable files (never overwritten; read again after 30 s).
# LOCKS (build review): SetStore.class guards memory only (setMem / resetMem / pruneOffline). A player's file read (readLocked) and write
# (writeLocked: fsync + retries) run under lockOf(k), one of 64 ReentrantLock stripes by uuid hash - never under SetStore.class, so a
# world-thread click or settings:fn:set never waits for another player's disk write. A stripe holder takes no other lock and calls no
# other mod. Lock order: SetStore.class -> stripe only via tryLock (pruneOffline), so there is no cycle.
F(sst, "public static java.nio.file.Path DIR;")
F(sst, "public static final java.util.concurrent.ConcurrentHashMap VALS = new java.util.concurrent.ConcurrentHashMap();")
F(sst, "public static final java.util.concurrent.ConcurrentHashMap BROKEN = new java.util.concurrent.ConcurrentHashMap();")
F(sst, "public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();")
F(sst, "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();")
F(sst, "public static final java.util.concurrent.ConcurrentHashMap LOCKS = new java.util.concurrent.ConcurrentHashMap();")
M(sst, r"""
public static java.util.UUID uuidOf(Object o) {
  if (o instanceof java.util.UUID) return (java.util.UUID) o;
  if (o instanceof String) { try { return java.util.UUID.fromString((String) o); } catch (Throwable t) { return null; } }
  return null;
}""")
M(sst, r"""
public static java.nio.file.Path fileOf(String k) {
  return DIR.resolve(k + ".properties");
}""")
# the lock stripe of one player's file (64 stripes, created on first use, never removed - bounded, no per-player leak)
M(sst, r"""
public static java.util.concurrent.locks.ReentrantLock lockOf(String k) {
  Integer i = Integer.valueOf(k.hashCode() & 63);
  Object l = LOCKS.get(i);
  if (l == null) {
    LOCKS.putIfAbsent(i, new java.util.concurrent.locks.ReentrantLock());
    l = LOCKS.get(i);
  }
  return (java.util.concurrent.locks.ReentrantLock) l;
}""")
# the file read - the caller holds lockOf(k). Only this method creates a VALS entry (setMem / resetMem need an existing one), and two
# reads of one player are serialized by the stripe, so the second one returns the first one's map.
M(sst, r"""
public static java.util.HashMap readLocked(String k) {
  Object m = VALS.get(k);
  if (m != null) return (java.util.HashMap) m;
  long now = System.currentTimeMillis();
  Long bad = (Long) BROKEN.get(k);
  if (bad != null && now - bad.longValue() < 30000L) return null;
  java.util.HashMap out = new java.util.HashMap();
  try {
    java.nio.file.Path f = fileOf(k);
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(new java.io.InputStreamReader(in, "UTF-8")); } finally { in.close(); }
      java.util.Iterator it = p.stringPropertyNames().iterator();
      while (it.hasNext()) {
        String key = (String) it.next();
        if (key.startsWith("_") || !@PKG@.SetReg.validKey(key)) continue;
        String v = p.getProperty(key, "").trim();
        if (v.equalsIgnoreCase("true")) out.put(key, Boolean.TRUE);
        else if (v.equalsIgnoreCase("false")) out.put(key, Boolean.FALSE);
      }
    }
  } catch (Throwable t) {
    if (bad == null) @PKG@.MenuUtil.warn("settings/" + k + ".properties cannot be read (" + t + ") - defaults are used and the file is NOT overwritten; read again every 30 s");
    BROKEN.put(k, Long.valueOf(now));
    return null;
  }
  BROKEN.remove(k);
  Object prev = VALS.putIfAbsent(k, out);
  return prev != null ? (java.util.HashMap) prev : out;
}""")
# lock-free when the map is loaded (the normal case after the join preload); otherwise one small file read under the player's stripe
M(sst, r"""
public static java.util.HashMap load(String k) {
  Object m = VALS.get(k);
  if (m != null) return (java.util.HashMap) m;
  if (DIR == null) return null;
  java.util.concurrent.locks.ReentrantLock lk = lockOf(k);
  java.util.HashMap out = null;
  lk.lock();
  try { out = readLocked(k); } finally { lk.unlock(); }
  return out;
}""")
M(sst, r"""
public static boolean isBroken(java.util.UUID u) {
  return u != null && BROKEN.containsKey(u.toString());
}""")
# the player's OWN choice only (null = never chose / file unreadable) - Tips needs it to tell "chose ON" from "default"
M(sst, r"""
public static Boolean own(java.util.UUID u, String key) {
  if (u == null || key == null) return null;
  String k = u.toString();
  Object m = VALS.get(k);
  java.util.HashMap vals = m != null ? (java.util.HashMap) m : load(k);
  if (vals == null) return null;
  Object v = vals.get(key);
  return v instanceof Boolean ? (Boolean) v : null;
}""")
M(sst, r"""
public static Boolean get(java.util.UUID u, String key) {
  if (u == null || key == null) return null;
  Boolean rd = @PKG@.SetReg.refusedDef(key);
  if (rd != null) return rd;
  Boolean o = own(u, key);
  if (o != null) return o;
  return @PKG@.SetReg.def(key);
}""")
# the file write - the caller holds lockOf(k). DIRTY is cleared BEFORE the snapshot, so a change published after it marks DIRTY again
# and schedules its own save; the snapshot map is never changed after publication (copy-on-write), so it is serialized without a lock.
M(sst, r"""
public static void writeLocked(String k) {
  DIRTY.remove(k);
  Object m = VALS.get(k);
  if (m == null || DIR == null || BROKEN.containsKey(k)) return;
  java.util.HashMap vals = (java.util.HashMap) m;
  java.util.ArrayList keys = new java.util.ArrayList(vals.keySet());
  java.util.Collections.sort(keys);
  StringBuilder sb = new StringBuilder();
  sb.append("# SkyyMenu settings of one player (uuid ").append(k).append("). Only the switches this player changed are listed - everything else uses the default.\n");
  sb.append("# Change them in game with /settings. Hand edits while the player is online are overwritten.\n");
  sb.append("_v=1\n");
  Object nm = NAMES.get(k);
  sb.append("_name=").append(@PKG@.MenuUtil.cleanName(nm == null ? "" : String.valueOf(nm))).append('\n');
  for (int i = 0; i < keys.size(); i++) {
    String key = (String) keys.get(i);
    Object v = vals.get(key);
    if (!(v instanceof Boolean)) continue;
    sb.append(key).append('=').append(((Boolean) v).booleanValue() ? "true" : "false").append('\n');
  }
  try { @PKG@.MenuUtil.atomicWrite(fileOf(k), sb.toString().getBytes("UTF-8")); }
  catch (Throwable t) {
    @PKG@.MenuUtil.warn("could not save settings/" + k + ".properties (kept in memory, retried every 30 s and at shutdown): " + t);
    DIRTY.put(k, Boolean.TRUE);
  }
}""")
M(sst, r"""
public static void saveNow(String k) {
  java.util.concurrent.locks.ReentrantLock lk = lockOf(k);
  lk.lock();
  try { writeLocked(k); } finally { lk.unlock(); }
}""")
# ================= 0.3.25 SoundSw: the player switch menu.sounds on the shared bridge (the sound rounds' contract) =================
# settings:sounds:<uuid> = java.lang.Boolean: TRUE = on, FALSE = muted; ABSENT = on (a player SkyyMenu has not seen, or one who left).
# The value = SetStore.get (own choice, else the server default, else ON). Published at join (SetLoadTask / MenuReady), on every change
# (SetStore.set / resetAll - the page, settings:fn:set), every 30 s for the online players (SeenTick: a changed server default) and
# removed when a player leaves (MenuQuit, SeenTick) and at shutdown. PUB = the uuids this mod published (so it removes only its own keys).
F(ssw, "public static final java.util.concurrent.ConcurrentHashMap PUB = new java.util.concurrent.ConcurrentHashMap();")
M(ssw, r"""
public static String key(java.util.UUID u) {
  return @PKG@.MenuData.SOUNDS_BRIDGE + u.toString();
}""")
M(ssw, r"""
public static boolean on(java.util.UUID u) {
  Boolean v = @PKG@.SetStore.get(u, @PKG@.MenuData.SOUNDS_KEY);
  return v == null || v.booleanValue();
}""")
# Fix round 2: pub runs on SkyyMenu-IO (sweep, SetLoadTask) AND the world thread (SetStore.set from the page / settings:fn:set). A sweep
# that read ON just before the player clicked OFF could put its stale TRUE after the click's FALSE. Lock-free fix (no lock: on() may read
# the player's file on the IO thread, and the world thread must never wait on that): after every put, read again and put again if the
# value changed meanwhile - whichever thread puts last has read the value AFTER its own previous put, so the last put is the current one.
M(ssw, r"""
public static void pub(java.util.UUID u) {
  if (u == null) return;
  try {
    boolean b = on(u);
    for (int i = 0; i < 4; i++) {
      Boolean v = b ? Boolean.TRUE : Boolean.FALSE;
      PUB.put(u, v);
      @PKG@.MenuUtil.bridge().put(key(u), v);
      boolean again = on(u);
      if (again == b) return;
      b = again;
    }
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not publish the sound switch of " + u + ": " + t); }
}""")
# MenuReady (world thread): publish only when the player's settings are already in memory (no disk read here); else SetLoadTask does
M(ssw, r"""
public static void ready(java.util.UUID u) {
  if (u != null && @PKG@.SetStore.VALS.containsKey(u.toString())) pub(u);
}""")
M(ssw, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  PUB.remove(u);
  try { @PKG@.MenuUtil.bridge().remove(key(u)); } catch (Throwable t) { }
}""")
# SeenTick (SkyyMenu-IO, every 30 s): drop the players who left, refresh the online ones. Fix round: SeenTick's own snapshot is
# taken BEFORE its disk work (retryDirty, flushes, loadAdmin), so a player who joined meanwhile (and was published by ready()) would
# be forgotten = un-muted for up to 30 s. sweep therefore takes a FRESH player list (live) right before it forgets anyone; only when
# that list cannot be read does it fall back to SeenTick's snapshot. sweepWith(snapshot, fresh) is the testable core.
M(ssw, r"""
public static java.util.HashSet live() {
  java.util.HashSet h = new java.util.HashSet();
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr != null && pr.isValid()) h.add(pr.getUuid());
    }
  } catch (Throwable t) { return null; }
  return h;
}""")
M(ssw, r"""
public static void sweepWith(java.util.Set online, java.util.Set fresh) {
  java.util.Set base = fresh != null ? fresh : online;
  if (base == null) return;
  java.util.ArrayList ks = new java.util.ArrayList(PUB.keySet());
  for (int i = 0; i < ks.size(); i++) {
    Object o = ks.get(i);
    if (!base.contains(o)) forget((java.util.UUID) o);
  }
  java.util.Iterator it = base.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (o instanceof java.util.UUID) pub((java.util.UUID) o);
  }
}""")
M(ssw, r"""
public static void sweep(java.util.Set online) {
  sweepWith(online, live());
}""")
M(ssw, r"""
public static void clearAll() {
  java.util.ArrayList ks = new java.util.ArrayList(PUB.keySet());
  for (int i = 0; i < ks.size(); i++) forget((java.util.UUID) ks.get(i));
}""")

# ---- SetSaveTask: the 500 ms delayed save (saveNow writes the NEWEST map, so several quick clicks give one write)
ssv.addInterface(pool.get("java.lang.Runnable"))
F(ssv, "public String k;")
C(ssv, "public SetSaveTask(String k) { this.k = k; }")
M(ssv, r"""
public void run() {
  try { @PKG@.SetStore.saveNow(this.k); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings save failed: " + t); }
}""")
# ---- SetStore (cont.)
# schedules the save; the caller has already marked DIRTY (setMem / resetMem). Called OUTSIDE SetStore.class. The inline fallback only
# runs when the executor refuses the task (the server is shutting down).
# 0.3.19 B: on SkyyMenu-IO (0.3.18: HytaleServer.SCHEDULED_EXECUTOR); inline only when MenuIO cannot take it (stopped)
M(sst, r"""
public static void saveSoon(String k) {
  if (!@PKG@.MenuIO.schedule(new @PKG@.SetSaveTask(k), 500L)) saveNow(k);
}""")
# memory only, under SetStore.class: 1 = the state already matches (onlyIfUnset and the player chose) or a save is already on its way,
# 2 = changed and newly DIRTY (the caller schedules the save after leaving the lock), 3 = the map is not loaded (the caller loads it
# outside this lock and tries again). The new map and its DIRTY mark are published in this one locked step (pruneOffline holds the same lock).
M(sst, r"""
public static synchronized int setMem(String k, String key, boolean val, boolean onlyIfUnset) {
  Object m = VALS.get(k);
  if (m == null) return 3;
  java.util.HashMap cur = (java.util.HashMap) m;
  if (onlyIfUnset && cur.containsKey(key)) return 1;
  java.util.HashMap nx = new java.util.HashMap(cur);
  nx.put(key, Boolean.valueOf(val));
  VALS.put(k, nx);
  return DIRTY.putIfAbsent(k, Boolean.TRUE) == null ? 2 : 1;
}""")
# 1 = the stored state matches the request (written, or skipped because onlyIfUnset and the player already chose), 0 = not saved
M(sst, r"""
public static int set(java.util.UUID u, String key, boolean val, boolean onlyIfUnset) {
  if (u == null || !@PKG@.SetReg.validKey(key)) return 0;
  String k = u.toString();
  for (int i = 0; i < 3; i++) {
    if (load(k) == null) return 0;
    int r = setMem(k, key, val, onlyIfUnset);
    if (r == 2) { saveSoon(k); if (@PKG@.MenuData.SOUNDS_KEY.equals(key)) @PKG@.SoundSw.pub(u); return 1; }   // 0.3.25
    if (r != 3) { if (r == 1 && @PKG@.MenuData.SOUNDS_KEY.equals(key)) @PKG@.SoundSw.pub(u); return r; }
  }
  return 0;
}""")
# 0.3.3: keep = the keys whose own choice stays (switches the player may not change - Reset all only resets rows they can change); the
# permission lookups run in resetAll BEFORE this lock, the kept values are taken from the map current under the lock
M(sst, r"""
public static synchronized int resetMem(String k, java.util.HashMap keep) {
  Object m = VALS.get(k);
  if (m == null) return 3;
  java.util.HashMap cur = (java.util.HashMap) m;
  java.util.HashMap nx = new java.util.HashMap();
  if (keep != null) {
    java.util.Iterator it = keep.keySet().iterator();
    while (it.hasNext()) {
      Object key = it.next();
      Object v = cur.get(key);
      if (v instanceof Boolean) nx.put(key, v);
    }
  }
  VALS.put(k, nx);
  return DIRTY.putIfAbsent(k, Boolean.TRUE) == null ? 2 : 1;
}""")
M(sst, r"""
public static int resetAll(java.util.UUID u) {
  if (u == null) return 0;
  String k = u.toString();
  for (int i = 0; i < 3; i++) {
    java.util.HashMap vals = load(k);
    if (vals == null) return 0;
    java.util.HashMap keep = new java.util.HashMap();
    java.util.Iterator it = vals.keySet().iterator();
    while (it.hasNext()) {
      Object key = it.next();
      if (key instanceof String && !@PKG@.SetReg.may(u, (String) key)) keep.put(key, Boolean.TRUE);
    }
    int r = resetMem(k, keep);
    if (r == 2) { saveSoon(k); @PKG@.SoundSw.pub(u); return 1; }   // 0.3.25
    if (r != 3) { if (r == 1) @PKG@.SoundSw.pub(u); return r; }
  }
  return 0;
}""")
M(sst, r"""
public static int retryDirty() {
  java.util.ArrayList ks = new java.util.ArrayList(DIRTY.keySet());
  for (int i = 0; i < ks.size(); i++) saveNow((String) ks.get(i));
  return ks.size();
}""")
# drop one offline player's cached map - only with the stripe got by tryLock (never while their file is being read or written; a busy
# stripe is simply tried again at the next SeenTick) and only when nothing is waiting to be saved
M(sst, r"""
public static void dropIfIdle(String k) {
  java.util.concurrent.locks.ReentrantLock lk = lockOf(k);
  if (!lk.tryLock()) return;
  try {
    if (!DIRTY.containsKey(k)) { VALS.remove(k); NAMES.remove(k); }
  } finally { lk.unlock(); }
}""")
# drop cached maps of players who left (not dirty ones), so a hand edit made while they are offline is read at their next join.
# SetStore.class keeps setMem / resetMem out while it checks DIRTY; it never blocks on a stripe (tryLock).
M(sst, r"""
public static synchronized void pruneOffline(java.util.Set online) {
  java.util.ArrayList ks = new java.util.ArrayList(VALS.keySet());
  for (int i = 0; i < ks.size(); i++) {
    String k = (String) ks.get(i);
    if (online.contains(k) || DIRTY.containsKey(k)) continue;
    dropIfIdle(k);
  }
  BROKEN.keySet().retainAll(online);
}""")
M(sst, r"""
public static void flushAll() {
  int n = retryDirty();
  if (n > 0) @PKG@.MenuUtil.info("settings: saved " + n + " changed player file(s) at shutdown");
}""")

# ================= Tips (0.1.3 book, 0.2 on the registry): the per-player "hover tooltips" switch = settings key menu.tooltips =================
# OFF renders the grid with InfoDisplay: None (the EyeSpy markup), so no tooltip can ever stick. 0.1.3 stored OFF as the file
# Skyy_SkyyMenu/notips/<uuid>.txt; migrate() moves it into the registry at the next join (SetLoadTask) and deletes the file only after
# the settings file is on disk. Until then an existing notips file still counts as OFF (legacyOff), so the switch never flips back on.
F(tip, "public static java.nio.file.Path DIR;")
F(tip, "public static final java.util.concurrent.ConcurrentHashMap LEGACY = new java.util.concurrent.ConcurrentHashMap();")
M(tip, r"""
public static boolean legacyOff(java.util.UUID u) {
  if (u == null) return false;
  Object v = LEGACY.get(u);
  if (v instanceof Boolean) return ((Boolean) v).booleanValue();
  boolean off = false;
  try { off = DIR != null && java.nio.file.Files.exists(DIR.resolve(u.toString() + ".txt"), new java.nio.file.LinkOption[0]); }
  catch (Throwable t) { off = false; }
  LEGACY.put(u, off ? Boolean.TRUE : Boolean.FALSE);
  return off;
}""")
M(tip, r"""
public static boolean isOff(java.util.UUID u) {
  if (u == null) return false;
  Boolean own = @PKG@.SetStore.own(u, @PKG@.MenuData.TIPS_KEY);
  if (own != null) return !own.booleanValue();
  if (legacyOff(u)) return true;
  Boolean v = @PKG@.SetStore.get(u, @PKG@.MenuData.TIPS_KEY);
  return v != null && !v.booleanValue();
}""")
# scheduler thread only (SetLoadTask): the one-shot move of a 0.1.3 notips file
M(tip, r"""
public static void migrate(java.util.UUID u) {
  if (u == null || DIR == null || !legacyOff(u)) return;
  String k = u.toString();
  if (@PKG@.SetStore.set(u, @PKG@.MenuData.TIPS_KEY, false, true) != 1) return;
  @PKG@.SetStore.saveNow(k);
  if (@PKG@.SetStore.DIRTY.containsKey(k) || @PKG@.SetStore.isBroken(u)) return;
  try {
    java.nio.file.Files.deleteIfExists(DIR.resolve(k + ".txt"));
    LEGACY.put(u, Boolean.FALSE);
    @PKG@.MenuUtil.info("moved the 0.1.3 Hover Tooltips switch of " + k + " to /settings (" + @PKG@.MenuData.TIPS_KEY + ", a choice already made there wins)");
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not remove notips/" + k + ".txt (the /settings value is saved; retried at the next join): " + t); }
}""")
# 0.3.29: Tips.setOff is gone (its only caller was the retired Hover Tooltips tile; Settings > General switches tooltips)

# ---- SetLoadTask: the preload (off the world thread) + the notips migration. PlayerReadyEvent fires on EVERY world switch, so preload()
# schedules the task only while there is work left: the player's map is not loaded yet (first ready of the session, or an unreadable
# file waiting for its 30 s re-read), or the 0.1.3 notips state is unknown / not moved yet (LEGACY null / TRUE). Otherwise nothing.
sld.addInterface(pool.get("java.lang.Runnable"))
F(sld, "public String k;")
F(sld, "public java.util.UUID u;")
C(sld, "public SetLoadTask(String k, java.util.UUID u) { this.k = k; this.u = u; }")
M(sld, r"""
public void run() {
  try {
    @PKG@.SetStore.load(this.k);
    @PKG@.SoundSw.pub(this.u);   // 0.3.25
    @PKG@.Tips.migrate(this.u);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("settings preload failed: " + t); }
}""")
M(sld, r"""
public static void preload(@PR@ pr) {
  try {
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    if (u == null) return;
    String k = u.toString();
    String n = pr.getUsername();
    if (n != null) @PKG@.SetStore.NAMES.put(k, n);
    if (@PKG@.SetStore.VALS.containsKey(k) && Boolean.FALSE.equals(@PKG@.Tips.LEGACY.get(u))) return;
    if (!@PKG@.MenuIO.schedule(new @PKG@.SetLoadTask(k, u), 0L)) @PKG@.MenuUtil.warn("could not schedule the settings preload (SkyyMenu-IO stopped)");
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule the settings preload: " + t); }
}""")

# ---- the three bridge Functions
sgf.addInterface(pool.get("java.util.function.Function"))
C(sgf, "public SetGetFn() { }")
M(sgf, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[1] instanceof String)) return null;
    java.util.UUID u = @PKG@.SetStore.uuidOf(a[0]);
    String key = (String) a[1];
    if (u == null || !@PKG@.SetReg.validKey(key)) return null;
    return @PKG@.SetStore.get(u, key);
  } catch (Throwable t) { return null; }
}""")
srf.addInterface(pool.get("java.util.function.Function"))
C(srf, "public SetRegFn() { }")
M(srf, r"""
public Object apply(Object o) {
  try { return @PKG@.SetReg.register(o) ? Boolean.TRUE : Boolean.FALSE; } catch (Throwable t) { return Boolean.FALSE; }
}""")
ssf.addInterface(pool.get("java.util.function.Function"))
C(ssf, "public SetSetFn() { }")
M(ssf, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) o;
    if (a.length < 3 || !(a[1] instanceof String) || !(a[2] instanceof Boolean)) return Boolean.FALSE;
    java.util.UUID u = @PKG@.SetStore.uuidOf(a[0]);
    String key = (String) a[1];
    if (u == null || !@PKG@.SetReg.validKey(key)) return Boolean.FALSE;
    if (!@PKG@.SetReg.may(u, key)) return Boolean.FALSE;      // 0.3.3: the player lacks the switch's permission node
    boolean only = a.length > 3 && Boolean.TRUE.equals(a[3]);
    return @PKG@.SetStore.set(u, key, ((Boolean) a[2]).booleanValue(), only) == 1 ? Boolean.TRUE : Boolean.FALSE;
  } catch (Throwable t) { return Boolean.FALSE; }
}""")


# ================= 0.3 SetDefCfg: kit hooks (custom: bindings) for Skyy_SkyyMenu/settings-defaults.properties =================
# settings.defaults = a custom table: EVERY known + registered player switch is an entry (also the ones without a line yet), value
# on / off / unset; menu.tooltipsDefault = the menu.tooltips line as an ON/OFF row. Memory changes at once (SetReg.adminPut); the kit
# writes the returned file line (true / false, or null = remove the line) 500 ms later, versions it and logs it.
M(sdc, r"""
public static String norm(String v) {
  if (v == null) return "unset";
  String s = v.trim().toLowerCase();
  if (s.equals("on") || s.equals("true") || s.equals("yes") || s.equals("1")) return "on";
  if (s.equals("off") || s.equals("false") || s.equals("no") || s.equals("0")) return "off";
  if (s.equals("unset") || s.equals("default") || s.equals("none") || s.length() == 0) return "unset";
  return null;
}""")
M(sdc, r"""
public static String entryOf(String key) {
  String p = "settings.defaults[";
  if (key == null || !key.startsWith(p) || !key.endsWith("]")) return null;
  return key.substring(p.length(), key.length() - 1);
}""")
M(sdc, r"""
public static String[] customKeys(String tableKey) {
  java.util.ArrayList ks = new java.util.ArrayList();
  java.util.HashSet seen = new java.util.HashSet();
  java.util.ArrayList all = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.MenuData.SET_ORDER.length; i++) all.add(@PKG@.MenuData.SET_ORDER[i]);
  all.addAll(new java.util.ArrayList(@PKG@.SetReg.DEFS.keySet()));
  all.addAll(new java.util.ArrayList(@PKG@.SetReg.ADMIN.keySet()));
  for (int i = 0; i < all.size(); i++) {
    Object o = all.get(i);
    if (!(o instanceof String)) continue;
    String k = (String) o;
    if (!@PKG@.SetReg.validKey(k) || !seen.add(k)) continue;
    ks.add(String.valueOf(10000 + @PKG@.SetReg.rank(k)) + "\t" + k);
  }
  java.util.Collections.sort(ks);
  String[] out = new String[ks.size()];
  for (int i = 0; i < out.length; i++) { String s = (String) ks.get(i); out[i] = s.substring(s.indexOf('\t') + 1); }
  return out;
}""")
M(sdc, r"""
public static String customGet(String key) {
  if ("menu.tooltipsDefault".equals(key)) {
    Object v = @PKG@.SetReg.ADMIN.get(@PKG@.MenuData.TIPS_KEY);
    if (v instanceof Boolean && !((Boolean) v).booleanValue()) return "false";
    return "true";
  }
  String e = entryOf(key);
  if (e == null || !@PKG@.SetReg.validKey(e)) return null;
  Object v = @PKG@.SetReg.ADMIN.get(e);
  if (v instanceof Boolean) return ((Boolean) v).booleanValue() ? "on" : "off";
  return "unset";
}""")
M(sdc, r"""
public static String check(String key, String value) {
  String e = entryOf(key);
  if (e == null) return null;
  if (!@PKG@.SetReg.validKey(e)) return "Not a settings key: " + e + ".";
  if (value == null) return null;
  if (norm(value) == null) return "Type on, off or unset.";
  return null;
}""")
M(sdc, r"""
public static Object[] customSet(String key, String value) {
  if ("menu.tooltipsDefault".equals(key)) {
    boolean on = !"false".equals(value);
    @PKG@.SetReg.adminPut(@PKG@.MenuData.TIPS_KEY, Boolean.valueOf(on));
    return new Object[] { "ok", on ? "true" : "false", null, new String[] { @PKG@.MenuData.TIPS_KEY, on ? "true" : "false" } };
  }
  String e = entryOf(key);
  if (e == null || !@PKG@.SetReg.validKey(e)) return new Object[] { "bad", null, "Not a settings key." };
  String n = norm(value);
  if (n == null) return new Object[] { "bad", null, "Type on, off or unset." };
  if (n.equals("unset")) {
    @PKG@.SetReg.adminPut(e, null);
    return new Object[] { "ok", "unset", null, new String[] { e, null } };
  }
  boolean on = n.equals("on");
  @PKG@.SetReg.adminPut(e, Boolean.valueOf(on));
  return new Object[] { "ok", n, null, new String[] { e, on ? "true" : "false" } };
}""")
M(sdc, r"""
public static String customRead(String key, java.util.Map vals) {
  if (!"menu.tooltipsDefault".equals(key) || vals == null) return null;
  Object v = vals.get(@PKG@.MenuData.TIPS_KEY);
  if (v != null && String.valueOf(v).trim().equalsIgnoreCase("false")) return "false";
  return "true";
}""")

# ================= 0.3.6 PageGuard: THE WORLD-JOIN PAGE GUARD (tools/menu_0_3_6_patch.py) =================
# World.addPlayer - the one way into a world (cross-world teleport, login, instances, a world's drain) - dispatches AddPlayerToWorldEvent
# while the player is in no world store (a teleport: on the OLD world's thread right after PlayerRef.removeFromStore), BEFORE
# onSetupPlayerJoining clears the page acknowledgements (and keeps PageManager.customPage) and long before the new world adds the player
# to its store. The client drops its page at the world change, so the page the server still has here is stale by construction. It is
# forgotten without a packet: at once when its onDismiss is the engine's empty one (no page code runs), else by StaleTask on the new
# world's thread with the player's real ref / store. EXEC = HytaleServer.SCHEDULED_EXECUTOR (set in setup(), the BankWatch.EXEC pattern;
# null = not set up: no timers, said once a minute). JOINS = world joins seen per player (MenuPage.changedWorld), dropped at disconnect.
guard.addInterface(pool.get("java.util.function.Consumer"))
F(guard, "public static volatile boolean STOP = false;")
F(guard, "public static volatile java.util.concurrent.ScheduledExecutorService EXEC;")
F(guard, "public static final java.util.concurrent.ConcurrentHashMap JOINS = new java.util.concurrent.ConcurrentHashMap();")
F(guard, "public static volatile long WARNED = 0L;")
F(guard, "public static volatile int FORGOT = 0;")
F(guard, "public static volatile int DEFERRED = 0;")
C(guard, "public PageGuard() { }")
M(guard, r"""
public static int joins(java.util.UUID u) {
  if (u == null) return 0;
  Object o = JOINS.get(u);
  return o instanceof Integer ? ((Integer) o).intValue() : 0;
}""")
M(guard, r"""
public static void bump(java.util.UUID u) {
  if (u == null) return;
  JOINS.put(u, Integer.valueOf(joins(u) + 1));
}""")
# true = the page's onDismiss is the engine's empty CustomUIPage.onDismiss (public in the engine, so a page can only override it public)
M(guard, r"""
public static boolean plainDismiss(Object page) {
  if (page == null) return false;
  try {
    java.lang.reflect.Method m = page.getClass().getMethod("onDismiss", new Class[] { @REF@.class, @ST@.class });
    return m.getDeclaringClass() == @PAGE@.class;
  } catch (Throwable t) { return false; }
}""")
M(guard, r"""
public static String who(@PR@ pr) {
  try {
    if (pr == null) return "?";
    String n = pr.getUsername();
    return n == null ? String.valueOf(pr.getUuid()) : n;
  } catch (Throwable t) { return "?"; }
}""")
M(guard, r"""
public static void warnOnce(String msg) {
  long now = System.currentTimeMillis();
  if (now - WARNED < 60000L) return;
  WARNED = now;
  @PKG@.MenuUtil.warn(msg);
}""")
# forget `page` on the server the way the client's Esc does: PageManager.handleEvent Dismiss = page.onDismiss(ref, st), then no current
# page - no packet, the acknowledgement counter untouched. Only while it is still the current page. true = it is gone now.
# 0.3.18: Hytale 0.7.0 renamed it handleLegacyCustomPageEvent (same body)
M(guard, r"""
public static boolean forget(@PGM@ pm, @REF@ ref, @ST@ st, @PAGE@ page) {
  if (pm == null || page == null || pm.getCustomPage() != page) return false;
  pm.handleLegacyCustomPageEvent(ref, st, new @CPE@(@CPT@.Dismiss, (String) null));
  return pm.getCustomPage() != page;
}""")

# ================= 0.3.6 StaleTask: a stale page with its OWN onDismiss, forgotten on the new world's thread =================
# Scheduler hop (PageGuard.EXEC, every STEP ms while the player is not in the new world's store yet) -> World.execute -> the check on
# that world's thread: still the same page -> PageGuard.forget with the player's real ref / store (what the engine would pass at the next
# page action there - without the +1). Ends when the page was closed or replaced meanwhile, the player left / went on to another world
# (that join has its own check), at shutdown (STOP) or after MAX tries (40 s: the engine waits up to 30 s for the client's chunks).
stale.addInterface(pool.get("java.lang.Runnable"))
F(stale, "public @PR@ pr;")
F(stale, "public @PAGE@ page;")
F(stale, "public @WLD@ target;")
F(stale, "public boolean onWorld;")
F(stale, "public int tries;")
F(stale, "public static final long STEP = 50L;")
F(stale, "public static final int MAX = 800;")
C(stale, r"""
public StaleTask(@PR@ pr, @PAGE@ page, @WLD@ target) {
  this.pr = pr;
  this.page = page;
  this.target = target;
  this.onWorld = false;
  this.tries = 0;
}""")
M(stale, r"""
public boolean later() {
  this.onWorld = false;
  this.tries = this.tries + 1;
  if (this.tries > MAX || @PKG@.PageGuard.STOP) return false;
  java.util.concurrent.ScheduledExecutorService ex = @PKG@.PageGuard.EXEC;
  if (ex == null) {
    @PKG@.PageGuard.warnOnce("no scheduler (SkyyMenu not set up) - a page with its own close code that was open across a world change is closed by the game later");
    return false;
  }
  ex.schedule(this, STEP, java.util.concurrent.TimeUnit.MILLISECONDS);
  return true;
}""")
M(stale, r"""
public static boolean start(@PR@ pr, @PAGE@ page, @WLD@ target) {
  if (pr == null || page == null || target == null) return false;
  return new @PKG@.StaleTask(pr, page, target).later();
}""")
M(stale, r"""
public void run() {
  try {
    if (@PKG@.PageGuard.STOP || this.pr == null || !this.pr.isValid()) return;
    java.util.UUID wu = this.pr.getWorldUuid();
    @UNI@ uni = @UNI@.get();
    @WLD@ now = (wu == null || uni == null) ? null : uni.getWorld(wu);
    if (now != this.target) return;
    if (!this.onWorld) {
      if (this.pr.getReference() == null) { later(); return; }
      this.onWorld = true;
      this.target.execute(this);
      return;
    }
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) { later(); return; }
    @ST@ st = r.getStore();
    if (st == null) { later(); return; }
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) { later(); return; }
    @PGM@ pm = p.getPageManager();
    if (pm == null || pm.getCustomPage() != this.page) return;
    if (@PKG@.PageGuard.forget(pm, r, st, this.page)) {
      @PKG@.PageGuard.FORGOT = @PKG@.PageGuard.FORGOT + 1;
      @PKG@.MenuUtil.info("forgot the page " + this.page.getClass().getName() + " of " + @PKG@.PageGuard.who(this.pr) + " in the new world (its own close code ran, no packet): no later page close or bench can leave the game waiting for an answer that never comes");
    }
  } catch (Throwable t) {
    @PKG@.PageGuard.warnOnce("the world-change page check failed for " + @PKG@.PageGuard.who(this.pr) + ": " + t);
  }
}""")
# the listener itself (after StaleTask: it starts one)
M(guard, r"""
public void accept(Object ev) {
  try {
    if (STOP || !(ev instanceof @ATW@)) return;
    @ATW@ e = (@ATW@) ev;
    @HLD@ h = e.getHolder();
    if (h == null) return;
    @PR@ pr = (@PR@) h.getComponent(@PR@.getComponentType());
    if (pr != null) bump(pr.getUuid());
    @PLA@ p = (@PLA@) h.getComponent(@PLA@.getComponentType());
    if (p == null) return;
    @PGM@ pm = p.getPageManager();
    if (pm == null) return;
    @PAGE@ cp = pm.getCustomPage();
    if (cp == null) return;
    String what = cp.getClass().getName();
    if (plainDismiss(cp)) {
      if (forget(pm, (@REF@) null, (@ST@) null, cp)) {
        FORGOT = FORGOT + 1;
        @PKG@.MenuUtil.info(who(pr) + " changed world with the page " + what + " still open on the server - forgot it there too (no packet; the game client closes every page at a world change), so no later page close or bench can leave the game waiting for an answer that never comes");
      }
      return;
    }
    if (@PKG@.StaleTask.start(pr, cp, e.getWorld())) {
      DEFERRED = DEFERRED + 1;
      @PKG@.MenuUtil.info(who(pr) + " changed world with the page " + what + " still open on the server - it has its own close code, so it is forgotten (no packet) as soon as " + who(pr) + " is in the new world");
    }
  } catch (Throwable t) {
    warnOnce("the world-change page check failed: " + t);
  }
}""")

# ================= 0.3.6 MenuWatch part 1: the menu page's safety net (BankWatch pattern; part 2 after MenuPage.watchTick) =========
# target == null: the scheduler-thread tick; target != null: the check on that world's thread (MenuPage.watchTick does every PageManager
# call). One check per second per open menu; it ends when the menu is closed or replaced, the player leaves, or at shutdown (STOP).
mwat.addInterface(pool.get("java.lang.Runnable"))
F(mwat, "public static final long PERIOD = 1000L;")
F(mwat, "public @PKG@.MenuPage page;")
F(mwat, "public @WLD@ target;")
C(mwat, r"""
public MenuWatch(@PKG@.MenuPage page, @WLD@ target) {
  this.page = page;
  this.target = target;
}""")
# 0.3.19 E: scheduleIn = schedule after ms (the backed-off delay of MenuPage.watchDelay); schedule = PERIOD as before
M(mwat, r"""
public static void scheduleIn(@PKG@.MenuPage page, long ms) {
  if (@PKG@.PageGuard.STOP || page == null) return;
  java.util.concurrent.ScheduledExecutorService ex = @PKG@.PageGuard.EXEC;
  try {
    if (ex == null) throw new java.lang.IllegalStateException("no scheduler (SkyyMenu not set up)");
    ex.schedule(new @PKG@.MenuWatch(page, (@WLD@) null), ms, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) {
    @PKG@.PageGuard.warnOnce("the menu page check could not be scheduled (" + t + ") - the menu still works, a click the game drops is just not healed");
  }
}""")
M(mwat, r"""
public static void schedule(@PKG@.MenuPage page) {
  if (@PKG@.PageGuard.STOP || page == null) return;
  java.util.concurrent.ScheduledExecutorService ex = @PKG@.PageGuard.EXEC;
  try {
    if (ex == null) throw new java.lang.IllegalStateException("no scheduler (SkyyMenu not set up)");
    ex.schedule(new @PKG@.MenuWatch(page, (@WLD@) null), PERIOD, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) {
    @PKG@.PageGuard.warnOnce("the menu page check could not be scheduled (" + t + ") - the menu still works, a click the game drops is just not healed");
  }
}""")

# ================= 0.3.10 StatsCalc: every number of the Stats page. Bridge reads only (java.lang types, tools/PROFILES-CONTRACT.md: the
# UUID keys always hold the ACTIVE profile), plus the player's EntityStatMap (vitals(): world thread, called from StatsPage.build). A stat
# whose mod is missing shows "-" and why; nothing here writes anything. Rows = String[] { name, total, source }: name + total + source
# + 2 <= ST_LINE_MAX (the source is clipped). Health / Mana / Stamina: the Skyy parts by key prefix, then ", base <the rest>" if it fits.
F(scl, "public static final int LINE_MAX = %d;" % ST_LINE_MAX)
F(scl, "public static final double JUMP_H0 = 2.1756;")      # tools/skyymove.py: default JumpForce 11.8 -> 11.8^2 / (2 x 32) blocks
F(scl, "public static final String[] GK = %s;" % jarr([g[0] for g in ST_GEAR]))
F(scl, "public static final String[] GL = %s;" % jarr([g[1] for g in ST_GEAR]))
F(scl, "public static final String[] GU = %s;" % jarr([g[3] for g in ST_GEAR]))
F(scl, "public static final String[] ELEM_K = %s;" % jarr([g[0] for g in ST_ELEM]))
F(scl, "public static final String[] ELEM_S = %s;" % jarr([g[1] for g in ST_ELEM]))
F(scl, "public static final String[] RAW_K = %s;" % jarr([g[0] for g in ST_RAW]))
F(scl, "public static final String[] RAW_S = %s;" % jarr([g[1] for g in ST_RAW]))
F(scl, "public static final String[] GROUPS = %s;" % jarr(ST_GROUPS))
F(scl, "public static final String[] FORT_N = %s;" % jarr([f[0] for f in ST_FORTUNE]))
F(scl, "public static final String[] FORT_K = %s;" % jarr([f[1] for f in ST_FORTUNE]))
F(scl, "public static final String[] WIS_N = %s;" % jarr([f[0] for f in ST_WISDOM]))
F(scl, "public static final String[] WIS_K = %s;" % jarr([f[1] for f in ST_WISDOM]))
F(scl, "public static final String[] CLASS_SKILLS = %s;" % jarr(CLASS_SKILLS + CLASS_SKILLS_OLD))   # 0.3.13: + the old Monk label
F(scl, "public static final String[] TABS = %s;" % jarr(ST_TABS))
F(scl, "public static final String[] NOTES = %s;" % jarr(ST_NOTES))
F(scl, "public static final String SUB = %s;" % jstr(ST_SUB))
F(scl, "public static final int ROWS = %d;" % ST_ROWS)
M(scl, r"""
public static java.util.Map br() { return @PKG@.MenuUtil.bridge(); }""")
M(scl, r"""
public static String num(double v) {
  if (Double.isNaN(v) || Double.isInfinite(v)) return "0";
  double x = v;
  if (x > 1.0E9) x = 1.0E9;
  if (x < -1.0E9) x = -1.0E9;
  long r = Math.round(x * 10.0);
  if (r % 10L == 0L) return @PKG@.MenuUtil.fmt(r / 10L);
  long a = r < 0L ? -r : r;
  return (r < 0L ? "-" : "") + String.valueOf(a / 10L) + "." + String.valueOf(a % 10L);
}""")
M(scl, r"""
public static String signed(double v) {
  return (Math.round(v * 10.0) > 0L ? "+" : "") + num(v);
}""")
M(scl, r"""
public static java.util.HashMap kv(Object o) {
  java.util.HashMap m = new java.util.HashMap();
  if (!(o instanceof String)) return m;
  String[] parts = ((String) o).split(",");
  for (int i = 0; i < parts.length; i++) {
    String p = parts[i].trim();
    int c = p.lastIndexOf(':');
    if (c <= 0 || c >= p.length() - 1) continue;
    String k = p.substring(0, c).trim();
    double v = Double.NaN;
    try { v = Double.parseDouble(p.substring(c + 1).trim()); } catch (Throwable t) { v = Double.NaN; }
    if (Double.isNaN(v) || Double.isInfinite(v)) continue;
    Object old = m.get(k);
    double nv = (old instanceof Double ? ((Double) old).doubleValue() : 0.0) + v;
    if (nv > 1.0E9) nv = 1.0E9;
    if (nv < -1.0E9) nv = -1.0E9;
    m.put(k, Double.valueOf(nv));
  }
  return m;
}""")
M(scl, r"""
public static double get(java.util.HashMap m, String k) {
  Object o = m == null ? null : m.get(k);
  return o instanceof Double ? ((Double) o).doubleValue() : 0.0;
}""")
# the skill string in its own order: [name, level] pairs
M(scl, r"""
public static java.util.ArrayList pairs(Object o) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (!(o instanceof String)) return out;
  String[] parts = ((String) o).split(",");
  for (int i = 0; i < parts.length; i++) {
    String p = parts[i].trim();
    int c = p.lastIndexOf(':');
    if (c <= 0 || c >= p.length() - 1) continue;
    int lv = -1;
    try { lv = Integer.parseInt(p.substring(c + 1).trim()); } catch (Throwable t) { lv = -1; }
    if (lv < 0) continue;
    out.add(new String[] { @PKG@.MenuUtil.safe(p.substring(0, c).trim()), String.valueOf(lv) });
  }
  return out;
}""")
M(scl, r"""
public static void add(java.util.ArrayList rows, String name, String value, String src) {
  String n = @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(name == null ? "" : name), 32);
  String v = @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(value == null ? "" : value), 24);
  int room = LINE_MAX - n.length() - v.length() - 2;
  if (room < 12) room = 12;
  rows.add(new String[] { n, v, @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(src == null ? "" : src), room) });
}""")
M(scl, r"""
public static void part(StringBuilder sb, String label, double v, String unit) {
  if (Math.abs(v) < 0.05) return;
  if (sb.length() > 0) sb.append(", ");
  sb.append(label).append(' ').append(signed(v)).append(unit);
}""")
M(scl, r"""
public static Object call(String key, Object arg) {
  try {
    Object f = br().get(key);
    if (f instanceof java.util.function.Function) return ((java.util.function.Function) f).apply(arg);
  } catch (Throwable t) { }
  return null;
}""")
# a value of another mod's Server Setup row (tools/CONFIG-CONTRACT.md op "get"; null = not a row / mod missing -> the default)
M(scl, r"""
public static String cfg(String mod, String key) {
  Object r = call("config:fn:" + mod, new Object[] { "get", key });
  return r instanceof String ? (String) r : null;
}""")
M(scl, r"""
public static double cfgNum(String mod, String key, double def) {
  String s = cfg(mod, key);
  if (s == null) return def;
  double d = def;
  try { d = Double.parseDouble(s.trim()); } catch (Throwable t) { d = def; }
  if (Double.isNaN(d) || Double.isInfinite(d)) return def;
  return d;
}""")
M(scl, r"""
public static boolean cfgOn(String mod, String key, boolean def) {
  String s = cfg(mod, key);
  if (s == null) return def;
  String t = s.trim().toLowerCase();
  if (t.equals("true")) return true;
  if (t.equals("false")) return false;
  return def;
}""")
# the summed skill-tree bonus of one key (skill:bonus:<uuid> = source -> Map{"dd.mining": 0.02, "xp.mining": 0.15, ...}) - the same sum
# SkyySkills' SkillBonus.sum makes
M(scl, r"""
public static double bonus(java.util.UUID u, String key) {
  double s = 0.0;
  try {
    Object o = br().get("skill:bonus:" + u.toString());
    if (!(o instanceof java.util.Map)) return 0.0;
    java.util.Iterator it = ((java.util.Map) o).values().iterator();
    while (it.hasNext()) {
      Object v = it.next();
      if (!(v instanceof java.util.Map)) continue;
      Object n = ((java.util.Map) v).get(key);
      if (!(n instanceof Number)) continue;
      double d = ((Number) n).doubleValue();
      if (Double.isNaN(d) || Double.isInfinite(d)) continue;
      s = s + d;
    }
  } catch (Throwable t) { return 0.0; }
  return s;
}""")
M(scl, r"""
public static String text(String key) {
  Object o = br().get(key);
  if (!(o instanceof String)) return null;
  String t = ((String) o).trim();
  return t.length() == 0 ? null : @PKG@.MenuUtil.safe(t);
}""")
# fix round: profile:class:<uuid> (SkyyProfiles) is AUTHORITATIVE (SkyyClasses 0.1.3+ / SkyySkills 0.3.2+ read it first); class:<uuid> +
# class:skill:<uuid> lag a profile switch by up to ~2 s (SkyyClasses' ClassTick). classSyncing = SkyyClasses is loaded (class:fn:get) and
# its class:<uuid> does not match the profile's class yet - then the class skill is stale and nothing class-skill based is shown.
M(scl, r"""
public static String className(java.util.UUID u) {
  String c = text("profile:class:" + u.toString());
  return c != null ? c : text("class:" + u.toString());
}""")
M(scl, r"""
public static boolean classSyncing(java.util.UUID u) {
  String pc = text("profile:class:" + u.toString());
  if (pc == null) return false;
  if (!(br().get("class:fn:get") instanceof java.util.function.Function)) return false;
  String c = text("class:" + u.toString());
  return c == null || !c.equalsIgnoreCase(pc);
}""")
M(scl, r"""
public static String classSkill(java.util.UUID u) { return classSyncing(u) ? null : text("class:skill:" + u.toString()); }""")
M(scl, r"""
public static String profileName(java.util.UUID u) {
  String p = text("profile:pname:" + u.toString());
  return p != null ? p : text("profile:name:" + u.toString());
}""")
M(scl, r"""
public static Object[] overallInfo(java.util.UUID u) {
  Object r = call("skill:fn:overall", u);
  if (r instanceof Object[] && ((Object[]) r).length >= 5 && ((Object[]) r)[0] instanceof Number) return (Object[]) r;
  return null;
}""")
M(scl, r"""
public static int overall(java.util.UUID u) {
  Object[] o = overallInfo(u);
  if (o != null) return ((Number) o[0]).intValue();
  Object v = br().get("skill:overall:" + u.toString());
  return v instanceof Number ? ((Number) v).intValue() : -1;
}""")
# "Mining 12, Foraging 8, Farming 5" - the n highest levels (ties: the skill string's order)
M(scl, r"""
public static String topSkills(java.util.UUID u, int n) {
  java.util.ArrayList ps = pairs(br().get("skill:" + u.toString()));
  if (ps.isEmpty()) return null;
  boolean[] used = new boolean[ps.size()];
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < n; k++) {
    int best = -1;
    int bl = -1;
    for (int i = 0; i < ps.size(); i++) {
      if (used[i]) continue;
      int lv = Integer.parseInt(((String[]) ps.get(i))[1]);
      if (lv > bl) { bl = lv; best = i; }
    }
    if (best < 0) break;
    used[best] = true;
    if (sb.length() > 0) sb.append(", ");
    sb.append(((String[]) ps.get(best))[0]).append(' ').append(bl);
  }
  return sb.toString();
}""")
M(scl, r"""
public static String header(java.util.UUID u, String player) {
  StringBuilder sb = new StringBuilder(@PKG@.MenuUtil.safe(player));
  String c = className(u);
  if (c != null) sb.append("  -  ").append(c);
  String p = profileName(u);
  if (p != null) sb.append("  -  profile ").append(p);
  int ov = overall(u);
  if (ov >= 0) sb.append("  -  Overall Level ").append(ov);
  return @PKG@.MenuUtil.clip(sb.toString(), LINE_MAX);
}""")
# ---- Health / Mana / Stamina: the max the player has right now, split by the MAX modifiers' key prefixes (every Skyy mod names its own)
M(scl, r"""
public static int group(String key) {
  if (key == null) return -1;
  if (key.startsWith("skyygear_")) return 0;
  if (key.startsWith("skyyacc_")) return 1;
  if (key.startsWith("skyyskill_overall")) return 2;
  if (key.startsWith("skyyskill_class")) return 3;
  if (key.startsWith("skyyskill_base")) return 4;
  if (key.startsWith("skyyskill_")) return 5;
  if (key.startsWith("skyytree_")) return 6;
  return -1;
}""")
M(scl, r"""
public static String[] vital(@ESV@ v) {
  if (v == null) return null;
  float max = v.getMax();
  double[] grp = new double[GROUPS.length];
  double known = 0.0;
  java.util.Map mods = v.getModifiers();
  if (mods != null) {
    java.util.Iterator it = mods.keySet().iterator();
    while (it.hasNext()) {
      Object k = it.next();
      Object mo = mods.get(k);
      if (!(mo instanceof @SMO@)) continue;
      @SMO@ sm = (@SMO@) mo;
      if (sm.getTarget() != @MTG@.MAX || sm.getCalculationType() != @CAL@.ADDITIVE) continue;
      int gi = group(String.valueOf(k));
      if (gi < 0) continue;
      double a = (double) sm.getAmount();
      if (Double.isNaN(a) || Double.isInfinite(a)) continue;
      grp[gi] = grp[gi] + a;
      known = known + a;
    }
  }
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < grp.length; i++) part(sb, GROUPS[i], grp[i], "");
  return new String[] { num((double) max), sb.toString(), num((double) max - known) };
}""")
M(scl, r"""
public static String[] vitalAt(@ESM@ m, int idx) {
  try {
    if (m == null || idx < 0) return null;
    return vital(m.get(idx));
  } catch (Throwable t) { return null; }
}""")
# world thread only (StatsPage.build): null = the stat map could not be read (the rows then say so)
M(scl, r"""
public static Object[] vitals(@ST@ st, @REF@ ref) {
  try {
    if (st == null || ref == null || !ref.isValid()) return null;
    @ESM@ m = (@ESM@) st.getComponent(ref, @ESM@.getComponentType());
    if (m == null) return null;
    return new Object[] { vitalAt(m, @DST@.getHealth()), vitalAt(m, @DST@.getMana()), vitalAt(m, @DST@.getStamina()) };
  } catch (Throwable t) { return null; }
}""")
M(scl, r"""
public static void vitalRow(java.util.ArrayList rows, String name, Object[] vit, int i) {
  String[] e = null;
  if (vit != null && i < vit.length && vit[i] instanceof String[]) e = (String[]) vit[i];
  if (e == null) { add(rows, name, "-", "not read - click Refresh"); return; }
  String src = e[1];
  String tail = (src.length() == 0 ? "Base " : ", base ") + e[2];
  if (src.length() + tail.length() <= LINE_MAX - name.length() - e[0].length() - 2) src = src + tail;
  add(rows, name, e[0], src);
}""")
# ---- gear + accessory stats (gear:stats:<uuid> = SkyyGear's active totals without the accessory part, gear:extra:<uuid> = that part)
M(scl, r"""
public static int gi(String key) {
  for (int i = 0; i < GK.length; i++) if (GK[i].equals(key)) return i;
  return -1;
}""")
M(scl, r"""
public static void gearRow(java.util.ArrayList rows, java.util.HashMap g, java.util.HashMap a, boolean gearOn, String key) {
  int k = gi(key);
  if (k < 0) return;
  double gv = get(g, key);
  double av = get(a, key);
  StringBuilder sb = new StringBuilder();
  part(sb, "Gear", gv, GU[k]);
  part(sb, "Accessories", av, GU[k]);
  if (sb.length() == 0) sb.append(gearOn ? "nothing from your gear or accessories" : "SkyyGear is not on this server");
  add(rows, GL[k], num(gv + av) + GU[k], sb.toString());
}""")
# 0.3.12: the skill Defense SkyySkills 0.4.25 publishes (skill:def:<uuid> = Double, Foraging + class balance Defense, the same units as gear
# Defense - SkyySkills sums both in SkyyGear's formula). Only a Double > 0 counts (NaN / infinite / any other type / missing = 0, the
# SkyySkills clamp 100000 kept); 0 = the row is exactly 0.3.11's gearRow. Fix round: with SkyyGear's part.stats "false" (config:fn:SkyyGear
# get, cfgOn - the same test SkyySkills' SkillDef.gearCfg makes) SkyySkills reduces hits by the skill Defense ALONE, so the row then counts
# only the skill Defense and says "gear stats off" (key absent: still exactly 0.3.11's row).
M(scl, r"""
public static double skillDef(java.util.UUID u) {
  try {
    Object o = u == null ? null : br().get("skill:def:" + u.toString());
    if (!(o instanceof Double)) return 0.0;
    double v = ((Double) o).doubleValue();
    if (Double.isNaN(v) || Double.isInfinite(v) || !(v > 0.0)) return 0.0;
    return v > 100000.0 ? 100000.0 : v;
  } catch (Throwable t) { return 0.0; }
}""")
M(scl, r"""
public static void defRow(java.util.ArrayList rows, java.util.UUID u, java.util.HashMap g, java.util.HashMap a, boolean gearOn) {
  double sv = skillDef(u);
  if (!(sv > 0.0)) { gearRow(rows, g, a, gearOn, "def"); return; }
  int k = gi("def");
  if (k < 0) return;
  boolean gs = cfgOn("SkyyGear", "part.stats", true);
  double gv = gs ? get(g, "def") : 0.0;
  double av = gs ? get(a, "def") : 0.0;
  StringBuilder sb = new StringBuilder();
  part(sb, "Gear", gv, GU[k]);
  part(sb, "Accessories", av, GU[k]);
  part(sb, "Skills", sv, GU[k]);
  if (!gs) sb.append(sb.length() == 0 ? "gear stats off" : ", gear stats off");
  if (sb.length() == 0) sb.append(gearOn ? "nothing from your gear or accessories" : "SkyyGear is not on this server");
  add(rows, GL[k], num(gv + av + sv) + GU[k], sb.toString());
}""")
M(scl, r"""
public static void groupRow(java.util.ArrayList rows, java.util.HashMap g, java.util.HashMap a, String[] keys, String[] shorts, String name, boolean always) {
  double t = 0.0;
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < keys.length; k++) {
    double v = get(g, keys[k]) + get(a, keys[k]);
    t = t + v;
    part(sb, shorts[k], v, "");
  }
  if (Math.abs(t) < 0.05 && !always) return;
  if (sb.length() == 0) sb.append("none - it comes from weapons");
  add(rows, name, num(t), sb.toString());
}""")
# ---- movement (tools/skyymove.py: flat sources add on the default, pct sources multiply on top; speed clamp 0.3-5, jump h0 + 20, fall 0-2)
M(scl, r"""
public static String moveName(String src) {
  String s = src == null ? "" : src;
  if (s.startsWith("gear")) return "Gear";
  if (s.startsWith("accessories")) return "Accessories";
  if (s.startsWith("skills.acrobatics")) return "Acrobatics";
  if (s.startsWith("skills")) return "Skills";
  if (s.startsWith("trees")) return "Skill trees";
  return @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(s), 20);
}""")
M(scl, r"""
public static String[] move(java.util.UUID u, String stat) {
  double flat = 0.0;
  double pct = 0.0;
  boolean jump = "jump".equals(stat);
  StringBuilder sb = new StringBuilder();
  try {
    Object o = br().get("move:" + u.toString());
    if (o instanceof java.util.Map) {
      java.util.Map mm = (java.util.Map) o;
      java.util.Iterator it = mm.keySet().iterator();
      while (it.hasNext()) {
        Object src = it.next();
        Object e = mm.get(src);
        if (!(e instanceof java.util.Map)) continue;
        Object n = ((java.util.Map) e).get(stat);
        if (!(n instanceof Number)) continue;
        double d = ((Number) n).doubleValue();
        if (Double.isNaN(d) || Double.isInfinite(d) || d == 0.0) continue;
        boolean isPct = "pct".equals(String.valueOf(((java.util.Map) e).get("layer")));
        if (isPct) pct = pct + d; else flat = flat + d;
        if (jump && !isPct) part(sb, moveName(String.valueOf(src)), d, " blocks");
        else part(sb, moveName(String.valueOf(src)), d * 100.0, "%");
      }
    }
  } catch (Throwable t) { }
  double total = 0.0;
  if (jump) {
    double j = (JUMP_H0 + flat) * (1.0 + pct);
    if (j < 0.0) j = 0.0;
    if (j > JUMP_H0 + 20.0) j = JUMP_H0 + 20.0;
    total = (j / JUMP_H0 - 1.0) * 100.0;
  } else {
    double f = (1.0 + flat) * (1.0 + pct);
    if ("speed".equals(stat)) {
      if (f < 0.3) f = 0.3;
      if (f > 5.0) f = 5.0;
    } else {
      if (f < 0.0) f = 0.0;
      if (f > 2.0) f = 2.0;
    }
    total = (f - 1.0) * 100.0;
  }
  if (sb.length() == 0) sb.append("no bonus right now");
  return new String[] { signed(total) + "%", sb.toString() };
}""")
M(scl, r"""
public static String sourceName(String src) {
  String s = src == null ? "" : src.trim();
  if (s.startsWith("tree")) return "Skill trees";
  if (s.startsWith("acc")) return "Accessories";
  if (s.startsWith("gear")) return "Gear";
  return @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(s), 20);
}""")
M(scl, r"""
public static String[] manaRegen(java.util.UUID u) {
  Object t = call("skill:fn:manaregen", new Object[] { "get", u });
  if (!(t instanceof Number)) return new String[] { "-", "needs SkyySkills" };
  double tot = ((Number) t).doubleValue();
  StringBuilder sb = new StringBuilder();
  Object s = call("skill:fn:manaregen", new Object[] { "sources", u });
  if (s instanceof String[]) {
    String[] a = (String[]) s;
    for (int i = 0; i < a.length; i++) {
      String x = a[i] == null ? "" : a[i];
      int eq = x.indexOf('=');
      if (x.length() == 0) continue;
      if (sb.length() > 0) sb.append(", ");
      if (eq > 0) sb.append(sourceName(x.substring(0, eq))).append(' ').append(x.substring(eq + 1).trim()).append('%');
      else sb.append(x);
    }
  }
  if (sb.length() == 0) sb.append("no bonus - skill tree nodes add Mana Regen");
  return new String[] { signed(tot) + "%", sb.toString() };
}""")
# 0.3.30: the Health Regen row (RESUME queue, Menu 0.3.30): SkyySkills 0.4.43's skill:fn:hpregen {"row", UUID} -> String[]{value, detail}
# ("3.5/s", "1.2/s in combat; ..."); without it "-" + what it needs
M(scl, r"""
public static String[] hpRegen(java.util.UUID u) {
  Object r = call("skill:fn:hpregen", new Object[] { "row", u });
  if ((r instanceof String[]) && ((String[]) r).length >= 2) {
    String[] a = (String[]) r;
    String v = a[0] == null ? "-" : @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(a[0]), 20);
    String d = a[1] == null ? "" : @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(a[1]), 70);
    return new String[] { v.length() == 0 ? "-" : v, d };
  }
  return new String[] { "-", "needs SkyySkills 0.4.43" };
}""")
# ---- gathering: Fortune = today's double-drop chance (SkyySkills Perks.chanceU: level x perk.<skill>.doubleDropPerLevel + the tree dd.<skill>,
# capped by perk.doubleDropMax); Wisdom = the tree xp.<skill> part
# fix round: perk.<skill>.doubleDropOnly (SkyySkills default foraging = _Trunk) leads the source: "logs only: " / "some blocks only: "
M(scl, r"""
public static void fortune(java.util.ArrayList rows, java.util.UUID u, java.util.HashMap sk, boolean skillsOn, int i) {
  String name = FORT_N[i] + " Fortune";
  if (!skillsOn) { add(rows, name, "-", "needs SkyySkills"); return; }
  String key = FORT_K[i];
  double lvl = get(sk, FORT_N[i]);
  double rate = cfgOn("SkyySkills", "perk.enabled", true) ? cfgNum("SkyySkills", "perk." + key + ".doubleDropPerLevel", 0.005) : 0.0;
  double tree = cfgOn("SkyySkills", "bridge.bonus.enabled", true) ? bonus(u, "dd." + key) : 0.0;
  double max = cfgNum("SkyySkills", "perk.doubleDropMax", 1.0);
  if (max > 1.0) max = 1.0;
  if (max < 0.0) max = 0.0;
  double perk = lvl * rate;
  double tot = perk + tree;
  if (tot > max) tot = max;
  if (tot < 0.0) tot = 0.0;
  StringBuilder sb = new StringBuilder();
  part(sb, FORT_N[i] + " level " + (int) lvl, perk * 100.0, "%");
  part(sb, "Skill trees", tree * 100.0, "%");
  if (perk + tree > max) sb.append(" (max ").append(num(max * 100.0)).append("%)");
  if (sb.length() == 0) sb.append("level up ").append(FORT_N[i]).append(" for double drops");
  else {
    String only = cfg("SkyySkills", "perk." + key + ".doubleDropOnly");
    if (only == null) only = "foraging".equals(key) ? "_Trunk" : "";
    only = only.trim();
    if (only.equalsIgnoreCase("_Trunk")) sb.insert(0, "logs only: ");
    else if (only.length() > 0) sb.insert(0, "some blocks only: ");
  }
  add(rows, name, num(tot * 100.0) + "%", sb.toString());
}""")
M(scl, r"""
public static void wisdom(java.util.ArrayList rows, java.util.UUID u, boolean skillsOn, int i) {
  String name = WIS_N[i] + " Wisdom";
  if (!skillsOn) { add(rows, name, "-", "needs SkyySkills"); return; }
  double w = cfgOn("SkyySkills", "bridge.bonus.enabled", true) ? bonus(u, "xp." + WIS_K[i]) : 0.0;
  StringBuilder sb = new StringBuilder();
  part(sb, "Skill trees", w * 100.0, "% XP");
  if (sb.length() == 0) sb.append("Wisdom nodes in the skill trees add XP");
  add(rows, name, signed(w * 100.0) + "%", sb.toString());
}""")
# 0.3.13: the class balance damage % SkyySkills 0.4.26 publishes (skill:dmg:<uuid> = Double PERCENT, the skill:def rules). Only a Double > 0
# counts (NaN / infinite / any other type / missing = 0; the SkyySkills clamp 100000 kept); below 0.05 (the part() floor) = the row is exactly 0.3.12's.
M(scl, r"""
public static double skillDmg(java.util.UUID u) {
  try {
    Object o = u == null ? null : br().get("skill:dmg:" + u.toString());
    if (!(o instanceof Double)) return 0.0;
    double v = ((Double) o).doubleValue();
    if (Double.isNaN(v) || Double.isInfinite(v) || !(v > 0.0)) return 0.0;
    return v > 100000.0 ? 100000.0 : v;
  } catch (Throwable t) { return 0.0; }
}""")
M(scl, r"""
public static void classDamage(java.util.ArrayList rows, java.util.UUID u, java.util.HashMap sk) {
  if (classSyncing(u)) { add(rows, "Class Weapon Damage", "-", "class syncing, Refresh in a moment"); return; }
  String cs = classSkill(u);
  if (cs == null) { add(rows, "Class Weapon Damage", "-", "no class on this profile yet"); return; }
  double lvl = get(sk, cs);
  double rate = cfgOn("SkyySkills", "perk.enabled", true) ? cfgNum("SkyySkills", "perk.combat.damagePerLevel", 0.002) : 0.0;
  double cb = skillDmg(u);
  if (!(cb >= 0.05)) {
    add(rows, "Class Weapon Damage", signed(lvl * rate * 100.0) + "%", cs + " level " + (int) lvl + ", with your class weapons");
    return;
  }
  double lp = lvl * rate * 100.0;
  StringBuilder sb = new StringBuilder();
  sb.append(cs).append(" level ").append((int) lvl);
  if (Math.abs(lp) >= 0.05) sb.append(' ').append(signed(lp)).append('%');
  part(sb, "Class balance", cb, "%");
  add(rows, "Class Weapon Damage", signed(lp + cb) + "%", sb.toString());
}""")
M(scl, r"""
public static boolean isClassSkill(String name) {
  for (int i = 0; i < CLASS_SKILLS.length; i++) if (CLASS_SKILLS[i].equals(name)) return true;
  return false;
}""")
# ---- the five tabs
M(scl, r"""
public static void mainTab(java.util.ArrayList rows, java.util.UUID u, Object[] vit) {
  java.util.HashMap g = kv(br().get("gear:stats:" + u.toString()));
  java.util.HashMap a = kv(br().get("gear:extra:" + u.toString()));
  boolean gearOn = br().get("gear:fn:stats") instanceof java.util.function.Function;
  vitalRow(rows, "Health", vit, 0);
  vitalRow(rows, "Mana", vit, 1);
  vitalRow(rows, "Stamina", vit, 2);
  defRow(rows, u, g, a, gearOn);   // 0.3.12: + the skill Defense (skill:def:<uuid>); without it = gearRow(.., "def")
  gearRow(rows, g, a, gearOn, "str");
  gearRow(rows, g, a, gearOn, "cc");
  gearRow(rows, g, a, gearOn, "cd");
  gearRow(rows, g, a, gearOn, "mp");
  String[] sp = move(u, "speed");
  add(rows, "Speed", sp[0], sp[1]);
  String[] jp = move(u, "jump");
  add(rows, "Jump Height", jp[0], jp[1]);
  String[] fd = move(u, "fallDamage");
  add(rows, "Fall Damage", fd[0], fd[1]);
  String[] mr = manaRegen(u);
  add(rows, "Mana Regen", mr[0], mr[1]);
  String[] hr = hpRegen(u);   // 0.3.30
  add(rows, "Health Regen", hr[0], hr[1]);
  gearRow(rows, g, a, gearOn, "stam");
}""")
M(scl, r"""
public static void combatTab(java.util.ArrayList rows, java.util.UUID u) {
  java.util.HashMap g = kv(br().get("gear:stats:" + u.toString()));
  java.util.HashMap a = kv(br().get("gear:extra:" + u.toString()));
  boolean gearOn = br().get("gear:fn:stats") instanceof java.util.function.Function;
  gearRow(rows, g, a, gearOn, "dmg");
  gearRow(rows, g, a, gearOn, "chg");
  gearRow(rows, g, a, gearOn, "tdmg");
  groupRow(rows, g, a, ELEM_K, ELEM_S, "Elemental Damage", true);
  groupRow(rows, g, a, RAW_K, RAW_S, "Raw Elemental Damage", false);
  gearRow(rows, g, a, gearOn, "lsteal");
  gearRow(rows, g, a, gearOn, "msteal");
  gearRow(rows, g, a, gearOn, "hpr");
  gearRow(rows, g, a, gearOn, "hprp");
  classDamage(rows, u, kv(br().get("skill:" + u.toString())));
}""")
M(scl, r"""
public static void gatheringTab(java.util.ArrayList rows, java.util.UUID u) {
  java.util.HashMap sk = kv(br().get("skill:" + u.toString()));
  boolean on = br().get("skill:fn:level") instanceof java.util.function.Function;
  for (int i = 0; i < FORT_N.length; i++) fortune(rows, u, sk, on, i);
  for (int i = 0; i < WIS_N.length; i++) wisdom(rows, u, on, i);
}""")
# fix round: the other class skills get one row each while the tab has room (ROWS), else they are packed into as few
# "Other class skills" rows as fit LINE_MAX (never one clipped "..." row - a player who tried every class has 6)
M(scl, r"""
public static void otherRows(java.util.ArrayList rows, String joined, int n) {
  String[] parts = joined.split(", ");
  if (rows.size() + parts.length <= ROWS) {
    for (int i = 0; i < parts.length; i++) {
      int sp = parts[i].lastIndexOf(' ');
      if (sp <= 0) continue;
      add(rows, parts[i].substring(0, sp), "Level " + parts[i].substring(sp + 1), "another class's weapon skill");
    }
    return;
  }
  String name = "Other class skills";
  String val = String.valueOf(n);
  int room = LINE_MAX - name.length() - val.length() - 2;
  StringBuilder line = new StringBuilder();
  boolean first = true;
  for (int i = 0; i < parts.length; i++) {
    if (line.length() > 0 && line.length() + 2 + parts[i].length() > room) {
      add(rows, name, first ? val : "", line.toString());
      first = false;
      line = new StringBuilder();
    }
    if (line.length() > 0) line.append(", ");
    line.append(parts[i]);
  }
  if (line.length() > 0) add(rows, name, first ? val : "", line.toString());
}""")
M(scl, r"""
public static void skillsTab(java.util.ArrayList rows, java.util.UUID u) {
  Object[] ov = overallInfo(u);
  int lv = overall(u);
  if (ov != null) {
    StringBuilder sb = new StringBuilder();
    if (ov[1] instanceof Number) sb.append("average ").append(num(((Number) ov[1]).intValue() / 10.0));
    if (ov[2] instanceof Number) sb.append(" over ").append(((Number) ov[2]).intValue()).append(" skills");
    double hp = ov[3] instanceof Number ? ((Number) ov[3]).doubleValue() : 0.0;
    double mn = ov[4] instanceof Number ? ((Number) ov[4]).doubleValue() : 0.0;
    if (Math.abs(hp) >= 0.05) sb.append(", ").append(signed(hp)).append(" Health");
    if (Math.abs(mn) >= 0.05) sb.append(", ").append(signed(mn)).append(" Mana");
    add(rows, "Overall Level", String.valueOf(lv), sb.toString());
  } else {
    add(rows, "Overall Level", lv >= 0 ? String.valueOf(lv) : "-", lv >= 0 ? "" : "needs SkyySkills");
  }
  java.util.ArrayList ps = pairs(br().get("skill:" + u.toString()));
  if (ps.isEmpty()) { add(rows, "Skills", "-", "no skill data yet - SkyySkills loads it when you play"); return; }
  String cs = classSkill(u);
  StringBuilder others = new StringBuilder();
  int nOther = 0;
  for (int i = 0; i < ps.size(); i++) {
    String[] p = (String[]) ps.get(i);
    if (isClassSkill(p[0])) {
      if (cs != null && cs.equals(p[0])) add(rows, p[0], "Level " + p[1], "your class weapon skill");
      else {
        if (others.length() > 0) others.append(", ");
        others.append(p[0]).append(' ').append(p[1]);
        nOther++;
      }
    } else add(rows, p[0], "Level " + p[1], "");
  }
  if (nOther > 0) otherRows(rows, others.toString(), nOther);
}""")
M(scl, r"""
public static void profileTab(java.util.ArrayList rows, java.util.UUID u) {
  String p = profileName(u);
  add(rows, "Profile", p == null ? "-" : p, "Change Profile opens your profile list");
  String c = className(u);
  String cs = classSkill(u);
  add(rows, "Class", c == null ? "none yet" : c, classSyncing(u) ? "class syncing, Refresh in a moment" : cs == null ? "" : cs + " is your class weapon skill");
  long pu = @PKG@.MenuUtil.purse(u);
  add(rows, "Purse", pu < 0L ? "-" : @PKG@.MenuUtil.fmt(pu), pu < 0L ? "SkyyCoins is not on this server" : "coins you carry");
  long bk = @PKG@.MenuUtil.bank(u);
  add(rows, "Bank", bk < 0L ? "-" : @PKG@.MenuUtil.fmt(bk), bk < 0L ? "open the Bank to load it" : "coins in the bank - safe when you die");
  java.util.Map b = br();
  add(rows, "Void Charms", String.valueOf(@PKG@.MenuUtil.csvCount(b.get("acc:has:" + u.toString()))),
      "bench accessories, and " + @PKG@.MenuUtil.csvCount(b.get("acc:tal:" + u.toString())) + " talismans");
  add(rows, "Collection Recipes", String.valueOf(@PKG@.MenuUtil.csvCount(b.get("coll:recipes:" + u.toString()))),
      "recipes your collections unlocked");
}""")
M(scl, r"""
public static java.util.ArrayList rows(java.util.UUID u, int tab, Object[] vit) {
  java.util.ArrayList rows = new java.util.ArrayList();
  try {
    if (tab == 0) mainTab(rows, u, vit);
    else if (tab == 1) combatTab(rows, u);
    else if (tab == 2) gatheringTab(rows, u);
    else if (tab == 3) skillsTab(rows, u);
    else profileTab(rows, u);
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("stats page rows failed: " + t);
    add(rows, "Error", "-", "could not read your stats - see the server log");
  }
  return rows;
}""")

# ================= PetTile (0.3.14): the Pets tile of the main menu =================
# Pets are per PROFILE and never transfer (Skyy 2026-10-10). SkyyPets 0.1+ keeps each profile's pets in <mods>/Skyy_SkyyPets/pets/<storage
# key>.properties (Properties text, v=1, active.1 / active.2 = pet ids, pet.<id>.kind / name / level / rarity); the storage key is
# profile:fn:key (Given.key). We only READ it (never write, never hold it open: NIO shares delete, SkyyPets' atomic replace works), on the
# menu's build, cached per key by (modified time, size). Result (String[10]): state ("ok" / "none" = no file / "bad" = unreadable, over
# 1 MB, no v=1 - SkyyPets refuses such a file too), pet slot kind / name / level / rarity, summon slot kind / name / level / rarity, owned.
F(pet, "public static volatile java.nio.file.Path DIR;")
F(pet, "public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();")
F(pet, "public static final String[] RARITY = %s;" % jarr(["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]))
F(pet, "public static volatile long READS = 0L;")
M(pet, r"""
public static String[] empty(String state) {
  String[] a = new String[10];
  for (int i = 0; i < a.length; i++) a[i] = "";
  a[0] = state;
  a[9] = "0";
  return a;
}""")
# = SkyyPets' PetKind.display ("VoidEye" -> "Void Eye", "_" -> space), made safe for the tooltip
M(pet, r"""
public static String display(String id) {
  if (id == null) return "";
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < id.length() && i < 40; i++) {
    char c = id.charAt(i);
    if (c == '_') { b.append(' '); continue; }
    if (i > 0 && Character.isUpperCase(c) && Character.isLowerCase(id.charAt(i - 1))) b.append(' ');
    b.append(c);
  }
  return @PKG@.MenuUtil.safe(b.toString()).trim();
}""")
# = SkyyPets' PetRec.lv (Long.parseLong of the trimmed text, else the default), clamped
M(pet, r"""
public static long num(java.util.Properties p, String k, long d, long lo, long hi) {
  long v = d;
  String s = p.getProperty(k);
  if (s != null) { try { v = Long.parseLong(s.trim()); } catch (Throwable t) { v = d; } }
  if (v < lo) v = lo;
  if (v > hi) v = hi;
  return v;
}""")
# one slot -> out[at] kind, out[at + 1] name (its own name if set, cut to 24 like SkyyPets' nameplate, else the kind's), [at + 2] level,
# [at + 3] rarity name. An id without a kind = an empty slot (SkyyPets' PetRec.active does the same).
M(pet, r"""
public static void fill(String[] out, int at, java.util.Properties p, String id0) {
  String id = id0 == null ? "" : id0.trim();
  if (id.length() == 0) return;
  String kind = p.getProperty("pet." + id + ".kind");
  if (kind == null || kind.trim().length() == 0) return;
  kind = kind.trim();
  String nm = p.getProperty("pet." + id + ".name");
  nm = nm == null ? "" : @PKG@.MenuUtil.safe(nm.trim()).trim();
  if (nm.length() > 24) nm = nm.substring(0, 24).trim();
  if (nm.length() == 0) nm = display(kind);
  out[at] = kind;
  out[at + 1] = nm;
  out[at + 2] = String.valueOf(num(p, "pet." + id + ".level", 1L, 1L, 100L));
  out[at + 3] = RARITY[(int) num(p, "pet." + id + ".rarity", 1L, 1L, 6L) - 1];
}""")
M(pet, r"""
public static String[] parse(java.util.Properties p) {
  String[] out = empty("ok");
  int n = 0;
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith("pet.") && k.endsWith(".kind") && k.length() > 9) n++;
  }
  out[9] = String.valueOf(n);
  fill(out, 1, p, p.getProperty("active.1", ""));
  fill(out, 5, p, p.getProperty("active.2", ""));
  return out;
}""")
M(pet, r"""
public static String[] read(String key) {
  java.nio.file.Path d = DIR;
  if (d == null || !@PKG@.Given.validKey(key)) return empty("none");
  try {
    java.nio.file.Path f = d.resolve(key + ".properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) { CACHE.remove(key); return empty("none"); }
    if (!java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) return empty("bad");
    long mt = java.nio.file.Files.getLastModifiedTime(f, new java.nio.file.LinkOption[0]).toMillis();
    long sz = java.nio.file.Files.size(f);
    Object[] c = (Object[]) CACHE.get(key);
    if (c != null && ((Long) c[0]).longValue() == mt && ((Long) c[1]).longValue() == sz) return (String[]) c[2];
    String[] out;
    if (sz > 1048576L) out = empty("bad");
    else {
      byte[] b = java.nio.file.Files.readAllBytes(f);
      READS = READS + 1L;
      java.util.Properties p = new java.util.Properties();
      p.load(new java.io.ByteArrayInputStream(b));
      String v = p.getProperty("v");
      out = (v == null || !v.trim().equals("1")) ? empty("bad") : parse(p);
    }
    if (CACHE.size() > 2000) CACHE.clear();
    CACHE.put(key, new Object[] { Long.valueOf(mt), Long.valueOf(sz), out });
    return out;
  } catch (Throwable t) { return empty("bad"); }
}""")
# the ACTIVE profile's record (never the account: the storage key changes with the profile)
M(pet, r"""
public static String[] of(java.util.UUID u) {
  if (u == null) return empty("none");
  return read(@PKG@.Given.key(u));
}""")
# SkyyPets is loaded: its bridge function (setup .. shutdown) AND a /pets command (another mod's /pets alone never shows the tile)
M(pet, r"""
public static boolean installed() {
  try { return @PKG@.MenuUtil.bridge().get("pets:fn:onxp") != null && @PKG@.MenuUtil.cmd("pets") != null; }
  catch (Throwable t) { return false; }
}""")
M(pet, r"""
public static boolean has(String[] pi) {
  return pi != null && pi.length == 10 && "ok".equals(pi[0]) && pi[1].length() > 0;
}""")
M(pet, r"""
public static String title(String[] pi) {
  return has(pi) ? "Pets - " + pi[2] + " Lv " + pi[3] : "Pets";
}""")
M(pet, r"""
public static String icon(String[] pi) {
  if (!has(pi)) return @PKG@.MenuData.ICON_PETS;
  for (int i = 0; i < @PKG@.MenuData.PET_KIND.length; i++) if (@PKG@.MenuData.PET_KIND[i].equals(pi[1])) return @PKG@.MenuData.PET_ICON[i];
  return @PKG@.MenuData.ICON_PETS;
}""")
M(pet, r"""
public static String slotText(String[] pi, int at) {
  if (pi[at].length() == 0) return "empty";
  String kd = display(pi[at]);
  if (pi[at + 1].equals(kd)) return pi[at + 3] + " " + kd + " Lv " + pi[at + 2];
  return pi[at + 1] + " (" + pi[at + 3] + " " + kd + ") Lv " + pi[at + 2];
}""")
M(pet, r"""
public static String body(java.util.UUID u, String[] pi) {
  int max = @PKG@.StatsCalc.LINE_MAX;
  String pn = "";
  try {
    Object o = u == null ? null : @PKG@.MenuUtil.bridge().get("profile:name:" + u.toString());
    if (o instanceof String) pn = @PKG@.MenuUtil.safe((String) o).trim();
  } catch (Throwable t) { pn = ""; }
  if (pn.length() > 27) pn = pn.substring(0, 24).trim() + "...";
  StringBuilder sb = new StringBuilder();
  sb.append(@PKG@.MenuUtil.clip("Your pets on this profile" + (pn.length() > 0 ? " (" + pn + ")" : "") + ". Click to see them all.", max));
  if (pi == null || pi.length != 10 || "bad".equals(pi[0])) sb.append("\nYour pet file could not be read. Ask an admin.");
  else {
    sb.append("\n").append(@PKG@.MenuUtil.clip("Pet slot: " + slotText(pi, 1), max));
    if (pi[5].length() > 0) sb.append("\n").append(@PKG@.MenuUtil.clip("Summon slot: " + slotText(pi, 5), max));
    sb.append("\n").append(@PKG@.MenuUtil.clip("Pets owned: " + pi[9], max));
  }
  sb.append("\nPets stay on this profile - every profile has its own.");
  sb.append("\nCommand: /pets (or /pet)");
  return sb.toString();
}""")

# ================= 0.3.29 MenuLayout: every player's HOME shortcut grid + TELEPORT grid (Skyy 2026-10-15, the unified menu) =================
# 0.3.30: a grid = String[HG_N] of shortcut keys, 5 x 5 (25). The files keep 0.3.29's 7 x 5 numbering (G7: slot = row * 7 + column, the
# 5 x 5 grid = columns 1 - 5); fold() reads a 7 x 5 line set into the 5 x 5 grid (columns 0 / 6 move to the nearest free slot, the same
# page twice is kept once), lines() writes it back in the 7 x 5 numbering. A record grows two elements: [6] Boolean "the 0.3.30 update
# changed this grid and is not written yet", [7] String "<n>|<keys>" = pins that found no free slot (they wait in + Add).
# 0.3.29: A grid = String[HG_N] of shortcut keys (null = an empty slot). A RECORD (one per account, also the server
# default DEF) = Object[]{ String[] home or null (= the default), String[] tp or null, String old line (_old) or null, String 0.3.28 tile
# lines or null, Boolean "one-time update not yet written", String _name from the file }. OWN: uuid text -> its record (never changed
# after it is published - copy-on-write), NONE (no file) or ERR (a read error: the default is drawn, editing is refused, re-read after
# 30 s). Files (Skyy_SkyyMenu/layouts/<uuid>.properties, layout-default.properties), extended backward-compatibly:
#   _v=1  _home=1|0  _tp=1|0  [_old=<0.3.28 tile=slot,...>]  <the 0.3.28 tile=slot lines, kept for a rollback>  g.<slot>=<key>  t.<slot>=<key>
# THE ONE-TIME UPDATE (PROJECT-RULES 4): a file with _v=1 and 0.3.28 tile lines but no _home is a 0.3.28 layout: migrate() in memory at
# the first read (hubs replace the tiles they cover, the rest keep their offset from the centre, outside = + Add), then the first write
# (SkyyMenu-IO) keeps a VERIFIED History copy of the exact old bytes in config-history/ first (read back + compared; a failure = no write,
# retried), writes _home (the run-once marker) + _old (the old line) + the old tile lines + the new grid, and queues one config-changes.log
# line (status done; Undo = Edit shortcuts > Old tiles back). A removed tile never comes back by itself (no "new tile -> first free slot").
F(lay, "public static volatile java.nio.file.Path DIR;")
F(lay, "public static volatile java.nio.file.Path DEF_FILE;")
F(lay, 'public static final String NONE = "none";')
F(lay, 'public static final String BAD = "bad";')
F(lay, 'public static final String ERR = "err";')
F(lay, 'public static final String DEF_KEY = "_default";')
F(lay, "public static volatile Object[] DEF;")
F(lay, "public static volatile boolean DEF_BROKEN;")
F(lay, "public static volatile int MIGRATIONS;")
F(lay, "public static volatile int FOLDS;")            # 0.3.30: grids the 5 x 5 update changed at their first read
F(lay, "public static final java.util.concurrent.ConcurrentHashMap SPILL = new java.util.concurrent.ConcurrentHashMap();")   # 0.3.30: uuid -> "<n>|<keys>"
F(lay, 'public static final java.time.format.DateTimeFormatter STAMP = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");')
F(lay, 'public static final java.time.format.DateTimeFormatter HUMAN = java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");')
# SNAPPED: file key -> FALSE = its History copy is made (a failed write then never makes a second one), TRUE = the update is written + logged.
# HFAIL: file key -> Integer, failed History copies in a row (HIST_TRIES = write anyway: the old layout stays in the file itself).
for _f in ("OWN", "NAMES", "DIRTY", "WARNED", "BROKEN", "ERRAT", "MIGRATED", "SNAPPED", "HFAIL"):
    F(lay, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
F(lay, "public static final int HIST_TRIES = 3;")
# fix round: the server default's one-time update waits for the first player (DEF_PENDING): at setup no other mod has published its hub
# tabs yet, so the hub check of migrate() could not see them
F(lay, "public static final java.util.concurrent.atomic.AtomicBoolean DEF_PENDING = new java.util.concurrent.atomic.AtomicBoolean(false);")
F(lay, 'public static final String HIST_INDEX = "SkyyMenu-layouts-index.log";')
# LayoutSaveTask's fields + constructors first (saveSoon / preload construct it); its run() after saveNow
lsv.addInterface(pool.get("java.lang.Runnable"))
F(lsv, "public String k;")
F(lsv, "public boolean load;")
C(lsv, "public LayoutSaveTask(String k) { this.k = k; this.load = false; }")
C(lsv, "public LayoutSaveTask(String k, boolean load) { this.k = k; this.load = load; }")
M(lay, r"""
public static boolean isMain(int i) {
  return i >= 0 && i < @PKG@.MenuData.E_VIEW.length && "main".equals(@PKG@.MenuData.E_VIEW[i]);
}""")
# the 0.3.28 built-in layout (layout D) - only the retired 9 x 6 code path still reads it
M(lay, r"""
public static int[] builtinOld() {
  int n = @PKG@.MenuData.E_VIEW.length;
  int[] out = new int[n];
  for (int i = 0; i < n; i++) out[i] = isMain(i) ? @PKG@.MenuData.E_SLOT[i] : -1;
  return out;
}""")
M(lay, r"""
public static int keyIndex(String k) {
  if (k == null) return -1;
  for (int i = 0; i < @PKG@.MenuData.E_KEY.length; i++) { if (isMain(i) && @PKG@.MenuData.E_KEY[i].equals(k)) return i; }
  return -1;
}""")
M(lay, r"""
public static int hubIdx(String h) {
  if (h == null) return -1;
  for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) { if (@PKG@.MenuData.HUB_ID[i].equals(h)) return i; }
  return -1;
}""")
M(lay, r"""
public static boolean okWarp(String n) {
  if (n == null || n.length() < 1 || n.length() > 64) return false;   // 0.3.38: 64 (vanilla /warp set names may be longer than 32)
  for (int i = 0; i < n.length(); i++) {
    char c = n.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-' || c == '.')) return false;   // 0.3.38: + '.' (SkyyEssentials' warp name rule)
  }
  return true;
}""")
M(lay, r"""
public static boolean okTp(String k) {
  if (k == null) return false;
  for (int i = 0; i < @PKG@.MenuData.TPK_KEY.length; i++) { if (@PKG@.MenuData.TPK_KEY[i].equals(k)) return true; }
  if (k.startsWith("ihome:") || k.startsWith("zhome:")) return okWarp(k.substring(6));   // 0.3.37: an island home / a home (names: the warp rule)
  return k.startsWith("warp:") && okWarp(k.substring(5));
}""")
# a key that may sit on a grid (tp = the Teleport grid: teleport targets only; Home takes every kind)
M(lay, r"""
public static boolean okKey(String k, boolean tp) {
  if (k == null || k.length() < 4 || k.length() > 80) return false;
  if (okTp(k)) return true;
  if (tp) return false;
  if (k.startsWith("hub:")) return hubIdx(k.substring(4)) >= 0;
  if (k.startsWith("tab:")) {
    int c = k.indexOf(':', 4);
    return c > 4 && hubIdx(k.substring(4, c)) >= 0 && @PKG@.HubBar.okId(k.substring(c + 1));
  }
  if (k.startsWith("tile:")) {
    int i = keyIndex(k.substring(5));
    return i >= 0 && !"-".equals(@PKG@.MenuData.MIG[i]);
  }
  return false;
}""")
M(lay, r"""
public static boolean has(String[] g, String k) {
  if (g == null || k == null) return false;
  for (int i = 0; i < g.length; i++) { if (k.equals(g[i])) return true; }
  return false;
}""")
M(lay, "public static String[] blank() { return new String[@PKG@.MenuData.HG_N]; }")
M(lay, "public static String[] blank7() { return new String[@PKG@.MenuData.G7_N]; }")   # 0.3.30: the 7 x 5 numbering of the files
M(lay, "public static int to7(int s) { return (s / @PKG@.MenuData.HG_COLS) * @PKG@.MenuData.G7_COLS + s % @PKG@.MenuData.HG_COLS + @PKG@.MenuData.G7_OFF; }")
M(lay, "public static Object el(Object[] r, int i) { return r != null && i >= 0 && i < r.length ? r[i] : null; }")
M(lay, r"""
public static String[] copy(String[] g) {
  String[] o = blank();
  if (g == null) return o;
  for (int i = 0; i < o.length && i < g.length; i++) o[i] = g[i];
  return o;
}""")
# part 0 = Home, 1 = Teleport: the built-in default grid
M(lay, r"""
public static String[] builtin(int part) {
  String[] g = blank();
  String[] ks = @PKG@.MenuData.BH_KEY;
  int[] ss = @PKG@.MenuData.BH_SLOT;
  if (part == 1) { ks = @PKG@.MenuData.BT_KEY; ss = @PKG@.MenuData.BT_SLOT; }
  for (int i = 0; i < ks.length; i++) g[ss[i]] = ks[i];
  return g;
}""")
M(lay, r"""
public static void warnOnce(String what, String msg) {
  if (WARNED.putIfAbsent(what, Boolean.TRUE) != null) return;
  @PKG@.MenuUtil.warn(msg);
}""")
# g.<slot> / t.<slot> lines -> a 7 x 5 grid (0.3.30: fold() makes it 5 x 5); a bad key, a slot outside 0 - 34 or a key already on it is skipped
M(lay, r"""
public static String[] slotLines(java.util.Properties p, String pre, boolean tp) {
  String[] g = blank7();
  for (int s = 0; s < g.length; s++) {
    String v = p.getProperty(pre + s);
    if (v == null) continue;
    v = v.trim();
    if (okKey(v, tp) && !has(g, v)) g[s] = v;
  }
  return g;
}""")
# the 0.3.28 tile=slot lines (slots 0 - 44) -> int[entry] = slot (-1 = none); null = no usable line
# a 0.3.28 tile line's slot: 0 - 44, else -1
M(lay, r"""
public static int slotOf(String v) {
  int sl = -1;
  try { sl = Integer.parseInt(v.trim()); } catch (Throwable t) { sl = -1; }
  return sl >= 0 && sl < @PKG@.MenuData.LAY_GRID ? sl : -1;
}""")
M(lay, r"""
public static int[] parseOld(java.util.Properties p) {
  int n = @PKG@.MenuData.E_VIEW.length;
  int[] out = new int[n];
  int got = 0;
  for (int i = 0; i < n; i++) {
    out[i] = -1;
    if (!isMain(i)) continue;
    String v = p.getProperty(@PKG@.MenuData.E_KEY[i]);
    if (v == null) continue;
    int sl = slotOf(v);
    if (sl >= 0) { out[i] = sl; got = got + 1; }
  }
  if (got == 0) return null;
  return out;
}""")
M(lay, r"""
public static String oldLine(int[] old) {
  StringBuilder sb = new StringBuilder();
  for (int s = 0; s < @PKG@.MenuData.LAY_GRID; s++) {
    for (int i = 0; i < old.length; i++) {
      if (!isMain(i) || old[i] != s) continue;
      if (sb.length() > 0) sb.append(',');
      sb.append(@PKG@.MenuData.E_KEY[i]).append('=').append(s);
    }
  }
  return sb.toString();
}""")
M(lay, r"""
public static String compatText(int[] old) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < old.length; i++) {
    if (!isMain(i) || old[i] < 0) continue;
    sb.append(@PKG@.MenuData.E_KEY[i]).append('=').append(old[i]).append('\n');
  }
  return sb.toString();
}""")
# 9 x 6 slot -> 7 x 5 slot keeping its offset from the centre (13 -> 17); -1 = outside the new grid
M(lay, r"""
public static int mapSlot(int s) {
  if (s < 0 || s >= @PKG@.MenuData.LAY_GRID) return -1;
  int r = s / @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CR + @PKG@.MenuData.G7_CR;
  int c = s % @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CC + @PKG@.MenuData.G7_CC;
  if (r < 0 || r >= @PKG@.MenuData.G7_ROWS || c < 0 || c >= @PKG@.MenuData.G7_COLS) return -1;
  return r * @PKG@.MenuData.G7_COLS + c;
}""")
# fix round: is the page an old tile IS (MenuData.MIG_TAB, "<hub>:<tab>") on this server right now (its hub:tab:<hub>:<tab> published)?
M(lay, r"""
public static boolean tabHere(String t) {
  if (t == null || t.length() == 0) return false;
  try { return @PKG@.HubBar.get("hub:tab:" + t) instanceof Object[]; } catch (Throwable x) { return false; }
}""")
# fix round 2: a hub whose covered tiles ALL sat outside the 7 x 5 grid (Skyy's own layout: Social on the left edge, Settings on the right)
# still replaces them - it goes on the free slot nearest to its first covered tile's spot pulled inside the grid (ties: reading order).
# Only hubs that replace a tile (its page is published right now); uncovered tiles outside still wait in + Add. Runs after every tile
# inside the grid has its place, so it only fills empty slots.
M(lay, r"""
public static void placeOutside(String[] g, int[] old) {
  for (int s = 0; s < @PKG@.MenuData.LAY_GRID; s++) {
    int i = -1;
    for (int k = 0; k < old.length; k++) { if (isMain(k) && old[k] == s) { i = k; break; } }
    if (i < 0) continue;
    String m = @PKG@.MenuData.MIG[i];
    if (m.length() == 0 || m.equals("-") || m.startsWith("=")) continue;
    if (!tabHere(@PKG@.MenuData.MIG_TAB[i])) continue;
    String key = "hub:" + m;
    if (has(g, key)) continue;
    int r = s / @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CR + @PKG@.MenuData.G7_CR;
    int c = s % @PKG@.MenuData.OLD_COLS - @PKG@.MenuData.OLD_CC + @PKG@.MenuData.G7_CC;
    if (r < 0) r = 0;
    if (r > @PKG@.MenuData.G7_ROWS - 1) r = @PKG@.MenuData.G7_ROWS - 1;
    if (c < 0) c = 0;
    if (c > @PKG@.MenuData.G7_COLS - 1) c = @PKG@.MenuData.G7_COLS - 1;
    int best = -1;
    int bd = 0;
    for (int x = 0; x < g.length; x++) {
      if (g[x] != null) continue;
      int dr = x / @PKG@.MenuData.G7_COLS - r;
      int dc = x % @PKG@.MenuData.G7_COLS - c;
      int d = dr * dr + dc * dc;
      if (best < 0 || d < bd) { best = x; bd = d; }
    }
    if (best >= 0) g[best] = key;
  }
}""")
# THE MIGRATION (hubs = true; false = "Old tiles back": every old tile as itself). The old tiles in reading order: Hover Tooltips is
# retired; a covered tile -> its hub, on the first covered tile's new slot that is inside the grid (once per hub) - but ONLY when the
# tile's own page is published as that hub's tab right now (fix round: a hub without the page would turn a working tile into a
# "coming soon" stub for good; such a tile stays itself); Teleport -> the Teleport shortcut; any other tile -> itself; a slot outside the
# 7 x 5 grid = not placed (it waits in + Add). Runs at a player's first read (join: every mod has published its tabs).
M(lay, r"""
public static String[] migrate7(int[] old, boolean hubs) {
  String[] g = blank7();
  if (old == null) return g;
  for (int s = 0; s < @PKG@.MenuData.LAY_GRID; s++) {
    int i = -1;
    for (int k = 0; k < old.length; k++) { if (isMain(k) && old[k] == s) { i = k; break; } }
    if (i < 0) continue;
    String m = @PKG@.MenuData.MIG[i];
    if (m.equals("-")) continue;
    int ns = mapSlot(s);
    if (ns < 0 || g[ns] != null) continue;
    String key = null;
    if (m.startsWith("=")) key = m.substring(1);
    else if (hubs && m.length() > 0 && tabHere(@PKG@.MenuData.MIG_TAB[i])) key = "hub:" + m;
    else key = "tile:" + @PKG@.MenuData.E_KEY[i];
    if (has(g, key)) continue;
    g[ns] = key;
  }
  if (hubs) placeOutside(g, old);
  return g;
}""")
# 0.3.30: ONE ENTRY PER PAGE (Skyy 2026-10-16 "make sure we dont have any duplicates"). canon() = the page a key opens: an old tile ->
# the hub tab it IS (MenuData.MIG_TAB, fix round 2's twin), a hub with a DEFAULT tab (Character -> skills, World -> teleport) -> that tab,
# anything else -> itself. + Add lists a page once and a grid never holds it twice (hasSame). rank(): which key of a page a saved grid keeps
# - the tab (0), else the old tile (1), else the hub (2).
M(lay, r"""
public static String canon(String k) {
  if (k == null) return null;
  if (k.startsWith("tile:")) {
    int i = keyIndex(k.substring(5));
    if (i >= 0 && @PKG@.MenuData.MIG_TAB[i].length() > 0) return "tab:" + @PKG@.MenuData.MIG_TAB[i];
    return k;
  }
  if (k.startsWith("hub:")) {
    int h = hubIdx(k.substring(4));
    if (h >= 0 && @PKG@.MenuData.HUB_DEFTAB[h].length() > 0) return "tab:" + @PKG@.MenuData.HUB_ID[h] + ":" + @PKG@.MenuData.HUB_DEFTAB[h];
  }
  return k;
}""")
M(lay, r"""
public static int rank(String k) {
  if (k == null) return 9;
  if (k.equals(canon(k))) return 0;
  return k.startsWith("tile:") ? 1 : 2;
}""")
M(lay, r"""
public static boolean hasSame(String[] g, String k) {
  if (g == null || k == null) return false;
  String c = canon(k);
  for (int i = 0; i < g.length; i++) { if (g[i] != null && c.equals(canon(g[i]))) return true; }
  return false;
}""")
# + Add's list: k unless its page is listed already (cs = the pages listed so far)
M(lay, r"""
public static void addOnce(java.util.ArrayList out, java.util.ArrayList cs, String k) {
  String c = canon(k);
  if (c == null || cs.contains(c)) return;
  cs.add(c);
  out.add(k);
}""")
# THE 5 x 5 FOLD (0.3.30): a 7 x 5 grid (the files' numbering) -> Object[]{ String[25] grid, Boolean changed, String "<n>|<keys>" or null }.
# Columns 1 - 5 keep their place; the same page twice keeps its best key (rank, ties = reading order; Home only); a pin in column 0 / 6
# goes to the free slot nearest its spot pulled inside (ties = reading order; the pins in reading order) unless its page is on the grid
# already (then the more exact of the two keys stays in that slot); no free slot = it waits in + Add (counted, named in [2]). changed = anything moved or merged.
M(lay, r"""
public static Object[] fold(String[] g7, boolean tp) {
  String[] g = blank();
  boolean ch = false;
  java.util.ArrayList over = new java.util.ArrayList();
  int cols = @PKG@.MenuData.HG_COLS;
  for (int s = 0; g7 != null && s < g7.length && s < @PKG@.MenuData.G7_N; s++) {
    if (g7[s] == null) continue;
    int r = s / @PKG@.MenuData.G7_COLS;
    int c = s % @PKG@.MenuData.G7_COLS - @PKG@.MenuData.G7_OFF;
    if (c >= 0 && c < cols && r < @PKG@.MenuData.HG_ROWS) g[r * cols + c] = g7[s];
    else over.add(Integer.valueOf(s));
  }
  if (!tp) {
    for (int i = 0; i < g.length; i++) {
      if (g[i] == null) continue;
      String ci = canon(g[i]);
      for (int j = 0; j < g.length; j++) {
        if (j == i || g[j] == null || !ci.equals(canon(g[j]))) continue;
        int ri = rank(g[i]);
        int rj = rank(g[j]);
        if (rj < ri || (rj == ri && j < i)) { g[i] = null; ch = true; break; }
      }
    }
  }
  int ns = 0;
  StringBuilder sp = new StringBuilder();
  for (int k = 0; k < over.size(); k++) {
    int s = ((Integer) over.get(k)).intValue();
    String key = g7[s];
    ch = true;
    if (tp ? has(g, key) : hasSame(g, key)) {
      if (!tp) {   // the same page is on the grid already: the more exact key stays (in that slot)
        for (int j = 0; j < g.length; j++) { if (g[j] != null && canon(g[j]).equals(canon(key)) && rank(key) < rank(g[j])) g[j] = key; }
      }
      continue;
    }
    int r = s / @PKG@.MenuData.G7_COLS;
    int c = s % @PKG@.MenuData.G7_COLS - @PKG@.MenuData.G7_OFF;
    if (c < 0) c = 0;
    if (c > cols - 1) c = cols - 1;
    if (r > @PKG@.MenuData.HG_ROWS - 1) r = @PKG@.MenuData.HG_ROWS - 1;
    int best = -1;
    int bd = 0;
    for (int x = 0; x < g.length; x++) {
      if (g[x] != null) continue;
      int dr = x / cols - r;
      int dc = x % cols - c;
      int d = dr * dr + dc * dc;
      if (best < 0 || d < bd) { best = x; bd = d; }
    }
    if (best < 0) {
      ns = ns + 1;
      if (sp.length() > 0) sp.append(',');
      sp.append(key);
      continue;
    }
    g[best] = key;
  }
  return new Object[] { g, Boolean.valueOf(ch), ns == 0 ? null : ns + "|" + sp.toString() };
}""")
# fix 2: both grids' spill lists in one "<n>|<keys>" (Home first, then Teleport) - the log line, the chat note and Right now name them all
M(lay, r"""
public static String joinSpill(String a, String b) {
  if (a == null) return b;
  if (b == null) return a;
  int i = a.indexOf('|');
  int j = b.indexOf('|');
  int n = 0;
  try { n = Integer.parseInt(a.substring(0, i)) + Integer.parseInt(b.substring(0, j)); } catch (Throwable t) { n = 0; }
  return n + "|" + a.substring(i + 1) + "," + b.substring(j + 1);
}""")
# the 0.3.28 update (migrate7, the 7 x 5 grid 0.3.29 made) then the 5 x 5 fold
M(lay, r"""
public static String[] migrate(int[] old, boolean hubs) {
  return (String[]) fold(migrate7(old, hubs), false)[0];
}""")
# properties -> a record; null = not a layout (no _v=1, or neither _home nor 0.3.28 tile lines)
M(lay, r"""
public static Object[] parse(java.util.Properties p) {
  if (p == null || !"1".equals(p.getProperty("_v", "").trim())) return null;
  String hm = p.getProperty("_home");
  int[] old = parseOld(p);
  String nm = p.getProperty("_name");
  if (hm == null) {
    if (old == null) return null;
    Object[] f0 = fold(migrate7(old, true), false);
    return new Object[] { f0[0], null, oldLine(old), compatText(old), Boolean.TRUE, nm, Boolean.FALSE, f0[2] };
  }
  String[] home = null;
  Object[] fh = null;
  if ("1".equals(hm.trim())) { fh = fold(slotLines(p, "g.", false), false); home = (String[]) fh[0]; }
  String[] tp = null;
  Object[] ft = null;
  if ("1".equals(p.getProperty("_tp", "").trim())) { ft = fold(slotLines(p, "t.", true), true); tp = (String[]) ft[0]; }
  boolean ch = (fh != null && Boolean.TRUE.equals(fh[1])) || (ft != null && Boolean.TRUE.equals(ft[1]));
  String sp = joinSpill(fh != null ? (String) fh[2] : null, ft != null ? (String) ft[2] : null);   // fix 2: Home + Teleport
  String ol = p.getProperty("_old");
  if (ol != null) ol = ol.trim();
  if (ol != null && ol.length() == 0) ol = null;
  String ct = null;
  if (old != null) ct = compatText(old);
  return new Object[] { home, tp, ol, ct, Boolean.FALSE, nm, Boolean.valueOf(ch), sp };
}""")
# null = no file; Object[] = a record; BAD = the file reads but holds no layout; ERR = a read error (both warned once per file)
M(lay, r"""
public static Object readFile(java.nio.file.Path f, String what) {
  if (f == null) return null;
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(new java.io.InputStreamReader(in, "UTF-8")); } finally { in.close(); }
    Object[] r = parse(p);
    if (r != null) return r;
    warnOnce(what, "the menu layout file " + what + " holds no usable layout (it needs _v=1 and _home or tile=slot lines) - the default shortcuts are used; the file stays as it is until the shortcuts are changed in game (then it is kept as " + what + ".bad)");
    return BAD;
  } catch (Throwable t) {
    warnOnce(what, "the menu layout file " + what + " cannot be read (" + t + ") - the default shortcuts are shown and cannot be edited until the file reads again (tried again every 30 s); the file is NOT changed");
  }
  return ERR;
}""")
M(lay, r"""
public static void lines(StringBuilder sb, String pre, String[] g) {
  if (g == null) return;
  for (int s = 0; s < g.length; s++) { if (g[s] != null) sb.append(pre).append(to7(s)).append('=').append(g[s]).append('\n'); }   // 0.3.30: 7 x 5 numbering
}""")
# the 0.3.29 lines of a record (_home / _tp / _old / g. / t.): text() writes them after the 0.3.28 lines, the one-time update appends them
M(lay, r"""
public static String tail(Object[] r) {
  StringBuilder sb = new StringBuilder();
  sb.append("_home=").append(r[0] != null ? "1" : "0").append('\n');
  sb.append("_tp=").append(r[1] != null ? "1" : "0").append('\n');
  if (r[2] != null) sb.append("_old=").append((String) r[2]).append('\n');
  sb.append("_g5=1\n");   // 0.3.30: the 5 x 5 run-once marker
  lines(sb, "g.", (String[]) r[0]);
  lines(sb, "t.", (String[]) r[1]);
  return sb.toString();
}""")
# the 0.3.28 tile lines: the file's own, else (fix round) the 0.3.28 built-in layout D in full - a rollback to 0.3.28 then shows layout D
# exactly (one lone teleport=13 line made 0.3.28 put the other tiles in the first free slots). Fix round 2: a player with no 0.3.28 file
# on a server whose default holds 0.3.28 tile lines (a custom 0.3.28 server default) gets THOSE lines - a rollback then shows them the
# server's default, as 0.3.28 did, not layout D
M(lay, r"""
public static String text(Object[] r, String head) {
  StringBuilder sb = new StringBuilder();
  sb.append(head);
  sb.append("_v=1\n");
  String ct = (String) r[3];
  Object[] d = DEF;
  if (ct == null && d != null && d != r && d.length > 3 && d[3] != null) ct = (String) d[3];   // fix round 2: a custom server default's lines
  sb.append(ct != null ? ct : compatText(builtinOld()));
  sb.append(tail(r));
  return sb.toString();
}""")
# a file that already holds 0.3.29 lines (hand-made: g. / t. / _home / _tp / _old) is rewritten in full, never appended to
M(lay, r"""
public static boolean hasNewLines(String t) {
  String[] ls = t.split("\n");
  for (int i = 0; i < ls.length; i++) {
    String l = ls[i].trim();
    if (l.startsWith("g.") || l.startsWith("t.") || l.startsWith("_home") || l.startsWith("_tp") || l.startsWith("_old") || l.startsWith("_g5")) return true;
  }
  return false;
}""")
# the bytes to write. THE ONE-TIME UPDATE (PROJECT-RULES 4 "keep the file's bytes and line endings"): the old file's EXACT bytes + the
# 0.3.29 lines appended in its own line ending (a later _key wins in a properties file; a 0.3.28 SkyyMenu reads the untouched old lines).
# Any later save: the whole file in the file's own line ending (CRLF stays CRLF).
# 0.3.30: the 5 x 5 update's lines for one grid: every 7 x 5 slot whose value changes (a slot that loses its pin: "<pre><slot>=" - an empty
# value is no key for 0.3.29 or 0.3.30). Later lines win in a properties file, so 0.3.29 (a rollback) reads the same 5 x 5 grid.
M(lay, r"""
public static void diff(StringBuilder sb, java.util.Properties p, String pre, String[] g) {
  if (g == null) return;
  String[] n7 = blank7();
  for (int s = 0; s < g.length; s++) { if (g[s] != null) n7[to7(s)] = g[s]; }
  for (int s = 0; s < n7.length; s++) {
    String ov = p.getProperty(pre + s);
    if (ov != null) ov = ov.trim();
    if (n7[s] == null) { if (ov != null && ov.length() > 0 && okKey(ov, pre.equals("t."))) sb.append(pre).append(s).append("=\n"); }   // fix: an unknown key stays as it was
    else if (!n7[s].equals(ov)) sb.append(pre).append(s).append('=').append(n7[s]).append('\n');
  }
}""")
M(lay, r"""
public static String foldTail(String old, Object[] r) throws java.io.IOException {
  java.util.Properties p = new java.util.Properties();
  p.load(new java.io.StringReader(old));
  StringBuilder sb = new StringBuilder();
  sb.append("# 0.3.30: the shortcuts are a 5 x 5 grid (columns 1 - 5 of the numbering above): pins from columns 0 and 6 moved in, a page held twice kept once - every line above is kept as it was\n");
  sb.append("_g5=1\n");
  diff(sb, p, "g.", (String[]) r[0]);
  diff(sb, p, "t.", (String[]) r[1]);
  return sb.toString();
}""")
M(lay, r"""
public static byte[] appendTo(byte[] was, String add, String nl) throws java.io.IOException {
  if (was.length > 0 && was[was.length - 1] != (byte) 10) add = "\n" + add;
  if (!nl.equals("\n")) add = add.replace("\n", nl);
  byte[] tb = add.getBytes("UTF-8");
  byte[] out = new byte[was.length + tb.length];
  System.arraycopy(was, 0, out, 0, was.length);
  System.arraycopy(tb, 0, out, was.length, tb.length);
  return out;
}""")
# the bytes to write. THE ONE-TIME UPDATES (PROJECT-RULES 4 "keep the file's bytes and line endings"): the old file's EXACT bytes + the new
# lines appended in its own line ending - 0.3.29's (a 0.3.28 layout: every line of the record) and 0.3.30's (a 0.3.29 layout whose grid
# the 5 x 5 fold changed: only the lines that change). Any later save: the whole file in the file's own line ending (CRLF stays CRLF).
M(lay, r"""
public static byte[] bytesFor(byte[] was, boolean mig, boolean fold, Object[] r, String head) throws java.io.IOException {
  String old = null;
  if (was != null) old = new String(was, "UTF-8");
  String nl = (old != null && old.indexOf("\r\n") >= 0) ? "\r\n" : "\n";
  if (mig && old != null && !hasNewLines(old))
    return appendTo(was, "# 0.3.29: the Home shortcuts (the one-time update - every line above is the 0.3.28 layout exactly as it was)\n" + tail(r), nl);
  if (fold && old != null) return appendTo(was, foldTail(old, r), nl);
  String t = text(r, head);
  if (!nl.equals("\n")) t = t.replace("\n", nl);
  return t.getBytes("UTF-8");
}""")
M(lay, r"""
public static boolean empty(Object[] r) {
  return r == null || (r[0] == null && r[1] == null && r[2] == null && r[3] == null);
}""")
M(lay, r"""
public static String summary(Object g) {
  if (!(g instanceof String[])) return "the default shortcuts";
  String[] a = (String[]) g;
  StringBuilder sb = new StringBuilder();
  for (int s = 0; s < a.length; s++) { if (a[s] != null) { if (sb.length() > 0) sb.append(' '); sb.append(s).append('=').append(a[s]); } }
  return sb.length() == 0 ? "no shortcuts" : sb.toString();
}""")
M(lay, r"""
public static void keepBad(java.nio.file.Path f) throws java.io.IOException {
  if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
  java.nio.file.Path b = f.resolveSibling(f.getFileName().toString() + ".bad");
  if (java.nio.file.Files.exists(b, new java.nio.file.LinkOption[0])) b = f.resolveSibling(f.getFileName().toString() + ".bad-" + System.currentTimeMillis());
  java.nio.file.Files.move(f, b, new java.nio.file.CopyOption[0]);
}""")
M(lay, r"""
public static String fileId(String what) { return "Skyy_SkyyMenu~" + what.replace('/', '~'); }""")
# THE VERIFIED HISTORY COPY (PROJECT-RULES 4, before the one-time update's first write): the file's exact bytes -> config-history/
# <fileId>.<yyyyMMdd-HHmmss-SSS>.bak (the config kit's folder and naming), read back and compared byte for byte; any difference throws
# (the file is then NOT written; saveNow keeps it DIRTY and retries every 30 s). One index line in the kit's format (best effort) - in its OWN file
# config-history/SkyyMenu-layouts-index.log (fix round: the kit's index.log compaction drops ids that are not settings files).
M(lay, r"""
public static java.nio.file.Path history(java.nio.file.Path f, String what, String sum) throws java.io.IOException {
  byte[] cur = java.nio.file.Files.readAllBytes(f);
  java.nio.file.Path dir = f.toAbsolutePath().getParent();
  if (dir.getFileName() != null && "layouts".equals(dir.getFileName().toString())) dir = dir.getParent();
  dir = dir.resolve("config-history");
  java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
  String id = fileId(what);
  java.time.LocalDateTime now = java.time.LocalDateTime.now();
  java.nio.file.Path b = null;
  String st = null;
  for (int g = 0; g < 1000; g++) {
    java.time.LocalDateTime t = now.plusNanos(1000000L * g);
    st = STAMP.format(t);
    b = dir.resolve(id + "." + st + ".bak");
    if (!java.nio.file.Files.exists(b, new java.nio.file.LinkOption[0])) { now = t; break; }
  }
  @PKG@.MenuUtil.atomicWrite(b, cur);
  byte[] back = java.nio.file.Files.readAllBytes(b);
  if (!java.util.Arrays.equals(back, cur)) throw new java.io.IOException("the History copy " + b.getFileName() + " does not match " + what + " - the file is not changed");
  String line = id + "#" + st + "\tSkyy_SkyyMenu/" + what + "\t" + HUMAN.format(now) + "\tSkyyMenu update\t" + sum + "\n";
  try { java.nio.file.Files.write(dir.resolve(HIST_INDEX), line.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND }); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not add the History line of " + what + " to config-history/" + HIST_INDEX + " (the copy " + b.getFileName() + " is kept): " + t); }
  return b;
}""")
# one config-changes.log line per updated file (the config kit's queue: written by its save task / at shutdown); status done (a layout is
# not a setting row, so Server Setup offers no Undo button - Edit shortcuts > Old tiles back undoes it)
M(lay, r"""
public static void logMigration(String k, Object[] r) {
  try {
    @PKG@.CfgLog.add(null, "SkyyMenu update", "update", "menu.layout[" + k + "]", r[2] == null ? "" : (String) r[2],
      "(0.3.29 Home shortcuts: " + summary(r[0]) + " - Edit shortcuts, " + (DEF_KEY.equals(k) ? "Old default" : "Old tiles back") + " undoes it)", "done");
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not log the menu layout update of " + k + " in config-changes.log: " + t); }
}""")
# the History copy before the update's first write - ONCE per file (fix round): SNAPPED FALSE right after the copy is verified, so a
# failed write retried every 30 s never makes another copy; a copy that fails HIST_TRIES times in a row (config-history not writable)
# no longer blocks the player's shortcuts for good: written anyway with a warning (the old layout stays in the file itself: its exact
# bytes + _old)
M(lay, r"""
public static void snapFirst(String k, java.nio.file.Path f, String what) throws java.io.IOException {
  if (SNAPPED.containsKey(k) || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
  try {
    history(f, what, "before the SkyyMenu shortcuts update (the old layout also stays in the file)");
    SNAPPED.put(k, Boolean.FALSE);
    HFAIL.remove(k);
  } catch (Throwable t) {
    Object n = HFAIL.get(k);
    int c = (n instanceof Integer) ? ((Integer) n).intValue() + 1 : 1;
    HFAIL.put(k, Integer.valueOf(c));
    if (c < HIST_TRIES) throw new java.io.IOException("the History copy of " + what + " failed (" + t + ") - the file is not changed yet (try " + c + " of " + HIST_TRIES + ")");
    @PKG@.MenuUtil.warn("the History copy of " + what + " failed " + c + " times (" + t + ") - the update is written without it; the old layout stays in the file (its old lines are kept as they were, + _old)");
    SNAPPED.put(k, Boolean.FALSE);
  }
}""")
M(lay, r"""
public static byte[] readWas(java.nio.file.Path f) throws java.io.IOException {
  if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
  return java.nio.file.Files.readAllBytes(f);
}""")
# 0.3.30: the 5 x 5 update's config-changes.log line (status done: the old lines stay in the file above the appended ones; a rollback to
# 0.3.29 reads the same grid - there is nothing to undo in game, the pins only moved inside the grid or a page held twice was kept once)
M(lay, r"""
public static void logFold(String k, Object[] r) {
  try {
    @PKG@.CfgLog.add(null, "SkyyMenu update", "update", "menu.layout[" + k + "]", "7 x 5",
      "(0.3.30 the 5 x 5 shortcut grid: " + summary(r[0]) + (el(r, 7) != null ? "; no free slot (they wait in Edit shortcuts, + Add): " + el(r, 7) : "")
      + " - undo: the old lines stay in the file above the new ones, and the History copy made just before holds the whole old file)", "done");
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not log the menu layout update of " + k + " in config-changes.log: " + t); }
}""")
M(lay, r"""
public static void finishMig(String k, Object[] r, boolean mig) {
  SNAPPED.put(k, Boolean.TRUE);
  HFAIL.remove(k);
  if (mig) logMigration(k, r); else logFold(k, r);
}""")
M(lay, r"""
public static void writeOwn(String k) throws java.io.IOException {
  Object o = OWN.get(k);
  if (o == null || DIR == null) return;
  java.nio.file.Path f = DIR.resolve(k + ".properties");
  String what = "layouts/" + k + ".properties";
  if (BROKEN.remove(k) != null) keepBad(f);
  if (!(o instanceof Object[])) { java.nio.file.Files.deleteIfExists(f); return; }
  Object[] r = (Object[]) o;
  boolean mig = Boolean.TRUE.equals(r[4]) && !Boolean.TRUE.equals(SNAPPED.get(k));
  boolean fold = Boolean.TRUE.equals(el(r, 6)) && !Boolean.TRUE.equals(SNAPPED.get(k));   // 0.3.30
  if (mig || fold) snapFirst(k, f, what);
  byte[] was = readWas(f);
  if (empty(r)) java.nio.file.Files.deleteIfExists(f);
  else {
    Object nm = NAMES.get(k);
    if (nm == null) nm = r[5];
    String head = "# SkyyMenu: the SkyWynn Menu shortcuts of one player (account uuid " + k + ", the same for every profile).\n"
      + "# g.<slot> = the Home grid, t.<slot> = the Teleport grid: 5 x 5 = columns 1 - 5 of slot = row * 7 + column (17 = the centre). _home / _tp 0 = the default.\n"
      + "# _old and the tile=slot lines are the 0.3.28 layout (kept for a rollback). Change it in game: Home - Edit shortcuts. Delete this file = the defaults.\n"
      + "_name=" + @PKG@.MenuUtil.cleanName(nm == null ? "" : String.valueOf(nm)) + "\n";
    @PKG@.MenuUtil.atomicWrite(f, bytesFor(was, mig, fold, r, head));
  }
  if (mig || fold) finishMig(k, r, mig);
}""")
M(lay, r"""
public static void writeDef() throws java.io.IOException {
  java.nio.file.Path f = DEF_FILE;
  if (f == null) return;
  if (DEF_BROKEN) { DEF_BROKEN = false; keepBad(f); }
  Object[] d = DEF;
  if (d == null || (empty(d) && !Boolean.TRUE.equals(d[4]))) { java.nio.file.Files.deleteIfExists(f); return; }
  boolean mig = Boolean.TRUE.equals(d[4]) && !Boolean.TRUE.equals(SNAPPED.get(DEF_KEY));
  boolean fold = Boolean.TRUE.equals(el(d, 6)) && !Boolean.TRUE.equals(SNAPPED.get(DEF_KEY));   // 0.3.30
  if (mig || fold) snapFirst(DEF_KEY, f, "layout-default.properties");
  byte[] was = readWas(f);
  String head = "# SkyyMenu: the SERVER DEFAULT shortcuts - every player without their own gets them. g.<slot> = Home, t.<slot> = Teleport (5 x 5 = columns 1 - 5 of slot = row * 7 + column).\n"
    + "# Set in game by an admin: Home - Edit shortcuts - Set default. Delete this file = the standard shortcuts.\n";
  @PKG@.MenuUtil.atomicWrite(f, bytesFor(was, mig, fold, d, head));
  if (mig || fold) finishMig(DEF_KEY, d, mig);
}""")
M(lay, r"""
public static synchronized void saveNow(String k) {
  DIRTY.remove(k);
  try {
    if (DEF_KEY.equals(k)) writeDef(); else writeOwn(k);
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("could not save the menu shortcuts " + (DEF_KEY.equals(k) ? "layout-default.properties" : "layouts/" + k + ".properties") + " (kept in memory, retried every 30 s and at shutdown): " + t);
    DIRTY.put(k, Boolean.TRUE);
  }
}""")
# ---- LayoutSaveTask: the delayed save (saveNow writes the NEWEST state, so quick clicks give few writes); load = the join preload
M(lay, r"""
public static void saveSoon(String k) {
  DIRTY.put(k, Boolean.TRUE);
  if (!@PKG@.MenuIO.schedule(new @PKG@.LayoutSaveTask(k), 300L)) saveNow(k);
}""")
M(lay, r"""
public static Object own(String k) {
  Object o = OWN.get(k);
  if (o != null) return o;
  if (DIR == null) return NONE;
  Object at = ERRAT.get(k);
  if (at != null && System.currentTimeMillis() - ((Long) at).longValue() < 30000L) return ERR;
  Object r = readFile(DIR.resolve(k + ".properties"), "layouts/" + k + ".properties");
  if (ERR.equals(r)) { ERRAT.put(k, Long.valueOf(System.currentTimeMillis())); return ERR; }
  ERRAT.remove(k);
  if (r == null) r = NONE;
  else if (BAD.equals(r)) { BROKEN.put(k, Boolean.TRUE); r = NONE; }
  Object prev = OWN.putIfAbsent(k, r);
  if (prev != null) return prev;
  if (r instanceof Object[] && el((Object[]) r, 7) != null) {   // 0.3.30: pins that found no free slot in the 5 x 5 grid - the player is told once
    SPILL.putIfAbsent(k, el((Object[]) r, 7));   // fix: a second read never re-arms the one-time chat note
    @PKG@.MenuUtil.info("menu layout layouts/" + k + ".properties: " + el((Object[]) r, 7) + " - more shortcuts than the 25 slots; they wait in Edit shortcuts, + Add");
  }
  boolean fd = (r instanceof Object[]) && Boolean.TRUE.equals(el((Object[]) r, 6));
  if ((r instanceof Object[]) && (Boolean.TRUE.equals(((Object[]) r)[4]) || fd)) {
    SNAPPED.remove(k);    // fix round 2: a 0.3.28 file read again (an admin restored a .bak by hand) = a NEW update: History copy + append again
    HFAIL.remove(k);
    if (Boolean.TRUE.equals(((Object[]) r)[4])) {
      MIGRATED.put(k, Boolean.TRUE);
      MIGRATIONS = MIGRATIONS + 1;
      @PKG@.MenuUtil.info("menu layout layouts/" + k + ".properties: the 0.3.29 one-time update - hubs replace the old tiles they cover, the other tiles keep their place, Hover Tooltips goes (Settings has it); the old layout stays in the file (_old + the 0.3.28 lines) and a History copy goes to config-history first");
    } else {
      FOLDS = FOLDS + 1;
      @PKG@.MenuUtil.info("menu layout layouts/" + k + ".properties: the 0.3.30 one-time update - the 5 x 5 shortcut grid (pins of columns 0 and 6 moved in, a page held twice kept once): " + summary(((Object[]) r)[0]) + "; a History copy goes to config-history first, the old lines stay in the file");
    }
    saveSoon(k);
  }
  return r;
}""")
M(lay, r"""
public static boolean unreadable(java.util.UUID u) {
  return u != null && ERR.equals(own(u.toString()));
}""")
M(lay, r"""
public static Object[] rec(java.util.UUID u) {
  if (u == null) return null;
  Object o = own(u.toString());
  if (o instanceof Object[]) return (Object[]) o;
  return null;
}""")
# the _old line (tile=slot,...) -> int[entry] = 0.3.28 slot (-1 = none)
M(lay, r"""
public static int[] parseOldLine(String ol) {
  int[] old = new int[@PKG@.MenuData.E_VIEW.length];
  for (int i = 0; i < old.length; i++) old[i] = -1;
  if (ol == null) return old;
  String[] ps = ol.split(",");
  for (int j = 0; j < ps.length; j++) {
    int e = ps[j].indexOf('=');
    if (e <= 0) continue;
    int i = keyIndex(ps[j].substring(0, e).trim());
    int sl = slotOf(ps[j].substring(e + 1));
    if (i >= 0 && sl >= 0) old[i] = sl;
  }
  return old;
}""")
# fix round: the server default's one-time update, deferred from setup (loadDefault) to the first use after every mod published its hub
# tabs (a player's join / a page draw / an admin change): migrate() again with the hub check, then written (History copy first) once
M(lay, r"""
public static void settleDef() {
  if (!DEF_PENDING.compareAndSet(true, false)) return;
  Object[] d = DEF;
  if (d == null || d[2] == null || !Boolean.TRUE.equals(d[4])) return;
  Object[] nx = new Object[] { migrate(parseOldLine((String) d[2]), true), d[1], d[2], d[3], d[4], d[5], el(d, 6), el(d, 7) };
  DEF = nx;
  @PKG@.MenuUtil.info("menu layout layout-default.properties: the 0.3.29 one-time update of the server default (hubs whose pages are on this server replace the old tiles they cover; the old layout stays in the file; a History copy goes to config-history first): " + summary(nx[0]));
  saveSoon(DEF_KEY);
}""")
# the grid a player sees: their own, else the server default, else the built-in one (a copy - change it freely)
M(lay, r"""
public static String[] grid(java.util.UUID u, int part) {
  settleDef();
  Object[] r = rec(u);
  if (r != null && r[part] != null) return copy((String[]) r[part]);
  Object[] d = DEF;
  if (d != null && d[part] != null) return copy((String[]) d[part]);
  return builtin(part);
}""")
M(lay, r"""
public static String oldOf(java.util.UUID u) {
  Object[] r = rec(u);
  return r == null ? null : (String) r[2];
}""")
# "Old tiles back" (the in-game Undo of the one-time update): the _old line as tiles, each on its own mapped slot (no hubs)
M(lay, r"""
public static String[] oldTilesBack(java.util.UUID u) {
  String ol = oldOf(u);
  if (ol == null) return null;
  return migrate(parseOldLine(ol), false);
}""")
# fix round 2 (PROJECT-RULES 4 "a change-log line with Undo"): the SERVER DEFAULT's in-game Undo - admins, Home - Edit shortcuts - Old default:
# the server default's _old line as tiles on their mapped slots (no hubs); null = the server default has no 0.3.28 layout to bring back
M(lay, r"""
public static boolean hasOldDefault() {
  Object[] d = DEF;
  return d != null && d.length > 2 && d[2] != null;
}""")
M(lay, r"""
public static String[] oldDefaultBack() {
  settleDef();
  Object[] d = DEF;
  if (d == null || d[2] == null) return null;
  return migrate(parseOldLine((String) d[2]), false);
}""")
M(lsv, r"""
public void run() {
  try {
    if (this.load) @PKG@.MenuLayout.own(this.k);
    else @PKG@.MenuLayout.saveNow(this.k);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu shortcuts " + (this.load ? "preload" : "save") + " failed: " + t); }
}""")
M(lay, r"""
public static void preload(java.util.UUID u) {
  try {
    settleDef();
    if (u == null || DIR == null) return;
    String k = u.toString();
    if (OWN.containsKey(k)) return;
    if (!@PKG@.MenuIO.schedule(new @PKG@.LayoutSaveTask(k, true), 0L)) @PKG@.MenuUtil.warn("could not schedule the menu shortcuts preload (SkyyMenu-IO stopped)");
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule the menu shortcuts preload: " + t); }
}""")
# a change (world thread: memory + a scheduled save): part 0 Home / 1 Teleport; g = the new grid, null = back to the default. 1 = done.
M(lay, r"""
public static int put(java.util.UUID u, String name, int part, String[] g) {
  if (u == null || part < 0 || part > 1) return 0;
  String k = u.toString();
  Object o = own(k);
  if (ERR.equals(o)) return 0;
  Object[] nx = new Object[] { null, null, null, null, Boolean.FALSE, null, Boolean.FALSE, null };
  if (o instanceof Object[]) {
    Object[] r = (Object[]) o;
    for (int i = 0; i < nx.length && i < r.length; i++) nx[i] = r[i];
  }
  nx[part] = null;
  if (g != null) nx[part] = copy(g);
  if (name != null) NAMES.put(k, name);
  DIRTY.put(k, Boolean.TRUE);
  OWN.put(k, nx);
  saveSoon(k);
  return 1;
}""")
M(lay, r"""
public static int saveDefault(int part, String[] g) {
  if (part < 0 || part > 1 || g == null) return 0;
  settleDef();
  Object[] d = DEF;
  Object[] nx = new Object[] { null, null, null, null, Boolean.FALSE, null, Boolean.FALSE, null };
  if (d != null) { for (int i = 0; i < 5 && i < d.length; i++) nx[i] = d[i]; nx[6] = el(d, 6) == null ? Boolean.FALSE : el(d, 6); }
  nx[part] = copy(g);
  DEF = nx;
  saveSoon(DEF_KEY);
  return 1;
}""")
M(lay, r"""
public static int clearDefault(int part) {
  if (part < 0 || part > 1) return 0;
  settleDef();
  Object[] d = DEF;
  if (d == null) { saveSoon(DEF_KEY); return 1; }
  Object[] nx = new Object[] { d[0], d[1], d[2], d[3], d[4], null, el(d, 6) == null ? Boolean.FALSE : el(d, 6), null };
  nx[part] = null;
  if (empty(nx) && !Boolean.TRUE.equals(nx[4])) DEF = null;
  else DEF = nx;
  saveSoon(DEF_KEY);
  return 1;
}""")
# at start (setup, after MenuIO.begin): the server default file -> DEF (a 0.3.28 file is updated once: settleDef at the first join)
M(lay, r"""
public static void loadDefault() {
  DEF_PENDING.set(false);
  Object r = readFile(DEF_FILE, "layout-default.properties");
  DEF_BROKEN = BAD.equals(r);
  if (r instanceof Object[]) {
    DEF = (Object[]) r;
    if (!Boolean.TRUE.equals(DEF[4]) && Boolean.TRUE.equals(el(DEF, 6))) {   // 0.3.30: the server default's 5 x 5 update (written once)
      SNAPPED.remove(DEF_KEY);
      HFAIL.remove(DEF_KEY);
      FOLDS = FOLDS + 1;
      @PKG@.MenuUtil.info("menu layout layout-default.properties: the 0.3.30 one-time update of the server default - the 5 x 5 grid: " + summary(DEF[0]));
      saveSoon(DEF_KEY);
    }
    if (Boolean.TRUE.equals(DEF[4])) {
      SNAPPED.remove(DEF_KEY);    // fix round 2: a 0.3.28 default (again) = a new update with its own History copy
      HFAIL.remove(DEF_KEY);
      MIGRATIONS = MIGRATIONS + 1;
      DEF_PENDING.set(true);
      @PKG@.MenuUtil.info("menu layout layout-default.properties: a 0.3.28 server default - its 0.3.29 one-time update runs when the first player joins (every mod has published its hub tabs by then)");
    }
  } else DEF = null;
  @PKG@.MenuUtil.info("menu shortcuts: " + (DEF != null ? "the server default from layout-default.properties" : "the standard shortcuts are the server default") + "; players' own shortcuts in layouts/");
}""")
M(lay, r"""
public static void flushAll() {
  java.util.ArrayList ks = new java.util.ArrayList(DIRTY.keySet());
  for (int i = 0; i < ks.size(); i++) saveNow((String) ks.get(i));
}""")
M(lay, r"""
public static synchronized void pruneOffline(java.util.Set onlineK) {
  java.util.ArrayList ks = new java.util.ArrayList(OWN.keySet());
  for (int i = 0; i < ks.size(); i++) {
    String k = (String) ks.get(i);
    if (onlineK.contains(k) || DIRTY.containsKey(k)) continue;
    Object v = OWN.get(k);
    if (v == null || !OWN.remove(k, v)) continue;
    if (DIRTY.containsKey(k)) { OWN.putIfAbsent(k, v); continue; }
    NAMES.remove(k);
  }
  java.util.ArrayList es = new java.util.ArrayList(ERRAT.keySet());
  for (int i = 0; i < es.size(); i++) { if (!onlineK.contains(es.get(i))) ERRAT.remove(es.get(i)); }
  java.util.ArrayList ms = new java.util.ArrayList(MIGRATED.keySet());
  for (int i = 0; i < ms.size(); i++) { if (!onlineK.contains(ms.get(i))) MIGRATED.remove(ms.get(i)); }
  java.util.ArrayList sps = new java.util.ArrayList(SPILL.keySet());
  for (int i = 0; i < sps.size(); i++) { if (!onlineK.contains(sps.get(i))) SPILL.remove(sps.get(i)); }
}""")

# ================= 0.3.28 MenuHub part 1: hub:last + the hub click helper (the pages use these; part 2 opens pages, after them) =========
# hub:last:<uuid> = a java.util.Map (hub -> last tab) on the bridge, MEMORY ONLY (spec 2.1): made at join (MenuReady) and whenever a hub
# page draws (ensure), removed on disconnect (MenuQuit), for players gone (SeenTick, a fresh online list) and at shutdown. LAST = the uuids
# whose map THIS mod made (forget removes only a key that still holds our map). Every HubBar.build (any mod) writes into it.
F(mhub, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
M(mhub, r"""
public static java.util.Map ensure(java.util.UUID u) {
  if (u == null) return null;
  try {
    java.util.Map br = @PKG@.MenuUtil.bridge();
    String k = "hub:last:" + u.toString();
    Object o = br.get(k);
    if (o == null) {
      java.util.concurrent.ConcurrentHashMap m = new java.util.concurrent.ConcurrentHashMap();
      Object prev = br.putIfAbsent(k, m);
      o = prev == null ? m : prev;
    }
    if (!(o instanceof java.util.Map)) return null;
    LAST.put(u, o);
    return (java.util.Map) o;
  } catch (Throwable t) { return null; }
}""")
M(mhub, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  Object mine = LAST.remove(u);
  if (mine == null) return;
  try { @PKG@.MenuUtil.bridge().remove("hub:last:" + u.toString(), mine); } catch (Throwable t) { }
}""")
M(mhub, r"""
public static int sweep(java.util.Set online) {
  java.util.Set base = @PKG@.SoundSw.live();
  if (base == null) base = online;
  if (base == null) return 0;
  java.util.ArrayList ks = new java.util.ArrayList(LAST.keySet());
  int n = 0;
  for (int i = 0; i < ks.size(); i++) {
    Object o = ks.get(i);
    if (!base.contains(o)) { forget((java.util.UUID) o); n = n + 1; }
  }
  return n;
}""")
M(mhub, r"""
public static int clearAll() {
  java.util.ArrayList ks = new java.util.ArrayList(LAST.keySet());
  for (int i = 0; i < ks.size(); i++) forget((java.util.UUID) ks.get(i));
  return @PKG@.HubBar.removeAll();
}""")
M(mhub, r"""
public static int hubIndex(String hub) {
  if (hub == null) return -1;
  for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) { if (@PKG@.MenuData.HUB_ID[i].equals(hub)) return i; }
  return -1;
}""")
# the visible rule of Menu's own tabs (the TILE_RULES of the Mods / Server Setup tiles): mods = admins, or everyone while menu.modsHelp is
# on; setup = admins (the Server Setup page re-checks its node on every click - its own guard)
M(mhub, r"""
public static boolean visible(String tab, @PR@ pr) {
  if (tab == null) return false;
  if (tab.equals("setup")) return @PKG@.MenuUtil.isAdmin(pr);
  if (tab.equals("mods")) return @PKG@.MenuUtil.isAdmin(pr) || @PKG@.MenuCfg.MODS_HELP;
  return true;
}""")
M(mhub, r"""
public static boolean opened(String r) {
  return "back".equals(r) || "bridge".equals(r) || "command".equals(r);
}""")
# a page's click: null = not a hub click; "close" (the X); "menu" (< Menu: the page opens the SkyWynn Menu itself - never /skymenu, which
# would also hand out a lost menu item); else HubBar.handle's answer ("self", "bridge", "command", "hidden", "missing", "nocmd", "failed")
M(mhub, r"""
public static String click(@PR@ pr, String data, String hub, String tab) {
  if (data == null || data.indexOf("\"hub:") < 0) return null;
  String a = @PKG@.HubBar.jsonStr(data, "a");
  if (!a.startsWith("hub:")) return null;
  if (a.equals("hub:back") || a.equals("hub:h:home")) return "menu";   // 0.3.29: row 1's Home = the Home page (never /skymenu)
  return @PKG@.HubBar.route(pr, data, hub, tab);                      // 0.3.29: kit 1.6 - row 1 (hub:h:<hub>), then the tabs / the X
}""")
# the tab a hub command opens: the hub's last tab while it is still shown to this player, else the first shown tab; null = none yet
M(mhub, r"""
public static String pick(String hub, java.util.UUID u) {
  return @PKG@.HubBar.pickTab(hub, u);   // 0.3.29: the hub's default tab (Character -> Skills), else the last tab, else the first
}""")

# ================= MenuPage (inline page; views switched with rebuild()) =================
for f in ("public String view;", "public int pageNo;", "public java.util.UUID selU;", "public String[] acts;", "public String[] names;",
          "public String[] bodies;", "public String infoName;", "public String infoBody;", "public String status;", "public String title;",
          "public int pages;", "public boolean cleared;", "public String cfgArm;"):
    F(page, f)
# 0.3.6: the world the menu was first built in (openCustomPage) + the player's world joins then (PageGuard.JOINS), the send time of its
# last packet (the check waits SETTLE after it), the safety net's state. A client acknowledges a page packet within a few frames, so 1 s
# later a test click the engine still drops means the acknowledgements are stuck. At most HEAL_ANSWERS answers per menu.
F(page, "public @WLD@ world;")
F(page, "public int joinSeen;")
F(page, "public volatile long lastSend;")
F(page, "public boolean watching;")
F(page, "public String probeNonce;")
F(page, "public boolean probeSeen;")
F(page, "public int heals;")
F(page, "public int watchFails;")
# 0.3.19 E: healthy = test clicks that arrived in a row with nothing sent since (watchDelay backs off), seenSend = the lastSend those saw
F(page, "public int healthy;")
F(page, "public long seenSend;")
F(page, "public static final long SETTLE = 1000L;")
F(page, "public static final int HEAL_ANSWERS = 3;")
# 0.3.17: the layout editor - editing (main view only), editSel = the slot of the picked-up tile (-1 = none), lay = the layout drawn
# (MenuLayout.of), occ = slot -> entry index of the tile there (hidden tiles too, -1 = empty), hid = the slot of a tile this player
# cannot see (a Kept slot in edit mode). lay / occ / hid are made by fillStatic on every draw of the main view.
for f in ("public boolean editing;", "public int editSel;", "public boolean[] hid;",
          "public String[] ihs;", "public String[] zhs;", "public java.util.HashMap wth;", "public String[] autoAt;"):   # 0.3.37: island homes, homes, warp themes, the auto tile of each slot (Arrange)   # 0.3.29: lay / occ went with the 9 x 6 main view
    F(page, f)
# 0.3.29: Home / Teleport - grid = the keys drawn (35), gridN = the slots of the grid on screen (35 on Home / Teleport, 54 in the classic
# views), addSlot = the empty slot the + Add list fills (-1 = no list), addPage / addPages / addKeys = that list, alertT = Right now's targets
for f in ("public String[] grid;", "public int gridN;", "public int addSlot;", "public int addPage;", "public int addPages;",
          "public String[] addKeys;", "public String[] alertT;"):
    F(page, f)
C(page, r"""
public MenuPage(@PR@ pr, String view) {
  super(pr, @LIFE@.CanDismiss);
  this.view = view == null ? "main" : view;
  this.pageNo = 0;
  this.status = "";
  this.pages = 1;
  this.editing = false;
  this.editSel = -1;
  this.addSlot = -1;
  this.gridN = 54;
}""")
# 0.2 SettingsPage fields + constructor right here (javassist: MenuPage.openSettings and the page's "< SkyWynn Menu" button use each
# other's constructors - the SkyyHud WidgetsPage / EditorPage pattern: constructors first, methods after). cat -1 = the first tab with rows.
for f in ("public int cat;", "public int pageNo;", "public String status;", "public long armedAt;", "public String[] rowKeys;",
          "public boolean drained;", "public String search;", "public String findDraft;", "public int[] findTabs;"):   # 0.3.25: + the search
    F(spg, f)
C(spg, r"""
public SettingsPage(@PR@ pr, int cat) {
  super(pr, @LIFE@.CanDismiss);
  this.cat = cat;
  this.pageNo = 0;
  this.status = "";
  this.armedAt = 0L;
  this.rowKeys = new String[@PKG@.MenuData.SET_ROWS];
  this.drained = false;
  this.search = "";
  this.findDraft = "";
  this.findTabs = new int[0];
}""")
# 0.3.10 StatsPage fields + constructor here too (MenuPage.openStats and the page's "< SkyWynn Menu" button use each other's
# constructors). tab = 0 Main, 1 Combat, 2 Gathering, 3 Skills, 4 Profile.
for f in ("public int tab;", "public String status;"):
    F(stp, f)
C(stp, r"""
public StatsPage(@PR@ pr, int tab) {
  super(pr, @LIFE@.CanDismiss);
  this.tab = tab < 0 || tab >= @PKG@.StatsCalc.TABS.length ? 0 : tab;
  this.status = "";
}""")
# 0.3 AdminPage fields + constructor right here too (MenuPage.openAdmin and the page's "< SkyWynn Menu" button use each other's
# constructors - constructors first, methods after). View = list / mod / table / confirm / log / hist / io (spec 2.3).
for f in ("public String view;", "public String mod;", "public int cat;", "public int listPage;", "public int modPage;", "public int tPage;",
          "public int logPage;", "public int histPage;", "public String tableKey;", "public String tFilter;", "public String tFilterDraft;",
          "public String findDraft;", "public String status;", "public int statusKind;", "public boolean showAdv;", "public java.util.HashMap drafts;",
          "public Object[] pending;", "public String pendingMod;", "public String pendingMsg;", "public int pendingKind;",
          "public java.util.ArrayList pendingCodes;", "public String[] rowKeys;", "public String backView;", "public String search;",
          "public boolean locked;", "public boolean jumpHit;", "public String[] listMods;", "public String[] listReload;", "public String[] tKeys;",
          "public String[] listJump;", "public int jumpRow;",   # 0.3.25: a search result's target (r<row> / c<tab>), the row to show
          "public String[] tVals;", "public java.util.HashMap tDrafts;", "public String[] tAdd;", "public java.util.ArrayList items;",
          "public String histFile;", "public String[] histIds;", "public String[] histFiles;", "public String histPreview;", "public String logMod;",
          "public java.util.ArrayList logShown;", "public String[] logTabs;", "public boolean ioAll;", "public String ioScope;", "public String ioCode;",
          "public String ioImport;", "public String ioPreview;", "public String ioPreviewCode;", "public java.util.ArrayList ioPlan;",
          "public int ioPlanTotal;", "public String[] ioFiles;", "public java.util.ArrayList evKeys;", "public java.util.ArrayList evSels;",
          "public java.util.ArrayList fT;", "public java.util.ArrayList fA;", "public java.util.ArrayList fW;",
          "public int rowSz;", "public java.util.HashSet boxRows;"):   # 0.3.36: the mod view's grow tier + its rows with a text box
    F(apg, f)
C(apg, r"""
public AdminPage(@PR@ pr, String view, String mod) {
  super(pr, @LIFE@.CanDismiss);
  this.view = view == null ? "list" : view;
  this.mod = mod;
  this.cat = 0;
  this.listPage = 0;
  this.modPage = 0;
  this.tPage = 0;
  this.logPage = 0;
  this.histPage = 0;
  this.tableKey = null;
  this.tFilter = "";
  this.tFilterDraft = "";
  this.findDraft = "";
  this.status = "";
  this.statusKind = 0;
  this.showAdv = false;
  this.drafts = new java.util.HashMap();
  this.pending = null;
  this.pendingMod = null;
  this.pendingMsg = "";
  this.pendingKind = 0;
  this.pendingCodes = null;
  this.rowKeys = new String[@MD@.ADM_ROWS];
  this.backView = "list";
  this.search = "";
  this.locked = false;
  this.jumpHit = false;
  this.listMods = new String[@MD@.ADM_LROWS];
  this.listReload = new String[@MD@.ADM_LROWS];
  this.listJump = new String[@MD@.ADM_LROWS];
  this.jumpRow = -1;
  this.tKeys = new String[@MD@.ADM_ROWS];
  this.tVals = new String[@MD@.ADM_ROWS];
  this.tDrafts = new java.util.HashMap();
  this.tAdd = new String[4];
  this.items = new java.util.ArrayList();
  this.histFile = "";
  this.histIds = new String[@MD@.ADM_HROWS];
  this.histFiles = new String[0];
  this.histPreview = null;
  this.logMod = "";
  this.logShown = new java.util.ArrayList();
  this.logTabs = new String[0];
  this.ioAll = false;
  this.ioScope = "changed";
  this.ioCode = null;
  this.ioImport = "";
  this.ioPreview = null;
  this.ioPreviewCode = null;
  this.ioPlan = new java.util.ArrayList();
  this.ioPlanTotal = 0;
  this.ioFiles = new String[0];
  this.evKeys = new java.util.ArrayList();
  this.evSels = new java.util.ArrayList();
  this.fT = new java.util.ArrayList();
  this.fA = new java.util.ArrayList();
  this.fW = new java.util.ArrayList();
}""")

# ================= 0.3.23 OpsPage (the Admin page): data, fields, constructor (methods after the AdminPage section) =================
F(ops, "public static final String[] O_TABS = %s;" % jarr(OPS_TABS))
F(ops, "public static final int O_DIAG = %d;" % OPS_DIAG)
F(ops, "public static final int[] O_TAB = %s;" % jints([o[0] for o in OPS]))
F(ops, "public static final String[] O_LABEL = %s;" % jarr([o[1] for o in OPS]))
F(ops, "public static final String[] O_LINE = %s;" % jarr([o[2] for o in OPS]))
F(ops, "public static final String[] O_NODE = %s;" % jarr([o[3] for o in OPS]))
F(ops, "public static final String[] O_MOD = %s;" % jarr([o[4] for o in OPS]))
F(ops, "public static final boolean[] O_CONF = %s;" % jbools([o[5] for o in OPS]))
F(ops, "public static final int[] O_DEPTH = %s;" % jints([ops_depth(o[2]) for o in OPS]))
F(ops, "public static final boolean[] O_EXTRA = %s;" % jbools([o[2].split(" ")[0] in OPS_EXTRA_ROOTS for o in OPS]))
F(ops, "public static final String[] O_HINT = %s;" % jarr([o[6] for o in OPS]))
F(ops, "public static final String[] O_STAT = %s;" % jarr([o[7] for o in OPS]))
F(ops, "public static final String[] O_HELP = %s;" % jarr([ops_help(o) for o in OPS]))
F(ops, "public static final String[] O_SUBN = %s;" % jarr([SUI.render(m) for m in OPS_SUBMK[0]]))   # 0.3.36: the sub-tab row
F(ops, "public static final String[] O_SUBS = %s;" % jarr([SUI.render(m) for m in OPS_SUBMK[1]]))
F(ops, "public static final String O_SUBGAP = %s;" % jstr(OPS_SUBMK[2]))
F(ops, "public static final String[] O_SETMOD = %s;" % jarr([m for m, v in OPS_SET]))
F(ops, "public static final String[] O_SETVER = %s;" % jarr([v for m, v in OPS_SET]))
F(ops, "public static final int LIST_IN = %d;" % OPS_LIST_IN)            # 0.3.36: one scroll list - its room + the row sizes (rule 7)
F(ops, "public static final int[] O_ROWH = %s;" % jints(OPS_ROW_H))
F(ops, "public static final int ROW_GAP = %d;" % OPS_ROW_GAP)
F(ops, "public static final int LINE_H = %d;" % (OPS_LINE_H + OPS_LINE_GAP))
F(ops, "public static final int LINE_MAX = %d;" % OPS_LINE_MAX)
F(ops, "public static final int TEXT_MAX = %d;" % OPS_TEXT_MAX)
F(ops, "public static final long CONFIRM_MS = %dL;" % OPS_CONFIRM_MS)
F(ops, "public static final long DOUBLE_MS = %dL;" % OPS_DOUBLE_MS)
F(ops, "public static final String SUB = %s;" % jstr(OPS_SUB))
F(ops, "public static final String NOACCESS = %s;" % jstr(OPS_NOACCESS))
for f in ("public int tab;", "public int pg;", "public String arg;", "public String pick;", "public String info;", "public int armed;",
          "public long armedAt;", "public String armedLine;", "public int lastI;", "public long lastAt;", "public String lastLine;", "public boolean field;", "public java.util.Map test;"):
    F(ops, f)
C(ops, r"""
public OpsPage(@PR@ pr, int tab) {
  super(pr, @LIFE@.CanDismiss);
  this.tab = tab < 0 || tab >= O_TABS.length ? 0 : tab;
  this.pg = 0;
  this.arg = "";
  this.pick = null;
  try { this.pick = pr == null ? null : pr.getUsername(); } catch (Throwable t) { this.pick = null; }
  this.info = "";
  this.armed = -1;
  this.armedAt = 0L;
  this.armedLine = "";
  this.lastI = -1;
  this.lastAt = 0L;
  this.lastLine = "";
  this.field = false;
  this.test = null;
}""")

# ================= 0.3 AdmSaveTask: export copies written on the scheduler (never on the world thread) + the imports folder =================
ast.addInterface(pool.get("java.lang.Runnable"))
F(ast, "public static java.nio.file.Path BASE;")
F(ast, "public String name;")
F(ast, "public String text;")
C(ast, "public AdmSaveTask(String name, String text) { this.name = name; this.text = text; }")
# only ever exports/<one file name>: the same refusal readImport has (no / \ .. : in the file name), and the resolved file must sit
# directly in exports/ (defence in depth behind AdminPage.validMod, which keeps odd <Mod> names off the page)
M(ast, r"""
public static boolean okExport(String name) {
  if (BASE == null || name == null || !name.startsWith("exports/")) return false;
  String fn = name.substring(8);
  if (fn.length() == 0 || fn.length() > 120 || fn.indexOf('/') >= 0 || fn.indexOf('\\') >= 0 || fn.indexOf("..") >= 0 || fn.indexOf(':') >= 0) return false;
  try {
    java.nio.file.Path dir = BASE.resolve("exports").toAbsolutePath().normalize();
    java.nio.file.Path f = dir.resolve(fn).normalize();
    return dir.equals(f.getParent());
  } catch (Throwable t) { return false; }
}""")
M(ast, r"""
public void run() {
  try {
    if (BASE == null || this.name == null || this.text == null) return;
    if (!okExport(this.name)) { @PKG@.MenuUtil.warn("Server Setup refused to save " + this.name + " - only a plain file name inside Skyy_SkyyMenu/exports/ is written"); return; }
    java.nio.file.Path f = BASE.resolve(this.name);
    @PKG@.MenuUtil.atomicWrite(f, this.text.getBytes("UTF-8"));
    @PKG@.MenuUtil.info("Server Setup saved Skyy_SkyyMenu/" + this.name);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("Server Setup could not save Skyy_SkyyMenu/" + this.name + ": " + t); }
}""")
M(ast, r"""
public static void save(String name, String text) {
  if (!@PKG@.MenuIO.schedule(new @PKG@.AdmSaveTask(name, text), 0L)) new @PKG@.AdmSaveTask(name, text).run();
}""")
M(ast, r"""
public static void ensureDirs() {
  try {
    if (BASE == null) return;
    java.nio.file.Files.createDirectories(BASE.resolve("imports"), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.createDirectories(BASE.resolve("exports"), new java.nio.file.attribute.FileAttribute[0]);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not create Skyy_SkyyMenu/imports and exports: " + t); }
}""")
M(ast, r"""
public static String[] importFiles() {
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    if (BASE == null) return new String[0];
    java.nio.file.Path d = BASE.resolve("imports");
    if (!java.nio.file.Files.isDirectory(d, new java.nio.file.LinkOption[0])) return new String[0];
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(d);
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext() && out.size() < 200) {
        java.nio.file.Path p = (java.nio.file.Path) it.next();
        String n = p.getFileName().toString();
        if (n.toLowerCase().endsWith(".txt") && java.nio.file.Files.isRegularFile(p, new java.nio.file.LinkOption[0])) out.add(n);
      }
    } finally { ds.close(); }
  } catch (Throwable t) { }
  java.util.Collections.sort(out);
  return (String[]) out.toArray(new String[0]);
}""")
M(ast, r"""
public static String readImport(String name) {
  try {
    if (BASE == null || name == null || name.indexOf('/') >= 0 || name.indexOf('\\') >= 0 || name.indexOf("..") >= 0) return null;
    java.nio.file.Path p = BASE.resolve("imports").resolve(name);
    if (java.nio.file.Files.size(p) > 1048576L) return null;
    return new String(java.nio.file.Files.readAllBytes(p), "UTF-8");
  } catch (Throwable t) { return null; }
}""")
# public wrapper so RefreshTask (another class) can rebuild - CustomUIPage.rebuild() is protected
M(page, r"""
public void refresh() { rebuild(); }""")
# 0.3.6 (before RefreshTask / CloseTask, which use them): the page's player for MenuWatch (playerRef is a protected engine field);
# did the player change world since this menu was opened? - the world of its first build differs from `now`, or PageGuard counted a
# world join of that player since (a re-join of the same world counts too). Without a first build (no world known) only the join count.
M(page, r"""
public @PR@ who() { return this.playerRef; }""")
M(page, r"""
public boolean changedWorld(@WLD@ now) {
  if (this.world != null && now != null && now != this.world) return true;
  return this.watching && this.joinSeen != @PKG@.PageGuard.joins(this.playerRef.getUuid());
}""")
# one [SkyyMenu] line for the first failure of a menu's check, then quiet retries; it gives up after 30 (the menu still works)
M(page, r"""
public boolean watchFail(Throwable t) {
  this.watchFails = this.watchFails + 1;
  if (this.watchFails == 1) @PKG@.MenuUtil.warn("the menu page check for " + @PKG@.PageGuard.who(this.playerRef) + " failed (retried quietly): " + t);
  return this.watchFails < 30;
}""")

# ================= RefreshTask: re-draw the menu shortly after a keep-open command ran (world thread) =================
# 0.3.6: a menu the player no longer sees after a world change is forgotten (PageGuard.forget, no packet), never redrawn: a redraw of
# a page the client dropped is +1 page acknowledgement the client never sends (every page would ignore clicks)
ref_.addInterface(pool.get("java.lang.Runnable"))
F(ref_, "public @PKG@.MenuPage page;")
F(ref_, "public @PR@ pr;")
F(ref_, "public @WLD@ expected;")
C(ref_, r"""
public RefreshTask(@PKG@.MenuPage page, @PR@ pr) { this.page = page; this.pr = pr; this.expected = null; }""")
M(ref_, r"""
public static void schedule(@PKG@.MenuPage page, @PR@ pr, long ms) {
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.RefreshTask(page, pr), ms, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule a menu refresh: " + t); }
}""")
M(ref_, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    if (this.expected == null) {
      java.util.UUID wu = this.pr.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) return;
      this.expected = w;
      w.execute(this);
      return;
    }
    java.util.UUID wu2 = this.pr.getWorldUuid();
    if (wu2 == null || @UNI@.get().getWorld(wu2) != this.expected) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    @PGM@ pm = p.getPageManager();
    if (pm == null || pm.getCustomPage() != this.page) return;
    if (this.page.changedWorld(this.expected)) {
      if (@PKG@.PageGuard.forget(pm, r, st, this.page)) @PKG@.MenuUtil.info("the menu redraw after a command found the menu of " + @PKG@.PageGuard.who(this.pr) + " still open on the server after a world change - forgot it there too instead of redrawing it (no packet)");
      return;
    }
    this.page.refresh();
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu refresh failed: " + t); }
}""")

# ---- MenuPage helpers (callees first)
M(page, r"""
public static @IGS@ filler() {
  if (@PKG@.MenuData.FILLER == null) return new @IGS@();
  @IGS@ g = new @IGS@(new @IS@(@PKG@.MenuData.FILLER, 1));
  g.setName(" ");
  g.setActivatable(false);
  g.setSkipItemQualityBackground(true);
  return g;
}""")
M(page, r"""
public void put(java.util.ArrayList slots, int idx, String icon, String name, String body, String foot, String act, boolean dim) {
  if (idx < 0 || idx >= 54 || idx >= slots.size()) return;   // 0.3.29: Home / Teleport have 35 slots
  try {
    @IGS@ gs = new @IGS@(new @IS@(icon, 1));
    gs.setName(name);
    gs.setDescription(@PKG@.MenuData.tooltip(body, foot, dim));
    gs.setActivatable(act != null);
    if (dim) gs.setItemIncompatible(true);
    gs.setSkipItemQualityBackground(true);
    slots.set(idx, gs);
    this.acts[idx] = act;
    this.names[idx] = name;
    this.bodies[idx] = body;
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not draw menu slot " + idx + " (" + icon + "): " + t); }
}""")
# page count for n items shown `per` at a time; clamps this.pageNo
M(page, r"""
public int paging(int n, int per) {
  int p = n <= 0 ? 1 : (n + per - 1) / per;
  if (this.pageNo >= p) this.pageNo = p - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  return p;
}""")
M(page, r"""
public String purseText() {
  long v = @PKG@.MenuUtil.purse(this.playerRef.getUuid());
  return v < 0L ? "SkyyCoins is not installed" : @PKG@.MenuUtil.fmt(v) + " coins";
}""")
M(page, r"""
public String bankText() {
  long v = @PKG@.MenuUtil.bank(this.playerRef.getUuid());
  return v < 0L ? "not loaded yet - open the Bank" : @PKG@.MenuUtil.fmt(v) + " coins";
}""")
# 0.3.10: short lines (the info box's lines are 20 px, unwrapped, about 80 characters: the 0.3.9 "Skills:" list was cut off) - every
# detail line clipped to StatsCalc.LINE_MAX; the whole list is on the Stats page the tile opens
M(page, r"""
public String profileBody() {
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map br = @PKG@.MenuUtil.bridge();
  int max = @PKG@.StatsCalc.LINE_MAX;
  StringBuilder sb = new StringBuilder();
  sb.append("Your SkyWynn profile, ").append(@PKG@.MenuUtil.safe(this.playerRef.getUsername())).append(". Click for all your stats.");
  String cls = @PKG@.StatsCalc.className(u);
  int ov = @PKG@.StatsCalc.overall(u);
  sb.append("\n").append(@PKG@.MenuUtil.clip("Class: " + (cls == null ? "none yet" : cls) + (ov >= 0 ? "   -   Overall Level " + ov : ""), max));
  sb.append("\n").append(@PKG@.MenuUtil.clip("Purse: " + purseText(), max));
  long bk = @PKG@.MenuUtil.bank(u);
  sb.append("\n").append(@PKG@.MenuUtil.clip("Bank: " + (bk < 0L ? "open the Bank to load it" : @PKG@.MenuUtil.fmt(bk) + " coins"), max));
  String top = @PKG@.StatsCalc.topSkills(u, 3);
  sb.append("\n").append(@PKG@.MenuUtil.clip("Top skills: " + (top == null ? "no skill data yet" : top), max));
  sb.append("\n").append(@PKG@.MenuUtil.clip("Void Charms: " + @PKG@.MenuUtil.csvCount(br.get("acc:has:" + u.toString())) + " accessories, "
    + @PKG@.MenuUtil.csvCount(br.get("acc:tal:" + u.toString())) + " talismans", max));
  sb.append("\n").append(@PKG@.MenuUtil.clip("Recipes unlocked by collections: " + @PKG@.MenuUtil.csvCount(br.get("coll:recipes:" + u.toString())), max));
  return sb.toString();
}""")
# the command an action would run (for greying out entries whose mod is missing)
M(page, r"""
public static String cmdOf(String act) {
  if (act == null) return null;
  if (act.startsWith("cmd:")) return @PKG@.MenuUtil.firstWord(act.substring(4));
  if (act.startsWith("cmdc:")) return @PKG@.MenuUtil.firstWord(act.substring(5));
  return null;
}""")
M(page, r"""
public static String lineOf(String act) {
  if (act == null) return null;
  if (act.startsWith("cmd:")) return act.substring(4);
  if (act.startsWith("cmdc:")) return act.substring(5);
  return null;
}""")
# 0.3.29: the 0.3.17 edit-mode tiles of the 9 x 6 main view are retired (Home: editTile2 / emptyMark)
# 0.3.16: THE PER-TILE VISIBILITY RULE (TILE_RULES -> MenuData E_PERM / E_OPEN / E_NEED / E_UNLOCK). perm: the node (ADMIN_NODE = the
# admin check fillStatic already made; another node = PlayerRef.hasPermission, fail closed), unless the named Server Setup switch opens
# the tile to everyone; need: the bridge key holds a Function; unlock: while the key holds a Function, apply(UUID) must answer TRUE (an
# absent key = shown; a throw = hidden + one warning per key). Runs on the world thread while the menu is drawn.
M(page, r"""
public boolean tileVisible(int i, boolean admin) {
  String perm = @PKG@.MenuData.E_PERM[i];
  if (perm.length() > 0) {
    boolean ok = false;
    if (perm.equals(@PKG@.MenuData.ADMIN_NODE)) ok = admin;
    else {
      try { ok = this.playerRef.hasPermission(perm); } catch (Throwable t) { ok = false; }
    }
    String open = @PKG@.MenuData.E_OPEN[i];
    if (!ok && "modsHelp".equals(open) && @PKG@.MenuCfg.MODS_HELP) ok = true;
    if (!ok) return false;
  }
  java.util.Map br = @PKG@.MenuUtil.bridge();
  String need = @PKG@.MenuData.E_NEED[i];
  if (need.length() > 0 && !(br.get(need) instanceof java.util.function.Function)) return false;
  String un = @PKG@.MenuData.E_UNLOCK[i];
  if (un.length() == 0) return true;
  Object f = br.get(un);
  if (!(f instanceof java.util.function.Function)) return true;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(this.playerRef.getUuid()); }
  catch (Throwable t) {
    r = null;
    if (@PKG@.MenuData.TILE_WARNED.putIfAbsent(un, un) == null) @PKG@.MenuUtil.warn("the menu tile unlock check " + un + " failed (the tile stays hidden): " + t);
  }
  return Boolean.TRUE.equals(r);
}""")
# 0.3.29: fillStatic (the classic views' fixed entries) is defined after tileLook
# 0.3.29: the 0.3.28 warp filler is retired (the Teleport grid page fills its warps: fillAutoWarps)
M(page, r"""
public void fillPlayers(java.util.ArrayList slots) {
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.UUID me = this.playerRef.getUuid();
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ p = (@PR@) it.next();
    if (p == null || !p.isValid() || me.equals(p.getUuid())) continue;
    String n = p.getUsername();
    if (n == null) continue;
    rows.add(n.toLowerCase() + "\t" + p.getUuid().toString() + "\t" + n);
  }
  java.util.Collections.sort(rows);
  int per = @PKG@.MenuData.PLAYER_SLOTS.length;
  this.pages = paging(rows.size(), per);
  for (int i = 0; i < per; i++) {
    int k = this.pageNo * per + i;
    if (k >= rows.size()) break;
    String[] parts = ((String) rows.get(k)).split("\t");
    if (parts.length < 3) continue;
    String n = @PKG@.MenuUtil.safe(parts[2]);
    put(slots, @PKG@.MenuData.PLAYER_SLOTS[i], @PKG@.MenuData.ICON_PLAYER, n,
        n + " is online.\nClick to send a teleport request, visit their island or invite them to your party.", "Click for options", "player:" + parts[1], false);
  }
  if (rows.isEmpty()) put(slots, @PKG@.MenuData.NO_PLAYERS_SLOT, @PKG@.MenuData.ICON_PLAYER, "Nobody else is online",
      "You are the only player online right now.", null, "info", true);
}""")
M(page, r"""
public @PR@ selected() {
  if (this.selU == null) return null;
  try {
    @PR@ p = @UNI@.get().getPlayer(this.selU);
    return p != null && p.isValid() ? p : null;
  } catch (Throwable t) { return null; }
}""")
M(page, r"""
public void fillPlayer(java.util.ArrayList slots) {
  @PR@ target = selected();
  if (target == null) {
    this.title = "Player offline";
    put(slots, @PKG@.MenuData.NO_PLAYERS_SLOT, @PKG@.MenuData.ICON_PLAYER, "Player offline", "That player is no longer online.", "Players above lists who is online", "info", true);   // 0.3.35
    return;
  }
  String n = @PKG@.MenuUtil.safe(target.getUsername());
  this.title = n;
  put(slots, @PKG@.MenuData.PLAYER_HEAD_SLOT, @PKG@.MenuData.ICON_PLAYER, n, n + " is online.\nPick what you want to do below.", null, "info", false);
  for (int i = 0; i < @PKG@.MenuData.PA_SLOT.length; i++) {
    String c = @PKG@.MenuUtil.firstWord(@PKG@.MenuData.PA_CMD[i]);
    boolean dim = @PKG@.MenuUtil.cmd(c) == null;
    String pname = @PKG@.MenuData.PA_NAME[i];
    String pbody = @PKG@.MenuData.PA_BODY[i];
    String pfoot = @PKG@.MenuData.PA_FOOT[i];
    int li = dim ? -1 : @PKG@.MenuUtil.legacyPa(@PKG@.MenuData.PA_SLOT[i]);
    if (li >= 0) { pname = @PKG@.MenuData.PAL_NAME[li]; pbody = @PKG@.MenuData.PAL_BODY[li]; pfoot = @PKG@.MenuData.PAL_FOOT[li]; }
    put(slots, @PKG@.MenuData.PA_SLOT[i], @PKG@.MenuData.PA_ICON[i], pname + (dim ? " (not installed)" : ""),
        pbody.replace("%P", n), dim ? "Not installed on this server" : pfoot, "pact:" + i, dim);
  }
}""")
M(page, r"""
public void fillMods(java.util.ArrayList slots) {
  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);
  int per = @PKG@.MenuData.MOD_SLOTS.length;
  int n = @PKG@.MenuData.MOD_NAME.length;
  this.pages = paging(n, per);
  for (int i = 0; i < per; i++) {
    int k = this.pageNo * per + i;
    if (k >= n) break;
    String live = @PKG@.MenuUtil.liveVersion(@PKG@.MenuData.MOD_NAME[k]);
    boolean installed = live != null || @PKG@.MenuUtil.cmd(@PKG@.MenuData.MOD_CHECK[k]) != null;
    String ver = live != null ? live : @PKG@.MenuData.MOD_VER[k];
    boolean cfg = admin && installed && @PKG@.MenuUtil.bridge().get("config:def:" + @PKG@.MenuData.MOD_NAME[k]) instanceof Object[];
    put(slots, @PKG@.MenuData.MOD_SLOTS[i], @PKG@.MenuData.MOD_ICON[k],
        @PKG@.MenuData.MOD_NAME[k] + " " + ver + (installed ? "" : " (not installed)"), @PKG@.MenuUtil.modBodyFor(k, admin),
        installed ? (cfg ? "Click to set up this mod" : "Click to show the commands below") : "Not installed on this server",
        cfg ? "modcfg:" + k : "mod:" + k, !installed);
  }
}""")
M(page, r"""
public void nav(java.util.ArrayList slots) {
  String back = this.view.equals("player") ? "Players Online" : "Home";   // 0.3.29: the classic views only (Home is a grid page)
  // 0.3.35: no grid buttons (the old back / close / page tiles) - rows 1 + 2 lead away, the footer has Close and the page arrows
  if (back == null) return;
}""")
# ================= 0.3.29 MenuPage: HOME + TELEPORT (the 7 x 5 grid pages) - the shortcut keys, the grid, the editor's grid, + Add =================
M(page, r"""
public static String pageOf(int page, int pages) { return pages > 1 ? "  (page " + (page + 1) + " of " + pages + ")" : ""; }""")
M(page, r"""
public boolean isDash() {
  String v = this.view == null ? "main" : this.view;
  return v.equals("main") || v.equals("tp");
}""")
M(page, "public int part() { return \"tp\".equals(this.view) ? 1 : 0; }")
M(page, r"""
public static String[] gone(String icon, String name) {
  return new String[] { icon, name, "That is not on this server right now.", "Not on this server", null, "gone" };
}""")
# an old 0.3.28 tile as a shortcut: its rule, text, icon and action exactly as the 0.3.28 main view drew it (fillStatic)
M(page, r"""
public String[] tileLook(int i, boolean admin) {
  java.util.UUID me = this.playerRef.getUuid();
  String act = @PKG@.MenuData.E_ACT[i];
  String name = @PKG@.MenuData.E_NAME[i];
  String body = @PKG@.MenuData.E_BODY[i];
  String icon = @PKG@.MenuData.E_ICON[i];
  if (!tileVisible(i, admin)) return new String[] { icon, name, "", "", null, "perm" };
  if ("profile".equals(act)) body = profileBody();
  if ("cmdc:pets".equals(act)) {
    if (!@PKG@.PetTile.installed()) return gone(icon, name);
    String[] pi = @PKG@.PetTile.of(me);
    name = @PKG@.PetTile.title(pi);
    body = @PKG@.PetTile.body(me, pi);
    icon = @PKG@.PetTile.icon(pi);
  }
  if (body.indexOf("%PURSE%") >= 0) body = body.replace("%PURSE%", purseText());
  if (body.indexOf("%BANK%") >= 0) body = body.replace("%BANK%", bankText());
  String c = cmdOf(act);
  boolean dim = c != null && @PKG@.MenuUtil.cmd(c) == null;
  String need = dim ? null : @PKG@.MenuUtil.needOf(lineOf(act));
  if (need != null) return new String[] { icon, name + " (update needed)", body, "Needs " + need + " on this server", act, "dim" };
  String foot = dim ? "Not installed on this server" : @PKG@.MenuData.E_FOOT[i];
  return new String[] { icon, name + (dim ? " (not installed)" : ""), body, foot == null ? "Click to open!" : foot, act, dim ? "dim" : "ok" };
}""")
# the classic views' fixed entries (Players: Accept / Deny) - drawn the way a tile shortcut is ("perm" / "gone" = not drawn)
M(page, r"""
public void fillStatic(java.util.ArrayList slots) {
  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);
  for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {
    if (!@PKG@.MenuData.E_VIEW[i].equals(this.view)) continue;
    String[] l = tileLook(i, admin);
    if (l[5].equals("ok") || l[5].equals("dim")) put(slots, @PKG@.MenuData.E_SLOT[i], l[0], l[1], l[2], l[3], l[4], l[5].equals("dim"));
  }
}""")
M(page, r"""
public static String tabIcon(String h, String t) {
  String k = h + ":" + t;
  for (int i = 0; i < @PKG@.MenuData.TAB_KEY.length; i++) { if (@PKG@.MenuData.TAB_KEY[i].equals(k)) return @PKG@.MenuData.TAB_ICON[i]; }   // 0.3.30
  int hi = @PKG@.MenuHub.hubIndex(h);
  return hi < 0 ? @PKG@.MenuData.ICON_EMPTY : @PKG@.MenuData.HUB_ICON[hi];
}""")
M(page, r"""
public static int tpEntry(String k) {
  for (int i = 0; i < @PKG@.MenuData.TPK_KEY.length; i++) { if (@PKG@.MenuData.TPK_KEY[i].equals(k)) return @PKG@.MenuData.TPK_E[i]; }
  return -1;
}""")
# what a shortcut key draws: { icon, name, hover text, foot, action (null = none), state } - state "ok", "dim" (not installed / locked),
# "gone" (not on this server: hidden; the editor shows it so it can be removed) or "perm" (not for this player: fully hidden, the
# 2026-09-25 rule). Runs on the world thread while the page is drawn.
# 0.3.37: a bridge's home list (String[] names; null = the bridge is not there; names that break the key rule are left out)
M(page, r"""
public String[] homesOf(String key) {
  Object f = @PKG@.MenuUtil.bridge().get(key);
  if (!(f instanceof java.util.function.Function)) return null;
  try {
    Object r = ((java.util.function.Function) f).apply(this.playerRef.getUuid());
    if (r instanceof String[]) {
      String[] a = (String[]) r;
      java.util.ArrayList ok = new java.util.ArrayList();
      for (int i = 0; i < a.length; i++) { if (a[i] != null && @PKG@.MenuLayout.okWarp(a[i]) && !ok.contains(a[i])) ok.add(a[i]); }
      return (String[]) ok.toArray(new String[0]);
    }
  } catch (Throwable t) { @PKG@.PageGuard.warnOnce("the bridge " + key + " failed: " + t); }
  return new String[0];
}""")
# 0.3.37: essentials:fn:warps -> { lower warp id -> theme }; empty = no bridge (every warp the signpost)
M(page, r"""
public static java.util.HashMap warpThemes() {
  java.util.HashMap m = new java.util.HashMap();
  Object f = @PKG@.MenuUtil.bridge().get("essentials:fn:warps");
  if (!(f instanceof java.util.function.Function)) return m;
  try {
    Object r = ((java.util.function.Function) f).apply((Object) null);
    if (r instanceof String[]) {
      String[] a = (String[]) r;
      for (int i = 0; i < a.length; i++) {
        if (a[i] == null) continue;
        int p = a[i].lastIndexOf('|');
        if (p > 0) m.put(a[i].substring(0, p).toLowerCase(java.util.Locale.ROOT), a[i].substring(p + 1));
      }
    }
  } catch (Throwable t) { @PKG@.PageGuard.warnOnce("the bridge essentials:fn:warps failed: " + t); }
  return m;
}""")
M(page, r"""
public static String themeIcon(java.util.HashMap th, String warp) {
  Object t = th == null || warp == null ? null : th.get(warp.toLowerCase(java.util.Locale.ROOT));
  if (t instanceof String) {
    for (int i = 0; i < @PKG@.MenuData.WI_THEME.length; i++) { if (@PKG@.MenuData.WI_THEME[i].equals(t)) return @PKG@.MenuData.WI_ICON[i]; }
  }
  return @PKG@.MenuData.ICON_WARP;
}""")
# the name as the bridge spells it (any case), null = not in the list
M(page, r"""
public static String nameIn(String[] a, String n) {
  if (a == null || n == null) return null;
  for (int i = 0; i < a.length; i++) { if (a[i] != null && a[i].equalsIgnoreCase(n)) return a[i]; }
  return null;
}""")
# the lists one draw uses (world thread): island homes, homes, the warp icons
M(page, r"""
public void loadTp() {
  this.ihs = homesOf("island:fn:homes");
  this.zhs = homesOf("essentials:fn:homes");
  this.wth = warpThemes();
}""")
# a warp tile { icon, name, hover text (+ pos), foot, action, state } - open or locked (look() and fillAutoWarps)
M(page, r"""
public String[] warpTile(String n, @WRP@ w, String pos) {
  String id = @PKG@.MenuUtil.safe(w.getId());
  boolean open = @PKG@.MenuUtil.isWarpUnlocked(this.playerRef, w.getId());
  return new String[] { open ? themeIcon(this.wth, n) : @PKG@.MenuData.ICON_WARP_LOCKED, open ? id : id + " (locked)",   // 0.3.37: its icon
                        "Warp " + id + ".\nWorld: " + @PKG@.MenuUtil.safe(w.getWorld()) + pos,
                        open ? "Click to warp!" : "Locked - you have not unlocked this warp yet", open ? "warp:" + n : "locked:" + n, open ? "ok" : "dim" };
}""")
M(page, r"""
public static String redirect(String k, java.util.UUID me) {
  if (k == null) return null;
  int i = -1;
  for (int j = 0; j < @PKG@.MenuData.REDIR_FROM.length; j++) { if (@PKG@.MenuData.REDIR_FROM[j].equals(k)) i = j; }
  if (i < 0) return null;
  Object o = @PKG@.HubBar.get("hub:tab:" + k.substring(4));
  if (o instanceof Object[] && ((Object[]) o).length >= 6) {
    Object[] e = (Object[]) o;
    if (@PKG@.HubBar.hostOf(e) == null && @PKG@.HubBar.visible(e, me)) return null;
  }
  String to = @PKG@.MenuData.REDIR_TO[i];
  if (to.startsWith("cmd:")) return @PKG@.MenuUtil.cmd(@PKG@.MenuUtil.firstWord(to.substring(4))) != null ? to : null;
  if (to.startsWith("tab:") && @PKG@.HubBar.get("hub:tab:" + to.substring(4)) instanceof Object[]) return to;
  return null;
}""")
M(page, r"""
public static String redirName(String k) {
  for (int j = 0; j < @PKG@.MenuData.REDIR_FROM.length; j++) { if (@PKG@.MenuData.REDIR_FROM[j].equals(k)) return @PKG@.MenuData.REDIR_NAME[j] + "|" + @PKG@.MenuData.REDIR_WHY[j]; }
  return "|";
}""")
M(page, r"""
public String[] look(String k, boolean admin) {
  java.util.UUID me = this.playerRef.getUuid();
  if (k == null) return null;
  if (k.startsWith("hub:")) {
    String h = k.substring(4);
    int hi = @PKG@.MenuHub.hubIndex(h);
    if (hi < 0) return gone(@PKG@.MenuData.ICON_EMPTY, k);
    java.util.ArrayList t = @PKG@.HubBar.tabs(h, me);
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < t.size() && i < 9; i++) { if (i > 0) sb.append(", "); sb.append((String) ((Object[]) t.get(i))[1]); }
    String dt = @PKG@.MenuData.HUB_DEFTAB[hi];
    String body = @PKG@.MenuData.HUB_BLURB[hi] + "\n" + (t.isEmpty() ? @PKG@.MenuData.HUB_SOON[hi] : "Tabs: " + sb.toString())
      + (dt.length() > 0 ? "\nOpens on its " + dt.substring(0, 1).toUpperCase() + dt.substring(1) + " page." : "\nOpens the page you used last.") + "\nCommand: /" + @PKG@.MenuData.HUB_CMD[hi];
    return new String[] { @PKG@.MenuData.HUB_ICON[hi], @PKG@.MenuData.HUB_TITLE[hi], body, "Click to open!", "sc:" + k, "ok" };
  }
  if (k.equals("tab:settings:layout")) {   // 0.3.35: Edit shortcuts left the Settings hub (Skyy popup 5); the shortcut still opens the editor
    return new String[] { tabIcon("settings", "layout"), "Edit shortcuts", "Pick what shows on your Home page and the Teleport page.\nThe same as the Edit shortcuts button at the foot of Home.", "Click to edit!", "sc:" + k, "ok" };
  }
  if (k.startsWith("tab:")) {
    String rd = redirect(k, me);          // 0.3.34: a merged-away tab draws as where its page went (never locked)
    if (rd != null) {
      int c0 = k.indexOf(':', 4);
      String nw = redirName(k);
      String ic0 = c0 < 0 ? @PKG@.MenuData.ICON_EMPTY : tabIcon(k.substring(4, c0), k.substring(c0 + 1));
      return new String[] { ic0, nw.substring(0, nw.indexOf('|')), "Opens " + nw.substring(nw.indexOf('|') + 1) + "." + (rd.startsWith("cmd:") ? "\nCommand: /" + rd.substring(4) : ""), "Click to open!", "sc:" + k, "ok" };
    }
    int c = k.indexOf(':', 4);
    if (c < 0) return gone(@PKG@.MenuData.ICON_EMPTY, k);
    String h = k.substring(4, c);
    String tb = k.substring(c + 1);
    int hi = @PKG@.MenuHub.hubIndex(h);
    String icon = tabIcon(h, tb);
    Object o = @PKG@.HubBar.get("hub:tab:" + h + ":" + tb);
    if (hi < 0 || !(o instanceof Object[]) || ((Object[]) o).length < 6) return gone(icon, (hi < 0 ? h : @PKG@.MenuData.HUB_TITLE[hi]) + " > " + tb);
    Object[] e = (Object[]) o;
    String lab = (e[1] instanceof String) ? @PKG@.HubBar.clean((String) e[1]) : tb;
    String host = @PKG@.HubBar.hostOf(e);   // 0.3.33: a merged page (Stats in Skills, Class in Trees) is never locked
    if (host == null && !@PKG@.HubBar.visible(e, me)) return new String[] { icon, lab, "", "", null, "perm" };
    String cmd = (e[3] instanceof String) ? (String) e[3] : "";
    String body = @PKG@.MenuData.HUB_TITLE[hi] + " > " + lab + " - a page of the " + @PKG@.MenuData.HUB_TITLE[hi] + " hub." + (cmd.length() > 0 ? "\nCommand: /" + cmd : "");
    Object ho = host == null ? null : @PKG@.HubBar.get("hub:tab:" + h + ":" + host);
    if (ho instanceof Object[] && ((Object[]) ho).length >= 6) {
      Object[] he = (Object[]) ho;
      String hl = (he[1] instanceof String) ? @PKG@.HubBar.clean((String) he[1]) : host;
      body = @PKG@.MenuData.HUB_TITLE[hi] + " > " + hl + " > " + lab + " - part of the " + hl + " tab." + (cmd.length() > 0 ? "\nCommand: /" + cmd : "");
    }
    return new String[] { icon, lab, body, "Click to open!", "sc:" + k, "ok" };
  }
  if (k.startsWith("tile:")) {
    int i = @PKG@.MenuLayout.keyIndex(k.substring(5));
    if (i < 0) return gone(@PKG@.MenuData.ICON_EMPTY, k);
    return tileLook(i, admin);
  }
  if (k.startsWith("tp:")) {
    int i = tpEntry(k);
    if (i < 0) return gone(@PKG@.MenuData.ICON_EMPTY, k);
    String act = @PKG@.MenuData.E_ACT[i];
    String c = cmdOf(act);
    boolean dim = c != null && @PKG@.MenuUtil.cmd(c) == null;
    return new String[] { @PKG@.MenuData.E_ICON[i], @PKG@.MenuData.E_NAME[i] + (dim ? " (not installed)" : ""), @PKG@.MenuData.E_BODY[i],
                          dim ? "Not installed on this server" : @PKG@.MenuData.E_FOOT[i], act, dim ? "dim" : "ok" };
  }
  if (k.startsWith("warp:")) {
    String n = k.substring(5);
    @TPP@ tp = null;
    try { tp = @TPP@.get(); } catch (Throwable t) { tp = null; }
    if (tp == null || !tp.isWarpsLoaded()) return new String[] { @PKG@.MenuData.ICON_WARP, n, "Warp " + n + ".\nThe warp list is still loading.", "Click to warp!", "warp:" + n, "ok" };
    @WRP@ w = (@WRP@) tp.getWarps().get(n);
    if (w == null) return gone(@PKG@.MenuData.ICON_WARP_LOCKED, n);
    return warpTile(n, w, "");
  }
  if (k.startsWith("ihome:") || k.startsWith("zhome:")) {   // 0.3.37: an island home (SkyyIslands) / a home (SkyyEssentials)
    boolean isl = k.startsWith("ihome:");
    String n = k.substring(6);
    String ic = isl ? @PKG@.MenuData.ICON_IHOME : @PKG@.MenuData.ICON_ZHOME;
    String nm = nameIn(isl ? this.ihs : this.zhs, n);
    if (nm == null) return gone(ic, (isl ? "Island home " : "Home ") + n);
    if (isl) return new String[] { ic, "Island home " + nm, "Your island home " + nm + " (set with /island sethome " + nm + ").\nCommand: /island " + nm, "Click to teleport!", "ihome:" + nm, "ok" };
    return new String[] { ic, "Home " + nm, "Your home " + nm + " (set with /sethome " + nm + ").\nCommand: /home " + nm, "Click to teleport!", "zhome:" + nm, "ok" };
  }
  return gone(@PKG@.MenuData.ICON_EMPTY, k);
}""")
M(page, r"""
public String nameOf(String k) {
  String[] l = look(k, true);
  return l == null ? "That shortcut" : l[1];
}""")
M(page, r"""
public void editTile2(java.util.ArrayList slots, int s, String icon, String name) {
  boolean sel = s == this.editSel;
  put(slots, s, icon, sel ? "[Moving] " + name : name, sel ? @PKG@.MenuData.HT_SEL_BODY : @PKG@.MenuData.HT_TILE_BODY,
      sel ? @PKG@.MenuData.HT_SEL_FOOT : (this.editSel >= 0 ? @PKG@.MenuData.HT_SWAP_FOOT : @PKG@.MenuData.HT_PICK_FOOT), "eslot", false);
}""")
M(page, r"""
public void drawKey(java.util.ArrayList slots, int s, String k, boolean admin) {
  String[] l = look(k, admin);
  if (l == null) return;
  String st = l[5];
  if (this.editing) {
    if (st.equals("perm")) { this.hid[s] = true; return; }
    editTile2(slots, s, l[0], l[1] + (st.equals("gone") ? " (not on this server)" : ""));
    return;
  }
  if (st.equals("perm") || st.equals("gone")) return;
  put(slots, s, l[0], l[1], l[2], l[3], l[4], st.equals("dim"));
}""")
M(page, r"""
public void emptyMark(java.util.ArrayList slots, int s) {
  boolean mv = this.editSel >= 0;
  put(slots, s, @PKG@.MenuData.ICON_EMPTY, @PKG@.MenuData.HT_EMPTY_NAME, mv ? @PKG@.MenuData.HT_EMPTY_MOVE : @PKG@.MenuData.HT_EMPTY_ADD,
      mv ? @PKG@.MenuData.HT_EMPTY_FOOT_MOVE : @PKG@.MenuData.HT_EMPTY_FOOT_ADD, "eslot", false);
}""")
# + Add: every hub, every hub tab this player can see (from the registry - other mods' tabs appear when they are loaded), every 0.3.28
# tile this player can see (not Hover Tooltips), every teleport target; on the Teleport grid: the teleport targets only
M(page, r"""
public java.util.ArrayList candidates(boolean home, boolean admin) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.UUID me = this.playerRef.getUuid();
  if (home) {
    // 0.3.30: one entry per page (MenuLayout.canon): a hub whose default tab is shown here is listed as that TAB (Teleport, Skills - the
    // key a saved grid keeps too), then every other hub, every tab, every old tile that is not one of them
    java.util.ArrayList cs = new java.util.ArrayList();
    java.util.ArrayList tk = new java.util.ArrayList();
    for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) {
      java.util.ArrayList t = @PKG@.HubBar.tabs(@PKG@.MenuData.HUB_ID[i], me);
      for (int j = 0; j < t.size(); j++) tk.add("tab:" + @PKG@.MenuData.HUB_ID[i] + ":" + (String) ((Object[]) t.get(j))[0]);
      // 0.3.33: every MERGED page keeps its own shortcut (Skyy 2026-10-15 "each page should keep its own to open it"), right after its host
      java.util.ArrayList sx = @PKG@.HubBar.subTabs(@PKG@.MenuData.HUB_ID[i], me);
      for (int j = 0; j < sx.size(); j++) {
        Object[] x = (Object[]) sx.get(j);
        String k2 = "tab:" + @PKG@.MenuData.HUB_ID[i] + ":" + (String) x[0];
        if (tk.contains(k2)) continue;
        int at = tk.indexOf("tab:" + @PKG@.MenuData.HUB_ID[i] + ":" + (String) x[2]);
        if (at < 0) tk.add(k2); else tk.add(at + 1, k2);
      }
    }
    for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) {
      String hk = "hub:" + @PKG@.MenuData.HUB_ID[i];
      String c = @PKG@.MenuLayout.canon(hk);
      if (!c.equals(hk) && tk.contains(c)) continue;
      @PKG@.MenuLayout.addOnce(out, cs, hk);
    }
    for (int i = 0; i < tk.size(); i++) @PKG@.MenuLayout.addOnce(out, cs, (String) tk.get(i));
    for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {
      if (!@PKG@.MenuLayout.isMain(i) || "-".equals(@PKG@.MenuData.MIG[i])) continue;
      String[] l = tileLook(i, admin);
      if (l[5].equals("ok") || l[5].equals("dim")) @PKG@.MenuLayout.addOnce(out, cs, "tile:" + @PKG@.MenuData.E_KEY[i]);
    }
  }
  for (int i = 0; i < @PKG@.MenuData.TPK_KEY.length; i++) out.add(@PKG@.MenuData.TPK_KEY[i]);
  if (this.ihs != null) { for (int i = 0; i < this.ihs.length; i++) out.add("ihome:" + this.ihs[i]); }   // 0.3.37: island homes, homes
  if (this.zhs != null) { for (int i = 0; i < this.zhs.length; i++) out.add("zhome:" + this.zhs[i]); }
  try {
    @TPP@ tp = @TPP@.get();
    if (tp != null && tp.isWarpsLoaded()) {
      java.util.ArrayList ws = new java.util.ArrayList();
      java.util.Iterator it = tp.getWarps().keySet().iterator();
      while (it.hasNext()) { String w = String.valueOf(it.next()); if (@PKG@.MenuLayout.okWarp(w)) ws.add(w); }
      java.util.Collections.sort(ws);
      for (int i = 0; i < ws.size(); i++) out.add("warp:" + (String) ws.get(i));
    }
  } catch (Throwable t) { }
  return out;
}""")
M(page, r"""
public static String kindOf(String k) {
  if (k.startsWith("hub:")) return "A hub.";
  if (k.startsWith("tab:")) return "One page of a hub.";
  if (k.startsWith("tile:")) return "A tile of the old menu.";
  return "A teleport.";
}""")
M(page, r"""
public void fillAdd(java.util.ArrayList slots, boolean home, boolean admin) {
  java.util.UUID me = this.playerRef.getUuid();
  this.grid = @PKG@.MenuLayout.grid(me, part());
  java.util.ArrayList c = candidates(home, admin);
  java.util.ArrayList left = new java.util.ArrayList();
  for (int i = 0; i < c.size(); i++) { if (!@PKG@.MenuLayout.hasSame(this.grid, (String) c.get(i))) left.add(c.get(i)); }
  int per = @PKG@.MenuData.HG_N;
  this.addPages = left.isEmpty() ? 1 : (left.size() + per - 1) / per;
  if (this.addPage >= this.addPages) this.addPage = this.addPages - 1;
  if (this.addPage < 0) this.addPage = 0;
  this.addKeys = new String[per];
  for (int s = 0; s < per; s++) {
    int k = this.addPage * per + s;
    if (k >= left.size()) break;
    String key = (String) left.get(k);
    String[] l = look(key, admin);
    if (l == null || l[5].equals("perm") || l[5].equals("gone")) continue;
    this.addKeys[s] = key;
    put(slots, s, l[0], l[1], kindOf(key) + "\n" + l[2], "Click to put it in the empty slot", "eadd", false);
  }
  if (left.isEmpty()) put(slots, @PKG@.MenuData.HG_CR * @PKG@.MenuData.HG_COLS + @PKG@.MenuData.HG_CC, @PKG@.MenuData.ICON_NO_WARPS, "Nothing left to add",
                          @PKG@.MenuData.HT_NONE_LEFT, null, "info", true);
}""")
# the Teleport page: warps nobody placed fill the free slots of rows 4 and 5 (Prev / Next page through them)
# 0.3.37: island homes, then homes, then warps - every one the player has not placed (new ones land at the end); in Arrange they are
# drawn as pick-up tiles (autoAt[slot] = the key; a click pins it there - dashEditClick)
M(page, r"""
public static void addAuto(java.util.ArrayList keys, String[] grid, String pfx, String[] names) {
  if (names == null) return;
  for (int i = 0; i < names.length; i++) {
    String k = pfx + names[i];
    boolean on = false;
    for (int s = 0; s < grid.length; s++) { if (grid[s] != null && grid[s].equalsIgnoreCase(k)) on = true; }
    if (!on) keys.add(k);
  }
}""")
M(page, r"""
public void fillAutoWarps(java.util.ArrayList slots) {
  @TPP@ tp = null;
  try { tp = @TPP@.get(); } catch (Throwable t) { }
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.Map warps = null;
  boolean placed = false;
  for (int s = 0; s < this.grid.length; s++) { if (this.grid[s] != null && this.grid[s].startsWith("warp:")) placed = true; }
  addAuto(keys, this.grid, "ihome:", this.ihs);
  addAuto(keys, this.grid, "zhome:", this.zhs);
  int nw = 0;
  if (tp != null && tp.isWarpsLoaded()) {
    warps = tp.getWarps();
    java.util.ArrayList ws = new java.util.ArrayList();
    java.util.Iterator it = warps.keySet().iterator();
    while (it.hasNext()) { String k = String.valueOf(it.next()); if (!@PKG@.MenuLayout.has(this.grid, "warp:" + k)) ws.add(k); }
    java.util.Collections.sort(ws);
    nw = ws.size();
    for (int i = 0; i < ws.size(); i++) keys.add("warp:" + (String) ws.get(i));
  }
  java.util.ArrayList free = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.MenuData.TP_AUTO.length; i++) {
    int s = @PKG@.MenuData.TP_AUTO[i];
    if (this.grid[s] == null) free.add(Integer.valueOf(s));
  }
  int per = free.size();
  if (per == 0) return;
  this.pages = paging(keys.size(), per);
  if (this.pageNo >= this.pages) this.pageNo = this.pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  for (int i = 0; i < per; i++) {
    int k = this.pageNo * per + i;
    if (k >= keys.size()) break;
    String key = (String) keys.get(k);
    int s = ((Integer) free.get(i)).intValue();
    String[] l = null;
    if (key.startsWith("warp:")) {
      @WRP@ w = (@WRP@) warps.get(key.substring(5));
      if (w == null) continue;
      String pos = "";
      try {
        @V3D@ p = w.getTransform().getPosition();
        pos = "\nX " + (long) Math.floor(p.x) + "   Y " + (long) Math.floor(p.y) + "   Z " + (long) Math.floor(p.z);
      } catch (Throwable t) { }
      l = warpTile(key.substring(5), w, pos);
    } else {
      l = look(key, false);
    }
    if (l == null || l[5].equals("perm") || l[5].equals("gone")) continue;
    if (this.editing) {
      if (this.autoAt != null && s < this.autoAt.length) this.autoAt[s] = key;
      editTile2(slots, s, l[0], l[1]);
    } else {
      put(slots, s, l[0], l[1], l[2], l[3], l[4], l[5].equals("dim"));
    }
  }
  if (nw == 0 && !placed && !this.editing) {
    int at = keys.isEmpty() ? (per > 3 ? 3 : 0) : keys.size() - this.pageNo * per;
    if (at >= 0 && at < per) {
      put(slots, ((Integer) free.get(at)).intValue(), @PKG@.MenuData.ICON_NO_WARPS, "No warps yet",
          tp == null || warps != null ? "No warps have been set on this server yet.\nAn admin adds them on /warpadmin (Add warp here)." : "The warp list is still loading.\nOpen this menu again in a moment.",
          null, "info", true);
    }
  }
}""")
M(page, r"""
public void fillDash(java.util.ArrayList slots) {
  boolean home = this.view.equals("main");
  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);
  loadTp();                                                         // 0.3.37: island homes, homes, warp icons
  this.autoAt = new String[@PKG@.MenuData.HG_N];
  if (this.editing && this.addSlot >= 0) { fillAdd(slots, home, admin); return; }
  this.grid = @PKG@.MenuLayout.grid(this.playerRef.getUuid(), part());
  for (int s = 0; s < this.grid.length && s < slots.size(); s++) {
    String k = this.grid[s];
    if (k == null) { if (this.editing) emptyMark(slots, s); continue; }
    drawKey(slots, s, k, admin);
  }
  if (!home) fillAutoWarps(slots);   // 0.3.37: in Arrange too (pick-up tiles)
}""")
M(page, r"""
public void fill(java.util.ArrayList slots) {
  int vi = @PKG@.MenuData.viewIndex(this.view);
  this.view = @PKG@.MenuData.V_KEY[vi];
  this.title = @PKG@.MenuData.V_TITLE[vi];
  this.pages = 1;
  if (isDash()) {
    fillDash(slots);
    if (this.pages <= 1) this.pageNo = 0;
    return;
  }
  fillStatic(slots);
  if (this.view.equals("players")) fillPlayers(slots);
  else if (this.view.equals("player")) fillPlayer(slots);
  else if (this.view.equals("mods")) fillMods(slots);
  if (this.pages <= 1) this.pageNo = 0;
  nav(slots);
  this.title = this.title + pageOf(this.pageNo, this.pages);
}""")
# 0.3.29: every view is a hub page: main = Home (row 1, Home active), tp = World > Teleport, players / player = Social > Players, mods =
# Settings > Mods (the classic 9 x 6 views keep the 0.3.28 body in the kit 1.6 row shell)
M(page, r"""
public String hubName() {
  String v = this.view == null ? "main" : this.view;
  if (v.equals("main")) return "home";
  if (v.equals("tp")) return "world";
  if (v.equals("players") || v.equals("player")) return "social";
  return "settings";
}""")
M(page, r"""
public String hubTab() {
  String v = this.view == null ? "main" : this.view;
  if (v.equals("tp")) return "teleport";
  if (v.equals("players") || v.equals("player")) return "players";
  if (v.equals("mods")) return "mods";
  return null;
}""")
# Right now: every bridge key home:alert:<mod> (sorted) holding a java.util.function.Function; apply(UUID) -> up to 3 lines "text|target"
# (a throw = skipped + one warning per key). At most AL_SHOW lines in all; each text clipped to AL_MAX characters.
M(page, r"""
public java.util.ArrayList alerts() {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Map br = @PKG@.MenuUtil.bridge();
  java.util.ArrayList ks = new java.util.ArrayList();
  try {
    java.util.Iterator it = br.keySet().iterator();
    while (it.hasNext()) { Object k = it.next(); if ((k instanceof String) && ((String) k).startsWith("home:alert:")) ks.add(k); }
  } catch (Throwable t) { }
  java.util.Collections.sort(ks);
  for (int i = 0; i < ks.size(); i++) {
    String key = (String) ks.get(i);
    Object f = br.get(key);
    if (!(f instanceof java.util.function.Function)) continue;
    Object r = null;
    try { r = ((java.util.function.Function) f).apply(this.playerRef.getUuid()); }
    catch (Throwable t) {
      r = null;
      if (@PKG@.MenuData.TILE_WARNED.putIfAbsent(key, key) == null) @PKG@.MenuUtil.warn("the Home alert " + key + " failed (skipped): " + t);
    }
    if (!(r instanceof String)) continue;
    String[] ls = ((String) r).split("\n");
    int n = 0;
    for (int j = 0; j < ls.length && n < 3; j++) {
      String ln = ls[j].trim();
      if (ln.length() == 0) continue;
      int bar = ln.lastIndexOf('|');
      String tx = bar >= 0 ? ln.substring(0, bar) : ln;
      String tg = bar >= 0 ? ln.substring(bar + 1).trim() : "";
      tx = @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(tx).trim(), @PKG@.MenuData.AL_MAX);
      if (tx.length() == 0) continue;
      out.add(new String[] { tx, tg });
      n = n + 1;
      if (out.size() >= @PKG@.MenuData.AL_SHOW) return out;
    }
  }
  return out;
}""")
# 0.3.30 RIGHT NOW rows (research/Unified-Menu-Plan.md section 2; Skyy 2026-10-16 "the menu is missing this right now section from the
# design."): from existing bridges only, read while Home is drawn (world thread, no ticking). quest:fn:hud (SkyyQuests: Object[]{ title,
# "3 / 24", then per shown task name, progress, frac, where, dir, Boolean done }) -> the first undone task; all shown tasks done = claim.
M(page, r"""
public static String questLine(java.util.UUID u) {
  Object f = @PKG@.MenuUtil.bridge().get("quest:fn:hud");
  if (u == null || !(f instanceof java.util.function.Function)) return null;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(u); }
  catch (Throwable t) {
    if (@PKG@.MenuData.TILE_WARNED.putIfAbsent("quest:fn:hud", "quest:fn:hud") == null) @PKG@.MenuUtil.warn("quest:fn:hud failed (the Right now quest line is left out): " + t);
    return null;
  }
  if (!(r instanceof Object[])) return null;
  Object[] a = (Object[]) r;
  boolean any = false;
  for (int i = 2; i + 5 < a.length; i += 6) {
    any = true;
    if (Boolean.TRUE.equals(a[i + 5])) continue;
    String nm = (a[i] instanceof String) ? ((String) a[i]).trim() : "";
    String pg = (a[i + 1] instanceof String) ? ((String) a[i + 1]).trim() : "";
    if (nm.length() == 0) continue;
    return @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe("Quest: " + nm + (pg.length() > 0 ? " " + pg : "")), @PKG@.MenuData.AL_MAX);
  }
  return any ? "Quest done - claim it" : null;
}""")
# SkyyGear's mystery bags (Skyy_Unid_Bag_<Rarity>) in the player's inventory - only while SkyyGear is loaded (gear:fn:smithing); world thread
M(page, r"""
public int unidBags(@REF@ ref, @ST@ st) {
  if (ref == null || st == null || !(@PKG@.MenuUtil.bridge().get("gear:fn:smithing") instanceof java.util.function.Function)) return 0;
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    return @PKG@.MenuUtil.countPrefix(p, "Skyy_Unid_Bag_");
  } catch (Throwable t) { return 0; }
}""")
M(page, r"""
public java.util.ArrayList nowRows(@REF@ ref, @ST@ st) {
  java.util.ArrayList out = new java.util.ArrayList();
  String q = questLine(this.playerRef.getUuid());
  if (q != null) out.add(new String[] { q, "world:quests" });
  int nb = unidBags(ref, st);
  if (nb > 0) out.add(new String[] { nb + (nb == 1 ? " mystery bag to identify" : " mystery bags to identify"), "smithing:identify" });
  java.util.ArrayList al = alerts();
  for (int i = 0; i < al.size() && out.size() < @PKG@.MenuData.AL_SHOW; i++) out.add(al.get(i));
  return out;
}""")
# 0.3.30 THE BIG ROW 1 (Home + every hub with a hub:def, kit 1.6 HubBar.hubs order) in the body of Home / Teleport: the kit's row button art,
# 48 px, a 32 px item icon, an 18 px label. Clicks a = "hub:h:<id>" (hubClick, as the kit row). Twin: big_row_preview in the build script.
M(page, r"""
public void bigRow(@UCB@ b, @UEB@ ev, String parent, String myHub, int w) {
  java.util.ArrayList h = @PKG@.HubBar.hubs();
  b.appendInline(parent, @PKG@.MenuData.UI_BROW);
  int n = h.size();
  if (n == 0) return;
  int bw = (w - @PKG@.MenuData.BR_GAP * (n - 1)) / n;
  boolean icons = bw >= @PKG@.MenuData.BR_ICON_MIN;
  for (int i = 0; i < n; i++) {
    Object[] e = (Object[]) h.get(i);
    String id = (String) e[0];
    boolean sel = id.equals(myHub);
    if (i > 0) b.appendInline("#SkyyMBRow", "Group { Anchor: (Width: " + @PKG@.MenuData.BR_GAP + "); }");
    String bid = "SkyyMBR" + i;
    b.appendInline("#SkyyMBRow", "Button #" + bid + " { Anchor: (Width: " + bw + ", Height: " + @PKG@.MenuData.BR_H + "); LayoutMode: Left; Padding: (Horizontal: " + @PKG@.MenuData.BR_PAD + ", Vertical: " + @PKG@.MenuData.BR_PADV + "); " + @PKG@.HubBar.rowStyle(sel) + " }");
    int lw = bw - 2 * @PKG@.MenuData.BR_PAD;
    String ic = (String) e[2];
    if (icons && @PKG@.HubBar.okItem(ic)) {
      b.appendInline("#" + bid, "ItemIcon { Anchor: (Width: " + @PKG@.MenuData.BR_ICON + ", Height: " + @PKG@.MenuData.BR_ICON + "); ItemId: \"" + ic + "\"; }");
      b.appendInline("#" + bid, "Group { Anchor: (Width: " + @PKG@.MenuData.BR_ICON_GAP + "); }");
      lw = lw - @PKG@.MenuData.BR_ICON - @PKG@.MenuData.BR_ICON_GAP;
    }
    b.appendInline("#" + bid, "Label { Anchor: (Width: " + lw + "); Text: \"" + (String) e[1] + "\"; Style: " + (sel ? @PKG@.MenuData.BR_LABSEL : @PKG@.MenuData.BR_LABN) + "; }");
    ev.addEventBinding(@BT@.Activating, "#" + bid, @EVD@.of("a", "hub:h:" + id));
  }
}""")
M(page, r"""
public static boolean hasTabArt(String stem) {
  for (int i = 0; i < @PKG@.MenuData.TAB_ART.length; i++) { if (@PKG@.MenuData.TAB_ART[i].equals(stem)) return true; }
  return false;
}""")
# 0.3.30 THE BIG ROW 2 (Teleport: the World tabs): 56 px tabs (the kit's tab art), each tab's icon behind its word (its putIcon icon, else
# the contract art SkyyMenu ships - SkyyHubTabs/<hub>_<tab>.png, "_on" while active), a 20 px label. Clicks a = "hub:<tab>" (hubClick).
M(page, r"""
public void bigTabs(@UCB@ b, @UEB@ ev, String parent, String hub, String myTab, int w) {
  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.HubBar.remember(u, hub, myTab);
  b.appendInline(parent, @PKG@.MenuData.UI_BTABS);
  int cap = (w + @PKG@.MenuData.BT_GAP) / (@PKG@.MenuData.BT_MIN + @PKG@.MenuData.BT_GAP);
  java.util.ArrayList t = @PKG@.HubBar.shown(@PKG@.HubBar.tabs(hub, u), myTab, cap < 1 ? 1 : cap);
  int n = t.size();
  if (n == 0) return;
  int tw = (w - @PKG@.MenuData.BT_GAP * (n - 1)) / n;
  for (int i = 0; i < n; i++) {
    Object[] e = (Object[]) t.get(i);
    String id = (String) e[0];
    boolean sel = id.equals(myTab);
    if (i > 0) b.appendInline("#SkyyMBTabs", "Group { Anchor: (Width: " + @PKG@.MenuData.BT_GAP + "); }");
    String bid = "SkyyMBT" + i;
    b.appendInline("#SkyyMBTabs", "Button #" + bid + " { Anchor: (Width: " + tw + ", Height: " + @PKG@.MenuData.BT_H + "); " + @PKG@.HubBar.tabBStyle(sel) + " }");
    String stem = @PKG@.HubBar.iconOf((Object[]) e[3]);
    if (stem == null && hasTabArt(hub + "_" + id)) stem = hub + "_" + id;
    if (stem != null) b.appendInline("#" + bid, "Group { Anchor: (Left: " + ((tw - @PKG@.MenuData.BT_ICON) / 2) + ", Top: " + @PKG@.MenuData.BT_ICON_TOP + ", Width: " + @PKG@.MenuData.BT_ICON + ", Height: " + @PKG@.MenuData.BT_ICON + "); Background: \"" + @PKG@.MenuData.TAB_ART_DIR + stem + (sel ? "_on" : "") + ".png\"; }");
    b.appendInline("#" + bid, "Label { Anchor: (Left: 0, Top: 0, Width: " + tw + ", Height: " + @PKG@.MenuData.BT_H + "); Padding: (Horizontal: " + @PKG@.MenuData.BT_PAD + "); Text: \"" + @PKG@.HubBar.clean((String) e[1]) + "\"; Style: " + @PKG@.MenuData.BT_LAB + "; }");
    ev.addEventBinding(@BT@.Activating, "#" + bid, @EVD@.of("a", "hub:" + id));
  }
}""")
M(page, r"""
public int youLine(@UCB@ b, int n, String text) {
  if (n >= @PKG@.MenuData.UI_HYL.length) return n;
  b.appendInline("#SkyyMHmYou", @PKG@.MenuData.UI_HYL[n]);
  b.set("#SkyyMHmYL" + n + ".Text", text);
  return n + 1;
}""")
M(page, r"""
public static String vitMax(Object[] vit, int i) {
  if (vit == null || i >= vit.length || !(vit[i] instanceof String[])) return null;
  String[] e = (String[]) vit[i];
  return e.length > 0 ? e[0] : null;
}""")
# YOU: the numbers players check most, from the existing bridge keys / the stat map (missing ones are left out); a click = Character > Stats
M(page, r"""
public void youPanel(@UCB@ b, @UEB@ ev, @REF@ ref, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HYOU);
  b.appendInline("#SkyyMHmYou", @PKG@.MenuData.UI_HYT);
  b.appendInline("#SkyyMHmYou", @PKG@.MenuData.UI_HYN);
  b.set("#SkyyMHmYN.Text", @PKG@.MenuUtil.safe(this.playerRef.getUsername()));
  int n = 0;
  String cls = @PKG@.StatsCalc.className(u);
  if (cls != null) n = youLine(b, n, "Class: " + cls);
  String pn = @PKG@.StatsCalc.profileName(u);
  if (pn != null) n = youLine(b, n, "Profile: " + pn);
  int lv = @PKG@.StatsCalc.overall(u);
  if (lv >= 0) {
    n = youLine(b, n, "Overall Level " + lv);
    Object[] ov = @PKG@.StatsCalc.overallInfo(u);
    int fill = 0;
    if (ov != null && ov.length > 1 && (ov[1] instanceof Number)) {
      int t = ((Number) ov[1]).intValue() % 10;
      if (t < 0) t = 0;
      fill = (@PKG@.MenuData.YOU_BAR_W * t) / 10;
    }
    b.appendInline("#SkyyMHmYou", @PKG@.MenuData.UI_HYBAR0 + fill + @PKG@.MenuData.UI_HYBAR1);
  }
  long pu = @PKG@.MenuUtil.purse(u);
  if (pu >= 0L) n = youLine(b, n, "Coins: " + @PKG@.MenuUtil.fmt(pu));
  long bk = @PKG@.MenuUtil.bank(u);
  if (bk >= 0L) n = youLine(b, n, "Bank: " + @PKG@.MenuUtil.fmt(bk));
  Object[] vit = null;
  try { vit = @PKG@.StatsCalc.vitals(st, ref); } catch (Throwable t) { vit = null; }
  String hp = vitMax(vit, 0);
  if (hp != null) n = youLine(b, n, "Health: " + hp);
  String mp = vitMax(vit, 1);
  if (mp != null) n = youLine(b, n, "Mana: " + mp);
  b.appendInline("#SkyyMHmYou", @PKG@.MenuData.UI_HYH);
  ev.addEventBinding(@BT@.Activating, "#SkyyMHmYou", @EVD@.of("a", "hyou"));
}""")
# 0.3.30: always drawn (Skyy's design: You | Pinned | Right now); nothing to do = "Nothing waiting"
M(page, r"""
public void nowPanel(@UCB@ b, @UEB@ ev, @REF@ ref, @ST@ st) {
  java.util.ArrayList al = nowRows(ref, st);
  this.alertT = new String[al.size()];
  b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HNOW);
  b.appendInline("#SkyyMHmNow", @PKG@.MenuData.UI_HNOWT);
  if (al.isEmpty()) { b.appendInline("#SkyyMHmNow", @PKG@.MenuData.UI_HNOWNONE); return; }
  for (int i = 0; i < al.size() && i < @PKG@.MenuData.UI_HA.length; i++) {
    String[] a = (String[]) al.get(i);
    this.alertT[i] = a[1];
    b.appendInline("#SkyyMHmNow", @PKG@.MenuData.UI_HA[i]);
    b.set("#SkyyMHmA" + i + ".Text", a[0] + (a[1].length() > 0 ? "  >" : ""));
    ev.addEventBinding(@BT@.Activating, "#SkyyMHmA" + i, @EVD@.of("a", "halert" + i));
  }
}""")
# 0.3.30: the 5 x 5 update left pins without a slot - told once (chat + the Home info line), by name; null = nothing to tell
M(page, r"""
public String spillNote() {
  String u = this.playerRef.getUuid().toString();
  Object o = @PKG@.MenuLayout.SPILL.get(u);
  if (!(o instanceof String) || ((String) o).startsWith("!")) return null;   // fix: told once ('!'); the Right now row stays until Edit shortcuts opens
  String sv = (String) o;
  @PKG@.MenuLayout.SPILL.put(u, "!" + sv);
  int bar = sv.indexOf('|');
  String[] ks = (bar >= 0 ? sv.substring(bar + 1) : sv).split(",");
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ks.length && i < 8; i++) { if (ks[i].length() == 0) continue; if (sb.length() > 0) sb.append(", "); sb.append(nameOf(ks[i])); }
  return ks.length + (ks.length == 1 ? " shortcut" : " shortcuts") + " did not fit the 5 x 5 grid - they wait in Edit shortcuts, + Add: " + @PKG@.MenuUtil.clip(sb.toString(), 90);
}""")
M(page, r"""
public static int fbIndex(String w) {
  for (int i = 0; i < @PKG@.MenuData.FB_WORD.length; i++) { if (@PKG@.MenuData.FB_WORD[i].equals(w)) return i; }
  return -1;
}""")
# the foot row: Home = the info line (the status, else what to do) + the buttons; Teleport = the buttons, centred. Each sends a = "f<word>".
M(page, r"""
public void foot(@UCB@ b, @UEB@ ev, boolean home, String info) {
  java.util.ArrayList ws = new java.util.ArrayList();
  boolean add = this.editing && this.addSlot >= 0;
  if (add) {
    if (this.addPage > 0) ws.add("aprev");
    if (this.addPage < this.addPages - 1) ws.add("anext");
    ws.add("acancel");
  } else if (this.editing) {
    if (this.editSel >= 0) ws.add("eremove");
    ws.add("ereset");
    if (@PKG@.MenuUtil.isAdmin(this.playerRef)) { ws.add("esrv"); ws.add("estd"); }
    if (home && @PKG@.MenuLayout.oldOf(this.playerRef.getUuid()) != null) ws.add("eold");
    if (home && this.editSel < 0 && @PKG@.MenuLayout.hasOldDefault() && @PKG@.MenuUtil.isAdmin(this.playerRef)) ws.add("edold");
    if (!home && this.pageNo > 0) ws.add("prev");                   // 0.3.38: Arrange pages through the auto tiles too
    if (!home && this.pageNo < this.pages - 1) ws.add("next");
    ws.add("edone");
  } else {
    ws.add("hedit");
    if (!home && this.pageNo > 0) ws.add("prev");
    if (!home && this.pageNo < this.pages - 1) ws.add("next");
    ws.add("close");
  }
  String par = home ? "#SkyyMHmFoot" : "#SkyyMTpFoot";
  int used = 0;
  for (int k = 0; k < ws.size(); k++) {
    int fi = fbIndex((String) ws.get(k));
    used = used + (home ? @PKG@.MenuData.FB_W[fi] : @PKG@.MenuData.FB_TW[fi]) + @PKG@.MenuData.FB_GAP;
  }
  if (home) {
    b.appendInline(par, @PKG@.MenuData.UI_HINFO0 + (@PKG@.MenuData.HOME_FOOT_W - used) + @PKG@.MenuData.UI_HINFO1);
    b.set("#SkyyMHmInfo.Text", info == null ? "" : info);
  } else {
    int lead = (@PKG@.MenuData.TP_FOOT_W - used + @PKG@.MenuData.FB_GAP) / 2;
    if (lead > 0) b.appendInline(par, "Group { Anchor: (Width: " + lead + "); }");
  }
  for (int k = 0; k < ws.size(); k++) {
    String w = (String) ws.get(k);
    int fi = fbIndex(w);
    if (home || k > 0) b.appendInline(par, @PKG@.MenuData.UI_FSP);
    b.appendInline(par, home ? @PKG@.MenuData.UI_FBH[fi] : @PKG@.MenuData.UI_FBT[fi]);
    ev.addEventBinding(@BT@.Activating, (home ? "#SkyyMHmF" : "#SkyyMTpF") + w, @EVD@.of("a", "f" + w));
  }
}""")
# 0.3.30: Home and Teleport scaled up - the kit's 38 px title bar holds the crest + the page title; row 1 (and Teleport's row 2) are drawn
# big as the body's first children (bigRow / bigTabs); the close X is the shell's (bound here: a = "hub:close")
M(page, r"""
public void buildDash(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st, java.util.ArrayList slots, boolean tipsOff) {
  boolean home = this.view.equals("main");
  java.util.UUID me = this.playerRef.getUuid();
  String stx = this.status == null ? "" : this.status;
  boolean add = this.editing && this.addSlot >= 0;
  @PKG@.MenuHub.ensure(me);
  if (home) {
    String sp = spillNote();
    if (sp != null) {
      stx = sp;
      try { this.playerRef.sendMessage(@MSG@.raw("[SkyWynn Menu] " + sp)); } catch (Throwable t) { }
    }
""" + "\n".join("    " + ln for ln in HOME_JAVA.split("\n")) + r"""
    """ + HOME_PAGE17 + r"""   // 0.3.35: row 1 (kit 1.7)
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HLEAD);
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HMAIN);
    youPanel(b, ev, ref, st);
    b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HSP16);
    b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HMID);
    b.appendInline("#SkyyMHmMid", @PKG@.MenuData.UI_HMIDT);
    b.appendInline("#SkyyMHmMid", @PKG@.MenuData.UI_HGAP5);
    b.appendInline("#SkyyMHmMid", @PKG@.MenuData.UI_HGW);
    b.appendInline("#SkyyMGW", tipsOff ? @PKG@.MenuData.UI_HGRIDNT : @PKG@.MenuData.UI_HGRID);
    b.appendInline("#SkyyMHmMain", @PKG@.MenuData.UI_HSP16);
    nowPanel(b, ev, ref, st);
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HGAP8);
    b.appendInline("#SkyyMHome", @PKG@.MenuData.UI_HFOOT);
    String info = stx.length() > 0 ? stx : (add ? @PKG@.MenuData.HT_ADD : (this.editing ? @PKG@.MenuData.HT_EDIT : (tipsOff ? @PKG@.MenuData.HT_HINT_OFF : @PKG@.MenuData.HT_HINT)));
    foot(b, ev, true, info);
    b.set("#SkyyMHmMidT.Text", add ? @PKG@.MenuData.HT_MID_ADD + pageOf(this.addPage, this.addPages)
                                   : (this.editing ? @PKG@.MenuData.HT_MID_EDIT : @PKG@.MenuData.HT_MID));
    ev.addEventBinding(@BT@.Dismissing, "#SkyyMHm", @EVD@.of("a", "mesc"), false);
    ev.addEventBinding(@BT@.Activating, "#SkyyMHmHubClose", @EVD@.of("a", "hub:close"));
  } else {
""" + "\n".join("    " + ln for ln in TP_JAVA.split("\n")) + r"""
    """ + TP_PAGE17 + r"""   // 0.3.35: rows 1 + 2 (kit 1.7)
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TLEADY);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TROW);
    b.appendInline("#SkyyMTpRow", @PKG@.MenuData.UI_TLEAD);
    b.appendInline("#SkyyMTpRow", @PKG@.MenuData.UI_HGW);
    b.appendInline("#SkyyMGW", tipsOff ? @PKG@.MenuData.UI_HGRIDNT : @PKG@.MenuData.UI_HGRID);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TGAP);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TINFO);
    b.appendInline("#SkyyMTpInfo", @PKG@.MenuData.UI_TIN);
    b.appendInline("#SkyyMTpInfo", @PKG@.MenuData.UI_TID);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TGAP);
    b.appendInline("#SkyyMTpB", @PKG@.MenuData.UI_TFOOT);
    foot(b, ev, false, null);
    String iname = this.infoName;
    String ibody = this.infoBody;
    if (iname == null) {
      iname = add ? "Add a teleport" + pageOf(this.addPage, this.addPages)
                  : (this.editing ? "Editing the Teleport page - no dragging" : "Teleport" + pageOf(this.pageNo, this.pages));
      ibody = add ? @PKG@.MenuData.HT_ADD : (this.editing ? @PKG@.MenuData.HT_EDIT : @PKG@.MenuData.HT_TP_HINT);
    }
    String[] lines = (ibody == null ? "" : ibody).split("\n");
    b.set("#SkyyMTpIN.Text", iname);
    b.set("#SkyyMTpID.Text", stx.length() > 0 ? stx : (lines.length > 0 ? lines[0] : ""));   // 0.3.30: the status line moved into the info box
    ev.addEventBinding(@BT@.Dismissing, "#SkyyMTp", @EVD@.of("a", "mesc"), false);
    ev.addEventBinding(@BT@.Activating, "#SkyyMTpHubClose", @EVD@.of("a", "hub:close"));
  }
  b.set("#SkyyMGrid.Slots", slots);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyMGrid", @EVD@.of("a", "mslot"), false);
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.cleared = false;
  this.lastSend = System.currentTimeMillis();
  if (!this.watching && ref != null && st != null) {
    this.watching = true;
    try {
      Object ex = st.getExternalData();
      if (ex instanceof @EST@) this.world = ((@EST@) ex).getWorld();
    } catch (Throwable tw) { this.world = null; }
    this.joinSeen = @PKG@.PageGuard.joins(this.playerRef.getUuid());
    @PKG@.MenuWatch.schedule(this);
  }
  boolean tipsOff = @PKG@.Tips.isOff(this.playerRef.getUuid());
  boolean dash = isDash();
  int gn = dash ? @PKG@.MenuData.HG_N : 54;
  this.gridN = gn;
  this.acts = new String[54];
  this.names = new String[54];
  this.bodies = new String[54];
  this.hid = new boolean[54];
  java.util.ArrayList slots = new java.util.ArrayList();
  for (int i = 0; i < gn; i++) slots.add(filler());
  try { fill(slots); } catch (Throwable t) { @PKG@.MenuUtil.warn("menu view " + this.view + " failed: " + t); }
  if (dash) { buildDash(ref, b, ev, st, slots, tipsOff); return; }
  String stx = this.status == null ? "" : this.status;
  int nInfo = @PKG@.MenuData.CL_INFO_LINES;
  @PKG@.MenuHub.ensure(this.playerRef.getUuid());
  if (hubName().equals("social")) {
""" + "\n".join("    " + ln for ln in MH_JAVA["social"].split("\n")) + r"""
  } else {
""" + "\n".join("    " + ln for ln in MH_JAVA["settings"].split("\n")) + r"""
  }
  // 0.3.35: the grid (left) + the info panel (right) in the kit 1.7 page; the footer: hint / status, the grid's page arrows, Close
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_CGRIDWRAP);
  b.appendInline("#SkyyMGridWrap", tipsOff ? @PKG@.MenuData.UI_CGRIDNT : @PKG@.MenuData.UI_CGRID);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_CGAP);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_CINFOBOX);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_CINFONAME);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_CINFODESC);
  for (int i = 0; i < nInfo; i++) b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_CINFO[i]);
  b.appendInline("#SkyyMenuHFoot", stx.length() > 0 ? @PKG@.MenuData.UI_CHINTST : @PKG@.MenuData.UI_CHINT);
  b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CFSP);
  if (this.pages > 1) {
    b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CPREV);
    b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CFSP);
    b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CNEXT);
    b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CFSP);
    ev.addEventBinding(@BT@.Activating, "#SkyyMPrev", @EVD@.of("a", "mprev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyMNext", @EVD@.of("a", "mnext"));
  } else {
    b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CNOPAGE);
  }
  b.appendInline("#SkyyMenuHFoot", @PKG@.MenuData.UI_CCLOSE);
  ev.addEventBinding(@BT@.Activating, "#SkyyMClose", @EVD@.of("a", "mclose"));
  String hint = tipsOff ? "Tooltips off - the speech bubble at the top right turns them on. Click an item to use it."
                        : "Hover an item for details - click it to use it. Esc closes the menu.";
  b.set("#SkyyMHint.Text", stx.length() > 0 ? stx : hint);
  String iname = this.infoName;
  String ibody = this.infoBody;
  if (iname == null) {
    int vi = @PKG@.MenuData.viewIndex(this.view);
    iname = this.title;
    ibody = @PKG@.MenuData.V_INTRO[vi];
  }
  String[] lines = (ibody == null ? "" : ibody).split("\n");
  b.set("#SkyyMInfoName.Text", iname == null ? "" : iname);
  b.set("#SkyyMInfoDesc.Text", lines.length > 0 ? lines[0] : "");
  for (int i = 0; i < nInfo; i++) {
    String t = i + 1 < lines.length ? lines[i + 1] : "";
    if (i == nInfo - 1 && lines.length > nInfo + 1) t = t + "   ...";
    b.set("#SkyyMInfo" + i + ".Text", t);
  }
  b.set("#SkyyMGrid.Slots", slots);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyMGrid", @EVD@.of("a", "mslot"), false);
  ev.addEventBinding(@BT@.Dismissing, "#SkyyMenuH", @EVD@.of("a", "mesc"), false);
  """ + MH_BUILD + r"""
}""")
M(page, r"""
public void open(String v) {
  this.view = v;
  this.pageNo = 0;
  this.infoName = null;
  this.infoBody = null;
}""")
M(page, r"""
public void goBack() {
  if (this.view.equals("player")) open("players");
  else open("main");
}""")
# 0.1.3 stuck-tooltip mitigation: ONE update that empties every slot (the hovered one too) while the page is still open, sent before
# the server closes the menu or hands it to a page command. Only called while this menu is the open page (click handlers, CloseTask
# checks it). Acknowledged like any update (never a Dismiss); build() resets the flag.
M(page, r"""
public void clearGrid() {
  if (this.cleared) return;
  this.cleared = true;
  try {
    java.util.ArrayList empty = new java.util.ArrayList();
    for (int i = 0; i < this.gridN; i++) empty.add(new @IGS@());   // 0.3.29: the grid on screen (35 on Home / Teleport)
    @UCB@ b = new @UCB@();
    b.set("#SkyyMGrid.Slots", empty);
    sendUpdate(b);
    this.lastSend = System.currentTimeMillis();
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not clear the menu grid: " + t); }
}""")
M(page, r"""
public void closePage(@REF@ ref, @ST@ st) {
  clearGrid();
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().setPage(ref, st, @PGE@.None);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not close the menu: " + t); }
}""")
# ================= CloseTask (0.1.2): close the menu after a command ONLY if the menu is still the open page =================
# 0.3.6: ... and only if the player did not change world since the menu opened (the Island / Hub tile: this task runs on the NEW world,
# where the client shows no page any more). Such a menu is forgotten on the server like Esc (PageGuard.forget: no packet, counter
# unchanged); 0.3.5 closed it with setPage(None) = +1 page acknowledgement the client never sends -> every page ignored clicks.
# (a page command replaces the menu by itself; closing first made the client's close answer dismiss the NEW page server-side)
clo_.addInterface(pool.get("java.lang.Runnable"))
clo_.addInterface(pool.get("java.util.function.BiConsumer"))
F(clo_, "public @PKG@.MenuPage page;")
F(clo_, "public @PR@ pr;")
F(clo_, "public @WLD@ expected;")
C(clo_, r"""
public CloseTask(@PKG@.MenuPage page, @PR@ pr) { this.page = page; this.pr = pr; this.expected = null; }""")
M(clo_, r"""
public void accept(Object result, Object error) {
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(this, 150L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule the menu close: " + t); }
}""")
M(clo_, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    if (this.expected == null) {
      java.util.UUID wu = this.pr.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) return;
      this.expected = w;
      w.execute(this);
      return;
    }
    java.util.UUID wu2 = this.pr.getWorldUuid();
    if (wu2 == null || @UNI@.get().getWorld(wu2) != this.expected) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    @PGM@ pm = p.getPageManager();
    if (pm == null || pm.getCustomPage() != this.page) return;
    if (this.page.changedWorld(this.expected)) {
      if (@PKG@.PageGuard.forget(pm, r, st, this.page)) @PKG@.MenuUtil.info("the menu close after a command found the menu of " + @PKG@.PageGuard.who(this.pr) + " still open on the server after a world change - forgot it there too instead of closing it (no packet)");
      return;
    }
    this.page.closePage(r, st);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu close failed: " + t); }
}""")
# run a command AS THIS PLAYER (vanilla /su pattern); installed + permission are checked first so the player gets a clear answer.
# The permission check fails CLOSED: the engine's AbstractCommand.acceptCall0 calls the same hasPermission, so if it throws here the
# command could not run anyway - say so in the menu instead of closing it and leaving a cryptic chat error.
M(page, r"""
public void runCmd(@REF@ ref, @ST@ st, String line, boolean close) {
  String name = @PKG@.MenuUtil.firstWord(line);
  @ACM@ c = @PKG@.MenuUtil.cmd(name);
  if (c == null) { this.status = "/" + name + " is not on this server - that mod is not installed."; rebuild(); return; }
  String need = @PKG@.MenuUtil.needOf(line);
  if (need != null) { this.status = "/" + line + " needs " + need + " - this server has an older version."; rebuild(); return; }
  boolean ok = false;
  boolean checked = true;
  try { ok = c.hasPermission(this.playerRef); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("permission check for /" + name + " failed: " + t); ok = false; checked = false; }
  if (!checked) {
    this.status = "Could not check your permission for /" + name + ". Ask an admin.";
    rebuild();
    return;
  }
  if (!ok) {
    String node = null;
    try { node = c.getPermission(); } catch (Throwable t) { }
    this.status = "You do not have permission for /" + name + (node == null ? "" : " (" + @PKG@.MenuUtil.safe(node) + ")") + ". Ask an admin.";
    rebuild();
    return;
  }
  if (close) clearGrid();
  java.util.concurrent.CompletableFuture fut = null;
  try { fut = @CMGR@.get().handleCommand(this.playerRef, line); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("/" + line + " failed: " + t); this.status = "/" + name + " could not be run."; rebuild(); return; }
  if (close) {
    @PKG@.CloseTask ct = new @PKG@.CloseTask(this, this.playerRef);
    if (fut != null) fut.whenComplete(ct); else ct.accept(null, null);
  }
  if (!close) {
    this.status = "/" + line + "  - see your chat";
    rebuild();
    @PKG@.RefreshTask.schedule(this, this.playerRef, 900L);
  }
}""")
# same calls as vanilla WarpCommand.tryGo / SpawnCommand: add a Teleport component on the player's world thread,
# and record the old position in vanilla TeleportHistory so /tp back works (SkyyEssentials pattern)
# 0.3.18: the teleport itself (Teleport component + the TeleportHistory entry) is moveTo, shared with spawnResolved when the menu was
# closed before the spawn point arrived; teleport() = moveTo + close + the chat line, exactly 0.3.17's steps in 0.3.17's order
M(page, r"""
public void moveTo(@REF@ ref, @ST@ st, @TP@ t, String label) {
  @WLD@ here = null;
  try { java.util.UUID wu = this.playerRef.getWorldUuid(); here = wu == null ? null : @UNI@.get().getWorld(wu); } catch (Throwable t0) { }
  @TC@ mtc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
  @HR@ mhr = (@HR@) st.getComponent(ref, @HR@.getComponentType());
  st.addComponent(ref, @TP@.getComponentType(), t);
  try {
    if (here != null && mtc != null && mtc.getPosition() != null) {
      @V3D@ p = mtc.getPosition();
      @R3F@ r = mhr != null ? mhr.getRotation() : null;
      @TPH@ h = (@TPH@) st.ensureAndGetComponent(ref, @TPH@.getComponentType());
      if (h != null) h.append(here, new @V3D@(p.x, p.y, p.z), r != null ? new @R3F@(r.x, r.y, r.z) : new @R3F@(), "Menu: " + label);
    }
  } catch (Throwable t2) { }
}""")
M(page, r"""
public boolean teleport(@REF@ ref, @ST@ st, @TP@ t, String label) {
  if (st.getComponent(ref, @TP@.getComponentType()) != null) { this.status = "You are already teleporting."; rebuild(); return false; }
  moveTo(ref, st, t, label);
  closePage(ref, st);
  this.playerRef.sendMessage(@MSG@.raw("[Menu] Teleporting to " + label + "..."));
  return true;
}""")
# 0.3.18 (Hytale 0.7.0): the spawn point is a CompletableFuture now (getSpawnPointAsync; the height-map provider loads a chunk first).
# Never waited for on the world thread: SpawnTask gets it (whenComplete), hops to the player's world thread and calls spawnResolved.
# There: the menu still open -> teleport() as 0.3.17; closed meanwhile -> moveTo + the chat line (no page touched); no spawn point / an
# error -> 0.3.17's status line on the open menu, else a chat line.
M(page, r"""
public void spawnResolved(@REF@ ref, @ST@ st, @WLD@ target, Object result, Throwable error) {
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  boolean open = p != null && p.getPageManager() != null && p.getPageManager().getCustomPage() == this;
  if (error != null) @PKG@.MenuUtil.warn("the spawn point of the main world could not be found for " + @PKG@.PageGuard.who(this.playerRef) + ": " + error);
  if (error != null || !(result instanceof @TRF@)) {
    String why = error != null ? "The spawn point could not be found - try again." : "The main world has no spawn point.";
    if (open) { this.status = why; rebuild(); }
    else this.playerRef.sendMessage(@MSG@.raw("[Menu] " + why));
    return;
  }
  @TP@ t = @TP@.createForPlayer(target, (@TRF@) result);
  if (open) { teleport(ref, st, t, "Spawn"); return; }
  if (st.getComponent(ref, @TP@.getComponentType()) != null) return;
  moveTo(ref, st, t, "Spawn");
  this.playerRef.sendMessage(@MSG@.raw("[Menu] Teleporting to Spawn..."));
}""")
F(spt, "public @PKG@.MenuPage page;")
F(spt, "public @PR@ pr;")
F(spt, "public @WLD@ target;")
F(spt, "public @WLD@ home;")
F(spt, "public volatile Object result;")
F(spt, "public volatile Throwable error;")
spt.addInterface(pool.get("java.lang.Runnable"))
spt.addInterface(pool.get("java.util.function.BiConsumer"))
C(spt, r"""
public SpawnTask(@PKG@.MenuPage page, @PR@ pr, @WLD@ target, @WLD@ home) { this.page = page; this.pr = pr; this.target = target; this.home = home; }""")
# any thread (the future's): keep the answer, hop to the world the player clicked in
M(spt, r"""
public void accept(Object r, Object e) {
  this.result = r;
  this.error = e instanceof Throwable ? (Throwable) e : null;
  try { this.home.execute(this); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not finish the Spawn teleport: " + t); }
}""")
# that world's thread: only while the player is still in it (a world change meanwhile = they went somewhere else - nothing to do)
M(spt, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    java.util.UUID wu = this.pr.getWorldUuid();
    if (wu == null || @UNI@.get().getWorld(wu) != this.home) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    this.page.spawnResolved(r, st, this.target, this.result, this.error);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("the Spawn teleport failed: " + t); }
}""")
M(page, r"""
public void doSpawn(@REF@ ref, @ST@ st) {
  @WLD@ target = @UNI@.get().getDefaultWorld();
  if (target == null) { this.status = "The main world is not loaded."; rebuild(); return; }
  @WLD@ home = null;
  try { java.util.UUID wu = this.playerRef.getWorldUuid(); home = wu == null ? null : @UNI@.get().getWorld(wu); } catch (Throwable t0) { }
  if (home == null) { this.status = "The main world has no spawn point."; rebuild(); return; }
  java.util.concurrent.CompletableFuture f = target.getWorldConfig().getSpawnProvider().getSpawnPointAsync(target, this.playerRef.getUuid());
  if (f == null) { this.status = "The main world has no spawn point."; rebuild(); return; }
  f.whenComplete(new @PKG@.SpawnTask(this, this.playerRef, target, home));
}""")
# 0.3.37: an island home / a home tile: the owner mod's bridge does the teleport with its own rules. Island: the page closes first (the
# /island teleport may change worlds - the My Island tile's order); /island's chat line says what happened. Home: "ok" = queued on the
# player's world thread -> the page closes; else the reason stays in the status line.
M(page, r"""
public void goHome(@REF@ ref, @ST@ st, String name, boolean island) {
  String key = island ? "island:fn:gohome" : "essentials:fn:gohome";
  Object f = @PKG@.MenuUtil.bridge().get(key);
  if (!(f instanceof java.util.function.Function)) { this.status = island ? "Island homes are not on this server right now." : "Homes are not on this server right now."; rebuild(); return; }
  Object[] a = new Object[] { this.playerRef.getUuid(), name };
  if (island) {
    closePage(ref, st);
    try { ((java.util.function.Function) f).apply(a); } catch (Throwable t) { @PKG@.MenuUtil.warn("the bridge " + key + " failed: " + t); }
    return;
  }
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(a); } catch (Throwable t) { @PKG@.MenuUtil.warn("the bridge " + key + " failed: " + t); r = null; }
  String s = r == null ? "" : String.valueOf(r);
  if (s.equals("ok")) { closePage(ref, st); return; }
  this.status = s.length() == 0 ? "That did not work - try again." : "Could not go home: " + s;
  rebuild();
}""")
M(page, r"""
public void doWarp(@REF@ ref, @ST@ st, String key) {
  @TPP@ tp = @TPP@.get();
  if (tp == null || !tp.isWarpsLoaded()) { this.status = "Warps are still loading - try again in a moment."; rebuild(); return; }
  @WRP@ w = (@WRP@) tp.getWarps().get(key);
  if (w == null) { this.status = "That warp was removed."; rebuild(); return; }
  String id = @PKG@.MenuUtil.safe(w.getId());
  if (!@PKG@.MenuUtil.isWarpUnlocked(this.playerRef, w.getId())) { this.status = "You have not unlocked the warp " + id + " yet."; rebuild(); return; }
  @WLD@ target = @UNI@.get().getWorld(w.getWorld());
  @TP@ t = w.toTeleport();
  if (target == null || t == null) { this.status = "The world of warp " + id + " is not loaded."; rebuild(); return; }
  teleport(ref, st, t, "warp " + id);
}""")
M(page, r"""
public void playerAction(@REF@ ref, @ST@ st, int i) {
  if (i < 0 || i >= @PKG@.MenuData.PA_CMD.length) return;
  @PR@ target = selected();
  if (target == null) { open("players"); this.status = "That player went offline."; rebuild(); return; }
  String n = @PKG@.MenuUtil.cleanName(target.getUsername());
  if (n.length() == 0) { this.status = "That player's name cannot be used in a command."; rebuild(); return; }
  runCmd(ref, st, @PKG@.MenuData.PA_CMD[i].replace("%P", n), @PKG@.MenuData.PA_CLOSE[i]);
}""")
# 0.2: the torch (slot 51; 0.3.3: slot 39) opens the Settings page straight from the menu - never closing first (the 0.1.2 rule). The grid is emptied
# once before the hand-off (the 0.1.3 stuck-tooltip rule for every page hand-off; an update is acknowledged like any other).
M(page, r"""
public void openSettings(@REF@ ref, @ST@ st) {
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  clearGrid();
  p.getPageManager().openCustomPage(ref, st, new @PKG@.SettingsPage(this.playerRef, -1));
}""")
# 0.3: the book (slot 41) and an admin's click on a set-up mod open Server Setup straight from the menu (never closing first); the grid
# is emptied once before the hand-off like every page hand-off. The node is checked here AND by the page's own guard().
M(page, r"""
public void openAdmin(@REF@ ref, @ST@ st, String mod) {
  if (!@PKG@.MenuUtil.isAdmin(this.playerRef)) { this.status = "You do not have access to Server Setup."; rebuild(); return; }
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  clearGrid();
  p.getPageManager().openCustomPage(ref, st, new @PKG@.AdminPage(this.playerRef, mod == null ? "list" : "mod", mod));
}""")
# 0.3.10: the Your Profile tile opens the Stats page straight from the menu (never closing first); the grid is emptied once before
# the hand-off like every page hand-off (openSettings / openAdmin)
M(page, r"""
public void openStats(@REF@ ref, @ST@ st) {
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  clearGrid();
  p.getPageManager().openCustomPage(ref, st, new @PKG@.StatsPage(this.playerRef, 0));
}""")
# 0.3.16: a bridge tile (the Wardrobe) hands the player to another mod's page through its bridge Function, straight from the menu
# (never closing first; the grid is emptied once before the hand-off like openSettings / openStats). Contract: apply(UUID player) on the
# player's world thread opens that mod's page and answers Boolean.TRUE; anything else = the menu stays and says so - but ONLY while the
# menu is still the player's page: a callee that opened its page and then threw / answered non-TRUE owns the screen, so the menu sends
# nothing more (a page update to a page the client no longer shows = the stuck page acknowledgement watchTick heals).
M(page, r"""
public void openBridge(@REF@ ref, @ST@ st, String key) {
  Object f = @PKG@.MenuUtil.bridge().get(key);
  if (!(f instanceof java.util.function.Function)) { this.status = "That page is not on this server right now."; rebuild(); return; }
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  @PGM@ pm = p.getPageManager();
  if (pm == null) return;
  clearGrid();
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(this.playerRef.getUuid()); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("the menu tile " + key + " failed: " + t); r = null; }
  if (Boolean.TRUE.equals(r)) return;
  if (pm.getCustomPage() != this) { @PKG@.MenuUtil.warn("the menu tile " + key + " opened another page but answered " + String.valueOf(r) + " - left that page alone"); return; }
  this.status = "That page could not be opened right now.";
  rebuild();
}""")
# 0.3.17: THE LAYOUT EDITOR'S CLICKS (main view, world thread). First click on a tile = pick it up; a click on another slot (a tile or an
# Empty slot) = swap + save (MenuLayout.swap); the picked-up tile again = cancel; a hidden tile's slot (not drawn) is never a target
# (a stale / forged click on it gets KEPT_MSG); a layout file that cannot be read right now is never changed (EDIT_WAIT). Reset / the two admin buttons need a second click (cfgArm, the modcfg pattern); the admin node is re-checked on the click.
# ================= 0.3.29 EDIT SHORTCUTS (Home + Teleport; Skyy 2026-10-15 "have a way to remove and add them. so you can pick what shows up.
# and how its organized"). No dragging (AreItemsDraggable: false - every text says so): a tile click picks it up, another slot swaps / moves,
# Remove takes it off, an empty slot opens + Add. Saved at once per account (MenuLayout.put). Reset / Set default / Clear default / Old tiles
# back need a second click (cfgArm); the admin node is re-checked on the click. A layout file that cannot be read is never changed.
M(page, r"""
public void leaveEdit() {
  this.editing = false;
  this.editSel = -1;
  this.addSlot = -1;
}""")
M(page, r"""
public void startEdit() {
  @PKG@.MenuLayout.SPILL.remove(this.playerRef.getUuid().toString());   // fix: the 5 x 5 spill note is seen - Right now drops its row
  this.editing = true;
  this.editSel = -1;
  this.addSlot = -1;
  this.addPage = 0;
  this.infoName = null;
  this.infoBody = null;
  this.status = @PKG@.MenuData.HT_EDIT_START;
}""")
# a changed grid saved (part 0 Home / 1 Teleport); false = it failed (the page already says so)
M(page, r"""
public boolean saveGrid(int p, String[] g) {
  if (@PKG@.MenuLayout.put(this.playerRef.getUuid(), this.playerRef.getUsername(), p, g) == 1) return true;
  this.status = "That did not work - try again.";
  rebuild();
  return false;
}""")
M(page, r"""
public void dashEditClick(int idx, String act) {
  java.util.UUID me = this.playerRef.getUuid();
  if (@PKG@.MenuLayout.unreadable(me)) { this.editSel = -1; this.addSlot = -1; this.status = @PKG@.MenuData.EDIT_WAIT; rebuild(); return; }
  int p = part();
  if (act.equals("eadd")) {
    if (this.addSlot < 0 || this.addKeys == null || idx < 0 || idx >= this.addKeys.length || this.addKeys[idx] == null) { this.status = "Pick a shortcut from the list."; rebuild(); return; }
    String k = this.addKeys[idx];
    String[] g = @PKG@.MenuLayout.grid(me, p);
    int at = this.addSlot;
    this.addSlot = -1;
    if (at < 0 || at >= g.length || g[at] != null) { this.status = "That slot is not free any more - nothing was added."; rebuild(); return; }
    if (@PKG@.MenuLayout.hasSame(g, k)) { this.status = nameOf(k) + " is on your grid already (that page has one shortcut)."; rebuild(); return; }
    g[at] = k;
    if (!saveGrid(p, g)) return;
    this.status = nameOf(k) + " added.";
    rebuild();
    return;
  }
  if (!act.equals("eslot") || this.grid == null || idx < 0 || idx >= this.grid.length) { rebuild(); return; }
  if (this.editSel < 0) {
    if (this.hid[idx]) { this.status = @PKG@.MenuData.KEPT_MSG; rebuild(); return; }
    if (this.grid[idx] == null && this.autoAt != null && idx < this.autoAt.length && this.autoAt[idx] != null) {   // 0.3.37: an auto tile: pinned here + picked up
      String ak = this.autoAt[idx];
      if (!@PKG@.MenuLayout.okKey(ak, p == 1)) { this.status = nameOf(ak) + " can't be arranged (its name has characters a layout can't save) - it stays in the free slots."; rebuild(); return; }   // 0.3.38
      String[] g = @PKG@.MenuLayout.copy(this.grid);
      if (@PKG@.MenuLayout.has(g, ak)) { rebuild(); return; }
      g[idx] = ak;
      if (!saveGrid(p, g)) return;
      this.editSel = idx;
      this.status = "Picked up " + nameOf(ak) + " - click the slot where it should go (no dragging).";
      rebuild();
      return;
    }
    if (this.grid[idx] == null) { this.addSlot = idx; this.addPage = 0; this.status = ""; rebuild(); return; }
    this.editSel = idx;
    this.status = "Picked up " + nameOf(this.grid[idx]) + " - click another slot to move it there, or press Remove.";
    rebuild();
    return;
  }
  if (idx == this.editSel) { this.editSel = -1; this.status = "Cancelled - nothing moved."; rebuild(); return; }
  int from = this.editSel;
  this.editSel = -1;
  if (this.hid[idx] || this.hid[from]) { this.status = @PKG@.MenuData.KEPT_MSG; rebuild(); return; }
  String[] g = @PKG@.MenuLayout.copy(this.grid);
  String a = g[from];
  String bb = g[idx];
  if (a == null) { this.status = "That move did not work - try again."; rebuild(); return; }
  g[idx] = a;
  g[from] = bb;
  if (!saveGrid(p, g)) return;
  this.status = bb != null ? nameOf(a) + " and " + nameOf(bb) + " swapped places." : nameOf(a) + " moved.";
  rebuild();
}""")
M(page, r"""
public void footClick(@REF@ ref, @ST@ st, String w) {
  String armed = this.cfgArm;
  this.cfgArm = null;
  this.status = "";
  java.util.UUID me = this.playerRef.getUuid();
  if (w.equals("close")) { closePage(ref, st); return; }
  if (w.equals("hedit")) {
    if (@PKG@.MenuLayout.unreadable(me)) { this.status = @PKG@.MenuData.EDIT_WAIT; rebuild(); return; }
    startEdit();
    rebuild();
    return;
  }
  if (w.equals("prev")) { if (this.pageNo > 0) this.pageNo = this.pageNo - 1; rebuild(); return; }
  if (w.equals("next")) { this.pageNo = this.pageNo + 1; rebuild(); return; }
  if (!this.editing) { rebuild(); return; }
  if (w.equals("acancel")) { this.addSlot = -1; this.status = "Nothing was added."; rebuild(); return; }
  if (w.equals("aprev")) { if (this.addPage > 0) this.addPage = this.addPage - 1; rebuild(); return; }
  if (w.equals("anext")) { this.addPage = this.addPage + 1; rebuild(); return; }
  if (w.equals("edone")) {
    leaveEdit();
    @PKG@.MenuLayout.MIGRATED.remove(me.toString());
    this.status = "Saved - your shortcuts work as normal again.";
    rebuild();
    return;
  }
  if (@PKG@.MenuLayout.unreadable(me)) { this.editSel = -1; this.status = @PKG@.MenuData.EDIT_WAIT; rebuild(); return; }
  int p = part();
  if (w.equals("eremove")) {
    if (this.editSel < 0 || this.grid == null || this.editSel >= this.grid.length || this.grid[this.editSel] == null) { this.editSel = -1; this.status = "Pick a tile up first, then press Remove."; rebuild(); return; }
    String[] g = @PKG@.MenuLayout.copy(this.grid);
    String gone = g[this.editSel];
    g[this.editSel] = null;
    this.editSel = -1;
    if (!saveGrid(p, g)) return;
    this.status = nameOf(gone) + " removed - it waits in + Add (click an empty slot).";
    rebuild();
    return;
  }
  if (w.equals("esrv") || w.equals("estd") || w.equals("edold")) {
    if (!@PKG@.MenuUtil.isAdmin(this.playerRef)) { this.status = "Only admins can change the server default shortcuts."; rebuild(); return; }
  }
  if (w.equals("edold") && p != 0) { this.status = "Old default works on the Home page."; rebuild(); return; }
  if (!w.equals(armed) && (w.equals("ereset") || w.equals("esrv") || w.equals("estd") || w.equals("eold") || w.equals("edold"))) {
    this.cfgArm = w;
    if (w.equals("ereset")) this.status = "Click Reset again: this page goes back to the default shortcuts.";
    else if (w.equals("esrv")) this.status = "Click Set default again: YOUR shortcuts become the server default (for players without their own).";
    else if (w.equals("estd")) this.status = "Click Clear default again: the standard shortcuts become the server default again.";
    else if (w.equals("edold")) this.status = "Click Old default again: the server default gets its old tiles back (as before the update).";
    else this.status = "Click Old tiles back again: your old menu tiles come back in place of the hubs.";
    rebuild();
    return;
  }
  this.editSel = -1;
  if (w.equals("ereset")) {
    @PKG@.MenuLayout.put(me, this.playerRef.getUsername(), p, null);
    this.status = "Back to the default shortcuts.";
  } else if (w.equals("esrv")) {
    if (@PKG@.MenuLayout.saveDefault(p, @PKG@.MenuLayout.grid(me, p)) == 1) this.status = "Saved - every player without their own shortcuts now gets yours.";
    else this.status = "That did not work - try again.";
  } else if (w.equals("estd")) {
    @PKG@.MenuLayout.clearDefault(p);
    this.status = "The standard shortcuts are the server default again.";
  } else if (w.equals("eold")) {
    String[] g = @PKG@.MenuLayout.oldTilesBack(me);
    if (g == null || @PKG@.MenuLayout.put(me, this.playerRef.getUsername(), 0, g) != 1) this.status = "There is no old layout to bring back.";
    else this.status = "Your old tiles are back where they were (the ones that did not fit wait in + Add).";
  } else if (w.equals("edold")) {
    String[] g = @PKG@.MenuLayout.oldDefaultBack();
    if (g == null || @PKG@.MenuLayout.saveDefault(0, g) != 1) this.status = "The server default has no old layout to bring back.";
    else this.status = "The server default has its old tiles back (for players without their own shortcuts).";
  }
  rebuild();
}""")
# a shortcut / a row-1 hub / an alert opens a tab: SkyyMenu's own views switch IN PLACE (the page stays, the mouse spot stays), its own pages
# open straight from the menu (the grid emptied first), any other tab through its bridge Function, else its command (HubBar.open)
M(page, r"""
public void openTab(@REF@ ref, @ST@ st, String h, String tb) {
  if (h == null || tb == null || @PKG@.MenuHub.hubIndex(h) < 0 || !@PKG@.HubBar.okId(tb)) { this.status = @PKG@.MenuData.HUB_TXT_FAIL; rebuild(); return; }
  if (h.equals("world") && tb.equals("teleport")) { leaveEdit(); open("tp"); rebuild(); return; }
  if (h.equals("social") && tb.equals("players")) { leaveEdit(); open("players"); rebuild(); return; }
  if (h.equals("settings") && tb.equals("mods")) {
    if (!@PKG@.MenuHub.visible("mods", this.playerRef)) { this.status = @PKG@.MenuData.HUB_TXT_FAIL; rebuild(); return; }
    leaveEdit();
    open("mods");
    rebuild();
    return;
  }
  if (h.equals("settings") && tb.equals("layout")) {
    if (@PKG@.MenuLayout.unreadable(this.playerRef.getUuid())) { this.status = @PKG@.MenuData.EDIT_WAIT; rebuild(); return; }
    open("main");
    startEdit();
    rebuild();
    return;
  }
  if (h.equals("character") && tb.equals("stats")) { openStats(ref, st); return; }
  if (h.equals("settings") && tb.equals("settings")) { openSettings(ref, st); return; }
  if (h.equals("settings") && tb.equals("setup")) { openAdmin(ref, st, null); return; }
  clearGrid();
  String r = @PKG@.HubBar.openSub(this.playerRef, this.playerRef.getUuid(), h, tb);   // 0.3.33: a merged page opens too (= open() for the others)
  if ("command".equals(r)) { @PKG@.RefreshTask.schedule(this, this.playerRef, 900L); return; }
  if (@PKG@.MenuHub.opened(r)) return;
  this.status = "missing".equals(r) ? "That page is not on this server right now." : @PKG@.MenuData.HUB_TXT_FAIL;
  rebuild();
}""")
M(page, r"""
public void openHub(@REF@ ref, @ST@ st, String h) {
  int hi = @PKG@.MenuHub.hubIndex(h);
  if (hi < 0) { this.status = @PKG@.MenuData.HUB_TXT_FAIL; rebuild(); return; }
  String tab = @PKG@.HubBar.pickTab(h, this.playerRef.getUuid());
  if (tab == null) { this.status = "[" + @PKG@.MenuData.HUB_TITLE[hi] + "] " + @PKG@.MenuData.HUB_SOON[hi]; rebuild(); return; }
  openTab(ref, st, h, tab);
}""")
M(page, r"""
public void shortcut(@REF@ ref, @ST@ st, String k) {
  if (k.startsWith("hub:")) { openHub(ref, st, k.substring(4)); return; }
  if (k.equals("tab:settings:hud")) {   // fix: the HUD editor directly (= the player typing /skyyhud); no SkyyHud = one chat line
    if (@PKG@.MenuUtil.cmd("skyyhud") != null) { runCmd(ref, st, "skyyhud", true); return; }
    try { this.playerRef.sendMessage(@MSG@.raw("[Menu] The HUD editor is not on this server - SkyyHud is not installed.")); } catch (Throwable t) { }
    return;
  }
  if (k.startsWith("tab:")) {
    String rd = redirect(k, this.playerRef.getUuid());          // 0.3.34: a merged-away tab opens where its page went
    if (rd != null && rd.startsWith("cmd:")) { runCmd(ref, st, rd.substring(4), true); return; }
    String k2 = rd != null ? rd : k;
    int c = k2.indexOf(':', 4);
    if (c > 4) { openTab(ref, st, k2.substring(4, c), k2.substring(c + 1)); return; }
  }
  this.status = "That shortcut does not work any more - Edit shortcuts can remove it.";
  rebuild();
}""")
M(page, r"""
public void youClick(@REF@ ref, @ST@ st) {
  leaveEdit();
  openStats(ref, st);
}""")
M(page, r"""
public void alertClick(@REF@ ref, @ST@ st, String n) {
  int i = -1;
  try { i = Integer.parseInt(n); } catch (Throwable t) { i = -1; }
  this.status = "";
  if (this.alertT == null || i < 0 || i >= this.alertT.length) { rebuild(); return; }
  String t = this.alertT[i] == null ? "" : this.alertT[i];
  if (t.equals("edit")) { openTab(ref, st, "settings", "layout"); return; }
  int c = t.indexOf(':');
  if (c > 0) { openTab(ref, st, t.substring(0, c), t.substring(c + 1)); return; }
  if (@PKG@.MenuHub.hubIndex(t) >= 0) { openHub(ref, st, t); return; }
  this.status = "That note has no page to open.";
  rebuild();
}""")
M(page, r"""
public void click(@REF@ ref, @ST@ st, int idx, String act) {
  this.status = "";
  String armed = this.cfgArm;
  this.cfgArm = null;
  if (act.equals("close")) { closePage(ref, st); return; }
  if (this.editing && isDash()) { dashEditClick(idx, act); return; }   // 0.3.29: Edit shortcuts (Home + Teleport)
  if (act.startsWith("sc:")) { shortcut(ref, st, act.substring(3)); return; }   // 0.3.29: a hub / tab shortcut
  if (act.equals("back")) { goBack(); rebuild(); return; }
  if (act.equals("prev")) { if (this.pageNo > 0) this.pageNo = this.pageNo - 1; rebuild(); return; }
  if (act.equals("next")) { this.pageNo = this.pageNo + 1; rebuild(); return; }
  if (act.startsWith("view:")) { open(act.substring(5)); rebuild(); return; }
  if (act.startsWith("player:")) {
    try { this.selU = java.util.UUID.fromString(act.substring(7)); } catch (Throwable t) { this.selU = null; }
    open("player");
    rebuild();
    return;
  }
  if (act.equals("settings")) { openSettings(ref, st); return; }
  if (act.equals("admin")) { openAdmin(ref, st, null); return; }
  if (act.equals("profile")) { openStats(ref, st); return; }
  if (act.startsWith("bridge:")) { openBridge(ref, st, act.substring(7)); return; }
  if (act.startsWith("modcfg:")) {
    int mk = -1;
    try { mk = Integer.parseInt(act.substring(7)); } catch (Throwable t) { mk = -1; }
    if (mk >= 0 && mk < @PKG@.MenuData.MOD_NAME.length) {
      if (!@PKG@.Tips.isOff(this.playerRef.getUuid()) || act.equals(armed)) { openAdmin(ref, st, @PKG@.MenuData.MOD_NAME[mk]); return; }
      this.cfgArm = act;
      this.infoName = this.names[idx];
      this.infoBody = this.bodies[idx];
      this.status = "Click it again to open its Server Setup page.";
      rebuild();
      return;
    }
  }
  this.infoName = this.names[idx];
  this.infoBody = this.bodies[idx];   // 0.3.29: no Hover Tooltips tile (Settings > General has the switch)
  if (act.equals("info") || act.equals("profile") || act.startsWith("mod:")) { rebuild(); return; }
  if (act.startsWith("locked:")) { this.status = "That warp is locked."; rebuild(); return; }
  if (act.startsWith("cmdc:")) { runCmd(ref, st, act.substring(5), true); return; }
  if (act.startsWith("cmd:")) { runCmd(ref, st, act.substring(4), false); return; }
  if (act.equals("spawn")) { doSpawn(ref, st); return; }
  if (act.startsWith("warp:")) { doWarp(ref, st, act.substring(5)); return; }
  if (act.startsWith("ihome:")) { goHome(ref, st, act.substring(6), true); return; }    // 0.3.37
  if (act.startsWith("zhome:")) { goHome(ref, st, act.substring(6), false); return; }
  if (act.startsWith("pact:")) { playerAction(ref, st, Integer.parseInt(act.substring(5))); return; }
  @PKG@.MenuUtil.warn("unknown menu action " + act);
}""")
# 0.1.3 "mesc" = the experimental Esc hook: never send anything here (a page the client already closed may not acknowledge it and
# PageManager would then drop every later click); CloseTask acts 150 ms later only while this menu is still the open page.
# 0.3.28: a click on the hub bar of a menu view. The X closes (closePage: grid emptied first); "< Menu" = the main view in place; the active
# tab = redraw (a player's page -> the players list); Mods / Menu layout from each other = switched in place (same page); any other tab =
# the grid emptied once, then HubBar.handle (its open Function or its command - RefreshTask redraws the menu when a command opened no
# page); a tab that could not open = the status line.
M(page, r"""
public void hubClick(@REF@ ref, @ST@ st, String data) {
  String a = @PKG@.HubBar.jsonStr(data, "a");
  if (!a.startsWith("hub:")) return;
  this.status = "";
  this.cfgArm = null;
  if (a.equals("hub:close")) { closePage(ref, st); return; }
  String myHub = hubName();
  String myTab = hubTab();
  if (a.startsWith("hub:h:")) {
    String h = a.substring(6);
    if (h.equals("home")) { leaveEdit(); open("main"); rebuild(); return; }
    if (h.equals(myHub)) { if (this.view.equals("player")) open("players"); rebuild(); return; }
    leaveEdit();
    openHub(ref, st, h);
    return;
  }
  if (a.equals("hub:back")) { leaveEdit(); open("main"); rebuild(); return; }
  String id = a.substring(4);
  if (myTab != null && id.equals(myTab)) { if (this.view.equals("player")) open("players"); rebuild(); return; }
  if (myHub.equals("home") || !@PKG@.HubBar.okId(id)) { this.status = @PKG@.MenuData.HUB_TXT_FAIL; rebuild(); return; }
  leaveEdit();
  openTab(ref, st, myHub, id);
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    if (data.indexOf("\"skyymenucheck\"") >= 0) {
      if (this.probeNonce != null && this.probeNonce.length() > 0 && data.indexOf("\"" + this.probeNonce + "\"") >= 0) this.probeSeen = true;
      return;
    }
    if (data.indexOf("mesc\"") >= 0) { new @PKG@.CloseTask(this, this.playerRef).accept(null, null); return; }
    if (data.indexOf("\"hub:") >= 0) { hubClick(ref, st, data); return; }   // 0.3.28: the hub bar of a menu view (0.3.29: + row 1)
    if (data.indexOf("\"hyou\"") >= 0 || data.indexOf("\"halert") >= 0 || data.indexOf("\"f") >= 0) {   // 0.3.29: Home / Teleport
      String fa = @PKG@.HubBar.jsonStr(data, "a");
      if (fa.equals("hyou")) { youClick(ref, st); return; }
      if (fa.startsWith("halert")) { alertClick(ref, st, fa.substring(6)); return; }
      if (fa.startsWith("f") && fbIndex(fa.substring(1)) >= 0) { footClick(ref, st, fa.substring(1)); return; }
    }
    if (data.indexOf("mclose\"") >= 0) { closePage(ref, st); return; }
    if (data.indexOf("mback\"") >= 0) { this.status = ""; goBack(); rebuild(); return; }
    if (data.indexOf("mprev\"") >= 0) { this.status = ""; if (this.pageNo > 0) this.pageNo = this.pageNo - 1; rebuild(); return; }
    if (data.indexOf("mnext\"") >= 0) { this.status = ""; this.pageNo = this.pageNo + 1; rebuild(); return; }
    if (data.indexOf("mslot\"") < 0) return;
    int idx = @PKG@.MenuUtil.jsonInt(data, "SlotIndex");
    if (idx < 0 || idx >= 54 || idx >= this.gridN || this.acts == null) { @PKG@.MenuUtil.info("unexpected slot payload: " + data); return; }
    String act = this.acts[idx];
    if (act == null) return;
    click(ref, st, idx, act);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu click failed: " + t); }
}""")

# ================= 0.3.6 MenuPage.watchTick: the menu's check, on the player's world thread (MenuWatch hands it here). true = again.
#  - the menu is no longer the open page (closed / replaced) -> done;
#  - the player changed world since it opened -> the client dropped it: forget it on the server (PageGuard.forget, no packet) -> done;
#  - SETTLE after the menu's last packet: a test click through the engine's own gate (PageManager.handleEvent Data -> this menu's
#    handleDataEvent only while customPageRequiredAcknowledgments == 0). It arrives -> healthy, nothing is sent. It does not -> the game
#    is dropping this menu's clicks: log, PageManager.clearCustomPageAcknowledgements() (what a world change runs) and, for the first
#    HEAL_ANSWERS heals of this menu, an answer (the menu redrawn with a status line) so a waiting client stops waiting; later heals
#    reset silently (never a periodic page update).
# 0.3.19 E: the next check's delay: 1 s, after 3 healthy checks in a row 2 s (any packet the menu sends starts over; FIX ROUND: 2 s at
# most, so a click the game drops is healed within 2 s)
M(page, r"""
public long watchDelay() {
  int h = this.healthy;
  if (h < 3) return @PKG@.MenuWatch.PERIOD;
  return 2L * @PKG@.MenuWatch.PERIOD;
}""")
M(page, r"""
public boolean watchTick(@WLD@ now) {
  @REF@ ref = this.playerRef.getReference();
  if (ref == null || !ref.isValid()) return this.playerRef.isValid();
  @ST@ st = ref.getStore();
  if (st == null) return true;
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return true;
  @PGM@ pm = p.getPageManager();
  if (pm == null) return true;
  if (pm.getCustomPage() != this) return false;
  if (changedWorld(now)) {
    if (@PKG@.PageGuard.forget(pm, ref, st, this)) @PKG@.MenuUtil.info("the SkyWynn Menu of " + @PKG@.PageGuard.who(this.playerRef) + " was still open on the server after a world change - forgot it there too (no packet)");
    return false;
  }
  long t = System.currentTimeMillis();
  long ls = this.lastSend;
  if (ls != this.seenSend) { this.seenSend = ls; this.healthy = 0; }
  if (t - ls < SETTLE) return true;
  this.probeNonce = Long.toHexString(System.nanoTime() ^ (((long) System.identityHashCode(this)) << 24));
  this.probeSeen = false;
  pm.handleLegacyCustomPageEvent(ref, st, new @CPE@(@CPT@.Data, "{\"a\":\"skyymenucheck\",\"n\":\"" + this.probeNonce + "\"}"));
  if (this.probeSeen) { this.healthy = this.healthy + 1; return true; }
  if (pm.getCustomPage() != this) return false;
  this.healthy = 0;
  this.heals = this.heals + 1;
  boolean answer = this.heals <= HEAL_ANSWERS;
  if (this.heals <= 3 || this.heals % 60 == 0) @PKG@.MenuUtil.warn("the game was dropping " + @PKG@.PageGuard.who(this.playerRef) + "'s menu clicks (it still waited for a page acknowledgement the client will never send - e.g. a page update or close sent to a page the client no longer shows); reset the page acknowledgements" + (answer ? " and answered the menu" : "") + " (" + this.heals + ")");
  pm.clearLegacyCustomPageAcknowledgements();
  if (answer) {
    this.status = "Clicks were stuck (a game hiccup after a teleport) - fixed. Click again.";
    rebuild();
  }
  return true;
}""")
# ================= 0.3.6 MenuWatch part 2: the scheduler-thread tick -> the player's world thread
M(mwat, r"""
public void hop() {
  if (@PKG@.PageGuard.STOP) return;
  @PR@ pr = this.page.who();
  if (pr == null || !pr.isValid()) return;
  java.util.UUID wu = pr.getWorldUuid();
  @UNI@ uni = @UNI@.get();
  @WLD@ w = null;
  if (wu != null && uni != null) w = uni.getWorld(wu);
  if (w == null) { schedule(this.page); return; }
  w.execute(new @PKG@.MenuWatch(this.page, w));
}""")
M(mwat, r"""
public void run() {
  if (this.target == null) {
    try { hop(); }
    catch (Throwable t) { if (this.page.watchFail(t)) schedule(this.page); }
    return;
  }
  boolean again = false;
  try { again = this.page.watchTick(this.target); }
  catch (Throwable t) { again = this.page.watchFail(t); }
  if (again && !@PKG@.PageGuard.STOP) scheduleIn(this.page, this.page.watchDelay());
}""")

# 0.3.35: Your Stats = ONE scroll list - each section (Main, Combat, Gathering) = a head row {null, name, note} + its stat rows
M(scl, r"""
public static java.util.ArrayList allRows(java.util.UUID u, Object[] vit) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int t = 0; t < 3 && t < TABS.length; t++) {
    java.util.ArrayList rs = rows(u, t, vit);
    out.add(new String[] { null, TABS[t], t < NOTES.length ? NOTES[t] : "" });
    for (int i = 0; i < rs.size(); i++) out.add(rs.get(i));
  }
  return out;
}""")

# ================= 0.3.10 StatsPage: the Stats page (one inline page, tabs switched with rebuild(); no timers, no MouseEntered/Exited) =================
# build() reads everything again (the vitals on this world thread), so Refresh / a tab click shows the current numbers. Click payloads
# are matched with both quotes. Change Profile = the player's own /profiles through the engine command manager (installed + permission
# checked first, like the menu tiles); the page never closes itself before another page opens.
# fix round: /profiles counts only when it is SkyyProfiles' own command (PROFILES_CMD) - another pack mod (EndlessLeveling's /profile has
# the alias "profiles") may win the name; then the button is hidden, exactly as without SkyyProfiles.
F(stp, 'public static final String PROFILES_CMD = "com.skyy.profiles.ProfilesCmd";')
M(stp, r"""
public static @ACM@ profilesCmd() {
  @ACM@ c = @PKG@.MenuUtil.cmd("profiles");
  if (c == null) return null;
  return PROFILES_CMD.equals(c.getClass().getName()) ? c : null;
}""")
M(stp, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  Object[] vit = @PKG@.StatsCalc.vitals(st, ref);
  java.util.ArrayList rows = @PKG@.StatsCalc.allRows(u, vit);      // 0.3.35: one scroll list (Main, Combat, Gathering)
  boolean prof = profilesCmd() != null;
""" + "\n".join("  " + ln for ln in ST_SHELL_JAVA.split("\n")) + r"""
  @PKG@.MenuHub.ensure(u);
  """ + ST_HUB_JAVA + r"""
""" + "\n".join("  " + ln for ln in ST_SUB_JAVA.split("\n")) + r"""
  for (int i = 0; i < rows.size(); i++) {
    String[] r = (String[]) rows.get(i);
    if (r[0] == null) {
""" + "\n".join("      " + ln for ln in ST_HEAD_JAVA.split("\n")) + r"""
      b.set("#SkyyStatN" + i + ".Text", r[1]);
      b.set("#SkyyStatS" + i + ".Text", r[2]);
      continue;
    }
""" + "\n".join("    " + ln for ln in ST_ROW_JAVA.split("\n")) + r"""
    b.set("#SkyyStatN" + i + ".Text", r[0]);
    b.set("#SkyyStatV" + i + ".Text", r[1]);
    b.set("#SkyyStatS" + i + ".Text", r[2]);
  }
  """ + ST_FOOT_JAVA["msg"] + r"""
  """ + ST_FOOT_JAVA["gap"] + r"""
  """ + ST_FOOT_JAVA["refresh"] + r"""
  """ + ST_FOOT_JAVA["gap"] + r"""
  if (prof) {
    """ + ST_FOOT_JAVA["profile"] + r"""
    ev.addEventBinding(@BT@.Activating, "#SkyyStatProfile", @EVD@.of("a", "tprofile"));
  } else {
    """ + ST_FOOT_JAVA["noprofile"] + r"""
  }
  """ + ST_FOOT_JAVA["gap"] + r"""
  """ + ST_FOOT_JAVA["close"] + r"""
  ev.addEventBinding(@BT@.Activating, "#SkyyStatRefresh", @EVD@.of("a", "trefresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyStatClose", @EVD@.of("a", "tclose"));
  b.set("#SkyyStatHead.Text", @PKG@.StatsCalc.header(u, this.playerRef.getUsername()));
  b.set("#SkyyStatSub.Text", @PKG@.StatsCalc.SUB);
  b.set("#SkyyStatMsg.Text", this.status == null ? "" : this.status);
}""")
# StatsTask's answer (before StatsTask, which calls it): the page is still open 0.9 s after Change Profile -> /profiles answered in chat
M(stp, r"""
public void answer() {
  this.status = "Your profile list did not open - read your chat.";
  rebuild();
}""")
M(stp, r"""
public @PR@ who() { return this.playerRef; }""")

# ================= StatsTask: one redraw 0.9 s after Change Profile, ONLY while the Stats page is still the player's open page in the
# same world (RefreshTask pattern: scheduler -> World.execute -> check on the world thread; the scheduler = PageGuard.EXEC, which setup()
# sets to HytaleServer.SCHEDULED_EXECUTOR - no scheduler = no answer, the page simply stays as it is). A page the client no longer shows is never
# redrawn (a redraw it never acknowledges would make every page ignore clicks - the 0.3.6 rule).
sta.addInterface(pool.get("java.lang.Runnable"))
F(sta, "public @PKG@.StatsPage page;")
F(sta, "public @PR@ pr;")
F(sta, "public @WLD@ expected;")
C(sta, r"""
public StatsTask(@PKG@.StatsPage page, @PR@ pr) { this.page = page; this.pr = pr; this.expected = null; }""")
M(sta, r"""
public static boolean schedule(@PKG@.StatsPage page, @PR@ pr, long ms) {
  java.util.concurrent.ScheduledExecutorService ex = @PKG@.PageGuard.EXEC;
  if (ex == null) return false;
  try { ex.schedule(new @PKG@.StatsTask(page, pr), ms, java.util.concurrent.TimeUnit.MILLISECONDS); return true; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule the stats page check: " + t); return false; }
}""")
M(sta, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    if (this.expected == null) {
      java.util.UUID wu = this.pr.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) return;
      this.expected = w;
      w.execute(this);
      return;
    }
    java.util.UUID wu2 = this.pr.getWorldUuid();
    if (wu2 == null || @UNI@.get().getWorld(wu2) != this.expected) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    @PGM@ pm = p.getPageManager();
    if (pm == null || pm.getCustomPage() != this.page) return;
    this.page.answer();
  } catch (Throwable t) { @PKG@.MenuUtil.warn("stats page check failed: " + t); }
}""")
M(stp, r"""
public void changeProfile(@REF@ ref, @ST@ st) {
  @ACM@ c = profilesCmd();
  if (c == null) { this.status = "Profiles are not on this server."; rebuild(); return; }
  boolean ok = false;
  try { ok = c.hasPermission(this.playerRef); } catch (Throwable t) { @PKG@.MenuUtil.warn("permission check for /profiles failed: " + t); ok = false; }
  if (!ok) { this.status = "You do not have permission for /profiles. Ask an admin."; rebuild(); return; }
  try { @CMGR@.get().handleCommand(this.playerRef, "profiles"); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("/profiles from the stats page failed: " + t); this.status = "/profiles could not be run."; rebuild(); return; }
  @PKG@.StatsTask.schedule(this, this.playerRef, 900L);
}""")
M(stp, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String hr = @PKG@.MenuHub.click(this.playerRef, data, "character", "stats");   // 0.3.28: the hub bar
    if (hr != null) {
      if (hr.equals("close")) {
        @PLA@ hc = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
        if (hc != null) hc.getPageManager().setPage(ref, st, @PGE@.None);
        return;
      }
      if (hr.equals("menu")) {
        @PLA@ hm = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
        if (hm != null) hm.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));
        return;
      }
      if (@PKG@.MenuHub.opened(hr)) return;
      this.status = hr.equals("self") ? "" : @PKG@.MenuData.HUB_TXT_FAIL;
      rebuild();
      return;
    }
    if (data.indexOf("\"tclose\"") >= 0) {
      @PLA@ pc = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      if (pc != null) pc.getPageManager().setPage(ref, st, @PGE@.None);
      return;
    }
    if (data.indexOf("\"tmenu\"") >= 0) {
      @PLA@ pm = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      if (pm != null) pm.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));
      return;
    }
    if (data.indexOf("\"tprofile\"") >= 0) { this.status = ""; changeProfile(ref, st); return; }
    for (int i = 0; i < @PKG@.StatsCalc.TABS.length; i++) {
      if (data.indexOf("\"ttab" + i + "\"") >= 0) { this.tab = i; this.status = ""; rebuild(); return; }
    }
    if (data.indexOf("\"trefresh\"") >= 0) { this.status = "Refreshed - these are your stats right now."; rebuild(); return; }
    rebuild();
  } catch (Throwable t) { @PKG@.MenuUtil.warn("stats page click failed: " + t); }
}""")

# ================= /stats (alias /profilestats): opens the Stats page; no arguments; everyone (hytale:Adventurer) =================
C(stc, r"""
public StatsCmd() {
  super("stats", "Open your Stats page - every stat of your character");
  addAliases(new String[] { "profilestats" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(stc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ player = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new @PKG@.StatsPage(pr, 0));
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("/stats failed: " + t);
    pr.sendMessage(@MSG@.raw("[Stats] Could not open your stats page."));
  }
}""")

# ================= 0.2 SettingsPage (research/Settings-Spec.md 4.2-4.4): one inline page, tabs / rows switched with rebuild() =================
# Rows = the REGISTERED keys of the tab (SetReg.keysOf), sorted by SET_ORDER. Labels / help lines of other mods only go through b.set.
# 0.3.3: only the rows this player may change (SetReg.visible - a registration's permission node); the others are hidden, never greyed.
# Paging and the header count visible rows; a tab with no visible row is not drawn (the tab buttons close up, same ids and styles).
# Click payloads are matched with both quotes ("son1" can never match "son11" or "soff1"). No MouseEntered/Exited bindings, no timers:
# the armed Reset reverts on the next click; a change made elsewhere shows at the next click. The settings:def:* drain (a scan of the
# whole shared bridge map) runs once per opened page, on its first build - clicks only rebuild from SetReg.DEFS.
# 0.3.25: the search (Skyy 2026-10-14 "a search bar, to easily find settings"): every word of the query must appear in the setting's key,
# label, help text or its tab's SHORT name (case ignored). Fix round 2: the short name (SET_TAB "Coins"), not the long header (SET_HEAD
# "General (party, guild, teleports, menu)"), so a header word like "party" no longer lists every row of that tab. Only rows the player may change (the visible ones) are searched.
M(spg, r"""
public static boolean words(String hay, String q) {
  if (hay == null || q == null) return false;
  String h = hay.toLowerCase();
  String[] ws = q.trim().toLowerCase().split("\\s+");
  int n = 0;
  for (int i = 0; i < ws.length; i++) {
    if (ws[i].length() == 0) continue;
    if (h.indexOf(ws[i]) < 0) return false;
    n++;
  }
  return n > 0;
}""")
M(spg, r"""
public String[] found(Object[] vis, String q) {
  java.util.ArrayList ks = new java.util.ArrayList();
  java.util.ArrayList ts = new java.util.ArrayList();
  for (int i = 0; i < vis.length; i++) {
    String[] vk = (String[]) vis[i];
    String head = i < @PKG@.MenuData.SET_TAB.length ? @PKG@.MenuData.SET_TAB[i] : "";
    for (int k = 0; k < vk.length; k++) {
      Object[] d = @PKG@.SetReg.info(vk[k]);
      String hay = vk[k] + " " + head + (d == null ? "" : " " + String.valueOf(d[2]) + " " + String.valueOf(d[5]));
      if (!words(hay, q)) continue;
      ks.add(vk[k]);
      ts.add(Integer.valueOf(i));
    }
  }
  int[] t = new int[ts.size()];
  for (int j = 0; j < t.length; j++) t[j] = ((Integer) ts.get(j)).intValue();
  this.findTabs = t;
  return (String[]) ks.toArray(new String[0]);
}""")
# every click carries the search box (drafts survive any click); "@" built from a char (the build script's token check)
M(spg, r"""
public @EVD@ sevd(String a) {
  return @EVD@.of("a", a).append(String.valueOf((char) 64) + "Find", "#SkyyStgFind.Value");
}""")
M(spg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  if (!this.drained) { this.drained = true; @PKG@.SetReg.drainIdx(); }
  java.util.UUID u = this.playerRef.getUuid();
  int nCat = @PKG@.MenuData.SET_CAT_ID.length;
  Object[] vis = new Object[nCat];
  int first = -1;
  for (int i = 0; i < nCat; i++) {
    String[] vk = @PKG@.SetReg.visible(i, u);
    vis[i] = vk;
    if (first < 0 && vk.length > 0) first = i;
  }
  if (this.cat < 0 || this.cat >= nCat || (first >= 0 && ((String[]) vis[this.cat]).length == 0)) {
    this.cat = first >= 0 ? first : 0;
    this.pageNo = 0;
  }
  String q = this.search == null ? "" : this.search.trim();
  boolean find = q.length() >= 2;
  String[] keys = find ? found(vis, q) : (String[]) vis[this.cat];
  this.pageNo = 0;                                 // 0.3.35: one scroll list - no pages
  this.rowKeys = new String[keys.length];
  String stt = this.status == null ? "" : this.status;
  if (stt.length() == 0 && @PKG@.SetStore.isBroken(u)) stt = @PKG@.MenuData.SET_TXT_BROKEN;
  @PKG@.MenuHub.ensure(u);
""" + "\n".join("  " + ln for ln in STG_HUB_JAVA.split("\n")) + r"""
  int shown = 0;                                   // 0.3.35: the ONE sub-tab row = the categories with rows for this player
  for (int i = 0; i < nCat; i++) {
    if (((String[]) vis[i]).length == 0) continue;
    @PKG@.HubBar.subTab(b, ev, "SkyyStgH", shown, @PKG@.MenuData.SET_TAB[i], i == this.cat && !find, "stab" + i, @PKG@.MenuData.STG_TAB_W);
    shown++;
  }
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SFINDROW);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SFIND);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SSP10F);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SFINDGO);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SSP10F);
  b.appendInline("#SkyyStgFindRow", @PKG@.MenuData.UI_SFINDCLR);
  String fd = this.findDraft == null ? "" : this.findDraft;
  if (fd.length() > 0) b.set("#SkyyStgFind.Value", fd);
  ev.addEventBinding(@BT@.Activating, "#SkyyStgFindGo", sevd("sfind"));
  ev.addEventBinding(@BT@.Activating, "#SkyyStgFindClr", sevd("sfclr"));
  ev.addEventBinding(@BT@.Validating, "#SkyyStgFind", sevd("sfind"), false);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SGAP8);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SHEAD);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SROWS);
  int sz = @PKG@.HubBar.growSize(keys.length, @PKG@.MenuData.STG_LIST_H - 8, @PKG@.MenuData.STG_ROW_H, 3);   // Skyy rule 7: a short list fills its room
  for (int r = 0; r < keys.length; r++) {
    String key = keys[r];
    this.rowKeys[r] = key;
    Object[] d = @PKG@.SetReg.info(key);
    Boolean v = @PKG@.SetStore.get(u, key);
    boolean on = v == null || v.booleanValue();
    String row = "#SkyyStgRow" + r;
    String txt = "#SkyyStgTxt" + r;
    b.appendInline("#SkyyStgRows", "Group #SkyyStgRow" + r + @PKG@.MenuData.UI_SROWB[sz]);
    b.appendInline(row, @PKG@.MenuData.UI_SSP14);
    b.appendInline(row, "Group #SkyyStgTxt" + r + @PKG@.MenuData.UI_STXTB);
    b.appendInline(txt, "Label #SkyyStgName" + r + @PKG@.MenuData.UI_SNAMEB);
    b.appendInline(txt, "Label #SkyyStgDesc" + r + @PKG@.MenuData.UI_SDESCB);
    b.appendInline(row, "TextButton #SkyyStgOn" + r + (on ? @PKG@.MenuData.UI_SONSELB : @PKG@.MenuData.UI_SONB));
    b.appendInline(row, @PKG@.MenuData.UI_SSP10);
    b.appendInline(row, "TextButton #SkyyStgOff" + r + (on ? @PKG@.MenuData.UI_SOFFB : @PKG@.MenuData.UI_SOFFSELB));
    b.set("#SkyyStgName" + r + ".Text", d == null ? key : String.valueOf(d[2]));
    String desc = d == null ? "" : String.valueOf(d[5]);
    if (find && r < this.findTabs.length) {
      String own = d == null || d[0] == null ? "SkyyMenu" : String.valueOf(d[0]);
      desc = @PKG@.MenuData.SET_TAB[this.findTabs[r]] + ("SkyyMenu".equals(own) ? "" : " (" + own + ")") + ": " + desc;
    }
    b.set("#SkyyStgDesc" + r + ".Text", @PKG@.MenuUtil.clip(desc, 150));
    ev.addEventBinding(@BT@.Activating, "#SkyyStgOn" + r, sevd("son" + r));
    ev.addEventBinding(@BT@.Activating, "#SkyyStgOff" + r, sevd("soff" + r));
  }
  if (keys.length == 0) {
    b.appendInline("#SkyyStgRows", @PKG@.MenuData.UI_SEMPTY);
    b.set("#SkyyStgEmpty.Text", find ? @PKG@.MenuData.SET_TXT_NOFIND : @PKG@.MenuData.SET_TXT_EMPTY);
  }
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SALWAYS);
  boolean armed = this.armedAt > 0L && System.currentTimeMillis() - this.armedAt <= 10000L;
  b.appendInline("#SkyyStgHFoot", stt.length() > 0 ? @PKG@.MenuData.UI_SHINTST : @PKG@.MenuData.UI_SHINT);   // the status shows here
  b.appendInline("#SkyyStgHFoot", @PKG@.MenuData.UI_SFSP);
  b.appendInline("#SkyyStgHFoot", armed ? @PKG@.MenuData.UI_SRESETARM : @PKG@.MenuData.UI_SRESET);
  b.appendInline("#SkyyStgHFoot", @PKG@.MenuData.UI_SFSP);
  b.appendInline("#SkyyStgHFoot", @PKG@.MenuData.UI_SCLOSE);
  ev.addEventBinding(@BT@.Activating, "#SkyyStgReset", sevd("sreset"));
  ev.addEventBinding(@BT@.Activating, "#SkyyStgClose", sevd("sclose"));
  int n = keys.length;
  b.set("#SkyyStgHint.Text", stt.length() > 0 ? stt : @PKG@.MenuData.SET_TXT_HINT);
  String head = find ? "Search \"" + @PKG@.MenuUtil.clip(q, 30) + "\"" : @PKG@.MenuData.SET_HEAD[this.cat];
  b.set("#SkyyStgHead.Text", head + "   -   " + n + (n == 1 ? " setting" : " settings"));
  b.set("#SkyyStgAlways.Text", find ? @PKG@.MenuData.SET_TXT_FIND : @PKG@.MenuData.SET_ALWAYS[this.cat]);
  """ + STG_HUB_BUILD + r"""
}""")
M(spg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String hr = @PKG@.MenuHub.click(this.playerRef, data, "settings", "settings");   // 0.3.28: the hub bar
    if (hr != null) {
      boolean hadArm = this.armedAt > 0L;
      this.armedAt = 0L;                     // a hub click disarms Reset all, like every other click on this page
      if (hr.equals("close")) {
        @PLA@ hc = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
        if (hc != null) hc.getPageManager().setPage(ref, st, @PGE@.None);
        return;
      }
      if (hr.equals("menu")) {
        @PLA@ hm = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
        if (hm != null) hm.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));
        return;
      }
      if (@PKG@.MenuHub.opened(hr)) return;
      // the page's own tab with nothing to clear: no redraw, so a search the player is typing stays in its box (the bar sends no fields)
      if (hr.equals("self") && !hadArm && (this.status == null || this.status.length() == 0)) return;
      this.status = hr.equals("self") ? "" : @PKG@.MenuData.HUB_TXT_FAIL;
      rebuild();
      return;
    }
    String fk = String.valueOf((char) 64) + "Find";
    if (data.indexOf("\"" + fk + "\"") >= 0) {
      this.findDraft = @PKG@.MenuUtil.jstr(data, fk, 40);
      data = "{\"a\":\"" + @PKG@.MenuUtil.jstr(data, "a", 24) + "\"}";
    }
    java.util.UUID u = this.playerRef.getUuid();
    if (data.indexOf("\"sclose\"") >= 0) {
      @PLA@ pc = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      if (pc != null) pc.getPageManager().setPage(ref, st, @PGE@.None);
      return;
    }
    if (data.indexOf("\"smenu\"") >= 0) {
      @PLA@ pm = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      if (pm != null) pm.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));
      return;
    }
    long now = System.currentTimeMillis();
    boolean wasArmed = this.armedAt > 0L && now - this.armedAt <= 10000L;
    this.armedAt = 0L;
    if (data.indexOf("\"sreset\"") >= 0) {
      if (!wasArmed) {
        this.armedAt = now;
        this.status = @PKG@.MenuData.SET_TXT_ARM;
      } else {
        this.status = @PKG@.SetStore.resetAll(u) == 1 ? @PKG@.MenuData.SET_TXT_RESET : @PKG@.MenuData.SET_TXT_BROKEN;
      }
      rebuild();
      return;
    }
    if (data.indexOf("\"sfind\"") >= 0) {
      String q = this.findDraft == null ? "" : this.findDraft.trim();
      if (q.length() == 1) { this.status = @PKG@.MenuData.SET_TXT_SHORT; rebuild(); return; }
      this.search = q;
      this.pageNo = 0;
      this.status = "";
      rebuild();
      return;
    }
    if (data.indexOf("\"sfclr\"") >= 0) { this.search = ""; this.findDraft = ""; this.pageNo = 0; this.status = ""; rebuild(); return; }
    for (int i = 0; i < @PKG@.MenuData.SET_CAT_ID.length; i++) {
      if (data.indexOf("\"stab" + i + "\"") >= 0) { this.cat = i; this.pageNo = 0; this.status = ""; this.search = ""; this.findDraft = ""; rebuild(); return; }
    }
    if (data.indexOf("\"sprev\"") >= 0) { if (this.pageNo > 0) this.pageNo = this.pageNo - 1; this.status = ""; rebuild(); return; }
    if (data.indexOf("\"snext\"") >= 0) { this.pageNo = this.pageNo + 1; this.status = ""; rebuild(); return; }
    for (int r = 0; r < this.rowKeys.length; r++) {
      boolean hitOn = data.indexOf("\"son" + r + "\"") >= 0;
      boolean hitOff = !hitOn && data.indexOf("\"soff" + r + "\"") >= 0;
      if (!hitOn && !hitOff) continue;
      String key = this.rowKeys[r];
      if (key == null) { rebuild(); return; }
      if (!@PKG@.SetReg.may(u, key)) { this.status = @PKG@.MenuData.SET_TXT_GONE; rebuild(); return; }
      int ok = @PKG@.SetStore.set(u, key, hitOn, false);
      Object[] d = @PKG@.SetReg.info(key);
      String label = d == null ? key : String.valueOf(d[2]);
      this.status = ok == 1 ? label + (hitOn ? ": ON - saved." : ": OFF - saved.") : @PKG@.MenuData.SET_TXT_BROKEN;
      rebuild();
      return;
    }
    rebuild();
  } catch (Throwable t) { @PKG@.MenuUtil.warn("settings click failed: " + t); }
}""")

# ================= /settings (alias /skysettings): opens the page; no arguments; everyone (hytale:Adventurer) =================
C(scmd, r"""
public SettingsCmd() {
  super("settings", "Open your settings - turn chat messages on or off");
  addAliases(new String[] { "skysettings" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(scmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ player = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new @PKG@.SettingsPage(pr, -1));
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("/settings failed: " + t);
    pr.sendMessage(@MSG@.raw("[Settings] Could not open your settings."));
  }
}""")

# ================= 0.3 AdminPage (research/Server-Setup-Spec.md 2.3-2.10): Server Setup, one inline page, seven views =================
# Talks to a mod ONLY through the bridge (config:def:<Mod> + config:fn:<Mod>, java.lang types, tools/CONFIG-CONTRACT.md). The mod
# validates, saves, logs and versions; this page draws and passes clicks. No timers, no periodic updates, no MouseEntered/Exited.
# ---- seams: the ONLY methods that touch the engine / other pages (the bare-JVM harness swaps exactly these)
M(apg, r"""
public boolean guard() {
  boolean ok = false;
  try { ok = this.playerRef != null && this.playerRef.hasPermission(@MD@.ADMIN_NODE); } catch (Throwable t) { ok = false; }
  if (!ok) {
    this.pending = null;
    this.pendingCodes = null;
    this.drafts = new java.util.HashMap();
    this.tDrafts = new java.util.HashMap();
    this.status = @MD@.ADM_NOACCESS;
    this.statusKind = 3;
  }
  this.locked = !ok;
  return ok;
}""")
M(apg, r"""
public java.util.UUID me() {
  try { return this.playerRef.getUuid(); } catch (Throwable t) { return null; }
}""")
M(apg, r"""
public String myName() {
  try { String n = this.playerRef.getUsername(); return n == null ? "" : n; } catch (Throwable t) { return ""; }
}""")
M(apg, r"""
public boolean alive(String m) {
  return m != null && @MU@.liveVersion(m) != null;
}""")
M(apg, r"""
public boolean canEdit(String node) {
  if (node == null || node.length() == 0) return false;
  try { return this.playerRef.hasPermission(node); } catch (Throwable t) { return false; }
}""")
M(apg, r"""
public String heldItem(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return null;
    @INV@ inv = p.getInventory();
    if (inv == null) return null;
    @IS@ it = inv.getItemInHand();
    if (it == null || it.isEmpty()) return null;
    return it.getItemId();
  } catch (Throwable t) { return null; }
}""")
M(apg, r"""
public void setStatus(String s, int kind) {
  this.status = s == null ? "" : s;
  this.statusKind = kind;
}""")
# run a command line AS THIS ADMIN (the menu's handleCommand path; vanilla /su pattern) - link rows and the Reload buttons
M(apg, r"""
public boolean runLine(String line) {
  String name = @MU@.firstWord(line);
  try {
    if (name == null || @MU@.cmd(name) == null) { setStatus("/" + name + " is not on this server.", 3); return false; }
    @CMGR@.get().handleCommand(this.playerRef, line);
    return true;
  } catch (Throwable t) {
    @MU@.warn("Server Setup could not run /" + line + ": " + t);
    setStatus("/" + line + " could not be run.", 3);
    return false;
  }
}""")
M(apg, r"""
public void closeNow(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().setPage(ref, st, @PGE@.None);
  } catch (Throwable t) { @MU@.warn("could not close Server Setup: " + t); }
}""")
M(apg, r"""
public void openMenu(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));
  } catch (Throwable t) { @MU@.warn("could not open the SkyWynn Menu: " + t); }
}""")
# 0.3.28: after a hub bar click (MenuHub.click's answer): the X closes, "< Menu" opens the SkyWynn Menu, an opened tab owns the screen,
# the page's own tab draws nothing (the bar's click carries no field values: a redraw would drop typed text), a tab that could not open
# says so. Called from handleDataEvent AFTER guard() and from lockedClick.
M(apg, r"""
public void hubAfter(@REF@ ref, @ST@ st, String hr) {
  if (hr.equals("close")) { this.drafts = new java.util.HashMap(); closeNow(ref, st); return; }
  if (hr.equals("menu")) { openMenu(ref, st); return; }
  if (@PKG@.MenuHub.opened(hr)) return;
  if (hr.equals("self")) return;   // the page's own tab: nothing changes - no redraw, so typed values / an Import paste stay in their boxes
  setStatus(@MD@.HUB_TXT_FAIL, 3);
  rebuild();
}""")
# 0.3.23: the mod list's "Admin" button opens the Admin page (replaces this page; never close-then-open)
M(apg, r"""
public void openOps(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().openCustomPage(ref, st, new @PKG@.OpsPage(this.playerRef, 0));
  } catch (Throwable t) { @MU@.warn("could not open the Admin page: " + t); }
}""")
M(apg, r"""
public void saveFile(String name, String text) {
  @PKG@.AdmSaveTask.save(name, text);
}""")
# ---- header / row access (config:def:<Mod> = Object[10], rows = Object[11] of Strings; tools/CONFIG-CONTRACT.md)
M(apg, r"""
public static String hs(Object[] h, int i) {
  if (h == null || i < 0 || i >= h.length) return "";
  Object o = h[i];
  return o instanceof String ? (String) o : "";
}""")
# a <Mod> name read back off the shared bridge must be Skyy[A-Z][A-Za-z]{1,30} (the kit's MOD_RE, checked at the PUBLISHER's build only):
# this page shows it, runs it through commands and names export files after it, so a bogus config:def:<x> key (../, /, \, :) is ignored
M(apg, r"""
public static boolean validMod(String m) {
  if (m == null || m.length() < 6 || m.length() > 35 || !m.startsWith("Skyy")) return false;
  char c0 = m.charAt(4);
  if (c0 < 'A' || c0 > 'Z') return false;
  for (int i = 5; i < m.length(); i++) {
    char c = m.charAt(i);
    if (!((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z'))) return false;
  }
  return true;
}""")
M(apg, r"""
public static Object[] hdr(String m) {
  if (!validMod(m)) return null;
  try {
    Object o = @MU@.bridge().get("config:def:" + m);
    if (!(o instanceof Object[])) return null;
    Object[] h = (Object[]) o;
    if (h.length < 10 || !(h[5] instanceof String[]) || !(h[6] instanceof String[]) || !(h[7] instanceof Object[])) return null;
    return h;
  } catch (Throwable t) { return null; }
}""")
M(apg, r"""
public static boolean contractOk(Object[] h) {
  return h != null && @MD@.ADM_CONTRACT.equals(hs(h, 0));
}""")
M(apg, r"""
public static Object[] rowsOf(Object[] h) {
  if (h == null) return new Object[0];
  return (Object[]) h[7];
}""")
M(apg, r"""
public static Object[] rowAt(Object[] h, int i) {
  Object[] rs = rowsOf(h);
  if (i < 0 || i >= rs.length || !(rs[i] instanceof Object[])) return null;
  Object[] r = (Object[]) rs[i];
  if (r.length < 11) return null;
  return r;
}""")
M(apg, r"""
public static String rv(Object[] r, int i) {
  if (r == null || i < 0 || i >= r.length) return "";
  Object o = r[i];
  return o instanceof String ? (String) o : "";
}""")
M(apg, r"""
public static int rowIdx(Object[] h, String key) {
  if (key == null) return -1;
  Object[] rs = rowsOf(h);
  for (int i = 0; i < rs.length; i++) {
    Object[] r = rowAt(h, i);
    if (r != null && key.equals(rv(r, 0))) return i;
  }
  return -1;
}""")
M(apg, r"""
public static boolean hasFlag(Object[] r, String f) {
  return ("," + rv(r, 9) + ",").indexOf("," + f + ",") >= 0;
}""")
M(apg, r"""
public static String[] catIds(Object[] h) {
  if (h == null) return new String[0];
  return (String[]) h[5];
}""")
M(apg, r"""
public static String catLabel(Object[] h, int i) {
  if (h == null) return "";
  String[] l = (String[]) h[6];
  if (i < 0 || i >= l.length || l[i] == null) return "";
  return l[i];
}""")
M(apg, r"""
public static int catOf(Object[] h, Object[] r) {
  String[] ids = catIds(h);
  String c = rv(r, 2);
  for (int i = 0; i < ids.length; i++) if (ids[i] != null && ids[i].equals(c)) return i;
  return ids.length - 1;
}""")
M(apg, r"""
public static Object call(String m, Object[] args) {
  if (m == null) return null;
  try {
    Object f = @MU@.bridge().get("config:fn:" + m);
    if (!(f instanceof java.util.function.Function)) return null;
    return ((java.util.function.Function) f).apply(args);
  } catch (Throwable t) { @MU@.warn("config call to " + m + " failed: " + t); return null; }
}""")
M(apg, r"""
public static String cur(String m, String key) {
  Object o = call(m, new Object[] { "get", key });
  return o instanceof String ? (String) o : null;
}""")
# ---- 0.3.4: MILLISECOND ROWS IN SECONDS (Skyy, LOCKED 2026-10-01: "use seconds ... make sure you can use part numbers like 0.24").
# A row is milliseconds when its unit column (element 8) is "ms" on an int / dec row (tools/CONFIG-CONTRACT.md: the unit the file
# stores). The page shows and takes seconds; the mod always gets canonical milliseconds (its file, export codes and chat commands stay ms).
M(apg, r"""
public static boolean msRow(Object[] r) {
  if (r == null) return false;
  String t = rv(r, 3);
  return "ms".equals(rv(r, 8)) && (t.equals("int") || t.equals("dec"));
}""")
# milliseconds text -> seconds text, exact (BigDecimal, no float): 240 -> 0.24, 1500 -> 1.5, 30000 -> 30, 1 -> 0.001; not a number = as is
M(apg, r"""
public static String secText(String ms) {
  if (ms == null) return null;
  String t = ms.trim();
  if (t.length() == 0) return ms;
  try {
    java.math.BigDecimal d = new java.math.BigDecimal(t).movePointLeft(3);
    if (d.signum() == 0) return "0";
    return d.stripTrailingZeros().toPlainString();
  } catch (Throwable x) { return ms; }
}""")
# typed seconds -> canonical milliseconds text (whole = an int row: rounded half up, 0.2405 -> 241); "1.5s", "2 sec", "2 seconds" are
# seconds, "240ms" is milliseconds; null = not a time (empty, letters, a comma, two dots, other suffixes, exponents)
M(apg, r"""
public static String msOf(String typed, boolean whole) {
  if (typed == null) return null;
  String t0 = typed.trim().toLowerCase();
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < t0.length(); k++) { char c = t0.charAt(k); if (c != ' ' && c != '_') sb.append(c); }
  String t = sb.toString();
  if (t.length() == 0 || t.length() > 40) return null;
  int mul = 3;
  if (t.endsWith("ms")) { mul = 0; t = t.substring(0, t.length() - 2); }
  else if (t.endsWith("seconds")) t = t.substring(0, t.length() - 7);
  else if (t.endsWith("second")) t = t.substring(0, t.length() - 6);
  else if (t.endsWith("secs")) t = t.substring(0, t.length() - 4);
  else if (t.endsWith("sec")) t = t.substring(0, t.length() - 3);
  else if (t.endsWith("s")) t = t.substring(0, t.length() - 1);
  if (t.length() == 0) return null;
  int dots = 0;
  int digits = 0;
  for (int k = 0; k < t.length(); k++) {
    char c = t.charAt(k);
    if (c == '.') { dots++; continue; }
    if (c >= '0' && c <= '9') { digits++; continue; }
    if (k == 0 && (c == '-' || c == '+')) continue;
    return null;
  }
  if (dots > 1 || digits == 0) return null;
  try {
    java.math.BigDecimal d = new java.math.BigDecimal(t).movePointRight(mul);
    if (whole) d = d.setScale(0, java.math.RoundingMode.HALF_UP);
    if (d.signum() == 0) return "0";
    return d.stripTrailingZeros().toPlainString();
  } catch (Throwable x) { return null; }
}""")
# the row's bounds in seconds: "0.25 to 60 seconds" / "at least 0.25 seconds" / "at most 60 seconds" / ""
M(apg, r"""
public static String secRange(Object[] r) {
  String lo = rv(r, 5);
  String hi = rv(r, 6);
  if (lo.length() > 0 && hi.length() > 0) return secText(lo) + " to " + secText(hi) + " seconds";
  if (lo.length() > 0) return "at least " + secText(lo) + " seconds";
  if (hi.length() > 0) return "at most " + secText(hi) + " seconds";
  return "";
}""")
# the start of a millisecond row's help line: "0.25 to 60 seconds, default 2"
M(apg, r"""
public static String secHint(Object[] r) {
  String b = secRange(r);
  String d = rv(r, 4);
  if (b.length() == 0) b = "In seconds";
  return d.length() > 0 ? b + ", default " + secText(d) : b;
}""")
# null = within the row's bounds (or not checkable here: the mod checks again), else the refusal for the status line, in seconds
M(apg, r"""
public static String msRange(Object[] r, String msv) {
  try {
    java.math.BigDecimal v = new java.math.BigDecimal(msv);
    String lo = rv(r, 5);
    String hi = rv(r, 6);
    boolean low = lo.length() > 0 && v.compareTo(new java.math.BigDecimal(lo)) < 0;
    boolean high = hi.length() > 0 && v.compareTo(new java.math.BigDecimal(hi)) > 0;
    if (low || high) return rv(r, 1) + " must be " + secRange(r) + " - you typed " + secText(msv) + ".";
  } catch (Throwable x) { return null; }
  return null;
}""")
# what a typed value is SENT as: { value, null } (every row but a millisecond row: unchanged) or { null, the refusal }
M(apg, r"""
public static String[] typedValue(Object[] r, String v) {
  if (!msRow(r)) return new String[] { v, null };
  String m = msOf(v, !rv(r, 3).equals("dec"));
  if (m == null) return new String[] { null, rv(r, 1) + ": type the time in seconds, like 0.25 or 1.5 (a dot for decimals; 240ms works too)." };
  String bad = msRange(r, m);
  if (bad != null) return new String[] { null, bad };
  return new String[] { m, null };
}""")
# every message a mod's config kit sends back, in seconds: "240 ms" -> "0.24 s", "from 250 to 60000 ms" -> "from 0.25 to 60 s"
M(apg, r"""
public static String msWords(String s) {
  if (s == null || s.indexOf(" ms") < 0) return s;
  try {
    java.util.regex.Matcher m = java.util.regex.Pattern.compile("(?<![\\w.])from (-?\\d+(?:\\.\\d+)?) to (-?\\d+(?:\\.\\d+)?) ms\\b").matcher(s);
    StringBuffer sb = new StringBuffer();
    while (m.find()) m.appendReplacement(sb, java.util.regex.Matcher.quoteReplacement("from " + secText(m.group(1)) + " to " + secText(m.group(2)) + " s"));
    m.appendTail(sb);
    java.util.regex.Matcher m2 = java.util.regex.Pattern.compile("(?<![\\w.])(-?\\d+(?:\\.\\d+)?) ms\\b").matcher(sb.toString());
    StringBuffer sb2 = new StringBuffer();
    while (m2.find()) m2.appendReplacement(sb2, java.util.regex.Matcher.quoteReplacement(secText(m2.group(1)) + " s"));
    m2.appendTail(sb2);
    return sb2.toString();
  } catch (Throwable t) { return s; }
}""")
# a millisecond row's OWN help line (the mod wrote it in ms: "...once per this many ms.", SkyySkills feedbackMs / harvestCooldownMs /
# acro.feedbackMs, SkyyGear regen.periodMs) in seconds too - a "(s)" row must not say "ms" under it: a number + ms goes through msWords
# ("250 ms" -> "0.25 s"), a loose "ms" / "millisecond(s)" word becomes "seconds"; whole words only ("items", "msgs" stay)
M(apg, r"""
public static String secHelp(String h) {
  if (h == null) return "";
  String t = msWords(h);
  try { t = t.replaceAll("(?i)\\b(?:milliseconds?|millis|ms)\\b", "seconds"); } catch (Throwable x) { }
  return t;
}""")
M(apg, r"""
public static String rStatus(Object r) {
  if (!(r instanceof Object[])) return null;
  Object[] a = (Object[]) r;
  return a.length > 0 && a[0] instanceof String ? (String) a[0] : null;
}""")
M(apg, r"""
public static String rMsg(Object r) {
  if (!(r instanceof Object[])) return "";
  Object[] a = (Object[]) r;
  return a.length > 2 && a[2] instanceof String ? msWords((String) a[2]) : "";
}""")
M(apg, r"""
public static String rVal(Object r) {
  if (!(r instanceof Object[])) return null;
  Object[] a = (Object[]) r;
  return a.length > 1 && a[1] instanceof String ? (String) a[1] : null;
}""")
# a value as the admin reads it (the kit's own disp rule): bool ON/OFF, % glued on, other units after a space
M(apg, r"""
public static String disp(Object[] r, String v) {
  if (v == null) return "(unknown)";
  String t = rv(r, 3);
  if (t.equals("bool")) { if (v.equals("true")) return "ON"; if (v.equals("false")) return "OFF"; return v; }
  if (v.length() == 0) return "(empty)";
  if (msRow(r)) return secText(v) + " s";
  String u = rv(r, 8);
  if (u.length() == 0) return v;
  if (u.equals("%")) { if (t.equals("range")) return v.replace("-", "%-") + "%"; return v + "%"; }
  return v + " " + u;
}""")
M(apg, r"""
public static String tagOf(Object[] r) {
  StringBuilder sb = new StringBuilder();
  if (hasFlag(r, "ro")) sb.append("READ ONLY");
  else if (hasFlag(r, "restart")) sb.append("RESTART");
  else if (hasFlag(r, "new")) sb.append("NEW ONLY");
  else if (hasFlag(r, "live")) sb.append("LIVE");
  if (hasFlag(r, "danger")) { if (sb.length() > 0) sb.append(" - "); sb.append("CONFIRM"); }
  if (hasFlag(r, "part")) { if (sb.length() > 0) sb.append(" - "); sb.append("PART"); }
  if (hasFlag(r, "adv")) { if (sb.length() > 0) sb.append(" - "); sb.append("ADVANCED"); }
  return sb.toString();
}""")
M(apg, r"""
public static String[] chVals(String opts) {
  String[] p = opts.split(",");
  String[] out = new String[p.length];
  for (int k = 0; k < p.length; k++) { int b = p[k].indexOf('|'); out[k] = (b < 0 ? p[k] : p[k].substring(0, b)).trim(); }
  return out;
}""")
M(apg, r"""
public static String[] chLabels(String opts) {
  String[] p = opts.split(",");
  String[] out = new String[p.length];
  for (int k = 0; k < p.length; k++) { int b = p[k].indexOf('|'); out[k] = (b < 0 ? p[k] : p[k].substring(b + 1)).trim(); }
  return out;
}""")
M(apg, r"""
public static String[] tCols(String opts) {
  String[] p = opts.split(";");
  if (p.length < 3) return new String[] { "Value" };
  return p[2].split("\\|");
}""")
M(apg, r"""
public static String tMode(String opts) {
  String[] p = opts.split(";");
  if (p.length < 2) return "none";
  return p[1].trim();
}""")
M(apg, r"""
public static String stepOf(String opts) {
  if (opts == null || !opts.startsWith("step=")) return null;
  return opts.substring(5).trim();
}""")
M(apg, r"""
public static boolean hasOpt(String opts, String t) {
  return ("," + opts + ",").indexOf("," + t + ",") >= 0;
}""")
M(apg, r"""
public static java.util.ArrayList csv(String s) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (s == null) return out;
  String[] p = s.split(",");
  for (int k = 0; k < p.length; k++) { String x = p[k].trim(); if (x.length() > 0) out.add(x); }
  return out;
}""")
M(apg, r"""
public static String joinList(java.util.ArrayList l, String sep) {
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < l.size(); k++) { if (k > 0) sb.append(sep); sb.append(String.valueOf(l.get(k))); }
  return sb.toString();
}""")
M(apg, r"""
public static String firstLine(String s) {
  if (s == null) return "";
  int n = s.indexOf('\n');
  return n < 0 ? s : s.substring(0, n);
}""")
M(apg, r"""
public static String timeShort(String t) {
  if (t == null) return "";
  if (t.length() >= 16 && t.charAt(10) == 'T') return t.substring(5, 10) + " " + t.substring(11, 16);
  return t;
}""")
M(apg, r"""
public static java.util.ArrayList wrap(String msg, int w) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (msg == null) return out;
  String[] ls = msg.split("\n");
  for (int k = 0; k < ls.length; k++) {
    String s = ls[k].replace('\t', ' ').replace('\r', ' ');
    while (s.length() > w) {
      int cut = s.lastIndexOf(' ', w);
      if (cut < w / 2) cut = w;
      out.add(s.substring(0, cut).trim());
      s = s.substring(cut).trim();
    }
    out.add(s);
  }
  return out;
}""")
M(apg, r"""
public static boolean has(String hay, String needle) {
  return hay != null && needle != null && needle.length() > 0 && hay.toLowerCase().indexOf(needle.toLowerCase()) >= 0;
}""")
# "@" starts a TextField read-back key (EventData "@Key" -> "#Id.Value"); built from a char so the build script's token check stays simple
M(apg, r"""
public static String at(String k) {
  return String.valueOf((char) 64) + k;
}""")
M(apg, r"""
public static String stamp() {
  return java.time.LocalDateTime.now().format(java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmm"));
}""")
M(apg, r"""
public static int tailNum(String a, String prefix) {
  if (a == null || !a.startsWith(prefix) || a.length() == prefix.length()) return -1;
  String t = a.substring(prefix.length());
  for (int k = 0; k < t.length(); k++) if (t.charAt(k) < '0' || t.charAt(k) > '9') return -1;
  try { return Integer.parseInt(t); } catch (Throwable x) { return -1; }
}""")
M(apg, r"""
public static int modIndex(String m) {
  for (int k = 0; k < @MD@.MOD_NAME.length; k++) if (@MD@.MOD_NAME[k].equals(m)) return k;
  return -1;
}""")
M(apg, r"""
public static boolean installed(int k) {
  if (k < 0) return false;
  return @MU@.liveVersion(@MD@.MOD_NAME[k]) != null || @MU@.cmd(@MD@.MOD_CHECK[k]) != null;
}""")
# every mod that publishes a readable config:def:<Mod> (the pull model; 0.3.19 F: the names come from the small index MenuIdx - kept fresh
# on SkyyMenu-IO - instead of a scan of the whole bridge at every build; each name is still checked here, hdr(m) reads its value)
M(apg, r"""
public static String[] cfgMods() {
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    String[] ms = @PKG@.MenuIdx.configMods();
    for (int i = 0; i < ms.length; i++) {
      String m = ms[i];
      if (hdr(m) != null && !out.contains(m)) out.add(m);
    }
  } catch (Throwable t) { }
  java.util.Collections.sort(out);
  return (String[]) out.toArray(new String[0]);
}""")
M(apg, r"""
public static String resolveMod(String arg) {
  if (arg == null) return null;
  String a = arg.trim();
  if (a.length() == 0) return null;
  String[] cm = cfgMods();
  for (int i = 0; i < cm.length; i++) if (cm[i].equalsIgnoreCase(a) || cm[i].equalsIgnoreCase("Skyy" + a)) return cm[i];
  for (int i = 0; i < cm.length; i++) if (hs(hdr(cm[i]), 2).equalsIgnoreCase(a)) return cm[i];
  for (int k = 0; k < @MD@.MOD_NAME.length; k++) {
    String m = @MD@.MOD_NAME[k];
    if ((m.equalsIgnoreCase(a) || m.equalsIgnoreCase("Skyy" + a)) && installed(k)) return m;
  }
  return null;
}""")
# 0.3.25: a setting matches when EVERY word of the search is in its key, label or help text (case ignored)
M(apg, r"""
public static boolean words(String hay, String q) {
  if (hay == null || q == null) return false;
  String h = hay.toLowerCase();
  String[] ws = q.trim().toLowerCase().split("\\s+");
  int n = 0;
  for (int i = 0; i < ws.length; i++) {
    if (ws[i].length() == 0) continue;
    if (h.indexOf(ws[i]) < 0) return false;
    n++;
  }
  return n > 0;
}""")
M(apg, r"""
public static boolean rowHit(Object[] r, String q) {
  return r != null && words(rv(r, 0) + " " + rv(r, 1) + " " + rv(r, 10), q);
}""")
# 0.3.25: the search results of one mod: { mod, "hit", name, line 2, "", "0", target } - a tab ("c<i>") or a setting ("r<i>")
M(apg, r"""
public static java.util.ArrayList settingHits(String m, Object[] h, String q) {
  java.util.ArrayList out = new java.util.ArrayList();
  String title = hs(h, 2).length() > 0 ? hs(h, 2) : m;
  String[] ids = catIds(h);
  for (int c = 0; c < ids.length; c++) {
    if (words(catLabel(h, c), q)) out.add(new String[] { m, "hit", "Tab: " + catLabel(h, c), title + " (" + m + ") - every setting on its " + catLabel(h, c) + " tab", "", "0", "c" + c });
  }
  Object[] rs = rowsOf(h);
  for (int i = 0; i < rs.length; i++) {
    Object[] r = rowAt(h, i);
    if (r == null || !rowHit(r, q)) continue;
    String help = rv(r, 10);
    String name = rv(r, 1).length() > 0 ? rv(r, 1) : rv(r, 0);
    out.add(new String[] { m, "hit", name, title + " > " + catLabel(h, catOf(h, r)) + "  -  " + rv(r, 0) + (help.length() > 0 ? "  -  " + help : ""), "", "0", "r" + i });
  }
  return out;
}""")
M(apg, r"""
public static void addRow(java.util.ArrayList found, java.util.ArrayList keys, String sortKey, String[] e) {
  keys.add(sortKey + "\t" + String.valueOf(1000000 + found.size()).substring(1));
  found.add(e);
}""")
M(apg, r"""
public static java.util.ArrayList hitsOf(Object[] h, String q) {
  java.util.ArrayList out = new java.util.ArrayList();
  String[] ids = catIds(h);
  for (int i = 0; i < ids.length; i++) if (has(catLabel(h, i), q)) out.add("tab " + catLabel(h, i));
  Object[] rs = rowsOf(h);
  for (int i = 0; i < rs.length; i++) {
    Object[] r = rowAt(h, i);
    if (rowHit(r, q)) out.add(rv(r, 1));   // 0.3.25: + the key, every word
  }
  return out;
}""")
M(apg, r"""
public static int firstHit(Object[] h, String q) {
  Object[] rs = rowsOf(h);
  for (int i = 0; i < rs.length; i++) {
    Object[] r = rowAt(h, i);
    if (rowHit(r, q)) return i;   // 0.3.25: + the key, every word
  }
  return -1;
}""")
M(apg, r"""
public static java.util.ArrayList codesIn(String text) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (text == null || text.trim().length() == 0) return out;
  String[] toks = text.trim().split("\\s+");
  for (int i = 0; i < toks.length; i++) if (toks[i].startsWith("SKYY1.")) out.add(toks[i]);
  return out;
}""")
M(apg, r"""
public static String codeMod(String code) {
  String[] p = code.split("\\.");
  return p.length >= 2 ? p[1] : "";
}""")
# ---- inline pieces built at run time (the patterns are validated at build time with samples, and the harness checks the real output)
M(apg, r"""
public static String btn(String id, int w, int h, String text, String style) {
  String t = @MU@.inl(text);
  if (t.length() == 0) t = "-";
  return "TextButton #" + id + " { Anchor: (Width: " + w + ", Height: " + h + "); Text: \"" + t + "\"; " + style + " }";
}""")
M(apg, r"""
public static String spc(int w, int h) {
  return "Label { Anchor: (Width: " + w + ", Height: " + h + "); Text: \"\"; }";
}""")
M(apg, r"""
public static String lab(String id, int w, int h, int size, boolean bold, String color) {
  return "Label #" + id + " { Anchor: (Width: " + w + ", Height: " + h + "); Text: \"\"; Style: (FontSize: " + size + (bold ? ", RenderBold: true" : "") + ", TextColor: " + color + ", VerticalAlignment: Center); }";
}""")
M(apg, r"""
public static void field(@UCB@ b, String parent, String id, int w, int h, int max, String value, String ph) {
  b.appendInline(parent, "Group #" + id + "Box { Anchor: (Width: " + w + ", Height: " + h + "); Background: #16263a; }");
  String p = "";
  if (ph != null && ph.length() > 0) p = " PlaceholderText: \"" + @MU@.inl(ph) + "\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 17);";
  b.appendInline("#" + id + "Box", "TextField #" + id + " { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: " + max + ";" + p + " Style: (TextColor: #ffffff, FontSize: 19); }");
  if (value != null && value.length() > 0) b.set("#" + id + ".Value", value);
}""")
# ---- events: every button carries every TextField of the view (drafts survive any click, spec 2.5)
M(apg, r"""
public void evReset() {
  this.evKeys = new java.util.ArrayList();
  this.evSels = new java.util.ArrayList();
}""")
M(apg, r"""
public void evField(String key, String id) {
  this.evKeys.add(at(key));
  this.evSels.add("#" + id + ".Value");
}""")
M(apg, r"""
public @EVD@ evd(String a) {
  @EVD@ d = @EVD@.of("a", a);
  for (int k = 0; k < this.evKeys.size(); k++) d = d.append((String) this.evKeys.get(k), (String) this.evSels.get(k));
  return d;
}""")
M(apg, r"""
public void bind(@UEB@ ev, String id, String a) {
  ev.addEventBinding(@BT@.Activating, "#" + id, evd(a));
}""")
M(apg, r"""
public void bindEnter(@UEB@ ev, String id, String a) {
  ev.addEventBinding(@BT@.Validating, "#" + id, evd(a), false);
}""")
M(apg, r"""
public @EVD@ evdRow(String a, int r) {
  @EVD@ d = @EVD@.of("a", a);
  if (this.boxRows != null && this.boxRows.contains(Integer.valueOf(r))) d = d.append(at("V" + r), "#SkyyAdmVal" + r + ".Value");
  return d;
}""")
M(apg, r"""
public void bindR(@UEB@ ev, int r, String id, String a) {
  ev.addEventBinding(@BT@.Activating, "#" + id, evdRow(a, r));
}""")
M(apg, r"""
public void bindEnterR(@UEB@ ev, int r, String id, String a) {
  ev.addEventBinding(@BT@.Validating, "#" + id, evdRow(a, r), false);
}""")
M(apg, r"""
public static int catFit() {
  return (@MD@.ADM_ROWW - 150 - 5 - 150 - 16 + 5) / (@MD@.ADM_CATMIN + 5);
}""")
# ---- frame: accent, title, subtitle, the fixed body group; tail: status (4 colours) + a centred footer
# 0.3.35: the view crumbs = the ONE sub-tab row (Skyy rule 8: no back buttons - a sub view is a sub-tab): All mods | <the mod> | <this view>;
# the active one Primary and unbound, the others lead there (amods = the mod list, aback = the mod's page). In a confirm nothing is bound
# (any other click there = Cancel). {label, action or null, "1" = active}
M(apg, r"""
public java.util.ArrayList crumbs() {
  java.util.ArrayList c = new java.util.ArrayList();
  String v = this.view == null ? "list" : this.view;
  boolean conf = v.equals("confirm");
  boolean lst = v.equals("list") || this.locked;
  c.add(new String[] { "All mods", lst || conf ? null : "amods", lst ? "1" : "0", "150", "0" });
  if (lst) {
    if (!this.locked) c.add(new String[] { "Admin", "aops", "0", "150", "5" });   // 0.3.36: the Admin page (was a button in the search row)
    return c;
  }
  if (this.mod != null && !v.equals("log") && !(v.equals("io") && this.ioAll)) {
    boolean here = v.equals("mod");
    String nm = this.mod.startsWith("Skyy") && this.mod.length() > 4 ? this.mod.substring(4) : this.mod;
    c.add(new String[] { nm, here || conf ? null : "aback", here ? "1" : "0", "150", "5" });
    if (here) {
      Object[] h = hdr(this.mod);
      int nc = catIds(h).length;
      if (nc > 1 && nc <= catFit()) {                 // more than fit at ADM_CATMIN px: the in-page category picker (drawMod)
        int tw = (@MD@.ADM_ROWW - 150 - 5 - 150 - 16 - 5 * (nc - 1)) / nc;
        if (tw > 150) tw = 150;
        if (tw < @MD@.ADM_CATMIN) tw = @MD@.ADM_CATMIN;
        for (int i = 0; i < nc; i++) {
          boolean sel = i == this.cat;
          c.add(new String[] { catLabel(h, i), sel ? null : "atab" + i, sel ? "1" : "0", String.valueOf(tw), i == 0 ? "16" : "5", "cat" });
        }
      }
    }
  }
  String w = null;
  if (v.equals("table")) w = "Table";
  else if (v.equals("hist")) w = "History";
  else if (v.equals("io")) w = "Export";
  else if (v.equals("log")) w = "Changes";
  else if (conf) w = "Confirm";
  if (w != null) c.add(new String[] { w, null, "1", "150", "5" });
  return c;
}""")
M(apg, r"""
public static boolean crumbAct(String a) {
  return "amods".equals(a) || "aback".equals(a) || "amenu".equals(a);
}""")
# 0.3.36 (task 3, long crumb names): a text fitted to room px - whole when the label can shrink it to fit (12 px, the kit small button's
# MinShrinkTextToFitFontSize; ADM_CW = the client's glyph widths x 100 at 12 px, capitals), else cut with ... (b.set: the dots are not an
# inline character)
M(apg, r"""
public static int cw(char c) {
  char u = Character.toUpperCase(c);
  int k = u - 32;
  if (k < 0 || k >= @MD@.ADM_CW.length) return @MD@.ADM_CWMAX;
  return @MD@.ADM_CW[k];
}""")
M(apg, r"""
public static String fit(String s, int room) {
  if (s == null) return "";
  int lim = room * 100;
  int tot = 0;
  for (int i = 0; i < s.length(); i++) tot = tot + cw(s.charAt(i));
  if (tot <= lim) return s;
  int dots = 3 * cw('.');
  StringBuilder sb = new StringBuilder();
  int acc = 0;
  for (int i = 0; i < s.length(); i++) {
    int x = cw(s.charAt(i));
    if (acc + x + dots > lim) break;
    acc = acc + x;
    sb.append(s.charAt(i));
  }
  return sb.toString().trim() + "...";
}""")
M(apg, r"""
public static String crumbBtn(String id, int w, boolean sel) {
  return "TextButton #" + id + " { Anchor: (Width: " + w + ", Height: " + @MD@.ADM_SUBH + "); Padding: (Horizontal: " + @MD@.ADM_CRPAD + "); Text: \"\"; " + (sel ? @MD@.ADM_SUBSEL : @MD@.ADM_SUBN) + " }";
}""")
# the frame: the hub page, the crumbs (+ categories) in the sub-tab row (SkyyAdmCrumb<i>: 0.3.35's SkyyAdmCr<i> were the ids of a choice
# row's > button too), the title line beside them - or, when a mod's categories fill the row, the body's first line - and the body group
M(apg, r"""
public void frame(@UCB@ b, String title, String sub) {
""" + "\n".join("  " + ln for ln in ADM_HUB_JAVA.split("\n")) + r"""
  java.util.ArrayList cr = crumbs();
  int used = 0;
  boolean cats = false;
  for (int i = 0; i < cr.size(); i++) {
    String[] c = (String[]) cr.get(i);
    int w = Integer.parseInt(c[3]);
    int g = i > 0 ? Integer.parseInt(c[4]) : 0;
    if (g > 0) { b.appendInline("#SkyyAdmHSub", spc(g, @MD@.ADM_SUBH)); used = used + g; }
    b.appendInline("#SkyyAdmHSub", crumbBtn("SkyyAdmCrumb" + i, w, "1".equals(c[2])));
    b.set("#SkyyAdmCrumb" + i + ".Text", fit(c[0], w - 2 * @MD@.ADM_CRPAD - 2));
    used = used + w;
    if (c.length > 5) cats = true;
  }
  if (!cats) b.appendInline("#SkyyAdmHSub", "Label #SkyyAdmSub { Anchor: (Width: " + (@MD@.ADM_ROWW - used - 12) + ", Height: 32, Left: 12); Text: \"\"; Style: " + @MD@.ADM_SUBSTYLE + "; }");
  b.appendInline("#SkyyAdm", @MD@.UI_ABODY);
  if (cats) b.appendInline("#SkyyAdmBody", @MD@.UI_ASUB);
  String t = title == null ? "" : title;
  if (t.startsWith(@MD@.ADM_PREFIX)) t = t.substring(@MD@.ADM_PREFIX.length());   // the Server Setup tab already names the page
  String s = sub == null ? "" : sub;
  b.set("#SkyyAdmSub.Text", @MU@.clip(s.length() == 0 ? t : t + "   -   " + s, @MD@.ADM_SUBMAX));
}""")
M(apg, r"""
public void fReset() {
  this.fT = new java.util.ArrayList();
  this.fA = new java.util.ArrayList();
  this.fW = new java.util.ArrayList();
}""")
M(apg, r"""
public void foot(String text, String act, int w) {
  this.fT.add(text);
  this.fA.add(act);
  this.fW.add(Integer.valueOf(w));
}""")
M(apg, r"""
public void tail(@UCB@ b, @UEB@ ev) {
  int k = this.statusKind;
  if (k < 0 || k > 3) k = 0;
  java.util.ArrayList cr = crumbs();
  for (int i = 0; i < cr.size(); i++) {
    String[] c = (String[]) cr.get(i);
    if (c[1] != null) bind(ev, "SkyyAdmCrumb" + i, c[1]);      // with every text box of the view (bind = evd): no typed value is lost
  }
  int total = 0;
  int nb = 0;
  for (int i = 0; i < this.fW.size(); i++) {
    if (crumbAct((String) this.fA.get(i))) continue;
    total = total + ((Integer) this.fW.get(i)).intValue() + (nb > 0 ? 8 : 0);
    nb++;
  }
  int sw = @MD@.ADM_ROWW - total - 10;
  if (sw < 200) { @MU@.warn("server setup footer is " + total + " px wide"); sw = 200; }
  String sst = k == 1 ? @MD@.ADM_ST1 : (k == 2 ? @MD@.ADM_ST2 : (k == 3 ? @MD@.ADM_ST3 : @MD@.ADM_ST0));
  b.appendInline("#SkyyAdmHFoot", "Label #SkyyAdmStatus { Anchor: (Width: " + sw + ", Height: 48); Text: \"\"; Style: " + sst + "; }");
  b.set("#SkyyAdmStatus.Text", firstLine(this.status));
  b.appendInline("#SkyyAdmHFoot", spc(10, 48));
  int j = 0;
  for (int i = 0; i < this.fT.size(); i++) {
    if (crumbAct((String) this.fA.get(i))) continue;
    if (j > 0) b.appendInline("#SkyyAdmHFoot", spc(8, 48));
    String id = "SkyyAdmF" + i;
    b.appendInline("#SkyyAdmHFoot", btn(id, ((Integer) this.fW.get(i)).intValue(), 48, (String) this.fT.get(i), @MD@.ADM_BS));
    bind(ev, id, (String) this.fA.get(i));
    j++;
  }
  @PKG@.MenuHub.ensure(me());   // 0.3.28: every view ends here (tail) - the hub tab strip of Settings > Server Setup
  """ + ADM_HUB_BUILD + r"""
}""")
# 0.3.36: the in-page picker (the change log's mod filter, the history's file filter): <label>  <  <the picked name (k of n)>  >
M(apg, r"""
public void picker(@UCB@ b, @UEB@ ev, String label, String shown, String prevAct, String nextAct) {
  b.appendInline("#SkyyAdmBody", @MD@.UI_APICK);
  b.appendInline("#SkyyAdmPick", spc(14, 50));
  b.appendInline("#SkyyAdmPick", @MD@.UI_APICKL);
  b.set("#SkyyAdmPickL.Text", label);
  b.appendInline("#SkyyAdmPick", btn("SkyyAdmPickPrev", 60, 50, "<", @MD@.ADM_BS));
  b.appendInline("#SkyyAdmPick", spc(6, 50));
  b.appendInline("#SkyyAdmPick", @MD@.UI_APICKV);
  b.set("#SkyyAdmPickV.Text", shown);
  b.appendInline("#SkyyAdmPick", spc(6, 50));
  b.appendInline("#SkyyAdmPick", btn("SkyyAdmPickNext", 60, 50, ">", @MD@.ADM_BS));
  bind(ev, "SkyyAdmPickPrev", prevAct);
  bind(ev, "SkyyAdmPickNext", nextAct);
}""")
M(apg, r"""
public void preview(@UCB@ b, String head, String text) {
  b.appendInline("#SkyyAdmBody", @MD@.UI_APREV);
  b.appendInline("#SkyyAdmPrev", @MD@.UI_APREVHEAD);
  b.set("#SkyyAdmPrevHead.Text", head == null ? "" : head);
  java.util.ArrayList ls = wrap(text, 125);
  int max = @MD@.ADM_PLINES;
  for (int i = 0; i < ls.size() && i < max; i++) {
    b.appendInline("#SkyyAdmPrev", @MD@.UI_APL[i]);
    String t = (String) ls.get(i);
    if (i == max - 1 && ls.size() > max) t = "and " + (ls.size() - max + 1) + " more";
    b.set("#SkyyAdmPL" + i + ".Text", t);
  }
}""")
M(apg, r"""
public void drawLocked(@UCB@ b, @UEB@ ev) {
  evReset();
  fReset();
  frame(b, "Server Setup", "");
  foot("Close", "aclose", 170);
  tail(b, ev);
}""")

# ---- view list (spec 2.4): mods on the registry first (summary or the red state), then every other installed mod as file only
M(apg, r"""
public String[] summary(String m, Object[] h) {
  String state = "ok";
  String smsg = "";
  Object st = call(m, new Object[] { "status" });
  if (st instanceof String[] && ((String[]) st).length >= 2) { state = ((String[]) st)[0]; smsg = ((String[]) st)[1]; }
  if ("unreadable".equals(state)) return new String[] { "Its config file cannot be read - " + smsg, "1" };
  if ("unsaved".equals(state)) return new String[] { "Changes not saved yet - retrying. " + smsg, "1" };
  int n = 0;
  StringBuilder parts = new StringBuilder();
  StringBuilder eds = new StringBuilder();
  Object[] rs = rowsOf(h);
  for (int i = 0; i < rs.length; i++) {
    Object[] r = rowAt(h, i);
    if (r == null) continue;
    String t = rv(r, 3);
    if (t.equals("link")) { if (eds.length() > 0) eds.append(", "); eds.append(rv(r, 1)); continue; }
    if (t.equals("action")) continue;
    n++;
    if (hasFlag(r, "part")) {
      String v = cur(m, rv(r, 0));
      if (parts.length() > 0) parts.append(" - ");
      parts.append(rv(r, 1)).append("true".equals(v) ? " ON" : " OFF");
    }
  }
  StringBuilder sb = new StringBuilder();
  sb.append(n).append(n == 1 ? " setting" : " settings");
  if ("restart".equals(state)) sb.append(" - ").append(smsg);
  if (parts.length() > 0) sb.append(" - Parts: ").append(parts.toString());
  if (eds.length() > 0) sb.append(" - Editors: ").append(eds.toString());
  return new String[] { sb.toString(), "0" };
}""")
# { mod, kind, name, line 2, reload command, red } or null when a search leaves it out
M(apg, r"""
public String[] cfgRow(String m, Object[] h, String q) {
  String name = m + " " + hs(h, 3);
  if (!contractOk(h)) {
    if (q != null && !has(m, q)) return null;
    return new String[] { m, "cfg", name, "Needs a newer SkyyMenu (config contract " + hs(h, 0) + ") - update SkyyMenu to change it in game.", "", "1" };
  }
  if (!alive(m)) {
    if (q != null && !has(m, q)) return null;
    return new String[] { m, "cfg", name, "Not running - its settings cannot be changed now.", "", "1" };
  }
  if (q != null) {
    java.util.ArrayList hits = hitsOf(h, q);
    boolean nameHit = has(m, q) || has(hs(h, 2), q);
    if (hits.isEmpty() && !nameHit) return null;
    if (!hits.isEmpty()) {
      StringBuilder sb = new StringBuilder("Hits: ");
      for (int i = 0; i < hits.size() && i < 3; i++) { if (i > 0) sb.append(", "); sb.append((String) hits.get(i)); }
      if (hits.size() > 3) sb.append(", and ").append(hits.size() - 3).append(" more");
      return new String[] { m, "cfg", name, sb.toString(), "", "0" };
    }
  }
  String[] sm = summary(m, h);
  return new String[] { m, "cfg", name, sm[0], "", sm[1] };
}""")
M(apg, r"""
public String[] fileRow(int k) {
  String m = @MD@.MOD_NAME[k];
  String live = @MU@.liveVersion(m);
  String name = m + " " + (live != null ? live : @MD@.MOD_VER[k]);
  String rl = @MD@.MOD_RELOAD[k];
  if (rl.length() > 0 && @MU@.cmd(@MU@.firstWord(rl)) == null) rl = "";
  String line = @MD@.MOD_FLINE[k];
  String since = @MD@.MOD_SINCE[k];
  String red = "0";
  if (since.length() > 0) {
    if (live == null) line = "Not running here (disabled or missing) - " + line;
    else if (@MU@.verCmp(live, since) < 0) line = "Server Setup page from " + since + " on - " + line;
    else { line = "Its Server Setup page did not load - see the server log. " + line; red = "1"; }
  }
  return new String[] { m, "file", name, line, rl, red };
}""")
M(apg, r"""
public java.util.ArrayList listRows() {
  java.util.ArrayList found = new java.util.ArrayList();
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.HashSet seen = new java.util.HashSet();
  String q = this.search == null ? "" : this.search.trim();
  boolean find = q.length() >= 2;
  String[] cm = cfgMods();
  for (int i = 0; i < cm.length; i++) {
    String m = cm[i];
    seen.add(m);
    Object[] h = hdr(m);
    // 0.3.25: a running mod on the registry lists its matching SETTINGS (and itself first when its name matches)
    if (find && h != null && contractOk(h) && alive(m)) {
      if (has(m, q) || has(hs(h, 2), q)) addRow(found, keys, "0" + m.toLowerCase(), cfgRow(m, h, null));
      java.util.ArrayList hits = settingHits(m, h, q);
      for (int j = 0; j < hits.size(); j++) addRow(found, keys, "0" + m.toLowerCase(), (String[]) hits.get(j));
      continue;
    }
    String[] e = cfgRow(m, h, find ? q : null);
    if (e == null) continue;
    addRow(found, keys, "0" + m.toLowerCase(), e);
  }
  for (int k = 0; k < @MD@.MOD_NAME.length; k++) {
    String m = @MD@.MOD_NAME[k];
    if (seen.contains(m) || !installed(k)) continue;
    if (find && !has(m, q)) continue;
    addRow(found, keys, "1" + m.toLowerCase(), fileRow(k));
  }
  java.util.Collections.sort(keys);
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < keys.size(); i++) {
    String s = (String) keys.get(i);
    out.add(found.get(Integer.parseInt(s.substring(s.indexOf('\t') + 1))));
  }
  return out;
}""")
M(apg, r"""
public void drawList(@UCB@ b, @UEB@ ev) {
  java.util.ArrayList lr = listRows();
  this.listPage = 0;                                     // 0.3.36: one scroll list (no pages)
  String q = this.search == null ? "" : this.search.trim();
  int ncfg = 0;
  int nfile = 0;
  for (int i = 0; i < lr.size(); i++) { if ("cfg".equals(((String[]) lr.get(i))[1])) ncfg++; else nfile++; }
  String sub = @MD@.ADM_LISTSUB;
  if (q.length() < 2 && nfile > 0) sub = ncfg + (ncfg == 1 ? " mod is" : " mods are") + " set up for in-game editing - the rest show their file. Click Open.";
  int nhit = 0;
  for (int i = 0; i < lr.size(); i++) if ("hit".equals(((String[]) lr.get(i))[1])) nhit++;
  if (q.length() >= 2) sub = "Search: every mod's settings by name, help text or key (every word must match).";   // 0.3.25
  if (q.length() >= 2 && this.status.length() == 0) {
    if (lr.isEmpty()) setStatus("Nothing matches \"" + q + "\" - try other words. Mods not set up yet are matched by name only.", 2);
    else if (nhit > 0) setStatus(nhit + (nhit == 1 ? " match" : " matches") + " for \"" + q + "\" - Go to opens the setting, ready to change.", 0);
    else setStatus(lr.size() + (lr.size() == 1 ? " mod matches" : " mods match") + " \"" + q + "\" - Open shows the first hit.", 0);
  }
  evReset();
  evField("Find", "SkyyAdmFind");
  frame(b, "Server Setup", sub);
  b.appendInline("#SkyyAdmBody", @MD@.UI_ALSEARCH);
  field(b, "#SkyyAdmSearch", "SkyyAdmFind", 660, 50, 60, q, "search settings and editors");   // 0.3.36: Admin = a crumb now
  b.appendInline("#SkyyAdmSearch", spc(10, 50));
  b.appendInline("#SkyyAdmSearch", btn("SkyyAdmFindGo", 130, 50, "Search", @MD@.ADM_BS));
  b.appendInline("#SkyyAdmSearch", spc(10, 50));
  b.appendInline("#SkyyAdmSearch", btn("SkyyAdmFindClr", 130, 50, "Clear", @MD@.ADM_BS));
  bind(ev, "SkyyAdmFindGo", "afind");
  bind(ev, "SkyyAdmFindClr", "aclear");
  bindEnter(ev, "SkyyAdmFind", "afind");
  b.appendInline("#SkyyAdmBody", @MD@.UI_ALROWS);
  int nl = lr.size();
  this.listMods = new String[nl];
  this.listReload = new String[nl];
  this.listJump = new String[nl];
  int sz = @PKG@.HubBar.growSize(nl, @MD@.ADM_IN_LIST, @MD@.ADM_RH_L, 6);   // Skyy rule 7: a short list fills its room
  for (int r = 0; r < nl; r++) {
    String[] e = (String[]) lr.get(r);
    this.listMods[r] = e[0];
    this.listReload[r] = e[4];
    this.listJump[r] = e.length > 6 ? e[6] : "";   // 0.3.25
    String rsel = "#SkyyAdmLRow" + r;
    b.appendInline("#SkyyAdmLRows", "Group #SkyyAdmLRow" + r + @MD@.UI_ALROWB[sz]);
    b.appendInline(rsel, spc(14, 52));
    b.appendInline(rsel, @MD@.UI_ALTXTA + r + @MD@.UI_ALTXTB);
    b.appendInline("#SkyyAdmLTxt" + r, @MD@.UI_ALNAMEA + r + @MD@.UI_ALNAMEB);
    b.appendInline("#SkyyAdmLTxt" + r, "1".equals(e[5]) ? @MD@.UI_ALDESCREDA + r + @MD@.UI_ALDESCREDB : @MD@.UI_ALDESCA + r + @MD@.UI_ALDESCB);
    b.set("#SkyyAdmLName" + r + ".Text", e[2]);
    b.set("#SkyyAdmLDesc" + r + ".Text", @MU@.clip(e[3], 118));
    b.appendInline(rsel, spc(10, 52));
    b.appendInline(rsel, btn("SkyyAdmLOpen" + r, 150, 52, this.listJump[r].length() > 0 ? "Go to" : "Open", @MD@.ADM_BS));
    bind(ev, "SkyyAdmLOpen" + r, "aopen" + r);
    b.appendInline(rsel, spc(10, 52));
    if (e[4].length() > 0) {
      b.appendInline(rsel, btn("SkyyAdmLRel" + r, 150, 52, "Reload", @MD@.ADM_BS));
      bind(ev, "SkyyAdmLRel" + r, "arel" + r);
    }
    b.appendInline("#SkyyAdmLRows", @MD@.UI_AGAP6);
  }
  if (lr.isEmpty()) {
    b.appendInline("#SkyyAdmLRows", @MD@.UI_AEMPTY);
    b.set("#SkyyAdmEmpty.Text", q.length() >= 2 ? "No mod matches - click Clear to see every mod." : "No Skyy mod found on this server.");
  }
  fReset();
  foot("Changes", "achanges", 150);
  foot("Export all", "aexpall", 150);
  foot("Refresh", "arefresh", 130);
  // 0.3.35: the view crumbs lead away (sub-tab row; was a footer button, site 0)
  foot("Close", "aclose", 120);
  tail(b, ev);
}""")
# ---- view mod (spec 2.5): tabs, 7 rows per page, a widget per type, Default; a mod not on the registry shows its file (spec 2.11)
M(apg, r"""
public int[] visible(Object[] h) {
  Object[] rs = rowsOf(h);
  int n = 0;
  int[] tmp = new int[rs.length];
  for (int i = 0; i < rs.length; i++) {
    Object[] r = rowAt(h, i);
    if (r == null || catOf(h, r) != this.cat) continue;
    if (hasFlag(r, "adv") && !this.showAdv) continue;
    tmp[n] = i;
    n++;
  }
  int[] out = new int[n];
  System.arraycopy(tmp, 0, out, 0, n);
  return out;
}""")
M(apg, r"""
public int hiddenAdv(Object[] h) {
  if (this.showAdv) return 0;
  Object[] rs = rowsOf(h);
  int n = 0;
  for (int i = 0; i < rs.length; i++) { Object[] r = rowAt(h, i); if (r != null && catOf(h, r) == this.cat && hasFlag(r, "adv")) n++; }
  return n;
}""")
M(apg, r"""
public void jump(Object[] h) {
  String q = this.search == null ? "" : this.search.trim();
  if (q.length() < 2) return;
  int i = firstHit(h, q);
  if (i < 0) {
    String[] ids = catIds(h);
    for (int c = 0; c < ids.length; c++) if (has(catLabel(h, c), q)) { this.cat = c; this.modPage = 0; return; }
    return;
  }
  Object[] r = rowAt(h, i);
  this.cat = catOf(h, r);
  if (hasFlag(r, "adv")) this.showAdv = true;
  int[] vis = visible(h);
  for (int k = 0; k < vis.length; k++) if (vis[k] == i) { this.modPage = k / @MD@.ADM_ROWS; return; }
}""")
# 0.3.25: open the mod on the tab + page of row i (an advanced row switches "show advanced" on) - a search result's Go to
M(apg, r"""
public void jumpTo(Object[] h, int i) {
  Object[] r = rowAt(h, i);
  if (r == null) return;
  this.cat = catOf(h, r);
  if (hasFlag(r, "adv")) this.showAdv = true;
  int[] vis = visible(h);
  for (int k = 0; k < vis.length; k++) if (vis[k] == i) { this.modPage = k / @MD@.ADM_ROWS; break; }
  setStatus("Found: " + rv(r, 1) + " (" + catLabel(h, this.cat) + " tab).", 0);
}""")
M(apg, r"""
public static boolean typed(String t) {
  return t.equals("int") || t.equals("dec") || t.equals("text") || t.equals("range") || t.equals("color");
}""")
M(apg, r"""
public static String fileLine(Object[] h) {
  String[] fs = hs(h, 8).split(",");
  String f0 = fs.length > 0 ? fs[0].trim() : "";
  String more = "";
  if (fs.length == 2) more = " and 1 more file";
  if (fs.length > 2) more = " and " + (fs.length - 1) + " more files";
  return "Saved to " + f0 + more + " - changes are written at once.";
}""")
M(apg, r"""
public void drawRow(@UCB@ b, @UEB@ ev, Object[] h, int i, int r, boolean edit, boolean ok, String q) {
  Object[] w = rowAt(h, i);
  String key = rv(w, 0);
  String label = rv(w, 1);
  String type = rv(w, 3);
  String opts = rv(w, 7);
  boolean ro = !edit || hasFlag(w, "ro");
  String val = null;
  if (ok && !type.equals("link") && !type.equals("action") && !type.equals("table")) val = cur(this.mod, key);
  String draft = (String) this.drafts.get(key);
  boolean ms = msRow(w);
  String valShown = val == null ? null : (ms ? secText(val) : val);      // 0.3.4: (the choice widget below has its own "shown")
  if (draft != null && val != null && (draft.trim().equals(valShown) || (ms && val.equals(msOf(draft, !type.equals("dec")))))) { this.drafts.remove(key); draft = null; }
  String rsel = "#SkyyAdmRow" + r;
  String line = "#SkyyAdmLine" + r;
  String wsel = "#SkyyAdmW" + r;
  b.appendInline("#SkyyAdmRows", "Group #SkyyAdmRow" + r + @MD@.UI_AROWB[this.rowSz]);   // 0.3.36: the grow tier (drawMod)
  b.appendInline(rsel, @MD@.UI_ALINEA + r + @MD@.UI_ALINEB);
  b.appendInline(line, spc(14, 42));
  b.appendInline(line, @MD@.UI_ANAMEA + r + @MD@.UI_ANAMEB);
  b.appendInline(line, spc(10, 42));
  b.appendInline(line, @MD@.UI_AWA + r + @MD@.UI_AWB);
  b.appendInline(line, spc(10, 42));
  boolean def = false;
  if (type.equals("table")) {
    Object k = null;
    if (ok) k = call(this.mod, new Object[] { "keys", key, "" });
    int n = (k instanceof Object[] && ((Object[]) k).length > 0 && ((Object[]) k)[0] instanceof String[]) ? ((String[]) ((Object[]) k)[0]).length : 0;
    b.appendInline(wsel, btn("SkyyAdmEdit" + r, 240, 42, "Open - " + n + (n == 1 ? " entry" : " entries"), @MD@.ADM_BS));
    bindR(ev, r, "SkyyAdmEdit" + r, "aedit" + r);
  } else if (type.equals("items")) {
    int n = csv(val).size();
    b.appendInline(wsel, btn("SkyyAdmEdit" + r, 240, 42, (ro ? "Open - " : "Edit - ") + n + (n == 1 ? " item" : " items"), @MD@.ADM_BS));
    bindR(ev, r, "SkyyAdmEdit" + r, "aedit" + r);
    def = !ro;
  } else if (type.equals("link")) {
    b.appendInline(wsel, btn("SkyyAdmEdit" + r, 240, 42, "Open", @MD@.ADM_BS));
    bindR(ev, r, "SkyyAdmEdit" + r, "alink" + r);
  } else if (ro) {
    b.appendInline(wsel, @MD@.UI_AROA + r + @MD@.UI_AROB);
    b.set("#SkyyAdmRo" + r + ".Text", type.equals("action") ? "(admins with " + hs(h, 4) + " can run it)" : disp(w, val));
  } else if (type.equals("bool")) {
    boolean on = "true".equals(val);
    b.appendInline(wsel, btn("SkyyAdmOn" + r, 120, 42, "ON", on ? @MD@.ADM_ONSEL : @MD@.ADM_BS));
    b.appendInline(wsel, spc(10, 42));
    b.appendInline(wsel, btn("SkyyAdmOff" + r, 120, 42, "OFF", on ? @MD@.ADM_BS : @MD@.ADM_OFFSEL));
    bindR(ev, r, "SkyyAdmOn" + r, "aon" + r);
    bindR(ev, r, "SkyyAdmOff" + r, "aoff" + r);
    def = true;
  } else if (typed(type)) {
    String step = (type.equals("int") || type.equals("dec")) ? stepOf(opts) : null;
    field(b, wsel, "SkyyAdmVal" + r, step != null ? 156 : 270, 42, 2000, draft != null ? draft : (valShown == null ? "" : valShown), "");
    b.appendInline(wsel, spc(6, 42));
    b.appendInline(wsel, btn("SkyyAdmSet" + r, step != null ? 84 : 104, 42, "Set", @MD@.ADM_BS));
    bindR(ev, r, "SkyyAdmSet" + r, "aset" + r);
    bindEnterR(ev, r, "SkyyAdmVal" + r, "aset" + r);
    if (step != null) {
      b.appendInline(wsel, spc(6, 42));
      b.appendInline(wsel, btn("SkyyAdmMinus" + r, 60, 42, "Less", @MD@.ADM_BS));
      b.appendInline(wsel, spc(6, 42));
      b.appendInline(wsel, btn("SkyyAdmPlus" + r, 60, 42, "More", @MD@.ADM_BS));
      bindR(ev, r, "SkyyAdmMinus" + r, "aminus" + r);
      bindR(ev, r, "SkyyAdmPlus" + r, "aplus" + r);
    }
    def = true;
  } else if (type.equals("choice")) {
    String[] vs = chVals(opts);
    String[] ls = chLabels(opts);
    if (vs.length <= 4) {
      int bw = (380 - 6 * (vs.length - 1)) / vs.length;
      for (int j = 0; j < vs.length; j++) {
        if (j > 0) b.appendInline(wsel, spc(6, 42));
        String id = "SkyyAdmCh" + r + "x" + j;
        b.appendInline(wsel, btn(id, bw, 42, @MU@.inl(ls[j]).length() > 0 ? ls[j] : vs[j], vs[j].equals(val) ? @MD@.ADM_SEL16 : @MD@.ADM_BS16));
        bindR(ev, r, id, "ach" + r + "x" + j);
      }
    } else {
      String shown = val == null ? "" : val;
      for (int j = 0; j < vs.length; j++) if (vs[j].equals(val)) shown = ls[j];
      b.appendInline(wsel, btn("SkyyAdmCl" + r, 50, 42, "<", @MD@.ADM_BS));
      b.appendInline(wsel, spc(6, 42));
      b.appendInline(wsel, @MD@.UI_ACHVA + r + @MD@.UI_ACHVB);
      b.appendInline(wsel, spc(6, 42));
      b.appendInline(wsel, btn("SkyyAdmCr" + r, 50, 42, ">", @MD@.ADM_BS));
      b.set("#SkyyAdmChv" + r + ".Text", shown);
      bindR(ev, r, "SkyyAdmCl" + r, "acl" + r);
      bindR(ev, r, "SkyyAdmCr" + r, "acr" + r);
    }
    def = true;
  } else if (type.equals("action")) {
    b.appendInline(wsel, btn("SkyyAdmEdit" + r, 380, 42, opts, hasFlag(w, "danger") ? @MD@.ADM_RED : @MD@.ADM_BS));
    bindR(ev, r, "SkyyAdmEdit" + r, "aact" + r);
  } else {
    b.appendInline(wsel, @MD@.UI_AROA + r + @MD@.UI_AROB);
    b.set("#SkyyAdmRo" + r + ".Text", disp(w, val));
  }
  if (def) {
    b.appendInline(line, btn("SkyyAdmDef" + r, 110, 42, "Default", @MD@.ADM_BS));
    bindR(ev, r, "SkyyAdmDef" + r, "adef" + r);
  } else b.appendInline(line, spc(110, 42));
  b.appendInline(rsel, @MD@.UI_AHELPA + r + @MD@.UI_AHELPB);
  b.appendInline("#SkyyAdmHelpRow" + r, spc(14, 22));
  b.appendInline("#SkyyAdmHelpRow" + r, @MD@.UI_ADESCA + r + @MD@.UI_ADESCB);
  boolean hit = q.length() >= 2 && (has(label, q) || has(rv(w, 10), q));
  String unit = ms ? "s" : rv(w, 8);
  String tg = tagOf(w);
  String nm = (hit ? "> " : "") + label + (unit.length() > 0 ? " (" + unit + ")" : "") + (draft != null ? " *" : "");
  String help = rv(w, 10);
  if (ms) help = secHint(w) + (help.length() > 0 ? " - " + secHelp(help) : "");      // no dangling " - " on a row without help text
  if (tg.length() > 0 && nm.length() + 4 + tg.length() <= 50) nm = nm + "    " + tg;
  else if (tg.length() > 0) help = tg + "  -  " + help;
  b.set("#SkyyAdmName" + r + ".Text", @MU@.clip(nm, 52));
  b.set("#SkyyAdmDesc" + r + ".Text", @MU@.clip(help, 140));
  b.appendInline("#SkyyAdmRows", @MD@.UI_AGAP6);
}""")
M(apg, r"""
public void drawFileOnly(@UCB@ b, @UEB@ ev) {
  int k = modIndex(this.mod);
  evReset();
  String live = this.mod == null ? null : @MU@.liveVersion(this.mod);
  String nm = this.mod == null ? "" : this.mod;
  String since = k < 0 ? "" : @MD@.MOD_SINCE[k];
  boolean off = since.length() > 0 && live == null;
  boolean older = since.length() > 0 && live != null && @MU@.verCmp(live, since) < 0;
  frame(b, "Server Setup - " + nm + (live != null ? " " + live : ""), k < 0 ? "This mod has no settings page on this server."
      : (since.length() == 0 ? "Not set up for in-game editing yet - edit its file, then reload it."
      : (off ? "It is not running on this server - its file can still be edited."
      : (older ? "This version has no Server Setup page yet - edit its file, then reload it."
      : "Its Server Setup page did not load - edit its file, then reload it."))));
  java.util.ArrayList txt = new java.util.ArrayList();
  java.util.ArrayList bold = new java.util.ArrayList();
  if (k >= 0) {
    String[] fs = @MD@.MOD_CFG[k].length() == 0 ? new String[0] : @MD@.MOD_CFG[k].split(",");
    if (fs.length > 0) {
      txt.add(fs.length == 1 ? "Config file" : "Config files"); bold.add("1");
      for (int i = 0; i < fs.length; i++) { txt.add("    <world>/mods/" + fs[i].trim()); bold.add("0"); }
      txt.add(""); bold.add("0");
      txt.add("After editing"); bold.add("1");
      if (@MD@.MOD_RELOAD[k].length() > 0) { txt.add("    /" + @MD@.MOD_RELOAD[k] + " - reads the file again (the Reload button below runs it for you)"); bold.add("0"); }
      if (@MD@.MOD_NOTE[k].length() > 0) { txt.add("    " + @MD@.MOD_NOTE[k]); bold.add("0"); }
      if (@MD@.MOD_RELOAD[k].length() == 0 && @MD@.MOD_NOTE[k].length() == 0) { txt.add("    Restart the server."); bold.add("0"); }
    } else {
      txt.add(@MD@.MOD_NOTE[k]); bold.add("0");
    }
    String adm = @MD@.MOD_ADMIN[k];
    if (adm.length() > 0) {
      txt.add(""); bold.add("0");
      txt.add("Admin commands"); bold.add("1");
      String[] al = adm.split("\n");
      for (int i = 0; i < al.length; i++) { txt.add("    " + al[i]); bold.add("0"); }
    }
    txt.add(""); bold.add("0");
    if (since.length() == 0) { txt.add("Its settings show up here, with buttons, once its next version is set up for in-game editing."); bold.add("0"); }
    else {
      txt.add("Server Setup page: " + @MD@.MOD_STITLE[k] + " - " + @MD@.MOD_SWHAT[k] + "."); bold.add("1");
      if (off) { txt.add("    " + nm + " is not running here (disabled or missing) - see the server log."); bold.add("0"); }
      else if (older) { txt.add("    It comes with " + nm + " " + since + " - this server runs " + live + ". Update it, then restart."); bold.add("0"); }
      else { txt.add("    It did not publish its settings - look for " + nm + " errors in the server log."); bold.add("0"); }
    }
  }
  b.appendInline("#SkyyAdmBody", @MD@.UI_AINFO);
  for (int i = 0; i < txt.size() && i < @MD@.ADM_INFOLINES; i++) {
    b.appendInline("#SkyyAdmInfo", "1".equals(bold.get(i)) ? @MD@.UI_AINFOB[i] : @MD@.UI_AINFOL[i]);
    b.set("#SkyyAdmInfo" + i + ".Text", (String) txt.get(i));
  }
  fReset();
  String rl = k >= 0 ? @MD@.MOD_RELOAD[k] : "";
  if (rl.length() > 0 && @MU@.cmd(@MU@.firstWord(rl)) != null) foot("Reload", "afrel", 150);
  // 0.3.35: the view crumbs lead away (sub-tab row; was a footer button, site 1)
  foot("Close", "aclose", 150);
  tail(b, ev);
}""")
M(apg, r"""
public void drawMod(@UCB@ b, @UEB@ ev) {
  Object[] h = hdr(this.mod);
  if (h == null) { drawFileOnly(b, ev); return; }
  String node = hs(h, 4);
  boolean editor = canEdit(node);
  boolean ok = contractOk(h) && alive(this.mod);
  boolean edit = editor && ok;
  String[] ids = catIds(h);
  int nCat = ids.length;
  if (this.jumpHit) { jump(h); this.jumpHit = false; }
  if (this.jumpRow >= 0) { jumpTo(h, this.jumpRow); this.jumpRow = -1; }   // 0.3.25
  if (this.cat >= nCat) this.cat = nCat - 1;
  if (this.cat < 0) this.cat = 0;
  int[] vis = visible(h);
  int nv = vis.length;
  this.modPage = 0;                                      // 0.3.36: one scroll list of the category (no pages)
  evReset();
  this.rowKeys = new String[nv];
  this.boxRows = new java.util.HashSet();
  int nbox = 0;
  for (int r = 0; r < nv; r++) {
    Object[] w = rowAt(h, vis[r]);
    this.rowKeys[r] = rv(w, 0);
    if (ok && edit && !hasFlag(w, "ro") && typed(rv(w, 3))) {
      this.boxRows.add(Integer.valueOf(r));                // its own buttons carry its box (bindR)
      if (nbox < @MD@.ADM_MFIELDS) evField("V" + r, "SkyyAdmVal" + r);   // crumbs / footer: the first ADM_MFIELDS boxes
      nbox++;
    }
  }
  String sub = fileLine(h);
  if (!contractOk(h)) sub = @MD@.ADM_NEWER;
  else if (!alive(this.mod)) sub = this.mod + " is not running - its settings cannot be changed now.";
  else if (!editor) sub = "View only - changing " + this.mod + " needs " + node + ".";
  frame(b, "Server Setup - " + hs(h, 2) + " (" + this.mod + " " + hs(h, 3) + ")", sub);
  // 0.3.36: the categories are in the sub-tab row (crumbs(): All mods | <mod> | <category ...>) - no in-body tab rows
  boolean catPick = nCat > catFit();                     // critic 2: too many categories for the sub row -> the in-page picker
  if (catPick) picker(b, ev, "Category", catLabel(h, this.cat) + "  (" + (this.cat + 1) + " of " + nCat + ")", "cfprev", "cfnext");
  b.appendInline("#SkyyAdmBody", @MD@.UI_AHEAD);
  b.appendInline("#SkyyAdmBody", catPick ? @MD@.UI_AROWSP : @MD@.UI_AROWS);
  String q = this.search == null ? "" : this.search.trim();
  this.rowSz = @PKG@.HubBar.growSize(nv, catPick ? @MD@.ADM_IN_MODP : @MD@.ADM_IN_MOD, @MD@.ADM_RH_M, 6);   // Skyy rule 7: a short category fills its room
  for (int r = 0; r < nv; r++) drawRow(b, ev, h, vis[r], r, edit, ok, q);
  int adv = hiddenAdv(h);
  if (vis.length == 0) {
    b.appendInline("#SkyyAdmRows", @MD@.UI_AEMPTY);
    b.set("#SkyyAdmEmpty.Text", adv > 0 ? "Only advanced settings on this tab - switch Advanced to ON (footer button) to show them." : "Nothing on this tab.");
  }
  int n = vis.length;
  b.set("#SkyyAdmHead.Text", catLabel(h, this.cat) + "   -   " + n + (n == 1 ? " setting" : " settings")
      + (adv > 0 ? "   -   " + adv + " advanced hidden" : "") + (nbox > @MD@.ADM_MFIELDS ? "   -   past box " + @MD@.ADM_MFIELDS + ", press its Set" : ""));
  if (this.status.length() == 0 && ok) {
    Object st = call(this.mod, new Object[] { "status" });
    if (st instanceof String[] && ((String[]) st).length >= 2 && !"ok".equals(((String[]) st)[0])) {
      String s0 = ((String[]) st)[0];
      setStatus(((String[]) st)[1], "restart".equals(s0) ? 2 : 3);
    } else if (hs(h, 9).length() > 0) setStatus(hs(h, 9), 0);
  }
  fReset();
  foot("History", "ahist", 120);
  foot("Export / Import", "aio", 180);
  if (edit) foot("Reload file", "areload", 140);
  foot(this.showAdv ? "Advanced ON" : "Advanced OFF", "aadv", 160);
  // 0.3.35: the view crumbs lead away (sub-tab row; was a footer button, site 2)
  foot("Close", "aclose", 100);
  tail(b, ev);
}""")
# ---- view table (spec 2.6): a table row's entries, or an items row edited as a list kept in this page and saved with ONE set
M(apg, r"""
public static int[] colW(int n) {
  if (n >= 3) return new int[] { 146, 146, 146 };
  if (n == 2) return new int[] { 222, 222 };
  return new int[] { 450 };
}""")
M(apg, r"""
public String entryLabel(String e) {
  if ("SkyyMenu".equals(this.mod) && "settings.defaults".equals(this.tableKey)) {
    Object[] d = @PKG@.SetReg.info(e);
    if (d != null) return String.valueOf(d[2]);
  }
  return e;
}""")
M(apg, r"""
public void drawTable(@UCB@ b, @UEB@ ev) {
  Object[] h = hdr(this.mod);
  Object[] w = rowAt(h, rowIdx(h, this.tableKey));
  if (w == null) { this.view = "mod"; drawMod(b, ev); return; }
  boolean itemsMode = rv(w, 3).equals("items");
  boolean edit = canEdit(hs(h, 4)) && !hasFlag(w, "ro") && contractOk(h) && alive(this.mod);
  String opts = rv(w, 7);
  String[] cols = null;
  String mode = null;
  if (itemsMode) {
    cols = hasOpt(opts, "qty") ? new String[] { "Amount" } : new String[0];
    mode = "both";
  } else {
    cols = tCols(opts);
    mode = tMode(opts);
  }
  if (cols.length > 3) { String[] c3 = new String[3]; System.arraycopy(cols, 0, c3, 0, 3); cols = c3; }
  java.util.ArrayList eks = new java.util.ArrayList();
  java.util.ArrayList evs = new java.util.ArrayList();
  String flt = this.tFilter == null ? "" : this.tFilter.trim().toLowerCase();
  if (itemsMode) {
    for (int i = 0; i < this.items.size(); i++) {
      String it = String.valueOf(this.items.get(i));
      int c = it.lastIndexOf(':');
      String id = c > 0 && cols.length > 0 ? it.substring(0, c) : it;
      String qty = c > 0 && cols.length > 0 ? it.substring(c + 1) : "";
      if (flt.length() > 0 && id.toLowerCase().indexOf(flt) < 0) continue;
      eks.add(id);
      evs.add(qty);
    }
  } else if (contractOk(h) && alive(this.mod)) {
    Object o = call(this.mod, new Object[] { "keys", this.tableKey, flt });
    if (o instanceof Object[] && ((Object[]) o).length >= 3 && ((Object[]) o)[0] instanceof String[] && ((Object[]) o)[2] instanceof String[]) {
      String[] ks = (String[]) ((Object[]) o)[0];
      String[] vs = (String[]) ((Object[]) o)[2];
      for (int i = 0; i < ks.length; i++) { eks.add(ks[i]); evs.add(i < vs.length ? vs[i] : ""); }
    }
  }
  int per = eks.size();                                  // 0.3.36: one scroll list (no pages), capped:
  if (edit && cols.length > 0) { if (per > @MD@.ADM_TFIELDS / cols.length) per = @MD@.ADM_TFIELDS / cols.length; }
  else if (per > @MD@.ADM_TMAX) per = @MD@.ADM_TMAX;
  this.tPage = 0;
  boolean typeAdd = edit && (mode.equals("type") || mode.equals("both"));
  boolean heldAdd = edit && (mode.equals("held") || mode.equals("both"));
  int[] cw = colW(cols.length);
  evReset();
  evField("TF", "SkyyAdmTFind");
  this.tKeys = new String[per];
  this.tVals = new String[per];
  for (int r = 0; r < per; r++) {
    this.tKeys[r] = (String) eks.get(r);
    this.tVals[r] = (String) evs.get(r);
    if (edit) for (int c = 0; c < cols.length; c++) evField("C" + r + "x" + c, "SkyyAdmCol" + r + "x" + c);
  }
  if (typeAdd) evField("AK", "SkyyAdmAddKey");
  if (typeAdd || heldAdd) for (int c = 0; c < cols.length; c++) evField("A" + c, "SkyyAdmAdd" + c);
  String sub = null;
  if (itemsMode) sub = edit ? "Edit the list, then click Save list - nothing changes until you save it." : "View only.";
  else {
    StringBuilder cn = new StringBuilder();
    for (int c = 0; c < cols.length; c++) { if (c > 0) cn.append(" | "); cn.append(cols[c]); }
    sub = "Columns: " + cn.toString() + (edit ? " - type in the boxes and click Set." : " - view only.");
    if ("SkyyMenu".equals(this.mod) && "settings.defaults".equals(this.tableKey))
      sub = (edit ? "Type on, off or unset and click Set. " : "View only. ") + "Menu hover tooltips is the same line as the Hover tooltips default row.";
  }
  frame(b, hs(h, 2) + " - " + rv(w, 1), sub);
  b.appendInline("#SkyyAdmBody", @MD@.UI_ATFIND);
  b.appendInline("#SkyyAdmTFindRow", spc(200, 50));
  field(b, "#SkyyAdmTFindRow", "SkyyAdmTFind", 400, 50, 80, this.tFilter, "filter");
  b.appendInline("#SkyyAdmTFindRow", spc(10, 50));
  b.appendInline("#SkyyAdmTFindRow", btn("SkyyAdmTGo", 130, 50, "Search", @MD@.ADM_BS));
  b.appendInline("#SkyyAdmTFindRow", spc(10, 50));
  b.appendInline("#SkyyAdmTFindRow", btn("SkyyAdmTClr", 130, 50, "Clear", @MD@.ADM_BS));
  bind(ev, "SkyyAdmTGo", "tfind");
  bind(ev, "SkyyAdmTClr", "tclear");
  bindEnter(ev, "SkyyAdmTFind", "tfind");
  b.appendInline("#SkyyAdmBody", @MD@.UI_AHEAD);
  int n = eks.size();
  b.set("#SkyyAdmHead.Text", rv(w, 1) + "   -   " + n + (itemsMode ? (n == 1 ? " item" : " items") : (n == 1 ? " entry" : " entries"))
      + (flt.length() > 0 ? " match" : "") + (per < n ? "   -   " + per + " shown, the filter finds the rest" : ""));
  if (per < n && this.status.length() == 0) setStatus("Showing " + per + " of " + n + " - type in the filter to find the rest.", 2);   // critic 3
  b.appendInline("#SkyyAdmBody", @MD@.UI_ATCOLS);
  b.appendInline("#SkyyAdmCols", spc(14, 30));
  b.appendInline("#SkyyAdmCols", lab("SkyyAdmCh0", 300, 30, 16, true, "#9fb8cc"));
  b.set("#SkyyAdmCh0.Text", itemsMode ? "Item" : "Entry");
  b.appendInline("#SkyyAdmCols", spc(10, 30));
  for (int c = 0; c < cols.length; c++) {
    if (c > 0) b.appendInline("#SkyyAdmCols", spc(6, 30));
    b.appendInline("#SkyyAdmCols", lab("SkyyAdmCh" + (c + 1), cw[c], 30, 16, true, "#9fb8cc"));
    b.set("#SkyyAdmCh" + (c + 1) + ".Text", cols[c]);
  }
  b.appendInline("#SkyyAdmBody", typeAdd || heldAdd ? @MD@.UI_ATROWSA : @MD@.UI_ATROWSB);
  boolean canRemove = edit && (itemsMode || !mode.equals("none"));
  int sz = @PKG@.HubBar.growSize(per, typeAdd || heldAdd ? @MD@.ADM_IN_TABLEADD : @MD@.ADM_IN_TABLE, @MD@.ADM_RH_T, 6);
  for (int r = 0; r < per; r++) {
    String e = this.tKeys[r];
    if (e == null) break;
    String rsel = "#SkyyAdmTRow" + r;
    b.appendInline("#SkyyAdmTRows", "Group #SkyyAdmTRow" + r + @MD@.UI_ATROWB[sz]);
    b.appendInline(rsel, spc(14, 52));
    b.appendInline(rsel, @MD@.UI_ATKEYA + r + @MD@.UI_ATKEYB);
    b.set("#SkyyAdmTKey" + r + ".Text", @MU@.clip(itemsMode ? e : entryLabel(e), 30));
    b.appendInline(rsel, spc(10, 52));
    b.appendInline(rsel, @MD@.UI_ATCELLSA + r + @MD@.UI_ATCELLSB);
    String[] parts = this.tVals[r].split("\\|", -1);
    for (int c = 0; c < cols.length; c++) {
      if (c > 0) b.appendInline("#SkyyAdmTCols" + r, spc(6, 52));
      String v = c < parts.length ? parts[c] : "";
      String d = (String) this.tDrafts.get(e + "\t" + c);
      if (edit) {
        field(b, "#SkyyAdmTCols" + r, "SkyyAdmCol" + r + "x" + c, cw[c], 52, 200, d != null ? d : v, "");
        bindEnter(ev, "SkyyAdmCol" + r + "x" + c, "tset" + r);
      } else {
        b.appendInline("#SkyyAdmTCols" + r, lab("SkyyAdmColv" + r + "x" + c, cw[c], 52, 18, false, "#ffe9a0"));
        b.set("#SkyyAdmColv" + r + "x" + c + ".Text", v);
      }
    }
    b.appendInline(rsel, spc(10, 52));
    if (edit && cols.length > 0) { b.appendInline(rsel, btn("SkyyAdmTSet" + r, 100, 52, "Set", @MD@.ADM_BS)); bind(ev, "SkyyAdmTSet" + r, "tset" + r); }
    else b.appendInline(rsel, spc(100, 52));
    b.appendInline(rsel, spc(6, 52));
    if (canRemove) { b.appendInline(rsel, btn("SkyyAdmTRem" + r, 150, 52, "Remove", @MD@.ADM_BS)); bind(ev, "SkyyAdmTRem" + r, "trem" + r); }
    b.appendInline("#SkyyAdmTRows", @MD@.UI_AGAP6);
  }
  if (eks.isEmpty()) {
    b.appendInline("#SkyyAdmTRows", @MD@.UI_AEMPTY);
    b.set("#SkyyAdmEmpty.Text", flt.length() > 0 ? "Nothing matches the filter - click Clear." : (itemsMode ? "The list is empty." : "No entries yet."));
  }
  if (typeAdd || heldAdd) {
    b.appendInline("#SkyyAdmBody", @MD@.UI_ATADD);
    b.appendInline("#SkyyAdmTAdd", spc(14, 50));
    if (typeAdd) {
      field(b, "#SkyyAdmTAdd", "SkyyAdmAddKey", 300, 50, 120, this.tAdd[0], itemsMode ? "item id" : "new entry");
      bindEnter(ev, "SkyyAdmAddKey", "tadd");
    } else b.appendInline("#SkyyAdmTAdd", spc(300, 50));
    b.appendInline("#SkyyAdmTAdd", spc(10, 50));
    for (int c = 0; c < cols.length; c++) {
      if (c > 0) b.appendInline("#SkyyAdmTAdd", spc(6, 50));
      field(b, "#SkyyAdmTAdd", "SkyyAdmAdd" + c, cw[c], 50, 200, this.tAdd[c + 1], cols[c]);
    }
    if (cols.length == 0) b.appendInline("#SkyyAdmTAdd", spc(450, 50));
    b.appendInline("#SkyyAdmTAdd", spc(10, 50));
    if (typeAdd) { b.appendInline("#SkyyAdmTAdd", btn("SkyyAdmTAddGo", 100, 50, "Add", @MD@.ADM_BS)); bind(ev, "SkyyAdmTAddGo", "tadd"); }
    else b.appendInline("#SkyyAdmTAdd", spc(100, 50));
    b.appendInline("#SkyyAdmTAdd", spc(6, 50));
    if (heldAdd) { b.appendInline("#SkyyAdmTAdd", btn("SkyyAdmTHeld", 150, 50, "Add held item", @MD@.ADM_BS)); bind(ev, "SkyyAdmTHeld", "theld"); }
  }
  fReset();
  if (itemsMode && edit) { foot("Save list", "tsave", 150); foot("Undo edits", "tundo", 150); }
  // 0.3.35: the view crumbs lead away (sub-tab row; was a footer button, table)
  foot("Close", "aclose", 110);
  tail(b, ev);
}""")
# ---- view confirm (spec 2.7)
M(apg, r"""
public void drawConfirm(@UCB@ b, @UEB@ ev) {
  evReset();
  Object[] h = hdr(this.pendingMod);
  String who = this.pendingKind == 1 ? "Every mod in the code" : (h != null ? hs(h, 2) + " (" + this.pendingMod + ")" : (this.pendingMod == null ? "" : this.pendingMod));
  frame(b, "Please confirm", who);
  b.appendInline("#SkyyAdmBody", @MD@.UI_AMSGBOX);
  java.util.ArrayList ls = wrap(this.pendingMsg, 92);
  int max = @MD@.ADM_MSGLINES;
  for (int i = 0; i < ls.size() && i < max; i++) {
    b.appendInline("#SkyyAdmMsgBox", i == 0 ? @MD@.UI_AMSGQ[i] : @MD@.UI_AMSGL[i]);
    String t = (String) ls.get(i);
    if (i == max - 1 && ls.size() > max) t = "and " + (ls.size() - max + 1) + " more lines";
    b.set("#SkyyAdmMsg" + i + ".Text", t);
  }
  b.appendInline("#SkyyAdmBody", @MD@.UI_AGAP20);
  b.appendInline("#SkyyAdmBody", @MD@.UI_ACONF);
  b.appendInline("#SkyyAdmConf", spc(260, 56));
  b.appendInline("#SkyyAdmConf", btn("SkyyAdmYes", 260, 56, "Confirm", @MD@.ADM_RED));
  b.appendInline("#SkyyAdmConf", spc(40, 56));
  b.appendInline("#SkyyAdmConf", btn("SkyyAdmNo", 260, 56, "Cancel", @MD@.ADM_BS));
  bind(ev, "SkyyAdmYes", "ayes");
  bind(ev, "SkyyAdmNo", "ano");
  fReset();
  tail(b, ev);
}""")
# ---- view log (spec 2.8): every set-up mod's log op (40 newest each), newest first
M(apg, r"""
public static String logText(Object[] h, String m, String[] f) {
  String title = h == null ? m : hs(h, 2);
  String key = f[4];
  String when = timeShort(f[0]);
  String tail = "  (" + f[3] + ")" + ("ok".equals(f[7]) ? "" : "  [" + f[7] + "]");
  int bk = key.indexOf('[');
  if (bk > 0 && key.endsWith("]")) {
    String tk = key.substring(0, bk);
    String e = key.substring(bk + 1, key.length() - 1);
    Object[] w = rowAt(h, rowIdx(h, tk));
    String lbl = w == null ? tk : rv(w, 1);
    String what = null;
    if (f[5].equals("(none)")) what = "added  " + f[6].replace("|", " / ");
    else if (f[6].equals("(none)")) what = "removed";
    else what = f[5].replace("|", " / ") + " -> " + f[6].replace("|", " / ");
    return when + "  " + f[1] + "  " + title + "  " + lbl + ": " + e + "  " + what + tail;
  }
  Object[] w = rowAt(h, rowIdx(h, key));
  String lbl = w == null ? key : rv(w, 1);
  if (f[6].equals("(action)")) return when + "  " + f[1] + "  " + title + "  " + lbl + "  done" + tail;
  String o = w == null ? f[5] : disp(w, f[5]);
  String n = w == null ? f[6] : disp(w, f[6]);
  return when + "  " + f[1] + "  " + title + "  " + lbl + "  " + o + " -> " + n + tail;
}""")
M(apg, r"""
public void drawLog(@UCB@ b, @UEB@ ev) {
  evReset();
  java.util.ArrayList all = new java.util.ArrayList();
  java.util.ArrayList mods = new java.util.ArrayList();
  java.util.HashMap hdrs = new java.util.HashMap();
  String[] cm = cfgMods();
  for (int i = 0; i < cm.length; i++) {
    String m = cm[i];
    Object[] h = hdr(m);
    if (h == null || !contractOk(h) || !alive(m)) continue;
    hdrs.put(m, h);
    Object o = call(m, new Object[] { "log", Integer.valueOf(40) });
    if (!(o instanceof String[])) continue;
    String[] ls = (String[]) o;
    if (ls.length > 0 && mods.size() < 15) mods.add(m);
    if (this.logMod.length() > 0 && !this.logMod.equals(m)) continue;
    for (int k = 0; k < ls.length; k++) {
      String[] f = ls[k].split("\t", -1);
      if (f.length < 8) continue;
      all.add(f[0] + "\t" + (900000 - k) + "\t" + m + "\t" + ls[k]);
    }
  }
  java.util.Collections.sort(all);
  java.util.Collections.reverse(all);
  String[] tabs = new String[mods.size() + 1];
  tabs[0] = "";
  for (int i = 0; i < mods.size(); i++) tabs[i + 1] = (String) mods.get(i);
  this.logTabs = tabs;
  int per = all.size() > @MD@.ADM_GMAX ? @MD@.ADM_GMAX : all.size();   // 0.3.36: one scroll list, the newest ADM_GMAX (no pages)
  this.logPage = 0;
  int ti = 0;
  for (int i = 0; i < tabs.length; i++) if (tabs[i].equals(this.logMod)) ti = i;
  frame(b, "Server Setup - Changes", "Every change made in game, by command or by hand, newest first. Undo puts one value back.");
  String scope = this.logMod.length() == 0 ? "All mods" : hs((Object[]) hdrs.get(this.logMod), 2);
  picker(b, ev, "Show the changes of", scope + "  (" + (ti + 1) + " of " + tabs.length + ")", "lfprev", "lfnext");   // 0.3.36: no tab rows
  b.appendInline("#SkyyAdmBody", @MD@.UI_AHEAD);
  b.set("#SkyyAdmHead.Text", scope + "   -   " + all.size() + (all.size() == 1 ? " change" : " changes") + (per < all.size() ? "   -   the newest " + per + " shown" : ""));
  b.appendInline("#SkyyAdmBody", @MD@.UI_AGROWS);
  this.logShown = new java.util.ArrayList();
  int sz = @PKG@.HubBar.growSize(per, @MD@.ADM_IN_LOG, @MD@.ADM_RH_G, 6);
  for (int r = 0; r < per; r++) {
    String s = (String) all.get(r);
    int t0 = s.indexOf('\t');
    int t1 = s.indexOf('\t', t0 + 1);
    int t2 = s.indexOf('\t', t1 + 1);
    String m = s.substring(t1 + 1, t2);
    String[] f = s.substring(t2 + 1).split("\t", -1);
    Object[] h = (Object[]) hdrs.get(m);
    String key = f[4];
    int bk = key.indexOf('[');
    String base = bk > 0 ? key.substring(0, bk) : key;
    boolean undo = "ok".equals(f[7]) && !f[6].equals("(action)") && rowIdx(h, base) >= 0 && canEdit(hs(h, 4));
    String rsel = "#SkyyAdmGRow" + r;
    b.appendInline("#SkyyAdmGRows", "Group #SkyyAdmGRow" + r + @MD@.UI_AGROWB[sz]);
    b.appendInline(rsel, spc(14, 40));
    b.appendInline(rsel, @MD@.UI_AGTXTA + r + @MD@.UI_AGTXTB);
    b.set("#SkyyAdmGTxt" + r + ".Text", @MU@.clip(logText(h, m, f), 110));
    b.appendInline(rsel, spc(10, 40));
    if (undo) { b.appendInline(rsel, btn("SkyyAdmGUndo" + r, 120, 40, "Undo", @MD@.ADM_BS)); bind(ev, "SkyyAdmGUndo" + r, "lundo" + r); }
    b.appendInline("#SkyyAdmGRows", @MD@.UI_AGAP6);
    if (undo) this.logShown.add(new String[] { m, key, f[5], f[6] }); else this.logShown.add((Object) null);
  }
  if (all.isEmpty()) {
    b.appendInline("#SkyyAdmGRows", @MD@.UI_AEMPTY);
    b.set("#SkyyAdmEmpty.Text", "No changes logged yet.");
  }
  fReset();
  foot("Refresh", "arefresh", 130);
  // 0.3.35: the view crumbs lead away (sub-tab row; was a footer button, site 3)
  foot("Close", "aclose", 120);
  tail(b, ev);
}""")
# ---- view hist (spec 2.9): versions per file, preview + restore of one file
M(apg, r"""
public static String baseName(String f) {
  String s = f.trim();
  int sl = s.lastIndexOf('/');
  if (sl >= 0) s = s.substring(sl + 1);
  int dot = s.lastIndexOf('.');
  if (dot > 0) s = s.substring(0, dot);
  return s;
}""")
M(apg, r"""
public void drawHist(@UCB@ b, @UEB@ ev) {
  Object[] h = hdr(this.mod);
  if (h == null) { this.view = "list"; drawList(b, ev); return; }
  evReset();
  String[] fs = hs(h, 8).split(",");
  for (int i = 0; i < fs.length; i++) fs[i] = fs[i].trim();
  this.histFiles = fs;
  Object o = null;
  if (contractOk(h) && alive(this.mod)) o = call(this.mod, new Object[] { "versions" });
  String[] vs = o instanceof String[] ? (String[]) o : new String[0];
  java.util.ArrayList lines = new java.util.ArrayList();
  for (int i = 0; i < vs.length; i++) {
    String[] f = vs[i].split("\t", -1);
    if (f.length < 5) continue;
    if (this.histFile.length() > 0 && !this.histFile.equals(f[1])) continue;
    lines.add(f);
  }
  boolean prev = this.histPreview != null;
  int per = lines.size();                                // 0.3.36: one scroll list (no pages)
  this.histPage = 0;
  boolean edit = canEdit(hs(h, 4));
  frame(b, "History - " + hs(h, 2) + " (" + this.mod + ")", "Each config file keeps its newest versions. Preview one, then Restore it - a restore can be undone the same way.");
  if (fs.length > 1) {                                   // 0.3.36: the in-page picker (no tab row)
    int fi = 0;
    for (int i = 0; i < fs.length; i++) if (fs[i].equals(this.histFile)) fi = i + 1;
    picker(b, ev, "Show the versions of", (fi == 0 ? "All files" : baseName(this.histFile)) + "  (" + (fi + 1) + " of " + (fs.length + 1) + ")", "hfprev", "hfnext");
  }
  b.appendInline("#SkyyAdmBody", @MD@.UI_AHEAD);
  b.set("#SkyyAdmHead.Text", (this.histFile.length() == 0 ? "Every file" : this.histFile) + "   -   " + lines.size() + (lines.size() == 1 ? " version" : " versions")
      );
  b.appendInline("#SkyyAdmBody", prev ? @MD@.UI_AHROWSP : @MD@.UI_AHROWS);
  this.histIds = new String[per];
  int sz = @PKG@.HubBar.growSize(per, prev ? @MD@.ADM_IN_HISTPREV : @MD@.ADM_IN_HIST, @MD@.ADM_RH_H, 6);
  for (int r = 0; r < per; r++) {
    String[] f = (String[]) lines.get(r);
    this.histIds[r] = f[0];
    String when = f[2].length() >= 16 ? f[2].substring(0, 16) : f[2];
    String rsel = "#SkyyAdmHRow" + r;
    b.appendInline("#SkyyAdmHRows", "Group #SkyyAdmHRow" + r + @MD@.UI_AHROWB[sz]);
    b.appendInline(rsel, spc(14, 44));
    b.appendInline(rsel, @MD@.UI_AHTXTA + r + @MD@.UI_AHTXTB);
    b.set("#SkyyAdmHTxt" + r + ".Text", @MU@.clip(f[1] + "  -  " + when + "  -  " + f[4], 96));
    b.appendInline(rsel, spc(10, 44));
    b.appendInline(rsel, btn("SkyyAdmHPrev" + r, 120, 44, "Preview", @MD@.ADM_BS));
    bind(ev, "SkyyAdmHPrev" + r, "hprev" + r);
    b.appendInline(rsel, spc(6, 44));
    if (edit) { b.appendInline(rsel, btn("SkyyAdmHRes" + r, 120, 44, "Restore", @MD@.ADM_BS)); bind(ev, "SkyyAdmHRes" + r, "hres" + r); }
    b.appendInline("#SkyyAdmHRows", @MD@.UI_AGAP6);
  }
  if (lines.isEmpty()) {
    b.appendInline("#SkyyAdmHRows", @MD@.UI_AEMPTY);
    b.set("#SkyyAdmEmpty.Text", "No versions yet - a copy is kept the first time a file is changed.");
  }
  if (prev) preview(b, "Preview - what Restore would change:", this.histPreview);
  fReset();
  foot("Refresh", "arefresh", 130);
  // 0.3.35: the view crumbs lead away (sub-tab row; was a footer button, history)
  foot("Close", "aclose", 120);
  tail(b, ev);
}""")
# ---- view io (spec 2.10): export code + file, import code / file with preview; one mod, or every set-up mod from the list
M(apg, r"""
public void drawIo(@UCB@ b, @UEB@ ev) {
  evReset();
  evField("Imp", "SkyyAdmImp");
  Object[] h = null;
  if (!this.ioAll) h = hdr(this.mod);
  String title = this.ioAll ? "Export / Import - every mod" : "Export / Import - " + (h == null ? String.valueOf(this.mod) : hs(h, 2) + " (" + this.mod + ")");
  frame(b, title, "A code copies this setup to another world. It never holds player data.");
  b.appendInline("#SkyyAdmBody", @MD@.UI_AIOL1);
  b.set("#SkyyAdmIoL1.Text", "Export - " + ("all".equals(this.ioScope) ? "every value" : "only the values that differ from the default") + ". Select the code and copy it, or use the file in Skyy_SkyyMenu/exports.");
  b.appendInline("#SkyyAdmBody", @MD@.UI_AIOR1);
  String code = this.ioCode == null ? "" : this.ioCode;
  if (code.length() > 4000) code = "(too long for this box - use the file in Skyy_SkyyMenu/exports)";
  field(b, "#SkyyAdmIoR1", "SkyyAdmExp", 830, 50, 4000, code, "");
  b.appendInline("#SkyyAdmIoR1", spc(10, 50));
  b.appendInline("#SkyyAdmIoR1", btn("SkyyAdmScope", 200, 50, "all".equals(this.ioScope) ? "Changed only" : "Everything", @MD@.ADM_BS));
  bind(ev, "SkyyAdmScope", "iscope");
  b.appendInline("#SkyyAdmBody", @MD@.UI_AGAP12);
  b.appendInline("#SkyyAdmBody", @MD@.UI_AIOL2);
  b.set("#SkyyAdmIoL2.Text", this.ioAll ? "Import - paste one or more codes, click Preview (mod by mod), then Apply." : "Import - paste a code and click Preview, then Apply.");
  b.appendInline("#SkyyAdmBody", @MD@.UI_AIOR2);
  String imp = this.ioImport == null ? "" : this.ioImport;
  if (imp.length() > 4000) imp = "(from file - too long for this box)";
  field(b, "#SkyyAdmIoR2", "SkyyAdmImp", 780, 50, 4000, imp, "paste a code");
  bindEnter(ev, "SkyyAdmImp", "iprev");
  b.appendInline("#SkyyAdmIoR2", spc(10, 50));
  b.appendInline("#SkyyAdmIoR2", btn("SkyyAdmIPrev", 130, 50, "Preview", @MD@.ADM_BS));
  bind(ev, "SkyyAdmIPrev", "iprev");
  b.appendInline("#SkyyAdmIoR2", spc(10, 50));
  b.appendInline("#SkyyAdmIoR2", btn("SkyyAdmIApply", 130, 50, "Apply", @MD@.ADM_BS));
  bind(ev, "SkyyAdmIApply", "iapply");
  preview(b, this.ioPreview == null ? "Preview - paste a code or pick a file, then click Preview." : "Preview:", this.ioPreview == null ? "" : this.ioPreview);
  String[] files = @PKG@.AdmSaveTask.importFiles();
  this.ioFiles = files;
  b.appendInline("#SkyyAdmBody", @MD@.UI_AIOF);
  b.set("#SkyyAdmIoF.Text", files.length == 0 ? "Files in Skyy_SkyyMenu/imports: none yet - put .txt files with codes there to see them here."
      : "Files in Skyy_SkyyMenu/imports (" + files.length + ")" + (files.length > @MD@.ADM_FMAX ? " - the first " + @MD@.ADM_FMAX + " by name:" : ":"));
  b.appendInline("#SkyyAdmBody", @MD@.UI_AIOFROWS);    // 0.3.36: one scroll list (every file)
  for (int r = 0; r < files.length && r < @MD@.ADM_FMAX; r++) {
    b.appendInline("#SkyyAdmIoFRows", @MD@.UI_AFROWA + r + @MD@.UI_AFROWB);
    b.appendInline("#SkyyAdmFRow" + r, spc(14, 42));
    b.appendInline("#SkyyAdmFRow" + r, @MD@.UI_AFTXTA + r + @MD@.UI_AFTXTB);
    b.set("#SkyyAdmFTxt" + r + ".Text", files[r]);
    b.appendInline("#SkyyAdmFRow" + r, spc(10, 42));
    b.appendInline("#SkyyAdmFRow" + r, btn("SkyyAdmFPrev" + r, 130, 42, "Preview", @MD@.ADM_BS));
    bind(ev, "SkyyAdmFPrev" + r, "ifile" + r);
    b.appendInline("#SkyyAdmIoFRows", @MD@.UI_AGAP6);
  }
  fReset();
  // 0.3.35: the view crumbs lead away (sub-tab row; was a footer button, site 4)
  foot("Close", "aclose", 150);
  tail(b, ev);
}""")

# the two AdminPage methods the guard-order check reads (compiled below with M(apg, ADM_BUILD) / M(apg, ADM_HDE))
ADM_BUILD = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  if (!guard()) { drawLocked(b, ev); return; }
  try {
    String v = this.view == null ? "list" : this.view;
    if (v.equals("mod")) drawMod(b, ev);
    else if (v.equals("table")) drawTable(b, ev);
    else if (v.equals("confirm")) drawConfirm(b, ev);
    else if (v.equals("log")) drawLog(b, ev);
    else if (v.equals("hist")) drawHist(b, ev);
    else if (v.equals("io")) drawIo(b, ev);
    else { this.view = "list"; drawList(b, ev); }
  } catch (Throwable t) { @MU@.warn("server setup view " + this.view + " failed: " + t); }
}"""
ADM_HDE = r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (!guard()) { lockedClick(ref, st, data); return; }
    if (data == null) return;
    String hr = @PKG@.MenuHub.click(this.playerRef, data, "settings", "setup");   // 0.3.28: the hub bar (after the guard)
    if (hr != null) { hubAfter(ref, st, hr); return; }
    String a = @MU@.jstr(data, "a", 40);
    if (a.length() == 0) return;
    captureDrafts(data);
    if (a.equals("aclose")) { this.drafts = new java.util.HashMap(); closeNow(ref, st); return; }
    if (a.equals("amenu")) { openMenu(ref, st); return; }
    if (this.view.equals("confirm")) { clickConfirm(a); rebuild(); return; }
    if (!clickView(ref, st, a)) rebuild();
  } catch (Throwable t) { @MU@.warn("server setup click failed: " + t); }
}"""
# ================= 0.3 guard order (research/Server-Setup-Spec.md 2.3, 2.12, 8.1.4): the ONE permission gate comes first =================
def adm_guard_ok(build_src, hde_src):
    """build(): guard() is the first statement. handleDataEvent(): only 'try {' before guard(), and guard() before the first read or
    comparison of the action (so a button added later cannot skip the check)."""
    b = build_src.strip()
    if not b[b.index("{") + 1:].lstrip().startswith("if (!guard())"):
        return False
    g = hde_src.find("if (!guard())")
    if g < 0:
        return False
    marks = [hde_src.find(p) for p in ('jstr(data, "a"', '.equals("a', 'startsWith("a', 'indexOf("\\"a', "captureDrafts(", "clickView(")]
    marks = [x for x in marks if x >= 0]
    if not marks or g > min(marks):
        return False
    return hde_src[hde_src.index("{") + 1:g].strip() in ("", "try {")
assert adm_guard_ok(ADM_BUILD, ADM_HDE), "AdminPage: guard() must be the first statement of build() and come before any action handling"
_bad_hde = ADM_HDE.replace("    if (!guard())", '    if (@MU@.jstr(data, "a", 40).equals("aclose")) return;' + "\n" + "    if (!guard())", 1)
_bad_build = ADM_BUILD.replace("  if (!guard())", "  evReset();\n  if (!guard())", 1)
assert _bad_hde != ADM_HDE and not adm_guard_ok(ADM_BUILD, _bad_hde), "the guard-order check must refuse a handler branch before guard()"
assert _bad_build != ADM_BUILD and not adm_guard_ok(_bad_build, ADM_HDE), "the guard-order check must refuse a statement before guard() in build()"
print("server setup guard order: ok (and the crafted bad sources are refused)")

# ---- clicks: results, drafts, one handler per view
M(apg, r"""
public void handleResult(String m, Object r, Object[] args, int ci, String draftKey) {
  if (r == null) { setStatus(@MD@.ADM_NOANSWER, 3); return; }
  String s = rStatus(r);
  String msg = rMsg(r);
  if (s == null) { setStatus(@MD@.ADM_NOANSWER, 3); return; }
  if (s.equals("confirm")) {
    if (ci < 0 || args == null) { setStatus(msg, 2); return; }
    Object[] again = new Object[args.length];
    System.arraycopy(args, 0, again, 0, args.length);
    again[ci] = "yes";
    this.pending = again;
    this.pendingMod = m;
    this.pendingKind = 0;
    this.pendingMsg = msg;
    this.backView = this.view;
    this.view = "confirm";
    return;
  }
  if (s.equals("ok") || s.equals("restart")) {
    setStatus(firstLine(msg), s.equals("ok") ? 1 : 2);
    if (draftKey != null) this.drafts.remove(draftKey);
    return;
  }
  setStatus(firstLine(msg.length() > 0 ? msg : "Not changed."), 3);
}""")
M(apg, r"""
public void doSet(String key, String value) {
  Object[] a = new Object[] { "set", key, value, me(), myName(), "", "menu" };
  handleResult(this.mod, call(this.mod, a), a, 5, key);
}""")
M(apg, r"""
public void ask(String m, Object[] args, String msg) {
  this.pending = args;
  this.pendingMod = m;
  this.pendingKind = 0;
  this.pendingMsg = msg;
  this.backView = this.view;
  this.view = "confirm";
}""")
M(apg, r"""
public boolean ready(Object[] h) {
  if (h == null) { setStatus(this.mod + " has no in-game settings.", 3); return false; }
  if (!contractOk(h)) { setStatus(@MD@.ADM_NEWER, 3); return false; }
  if (!alive(this.mod)) { setStatus(this.mod + " is not running - its settings cannot be changed now.", 3); return false; }
  return true;
}""")
M(apg, r"""
public void clearEntryDrafts(String e) {
  for (int c = 0; c < 4; c++) this.tDrafts.remove(e + "\t" + c);
}""")
M(apg, r"""
public void captureDrafts(String data) {
  String v = this.view;
  if (v.equals("mod")) {
    for (int r = 0; r < this.rowKeys.length; r++) {
      String k = this.rowKeys[r];
      String j = at("V" + r);
      if (k == null || data.indexOf("\"" + j + "\"") < 0) continue;
      String t = @MU@.jstr(data, j, 2000);
      if (t.trim().length() > 0) this.drafts.put(k, t); else this.drafts.remove(k);
    }
  } else if (v.equals("table")) {
    if (data.indexOf("\"" + at("TF") + "\"") >= 0) this.tFilterDraft = @MU@.jstr(data, at("TF"), 80);
    for (int r = 0; r < this.tKeys.length; r++) {
      String e = this.tKeys[r];
      if (e == null) continue;
      for (int c = 0; c < 3; c++) {
        String j = at("C" + r + "x" + c);
        if (data.indexOf("\"" + j + "\"") >= 0) this.tDrafts.put(e + "\t" + c, @MU@.jstr(data, j, 200));
      }
    }
    if (data.indexOf("\"" + at("AK") + "\"") >= 0) this.tAdd[0] = @MU@.jstr(data, at("AK"), 120);
    for (int c = 0; c < 3; c++) if (data.indexOf("\"" + at("A" + c) + "\"") >= 0) this.tAdd[c + 1] = @MU@.jstr(data, at("A" + c), 200);
  } else if (v.equals("list")) {
    if (data.indexOf("\"" + at("Find") + "\"") >= 0) this.findDraft = @MU@.jstr(data, at("Find"), 60);
  } else if (v.equals("io")) {
    if (data.indexOf("\"" + at("Imp") + "\"") >= 0) {
      String t = @MU@.jstr(data, at("Imp"), 400000);
      if (!t.startsWith("(from file")) this.ioImport = t;
    }
  }
}""")
M(apg, r"""
public void lockedClick(@REF@ ref, @ST@ st, String data) {
  String hr = @PKG@.MenuHub.click(this.playerRef, data, "settings", "setup");   // 0.3.28: the hub bar works on the locked page too
  if (hr != null) { hubAfter(ref, st, hr); return; }
  if (data != null && "aclose".equals(@MU@.jstr(data, "a", 40))) { closeNow(ref, st); return; }
  rebuild();
}""")
M(apg, r"""
public void turn(int d) {
  String v = this.view;
  if (v.equals("list")) this.listPage = this.listPage + d;
  else if (v.equals("mod")) this.modPage = this.modPage + d;
  else if (v.equals("table")) this.tPage = this.tPage + d;
  else if (v.equals("log")) this.logPage = this.logPage + d;
  else if (v.equals("hist")) this.histPage = this.histPage + d;
}""")
M(apg, r"""
public void toList() {
  this.view = "list";
  this.drafts = new java.util.HashMap();
  this.tDrafts = new java.util.HashMap();
  this.pending = null;
}""")
M(apg, r"""
public void computeExport() {
  if (this.ioAll) {
    StringBuilder box = new StringBuilder();
    StringBuilder fl = new StringBuilder();
    StringBuilder bad = new StringBuilder();
    int n = 0;
    String[] cm = cfgMods();
    for (int i = 0; i < cm.length; i++) {
      Object[] h = hdr(cm[i]);
      if (h == null || !contractOk(h) || !alive(cm[i])) continue;
      Object o = call(cm[i], new Object[] { "export", this.ioScope });
      if (o instanceof String) {
        if (box.length() > 0) box.append(' ');
        box.append((String) o);
        fl.append((String) o).append('\n');
        n++;
      } else { if (bad.length() > 0) bad.append(", "); bad.append(cm[i]); }
    }
    this.ioCode = box.toString();
    String name = "all-" + stamp() + ".txt";
    if (n > 0) saveFile("exports/" + name, "# SkyWynn setup codes (one per mod), exported " + stamp() + " by " + myName() + ". Import them in Server Setup - Export all.\n" + fl.toString());
    setStatus(n + " mod code(s)" + (n > 0 ? " - a copy is saved to Skyy_SkyyMenu/exports/" + name : "") + (bad.length() > 0 ? " - not exported (a file cannot be read): " + bad.toString() : ""), bad.length() > 0 ? 2 : 1);
    return;
  }
  Object o = call(this.mod, new Object[] { "export", this.ioScope });
  if (!(o instanceof String)) { this.ioCode = ""; setStatus("Cannot export " + this.mod + " while one of its files cannot be read.", 3); return; }
  this.ioCode = (String) o;
  String name = this.mod + "-" + stamp() + ".txt";
  saveFile("exports/" + name, "# SkyWynn setup code for " + this.mod + ", exported " + stamp() + " by " + myName() + ". Import it in Server Setup - Export / Import.\n" + this.ioCode + "\n");
  setStatus("Code ready - a copy is saved to Skyy_SkyyMenu/exports/" + name + (this.ioCode.length() > 4000 ? " (too long for the box - use the file)" : ""), 1);
}""")
M(apg, r"""
public String modFor(String code) {
  String m = codeMod(code);
  Object[] h = hdr(m);
  if (h != null && contractOk(h) && alive(m)) return m;
  String[] cm = cfgMods();
  for (int i = 0; i < cm.length; i++) {
    Object[] hh = hdr(cm[i]);
    if (hh == null || !contractOk(hh) || !alive(cm[i])) continue;
    Object r = call(cm[i], new Object[] { "import", code, me(), myName(), "preview" });
    String s = rStatus(r);
    if (s == null) continue;
    if ("bad".equals(s) && rMsg(r).startsWith("This code is for")) continue;
    return cm[i];
  }
  return null;
}""")
M(apg, r"""
public void importPreview() {
  java.util.ArrayList cs = codesIn(this.ioImport);
  this.ioPreviewCode = null;
  this.ioPlan = new java.util.ArrayList();
  this.ioPlanTotal = 0;
  if (cs.isEmpty()) { this.ioPreview = null; setStatus("Paste a code that starts with SKYY1. first.", 3); return; }
  if (!this.ioAll) {
    String code = (String) cs.get(0);
    for (int i = 0; i < cs.size(); i++) if (codeMod((String) cs.get(i)).equals(this.mod)) { code = (String) cs.get(i); break; }
    Object r = call(this.mod, new Object[] { "import", code, me(), myName(), "preview" });
    String s = rStatus(r);
    this.ioPreview = r == null ? null : rMsg(r);
    if ("ok".equals(s)) {
      int n = 0;
      try { n = Integer.parseInt(rVal(r)); } catch (Throwable t) { n = 0; }
      this.ioPreviewCode = n > 0 ? code : null;
      setStatus(n > 0 ? n + " change(s) - click Apply to import them." : firstLine(rMsg(r)), n > 0 ? 0 : 1);
    } else setStatus(r == null ? @MD@.ADM_NOANSWER : firstLine(rMsg(r)), 3);
    return;
  }
  StringBuilder pv = new StringBuilder();
  for (int i = 0; i < cs.size(); i++) {
    String code = (String) cs.get(i);
    String m = modFor(code);
    if (m == null) { pv.append(codeMod(code)).append(": no mod on this server takes this code\n"); continue; }
    Object r = call(m, new Object[] { "import", code, me(), myName(), "preview" });
    String s = rStatus(r);
    String[] ls = rMsg(r).split("\n");
    pv.append(m).append(": ").append(ls.length > 0 ? ls[0] : "").append('\n');
    for (int k = 1; k < ls.length && k < 4; k++) pv.append("    ").append(ls[k]).append('\n');
    if ("ok".equals(s)) {
      int n = 0;
      try { n = Integer.parseInt(rVal(r)); } catch (Throwable t) { n = 0; }
      if (n > 0) { this.ioPlan.add(new String[] { m, code }); this.ioPlanTotal = this.ioPlanTotal + n; }
    }
  }
  this.ioPreview = pv.toString();
  setStatus(this.ioPlan.isEmpty() ? "Nothing to import." : this.ioPlanTotal + " change(s) in " + this.ioPlan.size() + " mod(s) - click Apply to import them.", this.ioPlan.isEmpty() ? 2 : 0);
}""")
M(apg, r"""
public void importApply() {
  if (this.ioAll) {
    if (this.ioPlan == null || this.ioPlan.isEmpty()) { setStatus("Click Preview first - there is nothing to import yet.", 2); return; }
    this.pendingKind = 1;
    this.pendingCodes = this.ioPlan;
    this.pendingMod = null;
    this.pending = null;
    this.pendingMsg = "Import " + this.ioPlanTotal + " change(s) into " + this.ioPlan.size() + " mod(s)? Each mod saves a version first, so History can undo it.\n" + (this.ioPreview == null ? "" : this.ioPreview);
    this.backView = "io";
    this.view = "confirm";
    return;
  }
  if (this.ioPreviewCode == null) { setStatus("Click Preview first - there is nothing to import yet.", 2); return; }
  if (!codesIn(this.ioImport).contains(this.ioPreviewCode)) { setStatus("The code changed - click Preview again.", 2); return; }
  ask(this.mod, new Object[] { "import", this.ioPreviewCode, me(), myName(), "apply" },
      "Import these changes into " + this.mod + "? It saves a version of each file first, so History can undo it.\n" + (this.ioPreview == null ? "" : this.ioPreview));
}""")
M(apg, r"""
public void clickConfirm(String a) {
  String back = this.backView == null ? "list" : this.backView;
  this.view = back;
  if (!a.equals("ayes")) {
    this.pending = null;
    this.pendingCodes = null;
    setStatus(@MD@.ADM_CANCEL, 0);
    return;
  }
  if (this.pendingKind == 1 && this.pendingCodes != null) {
    int ok = 0;
    StringBuilder bad = new StringBuilder();
    StringBuilder all = new StringBuilder();
    for (int k = 0; k < this.pendingCodes.size(); k++) {
      String[] e = (String[]) this.pendingCodes.get(k);
      Object r = call(e[0], new Object[] { "import", e[1], me(), myName(), "apply" });
      String s = rStatus(r);
      all.append(e[0]).append(": ").append(r == null ? "no answer" : firstLine(rMsg(r))).append('\n');
      if ("ok".equals(s) || "restart".equals(s)) ok++;
      else { if (bad.length() > 0) bad.append(", "); bad.append(e[0]); }
    }
    this.ioPreview = all.toString();
    this.ioPlan = new java.util.ArrayList();
    setStatus(bad.length() == 0 ? "Imported into " + ok + " mod(s)." : "Imported into " + ok + " mod(s) - problems with " + bad.toString() + " (see below).", bad.length() == 0 ? 1 : 3);
  } else if (this.pending != null) {
    Object[] args = this.pending;
    String m = this.pendingMod;
    Object[] h = hdr(m);
    if (h == null || !contractOk(h) || !alive(m)) setStatus(m + " is not running - nothing was changed.", 3);
    else {
      Object r = call(m, args);
      handleResult(m, r, args, -1, null);
      String op = String.valueOf(args[0]);
      String s = rStatus(r);
      boolean done = "ok".equals(s) || "restart".equals(s);
      if (op.equals("import") && r != null) { this.ioPreview = rMsg(r); if (done) this.ioPreviewCode = null; }
      if (op.equals("restore") && r != null) this.histPreview = rMsg(r);
      if (op.equals("set") && done) this.drafts.remove(String.valueOf(args[1]));
      if ((op.equals("tset") || op.equals("add")) && done) clearEntryDrafts(String.valueOf(args[2]));
    }
  }
  this.pending = null;
  this.pendingCodes = null;
}""")
M(apg, r"""
public void clickList(String a) {
  if (a.equals("afind")) {
    String q = this.findDraft == null ? "" : this.findDraft.trim();
    if (q.length() == 1) { setStatus("Type at least 2 letters to search.", 2); return; }
    this.search = q;
    this.listPage = 0;
    return;
  }
  if (a.equals("aclear")) { this.search = ""; this.findDraft = ""; this.listPage = 0; return; }
  if (a.equals("achanges")) { this.view = "log"; this.logMod = ""; this.logPage = 0; return; }
  if (a.equals("aexpall")) {
    this.view = "io"; this.ioAll = true; this.ioScope = "changed"; this.ioPreview = null; this.ioPreviewCode = null; this.ioPlan = new java.util.ArrayList();
    computeExport();
    return;
  }
  int r = tailNum(a, "aopen");
  if (r >= 0 && r < this.listMods.length && this.listMods[r] != null) {
    String m = this.listMods[r];
    Object[] h = hdr(m);
    if (h != null && !contractOk(h)) { setStatus(m + ": " + @MD@.ADM_NEWER, 3); return; }
    if (h != null && !alive(m)) { setStatus(m + " is not running - its settings cannot be changed now.", 3); return; }
    this.mod = m;
    this.view = "mod";
    this.cat = 0;
    this.modPage = 0;
    this.showAdv = false;
    this.drafts = new java.util.HashMap();
    this.jumpHit = h != null && this.search != null && this.search.trim().length() >= 2;
    // 0.3.25: a search result goes to exactly its tab / setting
    String j = this.listJump != null && r < this.listJump.length ? this.listJump[r] : null;
    int jn = j != null && j.length() > 1 ? tailNum(j, j.substring(0, 1)) : -1;
    if (h != null && jn >= 0 && j.startsWith("c")) { this.jumpHit = false; this.cat = jn; }
    if (h != null && jn >= 0 && j.startsWith("r")) { this.jumpHit = false; this.jumpRow = jn; }
    return;
  }
  r = tailNum(a, "arel");
  if (r >= 0 && r < this.listReload.length && this.listReload[r] != null && this.listReload[r].length() > 0) {
    String rl = this.listReload[r];
    if (runLine(rl)) setStatus("Ran /" + rl + " - the answer is in your chat.", 1);
  }
}""")
M(apg, r"""
public boolean clickMod(@REF@ ref, @ST@ st, String a) {
  if (a.equals("afrel")) {
    int k = modIndex(this.mod);
    String rl = k >= 0 ? @MD@.MOD_RELOAD[k] : "";
    if (rl.length() > 0 && runLine(rl)) setStatus("Ran /" + rl + " - the answer is in your chat.", 1);
    return false;
  }
  Object[] h = hdr(this.mod);
  if (h == null) return false;
  if (a.equals("cfprev") || a.equals("cfnext")) {         // 0.3.36: the category picker (more categories than the sub row holds)
    int nc = catIds(h).length;
    if (nc > 0) this.cat = a.equals("cfnext") ? (this.cat + 1) % nc : (this.cat + nc - 1) % nc;
    return false;
  }
  int t = tailNum(a, "atab");
  if (t >= 0) { this.cat = t; this.modPage = 0; return false; }
  if (a.equals("aadv")) { this.showAdv = !this.showAdv; this.modPage = 0; return false; }
  if (!ready(h)) return false;
  if (a.equals("ahist")) { this.view = "hist"; this.histFile = ""; this.histPreview = null; this.histPage = 0; return false; }
  if (a.equals("aio")) {
    this.view = "io"; this.ioAll = false; this.ioScope = "changed"; this.ioPreview = null; this.ioPreviewCode = null;
    computeExport();
    return false;
  }
  if (a.equals("areload")) { handleResult(this.mod, call(this.mod, new Object[] { "reload", me(), myName(), "menu" }), null, -1, null); return false; }
  int r = -1;
  int j = -1;
  String verb = null;
  String[] verbs = new String[] { "aset", "adef", "aon", "aoff", "aminus", "aplus", "aedit", "alink", "aact", "acl", "acr" };
  for (int k = 0; k < verbs.length && verb == null; k++) { int n = tailNum(a, verbs[k]); if (n >= 0) { r = n; verb = verbs[k]; } }
  if (verb == null && a.startsWith("ach") && a.indexOf('x') > 3) {
    r = tailNum(a.substring(0, a.indexOf('x')), "ach");
    j = tailNum("x" + a.substring(a.indexOf('x') + 1), "x");
    if (r >= 0 && j >= 0) verb = "ach";
  }
  if (verb == null || r < 0 || r >= this.rowKeys.length || this.rowKeys[r] == null) return false;
  String key = this.rowKeys[r];
  Object[] w = rowAt(h, rowIdx(h, key));
  if (w == null) { setStatus("That setting is gone - the mod changed.", 3); return false; }
  String opts = rv(w, 7);
  if (verb.equals("aset")) {
    String v = (String) this.drafts.get(key);
    boolean typedSet = v != null;
    if (v == null) v = cur(this.mod, key);
    if (v == null || v.trim().length() == 0) { setStatus("Type a value first.", 2); return false; }
    if (typedSet) {
      String[] tv = typedValue(w, v);
      if (tv[0] == null) { setStatus(tv[1], 3); return false; }
      v = tv[0];
    }
    doSet(key, v);
  } else if (verb.equals("adef")) doSet(key, (String) null);
  else if (verb.equals("aon")) doSet(key, "true");
  else if (verb.equals("aoff")) doSet(key, "false");
  else if (verb.equals("ach")) { String[] vs = chVals(opts); if (j < vs.length) doSet(key, vs[j]); }
  else if (verb.equals("acl") || verb.equals("acr")) {
    String[] vs = chVals(opts);
    String c = cur(this.mod, key);
    int at0 = 0;
    for (int k = 0; k < vs.length; k++) if (vs[k].equals(c)) at0 = k;
    int nx = verb.equals("acr") ? (at0 + 1) % vs.length : (at0 + vs.length - 1) % vs.length;
    doSet(key, vs[nx]);
  } else if (verb.equals("aminus") || verb.equals("aplus")) {
    String c = (String) this.drafts.get(key);
    boolean typedNow = c != null;
    if (typedNow && msRow(w)) { String mc = msOf(c, !rv(w, 3).equals("dec")); c = mc == null ? "?" : mc; }
    if (c == null) c = cur(this.mod, key);
    if (c == null) { setStatus(@MD@.ADM_NOANSWER, 3); return false; }
    String step = stepOf(opts);
    if (step == null) { setStatus("That setting is gone - the mod changed.", 3); return false; }
    try {
      java.math.BigDecimal v = new java.math.BigDecimal(c.trim());
      java.math.BigDecimal sp = new java.math.BigDecimal(step);
      v = verb.equals("aplus") ? v.add(sp) : v.subtract(sp);
      String nv = v.signum() == 0 ? "0" : v.stripTrailingZeros().toPlainString();
      doSet(key, nv);
    } catch (Throwable x) { setStatus(typedNow ? "The value in the box is not a number - fix it or click Default." : "The current value is not a number - type one in the box.", 3); }
  } else if (verb.equals("aedit")) {
    this.view = "table";
    this.tableKey = key;
    this.tFilter = "";
    this.tFilterDraft = "";
    this.tPage = 0;
    this.tDrafts = new java.util.HashMap();
    this.tAdd = new String[4];
    if (rv(w, 3).equals("items")) this.items = csv(cur(this.mod, key));
  } else if (verb.equals("alink")) {
    if (runLine(opts)) setStatus("Ran /" + opts + " - if no page opens, the answer is in your chat.", 1);
  } else if (verb.equals("aact")) {
    Object[] args = new Object[] { "action", key, me(), myName(), "", "menu" };
    handleResult(this.mod, call(this.mod, args), args, 4, null);
  }
  return false;
}""")
M(apg, r"""
public String entryNow(String m, String tk, String e) {
  Object o = call(m, new Object[] { "keys", tk, e });
  if (!(o instanceof Object[]) || ((Object[]) o).length < 3 || !(((Object[]) o)[0] instanceof String[]) || !(((Object[]) o)[2] instanceof String[])) return null;
  String[] ks = (String[]) ((Object[]) o)[0];
  String[] vs = (String[]) ((Object[]) o)[2];
  for (int i = 0; i < ks.length; i++) if (ks[i].equals(e)) return i < vs.length ? vs[i] : "";
  return null;
}""")
M(apg, r"""
public void clickTable(@REF@ ref, @ST@ st, String a) {
  Object[] h = hdr(this.mod);
  Object[] w = rowAt(h, rowIdx(h, this.tableKey));
  if (w == null) { this.view = "mod"; return; }
  if (a.equals("tfind")) { this.tFilter = this.tFilterDraft == null ? "" : this.tFilterDraft.trim(); this.tPage = 0; return; }
  if (a.equals("tclear")) { this.tFilter = ""; this.tFilterDraft = ""; this.tPage = 0; return; }
  if (!ready(h)) return;
  boolean itemsMode = rv(w, 3).equals("items");
  String label = rv(w, 1);
  String opts = rv(w, 7);
  int nc = itemsMode ? (hasOpt(opts, "qty") ? 1 : 0) : tCols(opts).length;
  if (nc > 3) nc = 3;
  if (itemsMode) {
    boolean qty = nc > 0;
    int r = tailNum(a, "tset");
    if (r >= 0 && r < this.tKeys.length && this.tKeys[r] != null && qty) {
      String e = this.tKeys[r];
      String q = (String) this.tDrafts.get(e + "\t0");
      if (q == null) q = this.tVals[r];
      int n = -1;
      try { n = Integer.parseInt(q.trim()); } catch (Throwable x) { n = -1; }
      if (n < 1 || n > 9999) { setStatus("The amount must be a whole number from 1 to 9999.", 3); return; }
      for (int i = 0; i < this.items.size(); i++) {
        String it = String.valueOf(this.items.get(i));
        int c = it.lastIndexOf(':');
        if ((c > 0 ? it.substring(0, c) : it).equals(e)) this.items.set(i, e + ":" + n);
      }
      clearEntryDrafts(e);
      setStatus(e + " x" + n + " - click Save list to keep it.", 0);
      return;
    }
    r = tailNum(a, "trem");
    if (r >= 0 && r < this.tKeys.length && this.tKeys[r] != null) {
      String e = this.tKeys[r];
      for (int i = this.items.size() - 1; i >= 0; i--) {
        String it = String.valueOf(this.items.get(i));
        int c = it.lastIndexOf(':');
        if ((qty && c > 0 ? it.substring(0, c) : it).equals(e)) this.items.remove(i);
      }
      clearEntryDrafts(e);
      setStatus(e + " taken off the list - click Save list to keep it.", 0);
      return;
    }
    if (a.equals("tadd") || a.equals("theld")) {
      String id = a.equals("theld") ? heldItem(ref, st) : (this.tAdd[0] == null ? "" : this.tAdd[0].trim());
      if (id == null || id.length() == 0) { setStatus(a.equals("theld") ? "Hold the item in your hand first." : "Type an item id first.", 2); return; }
      for (int i = 0; i < this.items.size(); i++) {
        String it = String.valueOf(this.items.get(i));
        int c = it.lastIndexOf(':');
        if ((qty && c > 0 ? it.substring(0, c) : it).equals(id)) { setStatus(id + " is already on the list.", 2); return; }
      }
      String q = qty ? (this.tAdd[1] == null || this.tAdd[1].trim().length() == 0 ? "1" : this.tAdd[1].trim()) : null;
      this.items.add(qty ? id + ":" + q : id);
      this.tAdd = new String[4];
      setStatus(id + " added to the list - click Save list to keep it.", 0);
      return;
    }
    if (a.equals("tsave")) {
      doSet(this.tableKey, joinList(this.items, ","));
      if (this.statusKind == 1) this.items = csv(cur(this.mod, this.tableKey));
      return;
    }
    if (a.equals("tundo")) { this.items = csv(cur(this.mod, this.tableKey)); this.tDrafts = new java.util.HashMap(); setStatus("Back to the saved list.", 0); return; }
    return;
  }
  int r = tailNum(a, "tset");
  if (r >= 0 && r < this.tKeys.length && this.tKeys[r] != null) {
    String e = this.tKeys[r];
    String[] parts = this.tVals[r].split("\\|", -1);
    StringBuilder v = new StringBuilder();
    for (int c = 0; c < nc; c++) {
      String d = (String) this.tDrafts.get(e + "\t" + c);
      if (d == null) d = c < parts.length ? parts[c] : "";
      if (c > 0) v.append('|');
      v.append(d.trim());
    }
    Object[] args = new Object[] { "tset", this.tableKey, e, v.toString(), me(), myName(), "", "menu" };
    handleResult(this.mod, call(this.mod, args), args, 6, null);
    if (this.statusKind == 1) clearEntryDrafts(e);
    return;
  }
  r = tailNum(a, "trem");
  if (r >= 0 && r < this.tKeys.length && this.tKeys[r] != null) {
    String e = this.tKeys[r];
    ask(this.mod, new Object[] { "remove", this.tableKey, e, me(), myName(), "yes", "menu" }, "Remove " + e + " from " + label + "?");
    return;
  }
  if (a.equals("tadd") || a.equals("theld")) {
    String e = a.equals("theld") ? heldItem(ref, st) : (this.tAdd[0] == null ? "" : this.tAdd[0].trim());
    if (e == null || e.length() == 0) { setStatus(a.equals("theld") ? "Hold the item in your hand first." : "Type the new entry first.", 2); return; }
    StringBuilder v = new StringBuilder();
    for (int c = 0; c < nc; c++) { if (c > 0) v.append('|'); v.append(this.tAdd[c + 1] == null ? "" : this.tAdd[c + 1].trim()); }
    Object[] args = new Object[] { "add", this.tableKey, e, v.toString(), me(), myName(), "", "menu" };
    handleResult(this.mod, call(this.mod, args), args, 6, null);
    if (this.statusKind == 1) this.tAdd = new String[4];
  }
}""")
M(apg, r"""
public void clickLog(String a) {
  if (a.equals("lfprev") || a.equals("lfnext")) {         // 0.3.36: the mod picker (All mods, then every mod with changes)
    int nt = this.logTabs == null ? 0 : this.logTabs.length;
    if (nt > 0) {
      int at0 = 0;
      for (int k = 0; k < nt; k++) if (this.logTabs[k].equals(this.logMod)) at0 = k;
      this.logMod = this.logTabs[a.equals("lfnext") ? (at0 + 1) % nt : (at0 + nt - 1) % nt];
    }
    this.logPage = 0;
    return;
  }
  int r = tailNum(a, "lundo");
  if (r < 0 || r >= this.logShown.size() || this.logShown.get(r) == null) return;
  String[] e = (String[]) this.logShown.get(r);
  String m = e[0];
  String key = e[1];
  String old = e[2];
  String nw = e[3];
  Object[] h = hdr(m);
  if (h == null || !contractOk(h) || !alive(m)) { setStatus(m + " is not running - nothing was changed.", 3); return; }
  int bk = key.indexOf('[');
  if (bk > 0 && key.endsWith("]")) {
    String tk = key.substring(0, bk);
    String en = key.substring(bk + 1, key.length() - 1);
    Object[] w = rowAt(h, rowIdx(h, tk));
    String lbl = w == null ? tk : rv(w, 1);
    String now = entryNow(m, tk, en);
    boolean same = nw.equals("(none)") ? now == null : nw.equals(now);
    if (!same) { setStatus(@MD@.ADM_CHANGED, 3); return; }
    if (old.equals("(none)")) ask(m, new Object[] { "remove", tk, en, me(), myName(), "yes", "undo" }, "Undo: take " + en + " out of " + lbl + " again?");
    else if (nw.equals("(none)")) ask(m, new Object[] { "add", tk, en, old, me(), myName(), "yes", "undo" }, "Undo: put " + en + " back into " + lbl + " (" + old.replace("|", " / ") + ")?");
    else ask(m, new Object[] { "tset", tk, en, old, me(), myName(), "yes", "undo" }, "Undo: put " + en + " in " + lbl + " back from " + nw.replace("|", " / ") + " to " + old.replace("|", " / ") + "?");
    return;
  }
  Object[] w = rowAt(h, rowIdx(h, key));
  String now = cur(m, key);
  if (now == null || !now.equals(nw)) { setStatus(@MD@.ADM_CHANGED, 3); return; }
  String lbl = w == null ? key : rv(w, 1);
  ask(m, new Object[] { "set", key, old, me(), myName(), "yes", "undo" }, "Undo: put " + lbl + " back from " + disp(w, nw) + " to " + disp(w, old) + "?");
}""")
M(apg, r"""
public void clickHist(String a) {
  if (a.equals("hfprev") || a.equals("hfnext")) {         // 0.3.36: the file picker (All files, then each file)
    int nf = this.histFiles == null ? 0 : this.histFiles.length;
    int at0 = 0;
    for (int k = 0; k < nf; k++) if (this.histFiles[k].equals(this.histFile)) at0 = k + 1;
    int m = nf + 1;
    int nx = a.equals("hfnext") ? (at0 + 1) % m : (at0 + m - 1) % m;
    this.histFile = nx == 0 ? "" : this.histFiles[nx - 1];
    this.histPage = 0;
    this.histPreview = null;
    return;
  }
  Object[] h = hdr(this.mod);
  if (!ready(h)) return;
  int r = tailNum(a, "hprev");
  if (r >= 0 && r < this.histIds.length && this.histIds[r] != null) {
    Object res = call(this.mod, new Object[] { "restore", this.histIds[r], me(), myName(), "preview" });
    if (res == null) { setStatus(@MD@.ADM_NOANSWER, 3); return; }
    this.histPreview = rMsg(res);
    setStatus("ok".equals(rStatus(res)) ? "Preview below - Restore applies exactly this." : firstLine(rMsg(res)), "ok".equals(rStatus(res)) ? 0 : 3);
    return;
  }
  r = tailNum(a, "hres");
  if (r >= 0 && r < this.histIds.length && this.histIds[r] != null) {
    String id = this.histIds[r];
    String file = "";
    String when = "";
    Object o = call(this.mod, new Object[] { "versions" });
    String[] vs = o instanceof String[] ? (String[]) o : new String[0];
    for (int i = 0; i < vs.length; i++) {
      String[] f = vs[i].split("\t", -1);
      if (f.length >= 3 && f[0].equals(id)) { file = f[1]; when = f[2].length() >= 16 ? f[2].substring(0, 16) : f[2]; }
    }
    int others = this.histFiles.length - 1;
    ask(this.mod, new Object[] { "restore", id, me(), myName(), "apply" }, "Restore " + file + " to " + when + "?"
        + (others > 0 ? " " + this.mod + "'s other " + others + (others == 1 ? " file is" : " files are") + " not changed." : "") + " A version of the file is saved first, so this can be undone the same way.");
  }
}""")
M(apg, r"""
public void clickIo(String a) {
  if (!this.ioAll && !ready(hdr(this.mod))) return;
  if (a.equals("iscope")) { this.ioScope = "all".equals(this.ioScope) ? "changed" : "all"; computeExport(); return; }
  if (a.equals("iprev")) { importPreview(); return; }
  if (a.equals("iapply")) { importApply(); return; }
  int r = tailNum(a, "ifile");
  if (r >= 0 && r < this.ioFiles.length) {
    String t = @PKG@.AdmSaveTask.readImport(this.ioFiles[r]);
    if (t == null) { setStatus("Could not read imports/" + this.ioFiles[r] + " (1 MB at most).", 3); return; }
    this.ioImport = t;
    importPreview();
  }
}""")
# true = another page took over, so no rebuild (nothing returns true now: handleCommand runs the command later, on the common pool, so a
# link row cannot know here whether its command opens a page; it rebuilds with a status line like the Reload buttons and the main
# menu's page commands - the command's page, when it opens one, then replaces this page)
M(apg, r"""
public boolean clickView(@REF@ ref, @ST@ st, String a) {
  String v = this.view;
  setStatus("", 0);
  if (a.equals("aprev")) { turn(-1); return false; }
  if (a.equals("anext")) { turn(1); return false; }
  if (a.equals("arefresh")) return false;
  if (a.equals("amods")) { toList(); return false; }
  if (a.equals("aops")) { openOps(ref, st); return true; }
  if (a.equals("aback")) {
    if (v.equals("table") || v.equals("hist")) this.view = "mod";
    else if (v.equals("io")) this.view = this.ioAll ? "list" : "mod";
    else toList();
    return false;
  }
  if (v.equals("list")) { clickList(a); return false; }
  if (v.equals("mod")) return clickMod(ref, st, a);
  if (v.equals("table")) { clickTable(ref, st, a); return false; }
  if (v.equals("log")) { clickLog(a); return false; }
  if (v.equals("hist")) { clickHist(a); return false; }
  if (v.equals("io")) { clickIo(a); return false; }
  return false;
}""")
M(apg, ADM_BUILD)
M(apg, ADM_HDE)
# /modconfig [mod] opens the page (the command runs on the player's world thread; never close-then-open)
M(apg, r"""
public static void openFor(@PR@ pr, @ST@ store, @REF@ ref, String arg) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return;
    String m = arg == null ? null : resolveMod(arg);
    @PKG@.AdminPage pg = new @PKG@.AdminPage(pr, m == null ? "list" : "mod", m);
    if (arg != null && m == null) {
      String q = arg.trim();
      pg.search = q.length() >= 2 ? q : "";
      pg.findDraft = q;
      pg.setStatus("No mod called " + q + " on this server - here is what matches.", 2);
    }
    p.getPageManager().openCustomPage(ref, store, pg);
  } catch (Throwable t) {
    @MU@.warn("/modconfig failed: " + t);
    try { pr.sendMessage(@MSG@.raw("[Server Setup] Could not open Server Setup.")); } catch (Throwable t2) { }
  }
}""")

# ================= 0.3.23 OpsPage methods (the Admin page). Seams: rootCmd / can / pageOk / dispatch / online / now / liveVer / redraw /
# closeNow / openMenu / openSetup - the ONLY methods that touch the engine or another page; `test` (always null in game) lets the
# bare-JVM harness hand in real command objects, a model sender, online names and the clock. No timers, no periodic updates.
for _m in SUI.java_status_methods():
    M(ops, _m)
M(ops, r"""
public long now() {
  if (this.test != null && this.test.get("now") instanceof Long) return ((Long) this.test.get("now")).longValue();
  return System.currentTimeMillis();
}""")
M(ops, r"""
public @ACM@ rootCmd(String name) {
  if (name == null) return null;
  if (this.test != null) {
    Object o = this.test.get("cmd:" + name.toLowerCase());
    return o instanceof @ACM@ ? (@ACM@) o : null;
  }
  return @MU@.cmd(name);
}""")
M(ops, r"""
public boolean can(@ACM@ c) {
  if (c == null) return false;
  try {
    if (this.test != null) {
      Object s = this.test.get("sender");
      return s instanceof com.hypixel.hytale.server.core.command.system.CommandSender && c.hasPermission((com.hypixel.hytale.server.core.command.system.CommandSender) s);
    }
    return this.playerRef != null && c.hasPermission(this.playerRef);
  } catch (Throwable t) { return false; }
}""")
M(ops, r"""
public boolean pageOk() {
  if (this.test != null) return Boolean.TRUE.equals(this.test.get("page"));
  return @MU@.isAdmin(this.playerRef);
}""")
M(ops, r"""
public String liveVer(String mod) {
  if (this.test != null) { Object o = this.test.get("ver:" + mod); return o instanceof String ? (String) o : null; }
  return @MU@.liveVersion(mod);
}""")
M(ops, r"""
public String[] online() {
  if (this.test != null) { Object o = this.test.get("online"); return o instanceof String[] ? (String[]) o : new String[0]; }
  java.util.ArrayList rows = new java.util.ArrayList();
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p == null || !p.isValid()) continue;
      String n = p.getUsername();
      if (n == null || n.length() == 0) continue;
      rows.add(n.toLowerCase() + "\t" + n);
    }
  } catch (Throwable t) { }
  java.util.Collections.sort(rows);
  String[] out = new String[rows.size()];
  for (int i = 0; i < out.length; i++) { String r = (String) rows.get(i); out[i] = r.substring(r.indexOf('\t') + 1); }
  return out;
}""")
M(ops, r"""
public boolean dispatch(String line) {
  if (this.test != null) {
    Object l = this.test.get("ran");
    if (l instanceof java.util.List) ((java.util.List) l).add(line);
    return !Boolean.TRUE.equals(this.test.get("fail"));
  }
  try {
    @CMGR@.get().handleCommand(this.playerRef, line);
    return true;
  } catch (Throwable t) { @MU@.warn("the Admin page could not run /" + line + ": " + t); return false; }
}""")
M(ops, r"""
public java.util.UUID me() {
  try { return this.playerRef == null ? null : this.playerRef.getUuid(); } catch (Throwable t) { return null; }
}""")
M(ops, r"""
public String who() {
  try { String n = this.playerRef == null ? null : this.playerRef.getUsername(); return n == null ? "?" : n; } catch (Throwable t) { return "?"; }
}""")
M(ops, r"""
public void redraw() {
  if (this.test != null) { Object n = this.test.get("redraws"); this.test.put("redraws", Integer.valueOf(n instanceof Integer ? ((Integer) n).intValue() + 1 : 1)); return; }
  rebuild();
}""")
M(ops, r"""
public void closeNow(@REF@ ref, @ST@ st) {
  if (this.test != null) { this.test.put("went", "close"); return; }
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().setPage(ref, st, @PGE@.None);
  } catch (Throwable t) { @MU@.warn("could not close the Admin page: " + t); }
}""")
M(ops, r"""
public void openMenu(@REF@ ref, @ST@ st) {
  if (this.test != null) { this.test.put("went", "menu"); return; }
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));
  } catch (Throwable t) { @MU@.warn("could not open the SkyWynn Menu: " + t); }
}""")
# 0.3.36: after a hub click (MenuHub.click's answer; the page is tab "ops" of Settings, so row 2's Server Setup leads to Server Setup): the X
# closes, Home opens the SkyWynn Menu, an opened tab owns the screen, a tab that could not open says so
M(ops, r"""
public void hubAfter(@REF@ ref, @ST@ st, String hr) {
  if (hr.equals("close")) { closeNow(ref, st); return; }
  if (hr.equals("menu")) { openMenu(ref, st); return; }
  if (@PKG@.MenuHub.opened(hr) || hr.equals("self")) return;
  this.info = "-" + @MD@.HUB_TXT_FAIL;
  redraw();
}""")
M(ops, r"""
public void openSetup(@REF@ ref, @ST@ st) {
  if (this.test != null) { this.test.put("went", "setup"); return; }
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().openCustomPage(ref, st, new @PKG@.AdminPage(this.playerRef, "list", (String) null));
  } catch (Throwable t) { @MU@.warn("could not open Server Setup: " + t); }
}""")
# ---- the command a button runs: the root by name, its O_DEPTH sub-commands walked (a missing one = an older mod = null, hidden), then
# the command itself when it takes exactly the remaining argument count (or at most it, for an O_EXTRA command), else its usage variant for that count, else null (hidden) -
# the command object whose hasPermission the engine checks before it runs exactly this line
M(ops, r"""
public @ACM@ leaf(int i) {
  if (i < 0 || i >= O_LINE.length) return null;
  String[] w = O_LINE[i].split(" ");
  @ACM@ c = rootCmd(w[0]);
  if (c == null) return null;
  int k = 1;
  while (k <= O_DEPTH[i] && k < w.length) {
    @ACM@ s = null;
    try { s = c.getSubCommand(w[k]); } catch (Throwable t) { s = null; }
    if (s == null) return null;
    c = s;
    k++;
  }
  int n = w.length - k;
  int req = -1;
  try { req = c.getRequiredArguments().size(); } catch (Throwable t) { req = -1; }
  if (req == n || (O_EXTRA[i] && req >= 0 && req <= n)) return c;
  @ACM@ v = null;
  try { v = c.getVariantByArgCount(n); } catch (Throwable t) { v = null; }
  return v;
}""")
M(ops, r"""
public boolean visible(int i) {
  return can(leaf(i));
}""")
M(ops, r"""
public int[] visibleOn(int t) {
  int n = 0;
  boolean[] v = new boolean[O_TAB.length];
  for (int i = 0; i < O_TAB.length; i++) { if (O_TAB[i] == t && visible(i)) { v[i] = true; n++; } }
  int[] out = new int[n];
  int k = 0;
  for (int i = 0; i < O_TAB.length; i++) if (v[i]) { out[k] = i; k++; }
  return out;
}""")
M(ops, r"""
public static int num(String s) {
  try { return Integer.parseInt(s); } catch (Throwable t) { return -1; }
}""")
M(ops, r"""
public static boolean okText(String s) {
  if (s == null || s.length() == 0 || s.length() > TEXT_MAX) return false;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    boolean ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '.' || c == ':' || c == '-';
    if (!ok) return false;
  }
  return true;
}""")
M(ops, r"""
public int pickIndex(String[] on) {
  if (this.pick == null) return -1;
  for (int j = 0; j < on.length; j++) if (on[j].equalsIgnoreCase(this.pick)) return j;
  return -1;
}""")
M(ops, r"""
public String picked() {
  String[] on = online();
  int j = pickIndex(on);
  return j < 0 ? null : on[j];
}""")
M(ops, r"""
public void cyclePick(int d) {
  String[] on = online();
  if (on.length == 0) { this.pick = null; return; }
  int j = pickIndex(on);
  if (j < 0) j = d > 0 ? 0 : on.length - 1;
  else j = (j + d + on.length) % on.length;
  this.pick = on[j];
}""")
# the exact line a button dispatches, or null (this.info says what is missing)
M(ops, r"""
public String expand(int i) {
  String line = O_LINE[i];
  if (line.indexOf("{p}") >= 0) {
    String p = picked();
    if (p == null) { this.info = "-Pick an online player first (the < and > next to Player)."; return null; }
    if (!okText(p)) { this.info = "-That player name cannot be typed into a command."; return null; }
    line = line.replace("{p}", p);
  }
  if (line.indexOf("{t}") >= 0) {
    String a = this.arg == null ? "" : this.arg.trim();
    if (a.length() == 0) { this.info = "-Type the " + O_HINT[i] + " into the Text box first."; return null; }
    if (!okText(a)) { this.info = "-The Text box takes letters, digits and _ . : - only (" + TEXT_MAX + " at most), no spaces."; return null; }
    line = line.replace("{t}", a);
  }
  return line;
}""")
M(ops, r"""
public boolean armedNow(int i) {
  long d = now() - this.armedAt;
  return this.armed == i && d >= 0L && d <= CONFIRM_MS;
}""")
M(ops, r"""
public void run(int i) {
  if (i < 0 || i >= O_LINE.length) return;
  if (!visible(i)) { this.armed = -1; this.info = "-You cannot run that command (no permission, or its mod is not on this server)."; return; }
  String line = expand(i);
  if (line == null) { this.armed = -1; return; }
  long t = now();
  long dl = t - this.lastAt;
  if (this.lastI == i && line.equals(this.lastLine) && dl >= 0L && dl < DOUBLE_MS) return;
  if (O_CONF[i]) {
    long d = t - this.armedAt;
    boolean same = this.armed == i && line.equals(this.armedLine) && d >= 0L;
    if (same && d < DOUBLE_MS) return;
    if (!same || d > CONFIRM_MS) {
      this.armed = i;
      this.armedAt = t;
      this.armedLine = line;
      if (same) this.info = "=The 10 s ran out. Press " + O_LABEL[i] + " again within 10 s to run /" + line;
      else this.info = "=Press " + O_LABEL[i] + " again within 10 s to run /" + line;
      return;
    }
  }
  this.armed = -1;
  this.armedLine = "";
  this.lastI = i;
  this.lastAt = t;
  this.lastLine = line;
  if (dispatch(line)) {
    this.info = "+Ran /" + line + " - the answer is in your chat.";
    @MU@.info("Admin page: " + who() + " ran /" + line);
  } else this.info = "-/" + line + " could not be run.";
}""")
M(ops, r"""
public static String statusOf(String key) {
  if (key == null || key.length() == 0) return "";
  Object o = null;
  try { java.util.Map b = @MU@.bridge(); o = b == null ? null : b.get(key); } catch (Throwable t) { o = null; }
  if (o == null) return "";
  if (key.equals("auction:count") && o instanceof Number) return ((Number) o).longValue() + " open";
  if (key.equals("bazaar:products")) return @MU@.csvCount(o) + " items";
  return "";
}""")
M(ops, r"""
public String helpOf(int i) {
  String s = statusOf(O_STAT[i]);
  return O_HELP[i] + (s.length() > 0 ? " - " + s : "");
}""")
M(ops, r"""
public static void addWrapped(java.util.ArrayList out, String head, String list) {
  String line = head;
  String[] parts = list.split(", ");
  for (int i = 0; i < parts.length; i++) {
    String add = (line.equals(head) ? "" : ", ") + parts[i];
    if (line.length() + add.length() > LINE_MAX && !line.equals(head)) { out.add(line + ","); line = "    " + parts[i]; }
    else line = line + add;
  }
  out.add(line);
}""")
M(ops, r"""
public String[] diagLines() {
  java.util.ArrayList out = new java.util.ArrayList();
  int run = 0;
  StringBuilder off = new StringBuilder();
  StringBuilder other = new StringBuilder();
  for (int k = 0; k < O_SETMOD.length; k++) {
    String v = liveVer(O_SETMOD[k]);
    if (v == null) { if (off.length() > 0) off.append(", "); off.append(O_SETMOD[k]); continue; }
    run++;
    if (!v.equals(O_SETVER[k])) { if (other.length() > 0) other.append(", "); other.append(O_SETMOD[k]).append(' ').append(v).append(" (set ").append(O_SETVER[k]).append(')'); }
  }
  out.add("Skyy mods running: " + run + " of the " + O_SETMOD.length + " in the set this menu was built with.");
  if (off.length() > 0) addWrapped(out, "Not running: ", off.toString());
  if (other.length() > 0) addWrapped(out, "Other version: ", other.toString());
  out.add("Players online: " + online().length);
  String ah = statusOf("auction:count");
  out.add("Auction House: " + (ah.length() > 0 ? ah : "no count published"));
  String bz = statusOf("bazaar:products");
  out.add("Bazaar: " + (bz.length() > 0 ? bz : "no item list published"));
  return (String[]) out.toArray(new String[0]);
}""")
# the Text box's EventData key "@OpsArg" (the at sign is the build's token marker, so it is made here - AdminPage.at's way)
M(ops, r"""
public static String argKey() {
  return String.valueOf((char) 64) + "OpsArg";
}""")
M(ops, r"""
public @EVD@ evd(String a) {
  @EVD@ d = @EVD@.of("a", a);
  if (this.field) d = d.append(argKey(), "#SkyyOpsArg.Value");
  return d;
}""")
# 0.3.36: the kit 1.7 hub page - rows 1 + 2 (HubBar.page17), the sub-tabs (their clicks carry the Text box), the picker row, ONE scroll list
# of the visible buttons (a short tab grows its rows: HubBar.growSize over O_ROWH; Diagnostics' info lines below), the footer
M(ops, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  boolean ok = pageOk();
  if (this.tab < 0 || this.tab >= O_TABS.length) this.tab = 0;
  int[] vis = ok ? visibleOn(this.tab) : new int[0];
  this.pg = 0;
  this.field = ok;
""" + "\n".join("  " + ln for ln in OPS_SHELL_JAVA.split("\n")) + r"""
  @PKG@.MenuHub.ensure(me());
  """ + OPS_HUB_JAVA + r"""
  if (ok) {
    for (int k = 0; k < O_SUBN.length; k++) {
      if (k > 0) b.appendInline("#SkyyOpsFSub", O_SUBGAP);
      b.appendInline("#SkyyOpsFSub", k == this.tab + 1 ? O_SUBS[k] : O_SUBN[k]);
      ev.addEventBinding(@BT@.Activating, "#SkyyOpsFSub" + k, evd(k == 0 ? "setup" : "ot" + (k - 1)));
    }
  }
  """ + OPS_PART_JAVA["sub"] + r"""
  b.set("#SkyyOpsSub.Text", ok ? SUB : textOf(NOACCESS));
  if (ok) {
    """ + OPS_PART_JAVA["pick"] + r"""
""" + "\n".join("    " + ln for ln in OPS_PICK_JAVA.split("\n")) + r"""
    String[] on = online();
    int pj = pickIndex(on);
    b.set("#SkyyOpsPName.Text", pj < 0 ? (on.length == 0 ? "nobody online" : "nobody picked") : on[pj] + "  (" + (pj + 1) + " of " + on.length + ")");
    if (this.arg != null && this.arg.length() > 0) b.set("#SkyyOpsArg.Value", this.arg);
    ev.addEventBinding(@BT@.Activating, "#SkyyOpsPPrev", evd("pprev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyOpsPNext", evd("pnext"));
    ev.addEventBinding(@BT@.Activating, "#SkyyOpsClr", evd("clr"));
  }
  """ + OPS_PART_JAVA["list"] + r"""
  int n = vis.length;
  String[] dl = new String[0];
  if (ok && this.tab == O_DIAG) dl = diagLines();
  else if (ok && n == 0) dl = new String[] { "No button on this tab for you: none of its commands is on this server, or your permissions do not include them." };
  int nr = (n + 1) / 2;
  int sz = nr > 0 ? @PKG@.HubBar.growSize(nr, LIST_IN - dl.length * LINE_H, O_ROWH, ROW_GAP) : 0;
  int bh = O_ROWH[sz];
  for (int c = 0; c < n; c++) {
    int r = c / 2;
    int i = vis[c];
    boolean arm = armedNow(i);
    boolean dng = O_CONF[i] || arm;
    if (c % 2 == 0) {
      """ + OPS_GRID_JAVA["row"] + r"""
    }
    """ + OPS_GRID_JAVA["cell"] + r"""
    """ + OPS_GRID_JAVA["btn"] + r"""
    b.set("#SkyyOpsA" + i + ".Text", arm ? "Press again" : O_LABEL[i]);
    """ + OPS_GRID_JAVA["gap"] + r"""
    """ + OPS_GRID_JAVA["help"] + r"""
    b.set("#SkyyOpsH" + c + ".Text", helpOf(i));
    ev.addEventBinding(@BT@.Activating, "#SkyyOpsA" + i, evd("op" + i));
  }
  for (int k = 0; k < dl.length; k++) {
    """ + OPS_GRID_JAVA["line"] + r"""
    b.set("#SkyyOpsI" + k + ".Text", dl[k]);
  }
""" + "\n".join("  " + ln for ln in OPS_FOOT_JAVA.split("\n")) + r"""
  b.set("#SkyyOpsMsg.Text", textOf(ok ? this.info : NOACCESS));
  ev.addEventBinding(@BT@.Activating, "#SkyyOpsClose", evd("close"));
}""")
M(ops, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String hr = @PKG@.MenuHub.click(this.playerRef, data, "settings", "ops");   // 0.3.36: rows 1 + 2 (the bar's click carries no Text box)
    if (hr != null) { hubAfter(ref, st, hr); return; }
    String a = @MU@.jstr(data, "a", 40);
    if (data.indexOf("\"" + argKey() + "\"") >= 0) this.arg = @MU@.jstr(data, argKey(), TEXT_MAX);
    if (a.equals("close")) { closeNow(ref, st); return; }
    if (!pageOk()) { this.info = NOACCESS; this.armed = -1; redraw(); return; }
    if (a.equals("setup")) { openSetup(ref, st); return; }
    if (a.startsWith("ot")) {
      int t = num(a.substring(2));
      if (t >= 0 && t < O_TABS.length) { this.tab = t; this.pg = 0; this.armed = -1; this.info = ""; }
    }
    else if (a.equals("pprev")) cyclePick(-1);
    else if (a.equals("pnext")) cyclePick(1);
    else if (a.equals("clr")) this.arg = "";
    else if (a.startsWith("op")) run(num(a.substring(2)));
    redraw();
  } catch (Throwable t) { @MU@.warn("admin page click failed: " + t); }
}""")
# /modconfig admin (the /modconfig <mod> usage variant; skyymenu.modconfig) and nothing else opens it; runs on the player's world thread
M(ops, r"""
public static void openFor(@PR@ pr, @ST@ store, @REF@ ref) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return;
    p.getPageManager().openCustomPage(ref, store, new @PKG@.OpsPage(pr, 0));
  } catch (Throwable t) {
    @MU@.warn("/modconfig admin failed: " + t);
    try { pr.sendMessage(@MSG@.raw("[Admin] Could not open the Admin page.")); } catch (Throwable t2) { }
  }
}""")

# ================= /modconfig (alias /serversetup) + the usage variant /modconfig <mod>; admins only (requirePermission, HANDOFF rule 1) =================
F(acmv, "public @RA@ modArg;")
C(acmv, r"""
public AdminModCmd() {
  super("Open one mod's settings in Server Setup: /modconfig <mod> (/modconfig admin = the Admin page)");
  requirePermission(@MD@.ADMIN_NODE);
  this.modArg = withRequiredArg("mod", "a mod name, e.g. menu, bank or SkyyEconomy (Skyy is optional)", @ATY@.STRING);
}""")
M(acmv, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  String a = null;
  try { a = String.valueOf(ctx.get(this.modArg)); } catch (Throwable t) { a = null; }
  if (a != null && a.trim().equalsIgnoreCase("admin")) { @PKG@.OpsPage.openFor(pr, store, ref); return; }   // 0.3.23
  @PKG@.AdminPage.openFor(pr, store, ref, a);
}""")
C(acmd, r"""
public AdminCmd() {
  super("modconfig", "(admin) Server Setup: change every Skyy mod's settings in game - /modconfig or /modconfig <mod>");
  requirePermission(@MD@.ADMIN_NODE);
  addAliases(new String[] { "serversetup" });
  addUsageVariant(new @PKG@.AdminModCmd());
}""")
M(acmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.AdminPage.openFor(pr, store, ref, (String) null);
}""")

# ================= 0.3.24 /soundtest (skyymenu.modconfig): hear any vanilla sound event 2D (research/Sound-Pass-Plan.md question 1) =================
import zipfile as _zf
_SNDZ = ASSETS_ZIP   # 0.3.26: the cached copy
SOUND_IDS = set(os.path.basename(n)[:-5] for n in _zf.ZipFile(_SNDZ).namelist() if n.startswith("Server/Audio/SoundEvents/") and n.endswith(".json"))
SND_LIST = [('SFX_Dungeon_Checkpoint_Activate', 'Quests: task done'), ('SFX_Event_Chapter_1_Complete_Sting', 'Quests: quest line done'), ('SFX_Coins_Land', 'Quests: reward paid'), ('SFX_Drag_Items_Paper', 'Quests: talk to a quest NPC'), ('SFX_Chest_Wooden_Open_Player', 'Exploration: Lost Loot / supply drop claimed'), ('SFX_Wood_Land', 'Exploration: supply drop lands'), ('SFX_Coffer_Goblin_Reward', 'Exploration reveal: Rare card; Bank: interest paid'), ('SFX_Memories_Unlock_Local', 'Exploration reveal: Legendary card'), ('SFX_Portal_Neutral_Teleport_Local', 'Islands: /island or /hub arrival'), ('SFX_Deployable_Totem_Heal_Spawn', 'Pets: pet into a slot'), ('SFX_Deployable_Totem_Heal_Despawn', 'Pets: pet out of its slot'), ('SFX_Discovery_Z1_Short', 'Exploration: discovery spot'), ('SFX_Discovery_Z1_Medium', 'Exploration: secret spot'), ('SFX_Discovery_Z2_Medium', 'Exploration: checklist entry')]
SND_MORE = [('SFX_Workbench_Upgrade_Complete_Default', 'plan: skill level up / upgrades'), ('SFX_Runebinders_Lattice_Unlock_Local', 'plan: tree node / recipe / slot unlock'), ('SFX_MemoryRestored', 'plan: big reward'), ('SFX_Divine_Respawn', 'plan: rebirth done / big heal'), ('SFX_Portal_Void', 'plan: rebirth confirm'), ('SFX_Void_Encroaching', 'plan: rebirth confirm (dark)'), ('SFX_Portal_Neutral_Open', 'plan: profile switch / shard portal'), ('SFX_Coins_Hit', 'plan: bank deposit / withdraw'), ('SFX_Coins_Break', 'plan: death coin loss'), ('SFX_Drop_Items_Paper', 'plan: AH listed / quest skipped'), ('SFX_Generic_Crafting_Failed', 'plan: cooldown / no Mana / refused'), ('SFX_Incorrect_Tool', 'plan: tool tier refused'), ('SFX_Ability_Wind_Strike_Imbue_Local', 'plan: ability cast (generic)'), ('SFX_Ability_Enrage', 'plan: rage ability'), ('SFX_Ability_Ground_Slam_Impact', 'plan: slam ability'), ('SFX_Chest_Legendary_FirstOpen_Player', 'plan: identify (rare and up)'), ('SFX_Weapon_Bench_Craft', 'plan: reforge a weapon'), ('SFX_Armour_Bench_Craft', 'plan: reforge armour'), ('SFX_Drag_Items_Gems', 'plan: accessory equip'), ('SFX_Crops_Grow_Stage_Complete', 'plan: double drop / totem tick'), ('SFX_Furnace_Bench_Processing_Complete', 'plan: compactor / compressor'), ('SFX_Crystal_Hit', 'plan: collect from a shard'), ('SFX_Tornado', 'plan: monk burst')]
_snd_all = SND_LIST + SND_MORE
assert all(i in SOUND_IDS for i, _u in _snd_all), [i for i, _u in _snd_all if i not in SOUND_IDS]
assert len(set(i for i, _u in _snd_all)) == len(_snd_all), "a sound id twice in the /soundtest list"
assert all(re.match(r"^[A-Za-z0-9_]{1,120}$", i) and all(32 <= ord(c) < 127 for c in u) for i, u in _snd_all)
F(snt, "public static final String[] IDS = %s;" % jarr([i for i, _u in _snd_all]))
F(snt, "public static final String[] USES = %s;" % jarr([u for _i, u in _snd_all]))
F(snt, "public static final int IN_USE = %d;" % len(SND_LIST))
F(snt, "public static final java.util.concurrent.ConcurrentHashMap CURSOR = new java.util.concurrent.ConcurrentHashMap();")
F(snt, "public static final java.util.concurrent.atomic.AtomicLong PLAYED = new java.util.concurrent.atomic.AtomicLong();")
M(snt, r"""
public static int idx(String id) {
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent.getAssetMap();
    return m == null ? Integer.MIN_VALUE : m.getIndex(id);
  } catch (Throwable t) { return Integer.MIN_VALUE; }
}""")
M(snt, r"""
public static boolean okId(String s) {
  if (s == null || s.length() == 0 || s.length() > 120) return false;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return false;
  }
  return true;
}""")
M(snt, r"""
public static int num(String s) {
  if (s == null || s.length() == 0 || s.length() > 4) return -1;
  for (int i = 0; i < s.length(); i++) if (s.charAt(i) < '0' || s.charAt(i) > '9') return -1;
  return Integer.parseInt(s);
}""")
# 2D to that player only (UI); the answer line ("+" played, "-" why not)
M(snt, r"""
public static String play(@PR@ pr, String id, String what) {
  if (pr == null) return "-No player.";
  int i = idx(id);
  if (i == Integer.MIN_VALUE || i == 0) return "-The game has no sound event '" + id + "'. Ids look like SFX_Coins_Land - /soundtest list.";
  try {
    com.hypixel.hytale.server.core.universe.world.SoundUtil.playSoundEvent2dToPlayer(pr, i, com.hypixel.hytale.protocol.SoundCategory.UI);
    PLAYED.incrementAndGet();
    return "+Playing " + what + " (only you hear it).";
  } catch (Throwable t) { @MU@.warn("/soundtest could not play " + id + ": " + t); return "-Could not play it - see the server log."; }
}""")
M(snt, r"""
public static String label(int n) {
  return "#" + n + " " + IDS[n - 1] + " - " + USES[n - 1];
}""")
M(snt, r"""
public static java.util.ArrayList help() {
  java.util.ArrayList out = new java.util.ArrayList();
  out.add("=/soundtest list - the " + IN_USE + " sounds SkyWynn plays now, numbered (/soundtest more = " + (IDS.length - IN_USE) + " ideas for later)");
  out.add("=/soundtest <number> | next | prev - play one from the list; /soundtest <id> - play any vanilla sound id (SFX_...)");
  out.add("=Change a mod's sound in Server Setup -> <mod> -> Sounds (each sound: on / off + its id).");
  return out;
}""")
# the whole command (pure but the play): lines to send. cursor per player for next / prev (1-based, wraps over the whole list)
M(snt, r"""
public static java.util.ArrayList run(@PR@ pr, String arg) {
  java.util.ArrayList out = new java.util.ArrayList();
  String a = arg == null ? "" : arg.trim();
  if (a.length() == 0 || a.equalsIgnoreCase("help")) return help();
  if (a.equalsIgnoreCase("list") || a.equalsIgnoreCase("more") || a.equalsIgnoreCase("all")) {
    boolean more = a.equalsIgnoreCase("more");
    int from = more ? IN_USE + 1 : 1;
    int to = a.equalsIgnoreCase("list") ? IN_USE : IDS.length;
    out.add("=" + (more ? "Sound ideas from the sound plan (not played yet):" : (to == IDS.length ? "Every listed sound:" : "Sounds SkyWynn plays now:")));
    for (int n = from; n <= to; n++) out.add(" " + label(n));
    out.add("=Play one: /soundtest <number> (or next / prev).");
    return out;
  }
  java.util.UUID u = null;
  try { u = pr == null ? null : pr.getUuid(); } catch (Throwable t) { u = null; }
  int n = num(a);
  if (a.equalsIgnoreCase("next") || a.equalsIgnoreCase("prev")) {
    Object o = u == null ? null : CURSOR.get(u);
    int c = o instanceof Integer ? ((Integer) o).intValue() : 0;
    if (a.equalsIgnoreCase("next")) c = c >= IDS.length ? 1 : c + 1;
    else c = c <= 1 ? IDS.length : c - 1;
    n = c;
  }
  if (n >= 0) {
    if (n < 1 || n > IDS.length) { out.add("-There is no #" + n + " - the list has 1 to " + IDS.length + " (/soundtest list)."); return out; }
    if (u != null) CURSOR.put(u, Integer.valueOf(n));
    out.add(play(pr, IDS[n - 1], label(n)));
    return out;
  }
  if (!okId(a)) { out.add("-A sound id is letters, digits and _ only (like SFX_Coins_Land), or a list number."); return out; }
  int k = -1;
  for (int j = 0; j < IDS.length; j++) if (IDS[j].equalsIgnoreCase(a)) k = j;
  out.add(play(pr, k >= 0 ? IDS[k] : a, k >= 0 ? label(k + 1) : a));
  return out;
}""")
M(snt, r"""
public static void send(@PR@ pr, java.util.ArrayList lines) {
  for (int i = 0; i < lines.size(); i++) {
    String l = String.valueOf(lines.get(i));
    char c = l.length() > 0 ? l.charAt(0) : ' ';
    String t = c == '+' || c == '-' || c == '=' ? l.substring(1) : l;
    try { pr.sendMessage(@MSG@.raw("[Sound test] " + t).color(c == '+' ? "@GOOD@" : (c == '-' ? "@BAD@" : "@INFO@"))); } catch (Throwable x) { }
  }
}""".replace("@GOOD@", SUI.COLOR["success"]).replace("@BAD@", SUI.COLOR["error"]).replace("@INFO@", SUI.COLOR["info"]))
F(stv, "public @RA@ whatArg;")
C(stv, r"""
public SoundTestArgCmd() {
  super("(admin) hear a vanilla sound: /soundtest list | more | <number> | next | prev | <sound id>");
  requirePermission(@MD@.ADMIN_NODE);
  this.whatArg = withRequiredArg("what", "list, more, a list number, next, prev or a sound id like SFX_Coins_Land", @ATY@.STRING);
}""")
M(stv, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  String a = null;
  try { a = String.valueOf(ctx.get(this.whatArg)); } catch (Throwable t) { a = null; }
  try { @PKG@.SoundTest.send(pr, @PKG@.SoundTest.run(pr, a)); }
  catch (Throwable t) { @MU@.warn("/soundtest failed: " + t); }
}""")
C(stm, r"""
public SoundTestCmd() {
  super("soundtest", "(admin) hear any vanilla sound by id or by number - /soundtest list");
  requirePermission(@MD@.ADMIN_NODE);
  addUsageVariant(new @PKG@.SoundTestArgCmd());
}""")
M(stm, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.SoundTest.send(pr, @PKG@.SoundTest.help()); } catch (Throwable t) { @MU@.warn("/soundtest failed: " + t); }
}""")

# ================= 0.3.28 MenuHub part 2: Menu's own tab pages, the open / visible Functions, the registry, the hub commands =========
# page(): the page a Menu tab opens. openFor(): the open Function's body - the player's world thread (a page event or a command is the
# caller, HUBS-CONTRACT 1): the player's page manager opens the page (a SkyWynn Menu on screen gets its grid emptied first, the 0.1.3
# stuck-tooltip rule for every hand-off). Anything that goes wrong = false (the bar then tries the tab's command, HUBS-CONTRACT 1).
M(mhub, r"""
public static @PAGE@ page(@PR@ pr, String tab) {
  if (pr == null || tab == null) return null;
  if (tab.equals("stats")) return new @PKG@.StatsPage(pr, 0);
  if (tab.equals("teleport")) return new @PKG@.MenuPage(pr, "tp");
  if (tab.equals("players")) return new @PKG@.MenuPage(pr, "players");
  if (tab.equals("settings")) return new @PKG@.SettingsPage(pr, -1);
  if (tab.equals("mods")) return new @PKG@.MenuPage(pr, "mods");
  if (tab.equals("setup")) return new @PKG@.AdminPage(pr, "list", null);
  if (tab.equals("layout")) {
    @PKG@.MenuPage m = new @PKG@.MenuPage(pr, "main");
    if (@PKG@.MenuLayout.unreadable(pr.getUuid())) m.status = @PKG@.MenuData.EDIT_WAIT;
    else m.startEdit();
    return m;
  }
  return null;
}""")
M(mhub, r"""
public static boolean openFor(java.util.UUID u, String tab) {
  if (u == null || tab == null) return false;
  try {
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null || !pr.isValid()) return false;
    if (!visible(tab, pr)) return false;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return false;
    @ST@ st = r.getStore();
    if (st == null) return false;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return false;
    @PGM@ pm = p.getPageManager();
    if (pm == null) return false;
    @PAGE@ pg = page(pr, tab);
    if (pg == null) return false;
    Object cur = pm.getCustomPage();
    if (cur instanceof @PKG@.MenuPage) ((@PKG@.MenuPage) cur).clearGrid();
    pm.openCustomPage(r, st, pg);
    return true;
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("the hub tab " + tab + " could not open: " + t);
    return false;
  }
}""")
mho.addInterface(pool.get("java.util.function.Function"))
F(mho, "public String tab;")
C(mho, "public MenuHubOpen(String tab) { this.tab = tab; }")
M(mho, r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
  return @PKG@.MenuHub.openFor((java.util.UUID) o, this.tab) ? Boolean.TRUE : Boolean.FALSE;
}""")
mhv.addInterface(pool.get("java.util.function.Function"))
F(mhv, "public String tab;")
C(mhv, "public MenuHubVis(String tab) { this.tab = tab; }")
M(mhv, r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer((java.util.UUID) o); } catch (Throwable t) { pr = null; }
  if (pr == null) return Boolean.FALSE;
  return @PKG@.MenuHub.visible(this.tab, pr) ? Boolean.TRUE : Boolean.FALSE;
}""")
mal.addInterface(pool.get("java.util.function.Function"))
C(mal, "public MenuAlert() { }")
M(mal, r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return null;
  java.util.UUID u = (java.util.UUID) o;
  StringBuilder sb = new StringBuilder();
  try {
    if (@PKG@.MenuLayout.MIGRATED.containsKey(u.toString())) sb.append(@PKG@.MenuData.AL_MIG).append("|edit");
    if (@PKG@.SetStore.isBroken(u)) { if (sb.length() > 0) sb.append('\n'); sb.append(@PKG@.MenuData.AL_SET).append("|settings:settings"); }
    if (@PKG@.MenuLayout.SPILL.containsKey(u.toString())) { if (sb.length() > 0) sb.append('\n'); sb.append(@PKG@.MenuData.AL_SPILL).append("|edit"); }   // 0.3.30
  } catch (Throwable t) { return null; }
  return sb.length() == 0 ? null : sb.toString();
}""")
# 0.3.30: a STAND-IN tab's Functions. MenuVtOpen = the owner's bridge Function (gear:fn:smithing {UUID, tab}); anything but TRUE = the kit's
# HubBar.open runs the tab's command as the player. MenuVtVis = the tab shows only while its command is on this server.
mvo.addInterface(pool.get("java.util.function.Function"))
F(mvo, "public String fn;")
F(mvo, "public String arg;")
C(mvo, "public MenuVtOpen(String fn, String arg) { this.fn = fn; this.arg = arg; }")
M(mvo, r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
  Object f = @PKG@.MenuUtil.bridge().get(this.fn);
  if (!(f instanceof java.util.function.Function)) return Boolean.FALSE;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(new Object[] { o, this.arg }); } catch (Throwable t) { r = null; }
  return Boolean.TRUE.equals(r) ? Boolean.TRUE : Boolean.FALSE;
}""")
mvv.addInterface(pool.get("java.util.function.Function"))
F(mvv, "public String cmd;")
C(mvv, "public MenuVtVis(String cmd) { this.cmd = cmd; }")
M(mvv, r"""
public Object apply(Object o) {
  return @PKG@.MenuUtil.cmd(@PKG@.MenuUtil.firstWord(this.cmd)) != null ? Boolean.TRUE : Boolean.FALSE;
}""")
F(mhub, "public static volatile int PROXIES;")
# setup(): hub:def:<hub> for the 7 hubs + Menu's own 7 tabs (HubBar.put: Object[]{mod, label, Integer order, command, open, visible});
# shutdown() removes them (clearAll -> HubBar.removeAll: only keys that still hold OUR arrays). Returns the tabs put.
M(mhub, r"""
public static int register() {
  // 0.3.29 (kit 1.6): hub:def:<hub> = {title, command, icon, default tab}; hub:def:home = row 1's Home button; home:alert:SkyyMenu
  for (int i = 0; i < @PKG@.MenuData.HUB_ID.length; i++) {
    String dt = @PKG@.MenuData.HUB_DEFTAB[i];
    @PKG@.HubBar.def4(@PKG@.MenuData.HUB_ID[i], @PKG@.MenuData.HUB_TITLE[i], @PKG@.MenuData.HUB_CMD[i], @PKG@.MenuData.HUB_ICON[i], dt.length() == 0 ? null : dt);
  }
  @PKG@.HubBar.def4("home", @PKG@.MenuData.HOME_TITLE, "skymenu", @PKG@.MenuData.HOME_ICON, null);
  java.util.Map am = @PKG@.HubBar.map();
  if (am != null) {
    Object al = new @PKG@.MenuAlert();
    am.put("home:alert:SkyyMenu", al);
    @PKG@.HubBar.mine().put("home:alert:SkyyMenu", al);
    String[] art = @PKG@.MenuData.TAB_ART;   // 0.3.35: the hub tab pictures this jar ships (kit 1.7: every mod's row 2 draws them while we are loaded)
    am.put("hub:art", art);
    @PKG@.HubBar.mine().put("hub:art", art);
  }
  int n = 0;
  for (int j = 0; j < @PKG@.MenuData.HT_TAB.length; j++) {
    String c = @PKG@.MenuData.HT_CMD[j];
    Object vis = null;
    if (@PKG@.MenuData.HT_VIS[j]) vis = new @PKG@.MenuHubVis(@PKG@.MenuData.HT_TAB[j]);
    String host = @PKG@.MenuData.HT_HOST[j];
    Object[] e = null;
    if (host.length() > 0) {   // 0.3.33: a MERGED tab (Stats -> part of Skills): published, never drawn in a strip while its host is there
      e = @PKG@.HubBar.putSub(@PKG@.MenuData.HT_HUB[j], @PKG@.MenuData.HT_TAB[j], "SkyyMenu", @PKG@.MenuData.HT_LABEL[j], @PKG@.MenuData.HT_ORDER[j],
                              c.length() == 0 ? null : c, new @PKG@.MenuHubOpen(@PKG@.MenuData.HT_TAB[j]), new @PKG@.HubHide(@PKG@.MenuData.HT_HUB[j], host),
                              @PKG@.MenuData.HT_HUB[j] + "_" + @PKG@.MenuData.HT_TAB[j], host);
    } else {
      e = @PKG@.HubBar.putIcon(@PKG@.MenuData.HT_HUB[j], @PKG@.MenuData.HT_TAB[j], "SkyyMenu", @PKG@.MenuData.HT_LABEL[j], @PKG@.MenuData.HT_ORDER[j],
                               c.length() == 0 ? null : c, new @PKG@.MenuHubOpen(@PKG@.MenuData.HT_TAB[j]), vis, @PKG@.MenuData.HT_HUB[j] + "_" + @PKG@.MenuData.HT_TAB[j]);   // 0.3.30: + its tab icon
    }
    if (e != null) n = n + 1;
  }
  // 0.3.30 STAND-IN TABS (Skyy 2026-10-16 "smithing still working"): every contract tab whose owner put none - only while the key is free (the
  // owner's own tab always wins: put before us = we skip it, put after us = it replaces ours; shutdown removes only what still is ours)
  int px = 0;
  for (int j = 0; j < @PKG@.MenuData.VT_HUB.length; j++) {
    if (@PKG@.HubBar.get("hub:tab:" + @PKG@.MenuData.VT_HUB[j] + ":" + @PKG@.MenuData.VT_TAB[j]) != null) continue;
    Object op = @PKG@.MenuData.VT_FN[j].length() == 0 ? null : new @PKG@.MenuVtOpen(@PKG@.MenuData.VT_FN[j], @PKG@.MenuData.VT_ARG[j]);
    Object[] e = @PKG@.HubBar.putIcon(@PKG@.MenuData.VT_HUB[j], @PKG@.MenuData.VT_TAB[j], "SkyyMenu", @PKG@.MenuData.VT_LABEL[j], @PKG@.MenuData.VT_ORDER[j],
                                      @PKG@.MenuData.VT_CMD[j], op, new @PKG@.MenuVtVis(@PKG@.MenuData.VT_CMD[j]), @PKG@.MenuData.VT_HUB[j] + "_" + @PKG@.MenuData.VT_TAB[j]);
    if (e != null) px = px + 1;
  }
  PROXIES = px;
  return n;
}""")
# a hub command (world thread): the hub's last tab while it is still shown, else its first shown tab (HubBar.open: its open Function,
# else its command); no tab yet = the "coming soon" chat line; a tab that could not open = one chat line. Returns open()'s answer.
M(mhub, r"""
public static String run(@PR@ pr, String hub) {
  if (pr == null) return "failed";
  int i = hubIndex(hub);
  String title = i < 0 ? String.valueOf(hub) : @PKG@.MenuData.HUB_TITLE[i];
  try {
    java.util.UUID u = pr.getUuid();
    ensure(u);
    String tab = pick(hub, u);
    if (tab == null) {
      pr.sendMessage(@MSG@.raw("[" + title + "] " + (i < 0 ? "Nothing here yet." : @PKG@.MenuData.HUB_SOON[i])));
      return "soon";
    }
    String r = @PKG@.HubBar.open(pr, u, hub, tab);
    if (opened(r)) return r;
    pr.sendMessage(@MSG@.raw("[" + title + "] " + @PKG@.MenuData.HUB_TXT_FAIL));
    return r;
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("/" + hub + " failed: " + t);
    try { pr.sendMessage(@MSG@.raw("[" + title + "] Could not open the " + title + " hub.")); } catch (Throwable t2) { }
    return "failed";
  }
}""")
# the five hub commands (spec 2.3): everyone (hytale:Adventurer, HANDOFF section 3), no arguments; /travel opens the World hub
C(hcch, r"""
public HubCharCmd() {
  super("character", "Open the Character hub - your stats and more, one tab each");
  addAliases(new String[] { "char" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hcch, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "character");
}""")
C(hcst, r"""
public HubStorageCmd() {
  super("storage", "Open the Storage hub - the Void, Requip, Vault and Bank in one place");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hcst, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "storage");
}""")
C(hcmk, r"""
public HubMarketCmd() {
  super("market", "Open the Market hub - Bazaar, Auction House and Merchants in one place");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hcmk, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "market");
}""")
C(hctr, r"""
public HubTravelCmd() {
  super("travel", "Open the World hub - teleports, warps, your island and exploring");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hctr, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "world");
}""")
C(hcso, r"""
public HubSocialCmd() {
  super("social", "Open the Social hub - players online, your party and guild");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hcso, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "social");
}""")
# 0.3.31: /crafting = the Crafting hub (id "smithing"): its last tab, else Crafting (the first by order)
C(hccr, r"""
public HubCraftCmd() {
  super("crafting", "Open the Crafting hub - the crafter (/craft) and Smithing (/smithing) in one place");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hccr, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.MenuHub.run(pr, "smithing");
}""")

# ================= MenuPageFactory (right-click on the menu item -> OpenCustomUI "SkyyMenu") =================
fac.addInterface(pool.get("java.util.function.Function"))
C(fac, "public MenuPageFactory() { }")
M(fac, r"""
public Object apply(Object o) {
  return new @PKG@.MenuPage((@PR@) o, "main");
}""")

# ================= 0.3.32 THE LIFELONG MENU ITEM (tools/skyyonce.py): MenuOnce (rules), MenuOnceTask, MenuOnceDropSys, MenuOnceThrowSys,
# MenuOnceInvSys, MenuOnceReady, MenuOnceFn (once:item:Skyy_Menu + the market:veto entry). ON = MenuCfg.KEEP_ITEM (row menu.itemKeep).
assert "menuitem" in ALIASES, "0.3.32: /menuitem is taken by another build script - pick another recall word"
LIFE = ONCE.emit(pool, PKG, "MenuOnce", item=MENU_ITEM_ID, name="SkyWynn Menu item", tag="[Menu]", recall="/menuitem", mod="SkyyMenu",
                 on_expr=PKG + ".MenuCfg.KEEP_ITEM", info_col=SUI.STATUS["="], warn_col=SUI.STATUS_INFO["gold"])

# ================= /skymenu =================
C(cmd, r"""
public MenuCmd() {
  super("skymenu", "Open the SkyWynn menu (gives you a new menu item if you lost it)");
  if (@PKG@.MenuData.ALIASES.length > 0) addAliases(@PKG@.MenuData.ALIASES);
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(cmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ player = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (player == null) return;
    java.util.UUID u = pr.getUuid();
    boolean none = @PKG@.MenuUtil.count(player, @PKG@.MenuData.ITEM_ID) <= 0;
    if (none && @PKG@.MenuUtil.profileBusy(u)) {
      pr.sendMessage(@MSG@.raw("[Menu] Your profile is still loading, so you get no new menu item yet. Type /skymenu again in a moment."));
    } else if (none) {
      if (@PKG@.MenuUtil.giveMenuItem(player)) {
        String gk = @PKG@.Given.key(u);
        @PKG@.Given.markGiven(gk);
        @PKG@.Given.SESSION.put(gk, Boolean.TRUE);
        pr.sendMessage(@MSG@.raw("[Menu] You did not have a SkyWynn Menu item, so here is a new one. Right-click it any time to open this menu."));
      } else {
        pr.sendMessage(@MSG@.raw("[Menu] Your inventory is full, so you could not get a new menu item. Make room and type /skymenu again."));
      }
    }
    player.getPageManager().openCustomPage(ref, store, new @PKG@.MenuPage(pr, "main"));
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("/skymenu failed: " + t);
    pr.sendMessage(@MSG@.raw("[Menu] Could not open the menu."));
  }
}""")

# ================= Given.plan (0.3.4; after MenuCfg - it reads MenuCfg.GIVE_ITEM) =================
# what a grant does for player u whose ACTIVE profile has the storage key `key` and who holds `held` menu items (-1 = no player entity now):
#   1 = nothing to do: this session did it, the item is switched off, the profile already got it (record), or it holds one (recorded now)
#   2 = try again later: SkyyProfiles is busy with that player's inventory (profile:busy - checked BEFORE the inventory is trusted), or
#       no player entity
#   4 = give ONE now (the session mark is set first, so a full inventory is not retried on every world switch - next login)
# 0.3.19 C: 0.3.4's plan in two halves, the same answers in the same order. planFiles = the FILE part (the legacy migration + the record),
# run on SkyyMenu-IO; planHeld = the INVENTORY part (busy, the count), run on the world thread with no file access - a held item's record
# is written back on SkyyMenu-IO (markLater; inline only when MenuIO is stopped).
gsv.addInterface(pool.get("java.lang.Runnable"))
F(gsv, "public String key;")
C(gsv, "public GivenSave(String key) { this.key = key; }")
M(gsv, r"""
public void run() {
  try { @PKG@.Given.markGiven(this.key); } catch (Throwable t) { @PKG@.MenuUtil.warn("could not save the menu-item record for " + this.key + ": " + t); }
}""")
M(giv, r"""
public static void markLater(String key) {
  if (!@PKG@.MenuIO.schedule(new @PKG@.GivenSave(key), 0L)) markGiven(key);
}""")
M(giv, r"""
public static int planFiles(java.util.UUID u, String key) {
  if (u == null || !validKey(key)) return 2;
  if (SESSION.containsKey(key)) return 1;
  if (!@PKG@.MenuCfg.GIVE_ITEM) { SESSION.put(key, Boolean.TRUE); return 1; }
  migrate(u, key);
  if (isGiven(key)) { SESSION.put(key, Boolean.TRUE); return 1; }
  return 4;
}""")
M(giv, r"""
public static int planHeld(java.util.UUID u, String key, int held) {
  if (u == null || !validKey(key)) return 2;
  if (SESSION.containsKey(key)) return 1;
  if (!@PKG@.MenuCfg.GIVE_ITEM) { SESSION.put(key, Boolean.TRUE); return 1; }
  if (@PKG@.MenuUtil.profileBusy(u)) return 2;
  if (held < 0) return 2;
  if (held > 0) { markLater(key); SESSION.put(key, Boolean.TRUE); return 1; }
  SESSION.put(key, Boolean.TRUE);
  return 4;
}""")

# ================= 0.3.19 G: THE HUB HOTKEY - double-tap crouch opens the SkyWynn Menu =================
# MenuHotkey: an EntityTickingSystem on every player (world thread, not parallel). Per player and tick: ONE MovementStatesComponent read
# (the server's copy of the client's movement states); a per-player state (long[3] { crouching last tick, the first press ms, the last open
# ms }) exists only after the player's first crouch (ST, keyed by the entity Ref; dead refs are dropped by SeenTick). step() = the gesture
# (pure: the harness drives it): a crouch PRESS (false -> true) on the ground with nothing else going on (still()) arms; a second press
# within MenuCfg.HOTKEY_GAP_MS fires once (MenuCfg.HOTKEY_COOLDOWN_MS between opens; both Server Setup rows, read live); a press while
# moving in another state disarms. The open itself is queued on the player's world thread (HotkeyOpen - never inside the system's tick):
# only with the player's switch on (menu.hotkey, ON by default), no other page open, NO open window (FIX ROUND: a chest / bench / vault
# window leaves getCustomPage() null) and SkyyProfiles not busy with the player, then exactly what /skymenu opens (the main view); a
# refusal is one INFO line. ON = false at shutdown.
F(mhk, "public static final java.util.concurrent.ConcurrentHashMap ST = new java.util.concurrent.ConcurrentHashMap();")
F(mhk, "public static volatile boolean ON = true;")
F(mhk, "public static volatile long FIRED = 0L;")
F(mhk, "public static volatile boolean FAILED_ONCE = false;")
C(mhk, "public MenuHotkey() { super(); }")
M(mhk, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}""")
M(mhk, r"""
public static boolean still(@MVS@ m) {
  if (m == null) return false;
  return m.onGround && !m.sprinting && !m.sliding && !m.rolling && !m.mantling && !m.climbing && !m.flying && !m.gliding
      && !m.swimming && !m.inFluid && !m.mounting && !m.sitting && !m.sleeping;
}""")
M(mhk, r"""
public static boolean step(long[] s, boolean crouch, boolean ok, long now) {
  boolean was = s[0] != 0L;
  s[0] = crouch ? 1L : 0L;
  if (!crouch || was) return false;
  if (!ok) { s[1] = 0L; return false; }
  long gap = @PKG@.MenuCfg.HOTKEY_GAP_MS;
  long cd = @PKG@.MenuCfg.HOTKEY_COOLDOWN_MS;
  if (s[1] > 0L && now - s[1] >= 0L && now - s[1] <= gap && (s[2] == 0L || now - s[2] >= cd || now < s[2])) {
    s[1] = 0L;
    s[2] = now;
    return true;
  }
  s[1] = now;
  return false;
}""")
M(mhk, r"""
public static void prune() {
  java.util.Iterator it = new java.util.ArrayList(ST.keySet()).iterator();
  while (it.hasNext()) {
    Object k = it.next();
    try { if (!(k instanceof @REF@) || !((@REF@) k).isValid()) ST.remove(k); } catch (Throwable t) { ST.remove(k); }
  }
}""")
hko.addInterface(pool.get("java.lang.Runnable"))
F(hko, "public @PR@ pr;")
F(hko, "public static volatile long OPENED = 0L;")
F(hko, "public static volatile long REFUSED = 0L;")
C(hko, "public HotkeyOpen(@PR@ pr) { this.pr = pr; }")
M(hko, r"""
public static boolean wanted(java.util.UUID u) {
  if (u == null) return false;
  Boolean on = @PKG@.SetStore.get(u, @PKG@.MenuData.HOTKEY_KEY);
  return on == null || on.booleanValue();
}""")
M(hko, r"""
public static void refuse(@PR@ pr, String why) {
  REFUSED = REFUSED + 1L;
  String who = "?";
  try { who = pr.getUsername() + " (" + pr.getUuid() + ")"; } catch (Throwable t) { }
  @PKG@.MenuUtil.info("hub hotkey: " + who + " - " + why + ", not opened");
}""")
M(hko, r"""
public void run() {
  try {
    if (!@PKG@.MenuHotkey.ON || this.pr == null || !this.pr.isValid()) return;
    if (!wanted(this.pr.getUuid())) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    if (@PKG@.MenuUtil.profileBusy(this.pr.getUuid())) { refuse(this.pr, "a profile switch is running"); return; }
    @PGM@ pm = p.getPageManager();
    if (pm == null) return;
    Object cp = pm.getCustomPage();
    if (cp != null) { refuse(this.pr, "page " + cp.getClass().getSimpleName() + " is open"); return; }
    java.util.List ws = p.getWindowManager() == null ? null : p.getWindowManager().getWindows();
    if (ws != null && !ws.isEmpty()) { refuse(this.pr, ws.size() + " window(s) open (" + ws.get(0).getClass().getSimpleName() + ")"); return; }
    pm.openCustomPage(r, st, new @PKG@.MenuPage(this.pr, "main"));
    OPENED = OPENED + 1L;
  } catch (Throwable t) { @PKG@.MenuUtil.warn("the hub hotkey could not open the menu: " + t); }
}""")
M(mhk, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (!ON) return;
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null) return;
    @MSC@ msc = (@MSC@) store.getComponent(ref, @MSC@.getComponentType());
    if (msc == null) return;
    @MVS@ ms = msc.getMovementStates();
    if (ms == null) return;
    long[] s = (long[]) ST.get(ref);
    if (s == null) {
      if (!ms.crouching) return;
      s = new long[3];
      ST.put(ref, s);
    }
    if (!step(s, ms.crouching, still(ms), System.currentTimeMillis())) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    Object ext = store.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    FIRED = FIRED + 1L;
    w.execute(new @PKG@.HotkeyOpen(pr));
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.MenuUtil.warn("the hub hotkey check failed (logged once): " + t); }
  }
}""")

# ================= GrantTask: give the menu item once per profile (SkyyMenu-IO -> the player's world thread) =================
# 0.3.19 C: two steps. expected == null: on SkyyMenu-IO - the storage key + the file checks (Given.planFiles); nothing to do = done, else
# the key is kept and the task hops to the player's world thread. expected != null: on that world thread - the same key still active
# (else back to the file check), then count + give (Given.planHeld). Retries (1 s) go back to SkyyMenu-IO; 30 tries at most, as 0.3.18.
grt.addInterface(pool.get("java.lang.Runnable"))
F(grt, "public @PR@ pr;")
F(grt, "public @WLD@ expected;")
F(grt, "public int tries;")
F(grt, "public String key;")
C(grt, "public GrantTask(@PR@ pr) { this.pr = pr; this.expected = null; this.tries = 0; this.key = null; }")
M(grt, r"""
public boolean later(long ms) {
  this.expected = null;
  this.key = null;
  this.tries = this.tries + 1;
  if (this.tries >= 30) return false;
  return @PKG@.MenuIO.schedule(this, ms);
}""")
# 0 = given now, 1 = nothing to do, 2 = retry later, 3 = inventory full (retried next login) - the decision is Given.planHeld (the file part
# ran on SkyyMenu-IO for this.key); ONE storage key for the whole grant, compared here on the world thread, where a SkyyProfiles switch -
# one world task - can never be half done
M(grt, r"""
public int grantNow(java.util.UUID u) {
  String key = @PKG@.Given.key(u);
  if (this.key == null || !this.key.equals(key)) return 2;
  @PLA@ p = null;
  @REF@ r = this.pr.getReference();
  if (r != null && r.isValid()) {
    @ST@ st = r.getStore();
    if (st != null) p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
  }
  int held = p == null ? -1 : @PKG@.MenuUtil.count(p, @PKG@.MenuData.ITEM_ID);
  int d = @PKG@.Given.planHeld(u, key, held);
  if (d != 4) return d;
  if (@PKG@.MenuUtil.giveMenuItem(p)) {
    @PKG@.Given.markLater(key);
    this.pr.sendMessage(@MSG@.raw("[SkyWynn] You got the SkyWynn Menu! Right-click it (or double-tap crouch, if the Hub hotkey switch is on in /settings) to open teleports, your bags, skills, the bazaar and more. Lost it? Type /skymenu."));
    return 0;
  }
  this.pr.sendMessage(@MSG@.raw("[SkyWynn] Your inventory is full, so you did not get the SkyWynn Menu item. Make room and type /skymenu."));
  return 3;
}""")
# true = this task runs again (re-scheduled, or queued on the world thread); false = done (Given.PENDING is released by run)
M(grt, r"""
public boolean step(java.util.UUID u) {
  if (!@PKG@.Given.wants(u)) return false;
  if (this.expected == null) {
    String key = @PKG@.Given.key(u);
    int d = @PKG@.Given.planFiles(u, key);
    if (d == 1) return false;
    if (d != 4 || @PKG@.MenuUtil.profileBusy(u)) return later(1000L);
    java.util.UUID wu = this.pr.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null) return later(1000L);
    this.key = key;
    this.expected = w;
    w.execute(this);
    return true;
  }
  java.util.UUID wu2 = this.pr.getWorldUuid();
  @WLD@ now = wu2 == null ? null : @UNI@.get().getWorld(wu2);
  if (now != this.expected) return later(1000L);
  if (@PKG@.Given.INFLIGHT.putIfAbsent(u, Boolean.TRUE) != null) return false;
  int res = 2;
  try { res = grantNow(u); } catch (Throwable t) { @PKG@.MenuUtil.warn("menu item grant failed for " + u + ": " + t); res = 3; }
  @PKG@.Given.INFLIGHT.remove(u);
  if (res == 2) return later(1000L);
  return false;
}""")
M(grt, r"""
public void run() {
  java.util.UUID u = null;
  boolean again = false;
  try {
    if (this.pr != null) u = this.pr.getUuid();
    if (u != null && this.pr.isValid()) again = step(u);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu item grant task failed: " + t); }
  if (!again && u != null) {
    @PKG@.Given.PENDING.remove(u);
    // FIX ROUND: ended while the profile still wants its item (30 tries used up, no world, MenuIO refused): the profile watch looks again
    try { if (@PKG@.Given.wants(u)) @PKG@.Given.EPOCH.remove(u); } catch (Throwable t) { }
  }
}""")
# 0.3.4: ONE pending GrantTask per player, 4 s after the trigger (both triggers use it; the task decides on the world thread)
M(giv, r"""
public static boolean schedule(@PR@ pr, long ms) {
  try {
    if (pr == null || !claim(pr.getUuid(), System.currentTimeMillis())) return false;
    if (@PKG@.MenuIO.schedule(new @PKG@.GrantTask(pr), ms)) return true;
    PENDING.remove(pr.getUuid());
    return false;
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule the menu item grant: " + t); return false; }
}""")

# ================= MenuReady: PlayerReadyEvent (every world switch) -> GrantTask once per profile and session =================
rdy.addInterface(pool.get("java.util.function.Consumer"))
C(rdy, "public MenuReady() { }")
M(rdy, r"""
public void accept(Object ev) {
  try {
    if (@PKG@.MenuUtil.firstCheck()) { @PKG@.MenuUtil.checkAliases(); @PKG@.MenuUtil.checkSettingsCmd(); @PKG@.MenuUtil.checkAdminCmd(); @PKG@.MenuIdx.prime(); }
    @PRE@ e = (@PRE@) ev;
    @REF@ r = e.getPlayerRef();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.SetLoadTask.preload(pr);
    @PKG@.SoundSw.ready(pr.getUuid());   // 0.3.25
    @PKG@.MenuHub.ensure(pr.getUuid());   // 0.3.28: hub:last:<uuid> (memory only)
    @PKG@.MenuLayout.preload(pr.getUuid());
    java.util.UUID u = pr.getUuid();
    @PKG@.Given.READY.put(u, Boolean.TRUE);
    if (!@PKG@.Given.wants(u)) return;
    @PKG@.Given.schedule(pr, 4000L);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("ready handler failed: " + t); }
}""")

# ================= GivenTick (0.3.4): the profile watch - a profile switch or a new profile (SkyyProfiles flips profile:fn:key) needs no
# world switch to give that profile its menu item. Every 2 s, only while SkyyProfiles is loaded (without it the key never changes and
# PlayerReadyEvent covers everything), only for players past their first PlayerReadyEvent (the join path schedules those): a player whose
# CURRENT storage key has no session mark gets ONE GrantTask (Given.schedule / claim).
# 0.3.19 D: SkyyProfiles bumps profile:epoch:<uuid> on every switch and every new profile (tools/PROFILES-CONTRACT.md rule 3), so the key
# function (wants) is asked only when that value changed since the last tick (Given.EPOCH; the first tick of a player counts as a change);
# no epoch published = 0.3.18's check every tick. Runs on SkyyMenu-IO (0.3.18: the shared scheduler). FIX ROUND: a schedule that is
# refused (a task still pending) forgets EPOCH[u], so the next tick looks again (GrantTask.run does the same when it ends unfinished).
gtk.addInterface(pool.get("java.lang.Runnable"))
C(gtk, "public GivenTick() { }")
M(gtk, r"""
public void run() {
  try {
    java.util.Map br = @PKG@.MenuUtil.bridge();
    if (!(br.get("profile:fn:key") instanceof java.util.function.Function)) return;
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      if (!@PKG@.Given.READY.containsKey(u)) continue;
      Object e = br.get("profile:epoch:" + u.toString());
      if (e != null) {
        Object was = @PKG@.Given.EPOCH.put(u, e);
        if (e.equals(was)) continue;
      }
      if (!@PKG@.Given.wants(u)) continue;
      if (!@PKG@.Given.schedule(pr, 4000L)) @PKG@.Given.EPOCH.remove(u);
    }
  } catch (Throwable t) { }
}""")

# ================= SeenTick: forget players who logged out (SkyyIslands SeenTick pattern) =================
seen.addInterface(pool.get("java.lang.Runnable"))
C(seen, "public SeenTick() { }")
M(seen, r"""
public void run() {
  java.util.HashSet online = new java.util.HashSet();
  java.util.HashSet onlineK = new java.util.HashSet();
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr != null && pr.isValid()) { online.add(pr.getUuid()); onlineK.add(pr.getUuid().toString()); }
    }
    @PKG@.Given.retainOnline(online, onlineK);
    @PKG@.Tips.LEGACY.keySet().retainAll(online);
  } catch (Throwable t) { return; }
  try {
    @PKG@.SetStore.retryDirty();
    @PKG@.SetStore.pruneOffline(onlineK);
    @PKG@.MenuLayout.flushAll();
    @PKG@.MenuLayout.pruneOffline(onlineK);
    @PKG@.SetReg.loadAdmin(false);
    @PKG@.SoundSw.sweep(online);   // 0.3.25
    @PKG@.MenuHub.sweep(online);   // 0.3.28: hub:last of players who left
  } catch (Throwable t) { @PKG@.MenuUtil.warn("settings upkeep failed: " + t); }
  try { @PKG@.MenuHotkey.prune(); } catch (Throwable t) { }
}""")

# ================= MenuQuit: PlayerDisconnectEvent -> drop the session guard at once (SkyyClasses ClassQuit pattern) =================
# grantNow() sets SESSION before it tries the inventory, so a full inventory is not re-tried (and re-messaged) on every world switch.
# Clearing it on disconnect makes "retried on the next login" exact even for a reconnect inside SeenTick's 30 s window.
quit_.addInterface(pool.get("java.util.function.Consumer"))
C(quit_, "public MenuQuit() { }")
M(quit_, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDE@) ev).getPlayerRef();
    if (pr == null) return;
    @PKG@.Given.forget(pr.getUuid());
    @PKG@.PageGuard.JOINS.remove(pr.getUuid());
    @PKG@.SoundSw.forget(pr.getUuid());   // 0.3.25
    @PKG@.MenuHub.forget(pr.getUuid());   // 0.3.28: hub:last:<uuid> goes with the player
  } catch (Throwable t) { }
}""")

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
F(pl, "public java.util.concurrent.ScheduledFuture watch;")
C(pl, "public SkyyMenuPlugin(%s init) { super(init); }" % JPI)
M(pl, r"""
public void setup() {
  @PKG@.PageGuard.STOP = false;
  @PKG@.PageGuard.EXEC = @HSV@.SCHEDULED_EXECUTOR;
  @PKG@.MenuIO.begin();
  @PKG@.MenuHotkey.ON = true;
  @PKG@.MenuUtil.LOG = getLogger();
  @PKG@.Given.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("given-profile");
  @PKG@.Given.LEGACY = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("given");
  @PKG@.Tips.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("notips");
  @PKG@.PetTile.DIR = getDataDirectory().resolveSibling("Skyy_SkyyPets").resolve("pets");
  @PKG@.SetStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("settings");
  @PKG@.MenuLayout.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("layouts");
  @PKG@.MenuLayout.DEF_FILE = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("layout-default.properties");
  @PKG@.MenuLayout.loadDefault();
  @PKG@.SetReg.ADMIN_FILE = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("settings-defaults.properties");
  @PKG@.SetReg.loadAdmin(true);
  @PKG@.MenuCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("config.properties");
  @PKG@.MenuCfg.init();
  @PKG@.AdmSaveTask.BASE = getDataDirectory().resolveSibling("Skyy_SkyyMenu");
  @PKG@.AdmSaveTask.ensureDirs();
  java.util.Map br = @PKG@.MenuUtil.bridge();
  br.put("settings:fn:register", new @PKG@.SetRegFn());
  br.put("settings:fn:get", new @PKG@.SetGetFn());
  br.put("settings:fn:set", new @PKG@.SetSetFn());
  @PKG@.SetReg.registerOwn();
  @PKG@.SetReg.drain();
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
  try {
    java.nio.file.Path kh = @PKG@.CfgRows.HOME == null ? null : @PKG@.CfgRows.HOME.toAbsolutePath().normalize();
    java.nio.file.Path kb = @PKG@.AdmSaveTask.BASE == null ? null : @PKG@.AdmSaveTask.BASE.toAbsolutePath().normalize();
    java.nio.file.Path km = @PKG@.CfgRows.MODS == null ? null : @PKG@.CfgRows.MODS.getFileName();
    if (kh != null && kh.equals(kb) && km != null && "mods".equalsIgnoreCase(km.toString())) @PKG@.MenuUtil.info("config kit folder: " + kh + " (config-history, config-changes.log)");
    else @PKG@.MenuUtil.warn("config kit folder is " + kh + " but SkyyMenu uses " + kb + " - the kit's mods folder is wrong, tell the developer");
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not check the config kit folder: " + t); }
  @OCU@.registerSimple(this, @PKG@.SkyyMenuPlugin.class, @PKG@.MenuData.PAGE_ID, new @PKG@.MenuPageFactory());
  getCommandRegistry().registerCommand(new @PKG@.MenuCmd());
  getCommandRegistry().registerCommand(new @PKG@.SettingsCmd());
  getCommandRegistry().registerCommand(new @PKG@.AdminCmd());
  // 0.3.24: /soundtest - a clash with another mod's /soundtest is logged and the menu still loads
  try { getCommandRegistry().registerCommand(new @PKG@.SoundTestCmd()); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /soundtest (another mod may own it): " + t); }
  // 0.3.10: /stats (/profilestats) - a clash with another mod's /stats is logged and the menu still loads
  try { getCommandRegistry().registerCommand(new @PKG@.StatsCmd()); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /stats (another mod may own it) - the Your Profile tile still opens the Stats page: " + t); }
  // 0.3.28: hubs H2 - the registry (hub:def:* + Menu's own tabs) and the hub commands (a clash is logged and the menu still loads)
  int hubTabs = @PKG@.MenuHub.register();
  int hubCmds = 0;
  try { getCommandRegistry().registerCommand(new @PKG@.HubCharCmd()); hubCmds = hubCmds + 1; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /character (another mod may own it): " + t); }
  try { getCommandRegistry().registerCommand(new @PKG@.HubStorageCmd()); hubCmds = hubCmds + 1; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /storage (another mod may own it): " + t); }
  try { getCommandRegistry().registerCommand(new @PKG@.HubMarketCmd()); hubCmds = hubCmds + 1; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /market (another mod may own it): " + t); }
  try { getCommandRegistry().registerCommand(new @PKG@.HubTravelCmd()); hubCmds = hubCmds + 1; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /travel (another mod may own it): " + t); }
  try { getCommandRegistry().registerCommand(new @PKG@.HubSocialCmd()); hubCmds = hubCmds + 1; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /social (another mod may own it): " + t); }
  try { getCommandRegistry().registerCommand(new @PKG@.HubCraftCmd()); hubCmds = hubCmds + 1; }   // 0.3.31
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /crafting (another mod may own it): " + t); }
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.MenuReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.MenuQuit());
  getEventRegistry().registerGlobal(@ATW@.class, new @PKG@.PageGuard());
  // 0.3.19: the 30 s upkeep (file writes) and the profile watch run on SkyyMenu-IO (0.3.18: the shared HytaleServer scheduler)
  this.ticker = @PKG@.MenuIO.every(new @PKG@.SeenTick(), 30000L, 30000L);
  this.watch = @PKG@.MenuIO.every(new @PKG@.GivenTick(), 5000L, 2000L);
  // 0.3.19 G: the hub hotkey (double-tap crouch) - a clash is logged and the menu still loads
  try { getEntityStoreRegistry().registerSystem(new @PKG@.MenuHotkey()); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register the hub hotkey (double-tap crouch) - the menu item and /skymenu still work: " + t); }
""" + LIFE["setup"] + r"""  getLogger().at(java.util.logging.Level.INFO).log("[SkyyMenu] """ + VERSION + r""" ready (config kit " + @PKG@.MenuData.CFG_KIT + ") - /skymenu""" + "".join(" /" + a for a in ALIASES) + r""", right-click the SkyWynn Menu item or double-tap crouch; the item is given once per profile; /settings (/skysettings): " + @PKG@.SetReg.DEFS.size() + " switch(es) registered so far; Server Setup: /modconfig (/serversetup) for admins, /soundtest (" + @PKG@.SoundTest.IDS.length + " sounds listed); Stats page: the Your Profile tile, /stats (/profilestats), page look """ + SUI_KIT_ID + r"""; hubs: " + hubTabs + " own tabs, " + hubCmds + " of 6 hub commands (/character /char /storage /market /crafting /travel /social), Sky Window kit textures shipped; Home + Edit shortcuts (5 x 5 grid, big row 1, " + @PKG@.MenuLayout.MIGRATIONS + " + " + @PKG@.MenuLayout.FOLDS + " layout update(s) at start), " + @PKG@.MenuHub.PROXIES + " stand-in hub tab(s) (Smithing " + (@PKG@.MenuUtil.cmd("smithing") != null ? "opens /smithing" : "has no /smithing") + "); page guard on (a page left open across a world change is forgotten at the join, no packet; the menu heals stuck page clicks); " + @PKG@.MenuOnce.statusText());
}""")
M(pl, r"""
protected void shutdown() {
  @PKG@.PageGuard.STOP = true;
  @PKG@.MenuHotkey.ON = false;
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { if (this.watch != null) this.watch.cancel(false); } catch (Throwable t) { }
  try { @PKG@.MenuIO.stop(2000L); } catch (Throwable t) { @PKG@.MenuUtil.warn("SkyyMenu-IO stop failed: " + t); }
  try { @PKG@.SetStore.flushAll(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings flush at shutdown failed: " + t); }
  try { @PKG@.SoundSw.clearAll(); } catch (Throwable t) { }   // 0.3.25
  try { @PKG@.MenuHub.clearAll(); } catch (Throwable t) { }   // 0.3.28: hub:def / Menu's tabs / hub:last off the bridge
  try { @PKG@.MenuLayout.flushAll(); } catch (Throwable t) { @PKG@.MenuUtil.warn("menu layout flush at shutdown failed: " + t); }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { @PKG@.MenuUtil.warn("config kit flush at shutdown failed: " + t); }
""" + LIFE["shutdown"] + r"""  super.shutdown();
}""")

WRITE = (dat, utl, giv, mcfg, sreg, sst, ssv, tip, sld, sgf, srf, ssf, sdc, page, spg, apg, ast, ref_, clo_, guard, stale, mwat, fac, cmd, scmd, acmv, acmd, grt, rdy, seen, quit_, gtk,
         scl, stp, sta, stc, pet, lay, lsv, spt, mio, midx, gsv, mhk, hko, ops, snt, stv, stm, ssw,
         hubb, mhub, mho, mhv, hcch, hcst, hcmk, hctr, hcso, hccr, mal, mvo, mvv, mhh, pl)   # 0.3.28: the hub classes; 0.3.29: MenuAlert; 0.3.30: MenuVt*; 0.3.33: HubHide
assert len(WRITE) == len(MADE) and all(any(c is w for w in WRITE) for c in MADE), "a pool.makeClass result is missing from the writeFile list"
for c in WRITE:
    c.writeFile(OUT)
for c in LIFE["classes"]:   # 0.3.32: the lifelong menu item (tools/skyyonce.py)
    c.writeFile(OUT)
# 0.3: the config kit checks its hooks (SetDefCfg, MenuCfg.load) and writes its 7 classes
KIT.write(OUT)
for c in list(MADE) + list(KIT.classes):
    _cf = os.path.join(OUT, *str(c.getName()).split(".")) + ".class"
    assert os.path.isfile(_cf), "class file not written: " + _cf
print("classes written:", len(WRITE), "+ config kit", len(KIT.classes))

# ================= post-build check: every inline UI string in the compiled MenuData class is intact =================
_md = open(os.path.join(OUT, "com", "skyy", "menu", "MenuData.class"), "rb").read()
_consts = cp_utf8(_md)
for s in list(UI.values()) + UI_INFO + SET_UI_ALL + ADM_UI_ALL:
    assert s in _consts, "inline UI string missing from MenuData.class: " + s[:80]
print("inline UI strings verified in MenuData.class:", len(UI) + len(UI_INFO) + len(SET_UI_ALL) + len(ADM_UI_ALL))
# 0.3.17: the editor's texts (Skyy's no-dragging rule) are in the compiled MenuData class
for _k, _v in EDIT_TXT.items():
    assert _v in _consts, "0.3.17: editor text %s missing from MenuData.class" % _k
print("0.3.17 editor texts verified in MenuData.class:", len(EDIT_TXT))
# 0.3.10: the Stats page's fixed kit markup is intact in StatsPage.class
_sp = cp_utf8(open(os.path.join(OUT, "com", "skyy", "menu", "StatsPage.class"), "rb").read())
for _m in ST_STATIC:
    assert _m in _sp, "stats page markup missing from StatsPage.class: " + _m[:80]
print("stats page markup verified in StatsPage.class:", len(ST_STATIC), "fixed parts")
print("server setup: node %s, /%s /%s, SkyyMenu config rows: %s" % (ADMIN_NODE, ADMIN_CMD, ADMIN_ALIAS, ", ".join(r[0] for r in MENU_CFG_ROWS)))
print("settings: %d known keys (%d tabs), own: %s, template %d bytes" % (len(SET_ORDER), len(SET_TABS), ", ".join(k[0] for k in OWN_SETTINGS), len(SET_TEMPLATE)))

# ================= assets: the menu item + its name / description =================
item = {
    "TranslationProperties": {"Name": "server.items.%s.name" % MENU_ITEM_ID, "Description": "server.items.%s.description" % MENU_ITEM_ID},
    "Categories": ["Items.Tools"],
    "Icon": MENU_ITEM_FIELDS["Icon"],                # 0.3.15: our own emblem (was the Voidheart's)
    "Quality": MENU_ITEM_QUALITY,
    "Tags": {"Type": ["Utility"]},
    "MaxStack": 1,
    "Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": PAGE_ID}}]}},
}
for k in VISUAL_KEYS:                                # 0.3.15: the fixed fields, in 0.3.14's key order (no key added or lost)
    if k in MENU_ITEM_FIELDS:
        item[k] = MENU_ITEM_FIELDS[k]
assert set(item) == set(["TranslationProperties", "Categories", "Quality", "Tags", "MaxStack", "Interactions"]) | set(MENU_ITEM_FIELDS) \
    and set(MENU_ITEM_FIELDS) == set(VISUAL_KEYS + ("Icon",)) - set(["ItemSoundSetId"]), "0.3.15: the menu item = 0.3.14's keys"
lang = [
    "items.%s.name=%s" % (MENU_ITEM_ID, MENU_ITEM_NAME), "server.items.%s.name=%s" % (MENU_ITEM_ID, MENU_ITEM_NAME),
    "items.%s.description=%s" % (MENU_ITEM_ID, MENU_ITEM_DESC), "server.items.%s.description=%s" % (MENU_ITEM_ID, MENU_ITEM_DESC),
]
files = {
    "Server/Item/Items/Utility/%s.json" % MENU_ITEM_ID: json.dumps(item, indent=2),
    "Server/Languages/en-US/server.lang": "\n".join(lang) + "\n",
}
# 0.3.15: the emblem's three files (the art manifest's bytes), at their Common/ path
for _f in MENU_ART_FILES:
    assert "Common/" + MENU_ITEM_FIELDS[_f] not in files
    files["Common/" + MENU_ITEM_FIELDS[_f]] = menu_art_file(_f)
print("menu item:", MENU_ITEM_ID, "own emblem look (%s):" % MENU_ART_DIR, ", ".join("%s %s (%d bytes)" % (_f, MENU_ITEM_FIELDS[_f],
      len(files["Common/" + MENU_ITEM_FIELDS[_f]])) for _f in MENU_ART_FILES), "- glow", MENU_ITEM_FIELDS["Light"]["Color"])
# 0.3.11: the icon-only items (hidden from the creative library) + their pictures + names
ICON_KEYS = ("Model", "Texture", "Scale", "PlayerAnimationsId", "ItemSoundSetId")   # the held look only (the Icon is ours)
for _iid in sorted(ICON_ITEMS):
    _art, _rel, _man, _nm, _lk = ICON_ITEMS[_iid]
    _lkd = look_of(_lk)
    _node = {"TranslationProperties": {"Name": "server.items.%s.name" % _iid}, "Icon": _rel, "Variant": True, "MaxStack": 1}
    for _k in ICON_KEYS:
        if _k in _lkd:
            _node[_k] = _lkd[_k]
    assert "Model" in _node and "Texture" in _node and "Categories" not in _node and "Recipe" not in _node and "Interactions" not in _node
    _p = "Server/Item/Items/Utility/%s.json" % _iid
    assert _p not in files and "Common/" + _rel not in files
    files[_p] = json.dumps(_node, indent=2)
    files["Common/" + _rel] = icon_item_png(_iid)
    lang.extend(["items.%s.name=%s" % (_iid, _nm), "server.items.%s.name=%s" % (_iid, _nm)])
    print("icon item:", _iid, "icon", _rel, "(%d bytes, %s)" % (len(files["Common/" + _rel]), _art), "held look of", _lk, "- hidden from the creative library")
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"
assert [e[2] for e in ENTRIES if e[0] == "main" and e[1] == 5] == [ICON_BAG], "0.3.11: the Accessory Bag tile uses our icon item (0.3.16: slot 5)"
# 0.3.14: the Pets tile, /pets (0.3.16: slot 3, Your Profile 33); every pet icon item shipped
assert [(e[3], e[6]) for e in ENTRIES if e[0] == "main" and e[1] in (3, 33)] == [("Your Profile", "profile"), ("Pets", "cmdc:pets")], "0.3.16: Pets at main 3, Profile 33"
assert all(("Skyy_Menu_Icon_Pet_" + _p) in ICON_ITEMS for _p in PET_ART) and \
    len(ICON_ITEMS) == 1 + len(PET_ART) + len(MENU_ICONS) - 1 + len(MENU_ICONS_2) + len(MENU_ICONS_3) + len(MENU_ICONS_W) + 1, \
    "0.3.14: the pet icon items (0.3.16: + 22 tile icon items; 0.3.26: + the 14 wave-1 icons)"
# 0.3.26: every wave-1 icon ships (item JSON + PNG = art/menu-icons-2 byte for byte, manifest sha256 + bytes), the manifest lists exactly
# MENU_ICONS_2 (same id, label and replaced vanilla id), and no menu spot of this wave still names the vanilla id it replaced
_m2 = json.load(open(os.path.join(HERE, "..", *(MENU_ICON_DIR_2 + "/manifest.json").split("/")), encoding="utf8"))
assert [(i["name"], i["id"], i["label"], i["replaces_vanilla_id"]) for i in _m2["icons"]] == \
    [(n, "Skyy_Menu_Icon_" + n, l, w) for n, l, w in MENU_ICONS_2], "0.3.26: MENU_ICONS_2 = art/menu-icons-2/manifest.json icons"
for _nm, _lab, _was in MENU_ICONS_2:
    _iid = "Skyy_Menu_Icon_" + _nm
    _rel = ICON_ITEMS[_iid][1]
    _png = files["Common/" + _rel]
    _me = [f for f in _m2["files"] if f["path"] == "Common/" + _rel]
    assert len(_me) == 1 and hashlib.sha256(_png).hexdigest() == _me[0]["sha256"] and len(_png) == _me[0]["bytes"], "0.3.26: %s = the art file" % _iid
    _js = json.loads(files["Server/Item/Items/Utility/%s.json" % _iid])
    assert _js["Icon"] == _rel and _js["Variant"] is True and "Categories" not in _js and "Recipe" not in _js and "Interactions" not in _js
    assert _iid not in ITEMS and "Common/" + _rel not in COMMON, "0.3.26: %s clashes with a vanilla item / file" % _iid
    assert ("server.items.%s.name=%s" % (_iid, _lab)) in lang, "0.3.26: %s has its name" % _iid
_W1 = dict([(("tp", 11), "MyIsland"), (("tp", 13), "Hub"), (("tp", 15), "Spawn"), (("players", 47), "Accept"), (("players", 51), "Deny")])
# 0.3.27: (("main", 11), "Shards") left with the tile; the icon item Skyy_Menu_Icon_Shards still ships (hidden, never held)
_W1 = dict(((_k, "Skyy_Menu_Icon_" + _v) for _k, _v in _W1.items()))
assert dict(((e[0], e[1]), e[2]) for e in ENTRIES if (e[0], e[1]) in _W1) == _W1, "0.3.26: the wave-1 ENTRIES wear our icons"
assert [a[1] for a in PLAYER_ACTIONS if a[0] in (28, 29, 30)] == ["Skyy_Menu_Icon_Hub", "Skyy_Menu_Icon_Spawn", "Skyy_Menu_Icon_MyIsland"]   # 0.3.30: one slot left
# fix 2: the player-page ACTIONS are buttons, not pages (never in + Add / Home / row 1). Only 0.3.26's three teleport actions wear the icon
# of the page they belong to (on purpose); every other action wears a vanilla item, never a Menu page icon (Invite to Guild = a banner)
assert not [a for a in PLAYER_ACTIONS if a[0] not in (28, 29, 30) and a[1].startswith("Skyy_Menu_Icon_")], "0.3.30: an action wears a page icon"
_chrome = (ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_WARP_LOCKED, ICON_NO_WARPS, ICON_PLAYER)
assert all(_c in ICON_ITEMS and _c not in ITEMS for _c in _chrome) and len(set(_chrome)) == len(_chrome), "0.3.26: the chrome icons are ours"
_was = set(w for _n, _l, w in MENU_ICONS_2)
assert not [_v for _v in list(_W1.values()) + list(_chrome) + [a[1] for a in PLAYER_ACTIONS if a[0] in (28, 29, 30)] if _v in _was], "0.3.26: a vanilla id left"
print("0.3.26 wave-1 icons:", len(MENU_ICONS_2), "icon items from", MENU_ICON_DIR_2, "-", ", ".join(n for n, _l, _w in MENU_ICONS_2))
# 0.3.16: every approved tile icon ships: the item JSON + the PNG at its art path, = art/menu-icons byte for byte; the bag = 0.3.11's file
import hashlib as _hl
_mman = json.load(open(os.path.join(HERE, "..", *(MENU_ICON_DIR + "/manifest.json").split("/")), encoding="utf8"))
assert sorted(t["name"] for t in _mman["tiles"]) == sorted(n for n, _t in MENU_ICONS) and \
    all(t["item_id"] == "Skyy_Menu_Icon_" + t["name"] and dict(MENU_ICONS)[t["name"]] == {"Accessory Bag": "Void Charms"}.get(t["tile"], t["tile"])
        for t in _mman["tiles"]), "0.3.16: the 23 approved icons (0.3.38: the bag tile is called Void Charms)"
for _nm, _tile in MENU_ICONS:
    _iid = "Skyy_Menu_Icon_" + _nm
    if _nm == "AccessoryBag":   # 0.3.37: the Void Charms item shows the approved amulet (art/void-charms-icon, checked by icon_item_png)
        continue
    _png = files["Common/" + ICON_ITEMS[_iid][1]]
    _art = open(os.path.join(HERE, "..", *(MENU_ICON_DIR + "/Common/Icons/ItemsGenerated/%s.png" % _iid).split("/")), "rb").read()
    _me = [f for f in _mman["files"] if f["path"] == "Common/Icons/ItemsGenerated/%s.png" % _iid]
    assert len(_me) == 1 and _png == _art and _hl.sha256(_png).hexdigest() == _me[0]["sha256"] and len(_png) == _me[0]["bytes"], \
        "0.3.16: %s's picture = art/menu-icons byte for byte (manifest sha256 + bytes)" % _iid
    _js = json.loads(files["Server/Item/Items/Utility/%s.json" % _iid])
    assert _js["Icon"] == ICON_ITEMS[_iid][1] and _js["Variant"] is True and "Categories" not in _js and "Recipe" not in _js
    assert "Server/Item/Items/Utility/%s.json" % _iid not in ASSETS.namelist() and "Common/" + ICON_ITEMS[_iid][1] not in COMMON, "0.3.16: no vanilla clash"
print("0.3.16 tile icons:", len(MENU_ICONS), "approved icons (22 new icon items + the 0.3.11 bag); layout D:", ", ".join(
    "%s %d" % (t, MAIN_D[t][0] * 9 + MAIN_D[t][1]) for t in sorted(MAIN_D, key=lambda t_: MAIN_D[t_][0] * 9 + MAIN_D[t_][1])))
print("0.3.16 tile rules:", "; ".join("%s %s" % (t, TILE_RULES[t]) for t in sorted(TILE_RULES)))
assert all(files["Common/Icons/ItemsGenerated/SkyyMenu_Pet_%s.png" % _p] for _p in PET_ART), "0.3.14: the pet icons are in the jar"
# 0.3.15: the menu item wears the emblem; the Mods row shows it; nothing names the Voidheart any more
assert json.loads(files["Server/Item/Items/Utility/%s.json" % MENU_ITEM_ID])["Model"] == MENU_ITEM_FIELDS["Model"], "0.3.15: the item JSON"
assert [m["icon"] for m in MODS if m["mod"] == "SkyyMenu"] == [MENU_ITEM_ID], "0.3.15: the Mods row icon"
assert "Voidheart" not in json.dumps(item) and not [m for m in MODS if "Voidheart" in m["icon"]], "0.3.15: no Voidheart look left"
print("entries:", len(ENTRIES), "player actions:", len(PLAYER_ACTIONS), "mods:", len(MODS),
      "(%d with a Server Setup page, %d with admin-only lines)" % (len([m for m in MODS if "setup" in m]), len([m for m in MODS if m.get("admin")])))

# 0.3.1: the kit source must still be the one this build emitted (an edit landing during the build fails it: build again)
assert kit_blob(KIT_FILE) == KIT_BLOB, "tools/skyycfg.py changed during this build (blob %s -> %s) - build again" % (KIT_BLOB[:12], kit_blob(KIT_FILE)[:12])
# 0.3.28: the Sky Window kit art - all 59 files, byte-identical in every hub jar (sha256-pinned by the kit; HUBS-CONTRACT 2.7), under
# Common/UI/Custom/SkyyKit/ only (a texture outside Common/UI/Custom disconnects the client - probe k1b, 2026-10-15)
_kit = SUI.kit_texture_files()
assert len(_kit) == len(SUI.SKY_FILES) == 59 and all(p.startswith("Common/UI/Custom/SkyyKit/") and ".." not in p for p in _kit), "0.3.28: the kit art"
assert not set(_kit) & set(files), "0.3.28: a kit file clashes with a file of this jar"
files.update(_kit)
print("0.3.28 kit art:", len(_kit), "files under Common/UI/Custom/SkyyKit/ (%d bytes)" % sum(len(v) for v in _kit.values()))
# 0.3.30: the hub tab icons (art/hub-tab-icons, manifest sha256 + bytes) at the kit 1.6 hook path - SkyyHubTabs/<hub>_<tab>(_on)@2x.png
_tabart = {}
for _st in TAB_ART:
    _h, _t = _st.split("_", 1)
    _pp = SUI.hub_tab_icon_paths(_h, _t)
    for _fn, _jp in (("%s.png" % _st, _pp[2]), ("%s_on.png" % _st, _pp[3])):
        if _st in TAB_ART_OVER:      # 0.3.37: the Void Charms amulet pair
            _odir, _om = TAB_ART_OVER[_st]
            _data = open(os.path.join(HERE, "..", *(_odir + "/hub-tab/" + _fn).split("/")), "rb").read()
            _me = [f for f in _om["files"] if f["path"] == "hub-tab/" + _fn]
        else:
            _data = open(os.path.join(HERE, "..", *(TAB_ART_DIR + "/" + _fn).split("/")), "rb").read()
            _me = [f for f in _TAM["files"] if f["path"] == _fn]
        assert len(_me) == 1 and hashlib.sha256(_data).hexdigest() == _me[0]["sha256"] and len(_data) == _me[0]["bytes"], "0.3.30: %s = its manifest entry" % _fn
        assert _jp.startswith("Common/UI/Custom/SkyyHubTabs/") and _jp.endswith("@2x.png") and _jp not in files and _jp not in COMMON
        _tabart[_jp] = _data
files.update(_tabart)
print("0.3.30 hub tab icons:", len(_tabart), "files under Common/UI/Custom/SkyyHubTabs/ (%d bytes)" % sum(len(v) for v in _tabart.values()))
jar = os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyyMenu", VERSION, "SkyWynn menu (Hypixel SkyBlock style): right-click the SkyWynn Menu item or /skymenu for teleports and warps, island menu, Pocket Dimension, Vault, Void Charms, HUD editor, crafting, skills, collections, bazaar, auction house, bank, reforge, identify, players, party, guild, your Stats page (/stats), a list of every mod with its commands, /settings (every mod's chat messages on or off, per player) and Server Setup for admins (/modconfig: every Skyy mod's settings in game). Zero dependencies.", PKG + ".SkyyMenuPlugin"), OUT, files)
# 0.3.28: the built jar carries the full kit set, byte for byte, and no SkyyKit file outside the custom root (silent: the build ends with
# the "assembled" line)
assert SUI.check_jar_kit(jar, need=("Header", "HeaderOrnament", "Tab", "Tab_Selected", "Close", "Frame", "Frame_Character", "Frame_World",
                                     "Frame_Social", "Tertiary")) == 59, "0.3.28: the jar's kit art"
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyMenu.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyMenu" % VERSION, disable_prefix="Skyy:")
