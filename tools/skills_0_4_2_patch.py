"""Derive SkyySkills/build_skyyskills_0.4.2.py from 0.4.1 (same style as skills_0_4_1_patch.py: rep(old, new) with asserted single anchors,
newline-agnostic; 0.4.1 stays untouched, its CRLF line endings are preserved). Edit THIS file, not the generated script.
0.4.2 = feedback round 2, stage 1 (HANDOFF 2026-09-24 07:05 queue):
 - research/Tree-Fall-Spec.md, the SkyySkills parts (sections 2, 3.1, 4): a felled tree pays every log that falls to the player whose
   cut made it fall - snapshot of the natural tree inside the BreakSys handler, commit first thing in BreakTask, FellWatch polls the
   claimed positions (scheduler hop -> world thread), FellCredit pays Foraging XP x fell.xpFactor (leaves x fell.leafXpFactor), a
   double-drop roll, SkyyCollections via coll:fn:add source "skills:felled", the per-log tree nodes through the NEW listener map
   skill:on:felled, and remembers the feller for skill:fn:felledBy. EnvSys (WorldEventSystem on EnvironmentBreakBlockEvent) unclaims
   positions taken by explosions / fire. Claims / layer / takeover rules of spec 2.4, watch end rules of 2.5, preconditions of 2.6,
   config block + clamps of 3.1 (appended once to an existing xp.properties), the handler-read fallback of 3.1, the sapling placed-tracker
   fix of 3.1 (placed.skipSaplings) and the optional skills:double count of 2.8 (collections.doubleDrops, default OFF).
 - Stats page scaled ~1.5x (Skyy: "scale the Stats page up"): root 960 x 795 (was 640 x 530), fonts 16/11/13/12/10 -> 24/17/20/18/15,
   bar 600 x 18, buttons 195 x 45 with 18 pt labels; every how-to line wraps (2 lines at 15 pt).
0.4.2 stage 2 (same version, appended below the stage 1 edits - everything stage 1 did is kept):
 - research/Double-Jump-Spec.md 3.2, the SkyySkills part: Acro.airJump in AcroSys.tick (world thread, every tick, after Acro.move and
   before Acro.dodge), split into the pure airTrack (edges + airtime) / airTry (gates + push speed) and the engine glue airJump; the
   acro.doubleJump.* block (trigger crouch | jump | both, default crouch; debug chat lines for spec test 5.0), appended once; bridge
   skill:dj:key for the SkyyTrees 0.2.1 card; Stats page "double jump 55%" + a Double Jump line.
 - PARTY COMBAT XP (beta backlog 6, Skyy: "party should share combat XP"): PartyXp.share after the killer's normal kill award - every
   OTHER party member (party:fn:members, SkyyParty 0.1.3) online, in the same world, ready, alive, not in creative and within
   party.combatShare.radius (48) blocks gets party.combatShare.fraction (0.5) of the killer's base kill XP in THEIR OWN current class
   skill (their profile; only the killer needs a class weapon); the killer keeps 100 %; a batched "[Party] +6 Archery XP ..." chat line
   throttled like the other XP lines; the party.combatShare.* block, appended once.
 - stage 2 review fixes: the acro.doubleJump.debug probe runs before the acro.doubleJump.enabled gate; airTrack restarts the airtime
   in every other Acro.excludedState (flying / gliding / mounted / sitting / sleeping) but keeps the charge (spec 2.3 rule 2); airJump's
   coarse gate is trigger-aware (djTrig); the party share goes through SkillXp.gain4 (gain3 + the party note) so the [Party] line
   prints before the SKILL LEVEL UP it causes (the PartyXp chat methods are compiled before SkillXp for that).
Run:  python tools/skills_0_4_2_patch.py   then   python SkyySkills/build_skyyskills_0.4.2.py   (NO --deploy: coordinated deploy)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.1.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.2.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.1"
s = raw.decode("utf8").replace("\r\n", "\n")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:100]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:100])
    s = s.replace(old, new)


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


def rep_between(start, end, new):
    """replace s[start .. end inclusive] (both anchors unique, end after start)"""
    global s
    assert s.count(start) == 1, "start anchor count %d: %s" % (s.count(start), start[:100])
    i = s.index(start)
    j = s.index(end, i)
    assert s.count(end) == 1, "end anchor count %d: %s" % (s.count(end), end[:100])
    s = s[:i] + new + s[j + len(end):]


# ================================================================ header / version
rep('''"""SkyySkills 0.4.1 - build script (derived from 0.4 by tools/skills_0_4_1_patch.py - edit the patch, not this file;
0.4 was derived from 0.3.2 by tools/skills_0_4_patch.py, 0.3.2 from 0.3.1 by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by
tools/skills_0_3_patch.py)
0.4.1 (research/Exploration-Build-Spec.md''', '''"""SkyySkills 0.4.2 - build script (derived from 0.4.1 by tools/skills_0_4_2_patch.py - edit the patch, not this file;
0.4.1 was derived from 0.4 by tools/skills_0_4_1_patch.py, 0.4 from 0.3.2 by tools/skills_0_4_patch.py, 0.3.2 from 0.3.1 by
tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.2 (research/Tree-Fall-Spec.md sections 2, 3.1 and 4 - FELLED TREES; + the Stats page 1.5x). Pairs with SkyyCollections 0.2.1
  (source skills:felled) and SkyyTrees 0.2.1 (same-Y Tree Feller, per-log nodes on skill:on:felled); every mix loads and is safe (spec 3.4).
  WHY: only the block a player breaks fires BreakBlockEvent; Hytale's block physics then removes the rest of the tree one pass at a time
  with no event and no player, so a felled tree paid 1 log (6 XP, Collections +1). Now every log that FALLS is paid to the feller.
  1 SNAPSHOT (BreakSys handler, synchronous, the tree is still standing): trigger TRUNK (a TreeWood _Trunk / _Trunk_Full id), BRANCH
    (_Branch_Short/_Long/_Corner) or UNDER (any other block - not leaves / roots - with a TreeWood trunk right above it, fell.underTrunk).
    Breadth-first search over the 26-neighbourhood: same-family wood (FellDefs: TreeWood.json / TreeLeaves.json generated from Assets.zip
    at build time), natural only (not in PlacedStore, not BlockPhysics.isDeco), |dx|,|dz| <= fell.radius, y <= y0 + fell.height; trunks
    y >= y0, branches / roots y >= y0 - 1 (BRANCH trigger: branches only). Trunks ON y0 are the LAYER (the other base logs of a thick
    tree: only cut, never claimed) but stay search nodes. Leaves: 26 neighbours of accepted wood, then up to 4 leaf steps, y >= y0 - 1
    (claims only with fell.leaves; always used for the natural-tree test fell.needLeaves). Caps fell.maxLogs / fell.maxLeaves /
    fell.maxReads (per-section cache), fell.maxSnapshotsPerSecond per player. Creative / fell.disabledWorlds: no snapshot.
    Fallback (spec 3.1): if a block read inside the handler throws, the log warns once and every later snapshot is taken in BreakTask
    instead, stepping through up to 2 empty cells straight above the seed.
  2 COMMIT (BreakTask, first thing after the cancel check, BEFORE XP and skill:on:gather - the Tree Feller breaks inside gather):
    dropped without natural leaves (needLeaves), without claims, over fell.maxWatchesPerPlayer / fell.maxWatches. Claim takeover
    (spec 2.4): a claim is taken when free / dead / the same player's, or from another player when this cut was not itself on their
    falling part (the last-support rule); the layer keys map to the new watch. A cancelled break (island protection) puts back a claim
    its handler removed and discards the snapshot.
  HAND BREAKS: a break on a claimed position unclaims it (paid by the normal hand path, never also as felled); the same player's break
    on their own claim / layer only touches that watch (no new search) - so the Tree Feller's extra base breaks never search again.
  3 WATCH (FellWatch, HarvestTask hop pattern every fell.pollMs): a claimed position whose block index turned 0 (air) and is still
    held by this watch = FELLED; -1 (chunk gone) = lost, another block = replaced (no credit). Ends when all resolved, fell.quietMs
    without a change (touch() counts), fell.maxWatchMs, or the owner went offline; releases its claims / layer entries; optional
    "Tree felled: 19 logs, 42 leaves (+156 Foraging XP)" line (fell.message, hidden by /skills quiet); fell.debug = one log line per
    watch (claims, credited, hand, env, lost, other, replaced, skipped, dropped, collections, xp, ms) and one per snapshot (reads, us).
  4 CREDIT (FellCredit.one, world thread) only while the owner is online, on the snapshot's profile (pkey), not profile:busy, in the
    tree's world and not in creative: Foraging XP = the hand-break table (SkillCfg.classifyBreak, global multiplier) x fell.xpFactor
    (leaves x fell.leafXpFactor), + the skill-tree XP bonus (Foraging Wisdom) through the normal award path ("+XP" lines, level ups,
    coins); Perks.breakDouble (fell.doubleDrops; perk.foraging.doubleDropOnly=_Trunk keeps it to trunks); SkyyCollections: the
    ENGINE's physics drop selection (Physics, else Breaking (quantity), else Soft, else Harvest) re-rolled with BlockHarvestUtils.getDrops,
    each stack -> coll:fn:add Object[]{UUID, itemId, Long qty, "skills:felled", pkey} (fell.collections; SkyyCollections 0.2.1 accepts
    the source by default, 0.2 only if an admin adds it to bridge.add.sources); skill:on:felled listeners (fell.nodes, only for blocks
    the XP table knows); the "felled by" memory. A rule-less block still counts in Collections, gets no XP / double drop / nodes.
  EXPLOSIONS / FIRE: EnvSys (WorldEventSystem, EnvironmentBreakBlockEvent - fired by explosions before the removal and by fire right
    after its setBlock, both on the entity store, bytecode-checked) removes a claimed position: never paid as felled. If EnvSys cannot
    be registered the log warns and the fell feature stays OFF until the next restart (FellCfg.BROKEN; /skills reload does not help).
  BRIDGE: skill:on:felled = ConcurrentHashMap name -> Function (putIfAbsent in setup, left in place at shutdown), called once per
    credited position with Object[]{PlayerRef, Integer row, BlockType, String world, Integer x, Integer y, Integer z, String pkey}, each
    listener in its own try/catch, a failure logged once per listener; a SEPARATE map from skill:on:gather, so SkyyTrees 0.1 / 0.2 never
    see felled logs. skill:fn:felledBy apply(Object[]{String world, Integer x, Integer y, Integer z}) -> Object[]{UUID owner, String
    pkey, Long atMillis, String "falling" | "felled"} or null (any thread; "felled" is remembered fell.memoryMs, 8192 per world).
  CONFIG: the "Felled trees" block (fell.* + placed.skipSaplings + collections.doubleDrops) is in a fresh xp.properties and appended
    ONCE to an existing file without fell.enabled (FellCfg.ensureDefaults); /skills reload re-reads it; clamps pollMs 50-1000,
    quietMs 500-10000, radius 1-16, height 1-128, maxLogs 1-1024, maxLeaves 0-2048, factors 0-5 (+ sane bounds for the rest).
    Skyy decisions left as switches (spec section 6): fell.extraTrees=false (apple fruit trees + the Bamboo / Ice Trunk_Full blocks
    that Hytale's tree lists miss), placed.skipSaplings=true (a planted sapling is not recorded as placed, so the base log of a replanted
    tree pays - the spec's recommended fix), collections.doubleDrops=false (double-drop items counted in Collections, hand breaks too).
  STATS PAGE 1.5x: root 960 x 795 (fits a 1080-high screen), title 24 pt, sub 17, headers 20, lines 18 (28 high), how-to 15 pt wrapped,
    bar 600 x 18, buttons 195 x 45 (18 pt). The Foraging how-to says felled trees pay every falling log (while the feature is on).
  CHECKED in a bare JVM (2026-09-24, scratch harness under tools/dev/scratch, deleted afterwards): all 68 classes pass -Xverify:all;
    FellCfg defaults / clamps / disabledWorlds / ensureDefaults (appends once, no-op when fell.enabled exists); FellDefs ids (apple only
    with fell.extraTrees); the search through the FellRead test seam: 1-wide birch (19 logs + every leaf claimed, the cut log not),
    leaves off, a mid-trunk cut, UNDER (20 logs incl. the seed), UNDER without a trunk, a deco tower (nothing, no natural leaves), a
    PlacedStore log never claimed, 2x2 (layer 3, 64 logs above), a flared base (wood above a far base log claimed through layer nodes),
    BRANCH trigger (branches only), the read budget, touching same-family trees join / another family excluded, the late fallback (up
    to 2 empty cells), the 10/s rate limit; claims: commit, a hand break by another player (inOther) and by the owner (reuse), layer
    reuse, cancelled-break restore, a cut inside another player's fall keeps their claims, the last-support cut takes them, EnvSys
    unclaim, felledBy falling / felled / null, end releases, the needLeaves drop, maxWatchesPerPlayer 4, endAll; the Stats page markup
    for 9 skills (root 960 x 795, unique ids without underscores, content <= 752 px incl. padding).
    Test seams (harness only; null / false in the game): FellRead.TEST, FellRead.TESTDECO, Fell.TEST_NO_SCHEDULE.
  UNVERIFIED (needs the game): block reads inside the BreakBlockEvent handler (spec T1; a throw switches to the late fallback), the
    cascade timing vs fell.quietMs (T14), EnvSys registration and delivery (T17), FellCredit end to end with a real player (XP, double
    drops, coll:fn:add, skill:on:felled), the scheduler hop, the Stats page on a real client at 1.5x.
0.4.1 (research/Exploration-Build-Spec.md''')
rep('''Run:   python build_skyyskills_0.4.1.py            -> SkyySkills/SkyySkills-0.4.1.jar
       python build_skyyskills_0.4.1.py --deploy   -> also copies''', '''Run:   python build_skyyskills_0.4.2.py            -> SkyySkills/SkyySkills-0.4.2.jar
       python build_skyyskills_0.4.2.py --deploy   -> also copies''')
rep('VERSION = "0.4.1"', 'VERSION = "0.4.2"')

# ================================================================ API names + probes (0.4.2, checked with tools/dev reflect.py / bcfull.py)
after('''CMGR= "com.hypixel.hytale.server.core.command.system.CommandManager"      # 0.4 trees bridge: the Tree buttons run /tree <skill>
''', '''# 0.4.2 felled trees (tools/dev reflect.py + bcfull.py against HytaleServer.jar 2026-09-24; research/Tree-Fall-Spec.md 1.3 / 2.4 / 3.1)
WES = "com.hypixel.hytale.component.system.WorldEventSystem"                  # C(Class), handle(Store, CommandBuffer, EcsEvent)
EBE = "com.hypixel.hytale.server.core.event.events.ecs.EnvironmentBreakBlockEvent"   # getTargetBlock(), getBlockType()
BPH = "com.hypixel.hytale.server.core.blocktype.component.BlockPhysics"       # chunk-section component: isDeco(x, y, z)
PDT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.PhysicsDropType"
CKU = "com.hypixel.hytale.math.util.ChunkUtil"                                # BITS = 5 (32-block sections), HEIGHT = 320
''')
after('''for c, m in ((CMGR, "get"), (CMGR, "handleCommand"), ("java.util.Map", "putIfAbsent"), ("java.lang.Double", "isNaN")):
    B.probe(pool, c, m)
''', '''for c, m in ((WES, "handle"), (EBE, "getTargetBlock"), (EBE, "getBlockType"), (BPH, "getComponentType"), (BPH, "isDeco"),
             (BGA, "getPhysics"), (PDT, "getItemId"), (PDT, "getDropListId"), (CKU, "BITS"), (CKU, "HEIGHT"), (PBE, "getItemInHand"),
             (BHU, "getDrops"), (WLD, "getChunkStore"), (PR, "getWorldUuid"), (UNI, "getWorld"), ("java.util.concurrent.ConcurrentHashMap", "remove"),
             ("java.lang.System", "arraycopy"), ("java.util.Arrays", "asList")):
    B.probe(pool, c, m)
''')

# ================================================================ xp.properties: the Felled trees block + the tree lists (spec 2.2 / 3.1)
after('''EXPL_LIT = json.dumps(EXPL_DEFAULTS)
''', r'''# 0.4.2: felled trees (research/Tree-Fall-Spec.md 3.1). Also appended once to an existing xp.properties that has no fell.enabled key
# (FellCfg.ensureDefaults); the code defaults in FellCfg are the same numbers.
FELL_L = []
FELL_L.append("# ---------- Felled trees (SkyySkills 0.4.2): every log that falls because you cut the tree pays like a hand-broken log ----------")
FELL_L.append("# Comments must stay on their own lines.")
FELL_L.append("# Hytale fells a tree when its base is cut, but only the block you break fires an event. SkyySkills remembers the natural")
FELL_L.append("# tree at that moment and pays each log (and leaf) that then falls to the player who cut it: Foraging XP x fell.xpFactor")
FELL_L.append("# (leaves x fell.leafXpFactor), a double-drop roll, a SkyyCollections count (source skills:felled) and the per-log")
FELL_L.append("# skill-tree rolls (skill:on:felled). Placed logs never fall and never pay. Explosions and fire never pay as felled.")
FELL_L.append("fell.enabled=true")
FELL_L.append("fell.xpFactor=1.0")
FELL_L.append("fell.leaves=true")
FELL_L.append("fell.leafXpFactor=1.0")
FELL_L.append("# needLeaves: only a tree that touches natural leaves pays (a log wall or a placed log tower never does)")
FELL_L.append("fell.needLeaves=true")
FELL_L.append("# underTrunk: digging out the block under a trunk fells the tree too - it pays the same")
FELL_L.append("fell.underTrunk=true")
FELL_L.append("fell.doubleDrops=true")
FELL_L.append("fell.collections=true")
FELL_L.append("fell.nodes=true")
FELL_L.append("# message: one 'Tree felled: 19 logs, 42 leaves (+156 Foraging XP)' line per tree (/skills quiet hides it)")
FELL_L.append("fell.message=true")
FELL_L.append("# worlds where felled trees never pay, comma separated exact world names")
FELL_L.append("fell.disabledWorlds=")
FELL_L.append("# search limits: blocks sideways from the cut, blocks above it, logs, leaves, block reads per tree")
FELL_L.append("fell.radius=8")
FELL_L.append("fell.height=64")
FELL_L.append("fell.maxLogs=256")
FELL_L.append("fell.maxLeaves=384")
FELL_L.append("fell.maxReads=8000")
FELL_L.append("fell.maxSnapshotsPerSecond=10")
FELL_L.append("fell.maxWatchesPerPlayer=4")
FELL_L.append("fell.maxWatches=64")
FELL_L.append("# milliseconds: how often a falling tree is checked, how long it may stay still before the watch ends, the longest watch,")
FELL_L.append("# how long 'who felled this' is remembered for other mods (skill:fn:felledBy)")
FELL_L.append("fell.pollMs=200")
FELL_L.append("fell.quietMs=3000")
FELL_L.append("fell.maxWatchMs=60000")
FELL_L.append("fell.memoryMs=60000")
FELL_L.append("# debug: one server-log line per snapshot and per felled tree (claims, credited, hand, env, lost, ms) - measures the fall timing")
FELL_L.append("fell.debug=false")
FELL_L.append("# Skyy decisions (research/Tree-Fall-Spec.md section 6):")
FELL_L.append("# extraTrees: also pay felled apple fruit trees and the Bamboo / Ice Trunk_Full blocks (Hytale's tree lists miss them)")
FELL_L.append("fell.extraTrees=false")
FELL_L.append("# skipSaplings: a sapling you plant is not recorded as a placed block, so the base log of a replanted tree pays when broken")
FELL_L.append("placed.skipSaplings=true")
FELL_L.append("# doubleDrops: items from the double-drop perk also count in SkyyCollections (source skills:double) - hand breaks too")
FELL_L.append("collections.doubleDrops=false")
L.append("")
L.extend(FELL_L)
FELL_DEFAULTS = "\n".join(FELL_L) + "\n"
assert all(ord(ch) < 128 for ch in FELL_DEFAULTS) and '"' not in FELL_DEFAULTS
FELL_LIT = json.dumps(FELL_DEFAULTS)
# the engine's own tree lists (spec 2.2): Server/BlockTypeList/TreeWood.json (Wood_<W>_<Trunk|Trunk_Full|Branch_*|Roots>) and TreeLeaves.json
with zipfile.ZipFile(ASSETS) as z:
    TREE_WOOD = sorted(json.loads(z.read("Server/BlockTypeList/TreeWood.json").decode("utf8"))["Blocks"])
    TREE_LEAVES = sorted(json.loads(z.read("Server/BlockTypeList/TreeLeaves.json").decode("utf8"))["Blocks"])
FELL_SUFFIXES = ["_Trunk_Full", "_Trunk", "_Branch_Short", "_Branch_Long", "_Branch_Corner", "_Roots"]
assert len(TREE_WOOD) >= 150 and len(TREE_LEAVES) >= 30, (len(TREE_WOOD), len(TREE_LEAVES))
for _i in TREE_WOOD:
    assert _i.startswith("Wood_") and any(_i.endswith(_x) for _x in FELL_SUFFIXES), "unexpected TreeWood id " + _i
for _i in TREE_LEAVES:
    assert _i.startswith("Plant_Leaves_"), "unexpected TreeLeaves id " + _i
for _i in TREE_WOOD + TREE_LEAVES:
    assert all(ord(ch) < 128 for ch in _i) and '"' not in _i and "\\" not in _i
# fell.extraTrees (Skyy decision, spec 2.2 / 6.7): ids the engine lists miss - only those that really exist as block items
FELL_EXTRA_WOOD = [i for i in ("Wood_Apple_Trunk", "Wood_Apple_Trunk_Full", "Wood_Apple_Branch_Short", "Wood_Apple_Branch_Long",
                               "Wood_Apple_Branch_Corner", "Wood_Apple_Roots", "Wood_Bamboo_Trunk_Full", "Wood_Ice_Trunk_Full")
                   if i in ITEM_IDS and i not in TREE_WOOD]
FELL_EXTRA_LEAVES = [i for i in ("Plant_Leaves_Apple",) if i in ITEM_IDS and i not in TREE_LEAVES]
assert "Wood_Apple_Trunk" in FELL_EXTRA_WOOD and FELL_EXTRA_LEAVES == ["Plant_Leaves_Apple"], (FELL_EXTRA_WOOD, FELL_EXTRA_LEAVES)
print("felled trees: %d wood ids, %d leaf ids (+ extraTrees %d / %d)" % (len(TREE_WOOD), len(TREE_LEAVES), len(FELL_EXTRA_WOOD), len(FELL_EXTRA_LEAVES)))
''')

# ================================================================ classes
after('''exc  = pool.makeClass(PKG + ".ExplCfg")
''', '''# 0.4.2 felled trees (research/Tree-Fall-Spec.md 3.1)
fcf  = pool.makeClass(PKG + ".FellCfg")
fdf  = pool.makeClass(PKG + ".FellDefs")
frd  = pool.makeClass(PKG + ".FellRead")
fsn  = pool.makeClass(PKG + ".FellSnap")
fwt  = pool.makeClass(PKG + ".FellWatch")
fel  = pool.makeClass(PKG + ".Fell")
fdr  = pool.makeClass(PKG + ".FellDrops")
fcr  = pool.makeClass(PKG + ".FellCredit")
ffn  = pool.makeClass(PKG + ".FelledByFn")
esy  = pool.makeClass(PKG + ".EnvSys", pool.get(WES))
''')

# ================================================================ FellCfg (before BridgeCfg: SkillCfg.load calls it)
before('''# ================= BridgeCfg (0.4): bridge.* keys (skill:fn:addxp / skill:fn:craftxp) =================
''', r'''# ================= FellCfg (0.4.2): the Felled trees block of xp.properties (research/Tree-Fall-Spec.md 3.1) =================
# Read by SkillCfg.load (so /skills reload re-reads it), appended ONCE to an existing file without fell.enabled (the AlchCfg pattern; the
# code defaults are the same numbers). BROKEN = EnvSys could not be registered: the feature stays off until the next restart (spec 2.4).
# CODE / FAM (block index -> kind / family) and IDCODE / IDFAM (block id -> kind / family) are FellDefs' caches; cleared by read()
# because fell.extraTrees changes what counts as a tree.
fcf.addField(CtField.make("public static final String DEFAULTS = " + FELL_LIT + ";", fcf))
for decl in ("boolean ENABLED = true", "boolean BROKEN = false", "double XP_FACTOR = 1.0", "boolean LEAVES = true", "double LEAF_XP_FACTOR = 1.0",
             "boolean NEED_LEAVES = true", "boolean UNDER_TRUNK = true", "boolean DOUBLE_DROPS = true", "boolean COLLECTIONS = true",
             "boolean NODES = true", "boolean MESSAGE = true", "int RADIUS = 8", "int HEIGHT = 64", "int MAX_LOGS = 256", "int MAX_LEAVES = 384",
             "int MAX_READS = 8000", "int MAX_SNAPS = 10", "int MAX_PER_PLAYER = 4", "int MAX_WATCHES = 64", "long POLL_MS = 200L",
             "long QUIET_MS = 3000L", "long MAX_WATCH_MS = 60000L", "long MEMORY_MS = 60000L", "boolean DEBUG = false",
             "boolean EXTRA_TREES = false", "boolean SKIP_SAPLINGS = true", "boolean DD_COLLECTIONS = false",
             "java.util.HashSet DISABLED = new java.util.HashSet()"):
    fcf.addField(CtField.make("public static volatile " + decl + ";", fcf))
for nm in ("CODE", "FAM", "IDCODE", "IDFAM"):
    fcf.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap " + nm + " = new java.util.concurrent.ConcurrentHashMap();", fcf))
fcf.addMethod(CtNewMethod.make("""
public static boolean on() {
  return ENABLED && !BROKEN;
}""", fcf))
fcf.addMethod(CtNewMethod.make("""
public static long clampL(long v, long lo, long hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}""", fcf))
fcf.addMethod(CtNewMethod.make("""
public static double clampD(double v, double lo, double hi) {
  if (Double.isNaN(v) || v < lo) return lo;
  if (v > hi) return hi;
  return v;
}""", fcf))
fcf.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ENABLED = {PKG}.SkillCfg.bool(p, "fell.enabled", true);
  XP_FACTOR = clampD({PKG}.SkillCfg.dbl(p, "fell.xpFactor", 1.0), 0.0, 5.0);
  LEAVES = {PKG}.SkillCfg.bool(p, "fell.leaves", true);
  LEAF_XP_FACTOR = clampD({PKG}.SkillCfg.dbl(p, "fell.leafXpFactor", 1.0), 0.0, 5.0);
  NEED_LEAVES = {PKG}.SkillCfg.bool(p, "fell.needLeaves", true);
  UNDER_TRUNK = {PKG}.SkillCfg.bool(p, "fell.underTrunk", true);
  DOUBLE_DROPS = {PKG}.SkillCfg.bool(p, "fell.doubleDrops", true);
  COLLECTIONS = {PKG}.SkillCfg.bool(p, "fell.collections", true);
  NODES = {PKG}.SkillCfg.bool(p, "fell.nodes", true);
  MESSAGE = {PKG}.SkillCfg.bool(p, "fell.message", true);
  RADIUS = (int) clampL({PKG}.SkillCfg.lng(p, "fell.radius", 8L), 1L, 16L);
  HEIGHT = (int) clampL({PKG}.SkillCfg.lng(p, "fell.height", 64L), 1L, 128L);
  MAX_LOGS = (int) clampL({PKG}.SkillCfg.lng(p, "fell.maxLogs", 256L), 1L, 1024L);
  MAX_LEAVES = (int) clampL({PKG}.SkillCfg.lng(p, "fell.maxLeaves", 384L), 0L, 2048L);
  MAX_READS = (int) clampL({PKG}.SkillCfg.lng(p, "fell.maxReads", 8000L), 100L, 100000L);
  MAX_SNAPS = (int) clampL({PKG}.SkillCfg.lng(p, "fell.maxSnapshotsPerSecond", 10L), 1L, 100L);
  MAX_PER_PLAYER = (int) clampL({PKG}.SkillCfg.lng(p, "fell.maxWatchesPerPlayer", 4L), 1L, 64L);
  MAX_WATCHES = (int) clampL({PKG}.SkillCfg.lng(p, "fell.maxWatches", 64L), 1L, 1024L);
  POLL_MS = clampL({PKG}.SkillCfg.lng(p, "fell.pollMs", 200L), 50L, 1000L);
  QUIET_MS = clampL({PKG}.SkillCfg.lng(p, "fell.quietMs", 3000L), 500L, 10000L);
  MAX_WATCH_MS = clampL({PKG}.SkillCfg.lng(p, "fell.maxWatchMs", 60000L), 1000L, 600000L);
  MEMORY_MS = clampL({PKG}.SkillCfg.lng(p, "fell.memoryMs", 60000L), 0L, 600000L);
  DEBUG = {PKG}.SkillCfg.bool(p, "fell.debug", false);
  EXTRA_TREES = {PKG}.SkillCfg.bool(p, "fell.extraTrees", false);
  SKIP_SAPLINGS = {PKG}.SkillCfg.bool(p, "placed.skipSaplings", true);
  DD_COLLECTIONS = {PKG}.SkillCfg.bool(p, "collections.doubleDrops", false);
  java.util.HashSet ds = new java.util.HashSet();
  String dw = p.getProperty("fell.disabledWorlds");
  if (dw != null) {{
    String[] ps = dw.split(",");
    for (int i = 0; i < ps.length; i++) {{
      String t = ps[i].trim().toLowerCase(java.util.Locale.ROOT);
      if (t.length() > 0) ds.add(t);
    }}
  }}
  DISABLED = ds;
  CODE.clear();
  FAM.clear();
  IDCODE.clear();
  IDFAM.clear();
}}""", fcf))
fcf.addMethod(CtNewMethod.make("""
public static boolean worldOk(String w) {
  if (w == null) return false;
  java.util.HashSet d = DISABLED;
  return d.isEmpty() || !d.contains(w.toLowerCase(java.util.Locale.ROOT));
}""", fcf))
fcf.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  if (p.getProperty("fell.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Felled trees section (fell.*, placed.skipSaplings, collections.doubleDrops - default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Felled trees section to xp.properties: " + t); }}
}}""", fcf))
fcf.addMethod(CtNewMethod.make("""
public static String text() {
  if (BROKEN) return "OFF (the explosion / fire guard EnvSys could not be registered - see the warning above)";
  if (!ENABLED) return "off (fell.enabled=false)";
  return "on (XP x" + XP_FACTOR + (LEAVES ? ", leaves x" + LEAF_XP_FACTOR : ", leaves not paid") + (DOUBLE_DROPS ? ", double drops" : "") + (COLLECTIONS ? ", collections" : "") + (EXTRA_TREES ? ", + apple trees" : "") + ")";
}""", fcf))

''')
after('''    {PKG}.ExplCfg.ensureDefaults(p);
''', '''    {PKG}.FellCfg.ensureDefaults(p);
''')
after('''    {PKG}.ExplCfg.read(p);
''', '''    {PKG}.FellCfg.read(p);
''')
rep('''", exploration " + ({PKG}.ExplCfg.ENABLED ? "on (no boosters)" : "off") + ", bridge skills "''',
    '''", exploration " + ({PKG}.ExplCfg.ENABLED ? "on (no boosters)" : "off") + ", felled trees " + {PKG}.FellCfg.text() + ", bridge skills "''')

# ================================================================ SkillBonus.felled: the skill:on:felled listener map (spec 2.8)
before('''
# ================= SkillXp: award + level-up (world thread) =================
''', r'''# 0.4.2 (Tree-Fall-Spec 2.8): skill:on:felled - a SEPARATE map from skill:on:gather (an old SkyyTrees never sees felled logs and can never
# start an ability from one). World thread, once per credited felled position, after its XP and double drop; every listener gets its own
# argument array Object[]{PlayerRef, Integer row, BlockType, String world, Integer x, Integer y, Integer z, String pkey} and its own
# try/catch; a failure is logged once per listener.
sbn.addMethod(CtNewMethod.make(f"""
public static void failedFelled(Object name, Throwable t) {{
  String n = String.valueOf(name);
  if (FAILED.putIfAbsent("felled:" + n, Boolean.TRUE) == null) {PKG}.SkillCfg.warn("skill:on:felled listener '" + n + "' failed (logged once per listener): " + t);
}}""", sbn))
sbn.addMethod(CtNewMethod.make(f"""
public static void felled({PR} pr, int row, {BTY} bt, String world, int x, int y, int z, String pkey) {{
  if (pr == null) return;
  java.util.ArrayList names = new java.util.ArrayList();
  java.util.ArrayList fns = new java.util.ArrayList();
  try {{
    Object o = {PKG}.SkillStore.bridge().get("skill:on:felled");
    if (!(o instanceof java.util.Map)) return;
    java.util.Iterator it = ((java.util.Map) o).entrySet().iterator();
    while (it.hasNext()) {{
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      if (e.getValue() instanceof java.util.function.Function) {{ names.add(e.getKey()); fns.add(e.getValue()); }}
    }}
  }} catch (Throwable t) {{ return; }}
  for (int i = 0; i < fns.size(); i++) {{
    try {{
      ((java.util.function.Function) fns.get(i)).apply(new Object[] {{ pr, Integer.valueOf(row), bt, world, Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z), pkey }});
    }} catch (Throwable t) {{ failedFelled(names.get(i), t); }}
  }}
}}""", sbn))
''')

# ================================================================ Perks: optional skills:double Collections count (spec 2.8, Skyy decision)
before('''# "Double drop!" chat line: at most one per feedbackMs per player''', r'''# 0.4.2 (Tree-Fall-Spec 2.8, optional; collections.doubleDrops, default OFF - Skyy decides): the items the double-drop perk GAVE also
# count in SkyyCollections (source skills:double, accepted by SkyyCollections 0.2 by default). Hand breaks, F-harvests and felled logs alike.
perk.addMethod(CtNewMethod.make(f"""
public static void collDouble({PR} pr, java.util.List drops) {{
  try {{
    if (!{PKG}.FellCfg.DD_COLLECTIONS || pr == null || drops == null) return;
    Object f = {PKG}.SkillStore.bridge().get("coll:fn:add");
    if (!(f instanceof java.util.function.Function)) return;
    java.util.UUID u = pr.getUuid();
    String k = {PKG}.SkillStore.pkey(u);
    for (int i = 0; i < drops.size(); i++) {{
      Object o = drops.get(i);
      if (!(o instanceof {IS})) continue;
      {IS} is = ({IS}) o;
      if (is.isEmpty() || is.getItemId() == null || is.getQuantity() <= 0) continue;
      ((java.util.function.Function) f).apply(new Object[] {{ u, is.getItemId(), Long.valueOf((long) is.getQuantity()), "skills:double", k }});
    }}
  }} catch (Throwable t) {{ }}
}}""", perk))
''')
rep('''  String what = give(pr, drops, world);
  if (what == null || !{PKG}.PerkCfg.DD_MSG) return;''', '''  String what = give(pr, drops, world);
  if (what != null) collDouble(pr, drops);
  if (what == null || !{PKG}.PerkCfg.DD_MSG) return;''')

# ================================================================ the Fell classes (before the deferred tasks: BreakTask calls Fell.*)
FELL_BLOCK = r'''# ================= 0.4.2 FELLED TREES (research/Tree-Fall-Spec.md sections 2 / 3.1 / 4) =================
# FellDefs: which block ids are tree wood / leaves - Hytale's own lists (Assets.zip Server/BlockTypeList/TreeWood.json, TreeLeaves.json)
# generated at build time, + the fell.extraTrees ids. Codes: 0 none, 1 trunk (_Trunk / _Trunk_Full), 2 branch, 3 roots, 4 leaves.
# family = the wood id without its suffix (Wood_Birch_Trunk -> Wood_Birch). Cached per block id and per block index (FellCfg maps).
fdf.addField(CtField.make("public static final java.util.HashSet WOOD = new java.util.HashSet(java.util.Arrays.asList(" + jarr(TREE_WOOD) + "));", fdf))
fdf.addField(CtField.make("public static final java.util.HashSet LEAVES = new java.util.HashSet(java.util.Arrays.asList(" + jarr(TREE_LEAVES) + "));", fdf))
fdf.addField(CtField.make("public static final java.util.HashSet WOODX = new java.util.HashSet(java.util.Arrays.asList(" + jarr(FELL_EXTRA_WOOD) + "));", fdf))
fdf.addField(CtField.make("public static final java.util.HashSet LEAVESX = new java.util.HashSet(java.util.Arrays.asList(" + jarr(FELL_EXTRA_LEAVES) + "));", fdf))
fdf.addField(CtField.make("public static final String[] SUFFIXES = " + jarr(FELL_SUFFIXES) + ";", fdf))
fdf.addMethod(CtNewMethod.make(f"""
public static int kindOfId(String id) {{
  if (id == null) return 0;
  boolean x = {PKG}.FellCfg.EXTRA_TREES;
  if (WOOD.contains(id) || (x && WOODX.contains(id))) {{
    if (id.endsWith("_Trunk") || id.endsWith("_Trunk_Full")) return 1;
    if (id.endsWith("_Branch_Short") || id.endsWith("_Branch_Long") || id.endsWith("_Branch_Corner")) return 2;
    if (id.endsWith("_Roots")) return 3;
    return 0;
  }}
  if (LEAVES.contains(id) || (x && LEAVESX.contains(id))) return 4;
  return 0;
}}""", fdf))
fdf.addMethod(CtNewMethod.make("""
public static String familyOfId(String id) {
  if (id == null) return "";
  for (int i = 0; i < SUFFIXES.length; i++) {
    if (id.endsWith(SUFFIXES[i])) return id.substring(0, id.length() - SUFFIXES[i].length());
  }
  return id;
}""", fdf))
fdf.addMethod(CtNewMethod.make("""
public static String rawId(String id) {
  if (id == null) return null;
  String r = id;
  if (r.startsWith("*")) r = r.substring(1);
  int s = r.indexOf("_State_");
  if (s > 0) r = r.substring(0, s);
  return r;
}""", fdf))
fdf.addMethod(CtNewMethod.make(f"""
public static int code({BTY} bt) {{
  if (bt == null) return 0;
  String id = bt.getId();
  if (id == null) return 0;
  Object c = {PKG}.FellCfg.IDCODE.get(id);
  if (c instanceof Integer) return ((Integer) c).intValue();
  String n = rawId(id);
  int k = kindOfId(n);
  String f = n;
  if (k == 0) {{
    String g = {PKG}.SkillCfg.familyId(bt);
    if (g != null && !g.equals(n)) {{ k = kindOfId(g); f = g; }}
  }}
  {PKG}.FellCfg.IDFAM.put(id, (k == 0 || k == 4) ? "" : familyOfId(f));
  {PKG}.FellCfg.IDCODE.put(id, Integer.valueOf(k));
  return k;
}}""", fdf))
fdf.addMethod(CtNewMethod.make(f"""
public static String fam({BTY} bt) {{
  if (bt == null || bt.getId() == null) return "";
  code(bt);
  Object f = {PKG}.FellCfg.IDFAM.get(bt.getId());
  return f instanceof String ? (String) f : "";
}}""", fdf))
fdf.addMethod(CtNewMethod.make(f"""
public static int codeIdx(int idx) {{
  if (idx <= 0) return 0;
  Integer key = Integer.valueOf(idx);
  Object c = {PKG}.FellCfg.CODE.get(key);
  if (c instanceof Integer) return ((Integer) c).intValue();
  {BTY} bt = null;
  try {{ bt = ({BTY}) {BTY}.getAssetMap().getAsset(idx); }} catch (Throwable t) {{ bt = null; }}
  int k = code(bt);
  {PKG}.FellCfg.FAM.put(key, k == 0 ? "" : fam(bt));
  {PKG}.FellCfg.CODE.put(key, Integer.valueOf(k));
  return k;
}}""", fdf))
fdf.addMethod(CtNewMethod.make(f"""
public static String famIdx(int idx) {{
  if (codeIdx(idx) == 0) return "";
  Object f = {PKG}.FellCfg.FAM.get(Integer.valueOf(idx));
  return f instanceof String ? (String) f : "";
}}""", fdf))

# FellRead: block reads for one snapshot or one watch poll (world thread). The SkillCfg.blockIdAt read path (never loads a chunk), with the
# chunk section (BlockSection + BlockPhysics) cached per 32-block section, so each read is an array lookup. idx: the block index,
# 0 = empty, -1 = not loaded / out of the world / over the read budget (over = true); deco = BlockPhysics.isDeco (player-placed logs and
# leaves, spec 1.4). err = the first exception a read threw (the handler-read fallback, spec 3.1). TEST / TESTDECO = test seam for the
# bare-JVM harness (packed PlacedStore key -> index / deco); always null in the game.
frd.addField(CtField.make("public static volatile java.util.function.Function TEST = null;", frd))
frd.addField(CtField.make("public static volatile java.util.function.Function TESTDECO = null;", frd))
frd.addField(CtField.make(f"public {WLD} w;", frd))
frd.addField(CtField.make(f"public {CHS} cs;", frd))
frd.addField(CtField.make(f"public {ST} st;", frd))
frd.addField(CtField.make("public java.util.HashMap secs;", frd))
frd.addField(CtField.make("public int reads;", frd))
frd.addField(CtField.make("public int max;", frd))
frd.addField(CtField.make("public boolean over;", frd))
frd.addField(CtField.make("public Throwable err;", frd))
frd.addConstructor(CtNewConstructor.make(f"""
public FellRead({WLD} w, int max) {{
  this.w = w; this.max = max; this.reads = 0; this.over = false; this.err = null;
  this.secs = new java.util.HashMap();
  this.cs = null; this.st = null;
  try {{
    if (w != null) {{
      this.cs = w.getChunkStore();
      if (this.cs != null) this.st = this.cs.getStore();
    }}
  }} catch (Throwable t) {{ this.err = t; }}
}}""", frd))
frd.addMethod(CtNewMethod.make(f"""
public Object[] sec(int x, int y, int z) {{
  int b = {CKU}.BITS;
  Long sk = Long.valueOf(((((long) (x >> b)) & 2097151L) << 42) | ((((long) (z >> b)) & 2097151L) << 21) | (((long) (y >> b)) & 2097151L));
  Object o = this.secs.get(sk);
  if (o != null) return (Object[]) o;
  Object[] e = new Object[3];
  try {{
    if (this.cs != null && this.st != null) {{
      {REF} sr = this.cs.getChunkSectionReferenceAtBlock(x, y, z);
      if (sr != null && sr.isValid()) {{
        e[0] = this.st.getComponent(sr, {BSC}.getComponentType());
        e[1] = sr;
      }}
    }}
  }} catch (Throwable t) {{ if (this.err == null) this.err = t; e[0] = null; e[1] = null; }}
  this.secs.put(sk, e);
  return e;
}}""", frd))
frd.addMethod(CtNewMethod.make(f"""
public int idx(int x, int y, int z) {{
  if (y < 0 || y >= {CKU}.HEIGHT) return -1;
  if (this.reads >= this.max) {{ this.over = true; return -1; }}
  this.reads++;
  java.util.function.Function tf = TEST;
  if (tf != null) {{
    Object r = tf.apply(Long.valueOf({PKG}.PlacedStore.key(x, y, z)));
    if (r instanceof Number) return ((Number) r).intValue();
    return 0;
  }}
  Object[] e = sec(x, y, z);
  if (e[0] == null) return -1;
  try {{ return (({BSC}) e[0]).get(x, y, z); }} catch (Throwable t) {{ if (this.err == null) this.err = t; return -1; }}
}}""", frd))
frd.addMethod(CtNewMethod.make(f"""
public boolean deco(int x, int y, int z) {{
  java.util.function.Function tf = TESTDECO;
  if (tf != null) return Boolean.TRUE.equals(tf.apply(Long.valueOf({PKG}.PlacedStore.key(x, y, z))));
  if (TEST != null) return false;
  Object[] e = sec(x, y, z);
  if (e[1] == null) return false;
  try {{
    if (e[2] == null) {{
      Object bp = this.st.getComponent(({REF}) e[1], {BPH}.getComponentType());
      if (bp == null) e[2] = Boolean.FALSE;
      else e[2] = bp;
    }}
    if (!(e[2] instanceof {BPH})) return false;
    return (({BPH}) e[2]).isDeco(x, y, z);
  }} catch (Throwable t) {{ if (this.err == null) this.err = t; return false; }}
}}""", frd))

# FellSnap: one snapshot (spec 2.3). trig 1 TRUNK, 2 BRANCH, 3 UNDER. b* = the broken block (y0 = by). Claims = x/y/z/idx/key/leaf[0..n),
# layer = lkey[0..ln) (trunks ON y0: cut, never claimed). late = the handler could not read blocks: search again in BreakTask (spec 3.1).
for decl in (f"{WLD} w", "String wn", "java.util.UUID u", "String pk", "long created", "long took", "int trig", "int bx", "int by", "int bz",
             f"{BTY} bt", "String fam", "boolean inOther", "boolean late", "boolean leafSeen", "int n", "int[] x", "int[] y", "int[] z",
             "int[] idx", "long[] key", "boolean[] leaf", "int ln", "long[] lkey", "int logs", "int leaves", "int reads"):
    fsn.addField(CtField.make("public " + decl + ";", fsn))
fsn.addConstructor(CtNewConstructor.make("public FellSnap() { this.n = 0; this.ln = 0; this.fam = null; }", fsn))

# FellWatch (spec 2.5): the claimed positions of one snapshot, polled every fell.pollMs (run() is added after Fell / FellCredit, which it
# calls). Counters for the debug line: hand (hand-broken while claimed), env (explosion / fire), other (taken over by a newer claim),
# lost (chunk gone), replaced (another block), skipped (another player's claim at commit), dropped (credit preconditions failed).
fwt.addInterface(pool.get("java.lang.Runnable"))
for decl in (f"{WLD} w", "String wn", "java.util.UUID u", "String pk", "int trig", "long created", "long lastChange", "boolean hop",
             "volatile boolean ended", "int n", "int[] x", "int[] y", "int[] z", "int[] idx", "long[] key", "boolean[] leaf", "boolean[] done",
             "int left", "int ln", "long[] lkey", "long took", "int reads", "int sLogs", "int sLeaves", "int credited", "int cLogs",
             "int cLeaves", "int hand", "int env", "int other", "int lost", "int replaced", "int skipped", "int dropped", "int collYes",
             "int collNo", "long xp", "int row"):
    fwt.addField(CtField.make("public " + decl + ";", fwt))
fwt.addConstructor(CtNewConstructor.make(f"""
public FellWatch({PKG}.FellSnap s) {{
  this.w = s.w; this.wn = s.wn; this.u = s.u; this.pk = s.pk; this.trig = s.trig;
  this.n = s.n;
  this.x = new int[this.n]; System.arraycopy(s.x, 0, this.x, 0, this.n);
  this.y = new int[this.n]; System.arraycopy(s.y, 0, this.y, 0, this.n);
  this.z = new int[this.n]; System.arraycopy(s.z, 0, this.z, 0, this.n);
  this.idx = new int[this.n]; System.arraycopy(s.idx, 0, this.idx, 0, this.n);
  this.key = new long[this.n]; System.arraycopy(s.key, 0, this.key, 0, this.n);
  this.leaf = new boolean[this.n]; System.arraycopy(s.leaf, 0, this.leaf, 0, this.n);
  this.done = new boolean[this.n];
  this.left = this.n;
  this.ln = s.ln;
  this.lkey = new long[this.ln]; System.arraycopy(s.lkey, 0, this.lkey, 0, this.ln);
  this.created = s.created;
  this.lastChange = System.currentTimeMillis();
  this.hop = false; this.ended = false; this.row = -1;
  this.took = s.took; this.reads = s.reads; this.sLogs = s.logs; this.sLeaves = s.leaves;
}}""", fwt))
fwt.addMethod(CtNewMethod.make("""
public boolean live() {
  return !this.ended;
}""", fwt))
fwt.addMethod(CtNewMethod.make("""
public void touch() {
  this.lastChange = System.currentTimeMillis();
}""", fwt))

# Fell: the per-world claim maps and the snapshot / commit / release logic (spec 2.3 / 2.4 / 2.5). CLAIMS / LAYER: world name ->
# ConcurrentHashMap(Long PlacedStore.key -> FellWatch); read and written on that world's thread (the bridge only reads). FELLED: world ->
# LinkedHashMap(Long key -> Object[]{UUID, pkey, Long at, String blockId}), 8192 per world, fell.memoryMs TTL (synchronized statics).
fel.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CLAIMS = new java.util.concurrent.ConcurrentHashMap();", fel))
fel.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LAYER = new java.util.concurrent.ConcurrentHashMap();", fel))
fel.addField(CtField.make("public static final java.util.HashMap FELLED = new java.util.HashMap();", fel))
fel.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap WATCHES = new java.util.concurrent.ConcurrentHashMap();", fel))
fel.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap RATE = new java.util.concurrent.ConcurrentHashMap();", fel))
fel.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap FAILED = new java.util.concurrent.ConcurrentHashMap();", fel))
fel.addField(CtField.make("public static volatile boolean HANDLER_FAILED = false;", fel))
fel.addField(CtField.make("public static volatile boolean TEST_NO_SCHEDULE = false;", fel))   # test seam (bare-JVM harness): commit without scheduling; always false in the game
fel.addMethod(CtNewMethod.make(f"""
public static void failed(String tag, Throwable t) {{
  if (FAILED.putIfAbsent(tag, Boolean.TRUE) == null) {PKG}.SkillCfg.warn("felled trees: " + tag + " failed (logged once): " + t);
}}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static long key(int x, int y, int z) {{
  return {PKG}.PlacedStore.key(x, y, z);
}}""", fel))
fel.addMethod(CtNewMethod.make("""
public static java.util.concurrent.ConcurrentHashMap claims(String wn) {
  Object m = CLAIMS.get(wn);
  if (m == null) { CLAIMS.putIfAbsent(wn, new java.util.concurrent.ConcurrentHashMap()); m = CLAIMS.get(wn); }
  return (java.util.concurrent.ConcurrentHashMap) m;
}""", fel))
fel.addMethod(CtNewMethod.make("""
public static java.util.concurrent.ConcurrentHashMap layer(String wn) {
  Object m = LAYER.get(wn);
  if (m == null) { LAYER.putIfAbsent(wn, new java.util.concurrent.ConcurrentHashMap()); m = LAYER.get(wn); }
  return (java.util.concurrent.ConcurrentHashMap) m;
}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static boolean online(java.util.UUID u) {{
  try {{
    {PR} pr = {UNI}.get().getPlayer(u);
    return pr != null && pr.isValid();
  }} catch (Throwable t) {{ return false; }}
}}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static synchronized void felledPut(String wn, long k, Object[] v) {{
  java.util.LinkedHashMap m = (java.util.LinkedHashMap) FELLED.get(wn);
  if (m == null) {{ m = new java.util.LinkedHashMap(); FELLED.put(wn, m); }}
  Long kk = Long.valueOf(k);
  m.remove(kk);
  m.put(kk, v);
  long now = System.currentTimeMillis();
  long ttl = {PKG}.FellCfg.MEMORY_MS;
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) {{
    Object[] e = (Object[]) it.next();
    if (m.size() > 8192 || now - ((Long) e[2]).longValue() >= ttl) it.remove();
    else break;
  }}
}}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static synchronized Object[] felledGet(String wn, long k) {{
  java.util.LinkedHashMap m = (java.util.LinkedHashMap) FELLED.get(wn);
  if (m == null) return null;
  Object o = m.get(Long.valueOf(k));
  if (o == null) return null;
  Object[] e = (Object[]) o;
  if (System.currentTimeMillis() - ((Long) e[2]).longValue() >= {PKG}.FellCfg.MEMORY_MS) return null;
  return e;
}}""", fel))
fel.addMethod(CtNewMethod.make("""
public static synchronized void clearFelled() {
  FELLED.clear();
}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static void handlerFailed(Throwable t) {{
  if (!HANDLER_FAILED) {{
    HANDLER_FAILED = true;
    {PKG}.SkillCfg.warn("felled trees: reading blocks inside the break event failed (" + t + ") - snapshots are taken a moment later from now on (fallback, research/Tree-Fall-Spec.md 3.1)");
  }}
}}""", fel))
# natural = not in the placed-block tracker and not deco (spec 2.3)
fel.addMethod(CtNewMethod.make(f"""
public static boolean natural(String wn, {PKG}.FellRead R, int x, int y, int z) {{
  if ({PKG}.PlacedStore.contains(wn, key(x, y, z))) return false;
  return !R.deco(x, y, z);
}}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static void addClaim({PKG}.FellSnap s, int x, int y, int z, int idx, boolean leaf) {{
  int i = s.n;
  s.x[i] = x; s.y[i] = y; s.z[i] = z; s.idx[i] = idx; s.key[i] = key(x, y, z); s.leaf[i] = leaf;
  s.n = i + 1;
  if (leaf) s.leaves = s.leaves + 1;
  else s.logs = s.logs + 1;
}}""", fel))
# fell.maxSnapshotsPerSecond per player (world thread of the player; a player is in one world at a time)
fel.addMethod(CtNewMethod.make(f"""
public static boolean rate(java.util.UUID u) {{
  long sec = System.currentTimeMillis() / 1000L;
  long[] c = (long[]) RATE.get(u);
  if (c == null) {{
    if (RATE.size() > 2000) RATE.clear();
    c = new long[2];
    RATE.put(u, c);
  }}
  if (c[0] != sec) {{ c[0] = sec; c[1] = 0L; }}
  if (c[1] >= (long) {PKG}.FellCfg.MAX_SNAPS) return false;
  c[1] = c[1] + 1L;
  return true;
}}""", fel))
# the search (spec 2.3): breadth-first over the 26-neighbourhood from the seed(s). Every read cell is marked seen once. Wood: same family,
# natural, radius / height, trunks y >= y0 (BRANCH trigger: branches only), branches / roots y >= y0 - 1; trunks ON y0 -> layer (still
# expanded, so the first cut of a thick tree records the wood above EVERY base log); others -> claims. Leaves next to accepted wood are
# candidates; the leaf phase accepts natural ones (leafSeen) and walks up to 4 leaf steps (claims only with fell.leaves).
fel.addMethod(CtNewMethod.make(f"""
public static void search({PKG}.FellSnap s, {PKG}.FellRead R, int[] sx, int[] sy, int[] sz, int[] si, boolean[] sc, int ns) {{
  int maxW = {PKG}.FellCfg.MAX_LOGS + ns;
  int maxL = {PKG}.FellCfg.MAX_LEAVES;
  int rad = {PKG}.FellCfg.RADIUS;
  int y0 = s.by;
  int top = y0 + {PKG}.FellCfg.HEIGHT;
  int cap = maxW + maxL + 2;
  s.x = new int[cap]; s.y = new int[cap]; s.z = new int[cap]; s.idx = new int[cap]; s.key = new long[cap]; s.leaf = new boolean[cap];
  s.n = 0; s.logs = 0; s.leaves = 0;
  s.lkey = new long[maxW + 2]; s.ln = 0;
  s.leafSeen = false;
  int[] wx = new int[maxW + 2]; int[] wy = new int[maxW + 2]; int[] wz = new int[maxW + 2];
  int wc = 0;
  java.util.HashSet seen = new java.util.HashSet();
  for (int i = 0; i < ns; i++) {{
    wx[wc] = sx[i]; wy[wc] = sy[i]; wz[wc] = sz[i]; wc++;
    seen.add(Long.valueOf(key(sx[i], sy[i], sz[i])));
    if (sc[i]) addClaim(s, sx[i], sy[i], sz[i], si[i], false);
  }}
  java.util.ArrayList cand = new java.util.ArrayList();
  boolean full = wc >= maxW;
  int head = 0;
  while (head < wc && !R.over) {{
    int cx = wx[head]; int cy = wy[head]; int cz = wz[head];
    head++;
    for (int dx = -1; dx <= 1; dx++) {{
      for (int dy = -1; dy <= 1; dy++) {{
        for (int dz = -1; dz <= 1; dz++) {{
          if (dx == 0 && dy == 0 && dz == 0) continue;
          int nx = cx + dx; int ny = cy + dy; int nz = cz + dz;
          if (nx - s.bx > rad || s.bx - nx > rad || nz - s.bz > rad || s.bz - nz > rad) continue;
          if (ny > top || ny < y0 - 1) continue;
          Long kk = Long.valueOf(key(nx, ny, nz));
          if (seen.contains(kk)) continue;
          seen.add(kk);
          int id = R.idx(nx, ny, nz);
          if (id <= 0) continue;
          int c = {PKG}.FellDefs.codeIdx(id);
          if (c == 0) continue;
          if (c == 4) {{ cand.add(new int[] {{ nx, ny, nz, id }}); continue; }}
          if (full) continue;
          if (!s.fam.equals({PKG}.FellDefs.famIdx(id))) continue;
          if (s.trig == 2) {{
            if (c != 2) continue;
          }} else if (c == 1 && ny < y0) continue;
          if (!natural(s.wn, R, nx, ny, nz)) continue;
          wx[wc] = nx; wy[wc] = ny; wz[wc] = nz; wc++;
          if (c == 1 && ny == y0) {{ s.lkey[s.ln] = kk.longValue(); s.ln = s.ln + 1; }}
          else addClaim(s, nx, ny, nz, id, false);
          if (wc >= maxW) full = true;
        }}
      }}
    }}
  }}
  boolean claimLeaves = {PKG}.FellCfg.LEAVES && maxL > 0;
  int[] qx = new int[maxL + 1]; int[] qy = new int[maxL + 1]; int[] qz = new int[maxL + 1]; int[] qd = new int[maxL + 1];
  int qc = 0;
  java.util.HashSet lseen = new java.util.HashSet();
  for (int i = 0; i < cand.size(); i++) {{
    int[] cd = (int[]) cand.get(i);
    if (!natural(s.wn, R, cd[0], cd[1], cd[2])) continue;
    s.leafSeen = true;
    if (!claimLeaves || qc >= maxL) break;
    lseen.add(Long.valueOf(key(cd[0], cd[1], cd[2])));
    qx[qc] = cd[0]; qy[qc] = cd[1]; qz[qc] = cd[2]; qd[qc] = 1; qc++;
    addClaim(s, cd[0], cd[1], cd[2], cd[3], true);
  }}
  int lh = 0;
  while (claimLeaves && lh < qc && qc < maxL && !R.over) {{
    int cx = qx[lh]; int cy = qy[lh]; int cz = qz[lh]; int cdp = qd[lh];
    lh++;
    if (cdp >= 4) continue;
    for (int dx = -1; dx <= 1; dx++) {{
      for (int dy = -1; dy <= 1; dy++) {{
        for (int dz = -1; dz <= 1; dz++) {{
          if (dx == 0 && dy == 0 && dz == 0) continue;
          if (qc >= maxL) continue;
          int nx = cx + dx; int ny = cy + dy; int nz = cz + dz;
          if (nx - s.bx > rad || s.bx - nx > rad || nz - s.bz > rad || s.bz - nz > rad) continue;
          if (ny > top || ny < y0 - 1) continue;
          Long kk = Long.valueOf(key(nx, ny, nz));
          if (seen.contains(kk) || lseen.contains(kk)) continue;
          lseen.add(kk);
          int id = R.idx(nx, ny, nz);
          if (id <= 0 || {PKG}.FellDefs.codeIdx(id) != 4) continue;
          if (!natural(s.wn, R, nx, ny, nz)) continue;
          qx[qc] = nx; qy[qc] = ny; qz[qc] = nz; qd[qc] = cdp + 1; qc++;
          addClaim(s, nx, ny, nz, id, true);
        }}
      }}
    }}
  }}
}}""", fel))
# seeds + search (spec 2.3): TRUNK / BRANCH = the broken block (a search node, never a claim); UNDER = the natural trunk right above the
# broken block (a claim). late (the handler-read fallback, spec 3.1): the broken block is gone and physics may already have removed the
# next logs, so the search may step through up to 2 empty cells straight above the seed to reach the rest of the tree.
fel.addMethod(CtNewMethod.make(f"""
public static void run({PKG}.FellSnap s, {PKG}.FellRead R, boolean late) {{
  long t0 = System.nanoTime();
  int[] sx = new int[2]; int[] sy = new int[2]; int[] sz = new int[2]; int[] si = new int[2]; boolean[] sc = new boolean[2];
  int ns = 0;
  s.n = 0; s.ln = 0; s.leafSeen = false;
  if (s.trig == 3) {{
    int yy = s.by + 1;
    int empt = 0;
    boolean stop = false;
    while (!stop && yy <= s.by + 3) {{
      int id = R.idx(s.bx, yy, s.bz);
      if (id > 0 && {PKG}.FellDefs.codeIdx(id) == 1) {{
        if (natural(s.wn, R, s.bx, yy, s.bz)) {{
          s.fam = {PKG}.FellDefs.famIdx(id);
          sx[0] = s.bx; sy[0] = yy; sz[0] = s.bz; si[0] = id; sc[0] = true; ns = 1;
        }}
        stop = true;
      }} else if (id == 0 && late && empt < 2) {{
        empt++;
        yy++;
      }} else stop = true;
    }}
  }} else if (s.fam != null && s.fam.length() > 0) {{
    sx[0] = s.bx; sy[0] = s.by; sz[0] = s.bz; si[0] = 0; sc[0] = false; ns = 1;
    if (late) {{
      int yy = s.by + 1;
      int empt = 0;
      boolean stop = false;
      while (!stop && yy <= s.by + 3) {{
        int id = R.idx(s.bx, yy, s.bz);
        if (id == 0 && empt < 2) {{ empt++; yy++; continue; }}
        if (id > 0) {{
          int c = {PKG}.FellDefs.codeIdx(id);
          boolean ok = s.fam.equals({PKG}.FellDefs.famIdx(id)) && (s.trig == 2 ? c == 2 : (c == 1 || c == 2 || c == 3));
          if (ok && natural(s.wn, R, s.bx, yy, s.bz)) {{ sx[1] = s.bx; sy[1] = yy; sz[1] = s.bz; si[1] = id; sc[1] = true; ns = 2; }}
        }}
        stop = true;
      }}
    }}
  }}
  if (ns == 0 || s.fam == null) {{ s.n = 0; return; }}
  if (!rate(s.u)) {{ s.n = 0; if ({PKG}.FellCfg.DEBUG) {PKG}.SkillCfg.info("fell: snapshot skipped - over fell.maxSnapshotsPerSecond for " + s.u); return; }}
  search(s, R, sx, sy, sz, si, sc, ns);
  s.reads = R.reads;
  s.took = System.nanoTime() - t0;
}}""", fel))
# handler (spec 2.2 / 3.1 hook 1): trigger test (cheap for non-tree blocks: one read above), then the search while the tree still stands.
# Returns null (no snapshot), a FellSnap, or a FellSnap with late = true (reads failed in the handler: BreakTask searches instead).
fel.addMethod(CtNewMethod.make(f"""
public static {PKG}.FellSnap snapshot({WLD} w, java.util.UUID u, String pk, {BTY} bt, int x, int y, int z, boolean inOther) {{
  if (!{PKG}.FellCfg.on() || w == null || bt == null) return null;
  int c = {PKG}.FellDefs.code(bt);
  int trig;
  if (c == 1) trig = 1;
  else if (c == 2) trig = 2;
  else if (c == 3 || c == 4) return null;
  else if ({PKG}.FellCfg.UNDER_TRUNK) trig = 3;
  else return null;
  {PKG}.FellSnap s = new {PKG}.FellSnap();
  s.w = w; s.wn = w.getName(); s.u = u; s.pk = pk; s.created = System.currentTimeMillis();
  s.trig = trig; s.bx = x; s.by = y; s.bz = z; s.bt = bt; s.inOther = inOther;
  s.fam = null;
  if (trig != 3) s.fam = {PKG}.FellDefs.fam(bt);
  if (HANDLER_FAILED) {{ s.late = true; return s; }}
  {PKG}.FellRead R = new {PKG}.FellRead(w, {PKG}.FellCfg.MAX_READS);
  if (trig == 3) {{
    int above = R.idx(x, y + 1, z);
    if (R.err != null) {{ handlerFailed(R.err); s.late = true; return s; }}
    if (above <= 0 || {PKG}.FellDefs.codeIdx(above) != 1) return null;
  }}
  run(s, R, false);
  if (R.err != null) {{
    handlerFailed(R.err);
    s.late = true; s.n = 0; s.ln = 0; s.fam = null;
    if (trig != 3) s.fam = {PKG}.FellDefs.fam(bt);
    return s;
  }}
  if (s.n <= 0) return null;
  return s;
}}""", fel))
# the fallback search in BreakTask (world thread, the broken block is gone)
fel.addMethod(CtNewMethod.make(f"""
public static {PKG}.FellSnap snapshotLate({PKG}.FellSnap s) {{
  if (s == null || s.w == null || !{PKG}.FellCfg.on()) return null;
  {PKG}.FellRead R = new {PKG}.FellRead(s.w, {PKG}.FellCfg.MAX_READS);
  run(s, R, true);
  s.late = false;
  if (R.err != null) failed("late snapshot read", R.err);
  if (s.n <= 0) return null;
  return s;
}}""", fel))
# hand break (spec 2.4 handler steps 1-2) -> Object[]{watch it was unclaimed from (or null), Boolean inOther, Boolean reused}
fel.addMethod(CtNewMethod.make(f"""
public static Object[] onBreak(String wn, java.util.UUID u, int x, int y, int z) {{
  Object[] r = new Object[3];
  r[1] = Boolean.FALSE;
  r[2] = Boolean.FALSE;
  Long k = Long.valueOf(key(x, y, z));
  Object cm0 = CLAIMS.get(wn);
  if (cm0 != null) {{
    java.util.concurrent.ConcurrentHashMap cm = (java.util.concurrent.ConcurrentHashMap) cm0;
    Object h = cm.get(k);
    if (h instanceof {PKG}.FellWatch) {{
      {PKG}.FellWatch o = ({PKG}.FellWatch) h;
      cm.remove(k, o);
      if (o.live()) {{
        o.hand = o.hand + 1;
        r[0] = o;
        if (o.u.equals(u)) {{ o.touch(); r[2] = Boolean.TRUE; }}
        else r[1] = Boolean.TRUE;
        return r;
      }}
    }}
  }}
  Object lm0 = LAYER.get(wn);
  if (lm0 != null) {{
    Object lw = ((java.util.concurrent.ConcurrentHashMap) lm0).get(k);
    if (lw instanceof {PKG}.FellWatch) {{
      {PKG}.FellWatch o = ({PKG}.FellWatch) lw;
      if (o.live() && o.u.equals(u)) {{ o.touch(); r[2] = Boolean.TRUE; }}
    }}
  }}
  return r;
}}""", fel))
# a cancelled break puts back the claim its handler removed (spec 3.1 hook 2)
fel.addMethod(CtNewMethod.make(f"""
public static void restore(String wn, {BBE} ev, Object unclaimed) {{
  if (!(unclaimed instanceof {PKG}.FellWatch) || ev == null) return;
  {PKG}.FellWatch o = ({PKG}.FellWatch) unclaimed;
  if (!o.live()) return;
  {V3I} t = ev.getTargetBlock();
  if (t == null) return;
  if (claims(wn).putIfAbsent(Long.valueOf(key(t.x(), t.y(), t.z())), o) == null && o.hand > 0) o.hand = o.hand - 1;
}}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static int countFor(java.util.UUID u) {{
  int c = 0;
  java.util.Iterator it = WATCHES.keySet().iterator();
  while (it.hasNext()) {{
    {PKG}.FellWatch W = ({PKG}.FellWatch) it.next();
    if (W.live() && W.u.equals(u)) c++;
  }}
  return c;
}}""", fel))
# end a watch: release its claims / layer entries (only where they still point at it), optional chat summary, debug line (spec 2.5 / 2.9)
fel.addMethod(CtNewMethod.make(f"""
public static void end({PKG}.FellWatch W, boolean fromWorld) {{
  if (W == null || W.ended) return;
  W.ended = true;
  WATCHES.remove(W);
  try {{
    java.util.concurrent.ConcurrentHashMap cm = claims(W.wn);
    for (int i = 0; i < W.n; i++) cm.remove(Long.valueOf(W.key[i]), W);
    java.util.concurrent.ConcurrentHashMap lm = layer(W.wn);
    for (int j = 0; j < W.ln; j++) lm.remove(Long.valueOf(W.lkey[j]), W);
  }} catch (Throwable t) {{ failed("release", t); }}
  long now = System.currentTimeMillis();
  try {{
    if (fromWorld && {PKG}.FellCfg.MESSAGE && W.credited > 0 && !{PKG}.SkillStore.quiet(W.u)) {{
      {PR} pr = {UNI}.get().getPlayer(W.u);
      if (pr != null && pr.isValid()) {{
        StringBuilder sb = new StringBuilder("Tree felled: ");
        sb.append(W.cLogs).append(W.cLogs == 1 ? " log" : " logs");
        if (W.cLeaves > 0) sb.append(", ").append(W.cLeaves).append(W.cLeaves == 1 ? " leaf" : " leaves");
        if (W.xp > 0L && W.row >= 0 && W.row < {PKG}.SkillDefs.N) sb.append(" (+").append({PKG}.SkillDefs.fmt(W.xp)).append(" ").append({PKG}.SkillDefs.LABELS[W.row]).append(" XP)");
        pr.sendMessage({MSG}.raw(sb.toString()).color("#9fe0a0"));
      }}
    }}
  }} catch (Throwable t) {{ failed("summary", t); }}
  if ({PKG}.FellCfg.DEBUG) {PKG}.SkillCfg.info("fell: watch end " + W.u + " world " + W.wn + " claims " + W.n + " (logs " + W.sLogs + ", leaves " + W.sLeaves + ", layer " + W.ln + ") credited " + W.credited + " (logs " + W.cLogs + ", leaves " + W.cLeaves + ") hand " + W.hand + " env " + W.env + " lost " + W.lost + " other " + W.other + " replaced " + W.replaced + " skipped " + W.skipped + " dropped " + W.dropped + " collections " + W.collYes + "/" + (W.collYes + W.collNo) + " xp " + W.xp + " ms " + (now - W.created));
}}""", fel))
# watches whose world stopped running tasks never end by themselves: drop them after maxWatchMs + 30 s
fel.addMethod(CtNewMethod.make(f"""
public static void pruneStale() {{
  long now = System.currentTimeMillis();
  java.util.ArrayList old = new java.util.ArrayList();
  java.util.Iterator it = WATCHES.keySet().iterator();
  while (it.hasNext()) {{
    {PKG}.FellWatch W = ({PKG}.FellWatch) it.next();
    if (now - W.created >= {PKG}.FellCfg.MAX_WATCH_MS + 30000L) old.add(W);
  }}
  for (int i = 0; i < old.size(); i++) end(({PKG}.FellWatch) old.get(i), false);
}}""", fel))
# commit (spec 2.4 commit steps 1-3; BreakTask, world thread, not cancelled)
fel.addMethod(CtNewMethod.make(f"""
public static void commit({PKG}.FellSnap s0) {{
  {PKG}.FellSnap s = s0;
  if (s == null) return;
  if (s.late) s = snapshotLate(s);
  if (s == null || s.n <= 0) return;
  boolean dbg = {PKG}.FellCfg.DEBUG;
  if ({PKG}.FellCfg.NEED_LEAVES && !s.leafSeen) {{ if (dbg) {PKG}.SkillCfg.info("fell: snapshot dropped - no natural leaves (" + s.logs + " logs) at " + s.bx + " " + s.by + " " + s.bz); return; }}
  pruneStale();
  if (countFor(s.u) >= {PKG}.FellCfg.MAX_PER_PLAYER) {{ if (dbg) {PKG}.SkillCfg.info("fell: snapshot dropped - fell.maxWatchesPerPlayer reached for " + s.u); return; }}
  if (WATCHES.size() >= {PKG}.FellCfg.MAX_WATCHES) {{ if (dbg) {PKG}.SkillCfg.info("fell: snapshot dropped - fell.maxWatches reached"); return; }}
  {PKG}.FellWatch W = new {PKG}.FellWatch(s);
  java.util.concurrent.ConcurrentHashMap cm = claims(s.wn);
  int held = 0;
  for (int i = 0; i < W.n; i++) {{
    Long k = Long.valueOf(W.key[i]);
    Object h = cm.get(k);
    boolean take = h == null;
    if (!take) {{
      {PKG}.FellWatch o = ({PKG}.FellWatch) h;
      if (!o.live() || o.u.equals(s.u) || !s.inOther) {{
        take = true;
        if (o.live() && o != W) o.other = o.other + 1;
      }}
    }}
    if (take) {{ cm.put(k, W); held++; }}
    else {{ W.done[i] = true; W.left = W.left - 1; W.skipped = W.skipped + 1; }}
  }}
  if (held == 0) {{ if (dbg) {PKG}.SkillCfg.info("fell: snapshot dropped - every position is claimed by another player's falling tree"); return; }}
  java.util.concurrent.ConcurrentHashMap lm = layer(s.wn);
  for (int j = 0; j < W.ln; j++) lm.put(Long.valueOf(W.lkey[j]), W);
  WATCHES.put(W, Boolean.TRUE);
  if (dbg) {PKG}.SkillCfg.info("fell: snapshot " + s.u + " world " + s.wn + " trigger " + (s.trig == 1 ? "trunk" : (s.trig == 2 ? "branch" : "under")) + " at " + s.bx + " " + s.by + " " + s.bz + " logs " + s.logs + " leaves " + s.leaves + " layer " + s.ln + " held " + held + " reads " + s.reads + " took " + (s.took / 1000L) + " us" + (s.inOther ? " (cut inside another player's fall)" : ""));
  W.hop = true;
  if (TEST_NO_SCHEDULE) return;
  try {{ {HSV}.SCHEDULED_EXECUTOR.schedule(W, {PKG}.FellCfg.POLL_MS, java.util.concurrent.TimeUnit.MILLISECONDS); }} catch (Throwable t) {{ failed("schedule", t); end(W, false); }}
}}""", fel))
# EnvSys: an explosion / fire removed a position -> unclaim it (never paid as felled, spec 2.4 "Environment breaks")
fel.addMethod(CtNewMethod.make(f"""
public static void envBreak(String wn, {V3I} t) {{
  if (t == null || wn == null) return;
  Object m = CLAIMS.get(wn);
  if (m == null) return;
  Object o = ((java.util.concurrent.ConcurrentHashMap) m).remove(Long.valueOf(key(t.x(), t.y(), t.z())));
  if (o instanceof {PKG}.FellWatch) {{
    {PKG}.FellWatch W = ({PKG}.FellWatch) o;
    W.env = W.env + 1;
  }}
}}""", fel))
# skill:fn:felledBy (spec 2.8): "falling" = claimed by a live watch (atMillis = snapshot time), "felled" = credited within fell.memoryMs
fel.addMethod(CtNewMethod.make(f"""
public static Object[] felledBy(String wn, int x, int y, int z) {{
  long k = key(x, y, z);
  Object m = CLAIMS.get(wn);
  if (m != null) {{
    Object o = ((java.util.concurrent.ConcurrentHashMap) m).get(Long.valueOf(k));
    if (o instanceof {PKG}.FellWatch) {{
      {PKG}.FellWatch W = ({PKG}.FellWatch) o;
      if (W.live()) return new Object[] {{ W.u, W.pk, Long.valueOf(W.created), "falling" }};
    }}
  }}
  Object[] f = felledGet(wn, k);
  if (f == null) return null;
  return new Object[] {{ f[0], f[1], f[2], "felled" }};
}}""", fel))
fel.addMethod(CtNewMethod.make(f"""
public static void endAll() {{
  java.util.ArrayList all = new java.util.ArrayList(WATCHES.keySet());
  for (int i = 0; i < all.size(); i++) end(({PKG}.FellWatch) all.get(i), false);
  CLAIMS.clear();
  LAYER.clear();
  WATCHES.clear();
  clearFelled();
}}""", fel))

# FellDrops: the engine's physics drop selection (BlockHarvestUtils.naturallyRemoveBlockByPhysics, bytecode 2026-09-24): Physics
# (quantity 1), else Breaking (its quantity), else Soft, else Harvest -> getDrops(bt, quantity, itemId, dropListId). A fresh roll.
fdr.addMethod(CtNewMethod.make(f"""
public static java.util.List roll({BTY} bt) {{
  if (bt == null) return null;
  int q = 1;
  String item = null;
  String list = null;
  {BGA} g = bt.getGathering();
  if (g != null) {{
    {PDT} ph = g.getPhysics();
    {BBD} br = g.getBreaking();
    {SBD} so = g.getSoft();
    {HDT} hv = g.getHarvest();
    if (ph != null) {{ item = ph.getItemId(); list = ph.getDropListId(); }}
    else if (br != null) {{ q = br.getQuantity(); item = br.getItemId(); list = br.getDropListId(); }}
    else if (so != null) {{ item = so.getItemId(); list = so.getDropListId(); }}
    else if (hv != null) {{ item = hv.getItemId(); list = hv.getDropListId(); }}
  }}
  return {BHU}.getDrops(bt, q, item, list);
}}""", fdr))

# FellCredit (spec 2.6): one felled position, world thread of the tree's world
fcr.addMethod(CtNewMethod.make(f"""
public static void coll({PKG}.FellWatch W, {BTY} bt) {{
  Object f = {PKG}.SkillStore.bridge().get("coll:fn:add");
  if (!(f instanceof java.util.function.Function)) return;
  java.util.List drops = null;
  try {{ drops = {PKG}.FellDrops.roll(bt); }} catch (Throwable t) {{ {PKG}.Fell.failed("drop roll", t); return; }}
  if (drops == null) return;
  for (int j = 0; j < drops.size(); j++) {{
    Object o = drops.get(j);
    if (!(o instanceof {IS})) continue;
    {IS} is = ({IS}) o;
    if (is.isEmpty() || is.getItemId() == null || is.getQuantity() <= 0) continue;
    Object r = null;
    try {{ r = ((java.util.function.Function) f).apply(new Object[] {{ W.u, is.getItemId(), Long.valueOf((long) is.getQuantity()), "skills:felled", W.pk }}); }} catch (Throwable t) {{ r = null; }}
    if (Boolean.TRUE.equals(r)) W.collYes = W.collYes + 1;
    else W.collNo = W.collNo + 1;
  }}
}}""", fcr))
fcr.addMethod(CtNewMethod.make(f"""
public static void one({PKG}.FellWatch W, int i) {{
  try {{
    {PR} pr = {UNI}.get().getPlayer(W.u);
    if (pr == null || !pr.isValid()) {{ W.dropped = W.dropped + 1; return; }}
    if (!W.pk.equals({PKG}.SkillStore.pkey(W.u))) {{ W.dropped = W.dropped + 1; return; }}
    if ({PKG}.SkillStore.bridge().get("profile:busy:" + W.u.toString()) != null) {{ W.dropped = W.dropped + 1; return; }}
    {WLD} pw = {UNI}.get().getWorld(pr.getWorldUuid());
    if (pw == null || !W.wn.equals(pw.getName())) {{ W.dropped = W.dropped + 1; return; }}
    {REF} r = pr.getReference();
    if (r == null || !r.isValid()) {{ W.dropped = W.dropped + 1; return; }}
    if ({PKG}.SkillXp.creative(r.getStore(), r)) {{ W.dropped = W.dropped + 1; return; }}
    {BTY} bt = ({BTY}) {BTY}.getAssetMap().getAsset(W.idx[i]);
    if (bt == null) {{ W.dropped = W.dropped + 1; return; }}
    long[] rule = {PKG}.SkillCfg.classifyBreak(bt);
    int row = rule == null ? -1 : (int) rule[0];
    if (rule != null && rule[2] == 1L) {{
      double fct = W.leaf[i] ? {PKG}.FellCfg.LEAF_XP_FACTOR : {PKG}.FellCfg.XP_FACTOR;
      long xp = Math.round((double) rule[1] * fct);
      if (xp > 0L) {{
        long amt = {PKG}.SkillBonus.boost(W.u, row, xp);
        {PKG}.SkillXp.gain3(pr, row, amt, true, false);
        W.xp = W.xp + amt;
        W.row = row;
      }}
    }}
    if ({PKG}.FellCfg.DOUBLE_DROPS && rule != null) {PKG}.Perks.breakDouble(pr, row, bt, W.wn, true);
    if ({PKG}.FellCfg.COLLECTIONS) coll(W, bt);
    if ({PKG}.FellCfg.NODES && rule != null) {PKG}.SkillBonus.felled(pr, row, bt, W.wn, W.x[i], W.y[i], W.z[i], W.pk);
    {PKG}.Fell.felledPut(W.wn, W.key[i], new Object[] {{ W.u, W.pk, Long.valueOf(System.currentTimeMillis()), bt.getId() }});
    W.credited = W.credited + 1;
    if (W.leaf[i]) W.cLeaves = W.cLeaves + 1;
    else W.cLogs = W.cLogs + 1;
  }} catch (Throwable t) {{ {PKG}.Fell.failed("credit", t); }}
}}""", fcr))

# FellWatch.run (spec 2.5; the HarvestTask hop pattern: scheduler -> world.execute -> poll)
fwt.addMethod(CtNewMethod.make(f"""
public void run() {{
  if (this.ended) return;
  long now = System.currentTimeMillis();
  if (this.hop) {{
    this.hop = false;
    if (now - this.created >= {PKG}.FellCfg.MAX_WATCH_MS + 30000L) {{ {PKG}.Fell.end(this, false); return; }}
    try {{ this.w.execute(this); }} catch (Throwable t) {{ {PKG}.Fell.end(this, false); }}
    return;
  }}
  try {{
    {PKG}.FellRead R = new {PKG}.FellRead(this.w, 2147483647);
    java.util.concurrent.ConcurrentHashMap cm = {PKG}.Fell.claims(this.wn);
    for (int i = 0; i < this.n; i++) {{
      if (this.done[i]) continue;
      int cur = R.idx(this.x[i], this.y[i], this.z[i]);
      if (cur == this.idx[i]) continue;
      this.done[i] = true;
      this.left--;
      this.lastChange = now;
      if (cur != 0) {{
        if (cur < 0) this.lost++;
        else this.replaced++;
        continue;
      }}
      Long k = Long.valueOf(this.key[i]);
      if (cm.get(k) != this) continue;
      cm.remove(k, this);
      {PKG}.FellCredit.one(this, i);
    }}
    if (R.err != null) {PKG}.Fell.failed("watch read", R.err);
  }} catch (Throwable t) {{ {PKG}.Fell.failed("watch", t); {PKG}.Fell.end(this, true); return; }}
  if (this.left <= 0 || now - this.lastChange >= {PKG}.FellCfg.QUIET_MS || now - this.created >= {PKG}.FellCfg.MAX_WATCH_MS || !{PKG}.Fell.online(this.u)) {{ {PKG}.Fell.end(this, true); return; }}
  this.hop = true;
  try {{ {HSV}.SCHEDULED_EXECUTOR.schedule(this, {PKG}.FellCfg.POLL_MS, java.util.concurrent.TimeUnit.MILLISECONDS); }} catch (Throwable t) {{ {PKG}.Fell.end(this, true); }}
}}""", fwt))

# skill:fn:felledBy (spec 2.8): apply(Object[]{String world, Integer x, Integer y, Integer z}) -> Object[]{UUID, pkey, Long at, state} | null
ffn.addInterface(pool.get("java.util.function.Function"))
ffn.addConstructor(CtNewConstructor.make("public FelledByFn() { }", ffn))
ffn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 4 || a[0] == null || !(a[1] instanceof Number) || !(a[2] instanceof Number) || !(a[3] instanceof Number)) return null;
    return {PKG}.Fell.felledBy(String.valueOf(a[0]), ((Number) a[1]).intValue(), ((Number) a[2]).intValue(), ((Number) a[3]).intValue());
  }} catch (Throwable t) {{ return null; }}
}}""", ffn))

'''
before('''# ================= deferred tasks (run on the world thread after every system saw the event) =================
''', FELL_BLOCK)

# ================================================================ BreakTask: fields, constructor, hook 2 (spec 3.1)
after('''btk.addField(CtField.make("public long[] rule;", btk))
''', '''btk.addField(CtField.make("public Object fs;", btk))          # 0.4.2: the FellSnap taken in the handler (null = none)
btk.addField(CtField.make("public Object unclaimed;", btk))   # 0.4.2: the FellWatch whose claim this break removed (put back if cancelled)
''')
after('''public BreakTask({BBE} ev, java.util.UUID u, String world, long[] rule) {{
  this.ev = ev; this.u = u; this.world = world; this.rule = rule;
}}""", btk))
''', '''btk.addConstructor(CtNewConstructor.make(f"""
public BreakTask({BBE} ev, java.util.UUID u, String world, long[] rule, Object fs, Object unclaimed) {{
  this.ev = ev; this.u = u; this.world = world; this.rule = rule; this.fs = fs; this.unclaimed = unclaimed;
}}""", btk))
''')
rep('''    if (this.ev.isCancelled()) return;
    boolean wasPlaced = false;''', '''    if (this.ev.isCancelled()) {{
      try {{ {PKG}.Fell.restore(this.world, this.ev, this.unclaimed); }} catch (Throwable ft) {{ {PKG}.Fell.failed("restore", ft); }}
      return;
    }}
    if (this.fs != null) {{
      try {{ {PKG}.Fell.commit(({PKG}.FellSnap) this.fs); }} catch (Throwable ft) {{ {PKG}.Fell.failed("commit", ft); }}
    }}
    boolean wasPlaced = false;''')

# ================================================================ PlaceTask: the sapling placed-tracker fix (spec 3.1, placed.skipSaplings)
rep('''    {V3I} t = this.ev.getTargetBlock();
    if (t == null) return;
    {PKG}.PlacedStore.add(this.world, {PKG}.PlacedStore.key(t.x(), t.y(), t.z()));''', '''    {V3I} t = this.ev.getTargetBlock();
    if (t == null) return;
    if ({PKG}.FellCfg.SKIP_SAPLINGS) {{
      {IS} hand = this.ev.getItemInHand();
      String hid = hand == null ? null : hand.getItemId();
      if (hid != null && hid.startsWith("Plant_Sapling_")) return;
    }}
    {PKG}.PlacedStore.add(this.world, {PKG}.PlacedStore.key(t.x(), t.y(), t.z()));''')

# ================================================================ BreakSys: hook 1 (spec 3.1)
rep('''    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    long[] rule = {PKG}.SkillCfg.classifyBreak(e.getBlockType());
    if (rule != null && {PKG}.SkillXp.creative(st, r)) rule = null;
    if (rule == null && !{PKG}.SkillCfg.IGNORE_PLACED) return;
    w.execute(new {PKG}.BreakTask(e, pr.getUuid(), w.getName(), rule));''', '''    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    Object fs = null;
    Object unclaimed = null;
    try {{
      if ({PKG}.FellCfg.on()) {{
        {V3I} t = e.getTargetBlock();
        if (t != null) {{
          String fwn = w.getName();
          Object[] hc = {PKG}.Fell.onBreak(fwn, pr.getUuid(), t.x(), t.y(), t.z());
          unclaimed = hc[0];
          if (!((Boolean) hc[2]).booleanValue() && {PKG}.FellCfg.worldOk(fwn) && !{PKG}.SkillXp.creative(st, r))
            fs = {PKG}.Fell.snapshot(w, pr.getUuid(), {PKG}.SkillStore.pkey(pr.getUuid()), e.getBlockType(), t.x(), t.y(), t.z(), ((Boolean) hc[1]).booleanValue());
        }}
      }}
    }} catch (Throwable ft) {{ {PKG}.Fell.failed("snapshot", ft); }}
    long[] rule = {PKG}.SkillCfg.classifyBreak(e.getBlockType());
    if (rule != null && {PKG}.SkillXp.creative(st, r)) rule = null;
    if (rule == null && !{PKG}.SkillCfg.IGNORE_PLACED && fs == null && unclaimed == null) return;
    w.execute(new {PKG}.BreakTask(e, pr.getUuid(), w.getName(), rule, fs, unclaimed));''')

# ================================================================ EnvSys (spec 2.4 "Environment breaks")
before('''# ================= CraftSys (0.4): CraftRecipeEvent$Post = one finished craft unit at a vanilla crafting bench (Alchemy spec 3.1) ======
''', r'''# ================= EnvSys (0.4.2, Tree-Fall-Spec 2.4): explosions + fire fire EnvironmentBreakBlockEvent on the ENTITY store =================
# (ExplosionUtils -> performBlockDamage with a null breaker -> performBlockBreak's else branch, before the removal; FireFluidTicker.
# applyBurnResult -> World.getEntityStore().getStore().invoke(...) right after its setBlock - both bytecode-checked). The physics cascade
# fires no event, so "an EnvironmentBreakBlockEvent named this claimed position" = an explosion or fire took it: unclaim, never pay as
# felled. A WorldEventSystem (no query), like the engine's TriggerVolumeBlockEventSystems$EnvironmentBlockBroken.
esy.addField(CtField.make("public static boolean FAILED_ONCE = false;", esy))
esy.addConstructor(CtNewConstructor.make(f"public EnvSys() {{ super({EBE}.class); }}", esy))
esy.addMethod(CtNewMethod.make(f"""
public void handle({ST} st, {CB} buf, {EV} ev) {{
  try {{
    if (!(ev instanceof {EBE})) return;
    if ({PKG}.Fell.CLAIMS.isEmpty()) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    {PKG}.Fell.envBreak(w.getName(), (({EBE}) ev).getTargetBlock());
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("EnvSys failed (logged once): " + t); }}
  }}
}}""", esy))

''')

# ================================================================ Stats page 1.5x (Skyy 2026-09-24 07:05) + the Foraging how-to
rep('''# ================= StatsPage (0.3): one skill - level, XP to next, boosts now (numbers), what the next level adds =================
''', '''# ================= StatsPage (0.3): one skill - level, XP to next, boosts now (numbers), what the next level adds =================
# 0.4.2: scaled ~1.5x (Skyy): root 960 x 795 (was 640 x 530; fits a 1080-high screen), fonts 24 / 17 / 20 / 18 / 15, bar 600 x 18,
# buttons 195 x 45 with 18 pt labels, the how-to line always wraps (2 lines). Content height at most 752 (7 + 7 lines).
STBARW = 600
''')
rep('''  if (s == {PKG}.SkillDefs.FORAGING) return "Earn XP by chopping trees - rare woods pay more";''',
    '''  if (s == {PKG}.SkillDefs.FORAGING) return "Earn XP by chopping trees - rare woods pay more" + ({PKG}.FellCfg.on() ? " - fell a tree and every log" + ({PKG}.FellCfg.LEAVES ? " and leaf" : "") + " that comes down pays you too" : "");''')
rep_between('''public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  int s = this.slot;''', '''    ev.addEventBinding({BT}.Activating, "#SkyyStTree", {EVD}.of("a", "sttree"));
  }}
}}""", spg))''', '''public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  int s = this.slot;
  if (s < 0 || s >= {PKG}.SkillDefs.N) s = 0;
  int cs = {PKG}.SkillClass.slot(u);
  if (s == {PKG}.SkillDefs.COMBAT && cs >= 0) s = cs;
  long total = d[s];
  int lv = {PKG}.SkillDefs.levelOf(total);
  long cur = {PKG}.SkillDefs.intoLevel(total);
  long need = {PKG}.SkillDefs.needFor(total);
  int fill = need > 0L ? (int) ({STBARW}L * cur / need) : {STBARW};
  if (fill < 0) fill = 0;
  if (fill > {STBARW}) fill = {STBARW};
  boolean legacy = s == {PKG}.SkillDefs.COMBAT;
  if (legacy) fill = 0;
  String col = {PKG}.SkillDefs.COLORS[s];
  String name = legacy ? "Combat" : {PKG}.SkillClass.skillName(u, s);
  String bs = "Style: TextButtonStyle(Default: (Background: #27463a, LabelStyle: (FontSize: 18, TextColor: #dcffe8, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #3b6b54, LabelStyle: (FontSize: 18, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #172a22, LabelStyle: (FontSize: 18, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyySkStats {{ Anchor: (Width: 960, Height: 795); Background: #0b1524(0.96); Padding: (Horizontal: 24, Vertical: 15); LayoutMode: Top; }}");
  b.appendInline("#SkyySkStats", "Group {{ Anchor: (Height: 3); Background: #9fe0a0; }}");
  b.appendInline("#SkyySkStats", "Label #SkyyStTitle {{ Anchor: (Height: 45); Text: \\\\"\\\\"; Style: (FontSize: 24, RenderBold: true, TextColor: " + col + ", HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.set("#SkyyStTitle.Text", legacy ? "Combat - no class" : name + " - level " + lv + " of " + {PKG}.SkillDefs.MAX);
  b.appendInline("#SkyySkStats", "Label #SkyyStSub {{ Anchor: (Height: 27); Text: \\\\"\\\\"; Style: (FontSize: 17, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  String sub;
  if (legacy) sub = "Choose a class with /class - each class has its own combat skill";
  else if (need > 0L) sub = {PKG}.SkillDefs.fmt(cur) + " / " + {PKG}.SkillDefs.fmt(need) + " XP to level " + (lv + 1) + "  (" + {PKG}.SkillDefs.fmt(need - cur) + " to go)";
  else sub = "MAX LEVEL - " + {PKG}.SkillDefs.fmt(total) + " XP";
  b.set("#SkyyStSub.Text", sub);
  b.appendInline("#SkyySkStats", "Group #SkyyStBarRow {{ Anchor: (Height: 24); LayoutMode: Left; Padding: (Top: 3); }}");
  b.appendInline("#SkyyStBarRow", "Label {{ Anchor: (Width: 156, Height: 18); Text: \\\\"\\\\"; }}");
  b.appendInline("#SkyyStBarRow", "Group #SkyyStBar {{ Anchor: (Width: {STBARW}, Height: 18); Background: #22324a; }}");
  if (fill > 0) b.appendInline("#SkyyStBar", "Group {{ Anchor: (Left: 0, Top: 0, Width: " + fill + ", Height: 18); Background: " + col + "; }}");
  if ({PKG}.SkillDefs.isClass(s) && s != cs) {{
    String cn = {PKG}.SkillDefs.CLASSES[s - {PKG}.SkillDefs.CLASS0];
    String art = (cn.startsWith("A") || cn.startsWith("E") || cn.startsWith("I") || cn.startsWith("O") || cn.startsWith("U")) ? "an " : "a ";
    line(b, "SkyyStNote", "You are not " + art + cn + " right now - these boosts work while you are one", "#ffb080", 17, true, 30);
  }} else {{
    b.appendInline("#SkyySkStats", "Label {{ Anchor: (Height: 12); Text: \\\\"\\\\"; }}");
  }}
  line(b, "SkyyStNowHd", legacy ? "Your combat" : "Boosts right now (level " + lv + ")", "#e6fff0", 20, true, 36);
  java.util.ArrayList now = lines(u, s, lv, false);
  for (int i = 0; i < now.size() && i < 7; i++) line(b, "SkyyStNow" + i, "   " + (String) now.get(i), "#dfe8f0", 18, false, 28);
  b.appendInline("#SkyySkStats", "Label {{ Anchor: (Height: 12); Text: \\\\"\\\\"; }}");
  if (!legacy) {{
    if (need > 0L) {{
      line(b, "SkyyStNextHd", "Level " + (lv + 1) + " adds", "#e6fff0", 20, true, 36);
      java.util.ArrayList nx = lines(u, s, lv, true);
      for (int i = 0; i < nx.size() && i < 7; i++) line(b, "SkyyStNext" + i, "   " + (String) nx.get(i), "#bfe8c8", 18, false, 28);
    }} else {{
      line(b, "SkyyStNextHd", "Max level reached - nothing more to unlock", "#ffe08a", 20, true, 36);
    }}
    b.appendInline("#SkyySkStats", "Label {{ Anchor: (Height: 12); Text: \\\\"\\\\"; }}");
  }}
  wrapLine(b, "SkyyStHow", how(s), "#8fa6ba", 15, 45);
  b.appendInline("#SkyySkStats", "Group #SkyyStNav {{ Anchor: (Height: 60); LayoutMode: Left; Padding: (Top: 12); }}");
  String tree = {PKG}.SkillBonus.treeAvailable(s) ? {PKG}.SkillBonus.treeName(s) : null;
  b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: " + (tree != null ? 133 : 246) + ", Height: 45); Text: \\\\"\\\\"; }}");
  b.appendInline("#SkyyStNav", "TextButton #SkyyStBack {{ Anchor: (Width: 195, Height: 45); Text: \\\\"< Back\\\\"; " + bs + " }}");
  b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: 30, Height: 45); Text: \\\\"\\\\"; }}");
  b.appendInline("#SkyyStNav", "TextButton #SkyyStTop {{ Anchor: (Width: 195, Height: 45); Text: \\\\"Top 10\\\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyStBack", {EVD}.of("a", "stback"));
  ev.addEventBinding({BT}.Activating, "#SkyyStTop", {EVD}.of("a", "sttop"));
  if (tree != null) {{
    b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: 30, Height: 45); Text: \\\\"\\\\"; }}");
    b.appendInline("#SkyyStNav", "TextButton #SkyyStTree {{ Anchor: (Width: 195, Height: 45); Text: \\\\"Skill tree\\\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyStTree", {EVD}.of("a", "sttree"));
  }}
}}""", spg))''')

# ================================================================ plugin: EnvSys, bridge, shutdown, log line, class list, manifest
after('''  getEntityStoreRegistry().registerSystem(new {PKG}.BreakSys());
''', '''  try {{
    getEntityStoreRegistry().registerSystem(new {PKG}.EnvSys());
  }} catch (Throwable t) {{
    {PKG}.FellCfg.BROKEN = true;
    {PKG}.SkillCfg.warn("could not register EnvSys (explosion / fire guard for felled trees): " + t + " - felled trees stay OFF until the next restart");
  }}
''')
after('''  {PKG}.SkillStore.bridge().putIfAbsent("skill:on:gather", new java.util.concurrent.ConcurrentHashMap());
''', '''  {PKG}.SkillStore.bridge().putIfAbsent("skill:on:felled", new java.util.concurrent.ConcurrentHashMap());
  {PKG}.SkillStore.bridge().put("skill:fn:felledBy", new {PKG}.FelledByFn());
''')
after('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:placed"); }} catch (Throwable t) {{ }}
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:felledBy"); }} catch (Throwable t) {{ }}
  try {{ {PKG}.Fell.endAll(); }} catch (Throwable t) {{ }}
''')
rep('''rows Alchemy (Alchemy Bench) / Smithing (Furnace) / Cooking (via SkyyCooking) / Exploration (via SkyyExploration, no boosters);''',
    '''rows Alchemy (Alchemy Bench) / Smithing (Furnace) / Cooking (via SkyyCooking) / Exploration (via SkyyExploration, no boosters); felled trees " + {PKG}.FellCfg.text() + ";''')
rep('''afss, afn, cfn, xcmd, sbn, xfn, dfn, pfn, exc):''', '''afss, afn, cfn, xcmd, sbn, xfn, dfn, pfn, exc,
          fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy):''')
rep('''XP from breaking blocks, ripe crops,''', '''XP from breaking blocks (a felled tree pays every log that falls), ripe crops,''')


# ####################################################################################################################################
# STAGE 2: the Acrobatics DOUBLE JUMP (research/Double-Jump-Spec.md 3.2) + PARTY COMBAT XP (beta backlog 6). Applied on top of stage 1.
# ####################################################################################################################################

REG0 = s.count("registerSystem(")
# ================================================================ S2 header paragraph (generated build docstring)
before('''0.4.1 (research/Exploration-Build-Spec.md section 3 - the Exploration row''', '''0.4.2 stage 2 (same version; tools/skills_0_4_2_patch.py STAGE 2 - the stage 1 felled trees + Stats page 1.5x above are kept):
  DOUBLE JUMP (research/Double-Jump-Spec.md 3.2, the SkyySkills part). The node is SkyyTrees 0.2.1 "Double Jump" (RDouble, Acrobatics
    tier II slot 5): skill:bonus doublejump.acrobatics = the air-jump height as a fraction of the player's own jump height (0.55-1.0).
    Acro.airJump runs in AcroSys.tick on the world thread EVERY tick (right after Acro.move, before Acro.dodge). airTrack (pure) keeps
    the edges and the airtime: crouch press, jump press, extraJumpsUsed change; ground / climbing / fluid / swimming / mantling = charge
    reset (spec 2.3 rule 2); mounted / flying / gliding / sitting / sleeping (the rest of Acro.excludedState) restart the airtime clock
    but keep the charge, so minAirMs counts from the end of the glide / flight and a mid-air glide never refills the jump. airTry (pure)
    decides: trigger acro.doubleJump.trigger = crouch (rising edge of MovementStates.crouching while airborne -
    DEFAULT, copied from TerrariaAddons' Cloud in a Bottle) | jump (rising edge of MovementStates.jumping while airborne; never when the
    client jumped itself: upward speed above fallJumpForce / 2 = a coyote or buffered jump) | both; minAirMs after leaving the ground,
    maxJumps per airtime, cooldownMs, the node (0 = none, clamped to maxFraction), not falling faster than maxFallSpeed (0 = the world's
    MovementConfig MinFallSpeedToEngageRoll, vanilla 21 b/s = before a landing would hurt). airJump (engine glue): acro.enabled +
    acro.doubleJump.enabled, not mounted / flying / gliding / sitting / sleeping / climbing / in fluid / swimming / mantling
    (Acro.excludedState), not creative (the REAL game mode), Stamina (acro.doubleJump.stamina, taken only when the jump happens; too
    little = no jump and the charge is kept; StaminaRegenDelay set to -staminaRegenDelay like vanilla Double_Jump.json), then ONE
    Velocity Set instruction: vy = min(jumpForce x sqrt(V), sqrt(2 g maxBlocks)), horizontal = the client's own + forwardPush along it.
    0 Acrobatics XP by default (acro.doubleJump.xp -> the capped pending pool) and the push never pays ground-jump XP (s[9] = now).
    Optional FX (acro.doubleJump.fx): SFX_Player_Jump + Impact_Feathers_Black. acro.doubleJump.debug=true: players with skyyskills.admin
    get a "[Skills] DJ debug: crouch edge in air - vy .. - air .. ms - used .." chat line per airborne crouch / jump / extraJumpsUsed
    edge (spec test 5.0 decides the trigger; the probe also works with acro.doubleJump.enabled=false, it only needs acro.enabled).
    Only an edge of the configured trigger goes on to the node / movement-settings lookups. Charges reset on a world change and a
    profile switch (Acro.reset / profileReset).
    Bridge skill:dj:key = "crouch" / "jump" / "jump or crouch" (setup + /skills reload, removed at shutdown) = the %K of the SkyyTrees
    card. Stats page: "double jump 55%" in the Acrobatics "Skill tree:" line + "Double Jump: press crouch in mid-air for a 55% jump -
    2 Stamina" while the node is owned. STATE double[292] (281-287 used, see the layout comment).
  PARTY COMBAT XP (beta backlog 6, Skyy: "party should share combat XP"). KillSys pays the killer exactly as before (class, class weapon,
    not creative; the killer keeps 100 %), then PartyXp.share: every OTHER member of the killer's party (bridge party:fn:members,
    SkyyParty 0.1.3: String[] member UUIDs) who is online, in the SAME world (same entity store = the same world thread), ready, alive,
    not in creative (creativeXp rule) and within party.combatShare.radius (48) blocks of the killer gets party.combatShare.fraction
    (0.5) of the killer's base kill XP (after the xp multiplier, before the killer's tree bonus; a fraction is paid by chance) into
    THEIR OWN current class skill on THEIR active profile (needs a class; no weapon rule for them; skipped while their class is still
    following a profile switch - SkillClass.consistent), + their own tree XP bonus (party.combatShare.treeBonus). Level ups, coins and
    SkyyGuilds guild XP follow the normal award path. Chat: "[Party] +6 Archery XP (340/500) from Skyy's kill" - batched per member
    and throttled like the other XP lines (feedbackMs, flushed by the 1 s ticker; /skills quiet, feedback=false and
    party.combatShare.message=false hide it). The share goes through SkillXp.gain4 (= gain3 + the party note right after the XP is
    added, like SkillMsg.note), and a level up flushes the pending [Party] line first, so it always prints BEFORE the SKILL LEVEL UP it
    causes, like every other XP line. Without SkyyParty (no party:fn:members) nothing changes. The class how-to line on the
    Stats page mentions the share while it is on and SkyyParty is loaded.
  CONFIG: the "Double Jump" (acro.doubleJump.*) and "Party combat XP" (party.combatShare.*) blocks are in a fresh xp.properties and
    appended ONCE each to an existing file without acro.doubleJump.enabled / party.combatShare.enabled (AcroCfg.ensureDj,
    PartyCfg.ensureDefaults); /skills reload re-reads both and republishes skill:dj:key. Clamps: maxJumps 1-5, maxFraction 0-1.5,
    maxBlocks 0.5-10, forwardPush 0-10, cooldownMs 0-60000, minAirMs 0-5000, fraction 0-1, radius 1-512.
  COMMANDS / UI: no new command. Stats page lines only (no new element ids).
  CHECKED in a bare JVM (2026-09-24, scratch harness under tools/dev/scratch, deleted afterwards): all 71 classes load + initialise
    under -Xverify:all; the compiled call targets (SoundUtil.playSoundEvent3d(int, SoundCategory, Vector3d, ComponentAccessor),
    ParticleUtil.spawnParticleEffect(String, Vector3dc, List, ComponentAccessor), Velocity.addInstruction(.., Set), the MovementConfig
    chain, EntityStatMap subtract / set, PartyXp.share after SkillXp.gain in KillSys) read back from the bytecode; config: both blocks
    once in a fresh file, appended once each to a 0.4.1-style file and to a 0.1-era file (no duplicate keys after two loads), every
    default, the trigger parse (Jump / both / unknown -> crouch), every clamp, djText / PartyCfg.text / the load summary; airTrack
    (ground / climbing reset, airtime start, crouch / jump / extraJumpsUsed edges, holding = no edge) and airTry (-1 .. -7 reasons:
    trigger per mode, minAirMs, one charge, cooldown, no node, falling 25 > 21, rule J in jump mode only, both = crouch skips rule J; vy =
    11.8 x sqrt(0.55) = 8.75; cap 14.97); reset / profileReset zero 281 / 282 / 284 / 285; STATE double[292]; djFraction from
    skill:bonus (clamped by maxFraction, 0 with bridge.bonus.enabled=false); djLine / the tree line "double jump 55%" / 6 Acrobatics
    lines (cap 7); skill:dj:key crouch / "jump or crouch"; djMaxFall without a world = 21; PartyXp.amount (10 x 0.5 = 5, 7 x 0.5 = 3 or 4
    with mean 3.5, 1 x 0.5 = 0 or 1 with mean 0.5); members() from a fake party:fn:members; slotFor (no SkyyClasses / no class / Archer /
    class still switching -> -1); the chat batching ("from Skyy's kill", "from 2 kills by Skyy", "from 2 party kills", the SkyyClasses
    skill display name, throttle, drop); the class how-to text only while SkyyParty is loaded.
  UNVERIFIED (needs the game): spec test 5.0 - whether the client reports MovementStates.crouching (and jumping) while airborne; the
    Velocity Set push feel + latency; the Stamina cost / regen pause; the world MovementConfig lookup (21 in vanilla); the FX; the
    SkyyTrees 0.2.1 node -> skill:bonus doublejump.acrobatics path in game; PartyXp.share end to end with two real players (member
    PlayerRef -> Ref in the killer's store, positions, level ups on the member's profile, the chat line); the Stats page lines on a client.
''')

# ================================================================ S2 API names + probes (tools/dev reflect.py against HytaleServer.jar, 2026-09-24)
after('''             ("java.lang.System", "arraycopy"), ("java.util.Arrays", "asList")):
    B.probe(pool, c, m)
''', '''# 0.4.2 stage 2: double jump (research/Double-Jump-Spec.md 1.4 / 3.2). MMG / MVS / PHC are tools/skyymove.py's names.
MMG = MV.MMG
MVS = MV.MVS
PHC = MV.PHC
MCF = "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementConfig"   # asset: getMinFallSpeedToEngageRoll()
GPC = "com.hypixel.hytale.server.core.asset.type.gameplay.GameplayConfig"
PCF = "com.hypixel.hytale.server.core.asset.type.gameplay.PlayerConfig"
ESTT= "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType"
SEV = "com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent"
SNU = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
SCAT= "com.hypixel.hytale.protocol.SoundCategory"
PTU = "com.hypixel.hytale.server.core.universe.world.ParticleUtil"
ILT = "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap"
for c, m in ((MVT, "extraJumpsUsed"), (MVT, "crouching"), (MVT, "jumping"), (MVT, "onGround"), (CVT, "Set"), (MMG, "getComponentType"),
             (MMG, "getSettings"), (MVS, "jumpForce"), (MVS, "fallJumpForce"), (PHC, "GRAVITY_ACCELERATION"), (MCF, "getAssetMap"),
             (MCF, "getMinFallSpeedToEngageRoll"), (WLD, "getGameplayConfig"), (GPC, "getPlayerConfig"), (PCF, "getMovementConfigIndex"),
             (ESM, "subtractStatValue"), (ESM, "setStatValue"), (DST, "getStamina"), (ESTT, "getAssetMap"), (SEV, "getAssetMap"),
             (SNU, "playSoundEvent3d"), (PTU, "spawnParticleEffect"), (SCAT, "SFX"), (ILT, "getAsset"), (ILT, "getIndex"),
             (VEL, "addInstruction"), (VEL, "getClientVelocity"), (PLA, "getGameMode"), (PR, "hasPermission"),
             # party combat XP: members by UUID -> PlayerRef -> Ref in the killer's store, their position
             (UNI, "getPlayer"), (PR, "getReference"), (PR, "isValid"), (REF, "getStore"), (TRC, "getPosition"), (PLA, "isWaitingForClientReady")):
    B.probe(pool, c, m)
''')

# ================================================================ S2 xp.properties blocks (fresh file = part of DEFAULTS; old file = appended once)
after('''print("felled trees: %d wood ids, %d leaf ids (+ extraTrees %d / %d)" % (len(TREE_WOOD), len(TREE_LEAVES), len(FELL_EXTRA_WOOD), len(FELL_EXTRA_LEAVES)))
''', r'''# 0.4.2 stage 2: Double Jump (research/Double-Jump-Spec.md 3.2). NOT part of ACRO_L on purpose: AcroCfg.ensureDefaults appends ACRO_L to a
# 0.1-era file, AcroCfg.ensureDj appends this block to any file without acro.doubleJump.enabled - both in the same load, never twice.
DJ_L = []
DJ_L.append("# ---------- Double Jump (SkyySkills 0.4.2) - the Acrobatics skill-tree node (SkyyTrees 0.2.1, skill:bonus doublejump.acrobatics) ----------")
DJ_L.append("# Comments must stay on their own lines.")
DJ_L.append("# trigger: crouch = press crouch in mid-air (default); jump = the jump key in mid-air (only if research/Double-Jump-Spec.md test 5.0")
DJ_L.append("# showed the client reports it); both = either one.")
DJ_L.append("acro.doubleJump.enabled=true")
DJ_L.append("acro.doubleJump.trigger=crouch")
DJ_L.append("# extra jumps per airtime (1-5); they recharge when you land, climb, swim or touch water")
DJ_L.append("acro.doubleJump.maxJumps=1")
DJ_L.append("# Air jump height = the node value (a fraction of your own jump height), capped at maxFraction and at maxBlocks.")
DJ_L.append("acro.doubleJump.maxFraction=1.0")
DJ_L.append("acro.doubleJump.maxBlocks=3.5")
DJ_L.append("# forwardPush: extra blocks per second along the way you are moving (only while moving)")
DJ_L.append("acro.doubleJump.forwardPush=2.0")
DJ_L.append("# Stamina per double jump (too little = no double jump, the charge is kept); staminaRegenDelay pauses regen briefly (0 = off)")
DJ_L.append("acro.doubleJump.stamina=2.0")
DJ_L.append("acro.doubleJump.staminaRegenDelay=0.3")
DJ_L.append("# milliseconds between two double jumps, and after leaving the ground before a press counts")
DJ_L.append("acro.doubleJump.cooldownMs=250")
DJ_L.append("acro.doubleJump.minAirMs=100")
DJ_L.append("# 0 = the world's MovementConfig MinFallSpeedToEngageRoll (vanilla 21 - the speed where landings start to hurt); below 0 = no limit.")
DJ_L.append("acro.doubleJump.maxFallSpeed=0")
DJ_L.append("# Acrobatics XP per double jump (0 = none; it counts against acro.maxXpPerMinute)")
DJ_L.append("acro.doubleJump.xp=0")
DJ_L.append("# fx: jump sound + feather particles at your feet")
DJ_L.append("acro.doubleJump.fx=true")
DJ_L.append("# debug=true: players with skyyskills.admin see a chat line for every crouch / jump / extra-jump edge while airborne (test 5.0).")
DJ_L.append("acro.doubleJump.debug=false")
L.append("")
L.extend(DJ_L)
DJ_DEFAULTS = "\n".join(DJ_L) + "\n"
assert all(ord(ch) < 128 for ch in DJ_DEFAULTS) and '"' not in DJ_DEFAULTS
DJ_LIT = json.dumps(DJ_DEFAULTS)
# 0.4.2 stage 2: party combat XP (beta backlog 6). Appended once to a file without party.combatShare.enabled (PartyCfg.ensureDefaults).
PARTY_L = []
PARTY_L.append("# ---------- Party combat XP (SkyySkills 0.4.2) - needs SkyyParty 0.1.3+ (bridge party:fn:members) ----------")
PARTY_L.append("# Comments must stay on their own lines.")
PARTY_L.append("# When a kill pays you class combat XP, every other member of your party who is online, in the same world, within radius")
PARTY_L.append("# blocks of you and not in creative also gets fraction of that XP in THEIR OWN current class skill. The killer keeps 100 percent.")
PARTY_L.append("# Only the killer needs a class weapon; the others need a class. treeBonus: their own skill-tree XP bonus applies to the share.")
PARTY_L.append("party.combatShare.enabled=true")
PARTY_L.append("party.combatShare.fraction=0.5")
PARTY_L.append("party.combatShare.radius=48")
PARTY_L.append("party.combatShare.treeBonus=true")
PARTY_L.append("# message: a '[Party] +6 Archery XP (340/500) from Skyy's kill' chat line, throttled like the other XP lines (/skills quiet hides it)")
PARTY_L.append("party.combatShare.message=true")
L.append("")
L.extend(PARTY_L)
PARTY_DEFAULTS = "\n".join(PARTY_L) + "\n"
assert all(ord(ch) < 128 for ch in PARTY_DEFAULTS) and '"' not in PARTY_DEFAULTS
PARTY_LIT = json.dumps(PARTY_DEFAULTS)
''')

# ================================================================ S2 classes
after('''esy  = pool.makeClass(PKG + ".EnvSys", pool.get(WES))
''', '''# 0.4.2 stage 2: party combat XP (beta backlog 6)
pcg  = pool.makeClass(PKG + ".PartyCfg")
pxp  = pool.makeClass(PKG + ".PartyXp")
pft  = pool.makeClass(PKG + ".PartyFlushTask")
''')

# ================================================================ S2 AcroCfg: acro.doubleJump.* (spec 3.2)
after('''    acfg.addField(CtField.make("public static volatile %s;" % _decl, acfg))
''', '''# 0.4.2 stage 2: acro.doubleJump.* (research/Double-Jump-Spec.md 3.2) - read by readDj from SkillCfg.load, so /skills reload re-reads them
for _decl in ("boolean DJ_ON = true", "int DJ_TRIGGER = 0", 'String DJ_KEY = "crouch"', "int DJ_MAX_JUMPS = 1", "double DJ_MAX_FRAC = 1.0",
              "double DJ_MAX_BLOCKS = 3.5", "double DJ_FORWARD = 2.0", "double DJ_STAMINA = 2.0", "double DJ_REGEN_DELAY = 0.3",
              "long DJ_CD = 250L", "long DJ_MIN_AIR = 100L", "double DJ_MAX_FALL = 0.0", "double DJ_XP = 0.0", "boolean DJ_FX = true",
              "boolean DJ_DEBUG = false"):
    acfg.addField(CtField.make("public static volatile %s;" % _decl, acfg))
acfg.addField(CtField.make("public static final String DJ_DEFAULTS = " + DJ_LIT + ";", acfg))
''')
after('''  TREE_DODGE_MAX = Math.min(2.0, nn({PKG}.SkillCfg.dbl(p, "acro.treeDodgeMax", 0.25)));
}}""", acfg))
''', r'''# 0.4.2 stage 2 (Double-Jump-Spec 3.2): trigger 0 crouch (default), 1 jump, 2 both - an unknown value = crouch + one warning per load.
# DJ_KEY = the words the SkyyTrees card (bridge skill:dj:key, Acro.djPublish) and the Stats page show.
acfg.addMethod(CtNewMethod.make("""
public static double clampD(double v, double lo, double hi) {
  if (Double.isNaN(v) || v < lo) return lo;
  if (v > hi) return hi;
  return v;
}""", acfg))
acfg.addMethod(CtNewMethod.make(f"""
public static void readDj(java.util.Properties p) {{
  DJ_ON = {PKG}.SkillCfg.bool(p, "acro.doubleJump.enabled", true);
  int tr = 0;
  String t = p.getProperty("acro.doubleJump.trigger");
  if (t != null) {{
    String x = t.trim().toLowerCase(java.util.Locale.ROOT);
    if (x.equals("jump")) tr = 1;
    else if (x.equals("both")) tr = 2;
    else if (x.length() > 0 && !x.equals("crouch")) {PKG}.SkillCfg.warn("acro.doubleJump.trigger=" + t.trim() + " is not crouch, jump or both - using crouch");
  }}
  DJ_TRIGGER = tr;
  DJ_KEY = tr == 1 ? "jump" : (tr == 2 ? "jump or crouch" : "crouch");
  DJ_MAX_JUMPS = (int) clampD((double) {PKG}.SkillCfg.lng(p, "acro.doubleJump.maxJumps", 1L), 1.0, 5.0);
  DJ_MAX_FRAC = clampD({PKG}.SkillCfg.dbl(p, "acro.doubleJump.maxFraction", 1.0), 0.0, 1.5);
  DJ_MAX_BLOCKS = clampD({PKG}.SkillCfg.dbl(p, "acro.doubleJump.maxBlocks", 3.5), 0.5, 10.0);
  DJ_FORWARD = clampD({PKG}.SkillCfg.dbl(p, "acro.doubleJump.forwardPush", 2.0), 0.0, 10.0);
  DJ_STAMINA = clampD({PKG}.SkillCfg.dbl(p, "acro.doubleJump.stamina", 2.0), 0.0, 1000.0);
  DJ_REGEN_DELAY = clampD({PKG}.SkillCfg.dbl(p, "acro.doubleJump.staminaRegenDelay", 0.3), 0.0, 10.0);
  DJ_CD = (long) clampD((double) {PKG}.SkillCfg.lng(p, "acro.doubleJump.cooldownMs", 250L), 0.0, 60000.0);
  DJ_MIN_AIR = (long) clampD((double) {PKG}.SkillCfg.lng(p, "acro.doubleJump.minAirMs", 100L), 0.0, 5000.0);
  double mf = {PKG}.SkillCfg.dbl(p, "acro.doubleJump.maxFallSpeed", 0.0);
  DJ_MAX_FALL = Double.isNaN(mf) ? 0.0 : (mf > 1000.0 ? 1000.0 : mf);
  DJ_XP = clampD({PKG}.SkillCfg.dbl(p, "acro.doubleJump.xp", 0.0), 0.0, 1000.0);
  DJ_FX = {PKG}.SkillCfg.bool(p, "acro.doubleJump.fx", true);
  DJ_DEBUG = {PKG}.SkillCfg.bool(p, "acro.doubleJump.debug", false);
}}""", acfg))
acfg.addMethod(CtNewMethod.make(f"""
public static void ensureDj(java.util.Properties p) {{
  if (p.getProperty("acro.doubleJump.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DJ_DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Double Jump section (acro.doubleJump.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Double Jump section to xp.properties: " + t); }}
}}""", acfg))
acfg.addMethod(CtNewMethod.make("""
public static String djText() {
  if (!ENABLED) return "off (acro.enabled=false)";
  if (!DJ_ON) return "off (acro.doubleJump.enabled=false)";
  return "on (" + DJ_KEY + " in mid-air" + (DJ_DEBUG ? ", DEBUG chat lines on" : "") + ")";
}""", acfg))
''')

# ================================================================ S2 PartyCfg (before BridgeCfg = before SkillCfg.load, which calls it)
before('''# ================= BridgeCfg (0.4): bridge.* keys (skill:fn:addxp / skill:fn:craftxp) =================
''', r'''# ================= PartyCfg (0.4.2 stage 2): party.combatShare.* of xp.properties (beta backlog 6: "party should share combat XP") ======
# Read by SkillCfg.load (/skills reload re-reads it); appended ONCE to an existing file without party.combatShare.enabled (the FellCfg
# pattern; the code defaults are the same numbers).
pcg.addField(CtField.make("public static final String DEFAULTS = " + PARTY_LIT + ";", pcg))
for decl in ("boolean ON = true", "double FRACTION = 0.5", "double RADIUS = 48.0", "boolean TREE_BONUS = true", "boolean MESSAGE = true"):
    pcg.addField(CtField.make("public static volatile " + decl + ";", pcg))
pcg.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ON = {PKG}.SkillCfg.bool(p, "party.combatShare.enabled", true);
  double f = {PKG}.SkillCfg.dbl(p, "party.combatShare.fraction", 0.5);
  FRACTION = (Double.isNaN(f) || f < 0.0) ? 0.0 : (f > 1.0 ? 1.0 : f);
  double r = {PKG}.SkillCfg.dbl(p, "party.combatShare.radius", 48.0);
  RADIUS = (Double.isNaN(r) || r < 1.0) ? 1.0 : (r > 512.0 ? 512.0 : r);
  TREE_BONUS = {PKG}.SkillCfg.bool(p, "party.combatShare.treeBonus", true);
  MESSAGE = {PKG}.SkillCfg.bool(p, "party.combatShare.message", true);
}}""", pcg))
pcg.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  if (p.getProperty("party.combatShare.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Party combat XP section (party.combatShare.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Party combat XP section to xp.properties: " + t); }}
}}""", pcg))
pcg.addMethod(CtNewMethod.make("""
public static boolean on() {
  return ON && FRACTION > 0.0;
}""", pcg))
pcg.addMethod(CtNewMethod.make("""
public static String pct() {
  return String.valueOf(Math.round(FRACTION * 100.0)) + "%";
}""", pcg))
pcg.addMethod(CtNewMethod.make("""
public static String blocks() {
  double r = RADIUS;
  if (r == Math.floor(r)) return String.valueOf((long) r);
  return String.valueOf(Math.round(r * 10.0) / 10.0);
}""", pcg))
pcg.addMethod(CtNewMethod.make("""
public static String text() {
  if (!on()) return "off";
  return "on (" + pct() + " to party members within " + blocks() + " blocks" + (TREE_BONUS ? " + their tree XP bonus" : "") + ")";
}""", pcg))

''')

# ================================================================ S2 SkillCfg.load: ensure + read both blocks, reload summary
after('''    {PKG}.FellCfg.ensureDefaults(p);
''', '''    {PKG}.AcroCfg.ensureDj(p);
    {PKG}.PartyCfg.ensureDefaults(p);
''')
after('''    {PKG}.FellCfg.read(p);
''', '''    {PKG}.AcroCfg.readDj(p);
    {PKG}.PartyCfg.read(p);
''')
rep('''", felled trees " + {PKG}.FellCfg.text() + ", bridge skills "''',
    '''", felled trees " + {PKG}.FellCfg.text() + ", double jump " + {PKG}.AcroCfg.djText() + ", party combat XP " + {PKG}.PartyCfg.text() + ", bridge skills "''')

# ================================================================ S2 Acro: STATE 292, resets, the double jump methods, the AcroSys hook
before('''acro.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap STATE = new java.util.concurrent.ConcurrentHashMap();", acro))''',
       '''# 0.4.2 stage 2 (Double-Jump-Spec 3.2): double[292]: 281 prev crouching, 282 air jumps used since the last ground contact, 283 last double
#  jump ms, 284 airborne-since ms (0 = grounded), 285 prev jumping (own copy; s[5] belongs to move()), 286 last debug line ms,
#  287 prev extraJumpsUsed, 288-291 spare. reset (world change) and profileReset also zero 281, 282, 284 and 285.
''')
rep('''  double[] n = new double[281];''', '''  double[] n = new double[292];''')
rep('''  s[3] = 0.0; s[5] = 0.0; s[6] = 0.0; s[8] = 0.0; s[18] = 0.0; s[23] = 0.0;
}''', '''  s[3] = 0.0; s[5] = 0.0; s[6] = 0.0; s[8] = 0.0; s[18] = 0.0; s[23] = 0.0;
  s[281] = 0.0; s[282] = 0.0; s[284] = 0.0; s[285] = 0.0;
}''')
rep('''  s[15] = 0.0; s[16] = 0.0; s[17] = 0.0; s[18] = 0.0; s[21] = 0.0; s[152] = 0.0;
}''', '''  s[15] = 0.0; s[16] = 0.0; s[17] = 0.0; s[18] = 0.0; s[21] = 0.0; s[152] = 0.0;
  s[281] = 0.0; s[282] = 0.0; s[284] = 0.0; s[285] = 0.0;
}''')
before('''# AcroSys: EntityTickingSystem on Player entities (AccEffects pattern; runs on the world thread, not parallel)
''', r'''# ---- 0.4.2 stage 2: DOUBLE JUMP (research/Double-Jump-Spec.md 3.2). All of it runs in AcroSys.tick on the world thread. ----
acro.addField(CtField.make("public static volatile boolean DJ_WARNED = false;", acro))
# the node value = air-jump height as a fraction of the player's own jump height (SkyyTrees 0.2.1 skill:bonus doublejump.acrobatics,
# 0.55-1.0), clamped to acro.doubleJump.maxFraction; 0 = no node (also: node toggled off in /tree, bridge.bonus.enabled=false)
acro.addMethod(CtNewMethod.make(f"""
public static double djFraction(java.util.UUID u) {{
  if (u == null) return 0.0;
  double f = {PKG}.SkillBonus.sum(u, "doublejump.acrobatics");
  if (!(f > 0.0)) return 0.0;
  return f > {PKG}.AcroCfg.DJ_MAX_FRAC ? {PKG}.AcroCfg.DJ_MAX_FRAC : f;
}}""", acro))
# the REAL game mode (SkillXp.creative returns false when creativeXp=true, so it must not be reused here)
acro.addMethod(CtNewMethod.make(f"""
public static boolean creativeMode({ST} st, {REF} r) {{
  try {{
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    return p != null && p.getGameMode() == {GM}.Creative;
  }} catch (Throwable t) {{ return false; }}
}}""", acro))
# rule 7 falling-speed gate, 0 = no limit. Reads the WORLD's MovementConfig asset exactly like DamageSystems$FallDamagePlayers does for
# real fall damage. Do NOT "simplify" this to djSettings(...).minFallSpeedToEngageRoll: that per-player protocol MovementSettings is a
# toPacket() copy that movement mods rewrite, and fall damage never reads it, so the two can drift apart.
acro.addMethod(CtNewMethod.make(f"""
public static double djMaxFall({ST} store) {{
  double c = {PKG}.AcroCfg.DJ_MAX_FALL;
  if (c < 0.0) return 0.0;
  if (c > 0.0) return c;
  try {{
    {WLD} w = (({EST}) store.getExternalData()).getWorld();
    int mi = w.getGameplayConfig().getPlayerConfig().getMovementConfigIndex();
    {MCF} mc = ({MCF}) {MCF}.getAssetMap().getAsset(mi);
    if (mc != null && mc.getMinFallSpeedToEngageRoll() > 0.0f) return (double) mc.getMinFallSpeedToEngageRoll();
  }} catch (Throwable t) {{ }}
  return 21.0;
}}""", acro))
acro.addMethod(CtNewMethod.make(f"""
public static {MVS} djSettings({ST} store, {REF} ref) {{
  try {{
    {MMG} mm = ({MMG}) store.getComponent(ref, {MMG}.getComponentType());
    if (mm == null) return null;
    return mm.getSettings();
  }} catch (Throwable t) {{ return null; }}
}}""", acro))
# rule 5: false = not enough Stamina (no jump, the charge is kept); the cost is taken only when the jump really happens. The regen
# pause is its own try: a missing StaminaRegenDelay stat never cancels a jump that was already paid for.
acro.addMethod(CtNewMethod.make(f"""
public static boolean djStamina({CB} cb, {REF} ref) {{
  double cost = {PKG}.AcroCfg.DJ_STAMINA;
  if (cost <= 0.0) return true;
  try {{
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());
    if (m == null) return true;
    int si = {DST}.getStamina();
    {ESV} sv = m.get(si);
    if (sv == null) return true;
    if ((double) sv.get() < cost) return false;
    m.subtractStatValue(si, (float) cost);
    if ({PKG}.AcroCfg.DJ_REGEN_DELAY > 0.0) {{
      try {{
        int di = {ESTT}.getAssetMap().getIndex("StaminaRegenDelay");
        if (di >= 0) m.setStatValue(di, (float) (0.0 - {PKG}.AcroCfg.DJ_REGEN_DELAY));
      }} catch (Throwable t2) {{ }}
    }}
    return true;
  }} catch (Throwable t) {{
    if (!DJ_WARNED) {{ DJ_WARNED = true; {PKG}.SkillCfg.warn("double jump stamina failed (logged once): " + t); }}
    return false;
  }}
}}""", acro))
# optional polish (acro.doubleJump.fx), never throws: the native extra-jump sound of Debug_Movement_Boots + vanilla Double_Jump.json's
# particle at the feet (target list = the jumper, the TerrariaAddons pattern)
acro.addMethod(CtNewMethod.make(f"""
public static void djFx({ST} store, {REF} ref) {{
  if (!{PKG}.AcroCfg.DJ_FX) return;
  {V3D} p = null;
  try {{
    {TRC} tc = ({TRC}) store.getComponent(ref, {TRC}.getComponentType());
    if (tc != null) p = tc.getPosition();
  }} catch (Throwable t) {{ p = null; }}
  if (p == null) return;
  try {{
    int si = {SEV}.getAssetMap().getIndex("SFX_Player_Jump");
    if (si >= 0) {SNU}.playSoundEvent3d(si, {SCAT}.SFX, p, store);
  }} catch (Throwable t) {{ }}
  try {{
    {PTU}.spawnParticleEffect("Impact_Feathers_Black", p, java.util.Collections.singletonList(ref), store);
  }} catch (Throwable t) {{ }}
}}""", acro))
# acro.doubleJump.debug (spec test 5.0): one chat line per airborne edge, admins only, at most one per 200 ms
acro.addMethod(CtNewMethod.make(f"""
public static void djDebug(double[] s, {PR} pr, String what, double vy, long now) {{
  if (pr == null || (double) now - s[286] < 200.0) return;
  try {{ if (!pr.hasPermission("skyyskills.admin")) return; }} catch (Throwable t) {{ return; }}
  s[286] = (double) now;
  long air = 0L;
  if (s[284] > 0.0) air = now - (long) s[284];
  pr.sendMessage({MSG}.raw("[Skills] DJ debug: " + what + " in air - vy " + (Math.round(vy * 10.0) / 10.0) + " - air " + air + " ms - used " + (int) s[282]).color("#c8a0ff"));
}}""", acro))
# PURE (no engine object, bare-JVM tested): the edges of this tick and the airtime. Returns bits 1 = crouch press, 2 = jump press,
# 4 = extraJumpsUsed changed; 0 = on the ground / climbing / in fluid / swimming / mantling (charge + airtime reset, spec 2.3 rule 2),
# in any other Acro.excludedState (mounted / flying / gliding / sitting / sleeping: airtime restarts, the charge is KEPT - review fix:
# time spent flying or gliding no longer counts toward minAirMs, and a mid-air glide toggle can never refill the jump) or no edge.
acro.addMethod(CtNewMethod.make(f"""
public static int airTrack(double[] s, {MVT} ms, long now) {{
  boolean cEdge = ms.crouching && s[281] < 0.5;
  boolean jEdge = ms.jumping && s[285] < 0.5;
  int xj = (int) ms.extraJumpsUsed;
  boolean xEdge = (double) xj != s[287];
  s[281] = ms.crouching ? 1.0 : 0.0;
  s[285] = ms.jumping ? 1.0 : 0.0;
  s[287] = (double) xj;
  if (ms.onGround || ms.climbing || ms.inFluid || ms.swimming || ms.mantling) {{ s[282] = 0.0; s[284] = 0.0; return 0; }}
  if (excludedState(ms)) {{ s[284] = 0.0; return 0; }}
  if (s[284] <= 0.0) s[284] = (double) now;
  int bits = 0;
  if (cEdge) bits = bits | 1;
  if (jEdge) bits = bits | 2;
  if (xEdge) bits = bits | 4;
  return bits;
}}""", acro))
# PURE: true = this tick has an edge of the configured trigger (acro.doubleJump.trigger crouch 0 / jump 1 / both 2). airJump's coarse
# gate (review fix: a stray edge of the other key no longer runs the node / movement-settings / MovementConfig lookups); airTry keeps
# its own byCrouch / byJump (rule J needs them).
acro.addMethod(CtNewMethod.make(f"""
public static boolean djTrig(int bits) {{
  int trig = {PKG}.AcroCfg.DJ_TRIGGER;
  if (trig != 1 && (bits & 1) != 0) return true;
  return trig != 0 && (bits & 2) != 0;
}}""", acro))
# PURE: the gates of spec 2.3 that need no engine object + the push speed. f = node fraction, vy0 = the client's vertical speed now,
# mf = falling-speed limit (0 = none), jf / fj = the player's jumpForce / fallJumpForce. Returns vy > 0 = jump now, else a reason:
# -1 no trigger edge, -2 too soon after leaving the ground, -3 no charge left, -4 cooldown, -5 no node, -6 falling too fast,
# -7 jump mode: the client jumped itself (coyote / buffered jump, rule J), -8 no push.
acro.addMethod(CtNewMethod.make(f"""
public static double airTry(double[] s, int bits, long now, double f, double vy0, double mf, double jf, double fj) {{
  int trig = {PKG}.AcroCfg.DJ_TRIGGER;
  boolean byCrouch = trig != 1 && (bits & 1) != 0;
  boolean byJump = trig != 0 && (bits & 2) != 0;
  if (!byCrouch && !byJump) return -1.0;
  if ((double) now - s[284] < (double) {PKG}.AcroCfg.DJ_MIN_AIR) return -2.0;
  if (s[282] >= (double) {PKG}.AcroCfg.DJ_MAX_JUMPS) return -3.0;
  if ((double) now - s[283] < (double) {PKG}.AcroCfg.DJ_CD) return -4.0;
  if (!(f > 0.0)) return -5.0;
  if (mf > 0.0 && vy0 < 0.0 - mf) return -6.0;
  if (!byCrouch && vy0 > 0.5 * fj) return -7.0;
  double vy = jf * Math.sqrt(f);
  double cap = Math.sqrt(2.0 * {PHC}.GRAVITY_ACCELERATION * {PKG}.AcroCfg.DJ_MAX_BLOCKS);
  if (vy > cap) vy = cap;
  if (!(vy > 0.0)) return -8.0;
  return vy;
}}""", acro))
# the engine glue (world thread, every tick). Stamina is taken AFTER every other gate, so a refused jump never costs Stamina or a charge.
# Review fix: the debug probe (spec test 5.0) runs BEFORE the acro.doubleJump.enabled check, so it also reports edges while the double
# jump itself is off (it still needs acro.enabled: AcroSys only calls airJump then).
acro.addMethod(CtNewMethod.make(f"""
public static void airJump(double[] s, {ST} store, {CB} cb, {REF} ref, {PR} pr, java.util.UUID u, {MVT} ms, long now) {{
  if (ms == null) return;
  int bits = airTrack(s, ms, now);
  if (bits == 0) return;
  if (!{PKG}.AcroCfg.DJ_ON && !{PKG}.AcroCfg.DJ_DEBUG) return;
  {VEL} v = ({VEL}) cb.getComponent(ref, {VEL}.getComponentType());
  {V3D} cv = null;
  if (v != null) cv = v.getClientVelocity();
  double vy0 = 0.0;
  if (cv != null) vy0 = cv.y();
  if ({PKG}.AcroCfg.DJ_DEBUG) {{
    String what = "extraJumpsUsed " + (int) ms.extraJumpsUsed;
    if ((bits & 2) != 0) what = "jump edge";
    if ((bits & 1) != 0) what = "crouch edge";
    djDebug(s, pr, what, vy0, now);
  }}
  if (!{PKG}.AcroCfg.DJ_ON || !djTrig(bits) || v == null || cv == null) return;
  if (excludedState(ms) || creativeMode(store, ref)) return;
  double f = djFraction(u);
  if (f <= 0.0) return;
  {MVS} st = djSettings(store, ref);
  double jf = 11.8;
  double fj = 7.0;
  if (st != null && st.jumpForce > 0.0f) jf = (double) st.jumpForce;
  if (st != null && st.fallJumpForce > 0.0f) fj = (double) st.fallJumpForce;
  double vy = airTry(s, bits, now, f, vy0, djMaxFall(store), jf, fj);
  if (vy <= 0.0) return;
  if (!djStamina(cb, ref)) return;
  double hx = cv.x();
  double hz = cv.z();
  double hl = Math.sqrt(hx * hx + hz * hz);
  double fw = {PKG}.AcroCfg.DJ_FORWARD;
  if (hl >= 1.0 && fw > 0.0) {{ hx = hx + hx / hl * fw; hz = hz + hz / hl * fw; }}
  v.addInstruction(new {V3D}(hx, vy, hz), ({VCF}) null, {CVT}.Set);
  s[282] = s[282] + 1.0;
  s[283] = (double) now;
  s[9] = (double) now;
  if ({PKG}.AcroCfg.DJ_XP > 0.0 && !{PKG}.SkillXp.creative(store, ref)) s[11] = s[11] + {PKG}.AcroCfg.DJ_XP;
  djFx(store, ref);
}}""", acro))
# Stats page line while the node is owned (null = no node); the key words follow acro.doubleJump.trigger
acro.addMethod(CtNewMethod.make(f"""
public static String djLine(java.util.UUID u) {{
  double f = djFraction(u);
  if (f <= 0.0) return null;
  if (!{PKG}.AcroCfg.DJ_ON) return "Double Jump (skill tree) is turned off on this server";
  double st = {PKG}.AcroCfg.DJ_STAMINA;
  String sc = String.valueOf(st);
  if (st == Math.floor(st)) sc = String.valueOf((long) st);
  String cost = "";
  if (st > 0.0) cost = " - " + sc + " Stamina";
  return "Double Jump: press " + {PKG}.AcroCfg.DJ_KEY + " in mid-air for a " + Math.round(f * 100.0) + "% jump" + cost;
}}""", acro))
# bridge skill:dj:key (spec 3.3) for the SkyyTrees 0.2.1 card "Press %K in mid-air": setup + /skills reload; removed in shutdown
acro.addMethod(CtNewMethod.make(f"""
public static void djPublish() {{
  try {{ {PKG}.SkillStore.bridge().put("skill:dj:key", {PKG}.AcroCfg.DJ_KEY); }} catch (Throwable t) {{ }}
}}""", acro))

''')
after('''      if (ms != null && pos != null) {PKG}.Acro.move(s, ms, pos, dt, now, creative);
''', '''      {PKG}.Acro.airJump(s, store, cb, ref, pr, u, ms, now);
''')

# ================================================================ S2 PartyXp chat batching (before SkillXp: gain4 calls PartyXp.note / send)
before('''# ================= SkillXp: award + level-up (world thread) =================
''', r'''# ================= PartyXp chat (0.4.2 stage 2) - BEFORE SkillXp: SkillXp.gain4 calls PartyXp.note and its level-up branch PartyXp.send =================
# Chat: PEND uuid -> long[N + 1] (XP per slot, [N] = number of shares), WHO uuid -> killer name ("" = several), LAST uuid -> ms of the last
# line: "[Party] +6 Archery XP (340/500) from Skyy's kill", sent at most once per feedbackMs (SkillMsg's throttle), leftovers by the
# 1 s ticker (flushDue -> PartyFlushTask on the member's world thread). /skills quiet, feedback=false, party.combatShare.message=false hide it.
# Review fix (level-up order): gain4 notes the share right after the XP is added (exactly where gain3 calls SkillMsg.note) and a level up
# flushes this queue right after SkillMsg's, so the "[Party] +N ... XP" line always prints BEFORE the SKILL LEVEL UP it causes.
pxp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();", pxp))
pxp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap WHO = new java.util.concurrent.ConcurrentHashMap();", pxp))
pxp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();", pxp))
# chat batching (synchronized methods, never a multi-statement synchronized block)
pxp.addMethod(CtNewMethod.make(f"""
public static synchronized boolean add(java.util.UUID u, int slot, long amt, String from) {{
  String fr = from == null ? "" : from;
  long[] p = (long[]) PEND.get(u);
  if (p == null) {{
    p = new long[{PKG}.SkillDefs.N + 1];
    PEND.put(u, p);
    WHO.put(u, fr);
  }} else {{
    Object w = WHO.get(u);
    if (!(w instanceof String) || !((String) w).equals(fr)) WHO.put(u, "");
  }}
  p[slot] += amt;
  p[{PKG}.SkillDefs.N] += 1L;
  Long last = (Long) LAST.get(u);
  return last == null || System.currentTimeMillis() - last.longValue() >= {PKG}.SkillCfg.FEEDBACK_MS;
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static synchronized String take(java.util.UUID u) {{
  long[] p = (long[]) PEND.get(u);
  if (p == null) return null;
  Object wo = WHO.get(u);
  String who = wo instanceof String ? (String) wo : "";
  PEND.remove(u);
  WHO.remove(u);
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  long[] d = {PKG}.SkillStore.data(u);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
    if (p[i] <= 0L) continue;
    if (sb.length() > 0) sb.append("    ");
    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillClass.skillName(u, i)).append(" XP (").append({PKG}.SkillDefs.progress(d[i])).append(")");
  }}
  if (sb.length() == 0) return null;
  long n = p[{PKG}.SkillDefs.N];
  String src;
  if (who.length() > 0) src = n > 1L ? n + " kills by " + who : who + "'s kill";
  else src = n + " party kills";
  return "[Party] " + sb.toString() + " from " + src;
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static void send({PR} pr) {{
  try {{
    String s = take(pr.getUuid());
    if (s != null) pr.sendMessage({MSG}.raw(s).color("#a8e8c0"));
  }} catch (Throwable t) {{ }}
}}""", pxp))
pxp.addMethod(CtNewMethod.make("""
public static synchronized void drop(java.util.UUID u) {
  PEND.remove(u);
  WHO.remove(u);
  LAST.remove(u);
}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static void note({PR} pr, int slot, long amt, String from) {{
  if (!{PKG}.PartyCfg.MESSAGE || !{PKG}.SkillCfg.FEEDBACK || pr == null || amt <= 0L) return;
  if (slot < 0 || slot >= {PKG}.SkillDefs.N) return;
  java.util.UUID u = pr.getUuid();
  if ({PKG}.SkillStore.quiet(u)) return;
  if (add(u, slot, amt, from)) send(pr);
}}""", pxp))

''')

# ================================================================ S2 SkillXp.gain4 = gain3 + the party note (review fix: [Party] line before SKILL LEVEL UP)
rep('''public static void gain3({PR} pr, int skill, long amount, boolean note, boolean bonus) {{
  if (pr == null || amount <= 0L || skill < 0 || skill >= {PKG}.SkillDefs.N) return;
''', '''public static void gain4({PR} pr, int skill, long amount, boolean note, boolean bonus, String party) {{
  if (pr == null || amount <= 0L || skill < 0 || skill >= {PKG}.SkillDefs.N) return;
''')
after('''  if (note) {PKG}.SkillMsg.note(pr, skill, amount);
''', '''  if (party != null) {PKG}.PartyXp.note(pr, skill, amount, party);
''')
after('''  if (r[1] > r[0]) {{
    {PKG}.SkillMsg.send(pr);
''', '''    {PKG}.PartyXp.send(pr);
''')
before('''# 0.4 trees bridge: gain2 = gain3 WITH the skill-tree XP bonus (every normal award).''', '''# 0.4.2 stage 2: gain3 = gain4 without a party note (every caller before 0.4.2 is unchanged); PartyXp.one calls gain4 with the killer's name
xp.addMethod(CtNewMethod.make(f"""
public static void gain3({PR} pr, int skill, long amount, boolean note, boolean bonus) {{
  gain4(pr, skill, amount, note, bonus, null);
}}""", xp))
''')

# ================================================================ S2 PartyXp + PartyFlushTask (before the ECS systems: KillSys calls PartyXp.share)
before('''# ================= ECS systems =================
''', r'''# ================= PartyXp (0.4.2 stage 2, beta backlog 6: "party should share combat XP") =================
# World thread (called by KillSys after the killer's own award). Every OTHER member of the killer's SkyyParty party (party:fn:members,
# String[] of member UUIDs, leader first; empty when not in a party) who is online, in the SAME world (their Ref lives in the killer's
# entity store = this world thread, so their components may be read here), ready, alive, not in creative (the creativeXp rule of a
# normal kill) and within party.combatShare.radius blocks of the killer gets amount(base, fraction) into THEIR OWN current class skill:
# SkillClass.slot of THEIR class (needs SkyyClasses + a class; skipped while their class still follows a profile switch - consistent()),
# written through SkillXp.gain4 = THEIR active profile (pkey). Only the killer needs a class weapon (KillSys.killSlot). base = the
# killer's kill XP after the xp multiplier and BEFORE the killer's tree bonus; the member's own tree XP bonus applies with
# party.combatShare.treeBonus. The killer keeps 100 % (KillSys pays them first, unchanged).
# Chat batching (PEND / WHO / LAST, add / take / send / drop / note) is the "PartyXp chat" block before SkillXp (gain4 calls it).
pxp.addField(CtField.make("public static volatile boolean FAILED_ONCE = false;", pxp))
# base x fraction, the fractional part paid by chance (1 XP x 50 % = 1 XP half of the time)
pxp.addMethod(CtNewMethod.make("""
public static long amount(long base, double fr) {
  if (base <= 0L || !(fr > 0.0)) return 0L;
  if (fr > 1.0) fr = 1.0;
  double x = (double) base * fr;
  long w = (long) Math.floor(x);
  double f = x - (double) w;
  if (f > 0.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() < f) w++;
  return w;
}""", pxp))
# party:fn:members as String[] (null = SkyyParty missing or no answer)
pxp.addMethod(CtNewMethod.make(f"""
public static String[] members(java.util.UUID u) {{
  try {{
    Object f = {PKG}.SkillStore.bridge().get("party:fn:members");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(u);
    if (!(r instanceof Object[])) return null;
    Object[] a = (Object[]) r;
    String[] out = new String[a.length];
    for (int i = 0; i < a.length; i++) out[i] = a[i] == null ? null : String.valueOf(a[i]);
    return out;
  }} catch (Throwable t) {{ return null; }}
}}""", pxp))
# the receiving member's class skill slot, -1 = none (SkyyClasses missing, no / unknown class, class still following a profile switch)
pxp.addMethod(CtNewMethod.make(f"""
public static int slotFor(java.util.UUID u) {{
  if ({PKG}.SkillClass.allowedFn() == null) return -1;
  if (!{PKG}.SkillClass.consistent(u)) return -1;
  return {PKG}.SkillClass.slot(u);
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static {V3D} pos({ST} s, {REF} r) {{
  try {{
    {TRC} tc = ({TRC}) s.getComponent(r, {TRC}.getComponentType());
    if (tc == null) return null;
    return tc.getPosition();
  }} catch (Throwable t) {{ return null; }}
}}""", pxp))
# leftovers: the 1 s ticker hands each due line to the member's world thread (SkillMsg.flushDue pattern)
pft.addInterface(pool.get("java.lang.Runnable"))
pft.addField(CtField.make("public java.util.UUID u;", pft))
pft.addConstructor(CtNewConstructor.make("public PartyFlushTask(java.util.UUID u) { this.u = u; }", pft))
pft.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) {{ {PKG}.PartyXp.drop(this.u); return; }}
    {PKG}.PartyXp.send(pr);
  }} catch (Throwable t) {{ }}
}}""", pft))
pxp.addMethod(CtNewMethod.make(f"""
public static void flushDue() {{
  try {{
    if (PEND.isEmpty()) return;
    long now = System.currentTimeMillis();
    java.util.Iterator it = new java.util.ArrayList(PEND.keySet()).iterator();
    while (it.hasNext()) {{
      java.util.UUID u = (java.util.UUID) it.next();
      Long last = (Long) LAST.get(u);
      if (last != null && now - last.longValue() < {PKG}.SkillCfg.FEEDBACK_MS) continue;
      {PR} pr = {UNI}.get().getPlayer(u);
      if (pr == null || !pr.isValid()) {{ drop(u); continue; }}
      {WLD} w = {UNI}.get().getWorld(pr.getWorldUuid());
      if (w == null) continue;
      LAST.put(u, Long.valueOf(now));
      try {{ w.execute(new {PKG}.PartyFlushTask(u)); }} catch (Throwable t) {{ }}
    }}
  }} catch (Throwable t) {{ }}
}}""", pxp))
# every 30 s (SkillTick): forget players who left (LAST outlives PEND)
pxp.addMethod(CtNewMethod.make(f"""
public static void retainOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr != null) online.add(pr.getUuid());
    }}
    LAST.keySet().retainAll(online);
    PEND.keySet().retainAll(online);
    WHO.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", pxp))
# one member: every rule of the header comment; returns the XP paid (0 = skipped)
pxp.addMethod(CtNewMethod.make(f"""
public static long one(java.util.UUID ku, String kn, {V3D} kpos, {ST} s, String mid, long base, double fr, double r2) {{
  if (mid == null || mid.trim().length() == 0) return 0L;
  java.util.UUID mu = java.util.UUID.fromString(mid.trim());
  if (mu.equals(ku)) return 0L;
  {PR} mp = {UNI}.get().getPlayer(mu);
  if (mp == null || !mp.isValid()) return 0L;
  {REF} mr = mp.getReference();
  if (mr == null || !mr.isValid() || mr.getStore() != s) return 0L;
  {PLA} pl = ({PLA}) s.getComponent(mr, {PLA}.getComponentType());
  if (pl == null || pl.isWaitingForClientReady()) return 0L;
  if ({PKG}.SkillXp.creative(s, mr) || !{PKG}.Acro.alive(s, mr)) return 0L;
  {V3D} mpos = pos(s, mr);
  if (mpos == null) return 0L;
  double dx = mpos.x() - kpos.x();
  double dy = mpos.y() - kpos.y();
  double dz = mpos.z() - kpos.z();
  if (dx * dx + dy * dy + dz * dz > r2) return 0L;
  int slot = slotFor(mu);
  if (slot < 0) return 0L;
  long amt = amount(base, fr);
  if (amt <= 0L) return 0L;
  if ({PKG}.PartyCfg.TREE_BONUS) amt = {PKG}.SkillBonus.boost(mu, slot, amt);
  {PKG}.SkillXp.gain4(mp, slot, amt, false, false, kn == null ? "" : kn);
  return amt;
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static void share({PR} kp, {REF} kr, {ST} s, long base) {{
  if (!{PKG}.PartyCfg.on() || base <= 0L || kp == null || kr == null || s == null) return;
  double fr = {PKG}.PartyCfg.FRACTION;
  java.util.UUID ku = kp.getUuid();
  String[] ms = members(ku);
  if (ms == null || ms.length < 2) return;
  {V3D} kpos = pos(s, kr);
  if (kpos == null) return;
  double rad = {PKG}.PartyCfg.RADIUS;
  double r2 = rad * rad;
  String kn = null;
  try {{ kn = kp.getUsername(); }} catch (Throwable t) {{ kn = null; }}
  for (int i = 0; i < ms.length; i++) {{
    try {{
      one(ku, kn, kpos, s, ms[i], base, fr, r2);
    }} catch (Throwable t) {{
      if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("party combat XP share failed (logged once): " + t); }}
    }}
  }}
}}""", pxp))
# the class how-to line of the Stats page ("" while off or SkyyParty is not loaded)
pxp.addMethod(CtNewMethod.make(f"""
public static String howText() {{
  if (!{PKG}.PartyCfg.on()) return "";
  try {{
    if (!({PKG}.SkillStore.bridge().get("party:fn:members") instanceof java.util.function.Function)) return "";
  }} catch (Throwable t) {{ return ""; }}
  return ". Party members within " + {PKG}.PartyCfg.blocks() + " blocks get " + {PKG}.PartyCfg.pct() + " of your kill XP (in their own class skill)";
}}""", pxp))

''')

# ================================================================ S2 KillSys: the killer is paid exactly as before, then the party share
rep('''    {PKG}.SkillXp.gain(pr, slot, {PKG}.SkillCfg.combatXp(role, maxHp));
''', '''    long cx = {PKG}.SkillCfg.combatXp(role, maxHp);
    {PKG}.SkillXp.gain(pr, slot, cx);
    {PKG}.PartyXp.share(pr, k, s, cx);
''')

# ================================================================ S2 Stats page: Acrobatics tree line + Double Jump line, class how-to
after('''  if (dg > 0.00001) parts.add("+" + pc(dg) + " dodge push");
''', '''  double djf = {PKG}.Acro.djFraction(u);
  if (djf > 0.00001) parts.add("double jump " + pc(djf));
''')
after('''      if (db > 0.00001) out.add("+" + pc(db) + " dodge push");
''', '''      if (!next) {{
        String dj = {PKG}.Acro.djLine(u);
        if (dj != null) out.add(dj);
      }}
''')
rep('''  return "Earn XP by defeating monsters with " + c + " weapons" + (w == null ? "" : " - " + w);''',
    '''  return "Earn XP by defeating monsters with " + c + " weapons" + (w == null ? "" : " - " + w) + {PKG}.PartyXp.howText();''')

# ================================================================ S2 ticker, reload, plugin setup / shutdown / log line, class list, manifest
after('''  try {{ {PKG}.SkillMsg.flushDue(); }} catch (Throwable t) {{ }}
''', '''  try {{ {PKG}.PartyXp.flushDue(); }} catch (Throwable t) {{ }}
''')
rep('''  if (this.n % 30L == 0L) {{ try {{ {PKG}.Acro.retainOnline(); }} catch (Throwable t) {{ }} }}''',
    '''  if (this.n % 30L == 0L) {{ try {{ {PKG}.Acro.retainOnline(); }} catch (Throwable t) {{ }} try {{ {PKG}.PartyXp.retainOnline(); }} catch (Throwable t) {{ }} }}''')
rep('''  pr.sendMessage({MSG}.raw("[Skills] xp.properties reloaded: " + {PKG}.SkillCfg.load()));''',
    '''  String res = {PKG}.SkillCfg.load();
  {PKG}.Acro.djPublish();
  pr.sendMessage({MSG}.raw("[Skills] xp.properties reloaded: " + res));''')
after('''  String rules = {PKG}.SkillCfg.load();
''', '''  {PKG}.Acro.djPublish();
''')
after('''  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:felledBy"); }} catch (Throwable t) {{ }}
''', '''  try {{ {PKG}.SkillStore.bridge().remove("skill:dj:key"); }} catch (Throwable t) {{ }}
''')
rep('''no boosters); felled trees " + {PKG}.FellCfg.text() + ";''',
    '''no boosters); felled trees " + {PKG}.FellCfg.text() + "; double jump " + {PKG}.AcroCfg.djText() + " (bridge skill:dj:key); party combat XP " + {PKG}.PartyCfg.text() + ";''')
rep('''          fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy):''', '''          fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft):''')
rep('''kills with class weapons and running / jumping / big survived falls / dodging.''',
    '''kills with class weapons (nearby SkyyParty members get a share in their own class skill) and running / jumping / big survived falls / dodging (+ the Acrobatics tree Double Jump: crouch in mid-air).''')

# ================================================================ sanity
assert 'VERSION = "0.4.2"' in s and "0.4.2 (research/Tree-Fall-Spec.md sections 2, 3.1 and 4" in s
assert s.count("{PKG}.FellCfg.ensureDefaults(p);") == 1 and s.count("{PKG}.FellCfg.read(p);") == 1
assert s.index("{PKG}.FellCfg.read(p);") < s.index("{PKG}.BridgeCfg.read(p);")
# dependency order (javassist compiles each method when it is added): FellCfg before SkillCfg.load, the Fell block before BreakTask,
# BreakSys after the Fell block, FellWatch.run after FellCredit.one, SkillBonus.felled before FellCredit
assert s.index('fcf.addMethod(CtNewMethod.make(f"""\npublic static void read(') < s.index("public static synchronized String load()")
assert s.index("# ================= 0.4.2 FELLED TREES") < s.index("# ================= deferred tasks")
assert s.index("public static void felled({PR} pr, int row") < s.index("# ================= 0.4.2 FELLED TREES")
assert s.index("public static void one({PKG}.FellWatch W, int i)") < s.index('fwt.addMethod(CtNewMethod.make(f"""\npublic void run()')
assert s.index("public static void commit({PKG}.FellSnap s0)") < s.index('event_system(bsy, "BreakSys"')
assert s.index("public static void collDouble(") < s.index("public static void doubled(")
assert s.count("registerSystem(new {PKG}.EnvSys())") == 1 and s.count("registerSystem(new {PKG}.BreakSys())") == 1
assert s.count('bridge().putIfAbsent("skill:on:felled"') == 1 and s.count('bridge().put("skill:fn:felledBy"') == 1
assert s.count('bridge().remove("skill:fn:felledBy")') == 1 and s.count("{PKG}.Fell.endAll();") == 1
assert s.count("new {PKG}.BreakTask(e, pr.getUuid(), w.getName(), rule, fs, unclaimed)") == 1
assert s.count("{PKG}.Fell.commit(({PKG}.FellSnap) this.fs);") == 1 and s.count("{PKG}.Fell.restore(this.world, this.ev, this.unclaimed);") == 1
assert s.index("{PKG}.Fell.commit(({PKG}.FellSnap) this.fs);") < s.index("{PKG}.SkillBonus.gather(pr, (int) this.rule[0]"), "commit must run before gather (Tree Feller)"
assert "Width: 640, Height: 530" not in s and s.count("Width: 960, Height: 795") == 1 and "#SkyyStBar\", \"Group {{ Anchor: (Left: 0, Top: 0, Width: \" + fill + \", Height: 12)" not in s
assert s.count('"skills:felled", W.pk') == 1 and s.count('"skills:double", k') == 1
assert "fell.enabled=true" in s and "FELL_LIT" in s
# stage 2: dependency order (javassist compiles each method when it is added) and the hooks
assert s.index("public static void readDj(java.util.Properties p)") < s.index("public static synchronized String load()")
assert s.index("# ================= PartyCfg (0.4.2 stage 2)") < s.index("public static synchronized String load()")
assert s.index("public static String djText()") < s.index("public static synchronized String load()")
assert s.count("{PKG}.AcroCfg.ensureDj(p);") == 1 and s.count("{PKG}.AcroCfg.readDj(p);") == 1
assert s.count("{PKG}.PartyCfg.ensureDefaults(p);") == 1 and s.count("{PKG}.PartyCfg.read(p);") == 1
assert s.index("public static int airTrack(") < s.index("public static double airTry(") < s.index("public static void airJump(")
assert s.index("public static void airJump(") < s.index("public void tick(float dt, int idx, {ACH} chunk, {ST} store, {CB} cb)")
assert s.count("{PKG}.Acro.airJump(s, store, cb, ref, pr, u, ms, now);") == 1
assert s.index("{PKG}.Acro.move(s, ms, pos, dt, now, creative);") < s.index("{PKG}.Acro.airJump(s, store, cb, ref, pr, u, ms, now);") \
    < s.index("{PKG}.Acro.dodge(s, store, cb, ref, u, now, creative, {PKG}.Acro.excludedState(ms));")
assert s.count("new double[292]") == 1 and "new double[281]" not in s
assert s.count("s[281] = 0.0; s[282] = 0.0; s[284] = 0.0; s[285] = 0.0;") == 2
assert s.index("public static String djLine(java.util.UUID u)") < s.index("public static String acroTreeLine(java.util.UUID u)")
assert s.index("# ================= PartyXp (0.4.2 stage 2") < s.index("public void onComponentAdded({REF} r, {CMP} c, {ST} s, {CB} b)")
assert s.index("public static synchronized String take(java.util.UUID u) {{\n  long[] p = (long[]) PEND.get(u);\n  if (p == null) return null;\n  Object wo") \
    < s.index('pft.addMethod(CtNewMethod.make(f"""\npublic void run()') < s.index("public static void flushDue() {{\n  try {{\n    if (PEND.isEmpty())")
assert s.index("public static long one(") < s.index("public static void share({PR} kp")
# stage 2 review fixes: [Party] line before SKILL LEVEL UP (PartyXp chat block compiled before SkillXp.gain4), debug probe before the
# enabled gate, trigger-aware coarse gate, airtime restart in every excludedState (charge kept)
assert s.index("public static void note({PR} pr, int slot, long amt, String from)") < s.index("public static void gain4({PR} pr")
assert s.index("public static void send({PR} pr) {{\n  try {{\n    String s = take(pr.getUuid());\n    if (s != null) pr.sendMessage({MSG}.raw(s).color(\"#a8e8c0\"))") \
    < s.index("public static void gain4({PR} pr")
assert s.index("public static void gain4({PR} pr") < s.index("public static void gain3({PR} pr") < s.index("public static void gain2({PR} pr")
assert s.count("public static void gain3({PR} pr") == 1 and s.count("public static void gain4({PR} pr") == 1
assert s.count("  gain4(pr, skill, amount, note, bonus, null);") == 1
assert s.count("  if (note) {PKG}.SkillMsg.note(pr, skill, amount);\n  if (party != null) {PKG}.PartyXp.note(pr, skill, amount, party);\n") == 1
assert s.count("    {PKG}.SkillMsg.send(pr);\n    {PKG}.PartyXp.send(pr);\n    for (long lv = r[0] + 1L;") == 1
assert s.count('{PKG}.SkillXp.gain4(mp, slot, amt, false, false, kn == null ? "" : kn);') == 1 and "note(mp, slot, amt, kn)" not in s
assert s.index("public static boolean excludedState({MVT} ms)") < s.index("public static int airTrack(")
assert s.count("  if (excludedState(ms)) {{ s[284] = 0.0; return 0; }}") == 1
assert s.index("public static boolean djTrig(int bits)") < s.index("public static void airJump(")
assert s.index("  if ({PKG}.AcroCfg.DJ_DEBUG) {{\n    String what") < s.index("  if (!{PKG}.AcroCfg.DJ_ON || !djTrig(bits) || v == null || cv == null) return;")
assert "if (bits == 0 || !{PKG}.AcroCfg.DJ_ON) return;" not in s and "if ((bits & 3) == 0 || v == null || cv == null) return;" not in s
assert s.index("public static String howText()") < s.index("public static String how(int s)")
assert s.count("{PKG}.PartyXp.share(pr, k, s, cx);") == 1 and s.count("{PKG}.SkillXp.gain(pr, slot, cx);") == 1
assert s.count("{PKG}.PartyXp.flushDue();") == 1 and s.count("{PKG}.PartyXp.retainOnline();") == 1
assert s.count("{PKG}.Acro.djPublish();") == 2 and s.count('bridge().remove("skill:dj:key")') == 1
assert "esy, pcg, pxp, pft):" in s and s.count("registerSystem(") == REG0   # stage 2 registers no system (ONE registerSystem per class)
assert "DJ_LIT" in s and "PARTY_LIT" in s and "acro.doubleJump.enabled=true" in s and "party.combatShare.enabled=true" in s
for ident in re.findall(r"#(Skyy[A-Za-z0-9_]*)", s):
    assert "_" not in ident, "UI id with an underscore: " + ident
assert "--deploy" in s   # the script keeps its optional deploy switch; this workflow never passes it
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.4.1
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
