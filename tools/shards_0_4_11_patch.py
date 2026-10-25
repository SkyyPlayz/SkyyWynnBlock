"""Derive SkyyShards/build_skyyshards_0.4.11.py from the GENERATED SkyyShards 0.4.10 (build_skyyshards_0.4.10.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_10_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.10 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_11_patch.py   then   python SkyyShards/build_skyyshards_0.4.11.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.11.py

0.4.11 (2026-10-24) = THE COMBAT SHARD: ONE ISLAND PER ZONE (starter archipelago round R5; research/Starter-Archipelago-Spec.md section 10 +
  section 16 row R5). Skyy's words (docs/answered/world.md 2026-10-23 SHARD UPGRADE MAP): "except the combat shards because mobs dont have
  tiers. so the combat shard will have an island per zone. and you can lvl up how man ymobs spawn at once, how high of lvl the mobs are, and
  how fast they spawn. each island upgrade makes the island bigger, and adds more mob options to the pool. at max lvl zone 1 combat shard
  island will have an upper portion for all the mobs that appear above ground, and a lover section mottled after the deep caverns with the
  mobs that appear in those deep caves. (its always night on the combat shard, and the mobs that spawn at night spawn there too.)" + "Start
  the next queued rounds from RESUME (..., R5 Combat shard islands)." Built on top of the 0.4.10 hotfix (status line after base2, kShown).
  1. ZONE ISLANDS (spec 10): the Combat ladder is Zone 1 .. Zone 5 (Zone 1 = the old skeleton island, its key "skeleton" kept, so every
     Combat island owned today IS Zone 1; Zones 2-5 = keys zone2 .. zone5). They sit on the shard's inner ring like every other shard's
     islands (the 0.4.x hexagon places, 60 degrees apart - the map mirrors the world; spec 10's "72-degree steps" would move the
     shard-world places every other shard uses: DECISION, the existing ring kept). Buying is in order (the 0.4.8 buy flow, map Buy view):
     coins = isl.buyHours at the zone's COST tier (spec 13.2: Zone 1 at T2 numbers, Zone N at P7_MID_T 2 / 5 / 8 / 11 / 14) + 64 of the
     zone's common mob drop (isl.buyItems.combat "raw:64": Bone Fragments / Medium Hide / Ice Essence / Cindercloth Scrap / Fire Essence)
     and Zone N needs CLASS level combat.zoneLevel.N (20 / 40 / 60 / 80 = 20 x (N - 1)); the map captions say "Zone N" (no tier tag).
  2. THE THREE COMBAT SUB-UPGRADES (spec 10 table; 5 levels per size, the same max-then-grow rule; saved in the 0.4.8 keys amt / deco / irr):
     Mobs at once (Small 3..8, Medium 8..12, Large 12..18, split upper / lower), Mob level (inside the zone's band: Zone 1 Small Lv 1-3 ..
     5-8, Medium 5-8 .. 10-13, Large 10-13 .. 16-20; Zone N adds combat.levelOffset 0 / 20 / 40 / 60 / 80), Spawn speed (respawn seconds:
     Small 30 .. 15, Medium 15 .. 10, Large 10 .. 6). Costs = the 0.4.8 sub hours at the zone's cost tier + combat.mat.cap / level / speed
     (the zone's drop + Void / Life / Water Essence, x the level bought). Each level also adds the 0.4.9 +3 % to the Soul Cage's output,
     and (fix, critic r5combat2 2nd round - spec 10 "the Soul Cage also kills ... using the pool, the mob level and the spawn speed") Mobs
     at once x Spawn speed raise it more: up to combat.spawnBonus (40) % at the top (Large 18 mobs / 6 s), by the log share of the spawn
     rate in between (a new island x1, Small 5/5 + 5/5 x1.18).
  3. SIZE ADDS MOBS + LAND (spec 10): Small = a plains arena of the zone's ground (Zone 1 grass, 2 sand, 3 cold grass, 4 ash, 5 cooled
     magma) with torches; Medium + a forest edge (the zone's trees) and a rocky rise; Large + a swamp / oasis / snow / gravel / lava-rock
     corner AND THE LOWER PART: a 23 x 23 x 9 cavern under the island in the deep-caverns look (the zone's rock, 4 pillars, crystals,
     glowing lava rock, torches) reached by a spiral stair with a fence around its top (in the island's free quarter, never on a bridge's
     walkway). Pools (vanilla role ids, every one read from Assets.zip at BUILD time and found in that zone's own vanilla spawn files):
     Small = the zone's plains / tier-1 mobs + the tier-1 NIGHT void mobs (Larva / Crawler / Eye), Medium + its tier-2 mobs, Large upper
     + its tier-3 mobs (Zone 1: Snake_Marsh, Fen_Stalker, Skeleton_Mage, Void_Spectre), Large lower = the zone's cave mobs (Zone 1:
     goblins scrapper / lobber / miner / burner, rats, cave spiders, magma toads, Golem_Firesteel, mineshaft skeletons). Goblin "hermit"
     (spec) is not a vanilla role - left out. Server Setup -> Shards -> Combat islands: combat.pool.<zone>.<small|medium|large|lower>.
  4. ALWAYS NIGHT (spec 10, combat.nightHold): a player standing in the Combat region of a shard world gets the world's time settings with
     the clock paused + the game time of the next midnight (UpdateTimeSettings + UpdateTime, the packets WorldTimeResource itself sends),
     again every second; fix (critic r5combat2): the vanilla TimePacketSystem broadcasts the world's real UpdateTime every second, so an
     outbound PlayerPacketFilter (ShNightF, SkyyEssentials' proven PacketAdapters.registerOutbound path) DROPS the world's own UpdateTime /
     UpdateTimeSettings for exactly the players we hold at night (same world, our packet sent < 3.5 s ago; ours pass by a ThreadLocal mark);
     leaving the region (another shard's region of the same world) releases the hold first, then sends the world's real time back
     (WorldTimeResource.sendTimePackets); another world sends its own on join. The shard world's clock is NEVER changed (the other five
     shards share that world, crops grow by it, SkyyIslands keeps it in step with the hub). Night-only vanilla spawns do not exist in a
     shard world (no natural spawning), so the night void mobs are simply part of every pool.
  5. THE SPAWNER (manual phase AND Automated; ShFight, the world thread, every second): mobs spawn ONLY while an owner / co-op member stands
     on that island (that part: upper or the cavern), up to "Mobs at once" alive, one per island a second while filling, then each dead
     mob's place comes back after "Spawn speed" seconds; SkyyMobs mob:fn:setLevel gives each its level (Mob level range + the zone offset;
     no SkyyMobs = vanilla level - no SkyyMobs change needed); NPCPlugin.spawnNPC (the SkyyIslands camp's proven call). SAFETY: never
     closer than combat.minDist (6) blocks to ANY player, only on our own floor with 2 free blocks above; a mob that leaves its island
     (8 blocks past the rim, 22 below, 30 above) is removed (no drops) - nothing escapes into the rest of the shard world; nobody on an
     island for 30 s = its mobs are removed; mobs left in the chunks by a restart are found (their pool role inside the island box) and
     counted, above the cap removed. NO AFK FARM: an island spawns only while a member there has MOVED 1.5 blocks in combat.afkSec (300 s),
     and every combat island of a profile together spawns at most combat.maxPerHour (300 = 2 x the balance model's 150 open-world kills
     an hour) mobs an hour (token bucket) at Small level 0 - fix (critic r5combat2 2nd round: a flat 300 made Mobs at once + Spawn speed
     pointless) the bucket refills at that x the island's spawn rate vs Small level 0 (mobs at once / respawn: up to x30), so the real
     limit is how fast the player kills. The spawner picks each mob by its VANILLA SPAWN ODDS in that zone (fix, critic: rare vanilla mobs
     stay rare). Manual kills are ordinary vanilla kills: drops (SkyySacks' auto-pickup puts mob drops into the
     Combat bag - Sacks 0.8.29's rule), kill XP, SkyyMobs levels. shard:fn:allowed now answers "hurt" with yes (SkyyIslands 0.5.8 asked it
     for every hit on an NPC in a shard world and got no - nobody could have hit a shard mob) - fix (critic): ONLY for an attacker the
     combat tick saw in that world's Combat region within the last 3 s (ShCombat.HERE); an NPC anywhere else in a shard world stays safe.
  6. THE SOUL CAGE ON THE POOL (spec 10, Automated or manual at shard.manualPct): the lazy maths of 0.4.x, but Collect gives the island's
     mob pool's drops instead of only Bone Fragments: the stored count is split over the vanilla drop items of every pool role in the mix
     an even fight of that pool gives (each role's items at their average count a kill, build-time from its DropList; armor / weapons left
     out), whole numbers by largest remainder; a pool without known drops gives the zone's common drop. Still no XP at Collect (Skyy G9).
     Fix (critic): a full inventory never picks the drops - when not all fit, the player keeps EXACTLY the mix of the largest count that
     fitted (the extra taken back, counted), the rest stays stored as a count; that part must hold every kind of the full take (fix, 2nd
     round: else one free slot handed out only the most common drop, Collect after Collect) - else nothing ("a free slot each").
     Fix (critic r5combat2 2nd round, coins): each role's drops count at its vanilla spawn odds, and combat.cageSkip items never come from a
     Soul Cage (Void Essence / Voidheart - the night void mobs' drops, the Mobs at once + Time Compressor material - and ingots, ores,
     crystals, stone: no Mining collection from a combat Collect); they come from fighting. A new Zone 1 Small island's Soul Cage I then
     sells for ~1x its 0.4.10 Bone Fragments at the live Bazaar prices (with Void Essence: ~8x). The mix follows the island's size at
     Collect time (growing just before a Collect re-mixes what was stored: at most two grows per island, a one-off - accepted, noted).
     BALANCE (fix, critic: Skyy 2026-10-24 SHARD UPGRADE BONUS "new islands stay the same. max islands out put should far exceed player
     productivity" wins over the round brief's "must not out-earn by much"): an arena has no crop tiles, so a Soul Cage's rate never grows
     with its range or the island's area (0.4.10's reach would give a maxed Large ~14x fighting); each Soul Cage works at its tier's
     worker speed. RETUNE (Skyy 2026-10-24 popup COMBAT SHARD PACE: "how much should a MAXED combat island make compared to fighting that
     zone yourself (per hour)?" -> "About 1-1.5x (Recommended)" - it replaces the first build's ~2.5-7x): one number could not do it (at
     100 % the zones spread 2.5-7x, wider than the 1.5x window, and a flat cut would also cut today's owned Zone 1 islands), so the
     island's rate r goes through combat.cageGrowth (54 %): above one Soul Cage I's speed r0 it becomes r0 x (r / r0) ^ 0.54 (at or
     below r0 - a new island, the manual phase - nothing changes; every cage, upgrade and grow still adds), then x combat.cagePct of its
     zone (100 / 68 / 39 / 82 / 68). The Time Compressor is NOT squeezed (x2 on every shard, as its menu says) - it is part of the target:
     a FULLY maxed Large (5 Soul Cages of the zone's tier, every sub 5/5, Time Compressor III) = 1.23-1.26x the COINS of fighting that
     zone yourself (150 kills / h, balance_model KILLS_H; the live Bazaar prices), 0.62-0.63x without the compressor, 5 Soul Cage V +
     TC III 1.26-1.42x; a new Small island 0.001-0.13x (Zone 1 = exactly 0.4.10). Numbers: harness phase BAL.
  NOT IN THIS ROUND: multi-block vanilla set pieces; elite / boss spawns on the islands; Soul Orbs feeding the cage per kill.
  SAVED DATA: none new (combat.i<n>.type zone2..zone5 for bought zones; the sub levels in the 0.4.8 keys - on purpose, no reset: a Zone 1
  island's Amount / Decorations / Irrigation levels bought before 0.4.11 (same coin hours) now read as Mobs at once / Mob level / Spawn
  speed - nothing is lost, only gained). No migration; the 0.4.8 map migration (migrate2) now leaves Combat islands' types alone (fix,
  critic: a profile not loaded since 0.4.6 / 0.4.7 would have had its extra Skeleton islands renamed Zone 2-5 for free). Config: new rows
  only (Server Setup -> Shards -> Combat islands); an existing config.properties without them reads the defaults.
  ROLLBACK 0.4.11 -> 0.4.10: alone, but a profile that BOUGHT Zone 2-5 then has islands 0.4.10 reads as its one Combat type (they make
  Bone Fragments); no file change needed. Mobs alive in a combat island at the rollback stay as ordinary mobs until killed.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.10.py"), os.path.join(HERE, "build_skyyshards_0.4.11.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.10"\n') and P.has("GENERATED by tools/shards_0_4_10_patch.py") and not P.has("ShFight"), "not the generated SkyyShards 0.4.10"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
KINDS_COMBAT = 5   # KINDS.index("Combat") in the build script (asserted there: KINDS[5] == "Combat")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.11 (2026-10-24)"):].rstrip() + "\n"

P.rep('''"""SkyyShards 0.4.10 - build script (javassist via jpype). GENERATED by tools/shards_0_4_10_patch.py from build_skyyshards_0.4.9.py
(generated by tools/shards_0_4_9_patch.py from 0.4.8, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.10" / "0.4.9" / "0.4.8" / "0.4.7" / "0.4.6" / "0.4.5" / "0.4.4" / "0.4.3" / "0.4.2" / "0.4.1" / "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.10.py   -> SkyyShards/SkyyShards-0.4.10.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.10.py
''', '''"""SkyyShards 0.4.11 - build script (javassist via jpype). GENERATED by tools/shards_0_4_11_patch.py from build_skyyshards_0.4.10.py
(generated by tools/shards_0_4_10_patch.py from 0.4.9, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.11" / "0.4.10" / "0.4.9" / "0.4.8" / "0.4.7" / "0.4.6" / "0.4.5" / "0.4.4" / "0.4.3" / "0.4.2" / "0.4.1" / "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.11.py   -> SkyyShards/SkyyShards-0.4.11.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.11.py
''' + NOTE + '''
0.4.10 notes:
''')
P.rep('VERSION = "0.4.10"\n', 'VERSION = "0.4.11"\n')

# ---------------------------------------------------------------------------------------------------- 1. the Combat ladder = 5 zones (build time)
P.rep('''# Combat (5): today's skeleton island only (the zone islands are round R5)
_ty48(5, "skeleton", "Skeleton", 1, "Ingredient_Bone_Fragment")
assert [len(_l) for _l in LAD] == [11, 15, 15, 8, 8, 1], [len(_l) for _l in LAD]''', '''# Combat (5): 0.4.11 R5 THE COMBAT SHARD - ONE ISLAND PER ZONE (spec 10; Skyy 2026-10-23: "the combat shard will have an island per zone").
# Zone 1 = the old skeleton island (its key kept: every Combat island owned today is Zone 1), Zones 2-5 bought in order. tier = the island's
# COST tier (spec 13.2: Zone 1 at T2 numbers, Zone N at P7_MID_T); prod = the zone's common mob drop (the buy items "raw:64" + the Soul Cage's
# fallback when a pool has no known drops)
CZ_N = 5
CZ_TIER = list(_BM48.P7_MID_T)
assert CZ_TIER == [2, 5, 8, 11, 14], CZ_TIER
CZ_DROP = ["Ingredient_Bone_Fragment", "Ingredient_Hide_Medium", "Ingredient_Ice_Essence", "Ingredient_Fabric_Scrap_Cindercloth", "Ingredient_Fire_Essence"]
for _z in range(CZ_N):
    _ty48(5, "skeleton" if _z == 0 else "zone%d" % (_z + 1), "Zone %d" % (_z + 1), CZ_TIER[_z], CZ_DROP[_z])
assert [len(_l) for _l in LAD] == [11, 15, 15, 8, 8, 5], [len(_l) for _l in LAD]
# the pools (spec 10 "each island upgrade ... adds more mob options to the pool"): per zone the roles a size ADDS (Small | Medium | Large
# upper) + the deep-cavern part (Large only). Vanilla role ids; each one must be a role in Assets.zip AND be listed in that zone's own vanilla
# spawn files (SkyWynn Zones 1-4 = vanilla Zones 1-4, Zone 5 = a second vanilla Zone 4 - SkyyWorldGen), checked below. The night void mobs
# (Server/NPC/Spawn/World/Void/Tier*_Night) join Small (spec: "the mobs that spawn at night spawn there too"). Flyers stay on a leash.
CZ_POOL = [
    ("Skeleton_Fighter,Wolf_Black,Larva_Void,Crawler_Void,Eye_Void", "Bear_Grizzly,Spider,Skeleton_Burnt_Praetorian",
     "Snake_Marsh,Fen_Stalker,Skeleton_Mage,Void_Spectre",
     "Goblin_Scrapper,Goblin_Lobber,Goblin_Miner,Goblin_Burner,Rat,Spider_Cave,Toad_Rhino_Magma,Golem_Firesteel,Skeleton_Soldier"),
    ("Hyena,Tiger_Sabertooth,Skeleton_Sand_Guard,Skeleton_Sand_Assassin,Larva_Void,Crawler_Void,Eye_Void", "Scorpion,Snake_Rattle,Scarak_Seeker",
     "Cactee,Crocodile,Skeleton_Sand_Mage,Void_Spectre", "Rat,Snake_Cobra,Goblin_Scrapper,Goblin_Lobber,Scarak_Louse,Toad_Rhino_Magma,Golem_Firesteel"),
    ("Skeleton_Scout,Snake_Cobra,Larva_Void,Crawler_Void,Eye_Void", "Wolf_White,Bear_Grizzly,Skeleton_Frost_Fighter",
     "Bear_Polar,Leopard_Snow,Skeleton_Frost_Soldier,Skeleton_Frost_Mage,Skeleton_Frost_Knight,Skeleton_Frost_Ranger,Outlander_Berserker,Outlander_Hunter,Void_Spectre",
     "Rat,Spider_Cave,Goblin_Scrapper,Skeleton_Frost_Soldier"),
    ("Skeleton_Burnt_Soldier,Skeleton_Burnt_Praetorian,Toad_Rhino", "Skeleton_Burnt_Lancer,Wraith,Hound_Bleached",
     "Spark_Living,Skeleton_Incandescent_Head,Zombie_Burnt", "Rat,Zombie,Zombie_Burnt,Hound_Bleached,Skeleton_Burnt_Alchemist"),
    ("Skeleton_Burnt_Lancer,Skeleton_Incandescent_Footman,Toad_Rhino_Magma", "Skeleton_Incandescent_Mage,Emberwulf,Skeleton_Burnt_Gunner,Raptor_Cave",
     "Snapdragon,Rex_Cave,Zombie_Burnt,Spark_Living", "Golem_Firesteel,Toad_Rhino_Magma,Zombie_Burnt,Skeleton_Burnt_Alchemist,Hound_Bleached"),
]
CZ_SRC = ["Zone1", "Zone2", "Zone3", "Zone4", "Zone4"]
_CZ_ROLES = dict((_n.rsplit("/", 1)[1][:-5], _n) for _n in AZN if _n.startswith("Server/NPC/Roles/") and _n.endswith(".json"))
_CZ_DROPS = dict((_n.rsplit("/", 1)[1][:-5], _n) for _n in AZN if _n.startswith("Server/Drops/") and _n.endswith(".json"))


def _cz_ids(o, out):
    if isinstance(o, dict):
        for _kk, _vv in o.items():
            if _kk == "Id" and isinstance(_vv, str):
                out.add(_vv)
            else:
                _cz_ids(_vv, out)
    elif isinstance(o, list):
        for _vv in o:
            _cz_ids(_vv, out)


_CZ_SPAWN = {}
_CZ_SPW = {}   # fix (critic r5combat2 2nd round): each spawn file's top-level (role, Weight) entries
for _n in AZN:
    if _n.startswith("Server/NPC/Spawn/") and _n.endswith(".json"):
        _s = set()
        _npcs = json.loads(AZ.read(_n).decode("utf-8-sig")).get("NPCs", [])
        _cz_ids(_npcs, _s)
        _CZ_SPAWN[_n] = _s
        _CZ_SPW[_n] = [(_e.get("Id"), float(_e.get("Weight", 1))) for _e in (_npcs if isinstance(_npcs, list) else []) if isinstance(_e, dict) and isinstance(_e.get("Id"), str)]
for _z in range(CZ_N):
    _src = set()
    for _n, _s in _CZ_SPAWN.items():
        if ("/" + CZ_SRC[_z] + "/") in _n or "/World/Void/" in _n:
            _src |= _s
    for _part in CZ_POOL[_z]:
        for _r in _part.split(","):
            assert _r in _CZ_ROLES, "0.4.11: combat pool role %s is not a vanilla NPC role" % _r
            assert _r in _src or _r + "_Wander" in _src, "0.4.11: combat pool role %s is not in the vanilla %s spawn files" % (_r, CZ_SRC[_z])   # (or as its _Wander twin)
# fix (critic r5combat2 2nd round): each pool role's vanilla SPAWN ODDS in its zone = its Weight's share of every zone / night-void spawn file
# that lists it (or its _Wander twin), summed. The spawner picks by these and the Soul Cage's mix weights each role's drops by them, so a
# mob that is rare in vanilla (Skeleton_Burnt_Praetorian: one weight-2 entry) stays rare on the island and in the cage (no 1/8 share of
# Thorium / Cobalt Ingots on a Zone 1 Medium island). A role found only nested = 1.0; an admin-added role (not in the table) = 1.0.
CZ_WT = []
for _z in range(CZ_N):
    _wz = {}
    for _part in CZ_POOL[_z]:
        for _r in _part.split(","):
            if _r in _wz:
                continue
            _w = 0.0
            for _n, _l in _CZ_SPW.items():
                if ("/" + CZ_SRC[_z] + "/") in _n or "/World/Void/" in _n:
                    _tw = sum(_x[1] for _x in _l) or 1.0
                    _w += sum(_x[1] for _x in _l if _x[0] in (_r, _r + "_Wander")) / _tw
            _wz[_r] = round(_w if _w > 0.0 else 1.0, 4)
    CZ_WT.append(_wz)
assert CZ_WT[0]["Skeleton_Burnt_Praetorian"] < 0.25 * CZ_WT[0]["Skeleton_Fighter"] and CZ_WT[0]["Rat"] > 5 * CZ_WT[0]["Golem_Firesteel"], CZ_WT[0]
# each pool role's vanilla drops: the items its DropList gives a kill ON AVERAGE (Multiple = each part at its Weight %, Choice = by weight,
# Single = the middle of QuantityMin..Max; armor / weapons / tools left out - gear items carry SkyyGear documents) -> [(item, items a kill)]
def _cz_ev(c, out, f):
    _t = c.get("Type")
    if _t == "Single":
        _it = c.get("Item", {})
        _i = _it.get("ItemId") or ""
        if _i in ITEMS and not _i.startswith(("Armor_", "Weapon_", "Tool_")):
            out[_i] = out.get(_i, 0.0) + f * (_it.get("QuantityMin", 1) + _it.get("QuantityMax", 1)) / 2.0
        return
    _ch = c.get("Containers", [])
    if _t == "Multiple":
        for _c in _ch:
            _cz_ev(_c, out, f * min(1.0, _c.get("Weight", 100) / 100.0))
    elif _t == "Choice":
        _tw = float(sum(_c.get("Weight", 1) for _c in _ch) or 1)
        for _c in _ch:
            _cz_ev(_c, out, f * _c.get("Weight", 1) / _tw)


CZ_DROPS = {}
for _r in sorted(set(_r for _pl in CZ_POOL for _pt in _pl for _r in _pt.split(","))):
    _out = {}
    for _d in re.findall(r'"DropList"\\s*:\\s*"([^"]+)"', AZ.read(_CZ_ROLES[_r]).decode("utf-8-sig")):
        if _d in _CZ_DROPS:
            _cz_ev(json.loads(AZ.read(_CZ_DROPS[_d]).decode("utf-8-sig")).get("Container", {}), _out, 1.0)
    CZ_DROPS[_r] = [(_i, round(_q, 4)) for _i, _q in sorted(_out.items()) if _q > 0.0]
_cz_sk = dict(CZ_DROPS["Skeleton_Fighter"])
assert abs(_cz_sk.get("Ingredient_Bone_Fragment", 0) - 1.5) < 1e-9 and abs(_cz_sk.get("Ingredient_Fabric_Scrap_Linen", 0) - 1.5) < 1e-9, _cz_sk
assert sum(1 for _r in CZ_DROPS if CZ_DROPS[_r]) >= 30, "0.4.11: most pool roles have vanilla drops"
# the spec 10 tables (L0 .. L5 per size; Medium / Large L0 = the size below's L5, so a grow never makes it worse)
CZ_CAP = [[3, 4, 5, 6, 7, 8], [8, 9, 10, 10, 11, 12], [12, 13, 14, 16, 17, 18]]
CZ_LVL = [[(1, 3), (2, 4), (2, 5), (3, 6), (4, 7), (5, 8)], [(5, 8), (6, 9), (7, 10), (8, 11), (9, 12), (10, 13)],
          [(10, 13), (11, 14), (12, 16), (13, 17), (15, 19), (16, 20)]]
CZ_RSP = [[30, 27, 24, 21, 18, 15], [15, 14, 13, 12, 11, 10], [10, 9, 8, 8, 7, 6]]
CZ_OFF = [0, 20, 40, 60, 80]
CZ_ZLV = [20, 40, 60, 80]
for _s in range(2):
    assert CZ_CAP[_s][5] == CZ_CAP[_s + 1][0] and CZ_LVL[_s][5] == CZ_LVL[_s + 1][0] and CZ_RSP[_s][5] == CZ_RSP[_s + 1][0], "0.4.11: L0 = the size below's L5"
assert CZ_CAP[0][0] == 3 and CZ_CAP[2][5] == 18 and CZ_LVL[0][0] == (1, 3) and CZ_LVL[2][5] == (16, 20) and CZ_RSP[0][0] == 30 and CZ_RSP[2][5] == 6, "0.4.11: spec 10's ends"
CZ_MAT = ["raw:16|raw:32,Ingredient_Void_Essence:1|raw:64,Ingredient_Void_Essence:2",
          "raw:16|raw:32,Ingredient_Life_Essence:1|raw:64,Ingredient_Life_Essence:2",
          "raw:8,Ingredient_Water_Essence:1|raw:16,Ingredient_Water_Essence:2|raw:32,Ingredient_Water_Essence:4"]
for _v in CZ_MAT:
    for _part in _v.replace("|", ",").split(","):
        assert _part.split(":")[0] == "raw" or _part.split(":")[0] in ITEMS, "0.4.11: combat material %s" % _part
CZ_MAXH, CZ_AFK, CZ_DIST = 2 * _BM48.KILLS_H, 300, 6
assert CZ_MAXH == 300
# THE SOUL CAGE'S PACE (fix, critic r5combat2 - Skyy 2026-10-24: "new islands stay the same. max islands out put should far exceed player
# productivity"): an arena has no crop tiles, so a Soul Cage's rate does NOT grow with its range or the island's area (0.4.10's area
# reach: a maxed Large with 5 Soul Cage V would make ~14x fighting); each Soul Cage works at its tier's worker speed, the island's total
# then goes through combat.cageGrowth + combat.cagePct of its zone (below; ShCfg.cbOut in ShTotem.islandRate, before the Time Compressor):
# a new Zone 1 Small island with one Soul Cage I = 67.5 drops / h, exactly 0.4.10 (a new island stays the same). Harness phase BAL.
CZ_CAGE = [100, 68, 39, 82, 68]
# 0.4.11 retune (Skyy 2026-10-24 popup COMBAT SHARD PACE: a MAXED combat island ~1-1.5x fighting that zone yourself, "About 1-1.5x
# (Recommended)"; + "new islands stay the same"): one percent cannot do it - at 100 % the zones' maxed / fighting ratios spread 2.5-7x (a
# 2.7x spread > the 1.5x window) and a flat cut would also cut a new (owned, 0.4.10) Zone 1 island. So two numbers: combat.cageGrowth =
# how much of an island's growth past ONE Soul Cage I counts, as a power (out = r0 x (rate / r0) ^ growth %, r0 = the tier I worker
# speed; at or below r0 nothing changes: a new island stays exactly the same, every upgrade / cage / grow still adds), then
# combat.cagePct per zone (Zone 1 100 = a new Zone 1 island = 0.4.10). The Time Compressor is NOT squeezed (it stays x2 on every shard,
# as its menu says) - it is part of the target: a fully maxed island WITH Time Compressor III = ~1.0-1.5x, without = half. Harness BAL.
CZ_GROW = 54
# fix (critic r5combat2 2nd round, items + coins): items a Soul Cage never makes - they come from fighting. The night void mobs' Void Essence
# / Voidheart (the Mobs at once + Time Compressor material: an island must not pay for its own upgrades; with them a new Zone 1 Small
# island's mix sells at ~8x the 0.4.10 Bone Fragments at the live P7 Bazaar prices, without them ~1x - Skyy "new islands stay the same")
# and other skills' goods (ingots, ores, crystals, stone: no Mining collection from a combat Collect). "X*" = every id starting with X.
CZ_SKIP = "Ingredient_Void_Essence,Ingredient_Voidheart,Ore_*,Ingredient_Bar_*,Ingredient_Crystal_*,Rock_*"
for _v in CZ_SKIP.split(","):
    assert _v.endswith("*") or _v in ITEMS, "0.4.11: combat.cageSkip %s" % _v
# fix (critic r5combat2 2nd round, spec 10 "Automated: the Soul Cage also kills on its own ... using the pool, the mob level and the spawn
# speed"): Mobs at once x Spawn speed (the island's spawn throughput, mobs at once / respawn seconds) raise a Soul Cage's output on top of
# the +3 % a level: the throughput's log share of the way from Small level 0 (3 / 30 s) to the top (Large 18 / 6 s = 30x) gives up to
# combat.spawnBonus % more (40: a maxed Large x1.4, Small Mobs at once 5 + Spawn speed 5 x1.18, a new island x1). Mob level keeps the
# +3 % a level. Balance: harness phase BAL (coins at the Bazaar's prices).
CZ_SPB = 40''')

# ---------------------------------------------------------------------------------------------------- 2. the combat land's blocks (after XIDS)
P.rep('''def _xi48(v):
    return -1 if not v else XBASE + XIDS.index(v)
''', '''def _xi48(v):
    return -1 if not v else XBASE + XIDS.index(v)


# 0.4.11 the combat islands' land per zone (vanilla blocks, checked here; nothing copied - placed by id): floor, rim, rise, rise top, trunk,
# leaves, corner ground, corner plant, cavern rock, cavern crystal; + one torch, fence and glowing lava rock (no fluid: "a little lava" that
# never flows)
CZ_PAL = [("Soil_Grass", "Rock_Stone_Brick_Mossy", "Rock_Stone", "Rock_Stone_Mossy", "Wood_Oak_Trunk", "Plant_Leaves_Oak", "Soil_Mud", "Plant_Reeds_Marsh", "Rock_Stone", "Rock_Crystal_Blue_Medium"),
          ("Soil_Sand", "Rock_Sandstone_Brick", "Rock_Sandstone", "Rock_Sandstone", "Wood_Gumboab_Trunk", "Plant_Leaves_Gumboab", "Soil_Sand_Red", "Plant_Cactus_1", "Rock_Sandstone", "Rock_Crystal_Yellow_Medium"),
          ("Soil_Grass_Cold", "Rock_Slate_Brick", "Rock_Ice", "Soil_Snow", "Wood_Fir_Trunk", "Plant_Leaves_Fir_Snow", "Soil_Snow", "Plant_Fern_Forest", "Rock_Slate", "Rock_Crystal_White_Medium"),
          ("Soil_Ash", "Rock_Volcanic_Brick", "Rock_Volcanic", "Rock_Volcanic", "Wood_Burnt_Trunk", "Plant_Leaves_Burnt", "Soil_Gravel", "Plant_Bramble_Dead_Lavathorn", "Rock_Volcanic", "Rock_Crystal_Red_Medium"),
          ("Rock_Magma_Cooled", "Rock_Basalt_Brick", "Rock_Basalt", "Rock_Basalt", "Wood_Fire_Trunk", "Plant_Leaves_Fire", "Rock_Volcanic_Cracked_Lava", "Plant_Reeds_Lava", "Rock_Basalt", "Rock_Crystal_Purple_Medium")]
CZ_ONE = ("Furniture_Crude_Torch", "Wood_Softwood_Fence", "Rock_Volcanic_Cracked_Lava")
for _row in CZ_PAL + [CZ_ONE]:
    for _id in _row:
        assert _id in ITEMS and json.loads(AZ.read(ITEMS[_id]).decode("utf-8-sig")).get("BlockType") is not None, "0.4.11: combat land block %s" % _id
for _row in CZ_PAL:   # the plants / crystals / leaves stand alone (placed only on AIR): one-cell blocks
    for _id in (_row[7], _row[9]) + CZ_ONE[:2]:
        _bt = json.loads(AZ.read(ITEMS[_id]).decode("utf-8-sig")).get("BlockType")
        assert _bt.get("HitboxType") in _HB_OK48, "0.4.11: %s is not a one-cell block (%s)" % (_id, _bt.get("HitboxType"))


def _xc48(v):
    if v not in XIDS:
        XIDS.append(v)
    return _xi48(v)


CZ_PALI = [[_xc48(_id) for _id in _row] for _row in CZ_PAL]
CZ_ONEI = [_xc48(_id) for _id in CZ_ONE]
''')

# ---------------------------------------------------------------------------------------------------- 3. config: fields, the default file, rows, loader
P.rep('''          "public static final int[] BAND = new int[] { %s };" % ", ".join(str(_x) for _x in BAND48)):
    F(cfg, f)''', '''          "public static final int[] BAND = new int[] { %s };" % ", ".join(str(_x) for _x in BAND48)):
    F(cfg, f)
# 0.4.11: THE COMBAT SHARD (Server Setup -> Shards -> Combat islands; arrays swapped whole by the loader). CAP / LO / HI / RSP = size x 6 + level
CZ_POOLF = [_pl[_q] for _pl in CZ_POOL for _q in range(4)]
for f in ("public static volatile boolean CB_NIGHT = true;", "public static volatile boolean CB_SPAWN = true;",
          "public static volatile int[] CB_ZLV = new int[] { %s };" % ", ".join(str(_x) for _x in CZ_ZLV),
          "public static final int[] DEF_CB_CAP = new int[] { %s };" % ", ".join(str(_x) for _r in CZ_CAP for _x in _r),
          "public static volatile int[] CB_CAP = new int[] { %s };" % ", ".join(str(_x) for _r in CZ_CAP for _x in _r),
          "public static volatile int[] CB_LO = new int[] { %s };" % ", ".join(str(_x[0]) for _r in CZ_LVL for _x in _r),
          "public static volatile int[] CB_HI = new int[] { %s };" % ", ".join(str(_x[1]) for _r in CZ_LVL for _x in _r),
          "public static volatile int[] CB_RSP = new int[] { %s };" % ", ".join(str(_x) for _r in CZ_RSP for _x in _r),
          "public static final int[] DEF_CB_OFF = new int[] { %s };" % ", ".join(str(_x) for _x in CZ_OFF),
          "public static volatile int[] CB_OFF = new int[] { %s };" % ", ".join(str(_x) for _x in CZ_OFF),
          "public static final String[] DEF_CB_POOL = %s;" % _ja48(CZ_POOLF), "public static volatile String[] CB_POOL = %s;" % _ja48(CZ_POOLF),
          "public static volatile int CB_MAXH = %d;" % CZ_MAXH, "public static volatile int CB_AFK = %d;" % CZ_AFK, "public static volatile int CB_DIST = %d;" % CZ_DIST,
          "public static final int[] DEF_CB_CAGE = new int[] { %s };" % ", ".join(str(_x) for _x in CZ_CAGE),
          "public static volatile int[] CB_CAGE = new int[] { %s };" % ", ".join(str(_x) for _x in CZ_CAGE),
          "public static volatile int CB_GROW = %d;" % CZ_GROW, "public static volatile int CB_SPB = %d;" % CZ_SPB,
          "public static final String[] DEF_CB_SKIP = %s;" % _ja48(CZ_SKIP.split(",")), "public static volatile String[] CB_SKIP = %s;" % _ja48(CZ_SKIP.split(",")),
          "public static final String[] DEF_CB_MAT = %s;" % _ja48(CZ_MAT), "public static volatile String[] CB_MAT = %s;" % _ja48(CZ_MAT)):
    F(cfg, f)''')
P.rep('''    "# storage.tierN = stacks of 100 each island of the shard holds at storage tier N (0.4.4: 3 days of a full Large island at Totem N).",''',
      '''    "# combat.* = 0.4.11 THE COMBAT SHARD (one island per zone). nightHold = players on the Combat Shard see midnight (their screen only;",
    "# the shard world's clock is not changed). spawn = combat islands spawn mobs while an owner / co-op member stands on them.",
    "# zoneLevel.N = the class level that buys Zone N. cap / level / respawn.<size> = 6 values for the sub-upgrade levels 0..5 (mobs at once,",
    "# mob level ranges lo-hi inside Zone 1 - levelOffset adds 0 / 20 / 40 / 60 / 80 for Zones 1-5 -, seconds before a dead mob's place",
    "# spawns again). pool.<zone>.<small|medium|large|lower> = NPC role ids each size ADDS (lower = the Large island's cavern). maxPerHour =",
    "# mobs all combat islands of a profile spawn in an hour at most (0 = no limit); afkSec = an island spawns only while someone there moved",
    "# in this many seconds (0 = off); minDist = never closer to a player. mat.cap / level / speed = the 3 sub-upgrades' items (x the level).",
    "# cagePct = 5 percents (Zone 1..5): a combat island's Soul Cage output in that zone (range / island size add nothing in an arena).",
    "# cageGrowth = % of a combat island's growth past one Soul Cage I that counts (a power; 100 = all of it; a new island stays the same).",
    "# spawnBonus = % more Soul Cage output at the top Mobs at once + Spawn speed (in between by the spawn rate's share). cageSkip = items a",
    "# Soul Cage never makes (they come from fighting; X* = every id starting with X). maxPerHour counts at Small level 0 and grows with the",
    "# island's mobs at once / respawn time.",
    "combat.nightHold=true", "combat.spawn=true",
] + ["combat.zoneLevel.%d=%d" % (_z + 2, CZ_ZLV[_z]) for _z in range(4)] + \\
    ["combat.cap.%s=%s" % (_sn, ",".join(str(_x) for _x in CZ_CAP[_i])) for _i, _sn in enumerate(("small", "medium", "large"))] + \\
    ["combat.level.%s=%s" % (_sn, ",".join("%d-%d" % _x for _x in CZ_LVL[_i])) for _i, _sn in enumerate(("small", "medium", "large"))] + \\
    ["combat.respawn.%s=%s" % (_sn, ",".join(str(_x) for _x in CZ_RSP[_i])) for _i, _sn in enumerate(("small", "medium", "large"))] + \\
    ["combat.levelOffset=" + ",".join(str(_x) for _x in CZ_OFF)] + \\
    ["combat.pool.%d.%s=%s" % (_z + 1, _pn, CZ_POOL[_z][_q]) for _z in range(CZ_N) for _q, _pn in enumerate(("small", "medium", "large", "lower"))] + \\
    ["combat.maxPerHour=%d" % CZ_MAXH, "combat.afkSec=%d" % CZ_AFK, "combat.minDist=%d" % CZ_DIST, "combat.cagePct=" + ",".join(str(_x) for _x in CZ_CAGE),
     "combat.cageGrowth=%d" % CZ_GROW, "combat.spawnBonus=%d" % CZ_SPB, "combat.cageSkip=" + CZ_SKIP] + \\
    ["combat.mat.%s=%s" % (_mk, CZ_MAT[_i]) for _i, _mk in enumerate(("cap", "level", "speed"))] + [
    "# storage.tierN = stacks of 100 each island of the shard holds at storage tier N (0.4.4: 3 days of a full Large island at Totem N).",''')
P.rep('''for _r in ROWS:
    assert len(_r[1]) <= 40 and len(_r[10]) <= 100, "0.4: Server Setup label / help too long: %s" % (_r[0],)''', '''# 0.4.11: Server Setup -> Shards -> Combat islands
CATS = CATS + [("combat", "Combat islands")]
ROWS += [("combat.nightHold", "Always night on combat islands", "combat", "bool", "true", "", "", "", "", "live",
          "Players in the Combat Shard see midnight (their screen only - the shard's clock is not changed).", "reload@config.properties:combat.nightHold"),
         ("combat.spawn", "Combat islands spawn mobs", "combat", "bool", "true", "", "", "", "", "live",
          "Mobs spawn on a combat island while its owner or a co-op member stands on it.", "reload@config.properties:combat.spawn")]
ROWS += [("combat.zoneLevel.%d" % (_z + 2), "Zone %d island: class level" % (_z + 2), "combat", "int", str(CZ_ZLV[_z]), "0", "1000", "", "", "live",
          "The class level that may buy the Zone %d island (0 = any)." % (_z + 2), "reload@config.properties:combat.zoneLevel.%d" % (_z + 2)) for _z in range(4)]
ROWS += [("combat.cap.%s" % _sn, "%s: mobs at once, level 0-5" % _sl, "combat", "text", ",".join(str(_x) for _x in CZ_CAP[_i]), "", "60", "", "", "live",
          "6 numbers: mobs alive at once at Mobs at once level 0..5 (Large: half of them in the cavern).", "reload@config.properties:combat.cap.%s" % _sn)
         for _i, (_sn, _sl) in enumerate((("small", "Small"), ("medium", "Medium"), ("large", "Large")))]
ROWS += [("combat.level.%s" % _sn, "%s: mob levels, level 0-5" % _sl, "combat", "text", ",".join("%d-%d" % _x for _x in CZ_LVL[_i]), "", "80", "", "", "live",
          "6 ranges lo-hi: mob levels at Mob level 0..5 in Zone 1 (the zone offset is added).", "reload@config.properties:combat.level.%s" % _sn)
         for _i, (_sn, _sl) in enumerate((("small", "Small"), ("medium", "Medium"), ("large", "Large")))]
ROWS += [("combat.respawn.%s" % _sn, "%s: respawn time, level 0-5" % _sl, "combat", "text", ",".join(str(_x) for _x in CZ_RSP[_i]), "", "60", "", "s", "live",
          "6 numbers: seconds before a dead mob's place spawns again at Spawn speed level 0..5.", "reload@config.properties:combat.respawn.%s" % _sn)
         for _i, (_sn, _sl) in enumerate((("small", "Small"), ("medium", "Medium"), ("large", "Large")))]
ROWS += [("combat.levelOffset", "Mob level added per zone", "combat", "text", ",".join(str(_x) for _x in CZ_OFF), "", "40", "", "", "live",
          "5 numbers: levels added to the ranges on Zone 1..5 (each zone's level band).", "reload@config.properties:combat.levelOffset")]
ROWS += [("combat.pool.%d.%s" % (_z + 1, _pn), "Zone %d mobs: %s" % (_z + 1, _pl), "combat", "text", CZ_POOL[_z][_q], "", "400", "", "", "live,adv",
          "NPC role ids (comma separated) the %s island adds to Zone %d's pool." % (_pl, _z + 1), "reload@config.properties:combat.pool.%d.%s" % (_z + 1, _pn))
         for _z in range(CZ_N) for _q, (_pn, _pl) in enumerate((("small", "Small"), ("medium", "Medium"), ("large", "Large upper"), ("lower", "Large cavern")))]
ROWS += [("combat.maxPerHour", "Mobs per hour at most (a profile)", "combat", "int", str(CZ_MAXH), "0", "100000", "", "", "live",
          "A profile's spawns an hour at Small level 0; x the island's mobs at once / respawn. 0 = no limit.", "reload@config.properties:combat.maxPerHour"),
         ("combat.afkSec", "Spawning stops when nobody moves", "combat", "int", str(CZ_AFK), "0", "86400", "", "s", "live",
          "An island spawns only while someone on it moved within this time (no AFK farms). 0 = off.", "reload@config.properties:combat.afkSec"),
         ("combat.minDist", "Never spawn closer to a player", "combat", "int", str(CZ_DIST), "0", "32", "", "", "live",
          "Blocks: a mob never appears closer than this to any player.", "reload@config.properties:combat.minDist"),
         ("combat.cagePct", "Soul Cage pay per zone (%)", "combat", "text", ",".join(str(_x) for _x in CZ_CAGE), "", "40", "", "", "live",
          "5 percents, Zone 1..5: a combat island's Soul Cage output (Zone 1 100 = a new island's 0.4.10 rate).", "reload@config.properties:combat.cagePct"),
         ("combat.cageGrowth", "Combat island growth that counts", "combat", "int", str(CZ_GROW), "0", "100", "", "%", "live",
          "Power on growth past one Soul Cage I (cages, upgrades, size). 100 = all; new islands stay the same.", "reload@config.properties:combat.cageGrowth"),
         ("combat.spawnBonus", "Soul Cage bonus at top spawn speed", "combat", "int", str(CZ_SPB), "0", "1000", "", "%", "live",
          "% more Soul Cage output at the top Mobs at once + Spawn speed levels (in between: part of it).", "reload@config.properties:combat.spawnBonus"),
         ("combat.cageSkip", "Items a Soul Cage never makes", "combat", "text", CZ_SKIP, "", "400", "", "", "live,adv",
          "Item ids (comma separated; X* = every id starting with X) that only come from fighting.", "reload@config.properties:combat.cageSkip")]
ROWS += [("combat.mat.%s" % _mk, "%s items (S|M|L)" % _ml, "combat", "text", CZ_MAT[_i], "", "300", "", "", "live",
          "Small|Medium|Large: raw (the zone's drop) or Item:qty, x the level bought.", "reload@config.properties:combat.mat.%s" % _mk)
         for _i, (_mk, _ml) in enumerate((("cap", "Mobs at once"), ("level", "Mob level"), ("speed", "Spawn speed")))]
for _r in ROWS:
    assert len(_r[1]) <= 40 and len(_r[10]) <= 100, "0.4: Server Setup label / help too long: %s" % (_r[0],)''')
P.rep('''          "  CAVE_PCT = intsOf(p.getProperty(\\"cave.amount.pct\\"), DEF_CAVE_PCT, 0, 100, \\"cave.amount.pct\\");"]''',
      '''          "  CAVE_PCT = intsOf(p.getProperty(\\"cave.amount.pct\\"), DEF_CAVE_PCT, 0, 100, \\"cave.amount.pct\\");"]
# 0.4.11: the combat islands
_load += ["  CB_NIGHT = bool(p.getProperty(\\"combat.nightHold\\"), true);", "  CB_SPAWN = bool(p.getProperty(\\"combat.spawn\\"), true);",
          "  int[] czl = new int[4];"]
_load += ["  czl[%d] = intOf(p.getProperty(\\"combat.zoneLevel.%d\\"), %d, 0, 1000);" % (_z, _z + 2, CZ_ZLV[_z]) for _z in range(4)]
_load += ["  CB_ZLV = czl;", "  int[] ccp = new int[18]; int[] clo = new int[18]; int[] chi = new int[18]; int[] crs = new int[18];"]
for _i, _sn in enumerate(("small", "medium", "large")):
    _load += ["  int[] cca%d = intsOf(p.getProperty(\\"combat.cap.%s\\"), new int[] { %s }, 1, 60, \\"combat.cap.%s\\");" % (_i, _sn, ", ".join(str(_x) for _x in CZ_CAP[_i]), _sn),
              "  int[] cla%d = rangesOf(p.getProperty(\\"combat.level.%s\\"), new int[] { %s }, \\"combat.level.%s\\");" % (_i, _sn, ", ".join(str(_x) for _x in [_y[0] for _y in CZ_LVL[_i]] + [_y[1] for _y in CZ_LVL[_i]]), _sn),
              "  int[] cra%d = intsOf(p.getProperty(\\"combat.respawn.%s\\"), new int[] { %s }, 1, 3600, \\"combat.respawn.%s\\");" % (_i, _sn, ", ".join(str(_x) for _x in CZ_RSP[_i]), _sn),
              "  for (int cq%d = 0; cq%d < 6; cq%d++) { ccp[%d + cq%d] = cca%d[cq%d]; clo[%d + cq%d] = cla%d[cq%d]; chi[%d + cq%d] = cla%d[6 + cq%d]; crs[%d + cq%d] = cra%d[cq%d]; }"
              % (_i, _i, _i, 6 * _i, _i, _i, _i, 6 * _i, _i, _i, _i, 6 * _i, _i, _i, _i, 6 * _i, _i, _i, _i)]
_load += ["  CB_CAP = ccp; CB_LO = clo; CB_HI = chi; CB_RSP = crs;",
          "  CB_OFF = intsOf(p.getProperty(\\"combat.levelOffset\\"), DEF_CB_OFF, 0, 1000, \\"combat.levelOffset\\");",
          "  String[] cpl = new String[%d];" % (4 * CZ_N)]
_load += ["  { String cpv%d = p.getProperty(\\"combat.pool.%d.%s\\"); cpl[%d] = cpv%d == null ? DEF_CB_POOL[%d] : cpv%d.trim(); }" % (_z * 4 + _q, _z + 1, _pn, _z * 4 + _q, _z * 4 + _q, _z * 4 + _q, _z * 4 + _q)
          for _z in range(CZ_N) for _q, _pn in enumerate(("small", "medium", "large", "lower"))]
_load += ["  CB_POOL = cpl;",
          "  CB_MAXH = intOf(p.getProperty(\\"combat.maxPerHour\\"), %d, 0, 100000);" % CZ_MAXH,
          "  CB_AFK = intOf(p.getProperty(\\"combat.afkSec\\"), %d, 0, 86400);" % CZ_AFK,
          "  CB_DIST = intOf(p.getProperty(\\"combat.minDist\\"), %d, 0, 32);" % CZ_DIST,
          "  CB_CAGE = intsOf(p.getProperty(\\"combat.cagePct\\"), DEF_CB_CAGE, 0, 1000, \\"combat.cagePct\\");",
          "  CB_GROW = intOf(p.getProperty(\\"combat.cageGrowth\\"), %d, 0, 100);" % CZ_GROW,
          "  CB_SPB = intOf(p.getProperty(\\"combat.spawnBonus\\"), %d, 0, 1000);" % CZ_SPB,
          "  { String csk = p.getProperty(\\"combat.cageSkip\\"); CB_SKIP = csk == null ? DEF_CB_SKIP : skipOf(csk); }",
          "  String[] cmt = new String[3];"]
_load += ["  { String cmv%d = p.getProperty(\\"combat.mat.%s\\"); cmt[%d] = cmv%d == null ? DEF_CB_MAT[%d] : cmv%d.trim(); }" % (_i, _mk, _i, _i, _i, _i)
          for _i, _mk in enumerate(("cap", "level", "speed"))]
_load += ["  CB_MAT = cmt;"]''')
P.rep('''M(cfg, r"""
public static String num(long n) {''', '''# 0.4.11: "1-3,2-4,..." (up to n ranges, the last one repeats) -> { lo x n, hi x n }; a bad text = the default + one WARN
# fix (critic r5combat2 2nd round): combat.cageSkip -> the trimmed, non-empty ids
M(cfg, r"""
public static String[] skipOf(String v) {
  java.util.ArrayList l = new java.util.ArrayList();
  String[] a = v.split(",");
  for (int i = 0; i < a.length; i++) { String x = a[i].trim(); if (x.length() > 0 && !l.contains(x)) l.add(x); }
  String[] o = new String[l.size()];
  for (int i = 0; i < o.length; i++) o[i] = (String) l.get(i);
  return o;
}""")
# fix (critic r5combat2 2nd round, spec 10): the Soul Cage's spawn factor on a combat island = (1 + spawnBonus %) ^ (the log share of the island's
# spawn throughput cap / respawn between Small level 0 and the table's top); 1 at a new island, never below 1
M(cfg, r"""
public static double cbSpawnX(int size, int a, int i) {
  int[] c = CB_CAP;
  int[] r = CB_RSP;
  if (c == null || r == null || c.length < 18 || r.length < 18 || CB_SPB <= 0) return 1.0;
  int s = size < 1 ? 1 : (size > 3 ? 3 : size);
  int ia = (s - 1) * 6 + (a < 0 ? 0 : (a > 5 ? 5 : a));
  int ii = (s - 1) * 6 + (i < 0 ? 0 : (i > 5 ? 5 : i));
  double s0 = (double) c[0] / (double) (r[0] < 1 ? 1 : r[0]);
  double sm = (double) c[17] / (double) (r[17] < 1 ? 1 : r[17]);
  double sv = (double) c[ia] / (double) (r[ii] < 1 ? 1 : r[ii]);
  if (!(sm > s0) || !(sv > s0)) return 1.0;
  double f = Math.log(sv / s0) / Math.log(sm / s0);
  if (f > 1.0) f = 1.0;
  return Math.pow(1.0 + (double) CB_SPB / 100.0, f);
}""")
# 0.4.11 retune (Skyy popup COMBAT SHARD PACE "About 1-1.5x"): a combat island's rate r (items / min, before the Time Compressor) ->
# r0 x (r / r0) ^ (cageGrowth %) above r0 = one Soul Cage I's speed (a new island and the manual phase unchanged), x cagePct of zone z
M(cfg, r"""
public static double cbOut(double r, int z) {
  double[] rt = RATES;
  double r0 = rt == null || rt.length < 1 ? 0.0 : rt[0];
  double g = (double) CB_GROW / 100.0;
  double o = r;
  if (r0 > 0.0 && r > r0 && g < 1.0) o = r0 * Math.pow(r / r0, g < 0.0 ? 0.0 : g);
  int[] c = CB_CAGE;
  if (c == null || c.length < 1) return o;
  int zi = z < 0 ? 0 : (z >= c.length ? c.length - 1 : z);
  return o * (double) c[zi] / 100.0;
}""")
M(cfg, r"""
public static int[] rangesOf(String v, int[] def, String key) {
  int n = def.length / 2;
  int[] d = new int[def.length];
  for (int i = 0; i < d.length; i++) d[i] = def[i];
  if (v == null || v.trim().length() == 0) return d;
  try {
    String[] a = v.trim().split(",");
    if (a.length < 1 || a.length > n) throw new IllegalArgumentException("1 to " + n + " ranges");
    int lo = 1;
    int hi = 1;
    for (int i = 0; i < n; i++) {
      if (i < a.length) {
        String s = a[i].trim();
        int c = s.indexOf('-', 1);
        if (c < 0) { lo = Integer.parseInt(s); hi = lo; }
        else { lo = Integer.parseInt(s.substring(0, c).trim()); hi = Integer.parseInt(s.substring(c + 1).trim()); }
        if (lo < 1) lo = 1;
        if (lo > 1000) lo = 1000;
        if (hi < lo) hi = lo;
        if (hi > 1000) hi = 1000;
      }
      d[i] = lo;
      d[n + i] = hi;
    }
    return d;
  } catch (Throwable t) {
    warnOnce("ranges:" + key + "=" + v, key + "=" + v + " is not a list of " + n + " ranges like 1-3 - the default is used");
    for (int i = 0; i < d.length; i++) d[i] = def[i];
    return d;
  }
}""")
M(cfg, r"""
public static String num(long n) {''')

# ---------------------------------------------------------------------------------------------------- 4. ShIsl: the zone names, the combat sub names
P.rep('''M(isl48, "public static String tname(int t) { return t < 0 || t >= TN ? \\"\\" : \\"T\\" + TIER[t] + \\" \\" + NAME[t]; }")''',
      '''M(isl48, "public static String tname(int t) { return t < 0 || t >= TN ? \\"\\" : (TK[t] == %d ? NAME[t] : \\"T\\" + TIER[t] + \\" \\" + NAME[t]); }" % KINDS.index("Combat"))   # 0.4.11: "Zone 2" (mobs have no tiers)''')
P.rep('''public static String subName(int kd, int which) {
  String st = STYLE[kd];
  if (which == 1) return "Decorations";''', '''public static String subName(int kd, int which) {
  String st = STYLE[kd];
  if (st.equals("arena")) return which == 0 ? "Mobs at once" : (which == 1 ? "Mob level" : "Spawn speed");   // 0.4.11 (spec 10)
  if (which == 1) return "Decorations";''')
P.rep('''@PKG@.ShIsl.subName(kd, 0) + " " + a + "/5, Decorations " + d + "/5, " + @PKG@.ShIsl.subName(kd, 2)''',
      '''@PKG@.ShIsl.subName(kd, 0) + " " + a + "/5, " + @PKG@.ShIsl.subName(kd, 1) + " " + d + "/5, " + @PKG@.ShIsl.subName(kd, 2)''')

# ---------------------------------------------------------------------------------------------------- 4a. migrate2 (0.4.8's one-time map migration): Combat keeps its types
# fix (critic r5combat2 2nd round): 0.4.6 / 0.4.7 (deployed 2026-10-23) let a profile buy Combat islands 2-6 (all Skeleton); the 0.4.8 map
# migration renames the nth owned island to ladder tier n, and with 5 Combat tiers now a profile that has not loaded since 0.4.7 would get
# Zones 2-5 free (no coins, no 64 drops, no class level). Combat islands keep their type (as every profile migrated under 0.4.8-0.4.10: its
# extra islands stayed Zone 1 = Skeleton).
P.rep('''        if (want < @PKG@.ShIsl.LADN[kd]) {''', '''        if (want < @PKG@.ShIsl.LADN[kd] && kd != %d) {   // 0.4.11 fix (critic): Combat islands keep their type (Zones 2-5 are bought)''' % KINDS_COMBAT)
# ---------------------------------------------------------------------------------------------------- 4b. the Soul Cage's pace on a combat island (no area reach)
P.rep('''  double i = 1.0 + @PKG@.ShCfg.IRR_PCT / 100.0 * (double) lt(size, sub(p, kd, slot, 2));
  return a * d * i;
}""")''', '''  double i = 1.0 + @PKG@.ShCfg.IRR_PCT / 100.0 * (double) lt(size, sub(p, kd, slot, 2));
  if (kd == %d) return a * d * i * @PKG@.ShCfg.cbSpawnX(size, sub(p, kd, slot, 0), sub(p, kd, slot, 2));   // 0.4.11 fix (critic): Mobs at once x Spawn speed drive the Soul Cage (spec 10)
  return a * d * i;
}""")''' % KINDS_COMBAT)
P.rep('''  return w * (1.0 + s / 100.0) * tcMult(kd, p) * @PKG@.ShIsl.mult(kd, p, slot, size);   // 0.4.8: x the island's 3 sub-upgrades''',
      '''  if (kd == %d) return @PKG@.ShCfg.cbOut(w * (1.0 + s / 100.0) * @PKG@.ShIsl.mult(kd, p, slot, size), @PKG@.ShIsl.rank(@PKG@.ShIsl.ty(kd, p, slot))) * tcMult(kd, p);   // 0.4.11 retune: combat.cageGrowth + cagePct of the zone, then the Time Compressor (unsqueezed)
  return w * (1.0 + s / 100.0) * tcMult(kd, p) * @PKG@.ShIsl.mult(kd, p, slot, size);   // 0.4.8: x the island's 3 sub-upgrades''' % KINDS_COMBAT)
P.rep('''  double reach = (double) cov(size, range(f, t)) / (double) ref;''', '''  double reach = (double) cov(size, range(f, t)) / (double) ref;
  if (kd == %d) reach = 1.0;   // 0.4.11: an arena has no tiles to cover - the tier's speed (combat.cagePct / cageGrowth act on the whole island: ShTotem.islandRate)''' % KINDS_COMBAT)

# ---------------------------------------------------------------------------------------------------- 5. ShCombat: the combat tables + maths (pure)
P.rep('''# ================= ShGeo: the region layout (spec 9.1), pure maths - every block the region wants =================''',
      '''# ================= 0.4.11 ShCombat: THE COMBAT SHARD's tables + maths (pure; any thread; research/Starter-Archipelago-Spec.md 10) =================
cmb = mk("ShCombat")
_CZR = sorted(CZ_DROPS)
for f in ("public static final int CK = %d;" % KINDS.index("Combat"), "public static final int ZN = %d;" % CZ_N,
          "public static final String[] DROP_ROLE = %s;" % _ja48(_CZR), "public static final String[] DROP_IDS = %s;" % _ja48([",".join("%s:%g" % _e for _e in CZ_DROPS[_r]) for _r in _CZR]),
          "public static final String[] W_KEY = %s;" % _ja48(["%d|%s" % (_z, _r) for _z in range(CZ_N) for _r in sorted(CZ_WT[_z])]),
          "public static final double[] W_VAL = new double[] { %s };" % ", ".join(repr(CZ_WT[_z][_r]) for _z in range(CZ_N) for _r in sorted(CZ_WT[_z]))):
    F(cmb, f)
M(cmb, "public static boolean is(int kd) { return kd == CK; }")
M(cmb, r"""
public static int ix(int size, int lvl) {
  int s = size < 1 ? 1 : (size > 3 ? 3 : size);
  int l = lvl < 0 ? 0 : (lvl > 5 ? 5 : lvl);
  return (s - 1) * 6 + l;
}""")
M(cmb, r"""
public static int cap(int size, int lvl) {
  int[] a = @PKG@.ShCfg.CB_CAP;
  int i = ix(size, lvl);
  int v = i < a.length ? a[i] : 3;
  return v < 1 ? 1 : (v > 60 ? 60 : v);
}""")
M(cmb, "public static int lowerCap(int size, int lvl) { return size >= 3 ? cap(size, lvl) / 2 : 0; }")   # spec 10: Large = split upper / lower
M(cmb, r"""
public static int off(int z) {
  int[] o = @PKG@.ShCfg.CB_OFF;
  return z >= 0 && z < o.length ? o[z] : 0;
}""")
M(cmb, r"""
public static int lvLo(int z, int size, int lvl) {
  int[] a = @PKG@.ShCfg.CB_LO;
  int i = ix(size, lvl);
  int v = (i < a.length ? a[i] : 1) + off(z);
  return v < 1 ? 1 : v;
}""")
M(cmb, r"""
public static int lvHi(int z, int size, int lvl) {
  int[] a = @PKG@.ShCfg.CB_HI;
  int i = ix(size, lvl);
  int v = (i < a.length ? a[i] : 1) + off(z);
  int lo = lvLo(z, size, lvl);
  return v < lo ? lo : v;
}""")
M(cmb, r"""
public static int respawnSec(int size, int lvl) {
  int[] a = @PKG@.ShCfg.CB_RSP;
  int i = ix(size, lvl);
  int v = i < a.length ? a[i] : 30;
  return v < 1 ? 1 : v;
}""")
# fix (critic r5combat2 2nd round, the throughput lid): how much faster this island spawns than Small level 0 (mobs at once / respawn)
M(cmb, r"""
public static double lidX(int size, int a, int i) {
  double s0 = (double) cap(1, 0) / (double) respawnSec(1, 0);
  double s = (double) cap(size, a) / (double) respawnSec(size, i);
  return s0 > 0.0 && s > s0 ? s / s0 : 1.0;
}""")
M(cmb, r"""
public static int zoneOf(int t) {
  int r = @PKG@.ShIsl.rank(t);
  return r < 0 ? 0 : (r >= ZN ? ZN - 1 : r);
}""")
M(cmb, "public static int zone(int kd, java.util.Properties p, int slot) { return zoneOf(@PKG@.ShIsl.ty(kd, p, slot)); }")
# the class level Zone zi + 1 needs (zi = the ladder index: 0 = Zone 1 = with the shard)
M(cmb, r"""
public static int need(int zi) {
  int[] a = @PKG@.ShCfg.CB_ZLV;
  if (zi <= 0) return 0;
  return zi - 1 < a.length ? a[zi - 1] : 0;
}""")
M(cmb, r"""
public static void addAll(java.util.ArrayList out, String s) {
  if (s == null) return;
  String[] a = s.split(",");
  for (int i = 0; i < a.length; i++) {
    String v = a[i].trim();
    if (v.length() > 0 && !out.contains(v)) out.add(v);
  }
}""")
M(cmb, r"""
public static String[] arr(java.util.ArrayList l) {
  String[] o = new String[l.size()];
  for (int i = 0; i < o.length; i++) o[i] = (String) l.get(i);
  return o;
}""")
M(cmb, r"""
public static String[] csv(String s) {
  java.util.ArrayList l = new java.util.ArrayList();
  addAll(l, s);
  return arr(l);
}""")
# the roles of zone z at `size`: part 0 = the upper island (every size's additions so far), part 1 = the Large island's cavern
M(cmb, r"""
public static String[] roles(int z, int size, int part) {
  String[] P = @PKG@.ShCfg.CB_POOL;
  int zz = z < 0 ? 0 : (z >= ZN ? ZN - 1 : z);
  int si = size < 1 ? 1 : (size > 3 ? 3 : size);
  java.util.ArrayList out = new java.util.ArrayList();
  if (part == 1) { if (si >= 3 && zz * 4 + 3 < P.length) addAll(out, P[zz * 4 + 3]); }
  else for (int s = 0; s < si; s++) if (zz * 4 + s < P.length) addAll(out, P[zz * 4 + s]);
  return arr(out);
}""")
M(cmb, r"""
public static String[] allRoles(int z, int size) {
  java.util.ArrayList out = new java.util.ArrayList();
  String[] a = roles(z, size, 0);
  String[] b = roles(z, size, 1);
  for (int i = 0; i < a.length; i++) if (!out.contains(a[i])) out.add(a[i]);
  for (int i = 0; i < b.length; i++) if (!out.contains(b[i])) out.add(b[i]);
  return arr(out);
}""")
M(cmb, r"""
public static boolean has(String[] a, String v) {
  if (a == null || v == null) return false;
  for (int i = 0; i < a.length; i++) if (v.equals(a[i])) return true;
  return false;
}""")
M(cmb, r"""
public static String dropsOf(String role) {
  if (role == null) return "";
  for (int i = 0; i < DROP_ROLE.length; i++) if (DROP_ROLE[i].equals(role)) return DROP_IDS[i];
  return "";
}""")
# fix (critic r5combat2 2nd round): a role's vanilla spawn odds in zone z (W_KEY "z|role"; not in the table = 1.0)
M(cmb, r"""
public static double wt(int z, String role) {
  if (role == null) return 0.0;
  String k = z + "|" + role;
  for (int i = 0; i < W_KEY.length; i++) if (W_KEY[i].equals(k)) return W_VAL[i];
  return 1.0;
}""")
# the spawner's pick: by those odds (u in [0, 1))
M(cmb, r"""
public static String wpick(int z, java.util.ArrayList ok, double u) {
  int n = ok.size();
  if (n <= 0) return null;
  double tot = 0.0;
  for (int i = 0; i < n; i++) tot += wt(z, (String) ok.get(i));
  if (!(tot > 0.0)) return (String) ok.get(0);
  double x = u * tot;
  for (int i = 0; i < n; i++) { x -= wt(z, (String) ok.get(i)); if (x < 0.0) return (String) ok.get(i); }
  return (String) ok.get(n - 1);
}""")
# combat.cageSkip: an item a Soul Cage never makes ("X*" = every id starting with X)
M(cmb, r"""
public static boolean skip(String id) {
  String[] a = @PKG@.ShCfg.CB_SKIP;
  if (id == null || a == null) return false;
  for (int i = 0; i < a.length; i++) {
    String v = a[i];
    if (v == null || v.length() == 0) continue;
    if (v.endsWith("*")) { if (id.startsWith(v.substring(0, v.length() - 1))) return true; }
    else if (id.equals(v)) return true;
  }
  return false;
}""")
# THE SOUL CAGE ON THE POOL: n made items of a zone-z island of `size` -> its pool's vanilla drops in the mix a fight of the pool gives
# (each role's items at their average count a kill: DROP_IDS "item:count,...", x the role's vanilla spawn odds wt - fix, critic; the
# combat.cageSkip items left out - fix, critic); whole numbers by largest remainder (the first item wins a tie). No known drops = all n as
# `fallback`.
# -> Object[]{ String[] ids, long[] qty } (the qty add up to n)
M(cmb, r"""
public static Object[] split(int z, int size, long n, String fallback) {
  String[] rl = allRoles(z, size);
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList ws = new java.util.ArrayList();
  for (int i = 0; i < rl.length; i++) {
    double rw = wt(z, rl[i]);   // fix (critic): the role's vanilla spawn odds
    String[] it = csv(dropsOf(rl[i]));
    for (int j = 0; j < it.length; j++) {
      int c = it[j].lastIndexOf(':');
      String id = c > 0 ? it[j].substring(0, c) : it[j];
      double w = 1.0;
      if (c > 0) { try { w = Double.parseDouble(it[j].substring(c + 1)); } catch (Throwable x) { w = 0.0; } }
      w = w * rw;
      if (!(w > 0.0) || id.length() == 0 || skip(id)) continue;   // fix (critic): combat.cageSkip
      int at = ids.indexOf(id);
      if (at < 0) { ids.add(id); ws.add(Double.valueOf(w)); }
      else ws.set(at, Double.valueOf(((Double) ws.get(at)).doubleValue() + w));
    }
  }
  long nn = n < 0L ? 0L : n;
  if (ids.isEmpty()) return new Object[] { new String[] { fallback }, new long[] { nn } };
  double tot = 0.0;
  for (int i = 0; i < ws.size(); i++) tot += ((Double) ws.get(i)).doubleValue();
  int m = ids.size();
  long[] q = new long[m];
  double[] fr = new double[m];
  long given = 0L;
  for (int i = 0; i < m; i++) {
    double x = (double) nn * ((Double) ws.get(i)).doubleValue() / tot;
    q[i] = (long) Math.floor(x + 0.000000001);
    fr[i] = x - (double) q[i];
    given += q[i];
  }
  long left = nn - given;
  int guard = 0;
  while (left > 0L && guard < m + 4) {
    int b = 0;
    for (int i = 1; i < m; i++) if (fr[i] > fr[b] + 0.000000000001) b = i;
    q[b] = q[b] + 1L;
    fr[b] = -1.0;
    left--;
    guard++;
  }
  if (left > 0L) q[0] = q[0] + left;
  return new Object[] { arr(ids), q };
}""")
M(cmb, r"""
public static Object[] dropsFor(java.util.Properties p, int slot, long n) {
  int t = @PKG@.ShIsl.ty(CK, p, slot);
  return split(zoneOf(t), @PKG@.ShMath.size(CK, p, slot), n, @PKG@.ShIsl.PROD[t]);
}""")
# the 3 sub-upgrades' material templates (combat: combat.mat.*; the other shards: isl.mat.*)
M(cmb, r"""
public static String subMat(int kd, int which) {
  if (kd == CK) { String[] a = @PKG@.ShCfg.CB_MAT; if (which >= 0 && which < a.length) return a[which]; }
  return which == 0 ? @PKG@.ShCfg.MAT_AMT : (which == 1 ? @PKG@.ShCfg.MAT_DECO : @PKG@.ShCfg.MAT_IRR);
}""")
# texts (the Map tab): now / next of each sub-upgrade, the pool
M(cmb, r"""
public static String lvTxt(int z, int size, int lvl) {
  int lo = lvLo(z, size, lvl);
  int hi = lvHi(z, size, lvl);
  return lo == hi ? String.valueOf(lo) : lo + "-" + hi;
}""")
M(cmb, r"""
public static String nowTxt(int z, int size, int a, int d, int i) {
  int c = cap(size, a);
  int l = lowerCap(size, a);
  return c + " at once" + (l > 0 ? " (" + l + " below)" : "") + " - Lv " + lvTxt(z, size, d) + " - every " + respawnSec(size, i) + " s";
}""")
M(cmb, r"""
public static String nextTxt(int z, int size, int w, int lv) {
  if (w == 0) return cap(size, lv) + " -> " + cap(size, lv + 1) + " mobs at once";
  if (w == 1) return "Lv " + lvTxt(z, size, lv) + " -> " + lvTxt(z, size, lv + 1);
  return "every " + respawnSec(size, lv) + " s -> " + respawnSec(size, lv + 1) + " s";
}""")
M(cmb, r"""
public static String poolTxt(int z, int size) {
  int u = roles(z, size, 0).length;
  int l = roles(z, size, 1).length;
  return u + " kinds of mobs" + (l > 0 ? " + " + l + " in the cavern" : "");
}""")
# fix (critic r5combat2): the Map tab NAMES the mobs - the roles a size ADDS to the upper island (1 = the Small pool, 2 = Medium's, 3 =
# Large's upper ones), "Skeleton Fighter, Wolf Black +3 more" within maxC characters (the width harness measures every one)
M(cmb, "public static String pretty(String r) { return r == null ? \\"\\" : r.replace('_', ' '); }")
M(cmb, r"""
public static String[] adds(int z, int size) {
  String[] P = @PKG@.ShCfg.CB_POOL;
  int zz = z < 0 ? 0 : (z >= ZN ? ZN - 1 : z);
  int si = size < 1 ? 1 : (size > 3 ? 3 : size);
  int i = zz * 4 + si - 1;
  return i < P.length ? csv(P[i]) : new String[0];
}""")
M(cmb, r"""
public static String namesTxt(String[] a, int maxC) {
  String out = "";
  int k = 0;
  for (int i = 0; i < a.length; i++) {
    String n = pretty(a[i]);
    if (k > 0 && out.length() + 2 + n.length() > maxC) break;
    out = k > 0 ? out + ", " + n : n;
    k++;
  }
  if (k < a.length) out = out + " +" + (a.length - k) + " more";
  return out;
}""")
# fix (critic r5combat2): who may hit an NPC in a shard world ("hurt") - a player the combat tick saw in that world's Combat region in the
# last 3 s (ShFight.tickWorld marks them every second); everyone else / every other NPC stays protected. UUID -> Object[] { world, Long ms }
F(cmb, "public static final java.util.concurrent.ConcurrentHashMap HERE = new java.util.concurrent.ConcurrentHashMap();")
F(cmb, "public static final long HERE_MS = 3000L;")
M(cmb, r"""
public static void mark(java.util.UUID u, String wn, long now) {
  if (u == null || wn == null) return;
  if (HERE.size() > 4096) HERE.clear();
  HERE.put(u, new Object[] { wn, Long.valueOf(now) });
}""")
M(cmb, r"""
public static boolean mayHurt(String wn, Object who, long now) {
  if (!(who instanceof java.util.UUID) || wn == null) return false;
  Object o = HERE.get(who);
  if (!(o instanceof Object[])) return false;
  Object[] r = (Object[]) o;
  if (!wn.equals(r[0])) return false;
  long d = now - ((Long) r[1]).longValue();
  return d >= 0L && d <= HERE_MS;
}""")
# fix (critic r5combat2): COLLECT never lets a full inventory pick the drops - the largest count m <= n whose split fits in what arrived
# (have[j] per id, the split's id order); lo always fits (0 does), so the answer is a mix the player may keep exactly
M(cmb, r"""
public static boolean fits(Object[] s, long[] have) {
  long[] q = (long[]) s[1];
  for (int j = 0; j < q.length; j++) if (q[j] > (j < have.length ? have[j] : 0L)) return false;
  return true;
}""")
M(cmb, r"""
public static long fit(int z, int size, long n, String fallback, long[] have) {
  long lo = 0L;
  long hi = n < 0L ? 0L : n;
  while (lo < hi) {
    long mid = lo + (hi - lo + 1L) / 2L;
    if (fits(split(z, size, mid, fallback), have)) lo = mid; else hi = mid - 1L;
  }
  if (lo <= 0L) return 0L;
  long[] fq = (long[]) split(z, size, n, fallback)[1];   // fix (critic r5combat2 2nd round): every kind of the full take must be in the part
  long[] gq = (long[]) split(z, size, lo, fallback)[1];   // given - else 1 slot a Collect would hand out only the most common drop, again
  for (int j = 0; j < fq.length; j++) if (fq[j] > 0L && (j >= gq.length || gq[j] <= 0L)) return 0L;   // and again (a free slot each)
  return lo;
}""")
M(cmb, r"""
public static long fitFor(java.util.Properties p, int slot, long n, long[] have) {
  int t = @PKG@.ShIsl.ty(CK, p, slot);
  return fit(zoneOf(t), @PKG@.ShMath.size(CK, p, slot), n, @PKG@.ShIsl.PROD[t], have);
}""")

# ================= ShGeo: the region layout (spec 9.1), pure maths - every block the region wants =================''')

# ---------------------------------------------------------------------------------------------------- 6. ShGeo: the combat land + the cavern + the stair
P.rep('''M(geo, "public static int ox(int kd) { return 1024 * kd; }")''', '''# 0.4.11: the combat islands' land (zone palettes = IDS indexes; quarters q = (QX, QZ) signs; trees of the Medium / Large forest edge)
for f in ("public static final int[] CFLOOR = new int[] { %s };" % ", ".join(str(_r[0]) for _r in CZ_PALI),
          "public static final int[] CRIM = new int[] { %s };" % ", ".join(str(_r[1]) for _r in CZ_PALI),
          "public static final int[] CRISE = new int[] { %s };" % ", ".join(str(_r[2]) for _r in CZ_PALI),
          "public static final int[] CTOP = new int[] { %s };" % ", ".join(str(_r[3]) for _r in CZ_PALI),
          "public static final int[] CTRUNK = new int[] { %s };" % ", ".join(str(_r[4]) for _r in CZ_PALI),
          "public static final int[] CLEAF = new int[] { %s };" % ", ".join(str(_r[5]) for _r in CZ_PALI),
          "public static final int[] CCORN = new int[] { %s };" % ", ".join(str(_r[6]) for _r in CZ_PALI),
          "public static final int[] CPLANT = new int[] { %s };" % ", ".join(str(_r[7]) for _r in CZ_PALI),
          "public static final int[] CCAVE = new int[] { %s };" % ", ".join(str(_r[8]) for _r in CZ_PALI),
          "public static final int[] CCRYS = new int[] { %s };" % ", ".join(str(_r[9]) for _r in CZ_PALI),
          "public static final int CTORCH = %d;" % CZ_ONEI[0], "public static final int CFENCE = %d;" % CZ_ONEI[1], "public static final int CLAVA = %d;" % CZ_ONEI[2],
          "public static final int[] QX = new int[] { 1, 1, -1, -1 };", "public static final int[] QZ = new int[] { -1, 1, 1, -1 };",
          "public static final int[] TRM = new int[] { 4, 7, 7, 4, 8, 8, 2, 9 };", "public static final int[] TRL = new int[] { 11, 5, 5, 11, 11, 11, 12, 8 };",
          "public static final int CAVE_R = 12;", "public static final int CAVE_FY = %d;" % (Y - 14), "public static final int CAVE_TY = %d;" % (Y - 4),
          "public static final java.util.concurrent.ConcurrentHashMap CSPOT = new java.util.concurrent.ConcurrentHashMap();"):
    F(geo, f)
assert Y - 14 > Y - 20, "0.4.11: the cavern floor stays above the void rescue line (ShSweep.RESCUE_Y)"
assert (Y - 14) >> 5 == 2 and (Y - 4) >> 5 == 3, "0.4.11: the cavern is in chunk section 2 (+ its ceiling in 3)"
M(geo, "public static int ox(int kd) { return 1024 * kd; }")''')
P.rep('''# the island of `size` around slot `slot` of kind kd (out: x, y, z, kind = index into IDS or a 0.4.8 cell kind). p = the profile (null = a''',
      '''# 0.4.11 THE COMBAT LAND. A quarter q of an island is free when no walkway (gap: toward its bridge / the islands bridged onto it) crosses
# its diagonal; quads(slot) = the quarters, free ones first: [0] the Large stair, [1] the rocky rise, [2] the forest edge, [3] the corner
M(geo, r"""
public static boolean qGap(int slot, int q) {
  for (int d = 3; d <= 12; d++) if (gap(slot, QX[q] * d, QZ[q] * d)) return true;
  return false;
}""")
M(geo, r"""
public static int[] quads(int slot) {
  int[] o = new int[4];
  boolean[] used = new boolean[4];
  int n = 0;
  for (int q = 0; q < 4; q++) if (!qGap(slot, q)) { o[n] = q; n++; used[q] = true; }
  for (int q = 0; q < 4; q++) if (!used[q]) { o[n] = q; n++; }
  return o;
}""")
M(geo, r"""
public static boolean inQ(int q, int dx, int dz, int a, int b) {
  int x = dx * QX[q];
  int z = dz * QZ[q];
  return x >= a && x <= b && z >= a && z <= b;
}""")
# the stair shaft of a Large combat island (centre 9, 9 in its quarter; the 5 x 5 around it is kept clear) + the cavern's lava rock
M(geo, r"""
public static boolean nearShaft(int sq, int dx, int dz) {
  int x = dx - 9 * QX[sq];
  int z = dz - 9 * QZ[sq];
  return x >= -2 && x <= 2 && z >= -2 && z <= 2;
}""")
M(geo, r"""
public static boolean isLava(int sq, int dx, int dz) {
  int x = -dx * QX[sq];
  int z = -dz * QZ[sq];
  if (x >= 7 && x <= 8 && z >= 7 && z <= 8) return true;
  int z2 = dz * QZ[sq];
  return x >= 7 && x <= 8 && z2 >= 2 && z2 <= 3;
}""")
# a tree of the forest edge: trunk 3 high (a plain block - put back if felled), leaves only on AIR; skipped when it would touch a walkway
M(geo, r"""
public static void ctree(java.util.ArrayList out, int slot, int cx, int cz, int dx, int dz, int trunk, int leaf) {
  for (int a = -1; a <= 1; a++) for (int b = -1; b <= 1; b++) if (gap(slot, dx + a, dz + b)) return;
  int x = cx + dx;
  int z = cz + dz;
  for (int y = Y + 1; y <= Y + 3; y++) add(out, x, y, z, trunk);
  for (int a = -1; a <= 1; a++) for (int b = -1; b <= 1; b++) {
    if (a != 0 || b != 0) out.add(new int[] { x + a, Y + 3, z + b, DECO_K, leaf });
    out.add(new int[] { x + a, Y + 4, z + b, DECO_K, leaf });
  }
  out.add(new int[] { x, Y + 5, z, DECO_K, leaf });
}""")
# THE SPIRAL STAIR (spec 10 "reached by a spiral stair"): a pillar from the cavern floor to the island floor, 8 steps around it per turn (one
# block down each), the ring AIR between; a fence round the top with the way in next to the first step
M(geo, r"""
public static void stair(java.util.ArrayList out, int x0, int z0, int z) {
  for (int y = CAVE_FY + 1; y <= Y; y++) add(out, x0, y, z0, CCAVE[z]);
  for (int y = CAVE_FY + 1; y <= Y; y++) {
    int i = Y - 1 - y;
    for (int k = 0; k < 8; k++) {
      int[] q = ringPos(1, k);
      add(out, x0 + q[0], y, z0 + q[1], (i >= 0 && (i % 8) == k) ? BRICK : AIR);
    }
  }
  for (int k = 0; k < 16; k++) {
    if (k <= 1 || k == 15) continue;
    int[] q = ringPos(2, k);
    out.add(new int[] { x0 + q[0], Y + 1, z0 + q[1], DECO_K, CFENCE });
  }
}""")
# THE LOWER PART (spec 10: "a lower section modelled after the deep caverns"): a 23 x 23 x 9 chamber under the Large island (the zone's rock:
# floor, walls, ceiling, 4 pillars), glowing lava rock in the floor, crystals along the walls + torches (only on AIR), the stair down
M(geo, r"""
public static void cavern(java.util.ArrayList out, int cx, int cz, int z, int sq) {
  int R = CAVE_R;
  for (int dx = -R; dx <= R; dx++) for (int dz = -R; dz <= R; dz++) {
    int ax = dx < 0 ? -dx : dx;
    int az = dz < 0 ? -dz : dz;
    int x = cx + dx;
    int zc = cz + dz;
    add(out, x, CAVE_FY, zc, isLava(sq, dx, dz) ? CLAVA : CCAVE[z]);
    add(out, x, CAVE_TY, zc, CCAVE[z]);
    if (ax == R || az == R || (ax == 5 && az == 5)) for (int y = CAVE_FY + 1; y < CAVE_TY; y++) add(out, x, y, zc, CCAVE[z]);
  }
  for (int i = 2; i < 80; i += 5) {
    int[] q = ringPos(10, i);
    if (nearShaft(sq, q[0], q[1])) continue;
    out.add(new int[] { cx + q[0], CAVE_FY + 1, cz + q[1], DECO_K, CCRYS[z] });
  }
  for (int i = 0; i < 48; i += 6) {
    int[] q = ringPos(6, i);
    out.add(new int[] { cx + q[0], CAVE_FY + 1, cz + q[1], DECO_K, CTORCH });
  }
  stair(out, cx + 9 * QX[sq], cz + 9 * QZ[sq], z);
}""")
# A COMBAT ISLAND of zone z at size si (spec 10): Small = a plains arena of the zone's ground + torches; Medium + the rocky rise and the
# forest edge; Large + the corner (swamp / oasis / snow / gravel / lava rock) and the cavern under it. The centre 3 x 3 = the totem pads.
M(geo, r"""
public static void combat(java.util.ArrayList out, int kd, java.util.Properties p, int slot, int si, int zone) {
  int h = HALF[si - 1];
  int cx = ox(kd) + SX[slot];
  int cz = OZ + SZ[slot];
  int z = zone < 0 ? 0 : (zone > 4 ? 4 : zone);
  int[] qs = quads(slot);
  for (int dx = -h; dx <= h; dx++) for (int dz = -h; dz <= h; dz++) {
    int ax = dx < 0 ? -dx : dx;
    int az = dz < 0 ? -dz : dz;
    if (ax == h && az == h) continue;
    int x = cx + dx;
    int zc = cz + dz;
    if (ax == h || az == h) add(out, x, Y, zc, CRIM[z]);
    else if (ax <= 1 && az <= 1) add(out, x, Y, zc, BRICK);
    else if (si >= 3 && inQ(qs[3], dx, dz, 8, 13)) add(out, x, Y, zc, CCORN[z]);
    else add(out, x, Y, zc, CFLOOR[z]);
    add(out, x, Y - 1, zc, DIRT);
    if (ax <= h - 2 && az <= h - 2) add(out, x, Y - 2, zc, STONE);
    if (ax <= h - 4 && az <= h - 4) add(out, x, Y - 3, zc, STONE);
  }
  int r = h - 1;
  for (int i = 3; i < 8 * r; i += 6) {
    int[] q = ringPos(r, i);
    if (gap(slot, q[0], q[1])) continue;
    out.add(new int[] { cx + q[0], Y + 1, cz + q[1], DECO_K, CTORCH });
  }
  if (si >= 2) {
    int rq = qs[1];
    for (int a = 3; a <= 9; a++) for (int b = 3; b <= 9; b++) {
      double d = Math.sqrt((double) ((a - 6) * (a - 6) + (b - 6) * (b - 6)));
      if (d > 3.2) continue;
      int dx = QX[rq] * a;
      int dz = QZ[rq] * b;
      if (gap(slot, dx, dz)) continue;
      add(out, cx + dx, Y + 1, cz + dz, CRISE[z]);
      if (d <= 1.6) add(out, cx + dx, Y + 2, cz + dz, CTOP[z]);
    }
    int fq = qs[2];
    for (int i = 0; i < TRM.length; i += 2) ctree(out, slot, cx, cz, QX[fq] * TRM[i], QZ[fq] * TRM[i + 1], CTRUNK[z], CLEAF[z]);
    if (si >= 3) for (int i = 0; i < TRL.length; i += 2) ctree(out, slot, cx, cz, QX[fq] * TRL[i], QZ[fq] * TRL[i + 1], CTRUNK[z], CLEAF[z]);
  }
  if (si >= 3) {
    int oq = qs[3];
    for (int a = 8; a <= 13; a++) for (int b = 8; b <= 13; b++) {
      if (((a + b) % 3) != 0) continue;
      int dx = QX[oq] * a;
      int dz = QZ[oq] * b;
      if (gap(slot, dx, dz)) continue;
      out.add(new int[] { cx + dx, Y + 1, cz + dz, DECO_K, CPLANT[z] });
    }
    cavern(out, cx, cz, z, qs[0]);
  }
}""")
# where a combat island's mobs may spawn (dx, dz pairs; part 0 = the island floor, part 1 = the cavern floor): never on the totem pads, the
# stair or its fence, a pillar or the lava rock. The block checks (floor solid, 2 free above) are made at spawn time.
M(geo, r"""
public static int[] cspots(int slot, int size, int part) {
  String key = slot + "|" + size + "|" + part;
  Object c = CSPOT.get(key);
  if (c instanceof int[]) return (int[]) c;
  int si = size < 1 ? 1 : (size > 3 ? 3 : size);
  int h = HALF[si - 1];
  int sq = quads(slot)[0];
  java.util.ArrayList a = new java.util.ArrayList();
  if (part == 0) {
    for (int dx = -(h - 1); dx <= h - 1; dx++) for (int dz = -(h - 1); dz <= h - 1; dz++) {
      if ((dx >= -1 && dx <= 1) && (dz >= -1 && dz <= 1)) continue;
      if (si >= 3 && nearShaft(sq, dx, dz)) continue;
      a.add(Integer.valueOf(dx));
      a.add(Integer.valueOf(dz));
    }
  } else if (si >= 3) {
    for (int dx = -10; dx <= 10; dx++) for (int dz = -10; dz <= 10; dz++) {
      if (nearShaft(sq, dx, dz) || isLava(sq, dx, dz)) continue;
      int ax = dx < 0 ? -dx : dx;
      int az = dz < 0 ? -dz : dz;
      if (ax == 5 && az == 5) continue;
      a.add(Integer.valueOf(dx));
      a.add(Integer.valueOf(dz));
    }
  }
  int[] r = new int[a.size()];
  for (int i = 0; i < r.length; i++) r[i] = ((Integer) a.get(i)).intValue();
  CSPOT.put(key, r);
  return r;
}""")
# the island of `size` around slot `slot` of kind kd (out: x, y, z, kind = index into IDS or a 0.4.8 cell kind). p = the profile (null = a''')
P.rep('''  if (st.equals("mine")) { cave(out, kd, slot, si, t, amt, ltd, lti); return; }''',
      '''  if (st.equals("mine")) { cave(out, kd, slot, si, t, amt, ltd, lti); return; }
  if (kd == @PKG@.ShCombat.CK) { combat(out, kd, p, slot, si, @PKG@.ShCombat.zoneOf(t)); return; }   // 0.4.11: the zone islands (spec 10)''')

# ---------------------------------------------------------------------------------------------------- 7. ShFill: the cavern's chunk section (y 64-95) is loaded too
P.rep('''    java.util.HashSet seen = new java.util.HashSet();
    java.util.ArrayList chl = new java.util.ArrayList();
    for (int i = 0; i < want.size(); i++) {
      int[] b = (int[]) want.get(i);
      int cx0 = b[0] >> 5; int cz0 = b[2] >> 5;
      if (seen.add(cx0 + "," + cz0)) chl.add(new int[] { cx0, cz0 });
    }''', '''    java.util.HashSet seen = new java.util.HashSet();
    java.util.HashSet low = new java.util.HashSet();   // 0.4.11: chunks with a cell under y 96 (a Large combat island's cavern = section 2)
    java.util.ArrayList chl = new java.util.ArrayList();
    for (int i = 0; i < want.size(); i++) {
      int[] b = (int[]) want.get(i);
      int cx0 = b[0] >> 5; int cz0 = b[2] >> 5;
      if (seen.add(cx0 + "," + cz0)) chl.add(new int[] { cx0, cz0 });
      if (b[1] < 96) low.add(cx0 + "," + cz0);
    }''')
P.rep('''    java.util.concurrent.CompletableFuture[] parts = new java.util.concurrent.CompletableFuture[n * 2];
    for (int i = 0; i < n; i++) {
      int[] c = (int[]) chl.get(i);
      job.cxs[i] = c[0];
      job.czs[i] = c[1];
      parts[2 * i] = cs.getChunkReferenceAsync(@CHU@.indexChunk(c[0], c[1]));
      parts[2 * i + 1] = cs.getChunkSectionReferenceAsync(c[0], 3, c[1]);
    }
    java.util.concurrent.CompletableFuture.allOf(parts).whenComplete(job);''', '''    java.util.ArrayList pl = new java.util.ArrayList();
    for (int i = 0; i < n; i++) {
      int[] c = (int[]) chl.get(i);
      job.cxs[i] = c[0];
      job.czs[i] = c[1];
      pl.add(cs.getChunkReferenceAsync(@CHU@.indexChunk(c[0], c[1])));
      pl.add(cs.getChunkSectionReferenceAsync(c[0], 3, c[1]));
      if (low.contains(c[0] + "," + c[1])) pl.add(cs.getChunkSectionReferenceAsync(c[0], 2, c[1]));   // 0.4.11
    }
    java.util.concurrent.CompletableFuture[] parts = new java.util.concurrent.CompletableFuture[pl.size()];
    for (int i = 0; i < parts.length; i++) parts[i] = (java.util.concurrent.CompletableFuture) pl.get(i);
    java.util.concurrent.CompletableFuture.allOf(parts).whenComplete(job);''')

# ---------------------------------------------------------------------------------------------------- 8. ShGate: hitting a mob in a shard world
P.rep('''  if (a.equals("pickup") || a.equals("drop")) return Boolean.TRUE;''', '''  if (a.equals("pickup") || a.equals("drop")) return Boolean.TRUE;
  if (a.equals("hurt")) return Boolean.valueOf(@PKG@.ShCombat.mayHurt(world, who, System.currentTimeMillis()));   // 0.4.11: the combat islands' mobs - only a player the combat tick saw in the Combat region (fix, critic: SkyyIslands 0.5.8 asks for every hit on ANY NPC)''')
P.rep('''public static Boolean allowed(String world, String action, String block) {''',
      '''public static Boolean allowed(String world, String action, String block, Object who) {''')   # 0.4.11: + the player (a hit's attacker)
P.rep('''M(gate, r"""
public Object apply(Object o) {''', '''M(gate, "public static Boolean allowed(String world, String action, String block) { return allowed(world, action, block, null); }")
M(gate, r"""
public Object apply(Object o) {''')
P.rep('''    return allowed(String.valueOf(a[0]), a[1] == null ? null : String.valueOf(a[1]), a.length > 2 && a[2] != null ? String.valueOf(a[2]) : "");''',
      '''    return allowed(String.valueOf(a[0]), a[1] == null ? null : String.valueOf(a[1]), a.length > 2 && a[2] != null ? String.valueOf(a[2]) : "", a.length > 3 ? a[3] : null);   // 0.4.11: + the player''')

# ---------------------------------------------------------------------------------------------------- 9. Collect: the Soul Cage gives the pool's drops
P.rep('''      if (take[i] > 0L) {
        int t = @PKG@.ShIsl.ty(kd, p, i);
        boolean sm = @PKG@.ShTotem.smelts(kd, p, i) && @PKG@.ShIsl.SMELT[t].length() > 0;''', '''      if (take[i] > 0L && kd == @PKG@.ShCombat.CK) {   // 0.4.11: a combat island's stored count = its mob pool's drops (ShCombat.split)
        Object[] dm = @PKG@.ShCombat.dropsFor(p, i, take[i]);
        String[] di = (String[]) dm[0];
        long[] dq = (long[]) dm[1];
        long[] dg = new long[di.length];
        boolean shortG = false;
        boolean prog = true;
        int pass = 0;
        while (prog && pass < 4000) {   // round-robin, a stack of 100 at a time: one kind never takes every free slot
          prog = false;
          pass++;
          for (int j = 0; j < di.length; j++) {
            if (dq[j] <= dg[j] || di[j] == null || di[j].length() == 0) continue;
            long g0 = @PKG@.ShInv.give(cs, di[j], Math.min(100L, dq[j] - dg[j]));
            if (g0 > 0L) { dg[j] += g0; prog = true; }
          }
        }
        for (int j = 0; j < di.length; j++) if (dg[j] < dq[j]) shortG = true;
        if (shortG) {   // fix (critic r5combat2): a full inventory never picks the drops - keep exactly the mix of the largest count that fitted
          long fm = @PKG@.ShCombat.fitFor(p, i, take[i], dg);
          long[] fq = (long[]) @PKG@.ShCombat.dropsFor(p, i, fm)[1];
          for (int j = 0; j < di.length; j++) {
            long ex = dg[j] - (j < fq.length ? fq[j] : 0L);
            if (ex > 0L && di[j] != null) dg[j] = dg[j] - @PKG@.ShInv.take(cs, di[j], ex);   // counted: what really came back
          }
        }
        long cdel = 0L;
        for (int j = 0; j < di.length; j++) {
          long g = dg[j];
          if (g <= 0L) continue;
          cdel += g;
          got.put(di[j], Long.valueOf((got.get(di[j]) == null ? 0L : ((Long) got.get(di[j])).longValue()) + g));
          cred.put(di[j], Long.valueOf((cred.get(di[j]) == null ? 0L : ((Long) cred.get(di[j])).longValue()) + g));
        }
        baseGiven += cdel;
        xpD += (double) cdel * xi;
        bm[i] = take[i] - cdel;
        backM += bm[i];
      } else if (take[i] > 0L) {
        int t = @PKG@.ShIsl.ty(kd, p, i);
        boolean sm = @PKG@.ShTotem.smelts(kd, p, i) && @PKG@.ShIsl.SMELT[t].length() > 0;''')

P.rep('''  if (baseGiven + gBonus <= 0L) return "-Your inventory is full - nothing was collected.";''',
      '''  if (baseGiven + gBonus <= 0L) return kd == @PKG@.ShCombat.CK ? "-Not enough room - a combat Collect gives every kind of drop together (a free slot each). Nothing was collected." : "-Your inventory is full - nothing was collected.";   // 0.4.11 fix''')

# ---------------------------------------------------------------------------------------------------- 10. buying a zone: the class level; the combat sub materials
P.rep('''  double cv = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[t]));   // the bridge asked outside the lock
  String res;
  int slot;''', '''  double cv = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[t]));   // the bridge asked outside the lock
  int zneed = kd == @PKG@.ShCombat.CK ? @PKG@.ShCombat.need(ti) : 0;   // 0.4.11 (spec 10): Zone N needs class level combat.zoneLevel.N
  if (zneed > 0) {
    int clv = @PKG@.ShIsl.level(u, kd);
    if (clv == -2) return "-Your class level could not be read right now - try again in a moment.";
    if (clv == -1) return "-The " + @PKG@.ShIsl.tname(t) + " island needs class level " + zneed + " - no class levels on this server (Server Setup -> Shards -> Combat islands: 0 = any).";   // fix (critic): no skills mod = locked, never open
    if (clv < zneed) return "-The " + @PKG@.ShIsl.tname(t) + " island needs class level " + zneed + " (you: " + clv + ").";
  }
  String res;
  int slot;''')
P.rep('''    String tm = which == 0 ? @PKG@.ShCfg.MAT_AMT : (which == 1 ? @PKG@.ShCfg.MAT_DECO : @PKG@.ShCfg.MAT_IRR);''',
      '''    String tm = @PKG@.ShCombat.subMat(kd, which);   // 0.4.11: combat islands = combat.mat.*''')
P.rep('''      long sc = @PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, lv + 1), tcv[s]);
      String tm = w == 0 ? @PKG@.ShCfg.MAT_AMT : (w == 1 ? @PKG@.ShCfg.MAT_DECO : @PKG@.ShCfg.MAT_IRR);''', '''      long sc = @PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, lv + 1), tcv[s]);
      String tm = @PKG@.ShCombat.subMat(kd, w);''')
P.rep('''        long sc = @PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, lv + 1), tcv[s]);
        String tm = w == 0 ? @PKG@.ShCfg.MAT_AMT : (w == 1 ? @PKG@.ShCfg.MAT_DECO : @PKG@.ShCfg.MAT_IRR);''', '''        long sc = @PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, lv + 1), tcv[s]);
        String tm = @PKG@.ShCombat.subMat(kd, w);''')

# ---------------------------------------------------------------------------------------------------- 11. ShFight: the spawner + the night hold (world thread)
P.rep('''# ================= ShTick: 1 s scheduler tick - idle unload + queue, regrow, sweep, particles, pending placements =================''',
      '''# ================= 0.4.11 ShFight: THE COMBAT ISLANDS LIVE (research/Starter-Archipelago-Spec.md 10; ShTick runs it every second on the shard
# world's own thread). 1. ALWAYS NIGHT: a player in the Combat region gets the world's time settings with the clock paused + the next
# midnight (the packets WorldTimeResource sends), again every 3 s; out of the region = the real time again (sendTimePackets). The world's
# own clock is never touched. 2. THE SPAWNER: per island part (upper / the Large cavern) up to "Mobs at once" mobs while an owner / co-op
# member stands there AND moved within combat.afkSec; one a second while filling; a dead mob's place comes back after "Spawn speed" s;
# never within combat.minDist of a player, only on a solid floor with 2 free blocks above; combat.maxPerHour per profile (token bucket);
# a mob off its island's leash is removed; nobody there for 30 s = the part's mobs are removed; mobs a restart left in the chunks are found
# (pool role in the box) and counted. Engine calls go through e*() (TEST = the harness's simulated world).
fight = mk("ShFight", None, ("java.lang.Runnable",))
for f in ("public @WLD@ w;",
          "public static final java.util.concurrent.ConcurrentHashMap MOBS = new java.util.concurrent.ConcurrentHashMap();",    # pkey|slot|part -> ArrayList uuid
          "public static final java.util.concurrent.ConcurrentHashMap DUE = new java.util.concurrent.ConcurrentHashMap();",     # pkey|slot|part -> ArrayList Long (ms)
          "public static final java.util.concurrent.ConcurrentHashMap EMPTY = new java.util.concurrent.ConcurrentHashMap();",   # pkey|slot|part -> Long (nobody there since)
          "public static final java.util.concurrent.ConcurrentHashMap SCAN = new java.util.concurrent.ConcurrentHashMap();",    # pkey|slot|part -> Long (last leftover scan)
          "public static final java.util.concurrent.ConcurrentHashMap MOVED = new java.util.concurrent.ConcurrentHashMap();",   # UUID -> double[] { x, y, z, ms moved }
          "public static final java.util.concurrent.ConcurrentHashMap BUCKET = new java.util.concurrent.ConcurrentHashMap();",  # pkey -> double[] { tokens, ms }
          "public static final java.util.concurrent.ConcurrentHashMap NIGHT = new java.util.concurrent.ConcurrentHashMap();",   # UUID -> Object[] { world, Long ms, world UUID }
          "public static final java.util.concurrent.ConcurrentHashMap ROLEOK = new java.util.concurrent.ConcurrentHashMap();",  # role -> Boolean
          "public static final long GRACE = 30000L;", "public static final long NIGHT_MS = 1000L;", "public static final double BURST = 18.0;",
          # fix (critic r5combat2): the vanilla TimePacketSystem broadcasts the real time every second - ShNightF drops it for a held player
          # (night sent < HOLD_MS ago in the same world); OWN marks our own packets on this thread
          "public static final long HOLD_MS = 3500L;", "public static final ThreadLocal OWN = new ThreadLocal();",
          "public static volatile @PFI@ FILTER = null;", "public static volatile java.util.UUID TEST_WID = null;",
          "public static volatile java.util.function.Function TEST = null;", "public static volatile long SEED = 0L;"):
    F(fight, f)
for _c in ("RUNS", "SPAWNS", "DESPAWNS", "GONE", "ADOPTED", "NIGHTS", "RESTORES", "AFK", "LID", "NOSPOT"):
    F(fight, "public static final java.util.concurrent.atomic.AtomicLong %s = new java.util.concurrent.atomic.AtomicLong();" % _c)
F(fight, "public boolean flush;")
C(fight, "public ShFight(@WLD@ w) { this.w = w; this.flush = false; }")
C(fight, "public ShFight(@WLD@ w, boolean flush) { this.w = w; this.flush = flush; }")   # the world's last player left: its mobs go now
M(fight, r"""
public static Object t(String op, Object a, Object b, Object c, Object d) {
  java.util.function.Function f = TEST;
  return f == null ? null : f.apply(new Object[] { op, a, b, c, d });
}""")
M(fight, r"""
public static boolean eRole(String role) {
  if (role == null || role.length() == 0) return false;
  if (TEST != null) return Boolean.TRUE.equals(t("role", role, null, null, null));
  Object c = ROLEOK.get(role);
  if (c instanceof Boolean) return ((Boolean) c).booleanValue();
  boolean ok = false;
  try { ok = @NPCP@.get().hasRoleName(role); } catch (Throwable x) { ok = false; }
  if (ROLEOK.size() > 2000) ROLEOK.clear();
  ROLEOK.put(role, Boolean.valueOf(ok));
  if (!ok) @PKG@.ShCfg.warnOnce("role:" + role, "combat islands: this server has no NPC role " + role + " - left out of the pool (Server Setup -> Shards -> Combat islands)");
  return ok;
}""")
# NPCPlugin.spawnNPC(store, role, null, pos, rot) = the SkyyIslands camp's call shape (world thread); its UUID or null
M(fight, r"""
public static String eSpawn(@WLD@ w, String role, double x, double y, double z) {
  if (TEST != null) { Object r = t("spawn", role, Double.valueOf(x), Double.valueOf(y), Double.valueOf(z)); return r == null ? null : String.valueOf(r); }
  try {
    @ST@ st = w.getEntityStore().getStore();
    @R3F@ rot = new @R3F@();
    rot.setYaw((float) (Math.random() * 6.283185307179586));
    @PAIR@ pr = @NPCP@.get().spawnNPC(st, role, (String) null, (@V3DC@) new @V3D@(x, y, z), (@R3C@) rot);
    @REF@ e = pr == null ? null : (@REF@) pr.first();
    if (e == null || !e.isValid()) return null;
    @UUC@ uc = (@UUC@) st.getComponent(e, @UUC@.getComponentType());
    return uc == null || uc.getUuid() == null ? null : uc.getUuid().toString();
  } catch (Throwable x) { @PKG@.ShCfg.warnOnce("spawn:" + role, "a combat island mob (" + role + ") could not be spawned (logged once): " + x); return null; }
}""")
# a tracked mob's position (null = dead, removed or not loaded)
M(fight, r"""
public static double[] eInfo(@WLD@ w, String uuid) {
  if (TEST != null) { Object r = t("info", uuid, null, null, null); if (r instanceof double[]) return (double[]) r; return null; }
  try {
    @REF@ r = w.getEntityStore().getRefFromUUID(java.util.UUID.fromString(uuid));
    if (r == null || !r.isValid()) return null;
    @ST@ st = r.getStore();
    if (st.getComponent(r, @DTH@.getComponentType()) != null) return null;
    @TCO@ tc = (@TCO@) st.getComponent(r, @TCO@.getComponentType());
    if (tc == null) return null;
    return new double[] { tc.getPosition().x, tc.getPosition().y, tc.getPosition().z };
  } catch (Throwable x) { return null; }
}""")
# a mob removed (no death = no drops; RemoveReason.REMOVE, the SkyyIslands camp's call)
M(fight, r"""
public static boolean eRemove(@WLD@ w, String uuid) {
  if (TEST != null) return Boolean.TRUE.equals(t("remove", uuid, null, null, null));
  try {
    @REF@ r = w.getEntityStore().getRefFromUUID(java.util.UUID.fromString(uuid));
    if (r == null || !r.isValid()) return false;
    w.getEntityStore().getStore().removeEntity(r, @RRS@.REMOVE);
    return true;
  } catch (Throwable x) { @PKG@.ShCfg.warnOnce("despawn", "a combat island mob could not be removed (logged once): " + x); return false; }
}""")
# living NPCs within rad of a point: Object[] { uuid, role, double[] pos } (the entity spatial index, the SkyyIslands camp's lookup)
M(fight, r"""
public static java.util.ArrayList eNear(@WLD@ w, double x, double y, double z, double rad) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (TEST != null) { Object r = t("near", Double.valueOf(x), Double.valueOf(y), Double.valueOf(z), Double.valueOf(rad)); if (r instanceof java.util.List) out.addAll((java.util.List) r); return out; }
  try {
    @ST@ st = w.getEntityStore().getStore();
    @SPR@ sr = (@SPR@) st.getResource(@EMOD@.get().getEntitySpatialResourceType());
    if (sr == null || sr.getSpatialStructure() == null) return out;
    java.util.ArrayList refs = new java.util.ArrayList();
    sr.getSpatialStructure().collect((@V3DC@) new @V3D@(x, y, z), rad, refs);
    for (int i = 0; i < refs.size(); i++) {
      Object o = refs.get(i);
      if (!(o instanceof @REF@)) continue;
      @REF@ r = (@REF@) o;
      if (!r.isValid()) continue;
      @NPCE@ n = (@NPCE@) st.getComponent(r, @NPCE@.getComponentType());
      if (n == null || st.getComponent(r, @DTH@.getComponentType()) != null) continue;
      @UUC@ uc = (@UUC@) st.getComponent(r, @UUC@.getComponentType());
      @TCO@ tc = (@TCO@) st.getComponent(r, @TCO@.getComponentType());
      if (uc == null || uc.getUuid() == null || tc == null) continue;
      out.add(new Object[] { uc.getUuid().toString(), n.getRoleName(), new double[] { tc.getPosition().x, tc.getPosition().y, tc.getPosition().z } });
    }
  } catch (Throwable x) { @PKG@.ShCfg.warnOnce("near", "the combat island mob scan failed (logged once): " + x); }
  return out;
}""")
# SkyyMobs mob:fn:setLevel {world, UUID, level} (that world's thread; no SkyyMobs = the vanilla level)
M(fight, r"""
public static boolean eLevel(@WLD@ w, String uuid, int lv) {
  if (TEST != null) return Boolean.TRUE.equals(t("level", uuid, Integer.valueOf(lv), null, null));
  try {
    java.util.function.Function f = @PKG@.ShCfg.fn("mob:fn:setLevel");
    if (f == null) return false;
    return Boolean.TRUE.equals(f.apply(new Object[] { w.getName(), java.util.UUID.fromString(uuid), Integer.valueOf(lv) }));
  } catch (Throwable x) { return false; }
}""")
M(fight, r"""
public static java.time.Instant midnight(java.time.Instant gt) {
  java.time.ZoneOffset z = @WTR@.ZONE_OFFSET;
  return gt.atOffset(z).toLocalDate().plusDays(1L).atStartOfDay().toInstant(z);
}""")
# ALWAYS NIGHT for one player: the world's time settings, clock paused, + the next midnight (only this player's screen)
M(fight, r"""
public static boolean eNight(@WLD@ w, Object pro, java.util.UUID u) {
  if (TEST != null) return Boolean.TRUE.equals(t("night", u, null, null, null));
  try {
    if (!(pro instanceof @PR@)) return false;
    @PR@ pr = (@PR@) pro;
    @ST@ st = w.getEntityStore().getStore();
    @WTR@ tr = (@WTR@) st.getResource(@WTR@.getResourceType());
    if (tr == null || tr.getGameTime() == null) return false;
    @UTS@ s = @WTR@.updateTimeSettingsPacket(new @UTS@(), w);
    s.timePaused = true;
    @UTI@ ut = new @UTI@(@WTR@.instantToInstantData(midnight(tr.getGameTime())));
    @PH@ h = pr.getPacketHandler();
    if (h == null) return false;
    OWN.set(Boolean.TRUE);   // fix (critic): our own packets pass ShNightF (it runs on this thread inside write)
    try {
      h.write((@TCP@) s);
      h.write((@TCP@) ut);
    } finally { OWN.remove(); }
    return true;
  } catch (Throwable x) { @PKG@.ShCfg.warnOnce("night", "the combat shard's night could not be sent (logged once): " + x); return false; }
}""")
M(fight, r"""
public static boolean eRestore(@WLD@ w, Object pro, java.util.UUID u) {
  if (TEST != null) return Boolean.TRUE.equals(t("restore", u, null, null, null));
  try {
    if (!(pro instanceof @PR@)) return false;
    @WTR@ tr = (@WTR@) w.getEntityStore().getStore().getResource(@WTR@.getResourceType());
    if (tr == null) return false;
    tr.sendTimePackets((@PR@) pro);
    return true;
  } catch (Throwable x) { @PKG@.ShCfg.warnOnce("restore", "the real time could not be sent back after the combat shard (logged once): " + x); return false; }
}""")
# fix (critic r5combat2): ShNightF's decision - drop the world's own time packet to this player? (held at night in that very world, our
# packet sent < HOLD_MS ago; never our own packet; any thread)
M(fight, r"""
public static boolean holds(java.util.UUID u, java.util.UUID wu, long now) {
  if (u == null || wu == null || OWN.get() != null) return false;
  Object o = NIGHT.get(u);
  if (!(o instanceof Object[])) return false;
  Object[] r = (Object[]) o;
  if (r.length < 3 || !wu.equals(r[2])) return false;
  long d = now - ((Long) r[1]).longValue();
  return d >= 0L && d < HOLD_MS;
}""")
# the night for every player of this world (pl: Object[] { UUID, double[] pos, Boolean member, PlayerRef }); returns the night packets sent
M(fight, r"""
public static int night(@WLD@ w, String wn, java.util.ArrayList pl, long now) {
  boolean on = @PKG@.ShCfg.CB_NIGHT && @PKG@.ShCfg.ON;
  java.util.UUID wid = TEST_WID;
  if (w != null) { try { wid = w.getWorldConfig().getUuid(); } catch (Throwable x) { wid = null; } }
  java.util.HashSet here = new java.util.HashSet();
  int n = 0;
  for (int i = 0; i < pl.size(); i++) {
    Object[] e = (Object[]) pl.get(i);
    java.util.UUID u = (java.util.UUID) e[0];
    double[] q = (double[]) e[1];
    here.add(u);
    boolean in = on && @PKG@.ShKind.ofX(q[0]) == @PKG@.ShCombat.CK;
    Object[] r = (Object[]) NIGHT.get(u);
    if (in) {
      if (r == null || !wn.equals(r[0]) || now - ((Long) r[1]).longValue() >= NIGHT_MS || now < ((Long) r[1]).longValue()) {
        if (eNight(w, e[3], u)) { NIGHT.put(u, new Object[] { wn, Long.valueOf(now), wid }); NIGHTS.incrementAndGet(); n++; }
      }
    } else if (r != null) {
      NIGHT.remove(u);   // fix (critic): the hold ends BEFORE the real time is sent (ShNightF lets it through)
      if (wn.equals(r[0]) && eRestore(w, e[3], u)) RESTORES.incrementAndGet();
    }
  }
  java.util.Iterator it = NIGHT.entrySet().iterator();   // gone from this world: the next world sends its own time on join
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    Object[] r = (Object[]) en.getValue();
    if (wn.equals(r[0]) && !here.contains(en.getKey())) it.remove();
  }
  return n;
}""")
M(fight, r"""
public static java.util.ArrayList list(java.util.concurrent.ConcurrentHashMap m, String key) {
  Object o = m.get(key);
  if (o instanceof java.util.ArrayList) return (java.util.ArrayList) o;
  java.util.ArrayList l = new java.util.ArrayList();
  m.put(key, l);
  return l;
}""")
# NO AFK FARM: this member moved 1.5 blocks within combat.afkSec (0 = always active)
M(fight, r"""
public static boolean active(java.util.UUID u, double[] q, long now) {
  Object o = MOVED.get(u);
  if (!(o instanceof double[])) { if (MOVED.size() > 4096) MOVED.clear(); MOVED.put(u, new double[] { q[0], q[1], q[2], (double) now }); return true; }
  double[] m = (double[]) o;
  double dx = q[0] - m[0];
  double dy = q[1] - m[1];
  double dz = q[2] - m[2];
  if (dx * dx + dy * dy + dz * dz > 2.25) { m[0] = q[0]; m[1] = q[1]; m[2] = q[2]; m[3] = (double) now; }
  int afk = @PKG@.ShCfg.CB_AFK;
  return afk <= 0 || (double) now - m[3] < 1000.0 * (double) afk;
}""")
# combat.maxPerHour per profile (a token bucket; BURST tokens to fill an island at once); fix (critic r5combat2 2nd round): it refills at
# maxPerHour x the asking island's lidX (its mobs at once / respawn vs Small level 0), so Mobs at once + Spawn speed really spawn faster
M(fight, r"""
public static boolean token(String k, long now, double mul) {
  int mh = @PKG@.ShCfg.CB_MAXH;
  if (mh <= 0) return true;
  Object o = BUCKET.get(k);
  double[] b;
  if (o instanceof double[]) b = (double[]) o;
  else { b = new double[] { BURST, (double) now }; BUCKET.put(k, b); }
  double dt = (double) now - b[1];
  if (dt > 0.0) b[0] = b[0] + dt * (double) mh * (mul > 1.0 ? mul : 1.0) / 3600000.0;
  if (b[0] > BURST) b[0] = BURST;
  b[1] = (double) now;
  if (b[0] < 1.0) return false;
  b[0] = b[0] - 1.0;
  return true;
}""")
M(fight, r"""
public static void untoken(String k) {
  Object o = BUCKET.get(k);
  if (o instanceof double[]) { double[] b = (double[]) o; b[0] = b[0] + 1.0; if (b[0] > BURST) b[0] = BURST; }
}""")
# the island box of a part (3 blocks past the rim; upper = above Y - 2, the cavern = Y - 18 .. Y - 2) and the leash (8 past the rim)
M(fight, r"""
public static boolean inBox(double[] q, int cx, int cz, int h, int part) {
  double dx = q[0] - (double) cx - 0.5;
  double dz = q[2] - (double) cz - 0.5;
  double m = (double) h + 3.0;
  if (dx < -m || dx > m || dz < -m || dz > m) return false;
  double y = q[1];
  int Y0 = @PKG@.ShGeo.Y;
  if (part == 0) return y >= (double) (Y0 - 2) && y <= (double) (Y0 + 24);
  return y < (double) (Y0 - 2) && y >= (double) (Y0 - 18);
}""")
M(fight, r"""
public static boolean leashOk(double[] q, int cx, int cz, int h) {
  double dx = q[0] - (double) cx - 0.5;
  double dz = q[2] - (double) cz - 0.5;
  double m = (double) h + 8.0;
  if (dx < -m || dx > m || dz < -m || dz > m) return false;
  int Y0 = @PKG@.ShGeo.Y;
  return q[1] >= (double) (Y0 - 22) && q[1] <= (double) (Y0 + 30);
}""")
M(fight, r"""
public static boolean far(java.util.ArrayList all, double x, double y, double z, double md) {
  double m2 = md * md;
  for (int i = 0; i < all.size(); i++) {
    double[] q = (double[]) all.get(i);
    double dx = q[0] - x;
    double dy = q[1] - y;
    double dz = q[2] - z;
    if (dx * dx + dy * dy + dz * dz < m2) return false;
  }
  return true;
}""")
# fix (critic r5combat2): only THIS profile's lists (pre = "pkey|"): every list is changed only by its own world's thread
M(fight, r"""
public static boolean tracked(String pre, String id) {
  java.util.Iterator it = MOBS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    Object o = en.getValue();
    if (((String) en.getKey()).startsWith(pre) && o instanceof java.util.ArrayList && ((java.util.ArrayList) o).contains(id)) return true;
  }
  return false;
}""")
# a part's mobs all removed (nobody there, the island gone, spawning off)
M(fight, r"""
public static int clear(@WLD@ w, String key) {
  int n = 0;
  Object o = MOBS.get(key);
  if (o instanceof java.util.ArrayList) {
    java.util.ArrayList l = (java.util.ArrayList) o;
    for (int i = 0; i < l.size(); i++) if (eRemove(w, (String) l.get(i))) n++;
    l.clear();
  }
  DUE.remove(key);
  EMPTY.remove(key);
  if (n > 0) GONE.addAndGet((long) n);
  return n;
}""")
# mobs a restart / an unload left in the chunks: a role of this island's pool, untracked, inside the part's box -> counted (every 10 s)
M(fight, r"""
public static int adopt(@WLD@ w, String key, int z, int size, int part, int cx, int cz, int h, long now, java.util.ArrayList mobs) {
  Object l = SCAN.get(key);
  if (l instanceof Long && now - ((Long) l).longValue() >= 0L && now - ((Long) l).longValue() < 10000L) return 0;
  SCAN.put(key, Long.valueOf(now));
  String[] rl = @PKG@.ShCombat.allRoles(z, size);
  String pre = key.substring(0, key.indexOf('|') + 1);
  double y = part == 0 ? (double) (@PKG@.ShGeo.Y + 2) : (double) (@PKG@.ShGeo.Y - 9);
  java.util.ArrayList near = eNear(w, (double) cx + 0.5, y, (double) cz + 0.5, (double) h + 6.0);
  int n = 0;
  for (int i = 0; i < near.size(); i++) {
    Object[] e = (Object[]) near.get(i);
    String id = (String) e[0];
    if (!@PKG@.ShCombat.has(rl, (String) e[1]) || tracked(pre, id) || !inBox((double[]) e[2], cx, cz, h, part)) continue;
    mobs.add(id);
    n++;
  }
  if (n > 0) ADOPTED.addAndGet((long) n);
  return n;
}""")
# ONE mob for a part: a known role of its pool, a spot on our floor (solid below, 2 free above) far from every player, its level
M(fight, r"""
public static String spawnOne(@WLD@ w, int z, int size, int lvl, int part, int slot, int cx, int cz, java.util.ArrayList all, java.util.Random rnd) {
  String[] rl = @PKG@.ShCombat.roles(z, size, part);
  java.util.ArrayList ok = new java.util.ArrayList();
  for (int i = 0; i < rl.length; i++) if (eRole(rl[i])) ok.add(rl[i]);
  if (ok.isEmpty()) return null;
  int[] sp = @PKG@.ShGeo.cspots(slot, size, part);
  if (sp.length < 2) return null;
  int by = part == 0 ? @PKG@.ShGeo.Y + 1 : @PKG@.ShGeo.CAVE_FY + 1;
  double md = (double) @PKG@.ShCfg.CB_DIST;
  for (int tries = 0; tries < 12; tries++) {
    int j = rnd.nextInt(sp.length / 2);
    int bx = cx + sp[2 * j];
    int bz = cz + sp[2 * j + 1];
    double x = (double) bx + 0.5;
    double zz = (double) bz + 0.5;
    if (!far(all, x, (double) by, zz, md)) continue;
    String fl = @PKG@.ShFill.idAt(w, bx, by - 1, bz);
    String a1 = @PKG@.ShFill.idAt(w, bx, by, bz);
    String a2 = @PKG@.ShFill.idAt(w, bx, by + 1, bz);
    if (fl == null || a1 == null || a2 == null || fl.length() == 0 || a1.length() > 0 || a2.length() > 0) continue;
    String role = @PKG@.ShCombat.wpick(z, ok, rnd.nextDouble());   // fix (critic): by the vanilla spawn odds
    String id = eSpawn(w, role, x, (double) by, zz);
    if (id == null) return null;
    int lo = @PKG@.ShCombat.lvLo(z, size, lvl);
    int hi = @PKG@.ShCombat.lvHi(z, size, lvl);
    eLevel(w, id, lo + (hi > lo ? rnd.nextInt(hi - lo + 1) : 0));
    SPAWNS.incrementAndGet();
    return id;
  }
  NOSPOT.incrementAndGet();
  return null;
}""")
# one island (both parts). lv = { Mobs at once, Mob level, Spawn speed }; mem = members of this world in the Combat region (Object[] { UUID,
# double[] pos, ... }), act = moved lately; all = every player's position. Returns the mobs spawned now.
M(fight, r"""
public static int island(@WLD@ w, String k, int slot, int t, int size, int[] lv, java.util.ArrayList mem, boolean[] act, java.util.ArrayList all, long now, java.util.Random rnd) {
  int kd = @PKG@.ShCombat.CK;
  int z = @PKG@.ShCombat.zoneOf(t);
  int si = size < 1 ? 1 : (size > 3 ? 3 : size);
  int h = @PKG@.ShGeo.HALF[si - 1];
  int cx = @PKG@.ShGeo.ox(kd) + @PKG@.ShGeo.SX[slot];
  int cz = @PKG@.ShGeo.OZ + @PKG@.ShGeo.SZ[slot];
  int capAll = @PKG@.ShCombat.cap(si, lv[0]);
  int low = @PKG@.ShCombat.lowerCap(si, lv[0]);
  long rsp = 1000L * (long) @PKG@.ShCombat.respawnSec(si, lv[2]);
  int spawned = 0;
  for (int part = 0; part < 2; part++) {
    String key = k + "|" + slot + "|" + part;
    int capP = part == 0 ? capAll - low : low;
    java.util.ArrayList mobs = list(MOBS, key);
    java.util.ArrayList due = list(DUE, key);
    for (int i = mobs.size() - 1; i >= 0; i--) {
      String id = (String) mobs.get(i);
      double[] q = eInfo(w, id);
      if (q == null) { mobs.remove(i); due.add(Long.valueOf(now + rsp)); continue; }
      if (!leashOk(q, cx, cz, h)) { if (eRemove(w, id)) DESPAWNS.incrementAndGet(); mobs.remove(i); due.add(Long.valueOf(now + rsp)); }
    }
    boolean here = false;
    boolean live = false;
    for (int m = 0; m < mem.size(); m++) {
      double[] q = (double[]) ((Object[]) mem.get(m))[1];
      if (inBox(q, cx, cz, h, part)) { here = true; if (act[m]) live = true; }
    }
    if (capP <= 0) { clear(w, key); continue; }
    if (!here) {
      Object e0 = EMPTY.get(key);
      if (!(e0 instanceof Long)) EMPTY.put(key, Long.valueOf(now));
      else if (now - ((Long) e0).longValue() >= GRACE) clear(w, key);
      continue;
    }
    EMPTY.remove(key);
    adopt(w, key, z, si, part, cx, cz, h, now, mobs);
    while (mobs.size() > capP) { String id = (String) mobs.remove(mobs.size() - 1); if (eRemove(w, id)) DESPAWNS.incrementAndGet(); }
    while (mobs.size() + due.size() < capP) due.add(Long.valueOf(now));
    while (mobs.size() + due.size() > capP && due.size() > 0) due.remove(due.size() - 1);
    if (!live) { AFK.incrementAndGet(); continue; }
    int di = -1;
    long best = Long.MAX_VALUE;
    for (int i = 0; i < due.size(); i++) { long v = ((Long) due.get(i)).longValue(); if (v <= now && v < best) { best = v; di = i; } }
    if (di < 0) continue;
    if (!token(k, now, @PKG@.ShCombat.lidX(si, lv[0], lv[2]))) { LID.incrementAndGet(); continue; }
    String id = spawnOne(w, z, si, lv[1], part, slot, cx, cz, all, rnd);
    if (id == null) { untoken(k); continue; }
    mobs.add(id);
    due.remove(di);
    spawned++;
  }
  return spawned;
}""")
# a profile still has tracked combat mobs (ShTick: the world emptied - flush them before it unloads, never left in its chunks)
M(fight, r"""
public static boolean has(String k) {
  if (k == null) return false;
  String pre = k + "|";
  java.util.Iterator it = MOBS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    Object v = en.getValue();
    if (((String) en.getKey()).startsWith(pre) && v instanceof java.util.ArrayList && !((java.util.ArrayList) v).isEmpty()) return true;
  }
  return false;
}""")
M(fight, r"""
public static int flushAll(@WLD@ w, String k) {
  if (k == null) return 0;
  String pre = k + "|";
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.Iterator it = MOBS.keySet().iterator();
  while (it.hasNext()) { String key = (String) it.next(); if (key.startsWith(pre)) keys.add(key); }
  int n = 0;
  for (int i = 0; i < keys.size(); i++) n += clear(w, (String) keys.get(i));
  java.util.Iterator si = SCAN.keySet().iterator();   // fix (critic): the world emptied - its scan times and night holds go too
  while (si.hasNext()) { String key = (String) si.next(); if (key.startsWith(pre)) si.remove(); }
  String wn = w == null ? "test" : w.getName();
  java.util.Iterator ni = NIGHT.entrySet().iterator();
  while (ni.hasNext()) { java.util.Map.Entry en = (java.util.Map.Entry) ni.next(); Object[] r = (Object[]) en.getValue(); if (wn.equals(r[0])) ni.remove(); }
  return n;
}""")
# the world's combat islands this second (pl as night()); the shard file is read under ShStore.LOCK, the engine calls after
M(fight, r"""
public static int tickWorld(@WLD@ w, String k, java.util.Properties p, java.util.ArrayList pl, long now) {
  RUNS.incrementAndGet();
  int kd = @PKG@.ShCombat.CK;
  String wn0 = w == null ? "test" : w.getName();
  night(w, wn0, pl, now);
  for (int i = 0; i < pl.size(); i++) {   // fix (critic): who may hit a mob here ("hurt") = a player in the Combat region this second
    Object[] e = (Object[]) pl.get(i);
    if (@PKG@.ShKind.ofX(((double[]) e[1])[0]) == kd) @PKG@.ShCombat.mark((java.util.UUID) e[0], wn0, now);
  }
  int n = @PKG@.ShMath.SLOTS;
  int[] ty = new int[n];
  int[] sz = new int[n];
  int[] lv = new int[3 * n];
  boolean any = false;
  @PKG@.ShStore.LOCK.lock(); try {
    boolean usable = @PKG@.ShCfg.CB_SPAWN && @PKG@.ShCfg.ON && p != null && @PKG@.ShMath.owned(kd, p) && !@PKG@.ShMath.paused(kd, p);
    for (int s = 0; s < n; s++) {
      ty[s] = -1;
      if (!usable || !@PKG@.ShMath.hasIsland(kd, p, s)) continue;
      ty[s] = @PKG@.ShIsl.ty(kd, p, s);
      sz[s] = @PKG@.ShMath.size(kd, p, s);
      for (int j = 0; j < 3; j++) lv[3 * s + j] = @PKG@.ShIsl.sub(p, kd, s, j);
      any = true;
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  java.util.Iterator it = MOBS.keySet().iterator();   // an island that is gone (or spawning off): its mobs go
  java.util.ArrayList gone = new java.util.ArrayList();
  String pre = k + "|";
  while (it.hasNext()) {
    String key = (String) it.next();
    if (!key.startsWith(pre)) continue;
    int a = key.indexOf('|', pre.length());
    int s = -1;
    try { s = Integer.parseInt(key.substring(pre.length(), a)); } catch (Throwable x) { s = -1; }
    if (s < 0 || s >= n || ty[s] < 0) gone.add(key);
  }
  for (int i = 0; i < gone.size(); i++) clear(w, (String) gone.get(i));
  if (!any) return 0;
  java.util.ArrayList mem = new java.util.ArrayList();
  java.util.ArrayList all = new java.util.ArrayList();
  for (int i = 0; i < pl.size(); i++) {
    Object[] e = (Object[]) pl.get(i);
    double[] q = (double[]) e[1];
    all.add(q);
    if (Boolean.TRUE.equals(e[2]) && @PKG@.ShKind.ofX(q[0]) == kd) mem.add(e);
  }
  boolean[] act = new boolean[mem.size()];
  for (int i = 0; i < act.length; i++) { Object[] e = (Object[]) mem.get(i); act[i] = active((java.util.UUID) e[0], (double[]) e[1], now); }
  java.util.Random rnd = SEED != 0L ? new java.util.Random(SEED ^ now) : new java.util.Random();
  int sp = 0;
  for (int s = 0; s < n; s++) {
    if (ty[s] < 0) continue;
    sp += island(w, k, s, ty[s], sz[s], new int[] { lv[3 * s], lv[3 * s + 1], lv[3 * s + 2] }, mem, act, all, now, rnd);
  }
  return sp;
}""")
# the world thread (ShTick, every second, a shard world with players): every player's place, then tickWorld
M(fight, r"""
public void run() {
  try {
    String k = @PKG@.ShWorlds.ownerOf(this.w.getName());
    if (k == null) return;
    if (this.flush) { flushAll(this.w, k); return; }
    java.util.Properties p = @PKG@.ShStore.get(k);
    java.util.ArrayList pl = new java.util.ArrayList();
    java.util.Iterator it = this.w.getPlayerRefs().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @PR@)) continue;
      @PR@ pr = (@PR@) o;
      if (!pr.isValid()) continue;
      @REF@ r = pr.getReference();
      if (r == null || !r.isValid()) continue;
      @TCO@ tc = (@TCO@) r.getStore().getComponent(r, @TCO@.getComponentType());
      if (tc == null) continue;
      java.util.UUID u = pr.getUuid();
      pl.add(new Object[] { u, new double[] { tc.getPosition().x, tc.getPosition().y, tc.getPosition().z }, Boolean.valueOf(@PKG@.ShRole.mayBeIn(u, k)), pr });
    }
    tickWorld(this.w, k, p, pl, System.currentTimeMillis());
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("fight", "the combat islands' tick failed (logged once): " + t); }
}""")
# fix (critic r5combat2): ShNightF = the outbound PlayerPacketFilter (SkyyEssentials 0.1.9's proven registerOutbound path; true = drop): the
# world's own UpdateTime / UpdateTimeSettings never reach a player held at night (ShFight.holds); every other packet passes; never throws
nightf = mk("ShNightF", None, (T["PPF"],))
C(nightf, "public ShNightF() { }")
M(nightf, r"""
public boolean test(@PR@ pr, @PKT@ pkt) {
  try {
    if (pr == null || !(pkt instanceof @UTI@ || pkt instanceof @UTS@)) return false;
    return @PKG@.ShFight.holds(pr.getUuid(), pr.getWorldUuid(), System.currentTimeMillis());
  } catch (Throwable t) { return false; }
}""")

# ================= ShTick: 1 s scheduler tick - idle unload + queue, regrow, sweep, particles, pending placements =================''')
P.rep('''      if (pc <= 0) { PRESENT.remove(nm); continue; }''', '''      if (pc <= 0) {
        PRESENT.remove(nm);
        if (@PKG@.ShFight.has(@PKG@.ShWorlds.ownerOf(nm))) w.execute(new @PKG@.ShFight(w, true));   // 0.4.11: the last player left - the combat mobs go now
        continue;
      }''')
P.rep('''      w.execute(new @PKG@.ShSweep(w));   // fix (critic): every second, not every 5 s (a removed co-op member / a profile switch)''',
      '''      w.execute(new @PKG@.ShSweep(w));   // fix (critic): every second, not every 5 s (a removed co-op member / a profile switch)
      w.execute(new @PKG@.ShFight(w));   // 0.4.11: the combat islands (always night + the spawner)''')

# ---------------------------------------------------------------------------------------------------- 12. the Map tab: zone captions, the combat texts, the class gate
P.rep('''MCAP = [["T%d %s" % (_t["tier"], _t["name"]) for _t in LAD[_k]] for _k in range(NK)]   # the disc captions (tier tag first)''',
      '''MCAP = [[(_t["name"] if KINDS[_k] == "Combat" else "T%d %s" % (_t["tier"], _t["name"])) for _t in LAD[_k]] for _k in range(NK)]   # the disc captions (tier tag first; 0.4.11: "Zone 2")''')
P.rep('''"Combat": "Zone islands come later"}''', '''"Combat": "Always night - zone by zone"}''')
P.rep('''"public int mview;", "public int zoom;",''', '''"public int mview;", "public int cLv;", "public int zoom;",''')
P.rep('''  int lockLv = lockNeed > 0 ? @PKG@.ShIsl.level(this.me, kd) : -1;
  this.locked = lockNeed > 0 && lockLv >= 0 && lockLv < lockNeed;''', '''  int lockLv = lockNeed > 0 ? @PKG@.ShIsl.level(this.me, kd) : -1;
  this.locked = lockNeed > 0 && lockLv >= 0 && lockLv < lockNeed;
  this.cLv = kd == @PKG@.ShCombat.CK ? (lockNeed > 0 ? lockLv : @PKG@.ShIsl.level(this.me, kd)) : -1;   // 0.4.11: the class level (Zone N's gate)''')
P.rep('''      this.mTex[i] = ((purse < 0L || purse >= bc) && items) ? "Ready" : "Open";''',
      '''      boolean zok = kd != @PKG@.ShCombat.CK || this.cLv >= @PKG@.ShCombat.need(i);   // fix (critic): an unreadable class level never counts as enough   // 0.4.11: a zone above your class level is not "can buy"
      this.mTex[i] = ((purse < 0L || purse >= bc) && items && zok) ? "Ready" : "Open";''')
P.rep('''    this.mTx[@@V1Ot@@] = "Makes " + perHour(r) + " / hour - " + @PKG@.ShMath.totems(kd, p, sl) + " of " + @PKG@.ShMath.pads(sz) + " pads - +" + @PKG@.ShCfg.dec((mu - 1.0) * 100.0) + " % from upgrades";''',
      '''    this.mTx[@@V1Ot@@] = "Makes " + perHour(r) + " / hour - " + @PKG@.ShMath.totems(kd, p, sl) + " of " + @PKG@.ShMath.pads(sz) + " pads - +" + @PKG@.ShCfg.dec((mu - 1.0) * 100.0) + " % from upgrades";
    if (kd == @PKG@.ShCombat.CK) this.mTx[@@V1Ot@@] = @PKG@.ShCombat.nowTxt(@PKG@.ShCombat.zoneOf(ts), sz, a0, d0, i0) + " - cage " + perHour(r) + " / h";   // 0.4.11''')
P.rep('''      this.mTx[ra[w]] = "Next: +" + @PKG@.ShCfg.dec(pc) + " % output" + ex;''',
      '''      this.mTx[ra[w]] = "Next: +" + @PKG@.ShCfg.dec(pc) + " % output" + ex;
      if (kd == @PKG@.ShCombat.CK) this.mTx[ra[w]] = "Next: " + @PKG@.ShCombat.nextTxt(@PKG@.ShCombat.zoneOf(ts), sz, w, lv);   // 0.4.11 (spec 10)''')
P.rep('''    } else this.mTx[@@SdA@@] = au ? "Automated - nothing to replant" : ("mine".equals(st) ? "Ore regrows by itself" : "Nothing to replant here");''',
      '''    } else if (kd == @PKG@.ShCombat.CK) {   // 0.4.11; fix (critic): the next size's mobs by name
      int cz0 = @PKG@.ShCombat.zoneOf(ts);
      this.mTx[@@SdA@@] = sz < 3 ? "Grow adds: " + @PKG@.ShCombat.namesTxt(@PKG@.ShCombat.adds(cz0, sz + 1), 30) + (sz == 2 ? " + a cavern" : "") : @PKG@.ShCombat.poolTxt(cz0, sz) + " - always night";
      this.mCol[@@SdA@@] = "@WARN@";
    }
    else this.mTx[@@SdA@@] = au ? "Automated - nothing to replant" : ("mine".equals(st) ? "Ore regrows by itself" : "Nothing to replant here");''')
P.rep('''    this.mTx[@@V2A@@] = "Makes " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.PROD[ts]) + ". It starts Small with its own 3 upgrades and appears at its place in the shard world.";''',
      '''    this.mTx[@@V2A@@] = "Makes " + @PKG@.ShTotem.pretty(@PKG@.ShIsl.PROD[ts]) + ". It starts Small with its own 3 upgrades and appears at its place in the shard world.";
    if (kd == @PKG@.ShCombat.CK) this.mTx[@@V2A@@] = "A " + @PKG@.ShIsl.NAME[ts] + " arena, always night, Lv " + @PKG@.ShCombat.lvTxt(@PKG@.ShCombat.zoneOf(ts), 1, 0) + ": " + @PKG@.ShCombat.namesTxt(@PKG@.ShCombat.adds(@PKG@.ShCombat.zoneOf(ts), 1), 46) + ". Grows with its 3 upgrades.";   // 0.4.11; fix (critic): the mobs by name''')
P.rep('''      this.mTx[@@V2Sb@@] = "Next in line - you can buy it here"; this.mCol[@@V2Sb@@] = "@GOOD@";
      this.mTx[@@V2G@@] = this.mine ? "Buy island takes the items first, then the coins." : "Only the island owner buys islands.";
      this.mOn[@@BBuy@@] = this.mine;''', '''      this.mTx[@@V2Sb@@] = "Next in line - you can buy it here"; this.mCol[@@V2Sb@@] = "@GOOD@";
      this.mTx[@@V2G@@] = this.mine ? "Buy island takes the items first, then the coins." : "Only the island owner buys islands.";
      this.mOn[@@BBuy@@] = this.mine;
      int zn = kd == @PKG@.ShCombat.CK ? @PKG@.ShCombat.need(s) : 0;   // 0.4.11: Zone N needs class level combat.zoneLevel.N
      if (zn > 0 && this.cLv < zn) { this.mTx[@@V2G@@] = "Needs class level " + zn + (this.cLv >= 0 ? " (you: " + this.cLv + ")." : " (class level not readable now)."); this.mCol[@@V2G@@] = "@BAD@"; this.mOn[@@BBuy@@] = false; }''')

# ---------------------------------------------------------------------------------------------------- 13. engine types + the build-time member checks
P.rep('''    "FLU":  "com.hypixel.hytale.server.core.asset.type.fluid.Fluid",''', '''    "FLU":  "com.hypixel.hytale.server.core.asset.type.fluid.Fluid",
    # 0.4.11: the combat islands - NPC spawn / lookup / removal (the SkyyIslands camp's calls) + the per-player night packets
    "NPCP": "com.hypixel.hytale.server.npc.NPCPlugin",
    "NPCE": "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "PAIR": "it.unimi.dsi.fastutil.Pair",
    "R3F":  "com.hypixel.hytale.math.vector.Rotation3f",
    "R3C":  "com.hypixel.hytale.math.vector.Rotation3fc",
    "UUC":  "com.hypixel.hytale.server.core.entity.UUIDComponent",
    "DTH":  "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "SPR":  "com.hypixel.hytale.component.spatial.SpatialResource",
    "EMOD": "com.hypixel.hytale.server.core.modules.entity.EntityModule",
    "RRS":  "com.hypixel.hytale.component.RemoveReason",
    "WTR":  "com.hypixel.hytale.server.core.modules.time.WorldTimeResource",
    "UTS":  "com.hypixel.hytale.protocol.packets.world.UpdateTimeSettings",
    "UTI":  "com.hypixel.hytale.protocol.packets.world.UpdateTime",
    "PH":   "com.hypixel.hytale.server.core.io.PacketHandler",
    "TCP":  "com.hypixel.hytale.protocol.ToClientPacket",
    # fix (critic r5combat2): the night hold's outbound packet filter (SkyyEssentials 0.1.9's types)
    "PAD":  "com.hypixel.hytale.server.core.io.adapter.PacketAdapters",
    "PPF":  "com.hypixel.hytale.server.core.io.adapter.PlayerPacketFilter",
    "PFI":  "com.hypixel.hytale.server.core.io.adapter.PacketFilter",
    "PKT":  "com.hypixel.hytale.protocol.Packet",''')
P.rep('''             (SUI.MAP_KEEP_TYPES["ANC"], "setWidth"), (SUI.MAP_KEEP_TYPES["ANC"], "setHeight"), (SUI.MAP_KEEP_TYPES["VAL"], "of")):''',
      '''             (SUI.MAP_KEEP_TYPES["ANC"], "setWidth"), (SUI.MAP_KEEP_TYPES["ANC"], "setHeight"), (SUI.MAP_KEEP_TYPES["VAL"], "of"),
             # 0.4.11: the combat islands
             (T["NPCP"], "get"), (T["NPCP"], "spawnNPC"), (T["NPCP"], "hasRoleName"), (T["NPCE"], "getComponentType"), (T["NPCE"], "getRoleName"),
             (T["PAIR"], "first"), (T["R3F"], "setYaw"), (T["UUC"], "getComponentType"), (T["UUC"], "getUuid"), (T["DTH"], "getComponentType"),
             (T["SPR"], "getSpatialStructure"), ("com.hypixel.hytale.component.spatial.SpatialStructure", "collect"), (T["EMOD"], "get"),
             (T["EMOD"], "getEntitySpatialResourceType"), (T["ST"], "removeEntity"), (T["RRS"], "REMOVE"), (T["EST"], "getRefFromUUID"),
             (T["WTR"], "updateTimeSettingsPacket"), (T["WTR"], "instantToInstantData"), (T["WTR"], "sendTimePackets"), (T["WTR"], "ZONE_OFFSET"),
             (T["UTS"], "timePaused"), (T["PR"], "getPacketHandler"), (T["PH"], "write"), (T["WLD"], "getPlayerRefs"),
             (T["PAD"], "registerOutbound"), (T["PAD"], "deregisterOutbound"), (T["PPF"], "test"), (T["WLD"], "getWorldConfig"),
             ("com.hypixel.hytale.server.core.universe.world.WorldConfig", "getUuid")):''')
P.rep('''[admc, gfn, dfn, smap, pl]''', '''[admc, gfn, dfn, smap, pl, cmb, fight, nightf]''')
# fix (critic r5combat2): the night hold's packet filter registered at start (a failure = a WARN; the night is still resent every second
# but the vanilla broadcast may flicker it) and removed at shutdown
P.rep('''  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.ShTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);''',
      '''  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.ShTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  try { @PKG@.ShFight.FILTER = @PAD@.registerOutbound((@PPF@) new @PKG@.ShNightF()); }   // 0.4.11 fix: the combat shard's night hold
  catch (Throwable t) { @PKG@.ShFight.FILTER = null; @PKG@.ShCfg.warn("combat shard night: the time packet filter could not be registered (the sky may flicker to day): " + t); }''')
P.rep('''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }''',
      '''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PFI@ nf = @PKG@.ShFight.FILTER; @PKG@.ShFight.FILTER = null; if (nf != null) @PAD@.deregisterOutbound(nf); } catch (Throwable t) { }   // 0.4.11 fix''')
P.rep('''getLogger().at(java.util.logging.Level.INFO).log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.10: the shard menu opens again''',
      '''getLogger().at(java.util.logging.Level.INFO).log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.11: THE COMBAT SHARD (one island per zone, " + @PKG@.ShCombat.ZN + " zones, always night, mobs while you are there - " + @PKG@.ShCombat.DROP_ROLE.length + " pool mobs, at most " + @PKG@.ShCfg.CB_MAXH + " an hour); 0.4.10: the shard menu opens again''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
_k = P.s.index
assert _k('cmb = mk("ShCombat")') < _k('geo = mk("ShGeo")') < _k('fight = mk("ShFight"') < _k('tick = mk("ShTick"'), "0.4.11: classes before their callers"
P.finish()
