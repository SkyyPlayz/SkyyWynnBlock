"""Derive SkyyMenu/build_skyymenu_0.3.4.py from the LIVE SkyyMenu 0.3.3 (python tools/menu_0_3_4_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: 0.3 -> menu_0_3_1_patch.py -> 0.3.1 -> menu_0_3_2_patch.py -> 0.3.2 ->
menu_0_3_3_patch.py -> 0.3.3 (= the tools/deploy_set.py SET pin) -> this patch -> 0.3.4.

0.3.4 = Skyy's decisions of 2026-10-01 (OPEN-QUESTIONS.md):

 1. THE MENU ITEM PER PROFILE ("every profile gets the SkyWynn Menu item the first time it is used" - 0.1 - 0.3.3 gave it once per
    PLAYER, so a new profile had none; Skyy hit it after /kit debug):
     - The "already given" record is keyed by SkyyProfiles' storage key (profile:fn:key, tools/PROFILES-CONTRACT.md: <uuid> for profile
       1, <uuid>-p<N> for profile N; <uuid> without SkyyProfiles): Skyy_SkyyMenu/given-profile/<key>.txt (atomic tmp + move, written
       once, never rewritten). The old per-PLAYER flags Skyy_SkyyMenu/given/<uuid>.txt are only READ from now on (never written or
       deleted, so a rollback to 0.3.3 still finds them).
     - Existing players: a player with an old flag and no per-profile record yet gets ONE record for the profile that is active when
       0.3.4 first sees them (Given.migrate, once per player and server run): that profile counts as already given - no second item on
       the first start, even if they lost it (/skymenu gives a lost one back, as before). Every other profile gets the item the first
       time it is used.
     - Never a second copy: a profile that already holds the item ANYWHERE in the inventory (hotbar, storage, backpack and - new in
       0.3.4 - utility and tools; MenuUtil.count) is only recorded, nothing is given.
     - profile:busy:<uuid> (SkyyProfiles is switching or recovering that player's inventory): the grant waits (retried every second,
       then again by the profile watch) and never trusts the inventory meanwhile (the busy check comes BEFORE the held check).
     - Triggers: PlayerReadyEvent (fires on EVERY world switch) and a new 2 s profile watch (GivenTick, only while SkyyProfiles is
       loaded, only for players past their first PlayerReadyEvent): whenever the player's CURRENT storage key has no session mark,
       ONE GrantTask is scheduled 4 s later (Given.claim: one pending task per player; the task hops onto the player's world thread
       and decides there with Given.plan). A world switch never re-gives: the session mark (Given.SESSION, keyed by storage key) and
       the record both say done. A full inventory sets the session mark (no retry on every world switch) and is retried at the next
       login, as in 0.3.3.
     - Server Setup "Give the menu item" help says profiles; the jar log line says "once per profile".
 2. SECONDS IN SERVER SETUP (Skyy: "use seconds. my brain doesnt compute milliseconds. (just make sure you can use part numbers like
    0.24"; LOCKED 2026-10-01):
     - HOW MENU KNOWS A ROW IS MILLISECONDS: the row's unit column (element 8 of the config:def row = "ms", tools/CONFIG-CONTRACT.md:
       "the unit the admin types, the code carries and the file stores") on an int or dec row (AdminPage.msRow). The config kit's own
       build-time unit rule forces unit ms on every row bound to a *_MS / *Ms / *MILLIS field, and the build scan below found no
       row named like milliseconds with another unit - so every millisecond row of the live set is caught (24 rows, listed by the
       build: "seconds rows"). Not converted (none exist today): a range row or an action value= row with unit ms (they keep ms).
     - SHOWN in seconds: the value box (240 -> 0.24), the name "(s)" instead of "(ms)", a read-only value ("0.24 s"), the help line
       starts with the bounds and the default in seconds ("0.25 to 60 seconds, default 2 - ..."), the Changes log (old -> new), the
       Undo question, and every message a mod's config kit sends back (result line, confirm question, History restore preview,
       import preview: AdminPage.msWords turns "240 ms" into "0.24 s" and "from 250 to 60000 ms" into "from 0.25 to 60 s").
     - TYPED in seconds with decimals (AdminPage.msOf, exact BigDecimal, no float): 0.24 -> 240, 1.5 -> 1500, 0.001 -> 1, 30 -> 30000,
       rounded half up to whole milliseconds on an int row (0.2405 -> 241); "1.5s", "2 sec", "2 seconds" work, "240ms" means
       milliseconds. Refused before anything is sent (status line, nothing changes): not a number, a comma, two dots, other suffixes,
       below the row's min or above its max ("Paid jump cooldown must be 0.2 to 600 seconds."). Less / More step in the file unit.
     - The row's own help text (the mod wrote it in ms: "...once per this many ms.") is shown in seconds too (AdminPage.secHelp, reviewed
       2026-10-01); a row without help text gets no dangling " - " after the bounds.
     - The FILE keeps milliseconds: the menu always sends canonical whole milliseconds to the mod (config:fn set), so every mod, file,
       export code and chat command (/<mod> set <key> <value>) stays in milliseconds as before. Hours / minutes / seconds rows are
       unchanged (SkyyProfiles deleteUndoHours stays in hours).
 3. MODS DATA = tools/deploy_set.py SET of 2026-10-01 (MODS_VERSIONS below - the ONE place to bump a version: edit it, regenerate,
    rebuild; the build's live-set check names anything else that differs). Text changes: SkyyGuilds 0.1.5 (disband pays back by contribution), SkyyProfiles 0.1.5 (/profiles delete,
    /profiles restore, /profileadmin archive list | restore, the 6-hour undo), SkyyAccessories 0.5.1 (18 slots, booster lines,
    /accessories lines, the admin give lines), SkyyGear 0.1.2 (/gear charged, admin), SkyyUiProbe 0.2 as a developer test mod (admin
    /skyprobe; drop the entry when it moves to RETIRED). ROUND_PINS / ROUND_RETIRED are empty: this SkyyMenu deploys on its own.
    SkyyGuilds 0.1.5 was deployed while this was built (MODS names it). SkyyGear 0.1.3 (built, not in SET yet) adds no command and no
    player switch in its current script, so bumping it is one MODS_VERSIONS edit.

CHECKED: build ("assembled"), python tools/ci/lint.py, the bare-JVM harness SkyyMenu/test_skyymenu_0.3.4.py (every 0.3.3 check + the
seconds conversion, every millisecond row, the per-profile item, two starts on a scratch copy of the live Skyy_SkyyMenu data, the class
byte-compare against SkyyMenu-0.3.3.jar).

NOT CHANGED: every page look (no new UI element, only texts in existing labels), the player Settings registry, commands, nodes, bridge
keys, the config kit (1.1), MENU_CFG_TEXT (the config.properties template; existing files are never rewritten; its comment line about
giveItem still says "new players ... first join" - changing it would change MenuCfg's bytes, which this round keeps identical).
"""
import os
import re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.3.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.4.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)

# THE MODS VERSIONS this SkyyMenu names = tools/deploy_set.py SET (2026-10-01, SkyyGuilds 0.1.5 deployed while this was built). Bump one
# here when its mod lands in SET (SkyyGear 0.1.3 next: no new command or switch in its script today), regenerate, rebuild - the build's live-set check prints
# "menu data matches the live set" or names what else differs (new switches, a renamed Server Setup page).
MODS_VERSIONS = {
    "SkyyProfiles": "0.1.5", "SkyyIslands": "0.5.4", "SkyySacks": "0.7.9", "SkyyAccessories": "0.5.1", "SkyyHud": "0.3.10",
    "SkyySkills": "0.4.10", "SkyyTrees": "0.2.5", "SkyyCollections": "0.2.4", "SkyyCooking": "0.1.3", "SkyyExploration": "0.2.2",
    "SkyyClasses": "0.1.10", "SkyyBazaar": "0.1.2", "SkyyAuctions": "0.1.2", "SkyyBank": "0.1.5", "SkyyCoins": "0.1.5",
    "SkyyVault": "0.1.5", "SkyyParty": "0.1.6", "SkyyGuilds": "0.1.5", "SkyyEssentials": "0.1.6", "SkyyGear": "0.1.2",
    "SkyyRanks": "0.1.1", "SkyyUiProbe": "0.2",
}


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


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF + "0.3.3: SkyyGear compat",
    '"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF +
    "0.3.4: Skyy's 2026-10-01 decisions: the SkyWynn Menu item once PER PROFILE (records given-profile/<storage key>.txt; the old" + LF +
    "       per-player flags given/<uuid>.txt only read: the profile active at the first 0.3.4 sight counts as given; never a second copy" + LF +
    "       while one is anywhere in the inventory incl. utility / tools; waits while profile:busy; PlayerReadyEvent + a 2 s profile" + LF +
    "       watch); Server Setup shows and takes millisecond rows (unit ms) in SECONDS with decimals (0.24 = 240 ms, rounded to whole ms," + LF +
    "       the file keeps ms; log, undo and kit messages in seconds too); MODS data = tools/deploy_set.py SET of 2026-10-01 (Profiles" + LF +
    "       0.1.5 delete / restore / archive, Accessories 0.5.1, Gear 0.1.2, SkyyUiProbe as a dev mod). Notes: tools/menu_0_3_4_patch.py." + LF +
    "0.3.3: SkyyGear compat")
rep('VERSION = "0.3.3"', 'VERSION = "0.3.4"')
rep('"set EXPECTED_KIT through tools/menu_0_3_3_patch.py (or its successor), regenerate, re-test"',
    '"set EXPECTED_KIT through tools/menu_0_3_4_patch.py (or its successor), regenerate, re-test"')
rep(''' - Given once per player: PlayerReadyEvent (fires on EVERY world switch) -> in-memory once-per-session guard -> GrantTask polls''',
    ''' - Given once per PROFILE (0.3.4; once per player before): PlayerReadyEvent (fires on EVERY world switch) or the 2 s profile watch
   (GivenTick) -> in-memory once-per-session guard keyed by the profile's storage key -> GrantTask polls''')
rep('''   after a restart. Inventory full -> message, retried on the next login (PlayerDisconnectEvent clears the session guard).''',
    '''   after a restart. Inventory full -> message, retried on the next login (PlayerDisconnectEvent clears the session guard).
   0.3.4: the persisted record is Skyy_SkyyMenu/given-profile/<storage key>.txt (profile:fn:key; <uuid> = profile 1 or no SkyyProfiles);
   the old given/<uuid>.txt flags are only read (Given.migrate: the profile active at the first 0.3.4 sight counts as given).''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyProfiles 0.1.5
rep('''     "setup": ("0.1.1", "Profiles", "profile slots (6 by default), switching, inventory"),
     "admin": ["/profileadmin config | set <setting> <value> - (admin) settings in chat"],
     "desc": "SkyBlock-style profiles: each profile is its own save with its own class (Archer, Warrior, Mage, Berserker or Priest), island, inventory, coins, bank, bags, skills and collections. A new profile starts with its class kit.",
     "commands": ["/profiles (or /profile) - open your profiles", "/profiles create (or new) - a new profile: pick its class, get its kit",
                  "/profiles switch <number or name> - switch to another profile", "/profiles list - your profiles in chat",
                  "/profileadmin info <player> - (admin) a player's profiles",
                  "/profileadmin setclass <player> <n> <class> - (admin) fix a class",
                  "/profileadmin reload - (admin) re-read the settings"]},''',
    '''     # 0.3.4: SkyyProfiles 0.1.5 - profile delete (confirm, then a 6-hour undo window by default), restore, the admin archive;
     # /profileadmin reload joins the config line (the info box shows 8 Commands lines at most)
     "setup": ("0.1.1", "Profiles", "profile slots, switching, inventory, delete undo hours"),
     "admin": ["/profileadmin config | set <setting> <value> | reload - (admin)",
               "/profileadmin archive list <player> - (admin) deleted and archived profiles",
               "/profileadmin archive restore <player> <profile> - (admin) bring one back"],
     "desc": "SkyBlock-style profiles: each profile is its own save with its own class (Archer, Warrior, Mage, Berserker or Priest), island, inventory, coins, bank, bags, skills and collections. A new profile starts with its class kit. A deleted profile can be restored for a few hours (6 by default).",
     "commands": ["/profiles (or /profile) - open your profiles", "/profiles create (or new) - a new profile: pick its class, get its kit",
                  "/profiles switch <number or name> - switch to another profile", "/profiles list - your profiles in chat",
                  "/profiles delete <number or name> - delete a profile (type it again to confirm)",
                  "/profiles restore <number or name> - bring back a profile you deleted",
                  "/profileadmin info <player> - (admin) a player's profiles",
                  "/profileadmin setclass <player> <n> <class> - (admin) fix a class"]},''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyAccessories 0.5.1
rep('''     "setup": ("0.4.4", "Accessories", "accessory slots, talisman bonuses, regeneration"),
     "admin": ["/accessories reload - (admin) re-read config.properties after hand edits"],
     "desc": "Your Accessory Bag: 9 slots for bench accessories (each unlocks its bench tab in /craft, the Campfire one cooks on the go) and stat talismans that work while they sit in the bag.",
     "commands": ["/accessories (or /acc, /accbag) - open your Accessory Bag"]},''',
    '''     # 0.3.4: SkyyAccessories 0.5 / 0.5.1 - booster accessories (one table, ten lines), 18 bag slots to start, /accessories lines,
     # admin give / givetier (requirePermission skyyaccessories.admin)
     "setup": ("0.4.4", "Accessories", "bag slots, booster lines and numbers, notices"),
     "admin": ["/accessories reload - (admin) re-read config.properties after hand edits",
               "/accessories give <player> <item> [amount] - (admin) give an accessory",
               "/accessories givetier <player> <line> <rarity> [amount] - (admin)"],
     "desc": "Your Accessory Bag: 18 slots to start for bench accessories (each unlocks its bench tab in /craft, the Campfire one cooks on the go) and booster accessories - Health, Stamina, Mana, Regeneration, Speed and more - that work while they sit in the bag. Only the best rarity of each line counts.",
     "commands": ["/accessories (or /acc, /accbag) - open your Accessory Bag",
                  "/accessories lines - every accessory line, its rarities and numbers"]},''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyGuilds 0.1.5
rep('''     "desc": "Guilds: found a guild with your friends - ranks, a shared guild bank, guild XP from your skills, guild levels and seasons.",''',
    '''     # 0.3.4: SkyyGuilds 0.1.5 (deployed 2026-10-01): a disband pays the guild bank back by each member's share of the deposits
     # (net = deposited - withdrawn), the member list shows that Contribution - no new command, switch or Server Setup title
     "desc": "Guilds: found a guild with your friends - ranks, a shared guild bank, guild XP from your skills, guild levels and seasons. If a guild disbands, its bank goes back to the members by what each put in.",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyGear 0.1.2
rep('''               "/gear migrate [player] - (admin) run the old rolled items scan now"],''',
    '''               "/gear migrate [player] - (admin) run the old rolled items scan now",
               "/gear charged - (admin) charged attack probe for the held weapon"],''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyUiProbe (dev)
rep('''     "commands": ["No commands for players - your rank shows in front of your name in chat."]},
]''',
    '''     "commands": ["No commands for players - your rank shows in front of your name in chat."]},
    # 0.3.4: SkyyUiProbe 0.2 is in tools/deploy_set.py SET as a DEVELOPER / TEST mod (the vanilla UI kit's probe pages, admins only:
    # requirePermission skyyuiprobe.admin). It moves to RETIRED once the probe results are in - then drop this entry.
    {"mod": "SkyyUiProbe", "version": "0.2", "icon": "Ingredient_Crystal_Cyan", "check": "skyprobe",
     "config": "", "reload": "", "note": "A developer test mod - nothing to set up.",
     "admin": ["/skyprobe [n | name | list] - (admin) open the UI kit probe pages"],
     "desc": "Developer test mod, not a game feature: admins open the UI kit's probe pages to check that the vanilla look works in game.",
     "commands": ["No commands for players - this is a developer test mod."]},
]''')

# ---------------------------------------------------------------------------------------------------------------- MODS: versions = SET
for _mod, _ver in MODS_VERSIONS.items():
    _pat = re.compile(r'(\{"mod": "%s", "version": ")([\d.]+)(")' % re.escape(_mod))
    _hits = _pat.findall(s)
    assert len(_hits) == 1, "MODS entry %s: %d hits" % (_mod, len(_hits))
    s = _pat.sub(lambda m: m.group(1) + _ver + m.group(3), s, count=1)

# ---------------------------------------------------------------------------------------------------------------- round data: none
rep('''# ---- 0.3.3: the round this SkyyMenu deploys WITH (round 9 + the SkyyGear round; round 8 is already pinned in tools/deploy_set.py SET):
# mod: (the SET version the round replaces - None for a mod the round ADDS -, the round's version). MODS names the round's version. The
# live-set check accepts it while SET still pins the replaced version (or lacks the new mod), reads the round's build script once it
# exists and runs a second time on the SET the main session pins when the round deploys (see menu_check). Inert once SET pins it.
ROUND_PINS = {"SkyyClasses": ("0.1.6", "0.1.7"), "SkyyTrees": ("0.2.3", "0.2.4"), "SkyyVault": ("0.1.2", "0.1.3"),
              "SkyyIslands": ("0.5.2", "0.5.3"), "SkyyRanks": ("0.1", "0.1.1"), "SkyyAuctions": ("0.1.1", "0.1.2"),
              "SkyyGear": (None, "0.1")}
# mods this round RETIRES: mod: (the SET version that leaves, the MODS entry that replaces it). The main session drops it from SET and puts
# it into tools/deploy_set.py RETIRED (SkyyGear spec 8.3); MODS no longer lists it.
ROUND_RETIRED = {"SkyyRolls": ("0.1.5", "SkyyGear")}''',
    '''# ---- the round this SkyyMenu deploys WITH: mod: (the SET version the round replaces - None for a mod the round ADDS -, the round's
# version). MODS names the round's version; the live-set check accepts it while SET still pins the replaced version and runs a second time
# on the SET the main session pins when the round deploys (see menu_check). Inert once SET pins it.
# 0.3.4: EMPTY - this SkyyMenu deploys on its own; MODS names exactly what tools/deploy_set.py SET pins (tools/menu_0_3_4_patch.py
# MODS_VERSIONS). To ship it together with e.g. SkyyGear 0.1.3: {"SkyyGear": ("0.1.2", "0.1.3")} + that version in MODS_VERSIONS.
ROUND_PINS = {}
# mods a round RETIRES: mod: (the SET version that leaves, the MODS entry that replaces it). 0.3.3 retired SkyyRolls (in RETIRED now).
ROUND_RETIRED = {}''')
rep('_PATCH = "tools/menu_0_3_3_patch.py"', '_PATCH = "tools/menu_0_3_4_patch.py"')

# ---------------------------------------------------------------------------------------------------------------- build report: seconds rows
rep('''ROUND_DRIFT = menu_report("this round's set", ROUND_SET, ROUND_SET_RETIRED)''',
    '''ROUND_DRIFT = menu_report("this round's set", ROUND_SET, ROUND_SET_RETIRED)
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
                nums = [x for x in a[4:] if isinstance(x, str) and re.match(r"^-?\\d+$", x)]
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
assert MS_ROWS and all(r[2] in ("int", "dec") for r in MS_ROWS), "every unit-ms row of the live set is an int / dec row (range rows keep ms)"''')

# ---------------------------------------------------------------------------------------------------------------- Server Setup: menu item row
rep('''     "New players get the SkyWynn Menu item at their first join. Off: only /skymenu gives one.",''',
    '''     "Every profile gets the SkyWynn Menu item the first time it is used. Off: only /skymenu gives one.",''')

# ---------------------------------------------------------------------------------------------------------------- probes + the new class
rep('''             (T["INV"], "getStorage"), (T["INV"], "getHotbar"), (T["INV"], "getBackpack"),''',
    '''             (T["INV"], "getStorage"), (T["INV"], "getHotbar"), (T["INV"], "getBackpack"), (T["INV"], "getUtility"), (T["INV"], "getTools"),''')
rep('''quit_ = mk("MenuQuit")''', '''quit_ = mk("MenuQuit")
gtk  = mk("GivenTick")      # 0.3.4: the 2 s profile watch (a new profile gets its menu item without a world switch)''')
rep('''WRITE = (dat, utl, giv, mcfg, sreg, sst, ssv, tip, sld, sgf, srf, ssf, sdc, page, spg, apg, ast, ref_, clo_, fac, cmd, scmd, acmv, acmd, grt, rdy, seen, quit_, pl)''',
    '''WRITE = (dat, utl, giv, mcfg, sreg, sst, ssv, tip, sld, sgf, srf, ssf, sdc, page, spg, apg, ast, ref_, clo_, fac, cmd, scmd, acmv, acmd, grt, rdy, seen, quit_, gtk, pl)''')

# ---------------------------------------------------------------------------------------------------------------- inventory: utility + tools
rep('''  return countIn(inv.getStorage(), id) + countIn(inv.getHotbar(), id) + countIn(inv.getBackpack(), id);''',
    '''  return countIn(inv.getStorage(), id) + countIn(inv.getHotbar(), id) + countIn(inv.getBackpack(), id)
       + countIn(inv.getUtility(), id) + countIn(inv.getTools(), id);''')
rep('''# ---- inventory (world thread only; SkyyBazaar Inv pattern: every add is verified by re-counting)''',
    '''# ---- inventory (world thread only; SkyyBazaar Inv pattern: every add is verified by re-counting)
# 0.3.4: count() = every container the item can sit in (hotbar, storage, backpack, utility, tools) - "never a second copy" (Skyy)''')

# ---------------------------------------------------------------------------------------------------------------- Given: per-profile records
GIVEN_OLD = '''# ================= Given: persisted "already got the menu item" flags + session guards =================
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
    byte[] data = ("menu item given " + System.currentTimeMillis() + "\\n").getBytes("UTF-8");
    java.nio.file.Files.write(tmp, data, new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".txt"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not save the menu-item flag for " + u + ": " + t); }
}""")
'''
GIVEN_NEW = '''# ================= Given: persisted "already got the menu item" records + session guards =================
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
    byte[] data = ("menu item given " + System.currentTimeMillis() + "\\n").getBytes("UTF-8");
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
public static synchronized boolean claim(java.util.UUID u, long now) {
  if (u == null) return false;
  Object o = PENDING.get(u);
  if (o instanceof Long && now - ((Long) o).longValue() < 90000L) return false;
  PENDING.put(u, Long.valueOf(now));
  return true;
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
}""")
'''
rep(GIVEN_OLD, GIVEN_NEW)

# ---------------------------------------------------------------------------------------------------------------- /skymenu: record per profile
rep('''      if (@PKG@.MenuUtil.giveMenuItem(player)) {
        @PKG@.Given.markGiven(u);
        @PKG@.Given.SESSION.put(u, Boolean.TRUE);''',
    '''      if (@PKG@.MenuUtil.giveMenuItem(player)) {
        String gk = @PKG@.Given.key(u);
        @PKG@.Given.markGiven(gk);
        @PKG@.Given.SESSION.put(gk, Boolean.TRUE);''')

# ---------------------------------------------------------------------------------------------------------------- Given.plan + GrantTask
GRANT_OLD_START = '''# ================= GrantTask: give the menu item once (scheduler -> the player's world thread) ================='''
GRANT_OLD_END = '''# ================= MenuReady: PlayerReadyEvent (every world switch) -> GrantTask once per session ================='''
i0, i1 = s.index(GRANT_OLD_START), s.index(GRANT_OLD_END)
assert s.count(GRANT_OLD_START) == 1 and s.count(GRANT_OLD_END) == 1 and i0 < i1
GRANT_NEW = '''# ================= Given.plan (0.3.4; after MenuCfg - it reads MenuCfg.GIVE_ITEM) =================
# what a grant does for player u whose ACTIVE profile has the storage key `key` and who holds `held` menu items (-1 = no player entity now):
#   1 = nothing to do: this session did it, the item is switched off, the profile already got it (record), or it holds one (recorded now)
#   2 = try again later: SkyyProfiles is busy with that player's inventory (profile:busy - checked BEFORE the inventory is trusted), or
#       no player entity
#   4 = give ONE now (the session mark is set first, so a full inventory is not retried on every world switch - next login)
M(giv, r"""
public static int plan(java.util.UUID u, String key, int held) {
  if (u == null || !validKey(key)) return 2;
  if (SESSION.containsKey(key)) return 1;
  if (!@PKG@.MenuCfg.GIVE_ITEM) { SESSION.put(key, Boolean.TRUE); return 1; }
  migrate(u, key);
  if (isGiven(key)) { SESSION.put(key, Boolean.TRUE); return 1; }
  if (@PKG@.MenuUtil.profileBusy(u)) return 2;
  if (held < 0) return 2;
  if (held > 0) { markGiven(key); SESSION.put(key, Boolean.TRUE); return 1; }
  SESSION.put(key, Boolean.TRUE);
  return 4;
}""")

# ================= GrantTask: give the menu item once per profile (scheduler -> the player's world thread) =================
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
# 0 = given now, 1 = nothing to do, 2 = retry later, 3 = inventory full (retried next login) - the decision is Given.plan; ONE storage key
# for the whole grant (resolved here on the world thread, where a SkyyProfiles switch - one world task - can never be half done)
M(grt, r"""
public int grantNow(java.util.UUID u) {
  String key = @PKG@.Given.key(u);
  @PLA@ p = null;
  @REF@ r = this.pr.getReference();
  if (r != null && r.isValid()) {
    @ST@ st = r.getStore();
    if (st != null) p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
  }
  int held = p == null ? -1 : @PKG@.MenuUtil.count(p, @PKG@.MenuData.ITEM_ID);
  int d = @PKG@.Given.plan(u, key, held);
  if (d != 4) return d;
  if (@PKG@.MenuUtil.giveMenuItem(p)) {
    @PKG@.Given.markGiven(key);
    this.pr.sendMessage(@MSG@.raw("[SkyWynn] You got the SkyWynn Menu! Right-click it to open teleports, your bags, skills, the bazaar and more. Lost it? Type /skymenu."));
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
    java.util.UUID wu = this.pr.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null) { later(1000L); return this.tries < 30; }
    this.expected = w;
    w.execute(this);
    return true;
  }
  java.util.UUID wu2 = this.pr.getWorldUuid();
  @WLD@ now = wu2 == null ? null : @UNI@.get().getWorld(wu2);
  if (now != this.expected) { later(1000L); return this.tries < 30; }
  if (@PKG@.Given.INFLIGHT.putIfAbsent(u, Boolean.TRUE) != null) return false;
  int res = 2;
  try { res = grantNow(u); } catch (Throwable t) { @PKG@.MenuUtil.warn("menu item grant failed for " + u + ": " + t); res = 3; }
  @PKG@.Given.INFLIGHT.remove(u);
  if (res == 2) { later(1000L); return this.tries < 30; }
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
  if (!again && u != null) @PKG@.Given.PENDING.remove(u);
}""")
# 0.3.4: ONE pending GrantTask per player, 4 s after the trigger (both triggers use it; the task decides on the world thread)
M(giv, r"""
public static boolean schedule(@PR@ pr, long ms) {
  try {
    if (pr == null || !claim(pr.getUuid(), System.currentTimeMillis())) return false;
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GrantTask(pr), ms, java.util.concurrent.TimeUnit.MILLISECONDS);
    return true;
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule the menu item grant: " + t); return false; }
}""")

'''
s = s[:i0] + GRANT_NEW + s[i1:]

# ---------------------------------------------------------------------------------------------------------------- MenuReady + GivenTick
rep('''    @PKG@.SetLoadTask.preload(pr);
    if (@PKG@.Given.SESSION.containsKey(pr.getUuid())) return;
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GrantTask(pr), 4L, java.util.concurrent.TimeUnit.SECONDS);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("ready handler failed: " + t); }
}""")''',
    '''    @PKG@.SetLoadTask.preload(pr);
    java.util.UUID u = pr.getUuid();
    @PKG@.Given.READY.put(u, Boolean.TRUE);
    if (!@PKG@.Given.wants(u)) return;
    @PKG@.Given.schedule(pr, 4000L);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("ready handler failed: " + t); }
}""")

# ================= GivenTick (0.3.4): the profile watch - a profile switch or a new profile (SkyyProfiles flips profile:fn:key) needs no
# world switch to give that profile its menu item. Every 2 s, only while SkyyProfiles is loaded (without it the key never changes and
# PlayerReadyEvent covers everything), only for players past their first PlayerReadyEvent (the join path schedules those): a player whose
# CURRENT storage key has no session mark gets ONE GrantTask (Given.schedule / claim). Cheap: one bridge read + one map lookup each.
gtk.addInterface(pool.get("java.lang.Runnable"))
C(gtk, "public GivenTick() { }")
M(gtk, r"""
public void run() {
  try {
    if (!(@PKG@.MenuUtil.bridge().get("profile:fn:key") instanceof java.util.function.Function)) return;
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      if (!@PKG@.Given.READY.containsKey(u) || !@PKG@.Given.wants(u)) continue;
      @PKG@.Given.schedule(pr, 4000L);
    }
  } catch (Throwable t) { }
}""")''')
rep('''# ================= MenuReady: PlayerReadyEvent (every world switch) -> GrantTask once per session =================''',
    '''# ================= MenuReady: PlayerReadyEvent (every world switch) -> GrantTask once per profile and session =================''')

# ---------------------------------------------------------------------------------------------------------------- SeenTick + MenuQuit
rep('''    @PKG@.Given.SESSION.keySet().retainAll(online);''', '''    @PKG@.Given.retainOnline(online, onlineK);''')
rep('''    @PKG@.Given.SESSION.remove(pr.getUuid());''', '''    @PKG@.Given.forget(pr.getUuid());''')

# ---------------------------------------------------------------------------------------------------------------- plugin
rep('''F(pl, "public java.util.concurrent.ScheduledFuture ticker;")''',
    '''F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
F(pl, "public java.util.concurrent.ScheduledFuture watch;")''')
rep('''  @PKG@.Given.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("given");''',
    '''  @PKG@.Given.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("given-profile");
  @PKG@.Given.LEGACY = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("given");''')
rep('''  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SeenTick(), 30L, 30L, java.util.concurrent.TimeUnit.SECONDS);''',
    '''  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SeenTick(), 30L, 30L, java.util.concurrent.TimeUnit.SECONDS);
  this.watch = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.GivenTick(), 5L, 2L, java.util.concurrent.TimeUnit.SECONDS);''')
rep('''right-click the SkyWynn Menu item; the item is given once per player; /settings''',
    '''right-click the SkyWynn Menu item; the item is given once per profile; /settings''')
rep('''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }''',
    '''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { if (this.watch != null) this.watch.cancel(false); } catch (Throwable t) { }''')

# ---------------------------------------------------------------------------------------------------------------- seconds: helpers
SEC_HELPERS = '''# ---- 0.3.4: MILLISECOND ROWS IN SECONDS (Skyy, LOCKED 2026-10-01: "use seconds ... make sure you can use part numbers like 0.24").
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
    java.util.regex.Matcher m = java.util.regex.Pattern.compile("(?<![\\\\w.])from (-?\\\\d+(?:\\\\.\\\\d+)?) to (-?\\\\d+(?:\\\\.\\\\d+)?) ms\\\\b").matcher(s);
    StringBuffer sb = new StringBuffer();
    while (m.find()) m.appendReplacement(sb, java.util.regex.Matcher.quoteReplacement("from " + secText(m.group(1)) + " to " + secText(m.group(2)) + " s"));
    m.appendTail(sb);
    java.util.regex.Matcher m2 = java.util.regex.Pattern.compile("(?<![\\\\w.])(-?\\\\d+(?:\\\\.\\\\d+)?) ms\\\\b").matcher(sb.toString());
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
  try { t = t.replaceAll("(?i)\\\\b(?:milliseconds?|millis|ms)\\\\b", "seconds"); } catch (Throwable x) { }
  return t;
}""")
'''
rep('''M(apg, r"""
public static String rStatus(Object r) {''', SEC_HELPERS + '''M(apg, r"""
public static String rStatus(Object r) {''')
rep('''  return a.length > 2 && a[2] instanceof String ? (String) a[2] : "";''',
    '''  return a.length > 2 && a[2] instanceof String ? msWords((String) a[2]) : "";''')
rep('''  if (v.length() == 0) return "(empty)";
  String u = rv(r, 8);''',
    '''  if (v.length() == 0) return "(empty)";
  if (msRow(r)) return secText(v) + " s";
  String u = rv(r, 8);''')

# ---------------------------------------------------------------------------------------------------------------- seconds: the row
rep('''  String draft = (String) this.drafts.get(key);
  if (draft != null && val != null && draft.trim().equals(val)) { this.drafts.remove(key); draft = null; }''',
    '''  String draft = (String) this.drafts.get(key);
  boolean ms = msRow(w);
  String valShown = val == null ? null : (ms ? secText(val) : val);      // 0.3.4: (the choice widget below has its own "shown")
  if (draft != null && val != null && (draft.trim().equals(valShown) || (ms && val.equals(msOf(draft, !type.equals("dec")))))) { this.drafts.remove(key); draft = null; }''')
rep('''    field(b, wsel, "SkyyAdmVal" + r, step != null ? 156 : 270, 42, 2000, draft != null ? draft : (val == null ? "" : val), "");''',
    '''    field(b, wsel, "SkyyAdmVal" + r, step != null ? 156 : 270, 42, 2000, draft != null ? draft : (valShown == null ? "" : valShown), "");''')
rep('''  String unit = rv(w, 8);
  String tg = tagOf(w);''',
    '''  String unit = ms ? "s" : rv(w, 8);
  String tg = tagOf(w);''')
rep('''  String help = rv(w, 10);
  if (tg.length() > 0 && nm.length() + 4 + tg.length() <= 50) nm = nm + "    " + tg;''',
    '''  String help = rv(w, 10);
  if (ms) help = secHint(w) + (help.length() > 0 ? " - " + secHelp(help) : "");      // no dangling " - " on a row without help text
  if (tg.length() > 0 && nm.length() + 4 + tg.length() <= 50) nm = nm + "    " + tg;''')

# ---------------------------------------------------------------------------------------------------------------- seconds: Set / Less / More
rep('''  if (verb.equals("aset")) {
    String v = (String) this.drafts.get(key);
    if (v == null) v = cur(this.mod, key);
    if (v == null || v.trim().length() == 0) { setStatus("Type a value first.", 2); return false; }
    doSet(key, v);''',
    '''  if (verb.equals("aset")) {
    String v = (String) this.drafts.get(key);
    boolean typedSet = v != null;
    if (v == null) v = cur(this.mod, key);
    if (v == null || v.trim().length() == 0) { setStatus("Type a value first.", 2); return false; }
    if (typedSet) {
      String[] tv = typedValue(w, v);
      if (tv[0] == null) { setStatus(tv[1], 3); return false; }
      v = tv[0];
    }
    doSet(key, v);''')
rep('''    String c = (String) this.drafts.get(key);
    boolean typedNow = c != null;
    if (c == null) c = cur(this.mod, key);''',
    '''    String c = (String) this.drafts.get(key);
    boolean typedNow = c != null;
    if (typedNow && msRow(w)) { String mc = msOf(c, !rv(w, 3).equals("dec")); c = mc == null ? "?" : mc; }
    if (c == null) c = cur(this.mod, key);''')

out = s.replace(LF, NL) if NL != LF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines)" % out.count("\n"))
