"""SkyyMenu 0.1 - build script (javassist via jpype).
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
 - Item Skyy_Menu ("SkyWynn Menu", Ingredient_Voidheart look, glows): right-click -> OpenCustomUI page "SkyyMenu"
   (item JSON Interactions.Secondary + OpenCustomUIInteraction.registerSimple, the SkyySacks / SkyyAccessories pattern).
 - Given once per player: PlayerReadyEvent (fires on EVERY world switch) -> in-memory once-per-session guard -> GrantTask polls
   until the player's world resolves, re-runs itself on that world's thread (world.execute, SkyySacks GrantTask pattern), skips
   if the player already holds the item, puts it in the LAST hotbar slot if free (Hypixel slot 9), else hotbar / storage /
   backpack, count-verified. Persisted flag = Skyy_SkyyMenu/given/<uuid>.txt (atomic tmp + move) so it is never re-given
   after a restart. Inventory full -> message, retried on the next login (PlayerDisconnectEvent clears the session guard).
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

VERSION = "0.3"
HERE = os.path.dirname(os.path.abspath(__file__))

# =====================================================================================================================
# ================================================  MENU DATA (edit me)  ==============================================
# =====================================================================================================================
# Text rules: no double quotes, braces, semicolons or backslashes. Write command arguments as <player> - they are shown as
# [player] because < > is tooltip markup. Each entry's text is a list of lines: the FIRST line is the description paragraph,
# the others are detail lines. Slots: 0-53, row by row (9 per row, 6 rows). Row 5: 45 = Back, 48 = Prev, 49 = Close, 50 = Next.
#
# Actions:  view:<main|tp|players|mods>  open a submenu                   cmdc:<command line>  run it, then close the menu (a page
#           cmd:<command line>  run it, keep the menu open (refreshes)         command simply replaces the menu)
#           profile  show your stats in the info box                      info   just show the text in the info box
#           spawn  teleport to the main world spawn                       tips   switch this player's hover tooltips on / off
#           settings  open the player Settings page (0.2, same as /settings)
#           admin  open Server Setup (0.3; only admins see this entry - players never do)

MENU_ITEM_ID = "Skyy_Menu"
MENU_ITEM_NAME = "SkyWynn Menu"
MENU_ITEM_LOOK = "Ingredient_Voidheart"      # vanilla item whose model / texture / icon / glow the menu item copies (not a backpack)
MENU_ITEM_QUALITY = "Epic"
MENU_ITEM_DESC = ("Right-click to open the SkyWynn Menu: teleports, your island menu, bags, vault, the HUD editor, skills, the bazaar, "
                  "the auction house, the bank, reforging, your party and guild, your settings and a list of every mod with its commands."
                  "\\n\\nLost it? Type /skymenu to get a new one.")
PAGE_ID = "SkyyMenu"                          # OpenCustomUI page id used by the item

ICON_BACK   = "Weapon_Arrow_Iron"
ICON_PREV   = "Weapon_Arrow_Crude"
ICON_NEXT   = "Weapon_Arrow_Iron"
ICON_CLOSE  = "Furniture_Flag_Small_Red"      # red flag with a white X (vanilla Barrier's icon is an empty wireframe cube)
ICON_WARP   = "Tool_Map"
ICON_PLAYER = "Armor_Leather_Light_Head"
FILLER_ICON = None                            # None = empty grid slots; e.g. "Editor_Empty" for a Hypixel glass-pane look

USE_MARKUP  = True                            # tooltip footer colors (<color is=...>); set False if raw tags show in game
FOOT_COLOR  = "#ffff55"
DIM_COLOR   = "#ff5555"

# (view, title, intro lines) - the intro fills the info box until something is clicked
VIEWS = [
    ("main",    "SkyWynn Menu",   ["Everything the server adds, in one place. Hover an item to read about it and click it to use it.",
                                   "Lost your menu item? Type /skymenu to get a new one."]),
    ("tp",      "Teleport",       ["Your island, the hub, the server spawn and every warp that has been set.",
                                   "Admins add warps with /warp set <name>."]),
    ("players", "Players Online", ["Click a player to send a teleport request, visit their island or invite them to your party.",
                                   "Teleport requests you receive can be accepted or denied at the bottom."]),
    ("player",  "Player",         ["What do you want to do with this player?"]),
    ("mods",    "Mods",           ["Every SkyWynn mod, what it does and all of its commands.",
                                   "Click a mod to show its commands here - hovering shows the same text."]),
]

# (view, slot, icon item id, name, text lines, tooltip footer or None, action)
ENTRIES = [
    # ---- main menu. Row 1 = Skyy's order (Teleport, Pocket Dimension, Accessory Bag, HUD editor, then the rest), row 2 = your island +
    # your stuff, row 3 = people, row 4 = the mod list; top right = the per-player tooltip switch (0.1.3 layout)
    ("main", 4,  "Armor_Iron_Head", "Your Profile", ["Your coins, bank, skill levels and accessories."], "Click to show your stats above", "profile"),
    ("main", 8,  "Deco_Book_Pile_Small", "Hover Tooltips",
        ["Switch the pop-up text of this menu on or off (saved for you).",
         "Off: nothing pops up when you hover an item. Click an item to use it",
         "and read what it does in this box.",
         "The same switch is in Settings (/settings, General tab)."], "Click to switch", "tips"),
    ("main", 10, "Instance_Gateway", "Teleport", ["Travel to your island, the hub, the server spawn and every warp that is set."], "Click to open!", "view:tp"),
    ("main", 11, "Ingredient_Void_Essence", "Pocket Dimension",
        ["Everything your Magic Bags swept up lives here. Pick items up or deposit them.",
         "Carry a bag to use its tab. A bag you lack shows how to craft it.",
         "Command: /sacks (or /pd, /bags)"], "Click to open!", "cmdc:sacks"),
    ("main", 12, "Utility_Bag_Seed", "Accessory Bag",
        ["Equip bench accessories and stat talismans - they work while they sit in the bag.", "Command: /accessories (or /acc)"],
        "Click to open!", "cmdc:accessories"),
    ("main", 13, "Deco_Map", "HUD Editor",
        ["Move, resize and switch every widget of your on-screen HUD.", "Save layouts as profiles or share them as a code.",
         "Command: /skyyhud (or /shud)"], "Click to open!", "cmdc:skyyhud"),
    ("main", 14, "Bench_WorkBench", "Crafting",
        ["Craft from your inventory and your Magic Bags.", "Bench accessories in your Accessory Bag unlock that bench's recipes.",
         "Command: /craft"], "Click to open!", "cmdc:craft"),
    ("main", 15, "Weapon_Sword_Iron", "Skills",
        ["Your skill levels and XP: gathering, your class weapon skill and more. Every level up pays coins.", "Command: /skills"],
        "Click to open!", "cmdc:skills"),
    ("main", 16, "Furniture_Village_Painting_1x1", "Collections",
        ["Everything you have gathered, your milestones and the recipes they unlock.", "Command: /collections"], "Click to open!", "cmdc:collections"),
    ("main", 20, "Plant_Sapling_Oak", "Island Menu",
        ["Your island in one page: members, visitors and island settings.", "Command: /island menu (or /is menu)"],
        "Click to open!", "cmdc:island menu"),
    ("main", 21, "Furniture_Ancient_Chest_Large_Treasure", "Bank",
        ["Deposit coins to earn interest. Bank coins are safe when you die.", "Deposit all, withdraw all or type any amount.",
         "Command: /bank"], "Click to open!", "cmdc:bank"),
    ("main", 22, "Furniture_Royal_Magic_Chest_Large", "Vault",
        ["Item storage shared by ALL of your profiles - move items from one profile to another.", "Command: /vault"],
        "Click to open!", "cmdc:vault"),
    ("main", 23, "Rock_Gem_Emerald", "Bazaar",
        ["Instantly buy and sell resources. Prices move as players trade.", "Command: /bazaar (or /bz)"], "Click to open!", "cmdc:bazaar"),
    # 0.2: the Auction House (SkyyAuctions 0.1, /ah) sits next to the Bazaar; Reforge moved one slot right
    ("main", 24, "Ingredient_Bar_Gold", "Auction House",
        ["Buy items other players listed and sell your own for a fixed price (Buy It Now).",
         "Claim the coins and items you are owed on the Manage page.",
         "Command: /ah (or /auction, /auctionhouse)"], "Click to open!", "cmdc:ah"),
    ("main", 25, "Tool_Hammer_Iron", "Reforge",
        ["Put in a weapon, armor piece or tool and pay coins to reroll its stats.", "Command: /reforge"], "Click to open!", "cmdc:reforge"),
    ("main", 30, "Furniture_Village_Sign", "Players",
        ["Everyone who is online: send teleport requests, visit islands, invite to your party."], "Click to open!", "view:players"),
    ("main", 31, "Deco_Scroll", "Party",
        ["Your party page: invite players, answer invites, see your party or leave it.", "Party chat: /pc <message>",
         "Command: /party (or /p)"], "Click to open!", "cmdc:party"),
    ("main", 32, "Furniture_Outlander_Banner", "Guild",
        ["Your guild page: members and ranks, the guild bank and guild XP.", "Not in a guild? Create one or accept an invite there.",
         "Guild chat: /gc <message>", "Command: /guild"], "Click to open!", "cmdc:guild"),
    ("main", 40, "Furniture_Ancient_Bookshelf", "Mods",
        ["Every SkyWynn mod on the server, what it does and all of its commands."], "Click to open!", "view:mods"),
    # 0.3: Server Setup right of Mods (research/Server-Setup-Spec.md 2.2) - drawn ONLY for players with skyymenu.modconfig
    ("main", 41, "Deco_Book_Pile_Large", "Server Setup",
        ["Change every Skyy mod's settings in game - only admins see this.",
         "Every change is saved to the mod's own file, logged and can be undone.",
         "Command: /modconfig (or /serversetup)"], "Click to open!", "admin"),
    # 0.2: Settings in the bottom row next to Close (SkyBlock's Redstone Torch spot, research/Settings-Spec.md 4.1)
    ("main", 51, "Furniture_Crude_Torch", "Settings",
        ["Turn chat messages on or off - one switch per message, for every mod.",
         "Your settings are the same on every profile.", "Command: /settings (or /skysettings)"], "Click to open!", "settings"),
    # ---- Teleport (warps are added automatically in rows 2-4, see WARP_SLOTS)
    ("tp", 11, "Soil_Grass", "My Island",
        ["Teleport to your own island. It is created the first time you go.", "Command: /island (or /is)"], "Click to teleport!", "cmdc:island"),
    ("tp", 13, "Hub_Portal_Default", "Hub",
        ["Go back to the hub from anywhere, including your island.", "Command: /hub (or /lobby)"], "Click to teleport!", "cmdc:hub"),
    ("tp", 15, "Spawn_Portal", "Spawn", ["Teleport to the spawn point of the main world."], "Click to teleport!", "spawn"),
    # ---- Players (online players are added automatically, see PLAYER_SLOTS)
    # cmdc (close first): accepting a /tpahere request teleports YOU (SkyyEssentials accept(): mover = r.here ? r.to : r.from)
    ("players", 47, "Ingredient_Crystal_Green", "Accept Teleport Request",
        ["Accept the newest teleport request someone sent you.", "Command: /tpaccept"], "Click to accept", "cmdc:tpaccept"),
    ("players", 51, "Ingredient_Crystal_Red", "Deny Teleport Request",
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
    (29, "Hub_Portal_Default", "Send Teleport Request", ["Ask %P if you may teleport to them. They have 60 seconds to accept.", "Command: /tpa %P"],
        "Click to send", "tpa %P", False),
    (30, "Spawn_Portal", "Invite Them Here", ["Ask %P to teleport to you.", "Command: /tpahere %P"], "Click to send", "tpahere %P", False),
    (31, "Soil_Grass", "Visit Their Island", ["Teleport to the island of %P and look around (you can only build with their build rights).",
        "Command: /island visit %P"], "Click to visit", "island visit %P", True),
    (32, "Deco_Scroll", "Invite to Party", ["Invite %P to your party.", "Command: /party invite %P"], "Click to invite", "party invite %P", False),
    (33, "Tool_Hammer_Iron", "Invite to Your Island", ["Invite %P to join your island as a co-op member. Only do this for friends.",
        "They join with /island accept.", "Command: /island invite %P"], "Click to invite", "island invite %P", False),
    (34, "Tool_Pickaxe_Iron", "Let Them Build", ["Let %P build on YOUR island without making them a member.",
        "Undo with /island untrust.", "Command: /island trust %P"], "Click to trust", "island trust %P", False),
]

WARP_SLOTS   = list(range(19, 26)) + list(range(28, 35)) + list(range(37, 44))                       # 21 warps per page
PLAYER_SLOTS = list(range(10, 17)) + list(range(19, 26)) + list(range(28, 35)) + list(range(37, 44))  # 28 players per page
MOD_SLOTS    = list(range(10, 17)) + list(range(19, 26)) + list(range(28, 35))                        # 21 mods per page
NO_WARPS_SLOT, NO_PLAYERS_SLOT, PLAYER_HEAD_SLOT = 31, 22, 13

# The Mods submenu: one item per mod (icon = the item that represents it, tooltip = what it does + every command).
# "check" = a command of that mod; the mod counts as installed when its plugin or that command is loaded. The live version is
# read from the loaded plugin's manifest; "version" is only shown when the mod is not installed.
# Commands use the short positional forms (SkyyIslands 0.4.3, SkyyHud 0.3.6, SkyyBank 0.1.1, ... added usage variants / subcommands).
MODS = [
    {"mod": "SkyyMenu", "version": VERSION, "icon": "Ingredient_Voidheart", "check": "skymenu",
     "config": "Skyy_SkyyMenu/config.properties,Skyy_SkyyMenu/settings-defaults.properties", "reload": "", "note": "Set up in game - Server Setup, Menu.",
     "desc": "The all-in-one SkyWynn menu: teleports, your island menu, Pocket Dimension, Vault, Accessory Bag, the HUD editor, crafting, skills, collections, the bazaar, the auction house, the bank, reforging, players, your party and guild, your settings, this list of mods and Server Setup for admins.",
     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item",
                  "/settings (or /skysettings) - turn chat messages on or off",
                  "/modconfig (or /serversetup) - (admin) change every mod's settings in game"]},
    {"mod": "SkyyProfiles", "version": "0.1", "icon": "Deco_Book_Pile_Large", "check": "profiles",
     "config": "Skyy_SkyyProfiles/config.properties", "reload": "profileadmin reload", "note": "",
     "desc": "SkyBlock-style profiles: each profile is its own save with its own class, island, inventory, coins, bank, bags, skills and collections.",
     "commands": ["/profiles (or /profile) - open your profiles", "/profiles create (or new) - a new profile, pick its class",
                  "/profiles switch <number or name> - switch to another profile", "/profiles list - your profiles in chat",
                  "/profileadmin info <player> - (admin) a player's profiles",
                  "/profileadmin setclass <player> <n> <class> - (admin) fix a class",
                  "/profileadmin reload - (admin) re-read the settings"]},
    {"mod": "SkyyIslands", "version": "0.5", "icon": "Soil_Grass", "check": "island",
     "config": "Skyy_SkyyIslands/config.properties", "reload": "island reload", "note": "",
     "admin": ["/island reload - (admin) re-read config.properties and every island file", "/sethub - (admin) set the hub where you stand"],
     "desc": "Your own private island in the sky: teleport home any time, invite friends as co-op members and choose who may visit or build in the island menu.",
     "commands": ["/island (or /is) - go to your island", "/island menu - members, visitors and island settings",
                  "/island visit <player> - visit a player's island",
                  "/island invite <player> - invite a co-op member (they /island accept)",
                  "/island trust <player> - give a player build rights only",
                  "/island leave | kick <player> - leave a co-op | (owner) remove one",
                  "/island reset - (owner) rebuild your island from scratch", "/hub (or /lobby) - back to the hub"],
     "old": {"need": "island menu",
             "desc": "Your own private island in the sky: teleport home any time (built with a starter chest the first time), give friends build rights or let anyone visit.",
             "commands": ["/island (or /is) - go to your island", "/island visit <player> - visit a player's island",
                          "/island invite <player> - give a player build rights", "/island info - about your island",
                          "/hub (or /lobby) - back to the hub", "/sethub - (admin) set the hub point"]}},
    {"mod": "SkyySacks", "version": "0.7.5", "icon": "Tool_Feedbag", "check": "sacks",
     "config": "Skyy_SkyySacks/config.properties", "reload": "", "note": "It is read again by itself within about 10 seconds.",
     "desc": "Magic Bags: carry a Mining, Foraging, Farming, Combat or Smithing bag and what you gather of that type goes straight into your Pocket Dimension. /craft crafts from your inventory and bags (Smithing, Farming, Furnace, Tannery and more tabs).",
     "commands": ["/sacks (or /pd, /bags) - your Pocket Dimension, missing bags show recipes",
                  "/craft (or /recipes) - craft from your inventory and bags", "/craft <words> - open crafting with a search"]},
    {"mod": "SkyyAccessories", "version": "0.4.3", "icon": "Utility_Bag_Seed", "check": "accessories",
     "config": "", "reload": "", "note": "No server settings in this version.",
     "desc": "Your Accessory Bag: 9 slots for bench accessories (each unlocks its bench tab in /craft, the Campfire one cooks on the go) and stat talismans that work while they sit in the bag.",
     "commands": ["/accessories (or /acc, /accbag) - open your Accessory Bag"]},
    {"mod": "SkyyHud", "version": "0.3.9", "icon": "Deco_Map", "check": "skyyhud",
     "config": "", "reload": "", "note": "No server settings - every player sets up their own HUD with /skyyhud.",
     "desc": "A customizable on-screen HUD: coordinates, zone, clocks, day counter, session timer, players online, coins, party and guild. Move, resize and colour every widget, save profiles or share your layout as a code.",
     "commands": ["/skyyhud (or /shud) - open the HUD editor", "/skyyhud export - print your layout as a code",
                  "/skyyhud import <code> - load a layout code", "/skyyhud reset - reset your layout",
                  "/skyyhud profile save|load|delete <name> - named layouts", "/skyyhud profile list - your saved layouts"]},
    {"mod": "SkyySkills", "version": "0.4.2", "icon": "Weapon_Sword_Iron", "check": "skills",
     "config": "Skyy_SkyySkills/xp.properties", "reload": "skills reload", "note": "",
     "desc": "Hypixel-style skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill - that level up as you play and pay coins on every level up.",
     "commands": ["/skills (or /skill) - open your Skills", "/skills stats <skill> - the Stats page of a skill",
                  "/skills top <skill> - the top 10 players of a skill", "/skills quiet - hide the +XP chat messages",
                  "/skills reload - (admin) re-read the XP settings", "/skills xp <skill> <amount> - (admin) test XP"]},
    {"mod": "SkyyTrees", "version": "0.2.1", "icon": "Plant_Sapling_Maple", "check": "tree",
     "config": "Skyy_SkyyTrees/trees.properties", "reload": "tree reload", "note": "",
     "desc": "Skill trees: spend the points your skill levels earn on nodes for Mining, Foraging, Farming, Cooking, Acrobatics and Exploration.",
     "commands": ["/tree (or /trees) - open your skill trees", "/tree <skill> - open one tree, for example /tree mining",
                  "/tree quiet - hide the Tree bonus chat line", "/tree reload - (admin) re-read the tree settings"]},
    {"mod": "SkyyCollections", "version": "0.2.1", "icon": "Furniture_Village_Painting_1x1", "check": "collections",
     "config": "Skyy_SkyyCollections/collections.properties,Skyy_SkyyCollections/rewards.properties,Skyy_SkyyCollections/config.properties", "reload": "collections reload", "note": "",
     "desc": "Hypixel-style Collections: everything you gather counts toward tiers. Tiers unlock crafting recipes for the /craft page and pay rewards.",
     "commands": ["/collections (or /coll) - open your Collections", "/collections <name> - the tiers of one collection",
                  "/collections unlocks (or recipes) - the recipes you unlocked",
                  "/collections top <collection|score> - the top 10 players",
                  "/collections give <collection> <amount> - (admin) test credit",
                  "/collections reload - (admin) re-read the collection rules"]},
    {"mod": "SkyyCooking", "version": "0.1.1", "icon": "Food_Pie_Meat", "check": "cooking",
     "config": "Skyy_SkyyCooking/cooking.properties", "reload": "cookadmin reload", "note": "",
     "desc": "Cooking: dishes you cook at a Cooking Bench get a Grade from your Cooking level and skill tree - higher Grades heal and buff more.",
     "commands": ["/cooking - your Cooking level, Grade and tree chances",
                  "/cookadmin give <dish> <grade> - (admin) test dishes",
                  "/cookadmin campfire <dish> <count> - (admin) test the Campfire cook",
                  "/cookadmin reload - (admin) re-read the cooking settings"]},
    {"mod": "SkyyExploration", "version": "0.2", "icon": "Furniture_Human_Ruins_Chest_Small", "check": "explore",
     "config": "Skyy_SkyyExploration/config.properties", "reload": "exploreadmin reload", "note": "Any key also in game: /exploreadmin set. titles.chatPriority needs a restart.",
     "admin": ["/exploreadmin set <key> <value> | get <key> - (admin) change or read any config key"],
     "desc": "Exploration: loot chests out in the world, uncover the map, discover zones, find discovery spots and finish each island's checklist - all of it pays Exploration XP and earns titles.",
     "commands": ["/explore (or /exploration, /discoveries) - your exploration page",
                  "/explore quiet - hide the chunk XP chat line (also in /settings)", "/title (or /titles) - your titles",
                  "/title <name> or /title off - wear a title or none",
                  "/exploreadmin - (admin) place discovery spots, edit island checklists",
                  "/exploreadmin reload|stats|resetme - (admin)"]},
    {"mod": "SkyyClasses", "version": "0.1.4", "icon": "Weapon_Shortbow_Iron", "check": "class",
     "config": "Skyy_SkyyClasses/config.properties", "reload": "classadmin reload", "note": "",
     "desc": "Classes: Archer, Warrior or Mage (Assassin and Shaman later). With SkyyProfiles the class is picked when you create a profile and locked to it.",
     "commands": ["/class (or /classes) - open the class page", "/classadmin set <player> <class> - (admin) give a class",
                  "/classadmin reset <player> - (admin) remove a class", "/classadmin info <player> - (admin) class data",
                  "/classadmin reload - (admin) re-read the settings"]},
    {"mod": "SkyyBazaar", "version": "0.1.2", "icon": "Rock_Gem_Emerald", "check": "bazaar",
     "config": "Skyy_SkyyBazaar/products.properties,Skyy_SkyyBazaar/market.properties", "reload": "bazaaradmin reload", "note": "",
     "desc": "A Hypixel-style Bazaar: instantly buy or sell dozens of resources against the server. Prices move as people trade.",
     "commands": ["/bazaar (or /bz) - open the Bazaar",
                  "/bazaaradmin price <itemId> <price> - (admin) set a price",
                  "/bazaaradmin reset|info <itemId|all> - (admin) reset or show prices",
                  "/bazaaradmin reload - (admin) re-read the product list"]},
    {"mod": "SkyyAuctions", "version": "0.1", "icon": "Ingredient_Bar_Gold", "check": "ah",
     "config": "Skyy_SkyyAuctions/config.properties,Skyy_Market/blocked.txt", "reload": "ahadmin reload", "note": "",
     "desc": "A Hypixel-style Auction House (Buy It Now): list an item for a fixed price, buy what other players list and claim the coins and items you are owed.",
     "commands": ["/ah (or /auction, /auctionhouse) - open the Auction House",
                  "/ah sell <price> [duration] - sell the item in your hand",
                  "/ah claim - claim your coins and items", "/ah manage - your listings and claims",
                  "/ah search <words> - search the listings",
                  "/ahadmin list|info|remove|reload|pause|resume - (admin)"]},
    {"mod": "SkyyBank", "version": "0.1.3", "icon": "Furniture_Ancient_Chest_Large_Treasure", "check": "bank",
     "config": "Skyy_SkyyBank/config.properties", "reload": "", "note": "Change the interest in chat with /bankconfig - saved at once.",
     "desc": "A SkyBlock-style bank next to your coin purse: deposit coins to earn interest and withdraw them any time. Bank coins are never lost when you die.",
     "commands": ["/bank - open the bank page", "/bank deposit <n|all> - put coins in (500, 2k, 1.5m or all)",
                  "/bank withdraw <n|all> - take coins out", "/bank status - your bank and purse in chat",
                  "/bankconfig <percent> <minutes> - (admin) interest"]},
    {"mod": "SkyyCoins", "version": "0.1.5", "icon": "Rock_Gem_Ruby", "check": "balance",
     "config": "Skyy_SkyyCoins/config.properties", "reload": "", "note": "Change the death penalty in chat with /deathpenalty - saved at once.",
     "desc": "The server's coins. Check your balance and pay other players. When you die you lose a set share of the coins in your purse (bank coins are safe).",
     "commands": ["/balance (or /bal, /coins, /purse) - your coins", "/pay <player> <amount> - send coins to a player",
                  "/coinsgive <amount> - (admin) give yourself coins", "/deathpenalty 5% or 5%-10% - (admin) coins lost on death"]},
    {"mod": "SkyyVault", "version": "0.1", "icon": "Furniture_Royal_Magic_Chest_Large", "check": "vault",
     "config": "Skyy_SkyyVault/config.properties", "reload": "vaultadmin reload", "note": "",
     "desc": "Your Vault: item storage shared by every profile you have, so you can move items from one profile to another. Buy more pages with coins.",
     "commands": ["/vault - open your Vault", "/vault <page> - open one vault page", "/vault buy - buy the next page (type it twice)",
                  "/vault info - your pages, slots used and the next price",
                  "/vaultadmin open|info|setpages <player> - (admin)"]},
    {"mod": "SkyyParty", "version": "0.1.3", "icon": "Deco_Scroll", "check": "party",
     "config": "Skyy_SkyyParty/config.properties", "reload": "", "note": "No reload command - restart the server after editing.",
     "desc": "Team up with friends: invite players to a party, chat privately and see your party on the HUD. The lead passes on if the leader leaves.",
     "commands": ["/party (or /p) - open the party page", "/party invite <player> - invite a player",
                  "/party accept | decline - answer an invite", "/party leave - leave your party", "/party list - list your party",
                  "/party kick | promote <player> - (leader)", "/party disband - (leader) end the party", "/pc <message> - chat with your party"]},
    {"mod": "SkyyGuilds", "version": "0.1.1", "icon": "Furniture_Outlander_Banner", "check": "guild",
     "config": "Skyy_SkyyGuilds/config.properties", "reload": "guildadmin reload", "note": "",
     "admin": ["/guildadmin reload - (admin) re-read config.properties", "/guildadmin xp <amount> <guild> - (admin) test guild XP"],
     "desc": "Guilds: found a guild with your friends - ranks, a shared guild bank, guild XP from your skills, guild levels and seasons.",
     "commands": ["/guild - open the guild page", "/guild create <name> - start a guild", "/guild invite <player> - (leader, admin) invite",
                  "/guild accept | decline | leave - answer an invite or leave",
                  "/guild bank deposit | withdraw <amount> | log - guild coins",
                  "/guild bank limit admin|member <n|0|none> - (leader) daily withdraw limit",
                  "/guild info | list - your guild | the top guilds", "/gc <message> - guild chat"]},
    {"mod": "SkyyEssentials", "version": "0.1.2", "icon": "Tool_Map", "check": "tpa",
     "config": "Skyy_SkyyEssentials/config.properties", "reload": "tradeadmin reload", "note": "Or change every key in game on /tradeadmin config. replyShortcut needs a restart.",
     "admin": ["/tradeadmin config - (admin) every setting of config.properties on one page", "/tradeadmin log [player] | return <player> - (admin) the trade log, end a trade and give items back"],
     "desc": "Everyday commands the base game is missing: teleport requests between players, private messages and safe trades of items and coins.",
     "commands": ["/tpa <player> - ask to teleport to a player", "/tpahere <player> - ask a player to teleport to you",
                  "/tpaccept | /tpdeny [player] - answer a teleport request", "/tpacancel - cancel your requests",
                  "/msg <player> <message> (or /tell, /w) - private message", "/reply <message> (or /r) - answer your last message",
                  "/trade <player> | claim - trade items and coins safely", "/fly - (staff) toggle flight"]},
    {"mod": "SkyyRolls", "version": "0.1.4", "icon": "Weapon_Longsword_Copper", "check": "rolls",
     "config": "Skyy_SkyyRolls/reforge.properties", "reload": "", "note": "It is read again by itself whenever someone opens /reforge.",
     "desc": "Random item stats (reforges) on weapons, armor and tools, shown on the item. Reforge an item for coins on the reforge page.",
     "commands": ["/reforge - open the reforge page", "/rolls give <item> - (admin) an item with random stats",
                  "/rolls read | reroll | clear - (admin) the item in your hand"]},
]
# ---- Settings (0.2, research/Settings-Spec.md sections 2 + 4): the player Settings page (/settings, the torch at main slot 51).
# Rows are NOT made from this list: a row appears only when its mod REGISTERS the key (settings:fn:register or a settings:def:<key>
# fallback on the bridge). This list gives the known keys their order inside a tab (SET_ORDER), fills the commented
# settings-defaults.properties template and is checked when you build (key format, label <= 40, help <= 90 characters).
# Tabs, in display order: (category id, tab button text = ONE word, header, "always shown" line under the rows)
SET_TABS = [
    ("skills",      "Skills",      "Skills",             "Always shown: the one-time note when your old Combat XP moves to your class skill."),
    ("collections", "Collections", "Collections",        "Always shown: the one-time note about how collections count items."),
    ("sacks",       "Sacks",       "Sacks & Crafting",   "Always shown: the profile-changed notice on an open bag or craft page."),
    ("combat",      "Combat",      "Combat & Classes",   "Always shown: the reminder to pick a class and admin changes to your class. Blocked hits stay blocked."),
    ("coins",       "Coins",       "Coins & Bank",       "Always shown: coins you lose when you die, and your starter coins."),
    ("profiles",    "Profiles",    "Profiles & Islands", "Always shown: profile setup, switch problems, crash repairs and items that did not fit back."),
    ("cooking",     "Cooking",     "Cooking & Trees",    "Everything on this tab can be switched off."),
    ("general",     "General",     "General (menu, party, teleports, messages)",
     "Always shown: accepted teleports and how they ended, party disbanded, and replies to your own commands and clicks."),
]
# Every known switch, all default ON: (key, tab id, label, help line, registered by). Settings-Spec 2.2 WITHOUT the three refusing
# General switches (party.invites, tpa.requests, msg.private) - Skyy has not answered refuse-vs-hide yet (spec section 6).
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
    ("coll.newCollection",   "collections", "New collections",              "New collection: Copper Ore! - the first item of a kind you gather", "SkyyCollections"),
    ("coll.tierUp",          "collections", "Collection tier-ups",          "COLLECTION UP with its rewards and the recipes it unlocked", "SkyyCollections"),
    ("sacks.benchDone",      "sacks",       "Furnace and Tannery done",     "Your Furnace is done - open /craft to collect", "SkyySacks"),
    ("sacks.benchFuel",      "sacks",       "Furnace out of fuel",          "Your Furnace ran out of fuel - once until you add more", "SkyySacks"),
    ("classes.blockedChat",  "combat",      "Blocked weapon - chat line",   "Only Archers can use bows... - at most every 3 s. The hit is blocked either way", "SkyyClasses"),
    ("classes.blockedPopup", "combat",      "Blocked weapon - popup",       "The popup with the weapon's icon - at most every 1.5 s", "SkyyClasses"),
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
    ("party.members",        "general",     "Party join, leave and leader", "Steve joined, left, disconnected or is now the party leader", "SkyyParty"),
    ("party.chat",           "general",     "Party chat",                   "[Party] lines from other members - your own lines always show", "SkyyParty"),
    ("tpa.updates",          "general",     "Teleport request updates",     "Denied, expired and cancelled requests - accepted ones always show", "SkyyEssentials"),
    ("menu.tooltips",        "general",     "Menu hover tooltips",          "Pop-up text when you hover an item in the SkyWynn Menu - OFF stops stuck tooltips", "SkyyMenu"),
]
TIPS_KEY = "menu.tooltips"      # the 0.1.3 Hover Tooltips book (slot 8) and the Settings row are this one key
SET_ROWS = 7                    # rows per tab page (Prev / Next appear only when a tab has more)
SET_TXT = {
    "HINT":   "Your own settings - the same on every profile. Click ON or OFF, it saves at once.",
    "EMPTY":  "Nothing to switch here yet - the mods for this tab are not installed or not updated.",
    "BROKEN": "Your settings file could not be read - changes are not saved. Tell an admin.",
    "ARM":    "Click Reset again within 10 seconds to reset EVERY tab to its default.",
    "RESET":  "Every setting is back to its default.",
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
     "New players get the SkyWynn Menu item at their first join. Off: only /skymenu gives one.",
     "field:MenuCfg.GIVE_ITEM@config.properties:giveItem"),
    ("menu.modsHelp", "Mods list for players", "menu", "bool", "true", "", "", "", "", "live",
     "Players see the Mods tile (every mod and its commands). Admins always see it.",
     "field:MenuCfg.MODS_HELP@config.properties:modsHelp"),
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
]) + "\n"
# =====================================================================================================================
# ==============================================  end of MENU DATA  ===================================================
# =====================================================================================================================

# ================= build-time checks: icons exist, text is safe, slots are sane =================
ASSETS = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
ITEMS = {}
for _n in ASSETS.namelist():
    if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
        ITEMS[os.path.basename(_n)[:-5]] = _n
COMMON = set(n for n in ASSETS.namelist() if n.startswith("Common/"))

def need_item(iid):
    assert iid in ITEMS, "unknown vanilla item id: %s (not in Assets.zip)" % iid

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

for ic in (ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_PLAYER, MENU_ITEM_LOOK) + ((FILLER_ICON,) if FILLER_ICON else ()):
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
    assert act in ("profile", "spawn", "info", "tips", "settings", "admin") or act.split(":", 1)[0] in ("view", "cmd", "cmdc"), "bad action " + act
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
    cur, hops, icon = iid, 0, None
    while cur and hops < 8 and icon is None:
        need_item(cur)
        d = json.loads(ASSETS.read(ITEMS[cur]).decode("utf-8-sig"))
        icon = d.get("Icon")
        cur = d.get("Parent"); hops += 1
    assert icon and "Common/" + icon in COMMON, "icon picture missing for %s: %s" % (iid, icon)
for _ic in sorted(set([e[2] for e in ENTRIES] + [a[1] for a in PLAYER_ACTIONS] + [m["icon"] for m in MODS] +
                      [ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_PLAYER])):
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
assert len(SET_TABS) == 8 and len(set(SET_CAT_ID)) == 8 and SET_CAT_ID[-1] == "general", "8 tabs, general last (unknown ids go there)"
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
for _k in ("party.invites", "tpa.requests", "msg.private"):
    assert _k not in SET_ORDER, "%s refuses the other player - not built until Skyy answers refuse-vs-hide (Settings-Spec section 6)" % _k
OWN_SETTINGS = [k for k in SET_KNOWN if k[4] == "SkyyMenu"]
assert TIPS_KEY in [k[0] for k in OWN_SETTINGS], "the Hover Tooltips key must be one of SkyyMenu's own settings"
assert 1 <= SET_ROWS <= 7
for _n, _t in SET_TXT.items():
    assert _t and "\n" not in _t, "SET_TXT %s" % _n
assert used.get(("main", 51)) == "Settings", "the Settings torch belongs at main slot 51 (Settings-Spec 4.1)"
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
assert used.get(("main", 41)) == "Server Setup", "the Server Setup book belongs at main slot 41, right of Mods (spec 2.2)"
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
ALIASES = [a for a in ("menu", "sbmenu") if a not in TAKEN]
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
    "BTNBACK":  'TextButton #SkyyMBack { Anchor: (Width: 168, Height: 40); Text: "< Back"; ' + BS + " }",
    "BTNPREV":  'TextButton #SkyyMPrev { Anchor: (Width: 154, Height: 40); Text: "< Prev page"; ' + BS + " }",
    "BTNNEXT":  'TextButton #SkyyMNext { Anchor: (Width: 154, Height: 40); Text: "Next page >"; ' + BS + " }",
    "BTNCLOSE": 'TextButton #SkyyMClose { Anchor: (Width: 168, Height: 40); Text: "Close"; ' + BS + " }",
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
SPW, SPH = 1120, 930
UI_S = {
    "SROOT":     "Group #SkyyStg { Anchor: (Width: %d, Height: %d); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 14); LayoutMode: Top; }" % (SPW, SPH),
    "SACCENT":   "Group { Anchor: (Height: 3); Background: #e0b060; }",
    "STITLE":    'Label #SkyyStgTitle { Anchor: (Height: 48); Text: "Settings"; Style: (FontSize: 28, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "SHINT":     'Label #SkyyStgHint { Anchor: (Height: 26); Text: ""; Style: (FontSize: 16, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "STABS0":    "Group #SkyyStgTabs0 { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 5); }",
    "STABS1":    "Group #SkyyStgTabs1 { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 5); }",
    "SSP12":     'Label { Anchor: (Width: 12, Height: 48); Text: ""; }',
    "SSP10":     'Label { Anchor: (Width: 10, Height: 52); Text: ""; }',
    "SSP14":     'Label { Anchor: (Width: 14, Height: 52); Text: ""; }',
    "SGAP8":     "Group { Anchor: (Height: 8); }",
    "SGAP6":     "Group { Anchor: (Height: 6); }",
    "SHEAD":     'Label #SkyyStgHead { Anchor: (Height: 40); Text: ""; Style: (FontSize: 24, RenderBold: true, TextColor: #e0b060, VerticalAlignment: Center); }',
    "SROWS":     "Group #SkyyStgRows { Anchor: (Height: %d); LayoutMode: Top; }" % (SET_ROWS * 76),
    "SEMPTY":    'Label #SkyyStgEmpty { Anchor: (Height: 80); Text: ""; Style: (FontSize: 19, TextColor: #c9dff0, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "SALWAYS":   'Label #SkyyStgAlways { Anchor: (Height: 26); Text: ""; Style: (FontSize: 15, TextColor: #8fa0b0, VerticalAlignment: Center); }',
    "SSTATUS":   'Label #SkyyStgStatus { Anchor: (Height: 30); Text: ""; Style: (FontSize: 17, RenderBold: true, TextColor: #ffd27f, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "SFOOT":     "Group #SkyyStgFoot { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 6); }",
    "SLEADA":    'Label { Anchor: (Width: 185, Height: 50); Text: ""; }',      # centres Reset + Menu + Close (710 px of 1080)
    "SLEADB":    'Label { Anchor: (Width: 25, Height: 50); Text: ""; }',       # centres Prev + Next + Reset + Menu + Close (1030 px)
    "SPREV":     'TextButton #SkyyStgPrev { Anchor: (Width: 150, Height: 50); Text: "< Prev"; ' + SBS + " }",
    "SNEXT":     'TextButton #SkyyStgNext { Anchor: (Width: 150, Height: 50); Text: "Next >"; ' + SBS + " }",
    "SRESET":    'TextButton #SkyyStgReset { Anchor: (Width: 300, Height: 50); Text: "Reset all to defaults"; ' + SBS + " }",
    "SRESETARM": 'TextButton #SkyyStgReset { Anchor: (Width: 300, Height: 50); Text: "Click again to reset ALL"; ' + RESET_ARM + " }",
    "SMENU":     'TextButton #SkyyStgMenu { Anchor: (Width: 220, Height: 50); Text: "< SkyWynn Menu"; ' + SBS + " }",
    "SCLOSE":    'TextButton #SkyyStgClose { Anchor: (Width: 170, Height: 50); Text: "Close"; ' + SBS + " }",
}
UI_SARR = {
    "STAB":    ['TextButton #SkyyStgTab%d { Anchor: (Width: 252, Height: 48); Text: "%s"; ' % (i, t[1]) + SBS + " }" for i, t in enumerate(SET_TABS)],
    "STABSEL": ['TextButton #SkyyStgTab%d { Anchor: (Width: 252, Height: 48); Text: "%s"; ' % (i, t[1]) + TAB_SEL + " }" for i, t in enumerate(SET_TABS)],
    "SROW":    ["Group #SkyyStgRow%d { Anchor: (Height: 70); Background: #142030(0.92); LayoutMode: Left; Padding: (Top: 9); }" % r for r in range(SET_ROWS)],
    "STXT":    ["Group #SkyyStgTxt%d { Anchor: (Width: 774, Height: 52); LayoutMode: Top; }" % r for r in range(SET_ROWS)],
    "SNAME":   ['Label #SkyyStgName%d { Anchor: (Height: 28); Text: ""; Style: (FontSize: 21, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }' % r for r in range(SET_ROWS)],
    "SDESC":   ['Label #SkyyStgDesc%d { Anchor: (Height: 24); Text: ""; Style: (FontSize: 16, TextColor: #b8c8d8, VerticalAlignment: Center); }' % r for r in range(SET_ROWS)],
    "SON":     ['TextButton #SkyyStgOn%d { Anchor: (Width: 120, Height: 52); Text: "ON"; ' % r + SBS + " }" for r in range(SET_ROWS)],
    "SONSEL":  ['TextButton #SkyyStgOn%d { Anchor: (Width: 120, Height: 52); Text: "ON"; ' % r + ON_SEL + " }" for r in range(SET_ROWS)],
    "SOFF":    ['TextButton #SkyyStgOff%d { Anchor: (Width: 120, Height: 52); Text: "OFF"; ' % r + SBS + " }" for r in range(SET_ROWS)],
    "SOFFSEL": ['TextButton #SkyyStgOff%d { Anchor: (Width: 120, Height: 52); Text: "OFF"; ' % r + OFF_SEL + " }" for r in range(SET_ROWS)],
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
assert "Width" in UI_S["SROOT"] and "Top:" not in UI_S["SROOT"].split("Anchor: (")[1].split(")")[0], "settings root anchor must be Width/Height only"
_stall = 2 * 14 + 3 + 48 + 26 + 58 + 58 + 8 + 40 + SET_ROWS * 76 + 26 + 30 + 62
assert _stall <= SPH, "settings parts are %d px tall, page is %d" % (_stall, SPH)
assert SPH <= 1080 - 100, "the settings page must fit a 1080 px high screen"
assert 14 + 774 + 120 + 10 + 120 <= SPW - 40, "a settings row is wider than the page"
assert 4 * 252 + 3 * 12 <= SPW - 40, "a tab row is wider than the page"
assert 25 + 150 + 150 + 300 + 220 + 170 + 4 * 10 <= SPW - 40 and 185 + 300 + 220 + 170 + 2 * 10 <= SPW - 40, "the settings footer is wider than the page"

# ================= 0.3 Server Setup page (research/Server-Setup-Spec.md 2.3-2.12): 1120 x 930, every id starts with SkyyAdm =================
# Fixed parts are constants here (validated below and found again in MenuData.class after the build); parts that carry a mod's text are
# built at run time by AdminPage.btn / lab / spc / field from the SAME patterns (the harness validated their output) with the text
# reduced to letters, digits, space and < > / - (MenuUtil.inl); Labels get every mod text through b.set.
def _tbsz(bg, fg, hov, pre, fs):
    lab = "LabelStyle: (FontSize: %d, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)" % (fs, fg)
    return ("Style: TextButtonStyle(Default: (Background: " + bg + ", " + lab + "), Hovered: (Background: " + hov + ", " + lab + "), "
            "Pressed: (Background: " + pre + ", " + lab + "));")
APW, APH = 1120, 930
A_INNER = APW - 40                                   # 1080: the root has Horizontal padding 20
A_BODY = APH - 2 * 14 - 3 - 48 - 26 - 30 - 62        # 733: accent, title, subtitle, (body), status, footer
ADM_ROWS, ADM_LROWS, ADM_GROWS, ADM_HROWS = 7, 8, 10, 8
ADM_INFOLINES, ADM_MSGLINES, ADM_PLINES, ADM_FROWS = 24, 16, 12, 4
ADM_STYLE = {
    "BS":    SBS,                                                        # brown, FontSize 18 (the Settings page buttons)
    "BS16":  _tbsz("#5a4420", "#ffe9c9", "#8a6a30", "#3a2a10", 16),     # tabs + choice buttons (longer texts)
    "SEL":   TAB_SEL,
    "SEL16": _tbsz("#e0b060", "#2a1a00", "#f0c880", "#b08840", 16),
    "ONSEL": ON_SEL,
    "OFFSEL": OFF_SEL,
    "RED":   RESET_ARM,
}
_TXT = lambda i, h, fs, col, bold=False, center=False, w=0: ('Label #%s { Anchor: (%sHeight: %d); Text: ""; Style: (FontSize: %d%s, TextColor: %s%s, VerticalAlignment: Center); }'
                                                            % (i, ("Width: %d, " % w) if w else "", h, fs, ", RenderBold: true" if bold else "", col, ", HorizontalAlignment: Center" if center else ""))
UI_A = {
    "AROOT":    "Group #SkyyAdm { Anchor: (Width: %d, Height: %d); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 14); LayoutMode: Top; }" % (APW, APH),
    "AACCENT":  "Group { Anchor: (Height: 3); Background: #e0b060; }",
    "ATITLE":   _TXT("SkyyAdmTitle", 48, 28, "#ffe9c9", True, True),
    "ASUB":     _TXT("SkyyAdmSub", 26, 16, "#9fb8cc", False, True),
    "ABODY":    "Group #SkyyAdmBody { Anchor: (Height: %d); LayoutMode: Top; }" % A_BODY,
    "AFOOT":    "Group #SkyyAdmFoot { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 6); }",
    "AGAP6":    "Group { Anchor: (Height: 6); }",
    "AGAP8":    "Group { Anchor: (Height: 8); }",
    "AGAP12":   "Group { Anchor: (Height: 12); }",
    "AGAP20":   "Group { Anchor: (Height: 20); }",
    "AHEAD":    _TXT("SkyyAdmHead", 40, 24, "#e0b060", True),
    "AEMPTY":   _TXT("SkyyAdmEmpty", 80, 19, "#c9dff0", False, True),
    # list
    "ALSEARCH": "Group #SkyyAdmSearch { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "ALROWS":   "Group #SkyyAdmLRows { Anchor: (Height: %d); LayoutMode: Top; }" % (ADM_LROWS * 76),
    # mod
    "ATABS0":   "Group #SkyyAdmTabs0 { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 5); }",
    "ATABS1":   "Group #SkyyAdmTabs1 { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 5); }",
    "AROWS":    "Group #SkyyAdmRows { Anchor: (Height: %d); LayoutMode: Top; }" % (ADM_ROWS * 76),
    "AINFO":    "Group #SkyyAdmInfo { Anchor: (Height: 700); Background: #142030(0.92); Padding: (Horizontal: 24, Vertical: 12); LayoutMode: Top; }",
    # table
    "ATFIND":   "Group #SkyyAdmTFindRow { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "ATCOLS":   "Group #SkyyAdmCols { Anchor: (Height: 30); LayoutMode: Left; }",
    "ATROWS":   "Group #SkyyAdmTRows { Anchor: (Height: %d); LayoutMode: Top; }" % (ADM_ROWS * 76),
    "ATADD":    "Group #SkyyAdmTAdd { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 6); }",
    # confirm
    "AMSGBOX":  "Group #SkyyAdmMsgBox { Anchor: (Height: 560); Background: #142030(0.92); Padding: (Horizontal: 24, Vertical: 12); LayoutMode: Top; }",
    "ACONF":    "Group #SkyyAdmConf { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 3); }",
    # log + history + io
    "AGROWS":   "Group #SkyyAdmGRows { Anchor: (Height: %d); LayoutMode: Top; }" % (ADM_GROWS * 52),
    "AHROWS8":  "Group #SkyyAdmHRows { Anchor: (Height: %d); LayoutMode: Top; }" % (ADM_HROWS * 58),
    "AHROWS4":  "Group #SkyyAdmHRows { Anchor: (Height: %d); LayoutMode: Top; }" % (4 * 58),
    "APREV":    "Group #SkyyAdmPrev { Anchor: (Height: 282); Background: #101c2c; Padding: (Horizontal: 16, Vertical: 8); LayoutMode: Top; }",
    "APREVHEAD": _TXT("SkyyAdmPrevHead", 26, 17, "#e0b060", True),
    "AIOL1":    _TXT("SkyyAdmIoL1", 34, 18, "#e0b060", True),
    "AIOL2":    _TXT("SkyyAdmIoL2", 34, 18, "#e0b060", True),
    "AIOR1":    "Group #SkyyAdmIoR1 { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "AIOR2":    "Group #SkyyAdmIoR2 { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 4); }",
    "AIOF":     _TXT("SkyyAdmIoF", 30, 17, "#9fb8cc"),
    "AIOFROWS": "Group #SkyyAdmIoFRows { Anchor: (Height: %d); LayoutMode: Top; }" % (ADM_FROWS * 48),
}
UI_AARR = {
    "ASTATUS":  [_TXT("SkyyAdmStatus", 30, 17, c, True, True) for c in ("#ffd27f", "#7fe07f", "#ffb347", "#ff7a7a")],
    "ALROW":    ["Group #SkyyAdmLRow%d { Anchor: (Height: 70); Background: #142030(0.92); LayoutMode: Left; Padding: (Top: 9); }" % r for r in range(ADM_LROWS)],
    "ALTXT":    ["Group #SkyyAdmLTxt%d { Anchor: (Width: 736, Height: 52); LayoutMode: Top; }" % r for r in range(ADM_LROWS)],
    "ALNAME":   [_TXT("SkyyAdmLName%d" % r, 28, 21, "#ffffff", True) for r in range(ADM_LROWS)],
    "ALDESC":   [_TXT("SkyyAdmLDesc%d" % r, 24, 16, "#b8c8d8") for r in range(ADM_LROWS)],
    "ALDESCRED": [_TXT("SkyyAdmLDesc%d" % r, 24, 16, "#ff8a8a", True) for r in range(ADM_LROWS)],
    "AROW":     ["Group #SkyyAdmRow%d { Anchor: (Height: 70); Background: #142030(0.92); LayoutMode: Top; Padding: (Top: 3); }" % r for r in range(ADM_ROWS)],
    "ALINE":    ["Group #SkyyAdmLine%d { Anchor: (Height: 42); LayoutMode: Left; }" % r for r in range(ADM_ROWS)],
    "ANAME":    [_TXT("SkyyAdmName%d" % r, 42, 20, "#ffffff", True, False, 556) for r in range(ADM_ROWS)],
    "AW":       ["Group #SkyyAdmW%d { Anchor: (Width: 380, Height: 42); LayoutMode: Left; }" % r for r in range(ADM_ROWS)],
    "AHELP":    ["Group #SkyyAdmHelpRow%d { Anchor: (Height: 22); LayoutMode: Left; }" % r for r in range(ADM_ROWS)],
    "ADESC":    [_TXT("SkyyAdmDesc%d" % r, 22, 15, "#b8c8d8", False, False, 1050) for r in range(ADM_ROWS)],
    "ARO":      [_TXT("SkyyAdmRo%d" % r, 42, 19, "#ffe9a0", True, False, 380) for r in range(ADM_ROWS)],
    "ACHV":     [_TXT("SkyyAdmChv%d" % r, 42, 18, "#ffe9a0", True, True, 268) for r in range(ADM_ROWS)],
    "ATROW":    ["Group #SkyyAdmTRow%d { Anchor: (Height: 70); Background: #142030(0.92); LayoutMode: Left; Padding: (Top: 9); }" % r for r in range(ADM_ROWS)],
    "ATKEY":    [_TXT("SkyyAdmTKey%d" % r, 52, 18, "#ffffff", True, False, 300) for r in range(ADM_ROWS)],
    "ATCELLS":  ["Group #SkyyAdmTCols%d { Anchor: (Width: 450, Height: 52); LayoutMode: Left; }" % r for r in range(ADM_ROWS)],
    "AINFOL":   [_TXT("SkyyAdmInfo%d" % i, 27, 18, "#e6f2ff") for i in range(ADM_INFOLINES)],
    "AINFOB":   [_TXT("SkyyAdmInfo%d" % i, 27, 19, "#e0b060", True) for i in range(ADM_INFOLINES)],
    "AMSGQ":    [_TXT("SkyyAdmMsg%d" % i, 33, 21, "#ffe9c9", True) for i in range(ADM_MSGLINES)],
    "AMSGL":    [_TXT("SkyyAdmMsg%d" % i, 33, 18, "#c9dff0") for i in range(ADM_MSGLINES)],
    "AGROW":    ["Group #SkyyAdmGRow%d { Anchor: (Height: 46); Background: #142030(0.92); LayoutMode: Left; Padding: (Top: 3); }" % r for r in range(ADM_GROWS)],
    "AGTXT":    [_TXT("SkyyAdmGTxt%d" % r, 40, 16, "#e6f2ff", False, False, 890) for r in range(ADM_GROWS)],
    "AHROW":    ["Group #SkyyAdmHRow%d { Anchor: (Height: 52); Background: #142030(0.92); LayoutMode: Left; Padding: (Top: 4); }" % r for r in range(ADM_HROWS)],
    "AHTXT":    [_TXT("SkyyAdmHTxt%d" % r, 44, 16, "#e6f2ff", False, False, 780) for r in range(ADM_HROWS)],
    "APL":      [_TXT("SkyyAdmPL%d" % i, 20, 15, "#c9dff0") for i in range(ADM_PLINES)],
    "AFROW":    ["Group #SkyyAdmFRow%d { Anchor: (Height: 42); LayoutMode: Left; }" % r for r in range(ADM_FROWS)],
    "AFTXT":    [_TXT("SkyyAdmFTxt%d" % r, 42, 17, "#e6f2ff", False, False, 900) for r in range(ADM_FROWS)],
}
# the run-time patterns (AdminPage.btn / spc / lab / field) with sample values, so the validation below also covers them
def adm_btn(i, w, h, text, style):
    return 'TextButton #%s { Anchor: (Width: %d, Height: %d); Text: "%s"; %s }' % (i, w, h, text, style)
def adm_field(i, w, h, mx, ph):
    p = (' PlaceholderText: "%s"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 17);' % ph) if ph else ""
    return ["Group #%sBox { Anchor: (Width: %d, Height: %d); Background: #16263a; }" % (i, w, h),
            "TextField #%s { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: %d;%s Style: (TextColor: #ffffff, FontSize: 19); }" % (i, mx, p)]
ADM_SAMPLES = ([adm_btn("SkyyAdmTab3", 126, 48, "Player settings", ADM_STYLE["SEL16"]), adm_btn("SkyyAdmF0", 90, 50, "< Prev", ADM_STYLE["BS"]),
                'Label { Anchor: (Width: 14, Height: 42); Text: ""; }', _TXT("SkyyAdmColv0x1", 52, 18, "#ffffff", False, False, 222)]
               + adm_field("SkyyAdmVal3", 196, 42, 2000, "") + adm_field("SkyyAdmFind", 520, 50, 60, "search settings and editors"))
ADM_UI_ALL = list(UI_A.values()) + [x for v in UI_AARR.values() for x in v] + list(ADM_STYLE.values())
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
assert "Width" in UI_A["AROOT"] and "Top:" not in UI_A["AROOT"].split("Anchor: (")[1].split(")")[0], "server setup root anchor must be Width/Height only"
# height budgets (spec 2.4 / 2.5 asserts, like the menu's _tall): the body of every view fits the fixed body group
assert 2 * 14 + 3 + 48 + 26 + A_BODY + 30 + 62 == APH and APH <= 1080 - 100, "the server setup page must fit a 1080 px high screen"
_abody = {"list": 58 + ADM_LROWS * 76, "mod": 2 * 58 + 8 + 40 + ADM_ROWS * 76, "file": 700, "table": 58 + 40 + 30 + ADM_ROWS * 76 + 62,
          "confirm": 560 + 20 + 62, "log": 2 * 58 + 40 + ADM_GROWS * 52, "hist": 58 + 40 + ADM_HROWS * 58, "histprev": 58 + 40 + 4 * 58 + 282,
          "io": 34 + 58 + 12 + 34 + 58 + 282 + 30 + ADM_FROWS * 48}
for _v, _h in _abody.items():
    assert _h <= A_BODY, "server setup view %s needs %d px, the body has %d" % (_v, _h, A_BODY)
assert 24 + ADM_INFOLINES * 27 <= 700 and 24 + ADM_MSGLINES * 33 <= 560 and 16 + 26 + ADM_PLINES * 20 <= 282
# width budgets (inner width 1080)
assert 14 + 736 + 10 + 150 + 10 + 150 <= A_INNER, "a list row is wider than the page"
assert 14 + 556 + 10 + 380 + 10 + 110 <= A_INNER and 156 + 6 + 84 + 6 + 60 + 6 + 60 <= 380 and 270 + 6 + 104 <= 380, "a mod row is wider than the page"
assert 8 * 126 + 7 * 8 <= A_INNER, "a tab row is wider than the page"
assert 14 + 300 + 10 + 450 + 10 + 100 + 6 + 150 <= A_INNER and 3 * 146 + 2 * 6 <= 450 and 2 * 222 + 6 <= 450, "a table row is wider than the page"
assert 14 + 890 + 10 + 120 <= A_INNER and 14 + 780 + 10 + 120 + 6 + 120 <= A_INNER and 830 + 10 + 200 <= A_INNER and 780 + 10 + 130 + 10 + 130 <= A_INNER
assert 90 + 90 + 120 + 180 + 140 + 160 + 110 + 100 + 7 * 8 <= A_INNER, "the mod footer is wider than the page"
assert 120 + 120 + 150 + 150 + 130 + 200 + 120 + 6 * 8 <= A_INNER, "the list footer is wider than the page"

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

E_VIEW = [e[0] for e in ENTRIES]; E_SLOT = [e[1] for e in ENTRIES]; E_ICON = [e[2] for e in ENTRIES]
E_NAME = [txt(e[3]) for e in ENTRIES]; E_BODY = [lines_of(e[4]) for e in ENTRIES]
E_FOOT = [txt(e[5]) if e[5] else None for e in ENTRIES]; E_ACT = [e[6] for e in ENTRIES]
for a in E_ACT:
    assert '"' not in a and "\\" not in a
PA = PLAYER_ACTIONS
MOD_BODY = [txt(m["desc"]) + "\nCommands:\n" + "\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m["commands"]) for m in MODS]
MOD_OLD_NEED = [m["old"]["need"] if "old" in m else "" for m in MODS]
MOD_OLD_BODY = [(txt(m["old"]["desc"]) + "\nCommands:\n" + "\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m["old"]["commands"]))
                if "old" in m else "" for m in MODS]
# Info-box detail lines go into #SkyyMInfo0..8: fixed 14 px labels WITHOUT Wrap (a wrapped second row would spill into the next
# label), about 730 px wide at FontSize 14 (0.1.2: everything 1.4x, so the same characters fit). Keep every static detail line short enough to fit on one row. The first line of each
# body goes to #SkyyMInfoDesc (wraps) and the hover tooltips always carry the full text.
INFO_MAX = 80
for _body in (E_BODY + MOD_BODY + [b for b in MOD_OLD_BODY if b] + [lines_of(v[2]) for v in VIEWS] +
              [lines_of(a[3]).replace("%P", "W" * 16) for a in PA] + [lines_of(a[3]).replace("%P", "W" * 16) for a in PA_LEGACY]):
    for _l in _body.split("\n")[1:]:
        assert len(_l) <= INFO_MAX, "info line longer than %d characters (unwrapped label, may be cut off - shorten it): %s" % (INFO_MAX, _l)

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
             (T["INV"], "getStorage"), (T["INV"], "getHotbar"), (T["INV"], "getBackpack"),
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
             ("com.hypixel.hytale.server.core.universe.world.spawn.ISpawnProvider", "getSpawnPoint"),
             (T["PRE"], "getPlayerRef"), (T["PDE"], "getPlayerRef"), (T["HSV"], "SCHEDULED_EXECUTOR"), (T["CTX"], "provided"),
             (T["BT"], "Validating"), (T["INV"], "getItemInHand"), (T["EVD"], "append"), (T["ACM"], "requirePermission"),
             (T["ACM"], "addUsageVariant"), (T["ACM"], "withRequiredArg"), (T["ATY"], "STRING"), (T["CTX"], "get")):
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
fac  = mk("MenuPageFactory")
cmd  = mk("MenuCmd", T["APC"])
scmd = mk("SettingsCmd", T["APC"])
acmv = mk("AdminModCmd", T["APC"])
acmd = mk("AdminCmd", T["APC"])
grt  = mk("GrantTask")
rdy  = mk("MenuReady")
seen = mk("SeenTick")
quit_ = mk("MenuQuit")
pl   = mk("SkyyMenuPlugin", JP)

def F(cls, src):
    cls.addField(CtField.make(jv(src), cls))
def M(cls, src):
    cls.addMethod(CtNewMethod.make(jv(src), cls))
def C(cls, src):
    cls.addConstructor(CtNewConstructor.make(jv(src), cls))

# ================= MenuData: everything from the MENU DATA section =================
for name, val in (("ITEM_ID", jstr(MENU_ITEM_ID)), ("PAGE_ID", jstr(PAGE_ID)), ("ICON_BACK", jstr(ICON_BACK)), ("ICON_PREV", jstr(ICON_PREV)),
                  ("ICON_NEXT", jstr(ICON_NEXT)), ("ICON_CLOSE", jstr(ICON_CLOSE)), ("ICON_WARP", jstr(ICON_WARP)),
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
F(dat, "public static final String[] E_NAME = %s;" % jarr(E_NAME))
F(dat, "public static final String[] E_BODY = %s;" % jarr(E_BODY))
F(dat, "public static final String[] E_FOOT = %s;" % jarr(E_FOOT))
F(dat, "public static final String[] E_ACT = %s;" % jarr(E_ACT))
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
F(dat, "public static final int SET_ROWS = %d;" % SET_ROWS)
F(dat, "public static final String SET_TEMPLATE = %s;" % jstr(SET_TEMPLATE))
for _n, _t in SET_TXT.items():
    F(dat, "public static final String SET_TXT_%s = %s;" % (_n, jstr(_t)))
F(dat, "public static final String TIPS_KEY = %s;" % jstr(TIPS_KEY))
F(dat, "public static final String[] OWN_KEY = %s;" % jarr([k[0] for k in OWN_SETTINGS]))
F(dat, "public static final String[] OWN_CAT = %s;" % jarr([k[1] for k in OWN_SETTINGS]))
F(dat, "public static final String[] OWN_LABEL = %s;" % jarr([k[2] for k in OWN_SETTINGS]))
F(dat, "public static final String[] OWN_HELP = %s;" % jarr([k[3] for k in OWN_SETTINGS]))
F(dat, "public static final boolean[] OWN_DEF = %s;" % jbools([True for k in OWN_SETTINGS]))
for _n, _t in UI_S.items():
    F(dat, "public static final String UI_%s = %s;" % (_n, jstr(_t)))
for _n, _v in UI_SARR.items():
    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))
# 0.3 Server Setup data + page strings
F(dat, "public static final String ADMIN_NODE = %s;" % jstr(ADMIN_NODE))
F(dat, "public static final String ADM_CONTRACT = %s;" % jstr(ADM_CONTRACT))
for _n, _v in (("ADM_ROWS", ADM_ROWS), ("ADM_LROWS", ADM_LROWS), ("ADM_GROWS", ADM_GROWS), ("ADM_HROWS", ADM_HROWS), ("ADM_INFOLINES", ADM_INFOLINES),
               ("ADM_MSGLINES", ADM_MSGLINES), ("ADM_PLINES", ADM_PLINES), ("ADM_FROWS", ADM_FROWS), ("ADM_INNER", A_INNER)):
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
F(dat, "public static final String MENU_CFG_TEXT = %s;" % jstr(MENU_CFG_TEXT))
for _n, _t in UI_A.items():
    F(dat, "public static final String UI_%s = %s;" % (_n, jstr(_t)))
for _n, _v in UI_AARR.items():
    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))
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
M(utl, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
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
  return countIn(inv.getStorage(), id) + countIn(inv.getHotbar(), id) + countIn(inv.getBackpack(), id);
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
    if (!okA) warn("/modconfig does not open Server Setup (" + (a == null ? "not registered" : "answered by " + a.getClass().getName()) + ") - admins can use the SkyWynn Menu book");
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

# ================= Given: persisted "already got the menu item" flags + session guards =================
F(giv, "public static java.nio.file.Path DIR;")
F(giv, "public static final java.util.concurrent.ConcurrentHashMap SESSION = new java.util.concurrent.ConcurrentHashMap();")
F(giv, "public static final java.util.concurrent.ConcurrentHashMap INFLIGHT = new java.util.concurrent.ConcurrentHashMap();")
M(giv, r"""
public static synchronized boolean isGiven(java.util.UUID u) {
  try { return DIR != null && java.nio.file.Files.exists(DIR.resolve(u.toString() + ".txt"), new java.nio.file.LinkOption[0]); }
  catch (Throwable t) { return false; }
}""")
M(giv, r"""
public static synchronized void markGiven(java.util.UUID u) {
  try {
    if (DIR == null) return;
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(u.toString() + ".txt.tmp");
    byte[] data = ("menu item given " + System.currentTimeMillis() + "\n").getBytes("UTF-8");
    java.nio.file.Files.write(tmp, data, new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".txt"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not save the menu-item flag for " + u + ": " + t); }
}""")

# ================= 0.3 MenuCfg: SkyyMenu's own server settings (Skyy_SkyyMenu/config.properties), bound to the config kit =================
# Fields are public static volatile (the kit writes them with the primitive Field setters, spec 1.4.1); load() is the kit's RELOAD
# (hand edits + Reload file) and the start-up load. init() writes the commented default file once when it is missing.
F(mcfg, "public static java.nio.file.Path FILE;")
F(mcfg, "public static volatile boolean GIVE_ITEM = true;")
F(mcfg, "public static volatile boolean MODS_HELP = true;")
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
    if (!java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) { GIVE_ITEM = true; MODS_HELP = true; return; }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    GIVE_ITEM = flag(p, "giveItem", true);
    MODS_HELP = flag(p, "modsHelp", true);
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
               FILES=MENU_CFG_FILES, NOTE=MENU_CFG_NOTE, RELOAD="MenuCfg.load", KEEP=20,
               DEFAULTS={"config.properties": MENU_CFG_TEXT, "settings-defaults.properties": SET_TEMPLATE})
print("config kit: %d rows, files %s" % (KIT.info["rows"], ", ".join(KIT.info["files"])))

# ================= 0.2 Settings registry (research/Settings-Spec.md 1.2-1.5) =================
# Bridge contract (never removed; java.lang types only - every mod has its own classloader):
#   settings:fn:register  apply(Object[] { String mod, String key, String label, String category, Boolean def, String help }) -> Boolean
#   settings:fn:get       apply(Object[] { UUID player, String key }) -> Boolean (choice, else admin default, else registered default; null = unknown)
#   settings:fn:set       apply(Object[] { UUID player, String key, Boolean value [, Boolean onlyIfUnset] }) -> Boolean (TRUE = stored state matches)
#   settings:def:<key>    the same Object[6] as register, written by every adopter at setup (drained here, so load order never matters)
# Guarantees: never throws (bad input = null / FALSE); never calls another mod, never writes the bridge from get/set, never touches ECS or
# inventories; the only locks are SetReg.class (register, memory only), SetStore.class (memory only - never held during file I/O) and
# SetStore's 64 lock stripes (one player's own file read / write; a stripe holder never takes another lock or calls out), so calling it
# from inside a caller's own lock is safe and no lock cycle exists. get is two ConcurrentHashMap reads + a HashMap read after the
# player's first read (preloaded at join); set / resetAll of a loaded player never wait for any disk write, not even that player's own.
# ---- SetReg: the registered switches (fields first - javassist) + the admin defaults file
F(sreg, "public static final java.util.concurrent.ConcurrentHashMap DEFS = new java.util.concurrent.ConcurrentHashMap();")
F(sreg, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")
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
# idempotent: the same mod registering again updates label / help / tab; a different mod registering the same key (shared keys such as
# rewards.late) is accepted and the FIRST registration is kept - one warning if the defaults differ
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
    Object[] old = (Object[]) DEFS.get(key);
    if (old != null && !mod.equals(old[0])) {
      if (!def.equals(old[4]) && WARNED.putIfAbsent(key, Boolean.TRUE) == null)
        @PKG@.MenuUtil.warn("setting " + key + ": " + mod + " wants default " + def + ", " + old[0] + " registered " + old[4] + " first - keeping " + old[4]);
      return true;
    }
    DEFS.put(key, new Object[] { mod, key, label, cat, def, help });
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
M(sreg, r"""
public static Object[] info(String key) {
  if (key == null) return null;
  Object[] d = (Object[]) DEFS.get(key);
  if (d == null) {
    Object v = @PKG@.MenuUtil.bridge().get("settings:def:" + key);
    if (v != null && register(v)) d = (Object[]) DEFS.get(key);
  }
  return d;
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
M(sst, r"""
public static void saveSoon(String k) {
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.SetSaveTask(k), 500L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { saveNow(k); }
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
    if (r == 2) { saveSoon(k); return 1; }
    if (r != 3) return r;
  }
  return 0;
}""")
M(sst, r"""
public static synchronized int resetMem(String k) {
  if (VALS.get(k) == null) return 3;
  VALS.put(k, new java.util.HashMap());
  return DIRTY.putIfAbsent(k, Boolean.TRUE) == null ? 2 : 1;
}""")
M(sst, r"""
public static int resetAll(java.util.UUID u) {
  if (u == null) return 0;
  String k = u.toString();
  for (int i = 0; i < 3; i++) {
    if (load(k) == null) return 0;
    int r = resetMem(k);
    if (r == 2) { saveSoon(k); return 1; }
    if (r != 3) return r;
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
# 1 = saved (memory now, file 500 ms later), 0 = the player's settings file is unreadable (nothing changed)
M(tip, r"""
public static int setOff(java.util.UUID u, boolean off) {
  if (u == null) return 0;
  return @PKG@.SetStore.set(u, @PKG@.MenuData.TIPS_KEY, !off, false);
}""")

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
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.SetLoadTask(k, u), 0L, java.util.concurrent.TimeUnit.MILLISECONDS);
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

# ================= MenuPage (inline page; views switched with rebuild()) =================
for f in ("public String view;", "public int pageNo;", "public java.util.UUID selU;", "public String[] acts;", "public String[] names;",
          "public String[] bodies;", "public String infoName;", "public String infoBody;", "public String status;", "public String title;",
          "public int pages;", "public boolean cleared;"):
    F(page, f)
C(page, r"""
public MenuPage(@PR@ pr, String view) {
  super(pr, @LIFE@.CanDismiss);
  this.view = view == null ? "main" : view;
  this.pageNo = 0;
  this.status = "";
  this.pages = 1;
}""")
# 0.2 SettingsPage fields + constructor right here (javassist: MenuPage.openSettings and the page's "< SkyWynn Menu" button use each
# other's constructors - the SkyyHud WidgetsPage / EditorPage pattern: constructors first, methods after). cat -1 = the first tab with rows.
for f in ("public int cat;", "public int pageNo;", "public String status;", "public long armedAt;", "public String[] rowKeys;",
          "public boolean drained;"):
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
}""")
# 0.3 AdminPage fields + constructor right here too (MenuPage.openAdmin and the page's "< SkyWynn Menu" button use each other's
# constructors - constructors first, methods after). View = list / mod / table / confirm / log / hist / io (spec 2.3).
for f in ("public String view;", "public String mod;", "public int cat;", "public int listPage;", "public int modPage;", "public int tPage;",
          "public int logPage;", "public int histPage;", "public String tableKey;", "public String tFilter;", "public String tFilterDraft;",
          "public String findDraft;", "public String status;", "public int statusKind;", "public boolean showAdv;", "public java.util.HashMap drafts;",
          "public Object[] pending;", "public String pendingMod;", "public String pendingMsg;", "public int pendingKind;",
          "public java.util.ArrayList pendingCodes;", "public String[] rowKeys;", "public String backView;", "public String search;",
          "public boolean locked;", "public boolean jumpHit;", "public String[] listMods;", "public String[] listReload;", "public String[] tKeys;",
          "public String[] tVals;", "public java.util.HashMap tDrafts;", "public String[] tAdd;", "public java.util.ArrayList items;",
          "public String histFile;", "public String[] histIds;", "public String[] histFiles;", "public String histPreview;", "public String logMod;",
          "public java.util.ArrayList logShown;", "public String[] logTabs;", "public boolean ioAll;", "public String ioScope;", "public String ioCode;",
          "public String ioImport;", "public String ioPreview;", "public String ioPreviewCode;", "public java.util.ArrayList ioPlan;",
          "public int ioPlanTotal;", "public String[] ioFiles;", "public java.util.ArrayList evKeys;", "public java.util.ArrayList evSels;",
          "public java.util.ArrayList fT;", "public java.util.ArrayList fA;", "public java.util.ArrayList fW;"):
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
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.AdmSaveTask(name, text), 0L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { new @PKG@.AdmSaveTask(name, text).run(); }
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

# ================= RefreshTask: re-draw the menu shortly after a keep-open command ran (world thread) =================
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
    if (p == null || p.getPageManager().getCustomPage() != this.page) return;
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
  if (idx < 0 || idx >= 54) return;
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
M(page, r"""
public String profileBody() {
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map br = @PKG@.MenuUtil.bridge();
  StringBuilder sb = new StringBuilder();
  sb.append("Your SkyWynn profile, ").append(@PKG@.MenuUtil.safe(this.playerRef.getUsername())).append('.');
  sb.append("\nPurse: ").append(purseText());
  long bk = @PKG@.MenuUtil.bank(u);
  sb.append("\nBank: ").append(bk < 0L ? "open the Bank to load it" : @PKG@.MenuUtil.fmt(bk) + " coins");
  String sk = @PKG@.MenuUtil.skills(u);
  sb.append("\nSkills: ").append(sk == null ? "no skill data yet" : sk);
  sb.append("\nAccessory Bag: ").append(@PKG@.MenuUtil.csvCount(br.get("acc:has:" + u.toString()))).append(" bench accessories, ")
    .append(@PKG@.MenuUtil.csvCount(br.get("acc:tal:" + u.toString()))).append(" talismans");
  sb.append("\nRecipes unlocked by collections: ").append(@PKG@.MenuUtil.csvCount(br.get("coll:recipes:" + u.toString())));
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
M(page, r"""
public void fillStatic(java.util.ArrayList slots) {
  java.util.UUID me = this.playerRef.getUuid();
  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);
  for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {
    if (!@PKG@.MenuData.E_VIEW[i].equals(this.view)) continue;
    String act = @PKG@.MenuData.E_ACT[i];
    if ("admin".equals(act) && !admin) continue;
    if ("view:mods".equals(act) && !admin && !@PKG@.MenuCfg.MODS_HELP) continue;
    String name = @PKG@.MenuData.E_NAME[i];
    String body = @PKG@.MenuData.E_BODY[i];
    if ("profile".equals(act)) body = profileBody();
    if ("tips".equals(act)) name = name + (@PKG@.Tips.isOff(me) ? ": OFF" : ": ON");
    if (body.indexOf("%PURSE%") >= 0) body = body.replace("%PURSE%", purseText());
    if (body.indexOf("%BANK%") >= 0) body = body.replace("%BANK%", bankText());
    String c = cmdOf(act);
    boolean dim = c != null && @PKG@.MenuUtil.cmd(c) == null;
    String need = dim ? null : @PKG@.MenuUtil.needOf(lineOf(act));
    if (need != null) {
      put(slots, @PKG@.MenuData.E_SLOT[i], @PKG@.MenuData.E_ICON[i], name + " (update needed)", body, "Needs " + need + " on this server", act, true);
      continue;
    }
    put(slots, @PKG@.MenuData.E_SLOT[i], @PKG@.MenuData.E_ICON[i], name + (dim ? " (not installed)" : ""), body,
        dim ? "Not installed on this server" : @PKG@.MenuData.E_FOOT[i], act, dim);
  }
}""")
M(page, r"""
public void fillWarps(java.util.ArrayList slots) {
  @TPP@ tp = null;
  try { tp = @TPP@.get(); } catch (Throwable t) { }
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.Map warps = null;
  if (tp != null && tp.isWarpsLoaded()) {
    warps = tp.getWarps();
    java.util.Iterator it = warps.keySet().iterator();
    while (it.hasNext()) keys.add(String.valueOf(it.next()));
    java.util.Collections.sort(keys);
  }
  int per = @PKG@.MenuData.WARP_SLOTS.length;
  this.pages = paging(keys.size(), per);
  for (int i = 0; i < per; i++) {
    int k = this.pageNo * per + i;
    if (k >= keys.size()) break;
    String key = (String) keys.get(k);
    @WRP@ w = (@WRP@) warps.get(key);
    if (w == null) continue;
    String id = @PKG@.MenuUtil.safe(w.getId());
    String pos = "";
    try {
      @V3D@ p = w.getTransform().getPosition();
      pos = "\nX " + (long) Math.floor(p.x) + "   Y " + (long) Math.floor(p.y) + "   Z " + (long) Math.floor(p.z);
    } catch (Throwable t) { }
    boolean open = @PKG@.MenuUtil.isWarpUnlocked(this.playerRef, w.getId());
    put(slots, @PKG@.MenuData.WARP_SLOTS[i], @PKG@.MenuData.ICON_WARP, open ? id : id + " (locked)",
        "Warp " + id + ".\nWorld: " + @PKG@.MenuUtil.safe(w.getWorld()) + pos,
        open ? "Click to warp!" : "Locked - you have not unlocked this warp yet", open ? "warp:" + key : "locked:" + key, !open);
  }
  if (keys.isEmpty()) {
    put(slots, @PKG@.MenuData.NO_WARPS_SLOT, @PKG@.MenuData.ICON_WARP, "No warps yet",
        tp == null || warps != null ? "No warps have been set on this server yet.\nAn admin can stand somewhere and type /warp set [name]." : "The warp list is still loading.\nOpen this menu again in a moment.",
        null, "info", true);
  }
}""")
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
    put(slots, @PKG@.MenuData.NO_PLAYERS_SLOT, @PKG@.MenuData.ICON_PLAYER, "Player offline", "That player is no longer online.", "Click to go back", "back", true);
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
        @PKG@.MenuData.MOD_NAME[k] + " " + ver + (installed ? "" : " (not installed)"), @PKG@.MenuUtil.modBody(k),
        installed ? (cfg ? "Click to set up this mod" : "Click to show the commands below") : "Not installed on this server",
        cfg ? "modcfg:" + k : "mod:" + k, !installed);
  }
}""")
M(page, r"""
public void nav(java.util.ArrayList slots) {
  if (!this.view.equals("main")) {
    String back = this.view.equals("player") ? "Players Online" : "the SkyWynn Menu";
    put(slots, 45, @PKG@.MenuData.ICON_BACK, "Go Back", "Back to " + back + ".", "Click to go back", "back", false);
  }
  put(slots, 49, @PKG@.MenuData.ICON_CLOSE, "Close", "Close the menu.", "Click to close", "close", false);
  if (this.pages > 1) {
    if (this.pageNo > 0) put(slots, 48, @PKG@.MenuData.ICON_PREV, "Previous Page", "Page " + this.pageNo + " of " + this.pages + ".", "Click to go back a page", "prev", false);
    if (this.pageNo < this.pages - 1) put(slots, 50, @PKG@.MenuData.ICON_NEXT, "Next Page", "Page " + (this.pageNo + 2) + " of " + this.pages + ".", "Click for the next page", "next", false);
  }
}""")
M(page, r"""
public void fill(java.util.ArrayList slots) {
  int vi = @PKG@.MenuData.viewIndex(this.view);
  this.view = @PKG@.MenuData.V_KEY[vi];
  this.title = @PKG@.MenuData.V_TITLE[vi];
  this.pages = 1;
  fillStatic(slots);
  if (this.view.equals("tp")) fillWarps(slots);
  else if (this.view.equals("players")) fillPlayers(slots);
  else if (this.view.equals("player")) fillPlayer(slots);
  else if (this.view.equals("mods")) fillMods(slots);
  if (this.pages <= 1) this.pageNo = 0;
  nav(slots);
  if (this.pages > 1) this.title = this.title + "  (page " + (this.pageNo + 1) + " of " + this.pages + ")";
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.cleared = false;
  boolean tipsOff = @PKG@.Tips.isOff(this.playerRef.getUuid());
  this.acts = new String[54];
  this.names = new String[54];
  this.bodies = new String[54];
  java.util.ArrayList slots = new java.util.ArrayList();
  for (int i = 0; i < 54; i++) slots.add(filler());
  try { fill(slots); } catch (Throwable t) { @PKG@.MenuUtil.warn("menu view " + this.view + " failed: " + t); }
  b.appendInline((String) null, @PKG@.MenuData.UI_ROOT);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_ACCENT);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_TITLE);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_HINT);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_INFOBOX);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFONAME);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFODESC);
  for (int i = 0; i < @PKG@.MenuData.UI_INFO.length; i++) b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFO[i]);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GAP);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GRIDWRAP);
  b.appendInline("#SkyyMGridWrap", tipsOff ? @PKG@.MenuData.UI_GRIDNOTIPS : @PKG@.MenuData.UI_GRID);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_STATUS);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_FOOT);
  b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_LEAD);
  if (!this.view.equals("main")) {
    b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_BTNBACK);
    b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_SPACER);
    ev.addEventBinding(@BT@.Activating, "#SkyyMBack", @EVD@.of("a", "mback"));
  }
  if (this.pages > 1) {
    b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_BTNPREV);
    b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_SPACER);
    b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_BTNNEXT);
    b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_SPACER);
    ev.addEventBinding(@BT@.Activating, "#SkyyMPrev", @EVD@.of("a", "mprev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyMNext", @EVD@.of("a", "mnext"));
  }
  b.appendInline("#SkyyMFoot", @PKG@.MenuData.UI_BTNCLOSE);
  ev.addEventBinding(@BT@.Activating, "#SkyyMClose", @EVD@.of("a", "mclose"));
  b.set("#SkyyMTitle.Text", this.title == null ? "SkyWynn Menu" : this.title);
  b.set("#SkyyMHint.Text", tipsOff ? "Tooltips off - the book at the top right turns them on. Click an item to use it."
                                   : "Hover an item for details - click it to use it. Esc closes the menu.");
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
  int nInfo = @PKG@.MenuData.UI_INFO.length;
  for (int i = 0; i < nInfo; i++) {
    String t = i + 1 < lines.length ? lines[i + 1] : "";
    if (i == nInfo - 1 && lines.length > nInfo + 1) t = t + "   ...";
    b.set("#SkyyMInfo" + i + ".Text", t);
  }
  b.set("#SkyyMStatus.Text", this.status == null ? "" : this.status);
  b.set("#SkyyMGrid.Slots", slots);
  ev.addEventBinding(@BT@.SlotClicking, "#SkyyMGrid", @EVD@.of("a", "mslot"), false);
  ev.addEventBinding(@BT@.Dismissing, "#SkyyMenu", @EVD@.of("a", "mesc"), false);
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
    for (int i = 0; i < 54; i++) empty.add(new @IGS@());
    @UCB@ b = new @UCB@();
    b.set("#SkyyMGrid.Slots", empty);
    sendUpdate(b);
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
    if (p == null || p.getPageManager().getCustomPage() != this.page) return;
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
M(page, r"""
public boolean teleport(@REF@ ref, @ST@ st, @TP@ t, String label) {
  if (st.getComponent(ref, @TP@.getComponentType()) != null) { this.status = "You are already teleporting."; rebuild(); return false; }
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
  closePage(ref, st);
  this.playerRef.sendMessage(@MSG@.raw("[Menu] Teleporting to " + label + "..."));
  return true;
}""")
M(page, r"""
public void doSpawn(@REF@ ref, @ST@ st) {
  @WLD@ target = @UNI@.get().getDefaultWorld();
  if (target == null) { this.status = "The main world is not loaded."; rebuild(); return; }
  @TRF@ where = target.getWorldConfig().getSpawnProvider().getSpawnPoint(target, this.playerRef.getUuid());
  if (where == null) { this.status = "The main world has no spawn point."; rebuild(); return; }
  teleport(ref, st, @TP@.createForPlayer(target, where), "Spawn");
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
# 0.2: the torch (slot 51) opens the Settings page straight from the menu - never closing first (the 0.1.2 rule). The grid is emptied
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
M(page, r"""
public void click(@REF@ ref, @ST@ st, int idx, String act) {
  this.status = "";
  if (act.equals("close")) { closePage(ref, st); return; }
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
  if (act.startsWith("modcfg:")) {
    int mk = -1;
    try { mk = Integer.parseInt(act.substring(7)); } catch (Throwable t) { mk = -1; }
    if (mk >= 0 && mk < @PKG@.MenuData.MOD_NAME.length) { openAdmin(ref, st, @PKG@.MenuData.MOD_NAME[mk]); return; }
  }
  this.infoName = this.names[idx];
  this.infoBody = this.bodies[idx];
  if (act.equals("tips")) {
    java.util.UUID u = this.playerRef.getUuid();
    boolean off = !@PKG@.Tips.isOff(u);
    if (@PKG@.Tips.setOff(u, off) != 1) {
      this.infoName = @PKG@.Tips.isOff(u) ? "Hover Tooltips: OFF" : "Hover Tooltips: ON";
      this.status = @PKG@.MenuData.SET_TXT_BROKEN;
      rebuild();
      return;
    }
    this.infoName = off ? "Hover Tooltips: OFF" : "Hover Tooltips: ON";
    this.status = off ? "Hover tooltips are off - click an item and read it in the box above." : "Hover tooltips are on again.";
    rebuild();
    return;
  }
  if (act.equals("info") || act.equals("profile") || act.startsWith("mod:")) { rebuild(); return; }
  if (act.startsWith("locked:")) { this.status = "That warp is locked."; rebuild(); return; }
  if (act.startsWith("cmdc:")) { runCmd(ref, st, act.substring(5), true); return; }
  if (act.startsWith("cmd:")) { runCmd(ref, st, act.substring(4), false); return; }
  if (act.equals("spawn")) { doSpawn(ref, st); return; }
  if (act.startsWith("warp:")) { doWarp(ref, st, act.substring(5)); return; }
  if (act.startsWith("pact:")) { playerAction(ref, st, Integer.parseInt(act.substring(5))); return; }
  @PKG@.MenuUtil.warn("unknown menu action " + act);
}""")
# 0.1.3 "mesc" = the experimental Esc hook: never send anything here (a page the client already closed may not acknowledge it and
# PageManager would then drop every later click); CloseTask acts 150 ms later only while this menu is still the open page.
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    if (data.indexOf("mesc\"") >= 0) { new @PKG@.CloseTask(this, this.playerRef).accept(null, null); return; }
    if (data.indexOf("mclose\"") >= 0) { closePage(ref, st); return; }
    if (data.indexOf("mback\"") >= 0) { this.status = ""; goBack(); rebuild(); return; }
    if (data.indexOf("mprev\"") >= 0) { this.status = ""; if (this.pageNo > 0) this.pageNo = this.pageNo - 1; rebuild(); return; }
    if (data.indexOf("mnext\"") >= 0) { this.status = ""; this.pageNo = this.pageNo + 1; rebuild(); return; }
    if (data.indexOf("mslot\"") < 0) return;
    int idx = @PKG@.MenuUtil.jsonInt(data, "SlotIndex");
    if (idx < 0 || idx >= 54 || this.acts == null) { @PKG@.MenuUtil.info("unexpected slot payload: " + data); return; }
    String act = this.acts[idx];
    if (act == null) return;
    click(ref, st, idx, act);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu click failed: " + t); }
}""")

# ================= 0.2 SettingsPage (research/Settings-Spec.md 4.2-4.4): one inline page, tabs / rows switched with rebuild() =================
# Rows = the REGISTERED keys of the tab (SetReg.keysOf), sorted by SET_ORDER. Labels / help lines of other mods only go through b.set.
# Click payloads are matched with both quotes ("son1" can never match "son11" or "soff1"). No MouseEntered/Exited bindings, no timers:
# the armed Reset reverts on the next click; a change made elsewhere shows at the next click. The settings:def:* drain (a scan of the
# whole shared bridge map) runs once per opened page, on its first build - clicks only rebuild from SetReg.DEFS.
M(spg, r"""
public int firstTab() {
  for (int i = 0; i < @PKG@.MenuData.SET_CAT_ID.length; i++) if (@PKG@.SetReg.keysOf(i).length > 0) return i;
  return 0;
}""")
M(spg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  if (!this.drained) { this.drained = true; @PKG@.SetReg.drain(); }
  java.util.UUID u = this.playerRef.getUuid();
  int nCat = @PKG@.MenuData.SET_CAT_ID.length;
  if (this.cat < 0) this.cat = firstTab();
  if (this.cat >= nCat) this.cat = 0;
  String[] keys = @PKG@.SetReg.keysOf(this.cat);
  int per = @PKG@.MenuData.SET_ROWS;
  int pages = keys.length <= 0 ? 1 : (keys.length + per - 1) / per;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  this.rowKeys = new String[per];
  b.appendInline((String) null, @PKG@.MenuData.UI_SROOT);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SACCENT);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_STITLE);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SHINT);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_STABS0);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_STABS1);
  for (int i = 0; i < nCat; i++) {
    String par = i < 4 ? "#SkyyStgTabs0" : "#SkyyStgTabs1";
    if (i % 4 != 0) b.appendInline(par, @PKG@.MenuData.UI_SSP12);
    b.appendInline(par, i == this.cat ? @PKG@.MenuData.UI_STABSEL[i] : @PKG@.MenuData.UI_STAB[i]);
    ev.addEventBinding(@BT@.Activating, "#SkyyStgTab" + i, @EVD@.of("a", "stab" + i));
  }
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SGAP8);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SHEAD);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SROWS);
  for (int r = 0; r < per; r++) {
    int k = this.pageNo * per + r;
    if (k >= keys.length) break;
    String key = keys[k];
    this.rowKeys[r] = key;
    Object[] d = @PKG@.SetReg.info(key);
    Boolean v = @PKG@.SetStore.get(u, key);
    boolean on = v == null || v.booleanValue();
    String row = "#SkyyStgRow" + r;
    String txt = "#SkyyStgTxt" + r;
    b.appendInline("#SkyyStgRows", @PKG@.MenuData.UI_SROW[r]);
    b.appendInline(row, @PKG@.MenuData.UI_SSP14);
    b.appendInline(row, @PKG@.MenuData.UI_STXT[r]);
    b.appendInline(txt, @PKG@.MenuData.UI_SNAME[r]);
    b.appendInline(txt, @PKG@.MenuData.UI_SDESC[r]);
    b.appendInline(row, on ? @PKG@.MenuData.UI_SONSEL[r] : @PKG@.MenuData.UI_SON[r]);
    b.appendInline(row, @PKG@.MenuData.UI_SSP10);
    b.appendInline(row, on ? @PKG@.MenuData.UI_SOFF[r] : @PKG@.MenuData.UI_SOFFSEL[r]);
    b.appendInline("#SkyyStgRows", @PKG@.MenuData.UI_SGAP6);
    b.set("#SkyyStgName" + r + ".Text", d == null ? key : String.valueOf(d[2]));
    b.set("#SkyyStgDesc" + r + ".Text", d == null ? "" : String.valueOf(d[5]));
    ev.addEventBinding(@BT@.Activating, "#SkyyStgOn" + r, @EVD@.of("a", "son" + r));
    ev.addEventBinding(@BT@.Activating, "#SkyyStgOff" + r, @EVD@.of("a", "soff" + r));
  }
  if (keys.length == 0) {
    b.appendInline("#SkyyStgRows", @PKG@.MenuData.UI_SEMPTY);
    b.set("#SkyyStgEmpty.Text", @PKG@.MenuData.SET_TXT_EMPTY);
  }
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SALWAYS);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SSTATUS);
  b.appendInline("#SkyyStg", @PKG@.MenuData.UI_SFOOT);
  boolean armed = this.armedAt > 0L && System.currentTimeMillis() - this.armedAt <= 10000L;
  if (pages > 1) {
    b.appendInline("#SkyyStgFoot", @PKG@.MenuData.UI_SLEADB);
    b.appendInline("#SkyyStgFoot", @PKG@.MenuData.UI_SPREV);
    b.appendInline("#SkyyStgFoot", @PKG@.MenuData.UI_SSP10);
    b.appendInline("#SkyyStgFoot", @PKG@.MenuData.UI_SNEXT);
    b.appendInline("#SkyyStgFoot", @PKG@.MenuData.UI_SSP10);
    ev.addEventBinding(@BT@.Activating, "#SkyyStgPrev", @EVD@.of("a", "sprev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyStgNext", @EVD@.of("a", "snext"));
  } else {
    b.appendInline("#SkyyStgFoot", @PKG@.MenuData.UI_SLEADA);
  }
  b.appendInline("#SkyyStgFoot", armed ? @PKG@.MenuData.UI_SRESETARM : @PKG@.MenuData.UI_SRESET);
  b.appendInline("#SkyyStgFoot", @PKG@.MenuData.UI_SSP10);
  b.appendInline("#SkyyStgFoot", @PKG@.MenuData.UI_SMENU);
  b.appendInline("#SkyyStgFoot", @PKG@.MenuData.UI_SSP10);
  b.appendInline("#SkyyStgFoot", @PKG@.MenuData.UI_SCLOSE);
  ev.addEventBinding(@BT@.Activating, "#SkyyStgReset", @EVD@.of("a", "sreset"));
  ev.addEventBinding(@BT@.Activating, "#SkyyStgMenu", @EVD@.of("a", "smenu"));
  ev.addEventBinding(@BT@.Activating, "#SkyyStgClose", @EVD@.of("a", "sclose"));
  int n = keys.length;
  b.set("#SkyyStgHint.Text", @PKG@.MenuData.SET_TXT_HINT);
  b.set("#SkyyStgHead.Text", @PKG@.MenuData.SET_HEAD[this.cat] + "   -   " + n + (n == 1 ? " setting" : " settings")
      + (pages > 1 ? "   -   page " + (this.pageNo + 1) + " of " + pages : ""));
  b.set("#SkyyStgAlways.Text", @PKG@.MenuData.SET_ALWAYS[this.cat]);
  String stt = this.status == null ? "" : this.status;
  if (stt.length() == 0 && @PKG@.SetStore.isBroken(u)) stt = @PKG@.MenuData.SET_TXT_BROKEN;
  b.set("#SkyyStgStatus.Text", stt);
}""")
M(spg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
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
    for (int i = 0; i < @PKG@.MenuData.SET_CAT_ID.length; i++) {
      if (data.indexOf("\"stab" + i + "\"") >= 0) { this.cat = i; this.pageNo = 0; this.status = ""; rebuild(); return; }
    }
    if (data.indexOf("\"sprev\"") >= 0) { if (this.pageNo > 0) this.pageNo = this.pageNo - 1; this.status = ""; rebuild(); return; }
    if (data.indexOf("\"snext\"") >= 0) { this.pageNo = this.pageNo + 1; this.status = ""; rebuild(); return; }
    for (int r = 0; r < this.rowKeys.length; r++) {
      boolean hitOn = data.indexOf("\"son" + r + "\"") >= 0;
      boolean hitOff = !hitOn && data.indexOf("\"soff" + r + "\"") >= 0;
      if (!hitOn && !hitOff) continue;
      String key = this.rowKeys[r];
      if (key == null) { rebuild(); return; }
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
  return a.length > 2 && a[2] instanceof String ? (String) a[2] : "";
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
# every mod that publishes a readable config:def:<Mod> (the pull model: scanned at every build, so load order never matters)
M(apg, r"""
public static String[] cfgMods() {
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    java.util.Iterator it = new java.util.ArrayList(@MU@.bridge().keySet()).iterator();
    while (it.hasNext()) {
      Object k = it.next();
      if (!(k instanceof String) || !((String) k).startsWith("config:def:")) continue;
      String m = ((String) k).substring(11);
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
M(apg, r"""
public static java.util.ArrayList hitsOf(Object[] h, String q) {
  java.util.ArrayList out = new java.util.ArrayList();
  String[] ids = catIds(h);
  for (int i = 0; i < ids.length; i++) if (has(catLabel(h, i), q)) out.add("tab " + catLabel(h, i));
  Object[] rs = rowsOf(h);
  for (int i = 0; i < rs.length; i++) {
    Object[] r = rowAt(h, i);
    if (r != null && (has(rv(r, 1), q) || has(rv(r, 10), q))) out.add(rv(r, 1));
  }
  return out;
}""")
M(apg, r"""
public static int firstHit(Object[] h, String q) {
  Object[] rs = rowsOf(h);
  for (int i = 0; i < rs.length; i++) {
    Object[] r = rowAt(h, i);
    if (r != null && (has(rv(r, 1), q) || has(rv(r, 10), q))) return i;
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
# ---- frame: accent, title, subtitle, the fixed body group; tail: status (4 colours) + a centred footer
M(apg, r"""
public void frame(@UCB@ b, String title, String sub) {
  b.appendInline((String) null, @MD@.UI_AROOT);
  b.appendInline("#SkyyAdm", @MD@.UI_AACCENT);
  b.appendInline("#SkyyAdm", @MD@.UI_ATITLE);
  b.appendInline("#SkyyAdm", @MD@.UI_ASUB);
  b.appendInline("#SkyyAdm", @MD@.UI_ABODY);
  b.set("#SkyyAdmTitle.Text", title == null ? "" : title);
  b.set("#SkyyAdmSub.Text", sub == null ? "" : sub);
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
  b.appendInline("#SkyyAdm", @MD@.UI_ASTATUS[k]);
  b.set("#SkyyAdmStatus.Text", firstLine(this.status));
  b.appendInline("#SkyyAdm", @MD@.UI_AFOOT);
  int total = 0;
  for (int i = 0; i < this.fW.size(); i++) total = total + ((Integer) this.fW.get(i)).intValue() + (i > 0 ? 8 : 0);
  if (total > @MD@.ADM_INNER) @MU@.warn("server setup footer is " + total + " px wide");
  int lead = (@MD@.ADM_INNER - total) / 2;
  if (lead > 0) b.appendInline("#SkyyAdmFoot", spc(lead, 50));
  for (int i = 0; i < this.fT.size(); i++) {
    if (i > 0) b.appendInline("#SkyyAdmFoot", spc(8, 50));
    String id = "SkyyAdmF" + i;
    b.appendInline("#SkyyAdmFoot", btn(id, ((Integer) this.fW.get(i)).intValue(), 50, (String) this.fT.get(i), @MD@.ADM_BS));
    bind(ev, id, (String) this.fA.get(i));
  }
}""")
M(apg, r"""
public void tabRow(@UCB@ b, @UEB@ ev, int i, String label, boolean sel, String act) {
  String par = i < 8 ? "#SkyyAdmTabs0" : "#SkyyAdmTabs1";
  if (i % 8 != 0) b.appendInline(par, spc(8, 48));
  b.appendInline(par, btn("SkyyAdmTab" + i, 126, 48, @MU@.clip(label, 14), sel ? @MD@.ADM_SEL16 : @MD@.ADM_BS16));
  bind(ev, "SkyyAdmTab" + i, act + i);
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
  return new String[] { m, "file", name, @MD@.MOD_FLINE[k], rl, "0" };
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
    seen.add(cm[i]);
    String[] e = cfgRow(cm[i], hdr(cm[i]), find ? q : null);
    if (e == null) continue;
    keys.add("0" + cm[i].toLowerCase() + "\t" + found.size());
    found.add(e);
  }
  for (int k = 0; k < @MD@.MOD_NAME.length; k++) {
    String m = @MD@.MOD_NAME[k];
    if (seen.contains(m) || !installed(k)) continue;
    if (find && !has(m, q)) continue;
    keys.add("1" + m.toLowerCase() + "\t" + found.size());
    found.add(fileRow(k));
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
  int per = @MD@.ADM_LROWS;
  int pages = lr.size() <= 0 ? 1 : (lr.size() + per - 1) / per;
  if (this.listPage >= pages) this.listPage = pages - 1;
  if (this.listPage < 0) this.listPage = 0;
  String q = this.search == null ? "" : this.search.trim();
  int ncfg = 0;
  int nfile = 0;
  for (int i = 0; i < lr.size(); i++) { if ("cfg".equals(((String[]) lr.get(i))[1])) ncfg++; else nfile++; }
  String sub = @MD@.ADM_LISTSUB;
  if (q.length() < 2 && nfile > 0) sub = ncfg + (ncfg == 1 ? " mod is" : " mods are") + " set up for in-game editing - the rest show their file. Click Open.";
  if (q.length() >= 2 && this.status.length() == 0) {
    if (lr.isEmpty()) setStatus("Nothing matches \"" + q + "\" - mods not set up yet are matched by name only.", 2);
    else setStatus(lr.size() + (lr.size() == 1 ? " mod matches" : " mods match") + " \"" + q + "\" - Open shows the first hit.", 0);
  }
  evReset();
  evField("Find", "SkyyAdmFind");
  frame(b, "Server Setup", sub);
  b.appendInline("#SkyyAdmBody", @MD@.UI_ALSEARCH);
  b.appendInline("#SkyyAdmSearch", spc(140, 50));
  field(b, "#SkyyAdmSearch", "SkyyAdmFind", 520, 50, 60, q, "search settings and editors");
  b.appendInline("#SkyyAdmSearch", spc(10, 50));
  b.appendInline("#SkyyAdmSearch", btn("SkyyAdmFindGo", 130, 50, "Search", @MD@.ADM_BS));
  b.appendInline("#SkyyAdmSearch", spc(10, 50));
  b.appendInline("#SkyyAdmSearch", btn("SkyyAdmFindClr", 130, 50, "Clear", @MD@.ADM_BS));
  bind(ev, "SkyyAdmFindGo", "afind");
  bind(ev, "SkyyAdmFindClr", "aclear");
  bindEnter(ev, "SkyyAdmFind", "afind");
  b.appendInline("#SkyyAdmBody", @MD@.UI_ALROWS);
  this.listMods = new String[per];
  this.listReload = new String[per];
  for (int r = 0; r < per; r++) {
    int k = this.listPage * per + r;
    if (k >= lr.size()) break;
    String[] e = (String[]) lr.get(k);
    this.listMods[r] = e[0];
    this.listReload[r] = e[4];
    String rsel = "#SkyyAdmLRow" + r;
    b.appendInline("#SkyyAdmLRows", @MD@.UI_ALROW[r]);
    b.appendInline(rsel, spc(14, 52));
    b.appendInline(rsel, @MD@.UI_ALTXT[r]);
    b.appendInline("#SkyyAdmLTxt" + r, @MD@.UI_ALNAME[r]);
    b.appendInline("#SkyyAdmLTxt" + r, "1".equals(e[5]) ? @MD@.UI_ALDESCRED[r] : @MD@.UI_ALDESC[r]);
    b.set("#SkyyAdmLName" + r + ".Text", e[2]);
    b.set("#SkyyAdmLDesc" + r + ".Text", @MU@.clip(e[3], 118));
    b.appendInline(rsel, spc(10, 52));
    b.appendInline(rsel, btn("SkyyAdmLOpen" + r, 150, 52, "Open", @MD@.ADM_BS));
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
  if (pages > 1) { foot("< Prev", "aprev", 120); foot("Next >", "anext", 120); }
  foot("Changes", "achanges", 150);
  foot("Export all", "aexpall", 150);
  foot("Refresh", "arefresh", 130);
  foot("< SkyWynn Menu", "amenu", 200);
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
  if (draft != null && val != null && draft.trim().equals(val)) { this.drafts.remove(key); draft = null; }
  String rsel = "#SkyyAdmRow" + r;
  String line = "#SkyyAdmLine" + r;
  String wsel = "#SkyyAdmW" + r;
  b.appendInline("#SkyyAdmRows", @MD@.UI_AROW[r]);
  b.appendInline(rsel, @MD@.UI_ALINE[r]);
  b.appendInline(line, spc(14, 42));
  b.appendInline(line, @MD@.UI_ANAME[r]);
  b.appendInline(line, spc(10, 42));
  b.appendInline(line, @MD@.UI_AW[r]);
  b.appendInline(line, spc(10, 42));
  boolean def = false;
  if (type.equals("table")) {
    Object k = null;
    if (ok) k = call(this.mod, new Object[] { "keys", key, "" });
    int n = (k instanceof Object[] && ((Object[]) k).length > 0 && ((Object[]) k)[0] instanceof String[]) ? ((String[]) ((Object[]) k)[0]).length : 0;
    b.appendInline(wsel, btn("SkyyAdmEdit" + r, 240, 42, "Open - " + n + (n == 1 ? " entry" : " entries"), @MD@.ADM_BS));
    bind(ev, "SkyyAdmEdit" + r, "aedit" + r);
  } else if (type.equals("items")) {
    int n = csv(val).size();
    b.appendInline(wsel, btn("SkyyAdmEdit" + r, 240, 42, (ro ? "Open - " : "Edit - ") + n + (n == 1 ? " item" : " items"), @MD@.ADM_BS));
    bind(ev, "SkyyAdmEdit" + r, "aedit" + r);
    def = !ro;
  } else if (type.equals("link")) {
    b.appendInline(wsel, btn("SkyyAdmEdit" + r, 240, 42, "Open", @MD@.ADM_BS));
    bind(ev, "SkyyAdmEdit" + r, "alink" + r);
  } else if (ro) {
    b.appendInline(wsel, @MD@.UI_ARO[r]);
    b.set("#SkyyAdmRo" + r + ".Text", type.equals("action") ? "(admins with " + hs(h, 4) + " can run it)" : disp(w, val));
  } else if (type.equals("bool")) {
    boolean on = "true".equals(val);
    b.appendInline(wsel, btn("SkyyAdmOn" + r, 120, 42, "ON", on ? @MD@.ADM_ONSEL : @MD@.ADM_BS));
    b.appendInline(wsel, spc(10, 42));
    b.appendInline(wsel, btn("SkyyAdmOff" + r, 120, 42, "OFF", on ? @MD@.ADM_BS : @MD@.ADM_OFFSEL));
    bind(ev, "SkyyAdmOn" + r, "aon" + r);
    bind(ev, "SkyyAdmOff" + r, "aoff" + r);
    def = true;
  } else if (typed(type)) {
    String step = (type.equals("int") || type.equals("dec")) ? stepOf(opts) : null;
    field(b, wsel, "SkyyAdmVal" + r, step != null ? 156 : 270, 42, 2000, draft != null ? draft : (val == null ? "" : val), "");
    b.appendInline(wsel, spc(6, 42));
    b.appendInline(wsel, btn("SkyyAdmSet" + r, step != null ? 84 : 104, 42, "Set", @MD@.ADM_BS));
    bind(ev, "SkyyAdmSet" + r, "aset" + r);
    bindEnter(ev, "SkyyAdmVal" + r, "aset" + r);
    if (step != null) {
      b.appendInline(wsel, spc(6, 42));
      b.appendInline(wsel, btn("SkyyAdmMinus" + r, 60, 42, "Less", @MD@.ADM_BS));
      b.appendInline(wsel, spc(6, 42));
      b.appendInline(wsel, btn("SkyyAdmPlus" + r, 60, 42, "More", @MD@.ADM_BS));
      bind(ev, "SkyyAdmMinus" + r, "aminus" + r);
      bind(ev, "SkyyAdmPlus" + r, "aplus" + r);
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
        bind(ev, id, "ach" + r + "x" + j);
      }
    } else {
      String shown = val == null ? "" : val;
      for (int j = 0; j < vs.length; j++) if (vs[j].equals(val)) shown = ls[j];
      b.appendInline(wsel, btn("SkyyAdmCl" + r, 50, 42, "<", @MD@.ADM_BS));
      b.appendInline(wsel, spc(6, 42));
      b.appendInline(wsel, @MD@.UI_ACHV[r]);
      b.appendInline(wsel, spc(6, 42));
      b.appendInline(wsel, btn("SkyyAdmCr" + r, 50, 42, ">", @MD@.ADM_BS));
      b.set("#SkyyAdmChv" + r + ".Text", shown);
      bind(ev, "SkyyAdmCl" + r, "acl" + r);
      bind(ev, "SkyyAdmCr" + r, "acr" + r);
    }
    def = true;
  } else if (type.equals("action")) {
    b.appendInline(wsel, btn("SkyyAdmEdit" + r, 380, 42, opts, hasFlag(w, "danger") ? @MD@.ADM_RED : @MD@.ADM_BS));
    bind(ev, "SkyyAdmEdit" + r, "aact" + r);
  } else {
    b.appendInline(wsel, @MD@.UI_ARO[r]);
    b.set("#SkyyAdmRo" + r + ".Text", disp(w, val));
  }
  if (def) {
    b.appendInline(line, btn("SkyyAdmDef" + r, 110, 42, "Default", @MD@.ADM_BS));
    bind(ev, "SkyyAdmDef" + r, "adef" + r);
  } else b.appendInline(line, spc(110, 42));
  b.appendInline(rsel, @MD@.UI_AHELP[r]);
  b.appendInline("#SkyyAdmHelpRow" + r, spc(14, 22));
  b.appendInline("#SkyyAdmHelpRow" + r, @MD@.UI_ADESC[r]);
  boolean hit = q.length() >= 2 && (has(label, q) || has(rv(w, 10), q));
  String unit = rv(w, 8);
  String tg = tagOf(w);
  String nm = (hit ? "> " : "") + label + (unit.length() > 0 ? " (" + unit + ")" : "") + (draft != null ? " *" : "");
  String help = rv(w, 10);
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
  frame(b, "Server Setup - " + nm + (live != null ? " " + live : ""), k < 0 ? "This mod has no settings page on this server." : "Not set up for in-game editing yet - edit its file, then reload it.");
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
    txt.add("Its settings show up here, with buttons, once its next version is set up for in-game editing."); bold.add("0");
  }
  b.appendInline("#SkyyAdmBody", @MD@.UI_AINFO);
  for (int i = 0; i < txt.size() && i < @MD@.ADM_INFOLINES; i++) {
    b.appendInline("#SkyyAdmInfo", "1".equals(bold.get(i)) ? @MD@.UI_AINFOB[i] : @MD@.UI_AINFOL[i]);
    b.set("#SkyyAdmInfo" + i + ".Text", (String) txt.get(i));
  }
  fReset();
  String rl = k >= 0 ? @MD@.MOD_RELOAD[k] : "";
  if (rl.length() > 0 && @MU@.cmd(@MU@.firstWord(rl)) != null) foot("Reload", "afrel", 150);
  foot("< Mods", "amods", 150);
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
  if (this.cat >= nCat) this.cat = nCat - 1;
  if (this.cat < 0) this.cat = 0;
  int[] vis = visible(h);
  int per = @MD@.ADM_ROWS;
  int pages = vis.length <= 0 ? 1 : (vis.length + per - 1) / per;
  if (this.modPage >= pages) this.modPage = pages - 1;
  if (this.modPage < 0) this.modPage = 0;
  evReset();
  this.rowKeys = new String[per];
  for (int r = 0; r < per; r++) {
    int k = this.modPage * per + r;
    if (k >= vis.length) break;
    Object[] w = rowAt(h, vis[k]);
    this.rowKeys[r] = rv(w, 0);
    if (ok && edit && !hasFlag(w, "ro") && typed(rv(w, 3))) evField("V" + r, "SkyyAdmVal" + r);
  }
  String sub = fileLine(h);
  if (!contractOk(h)) sub = @MD@.ADM_NEWER;
  else if (!alive(this.mod)) sub = this.mod + " is not running - its settings cannot be changed now.";
  else if (!editor) sub = "View only - changing " + this.mod + " needs " + node + ".";
  frame(b, "Server Setup - " + hs(h, 2) + " (" + this.mod + " " + hs(h, 3) + ")", sub);
  b.appendInline("#SkyyAdmBody", @MD@.UI_ATABS0);
  if (nCat > 8) b.appendInline("#SkyyAdmBody", @MD@.UI_ATABS1);
  for (int i = 0; i < nCat && i < 16; i++) tabRow(b, ev, i, catLabel(h, i), i == this.cat, "atab");
  b.appendInline("#SkyyAdmBody", @MD@.UI_AGAP8);
  b.appendInline("#SkyyAdmBody", @MD@.UI_AHEAD);
  b.appendInline("#SkyyAdmBody", @MD@.UI_AROWS);
  String q = this.search == null ? "" : this.search.trim();
  for (int r = 0; r < per; r++) {
    int k = this.modPage * per + r;
    if (k >= vis.length) break;
    drawRow(b, ev, h, vis[k], r, edit, ok, q);
  }
  int adv = hiddenAdv(h);
  if (vis.length == 0) {
    b.appendInline("#SkyyAdmRows", @MD@.UI_AEMPTY);
    b.set("#SkyyAdmEmpty.Text", adv > 0 ? "Only advanced settings on this tab - switch Advanced to ON (footer button) to show them." : "Nothing on this tab.");
  }
  int n = vis.length;
  b.set("#SkyyAdmHead.Text", catLabel(h, this.cat) + "   -   " + n + (n == 1 ? " setting" : " settings")
      + (pages > 1 ? "   -   page " + (this.modPage + 1) + " of " + pages : "") + (adv > 0 ? "   -   " + adv + " advanced hidden" : ""));
  if (this.status.length() == 0 && ok) {
    Object st = call(this.mod, new Object[] { "status" });
    if (st instanceof String[] && ((String[]) st).length >= 2 && !"ok".equals(((String[]) st)[0])) {
      String s0 = ((String[]) st)[0];
      setStatus(((String[]) st)[1], "restart".equals(s0) ? 2 : 3);
    } else if (hs(h, 9).length() > 0) setStatus(hs(h, 9), 0);
  }
  fReset();
  if (pages > 1) { foot("< Prev", "aprev", 90); foot("Next >", "anext", 90); }
  foot("History", "ahist", 120);
  foot("Export / Import", "aio", 180);
  if (edit) foot("Reload file", "areload", 140);
  foot(this.showAdv ? "Advanced ON" : "Advanced OFF", "aadv", 160);
  foot("< Mods", "amods", 110);
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
  int per = @MD@.ADM_ROWS;
  int pages = eks.size() <= 0 ? 1 : (eks.size() + per - 1) / per;
  if (this.tPage >= pages) this.tPage = pages - 1;
  if (this.tPage < 0) this.tPage = 0;
  boolean typeAdd = edit && (mode.equals("type") || mode.equals("both"));
  boolean heldAdd = edit && (mode.equals("held") || mode.equals("both"));
  int[] cw = colW(cols.length);
  evReset();
  evField("TF", "SkyyAdmTFind");
  this.tKeys = new String[per];
  this.tVals = new String[per];
  for (int r = 0; r < per; r++) {
    int k = this.tPage * per + r;
    if (k >= eks.size()) break;
    this.tKeys[r] = (String) eks.get(k);
    this.tVals[r] = (String) evs.get(k);
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
      + (flt.length() > 0 ? " match" : "") + (pages > 1 ? "   -   page " + (this.tPage + 1) + " of " + pages : ""));
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
  b.appendInline("#SkyyAdmBody", @MD@.UI_ATROWS);
  boolean canRemove = edit && (itemsMode || !mode.equals("none"));
  for (int r = 0; r < per; r++) {
    String e = this.tKeys[r];
    if (e == null) break;
    String rsel = "#SkyyAdmTRow" + r;
    b.appendInline("#SkyyAdmTRows", @MD@.UI_ATROW[r]);
    b.appendInline(rsel, spc(14, 52));
    b.appendInline(rsel, @MD@.UI_ATKEY[r]);
    b.set("#SkyyAdmTKey" + r + ".Text", @MU@.clip(itemsMode ? e : entryLabel(e), 30));
    b.appendInline(rsel, spc(10, 52));
    b.appendInline(rsel, @MD@.UI_ATCELLS[r]);
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
  if (pages > 1) { foot("< Prev", "aprev", 120); foot("Next >", "anext", 120); }
  if (itemsMode && edit) { foot("Save list", "tsave", 150); foot("Undo edits", "tundo", 150); }
  foot("< Back", "aback", 130);
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
  int per = @MD@.ADM_GROWS;
  int pages = all.size() <= 0 ? 1 : (all.size() + per - 1) / per;
  if (this.logPage >= pages) this.logPage = pages - 1;
  if (this.logPage < 0) this.logPage = 0;
  frame(b, "Server Setup - Changes", "Every change made in game, by command or by hand, newest first. Undo puts one value back.");
  b.appendInline("#SkyyAdmBody", @MD@.UI_ATABS0);
  if (tabs.length > 8) b.appendInline("#SkyyAdmBody", @MD@.UI_ATABS1);
  for (int i = 0; i < tabs.length && i < 16; i++) {
    String lbl = i == 0 ? "All" : hs((Object[]) hdrs.get(tabs[i]), 2);
    tabRow(b, ev, i, lbl, tabs[i].equals(this.logMod), "ltab");
  }
  b.appendInline("#SkyyAdmBody", @MD@.UI_AHEAD);
  String scope = this.logMod.length() == 0 ? "All mods" : hs((Object[]) hdrs.get(this.logMod), 2);
  b.set("#SkyyAdmHead.Text", scope + "   -   " + all.size() + (all.size() == 1 ? " change" : " changes") + (pages > 1 ? "   -   page " + (this.logPage + 1) + " of " + pages : ""));
  b.appendInline("#SkyyAdmBody", @MD@.UI_AGROWS);
  this.logShown = new java.util.ArrayList();
  for (int r = 0; r < per; r++) {
    int k = this.logPage * per + r;
    if (k >= all.size()) break;
    String s = (String) all.get(k);
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
    b.appendInline("#SkyyAdmGRows", @MD@.UI_AGROW[r]);
    b.appendInline(rsel, spc(14, 40));
    b.appendInline(rsel, @MD@.UI_AGTXT[r]);
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
  if (pages > 1) { foot("< Prev", "aprev", 120); foot("Next >", "anext", 120); }
  foot("Refresh", "arefresh", 130);
  foot("< Mods", "amods", 130);
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
  int per = prev ? 4 : @MD@.ADM_HROWS;
  int pages = lines.size() <= 0 ? 1 : (lines.size() + per - 1) / per;
  if (this.histPage >= pages) this.histPage = pages - 1;
  if (this.histPage < 0) this.histPage = 0;
  boolean edit = canEdit(hs(h, 4));
  frame(b, "History - " + hs(h, 2) + " (" + this.mod + ")", "Each config file keeps its newest versions. Preview one, then Restore it - a restore can be undone the same way.");
  if (fs.length > 1) {
    b.appendInline("#SkyyAdmBody", @MD@.UI_ATABS0);
    tabRow(b, ev, 0, "All files", this.histFile.length() == 0, "htab");
    for (int i = 0; i < fs.length && i < 7; i++) tabRow(b, ev, i + 1, baseName(fs[i]), fs[i].equals(this.histFile), "htab");
  }
  b.appendInline("#SkyyAdmBody", @MD@.UI_AHEAD);
  b.set("#SkyyAdmHead.Text", (this.histFile.length() == 0 ? "Every file" : this.histFile) + "   -   " + lines.size() + (lines.size() == 1 ? " version" : " versions")
      + (pages > 1 ? "   -   page " + (this.histPage + 1) + " of " + pages : ""));
  b.appendInline("#SkyyAdmBody", prev ? @MD@.UI_AHROWS4 : @MD@.UI_AHROWS8);
  this.histIds = new String[@MD@.ADM_HROWS];
  for (int r = 0; r < per; r++) {
    int k = this.histPage * per + r;
    if (k >= lines.size()) break;
    String[] f = (String[]) lines.get(k);
    this.histIds[r] = f[0];
    String when = f[2].length() >= 16 ? f[2].substring(0, 16) : f[2];
    String rsel = "#SkyyAdmHRow" + r;
    b.appendInline("#SkyyAdmHRows", @MD@.UI_AHROW[r]);
    b.appendInline(rsel, spc(14, 44));
    b.appendInline(rsel, @MD@.UI_AHTXT[r]);
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
  if (pages > 1) { foot("< Prev", "aprev", 120); foot("Next >", "anext", 120); }
  foot("Refresh", "arefresh", 130);
  foot("< Back", "aback", 130);
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
      : "Files in Skyy_SkyyMenu/imports (" + files.length + ")" + (files.length > @MD@.ADM_FROWS ? " - the first " + @MD@.ADM_FROWS + " by name:" : ":"));
  b.appendInline("#SkyyAdmBody", @MD@.UI_AIOFROWS);
  for (int r = 0; r < files.length && r < @MD@.ADM_FROWS; r++) {
    b.appendInline("#SkyyAdmIoFRows", @MD@.UI_AFROW[r]);
    b.appendInline("#SkyyAdmFRow" + r, spc(14, 42));
    b.appendInline("#SkyyAdmFRow" + r, @MD@.UI_AFTXT[r]);
    b.set("#SkyyAdmFTxt" + r + ".Text", files[r]);
    b.appendInline("#SkyyAdmFRow" + r, spc(10, 42));
    b.appendInline("#SkyyAdmFRow" + r, btn("SkyyAdmFPrev" + r, 130, 42, "Preview", @MD@.ADM_BS));
    bind(ev, "SkyyAdmFPrev" + r, "ifile" + r);
    b.appendInline("#SkyyAdmIoFRows", @MD@.UI_AGAP6);
  }
  fReset();
  foot("< Back", "aback", 150);
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
    if (v == null) v = cur(this.mod, key);
    if (v == null || v.trim().length() == 0) { setStatus("Type a value first.", 2); return false; }
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
  int t = tailNum(a, "ltab");
  if (t >= 0) { if (t < this.logTabs.length) this.logMod = this.logTabs[t]; this.logPage = 0; return; }
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
  int t = tailNum(a, "htab");
  if (t >= 0) { this.histFile = t == 0 || t > this.histFiles.length ? "" : this.histFiles[t - 1]; this.histPage = 0; this.histPreview = null; return; }
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

# ================= /modconfig (alias /serversetup) + the usage variant /modconfig <mod>; admins only (requirePermission, HANDOFF rule 1) =================
F(acmv, "public @RA@ modArg;")
C(acmv, r"""
public AdminModCmd() {
  super("Open one mod's settings in Server Setup: /modconfig <mod>");
  requirePermission(@MD@.ADMIN_NODE);
  this.modArg = withRequiredArg("mod", "a mod name, e.g. menu, bank or SkyyEconomy (Skyy is optional)", @ATY@.STRING);
}""")
M(acmv, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  String a = null;
  try { a = String.valueOf(ctx.get(this.modArg)); } catch (Throwable t) { a = null; }
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

# ================= MenuPageFactory (right-click on the menu item -> OpenCustomUI "SkyyMenu") =================
fac.addInterface(pool.get("java.util.function.Function"))
C(fac, "public MenuPageFactory() { }")
M(fac, r"""
public Object apply(Object o) {
  return new @PKG@.MenuPage((@PR@) o, "main");
}""")

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
        @PKG@.Given.markGiven(u);
        @PKG@.Given.SESSION.put(u, Boolean.TRUE);
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

# ================= GrantTask: give the menu item once (scheduler -> the player's world thread) =================
grt.addInterface(pool.get("java.lang.Runnable"))
F(grt, "public @PR@ pr;")
F(grt, "public @WLD@ expected;")
F(grt, "public int tries;")
C(grt, "public GrantTask(@PR@ pr) { this.pr = pr; this.expected = null; this.tries = 0; }")
M(grt, r"""
public void later(long ms) {
  this.expected = null;
  this.tries = this.tries + 1;
  if (this.tries < 30) @HSV@.SCHEDULED_EXECUTOR.schedule(this, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}""")
# 0 = given now, 1 = nothing to do (flag set / already has one), 2 = retry later, 3 = inventory full (retried next login)
M(grt, r"""
public int grantNow(java.util.UUID u) {
  if (@PKG@.Given.SESSION.containsKey(u)) return 1;
  if (!@PKG@.MenuCfg.GIVE_ITEM) { @PKG@.Given.SESSION.put(u, Boolean.TRUE); return 1; }
  if (@PKG@.Given.isGiven(u)) { @PKG@.Given.SESSION.put(u, Boolean.TRUE); return 1; }
  @REF@ r = this.pr.getReference();
  if (r == null || !r.isValid()) return 2;
  @ST@ st = r.getStore();
  if (st == null) return 2;
  @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
  if (p == null) return 2;
  if (@PKG@.MenuUtil.count(p, @PKG@.MenuData.ITEM_ID) > 0) { @PKG@.Given.markGiven(u); @PKG@.Given.SESSION.put(u, Boolean.TRUE); return 1; }
  if (@PKG@.MenuUtil.profileBusy(u)) return 2;
  @PKG@.Given.SESSION.put(u, Boolean.TRUE);
  if (@PKG@.MenuUtil.giveMenuItem(p)) {
    @PKG@.Given.markGiven(u);
    this.pr.sendMessage(@MSG@.raw("[SkyWynn] You got the SkyWynn Menu! Right-click it to open teleports, your bags, skills, the bazaar and more. Lost it? Type /skymenu."));
    return 0;
  }
  this.pr.sendMessage(@MSG@.raw("[SkyWynn] Your inventory is full, so you did not get the SkyWynn Menu item. Make room and type /skymenu."));
  return 3;
}""")
M(grt, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    java.util.UUID u = this.pr.getUuid();
    if (@PKG@.Given.SESSION.containsKey(u)) return;
    if (this.expected == null) {
      java.util.UUID wu = this.pr.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) { later(1000L); return; }
      this.expected = w;
      w.execute(this);
      return;
    }
    java.util.UUID wu2 = this.pr.getWorldUuid();
    @WLD@ now = wu2 == null ? null : @UNI@.get().getWorld(wu2);
    if (now != this.expected) { later(1000L); return; }
    if (@PKG@.Given.INFLIGHT.putIfAbsent(u, Boolean.TRUE) != null) return;
    int res = 2;
    try { res = grantNow(u); } catch (Throwable t) { @PKG@.MenuUtil.warn("menu item grant failed for " + u + ": " + t); res = 3; }
    @PKG@.Given.INFLIGHT.remove(u);
    if (res == 2) later(1000L);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu item grant task failed: " + t); }
}""")

# ================= MenuReady: PlayerReadyEvent (every world switch) -> GrantTask once per session =================
rdy.addInterface(pool.get("java.util.function.Consumer"))
C(rdy, "public MenuReady() { }")
M(rdy, r"""
public void accept(Object ev) {
  try {
    if (@PKG@.MenuUtil.firstCheck()) { @PKG@.MenuUtil.checkAliases(); @PKG@.MenuUtil.checkSettingsCmd(); @PKG@.MenuUtil.checkAdminCmd(); }
    @PRE@ e = (@PRE@) ev;
    @REF@ r = e.getPlayerRef();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.SetLoadTask.preload(pr);
    if (@PKG@.Given.SESSION.containsKey(pr.getUuid())) return;
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GrantTask(pr), 4L, java.util.concurrent.TimeUnit.SECONDS);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("ready handler failed: " + t); }
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
    @PKG@.Given.SESSION.keySet().retainAll(online);
    @PKG@.Tips.LEGACY.keySet().retainAll(online);
  } catch (Throwable t) { return; }
  try {
    @PKG@.SetStore.retryDirty();
    @PKG@.SetStore.pruneOffline(onlineK);
    @PKG@.SetReg.loadAdmin(false);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("settings upkeep failed: " + t); }
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
    @PKG@.Given.SESSION.remove(pr.getUuid());
  } catch (Throwable t) { }
}""")

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
C(pl, "public SkyyMenuPlugin(%s init) { super(init); }" % JPI)
M(pl, r"""
public void setup() {
  @PKG@.MenuUtil.LOG = getLogger();
  @PKG@.Given.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("given");
  @PKG@.Tips.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("notips");
  @PKG@.SetStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("settings");
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
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.MenuReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.MenuQuit());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SeenTick(), 30L, 30L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyMenu] """ + VERSION + r""" ready - /skymenu""" + "".join(" /" + a for a in ALIASES) + r""", right-click the SkyWynn Menu item; the item is given once per player; /settings (/skysettings): " + @PKG@.SetReg.DEFS.size() + " switch(es) registered so far; Server Setup: /modconfig (/serversetup) for admins");
}""")
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.SetStore.flushAll(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings flush at shutdown failed: " + t); }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { @PKG@.MenuUtil.warn("config kit flush at shutdown failed: " + t); }
  super.shutdown();
}""")

WRITE = (dat, utl, giv, mcfg, sreg, sst, ssv, tip, sld, sgf, srf, ssf, sdc, page, spg, apg, ast, ref_, clo_, fac, cmd, scmd, acmv, acmd, grt, rdy, seen, quit_, pl)
assert len(WRITE) == len(MADE) and all(any(c is w for w in WRITE) for c in MADE), "a pool.makeClass result is missing from the writeFile list"
for c in WRITE:
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
print("server setup: node %s, /%s /%s, SkyyMenu config rows: %s" % (ADMIN_NODE, ADMIN_CMD, ADMIN_ALIAS, ", ".join(r[0] for r in MENU_CFG_ROWS)))
print("settings: %d known keys (%d tabs), own: %s, template %d bytes" % (len(SET_ORDER), len(SET_TABS), ", ".join(k[0] for k in OWN_SETTINGS), len(SET_TEMPLATE)))

# ================= assets: the menu item + its name / description =================
look = look_of(MENU_ITEM_LOOK)
item = {
    "TranslationProperties": {"Name": "server.items.%s.name" % MENU_ITEM_ID, "Description": "server.items.%s.description" % MENU_ITEM_ID},
    "Categories": ["Items.Tools"],
    "Icon": look["Icon"],
    "Quality": MENU_ITEM_QUALITY,
    "Tags": {"Type": ["Utility"]},
    "MaxStack": 1,
    "Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": PAGE_ID}}]}},
}
for k in VISUAL_KEYS:
    if k in look:
        item[k] = look[k]
lang = [
    "items.%s.name=%s" % (MENU_ITEM_ID, MENU_ITEM_NAME), "server.items.%s.name=%s" % (MENU_ITEM_ID, MENU_ITEM_NAME),
    "items.%s.description=%s" % (MENU_ITEM_ID, MENU_ITEM_DESC), "server.items.%s.description=%s" % (MENU_ITEM_ID, MENU_ITEM_DESC),
]
files = {
    "Server/Item/Items/Utility/%s.json" % MENU_ITEM_ID: json.dumps(item, indent=2),
    "Server/Languages/en-US/server.lang": "\n".join(lang) + "\n",
}
print("menu item:", MENU_ITEM_ID, "looks like", MENU_ITEM_LOOK, "icon", look["Icon"])
print("entries:", len(ENTRIES), "player actions:", len(PLAYER_ACTIONS), "mods:", len(MODS))

jar = os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyyMenu", VERSION, "SkyWynn menu (Hypixel SkyBlock style): right-click the SkyWynn Menu item or /skymenu for teleports and warps, island menu, Pocket Dimension, Vault, Accessory Bag, HUD editor, crafting, skills, collections, bazaar, auction house, bank, reforge, players, party, guild, a list of every mod with its commands, /settings (every mod's chat messages on or off, per player) and Server Setup for admins (/modconfig: every Skyy mod's settings in game). Zero dependencies.", PKG + ".SkyyMenuPlugin"), OUT, files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyMenu.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyMenu" % VERSION, disable_prefix="Skyy:")
