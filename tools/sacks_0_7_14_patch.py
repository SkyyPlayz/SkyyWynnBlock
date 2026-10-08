"""Derive SkyySacks/build_skyysacks_0.7.14.py from the SET pin 0.7.13 (edit THIS file, then regenerate: python tools/sacks_0_7_14_patch.py).
0.7.14 = THE NEW BAG LOOK (art wiring only; Skyy 2026-10-07 "the current ones are boring ... pull the mouth of the bag open and it has a
swirling portal inside the bag", 2026-10-08 "option 1", "mouth stays open while you hold it.", "3. yes 4. yes", "as drawn, violet. start
the bag round" - docs/answered/bags.md). Spec: models-local/art/bags/README.md 'What the later wiring round must change' + manifest.json.

What changes (assets only - every class is 0.7.13's apart from the version text; no saved data, no item id, no recipe, no text changes):
  - The art is GENERATED AT BUILD TIME by the tracked generator tools/art/make_bags.py, imported and run IN MEMORY (its write() is
    redirected into a dict, its clean_old() is a no-op - the build writes nothing outside the jar). The files are vanilla-derived (the
    player lift poses + the sparkle numbers are read from Assets.zip), so they are never committed; they only ship inside the jar.
  - The 20 typed bags Skyy_Sack_<Mining/Foraging/Farming/Combat/Smithing>_<Small/Medium/Rare/Large> (= Normal / Unique / Rare / Legendary)
    + Skyy_Sack_Omni (Mythic) get, from the generator's manifest:
      Model = the rarity's model, Texture + Icon = the type x rarity look (the Omni: its own), IconProperties = the rarity's;
      Animation = Items/SkyySacks/SkyySacks_Bag_Open.blockyanim (the held bag's own always-open loop)            [part "anim"]
      PlayerAnimationsId = SkyySack (Server/Item/Animations/SkyySack.json: Parent Block + SackLift)              [part "set"]
      Particles + FirstPersonParticles = [{SystemId SkyySack_PortalSparkle, TargetNodeName Portal}]             [part "sparkle"]
      Interactions.SwapTo = one Simple step, RunTime 0.5, Effects.ItemAnimationId SackLift (Secondary kept)     [part "lift", needs "set"]
  - Shipped in the jar (generated): the 5 rarity models, 21 textures, 21 icons, the open animation, the 2 player lift animations, the
    SkyySack player animation set, the SkyySack_PortalSparkle particle system + spawner. Nothing overrides a vanilla path (build check).
  - _bag_assets_check accepts the jar's own files (Model / Texture / Icon exist in Assets.zip OR in the jar).
  - NEW build check _bag_look_check: exactly the 21 bag ids carry the new look, each from the manifest; every referenced file ships; the
    set has the SackLift key; every Parallel anywhere in the jar's JSON has at least 2 entries (today's SkyyArmory lesson).
PARTS (below): a part the engine validator refuses (SkyySacks/test_skyysacks_0.7.14.py section V loads the jar into the REAL asset
stores) is switched off here and the build left without it - a refused pack is the worst outcome. All four parts passed V (2026-10-08).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.13.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.14.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)

PARTS = {"anim": True, "set": True, "sparkle": True, "lift": True}   # switch a part off if the engine validator refuses it
assert not PARTS["lift"] or PARTS["set"], "the SwapTo lift plays a key of the SkyySack set"


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:90]
    assert count != 1 or s.count(old) == 1, "anchor not unique: " + old[:90]
    s = s.replace(old, new, count)


assert 'VERSION = "0.7.13"' in s and "SackBridge" in s and "sacks:fn:commit" in s and "make_bags" not in s, \
    "the source must be the generated 0.7.13 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
_ASSETS_MARK = "# ================= assets =================" + LF
assert s.count(_ASSETS_MARK) == 1
CODE013 = s[s.index('"""' + LF + "import sys, os"):s.index(_ASSETS_MARK)]   # every line before the assets: only the version changes

# ================= docstring + version =================
rep('"""SkyySacks 0.7.13 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.13.py           -> SkyySacks/SkyySacks-0.7.13.jar   (deploys go through tools/deploy_set.py --yes)' + LF
    + '       python build_skyysacks_0.7.13.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world (never used)' + LF,
    '"""SkyySacks 0.7.14 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.14.py           -> SkyySacks/SkyySacks-0.7.14.jar   (deploys go through tools/deploy_set.py --yes)' + LF
    + '       python build_skyysacks_0.7.14.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world (never used)' + LF)
rep("line per take / put. Magic Bags themselves are never in a bag (homeOf = null): a bag id answers 0. Everything else is 0.7.12's." + LF + '"""' + LF,
    "line per take / put. Magic Bags themselves are never in a bag (homeOf = null): a bag id answers 0. Everything else is 0.7.12's." + LF
    + "0.7.14 (derived from 0.7.13 by tools/sacks_0_7_14_patch.py - edit the patch, not this file; Skyy 2026-10-08 \"as drawn, violet. start the" + LF
    + "bag round\"): THE NEW BAG LOOK - art wiring only. tools/art/make_bags.py runs IN MEMORY at build time (vanilla-derived files: never" + LF
    + "committed, only in the jar); the 20 typed bags + the Omni get the rarity model, the type x rarity texture + icon, IconProperties, the" + LF
    + "always-open held animation, the SkyySack player set (Block + SackLift), the violet SkyySack_PortalSparkle particles on node Portal and" + LF
    + "a SwapTo lift (Simple 0.5 s, ItemAnimationId SackLift). Classes, ids, recipes, texts and saved data are 0.7.13's." + LF + '"""' + LF)
rep('VERSION = "0.7.13"', 'VERSION = "0.7.14"')

# ================= the art, generated at build time =================
ART = r'''# ================= 0.7.14 THE NEW BAG LOOK (tools/sacks_0_7_14_patch.py docstring) =================
# tools/art/make_bags.py (tracked, deterministic) runs IN MEMORY: its write() fills BAG_GEN instead of models-local/art/bags/, its
# clean_old() does nothing - the build writes no art file anywhere but the jar (vanilla-derived: never committed).
BAG_PARTS = @PARTS@   # tools/sacks_0_7_14_patch.py PARTS (a part the engine validator refuses is off)
def _bag_art():
    import importlib.util
    spec = importlib.util.spec_from_file_location("make_bags", os.path.join(HERE, "..", "tools", "art", "make_bags.py"))
    mb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mb)
    got = {}
    def _w(rel, data):
        assert rel not in got, "make_bags wrote %s twice" % rel
        got[rel] = bytes(data)
        return rel
    mb.write = _w
    mb.clean_old = lambda: None
    mb.main()
    return mb, got
BAG_MB, BAG_GEN = _bag_art()
BAG_MAN = json.loads(BAG_GEN["manifest.json"].decode("utf-8"))
_A = BAG_MAN["animations"]
BAG_SET_ID, BAG_LIFT_KEY = _A["player_set_id"], _A["lift_key"]
_P = BAG_MAN["particles"]["item_fields"]
def _nc(p):
    assert p.startswith("Common/"), p
    return p[len("Common/"):]
BAG_LOOK = {}
for _e in BAG_MAN["sacks"]:
    for _it in _e["items"]:
        _lk = {"Model": _nc(_e["model_path"]), "Texture": _nc(_it["texture_path"]), "Icon": _nc(_it["icon_path"]),
               "IconProperties": _e["icon_properties"]}
        if BAG_PARTS["anim"]:
            _lk["Animation"] = _nc(_e["animation_path"])
        if BAG_PARTS["set"]:
            _lk["PlayerAnimationsId"] = _e["player_animations_id"]
        if BAG_PARTS["sparkle"]:
            _lk["Particles"] = _P["Particles"]
            _lk["FirstPersonParticles"] = _P["FirstPersonParticles"]
        BAG_LOOK[_it["item"]] = _lk
assert sorted(BAG_LOOK) == sorted(MANAGED_IDS + [BAG_OMNI]), "the manifest maps exactly the 20 typed bags + the Omni: %s" % sorted(BAG_LOOK)
BAG_SWAPTO = {"Interactions": [{"Type": "Simple", "RunTime": 0.5, "Effects": {"ItemAnimationId": BAG_LIFT_KEY}}]}
# the generated files that ship in this jar (the Accessory Bag's go to SkyyAccessories; sheet / previews / manifest stay out)
def _bag_ships(rel):
    if rel.startswith("Common/Items/SkyySacks/"):
        return BAG_PARTS["anim"] or not rel.endswith(".blockyanim")
    if rel.startswith("Common/Icons/ItemsGenerated/SkyySacks_Bag_"):
        return True
    if rel.startswith("Common/Characters/Animations/Items/SkyySacks/") or rel == _A["player_set_draft"]:
        return BAG_PARTS["set"]
    if rel.startswith("Server/Particles/SkyySacks/"):
        return BAG_PARTS["sparkle"]
    return False
BAG_FILES = {}
for _rel in sorted(BAG_GEN):
    if _bag_ships(_rel):
        BAG_FILES[_rel] = BAG_GEN[_rel].decode("utf-8") if _rel.startswith("Server/") else BAG_GEN[_rel]
def bag_look(item_id, node):
    """0.7.14: the new look of a magic bag (only ids the manifest maps; anything else keeps its node unchanged)"""
    lk = BAG_LOOK.get(item_id)
    if lk is None:
        return node
    node.update(lk)
    if BAG_PARTS["lift"]:
        node["Interactions"]["SwapTo"] = BAG_SWAPTO
    return node
print("bag art: %d generated files in memory (tools/art/make_bags.py), %d ship in the jar; parts %s" % (
    len(BAG_GEN), len(BAG_FILES), ", ".join(k for k in ("anim", "set", "sparkle", "lift") if BAG_PARTS[k]) or "none"))

'''.replace("@PARTS@", repr(PARTS))
rep(_ASSETS_MARK, _ASSETS_MARK + ART)

# ================= sack_item: the look on top of the 0.7.13 node =================
rep('''    return {
      "TranslationProperties": {"Name": "server.items.%s.name" % item_id, "Description": "server.items.%s.description" % item_id},''',
    '''    node = {
      "TranslationProperties": {"Name": "server.items.%s.name" % item_id, "Description": "server.items.%s.description" % item_id},''')
rep('''      "Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": page_id}}]}}
    }
files = {}''', '''      "Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": page_id}}]}}
    }
    return bag_look(item_id, node)   # 0.7.14: the new look (Model / Texture / Icon / IconProperties / Animation / set / particles / SwapTo)
files = {}''')

# ================= ship the generated files =================
rep('''files["Common/" + WB.icon_path("SkyySacks")] = WB.icon_png(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
''', '''files["Common/" + WB.icon_path("SkyySacks")] = WB.icon_png(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
# 0.7.14: the generated bag art (models, textures, icons, animations, the player set, the sparkles - BAG_FILES above)
for _rel, _data in BAG_FILES.items():
    assert _rel not in files, "bag art would replace " + _rel
    files[_rel] = _data
''')

# ================= _bag_assets_check accepts the jar's own files =================
rep('''    def exists(p):
        q = "Common/" + p
        return q in names or (q.endswith(".png") and q[:-4] + "@2x.png" in names)''',
    '''    def exists(p):
        q = "Common/" + p
        return q in names or q in files or (q.endswith(".png") and q[:-4] + "@2x.png" in names)   # 0.7.14: + the jar's own files''')
rep('''                raise SystemExit("0.7.7 asset check: %s %s %s is not in Assets.zip" % (iid, k, node[k]))''',
    '''                raise SystemExit("0.7.7 asset check: %s %s %s is not in Assets.zip or the jar" % (iid, k, node[k]))''')

# ================= the new build check =================
CHECK = r'''

def _bag_look_check():
    """0.7.14 build checks: exactly the 21 bag ids carry the new look, each = the manifest; every file a look names ships in the jar (and no
    vanilla path is replaced); the set has the lift key; the open animation is 1200 frames; every Parallel in the jar has 2+ entries"""
    import zipfile
    items = dict((p.rsplit("/", 1)[1][:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    for iid, n in items.items():
        lk = BAG_LOOK[iid]
        for k, v in lk.items():
            assert n[k] == v, (iid, k, n[k], v)
        for k in ("Model", "Texture", "Icon"):
            assert ("Common/" + n[k]) in files and isinstance(files["Common/" + n[k]], bytes), (iid, k, n[k])
        if BAG_PARTS["anim"]:
            assert ("Common/" + n["Animation"]) in files, (iid, n["Animation"])
        assert n["Interactions"]["Secondary"]["Interactions"][0]["Type"] == "OpenCustomUI", iid
        assert ("SwapTo" in n["Interactions"]) == BAG_PARTS["lift"], iid
        assert n["Recipe"]["Input"] and n["Quality"] and n["MaxStack"] == 1, iid
    assert len(set(n["Texture"] for n in items.values())) == 21 and len(set(n["Icon"] for n in items.values())) == 21, "21 looks"
    assert len(set(n["Model"] for n in items.values())) == 5, "one model per rarity"
    if BAG_PARTS["set"]:
        st = json.loads(files["Server/Item/Animations/%s.json" % BAG_SET_ID])
        assert st["Parent"] == "Block" and BAG_LIFT_KEY in st["Animations"], st.get("Animations")
        for k in ("ThirdPerson", "FirstPerson"):
            assert ("Common/" + st["Animations"][BAG_LIFT_KEY][k]) in files, st["Animations"][BAG_LIFT_KEY][k]
    if BAG_PARTS["sparkle"]:
        ps = json.loads(files["Server/Particles/SkyySacks/SkyySack_PortalSparkle.particlesystem"])
        assert [x["SpawnerId"] for x in ps["Spawners"]] == ["SkyySack_PortalSparkle"] and "Server/Particles/SkyySacks/SkyySack_PortalSparkle.particlespawner" in files
    if BAG_PARTS["anim"]:
        oa = json.loads(files["Common/Items/SkyySacks/SkyySacks_Bag_Open.blockyanim"].decode("utf-8"))
        assert oa["duration"] == 1200 and oa["nodeAnimations"], "the always-open loop"
    bad = []
    def walk(p, x):
        if isinstance(x, dict):
            if x.get("Type") == "Parallel" and len(x.get("Interactions") or []) < 2:
                bad.append(p)
            for v in x.values():
                walk(p, v)
        elif isinstance(x, list):
            for v in x:
                walk(p, v)
    nj = 0
    for p, t in files.items():
        if p.startswith("Server/") and p.endswith(".json"):
            walk(p, json.loads(t))
            nj += 1
    assert not bad, "a Parallel with fewer than 2 entries (the engine refuses the whole pack): %s" % bad
    za = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    if os.path.isfile(za):
        with zipfile.ZipFile(za) as z:
            van = set(z.namelist())
        clash = sorted(p for p in BAG_FILES if p in van)
        assert not clash, "bag art must never replace a vanilla file: %s" % clash
    print("bag look checked: %d bags (5 models, 21 textures + icons), %d generated files shipped, %d JSON files without a short Parallel"
          % (len(items), len(BAG_FILES), nj))
_bag_look_check()
'''
rep(LF + "_bag_assets_check()" + LF, LF + "_bag_assets_check()" + LF + CHECK)

# ================= self-checks =================
assert 'VERSION = "0.7.14"' in s and s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "no new command or ECS system"
assert s[s.index('"""' + LF + "import sys, os"):s.index(_ASSETS_MARK)] == CODE013.replace('VERSION = "0.7.13"', 'VERSION = "0.7.14"'), \
    "every line before the assets = 0.7.13's (only the version)"
assert 0 <= s.find("def bag_look(") < s.find("def sack_item(") < s.find("return bag_look(item_id, node)") < s.find("files = {}")
assert s.find("for _rel, _data in BAG_FILES.items():") < s.find("_bag_assets_check()") < s.find("_bag_look_check()") < s.find("B.assemble(")
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
