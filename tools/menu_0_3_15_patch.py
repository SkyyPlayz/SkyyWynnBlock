"""Derive SkyyMenu/build_skyymenu_0.3.15.py from the LIVE SkyyMenu 0.3.14 (python tools/menu_0_3_15_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_14_patch.py -> 0.3.14 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch, never re-build it) -> this patch -> 0.3.15. 0.3.14's files stay untouched. The harness
SkyyMenu/test_skyymenu_0.3.15.py is its own file (it runs test_skyymenu_0.3.14.py's checks on the new jar next to a control run = every
old check carried forward, plus the new sections).

0.3.15 = THE MENU ITEM WEARS THE NEW SKYWYNN EMBLEM (art only). Skyy's own words (2026-10-09 / 10): "lets make a new icon for the menu",
"perfect! use it" - the art agent's emblem art/menu-emblem/ (original art, committed; a floating sky island + a gold compass star; read
art/menu-emblem/README.md + manifest.json; check: python tools/art/validate_menu_emblem.py).
  1. The menu item Skyy_Menu stops borrowing the vanilla Voidheart look (MENU_ITEM_LOOK = "Ingredient_Voidheart" + look_of(...) are
     gone) and gets FIXED fields (MENU_ITEM_FIELDS = the README's / manifest's "suggested_item_fields"): Icon Icons/ItemsGenerated/
     Skyy_Menu.png, Model Items/SkyyMenu/Skyy_Menu.blockymodel, Texture Items/SkyyMenu/Skyy_Menu_Texture.png, Scale 1.2,
     PlayerAnimationsId Item, IconProperties {Scale 0.9, Rotation [0,0,0], Translation [0,-13]}, Light {Color #432, Radius 1}.
     Build check: every one of those keys is a key of the vanilla Ingredient_Voidheart item JSON (Assets.zip, read only), and Scale /
     PlayerAnimationsId / IconProperties / Light.Radius = the Voidheart's values (same hand pose, size, icon framing, glow radius - only
     the glow colour changes, violet #103 -> faint warm gold #432); the key SET of the item = 0.3.14's (no key added or lost).
  2. The jar ships the three files at Common/Items/SkyyMenu/Skyy_Menu.blockymodel, Common/Items/SkyyMenu/Skyy_Menu_Texture.png and
     Common/Icons/ItemsGenerated/Skyy_Menu.png, read from art/menu-emblem/Common/... and checked at build against
     art/menu-emblem/manifest.json (sha256 + bytes, the icon_item_png way), the PNGs' sizes (icon 64 x 64, texture 128 x 64, RGBA8),
     the model = JSON with nodes; none of the paths exists in vanilla Common/ (never overrides a vanilla file).
  3. The Mods list's SkyyMenu row icon Ingredient_Voidheart -> Skyy_Menu (our own item, shipped by this jar: need_item / need_icon
     accept it like the ICON_ITEMS). MENU_ITEM_LOOK leaves the need_item loop.
  4. Players' existing Skyy_Menu stacks just change look: the item id, its JSON path, its name / description / quality / tags /
     interactions / MaxStack are 0.3.14's; no saved data, no Java behaviour change (MenuData's static data initialiser = the Mods row icon
     string; the version strings). ROUND_PINS = {} (deploys on its own).
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.14 outside them, byte for byte.
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.14.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.15.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
OLD = s
assert 'VERSION = "0.3.14"' in s and "0.3.14: THE PETS TILE IN THE TOP BAR" in s and "MENU_ITEM_FIELDS" not in s, "not the generated 0.3.14 script"
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
if _set is not None and _set.get("SkyyMenu") != "0.3.14":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.14" % _set.get("SkyyMenu"))

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.14: THE PETS TILE''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.15: THE MENU ITEM WEARS THE NEW SKYWYNN EMBLEM (art only; notes: tools/menu_0_3_15_patch.py; Skyy "lets make a new icon for the menu",
       "perfect! use it"): Skyy_Menu's look = our own art/menu-emblem/ (a floating sky island + a gold compass star): fixed item fields
       MENU_ITEM_FIELDS (Model / Texture / Icon shipped in this jar, checked against the art manifest; Scale / animations / icon framing
       / glow radius = the vanilla Voidheart's, glow colour warm gold) instead of the borrowed Voidheart look; the Mods list's SkyyMenu
       row shows it. Same item id - players' menu items just change look. No code change, no saved data; ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.15.py (every 0.3.14 check carried forward + CC 0.3.14 -> 0.3.15 + JT the emblem assets + MR the
  Mods row executed + V the engine's asset validators on the jar).
0.3.14: THE PETS TILE''')
rep('VERSION = "0.3.14"\n', 'VERSION = "0.3.15"\n')
rep(''' - Item Skyy_Menu ("SkyWynn Menu", Ingredient_Voidheart look, glows): right-click -> OpenCustomUI page "SkyyMenu"
''', ''' - Item Skyy_Menu ("SkyWynn Menu", our own SkyWynn emblem look since 0.3.15 - was the Voidheart's -, glows): right-click -> OpenCustomUI page "SkyyMenu"
''')

# ================================================================================================ the menu item's own look
rep('''MENU_ITEM_LOOK = "Ingredient_Voidheart"      # vanilla item whose model / texture / icon / glow the menu item copies (not a backpack)
''', '''# 0.3.15: THE MENU ITEM'S OWN LOOK (Skyy "lets make a new icon for the menu", "perfect! use it"): the SkyWynn emblem art/menu-emblem/
# (README + manifest.json; check python tools/art/validate_menu_emblem.py). Fixed fields = the manifest's "suggested_item_fields"; Scale /
# PlayerAnimationsId / IconProperties / Light.Radius = the vanilla Ingredient_Voidheart's (the look 0.3.14 borrowed: same hand pose, size,
# icon framing, glow radius), the glow colour a faint warm gold. Every key is checked against the Voidheart's JSON at build.
MENU_ITEM_FIELDS = {
    "Icon": "Icons/ItemsGenerated/Skyy_Menu.png",
    "Model": "Items/SkyyMenu/Skyy_Menu.blockymodel",
    "Texture": "Items/SkyyMenu/Skyy_Menu_Texture.png",
    "Scale": 1.2,
    "PlayerAnimationsId": "Item",
    "IconProperties": {"Scale": 0.9, "Rotation": [0, 0, 0], "Translation": [0, -13]},
    "Light": {"Color": "#432", "Radius": 1},
}
MENU_ITEM_KEYS_FROM = "Ingredient_Voidheart"   # 0.3.15: the vanilla item the fields' keys (and the pose values) are checked against - never copied
MENU_ART_DIR = "art/menu-emblem"               # 0.3.15: the art folder (its manifest.json lists every file with bytes + sha256)
MENU_ART_FILES = ("Model", "Texture", "Icon")   # 0.3.15: the item fields whose file ships in this jar at Common/<field value>
MENU_ART_PNG = {"Texture": (128, 64), "Icon": (64, 64)}   # 0.3.15: the PNG sizes (RGBA8)


def menu_art_file(field):
    """0.3.15: the menu item's own art file for a field (Model / Texture / Icon), checked: = art/menu-emblem/manifest.json (sha256 +
    bytes, the icon_item_png way); a PNG = its size, RGBA8; the model = JSON with nodes"""
    import hashlib
    rel = "Common/" + MENU_ITEM_FIELDS[field]
    data = open(os.path.join(HERE, "..", *(MENU_ART_DIR + "/" + rel).split("/")), "rb").read()
    ent = [f for f in json.load(open(os.path.join(HERE, "..", *(MENU_ART_DIR + "/manifest.json").split("/")), encoding="utf8"))["files"]
           if f["path"] == rel]
    assert len(ent) == 1 and hashlib.sha256(data).hexdigest() == ent[0]["sha256"] and len(data) == ent[0]["bytes"], \\
        "menu item %s: %s/%s is not the art manifest's file" % (field, MENU_ART_DIR, rel)
    if field in MENU_ART_PNG:
        assert data[:8] == b"\\x89PNG\\r\\n\\x1a\\n" and data[12:16] == b"IHDR" and struct.unpack(">II", data[16:24]) == MENU_ART_PNG[field] \\
            and data[24:26] == b"\\x08\\x06", "menu item %s: not a %d x %d RGBA8 PNG" % ((field,) + MENU_ART_PNG[field])
    else:
        _m = json.loads(data.decode("utf8"))
        assert isinstance(_m, dict) and isinstance(_m.get("nodes"), list) and _m["nodes"], "menu item %s: not a blockymodel" % field
    return data
''')

# ================================================================================================ the Mods row icon
rep('''    {"mod": "SkyyMenu", "version": VERSION, "icon": "Ingredient_Voidheart", "check": "skymenu",
''', '''    {"mod": "SkyyMenu", "version": VERSION, "icon": MENU_ITEM_ID, "check": "skymenu",     # 0.3.15: our own emblem (was Ingredient_Voidheart)
''')

# ================================================================================================ the build checks know the menu item
rep('''def need_item(iid):
    if iid in ICON_ITEMS:              # 0.3.11: our icon-only items (shipped by this jar, checked below)
        return
''', '''def need_item(iid):
    if iid in ICON_ITEMS or iid == MENU_ITEM_ID:   # 0.3.11: our icon-only items; 0.3.15: the menu item (shipped by this jar, checked below)
        return
''')
rep('''    icon_item_png(_iid)

VISUAL_KEYS = ''', '''    icon_item_png(_iid)
# 0.3.15: the menu item's own look - an id of ours, its files ours (the art manifest), never a vanilla path; its keys = vanilla item keys
assert MENU_ITEM_ID not in ITEMS and MENU_ITEM_ID not in ICON_ITEMS, "0.3.15: the menu item id %s must be ours" % MENU_ITEM_ID
for _f in MENU_ART_FILES:
    assert "Common/" + MENU_ITEM_FIELDS[_f] not in COMMON, "0.3.15: the menu item's %s would override the vanilla file %s" % (_f, MENU_ITEM_FIELDS[_f])
    assert MENU_ITEM_FIELDS[_f].split("/")[-1].startswith("Skyy_Menu"), "0.3.15: the menu item's %s file is named after it" % _f
    menu_art_file(_f)
_vh = json.loads(ASSETS.read(ITEMS[MENU_ITEM_KEYS_FROM]).decode("utf-8-sig"))
assert "Parent" not in _vh and set(MENU_ITEM_FIELDS) <= set(_vh), "0.3.15: every menu item field is a key of the vanilla %s: %s" % (
    MENU_ITEM_KEYS_FROM, sorted(set(MENU_ITEM_FIELDS) - set(_vh)))
for _k in ("Scale", "PlayerAnimationsId", "IconProperties"):
    assert MENU_ITEM_FIELDS[_k] == _vh[_k], "0.3.15: the menu item's %s = the Voidheart's (same pose / size / icon framing): %r" % (_k, _vh[_k])
assert set(MENU_ITEM_FIELDS["Light"]) == set(_vh["Light"]) and MENU_ITEM_FIELDS["Light"]["Radius"] == _vh["Light"]["Radius"], \\
    "0.3.15: the menu item's Light = the Voidheart's keys + radius (only the colour is ours)"
assert re.match(r"^#[0-9a-fA-F]{3}$", MENU_ITEM_FIELDS["Light"]["Color"]) and re.match(r"^#[0-9a-fA-F]{3}$", _vh["Light"]["Color"]), \\
    "0.3.15: the glow colour is written like the Voidheart's (#rgb)"

VISUAL_KEYS = ''')
rep('''for ic in (ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_PLAYER, MENU_ITEM_LOOK) + ((FILLER_ICON,) if FILLER_ICON else ()):
''', '''for ic in (ICON_BACK, ICON_PREV, ICON_NEXT, ICON_CLOSE, ICON_WARP, ICON_PLAYER) + ((FILLER_ICON,) if FILLER_ICON else ()):   # 0.3.15: the menu item look is ours (no vanilla look id here)
''')
rep('''def need_icon(iid):
    if iid in ICON_ITEMS:              # 0.3.11: the picture ships in this jar (icon_item_png checked it)
        return
''', '''def need_icon(iid):
    if iid in ICON_ITEMS or iid == MENU_ITEM_ID:   # 0.3.11: the picture ships in this jar (icon_item_png / 0.3.15 menu_art_file checked it)
        return
''')

# ================================================================================================ assets: the menu item
rep('''look = look_of(MENU_ITEM_LOOK)
item = {''', '''item = {''')
rep('''    "Icon": look["Icon"],
    "Quality": MENU_ITEM_QUALITY,''', '''    "Icon": MENU_ITEM_FIELDS["Icon"],                # 0.3.15: our own emblem (was the Voidheart's)
    "Quality": MENU_ITEM_QUALITY,''')
rep('''for k in VISUAL_KEYS:
    if k in look:
        item[k] = look[k]
lang = [''', '''for k in VISUAL_KEYS:                                # 0.3.15: the fixed fields, in 0.3.14's key order (no key added or lost)
    if k in MENU_ITEM_FIELDS:
        item[k] = MENU_ITEM_FIELDS[k]
assert set(item) == set(["TranslationProperties", "Categories", "Quality", "Tags", "MaxStack", "Interactions"]) | set(MENU_ITEM_FIELDS) \\
    and set(MENU_ITEM_FIELDS) == set(VISUAL_KEYS + ("Icon",)) - set(["ItemSoundSetId"]), "0.3.15: the menu item = 0.3.14's keys"
lang = [''')
rep('''print("menu item:", MENU_ITEM_ID, "looks like", MENU_ITEM_LOOK, "icon", look["Icon"])
''', '''# 0.3.15: the emblem's three files (the art manifest's bytes), at their Common/ path
for _f in MENU_ART_FILES:
    assert "Common/" + MENU_ITEM_FIELDS[_f] not in files
    files["Common/" + MENU_ITEM_FIELDS[_f]] = menu_art_file(_f)
print("menu item:", MENU_ITEM_ID, "own emblem look (%s):" % MENU_ART_DIR, ", ".join("%s %s (%d bytes)" % (_f, MENU_ITEM_FIELDS[_f],
      len(files["Common/" + MENU_ITEM_FIELDS[_f]])) for _f in MENU_ART_FILES), "- glow", MENU_ITEM_FIELDS["Light"]["Color"])
''')
rep('''assert all(files["Common/Icons/ItemsGenerated/SkyyMenu_Pet_%s.png" % _p] for _p in PET_ART), "0.3.14: the pet icons are in the jar"
''', '''assert all(files["Common/Icons/ItemsGenerated/SkyyMenu_Pet_%s.png" % _p] for _p in PET_ART), "0.3.14: the pet icons are in the jar"
# 0.3.15: the menu item wears the emblem; the Mods row shows it; nothing names the Voidheart any more
assert json.loads(files["Server/Item/Items/Utility/%s.json" % MENU_ITEM_ID])["Model"] == MENU_ITEM_FIELDS["Model"], "0.3.15: the item JSON"
assert [m["icon"] for m in MODS if m["mod"] == "SkyyMenu"] == [MENU_ITEM_ID], "0.3.15: the Mods row icon"
assert "Voidheart" not in json.dumps(item) and not [m for m in MODS if "Voidheart" in m["icon"]], "0.3.15: no Voidheart look left"
''')

# ================================================================================================ ROUND_PINS + the patch name
rep('''# 0.3.14: EMPTY - deploys on its own (the Pets tile reads SkyyPets 0.2's records, already the SET pin). 0.3.13's round is pinned in SET now.
ROUND_PINS = {}
''', '''# 0.3.14: EMPTY - deploys on its own (the Pets tile reads SkyyPets 0.2's records, already the SET pin). 0.3.13's round is pinned in SET now.
# 0.3.15: EMPTY - art only (the menu item's own emblem), deploys on its own.
ROUND_PINS = {}
''')
rep('_PATCH = "tools/menu_0_3_14_patch.py"', '_PATCH = "tools/menu_0_3_15_patch.py"')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
assert "MENU_ITEM_LOOK" not in s and "look_of(MENU" not in s, "MENU_ITEM_LOOK is gone"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.14 outside the recorded changes"
assert s.index("MENU_ITEM_FIELDS = {") < s.index("def menu_art_file(field):") < s.index("MODS = [") < s.index("COMMON = set(") \
    < s.index("    menu_art_file(_f)\n_vh = ") < s.index("item = {"), "definitions before use"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.14 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
