"""Derive SkyyIslands/build_skyyislands_0.5.10.py from the LIVE 0.5.9 (build_skyyislands_0.5.9.py = the tools/deploy_set.py SET pin, made by
tools/islands_0_5_9_patch.py - never edit a generated script, edit this patch). Every anchor is asserted; at the end every change is undone
on a copy and compared with 0.5.9 (nothing else changed). Line endings kept.
    python tools/islands_0_5_10_patch.py   then   python SkyyIslands/build_skyyislands_0.5.10.py   then   python SkyyIslands/test_skyyislands_0.5.10.py
(never --deploy: tools/deploy_set.py deploys the whole set).

0.5.10 (2026-10-14) = THE 3 STARTER ISLANDS (Skyy 2026-10-12 STARTER ISLANDS, docs/answered/social.md: "fixed design, but everything there is
breakable. so it guides you through the start, but wont restrict you. i want the 3 islands to be big enough to break some bushes, grab
some rubble, make crude tools, mine for some blocks, and get to the next island. (old broken structures on the islands.) but still small
islands, maybe 4x-5x the starter one we have no"; 2026-10-14 popup "Start now"). research/SkyyQuests-Tutorial-Spec.md 3.3.
  1. EVERY NEW ISLAND (and every /island reset) gets 3 hand-designed starter islands - the same for everyone - instead of the one 12 x 12
     island: island 1 (home, 618 columns = 4.4x the classic island's 140), island 2 (combat, 578 = 4.1x), island 3 (mini boss, 620 =
     4.4x; fix round: radius 13 -> 14, it was 3.9x), in a line east / south-east of the spawn, about 9 and 10 blocks of open sky
     apart (along each bridge line 8 sky cells; the broken plank stubs on both sides leave 3 and 5 blocks to bridge with blocks you
     gather). About 12,700 vanilla blocks:
       island 1: grass / dirt / stone, 3 oaks (15 logs), 13 bushes (fibre + sticks), 6 stick piles, 10 loose rubble, grass tufts, a
                 tilled starter plot with 9 freshly planted wheat crops (vanilla Plant_Crop_Wheat_Block: they grow into the ripe wheat of
                 tutorial task 7 and drop wheat seeds when broken - the kit has no seeds; 3 tilled cells left free for replanting), a
                 rocky outcrop with a short cave tunnel showing 8 copper ore, an old broken stone-brick wall + 2 broken pillars, the
                 starter chest at 4,129,4 (the starter kit, unchanged) and the spawn point at 8.5,129,8.5 (unchanged).
                 "make crude tools" (Skyy 2026-10-12): with SkyyGear 0.3.5's lifelong tools (lifelong.noCraft default true) tools are
                 NOT crafted - a new player gets their ONE Crude set through SkyyGear (/pickaxe /hatchet /hoe /sickle;
                 research/Gathering-Shards-Spec.md 3.1). The gatherables are for the workbench, bridging, building (and the vanilla crude
                 recipes only where a server switches lifelong.noCraft off)
       island 2: the ruined camp (a broken ring wall, a cold campfire, bones, broken pots), a stone knoll with 4 copper + 2 iron ore, 2
                 oaks, bushes / sticks / rubble
       island 3: a ring of 6 broken pillars (the mini boss arena), the old broken portal frame on the summit plateau, copper + iron on
                 the summit's faces, bushes / sticks / rubble
     NOTHING IS PROTECTED: every block is an ordinary vanilla block with its normal drops (no Unbreakable gather type - build-checked
     against Assets.zip); the island's own permission grid applies exactly as on the classic island.
     DESIGNS AS DATA: the layout is generated HERE at build time from vanilla block ids (s3_layout() below; no prefab file is read or
     copied) and shipped as one run-length String in the new class StarterIsles; FillTask places it with the same BlockOperations.setBlock
     call as the classic island, sorted bottom-up.
  2. ONLY NEW ISLANDS: FillTask still runs only from IslandBuild (island creation / reset) and still skips a world that already has its
     spawn block (8,128,8) - an existing island is never filled again. Nothing reads or rewrites existing islands or their files.
     FIX ROUND (critic): a 3-island fill that placed fewer than all blocks (a section did not load) asks the engine for the chunks
     again and fills ONCE more (FillTask.tries; only that retry passes the spawn-block guard; blocks already right count as placed);
     the starter kit + kit flag wait for that last pass. A second shortfall only warns (as before).
     FIX ROUND 2 (critics): (a) the retry pass never re-places a block that is already right (FillTask.has first) - the starter chest
     and anything in it stay as they are; (b) the 3-island kit goes in only when IslandStore.KITDONE does not have the owner yet
     (RelightTask's late kit, 4 s after the build, can land between the passes - no second kit, no wiped kit); (c) the fill runs in
     world-thread SLICES of at most ~15 ms (StarterIsles.SLICE_NS; the engine WARNs "Task took" past one tick step, 33 ms at 30 TPS -
     the single 12,700-block task took 125-200 ms), the next slice 20 ms later (FillTask.next: CompletableFuture.delayedExecutor ->
     FillTask.accept -> World.execute); FillTask.at = the next run, placed = blocks so far; then the grass tint one chunk per slice
     (FillTask.fin, StarterIsles.tintOne) and the kit in a slice of its own; only the first slice checks chunk (0,0) and the spawn block.
     The classic fill stays one task (0.5.9 unchanged). setup() initialises the engine's BitSetUtil class (its first use after a boot
     cost ~40 ms inside the first island fill's world-thread task - the one "Task took" WARN every first island has logged since 0.5.6).
     ChunkFill.load asks the engine for the 8 chunks / 16 sections the 3 islands touch (the classic 1 chunk + 2 sections otherwise);
     the grass tint goes to those 8 chunks; RelightNow relights cx -1..2 x cz -1..1 (12 columns, "n/12 chunks") while the design is the
     3 islands (the classic 3 x 3, "n/9", otherwise).
  3. SERVER SETUP -> Islands -> Starter kit -> "Starter islands" (choice, flag new): "3 starter islands" (default) | "Classic island" (the
     0.5.9 single island). config.properties starter.design=three|classic: a fresh file lists it, an existing file has no line = three (no
     migration, nothing rewritten). Islands already built never change either way.
  4. BRIDGE (for SkyyQuests 0.3.2 tutorial tasks 11 / 19 / 20 / 21 - the widget arrow + reach targets, spec 3.3): island:places (String,
     "id=island|x|y|z|label;..." - ids island1, cave, plot, island2, camp, island3, boss, portal; world "island" = any island world, every
     3-island island has the same design) - published while the design is "three", removed while it is "classic" and at shutdown; and
     island:fn:place (Function: String id, or Object[] {UUID, String id} -> "island|x|y|z|label" or null; the spec's shape).
  5. No saved-data change, no command change, no new permission. ROLLBACK to 0.5.9: safe (it ignores starter.design; islands already built
     stay as they are; new islands would be classic again).
LEFT OUT (later rounds, need Skyy's picks): the mini boss spawn + its Hub Shard drop, the working portal (island:portal event), the island 2
mob camp spawns (island worlds spawn no NPCs - Void world, IsSpawningNPC false), the Unclaimed Luggage chest (SkyyExploration).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.5.9.py")
dst = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.5.10.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.5.9"' in s and "GENERATED by tools/islands_0_5_9_patch.py" in s and "StarterIsles" not in s, "not the generated 0.5.9 script"
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.5.10 (2026-10-14)"):].rstrip() + "\n\n"

# ================================================================================================ docstring + version
rep('''"""SkyyIslands 0.5.9 - build script (javassist via jpype). GENERATED by tools/islands_0_5_9_patch.py from the LIVE 0.5.8 (itself
generated by tools/islands_0_5_8_patch.py from 0.5.7) - edit the patch, then regenerate; never edit this file by hand. Never run with
--deploy (tools/deploy_set.py deploys the coordinated set). Test: python SkyyIslands/test_skyyislands_0.5.9.py
''', '''"""SkyyIslands 0.5.10 - build script (javassist via jpype). GENERATED by tools/islands_0_5_10_patch.py from the LIVE 0.5.9 (itself
generated by tools/islands_0_5_9_patch.py from 0.5.8) - edit the patch, then regenerate; never edit this file by hand. Never run with
--deploy (tools/deploy_set.py deploys the coordinated set). Test: python SkyyIslands/test_skyyislands_0.5.10.py

''' + NOTE + '''0.5.9 (the base, still true unless 0.5.10 above says otherwise):
''')
rep('VERSION = "0.5.9"\n', 'VERSION = "0.5.10"\n')

# ================================================================================================ config text + field + load + row
rep('''    "sound.portal.id=SFX_Portal_Neutral_Teleport_Local",
    "",
])''', '''    "sound.portal.id=SFX_Portal_Neutral_Teleport_Local",
    "# 0.5.10 starter islands for NEW islands and resets: three (3 starter islands to bridge across) | classic (the old single island)",
    "starter.design=three",
    "",
])''')
rep('''          "public static volatile String SND_PORTAL_ID = \\"SFX_Portal_Neutral_Teleport_Local\\";"):
    F(cfg, f)''', '''          "public static volatile String SND_PORTAL_ID = \\"SFX_Portal_Neutral_Teleport_Local\\";",
          # 0.5.10: starter.design (three | classic) - read by ChunkFill.load for each NEW island / reset
          "public static volatile String STARTER_DESIGN = \\"three\\";"):
    F(cfg, f)''')
rep('''      SND_PORTAL_ID = p.getProperty("sound.portal.id", "SFX_Portal_Neutral_Teleport_Local").trim();
''', '''      SND_PORTAL_ID = p.getProperty("sound.portal.id", "SFX_Portal_Neutral_Teleport_Local").trim();
      String sd = p.getProperty("starter.design", "three").trim().toLowerCase();                   // 0.5.10 starter islands
      STARTER_DESIGN = sd.equals("classic") ? "classic" : "three";
''')
DESIGN_HELP = "New islands + resets: 3 islands to bridge across, or the old single island. Built ones never change."
assert len(DESIGN_HELP) <= 100, len(DESIGN_HELP)
rep('''     "action:IslandHooks.kitFromHotbar"),
''', '''     "action:IslandHooks.kitFromHotbar"),
    # 0.5.10: the 3 starter islands (Skyy 2026-10-12) or the classic single island - new islands and resets only
    ("starter.design", "Starter islands", "starter", "choice", "three", "", "", "three|3 starter islands,classic|Classic island", "", "new",
     "%s",
     "field:IslandCfg.STARTER_DESIGN@config.properties:starter.design;after=IslandHooks.afterDesign"),
''' % DESIGN_HELP)

# ================================================================================================ the classes
rep('''isnd = K("IslandSnd")        # 0.5.9: the sound helper (sound pass round 1): the portal sound on arrival
''', '''isnd = K("IslandSnd")        # 0.5.9: the sound helper (sound pass round 1): the portal sound on arrival
s3i  = K("StarterIsles")     # 0.5.10: the 3 starter islands (layout data, loads, fill, tint, places)
plfn = K("PlaceFn")          # 0.5.10: island:fn:place - a named place of the 3 starter islands
''')
rep('''       cfn, guard, g1, g2, g3, g4, g5, g6, g7, ghurt, page, rout, disp, rdy, seen, hooks, hht, kht, jnt, hsp, iio, rkf, wkf, hfn, isnd]''',
    '''       cfn, guard, g1, g2, g3, g4, g5, g6, g7, ghurt, page, rout, disp, rdy, seen, hooks, hht, kht, jnt, hsp, iio, rkf, wkf, hfn, isnd,
       s3i, plfn]''')

# ------------------------------------------------------------------------------------------------ the layout (Python, build time) + StarterIsles
S3 = r'''
# =====================================================================================================================
# 0.5.10 THE 3 STARTER ISLANDS (Skyy 2026-10-12): designs as DATA, generated here at build time from vanilla block ids (no prefab file is
# read or copied). s3_layout() -> (blocks {(x, y, z): id}, places {id: (x, y, z, label)}, tops {(x, z): grass y}, isle {(x, z): name}).
# The harness (SkyyIslands/test_skyyislands_0.5.10.py) imports this script's s3_layout through S3_ONLY=1 and compares it block for block
# with what the jar decodes and with a real island the real server built.
# =====================================================================================================================
import math as _s3m, random as _s3r
S3_GRASS, S3_DIRT, S3_STONE = "Soil_Grass", "Soil_Dirt", "Rock_Stone"
S3_ISLES = [  # (name, centre x, centre z, radius, grass height, deepest, wobble seed)
    ("island1", 8, 8, 14.0, 128, 9, 0.7),
    ("island2", 46, 14, 13.5, 127, 9, 2.3),
    ("island3", 75, 38, 14.0, 129, 10, 4.1),     # fix round (critic: 3.7-3.9x was under Skyy's "4x-5x"): radius 13 -> 14
]


def s3_hill(name, x, z):
    if name == "island1":   # a rocky outcrop with the copper cave (south-east of the spawn, +z = south; the same side as island 2)
        return max(0, int(round(4.4 - _s3m.hypot(x - 15, z - 16) / 1.6)))
    if name == "island2":   # a low stone knoll with ore on its faces
        return max(0, int(round(2.6 - _s3m.hypot(x - 39, z - 20) / 1.5)))
    return min(4, max(0, int(round(6.0 - _s3m.hypot(x - 79, z - 42) / 1.5))))   # island 3: the summit plateau (the portal frame)


def s3_layout():
    L, tops, isle, rocky = {}, {}, {}, set()
    for name, cx, cz, R, base, deep, sd in S3_ISLES:
        for x in range(int(cx - R - 3), int(cx + R + 4)):
            for z in range(int(cz - R - 3), int(cz + R + 4)):
                dx, dz = x - cx, z - cz
                d = _s3m.hypot(dx, dz)
                th = _s3m.atan2(dz, dx)
                rr = R + 1.6 * _s3m.sin(3 * th + sd) + 0.9 * _s3m.sin(5 * th + 2.1 * sd)
                if d > rr:
                    continue
                e = rr - d
                h = s3_hill(name, x, z)
                top = base + h
                depth = min(deep, 2 + int(e * 0.85)) + h
                tops[(x, z)] = top
                isle[(x, z)] = name
                if h > 0:
                    rocky.add((x, z))
                for y in range(top - depth, top + 1):
                    if y == top:
                        L[(x, y, z)] = S3_GRASS
                    elif h == 0 and y >= top - 2:
                        L[(x, y, z)] = S3_DIRT
                    else:
                        L[(x, y, z)] = S3_STONE
    used = set()

    def free(x, z, r=0):
        for a in range(x - r, x + r + 1):
            for b in range(z - r, z + r + 1):
                if (a, b) in used:
                    return False
        return (x, z) in tops

    def on(x, z, bid, dy=1):
        assert (x, z) in tops, (x, z, bid)
        L[(x, tops[(x, z)] + dy, z)] = bid
        used.add((x, z))

    def tree(x, z, hgt=5):
        assert free(x, z, 1), (x, z)
        t = tops[(x, z)]
        for y in range(t + 1, t + hgt + 1):
            L[(x, y, z)] = "Wood_Oak_Trunk"
        for a in range(x - 2, x + 3):
            for b in range(z - 2, z + 3):
                for y in range(t + hgt - 1, t + hgt + 2):
                    if a == x and b == z and y <= t + hgt:
                        continue
                    edge = abs(a - x) == 2 and abs(b - z) == 2
                    if edge or (y == t + hgt + 1 and (abs(a - x) == 2 or abs(b - z) == 2)):
                        continue
                    if (a, y, b) not in L:
                        L[(a, y, b)] = "Plant_Leaves_Oak"
        L[(x, t + hgt + 2, z)] = "Plant_Leaves_Oak"
        for a in range(x - 1, x + 2):
            for b in range(z - 1, z + 2):
                used.add((a, b))

    def wall(pts, hs, mats):
        for (x, z), hh in zip(pts, hs):
            if (x, z) not in tops or (x, z) in used:
                continue
            used.add((x, z))
            for k in range(hh):
                L[(x, tops[(x, z)] + 1 + k, z)] = mats[(x * 7 + z * 3 + k) % len(mats)]

    def pillar(x, z, hh, cap=None):
        assert free(x, z), (x, z)
        t = tops[(x, z)]
        L[(x, t + 1, z)] = "Rock_Stone_Brick_Pillar_Base"
        for k in range(2, hh + 1):
            L[(x, t + k, z)] = "Rock_Stone_Brick_Pillar_Middle"
        if cap:
            L[(x, t + hh + 1, z)] = cap
        used.add((x, z))

    RUIN = ["Rock_Stone_Brick", "Rock_Stone_Brick_Mossy", "Rock_Stone_Cobble_Mossy", "Rock_Stone_Brick", "Rock_Stone_Cobble"]
    # ---- the starter chest (FillTask.starterKit reads 4,129,4) and the spawn point (8.5, 129, 8.5) stay where the classic island has them
    assert tops.get((4, 4)) == 128 and tops.get((8, 8)) == 128, "island 1 must be flat at the chest and the spawn"
    L[(4, 129, 4)] = "Furniture_Crude_Chest_Small"
    for a in range(5, 12):
        for b in range(5, 12):
            used.add((a, b))
    used.add((4, 4))
    # ================= ISLAND 1 - home: trees, bushes, sticks, rubble, the copper cave, a farm plot, an old wall
    for x, z in ((0, 13), (13, 0), (-1, 3)):
        tree(x, z)
    for x in range(12, 19):       # the cave: a tunnel through the rocky outcrop, stone walls with copper ore showing
        for z in (15, 16):
            if (x, z) in tops and tops[(x, z)] >= 129:
                for y in (129, 130):
                    if y < tops[(x, z)]:
                        L.pop((x, y, z), None)
                L[(x, 128, z)] = S3_STONE
    for p in ((13, 129, 14), (14, 130, 17), (15, 129, 17), (16, 128, 15), (16, 130, 14), (17, 129, 14), (17, 129, 17), (18, 128, 16)):
        L[p] = "Ore_Copper_Stone"
    for x in range(12, 19):
        for z in (14, 15, 16, 17):
            used.add((x, z))
    for x in range(11, 14):       # the starter plot (tilled soil; fix round: 9 freshly planted wheat crops = the seed source of task 7)
        for z in range(2, 6):
            L[(x, 128, z)] = "Soil_Dirt_Tilled"
            if z <= 4:
                L[(x, 129, z)] = "Plant_Crop_Wheat_Block"
            used.add((x, z))
    wall([(-3, z) for z in range(5, 13)], [2, 3, 1, 0, 2, 3, 2, 1], RUIN)       # an old broken wall + 2 broken pillars
    wall([(x, 13) for x in range(-2, 3)], [3, 2, 2, 1, 0], RUIN)
    pillar(1, 17, 2, "Rock_Stone_Brick_Half")
    pillar(19, 8, 3)
    # ================= ISLAND 2 - combat: a ruined camp, an ore knoll, trees
    for x, z in ((53, 7), (42, 7)):
        tree(x, z)
    camp = (49, 16)
    ring = []
    for i in range(28):
        a = 2 * _s3m.pi * i / 28
        p = (int(round(camp[0] + 5 * _s3m.cos(a))), int(round(camp[1] + 5 * _s3m.sin(a))))
        if p not in ring:
            ring.append(p)
    hs = [2, 2, 1, 0, 0, 1, 2, 3, 2, 1, 1, 0, 2, 2, 3, 1, 0, 0, 1, 2, 2, 1, 2, 0, 1, 2, 3, 2, 1, 0]
    wall(ring, hs[:len(ring)], ["Rock_Stone_Cobble_Mossy", "Rock_Stone_Cobble", "Rock_Stone_Brick_Mossy"])
    on(camp[0], camp[1], "Deco_Campfire_Off")
    used.add((camp[0] + 1, camp[1]))                      # the camp place (next to the fire) stays clear
    for p in ((47, 14), (51, 18), (50, 13)):
        on(p[0], p[1], "Deco_Bone_Pile")
    for p in ((46, 18), (52, 15)):
        on(p[0], p[1], "Deco_Pot_Clay_Broken")
    for p in ((38, 19), (40, 21), (39, 22), (37, 20)):     # copper on the knoll's faces
        L[(p[0], tops[p], p[1])] = "Ore_Copper_Stone"
        used.add(p)
    for p in ((40, 19), (38, 21)):
        L[(p[0], tops[p], p[1])] = "Ore_Iron_Stone"
        used.add(p)
    # ================= ISLAND 3 - the mini boss: a ring of broken pillars, the old portal frame on the summit
    arena = (71, 34)
    for (dx, dz), hh in zip(((6, 0), (3, 5), (-3, 5), (-6, 0), (-3, -5), (3, -5)), (4, 2, 5, 1, 3, 2)):
        pillar(arena[0] + dx, arena[1] + dz, hh, "Rock_Stone_Brick_Half" if hh in (2, 4) else None)
    fx, fz0 = 81, 40
    fy = tops[(fx, fz0 + 2)] + 1
    for z in range(fz0, fz0 + 5):
        assert tops.get((fx, z)) == fy - 1, ("the portal frame needs the flat summit", z, tops.get((fx, z)))
        used.add((fx, z))
    for k in range(6):
        L[(fx, fy + k, fz0)] = "Rock_Stone_Brick"
    for k in range(4):
        L[(fx, fy + k, fz0 + 4)] = "Rock_Stone_Brick_Mossy"
    for z in range(fz0, fz0 + 3):
        L[(fx, fy + 5, z)] = "Rock_Stone_Brick_Decorative"
    L[(fx, fy, fz0 + 2)] = "Rock_Stone_Brick_Smooth"            # the empty socket for the Hub Shard (a later round)
    L[(fx, fy, fz0 + 1)] = "Rock_Stone_Brick_Half"
    for p in ((74, 45), (76, 47), (85, 39)):
        if p in rocky:
            L[(p[0], tops[p], p[1])] = "Ore_Copper_Stone"
            used.add(p)
    for p in ((83, 46), (77, 46)):
        if p in rocky:
            L[(p[0], tops[p], p[1])] = "Ore_Iron_Stone"
            used.add(p)

    def stub(a, b, n_from, n_to):      # ================= broken plank bridges pointing across each gap
        (ax, az), (bx, bz) = a, b
        ln = _s3m.hypot(bx - ax, bz - az)
        ux, uz = (bx - ax) / ln, (bz - az) / ln
        for c, u, n in ((a, (ux, uz), n_from), (b, (-ux, -uz), n_to)):
            k = 0
            while (int(round(c[0] + u[0] * k)), int(round(c[1] + u[1] * k))) in tops:
                k += 1
            edge_y = tops[(int(round(c[0] + u[0] * (k - 1))), int(round(c[1] + u[1] * (k - 1))))]
            for j in range(n):
                p = (int(round(c[0] + u[0] * (k + j))), int(round(c[1] + u[1] * (k + j))))
                if p not in tops:
                    L[(p[0], edge_y - (1 if j == n - 1 else 0), p[1])] = "Wood_Softwood_Planks"
    stub((8, 8), (46, 14), 3, 2)
    stub((46, 14), (75, 38), 2, 2)
    # ================= gatherables: bushes (fibre + sticks), sticks, loose rubble, grass - a fixed seed, never on paths / the hills
    rnd = _s3r.Random(20261012)
    want = {"island1": [("Plant_Bush", 8), ("Plant_Bush_Green", 5), ("Wood_Sticks", 6), ("Rubble_Stone", 7), ("Rubble_Stone_Mossy", 3),
                        ("Plant_Grass_Lush_Short", 22)],
            "island2": [("Plant_Bush", 4), ("Plant_Bush_Green", 2), ("Wood_Sticks", 4), ("Rubble_Stone", 5), ("Rubble_Stone_Mossy", 3),
                        ("Plant_Grass_Lush_Short", 16)],
            "island3": [("Plant_Bush", 3), ("Plant_Bush_Green", 1), ("Wood_Sticks", 3), ("Rubble_Stone", 5), ("Rubble_Stone_Mossy", 3),
                        ("Plant_Grass_Lush_Short", 12)]}
    cols = dict((n, sorted(p for p, v in isle.items() if v == n)) for n in want)
    for n in ("island1", "island2", "island3"):
        for bid, cnt in want[n]:
            got = 0
            while got < cnt:
                p = rnd.choice(cols[n])
                if not free(p[0], p[1], 0 if bid.startswith("Plant_Grass") else 1) or p in rocky:
                    continue
                if L.get((p[0], tops[p], p[1])) != S3_GRASS:
                    continue
                on(p[0], p[1], bid)
                got += 1
    # fix round (real-server H6): vanilla grass under a solid block turns to dirt on a random tick (seen under the camp's ring wall) -
    # the design puts dirt there from the start, so the island a player sees is the island the build made
    for (x, y, z), b in list(L.items()):
        if b == S3_GRASS and L.get((x, y + 1, z), "").startswith(("Rock_", "Ore_", "Wood_Oak_Trunk")):
            L[(x, y, z)] = S3_DIRT
    assert (8, 129, 8) not in L and (8, 130, 8) not in L, "the spawn point must stay clear"
    places = {
        "island1": (8.5, 129.0, 8.5, "Island 1"),
        "cave": (12.5, 129.0, 15.5, "The copper cave"),
        "plot": (12.5, 129.0, 5.5, "The starter plot"),     # fix round: the free row next to the planted wheat
        "island2": (46.5, float(tops[(46, 14)] + 1), 14.5, "Island 2"),
        "camp": (float(camp[0]) + 1.5, float(tops[(camp[0] + 1, camp[1])] + 1), float(camp[1]) + 0.5, "The old camp"),
        "island3": (75.5, float(tops[(75, 38)] + 1), 38.5, "Island 3"),
        "boss": (float(arena[0]) + 0.5, float(tops[arena] + 1), float(arena[1]) + 0.5, "The mini boss arena"),
        "portal": (float(fx) - 1.5, float(fy), float(fz0) + 2.5, "Hub portal"),
    }
    return L, places, tops, isle


S3_ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
S3_OFF = 64          # x and z are stored + 64 (two base-64 digits each), y as is


def s3_encode(L):
    """(palette, data, runs, chunks [(cx, cz)], sections [(cx, sy, cz)]): runs along +x of one id, sorted bottom-up (y, z, x); 8 chars a
    run = palette index, x + 64 (2), y (2), z + 64 (2), length (1, at most 63)"""
    pal = sorted(set(L.values()))
    assert len(pal) <= 64
    runs = []
    for k in sorted(L, key=lambda q: (q[1], q[2], q[0])):
        x, y, z = k
        b = L[k]
        r = runs[-1] if runs else None
        if r and r[1] == y and r[2] == z and r[3] == b and r[0] + r[4] == x and r[4] < 63:
            r[4] += 1
        else:
            runs.append([x, y, z, b, 1])

    def d2(v):
        assert 0 <= v < 4096, v
        return S3_ALPHA[v >> 6] + S3_ALPHA[v & 63]
    data = "".join(S3_ALPHA[pal.index(b)] + d2(x + S3_OFF) + d2(y) + d2(z + S3_OFF) + S3_ALPHA[n] for x, y, z, b, n in runs)
    chunks = sorted(set((x >> 5, z >> 5) for x, _y, z in L))
    secs = sorted(set((x >> 5, y >> 5, z >> 5) for x, y, z in L))
    return pal, data, len(runs), chunks, secs


def s3_decode(pal, data):
    out = {}
    for i in range(0, len(data), 8):
        v = [S3_ALPHA.index(c) for c in data[i:i + 8]]
        p, x, y, z, n = v[0], (v[1] << 6 | v[2]) - S3_OFF, v[3] << 6 | v[4], (v[5] << 6 | v[6]) - S3_OFF, v[7]
        for k in range(n):
            out[(x + k, y, z)] = pal[p]
    return out


S3_L, S3_PLACES, S3_TOPS, S3_ISLE = s3_layout()
S3_PAL, S3_DATA, S3_RUNS, S3_CHUNKS, S3_SECTS = s3_encode(S3_L)
assert s3_decode(S3_PAL, S3_DATA) == S3_L and len(S3_DATA) < 60000
assert all(-1 <= cx <= 2 and -1 <= cz <= 1 for cx, cz in S3_CHUNKS), S3_CHUNKS        # TintFix.fix (-2..2) and RelightNow (-1..2 x -1..1)
assert all(sy in (3, 4) for _cx, sy, _cz in S3_SECTS), S3_SECTS
S3_PLACES_TEXT = ";".join("%s=island|%s|%s|%s|%s" % (k, v[0], v[1], v[2], v[3]) for k, v in sorted(S3_PLACES.items()))
assert all(c not in S3_PLACES_TEXT for c in '"\\\\@') and all(";" not in v[3] and "|" not in v[3] and "=" not in v[3] for v in S3_PLACES.values())
'''
S3_CHECK = r'''
# build check: every block of the design is a vanilla BLOCK in Assets.zip (read only) that players can break (it or its Parent chain has
# BlockType.Gathering, no "Unbreakable" anywhere in that chain)
_S3Z = _zf.ZipFile(_SNDZ)
_S3N = dict((os.path.basename(n_)[:-5], n_) for n_ in _S3Z.namelist() if n_.startswith("Server/Item/Items/") and n_.endswith(".json"))
for _b in S3_PAL:
    _c, _g, _bt = _b, False, False
    while _c:
        assert _c in _S3N, "0.5.10: %s (starter islands) is not an item in Assets.zip" % _c
        _j = json.loads(_S3Z.read(_S3N[_c]))
        assert "Unbreakable" not in json.dumps(_j), "0.5.10: %s can not be broken" % _c
        _bt = _bt or "BlockType" in _j
        _g = _g or "Gathering" in _j.get("BlockType", {})
        _c = _j.get("Parent")
    assert _bt and _g, "0.5.10: %s is not a breakable block (BlockType %s, Gathering %s)" % (_b, _bt, _g)
'''
rep('''
# =====================================================================================================================
# 0.5.2 admin config kit (research/Server-Setup-Spec.md 4.17 + 5.5, tools/CONFIG-CONTRACT.md).''', S3_CHECK + '''
# =====================================================================================================================
# 0.5.2 admin config kit (research/Server-Setup-Spec.md 4.17 + 5.5, tools/CONFIG-CONTRACT.md).''')
# the layout itself sits right before the JVM starts, so S3_ONLY=1 can import it without a build
rep('''HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
''', '''HERE = os.path.dirname(os.path.abspath(__file__))
''' + S3 + '''if os.environ.get("S3_ONLY") == "1":          # 0.5.10: the harness reads the layout only (no JVM, no build)
    raise ImportError("S3_ONLY")
J = B.start()
''')

S3JAVA = r'''
# =====================================================================================================================
# 0.5.10 StarterIsles: the 3 starter islands' data (the run-length layout of s3_layout(), its palette, the chunks / sections it touches,
# the named places) + the code that loads, fills, tints and publishes them. three() = config starter.design is not "classic".
# =====================================================================================================================
F(s3i, 'public static final String ALPHA = "%s";' % S3_ALPHA)
F(s3i, "public static final String[] PAL = new String[] { %s };" % ", ".join('"%s"' % b for b in S3_PAL))
F(s3i, 'public static final String DATA = "%s";' % S3_DATA)
F(s3i, "public static final int RUNS = %d;" % S3_RUNS)
F(s3i, "public static final int BLOCKS = %d;" % len(S3_L))
F(s3i, "public static final int[] CHUNKS = new int[] { %s };" % ", ".join("%d, %d" % c for c in S3_CHUNKS))
F(s3i, "public static final int[] SECTS = new int[] { %s };" % ", ".join("%d, %d, %d" % c for c in S3_SECTS))
F(s3i, 'public static final String PLACES = "%s";' % S3_PLACES_TEXT)
F(s3i, "public static final int CX0 = %d;" % min(c[0] for c in S3_CHUNKS))
F(s3i, "public static final int CX1 = %d;" % max(c[0] for c in S3_CHUNKS))
F(s3i, "public static final int CZ0 = %d;" % min(c[1] for c in S3_CHUNKS))
F(s3i, "public static final int CZ1 = %d;" % max(c[1] for c in S3_CHUNKS))
M(s3i, r"""
public static boolean three() {
  String d = @PKG@.IslandCfg.STARTER_DESIGN;
  return d == null || !d.trim().equalsIgnoreCase("classic");
}""")
# the layout as int quintuples p, x, y, z, n (one per run, bottom-up) - decoded from DATA each fill (once per new island)
M(s3i, r"""
public static int[] decode() {
  int[] out = new int[RUNS * 5];
  for (int i = 0; i < RUNS; i++) {
    int o = i * 8;
    int[] v = new int[8];
    for (int k = 0; k < 8; k++) v[k] = ALPHA.indexOf(DATA.charAt(o + k));
    out[i * 5] = v[0];
    out[i * 5 + 1] = ((v[1] << 6) | v[2]) - 64;
    out[i * 5 + 2] = (v[3] << 6) | v[4];
    out[i * 5 + 3] = ((v[5] << 6) | v[6]) - 64;
    out[i * 5 + 4] = v[7];
  }
  return out;
}""")
# "island|x|y|z|label" of one named place, or null (an unknown id)
M(s3i, r"""
public static String placeOf(String id) {
  if (id == null) return null;
  String k = id.trim() + "=";
  String[] a = PLACES.split(";");
  for (int i = 0; i < a.length; i++) if (a[i].startsWith(k)) return a[i].substring(k.length());
  return null;
}""")
# island:places = every place while the design is the 3 islands (SkyyQuests' widget arrow + reach targets), removed for classic
M(s3i, r"""
public static void publish() {
  try {
    java.util.Map b = @PKG@.IslandStore.bridge();
    if (three()) b.put("island:places", PLACES); else b.remove("island:places");
  } catch (Throwable t) { @PKG@.IslandStore.warn("island:places publish failed: " + t); }
}""")
# ChunkFill.load (any thread): the chunks + sections of the 3 islands (8 + 16) through the ChunkStore (the engine queues the work)
M(s3i, r"""
public static java.util.concurrent.CompletableFuture[] loads(@CST@ cs) {
  int nc = CHUNKS.length / 2;
  int ns = SECTS.length / 3;
  java.util.concurrent.CompletableFuture[] parts = new java.util.concurrent.CompletableFuture[nc + ns];
  for (int i = 0; i < nc; i++) parts[i] = cs.getChunkReferenceAsync(@CHU@.indexChunk(CHUNKS[i * 2], CHUNKS[i * 2 + 1]));
  for (int i = 0; i < ns; i++) parts[nc + i] = cs.getChunkSectionReferenceAsync(SECTS[i * 3], SECTS[i * 3 + 1], SECTS[i * 3 + 2]);
  return parts;
}""")
# world thread: the grass tint of every chunk the 3 islands touch (+ tell the clients); returns the columns re-tinted
# fix round 2: one chunk per world-thread slice (FillTask.fin); tint() = all of them at once
M(s3i, r"""
public static int tintOne(@WLD@ w, int i) {
  long idx = @CHU@.indexChunk(CHUNKS[i * 2], CHUNKS[i * 2 + 1]);
  int n = @PKG@.TintFix.tintChunk(w, idx);
  if (n > 0) @PKG@.TintFix.resend(w, idx);
  return n;
}""")
M(s3i, r"""
public static int tint(@WLD@ w) {
  int cols = 0;
  for (int i = 0; i < CHUNKS.length / 2; i++) cols += tintOne(w, i);
  return cols;
}""")
'''
S3FILL = r'''
# 0.5.10 fix round 2 (world thread): the next slice of this fill ~20 ms later (delayedExecutor -> accept -> World.execute)
M(fill, r"""
public void next() {
  java.util.concurrent.CompletableFuture.completedFuture(world).whenCompleteAsync(this, java.util.concurrent.CompletableFuture.delayedExecutor(20L, java.util.concurrent.TimeUnit.MILLISECONDS));
}""")
# 0.5.10 fix round (world thread): is block id already at x,y,z? (the retry pass of a partly loaded fill counts it as placed)
M(fill, r"""
public boolean has(int x, int y, int z, String id) {
  try {
    int b = blockAt(world, x, y, z);
    return b > 0 && b == @BTY@.getAssetMap().getIndex(id);
  } catch (Throwable t) { return false; }
}""")
# 0.5.10 (world thread, FillTask.run): the blocks of the 3 islands through FillTask.put (BlockOperations.setBlock, as the classic island),
# bottom-up, from run t.at on for at most SLICE_NS (fix round 2: the engine WARNs a world task longer than one tick step); adds to
# t.placed (a block in a section that did not load = not placed); true = the last run is done. The retry pass (t.tries > 0) never
# re-places a block that is already right (fix round 2: the chest keeps its kit).
F(s3i, "public static final long SLICE_NS = 15000000L;")
M(s3i, r"""
public static boolean fill(@PKG@.FillTask t) {
  if (t.runs == null) t.runs = decode();
  int[] r = t.runs;
  long t0 = System.nanoTime();
  int i = t.at;
  while (i < RUNS) {
    String id = PAL[r[i * 5]];
    int x = r[i * 5 + 1]; int y = r[i * 5 + 2]; int z = r[i * 5 + 3]; int len = r[i * 5 + 4];
    for (int k = 0; k < len; k++) {
      if (t.tries > 0 && t.has(x + k, y, z, id)) t.placed = t.placed + 1;
      else t.placed = t.placed + t.put(x + k, y, z, id);
    }
    i = i + 1;
    if (System.nanoTime() - t0 >= SLICE_NS) break;
  }
  t.at = i;
  return i >= RUNS;
}""")
'''
rep('''
# =====================================================================================================================
# FillTask (world thread): the starter island in chunk (0,0) + starter kit (0.4.5, kit read through the CHUNK store)''', S3JAVA + '''
# =====================================================================================================================
# FillTask (world thread): the starter island in chunk (0,0) + starter kit (0.4.5, kit read through the CHUNK store)''')
rep('''F(fill, "public java.util.concurrent.CompletableFuture done;")
''', '''F(fill, "public java.util.concurrent.CompletableFuture done;")
F(fill, "public boolean three;")   # 0.5.10: set by ChunkFill.load = the design this new island gets (StarterIsles.three() at load time)
F(fill, "public int tries;")       # 0.5.10 fix round: 1 = this run is the one retry after a partly loaded 3-island fill
F(fill, "public int at;")          # 0.5.10 fix round 2: the next run of StarterIsles.DATA (the fill goes in world-thread slices)
F(fill, "public int placed;")      # 0.5.10 fix round 2: blocks placed (or, on the retry, found right) in this pass so far
F(fill, "public int slices;")      # 0.5.10 fix round 2: world-thread slices run (both passes) - in the log line
F(fill, "public int[] runs;")      # 0.5.10 fix round 2: StarterIsles.decode(), once per FillTask
F(fill, "public int fin;")         # 0.5.10 fix round 2: after the blocks: 1..8 = grass tint of chunk fin-1 (one per slice), 9 = the kit
''')
rep('''    return @BOP@.setBlock(world.getChunkStore(), r, x, y, z, bid, type, 0, 0, 0) ? 1 : 0;
  } catch (Throwable t) { return 0; }
}""")
M(fill, r"""
public void run() {
  int n = 0;
  try {
    if (section(world, 8, 128, 8) == null || section(world, 8, 124, 8) == null) { @PKG@.IslandStore.warn("chunk (0,0) did not load, island left empty"); done.complete(world); return; }
    if (blockAt(world, 8, 128, 8) > 0) { done.complete(world); return; }
    for (int x = 2; x <= 13; x++) for (int z = 2; z <= 13; z++) {''', '''    return @BOP@.setBlock(world.getChunkStore(), r, x, y, z, bid, type, 0, 0, 0) ? 1 : 0;
  } catch (Throwable t) { return 0; }
}""")''' + S3FILL + '''M(fill, r"""
public void run() {
  int n = 0;
  try {
    // 0.5.10 fix round 2: a later slice (at > 0) of a 3-island fill skips both checks (a section gone meanwhile = blocks short = the retry)
    if (this.at == 0 && (section(world, 8, 128, 8) == null || section(world, 8, 124, 8) == null)) { @PKG@.IslandStore.warn("chunk (0,0) did not load, island left empty"); done.complete(world); return; }
    if (this.tries == 0 && this.at == 0 && blockAt(world, 8, 128, 8) > 0) { done.complete(world); return; }   // 0.5.10: the retry pass is the same new island
    if (this.three) {                                   // 0.5.10: the 3 starter islands (chest + spawn as the classic island)
      boolean end = this.fin > 0 || @PKG@.StarterIsles.fill(this);
      this.slices = this.slices + 1;
      if (!end) { next(); return; }                     // fix round 2: the next slice ~20 ms later (accept -> World.execute)
      n = this.placed;
      if (this.fin == 0 && n < @PKG@.StarterIsles.BLOCKS && this.tries == 0) {
        // fix round (critic): a section did not load - ask the engine for all its chunks / sections again and fill ONCE more (the kit
        // and the kit flag wait for that pass; the skip guard above lets only this retry through)
        this.tries = 1;
        this.at = 0;
        this.placed = 0;
        @PKG@.IslandStore.warn("3 starter islands in " + world.getName() + ": " + n + " of " + @PKG@.StarterIsles.BLOCKS + " blocks placed (a section did not load) - loading again, one retry");
        java.util.concurrent.CompletableFuture.allOf(@PKG@.StarterIsles.loads(world.getChunkStore())).whenComplete(this);
        return;
      }
      // fix round 2: the grass tint one chunk per slice, then the kit in a slice of its own (each well under one tick step)
      if (this.fin <= @PKG@.StarterIsles.CHUNKS.length / 2) {
        if (this.fin > 0) @PKG@.StarterIsles.tintOne(world, this.fin - 1);
        this.fin = this.fin + 1;
        next();
        return;
      }
      String ow = @PKG@.IslandStore.ownerOf(world.getName());
      // fix round 2 (critic): RelightTask's late kit may already be in the chest (it can run between slices / passes) - never a second kit
      if (ow != null && @PKG@.IslandStore.KITDONE.containsKey(ow)) @PKG@.IslandStore.info("starter kit already in the chest of " + world.getName() + " (placed while the islands were filling) - not added again");
      else if (@PKG@.FillTask.starterKit(world) >= 0 && ow != null) @PKG@.IslandStore.setKitGiven(ow);
      @PKG@.IslandStore.info("3 starter islands placed in " + world.getName() + " (" + n + " of " + @PKG@.StarterIsles.BLOCKS + " blocks" + (this.tries > 0 ? ", after one retry" : "") + ") in " + this.slices + " world-thread slices");
      if (n < @PKG@.StarterIsles.BLOCKS) @PKG@.IslandStore.warn("3 starter islands in " + world.getName() + ": " + (@PKG@.StarterIsles.BLOCKS - n) + " blocks were not placed (a section did not load)");
      done.complete(world);
      return;
    }
    for (int x = 2; x <= 13; x++) for (int z = 2; z <= 13; z++) {''')
rep('''    java.util.concurrent.CompletableFuture[] parts = new java.util.concurrent.CompletableFuture[3];
    parts[0] = cs.getChunkReferenceAsync(@CHU@.indexChunk(0, 0));
    parts[1] = cs.getChunkSectionReferenceAsync(0, 3, 0);
    parts[2] = cs.getChunkSectionReferenceAsync(0, 4, 0);
    java.util.concurrent.CompletableFuture.allOf(parts).whenComplete(new @PKG@.FillTask(world, done));''', '''    @PKG@.FillTask ft = new @PKG@.FillTask(world, done);
    ft.three = @PKG@.StarterIsles.three();                 // 0.5.10: the design is fixed here, for this new island / reset
    java.util.concurrent.CompletableFuture[] parts;
    if (ft.three) parts = @PKG@.StarterIsles.loads(cs);
    else {
      parts = new java.util.concurrent.CompletableFuture[3];
      parts[0] = cs.getChunkReferenceAsync(@CHU@.indexChunk(0, 0));
      parts[1] = cs.getChunkSectionReferenceAsync(0, 3, 0);
      parts[2] = cs.getChunkSectionReferenceAsync(0, 4, 0);
    }
    java.util.concurrent.CompletableFuture.allOf(parts).whenComplete(ft);''')
rep('''    for (int cx = -1; cx <= 1; cx++) for (int cz = -1; cz <= 1; cz++) {
      // 0.5.6: 0.7's flood light calculation queues the column's sections and always answers false - count the chunks queued without an error
      try { world.getChunkLighting().invalidateLightInChunkSections(world.getChunkStore(), cx, cz, 0, 10); ok++; } catch (Throwable t) { }
    }
    int tinted = @PKG@.TintFix.fix(world);
    @PKG@.IslandStore.info("relight queued for " + world.getName() + " (" + ok + "/9 chunks)" + (tinted > 0 ? ", re-tinted " + tinted + " columns" : ""));''',
    '''    boolean s3 = @PKG@.StarterIsles.three();              // 0.5.10: the 3 starter islands reach cx 2 / cz 1 (12 columns)
    int x0 = s3 ? @PKG@.StarterIsles.CX0 : -1; int x1 = s3 ? @PKG@.StarterIsles.CX1 : 1;
    int z0 = s3 ? @PKG@.StarterIsles.CZ0 : -1; int z1 = s3 ? @PKG@.StarterIsles.CZ1 : 1;
    for (int cx = x0; cx <= x1; cx++) for (int cz = z0; cz <= z1; cz++) {
      // 0.5.6: 0.7's flood light calculation queues the column's sections and always answers false - count the chunks queued without an error
      try { world.getChunkLighting().invalidateLightInChunkSections(world.getChunkStore(), cx, cz, 0, 10); ok++; } catch (Throwable t) { }
    }
    int tinted = @PKG@.TintFix.fix(world);
    @PKG@.IslandStore.info("relight queued for " + world.getName() + " (" + ok + "/" + ((x1 - x0 + 1) * (z1 - z0 + 1)) + " chunks)" + (tinted > 0 ? ", re-tinted " + tinted + " columns" : ""));''')

# ------------------------------------------------------------------------------------------------ PlaceFn + hooks + setup / shutdown
PLFN = r'''
# 0.5.10 PlaceFn = island:fn:place: String id, or Object[] {UUID, String id} -> "island|x|y|z|label" (world "island" = any island world)
# while the design is the 3 islands; null otherwise / for an unknown id. Never throws.
plfn.addInterface(pool.get("java.util.function.Function"))
C(plfn, "public PlaceFn() { }")
M(plfn, r"""
public Object apply(Object o) {
  try {
    String id = null;
    if (o instanceof String) id = (String) o;
    else if (o instanceof Object[] && ((Object[]) o).length >= 2 && ((Object[]) o)[1] instanceof String) id = (String) ((Object[]) o)[1];
    if (id == null || !@PKG@.StarterIsles.three()) return null;
    return @PKG@.StarterIsles.placeOf(id);
  } catch (Throwable t) { return null; }
}""")
'''
rep('''# 0.5.8 C (review fix 2): island:fn:hub - UUID player -> Boolean (TRUE = sent).''', PLFN.lstrip("\n") + '''# 0.5.8 C (review fix 2): island:fn:hub - UUID player -> Boolean (TRUE = sent).''')
rep('''M(hooks, r"""
public static void reloadCfg() {
  @PKG@.IslandCfg.load(@PKG@.IslandCfg.BASE_ANIMALS);
  @PKG@.IslandStore.reparseAll();
}""")''', '''M(hooks, r"""
public static void reloadCfg() {
  @PKG@.IslandCfg.load(@PKG@.IslandCfg.BASE_ANIMALS);
  @PKG@.IslandStore.reparseAll();
  @PKG@.StarterIsles.publish();   // 0.5.10: island:places follows starter.design
}""")
# 0.5.10: starter.design changed in Server Setup -> island:places follows (new islands read the field at their ChunkFill.load)
M(hooks, r"""
public static void afterDesign(String key) {
  @PKG@.StarterIsles.publish();
}""")''')
rep('''  b.put("island:shardguard", "1");                       // 0.5.8 A: SkyyShards opens shard worlds only while this is published
''', '''  b.put("island:shardguard", "1");                       // 0.5.8 A: SkyyShards opens shard worlds only while this is published
  b.put("island:fn:place", new @PKG@.PlaceFn());         // 0.5.10: the 3 starter islands' named places (SkyyQuests)
  // 0.5.10 fix round 2: initialise the engine's BitSetUtil here (startup) - its first use after boot otherwise lands inside the first
  // island fill slice on the world thread (~40 ms, an engine "Task took" WARN seen on every first island since 0.5.6)
  try { Class.forName("com.hypixel.hytale.common.util.BitSetUtil"); } catch (Throwable t) { }
  @PKG@.StarterIsles.publish();                          // 0.5.10: island:places while starter.design = three
''')
rep('''"); portal sound " + (@PKG@.IslandCfg.SND_ON && @PKG@.IslandCfg.SND_PORTAL ? @PKG@.IslandCfg.SND_PORTAL_ID : "off"));''',
    '''"); portal sound " + (@PKG@.IslandCfg.SND_ON && @PKG@.IslandCfg.SND_PORTAL ? @PKG@.IslandCfg.SND_PORTAL_ID : "off") + "; new islands: " + (@PKG@.StarterIsles.three() ? "3 starter islands (" + @PKG@.StarterIsles.BLOCKS + " blocks)" : "classic island"));''')
rep('''    b.remove("island:role:key:fn"); b.remove("island:shardguard"); b.remove("island:world:key:fn"); b.remove("island:fn:hub");   // 0.5.8 C
''', '''    b.remove("island:role:key:fn"); b.remove("island:shardguard"); b.remove("island:world:key:fn"); b.remove("island:fn:hub");   // 0.5.8 C
    b.remove("island:fn:place"); b.remove("island:places");   // 0.5.10
''')

# ================================================================================================ checks on the result
_i = s.index
assert _i("S3_L, S3_PLACES, S3_TOPS, S3_ISLE = s3_layout()") < _i("J = B.start()")
assert _i("public static int tint(@WLD@ w)") > _i("public static int tintChunk(@WLD@ w, long idx)")
assert _i("public int put(int x, int y, int z, String id)") < _i("public static boolean fill(@PKG@.FillTask t)") < _i("public void run() {\n  int n = 0;\n  try {\n    // 0.5.10 fix round 2: a later slice")
assert _i("public static java.util.concurrent.CompletableFuture[] loads(") < _i("public static java.util.concurrent.CompletableFuture load(@WLD@ world)")
assert _i("public Object apply(Object o) {\n  try {\n    String id = null;") < _i("public static void afterDesign(String key)") < _i("public void setup()")
assert _i("isnd = K(") < _i("s3i  = K(") < _i("pl   = K(")
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.5.9 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.5.9 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
