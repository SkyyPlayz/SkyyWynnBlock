"""Derive SkyyShards/build_skyyshards_0.4.8.py from the GENERATED SkyyShards 0.4.7 (build_skyyshards_0.4.7.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_7_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.7 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_8_patch.py   then   python SkyyShards/build_skyyshards_0.4.8.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.8.py

0.4.8 (2026-10-23) = THE STARTER ARCHIPELAGO, ROUND R1 (research/Starter-Archipelago-Spec.md v2 sections 5, 7, 8, 9, 13, 15; Skyy
  2026-10-23: "i changed my mind on the shards. since they start at T1 and you have to work your way up. how about you just start with them."
  + "and we make them cheap and easy to upgrade at first, and get harder as you go." + "so its more manual until at least the first shard
  island upgrade." + layout v2 "much better! we can go with that"; every default in docs/answered/world.md 2026-10-23).
  1. SHARD DOORS (spec 5): bridge shard:fn:door = Function(Object[]{ UUID owner, String pkey, String kind, String world, Integer x, y, z })
     -> "+" recorded / "=" already known / "-..." refused. SkyyIslands 0.5.25 places the Skyy_Shard_<Kind> block on each starter island and
     calls it: the door becomes the shard's placed record (<kind>.placed, as a placed portal) + <kind>.door.starter (the same text) and the
     shard gets its T1 island (manual). A starter door cannot be picked up. A newer island (island reset) moves the door; a portal the
     player placed by hand on the current island is kept (the door is recorded beside it). Without the bridge nothing changes.
  2. LOCKS (spec 5): shard.lock.<kind> (default 5, 0 = open) on skill shard.lock.skill.<kind> (Farming / Foraging / Mining / Orchard /
     Ranching / class): the CLICKING player's own level (skill:fn:run, the class skill for Combat; skill:fn:level as the older fallback;
     unknown = open). Locked = the shard menu opens on a lock card (the strip says "Farming Shard - locked. Reach Farming 5 to open it. You:
     Farming 2." in red) and Enter / Collect / every upgrade / buy is refused with the same line. One chat line when the page opens.
  3. 0.4.6's LEVEL 20 GRANTS ARE OFF: ShMig048 (PROJECT-RULES 4; ShMig046's machinery) rewrites each lv20.<kind> still holding 20 to 0 (+
     totem.upCost "1:10,2:25,3:50,5:100" -> "1:4,2:16,4:40,8:100" and storage.coins.2..5 to the cheap-first ladder steps 6 / 8 / 9 / 10 =
     14,500 / 105,000 / 375,000 / 1,260,000), History snapshot first, one change-log line each with Undo, marker skyyshards-0.4.8-map.
     Shards already given stay valid; the 0.4.6 island.* / grow.*.coins rows stay in the file but are no longer read.
  4. ONE ISLAND PER TIER (spec 9): each shard's islands follow its tools/tier_tags.py ladder (Farming 15 crops, Foraging 15 tree tiers,
     Mining 11 ores, Orchard 8 fruits, Ranching 8 animals; Combat keeps its one skeleton island until R5). <kind>.i<n>.type = the tier's key
     (T1 keys unchanged: wheat / oak / copper / apple / chicken / skeleton). Buying is in order (T(n) needs T(n-1)); a bought island goes
     into the first free slot (16 slots: the 6 hexagon places of 0.4.x + 10 on an outer ring at 104 blocks, bridged to the nearest inner
     island). Collect gives each island's own item (and its Enchanted / smelted form).
  5. SIZE + 3 SUB-UPGRADES x 5 (spec 8): Amount / Decorations / Irrigation (Mining: Ore Amount / Decorations / Underground Springs;
     Ranching: Herd Size / Decorations / Water Troughs), levels 0-5 per size; Grow only at 5 / 5 / 5, then the three start at 0 again but
     never lose what they gave (the level counts on: 5 x (size - 1) + level). Visible: Amount = the share of spots filled (60 % .. 100 %),
     Decorations = vanilla props per level (isl.deco.props single-cell props a level, each level its own pair: flowers, fences + lanterns, hay + barrels, crates + planters, crystals ...), Irrigation = 2 x 2 water pools
     (FluidSection, the SkyyIslands pond path). Output x (1 + isl.amount.bonus % x levels) x (1 + isl.deco.pct % x levels) x (1 +
     isl.irrigation.pct % x levels), 0.5 % each by default so a maxed Large = x1.24 <= the spec's x1.25 ceiling. DECISION (open question
     for Skyy, fix2 wording): spec 8 asks for three things that cannot all hold here - deco + irrigation +2 % a level (x1.30 each = x1.69
     from those two rows alone), Amount = the share of spots filled (60 -> 100 %, x1.67 more if output followed the spots), AND "a T1 Small
     with subs 0 = today's Small, a maxed Large = today's Large x1.25" (the P6 idle cap). A totem's output does not count spots, so
     isl.amount.bonus stands in for the spec's "covered / ref" and the three rows share the x1.25 budget equally; the only way to show
     +2 % rows would be to make every new island start BELOW today's output. Server Setup can change all three.
  6. THE CHEAP-FIRST COST LADDER (spec 13, exactly its numbers): coins = round7(hours x 8,333 x the coin curve at the level); shard
     ladder steps 230 .. 1,260,000 (up.levels / up.hours); Automation = step 2 (550) + 128 of the shard's T1 item; island buy 0.5 h, subs
     0.01 .. 0.6 h, grows 0.15 / 0.5 h at the island's tier band (T1 1, T2 8 ... T15 95); materials per row (isl.mat.*, isl.buyItems.*).
     tools/balance_model.py --p11 --check proves them.
  7. MANUAL FIRST (spec 7): until the shard's Automation (once per shard, <kind>.auto=1) totems work at shard.manualPct (50) % on what is
     planted NOW: Farming starts with 8 Eternal Wheat around the centre + tilled soil (planting / watering / tilling allowed there,
     shard:fn:allowed); a seed / sapling store per island (Give seeds / Take back, shard.seedStoreMax 640) - every regrow (shard.regrowSec)
     and Enter replants empty cells / tree spots from it (1 each) and the scan is saved (<kind>.i<n>.pl / .tp); planted output uses (1 -
     shard.seedReturnPct %) of a seed per item (trees: 1 sapling per shard.itemsPerSapling items); offline counts at most
     shard.manualOfflineSec (7,200 s). Automated = 0.4.7's behaviour (every spot Eternal / regrown, 3 days offline). Every shard that already
     has islands is grandfathered Automated.
  8. MINING = COPPER CAVES (spec 9.3): every Mining island is a cave in a rock island of its ore's host rock (chamber 11 / 19 / 27 wide,
     5 / 7 / 9 high, an opening toward its bridge), ore on a fixed share of the walls / ceiling (Small 8 .. 28 %, Medium / Large from the size
     below's max); existing Mining islands are rebuilt once (marker <kind>.i<n>.cave=1; only our old ore nodes are cleared, exactly the old
     id) with Small -> Amount 2, Medium -> 1, Large -> 0: never fewer ore nodes than 16 / 72 / 160.
  9. PLAYER FILES (spec 15, once per profile, marker map.done=1, the file copied to shards/history/map/ first, byte-checked): Automation
     grandfathered (<kind>.auto=1) on every shard with islands; 0.4.6's extra islands of a shard become its next tiers in slot order (slot 2
     -> Lettuce, slot 3 -> Carrot ...; totems / storage kept; what they had stored is paid out as the OLD item: <kind>.i<n>.legacy); Mining
     sub levels as above. One collect.log line with the Undo.
  10. QUEST EVENTS (spec 12, SkyyQuests quest:fn:event): shard:door:<kind> (Enter), shard:seeds:<kind> (seeds given), shard:auto:<kind>.
  NOT IN THIS ROUND: the radial map page (R3 - the menu keeps its tabs; the Islands tab is a grid of the ladder with the new buttons),
  spec 8's multi-block set pieces read from vanilla prefabs (windmill, barn, fountain, waterfall; irrigation channels -> pond -> fountain)
  - this round places single-cell vanilla props + 2 x 2 pools only (fix2: scope cut stated, a later round),
  quests (R4), the Combat zone islands (R5).
  SAVED DATA: new keys only (<kind>.door.starter, .auto, .i<n>.amt / .deco / .irr / .eternal / .seed / .pl / .tp / .seeded / .cave /
  .legacy / .sacc, map.done); <kind>.i<n>.type holds the tier key.
  ROLLBACK 0.4.8 -> 0.4.7: TOGETHER with SkyyIslands 0.5.24 (FLOOR); Undo the ShMig048 rows first (Server Setup -> Shards -> Changes); copy
  shards/history/map/<pkey>.pre-0.4.8.properties back over shards/<pkey>.properties with the server stopped (0.4.7 cannot read crop-typed
  islands beyond the T1 type - it treats them as its one type). Added cave / deco blocks stay as plain blocks.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.7.py"), os.path.join(HERE, "build_skyyshards_0.4.8.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.7"\n') and P.has("GENERATED by tools/shards_0_4_7_patch.py") and not P.has("ShMig048"), "not the generated SkyyShards 0.4.7"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.8 (2026-10-23)"):].rstrip() + "\n"

P.rep('''"""SkyyShards 0.4.7 - build script (javassist via jpype). GENERATED by tools/shards_0_4_7_patch.py from build_skyyshards_0.4.6.py
(generated by tools/shards_0_4_6_patch.py from 0.4.5, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.7" / "0.4.6" / "0.4.5" / "0.4.4" / "0.4.3" / "0.4.2" / "0.4.1" / "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.7.py   -> SkyyShards/SkyyShards-0.4.7.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.7.py
''', '''"""SkyyShards 0.4.8 - build script (javassist via jpype). GENERATED by tools/shards_0_4_8_patch.py from build_skyyshards_0.4.7.py
(generated by tools/shards_0_4_7_patch.py from 0.4.6, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.8" / "0.4.7" / "0.4.6" / "0.4.5" / "0.4.4" / "0.4.3" / "0.4.2" / "0.4.1" / "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.8.py   -> SkyyShards/SkyyShards-0.4.8.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.8.py
''' + NOTE + '''
0.4.7 notes:
''')
P.rep('VERSION = "0.4.7"\n', 'VERSION = "0.4.8"\n')

# ================================================================================================ engine types (fluids: the irrigation pools)
P.rep('''    "TU":   "com.hypixel.hytale.server.core.util.TargetUtil",                                # fix4: the totem block looked at
''', '''    "TU":   "com.hypixel.hytale.server.core.util.TargetUtil",                                # fix4: the totem block looked at
    "FSC":  "com.hypixel.hytale.server.core.universe.world.chunk.section.FluidSection",     # 0.4.8: irrigation pools (the SkyyIslands pond path)
    "FLU":  "com.hypixel.hytale.server.core.asset.type.fluid.Fluid",
''')
P.rep('''             (T["IC"], "replaceItemStackInSlot")):
    B.probe(pool, c, m)''', '''             (T["IC"], "replaceItemStackInSlot"),
             # 0.4.8: the irrigation water (SkyyIslands 0.5.20's pond path: FluidSection.setFluid + setTicking)
             (T["FSC"], "getComponentType"), (T["FSC"], "setFluid"), (T["FSC"], "getFluidId"), (T["FLU"], "getAssetMap"), (T["FLU"], "getMaxFluidLevel")):
    B.probe(pool, c, m)''')

# ================================================================================================ the 16 island places (spec 9.4, kept positions)
P.rep('''SLOTS = 6
RING = 48                               # spec 9.1: 6 fixed slots on a hexagon 48 blocks out''',
      '''SLOTS = 16                              # 0.4.8: one island per tier (ladders up to 15) - 6 inner hexagon places (0.4.x, unchanged) + 10 outer
RING = 48                               # spec 9.1: 6 fixed slots on a hexagon 48 blocks out
RING2 = 104                             # 0.4.8: the outer ring (10 places, 36 degrees apart, between the hexagon's spokes)
NINNER = 6''')
P.rep('''SLOT_POS = []
for _i in range(SLOTS):                 # slot 1 = north (-z), then clockwise
    _a = math.radians(-90 + 60 * _i)
    SLOT_POS.append((int(round(RING * math.cos(_a))), int(round(RING * math.sin(_a)))))
for _i in range(SLOTS):''', '''SLOT_POS = []
for _i in range(NINNER):                # slot 1 = north (-z), then clockwise
    _a = math.radians(-90 + 60 * _i)
    SLOT_POS.append((int(round(RING * math.cos(_a))), int(round(RING * math.sin(_a)))))
SLOT_SRC = [-1] * NINNER                # 0.4.8: where each slot's bridge starts (-1 = the hub, else the inner slot it hangs on)
for _j in range(SLOTS - NINNER):        # 0.4.8: the outer ring, bridged to the nearest inner island
    _a = math.radians(-90 + 18 + 36 * _j)
    SLOT_POS.append((int(round(RING2 * math.cos(_a))), int(round(RING2 * math.sin(_a)))))
    _best = min(range(NINNER), key=lambda _i: (math.hypot(SLOT_POS[-1][0] - SLOT_POS[_i][0], SLOT_POS[-1][1] - SLOT_POS[_i][1]), _i))
    SLOT_SRC.append(_best)
assert len(SLOT_POS) == SLOTS == len(SLOT_SRC)
for _i in range(SLOTS):''')
P.rep('''assert RING - HALF[2] - HUB_HALF >= 8, "the hub and a Large island leave a bridge"
CHUNKS = sorted(set(((REGION_X + dx) >> 5, (REGION_Z + dz) >> 5) for dx in range(-(RING + HALF[2] + 2), RING + HALF[2] + 3)
                    for dz in range(-(RING + HALF[2] + 2), RING + HALF[2] + 3)))
assert len(CHUNKS) <= 25, CHUNKS''', '''assert RING - HALF[2] - HUB_HALF >= 8, "the hub and a Large island leave a bridge"
# 0.4.8: every bridge (hub -> inner, inner -> outer) runs clear of every OTHER island at Large (+ 2 blocks) and of the hub
def _bridge_cells48(i):
    _s = SLOT_SRC[i]
    _ax, _az = (0, 0) if _s < 0 else SLOT_POS[_s]
    _bx, _bz = SLOT_POS[i]
    _ln = math.hypot(_bx - _ax, _bz - _az)
    _ux, _uz = (_bx - _ax) / _ln, (_bz - _az) / _ln
    _t0 = (HUB_HALF - 1) if _s < 0 else HALF[0]
    _out = set()
    _t = float(_t0)
    while _t <= _ln - HALF[0]:
        for _w in (-1, 0, 1):
            _out.add((int(round(_ax + _ux * _t - _uz * _w)), int(round(_az + _uz * _t + _ux * _w))))
        _t += 0.5
    return _out
for _i in range(SLOTS):
    for (_x, _z) in _bridge_cells48(_i):
        for _j in range(SLOTS):
            if _j in (_i, SLOT_SRC[_i]):
                continue
            assert max(abs(_x - SLOT_POS[_j][0]), abs(_z - SLOT_POS[_j][1])) > HALF[2] + 2, "0.4.8: the bridge of slot %d crosses slot %d" % (_i, _j)
        if SLOT_SRC[_i] >= 0:
            assert abs(_x) + abs(_z) > HUB_HALF + 4, "0.4.8: an outer bridge crosses the hub"
EXT48 = RING2 + HALF[2] + 2
CHUNKS = sorted(set(((REGION_X + dx) >> 5, (REGION_Z + dz) >> 5) for dx in range(-EXT48, EXT48 + 1) for dz in range(-EXT48, EXT48 + 1)))
assert len(CHUNKS) <= 81, CHUNKS        # 0.4.8: the full region (a paint loads only the chunks its blocks are in)
assert EXT48 < 512 - 8, "0.4.8: a region stays inside its 1,024 blocks"''')
P.rep('''    _ch = sorted(set(((1024 * _k + dx) >> 5, dz >> 5) for dx in range(-(RING + HALF[2] + 2), RING + HALF[2] + 3)
                     for dz in range(-(RING + HALF[2] + 2), RING + HALF[2] + 3)))''',
      '''    _ch = sorted(set(((1024 * _k + dx) >> 5, dz >> 5) for dx in range(-EXT48, EXT48 + 1) for dz in range(-EXT48, EXT48 + 1)))''')

# ================================================================================================ build-time model: ladders, costs, geometry tables
P.rep('''# ================= config (the kit's DEFAULTS and the first-run file are the same text) =================
''', '''# ================= 0.4.8 ONE ISLAND PER TIER (research/Starter-Archipelago-Spec.md 9; tools/shards_0_4_8_patch.py) =================
# Each shard's islands follow its ladder from tools/tier_tags.py (sorted by tier): one island type per tier, T1 keys = the 0.3 types.
import tier_tags as _TT48
import balance_model as _BM48
_ENCHB48 = dict((_t[2], _SE.PREFIX + _t[0]) for _t in _SE.TABLE)
WG48 = set(_TT48.WG_IDS) | set(_TT48.CO_IDS) | {"Ore_Onyxium_Basalt"}   # made by SkyyWorldGen / SkyyCollections builds (not in Assets.zip)
LAD = [[] for _k in range(NK)]


def _ty48(kd, key, name, tier, prod, res1=None, leaf1=None, res2=None, leaf2=None, fruit=None, grow=None, host=None, seed=None, eseed=None, smelt=None):
    LAD[kd].append(dict(key=key, name=name, tier=tier, prod=prod, ench=_ENCHB48.get(prod), smelt=smelt, smeltEnch=_ENCHB48.get(smelt) if smelt else None,
                        res1=res1, leaf1=leaf1, res2=res2, leaf2=leaf2, fruit=fruit, grow=grow, host=host, seed=seed, eseed=eseed))


# Mining (0): the 7 vanilla ores + the 4 zone metals by tier (tier_tags ORES / ZONE_METALS); the cave rock = the ore's host
_MO48 = [("Copper", "Ore_Copper", "Ore_Copper_Stone", "Rock_Stone", "Ingredient_Bar_Copper"),
         ("Iron", "Ore_Iron", "Ore_Iron_Stone", "Rock_Stone", "Ingredient_Bar_Iron"),
         ("Thorium", "Ore_Thorium", "Ore_Thorium_Sandstone", "Rock_Sandstone", "Ingredient_Bar_Thorium"),
         ("Lead", "Ore_Lead_SkyWynn", "Ore_Lead_Sandstone_SkyWynn", "Rock_Sandstone", "Ingredient_Bar_Lead_SkyWynn"),
         ("Cobalt", "Ore_Cobalt", "Ore_Cobalt_Shale", "Rock_Shale", "Ingredient_Bar_Cobalt"),
         ("Chromium", "Ore_Chromium_SkyWynn", "Ore_Chromium_Shale_SkyWynn", "Rock_Shale", "Ingredient_Bar_Chromium_SkyWynn"),
         ("Adamantite", "Ore_Adamantite", "Ore_Adamantite_Magma", "Rock_Magma_Cooled", "Ingredient_Bar_Adamantite"),
         ("Slag", "Ore_Slag_SkyWynn", "Ore_Slag_Volcanic_SkyWynn", "Rock_Volcanic", "Ingredient_Bar_Slag_SkyWynn"),
         ("Mithril", "Ore_Mithril", "Ore_Mithril_Stone", "Rock_Stone", "Ingredient_Bar_Mithril"),
         ("Titanium", "Ore_Titanium_SkyWynn", "Ore_Titanium_Basalt_SkyWynn", "Rock_Basalt", "Ingredient_Bar_Titanium_SkyWynn"),
         ("Onyxium", "Ore_Onyxium", "Ore_Onyxium_Basalt", "Rock_Basalt", "Ingredient_Bar_Onyxium")]
assert sorted(_m[0] for _m in _MO48) == sorted([_o[0] for _o in _TT48.ORES] + [_z[0] for _z in _TT48.ZONE_METALS])
for _w, _it, _bl, _ho, _bar in sorted(_MO48, key=lambda _m: _TT48.metal_tier(_m[0])):
    _ty48(0, _w.lower(), _w, _TT48.metal_tier(_w), _it, res1=_bl, host=_ho, smelt=_bar)
# Foraging (1): one island per tree TIER (Skyy default taken: 15), its trees mixed (the tier's first two woods)


def _leaf48(w):
    _l = "Plant_Leaves_" + w
    return _l if _l in ITEMS else {"Bottletree": "Plant_Leaves_Bottle", "Ice": "Plant_Leaves_Frostwood"}.get(w, "Plant_Leaves_Oak")


def _sap48(ws):
    for _w in ws:
        _s = {"Fir": "Plant_Sapling_Spruce", "Ice": "Plant_Sapling_Spruce_Frozen"}.get(_w, "Plant_Sapling_" + _w)
        if _s in ITEMS:
            return _s
    return None


for _t in sorted(_TT48.LOGS):
    _ws = _TT48.LOGS[_t]
    _w0, _w1 = _ws[0], (_ws[1] if len(_ws) > 1 else _ws[0])
    _ty48(1, "oak" if _t == 1 else _w0.lower(), _w0.replace("_", " "), _t, "Wood_%s_Trunk" % _w0, res1="Wood_%s_Trunk" % _w0, leaf1=_leaf48(_w0),
          res2="Wood_%s_Trunk" % _w1, leaf2=_leaf48(_w1), seed=_sap48(_ws), eseed=_sap48(_ws))
# Farming (2): CROP_LADDER (15; the Mushroom from spores - Skyy 2026-10-18)
for _i, _c in enumerate(_TT48.CROP_LADDER):
    if _c == "Mushroom":
        _ty48(2, "mushroom", "Mushroom", _i + 1, "Plant_Crop_Mushroom_Cap_Brown", res1="Plant_Spores_Mushroom_Eternal", grow="Plant_Crop_Mushroom_Block",
              seed="Plant_Seeds_Mushroom", eseed="Plant_Spores_Mushroom_Eternal")
    else:
        _ty48(2, _c.lower(), _c, _i + 1, "Plant_Crop_%s_Item" % _c, res1="Plant_Crop_%s_Block_Eternal" % _c, grow="Plant_Crop_%s_Block" % _c,
              seed="Plant_Seeds_" + _c, eseed="Plant_Seeds_%s_Eternal" % _c)
# Ranching (3): the meat collections first, then the other animal products (Skyy default: produce XP later, SkyySkills R6)
for _i, (_k_, _n_, _p_) in enumerate((("chicken", "Chicken", "Food_Chicken_Raw"), ("cow", "Cow", "Food_Beef_Raw"), ("pig", "Pig", "Food_Pork_Raw"),
                                       ("boar", "Boar", "Food_Wildmeat_Raw"), ("sheep", "Sheep", "Ingredient_Fabric_Scrap_Wool"),
                                       ("turkey", "Turkey", "Ingredient_Feathers_Light"), ("goat", "Goat", "Ingredient_Hide_Light"),
                                       ("bison", "Bison", "Ingredient_Hide_Heavy"))):
    _ty48(3, _k_, _n_, _i + 1, _p_)
# Orchard (4): Apple (Skyy's T1), Berries, then the wild fruits (a bush island = no trunk, its fruit block on the spot)
for _i, (_k_, _n_, _p_, _tr, _lf, _fr, _sp) in enumerate((
        ("apple", "Apple", "Plant_Fruit_Apple", "Wood_Apple_Trunk", "Plant_Leaves_Apple", "Plant_Crop_Apple_Block", "Plant_Sapling_Apple"),
        ("berries", "Berries", "Plant_Fruit_Berries_Red", None, None, "Plant_Crop_Berry_Block", None),
        ("coconut", "Coconut", "Plant_Fruit_Coconut", "Wood_Palm_Trunk", "Plant_Leaves_Palm", None, "Plant_Sapling_Palm"),
        ("mango", "Mango", "Plant_Fruit_Mango", "Wood_Jungle_Trunk", "Plant_Leaves_Jungle", None, "Plant_Sapling_Jungle"),
        ("pinkberry", "Pinkberry", "Plant_Fruit_Pinkberry", None, None, "Plant_Crop_Berry_Wet_Block", None),
        ("azure", "Azure", "Plant_Fruit_Azure", "Wood_Azure_Trunk", "Plant_Leaves_Azure", None, "Plant_Sapling_Azure"),
        ("spiral", "Spiral", "Plant_Fruit_Spiral", "Wood_Spiral_Trunk", "Plant_Leaves_Spiral", None, "Plant_Sapling_Spiral"),
        ("windwillow", "Windwillow", "Plant_Fruit_Windwillow", "Wood_Windwillow_Trunk", "Plant_Leaves_Windwillow", None, "Plant_Sapling_Windwillow"))):
    _ty48(4, _k_, _n_, _i + 1, _p_, res1=_tr, leaf1=_lf, fruit=_fr, seed=_sp, eseed=_sp)
# Combat (5): today's skeleton island only (the zone islands are round R5)
_ty48(5, "skeleton", "Skeleton", 1, "Ingredient_Bone_Fragment")
assert [len(_l) for _l in LAD] == [11, 15, 15, 8, 8, 1], [len(_l) for _l in LAD]
assert [LAD[_k][0]["key"] for _k in range(NK)] == [ISL[_k]["type"] for _k in range(NK)], "0.4.8: the T1 keys are the 0.3 island types"
assert [LAD[_k][0]["prod"] for _k in range(NK)] == [ISL[_k]["prod"] for _k in range(NK)]
assert LAD[FARM_K][0]["res1"] == CROP["block"] and LAD[0][0]["res1"] == STYLE_BLOCKS["ore"]
for _k in range(NK):
    assert len(set(_t["key"] for _t in LAD[_k])) == len(LAD[_k]) and all(":" not in _t["key"] and "," not in _t["key"] for _t in LAD[_k])
    assert [_t["tier"] for _t in LAD[_k]] == sorted(_t["tier"] for _t in LAD[_k]), "0.4.8: sorted by tier (standing rule)"
    for _t in LAD[_k]:
        for _f in ("prod", "res1", "leaf1", "res2", "leaf2", "fruit", "grow", "host", "seed", "eseed", "smelt"):
            _v = _t[_f]
            assert _v is None or _v in ITEMS or _v in WG48 or _v in _SE.IDS, (KINDS[_k], _t["key"], _f, _v)
TY48 = [(_k, _t) for _k in range(NK) for _t in LAD[_k]]
LAD0 = [sum(len(LAD[_j]) for _j in range(_k)) for _k in range(NK)]
# the extra block ids the islands paint (after GEO_IDS + the totem blocks + the benches = XBASE): every type's blocks + the decorations
DECO48 = {   # style -> level 1..5 -> two vanilla props (single-cell blocks, build-checked below); Skyy: "visual differences per lvl"
    "farm": [("Plant_Flower_Common_Red", "Plant_Flower_Common_Yellow"), ("Wood_Softwood_Fence", "Deco_Lantern"), ("Plant_Hay_Bundle", "Furniture_Tavern_Barrel"),
             ("Furniture_Village_Crate", "Furniture_Village_Planter"), ("Rock_Stone_Brick", "Furniture_Village_Pot")],
    "grove": [("Plant_Fern_Forest", "Plant_Crop_Mushroom_Common_Brown"), ("Wood_Oak_Trunk", "Furniture_Village_Crate"), ("Furniture_Tavern_Barrel", "Plant_Bush_Green"),
              ("Deco_Lantern", "Furniture_Crude_Torch"), ("Furniture_Village_Planter", "Rock_Stone_Brick")],
    "orchard": [("Plant_Flower_Bushy_Purple", "Plant_Flower_Common_Blue"), ("Furniture_Village_Crate", "Deco_Bucket"), ("Deco_Hive", "Furniture_Village_Pot"),
                ("Wood_Softwood_Fence", "Deco_Lantern"), ("Furniture_Village_Planter", "Rock_Stone_Brick")],
    "mine": [("Deco_Lantern", "Furniture_Crude_Torch"), ("Rail", "Furniture_Village_Crate"), ("Wood_Oak_Trunk", "Furniture_Tavern_Barrel"),
             ("Rock_Crystal_Blue_Medium", "Deco_Bucket"), ("Rock_Crystal_Purple_Large", "Rock_Stone_Brick")],
    "ranch": [("Plant_Hay_Bundle", "Deco_Bucket"), ("Wood_Softwood_Fence", "Wood_Softwood_Fence"), ("Furniture_Tavern_Barrel", "Plant_Hay_Bundle"),
              ("Furniture_Village_Crate", "Deco_Lantern"), ("Rock_Stone_Brick", "Furniture_Village_Planter")],
    "arena": [(), (), (), (), ()],
}
_HB_OK48 = (None, "Plant_Small", "Plant_Medium", "Plant_Large", "Plant_Full", "Torch", "Fence_Thin", "Chest_Small", "Rail")
for _st, _lv in DECO48.items():
    assert len(_lv) == 5, _st
    for _pair in _lv:
        for _id in _pair:
            _bt = json.loads(AZ.read(ITEMS[_id]).decode("utf-8-sig")).get("BlockType")
            assert _bt is not None and _bt.get("HitboxType") in _HB_OK48, "0.4.8: decoration %s is not a one-cell block (%s)" % (_id, _bt and _bt.get("HitboxType"))
XIDS = []
for _k, _t in TY48:
    for _f in ("res1", "leaf1", "res2", "leaf2", "fruit", "grow", "host"):
        if _t[_f] and _t[_f] not in XIDS:
            XIDS.append(_t[_f])
for _st in sorted(DECO48):
    for _pair in DECO48[_st]:
        for _id in _pair:
            if _id not in XIDS:
                XIDS.append(_id)
XBASE = 24 + len(TOTEMS) + NK          # = len(GEO_IDS) + the totem blocks + the benches (asserted at ShGeo)
XRES = set(_t[_f] for _k, _t in TY48 for _f in ("res1", "leaf1", "res2", "leaf2", "fruit") if _t[_f])   # gatherables: painted only on AIR


def _xi48(v):
    return -1 if not v else XBASE + XIDS.index(v)


# the farm cells of each size, in planting order: the 8 Eternal Wheat cells around the centre first (Skyy: "8 eternal wheat around the
# totem"), then outwards; the ring just inside the rim is kept for decorations (never farmed); the totem pads' 3 x 3 stays brick
def _farm_order48(size):
    _h = HALF[size - 1]
    _cells = []
    for _dx in range(-_h, _h + 1):
        for _dz in range(-_h, _h + 1):
            _ax, _az = abs(_dx), abs(_dz)
            if max(_ax, _az) >= _h - 1 or (_ax <= 1 and _az <= 1):
                continue
            _cells.append((_dx, _dz))
    _eight = set([(2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (2, -2), (-2, 2), (-2, -2)])
    return sorted(_cells, key=lambda c: (0 if c in _eight else 1, c[0] * c[0] + c[1] * c[1], math.atan2(c[1], c[0])))


FARM48 = [_farm_order48(_s) for _s in (1, 2, 3)]
assert [len(_f) for _f in FARM48] == [72, 280, 616], [len(_f) for _f in FARM48]
assert set(FARM48[0][:8]) == set([(2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (2, -2), (-2, 2), (-2, -2)])
assert all(_c[0] * _c[0] + _c[1] * _c[1] <= 9 for _c in FARM48[0][:8]), "0.4.8: the 8 Eternal cells are inside a Totem I's range"


def _tree_order48(size):
    _h = HALF[size - 1]
    _pts = [(_dx, _dz) for _dx in range(-_h, _h + 1) for _dz in range(-_h, _h + 1)
            if max(abs(_dx), abs(_dz)) <= _h - 2 and not (abs(_dx) <= 2 and abs(_dz) <= 2) and _dx % 4 == 0 and _dz % 4 == 0]
    return sorted(_pts, key=lambda c: (c[0] * c[0] + c[1] * c[1], math.atan2(c[1], c[0])))


TREE48 = [_tree_order48(_s) for _s in (1, 2, 3)]
assert [len(_t) for _t in TREE48] == [8, 24, 48], [len(_t) for _t in TREE48]
# the cheap-first cost ladder (spec 13; tools/balance_model.py p7_H_at + p7_round - the same numbers the spec prints)
UP_LV48 = [3, 5, 8, 12, 15, 20, 28, 35, 45, 55]
UP_H48 = [0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1, 1.5, 2, 3]
SUB_H48 = [[0.01, 0.02, 0.03, 0.05, 0.07], [0.08, 0.1, 0.13, 0.16, 0.2], [0.25, 0.3, 0.4, 0.5, 0.6]]
GROW_H48, BUY_H48 = [0.15, 0.5], 0.5
COIN_H48 = _BM48.p7_H_at(10)          # 8,333.33: coins / h at Lv 10 (the P7 rule "every coin cost = hours of income at a reference level")
BAND48 = list(_BM48.BAND)
assert len(BAND48) == 16 and BAND48[0] == 1 and BAND48[1] == 8 and BAND48[14] == 95
assert [_BM48.p7_round(_h * _BM48.p7_H_at(_l)) for _l, _h in zip(UP_LV48, UP_H48)] == [230, 550, 1400, 3400, 6300, 14500, 37000, 105000, 375000, 1260000], \\
    "0.4.8: the shard ladder = spec 13.1"
assert [_BM48.p7_round(_h * _BM48.p7_H_at(1)) for _h in SUB_H48[0]] == [40, 80, 120, 200, 280] and _BM48.p7_round(0.5 * _BM48.p7_H_at(8)) == 3500, "0.4.8: spec 13.2"
UP_DEF_047 = UP_DEF
UP_DEF = "1:4,2:16,4:40,8:100"          # spec 13.1: totem tier-up I->II .. IV->V (Enchanted : Life Essence), cheaper first
AUTO_ITEMS48 = ["%s:128" % LAD[_k][0]["prod"] for _k in range(NK)]   # Automation = step 2 + 128 of the shard's T1 raw item
BUY_ITEMS48 = ["raw:128,ench:4", "raw:128,seed:16", "raw:128,seed:32", "raw:64,Tool_Capture_Crate:2", "raw:128,seed:16", "raw:64"]
assert "Tool_Capture_Crate" in ITEMS
MAT48 = {"amount": "raw:16|ench:1|ench:2", "deco": "Wood_Oak_Trunk:16,Rock_Stone_Cobble:16|Skyy_Ench_Oak:1,Skyy_Ench_Cobblestone:1|Skyy_Ench_Oak:2,Skyy_Ench_Cobblestone:2",
         "irrigation": "raw:8,Ingredient_Water_Essence:2|ench:1,Ingredient_Water_Essence:4|ench:2,Ingredient_Water_Essence:8", "grow": "ench:4,eseed:8|ench:16,eseed:24"}
for _v in list(MAT48.values()) + BUY_ITEMS48:
    for _part in _v.replace("|", ",").split(","):
        _pid = _part.split(":")[0]
        assert _pid in ("raw", "ench", "seed", "eseed") or _pid in ITEMS or _pid in _SE.IDS, "0.4.8: material %s" % _pid
AMT_PCT48 = [60, 68, 76, 84, 92, 100]
CAVE_PCT48 = [8, 12, 16, 20, 24, 28]
BONUS48 = 0.5                            # % per level of each sub-upgrade, kept across sizes (maxed Large = 1.075 ^ 3 = x1.24; the spec's +2 %: see the header, item 5)
DECO_N48 = 5                             # fix (critic): props each Decorations level places (a border section; Server Setup isl.deco.props 1-8)
assert (1 + BONUS48 * 15 / 100.0) ** 3 <= 1.25, "0.4.8: a maxed Large stays under the spec's x1.25"
LOCK_SKILL48 = ["Mining", "Foraging", "Farming", "Ranching", "Orchard", "class"]
LV20_DEF = 0                             # 0.4.8: the level 20 grants are off (Skyy 2026-10-23 "how about you just start with them")
print("0.4.8 ladders: %s islands; cave ore Small %s %%; ladder %s coins; totem.upCost %s" % (
    "/".join("%s %d" % (KINDS[_k], len(LAD[_k])) for _k in range(NK)), CAVE_PCT48,
    [_BM48.p7_round(_h * _BM48.p7_H_at(_l)) for _l, _h in zip(UP_LV48, UP_H48)], UP_DEF))

# ================= config (the kit's DEFAULTS and the first-run file are the same text) =================
''')
# the storage coins on the ladder (after 0.4.5's values) + the one-time config update's table
P.rep('''print("0.4.5 Balance P7 coin costs: storage %s, compactor %s, compressor %s, grow %d / %d, bench %s (idle share unchanged: totem.rate %s)" % (
    STORE_COINS[1:], CMP_COINS_DEF[1:], TC_COINS_DEF[1:], GROW_M_COINS, GROW_L_COINS, BENCH_COINS_DEF[2:], ["%g" % _r for _r in RATE_DEF]))
''', '''print("0.4.5 Balance P7 coin costs: storage %s, compactor %s, compressor %s, grow %d / %d, bench %s (idle share unchanged: totem.rate %s)" % (
    STORE_COINS[1:], CMP_COINS_DEF[1:], TC_COINS_DEF[1:], GROW_M_COINS, GROW_L_COINS, BENCH_COINS_DEF[2:], ["%g" % _r for _r in RATE_DEF]))
STORE_COINS_047 = list(STORE_COINS)
STORE_COINS = [0] + [_BM48.p7_round(UP_H48[_s - 1] * _BM48.p7_H_at(UP_LV48[_s - 1])) for _s in (6, 8, 9, 10)]   # 0.4.8: Storage II-V = ladder steps 6 / 8 / 9 / 10
assert STORE_COINS == [0, 14500, 105000, 375000, 1260000] and STORE_COINS_047 == [0, 43500, 305000, 1085000, 3880000]
MIG048 = [("lv20.%s" % KKEYS[_k], "20", "0", "n") for _k in range(NK)] + [("totem.upCost", UP_DEF_047, UP_DEF, "t")] + \\
         [("storage.coins.%d" % (_i + 1), "%d" % STORE_COINS_047[_i], "%d" % STORE_COINS[_i], "n") for _i in range(1, 5)]
MIG048_MK = "skyyshards-0.4.8-map"
MIG048_LINE = "# ---------- SkyyShards 0.4.8 (marker %s, runs once): shards come with the starter islands (level 20 grants off), cheaper totem tier-ups and storage on the cheap-first ladder; only untouched old default lines were changed ----------" % MIG048_MK
print("0.4.8 storage coins %s (was %s); one-time update %d lines" % (STORE_COINS[1:], STORE_COINS_047[1:], len(MIG048)))
''')
P.rep('''for _k, _o, _n, _t in MIG045:
    assert ("\\n%s=%s\\n" % (_k, _n)) in "\\n" + CONFIG_TEXT + "\\n", _k            # the new default file holds the new value''',
      '''for _k, _o, _n, _t in MIG045:
    if _k in [_m[0] for _m in MIG048]:   # 0.4.8: storage.coins.* moved on again (ShMig048 runs after ShMig045)
        continue
    assert ("\\n%s=%s\\n" % (_k, _n)) in "\\n" + CONFIG_TEXT + "\\n", _k            # the new default file holds the new value''')

# ================================================================================================ the config text, ShCfg fields, rows, loader
P.rep('''    "# SkyyShards 0.4.6 defaults (marker %s): shards are level 20 rewards - the shard recipes are off - keep this line." % MIG046_MK,''',
      '''    "# SkyyShards 0.4.6 defaults (marker %s): shards are level 20 rewards - the shard recipes are off - keep this line." % MIG046_MK,
    "# shard.lock.<shard> = 0.4.8 SHARD DOORS: the level of shard.lock.skill.<shard> a player needs before that shard's door opens (0 = open).",
    "# Each player's own level counts (class = the class skill, for the Combat Shard).",
] + ["shard.lock.%s=5" % KKEYS[_k] for _k in range(NK)] + ["shard.lock.skill.%s=%s" % (KKEYS[_k], LOCK_SKILL48[_k]) for _k in range(NK)] + [
    "# shard.manualPct = totems work at this percent until the shard's Automation is bought (Skyy: more manual at first);",
    "# shard.manualOfflineSec = before Automation, production counts at most this long between visits (7200 = 2 h).",
    "shard.manualPct=50", "shard.manualOfflineSec=7200",
    "# shard.seedStoreMax = the seeds / saplings one island's store holds; shard.seedReturnPct = percent of a seed a harvested planted crop gives",
    "# back (50 = every crop uses half a seed); shard.itemsPerSapling = logs / fruit per sapling used before Automation.",
    "shard.seedStoreMax=640", "shard.seedReturnPct=50", "shard.itemsPerSapling=20",
    "# up.levels / up.hours = the 0.4.8 shard upgrade ladder (10 steps): coins = hours x 8,333 x the coin curve at that level (cheap first).",
    "up.levels=" + ",".join(str(_x) for _x in UP_LV48), "up.hours=" + ",".join("%g" % _x for _x in UP_H48),
    "# up.auto.step = the ladder step of a shard's Automation (once per shard); up.auto.items.<shard> = its items (Item:qty,...).",
    "up.auto.step=2",
] + ["up.auto.items.%s=%s" % (KKEYS[_k], AUTO_ITEMS48[_k]) for _k in range(NK)] + [
    "# isl.* = 0.4.8 ISLAND UPGRADES: hours of income at the island's tier level (T1 = Lv 1, T2 = Lv 8 ... T15 = Lv 95) for buying the next",
    "# island, each of the 3 sub-upgrades' levels 1-5 per size, and the grows. Materials: raw = the island's item, ench = its Enchanted form,",
    "# seed / eseed = its seeds / Eternal seeds (saplings); a | splits Small | Medium | Large; sub-upgrade items are x the level bought.",
    "isl.buyHours=%g" % BUY_H48,
    "isl.subHours.small=" + ",".join("%g" % _x for _x in SUB_H48[0]), "isl.subHours.medium=" + ",".join("%g" % _x for _x in SUB_H48[1]),
    "isl.subHours.large=" + ",".join("%g" % _x for _x in SUB_H48[2]),
    "isl.growHours.medium=%g" % GROW_H48[0], "isl.growHours.large=%g" % GROW_H48[1],
] + ["isl.buyItems.%s=%s" % (KKEYS[_k], BUY_ITEMS48[_k]) for _k in range(NK)] + [
    "isl.mat.amount=" + MAT48["amount"], "isl.mat.deco=" + MAT48["deco"], "isl.mat.irrigation=" + MAT48["irrigation"], "isl.mat.grow=" + MAT48["grow"],
    "# isl.amount.pct = percent of an island's spots filled at Amount level 0..5 (6 numbers); isl.amount.bonus / isl.deco.pct /",
    "# isl.irrigation.pct = percent more output per level of that sub-upgrade (levels count on across sizes: 5 x (size - 1) + level).",
    "isl.amount.pct=" + ",".join(str(_x) for _x in AMT_PCT48), "isl.amount.bonus=%g" % BONUS48, "isl.deco.pct=%g" % BONUS48, "isl.irrigation.pct=%g" % BONUS48,
    "# isl.deco.props = props each Decorations level places (1-8: a border section of the level's two vanilla props).",
    "isl.deco.props=%d" % DECO_N48,
    "# cave.amount.pct = percent of a Small Mining cave's walls / ceiling that are ore at Ore Amount 0..5 (Medium / Large start at the size below's",
    "# most and climb to the last number).",
    "cave.amount.pct=" + ",".join(str(_x) for _x in CAVE_PCT48),
    "# SkyyShards 0.4.8 defaults (marker %s): shards come with the starter islands, the cheap-first ladder - keep this line." % MIG048_MK,''')
P.rep('''    "# totem.upCost = tier-up costs at the shard's Totem Bench (0.4), I->II .. IV->V, each Enchanted:essence.",''',
      '''    "# totem.upCost = tier-up costs (0.4.7: on the totem's own page), I->II .. IV->V, each Enchanted:essence (0.4.8: cheaper first).",''')
P.rep('''          "public static final double[] CURVE_X = new double[] { %s };" % ", ".join("%r" % b for a, b in CURVE_PTS)):
    F(cfg, f)
''', '''          "public static final double[] CURVE_X = new double[] { %s };" % ", ".join("%r" % b for a, b in CURVE_PTS)):
    F(cfg, f)
# 0.4.8: shard doors + locks, the manual phase, the cost ladder, the island upgrades (arrays swapped whole by the loader)
def _ja48(xs):
    return "new String[] { %s }" % ", ".join(jlit(x if x else "") for x in xs)


for f in ("public static volatile int[] LOCK = new int[] { %s };" % ", ".join("5" for _k in range(NK)),
          "public static volatile String[] LOCK_SKILL = %s;" % _ja48(LOCK_SKILL48), "public static final String[] DEF_LOCK_SKILL = %s;" % _ja48(LOCK_SKILL48),
          "public static volatile int MAN_PCT = 50;", "public static volatile int MAN_OFF_SEC = 7200;", "public static volatile int SEED_MAX = 640;",
          "public static volatile int SEED_RET = 50;", "public static volatile int PER_SAP = 20;",
          "public static volatile int[] UP_LV = new int[] { %s };" % ", ".join(str(_x) for _x in UP_LV48),
          "public static final int[] DEF_UP_LV = new int[] { %s };" % ", ".join(str(_x) for _x in UP_LV48),
          "public static volatile double[] UP_H = new double[] { %s };" % ", ".join(repr(float(_x)) for _x in UP_H48),
          "public static final double[] DEF_UP_H = new double[] { %s };" % ", ".join(repr(float(_x)) for _x in UP_H48),
          "public static volatile int AUTO_STEP = 2;",
          "public static volatile String[] AUTO_ITEMS = %s;" % _ja48(AUTO_ITEMS48), "public static final String[] DEF_AUTO_ITEMS = %s;" % _ja48(AUTO_ITEMS48),
          "public static volatile double BUY_H = %r;" % float(BUY_H48),
          "public static volatile double[] SUB_H = new double[] { %s };" % ", ".join(repr(float(_x)) for _r in SUB_H48 for _x in _r),
          "public static final double[] DEF_SUB_H = new double[] { %s };" % ", ".join(repr(float(_x)) for _r in SUB_H48 for _x in _r),
          "public static volatile double[] GROW_H = new double[] { %s };" % ", ".join(repr(float(_x)) for _x in GROW_H48),
          "public static volatile String[] BUY_ITEMS = %s;" % _ja48(BUY_ITEMS48), "public static final String[] DEF_BUY_ITEMS = %s;" % _ja48(BUY_ITEMS48),
          "public static volatile String MAT_AMT = %s;" % jlit(MAT48["amount"]), "public static volatile String MAT_DECO = %s;" % jlit(MAT48["deco"]),
          "public static volatile String MAT_IRR = %s;" % jlit(MAT48["irrigation"]), "public static volatile String MAT_GROW = %s;" % jlit(MAT48["grow"]),
          "public static volatile int[] AMT_PCT = new int[] { %s };" % ", ".join(str(_x) for _x in AMT_PCT48),
          "public static final int[] DEF_AMT_PCT = new int[] { %s };" % ", ".join(str(_x) for _x in AMT_PCT48),
          "public static volatile double AMT_BONUS = %r;" % BONUS48, "public static volatile double DECO_PCT = %r;" % BONUS48,
          "public static volatile double IRR_PCT = %r;" % BONUS48, "public static volatile int DECO_N = %d;" % DECO_N48,
          "public static volatile int[] CAVE_PCT = new int[] { %s };" % ", ".join(str(_x) for _x in CAVE_PCT48),
          "public static final int[] DEF_CAVE_PCT = new int[] { %s };" % ", ".join(str(_x) for _x in CAVE_PCT48),
          "public static final double COIN_H = %r;" % COIN_H48,
          "public static final int[] BAND = new int[] { %s };" % ", ".join(str(_x) for _x in BAND48)):
    F(cfg, f)
''')
P.rep('''for _r in ROWS:
    assert len(_r[1]) <= 40''', '''# 0.4.8: Server Setup -> Shards -> Shard doors / Island upgrades
CATS = CATS + [("locks", "Shard doors"), ("ladder", "Island upgrades")]
ROWS += [("shard.lock.%s" % KKEYS[_k], "%s door: %s level" % (KINDS[_k], LOCK_SKILL48[_k]), "locks", "int", "5", "0", "100", "", "", "live",
          "The %s level each player needs to open the %s Shard door. 0 = always open." % (LOCK_SKILL48[_k], KINDS[_k]),
          "reload@config.properties:shard.lock.%s" % KKEYS[_k]) for _k in range(NK)]
ROWS += [("shard.lock.skill.%s" % KKEYS[_k], "%s door: skill" % KINDS[_k], "locks", "text", LOCK_SKILL48[_k], "", "40", "", "", "live",
          "The skill whose level opens the %s door (class = the class skill)." % KINDS[_k], "reload@config.properties:shard.lock.skill.%s" % KKEYS[_k])
         for _k in range(NK)]
ROWS += [("shard.manualPct", "Totem speed before Automation", "ladder", "int", "50", "0", "100", "", "%", "live",
          "Totems work at this percent until the shard's Automation is bought (Skyy: manual first).", "reload@config.properties:shard.manualPct"),
         ("shard.manualOfflineSec", "Offline time before Automation", "ladder", "int", "7200", "60", "2592000", "", "s", "live",
          "Before Automation, production counts at most this long between visits (7200 = 2 h).", "reload@config.properties:shard.manualOfflineSec"),
         ("shard.seedStoreMax", "Seed store per island", "ladder", "int", "640", "0", "100000", "", "", "live",
          "Seeds / saplings one island's store holds (the totems replant from it).", "reload@config.properties:shard.seedStoreMax"),
         ("shard.seedReturnPct", "Seed back per planted crop", "ladder", "int", "50", "0", "100", "", "%", "live",
          "Percent of a seed a planted crop gives back (50 = each crop uses half a seed).", "reload@config.properties:shard.seedReturnPct"),
         ("shard.itemsPerSapling", "Items per sapling used", "ladder", "int", "20", "1", "10000", "", "", "live",
          "Before Automation: logs / fruit made per sapling taken from the store.", "reload@config.properties:shard.itemsPerSapling"),
         ("up.levels", "Shard ladder: levels", "ladder", "text", ",".join(str(_x) for _x in UP_LV48), "", "80", "", "", "live",
          "10 levels: each step's coin-curve level (cheap first, harder as you go).", "reload@config.properties:up.levels"),
         ("up.hours", "Shard ladder: hours of income", "ladder", "text", ",".join("%g" % _x for _x in UP_H48), "", "80", "", "", "live",
          "10 numbers: hours of income each step costs (coins = hours x 8,333 x the curve).", "reload@config.properties:up.hours"),
         ("up.auto.step", "Automation: ladder step", "ladder", "int", "2", "1", "10", "", "", "live",
          "The ladder step a shard's Automation costs (once per shard; default 550 coins).", "reload@config.properties:up.auto.step")]
ROWS += [("up.auto.items.%s" % KKEYS[_k], "Automation items: %s" % KINDS[_k], "ladder", "text", AUTO_ITEMS48[_k], "", "200", "", "", "live",
          "Item:qty,Item:qty the %s Shard's Automation costs besides coins." % KINDS[_k], "reload@config.properties:up.auto.items.%s" % KKEYS[_k])
         for _k in range(NK)]
ROWS += [("isl.buyHours", "Buy an island: hours", "ladder", "dec", "%g" % BUY_H48, "0", "100", "", "h", "live",
          "Hours of income at the island's tier level to buy it (T2 Lettuce = 3,500 coins).", "reload@config.properties:isl.buyHours")]
ROWS += [("isl.subHours.%s" % _sn, "%s sub-upgrades: hours" % _sl, "ladder", "text", ",".join("%g" % _x for _x in SUB_H48[_i]), "", "80", "", "", "live",
          "5 numbers: hours of income for levels 1-5 of each %s sub-upgrade." % _sl, "reload@config.properties:isl.subHours.%s" % _sn)
         for _i, (_sn, _sl) in enumerate((("small", "Small"), ("medium", "Medium"), ("large", "Large")))]
ROWS += [("isl.growHours.%s" % _sn, "Grow to %s: hours" % _sl, "ladder", "dec", "%g" % GROW_H48[_i], "0", "100", "", "h", "live",
          "Hours of income at the island's tier level to grow it to %s." % _sl, "reload@config.properties:isl.growHours.%s" % _sn)
         for _i, (_sn, _sl) in enumerate((("medium", "Medium"), ("large", "Large")))]
ROWS += [("isl.buyItems.%s" % KKEYS[_k], "Buy island items: %s" % KINDS[_k], "ladder", "text", BUY_ITEMS48[_k], "", "200", "", "", "live",
          "raw / ench / seed tokens or Item:qty - what a new %s island costs besides coins." % KINDS[_k], "reload@config.properties:isl.buyItems.%s" % KKEYS[_k])
         for _k in range(NK)]
ROWS += [("isl.mat.%s" % _mk, "%s items (S|M|L)" % _ml, "ladder", "text", MAT48[_mk], "", "300", "", "", "live",
          "Small|Medium|Large: raw / ench / seed / eseed tokens or Item:qty%s." % ("" if _mk == "grow" else ", x the level bought"),
          "reload@config.properties:isl.mat.%s" % _mk)
         for _mk, _ml in (("amount", "Amount"), ("deco", "Decorations"), ("irrigation", "Irrigation"), ("grow", "Grow (M|L)"))]
ROWS += [("isl.amount.pct", "Spots filled at Amount 0-5", "ladder", "text", ",".join(str(_x) for _x in AMT_PCT48), "", "60", "", "", "live",
          "6 percents: the share of an island's spots filled at Amount level 0..5.", "reload@config.properties:isl.amount.pct"),
         ("isl.amount.bonus", "Amount: output per level", "ladder", "dec", "%g" % BONUS48, "0", "100", "", "%", "live",
          "Percent more output per Amount level (levels count on across sizes).", "reload@config.properties:isl.amount.bonus"),
         ("isl.deco.pct", "Decorations: output per level", "ladder", "dec", "%g" % BONUS48, "0", "100", "", "%", "live",
          "Happier workers: percent more output per Decorations level (across sizes).", "reload@config.properties:isl.deco.pct"),
         ("isl.irrigation.pct", "Irrigation: output per level", "ladder", "dec", "%g" % BONUS48, "0", "100", "", "%", "live",
          "Faster regrowth: percent more output per Irrigation level (across sizes).", "reload@config.properties:isl.irrigation.pct"),
         ("isl.deco.props", "Decorations: props per level", "ladder", "int", "%d" % DECO_N48, "1", "8", "", "", "live",
          "Vanilla props each Decorations level places on the island's rim (a border section).", "reload@config.properties:isl.deco.props"),
         ("cave.amount.pct", "Cave ore at Ore Amount 0-5", "ladder", "text", ",".join(str(_x) for _x in CAVE_PCT48), "", "60", "", "", "live",
          "6 percents of a Small cave's walls / ceiling that are ore (bigger caves climb on).", "reload@config.properties:cave.amount.pct")]
for _r in ROWS:
    assert len(_r[1]) <= 40''')
P.rep('''_load += ["  MOD_UNL = mun;"]
''', '''_load += ["  MOD_UNL = mun;"]
# 0.4.8: the doors, the manual phase, the ladder, the island upgrades
_load += ["  int[] lk = new int[%d]; String[] lks = new String[%d];" % (NK, NK)]
_load += ["  lk[%d] = intOf(p.getProperty(\\"shard.lock.%s\\"), 5, 0, 100);" % (_k, KKEYS[_k]) for _k in range(NK)]
_load += ["  { String lv = p.getProperty(\\"shard.lock.skill.%s\\"); lks[%d] = (lv == null || lv.trim().length() == 0) ? DEF_LOCK_SKILL[%d] : lv.trim(); }" % (KKEYS[_k], _k, _k) for _k in range(NK)]
_load += ["  LOCK = lk; LOCK_SKILL = lks;",
          "  MAN_PCT = intOf(p.getProperty(\\"shard.manualPct\\"), 50, 0, 100);",
          "  MAN_OFF_SEC = intOf(p.getProperty(\\"shard.manualOfflineSec\\"), 7200, 60, 2592000);",
          "  SEED_MAX = intOf(p.getProperty(\\"shard.seedStoreMax\\"), 640, 0, 100000);",
          "  SEED_RET = intOf(p.getProperty(\\"shard.seedReturnPct\\"), 50, 0, 100);",
          "  PER_SAP = intOf(p.getProperty(\\"shard.itemsPerSapling\\"), 20, 1, 10000);",
          "  UP_LV = intsOf(p.getProperty(\\"up.levels\\"), DEF_UP_LV, 1, 100, \\"up.levels\\");",
          "  UP_H = decsOf(p.getProperty(\\"up.hours\\"), DEF_UP_H, 0.0, 1000.0, \\"up.hours\\");",
          "  AUTO_STEP = intOf(p.getProperty(\\"up.auto.step\\"), 2, 1, 10);",
          "  String[] aui = new String[%d];" % NK]
_load += ["  { String av = p.getProperty(\\"up.auto.items.%s\\"); aui[%d] = av == null ? DEF_AUTO_ITEMS[%d] : av.trim(); }" % (KKEYS[_k], _k, _k) for _k in range(NK)]
_load += ["  AUTO_ITEMS = aui;",
          "  BUY_H = decOf(p.getProperty(\\"isl.buyHours\\"), %r, 0.0, 100.0);" % float(BUY_H48),
          "  double[] sbh = new double[15];",
          "  double[] sb0 = decsOf(p.getProperty(\\"isl.subHours.small\\"), new double[] { %s }, 0.0, 100.0, \\"isl.subHours.small\\");" % ", ".join(repr(float(_x)) for _x in SUB_H48[0]),
          "  double[] sb1 = decsOf(p.getProperty(\\"isl.subHours.medium\\"), new double[] { %s }, 0.0, 100.0, \\"isl.subHours.medium\\");" % ", ".join(repr(float(_x)) for _x in SUB_H48[1]),
          "  double[] sb2 = decsOf(p.getProperty(\\"isl.subHours.large\\"), new double[] { %s }, 0.0, 100.0, \\"isl.subHours.large\\");" % ", ".join(repr(float(_x)) for _x in SUB_H48[2]),
          "  for (int sbi = 0; sbi < 5; sbi++) { sbh[sbi] = sb0[sbi]; sbh[5 + sbi] = sb1[sbi]; sbh[10 + sbi] = sb2[sbi]; }",
          "  SUB_H = sbh;",
          "  double[] grh = new double[2];",
          "  grh[0] = decOf(p.getProperty(\\"isl.growHours.medium\\"), %r, 0.0, 100.0);" % float(GROW_H48[0]),
          "  grh[1] = decOf(p.getProperty(\\"isl.growHours.large\\"), %r, 0.0, 100.0);" % float(GROW_H48[1]),
          "  GROW_H = grh;",
          "  String[] bui = new String[%d];" % NK]
_load += ["  { String bv2 = p.getProperty(\\"isl.buyItems.%s\\"); bui[%d] = bv2 == null ? DEF_BUY_ITEMS[%d] : bv2.trim(); }" % (KKEYS[_k], _k, _k) for _k in range(NK)]
_load += ["  BUY_ITEMS = bui;"]
_load += ["  { String mv = p.getProperty(\\"isl.mat.%s\\"); %s = mv == null ? %s : mv.trim(); }" % (_mk, _fld, jlit(MAT48[_mk]))
          for _mk, _fld in (("amount", "MAT_AMT"), ("deco", "MAT_DECO"), ("irrigation", "MAT_IRR"), ("grow", "MAT_GROW"))]
_load += ["  AMT_PCT = intsOf(p.getProperty(\\"isl.amount.pct\\"), DEF_AMT_PCT, 0, 100, \\"isl.amount.pct\\");",
          "  AMT_BONUS = decOf(p.getProperty(\\"isl.amount.bonus\\"), %r, 0.0, 100.0);" % BONUS48,
          "  DECO_PCT = decOf(p.getProperty(\\"isl.deco.pct\\"), %r, 0.0, 100.0);" % BONUS48,
          "  IRR_PCT = decOf(p.getProperty(\\"isl.irrigation.pct\\"), %r, 0.0, 100.0);" % BONUS48,
          "  DECO_N = intOf(p.getProperty(\\"isl.deco.props\\"), %d, 1, 8);" % DECO_N48,
          "  CAVE_PCT = intsOf(p.getProperty(\\"cave.amount.pct\\"), DEF_CAVE_PCT, 0, 100, \\"cave.amount.pct\\");"]
''')
# the list readers (before loadCfg): exactly n numbers like the default (fewer = the last one repeats; junk = the default + one WARN)
P.rep('''M(cfg, r"""
public static String num(long n) {''', '''M(cfg, r"""
public static int[] intsOf(String v, int[] def, int lo, int hi, String key) {
  int n = def.length;
  int[] d = new int[n];
  for (int i = 0; i < n; i++) d[i] = def[i];
  if (v == null || v.trim().length() == 0) return d;
  try {
    String[] a = v.trim().split(",");
    if (a.length < 1 || a.length > n) throw new IllegalArgumentException("1 to " + n + " numbers");
    int last = 0;
    for (int i = 0; i < n; i++) {
      if (i < a.length) {
        double x = Double.parseDouble(a[i].trim());
        if (Double.isNaN(x)) throw new IllegalArgumentException("not a number");
        int r = (int) Math.round(x);
        last = r < lo ? lo : (r > hi ? hi : r);
      }
      d[i] = last;
    }
    return d;
  } catch (Throwable t) {
    warnOnce("ints:" + key + "=" + v, key + "=" + v + " is not a list of " + n + " numbers - the default is used");
    for (int i = 0; i < n; i++) d[i] = def[i];
    return d;
  }
}""")
M(cfg, r"""
public static double[] decsOf(String v, double[] def, double lo, double hi, String key) {
  int n = def.length;
  double[] d = new double[n];
  for (int i = 0; i < n; i++) d[i] = def[i];
  if (v == null || v.trim().length() == 0) return d;
  try {
    String[] a = v.trim().split(",");
    if (a.length < 1 || a.length > n) throw new IllegalArgumentException("1 to " + n + " numbers");
    double last = 0.0;
    for (int i = 0; i < n; i++) {
      if (i < a.length) {
        double x = Double.parseDouble(a[i].trim());
        if (Double.isNaN(x)) throw new IllegalArgumentException("not a number");
        last = x < lo ? lo : (x > hi ? hi : x);
      }
      d[i] = last;
    }
    return d;
  } catch (Throwable t) {
    warnOnce("decs:" + key + "=" + v, key + "=" + v + " is not a list of " + n + " numbers - the default is used");
    for (int i = 0; i < n; i++) d[i] = def[i];
    return d;
  }
}""")
M(cfg, r"""
public static String num(long n) {''')

# ================================================================================================ ShMig048 = ShMig046's machinery, the 0.4.8 table
_a = P.s.index('''smig46 = mk("ShMig046")''')
_b = P.s.index('''M(cfg, r"""
public static int stacks(int tier) {''', _a)
_P48 = P.s[_a:_b]
for _x, _y in (('smig46 = mk("ShMig046")', 'smig48 = mk("ShMig048")'), ("F(smig46, _d)", "F(smig48, _d)"), ("M(smig46, r", "M(smig48, r"),
               ("jlit(MIG046_MK)", "jlit(MIG048_MK)"), ('"SkyyShards 0.4.6";', '"SkyyShards 0.4.8";'), ("jlit(MIG046_LINE)", "jlit(MIG048_LINE)"),
               ("for m in MIG046)", "for m in MIG048)"),
               ('" kept - the line is doubled or continues on the next line; the 0.4.6 default is empty = off (Server Setup -> Shards -> Crafting)"',
                '" kept - the line is doubled or continues on the next line; the 0.4.8 default is " + NEWV[j] + " (Server Setup -> Shards)"'),
               ('" kept - an admin changed it (the old default was " + OLDV[j] + "; since 0.4.6 shards are level 20 rewards and the default is off)"',
                '" kept - an admin changed it (the old default was " + OLDV[j] + ", the 0.4.8 default is " + NEWV[j] + ")"'),
               ("NOT updated for SkyyShards 0.4.6 (shard recipes off)", "NOT updated for SkyyShards 0.4.8 (starter shards, cheap-first ladder)"),
               ('"before the 0.4.6 shard recipes update (level 20 shards)"', '"before the 0.4.8 update (starter shards, cheap-first ladder)"'),
               ('"config.properties updated for SkyyShards 0.4.6 (shards are level 20 rewards: the 100,000-coin shard recipes are switched off): "',
                '"config.properties updated for SkyyShards 0.4.8 (shards come with the starter islands - level 20 grants off; cheaper totem tier-ups; storage on the cheap-first ladder): "'),
               ("could not update config.properties for SkyyShards 0.4.6 (shard recipes off;", "could not update config.properties for SkyyShards 0.4.8 (starter shards;"),
               ("loadCfg writes the 0.4.6 default with the marker", "loadCfg writes the 0.4.8 default with the marker")):
    assert _P48.count(_x) >= 1, _x
    _P48 = _P48.replace(_x, _y)
assert "smig46" not in _P48 and "MIG046" not in _P48 and "0.4.6" not in _P48, [l for l in _P48.split("\n") if "0.4.6" in l or "MIG046" in l][:5]
P.rep('''M(cfg, r"""
public static int stacks(int tier) {''', '''# ================= 0.4.8 ShMig048 (PROJECT-RULES 4; ShMig046's reviewed machinery copied by tools/shards_0_4_8_patch.py): lv20.<kind> 20 -> 0
# (the level 20 grants off - shards come with the starter islands), totem.upCost and storage.coins.2..5 onto the cheap-first ladder, only
# while a line still holds its old default; setup() runs it right after ShMig046
for _k, _o, _n, _t in MIG048:
    assert ("\\n%s=%s\\n" % (_k, _n)) in "\\n" + CONFIG_TEXT + "\\n", _k            # the new default file holds the new value
    assert _o != _n
assert CONFIG_TEXT.count(MIG048_MK) == 1
''' + _P48 + '''M(cfg, r"""
public static int stacks(int tier) {''')
P.rep('''  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.6 shard recipes update was skipped: " + t); }''',
      '''  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.6 shard recipes update was skipped: " + t); }
  try { @PKG@.ShMig048.run(@PKG@.ShCfg.FILE); }   // 0.4.8: untouched lv20.* 20 -> 0, totem.upCost + storage.coins onto the cheap-first ladder, once (History first; Undo)
  catch (Throwable t) { @PKG@.ShCfg.warn("the 0.4.8 settings update was skipped: " + t); }''')

# ================================================================================================ ShIsl: the ladders, sub-upgrades, costs, manual phase, locks
P.rep('''# ================= 0.4.6 ShLv20: the level 20 shards (Skyy 2026-10-23; tools/shards_0_4_6_patch.py). Part 1 = the class + its texts; the''',
      '''# ================= 0.4.8 ShIsl: ONE ISLAND PER TIER (pure tables + maths; any thread). Types = LAD (build time, tools/tier_tags.py), index t
# across every kind (LAD0[kd] .. LAD0[kd] + LADN[kd] - 1 = T1 .. Tn). Block fields hold ShGeo.IDS indexes (-1 = none).
isl48 = mk("ShIsl")


def _ia48(xs):
    return "new int[] { %s }" % ", ".join(str(int(x)) for x in xs)


def _sa48(xs):
    return "new String[] { %s }" % ", ".join(jlit(x if x else "") for x in xs)


for f in ("public static final int TN = %d;" % len(TY48), "public static final int[] TK = %s;" % _ia48([_k for _k, _t in TY48]),
          "public static final String[] KEY = %s;" % _sa48([_t["key"] for _k, _t in TY48]), "public static final String[] NAME = %s;" % _sa48([_t["name"] for _k, _t in TY48]),
          "public static final int[] TIER = %s;" % _ia48([_t["tier"] for _k, _t in TY48]),
          "public static final String[] PROD = %s;" % _sa48([_t["prod"] for _k, _t in TY48]), "public static final String[] ENCH = %s;" % _sa48([_t["ench"] for _k, _t in TY48]),
          "public static final String[] SMELT = %s;" % _sa48([_t["smelt"] for _k, _t in TY48]), "public static final String[] SMELTE = %s;" % _sa48([_t["smeltEnch"] for _k, _t in TY48]),
          "public static final String[] SEED = %s;" % _sa48([_t["seed"] for _k, _t in TY48]), "public static final String[] ESEED = %s;" % _sa48([_t["eseed"] for _k, _t in TY48]),
          "public static final int[] RES1 = %s;" % _ia48([_xi48(_t["res1"]) for _k, _t in TY48]), "public static final int[] LEAF1 = %s;" % _ia48([_xi48(_t["leaf1"]) for _k, _t in TY48]),
          "public static final int[] RES2 = %s;" % _ia48([_xi48(_t["res2"]) for _k, _t in TY48]), "public static final int[] LEAF2 = %s;" % _ia48([_xi48(_t["leaf2"]) for _k, _t in TY48]),
          "public static final int[] FRUIT = %s;" % _ia48([_xi48(_t["fruit"]) for _k, _t in TY48]), "public static final int[] GROW = %s;" % _ia48([_xi48(_t["grow"]) for _k, _t in TY48]),
          "public static final int[] HOST = %s;" % _ia48([_xi48(_t["host"]) for _k, _t in TY48]),
          "public static final int[] LAD0 = %s;" % _ia48(LAD0), "public static final int[] LADN = %s;" % _ia48([len(_l) for _l in LAD]),
          "public static final String[] STYLE = %s;" % _sa48([_i["style"] for _i in ISL]),
          "public static final int[] HALF = %s;" % _ia48(HALF),
          "public static final int[] FX1 = %s;" % _ia48([_c[0] for _c in FARM48[0]]), "public static final int[] FZ1 = %s;" % _ia48([_c[1] for _c in FARM48[0]]),
          "public static final int[] FX2 = %s;" % _ia48([_c[0] for _c in FARM48[1]]), "public static final int[] FZ2 = %s;" % _ia48([_c[1] for _c in FARM48[1]]),
          "public static final int[] FX3 = %s;" % _ia48([_c[0] for _c in FARM48[2]]), "public static final int[] FZ3 = %s;" % _ia48([_c[1] for _c in FARM48[2]]),
          "public static final int[] TX1 = %s;" % _ia48([_c[0] for _c in TREE48[0]]), "public static final int[] TZ1 = %s;" % _ia48([_c[1] for _c in TREE48[0]]),
          "public static final int[] TX2 = %s;" % _ia48([_c[0] for _c in TREE48[1]]), "public static final int[] TZ2 = %s;" % _ia48([_c[1] for _c in TREE48[1]]),
          "public static final int[] TX3 = %s;" % _ia48([_c[0] for _c in TREE48[2]]), "public static final int[] TZ3 = %s;" % _ia48([_c[1] for _c in TREE48[2]]),
          "public static final String[] SUBK = new String[] { \\"amt\\", \\"deco\\", \\"irr\\" };",
          "public static volatile java.util.function.Function LEVEL_TEST = null;",      # harness: Object[]{UUID, pkey, skill} -> Integer
          "public static final java.util.concurrent.atomic.AtomicLong QUESTS = new java.util.concurrent.atomic.AtomicLong();"):
    F(isl48, f)
M(isl48, "public static String ik(int kd, int slot, String f) { return @PKG@.ShKind.KEYS[kd] + \\".i\\" + slot + \\".\\" + f; }")
M(isl48, "public static String kk(int kd, String f) { return @PKG@.ShKind.KEYS[kd] + \\".\\" + f; }")
M(isl48, r"""
public static int ofKey(int kd, String key) {
  if (key == null || kd < 0 || kd >= LAD0.length) return -1;
  for (int i = LAD0[kd]; i < LAD0[kd] + LADN[kd]; i++) if (KEY[i].equals(key)) return i;
  return -1;
}""")
# the type of island `slot` (an unknown / missing key = the shard's T1 type, as 0.3-0.4.7 read every island)
M(isl48, r"""
public static int ty(int kd, java.util.Properties p, int slot) {
  int t = p == null ? -1 : ofKey(kd, @PKG@.ShStore.str(p, ik(kd, slot, "type")));
  return t < 0 ? LAD0[kd] : t;
}""")
M(isl48, "public static int rank(int t) { return t < 0 || t >= TN ? 0 : t - LAD0[TK[t]]; }")
M(isl48, "public static String tname(int t) { return t < 0 || t >= TN ? \\"\\" : \\"T\\" + TIER[t] + \\" \\" + NAME[t]; }")
M(isl48, r"""
public static boolean auto(int kd, java.util.Properties p) {
  return p != null && "1".equals(@PKG@.ShStore.str(p, kk(kd, "auto")));
}""")
M(isl48, "public static int sizeOf(java.util.Properties p, int kd, int slot) { return @PKG@.ShStore.intv(p, ik(kd, slot, \\"size\\"), 1, 1, 3); }")
M(isl48, r"""
public static int sub(java.util.Properties p, int kd, int slot, int which) {
  if (p == null || which < 0 || which > 2) return 0;
  return @PKG@.ShStore.intv(p, ik(kd, slot, SUBK[which]), 0, 0, 5);
}""")
M(isl48, r"""
public static int lt(int size, int lvl) {
  int s = size < 1 ? 1 : (size > 3 ? 3 : size);
  int l = lvl < 0 ? 0 : (lvl > 5 ? 5 : lvl);
  return 5 * (s - 1) + l;
}""")
# the island's output multiplier: each sub-upgrade's levels count on across the sizes (a grow never makes it worse)
M(isl48, r"""
public static double mult(int kd, java.util.Properties p, int slot, int size) {
  if (p == null) return 1.0;
  double a = 1.0 + @PKG@.ShCfg.AMT_BONUS / 100.0 * (double) lt(size, sub(p, kd, slot, 0));
  double d = 1.0 + @PKG@.ShCfg.DECO_PCT / 100.0 * (double) lt(size, sub(p, kd, slot, 1));
  double i = 1.0 + @PKG@.ShCfg.IRR_PCT / 100.0 * (double) lt(size, sub(p, kd, slot, 2));
  return a * d * i;
}""")
M(isl48, "public static int[] fx(int size) { return size >= 3 ? FX3 : (size == 2 ? FX2 : FX1); }")
M(isl48, "public static int[] fz(int size) { return size >= 3 ? FZ3 : (size == 2 ? FZ2 : FZ1); }")
M(isl48, "public static int[] tx(int size) { return size >= 3 ? TX3 : (size == 2 ? TX2 : TX1); }")
M(isl48, "public static int[] tz(int size) { return size >= 3 ? TZ3 : (size == 2 ? TZ2 : TZ1); }")
M(isl48, r"""
public static int pct(int amt) {
  int[] a = @PKG@.ShCfg.AMT_PCT;
  int i = amt < 0 ? 0 : (amt > 5 ? 5 : amt);
  return i < a.length ? a[i] : 100;
}""")
M(isl48, r"""
public static int farmN(int size, int amt) {
  int n0 = fx(size).length;
  int n = (int) Math.floor((double) n0 * (double) pct(amt) / 100.0 + 0.5);
  return n < 0 ? 0 : (n > n0 ? n0 : n);
}""")
M(isl48, r"""
public static int treeN(int size, int amt) {
  int n0 = tx(size).length;
  int n = (int) Math.ceil((double) n0 * (double) pct(amt) / 100.0 - 0.000001);
  return n < 0 ? 0 : (n > n0 ? n0 : n);
}""")
M(isl48, "public static int eternal(int kd, java.util.Properties p, int slot) { return @PKG@.ShStore.intv(p, ik(kd, slot, \\"eternal\\"), 0, 0, 100000); }")
M(isl48, "public static long seeds(int kd, java.util.Properties p, int slot) { long s = @PKG@.ShStore.lng(p, ik(kd, slot, \\"seed\\"), 0L); return s < 0L ? 0L : s; }")
# the last scan's planted (non-Eternal) farm cells by distance from the centre (bin d = 0..20, d = floor of the distance)
M(isl48, r"""
public static int[] bins(java.util.Properties p, int kd, int slot) {
  int[] b = new int[21];
  String s = p == null ? "" : @PKG@.ShStore.str(p, ik(kd, slot, "pl"));
  if (s.length() == 0) return b;
  String[] a = s.split(",");
  for (int i = 0; i < a.length && i < 21; i++) { try { int v = Integer.parseInt(a[i].trim()); b[i] = v < 0 ? 0 : v; } catch (Throwable t) { b[i] = 0; } }
  return b;
}""")
M(isl48, r"""
public static String binsText(int[] b) {
  StringBuilder sb = new StringBuilder();
  int last = -1;
  for (int i = 0; i < b.length; i++) if (b[i] > 0) last = i;
  for (int i = 0; i <= last; i++) { if (i > 0) sb.append(','); sb.append(b[i]); }
  return sb.toString();
}""")
M(isl48, "public static boolean trees(int kd) { String s = STYLE[kd]; return s.equals(\\"grove\\") || s.equals(\\"orchard\\"); }")
# MANUAL PHASE (spec 7): a worker of range r on island `slot` (size) works at this share. Farming: (Eternal cells + manualPct x planted
# cells inside r) / the tiles inside r (Skyy's start = 8 Eternal / 20 = 0.4; fully planted = (8 + 12 x 0.5) / 20 = 0.7). Foraging /
# Orchard: manualPct x the planted share of the tree spots (last scan; never scanned = the starter half). Others: manualPct.
M(isl48, r"""
public static double mfac(int kd, java.util.Properties p, int slot, int size, int r) {
  double mp = (double) @PKG@.ShCfg.MAN_PCT / 100.0;
  if (p == null) return mp;
  String st = STYLE[kd];
  if (st.equals("farm")) {
    int nf = farmN(size, sub(p, kd, slot, 0));
    int e = eternal(kd, p, slot);
    if (e > nf) e = nf;
    int[] fx = fx(size);
    int[] fz = fz(size);
    long rr = (long) r * (long) r;
    int tiles = 0; int eR = 0; int fR = 0;
    for (int i = 0; i < fx.length; i++) {
      long d2 = (long) fx[i] * (long) fx[i] + (long) fz[i] * (long) fz[i];
      if (d2 > rr) continue;
      tiles++;
      if (i < e) eR++;
      else if (i < nf) fR++;
    }
    if (tiles <= 0) return mp;
    int[] b = bins(p, kd, slot);
    int pR = 0;
    for (int j = 0; j < b.length && j <= r; j++) pR += b[j];
    if (pR > fR) pR = fR;
    return ((double) eR + mp * (double) pR) / (double) tiles;
  }
  if (trees(kd)) {
    int s = treeN(size, sub(p, kd, slot, 0));
    if (s <= 0) return 0.0;
    int tp = @PKG@.ShStore.intv(p, ik(kd, slot, "tp"), -1, -1, 100000);
    if (tp < 0) tp = (s + 1) / 2;
    if (tp > s) tp = s;
    return mp * (double) tp / (double) s;
  }
  return mp;
}""")
# the share of an island's manual output that came from PLANTED cells (they use seeds / saplings; Eternal cells do not)
M(isl48, r"""
public static double plantedShare(int kd, java.util.Properties p, int slot, int size) {
  if (p == null) return 0.0;
  if (trees(kd)) return 1.0;
  if (!STYLE[kd].equals("farm")) return 0.0;
  int nf = farmN(size, sub(p, kd, slot, 0));
  int e = eternal(kd, p, slot);
  if (e > nf) e = nf;
  int[] b = bins(p, kd, slot);
  int pl = 0;
  for (int j = 0; j < b.length; j++) pl += b[j];
  if (pl > nf - e) pl = nf - e;
  double mp = (double) @PKG@.ShCfg.MAN_PCT / 100.0;
  double w = (double) e + mp * (double) pl;
  return w <= 0.0 ? 0.0 : mp * (double) pl / w;
}""")
M(isl48, r"""
public static long offMs(int kd, java.util.Properties p) {
  long a = (long) @PKG@.ShCfg.MAX_OFF_SEC;
  if (auto(kd, p)) return 1000L * a;
  long m = (long) @PKG@.ShCfg.MAN_OFF_SEC;
  return 1000L * (m < a ? m : a);
}""")
# ---- costs (spec 13): coins = round7(hours x 8,333 x curve(level)); the island's level = its tier band (T1 Lv 1, T2 Lv 8 ... T15 Lv 95)
M(isl48, r"""
public static int band(int tier) {
  int[] b = @PKG@.ShCfg.BAND;
  int t = tier < 1 ? 1 : (tier > b.length ? b.length : tier);
  return b[t - 1];
}""")
M(isl48, r"""
public static long coins(double hours, double cv) {
  if (hours <= 0.0 || cv <= 0.0) return 0L;
  double x = hours * @PKG@.ShCfg.COIN_H * cv;
  if (x > 1000000000000.0) x = 1000000000000.0;
  return @PKG@.ShCfg.round7(x);
}""")
M(isl48, r"""
public static double subH(int size, int lvl) {
  double[] a = @PKG@.ShCfg.SUB_H;
  int s = size < 1 ? 1 : (size > 3 ? 3 : size);
  int i = (s - 1) * 5 + (lvl - 1);
  return (lvl < 1 || i < 0 || i >= a.length) ? 0.0 : a[i];
}""")
M(isl48, r"""
public static double growH(int toSize) {
  double[] a = @PKG@.ShCfg.GROW_H;
  return toSize == 2 ? a[0] : (toSize == 3 ? a[1] : 0.0);
}""")
# the shard ladder: step s (1..10) -> { level, hours }
M(isl48, r"""
public static int stepLv(int s) {
  int[] a = @PKG@.ShCfg.UP_LV;
  int i = s < 1 ? 0 : (s > a.length ? a.length - 1 : s - 1);
  return a[i];
}""")
M(isl48, r"""
public static double stepH(int s) {
  double[] a = @PKG@.ShCfg.UP_H;
  int i = s < 1 ? 0 : (s > a.length ? a.length - 1 : s - 1);
  return a[i];
}""")
M(isl48, r"""
public static String tok(int kd, int t, String tk) {
  if (tk.equals("raw")) return PROD[t];
  if (tk.equals("ench")) { String e = ENCH[t]; if (e.length() == 0) e = SMELTE[t]; if (e.length() == 0) e = @PKG@.ShKind.UPG[kd]; return e; }
  if (tk.equals("seed")) return SEED[t];
  if (tk.equals("eseed")) return ESEED[t];
  return tk;
}""")
# a material template "a|b|c": part `part` (Small | Medium | Large; past the end = the last part), every quantity x mul; tokens raw / ench /
# seed / eseed = this island type's items; an empty item (a type without seeds) is dropped; the same item twice is merged.
# -> Object[]{ String[] ids, long[] qty }
M(isl48, r"""
public static Object[] mats(int kd, int t, String tmpl, int part, long mul) {
  String[] parts = tmpl == null ? new String[0] : tmpl.split("\\\\|", -1);
  String s = parts.length == 0 ? "" : parts[part < 0 ? 0 : (part < parts.length ? part : parts.length - 1)];
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList qs = new java.util.ArrayList();
  String[] a = s.split(",");
  for (int i = 0; i < a.length; i++) {
    String x = a[i].trim();
    int c = x.lastIndexOf(':');
    if (c <= 0) continue;
    String id = tok(kd, t, x.substring(0, c).trim());
    long n = 0L;
    try { n = Long.parseLong(x.substring(c + 1).trim()); } catch (Throwable e) { n = 0L; }
    if (id == null || id.length() == 0 || n <= 0L || mul <= 0L) continue;
    n = n * mul;
    int at = ids.indexOf(id);
    if (at >= 0) qs.set(at, Long.valueOf(((Long) qs.get(at)).longValue() + n));
    else { ids.add(id); qs.add(Long.valueOf(n)); }
  }
  String[] oi = new String[ids.size()];
  long[] oq = new long[ids.size()];
  for (int i = 0; i < oi.length; i++) { oi[i] = (String) ids.get(i); oq[i] = ((Long) qs.get(i)).longValue(); }
  return new Object[] { oi, oq };
}""")
# ---- the Mining cave (spec 9.3): chamber (2h-1)^2 x H, ore cells at Ore Amount amt (Small 8 .. 28 %, bigger caves climb on)
M(isl48, "public static int caveH(int size) { return size >= 3 ? 9 : (size == 2 ? 7 : 5); }")
M(isl48, r"""
public static int caveCells(int size) {
  int s = size < 1 ? 1 : (size > 3 ? 3 : size);
  int w = 2 * HALF[s - 1] - 1;
  return w * w + 4 * w * caveH(s);
}""")
M(isl48, r"""
public static int oreN(int size, int amt) {
  int[] a = @PKG@.ShCfg.CAVE_PCT;
  int am = amt < 0 ? 0 : (amt > 5 ? 5 : amt);
  int s = size < 1 ? 1 : (size > 3 ? 3 : size);
  int lo = (int) Math.floor((double) caveCells(1) * (double) a[am] / 100.0 + 0.5);
  if (s == 1) return lo;
  int prev = (int) Math.floor((double) caveCells(1) * (double) a[5] / 100.0 + 0.5);
  for (int z = 2; z <= s; z++) {
    int hi = (int) Math.floor((double) caveCells(z) * (double) a[5] / 100.0 + 0.5);
    if (hi < prev) hi = prev;
    if (z == s) return prev + (hi - prev) * am / 5;
    prev = hi;
  }
  return prev;
}""")
# ---- LOCKS (spec 5): the CLICKING player's own level of shard.lock.skill.<kind> (class = the class skill); -1 = no SkyySkills (no level
# exists: open), fix2 (critic): -2 = SkyySkills is there but the level could not be read (a throw, a bad answer: LOCKED, asked again on the
# next click - "locked until farming lvl 5" must not open by accident); a player with no class yet = class level 0
M(isl48, r"""
public static int level(java.util.UUID u, int kd) {
  boolean have = false;
  try {
    String sk = @PKG@.ShCfg.LOCK_SKILL[kd];
    String pk = @PKG@.ShCfg.pkey(u);
    if (LEVEL_TEST != null) { have = true; Object r = LEVEL_TEST.apply(new Object[] { u, pk, sk }); return r instanceof Number ? ((Number) r).intValue() : -2; }
    java.util.function.Function run = @PKG@.ShCfg.fn("skill:fn:run");
    if (run != null) {
      have = true;
      String nm = sk;
      if ("class".equalsIgnoreCase(sk)) {
        Object c = run.apply(new Object[] { u, "class" });
        if (c == null) return 0;   // no class chosen yet = class level 0
        if (!(c instanceof Object[]) || ((Object[]) c).length < 6 || !(((Object[]) c)[5] instanceof String)) return -2;
        nm = (String) ((Object[]) c)[5];
      }
      Object r = run.apply(new Object[] { pk, nm });
      if (r instanceof Object[] && ((Object[]) r).length > 0 && ((Object[]) r)[0] instanceof Number) return ((Number) ((Object[]) r)[0]).intValue();
      return -2;
    }
    java.util.function.Function lf = @PKG@.ShCfg.fn("skill:fn:level");
    if (lf == null) return -1;
    have = true;
    Object r = lf.apply(new Object[] { u, "class".equalsIgnoreCase(sk) ? "Combat" : sk });
    return r instanceof Number ? ((Number) r).intValue() : -2;
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("locklevel", "reading a skill level for a shard door lock failed (the door stays locked until it reads; logged once): " + t); return have ? -2 : -1; }
}""")
M(isl48, r"""
public static String skillWord(int kd) {
  String sk = @PKG@.ShCfg.LOCK_SKILL[kd];
  return "class".equalsIgnoreCase(sk) ? "class level" : sk;
}""")
# null = open; else the lock card line. No SkyySkills at all (-1) = open (nothing can ever reach the level); fix2 (critic): SkyySkills there but
# the level not readable (-2) = locked with a "try again" line
M(isl48, r"""
public static String lockMsg(java.util.UUID u, int kd) {
  if (u == null || kd < 0 || kd >= @PKG@.ShKind.N) return null;
  int[] a = @PKG@.ShCfg.LOCK;
  int need = kd < a.length ? a[kd] : 0;
  if (need <= 0) return null;
  int lv = level(u, kd);
  if (lv == -1 || lv >= need) return null;
  if (lv < 0) return @PKG@.ShKind.NAMES[kd] + " Shard - locked. Reach " + skillWord(kd) + " " + need + " to open it. Your " + skillWord(kd) + " could not be read right now - try again in a moment.";
  return @PKG@.ShKind.NAMES[kd] + " Shard - locked. Reach " + skillWord(kd) + " " + need + " to open it. You: " + skillWord(kd) + " " + lv + ".";
}""")
M(isl48, r"""
public static void quest(java.util.UUID u, String key) {
  try {
    java.util.function.Function f = @PKG@.ShCfg.fn("quest:fn:event");
    if (f == null || u == null) return;
    f.apply(new Object[] { u, "event", key, Long.valueOf(1L) });
    QUESTS.incrementAndGet();
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("quest", "quest:fn:event failed (logged once): " + t); }
}""")

# ================= 0.4.6 ShLv20: the level 20 shards (Skyy 2026-10-23; tools/shards_0_4_6_patch.py). Part 1 = the class + its texts; the''')

# ================================================================================================ the lazy maths: manual factor, offline cap, seeds, starter
P.rep('''    f.apply(new Object[] { u, "event", key, Long.valueOf(1L) });
    QUESTS.incrementAndGet();
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("quest", "quest:fn:event failed (logged once): " + t); }
}""")
''', '''    f.apply(new Object[] { u, "event", key, Long.valueOf(1L) });
    QUESTS.incrementAndGet();
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("quest", "quest:fn:event failed (logged once): " + t); }
}""")
# MANUAL PHASE seeds (spec 7): `made` items of island `slot` - the planted cells' part uses (1 - shard.seedReturnPct %) of a seed each (trees:
# 1 sapling per shard.itemsPerSapling items); fractions carry over (<kind>.i<n>.sacc). An empty store = the planted part is not made.
# Returns the items kept. The caller holds ShStore.LOCK (ShMath.settle).
M(isl48, r"""
public static long consume(int kd, java.util.Properties p, int slot, long made, double perMul) {
  if (made <= 0L || p == null || auto(kd, p)) return made;
  boolean tr = trees(kd);
  if (!tr && !STYLE[kd].equals("farm")) return made;
  double share = plantedShare(kd, p, slot, sizeOf(p, kd, slot));
  if (share <= 0.0) return made;
  int ps = @PKG@.ShCfg.PER_SAP < 1 ? 1 : @PKG@.ShCfg.PER_SAP;
  double per = tr ? 1.0 / (double) ps : 1.0 - (double) @PKG@.ShCfg.SEED_RET / 100.0;
  if (perMul > 0.0 && perMul < 1.0) per = per * perMul;   // fix (critic): Auto-Replant workers use half the seeds
  if (per <= 0.0) return made;
  double acc = 0.0;
  try { acc = Double.parseDouble(@PKG@.ShStore.str(p, ik(kd, slot, "sacc"))); } catch (Throwable t) { acc = 0.0; }
  if (Double.isNaN(acc) || acc < 0.0 || acc >= 1.0) acc = 0.0;
  long have = seeds(kd, p, slot);
  double fromPl = (double) made * share;
  double need = fromPl * per + acc;
  long use = (long) Math.floor(need + 0.000000001);
  long keep = made;
  if (use > have) {
    double payable = ((double) have - acc) / per;
    if (payable < 0.0) payable = 0.0;
    keep = made - (long) Math.ceil(fromPl - payable - 0.000000001);
    if (keep < 0L) keep = 0L;
    use = have;
    acc = 0.0;
  } else acc = need - (double) use;
  p.setProperty(ik(kd, slot, "seed"), String.valueOf(have - use));
  p.setProperty(ik(kd, slot, "sacc"), String.valueOf(acc));
  return keep;
}""")
M(isl48, "public static long consume(int kd, java.util.Properties p, int slot, long made) { return consume(kd, p, slot, made, 1.0); }")
''')
P.rep('''  for (int i = 0; i < e.length; i++) {
    String[] f = parse(e[i]);
    w += workerRate(kd, f, size, t);
    s += supportPct(kd, f, t);
  }
  if (w <= 0.0) return 0.0;
  return w * (1.0 + s / 100.0) * tcMult(kd, p);''', '''  boolean man = !@PKG@.ShIsl.auto(kd, p);   // 0.4.8: before the shard's Automation a worker works on what is planted now, at shard.manualPct
  for (int i = 0; i < e.length; i++) {
    String[] f = parse(e[i]);
    double wr = workerRate(kd, f, size, t);
    if (man && wr > 0.0) wr = wr * @PKG@.ShIsl.mfac(kd, p, slot, size, range(f, t));
    w += wr;
    s += supportPct(kd, f, t);
  }
  if (w <= 0.0) return 0.0;
  return w * (1.0 + s / 100.0) * tcMult(kd, p) * @PKG@.ShIsl.mult(kd, p, slot, size);   // 0.4.8: x the island's 3 sub-upgrades''')
P.rep('''  long maxOff = 1000L * (long) @PKG@.ShCfg.MAX_OFF_SEC;
  if (now - last > maxOff) last = now - maxOff;''', '''  long maxOff = @PKG@.ShIsl.offMs(kd, p);   // 0.4.8: shard.manualOfflineSec (2 h) until the shard's Automation, then shard.maxOfflineSec
  if (now - last > maxOff) last = now - maxOff;''')
P.rep('''      if (!done) last = now;
    }
    stored += made;''', '''      if (!done) last = now;
    }
    made = @PKG@.ShIsl.consume(kd, p, slot, made, @PKG@.ShTotem.replantMul(kd, p, slot));   // 0.4.8: the planted part uses seeds (manual phase; Auto-Replant halves it)
    stored += made;''')
# fix (critic, spec 7): "Skyy_TotemMod_Replant keeps +10 % and ALSO halves seed use on its totem" - the share of the island's workers
# that carry an Auto-Replant modifier uses half the seeds (1.0 = none, 0.5 = every worker)
P.rep('''M(tot, "public static double supportPct(String[] f, long t) { return supportPct(@PKG@.ShKind.FARM, f, t); }")''', '''M(tot, "public static double supportPct(String[] f, long t) { return supportPct(@PKG@.ShKind.FARM, f, t); }")
M(tot, r"""
public static double replantMul(int kd, java.util.Properties p, int slot) {
  String[] e = entries(kd, p, slot);
  int w = 0; int r = 0;
  for (int i = 0; i < e.length; i++) {
    String[] f = parse(e[i]);
    int ti = idx(f[0]);
    if (ti < 0 || !WORKER[ti] || !accepts(ti, kd)) continue;
    w++;
    if (countMod(f, "replant") > 0) r++;
  }
  return w <= 0 ? 1.0 : 1.0 - 0.5 * (double) r / (double) w;
}""")''')
P.rep('''  p.setProperty(ik(kd, 0, "totems"), @PKG@.ShKind.WORKER[kd] + ":1");
}""")''', '''  p.setProperty(ik(kd, 0, "totems"), @PKG@.ShKind.WORKER[kd] + ":1");
  if (kd == FK) p.setProperty(ik(kd, 0, "eternal"), "8");   // 0.4.8 (Skyy): "it starts with like 8 eternal wheat around the totem, and a bunch of tilled soil"
}""")''')
# ================================================================================================ ShStore: the player-file migration (once per profile)
P.rep('''M(st, "public static void migrate(String k, java.util.Properties p) { }")   # 0.4: the body is set below (after ShTotem)''',
      '''M(st, "public static void migrate(String k, java.util.Properties p) { }")   # 0.4: the body is set below (after ShTotem)
M(st, "public static void migrate2(String k, java.util.Properties p) { }")   # 0.4.8: the body is set below (after ShMath) - the map migration
F(st, "public static final java.util.concurrent.atomic.AtomicLong MAPPED = new java.util.concurrent.atomic.AtomicLong();")''')
P.rep('''  migrate(k, p);   // 0.4: the 9.8 forms migration, once per profile file (marker forms=1)''',
      '''  migrate(k, p);   // 0.4: the 9.8 forms migration, once per profile file (marker forms=1)
  migrate2(k, p);   // 0.4.8: Automation grandfathered, 0.4.6's extra islands -> the next tiers, Mining caves (marker map.done=1)''')
P.rep('''st.getDeclaredMethod("migrate").setBody(jv(r"""{''', '''# 0.4.8: the map migration's History copy: shards/history/map/<pkey>.pre-0.4.8.properties (a different older one = a stamped name), byte-checked
M(st, r"""
public static String snapMap(String k) {
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "-";
    java.nio.file.Path h = DIR.resolve("history").resolve("map");
    java.nio.file.Files.createDirectories(h, new java.nio.file.attribute.FileAttribute[0]);
    byte[] src = java.nio.file.Files.readAllBytes(f);
    String name = k + ".pre-0.4.8.properties";
    java.nio.file.Path t = h.resolve(name);
    if (java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0]) && !java.util.Arrays.equals(src, java.nio.file.Files.readAllBytes(t))) {
      name = k + ".pre-0.4.8." + System.currentTimeMillis() + ".properties";
      t = h.resolve(name);
    }
    if (!java.nio.file.Files.exists(t, new java.nio.file.LinkOption[0])) {
      java.nio.file.Path tmp = h.resolve(name + ".tmp");
      java.nio.file.Files.write(tmp, src, new java.nio.file.OpenOption[0]);
      moveInto(tmp, t);
    }
    if (!java.util.Arrays.equals(src, java.nio.file.Files.readAllBytes(t))) { @PKG@.ShCfg.warnOnce("mapsnap:" + k, "the 0.4.8 map migration copy of " + k + " does not match the file - not migrated"); return null; }
    return "shards/history/map/" + name;
  } catch (Throwable x) {
    @PKG@.ShCfg.warnOnce("mapsnapx:" + k, "the 0.4.8 map migration of " + k + " is waiting: its History copy could not be written (" + x + ")");
    return null;
  }
}""")
st.getDeclaredMethod("migrate").setBody(jv(r"""{''')
P.rep('''# ================= ShGeo: the region layout (spec 9.1), pure maths - every block the region wants =================''',
      '''# ================= 0.4.8 ShStore.migrate2 = THE MAP MIGRATION (spec 15; PROJECT-RULES 4): once per profile file, marker map.done=1, the file
# copied to shards/history/map/ first (byte-checked), then in ONE write: every shard that already has islands is Automated (grandfathered -
# nothing anyone owns gets worse), production settled first; 0.4.6's extra islands of a shard become its next tiers in slot order (what they
# had stored is paid out as the OLD item: <kind>.i<n>.legacy = item:count); old islands get Amount 5 (Mining: Small 2 / Medium 1 / Large 0 =
# never fewer ore nodes). A refused copy / save leaves file + memory untouched (tried again at the next load). Nothing to change = the
# marker rides along with the next save.
st.getDeclaredMethod("migrate2").setBody(jv(r"""{
  String k = $1;
  java.util.Properties p = $2;
  if (p == null || k == null || "1".equals(p.getProperty("map.done"))) return;
  LOCK.lock();
  try {
    if ("1".equals(p.getProperty("map.done"))) return;
    boolean any = false;
    for (int kd = 0; kd < @PKG@.ShKind.N; kd++) if (@PKG@.ShMath.owned(kd, p)) any = true;
    if (!any) { p.setProperty("map.done", "1"); return; }
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    long now = System.currentTimeMillis();
    StringBuilder ch = new StringBuilder();
    for (int kd = 0; kd < @PKG@.ShKind.N; kd++) {
      if (!@PKG@.ShMath.owned(kd, p)) continue;
      String ak = @PKG@.ShIsl.kk(kd, "auto");
      if (!"1".equals(p.getProperty(ak))) { p.setProperty(ak, "1"); ch.append(' ').append(@PKG@.ShKind.KEYS[kd]).append(" automated"); }
      @PKG@.ShMath.settleAll(kd, p, now);
      int nth = 0;
      for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) {
        if (!@PKG@.ShMath.hasIsland(kd, p, s)) continue;
        int want = nth;
        nth++;
        if (want < @PKG@.ShIsl.LADN[kd]) {
          int wt = @PKG@.ShIsl.LAD0[kd] + want;
          int was = @PKG@.ShIsl.ty(kd, p, s);
          if (was != wt) {
            long sto = @PKG@.ShMath.stored(kd, p, s);
            if (sto > 0L) {
              p.setProperty(@PKG@.ShIsl.ik(kd, s, "legacy"), @PKG@.ShIsl.PROD[was] + ":" + sto);
              p.setProperty(@PKG@.ShIsl.ik(kd, s, "stored"), "0");
              p.remove(@PKG@.ShIsl.ik(kd, s, "xpn"));
              p.remove(@PKG@.ShIsl.ik(kd, s, "xpw"));
            }
            p.setProperty(@PKG@.ShIsl.ik(kd, s, "type"), @PKG@.ShIsl.KEY[wt]);
            ch.append(' ').append(@PKG@.ShKind.KEYS[kd]).append(".i").append(s).append(' ').append(@PKG@.ShIsl.KEY[was]).append("->").append(@PKG@.ShIsl.KEY[wt]).append(sto > 0L ? " (" + sto + " " + @PKG@.ShIsl.PROD[was] + " kept as legacy)" : "");
          }
        }
        String amk = @PKG@.ShIsl.ik(kd, s, "amt");
        if (p.getProperty(amk) == null) {
          int sz = @PKG@.ShMath.size(kd, p, s);
          String av = "mine".equals(@PKG@.ShIsl.STYLE[kd]) ? (sz >= 3 ? "0" : (sz == 2 ? "1" : "2")) : "5";
          p.setProperty(amk, av);
          ch.append(' ').append(@PKG@.ShKind.KEYS[kd]).append(".i").append(s).append(" amount ").append(av);
        }
      }
    }
    String snap = snapMap(k);
    if (snap == null) { p.clear(); p.putAll(old); return; }
    p.setProperty("map.done", "1");
    String err = save(k, p);
    if (err != null) { p.clear(); p.putAll(old); @PKG@.ShCfg.warnOnce("mapsave:" + k, "the 0.4.8 map migration of " + k + " is waiting (the file could not be saved: " + err + ")"); return; }
    MAPPED.incrementAndGet();
    log("map migration (SkyyShards @VERSION@) " + k + ":" + ch.toString() + " - History copy " + snap + " - Undo: stop the server, copy it back over shards/" + k + ".properties and put SkyyShards 0.4.7 + SkyyIslands 0.5.24 back");
    @PKG@.ShCfg.info("0.4.8 map migration: " + k + " -" + ch.toString() + " (collect.log has the Undo)");
  } finally { LOCK.unlock(); }
}"""))

# ================= ShGeo: the region layout (spec 9.1), pure maths - every block the region wants =================''')

# ================================================================================================ ShGeo: 16 places, one island per tier, caves, decorations, pools
P.rep('''F(geo, "public static final int RING = %d;" % RING)''', '''F(geo, "public static final int RING = %d;" % RING)
F(geo, "public static final int[] SRC = new int[] { %s };" % ", ".join(str(s) for s in SLOT_SRC))   # 0.4.8: -1 = bridged to the hub, else that inner slot''')
P.rep('''F(geo, 'public static final String[] IDS = new String[] { %s };' % ", ".join([jlit(x) for x in GEO_IDS] + [jlit(x) for x in TOTEM_BLOCK] + [jlit(x) for x in BENCH_BLOCKS]))   # 0.4: + the benches''',
      '''assert len(GEO_IDS) + len(TOTEM_BLOCK) + len(BENCH_BLOCKS) == XBASE, "0.4.8: XBASE"
GEO_ALL48 = GEO_IDS + TOTEM_BLOCK + BENCH_BLOCKS + XIDS
F(geo, 'public static final String[] IDS = new String[] { %s };' % ", ".join(jlit(x) for x in GEO_ALL48))   # 0.4: + the benches; 0.4.8: + the island types' blocks + decorations
F(geo, "public static final int XB = %d;" % XBASE)      # 0.4.8: IDS[XB ..] = the island types' blocks + the decorations (painted like plain blocks; gatherables only on AIR)
F(geo, "public static final boolean[] RESX = new boolean[] { %s };" % ", ".join(
    "true" if (_i in (6, 9, 10, 11, 12, 13, 14) or (_i >= XBASE and GEO_ALL48[_i] in XRES)) else "false" for _i in range(len(GEO_ALL48))))
_DK48 = []
for _k in range(NK):
    for _lv in range(5):
        _pair = DECO48[ISL[_k]["style"]][_lv]
        _DK48 += [_xi48(_pair[0]) if _pair else -1, _xi48(_pair[1]) if _pair else -1]
F(geo, "public static final int[] DECO = new int[] { %s };" % ", ".join(str(x) for x in _DK48))   # 0.4.8: kind x 10 + (level - 1) x 2 + j
F(geo, "public static final int[] DECOALL = new int[] { %s };" % ", ".join(str(_xi48(_id)) for _id in sorted(set(_i2 for _st in DECO48 for _pr in DECO48[_st] for _i2 in _pr))))''')
P.rep('''F(geo, "public static final int OPX = %d;" % OLD_PAD0[0])''', '''F(geo, "public static final int FIX_ORE = -4;")       # 0.4.8 one-time cave fix: clear only while exactly IDS[b[5]] (an old flat Mining island's node)
F(geo, "public static final int DECO_K = -5;")        # 0.4.8: a decoration IDS[b[4]] - placed only on AIR, never replaces anything
F(geo, "public static final int WATER = -6;")         # 0.4.8: an irrigation pool cell (FluidSection water; the floor block there is cleared)
F(geo, "public static final int FARM = -7;")          # 0.4.8 manual farm cell: b[4] slot, b[5] the crop's planted block, b[6] distance bin
F(geo, "public static final int TSPOT = -8;")         # 0.4.8 manual tree spot: b[4] slot, b[5] type, b[6] 1 = the second wood
F(geo, "public static final int TSEED = -9;")         # 0.4.8 the starter half of a manual tree island (planted free, once: <kind>.i<n>.seeded)
F(geo, "public static final int CLRCROP = -10;")      # 0.4.8: clear only a crop (Plant_Crop_ / Plant_Spores_) - a cell that is no farm spot now
F(geo, "public static final int ORECELL = -11;")      # 0.4.8 a cave ore cell: b[4] ore, b[5] host - ore on AIR or on the host rock (Ore Amount grew)
F(geo, "public static final int CLROURS = -12;")      # 0.4.8 a smaller cave's old shell: clear only while IDS[b[4]] (host) or IDS[b[5]] (ore)
F(geo, "public static final int CLRDECO = -13;")      # 0.4.8 a decoration spot no longer used: clear only our decoration ids
F(geo, "public static final int OPX = %d;" % OLD_PAD0[0])''')
P.rep('''M(geo, r"""
public static boolean res(int kind) {
  return kind == CROP || kind == ORE || kind == OTRUNK || kind == OLEAF || kind == ATRUNK || kind == ALEAF || kind == APPLE;
}""")''', '''M(geo, r"""
public static boolean res(int kind) {
  return kind >= 0 && kind < RESX.length && RESX[kind];   // 0.4.8: the 0.3 gatherables + every island type's crops / trunks / leaves / fruit / ore
}""")''')
_I0 = P.s.index('''# the island of `size` around slot `slot` of kind kd (out: x, y, z, kind = index into IDS)
M(geo, r"""
public static void island(java.util.ArrayList out, int kd, int slot, int size) {''')
_I1 = P.s.index('''M(geo, "public static void island(java.util.ArrayList out, int slot, int size) { island(out, FK, slot, size); }")''', _I0)
_OLD_ISLAND = P.s[_I0:_I1]
assert _OLD_ISLAND.count("public static void island(") == 1 and "0.4.7: no brick pillar" in _OLD_ISLAND
P.rep(_OLD_ISLAND, '''# fix (critic, Skyy: "it will replant in its range"): the reach of island `slot`'s worker totems = the biggest range of a worker that works
# in this shard (ShTotem.range: tier + Wider Area + boost), measured from the island centre like ShTotem.workerRate's crops-in-range; 0 = no
# worker = nothing is replanted from the store (the player plants by hand)
M(geo, r"""
public static int reach(int kd, java.util.Properties p, int slot) {
  if (p == null) return 0;
  String[] e = @PKG@.ShTotem.entries(kd, p, slot);
  long t = System.currentTimeMillis();
  int r = 0;
  for (int i = 0; i < e.length; i++) {
    String[] f = @PKG@.ShTotem.parse(e[i]);
    int ti = @PKG@.ShTotem.idx(f[0]);
    if (ti < 0 || !@PKG@.ShTotem.WORKER[ti] || !@PKG@.ShTotem.accepts(ti, kd)) continue;
    int q = @PKG@.ShTotem.range(f, t);
    if (q > r) r = q;
  }
  return r;
}""")
# 0.4.8: a point of the square ring of Chebyshev radius r (perimeter index i, 0 .. 8r - 1, from (-r, -r) clockwise) -> { dx, dz }
M(geo, r"""
public static int[] ringPos(int r, int i) {
  if (r <= 0) return new int[] { 0, 0 };
  int L = 8 * r;
  int k = ((i % L) + L) % L;
  int s = 2 * r;
  if (k < s) return new int[] { -r + k, -r };
  if (k < 2 * s) return new int[] { r, -r + (k - s) };
  if (k < 3 * s) return new int[] { r - (k - 2 * s), r };
  return new int[] { -r, r - (k - 3 * s) };
}""")
M(geo, "public static String ck(int dx, int dz) { return dx + \\",\\" + dz; }")
# 0.4.8 IRRIGATION: one 2 x 2 pool per level (levels count on across sizes: 1-5 on the Small ring, 6-10 on the Medium ring, 11-15 on the
# Large ring - a pool never moves when the island grows); cells "dx,dz" into out (the pool cells sit 3-4 inside each size's rim)
M(geo, r"""
public static void pools(java.util.HashSet out, int levels) {
  for (int m = 0; m < levels && m < 15; m++) {
    int band = m / 5;
    int r = HALF[band] - 3;
    int L = 8 * r;
    int[] q = ringPos(r, (m % 5) * (L / 5) + band);
    int sx = q[0] > 0 ? -1 : 1;
    int sz = q[1] > 0 ? -1 : 1;
    out.add(ck(q[0], q[1])); out.add(ck(q[0] + sx, q[1])); out.add(ck(q[0], q[1] + sz)); out.add(ck(q[0] + sx, q[1] + sz));
  }
}""")
# fix (critic): the walkway of island `slot` - a ring cell within 2 blocks of the line from the centre toward a bridge (to where its bridge
# comes from, and to every island bridged onto it) stays free of props (slot < 0 = no walkway: the harness / a plain picture)
M(geo, r"""
public static boolean gap(int slot, int dx, int dz) {
  if (slot < 0 || slot >= SX.length) return false;
  for (int j = -1; j < SX.length; j++) {
    int vx; int vz;
    if (j < 0) { int s = SRC[slot]; vx = (s < 0 ? 0 : SX[s]) - SX[slot]; vz = (s < 0 ? 0 : SZ[s]) - SZ[slot]; }
    else { if (j == slot || SRC[j] != slot) continue; vx = SX[j] - SX[slot]; vz = SZ[j] - SZ[slot]; }
    double len = Math.sqrt((double) (vx * vx + vz * vz));
    if (len < 1.0) continue;
    if ((double) (dx * vx + dz * vz) <= 0.0) continue;
    double perp = Math.abs((double) (dx * vz - dz * vx)) / len;
    if (perp <= 2.0) return true;
  }
  return false;
}""")
# 0.4.8 DECORATIONS (Skyy: "visual differences per lvl"): level l places isl.deco.props props (default 5: a border section, its two ids
# alternating; fix - critic: 2 single props a level could not be told apart) on the ring just inside that level's size band rim (levels
# 1-5 Small, 6-10 Medium, 11-15 Large: kept when the island grows), each level its own fifth of the ring, never on a walkway (gap);
# cells "dx,dz" -> IDS index into out
M(geo, r"""
public static void decoSpots0(java.util.HashMap out, int kd, int levels, int inset, int slot, int np0) {
  int np = np0 < 1 ? 1 : (np0 > 8 ? 8 : np0);
  for (int m = 0; m < levels && m < 15; m++) {
    int band = m / 5;
    int r = HALF[band] - inset;
    int L = 8 * r;
    int seg = L / 5;
    int step = seg / np < 1 ? 1 : seg / np;
    int base = (m % 5) * seg + band * 3;
    for (int j = 0; j < np; j++) {
      int id = DECO[kd * 10 + (m % 5) * 2 + (j % 2)];
      if (id < 0) continue;
      int at = base + j * step;
      for (int tries = 0; tries < L; tries++) {
        int[] q = ringPos(r, at + tries);
        String key = ck(q[0], q[1]);
        if (out.containsKey(key) || gap(slot, q[0], q[1])) continue;
        out.put(key, Integer.valueOf(id));
        break;
      }
    }
  }
}""")
M(geo, "public static void decoSpots(java.util.HashMap out, int kd, int levels, int inset, int slot) { decoSpots0(out, kd, levels, inset, slot, @PKG@.ShCfg.DECO_N); }")
# the deco spots of the size bands an island no longer uses for decorations (a smaller level count) - cleared of our props only
M(geo, r"""
public static void decoGone(java.util.ArrayList out, int kd, int cx, int y, int cz, int levels, int inset, java.util.HashMap now, int slot) {
  java.util.HashMap all = new java.util.HashMap();
  for (int np = 1; np <= 8; np++) { decoSpots0(all, kd, 15, inset, -1, np); decoSpots0(all, kd, 15, inset, slot, np); }   // every spot any level / prop count could use
  java.util.Iterator it = all.keySet().iterator();
  while (it.hasNext()) {
    String key = (String) it.next();
    if (now.containsKey(key)) continue;
    int c = key.indexOf(',');
    out.add(new int[] { cx + Integer.parseInt(key.substring(0, c)), y, cz + Integer.parseInt(key.substring(c + 1)), CLRDECO });
  }
}""")
# a tree of island type t at (x, z) (alt = the tier's second wood): trunk, leaves, an orchard tree's fruit; a bush type = its fruit block
M(geo, r"""
public static void tree(java.util.ArrayList out, int x, int z, int t, boolean alt) {
  int trunk = alt && @PKG@.ShIsl.RES2[t] >= 0 ? @PKG@.ShIsl.RES2[t] : @PKG@.ShIsl.RES1[t];
  int leaf = alt && @PKG@.ShIsl.LEAF2[t] >= 0 ? @PKG@.ShIsl.LEAF2[t] : @PKG@.ShIsl.LEAF1[t];
  int fruit = @PKG@.ShIsl.FRUIT[t];
  if (trunk < 0) { if (fruit >= 0) add(out, x, Y + 1, z, fruit); return; }
  if (leaf < 0) leaf = trunk;
  boolean grove = STYLE[@PKG@.ShIsl.TK[t]].equals("grove");
  int top = grove ? Y + 3 : Y + 2;
  for (int y = Y + 1; y <= top; y++) add(out, x, y, z, trunk);
  for (int lx = -1; lx <= 1; lx++) for (int lz = -1; lz <= 1; lz++) add(out, x + lx, top + 1, z + lz, leaf);
  add(out, x, top + 2, z, leaf);
  if (grove || fruit < 0) { add(out, x + 1, top, z, leaf); add(out, x - 1, top, z, leaf); add(out, x, top, z + 1, leaf); add(out, x, top, z - 1, leaf); }
  else { add(out, x + 1, top, z + 1, fruit); add(out, x - 1, top, z - 1, fruit); add(out, x + 1, top, z - 1, fruit); add(out, x - 1, top, z + 1, fruit); }
}""")
M(geo, r"""
public static int mix(int a, int b, int c, int d, int e) {
  int h = a * 73856093 ^ b * 19349663 ^ c * 83492791 ^ d * 2654435 ^ e * 40503;
  h = (h ^ (h >>> 13)) * 1274126177;
  return (h ^ (h >>> 16)) & 0x7fffffff;
}""")
# the side of a cave's opening: toward where its bridge comes from (0 = +x, 1 = -x, 2 = +z, 3 = -z)
M(geo, r"""
public static int facing(int slot) {
  int s = slot >= 0 && slot < SRC.length ? SRC[slot] : -1;
  int vx = (s < 0 ? 0 : SX[s]) - SX[slot];
  int vz = (s < 0 ? 0 : SZ[s]) - SZ[slot];
  int ax = vx < 0 ? -vx : vx;
  int az = vz < 0 ? -vz : vz;
  if (ax >= az) return vx >= 0 ? 0 : 1;
  return vz >= 0 ? 2 : 3;
}""")
M(geo, r"""
public static boolean opening(int side, int dx, int dz, int dy, int h) {
  if (dy < 1 || dy > 3) return false;
  if (side == 0) return dx == h && dz >= -1 && dz <= 1;
  if (side == 1) return dx == -h && dz >= -1 && dz <= 1;
  if (side == 2) return dz == h && dx >= -1 && dx <= 1;
  return dz == -h && dx >= -1 && dx <= 1;
}""")
# 0.4.8 THE MINING CAVE (spec 9.3, Skyy: "a cave full of copper with a totem in it ... upgrade how much copper is in the cave, and how big the
# cave is"): a rock island of the ore's host rock - floor, walls and a ceiling around a (2h-1)^2 x H chamber, an opening toward the bridge,
# ore on the hash-ranked share of the walls / ceiling (the same cells every paint: more Ore Amount = a superset), the totem pads on the
# floor, decorations on the floor ring, irrigation pools in the floor; the shells of the smaller sizes are cleared (our blocks only)
M(geo, r"""
public static void cave(java.util.ArrayList out, int kd, int slot, int si, int t, int amt, int ltd, int lti) {
  int h = HALF[si - 1];
  int H = @PKG@.ShIsl.caveH(si);
  int cx = ox(kd) + SX[slot];
  int cz = OZ + SZ[slot];
  int host = @PKG@.ShIsl.HOST[t] >= 0 ? @PKG@.ShIsl.HOST[t] : STONE;
  int ore = @PKG@.ShIsl.RES1[t] >= 0 ? @PKG@.ShIsl.RES1[t] : ORE;
  int side = facing(slot);
  java.util.HashSet water = new java.util.HashSet();
  pools(water, lti);
  for (int z0 = 1; z0 < si; z0++) {   // the smaller sizes' shells (a grow): cleared while they hold our host / ore
    int h0 = HALF[z0 - 1];
    int H0 = @PKG@.ShIsl.caveH(z0);
    for (int dx = -h0; dx <= h0; dx++) for (int dz = -h0; dz <= h0; dz++) {
      int ax = dx < 0 ? -dx : dx;
      int az = dz < 0 ? -dz : dz;
      boolean wall = ax == h0 || az == h0;
      if (wall) for (int y = 1; y <= H0; y++) out.add(new int[] { cx + dx, Y + y, cz + dz, CLROURS, host, ore });
      out.add(new int[] { cx + dx, Y + H0 + 1, cz + dz, CLROURS, host, ore });
    }
  }
  for (int dx = -h; dx <= h; dx++) for (int dz = -h; dz <= h; dz++) {
    int ax = dx < 0 ? -dx : dx;
    int az = dz < 0 ? -dz : dz;
    int x = cx + dx; int z = cz + dz;
    if (water.contains(ck(dx, dz)) && ax < h && az < h) { out.add(new int[] { x, Y, z, WATER }); out.add(new int[] { x, Y + 1, z, CLRCROP }); }
    else add(out, x, Y, z, host);
    add(out, x, Y - 1, z, DIRT);
    if (ax <= h - 2 && az <= h - 2) add(out, x, Y - 2, z, STONE);
    if (ax <= h - 4 && az <= h - 4) add(out, x, Y - 3, z, STONE);
  }
  java.util.ArrayList cand = new java.util.ArrayList();
  for (int dx = -h; dx <= h; dx++) for (int dz = -h; dz <= h; dz++) {
    int ax = dx < 0 ? -dx : dx;
    int az = dz < 0 ? -dz : dz;
    int x = cx + dx; int z = cz + dz;
    if (ax == h || az == h) {
      for (int y = 1; y <= H; y++) {
        if (opening(side, dx, dz, y, h)) { out.add(new int[] { x, Y + y, z, AIR }); continue; }
        if (ax == h && az == h) add(out, x, Y + y, z, host);
        else cand.add(new int[] { x, Y + y, z, dx, y, dz });
      }
      add(out, x, Y + H + 1, z, host);
    } else cand.add(new int[] { x, Y + H + 1, z, dx, H + 1, dz });
  }
  int n = @PKG@.ShIsl.oreN(si, amt);
  long[] keys = new long[cand.size()];
  for (int i = 0; i < keys.length; i++) {
    int[] c = (int[]) cand.get(i);
    keys[i] = ((long) mix(c[3], c[4], c[5], slot, kd) << 20) | (long) i;
  }
  java.util.Arrays.sort(keys);
  boolean[] isOre = new boolean[keys.length];
  for (int i = 0; i < n && i < keys.length; i++) isOre[(int) (keys[i] & 0xFFFFFL)] = true;
  for (int i = 0; i < keys.length; i++) {
    int[] c = (int[]) cand.get(i);
    if (isOre[i]) out.add(new int[] { c[0], c[1], c[2], ORECELL, ore, host });
    else add(out, c[0], c[1], c[2], host);
  }
  java.util.HashMap deco = new java.util.HashMap();
  decoSpots(deco, kd, ltd, 1, slot);
  decoGone(out, kd, cx, Y + 1, cz, ltd, 1, deco, slot);
  java.util.Iterator it = deco.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    String key = (String) en.getKey();
    int c = key.indexOf(',');
    int dx = Integer.parseInt(key.substring(0, c)); int dz = Integer.parseInt(key.substring(c + 1));
    if (water.contains(key)) continue;
    out.add(new int[] { cx + dx, Y + 1, cz + dz, DECO_K, ((Integer) en.getValue()).intValue() });
  }
}""")
# the island of `size` around slot `slot` of kind kd (out: x, y, z, kind = index into IDS or a 0.4.8 cell kind). p = the profile (null = a
# plain Automated T1 island with no upgrades - the 0.4.7 picture). 0.4.8: the island type's own blocks, the Amount share of its spots,
# the manual phase's farm cells / tree spots, decorations, pools; Mining = the cave
M(geo, r"""
public static void island(java.util.ArrayList out, int kd, java.util.Properties p, int slot, int size) {
  int si = size < 1 ? 1 : (size > 3 ? 3 : size);
  int h = HALF[si - 1];
  int cx = ox(kd) + SX[slot];
  int cz = OZ + SZ[slot];
  String st = STYLE[kd];
  int t = @PKG@.ShIsl.ty(kd, p, slot);
  boolean auto = p == null || @PKG@.ShIsl.auto(kd, p);
  int amt = @PKG@.ShIsl.sub(p, kd, slot, 0);
  int ltd = p == null ? 0 : @PKG@.ShIsl.lt(si, @PKG@.ShIsl.sub(p, kd, slot, 1));
  int lti = p == null ? 0 : @PKG@.ShIsl.lt(si, @PKG@.ShIsl.sub(p, kd, slot, 2));
  if (st.equals("mine")) { cave(out, kd, slot, si, t, amt, ltd, lti); return; }
  boolean farm = st.equals("farm");
  boolean arena = st.equals("arena");
  int rch = auto ? 0 : reach(kd, p, slot);   // fix (critic): the store replants only inside the worker totems' range
  java.util.HashSet water = new java.util.HashSet();
  pools(water, lti);
  java.util.HashMap deco = new java.util.HashMap();
  decoSpots(deco, kd, ltd, 1, slot);
  java.util.HashMap cells = new java.util.HashMap();   // farm: "dx,dz" -> its planting order index (Eternal first)
  if (farm) {
    int nf = @PKG@.ShIsl.farmN(si, amt);
    int e = p == null ? nf : @PKG@.ShIsl.eternal(kd, p, slot);
    int[] fx = @PKG@.ShIsl.fx(si);
    int[] fz = @PKG@.ShIsl.fz(si);
    int c = 0;
    for (int i = 0; i < fx.length && c < nf; i++) {
      String key = ck(fx[i], fz[i]);
      if (water.contains(key) || deco.containsKey(key)) continue;
      cells.put(key, Integer.valueOf((auto || c < e) ? -1 : c));
      c++;
    }
  }
  for (int dx = -h; dx <= h; dx++) for (int dz = -h; dz <= h; dz++) {
    int ax = dx < 0 ? -dx : dx;
    int az = dz < 0 ? -dz : dz;
    if (ax == h && az == h) continue;
    boolean rim = ax == h || az == h;
    boolean mid = ax <= 1 && az <= 1;
    int x = cx + dx; int z = cz + dz;
    String key = ck(dx, dz);
    if (rim) add(out, x, Y, z, arena ? MOSSY : GRASS);
    else if (mid) add(out, x, Y, z, BRICK);
    else if (water.contains(key) && !arena) { out.add(new int[] { x, Y, z, WATER }); out.add(new int[] { x, Y + 1, z, CLRCROP }); }
    else if (farm) {
      Object cv = cells.get(key);
      if (cv == null) { add(out, x, Y, z, GRASS); out.add(new int[] { x, Y + 1, z, CLRCROP }); }
      else {
        add(out, x, Y, z, TILL);
        int ci = ((Integer) cv).intValue();
        if (ci < 0) add(out, x, Y + 1, z, @PKG@.ShIsl.RES1[t] >= 0 ? @PKG@.ShIsl.RES1[t] : CROP);
        else if (dx * dx + dz * dz <= rch * rch) {
          int bin = (int) Math.floor(Math.sqrt((double) (dx * dx + dz * dz)));
          out.add(new int[] { x, Y + 1, z, FARM, slot, @PKG@.ShIsl.GROW[t] >= 0 ? @PKG@.ShIsl.GROW[t] : CROP, bin > 20 ? 20 : bin });
        }
      }
    }
    else if (arena) add(out, x, Y, z, BRICK);
    else add(out, x, Y, z, GRASS);
    add(out, x, Y - 1, z, DIRT);
    if (ax <= h - 2 && az <= h - 2) add(out, x, Y - 2, z, STONE);
    if (ax <= h - 4 && az <= h - 4) add(out, x, Y - 3, z, STONE);
  }
  if (st.equals("grove") || st.equals("orchard") || st.equals("ranch")) {
    int[] tx = @PKG@.ShIsl.tx(si);
    int[] tz = @PKG@.ShIsl.tz(si);
    int ns = @PKG@.ShIsl.treeN(si, amt);
    boolean seeded = p == null || "1".equals(@PKG@.ShStore.str(p, @PKG@.ShIsl.ik(kd, slot, "seeded")));
    for (int i = 0; i < tx.length && i < ns; i++) {
      int x = cx + tx[i]; int z = cz + tz[i];
      if (st.equals("ranch")) { add(out, x, Y + 1, z, HAY); continue; }
      if (auto) tree(out, x, z, t, (i % 2) == 1);
      else if (!seeded && (i % 2) == 0) out.add(new int[] { x, Y + 1, z, TSEED, slot, t, i % 2 });   // the free starter half (no sapling used)
      else if (tx[i] * tx[i] + tz[i] * tz[i] <= rch * rch) out.add(new int[] { x, Y + 1, z, TSPOT, slot, t, i % 2 });   // fix: replant only in range
    }
  }
  if (!arena) {
    decoGone(out, kd, cx, Y + 1, cz, ltd, 1, deco, slot);
    java.util.Iterator it = deco.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry en = (java.util.Map.Entry) it.next();
      String key = (String) en.getKey();
      if (water.contains(key)) continue;
      int c = key.indexOf(',');
      int dx = Integer.parseInt(key.substring(0, c)); int dz = Integer.parseInt(key.substring(c + 1));
      int ax = dx < 0 ? -dx : dx;
      int az = dz < 0 ? -dz : dz;
      if (ax >= h || az >= h || (ax <= 1 && az <= 1)) continue;
      out.add(new int[] { cx + dx, Y + 1, cz + dz, DECO_K, ((Integer) en.getValue()).intValue() });
    }
  }
}""")
M(geo, "public static void island(java.util.ArrayList out, int kd, int slot, int size) { island(out, kd, null, slot, size); }")   # 0.4.7's signature = a plain T1 island
''')
# the hub -> inner and inner -> outer bridges (0.4.8: SRC)
P.rep('''M(geo, r"""
public static void bridge(java.util.ArrayList out, int kd, int slot) {
  double dx = (double) SX[slot] / (double) RING;
  double dz = (double) SZ[slot] / (double) RING;
  int ox = ox(kd);
  java.util.HashSet seen = new java.util.HashSet();
  int end = RING - HALF[0];
  for (int s = (HUB - 1) * 2; s <= end * 2; s++) {
    double t = (double) s / 2.0;
    for (int w = -1; w <= 1; w++) {
      int x = (int) Math.round((double) ox + dx * t - dz * (double) w);
      int z = (int) Math.round((double) OZ + dz * t + dx * (double) w);''', '''M(geo, r"""
public static void bridge(java.util.ArrayList out, int kd, int slot) {
  int src = slot >= 0 && slot < SRC.length ? SRC[slot] : -1;   // 0.4.8: an outer island hangs on its inner neighbour
  double ax0 = src < 0 ? 0.0 : (double) SX[src];
  double az0 = src < 0 ? 0.0 : (double) SZ[src];
  double ln = Math.sqrt(((double) SX[slot] - ax0) * ((double) SX[slot] - ax0) + ((double) SZ[slot] - az0) * ((double) SZ[slot] - az0));
  if (ln < 1.0) return;
  double dx = ((double) SX[slot] - ax0) / ln;
  double dz = ((double) SZ[slot] - az0) / ln;
  int ox = ox(kd);
  java.util.HashSet seen = new java.util.HashSet();
  double end = ln - (double) HALF[0];
  int s0 = src < 0 ? (HUB - 1) * 2 : HALF[0] * 2;
  for (int s = s0; s <= (int) Math.floor(end * 2.0); s++) {
    double t = (double) s / 2.0;
    for (int w = -1; w <= 1; w++) {
      int x = (int) Math.round((double) ox + ax0 + dx * t - dz * (double) w);
      int z = (int) Math.round((double) OZ + az0 + dz * t + dx * (double) w);''')
# the one-time fixes: + the old flat Mining island's ore nodes (the cave rebuild, marker <kind>.i<slot>.cave = 1; slot + 100 in the set)
P.rep('''  out.add(new int[] { cx, Y + 2, cz, FIX_BRICK, slot });
  out.add(new int[] { cx + OPX, Y + 1, cz + OPZ, FIX_PAD, slot });
}""")''', '''  out.add(new int[] { cx, Y + 2, cz, FIX_BRICK, slot });
  out.add(new int[] { cx + OPX, Y + 1, cz + OPZ, FIX_PAD, slot });
}""")
# 0.4.8: an old (0.3 - 0.4.7) flat Mining island's ore nodes (every 2 blocks on its floor, y + 1) - cleared once, only while exactly the old
# node block; then the island is a cave (marker <kind>.i<slot>.cave = 1; the entries carry slot + 100)
M(geo, r"""
public static void caveFix(java.util.ArrayList out, int kd, java.util.Properties p, int slot) {
  if (!STYLE[kd].equals("mine") || "1".equals(p.getProperty(@PKG@.ShMath.kk(kd, "i" + slot + ".cave")))) return;
  int si = @PKG@.ShMath.size(kd, p, slot);
  int h = HALF[si - 1];
  int cx = ox(kd) + SX[slot];
  int cz = OZ + SZ[slot];
  for (int dx = -h + 1; dx <= h - 1; dx++) for (int dz = -h + 1; dz <= h - 1; dz++) {
    int ax = dx < 0 ? -dx : dx;
    int az = dz < 0 ? -dz : dz;
    if (((dx + 400) % 2) != 0 || ((dz + 400) % 2) != 0 || (ax <= 2 && az <= 2)) continue;
    out.add(new int[] { cx + dx, Y + 1, cz + dz, FIX_ORE, slot + 100, ORE });
  }
}""")''')
P.rep('''  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) island(out, kd, i, @PKG@.ShMath.size(kd, p, i));
  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) fixes(out, kd, p, i);   // 0.4.7: the one-time centre fix''',
      '''  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) caveFix(out, kd, p, i);   // 0.4.8: the old nodes go first (a cave cell may stand there)
  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) island(out, kd, p, i, @PKG@.ShMath.size(kd, p, i));   // 0.4.8: the profile's island
  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) fixes(out, kd, p, i);   // 0.4.7: the one-time centre fix''')
P.rep('''  for (int i = 0; i < all.size(); i++) { int[] b = (int[]) all.get(i); if (res(b[3])) out.add(b); }''',
      '''  for (int i = 0; i < all.size(); i++) { int[] b = (int[]) all.get(i); if (res(b[3]) || b[3] == FARM || b[3] == TSPOT || b[3] == TSEED || b[3] == ORECELL) out.add(b); }   // 0.4.8: + replanting / cave ore''')

# fix2 (critic): the region paint (Enter, the rescue) completes within 60 s at the latest - a slice the world dropped (it was closing) ends
# in ShHop's "could not be opened - try again" line instead of a silent wait
P.rep('''public static java.util.concurrent.CompletableFuture region(@WLD@ w, java.util.Properties p, int kd) {
  return paintAsync(w, p, kd, false);
}''', '''public static java.util.concurrent.CompletableFuture region(@WLD@ w, java.util.Properties p, int kd) {
  return paintAsync(w, p, kd, false).orTimeout(60L, java.util.concurrent.TimeUnit.SECONDS);   // 0.4.8 fix2
}''')
# ================================================================================================ ShFill: the 0.4.8 cell kinds, the replant scan, water, chunk list
P.rep('''F(fill, "public static volatile java.util.Map TEST_BLOCKS = null;")   # 0.4.7 harness: a block map instead of a world ("x,y,z" -> id)''',
      '''F(fill, "public static volatile java.util.Map TEST_BLOCKS = null;")   # 0.4.7 harness: a block map instead of a world ("x,y,z" -> id)
for _f48 in ("public long[] seedHave;", "public long[] seedUsed;", "public int[] pl;", "public int[] tp;", "public boolean[] scan;",
             "public boolean[] seedMiss;", "public boolean[] seeding;", "public int[] cxs;", "public int[] czs;",
             "public static final java.util.concurrent.atomic.AtomicLong PLANTED = new java.util.concurrent.atomic.AtomicLong();",
             "public static final java.util.concurrent.atomic.AtomicLong SCANS = new java.util.concurrent.atomic.AtomicLong();",
             # fix (critic): the profile whose live seed store the cells take from; the time-sliced paint's state (next entry, blocks set,
             # the centre-fix sets) + how many paints needed more than one slice
             "public String pkey;", "public boolean seedDirty;", "public int pos;", "public int[] cnt;", "public java.util.HashSet miss;", "public java.util.HashSet fxs;",
             "public static final long SLICE_NS = 15000000L;",
             "public static final java.util.concurrent.atomic.AtomicLong SLICED = new java.util.concurrent.atomic.AtomicLong();"):
    F(fill, _f48)   # 0.4.8: the manual phase's replant scan of one paint (per slot; pl = 21 distance bins a slot)''')
_F0 = P.s.index('''# paint: blocks that differ are set; a crop only where the block is AIR (a growing / ripe crop is never reset)
M(fill, r"""
public static int paintX(@WLD@ w, java.util.ArrayList want, java.util.HashSet fixed) {''')
_F1 = P.s.index('''# 0.4.7: paintX = paint + the one-time centre fix entries''', _F0)
P.rep(P.s[_F0:_F1], '''# 0.4.8: the fluid at a cell (0 = none, -1 = not loaded) + an irrigation pool cell (SkyyIslands 0.5.20's pond path: FluidSection.setFluid +
# setTicking; the harness block map stores "f:x,y,z")
M(fill, r"""
public static int fluidAt(@WLD@ w, int x, int y, int z) {
  java.util.Map tb = TEST_BLOCKS;
  if (tb != null) return tb.get("f:" + x + "," + y + "," + z) == null ? 0 : 1;
  try {
    @REF@ r = section(w, x, y, z);
    if (r == null) return -1;
    @FSC@ fs = (@FSC@) w.getChunkStore().getStore().getComponent(r, @FSC@.getComponentType());
    return fs == null ? 0 : fs.getFluidId(x, y, z);
  } catch (Throwable t) { return -1; }
}""")
M(fill, r"""
public static int water(@WLD@ w, int x, int y, int z) {
  java.util.Map tb = TEST_BLOCKS;
  if (tb != null) { tb.remove(x + "," + y + "," + z); tb.put("f:" + x + "," + y + "," + z, "Water_Source"); return 1; }
  try {
    @REF@ r = section(w, x, y, z);
    if (r == null) return 0;
    @ST@ cs = w.getChunkStore().getStore();
    @FSC@ fs = (@FSC@) cs.getComponent(r, @FSC@.getComponentType());
    if (fs == null) return 0;
    int id = @FLU@.getAssetMap().getIndexOrDefault("Water_Source", -1);
    if (id < 0) return 0;
    @FLU@ f = (@FLU@) @FLU@.getAssetMap().getAsset(id);
    if (f == null) return 0;
    fs.setFluid(x, y, z, f, (byte) f.getMaxFluidLevel());
    @BSEC@ bs = (@BSEC@) cs.getComponent(r, @BSEC@.getComponentType());
    if (bs != null) bs.setTicking(x, y, z, true);
    return 1;
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("water", "an irrigation pool's water could not be placed (logged once): " + t); return 0; }
}""")
# 0.4.8: the replant scan's bookkeeping (this paint's job; null = no scan). fix (critic): every seed is taken from the LIVE store under
# ShStore.LOCK at the moment its cell is planted (never from a snapshot) - a Take seeds while the paint runs can never get the same seeds
# twice; a cell that could not be set gives its seed back the same way. scanDone saves the store.
M(fill, r"""
public boolean seed(int s) {
  if (this.seedUsed == null || this.scan == null || s < 0 || s >= this.seedUsed.length || !this.scan[s] || this.pkey == null) return false;
  boolean ok = false;
  @PKG@.ShStore.LOCK.lock(); try {
    java.util.Properties p = @PKG@.ShStore.get(this.pkey);
    if (p != null && !@PKG@.ShIsl.auto(this.kind, p) && @PKG@.ShMath.hasIsland(this.kind, p, s)) {
      long have = @PKG@.ShIsl.seeds(this.kind, p, s);
      if (have > 0L) {
        p.setProperty(@PKG@.ShIsl.ik(this.kind, s, "seed"), String.valueOf(have - 1L));
        this.seedUsed[s] = this.seedUsed[s] + 1L;
        this.seedDirty = true;   // fix2 (critic): saved after this slice (saveSeeds), not only at the end of the whole paint
        ok = true;
      }
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  return ok;
}""")
M(fill, r"""
public void unseed(int s) {
  if (this.seedUsed == null || s < 0 || s >= this.seedUsed.length || this.seedUsed[s] <= 0L || this.pkey == null) return;
  @PKG@.ShStore.LOCK.lock(); try {
    java.util.Properties p = @PKG@.ShStore.get(this.pkey);
    if (p != null) {
      p.setProperty(@PKG@.ShIsl.ik(this.kind, s, "seed"), String.valueOf(@PKG@.ShIsl.seeds(this.kind, p, s) + 1L));
      this.seedUsed[s] = this.seedUsed[s] - 1L;
      this.seedDirty = true;
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")
# fix2 (critic): the store is saved after every slice that took seeds - a crash / stop between two slices can never leave the planted cells
# (saved with the chunks) AND the seeds still in the shard file. 1 = saved, 0 = nothing to save, -1 = the save failed (tried again next slice)
M(fill, r"""
public int saveSeeds() {
  if (!this.seedDirty || this.pkey == null) return 0;
  int r = 1;
  @PKG@.ShStore.LOCK.lock(); try {
    java.util.Properties p = @PKG@.ShStore.get(this.pkey);
    if (p == null) r = 0;
    else {
      String e = @PKG@.ShStore.save(this.pkey, p);
      if (e != null) { r = -1; @PKG@.ShCfg.warnOnce("seedsave:" + this.pkey, "the seed store of " + this.pkey + " could not be saved between two paint slices (" + e + ") - saved again after the next one"); }
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (r >= 0) this.seedDirty = false;
  return r;
}""")
M(fill, r"""
public void planted(int s, int bin) {
  if (this.pl == null || s < 0 || s * 21 + 20 >= this.pl.length) return;
  int k = bin < 0 ? 0 : (bin > 20 ? 20 : bin);
  this.pl[s * 21 + k] = this.pl[s * 21 + k] + 1;
}""")
M(fill, "public void tree(int s) { if (this.tp != null && s >= 0 && s < this.tp.length) this.tp[s] = this.tp[s] + 1; }")
M(fill, "public void smiss(int s) { if (this.seedMiss != null && s >= 0 && s < this.seedMiss.length) this.seedMiss[s] = true; }")
# 0.4.8: one cell of a 0.4.8 kind (b[3] < 0, not a fix entry): decorations / pools / crop clears / cave ore + shells / the manual phase's
# farm cells and tree spots (replanted from the island's seed store, 1 seed a cell; every planted one counted)
M(fill, r"""
public static int cell(@WLD@ w, int[] b, @PKG@.ShFill job) {
  int kq = b[3];
  if (kq == @PKG@.ShGeo.WATER) {
    int f = fluidAt(w, b[0], b[1], b[2]);
    if (f != 0) return 0;
    String c0 = idAt(w, b[0], b[1], b[2]);
    if (c0 == null) return 0;
    int m = 0;
    if (c0.length() > 0) m += clear(w, b[0], b[1], b[2]);
    return m + water(w, b[0], b[1], b[2]);
  }
  String cur = idAt(w, b[0], b[1], b[2]);
  if (cur == null) { if (kq == @PKG@.ShGeo.TSEED && job != null) job.smiss(b[4]); return 0; }
  if (kq == @PKG@.ShGeo.DECO_K) return cur.length() == 0 ? put(w, b[0], b[1], b[2], @PKG@.ShGeo.IDS[b[4]]) : 0;
  if (kq == @PKG@.ShGeo.CLRCROP) return (cur.indexOf("Plant_Crop_") >= 0 || cur.indexOf("Plant_Spores_") >= 0) ? clear(w, b[0], b[1], b[2]) : 0;
  if (kq == @PKG@.ShGeo.CLROURS) return (cur.length() > 0 && (cur.equals(@PKG@.ShGeo.IDS[b[4]]) || cur.equals(@PKG@.ShGeo.IDS[b[5]]))) ? clear(w, b[0], b[1], b[2]) : 0;
  if (kq == @PKG@.ShGeo.CLRDECO) {
    if (cur.length() == 0) return 0;
    int[] d = @PKG@.ShGeo.DECOALL;
    for (int i = 0; i < d.length; i++) if (cur.equals(@PKG@.ShGeo.IDS[d[i]])) return clear(w, b[0], b[1], b[2]);
    return 0;
  }
  if (kq == @PKG@.ShGeo.ORECELL) return (cur.length() == 0 || cur.equals(@PKG@.ShGeo.IDS[b[5]])) ? put(w, b[0], b[1], b[2], @PKG@.ShGeo.IDS[b[4]]) : 0;
  if (kq == @PKG@.ShGeo.FARM) {
    int s = b[4];
    if (cur.length() > 0) {
      if (job != null && (cur.indexOf("Plant_Crop_") >= 0 || cur.indexOf("Plant_Spores_") >= 0)) job.planted(s, b[6]);
      return 0;
    }
    if (job == null || !job.seed(s)) return 0;
    int m = put(w, b[0], b[1], b[2], @PKG@.ShGeo.IDS[b[5]]);
    if (m > 0) { job.planted(s, b[6]); PLANTED.incrementAndGet(); } else job.unseed(s);
    return m;
  }
  if (kq == @PKG@.ShGeo.TSPOT || kq == @PKG@.ShGeo.TSEED) {
    int s = b[4];
    if (cur.length() > 0) { if (job != null) job.tree(s); return 0; }
    boolean free = kq == @PKG@.ShGeo.TSEED;
    if (!free && (job == null || !job.seed(s))) return 0;
    java.util.ArrayList tc = new java.util.ArrayList();
    @PKG@.ShGeo.tree(tc, b[0], b[2], b[5], b.length > 6 && b[6] == 1);
    int m = 0;
    for (int j = 0; j < tc.size(); j++) {
      int[] c = (int[]) tc.get(j);
      String cc = idAt(w, c[0], c[1], c[2]);
      if (cc != null && cc.length() == 0) m += put(w, c[0], c[1], c[2], @PKG@.ShGeo.IDS[c[3]]);
    }
    if (job != null) { if (m > 0) { job.tree(s); PLANTED.incrementAndGet(); } else if (!free) job.unseed(s); }
    return m;
  }
  return 0;
}""")
# paint: blocks that differ are set; a crop only where the block is AIR (a growing / ripe crop is never reset). 0.4.8: + the cell kinds,
# + the old Mining nodes' fix (FIX_ORE), the island types' blocks (IDS[XB ..]: a plain compare; gatherables only on AIR)
M(fill, r"""
public static int paintZ(@WLD@ w, java.util.ArrayList want, java.util.HashSet fixed, @PKG@.ShFill job, java.util.HashSet miss, int from, long until, int[] cnt) {
  int n = 0;
  int i = from;
  while (i < want.size()) {
    if (until > 0L && i > from && ((i - from) & 15) == 0 && System.nanoTime() > until) break;   // fix (critic): at most ~15 ms a slice
    i++;
    int[] b = (int[]) want.get(i - 1);
    int kq = b[3];
    if (kq == @PKG@.ShGeo.FIX_BRICK || kq == @PKG@.ShGeo.FIX_PAD || kq == @PKG@.ShGeo.FIX_ORE) {
      Integer sl = Integer.valueOf(b.length > 4 ? b[4] : -1);
      String cur0 = idAt(w, b[0], b[1], b[2]);
      if (cur0 == null) { miss.add(sl); continue; }
      boolean ours = kq == @PKG@.ShGeo.FIX_BRICK ? cur0.equals(@PKG@.ShGeo.IDS[@PKG@.ShGeo.BRICK])
          : (kq == @PKG@.ShGeo.FIX_PAD ? cur0.indexOf("Skyy_TotemBlock_") >= 0 : (b.length > 5 && cur0.length() > 0 && cur0.equals(@PKG@.ShGeo.IDS[b[5]])));
      if (ours) { if (clear(w, b[0], b[1], b[2]) == 0) { miss.add(sl); continue; } n++; }
      if (fixed != null) fixed.add(sl);
      continue;
    }
    if (kq < 0) { n += cell(w, b, job); continue; }
    String id = @PKG@.ShGeo.IDS[kq];
    String cur = idAt(w, b[0], b[1], b[2]);
    if (cur == null) continue;
    if (@PKG@.ShGeo.res(kq)) { if (cur.length() == 0) n += put(w, b[0], b[1], b[2], id); continue; }   // 0.3: every gatherable block, only on AIR
    boolean stand = false;
    for (int s = 0; s < @PKG@.ShGeo.STANDS.length; s++) if (kq == @PKG@.ShGeo.STANDS[s]) stand = true;
    if (stand) { if (cur.indexOf(id) < 0) n += put(w, b[0], b[1], b[2], id); continue; }
    if (kq == @PKG@.ShGeo.AIR) { if (cur.length() > 0) n += clear(w, b[0], b[1], b[2]); continue; }   // 0.2: an empty totem pad (0.4.8: + a cave's opening)
    if (kq >= @PKG@.ShGeo.TOTEM && kq < @PKG@.ShGeo.XB) { if (cur.indexOf(id) < 0) n += put(w, b[0], b[1], b[2], id); continue; }   // 0.2: a totem (any rotation state); 0.4: a Totem Bench too
    if (kq == @PKG@.ShGeo.TILL && cur.indexOf(id) >= 0) continue;   // 0.4: watered / fertilized tilled soil (a state of it) is kept
    if (!id.equals(cur)) n += put(w, b[0], b[1], b[2], id);
  }
  cnt[0] = cnt[0] + n;
  return i;
}""")
# the whole paint in one go (0.4.7's shape; the harness + paintX)
M(fill, r"""
public static int paintY(@WLD@ w, java.util.ArrayList want, java.util.HashSet fixed, @PKG@.ShFill job) {
  java.util.HashSet miss = new java.util.HashSet();
  int[] c = new int[1];
  paintZ(w, want, fixed, job, miss, 0, 0L, c);
  if (fixed != null) fixed.removeAll(miss);
  return c[0];
}""")
M(fill, "public static int paintX(@WLD@ w, java.util.ArrayList want, java.util.HashSet fixed) { return paintY(w, want, fixed, null); }")   # 0.4.7's signature
''')
P.rep('''  if (fixed == null || fixed.size() == 0 || wn == null || !wn.startsWith("skyy-shard-") || wn.length() <= 11) return 0;
  String k = wn.substring(11);
  int n = 0;
  String done = "";''', '''  if (fixed == null || fixed.size() == 0 || wn == null || !wn.startsWith("skyy-shard-") || wn.length() <= 11) return 0;
  String k = wn.substring(11);
  int n = 0;
  String done = "";
  String caves = "";   // 0.4.8: slot + 100 = the cave rebuild of that island''')
P.rep('''      int s = ((Integer) it.next()).intValue();
      if (s < 0 || !@PKG@.ShMath.hasIsland(kd, p, s)) continue;
      String key = @PKG@.ShMath.kk(kd, "i" + s + ".centre");
      if ("1".equals(p.getProperty(key))) continue;
      p.setProperty(key, "1");
      done = done + " " + (s + 1);
      n++;''', '''      int s = ((Integer) it.next()).intValue();
      if (s >= 100) {   // 0.4.8: the old flat Mining island's nodes are cleared - it is a cave now
        int cs = s - 100;
        if (!@PKG@.ShMath.hasIsland(kd, p, cs)) continue;
        String ckey = @PKG@.ShMath.kk(kd, "i" + cs + ".cave");
        if ("1".equals(p.getProperty(ckey))) continue;
        p.setProperty(ckey, "1");
        caves = caves + " " + (cs + 1);
        n++;
        continue;
      }
      if (s < 0 || !@PKG@.ShMath.hasIsland(kd, p, s)) continue;
      String key = @PKG@.ShMath.kk(kd, "i" + s + ".centre");
      if ("1".equals(p.getProperty(key))) continue;
      p.setProperty(key, "1");
      done = done + " " + (s + 1);
      n++;''')
P.rep('''      else @PKG@.ShStore.log("centre " + k + " " + @PKG@.ShKind.KEYS[kd] + " island(s)" + done + ": the old brick pillar is gone, pad 1 is the centre (0.4.7, once)");''',
      '''      else {
        if (done.length() > 0) @PKG@.ShStore.log("centre " + k + " " + @PKG@.ShKind.KEYS[kd] + " island(s)" + done + ": the old brick pillar is gone, pad 1 is the centre (0.4.7, once)");
        if (caves.length() > 0) @PKG@.ShStore.log("cave " + k + " " + @PKG@.ShKind.KEYS[kd] + " island(s)" + caves + ": the old flat ore nodes are cleared - the island is a copper cave now (0.4.8, once)");
      }''')
# the scan's result (world thread, after the paint): planted cells / trees, the seeds used, the starter half planted - saved only when it changed
P.rep('''M(fill, r"""
public void run() {
  int n = 0;
  try {
    java.util.HashSet fx = this.cropsOnly ? null : new java.util.HashSet();
    n = paintX(this.world, this.want, fx);
    if (fx != null && fx.size() > 0) markFixed(this.world.getName(), this.kind, fx);   // 0.4.7
    if (n > 0 && !this.cropsOnly) {
      for (int i = 0; i < @PKG@.ShGeo.CX.length; i++) {
        int cx = @PKG@.ShGeo.chunkX(this.kind, i);
        long idx = @CHU@.indexChunk(cx, @PKG@.ShGeo.CZ[i]);
        tint(this.world, idx);
        try { this.world.getChunkLighting().invalidateLightInChunkSections(this.world.getChunkStore(), cx, @PKG@.ShGeo.CZ[i], 0, 10); } catch (Throwable t2) { }
      }
    }''', '''M(fill, r"""
public void prep(java.util.Properties p) {
  int n = @PKG@.ShMath.SLOTS;
  this.seedHave = new long[n]; this.seedUsed = new long[n]; this.pl = new int[n * 21]; this.tp = new int[n];
  this.scan = new boolean[n]; this.seedMiss = new boolean[n]; this.seeding = new boolean[n];
  this.pkey = p == null ? null : p.getProperty("pkey");   // fix (critic): seed() takes from this profile's live store
  if (p == null || @PKG@.ShIsl.auto(this.kind, p)) return;
  boolean tr = @PKG@.ShIsl.trees(this.kind);
  if (!tr && !"farm".equals(@PKG@.ShIsl.STYLE[this.kind])) return;
  for (int s = 0; s < n; s++) {
    if (!@PKG@.ShMath.hasIsland(this.kind, p, s)) continue;
    this.scan[s] = true;
    this.seedHave[s] = @PKG@.ShIsl.seeds(this.kind, p, s);
    this.seeding[s] = tr && !"1".equals(@PKG@.ShStore.str(p, @PKG@.ShIsl.ik(this.kind, s, "seeded")));
  }
}""")
M(fill, r"""
public int scanDone() {
  if (this.scan == null || this.world == null) return 0;
  String wn = this.world.getName();
  if (wn == null || !wn.startsWith("skyy-shard-") || wn.length() <= 11) return 0;
  String k = wn.substring(11);
  int kd = this.kind;
  int ch = 0;
  @PKG@.ShStore.LOCK.lock(); try {
    java.util.Properties p = @PKG@.ShStore.get(k);
    if (p == null) return 0;
    for (int s = 0; s < this.scan.length; s++) {
      if (!this.scan[s] || !@PKG@.ShMath.hasIsland(kd, p, s)) continue;
      if (@PKG@.ShIsl.trees(kd)) {
        String v = String.valueOf(this.tp[s]);
        if (!v.equals(@PKG@.ShStore.str(p, @PKG@.ShIsl.ik(kd, s, "tp")))) { p.setProperty(@PKG@.ShIsl.ik(kd, s, "tp"), v); ch++; }
      } else {
        int[] b = new int[21];
        for (int j = 0; j < 21; j++) b[j] = this.pl[s * 21 + j];
        String v = @PKG@.ShIsl.binsText(b);
        if (!v.equals(@PKG@.ShStore.str(p, @PKG@.ShIsl.ik(kd, s, "pl")))) { p.setProperty(@PKG@.ShIsl.ik(kd, s, "pl"), v); ch++; }
      }
      if (this.seedUsed[s] > 0L) ch++;   // fix (critic): the seeds already left the live store cell by cell (seed()) - only saved here
      if (this.seeding[s] && !this.seedMiss[s] && !"1".equals(@PKG@.ShStore.str(p, @PKG@.ShIsl.ik(kd, s, "seeded")))) { p.setProperty(@PKG@.ShIsl.ik(kd, s, "seeded"), "1"); ch++; }
    }
    if (ch > 0) {
      String e = @PKG@.ShStore.save(k, p);
      if (e != null) @PKG@.ShCfg.warnOnce("scan:" + k, "the replant scan of " + k + " could not be saved (" + e + ") - it is counted again on the next regrow");
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  SCANS.incrementAndGet();
  return ch;
}""")
M(fill, r"""
public void run() {
  int n = 0;
  try {
    if (this.cnt == null) { this.cnt = new int[1]; this.miss = new java.util.HashSet(); this.fxs = this.cropsOnly ? null : new java.util.HashSet(); this.pos = 0; }
    // fix (critic): time-sliced - at most SLICE_NS of painting a world tick, the rest on the next one (16 islands + caves + decorations)
    this.pos = paintZ(this.world, this.want, this.fxs, this, this.miss, this.pos, System.nanoTime() + SLICE_NS, this.cnt);   // 0.4.8: + the replant scan
    boolean whole = this.want == null || this.pos >= this.want.size();
    if (!whole) {
      if (this.placed != -2) { SLICED.incrementAndGet(); this.placed = -2; }   // -2 = between slices
      try { saveSeeds(); } catch (Throwable t0) { @PKG@.ShCfg.warnOnce("seedsave", "saving the seed store between two paint slices failed (logged once): " + t0); }   // fix2 (critic)
      if (!this.world.isAlive()) @PKG@.ShCfg.warn("shard fill: " + this.world.getName() + " closed between two paint slices - the rest is painted next time");   // fix2 (critic): never queue into a closing world
      else {
        try { this.world.execute(this); return; }
        catch (Throwable t1) { @PKG@.ShCfg.warn("shard fill: the next slice in " + this.world.getName() + " could not be queued (" + t1 + ") - the rest is painted next time"); }
      }
    }
    n = this.cnt[0];
    java.util.HashSet fx = this.fxs;
    if (fx != null) fx.removeAll(this.miss);
    if (whole && fx != null && fx.size() > 0) markFixed(this.world.getName(), this.kind, fx);   // 0.4.7 (only after the whole region)
    if (n > 0 && !this.cropsOnly) {
      int[] xs = this.cxs;
      int[] zs = this.czs;
      int m = xs == null ? @PKG@.ShGeo.CX.length : xs.length;
      for (int i = 0; i < m; i++) {
        int cx = xs == null ? @PKG@.ShGeo.chunkX(this.kind, i) : xs[i];
        int cz = zs == null ? @PKG@.ShGeo.CZ[i] : zs[i];
        long idx = @CHU@.indexChunk(cx, cz);
        tint(this.world, idx);
        try { this.world.getChunkLighting().invalidateLightInChunkSections(this.world.getChunkStore(), cx, cz, 0, 10); } catch (Throwable t2) { }
      }
    }''')
P.rep('''    RUNS.incrementAndGet();
  } catch (Throwable t) { @PKG@.ShCfg.warn("shard region fill failed in " + this.world.getName() + ": " + t); }
  this.placed = n;
  this.done.complete(this.world);''', '''    RUNS.incrementAndGet();
  } catch (Throwable t) { @PKG@.ShCfg.warn("shard region fill failed in " + this.world.getName() + ": " + t); }
  try { scanDone(); } catch (Throwable t3) { @PKG@.ShCfg.warn("shard replant scan failed in " + this.world.getName() + ": " + t3); }   // 0.4.8 (fix: after the last slice, also after a failed paint)
  this.placed = n;
  this.done.complete(this.world);''')
P.rep('''    java.util.ArrayList want;
    @PKG@.ShStore.LOCK.lock(); try { want = cropsOnly ? @PKG@.ShGeo.crops(p, kd) : @PKG@.ShGeo.region(p, kd); } finally { @PKG@.ShStore.LOCK.unlock(); }
    @CST@ cs = w.getChunkStore();
    int n = @PKG@.ShGeo.CX.length;
    java.util.concurrent.CompletableFuture[] parts = new java.util.concurrent.CompletableFuture[n * 2];
    for (int i = 0; i < n; i++) {
      int cx = @PKG@.ShGeo.chunkX(kd, i);
      parts[2 * i] = cs.getChunkReferenceAsync(@CHU@.indexChunk(cx, @PKG@.ShGeo.CZ[i]));
      parts[2 * i + 1] = cs.getChunkSectionReferenceAsync(cx, 3, @PKG@.ShGeo.CZ[i]);
    }
    @PKG@.ShFill job = new @PKG@.ShFill(w, want, done);
    job.cropsOnly = cropsOnly;
    job.kind = kd;
    java.util.concurrent.CompletableFuture.allOf(parts).whenComplete(job);''', '''    java.util.ArrayList want;
    @PKG@.ShFill job = new @PKG@.ShFill(w, null, done);
    job.cropsOnly = cropsOnly;
    job.kind = kd;
    @PKG@.ShStore.LOCK.lock(); try {
      want = cropsOnly ? @PKG@.ShGeo.crops(p, kd) : @PKG@.ShGeo.region(p, kd);
      job.prep(p);   // 0.4.8: the seed stores + which islands the replant scan counts
    } finally { @PKG@.ShStore.LOCK.unlock(); }
    job.want = want;
    // 0.4.8: load only the chunks the region's blocks are in (16 islands reach 118 blocks out; a small shard stays small)
    java.util.HashSet seen = new java.util.HashSet();
    java.util.ArrayList chl = new java.util.ArrayList();
    for (int i = 0; i < want.size(); i++) {
      int[] b = (int[]) want.get(i);
      int cx0 = b[0] >> 5; int cz0 = b[2] >> 5;
      if (seen.add(cx0 + "," + cz0)) chl.add(new int[] { cx0, cz0 });
    }
    int n = chl.size();
    job.cxs = new int[n];
    job.czs = new int[n];
    @CST@ cs = w.getChunkStore();
    java.util.concurrent.CompletableFuture[] parts = new java.util.concurrent.CompletableFuture[n * 2];
    for (int i = 0; i < n; i++) {
      int[] c = (int[]) chl.get(i);
      job.cxs[i] = c[0];
      job.czs[i] = c[1];
      parts[2 * i] = cs.getChunkReferenceAsync(@CHU@.indexChunk(c[0], c[1]));
      parts[2 * i + 1] = cs.getChunkSectionReferenceAsync(c[0], 3, c[1]);
    }
    java.util.concurrent.CompletableFuture.allOf(parts).whenComplete(job);''')

# ================================================================================================ ShCore: locks, collect per island type, grow / buy / subs / Automation / seeds
P.rep('''  if (!own) return "-No " + @PKG@.ShKind.NAMES[kd] + " Shard yet - " + @PKG@.ShLv20.src(kd, false) + ".";   // 0.4.6
  return null;
}""")
M(core, "public static String gate(java.util.UUID u, String k, java.util.Properties p) { return gate(u, k, FK, p); }")''',
      '''  if (!own) return "-No " + @PKG@.ShKind.NAMES[kd] + " Shard yet - " + @PKG@.ShLv20.src(kd, false) + ".";   // 0.4.6
  String lk = @PKG@.ShIsl.lockMsg(u, kd);   // 0.4.8: the shard door's lock (the clicking player's own level)
  if (lk != null) return "-" + lk;
  return null;
}""")
M(core, "public static String gate(java.util.UUID u, String k, java.util.Properties p) { return gate(u, k, FK, p); }")''')
# ---- Collect: each island gives its OWN type's item (0.4.8), a retyped 0.4.6 island first pays out its legacy (old) item
_C0 = P.s.index('''M(core, r"""
public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {''')
_C1 = P.s.index('''# 0.3.1 sound pass: the wrapper - the 0.3 body, then the collect sting''', _C0)
P.rep(P.s[_C0:_C1], '''M(core, r"""
public static String collect0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {   // 0.3.1: the 0.3 collect, renamed (the wrapper plays the sting)
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read - ask an admin to look at the server log.";
  String no = gate(u, k, kd, p);
  if (no != null) return no;
  String bon = @PKG@.ShKind.BONUS[kd];
  long want = 0L; long wantE = 0L; long wantL = 0L;
  long baseGiven = 0L; long gEnch = 0L; long gBonus = 0L; long backM = 0L; long backB = 0L; long backL = 0L;
  double xpD = 0.0;   // 0.4.4: Farming XP before the percent (each island at its own totem tiers)
  java.util.LinkedHashMap got = new java.util.LinkedHashMap();    // 0.4.8: item -> count given (the message)
  java.util.LinkedHashMap cred = new java.util.LinkedHashMap();   // 0.4.8: collection item -> count (each island its own crop / ore / log ...)
  @PKG@.ShStore.LOCK.lock(); try {
    long now = now();
    @PKG@.ShMath.settleAll(kd, p, now);
    int n = @PKG@.ShMath.SLOTS;
    long[] take = new long[n];
    long[] takeE = new long[n];
    long[] takeL = new long[n];
    String[] lid = new String[n];
    double[] xa = new double[n];   // 0.4.4 fix 2
    for (int i = 0; i < n; i++) {
      if (slot >= 0 && i != slot) continue;
      take[i] = @PKG@.ShMath.stored(kd, p, i);
      takeE[i] = bon.length() == 0 ? 0L : @PKG@.ShMath.ench(kd, p, i);
      String lg = @PKG@.ShStore.str(p, @PKG@.ShIsl.ik(kd, i, "legacy"));   // 0.4.8: "item:count" of a retyped 0.4.6 island
      int lc = lg.lastIndexOf(':');
      if (lc > 0) { try { takeL[i] = Long.parseLong(lg.substring(lc + 1).trim()); lid[i] = lg.substring(0, lc); } catch (Throwable t) { takeL[i] = 0L; } }
      if (takeL[i] < 0L) takeL[i] = 0L;
      if (take[i] > 0L || takeE[i] > 0L) xa[i] = @PKG@.ShMath.xpAvg(kd, p, i, now);
      want += take[i];
      wantE += takeE[i];
      wantL += takeL[i];
    }
    if (want + wantE + wantL <= 0L) return "=Nothing is stored there yet.";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    for (int i = 0; i < n; i++) {
      if (take[i] > 0L) @PKG@.ShMath.xpSet(kd, p, i, @PKG@.ShMath.stored(kd, p, i) - take[i], (double) (@PKG@.ShMath.stored(kd, p, i) - take[i]) * xa[i]);   // 0.4.4 fix 2
      if (take[i] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, i, "stored"), String.valueOf(@PKG@.ShMath.stored(kd, p, i) - take[i]));
      if (takeE[i] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, i, "ench"), String.valueOf(@PKG@.ShMath.ench(kd, p, i) - takeE[i]));
      if (takeL[i] > 0L) p.remove(@PKG@.ShIsl.ik(kd, i, "legacy"));
    }
    p.setProperty(lastKey(kd), String.valueOf(now));   // fix2: the Collect tab's "Last collected ... ago"
    String err = @PKG@.ShStore.save(k, p);
    if (err != null) { p.clear(); p.putAll(old); @PKG@.ShCfg.warn("Collect refused (debit not written): " + err); return "-Collect failed: the shard file could not be saved. Nothing was taken."; }
    int cmp = @PKG@.ShMath.compactor(kd, p);
    long[] bm = new long[n];
    long[] bb = new long[n];
    long[] bl = new long[n];
    for (int i = 0; i < n; i++) {
      double xi = xa[i];   // 0.4.4 fix 2: the XP of the tiers that MADE the items (ShMath.xpAvg, read before the debit)
      if (takeL[i] > 0L && lid[i] != null) {   // 0.4.8: the old item first (what the island had made before it became the next tier)
        long gl = @PKG@.ShInv.give(cs, lid[i], takeL[i]);
        if (gl > 0L) { got.put(lid[i], Long.valueOf((got.get(lid[i]) == null ? 0L : ((Long) got.get(lid[i])).longValue()) + gl)); cred.put(lid[i], Long.valueOf((cred.get(lid[i]) == null ? 0L : ((Long) cred.get(lid[i])).longValue()) + gl)); }
        baseGiven += gl;
        xpD += (double) gl * (double) @PKG@.ShCfg.xpOf(kd);
        bl[i] = takeL[i] - gl;
        backL += bl[i];
      }
      if (take[i] > 0L) {
        int t = @PKG@.ShIsl.ty(kd, p, i);
        boolean sm = @PKG@.ShTotem.smelts(kd, p, i) && @PKG@.ShIsl.SMELT[t].length() > 0;
        String out = sm ? @PKG@.ShIsl.SMELT[t] : @PKG@.ShIsl.PROD[t];
        String en = sm ? @PKG@.ShIsl.SMELTE[t] : @PKG@.ShIsl.ENCH[t];
        long e = (cmp >= 1 && en.length() > 0) ? take[i] / 100L : 0L;
        long ge = e > 0L ? @PKG@.ShInv.give(cs, en, e) : 0L;
        long rest = take[i] - 100L * ge;
        long gr = rest > 0L ? @PKG@.ShInv.give(cs, out, rest) : 0L;
        long del = 100L * ge + gr;
        baseGiven += del;
        xpD += (double) del * xi;   // 0.4.4
        gEnch += ge;
        if (ge > 0L) got.put(en, Long.valueOf((got.get(en) == null ? 0L : ((Long) got.get(en)).longValue()) + ge));
        if (gr > 0L) got.put(out, Long.valueOf((got.get(out) == null ? 0L : ((Long) got.get(out)).longValue()) + gr));
        String ci = @PKG@.ShIsl.PROD[t];   // the collection of the island's own item (ingots / compacted count as their ore / crop)
        if (del > 0L) cred.put(ci, Long.valueOf((cred.get(ci) == null ? 0L : ((Long) cred.get(ci)).longValue()) + del));
        bm[i] = take[i] - del;
        backM += bm[i];
      }
      if (takeE[i] > 0L) {
        long gb = @PKG@.ShInv.give(cs, bon, takeE[i]);
        gBonus += gb;
        xpD += (double) gb * (@PKG@.ShKind.BMULT[kd] > 1 ? (double) @PKG@.ShKind.BMULT[kd] * xi : (double) @PKG@.ShKind.BXP[kd]);   // 0.4.4
        bb[i] = takeE[i] - gb;
        backB += bb[i];
      }
    }
    if (backM > 0L || backB > 0L || backL > 0L) {
      for (int i = 0; i < n; i++) {
        if (bm[i] > 0L) @PKG@.ShMath.xpSet(kd, p, i, @PKG@.ShMath.stored(kd, p, i) + bm[i], (double) (@PKG@.ShMath.stored(kd, p, i) + bm[i]) * xa[i]);   // 0.4.4 fix 2
        if (bm[i] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, i, "stored"), String.valueOf(@PKG@.ShMath.stored(kd, p, i) + bm[i]));
        if (bb[i] > 0L) p.setProperty(@PKG@.ShMath.ik(kd, i, "ench"), String.valueOf(@PKG@.ShMath.ench(kd, p, i) + bb[i]));
        if (bl[i] > 0L) p.setProperty(@PKG@.ShIsl.ik(kd, i, "legacy"), lid[i] + ":" + bl[i]);
      }
      String e2 = @PKG@.ShStore.save(k, p);
      if (e2 != null) @PKG@.ShCfg.warn("Collect: " + backM + " + " + backB + " + " + backL + " items that did not fit are back in memory but not on disk yet: " + e2);
    }
    @PKG@.ShStore.log(u + " " + k + (kd == FK ? "" : " " + @PKG@.ShKind.KEYS[kd]) + " slot " + slot + " debit " + want + " given " + baseGiven + " back " + backM + (wantL > 0L ? " legacy " + wantL + " back " + backL : "") + (wantE > 0L ? " ench debit " + wantE + " given " + gBonus + " back " + backB : "") + (gEnch > 0L ? " compacted " + gEnch : "") + " " + got.toString());
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  String extra = "";
  int bm1 = @PKG@.ShKind.BMULT[kd];
  if (baseGiven + gBonus > 0L) {
    String skill = @PKG@.ShKind.SKILL[kd];
    long per = (long) @PKG@.ShCfg.xpOf(kd);
    long bxp = bm1 > 1 ? (long) bm1 * per : (long) @PKG@.ShKind.BXP[kd];
    boolean fx = kd == FK;   // 0.4.4: Farming pays each island's totem-tier XP (xp.wheat per tier)
    if (per > 0L || bxp > 0L || (fx && xpD > 0.0)) {   // Combat: drops only (Skyy G9), no XP call at all
      long xp = fx ? (long) Math.floor(xpD * (double) @PKG@.ShCfg.XP_PCT / 100.0 + 0.000000001) : (baseGiven * per + gBonus * bxp) * (long) @PKG@.ShCfg.XP_PCT / 100L;
      long xpLeft = owedXp(u, skill, xp);   // fix (critic): unpaid XP waits in the collector's file and is paid on a later Collect
      if (xpLeft > 0L) extra = extra + " (" + @PKG@.ShCfg.num(xpLeft) + " " + skill + " XP waits - paid on your next Collect)";
      else if (xp > 0L) extra = extra + " +" + @PKG@.ShCfg.num(xp) + " " + skill + " XP";
    }
    if (bm1 > 1 && gBonus > 0L) { String c0 = @PKG@.ShKind.PROD[kd]; cred.put(c0, Long.valueOf((cred.get(c0) == null ? 0L : ((Long) cred.get(c0)).longValue()) + (long) bm1 * gBonus)); }   // the alias rule
    java.util.Iterator ci = cred.entrySet().iterator();
    while (ci.hasNext()) {
      java.util.Map.Entry en = (java.util.Map.Entry) ci.next();
      long owedC = owed(u, (String) en.getKey(), ((Long) en.getValue()).longValue());
      if (owedC > 0L) extra = extra + " - " + @PKG@.ShCfg.num(owedC) + " " + @PKG@.ShTotem.pretty((String) en.getKey()) + " collection count waiting";
    }
    if (bm1 <= 1 && gBonus > 0L) {
      long owedB = owed(u, bon, gBonus);
      if (owedB > 0L) extra = extra + " - " + @PKG@.ShCfg.num(owedB) + " " + @PKG@.ShTotem.pretty(bon) + " collection count waiting";
    }
  }
  if (baseGiven + gBonus <= 0L) return "-Your inventory is full - nothing was collected.";
  StringBuilder gt = new StringBuilder();
  java.util.Iterator gi = got.entrySet().iterator();
  while (gi.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) gi.next();
    if (gt.length() > 0) gt.append(" + ");
    gt.append(@PKG@.ShCfg.num(((Long) en.getValue()).longValue())).append(' ').append(@PKG@.ShTotem.pretty((String) en.getKey()));
  }
  if (gBonus > 0L) { if (gt.length() > 0) gt.append(" + "); gt.append(@PKG@.ShCfg.num(gBonus)).append(' ').append(@PKG@.ShTotem.pretty(bon)).append(kd == FK ? " (Harvest Moon)" : " (rare finds)"); }
  long left = backM + backB + backL;
  return "+Collected " + gt.toString() + extra + (left > 0L ? ". " + @PKG@.ShCfg.num(left) + " did not fit and stay in the shard." : ".");
}""")
''')
# ---- the 0.4.6 grow + buy island move below the multi-item take (they now cost several items); their old bodies go
_G0 = P.s.index('''# grow an island one size (coins, the shard's grow item, its collection tier); pasted at once if the shard world is loaded
M(core, r"""
public static String grow0(''')
_G1 = P.s.index('''# 0.4.6: one purchase writing several keys (caller holds ShStore.LOCK)''', _G0)
P.rep(P.s[_G0:_G1], '''# 0.4.8: grow0 / grow are defined below takeAll (a grow costs several items: Enchanted + Eternal seeds, spec 13.2)
''')
_B0 = P.s.index('''# 0.4.6: buy an island for an empty slot (spec 9.4; Skyy "costs a lot to start getting more").''')
_B1 = P.s.index('''M(core, "public static String buyIsland(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) { String r = buyIsland0(u, k, kd, slot, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
''', _B0)
_B1 += len('''M(core, "public static String buyIsland(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) { String r = buyIsland0(u, k, kd, slot, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
''')
P.rep(P.s[_B0:_B1], '''# 0.4.8: buyIsland0 / buyIsland are defined below takeAll (the next tier of the ladder, coins + several items)
''')
P.rep('''# craft recipe ri at shard kd's bench (the 0.2-0.3 craft, gated by the bench: owner, shard owned, bench tier)''', '''# ================= 0.4.8 THE ISLAND UPGRADES (spec 8, 9, 13): the multi-item purchase, grow, buy the next tier, the 3 sub-upgrades, Automation,
# the seed store. Every purchase = purchase()'s order: every check, the items taken (counted, stacks with data kept), then the coins (items
# back when they fail), then every key written + SAVED (a refused save undoes it and refunds both). Owner only (gateOwn: + the door lock).
M(isl48, r"""
public static String subName(int kd, int which) {
  String st = STYLE[kd];
  if (which == 1) return "Decorations";
  if (which == 2) return st.equals("mine") ? "Underground Springs" : (st.equals("ranch") ? "Water Troughs" : "Irrigation");
  if (st.equals("mine")) return "Ore Amount";
  if (st.equals("ranch")) return "Herd Size";
  if (st.equals("grove")) return "Tree Amount";
  if (st.equals("orchard")) return "Fruit Trees";
  if (st.equals("farm")) return "Crop Amount";
  return "Amount";
}""")
M(isl48, r"""
public static int slotOf(int kd, java.util.Properties p, int t) {
  if (p == null) return -1;
  for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) if (@PKG@.ShMath.hasIsland(kd, p, s) && ty(kd, p, s) == t) return s;
  return -1;
}""")
M(isl48, r"""
public static int nextTier(int kd, java.util.Properties p) {
  for (int i = 0; i < LADN[kd]; i++) if (slotOf(kd, p, LAD0[kd] + i) < 0) return i;
  return -1;
}""")
M(isl48, r"""
public static int freeSlot(int kd, java.util.Properties p) {
  for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) if (!@PKG@.ShMath.hasIsland(kd, p, s)) return s;
  return -1;
}""")
M(isl48, r"""
public static String matsText(Object[] m) {
  String[] ids = (String[]) m[0];
  long[] q = (long[]) m[1];
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ids.length; i++) { if (sb.length() > 0) sb.append(" + "); sb.append(@PKG@.ShCfg.num(q[i])).append(' ').append(@PKG@.ShTotem.pretty(ids[i])); }
  return sb.toString();
}""")
M(core, r"""
public static String purchaseM(java.util.UUID u, String k, int kd, java.util.Properties p, @IC@[] cs, Object[] mats, long coins, String[] keys, String[] vals, String tag, String what) {
  String[] ids = (String[]) mats[0];
  long[] q = (long[]) mats[1];
  for (int i = 0; i < ids.length; i++) {
    long have = @PKG@.ShInv.count(cs, ids[i]);
    if (have < q[i]) return "-You need " + @PKG@.ShCfg.num(q[i]) + " " + @PKG@.ShTotem.pretty(ids[i]) + " (you have " + @PKG@.ShCfg.num(have) + ").";
  }
  long purse = @PKG@.ShPay.coins(u);
  if (coins > 0L && purse >= 0L && purse < coins) return "-You need " + @PKG@.ShCfg.num(coins) + " coins (you have " + @PKG@.ShCfg.num(purse) + ").";
  @PKG@.ShMath.settleAll(kd, p, now());   // production up to now at the old numbers
  java.util.ArrayList kept = new java.util.ArrayList();
  long[] took = takeAll(cs, ids, q, kept);
  if (took == null) return "-The items could not be taken - nothing was bought.";
  if (!@PKG@.ShPay.takeCoins(u, coins)) {
    long r = refundAll(cs, ids, took, kept);
    @PKG@.ShStore.log(u + " " + k + " " + tag + " coins refused - refund " + r + " items");
    return "-The coins could not be taken - your items are back.";
  }
  java.util.Properties old = new java.util.Properties();
  old.putAll(p);
  for (int i = 0; i < keys.length; i++) p.setProperty(keys[i], vals[i]);
  String e = @PKG@.ShStore.save(k, p);
  if (e != null) {
    p.clear(); p.putAll(old);
    long ri = refundAll(cs, ids, took, kept);
    boolean rc = @PKG@.ShPay.addCoins(u, coins);
    @PKG@.ShStore.log(u + " " + k + " " + what + " SAVE FAILED " + e + " - refund " + ri + " items, coins " + (rc ? coins : 0L) + " of " + coins);
    @PKG@.ShCfg.warn(tag + " not saved, refunded: " + e);
    return "-It could not be saved - your items" + (rc ? " and coins are" : " are") + " back." + (rc ? "" : " Ask an admin about the " + @PKG@.ShCfg.num(coins) + " coins (collect.log).");
  }
  @PKG@.ShStore.log(u + " " + k + " " + what + " paid " + coins + " coins + " + @PKG@.ShIsl.matsText(mats) + @PKG@.ShInv.keptText(kept));
  return null;
}""")
# GROW (spec 8): only when the 3 sub-upgrades are 5 / 5 / 5; then size + 1 and the three start at 0 (their levels count on). Cost = the
# grow hours at the island's tier level + isl.mat.grow (Enchanted 4 / 16 + the crop's Eternal seeds 8 / 24); + the 0.4.x collection tier rows
M(core, r"""
public static String grow0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);
  if (no != null) return no;
  if (slot < 0 || slot >= @PKG@.ShMath.SLOTS) return "-Pick an island first.";
  int t0;
  @PKG@.ShStore.LOCK.lock(); try { if (!@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet."; t0 = @PKG@.ShIsl.ty(kd, p, slot); } finally { @PKG@.ShStore.LOCK.unlock(); }
  double cv = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[t0]));   // the bridge asked outside the lock
  int ct = -2;
  String res;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t0) return "-That island changed meanwhile - open the menu again.";
    int sz = @PKG@.ShMath.size(kd, p, slot);
    if (sz >= 3) return "=That island is fully grown.";
    int a = @PKG@.ShIsl.sub(p, kd, slot, 0); int d = @PKG@.ShIsl.sub(p, kd, slot, 1); int i = @PKG@.ShIsl.sub(p, kd, slot, 2);
    if (a < 5 || d < 5 || i < 5) return "-Max all 3 upgrades first: " + @PKG@.ShIsl.subName(kd, 0) + " " + a + "/5, Decorations " + d + "/5, " + @PKG@.ShIsl.subName(kd, 2) + " " + i + "/5.";
    int need = sz == 1 ? @PKG@.ShCfg.GM_COLL : @PKG@.ShCfg.GL_COLL;
    if (need > 0) {
      @PKG@.ShStore.LOCK.unlock();
      try { ct = @PKG@.ShPay.collTier(u, @PKG@.ShKind.COLL[kd]); } finally { @PKG@.ShStore.LOCK.lock(); }
      if (ct < need) return "-Needs " + @PKG@.ShKind.CNAME[kd] + " collection " + need + " (you: " + (ct < 0 ? "?" : String.valueOf(ct)) + ").";
      if (@PKG@.ShMath.size(kd, p, slot) != sz) return "-That island changed meanwhile - open the menu again.";
    }
    long coins = @PKG@.ShIsl.coins(@PKG@.ShIsl.growH(sz + 1), cv);
    Object[] mats = @PKG@.ShIsl.mats(kd, t0, @PKG@.ShCfg.MAT_GROW, sz - 1, 1L);
    String[] keys = new String[] { @PKG@.ShMath.ik(kd, slot, "size"), @PKG@.ShIsl.ik(kd, slot, "amt"), @PKG@.ShIsl.ik(kd, slot, "deco"), @PKG@.ShIsl.ik(kd, slot, "irr") };
    String[] vals = new String[] { String.valueOf(sz + 1), "0", "0", "0" };
    String r = purchaseM(u, k, kd, p, cs, mats, coins, keys, vals, "grow", @PKG@.ShKind.KEYS[kd] + " grow slot " + slot + " " + @PKG@.ShIsl.KEY[t0] + " " + sz + " -> " + (sz + 1));
    if (r != null) return r;
    res = "+The " + @PKG@.ShIsl.tname(t0) + " island grew to " + (sz == 1 ? "Medium" : "Large") + " - its 3 upgrades start again (what they gave stays).";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShWorld2.repaint(k, kd);
  return res;
}""")
M(core, "public static String grow(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) { String r = grow0(u, k, kd, slot, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")   # 0.3.1
M(core, "public static String grow(java.util.UUID u, String k, int slot, @IC@[] cs) { return grow(u, k, FK, slot, cs); }")
# BUY THE NEXT TIER (spec 9.1): tier index ti (0 = T1) must be the first tier not owned (the path is in order); it goes into the first free slot,
# Small, no totems, Automated when the shard is. Cost = isl.buyHours at its tier level + isl.buyItems.<kind> (T2 Lettuce = 3,500 + 128 Lettuce
# + 32 Lettuce Seeds - Skyy's "money, lettuce, and lettuce seeds")
M(core, r"""
public static String buyIsland0(java.util.UUID u, String k, int kd, int ti, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);
  if (no != null) return no;
  if (ti < 0 || ti >= @PKG@.ShIsl.LADN[kd]) return "-Pick an island first.";
  int t = @PKG@.ShIsl.LAD0[kd] + ti;
  double cv = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[t]));   // the bridge asked outside the lock
  String res;
  int slot;
  @PKG@.ShStore.LOCK.lock(); try {
    if (@PKG@.ShIsl.slotOf(kd, p, t) >= 0) return "=You own the " + @PKG@.ShIsl.tname(t) + " island already.";
    int nx = @PKG@.ShIsl.nextTier(kd, p);
    if (nx != ti) return nx < 0 ? "=You own every island of this shard." : "-Buy the " + @PKG@.ShIsl.tname(@PKG@.ShIsl.LAD0[kd] + nx) + " island first (islands come in tier order).";
    slot = @PKG@.ShIsl.freeSlot(kd, p);
    if (slot < 0) return "=This shard has no room for another island.";
    long coins = @PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, cv);
    Object[] mats = @PKG@.ShIsl.mats(kd, t, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L);
    long tn = now();
    String[] keys = new String[] { @PKG@.ShMath.ik(kd, slot, "type"), @PKG@.ShMath.ik(kd, slot, "size"), @PKG@.ShMath.ik(kd, slot, "last"), @PKG@.ShMath.ik(kd, slot, "stored") };
    String[] vals = new String[] { @PKG@.ShIsl.KEY[t], "1", String.valueOf(tn), "0" };
    String r = purchaseM(u, k, kd, p, cs, mats, coins, keys, vals, "island", @PKG@.ShKind.KEYS[kd] + " buy " + @PKG@.ShIsl.KEY[t] + " island in slot " + (slot + 1));
    if (r != null) return r;
    res = "+The " + @PKG@.ShIsl.tname(t) + " island is yours (Small). Put a worker totem on it (Totems tab) so it makes items.";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShWorld2.repaint(k, kd);
  return res;
}""")
M(core, "public static String buyIsland(java.util.UUID u, String k, int kd, int ti, @IC@[] cs) { String r = buyIsland0(u, k, kd, ti, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
# A SUB-UPGRADE (spec 8): which 0 Amount / 1 Decorations / 2 Irrigation, the next level (1-5) at this size; cost = isl.subHours.<size>[level]
# at the island's tier level + isl.mat.<sub> (that size's part) x the level
M(core, r"""
public static String buySub0(java.util.UUID u, String k, int kd, int slot, int which, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);
  if (no != null) return no;
  if (slot < 0 || slot >= @PKG@.ShMath.SLOTS || which < 0 || which > 2) return "-Pick an island first.";
  int t0;
  @PKG@.ShStore.LOCK.lock(); try { if (!@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet."; t0 = @PKG@.ShIsl.ty(kd, p, slot); } finally { @PKG@.ShStore.LOCK.unlock(); }
  double cv = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[t0]));
  String res;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t0) return "-That island changed meanwhile - open the menu again.";
    int sz = @PKG@.ShMath.size(kd, p, slot);
    int lv = @PKG@.ShIsl.sub(p, kd, slot, which);
    String nm = @PKG@.ShIsl.subName(kd, which);
    if (lv >= 5) return sz >= 3 ? "=" + nm + " is at its highest level." : "=" + nm + " is 5/5 at this size - grow the island to go on.";
    int nl = lv + 1;
    long coins = @PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, nl), cv);
    String tm = which == 0 ? @PKG@.ShCfg.MAT_AMT : (which == 1 ? @PKG@.ShCfg.MAT_DECO : @PKG@.ShCfg.MAT_IRR);
    Object[] mats = @PKG@.ShIsl.mats(kd, t0, tm, sz - 1, (long) nl);
    String r = purchaseM(u, k, kd, p, cs, mats, coins, new String[] { @PKG@.ShIsl.ik(kd, slot, @PKG@.ShIsl.SUBK[which]) }, new String[] { String.valueOf(nl) },
                         "sub", @PKG@.ShKind.KEYS[kd] + " " + @PKG@.ShIsl.SUBK[which] + " slot " + slot + " " + @PKG@.ShIsl.KEY[t0] + " size " + sz + " " + lv + " -> " + nl);
    if (r != null) return r;
    res = "+" + nm + " " + nl + "/5 on the " + @PKG@.ShIsl.tname(t0) + " island (+" + @PKG@.ShCfg.dec((@PKG@.ShIsl.mult(kd, p, slot, sz) - 1.0) * 100.0) + " % output from its upgrades).";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShWorld2.repaint(k, kd);
  return res;
}""")
M(core, "public static String buySub(java.util.UUID u, String k, int kd, int slot, int which, @IC@[] cs) { String r = buySub0(u, k, kd, slot, which, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
# AUTOMATION (spec 7, once per shard): ladder step up.auto.step + up.auto.items.<kind>; then every island of the shard is automated
M(core, r"""
public static String buyAuto0(java.util.UUID u, String k, int kd, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);
  if (no != null) return no;
  int step = @PKG@.ShCfg.AUTO_STEP;
  double cv = @PKG@.ShCfg.curve(@PKG@.ShIsl.stepLv(step));
  @PKG@.ShStore.LOCK.lock(); try {
    if (@PKG@.ShIsl.auto(kd, p)) return "=This shard is automated already.";
    long coins = @PKG@.ShIsl.coins(@PKG@.ShIsl.stepH(step), cv);
    Object[] mats = @PKG@.ShIsl.mats(kd, @PKG@.ShIsl.LAD0[kd], @PKG@.ShCfg.AUTO_ITEMS[kd], 0, 1L);
    String r = purchaseM(u, k, kd, p, cs, mats, coins, new String[] { @PKG@.ShIsl.kk(kd, "auto") }, new String[] { "1" }, "auto", @PKG@.ShKind.KEYS[kd] + " automation");
    if (r != null) return r;
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShIsl.quest(u, "shard:auto:" + @PKG@.ShKind.KEYS[kd]);
  @PKG@.ShWorld2.repaint(k, kd);
  return "+Automation! Every island of this " + @PKG@.ShKind.NAMES[kd] + " Shard now works by itself at full speed" + ("farm".equals(@PKG@.ShIsl.STYLE[kd]) ? " - every tilled spot grows its Eternal crop." : ".");
}""")
M(core, "public static String buyAuto(java.util.UUID u, String k, int kd, @IC@[] cs) { String r = buyAuto0(u, k, kd, cs); @PKG@.ShSnd.ok(u, r, 2); return r; }")
# THE SEED STORE (spec 7): Give seeds = every matching seed / sapling you carry (Farming: Eternal seeds first - each makes one more cell
# Eternal, never used up), up to shard.seedStoreMax; SAVED before the items are taken (a short take puts the store back). Take back = the
# store into your inventory, saved first (what does not fit goes back into the store).
M(core, r"""
public static String seedsGive(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);
  if (no != null) return no;
  if (slot < 0 || slot >= @PKG@.ShMath.SLOTS) return "-Pick an island first.";
  String msg = "";
  long gotE = 0L; long gotS = 0L;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet.";
    if (@PKG@.ShIsl.auto(kd, p)) return "=This shard is automated - it needs no seeds.";
    int t = @PKG@.ShIsl.ty(kd, p, slot);
    boolean farm = "farm".equals(@PKG@.ShIsl.STYLE[kd]);
    String es = @PKG@.ShIsl.ESEED[t];
    String sd = @PKG@.ShIsl.SEED[t];
    if (!farm && !@PKG@.ShIsl.trees(kd)) return "=This shard needs no seeds.";
    if (farm && es.length() > 0) {   // Eternal seeds: one more Eternal cell each (up to the island's farm cells)
      int sz = @PKG@.ShMath.size(kd, p, slot);
      int room = @PKG@.ShIsl.farmN(sz, @PKG@.ShIsl.sub(p, kd, slot, 0)) - @PKG@.ShIsl.eternal(kd, p, slot);
      long have = @PKG@.ShInv.count(cs, es);
      long n = have < (long) room ? have : (long) room;
      if (n > 0L) {
        int e0 = @PKG@.ShIsl.eternal(kd, p, slot);
        p.setProperty(@PKG@.ShIsl.ik(kd, slot, "eternal"), String.valueOf((long) e0 + n));
        String er = @PKG@.ShStore.save(k, p);
        if (er != null) { p.setProperty(@PKG@.ShIsl.ik(kd, slot, "eternal"), String.valueOf(e0)); return "-The seed store could not be saved - nothing was taken."; }
        gotE = @PKG@.ShInv.take(cs, es, n);
        if (gotE < n) {
          p.setProperty(@PKG@.ShIsl.ik(kd, slot, "eternal"), String.valueOf((long) e0 + gotE));
          String er2 = @PKG@.ShStore.save(k, p);
          if (er2 != null) @PKG@.ShCfg.warn("the Eternal seed count of " + k + " could not be corrected (" + er2 + ")");
        }
      }
    }
    if (sd.length() > 0 && (!farm || !sd.equals(es))) {   // plain seeds (Farming) / saplings (Foraging, Orchard) into the store
      long cur = @PKG@.ShIsl.seeds(kd, p, slot);
      long room = (long) @PKG@.ShCfg.SEED_MAX - cur;
      long have = @PKG@.ShInv.count(cs, sd);
      long n = have < room ? have : room;
      if (n > 0L) {
        p.setProperty(@PKG@.ShIsl.ik(kd, slot, "seed"), String.valueOf(cur + n));
        String er = @PKG@.ShStore.save(k, p);
        if (er != null) { p.setProperty(@PKG@.ShIsl.ik(kd, slot, "seed"), String.valueOf(cur)); return "-The seed store could not be saved - nothing was taken."; }
        gotS = @PKG@.ShInv.take(cs, sd, n);
        if (gotS < n) {
          p.setProperty(@PKG@.ShIsl.ik(kd, slot, "seed"), String.valueOf(cur + gotS));
          String er2 = @PKG@.ShStore.save(k, p);
          if (er2 != null) @PKG@.ShCfg.warn("the seed store of " + k + " could not be corrected (" + er2 + ")");
        }
      }
    }
    if (gotE + gotS <= 0L) return "-You carry no " + (sd.length() > 0 ? @PKG@.ShTotem.pretty(sd) : "seeds") + (farm && es.length() > 0 ? " or " + @PKG@.ShTotem.pretty(es) : "") + " for this island" + (@PKG@.ShIsl.seeds(kd, p, slot) >= (long) @PKG@.ShCfg.SEED_MAX ? " (its store is full)" : "") + ".";
    @PKG@.ShStore.log(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " seeds slot " + slot + " eternal +" + gotE + " store +" + gotS);
    msg = "+" + (gotE > 0L ? gotE + " more Eternal cells" : "") + (gotE > 0L && gotS > 0L ? " and " : "") + (gotS > 0L ? gotS + " " + @PKG@.ShTotem.pretty(sd) + " in the store (" + @PKG@.ShIsl.seeds(kd, p, slot) + " now)" : "") + " - the totems replant from them.";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShIsl.quest(u, "shard:seeds:" + @PKG@.ShKind.KEYS[kd]);
  @PKG@.ShWorld2.repaint(k, kd);
  return msg;
}""")
M(core, r"""
public static String seedsTake(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);
  if (no != null) return no;
  if (slot < 0 || slot >= @PKG@.ShMath.SLOTS) return "-Pick an island first.";
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet.";
    int t = @PKG@.ShIsl.ty(kd, p, slot);
    String sd = @PKG@.ShIsl.SEED[t];
    long cur = @PKG@.ShIsl.seeds(kd, p, slot);
    if (cur <= 0L || sd.length() == 0) return "=The seed store is empty.";
    p.setProperty(@PKG@.ShIsl.ik(kd, slot, "seed"), "0");
    String er = @PKG@.ShStore.save(k, p);
    if (er != null) { p.setProperty(@PKG@.ShIsl.ik(kd, slot, "seed"), String.valueOf(cur)); return "-The seed store could not be saved - nothing moved."; }
    long g = @PKG@.ShInv.give(cs, sd, cur);
    if (g < cur) {
      p.setProperty(@PKG@.ShIsl.ik(kd, slot, "seed"), String.valueOf(cur - g));
      String er2 = @PKG@.ShStore.save(k, p);
      if (er2 != null) { @PKG@.ShCfg.warn("the seed store of " + k + " could not be saved after a short take back (" + er2 + ")"); @PKG@.ShStore.log(u + " " + k + " seeds take back " + g + " of " + cur + " - REST NOT SAVED " + er2); }
    }
    @PKG@.ShStore.log(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " seeds take back slot " + slot + " " + g + " of " + cur);
    return g <= 0L ? "-Your inventory is full - the seeds stay in the store." : "+" + g + " " + @PKG@.ShTotem.pretty(sd) + " back in your inventory" + (g < cur ? " (" + (cur - g) + " did not fit and stay in the store)." : ".");
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")

# craft recipe ri at shard kd's bench (the 0.2-0.3 craft, gated by the bench: owner, shard owned, bench tier)''')
# ---- Pick up: never the island's own starter door. fix2 (critic): unless that door's island was reset (a stale record) - then the shard
# comes back as an item like any reset portal (ShWorld2.enter tells the player to use Pick up Shard; the new world's archipelago, when it
# is built, records its new door beside the placed item)
P.rep('''  String id = null;
  @PKG@.ShStore.LOCK.lock(); try {
    placed = @PKG@.ShStore.str(p, @PKG@.ShMath.kk(kd, "placed"));
    a = placed.split("\\\\|");
    if (placed.length() == 0 || a.length != 4) return "-Your shard is not placed.";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (@PKG@.ShRole.stale(placed, k)) mode = 1;   // fix (critic): after an island reset the old portal is out of reach - the shard comes back from any menu
  else {''', '''  String id = null;
  boolean sdoor = false;   // 0.4.8: the record is the starter island's own door
  @PKG@.ShStore.LOCK.lock(); try {
    placed = @PKG@.ShStore.str(p, @PKG@.ShMath.kk(kd, "placed"));
    a = placed.split("\\\\|");
    if (placed.length() == 0 || a.length != 4) return "-Your shard is not placed.";
    sdoor = placed.equals(@PKG@.ShStore.str(p, @PKG@.ShMath.kk(kd, "door.starter")));
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (@PKG@.ShRole.stale(placed, k)) mode = 1;   // fix (critic): after an island reset the old portal is out of reach - the shard comes back from any menu
  else if (sdoor) return "-This is your starter island's own " + @PKG@.ShKind.NAMES[kd] + " Shard door - it stays there.";   // 0.4.8 (fix2: a reset island's stale door does not count)
  else {''')
# ---- Enter: the door lock + the quest event
P.rep('''  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (from != null && from.getName().equals(@PKG@.ShWorlds.name(k)) && st != null && ref != null) {''', '''  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  String lk = @PKG@.ShIsl.lockMsg(u, kd);   // 0.4.8: the door's lock (the clicking player's own level; no world load)
  if (lk != null) return "-" + lk;
  if (from != null && from.getName().equals(@PKG@.ShWorlds.name(k)) && st != null && ref != null) {''')
P.rep('''  hp.kind = kd;
  f.whenComplete(hp);
  return "+Opening your " + @PKG@.ShKind.NAMES[kd] + " Shard...";''', '''  hp.kind = kd;
  f.whenComplete(hp);
  @PKG@.ShIsl.quest(u, "shard:door:" + @PKG@.ShKind.KEYS[kd]);   // 0.4.8: SkyyQuests (the archipelago line, round R4)
  return "+Opening your " + @PKG@.ShKind.NAMES[kd] + " Shard...";''')
# ---- shard:fn:allowed: manual farming in a shard (Skyy: plant / till / water by hand) - planting seeds / saplings, using a hoe / watering can
P.rep('''  if (a.equals("use")) return Boolean.valueOf(crop(block) || (block != null && (block.indexOf("Skyy_Shard_") >= 0 || block.indexOf("Skyy_TotemBlock_") >= 0 || block.indexOf("Skyy_TotemBench_") >= 0)));   // 0.2: a totem opens its page; 0.3: every shard stand; 0.4: the Totem Bench''',
      '''  if (a.equals("use")) return Boolean.valueOf(crop(block) || soil(block) || (block != null && (block.indexOf("Skyy_Shard_") >= 0 || block.indexOf("Skyy_TotemBlock_") >= 0 || block.indexOf("Skyy_TotemBench_") >= 0)));   // 0.2: a totem opens its page; 0.3: every shard stand; 0.4: the Totem Bench; 0.4.8: soil (hoe / watering can)
  if (a.equals("place")) return Boolean.valueOf(plantable(block));   // 0.4.8: seeds / saplings / spores (SkyyIslands 0.5.25 reports the item placed)''')
P.rep('''M(gate, r"""
public static Boolean allowed(String world, String action, String block) {''', '''M(gate, "public static boolean soil(String id) { return id != null && (id.startsWith(\\"Soil_Dirt\\") || id.startsWith(\\"Soil_Grass\\")); }")   # 0.4.8
M(gate, r"""
public static boolean plantable(String id) {
  if (id == null) return false;
  return id.startsWith("Plant_Seeds_") || id.startsWith("Plant_Sapling_") || id.startsWith("Plant_Spores_") || id.indexOf("Plant_Crop_") >= 0;
}""")
M(gate, r"""
public static Boolean allowed(String world, String action, String block) {''')

# ================================================================================================ the page: the Islands tab = the ladder (R1 plain list; the map is R3)
P.rep('''i0.append(("#" + P + "IMap", SUI.panel(P + "IHub", "row", w=HBW, h=HBH, layout="Top", anchor={"left": MAPC[0] - HBW // 2, "top": MAPC[1] - HBH // 2})))
i0.append(("#" + P + "IHub", SUI.label(P + "IHubT", "Hub", "bold", w=HBW, h=HBH, align="Center")))
SLOT_UI = []
for i in range(SLOTS):
    ang = math.radians(-90 + 60 * i)
    cx_, cy_ = MAPC[0] + 245 * math.cos(ang), MAPC[1] + 190 * math.sin(ang)
    L_, T_ = int(round(cx_ - SBW / 2)), int(round(cy_ - SBH / 2))
    SLOT_UI.append((L_, T_))
    _boxes.append(("slot%d" % i, L_, T_, SBW, SBH))''', '''# 0.4.8: the boxes are the shard's LADDER in tier order (T1 first; box i = tier i + 1), 4 a row - the radial map is round R3
SBW, SBH = 156, 56
_GX0 = (LW - (4 * SBW + 3 * 16)) // 2
_GY0 = 48
_boxes = [("title", 12, 8, LW - 24, 26)]
_HUBT = _GY0 + 4 * (SBH + 14) + 6
i0.append(("#" + P + "IMap", SUI.panel(P + "IHub", "row", w=LW - 24, h=HBH, layout="Top", anchor={"left": 12, "top": _HUBT})))
i0.text("#" + P + "IHub", P + "IHubT", J_("this.iHub", "Islands come in tier order - buy each one after the one before it."), "caption", w=LW - 40, h=HBH, align="Center")
_boxes.append(("hub", 12, _HUBT, LW - 24, HBH))
SLOT_UI = []
for i in range(SLOTS):
    L_, T_ = _GX0 + (i % 4) * (SBW + 16), _GY0 + (i // 4) * (SBH + 14)
    SLOT_UI.append((L_, T_))
    _boxes.append(("slot%d" % i, L_, T_, SBW, SBH))''')
P.rep('''i0.text("#" + P + "IMap", P + "IMapT", "Pick a slot to see its island, or an empty slot to buy one. Islands grow in place.", "caption", w=LW - 24, h=26,
        anchor={"left": 12, "top": 8})
_boxes.append(("title", 12, 8, LW - 24, 26))''', '''i0.text("#" + P + "IMap", P + "IMapT", "Pick an island to upgrade it, or the next one to buy it. Islands grow in place.", "caption", w=LW - 24, h=26,
        anchor={"left": 12, "top": 8})''')
P.rep('''        a.text("#" + sid + "Tx", sid + "A", J_("this.sName[%d]" % i, "Slot 1 - Wheat"), "rowName", size=14, h=28, w=SBW - 16)
        a.text("#" + sid + "Tx", sid + "B", J_("this.sSub[%d]" % i, "Small"), "rowSub", size=12, h=22, w=SBW - 16)''',
      '''        a.text("#" + sid + "Tx", sid + "A", J_("this.sName[%d]" % i, "T1 Wheat"), "rowName", size=14, h=28, w=SBW - 16)
        a.text("#" + sid + "Tx", sid + "B", J_("this.sSub[%d]" % i, "Small 2/0/1"), "rowSub", size=12, h=22, w=SBW - 16, col=J_("this.sCol[%d]" % i, TEXT))''')
P.rep('''i1.text(IR, P + "IRT", J_("this.iTitle", "Slot 1 - Wheat Island"), "panelTitle", h=30, w=RW - 24)
for j, samp in enumerate(("Size: Small (13 x 13)", "Makes 60 items / hour", "Totems: 1 Harvest Spirit I", "Next: Medium (21 x 21)",
                          "Would make 96 items / hour", "Cost", "5,000 coins (you: 12,000)", "8 Eternal Wheat Seeds (you: 0)",
                          "Wheat collection 4 (you: 2)")):
    kind = "section" if j == 5 else "default"
    i1.text(IR, P + "IR%d" % j, J_("this.iTx[%d]" % j, samp), kind, size=14, h=28, w=RW - 24,
            col=J_("this.iCol[%d]" % j, TEXT) if j not in (5,) else None)''', '''i1.text(IR, P + "IRT", J_("this.iTitle", "T1 Wheat Island - Small"), "panelTitle", h=30, w=RW - 24)
IRWRAP, IRH1, IRH2 = (1, 2, 3, 4, 5, 7, 8), 22, 36   # fix (critic): the rows that wrap (2 lines of 13 px) / the one-line rows
for j, samp in enumerate(("Makes 24 items / hour - Manual phase", "Totems: 1 of 3 pads (Totems tab)", "Crop Amount 2/5 (+1.0 %)",
                          "Next: 120 coins + 48 Wheat", "Decorations 1/5 - next: 80 coins", "Irrigation 0/5 - next: 40 coins",
                          "Grow: max all 3 upgrades first", "Seed store: 12 Wheat Seeds", "Automation: 550 coins + 128 Wheat")):   # 0.4.8
    # fix (critic): the price rows (totems, the 3 sub-upgrades, Grow, Automation) wrap onto 2 lines - their materials are wider than the panel
    _wr = j in IRWRAP
    i1.text(IR, P + "IR%d" % j, J_("this.iTx[%d]" % j, samp), "default", size=13, h=IRH2 if _wr else IRH1, w=RW - 24, col=J_("this.iCol[%d]" % j, TEXT),
            wrap=True if _wr else None)   # (WrapMaxLines is not probed yet: the row height holds 2 lines)
assert 30 + sum(IRH2 if _j in IRWRAP else IRH1 for _j in range(9)) + 12 + 4 * (SUI.BTN_SMALL_H + 6) <= CH - 24, "0.4.8: the island panel fits"''')
P.rep('''ig = seg("igrow")
ig.append((IR, SUI.button(P + "IGrow", "Grow island", "secondary", w=RW - 24)))          # 0.4.2: Secondary''',
      '''# 0.4.8: an owned island's buttons (the 3 sub-upgrades + Grow), the seed store, the shard's Automation - small buttons, two a row
HB2 = (RW - 24 - 8) // 2
# fix (critic): the buttons carry the shard's own row names (Mining: Ore Amount / Springs, Ranching: Herd Size / Troughs, else Amount / Irrigation)
for sg_, (amt_, wat_) in (("ibtn", ("Amount", "Irrigation")), ("ibtnM", ("Ore Amount", "Springs")), ("ibtnR", ("Herd Size", "Troughs"))):
    ig = seg(sg_)
    for gi_, (b1_, t1x, b2_, t2x) in enumerate((("ISubA", amt_, "ISubD", "Decorations"), ("ISubI", wat_, "IGrow", "Grow island"))):
        ig.append((IR, SUI.group(P + "IBG%d" % gi_, layout="Left", w=RW - 24, h=SUI.BTN_SMALL_H, anchor={"bottom": 6})))
        ig.append(("#" + P + "IBG%d" % gi_, SUI.button(P + b1_, t1x, "secondary", "small", w=HB2)))
        ig.append(("#" + P + "IBG%d" % gi_, SUI.spacer(w=8)))
        ig.append(("#" + P + "IBG%d" % gi_, SUI.button(P + b2_, t2x, "secondary", "small", w=HB2)))
isd = seg("iseed")
isd.append((IR, SUI.group(P + "ISG", layout="Left", w=RW - 24, h=SUI.BTN_SMALL_H, anchor={"bottom": 6})))
isd.append(("#" + P + "ISG", SUI.button(P + "ISeed", "Give seeds", "secondary", "small", w=HB2)))
isd.append(("#" + P + "ISG", SUI.spacer(w=8)))
isd.append(("#" + P + "ISG", SUI.button(P + "ISeedB", "Take seeds", "secondary", "small", w=HB2)))
iau = seg("iauto")
iau.append((IR, SUI.button(P + "IAuto", "Buy Automation", "secondary", "small", w=RW - 24)))''')
P.rep('''            v.extend(SEG["iside"]); v.extend(SEG["ibuy" if sel == 1 else "igrow"])   # 0.4.6: one variant with Buy island''',
      '''            v.extend(SEG["iside"])   # 0.4.8: an owned island's buttons (+ seeds + Automation), or Buy island
            if sel == 1:
                v.extend(SEG["ibuy"])
            else:
                v.extend(SEG["ibtn"]); v.extend(SEG["iseed"]); v.extend(SEG["iauto"])''')
P.rep('''    jseg("iside"), "    if (this.iCan && this.mine) {", jseg("igrow"), binds([(P + "IGrow", "grow")]), "    }",''',
      '''    jseg("iside"), "    if (this.iCan && this.mine) {", "    if (this.kind == %d) {" % KINDS.index("Mining"), jseg("ibtnM"), "    } else if (this.kind == %d) {" % KINDS.index("Ranching"),
    jseg("ibtnR"), "    } else {", jseg("ibtn"), "    }", binds([(P + "ISubA", "isub0"), (P + "ISubD", "isub1"), (P + "ISubI", "isub2"), (P + "IGrow", "grow")]), "    }",
    "    if (this.iCan && this.mine && this.sCan) {", jseg("iseed"), binds([(P + "ISeed", "iseed"), (P + "ISeedB", "iseedb")]), "    }",   # 0.4.8
    "    if (this.aCan && this.mine) {", jseg("iauto"), binds([(P + "IAuto", "iauto")]), "    }",''')
P.rep('''          "public boolean manage;", "public int lostKind;", "public long recArm;", "public String[] xTx;",''',
      '''          "public boolean manage;", "public int lostKind;", "public long recArm;", "public String[] xTx;",
          "public String[] sCol;", "public int[] sSlot;", "public boolean sCan;", "public boolean aCan;", "public String iHub;", "public boolean locked;", "public int nBox;",   # 0.4.8''')
# fill(): 16 islands; the Islands tab = the ladder (box i = tier i + 1); the selected tier's side panel (owned: size / subs / grow / seeds /
# Automation; the next one: its price; later ones: "buy ... first"); the lock card in the strip
P.rep('''  this.cSlot = new int[6]; this.cName = new String[6]; this.cSub = new String[6]; this.cAmt = new String[6];
  this.cAll = new String[6]; this.uTx = new String[7]; this.uCol = new String[7];
  this.cmTx = new String[6]; this.cmTxC = new String[6]; this.tcTx = new String[6]; this.tcTxC = new String[6];
  this.sName = new String[6]; this.sSub = new String[6]; this.iTx = new String[9]; this.iCol = new String[9];
  for (int i = 0; i < 6; i++) { this.cName[i] = ""; this.cSub[i] = ""; this.cAmt[i] = ""; this.cAll[i] = ""; this.sName[i] = ""; this.sSub[i] = ""; this.cmTx[i] = ""; this.cmTxC[i] = "@TEXT@"; this.tcTx[i] = ""; this.tcTxC[i] = "@TEXT@"; }''',
      '''  int NS = @PKG@.ShMath.SLOTS;   // 0.4.8: 16 islands
  this.cSlot = new int[NS]; this.cName = new String[NS]; this.cSub = new String[NS]; this.cAmt = new String[NS];
  this.cAll = new String[6]; this.uTx = new String[7]; this.uCol = new String[7];
  this.cmTx = new String[6]; this.cmTxC = new String[6]; this.tcTx = new String[6]; this.tcTxC = new String[6];
  this.sName = new String[NS]; this.sSub = new String[NS]; this.sCol = new String[NS]; this.sSlot = new int[NS]; this.iTx = new String[9]; this.iCol = new String[9];
  for (int i = 0; i < NS; i++) { this.cName[i] = ""; this.cSub[i] = ""; this.cAmt[i] = ""; this.sName[i] = ""; this.sSub[i] = ""; this.sCol[i] = "@TEXT@"; this.sSlot[i] = -1; }
  for (int i = 0; i < 6; i++) { this.cAll[i] = ""; this.cmTx[i] = ""; this.cmTxC[i] = "@TEXT@"; this.tcTx[i] = ""; this.tcTxC[i] = "@TEXT@"; }
  this.sCan = false; this.aCan = false; this.locked = false;
  this.iHub = "Islands come in tier order - buy each one after the one before it.";''')
P.rep('''  @PKG@.ShStore.LOCK.lock(); try { ownedNow = @PKG@.ShMath.owned(kd, p); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (!ownedNow) this.sum2 = "No " + nm + " Shard yet - " + @PKG@.ShLv20.src(kd, false) + ".";   // 0.4.6''',
      '''  @PKG@.ShStore.LOCK.lock(); try { ownedNow = @PKG@.ShMath.owned(kd, p); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (!ownedNow) this.sum2 = "No " + nm + " Shard yet - " + @PKG@.ShLv20.src(kd, false) + ".";   // 0.4.6
  int lockNeed = kd < @PKG@.ShCfg.LOCK.length ? @PKG@.ShCfg.LOCK[kd] : 0;   // 0.4.8: the lock card (the bridge asked outside the lock)
  int lockLv = lockNeed > 0 ? @PKG@.ShIsl.level(this.me, kd) : -1;
  this.locked = lockNeed > 0 && lockLv >= 0 && lockLv < lockNeed;
  double[] tcv = new double[@PKG@.ShIsl.LADN[kd]];   // 0.4.8: the coin curve at each tier's level (asked outside the lock)
  for (int i = 0; i < tcv.length; i++) tcv[i] = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[@PKG@.ShIsl.LAD0[kd] + i]));
  double acv = @PKG@.ShCfg.curve(@PKG@.ShIsl.stepLv(@PKG@.ShCfg.AUTO_STEP));''')
P.rep('''    for (int i = 0; i < 6; i++) {
      boolean has = @PKG@.ShMath.hasIsland(kd, p, i);
      int sz = has ? @PKG@.ShMath.size(kd, p, i) : 0;
      this.sName[i] = "Slot " + (i + 1) + (has ? " - " + tn : "");
      this.sSub[i] = has ? (sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small")) : "Empty";
      if (!has) continue;''', '''    for (int i = 0; i < NS; i++) {
      boolean has = @PKG@.ShMath.hasIsland(kd, p, i);
      int sz = has ? @PKG@.ShMath.size(kd, p, i) : 0;
      if (!has) continue;''')
P.rep('''      this.cSlot[c] = i;
      this.cName[c] = tn + " Island " + (i + 1) + " - " + this.sSub[i];''', '''      this.cSlot[c] = i;
      this.cName[c] = @PKG@.ShIsl.tname(@PKG@.ShIsl.ty(kd, p, i)) + " Island - " + (sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small"));   // 0.4.8''')
_S0 = P.s.index('''    int s = this.sel < 0 || this.sel > 5 ? 0 : this.sel;
    boolean has = @PKG@.ShMath.hasIsland(kd, p, s);
    if (!has) {
      this.iTitle = "Slot " + (s + 1) + " - empty";''')
_S1 = P.s.index('''  } finally { @PKG@.ShStore.LOCK.unlock(); }
  long per = (long) @PKG@.ShCfg.xpOf(kd);''', _S0)
P.rep(P.s[_S0:_S1], '''    // 0.4.8: the ladder boxes (box i = tier i + 1 of this shard) + the selected tier's panel
    int nl = @PKG@.ShIsl.LADN[kd];
    this.nBox = nl;
    int nx = @PKG@.ShIsl.nextTier(kd, p);
    boolean autoN = @PKG@.ShIsl.auto(kd, p);
    for (int i = 0; i < NS; i++) {
      if (i >= nl) continue;
      int t = @PKG@.ShIsl.LAD0[kd] + i;
      int sl = @PKG@.ShIsl.slotOf(kd, p, t);
      this.sSlot[i] = sl;
      this.sName[i] = @PKG@.ShIsl.tname(t);
      if (sl >= 0) {
        int sz = @PKG@.ShMath.size(kd, p, sl);
        this.sSub[i] = (sz >= 3 ? "Large " : (sz == 2 ? "Medium " : "Small ")) + @PKG@.ShIsl.sub(p, kd, sl, 0) + "/" + @PKG@.ShIsl.sub(p, kd, sl, 1) + "/" + @PKG@.ShIsl.sub(p, kd, sl, 2);
        this.sCol[i] = "@GOOD@";
      } else if (i == nx) { this.sSub[i] = "Buy next"; this.sCol[i] = "@GOLD@"; }
      else { this.sSub[i] = "Locked"; this.sCol[i] = "@TEXT@"; }
    }
    int s = this.sel < 0 || this.sel >= nl ? 0 : this.sel;
    int ts = @PKG@.ShIsl.LAD0[kd] + s;
    int sl = @PKG@.ShIsl.slotOf(kd, p, ts);
    String auTxt = "";
    if (!autoN && ownedNow) {
      long ac = @PKG@.ShIsl.coins(@PKG@.ShIsl.stepH(@PKG@.ShCfg.AUTO_STEP), acv);
      Object[] am = @PKG@.ShIsl.mats(kd, @PKG@.ShIsl.LAD0[kd], @PKG@.ShCfg.AUTO_ITEMS[kd], 0, 1L);
      auTxt = "Automation (manual now): " + @PKG@.ShCfg.num(ac) + " coins" + (((String[]) am[0]).length > 0 ? " + " + @PKG@.ShIsl.matsText(am) : "");
      this.aCan = true;
    }
    if (sl >= 0) {
      int sz = @PKG@.ShMath.size(kd, p, sl);
      double r = @PKG@.ShMath.rate(kd, p, sl, now);
      this.iTitle = @PKG@.ShIsl.tname(ts) + " Island - " + (sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small"));
      this.iTx[0] = "Makes " + perHour(r) + " items / hour - " + (autoN ? "Automated" : "Manual phase (" + @PKG@.ShCfg.MAN_PCT + " %)");
      this.iCol[0] = autoN ? "@GOOD@" : "@WARN@";
      this.iTx[1] = "Totems: " + @PKG@.ShMath.totems(kd, p, sl) + " of " + @PKG@.ShMath.pads(sz) + " pads (Totems tab) - upgrades +" + @PKG@.ShCfg.dec((@PKG@.ShIsl.mult(kd, p, sl, sz) - 1.0) * 100.0) + " %";
      boolean all5 = true;
      for (int w = 0; w < 3; w++) {
        int lv = @PKG@.ShIsl.sub(p, kd, sl, w);
        if (lv < 5) all5 = false;
        String nm2 = @PKG@.ShIsl.subName(kd, w);
        if (lv >= 5) { this.iTx[2 + w] = nm2 + " 5/5" + (sz >= 3 ? " - highest" : " - grow to go on"); this.iCol[2 + w] = "@GOLD@"; continue; }
        long sc = @PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, lv + 1), tcv[s]);
        String tm = w == 0 ? @PKG@.ShCfg.MAT_AMT : (w == 1 ? @PKG@.ShCfg.MAT_DECO : @PKG@.ShCfg.MAT_IRR);
        Object[] sm = @PKG@.ShIsl.mats(kd, ts, tm, sz - 1, (long) (lv + 1));
        this.iTx[2 + w] = nm2 + " " + lv + "/5 - next: " + @PKG@.ShCfg.num(sc) + " coins" + (((String[]) sm[0]).length > 0 ? " + " + @PKG@.ShIsl.matsText(sm) : "");
        this.iCol[2 + w] = (purse < 0L || purse >= sc) && (cs == null || haveAll(new Object[] { sm[0], sm[1], Long.valueOf(0L) }, cs)) ? "@GOOD@" : "@BAD@";
      }
      if (sz >= 3) { this.iTx[5] = "Fully grown."; this.iCol[5] = "@GOLD@"; }
      else if (!all5) { this.iTx[5] = "Grow to " + (sz == 1 ? "Medium" : "Large") + ": max all 3 upgrades first"; this.iCol[5] = "@BAD@"; }
      else {
        long gc = @PKG@.ShIsl.coins(@PKG@.ShIsl.growH(sz + 1), tcv[s]);
        Object[] gm = @PKG@.ShIsl.mats(kd, ts, @PKG@.ShCfg.MAT_GROW, sz - 1, 1L);
        this.iTx[5] = "Grow to " + (sz == 1 ? "Medium" : "Large") + ": " + @PKG@.ShCfg.num(gc) + " coins" + (((String[]) gm[0]).length > 0 ? " + " + @PKG@.ShIsl.matsText(gm) : "");
        this.iCol[5] = (purse < 0L || purse >= gc) && (cs == null || haveAll(new Object[] { gm[0], gm[1], Long.valueOf(0L) }, cs)) ? "@GOOD@" : "@BAD@";
      }
      boolean seedy = !autoN && ("farm".equals(@PKG@.ShIsl.STYLE[kd]) || @PKG@.ShIsl.trees(kd)) && @PKG@.ShIsl.SEED[ts].length() > 0;
      if (seedy) {
        this.iTx[6] = "Seed store: " + @PKG@.ShIsl.seeds(kd, p, sl) + " " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.SEED[ts]) + ("farm".equals(@PKG@.ShIsl.STYLE[kd]) ? " - " + @PKG@.ShIsl.eternal(kd, p, sl) + " Eternal cells" : "");
        this.sCan = true;
      } else this.iTx[6] = autoN ? "Automated - nothing to replant." : "Ore regrows by itself.";
      this.iTx[7] = auTxt.length() > 0 ? auTxt : "Automated - every island of this shard works by itself.";
      this.iCol[7] = auTxt.length() > 0 ? "@WARN@" : "@GOOD@";
      this.iTx[8] = this.locked ? "Locked - reach " + @PKG@.ShIsl.skillWord(kd) + " " + lockNeed + " to use it." : "";
      this.iCol[8] = "@BAD@";
      this.iCan = true;
    } else {
      this.iTitle = @PKG@.ShIsl.tname(ts) + " Island";
      if (!ownedNow) { this.iTx[0] = "No " + nm + " Shard yet."; this.iTx[1] = "Its door is on your starter islands."; }
      else if (s != nx) { this.iTx[0] = nx < 0 ? "Every island is yours." : "Buy the " + @PKG@.ShIsl.tname(@PKG@.ShIsl.LAD0[kd] + nx) + " island first."; this.iCol[0] = "@BAD@"; this.iTx[1] = "Islands come in tier order."; }
      else {
        long bc = @PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, tcv[s]);
        Object[] bm2 = @PKG@.ShIsl.mats(kd, ts, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L);
        this.iTx[0] = "Makes " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.PROD[ts]) + " - a Small island, its own upgrades.";
        this.iTx[1] = "It makes items once a worker totem stands on it.";
        this.iTx[3] = "Cost";
        this.iTx[4] = have(purse, bc, "coins");
        this.iCol[4] = (purse < 0L || purse >= bc) ? "@GOOD@" : "@BAD@";
        String[] bi = (String[]) bm2[0];
        long[] bq = (long[]) bm2[1];
        for (int j = 0; j < bi.length && j < 3; j++) {
          long hb = @PKG@.ShInv.count(cs, bi[j]);
          this.iTx[5 + j] = have(cs == null ? -1L : hb, bq[j], @PKG@.ShTotem.pretty(bi[j]));
          this.iCol[5 + j] = (cs != null && hb >= bq[j]) ? "@GOOD@" : "@BAD@";
        }
        this.bCan = true;
      }
      this.iTx[8] = auTxt;
      this.iCol[8] = "@WARN@";
    }
''')
P.rep('''  this.sum1 = islands + (islands == 1 ? " island - " : " islands - ") + totems + (totems == 1 ? " totem - " : " totems - ") + perHour(rate) + " items / hour";''',
      '''  this.sum1 = islands + (islands == 1 ? " island - " : " islands - ") + totems + (totems == 1 ? " totem - " : " totems - ") + perHour(rate) + " items / hour";
  if (this.locked) {   // 0.4.8: the lock card (Style Guide 15: red = what you still need)
    this.sum1 = nm + " Shard - locked";
    this.sum2 = "Reach " + @PKG@.ShIsl.skillWord(kd) + " " + lockNeed + " to open it. You: " + @PKG@.ShIsl.skillWord(kd) + " " + lockLv + ".";
  }''')
P.rep('''  if (anyFull) { this.sto2 = "An island is FULL - collect now"; this.sto2c = "@BAD@"; }''',
      '''  if (this.locked) { this.sto2 = "Locked - look, don't touch"; this.sto2c = "@BAD@"; }
  else if (anyFull) { this.sto2 = "An island is FULL - collect now"; this.sto2c = "@BAD@"; }''')
# fillTotems: the selected TIER's island (its slot), 16 islands
P.rep('''  int s = this.sel < 0 || this.sel > 5 ? 0 : this.sel;
  if (p != null && !@PKG@.ShMath.hasIsland(kd, p, s)) { for (int i = 0; i < 6; i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) { s = i; break; } }''',
      '''  int s = p == null ? 0 : @PKG@.ShIsl.slotOf(kd, p, @PKG@.ShIsl.LAD0[kd] + (this.sel < 0 || this.sel >= @PKG@.ShIsl.LADN[kd] ? 0 : this.sel));   // 0.4.8: box = tier
  if (s < 0) s = 0;
  if (p != null && !@PKG@.ShMath.hasIsland(kd, p, s)) { for (int i = 0; i < @PKG@.ShMath.SLOTS; i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) { s = i; break; } }''')
P.rep('''    this.tCap = "Island " + (s + 1) + " - " + @PKG@.ShKind.TNAME[kd] + " " + (sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small")) + " - " + e.length''',
      '''    this.tCap = @PKG@.ShIsl.tname(@PKG@.ShIsl.ty(kd, p, s)) + " " + (sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small")) + " - " + e.length''')
# act(): two-digit boxes / rows; the new buttons
P.rep('''  if (a.startsWith("slot")) { int s = a.length() > 4 ? (int) (a.charAt(4) - '0') : 0; if (s >= 0 && s <= 5) { this.sel = s; this.tpad = 0; } return ""; }''',
      '''  if (a.startsWith("slot")) { int s = -1; try { s = Integer.parseInt(a.substring(4)); } catch (Throwable x) { s = -1; } if (s >= 0 && s < @PKG@.ShMath.SLOTS) { this.sel = s; this.tpad = 0; } return ""; }   // 0.4.8: 16 boxes''')
P.rep('''    if (a.startsWith("col")) {
      int r = a.length() > 3 ? (int) (a.charAt(3) - '0') : -1;''', '''    if (a.startsWith("col")) {
      int r = -1;
      try { r = Integer.parseInt(a.substring(3)); } catch (Throwable x) { r = -1; }   // 0.4.8: up to 16 rows''')
P.rep('''    if (a.equals("grow")) return @PKG@.ShCore.grow(u, k, kd, this.sel, invOf(ref, st));
    if (a.equals("ibuy")) return @PKG@.ShCore.buyIsland(u, k, kd, this.sel, invOf(ref, st));   // 0.4.6''',
      '''    if (a.equals("grow") || a.startsWith("isub") || a.equals("iseed") || a.equals("iseedb")) {   // 0.4.8: the selected tier's island
      @IC@[] cs8 = invOf(ref, st);
      fill(k, cs8);
      int sl8 = this.sSlot == null || this.sel < 0 || this.sel >= this.sSlot.length ? -1 : this.sSlot[this.sel];
      if (sl8 < 0) return "-That island is not yours yet.";
      if (a.equals("grow")) return @PKG@.ShCore.grow(u, k, kd, sl8, cs8);
      if (a.equals("iseed")) return @PKG@.ShCore.seedsGive(u, k, kd, sl8, cs8);
      if (a.equals("iseedb")) return @PKG@.ShCore.seedsTake(u, k, kd, sl8, cs8);
      int w8 = a.length() > 4 ? (int) (a.charAt(4) - '0') : -1;
      return @PKG@.ShCore.buySub(u, k, kd, sl8, w8, cs8);
    }
    if (a.equals("iauto")) return @PKG@.ShCore.buyAuto(u, k, kd, invOf(ref, st));   // 0.4.8
    if (a.equals("ibuy")) return @PKG@.ShCore.buyIsland(u, k, kd, this.sel, invOf(ref, st));   // 0.4.6; 0.4.8: the box = the tier''')
# the lock's one chat line when the menu opens
P.rep('''  String no = pg.openGate(wn);
  if (no == null) return pg;''', '''  String no = pg.openGate(wn);
  if (no == null) {
    if (pg.view == 0 && pr != null) { String lk = @PKG@.ShIsl.lockMsg(u, pg.kind); if (lk != null) @PKG@.ShSay.to(pr, "[Shards] " + lk, "@BAD@"); }   // 0.4.8
    return pg;
  }''')
P.rep('''  pg.stText = no;
  return null;
}""".replace("@INFO@", INFO))''', '''  pg.stText = no;
  return null;
}""".replace("@INFO@", INFO).replace("@BAD@", BAD))''')
P.rep('''] + ["    if (this.sel == %d) {\\n%s\\n    } else {\\n%s\\n    }\\n%s" % (i, jseg("islot%ds" % i), jseg("islot%dn" % i), binds([(P + "ISl%dSel" % i, "slot%d" % i)]))
     for i in range(SLOTS)] + [''', '''] + ["    if (this.nBox > %d) {\\n    if (this.sel == %d) {\\n%s\\n    } else {\\n%s\\n    }\\n%s\\n    }" % (i, i, jseg("islot%ds" % i), jseg("islot%dn" % i), binds([(P + "ISl%dSel" % i, "slot%d" % i)]))
     for i in range(SLOTS)] + [   # 0.4.8: only the shard's ladder (Mining 11, Orchard / Ranching 8 ...)''')

# ================================================================================================ shard:fn:door (spec 5) + the plugin
P.rep('''# ================= plugin =================
pl = mk("SkyyShardsPlugin", T["JP"])''', '''# ================= 0.4.8 shard:fn:door (spec 5): SkyyIslands 0.5.25 places the Skyy_Shard_<Kind> block on its starter island and calls this.
# Object[]{ UUID owner, String pkey, String kind, String world, Integer x, Integer y, Integer z } -> "+" recorded (the door is the shard's
# placed portal now) / "+kept" (recorded beside a portal the player placed on this island) / "=" already known / "-..." refused. The shard
# gets its T1 island (manual phase) if it has none. Any thread (it reads the islands bridge and writes the profile's shard file).
dfn = mk("ShDoor", None, ("java.util.function.Function",))
F(dfn, "public static final java.util.concurrent.atomic.AtomicLong DOORS = new java.util.concurrent.atomic.AtomicLong();")
C(dfn, "public ShDoor() { }")
M(dfn, r"""
public static String door(java.util.UUID owner, String pkey, String kind, String world, int x, int y, int z) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  int kd = kind == null ? -1 : @PKG@.ShKind.ofKey(kind);
  if (kd < 0) return "-Unknown shard " + kind + ".";
  if (!@PKG@.ShStore.validKey(pkey)) return "-Bad profile key.";
  if (world == null || world.length() == 0 || @PKG@.ShWorlds.isShard(world)) return "-A shard door goes on an island.";
  String io = @PKG@.ShRole.islandOwner(world);
  if (io != null && !io.equals(pkey)) return "-That island belongs to another profile.";
  java.util.Properties p = @PKG@.ShStore.get(pkey);
  if (p == null) return "-The shard file of " + pkey + " could not be read.";
  String where = world + "|" + x + "|" + y + "|" + z;
  long now = System.currentTimeMillis();
  boolean take = false;
  @PKG@.ShStore.LOCK.lock(); try {
    String dk = @PKG@.ShMath.kk(kd, "door.starter");
    String pk = @PKG@.ShMath.kk(kd, "placed");
    String door = @PKG@.ShStore.str(p, dk);
    String placed = @PKG@.ShStore.str(p, pk);
    if (where.equals(door) && where.equals(placed) && @PKG@.ShMath.owned(kd, p)) return "=";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    take = placed.length() == 0 || placed.equals(door) || @PKG@.ShRole.stale(placed, pkey);
    @PKG@.ShMath.starter(kd, p, now);
    p.setProperty(dk, where);
    if (take) {
      @PKG@.ShMath.settleAll(kd, p, now);   // a paused (picked-up) shard made nothing meanwhile: its clocks start now
      p.remove(@PKG@.ShMath.kk(kd, "paused"));
      p.setProperty(pk, where);
    }
    String e = @PKG@.ShStore.save(pkey, p);
    if (e != null) { p.clear(); p.putAll(old); @PKG@.ShCfg.warn("the " + kind + " door of " + pkey + " was not saved: " + e); return "-The shard file could not be saved."; }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  DOORS.incrementAndGet();
  @PKG@.ShStore.log((owner == null ? "-" : owner.toString()) + " " + pkey + " " + @PKG@.ShKind.KEYS[kd] + " starter door " + where + (take ? "" : " (a placed portal on this island is kept)"));
  return take ? "+" : "+kept";
}""")
M(dfn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return "-Bad call: Object[]{ UUID, String pkey, String kind, String world, Integer x, y, z }.";
    Object[] a = (Object[]) o;
    if (a.length < 7 || !(a[1] instanceof String) || !(a[2] instanceof String) || !(a[3] instanceof String) || !(a[4] instanceof Number) || !(a[5] instanceof Number) || !(a[6] instanceof Number))
      return "-Bad call: Object[]{ UUID, String pkey, String kind, String world, Integer x, y, z }.";
    java.util.UUID u = a[0] instanceof java.util.UUID ? (java.util.UUID) a[0] : null;
    return door(u, (String) a[1], (String) a[2], (String) a[3], ((Number) a[4]).intValue(), ((Number) a[5]).intValue(), ((Number) a[6]).intValue());
  } catch (Throwable t) { @PKG@.ShCfg.warn("shard:fn:door failed: " + t); return "-The door could not be recorded (server log)."; }
}""")

# ================= plugin =================
pl = mk("SkyyShardsPlugin", T["JP"])''')
P.rep('''  b.put("shard:fn:give", new @PKG@.ShGiveFn());   // fix2: the quest bridge (one shard per kind, ever)''',
      '''  b.put("shard:fn:give", new @PKG@.ShGiveFn());   // fix2: the quest bridge (one shard per kind, ever)
  b.put("shard:fn:door", new @PKG@.ShDoor());   // 0.4.8: SkyyIslands 0.5.25's starter islands record their shard doors''')
P.rep('''  @PKG@.ShCfg.info("bridge: shard:fn:allowed / world / totem / give (0.4: no SkyWynn Menu route - a shard menu opens only from its portal)");''',
      '''  @PKG@.ShCfg.info("bridge: shard:fn:allowed / world / totem / give / door (0.4: no SkyWynn Menu route - a shard menu opens only from its portal)");''')
P.rep('''  try { b.remove("shard:fn:allowed"); b.remove("shard:fn:world"); b.remove("shard:fn:totem"); b.remove("shard:fn:give"); b.remove("shard:version"); } catch (Throwable t) { }''',
      '''  try { b.remove("shard:fn:allowed"); b.remove("shard:fn:world"); b.remove("shard:fn:totem"); b.remove("shard:fn:give"); b.remove("shard:fn:door"); b.remove("shard:version"); } catch (Throwable t) { }''')
P.rep('''ALLC = [cfg, smig, smig45, smig46, st, knd, lv, tot,''', '''ALLC = [cfg, smig, smig45, smig46, smig48, st, knd, isl48, lv, tot,''')
P.rep('''+ [admc, gfn, pl]   # 0.4: + ShSoil, ShRain, ShHand''', '''+ [admc, gfn, dfn, pl]   # 0.4.8: + ShMig048, ShIsl, ShDoor   # 0.4: + ShSoil, ShRain, ShHand''')

P.rep('''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4: ONE MENU PER SHAR''', '''log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.8: STARTER SHARD DOORS (shard:fn:door, level-5 locks), one island per tier (Size + Amount / Decorations / Irrigation, cheap-first ladder), manual first until Automation, Mining copper caves; 0.4: ONE MENU PER SHAR''')
P.rep('''  if (kd < 0 || kd >= SKILL.length || n <= 0) return cap ? "An admin can give you one" : "an admin can give you one";''',
      '''  if (kd < 0 || kd >= SKILL.length || n <= 0) return cap ? "Its door is on your starter islands" : "its door is on your starter islands";   // 0.4.8''')

# ---- the region's plain blocks: one entry per cell (the LAST wins - a bridge end under an island's rim was painted twice every Enter);
# the 0.4.7 / 0.4.8 special cells keep their order
P.rep("""# everything the profile's region of kind kd wants, in paint order (hub, bridges, islands - a later block wins its position)""",
      """# 0.4.8: one plain block per cell - the last one wins (it used to be painted twice: plank then grass, every Enter); special cells stay
M(geo, r\"\"\"
public static java.util.ArrayList dedupe(java.util.ArrayList out) {
  java.util.HashMap last = new java.util.HashMap();
  for (int i = 0; i < out.size(); i++) {
    int[] b = (int[]) out.get(i);
    if (b[3] >= 0) last.put(b[0] + "," + b[1] + "," + b[2], Integer.valueOf(i));
  }
  java.util.ArrayList res = new java.util.ArrayList(last.size() + 64);
  for (int i = 0; i < out.size(); i++) {
    int[] b = (int[]) out.get(i);
    if (b[3] < 0) { res.add(b); continue; }
    Object li = last.get(b[0] + "," + b[1] + "," + b[2]);
    if (li != null && ((Integer) li).intValue() == i) res.add(b);
  }
  return res;
}\"\"\")
# everything the profile's region of kind kd wants, in paint order (hub, bridges, islands - a later block wins its position)""")
P.rep("""  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) pads(out, kd, p, i);   // 0.2: the totems on their pads
  return out;""", """  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(kd, p, i)) pads(out, kd, p, i);   // 0.2: the totems on their pads
  return dedupe(out);   // 0.4.8""")

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0
P.finish()
