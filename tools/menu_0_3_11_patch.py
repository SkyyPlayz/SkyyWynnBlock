"""Derive SkyyMenu/build_skyymenu_0.3.11.py from the LIVE SkyyMenu 0.3.10 (python tools/menu_0_3_11_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_10_patch.py -> 0.3.10 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch, never re-build it) -> this patch -> 0.3.11. 0.3.10's files stay untouched.

0.3.11 = THE ACCESSORY BAG TILE SHOWS OUR OWN ICON (art only; deploys with SkyyAccessories 0.5.9, which puts the same picture on the
Workbench "Accessories & Bags" tab - but neither needs the other). Skyy's own words (2026-10-08): "Use Option B gem colors", "Make it a
little brighter with a more leather look (still black leather, just lighter", "Yes, the bag icon looks good, commit it" - the art agent's
icon art/accessory-bag-icon/Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png (original art, committed; ART-RESUME.md Done 2).
  1. A menu tile's icon is an ITEM id (MenuPage.put: new ItemGridSlot(new ItemStack(icon, 1))), so the jar ships one icon-only item,
     Skyy_Menu_Icon_AccessoryBag: Icon = Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png (the art file, byte for byte, shipped at that
     path in this jar), the vanilla Utility_Bag_Seed's held look (Model / Texture / animations / sounds - a path reference, no file copied),
     hidden from the creative library (Variant true, no Categories - the SkyyAccessories 0.5.1 rule), no recipe, no interaction, a name
     ("Accessory Bag") in server.lang.
  2. The main menu's Accessory Bag tile (slot 12) uses it (was the vanilla Utility_Bag_Seed). The Mods list's SkyyAccessories entry keeps
     Utility_Bag_Seed (the task named the tile only).
  3. Build checks: the PNG = the art folder's manifest sha256 + bytes, a 64 x 64 RGBA PNG, never a vanilla Common/ path; the icon item id
     is no vanilla id; need_item / need_icon accept exactly the ICON_ITEMS ids (every other icon is still checked against Assets.zip).
  4. Java: no code change (MenuData's static data initialiser = the icon id string; the version strings). ROUND_PINS = {} (the Mods list
     version catch-up stays a later round).
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.10 outside them, byte for byte.
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.10.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.11.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.10"' in s and "0.3.10: THE STATS PAGE" in s and "ICON_ITEMS" not in s, "not the generated 0.3.10 script"
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
if _set is not None and _set.get("SkyyMenu") != "0.3.10":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.10" % _set.get("SkyyMenu"))

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.10: THE STATS PAGE''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.11: THE ACCESSORY BAG TILE SHOWS OUR OWN ICON (art only; notes: tools/menu_0_3_11_patch.py; Skyy 2026-10-08 "Yes, the bag icon looks
       good, commit it"): the jar ships the icon-only item Skyy_Menu_Icon_AccessoryBag (hidden from the creative library) whose Icon is
       art/accessory-bag-icon/.../SkyyAccessories_Bag_Menu.png (shipped at Common/Icons/ItemsGenerated/), and the main menu's Accessory Bag
       tile uses it (was the vanilla Utility_Bag_Seed). No code change; ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.11.py (every 0.3.10 check carried forward + K5 0.3.10 -> 0.3.11 + IC the icon item + V the
  engine's asset validators on the jar).
0.3.10: THE STATS PAGE''')
rep('VERSION = "0.3.10"\n', 'VERSION = "0.3.11"\n')

# ================================================================================================ the icon item table
rep('''PAGE_ID = "SkyyMenu"                          # OpenCustomUI page id used by the item
''', '''PAGE_ID = "SkyyMenu"                          # OpenCustomUI page id used by the item
# 0.3.11: OWN ICON ITEMS. A tile's icon is an ITEM id (MenuPage.put: new ItemGridSlot(new ItemStack(icon, 1))), so our own icon art rides
# on an icon-only item this jar ships: id -> (the art file in the repo, its path under Common/ in the jar = the item's Icon, the
# art folder's manifest.json, the item's name, the vanilla item whose held look it borrows). Hidden from the creative library (Variant
# true, no Categories), no recipe, no interaction.
ICON_ITEMS = {
    "Skyy_Menu_Icon_AccessoryBag": ("art/accessory-bag-icon/Common/Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png",
                                    "Icons/ItemsGenerated/SkyyAccessories_Bag_Menu.png", "art/accessory-bag-icon/manifest.json",
                                    "Accessory Bag", "Utility_Bag_Seed"),
}
ICON_BAG = "Skyy_Menu_Icon_AccessoryBag"      # 0.3.11: the Accessory Bag tile (Skyy 2026-10-08: "Yes, the bag icon looks good, commit it")


def icon_item_png(iid):
    """0.3.11: the icon item's PNG, checked: = its art manifest (sha256 + bytes), a 64 x 64 RGBA8 PNG"""
    import hashlib, struct
    art, rel, man, _nm, _look = ICON_ITEMS[iid]
    data = open(os.path.join(HERE, "..", *art.split("/")), "rb").read()
    ent = [f for f in json.load(open(os.path.join(HERE, "..", *man.split("/")), encoding="utf8"))["files"] if f["path"] == "Common/" + rel]
    assert len(ent) == 1 and hashlib.sha256(data).hexdigest() == ent[0]["sha256"] and len(data) == ent[0]["bytes"], \\
        "icon item %s: %s is not the art manifest's file" % (iid, art)
    assert data[:8] == b"\\x89PNG\\r\\n\\x1a\\n" and data[12:16] == b"IHDR" and struct.unpack(">II", data[16:24]) == (64, 64) \\
        and data[24:26] == b"\\x08\\x06", "icon item %s: not a 64 x 64 RGBA8 PNG" % iid
    return data
''')

# ================================================================================================ the tile
rep('''    ("main", 12, "Utility_Bag_Seed", "Accessory Bag",
''', '''    ("main", 12, ICON_BAG, "Accessory Bag",                  # 0.3.11: our own icon (was the vanilla Utility_Bag_Seed)
''')

# ================================================================================================ the build checks know the icon items
rep('''def need_item(iid):
    assert iid in ITEMS, "unknown vanilla item id: %s (not in Assets.zip)" % iid
''', '''def need_item(iid):
    if iid in ICON_ITEMS:              # 0.3.11: our icon-only items (shipped by this jar, checked below)
        return
    assert iid in ITEMS, "unknown vanilla item id: %s (not in Assets.zip)" % iid
for _iid, (_art, _rel, _man, _nm, _lk) in ICON_ITEMS.items():
    assert _iid not in ITEMS and _iid.startswith("Skyy_Menu_Icon_"), "0.3.11: icon item id %s must be ours, never a vanilla id" % _iid
    assert "Common/" + _rel not in COMMON, "0.3.11: icon item %s would override the vanilla file %s" % (_iid, _rel)
    assert _lk in ITEMS, "0.3.11: icon item %s borrows the look of an unknown item %s" % (_iid, _lk)
    icon_item_png(_iid)
''')
rep('''def need_icon(iid):
    cur, hops, icon = iid, 0, None
''', '''def need_icon(iid):
    if iid in ICON_ITEMS:              # 0.3.11: the picture ships in this jar (icon_item_png checked it)
        return
    cur, hops, icon = iid, 0, None
''')

# ================================================================================================ assets: the icon items + their names
rep('''print("menu item:", MENU_ITEM_ID, "looks like", MENU_ITEM_LOOK, "icon", look["Icon"])
''', '''print("menu item:", MENU_ITEM_ID, "looks like", MENU_ITEM_LOOK, "icon", look["Icon"])
# 0.3.11: the icon-only items (hidden from the creative library) + their pictures + names
ICON_KEYS = ("Model", "Texture", "Scale", "PlayerAnimationsId", "ItemSoundSetId")   # the held look only (the Icon is ours)
for _iid in sorted(ICON_ITEMS):
    _art, _rel, _man, _nm, _lk = ICON_ITEMS[_iid]
    _lkd = look_of(_lk)
    _node = {"TranslationProperties": {"Name": "server.items.%s.name" % _iid}, "Icon": _rel, "Variant": True, "MaxStack": 1}
    for _k in ICON_KEYS:
        if _k in _lkd:
            _node[_k] = _lkd[_k]
    assert "Model" in _node and "Texture" in _node and "Categories" not in _node and "Recipe" not in _node and "Interactions" not in _node
    _p = "Server/Item/Items/Utility/%s.json" % _iid
    assert _p not in files and "Common/" + _rel not in files
    files[_p] = json.dumps(_node, indent=2)
    files["Common/" + _rel] = icon_item_png(_iid)
    lang.extend(["items.%s.name=%s" % (_iid, _nm), "server.items.%s.name=%s" % (_iid, _nm)])
    print("icon item:", _iid, "icon", _rel, "(%d bytes, %s)" % (len(files["Common/" + _rel]), _art), "held look of", _lk, "- hidden from the creative library")
files["Server/Languages/en-US/server.lang"] = "\\n".join(lang) + "\\n"
assert [e[2] for e in ENTRIES if e[0] == "main" and e[1] == 12] == [ICON_BAG], "0.3.11: the Accessory Bag tile uses our icon item"
''')

# ================================================================================================ ROUND_PINS note
rep('''# 0.3.10: EMPTY - deploys on its own (the Stats page reads only what the live mods already publish). 0.3.9's round (SkyyClasses
# 0.1.14, SkyySkills 0.4.21, SkyyProfiles 0.1.6) is pinned in SET now.
''', '''# 0.3.10: EMPTY - deploys on its own (the Stats page reads only what the live mods already publish). 0.3.9's round (SkyyClasses
# 0.1.14, SkyySkills 0.4.21, SkyyProfiles 0.1.6) is pinned in SET now.
# 0.3.11: EMPTY - ships with SkyyAccessories 0.5.9 (same icon on the Workbench tab) but needs nothing from it; the Mods list version
# catch-up (SkyyAccessories 0.5.5 there) stays a later round.
''')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.10 outside the recorded changes"
assert s.index("def icon_item_png") < s.index("ENTRIES = [") if "ENTRIES = [" in s else True
assert s.index("COMMON = set(") < s.index("for _iid, (_art, _rel, _man, _nm, _lk) in ICON_ITEMS.items():")
compile(s, dst, "exec")
out = s.replace(LF, NL) if NL != LF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.10 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
