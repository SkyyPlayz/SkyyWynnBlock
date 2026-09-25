"""Derive SkyyMenu/build_skyymenu_0.2.py from the live 0.1.3 (python tools/menu_0_2_patch.py, then build the result).
Edit THIS patch, never the generated build script.

0.2 = the player Settings page, exactly per research/Settings-Spec.md sections 1.2-1.5 (bridge contract, internals, failure modes),
2 (tabs + switches) and 4 (page, /settings, menu icon, build checks):
 - REGISTRY on the skyy.bridge map (never removed; java.lang types only, every mod has its own classloader):
     settings:fn:register  apply(Object[] { String mod, String key, String label, String category, Boolean def, String help }) -> Boolean
     settings:fn:get       apply(Object[] { UUID player, String key }) -> Boolean: the player's choice, else the admin default, else the
                           registered default; null = unknown key (lock-free after the player's first read)
     settings:fn:set       apply(Object[] { UUID player, String key, Boolean value [, Boolean onlyIfUnset] }) -> Boolean (TRUE = the stored
                           state now matches the request; FALSE = could not be saved / bad args)
     settings:def:<key>    the same Object[6], written by every adopter at setup: drained right after the functions are put, again
                           each time a Settings page is OPENED (its first build only - a click never rescans the whole shared
                           bridge map, which also holds every player's coins:/skill:/bank:... keys), and looked up lazily by get
                           for an unknown key -> plugin load order never matters.
   Classes (javassist order, no forward references): SetReg (DEFS / WARNED / ADMIN / ADMIN_FILE / ADMIN_MTIME), SetStore (per-player
   maps, copy-on-write), SetSaveTask, SetStore (cont.), Tips (rewritten on the registry), SetLoadTask (preload + tooltip migration),
   SetGetFn / SetRegFn / SetSetFn, SettingsPage (fields + constructor right after the MenuPage constructor), SettingsCmd.
 - STORAGE: <world>/mods/Skyy_SkyyMenu/settings/<uuid>.properties, per PLAYER (same on every profile; PROFILES-CONTRACT rule 6). Only
   changed switches are written, keys sorted, header + _v=1 + _name. A change is in memory at once and saved 500 ms later on
   HytaleServer.SCHEDULED_EXECUTOR through MenuUtil.atomicWrite (SkyyProfiles' ProfCfg.atomicWrite verbatim: tmp, fsync, ATOMIC_MOVE +
   REPLACE_EXISTING, plain-replace fallback, 5 x 20 ms retries). A failed save stays dirty: retried by SeenTick every 30 s and by
   shutdown(). An UNREADABLE file is never overwritten: get = defaults, set = FALSE, the page shows a red line, read again every 30 s.
   SeenTick drops cached maps of offline players that are not dirty, so a hand edit made while offline is read at the next join.
   LOCKS (build-review fix): SetStore.class guards MEMORY ONLY (setMem / resetMem / pruneOffline: a few map operations). A player's file
   read (load) and write (saveNow: fsync + up to 5 x 20 ms retries) run under that player's lock stripe (one of 64 ReentrantLocks by
   uuid hash) and never under SetStore.class, so a click or a settings:fn:set on a world thread never waits for anybody's disk write.
   The stripe keeps one player's reads / writes in order (the newest map always lands last, one .tmp writer at a time); SeenTick only
   drops a cached map when it gets the stripe with tryLock (never while that file is being read or written) and it is not dirty.
   set/resetAll mark DIRTY inside the same SetStore.class step that publishes the new map, so a drop can never lose a change.
 - ADMIN DEFAULTS (server backbone): Skyy_SkyyMenu/settings-defaults.properties. Missing at start -> a commented template is written
   (one "#key=true" line per known key, grouped by tab). Re-read by SeenTick when its lastModified changes; a bad line is logged and
   ignored. A player's own choice always wins; "Reset all to defaults" returns a player to these admin defaults. (The in-game editor
   for this file is SkyyMenu 0.3's settings.defaults table, research/Server-Setup-Spec.md 4.7.)
 - PAGE (SettingsPage, 1120 x 930 inline, ids SkyyStg...): gold accent, title, hint, 8 tabs in two rows of 4 (Skills, Collections,
   Sacks, Combat, Coins, Profiles, Cooking, General), header "<tab header> - N settings", up to 7 rows per page (label + help line,
   ON / OFF buttons; the active one green / red), the tab's "Always shown" line, a status line, footer [< Prev] [Next >] (only with more
   than one page), [Reset all to defaults] (first click arms it red for 10 s, the second click resets EVERY tab; any other click
   disarms - no timer), [< SkyWynn Menu] (opens the menu straight from the page, never closing first), [Close]. Rows exist only for
   REGISTERED keys; a tab with none says so. Labels / help lines from other mods only ever go through b.set. No MouseEntered/Exited
   bindings, no periodic updates; a change made elsewhere shows at the next click.
 - /settings (alias /skysettings; setPermissionGroups hytale:Adventurer, no arguments) + a Furniture_Crude_Torch "Settings" entry at
   main-menu slot 51 (the spec default: SkyBlock's Redstone Torch spot next to Close). The first PlayerReadyEvent logs a warning when
   another mod answers /settings (duplicate command names are silently last-wins).
 - SkyyMenu's OWN switch: menu.tooltips ("Menu hover tooltips", General tab, default ON) registered at setup like any adopter. The
   0.1.3 Hover Tooltips book (slot 8) now reads and writes that same key, so the book and the Settings row are one switch.
   PRELOAD: PlayerReadyEvent fires on every world switch, so SetLoadTask is scheduled only while it still has work (the player's map
   is not loaded yet, or the notips state below is unknown / not moved yet); a normal world switch schedules nothing.
   MIGRATION: 0.1.3 kept "tooltips off" as Skyy_SkyyMenu/notips/<uuid>.txt. At the next join the preload task moves it: set
   menu.tooltips=false with onlyIfUnset (a choice already made wins), save synchronously, and only once that file is on disk delete
   the old notips file. Until then the menu treats an existing notips file as OFF, so nothing flips back on in between. Admins can
   make tooltips default OFF server-wide with "menu.tooltips=false" in settings-defaults.properties.
   (The other migrations of the spec - /skills quiet, /tree quiet - live in SkyySkills / SkyyTrees and use settings:fn:set with
   onlyIfUnset; SkyyMenu only provides the registry for them.)
 - Auction House entry (main slot 24, next to the Bazaar; Reforge moves 24 -> 25): cmdc:ah = SkyyAuctions 0.1's /ah page (aliases
   /auction, /auctionhouse), greyed "(not installed)" while /ah does not exist, like every entry. Icon Ingredient_Bar_Gold (gold for
   trading; item + icon picture checked in Assets.zip at build time). SkyyAuctions added to the Mods list (21 mods = one page).

LEFT OUT ON PURPOSE
 - The three REFUSING General switches party.invites, tpa.requests, msg.private: Skyy has not answered refuse-vs-hide (Settings-Spec
   section 6). Not in SET_ORDER, not in the defaults template, not mentioned on the page. If a mod registers them later they simply
   appear (sorted after the known keys of their tab).
 - The "(also in /settings)" wording on the /skills quiet and /tree quiet Mods-list lines (spec 4.1): the live SkyySkills 0.4.2 /
   SkyyTrees 0.2.1 do not use the registry yet, so that text would be false until they adopt it.
 - Link rows, /settings <key> on|off, sound switches (spec section 6 "Later").

DEVIATIONS (small, UX)
 - The General header reads "General (menu, party, teleports, messages)" because SkyyMenu's own row lives there.
 - The menu torch and /settings open the FIRST TAB THAT HAS ROWS (the spec opens tab 0), so an empty Skills tab never greets anyone.
   With the live 20-mod set (SkyyExploration 0.1, SkyySkills 0.4.2, ... none on the registry) the only row is SkyyMenu's own switch in
   General and the page opens there. SkyyExploration 0.2 (built by another workflow, not pinned yet) DOES adopt the registry: it
   registers explore.chunkXp + explore.finds (Skills tab) and flips explore.chunkXp from /explore quiet through settings:fn:set - with
   it installed the page opens on Skills (2 rows) and General keeps its 1 row.
 - settings:def:* is drained when a Settings page OPENS (its first build), not on every build as spec 1.2 says: every click rebuilt
   the page and rescanned the whole shared bridge map (which grows with players x mods). Load order still never matters (setup drain,
   page-open drain, lazy lookup in get); a def key written while a page is open shows the next time a page is opened.
 - SetStore.load / set / resetAll are no longer synchronized methods as spec 1.4 lists them: file I/O moved off SetStore.class onto
   per-player lock stripes (see LOCKS above), so spec guarantee 2 ("only around its own file I/O") is now "never during file I/O".
 - "Reset all to defaults" is in the footer of every tab and resets EVERY tab (spec 4.2/4.4; the label says "all" and the armed
   status line says "reset EVERY tab"). A per-tab reset is not in the spec - a later idea for Skyy, not built.
 - Before the menu hands over to the Settings page it empties its grid once (MenuPage.clearGrid), the 0.1.3 stuck-tooltip rule for every
   hand-off to another page. The update is acknowledged like any other (PageManager bytecode: updateCustomPage +1 ack per packet, the
   client answers in order), so it cannot cause the 0.1.2 "Loading..." problem.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.1.3.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.2.py")
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
rep('"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF + '0.1.3: new entries',
    '"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF +
    "0.2:   the player Settings page (research/Settings-Spec.md): a settings registry on the skyy.bridge map (settings:fn:register / get /" + LF +
    "       set; settings:def:<key> drained at start and at every page open), per-player files Skyy_SkyyMenu/settings/<uuid>.properties" + LF +
    "       (saved 500 ms after a change, atomic writes, never overwritten when unreadable), server-wide defaults in" + LF +
    "       settings-defaults.properties (commented template written once, re-read within 30 s), /settings (alias /skysettings) and a torch" + LF +
    "       at menu slot 51 opening a 1120 x 930 page: 8 tabs, ON/OFF rows, Reset all (two clicks), < SkyWynn Menu, Close. SkyyMenu's own" + LF +
    "       switch menu.tooltips = the 0.1.3 Hover Tooltips book (0.1.3 notips/<uuid>.txt files move into it at the next join). New" + LF +
    "       Auction House entry (/ah, SkyyAuctions) + SkyyAuctions in the Mods list. Notes: tools/menu_0_2_patch.py." + LF +
    "0.1.3: new entries")
rep('VERSION = "0.1.3"', 'VERSION = "0.2"')
rep("#           spawn  teleport to the main world spawn                       tips   switch this player's hover tooltips on / off",
    "#           spawn  teleport to the main world spawn                       tips   switch this player's hover tooltips on / off" + LF +
    "#           settings  open the player Settings page (0.2, same as /settings)")
rep(r'''MENU_ITEM_DESC = ("Right-click to open the SkyWynn Menu: teleports, your island menu, bags, vault, the HUD editor, skills, the bazaar, "
                  "the bank, reforging, your party and guild, and a list of every mod with its commands.\\n\\nLost it? Type /skymenu to get a new one.")''',
    r'''MENU_ITEM_DESC = ("Right-click to open the SkyWynn Menu: teleports, your island menu, bags, vault, the HUD editor, skills, the bazaar, "
                  "the auction house, the bank, reforging, your party and guild, your settings and a list of every mod with its commands."
                  "\\n\\nLost it? Type /skymenu to get a new one.")''')

# ---------------------------------------------------------------------------------------------------------------- entries
rep(LF.join([
    '        ["Switch the pop-up text of this menu on or off (saved for you).",',
    '         "Off: nothing pops up when you hover an item. Click an item to use it",',
    '         "and read what it does in this box."], "Click to switch", "tips"),']),
    LF.join([
    '        ["Switch the pop-up text of this menu on or off (saved for you).",',
    '         "Off: nothing pops up when you hover an item. Click an item to use it",',
    '         "and read what it does in this box.",',
    '         "The same switch is in Settings (/settings, General tab)."], "Click to switch", "tips"),']))
rep(LF.join([
    '    ("main", 24, "Tool_Hammer_Iron", "Reforge",',
    '        ["Put in a weapon, armor piece or tool and pay coins to reroll its stats.", "Command: /reforge"], "Click to open!", "cmdc:reforge"),']),
    LF.join([
    '    # 0.2: the Auction House (SkyyAuctions 0.1, /ah) sits next to the Bazaar; Reforge moved one slot right',
    '    ("main", 24, "Ingredient_Bar_Gold", "Auction House",',
    '        ["Buy items other players listed and sell your own for a fixed price (Buy It Now).",',
    '         "Claim the coins and items you are owed on the Manage page.",',
    '         "Command: /ah (or /auction, /auctionhouse)"], "Click to open!", "cmdc:ah"),',
    '    ("main", 25, "Tool_Hammer_Iron", "Reforge",',
    '        ["Put in a weapon, armor piece or tool and pay coins to reroll its stats.", "Command: /reforge"], "Click to open!", "cmdc:reforge"),']))
rep(LF.join([
    '    ("main", 40, "Furniture_Ancient_Bookshelf", "Mods",',
    '        ["Every SkyWynn mod on the server, what it does and all of its commands."], "Click to open!", "view:mods"),']),
    LF.join([
    '    ("main", 40, "Furniture_Ancient_Bookshelf", "Mods",',
    '        ["Every SkyWynn mod on the server, what it does and all of its commands."], "Click to open!", "view:mods"),',
    "    # 0.2: Settings in the bottom row next to Close (SkyBlock's Redstone Torch spot, research/Settings-Spec.md 4.1)",
    '    ("main", 51, "Furniture_Crude_Torch", "Settings",',
    '        ["Turn chat messages on or off - one switch per message, for every mod.",',
    '         "Your settings are the same on every profile.", "Command: /settings (or /skysettings)"], "Click to open!", "settings"),']))

# ---------------------------------------------------------------------------------------------------------------- settings data (MENU DATA)
SETTINGS_DATA = r'''
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
'''
rep(LF.join([
    '# =====================================================================================================================',
    '# ==============================================  end of MENU DATA  ===================================================']),
    SETTINGS_DATA.lstrip(LF) + LF.join([
    '# =====================================================================================================================',
    '# ==============================================  end of MENU DATA  ===================================================']))

# ---------------------------------------------------------------------------------------------------------------- Mods list
rep(LF.join([
    '     "desc": "The all-in-one SkyWynn menu: teleports, your island menu, Pocket Dimension, Vault, Accessory Bag, the HUD editor, crafting, skills, collections, the bazaar, the bank, reforging, players, your party and guild, and this list of mods.",',
    '     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item"]},']),
    LF.join([
    '     "desc": "The all-in-one SkyWynn menu: teleports, your island menu, Pocket Dimension, Vault, Accessory Bag, the HUD editor, crafting, skills, collections, the bazaar, the auction house, the bank, reforging, players, your party and guild, your settings and this list of mods.",',
    '     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item",',
    '                  "/settings (or /skysettings) - turn chat messages on or off"]},']))
rep(LF.join([
    '                  "/bazaaradmin reload - (admin) re-read the product list"]},']),
    LF.join([
    '                  "/bazaaradmin reload - (admin) re-read the product list"]},',
    '    {"mod": "SkyyAuctions", "version": "0.1", "icon": "Ingredient_Bar_Gold", "check": "ah",',
    '     "desc": "A Hypixel-style Auction House (Buy It Now): list an item for a fixed price, buy what other players list and claim the coins and items you are owed.",',
    '     "commands": ["/ah (or /auction, /auctionhouse) - open the Auction House",',
    '                  "/ah sell <price> [duration] - sell the item in your hand",',
    '                  "/ah claim - claim your coins and items", "/ah manage - your listings and claims",',
    '                  "/ah search <words> - search the listings",',
    '                  "/ahadmin list|info|remove|reload|pause|resume - (admin)"]},']))

# ---------------------------------------------------------------------------------------------------------------- build-time checks
rep('    assert act in ("profile", "spawn", "info", "tips") or act.split(":", 1)[0] in ("view", "cmd", "cmdc"), "bad action " + act',
    '    assert act in ("profile", "spawn", "info", "tips", "settings") or act.split(":", 1)[0] in ("view", "cmd", "cmdc"), "bad action " + act')
SETTINGS_CHECKS = r'''    assert _plines, "PA_LEGACY slot %d has no text" % _slot
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
'''
rep('    assert _plines, "PA_LEGACY slot %d has no text" % _slot' + LF, SETTINGS_CHECKS)

# vanilla scan: remember whether the vanilla jar knows the word "skysettings" (it must not); "settings" itself is the vanilla
# /world settings SUBCOMMAND (WorldSettingsCommand, only WorldCommand references it - Settings-Spec 0), so a constant-pool hit on
# "settings" proves nothing and is not checked here - the plugin checks the live command map at the first PlayerReadyEvent instead
rep(LF.join([
    '            try:',
    '                TAKEN |= set(WANT) & cp_utf8(zj.read(n))',
    '            except Exception:',
    '                pass']),
    LF.join([
    '            try:',
    '                _cp = cp_utf8(zj.read(n))',
    '                TAKEN |= set(WANT) & _cp',
    '                if "skysettings" in _cp:',
    '                    VANILLA_SKYSETTINGS.append(n)',
    '            except Exception:',
    '                pass']))
rep('TAKEN = set()' + LF + 'with zipfile.ZipFile(B.SERVER_JAR) as zj:',
    'TAKEN = set()' + LF + 'VANILLA_SKYSETTINGS = []' + LF + 'with zipfile.ZipFile(B.SERVER_JAR) as zj:')
rep('ALIAS_TEXT = (" (also " + ", ".join("/" + a for a in ALIASES) + ")") if ALIASES else ""' + LF,
    'ALIAS_TEXT = (" (also " + ", ".join("/" + a for a in ALIASES) + ")") if ALIASES else ""' + LF + r'''# 0.2: /settings + /skysettings (Settings-Spec 4.1) - no other Skyy build script may take them (same takes() rule as the menu words)
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
''')

# ---------------------------------------------------------------------------------------------------------------- inline UI: Settings page
SETTINGS_UI = r'''assert "Width" in UI["ROOT"] and "Top:" not in UI["ROOT"].split("Anchor: (")[1].split(")")[0], "page root anchor must be Width/Height only"

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
'''
rep('assert "Width" in UI["ROOT"] and "Top:" not in UI["ROOT"].split("Anchor: (")[1].split(")")[0], "page root anchor must be Width/Height only"' + LF,
    SETTINGS_UI)

# ---------------------------------------------------------------------------------------------------------------- classes (every makeClass is written)
rep_block('dat  = pool.makeClass(PKG + ".MenuData")', 'pl   = pool.makeClass(PKG + ".SkyyMenuPlugin", pool.get(JP))',
          ['tip  = pool.makeClass(PKG + ".Tips")', 'tsv  = pool.makeClass(PKG + ".TipsSave")'], r'''# 0.2: every class goes through mk(), and the writeFile list below is checked against MADE (Settings-Spec 1.4: a class left out of
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
pl   = mk("SkyyMenuPlugin", JP)''')

# ---------------------------------------------------------------------------------------------------------------- MenuData: settings fields
rep('F(dat, "public static final String[] PAL_FOOT = %s;" % jarr([txt(a[4]) for a in PA_LEGACY]))' + LF,
    'F(dat, "public static final String[] PAL_FOOT = %s;" % jarr([txt(a[4]) for a in PA_LEGACY]))' + LF + r'''# 0.2 settings data + page strings
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
''')

# ---------------------------------------------------------------------------------------------------------------- MenuUtil: atomicWrite + /settings check
rep('# dynamic text (player names, warp names, world names) -> one safe line, no markup' + LF,
    r'''# 0.2 (Settings-Spec 1.4): SkyyProfiles' ProfCfg.atomicWrite verbatim - tmp file + fsync + atomic rename (a plain replace only where the
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
''')
rep("# version of a loaded Skyy mod read from its manifest",
    r'''# 0.2: once per server run (first PlayerReadyEvent, all commands registered): /settings and /skysettings must answer with OUR SettingsCmd.
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
# version of a loaded Skyy mod read from its manifest''')

# ---------------------------------------------------------------------------------------------------------------- registry + Tips (replaces the 0.1.3 Tips/TipsSave)
REGISTRY = r'''# ================= 0.2 Settings registry (research/Settings-Spec.md 1.2-1.5) =================
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

'''
rep_block('# ================= Tips (0.1.3): per-player "hover tooltips off" switch; file Skyy_SkyyMenu/notips/<uuid>.txt exists = off =================',
          '  catch (Throwable t) { write(u, off); }' + LF + '}""")' + LF,
          ['TipsSave', 'public static boolean isOff', 'public static synchronized void write'], REGISTRY)

# ---------------------------------------------------------------------------------------------------------------- SettingsPage fields + constructor
rep('# public wrapper so RefreshTask (another class) can rebuild - CustomUIPage.rebuild() is protected' + LF,
    r'''# 0.2 SettingsPage fields + constructor right here (javassist: MenuPage.openSettings and the page's "< SkyWynn Menu" button use each
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
''')

# ---------------------------------------------------------------------------------------------------------------- MenuPage: open Settings + the book on the registry
rep('M(page, r"""' + LF + 'public void click(@REF@ ref, @ST@ st, int idx, String act) {',
    r'''# 0.2: the torch (slot 51) opens the Settings page straight from the menu - never closing first (the 0.1.2 rule). The grid is emptied
# once before the hand-off (the 0.1.3 stuck-tooltip rule for every page hand-off; an update is acknowledged like any other).
M(page, r"""
public void openSettings(@REF@ ref, @ST@ st) {
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  clearGrid();
  p.getPageManager().openCustomPage(ref, st, new @PKG@.SettingsPage(this.playerRef, -1));
}""")
M(page, r"""
public void click(@REF@ ref, @ST@ st, int idx, String act) {''')
rep(LF.join([
    '    open("player");',
    '    rebuild();',
    '    return;',
    '  }',
    '  this.infoName = this.names[idx];']),
    LF.join([
    '    open("player");',
    '    rebuild();',
    '    return;',
    '  }',
    '  if (act.equals("settings")) { openSettings(ref, st); return; }',
    '  this.infoName = this.names[idx];']))
rep(LF.join([
    '    boolean off = !@PKG@.Tips.isOff(u);',
    '    @PKG@.Tips.setOff(u, off);',
    '    this.infoName = off ? "Hover Tooltips: OFF" : "Hover Tooltips: ON";',
    '    this.status = off ? "Hover tooltips are off - click an item and read it in the box above." : "Hover tooltips are on again.";']),
    LF.join([
    '    boolean off = !@PKG@.Tips.isOff(u);',
    '    if (@PKG@.Tips.setOff(u, off) != 1) {',
    '      this.infoName = @PKG@.Tips.isOff(u) ? "Hover Tooltips: OFF" : "Hover Tooltips: ON";',
    '      this.status = @PKG@.MenuData.SET_TXT_BROKEN;',
    '      rebuild();',
    '      return;',
    '    }',
    '    this.infoName = off ? "Hover Tooltips: OFF" : "Hover Tooltips: ON";',
    '    this.status = off ? "Hover tooltips are off - click an item and read it in the box above." : "Hover tooltips are on again.";']))

# ---------------------------------------------------------------------------------------------------------------- SettingsPage methods + /settings
SETTINGS_PAGE = r'''# ================= 0.2 SettingsPage (research/Settings-Spec.md 4.2-4.4): one inline page, tabs / rows switched with rebuild() =================
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

'''
rep('# ================= MenuPageFactory (right-click on the menu item -> OpenCustomUI "SkyyMenu") =================',
    SETTINGS_PAGE + '# ================= MenuPageFactory (right-click on the menu item -> OpenCustomUI "SkyyMenu") =================')

# ---------------------------------------------------------------------------------------------------------------- MenuReady: preload + /settings check
rep('    if (@PKG@.MenuUtil.firstCheck()) @PKG@.MenuUtil.checkAliases();',
    '    if (@PKG@.MenuUtil.firstCheck()) { @PKG@.MenuUtil.checkAliases(); @PKG@.MenuUtil.checkSettingsCmd(); }')
rep(LF.join([
    '    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());',
    '    if (pr == null || @PKG@.Given.SESSION.containsKey(pr.getUuid())) return;']),
    LF.join([
    '    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());',
    '    if (pr == null) return;',
    '    @PKG@.SetLoadTask.preload(pr);',
    '    if (@PKG@.Given.SESSION.containsKey(pr.getUuid())) return;']))

# ---------------------------------------------------------------------------------------------------------------- SeenTick: settings upkeep
rep_block('M(seen, r"""' + LF + 'public void run() {', '}""")' + LF, ['@PKG@.Tips.OFF.keySet().retainAll(online);'], r'''M(seen, r"""
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
''')

# ---------------------------------------------------------------------------------------------------------------- plugin
rep(LF.join([
    '  @PKG@.Tips.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("notips");',
    '  @OCU@.registerSimple(this, @PKG@.SkyyMenuPlugin.class, @PKG@.MenuData.PAGE_ID, new @PKG@.MenuPageFactory());',
    '  getCommandRegistry().registerCommand(new @PKG@.MenuCmd());']),
    LF.join([
    '  @PKG@.Tips.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("notips");',
    '  @PKG@.SetStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("settings");',
    '  @PKG@.SetReg.ADMIN_FILE = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("settings-defaults.properties");',
    '  @PKG@.SetReg.loadAdmin(true);',
    '  java.util.Map br = @PKG@.MenuUtil.bridge();',
    '  br.put("settings:fn:register", new @PKG@.SetRegFn());',
    '  br.put("settings:fn:get", new @PKG@.SetGetFn());',
    '  br.put("settings:fn:set", new @PKG@.SetSetFn());',
    '  @PKG@.SetReg.registerOwn();',
    '  @PKG@.SetReg.drain();',
    '  @OCU@.registerSimple(this, @PKG@.SkyyMenuPlugin.class, @PKG@.MenuData.PAGE_ID, new @PKG@.MenuPageFactory());',
    '  getCommandRegistry().registerCommand(new @PKG@.MenuCmd());',
    '  getCommandRegistry().registerCommand(new @PKG@.SettingsCmd());']))
rep(r'''ready - /skymenu""" + "".join(" /" + a for a in ALIASES) + r""", right-click the SkyWynn Menu item; the item is given once per player");''',
    r'''ready - /skymenu""" + "".join(" /" + a for a in ALIASES) + r""", right-click the SkyWynn Menu item; the item is given once per player; /settings (/skysettings): " + @PKG@.SetReg.DEFS.size() + " switch(es) registered so far");''')
rep(LF.join([
    'protected void shutdown() {',
    '  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }',
    '  super.shutdown();']),
    LF.join([
    'protected void shutdown() {',
    '  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }',
    '  try { @PKG@.SetStore.flushAll(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings flush at shutdown failed: " + t); }',
    '  super.shutdown();']))

# ---------------------------------------------------------------------------------------------------------------- write list + post-build checks
rep(LF.join([
    'for c in (dat, utl, giv, tip, tsv, page, ref_, clo_, fac, cmd, grt, rdy, seen, quit_, pl):',
    '    c.writeFile(OUT)',
    'print("classes written")']),
    LF.join([
    'WRITE = (dat, utl, giv, sreg, sst, ssv, tip, sld, sgf, srf, ssf, page, spg, ref_, clo_, fac, cmd, scmd, grt, rdy, seen, quit_, pl)',
    'assert len(WRITE) == len(MADE) and all(any(c is w for w in WRITE) for c in MADE), "a pool.makeClass result is missing from the writeFile list"',
    'for c in WRITE:',
    '    c.writeFile(OUT)',
    'for c in MADE:',
    '    _cf = os.path.join(OUT, *str(c.getName()).split(".")) + ".class"',
    '    assert os.path.isfile(_cf), "class file not written: " + _cf',
    'print("classes written:", len(WRITE))']))
rep(LF.join([
    'for s in list(UI.values()) + UI_INFO:',
    '    assert s in _consts, "inline UI string missing from MenuData.class: " + s[:80]',
    'print("inline UI strings verified in MenuData.class:", len(UI) + len(UI_INFO))']),
    LF.join([
    'for s in list(UI.values()) + UI_INFO + SET_UI_ALL:',
    '    assert s in _consts, "inline UI string missing from MenuData.class: " + s[:80]',
    'print("inline UI strings verified in MenuData.class:", len(UI) + len(UI_INFO) + len(SET_UI_ALL))',
    'print("settings: %d known keys (%d tabs), own: %s, template %d bytes" % (len(SET_ORDER), len(SET_TABS), ", ".join(k[0] for k in OWN_SETTINGS), len(SET_TEMPLATE)))']))

# manifest description
rep('island menu, Pocket Dimension, Vault, Accessory Bag, HUD editor, crafting, skills, collections, bazaar, bank, reforge, players, party, guild and a list of every mod with its commands. Zero dependencies.',
    'island menu, Pocket Dimension, Vault, Accessory Bag, HUD editor, crafting, skills, collections, bazaar, auction house, bank, reforge, players, party, guild, a list of every mod with its commands, and /settings (every mod\'s chat messages on or off, per player). Zero dependencies.')

assert "tsv" not in s.split("# ================= javassist =================")[1].replace("tsv =", ""), "a TipsSave reference is left"
assert "Tips.OFF" not in s and "TipsSave" not in s.split("# ================= javassist =================")[1]
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
