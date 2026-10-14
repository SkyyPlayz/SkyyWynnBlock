"""Derive SkyyMenu/build_skyymenu_0.3.22.py from the LIVE SkyyMenu 0.3.21 (python tools/menu_0_3_22_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_21_patch.py -> 0.3.21 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.22. The harness SkyyMenu/test_skyymenu_0.3.22.py is its own file.

0.3.22 = THE SHARDS TILE (research/Gathering-Shards-Spec.md phase 5, "SkyyMenu (hub button)"; Skyy 2026-10-11 SHARDS 2 "i want the shar menu
in the portal on your main island too"): a new main-view tile "Shards" at row 1, col 2 (slot 11, left of Island Menu - a free slot of
layout D; the reserved slots 27 / 39 / 41 stay free). Drawn ONLY while SkyyShards publishes the bridge Function shard:fn:open
(TILE_RULES "need", the Wardrobe pattern); the click calls apply(UUID player) on the world thread, which opens SkyyShards' shard menu
(menu view: Collect, upgrades, islands, totems and Enter Shard; Pick up stays at the portal). Icon = the vanilla Portal_Device (a vanilla
id, so the menu builds and draws without SkyyShards; the shard's own icon ships in SkyyShards). No saved data, no new key, no command.
ROUND_PINS = {} (deploys with SkyyShards 0.1 + SkyyIslands 0.5.8; without SkyyShards the tile is simply hidden).
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.21.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.22.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
OLD = s
assert 'VERSION = "0.3.21"' in s and "0.3.21: THE MESSAGES TAB" in s and "shard:fn:open" not in s, "not the generated 0.3.21 script"
CHANGES = []


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
if _set is not None and _set.get("SkyyMenu") != "0.3.21":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.21" % _set.get("SkyyMenu"))

rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.21: THE MESSAGES TAB''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.22: THE SHARDS TILE (notes: tools/menu_0_3_22_patch.py; Gathering-Shards-Spec phase 5 "SkyyMenu (hub button)"): main-view tile "Shards"
       at row 1, col 2 (slot 11), drawn only while SkyyShards publishes shard:fn:open (TILE_RULES "need"); the click = apply(UUID) on the
       world thread = SkyyShards' shard menu. Icon: the vanilla Portal_Device. No saved-data change. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.22.py.
0.3.21: THE MESSAGES TAB''')
rep('VERSION = "0.3.21"\n', 'VERSION = "0.3.22"\n')
rep('''    ("main", 36, "Furniture_Village_Wardrobe", "Wardrobe",
        ["Your saved loadouts - one click swaps between them.", "Command: /wardrobe"],
        "Click to open!", "bridge:wardrobe:fn:open"),
''', '''    ("main", 36, "Furniture_Village_Wardrobe", "Wardrobe",
        ["Your saved loadouts - one click swaps between them.", "Command: /wardrobe"],
        "Click to open!", "bridge:wardrobe:fn:open"),
    # 0.3.22: THE SHARDS TILE (left of Island Menu) - drawn ONLY while SkyyShards publishes shard:fn:open (TILE_RULES "need"); the click
    # calls apply(UUID player) on the world thread = the shard menu (Collect, upgrades, islands, totems, Enter Shard)
    ("main", 11, "Portal_Device", "Shards",
        ["Your shard islands: collect what your totems harvested, upgrade storage, grow islands and enter your shard.",
         "Place your shard on your island to get a portal there too."],
        "Click to open!", "bridge:shard:fn:open"),
''')
rep("MAIN_D = {'Pets': (0, 3), ", "MAIN_D = {'Shards': (1, 2), 'Pets': (0, 3), ")
rep('''    "Wardrobe": {"need": "wardrobe:fn:open"},
''', '''    "Wardrobe": {"need": "wardrobe:fn:open"},
    "Shards": {"need": "shard:fn:open"},          # 0.3.22
''')
rep('''    assert _e[2] == (MENU_ICON_OF.get(_t) if _t not in ("Pets", "Wardrobe") else _e[2]), "0.3.16: %s wears its own icon" % _t''',
    '''    assert _e[2] == (MENU_ICON_OF.get(_t) if _t not in ("Pets", "Wardrobe", "Shards") else _e[2]), "0.3.16: %s wears its own icon" % _t   # 0.3.22: Shards = Portal_Device''')
rep('''assert _main["Pets"][2] == ICON_PETS and _main["Wardrobe"][2] == "Furniture_Village_Wardrobe" and _main["Wardrobe"][6] == "bridge:wardrobe:fn:open"''',
    '''assert _main["Pets"][2] == ICON_PETS and _main["Wardrobe"][2] == "Furniture_Village_Wardrobe" and _main["Wardrobe"][6] == "bridge:wardrobe:fn:open"
assert _main["Shards"][1] == 11 and _main["Shards"][6] == "bridge:shard:fn:open" and TILE_RULES["Shards"] == {"need": "shard:fn:open"}, "0.3.22: the Shards tile"''')

assert s.count("bridge:shard:fn:open") == 2, "0.3.22: the changes"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.21 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.21 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
