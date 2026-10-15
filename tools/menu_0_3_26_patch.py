"""Derive SkyyMenu/build_skyymenu_0.3.26.py from the LIVE SkyyMenu 0.3.25 (python tools/menu_0_3_26_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_25_patch.py -> 0.3.25 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.26. The harness SkyyMenu/test_skyymenu_0.3.26.py is its own file.

0.3.26 (2026-10-15) = OUR OWN ICONS, WAVE 1 (lean round menu0326). Skyy 2026-10-15 (SkyWynn Menu Teleport page screenshot with vanilla
icons): "lets do our own icons in every menu too." (docs/answered/ui.md; plan research/Menu-Icons-Plan.md). The 14 wave-1 icons of
art/menu-icons-2/ (tools/art/make_menu_icons_2.py, our own pixels, validator ALL OK, reviewed by the local session under the 2026-10-13
visuals go-ahead) ship as hidden icon-only items Skyy_Menu_Icon_<Name> exactly like the 0.3.16 tile icons (ICON_ITEMS + icon_item_png:
bytes + sha256 against art/menu-icons-2/manifest.json; held look = the vanilla Farming_Collar, never held; no recipe, no category):
  Teleport page   My Island (tp 11, was Soil_Grass), Hub (tp 13, was Hub_Portal_Default), Spawn (tp 15, was Spawn_Portal),
                  every warp ICON_WARP (was Tool_Map), a locked warp the NEW ICON_WARP_LOCKED (dim signpost + padlock; was Tool_Map),
                  "No warps yet" the NEW ICON_NO_WARPS (was Tool_Map)
  every page      Back 45 / Prev 48 / Next 50 / Close 49 (were Weapon_Arrow_Iron / _Crude / _Iron, Furniture_Flag_Small_Red)
  Players         every player tile + "Nobody else is online" / "Player offline" / the picked player's head = ICON_PLAYER (was
                  Armor_Leather_Light_Head); Accept / Deny Teleport Request (players 47 / 51, were Ingredient_Crystal_Green / _Red)
  main view       the Shards tile (main 11, was Portal_Device; 0.3.22's exception in the "every tile wears its own icon" check removed)
  player actions  README question 3 default [yes, reuse]: Send Teleport Request 29 = Hub, Invite Them Here 30 = Spawn, Visit Their
                  Island 31 = My Island (the other player actions are wave 2)
Also: every Assets.zip read of this build (the icon checks, SUI.verify, the /soundtest list) uses the CACHED copy (tools/serverjar.py) -
never the installed game file (2026-10-13 launcher-update lock). Saved data: none. ROUND_PINS = {}. Rollback to 0.3.25: safe (icons only).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.25.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.26.py")
CR, LF = chr(13), chr(10)
raw = open(src, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.25"' in s and "0.3.25: SEARCH BARS" in s and "MENU_ICONS_2" not in s, "not the generated 0.3.25 script"
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.25: SEARCH BARS''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.26: OUR OWN ICONS, WAVE 1 (notes: tools/menu_0_3_26_patch.py; Skyy 2026-10-15 "lets do our own icons in every menu too."): the 14
       art/menu-icons-2 icons as hidden icon items Skyy_Menu_Icon_<Name> (MENU_ICONS_2): Teleport My Island / Hub / Spawn, every warp,
       a locked warp (NEW ICON_WARP_LOCKED), "No warps yet" (NEW ICON_NO_WARPS); Back / Prev / Next / Close on every page; the player
       head (ICON_PLAYER); Accept / Deny; the Shards tile; player actions 29 / 30 / 31 reuse Hub / Spawn / My Island. Assets.zip = the
       cached copy (tools/serverjar.py). No saved data. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.26.py.
0.3.25: SEARCH BARS''')
rep('VERSION = "0.3.25"\n', 'VERSION = "0.3.26"\n')

# ---------------------------------------------------------------------------------------------------------------- the cached Assets.zip
rep('''import skyyui as SUI         # 0.3.10: the shared vanilla UI kit - the Stats page only (the older menu pages keep their own look)
''', '''import skyyui as SUI         # 0.3.10: the shared vanilla UI kit - the Stats page only (the older menu pages keep their own look)
import serverjar as _SJ      # 0.3.26: the CACHED Assets.zip (tools/serverjar.py) - never the installed game file
ASSETS_ZIP = _SJ.assets_zip()   # read-only
''')
rep('''ASSETS = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))''',
    '''ASSETS = zipfile.ZipFile(ASSETS_ZIP)   # 0.3.26: the cached copy''')
rep('''SUI.verify()
SUI_KIT_ID = SUI.kit_id()''', '''SUI.verify(assets_zip=ASSETS_ZIP)   # 0.3.26: the cached copy
SUI_KIT_ID = SUI.kit_id()''')
rep('''_SNDZ = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")''',
    '''_SNDZ = ASSETS_ZIP   # 0.3.26: the cached copy''')

# ---------------------------------------------------------------------------------------------------------------- the icon items
rep('''MENU_ICON_OF = dict((_tile, "Skyy_Menu_Icon_" + _nm) for _nm, _tile in MENU_ICONS)   # 0.3.16: tile name -> its icon item
''', '''MENU_ICON_OF = dict((_tile, "Skyy_Menu_Icon_" + _nm) for _nm, _tile in MENU_ICONS)   # 0.3.16: tile name -> its icon item
# 0.3.26: OUR OWN ICONS, WAVE 1 (Skyy 2026-10-15: "lets do our own icons in every menu too."; research/Menu-Icons-Plan.md): the 14 icons of
# art/menu-icons-2 (tools/art/make_menu_icons_2.py, original pixels; README there) as icon-only items Skyy_Menu_Icon_<Name>, shipped at
# the same Common/ path, checked against art/menu-icons-2/manifest.json (sha256 + bytes); held look = Farming_Collar like the tile icons.
# (name, item name, the vanilla id it replaces - the manifest's replaces_vanilla_id, checked at the end of the build)
MENU_ICON_DIR_2 = "art/menu-icons-2"
MENU_ICONS_2 = [("MyIsland", "My Island", "Soil_Grass"), ("Hub", "Hub", "Hub_Portal_Default"), ("Spawn", "Spawn", "Spawn_Portal"),
                ("Warp", "Warp", "Tool_Map"), ("WarpLocked", "Warp (locked)", "Tool_Map"), ("NoWarps", "No warps yet", "Tool_Map"),
                ("Shards", "Shards", "Portal_Device"), ("Back", "Go Back", "Weapon_Arrow_Iron"), ("Prev", "Previous Page", "Weapon_Arrow_Crude"),
                ("Next", "Next Page", "Weapon_Arrow_Iron"), ("Close", "Close", "Furniture_Flag_Small_Red"),
                ("Player", "Player", "Armor_Leather_Light_Head"), ("Accept", "Accept Request", "Ingredient_Crystal_Green"),
                ("Deny", "Deny Request", "Ingredient_Crystal_Red")]
for _nm, _lab, _was in MENU_ICONS_2:
    assert "Skyy_Menu_Icon_" + _nm not in ICON_ITEMS, "0.3.26: %s clashes with an icon item we already ship" % _nm
    ICON_ITEMS["Skyy_Menu_Icon_" + _nm] = ("%s/Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % (MENU_ICON_DIR_2, _nm),
                                         "Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % _nm, MENU_ICON_DIR_2 + "/manifest.json", _lab,
                                         "Farming_Collar")
MENU_ICON_OF["Shards"] = "Skyy_Menu_Icon_Shards"    # 0.3.26: the Shards tile wears its own icon too (was the vanilla Portal_Device)
''')
rep('''ICON_BACK   = "Weapon_Arrow_Iron"
ICON_PREV   = "Weapon_Arrow_Crude"
ICON_NEXT   = "Weapon_Arrow_Iron"
ICON_CLOSE  = "Furniture_Flag_Small_Red"      # red flag with a white X (vanilla Barrier's icon is an empty wireframe cube)
ICON_WARP   = "Tool_Map"
ICON_PLAYER = "Armor_Leather_Light_Head"
''', '''# 0.3.26: our own art/menu-icons-2 icons (were Weapon_Arrow_Iron / Weapon_Arrow_Crude / Weapon_Arrow_Iron / Furniture_Flag_Small_Red /
# Tool_Map / Armor_Leather_Light_Head); ICON_WARP_LOCKED + ICON_NO_WARPS are new (both were ICON_WARP)
ICON_BACK   = "Skyy_Menu_Icon_Back"           # a steel return arrow
ICON_PREV   = "Skyy_Menu_Icon_Prev"           # a steel double chevron, left
ICON_NEXT   = "Skyy_Menu_Icon_Next"           # the same, right
ICON_CLOSE  = "Skyy_Menu_Icon_Close"          # a riveted steel plate with a red X
ICON_WARP   = "Skyy_Menu_Icon_Warp"           # a wooden signpost (every unlocked warp)
ICON_WARP_LOCKED = "Skyy_Menu_Icon_WarpLocked"   # 0.3.26: the dim signpost + a padlock (a warp you have not unlocked)
ICON_NO_WARPS    = "Skyy_Menu_Icon_NoWarps"      # 0.3.26: a bare signpost ("No warps yet")
ICON_PLAYER = "Skyy_Menu_Icon_Player"         # a blocky player head
''')

# ---------------------------------------------------------------------------------------------------------------- ENTRIES + player actions
rep('''    ("main", 11, "Portal_Device", "Shards",''', '''    ("main", 11, "Skyy_Menu_Icon_Shards", "Shards",    # 0.3.26: our own icon (was Portal_Device)''')
rep('''    ("tp", 11, "Soil_Grass", "My Island",''', '''    ("tp", 11, "Skyy_Menu_Icon_MyIsland", "My Island",    # 0.3.26: our own icons on the Teleport page (were Soil_Grass /''')
rep('''    ("tp", 13, "Hub_Portal_Default", "Hub",''', '''    ("tp", 13, "Skyy_Menu_Icon_Hub", "Hub",               # Hub_Portal_Default / Spawn_Portal)''')
rep('''    ("tp", 15, "Spawn_Portal", "Spawn",''', '''    ("tp", 15, "Skyy_Menu_Icon_Spawn", "Spawn",''')
rep('''    ("players", 47, "Ingredient_Crystal_Green", "Accept Teleport Request",''',
    '''    ("players", 47, "Skyy_Menu_Icon_Accept", "Accept Teleport Request",    # 0.3.26: our own (was Ingredient_Crystal_Green)''')
rep('''    ("players", 51, "Ingredient_Crystal_Red", "Deny Teleport Request",''',
    '''    ("players", 51, "Skyy_Menu_Icon_Deny", "Deny Teleport Request",        # 0.3.26: our own (was Ingredient_Crystal_Red)''')
rep('''    (29, "Hub_Portal_Default", "Send Teleport Request",''', '''    # 0.3.26: 29 / 30 / 31 reuse our Hub / Spawn / My Island icons (art/menu-icons-2 README question 3 default; the rest = wave 2)
    (29, "Skyy_Menu_Icon_Hub", "Send Teleport Request",''')
rep('''    (30, "Spawn_Portal", "Invite Them Here",''', '''    (30, "Skyy_Menu_Icon_Spawn", "Invite Them Here",''')
rep('''    (31, "Soil_Grass", "Visit Their Island",''', '''    (31, "Skyy_Menu_Icon_MyIsland", "Visit Their Island",''')

# ---------------------------------------------------------------------------------------------------------------- build-time checks
rep('''for ic in (ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_PLAYER) + ((FILLER_ICON,) if FILLER_ICON else ()):''',
    '''for ic in (ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_WARP_LOCKED, ICON_NO_WARPS, ICON_PLAYER) + ((FILLER_ICON,) if FILLER_ICON else ()):''')
rep('''                      [ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_PLAYER])):''',
    '''                      [ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_WARP_LOCKED, ICON_NO_WARPS, ICON_PLAYER])):''')
rep('''    assert _e[2] == (MENU_ICON_OF.get(_t) if _t not in ("Pets", "Wardrobe", "Shards") else _e[2]), "0.3.16: %s wears its own icon" % _t   # 0.3.22: Shards = Portal_Device''',
    '''    assert _e[2] == (MENU_ICON_OF.get(_t) if _t not in ("Pets", "Wardrobe") else _e[2]), "0.3.16: %s wears its own icon" % _t   # 0.3.26: Shards too''')
rep('''assert _main["Shards"][1] == 11 and _main["Shards"][6] == "bridge:shard:fn:open"''',
    '''assert _main["Shards"][2] == "Skyy_Menu_Icon_Shards", "0.3.26: the Shards tile wears our own icon"
assert _main["Shards"][1] == 11 and _main["Shards"][6] == "bridge:shard:fn:open"''')

# ---------------------------------------------------------------------------------------------------------------- MenuData + fillWarps
rep('''                  ("ICON_NEXT", jstr(ICON_NEXT)), ("ICON_CLOSE", jstr(ICON_CLOSE)), ("ICON_WARP", jstr(ICON_WARP)),
''', '''                  ("ICON_NEXT", jstr(ICON_NEXT)), ("ICON_CLOSE", jstr(ICON_CLOSE)), ("ICON_WARP", jstr(ICON_WARP)),
                  ("ICON_WARP_LOCKED", jstr(ICON_WARP_LOCKED)), ("ICON_NO_WARPS", jstr(ICON_NO_WARPS)),   # 0.3.26
''')
rep('''    put(slots, @PKG@.MenuData.WARP_SLOTS[i], @PKG@.MenuData.ICON_WARP, open ? id : id + " (locked)",''',
    '''    put(slots, @PKG@.MenuData.WARP_SLOTS[i], open ? @PKG@.MenuData.ICON_WARP : @PKG@.MenuData.ICON_WARP_LOCKED, open ? id : id + " (locked)",''')
rep('''    put(slots, @PKG@.MenuData.NO_WARPS_SLOT, @PKG@.MenuData.ICON_WARP, "No warps yet",''',
    '''    put(slots, @PKG@.MenuData.NO_WARPS_SLOT, @PKG@.MenuData.ICON_NO_WARPS, "No warps yet",''')

# ---------------------------------------------------------------------------------------------------------------- shipped icons
rep('''assert all(("Skyy_Menu_Icon_Pet_" + _p) in ICON_ITEMS for _p in PET_ART) and len(ICON_ITEMS) == 1 + len(PET_ART) + len(MENU_ICONS) - 1, \\
    "0.3.14: the pet icon items (0.3.16: + 22 tile icon items)"
''', '''assert all(("Skyy_Menu_Icon_Pet_" + _p) in ICON_ITEMS for _p in PET_ART) and \\
    len(ICON_ITEMS) == 1 + len(PET_ART) + len(MENU_ICONS) - 1 + len(MENU_ICONS_2), \\
    "0.3.14: the pet icon items (0.3.16: + 22 tile icon items; 0.3.26: + the 14 wave-1 icons)"
# 0.3.26: every wave-1 icon ships (item JSON + PNG = art/menu-icons-2 byte for byte, manifest sha256 + bytes), the manifest lists exactly
# MENU_ICONS_2 (same id, label and replaced vanilla id), and no menu spot of this wave still names the vanilla id it replaced
_m2 = json.load(open(os.path.join(HERE, "..", *(MENU_ICON_DIR_2 + "/manifest.json").split("/")), encoding="utf8"))
assert [(i["name"], i["id"], i["label"], i["replaces_vanilla_id"]) for i in _m2["icons"]] == \\
    [(n, "Skyy_Menu_Icon_" + n, l, w) for n, l, w in MENU_ICONS_2], "0.3.26: MENU_ICONS_2 = art/menu-icons-2/manifest.json icons"
for _nm, _lab, _was in MENU_ICONS_2:
    _iid = "Skyy_Menu_Icon_" + _nm
    _rel = ICON_ITEMS[_iid][1]
    _png = files["Common/" + _rel]
    _me = [f for f in _m2["files"] if f["path"] == "Common/" + _rel]
    assert len(_me) == 1 and hashlib.sha256(_png).hexdigest() == _me[0]["sha256"] and len(_png) == _me[0]["bytes"], "0.3.26: %s = the art file" % _iid
    _js = json.loads(files["Server/Item/Items/Utility/%s.json" % _iid])
    assert _js["Icon"] == _rel and _js["Variant"] is True and "Categories" not in _js and "Recipe" not in _js and "Interactions" not in _js
    assert _iid not in ITEMS and "Common/" + _rel not in COMMON, "0.3.26: %s clashes with a vanilla item / file" % _iid
    assert ("server.items.%s.name=%s" % (_iid, _lab)) in lang, "0.3.26: %s has its name" % _iid
_W1 = dict([(("tp", 11), "MyIsland"), (("tp", 13), "Hub"), (("tp", 15), "Spawn"), (("players", 47), "Accept"), (("players", 51), "Deny"),
            (("main", 11), "Shards")])
_W1 = dict(((_k, "Skyy_Menu_Icon_" + _v) for _k, _v in _W1.items()))
assert dict(((e[0], e[1]), e[2]) for e in ENTRIES if (e[0], e[1]) in _W1) == _W1, "0.3.26: the wave-1 ENTRIES wear our icons"
assert [a[1] for a in PLAYER_ACTIONS if a[0] in (29, 30, 31)] == ["Skyy_Menu_Icon_Hub", "Skyy_Menu_Icon_Spawn", "Skyy_Menu_Icon_MyIsland"]
_chrome = (ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_WARP_LOCKED, ICON_NO_WARPS, ICON_PLAYER)
assert all(_c in ICON_ITEMS and _c not in ITEMS for _c in _chrome) and len(set(_chrome)) == len(_chrome), "0.3.26: the chrome icons are ours"
_was = set(w for _n, _l, w in MENU_ICONS_2)
assert not [_v for _v in list(_W1.values()) + list(_chrome) + [a[1] for a in PLAYER_ACTIONS if a[0] in (29, 30, 31)] if _v in _was], "0.3.26: a vanilla id left"
print("0.3.26 wave-1 icons:", len(MENU_ICONS_2), "icon items from", MENU_ICON_DIR_2, "-", ", ".join(n for n, _l, _w in MENU_ICONS_2))
''')

# ---------------------------------------------------------------------------------------------------------------- done
assert "hashlib" in s.split("ASSETS = zipfile.ZipFile(ASSETS_ZIP)")[0], "hashlib is imported before the shipped-icons check"
_i = s.index
assert _i("MENU_ICONS_2 = [") < _i("ICON_BACK   = \"Skyy_Menu_Icon_Back\"") < _i('("main", 11, "Skyy_Menu_Icon_Shards"') < _i("ASSETS = zipfile.ZipFile(ASSETS_ZIP)")
assert "B.HYTALE" not in s and '"Assets.zip"))' not in s, "0.3.26: an installed Assets.zip path is left"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.25 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.25 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
