"""SkyyMenu 0.1 - build script (javassist via jpype).
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
   The page is closed first when the command teleports or opens another page.
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

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))

# =====================================================================================================================
# ================================================  MENU DATA (edit me)  ==============================================
# =====================================================================================================================
# Text rules: no double quotes, braces, semicolons or backslashes. Write command arguments as <player> - they are shown as
# [player] because < > is tooltip markup. Each entry's text is a list of lines: the FIRST line is the description paragraph,
# the others are detail lines. Slots: 0-53, row by row (9 per row, 6 rows). Row 5: 45 = Back, 48 = Prev, 49 = Close, 50 = Next.
#
# Actions:  view:<main|tp|bank|players|party|mods>  open a submenu        cmdc:<command line>  close the menu, then run it
#           cmd:<command line>  run it, keep the menu open (refreshes)    spawn  teleport to the main world spawn
#           profile  show your stats in the info box                      info   just show the text in the info box

MENU_ITEM_ID = "Skyy_Menu"
MENU_ITEM_NAME = "SkyWynn Menu"
MENU_ITEM_LOOK = "Ingredient_Voidheart"      # vanilla item whose model / texture / icon / glow the menu item copies (not a backpack)
MENU_ITEM_QUALITY = "Epic"
MENU_ITEM_DESC = ("Right-click to open the SkyWynn Menu: teleports, your bags, the HUD editor, skills, the bazaar, the bank "
                  "and a list of every mod with its commands.\\n\\nLost it? Type /skymenu to get a new one.")
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
    ("bank",    "Bank",           ["Coins in the bank earn interest and are never lost when you die.",
                                   "Deposit or withdraw below, or type /bank."]),
    ("players", "Players Online", ["Click a player to send a teleport request, visit their island or invite them to your party.",
                                   "Teleport requests you receive can be accepted or denied at the bottom."]),
    ("player",  "Player",         ["What do you want to do with this player?"]),
    ("party",   "Party",          ["Parties let you play together and chat privately with /pc <message>."]),
    ("mods",    "Mods",           ["Every SkyWynn mod, what it does and all of its commands.",
                                   "Click a mod to show its commands here - hovering shows the same text."]),
]

# (view, slot, icon item id, name, text lines, tooltip footer or None, action)
ENTRIES = [
    # ---- main menu (Skyy's order: Teleport, Pocket Dimension, Accessory Bag, HUD editor, then the rest)
    ("main", 4,  "Armor_Iron_Head", "Your Profile", ["Your coins, bank, skill levels and accessories."], "Click to show your stats below", "profile"),
    ("main", 10, "Instance_Gateway", "Teleport", ["Travel to your island, the hub, the server spawn and every warp that is set."], "Click to open!", "view:tp"),
    ("main", 11, "Ingredient_Void_Essence", "Pocket Dimension",
        ["Everything your Magic Bags swept up lives here. Pick items up or deposit them.", "You need a Magic Bag on you to open it.",
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
        ["Your Mining, Foraging, Farming and Combat levels and XP. Every level up pays coins.", "Command: /skills"], "Click to open!", "cmdc:skills"),
    ("main", 16, "Furniture_Village_Painting_1x1", "Collections",
        ["Everything you have gathered, your milestones and the recipes they unlock.", "Command: /collections"], "Click to open!", "cmdc:collections"),
    ("main", 20, "Rock_Gem_Emerald", "Bazaar",
        ["Instantly buy and sell resources. Prices move as players trade.", "Command: /bazaar (or /bz)"], "Click to open!", "cmdc:bazaar"),
    ("main", 21, "Furniture_Ancient_Chest_Large_Treasure", "Bank",
        ["Deposit coins to earn interest. Bank coins are safe when you die."], "Click to open!", "view:bank"),
    ("main", 22, "Furniture_Village_Sign", "Players",
        ["Everyone who is online: send teleport requests, visit islands, invite to your party."], "Click to open!", "view:players"),
    ("main", 23, "Deco_Scroll", "Party", ["See your party, accept an invite or leave your party."], "Click to open!", "view:party"),
    ("main", 24, "Furniture_Ancient_Bookshelf", "Mods",
        ["Every SkyWynn mod on the server, what it does and all of its commands."], "Click to open!", "view:mods"),
    # ---- Teleport (warps are added automatically in rows 2-4, see WARP_SLOTS)
    ("tp", 11, "Soil_Grass", "My Island",
        ["Teleport to your own island. It is created the first time you go.", "Command: /island (or /is)"], "Click to teleport!", "cmdc:island"),
    ("tp", 13, "Hub_Portal_Default", "Hub",
        ["Go back to the hub from anywhere, including your island.", "Command: /hub (or /lobby)"], "Click to teleport!", "cmdc:hub"),
    ("tp", 15, "Spawn_Portal", "Spawn", ["Teleport to the spawn point of the main world."], "Click to teleport!", "spawn"),
    # ---- Bank (%BANK% / %PURSE% are filled in live)
    ("bank", 13, "Furniture_Ancient_Chest_Large_Treasure", "Bank Account",
        ["Coins in the bank earn interest and are never lost when you die.", "Bank: %BANK%", "Purse: %PURSE%"],
        "Click to print your balance in chat", "cmd:bank"),
    ("bank", 29, "Ingredient_Bar_Gold", "Deposit All", ["Move every coin in your purse into the bank.", "Purse: %PURSE%"],
        "Click to deposit everything", "cmd:bank --action deposit --amount all"),
    ("bank", 31, "Deco_Scroll", "Other Amounts",
        ["Type the amount yourself, for example 500, 2k or 1.5m:", "/bank --action deposit --amount 500",
         "/bank --action withdraw --amount 500"], None, "info"),
    ("bank", 33, "Furniture_Ancient_Chest_Small", "Withdraw All", ["Move every coin in the bank back into your purse.", "Bank: %BANK%"],
        "Click to withdraw everything", "cmd:bank --action withdraw --amount all"),
    # ---- Players (online players are added automatically, see PLAYER_SLOTS)
    # cmdc (close first): accepting a /tpahere request teleports YOU (SkyyEssentials accept(): mover = r.here ? r.to : r.from)
    ("players", 47, "Ingredient_Crystal_Green", "Accept Teleport Request",
        ["Accept the newest teleport request someone sent you.", "Command: /tpaccept"], "Click to accept", "cmdc:tpaccept"),
    ("players", 51, "Ingredient_Crystal_Red", "Deny Teleport Request",
        ["Refuse the newest teleport request someone sent you.", "Command: /tpdeny"], "Click to deny", "cmd:tpdeny"),
    # ---- Party
    ("party", 11, "Deco_Scroll", "Party Members", ["Show who is in your party (printed in chat).", "Command: /party list"], "Click to list", "cmd:party list"),
    ("party", 13, "Ingredient_Crystal_Green", "Accept Party Invite", ["Join the party that invited you.", "Command: /party accept"],
        "Click to accept", "cmd:party accept"),
    ("party", 15, "Ingredient_Crystal_Red", "Leave Party", ["Leave your party. If you lead it, the lead passes on.", "Command: /party leave"],
        "Click to leave", "cmd:party leave"),
    ("party", 31, "Furniture_Village_Sign", "Invite Players", ["Open Players, click a player, then Invite to Party.", "Party chat: /pc <message>"],
        "Click to open Players", "view:players"),
]

# Things you can do with a selected player. %P = their name (letters, digits, _ only). (slot, icon, name, lines, footer, command, close menu first)
PLAYER_ACTIONS = [
    (29, "Hub_Portal_Default", "Send Teleport Request", ["Ask %P if you may teleport to them. They have 60 seconds to accept.", "Command: /tpa %P"],
        "Click to send", "tpa %P", False),
    (30, "Spawn_Portal", "Invite Them Here", ["Ask %P to teleport to you.", "Command: /tpahere %P"], "Click to send", "tpahere %P", False),
    (31, "Soil_Grass", "Visit Their Island", ["Teleport to the island of %P and look around (you can only build with their build rights).",
        "Command: /island --action visit --player %P"], "Click to visit", "island --action visit --player %P", True),
    (32, "Deco_Scroll", "Invite to Party", ["Invite %P to your party.", "Command: /party invite %P"], "Click to invite", "party invite %P", False),
    (33, "Tool_Hammer_Iron", "Give Island Build Rights", ["Let %P build on YOUR island. Only do this for friends.",
        "Command: /island --action invite --player %P"], "Click to give build rights", "island --action invite --player %P", False),
]

WARP_SLOTS   = list(range(19, 26)) + list(range(28, 35)) + list(range(37, 44))                       # 21 warps per page
PLAYER_SLOTS = list(range(10, 17)) + list(range(19, 26)) + list(range(28, 35)) + list(range(37, 44))  # 28 players per page
MOD_SLOTS    = list(range(10, 17)) + list(range(19, 26)) + list(range(28, 35))                        # 21 mods per page
NO_WARPS_SLOT, NO_PLAYERS_SLOT, PLAYER_HEAD_SLOT = 31, 22, 13

# The Mods submenu: one item per mod (icon = the item that represents it, tooltip = what it does + every command).
# "check" = a command of that mod; the mod counts as installed when its plugin or that command is loaded. The live version is
# read from the loaded plugin's manifest; "version" is only shown when the mod is not installed.
# Commands with optional arguments are written in the form the engine accepts (--name value), see the docstring.
MODS = [
    {"mod": "SkyyMenu", "version": VERSION, "icon": "Ingredient_Voidheart", "check": "skymenu",
     "desc": "The all-in-one SkyWynn menu: teleports, your Pocket Dimension, Accessory Bag, the HUD editor, crafting, skills, collections, the bazaar, the bank, players, your party and this list of mods.",
     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item"]},
    {"mod": "SkyyIslands", "version": "0.4.1", "icon": "Soil_Grass", "check": "island",
     "desc": "Your own private island in the sky: teleport home any time (built with a starter chest the first time), give friends build rights or let anyone visit.",
     "commands": ["/island (or /is) - go to your island", "/island --action visit --player <player> - visit a player's island",
                  "/island --action invite --player <player> - give a player build rights", "/island --action info - about your island",
                  "/hub (or /lobby) - back to the hub", "/sethub - (admin) set the hub point"]},
    {"mod": "SkyySacks", "version": "0.6.1", "icon": "Tool_Feedbag", "check": "sacks",
     "desc": "Magic Bags: carry a Mining, Foraging or Farming bag and what you gather of that type goes straight into your Pocket Dimension instead of your inventory. Also adds crafting from your inventory and bags.",
     "commands": ["/sacks (or /pd, /bags) - open your Pocket Dimension (needs a Magic Bag on you)", "/craft (or /recipes) - craft from your inventory and bags"]},
    {"mod": "SkyyAccessories", "version": "0.2", "icon": "Utility_Bag_Seed", "check": "accessories",
     "desc": "Your Accessory Bag: 9 slots for bench accessories (unlock that bench's recipes in /craft) and stat talismans (health, stamina, mana, regeneration, speed) that work while they sit in the bag.",
     "commands": ["/accessories (or /acc, /accbag) - open your Accessory Bag"]},
    {"mod": "SkyyHud", "version": "0.3.3", "icon": "Deco_Map", "check": "skyyhud",
     "desc": "A customizable on-screen HUD: coordinates, zone, clocks, day counter, session timer, players online and coins. Drag widgets around in the editor, save profiles or share your layout as a code.",
     "commands": ["/skyyhud (or /shud) - open the HUD editor", "/skyyhud --action export - print your layout as a code",
                  "/skyyhud --action import --code <code> - load a layout code", "/skyyhud --action reset - reset your layout",
                  "/skyyhud --action profile --code save|load|delete <name> - named layouts", "/skyyhud --action profile --code list - your saved layouts",
                  "/skyyhud --action preview --code front|back|off - editor preview mode"]},
    {"mod": "SkyySkills", "version": "0.1", "icon": "Weapon_Sword_Iron", "check": "skills",
     "desc": "Hypixel-style skills - Mining, Foraging, Farming and Combat - that level up as you play and pay coins on every level up.",
     "commands": ["/skills (or /skill) - open your Skills", "/skills top <skill> - top 10 for mining, foraging, farming or combat",
                  "/skills quiet - hide the +XP chat messages", "/skills reload - (admin) re-read the XP settings"]},
    {"mod": "SkyyCollections", "version": "0.1.3", "icon": "Furniture_Village_Painting_1x1", "check": "collections",
     "desc": "Hypixel-style Collections: tracks everything you gather over your lifetime. Milestones I to V unlock crafting recipes for the /craft page.",
     "commands": ["/collections (or /coll) - open your Collections", "/collections --action unlocks - the recipes you unlocked",
                  "/collections --action reload - (admin) re-read the unlock rules"]},
    {"mod": "SkyyBazaar", "version": "0.1", "icon": "Rock_Gem_Emerald", "check": "bazaar",
     "desc": "A Hypixel-style Bazaar: instantly buy or sell dozens of resources against the server. Prices move as people trade.",
     "commands": ["/bazaar (or /bz) - open the Bazaar",
                  "/bazaaradmin --action price --item <id> --value <price> - (admin) set a price",
                  "/bazaaradmin --action reset|info --item <id|all> - (admin) reset or show prices",
                  "/bazaaradmin --action reload - (admin) re-read the product list"]},
    {"mod": "SkyyBank", "version": "0.1", "icon": "Furniture_Ancient_Chest_Large_Treasure", "check": "bank",
     "desc": "A SkyBlock-style bank next to your coin purse: deposit coins to earn interest and withdraw them any time. Bank coins are never lost when you die.",
     "commands": ["/bank - show your bank and purse", "/bank --action deposit --amount <n|all> - put coins in (500, 2k, 1.5m or all)",
                  "/bank --action withdraw --amount <n|all> - take coins out", "/bankconfig --percent <p> --minutes <m> - (admin) interest"]},
    {"mod": "SkyyCoins", "version": "0.1.3", "icon": "Rock_Gem_Ruby", "check": "balance",
     "desc": "The server's coins. Check your balance and pay other players. When you die you lose a set share of the coins in your purse (bank coins are safe).",
     "commands": ["/balance (or /bal, /coins, /purse) - your coins", "/pay <player> <amount> - send coins to a player",
                  "/coinsgive <amount> - (admin) give yourself coins", "/deathpenalty --percent 5% or 5%-10% - (admin) coins lost on death"]},
    {"mod": "SkyyParty", "version": "0.1.1", "icon": "Deco_Scroll", "check": "party",
     "desc": "Team up with friends: invite players to a party, chat privately and see who is in it. The lead passes on if the leader leaves.",
     "commands": ["/party (or /p) - party help", "/party invite <player> - invite a player", "/party accept - accept an invite",
                  "/party leave - leave your party", "/party list - list your party", "/pc <message> - chat with your party"]},
    {"mod": "SkyyEssentials", "version": "0.1", "icon": "Tool_Map", "check": "tpa",
     "desc": "Everyday commands the base game is missing: teleport requests between players and private messages.",
     "commands": ["/tpa <player> - ask to teleport to a player", "/tpahere <player> - ask a player to teleport to you",
                  "/tpaccept [player] - accept a teleport request", "/tpdeny [player] - deny a teleport request",
                  "/tpacancel - cancel your requests", "/msg <player> <message> (or /tell, /w) - private message",
                  "/reply <message> - answer your last message", "/fly - (staff) toggle flight"]},
    {"mod": "SkyyRolls", "version": "0.1", "icon": "Weapon_Longsword_Copper", "check": "rolls",
     "desc": "A test of random item stats (reforge, damage, strength, crit and quality) - the first step toward SkyBlock-style item modifiers. Still a developer test.",
     "commands": ["/rolls --action give --item <itemId> - an item with random stats", "/rolls --action read - stats of the item in your hand",
                  "/rolls --action reroll - re-roll the item in your hand"]},
]
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
    assert act in ("profile", "spawn", "info") or act.split(":", 1)[0] in ("view", "cmd", "cmdc"), "bad action " + act
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
with zipfile.ZipFile(B.SERVER_JAR) as zj:
    for n in zj.namelist():
        if n.startswith("com/hypixel/") and n.endswith(".class"):
            try:
                TAKEN |= set(WANT) & cp_utf8(zj.read(n))
            except Exception:
                pass
for p in glob.glob(os.path.join(B.PROJECT, "*", "build_*.py")):
    if os.path.basename(os.path.dirname(p)) == "SkyyMenu":
        continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    for w in WANT:
        if '"%s"' % w in t:
            TAKEN.add(w)
assert "skymenu" not in TAKEN, "/skymenu is already used by another command"
ALIASES = [a for a in ("menu", "sbmenu") if a not in TAKEN]
print("aliases:", ALIASES, "(taken elsewhere: %s)" % (sorted(TAKEN) or "none"))
ALIAS_TEXT = (" (also " + ", ".join("/" + a for a in ALIASES) + ")") if ALIASES else ""

# ================= inline UI strings (validated here: balanced, no underscores in element ids) =================
BS = ("Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 12, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
      "Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
      "Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));")
SLOT, COLS, ROWS = 60, 9, 6
GW, GH = SLOT * COLS, SLOT * ROWS
PW = GW + 32
PH = 680
UI = {
    "ROOT":     "Group #SkyyMenu { Anchor: (Width: %d, Height: %d); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }" % (PW, PH),
    "ACCENT":   "Group { Anchor: (Height: 2); Background: #e0b060; }",
    "TITLE":    'Label #SkyyMTitle { Anchor: (Height: 26); Text: ""; Style: (FontSize: 16, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "HINT":     'Label #SkyyMHint { Anchor: (Height: 16); Text: ""; Style: (FontSize: 10, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "GRIDWRAP": "Group #SkyyMGridWrap { Anchor: (Height: %d); }" % (GH + 4),
    "GRID":     "ItemGrid #SkyyMGrid { Anchor: (Horizontal: 0, Top: 2, Width: %d, Height: %d); SlotsPerRow: %d; AreItemsDraggable: false; Style: (SlotSize: %d, SlotIconSize: 44, SlotSpacing: 0); }" % (GW, GH, COLS, SLOT),
    "GAP":      "Group { Anchor: (Height: 6); }",
    "INFOBOX":  "Group #SkyyMInfoBox { Anchor: (Height: 186); Background: #142030(0.9); Padding: (Horizontal: 10, Vertical: 6); LayoutMode: Top; }",
    "INFONAME": 'Label #SkyyMInfoName { Anchor: (Height: 18); Text: ""; Style: (FontSize: 13, RenderBold: true, TextColor: #ffe9a0, VerticalAlignment: Center); }',
    "INFODESC": 'Label #SkyyMInfoDesc { Anchor: (Height: 30); Text: ""; Style: (FontSize: 11, TextColor: #c9dff0, Wrap: true); }',
    "STATUS":   'Label #SkyyMStatus { Anchor: (Height: 20); Text: ""; Style: (FontSize: 11, RenderBold: true, TextColor: #ffd27f, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "FOOT":     "Group #SkyyMFoot { Anchor: (Height: 32); LayoutMode: Left; Padding: (Top: 2); }",
    "SPACER":   'Label { Anchor: (Width: 8, Height: 28); Text: ""; }',
    "LEAD":     'Label { Anchor: (Width: 20, Height: 28); Text: ""; }',
    "BTNBACK":  'TextButton #SkyyMBack { Anchor: (Width: 120, Height: 28); Text: "< Back"; ' + BS + " }",
    "BTNPREV":  'TextButton #SkyyMPrev { Anchor: (Width: 110, Height: 28); Text: "< Prev page"; ' + BS + " }",
    "BTNNEXT":  'TextButton #SkyyMNext { Anchor: (Width: 110, Height: 28); Text: "Next page >"; ' + BS + " }",
    "BTNCLOSE": 'TextButton #SkyyMClose { Anchor: (Width: 120, Height: 28); Text: "Close"; ' + BS + " }",
}
INFO_LINES = 9
UI_INFO = ['Label #SkyyMInfo%d { Anchor: (Height: 14); Text: ""; Style: (FontSize: 10, TextColor: #9fb8cc, VerticalAlignment: Center); }' % i for i in range(INFO_LINES)]
for s in list(UI.values()) + UI_INFO:
    assert s.count("{") == s.count("}") and s.count("(") == s.count(")"), "unbalanced inline UI: " + s
    for eid in re.findall(r"#([A-Za-z0-9_]+)\s*\{", s):
        assert "_" not in eid, "underscore in element id #" + eid
    assert "Anchow" not in s and ";;" not in s
assert "Width" in UI["ROOT"] and "Top:" not in UI["ROOT"].split("Anchor: (")[1].split(")")[0], "page root anchor must be Width/Height only"

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
# Info-box detail lines go into #SkyyMInfo0..8: fixed 14 px labels WITHOUT Wrap (a wrapped second row would spill into the next
# label), about 520 px wide at FontSize 10. Keep every static detail line short enough to fit on one row. The first line of each
# body goes to #SkyyMInfoDesc (wraps) and the hover tooltips always carry the full text.
INFO_MAX = 80
for _body in E_BODY + MOD_BODY + [lines_of(v[2]) for v in VIEWS] + [lines_of(a[3]).replace("%P", "W" * 16) for a in PA]:
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
             (T["BT"], "Activating"), (T["BT"], "SlotClicking"), (T["LIFE"], "CanDismiss"), (T["OCU"], "registerSimple"),
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
dat  = pool.makeClass(PKG + ".MenuData")
utl  = pool.makeClass(PKG + ".MenuUtil")
giv  = pool.makeClass(PKG + ".Given")
page = pool.makeClass(PKG + ".MenuPage", pool.get(T["PAGE"]))
ref_ = pool.makeClass(PKG + ".RefreshTask")
fac  = pool.makeClass(PKG + ".MenuPageFactory")
cmd  = pool.makeClass(PKG + ".MenuCmd", pool.get(T["APC"]))
grt  = pool.makeClass(PKG + ".GrantTask")
rdy  = pool.makeClass(PKG + ".MenuReady")
seen = pool.makeClass(PKG + ".SeenTick")
quit_ = pool.makeClass(PKG + ".MenuQuit")
pl   = pool.makeClass(PKG + ".SkyyMenuPlugin", pool.get(JP))

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

# ================= MenuPage (inline page; views switched with rebuild()) =================
for f in ("public String view;", "public int pageNo;", "public java.util.UUID selU;", "public String[] acts;", "public String[] names;",
          "public String[] bodies;", "public String infoName;", "public String infoBody;", "public String status;", "public String title;",
          "public int pages;"):
    F(page, f)
C(page, r"""
public MenuPage(@PR@ pr, String view) {
  super(pr, @LIFE@.CanDismiss);
  this.view = view == null ? "main" : view;
  this.pageNo = 0;
  this.status = "";
  this.pages = 1;
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
  return v < 0L ? "not loaded yet - click Bank Account" : @PKG@.MenuUtil.fmt(v) + " coins";
}""")
M(page, r"""
public String profileBody() {
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map br = @PKG@.MenuUtil.bridge();
  StringBuilder sb = new StringBuilder();
  sb.append("Your SkyWynn profile, ").append(@PKG@.MenuUtil.safe(this.playerRef.getUsername())).append('.');
  sb.append("\nPurse: ").append(purseText());
  long bk = @PKG@.MenuUtil.bank(u);
  sb.append("\nBank: ").append(bk < 0L ? "open the Bank menu to load it" : @PKG@.MenuUtil.fmt(bk) + " coins");
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
public void fillStatic(java.util.ArrayList slots) {
  for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {
    if (!@PKG@.MenuData.E_VIEW[i].equals(this.view)) continue;
    String act = @PKG@.MenuData.E_ACT[i];
    String body = @PKG@.MenuData.E_BODY[i];
    if ("profile".equals(act)) body = profileBody();
    if (body.indexOf("%PURSE%") >= 0) body = body.replace("%PURSE%", purseText());
    if (body.indexOf("%BANK%") >= 0) body = body.replace("%BANK%", bankText());
    String c = cmdOf(act);
    boolean dim = c != null && @PKG@.MenuUtil.cmd(c) == null;
    put(slots, @PKG@.MenuData.E_SLOT[i], @PKG@.MenuData.E_ICON[i], @PKG@.MenuData.E_NAME[i] + (dim ? " (not installed)" : ""), body,
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
    put(slots, @PKG@.MenuData.PA_SLOT[i], @PKG@.MenuData.PA_ICON[i], @PKG@.MenuData.PA_NAME[i] + (dim ? " (not installed)" : ""),
        @PKG@.MenuData.PA_BODY[i].replace("%P", n), dim ? "Not installed on this server" : @PKG@.MenuData.PA_FOOT[i], "pact:" + i, dim);
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
        @PKG@.MenuData.MOD_NAME[k] + " " + ver + (installed ? "" : " (not installed)"), @PKG@.MenuData.MOD_BODY[k],
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
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GRIDWRAP);
  b.appendInline("#SkyyMGridWrap", @PKG@.MenuData.UI_GRID);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_GAP);
  b.appendInline("#SkyyMenu", @PKG@.MenuData.UI_INFOBOX);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFONAME);
  b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFODESC);
  for (int i = 0; i < @PKG@.MenuData.UI_INFO.length; i++) b.appendInline("#SkyyMInfoBox", @PKG@.MenuData.UI_INFO[i]);
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
  b.set("#SkyyMHint.Text", "Hover an item for details - click it to use it. Esc closes the menu.");
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
M(page, r"""
public void closePage(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().setPage(ref, st, @PGE@.None);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not close the menu: " + t); }
}""")
# run a command AS THIS PLAYER (vanilla /su pattern); installed + permission are checked first so the player gets a clear answer.
# The permission check fails CLOSED: the engine's AbstractCommand.acceptCall0 calls the same hasPermission, so if it throws here the
# command could not run anyway - say so in the menu instead of closing it and leaving a cryptic chat error.
M(page, r"""
public void runCmd(@REF@ ref, @ST@ st, String line, boolean close) {
  String name = @PKG@.MenuUtil.firstWord(line);
  @ACM@ c = @PKG@.MenuUtil.cmd(name);
  if (c == null) { this.status = "/" + name + " is not on this server - that mod is not installed."; rebuild(); return; }
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
  if (close) closePage(ref, st);
  @CMGR@.get().handleCommand(this.playerRef, line);
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
  this.infoName = this.names[idx];
  this.infoBody = this.bodies[idx];
  if (act.equals("info") || act.equals("profile") || act.startsWith("mod:")) { rebuild(); return; }
  if (act.startsWith("locked:")) { this.status = "That warp is locked."; rebuild(); return; }
  if (act.startsWith("cmdc:")) { runCmd(ref, st, act.substring(5), true); return; }
  if (act.startsWith("cmd:")) { runCmd(ref, st, act.substring(4), false); return; }
  if (act.equals("spawn")) { doSpawn(ref, st); return; }
  if (act.startsWith("warp:")) { doWarp(ref, st, act.substring(5)); return; }
  if (act.startsWith("pact:")) { playerAction(ref, st, Integer.parseInt(act.substring(5))); return; }
  @PKG@.MenuUtil.warn("unknown menu action " + act);
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
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
    if (@PKG@.MenuUtil.count(player, @PKG@.MenuData.ITEM_ID) <= 0) {
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
    @PRE@ e = (@PRE@) ev;
    @REF@ r = e.getPlayerRef();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null || @PKG@.Given.SESSION.containsKey(pr.getUuid())) return;
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GrantTask(pr), 4L, java.util.concurrent.TimeUnit.SECONDS);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("ready handler failed: " + t); }
}""")

# ================= SeenTick: forget players who logged out (SkyyIslands SeenTick pattern) =================
seen.addInterface(pool.get("java.lang.Runnable"))
C(seen, "public SeenTick() { }")
M(seen, r"""
public void run() {
  try {
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) { @PR@ pr = (@PR@) it.next(); if (pr != null && pr.isValid()) online.add(pr.getUuid()); }
    @PKG@.Given.SESSION.keySet().retainAll(online);
  } catch (Throwable t) { }
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
  @OCU@.registerSimple(this, @PKG@.SkyyMenuPlugin.class, @PKG@.MenuData.PAGE_ID, new @PKG@.MenuPageFactory());
  getCommandRegistry().registerCommand(new @PKG@.MenuCmd());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.MenuReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.MenuQuit());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SeenTick(), 30L, 30L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyMenu] """ + VERSION + r""" ready - /skymenu""" + "".join(" /" + a for a in ALIASES) + r""", right-click the SkyWynn Menu item; the item is given once per player");
}""")
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  super.shutdown();
}""")

for c in (dat, utl, giv, page, ref_, fac, cmd, grt, rdy, seen, quit_, pl):
    c.writeFile(OUT)
print("classes written")

# ================= post-build check: every inline UI string in the compiled MenuData class is intact =================
_md = open(os.path.join(OUT, "com", "skyy", "menu", "MenuData.class"), "rb").read()
_consts = cp_utf8(_md)
for s in list(UI.values()) + UI_INFO:
    assert s in _consts, "inline UI string missing from MenuData.class: " + s[:80]
print("inline UI strings verified in MenuData.class:", len(UI) + len(UI_INFO))

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
B.assemble(jar, B.manifest("SkyyMenu", VERSION, "SkyWynn menu (Hypixel SkyBlock style): right-click the SkyWynn Menu item or /skymenu for teleports and warps, Pocket Dimension, Accessory Bag, HUD editor, crafting, skills, collections, bazaar, bank, players, party and a list of every mod with its commands. Zero dependencies.", PKG + ".SkyyMenuPlugin"), OUT, files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyMenu.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyMenu" % VERSION, disable_prefix="Skyy:")
