"""Derive SkyyMenu/build_skyymenu_0.3.39.py from the LIVE SkyyMenu 0.3.38 (python tools/menu_0_3_39_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_38_patch.py -> 0.3.38 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.39. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.38 (nothing else changed). Line endings kept. The harness SkyyMenu/test_skyymenu_0.3.39.py is its own file.

0.3.39 (2026-10-18) = THE SUPPLIES TAB PICTURE + the Mods list version table.
  1. SUPPLIES TAB PICTURE (RESUME NEXT 2): Storage > Supplies (SkyyCooking 0.1.11's Potion Flask + Food Pouch tab) gets its 72 px tab
     picture pair like every other hub tab: art/hub-tab-icons/storage_supplies.png + storage_supplies_on.png (tools/art/
     make_hub_tab_icons.py t_supplies - the approved black-leather satchel look of art/accessory-bag-icon with a red potion flask and a
     tied food pouch peeking out; original pixels; the generator's --check validator passes). The art manifest now lists it, so TAB_ART
     holds storage_supplies again and the 0.3.38 TAB_NO_ART exemption is dropped: the jar ships Common/UI/Custom/SkyyHubTabs/
     storage_supplies(_on)@2x.png and every tab row (SkyyMenu's and the kit 1.7 row 2 of other mods while SkyyMenu is loaded) draws it
     behind the word. TAB_ICON["storage:supplies"] stays the satchel icon item Skyy_Menu_Icon_Supplies (0.3.38).
  2. MODS LIST VERSIONS: MODS_VERSIONS (the "version" a Mods entry shows while that mod is NOT installed) was frozen at old pins
     (SkyyAccessories 0.5.22 ...); it is rewritten from tools/deploy_set.py SET as it stands when this patch runs (same mods, same order;
     only the values change - a mod not in SET keeps its old value).
     ROUND_PINS {} (0.3.36's SkyyAccessories 0.5.21 -> 0.5.22 pin deployed long ago; it would fail against the live table).
  No new command, permission, setting or bridge key. Saved data: unchanged.
  ROLLBACK to 0.3.38: safe (the Supplies tab shows its label only; the offline Mods versions read old). NOTE: regenerating / rebuilding
  0.3.38 from its script now trips its TAB_NO_ART assert (the art manifest lists Supplies) - roll back with the built 0.3.38 jar.
"""
import ast, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G
import json

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.38.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.39.py"))
assert P.has('VERSION = "0.3.38"\n') and P.has("TAB_NO_ART") and P.has("tools/menu_0_3_38_patch.py"), "not the generated SkyyMenu 0.3.38 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# the art this round wires in (made + validated by tools/art/make_hub_tab_icons.py)
_tam = json.load(open(os.path.join(ROOT, "art", "hub-tab-icons", "manifest.json"), encoding="utf8"))
assert [(_i["hub"], _i["tab"]) for _i in _tam["icons"]].count(("storage", "supplies")) == 1 and \
    {"storage_supplies.png", "storage_supplies_on.png"} <= set(_f["path"] for _f in _tam["files"]), \
    "art/hub-tab-icons has no Supplies pair - run python tools/art/make_hub_tab_icons.py first"

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.39: the Storage > Supplies tab picture pair (art/hub-tab-icons storage_supplies, notes: tools/menu_0_3_39_patch.py) - TAB_NO_ART
       dropped; MODS_VERSIONS = tools/deploy_set.py SET of 2026-10-18.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.39.py.
''')
P.rep('VERSION = "0.3.38"\n', 'VERSION = "0.3.39"\n')

# =================================================================================================== 1. the Supplies tab picture
P.rep('''TAB_NO_ART = ("storage:supplies",)   # 0.3.38: no approved 72 px tab picture pair yet - the tab shows its label only (as in 0.3.37)
assert TAB_ART == sorted(_t.replace(":", "_") for _t in TAB_ICON if _t not in TAB_NO_ART), "0.3.30: one tab icon picture per contract tab (no Multitool)"''',
      '''# 0.3.39: Supplies has its picture pair (art/hub-tab-icons storage_supplies) - the 0.3.38 TAB_NO_ART exemption is gone
assert TAB_ART == sorted(_t.replace(":", "_") for _t in TAB_ICON), "0.3.30: one tab icon picture per contract tab (no Multitool)"
assert "storage_supplies" in TAB_ART, "0.3.39: the Supplies tab picture"''')

# =================================================================================================== 2. MODS_VERSIONS = the live SET
_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
assert _set and "SkyyMenu" in _set, "tools/deploy_set.py SET"
_blk = re.findall(r"^MODS_VERSIONS = \{\n.*?^\}", P.s, re.M | re.S)
assert len(_blk) == 1, "MODS_VERSIONS block: %d found" % len(_blk)
_old = re.findall(r'"(\w+)": "([\d.]+)"', _blk[0])
assert len(_old) == 25 and _old[0][0] == "SkyyHud" and dict(_old)["SkyyAccessories"] == "0.5.22", "the 0.3.38 table"
_new = [(_m, _set.get(_m, _v)) for _m, _v in _old]
_lines = ["    " + ", ".join('"%s": "%s"' % p for p in _new[i:i + 5]) + "," for i in range(0, len(_new), 5)]
P.rep(_blk[0], "MODS_VERSIONS = {   # 0.3.39: = tools/deploy_set.py SET of 2026-10-18\n" + "\n".join(_lines) + "\n}")
print("0.3.39 MODS_VERSIONS:", ", ".join("%s %s -> %s" % (_m, _v, _n2) for (_m, _v), (_x, _n2) in zip(_old, _new) if _v != _n2))
print("0.3.39 MODS_VERSIONS: not in SET (kept):", [_m for _m, _v in _old if _m not in _set])
# the 0.3.36 round pin (Accessories 0.5.21 -> 0.5.22) deployed long ago - with the table at the live SET it would fail its own check
P.rep('''ROUND_PINS = {"SkyyAccessories": ("0.5.21", "0.5.22")}   # 0.3.36: /charms (Void Charms) - deploy together''',
      '''ROUND_PINS = {}   # 0.3.39: none (0.3.36's SkyyAccessories 0.5.21 -> 0.5.22 pin is deployed; MODS_VERSIONS = the live SET)''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.39 adds no system / command"
P.finish()
