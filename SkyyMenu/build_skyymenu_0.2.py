"""SkyyMenu 0.1 - build script (javassist via jpype).
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

VERSION = "0.2"
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
     "desc": "The all-in-one SkyWynn menu: teleports, your island menu, Pocket Dimension, Vault, Accessory Bag, the HUD editor, crafting, skills, collections, the bazaar, the auction house, the bank, reforging, players, your party and guild, your settings and this list of mods.",
     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item",
                  "/settings (or /skysettings) - turn chat messages on or off"]},
    {"mod": "SkyyProfiles", "version": "0.1", "icon": "Deco_Book_Pile_Large", "check": "profiles",
     "desc": "SkyBlock-style profiles: each profile is its own save with its own class, island, inventory, coins, bank, bags, skills and collections.",
     "commands": ["/profiles (or /profile) - open your profiles", "/profiles create (or new) - a new profile, pick its class",
                  "/profiles switch <number or name> - switch to another profile", "/profiles list - your profiles in chat",
                  "/profileadmin info <player> - (admin) a player's profiles",
                  "/profileadmin setclass <player> <n> <class> - (admin) fix a class",
                  "/profileadmin reload - (admin) re-read the settings"]},
    {"mod": "SkyyIslands", "version": "0.5", "icon": "Soil_Grass", "check": "island",
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
     "desc": "Magic Bags: carry a Mining, Foraging, Farming, Combat or Smithing bag and what you gather of that type goes straight into your Pocket Dimension. /craft crafts from your inventory and bags (Smithing, Farming, Furnace, Tannery and more tabs).",
     "commands": ["/sacks (or /pd, /bags) - your Pocket Dimension, missing bags show recipes",
                  "/craft (or /recipes) - craft from your inventory and bags", "/craft <words> - open crafting with a search"]},
    {"mod": "SkyyAccessories", "version": "0.4.3", "icon": "Utility_Bag_Seed", "check": "accessories",
     "desc": "Your Accessory Bag: 9 slots for bench accessories (each unlocks its bench tab in /craft, the Campfire one cooks on the go) and stat talismans that work while they sit in the bag.",
     "commands": ["/accessories (or /acc, /accbag) - open your Accessory Bag"]},
    {"mod": "SkyyHud", "version": "0.3.9", "icon": "Deco_Map", "check": "skyyhud",
     "desc": "A customizable on-screen HUD: coordinates, zone, clocks, day counter, session timer, players online, coins, party and guild. Move, resize and colour every widget, save profiles or share your layout as a code.",
     "commands": ["/skyyhud (or /shud) - open the HUD editor", "/skyyhud export - print your layout as a code",
                  "/skyyhud import <code> - load a layout code", "/skyyhud reset - reset your layout",
                  "/skyyhud profile save|load|delete <name> - named layouts", "/skyyhud profile list - your saved layouts"]},
    {"mod": "SkyySkills", "version": "0.4.2", "icon": "Weapon_Sword_Iron", "check": "skills",
     "desc": "Hypixel-style skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill - that level up as you play and pay coins on every level up.",
     "commands": ["/skills (or /skill) - open your Skills", "/skills stats <skill> - the Stats page of a skill",
                  "/skills top <skill> - the top 10 players of a skill", "/skills quiet - hide the +XP chat messages",
                  "/skills reload - (admin) re-read the XP settings", "/skills xp <skill> <amount> - (admin) test XP"]},
    {"mod": "SkyyTrees", "version": "0.2.1", "icon": "Plant_Sapling_Maple", "check": "tree",
     "desc": "Skill trees: spend the points your skill levels earn on nodes for Mining, Foraging, Farming, Cooking, Acrobatics and Exploration.",
     "commands": ["/tree (or /trees) - open your skill trees", "/tree <skill> - open one tree, for example /tree mining",
                  "/tree quiet - hide the Tree bonus chat line", "/tree reload - (admin) re-read the tree settings"]},
    {"mod": "SkyyCollections", "version": "0.2.1", "icon": "Furniture_Village_Painting_1x1", "check": "collections",
     "desc": "Hypixel-style Collections: everything you gather counts toward tiers. Tiers unlock crafting recipes for the /craft page and pay rewards.",
     "commands": ["/collections (or /coll) - open your Collections", "/collections <name> - the tiers of one collection",
                  "/collections unlocks (or recipes) - the recipes you unlocked",
                  "/collections top <collection|score> - the top 10 players",
                  "/collections give <collection> <amount> - (admin) test credit",
                  "/collections reload - (admin) re-read the collection rules"]},
    {"mod": "SkyyCooking", "version": "0.1.1", "icon": "Food_Pie_Meat", "check": "cooking",
     "desc": "Cooking: dishes you cook at a Cooking Bench get a Grade from your Cooking level and skill tree - higher Grades heal and buff more.",
     "commands": ["/cooking - your Cooking level, Grade and tree chances",
                  "/cookadmin give <dish> <grade> - (admin) test dishes",
                  "/cookadmin campfire <dish> <count> - (admin) test the Campfire cook",
                  "/cookadmin reload - (admin) re-read the cooking settings"]},
    {"mod": "SkyyExploration", "version": "0.1", "icon": "Furniture_Human_Ruins_Chest_Small", "check": "explore",
     "desc": "Exploration: loot chests out in the world, uncover the map, discover zones and earn titles - all of it pays Exploration XP.",
     "commands": ["/explore (or /exploration, /discoveries) - your exploration page",
                  "/explore quiet - hide the chunk XP chat line", "/title (or /titles) - your titles",
                  "/title <name> or /title off - wear a title or none",
                  "/exploreadmin reload|stats|resetme - (admin)"]},
    {"mod": "SkyyClasses", "version": "0.1.4", "icon": "Weapon_Shortbow_Iron", "check": "class",
     "desc": "Classes: Archer, Warrior or Mage (Assassin and Shaman later). With SkyyProfiles the class is picked when you create a profile and locked to it.",
     "commands": ["/class (or /classes) - open the class page", "/classadmin set <player> <class> - (admin) give a class",
                  "/classadmin reset <player> - (admin) remove a class", "/classadmin info <player> - (admin) class data",
                  "/classadmin reload - (admin) re-read the settings"]},
    {"mod": "SkyyBazaar", "version": "0.1.2", "icon": "Rock_Gem_Emerald", "check": "bazaar",
     "desc": "A Hypixel-style Bazaar: instantly buy or sell dozens of resources against the server. Prices move as people trade.",
     "commands": ["/bazaar (or /bz) - open the Bazaar",
                  "/bazaaradmin price <itemId> <price> - (admin) set a price",
                  "/bazaaradmin reset|info <itemId|all> - (admin) reset or show prices",
                  "/bazaaradmin reload - (admin) re-read the product list"]},
    {"mod": "SkyyAuctions", "version": "0.1", "icon": "Ingredient_Bar_Gold", "check": "ah",
     "desc": "A Hypixel-style Auction House (Buy It Now): list an item for a fixed price, buy what other players list and claim the coins and items you are owed.",
     "commands": ["/ah (or /auction, /auctionhouse) - open the Auction House",
                  "/ah sell <price> [duration] - sell the item in your hand",
                  "/ah claim - claim your coins and items", "/ah manage - your listings and claims",
                  "/ah search <words> - search the listings",
                  "/ahadmin list|info|remove|reload|pause|resume - (admin)"]},
    {"mod": "SkyyBank", "version": "0.1.3", "icon": "Furniture_Ancient_Chest_Large_Treasure", "check": "bank",
     "desc": "A SkyBlock-style bank next to your coin purse: deposit coins to earn interest and withdraw them any time. Bank coins are never lost when you die.",
     "commands": ["/bank - open the bank page", "/bank deposit <n|all> - put coins in (500, 2k, 1.5m or all)",
                  "/bank withdraw <n|all> - take coins out", "/bank status - your bank and purse in chat",
                  "/bankconfig <percent> <minutes> - (admin) interest"]},
    {"mod": "SkyyCoins", "version": "0.1.5", "icon": "Rock_Gem_Ruby", "check": "balance",
     "desc": "The server's coins. Check your balance and pay other players. When you die you lose a set share of the coins in your purse (bank coins are safe).",
     "commands": ["/balance (or /bal, /coins, /purse) - your coins", "/pay <player> <amount> - send coins to a player",
                  "/coinsgive <amount> - (admin) give yourself coins", "/deathpenalty 5% or 5%-10% - (admin) coins lost on death"]},
    {"mod": "SkyyVault", "version": "0.1", "icon": "Furniture_Royal_Magic_Chest_Large", "check": "vault",
     "desc": "Your Vault: item storage shared by every profile you have, so you can move items from one profile to another. Buy more pages with coins.",
     "commands": ["/vault - open your Vault", "/vault <page> - open one vault page", "/vault buy - buy the next page (type it twice)",
                  "/vault info - your pages, slots used and the next price",
                  "/vaultadmin open|info|setpages <player> - (admin)"]},
    {"mod": "SkyyParty", "version": "0.1.3", "icon": "Deco_Scroll", "check": "party",
     "desc": "Team up with friends: invite players to a party, chat privately and see your party on the HUD. The lead passes on if the leader leaves.",
     "commands": ["/party (or /p) - open the party page", "/party invite <player> - invite a player",
                  "/party accept | decline - answer an invite", "/party leave - leave your party", "/party list - list your party",
                  "/party kick | promote <player> - (leader)", "/party disband - (leader) end the party", "/pc <message> - chat with your party"]},
    {"mod": "SkyyGuilds", "version": "0.1.1", "icon": "Furniture_Outlander_Banner", "check": "guild",
     "desc": "Guilds: found a guild with your friends - ranks, a shared guild bank, guild XP from your skills, guild levels and seasons.",
     "commands": ["/guild - open the guild page", "/guild create <name> - start a guild", "/guild invite <player> - (leader, admin) invite",
                  "/guild accept | decline | leave - answer an invite or leave",
                  "/guild bank deposit | withdraw <amount> | log - guild coins",
                  "/guild bank limit admin|member <n|0|none> - (leader) daily withdraw limit",
                  "/guild info | list - your guild | the top guilds", "/gc <message> - guild chat"]},
    {"mod": "SkyyEssentials", "version": "0.1.1", "icon": "Tool_Map", "check": "tpa",
     "desc": "Everyday commands the base game is missing: teleport requests between players and private messages.",
     "commands": ["/tpa <player> - ask to teleport to a player", "/tpahere <player> - ask a player to teleport to you",
                  "/tpaccept [player] - accept a teleport request", "/tpdeny [player] - deny a teleport request",
                  "/tpacancel - cancel your requests", "/msg <player> <message> (or /tell, /w) - private message",
                  "/reply <message> (or /r) - answer your last message", "/fly - (staff) toggle flight"]},
    {"mod": "SkyyRolls", "version": "0.1.4", "icon": "Weapon_Longsword_Copper", "check": "rolls",
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
    assert act in ("profile", "spawn", "info", "tips", "settings") or act.split(":", 1)[0] in ("view", "cmd", "cmdc"), "bad action " + act
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
with zipfile.ZipFile(B.SERVER_JAR) as zj:
    for n in zj.namelist():
        if n.startswith("com/hypixel/") and n.endswith(".class"):
            try:
                _cp = cp_utf8(zj.read(n))
                TAKEN |= set(WANT) & _cp
                if "skysettings" in _cp:
                    VANILLA_SKYSETTINGS.append(n)
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
             (T["PRE"], "getPlayerRef"), (T["PDE"], "getPlayerRef"), (T["HSV"], "SCHEDULED_EXECUTOR"), (T["CTX"], "provided")):
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
sreg = mk("SetReg")
sst  = mk("SetStore")
ssv  = mk("SetSaveTask")
tip  = mk("Tips")
sld  = mk("SetLoadTask")
sgf  = mk("SetGetFn")
srf  = mk("SetRegFn")
ssf  = mk("SetSetFn")
page = mk("MenuPage", T["PAGE"])
spg  = mk("SettingsPage", T["PAGE"])
ref_ = mk("RefreshTask")
clo_ = mk("CloseTask")
fac  = mk("MenuPageFactory")
cmd  = mk("MenuCmd", T["APC"])
scmd = mk("SettingsCmd", T["APC"])
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
    ADMIN = nx;
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
  for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {
    if (!@PKG@.MenuData.E_VIEW[i].equals(this.view)) continue;
    String act = @PKG@.MenuData.E_ACT[i];
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
  int per = @PKG@.MenuData.MOD_SLOTS.length;
  int n = @PKG@.MenuData.MOD_NAME.length;
  this.pages = paging(n, per);
  for (int i = 0; i < per; i++) {
    int k = this.pageNo * per + i;
    if (k >= n) break;
    String live = @PKG@.MenuUtil.liveVersion(@PKG@.MenuData.MOD_NAME[k]);
    boolean installed = live != null || @PKG@.MenuUtil.cmd(@PKG@.MenuData.MOD_CHECK[k]) != null;
    String ver = live != null ? live : @PKG@.MenuData.MOD_VER[k];
    put(slots, @PKG@.MenuData.MOD_SLOTS[i], @PKG@.MenuData.MOD_ICON[k],
        @PKG@.MenuData.MOD_NAME[k] + " " + ver + (installed ? "" : " (not installed)"), @PKG@.MenuUtil.modBody(k),
        installed ? "Click to show the commands below" : "Not installed on this server", "mod:" + k, !installed);
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
    if (@PKG@.MenuUtil.firstCheck()) { @PKG@.MenuUtil.checkAliases(); @PKG@.MenuUtil.checkSettingsCmd(); }
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
  java.util.Map br = @PKG@.MenuUtil.bridge();
  br.put("settings:fn:register", new @PKG@.SetRegFn());
  br.put("settings:fn:get", new @PKG@.SetGetFn());
  br.put("settings:fn:set", new @PKG@.SetSetFn());
  @PKG@.SetReg.registerOwn();
  @PKG@.SetReg.drain();
  @OCU@.registerSimple(this, @PKG@.SkyyMenuPlugin.class, @PKG@.MenuData.PAGE_ID, new @PKG@.MenuPageFactory());
  getCommandRegistry().registerCommand(new @PKG@.MenuCmd());
  getCommandRegistry().registerCommand(new @PKG@.SettingsCmd());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.MenuReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.MenuQuit());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SeenTick(), 30L, 30L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyMenu] """ + VERSION + r""" ready - /skymenu""" + "".join(" /" + a for a in ALIASES) + r""", right-click the SkyWynn Menu item; the item is given once per player; /settings (/skysettings): " + @PKG@.SetReg.DEFS.size() + " switch(es) registered so far");
}""")
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.SetStore.flushAll(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings flush at shutdown failed: " + t); }
  super.shutdown();
}""")

WRITE = (dat, utl, giv, sreg, sst, ssv, tip, sld, sgf, srf, ssf, page, spg, ref_, clo_, fac, cmd, scmd, grt, rdy, seen, quit_, pl)
assert len(WRITE) == len(MADE) and all(any(c is w for w in WRITE) for c in MADE), "a pool.makeClass result is missing from the writeFile list"
for c in WRITE:
    c.writeFile(OUT)
for c in MADE:
    _cf = os.path.join(OUT, *str(c.getName()).split(".")) + ".class"
    assert os.path.isfile(_cf), "class file not written: " + _cf
print("classes written:", len(WRITE))

# ================= post-build check: every inline UI string in the compiled MenuData class is intact =================
_md = open(os.path.join(OUT, "com", "skyy", "menu", "MenuData.class"), "rb").read()
_consts = cp_utf8(_md)
for s in list(UI.values()) + UI_INFO + SET_UI_ALL:
    assert s in _consts, "inline UI string missing from MenuData.class: " + s[:80]
print("inline UI strings verified in MenuData.class:", len(UI) + len(UI_INFO) + len(SET_UI_ALL))
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
B.assemble(jar, B.manifest("SkyyMenu", VERSION, "SkyWynn menu (Hypixel SkyBlock style): right-click the SkyWynn Menu item or /skymenu for teleports and warps, island menu, Pocket Dimension, Vault, Accessory Bag, HUD editor, crafting, skills, collections, bazaar, auction house, bank, reforge, players, party, guild, a list of every mod with its commands, and /settings (every mod's chat messages on or off, per player). Zero dependencies.", PKG + ".SkyyMenuPlugin"), OUT, files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyMenu.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyMenu" % VERSION, disable_prefix="Skyy:")
