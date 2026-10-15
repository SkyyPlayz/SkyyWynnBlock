"""Derive SkyyIslands/build_skyyislands_0.5.13.py from the LIVE 0.5.12 (build_skyyislands_0.5.12.py = the tools/deploy_set.py SET pin, made by
tools/islands_0_5_12_patch.py - never edit a generated script, edit this patch). Every anchor is asserted; at the end every change is undone
on a copy and compared with 0.5.12 (nothing else changed). Line endings kept.
    python tools/islands_0_5_13_patch.py   then   python SkyyIslands/build_skyyislands_0.5.13.py   then
    python SkyyIslands/test_skyyislands_0.5.13.py
(never --deploy: tools/deploy_set.py deploys the whole set).

0.5.13 (2026-10-15) = ISLAND TIME, THE PORTAL, THE CAMP, LOGIN (round islands0513; Skyy 2026-10-15: "time on my island doesnt match the hub" /
"portal spawned the wrong way. and you dont need the big frame around it" / "also the skeletons on my island keep respawning" + popup "Stop
after the quest (Recommended)" / "also when i connect, i should start on my island").
  1. ISLAND TIME = HUB TIME (Server Setup -> Islands -> Hub -> "Island time = hub time", islands.syncTime, default on; off = every world
     keeps its own clock, as before). Every island world (skyy-island-*) and SkyyShards shard world (skyy-shard-*) with a player in it
     keeps the hub world's game time (IslandStore.HUB_WORLD, else the default world): time of day, day count and moon phase (the engine
     derives the moon phase from the day - WorldTimeResource.setGameTime(Instant, World, accessor) = what /time set uses, it also sends
     the time to the players there). Cheap: one task on the hub's thread reads the hub's clock and hands it to each such world's own
     thread at most every 5 s per world (a new arrival is synced within 1 s); a world within 60 game-seconds of the hub is left alone.
     TIME NEVER GOES BACKWARDS (crops, saplings, benches, coops and DynamicSeasons read the world's game time; a backward jump would stall
     them): a world BEHIND the hub jumps forward to the hub (day + time); a world AHEAD (a bed skipped the night on the island, or an
     admin's /time there) is HELD - its clock paused (WorldConfig.setGameTimePaused, as /time pause) until the hub catches up, at most
     12 game hours (a bed skip ~ the rest of the night); further ahead = forward to the hub's next same time of day (the day count stays
     ahead). A bed skip in progress is never touched. The hub's own pause (/time pause in the hub) is mirrored on islands. Shard worlds
     are never paused by us: ahead = forward to the hub's time of day; hub paused = left alone. A held island is remembered in its island
     file (time.held=1) so a restart / unload mid-hold never leaves its clock paused: the next sync unpauses it (sync off: the island is
     unpaused once on its next visit). A hub clock that cannot be read (hub world not loaded / not set) releases held islands too. SkyyShards is not touched (time only, through the engine).
     GROWTH: while an island is unloaded (no players - instance WorldEmpty) its clock stood still before 0.5.13 (crops did not grow while
     you were away). Now it jumps forward to the hub's time when you arrive, and vanilla farming catches up the elapsed game time on its
     next tick (FarmingUtil.tickFarming: growth from lastTickGameTime to now, engine-capped) - crops / saplings grow while you are away,
     never backwards. The first sync of an old island is one big forward jump (e.g. Day 1 -> Day 27), so its crops may finish at once.
  2. THE HUB PORTAL: (a) the pad faces the way players walk in: BlockOperations.setBlock with rotation index 1 (yaw 90, NESW) for the
     portal pad and the socket (IsleEng.rotFor); a pad already standing with rotation 0 (0.5.12 islands) is turned once on the next visit
     (rotation read back through BlockSection.getRotationIndex). (b) NO BIG FRAME: new / reset 3-island islands get only the socket on
     the summit (the frame's 13 blocks are gone from the layout - S3_FRAME); the socket ("Broken Hub Portal", F to repair) now looks like
     the dormant portal pad (the pad's own model, no swirl / sound, a faint glow) = the portal's own base. On EXISTING islands the old
     frame goes when the portal is repaired, or on the next visit of an already repaired island: only the generator's exact cells (the
     13 frame cells + the 3 broken-top cells 0.5.12's repair filled), only where the cell still holds the generator's block id, only when
     at least 6 of the 16 still do (a frameless island never loses a player's block), once per island (portal.frame=gone in the island
     file). portal=1, the pad and the quest event (island:portal) are unchanged; the old top-filling on repair is gone.
  3. THE CAMP STOPS AFTER THE QUEST (Server Setup -> Starter islands -> "Camp stops after the quest", camp.stopAfterQuest, default on):
     no new camp skeletons once the island OWNER's profile has the tutorial task tutorial.defeat_mobs ("Defeat 5 mobs") done - read
     through SkyyQuests' quest:fn:done (Object[] {UUID, "line.task"} on the player's ACTIVE profile, so only while the owner is online
     with that island's profile active; co-op: stops once the owner has it). Remembered in the island file (camp.done=1, asked at most
     every 10 s until then). Skeletons already alive are left to die normally (no despawn, nothing lost). No SkyyQuests / owner never seen
     done = the camp as before.
  4. START ON YOUR ISLAND (Server Setup -> Hub -> "Start on your island", islands.islandOnLogin, default on): the first PlayerReady of an
     online session (login routing, +1.5 s, on that world's thread) sends a player who has an island (co-op member: the co-op island) to
     it through /island's own path (IslandCmd.go: loads the world first, teleports to the island's home / spawn) - unless they logged in
     on that island or in a world with its own respawn (islands.respawnKeep - shards skyy-shard-*, zone islands skywynn_z*, as the
     respawn hook; SkyyShards' own login router keeps working). Players with the Player Settings
     switch "Hub on login" (islands.hubOnLogin) ON, no island, or the setting off = as before (logged in on an island world -> the hub,
     else stay). The switch's registered default becomes OFF (everyone starts on their island); a player who switched it on keeps it.
     Only the first ready of the session routes (IslandStore.SEEN), so a world switch / respawn / the /island arrival never loops.
  5. No saved-data loss: new island-file keys only (time.held, portal.frame, camp.done; /island reset clears them), the frame / pad
     rotation changes blocks only on repaired portals. New config lines islands.syncTime, islands.islandOnLogin, camp.stopAfterQuest (a
     fresh file lists them, an existing file without them = the default; nothing rewritten). No command / permission change.
     ROLLBACK to 0.5.12: safe (a held island is unpaused on its next 0.5.12-free visit only if sync is turned on again - 0.5.12 ignores
     time.held, so roll back with no island mid-hold, i.e. nobody sleeping on an island; frames already removed stay removed; the
     socket looks like a smooth brick again).
UNVERIFIED in game: the pad's swirl facing (rotation 1 vs 3 is a mirror; the model is symmetric), the time packet on a hold, DynamicSeasons
on a forward jump.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.5.12.py")
dst = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.5.13.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.5.12"' in s and "GENERATED by tools/islands_0_5_12_patch.py" in s and "S3_FRAME" not in s, "not the generated 0.5.12 script"
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
NOTE = HEAD[HEAD.index("0.5.13 (2026-10-15)"):].rstrip() + "\n\n"

# ================================================================================================ docstring + version
rep('''"""SkyyIslands 0.5.12 - build script (javassist via jpype). GENERATED by tools/islands_0_5_12_patch.py from the LIVE 0.5.11 (itself
generated by tools/islands_0_5_11_patch.py from 0.5.10) - edit the patch, then regenerate; never edit this file by hand. Never run with
--deploy (tools/deploy_set.py deploys the coordinated set). Test: python SkyyIslands/test_skyyislands_0.5.12.py
''', '''"""SkyyIslands 0.5.13 - build script (javassist via jpype). GENERATED by tools/islands_0_5_13_patch.py from the LIVE 0.5.12 (itself
generated by tools/islands_0_5_12_patch.py from 0.5.11) - edit the patch, then regenerate; never edit this file by hand. Never run with
--deploy (tools/deploy_set.py deploys the coordinated set). Test: python SkyyIslands/test_skyyislands_0.5.13.py

''' + NOTE + '''0.5.12 (the base, still true unless 0.5.13 above says otherwise):
''')
rep('VERSION = "0.5.12"', 'VERSION = "0.5.13"')

# ================================================================================================ layout: no big frame (only the socket)
rep('''S3_MOUTH = (11, 13, 12, 14)      # 0.5.11: the cave mouth - x 11-13 wide, the opening at z 12, the passage to z 14 (the tunnel starts at z 15)
''', '''S3_MOUTH = (11, 13, 12, 14)      # 0.5.11: the cave mouth - x 11-13 wide, the opening at z 12, the passage to z 14 (the tunnel starts at z 15)
S3_FRAME = []                    # 0.5.13: the old portal frame's cells (x, y, z, block id) - no longer built; removed from repaired islands
''')
rep('''    for k in range(6):
        L[(fx, fy + k, fz0)] = "Rock_Stone_Brick"
    for k in range(4):
        L[(fx, fy + k, fz0 + 4)] = "Rock_Stone_Brick_Mossy"
    for z in range(fz0, fz0 + 3):
        L[(fx, fy + 5, z)] = "Rock_Stone_Brick_Decorative"
    L[(fx, fy, fz0 + 2)] = "Rock_Stone_Brick_Smooth"            # the empty socket for the Hub Shard (a later round)
    L[(fx, fy, fz0 + 1)] = "Rock_Stone_Brick_Half"
''', '''    # 0.5.13 (Skyy 2026-10-15: "you dont need the big frame around it"): the frame 0.5.10-0.5.12 built is only RECORDED (S3_FRAME - the
    # cells a repaired portal clears on existing islands); new / reset islands get the socket alone on the summit
    fr = {}
    for k in range(6):
        fr[(fx, fy + k, fz0)] = "Rock_Stone_Brick"
    for k in range(4):
        fr[(fx, fy + k, fz0 + 4)] = "Rock_Stone_Brick_Mossy"
    for z in range(fz0, fz0 + 3):
        fr[(fx, fy + 5, z)] = "Rock_Stone_Brick_Decorative"
    fr[(fx, fy, fz0 + 1)] = "Rock_Stone_Brick_Half"
    del S3_FRAME[:]
    S3_FRAME.extend((k[0], k[1], k[2], b) for k, b in sorted(fr.items()))
    L[(fx, fy, fz0 + 2)] = "Rock_Stone_Brick_Smooth"            # the socket for the Hub Shard (the portal's own base)
''')
rep('''    return {"socket": socket, "fix": fix, "spots": spots, "probe": probe, "isle2": (i2[1] + 0.5, i2[2] + 0.5), "boss": places["boss"][:3],
            "camp": cam[:3], "pad": (fx, fy, fz0 + 2)}
''', '''    # 0.5.13: the old frame = the 13 frame cells + the 3 broken-top cells 0.5.12's repair filled (only these are ever cleared)
    frame = [tuple(c) for c in S3_FRAME] + [tuple(f) for f in fix]
    assert len(frame) == 16 and len(set(c[:3] for c in frame)) == 16 and all(c[:3] not in L for c in frame) and socket not in [c[:3] for c in frame]
    return {"socket": socket, "fix": fix, "spots": spots, "probe": probe, "isle2": (i2[1] + 0.5, i2[2] + 0.5), "boss": places["boss"][:3],
            "camp": cam[:3], "pad": (fx, fy, fz0 + 2), "frame": frame}
''')

# ================================================================================================ config: 3 new settings
rep('''# 0.5.2: the starter kit that 0.5.1 hard-coded in FillTask.starterKit (same items, order and amounts) = config starter.kit's default
''', '''# 0.5.13: island time = hub time, start on your island, the camp stops after the quest
P2_ROWS += [
    ('islands.syncTime', 'Island time = hub time', 'hub', 'bool', 'true', '', '', '', '', 'live',
     "Island and shard worlds keep the hub's time of day, day and moon (never backwards).",
     'field:IslandCfg.SYNC_TIME@config.properties:islands.syncTime'),
    ('islands.islandOnLogin', 'Start on your island', 'hub', 'bool', 'true', '', '', '', '', 'live',
     "Players log in on their island (their Hub on login switch on = the hub; in a shard = stay there).",
     'field:IslandCfg.ISLAND_LOGIN@config.properties:islands.islandOnLogin'),
    ('camp.stopAfterQuest', 'Camp stops after the quest', 'isles', 'bool', 'true', '', '', '', '', 'live',
     "No new camp skeletons once the island owner has done Defeat 5 mobs (needs SkyyQuests).",
     'field:IslandCfg.CAMP_STOP@config.properties:camp.stopAfterQuest'),
]
# 0.5.2: the starter kit that 0.5.1 hard-coded in FillTask.starterKit (same items, order and amounts) = config starter.kit's default
''')
rep('''    "islands.respawnKeep=skyy-shard-,skywynn_z",
    "",
])''', '''    "islands.respawnKeep=skyy-shard-,skywynn_z",
    "# 0.5.13 true = island and shard worlds keep the hub's time of day, day and moon (never backwards; false = their own clocks)",
    "islands.syncTime=true",
    "# 0.5.13 true = players log in on their own island (their Hub on login switch on = the hub; logged out in a shard = stay there)",
    "islands.islandOnLogin=true",
    "# 0.5.13 true = no new camp skeletons once the island owner has done the tutorial's Defeat 5 mobs (needs SkyyQuests)",
    "camp.stopAfterQuest=true",
    "",
])''')
rep('''          "public static volatile String RESPAWN_KEEP = \\"skyy-shard-,skywynn_z\\";"):''',
    '''          "public static volatile String RESPAWN_KEEP = \\"skyy-shard-,skywynn_z\\";",
          # 0.5.13: island time = hub time, start on your island, the camp stops after the quest
          "public static volatile boolean SYNC_TIME = true;", "public static volatile boolean ISLAND_LOGIN = true;",
          "public static volatile boolean CAMP_STOP = true;"):''')
rep('''      RESPAWN_KEEP = p.getProperty("islands.respawnKeep", "skyy-shard-,skywynn_z").trim();
''', '''      RESPAWN_KEEP = p.getProperty("islands.respawnKeep", "skyy-shard-,skywynn_z").trim();
      SYNC_TIME = !"false".equalsIgnoreCase(p.getProperty("islands.syncTime", "true").trim());           // 0.5.13
      ISLAND_LOGIN = !"false".equalsIgnoreCase(p.getProperty("islands.islandOnLogin", "true").trim());  // 0.5.13
      CAMP_STOP = !"false".equalsIgnoreCase(p.getProperty("camp.stopAfterQuest", "true").trim());       // 0.5.13
''')

# ================================================================================================ /island reset clears the new keys
rep('''    p.remove("portal"); p.remove("portal.at"); p.remove("portal.by"); p.remove("isles");   // 0.5.12: a reset island has a broken portal again
''', '''    p.remove("portal"); p.remove("portal.at"); p.remove("portal.by"); p.remove("isles");   // 0.5.12: a reset island has a broken portal again
    p.remove("portal.frame"); p.remove("camp.done"); p.remove("time.held");                  // 0.5.13: a reset island starts fresh
''')

# ================================================================================================ engine aliases (world time, sleep)
rep('''    "V3DC":  "org.joml.Vector3dc",
''', '''    "V3DC":  "org.joml.Vector3dc",
    # 0.5.13: island time = hub time (the world clock /time set uses) + a bed skip in progress (WorldSomnolence state = WorldSlumber)
    "WTR":   "com.hypixel.hytale.server.core.modules.time.WorldTimeResource",
    "WSOM":  "com.hypixel.hytale.builtin.beds.sleep.resources.WorldSomnolence",
    "WSLU":  "com.hypixel.hytale.builtin.beds.sleep.resources.WorldSlumber",
''')

# ================================================================================================ login routing: start on your island
rep('''M(rout, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return;
    @WLD@ w = @UNI@.get().getWorld(wu);
    if (w == null || !@PKG@.IslandStore.isIslandWorld(w.getName())) return;
    @REF@ r = pr.getReference();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    boolean sent = @PKG@.HubCmd.sendToHub(st, r, pr, w);   // 0.5.2: the teleport never depends on the player's setting
    if (sent && @PKG@.IslandStore.notifyOn(pr.getUuid(), "islands.hubOnLogin")) pr.sendMessage(@MSG@.raw("[Island] Welcome back! You start in the hub - /island takes you home."));
  } catch (Throwable t) { @PKG@.IslandStore.warn("login routing failed: " + t); }
}""")''', '''F(rout, "public static final java.util.concurrent.atomic.AtomicLong HOME = new java.util.concurrent.atomic.AtomicLong();")
# 0.5.13 review: a world with its own respawn (islands.respawnKeep: shards, zone islands) keeps a player who logged out there - the same
# test as the respawn hook's IsleLife.keepWorld (IsleLife is compiled after RouteTask, so it is repeated here on IslandCfg.RESPAWN_KEEP)
M(rout, r"""
public static boolean keep(String wn) {
  if (wn == null) return false;
  if (wn.startsWith("skyy-shard-")) return true;
  String csv = @PKG@.IslandCfg.RESPAWN_KEEP;
  String[] a = csv == null ? new String[0] : csv.split(",");
  for (int i = 0; i < a.length; i++) {
    String p = a[i].trim();
    if (p.length() > 0 && wn.startsWith(p)) return true;
  }
  return false;
}""")
# 0.5.13 the login decision (pure; the harness runs it): 0 = stay, 1 = to the player's island (/island's path), 2 = to the hub
M(rout, r"""
public static int decide(String wn, String home, boolean onIsland, boolean islandOn, boolean hubPref) {
  if (wn == null) return 0;
  if (!islandOn || hubPref || home == null) return onIsland ? 2 : 0;    // as before 0.5.13: logged in on an island world -> the hub
  if (wn.equals(home)) return 0;                                        // on their own / co-op island already
  if (keep(wn)) return 0;                                              // a shard / zone world (islands.respawnKeep): stay there
  return 1;
}""")
# the Player Settings switch "Hub on login" (islands.hubOnLogin): only a stored / admin TRUE means the hub (no SkyyMenu = the island)
M(rout, r"""
public static boolean hubPref(java.util.UUID u) {
  try {
    Object f = @PKG@.IslandStore.bridge().get("settings:fn:get");
    if (!(f instanceof java.util.function.Function)) return false;
    return Boolean.TRUE.equals(((java.util.function.Function) f).apply(new Object[] { u, "islands.hubOnLogin" }));
  } catch (Throwable t) { return false; }
}""")
M(rout, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return;
    @WLD@ w = @UNI@.get().getWorld(wu);
    if (w == null) return;
    String wn = w.getName();
    java.util.UUID u = pr.getUuid();
    String hk = @PKG@.IslandStore.homeKey(u);
    @PKG@.IslandSettings s = hk == null ? null : @PKG@.IslandStore.settings(hk);
    String home = (s == null || s.bad) ? null : s.world;
    int d = decide(wn, home, @PKG@.IslandStore.isIslandWorld(wn), @PKG@.IslandCfg.ISLAND_LOGIN, hubPref(u));
    if (d == 0) return;
    @REF@ r = pr.getReference();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    if (d == 1) {                                          // 0.5.13: /island's own path (loads the island world first)
      HOME.incrementAndGet();
      @PKG@.IslandCmd.go(st, r, pr, w, hk, hk.equals(@PKG@.IslandStore.pkey(u)));
      return;
    }
    boolean sent = @PKG@.HubCmd.sendToHub(st, r, pr, w);   // 0.5.2: the teleport never depends on the player's setting
    if (sent) pr.sendMessage(@MSG@.raw("[Island] Welcome back! You start in the hub - /island takes you home."));
  } catch (Throwable t) { @PKG@.IslandStore.warn("login routing failed: " + t); }
}""")''')
rep('''  @PKG@.IslandStore.regSetting("islands.hubOnLogin", "Hub on login", "profiles", true, "Welcome back! You start in the hub - when you log in on an island");''',
    '''  @PKG@.IslandStore.regSetting("islands.hubOnLogin", "Hub on login", "profiles", false, "Start in the hub when you log in - off: you start on your own island");   // 0.5.13: default off''')

# ================================================================================================ the socket = the dormant portal pad
rep('''    P2_SOCKET: {"TranslationProperties": {"Name": "server.items.%s.name" % P2_SOCKET}, "Icon": "Icons/ItemsGenerated/Rock_Stone_Brick_Smooth.png",
                "PlayerAnimationsId": "Block", "Quality": "Technical",
                "BlockType": {"Material": "Solid", "DrawType": "Cube", "Group": "Stone", "Flags": {},
                              "Gathering": {"Breaking": {"GatherType": "Unbreakable"}}, "BlockParticleSetId": "Stone",
                              "Textures": [{"All": "BlockTextures/Rock_Stone_Brick_Smooth.png", "Weight": 1}],
                              "ParticleColor": "#737055", "BlockSoundSetId": "Stone", "PhysicalMaterialId": "Stone",   # ui-data: block particles (not UI)
                              "Light": {"Color": "#536"},   # ui-data: a faint violet glow of the empty socket (not UI)
                              "InteractionHint": "server.interactionHints.repair", "Interactions": {"Use": _p2_use("SFX_Crystal_Hit")}}},''',
    '''    # 0.5.13: the socket is the portal's own base - the hub portal pad's model, dormant (no swirl, no sound, no animation), a faint glow
    P2_SOCKET: {"TranslationProperties": {"Name": "server.items.%s.name" % P2_SOCKET}, "Icon": "Icons/ItemsGenerated/Portal_Device.png",
                "PlayerAnimationsId": "Block", "Quality": "Technical",
                "BlockType": {"DrawType": "Model", "Material": "Solid", "Opacity": "Transparent",
                              "CustomModel": "Blocks/Miscellaneous/Platform_MagicInactive.blockymodel",
                              "CustomModelTexture": [{"Texture": "Blocks/Miscellaneous/Platform_Magic_Blue.png", "Weight": 1}],
                              "HitboxType": "Pad_Portal", "VariantRotation": "NESW", "Flags": {},
                              "Gathering": {"Breaking": {"GatherType": "Unbreakable"}}, "BlockParticleSetId": "Stone",
                              "BlockSoundSetId": "Stone", "PhysicalMaterialId": "Stone",
                              "Light": {"Color": "#536"},   # ui-data: a faint violet glow of the broken portal (not UI)
                              "InteractionHint": "server.interactionHints.repair", "Interactions": {"Use": _p2_use("SFX_Crystal_Hit")}}},''')
rep('''           "Common/Blocks/Miscellaneous/Platform_Magic_Blue2.png", "Common/Blocks/Miscellaneous/Platform_Magic_Idle.blockyanim",''',
    '''           "Common/Blocks/Miscellaneous/Platform_Magic_Blue2.png", "Common/Blocks/Miscellaneous/Platform_Magic_Idle.blockyanim",
           "Common/Blocks/Miscellaneous/Platform_Magic_Blue.png", "Server/Item/Block/Hitboxes/Furniture/Pad_Portal.json",   # 0.5.13: the socket''')

# ================================================================================================ the seam: new engine calls
rep('''             "public abstract void relight(String wn);"):
    M(iapi, _sig)''', '''             "public abstract void relight(String wn);",
             # 0.5.13: block rotation, the world clock (island time = hub time), SkyyQuests task state
             "public abstract int rot(String wn, int x, int y, int z);",
             "public abstract long gameTime(String wn);",
             "public abstract int timeFlags(String wn);",
             "public abstract boolean setGameTime(String wn, long ms);",
             "public abstract boolean setTimePaused(String wn, boolean p);",
             "public abstract java.util.Set timeWorlds();",
             "public abstract int questDone(String owner, String task);"):
    M(iapi, _sig)''')
rep('''           "public long blocksAt;", "public boolean portal;", "public boolean named;",''',
    '''           "public long blocksAt;", "public boolean portal;", "public boolean named;",
           "public boolean campDone;", "public long questAt;", "public boolean rotOk;", "public boolean frameDone;",   # 0.5.13''')
rep('''for _f in ("public int mode;", "public String wn;", "public java.util.UUID u;", "public String a;", "public String[] ks;", "public String[] vs;"):
    F(itsk, _f)''', '''for _f in ("public int mode;", "public String wn;", "public java.util.UUID u;", "public String a;", "public String[] ks;", "public String[] vs;",
           "public long ms;", "public int fl;"):    # 0.5.13: the hub's clock + flags handed to a world's time task
    F(itsk, _f)''')

# ================================================================================================ IsleEng: rotation, air, the clock, quests
rep('''# BlockOperations.setBlock exactly as FillTask.put (rotation 0, filler 0, settings 0)
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
}""")''', '''# 0.5.13: the rotation a block is placed with - the portal pad and its socket face the way players walk in (yaw 90 = RotationTuple 1)
M(ieng, r"""
public static int rotFor(String id) {
  return ("Skyy_Island_Hub_Portal".equals(id) || "Skyy_Island_Portal_Socket".equals(id)) ? 1 : 0;
}""")
# BlockOperations.setBlock as FillTask.put (filler 0, settings 0); 0.5.13: rotation rotFor(id), "" = air (BlockType.EMPTY)
M(ieng, r"""
public boolean setBlock(String wn, int x, int y, int z, String id) {
  @WLD@ w = world(wn);
  if (w == null || id == null) return false;
  try {
    @REF@ r = @PKG@.FillTask.section(w, x, y, z);
    if (r == null) return false;
    int bid = 0;
    @BTY@ type = null;
    if (id.length() == 0) {
      bid = @BTY@.EMPTY_ID;
      type = @BTY@.EMPTY;
    } else {
      bid = @BTY@.getAssetMap().getIndex(id);
      if (bid == Integer.MIN_VALUE) return false;
      type = (@BTY@) @BTY@.getAssetMap().getAsset(bid);
    }
    if (type == null) return false;
    return @BOP@.setBlock(w.getChunkStore(), r, x, y, z, bid, type, rotFor(id), 0, 0);
  } catch (Throwable t) { return false; }
}""")
# 0.5.13: the rotation index at x,y,z (-1 = not loaded)
M(ieng, r"""
public int rot(String wn, int x, int y, int z) {
  @WLD@ w = world(wn);
  if (w == null) return -1;
  try {
    @REF@ r = @PKG@.FillTask.section(w, x, y, z);
    if (r == null) return -1;
    @BSEC@ bs = (@BSEC@) w.getChunkStore().getStore().getComponent(r, @BSEC@.getComponentType());
    return bs == null ? -1 : bs.getRotationIndex(x, y, z);
  } catch (Throwable t) { return -1; }
}""")''')
rep('''M(ieng, "public void relight(String wn) { @PKG@.RelightTask.schedule(wn); }")
''', '''M(ieng, "public void relight(String wn) { @PKG@.RelightTask.schedule(wn); }")
# 0.5.13 island time = hub time: the world clock (WorldTimeResource, epoch ms; Long.MIN_VALUE = unknown) - that world's thread
M(ieng, r"""
public long gameTime(String wn) {
  @WLD@ w = world(wn);
  if (w == null) return Long.MIN_VALUE;
  try {
    @WTR@ t = (@WTR@) w.getEntityStore().getStore().getResource(@WTR@.getResourceType());
    if (t == null || t.getGameTime() == null) return Long.MIN_VALUE;
    return t.getGameTime().toEpochMilli();
  } catch (Throwable x) { return Long.MIN_VALUE; }
}""")
# bit 1 = the clock is paused (WorldConfig), bit 2 = a bed skip is running (WorldSomnolence state WorldSlumber); -1 = unknown
M(ieng, r"""
public int timeFlags(String wn) {
  @WLD@ w = world(wn);
  if (w == null) return -1;
  int f = 0;
  try { if (w.getWorldConfig().isGameTimePaused()) f = f | 1; } catch (Throwable t) { return -1; }
  try {
    @WSOM@ s = (@WSOM@) w.getEntityStore().getStore().getResource(@WSOM@.getResourceType());
    if (s != null && s.getState() instanceof @WSLU@) f = f | 2;
  } catch (Throwable t) { }
  return f;
}""")
# = /time set: WorldTimeResource.setGameTime(Instant, World, accessor) sets day + time, the moon phase, and sends the time to the players
M(ieng, r"""
public boolean setGameTime(String wn, long ms) {
  @WLD@ w = world(wn);
  if (w == null) return false;
  try {
    @ST@ st = w.getEntityStore().getStore();
    @WTR@ t = (@WTR@) st.getResource(@WTR@.getResourceType());
    if (t == null) return false;
    t.setGameTime(java.time.Instant.ofEpochMilli(ms), w, (@CA@) st);
    return true;
  } catch (Throwable x) { return false; }
}""")
# = /time pause: WorldConfig.setGameTimePaused (the time system sends the new settings to the players on its next tick)
M(ieng, r"""
public boolean setTimePaused(String wn, boolean p) {
  @WLD@ w = world(wn);
  if (w == null) return false;
  try {
    @WCFG@ c = w.getWorldConfig();
    if (c.isGameTimePaused() == p) return false;
    c.setGameTimePaused(p);
    c.markChanged();
    return true;
  } catch (Throwable t) { return false; }
}""")
# loaded island / shard worlds with a player in them (scheduler thread)
M(ieng, r"""
public java.util.Set timeWorlds() {
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
      String n = w.getName();
      if (n != null && (n.startsWith("skyy-island-") || n.startsWith("skyy-shard-"))) out.add(n);
    }
  } catch (Throwable t) { }
  return out;
}""")
# SkyyQuests quest:fn:done (Object[] {UUID, "line.task"}, the ACTIVE profile): 1 done, 0 not, -1 unknown (no Quests / owner offline or on
# another profile)
M(ieng, r"""
public int questDone(String owner, String task) {
  try {
    Object f = @PKG@.IslandStore.bridge().get("quest:fn:done");
    if (!(f instanceof java.util.function.Function) || owner == null) return -1;
    java.util.UUID u = @PKG@.IslandStore.ownerUuid(owner);
    if (u == null || @PKG@.IslandStore.online(u) == null) return -1;
    if (!owner.equals(@PKG@.IslandStore.pkey(u))) return -1;
    return Boolean.TRUE.equals(((java.util.function.Function) f).apply(new Object[] { u, task })) ? 1 : 0;
  } catch (Throwable t) { return -1; }
}""")
for c, m in ((T["WTR"], "getResourceType"), (T["WTR"], "getGameTime"), (T["WTR"], "setGameTime"), (T["WSOM"], "getResourceType"),
             (T["WSOM"], "getState"), (T["WCFG"], "isGameTimePaused"), (T["WCFG"], "setGameTimePaused"), (T["BSEC"], "getRotationIndex")):
    B.probe(pool, c, m)      # 0.5.13: a missing engine member stops the build here, not in game
''')

# ================================================================================================ IsleLife: constants
rep('''           "public static final int PROBE_NEED = 6;",''', '''           "public static final int PROBE_NEED = 6;",
           # 0.5.13: the old frame (16 cells: frame + 0.5.12's filled top) and how many must still hold the generator's ids to be cleared
           "public static final int[] FRAME = new int[] { %s };" % ", ".join(_ji(f_[:3]) for f_ in _P2["frame"]),
           "public static final String[] FRAME_IDS = new String[] { %s };" % ", ".join('"%s"' % f_[3] for f_ in _P2["frame"]),
           "public static final int FRAME_NEED = 6;",
           'public static final String QUEST_TASK = "tutorial.defeat_mobs";',
           # 0.5.13 island time = hub time: last sync per world, the worlds we paused, the hub task queued at
           "public static final java.util.concurrent.ConcurrentHashMap TIME_AT = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap HELD = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile long HUBQ = 0L;",
           "public static final long TIME_GAP = 5000L;", "public static final long TIME_TOL = 60000L;",
           "public static final long TIME_HOLD = 43200000L;", "public static final long DAY_MS = 86400000L;",
           "public static final java.util.concurrent.atomic.AtomicLong SYNCS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong FRAMES = new java.util.concurrent.atomic.AtomicLong();",''')

# ================================================================================================ camp: stop after the quest
rep('''M(ilif, r"""
public static int campTick(String wn, @PKG@.IsleState st, java.util.ArrayList mem, long now) {
  if (!@PKG@.IslandCfg.CAMP_ON) return 0;
  if (!anyNear(mem, ISLE2[0], ISLE2[1], ISLE2_R)) return 0;
''', '''# 0.5.13: the island owner's profile has tutorial.defeat_mobs done (SkyyQuests, asked every 10 s; remembered as camp.done=1)
M(ilif, r"""
public static boolean campDone(String wn, @PKG@.IsleState st, long now) {
  if (st.campDone) return true;
  String owner = @PKG@.IslandStore.ownerOf(wn);
  if (owner == null) return false;
  if (fileHas(owner, "camp.done", "1")) { st.campDone = true; return true; }
  if (st.questAt != 0L && now - st.questAt >= 0L && now - st.questAt < 10000L) return false;
  st.questAt = now;
  if (api().questDone(owner, QUEST_TASK) != 1) return false;
  st.campDone = true;
  saveProps(owner, new String[] { "camp.done" }, new String[] { "1" });
  return true;
}""")
M(ilif, r"""
public static int campTick(String wn, @PKG@.IsleState st, java.util.ArrayList mem, long now) {
  if (!@PKG@.IslandCfg.CAMP_ON) return 0;
  if (!anyNear(mem, ISLE2[0], ISLE2[1], ISLE2_R)) return 0;
  if (@PKG@.IslandCfg.CAMP_STOP && campDone(wn, st, now)) return 0;     // 0.5.13: the camp stops after the quest
''')

# ================================================================================================ portal: turn the pad, clear the old frame
rep('''# the socket while broken / the pad once repaired, re-checked every 30 s (only over the smooth brick, air, or the other of the two)
M(ilif, r"""
public static int portalBlocks(String wn, @PKG@.IsleState st, String owner, long now) {''', '''# 0.5.13: a pad placed with another rotation (0.5.12) is turned once (air, then the pad with rotFor = 1); -1 rotation = not loaded, later
M(ilif, r"""
public static int padTurn(String wn, @PKG@.IsleState st) {
  if (st.rotOk) return 0;
  @PKG@.IsleApi a = api();
  int r = a.rot(wn, SOCKETP[0], SOCKETP[1], SOCKETP[2]);
  if (r < 0) return 0;
  st.rotOk = true;
  if (r == @PKG@.IsleEng.rotFor(PAD)) return 0;
  a.setBlock(wn, SOCKETP[0], SOCKETP[1], SOCKETP[2], "");
  return a.setBlock(wn, SOCKETP[0], SOCKETP[1], SOCKETP[2], PAD) ? 1 : 0;
}""")
# 0.5.13 (Skyy: "you dont need the big frame around it"): once per island, after the repair - the generator's frame cells that still hold
# the generator's block id become air, only when at least FRAME_NEED of the 16 do (a frameless island never loses a player's block);
# portal.frame=gone in the island file. Any cell not loaded = try again later.
M(ilif, r"""
public static int frameClear(String wn, String owner, @PKG@.IsleState st) {
  if (st.frameDone) return 0;
  if (fileHas(owner, "portal.frame", "gone")) { st.frameDone = true; return 0; }
  @PKG@.IsleApi a = api();
  int k = FRAME_IDS.length;
  boolean[] hit = new boolean[k];
  int match = 0;
  for (int i = 0; i < k; i++) {
    String b = a.block(wn, FRAME[i * 3], FRAME[i * 3 + 1], FRAME[i * 3 + 2]);
    if (b == null) return 0;
    if (FRAME_IDS[i].equals(b)) { hit[i] = true; match++; }
  }
  int n = 0;
  if (match >= FRAME_NEED) {
    for (int i = 0; i < k; i++) if (hit[i] && a.setBlock(wn, FRAME[i * 3], FRAME[i * 3 + 1], FRAME[i * 3 + 2], "")) n++;
  }
  st.frameDone = true;
  saveProps(owner, new String[] { "portal.frame" }, new String[] { "gone" });
  if (n > 0) { FRAMES.incrementAndGet(); a.relight(wn); }
  return n;
}""")
# the socket while broken / the pad once repaired, re-checked every 30 s (only over the smooth brick, air, or the other of the two)
M(ilif, r"""
public static int portalBlocks(String wn, @PKG@.IsleState st, String owner, long now) {''')
rep('''  if (PAD.equals(b)) {            // fix (c): the pad in the socket = repaired, even when the portal=1 write was lost
    st.portal = true;
''', '''  if (PAD.equals(b)) {            // fix (c): the pad in the socket = repaired, even when the portal=1 write was lost
    st.portal = true;
    padTurn(wn, st);               // 0.5.13: the pad faces the way players walk in
    frameClear(wn, owner, st);     // 0.5.13: no big frame
''')
rep('''  int n = a.setBlock(wn, SOCKETP[0], SOCKETP[1], SOCKETP[2], PAD) ? 1 : 0;
  for (int i = 0; i + 2 < FIX.length; i += 3) {
    String b = a.block(wn, FIX[i], FIX[i + 1], FIX[i + 2]);
    if (b != null && b.length() == 0 && a.setBlock(wn, FIX[i], FIX[i + 1], FIX[i + 2], FIX_IDS[i / 3])) n++;
  }
''', '''  int n = a.setBlock(wn, SOCKETP[0], SOCKETP[1], SOCKETP[2], PAD) ? 1 : 0;
  st.rotOk = true;                 // 0.5.13: placed with rotFor(PAD)
  n += frameClear(wn, owner, st);  // 0.5.13: no big frame - the old frame goes (only the generator's own blocks), no top filled in
''')

# ================================================================================================ island time = hub time
rep('''# the 1 s ticker (scheduler thread): one IsleTask per island world with players, never two queued for one world (10 s grace)
''', '''# 0.5.13 island time = hub time. markHeld: remember a world WE paused (memory + time.held in an island file, so a restart / unload
# mid-hold is undone on the next sync, even with the setting off)
M(ilif, r"""
public static void markHeld(String wn, boolean held) {
  if (held) HELD.put(wn, Boolean.TRUE); else HELD.remove(wn);
  String owner = @PKG@.IslandStore.ownerOf(wn);
  if (owner == null) return;
  if (held != fileHas(owner, "time.held", "1")) saveProps(owner, new String[] { "time.held" }, new String[] { held ? "1" : "0" });
}""")
M(ilif, r"""
public static boolean heldFile(String wn) {
  String owner = @PKG@.IslandStore.ownerOf(wn);
  return owner != null && fileHas(owner, "time.held", "1");
}""")
# the setting is off (or was turned off): a world we paused gets its clock back (world thread, IsleTask mode 11)
M(ilif, r"""
public static int release(String wn) {
  boolean was = HELD.remove(wn) != null;
  boolean file = heldFile(wn);
  if (!was && !file) return 0;
  @PKG@.IsleApi a = api();
  int f = a.timeFlags(wn);
  int r = 0;
  if (f >= 0 && (f & 1) != 0 && a.setTimePaused(wn, false)) r = 2;
  if (file) saveProps(@PKG@.IslandStore.ownerOf(wn), new String[] { "time.held" }, new String[] { "0" });
  return r;
}""")
# one world's clock against the hub's h (epoch ms) + its flags hf (world thread, IsleTask mode 10). Never backwards: behind -> forward to
# the hub; ahead -> held (paused) until the hub catches up, at most TIME_HOLD (islands only), else forward to the hub's next same time of
# day; a bed skip in progress is left alone; the hub's pause is mirrored on islands. Returns bit 1 = time set, bit 2 = pause changed.
M(ilif, r"""
public static int syncTime(String wn, long h, int hf) {
  if (wn == null) return 0;
  if (!@PKG@.IslandCfg.SYNC_TIME) return release(wn);
  @PKG@.IsleApi a = api();
  boolean isle = @PKG@.IslandStore.ownerOf(wn) != null;
  boolean hubPaused = (hf & 1) != 0;
  if (!isle && hubPaused) return 0;
  long i = a.gameTime(wn);
  int f = a.timeFlags(wn);
  if (i == Long.MIN_VALUE || f < 0 || h == Long.MIN_VALUE) return 0;
  if ((f & 2) != 0) return 0;
  long d = i - h;
  boolean hold = false;
  int r = 0;
  if (d + TIME_TOL < 0L) {          // (not d < -TIME_TOL: javassist folds the minus away on a static final long)
    if (a.setGameTime(wn, h)) r = r | 1;
  } else if (d > TIME_TOL) {
    long rem = d % DAY_MS;
    if (rem > TIME_TOL && rem < DAY_MS - TIME_TOL) {
      if (isle && rem <= TIME_HOLD) hold = true;
      else if (a.setGameTime(wn, i + (DAY_MS - rem))) r = r | 1;
    }
  }
  boolean want = isle && (hold || hubPaused);
  if (isle && want != ((f & 1) != 0) && a.setTimePaused(wn, want)) r = r | 2;
  if (isle) markHeld(wn, want);
  if (r != 0) SYNCS.incrementAndGet();
  return r;
}""")
# 0.5.13 review: the hub's clock cannot be read (hub world unloaded / not set) -> the worlds WE paused get their clocks back (mode 11)
M(ilif, r"""
public static int releaseHeld(String[] ws) {
  if (ws == null) return 0;
  @PKG@.IsleApi a = api();
  int n = 0;
  for (int i = 0; i < ws.length; i++) {
    if (ws[i] == null || (!HELD.containsKey(ws[i]) && !heldFile(ws[i]))) continue;
    if (a.exec(ws[i], new @PKG@.IsleTask(11, ws[i], null))) n++;
  }
  return n;
}""")
# the hub's thread (IsleTask mode 12): read the hub's clock once, hand it to each due world's own thread
M(ilif, r"""
public static int timeHub(String hub, String[] ws) {
  HUBQ = 0L;
  @PKG@.IsleApi a = api();
  long h = a.gameTime(hub);
  int hf = a.timeFlags(hub);
  if (ws == null) return 0;
  if (h == Long.MIN_VALUE || hf < 0) { releaseHeld(ws); return 0; }
  int n = 0;
  for (int i = 0; i < ws.length; i++) {
    @PKG@.IsleTask t = new @PKG@.IsleTask(10, ws[i], null);
    t.ms = h;
    t.fl = hf;
    if (a.exec(ws[i], t)) n++;
  }
  return n;
}""")
# the 1 s ticker (scheduler thread): island / shard worlds with players not synced for TIME_GAP -> one hub task (never two queued)
M(ilif, r"""
public static int timeAll(long now) {
  @PKG@.IsleApi a = api();
  java.util.Iterator it = a.timeWorlds().iterator();
  java.util.ArrayList due = new java.util.ArrayList();
  String hub = a.hubWorld();
  while (it.hasNext()) {
    String wn = (String) it.next();
    if (wn == null || wn.equals(hub)) continue;
    Object t = TIME_AT.get(wn);
    if (t instanceof Long && now - ((Long) t).longValue() >= 0L && now - ((Long) t).longValue() < TIME_GAP) continue;
    if (!@PKG@.IslandCfg.SYNC_TIME && !HELD.containsKey(wn) && !heldFile(wn)) continue;
    due.add(wn);
  }
  if (due.isEmpty()) return 0;
  if (@PKG@.IslandCfg.SYNC_TIME && hub != null && HUBQ != 0L && now - HUBQ >= 0L && now - HUBQ < 10000L) return 0;
  if (TIME_AT.size() > 4096) TIME_AT.clear();
  for (int i = 0; i < due.size(); i++) TIME_AT.put(due.get(i), Long.valueOf(now));
  String[] ws = new String[due.size()];
  for (int i = 0; i < ws.length; i++) ws[i] = (String) due.get(i);
  if (!@PKG@.IslandCfg.SYNC_TIME || hub == null) return releaseHeld(ws);   // off, or no hub (review: never paused forever)
  @PKG@.IsleTask t = new @PKG@.IsleTask(12, hub, null);
  t.ks = ws;
  HUBQ = now;
  if (!a.exec(hub, t)) { HUBQ = 0L; return releaseHeld(ws); }               // the hub world is not loaded
  return ws.length;
}""")
# the 1 s ticker (scheduler thread): one IsleTask per island world with players, never two queued for one world (10 s grace)
''')
rep('''    if (a.exec(wn, new @PKG@.IsleTask(0, wn, null))) n++; else QUEUED.remove(wn);
  }
  return n;
}""")''', '''    if (a.exec(wn, new @PKG@.IsleTask(0, wn, null))) n++; else QUEUED.remove(wn);
  }
  try { timeAll(now); } catch (Throwable t) { warnOnce("time", "island time sync failed (logged once): " + t); }   // 0.5.13
  return n;
}""")''')
rep('''    if (this.mode == 0) { @PKG@.IsleLife.tickWorld(this.wn); @PKG@.IsleLife.QUEUED.remove(this.wn); return; }
''', '''    if (this.mode == 0) { @PKG@.IsleLife.tickWorld(this.wn); @PKG@.IsleLife.QUEUED.remove(this.wn); return; }
    if (this.mode == 10) { @PKG@.IsleLife.syncTime(this.wn, this.ms, this.fl); return; }     // 0.5.13 island time = hub time
    if (this.mode == 11) { @PKG@.IsleLife.release(this.wn); return; }
    if (this.mode == 12) { @PKG@.IsleLife.timeHub(this.wn, this.ks); return; }
''')

# ================================================================================================ the ready line
rep('''+ ", hooks " + @PKG@.IsleLife.HOOKS + "/3, "''',
    '''+ ", island time = hub time " + (@PKG@.IslandCfg.SYNC_TIME ? "on" : "off") + ", start on your island " + (@PKG@.IslandCfg.ISLAND_LOGIN ? "on" : "off") + ", camp stops after the quest " + (@PKG@.IslandCfg.CAMP_STOP ? "on" : "off") + ", hooks " + @PKG@.IsleLife.HOOKS + "/3, "''')

# ================================================================================================ checks on the result
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0
_i = s.index
assert _i("S3_FRAME = []") < _i("def s3_layout():") < _i("    del S3_FRAME[:]") < _i("S3_L, S3_PLACES, S3_TOPS, S3_ISLE = s3_layout()") < _i("S3_P2 = s3_part2(")
assert _i("public static int rotFor(String id)") < _i("public boolean setBlock(String wn, int x, int y, int z, String id) {")
assert _i("public static boolean campDone(") < _i("public static int campTick(")
assert _i("public static int padTurn(") < _i("public static int frameClear(") < _i("public static int portalBlocks(") < _i("public static int repair(")
assert _i("public static int releaseHeld(") < _i("public static int timeHub(") and _i("public static boolean keep(String wn)") < _i("public static int decide(String wn")
assert _i("public static int syncTime(") < _i("public static int timeHub(") < _i("public static int timeAll(") < _i("public static int tickAll()") < _i("if (this.mode == 10)")
assert _i("public static int decide(String wn") < _i("public static boolean hubPref(") < _i("    int d = decide(wn, home")
assert _i('"V3DC":  "org.joml.Vector3dc",') < _i('"WTR":   "com.hypixel') < _i("public long gameTime(String wn)")
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.5.12 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.5.12 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
