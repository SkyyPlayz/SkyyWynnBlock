"""Derive SkyyMenu/build_skyymenu_0.3.5.py from the LIVE SkyyMenu 0.3.4 (python tools/menu_0_3_5_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: 0.3 -> menu_0_3_1_patch.py -> 0.3.1 -> ... -> menu_0_3_4_patch.py -> 0.3.4
(= the tools/deploy_set.py SET pin) -> this patch -> 0.3.5.

0.3.5 = DATA / TEXT REFRESH ONLY - no behaviour change (no Java method, page, command, node, bridge key, file or config row changes):

 1. THE MODS LIST = tools/deploy_set.py SET of 2026-10-02: 24 Skyy mods. Bumped: SkyyHud 0.3.11, SkyySacks 0.7.12, SkyyCollections
    0.2.5, SkyyIslands 0.5.5, SkyyGear 0.2, SkyySkills 0.4.12, SkyyAccessories 0.5.2, SkyyEssentials 0.1.7, SkyyGuilds 0.1.6, SkyyUiProbe
    0.3 (still a DEVELOPER / TEST mod: admin lines only); NEW entry SkyyMobs 0.1 (after SkyyGear). SkyyMenu's own entry stays VERSION.
 2. ONE VERSION TABLE (Skyy: "easy to bump"): the generated script carries MODS_VERSIONS = {mod: version} in its MENU DATA section and
    every MODS entry reads "version": MODS_VERSIONS["SkyyX"] (the build asserts the table and MODS name the same mods). The table is
    written from MODS_VERSIONS below, in SET order. TO BUMP A VERSION LATER: copy this patch to tools/menu_<ver>_patch.py, read the
    generated 0.3.5 script, replace its table with ONE rep of the block (the table line down to its closing brace; bump_table() below
    is that rep), regenerate, rebuild. The build's live-set check prints the table for the live SET (ready to paste) whenever a version
    differs. The harness (SkyyMenu/test_skyymenu_0.3.5.py) checks every jar version against tools/deploy_set.py SET.
 3. HELP TEXTS for what shipped on 2026-10-01 / 2026-10-02 - read off each mod's newest build script (command names, settings):
    SkyySacks 0.7.11 - 0.7.12 (stack refill on the /sacks page: Hotbar only / Full inventory / Off; bags of one type add up; vanilla
    benches, inventory crafting and /craft use the bags you carry), SkyyCollections 0.2.5 (coins never buy a tier, recipe or bag),
    SkyyEssentials 0.1.7 (Magic Bags + the Accessory Bag can't be traded), SkyyHud 0.3.11 (the Skills widget), SkyySkills 0.4.12 (class
    skills on their own XP curve, Mana refills in combat at half speed, admin /skills mana), SkyyGear 0.2 (each item's own level = its
    requirement, crafted at your level inside the material's band, admin /gear relevel [player]), SkyyMobs 0.1 (/mobs + /mobs info;
    admin /mobs inspect | set <level> | platetest | reload; Server Setup -> Mobs), SkyyUiProbe 0.3 (admin /skyprobe win | secgrid),
    SkyyAccessories 0.5.2 (the Workbench tab "Accessories & Bags" - written "Accessories and Bags": a raw & in tooltip markup is not
    proven), SkyyGuilds 0.1.6 (the leave / kick refund, 35% by default). Main menu: Pocket Dimension names the stack refill, Crafting says
    benches and inventory crafting use the bags too, Accessory Bag says booster accessories (stat talismans became boosters in 0.5).
    Server Setup fallback texts ("setup" = shown only while a mod publishes no config:def): Sacks, Skills, Gear, Mobs.
 4. BUILD CHECKS (no jar change): the live-set check reads a config kit emit whose MOD= is a module constant (SkyyMobs 0.1:
    CFG.emit(pool, PKG, MOD=MOD, TITLE="Mobs") with MOD = "SkyyMobs"); 0.3.5 text asserts; the paste-ready version table.

NOT CHANGED: every Java method body, every page look, MENU_ITEM_DESC (the item / lang files stay byte-identical), SET_KNOWN (no mod of
the 2026-10-02 set registers a new player switch - the build's live-set check proves it), ROUND_PINS / ROUND_RETIRED (empty: this
SkyyMenu deploys on its own), the config kit pin (1.1). Expected class changes vs 0.3.4: MenuData (the data), SkyyMenuPlugin + CfgRows +
CfgFn (the version string only), manifest.json - SkyyMenu/test_skyymenu_0.3.5.py K checks exactly that.

CHECKED (2026-10-02): build "assembled ...SkyyMenu-0.3.5.jar 178578 bytes" with "menu data matches the live set" and "... this round's
set" (24 mods, 42 player switches registered, 24 seconds rows); python tools/ci/lint.py 0 fails (26 warnings, all SkyySacks 0.7.12);
tools/skyyui_test.py 10060 ok + the 1 known stale fail (base-gated WrapMaxLines); tools/skyycfg_test.py PASS; the bare-JVM harness
SkyyMenu/test_skyymenu_0.3.5.py 748 ok, 0 fails (every 0.3.4 check, the jar versions = SET, the new texts, two starts on scratch COPIES
of the live Skyy_SkyyMenu data as it is today AND as 0.3.3 left it, the class byte-compare against SkyyMenu-0.3.4.jar: 33 of 37 classes
byte-identical, MenuData differs only in <clinit>); the same harness on the 0.3.4 jar fails exactly the stale versions / texts and K
(J passes there too: the start check no longer depends on the jar). A simulated SET bump (SkyyHud 0.3.12) makes the build's live-set
check name it and print the version table; a wrong SkyyMobs setup title is named through the MOD=MOD emit.
"""
import os
import re
import ast
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.4.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.5.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)

# THE ONE VERSION TABLE = tools/deploy_set.py SET of 2026-10-02 (SET order; SkyyMenu's own entry is VERSION). Bump here, regenerate, rebuild.
MODS_VERSIONS = [
    ("SkyyHud", "0.3.11"), ("SkyySacks", "0.7.12"), ("SkyyCoins", "0.1.5"), ("SkyyCollections", "0.2.5"), ("SkyyParty", "0.1.6"),
    ("SkyyBank", "0.1.5"), ("SkyyIslands", "0.5.5"), ("SkyyBazaar", "0.1.2"), ("SkyyGear", "0.2"), ("SkyySkills", "0.4.12"),
    ("SkyyAccessories", "0.5.2"), ("SkyyClasses", "0.1.10"), ("SkyyEssentials", "0.1.7"), ("SkyyProfiles", "0.1.5"),
    ("SkyyCooking", "0.1.3"), ("SkyyTrees", "0.2.5"), ("SkyyExploration", "0.2.2"), ("SkyyGuilds", "0.1.6"), ("SkyyVault", "0.1.5"),
    ("SkyyAuctions", "0.1.2"), ("SkyyRanks", "0.1.1"), ("SkyyUiProbe", "0.3"), ("SkyyMobs", "0.1"),
]
NEW_MODS = ["SkyyMobs"]          # MODS entries this patch ADDS (their entry is written with MODS_VERSIONS[...] already)


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


def table_text(pairs):
    """the generated MODS_VERSIONS block: 5 mods per line (SET order)"""
    lines = []
    for i in range(0, len(pairs), 5):
        lines.append("    " + ", ".join('"%s": "%s"' % p for p in pairs[i:i + 5]) + ",")
    return "MODS_VERSIONS = {\n" + "\n".join(lines) + "\n}"


def bump_table(text, pairs):
    """THE rep a later menu patch uses on a generated script that already has the table (0.3.5+): the whole block -> the new table"""
    blk = re.findall(r"^MODS_VERSIONS = \{\n.*?^\}", text, re.M | re.S)
    assert len(blk) == 1, "MODS_VERSIONS block: %d found" % len(blk)
    return text.replace(blk[0], table_text(pairs), 1)


# a note (never a stop) when this table and tools/deploy_set.py SET differ right now - the build's live-set check is the real gate
_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = [x for x in ast.literal_eval(_n.value) if x[0] != "SkyyMenu"]
assert len(set(m for m, v in MODS_VERSIONS)) == len(MODS_VERSIONS), "a mod is twice in MODS_VERSIONS"
if _set is not None and sorted(_set) != sorted(MODS_VERSIONS):
    print("NOTE: MODS_VERSIONS differs from tools/deploy_set.py SET now: table-only %s, SET-only %s" %
          (sorted(set(MODS_VERSIONS) - set(_set)), sorted(set(_set) - set(MODS_VERSIONS))))

# ---------------------------------------------------------------------------------------------------------------- header + version
rep('"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF + "0.3.4: Skyy's 2026-10-01 decisions",
    '"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF +
    "0.3.5: DATA / TEXT REFRESH ONLY (no behaviour change): the Mods list = tools/deploy_set.py SET of 2026-10-02 (24 Skyy mods: the NEW" + LF +
    "       SkyyMobs 0.1 entry, SkyyUiProbe 0.3 still a dev mod) through ONE version table, MODS_VERSIONS in MENU DATA (every MODS entry" + LF +
    "       reads it; the build prints the table for the live SET when a version differs); help texts for what shipped on 2026-10-01 /" + LF +
    "       2026-10-02 - Sacks stack refill / bags add up / benches + inventory crafting use the bags, Collections coins never buy tiers," + LF +
    "       Essentials no Magic Bags in /trade, Hud Skills widget, Skills class curve + in-combat Mana + /skills mana, Gear item levels +" + LF +
    "       /gear relevel, Mobs /mobs, UiProbe win / secgrid, Accessories Workbench tab, Guilds leave refund; the live-set check reads a" + LF +
    "       config kit emit with MOD=<module constant> (SkyyMobs). Notes: tools/menu_0_3_5_patch.py." + LF +
    "0.3.4: Skyy's 2026-10-01 decisions")
rep('VERSION = "0.3.4"', 'VERSION = "0.3.5"')
rep('"set EXPECTED_KIT through tools/menu_0_3_4_patch.py (or its successor), regenerate, re-test"',
    '"set EXPECTED_KIT through tools/menu_0_3_5_patch.py (or its successor), regenerate, re-test"')

# ---------------------------------------------------------------------------------------------------------------- the ONE version table
rep('''# Commands use the short positional forms (SkyyIslands 0.4.3, SkyyHud 0.3.6, SkyyBank 0.1.1, ... added usage variants / subcommands).
MODS = [''',
    '''# Commands use the short positional forms (SkyyIslands 0.4.3, SkyyHud 0.3.6, SkyyBank 0.1.1, ... added usage variants / subcommands).
# ---- 0.3.5: THE ONE VERSION TABLE of the Mods list = tools/deploy_set.py SET (SET order; SkyyMenu's own entry is VERSION). Every MODS
# entry below reads its "version" from here (asserted). To bump: the next tools/menu_<ver>_patch.py rewrites this one block (the table
# line down to its closing brace - tools/menu_0_3_5_patch.py bump_table), regenerate, rebuild; the build's live-set check names every
# difference and prints this table for the live SET.
''' + table_text(MODS_VERSIONS) + '''
MODS = [''')
_seen = []


def _to_table(m):
    _seen.append(m.group(2))
    return '%sMODS_VERSIONS["%s"]' % (m.group(1), m.group(2))


s = re.sub(r'(\{"mod": "(Skyy\w+)", "version": )"[\d.]+"', _to_table, s)
assert sorted(_seen) == sorted(m for m, v in MODS_VERSIONS if m not in NEW_MODS), \
    "MODS entries moved onto the table: %s" % sorted(set(_seen) ^ set(m for m, v in MODS_VERSIONS if m not in NEW_MODS))
assert '{"mod": "SkyyMenu", "version": VERSION,' in s

# ---------------------------------------------------------------------------------------------------------------- main menu entries
rep('''        ["Everything your Magic Bags swept up lives here. Pick items up or deposit them.",
         "Carry a bag to use its tab. A bag you lack shows how to craft it.",
         "Command: /sacks (or /pd, /bags)"], "Click to open!", "cmdc:sacks"),''',
    '''        ["Everything your Magic Bags swept up lives here. Pick items up or deposit them.",
         "Carry a bag to use its tab. A bag you lack shows how to craft it.",
         "Stack refill: Hotbar only, Full inventory or Off - pick it on that page.",
         "Command: /sacks (or /pd, /bags)"], "Click to open!", "cmdc:sacks"),''')
rep('''        ["Equip bench accessories and stat talismans - they work while they sit in the bag.", "Command: /accessories (or /acc)"],''',
    '''        ["Equip bench accessories and booster accessories - they work while they sit in the bag.", "Command: /accessories (or /acc)"],''')
rep('''        ["Craft from your inventory and your Magic Bags.", "Bench accessories in your Accessory Bag unlock that bench's recipes.",
         "Command: /craft"], "Click to open!", "cmdc:craft"),''',
    '''        ["Craft from your inventory and your Magic Bags.", "Bench accessories in your Accessory Bag unlock that bench's recipes.",
         "Vanilla benches and inventory crafting use the bags you carry too.",
         "Command: /craft"], "Click to open!", "cmdc:craft"),''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyySacks 0.7.12
rep('''     "setup": ("0.7.6", "Bags and Crafting", "craft search, bag caps by rarity, free bag recipes, Furnace"),
     "desc": "Magic Bags in four rarities (Normal, Unique, Rare, Legendary) send what you gather of their type - Mining, Foraging, Farming, Combat or Smithing - straight into your Pocket Dimension, and the Mythic Omni Bag does it for every type. Collections unlock the bag recipes. /craft crafts from your inventory and bags.",
     "commands": ["/sacks (or /pd, /bags) - your Pocket Dimension, missing bags show recipes",
                  "/craft (or /recipes) - craft from your inventory and bags", "/craft <words> - open crafting with a search"]},''',
    '''     # 0.3.5: SkyySacks 0.7.11 - 0.7.12 - the stack refill (a per-player choice on the bag page: Hotbar only = default / Full inventory /
     # Off; Server Setup bags.refill + bags.refillDefault), bags of one type ADD UP (the Omni adds to every type), vanilla benches and
     # inventory (pocket) crafting use the bags you carry (bags.pocketCraft, on); Charcoal goes in the Smithing bag (0.7.10)
     "setup": ("0.7.6", "Bags and Crafting", "bag caps, free recipes, stack refill, benches, Furnace"),
     "desc": "Magic Bags in four rarities (Normal, Unique, Rare, Legendary) send what you gather of their type - Mining, Foraging, Farming, Combat or Smithing - into your Pocket Dimension, and the Mythic Omni Bag does it for every type. Bags of one type add up. Collections unlock the bag recipes. Benches, inventory crafting and /craft use the bags you carry.",
     "commands": ["/sacks (or /pd, /bags) - your Pocket Dimension, missing bags show recipes",
                  "Stack refill (on the /sacks page): Hotbar only, Full inventory or Off",
                  "/craft (or /recipes) - craft from your inventory and bags", "/craft <words> - open crafting with a search"]},''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyAccessories 0.5.2
rep('''     "desc": "Your Accessory Bag: 18 slots to start for bench accessories (each unlocks its bench tab in /craft, the Campfire one cooks on the go) and booster accessories - Health, Stamina, Mana, Regeneration, Speed and more - that work while they sit in the bag. Only the best rarity of each line counts.",''',
    '''     # 0.3.5: SkyyAccessories 0.5.2 - every accessory and bag recipe in the Workbench tab "Accessories & Bags" (no & in tooltip text)
     "desc": "Your Accessory Bag: 18 slots to start for bench accessories (each unlocks its bench tab in /craft, the Campfire one cooks on the go) and booster accessories - Health, Stamina, Mana, Regeneration, Speed and more - that work in the bag. Only the best rarity of each line counts. Craft them in the Workbench tab Accessories and Bags.",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyHud 0.3.11
rep('''     "desc": "A customizable on-screen HUD: coordinates, zone, clocks, day counter, session timer, players online, coins, party and guild. Move, resize and colour every widget, save profiles or share your layout as a code.",''',
    '''     # 0.3.5: SkyyHud 0.3.11 - the Skills widget (Overall Level + any skills, each line on / off in the widget's Settings; Overall + class
     # skill by default) - no new command, player switch or Server Setup title
     "desc": "A customizable on-screen HUD: coordinates, zone, clocks, day counter, session timer, players online, coins, party, guild and skills (your Overall Level and the skills you pick in its Settings). Move, resize and colour every widget, save profiles or share your layout as a code.",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyySkills 0.4.12
rep('''     "setup": ("0.4.3", "Skills", "levels, XP rates, perks, Overall Level, Mana, parts on/off"),
     "desc": "Hypixel-style skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill (Archery, Swordsmanship, Sorcery, Fury or Divinity) - that level up as you play and pay coins on every level up. Your Overall Level adds a little Health and Mana.",
     "commands": ["/skills (or /skill) - open your Skills", "/skills stats <skill> - the Stats page of a skill (or overall)",
                  "/skills top <skill> - the top 10 players of a skill", "/skills quiet - hide the +XP chat messages",
                  "/skills reload - (admin) re-read the XP settings", "/skills xp <skill> <amount> - (admin) test XP"]},''',
    '''     # 0.3.5: SkyySkills 0.4.12 - class skills level on their OWN XP table (levels.class rows), in-combat Mana regen (default 50%,
     # row mana.regen.inCombat), the admin /skills mana (requirePermission skyyskills.admin); 0.4.11 Priest heal XP - no new player switch
     "setup": ("0.4.3", "Skills", "levels, class curve, XP rates, perks, Overall Level, Mana"),
     "desc": "Hypixel-style skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill (Archery, Swordsmanship, Sorcery, Fury or Divinity, on its own XP curve) - level up as you play and pay coins at every level up. Your Overall Level adds a little Health and Mana, and Mana refills in combat at half speed.",
     "commands": ["/skills (or /skill) - open your Skills", "/skills stats <skill> - the Stats page of a skill (or overall)",
                  "/skills top <skill> - the top 10 players of a skill", "/skills quiet - hide the +XP chat messages",
                  "/skills reload - (admin) re-read the XP settings", "/skills xp <skill> <amount> - (admin) test XP",
                  "/skills mana - (admin) your live Mana regen: in or out of combat, boosts"]},''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyCollections 0.2.5
rep('''     "desc": "Hypixel-style Collections: everything you gather counts toward tiers. Tiers unlock crafting recipes and pay rewards - each Magic Bag type climbs one collection: Normal, Unique, Rare and Legendary at tiers I, III, V and VII.",''',
    '''     # 0.3.5: SkyyCollections 0.2.5 - coins never buy a collection tier, a recipe unlock or a bag (Coin unlocks OFF by default; tiers
     # already bought stay) - no new command, switch or Server Setup title
     "desc": "Hypixel-style Collections: everything you gather counts toward tiers. Tiers unlock crafting recipes and pay rewards - each Magic Bag type climbs one collection: Normal, Unique, Rare and Legendary at tiers I, III, V and VII. Coins never buy a tier, recipe or bag.",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyGuilds 0.1.6
rep('''     "desc": "Guilds: found a guild with your friends - ranks, a shared guild bank, guild XP from your skills, guild levels and seasons. If a guild disbands, its bank goes back to the members by what each put in.",''',
    '''     # 0.3.5: SkyyGuilds 0.1.6 - a member who leaves or is kicked gets back part of their contribution (Server Setup Leave refund, 35%)
     "desc": "Guilds: found a guild with your friends - ranks, a shared guild bank, guild XP from your skills, guild levels and seasons. If a guild disbands, its bank goes back to the members by what each put in, and a member who leaves or is kicked gets part of theirs back (35% by default).",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyEssentials 0.1.7
rep('''     "desc": "Everyday commands the base game is missing: teleport requests between players, private messages and safe trades of items and coins. Turn teleport requests or private messages off in /settings (staff get through while privacy.staffBypass is on).",''',
    '''     # 0.3.5: SkyyEssentials 0.1.7 - Magic Bags + the Accessory Bag are blocked in /trade (Server Setup Essentials -> Trade list
     # tradeBlockedItems, the AH's list); 0.1.6 item durability switch (Server Setup only)
     "desc": "Everyday commands the base game is missing: teleport requests between players, private messages and safe trades of items and coins (Magic Bags and the Accessory Bag can't be traded). Turn teleport requests or private messages off in /settings (staff get through while privacy.staffBypass is on).",''')
rep('''                  "/trade <player> | claim - trade items and coins safely", "/fly - (staff) toggle flight"]},''',
    '''                  "/trade <player> | claim - trade items and coins safely (no Magic Bags)", "/fly - (staff) toggle flight"]},''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyGear 0.2 + SkyyMobs 0.1
rep('''     "setup": ("0.1", "Gear", "rarities, levels, costs and odds"),''',
    '''     # 0.3.5: SkyyGear 0.2 (stage 1 of the Wynn-style levels) - every item stores its own level = its requirement, crafted at your level
     # inside overlapping material bands; the admin /gear relevel [player]; 0.1.3 every world chest's gear unidentified
     "setup": ("0.1", "Gear", "rarities, level bands, crafting levels, costs and odds"),''')
rep('''               "/gear charged - (admin) charged attack probe for the held weapon"],
     "desc": "Rarity, level and modifiers on every weapon and armor piece: crafted gear rolls, mob and chest gear drops unidentified, /identify reveals it, /reforge rerolls it.",
     "commands": ["/reforge - reroll the modifiers of a weapon or armor piece for coins",
                  "/identify - reveal the modifiers of unidentified gear for coins",
                  "/gear - the held item's gear lines, your totals and your Smithing rarity"]},''',
    '''               "/gear charged - (admin) charged attack probe for the held weapon",
               "/gear relevel [player] - (admin) move stamped gear into today's level bands"],
     "desc": "Rarity, level and modifiers on every weapon and armor piece. Each item has its own level - the class weapon skill you need to use it - and crafted gear comes out at your level within its material's band. Crafted gear rolls, mob and chest gear drops unidentified, /identify reveals it, /reforge rerolls it.",
     "commands": ["/reforge - reroll the modifiers of a weapon or armor piece for coins",
                  "/identify - reveal the modifiers of unidentified gear for coins",
                  "/gear - the held item's gear lines, your totals and your Smithing rarity"]},
    # 0.3.5: SkyyMobs 0.1 (NEW, deployed 2026-10-02): mob levels by zone / biome. /mobs + /mobs info for every player (hytale:Adventurer);
    # /mobs inspect | set | platetest | reload need skyymobs.admin; Server Setup -> Mobs (config kit, MOD=MOD constant); no player switch
    {"mod": "SkyyMobs", "version": MODS_VERSIONS["SkyyMobs"], "icon": "Armor_Trork_Head", "check": "mobs",
     "config": "Skyy_SkyyMobs/config.properties,Skyy_SkyyMobs/bands.properties", "reload": "mobs reload", "note": "",
     "setup": ("0.1", "Mobs", "difficulty, who gets levels, level bands, nameplates"),
     "admin": ["/mobs inspect - (admin) level, band and lookup of the mob you look at",
               "/mobs set <level> - (admin) the level of the mob you look at (0 removes it)",
               "/mobs platetest - (admin) try the three nameplate colour markups",
               "/mobs reload - (admin) re-read config.properties and bands.properties"],
     "desc": "Mob levels: hostile mobs and neutral fighters get a level from the zone and biome they spawn in (Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60). Each level adds health and damage, and the nameplate shows it, like [Lv 9] Trork Warrior. Animals, traders, pets and bosses never get one.",
     "commands": ["/mobs (or /mobs info) - the mob level band where you stand"]},''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyUiProbe 0.3 (dev)
rep('''    # 0.3.4: SkyyUiProbe 0.2 is in tools/deploy_set.py SET as a DEVELOPER / TEST mod (the vanilla UI kit's probe pages, admins only:
    # requirePermission skyyuiprobe.admin). It moves to RETIRED once the probe results are in - then drop this entry.
    {"mod": "SkyyUiProbe", "version": MODS_VERSIONS["SkyyUiProbe"], "icon": "Ingredient_Crystal_Cyan", "check": "skyprobe",
     "config": "", "reload": "", "note": "A developer test mod - nothing to set up.",
     "admin": ["/skyprobe [n | name | list] - (admin) open the UI kit probe pages"],
     "desc": "Developer test mod, not a game feature: admins open the UI kit's probe pages to check that the vanilla look works in game.",''',
    '''    # 0.3.4: SkyyUiProbe 0.2 is in tools/deploy_set.py SET as a DEVELOPER / TEST mod (the vanilla UI kit's probe pages, admins only:
    # requirePermission skyyuiprobe.admin). It moves to RETIRED once the probe results are in - then drop this entry.
    # 0.3.5: SkyyUiProbe 0.3 - + the two vault window probes P1 /skyprobe win and P2 /skyprobe secgrid (probe pages 23 and 24)
    {"mod": "SkyyUiProbe", "version": MODS_VERSIONS["SkyyUiProbe"], "icon": "Ingredient_Crystal_Cyan", "check": "skyprobe",
     "config": "", "reload": "", "note": "A developer test mod - nothing to set up.",
     "admin": ["/skyprobe [n | name | list] - (admin) open the UI kit probe pages",
               "/skyprobe win | secgrid - (admin) the two vault window probes (23, 24)"],
     "desc": "Developer test mod, not a game feature: admins open the UI kit's probe pages and two vault window probes to check what works in game.",''')

# ---------------------------------------------------------------------------------------------------------------- round data comment
rep('''# 0.3.4: EMPTY - this SkyyMenu deploys on its own; MODS names exactly what tools/deploy_set.py SET pins (tools/menu_0_3_4_patch.py
# MODS_VERSIONS). To ship it together with e.g. SkyyGear 0.1.3: {"SkyyGear": ("0.1.2", "0.1.3")} + that version in MODS_VERSIONS.''',
    '''# 0.3.4 / 0.3.5: EMPTY - this SkyyMenu deploys on its own; MODS names exactly what tools/deploy_set.py SET pins (the MODS_VERSIONS
# table above). To ship it together with e.g. SkyyGear 0.2.1: {"SkyyGear": ("0.2", "0.2.1")} + that version in MODS_VERSIONS.''')

# ---------------------------------------------------------------------------------------------------------------- build checks: the table
rep('''VER_RE = re.compile(r"^\\d+(\\.\\d+){1,3}$")
def ver_t(v):
    return tuple(int(x) for x in v.split("."))''',
    '''VER_RE = re.compile(r"^\\d+(\\.\\d+){1,3}$")
def ver_t(v):
    return tuple(int(x) for x in v.split("."))
# 0.3.5: THE ONE VERSION TABLE - MODS_VERSIONS names exactly the MODS mods (SkyyMenu's own entry = VERSION) and every entry reads it
_tbl_mods = sorted(m["mod"] for m in MODS if m["mod"] != "SkyyMenu")
assert sorted(MODS_VERSIONS) == _tbl_mods, "MODS_VERSIONS and MODS name different mods: %s" % sorted(set(MODS_VERSIONS) ^ set(_tbl_mods))
for _m in MODS:
    _want = VERSION if _m["mod"] == "SkyyMenu" else MODS_VERSIONS[_m["mod"]]
    assert _m["version"] == _want and VER_RE.match(_want), "%s: version %r, the table says %r" % (_m["mod"], _m["version"], _want)''')

# ---------------------------------------------------------------------------------------------------------------- build checks: 0.3.5 texts
rep('''for _stale in ("type it twice", "on its way", "31 s", "world spawn", "SkyyRolls", "/rolls"):
    assert _stale not in _alltext3, "stale menu text: " + _stale''',
    '''for _stale in ("type it twice", "on its way", "31 s", "world spawn", "SkyyRolls", "/rolls"):
    assert _stale not in _alltext3, "stale menu text: " + _stale
# 0.3.5: the help texts of the 2026-10-01 / 2026-10-02 builds (tools/menu_0_3_5_patch.py 3) - command names as their build scripts define them
_mb = _bym["SkyyMobs"]
assert _mb["check"] == "mobs" and _mb["setup"][1] == "Mobs" and _mb["reload"] == "mobs reload", "SkyyMobs: /mobs, Server Setup Mobs"
assert [c for c in _mb["commands"] if c.startswith("/mobs (or /mobs info) ")], "SkyyMobs Commands: /mobs (or /mobs info)"
for _sub in ("inspect", "set", "platetest", "reload"):
    assert [a for a in _mb["admin"] if a.startswith("/mobs " + _sub + " ")], "SkyyMobs admin line /mobs %s" % _sub
assert [a for a in _g["admin"] if a.startswith("/gear relevel ")] and "its own level" in _g["desc"], "SkyyGear 0.2: item levels, /gear relevel"
assert [c for c in _bym["SkyySkills"]["commands"] if c.startswith("/skills mana ") and "(admin)" in c], "SkyySkills 0.4.12: /skills mana (admin)"
assert "own XP curve" in _bym["SkyySkills"]["desc"] and "in combat" in _bym["SkyySkills"]["desc"], "SkyySkills 0.4.12: class curve, combat Mana"
_upb = _bym["SkyyUiProbe"]
assert [a for a in _upb["admin"] if a.startswith("/skyprobe win | secgrid ")] and not [c for c in _upb["commands"] if "/skyprobe" in c], \\
    "SkyyUiProbe 0.3: /skyprobe win | secgrid, admins only"
_sk3 = _bym["SkyySacks"]
assert [c for c in _sk3["commands"] if c.startswith("Stack refill ")] and "add up" in _sk3["desc"] and "Benches, inventory crafting" in _sk3["desc"], \\
    "SkyySacks 0.7.11 - 0.7.12: stack refill, bags add up, benches + inventory crafting"
assert "Coins never buy" in _bym["SkyyCollections"]["desc"], "SkyyCollections 0.2.5: coins never buy tiers"
assert "can't be traded" in _ess["desc"] and [c for c in _ess["commands"] if c.startswith("/trade ") and "no Magic Bags" in c], \\
    "SkyyEssentials 0.1.7: no Magic Bags in /trade"
assert "skills" in _bym["SkyyHud"]["desc"] and "Overall Level" in _bym["SkyyHud"]["desc"], "SkyyHud 0.3.11: the Skills widget"
assert "Accessories and Bags" in _bym["SkyyAccessories"]["desc"] and "leaves or is kicked" in _bym["SkyyGuilds"]["desc"], \\
    "SkyyAccessories 0.5.2 Workbench tab, SkyyGuilds 0.1.6 leave refund"
assert "&" not in _alltext3, "no raw & in tooltip text (markup not proven)"''')

# ---------------------------------------------------------------------------------------------------------------- live-set check: MOD=<constant>
rep('''_EMIT = re.compile(r'\\.emit\\(\\s*pool\\s*,\\s*PKG\\s*,\\s*MOD\\s*=\\s*"(\\w+)"\\s*,\\s*TITLE\\s*=\\s*"([^"]+)"')
_PATCH = "tools/menu_0_3_4_patch.py"''',
    '''_EMIT = re.compile(r'\\.emit\\(\\s*pool\\s*,\\s*PKG\\s*,\\s*MOD\\s*=\\s*"(\\w+)"\\s*,\\s*TITLE\\s*=\\s*"([^"]+)"')
# 0.3.5: SkyyMobs 0.1 passes its module constant (CFG.emit(pool, PKG, MOD=MOD, TITLE="Mobs"), MOD = "SkyyMobs"): read that constant
_EMIT_VAR = re.compile(r'\\.emit\\(\\s*pool\\s*,\\s*PKG\\s*,\\s*MOD\\s*=\\s*([A-Za-z_]\\w*)\\s*,\\s*TITLE\\s*=\\s*"([^"]+)"')
_PATCH = "tools/menu_0_3_5_patch.py"


def _emits(t):
    """(MOD, TITLE) of every config kit emit of a build script: MOD="Name", or MOD=<module constant> = "Name" ("?<constant>" if unclear)"""
    out = list(_EMIT.findall(t))
    for _var, _title in _EMIT_VAR.findall(t):
        _c = re.findall(r'^%s\\s*=\\s*"(\\w+)"' % re.escape(_var), t, re.M)
        out.append((_c[0] if len(_c) == 1 else "?" + _var, _title))
    return out''')
rep('''        _em = _EMIT.findall(t)
        _st = m.get("setup")''',
    '''        _em = _emits(t)
        _st = m.get("setup")''')

# ---------------------------------------------------------------------------------------------------------------- live-set check: paste table
rep('''DRIFT = menu_report("the live set", _LIVE, _LIVE_RETIRED)''',
    '''DRIFT = menu_report("the live set", _LIVE, _LIVE_RETIRED)
# 0.3.5: a version differs -> the ONE table for the live SET, ready for the next tools/menu_<ver>_patch.py (nothing is written)
if [_d for _d in DRIFT if "the live set runs" in _d or "is live but not in MODS" in _d]:
    print("MODS_VERSIONS for the live set (paste into the next menu patch, then regenerate): {" +
          ", ".join('"%s": "%s"' % (_m, _v) for _m, _v in _LIVE if _m != "SkyyMenu") + "}")''')

# ---------------------------------------------------------------------------------------------------------------- self-checks
assert s.count("MODS_VERSIONS = {") == 1 and bump_table(s, MODS_VERSIONS) == s, "bump_table must rewrite exactly the generated table"
assert not re.search(r'\{"mod": "Skyy\w+", "version": "', s), "a MODS entry still carries a literal version"
assert s.count('"version": MODS_VERSIONS["') == len(MODS_VERSIONS), "every table mod has exactly one MODS entry"

out = s.replace(LF, NL) if NL != LF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines)" % out.count("\n"))
