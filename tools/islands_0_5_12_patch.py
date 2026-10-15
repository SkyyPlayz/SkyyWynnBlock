"""Derive SkyyIslands/build_skyyislands_0.5.12.py from the LIVE 0.5.11 (build_skyyislands_0.5.11.py = the tools/deploy_set.py SET pin, made by
tools/islands_0_5_11_patch.py - never edit a generated script, edit this patch). Every anchor is asserted; at the end every change is undone
on a copy and compared with 0.5.11 (nothing else changed). Line endings kept.
    python tools/islands_0_5_12_patch.py   then   python SkyyIslands/build_skyyislands_0.5.12.py   then
    python SkyyIslands/test_skyyislands_0.5.12.py
(never --deploy: tools/deploy_set.py deploys the whole set). Pairs with SkyyMobs 0.1.9 (mob:fn:setLevel; works without it - see 2 / 6).

0.5.12 (2026-10-15) = STARTER ISLANDS PART 2 (round isle2; Skyy 2026-10-15 after a fresh-profile test: "island 2. no mobs to kill." / "no boss,
and no real portal." / "make sure you respawn on your island, not the default spawn." / popup "Island 2's camp has no mob spawner yet (it was
left out of the last build). What should spawn there? -> Skeletons (Recommended)"; research/SkyyQuests-Tutorial-Spec.md 3.3 + Q3 default).
Only islands with the 3-island design get 1-3 (classic islands are unchanged); island worlds spawn no NPCs on their own (Void world,
IsSpawningNPC false), so SkyyIslands spawns these itself with the engine call SkyyMerchants / SkyyQuests already use
(NPCPlugin.spawnNPC(store, role, null, pos, rot)), on the island world's own thread, and NOTHING outside an island world.
  1. ISLAND 2 CAMP: skeletons around the old camp (camp.roles, default Skeleton_Fighter, Skeleton_Fighter, Skeleton_Soldier - the vanilla
     Zone 1 skeletons; Lv camp.levelMin-camp.levelMax = 1-3 through SkyyMobs 0.1.9 mob:fn:setLevel) - camp.count (3) of them while an
     island member (owner / co-op / trusted - rank trusted or higher) stands on island 2 (within 18 blocks of its centre, 46,14); after
     one dies a new one comes camp.respawnSeconds (60 s) later; never more than camp.max (5) alive (alive = the ones this session spawned
     that still live + any camp skeleton found within 28 blocks of the camp - so leftovers saved in the chunk count after a restart); no
     member on island 2 = no spawns. Spawn spots: 6 fixed cells inside the camp's ring wall (build-time, from the layout), each used only
     while its cell + the 2 above are free and the block under it is solid. They are ordinary vanilla mobs: normal drops and kill XP, and
     SkyyQuests' "Defeat 5 mobs" (kill any) counts them with its own kill hook.
  2. ISLAND 3 MINI BOSS "Shardkeeper": boss.role (Golem_Crystal_Earth, the TownProbe-proven role SkyyQuests' "Defeat the mini boss"
     counts) at the arena (71.5,130,34.5), Lv boss.level (10) and the name boss.name ("[Lv 10] Shardkeeper") through mob:fn:setLevel
     (without SkyyMobs 0.1.9: no level, and the Nameplate / display name "Shardkeeper" are put on it here). It wakes when an island member
     comes within 18 blocks of the arena and none is alive (tracked, or a boss role found within 40 blocks); after it dies the next one
     waits boss.cooldownSeconds (300 s; 30 s when no player killed it, e.g. it fell off). On wake: "[Island] The Shardkeeper has woken
     on island 3!" to the members there.
     THE HUB SHARD (new item Skyy_Hub_Shard - no Hub Shard existed in SkyyQuests / SkyyIslands; icon = research/cloud/icons-1013 art,
     model = the vanilla crystal fragment with the void texture, both by reference): when a Shardkeeper dies to a player, the killer and
     every island member within 32 blocks of the arena get ONE Hub Shard - only the first time on their current PROFILE (the profile
     key goes to Skyy_SkyyIslands/hubshards.properties, a new file); later kills give normal loot only. Given storage first (counted);
     bags full = "make room" and it is given as soon as there is room (retried every second while they are on an island).
  3. THE WORKING PORTAL: the empty socket of the broken frame (81,134,42, a vanilla smooth brick in 0.5.10 / 0.5.11 islands) becomes
     Skyy_Island_Portal_Socket (looks the same, faint violet glow, "Press [F] to repair", unbreakable) the first time a player is on the
     island (only while that cell still holds the smooth brick or is empty). F on it with a Hub Shard anywhere in the bags (island members
     - co-op or higher - or a server admin) takes ONE shard (counted) and repairs the portal: the socket becomes Skyy_Island_Hub_Portal
     (the vanilla hub portal pad look: model, light, particles, ambient sound by reference; "Press [F] to activate"; unbreakable), the
     frame's broken top is filled in (only empty cells), the island file gets portal=1 / portal.at / portal.by (new keys - per island,
     kept by restarts), everyone on the island is told, and SkyyQuests gets island:portal for that player (quest:fn:event; this mod now
     puts quest:caller:islands on the bridge, so tutorial task 21 "Travel to the hub" goes live). Before repair F says "Repair this portal
     with a Hub Shard (the Shardkeeper on this island drops one)". After repair stepping onto the pad or F on it sends the player to the
     hub (HubCmd.sendToHub, the /hub path, the portal sound) and sends island:portal again; at most once per 4 s per player.
  4. RESPAWN ON YOUR ISLAND (Server Setup -> Islands -> Hub -> "Respawn on your island", islands.respawnHome, default on): when a player
     respawns after a death (DeathComponent removed; 0.8 s later on that world's thread) - died on their own island (co-op members: the
     co-op island = IslandStore.homeKey) = nothing to do (the engine already uses their bed there, else the island spawn); died anywhere
     else with a bed set in THAT world = nothing (vanilla bed respawn elsewhere is left alone); else -> their island: their bed on the
     island when they have one and the island world is loaded, else the island spawn (world loaded) or /island's own load + teleport;
     no island yet (or the island file has no world) -> the hub, unless they died in the hub world.
  5. SERVER SETUP: new category "Starter islands" (camp on / count / max / respawn s / roles / Lv min / Lv max, boss on / cooldown s / Lv /
     role / name) + "Respawn on your island" under Hub. config.properties keys camp.*, boss.*, islands.respawnHome: a fresh file lists
     them, an existing file has no line = the default (no migration, nothing rewritten).
  6. Engine seam IsleApi (IsleLife.API; null = the real engine IsleEng) so the harness EXECUTES the camp / boss / portal / loot / respawn
     logic on stand-in worlds. ECS: IsleUse (UseBlockEvent$Pre on the two new blocks; IslandPerms.useFlag leaves Skyy_Island_* blocks
     to it - visitors may use a repaired portal, only members repair), IsleDeath (DeathSystems$OnDeathSystem: camp / boss deaths, the
     killer), IsleRespawn (RespawnSystems$OnRespawnSystem, Player query) - one registerSystem each; IsleTick (1 s scheduler) queues one
     IsleTask per island world with players on its world thread. A 3-island island is recognised by 12 deep stone cells of islands 2 + 3
     (at least 6 = yes) and then remembered in its island file (isles=3, new key) so later digging does not matter.
  7. FIX ROUND (critics isle2, 2026-10-15): (a) /island reset clears portal / portal.at / portal.by / isles with kit (a reset island
     has a broken portal again and is probed again); (b) a lost Hub Shard no longer locks a profile out: after the first one, a
     Shardkeeper kill gives a co-op member (rank co-op or higher) of THIS island one more shard while its portal is still broken and they
     hold none; (c) the pad standing in the socket = repaired (a lost portal=1 write is written again, never a dead pad); (d) no Hub Shard
     move while profile:busy:<uuid> is on the bridge (PROFILES-CONTRACT 4.5: owed, retried); (e) an unreadable hubshards.properties is
     kept as hubshards.properties.bad; (f) a pet's / summon's killing blow counts for its owner (pets:fn:ownerOf, as SkyyMobs 0.1.8);
     (g) each camp death has its own respawn time (kill A, then B 30 s later: A's comes back at 60 s, B's at 90 s); (h) respawn on your
     island leaves worlds with their own respawn alone: islands.respawnKeep (default skyy-shard-,skywynn_z = SkyyShards worlds and the
     SkyyWorldGen zone islands; name prefixes, comma separated; the hub IS routed home - Skyy woke at the default spawn); (i)
     quest:caller:islands is on the bridge only while new islands get 3 islands AND the mini boss is on (with island:places, re-checked
     when either setting changes), and /hub from a home island known to be classic sends island:portal (no portal there to repair);
     (j) the socket goes on an empty cell only with ground under it.
LEFT OUT: the Unclaimed Luggage chest on island 2 (SkyyExploration); a portal on classic islands (they have no frame - /hub as before).
No saved-data loss (new keys / one new file only), no command, no permission change. ROLLBACK to 0.5.11: NOT clean once used - Hub
Shards (bags, Vaults, chests) become unknown items and the socket / pad unknown blocks on 0.5.11; hubshards.properties survives, so a
roll forward does not re-give a first shard (the again-rule in 7b covers a co-op member whose portal is still broken). The main session
should add a FLOOR for SkyyIslands 0.5.12 in tools/deploy_set.py once a Hub Shard has been given.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.5.11.py")
dst = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.5.12.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.5.11"' in s and "GENERATED by tools/islands_0_5_11_patch.py" in s and "IsleLife" not in s, "not the generated 0.5.11 script"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.5.12 (2026-10-15)"):].rstrip() + "\n\n"

# ================================================================================================ docstring + version
rep('''"""SkyyIslands 0.5.11 - build script (javassist via jpype). GENERATED by tools/islands_0_5_11_patch.py from the LIVE 0.5.10 (itself
generated by tools/islands_0_5_10_patch.py from 0.5.9) - edit the patch, then regenerate; never edit this file by hand. Never run with
--deploy (tools/deploy_set.py deploys the coordinated set). Test: python SkyyIslands/test_skyyislands_0.5.11.py --no-server
''', '''"""SkyyIslands 0.5.12 - build script (javassist via jpype). GENERATED by tools/islands_0_5_12_patch.py from the LIVE 0.5.11 (itself
generated by tools/islands_0_5_11_patch.py from 0.5.10) - edit the patch, then regenerate; never edit this file by hand. Never run with
--deploy (tools/deploy_set.py deploys the coordinated set). Test: python SkyyIslands/test_skyyislands_0.5.12.py

''' + NOTE + '''0.5.11 (the base, still true unless 0.5.12 above says otherwise):
''')
rep('VERSION = "0.5.11"', 'VERSION = "0.5.12"')

# ================================================================================================ build-time part-2 data (layout)
rep('''if os.environ.get("S3_ONLY") == "1":          # 0.5.10: the harness reads the layout only (no JVM, no build)
''', '''

# 0.5.12 STARTER ISLANDS PART 2: the fixed cells the camp / boss / portal code uses, read from the layout here (the harness reads them too)
def s3_part2(L, places, tops, isle):
    fx, fz0 = 81, 40
    fy = tops[(fx, fz0 + 2)] + 1
    socket = (fx, fy, fz0 + 2)
    assert L.get(socket) == "Rock_Stone_Brick_Smooth", ("the frame's empty socket", L.get(socket))
    fix = [(fx, fy + 4, fz0 + 4, "Rock_Stone_Brick_Mossy"), (fx, fy + 5, fz0 + 4, "Rock_Stone_Brick_Mossy"),
           (fx, fy + 5, fz0 + 3, "Rock_Stone_Brick_Decorative")]
    for x, y, z, _b in fix:
        assert (x, y, z) not in L, ("the frame's broken top is empty there", x, y, z)
    for z in (fz0 + 1, fz0 + 2, fz0 + 3):
        for y in range(fy + 1, fy + 5):
            assert (fx, y, z) not in L, ("the frame's opening is open", y, z)
    cam = places["camp"]
    cx, cz = int(cam[0] - 1.5), int(cam[2] - 0.5)       # the cold campfire (the camp place is next to it)
    assert L.get((cx, tops[(cx, cz)] + 1, cz)) == "Deco_Campfire_Off", "the camp fire"
    cand = []
    for x in range(cx - 4, cx + 5):
        for z in range(cz - 4, cz + 5):
            d = _s3m.hypot(x - cx, z - cz)
            if not (1.4 <= d <= 3.6) or isle.get((x, z)) != "island2":
                continue
            t = tops[(x, z)]
            if any((x, t + k, z) in L for k in (1, 2, 3)) or L.get((x, t, z)) not in (S3_GRASS, S3_DIRT, S3_STONE):
                continue
            cand.append((_s3m.atan2(z - cz, x - cx), x + 0.5, t + 1.0, z + 0.5))
    cand.sort()
    step = max(1, len(cand) // 6)
    spots = [c[1:] for c in cand[::step]][:6]
    assert len(spots) == 6, ("6 camp spawn spots", len(cand))
    deep = sorted(k for k, b in L.items() if b == S3_STONE and isle.get((k[0], k[2])) in ("island2", "island3") and k[1] <= tops[(k[0], k[2])] - 4)
    probe = deep[::len(deep) // 12][:12]
    assert len(probe) == 12 and all(L[p] == S3_STONE for p in probe)
    i2 = [v for v in S3_ISLES if v[0] == "island2"][0]
    return {"socket": socket, "fix": fix, "spots": spots, "probe": probe, "isle2": (i2[1] + 0.5, i2[2] + 0.5), "boss": places["boss"][:3],
            "camp": cam[:3], "pad": (fx, fy, fz0 + 2)}


S3_P2 = s3_part2(S3_L, S3_PLACES, S3_TOPS, S3_ISLE)
if os.environ.get("S3_ONLY") == "1":          # 0.5.10: the harness reads the layout only (no JVM, no build)
''')

# ================================================================================================ engine tokens
rep('''    "PKG":   PKG,
''', '''    # 0.5.12 starter islands part 2: NPC spawn (SkyyMerchants / SkyyQuests call shape), deaths, respawns, the spatial NPC lookup, bags
    "NPCP":  "com.hypixel.hytale.server.npc.NPCPlugin",
    "PAIR":  "it.unimi.dsi.fastutil.Pair",
    "V3D":   "org.joml.Vector3d",
    "V3DC":  "org.joml.Vector3dc",
    "R3C":   "com.hypixel.hytale.math.vector.Rotation3fc",
    "UUC":   "com.hypixel.hytale.server.core.entity.UUIDComponent",
    "ODS":   "com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$OnDeathSystem",
    "ORS":   "com.hypixel.hytale.server.core.modules.entity.damage.RespawnSystems$OnRespawnSystem",
    "DTH":   "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "CMP":   "com.hypixel.hytale.component.Component",
    "EMOD":  "com.hypixel.hytale.server.core.modules.entity.EntityModule",
    "SPR":   "com.hypixel.hytale.component.spatial.SpatialResource",
    "INV":   "com.hypixel.hytale.server.core.inventory.Inventory",
    "NPL":   "com.hypixel.hytale.server.core.entity.nameplate.Nameplate",
    "DNC":   "com.hypixel.hytale.server.core.modules.entity.component.DisplayNameComponent",
    "PWD":   "com.hypixel.hytale.server.core.entity.entities.player.data.PlayerWorldData",
    "PRP":   "com.hypixel.hytale.server.core.entity.entities.player.data.PlayerRespawnPointData",
    "PKG":   PKG,
''')

# ================================================================================================ config text + fields + load + rows
rep('''    "starter.design=three",
    "",
])''', '''    "starter.design=three",
    "# 0.5.12 island 2 camp (3-island islands): skeletons while a member is on island 2; a dead one comes back after camp.respawnSeconds",
    "camp.enabled=true",
    "camp.count=3",
    "camp.max=5",
    "camp.respawnSeconds=60",
    "camp.roles=Skeleton_Fighter,Skeleton_Fighter,Skeleton_Soldier",
    "camp.levelMin=1",
    "camp.levelMax=3",
    "# 0.5.12 island 3 mini boss: wakes when a member comes near; drops the Hub Shard once per player profile; the next one after the cooldown",
    "boss.enabled=true",
    "boss.cooldownSeconds=300",
    "boss.level=10",
    "boss.role=Golem_Crystal_Earth",
    "boss.name=Shardkeeper",
    "# 0.5.12 respawn: true = after a death a player wakes on their own island (a bed set where they died wins; no island = the hub)",
    "islands.respawnHome=true",
    "# 0.5.12 worlds that keep their own respawn (world name starts with one of these, comma separated): SkyyShards worlds, zone islands",
    "islands.respawnKeep=skyy-shard-,skywynn_z",
    "",
])''')
rep('''          "public static volatile String STARTER_DESIGN = \\"three\\";"):
    F(cfg, f)''', '''          "public static volatile String STARTER_DESIGN = \\"three\\";",
          # 0.5.12 starter islands part 2: the island 2 camp, the island 3 mini boss, respawn on your island
          "public static volatile boolean CAMP_ON = true;", "public static volatile int CAMP_COUNT = 3;", "public static volatile int CAMP_MAX = 5;",
          "public static volatile int CAMP_RESPAWN = 60;",
          "public static volatile String CAMP_ROLES = \\"Skeleton_Fighter,Skeleton_Fighter,Skeleton_Soldier\\";",
          "public static volatile int CAMP_LV_MIN = 1;", "public static volatile int CAMP_LV_MAX = 3;",
          "public static volatile boolean BOSS_ON = true;", "public static volatile int BOSS_COOLDOWN = 300;", "public static volatile int BOSS_LEVEL = 10;",
          "public static volatile String BOSS_ROLE = \\"Golem_Crystal_Earth\\";", "public static volatile String BOSS_NAME = \\"Shardkeeper\\";",
          "public static volatile boolean RESPAWN_HOME = true;",
          "public static volatile String RESPAWN_KEEP = \\"skyy-shard-,skywynn_z\\";"):
    F(cfg, f)''')
rep('''      STARTER_DESIGN = sd.equals("classic") ? "classic" : "three";
''', '''      STARTER_DESIGN = sd.equals("classic") ? "classic" : "three";
      CAMP_ON = !"false".equalsIgnoreCase(p.getProperty("camp.enabled", "true").trim());            // 0.5.12 part 2
      CAMP_COUNT = (int) lng(p, "camp.count", 3L, 0L, 20L);
      CAMP_MAX = (int) lng(p, "camp.max", 5L, 1L, 20L);
      CAMP_RESPAWN = (int) lng(p, "camp.respawnSeconds", 60L, 5L, 3600L);
      CAMP_ROLES = p.getProperty("camp.roles", "Skeleton_Fighter,Skeleton_Fighter,Skeleton_Soldier").trim();
      CAMP_LV_MIN = (int) lng(p, "camp.levelMin", 1L, 1L, 1000L);
      CAMP_LV_MAX = (int) lng(p, "camp.levelMax", 3L, 1L, 1000L);
      BOSS_ON = !"false".equalsIgnoreCase(p.getProperty("boss.enabled", "true").trim());
      BOSS_COOLDOWN = (int) lng(p, "boss.cooldownSeconds", 300L, 10L, 86400L);
      BOSS_LEVEL = (int) lng(p, "boss.level", 10L, 1L, 1000L);
      BOSS_ROLE = p.getProperty("boss.role", "Golem_Crystal_Earth").trim();
      BOSS_NAME = p.getProperty("boss.name", "Shardkeeper").trim();
      RESPAWN_HOME = !"false".equalsIgnoreCase(p.getProperty("islands.respawnHome", "true").trim());
      RESPAWN_KEEP = p.getProperty("islands.respawnKeep", "skyy-shard-,skywynn_z").trim();
''')
rep('''            ("starter", "Starter kit"), ("hub", "Hub"), ("tech", "Technical"), ("sounds", "Sounds")]          # 0.5.9: + Sounds''',
    '''            ("starter", "Starter kit"), ("hub", "Hub"), ("tech", "Technical"), ("sounds", "Sounds"),          # 0.5.9: + Sounds
            ("isles", "Starter islands")]                                                                       # 0.5.12: camp + mini boss''')
P2_ROWS = [
    ("camp.enabled", "Island 2 camp", "isles", "bool", "true", "", "", "", "", "live",
     "Skeletons at island 2's old camp while a member is on island 2 (3-island islands only).", "field:IslandCfg.CAMP_ON@config.properties:camp.enabled"),
    ("camp.count", "Camp skeletons", "isles", "int", "3", "0", "20", "step=1", "", "live",
     "How many skeletons the camp keeps up.", "field:IslandCfg.CAMP_COUNT@config.properties:camp.count"),
    ("camp.max", "Camp skeletons at most", "isles", "int", "5", "1", "20", "step=1", "", "live",
     "Never more alive at the camp than this (leftovers count too).", "field:IslandCfg.CAMP_MAX@config.properties:camp.max"),
    ("camp.respawnSeconds", "Camp respawn time", "isles", "int", "60", "5", "3600", "step=5", "s", "live",
     "A new skeleton comes this long after one dies.", "field:IslandCfg.CAMP_RESPAWN@config.properties:camp.respawnSeconds"),
    ("camp.roles", "Camp mobs", "isles", "text", "Skeleton_Fighter,Skeleton_Fighter,Skeleton_Soldier", "1", "300", "", "", "live,adv",
     "NPC role ids, comma separated, used in turn.", "field:IslandCfg.CAMP_ROLES@config.properties:camp.roles"),
    ("camp.levelMin", "Camp lowest level", "isles", "int", "1", "1", "1000", "step=1", "", "live",
     "Lowest mob level at the camp (needs SkyyMobs).", "field:IslandCfg.CAMP_LV_MIN@config.properties:camp.levelMin"),
    ("camp.levelMax", "Camp highest level", "isles", "int", "3", "1", "1000", "step=1", "", "live",
     "Highest mob level at the camp (needs SkyyMobs).", "field:IslandCfg.CAMP_LV_MAX@config.properties:camp.levelMax"),
    ("boss.enabled", "Island 3 mini boss", "isles", "bool", "true", "", "", "", "", "live",
     "The mini boss wakes when a member comes near; it drops the Hub Shard for the portal.",
     "field:IslandCfg.BOSS_ON@config.properties:boss.enabled;after=IslandHooks.afterDesign"),
    ("boss.cooldownSeconds", "Mini boss respawn time", "isles", "int", "300", "10", "86400", "step=30", "s", "live",
     "After the mini boss dies the next one waits this long.", "field:IslandCfg.BOSS_COOLDOWN@config.properties:boss.cooldownSeconds"),
    ("boss.level", "Mini boss level", "isles", "int", "10", "1", "1000", "step=1", "", "live",
     "Its level (needs SkyyMobs).", "field:IslandCfg.BOSS_LEVEL@config.properties:boss.level"),
    ("boss.role", "Mini boss mob", "isles", "text", "Golem_Crystal_Earth", "1", "80", "", "", "live,adv",
     "NPC role id. The tutorial's mini boss task counts Golem_Crystal_Earth.", "field:IslandCfg.BOSS_ROLE@config.properties:boss.role"),
    ("boss.name", "Mini boss name", "isles", "text", "Shardkeeper", "1", "40", "", "", "live",
     "The name over its head.", "field:IslandCfg.BOSS_NAME@config.properties:boss.name"),
    ("islands.respawnHome", "Respawn on your island", "hub", "bool", "true", "", "", "", "", "live",
     "After a death you wake on your island (a bed where you died wins; no island = the hub).",
     "field:IslandCfg.RESPAWN_HOME@config.properties:islands.respawnHome"),
    ("islands.respawnKeep", "Worlds with their own respawn", "hub", "text", "skyy-shard-,skywynn_z", "0", "200", "", "", "live,adv",
     "World name starts, comma separated: deaths there keep that world's respawn (shards, zones).",
     "field:IslandCfg.RESPAWN_KEEP@config.properties:islands.respawnKeep"),
]
for _r in P2_ROWS:
    assert len(_r[1]) <= 40 and len(_r[10]) <= 100, _r
rep('''     "field:IslandCfg.SND_PORTAL_ID@config.properties:sound.portal.id;check=IslandSnd.check"),
]''', '''     "field:IslandCfg.SND_PORTAL_ID@config.properties:sound.portal.id;check=IslandSnd.check"),
] + P2_ROWS   # 0.5.12: the camp, the mini boss, respawn on your island (P2_ROWS is defined after RANKS)''')
# the rows must exist before CFG_ROWS is built: define P2_ROWS right after FLAGS (python, build time)
rep('''RANKS = ["visitor", "trusted", "member", "admin", "owner"]
''', '''RANKS = ["visitor", "trusted", "member", "admin", "owner"]
# 0.5.12: Server Setup rows of the camp / mini boss / respawn (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
P2_ROWS = %r
''' % (P2_ROWS,))

# ================================================================================================ the classes
rep('''plfn = K("PlaceFn")          # 0.5.10: island:fn:place - a named place of the 3 starter islands
''', '''plfn = K("PlaceFn")          # 0.5.10: island:fn:place - a named place of the 3 starter islands
iapi = pool.makeInterface(PKG + ".IsleApi")   # 0.5.12: the engine seam of part 2 (IsleLife.API; the harness puts a stand-in there)
ista = K("IsleState")        # 0.5.12: one island world's camp / boss / portal state (memory)
ilif = K("IsleLife")         # 0.5.12: the camp, the mini boss, the Hub Shard, the portal, respawn routing (logic through IsleApi)
ieng = K("IsleEng")          # 0.5.12: IsleApi on the real engine
itsk = K("IsleTask")         # 0.5.12: one job on a world thread (tick / loot / portal use / respawn) + the 1 s ticker + IO saves
iuse = K("IsleUse", T["EES"])        # 0.5.12: UseBlockEvent$Pre on the portal socket / pad
idth = K("IsleDeath", T["ODS"])      # 0.5.12: camp / boss deaths (DeathComponent added)
irsp = K("IsleRespawn", T["ORS"])    # 0.5.12: a player respawned (DeathComponent removed)
''')
rep('''       s3i, plfn]''', '''       s3i, plfn, iapi, ista, ilif, ieng, itsk, iuse, idth, irsp]''')

# ================================================================================================ guard: our blocks are not guarded
rep('''  if (t != @ITY@.Use && t != @ITY@.Secondary) return -1;
''', '''  if (t != @ITY@.Use && t != @ITY@.Secondary) return -1;
  try { if (String.valueOf(bt.getId()).startsWith("Skyy_Island_")) return -1; } catch (Throwable x) { }   // 0.5.12: the portal socket / pad (IsleUse)
''')

# ================================================================================================ the part-2 code (before the plugin)
P2 = r'''
# =====================================================================================================================
# 0.5.12 STARTER ISLANDS PART 2 (tools/islands_0_5_12_patch.py): the island 2 camp, the island 3 mini boss + the Hub Shard, the working
# portal, respawn on your island. Logic in IsleLife through the engine seam IsleApi (IsleEng = the real engine; the harness swaps in a
# stand-in), one IsleTask per job on the right thread, three ECS hooks (IsleUse, IsleDeath, IsleRespawn).
# =====================================================================================================================
P2_SHARD, P2_SOCKET, P2_PAD = "Skyy_Hub_Shard", "Skyy_Island_Portal_Socket", "Skyy_Island_Hub_Portal"
_p2z = _zf.ZipFile(_SNDZ)        # the CACHED Assets.zip (0.5.11) - read only
_p2n = set(_p2z.namelist())
for _r in ("Skeleton_Fighter", "Skeleton_Soldier", "Golem_Crystal_Earth"):
    assert any(n_.startswith("Server/NPC/Roles/") and n_.endswith("/" + _r + ".json") for n_ in _p2n), "NPC role %s is not in Assets.zip" % _r
for _snd in ("SFX_Crystal_Hit", "SFX_Portal_Neutral", "SFX_Portal_Neutral_Open"):
    assert any(n_.startswith("Server/Audio/SoundEvents/") and n_.endswith("/" + _snd + ".json") for n_ in _p2n), "sound %s" % _snd
for _p in ("Common/Resources/Crystals/Crystal_Fragment.blockymodel", "Common/Resources/Crystals/Crystal_Fragment_Textures/Void.png",
           "Common/BlockTextures/Rock_Stone_Brick_Smooth.png", "Common/Blocks/Miscellaneous/Platform_MagicInactive.blockymodel",
           "Common/Blocks/Miscellaneous/Platform_Magic_Blue2.png", "Common/Blocks/Miscellaneous/Platform_Magic_Idle.blockyanim",
           "Common/Icons/ItemsGenerated/Rock_Stone_Brick_Smooth.png", "Common/Icons/ItemsGenerated/Portal_Device.png",
           "Server/Particles/Spell/Portal/MagicPortal_Default.particlesystem", "Server/Item/Qualities/Rare.json", "Server/Item/Qualities/Technical.json"):
    assert _p in _p2n, "vanilla asset %s is gone (the engine changed?)" % _p
for _id in (P2_SHARD, P2_SOCKET, P2_PAD):
    assert not any(n_.endswith("/" + _id + ".json") for n_ in _p2n), "%s is already a vanilla id" % _id
P2_ICON_PATH = "Icons/ItemsGenerated/%s.png" % P2_SHARD
P2_ICON = open(os.path.join(HERE, "..", "research", "cloud", "icons-1013", "icons", "Skyy_Hub_Shard.png"), "rb").read()   # our own art
assert P2_ICON[:4] == b"\x89PNG"


def _p2_use(snd):
    return {"Interactions": [{"Type": "Simple", "Effects": {"LocalSoundEventId": snd}}]}   # the vanilla plush pattern: a use with a sound


P2_ITEMS = {
    P2_SHARD: {"TranslationProperties": {"Name": "server.items.%s.name" % P2_SHARD, "Description": "server.items.%s.description" % P2_SHARD},
               "Icon": P2_ICON_PATH, "Categories": ["Items.Utility"], "MaxStack": 16, "Quality": "Rare", "PlayerAnimationsId": "Item",
               "Model": "Resources/Crystals/Crystal_Fragment.blockymodel", "Texture": "Resources/Crystals/Crystal_Fragment_Textures/Void.png",
               "Scale": 1.2, "IconProperties": {"Scale": 0.75, "Translation": [-0.3, 0.3], "Rotation": [34.315, 29.815, 22.5]},
               "ItemSoundSetId": "ISS_Items_Gems"},
    P2_SOCKET: {"TranslationProperties": {"Name": "server.items.%s.name" % P2_SOCKET}, "Icon": "Icons/ItemsGenerated/Rock_Stone_Brick_Smooth.png",
                "PlayerAnimationsId": "Block", "Quality": "Technical",
                "BlockType": {"Material": "Solid", "DrawType": "Cube", "Group": "Stone", "Flags": {},
                              "Gathering": {"Breaking": {"GatherType": "Unbreakable"}}, "BlockParticleSetId": "Stone",
                              "Textures": [{"All": "BlockTextures/Rock_Stone_Brick_Smooth.png", "Weight": 1}],
                              "ParticleColor": "#737055", "BlockSoundSetId": "Stone", "PhysicalMaterialId": "Stone",   # ui-data: block particles (not UI)
                              "Light": {"Color": "#536"},   # ui-data: a faint violet glow of the empty socket (not UI)
                              "InteractionHint": "server.interactionHints.repair", "Interactions": {"Use": _p2_use("SFX_Crystal_Hit")}}},
    P2_PAD: {"TranslationProperties": {"Name": "server.items.%s.name" % P2_PAD}, "Icon": "Icons/ItemsGenerated/Portal_Device.png",
             "PlayerAnimationsId": "Block", "Quality": "Technical",
             "BlockType": {"DrawType": "Model", "Material": "Solid", "Opacity": "Transparent",
                           "CustomModel": "Blocks/Miscellaneous/Platform_MagicInactive.blockymodel",
                           "CustomModelTexture": [{"Texture": "Blocks/Miscellaneous/Platform_Magic_Blue2.png", "Weight": 1}],
                           "CustomModelAnimation": "Blocks/Miscellaneous/Platform_Magic_Idle.blockyanim",
                           "HitboxType": "Pad_Portal", "BlockParticleSetId": "Stone", "BlockSoundSetId": "Stone", "PhysicalMaterialId": "Stone",
                           "VariantRotation": "NESW", "Flags": {}, "Gathering": {"Breaking": {"GatherType": "Unbreakable"}},
                           "Light": {"Color": "#77f", "Radius": 3},   # ui-data: the vanilla hub portal pad's light (not UI)
                           "AmbientSoundEventId": "SFX_Portal_Neutral",
                           "Particles": [{"SystemId": "MagicPortal_Default", "PositionOffset": {"Y": 2.0}, "Scale": 0.8}],
                           "InteractionHint": "server.interactionHints.activate", "Interactions": {"Use": _p2_use("SFX_Portal_Neutral_Open")}}},
}
P2_LANG = []
for _pre in ("", "server."):
    P2_LANG += ["%sitems.%s.name=Hub Shard" % (_pre, P2_SHARD),
                "%sitems.%s.description=Dropped by the Shardkeeper on island 3. Use it on the broken portal at the summit to repair it - the "
                "portal takes you to the hub." % (_pre, P2_SHARD),
                "%sitems.%s.name=Broken Hub Portal" % (_pre, P2_SOCKET),
                "%sitems.%s.name=Hub Portal" % (_pre, P2_PAD)]
P2_FILES = dict(("Server/Item/Items/SkyyIslands/%s.json" % k_, json.dumps(v_, indent=2)) for k_, v_ in P2_ITEMS.items())
P2_FILES["Server/Languages/en-US/server.lang"] = "\n".join(P2_LANG) + "\n"

# the engine members part 2 calls (a missing one stops the build here, not in game)
for c, m in ((T["NPCP"], "get"), (T["NPCP"], "spawnNPC"), (T["NPCP"], "hasRoleName"), (T["PAIR"], "first"), (T["UUC"], "getUuid"),
             (T["UUC"], "getComponentType"), (T["ODS"], "onComponentAdded"), (T["ORS"], "onComponentRemoved"), (T["DTH"], "getDeathInfo"),
             (T["DTH"], "getComponentType"), (T["DMG"], "getSource"), (T["DENT"], "getRef"), (T["EMOD"], "get"),
             (T["EMOD"], "getEntitySpatialResourceType"), (T["SPR"], "getSpatialStructure"),
             ("com.hypixel.hytale.component.spatial.SpatialStructure", "collect"), (T["ST"], "getResource"), (T["ST"], "putComponent"),
             (T["ST"], "getExternalData"), (T["EST"], "getRefFromUUID"), (T["EST"], "getStore"), (T["WLD"], "getEntityStore"),
             (T["WLD"], "getPlayerRefs"), (T["WLD"], "isAlive"), (T["WLD"], "getName"), (T["PLA"], "getPlayerConfigData"), (T["PLA"], "getInventory"),
             ("com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData", "getPerWorldData"), (T["PWD"], "getRespawnPoints"),
             (T["PRP"], "getRespawnPosition"), (T["INV"], "getStorage"), (T["INV"], "getHotbar"), (T["INV"], "getBackpack"),
             (T["IC"], "removeItemStackFromSlot"), (T["IS"], "getItemId"), (T["NPL"], "getComponentType"), (T["DNC"], "getComponentType"),
             (T["TC"], "getPosition"), (T["UNI"], "getDefaultWorld"), (T["UBE"], "getBlockType"), (T["UBE"], "getInteractionType"),
             (T["BTY"], "getId"), (T["ACH"], "getReferenceTo"), (T["R3F"], "setYaw"), (T["PR"], "getUuid"), (T["REF"], "getStore")):
    B.probe(pool, c, m)
_P2 = S3_P2
P2_PAD_BOX = (_P2["pad"][0] - 0.3, _P2["pad"][1] - 0.2, _P2["pad"][2] - 1.0, _P2["pad"][0] + 1.3, _P2["pad"][1] + 2.0, _P2["pad"][2] + 2.0)


def _jd(vals):
    return ", ".join(repr(float(v_)) for v_ in vals)


def _ji(vals):
    return ", ".join(str(int(v_)) for v_ in vals)


# ---------------------------------------------------------------------------------------------------------------- IsleApi (the seam)
for _sig in ("public abstract long now();",
             "public abstract Object[] players(String wn);",
             "public abstract java.util.ArrayList npcs(String wn, double x, double y, double z, double r);",
             "public abstract boolean alive(String wn, String uuid);",
             "public abstract boolean roleOk(String role);",
             "public abstract String spawn(String wn, String role, double x, double y, double z, float yaw);",
             "public abstract boolean level(String wn, String uuid, int lvl, String name);",
             "public abstract String block(String wn, int x, int y, int z);",
             "public abstract boolean setBlock(String wn, int x, int y, int z, String id);",
             "public abstract long count(String wn, java.util.UUID u, String id);",
             "public abstract long take(String wn, java.util.UUID u, String id, long n);",
             "public abstract long give(String wn, java.util.UUID u, String id, long n);",
             "public abstract void say(java.util.UUID u, String text, String color);",
             "public abstract String name(java.util.UUID u);",
             "public abstract boolean toHub(String wn, java.util.UUID u);",
             "public abstract boolean hasBed(java.util.UUID u, String inWorld);",
             "public abstract int goHome(String wn, java.util.UUID u, String homeKey, String homeWorld);",
             "public abstract boolean exec(String wn, Runnable r);",
             "public abstract boolean save(Runnable r);",
             "public abstract boolean quest(java.util.UUID u, String key);",
             "public abstract boolean isAdmin(java.util.UUID u);",
             "public abstract String hubWorld();",
             "public abstract java.util.Set islandWorlds();",
             "public abstract void relight(String wn);"):
    M(iapi, _sig)

# ---------------------------------------------------------------------------------------------------------------- IsleState (memory)
for _f in ("public String world;", "public int three;", "public long probeAt;", "public long campNext;", "public long bossNext;",
           "public String boss;", "public final java.util.HashSet camp = new java.util.HashSet();", "public int spot;", "public int role;",
           "public long blocksAt;", "public boolean portal;", "public boolean named;",
           "public final java.util.ArrayList due = new java.util.ArrayList();"):   # fix (g): one respawn time per camp death
    F(ista, _f)
C(ista, "public IsleState(String w) { this.world = w; this.three = -1; }")

# ---------------------------------------------------------------------------------------------------------------- IsleTask (fields + ctor; run() below)
itsk.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public int mode;", "public String wn;", "public java.util.UUID u;", "public String a;", "public String[] ks;", "public String[] vs;"):
    F(itsk, _f)
C(itsk, "public IsleTask(int mode, String wn, java.util.UUID u) { this.mode = mode; this.wn = wn; this.u = u; }")

# ---------------------------------------------------------------------------------------------------------------- IsleEng (IsleApi on the engine)
ieng.addInterface(iapi)
C(ieng, "public IsleEng() { }")
M(ieng, "public static @WLD@ world(String wn) { return @PKG@.IslandStore.loadedWorld(wn); }")
M(ieng, "public long now() { return System.currentTimeMillis(); }")
# players in that world: Object[] { UUID, Double x, Double y, Double z } each (world thread)
M(ieng, r"""
public Object[] players(String wn) {
  @WLD@ w = world(wn);
  if (w == null) return new Object[0];
  java.util.ArrayList out = new java.util.ArrayList();
  Object[] a = w.getPlayerRefs().toArray();
  for (int i = 0; i < a.length; i++) {
    if (!(a[i] instanceof @PR@)) continue;
    @PR@ pr = (@PR@) a[i];
    try {
      @REF@ r = pr.getReference();
      if (r == null || !r.isValid()) continue;
      @TC@ tc = (@TC@) r.getStore().getComponent(r, @TC@.getComponentType());
      if (tc == null) continue;
      @V3D@ p = tc.getPosition();
      out.add(new Object[] { pr.getUuid(), Double.valueOf(p.x), Double.valueOf(p.y), Double.valueOf(p.z) });
    } catch (Throwable t) { }
  }
  return out.toArray();
}""")
# NPCs (alive) within rad of a point: Object[] { String uuid, String role } each - the engine's entity spatial index (Selector pattern)
M(ieng, r"""
public java.util.ArrayList npcs(String wn, double x, double y, double z, double rad) {
  java.util.ArrayList out = new java.util.ArrayList();
  @WLD@ w = world(wn);
  if (w == null) return out;
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
    @NPC@ n = (@NPC@) st.getComponent(r, @NPC@.getComponentType());
    if (n == null || st.getComponent(r, @DTH@.getComponentType()) != null) continue;
    @UUC@ uc = (@UUC@) st.getComponent(r, @UUC@.getComponentType());
    if (uc == null || uc.getUuid() == null) continue;
    out.add(new Object[] { uc.getUuid().toString(), n.getRoleName() });
  }
  return out;
}""")
M(ieng, r"""
public boolean alive(String wn, String uuid) {
  @WLD@ w = world(wn);
  if (w == null || uuid == null) return false;
  try {
    @REF@ r = w.getEntityStore().getRefFromUUID(java.util.UUID.fromString(uuid));
    if (r == null || !r.isValid()) return false;
    return r.getStore().getComponent(r, @DTH@.getComponentType()) == null;
  } catch (Throwable t) { return false; }
}""")
M(ieng, r"""
public boolean roleOk(String role) {
  try { return role != null && role.length() > 0 && @NPCP@.get().hasRoleName(role); } catch (Throwable t) { return false; }
}""")
# NPCPlugin.spawnNPC(store, role, null, pos, rot) = SkyyMerchants / SkyyQuests' call shape (world thread, outside any system); its UUID
M(ieng, r"""
public String spawn(String wn, String role, double x, double y, double z, float yaw) {
  @WLD@ w = world(wn);
  if (w == null) return null;
  @ST@ st = w.getEntityStore().getStore();
  @R3F@ rot = new @R3F@();
  rot.setYaw(yaw);
  @PAIR@ p = @NPCP@.get().spawnNPC(st, role, (String) null, (@V3DC@) new @V3D@(x, y, z), (@R3C@) rot);
  @REF@ e = p == null ? null : (@REF@) p.first();
  if (e == null || !e.isValid()) return null;
  @UUC@ uc = (@UUC@) st.getComponent(e, @UUC@.getComponentType());
  return uc == null || uc.getUuid() == null ? null : uc.getUuid().toString();
}""")
# SkyyMobs 0.1.9 mob:fn:setLevel (level + plate name); without it: no level, the name goes on the Nameplate + display name here
M(ieng, r"""
public boolean level(String wn, String uuid, int lvl, String name) {
  try {
    Object f = @PKG@.IslandStore.bridge().get("mob:fn:setLevel");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { wn, java.util.UUID.fromString(uuid), Integer.valueOf(lvl), name });
      if (Boolean.TRUE.equals(r)) return true;
    }
  } catch (Throwable t) { }
  if (name == null || name.length() == 0) return false;
  try {
    @WLD@ w = world(wn);
    if (w == null) return false;
    @REF@ r = w.getEntityStore().getRefFromUUID(java.util.UUID.fromString(uuid));
    if (r == null || !r.isValid()) return false;
    @ST@ st = r.getStore();
    st.putComponent(r, @NPL@.getComponentType(), new @NPL@(name));
    st.putComponent(r, @DNC@.getComponentType(), new @DNC@(@MSG@.raw(name)));
  } catch (Throwable t) { }
  return false;
}""")
# the block id at x,y,z: null = not loaded, "" = air (FillTask.blockAt)
M(ieng, r"""
public String block(String wn, int x, int y, int z) {
  @WLD@ w = world(wn);
  if (w == null) return null;
  int b = @PKG@.FillTask.blockAt(w, x, y, z);
  if (b < 0) return null;
  if (b == 0) return "";
  @BTY@ t = (@BTY@) @BTY@.getAssetMap().getAsset(b);
  return t == null ? "?" : String.valueOf(t.getId());
}""")
# BlockOperations.setBlock exactly as FillTask.put (rotation 0, filler 0, settings 0)
M(ieng, r"""
public boolean setBlock(String wn, int x, int y, int z, String id) {
  @WLD@ w = world(wn);
  if (w == null) return false;
  try {
    @REF@ r = @PKG@.FillTask.section(w, x, y, z);
    if (r == null) return false;
    int bid = @BTY@.getAssetMap().getIndex(id);
    if (bid == Integer.MIN_VALUE) return false;
    @BTY@ type = (@BTY@) @BTY@.getAssetMap().getAsset(bid);
    if (type == null) return false;
    return @BOP@.setBlock(w.getChunkStore(), r, x, y, z, bid, type, 0, 0, 0);
  } catch (Throwable t) { return false; }
}""")
# the player's bags, storage first (world thread)
M(ieng, r"""
public static @IC@[] conts(java.util.UUID u) {
  @PR@ pr = @PKG@.IslandStore.online(u);
  if (pr == null) return null;
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return null;
  @PLA@ pl = (@PLA@) r.getStore().getComponent(r, @PLA@.getComponentType());
  @INV@ in = pl == null ? null : pl.getInventory();
  if (in == null) return null;
  return new @IC@[] { in.getStorage(), in.getHotbar(), in.getBackpack() };
}""")
M(ieng, r"""
public static long countIn(@IC@[] cs, String id) {
  long n = 0L;
  if (cs == null || id == null) return 0L;
  for (int i = 0; i < cs.length; i++) {
    if (cs[i] == null) continue;
    short cap = cs[i].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cs[i].getItemStack(s);
      if (it != null && !it.isEmpty() && id.equals(it.getItemId())) n += (long) it.getQuantity();
    }
  }
  return n;
}""")
M(ieng, "public long count(String wn, java.util.UUID u, String id) { return countIn(conts(u), id); }")
# take exactly n (slot by slot, counted before and after); what was really taken
M(ieng, r"""
public long take(String wn, java.util.UUID u, String id, long n) {
  @IC@[] cs = conts(u);
  if (cs == null || n <= 0L) return 0L;
  long before = countIn(cs, id);
  long left = n;
  for (int i = 0; i < cs.length && left > 0L; i++) {
    if (cs[i] == null) continue;
    short cap = cs[i].getCapacity();
    for (short s = 0; s < cap && left > 0L; s++) {
      @IS@ it = cs[i].getItemStack(s);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
      int want = (int) Math.min((long) it.getQuantity(), left);
      try { cs[i].removeItemStackFromSlot(s, want); } catch (Throwable t) { }
      left = n - (before - countIn(cs, id));
    }
  }
  return before - countIn(cs, id);
}""")
# give n, storage first (counted); what really arrived
M(ieng, r"""
public long give(String wn, java.util.UUID u, String id, long n) {
  @IC@[] cs = conts(u);
  if (cs == null || n <= 0L) return 0L;
  long before = countIn(cs, id);
  for (int i = 0; i < cs.length; i++) {
    long got = countIn(cs, id) - before;
    if (got >= n) break;
    if (cs[i] == null) continue;
    try { cs[i].addItemStack(new @IS@(id, (int) (n - got))); } catch (Throwable t) { }
  }
  return countIn(cs, id) - before;
}""")
M(ieng, "public void say(java.util.UUID u, String text, String color) { @PKG@.IslandStore.sayU(u, text, color); }")
M(ieng, r"""
public String name(java.util.UUID u) {
  @PR@ pr = @PKG@.IslandStore.online(u);
  return pr == null ? "Someone" : pr.getUsername();
}""")
# the /hub path (SendHubTask.now: HubCmd.sendToHub, at most once per player per 4 s) + the portal sound on arrival
M(ieng, r"""
public boolean toHub(String wn, java.util.UUID u) {
  @PR@ pr = @PKG@.IslandStore.online(u);
  if (pr == null) return false;
  @REF@ r = pr.getReference();
  @WLD@ w = world(wn);
  if (r == null || !r.isValid() || w == null) return false;
  @PKG@.IslandSnd.arm(u);
  return @PKG@.SendHubTask.now(r.getStore(), r, pr, w, null);
}""")
# the player's respawn points (beds) in one world, read from the saved per-world data WITHOUT creating an entry; null = none
M(ieng, r"""
public static @PRP@[] points(java.util.UUID u, String inWorld) {
  @PR@ pr = @PKG@.IslandStore.online(u);
  if (pr == null || inWorld == null) return null;
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return null;
  @PLA@ pl = (@PLA@) r.getStore().getComponent(r, @PLA@.getComponentType());
  if (pl == null || pl.getPlayerConfigData() == null) return null;
  java.util.Map m = pl.getPlayerConfigData().getPerWorldData();
  Object o = m == null ? null : m.get(inWorld);
  if (!(o instanceof @PWD@)) return null;
  @PRP@[] a = ((@PWD@) o).getRespawnPoints();
  if (a == null || a.length == 0 || a[0] == null) return null;
  return a;
}""")
M(ieng, "public boolean hasBed(java.util.UUID u, String inWorld) { return points(u, inWorld) != null; }")
# respawn -> the island: loaded island world = the bed there (1) or its spawn point (2) by a Teleport component; else /island's own load (3)
M(ieng, r"""
public int goHome(String wn, java.util.UUID u, String hk, String home) {
  @PR@ pr = @PKG@.IslandStore.online(u);
  if (pr == null || home == null || hk == null) return 0;
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return 0;
  @ST@ st = r.getStore();
  @WLD@ from = world(wn);
  if (from == null) return 0;
  @WLD@ w2 = world(home);
  if (w2 != null) {
    @TRF@ where = null;
    int how = 2;
    @PRP@[] pts = points(u, home);
    if (pts != null && pts[0].getRespawnPosition() != null) {
      @V3D@ p = pts[0].getRespawnPosition();
      where = new @TRF@(p.x, p.y, p.z, 0.0f, 0.0f, 0.0f);
      how = 1;
    } else {
      try {
        java.util.concurrent.CompletableFuture f = w2.getWorldConfig().getSpawnProvider().getSpawnPointAsync(w2, u);
        if (f != null && f.isDone()) { Object o = f.getNow(null); where = (o instanceof @TRF@) ? (@TRF@) o : null; }
      } catch (Throwable t) { where = null; }
    }
    if (where != null) {
      try {
        ((@CA@) st).addComponent(r, @TP@.getComponentType(), @TP@.createForPlayer(w2, where));
        return how;
      } catch (Throwable t) { @PKG@.IslandStore.warn("respawn teleport to the island failed (using /island instead): " + t); }
    }
  }
  @PKG@.IslandCmd.go(st, r, pr, from, hk, hk.equals(@PKG@.IslandStore.pkey(u)));
  return 3;
}""")
M(ieng, r"""
public boolean exec(String wn, Runnable r) {
  @WLD@ w = world(wn);
  if (w == null || r == null) return false;
  try { w.execute(r); return true; } catch (Throwable t) { return false; }
}""")
# SkyyIslands-IO (never a file on a world thread); IO not running = run here; false = it ran here
M(ieng, r"""
public boolean save(Runnable r) {
  java.util.concurrent.ExecutorService e = @PKG@.IslandStore.IO;
  if (e != null && !@PKG@.IslandStore.STOPPING) {
    try { e.execute(r); return true; } catch (Throwable t) { }
  }
  r.run();
  return false;
}""")
M(ieng, r"""
public boolean quest(java.util.UUID u, String key) {
  try {
    Object f = @PKG@.IslandStore.bridge().get("quest:fn:event");
    if (!(f instanceof java.util.function.Function)) return false;
    return Boolean.TRUE.equals(((java.util.function.Function) f).apply(new Object[] { u, "event", key, Long.valueOf(1L) }));
  } catch (Throwable t) { return false; }
}""")
M(ieng, r"""
public boolean isAdmin(java.util.UUID u) {
  @PR@ pr = @PKG@.IslandStore.online(u);
  return pr != null && @PKG@.IslandPerms.isAdmin(pr);
}""")
M(ieng, r"""
public String hubWorld() {
  String h = @PKG@.IslandStore.HUB_WORLD;
  if (h != null) return h;
  try { @WLD@ d = @UNI@.get().getDefaultWorld(); return d == null ? null : d.getName(); } catch (Throwable t) { return null; }
}""")
M(ieng, r"""
public java.util.Set islandWorlds() {
  java.util.HashSet out = new java.util.HashSet();
  try {
    @UNI@ uni = @UNI@.get();
    java.util.Iterator it = uni.getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @PR@)) continue;
      java.util.UUID wu = ((@PR@) o).getWorldUuid();
      if (wu == null) continue;
      @WLD@ w = uni.getWorld(wu);
      if (w == null || !w.isAlive()) continue;
      if (@PKG@.IslandStore.isIslandWorld(w.getName())) out.add(w.getName());
    }
  } catch (Throwable t) { }
  return out;
}""")
M(ieng, "public void relight(String wn) { @PKG@.RelightTask.schedule(wn); }")

# ---------------------------------------------------------------------------------------------------------------- IsleLife (the logic)
for _f in ("public static volatile @PKG@.IsleApi API = null;",
           "public static volatile int HOOKS = 0;",
           "public static final java.util.concurrent.ConcurrentHashMap ST = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap GOT = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap QUEUED = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap STEP = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap WARN = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile java.nio.file.Path GOT_FILE = null;",
           "public static final Object GOT_LOCK = new Object();",
           "public static final java.util.concurrent.atomic.AtomicLong SPAWNED = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong BOSSES = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong GIVEN = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong REPAIRS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong TRIPS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong ROUTED = new java.util.concurrent.atomic.AtomicLong();",
           'public static final String SHARD = "%s";' % P2_SHARD,
           'public static final String SOCKET = "%s";' % P2_SOCKET,
           'public static final String PAD = "%s";' % P2_PAD,
           "public static final double[] CAMP = new double[] { %s };" % _jd(_P2["camp"]),
           "public static final double[] ISLE2 = new double[] { %s };" % _jd(_P2["isle2"]),
           "public static final double[] BOSS = new double[] { %s };" % _jd(_P2["boss"]),
           "public static final int[] SOCKETP = new int[] { %s };" % _ji(_P2["socket"]),
           "public static final int[] FIX = new int[] { %s };" % ", ".join(_ji(f_[:3]) for f_ in _P2["fix"]),
           "public static final String[] FIX_IDS = new String[] { %s };" % ", ".join('"%s"' % f_[3] for f_ in _P2["fix"]),
           "public static final double[] SPOTS = new double[] { %s };" % ", ".join(_jd(sp_) for sp_ in _P2["spots"]),
           "public static final int[] PROBE = new int[] { %s };" % ", ".join(_ji(p_) for p_ in _P2["probe"]),
           "public static final double[] PAD_BOX = new double[] { %s };" % _jd(P2_PAD_BOX),
           "public static final int PROBE_NEED = 6;",
           "public static final double ISLE2_R = 18.0;", "public static final double CAMP_R = 28.0;", "public static final double BOSS_NEAR = 18.0;",
           "public static final double BOSS_R = 40.0;", "public static final double LOOT_R = 32.0;",
           'public static final String REPAIR_TEXT = "[Island] Repair this portal with a Hub Shard (the Shardkeeper on this island drops one)";'):
    F(ilif, _f)
M(ilif, r"""
public static @PKG@.IsleApi api() {
  @PKG@.IsleApi a = API;
  if (a == null) { a = new @PKG@.IsleEng(); API = a; }
  return a;
}""")
M(ilif, r"""
public static void warnOnce(String key, String msg) {
  if (WARN.size() > 256) WARN.clear();
  if (WARN.putIfAbsent(key, Boolean.TRUE) == null) @PKG@.IslandStore.warn(msg);
}""")
M(ilif, r"""
public static @PKG@.IsleState state(String wn) {
  Object o = ST.get(wn);
  if (o instanceof @PKG@.IsleState) return (@PKG@.IsleState) o;
  if (ST.size() > 4096) ST.clear();
  @PKG@.IsleState s = new @PKG@.IsleState(wn);
  Object p = ST.putIfAbsent(wn, s);
  return p instanceof @PKG@.IsleState ? (@PKG@.IsleState) p : s;
}""")
M(ilif, r"""
public static String[] roles(String csv) {
  java.util.ArrayList l = new java.util.ArrayList();
  String[] a = csv == null ? new String[0] : csv.split(",");
  for (int i = 0; i < a.length; i++) {
    String t = a[i].trim();
    if (t.length() > 0) l.add(t);
  }
  String[] out = new String[l.size()];
  for (int i = 0; i < out.length; i++) out[i] = (String) l.get(i);
  return out;
}""")
M(ilif, r"""
public static boolean inList(String[] a, String r) {
  if (r == null || a == null) return false;
  for (int i = 0; i < a.length; i++) if (a[i].equals(r)) return true;
  return false;
}""")
M(ilif, r"""
public static double d2(double ax, double az, double bx, double bz) {
  double dx = ax - bx;
  double dz = az - bz;
  return dx * dx + dz * dz;
}""")
M(ilif, r"""
public static boolean fileHas(String owner, String key, String val) {
  try {
    @PKG@.IslandSettings s = @PKG@.IslandStore.settings(owner);
    return s != null && !s.bad && s.raw != null && val.equals(s.raw.getProperty(key));
  } catch (Throwable t) { return false; }
}""")
# repaired = this session's repair (st.portal: before the island file write lands) or portal=1 in the island file
M(ilif, r"""
public static boolean portalOn(String owner, @PKG@.IsleState st) {
  return (st != null && st.portal) || fileHas(owner, "portal", "1");
}""")
# island file keys through SkyyIslands-IO (IsleTask mode 6 -> IslandStore.setProps: the island's own lock, PEND, the IO writer)
M(ilif, r"""
public static void saveProps(String owner, String[] ks, String[] vs) {
  @PKG@.IsleTask t = new @PKG@.IsleTask(6, null, null);
  t.a = owner;
  t.ks = ks;
  t.vs = vs;
  api().save(t);
}""")
# 1 = a 3-island island (>= PROBE_NEED of the deep stone cells of islands 2 + 3), 0 = not, -1 = cells not loaded (world thread)
M(ilif, r"""
public static int probe(String wn) {
  @PKG@.IsleApi a = api();
  int hit = 0;
  int gone = 0;
  for (int i = 0; i + 2 < PROBE.length; i += 3) {
    String b = a.block(wn, PROBE[i], PROBE[i + 1], PROBE[i + 2]);
    if (b == null) gone++;
    else if ("Rock_Stone".equals(b)) hit++;
  }
  if (hit >= PROBE_NEED) return 1;
  return gone > 0 ? -1 : 0;
}""")
M(ilif, r"""
public static boolean three(String wn, @PKG@.IsleState st, String owner, long now) {
  if (st.three == 1) return true;
  if (st.three == 0 && now - st.probeAt < 60000L) return false;
  if (fileHas(owner, "isles", "3")) { st.three = 1; return true; }
  if (st.three == -1 && st.probeAt != 0L && now - st.probeAt < 5000L) return false;
  int r = probe(wn);
  st.probeAt = now;
  st.three = r;
  if (r != 1) return false;
  saveProps(owner, new String[] { "isles" }, new String[] { "3" });
  return true;
}""")
# rows of players with a role on this island (owner / admin / co-op / trusted = rank >= 1)
M(ilif, r"""
public static java.util.ArrayList members(String owner, Object[] rows) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < rows.length; i++) {
    Object[] r = (Object[]) rows[i];
    if (@PKG@.IslandPerms.rankU(owner, (java.util.UUID) r[0]) >= 1) out.add(r);
  }
  return out;
}""")
M(ilif, r"""
public static boolean anyNear(java.util.ArrayList rows, double cx, double cz, double rad) {
  for (int i = 0; i < rows.size(); i++) {
    Object[] r = (Object[]) rows.get(i);
    double y = ((Double) r[2]).doubleValue();
    if (y < 100.0 || y > 220.0) continue;
    if (d2(((Double) r[1]).doubleValue(), ((Double) r[3]).doubleValue(), cx, cz) <= rad * rad) return true;
  }
  return false;
}""")
# a camp spawn spot is free: its cell + the one above are air, the block under it is solid (loaded)
M(ilif, r"""
public static boolean spotFree(String wn, int s) {
  @PKG@.IsleApi a = api();
  int x = (int) Math.floor(SPOTS[s * 3]);
  int y = (int) Math.floor(SPOTS[s * 3 + 1]);
  int z = (int) Math.floor(SPOTS[s * 3 + 2]);
  String b0 = a.block(wn, x, y, z);
  String b1 = a.block(wn, x, y + 1, z);
  String un = a.block(wn, x, y - 1, z);
  return b0 != null && b0.length() == 0 && b1 != null && b1.length() == 0 && un != null && un.length() > 0;
}""")
# camp skeletons alive: the tracked ones still alive + any camp-role NPC within CAMP_R of the camp (leftovers saved in the chunk)
M(ilif, r"""
public static int campAlive(String wn, @PKG@.IsleState st, String[] rl) {
  @PKG@.IsleApi a = api();
  java.util.HashSet seen = new java.util.HashSet();
  Object[] tr = st.camp.toArray();
  for (int i = 0; i < tr.length; i++) {
    String id = (String) tr[i];
    if (a.alive(wn, id)) seen.add(id); else st.camp.remove(id);
  }
  java.util.ArrayList n = a.npcs(wn, CAMP[0], CAMP[1], CAMP[2], CAMP_R);
  for (int i = 0; i < n.size(); i++) {
    Object[] e = (Object[]) n.get(i);
    if (inList(rl, (String) e[1])) seen.add(e[0]);
  }
  return seen.size();
}""")
M(ilif, r"""
public static int campTick(String wn, @PKG@.IsleState st, java.util.ArrayList mem, long now) {
  if (!@PKG@.IslandCfg.CAMP_ON) return 0;
  if (!anyNear(mem, ISLE2[0], ISLE2[1], ISLE2_R)) return 0;
  String[] rl = roles(@PKG@.IslandCfg.CAMP_ROLES);
  if (rl.length == 0 || now < st.campNext) return 0;
  int wait = 0;
  for (int i = st.due.size() - 1; i >= 0; i--) {
    if (((Long) st.due.get(i)).longValue() <= now) st.due.remove(i); else wait++;
  }
  int target = Math.min(@PKG@.IslandCfg.CAMP_COUNT, @PKG@.IslandCfg.CAMP_MAX);
  int alive = campAlive(wn, st, rl);
  int want = target - alive - wait;
  if (want <= 0) return 0;
  @PKG@.IsleApi a = api();
  int lo = @PKG@.IslandCfg.CAMP_LV_MIN;
  int hi = Math.max(lo, @PKG@.IslandCfg.CAMP_LV_MAX);
  int ns = SPOTS.length / 3;
  int n = 0;
  for (int k = 0; k < want; k++) {
    int pick = -1;
    for (int j = 0; j < ns && pick < 0; j++) {
      int s = (st.spot + j) % ns;
      if (spotFree(wn, s)) pick = s;
    }
    if (pick < 0) break;
    st.spot = pick + 1;
    String role = rl[st.role % rl.length];
    st.role = st.role + 1;
    if (!a.roleOk(role)) { warnOnce("role:" + role, "camp.roles: '" + role + "' is not an NPC role this server knows - skipped"); continue; }
    String id = a.spawn(wn, role, SPOTS[pick * 3], SPOTS[pick * 3 + 1], SPOTS[pick * 3 + 2], 0.0f);
    if (id == null) continue;
    st.camp.add(id);
    a.level(wn, id, lo + java.util.concurrent.ThreadLocalRandom.current().nextInt(hi - lo + 1), null);
    SPAWNED.incrementAndGet();
    n++;
  }
  if (n == 0) st.campNext = now + 10000L;
  return n;
}""")
M(ilif, r"""
public static int bossTick(String wn, @PKG@.IsleState st, java.util.ArrayList mem, long now) {
  if (!@PKG@.IslandCfg.BOSS_ON) return 0;
  String role = @PKG@.IslandCfg.BOSS_ROLE;
  if (role == null || role.length() == 0) return 0;
  if (!anyNear(mem, BOSS[0], BOSS[2], BOSS_NEAR)) return 0;
  @PKG@.IsleApi a = api();
  if (st.boss != null && a.alive(wn, st.boss)) return 0;
  st.boss = null;
  java.util.ArrayList n = a.npcs(wn, BOSS[0], BOSS[1], BOSS[2], BOSS_R);
  for (int i = 0; i < n.size(); i++) {
    Object[] e = (Object[]) n.get(i);
    if (!role.equals(e[1])) continue;
    st.boss = (String) e[0];
    if (!st.named) { st.named = true; a.level(wn, st.boss, @PKG@.IslandCfg.BOSS_LEVEL, @PKG@.IslandCfg.BOSS_NAME); }
    return 0;
  }
  if (now < st.bossNext) return 0;
  if (!a.roleOk(role)) { warnOnce("role:" + role, "boss.role: '" + role + "' is not an NPC role this server knows - no mini boss"); st.bossNext = now + 60000L; return 0; }
  String id = a.spawn(wn, role, BOSS[0], BOSS[1], BOSS[2], 0.0f);
  if (id == null) { st.bossNext = now + 10000L; return 0; }
  st.boss = id;
  st.named = true;
  a.level(wn, id, @PKG@.IslandCfg.BOSS_LEVEL, @PKG@.IslandCfg.BOSS_NAME);
  BOSSES.incrementAndGet();
  for (int i = 0; i < mem.size(); i++) a.say((java.util.UUID) ((Object[]) mem.get(i))[0], "[Island] The " + @PKG@.IslandCfg.BOSS_NAME + " has woken on island 3!", "#ffe08a");
  return 1;
}""")
# the socket while broken / the pad once repaired, re-checked every 30 s (only over the smooth brick, air, or the other of the two)
M(ilif, r"""
public static int portalBlocks(String wn, @PKG@.IsleState st, String owner, long now) {
  if (st.blocksAt != 0L && now - st.blocksAt < 30000L) return 0;
  @PKG@.IsleApi a = api();
  String b = a.block(wn, SOCKETP[0], SOCKETP[1], SOCKETP[2]);
  if (b == null) return 0;
  st.blocksAt = now;
  if (PAD.equals(b)) {            // fix (c): the pad in the socket = repaired, even when the portal=1 write was lost
    st.portal = true;
    if (!fileHas(owner, "portal", "1")) {
      warnOnce("pad:" + wn, "island " + wn + ": the hub portal pad is there but the island file has no portal=1 - written again");
      saveProps(owner, new String[] { "portal" }, new String[] { "1" });
      return 3;
    }
    return 0;
  }
  if (portalOn(owner, st)) {
    if (b.length() == 0 || SOCKET.equals(b) || "Rock_Stone_Brick_Smooth".equals(b)) return a.setBlock(wn, SOCKETP[0], SOCKETP[1], SOCKETP[2], PAD) ? 2 : 0;
    return 0;
  }
  if (b.length() == 0) {           // fix (j): an empty cell only with ground under it (never a floating socket)
    String un = a.block(wn, SOCKETP[0], SOCKETP[1] - 1, SOCKETP[2]);
    if (un == null || un.length() == 0) return 0;
  }
  if (b.length() == 0 || "Rock_Stone_Brick_Smooth".equals(b)) return a.setBlock(wn, SOCKETP[0], SOCKETP[1], SOCKETP[2], SOCKET) ? 1 : 0;
  return 0;
}""")
M(ilif, r"""
public static boolean gate(java.util.UUID u, long now, long gap) {
  Object o = STEP.get(u);
  if (o instanceof Long) {
    long d = now - ((Long) o).longValue();
    if (d >= 0L && d < gap) return false;
  }
  if (STEP.size() > 4096) STEP.clear();
  STEP.put(u, Long.valueOf(now));
  return true;
}""")
# fix (d): SkyyProfiles is swapping this player's bags (PROFILES-CONTRACT 4.5) - no Hub Shard moves now
M(ilif, r"""
public static boolean busy(java.util.UUID u) {
  try { return u != null && @PKG@.IslandStore.bridge().get("profile:busy:" + u) != null; } catch (Throwable t) { return false; }
}""")
# fix (f): the owner of a pet / summon (SkyyPets pets:fn:ownerOf: entity UUID -> owner UUID or String, as SkyyMobs 0.1.8), or null
M(ilif, r"""
public static java.util.UUID petOwner(java.util.UUID e) {
  if (e == null) return null;
  try {
    Object f = @PKG@.IslandStore.bridge().get("pets:fn:ownerOf");
    if (!(f instanceof java.util.function.Function)) return null;
    Object o = ((java.util.function.Function) f).apply(e);
    if (o instanceof java.util.UUID) return (java.util.UUID) o;
    if (o instanceof String) return java.util.UUID.fromString(((String) o).trim());
  } catch (Throwable t) { }
  return null;
}""")
# fix (h): a world whose name starts with one of islands.respawnKeep keeps its own respawn (SkyyShards worlds, zone islands)
M(ilif, r"""
public static boolean keepWorld(String wn) {
  if (wn == null) return false;
  String[] a = roles(@PKG@.IslandCfg.RESPAWN_KEEP);
  for (int i = 0; i < a.length; i++) if (wn.startsWith(a[i])) return true;
  return false;
}""")
# fix (i): /hub from a home island known to be classic (no frame, no portal) = the tutorial's island:portal part (SkyyQuests)
M(ilif, r"""
public static boolean classicTrip(java.util.UUID u) {
  try {
    if (u == null) return false;
    String hk = @PKG@.IslandStore.homeKey(u);
    @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
    if (s == null || s.bad || s.world == null || fileHas(hk, "isles", "3")) return false;
    Object o = ST.get(s.world);
    if (!(o instanceof @PKG@.IsleState) || ((@PKG@.IsleState) o).three != 0) return false;
    return api().quest(u, "island:portal");
  } catch (Throwable t) { return false; }
}""")
# the repaired portal: to the hub (+ island:portal for SkyyQuests); at most once per 4 s per player
M(ilif, r"""
public static int usePad(String wn, java.util.UUID u, long now) {
  String owner = @PKG@.IslandStore.ownerOf(wn);
  if (owner == null || u == null || !portalOn(owner, state(wn))) return 0;
  if (!gate(u, now, 4000L)) return 0;
  @PKG@.IsleApi a = api();
  a.quest(u, "island:portal");
  if (!a.toHub(wn, u)) return 0;
  TRIPS.incrementAndGet();
  return 1;
}""")
M(ilif, r"""
public static int repair(String wn, String owner, @PKG@.IsleState st, java.util.UUID u, long now) {
  @PKG@.IsleApi a = api();
  st.portal = true;
  st.blocksAt = now;
  int n = a.setBlock(wn, SOCKETP[0], SOCKETP[1], SOCKETP[2], PAD) ? 1 : 0;
  for (int i = 0; i + 2 < FIX.length; i += 3) {
    String b = a.block(wn, FIX[i], FIX[i + 1], FIX[i + 2]);
    if (b != null && b.length() == 0 && a.setBlock(wn, FIX[i], FIX[i + 1], FIX[i + 2], FIX_IDS[i / 3])) n++;
  }
  String who = a.name(u);
  saveProps(owner, new String[] { "portal", "portal.at", "portal.by" }, new String[] { "1", String.valueOf(now), who });
  REPAIRS.incrementAndGet();
  a.quest(u, "island:portal");
  a.relight(wn);
  Object[] rows = a.players(wn);
  for (int i = 0; i < rows.length; i++) a.say((java.util.UUID) ((Object[]) rows[i])[0], "[Island] " + who + " repaired the hub portal! Step into it to travel to the hub.", "#8fe39a");
  return n;
}""")
# F on the broken socket: island members (co-op or higher) or a server admin, one Hub Shard from the bags (counted) -> repair
M(ilif, r"""
public static String useSocket(String wn, java.util.UUID u, long now) {
  String owner = @PKG@.IslandStore.ownerOf(wn);
  if (owner == null || u == null) return "none";
  @PKG@.IsleState st = state(wn);
  if (portalOn(owner, st)) return usePad(wn, u, now) > 0 ? "trip" : "wait";
  if (!gate(u, now, 1000L)) return "wait";
  @PKG@.IsleApi a = api();
  if (@PKG@.IslandPerms.rankU(owner, u) < 2 && !a.isAdmin(u)) { a.say(u, "[Island] Only this island's co-op members can repair its portal.", "#ff9d6b"); return "rank"; }
  if (a.count(wn, u, SHARD) < 1L) { a.say(u, REPAIR_TEXT, "#ffe08a"); return "need"; }
  if (busy(u)) { a.say(u, "[Island] Your profile is busy - try again in a moment.", "#ff9d6b"); return "busy"; }
  if (a.take(wn, u, SHARD, 1L) != 1L) { a.say(u, "[Island] Could not take the Hub Shard from your bags - try again.", "#ff9d6b"); return "fail"; }
  repair(wn, owner, st, u, now);
  return "repaired";
}""")
# standing in the repaired portal's opening = using it
M(ilif, r"""
public static int stepTick(String wn, String owner, @PKG@.IsleState st, Object[] rows, long now) {
  if (!portalOn(owner, st)) return 0;
  int n = 0;
  for (int i = 0; i < rows.length; i++) {
    Object[] r = (Object[]) rows[i];
    double x = ((Double) r[1]).doubleValue();
    double y = ((Double) r[2]).doubleValue();
    double z = ((Double) r[3]).doubleValue();
    if (x >= PAD_BOX[0] && x <= PAD_BOX[3] && y >= PAD_BOX[1] && y <= PAD_BOX[4] && z >= PAD_BOX[2] && z <= PAD_BOX[5]) n += usePad(wn, (java.util.UUID) r[0], now);
  }
  return n;
}""")
# hubshards.properties: profile key -> time of the first Hub Shard (load at start; saved on SkyyIslands-IO after each first shard)
M(ilif, r"""
public static int loadGot(java.nio.file.Path f) {
  GOT_FILE = f;
  GOT.clear();
  if (f == null) return 0;
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return 0;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      long v = 0L;
      try { v = Long.parseLong(p.getProperty(k).trim()); } catch (Throwable t) { v = 0L; }
      GOT.put(k, Long.valueOf(v));
    }
  } catch (Throwable t) {
    String kept = "";
    try {   // fix (e): keep the unreadable file (the next save would replace it) for an admin to look at
      java.nio.file.Files.copy(f, f.resolveSibling(f.getFileName().toString() + ".bad"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      kept = " - the file is kept as hubshards.properties.bad";
    } catch (Throwable t2) { kept = " - could not keep a copy: " + t2; }
    @PKG@.IslandStore.warn("could not read hubshards.properties (first Hub Shards are counted again from now on): " + t + kept);
  }
  return GOT.size();
}""")
M(ilif, r"""
public static String saveGot0() {
  java.nio.file.Path f = GOT_FILE;
  if (f == null) return "no file";
  try {
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = GOT.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      p.setProperty(String.valueOf(e.getKey()), String.valueOf(e.getValue()));
    }
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyIslands: profile keys that got their first Hub Shard (time)"); } finally { out.close(); }
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    return null;
  } catch (Throwable t) { return String.valueOf(t); }
}""")
M(ilif, r"""
public static void saveGotNow() {
  String e = null;
  synchronized (GOT_LOCK) { e = saveGot0(); }
  if (e != null) @PKG@.IslandStore.warn("could not save hubshards.properties: " + e + " - kept in memory, saved again with the next Hub Shard");
}""")
M(ilif, "public static void saveGot() { api().save(new @PKG@.IsleTask(7, null, null)); }")
# fix (b): after the first one, one more Hub Shard for a co-op member (or higher) of THIS island while its portal is still broken and
# they hold none (a lost / sold / reset-away shard never locks a profile out; nobody else gets more)
M(ilif, r"""
public static boolean again(String wn, java.util.UUID u) {
  String owner = @PKG@.IslandStore.ownerOf(wn);
  if (owner == null || u == null || portalOn(owner, state(wn))) return false;
  if (@PKG@.IslandPerms.rankU(owner, u) < 2) return false;
  return api().count(wn, u, SHARD) < 1L;
}""")
# one Hub Shard for this player's profile key (the first one, or one more by again()): given (counted) or owed (bags full or the profile
# busy - PENDING, retried every second on an island)
M(ilif, r"""
public static boolean grant(String wn, java.util.UUID u, String pk, long now) {
  boolean first = !GOT.containsKey(pk);
  if (!first && !again(wn, u)) { PENDING.remove(u); return false; }
  @PKG@.IsleApi a = api();
  if (busy(u)) { PENDING.put(u, pk); return false; }   // fix (d): retried once SkyyProfiles is done
  if (a.give(wn, u, SHARD, 1L) >= 1L) {
    if (first) GOT.put(pk, Long.valueOf(now));
    PENDING.remove(u);
    GIVEN.incrementAndGet();
    if (first) saveGot();
    a.say(u, "[Island] You got a Hub Shard! Use it on the broken portal on island 3's summit to repair it.", "#8fe39a");
    return true;
  }
  if (PENDING.put(u, pk) == null) a.say(u, "[Island] Your bags are full - make room and your Hub Shard arrives.", "#ff9d6b");
  return false;
}""")
M(ilif, r"""
public static int pendingTick(String wn, Object[] rows, long now) {
  if (PENDING.isEmpty()) return 0;
  int n = 0;
  for (int i = 0; i < rows.length; i++) {
    java.util.UUID u = (java.util.UUID) ((Object[]) rows[i])[0];
    Object pk = PENDING.get(u);
    if (!(pk instanceof String) || !pk.equals(@PKG@.IslandStore.pkey(u))) continue;
    if (grant(wn, u, (String) pk, now)) n++;
  }
  return n;
}""")
# a Shardkeeper died to a player (IsleTask mode 1, world thread): the killer + island members within LOOT_R of the arena, first time per profile
M(ilif, r"""
public static int bossLoot(String wn, java.util.UUID killer, long now) {
  String owner = @PKG@.IslandStore.ownerOf(wn);
  Object[] rows = api().players(wn);
  int n = 0;
  for (int i = 0; i < rows.length; i++) {
    Object[] r = (Object[]) rows[i];
    java.util.UUID u = (java.util.UUID) r[0];
    if (!u.equals(killer)) {
      if (owner == null || @PKG@.IslandPerms.rankU(owner, u) < 1) continue;
      if (d2(((Double) r[1]).doubleValue(), ((Double) r[3]).doubleValue(), BOSS[0], BOSS[2]) > LOOT_R * LOOT_R) continue;
    }
    String pk = @PKG@.IslandStore.pkey(u);
    if (GOT.containsKey(pk) && !again(wn, u)) continue;
    if (grant(wn, u, pk, now)) n++;
  }
  return n;
}""")
# IsleDeath (world thread, inside the death system: memory only + a queued task): 1 = a camp mob, 2 = the mini boss, 0 = neither
M(ilif, r"""
public static int onDeath(String wn, String role, String uuid, java.util.UUID killer, double x, double z, long now) {
  Object o = ST.get(wn);
  if (!(o instanceof @PKG@.IsleState) || role == null) return 0;
  @PKG@.IsleState st = (@PKG@.IsleState) o;
  if (st.three != 1) return 0;
  boolean tracked = uuid != null && st.camp.contains(uuid);
  if (inList(roles(@PKG@.IslandCfg.CAMP_ROLES), role) && (tracked || d2(x, z, CAMP[0], CAMP[2]) <= CAMP_R * CAMP_R)) {
    if (uuid != null) st.camp.remove(uuid);
    st.due.add(Long.valueOf(now + (long) @PKG@.IslandCfg.CAMP_RESPAWN * 1000L));   // fix (g): this death's own respawn time
    while (st.due.size() > 40) st.due.remove(0);
    return 1;
  }
  boolean boss = uuid != null && uuid.equals(st.boss);
  if (role.equals(@PKG@.IslandCfg.BOSS_ROLE) && (boss || d2(x, z, BOSS[0], BOSS[2]) <= BOSS_R * BOSS_R)) {
    st.boss = null;
    st.bossNext = now + (killer != null ? (long) @PKG@.IslandCfg.BOSS_COOLDOWN * 1000L : 30000L);
    if (killer != null) api().exec(wn, new @PKG@.IsleTask(1, wn, killer));
    return 2;
  }
  return 0;
}""")
# respawn routing (pure): 0 = leave it to the engine, 1 = to the player's island, 2 = to the hub
M(ilif, r"""
public static int route(String dw, String home, boolean bedHere, String hub, boolean on) {
  if (!on || dw == null) return 0;
  if (home != null) {
    if (home.equals(dw) || bedHere) return 0;
    return 1;
  }
  if (bedHere || (hub != null && hub.equals(dw))) return 0;
  return 2;
}""")
M(ilif, r"""
public static boolean present(Object[] rows, java.util.UUID u) {
  for (int i = 0; i < rows.length; i++) if (u.equals(((Object[]) rows[i])[0])) return true;
  return false;
}""")
# IsleTask mode 4 (the death world's thread, 0.8 s after the respawn): -1 = not in that world any more, else route()'s answer when done
M(ilif, r"""
public static int respawn(String wn, java.util.UUID u) {
  if (!@PKG@.IslandCfg.RESPAWN_HOME || wn == null || u == null) return 0;
  @PKG@.IsleApi a = api();
  if (!present(a.players(wn), u)) return -1;
  if (keepWorld(wn)) return 0;                // fix (h): that world keeps its own respawn (shards, zones)
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s == null || s.bad) return 0;
  int r = route(wn, s.world, a.hasBed(u, wn), a.hubWorld(), true);
  if (r == 1) {
    if (a.goHome(wn, u, hk, s.world) <= 0) return 0;
    ROUTED.incrementAndGet();
    return 1;
  }
  if (r == 2) {
    if (!a.toHub(wn, u)) return 0;
    ROUTED.incrementAndGet();
    return 2;
  }
  return 0;
}""")
M(ilif, r"""
public static void respawnLater(String wn, java.util.UUID u) {
  if (!@PKG@.IslandCfg.RESPAWN_HOME || wn == null || u == null) return;
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.IsleTask(5, wn, u), 800L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { warnOnce("respawn", "could not schedule the respawn routing: " + t); }
}""")
# one island world (IsleTask mode 0, its world thread): the portal blocks, the pad, owed shards, the camp, the mini boss
M(ilif, r"""
public static int tickWorld(String wn) {
  try {
    if (wn == null || !@PKG@.IslandStore.isIslandWorld(wn) || @PKG@.IslandStore.isRetired(wn)) return 0;
    String owner = @PKG@.IslandStore.ownerOf(wn);
    if (owner == null) return 0;
    @PKG@.IsleApi a = api();
    long now = a.now();
    @PKG@.IsleState st = state(wn);
    if (!three(wn, st, owner, now)) return 0;
    Object[] rows = a.players(wn);
    if (rows.length == 0) return 0;
    int n = portalBlocks(wn, st, owner, now);
    n += stepTick(wn, owner, st, rows, now);
    n += pendingTick(wn, rows, now);
    java.util.ArrayList mem = members(owner, rows);
    if (mem.size() > 0) {
      n += campTick(wn, st, mem, now);
      n += bossTick(wn, st, mem, now);
    }
    return n;
  } catch (Throwable t) { warnOnce("tick", "the island tick failed (logged once): " + t); return 0; }
}""")
# the 1 s ticker (scheduler thread): one IsleTask per island world with players, never two queued for one world (10 s grace)
M(ilif, r"""
public static int tickAll() {
  @PKG@.IsleApi a = api();
  long now = a.now();
  java.util.Iterator it = a.islandWorlds().iterator();
  int n = 0;
  while (it.hasNext()) {
    String wn = (String) it.next();
    Object q = QUEUED.get(wn);
    if (q instanceof Long && now - ((Long) q).longValue() < 10000L) continue;
    QUEUED.put(wn, Long.valueOf(now));
    if (a.exec(wn, new @PKG@.IsleTask(0, wn, null))) n++; else QUEUED.remove(wn);
  }
  return n;
}""")
M(itsk, r"""
public void run() {
  try {
    if (this.mode == 9) { @PKG@.IsleLife.tickAll(); return; }
    if (this.mode == 0) { @PKG@.IsleLife.tickWorld(this.wn); @PKG@.IsleLife.QUEUED.remove(this.wn); return; }
    long now = @PKG@.IsleLife.api().now();
    if (this.mode == 1) { @PKG@.IsleLife.bossLoot(this.wn, this.u, now); return; }
    if (this.mode == 2) { @PKG@.IsleLife.useSocket(this.wn, this.u, now); return; }
    if (this.mode == 3) { @PKG@.IsleLife.usePad(this.wn, this.u, now); return; }
    if (this.mode == 4) { @PKG@.IsleLife.respawn(this.wn, this.u); return; }
    if (this.mode == 5) { @PKG@.IsleLife.api().exec(this.wn, new @PKG@.IsleTask(4, this.wn, this.u)); return; }
    if (this.mode == 6) { if (!@PKG@.IslandStore.setProps(this.a, this.ks, this.vs)) @PKG@.IslandStore.warn("could not write " + java.util.Arrays.toString(this.ks) + " to island file " + this.a + " (kept in memory; the pad check writes portal=1 again)"); return; }
    if (this.mode == 7) { @PKG@.IsleLife.saveGotNow(); return; }
  } catch (Throwable t) { @PKG@.IsleLife.warnOnce("task" + this.mode, "island part-2 task " + this.mode + " failed (logged once): " + t); }
}""")

# ---------------------------------------------------------------------------------------------------------------- the ECS hooks
C(iuse, "public IsleUse() { super(@UBPRE@.class); }")
M(iuse, "public @QRY@ getQuery() { return @ARCH@.empty(); }")
M(iuse, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @UBE@)) return;
    @UBE@ e = (@UBE@) ev;
    if (e.getInteractionType() != @ITY@.Use) return;
    @BTY@ bt = e.getBlockType();
    String id = bt == null ? "" : String.valueOf(bt.getId());
    int mode = @PKG@.IsleLife.SOCKET.equals(id) ? 2 : (@PKG@.IsleLife.PAD.equals(id) ? 3 : 0);
    if (mode == 0) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null || !@PKG@.IslandStore.isIslandWorld(w.getName())) return;
    @REF@ r = chunk.getReferenceTo(idx);
    @PR@ pr = r == null ? null : (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.IsleLife.api().exec(w.getName(), new @PKG@.IsleTask(mode, w.getName(), pr.getUuid()));
  } catch (Throwable t) { @PKG@.IsleLife.warnOnce("use", "the portal use hook failed (logged once): " + t); }
}""")
C(idth, "public IsleDeath() { super(); }")
M(idth, "public @QRY@ getQuery() { return @ARCH@.empty(); }")
M(idth, r"""
public void onComponentAdded(@REF@ r, @CMP@ c, @ST@ s, @CB@ b) {
  try {
    if (r == null || !(c instanceof @DTH@)) return;
    Object ext = s.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null || !@PKG@.IslandStore.isIslandWorld(w.getName())) return;
    @NPC@ npc = (@NPC@) s.getComponent(r, @NPC@.getComponentType());
    if (npc == null) return;
    @UUC@ uc = (@UUC@) s.getComponent(r, @UUC@.getComponentType());
    @TC@ tc = (@TC@) s.getComponent(r, @TC@.getComponentType());
    double x = 0.0;
    double z = 0.0;
    if (tc != null && tc.getPosition() != null) { x = tc.getPosition().x; z = tc.getPosition().z; }
    java.util.UUID killer = null;
    @DMG@ d = ((@DTH@) c).getDeathInfo();
    Object src = d == null ? null : d.getSource();
    if (src instanceof @DENT@) {
      @REF@ k = ((@DENT@) src).getRef();
      if (k != null && k.isValid() && k.getStore() == s) {
        @PR@ pr = (@PR@) s.getComponent(k, @PR@.getComponentType());
        if (pr != null) killer = pr.getUuid();
        else {      // fix (f): a pet / summon's killing blow counts for its owner
          @UUC@ ku = (@UUC@) s.getComponent(k, @UUC@.getComponentType());
          if (ku != null) killer = @PKG@.IsleLife.petOwner(ku.getUuid());
        }
      }
    }
    @PKG@.IsleLife.onDeath(w.getName(), npc.getRoleName(), uc == null || uc.getUuid() == null ? null : uc.getUuid().toString(), killer, x, z, @PKG@.IsleLife.api().now());
  } catch (Throwable t) { @PKG@.IsleLife.warnOnce("death", "the camp / boss death hook failed (logged once): " + t); }
}""")
C(irsp, "public IsleRespawn() { super(); }")
M(irsp, "public @QRY@ getQuery() { return @PLA@.getComponentType(); }")
M(irsp, r"""
public void onComponentRemoved(@REF@ r, @CMP@ c, @ST@ s, @CB@ b) {
  try {
    if (r == null || !(c instanceof @DTH@) || !@PKG@.IslandCfg.RESPAWN_HOME) return;
    Object ext = s.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    @PR@ pr = (@PR@) s.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.IsleLife.respawnLater(w.getName(), pr.getUuid());
  } catch (Throwable t) { @PKG@.IsleLife.warnOnce("respawn", "the respawn hook failed (logged once): " + t); }
}""")
F(pl, "public java.util.concurrent.ScheduledFuture isleTicker;")
'''
rep('''# ================= plugin =================
''', P2 + '''
# ================= plugin =================
''')

# ================================================================================================ setup / shutdown / ready line
rep('''  b.put("island:fn:place", new @PKG@.PlaceFn());         // 0.5.10: the 3 starter islands' named places (SkyyQuests)
''', '''  b.put("island:fn:place", new @PKG@.PlaceFn());         // 0.5.10: the 3 starter islands' named places (SkyyQuests)
  // 0.5.12: quest:caller:islands (SkyyQuests tutorial task 21 goes live) is put by StarterIsles.publish below (3 islands + mini boss on)
  @PKG@.IsleLife.loadGot(base.resolve("hubshards.properties"));   // 0.5.12: who already got their first Hub Shard (profile keys)
''')
rep('''  getEntityStoreRegistry().registerSystem(new @PKG@.GuardHurt());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SeenTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
''', '''  getEntityStoreRegistry().registerSystem(new @PKG@.GuardHurt());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SeenTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  // 0.5.12 starter islands part 2: the portal socket / pad, camp + boss deaths, respawns, and the 1 s island tick
  int p2 = 0;
  try { getEntityStoreRegistry().registerSystem(new @PKG@.IsleUse()); p2++; } catch (Throwable t) { @PKG@.IslandStore.warn("the portal use hook could not be registered: " + t); }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.IsleDeath()); p2++; } catch (Throwable t) { @PKG@.IslandStore.warn("the camp / boss death hook could not be registered: " + t); }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.IsleRespawn()); p2++; } catch (Throwable t) { @PKG@.IslandStore.warn("the respawn hook could not be registered: " + t); }
  @PKG@.IsleLife.HOOKS = p2;
  this.isleTicker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.IsleTask(9, null, null), 3L, 1L, java.util.concurrent.TimeUnit.SECONDS);
''')
rep('''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
''', '''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { if (this.isleTicker != null) this.isleTicker.cancel(false); } catch (Throwable t) { }   // 0.5.12
''')
rep('''    b.remove("island:fn:place"); b.remove("island:places");   // 0.5.10
''', '''    b.remove("island:fn:place"); b.remove("island:places");   // 0.5.10
    b.remove("quest:caller:islands");                          // 0.5.12
''')
rep('''"; new islands: " + (@PKG@.StarterIsles.three() ? "3 starter islands (" + @PKG@.StarterIsles.BLOCKS + " blocks)" : "classic island"));''',
    '''"; new islands: " + (@PKG@.StarterIsles.three() ? "3 starter islands (" + @PKG@.StarterIsles.BLOCKS + " blocks)" : "classic island") + "; part 2 (3-island islands): camp " + (@PKG@.IslandCfg.CAMP_ON ? @PKG@.IslandCfg.CAMP_COUNT + " x " + @PKG@.IslandCfg.CAMP_ROLES : "off") + ", mini boss " + (@PKG@.IslandCfg.BOSS_ON ? @PKG@.IslandCfg.BOSS_NAME + " (" + @PKG@.IslandCfg.BOSS_ROLE + ")" : "off") + ", Hub Shard portal, respawn on your island " + (@PKG@.IslandCfg.RESPAWN_HOME ? "on" : "off") + ", hooks " + @PKG@.IsleLife.HOOKS + "/3, " + @PKG@.IsleLife.GOT.size() + " Hub Shards given");''')

# ================================================================================================ jar files: the Hub Shard + the 2 blocks
rep('''    "Server/Instances/SkyyIsland/resources/InstanceData.json": '{\\n  "HadPlayer": false\\n}\\n',
}
''', '''    "Server/Instances/SkyyIsland/resources/InstanceData.json": '{\\n  "HadPlayer": false\\n}\\n',
}
files.update(P2_FILES)   # 0.5.12: Skyy_Hub_Shard, Skyy_Island_Portal_Socket, Skyy_Island_Hub_Portal + their names (server.lang)
''')
rep('''B.assemble(jar, m, OUT, extra_files=files)
''', '''B.assemble(jar, m, OUT, extra_files=files)
with zipfile.ZipFile(jar, "a") as _jz:                    # 0.5.12: the Hub Shard icon (our own art, research/cloud/icons-1013)
    _jz.writestr("Common/" + P2_ICON_PATH, P2_ICON)
''')

# ================================================================================================ fix round (critics isle2)
# (a) /island reset: the reset island's portal is broken again and it is probed again (portal / portal.at / portal.by / isles go with kit)
rep('''    p.remove("kit");
    reset = true;
''', '''    p.remove("kit");
    p.remove("portal"); p.remove("portal.at"); p.remove("portal.by"); p.remove("isles");   // 0.5.12: a reset island has a broken portal again
    reset = true;
''')
# (i) quest:caller:islands only while new islands get 3 islands AND the mini boss is on (it drops the Hub Shard the portal needs)
rep('''    if (three()) b.put("island:places", PLACES); else b.remove("island:places");
''', '''    if (three()) b.put("island:places", PLACES); else b.remove("island:places");
    if (three() && @PKG@.IslandCfg.BOSS_ON) b.put("quest:caller:islands", Boolean.TRUE); else b.remove("quest:caller:islands");   // 0.5.12
''')
# (i) /hub calls IsleLife.classicTrip -> its execute is compiled after IsleLife (methods before callers): moved into the part-2 block
HUB_OLD = 'M(hcmd, r"""\nprotected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {\n  try {\n    pr.sendMessage(@MSG@.raw("[Island] Warping to the hub..."));\n    if (!sendToHub(store, ref, pr, world)) pr.sendMessage(@MSG@.raw("[Island] No hub is set and no default world spawn was found. An admin can stand somewhere and run /sethub."));\n    else if (world == null || @PKG@.IslandStore.HUB_WORLD == null || !@PKG@.IslandStore.HUB_WORLD.equals(world.getName())) @PKG@.IslandSnd.arm(pr.getUuid());   // 0.5.9: the portal sound on arrival (not for a hop inside the hub world: no world change = no ready)\n  } catch (Throwable t) {\n    @PKG@.IslandStore.warn("/hub failed: " + t);\n    pr.sendMessage(@MSG@.raw("[Island] Could not warp: " + t.getMessage()));\n  }\n}""")\n'
HUB_NEW = 'M(hcmd, r"""\nprotected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {\n  try {\n    pr.sendMessage(@MSG@.raw("[Island] Warping to the hub..."));\n    boolean sent = sendToHub(store, ref, pr, world);\n    if (sent) @PKG@.IsleLife.classicTrip(pr.getUuid());   // 0.5.12 fix (i): a classic home island has no portal - /hub is the tutorial\'s portal step\n    if (!sent) pr.sendMessage(@MSG@.raw("[Island] No hub is set and no default world spawn was found. An admin can stand somewhere and run /sethub."));\n    else if (world == null || @PKG@.IslandStore.HUB_WORLD == null || !@PKG@.IslandStore.HUB_WORLD.equals(world.getName())) @PKG@.IslandSnd.arm(pr.getUuid());   // 0.5.9: the portal sound on arrival (not for a hop inside the hub world: no world change = no ready)\n  } catch (Throwable t) {\n    @PKG@.IslandStore.warn("/hub failed: " + t);\n    pr.sendMessage(@MSG@.raw("[Island] Could not warp: " + t.getMessage()));\n  }\n}""")\n'
rep(HUB_OLD, '''# 0.5.12: HubCmd.execute is compiled below IsleLife (it calls IsleLife.classicTrip) - see the part-2 block
''')
rep('''F(pl, "public java.util.concurrent.ScheduledFuture isleTicker;")
''', '''F(pl, "public java.util.concurrent.ScheduledFuture isleTicker;")
# 0.5.12 fix (i): /hub (moved here from the /hub section: it calls IsleLife.classicTrip)
''' + HUB_NEW)

# ================================================================================================ checks on the result
assert s.count("registerSystem(") == REG0 + 3 and s.count("registerCommand(") == CMD0
_i = s.index
assert _i("def s3_part2(") < _i("S3_P2 = s3_part2(") < _i('if os.environ.get("S3_ONLY") == "1":')
assert _i("P2_ROWS = [(") < _i("] + P2_ROWS")
assert _i('iapi = pool.makeInterface(PKG + ".IsleApi")') < _i("public abstract long now();") < _i("public static int tickWorld(") < _i("# ================= plugin =================")
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.5.11 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.5.11 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
