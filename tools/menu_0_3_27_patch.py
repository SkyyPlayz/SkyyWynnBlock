"""Derive SkyyMenu/build_skyymenu_0.3.27.py from the LIVE SkyyMenu 0.3.26 (python tools/menu_0_3_27_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_26_patch.py -> 0.3.26 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.27. The harness SkyyMenu/test_skyymenu_0.3.27.py is its own file.

0.3.27 (2026-10-15) = THE SHARDS TILE GOES (round shards04, the SkyyMenu part of research/Gathering-Shards-Spec.md phase 9 / 9.5 / 9.8 and
question 22 [remove]). Skyy 2026-10-15 (docs/answered/skills.md SHARD MENUS): "i would rather each shard has its own menu. and i was
picturing you open them by right clicking the shard on your island, not in the menu. (make it so the shard menu can only be opened on your
island. and its hidden everywhere else"
  1. The main-view tile "Shards" (slot 11, 0.3.22, our icon since 0.3.26; drawn while SkyyShards published shard:fn:open) is removed:
     its ENTRIES row, its MAIN_D slot (slot 11 is free again: MAIN_FREE), its TILE_RULES "need" rule and the 0.3.22 / 0.3.26 asserts that
     named it. SkyyShards 0.4 no longer publishes shard:fn:open (the tile would have hidden itself anyway - TILE_RULES "need").
  2. The Island Menu tile's text gains one line: "Shards: right-click one on your island to open its menu."
  3. Kept: the icon item Skyy_Menu_Icon_Shards (wave-1 art, hidden, never held - free for a later page), the Admin page's four Shards
     buttons (0.3.25: give / info / unplace / unload; /shardadmin stays an admin tool).
Saved data: none. ROUND_PINS = {}. Rollback to 0.3.26: safe (the old tile stays hidden while SkyyShards 0.4 publishes no shard:fn:open).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.26.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.27.py")
CR, LF = chr(13), chr(10)
raw = open(src, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.26"' in s and "0.3.26: OUR OWN ICONS, WAVE 1" in s and "0.3.27" not in s, "not the generated 0.3.26 script"
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.26: OUR OWN ICONS, WAVE 1''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.27: THE SHARDS TILE GOES (notes: tools/menu_0_3_27_patch.py; Skyy 2026-10-15 SHARD MENUS "make it so the shard menu can only be
       opened on your island. and its hidden everywhere else"): the main-view tile "Shards" (slot 11) is removed with its TILE_RULES
       rule (SkyyShards 0.4 opens each shard's menu only from its portal on your island and publishes no shard:fn:open); the Island
       Menu tile says "Shards: right-click one on your island to open its menu." No saved data. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.27.py.
0.3.26: OUR OWN ICONS, WAVE 1''')
rep('VERSION = "0.3.26"\n', 'VERSION = "0.3.27"\n')

# ---------------------------------------------------------------------------------------------------------------- the tile goes
rep('''    # 0.3.22: THE SHARDS TILE (left of Island Menu) - drawn ONLY while SkyyShards publishes shard:fn:open (TILE_RULES "need"); the click
    # calls apply(UUID player) on the world thread = the shard menu (Collect, upgrades, islands, totems, Enter Shard)
    ("main", 11, "Skyy_Menu_Icon_Shards", "Shards",    # 0.3.26: our own icon (was Portal_Device)
        ["Your shard islands: collect what your totems harvested, upgrade storage, grow islands and enter your shard.",
         "Place your shard on your island to get a portal there too."],
        "Click to open!", "bridge:shard:fn:open"),
''', '''    # 0.3.27: the 0.3.22 SHARDS TILE (slot 11) is gone - Skyy 2026-10-15: each shard's menu opens only from its portal on your island
''')
rep('''    ("main", 12, "Skyy_Menu_Icon_IslandMenu", "Island Menu",
        ["Your island in one page: members, visitors and island settings.", "Command: /island menu (or /is menu)"],
        "Click to open!", "cmdc:island menu"),''', '''    ("main", 12, "Skyy_Menu_Icon_IslandMenu", "Island Menu",
        ["Your island in one page: members, visitors and island settings.", "Command: /island menu (or /is menu)",
         "Shards: right-click one on your island to open its menu."],    # 0.3.27
        "Click to open!", "cmdc:island menu"),''')
rep('''MAIN_D = {'Shards': (1, 2), 'Pets': (0, 3),''', '''MAIN_D = {'Pets': (0, 3),''')   # 0.3.27: no Shards tile
rep('''MAIN_FREE = (27, 39, 41)''', '''MAIN_FREE = (11, 27, 39, 41)   # 0.3.27: slot 11 (the old Shards tile) is free again''')
rep('''    "Shards": {"need": "shard:fn:open"},          # 0.3.22
''', '')
rep('''assert _main["Shards"][2] == "Skyy_Menu_Icon_Shards", "0.3.26: the Shards tile wears our own icon"
assert _main["Shards"][1] == 11 and _main["Shards"][6] == "bridge:shard:fn:open" and TILE_RULES["Shards"] == {"need": "shard:fn:open"}, "0.3.22: the Shards tile"
''', '''# 0.3.27: the Shards tile is gone - no tile, no rule, no action names the shard menu (each shard's menu opens only from its portal)
assert "Shards" not in _main and "Shards" not in TILE_RULES and not [e for e in ENTRIES if "shard:fn:open" in e[6]], "0.3.27: the Shards tile is gone"
assert 11 in MAIN_FREE and 11 not in [e[1] for e in _main.values()], "0.3.27: slot 11 is free"
assert [l for l in _main["Island Menu"][4] if l.startswith("Shards: right-click")], "0.3.27: the Island Menu tile tells where shard menus open"
''')
rep('''_W1 = dict([(("tp", 11), "MyIsland"), (("tp", 13), "Hub"), (("tp", 15), "Spawn"), (("players", 47), "Accept"), (("players", 51), "Deny"),
            (("main", 11), "Shards")])''', '''_W1 = dict([(("tp", 11), "MyIsland"), (("tp", 13), "Hub"), (("tp", 15), "Spawn"), (("players", 47), "Accept"), (("players", 51), "Deny")])
# 0.3.27: (("main", 11), "Shards") left with the tile; the icon item Skyy_Menu_Icon_Shards still ships (hidden, never held)''')

# ---------------------------------------------------------------------------------------------------------------- done
assert "shard:fn:open" not in s.split('"""', 2)[2].replace("no shard:fn:open", "").replace('"shard:fn:open" in e[6]', ""), \
    "0.3.27: shard:fn:open is still named in the code"
_u = s
for _new, _old in reversed(CHANGES):
    assert _new == "" or _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    if _new == "":
        continue
    _u = _u.replace(_new, _old, 1)
# the one deletion (TILE_RULES) is put back by position: its neighbours are unique
_u = _u.replace('''    "Wardrobe": {"need": "wardrobe:fn:open"},
}''', '''    "Wardrobe": {"need": "wardrobe:fn:open"},
    "Shards": {"need": "shard:fn:open"},          # 0.3.22
}''', 1)
assert _u == OLD, "the generated script differs from 0.3.26 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.26 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
