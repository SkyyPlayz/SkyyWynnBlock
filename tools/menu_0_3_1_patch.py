"""Derive SkyyMenu/build_skyymenu_0.3.1.py from SkyyMenu 0.3 (python tools/menu_0_3_1_patch.py, then build the result).
Edit THIS patch, never the generated build script.

0.3.1 = SkyyMenu 0.3 brought up to the live set of 2026-09-25 04:11 (tools/deploy_set.py SET, round 4 = 16 mods adopted the admin config
kit). Everything 0.3 does is kept (Settings, registry, Server Setup with its seven views, /modconfig, the kit rows); only MENU DATA,
four small Java methods and the Settings row height change:

 1. MODS (the players' Mods view and the Server Setup file-only fallback texts) follow the live versions: Profiles 0.1.1, Islands 0.5.2,
    Sacks 0.7.6, Accessories 0.4.4, Hud 0.3.10, Skills 0.4.3, Trees 0.2.2, Collections 0.2.2, Cooking 0.1.2, Exploration 0.2.1,
    Classes 0.1.5, Vault 0.1.1, Party 0.1.4, Guilds 0.1.2, Essentials 0.1.4, Rolls 0.1.5, Auctions 0.1.1 (Bazaar / Bank / Coins were
    already live: file only until SkyyEconomy; Essentials 0.1.4 + Auctions 0.1.1 = the 2026-09-25 05:42 ItemGridSlot hotfix, same
    commands, files and Server Setup page as 0.1.3 / 0.1). The old "No server settings" notes (Accessories, Hud), Party's "No reload command" and the
    missing Accessories / Hud config files are replaced by each mod's live file(s) and reload command, and a new optional "setup" field
    (first version with a Server Setup page, the page title, what is on it) describes the page. The rule stays: the Server Setup LIST
    comes from the config:def: scan; the static fields are only the fallback for a mod that publishes no config:def. That fallback now
    says why: "Server Setup page from <since> on - <file line>" when the server runs an older version, (red) "Its Server Setup page
    did not load - see the server log." when the version should have it, or "Not running here (disabled or missing) - <file line>"
    when no enabled plugin of that name is loaded although its check command answers (no version to compare: the plugin is disabled,
    or that command is another mod's) (AdminPage.fileRow); the file-only info page ends with "Server Setup page: <title> - <what>."
    plus the same reason (AdminPage.drawFileOnly). SkyyRanks 0.1 (live since round 3, missing
    from the list) gets its entry; the Mods view shows 28 mods per page (MOD_SLOTS rows 1-4) so all 22 still fit on one page.
 2. Player switches: guild.online, guild.members, guild.chat (SkyyGuilds 0.1.2's regSetting texts, tab General, after the party rows)
    join SET_KNOWN, so SET_ORDER, the settings-defaults.properties template (written only when the file is missing - an existing file
    keeps its lines; the Server Setup defaults table lists every registered switch anyway) and the defaults table order know them.
    Compared against every regSetting call in the newest build script of every live mod: those three were the only missing keys; every
    other label / tab / help already matched. A new build-time cross-check (below the MODS checks) re-reads tools/deploy_set.py SET and
    those scripts on every build and prints "WARNING menu data: ..." for any live mod missing from MODS, a version that differs, a
    switch that is unknown or worded differently, or a Server Setup title that differs ("menu data matches the live set" when clean).
 3. Settings tabs hold 8 rows per page instead of 7 (rows 61 px + 6 px gap instead of 70 + 6, same fonts and buttons; the page stays
    1120 x 930, the parts are 923 px), so General (7 switches with the guild rows) and Skills (7) have room again - and the 0.2 paging
    (Prev / Next in the footer, "page 1 of 2" in the header, only when a tab has more rows) still takes any further switch.
 4. Admin-only lines in the Mods view: a MODS entry's "admin" list (0.3 showed it only on the Server Setup file-only page) is now also
    shown to admins (skyymenu.modconfig) in the Mods view tooltip and info box, under "Admin only:" between the description and the
    commands; players never see it (MenuUtil.modBodyFor). RULE: the "(admin)" lines that were already in a mod's "commands" list in 0.3
    stay there, shown to everyone as before (players' Mods text = 0.3's for every mod, Server-Setup-Spec 2.2 "players keep today's
    behaviour"); the "admin" list holds only the admin commands the Mods list did not show at all. So SkyySkills, Trees, Collections,
    Cooking, Classes and Rolls have no "admin" list (every admin command of theirs is already in Commands), and Profiles / Exploration /
    Vault keep their 0.3 "(admin)" Commands lines and add only the missing ones. New admin-only lines: SkyyEssentials 0.1.3 /warpadmin
    (+ /tradeadmin config, log|return), SkyyParty 0.1.4 /partyadmin, set, reload, SkyyHud 0.3.10 /skyyhud default [use | clear],
    SkyyIslands 0.5.2 /modconfig islands (starter kit from your hotbar), /island reload, /sethub; and the other admin commands the list
    was missing: /profileadmin config|set, /exploreadmin set|get, /accessories reload, /vaultadmin config|reload, /guildadmin
    config|set|reload|xp, and SkyyRanks' /rankadmin + /rank. A mod shown in its "old" wording (SkyyIslands before 0.5) gets no admin
    lines. Build checks: admin lines say (admin) or (staff) (the 0.3 check, still in force), <= 80 characters, not also a Commands
    line; an admin tooltip has <= 14 detail lines; a description is ONE line (modBodyFor puts the admin block after the first line) and
    MOD_ABODY, built from its parts, must equal what modBodyFor makes of MOD_BODY.
    Tooltips OFF: an admin's click on a set-up mod first shows its text (with the admin lines) in the info box and says "Click it again to
    open its Server Setup page."; the second click on the same tile opens it (0.3 opened it at once, so a tooltips-off admin could never
    read a set-up mod's commands). With tooltips ON (the default) the click opens Server Setup at once, exactly as in 0.3.

 5. The config kit is PINNED (review 2026-09-25): tools/skyycfg.py is emitted as it is on disk, so EXPECTED_KIT (in KIT_PIN below) names
    the kit this SkyyMenu carries - kit 1.1, the kit fix every mod picks up at its next version. The build fails when the kit on disk is
    another version (change EXPECTED_KIT on purpose, regenerate, re-test), prints "config kit <v>: tools/skyycfg.py blob <12 hex>, the
    committed file" (or "NOT the committed file" + a WARNING while the kit has uncommitted edits), repeats the blob in the "config kit:"
    summary line, stores "<v> <blob>" in MenuData.CFG_KIT - the server log's ready line reads "[SkyyMenu] 0.3.1 ready (config kit <v>
    <blob>) - ..." - and re-reads the kit file right before the jar is written: an edit that lands during the build fails it.

NOT CHANGED: no kit change (the kit is only pinned and identified), no adopter mod rebuilt or bumped, no bridge key, file, node, command
or default changed; the three refusing switches (party.invites, tpa.requests, msg.private) stay unbuilt.
KNOWN: SkyyMenu draws a kit 1.1 value= action row (Object[12]) as a plain action button and sends no value (the kit then uses the row's
default or answers bad) - a typed-value widget for those rows is the next SkyyMenu's job; no live mod publishes one yet.

TESTED (2026-09-25, bare JVM + jpype, scratch harness under tools/dev/scratch/r5/, deleted afterwards; 681 checks, 0 fails): all 36
classes of the built jar load and initialize under -Xverify:all; every live mod of tools/deploy_set.py SET is in MODS with its live
version; the 16 adopters + Menu + Ranks carry a Server Setup description, a config file and no stale note; players' Mods text = 0.3's
MOD_BODY for every mod, admins' = description + "Admin only:" + admin lines + commands (Essentials /warpadmin, Party /partyadmin,
Hud /skyyhud default, Islands /modconfig islands + /sethub + /island reload are in the admin text and never in the player text);
every info line <= 80, admin tooltips <= 14 lines; verCmp (0.3.9 < 0.3.10, 0.5 < 0.5.2, "?", null). Instrumented copies (liveVersion,
isAdmin, Tips.isOff, put, openAdmin, rebuild swapped): all 22 mods on one Mods page in the right slots, admin clicks modcfg:/mod:
with the right footers; tooltips ON one click opens Server Setup; tooltips OFF first click shows the text + "Click it again ...",
another tile re-arms, the second click on the same tile opens it; a player's click never shows admin lines; AdminPage.fileRow
(older version / did not load (red) / file-only unchanged) and drawFileOnly (page line + both reasons + reload + admin commands);
SettingsPage with the 30 live switches: General = 7 rows in SET_ORDER (party, guild x3, tpa, menu) on one page, Skills = 7, 10 General
switches = 8 rows + Prev / Next + "page 1 of 2", Next -> page 2 with the other 2 rows, a row click there saves, Prev back; unique ids,
no underscores; SetDefCfg.customKeys lists guild.online / members / chat right after party.chat. The jar's kit classes = SkyyMenu 0.3's
(kit 1.0; constant-pool diff = the version and the template's guild lines only).
RE-TESTED after the review fixes (2026-09-25, same kind of scratch harness, deleted afterwards; 306 checks, 0 fails) on the jar built
from THIS patch with kit 1.1: 36 of 36 classes load and initialize under -Xverify:all; MenuData.CFG_KIT = "1.1 <blob of the kit on
disk>" (= git hash-object tools/skyycfg.py), CfgRows.KIT = "1.1", the ready line carries it; for all 22 mods the player text = MOD_BODY
without "Admin only:" and the admin text = the one-line description + "Admin only:" + admin lines + Commands (<= 14 detail lines,
every line <= 80); verCmp (10 cases); instrumented liveVersion: fileRow for SkyyParty not running / 0.1.3 (older) / 0.1.4 and 0.1.10
(did not load, red) and SkyyBazaar (file only, unchanged with and without a live version); drawFileOnly subtitle + reason for the
same three states, page line, admin commands, file-only mod unchanged; instrumented Tips.isOff / openAdmin / rebuild: tooltips ON
one click opens, OFF first click shows the text + "Click it again ...", another tile re-arms, the second click opens, a mod: click
never opens and disarms. EXPECTED_KIT = "1.0" against the kit 1.1 on disk: the build stops at the pin with its message. Constant-pool
diff against the reviewer's 04:43 jar: AdminPage (+3 not-running texts), MenuData (+CFG_KIT), SkyyMenuPlugin (ready line), CfgFile
(the kit edit of 04:44 - the drift the pin now makes visible). NOT re-run: the Settings paging and Mods-page slot checks of the first
harness (no code of theirs changed since; the build's own layout asserts still pass).
FINAL CROSS-CHECK (2026-09-25 ~05:50, scratch harness under tools/dev/scratch/r5/, deleted afterwards; 1735 checks, 0 fails) found the
live set moved at 05:42 (hotfix SkyyEssentials 0.1.4 + SkyyAuctions 0.1.1) after the 05:32 build: MODS said 0.1.3 / 0.1 -> fixed above
(versions only), rebuilt with kit 1.1 blob d691f13c78ec. SkyyMenu 0.3.1 + the 21 other SET jars in ONE JVM (-Xverify:all, each jar in its
own URLClassLoader; 840 classes link and initialize); the engine's PermissionsModule (real HytalePermissionsProvider, its default
permissions.json, op in hytale:Admin), CommandManager (CommandManager.register) and PluginManager (manifests decoded by the engine's own
PluginManifest.CODEC) allocated without constructors; every plugin's setup() replayed from its bytecode (56 root commands, 31
regSetting calls with their constant arguments, 18 CfgPub.start) in SET order (the 6 switch mods set up before SkyyMenu reach the
registry through the settings:def drain, the 6 after it through settings:fn:register). Settings: all 30 adopter switches in their own tab with their label + help
(General 7, Skills 7, every tab one page; with 3 more General switches: 8 + 2 over two pages with Prev / Next). Server Setup list: 22
rows = 18 set up (name = running version, not red) + Coins, Bank, Bazaar, Auctions file only, 3 list pages, subtitle "18 mods are set up
..."; every set-up mod's page draws to the end on every tab and page (Advanced on) and every table view draws. Mods list: 22 = SET,
static version = SET = manifest, Server Setup title / files / since / reload + check commands match the jars (SkyyRanks 0.1 shows as
0.1.0: the engine's Semver). Non-op: guard() locked, no-access page only, isAdmin false, no admin node in hytale:Adventurer (116 nodes),
27 admin command nodes + every mod's NODE denied (op allowed), every adopter's config:fn answers denied to the non-op and to a null who
over "command" (op: ok).
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.1.py")
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


def rep_between(start, end, must_contain, new):
    """replace s[start ... end) (start included, end excluded) - both markers unique"""
    global s
    assert s.count(start) == 1, "block start not unique: " + start[:80]
    assert s.count(end) == 1, "block end not unique: " + end[:80]
    i = s.index(start)
    j = s.index(end, i)
    old = s[i:j]
    for m in must_contain:
        assert m in old, "block does not contain " + m
    s = s[:i] + new + s[j:]


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF + '0.3:   Server Setup, the admin Mods section',
    '"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF +
    "0.3.1: menu data brought up to the live set (tools/deploy_set.py SET, round 4): Mods list versions, config files, reload commands and" + LF +
    "       a description of each mod's Server Setup page (the list itself still comes from the config:def: scan); SkyyRanks in the list;" + LF +
    "       admin-only command lines for admins (Essentials /warpadmin, Party /partyadmin, Hud /skyyhud default, Islands, ...); the guild" + LF +
    "       switches in the known list and the defaults template; Settings tabs hold 8 rows per page (paging stays); a build-time" + LF +
    "       cross-check against the live scripts. Notes: tools/menu_0_3_1_patch.py." + LF +
    "0.3:   Server Setup, the admin Mods section")
rep('VERSION = "0.3"', 'VERSION = "0.3.1"')

# ---------------------------------------------------------------------------------------------------------------- the config kit is pinned
# review 2026-09-25: tools/skyycfg.py is emitted as it is on disk, so a kit revision must be picked up ON PURPOSE. EXPECTED_KIT is the kit
# this SkyyMenu carries (bump it here, deliberately, then re-test); the build fails when the kit on disk is another version, prints the
# kit's git blob id and whether it is the committed file, stores "<kit> <blob>" in MenuData.CFG_KIT (shown in the ready line of the
# server log) and re-reads the file right before the jar is written, so a kit edit landing during the build fails it.
KIT_PIN = r'''
# 0.3.1: the config kit this jar carries (tools/menu_0_3_1_patch.py pins it; see the "config kit" lines of the build output)
import hashlib, subprocess
EXPECTED_KIT = "1.1"
def kit_blob(path):
    """git blob id of the kit source (= git rev-parse HEAD:tools/skyycfg.py when the file is the committed one)"""
    d = open(path, "rb").read()
    return hashlib.sha1(("blob %d" % len(d)).encode("ascii") + b"\x00" + d).hexdigest()
KIT_FILE = os.path.abspath(CFG.__file__)
KIT_NOW = getattr(CFG, "KIT_VERSION", "1.0")      # the committed kit 1.0 has no KIT_VERSION constant
assert KIT_NOW == EXPECTED_KIT, ("tools/skyycfg.py is config kit %s, SkyyMenu %s pins kit %s - pick a kit change up on purpose: "
                                 "set EXPECTED_KIT in tools/menu_0_3_1_patch.py, regenerate, re-test" % (KIT_NOW, VERSION, EXPECTED_KIT))
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
'''
rep('HERE = os.path.dirname(os.path.abspath(__file__))' + LF,
    'HERE = os.path.dirname(os.path.abspath(__file__))' + LF + KIT_PIN)

# ---------------------------------------------------------------------------------------------------------------- Mods view: 28 per page
rep("MOD_SLOTS    = list(range(10, 17)) + list(range(19, 26)) + list(range(28, 35))                        # 21 mods per page",
    "MOD_SLOTS    = list(range(10, 17)) + list(range(19, 26)) + list(range(28, 35)) + list(range(37, 44))  # 28 mods per page (0.3.1: 22 mods)")

# ---------------------------------------------------------------------------------------------------------------- MODS (the whole list)
NEW_MODS = r'''MODS = [
    {"mod": "SkyyMenu", "version": VERSION, "icon": "Ingredient_Voidheart", "check": "skymenu",
     "config": "Skyy_SkyyMenu/config.properties,Skyy_SkyyMenu/settings-defaults.properties", "reload": "", "note": "Set up in game - Server Setup, Menu.",
     "setup": ("0.3", "Menu", "the menu item, the Mods tile, player settings defaults"),
     "desc": "The all-in-one SkyWynn menu: teleports, your island menu, Pocket Dimension, Vault, Accessory Bag, the HUD editor, crafting, skills, collections, the bazaar, the auction house, the bank, reforging, players, your party and guild, your settings, this list of mods and Server Setup for admins.",
     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item",
                  "/settings (or /skysettings) - turn chat messages on or off",
                  "/modconfig (or /serversetup) - (admin) change every mod's settings in game"]},
    {"mod": "SkyyProfiles", "version": "0.1.1", "icon": "Deco_Book_Pile_Large", "check": "profiles",
     "config": "Skyy_SkyyProfiles/config.properties", "reload": "profileadmin reload", "note": "",
     "setup": ("0.1.1", "Profiles", "profile slots (6 by default), switching, inventory"),
     "admin": ["/profileadmin config | set <setting> <value> - (admin) settings in chat"],
     "desc": "SkyBlock-style profiles: each profile is its own save with its own class, island, inventory, coins, bank, bags, skills and collections.",
     "commands": ["/profiles (or /profile) - open your profiles", "/profiles create (or new) - a new profile, pick its class",
                  "/profiles switch <number or name> - switch to another profile", "/profiles list - your profiles in chat",
                  "/profileadmin info <player> - (admin) a player's profiles",
                  "/profileadmin setclass <player> <n> <class> - (admin) fix a class",
                  "/profileadmin reload - (admin) re-read the settings"]},
    {"mod": "SkyyIslands", "version": "0.5.2", "icon": "Soil_Grass", "check": "island",
     "config": "Skyy_SkyyIslands/config.properties", "reload": "island reload", "note": "",
     "setup": ("0.5.2", "Islands", "island defaults, visitors, co-op, limits, starter kit, hub"),
     "admin": ["/modconfig islands - (admin) island defaults, starter kit from your hotbar",
               "/island reload - (admin) re-read config.properties and every island file",
               "/sethub - (admin) set the hub where you stand (also in Server Setup)"],
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
    {"mod": "SkyySacks", "version": "0.7.6", "icon": "Tool_Feedbag", "check": "sacks",
     "config": "Skyy_SkyySacks/config.properties", "reload": "", "note": "It is read again by itself within about 10 seconds.",
     "setup": ("0.7.6", "Bags and Crafting", "craft search box, bag caps, Furnace and Tannery"),
     "desc": "Magic Bags: carry a Mining, Foraging, Farming, Combat or Smithing bag and what you gather of that type goes straight into your Pocket Dimension. /craft crafts from your inventory and bags (Smithing, Farming, Furnace, Tannery and more tabs).",
     "commands": ["/sacks (or /pd, /bags) - your Pocket Dimension, missing bags show recipes",
                  "/craft (or /recipes) - craft from your inventory and bags", "/craft <words> - open crafting with a search"]},
    {"mod": "SkyyAccessories", "version": "0.4.4", "icon": "Utility_Bag_Seed", "check": "accessories",
     "config": "Skyy_SkyyAccessories/config.properties", "reload": "accessories reload", "note": "",
     "setup": ("0.4.4", "Accessories", "accessory slots, talisman bonuses, regeneration"),
     "admin": ["/accessories reload - (admin) re-read config.properties after hand edits"],
     "desc": "Your Accessory Bag: 9 slots for bench accessories (each unlocks its bench tab in /craft, the Campfire one cooks on the go) and stat talismans that work while they sit in the bag.",
     "commands": ["/accessories (or /acc, /accbag) - open your Accessory Bag"]},
    {"mod": "SkyyHud", "version": "0.3.10", "icon": "Deco_Map", "check": "skyyhud",
     "config": "Skyy_SkyyHud/config.properties", "reload": "", "note": "Hand edits are read at the next server start.",
     "setup": ("0.3.10", "HUD", "the HUD layout new players start with"),
     "admin": ["/skyyhud default - (admin) which layout new players start with",
               "/skyyhud default use | clear - (admin) set it to your layout | the built-in one"],
     "desc": "A customizable on-screen HUD: coordinates, zone, clocks, day counter, session timer, players online, coins, party and guild. Move, resize and colour every widget, save profiles or share your layout as a code.",
     "commands": ["/skyyhud (or /shud) - open the HUD editor", "/skyyhud export - print your layout as a code",
                  "/skyyhud import <code> - load a layout code", "/skyyhud reset - back to the server's default layout",
                  "/skyyhud profile save|load|delete <name> - named layouts", "/skyyhud profile list - your saved layouts"]},
    {"mod": "SkyySkills", "version": "0.4.3", "icon": "Weapon_Sword_Iron", "check": "skills",
     "config": "Skyy_SkyySkills/xp.properties", "reload": "skills reload", "note": "",
     "setup": ("0.4.3", "Skills", "levels, XP rates, perks, parts on or off"),
     "desc": "Hypixel-style skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill - that level up as you play and pay coins on every level up.",
     "commands": ["/skills (or /skill) - open your Skills", "/skills stats <skill> - the Stats page of a skill",
                  "/skills top <skill> - the top 10 players of a skill", "/skills quiet - hide the +XP chat messages",
                  "/skills reload - (admin) re-read the XP settings", "/skills xp <skill> <amount> - (admin) test XP"]},
    {"mod": "SkyyTrees", "version": "0.2.2", "icon": "Plant_Sapling_Maple", "check": "tree",
     "config": "Skyy_SkyyTrees/trees.properties", "reload": "tree reload", "note": "",
     "setup": ("0.2.2", "Trees", "node values, Dust, Tree Feller, Vein Burst"),
     "desc": "Skill trees: spend the points your skill levels earn on nodes for Mining, Foraging, Farming, Cooking, Acrobatics and Exploration.",
     "commands": ["/tree (or /trees) - open your skill trees", "/tree <skill> - open one tree, for example /tree mining",
                  "/tree quiet - hide the Tree bonus chat line", "/tree reload - (admin) re-read the tree settings"]},
    {"mod": "SkyyCollections", "version": "0.2.2", "icon": "Furniture_Village_Painting_1x1", "check": "collections",
     "config": "Skyy_SkyyCollections/config.properties,Skyy_SkyyCollections/collections.properties,Skyy_SkyyCollections/rewards.properties", "reload": "collections reload", "note": "",
     "setup": ("0.2.2", "Collections", "curves, tier rewards, coin unlocks, rules"),
     "desc": "Hypixel-style Collections: everything you gather counts toward tiers. Tiers unlock crafting recipes for the /craft page and pay rewards.",
     "commands": ["/collections (or /coll) - open your Collections", "/collections <name> - the tiers of one collection",
                  "/collections unlocks (or recipes) - the recipes you unlocked",
                  "/collections top <collection|score> - the top 10 players",
                  "/collections give <collection> <amount> - (admin) test credit",
                  "/collections reload - (admin) re-read the collection rules"]},
    {"mod": "SkyyCooking", "version": "0.1.2", "icon": "Food_Pie_Meat", "check": "cooking",
     "config": "Skyy_SkyyCooking/cooking.properties", "reload": "cookadmin reload", "note": "",
     "setup": ("0.1.2", "Cooking", "graded cooking, grades, Cooking XP, campfire, tree"),
     "desc": "Cooking: dishes you cook at a Cooking Bench get a Grade from your Cooking level and skill tree - higher Grades heal and buff more.",
     "commands": ["/cooking - your Cooking level, Grade and tree chances",
                  "/cookadmin give <dish> <grade> - (admin) test dishes",
                  "/cookadmin campfire <dish> <count> - (admin) test the Campfire cook",
                  "/cookadmin reload - (admin) re-read the cooking settings"]},
    {"mod": "SkyyExploration", "version": "0.2.1", "icon": "Furniture_Human_Ruins_Chest_Small", "check": "explore",
     "config": "Skyy_SkyyExploration/config.properties", "reload": "exploreadmin reload", "note": "Any key also in game: /exploreadmin set. titles.chatPriority needs a restart.",
     "setup": ("0.2.1", "Exploration", "XP sources, chest luck, spots, checklists, titles"),
     "admin": ["/exploreadmin set <key> <value> | get <key> - (admin) change or read a key"],
     "desc": "Exploration: loot chests out in the world, uncover the map, discover zones, find discovery spots and finish each island's checklist - all of it pays Exploration XP and earns titles.",
     "commands": ["/explore (or /exploration, /discoveries) - your exploration page",
                  "/explore quiet - hide the chunk XP chat line (also in /settings)", "/title (or /titles) - your titles",
                  "/title <name> or /title off - wear a title or none",
                  "/exploreadmin - (admin) place discovery spots, edit island checklists",
                  "/exploreadmin reload|stats|resetme - (admin)"]},
    {"mod": "SkyyClasses", "version": "0.1.5", "icon": "Weapon_Shortbow_Iron", "check": "class",
     "config": "Skyy_SkyyClasses/config.properties", "reload": "classadmin reload", "note": "",
     "setup": ("0.1.5", "Classes", "the weapon lock and the class picker"),
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
    {"mod": "SkyyAuctions", "version": "0.1.1", "icon": "Ingredient_Bar_Gold", "check": "ah",
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
    {"mod": "SkyyVault", "version": "0.1.1", "icon": "Furniture_Royal_Magic_Chest_Large", "check": "vault",
     "config": "Skyy_SkyyVault/config.properties", "reload": "vaultadmin reload", "note": "",
     "setup": ("0.1.1", "Vault", "free pages, page prices, page size, after-switch wait"),
     "admin": ["/vaultadmin config | config <key> <value> - (admin) settings in chat",
               "/vaultadmin reload - (admin) re-read config.properties"],
     "desc": "Your Vault: item storage shared by every profile you have, so you can move items from one profile to another. Buy more pages with coins.",
     "commands": ["/vault - open your Vault", "/vault <page> - open one vault page", "/vault buy - buy the next page (type it twice)",
                  "/vault info - your pages, slots used and the next price",
                  "/vaultadmin open|info|setpages <player> - (admin)"]},
    {"mod": "SkyyParty", "version": "0.1.4", "icon": "Deco_Scroll", "check": "party",
     "config": "Skyy_SkyyParty/config.properties", "reload": "partyadmin reload", "note": "",
     "setup": ("0.1.4", "Party", "the largest party and how long an invite lasts"),
     "admin": ["/partyadmin - (admin) the party settings and how to change them",
               "/partyadmin set <maxSize|inviteSeconds> <value> - (admin) change one",
               "/partyadmin reload - (admin) re-read config.properties"],
     "desc": "Team up with friends: invite players to a party, chat privately and see your party on the HUD. The lead passes on if the leader leaves.",
     "commands": ["/party (or /p) - open the party page", "/party invite <player> - invite a player",
                  "/party accept | decline - answer an invite", "/party leave - leave your party", "/party list - list your party",
                  "/party kick | promote <player> - (leader)", "/party disband - (leader) end the party", "/pc <message> - chat with your party"]},
    {"mod": "SkyyGuilds", "version": "0.1.2", "icon": "Furniture_Outlander_Banner", "check": "guild",
     "config": "Skyy_SkyyGuilds/config.properties", "reload": "guildadmin reload", "note": "",
     "setup": ("0.1.2", "Guilds", "guild size, guild XP, levels, the guild bank"),
     "admin": ["/guildadmin config | set <key> <value> - (admin) settings in chat",
               "/guildadmin reload - (admin) re-read config.properties", "/guildadmin xp <amount> <guild> - (admin) test guild XP"],
     "desc": "Guilds: found a guild with your friends - ranks, a shared guild bank, guild XP from your skills, guild levels and seasons.",
     "commands": ["/guild - open the guild page", "/guild create <name> - start a guild", "/guild invite <player> - (leader, admin) invite",
                  "/guild accept | decline | leave - answer an invite or leave",
                  "/guild bank deposit | withdraw <amount> | log - guild coins",
                  "/guild bank limit admin|member <n|0|none> - (leader) daily withdraw limit",
                  "/guild info | list - your guild | the top guilds", "/gc <message> - guild chat"]},
    {"mod": "SkyyEssentials", "version": "0.1.4", "icon": "Tool_Map", "check": "tpa",
     "config": "Skyy_SkyyEssentials/config.properties", "reload": "tradeadmin reload", "note": "Also in game: /tradeadmin config, /warpadmin. replyShortcut needs a restart.",
     "setup": ("0.1.3", "Essentials", "teleports, messages, warps, world spawn, trade"),
     "admin": ["/warpadmin - (admin) warps editor: add, move, rename, remove, world spawn",
               "/tradeadmin config - (admin) the trade settings page",
               "/tradeadmin log [player] | return <player> - (admin) trade log, items back"],
     "desc": "Everyday commands the base game is missing: teleport requests between players, private messages and safe trades of items and coins.",
     "commands": ["/tpa <player> - ask to teleport to a player", "/tpahere <player> - ask a player to teleport to you",
                  "/tpaccept | /tpdeny [player] - answer a teleport request", "/tpacancel - cancel your requests",
                  "/msg <player> <message> (or /tell, /w) - private message", "/reply <message> (or /r) - answer your last message",
                  "/trade <player> | claim - trade items and coins safely", "/fly - (staff) toggle flight"]},
    {"mod": "SkyyRolls", "version": "0.1.5", "icon": "Weapon_Longsword_Copper", "check": "rolls",
     "config": "Skyy_SkyyRolls/reforge.properties", "reload": "", "note": "It is read again by itself whenever someone opens /reforge.",
     "setup": ("0.1.5", "Rolls", "the reforge cost of each rarity"),
     "desc": "Random item stats (reforges) on weapons, armor and tools, shown on the item. Reforge an item for coins on the reforge page.",
     "commands": ["/reforge - open the reforge page", "/rolls give <item> - (admin) an item with random stats",
                  "/rolls read | reroll | clear - (admin) the item in your hand"]},
    # 0.3.1: SkyyRanks 0.1 (live since round 3) - every command is admin only, so players read the description alone
    {"mod": "SkyyRanks", "version": "0.1", "icon": "Furniture_Royal_Magic_Chair", "check": "rankadmin",
     "config": "Skyy_SkyyRanks/config.properties,Skyy_SkyyRanks/ranks.properties", "reload": "rankadmin reload", "note": "",
     "setup": ("0.1", "Ranks", "the ranks editor, the default rank, the chat prefix"),
     "admin": ["/rankadmin - (admin) the ranks editor: ranks, prefixes, grants, members",
               "/rankadmin player <player> - (admin) one player's rank and denies",
               "/rank set | clear <player> - (admin) give or take a rank in chat",
               "/rankadmin reload | sync - (admin) re-read the files, fix the groups"],
     "desc": "Server ranks with a chat prefix in front of your name. The admins make the ranks and what each rank may do, all in game.",
     "commands": ["No commands for players - your rank shows in front of your name in chat."]},
]
'''
rep_between("MODS = [" + LF + '    {"mod": "SkyyMenu"', "# ---- Settings (0.2, research/Settings-Spec.md sections 2 + 4)",
            ['"mod": "SkyyRolls", "version": "0.1.4"', '"note": "No server settings in this version."',
             '"note": "No reload command - restart the server after editing."'], NEW_MODS)

# ---------------------------------------------------------------------------------------------------------------- Settings: guild switches, General tab texts, 8 rows
rep('''    ("party.chat",           "general",     "Party chat",                   "[Party] lines from other members - your own lines always show", "SkyyParty"),''',
    '''    ("party.chat",           "general",     "Party chat",                   "[Party] lines from other members - your own lines always show", "SkyyParty"),
    # 0.3.1: SkyyGuilds 0.1.2's three hide-only switches (its regSetting texts, category general, all default ON)
    ("guild.online",         "general",     "Guild members online/offline", "Steve is online / went offline - the server's guild online notices must be on too", "SkyyGuilds"),
    ("guild.members",        "general",     "Guild join, leave and ranks",  "Steve joined, left, was removed or got a new rank - lines about you always show", "SkyyGuilds"),
    ("guild.chat",           "general",     "Guild chat",                   "[Guild] lines from other members - your own lines always show", "SkyyGuilds"),''')
rep('''    ("general",     "General",     "General (menu, party, teleports, messages)",
     "Always shown: accepted teleports and how they ended, party disbanded, and replies to your own commands and clicks."),''',
    '''    ("general",     "General",     "General (party, guild, teleports, menu)",
     "Always shown: accepted teleports, party or guild disbanded, lines about you, and replies to your own commands and clicks."),''')
rep("SET_ROWS = 7                    # rows per tab page (Prev / Next appear only when a tab has more)",
    "SET_ROWS = 8                    # rows per tab page (Prev / Next appear only when a tab has more; 0.3.1: 8, was 7)")
rep("assert 1 <= SET_ROWS <= 7", "assert 1 <= SET_ROWS <= 8")
rep('''    "SROWS":     "Group #SkyyStgRows { Anchor: (Height: %d); LayoutMode: Top; }" % (SET_ROWS * 76),''',
    '''    "SROWS":     "Group #SkyyStgRows { Anchor: (Height: %d); LayoutMode: Top; }" % (SET_ROWS * 67),     # 0.3.1: rows 61 + gap 6''')
rep('''    "SROW":    ["Group #SkyyStgRow%d { Anchor: (Height: 70); Background: #142030(0.92); LayoutMode: Left; Padding: (Top: 9); }" % r for r in range(SET_ROWS)],''',
    '''    "SROW":    ["Group #SkyyStgRow%d { Anchor: (Height: 61); Background: #142030(0.92); LayoutMode: Left; Padding: (Top: 4); }" % r for r in range(SET_ROWS)],''')
rep("_stall = 2 * 14 + 3 + 48 + 26 + 58 + 58 + 8 + 40 + SET_ROWS * 76 + 26 + 30 + 62",
    "_stall = 2 * 14 + 3 + 48 + 26 + 58 + 58 + 8 + 40 + SET_ROWS * 67 + 26 + 30 + 62" + LF +
    "assert 4 + 52 <= 61, 'a settings row must hold its 52 px text block and buttons'")

# ---------------------------------------------------------------------------------------------------------------- build checks: setup / admin fields + live-set cross-check
LIVE_CHECKS = r'''
# 0.3.1: "setup" = (first version with a Server Setup page, its page title, what is on it) - the fallback text while that mod publishes
# no config:def (an older version, or it failed to start); "admin" = lines only admins see in the Mods view (and on the file-only page)
VER_RE = re.compile(r"^\d+(\.\d+){1,3}$")
def ver_t(v):
    return tuple(int(x) for x in v.split("."))
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

# 0.3.1: the menu data must follow the live set (tools/deploy_set.py SET) and every live mod's own texts. Differences are printed as
# WARNINGs, never fail the build (a later SET bump must not stop this version from building) - read the build output: it ends the check
# with "menu data matches the live set" when MODS versions, MODS entries, the known switches (label / tab / help) and the Server Setup
# titles all agree with the newest build script of every mod SET pins.
import ast as _ast
_ds_src = open(os.path.join(B.PROJECT, "tools", "deploy_set.py"), encoding="utf-8").read()
_LIVE = None
for _n in _ast.parse(_ds_src).body:
    if isinstance(_n, _ast.Assign) and any(isinstance(_t, _ast.Name) and _t.id == "SET" for _t in _n.targets):
        _LIVE = _ast.literal_eval(_n.value)
assert _LIVE, "tools/deploy_set.py has no SET list"
DRIFT = []
_modix = dict((m["mod"], m) for m in MODS)
_known = dict((k[0], k) for k in SET_KNOWN)
_REG = re.compile(r'regSetting\(\s*"([^"]+)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*(true|false|True|False)\s*,\s*"([^"]*)"\s*\)')
_EMIT = re.compile(r'\.emit\(\s*pool\s*,\s*PKG\s*,\s*MOD\s*=\s*"(\w+)"\s*,\s*TITLE\s*=\s*"([^"]+)"')
_live_keys = set()
for _mod, _ver in _LIVE:
    if _mod == "SkyyMenu":
        continue    # its own entry carries VERSION; SET pins the SkyyMenu that is deployed now
    _m = _modix.get(_mod)
    if _m is None:
        DRIFT.append("%s %s is live but not in MODS" % (_mod, _ver))
        continue
    if _m["version"] != _ver:
        DRIFT.append("%s: MODS says %s, the live set runs %s" % (_mod, _m["version"], _ver))
    _p = os.path.join(B.PROJECT, _mod, "build_%s_%s.py" % (_mod.lower(), _ver))
    if not os.path.isfile(_p):
        DRIFT.append("%s: no build script %s" % (_mod, os.path.relpath(_p, B.PROJECT)))
        continue
    _t = open(_p, encoding="utf-8", errors="ignore").read()
    for _k, _lab, _cat, _def, _hlp in _REG.findall(_t):
        _live_keys.add(_k)
        _kn = _known.get(_k)
        if _kn is None:
            DRIFT.append("%s registers the player switch %s - not in SET_KNOWN" % (_mod, _k))
            continue
        if (_kn[2], _kn[1], _kn[3]) != (_lab, _cat, _hlp):
            DRIFT.append("%s: switch %s is %r / %s / %r in the mod, SET_KNOWN differs" % (_mod, _k, _lab, _cat, _hlp))
        if _def.lower() != "true":
            DRIFT.append("%s: switch %s defaults to OFF in the mod" % (_mod, _k))
    _em = _EMIT.findall(_t)
    _st = _m.get("setup")
    if _em and not _st:
        DRIFT.append("%s has a Server Setup page (%s) but no MODS setup entry" % (_mod, _em[0][1]))
    elif _st and not _em:
        DRIFT.append("%s: MODS describes a Server Setup page, its live build script publishes none" % _mod)
    elif _st and _em and (_st[1] != _em[0][1] or _em[0][0] != _mod):
        DRIFT.append("%s: MODS setup page %r, the mod publishes %s %r" % (_mod, _st[1], _em[0][0], _em[0][1]))
for _k in SET_KNOWN:
    if _k[4] != "SkyyMenu" and _k[0] not in _live_keys:
        print("note: known switch %s (%s) is not registered by any live mod yet" % (_k[0], _k[4]))
for _d in DRIFT:
    print("WARNING menu data:", _d)
if DRIFT:
    print("WARNING: %d menu data difference(s) with the live set - update MENU DATA (tools/menu_0_3_1_patch.py or its successor)" % len(DRIFT))
else:
    print("menu data matches the live set (%d mods in tools/deploy_set.py SET, %d player switches registered by them)" % (len(_LIVE), len(_live_keys)))
'''
rep(LF.join([
    'MOD_ADMIN = ["\\n".join([c.replace("%ALIASES%", "") for c in m["commands"] if "(admin)" in c or "(staff)" in c] + m.get("admin", []))',
    '             for m in MODS]']) + LF,
    LF.join([
    'MOD_ADMIN = ["\\n".join([c.replace("%ALIASES%", "") for c in m["commands"] if "(admin)" in c or "(staff)" in c] + m.get("admin", []))',
    '             for m in MODS]']) + LF + LIVE_CHECKS)

# ---------------------------------------------------------------------------------------------------------------- Java data: admin bodies + setup arrays
rep(LF.join([
    'MOD_OLD_BODY = [(txt(m["old"]["desc"]) + "\\nCommands:\\n" + "\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m["old"]["commands"]))',
    '                if "old" in m else "" for m in MODS]']) + LF,
    LF.join([
    'MOD_OLD_BODY = [(txt(m["old"]["desc"]) + "\\nCommands:\\n" + "\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m["old"]["commands"]))',
    '                if "old" in m else "" for m in MODS]',
    '# 0.3.1: the admin-only lines of the Mods view (MODS "admin"): admins read them under MOD_AHEAD between the description and the',
    '# commands (MenuUtil.modBodyFor builds exactly MOD_ABODY at run time), players never see them. The tooltip opens ABOVE the icon, so',
    '# an admin tooltip keeps to 14 detail lines.',
    'MOD_AHEAD = "Admin only:"',
    'MOD_AONLY = ["\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m.get("admin", [])) for m in MODS]',
    '# review 2026-09-25: MenuUtil.modBodyFor puts the admin block after the FIRST line of the text, so a description is one line (the',
    '# info box wraps it); MOD_ABODY is built from its parts and must equal what modBodyFor makes of MOD_BODY',
    'for _m in MODS:',
    '    for _d in [_m["desc"]] + ([_m["old"]["desc"]] if "old" in _m else []):',
    '        assert "\\n" not in _d and "\\r" not in _d, "%s: desc must be one line (the admin lines go after the first line)" % _m["mod"]',
    'MOD_ABODY = [(txt(m["desc"]) + "\\n" + MOD_AHEAD + "\\n" + MOD_AONLY[i] + "\\nCommands:\\n" +',
    '              "\\n".join(txt(c.replace("%ALIASES%", ALIAS_TEXT)) for c in m["commands"])) if MOD_AONLY[i] else MOD_BODY[i]',
    '             for i, m in enumerate(MODS)]',
    'def java_abody(b, a):',
    '    """= MenuUtil.modBodyFor(k, true) on the text b (no "old" wording)"""',
    '    if not a:',
    '        return b',
    '    nl = b.find("\\n")',
    '    return b + "\\n" + MOD_AHEAD + "\\n" + a if nl < 0 else b[:nl] + "\\n" + MOD_AHEAD + "\\n" + a + b[nl:]',
    'for _i, _b in enumerate(MOD_ABODY):',
    '    assert _b == java_abody(MOD_BODY[_i], MOD_AONLY[_i]), "%s: admin text differs from MenuUtil.modBodyFor" % MODS[_i]["mod"]',
    '    assert len(_b.split("\\n")) - 1 <= 14, "%s: the admin tooltip has %d detail lines (max 14)" % (MODS[_i]["mod"], len(_b.split("\\n")) - 1)',
    'MOD_SINCE = [m["setup"][0] if "setup" in m else "" for m in MODS]',
    'MOD_STITLE = [txt(m["setup"][1]) if "setup" in m else "" for m in MODS]',
    'MOD_SWHAT = [txt(m["setup"][2]) if "setup" in m else "" for m in MODS]']) + LF)
rep("for _body in (E_BODY + MOD_BODY + [b for b in MOD_OLD_BODY if b] + [lines_of(v[2]) for v in VIEWS] +",
    "for _body in (E_BODY + MOD_BODY + MOD_ABODY + [b for b in MOD_OLD_BODY if b] + [lines_of(v[2]) for v in VIEWS] +")
rep('F(dat, "public static final String[] MOD_FLINE = %s;" % jarr(MOD_FLINE))' + LF,
    'F(dat, "public static final String[] MOD_FLINE = %s;" % jarr(MOD_FLINE))' + LF +
    '# 0.3.1: admin-only Mods view lines + the Server Setup page each mod has from which version (fallback texts)' + LF +
    'F(dat, "public static final String MOD_AHEAD = %s;" % jstr(MOD_AHEAD))' + LF +
    'F(dat, "public static final String[] MOD_AONLY = %s;" % jarr(MOD_AONLY))' + LF +
    'F(dat, "public static final String[] MOD_SINCE = %s;" % jarr(MOD_SINCE))' + LF +
    'F(dat, "public static final String[] MOD_STITLE = %s;" % jarr(MOD_STITLE))' + LF +
    'F(dat, "public static final String[] MOD_SWHAT = %s;" % jarr(MOD_SWHAT))' + LF)

# ---------------------------------------------------------------------------------------------------------------- MenuUtil: modBodyFor + verCmp
rep(LF.join([
    'public static String modBody(int k) {',
    '  if (k < 0 || k >= @PKG@.MenuData.MOD_BODY.length) return "";',
    '  String need = @PKG@.MenuData.MOD_OLD_NEED[k];',
    '  if (need != null && need.length() > 0 && needOf(need) != null) return @PKG@.MenuData.MOD_OLD_BODY[k];',
    '  return @PKG@.MenuData.MOD_BODY[k];',
    '}""")']) + LF,
    LF.join([
    'public static String modBody(int k) {',
    '  if (k < 0 || k >= @PKG@.MenuData.MOD_BODY.length) return "";',
    '  String need = @PKG@.MenuData.MOD_OLD_NEED[k];',
    '  if (need != null && need.length() > 0 && needOf(need) != null) return @PKG@.MenuData.MOD_OLD_BODY[k];',
    '  return @PKG@.MenuData.MOD_BODY[k];',
    '}""")',
    '# 0.3.1: the Mods-list text for this viewer: admins also read the mod\'s admin-only lines (MODS "admin") right under the description;',
    '# players get modBody unchanged. The "old" wording (an older installed version) carries its own lines only. = MOD_ABODY in Python.',
    'M(utl, r"""',
    'public static String modBodyFor(int k, boolean admin) {',
    '  String body = modBody(k);',
    '  if (!admin || k < 0 || k >= @PKG@.MenuData.MOD_AONLY.length) return body;',
    '  String a = @PKG@.MenuData.MOD_AONLY[k];',
    '  if (a == null || a.length() == 0) return body;',
    '  String need = @PKG@.MenuData.MOD_OLD_NEED[k];',
    '  if (need != null && need.length() > 0 && needOf(need) != null) return body;',
    '  int nl = body.indexOf(\'\\n\');',
    '  if (nl < 0) return body + "\\n" + @PKG@.MenuData.MOD_AHEAD + "\\n" + a;',
    '  return body.substring(0, nl) + "\\n" + @PKG@.MenuData.MOD_AHEAD + "\\n" + a + body.substring(nl);',
    '}""")',
    '# 0.3.1: version order of two manifest versions ("0.3.10" > "0.3.9"): -1, 0 or 1; parts are the leading digits of each dot part',
    '# (missing or non-numeric = 0), so an unknown "?" compares equal to "0" and never throws',
    'M(utl, r"""',
    'public static int verNum(String p) {',
    '  int n = 0;',
    '  if (p == null) return 0;',
    '  for (int i = 0; i < p.length() && i < 9; i++) {',
    '    char c = p.charAt(i);',
    '    if (c < \'0\' || c > \'9\') break;',
    '    n = n * 10 + (c - \'0\');',
    '  }',
    '  return n;',
    '}""")',
    'M(utl, r"""',
    'public static int verCmp(String a, String b) {',
    '  if (a == null || b == null) return 0;',
    '  String[] x = a.trim().split("\\\\.");',
    '  String[] y = b.trim().split("\\\\.");',
    '  int n = x.length > y.length ? x.length : y.length;',
    '  for (int i = 0; i < n; i++) {',
    '    int p = i < x.length ? verNum(x[i]) : 0;',
    '    int q = i < y.length ? verNum(y[i]) : 0;',
    '    if (p < q) return -1;',
    '    if (p > q) return 1;',
    '  }',
    '  return 0;',
    '}""")']) + LF)

# ---------------------------------------------------------------------------------------------------------------- MenuPage: admin bodies, tooltips-off second click
rep('          "public int pages;", "public boolean cleared;"):',
    '          "public int pages;", "public boolean cleared;", "public String cfgArm;"):')
rep("        @PKG@.MenuData.MOD_NAME[k] + \" \" + ver + (installed ? \"\" : \" (not installed)\"), @PKG@.MenuUtil.modBody(k),",
    "        @PKG@.MenuData.MOD_NAME[k] + \" \" + ver + (installed ? \"\" : \" (not installed)\"), @PKG@.MenuUtil.modBodyFor(k, admin),")
rep(LF.join([
    'public void click(@REF@ ref, @ST@ st, int idx, String act) {',
    '  this.status = "";']) + LF,
    LF.join([
    'public void click(@REF@ ref, @ST@ st, int idx, String act) {',
    '  this.status = "";',
    '  String armed = this.cfgArm;',
    '  this.cfgArm = null;']) + LF)
rep(LF.join([
    '  if (act.startsWith("modcfg:")) {',
    '    int mk = -1;',
    '    try { mk = Integer.parseInt(act.substring(7)); } catch (Throwable t) { mk = -1; }',
    '    if (mk >= 0 && mk < @PKG@.MenuData.MOD_NAME.length) { openAdmin(ref, st, @PKG@.MenuData.MOD_NAME[mk]); return; }',
    '  }']) + LF,
    LF.join([
    '  if (act.startsWith("modcfg:")) {',
    '    int mk = -1;',
    '    try { mk = Integer.parseInt(act.substring(7)); } catch (Throwable t) { mk = -1; }',
    '    if (mk >= 0 && mk < @PKG@.MenuData.MOD_NAME.length) {',
    # 0.3.1: without hover tooltips the first click shows the text (commands + admin lines) in the info box, the second opens Server Setup
    '      if (!@PKG@.Tips.isOff(this.playerRef.getUuid()) || act.equals(armed)) { openAdmin(ref, st, @PKG@.MenuData.MOD_NAME[mk]); return; }',
    '      this.cfgArm = act;',
    '      this.infoName = this.names[idx];',
    '      this.infoBody = this.bodies[idx];',
    '      this.status = "Click it again to open its Server Setup page.";',
    '      rebuild();',
    '      return;',
    '    }',
    '  }']) + LF)

# ---------------------------------------------------------------------------------------------------------------- AdminPage: adopter-aware fallback texts
rep(LF.join([
    'public String[] fileRow(int k) {',
    '  String m = @MD@.MOD_NAME[k];',
    '  String live = @MU@.liveVersion(m);',
    '  String name = m + " " + (live != null ? live : @MD@.MOD_VER[k]);',
    '  String rl = @MD@.MOD_RELOAD[k];',
    '  if (rl.length() > 0 && @MU@.cmd(@MU@.firstWord(rl)) == null) rl = "";',
    '  return new String[] { m, "file", name, @MD@.MOD_FLINE[k], rl, "0" };',
    '}""")']),
    LF.join([
    'public String[] fileRow(int k) {',
    '  String m = @MD@.MOD_NAME[k];',
    '  String live = @MU@.liveVersion(m);',
    '  String name = m + " " + (live != null ? live : @MD@.MOD_VER[k]);',
    '  String rl = @MD@.MOD_RELOAD[k];',
    '  if (rl.length() > 0 && @MU@.cmd(@MU@.firstWord(rl)) == null) rl = "";',
    # 0.3.1: a mod that has a Server Setup page from MOD_SINCE on but published no config:def: say why (not running / older version /
    # did not load). live == null here = its check command answers but no ENABLED plugin of that name is loaded (disabled, or the
    # command is another mod's): no version to compare, so neither "older" nor the red "did not load" (review 2026-09-25)
    '  String line = @MD@.MOD_FLINE[k];',
    '  String since = @MD@.MOD_SINCE[k];',
    '  String red = "0";',
    '  if (since.length() > 0) {',
    '    if (live == null) line = "Not running here (disabled or missing) - " + line;',
    '    else if (@MU@.verCmp(live, since) < 0) line = "Server Setup page from " + since + " on - " + line;',
    '    else { line = "Its Server Setup page did not load - see the server log. " + line; red = "1"; }',
    '  }',
    '  return new String[] { m, "file", name, line, rl, red };',
    '}""")']))
rep('''  frame(b, "Server Setup - " + nm + (live != null ? " " + live : ""), k < 0 ? "This mod has no settings page on this server." : "Not set up for in-game editing yet - edit its file, then reload it.");''',
    '''  String since = k < 0 ? "" : @MD@.MOD_SINCE[k];
  boolean off = since.length() > 0 && live == null;
  boolean older = since.length() > 0 && live != null && @MU@.verCmp(live, since) < 0;
  frame(b, "Server Setup - " + nm + (live != null ? " " + live : ""), k < 0 ? "This mod has no settings page on this server."
      : (since.length() == 0 ? "Not set up for in-game editing yet - edit its file, then reload it."
      : (off ? "It is not running on this server - its file can still be edited."
      : (older ? "This version has no Server Setup page yet - edit its file, then reload it."
      : "Its Server Setup page did not load - edit its file, then reload it."))));''')
rep(LF.join([
    '    txt.add(""); bold.add("0");',
    '    txt.add("Its settings show up here, with buttons, once its next version is set up for in-game editing."); bold.add("0");']),
    LF.join([
    '    txt.add(""); bold.add("0");',
    '    if (since.length() == 0) { txt.add("Its settings show up here, with buttons, once its next version is set up for in-game editing."); bold.add("0"); }',
    '    else {',
    '      txt.add("Server Setup page: " + @MD@.MOD_STITLE[k] + " - " + @MD@.MOD_SWHAT[k] + "."); bold.add("1");',
    '      if (off) { txt.add("    " + nm + " is not running here (disabled or missing) - see the server log."); bold.add("0"); }',
    '      else if (older) { txt.add("    It comes with " + nm + " " + since + " - this server runs " + live + ". Update it, then restart."); bold.add("0"); }',
    '      else { txt.add("    It did not publish its settings - look for " + nm + " errors in the server log."); bold.add("0"); }',
    '    }']))

# ---------------------------------------------------------------------------------------------------------------- config kit identity
rep('print("config kit: %d rows, files %s" % (KIT.info["rows"], ", ".join(KIT.info["files"])))',
    'assert KIT.info.get("kit", "1.0") == EXPECTED_KIT, "the emitted config kit is %s, SkyyMenu pins %s" % (KIT.info.get("kit", "1.0"), EXPECTED_KIT)' + LF +
    'print("config kit: %d rows (kit %s, skyycfg.py blob %s), files %s" % (KIT.info["rows"], KIT.info.get("kit", "1.0"), KIT_BLOB[:12], ", ".join(KIT.info["files"])))')
rep('# 0.3.1: admin-only Mods view lines + the Server Setup page each mod has from which version (fallback texts)' + LF,
    '# 0.3.1: which config kit revision this jar carries ("<kit> <first 12 hex of the skyycfg.py git blob>"), shown in the ready line' + LF +
    'F(dat, "public static final String CFG_KIT = %s;" % jstr(KIT_ID))' + LF +
    '# 0.3.1: admin-only Mods view lines + the Server Setup page each mod has from which version (fallback texts)' + LF)
rep('''log("[SkyyMenu] """ + VERSION + r""" ready - /skymenu"""''',
    '''log("[SkyyMenu] """ + VERSION + r""" ready (config kit " + @PKG@.MenuData.CFG_KIT + ") - /skymenu"""''')
rep('jar = os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)' + LF,
    '# 0.3.1: the kit source must still be the one this build emitted (an edit landing during the build fails it: build again)' + LF +
    'assert kit_blob(KIT_FILE) == KIT_BLOB, "tools/skyycfg.py changed during this build (blob %s -> %s) - build again" % (KIT_BLOB[:12], kit_blob(KIT_FILE)[:12])' + LF +
    'jar = os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)' + LF)

# ---------------------------------------------------------------------------------------------------------------- summary print
rep('print("entries:", len(ENTRIES), "player actions:", len(PLAYER_ACTIONS), "mods:", len(MODS))',
    'print("entries:", len(ENTRIES), "player actions:", len(PLAYER_ACTIONS), "mods:", len(MODS),' + LF +
    '      "(%d with a Server Setup page, %d with admin-only lines)" % (len([m for m in MODS if "setup" in m]), len([m for m in MODS if m.get("admin")])))')

assert "No server settings" not in s and 'VERSION = "0.3.1"' in s
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
