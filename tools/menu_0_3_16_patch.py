"""Derive SkyyMenu/build_skyymenu_0.3.16.py from the LIVE SkyyMenu 0.3.15 (python tools/menu_0_3_16_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_15_patch.py -> 0.3.15 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch, never re-build it) -> this patch -> 0.3.16. 0.3.15's files stay untouched. The harness
SkyyMenu/test_skyymenu_0.3.16.py is its own file (derived from test_skyymenu_0.3.15.py: it runs the 0.3.15 harness on the new jar next to
a control run = every old check carried forward, plus the new sections).

0.3.16 = LAYOUT D + THE OWN TILE ICONS + PER-TILE VISIBILITY RULES. Skyy's own words (2026-10-10, docs/answered/ui.md):
  "lets make an Icon for everything in this menu. when you open it, it starts on the center, where the hud editor is, id put the teleporter
   there, and put the most used things around that. with the less used things like mods, and server settings separate near the bottom. in a
   row or something."  /  "go with D"  /  (on art/menu-icons/sheet.png) "beautiful! i love it"  /  "can we control what's visible in the
   menu with permissions? or do we have to make several menus?"
  1. LAYOUT D (main view only; 9 x 6, slot = row * 9 + col). Teleport on slot 13 (the slot under the mouse when the menu opens = the old
     HUD Editor slot). The plus: row 0 Pets 3 / Skills 4 / Accessory Bag 5; row 1 Island Menu 12 / TELEPORT 13 / Crafting 14; row 2 Bank
     21 / Bazaar 22 / Auction House 23; row 3 Vault 29 / Reforge 30 / Identify 31 / Pocket Dimension 32 / Your Profile 33; row 4
     Collections 40 (39 / 41 kept FREE for Classes / Fishing). LEFT bar col 0: Players 0, Party 9, Guild 18 (27 free for Quests), Wardrobe
     36 = ONLY while a wardrobe:fn:open bridge Function exists (click = calls it). RIGHT bar col 8: Hover Tooltips 8, Settings 17, HUD
     Editor 26, Mods 35, Server Setup 44. Back / Prev / Close / Next (45 / 48 / 49 / 50) as before; every other view unchanged; a hidden
     tile leaves its slot EMPTY (nothing shifts). The "tooltips off" hint names the speech bubble (the Hover Tooltips icon).
  2. ICONS: the 23 approved icons of art/menu-icons/ (manifest.json sha256 + bytes checked at build, the icon_item_png way) as hidden
     icon-only items Skyy_Menu_Icon_<Name> (the 0.3.11 ICON_ITEMS pattern: Variant, no Categories / Recipe / Interactions, held look of
     the vanilla Farming_Collar like the pet icons). AccessoryBag = the item 0.3.11 already ships (art/menu-icons' copy is checked to be
     byte-identical to it); Pets = ICON_PETS (the fallback - the tile keeps showing the pet's own art); no id / path is vanilla.
  3. PER-TILE VISIBILITY RULES (TILE_RULES, data-driven; MenuData E_PERM / E_OPEN / E_NEED / E_UNLOCK; MenuPage.tileVisible): a tile is
     drawn only if (a) perm: the player has the node (ADMIN_NODE = the existing admin check), unless (open) a Server Setup switch opens it
     to everyone; (b) need: a bridge key must hold a java.util.function.Function; (c) unlock: if the bridge key holds a Function,
     apply(UUID player) must answer Boolean.TRUE (an absent key = shown as today; a throwing / non-TRUE answer = hidden, warned once per
     key); (d) the owning mod present as before (greyed "(not installed)" / the Pets tile hidden without SkyyPets). Today's rules as data:
     Server Setup = perm skyymenu.modconfig; Mods = perm skyymenu.modconfig, opened to all by menu.modsHelp (default on - so players see it
     as today); Bank = unlock bank:fn:unlocked (nobody publishes it yet -> shown as today); Wardrobe = need wardrobe:fn:open.
No saved data, no command change; ROUND_PINS = {}.
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.15 outside them, byte for byte.
"""
import os
import re
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.15.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.16.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
OLD = s
assert 'VERSION = "0.3.15"' in s and "0.3.15: THE MENU ITEM WEARS THE NEW SKYWYNN EMBLEM" in s and "TILE_RULES" not in s, "not the generated 0.3.15 script"
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
if _set is not None and _set.get("SkyyMenu") != "0.3.15":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.15" % _set.get("SkyyMenu"))

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.15: THE MENU ITEM WEARS''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.16: LAYOUT D + OWN TILE ICONS + PER-TILE VISIBILITY RULES (notes: tools/menu_0_3_16_patch.py; Skyy 2026-10-10 "go with D",
       "beautiful! i love it", "can we control what's visible in the menu with permissions?"): the main view = layout D (Teleport on
       slot 13 under the mouse, the plus around it, social bar left, admin bar right, MAIN_D); every main tile wears its art/menu-icons
       icon (22 new hidden icon items Skyy_Menu_Icon_<Name>, MENU_ICONS); TILE_RULES (perm node / Server Setup switch / bridge Function
       needed / bridge unlock Function) decide which tiles are drawn - a hidden tile leaves its slot empty; a Wardrobe tile (slot 36)
       appears only while SkyyWardrobe publishes wardrobe:fn:open (click = apply(UUID)). No saved data; ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.16.py (every 0.3.15 check carried forward + CC 0.3.15 -> 0.3.16 + JT the icon items + D the
  layout, admin vs player, hidden-tile gaps, unlock / need / Wardrobe executed through the engine's PageManager + AA the engine-access audit).
0.3.15: THE MENU ITEM WEARS''')
rep('VERSION = "0.3.15"\n', 'VERSION = "0.3.16"\n')

# ================================================================================================ the icon items
MENU_ICONS = [  # (art name, tile name)
    ("YourProfile", "Your Profile"), ("Pets", "Pets"), ("HoverTooltips", "Hover Tooltips"), ("Teleport", "Teleport"),
    ("PocketDimension", "Pocket Dimension"), ("AccessoryBag", "Accessory Bag"), ("HudEditor", "HUD Editor"), ("Crafting", "Crafting"),
    ("Skills", "Skills"), ("Collections", "Collections"), ("IslandMenu", "Island Menu"), ("Bank", "Bank"), ("Vault", "Vault"),
    ("Bazaar", "Bazaar"), ("AuctionHouse", "Auction House"), ("Reforge", "Reforge"), ("Identify", "Identify"), ("Players", "Players"),
    ("Party", "Party"), ("Guild", "Guild"), ("Settings", "Settings"), ("Mods", "Mods"), ("ServerSetup", "Server Setup"),
]
rep('''ICON_PETS = "Farming_Collar"                  # 0.3.14: the Pets tile without a pet icon (vanilla Deco_Dog_Collar picture)
''', '''# 0.3.16: THE OWN TILE ICONS (Skyy 2026-10-10 on art/menu-icons/sheet.png: "beautiful! i love it"): one icon-only item per main tile,
# Skyy_Menu_Icon_<Name>, picture = art/menu-icons/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_<Name>.png (shipped at the same path under
# Common/, checked against art/menu-icons/manifest.json sha256 + bytes); held look = the vanilla Farming_Collar (like the pet icons - these
# items are never held). AccessoryBag is 0.3.11's item (the art folder's copy is checked to be byte-identical to it).
MENU_ICON_DIR = "art/menu-icons"
MENU_ICONS = %r
for _nm, _tile in MENU_ICONS:
    if _nm != "AccessoryBag":
        ICON_ITEMS["Skyy_Menu_Icon_" + _nm] = ("%%s/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%%s.png" %% (MENU_ICON_DIR, _nm),
                                             "Icons/ItemsGenerated/Skyy_Menu_Icon_%%s.png" %% _nm, MENU_ICON_DIR + "/manifest.json", _tile,
                                             "Farming_Collar")
MENU_ICON_OF = dict((_tile, "Skyy_Menu_Icon_" + _nm) for _nm, _tile in MENU_ICONS)   # 0.3.16: tile name -> its icon item
ICON_PETS = "Skyy_Menu_Icon_Pets"             # 0.3.14: the Pets tile without a pet icon (0.3.16: our own collar icon, was the vanilla Farming_Collar)
''' % (MENU_ICONS,))

# ================================================================================================ LAYOUT D (ENTRIES main rows)
MAIN_D = {  # tile -> (row, col)
    "Pets": (0, 3), "Skills": (0, 4), "Accessory Bag": (0, 5),
    "Island Menu": (1, 3), "Teleport": (1, 4), "Crafting": (1, 5),
    "Bank": (2, 3), "Bazaar": (2, 4), "Auction House": (2, 5),
    "Vault": (3, 2), "Reforge": (3, 3), "Identify": (3, 4), "Pocket Dimension": (3, 5), "Your Profile": (3, 6),
    "Collections": (4, 4),
    "Players": (0, 0), "Party": (1, 0), "Guild": (2, 0), "Wardrobe": (4, 0),
    "Hover Tooltips": (0, 8), "Settings": (1, 8), "HUD Editor": (2, 8), "Mods": (3, 8), "Server Setup": (4, 8),
}
a = s.index("ENTRIES = [\n")
b = s.index("    # ---- Teleport (warps are added automatically")
blk = s[a:b]
new = blk
seen = []


def slot_icon(m):
    name = m.group(3)
    seen.append(name)
    r, c = MAIN_D[name]
    icon = "ICON_PETS" if name == "Pets" else ('"Skyy_Menu_Icon_%s"' % dict((t, n) for n, t in MENU_ICONS)[name])
    return '("main", %d, %s, "%s",' % (r * 9 + c, icon, name)


new = re.sub(r'\("main", (\d+), +([A-Za-z_"0-9]+), "([^"]+)",', slot_icon, new)
assert sorted(seen) == sorted(t for _n, t in MENU_ICONS), "every main tile re-slotted once: %s" % seen
new = new.replace('''    # ---- main menu. Row 1 = Skyy's order (Teleport, Pocket Dimension, Accessory Bag, HUD editor, then the rest), row 2 = your island +
    # your stuff, row 3 = people, row 4 = the mod list; top right = the per-player tooltip switch (0.1.3 layout)
''', '''    # ---- main menu. 0.3.16: LAYOUT D (Skyy 2026-10-10 "go with D"; MAIN_D below is the map, checked at build): Teleport on slot 13 (the
    # slot under the mouse when the menu opens), the most used tiles in a plus around it, the social bar down the LEFT edge, the admin /
    # options bar down the RIGHT edge; every tile wears its own art/menu-icons icon (MENU_ICON_OF). Before 0.3.16: the 0.1.3 rows.
''', 1)
assert new.count("0.3.16: LAYOUT D") == 1
WARD = '''    # 0.3.16: THE WARDROBE TILE (left bar, row 4; Skyy's layout D "Players, Party, Guild + future Quests, Wardrobe") - drawn ONLY while
    # SkyyWardrobe publishes the bridge Function wardrobe:fn:open (TILE_RULES "need"); the click calls apply(UUID player) on the world
    # thread, which opens SkyyWardrobe's page (TRUE = opened). Stand-in icon = the vanilla Village Wardrobe until its own art exists.
    ("main", 36, "Furniture_Village_Wardrobe", "Wardrobe",
        ["Your saved loadouts - one click swaps between them.", "Command: /wardrobe"],
        "Click to open!", "bridge:wardrobe:fn:open"),
'''
new = new + WARD
rep(blk, new)

# the tile rules + the layout map, right before the Java data is made (every name above is defined there)
rep('''E_VIEW = [e[0] for e in ENTRIES]; E_SLOT = [e[1] for e in ENTRIES]; E_ICON = [e[2] for e in ENTRIES]
''', '''# 0.3.16: LAYOUT D - tile -> (row, col) of the main view (slot = row * 9 + col); 39 / 41 (Classes / Fishing) and 27 (Quests) stay FREE
MAIN_D = %r
MAIN_FREE = (27, 39, 41)
# 0.3.16: PER-TILE VISIBILITY RULES (Skyy "can we control what's visible in the menu with permissions? or do we have to make several
# menus?" -> ONE menu, a rule per tile). tile name -> {"perm": node the player needs (ADMIN_NODE = the admin check MenuUtil.isAdmin),
# "open": a Server Setup switch that shows the tile to everyone anyway (only "modsHelp" = menu.modsHelp), "need": a bridge key that must
# hold a java.util.function.Function, "unlock": a bridge key - while it holds a Function, apply(UUID player) must answer Boolean.TRUE (an
# absent key = shown as today)}. A hidden tile leaves its slot empty. Ranks / earned unlocks plug in here later (data only).
TILE_RULES = {
    "Server Setup": {"perm": ADMIN_NODE},
    "Mods": {"perm": ADMIN_NODE, "open": "modsHelp"},
    "Bank": {"unlock": "bank:fn:unlocked"},
    "Wardrobe": {"need": "wardrobe:fn:open"},
}
TILE_OPEN = ("modsHelp",)                     # 0.3.16: the switches a rule may name (MenuPage.tileVisible knows each one)
_main = dict((e[3], e) for e in ENTRIES if e[0] == "main")
assert sorted(_main) == sorted(MAIN_D) and len(_main) == len([e for e in ENTRIES if e[0] == "main"]), "0.3.16: every main tile has a D slot"
for _t, (_r, _c) in MAIN_D.items():
    assert 0 <= _r < 5 and 0 <= _c < 9 and _main[_t][1] == _r * 9 + _c, "0.3.16: %%s belongs at row %%d col %%d = slot %%d" %% (_t, _r, _c, _r * 9 + _c)
assert len(set(MAIN_D.values())) == len(MAIN_D) and not set(MAIN_FREE) & set(e[1] for e in _main.values()), "0.3.16: D slots unique, free slots free"
assert _main["Teleport"][1] == 13 and _main["Teleport"][6] == "view:tp", "0.3.16: Teleport on slot 13 (under the mouse when the menu opens)"
assert [_main[t][1] for t in ("Players", "Party", "Guild", "Wardrobe")] == [0, 9, 18, 36], "0.3.16: the social bar down the left edge"
assert [_main[t][1] for t in ("Hover Tooltips", "Settings", "HUD Editor", "Mods", "Server Setup")] == [8, 17, 26, 35, 44], "0.3.16: the right bar"
for _t, _e in _main.items():
    assert _e[2] == (MENU_ICON_OF.get(_t) if _t not in ("Pets", "Wardrobe") else _e[2]), "0.3.16: %%s wears its own icon" %% _t
assert _main["Pets"][2] == ICON_PETS and _main["Wardrobe"][2] == "Furniture_Village_Wardrobe" and _main["Wardrobe"][6] == "bridge:wardrobe:fn:open"
_BRK = re.compile(r"^[a-z][a-z0-9]*:fn:[A-Za-z][A-Za-z0-9]*$")
for _t, _rl in TILE_RULES.items():
    assert _t in _main and set(_rl) <= set(["perm", "open", "need", "unlock"]) and _rl, "0.3.16: rule of an unknown tile / key: %%s %%s" %% (_t, _rl)
    assert "perm" not in _rl or re.match(r"^[a-z][a-z0-9]*(\\.[a-z0-9]+)+$", _rl["perm"]), "0.3.16: %%s perm node" %% _t
    assert "open" not in _rl or ("perm" in _rl and _rl["open"] in TILE_OPEN), "0.3.16: %%s open needs a perm + a known switch" %% _t
    assert all(_BRK.match(_rl[_k]) for _k in ("need", "unlock") if _k in _rl), "0.3.16: %%s bridge keys look like <mod>:fn:<name>" %% _t
assert [e[3] for e in ENTRIES if e[6] == "admin"] == ["Server Setup"] and TILE_RULES["Server Setup"] == {"perm": ADMIN_NODE}, "0.3.16: Server Setup = admins"
assert [e[3] for e in ENTRIES if e[6] == "view:mods"] == ["Mods"] and TILE_RULES["Mods"] == {"perm": ADMIN_NODE, "open": "modsHelp"}, \\
    "0.3.16: Mods = admins, or everyone while menu.modsHelp is on (0.3.15's rule)"
for _e in ENTRIES:
    assert not _e[6].startswith("bridge:") or (_e[0] == "main" and TILE_RULES.get(_e[3], {}).get("need") == _e[6][7:]), \\
        "0.3.16: a bridge tile is drawn only while its Function exists: %%s" %% _e[3]
def _rule(e, k):
    return TILE_RULES.get(e[3], {}).get(k, "") if e[0] == "main" else ""
E_PERM = [_rule(e, "perm") for e in ENTRIES]; E_OPEN = [_rule(e, "open") for e in ENTRIES]
E_NEED = [_rule(e, "need") for e in ENTRIES]; E_UNLOCK = [_rule(e, "unlock") for e in ENTRIES]
E_VIEW = [e[0] for e in ENTRIES]; E_SLOT = [e[1] for e in ENTRIES]; E_ICON = [e[2] for e in ENTRIES]
''' % (MAIN_D,))

# the action check knows bridge: tiles
rep('''    assert act in ("profile", "spawn", "info", "tips", "settings", "admin") or act.split(":", 1)[0] in ("view", "cmd", "cmdc"), "bad action " + act
''', '''    assert act in ("profile", "spawn", "info", "tips", "settings", "admin") or act.split(":", 1)[0] in ("view", "cmd", "cmdc", "bridge"), "bad action " + act
''')

# the old fixed-slot asserts follow layout D
rep('''assert used.get(("main", 39)) == "Settings" and used.get(("main", 40)) == "Mods", \\
    "the Settings torch belongs at main slot 39, immediately left of Mods (LOCKED 2026-09-25, Settings-Spec 4.1)"
assert ("main", 51) not in used, "main slot 51 is free since 0.3.3 (the torch moved to 39)"
''', '''# 0.3.16: layout D - Settings at main slot 17 (right bar, row 1; 0.3.3 - 0.3.15: slot 39 left of Mods), Mods at 35
assert used.get(("main", 17)) == "Settings" and used.get(("main", 35)) == "Mods", "0.3.16: layout D puts Settings at main 17 and Mods at 35"
assert ("main", 51) not in used, "main slot 51 is free since 0.3.3 (the torch moved to 39)"
''')
rep('''assert used.get(("main", 25)) == "Reforge" and used.get(("main", 26)) == "Identify", "Reforge at main slot 25, Identify at 26"
assert [e for e in ENTRIES if e[:3] == ("main", 26, "Ingredient_Crystal_Purple") and e[6] == "cmdc:identify"], "Identify runs /identify"
assert [e for e in ENTRIES if e[:2] == ("main", 25) and e[6] == "cmdc:reforge" and "modifiers" in e[4][0] and "tool" not in e[4][0]], \\
''', '''assert used.get(("main", 30)) == "Reforge" and used.get(("main", 31)) == "Identify", "0.3.16: Reforge at main slot 30, Identify at 31 (layout D)"
assert [e for e in ENTRIES if e[:3] == ("main", 31, "Skyy_Menu_Icon_Identify") and e[6] == "cmdc:identify"], "Identify runs /identify"
assert [e for e in ENTRIES if e[:2] == ("main", 30) and e[6] == "cmdc:reforge" and "modifiers" in e[4][0] and "tool" not in e[4][0]], \\
''')
rep('''assert used.get(("main", 41)) == "Server Setup", "the Server Setup book belongs at main slot 41, right of Mods (spec 2.2)"
''', '''assert used.get(("main", 44)) == "Server Setup", "0.3.16: Server Setup at main slot 44, under Mods on the right bar (layout D)"
''')
rep('''assert [e[2] for e in ENTRIES if e[0] == "main" and e[1] == 12] == [ICON_BAG], "0.3.11: the Accessory Bag tile uses our icon item"
# 0.3.14: the Pets tile right of Your Profile in the top row, /pets; every pet icon item shipped
assert [(e[3], e[6]) for e in ENTRIES if e[0] == "main" and e[1] in (4, 5)] == [("Your Profile", "profile"), ("Pets", "cmdc:pets")], "0.3.14: Pets at main 5"
assert all(("Skyy_Menu_Icon_Pet_" + _p) in ICON_ITEMS for _p in PET_ART) and len(ICON_ITEMS) == 1 + len(PET_ART), "0.3.14: the pet icon items"
''', '''assert [e[2] for e in ENTRIES if e[0] == "main" and e[1] == 5] == [ICON_BAG], "0.3.11: the Accessory Bag tile uses our icon item (0.3.16: slot 5)"
# 0.3.14: the Pets tile, /pets (0.3.16: slot 3, Your Profile 33); every pet icon item shipped
assert [(e[3], e[6]) for e in ENTRIES if e[0] == "main" and e[1] in (3, 33)] == [("Your Profile", "profile"), ("Pets", "cmdc:pets")], "0.3.16: Pets at main 3, Profile 33"
assert all(("Skyy_Menu_Icon_Pet_" + _p) in ICON_ITEMS for _p in PET_ART) and len(ICON_ITEMS) == 1 + len(PET_ART) + len(MENU_ICONS) - 1, \\
    "0.3.14: the pet icon items (0.3.16: + 22 tile icon items)"
# 0.3.16: every approved tile icon ships: the item JSON + the PNG at its art path, = art/menu-icons byte for byte; the bag = 0.3.11's file
import hashlib as _hl
_mman = json.load(open(os.path.join(HERE, "..", *(MENU_ICON_DIR + "/manifest.json").split("/")), encoding="utf8"))
assert sorted(t["name"] for t in _mman["tiles"]) == sorted(n for n, _t in MENU_ICONS) and \\
    all(t["item_id"] == "Skyy_Menu_Icon_" + t["name"] and dict(MENU_ICONS)[t["name"]] == t["tile"] for t in _mman["tiles"]), "0.3.16: the 23 approved icons"
for _nm, _tile in MENU_ICONS:
    _iid = "Skyy_Menu_Icon_" + _nm
    _png = files["Common/" + ICON_ITEMS[_iid][1]]
    _art = open(os.path.join(HERE, "..", *(MENU_ICON_DIR + "/Common/Icons/ItemsGenerated/%s.png" % _iid).split("/")), "rb").read()
    _me = [f for f in _mman["files"] if f["path"] == "Common/Icons/ItemsGenerated/%s.png" % _iid]
    assert len(_me) == 1 and _png == _art and _hl.sha256(_png).hexdigest() == _me[0]["sha256"] and len(_png) == _me[0]["bytes"], \\
        "0.3.16: %s's picture = art/menu-icons byte for byte (manifest sha256 + bytes)" % _iid
    _js = json.loads(files["Server/Item/Items/Utility/%s.json" % _iid])
    assert _js["Icon"] == ICON_ITEMS[_iid][1] and _js["Variant"] is True and "Categories" not in _js and "Recipe" not in _js
    assert "Server/Item/Items/Utility/%s.json" % _iid not in ASSETS.namelist() and "Common/" + ICON_ITEMS[_iid][1] not in COMMON, "0.3.16: no vanilla clash"
print("0.3.16 tile icons:", len(MENU_ICONS), "approved icons (22 new icon items + the 0.3.11 bag); layout D:", ", ".join(
    "%s %d" % (t, MAIN_D[t][0] * 9 + MAIN_D[t][1]) for t in sorted(MAIN_D, key=lambda t_: MAIN_D[t_][0] * 9 + MAIN_D[t_][1])))
print("0.3.16 tile rules:", "; ".join("%s %s" % (t, TILE_RULES[t]) for t in sorted(TILE_RULES)))
''')

# ================================================================================================ MenuData: the rule arrays
rep('''F(dat, "public static final String[] E_ACT = %s;" % jarr(E_ACT))
''', '''F(dat, "public static final String[] E_ACT = %s;" % jarr(E_ACT))
# 0.3.16: per-tile visibility rules ("" = no rule) + the keys an unlock Function already failed for (one warning each)
F(dat, "public static final String[] E_PERM = %s;" % jarr(E_PERM))
F(dat, "public static final String[] E_OPEN = %s;" % jarr(E_OPEN))
F(dat, "public static final String[] E_NEED = %s;" % jarr(E_NEED))
F(dat, "public static final String[] E_UNLOCK = %s;" % jarr(E_UNLOCK))
F(dat, "public static final java.util.concurrent.ConcurrentHashMap TILE_WARNED = new java.util.concurrent.ConcurrentHashMap();")
''')

# ================================================================================================ MenuPage: tileVisible + fillStatic
rep('''M(page, r"""
public void fillStatic(java.util.ArrayList slots) {
  java.util.UUID me = this.playerRef.getUuid();
  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);
  for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {
    if (!@PKG@.MenuData.E_VIEW[i].equals(this.view)) continue;
    String act = @PKG@.MenuData.E_ACT[i];
    if ("admin".equals(act) && !admin) continue;
    if ("view:mods".equals(act) && !admin && !@PKG@.MenuCfg.MODS_HELP) continue;
''', '''# 0.3.16: THE PER-TILE VISIBILITY RULE (TILE_RULES -> MenuData E_PERM / E_OPEN / E_NEED / E_UNLOCK). perm: the node (ADMIN_NODE = the
# admin check fillStatic already made; another node = PlayerRef.hasPermission, fail closed), unless the named Server Setup switch opens
# the tile to everyone; need: the bridge key holds a Function; unlock: while the key holds a Function, apply(UUID) must answer TRUE (an
# absent key = shown; a throw = hidden + one warning per key). Runs on the world thread while the menu is drawn.
M(page, r"""
public boolean tileVisible(int i, boolean admin) {
  String perm = @PKG@.MenuData.E_PERM[i];
  if (perm.length() > 0) {
    boolean ok = false;
    if (perm.equals(@PKG@.MenuData.ADMIN_NODE)) ok = admin;
    else {
      try { ok = this.playerRef.hasPermission(perm); } catch (Throwable t) { ok = false; }
    }
    String open = @PKG@.MenuData.E_OPEN[i];
    if (!ok && "modsHelp".equals(open) && @PKG@.MenuCfg.MODS_HELP) ok = true;
    if (!ok) return false;
  }
  java.util.Map br = @PKG@.MenuUtil.bridge();
  String need = @PKG@.MenuData.E_NEED[i];
  if (need.length() > 0 && !(br.get(need) instanceof java.util.function.Function)) return false;
  String un = @PKG@.MenuData.E_UNLOCK[i];
  if (un.length() == 0) return true;
  Object f = br.get(un);
  if (!(f instanceof java.util.function.Function)) return true;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(this.playerRef.getUuid()); }
  catch (Throwable t) {
    r = null;
    if (@PKG@.MenuData.TILE_WARNED.putIfAbsent(un, un) == null) @PKG@.MenuUtil.warn("the menu tile unlock check " + un + " failed (the tile stays hidden): " + t);
  }
  return Boolean.TRUE.equals(r);
}""")
M(page, r"""
public void fillStatic(java.util.ArrayList slots) {
  java.util.UUID me = this.playerRef.getUuid();
  boolean admin = @PKG@.MenuUtil.isAdmin(this.playerRef);
  for (int i = 0; i < @PKG@.MenuData.E_VIEW.length; i++) {
    if (!@PKG@.MenuData.E_VIEW[i].equals(this.view)) continue;
    String act = @PKG@.MenuData.E_ACT[i];
    if (!tileVisible(i, admin)) continue;
''')

# ================================================================================================ MenuPage: the bridge tile click
rep('''M(page, r"""
public void click(@REF@ ref, @ST@ st, int idx, String act) {''', '''# 0.3.16: a bridge tile (the Wardrobe) hands the player to another mod's page through its bridge Function, straight from the menu
# (never closing first; the grid is emptied once before the hand-off like openSettings / openStats). Contract: apply(UUID player) on the
# player's world thread opens that mod's page and answers Boolean.TRUE; anything else = the menu stays and says so - but ONLY while the
# menu is still the player's page: a callee that opened its page and then threw / answered non-TRUE owns the screen, so the menu sends
# nothing more (a page update to a page the client no longer shows = the stuck page acknowledgement watchTick heals).
M(page, r"""
public void openBridge(@REF@ ref, @ST@ st, String key) {
  Object f = @PKG@.MenuUtil.bridge().get(key);
  if (!(f instanceof java.util.function.Function)) { this.status = "That page is not on this server right now."; rebuild(); return; }
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  @PGM@ pm = p.getPageManager();
  if (pm == null) return;
  clearGrid();
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(this.playerRef.getUuid()); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("the menu tile " + key + " failed: " + t); r = null; }
  if (Boolean.TRUE.equals(r)) return;
  if (pm.getCustomPage() != this) { @PKG@.MenuUtil.warn("the menu tile " + key + " opened another page but answered " + String.valueOf(r) + " - left that page alone"); return; }
  this.status = "That page could not be opened right now.";
  rebuild();
}""")
M(page, r"""
public void click(@REF@ ref, @ST@ st, int idx, String act) {''')
rep('''  if (act.equals("profile")) { openStats(ref, st); return; }
  if (act.startsWith("modcfg:")) {''', '''  if (act.equals("profile")) { openStats(ref, st); return; }
  if (act.startsWith("bridge:")) { openBridge(ref, st, act.substring(7)); return; }
  if (act.startsWith("modcfg:")) {''')

# ================================================================================================ the admin-command warning names the tile
# (0.3.16: Server Setup is no longer a book - it wears its own icon at main slot 44)
rep('''- admins can use the SkyWynn Menu book");''',
    '''- admins can use the Server Setup tile in the SkyWynn Menu");''')

# ================================================================================================ the hint names the new icon
rep('''"Tooltips off - the book at the top right turns them on. Click an item to use it."''',
    '''"Tooltips off - the speech bubble at the top right turns them on. Click an item to use it."''')

# ================================================================================================ ROUND_PINS + the patch name
rep('''# 0.3.15: EMPTY - art only (the menu item's own emblem), deploys on its own.
ROUND_PINS = {}
''', '''# 0.3.15: EMPTY - art only (the menu item's own emblem), deploys on its own.
# 0.3.16: EMPTY - layout D + icons + tile rules, no other mod needed (the Wardrobe tile waits for SkyyWardrobe's wardrobe:fn:open).
ROUND_PINS = {}
''')
rep('_PATCH = "tools/menu_0_3_15_patch.py"', '_PATCH = "tools/menu_0_3_16_patch.py"')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.15 outside the recorded changes"
assert s.index("MENU_ICONS = [") < s.index("ENTRIES = [") < s.index("ADMIN_NODE = ") < s.index("TILE_RULES = {") < s.index("E_PERM = [") \
    < s.index('F(dat, "public static final String[] E_PERM') < s.index("public boolean tileVisible(") < s.index("public void fillStatic(") \
    < s.index("public void openBridge(") < s.index("public void click(@REF@"), "definitions before use"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.15 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
