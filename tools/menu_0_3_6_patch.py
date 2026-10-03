"""Derive SkyyMenu/build_skyymenu_0.3.6.py from the LIVE SkyyMenu 0.3.5 (python tools/menu_0_3_6_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: 0.3 -> menu_0_3_1_patch.py -> ... -> menu_0_3_5_patch.py -> 0.3.5 (= the
tools/deploy_set.py SET pin, generated - never re-run its patch, never re-build it) -> this patch -> 0.3.6. 0.3.5's files stay untouched.

0.3.6 = THE STUCK-PAGE FIX + the Mods list of the 2026-10-03 SET.

ROOT CAUSE (proven 2026-10-03 by the SkyyBank 0.1.6 round - HANDOFF log, SkyyBank/build_skyybank_0.1.6.py; re-read from the release
HytaleServer.jar bytecode for this patch, tools/dev/bcfull.py / callers.py):
  - PageManager.handleEvent: Data (a page click) returns at once while customPageRequiredAcknowledgments != 0 - silently; Dismiss does
    customPage.onDismiss(ref, store) + customPage = null and nothing else (no packet, no counter change); Acknowledge decrements (below
    0: incremented back + "Client sent unexpected acknowledgement"). The switch map PageManager$1: 1 = Dismiss, 2 = Data, 3 = Acknowledge.
  - +1 for every page packet: updateCustomPage (openCustomPage, CustomUIPage.rebuild, sendUpdate), and setPage(..) - so close(),
    setPage(None), setPageWithWindows (benches) - but ONLY while a custom page is open (setPage with no page sends SetPage, adds nothing).
  - World.addPlayer(playerRef, transform, ..) is the one way into a world (TeleportSystems$PlayerMoveSystem.teleportToWorld on the OLD
    world's thread right after PlayerRef.removeFromStore, Universe.addPlayer / transferPlayerAsync / resetPlayer, InstancesPlugin,
    HubPortalInteraction, World.drainPlayersTo): it sets the player's world id, DISPATCHES AddPlayerToWorldEvent(holder, world, message)
    synchronously (holder = the player's components; the player is in no world store), then runAsync(onSetupPlayerJoining) = player
    .getPageManager().clearCustomPageAcknowledgements() + the JoinWorld packet, and only after the client is ready for chunks (up to 30 s)
    thenApplyAsync(onFinishPlayerJoining, world) = PlayerRef.addToStore on the new world's thread. The reset keeps PageManager.customPage;
    the client drops its page at the world change. PlayerReadyEvent comes later still (the client's ClientReady, or a 10 s timeout on
    the SCHEDULED_EXECUTOR thread - not the world thread).
  - So a page open across a world change stays the server's page, and the next setPage / page update for it (SkyyMenu 0.3.5's CloseTask
    ~150 ms after the Island / Hub tile, RefreshTask, any bench) adds 1 the client never acknowledges: every custom page ignores clicks
    until the next world change.

WHAT 0.3.6 CHANGES (Java):
 1. CloseTask / RefreshTask (SkyyMenu's only delayed page calls - every other page call answers a click on a page the client shows):
    a menu that is still the server's page but whose player changed world since it opened (MenuPage.changedWorld: the world it was first
    built in differs, or PageGuard counted a world join since - a re-join of the same world counts too) is FORGOTTEN like Esc
    (PageGuard.forget = PageManager.handleEvent Dismiss: no packet, counter unchanged) instead of setPage(None) / rebuild().
 2. PageGuard - THE GENERIC GUARD (every page of every mod; SkyyMenu is in every SkyWynn pack): an AddPlayerToWorldEvent listener
    (registerGlobal, like the engine's own PluginManager / AssetModule listeners). The page a player still has on the server when the
    engine adds them to a world is by construction from before the world change:
      - its onDismiss is the engine's empty CustomUIPage.onDismiss (SkyyMenu's three pages and most pages): forgotten right there,
        PageManager.handleEvent(null, null, Dismiss) - no page code runs, no packet, the counter untouched - before onSetupPlayerJoining
        and before anything of the new world can run, so no later setPage can add an unacknowledged count because of it;
      - it has its OWN onDismiss (SkyyBank, SkyyVault, SkyyEssentials trade, SkyyProfiles, vanilla Respawn / preview pages - some of
        them use ref / store): StaleTask forgets it on the new world's thread as soon as the player is in that world's store, with the
        player's real ref / store (the arguments the engine itself would pass at the next page action there), only while it is still
        that exact page (polled every 50 ms through the scheduler, at most 40 s: the engine waits up to 30 s for the client's chunks).
    It also counts world joins per player (JOINS, dropped at disconnect) for changedWorld.
 3. MenuWatch - the safety net, BankWatch's pattern (SkyyBank 0.1.6), for SkyyMenu's own menu page only: every 1 s while a menu is open
    (scheduler -> the player's world thread): closed / replaced -> done; changed world -> forget (no packet); 1 s after the menu's last
    packet a test click through the engine's own gate; dropped -> clearCustomPageAcknowledgements (the public reset the engine runs at
    a world change) + an answer (the menu redrawn with a status line; at most HEAL_ANSWERS = 3 answers per menu, later heals reset
    silently - never a periodic page update). A healthy menu sends nothing. NOT generic on purpose: a net for every page would need test
    clicks into other mods' pages (their handlers would act on them) or the engine's private counter field - neither is safe. A healed
    counter frees every page, so "open the SkyWynn Menu" un-sticks the whole UI.
 Plugin: setup() sets PageGuard.STOP = false + PageGuard.EXEC = HytaleServer.SCHEDULED_EXECUTOR (the timers' scheduler, BankWatch.EXEC
 pattern) and registers PageGuard; shutdown() sets PageGuard.STOP; MenuQuit drops JOINS of the leaving player.

DATA / TEXT (4): the Mods list = tools/deploy_set.py SET of 2026-10-03 (25 mods incl. SkyyMenu): NEW entry SkyyWorldGen 0.1 (admin-only
/zone, Server Setup -> World Gen); bumps Hud 0.3.12 (combat indicator), Bank 0.1.6, Gear 0.2.1 (damage / armor by level), Skills 0.4.14
(kill XP by mob level, early gathering, roll landings), Accessories 0.5.3 (Night Vision), Cooking 0.1.4 (+32% per Grade), UiProbe 0.3.1,
Mobs 0.1.2 (difficulty ladder, health floor). No new player switch or Server Setup title besides World Gen (the build's live-set check).

NOT CHANGED: SettingsPage, AdminPage (their guard-first order), the menu look, every other class (the harness byte-compares), the config
kit pin (1.1), MENU_ITEM_DESC (item / lang files byte-identical), SET_KNOWN, ROUND_PINS / ROUND_RETIRED (empty: deploys on its own).

Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.5 outside them, byte for byte.
CHECKED: see CHECKED below (filled in after SkyyMenu/test_skyymenu_0.3.6.py passed).
"""
import os
import re
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.5.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.6.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.5"' in s and "0.3.5: DATA / TEXT REFRESH ONLY" in s, "not the generated 0.3.5 script"
assert "@@" not in s, "0.3.5 already holds a @@ token"
CHANGES = []            # (new text, old text) of every change, in order: undone at the end


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


TOKEN_RE = re.compile(r"@@[A-Z0-9]+@@")


def fill(template, values):
    """@@NAME@@ replacement: every token of `values` occurs exactly once, no value holds "@@", none is left over"""
    for name, value in values.items():
        tok = "@@%s@@" % name
        assert template.count(tok) == 1, "token %s occurs %d times" % (tok, template.count(tok))
        assert "@@" not in value, "the value for %s holds '@@'" % tok
        template = template.replace(tok, value)
    left = TOKEN_RE.findall(template)
    assert not left, "tokens left unfilled: %s" % left
    return template


# THE ONE VERSION TABLE = tools/deploy_set.py SET of 2026-10-03 (SET order; SkyyMenu's own entry is VERSION). Bump here, regenerate, rebuild.
MODS_VERSIONS = [
    ("SkyyHud", "0.3.12"), ("SkyySacks", "0.7.12"), ("SkyyCoins", "0.1.5"), ("SkyyCollections", "0.2.5"), ("SkyyParty", "0.1.6"),
    ("SkyyBank", "0.1.6"), ("SkyyIslands", "0.5.5"), ("SkyyBazaar", "0.1.2"), ("SkyyGear", "0.2.1"), ("SkyySkills", "0.4.14"),
    ("SkyyAccessories", "0.5.3"), ("SkyyClasses", "0.1.10"), ("SkyyEssentials", "0.1.7"), ("SkyyProfiles", "0.1.5"),
    ("SkyyCooking", "0.1.4"), ("SkyyTrees", "0.2.5"), ("SkyyExploration", "0.2.2"), ("SkyyGuilds", "0.1.6"), ("SkyyVault", "0.1.5"),
    ("SkyyAuctions", "0.1.2"), ("SkyyRanks", "0.1.1"), ("SkyyUiProbe", "0.3.1"), ("SkyyMobs", "0.1.2"), ("SkyyWorldGen", "0.1"),
]
_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = [x for x in ast.literal_eval(_n.value) if x[0] != "SkyyMenu"]
assert len(set(m for m, v in MODS_VERSIONS)) == len(MODS_VERSIONS), "a mod is twice in MODS_VERSIONS"
if _set is not None and sorted(_set) != sorted(MODS_VERSIONS):
    print("NOTE: MODS_VERSIONS differs from tools/deploy_set.py SET now: table-only %s, SET-only %s" %
          (sorted(set(MODS_VERSIONS) - set(_set)), sorted(set(_set) - set(MODS_VERSIONS))))


def table_text(pairs):
    """the generated MODS_VERSIONS block: 5 mods per line (SET order) - the same layout as tools/menu_0_3_5_patch.py"""
    lines = []
    for i in range(0, len(pairs), 5):
        lines.append("    " + ", ".join('"%s": "%s"' % p for p in pairs[i:i + 5]) + ",")
    return "MODS_VERSIONS = {\n" + "\n".join(lines) + "\n}"


_blk = re.findall(r"^MODS_VERSIONS = \{\n.*?^\}", s, re.M | re.S)
assert len(_blk) == 1, "MODS_VERSIONS block: %d found" % len(_blk)

# ================================================================================================ docstring
DOC_NEW = '''"""SkyyMenu 0.1 - build script (javassist via jpype).
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
@@CHECKED@@
  UNVERIFIED (needs the game): the client dropping its page at JoinWorld (the 0.1.6 bank round's model, matches Skyy's client log); the
    menu's heal answer clearing a "Loading..." box (the bank's answer is the same kind of page update); the real timing of the 1 s checks
    for a remote player (a client slower than 1 s to acknowledge can make a check reset early - the engine's own "unexpected
    acknowledgement" line follows, harmless).
0.3.5: DATA / TEXT REFRESH ONLY'''
CHECKED = '''  CHECKED with SkyyMenu/test_skyymenu_0.3.6.py (committed - re-run it, it needs SkyyMenu-0.3.5.jar too) - 2026-10-03, 938 checks,
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
    (base-gated WrapMaxLines); tools/skyycfg_test.py PASS; tools/deploy_set.py --check all 25 jars present.'''
rep('"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF + "0.3.5: DATA / TEXT REFRESH ONLY", fill(DOC_NEW, {"CHECKED": CHECKED}))
rep('VERSION = "0.3.5"', 'VERSION = "0.3.6"')
rep('"set EXPECTED_KIT through tools/menu_0_3_5_patch.py (or its successor), regenerate, re-test"',
    '"set EXPECTED_KIT through tools/menu_0_3_6_patch.py (or its successor), regenerate, re-test"')

# ================================================================================================ the ONE version table
rep(_blk[0], table_text(MODS_VERSIONS))

# ================================================================================================ MODS texts
# SkyyHud 0.3.12: the Combat Indicator widget (red "In combat Ns" + a shrinking bar, hidden out of combat by default)
rep('''     "desc": "A customizable on-screen HUD: coordinates, zone, clocks, day counter, session timer, players online, coins, party, guild and skills (your Overall Level and the skills you pick in its Settings). Move, resize and colour every widget, save profiles or share your layout as a code.",''',
    '''     # 0.3.6: SkyyHud 0.3.12 - the Combat Indicator widget (red In combat + countdown + a shrinking bar; hidden out of combat by default)
     "desc": "A customizable on-screen HUD: coordinates, zone, clocks, day counter, session timer, players online, coins, party, guild, skills (your Overall Level and the skills you pick in its Settings) and a combat indicator (red with a countdown while you are in combat). Move, resize and colour every widget, save profiles or share your layout as a code.",''')
# SkyyGear 0.2.1: weapon damage and armor stats grow with the item level (stages 2-3); new Server Setup rows
rep('''     "setup": ("0.1", "Gear", "rarities, level bands, crafting levels, costs and odds"),''',
    '''     # 0.3.6: SkyyGear 0.2.1 (stages 2-3) - weapon damage and armor Health / resistance grow with the item's level
     "setup": ("0.1", "Gear", "rarities, level bands, damage and armor by level, costs"),''')
rep('''     "desc": "Rarity, level and modifiers on every weapon and armor piece. Each item has its own level - the class weapon skill you need to use it - and crafted gear comes out at your level within its material's band. Crafted gear rolls, mob and chest gear drops unidentified, /identify reveals it, /reforge rerolls it.",''',
    '''     "desc": "Rarity, level and modifiers on every weapon and armor piece. Each item has its own level - the class weapon skill you need to use it - and its damage or armor grows with that level. Crafted gear comes out at your level within its material's band and rolls, mob and chest gear drops unidentified, /identify reveals it, /reforge rerolls it.",''')
# SkyySkills 0.4.13 / 0.4.14: kill XP by mob level + gap rule, gathering XP x3 early, roll landings pay fall XP (no new command / switch)
rep('''     "desc": "Hypixel-style skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill (Archery, Swordsmanship, Sorcery, Fury or Divinity, on its own XP curve) - level up as you play and pay coins at every level up. Your Overall Level adds a little Health and Mana, and Mana refills in combat at half speed.",''',
    '''     # 0.3.6: SkyySkills 0.4.13 - 0.4.14 - kill XP by mob level + the level gap, gathering XP x3 to level 10, a rolled landing pays
     # fall XP, sickle swings pay Farming XP; Mana keeps refilling while charging - no new command, player switch or Server Setup title
     "desc": "Hypixel-style skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill (Archery, Swordsmanship, Sorcery, Fury or Divinity, on its own XP curve) - level up as you play and pay coins. Stronger mobs pay more kill XP and early gathering is faster. Your Overall Level adds Health and Mana, and Mana refills in combat at half speed.",''')
# SkyyAccessories 0.5.3: the Night Vision accessory (Rare, admin give), Server Setup -> Accessories -> Night Vision
rep('''     "setup": ("0.4.4", "Accessories", "bag slots, booster lines and numbers, notices"),''',
    '''     # 0.3.6: SkyyAccessories 0.5.3 - the Night Vision accessory (Rare, admin give only; its Server Setup rows under Accessories)
     "setup": ("0.4.4", "Accessories", "bag slots, booster lines, notices, Night Vision"),''')
rep('''     "desc": "Your Accessory Bag: 18 slots to start for bench accessories (each unlocks its bench tab in /craft, the Campfire one cooks on the go) and booster accessories - Health, Stamina, Mana, Regeneration, Speed and more - that work in the bag. Only the best rarity of each line counts. Craft them in the Workbench tab Accessories and Bags.",''',
    '''     "desc": "Your Accessory Bag: 18 slots to start for bench accessories (each unlocks its bench tab in /craft, the Campfire one cooks on the go) and booster accessories - Health, Stamina, Mana, Regeneration, Speed, Night Vision (an admin item for now) and more - that work in the bag. Only the best rarity of each line counts. Craft them in the Workbench tab Accessories and Bags.",''')
# SkyyCooking 0.1.4: Grade strength +32% per Grade, durations unchanged
rep('''     "desc": "Cooking: dishes you cook at a Cooking Bench get a Grade from your Cooking level and skill tree - higher Grades heal and buff more.",''',
    '''     # 0.3.6: SkyyCooking 0.1.4 - food strength +32% per Grade, buff durations as before (2^(Grade/5)), Cooking XP default x0.5
     "desc": "Cooking: dishes you cook at a Cooking Bench get a Grade from your Cooking level and skill tree - every Grade makes the food 32% stronger and its buffs last longer.",''')
# SkyyMobs 0.1.1 / 0.1.2: the difficulty ladder (Easy / Normal / Hard / Custom), the level health floor
rep('''     "setup": ("0.1", "Mobs", "difficulty, who gets levels, level bands, nameplates"),''',
    '''     # 0.3.6: SkyyMobs 0.1.1 - 0.1.2 - Difficulty Easy / Normal / Hard / Custom, the level health floor (row strength.floor, 50 HP)
     "setup": ("0.1", "Mobs", "difficulty, health floor, who gets levels, bands, plates"),''')
rep('''     "desc": "Mob levels: hostile mobs and neutral fighters get a level from the zone and biome they spawn in (Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60). Each level adds health and damage, and the nameplate shows it, like [Lv 9] Trork Warrior. Animals, traders, pets and bosses never get one.",
     "commands": ["/mobs (or /mobs info) - the mob level band where you stand"]},''',
    '''     "desc": "Mob levels: hostile mobs and neutral fighters get a level from the zone and biome they spawn in (Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60). Each level adds health and damage (Difficulty Easy, Normal or Hard in Server Setup), weak mobs get a health floor, and the nameplate shows it, like [Lv 9] Trork Warrior. Animals, traders, pets and bosses never get one.",
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
     "commands": ["No commands for players yet - the zone islands are an admin test."]},''')
rep('''# 0.3.4 / 0.3.5: EMPTY - this SkyyMenu deploys on its own; MODS names exactly what tools/deploy_set.py SET pins (the MODS_VERSIONS
# table above).''', '''# 0.3.4 / 0.3.5 / 0.3.6: EMPTY - this SkyyMenu deploys on its own; MODS names exactly what tools/deploy_set.py SET pins (the
# MODS_VERSIONS table above).''')

# ================================================================================================ build checks: 0.3.6 texts
rep('''assert "&" not in _alltext3, "no raw & in tooltip text (markup not proven)"''',
    '''assert "&" not in _alltext3, "no raw & in tooltip text (markup not proven)"
# 0.3.6: the help texts of the 2026-10-02 / 2026-10-03 builds (tools/menu_0_3_6_patch.py DATA / TEXT) - command names as SkyyWorldGen 0.1 defines them
_wg = _bym["SkyyWorldGen"]
assert _wg["check"] == "zone" and _wg["setup"][1] == "World Gen" and _wg["reload"] == "zone reload" \\
    and _wg["config"] == "Skyy_SkyyWorldGen/config.properties", "SkyyWorldGen: /zone, Server Setup World Gen, its config file"
for _sub in ("- ", "1 ", "info ", "leave ", "setlanding ", "reload "):
    assert [a for a in _wg["admin"] if a.startswith("/zone " + _sub) or ("| " + _sub.strip() + " ") in a], "SkyyWorldGen admin line /zone %s" % _sub
assert not [c for c in _wg["commands"] if "/zone" in c], "SkyyWorldGen 0.1: every /zone command is admin-only (no player Commands line)"
assert [m["mod"] for m in MODS].index("SkyyWorldGen") == [m["mod"] for m in MODS].index("SkyyMobs") + 1, "SkyyWorldGen right after SkyyMobs"
assert "combat indicator" in _bym["SkyyHud"]["desc"], "SkyyHud 0.3.12: the combat indicator"
assert "grows with that level" in _g["desc"] and "damage and armor by level" in _g["setup"][2], "SkyyGear 0.2.1: damage and armor by level"
assert "Stronger mobs pay more kill XP" in _bym["SkyySkills"]["desc"], "SkyySkills 0.4.14: kill XP by mob level"
assert "Night Vision" in _bym["SkyyAccessories"]["desc"] and "Night Vision" in _bym["SkyyAccessories"]["setup"][2], "SkyyAccessories 0.5.3: Night Vision"
assert "32% stronger" in _bym["SkyyCooking"]["desc"], "SkyyCooking 0.1.4: +32% per Grade"
assert "Difficulty Easy, Normal or Hard" in _mb["desc"] and "health floor" in _mb["desc"] and "health floor" in _mb["setup"][2], \\
    "SkyyMobs 0.1.1 - 0.1.2: difficulty ladder, health floor"
assert max(len(m["desc"]) for m in MODS) <= 390, "a Mods description is longer than 390 characters (the tooltip grows too tall; 0.3.5 max 350)"''')

# ================================================================================================ live-set check: patch name
rep('_PATCH = "tools/menu_0_3_5_patch.py"', '_PATCH = "tools/menu_0_3_6_patch.py"')

# ================================================================================================ engine types + probes
rep('''    "PERM": "com.hypixel.hytale.server.core.permissions.PermissionsModule",
}''', '''    "PERM": "com.hypixel.hytale.server.core.permissions.PermissionsModule",
    # 0.3.6: the stuck-page fix - the page event the engine itself handles (Dismiss / Data), the world of a store, the world-join event
    "EST":  "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "CPE":  "com.hypixel.hytale.protocol.packets.interface_.CustomPageEvent",
    "CPT":  "com.hypixel.hytale.protocol.packets.interface_.CustomPageEventType",
    "ATW":  "com.hypixel.hytale.server.core.event.events.player.AddPlayerToWorldEvent",
    "HLD":  "com.hypixel.hytale.component.Holder",
}''')
rep('''             (T["PERM"], "get"), (T["PERM"], "hasPermission")):
    B.probe(pool, c, m)
''', '''             (T["PERM"], "get"), (T["PERM"], "hasPermission")):
    B.probe(pool, c, m)
# 0.3.6: every engine member the stuck-page fix uses (all public; rebuild stays on 'this' inside MenuPage)
for c, m in ((T["PGM"], "handleEvent"), (T["PGM"], "clearCustomPageAcknowledgements"), (T["PAGE"], "onDismiss"), (T["CPE"], "type"),
             (T["CPE"], "data"), (T["CPT"], "Dismiss"), (T["CPT"], "Data"), (T["EST"], "getWorld"), (T["ST"], "getExternalData"),
             (T["ATW"], "getHolder"), (T["ATW"], "getWorld"), (T["HLD"], "getComponent"), (T["PR"], "getComponentType")):
    B.probe(pool, c, m)
''')
rep('''ref_ = mk("RefreshTask")
clo_ = mk("CloseTask")
''', '''ref_ = mk("RefreshTask")
clo_ = mk("CloseTask")
guard = mk("PageGuard")     # 0.3.6: the world-join page guard (AddPlayerToWorldEvent) + forget / joins helpers
stale = mk("StaleTask")     # 0.3.6: forgets a page that has its own onDismiss on the new world's thread
mwat = mk("MenuWatch")      # 0.3.6: the menu page's safety net (BankWatch pattern)
''')

# ================================================================================================ PageGuard, StaleTask, MenuWatch part 1
GUARD_SRC = r'''# ================= 0.3.6 PageGuard: THE WORLD-JOIN PAGE GUARD (tools/menu_0_3_6_patch.py) =================
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
M(guard, r"""
public static boolean forget(@PGM@ pm, @REF@ ref, @ST@ st, @PAGE@ page) {
  if (pm == null || page == null || pm.getCustomPage() != page) return false;
  pm.handleEvent(ref, st, new @CPE@(@CPT@.Dismiss, (String) null));
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

'''
rep('''# ================= MenuPage (inline page; views switched with rebuild()) =================
''', GUARD_SRC + '''# ================= MenuPage (inline page; views switched with rebuild()) =================
''')

# ================================================================================================ MenuPage: fields
rep('''          "public int pages;", "public boolean cleared;", "public String cfgArm;"):
    F(page, f)
''', '''          "public int pages;", "public boolean cleared;", "public String cfgArm;"):
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
F(page, "public static final long SETTLE = 1000L;")
F(page, "public static final int HEAL_ANSWERS = 3;")
''')

# ================================================================================================ MenuPage: who / changedWorld / watchFail
rep('''M(page, r"""
public void refresh() { rebuild(); }""")
''', '''M(page, r"""
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
''')

# ================================================================================================ RefreshTask: forget after a world change
rep('''    if (p == null || p.getPageManager().getCustomPage() != this.page) return;
    this.page.refresh();
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu refresh failed: " + t); }''',
    '''    if (p == null) return;
    @PGM@ pm = p.getPageManager();
    if (pm == null || pm.getCustomPage() != this.page) return;
    if (this.page.changedWorld(this.expected)) {
      if (@PKG@.PageGuard.forget(pm, r, st, this.page)) @PKG@.MenuUtil.info("the menu redraw after a command found the menu of " + @PKG@.PageGuard.who(this.pr) + " still open on the server after a world change - forgot it there too instead of redrawing it (no packet)");
      return;
    }
    this.page.refresh();
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu refresh failed: " + t); }''')
rep('''# ================= RefreshTask: re-draw the menu shortly after a keep-open command ran (world thread) =================
''', '''# ================= RefreshTask: re-draw the menu shortly after a keep-open command ran (world thread) =================
# 0.3.6: a menu the player no longer sees after a world change is forgotten (PageGuard.forget, no packet), never redrawn: a redraw of
# a page the client dropped is +1 page acknowledgement the client never sends (every page would ignore clicks)
''')

# ================================================================================================ MenuPage.build: world, joins, send time, check
rep('''public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.cleared = false;
  boolean tipsOff = ''', '''public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
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
  boolean tipsOff = ''')

# ================================================================================================ MenuPage.clearGrid: send time
rep('''    b.set("#SkyyMGrid.Slots", empty);
    sendUpdate(b);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not clear the menu grid: " + t); }''',
    '''    b.set("#SkyyMGrid.Slots", empty);
    sendUpdate(b);
    this.lastSend = System.currentTimeMillis();
  } catch (Throwable t) { @PKG@.MenuUtil.warn("could not clear the menu grid: " + t); }''')

# ================================================================================================ CloseTask: forget after a world change
rep('''# ================= CloseTask (0.1.2): close the menu after a command ONLY if the menu is still the open page =================
''', '''# ================= CloseTask (0.1.2): close the menu after a command ONLY if the menu is still the open page =================
# 0.3.6: ... and only if the player did not change world since the menu opened (the Island / Hub tile: this task runs on the NEW world,
# where the client shows no page any more). Such a menu is forgotten on the server like Esc (PageGuard.forget: no packet, counter
# unchanged); 0.3.5 closed it with setPage(None) = +1 page acknowledgement the client never sends -> every page ignored clicks.
''')
rep('''    if (p == null || p.getPageManager().getCustomPage() != this.page) return;
    this.page.closePage(r, st);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu close failed: " + t); }''',
    '''    if (p == null) return;
    @PGM@ pm = p.getPageManager();
    if (pm == null || pm.getCustomPage() != this.page) return;
    if (this.page.changedWorld(this.expected)) {
      if (@PKG@.PageGuard.forget(pm, r, st, this.page)) @PKG@.MenuUtil.info("the menu close after a command found the menu of " + @PKG@.PageGuard.who(this.pr) + " still open on the server after a world change - forgot it there too instead of closing it (no packet)");
      return;
    }
    this.page.closePage(r, st);
  } catch (Throwable t) { @PKG@.MenuUtil.warn("menu close failed: " + t); }''')

# ================================================================================================ MenuPage.handleDataEvent: the test click
rep('''    if (data == null) return;
    if (data.indexOf("mesc\\"") >= 0) { new @PKG@.CloseTask(this, this.playerRef).accept(null, null); return; }''',
    '''    if (data == null) return;
    if (data.indexOf("\\"skyymenucheck\\"") >= 0) {
      if (this.probeNonce != null && this.probeNonce.length() > 0 && data.indexOf("\\"" + this.probeNonce + "\\"") >= 0) this.probeSeen = true;
      return;
    }
    if (data.indexOf("mesc\\"") >= 0) { new @PKG@.CloseTask(this, this.playerRef).accept(null, null); return; }''')

# ================================================================================================ MenuPage.watchTick + MenuWatch part 2
HEAL_TEXT = "Clicks were stuck (a game hiccup after a teleport) - fixed. Click again."
assert '"' not in HEAL_TEXT and "\\" not in HEAL_TEXT and "@" not in HEAL_TEXT and len(HEAL_TEXT) <= 80
WATCH_SRC = r'''# ================= 0.3.6 MenuPage.watchTick: the menu's check, on the player's world thread (MenuWatch hands it here). true = again.
#  - the menu is no longer the open page (closed / replaced) -> done;
#  - the player changed world since it opened -> the client dropped it: forget it on the server (PageGuard.forget, no packet) -> done;
#  - SETTLE after the menu's last packet: a test click through the engine's own gate (PageManager.handleEvent Data -> this menu's
#    handleDataEvent only while customPageRequiredAcknowledgments == 0). It arrives -> healthy, nothing is sent. It does not -> the game
#    is dropping this menu's clicks: log, PageManager.clearCustomPageAcknowledgements() (what a world change runs) and, for the first
#    HEAL_ANSWERS heals of this menu, an answer (the menu redrawn with a status line) so a waiting client stops waiting; later heals
#    reset silently (never a periodic page update).
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
  if (t - this.lastSend < SETTLE) return true;
  this.probeNonce = Long.toHexString(System.nanoTime() ^ (((long) System.identityHashCode(this)) << 24));
  this.probeSeen = false;
  pm.handleEvent(ref, st, new @CPE@(@CPT@.Data, "{\"a\":\"skyymenucheck\",\"n\":\"" + this.probeNonce + "\"}"));
  if (this.probeSeen) return true;
  if (pm.getCustomPage() != this) return false;
  this.heals = this.heals + 1;
  boolean answer = this.heals <= HEAL_ANSWERS;
  if (this.heals <= 3 || this.heals % 60 == 0) @PKG@.MenuUtil.warn("the game was dropping " + @PKG@.PageGuard.who(this.playerRef) + "'s menu clicks (it still waited for a page acknowledgement the client will never send - e.g. a page update or close sent to a page the client no longer shows); reset the page acknowledgements" + (answer ? " and answered the menu" : "") + " (" + this.heals + ")");
  pm.clearCustomPageAcknowledgements();
  if (answer) {
    this.status = "@@HEAL@@";
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
  if (again && !@PKG@.PageGuard.STOP) schedule(this.page);
}""")

'''
rep('''# ================= 0.2 SettingsPage (research/Settings-Spec.md 4.2-4.4): one inline page, tabs / rows switched with rebuild() =================
''', WATCH_SRC.replace("@@HEAL@@", HEAL_TEXT) +
    '''# ================= 0.2 SettingsPage (research/Settings-Spec.md 4.2-4.4): one inline page, tabs / rows switched with rebuild() =================
''')

# ================================================================================================ MenuQuit: drop the join count
rep('''    @PKG@.Given.forget(pr.getUuid());
  } catch (Throwable t) { }
}""")
''', '''    @PKG@.Given.forget(pr.getUuid());
    @PKG@.PageGuard.JOINS.remove(pr.getUuid());
  } catch (Throwable t) { }
}""")
''')

# ================================================================================================ plugin
rep('''public void setup() {
  @PKG@.MenuUtil.LOG = getLogger();''', '''public void setup() {
  @PKG@.PageGuard.STOP = false;
  @PKG@.PageGuard.EXEC = @HSV@.SCHEDULED_EXECUTOR;
  @PKG@.MenuUtil.LOG = getLogger();''')
rep('''  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.MenuQuit());
''', '''  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.MenuQuit());
  getEventRegistry().registerGlobal(@ATW@.class, new @PKG@.PageGuard());
''')
rep('''; Server Setup: /modconfig (/serversetup) for admins");''',
    '''; Server Setup: /modconfig (/serversetup) for admins; page guard on (a page left open across a world change is forgotten at the join, no packet; the menu heals stuck page clicks)");''')
rep('''protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }''', '''protected void shutdown() {
  @PKG@.PageGuard.STOP = true;
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }''')
rep('''WRITE = (dat, utl, giv, mcfg, sreg, sst, ssv, tip, sld, sgf, srf, ssf, sdc, page, spg, apg, ast, ref_, clo_, fac,''',
    '''WRITE = (dat, utl, giv, mcfg, sreg, sst, ssv, tip, sld, sgf, srf, ssf, sdc, page, spg, apg, ast, ref_, clo_, guard, stale, mwat, fac,''')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
assert s.count("MODS_VERSIONS = {") == 1 and s.count('"version": MODS_VERSIONS["') == len(MODS_VERSIONS), \
    "every table mod has exactly one MODS entry"
assert not re.search(r'\{"mod": "Skyy\w+", "version": "', s), "a MODS entry still carries a literal version"
# javassist order (methods before callers): PageGuard helpers -> StaleTask -> PageGuard.accept -> MenuWatch.schedule -> MenuPage fields ->
# changedWorld (RefreshTask / CloseTask use it) -> build (MenuWatch.schedule) -> handleDataEvent -> watchTick -> MenuWatch.hop / run
_o = [s.index(x) for x in ("public static boolean forget(@PGM@ pm,", "public static boolean start(@PR@ pr, @PAGE@ page, @WLD@ target)",
                           "public void accept(Object ev) {\n  try {\n    if (STOP || !(ev instanceof @ATW@))", "public static void schedule(@PKG@.MenuPage page)",
                           'F(page, "public int joinSeen;")', "public boolean changedWorld(@WLD@ now)", "public RefreshTask(@PKG@.MenuPage page",
                           "public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {\n  this.cleared = false;",
                           "public CloseTask(@PKG@.MenuPage page", '"\\"skyymenucheck\\""', "public boolean watchTick(@WLD@ now)",
                           "public void hop() {\n  if (@PKG@.PageGuard.STOP) return;")]
assert _o == sorted(_o), "javassist order of the 0.3.6 pieces: %s" % _o
# the three SkyyMenu pages keep the engine's empty onDismiss (PageGuard forgets them at once at a world join, no page code runs)
assert "void onDismiss(" not in s, "a SkyyMenu page overrides onDismiss - PageGuard would then defer it instead of forgetting it at once"
assert s.count(".setPage(") == OLD.count(".setPage(") and s.count("rebuild();") == OLD.count("rebuild();") + 1, \
    "0.3.6 adds no setPage call and exactly one rebuild (the heal answer)"
# nothing outside the recorded changes moved: undo them (newest first) and get 0.3.5 back, byte for byte
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.5 outside the recorded changes"
compile(s, dst, "exec")
out = s.replace(LF, NL) if NL != LF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.5 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
