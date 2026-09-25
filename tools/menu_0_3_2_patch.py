"""Derive SkyyMenu/build_skyymenu_0.3.2.py from SkyyMenu 0.3.1 (python tools/menu_0_3_2_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: 0.3 -> tools/menu_0_3_1_patch.py -> 0.3.1 -> this patch -> 0.3.2.

0.3.2 = SkyyMenu 0.3.1 brought up to round 6 (live 2026-09-25 07:11: SkyyClasses 0.1.6 + SkyySkills 0.4.4 + SkyyProfiles 0.1.2 =
Berserker / Fury, Priest / Divinity, class kits) and SkyyTrees 0.2.3 (06:53). MENU DATA and build checks only - no Java method, page
layout, bridge key, file, node, command or default changes:

 1. CLASS TEXTS name the 7-class roster of SkyyClasses 0.1.6: Archer, Warrior, Mage, Berserker, Priest playable; Assassin, Shaman
    later - and the weapon skills Archery, Swordsmanship, Sorcery, Fury, Divinity:
     - Mods list SkyyClasses 0.1.6: description (the five playable classes, Priest = the party healer, Assassin and Shaman later, own
       weapons + weapon skill + a kit with its basic weapon); Commands gain "/class kit" (players); the new "admin" list (admins only,
       Mods view tooltip + info box under "Admin only:", and the Server Setup file-only page) holds "/classadmin kit <player> [class]"
       - the 0.3.1 rule: "(admin)" lines already under Commands stay there, the admin list takes only admin commands the list did not
       show; /classadmin info says "class and kit data" (0.1.6 shows the kit state there). Server Setup text: "weapon lock, class
       picker, class kits, Priest heal" (0.1.6's four categories).
     - Mods list SkyySkills: the description names the five class weapon skills; Server Setup text adds "Divinity heal XP" (0.4.4's
       divinity.* rows).
     - Mods list SkyyProfiles 0.1.2: the description names the five playable classes and the class kit a new profile starts with;
       "/profiles create" says "pick its class, get its kit".
     - Menu entry Skills (main slot 15): "your class weapon skill (Archery, Swordsmanship, Sorcery, Fury or Divinity)".
     - Settings tab Combat & Classes, the always-shown line: + "your class kit" (0.1.6's kit popup + chat line are not toggleable).
 2. MODS VERSIONS follow tools/deploy_set.py SET: Classes 0.1.6, Profiles 0.1.2, Trees 0.2.3 (Server Setup text + "tool swings", 0.2.3's
    swing.enabled row) and SkyySkills 0.4.5 = THIS ROUND's pin (research/Crossbow-Loaded-Spec.md: crossbows stay loaded, Archery level-5
    reward; no new command, player switch or Server Setup page title - "Nothing else changes: not ... SkyyMenu") and SkyyGuilds 0.1.3 =
    also this round (tools/guilds_0_1_3_patch.py: Fury + Divinity count for guild XP; same commands, switches, page title - its MODS
    text already says "guild XP from your skills"). New ROUND_PINS ({"SkyySkills": ("0.4.4", "0.4.5"), "SkyyGuilds": ("0.1.2",
    "0.1.3")}): the live-set cross-check accepts a MODS version equal to SET's, or equal to the round's pin while SET still pins the
    version the round replaces (printed as "note (this round): ..."), and reads the round's build script for the switch / Server Setup
    checks as soon as it exists (the SET version's script until then, with a note). Anything else is a WARNING as in 0.3.1. Once SET
    pins the round's version the entry is inert (MODS = SET); the next SkyyMenu drops it. If the round does NOT pin one of them, set
    that MODS version back to SET's and drop its ROUND_PINS entry (only the "not installed" fallback text shows the static version).
    Review fix (2026-09-25): SkyyGuilds 0.1.3 was questioned as unasked-for coupling. Kept: it is one of this round's (r7) three patch
    mods (tools/guilds_0_1_3_patch.py, checked under tools/dev/scratch/r7-skyyguilds; HANDOFF's round-6 follow-ups name the Guilds
    xpSkills gap next to this menu text), exactly like SkyySkills 0.4.5. So that a wrong pin can never ride along silently: every round
    note now names its two-line revert, and once SET pins SkyyMenu at this VERSION or newer (the round is pinned), a ROUND_PINS entry
    whose mod SET still pins at the replaced version is a WARNING ("the round went without ..."), not a note.
    r7 cross-check fix: SkyyVault 0.1.1 -> 0.1.2 (SET pins it since 07:47; the build warned); its fallback Server Setup text names the
    page arrows. Nothing else of its entry changes (0.1.2 keeps 0.1.1's commands, files and page title).
 3. PLAYER SWITCHES: SkyyClasses 0.1.6's classes.healGiven + classes.healTaken (its exact regSetting texts, tab combat, default ON) join
    SET_KNOWN after classes.blockedPopup - so SET_ORDER, the settings-defaults.properties template (written only when the file is
    missing; an existing file keeps its lines - the Server Setup defaults table lists every known + registered switch anyway) and the
    defaults table order know them. Compared against EVERY regSetting in the newest build script of every SET mod (and the in-progress
    round scripts): those two were the only missing keys. SkyySkills 0.4.4 registers NO Fury / Divinity switch (its six regSetting
    calls are the 0.4.3 ones: skills.xpGain, levelUp, doubleDrop, extraPotion, combatHints, rewards.late) - the Divinity-related player
    switches are the two Priest heal lines above. Combat & Classes now has 4 rows (one page).
 4. BUILD CHECKS (new): CLASS_PLAYABLE / CLASS_LATER / CLASS_SKILLS (MENU DATA) must appear in the SkyyClasses, SkyyProfiles and
    SkyySkills descriptions and the Skills entry, the old "Archer, Warrior or Mage" wording nowhere, /class kit under Commands and
    /classadmin kit in the admin list (hard asserts); the live-set cross-check also reads the CLASSES roster of the SkyyClasses build
    script SET pins (name, weapon skill, enabled) and WARNs when it differs from those three lists; a tab's always-shown line <= 121
    characters (one unwrapped 26 px label; 121 = the General line, the longest one 0.3.1 shows; Combat's new line is 118).
 5. The config kit stays PINNED at kit 1.1 (EXPECTED_KIT, inherited from 0.3.1); its messages now name this patch.

NOT CHANGED: every other MODS entry, every Java method, the Settings / Server Setup / Mods pages, the kit, the three refusing switches
(party.invites, tpa.requests, msg.private stay unbuilt). The new "admin" line and the Classes texts use only the 0.3.1 code paths
(MenuUtil.modBodyFor, AdminPage.drawFileOnly), so no instrumented re-test of those paths is needed beyond the build's own asserts.
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.1.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.2.py")
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


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF + "0.3.1: menu data brought up to the live set",
    '"""SkyyMenu 0.1 - build script (javassist via jpype).' + LF +
    "0.3.2: menu data for round 6 (Berserker / Fury, Priest / Divinity, class kits): every class text names the 7-class roster (Archer," + LF +
    "       Warrior, Mage, Berserker, Priest playable; Assassin, Shaman later) and the weapon skills; SkyyClasses /class kit + the admin" + LF +
    "       line /classadmin kit; Mods list versions = tools/deploy_set.py SET (SkyySkills 0.4.5 + SkyyGuilds 0.1.3 = the round's pins," + LF +
    "       ROUND_PINS); the Priest heal switches classes.healGiven / healTaken in the known list and the defaults template; roster checks." + LF +
    "       Notes: tools/menu_0_3_2_patch.py." + LF +
    "0.3.1: menu data brought up to the live set")
rep('VERSION = "0.3.1"', 'VERSION = "0.3.2"')

# ---------------------------------------------------------------------------------------------------------------- the kit pin names this patch
rep("# 0.3.1: the config kit this jar carries (tools/menu_0_3_1_patch.py pins it; see the \"config kit\" lines of the build output)",
    "# 0.3.1: the config kit this jar carries (tools/menu_0_3_1_patch.py pins it, 0.3.2 keeps the pin - change it with a rep in" + LF +
    "# tools/menu_0_3_2_patch.py; see the \"config kit\" lines of the build output)")
rep('"set EXPECTED_KIT in tools/menu_0_3_1_patch.py, regenerate, re-test"',
    '"set EXPECTED_KIT through tools/menu_0_3_2_patch.py (or its successor), regenerate, re-test"')

# ---------------------------------------------------------------------------------------------------------------- menu entry: Skills
rep('''        ["Your skill levels and XP: gathering, your class weapon skill and more. Every level up pays coins.", "Command: /skills"],''',
    '''        ["Your skill levels and XP: gathering, your class weapon skill (Archery, Swordsmanship, Sorcery, Fury or Divinity) and more. "
         "Every level up pays coins.", "Command: /skills"],''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyProfiles 0.1.2
rep('''    {"mod": "SkyyProfiles", "version": "0.1.1", "icon": "Deco_Book_Pile_Large", "check": "profiles",''',
    '''    {"mod": "SkyyProfiles", "version": "0.1.2", "icon": "Deco_Book_Pile_Large", "check": "profiles",''')
rep('''     "desc": "SkyBlock-style profiles: each profile is its own save with its own class, island, inventory, coins, bank, bags, skills and collections.",
     "commands": ["/profiles (or /profile) - open your profiles", "/profiles create (or new) - a new profile, pick its class",''',
    '''     "desc": "SkyBlock-style profiles: each profile is its own save with its own class (Archer, Warrior, Mage, Berserker or Priest), island, inventory, coins, bank, bags, skills and collections. A new profile starts with its class kit.",
     "commands": ["/profiles (or /profile) - open your profiles", "/profiles create (or new) - a new profile: pick its class, get its kit",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyySkills 0.4.5 (round pin)
rep('''    {"mod": "SkyySkills", "version": "0.4.3", "icon": "Weapon_Sword_Iron", "check": "skills",
     "config": "Skyy_SkyySkills/xp.properties", "reload": "skills reload", "note": "",
     "setup": ("0.4.3", "Skills", "levels, XP rates, perks, parts on or off"),
     "desc": "Hypixel-style skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill - that level up as you play and pay coins on every level up.",''',
    '''    # 0.3.2: 0.4.5 = this round's pin (ROUND_PINS below; SET pins 0.4.4 until the round deploys). 0.4.4 added Fury + Divinity (Divinity
    # XP from Priest heals, divinity.* rows), 0.4.5 crossbows stay loaded (Archery level 5): no new command, switch or page title
    {"mod": "SkyySkills", "version": "0.4.5", "icon": "Weapon_Sword_Iron", "check": "skills",
     "config": "Skyy_SkyySkills/xp.properties", "reload": "skills reload", "note": "",
     "setup": ("0.4.3", "Skills", "levels, XP rates, perks, Divinity heal XP, parts on or off"),
     "desc": "Hypixel-style skills - Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class weapon skill (Archery, Swordsmanship, Sorcery, Fury or Divinity) - that level up as you play and pay coins on every level up.",''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyTrees 0.2.3
rep('''    {"mod": "SkyyTrees", "version": "0.2.2", "icon": "Plant_Sapling_Maple", "check": "tree",
     "config": "Skyy_SkyyTrees/trees.properties", "reload": "tree reload", "note": "",
     "setup": ("0.2.2", "Trees", "node values, Dust, Tree Feller, Vein Burst"),''',
    '''    {"mod": "SkyyTrees", "version": "0.2.3", "icon": "Plant_Sapling_Maple", "check": "tree",
     "config": "Skyy_SkyyTrees/trees.properties", "reload": "tree reload", "note": "",
     "setup": ("0.2.2", "Trees", "node values, Dust, Tree Feller, Vein Burst, tool swings"),''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyClasses 0.1.6
rep('''    {"mod": "SkyyClasses", "version": "0.1.5", "icon": "Weapon_Shortbow_Iron", "check": "class",
     "config": "Skyy_SkyyClasses/config.properties", "reload": "classadmin reload", "note": "",
     "setup": ("0.1.5", "Classes", "the weapon lock and the class picker"),
     "desc": "Classes: Archer, Warrior or Mage (Assassin and Shaman later). With SkyyProfiles the class is picked when you create a profile and locked to it.",
     "commands": ["/class (or /classes) - open the class page", "/classadmin set <player> <class> - (admin) give a class",
                  "/classadmin reset <player> - (admin) remove a class", "/classadmin info <player> - (admin) class data",
                  "/classadmin reload - (admin) re-read the settings"]},''',
    '''    # 0.3.2: SkyyClasses 0.1.6 (round 6): Berserker (Fury) + Priest (Divinity) playable, class kits (/class kit, /classadmin kit)
    {"mod": "SkyyClasses", "version": "0.1.6", "icon": "Weapon_Shortbow_Iron", "check": "class",
     "config": "Skyy_SkyyClasses/config.properties", "reload": "classadmin reload", "note": "",
     "setup": ("0.1.5", "Classes", "weapon lock, class picker, class kits, Priest heal"),
     "admin": ["/classadmin kit <player> [class] - (admin) give a player a class kit now"],
     "desc": "Classes: Archer, Warrior, Mage, Berserker or Priest (the party healer) - Assassin and Shaman later. Each class has its own weapons and weapon skill and a kit with its basic weapon. With SkyyProfiles the class is picked when you create a profile.",
     "commands": ["/class (or /classes) - open the class page",
                  "/class kit - collect kit items that did not fit (or see your kit)",
                  "/classadmin set <player> <class> - (admin) give a class",
                  "/classadmin reset <player> - (admin) remove a class", "/classadmin info <player> - (admin) class and kit data",
                  "/classadmin reload - (admin) re-read the settings"]},''')

# ---------------------------------------------------------------------------------------------------------------- Settings: combat tab, heal switches
rep('''    ("combat",      "Combat",      "Combat & Classes",   "Always shown: the reminder to pick a class and admin changes to your class. Blocked hits stay blocked."),''',
    '''    ("combat",      "Combat",      "Combat & Classes",   "Always shown: the reminder to pick a class, your class kit and admin changes to your class. Blocked hits stay blocked."),''')
rep('''    ("classes.blockedPopup", "combat",      "Blocked weapon - popup",       "The popup with the weapon's icon - at most every 1.5 s", "SkyyClasses"),''',
    '''    ("classes.blockedPopup", "combat",      "Blocked weapon - popup",       "The popup with the weapon's icon - at most every 1.5 s", "SkyyClasses"),
    # 0.3.2: SkyyClasses 0.1.6's two Priest heal lines (its regSetting texts, category combat, default ON; the heal itself always happens)
    ("classes.healGiven",    "combat",      "Priest heals - your heals",    "Your heals: +23 HP to 2 party members and +6 HP to you - one line every 5 s at most", "SkyyClasses"),
    ("classes.healTaken",    "combat",      "Priest heals - healed by others", "Skyy healed you +12 HP - one line every 5 s at most. The heal happens either way", "SkyyClasses"),''')

# ---------------------------------------------------------------------------------------------------------------- MENU DATA: roster + round pins
rep('''TIPS_KEY = "menu.tooltips"      # the 0.1.3 Hover Tooltips book (slot 8) and the Settings row are this one key''',
    '''TIPS_KEY = "menu.tooltips"      # the 0.1.3 Hover Tooltips book (slot 8) and the Settings row are this one key
# ---- 0.3.2: the class roster every class text names (SkyyClasses 0.1.6 CLASSES, in its display order; the build checks the texts
# against these lists and the live-set cross-check checks these lists against the SkyyClasses build script SET pins)
CLASS_PLAYABLE = ["Archer", "Warrior", "Mage", "Berserker", "Priest"]
CLASS_LATER    = ["Assassin", "Shaman"]
CLASS_SKILLS   = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity"]      # the weapon skill of each CLASS_PLAYABLE class
# ---- 0.3.2: versions THIS round pins that tools/deploy_set.py SET does not carry yet (they deploy together with this SkyyMenu):
# mod: (the SET version the round replaces, the round's version). MODS may already name the round's version; the live-set cross-check
# accepts it while SET still pins the replaced version and reads the round's build script once it exists. Inert once SET pins it.
ROUND_PINS = {"SkyySkills": ("0.4.4", "0.4.5"), "SkyyGuilds": ("0.1.2", "0.1.3")}''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyVault 0.1.2
# r7 cross-check fix (2026-09-25): SET pins SkyyVault 0.1.2 (deployed 07:47, after this patch was first written) - the build warned
# "SkyyVault: MODS says 0.1.1, the live set runs 0.1.2". Version + the fallback Server Setup text (0.1.2's page-arrow rows); its
# commands, files and page title are 0.1.1's (build_skyyvault_0.1.2.py header: "commands, config rows ... unchanged" apart from the 3 rows).
rep('''    {"mod": "SkyyVault", "version": "0.1.1", "icon": "Furniture_Royal_Magic_Chest_Large", "check": "vault",
     "config": "Skyy_SkyyVault/config.properties", "reload": "vaultadmin reload", "note": "",
     "setup": ("0.1.1", "Vault", "free pages, page prices, page size, after-switch wait"),''',
    '''    {"mod": "SkyyVault", "version": "0.1.2", "icon": "Furniture_Royal_Magic_Chest_Large", "check": "vault",
     "config": "Skyy_SkyyVault/config.properties", "reload": "vaultadmin reload", "note": "",
     "setup": ("0.1.1", "Vault", "free pages, prices, page size, arrows, after-switch wait"),''')

# ---------------------------------------------------------------------------------------------------------------- MODS: SkyyGuilds 0.1.3 (round pin)
rep('''    {"mod": "SkyyGuilds", "version": "0.1.2", "icon": "Furniture_Outlander_Banner", "check": "guild",''',
    '''    # 0.3.2: 0.1.3 = this round's pin (ROUND_PINS): Fury + Divinity count for guild XP; same commands, switches and page title
    {"mod": "SkyyGuilds", "version": "0.1.3", "icon": "Furniture_Outlander_Banner", "check": "guild",''')

# ---------------------------------------------------------------------------------------------------------------- build checks: roster texts
ROSTER_CHECKS = r'''
# 0.3.2: every class text names the 7-class roster and the five weapon skills (CLASS_PLAYABLE / CLASS_LATER / CLASS_SKILLS)
assert len(CLASS_PLAYABLE) == len(CLASS_SKILLS) and not set(CLASS_PLAYABLE) & set(CLASS_LATER)
_bym = dict((m["mod"], m) for m in MODS)
for _n in CLASS_PLAYABLE + CLASS_LATER:
    assert _n in _bym["SkyyClasses"]["desc"], "SkyyClasses desc must name the class %s" % _n
assert "later" in _bym["SkyyClasses"]["desc"], "SkyyClasses desc must say which classes come later"
for _n in CLASS_PLAYABLE:
    assert _n in _bym["SkyyProfiles"]["desc"], "SkyyProfiles desc must name the playable class %s" % _n
_skills_entry = [e for e in ENTRIES if e[0] == "main" and e[3] == "Skills"]
assert len(_skills_entry) == 1, "one Skills entry in the main menu"
for _sk in CLASS_SKILLS:
    assert _sk in _bym["SkyySkills"]["desc"], "SkyySkills desc must name the class skill %s" % _sk
    assert _sk in _skills_entry[0][4][0], "the Skills menu entry must name the class skill %s" % _sk
assert [c for c in _bym["SkyyClasses"]["commands"] if c.startswith("/class kit ")], "SkyyClasses Commands list /class kit (players)"
assert [a for a in _bym["SkyyClasses"].get("admin", []) if a.startswith("/classadmin kit ")], "SkyyClasses admin lines list /classadmin kit"
assert not [c for c in _bym["SkyyClasses"]["commands"] if c.startswith("/classadmin kit")], "/classadmin kit is an admin-only line"
_alltext = " ".join([m["desc"] + " " + " ".join(m["commands"] + m.get("admin", [])) for m in MODS] +
                    [" ".join(e[4]) for e in ENTRIES] + [t[3] for t in SET_TABS] + [k[3] for k in SET_KNOWN])
assert "Warrior or Mage" not in _alltext, "the old 3-class wording is gone"
for _t in SET_TABS:
    assert len(_t[3]) <= 121, "always-shown line of tab %s is %d characters (one unwrapped label, max 121 = the General line of 0.3.1)" % (_t[0], len(_t[3]))
for _rm, (_rfrom, _rto) in ROUND_PINS.items():
    assert _rm in _bym and VER_RE.match(_rfrom) and VER_RE.match(_rto) and ver_t(_rfrom) < ver_t(_rto), "ROUND_PINS %s" % _rm
'''
rep("assert len(MODS) <= len(MOD_SLOTS), \"every mod fits on one Mods page (%d mods, %d slots)\" % (len(MODS), len(MOD_SLOTS))" + LF,
    "assert len(MODS) <= len(MOD_SLOTS), \"every mod fits on one Mods page (%d mods, %d slots)\" % (len(MODS), len(MOD_SLOTS))" + LF +
    ROSTER_CHECKS)

# ---------------------------------------------------------------------------------------------------------------- live-set cross-check: round pins + roster
rep("DRIFT = []" + LF, "DRIFT = []" + LF + "ROUND_NOTES = []        # 0.3.2: accepted round pins (ROUND_PINS) - printed as notes, never a WARNING" + LF)
rep("_live_keys = set()" + LF + "for _mod, _ver in _LIVE:" + LF,
    "_live_keys = set()" + LF + "CLASSES_SRC = None      # 0.3.2: the SkyyClasses build script the roster is checked against" + LF +
    "# 0.3.2 review: SET pins this SkyyMenu (or newer) = the round is pinned; a round pin SET still does not carry is then a WARNING" + LF +
    "_menu_pin = dict(_LIVE).get(\"SkyyMenu\", \"\")" + LF +
    "ROUND_PINNED = bool(VER_RE.match(_menu_pin)) and ver_t(_menu_pin) >= ver_t(VERSION)" + LF +
    "for _mod, _ver in _LIVE:" + LF)
rep('''    if _m["version"] != _ver:
        DRIFT.append("%s: MODS says %s, the live set runs %s" % (_mod, _m["version"], _ver))
    _p = os.path.join(B.PROJECT, _mod, "build_%s_%s.py" % (_mod.lower(), _ver))
    if not os.path.isfile(_p):
        DRIFT.append("%s: no build script %s" % (_mod, os.path.relpath(_p, B.PROJECT)))
        continue
    _t = open(_p, encoding="utf-8", errors="ignore").read()
''', '''    # 0.3.2: a round pin (ROUND_PINS) is accepted while SET still pins the version the round replaces; its script is read once it exists
    _rp = ROUND_PINS.get(_mod)
    _vers = [_ver]
    if _m["version"] != _ver:
        if _rp and _rp[0] == _ver and _m["version"] == _rp[1] and not ROUND_PINNED:
            ROUND_NOTES.append("%s: MODS says %s = this round's pin (tools/deploy_set.py SET pins %s until the round deploys; if the round "
                               "does not ship %s %s, set its MODS version back to %s and drop its ROUND_PINS entry in tools/menu_0_3_2_patch.py)" %
                               (_mod, _rp[1], _ver, _mod, _rp[1], _ver))
            _vers = [_rp[1], _ver]
        elif _rp and _rp[0] == _ver and _m["version"] == _rp[1]:
            DRIFT.append("%s: SET pins SkyyMenu %s but still %s %s - the round went without %s %s: set its MODS version back to %s and "
                         "drop its ROUND_PINS entry in tools/menu_0_3_2_patch.py" % (_mod, _menu_pin, _mod, _ver, _mod, _rp[1], _ver))
        else:
            DRIFT.append("%s: MODS says %s, the live set runs %s" % (_mod, _m["version"], _ver))
    _p = None
    for _v in _vers:
        _pv = os.path.join(B.PROJECT, _mod, "build_%s_%s.py" % (_mod.lower(), _v))
        if os.path.isfile(_pv):
            _p = _pv
            break
        if _v != _ver:
            ROUND_NOTES.append("%s %s: no build script yet (%s) - its switches and Server Setup title are checked against %s %s" %
                               (_mod, _v, os.path.relpath(_pv, B.PROJECT), _mod, _ver))
    if _p is None:
        DRIFT.append("%s: no build script %s" % (_mod, os.path.relpath(os.path.join(B.PROJECT, _mod, "build_%s_%s.py" % (_mod.lower(), _ver)), B.PROJECT)))
        continue
    _t = open(_p, encoding="utf-8", errors="ignore").read()
    if _mod == "SkyyClasses":
        CLASSES_SRC = _t
''')
rep('''for _k in SET_KNOWN:
    if _k[4] != "SkyyMenu" and _k[0] not in _live_keys:''',
    '''# 0.3.2: the roster the class texts name = the CLASSES list of the SkyyClasses build script SET pins (name, weapon skill, enabled)
_CL = re.findall(r'\\{"name": "(\\w+)", "skill": "([^"]+)", "color": "[^"]*", "enabled": (True|False)', CLASSES_SRC or "")
if not _CL:
    DRIFT.append("SkyyClasses: no CLASSES roster found in its live build script - check CLASS_PLAYABLE / CLASS_LATER / CLASS_SKILLS by hand")
else:
    _cp = [(_n, _sk) for _n, _sk, _en in _CL if _en == "True"]
    _cl = [_n for _n, _sk, _en in _CL if _en == "False"]
    if [_n for _n, _sk in _cp] != CLASS_PLAYABLE or [_sk for _n, _sk in _cp] != CLASS_SKILLS or _cl != CLASS_LATER:
        DRIFT.append("SkyyClasses roster is playable %s, later %s - CLASS_PLAYABLE / CLASS_SKILLS / CLASS_LATER and the class texts differ" %
                     (", ".join("%s (%s)" % x for x in _cp), ", ".join(_cl)))
for _k in SET_KNOWN:
    if _k[4] != "SkyyMenu" and _k[0] not in _live_keys:''')
rep('''for _d in DRIFT:
    print("WARNING menu data:", _d)
if DRIFT:
    print("WARNING: %d menu data difference(s) with the live set - update MENU DATA (tools/menu_0_3_1_patch.py or its successor)" % len(DRIFT))
else:
    print("menu data matches the live set (%d mods in tools/deploy_set.py SET, %d player switches registered by them)" % (len(_LIVE), len(_live_keys)))''',
    '''for _d in ROUND_NOTES:
    print("note (this round):", _d)
for _d in DRIFT:
    print("WARNING menu data:", _d)
if DRIFT:
    print("WARNING: %d menu data difference(s) with the live set - update MENU DATA (tools/menu_0_3_2_patch.py or its successor)" % len(DRIFT))
else:
    print("menu data matches the live set (%d mods in tools/deploy_set.py SET, %d player switches registered by them, roster %s; later %s%s)" %
          (len(_LIVE), len(_live_keys), ", ".join(CLASS_PLAYABLE), ", ".join(CLASS_LATER),
           "; round pins accepted: " + ", ".join("%s %s" % (k, v[1]) for k, v in sorted(ROUND_PINS.items())) if ROUND_NOTES else ""))''')

assert 'VERSION = "0.3.2"' in s and "Classes: Archer, Warrior or Mage" not in s and '"classes.healTaken"' in s
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
