"""Derive SkyyMenu/build_skyymenu_0.3.py from SkyyMenu 0.2 (python tools/menu_0_3_patch.py, then build the result).
Edit THIS patch, never the generated build script.

0.3 = the admin Mods section ("Server Setup"), exactly per research/Server-Setup-Spec.md section 2 (who sees it, entry points, the
page and its seven views, mods not updated yet, inline strings + build checks), with section 9's defaults (Skyy has not answered yet):
 - WHO: node skyymenu.modconfig (ops have it through hytale:Admin's built-in "*"). Every build() and every click first runs the ONE
   gate AdminPage.guard() (re-reads playerRef.hasPermission): on a no it drops pending + drafts, shows the red line "You no longer have
   access to Server Setup." and the page draws only that line and Close; only Close still works. A build check proves the order (the
   guard is the first statement of build() and comes before the first action comparison in handleDataEvent) and a crafted bad source
   must fail that check. Changing a mod also needs THAT mod's own node: the mod re-checks it on every write (tools/CONFIG-CONTRACT.md);
   a viewer without it sees the mod's page read-only ("View only - changing SkyyBank needs skyybank.admin.").
 - ENTRY POINTS: a "Server Setup" book (Deco_Book_Pile_Large) at main-menu slot 41, right of Mods; players never see it (skipped, not
   greyed). In the Mods view an admin's click on a mod that publishes config:def:<Mod> opens that mod's page ("Click to set up this mod");
   players keep the commands info box. /modconfig (alias /serversetup, requirePermission skyymenu.modconfig - the project's admin-command
   rule, see DEVIATIONS) and the usage variant /modconfig <mod> (case-insensitive, Skyy prefix optional: /modconfig menu, or the page
   title). The first PlayerReadyEvent logs whether /modconfig and /serversetup really answer with SkyyMenu.
 - THE PAGE (AdminPage, one inline page 1120 x 930, ids SkyyAdm..., views switched with rebuild(); no timers, no periodic updates,
   no MouseEntered/Exited bindings, never closes before opening another page, Esc closes):
     list    every installed Skyy mod: mods with config first (n settings, "k wait for a restart", Parts ON/OFF, Editors), the red state
             when a file cannot be read or a save failed, "Not running", "Needs a newer SkyyMenu"; then every other installed mod as
             FILE ONLY with its config path and its reload command or note (spec 2.11) and a Reload button when that command exists.
             Search box (>= 2 letters; mod names, titles, tab labels, every row label + help; mods not set up are matched by name only):
             line 2 lists the hits, Open lands on the first hit's tab + page and marks hit rows with ">". Footer: Prev/Next, Changes,
             Export all, Refresh, < SkyWynn Menu, Close. Day one reads "1 mod is set up for in-game editing - the rest show their file."
     mod     a set-up mod: tabs (8 per row, up to 16), header, 7 rows per page (label + unit + tag LIVE/RESTART/NEW ONLY/CONFIRM/PART,
             "*" while a typed draft differs, ">" on search hits; the full help line under it), widgets per type: bool ON/OFF, int/dec/
             text/range/color TextField + Set (+ - / + with step=), choice <= 4 buttons else < value >, items "Edit - n items", table
             "Open - n entries", link "Open" (runs the command as the admin; its editor page replaces this one), action button, ro value;
             Default on every changeable row. Every button carries every visible TextField (drafts survive any click); Enter = that
             row's Set. Footer: Prev/Next, History, Export / Import, Reload file, Advanced ON/OFF, < Mods, Close.
             A FILE-ONLY mod opens the same view as an info page: its config file(s), how to reload them, its admin commands, [Reload].
     table   a table row's entries (keys/tset/add/remove) with a filter box, 1-3 value columns, Set, Remove (always confirmed), an add
             row (typed key and/or "Add held item" per the table's add mode); an items row uses the same view on a list kept in the
             page (Set amount, Remove, Add, Add held item) saved with ONE set of the whole list (Save list / Undo edits).
     confirm the mod's question ("Change X from A to B?") or SkyyMenu's own (every remove, undo, import apply, restore apply) with
             Confirm (red) / Cancel; Cancel, Esc or any other click drops it; no timer.
     log     Changes: the log op of every set-up mod (40 newest each), newest first, 10 per page, tabs All + one per mod; labels and
             units from the schema; table lines read "Bazaar products: Ore_Iron  added  Ores / 12.5 / Iron Ore"; Undo on status=ok lines
             (inverse op, confirmed; "Changed again since - open the mod to edit it." when the value moved on).
     hist    History of one mod: versions newest first, 8 per page (4 + the preview box while a preview is shown), a file tab row when
             the mod has several files; Preview (restore preview, 12 lines + "and n more") and Restore (confirmed, names the file and
             says what stays).
     io      Export / Import: the export code in a box (scope changed, "Everything" switches to all) and the same text saved to
             Skyy_SkyyMenu/exports/<Mod>-<yyyyMMdd-HHmm>.txt (written on the scheduler, never on the world thread); import box ->
             Preview -> Apply (confirmed); every .txt in Skyy_SkyyMenu/imports/ listed with its own Preview. From the list, Export all /
             import all: one code per mod (all-<stamp>.txt), previews mod by mod, applies mod by mod.
 - SKYYMENU'S OWN CONFIG through tools/skyycfg.py (spec 4.7; config:def:SkyyMenu + config:fn:SkyyMenu on the bridge, node skyymenu.admin):
     menu.giveItem         bool  config.properties giveItem   give the menu item on the first join (/skymenu still gives a lost one)
     menu.modsHelp         bool  config.properties modsHelp   players see the Mods tile (admins always do)
     menu.tooltipsDefault  bool  settings-defaults.properties menu.tooltips (custom: the same line as the table entry below)
     settings.defaults     table every known + registered player switch, value on / off / unset, writes settings-defaults.properties
                                 (custom: so every switch is listed, also the ones with no line yet; fixed entry set = no Add/Remove)
   New file Skyy_SkyyMenu/config.properties (written once when missing, read by MenuCfg.load = the kit's RELOAD). The 0.2 settings
   registry now takes in-game edits at once (SetReg.adminPut) and its 30 s re-read of settings-defaults.properties waits 5 s after an
   in-game edit so it cannot read the file between the edit and the kit's save (SetReg.adminSwap, one lock).
 - Everything 0.2 does is kept (Settings page, registry, /settings, the torch, the tooltip migration, Auction House entry).

LEFT OUT (and why)
 - The spec's setPermissionGroups(new String[0]) on /modconfig: HANDOFF command rule 1 says never on admin commands (requirePermission
   only), and every other Skyy admin command follows that rule.
 - "Later: warp locks" in SkyyMenu's own config (spec 4.7 marks them later; they need SkyyRanks / the warps editor).
 - The color widget (spec: reserved for v2) - a color row shows a TextField like text.
 - Restoring the settings.defaults table from History: the kit cannot restore custom tables (tools/CONFIG-CONTRACT.md known limits);
   the restore preview lists it under "Not restored". Export / import of it works.
 - Hand edits of settings-defaults.properties are applied by the 0.2 30-second re-read, not logged via=file (custom rows only log their
   own file key; the kit merges the rest silently).

DEVIATIONS (small, UX or rule-driven)
 - Mod rows are two lines: label + widget + Default on top, the full help line (up to 100 characters) across the whole row below, so a
   help line is never cut (the spec's 470 px text column could show about 55 of its 100 characters).
 - Buttons whose text comes from a mod (tab labels, choice labels, action text, file names) use inline text reduced to letters, digits,
   space and < > / - (the characters proven inline); every Label text from a mod goes through b.set.
 - A file-only mod's row has Open (its info page: files, reload, admin commands) plus Reload when a reload command exists.
 - "Advanced ON/OFF" without a colon, and the step buttons read "Less" / "More" instead of - / + ("+" is not in the proven inline set).
 - The row tag (LIVE, CONFIRM, ...) sits after the label when both fit the 556 px label; a long label moves the tag to the front of
   the help line instead of cutting it. Table entries of settings.defaults show the switch's label (the key when not registered).

REVIEW FIXES (after the first build; compiled + linted, not harness-run again)
 - Less / More step from the typed box when there is one (the draft), like Set; a mod that does not answer its get shows "That mod did
   not answer" instead of "not a number"; a box that is not a number says so ("The value in the box is not a number").
 - <Mod> names read off the bridge must match the kit's MOD_RE (AdminPage.validMod inside hdr(), so cfgMods / resolveMod / modFor /
   every draw skip a bogus config:def:<x> key); AdmSaveTask only writes exports/<plain file name> that resolves directly inside
   Skyy_SkyyMenu/exports/ (the readImport rule on the write side).
 - A link row always rebuilds with "Ran /<cmd> - if no page opens, the answer is in your chat." (handleCommand runs the command later on
   the common pool, so the page cannot know whether it opens a page; the command's page, when it opens one, replaces this page - the
   pattern the main menu's page commands use).
 - The empty-tab hint says "switch Advanced to ON (footer button)"; the tooltip default row's help names the table entry by its shown
   label, and SkyyMenu's defaults table subtitle says the Menu hover tooltips entry is that same line.
 - The first boot logs "config kit folder: <world>/mods/Skyy_SkyyMenu (config-history, config-changes.log)", or warns when the kit's
   folder differs from Skyy_SkyyMenu or its parent is not mods/.

TESTED (bare JVM, scratch harness, deleted afterwards): all 46 classes (SkyyMenu 0.3 + a kit-built sample mod) load under -Xverify:all;
every view rendered with the real UICommandBuilder / UIEventBuilder and every inline string, id, parent, set target, event binding and
footer width checked; clicks driven through handleDataEvent for every widget and view (part OFF confirm / ON no confirm, danger int
confirm, drafts across clicks, bad value kept, range, Default, Less/More, choice buttons + cycling, Advanced, restart amber, items list
edit + Save list / Undo edits, table add / set / remove with confirm + filter, action with confirm, link, read-only, Reload file after a
hand edit, History tabs / preview / restore, Export (file written) / Import preview / apply / file / tampered code, Export all + import
all preview, Changes + Undo + "Changed again since", SkyyMenu's own rows writing config.properties and settings-defaults.properties,
the 5 s re-read wait, view only, not running, newer contract, file-only page, the locked page (only Close works), /modconfig name
resolution). The engine seams (guard, alive, canEdit, heldItem, runLine, closeNow, openMenu, rebuild) were swapped for test copies.

ROUND-3 CROSS-CHECK (2026-09-25: SkyyMenu 0.3 + SkyyRanks 0.1 + every other jar pinned in tools/deploy_set.py SET in one -Xverify:all JVM,
the REAL jars in their own class loaders, the real CommandManager / HytalePermissionsProvider / PermissionQuery semantics):
 - The Mods text + file-only rows of the two mods whose pinned versions moved on after 0.1.3 wrote them: SkyyEssentials 0.1.2 (/trade in
   the player list - /tpaccept and /tpdeny share a line to stay at 8 - and its /tradeadmin reload now gets the Reload button; the old
   row said "No reload command"; /tradeadmin config and log|return on its info page) and SkyyExploration 0.2 (discovery spots, island
   checklists, the /exploreadmin page, /exploreadmin set|get, "/explore quiet ... (also in /settings)" - 0.2 flips explore.chunkXp).
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.2.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.py")
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
rep('"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF + '0.2:   the player Settings page',
    '"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF +
    "0.3:   Server Setup, the admin Mods section (research/Server-Setup-Spec.md section 2): a book at menu slot 41 and /modconfig" + LF +
    "       (alias /serversetup, node skyymenu.modconfig) open one 1120 x 930 page with seven views - the mod list (every installed Skyy" + LF +
    "       mod; mods on the config registry first, the rest file only with their path and reload command; search), a mod's settings" + LF +
    "       (tabs, a widget per type, Default, drafts), table / list editor, confirm, Changes (log + undo), History (preview + restore)," + LF +
    "       Export / Import (codes + files). One guard() re-checks the node first in every build and click. SkyyMenu's own settings" + LF +
    "       (menu item, Mods tile, tooltip default, player settings defaults table) go through tools/skyycfg.py. Notes: tools/menu_0_3_patch.py." + LF +
    "0.2:   the player Settings page")
rep('VERSION = "0.2"', 'VERSION = "0.3"')
rep("#           settings  open the player Settings page (0.2, same as /settings)",
    "#           settings  open the player Settings page (0.2, same as /settings)" + LF +
    "#           admin  open Server Setup (0.3; only admins see this entry - players never do)")

# ---------------------------------------------------------------------------------------------------------------- entries
rep(LF.join([
    '    ("main", 40, "Furniture_Ancient_Bookshelf", "Mods",',
    '        ["Every SkyWynn mod on the server, what it does and all of its commands."], "Click to open!", "view:mods"),']),
    LF.join([
    '    ("main", 40, "Furniture_Ancient_Bookshelf", "Mods",',
    '        ["Every SkyWynn mod on the server, what it does and all of its commands."], "Click to open!", "view:mods"),',
    "    # 0.3: Server Setup right of Mods (research/Server-Setup-Spec.md 2.2) - drawn ONLY for players with skyymenu.modconfig",
    '    ("main", 41, "Deco_Book_Pile_Large", "Server Setup",',
    '        ["Change every Skyy mod\'s settings in game - only admins see this.",',
    '         "Every change is saved to the mod\'s own file, logged and can be undone.",',
    '         "Command: /modconfig (or /serversetup)"], "Click to open!", "admin"),']))

# ---------------------------------------------------------------------------------------------------------------- Mods list: SkyyMenu + config/reload fields
rep(LF.join([
    '     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item",',
    '                  "/settings (or /skysettings) - turn chat messages on or off"]},']),
    LF.join([
    '     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item",',
    '                  "/settings (or /skysettings) - turn chat messages on or off",',
    '                  "/modconfig (or /serversetup) - (admin) change every mod\'s settings in game"]},']))
rep("your party and guild, your settings and this list of mods.\",",
    "your party and guild, your settings, this list of mods and Server Setup for admins.\",")
# round-3 cross-check: the Mods text of the two mods whose pinned versions (tools/deploy_set.py SET) moved on after 0.1.3 wrote their
# entries - SkyyEssentials 0.1.2 (/trade, /tradeadmin config|log|return|reload) and SkyyExploration 0.2 (discovery spots, island
# checklists, the /exploreadmin page, /exploreadmin set|get, /explore quiet now flips the explore.chunkXp switch of /settings)
rep(LF.join([
    '    {"mod": "SkyyExploration", "version": "0.1", "icon": "Furniture_Human_Ruins_Chest_Small", "check": "explore",',
    '     "desc": "Exploration: loot chests out in the world, uncover the map, discover zones and earn titles - all of it pays Exploration XP.",',
    '     "commands": ["/explore (or /exploration, /discoveries) - your exploration page",',
    '                  "/explore quiet - hide the chunk XP chat line", "/title (or /titles) - your titles",',
    '                  "/title <name> or /title off - wear a title or none",',
    '                  "/exploreadmin reload|stats|resetme - (admin)"]},']),
    LF.join([
    '    {"mod": "SkyyExploration", "version": "0.2", "icon": "Furniture_Human_Ruins_Chest_Small", "check": "explore",',
    '     "desc": "Exploration: loot chests out in the world, uncover the map, discover zones, find discovery spots and finish each island\'s checklist - all of it pays Exploration XP and earns titles.",',
    '     "commands": ["/explore (or /exploration, /discoveries) - your exploration page",',
    '                  "/explore quiet - hide the chunk XP chat line (also in /settings)", "/title (or /titles) - your titles",',
    '                  "/title <name> or /title off - wear a title or none",',
    '                  "/exploreadmin - (admin) place discovery spots, edit island checklists",',
    '                  "/exploreadmin reload|stats|resetme - (admin)"]},']))
rep(LF.join([
    '    {"mod": "SkyyEssentials", "version": "0.1.1", "icon": "Tool_Map", "check": "tpa",',
    '     "desc": "Everyday commands the base game is missing: teleport requests between players and private messages.",',
    '     "commands": ["/tpa <player> - ask to teleport to a player", "/tpahere <player> - ask a player to teleport to you",',
    '                  "/tpaccept [player] - accept a teleport request", "/tpdeny [player] - deny a teleport request",',
    '                  "/tpacancel - cancel your requests", "/msg <player> <message> (or /tell, /w) - private message",',
    '                  "/reply <message> (or /r) - answer your last message", "/fly - (staff) toggle flight"]},']),
    LF.join([
    '    {"mod": "SkyyEssentials", "version": "0.1.2", "icon": "Tool_Map", "check": "tpa",',
    '     "desc": "Everyday commands the base game is missing: teleport requests between players, private messages and safe trades of items and coins.",',
    '     "commands": ["/tpa <player> - ask to teleport to a player", "/tpahere <player> - ask a player to teleport to you",',
    '                  "/tpaccept | /tpdeny [player] - answer a teleport request", "/tpacancel - cancel your requests",',
    '                  "/msg <player> <message> (or /tell, /w) - private message", "/reply <message> (or /r) - answer your last message",',
    '                  "/trade <player> | claim - trade items and coins safely", "/fly - (staff) toggle flight"]},']))
# spec 2.11: the file a server owner edits while the mod is not on the config registry yet, the command that re-reads it, a note, and
# admin commands the Mods text does not list. Used only while the mod publishes no config:def:<Mod>.
MOD_SETUP = [
    ("SkyyMenu", "Skyy_SkyyMenu/config.properties,Skyy_SkyyMenu/settings-defaults.properties", "", "Set up in game - Server Setup, Menu.", []),
    ("SkyyProfiles", "Skyy_SkyyProfiles/config.properties", "profileadmin reload", "", []),
    ("SkyyIslands", "Skyy_SkyyIslands/config.properties", "island reload", "",
     ["/island reload - (admin) re-read config.properties and every island file", "/sethub - (admin) set the hub where you stand"]),
    ("SkyySacks", "Skyy_SkyySacks/config.properties", "", "It is read again by itself within about 10 seconds.", []),
    ("SkyyAccessories", "", "", "No server settings in this version.", []),
    ("SkyyHud", "", "", "No server settings - every player sets up their own HUD with /skyyhud.", []),
    ("SkyySkills", "Skyy_SkyySkills/xp.properties", "skills reload", "", []),
    ("SkyyTrees", "Skyy_SkyyTrees/trees.properties", "tree reload", "", []),
    ("SkyyCollections", "Skyy_SkyyCollections/collections.properties,Skyy_SkyyCollections/rewards.properties,Skyy_SkyyCollections/config.properties",
     "collections reload", "", []),
    ("SkyyCooking", "Skyy_SkyyCooking/cooking.properties", "cookadmin reload", "", []),
    ("SkyyExploration", "Skyy_SkyyExploration/config.properties", "exploreadmin reload",
     "Any key also in game: /exploreadmin set. titles.chatPriority needs a restart.",
     ["/exploreadmin set <key> <value> | get <key> - (admin) change or read any config key"]),
    ("SkyyClasses", "Skyy_SkyyClasses/config.properties", "classadmin reload", "", []),
    ("SkyyBazaar", "Skyy_SkyyBazaar/products.properties,Skyy_SkyyBazaar/market.properties", "bazaaradmin reload", "", []),
    ("SkyyAuctions", "Skyy_SkyyAuctions/config.properties,Skyy_Market/blocked.txt", "ahadmin reload", "", []),
    ("SkyyBank", "Skyy_SkyyBank/config.properties", "", "Change the interest in chat with /bankconfig - saved at once.", []),
    ("SkyyCoins", "Skyy_SkyyCoins/config.properties", "", "Change the death penalty in chat with /deathpenalty - saved at once.", []),
    ("SkyyVault", "Skyy_SkyyVault/config.properties", "vaultadmin reload", "", []),
    ("SkyyParty", "Skyy_SkyyParty/config.properties", "", "No reload command - restart the server after editing.", []),
    ("SkyyGuilds", "Skyy_SkyyGuilds/config.properties", "guildadmin reload", "",
     ["/guildadmin reload - (admin) re-read config.properties", "/guildadmin xp <amount> <guild> - (admin) test guild XP"]),
    ("SkyyEssentials", "Skyy_SkyyEssentials/config.properties", "tradeadmin reload",
     "Or change every key in game on /tradeadmin config. replyShortcut needs a restart.",
     ["/tradeadmin config - (admin) every setting of config.properties on one page",
      "/tradeadmin log [player] | return <player> - (admin) the trade log, end a trade and give items back"]),
    ("SkyyRolls", "Skyy_SkyyRolls/reforge.properties", "", "It is read again by itself whenever someone opens /reforge.", []),
]
for _m, _cfg, _rl, _note, _adm in MOD_SETUP:
    _pat = '    {"mod": "%s", ' % _m
    assert s.count(_pat) == 1, "MODS entry not found once: " + _m
    _i = s.index(_pat)
    _j = s.index(LF, _i) + 1
    _extra = '     "config": "%s", "reload": "%s", "note": "%s",' % (_cfg, _rl, _note)
    if _adm:
        _extra += LF + '     "admin": [' + ", ".join('"%s"' % a for a in _adm) + '],'
    s = s[:_j] + _extra + LF + s[_j:]

# ---------------------------------------------------------------------------------------------------------------- Server Setup data (MENU DATA)
ADMIN_DATA = r'''
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
'''
rep(LF.join([
    '# =====================================================================================================================',
    '# ==============================================  end of MENU DATA  ===================================================']),
    ADMIN_DATA.lstrip(LF) + LF.join([
    '# =====================================================================================================================',
    '# ==============================================  end of MENU DATA  ===================================================']))

# ---------------------------------------------------------------------------------------------------------------- build-time checks
rep('    assert act in ("profile", "spawn", "info", "tips", "settings") or act.split(":", 1)[0] in ("view", "cmd", "cmdc"), "bad action " + act',
    '    assert act in ("profile", "spawn", "info", "tips", "settings", "admin") or act.split(":", 1)[0] in ("view", "cmd", "cmdc"), "bad action " + act')
ADMIN_CHECKS = r'''assert "@" not in SET_TEMPLATE
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
'''
rep('assert "@" not in SET_TEMPLATE' + LF, ADMIN_CHECKS)

# vanilla + Skyy scan for /modconfig and /serversetup (spec 2.2 build check)
rep(LF.join([
    '                if "skysettings" in _cp:',
    '                    VANILLA_SKYSETTINGS.append(n)']),
    LF.join([
    '                if "skysettings" in _cp:',
    '                    VANILLA_SKYSETTINGS.append(n)',
    '                if "modconfig" in _cp or "serversetup" in _cp:',
    '                    VANILLA_ADMINW.append(n)']))
rep('TAKEN = set()' + LF + 'VANILLA_SKYSETTINGS = []' + LF,
    'TAKEN = set()' + LF + 'VANILLA_SKYSETTINGS = []' + LF + 'VANILLA_ADMINW = []' + LF)
rep('print("settings command: /settings /skysettings (taken elsewhere: %s)" % (SET_TAKEN or "none"))' + LF,
    'print("settings command: /settings /skysettings (taken elsewhere: %s)" % (SET_TAKEN or "none"))' + LF + r'''# 0.3: /modconfig + /serversetup (spec 2.2): no vanilla class and no other Skyy build script may know either word
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
''')

# ---------------------------------------------------------------------------------------------------------------- inline UI: Server Setup page
ADMIN_UI = r'''assert 25 + 150 + 150 + 300 + 220 + 170 + 4 * 10 <= SPW - 40 and 185 + 300 + 220 + 170 + 2 * 10 <= SPW - 40, "the settings footer is wider than the page"

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
'''
rep('assert 25 + 150 + 150 + 300 + 220 + 170 + 4 * 10 <= SPW - 40 and 185 + 300 + 220 + 170 + 2 * 10 <= SPW - 40, "the settings footer is wider than the page"' + LF,
    ADMIN_UI)

# ---------------------------------------------------------------------------------------------------------------- tokens, probes, the kit import
rep('    "PKG":  "com.skyy.menu",' + LF,
    '    "PKG":  "com.skyy.menu",' + LF +
    '    "MD":   "com.skyy.menu.MenuData",' + LF +
    '    "MU":   "com.skyy.menu.MenuUtil",' + LF +
    '    "RA":   "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",' + LF +
    '    "ATY":  "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",' + LF)
rep('             (T["PRE"], "getPlayerRef"), (T["PDE"], "getPlayerRef"), (T["HSV"], "SCHEDULED_EXECUTOR"), (T["CTX"], "provided")):',
    '             (T["PRE"], "getPlayerRef"), (T["PDE"], "getPlayerRef"), (T["HSV"], "SCHEDULED_EXECUTOR"), (T["CTX"], "provided"),' + LF +
    '             (T["BT"], "Validating"), (T["INV"], "getItemInHand"), (T["EVD"], "append"), (T["ACM"], "requirePermission"),' + LF +
    '             (T["ACM"], "addUsageVariant"), (T["ACM"], "withRequiredArg"), (T["ATY"], "STRING"), (T["CTX"], "get")):')
rep('import skyybuild as B' + LF, 'import skyybuild as B' + LF + 'import skyycfg as CFG        # 0.3: the admin config kit (SkyyMenu\'s own settings, research/Server-Setup-Spec.md 1.4)' + LF)

# ---------------------------------------------------------------------------------------------------------------- classes
rep('giv  = mk("Given")' + LF, 'giv  = mk("Given")' + LF + 'mcfg = mk("MenuCfg")' + LF)
rep('ssf  = mk("SetSetFn")' + LF, 'ssf  = mk("SetSetFn")' + LF + 'sdc  = mk("SetDefCfg")' + LF)
rep('spg  = mk("SettingsPage", T["PAGE"])' + LF, 'spg  = mk("SettingsPage", T["PAGE"])' + LF + 'apg  = mk("AdminPage", T["PAGE"])' + LF + 'ast  = mk("AdmSaveTask")' + LF)
rep('scmd = mk("SettingsCmd", T["APC"])' + LF, 'scmd = mk("SettingsCmd", T["APC"])' + LF + 'acmv = mk("AdminModCmd", T["APC"])' + LF + 'acmd = mk("AdminCmd", T["APC"])' + LF)

# ---------------------------------------------------------------------------------------------------------------- MenuData: Server Setup fields
rep('for _n, _v in UI_SARR.items():' + LF + '    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))' + LF,
    'for _n, _v in UI_SARR.items():' + LF + '    F(dat, "public static final String[] UI_%s = %s;" % (_n, jarr(_v)))' + LF + r'''# 0.3 Server Setup data + page strings
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
''')

# ---------------------------------------------------------------------------------------------------------------- MenuUtil: admin check, text helpers, /modconfig check
rep("# version of a loaded Skyy mod read from its manifest",
    r'''# 0.3: is this player allowed into Server Setup (skyymenu.modconfig; false on any error)
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
# version of a loaded Skyy mod read from its manifest''')

# ---------------------------------------------------------------------------------------------------------------- MenuCfg + the kit (SkyyMenu's own admin config)
MENUCFG = r'''# ================= 0.3 MenuCfg: SkyyMenu's own server settings (Skyy_SkyyMenu/config.properties), bound to the config kit =================
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

'''
rep('# ================= 0.2 Settings registry (research/Settings-Spec.md 1.2-1.5) =================' + LF,
    MENUCFG + '# ================= 0.2 Settings registry (research/Settings-Spec.md 1.2-1.5) =================' + LF)

# ---------------------------------------------------------------------------------------------------------------- SetReg: in-game edits of the defaults file
rep('F(sreg, "public static volatile long ADMIN_MTIME = -1L;")' + LF,
    'F(sreg, "public static volatile long ADMIN_MTIME = -1L;")' + LF +
    '# 0.3: time of the last in-game edit of settings-defaults.properties (Server Setup -> Menu); the 30 s re-read waits 5 s after one' + LF +
    'F(sreg, "public static volatile long EDIT_AT = 0L;")' + LF)
rep('# settings-defaults.properties: written as a commented template when missing (first = setup), re-read when lastModified changes' + LF,
    r'''# 0.3: ADMIN is replaced wholesale under ONE lock by both writers: the file re-read (adminSwap, refused for 5 s after an in-game edit so
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
''')
rep(LF.join([
    '    ADMIN = nx;',
    '    ADMIN_MTIME = mt;']),
    LF.join([
    '    if (!adminSwap(nx, first)) return;',
    '    ADMIN_MTIME = mt;']))

# ---------------------------------------------------------------------------------------------------------------- SetDefCfg: the kit hooks for the defaults file
SETDEF = r'''# ================= 0.3 SetDefCfg: kit hooks (custom: bindings) for Skyy_SkyyMenu/settings-defaults.properties =================
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

'''
rep('# ================= MenuPage (inline page; views switched with rebuild()) =================' + LF,
    SETDEF + '# ================= MenuPage (inline page; views switched with rebuild()) =================' + LF)

# ---------------------------------------------------------------------------------------------------------------- AdminPage fields + constructor, AdmSaveTask
ADMIN_CTOR = r'''# 0.3 AdminPage fields + constructor right here too (MenuPage.openAdmin and the page's "< SkyWynn Menu" button use each other's
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
'''
rep('# public wrapper so RefreshTask (another class) can rebuild - CustomUIPage.rebuild() is protected' + LF,
    ADMIN_CTOR + '# public wrapper so RefreshTask (another class) can rebuild - CustomUIPage.rebuild() is protected' + LF)

# ---------------------------------------------------------------------------------------------------------------- MenuPage: the book, Mods tiles, Mods help switch
rep(LF.join([
    'public void fillStatic(java.util.ArrayList slots) {',
    '  java.util.UUID me = this.playerRef.getUuid();',
    '  for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {',
    '    if (!@PKG@.MenuData.E_VIEW[i].equals(this.view)) continue;',
    '    String act = @PKG@.MenuData.E_ACT[i];']),
    LF.join([
    'public void fillStatic(java.util.ArrayList slots) {',
    '  java.util.UUID me = this.playerRef.getUuid();',
    '  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);',
    '  for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {',
    '    if (!@PKG@.MenuData.E_VIEW[i].equals(this.view)) continue;',
    '    String act = @PKG@.MenuData.E_ACT[i];',
    '    if ("admin".equals(act) && !admin) continue;',
    '    if ("view:mods".equals(act) && !admin && !@PKG@.MenuCfg.MODS_HELP) continue;']))
rep(LF.join([
    '    String ver = live != null ? live : @PKG@.MenuData.MOD_VER[k];',
    '    put(slots, @PKG@.MenuData.MOD_SLOTS[i], @PKG@.MenuData.MOD_ICON[k],',
    '        @PKG@.MenuData.MOD_NAME[k] + " " + ver + (installed ? "" : " (not installed)"), @PKG@.MenuUtil.modBody(k),',
    '        installed ? "Click to show the commands below" : "Not installed on this server", "mod:" + k, !installed);']),
    LF.join([
    '    String ver = live != null ? live : @PKG@.MenuData.MOD_VER[k];',
    '    boolean cfg = admin && installed && @PKG@.MenuUtil.bridge().get("config:def:" + @PKG@.MenuData.MOD_NAME[k]) instanceof Object[];',
    '    put(slots, @PKG@.MenuData.MOD_SLOTS[i], @PKG@.MenuData.MOD_ICON[k],',
    '        @PKG@.MenuData.MOD_NAME[k] + " " + ver + (installed ? "" : " (not installed)"), @PKG@.MenuUtil.modBody(k),',
    '        installed ? (cfg ? "Click to set up this mod" : "Click to show the commands below") : "Not installed on this server",',
    '        cfg ? "modcfg:" + k : "mod:" + k, !installed);']))
rep(LF.join([
    'public void fillMods(java.util.ArrayList slots) {',
    '  int per = @PKG@.MenuData.MOD_SLOTS.length;']),
    LF.join([
    'public void fillMods(java.util.ArrayList slots) {',
    '  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);',
    '  int per = @PKG@.MenuData.MOD_SLOTS.length;']))
rep(LF.join([
    'M(page, r"""',
    'public void click(@REF@ ref, @ST@ st, int idx, String act) {']),
    r'''# 0.3: the book (slot 41) and an admin's click on a set-up mod open Server Setup straight from the menu (never closing first); the grid
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
public void click(@REF@ ref, @ST@ st, int idx, String act) {''')
rep('  if (act.equals("settings")) { openSettings(ref, st); return; }' + LF,
    '  if (act.equals("settings")) { openSettings(ref, st); return; }' + LF +
    '  if (act.equals("admin")) { openAdmin(ref, st, null); return; }' + LF +
    '  if (act.startsWith("modcfg:")) {' + LF +
    '    int mk = -1;' + LF +
    '    try { mk = Integer.parseInt(act.substring(7)); } catch (Throwable t) { mk = -1; }' + LF +
    '    if (mk >= 0 && mk < @PKG@.MenuData.MOD_NAME.length) { openAdmin(ref, st, @PKG@.MenuData.MOD_NAME[mk]); return; }' + LF +
    '  }' + LF)

# ---------------------------------------------------------------------------------------------------------------- AdminPage methods (part 1: seams + helpers)
ADMIN_PAGE_1 = r'''# ================= 0.3 AdminPage (research/Server-Setup-Spec.md 2.3-2.10): Server Setup, one inline page, seven views =================
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

'''

# ---------------------------------------------------------------------------------------------------------------- AdminPage methods (part 2: the views)
ADMIN_PAGE_2 = r'''# ---- view list (spec 2.4): mods on the registry first (summary or the red state), then every other installed mod as file only
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

'''

# ---------------------------------------------------------------------------------------------------------------- AdminPage methods (part 3: build + clicks)
# The two sources the guard-order build check reads (spec 2.3 / 2.12) are Python constants so the check sees exactly what is compiled.
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
ADMIN_PAGE_3 = r'''# ---- clicks: results, drafts, one handler per view
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

'''
# the guard-order build check (spec 2.3 / 2.12 / 8.1.4) goes into the build script right after the two sources it reads, with a
# must-fail self-test; the same two constants are what M(apg, ...) compiles
GUARD_CHECK = r'''
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

'''
assert '"""' not in ADM_BUILD and '"""' not in ADM_HDE
ADM_SRC_DEFS = ('# the two AdminPage methods the guard-order check reads (compiled below with M(apg, ADM_BUILD) / M(apg, ADM_HDE))' + LF +
                'ADM_BUILD = r"""' + ADM_BUILD + '"""' + LF + 'ADM_HDE = r"""' + ADM_HDE + '"""' + LF)
rep('# ================= MenuPageFactory (right-click on the menu item -> OpenCustomUI "SkyyMenu") =================',
    ADMIN_PAGE_1 + ADMIN_PAGE_2 + ADM_SRC_DEFS + GUARD_CHECK.lstrip(LF) + ADMIN_PAGE_3 +
    '# ================= MenuPageFactory (right-click on the menu item -> OpenCustomUI "SkyyMenu") =================')

# ---------------------------------------------------------------------------------------------------------------- MenuReady, GrantTask
rep('    if (@PKG@.MenuUtil.firstCheck()) { @PKG@.MenuUtil.checkAliases(); @PKG@.MenuUtil.checkSettingsCmd(); }',
    '    if (@PKG@.MenuUtil.firstCheck()) { @PKG@.MenuUtil.checkAliases(); @PKG@.MenuUtil.checkSettingsCmd(); @PKG@.MenuUtil.checkAdminCmd(); }')
# menu.giveItem OFF (Server Setup - Menu): no item at the first join; the session guard is set so it is not re-tried on every world
# switch. /skymenu still hands a lost item back (a player asking for it).
rep(LF.join([
    'public int grantNow(java.util.UUID u) {',
    '  if (@PKG@.Given.SESSION.containsKey(u)) return 1;']),
    LF.join([
    'public int grantNow(java.util.UUID u) {',
    '  if (@PKG@.Given.SESSION.containsKey(u)) return 1;',
    '  if (!@PKG@.MenuCfg.GIVE_ITEM) { @PKG@.Given.SESSION.put(u, Boolean.TRUE); return 1; }']))

# ---------------------------------------------------------------------------------------------------------------- plugin
rep(LF.join([
    '  @PKG@.SetReg.ADMIN_FILE = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("settings-defaults.properties");',
    '  @PKG@.SetReg.loadAdmin(true);']),
    LF.join([
    '  @PKG@.SetReg.ADMIN_FILE = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("settings-defaults.properties");',
    '  @PKG@.SetReg.loadAdmin(true);',
    '  @PKG@.MenuCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("config.properties");',
    '  @PKG@.MenuCfg.init();',
    '  @PKG@.AdmSaveTask.BASE = getDataDirectory().resolveSibling("Skyy_SkyyMenu");',
    '  @PKG@.AdmSaveTask.ensureDirs();']))
rep(LF.join([
    '  @PKG@.SetReg.registerOwn();',
    '  @PKG@.SetReg.drain();']),
    LF.join([
    '  @PKG@.SetReg.registerOwn();',
    '  @PKG@.SetReg.drain();',
    '  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());',
    # the first adopter proves the kit's folder on the first boot: <world>/mods/Skyy_SkyyMenu, the same folder resolveSibling gives
    # (disk evidence: an old versioned data dir "Skyy_0.1 SkyyCoins" sits next to Skyy_SkyyCoins in mods/, so getParent() = mods/)
    '  try {',
    '    java.nio.file.Path kh = @PKG@.CfgRows.HOME == null ? null : @PKG@.CfgRows.HOME.toAbsolutePath().normalize();',
    '    java.nio.file.Path kb = @PKG@.AdmSaveTask.BASE == null ? null : @PKG@.AdmSaveTask.BASE.toAbsolutePath().normalize();',
    '    java.nio.file.Path km = @PKG@.CfgRows.MODS == null ? null : @PKG@.CfgRows.MODS.getFileName();',
    '    if (kh != null && kh.equals(kb) && km != null && "mods".equalsIgnoreCase(km.toString())) @PKG@.MenuUtil.info("config kit folder: " + kh + " (config-history, config-changes.log)");',
    '    else @PKG@.MenuUtil.warn("config kit folder is " + kh + " but SkyyMenu uses " + kb + " - the kit\'s mods folder is wrong, tell the developer");',
    '  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not check the config kit folder: " + t); }']))
rep('  getCommandRegistry().registerCommand(new @PKG@.SettingsCmd());' + LF,
    '  getCommandRegistry().registerCommand(new @PKG@.SettingsCmd());' + LF +
    '  getCommandRegistry().registerCommand(new @PKG@.AdminCmd());' + LF)
rep(r''' switch(es) registered so far");''',
    r''' switch(es) registered so far; Server Setup: /modconfig (/serversetup) for admins");''')
rep('  try { @PKG@.SetStore.flushAll(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings flush at shutdown failed: " + t); }' + LF,
    '  try { @PKG@.SetStore.flushAll(); } catch (Throwable t) { @PKG@.MenuUtil.warn("settings flush at shutdown failed: " + t); }' + LF +
    '  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { @PKG@.MenuUtil.warn("config kit flush at shutdown failed: " + t); }' + LF)

# ---------------------------------------------------------------------------------------------------------------- write list + post-build checks
rep('WRITE = (dat, utl, giv, sreg, sst, ssv, tip, sld, sgf, srf, ssf, page, spg, ref_, clo_, fac, cmd, scmd, grt, rdy, seen, quit_, pl)',
    'WRITE = (dat, utl, giv, mcfg, sreg, sst, ssv, tip, sld, sgf, srf, ssf, sdc, page, spg, apg, ast, ref_, clo_, fac, cmd, scmd, acmv, acmd, grt, rdy, seen, quit_, pl)')
rep(LF.join([
    'for c in MADE:',
    '    _cf = os.path.join(OUT, *str(c.getName()).split(".")) + ".class"',
    '    assert os.path.isfile(_cf), "class file not written: " + _cf',
    'print("classes written:", len(WRITE))']),
    LF.join([
    '# 0.3: the config kit checks its hooks (SetDefCfg, MenuCfg.load) and writes its 7 classes',
    'KIT.write(OUT)',
    'for c in list(MADE) + list(KIT.classes):',
    '    _cf = os.path.join(OUT, *str(c.getName()).split(".")) + ".class"',
    '    assert os.path.isfile(_cf), "class file not written: " + _cf',
    'print("classes written:", len(WRITE), "+ config kit", len(KIT.classes))']))
rep(LF.join([
    'for s in list(UI.values()) + UI_INFO + SET_UI_ALL:',
    '    assert s in _consts, "inline UI string missing from MenuData.class: " + s[:80]',
    'print("inline UI strings verified in MenuData.class:", len(UI) + len(UI_INFO) + len(SET_UI_ALL))']),
    LF.join([
    'for s in list(UI.values()) + UI_INFO + SET_UI_ALL + ADM_UI_ALL:',
    '    assert s in _consts, "inline UI string missing from MenuData.class: " + s[:80]',
    'print("inline UI strings verified in MenuData.class:", len(UI) + len(UI_INFO) + len(SET_UI_ALL) + len(ADM_UI_ALL))',
    'print("server setup: node %s, /%s /%s, SkyyMenu config rows: %s" % (ADMIN_NODE, ADMIN_CMD, ADMIN_ALIAS, ", ".join(r[0] for r in MENU_CFG_ROWS)))']))

# manifest description
rep("a list of every mod with its commands, and /settings (every mod's chat messages on or off, per player). Zero dependencies.",
    "a list of every mod with its commands, /settings (every mod's chat messages on or off, per player) and Server Setup for admins (/modconfig: every Skyy mod's settings in game). Zero dependencies.")

assert "@ADM" not in s and "Tips.OFF" not in s
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
