"""Derive SkyyMenu/build_skyymenu_0.3.10.py from the LIVE SkyyMenu 0.3.9 (python tools/menu_0_3_10_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: 0.3 -> menu_0_3_1_patch.py -> ... -> menu_0_3_9_patch.py -> 0.3.9 (= the
tools/deploy_set.py SET pin, generated - never re-run its patch, never re-build it) -> this patch -> 0.3.10. 0.3.9's files stay untouched.

0.3.10 = THE STATS PAGE, phase 1 (research/cloud/Stats-Page-Spec.md part P1). Skyy's own words (docs/answered/ui.md 2026-10-03 + the
2026-10-08 chat on the SkyWynn Menu "Your Profile" tile):
  "this button should pull up a page with all your characters stats, and a button to change profiles."
  "this menus should show me all my stats with my current gear, accessory's skill and class bonuses. and everything. like on skyblock it
   should show health, mana, stamina, strength, crit chance, crit damage,"
  1. The Your Profile tile (main menu slot 4) OPENS the new Stats page (it only showed a cut-off text above the grid before). Its hover
     text is short lines now (class + Overall Level, purse, bank, top 3 skills, bag counts - each under 80 characters; the old one-line
     "Skills: Mining 6, Forag..." list was cut off).
  2. StatsPage: a vanilla-look INLINE page from the shared kit tools/skyyui.py (page_shell, labels, buttons, the well, the content
     separator - only properties the deployed kit pages use: SUI.assert_proven), 1100 x 900. Header = player, class, profile name,
     Overall Level. Five tabs (Main / Combat / Gathering / Skills / Profile; the active one Primary, the rest Secondary), one row per stat
     (name, total, where it comes from - the breakdown is the row's third column, not a hover: the kit's tooltip is UNVERIFIED),
     a note line per tab, a status line, footer < SkyWynn Menu / Refresh / Change Profile / Close. No periodic updates (Refresh button).
  3. Phase-1 sources only (spec 4.2; no other mod changes): Health / Mana / Stamina = the player's EntityStatMap max (world thread, in
     build) split by modifier key prefix (skyygear_ = Gear, skyyacc_ = Accessories, skyyskill_overall* = Overall Level, skyyskill_class*
     = Class, skyyskill_base* = Base Mana, skyyskill_* = Skills, skyytree_ = Trees; the rest = "base", shown when the row has room); gear stats
     from gear:stats:<uuid> + the accessory part gear:extra:<uuid> (LIVE SkyyGear rows only - the build cross-checks them against the
     SET SkyyGear script; planned stats are hidden); Speed / Jump / Fall Damage from the movement protocol map move:<uuid>
     (tools/skyymove.py formula); Mana Regen = skill:fn:manaregen; Fortune = today's double-drop chance (level x
     perk.<skill>.doubleDropPerLevel + the skill:bonus dd.<skill> tree part, capped by perk.doubleDropMax - SkyySkills' config read
     through config:fn:SkyySkills get, defaults when a key is not a Server Setup row); Wisdom = the skill:bonus xp.<skill> part; Class
     Weapon Damage = class level x perk.combat.damagePerLevel; skill levels skill:<uuid>; Overall skill:fn:overall; class class:<uuid>;
     profile name profile:name:<uuid>; purse / bank / bag counts as before.
  4. "Change Profile" runs the player's OWN /profiles (SkyyProfiles 0.1.6: opens its profile page) through the engine command manager
     after the same installed + permission checks the menu tiles use - no SkyyProfiles change, no new bridge key. Hidden when no
     /profiles command is loaded. If the page is still open 0.9 s later (the command answered in chat instead) it says so (StatsTask:
     one redraw, only while it is still the open page in the same world).
  5. /stats (alias /profilestats, hytale:Adventurer) opens the page; registered in a try (a clash is logged, the menu still loads).
  6. ROUND_PINS = {} (deploys on its own); no saved data, no setting, no asset change (the menu item JSON + server.lang byte-identical).
Spec questions Skyy did not answer, defaults used (tell Skyy): phase 1 only; planned stats hidden (no checkbox - UNVERIFIED in the kit);
Fortune shown as today's double-drop % until the tools round; /stats <player> for admins left out (spec 2.1 extra).
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.9 outside them, byte for byte.
"""
import os
import re
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.9.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.10.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.9"' in s and "0.3.9: CLASS TEXTS ONLY" in s, "not the generated 0.3.9 script"
assert "@@" not in s, "0.3.9 already holds a @@ token"
CHANGES = []            # (new text, old text) of every change, in order: undone at the end


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyMenu") != "0.3.9":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.9" % _set.get("SkyyMenu"))

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.9: CLASS TEXTS ONLY''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.10: THE STATS PAGE, phase 1 (research/cloud/Stats-Page-Spec.md P1; notes: tools/menu_0_3_10_patch.py): the Your Profile tile and
       /stats (/profilestats) open StatsPage - a vanilla-kit inline page (tools/skyyui.py) with every LIVE stat of the active profile
       (Health / Mana / Stamina from the EntityStatMap split by modifier source, gear + accessory stats, speed / jump / fall damage,
       Mana Regen, Fortune as double-drop %, Wisdom, skills, Overall, class, purse, bank, bags) in five tabs, and a Change Profile
       button (runs the player's own /profiles; hidden without it). The Your Profile hover text is short lines. No saved data, no
       setting, no other mod changed; ROUND_PINS = {} (deploys on its own).
  CHECKED: see SkyyMenu/test_skyymenu_0.3.10.py (every 0.3.9 check carried forward + S the Stats page flows + K4 0.3.9 -> 0.3.10).
0.3.9: CLASS TEXTS ONLY''')
rep('VERSION = "0.3.9"', 'VERSION = "0.3.10"')
rep('"set EXPECTED_KIT through tools/menu_0_3_9_patch.py (or its successor), regenerate, re-test"',
    '"set EXPECTED_KIT through tools/menu_0_3_10_patch.py (or its successor), regenerate, re-test"')
rep('''import skyycfg as CFG        # 0.3: the admin config kit (SkyyMenu's own settings, research/Server-Setup-Spec.md 1.4)
''', '''import skyycfg as CFG        # 0.3: the admin config kit (SkyyMenu's own settings, research/Server-Setup-Spec.md 1.4)
import skyyui as SUI         # 0.3.10: the shared vanilla UI kit - the Stats page only (the older menu pages keep their own look)
''')
rep('''#           profile  show your stats in the info box                      info   just show the text in the info box''',
    '''#           profile  open the Stats page (0.3.10; was: show stats in the box)  info   just show the text in the info box''')

# ================================================================================================ the Your Profile tile
rep('''    ("main", 4,  "Armor_Iron_Head", "Your Profile", ["Your coins, bank, skill levels and accessories."], "Click to show your stats above", "profile"),''',
    '''    # 0.3.10: the tile opens the Stats page (StatsPage, also /stats); its hover text is MenuPage.profileBody (short lines)
    ("main", 4,  "Armor_Iron_Head", "Your Profile", ["All your stats: health, mana, strength, crit, fortune, skills and more."],
        "Click to open your Stats page", "profile"),''')

# ================================================================================================ the SkyyMenu Mods entry
rep('''     "desc": "The all-in-one SkyWynn menu: teleports, your island menu, Pocket Dimension, Vault, Accessory Bag, the HUD editor, crafting, skills, collections, the bazaar, the auction house, the bank, reforging and identifying gear, players, your party and guild, your settings, this list of mods and Server Setup for admins.",
     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item",''',
    '''     # 0.3.10: the Stats page (/stats)
     "desc": "The all-in-one SkyWynn menu: teleports, your island menu, Pocket Dimension, Vault, Accessory Bag, the HUD editor, crafting, skills, collections, the bazaar, the auction house, the bank, reforging and identifying gear, players, your party and guild, your stats, your settings, this list of mods and Server Setup for admins.",
     "commands": ["/skymenu%ALIASES% - open the menu or replace a lost menu item",
                  "/stats (or /profilestats) - all your stats on one page",''')

# ================================================================================================ ROUND_PINS: deploys on its own
rep('''ROUND_PINS = {'SkyyClasses': ('0.1.13', '0.1.14'), 'SkyyProfiles': ('0.1.5', '0.1.6'), 'SkyySkills': ('0.4.20', '0.4.21')}''',
    '''# 0.3.10: EMPTY - deploys on its own (the Stats page reads only what the live mods already publish). 0.3.9's round (SkyyClasses
# 0.1.14, SkyySkills 0.4.21, SkyyProfiles 0.1.6) is pinned in SET now.
ROUND_PINS = {}''')

# ================================================================================================ live-set check: patch name
rep('_PATCH = "tools/menu_0_3_9_patch.py"', '_PATCH = "tools/menu_0_3_10_patch.py"')

# ================================================================================================ the Stats page markup (build time, kit)
STATS_PY = r'''
# ================= 0.3.10 THE STATS PAGE (research/cloud/Stats-Page-Spec.md P1): markup from the shared vanilla kit tools/skyyui.py =================
# Built when this script runs: SUI.verify() proves every vanilla value / texture / sound against Assets.zip (read-only) and stops the
# build on drift. Only properties the deployed kit pages use (SUI.assert_proven); every id starts with SkyyStat, no underscores.
SUI.verify()
SUI_KIT_ID = SUI.kit_id()
ST_W, ST_H = 1100, 900               # fits 1080 px with the ornaments (asserted)
ST_TABS = ["Main", "Combat", "Gathering", "Skills", "Profile"]
ST_NOTES = [
    "Health, Mana, Stamina: your max now. Base = the game's own part and armor.",
    "Gear = your held weapon and worn armor. Stats not built yet are hidden.",
    "Fortune = chance for a double drop (tools add more later). Wisdom = more XP.",
    "Your skill levels on this profile. /skills shows your XP and rewards.",
    "Each profile has its own class, skills and stats. Change Profile lists them.",
]
ST_SUB = "What applies to you right now. Click Refresh after you change your gear."
ST_LINE_MAX = 79                     # a stat row (name + total + source + 2) and every header / note line stays under 80 characters
ST_ROW_H, ST_ROW_GAP = 38, 2
ST_NAME_W, ST_VAL_W, ST_MID_W = 300, 200, 30
ST_NAME_FS, ST_VAL_FS, ST_SRC_FS = 18, 18, 15
ST_FOOT_MENU_W, ST_FOOT_PROF_W, ST_FOOT_GAP = 220, 200, 6
# the gear stats the page shows: SkyyGear's LIVE rows (key, page label, short label, unit). spd (Speed) is shown from the movement
# map (what is applied), the "coming later" rows are hidden (spec default). Cross-checked against the SET SkyyGear script below.
ST_GEAR = [("def", "Defense", "Defense", ""), ("str", "Strength", "Strength", ""), ("cc", "Crit Chance", "Crit", "%"),
           ("cd", "Crit Damage", "Crit Dmg", "%"), ("mp", "Magical Power", "Magic", ""), ("stam", "Stamina Regen", "Stamina", ""),
           ("dmg", "Damage", "Damage", "%"), ("chg", "Charged Attack Damage", "Charged", "%"), ("tdmg", "True Damage", "True", ""),
           ("lsteal", "Life Steal", "Life Steal", "%"), ("msteal", "Mana Steal", "Mana Steal", ""),
           ("hpr", "Health Regen", "Regen", ""), ("hprp", "Health Regen %", "Regen", "%")]
ST_ELEM = [("fEarth", "Earth"), ("fThunder", "Thunder"), ("fWater", "Water"), ("fFire", "Fire"), ("fAir", "Air")]
ST_RAW = [("rThunder", "Thunder"), ("rWater", "Water"), ("rElem", "Elemental")]
ST_GROUPS = ["Gear", "Accessories", "Overall", "Class", "Base Mana", "Skills", "Trees"]   # short: a Health row holds five parts
ST_FORTUNE = [("Mining", "mining"), ("Foraging", "foraging"), ("Farming", "farming")]
ST_WISDOM = [("Mining", "mining"), ("Foraging", "foraging"), ("Farming", "farming"), ("Cooking", "cooking")]
for _t in ST_NOTES + [ST_SUB]:
    assert len(_t) <= ST_LINE_MAX, "stats line over %d characters: %s" % (ST_LINE_MAX, _t)
# the SET SkyyGear script's LIVE stat rows (key, label, unit, live) - a row this page shows must still be a LIVE row with the same unit
_gear_ver = dict(_LIVE).get("SkyyGear") if _LIVE else None
_gear_py = os.path.join(B.PROJECT, "SkyyGear", "build_skyygear_%s.py" % _gear_ver) if _gear_ver else None
if _gear_py and os.path.isfile(_gear_py):
    _gt = open(_gear_py, encoding="utf-8").read()
    _grows = dict((m.group(1), (m.group(2), m.group(3), m.group(4))) for m in
                  re.finditer(r'\("(\w+)", "([^"]+)", "[wsae]+", "(%?)", \d+, \d+, ([01]), "\w*"\)', _gt))
    for _k, _lab, _short, _u in ST_GEAR + [(k, l, l, "") for k, l in ST_ELEM + ST_RAW]:
        assert _k in _grows, "SkyyGear %s has no stat %s any more" % (_gear_ver, _k)
        assert _grows[_k][2] == "1", "SkyyGear %s: %s is not a LIVE stat (the Stats page hides planned stats)" % (_gear_ver, _k)
        if _k in [g[0] for g in ST_GEAR]:
            assert _grows[_k][1] == _u, "SkyyGear %s: %s unit %r, the page says %r" % (_gear_ver, _k, _grows[_k][1], _u)
    print("stats page: %d gear stats checked against SkyyGear %s (LIVE rows, units)" % (len(ST_GEAR) + len(ST_ELEM) + len(ST_RAW), _gear_ver))
else:
    print("WARNING stats page: no SET SkyyGear script found - the gear stat list was not cross-checked")


def stats_page():
    """(shell, rows, tabs, foot): the Stats page's markup. The fixed parts are in the shell (one Java block); the tab buttons, the
    stat rows and the footer are appended by StatsPage.build at run time from the markups returned here (J() ids / looks)."""
    J = SUI.J
    sh = SUI.page_shell("SkyyStatF", ST_W, ST_H, "Your Stats", body_id="SkyyStat")
    ap, body, IW = sh.appends, sh.body, sh.inner_w
    used = []
    used.append(ap.add(body, SUI.label("SkyyStatHead", "", "heading", h=30, size=20, wrap=False)))
    used.append(ap.add(body, SUI.label("SkyyStatSub", "", "caption", h=24, size=ST_SRC_FS)))
    used.append(ap.add(body, SUI.group("SkyyStatTabs", "Left", h=SUI.BTN_H, anchor={"top": 8, "bottom": 8})))
    well_pad = SUI.WELL_PAD
    rows_h = ST_ROWS * (ST_ROW_H + ST_ROW_GAP)
    used.append(ap.add(body, SUI.panel("SkyyStatList", "well", h=rows_h + 2 * well_pad)))
    used.append(ap.add(body, SUI.label("SkyyStatNote", "", "caption", h=26, size=ST_SRC_FS, anchor={"top": 6})))
    used.append(ap.add(body, SUI.label("SkyyStatMsg", "", "bold", h=26, size=16, col="info", align="Center")))
    used.append(ap.add(body, SUI.separator("content", anchor={"top": SUI.SEP_MARGIN, "bottom": SUI.SEP_MARGIN})))
    used.append(ap.add(body, SUI.group("SkyyStatFoot", "Left", h=SUI.BTN_H)))
    left = sh.fit(used)
    assert left >= 0, "stats page parts do not fit"
    # tabs: equal widths, 5 px apart (the vanilla tab rule); the active one Primary
    tab_w = (IW - (len(ST_TABS) - 1) * SUI.TAB_GAP) // len(ST_TABS)
    tabs = []
    for i, name in enumerate(ST_TABS):
        anc = {"right": SUI.TAB_GAP} if i < len(ST_TABS) - 1 else None
        tabs.append(SUI.choose(J("this.tab == %d" % i), SUI.button("SkyyStatTab%d" % i, name, "primary", w=tab_w, anchor=anc),
                               SUI.button("SkyyStatTab%d" % i, name, "secondary", w=tab_w, anchor=anc)))
    # one stat row: name | total (right-aligned) | gap | where it comes from
    row_w = IW - 2 * well_pad
    src_w = row_w - ST_NAME_W - ST_VAL_W - ST_MID_W
    rid = J("i", "0")
    rows = [("SkyyStatList", SUI.group("SkyyStatR" + rid, "Left", h=ST_ROW_H, anchor={"bottom": ST_ROW_GAP})),
            ("SkyyStatR" + rid, SUI.label("SkyyStatN" + rid, "", "rowName", w=ST_NAME_W, h=ST_ROW_H, size=ST_NAME_FS, anchor={"left": 8})),
            ("SkyyStatR" + rid, SUI.label("SkyyStatV" + rid, "", "rowName", w=ST_VAL_W - 8, h=ST_ROW_H, size=ST_VAL_FS, align="End")),
            ("SkyyStatR" + rid, SUI.spacer(w=ST_MID_W, h=ST_ROW_H)),
            ("SkyyStatR" + rid, SUI.label("SkyyStatS" + rid, "", "rowSub", w=src_w, h=ST_ROW_H, size=ST_SRC_FS))]
    # the footer: < SkyWynn Menu, Refresh, Change Profile (or a spacer of its width), a filler, Close - filled exactly
    g = ST_FOOT_GAP
    fill = IW - (ST_FOOT_MENU_W + g + SUI.BTN_MIN_W + g + ST_FOOT_PROF_W) - SUI.BTN_MIN_W
    assert fill >= 0, "the stats footer is wider than the page"
    foot = {
        "menu": SUI.button("SkyyStatMenu", "< SkyWynn Menu", "secondary", w=ST_FOOT_MENU_W, anchor={"right": g}),
        "refresh": SUI.button("SkyyStatRefresh", "Refresh", "secondary", anchor={"right": g}),
        "profile": SUI.button("SkyyStatProfile", "Change Profile", "primary", w=ST_FOOT_PROF_W),
        "noprofile": SUI.spacer(w=ST_FOOT_PROF_W, h=SUI.BTN_H),
        "fill": SUI.spacer(w=fill, h=SUI.BTN_H),
        "close": SUI.button("SkyyStatClose", "Close", "secondary", sound="cancel"),
    }
    # every look this page can show, checked as one page (ids, parents, markup rules, proven properties only)
    chk = SUI.Appends(list(ap))
    for t in tabs:
        chk.append(("SkyyStatTabs", t))
    chk.extend(rows)
    for k in ("menu", "refresh", "profile", "fill", "close"):
        chk.append(("SkyyStatFoot", foot[k]))
    chk.check("SkyyStat")
    SUI.assert_proven(chk, what="stats page")
    SUI.assert_proven([foot["noprofile"]], what="stats page footer spacer")
    assert sum(SUI.outer_size(foot[k])[0] for k in ("menu", "refresh", "profile", "fill", "close")) == IW, "footer not filled exactly"
    assert ST_H - SUI.DECO_TOP - SUI.DECO_BOTTOM <= 1080, "the stats page with its ornaments must fit a 1080 px screen"
    # every fixed text fits its label (the client's own font tables)
    for _t in ST_NOTES + [ST_SUB]:
        assert SUI.text_width(_t, ST_SRC_FS) <= IW, "stats note too wide: " + _t
    # the widest names / totals a row shows fit their columns (the client's font)
    for _t in ("Charged Attack Damage", "Collection Recipes", "Other class skills"):
        assert SUI.text_width(_t, ST_NAME_FS, bold=True) <= ST_NAME_W - 8, "stat name too wide: " + _t
    for _t in ("1,000,000,000%", "999,999,999,999", "Level 100", "+1,000,000,000%"):
        assert SUI.text_width(_t, ST_VAL_FS, bold=True) <= ST_VAL_W - 8, "stat total too wide: " + _t
    return sh, rows, tabs, foot, src_w, left


ST_ROWS = 14
ST_SH, ST_ROW_MK, ST_TAB_MK, ST_FOOT_MK, ST_SRC_W, ST_LEFT = stats_page()
# a stat row's longest source text (the Java clips name + total + source to ST_LINE_MAX characters) fits its column
for _t in ("Gear +40, Accessories +12, Overall +7, Skills +18, Trees +5, base 9",
           "Accessories +4, Overall +2.8, Class +10, Base Mana +10, Skills +2.4, base 9",
           "W" * 8 + " level 100 +50%, Skill trees +50% (max 100%)",
           "some blocks only: Foraging level 100 +50%, Skill trees +50% (max 100%)",
           "Swordsmanship 100, Assassination 100, Discipline 100, Sorcery 100"):
    assert SUI.text_width(_t, ST_SRC_FS) <= ST_SRC_W, "source column too narrow for: " + _t
ST_SHELL_JAVA = ST_SH.java("b")
ST_TABS_JAVA = "\n".join(SUI.java_append(p, mk) for p, mk in [("SkyyStatTabs", t) for t in ST_TAB_MK])
ST_ROW_JAVA = "\n".join(SUI.java_append(p, mk) for p, mk in ST_ROW_MK)
ST_FOOT_JAVA = dict((k, SUI.java_append("SkyyStatFoot", mk)) for k, mk in ST_FOOT_MK.items())
ST_STATIC = [SUI.render(mk) for _p, mk in ST_SH.appends if not SUI.has_j(mk)]
print("stats page: %d x %d, %d rows per tab, %d px left in the body, kit %s" % (ST_W, ST_H, ST_ROWS, ST_LEFT, SUI_KIT_ID))
'''
rep('''JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"''', STATS_PY.lstrip("\n") + '''
JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"''')

# ================================================================================================ tokens for the stat classes
rep('''    "HLD":  "com.hypixel.hytale.component.Holder",
}''', '''    "HLD":  "com.hypixel.hytale.component.Holder",
    # 0.3.10: the Stats page reads the player's Health / Mana / Stamina (max + the MAX modifiers by key) on the world thread
    "ESM":  "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV":  "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST":  "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "SMO":  "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier",
    "MTG":  "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget",
    "CAL":  "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType",
}''')

# ================================================================================================ engine members probed at build time
rep('''             (T["ATW"], "getHolder"), (T["ATW"], "getWorld"), (T["HLD"], "getComponent"), (T["PR"], "getComponentType")):
    B.probe(pool, c, m)''', '''             (T["ATW"], "getHolder"), (T["ATW"], "getWorld"), (T["HLD"], "getComponent"), (T["PR"], "getComponentType")):
    B.probe(pool, c, m)
# 0.3.10: every engine member the Stats page uses
for c, m in ((T["ESM"], "getComponentType"), (T["ESM"], "get"), (T["ESV"], "getMax"), (T["ESV"], "getModifiers"),
             (T["DST"], "getHealth"), (T["DST"], "getMana"), (T["DST"], "getStamina"), (T["SMO"], "getAmount"),
             (T["SMO"], "getCalculationType"), (T["SMO"], "getTarget"), (T["MTG"], "MAX"), (T["CAL"], "ADDITIVE")):
    B.probe(pool, c, m)''')

# ================================================================================================ the new classes
rep('''pl   = mk("SkyyMenuPlugin", JP)''', '''scl  = mk("StatsCalc")      # 0.3.10: the Stats page's numbers (bridge reads + the EntityStatMap of the player)
stp  = mk("StatsPage", T["PAGE"])
sta  = mk("StatsTask")      # 0.3.10: the one answer after Change Profile when /profiles did not open its page
stc  = mk("StatsCmd", T["APC"])
pl   = mk("SkyyMenuPlugin", JP)''')

# ================================================================================================ StatsCalc (before MenuPage: profileBody uses it)
STATS_CALC = r'''
# ================= 0.3.10 StatsCalc: every number of the Stats page. Bridge reads only (java.lang types, tools/PROFILES-CONTRACT.md: the
# UUID keys always hold the ACTIVE profile), plus the player's EntityStatMap (vitals(): world thread, called from StatsPage.build). A stat
# whose mod is missing shows "-" and why; nothing here writes anything. Rows = String[] { name, total, source }: name + total + source
# + 2 <= ST_LINE_MAX (the source is clipped). Health / Mana / Stamina: the Skyy parts by key prefix, then ", base <the rest>" if it fits.
F(scl, "public static final int LINE_MAX = %d;" % ST_LINE_MAX)
F(scl, "public static final double JUMP_H0 = 2.1756;")      # tools/skyymove.py: default JumpForce 11.8 -> 11.8^2 / (2 x 32) blocks
F(scl, "public static final String[] GK = %s;" % jarr([g[0] for g in ST_GEAR]))
F(scl, "public static final String[] GL = %s;" % jarr([g[1] for g in ST_GEAR]))
F(scl, "public static final String[] GU = %s;" % jarr([g[3] for g in ST_GEAR]))
F(scl, "public static final String[] ELEM_K = %s;" % jarr([g[0] for g in ST_ELEM]))
F(scl, "public static final String[] ELEM_S = %s;" % jarr([g[1] for g in ST_ELEM]))
F(scl, "public static final String[] RAW_K = %s;" % jarr([g[0] for g in ST_RAW]))
F(scl, "public static final String[] RAW_S = %s;" % jarr([g[1] for g in ST_RAW]))
F(scl, "public static final String[] GROUPS = %s;" % jarr(ST_GROUPS))
F(scl, "public static final String[] FORT_N = %s;" % jarr([f[0] for f in ST_FORTUNE]))
F(scl, "public static final String[] FORT_K = %s;" % jarr([f[1] for f in ST_FORTUNE]))
F(scl, "public static final String[] WIS_N = %s;" % jarr([f[0] for f in ST_WISDOM]))
F(scl, "public static final String[] WIS_K = %s;" % jarr([f[1] for f in ST_WISDOM]))
F(scl, "public static final String[] CLASS_SKILLS = %s;" % jarr(CLASS_SKILLS))
F(scl, "public static final String[] TABS = %s;" % jarr(ST_TABS))
F(scl, "public static final String[] NOTES = %s;" % jarr(ST_NOTES))
F(scl, "public static final String SUB = %s;" % jstr(ST_SUB))
F(scl, "public static final int ROWS = %d;" % ST_ROWS)
M(scl, r"""
public static java.util.Map br() { return @PKG@.MenuUtil.bridge(); }""")
M(scl, r"""
public static String num(double v) {
  if (Double.isNaN(v) || Double.isInfinite(v)) return "0";
  double x = v;
  if (x > 1.0E9) x = 1.0E9;
  if (x < -1.0E9) x = -1.0E9;
  long r = Math.round(x * 10.0);
  if (r % 10L == 0L) return @PKG@.MenuUtil.fmt(r / 10L);
  long a = r < 0L ? -r : r;
  return (r < 0L ? "-" : "") + String.valueOf(a / 10L) + "." + String.valueOf(a % 10L);
}""")
M(scl, r"""
public static String signed(double v) {
  return (Math.round(v * 10.0) > 0L ? "+" : "") + num(v);
}""")
M(scl, r"""
public static java.util.HashMap kv(Object o) {
  java.util.HashMap m = new java.util.HashMap();
  if (!(o instanceof String)) return m;
  String[] parts = ((String) o).split(",");
  for (int i = 0; i < parts.length; i++) {
    String p = parts[i].trim();
    int c = p.lastIndexOf(':');
    if (c <= 0 || c >= p.length() - 1) continue;
    String k = p.substring(0, c).trim();
    double v = Double.NaN;
    try { v = Double.parseDouble(p.substring(c + 1).trim()); } catch (Throwable t) { v = Double.NaN; }
    if (Double.isNaN(v) || Double.isInfinite(v)) continue;
    Object old = m.get(k);
    double nv = (old instanceof Double ? ((Double) old).doubleValue() : 0.0) + v;
    if (nv > 1.0E9) nv = 1.0E9;
    if (nv < -1.0E9) nv = -1.0E9;
    m.put(k, Double.valueOf(nv));
  }
  return m;
}""")
M(scl, r"""
public static double get(java.util.HashMap m, String k) {
  Object o = m == null ? null : m.get(k);
  return o instanceof Double ? ((Double) o).doubleValue() : 0.0;
}""")
# the skill string in its own order: [name, level] pairs
M(scl, r"""
public static java.util.ArrayList pairs(Object o) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (!(o instanceof String)) return out;
  String[] parts = ((String) o).split(",");
  for (int i = 0; i < parts.length; i++) {
    String p = parts[i].trim();
    int c = p.lastIndexOf(':');
    if (c <= 0 || c >= p.length() - 1) continue;
    int lv = -1;
    try { lv = Integer.parseInt(p.substring(c + 1).trim()); } catch (Throwable t) { lv = -1; }
    if (lv < 0) continue;
    out.add(new String[] { @PKG@.MenuUtil.safe(p.substring(0, c).trim()), String.valueOf(lv) });
  }
  return out;
}""")
M(scl, r"""
public static void add(java.util.ArrayList rows, String name, String value, String src) {
  String n = @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(name == null ? "" : name), 32);
  String v = @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(value == null ? "" : value), 24);
  int room = LINE_MAX - n.length() - v.length() - 2;
  if (room < 12) room = 12;
  rows.add(new String[] { n, v, @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(src == null ? "" : src), room) });
}""")
M(scl, r"""
public static void part(StringBuilder sb, String label, double v, String unit) {
  if (Math.abs(v) < 0.05) return;
  if (sb.length() > 0) sb.append(", ");
  sb.append(label).append(' ').append(signed(v)).append(unit);
}""")
M(scl, r"""
public static Object call(String key, Object arg) {
  try {
    Object f = br().get(key);
    if (f instanceof java.util.function.Function) return ((java.util.function.Function) f).apply(arg);
  } catch (Throwable t) { }
  return null;
}""")
# a value of another mod's Server Setup row (tools/CONFIG-CONTRACT.md op "get"; null = not a row / mod missing -> the default)
M(scl, r"""
public static String cfg(String mod, String key) {
  Object r = call("config:fn:" + mod, new Object[] { "get", key });
  return r instanceof String ? (String) r : null;
}""")
M(scl, r"""
public static double cfgNum(String mod, String key, double def) {
  String s = cfg(mod, key);
  if (s == null) return def;
  double d = def;
  try { d = Double.parseDouble(s.trim()); } catch (Throwable t) { d = def; }
  if (Double.isNaN(d) || Double.isInfinite(d)) return def;
  return d;
}""")
M(scl, r"""
public static boolean cfgOn(String mod, String key, boolean def) {
  String s = cfg(mod, key);
  if (s == null) return def;
  String t = s.trim().toLowerCase();
  if (t.equals("true")) return true;
  if (t.equals("false")) return false;
  return def;
}""")
# the summed skill-tree bonus of one key (skill:bonus:<uuid> = source -> Map{"dd.mining": 0.02, "xp.mining": 0.15, ...}) - the same sum
# SkyySkills' SkillBonus.sum makes
M(scl, r"""
public static double bonus(java.util.UUID u, String key) {
  double s = 0.0;
  try {
    Object o = br().get("skill:bonus:" + u.toString());
    if (!(o instanceof java.util.Map)) return 0.0;
    java.util.Iterator it = ((java.util.Map) o).values().iterator();
    while (it.hasNext()) {
      Object v = it.next();
      if (!(v instanceof java.util.Map)) continue;
      Object n = ((java.util.Map) v).get(key);
      if (!(n instanceof Number)) continue;
      double d = ((Number) n).doubleValue();
      if (Double.isNaN(d) || Double.isInfinite(d)) continue;
      s = s + d;
    }
  } catch (Throwable t) { return 0.0; }
  return s;
}""")
M(scl, r"""
public static String text(String key) {
  Object o = br().get(key);
  if (!(o instanceof String)) return null;
  String t = ((String) o).trim();
  return t.length() == 0 ? null : @PKG@.MenuUtil.safe(t);
}""")
# fix round: profile:class:<uuid> (SkyyProfiles) is AUTHORITATIVE (SkyyClasses 0.1.3+ / SkyySkills 0.3.2+ read it first); class:<uuid> +
# class:skill:<uuid> lag a profile switch by up to ~2 s (SkyyClasses' ClassTick). classSyncing = SkyyClasses is loaded (class:fn:get) and
# its class:<uuid> does not match the profile's class yet - then the class skill is stale and nothing class-skill based is shown.
M(scl, r"""
public static String className(java.util.UUID u) {
  String c = text("profile:class:" + u.toString());
  return c != null ? c : text("class:" + u.toString());
}""")
M(scl, r"""
public static boolean classSyncing(java.util.UUID u) {
  String pc = text("profile:class:" + u.toString());
  if (pc == null) return false;
  if (!(br().get("class:fn:get") instanceof java.util.function.Function)) return false;
  String c = text("class:" + u.toString());
  return c == null || !c.equalsIgnoreCase(pc);
}""")
M(scl, r"""
public static String classSkill(java.util.UUID u) { return classSyncing(u) ? null : text("class:skill:" + u.toString()); }""")
M(scl, r"""
public static String profileName(java.util.UUID u) { return text("profile:name:" + u.toString()); }""")
M(scl, r"""
public static Object[] overallInfo(java.util.UUID u) {
  Object r = call("skill:fn:overall", u);
  if (r instanceof Object[] && ((Object[]) r).length >= 5 && ((Object[]) r)[0] instanceof Number) return (Object[]) r;
  return null;
}""")
M(scl, r"""
public static int overall(java.util.UUID u) {
  Object[] o = overallInfo(u);
  if (o != null) return ((Number) o[0]).intValue();
  Object v = br().get("skill:overall:" + u.toString());
  return v instanceof Number ? ((Number) v).intValue() : -1;
}""")
# "Mining 12, Foraging 8, Farming 5" - the n highest levels (ties: the skill string's order)
M(scl, r"""
public static String topSkills(java.util.UUID u, int n) {
  java.util.ArrayList ps = pairs(br().get("skill:" + u.toString()));
  if (ps.isEmpty()) return null;
  boolean[] used = new boolean[ps.size()];
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < n; k++) {
    int best = -1;
    int bl = -1;
    for (int i = 0; i < ps.size(); i++) {
      if (used[i]) continue;
      int lv = Integer.parseInt(((String[]) ps.get(i))[1]);
      if (lv > bl) { bl = lv; best = i; }
    }
    if (best < 0) break;
    used[best] = true;
    if (sb.length() > 0) sb.append(", ");
    sb.append(((String[]) ps.get(best))[0]).append(' ').append(bl);
  }
  return sb.toString();
}""")
M(scl, r"""
public static String header(java.util.UUID u, String player) {
  StringBuilder sb = new StringBuilder(@PKG@.MenuUtil.safe(player));
  String c = className(u);
  if (c != null) sb.append("  -  ").append(c);
  String p = profileName(u);
  if (p != null) sb.append("  -  profile ").append(p);
  int ov = overall(u);
  if (ov >= 0) sb.append("  -  Overall Level ").append(ov);
  return @PKG@.MenuUtil.clip(sb.toString(), LINE_MAX);
}""")
# ---- Health / Mana / Stamina: the max the player has right now, split by the MAX modifiers' key prefixes (every Skyy mod names its own)
M(scl, r"""
public static int group(String key) {
  if (key == null) return -1;
  if (key.startsWith("skyygear_")) return 0;
  if (key.startsWith("skyyacc_")) return 1;
  if (key.startsWith("skyyskill_overall")) return 2;
  if (key.startsWith("skyyskill_class")) return 3;
  if (key.startsWith("skyyskill_base")) return 4;
  if (key.startsWith("skyyskill_")) return 5;
  if (key.startsWith("skyytree_")) return 6;
  return -1;
}""")
M(scl, r"""
public static String[] vital(@ESV@ v) {
  if (v == null) return null;
  float max = v.getMax();
  double[] grp = new double[GROUPS.length];
  double known = 0.0;
  java.util.Map mods = v.getModifiers();
  if (mods != null) {
    java.util.Iterator it = mods.keySet().iterator();
    while (it.hasNext()) {
      Object k = it.next();
      Object mo = mods.get(k);
      if (!(mo instanceof @SMO@)) continue;
      @SMO@ sm = (@SMO@) mo;
      if (sm.getTarget() != @MTG@.MAX || sm.getCalculationType() != @CAL@.ADDITIVE) continue;
      int gi = group(String.valueOf(k));
      if (gi < 0) continue;
      double a = (double) sm.getAmount();
      if (Double.isNaN(a) || Double.isInfinite(a)) continue;
      grp[gi] = grp[gi] + a;
      known = known + a;
    }
  }
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < grp.length; i++) part(sb, GROUPS[i], grp[i], "");
  return new String[] { num((double) max), sb.toString(), num((double) max - known) };
}""")
M(scl, r"""
public static String[] vitalAt(@ESM@ m, int idx) {
  try {
    if (m == null || idx < 0) return null;
    return vital(m.get(idx));
  } catch (Throwable t) { return null; }
}""")
# world thread only (StatsPage.build): null = the stat map could not be read (the rows then say so)
M(scl, r"""
public static Object[] vitals(@ST@ st, @REF@ ref) {
  try {
    if (st == null || ref == null || !ref.isValid()) return null;
    @ESM@ m = (@ESM@) st.getComponent(ref, @ESM@.getComponentType());
    if (m == null) return null;
    return new Object[] { vitalAt(m, @DST@.getHealth()), vitalAt(m, @DST@.getMana()), vitalAt(m, @DST@.getStamina()) };
  } catch (Throwable t) { return null; }
}""")
M(scl, r"""
public static void vitalRow(java.util.ArrayList rows, String name, Object[] vit, int i) {
  String[] e = null;
  if (vit != null && i < vit.length && vit[i] instanceof String[]) e = (String[]) vit[i];
  if (e == null) { add(rows, name, "-", "not read - click Refresh"); return; }
  String src = e[1];
  String tail = (src.length() == 0 ? "Base " : ", base ") + e[2];
  if (src.length() + tail.length() <= LINE_MAX - name.length() - e[0].length() - 2) src = src + tail;
  add(rows, name, e[0], src);
}""")
# ---- gear + accessory stats (gear:stats:<uuid> = SkyyGear's active totals without the accessory part, gear:extra:<uuid> = that part)
M(scl, r"""
public static int gi(String key) {
  for (int i = 0; i < GK.length; i++) if (GK[i].equals(key)) return i;
  return -1;
}""")
M(scl, r"""
public static void gearRow(java.util.ArrayList rows, java.util.HashMap g, java.util.HashMap a, boolean gearOn, String key) {
  int k = gi(key);
  if (k < 0) return;
  double gv = get(g, key);
  double av = get(a, key);
  StringBuilder sb = new StringBuilder();
  part(sb, "Gear", gv, GU[k]);
  part(sb, "Accessories", av, GU[k]);
  if (sb.length() == 0) sb.append(gearOn ? "nothing from your gear or accessories" : "SkyyGear is not on this server");
  add(rows, GL[k], num(gv + av) + GU[k], sb.toString());
}""")
M(scl, r"""
public static void groupRow(java.util.ArrayList rows, java.util.HashMap g, java.util.HashMap a, String[] keys, String[] shorts, String name, boolean always) {
  double t = 0.0;
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < keys.length; k++) {
    double v = get(g, keys[k]) + get(a, keys[k]);
    t = t + v;
    part(sb, shorts[k], v, "");
  }
  if (Math.abs(t) < 0.05 && !always) return;
  if (sb.length() == 0) sb.append("none - it comes from weapons");
  add(rows, name, num(t), sb.toString());
}""")
# ---- movement (tools/skyymove.py: flat sources add on the default, pct sources multiply on top; speed clamp 0.3-5, jump h0 + 20, fall 0-2)
M(scl, r"""
public static String moveName(String src) {
  String s = src == null ? "" : src;
  if (s.startsWith("gear")) return "Gear";
  if (s.startsWith("accessories")) return "Accessories";
  if (s.startsWith("skills.acrobatics")) return "Acrobatics";
  if (s.startsWith("skills")) return "Skills";
  if (s.startsWith("trees")) return "Skill trees";
  return @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(s), 20);
}""")
M(scl, r"""
public static String[] move(java.util.UUID u, String stat) {
  double flat = 0.0;
  double pct = 0.0;
  boolean jump = "jump".equals(stat);
  StringBuilder sb = new StringBuilder();
  try {
    Object o = br().get("move:" + u.toString());
    if (o instanceof java.util.Map) {
      java.util.Map mm = (java.util.Map) o;
      java.util.Iterator it = mm.keySet().iterator();
      while (it.hasNext()) {
        Object src = it.next();
        Object e = mm.get(src);
        if (!(e instanceof java.util.Map)) continue;
        Object n = ((java.util.Map) e).get(stat);
        if (!(n instanceof Number)) continue;
        double d = ((Number) n).doubleValue();
        if (Double.isNaN(d) || Double.isInfinite(d) || d == 0.0) continue;
        boolean isPct = "pct".equals(String.valueOf(((java.util.Map) e).get("layer")));
        if (isPct) pct = pct + d; else flat = flat + d;
        if (jump && !isPct) part(sb, moveName(String.valueOf(src)), d, " blocks");
        else part(sb, moveName(String.valueOf(src)), d * 100.0, "%");
      }
    }
  } catch (Throwable t) { }
  double total = 0.0;
  if (jump) {
    double j = (JUMP_H0 + flat) * (1.0 + pct);
    if (j < 0.0) j = 0.0;
    if (j > JUMP_H0 + 20.0) j = JUMP_H0 + 20.0;
    total = (j / JUMP_H0 - 1.0) * 100.0;
  } else {
    double f = (1.0 + flat) * (1.0 + pct);
    if ("speed".equals(stat)) {
      if (f < 0.3) f = 0.3;
      if (f > 5.0) f = 5.0;
    } else {
      if (f < 0.0) f = 0.0;
      if (f > 2.0) f = 2.0;
    }
    total = (f - 1.0) * 100.0;
  }
  if (sb.length() == 0) sb.append("no bonus right now");
  return new String[] { signed(total) + "%", sb.toString() };
}""")
M(scl, r"""
public static String sourceName(String src) {
  String s = src == null ? "" : src.trim();
  if (s.startsWith("tree")) return "Skill trees";
  if (s.startsWith("acc")) return "Accessories";
  if (s.startsWith("gear")) return "Gear";
  return @PKG@.MenuUtil.clip(@PKG@.MenuUtil.safe(s), 20);
}""")
M(scl, r"""
public static String[] manaRegen(java.util.UUID u) {
  Object t = call("skill:fn:manaregen", new Object[] { "get", u });
  if (!(t instanceof Number)) return new String[] { "-", "needs SkyySkills" };
  double tot = ((Number) t).doubleValue();
  StringBuilder sb = new StringBuilder();
  Object s = call("skill:fn:manaregen", new Object[] { "sources", u });
  if (s instanceof String[]) {
    String[] a = (String[]) s;
    for (int i = 0; i < a.length; i++) {
      String x = a[i] == null ? "" : a[i];
      int eq = x.indexOf('=');
      if (x.length() == 0) continue;
      if (sb.length() > 0) sb.append(", ");
      if (eq > 0) sb.append(sourceName(x.substring(0, eq))).append(' ').append(x.substring(eq + 1).trim()).append('%');
      else sb.append(x);
    }
  }
  if (sb.length() == 0) sb.append("no bonus - skill tree nodes add Mana Regen");
  return new String[] { signed(tot) + "%", sb.toString() };
}""")
# ---- gathering: Fortune = today's double-drop chance (SkyySkills Perks.chanceU: level x perk.<skill>.doubleDropPerLevel + the tree dd.<skill>,
# capped by perk.doubleDropMax); Wisdom = the tree xp.<skill> part
# fix round: perk.<skill>.doubleDropOnly (SkyySkills default foraging = _Trunk) leads the source: "logs only: " / "some blocks only: "
M(scl, r"""
public static void fortune(java.util.ArrayList rows, java.util.UUID u, java.util.HashMap sk, boolean skillsOn, int i) {
  String name = FORT_N[i] + " Fortune";
  if (!skillsOn) { add(rows, name, "-", "needs SkyySkills"); return; }
  String key = FORT_K[i];
  double lvl = get(sk, FORT_N[i]);
  double rate = cfgOn("SkyySkills", "perk.enabled", true) ? cfgNum("SkyySkills", "perk." + key + ".doubleDropPerLevel", 0.005) : 0.0;
  double tree = cfgOn("SkyySkills", "bridge.bonus.enabled", true) ? bonus(u, "dd." + key) : 0.0;
  double max = cfgNum("SkyySkills", "perk.doubleDropMax", 1.0);
  if (max > 1.0) max = 1.0;
  if (max < 0.0) max = 0.0;
  double perk = lvl * rate;
  double tot = perk + tree;
  if (tot > max) tot = max;
  if (tot < 0.0) tot = 0.0;
  StringBuilder sb = new StringBuilder();
  part(sb, FORT_N[i] + " level " + (int) lvl, perk * 100.0, "%");
  part(sb, "Skill trees", tree * 100.0, "%");
  if (perk + tree > max) sb.append(" (max ").append(num(max * 100.0)).append("%)");
  if (sb.length() == 0) sb.append("level up ").append(FORT_N[i]).append(" for double drops");
  else {
    String only = cfg("SkyySkills", "perk." + key + ".doubleDropOnly");
    if (only == null) only = "foraging".equals(key) ? "_Trunk" : "";
    only = only.trim();
    if (only.equalsIgnoreCase("_Trunk")) sb.insert(0, "logs only: ");
    else if (only.length() > 0) sb.insert(0, "some blocks only: ");
  }
  add(rows, name, num(tot * 100.0) + "%", sb.toString());
}""")
M(scl, r"""
public static void wisdom(java.util.ArrayList rows, java.util.UUID u, boolean skillsOn, int i) {
  String name = WIS_N[i] + " Wisdom";
  if (!skillsOn) { add(rows, name, "-", "needs SkyySkills"); return; }
  double w = cfgOn("SkyySkills", "bridge.bonus.enabled", true) ? bonus(u, "xp." + WIS_K[i]) : 0.0;
  StringBuilder sb = new StringBuilder();
  part(sb, "Skill trees", w * 100.0, "% XP");
  if (sb.length() == 0) sb.append("Wisdom nodes in the skill trees add XP");
  add(rows, name, signed(w * 100.0) + "%", sb.toString());
}""")
M(scl, r"""
public static void classDamage(java.util.ArrayList rows, java.util.UUID u, java.util.HashMap sk) {
  if (classSyncing(u)) { add(rows, "Class Weapon Damage", "-", "class syncing, Refresh in a moment"); return; }
  String cs = classSkill(u);
  if (cs == null) { add(rows, "Class Weapon Damage", "-", "no class on this profile yet"); return; }
  double lvl = get(sk, cs);
  double rate = cfgOn("SkyySkills", "perk.enabled", true) ? cfgNum("SkyySkills", "perk.combat.damagePerLevel", 0.002) : 0.0;
  add(rows, "Class Weapon Damage", signed(lvl * rate * 100.0) + "%", cs + " level " + (int) lvl + ", with your class weapons");
}""")
M(scl, r"""
public static boolean isClassSkill(String name) {
  for (int i = 0; i < CLASS_SKILLS.length; i++) if (CLASS_SKILLS[i].equals(name)) return true;
  return false;
}""")
# ---- the five tabs
M(scl, r"""
public static void mainTab(java.util.ArrayList rows, java.util.UUID u, Object[] vit) {
  java.util.HashMap g = kv(br().get("gear:stats:" + u.toString()));
  java.util.HashMap a = kv(br().get("gear:extra:" + u.toString()));
  boolean gearOn = br().get("gear:fn:stats") instanceof java.util.function.Function;
  vitalRow(rows, "Health", vit, 0);
  vitalRow(rows, "Mana", vit, 1);
  vitalRow(rows, "Stamina", vit, 2);
  gearRow(rows, g, a, gearOn, "def");
  gearRow(rows, g, a, gearOn, "str");
  gearRow(rows, g, a, gearOn, "cc");
  gearRow(rows, g, a, gearOn, "cd");
  gearRow(rows, g, a, gearOn, "mp");
  String[] sp = move(u, "speed");
  add(rows, "Speed", sp[0], sp[1]);
  String[] jp = move(u, "jump");
  add(rows, "Jump Height", jp[0], jp[1]);
  String[] fd = move(u, "fallDamage");
  add(rows, "Fall Damage", fd[0], fd[1]);
  String[] mr = manaRegen(u);
  add(rows, "Mana Regen", mr[0], mr[1]);
  gearRow(rows, g, a, gearOn, "stam");
}""")
M(scl, r"""
public static void combatTab(java.util.ArrayList rows, java.util.UUID u) {
  java.util.HashMap g = kv(br().get("gear:stats:" + u.toString()));
  java.util.HashMap a = kv(br().get("gear:extra:" + u.toString()));
  boolean gearOn = br().get("gear:fn:stats") instanceof java.util.function.Function;
  gearRow(rows, g, a, gearOn, "dmg");
  gearRow(rows, g, a, gearOn, "chg");
  gearRow(rows, g, a, gearOn, "tdmg");
  groupRow(rows, g, a, ELEM_K, ELEM_S, "Elemental Damage", true);
  groupRow(rows, g, a, RAW_K, RAW_S, "Raw Elemental Damage", false);
  gearRow(rows, g, a, gearOn, "lsteal");
  gearRow(rows, g, a, gearOn, "msteal");
  gearRow(rows, g, a, gearOn, "hpr");
  gearRow(rows, g, a, gearOn, "hprp");
  classDamage(rows, u, kv(br().get("skill:" + u.toString())));
}""")
M(scl, r"""
public static void gatheringTab(java.util.ArrayList rows, java.util.UUID u) {
  java.util.HashMap sk = kv(br().get("skill:" + u.toString()));
  boolean on = br().get("skill:fn:level") instanceof java.util.function.Function;
  for (int i = 0; i < FORT_N.length; i++) fortune(rows, u, sk, on, i);
  for (int i = 0; i < WIS_N.length; i++) wisdom(rows, u, on, i);
}""")
# fix round: the other class skills get one row each while the tab has room (ROWS), else they are packed into as few
# "Other class skills" rows as fit LINE_MAX (never one clipped "..." row - a player who tried every class has 6)
M(scl, r"""
public static void otherRows(java.util.ArrayList rows, String joined, int n) {
  String[] parts = joined.split(", ");
  if (rows.size() + parts.length <= ROWS) {
    for (int i = 0; i < parts.length; i++) {
      int sp = parts[i].lastIndexOf(' ');
      if (sp <= 0) continue;
      add(rows, parts[i].substring(0, sp), "Level " + parts[i].substring(sp + 1), "another class's weapon skill");
    }
    return;
  }
  String name = "Other class skills";
  String val = String.valueOf(n);
  int room = LINE_MAX - name.length() - val.length() - 2;
  StringBuilder line = new StringBuilder();
  boolean first = true;
  for (int i = 0; i < parts.length; i++) {
    if (line.length() > 0 && line.length() + 2 + parts[i].length() > room) {
      add(rows, name, first ? val : "", line.toString());
      first = false;
      line = new StringBuilder();
    }
    if (line.length() > 0) line.append(", ");
    line.append(parts[i]);
  }
  if (line.length() > 0) add(rows, name, first ? val : "", line.toString());
}""")
M(scl, r"""
public static void skillsTab(java.util.ArrayList rows, java.util.UUID u) {
  Object[] ov = overallInfo(u);
  int lv = overall(u);
  if (ov != null) {
    StringBuilder sb = new StringBuilder();
    if (ov[1] instanceof Number) sb.append("average ").append(num(((Number) ov[1]).intValue() / 10.0));
    if (ov[2] instanceof Number) sb.append(" over ").append(((Number) ov[2]).intValue()).append(" skills");
    double hp = ov[3] instanceof Number ? ((Number) ov[3]).doubleValue() : 0.0;
    double mn = ov[4] instanceof Number ? ((Number) ov[4]).doubleValue() : 0.0;
    if (Math.abs(hp) >= 0.05) sb.append(", ").append(signed(hp)).append(" Health");
    if (Math.abs(mn) >= 0.05) sb.append(", ").append(signed(mn)).append(" Mana");
    add(rows, "Overall Level", String.valueOf(lv), sb.toString());
  } else {
    add(rows, "Overall Level", lv >= 0 ? String.valueOf(lv) : "-", lv >= 0 ? "" : "needs SkyySkills");
  }
  java.util.ArrayList ps = pairs(br().get("skill:" + u.toString()));
  if (ps.isEmpty()) { add(rows, "Skills", "-", "no skill data yet - SkyySkills loads it when you play"); return; }
  String cs = classSkill(u);
  StringBuilder others = new StringBuilder();
  int nOther = 0;
  for (int i = 0; i < ps.size(); i++) {
    String[] p = (String[]) ps.get(i);
    if (isClassSkill(p[0])) {
      if (cs != null && cs.equals(p[0])) add(rows, p[0], "Level " + p[1], "your class weapon skill");
      else {
        if (others.length() > 0) others.append(", ");
        others.append(p[0]).append(' ').append(p[1]);
        nOther++;
      }
    } else add(rows, p[0], "Level " + p[1], "");
  }
  if (nOther > 0) otherRows(rows, others.toString(), nOther);
}""")
M(scl, r"""
public static void profileTab(java.util.ArrayList rows, java.util.UUID u) {
  String p = profileName(u);
  add(rows, "Profile", p == null ? "-" : p, "Change Profile opens your profile list");
  String c = className(u);
  String cs = classSkill(u);
  add(rows, "Class", c == null ? "none yet" : c, classSyncing(u) ? "class syncing, Refresh in a moment" : cs == null ? "" : cs + " is your class weapon skill");
  long pu = @PKG@.MenuUtil.purse(u);
  add(rows, "Purse", pu < 0L ? "-" : @PKG@.MenuUtil.fmt(pu), pu < 0L ? "SkyyCoins is not on this server" : "coins you carry");
  long bk = @PKG@.MenuUtil.bank(u);
  add(rows, "Bank", bk < 0L ? "-" : @PKG@.MenuUtil.fmt(bk), bk < 0L ? "open the Bank to load it" : "coins in the bank - safe when you die");
  java.util.Map b = br();
  add(rows, "Accessory Bag", String.valueOf(@PKG@.MenuUtil.csvCount(b.get("acc:has:" + u.toString()))),
      "bench accessories, and " + @PKG@.MenuUtil.csvCount(b.get("acc:tal:" + u.toString())) + " talismans");
  add(rows, "Collection Recipes", String.valueOf(@PKG@.MenuUtil.csvCount(b.get("coll:recipes:" + u.toString()))),
      "recipes your collections unlocked");
}""")
M(scl, r"""
public static java.util.ArrayList rows(java.util.UUID u, int tab, Object[] vit) {
  java.util.ArrayList rows = new java.util.ArrayList();
  try {
    if (tab == 0) mainTab(rows, u, vit);
    else if (tab == 1) combatTab(rows, u);
    else if (tab == 2) gatheringTab(rows, u);
    else if (tab == 3) skillsTab(rows, u);
    else profileTab(rows, u);
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("stats page rows failed: " + t);
    add(rows, "Error", "-", "could not read your stats - see the server log");
  }
  return rows;
}""")
'''
rep('''# ================= MenuPage (inline page; views switched with rebuild()) =================''',
    STATS_CALC.lstrip("\n") + '''
# ================= MenuPage (inline page; views switched with rebuild()) =================''')

# ================================================================================================ StatsPage fields + constructor (constructors first)
rep('''# 0.3 AdminPage fields + constructor right here too (MenuPage.openAdmin and the page's "< SkyWynn Menu" button use each other's''',
    '''# 0.3.10 StatsPage fields + constructor here too (MenuPage.openStats and the page's "< SkyWynn Menu" button use each other's
# constructors). tab = 0 Main, 1 Combat, 2 Gathering, 3 Skills, 4 Profile.
for f in ("public int tab;", "public String status;"):
    F(stp, f)
C(stp, r"""
public StatsPage(@PR@ pr, int tab) {
  super(pr, @LIFE@.CanDismiss);
  this.tab = tab < 0 || tab >= @PKG@.StatsCalc.TABS.length ? 0 : tab;
  this.status = "";
}""")
# 0.3 AdminPage fields + constructor right here too (MenuPage.openAdmin and the page's "< SkyWynn Menu" button use each other's''')

# ================================================================================================ the Your Profile hover text: short lines
rep('''M(page, r"""
public String profileBody() {
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map br = @PKG@.MenuUtil.bridge();
  StringBuilder sb = new StringBuilder();
  sb.append("Your SkyWynn profile, ").append(@PKG@.MenuUtil.safe(this.playerRef.getUsername())).append('.');
  sb.append("\\nPurse: ").append(purseText());
  long bk = @PKG@.MenuUtil.bank(u);
  sb.append("\\nBank: ").append(bk < 0L ? "open the Bank to load it" : @PKG@.MenuUtil.fmt(bk) + " coins");
  String sk = @PKG@.MenuUtil.skills(u);
  sb.append("\\nSkills: ").append(sk == null ? "no skill data yet" : sk);
  sb.append("\\nAccessory Bag: ").append(@PKG@.MenuUtil.csvCount(br.get("acc:has:" + u.toString()))).append(" bench accessories, ")
    .append(@PKG@.MenuUtil.csvCount(br.get("acc:tal:" + u.toString()))).append(" talismans");
  sb.append("\\nRecipes unlocked by collections: ").append(@PKG@.MenuUtil.csvCount(br.get("coll:recipes:" + u.toString())));
  return sb.toString();
}""")''', '''# 0.3.10: short lines (the info box's lines are 20 px, unwrapped, about 80 characters: the 0.3.9 "Skills:" list was cut off) - every
# detail line clipped to StatsCalc.LINE_MAX; the whole list is on the Stats page the tile opens
M(page, r"""
public String profileBody() {
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map br = @PKG@.MenuUtil.bridge();
  int max = @PKG@.StatsCalc.LINE_MAX;
  StringBuilder sb = new StringBuilder();
  sb.append("Your SkyWynn profile, ").append(@PKG@.MenuUtil.safe(this.playerRef.getUsername())).append(". Click for all your stats.");
  String cls = @PKG@.StatsCalc.className(u);
  int ov = @PKG@.StatsCalc.overall(u);
  sb.append("\\n").append(@PKG@.MenuUtil.clip("Class: " + (cls == null ? "none yet" : cls) + (ov >= 0 ? "   -   Overall Level " + ov : ""), max));
  sb.append("\\n").append(@PKG@.MenuUtil.clip("Purse: " + purseText(), max));
  long bk = @PKG@.MenuUtil.bank(u);
  sb.append("\\n").append(@PKG@.MenuUtil.clip("Bank: " + (bk < 0L ? "open the Bank to load it" : @PKG@.MenuUtil.fmt(bk) + " coins"), max));
  String top = @PKG@.StatsCalc.topSkills(u, 3);
  sb.append("\\n").append(@PKG@.MenuUtil.clip("Top skills: " + (top == null ? "no skill data yet" : top), max));
  sb.append("\\n").append(@PKG@.MenuUtil.clip("Accessory Bag: " + @PKG@.MenuUtil.csvCount(br.get("acc:has:" + u.toString())) + " accessories, "
    + @PKG@.MenuUtil.csvCount(br.get("acc:tal:" + u.toString())) + " talismans", max));
  sb.append("\\n").append(@PKG@.MenuUtil.clip("Recipes unlocked by collections: " + @PKG@.MenuUtil.csvCount(br.get("coll:recipes:" + u.toString())), max));
  return sb.toString();
}""")''')

# ================================================================================================ the tile opens the page
rep('''M(page, r"""
public void click(@REF@ ref, @ST@ st, int idx, String act) {''', '''# 0.3.10: the Your Profile tile opens the Stats page straight from the menu (never closing first); the grid is emptied once before
# the hand-off like every page hand-off (openSettings / openAdmin)
M(page, r"""
public void openStats(@REF@ ref, @ST@ st) {
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  clearGrid();
  p.getPageManager().openCustomPage(ref, st, new @PKG@.StatsPage(this.playerRef, 0));
}""")
M(page, r"""
public void click(@REF@ ref, @ST@ st, int idx, String act) {''')
rep('''  if (act.equals("settings")) { openSettings(ref, st); return; }
  if (act.equals("admin")) { openAdmin(ref, st, null); return; }
  if (act.startsWith("modcfg:")) {''', '''  if (act.equals("settings")) { openSettings(ref, st); return; }
  if (act.equals("admin")) { openAdmin(ref, st, null); return; }
  if (act.equals("profile")) { openStats(ref, st); return; }
  if (act.startsWith("modcfg:")) {''')

# ================================================================================================ StatsPage methods, StatsTask, StatsCmd
STATS_PAGE = r'''
# ================= 0.3.10 StatsPage: the Stats page (one inline page, tabs switched with rebuild(); no timers, no MouseEntered/Exited) =================
# build() reads everything again (the vitals on this world thread), so Refresh / a tab click shows the current numbers. Click payloads
# are matched with both quotes. Change Profile = the player's own /profiles through the engine command manager (installed + permission
# checked first, like the menu tiles); the page never closes itself before another page opens.
# fix round: /profiles counts only when it is SkyyProfiles' own command (PROFILES_CMD) - another pack mod (EndlessLeveling's /profile has
# the alias "profiles") may win the name; then the button is hidden, exactly as without SkyyProfiles.
F(stp, 'public static final String PROFILES_CMD = "com.skyy.profiles.ProfilesCmd";')
M(stp, r"""
public static @ACM@ profilesCmd() {
  @ACM@ c = @PKG@.MenuUtil.cmd("profiles");
  if (c == null) return null;
  return PROFILES_CMD.equals(c.getClass().getName()) ? c : null;
}""")
M(stp, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  if (this.tab < 0 || this.tab >= @PKG@.StatsCalc.TABS.length) this.tab = 0;
  Object[] vit = null;
  if (this.tab == 0) vit = @PKG@.StatsCalc.vitals(st, ref);
  java.util.ArrayList rows = @PKG@.StatsCalc.rows(u, this.tab, vit);
  boolean prof = profilesCmd() != null;
""" + "\n".join("  " + ln for ln in ST_SHELL_JAVA.split("\n")) + r"""
""" + "\n".join("  " + ln for ln in ST_TABS_JAVA.split("\n")) + r"""
  for (int t = 0; t < @PKG@.StatsCalc.TABS.length; t++) ev.addEventBinding(@BT@.Activating, "#SkyyStatTab" + t, @EVD@.of("a", "ttab" + t));
  int n = rows.size() < @PKG@.StatsCalc.ROWS ? rows.size() : @PKG@.StatsCalc.ROWS;
  for (int i = 0; i < n; i++) {
    String[] r = (String[]) rows.get(i);
""" + "\n".join("    " + ln for ln in ST_ROW_JAVA.split("\n")) + r"""
    b.set("#SkyyStatN" + i + ".Text", r[0]);
    b.set("#SkyyStatV" + i + ".Text", r[1]);
    b.set("#SkyyStatS" + i + ".Text", r[2]);
  }
  """ + ST_FOOT_JAVA["menu"] + r"""
  """ + ST_FOOT_JAVA["refresh"] + r"""
  if (prof) {
    """ + ST_FOOT_JAVA["profile"] + r"""
    ev.addEventBinding(@BT@.Activating, "#SkyyStatProfile", @EVD@.of("a", "tprofile"));
  } else {
    """ + ST_FOOT_JAVA["noprofile"] + r"""
  }
  """ + ST_FOOT_JAVA["fill"] + r"""
  """ + ST_FOOT_JAVA["close"] + r"""
  ev.addEventBinding(@BT@.Activating, "#SkyyStatMenu", @EVD@.of("a", "tmenu"));
  ev.addEventBinding(@BT@.Activating, "#SkyyStatRefresh", @EVD@.of("a", "trefresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyStatClose", @EVD@.of("a", "tclose"));
  b.set("#SkyyStatHead.Text", @PKG@.StatsCalc.header(u, this.playerRef.getUsername()));
  b.set("#SkyyStatSub.Text", @PKG@.StatsCalc.SUB);
  b.set("#SkyyStatNote.Text", @PKG@.StatsCalc.NOTES[this.tab]);
  b.set("#SkyyStatMsg.Text", this.status == null ? "" : this.status);
}""")
# StatsTask's answer (before StatsTask, which calls it): the page is still open 0.9 s after Change Profile -> /profiles answered in chat
M(stp, r"""
public void answer() {
  this.status = "Your profile list did not open - read your chat.";
  rebuild();
}""")
M(stp, r"""
public @PR@ who() { return this.playerRef; }""")

# ================= StatsTask: one redraw 0.9 s after Change Profile, ONLY while the Stats page is still the player's open page in the
# same world (RefreshTask pattern: scheduler -> World.execute -> check on the world thread; the scheduler = PageGuard.EXEC, which setup()
# sets to HytaleServer.SCHEDULED_EXECUTOR - no scheduler = no answer, the page simply stays as it is). A page the client no longer shows is never
# redrawn (a redraw it never acknowledges would make every page ignore clicks - the 0.3.6 rule).
sta.addInterface(pool.get("java.lang.Runnable"))
F(sta, "public @PKG@.StatsPage page;")
F(sta, "public @PR@ pr;")
F(sta, "public @WLD@ expected;")
C(sta, r"""
public StatsTask(@PKG@.StatsPage page, @PR@ pr) { this.page = page; this.pr = pr; this.expected = null; }""")
M(sta, r"""
public static boolean schedule(@PKG@.StatsPage page, @PR@ pr, long ms) {
  java.util.concurrent.ScheduledExecutorService ex = @PKG@.PageGuard.EXEC;
  if (ex == null) return false;
  try { ex.schedule(new @PKG@.StatsTask(page, pr), ms, java.util.concurrent.TimeUnit.MILLISECONDS); return true; }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not schedule the stats page check: " + t); return false; }
}""")
M(sta, r"""
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
    if (p == null) return;
    @PGM@ pm = p.getPageManager();
    if (pm == null || pm.getCustomPage() != this.page) return;
    this.page.answer();
  } catch (Throwable t) { @PKG@.MenuUtil.warn("stats page check failed: " + t); }
}""")
M(stp, r"""
public void changeProfile(@REF@ ref, @ST@ st) {
  @ACM@ c = profilesCmd();
  if (c == null) { this.status = "Profiles are not on this server."; rebuild(); return; }
  boolean ok = false;
  try { ok = c.hasPermission(this.playerRef); } catch (Throwable t) { @PKG@.MenuUtil.warn("permission check for /profiles failed: " + t); ok = false; }
  if (!ok) { this.status = "You do not have permission for /profiles. Ask an admin."; rebuild(); return; }
  try { @CMGR@.get().handleCommand(this.playerRef, "profiles"); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("/profiles from the stats page failed: " + t); this.status = "/profiles could not be run."; rebuild(); return; }
  @PKG@.StatsTask.schedule(this, this.playerRef, 900L);
}""")
M(stp, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    if (data.indexOf("\"tclose\"") >= 0) {
      @PLA@ pc = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      if (pc != null) pc.getPageManager().setPage(ref, st, @PGE@.None);
      return;
    }
    if (data.indexOf("\"tmenu\"") >= 0) {
      @PLA@ pm = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      if (pm != null) pm.getPageManager().openCustomPage(ref, st, new @PKG@.MenuPage(this.playerRef, "main"));
      return;
    }
    if (data.indexOf("\"tprofile\"") >= 0) { this.status = ""; changeProfile(ref, st); return; }
    for (int i = 0; i < @PKG@.StatsCalc.TABS.length; i++) {
      if (data.indexOf("\"ttab" + i + "\"") >= 0) { this.tab = i; this.status = ""; rebuild(); return; }
    }
    if (data.indexOf("\"trefresh\"") >= 0) { this.status = "Refreshed - these are your stats right now."; rebuild(); return; }
    rebuild();
  } catch (Throwable t) { @PKG@.MenuUtil.warn("stats page click failed: " + t); }
}""")

# ================= /stats (alias /profilestats): opens the Stats page; no arguments; everyone (hytale:Adventurer) =================
C(stc, r"""
public StatsCmd() {
  super("stats", "Open your Stats page - every stat of your character");
  addAliases(new String[] { "profilestats" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(stc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ player = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new @PKG@.StatsPage(pr, 0));
  } catch (Throwable t) {
    @PKG@.MenuUtil.warn("/stats failed: " + t);
    pr.sendMessage(@MSG@.raw("[Stats] Could not open your stats page."));
  }
}""")

'''
rep('''# ================= 0.2 SettingsPage (research/Settings-Spec.md 4.2-4.4): one inline page, tabs / rows switched with rebuild() =================''',
    STATS_PAGE.lstrip("\n") + '''# ================= 0.2 SettingsPage (research/Settings-Spec.md 4.2-4.4): one inline page, tabs / rows switched with rebuild() =================''')

# ================================================================================================ plugin: /stats + the ready line
rep('''  getCommandRegistry().registerCommand(new @PKG@.AdminCmd());
''', '''  getCommandRegistry().registerCommand(new @PKG@.AdminCmd());
  // 0.3.10: /stats (/profilestats) - a clash with another mod's /stats is logged and the menu still loads
  try { getCommandRegistry().registerCommand(new @PKG@.StatsCmd()); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /stats (another mod may own it) - the Your Profile tile still opens the Stats page: " + t); }
''')
rep('''Server Setup: /modconfig (/serversetup) for admins; page guard on''',
    '''Server Setup: /modconfig (/serversetup) for admins; Stats page: the Your Profile tile, /stats (/profilestats), page look """ + SUI_KIT_ID + r"""; page guard on''')
rep('''WRITE = (dat, utl, giv, mcfg, sreg, sst, ssv, tip, sld, sgf, srf, ssf, sdc, page, spg, apg, ast, ref_, clo_, guard, stale, mwat, fac, cmd, scmd, acmv, acmd, grt, rdy, seen, quit_, gtk, pl)''',
    '''WRITE = (dat, utl, giv, mcfg, sreg, sst, ssv, tip, sld, sgf, srf, ssf, sdc, page, spg, apg, ast, ref_, clo_, guard, stale, mwat, fac, cmd, scmd, acmv, acmd, grt, rdy, seen, quit_, gtk,
         scl, stp, sta, stc, pl)''')
rep('''print("inline UI strings verified in MenuData.class:", len(UI) + len(UI_INFO) + len(SET_UI_ALL) + len(ADM_UI_ALL))''',
    '''print("inline UI strings verified in MenuData.class:", len(UI) + len(UI_INFO) + len(SET_UI_ALL) + len(ADM_UI_ALL))
# 0.3.10: the Stats page's fixed kit markup is intact in StatsPage.class
_sp = cp_utf8(open(os.path.join(OUT, "com", "skyy", "menu", "StatsPage.class"), "rb").read())
for _m in ST_STATIC:
    assert _m in _sp, "stats page markup missing from StatsPage.class: " + _m[:80]
print("stats page markup verified in StatsPage.class:", len(ST_STATIC), "fixed parts")''')
rep('''players, party, guild, a list of every mod with its commands, /settings''',
    '''players, party, guild, your Stats page (/stats), a list of every mod with its commands, /settings''')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.9 outside the recorded changes"
compile(s, dst, "exec")
out = s.replace(LF, NL) if NL != LF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.9 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
