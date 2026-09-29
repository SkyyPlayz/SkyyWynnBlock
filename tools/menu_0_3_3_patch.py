"""Derive SkyyMenu/build_skyymenu_0.3.3.py from the LIVE SkyyMenu 0.3.2 (python tools/menu_0_3_3_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: 0.3 -> menu_0_3_1_patch.py -> 0.3.1 -> menu_0_3_2_patch.py -> 0.3.2 -> this
patch -> 0.3.3.

0.3.3 = SkyyGear compat (research/SkyyGear-Stage1-Spec.md 7.3.2) + Skyy's Settings locks (OPEN-QUESTIONS "Player Settings", LOCKED
2026-09-25; research/Settings-Spec.md 4.1 / 4.4) + the menu data of rounds 8 and 9:

 1. SKYYGEAR (spec 7.3.2):
     - Identify tile: main slot 26, right of Reforge (free in 0.3.2), icon Ingredient_Crystal_Purple (the build checks the item + its icon
       picture in Assets.zip like every icon), action cmdc:identify. While no /identify command is loaded the 0.1.3 path greys it:
       "Identify (not installed)", footer "Not installed on this server" (MenuPage.fillStatic, unchanged code).
     - Reforge tile (main slot 25) keeps cmdc:reforge; text "Put in a weapon or armor piece and pay coins to reroll its modifiers."
       (SkyyGear 0.1 refuses tools, spec 5.4).
     - Mods list: SkyyGear 0.1 REPLACES SkyyRolls (description, /reforge /identify /gear, the admin-only /gear lines, config file, Server
       Setup page "Gear"). The menu item description, SkyyMenu's own Mods text and the jar manifest name identifying next to reforging.
 2. SETTINGS ICON at main slot 39, immediately left of Mods (40); Server Setup stays at 41; slot 51 is free (build asserts).
 3. SETTINGS VISIBILITY BY PERMISSION (Settings-Spec 4.4 "Who sees a row"):
     - settings:fn:register and settings:def:<key> take an optional 7th element String perm (a permission node). Six elements = every
       player may change it (0.2 - 0.3.2 behaviour). null or "" = no node. A node must be PLAIN (review fix): the menu's own node
       pattern ^[a-z][a-z0-9]*(\\.[a-z0-9]+)+$, max 100 characters - no "-" (the engine's deny prefix would invert the check), no *, :,
       _ or spaces, no "..", no leading / trailing dot. No Skyy mod registers a node yet; every literal node the mods use passes.
     - Anything else REFUSES THE KEY, fail closed (review fix): FALSE, one WARN, and the key stays refused for this server run - an
       earlier registration of it (same mod or not) is dropped, later ones are refused, the row is hidden for everyone, may() is false,
       settings:fn:set refuses it and settings:fn:get answers the registered default (the player's stored choice and the admin default
       are ignored; callers only ever get TRUE / FALSE for it).
     - Two mods on one key (review fix, the STRICTER registration wins): the first registration's texts and default stay, but a node is
       never dropped - no node + a node = gated by that node (also when the first mod registers again, the settings:def: drain); two
       different nodes = the key is refused. One WARN either way. A mod may still change its OWN node to another valid node.
     - The check is PermissionsModule.get().hasPermission(uuid, node) = exactly what PlayerRef.hasPermission(node) runs (HytaleServer.jar
       bytecode: PlayerRef.hasPermission(String) is PermissionsModule.get().hasPermission(this.uuid, node)) = the check the menu uses for
       Server Setup (MenuUtil.isAdmin). Fail closed: no PermissionsModule / any error = hidden. It is never called under a SetReg / SetStore
       lock (SetReg.may reads the registration first, then asks the engine).
     - SettingsPage: rows the player may not change are HIDDEN (SetReg.visible), never greyed; paging and the "N settings" header count
       only visible rows; a tab with no visible row is NOT DRAWN (the other tab buttons close up, same ids, same styles); a stale page
       click on a row whose node the player lost refuses ("You can no longer change that setting.") and redraws.
     - settings:fn:set refuses (FALSE) a key whose node the player lacks. Reset all keeps the player's own choices on keys they may not
       change (only rows they can change go back to the default).
     - SkyyGear's three switches carry no node (spec 9.3): every player sees them.
 4. PLAYER SWITCHES (SET_KNOWN = SET_ORDER + the settings-defaults.properties template, written only when the file is missing):
     - General: party.invites (SkyyParty 0.1.5) is the FIRST General row, tpa.requests + msg.private (SkyyEssentials 0.1.5) around
       tpa.updates - research/Settings-Spec.md 2.2 order (the guild rows of 0.3.1 stay between party and teleports). Skyy answered
       "block" (2026-09-25), so the 0.3.2 assert that forbade the three keys is gone; a new assert keeps the 2.2 order. General = 10 rows.
     - Skills: skills.overallUp (SkyySkills 0.4.6) as row 8.
     - Combat: skills.xbowMeter / xbowSound / xbowHint (SkyySkills 0.4.6) and gear.blockedPopup / armorWarn / notices (SkyyGear 0.1);
       classes.healGiven / healTaken help lines say 10 s (SkyyClasses 0.1.7 = Skyy's edited feedbackMs). Combat = 10 rows.
     - Combat and General need two pages at SET_ROWS 8 (the 0.3.1 Prev / Next code; the build prints the rows per tab).
     Every label / tab / help is the registering mod's exact regSetting text (the live-set check compares them).
 5. MODS LIST TEXTS (rounds 8 + 9, read from the newest scripts): SkyyEssentials 0.1.5 (Server Setup parts, teleports, messages, staff
    bypass, warps, trade - no world-spawn rows; /warpadmin = the Warps page; the /settings switches + privacy.staffBypass), SkyyParty 0.1.5
    (party invites switch, /partyadmin set privacy.staffBypass), SkyySkills 0.4.6 (Overall Level, /skills stats overall), SkyySacks 0.7.7
    (rarity bags + the Mythic Omni Bag, bag recipes from collections), SkyyCollections 0.2.3 (the bag ladder), SkyyClasses 0.1.7 (/class
    arrows; kits land in the hotbar at once), SkyyVault 0.1.3 (buy confirm window, no "type it twice"), SkyyIslands 0.5.3 (island admins
    invite), SkyyRanks 0.1.1 (Member / Admin / Developer / Owner, ops and the Owner rank edit), SkyyTrees 0.2.4, SkyyAuctions 0.1.2.
 6. LIVE-SET CHECK: one function (menu_check) run on SET as tools/deploy_set.py pins it NOW and on THIS ROUND's SET (SET with every
    ROUND_PINS version, the mods the round adds, SkyyMenu VERSION, the ROUND_RETIRED mods out of SET and in RETIRED). ROUND_PINS =
    round 9 (SkyyClasses 0.1.7, SkyyTrees 0.2.4, SkyyVault 0.1.3, SkyyIslands 0.5.3, SkyyRanks 0.1.1) + SkyyAuctions 0.1.2 + SkyyGear 0.1
    (new: (None, "0.1")); ROUND_RETIRED = SkyyRolls 0.1.5 (replaced by SkyyGear). Round 8 is already pinned in SET, so its MODS versions
    equal SET's. Both runs must end in "menu data matches ...". A round version whose build script does not exist yet (SkyyAuctions
    0.1.2 while it is being built) is checked against the replaced version's script, with a note. The regSetting pattern also accepts a
    6th (permission) argument.
 7. Config kit KEEP 20 -> 10 (OPEN-QUESTIONS "In-game server setup" 3, LOCKED 2026-09-25) for SkyyMenu's own config history.
 8. REVIEW FIXES (2026-09-29): the SetReg rules of 3 (refused keys fail closed, plain nodes only, the stricter node wins; the live-set
    check also flags a regSetting node that is not plain); Commands lines marked (admin) or (staff) are no longer in MOD_BODY (the Mods
    text every player reads, e.g. /classadmin, /ahadmin, /fly) - admins read them in the "Admin only:" block (MOD_AONLY = the same lines
    MOD_ADMIN lists on the Server Setup page); the SkyyRanks admin line names SkyyRanks 0.1.1's real syntax (/rank set <player> <rank>).

CHECKED: build (both live-set runs "menu data matches"), python tools/ci/lint.py, and the bare-JVM harness SkyyMenu/test_skyymenu_0.3.3.py
(-Xverify:all; the engine's own PermissionsModule.hasPermission behind a fake provider; the real SettingsPage.build; see its count).

NOT CHANGED: the menu / Settings / Server Setup page looks (the vanilla pass of the existing pages is RESUME step 5; the only new UI item is
one grid tile with a vanilla item icon), every command, node, file, bridge key and default, the config kit version (1.1).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.2.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.3.py")
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
        assert n == count, "anchor count %d != %d: %s" % (n, count, old[:100])
        s = s.replace(old, new)


def cut(a, b, new):
    """replace everything from anchor a (included) up to anchor b (kept) with new"""
    global s
    assert s.count(a) == 1, "cut start count %d: %s" % (s.count(a), a[:100])
    assert s.count(b) == 1, "cut end count %d: %s" % (s.count(b), b[:100])
    i, j = s.index(a), s.index(b)
    assert i < j, "cut anchors out of order: %s / %s" % (a[:60], b[:60])
    s = s[:i] + new + s[j:]


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF + "0.3.2: menu data for round 6",
    '"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF +
    "0.3.3: SkyyGear compat + Skyy's Settings locks (research/SkyyGear-Stage1-Spec.md 7.3.2, research/Settings-Spec.md 4.1 / 4.4): an" + LF +
    "       Identify tile (main slot 26, /identify, greyed while SkyyGear is absent), Reforge text for SkyyGear, SkyyGear 0.1 replaces SkyyRolls" + LF +
    "       in the Mods list; the Settings torch at main slot 39 (left of Mods); settings visibility by permission (optional 7th registration" + LF +
    "       element = a node; rows the player may not change are hidden, never greyed; settings:fn:set refuses them); the refusing General" + LF +
    "       switches party.invites / tpa.requests / msg.private, skills.overallUp, the crossbow switches and SkyyGear's three in the known" + LF +
    "       list; Mods texts of rounds 8 + 9; the live-set check also accepts this round's SET (ROUND_PINS / ROUND_RETIRED); kit KEEP 10." + LF +
    "       Review fixes: a bad node refuses the key for good (hidden, set refused, get = its default), plain nodes only, the stricter" + LF +
    "       node wins when two mods register one key; (admin) / (staff) Commands lines only in the admins' Mods text; /rank set <player> <rank>." + LF +
    "       Notes: tools/menu_0_3_3_patch.py." + LF +
    "0.3.2: menu data for round 6")
rep('VERSION = "0.3.2"', 'VERSION = "0.3.3"')

# ---------------------------------------------------------------------------------------------------------------- the kit pin names this patch
rep("# 0.3.1: the config kit this jar carries (tools/menu_0_3_1_patch.py pins it, 0.3.2 keeps the pin - change it with a rep in" + LF +
    "# tools/menu_0_3_2_patch.py; see the \"config kit\" lines of the build output)",
    "# 0.3.1: the config kit this jar carries (tools/menu_0_3_1_patch.py pins it, 0.3.2 and 0.3.3 keep the pin - change it with a rep in" + LF +
    "# tools/menu_0_3_3_patch.py; see the \"config kit\" lines of the build output)")
rep('"set EXPECTED_KIT through tools/menu_0_3_2_patch.py (or its successor), regenerate, re-test"',
    '"set EXPECTED_KIT through tools/menu_0_3_3_patch.py (or its successor), regenerate, re-test"')
# LOCKED 2026-09-25 (OPEN-QUESTIONS "In-game server setup" 3): 10 old config file versions
rep('FILES=MENU_CFG_FILES, NOTE=MENU_CFG_NOTE, RELOAD="MenuCfg.load", KEEP=20,',
    'FILES=MENU_CFG_FILES, NOTE=MENU_CFG_NOTE, RELOAD="MenuCfg.load", KEEP=10,')

# ---------------------------------------------------------------------------------------------------------------- the menu item text + manifest
rep('"the auction house, the bank, reforging, your party and guild, your settings and a list of every mod with its commands."',
    '"the auction house, the bank, reforging and identifying gear, your party and guild, your settings and a list of every mod with "'
    + LF + '                  "its commands."')
rep("bazaar, auction house, bank, reforge, players, party, guild, a list of every mod",
    "bazaar, auction house, bank, reforge, identify, players, party, guild, a list of every mod")

# ---------------------------------------------------------------------------------------------------------------- menu entries: Reforge, Identify, Settings
rep('''    ("main", 25, "Tool_Hammer_Iron", "Reforge",
        ["Put in a weapon, armor piece or tool and pay coins to reroll its stats.", "Command: /reforge"], "Click to open!", "cmdc:reforge"),''',
    '''    # 0.3.3: SkyyGear 0.1 owns /reforge (the same command SkyyRolls had): weapons and armor, tools are refused (SkyyGear spec 5.4)
    ("main", 25, "Tool_Hammer_Iron", "Reforge",
        ["Put in a weapon or armor piece and pay coins to reroll its modifiers.", "Command: /reforge"], "Click to open!", "cmdc:reforge"),
    # 0.3.3: Identify right of Reforge (SkyyGear 0.1 /identify, spec 7.3.2); greyed "(not installed)" while no /identify command is loaded
    ("main", 26, "Ingredient_Crystal_Purple", "Identify",
        ["Reveal the modifiers of unidentified weapons and armor from mobs and loot chests. Costs coins by rarity and level.",
         "Command: /identify"], "Click to open!", "cmdc:identify"),''')
rep('''    # 0.2: Settings in the bottom row next to Close (SkyBlock's Redstone Torch spot, research/Settings-Spec.md 4.1)
    ("main", 51, "Furniture_Crude_Torch", "Settings",''',
    '''    # 0.3.3: Settings immediately LEFT of Mods (LOCKED 2026-09-25, research/Settings-Spec.md 4.1). 0.2 - 0.3.2 had it at slot 51 next to Close
    ("main", 39, "Furniture_Crude_Torch", "Settings",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyMenu
rep('''collections, the bazaar, the auction house, the bank, reforging, players, your party and guild, your settings, this list of mods and Server Setup for admins.",''',
    '''collections, the bazaar, the auction house, the bank, reforging and identifying gear, players, your party and guild, your settings, this list of mods and Server Setup for admins.",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyIslands 0.5.3
rep('''    {"mod": "SkyyIslands", "version": "0.5.2", "icon": "Soil_Grass", "check": "island",''',
    '''    # 0.3.3: SkyyIslands 0.5.3 (round 9): island admins may invite co-op members, visitor limit 10, beds stay member-only
    {"mod": "SkyyIslands", "version": "0.5.3", "icon": "Soil_Grass", "check": "island",''')
rep('''                  "/island invite <player> - invite a co-op member (they /island accept)",''',
    '''                  "/island invite <player> - (owner or island admin) invite a co-op member",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyySacks 0.7.7
rep('''    {"mod": "SkyySacks", "version": "0.7.6", "icon": "Tool_Feedbag", "check": "sacks",
     "config": "Skyy_SkyySacks/config.properties", "reload": "", "note": "It is read again by itself within about 10 seconds.",
     "setup": ("0.7.6", "Bags and Crafting", "craft search box, bag caps, Furnace and Tannery"),
     "desc": "Magic Bags: carry a Mining, Foraging, Farming, Combat or Smithing bag and what you gather of that type goes straight into your Pocket Dimension. /craft crafts from your inventory and bags (Smithing, Farming, Furnace, Tannery and more tabs).",''',
    '''    # 0.3.3: SkyySacks 0.7.7 (round 8): Magic Bags by rarity + the Mythic Omni Bag, bag recipes unlocked by collections
    {"mod": "SkyySacks", "version": "0.7.7", "icon": "Tool_Feedbag", "check": "sacks",
     "config": "Skyy_SkyySacks/config.properties", "reload": "", "note": "It is read again by itself within about 10 seconds.",
     "setup": ("0.7.6", "Bags and Crafting", "craft search, bag caps by rarity, free bag recipes, Furnace"),
     "desc": "Magic Bags in four rarities (Normal, Unique, Rare, Legendary) send what you gather of their type - Mining, Foraging, Farming, Combat or Smithing - straight into your Pocket Dimension, and the Mythic Omni Bag does it for every type. Collections unlock the bag recipes. /craft crafts from your inventory and bags.",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyySkills 0.4.6 (round 8, pinned)
rep('''    # 0.3.2: 0.4.5 = this round's pin (ROUND_PINS below; SET pins 0.4.4 until the round deploys). 0.4.4 added Fury + Divinity (Divinity
    # XP from Priest heals, divinity.* rows), 0.4.5 crossbows stay loaded (Archery level 5): no new command, switch or page title
    {"mod": "SkyySkills", "version": "0.4.5", "icon": "Weapon_Sword_Iron", "check": "skills",
     "config": "Skyy_SkyySkills/xp.properties", "reload": "skills reload", "note": "",
     "setup": ("0.4.3", "Skills", "levels, XP rates, perks, Divinity heal XP, parts on or off"),
     "desc": "Hypixel-style skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill (Archery, Swordsmanship, Sorcery, Fury or Divinity) - that level up as you play and pay coins on every level up.",
     "commands": ["/skills (or /skill) - open your Skills", "/skills stats <skill> - the Stats page of a skill",''',
    '''    # 0.3.3: SkyySkills 0.4.6 (round 8, pinned): base Mana, the Overall Level (skills.overallUp), crossbow extras (skills.xbow* switches)
    {"mod": "SkyySkills", "version": "0.4.6", "icon": "Weapon_Sword_Iron", "check": "skills",
     "config": "Skyy_SkyySkills/xp.properties", "reload": "skills reload", "note": "",
     "setup": ("0.4.3", "Skills", "levels, XP rates, perks, Overall Level, Mana, parts on/off"),
     "desc": "Hypixel-style skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill (Archery, Swordsmanship, Sorcery, Fury or Divinity) - that level up as you play and pay coins on every level up. Your Overall Level adds a little Health and Mana.",
     "commands": ["/skills (or /skill) - open your Skills", "/skills stats <skill> - the Stats page of a skill (or overall)",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyTrees 0.2.4
rep('''    {"mod": "SkyyTrees", "version": "0.2.3", "icon": "Plant_Sapling_Maple", "check": "tree",''',
    '''    # 0.3.3: SkyyTrees 0.2.4 (round 9): Tree Feller 1/2/4/5/6/10, Double Jump in tier III - no new command, switch or page title
    {"mod": "SkyyTrees", "version": "0.2.4", "icon": "Plant_Sapling_Maple", "check": "tree",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyCollections 0.2.3
rep('''    {"mod": "SkyyCollections", "version": "0.2.2", "icon": "Furniture_Village_Painting_1x1", "check": "collections",
     "config": "Skyy_SkyyCollections/config.properties,Skyy_SkyyCollections/collections.properties,Skyy_SkyyCollections/rewards.properties", "reload": "collections reload", "note": "",
     "setup": ("0.2.2", "Collections", "curves, tier rewards, coin unlocks, rules"),
     "desc": "Hypixel-style Collections: everything you gather counts toward tiers. Tiers unlock crafting recipes for the /craft page and pay rewards.",''',
    '''    # 0.3.3: SkyyCollections 0.2.3 (round 8): the Magic Bag ladder - each bag type unlocks from one collection at tiers I / III / V / VII
    {"mod": "SkyyCollections", "version": "0.2.3", "icon": "Furniture_Village_Painting_1x1", "check": "collections",
     "config": "Skyy_SkyyCollections/config.properties,Skyy_SkyyCollections/collections.properties,Skyy_SkyyCollections/rewards.properties", "reload": "collections reload", "note": "",
     "setup": ("0.2.2", "Collections", "curves, tier rewards, bag ladder, coin unlocks, rules"),
     "desc": "Hypixel-style Collections: everything you gather counts toward tiers. Tiers unlock crafting recipes and pay rewards - each Magic Bag type climbs one collection: Normal, Unique, Rare and Legendary at tiers I, III, V and VII.",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyClasses 0.1.7
rep('''    # 0.3.2: SkyyClasses 0.1.6 (round 6): Berserker (Fury) + Priest (Divinity) playable, class kits (/class kit, /classadmin kit)
    {"mod": "SkyyClasses", "version": "0.1.6", "icon": "Weapon_Shortbow_Iron", "check": "class",
     "config": "Skyy_SkyyClasses/config.properties", "reload": "classadmin reload", "note": "",
     "setup": ("0.1.5", "Classes", "weapon lock, class picker, class kits, Priest heal"),
     "admin": ["/classadmin kit <player> [class] - (admin) give a player a class kit now"],
     "desc": "Classes: Archer, Warrior, Mage, Berserker or Priest (the party healer) - Assassin and Shaman later. Each class has its own weapons and weapon skill and a kit with its basic weapon. With SkyyProfiles the class is picked when you create a profile.",
     "commands": ["/class (or /classes) - open the class page",
                  "/class kit - collect kit items that did not fit (or see your kit)",''',
    '''    # 0.3.2: SkyyClasses 0.1.6 (round 6): Berserker (Fury) + Priest (Divinity) playable, class kits (/class kit, /classadmin kit)
    # 0.3.3: SkyyClasses 0.1.7 (round 9): kits land in the hotbar at once (no wait), /class arrows (daily Archer arrows), Healing Totem = Priest
    {"mod": "SkyyClasses", "version": "0.1.7", "icon": "Weapon_Shortbow_Iron", "check": "class",
     "config": "Skyy_SkyyClasses/config.properties", "reload": "classadmin reload", "note": "",
     "setup": ("0.1.5", "Classes", "weapon lock, class picker, kits, Priest heal, Archer arrows"),
     "admin": ["/classadmin kit <player> [class] - (admin) give a player a class kit now"],
     "desc": "Classes: Archer, Warrior, Mage, Berserker or Priest (the party healer) - Assassin and Shaman later. Each class has its own weapons and weapon skill and a kit with its basic weapon that lands in your hotbar at once. With SkyyProfiles the class is picked when you create a profile.",
     "commands": ["/class (or /classes) - open the class page",
                  "/class kit - collect kit items that did not fit your hotbar (or see your kit)",
                  "/class arrows - (Archers) claim your free daily arrows",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyAuctions 0.1.2 (round pin)
rep('''    {"mod": "SkyyAuctions", "version": "0.1.1", "icon": "Ingredient_Bar_Gold", "check": "ah",
     "config": "Skyy_SkyyAuctions/config.properties,Skyy_Market/blocked.txt", "reload": "ahadmin reload", "note": "",
     "desc": "A Hypixel-style Auction House (Buy It Now): list an item for a fixed price, buy what other players list and claim the coins and items you are owed.",''',
    '''    # 0.3.3: SkyyAuctions 0.1.2 = this round's pin (SkyyGear spec 7.3.1: gear rarity + modifiers through the bridge, 48h = double listing
    # fee, other profiles may buy, Magic Bags blocked) - same commands and files
    {"mod": "SkyyAuctions", "version": "0.1.2", "icon": "Ingredient_Bar_Gold", "check": "ah",
     "config": "Skyy_SkyyAuctions/config.properties,Skyy_Market/blocked.txt", "reload": "ahadmin reload", "note": "",
     "desc": "A Hypixel-style Auction House (Buy It Now): list an item for a fixed price, buy what other players list and claim the coins and items you are owed. Gear shows its rarity and modifiers. Magic Bags cannot be sold.",''')
rep('''                  "/ahadmin list|info|remove|reload|pause|resume - (admin)"]},''',
    '''                  "/ahadmin list|info|remove|reload|pause|resume|regrant - (admin)"]},''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyVault 0.1.3
rep('''    {"mod": "SkyyVault", "version": "0.1.2", "icon": "Furniture_Royal_Magic_Chest_Large", "check": "vault",
     "config": "Skyy_SkyyVault/config.properties", "reload": "vaultadmin reload", "note": "",
     "setup": ("0.1.1", "Vault", "free pages, prices, page size, arrows, after-switch wait"),''',
    '''    # 0.3.3: SkyyVault 0.1.3 (round 9): pages from buyConfirmCoins up ask in a confirm window (the 0.1.2 second-click buy is gone)
    {"mod": "SkyyVault", "version": "0.1.3", "icon": "Furniture_Royal_Magic_Chest_Large", "check": "vault",
     "config": "Skyy_SkyyVault/config.properties", "reload": "vaultadmin reload", "note": "",
     "setup": ("0.1.1", "Vault", "free pages, prices, buy confirm, page size, arrows, waits"),''')
rep('''"/vault buy - buy the next page (type it twice)",''', '''"/vault buy - buy the next page (a window may ask you to confirm)",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyParty 0.1.5 (round 8, pinned)
rep('''    {"mod": "SkyyParty", "version": "0.1.4", "icon": "Deco_Scroll", "check": "party",
     "config": "Skyy_SkyyParty/config.properties", "reload": "partyadmin reload", "note": "",
     "setup": ("0.1.4", "Party", "the largest party and how long an invite lasts"),
     "admin": ["/partyadmin - (admin) the party settings and how to change them",
               "/partyadmin set <maxSize|inviteSeconds> <value> - (admin) change one",
               "/partyadmin reload - (admin) re-read config.properties"],
     "desc": "Team up with friends: invite players to a party, chat privately and see your party on the HUD. The lead passes on if the leader leaves.",''',
    '''    # 0.3.3: SkyyParty 0.1.5 (round 8, pinned): the party.invites switch refuses invites; staff bypass row privacy.staffBypass
    {"mod": "SkyyParty", "version": "0.1.5", "icon": "Deco_Scroll", "check": "party",
     "config": "Skyy_SkyyParty/config.properties", "reload": "partyadmin reload", "note": "",
     "setup": ("0.1.4", "Party", "party size, invite time, staff bypass"),
     "admin": ["/partyadmin - (admin) the party settings and how to change them",
               "/partyadmin set <maxSize|inviteSeconds|privacy.staffBypass> <value> - (admin)",
               "/partyadmin reload - (admin) re-read config.properties"],
     "desc": "Team up with friends: invite players to a party, chat privately and see your party on the HUD. Turn party invites off in /settings to refuse them (staff get through while privacy.staffBypass is on).",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyGuilds (the 0.3.2 round pin is pinned now)
rep('''    # 0.3.2: 0.1.3 = this round's pin (ROUND_PINS): Fury + Divinity count for guild XP; same commands, switches and page title''',
    '''    # 0.3.2: SkyyGuilds 0.1.3 (pinned since round 7): Fury + Divinity count for guild XP; same commands, switches and page title''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyEssentials 0.1.5 (round 8, pinned)
rep('''    {"mod": "SkyyEssentials", "version": "0.1.4", "icon": "Tool_Map", "check": "tpa",
     "config": "Skyy_SkyyEssentials/config.properties", "reload": "tradeadmin reload", "note": "Also in game: /tradeadmin config, /warpadmin. replyShortcut needs a restart.",
     "setup": ("0.1.3", "Essentials", "teleports, messages, warps, world spawn, trade"),
     "admin": ["/warpadmin - (admin) warps editor: add, move, rename, remove, world spawn",''',
    '''    # 0.3.3: SkyyEssentials 0.1.5 (round 8, pinned): tpa.requests + msg.private refuse the sender, staff bypass row privacy.staffBypass,
    # Server Setup parts / teleports / messages / privacy / warps / trade - the world-spawn rows are gone, /warpadmin is the Warps page
    {"mod": "SkyyEssentials", "version": "0.1.5", "icon": "Tool_Map", "check": "tpa",
     "config": "Skyy_SkyyEssentials/config.properties", "reload": "tradeadmin reload", "note": "Also in game: /tradeadmin config, /warpadmin. replyShortcut needs a restart.",
     "setup": ("0.1.3", "Essentials", "parts, teleports, messages, staff bypass, warps, trade"),
     "admin": ["/warpadmin - (admin) the Warps page: add, move, rename, remove and visit warps",''')
rep('''     "desc": "Everyday commands the base game is missing: teleport requests between players, private messages and safe trades of items and coins.",''',
    '''     "desc": "Everyday commands the base game is missing: teleport requests between players, private messages and safe trades of items and coins. Turn teleport requests or private messages off in /settings (staff get through while privacy.staffBypass is on).",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyRolls -> SkyyGear 0.1
rep('''    {"mod": "SkyyRolls", "version": "0.1.5", "icon": "Weapon_Longsword_Copper", "check": "rolls",
     "config": "Skyy_SkyyRolls/reforge.properties", "reload": "", "note": "It is read again by itself whenever someone opens /reforge.",
     "setup": ("0.1.5", "Rolls", "the reforge cost of each rarity"),
     "desc": "Random item stats (reforges) on weapons, armor and tools, shown on the item. Reforge an item for coins on the reforge page.",
     "commands": ["/reforge - open the reforge page", "/rolls give <item> - (admin) an item with random stats",
                  "/rolls read | reroll | clear - (admin) the item in your hand"]},''',
    '''    # 0.3.3: SkyyGear 0.1 REPLACES SkyyRolls (research/SkyyGear-Stage1-Spec.md 7.3.2 + 8; ROUND_RETIRED below): /reforge moved, /identify,
    # /gear and the admin /gear lines (every /gear sub-command needs skyygear.admin). Server Setup -> Gear comes from its config:def:SkyyGear
    {"mod": "SkyyGear", "version": "0.1", "icon": "Weapon_Longsword_Copper", "check": "gear",
     "config": "Skyy_SkyyGear/config.properties", "reload": "", "note": "Set up in game - Server Setup, Gear.",
     "setup": ("0.1", "Gear", "rarities, levels, costs and odds"),
     "admin": ["/gear give <item> [--rarity <id>] [--unid true] - (admin) a gear item",
               "/gear read | reroll | clear - (admin) the item in your hand",
               "/gear rarity <id> | unid | identify - (admin) the item in your hand",
               "/gear level <n|clear> | gate <skill|class> - (admin) the item in your hand",
               "/gear migrate [player] - (admin) run the old rolled items scan now"],
     "desc": "Rarity, level and modifiers on every weapon and armor piece: crafted gear rolls, mob and chest gear drops unidentified, /identify reveals it, /reforge rerolls it.",
     "commands": ["/reforge - reroll the modifiers of a weapon or armor piece for coins",
                  "/identify - reveal the modifiers of unidentified gear for coins",
                  "/gear - the held item's gear lines, your totals and your Smithing rarity"]},''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyRanks 0.1.1
rep('''    {"mod": "SkyyRanks", "version": "0.1", "icon": "Furniture_Royal_Magic_Chair", "check": "rankadmin",''',
    '''    # 0.3.3: SkyyRanks 0.1.1 (round 9): seeds Member / Admin / Developer + the protected Owner rank; the editor = ops + the Owner rank
    {"mod": "SkyyRanks", "version": "0.1.1", "icon": "Furniture_Royal_Magic_Chair", "check": "rankadmin",''')
# review fix: SkyyRanks 0.1.1's real syntax (RkSetCmd "/rank set <player> <rank>", RkClearCmd "/rank clear <player>")
rep('''               "/rank set | clear <player> - (admin) give or take a rank in chat",''',
    '''               "/rank set <player> <rank> | clear <player> - (admin) give or take a rank in chat",''')
rep('''     "desc": "Server ranks with a chat prefix in front of your name. The admins make the ranks and what each rank may do, all in game.",''',
    '''     "desc": "Server ranks with a chat prefix in front of your name - Member, Admin, Developer and Owner to start. Ops and the Owner rank make the ranks and what each rank may do, all in game.",''')

# ---------------------------------------------------------------------------------------------------------------- Settings: known switches
rep('''# ---- Settings (0.2, research/Settings-Spec.md sections 2 + 4): the player Settings page (/settings, the torch at main slot 51).''',
    '''# ---- Settings (0.2, research/Settings-Spec.md sections 2 + 4): the player Settings page (/settings, the torch at main slot 39 since 0.3.3).''')
rep('''# Every known switch, all default ON: (key, tab id, label, help line, registered by). Settings-Spec 2.2 WITHOUT the three refusing
# General switches (party.invites, tpa.requests, msg.private) - Skyy has not answered refuse-vs-hide yet (spec section 6).''',
    '''# Every known switch, all default ON: (key, tab id, label, help line, registered by). Settings-Spec 2.2 order. 0.3.3: WITH the three
# refusing General switches (party.invites, tpa.requests, msg.private) - Skyy answered "block" on 2026-09-25 (SkyyParty 0.1.5 and
# SkyyEssentials 0.1.5 register them). A switch whose mod registers a permission node (7th element, 0.3.3) is shown only to holders.''')
rep('''    ("explore.finds",        "skills",      "Exploration finds",            "Loot chests, chest luck, new zones, discoveries, checklists and new titles", "SkyyExploration"),''',
    '''    ("explore.finds",        "skills",      "Exploration finds",            "Loot chests, chest luck, new zones, discoveries, checklists and new titles", "SkyyExploration"),
    # 0.3.3: SkyySkills 0.4.6 (research/Overall-Level-Spec.md): the Overall Level line, Skills tab row 8
    ("skills.overallUp",     "skills",      "Overall Level ups",            "OVERALL LEVEL UP 12 -> 13 with the max Health and Mana it added", "SkyySkills"),''')
rep('''    ("classes.healGiven",    "combat",      "Priest heals - your heals",    "Your heals: +23 HP to 2 party members and +6 HP to you - one line every 5 s at most", "SkyyClasses"),
    ("classes.healTaken",    "combat",      "Priest heals - healed by others", "Skyy healed you +12 HP - one line every 5 s at most. The heal happens either way", "SkyyClasses"),''',
    '''    # 0.3.3: SkyyClasses 0.1.7 texts: one line every 10 s (Skyy's edited priestHeal.feedbackMs default)
    ("classes.healGiven",    "combat",      "Priest heals - your heals",    "Your heals: +23 HP to 2 party members and +6 HP to you - one line every 10 s at most", "SkyyClasses"),
    ("classes.healTaken",    "combat",      "Priest heals - healed by others", "Skyy healed you +12 HP - one line every 10 s at most. The heal happens either way", "SkyyClasses"),
    # 0.3.3: SkyyGear 0.1's three switches (spec 9.3, no permission node = every player sees them)
    ("gear.blockedPopup",    "combat",      "Gear level popups",            "Popup when a weapon is too high level or unidentified", "SkyyGear"),
    ("gear.armorWarn",       "combat",      "Armor level warning",          "Chat line when armor gives no stats because of its level", "SkyyGear"),
    ("gear.notices",         "combat",      "Gear update notices",          "One-time line when your old rolled items move to the new gear system", "SkyyGear"),
    # 0.3.3: SkyySkills 0.4.6's crossbow switches (LOCKED 2026-09-25: meter, sound and hint each switchable)
    ("skills.xbowMeter",     "combat",      "Crossbows keep the big-arrow meter", "Your crossbow's big-arrow meter comes back with its bolts when you switch back to it", "SkyySkills"),
    ("skills.xbowSound",     "combat",      "Crossbow reload sound",        "The crossbow load sound when your kept bolts go back in (Archery perk)", "SkyySkills"),
    ("skills.xbowHint",      "combat",      "Crossbow reload chat line",    "Crossbow reloaded - 6 bolts back in - when your kept bolts return", "SkyySkills"),''')
rep('''    ("party.members",        "general",     "Party join, leave and leader", "Steve joined, left, disconnected or is now the party leader", "SkyyParty"),''',
    '''    # 0.3.3: SkyyParty 0.1.5 - the FIRST General row (Settings-Spec 2.2); OFF refuses the inviter
    ("party.invites",        "general",     "Party invites",                "OFF: other players can't invite you - they are told so", "SkyyParty"),
    ("party.members",        "general",     "Party join, leave and leader", "Steve joined, left, disconnected or is now the party leader", "SkyyParty"),''')
rep('''    ("tpa.updates",          "general",     "Teleport request updates",     "Denied, expired and cancelled requests - accepted ones always show", "SkyyEssentials"),''',
    '''    # 0.3.3: SkyyEssentials 0.1.5's refusing switches around tpa.updates (Settings-Spec 2.2 order)
    ("tpa.requests",         "general",     "Teleport requests",            "OFF: nobody can send you /tpa or /tpahere - they are told (staff may still)", "SkyyEssentials"),
    ("tpa.updates",          "general",     "Teleport request updates",     "Denied, expired and cancelled requests - accepted ones always show", "SkyyEssentials"),
    ("msg.private",          "general",     "Private messages",             "OFF: /msg and /reply to you are refused and the sender is told (staff may still)", "SkyyEssentials"),''')
rep('''    "RESET":  "Every setting is back to its default.",''',
    '''    "RESET":  "Every setting is back to its default.",
    "GONE":   "You can no longer change that setting.",      # 0.3.3: a stale click on a row whose permission node the player lost''')

# ---------------------------------------------------------------------------------------------------------------- MENU DATA: round pins + retired
rep('''# ---- 0.3.2: versions THIS round pins that tools/deploy_set.py SET does not carry yet (they deploy together with this SkyyMenu):
# mod: (the SET version the round replaces, the round's version). MODS may already name the round's version; the live-set cross-check
# accepts it while SET still pins the replaced version and reads the round's build script once it exists. Inert once SET pins it.
ROUND_PINS = {"SkyySkills": ("0.4.4", "0.4.5"), "SkyyGuilds": ("0.1.2", "0.1.3")}''',
    '''# ---- 0.3.3: the round this SkyyMenu deploys WITH (round 9 + the SkyyGear round; round 8 is already pinned in tools/deploy_set.py SET):
# mod: (the SET version the round replaces - None for a mod the round ADDS -, the round's version). MODS names the round's version. The
# live-set check accepts it while SET still pins the replaced version (or lacks the new mod), reads the round's build script once it
# exists and runs a second time on the SET the main session pins when the round deploys (see menu_check). Inert once SET pins it.
ROUND_PINS = {"SkyyClasses": ("0.1.6", "0.1.7"), "SkyyTrees": ("0.2.3", "0.2.4"), "SkyyVault": ("0.1.2", "0.1.3"),
              "SkyyIslands": ("0.5.2", "0.5.3"), "SkyyRanks": ("0.1", "0.1.1"), "SkyyAuctions": ("0.1.1", "0.1.2"),
              "SkyyGear": (None, "0.1")}
# mods this round RETIRES: mod: (the SET version that leaves, the MODS entry that replaces it). The main session drops it from SET and puts
# it into tools/deploy_set.py RETIRED (SkyyGear spec 8.3); MODS no longer lists it.
ROUND_RETIRED = {"SkyyRolls": ("0.1.5", "SkyyGear")}''')

# ---------------------------------------------------------------------------------------------------------------- build checks: slots + switches
rep('''for _k in ("party.invites", "tpa.requests", "msg.private"):
    assert _k not in SET_ORDER, "%s refuses the other player - not built until Skyy answers refuse-vs-hide (Settings-Spec section 6)" % _k''',
    '''# 0.3.3: Skyy answered "block" (2026-09-25): the three refusing General switches are known, in Settings-Spec 2.2 order - party.invites is
# the FIRST General row, then tpa.requests before tpa.updates before msg.private
_gen = [k[0] for k in SET_KNOWN if k[1] == "general"]
assert _gen and _gen[0] == "party.invites", "party.invites is the first General row (Settings-Spec 2.2)"
assert _gen.index("tpa.requests") < _gen.index("tpa.updates") < _gen.index("msg.private"), "General order: tpa.requests, tpa.updates, msg.private"
SET_TAB_ROWS = [(t[0], len([k for k in SET_KNOWN if k[1] == t[0]])) for t in SET_TABS]
assert all(n <= 3 * SET_ROWS for _c, n in SET_TAB_ROWS), "a tab would need more than 3 pages: %s" % SET_TAB_ROWS''')
rep('''assert used.get(("main", 51)) == "Settings", "the Settings torch belongs at main slot 51 (Settings-Spec 4.1)"''',
    '''assert used.get(("main", 39)) == "Settings" and used.get(("main", 40)) == "Mods", \\
    "the Settings torch belongs at main slot 39, immediately left of Mods (LOCKED 2026-09-25, Settings-Spec 4.1)"
assert ("main", 51) not in used, "main slot 51 is free since 0.3.3 (the torch moved to 39)"
# 0.3.3: Identify right of Reforge (SkyyGear spec 7.3.2)
assert used.get(("main", 25)) == "Reforge" and used.get(("main", 26)) == "Identify", "Reforge at main slot 25, Identify at 26"
assert [e for e in ENTRIES if e[:3] == ("main", 26, "Ingredient_Crystal_Purple") and e[6] == "cmdc:identify"], "Identify runs /identify"
assert [e for e in ENTRIES if e[:2] == ("main", 25) and e[6] == "cmdc:reforge" and "modifiers" in e[4][0] and "tool" not in e[4][0]], \\
    "Reforge text is SkyyGear's (weapons and armor, modifiers)"''')

# ---------------------------------------------------------------------------------------------------------------- build checks: MODS texts + round data
rep('''for _rm, (_rfrom, _rto) in ROUND_PINS.items():
    assert _rm in _bym and VER_RE.match(_rfrom) and VER_RE.match(_rto) and ver_t(_rfrom) < ver_t(_rto), "ROUND_PINS %s" % _rm
''',
    '''# 0.3.3: round data - MODS names every round version, a retired mod is out of MODS and replaced by a MODS entry
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
''')

# ---------------------------------------------------------------------------------------------------------------- live-set check: one function, two runs
NEW_CHECK = r'''# 0.3.1: the menu data must follow the live set (tools/deploy_set.py SET) and every live mod's own texts. Differences are printed as
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
_PATCH = "tools/menu_0_3_3_patch.py"


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
        _em = _EMIT.findall(t)
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
print("settings rows per tab (%d per page): %s" % (SET_ROWS, ", ".join("%s %d%s" % (c, n, " (2 pages)" if n > SET_ROWS else "")
                                                                  for c, n in SET_TAB_ROWS)))

'''
cut("# 0.3.1: the menu data must follow the live set (tools/deploy_set.py SET) and every live mod's own texts. Differences are printed as",
    "# ================= /menu and /sbmenu only when nothing else uses them", NEW_CHECK)

# ---------------------------------------------------------------------------------------------------------------- review fix: admin lines only for admins
rep('''MOD_BODY = [txt(m["desc"]) + "\\nCommands:\\n" + "\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m["commands"]) for m in MODS]
MOD_OLD_NEED = [m["old"]["need"] if "old" in m else "" for m in MODS]
MOD_OLD_BODY = [(txt(m["old"]["desc"]) + "\\nCommands:\\n" + "\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m["old"]["commands"]))
                if "old" in m else "" for m in MODS]''',
    '''# 0.3.3 (review): a Commands line marked (admin) or (staff) is admin-only too - it is never in MOD_BODY / MOD_OLD_BODY (the Mods text
# every player reads); admins read it in the "Admin only:" block (MOD_AONLY below = exactly the lines MOD_ADMIN lists on the Server
# Setup page: those Commands lines, then the MODS "admin" lines)
def admin_line(c):
    return "(admin)" in c or "(staff)" in c
def player_lines(cmds):
    return [c for c in cmds if not admin_line(c)]
def admin_lines(m):
    return [c for c in m["commands"] if admin_line(c)] + m.get("admin", [])
for _m in MODS:
    assert player_lines(_m["commands"]) and ("old" not in _m or player_lines(_m["old"]["commands"])), \\
        "%s: every Commands line is admin-only - players need one line (e.g. 'No commands for players - ...')" % _m["mod"]
MOD_BODY = [txt(m["desc"]) + "\\nCommands:\\n" + "\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in player_lines(m["commands"]))
            for m in MODS]
MOD_OLD_NEED = [m["old"]["need"] if "old" in m else "" for m in MODS]
MOD_OLD_BODY = [(txt(m["old"]["desc"]) + "\\nCommands:\\n" + "\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in player_lines(m["old"]["commands"])))
                if "old" in m else "" for m in MODS]
for _i, _m in enumerate(MODS):
    assert MOD_ADMIN[_i] == "\\n".join(c.replace("%ALIASES%", "") for c in admin_lines(_m)), "%s: MOD_ADMIN lines" % _m["mod"]
for _b in MOD_BODY + MOD_OLD_BODY:
    assert "(admin)" not in _b and "(staff)" not in _b, "an admin line in the players' Mods text: " + _b[:80]''')
rep('''MOD_AONLY = ["\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m.get("admin", [])) for m in MODS]''',
    '''# 0.3.3 (review): + the (admin) / (staff) Commands lines (admin_lines = the MOD_ADMIN lines), which MOD_BODY no longer carries
MOD_AONLY = ["\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in admin_lines(m)) for m in MODS]''')
rep('''MOD_ABODY = [(txt(m["desc"]) + "\\n" + MOD_AHEAD + "\\n" + MOD_AONLY[i] + "\\nCommands:\\n" +
              "\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m["commands"])) if MOD_AONLY[i] else MOD_BODY[i]''',
    '''MOD_ABODY = [(txt(m["desc"]) + "\\n" + MOD_AHEAD + "\\n" + MOD_AONLY[i] + "\\nCommands:\\n" +
              "\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in player_lines(m["commands"]))) if MOD_AONLY[i] else MOD_BODY[i]''')

# ================================================================================================================ Java
# ---------------------------------------------------------------------------------------------------------------- PermissionsModule token + probe
rep('''    "ATY":  "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
}''',
    '''    "ATY":  "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    # 0.3.3: settings visibility by permission - PlayerRef.hasPermission(node) IS PermissionsModule.get().hasPermission(uuid, node)
    # (HytaleServer.jar bytecode), so the UUID form is the same check the menu uses for Server Setup
    "PERM": "com.hypixel.hytale.server.core.permissions.PermissionsModule",
}''')
rep('''(T["ATY"], "STRING"), (T["CTX"], "get")):''',
    '''(T["ATY"], "STRING"), (T["CTX"], "get"),
             (T["PERM"], "get"), (T["PERM"], "hasPermission")):''')

# ---------------------------------------------------------------------------------------------------------------- SetReg: the 7th element (perm)
rep('''#   settings:fn:register  apply(Object[] { String mod, String key, String label, String category, Boolean def, String help }) -> Boolean''',
    '''#   settings:fn:register  apply(Object[] { String mod, String key, String label, String category, Boolean def, String help [, String perm] })
#                         -> Boolean. 0.3.3: the optional 7th element = a permission node: only players holding it see the row (hidden, never
#                         greyed) and may set it; null / "" / six elements = every player; any value that is not a plain node
#                         (SetReg.validPerm) REFUSES THE KEY for this run (fail closed: hidden for all, set FALSE, get = its default).
#                         Two mods on one key: the stricter wins (a node is never dropped; two different nodes refuse the key).''')
rep('''#   settings:fn:get       apply(Object[] { UUID player, String key }) -> Boolean (choice, else admin default, else registered default; null = unknown)''',
    '''#   settings:fn:get       apply(Object[] { UUID player, String key }) -> Boolean (choice, else admin default, else registered default; null = unknown;
#                         0.3.3: a refused key answers its registered default - never a stored choice)''')
rep('''#   settings:fn:set       apply(Object[] { UUID player, String key, Boolean value [, Boolean onlyIfUnset] }) -> Boolean (TRUE = stored state matches)''',
    '''#   settings:fn:set       apply(Object[] { UUID player, String key, Boolean value [, Boolean onlyIfUnset] }) -> Boolean (TRUE = stored state matches;
#                         0.3.3: FALSE for a key whose permission node the player lacks)''')
rep('''#   settings:def:<key>    the same Object[6] as register, written by every adopter at setup (drained here, so load order never matters)''',
    '''#   settings:def:<key>    the same Object[6] (or Object[7]) as register, written by every adopter at setup (drained here, so load order never matters)''')
rep("# from inside a caller's own lock is safe and no lock cycle exists. get is two ConcurrentHashMap reads + a HashMap read after the",
    "# from inside a caller's own lock is safe and no lock cycle exists. get is four ConcurrentHashMap reads + a HashMap read after the")
# review fix: REFUSED (keys refused for this run: key -> the Boolean default settings:fn:get answers) and PERM_MOD (key -> the mod whose
# node gates it, so a first mod registering again - the settings:def: drain - never drops another mod's node). Fields first (javassist).
rep('''F(sreg, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")''',
    '''F(sreg, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")
# 0.3.3 (review): keys refused for this server run (a registration with a node that is not plain, or two mods with two different nodes):
# key -> the Boolean default settings:fn:get answers. Never cleared: hidden for everyone, may() false, set refused, later registrations
# refused - load order never makes a refused key visible. PERM_MOD: key -> the mod whose node gates the key (DEFS stays Object[7]).
F(sreg, "public static final java.util.concurrent.ConcurrentHashMap REFUSED = new java.util.concurrent.ConcurrentHashMap();")
F(sreg, "public static final java.util.concurrent.ConcurrentHashMap PERM_MOD = new java.util.concurrent.ConcurrentHashMap();")''')
rep('''# idempotent: the same mod registering again updates label / help / tab; a different mod registering the same key (shared keys such as
# rewards.late) is accepted and the FIRST registration is kept - one warning if the defaults differ
M(sreg, r"""
public static synchronized boolean register(Object o) {''',
    '''# 0.3.3 (review): a permission node of a registration (element 7) must be PLAIN - the menu's own node pattern
# ^[a-z][a-z0-9]*(\\.[a-z0-9]+)+$ (ADMIN_NODE / MENU_CFG_NODE), 3-100 characters: no leading "-" (the engine's personal-deny syntax would
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
public static synchronized boolean register(Object o) {''')
rep('''    Boolean def = a[4] instanceof Boolean ? (Boolean) a[4] : Boolean.TRUE;
    String help = a.length > 5 ? clip(a[5], 100) : "";
    Object[] old = (Object[]) DEFS.get(key);
    if (old != null && !mod.equals(old[0])) {
      if (!def.equals(old[4]) && WARNED.putIfAbsent(key, Boolean.TRUE) == null)
        @PKG@.MenuUtil.warn("setting " + key + ": " + mod + " wants default " + def + ", " + old[0] + " registered " + old[4] + " first - keeping " + old[4]);
      return true;
    }
    DEFS.put(key, new Object[] { mod, key, label, cat, def, help });
    return true;''',
    '''    Boolean def = a[4] instanceof Boolean ? (Boolean) a[4] : Boolean.TRUE;
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
    return true;''')
# 0.3.3 (review): info() never asks the bridge again for a refused key
rep('''  Object[] d = (Object[]) DEFS.get(key);
  if (d == null) {
    Object v = @PKG@.MenuUtil.bridge().get("settings:def:" + key);
    if (v != null && register(v)) d = (Object[]) DEFS.get(key);''',
    '''  Object[] d = (Object[]) DEFS.get(key);
  if (d == null && !REFUSED.containsKey(key)) {
    Object v = @PKG@.MenuUtil.bridge().get("settings:def:" + key);
    if (v != null && register(v)) d = (Object[]) DEFS.get(key);''')
# SetReg.may / allowed / visible (after info + keysOf: javassist compiles callees first)
rep('''M(sreg, r"""
public static Boolean def(String key) {''',
    '''# 0.3.3: may the player change (and so see) this switch? No node = yes. The node check = PermissionsModule.get().hasPermission(uuid, node),
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
public static Boolean def(String key) {''')
rep('''  java.util.Collections.sort(rows);
  String[] out = new String[rows.size()];
  for (int i = 0; i < out.length; i++) { String s = (String) rows.get(i); out[i] = s.substring(s.indexOf('\\t') + 1); }
  return out;
}""")
# 0.3: ADMIN is replaced wholesale''',
    '''  java.util.Collections.sort(rows);
  String[] out = new String[rows.size()];
  for (int i = 0; i < out.length; i++) { String s = (String) rows.get(i); out[i] = s.substring(s.indexOf('\\t') + 1); }
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
# 0.3: ADMIN is replaced wholesale''')

# ---------------------------------------------------------------------------------------------------------------- SetStore.get: a refused key answers its default
# review fix: settings:fn:get (and the page) of a REFUSED key = its registered default - never a choice stored before or around the
# refusal, never null, so every caller's notifyOn / gate stays on its safe TRUE / FALSE path
rep('''public static Boolean get(java.util.UUID u, String key) {
  if (u == null || key == null) return null;
  Boolean o = own(u, key);''',
    '''public static Boolean get(java.util.UUID u, String key) {
  if (u == null || key == null) return null;
  Boolean rd = @PKG@.SetReg.refusedDef(key);
  if (rd != null) return rd;
  Boolean o = own(u, key);''')

# ---------------------------------------------------------------------------------------------------------------- SetStore: Reset all keeps choices the player may not change
rep('''M(sst, r"""
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
    int r = resetMem(k);''',
    '''# 0.3.3: keep = the keys whose own choice stays (switches the player may not change - Reset all only resets rows they can change); the
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
    int r = resetMem(k, keep);''')

# ---------------------------------------------------------------------------------------------------------------- settings:fn:set refuses a key the player may not change
rep('''    boolean only = a.length > 3 && Boolean.TRUE.equals(a[3]);
    return @PKG@.SetStore.set(u, key, ((Boolean) a[2]).booleanValue(), only) == 1 ? Boolean.TRUE : Boolean.FALSE;''',
    '''    if (!@PKG@.SetReg.may(u, key)) return Boolean.FALSE;      // 0.3.3: the player lacks the switch's permission node
    boolean only = a.length > 3 && Boolean.TRUE.equals(a[3]);
    return @PKG@.SetStore.set(u, key, ((Boolean) a[2]).booleanValue(), only) == 1 ? Boolean.TRUE : Boolean.FALSE;''')

# ---------------------------------------------------------------------------------------------------------------- MenuPage.openSettings comment
rep('''# 0.2: the torch (slot 51) opens the Settings page straight from the menu''',
    '''# 0.2: the torch (slot 51; 0.3.3: slot 39) opens the Settings page straight from the menu''')

# ---------------------------------------------------------------------------------------------------------------- SettingsPage: visible rows only, empty tabs not drawn
rep('''# Rows = the REGISTERED keys of the tab (SetReg.keysOf), sorted by SET_ORDER. Labels / help lines of other mods only go through b.set.''',
    '''# Rows = the REGISTERED keys of the tab (SetReg.keysOf), sorted by SET_ORDER. Labels / help lines of other mods only go through b.set.
# 0.3.3: only the rows this player may change (SetReg.visible - a registration's permission node); the others are hidden, never greyed.
# Paging and the header count visible rows; a tab with no visible row is not drawn (the tab buttons close up, same ids and styles).''')
rep('''M(spg, r"""
public int firstTab() {
  for (int i = 0; i < @PKG@.MenuData.SET_CAT_ID.length; i++) if (@PKG@.SetReg.keysOf(i).length > 0) return i;
  return 0;
}""")
''', "")
rep('''  java.util.UUID u = this.playerRef.getUuid();
  int nCat = @PKG@.MenuData.SET_CAT_ID.length;
  if (this.cat < 0) this.cat = firstTab();
  if (this.cat >= nCat) this.cat = 0;
  String[] keys = @PKG@.SetReg.keysOf(this.cat);''',
    '''  java.util.UUID u = this.playerRef.getUuid();
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
  String[] keys = (String[]) vis[this.cat];''')
rep('''  for (int i = 0; i < nCat; i++) {
    String par = i < 4 ? "#SkyyStgTabs0" : "#SkyyStgTabs1";
    if (i % 4 != 0) b.appendInline(par, @PKG@.MenuData.UI_SSP12);
    b.appendInline(par, i == this.cat ? @PKG@.MenuData.UI_STABSEL[i] : @PKG@.MenuData.UI_STAB[i]);
    ev.addEventBinding(@BT@.Activating, "#SkyyStgTab" + i, @EVD@.of("a", "stab" + i));
  }''',
    '''  int shown = 0;
  for (int i = 0; i < nCat; i++) {
    if (((String[]) vis[i]).length == 0) continue;
    String par = shown < 4 ? "#SkyyStgTabs0" : "#SkyyStgTabs1";
    if (shown % 4 != 0) b.appendInline(par, @PKG@.MenuData.UI_SSP12);
    b.appendInline(par, i == this.cat ? @PKG@.MenuData.UI_STABSEL[i] : @PKG@.MenuData.UI_STAB[i]);
    ev.addEventBinding(@BT@.Activating, "#SkyyStgTab" + i, @EVD@.of("a", "stab" + i));
    shown++;
  }''')
rep('''      String key = this.rowKeys[r];
      if (key == null) { rebuild(); return; }
      int ok = @PKG@.SetStore.set(u, key, hitOn, false);''',
    '''      String key = this.rowKeys[r];
      if (key == null) { rebuild(); return; }
      if (!@PKG@.SetReg.may(u, key)) { this.status = @PKG@.MenuData.SET_TXT_GONE; rebuild(); return; }
      int ok = @PKG@.SetStore.set(u, key, hitOn, false);''')

# ---------------------------------------------------------------------------------------------------------------- done
for _must in ('VERSION = "0.3.3"', '"cmdc:identify"', '("main", 39, "Furniture_Crude_Torch"', '"mod": "SkyyGear"', '"party.invites"',
              '"tpa.requests"', '"msg.private"', '"skills.overallUp"', '"gear.notices"', "public static String[] visible(int cat",
              "SetReg.may(u, key)", "ROUND_RETIRED = {", "KEEP=10,",
              # review fixes
              "public static Boolean refusedDef(String key)", "public static void refuse(String key, Boolean def, String why)",
              "if (refusedDef(key) != null) return false;", "Boolean rd = @PKG@.SetReg.refusedDef(key);", "PERM_MOD.put(key, mod);",
              "for c in player_lines(m[\"commands\"])", "for c in admin_lines(m)", "/rank set <player> <rank> | clear <player> - (admin)",
              "_NODE_RE.match(_perm)"):
    assert _must in s, "missing after patch: " + _must
for _gone in ('"mod": "SkyyRolls"', "firstTab()", '("main", 51, "Furniture_Crude_Torch"', "page (type it twice)",
              '"/rank set | clear <player>', "c == '_' || c == '-' || c == ':'", 'WARNED.putIfAbsent("perm:"'):
    assert _gone not in s, "still there after patch: " + _gone
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
