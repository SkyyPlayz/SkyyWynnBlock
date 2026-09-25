"""Derive SkyyMenu/build_skyymenu_0.1.3.py from the live 0.1.2 (python tools/menu_0_1_3_patch.py, then build the result).
0.1.3 (Skyy's beta backlog, HANDOFF log 2026-09-24 20:10):
 - NEW main-menu entries (icons checked against Assets.zip at build time, picture file included):
     Island Menu  (Plant_Sapling_Oak)                  -> /island menu   (SkyyIslands 0.5 island menu page)
     Vault        (Furniture_Royal_Magic_Chest_Large)  -> /vault         (SkyyVault, items shared by all profiles)
     Reforge      (Tool_Hammer_Iron)                   -> /reforge       (SkyyRolls 0.1.4 reforge page)
     Guild        (Furniture_Outlander_Banner)         -> /guild         (SkyyGuilds guild page)
     Party        (Deco_Scroll, was a submenu)         -> /party         (SkyyParty 0.1.3 party page)
     Bank         (was a submenu)                      -> /bank          (SkyyBank 0.1.3 bank page)
   All are "cmdc" actions = the 0.1.2 rule: the command runs with the menu still open, a page command simply replaces the menu, and
   CloseTask closes the menu ~150 ms later only if the menu is still the open page. The old Bank and Party submenus are removed (their
   pages do all of it); the Bank view's "Bank Account" (a keep-open /bank that now opened the bank page over a rebuilding menu) is gone.
   Rows: 1 = Skyy's order (unchanged), 2 = Island Menu, Bank, Vault, Bazaar, Reforge, 3 = Players, Party, Guild, 4 = Mods.
   An entry whose mod is missing is greyed "(not installed)" as before. /island menu is a SUBCOMMAND of an installed /island, so it gets
   its own check (NEEDS_SUB): with an /island that has no "menu" subcommand (SkyyIslands 0.4.5) the entry is greyed "(update needed)"
   and a click explains instead of sending a command the old /island would reject. AbstractCommand.getSubCommand(name) lower-cases the
   name and also resolves subcommand aliases (HytaleServer.jar bytecode).
 - Build-time alias check fixed: /menu counted as "taken" whenever ANY other build script contained the text "menu" in quotes. SkyyIslands
   0.5 adds a "menu" subcommand to /island, which would have silently dropped the /menu alias. A Skyy script now takes a word only
   through addAliases(...) or a super("word"...) whose class is NOT passed to addSubCommand (+ the helper forms, see Review fixes).
 - STUCK TOOLTIP (beta bug: hover an item, press Esc -> its tooltip stays on screen). Findings:
     * The item tooltip is not part of our page. The client draws it on a global ItemTooltipLayer (HytaleClient.exe: ItemTooltipLayer,
       ShowTooltipForItem, ClearTooltip, _hoveredItemElement); the ItemGrid only asks that layer to show/clear. When Esc removes the page
       client-side the layer is not cleared - a CLIENT bug.
     * The server cannot clear it after the fact: Esc closes the page on the client first, then sends CustomPageEvent Dismiss; the
       server's PageManager.handleEvent(Dismiss) only calls onDismiss and sets customPage = null. There is no page left to update, and a
       SetPage(None) with no custom page open is never acknowledged-counted (unexpected-ack risk), so nothing is sent on dismiss.
     * Other installed mods: the ItemGrids that never show a stuck tooltip switch it off - `InfoDisplay: None;` inline (EyeSpy's
       ItemGridValue in Skyys-Modpack, Alec's Tamework .ui files). ItemGridInfoDisplayMode = Tooltip | Adjacent | None; Adjacent is the
       creative Builder-Tools list layout (vanilla Server/Item/Category/CreativeLibrary/Tool.json), not a hover pane for a 9x6 grid.
   Mitigations in 0.1.3:
     1. Every close the SERVER does (Close slot / Close button, teleports, spawn, warps, CloseTask) and every hand-off to a page command
        first sends ONE update that empties the grid (54 empty ItemGridSlots, MenuPage.clearGrid), then closes / runs the command. The
        slot under the mouse turns empty while the page is still there, so the grid can clear its own tooltip before it is removed.
        Protocol: an update is +1 required acknowledgement answered by an Acknowledge, never by a Dismiss, so it cannot cause the 0.1.2
        "Loading..." problem (that came from closing before opening). Commands run on ForkJoinPool -> world thread
        (CommandManager.handleCommand bytecode), so the clear always reaches the client before the next page.
     2. Esc hook (EXPERIMENT, probably a no-op - do not count on it): a Dismissing event binding on the page root Group #SkyyMenu (the
        client's Group has Validating + Dismissing events, HyUI's GroupBuilder.onDismissing binds the same). It can only help if a
        Dismissing binding makes the client hand Esc to the server INSTEAD of tearing the page down itself. On the normal Esc path the
        client removes the page (and leaves the tooltip) before anything reaches the server, and no server update can reach back in
        time. IF the client routes Esc to the root group and keeps the page, the server gets "mesc" and CloseTask closes the menu 150 ms
        later with the grid cleared first - only if the menu is still the open page, so when the client closed the page itself (its
        Dismiss arrives within those 150 ms) nothing is sent. If the client never routes Esc there, Esc behaves exactly like 0.1.2.
        Why "mesc" does NOT clear the grid at once (review 2026-09-24): PageManager.handleEvent drops EVERY data event while
        customPageRequiredAcknowledgments != 0, Dismiss does not reset that counter, and only World.onSetupPlayerJoining clears it
        (HytaleServer.jar bytecode). An update sent to a page the client already closed may never be acknowledged, and then every
        button of every later page does nothing until the next world change. The 150 ms wait + "still the open page" check is what
        keeps the hook from ever sending to a closed page.
     3. Per-player "Hover Tooltips" switch (main menu, top right, saved in Skyy_SkyyMenu/notips/<uuid>.txt): OFF renders the grid with
        `InfoDisplay: None;` (the proven EyeSpy markup), so no tooltip can ever stick; the info box above the grid shows an entry's text
        when it is clicked. This is the ONLY mitigation that structurally prevents the stuck tooltip. Default ON (Skyy praised the hover
        tooltips of 0.1.2 - switching the default off is Skyy's call). The file is written off the world thread (TipsSave on the
        scheduler: tmp file + atomic replace, 5 x 20 ms retries on Windows sharing violations, like SkyyProfiles); the in-memory switch
        is set at once, so a failed save only loses it after a relog.
 - Small text fixes: Your Profile footer says "above" (the info box moved above the grid in 0.1.2), Skills text no longer names the
   retired Combat skill, the item description knows the new commands.
 - Review fixes (2026-09-24):
     * Version-dependent wording: the player action "Invite to Your Island" (SkyyIslands 0.5 makes invitees members) and the Mods-list
       SkyyIslands text only show while /island has the "menu" subcommand (the NEEDS_SUB check). With SkyyIslands 0.4.5 the old wording
       comes back ("Give Island Build Rights", build rights only). Data: PA_LEGACY and a MODS entry's "old" key.
     * Mods list refreshed against the live 19-mod set: SkyyClasses, SkyyProfiles, SkyyCooking, SkyyTrees and SkyyExploration added (20
       mods, one page); SkyySacks, SkyyAccessories, SkyyHud, SkyySkills (no Combat skill, the 0.4.1 skills + /skills stats|xp),
       SkyyCollections, SkyyCoins, SkyyBazaar, SkyyVault rewritten from their live build scripts. The shown version is the loaded
       manifest's; "version" here only shows for a mod that is not installed.
     * Menu item grant respects profile:busy:<uuid> (tools/PROFILES-CONTRACT.md rule 5): GrantTask retries while SkyyProfiles runs a
       crash recovery, /skymenu opens the page but gives no item then. (Skyy_Menu is SkyyProfiles' default keepItems, so the recovery
       never clears it - but a menu item placed before the recovery could push a restored item out of its slot.)
     * /menu alias safety: the build check also reads helper-built commands (SkyyGuilds / SkyyVault write super("%s", ...) through a
       Python cmd("Class", "word", ..., subs=(...), aliases=(...)) helper - the plain super("word" scan cannot see those), and at the
       FIRST PlayerReadyEvent the server log gets one line: every command word of the menu belongs to SkyyMenu, or a WARNING naming the
       other command that also claims /menu, /sbmenu or /skymenu (the engine keeps only one - root names beat aliases, the last alias
       registered wins).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.1.2.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.1.3.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n >= 1, "anchor missing: " + old[:100]
    if count == 1:
        assert n == 1, "anchor not unique (%d): %s" % (n, old[:100])
        s = s.replace(old, new, 1)
    else:
        s = s.replace(old, new)


def rep_block(start, end, must_contain, new):
    """replace s[start ... end] (end marker included) - both markers unique"""
    global s
    assert s.count(start) == 1, "block start not unique: " + start[:80]
    i = s.index(start)
    j = s.index(end, i) + len(end)
    old = s[i:j]
    for m in must_contain:
        assert m in old, "block does not contain " + m
    s = s[:i] + new + s[j:]


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('VERSION = "0.1.2"', 'VERSION = "0.1.3"')
rep("0.1.2: pages opened from the menu no longer hang on Loading...",
    "0.1.3: new entries Island Menu (/island menu), Vault (/vault), Reforge (/reforge), Guild (/guild); Party opens the /party page and Bank" + LF +
    "       the /bank page (all page commands keep the 0.1.2 open-over-the-menu rule; the Bank + Party submenus are gone); a per-player" + LF +
    "       Hover Tooltips switch (the only sure stuck-tooltip fix; saved off the world thread); stuck-tooltip mitigations (every server-side" + LF +
    "       close empties the grid first, an experimental Esc hook on the page root); Mods list = the live 19-mod set; Islands wording follows" + LF +
    "       the installed SkyyIslands; the menu item grant waits out profile:busy; a runtime check that /menu, /sbmenu, /skymenu are ours." + LF +
    "       Notes + the tooltip investigation: tools/menu_0_1_3_patch.py." + LF +
    "0.1.2: pages opened from the menu no longer hang on Loading...")
rep("   The page is closed first when the command teleports or opens another page.",
    "   (0.1.2+) The command runs with the menu still open: a page command replaces the menu, anything else closes it ~150 ms later.")
rep(LF.join([
    "# Actions:  view:<main|tp|bank|players|party|mods>  open a submenu        cmdc:<command line>  close the menu, then run it",
    "#           cmd:<command line>  run it, keep the menu open (refreshes)    spawn  teleport to the main world spawn",
    "#           profile  show your stats in the info box                      info   just show the text in the info box"]),
    LF.join([
    "# Actions:  view:<main|tp|players|mods>  open a submenu                   cmdc:<command line>  run it, then close the menu (a page",
    "#           cmd:<command line>  run it, keep the menu open (refreshes)         command simply replaces the menu)",
    "#           profile  show your stats in the info box                      info   just show the text in the info box",
    "#           spawn  teleport to the main world spawn                       tips   switch this player's hover tooltips on / off"]))
rep('MENU_ITEM_DESC = ("Right-click to open the SkyWynn Menu: teleports, your bags, the HUD editor, skills, the bazaar, the bank "' + LF +
    '                  "and a list of every mod with its commands.\\\\n\\\\nLost it? Type /skymenu to get a new one.")',
    'MENU_ITEM_DESC = ("Right-click to open the SkyWynn Menu: teleports, your island menu, bags, vault, the HUD editor, skills, the bazaar, "' + LF +
    '                  "the bank, reforging, your party and guild, and a list of every mod with its commands.\\\\n\\\\nLost it? Type /skymenu to get a new one.")')

# ---------------------------------------------------------------------------------------------------------------- views (Bank + Party submenus removed)
rep(LF.join([
    '    ("bank",    "Bank",           ["Coins in the bank earn interest and are never lost when you die.",',
    '                                   "Deposit or withdraw below, or type /bank."]),', '']), "")
rep('    ("party",   "Party",          ["Parties let you play together and chat privately with /pc <message>."]),' + LF, "")

# ---------------------------------------------------------------------------------------------------------------- entries
NEW_ENTRIES = r'''ENTRIES = [
    # ---- main menu. Row 1 = Skyy's order (Teleport, Pocket Dimension, Accessory Bag, HUD editor, then the rest), row 2 = your island +
    # your stuff, row 3 = people, row 4 = the mod list; top right = the per-player tooltip switch (0.1.3 layout)
    ("main", 4,  "Armor_Iron_Head", "Your Profile", ["Your coins, bank, skill levels and accessories."], "Click to show your stats above", "profile"),
    ("main", 8,  "Deco_Book_Pile_Small", "Hover Tooltips",
        ["Switch the pop-up text of this menu on or off (saved for you).",
         "Off: nothing pops up when you hover an item. Click an item to use it",
         "and read what it does in this box."], "Click to switch", "tips"),
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
    ("main", 24, "Tool_Hammer_Iron", "Reforge",
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
'''
rep_block("ENTRIES = [" + LF, LF + "]" + LF, ['"cmd:party leave"', '"view:bank"', '"cmd:bank deposit all"'], NEW_ENTRIES)

# ---------------------------------------------------------------------------------------------------------------- player actions
rep(LF.join([
    '    (33, "Tool_Hammer_Iron", "Give Island Build Rights", ["Let %P build on YOUR island. Only do this for friends.",',
    '        "Command: /island invite %P"], "Click to give build rights", "island invite %P", False),']),
    LF.join([
    '    (33, "Tool_Hammer_Iron", "Invite to Your Island", ["Invite %P to join your island as a co-op member. Only do this for friends.",',
    '        "They join with /island accept.", "Command: /island invite %P"], "Click to invite", "island invite %P", False),',
    # main session 2026-09-24 (islands review finding 4): 0.5 splits build rights from membership - a one-click Trusted entry
    '    (34, "Tool_Pickaxe_Iron", "Let Them Build", ["Let %P build on YOUR island without making them a member.",',
    '        "Undo with /island untrust.", "Command: /island trust %P"], "Click to trust", "island trust %P", False),']))

# ---------------------------------------------------------------------------------------------------------------- Mods list
# Review 2026-09-24: the whole list refreshed against the live 19-mod set (tools/deploy_set.py SET) + the 0.1.3 partners, commands read
# from each mod's newest build script. Optional "old": {"need": <NEEDS_SUB line>, "desc", "commands"} = the text shown while that
# subcommand check says the installed mod is older (SkyyIslands 0.4.5 until 0.5 ships).
# Round cross-check 2026-09-24: versions + texts brought to this round's set (Sacks 0.7.5 Smithing bag / page without a bag, Guilds
# 0.1.1 Admin rank + bank limit / log, Essentials 0.1.1 /r); "version" is only shown for a mod that is not installed.
NEW_MODS = r'''MODS = [
    {"mod": "SkyyMenu", "version": VERSION, "icon": "Ingredient_Voidheart", "check": "skymenu",
     "desc": "The all-in-one SkyWynn menu: teleports, your island menu, Pocket Dimension, Vault, Accessory Bag, the HUD editor, crafting, skills, collections, the bazaar, the bank, reforging, players, your party and guild, and this list of mods.",
     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item"]},
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
'''
rep_block("MODS = [" + LF, LF + "]" + LF, ['"mod": "SkyyRolls", "version": "0.1"', '"mod": "SkyyEssentials"'], NEW_MODS)

# ---------------------------------------------------------------------------------------------------------------- build-time checks
rep('    assert act in ("profile", "spawn", "info") or act.split(":", 1)[0] in ("view", "cmd", "cmdc"), "bad action " + act',
    '    assert act in ("profile", "spawn", "info", "tips") or act.split(":", 1)[0] in ("view", "cmd", "cmdc"), "bad action " + act')
rep(LF.join([
    'for m in MODS:',
    '    need_item(m["icon"])',
    '    assert len(m["commands"]) <= 8, "the info box shows 8 command lines, %s has %d" % (m["mod"], len(m["commands"]))']),
    LF.join([
    'for m in MODS:',
    '    need_item(m["icon"])',
    '    assert len(m["commands"]) <= 8, "the info box shows 8 command lines, %s has %d" % (m["mod"], len(m["commands"]))',
    '# 0.1.3: the icon PICTURE must exist too (Icon follows Parent like look_of; the grid shows that file)',
    'def need_icon(iid):',
    '    cur, hops, icon = iid, 0, None',
    '    while cur and hops < 8 and icon is None:',
    '        need_item(cur)',
    '        d = json.loads(ASSETS.read(ITEMS[cur]).decode("utf-8-sig"))',
    '        icon = d.get("Icon")',
    '        cur = d.get("Parent"); hops += 1',
    '    assert icon and "Common/" + icon in COMMON, "icon picture missing for %s: %s" % (iid, icon)',
    'for _ic in sorted(set([e[2] for e in ENTRIES] + [a[1] for a in PLAYER_ACTIONS] + [m["icon"] for m in MODS] +',
    '                      [ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_PLAYER])):',
    '    need_icon(_ic)',
    '_lines = [e[6].split(":", 1)[1] for e in ENTRIES if e[6].split(":", 1)[0] in ("cmd", "cmdc")] + [a[5] for a in PLAYER_ACTIONS]',
    'for _c, _sub, _need in NEEDS_SUB:',
    '    assert _c == _c.lower() and _sub == _sub.lower() and " " not in _c + _sub, "NEEDS_SUB words are single lower-case words"',
    '    assert any(l.split(" ")[:2] == [_c, _sub] for l in _lines), "NEEDS_SUB %s %s matches no menu command" % (_c, _sub)',
    '    txt(_need)',
    '# review 2026-09-24: version-dependent wording (MODS "old", PA_LEGACY) hangs on a NEEDS_SUB line',
    '_subs = [_c + " " + _sub for _c, _sub, _need in NEEDS_SUB]',
    'assert len(set(m["mod"] for m in MODS)) == len(MODS), "a mod is listed twice in MODS"',
    'for m in MODS:',
    '    if "old" in m:',
    '        assert m["old"]["need"] in _subs, "%s: old.need %s is no NEEDS_SUB line" % (m["mod"], m["old"]["need"])',
    '        assert len(m["old"]["commands"]) <= 8, "the info box shows 8 command lines, %s (old) has %d" % (m["mod"], len(m["old"]["commands"]))',
    'for _slot, _need, _name, _plines, _foot in PA_LEGACY:',
    '    assert _slot in [a[0] for a in PLAYER_ACTIONS], "PA_LEGACY slot %d is no player action" % _slot',
    '    assert _need in _subs, "PA_LEGACY need %s is no NEEDS_SUB line" % _need',
    '    assert _plines, "PA_LEGACY slot %d has no text" % _slot']))
# Mods-list bodies for the old wording + the legacy player-action texts (same 80-character info-line rule as every other body)
rep('MOD_BODY = [txt(m["desc"]) + "\\nCommands:\\n" + "\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m["commands"]) for m in MODS]',
    'MOD_BODY = [txt(m["desc"]) + "\\nCommands:\\n" + "\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m["commands"]) for m in MODS]' + LF +
    'MOD_OLD_NEED = [m["old"]["need"] if "old" in m else "" for m in MODS]' + LF +
    'MOD_OLD_BODY = [(txt(m["old"]["desc"]) + "\\nCommands:\\n" + "\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m["old"]["commands"]))' + LF +
    '                if "old" in m else "" for m in MODS]')
rep('for _body in E_BODY + MOD_BODY + [lines_of(v[2]) for v in VIEWS] + [lines_of(a[3]).replace("%P", "W" * 16) for a in PA]:',
    'for _body in (E_BODY + MOD_BODY + [b for b in MOD_OLD_BODY if b] + [lines_of(v[2]) for v in VIEWS] +' + LF +
    '              [lines_of(a[3]).replace("%P", "W" * 16) for a in PA] + [lines_of(a[3]).replace("%P", "W" * 16) for a in PA_LEGACY]):')

# /menu must not count as taken because SkyyIslands 0.5 has an /island SUBCOMMAND named "menu"
rep(LF.join([
    'for p in glob.glob(os.path.join(B.PROJECT, "*", "build_*.py")):',
    '    if os.path.basename(os.path.dirname(p)) == "SkyyMenu":',
    '        continue',
    '    t = open(p, encoding="utf-8", errors="ignore").read()',
    '    for w in WANT:',
    '        if \'"%s"\' % w in t:',
    '            TAKEN.add(w)']),
    LF.join([
    '# 0.1.3: a Skyy build script takes a word only as a ROOT command or an alias: addAliases(... <word> ...) or super(<word>, ...) in a class that',
    '# is NOT passed to addSubCommand (SkyyIslands 0.5 has /island menu = a subcommand named "menu", which is no /menu command). The nearest',
    '# "public ClassName(" before the super call is its constructor. 0.1.2 counted any quoted "menu" anywhere and would drop /menu.',
    '# Review 2026-09-24: SkyyGuilds and SkyyVault write their super calls through a Python helper (super("%s", ...) % name), so the',
    '# literal scan cannot see them: cmd("Class", "<word>", ...) is a root command unless that class is in some subs=(...) or',
    '# variant="Class", and aliases=(... "<word>" ...) takes the word (even on a subcommand: that errs loud - the build prints "taken',
    '# elsewhere"). SkyyIslands 0.5 builds its subcommands with sub("Class", "menu", ...), never a root. Best effort only - the plugin also',
    '# checks the LIVE command map at the first PlayerReadyEvent and logs a WARNING when another command claims /menu, /sbmenu or /skymenu',
    '# (MenuUtil.checkAliases).',
    'SUB_RE = re.compile(r"addSubCommand\\(\\s*new\\s+[^\\s(]*?(\\w+)\\s*\\(")',
    'CTOR_RE = re.compile(r"public\\s+(\\w+)\\s*\\(")',
    'HELPER_SUBS_RE = re.compile(r"(?:subs\\s*=\\s*\\(([^)]*)\\)|variant\\s*=\\s*(\\"\\w+\\"))")',
    'def takes(text, w):',
    '    if re.search(r\'addAliases\\([^)]*"%s"\' % re.escape(w), text):',
    '        return True',
    '    subs = set(SUB_RE.findall(text))',
    '    for mm in re.finditer(r\'super\\(\\s*"%s"\' % re.escape(w), text):',
    '        ctors = CTOR_RE.findall(text[:mm.start()])',
    '        if not ctors or ctors[-1] not in subs:',
    '            return True',
    '    hsubs = set()',
    '    for a, b in HELPER_SUBS_RE.findall(text):',
    '        hsubs |= set(re.findall(r\'"(\\w+)"\', a + " " + b))',
    '    for mm in re.finditer(r\'\\bcmd\\(\\s*"(\\w+)"\\s*,\\s*"%s"\' % re.escape(w), text):',
    '        if mm.group(1) not in hsubs:',
    '            return True',
    '    if re.search(r\'aliases\\s*=\\s*\\([^)]*"%s"\' % re.escape(w), text):',
    '        return True',
    '    return False',
    '# (the test strings are split after "super(" so tools/ci/lint.py does not read them as commands of this mod)',
    'assert takes(\'public MenuCmd() { super(\' + \'"menu", "d"); }\', "menu")',
    'assert not takes(\'public IslandMenuCmd() { super(\' + \'"menu", "d"); } addSubCommand(new {PKG}.IslandMenuCmd());\', "menu")',
    'assert takes(\'addAliases(new String[] { "menu" });\', "menu")',
    'assert takes(\'cmd("GMenuCmd", "menu", "d", [], "")\', "menu")',
    'assert not takes(\'cmd("GMenuCmd", "menu", "d", [], "")\\nroot = cmd("GuildCmd", "guild", "d", [], "",\\n    subs=("GHelpCmd",\\n          "GMenuCmd"))\', "menu")',
    'assert not takes(\'cmd("VMenuCmd", "menu", "d", [], "")\\ncmd("VaultCmd", "vault", "d", [], "", variant="VMenuCmd")\', "menu")',
    'assert takes(\'cmd("GuildCmd", "guild", "d", [], "", aliases=("g", "menu"))\', "menu")',
    'assert not takes(\'cmd("GuildCmd", "guild", "d", [], "", aliases=("g",))\', "menu")',
    'for p in glob.glob(os.path.join(B.PROJECT, "*", "build_*.py")):',
    '    if os.path.basename(os.path.dirname(p)) == "SkyyMenu":',
    '        continue',
    '    t = open(p, encoding="utf-8", errors="ignore").read()',
    '    for w in WANT:',
    '        if takes(t, w):',
    '            TAKEN.add(w)']))

# ---------------------------------------------------------------------------------------------------------------- inline UI: tooltip-free grid
rep('    "GAP":      "Group { Anchor: (Height: 8); }",',
    '    # 0.1.3: the same grid without hover tooltips (per-player switch). InfoDisplay: None is the inline markup EyeSpy / Tamework ship.' + LF +
    '    "GRIDNOTIPS": "ItemGrid #SkyyMGrid { Anchor: (Horizontal: 0, Top: 3, Width: %d, Height: %d); SlotsPerRow: %d; AreItemsDraggable: false; InfoDisplay: None; Style: (SlotSize: %d, SlotIconSize: 62, SlotSpacing: 0); }" % (GW, GH, COLS, SLOT),' + LF +
    '    "GAP":      "Group { Anchor: (Height: 8); }",')

# ---------------------------------------------------------------------------------------------------------------- probes
rep('(T["BT"], "Activating"), (T["BT"], "SlotClicking"),',
    '(T["BT"], "Activating"), (T["BT"], "SlotClicking"), (T["BT"], "Dismissing"), (T["ACM"], "getSubCommand"), (T["PAGE"], "sendUpdate"),' + LF +
    '             (T["ACM"], "getName"), (T["ACM"], "getAliases"), (T["CMGR"], "getCommandRegistration"),')

# ---------------------------------------------------------------------------------------------------------------- classes
rep('giv  = pool.makeClass(PKG + ".Given")', 'giv  = pool.makeClass(PKG + ".Given")' + LF + 'tip  = pool.makeClass(PKG + ".Tips")' + LF +
    'tsv  = pool.makeClass(PKG + ".TipsSave")')
rep("for c in (dat, utl, giv, page, ref_, clo_, fac, cmd, grt, rdy, seen, quit_, pl):",
    "for c in (dat, utl, giv, tip, tsv, page, ref_, clo_, fac, cmd, grt, rdy, seen, quit_, pl):")

# MenuData: the subcommand checks
rep('F(dat, "public static final String[] ALIASES = %s;" % jarr(ALIASES))',
    'F(dat, "public static final String[] ALIASES = %s;" % jarr(ALIASES))' + LF +
    'F(dat, "public static final String[] SUB_CMD = %s;" % jarr([n[0] for n in NEEDS_SUB]))' + LF +
    'F(dat, "public static final String[] SUB_SUB = %s;" % jarr([n[1] for n in NEEDS_SUB]))' + LF +
    'F(dat, "public static final String[] SUB_NEED = %s;" % jarr([txt(n[2]) for n in NEEDS_SUB]))' + LF +
    'F(dat, "public static final String[] MOD_OLD_NEED = %s;" % jarr(MOD_OLD_NEED))' + LF +
    'F(dat, "public static final String[] MOD_OLD_BODY = %s;" % jarr(MOD_OLD_BODY))' + LF +
    'F(dat, "public static final int[] PAL_SLOT = %s;" % jints([a[0] for a in PA_LEGACY]))' + LF +
    'F(dat, "public static final String[] PAL_NEED = %s;" % jarr([a[1] for a in PA_LEGACY]))' + LF +
    'F(dat, "public static final String[] PAL_NAME = %s;" % jarr([txt(a[2]) for a in PA_LEGACY]))' + LF +
    'F(dat, "public static final String[] PAL_BODY = %s;" % jarr([lines_of(a[3]) for a in PA_LEGACY]))' + LF +
    'F(dat, "public static final String[] PAL_FOOT = %s;" % jarr([txt(a[4]) for a in PA_LEGACY]))')

# MenuUtil.needOf (after cmd + firstWord)
NEED_OF = r'''# 0.1.3: "island menu" -> null when /island has that subcommand (or /island is missing: the normal "not installed" path) or the check
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
'''
rep("# version of a loaded Skyy mod read from its manifest", NEED_OF + "# version of a loaded Skyy mod read from its manifest")

# Tips: per-player hover-tooltip switch (per PLAYER like all menu data - tools/PROFILES-CONTRACT.md rule 6)
TIPS = r'''# ================= Tips (0.1.3): per-player "hover tooltips off" switch; file Skyy_SkyyMenu/notips/<uuid>.txt exists = off =================
F(tip, "public static java.nio.file.Path DIR;")
F(tip, "public static final java.util.concurrent.ConcurrentHashMap OFF = new java.util.concurrent.ConcurrentHashMap();")
M(tip, r"""
public static boolean isOff(java.util.UUID u) {
  if (u == null) return false;
  Object v = OFF.get(u);
  if (v instanceof Boolean) return ((Boolean) v).booleanValue();
  boolean off = false;
  try { off = DIR != null && java.nio.file.Files.exists(DIR.resolve(u.toString() + ".txt"), new java.nio.file.LinkOption[0]); }
  catch (Throwable t) { off = false; }
  OFF.put(u, off ? Boolean.TRUE : Boolean.FALSE);
  return off;
}""")
# review 2026-09-24: the file is written OFF the world thread (TipsSave on the scheduler) with the Given.markGiven pattern (tmp file +
# atomic replace) plus SkyyProfiles' 5 x 20 ms retries (Windows AccessDeniedException / sharing violations). write() saves the CURRENT
# in-memory value (the scheduled value only if the player already left), so two quick clicks whose saves run out of order still end on
# the last click. Only the file's existence matters (isOff), never its content.
M(tip, r"""
public static synchronized void write(java.util.UUID u, boolean fallback) {
  if (u == null || DIR == null) return;
  Object v = OFF.get(u);
  boolean off = v instanceof Boolean ? ((Boolean) v).booleanValue() : fallback;
  java.nio.file.Path f = DIR.resolve(u.toString() + ".txt");
  Throwable last = null;
  for (int attempt = 0; attempt < 5; attempt++) {
    try {
      if (off) {
        java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
        java.nio.file.Path tmp = DIR.resolve(u.toString() + ".txt.tmp");
        byte[] data = ("hover tooltips off " + System.currentTimeMillis() + "\n").getBytes("UTF-8");
        java.nio.file.Files.write(tmp, data, new java.nio.file.OpenOption[0]);
        java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      } else {
        java.nio.file.Files.deleteIfExists(f);
      }
      return;
    } catch (Throwable t) {
      last = t;
      try { Thread.sleep(20L); } catch (Throwable t2) { }
    }
  }
  @PKG@.MenuUtil.warn("could not save the tooltip setting for " + u + " (it stays until they log out): " + last);
}""")
tsv.addInterface(pool.get("java.lang.Runnable"))
F(tsv, "public java.util.UUID u;")
F(tsv, "public boolean off;")
C(tsv, "public TipsSave(java.util.UUID u, boolean off) { this.u = u; this.off = off; }")
M(tsv, r"""
public void run() {
  try { @PKG@.Tips.write(this.u, this.off); } catch (Throwable t) { @PKG@.MenuUtil.warn("tooltip setting save failed: " + t); }
}""")
M(tip, r"""
public static void setOff(java.util.UUID u, boolean off) {
  if (u == null) return;
  OFF.put(u, off ? Boolean.TRUE : Boolean.FALSE);
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.TipsSave(u, off), 0L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { write(u, off); }
}""")

'''
rep("# ================= MenuPage (inline page; views switched with rebuild()) =================",
    TIPS + "# ================= MenuPage (inline page; views switched with rebuild()) =================")

# MenuPage: cleared flag
rep('          "public int pages;"):', '          "public int pages;", "public boolean cleared;"):')

# texts that pointed at the removed Bank submenu
rep('sb.append("\\nBank: ").append(bk < 0L ? "open the Bank menu to load it" : @PKG@.MenuUtil.fmt(bk) + " coins");',
    'sb.append("\\nBank: ").append(bk < 0L ? "open the Bank to load it" : @PKG@.MenuUtil.fmt(bk) + " coins");')
rep('return v < 0L ? "not loaded yet - click Bank Account" : @PKG@.MenuUtil.fmt(v) + " coins";',
    'return v < 0L ? "not loaded yet - open the Bank" : @PKG@.MenuUtil.fmt(v) + " coins";')

# lineOf (after cmdOf) + fillStatic with the tooltip switch name and the subcommand check
rep(LF.join([
    '  if (act.startsWith("cmdc:")) return @PKG@.MenuUtil.firstWord(act.substring(5));',
    '  return null;',
    '}""")']),
    LF.join([
    '  if (act.startsWith("cmdc:")) return @PKG@.MenuUtil.firstWord(act.substring(5));',
    '  return null;',
    '}""")',
    'M(page, r"""',
    'public static String lineOf(String act) {',
    '  if (act == null) return null;',
    '  if (act.startsWith("cmd:")) return act.substring(4);',
    '  if (act.startsWith("cmdc:")) return act.substring(5);',
    '  return null;',
    '}""")']))
rep_block('M(page, r"""' + LF + 'public void fillStatic(java.util.ArrayList slots) {', '}""")' + LF, ['E_FOOT[i], act, dim);'], r'''M(page, r"""
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
''')

# build(): cleared reset, tooltip-free grid, hint, Esc hook
rep(LF.join([
    'public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {',
    '  this.acts = new String[54];']),
    LF.join([
    'public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {',
    '  this.cleared = false;',
    '  boolean tipsOff = @PKG@.Tips.isOff(this.playerRef.getUuid());',
    '  this.acts = new String[54];']))
rep('  b.appendInline("#SkyyMGridWrap", @PKG@.MenuData.UI_GRID);',
    '  b.appendInline("#SkyyMGridWrap", tipsOff ? @PKG@.MenuData.UI_GRIDNOTIPS : @PKG@.MenuData.UI_GRID);')
rep('  b.set("#SkyyMHint.Text", "Hover an item for details - click it to use it. Esc closes the menu.");',
    '  b.set("#SkyyMHint.Text", tipsOff ? "Tooltips off - the book at the top right turns them on. Click an item to use it."' + LF +
    '                                   : "Hover an item for details - click it to use it. Esc closes the menu.");')
rep('  ev.addEventBinding(@BT@.SlotClicking, "#SkyyMGrid", @EVD@.of("a", "mslot"), false);' + LF + '}""")',
    '  ev.addEventBinding(@BT@.SlotClicking, "#SkyyMGrid", @EVD@.of("a", "mslot"), false);' + LF +
    '  ev.addEventBinding(@BT@.Dismissing, "#SkyyMenu", @EVD@.of("a", "mesc"), false);' + LF + '}""")')

# clearGrid + closePage that clears first
rep(LF.join([
    'M(page, r"""',
    'public void closePage(@REF@ ref, @ST@ st) {',
    '  try {']),
    LF.join([
    '# 0.1.3 stuck-tooltip mitigation: ONE update that empties every slot (the hovered one too) while the page is still open, sent before',
    '# the server closes the menu or hands it to a page command. Only called while this menu is the open page (click handlers, CloseTask',
    '# checks it). Acknowledged like any update (never a Dismiss); build() resets the flag.',
    'M(page, r"""',
    'public void clearGrid() {',
    '  if (this.cleared) return;',
    '  this.cleared = true;',
    '  try {',
    '    java.util.ArrayList empty = new java.util.ArrayList();',
    '    for (int i = 0; i < 54; i++) empty.add(new @IGS@());',
    '    @UCB@ b = new @UCB@();',
    '    b.set("#SkyyMGrid.Slots", empty);',
    '    sendUpdate(b);',
    '  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not clear the menu grid: " + t); }',
    '}""")',
    'M(page, r"""',
    'public void closePage(@REF@ ref, @ST@ st) {',
    '  clearGrid();',
    '  try {']))

# runCmd: subcommand check, clear before a closing command, never leave an emptied menu behind
rep('  if (c == null) { this.status = "/" + name + " is not on this server - that mod is not installed."; rebuild(); return; }',
    '  if (c == null) { this.status = "/" + name + " is not on this server - that mod is not installed."; rebuild(); return; }' + LF +
    '  String need = @PKG@.MenuUtil.needOf(line);' + LF +
    '  if (need != null) { this.status = "/" + line + " needs " + need + " - this server has an older version."; rebuild(); return; }')
rep('  java.util.concurrent.CompletableFuture fut = @CMGR@.get().handleCommand(this.playerRef, line);',
    '  if (close) clearGrid();' + LF +
    '  java.util.concurrent.CompletableFuture fut = null;' + LF +
    '  try { fut = @CMGR@.get().handleCommand(this.playerRef, line); }' + LF +
    '  catch (Throwable t) { @PKG@.MenuUtil.warn("/" + line + " failed: " + t); this.status = "/" + name + " could not be run."; rebuild(); return; }')

# click: the tooltip switch
rep(LF.join([
    '  this.infoName = this.names[idx];',
    '  this.infoBody = this.bodies[idx];']),
    LF.join([
    '  this.infoName = this.names[idx];',
    '  this.infoBody = this.bodies[idx];',
    '  if (act.equals("tips")) {',
    '    java.util.UUID u = this.playerRef.getUuid();',
    '    boolean off = !@PKG@.Tips.isOff(u);',
    '    @PKG@.Tips.setOff(u, off);',
    '    this.infoName = off ? "Hover Tooltips: OFF" : "Hover Tooltips: ON";',
    '    this.status = off ? "Hover tooltips are off - click an item and read it in the box above." : "Hover tooltips are on again.";',
    '    rebuild();',
    '    return;',
    '  }']))

# handleDataEvent: Esc hook -> CloseTask (acts only if the client kept the menu open). EXPERIMENT (see the docstring): do NOT clear the
# grid right here - if the client already closed the page, that update may never be acknowledged and PageManager then drops every
# data event (all buttons of every later page) until the next world change. CloseTask clears + closes only if the menu is still open.
rep('M(page, r"""' + LF + 'public void handleDataEvent(',
    '# 0.1.3 "mesc" = the experimental Esc hook: never send anything here (a page the client already closed may not acknowledge it and' + LF +
    '# PageManager would then drop every later click); CloseTask acts 150 ms later only while this menu is still the open page.' + LF +
    'M(page, r"""' + LF + 'public void handleDataEvent(')
rep(LF.join([
    '    if (data == null) return;',
    '    if (data.indexOf("mclose\\"") >= 0) { closePage(ref, st); return; }']),
    LF.join([
    '    if (data == null) return;',
    '    if (data.indexOf("mesc\\"") >= 0) { new @PKG@.CloseTask(this, this.playerRef).accept(null, null); return; }',
    '    if (data.indexOf("mclose\\"") >= 0) { closePage(ref, st); return; }']))

# review 2026-09-24: player actions + Mods list show the OLD wording while the installed mod is older (PA_LEGACY / MODS "old")
rep(LF.join([
    '    boolean dim = @PKG@.MenuUtil.cmd(c) == null;',
    '    put(slots, @PKG@.MenuData.PA_SLOT[i], @PKG@.MenuData.PA_ICON[i], @PKG@.MenuData.PA_NAME[i] + (dim ? " (not installed)" : ""),',
    '        @PKG@.MenuData.PA_BODY[i].replace("%P", n), dim ? "Not installed on this server" : @PKG@.MenuData.PA_FOOT[i], "pact:" + i, dim);']),
    LF.join([
    '    boolean dim = @PKG@.MenuUtil.cmd(c) == null;',
    '    String pname = @PKG@.MenuData.PA_NAME[i];',
    '    String pbody = @PKG@.MenuData.PA_BODY[i];',
    '    String pfoot = @PKG@.MenuData.PA_FOOT[i];',
    '    int li = dim ? -1 : @PKG@.MenuUtil.legacyPa(@PKG@.MenuData.PA_SLOT[i]);',
    '    if (li >= 0) { pname = @PKG@.MenuData.PAL_NAME[li]; pbody = @PKG@.MenuData.PAL_BODY[li]; pfoot = @PKG@.MenuData.PAL_FOOT[li]; }',
    '    put(slots, @PKG@.MenuData.PA_SLOT[i], @PKG@.MenuData.PA_ICON[i], pname + (dim ? " (not installed)" : ""),',
    '        pbody.replace("%P", n), dim ? "Not installed on this server" : pfoot, "pact:" + i, dim);']))
rep('        @PKG@.MenuData.MOD_NAME[k] + " " + ver + (installed ? "" : " (not installed)"), @PKG@.MenuData.MOD_BODY[k],',
    '        @PKG@.MenuData.MOD_NAME[k] + " " + ver + (installed ? "" : " (not installed)"), @PKG@.MenuUtil.modBody(k),')

# review 2026-09-24: the menu item grant respects profile:busy (tools/PROFILES-CONTRACT.md rule 5). grantNow's 2 = "retry in 1 s"
# (GrantTask.run -> later(1000L), up to 30 tries; SESSION stays unset, so the next world switch schedules a new GrantTask if needed).
rep(LF.join([
    '  if (@PKG@.MenuUtil.count(p, @PKG@.MenuData.ITEM_ID) > 0) { @PKG@.Given.markGiven(u); @PKG@.Given.SESSION.put(u, Boolean.TRUE); return 1; }',
    '  @PKG@.Given.SESSION.put(u, Boolean.TRUE);']),
    LF.join([
    '  if (@PKG@.MenuUtil.count(p, @PKG@.MenuData.ITEM_ID) > 0) { @PKG@.Given.markGiven(u); @PKG@.Given.SESSION.put(u, Boolean.TRUE); return 1; }',
    '  if (@PKG@.MenuUtil.profileBusy(u)) return 2;',
    '  @PKG@.Given.SESSION.put(u, Boolean.TRUE);']))
rep(LF.join([
    '    if (@PKG@.MenuUtil.count(player, @PKG@.MenuData.ITEM_ID) <= 0) {',
    '      if (@PKG@.MenuUtil.giveMenuItem(player)) {']),
    LF.join([
    '    boolean none = @PKG@.MenuUtil.count(player, @PKG@.MenuData.ITEM_ID) <= 0;',
    '    if (none && @PKG@.MenuUtil.profileBusy(u)) {',
    '      pr.sendMessage(@MSG@.raw("[Menu] Your profile is still loading, so you get no new menu item yet. Type /skymenu again in a moment."));',
    '    } else if (none) {',
    '      if (@PKG@.MenuUtil.giveMenuItem(player)) {']))

# review 2026-09-24: the once-per-run command ownership check (MenuUtil.checkAliases) at the first PlayerReadyEvent
rep(LF.join([
    'public void accept(Object ev) {',
    '  try {',
    '    @PRE@ e = (@PRE@) ev;']),
    LF.join([
    'public void accept(Object ev) {',
    '  try {',
    '    if (@PKG@.MenuUtil.firstCheck()) @PKG@.MenuUtil.checkAliases();',
    '    @PRE@ e = (@PRE@) ev;']))

# SeenTick: forget the tooltip cache of players who left
rep('    @PKG@.Given.SESSION.keySet().retainAll(online);',
    '    @PKG@.Given.SESSION.keySet().retainAll(online);' + LF + '    @PKG@.Tips.OFF.keySet().retainAll(online);')

# manifest description
rep('for teleports and warps, Pocket Dimension, Accessory Bag, HUD editor, crafting, skills, collections, bazaar, bank, players, party and a list of every mod with its commands.',
    'for teleports and warps, island menu, Pocket Dimension, Vault, Accessory Bag, HUD editor, crafting, skills, collections, bazaar, bank, reforge, players, party, guild and a list of every mod with its commands.')

# plugin setup
rep('  @PKG@.Given.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("given");',
    '  @PKG@.Given.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("given");' + LF +
    '  @PKG@.Tips.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("notips");')

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
