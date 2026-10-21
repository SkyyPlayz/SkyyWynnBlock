"""Derive SkyyZones/build_skyyzones_0.2.0.py from SkyyZones/build_skyyzones_0.1.0.py (the tools/deploy_set.py SET pin, a hand-written NEW
mod script). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with 0.1.0 (nothing
else changed); 0.1.0 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/zones_0_2_0_patch.py   then   python SkyyZones/build_skyyzones_0.2.0.py   (never --deploy)
      then  python SkyyZones/test_skyyzones_0.2.0.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = r'''0.2.0 (2026-10-20) = phase Z2 of research/cloud/Zone-Regen-Spec.md (sections 4.1-4.3, 5.2-5.3, 7 X1-X4, 9): REGROWING BLOCKS in SKYBLOCK
  regions. Skyy 2026-10-15 (docs/answered/world.md 75): "when you mine stone, you get stone, and it swaps to an unbreakable block for a few
  seconds, then swaps back"; spec defaults taken 2026-10-20 (world.md 120: regrow 3-15 s ores, bedrock placeholders, ...).
  1. THE BREAK (ZGuard, sync, first among the event's systems): a listed block of a SKYBLOCK region (decide() = allow, not builder mode) whose
     type regrows (regrow.<type> > 0 s) -> ZRegen.broke: the exact block id (state kept) + rotation are read, a D line is APPENDED TO THE
     JOURNAL FIRST (regen/<world>.journal, written + flushed in the handler; a failed write CANCELS the break: no drop, nothing changes),
     then the engine breaks it as vanilla (drop, XP, collections untouched). A position already waiting ("depleted") refuses every break /
     dig crack / place there ("Growing back - wait a moment.") - one break = one drop roll, a regrowing block can never be mined twice for
     one regrow (spec 7 X3; two breaks in one tick: the 2nd is refused). Mobs: the same (a mob break of a listed block regrows too).
     Multi-block parts (filler != 0) and odd ids break like vanilla (no regrow, warned once). Builder mode breaks start no regrow (spec 3.1).
  2. THE PLACEHOLDER (ZPass on the world thread, queued by World.execute - probe Z1: execute() always QUEUES (taskQueue.offer), so it runs
     after performBlockBreak removed the block): the spot still holds the original id = another mod cancelled the break -> the entry is
     dropped (R line); else the type's placeholder (default Rock_Bedrock, rotation 0) is written with BlockOperations.setBlock (no
     PlaceBlockEvent - probe Z5: SkyySkills' PlacedStore only adds on PlaceBlockEvent and removes on break, so a regrown block pays XP
     again; NO SkyySkills change needed - confirmed against SkyySkills 0.4.56).
  3. THE TIMER: regrowAt = now + regrow.<type> s x regen.speedMult x (1 +- regen.jitter), at least 0.5 s. A 1 s scheduler tick (ZTicker)
     queues one ZPass per world that has waiting blocks; the pass writes at most regen.passBatch blocks; due -> the spot holds the
     placeholder or air -> the original id + rotation back (R line); a player standing in the block's space -> retry every 1 s (after 12
     tries: warned once, every 5 s; spec 4.3); the spot changed by hand (another block) -> left as it is, entry dropped, logged; already the
     original -> entry dropped. regen.maxDepleted per world: above it the oldest waiting block comes back early.
  4. CATCH-UP ON CHUNK LOAD: a due entry in an unloaded chunk is skipped (nothing is ticked there; the chunk saves with the placeholder) and
     restored by the first pass after the chunk is loaded again (polled every second; ChunkPreLoadProcessEvent carries a Holder, not a
     writable section). /zones restore and regen.enabled off ASK for the chunk (ChunkStore.getChunkSectionReferenceAtBlockAsync) and run a
     pass when it is there (thenRunAsync on the world).
  5. RESTART SAFETY: regen/<world>.journal (append-only: "D x y z <original id> <type> <regrowAt ms> <rotation> <placeholder>", "R x y z")
     + regen/<world>.snap every 60 s (temp file + atomic rename, then the journal is emptied; an entry is put in memory BEFORE its D line so
     a snapshot never misses one). Start: snapshot + journal replayed (bad lines skipped + counted), then compacted (never when a file
     could not be read); timers are wall-clock (regen.offlineCounts true; false = the downtime is added to every timer). Restart
     mid-timer keeps the block waiting; a crash at worst lets a block grow back early, never a placeholder forever (the journal line is
     written before the block changes). Shutdown: a final snapshot.
  6. COMMANDS: /zones status (builders: waiting blocks per world / type, next due, counters, journal errors), /zones restore <region|all>
     (admins: every waiting block back NOW - loaded chunks at once, the rest are loaded first; REQUIRED BEFORE ANY ROLLBACK of SkyyZones,
     also Server Setup -> Zones -> Regrowing blocks -> Restore all), /zones audit <region> [fix] (admins: placeholder blocks in the region's
     loaded chunks with no waiting entry - a lost write; 'fix' turns them into their type's first plain block id; at most 500,000 blocks a
     run). The spec's automatic audit at start is NOT done (the journal is written synchronously now, and builders may use bedrock as decor).
     /zones info shows "Mined: grows back as X in N s". Bridge zones:fn:check answers deny for break / place at a waiting spot.
  7. SERVER SETUP -> Zones -> Regrowing blocks (new file Skyy_SkyyZones/regen.properties, written once; types.properties is unchanged - no
     migration): regen.enabled (danger; off = every waiting block back at once, breaks like 0.1.0), regen.speedMult, regen.jitter,
     regen.offlineCounts, regen.defaultSec (a type with no row, 5 s), regen.passBatch 200, regen.maxDepleted 20,000, the table
     regrow.<type> = <seconds>,<placeholder> (spec Q2 defaults: stone 3, copper 4, iron 5, thorium 6, cobalt 8, adamantite 10, mithril 12,
     onyxium 15, gem 30; silver 6 + gold 6 are the BUILDER'S CHOICE - Q2 has no silver / gold row; logs 0, crops 0 - 0 = no regrow: logs + crops
     wait for Z3 whole-tree / crop-stage regrow and are held at 0 until then) and the action "Restore all".
  FIXER (critics of 0.2.0): (a) an unreadable regen/ file at a start HOLDS that world's files (no snapshot rewrites or deletes them until a
     start reads them) and files are read leniently (a bad byte no longer fails the read); (b) a torn last journal line (no newline) is
     skipped, warned with its text and the file kept as <world>.journal.torn-<ms>; (c) a placeholder that is itself a listed block of a type
     is refused in Server Setup and replaced by Rock_Bedrock at run time (else a spot could be mined again at once); (d) logs / crops rows
     above 0 are refused (Server Setup) / read as 0 (hand edit) until Z3; (e) regen.maxDepleted and region / type changes FORCE the entry,
     so an unloaded one is loaded too; a region deleted / retyped / overlaid (any index change) puts its waiting blocks back at once (spec 9);
     (f) chunk loads are asked once per chunk, at most 8 per pass, re-asked after 30 s if the chunk never came, and the load callback only
     queues a merged pass; (g) regen.offlineCounts off measures the downtime from regen/alive (a 60 s heartbeat), not the last mined block;
     (h) the stone type lists the cobbles + mossy stone (Rock_*_Cobble, Rock_Stone_Mossy; spec 4.2 "Cobble"; no migration: no
     Skyy_SkyyZones folder exists in any world yet - 0.1.0 never started on Skyy's PC); (i) /zones audit fix puts an ore back as its type's
     vanilla id (Ore_Copper* -> Ore_Copper_Stone, build-time table) and prefers stone when several types share the placeholder; (j) /zones
     info and region create / types say when a listed type does not grow back; (k) regen.passBatch = writes per PASS (the rest follow on
     the next world tick; this is the spec's loadBatch cap too).
  FIXER 2 (second critics): (l) a block that grew back is journaled as a V line and kept 30 min in the snapshot; the next start CHECKS those
     spots when their chunk is loaded - one still holding its placeholder (a crash before the chunk was saved again) gets its original back
     (/zones status counts them); (m) a regen/ file with skipped bad lines is kept as <file>.bad-<ms> before the start compacts it; (n) a
     waiting spot is refused while zones.on is off too (only builder mode passes; bridge zones:fn:check the same); (o) a backlog pass is
     never re-queued into the same world tick (World.consumeTaskQueue drains its queue until empty - read from the jar): the next pass runs
     50 ms later from the scheduler, so regen.passBatch really caps writes per tick; (p) a queued pass that never ran (its world stopped)
     blocks that world's passes for at most 5 s; (q) /zones audit reads at most 500,000 blocks a run (a world-thread stall cap).
  8. 0.1.0 CRITIC FINDING (fail-open on a typo in a hand-edited region line) - CLOSED: 0.1.0 already kept a bad region protecting by its copy
     in memory (reload) / its newest history/ copy / as FULL with its boxes; it still dropped a region whose world or boxes line was bad when
     nothing was in memory and history/ held no copy (a fresh start after a hand edit). Now: (a) regions.good.properties = the text of every
     successful write and every clean load with regions - checked FIRST for a region's last good copy and for a missing / blank / unreadable file at a
     start (exact, history/ is one change behind); (b) a bad region with no good copy anywhere, a readable world but no readable box locks
     its WHOLE WORLD as FULL (ZCfg.LOCKW, warned loudly) until the line is fixed + /zones reload; only a region with no readable world is
     left out (warned).
  Z3 (whole-tree fell + respawn, crop stage reset) is NOT in this round: the engine probes do not answer cleanly from the server jar -
  Wood_*_Trunk / Plant_Leaves_* carry Support + Physics (BlockPhysicsUtil support chains decide at RUN time whether the rest of a tree
  falls - Z2 / Z16) and trunks carry Farming Stages (tree growth), Z17 (a tree rewritten around a player) needs a live test; crops
  F-harvest through ChangeFarmingStage-like writes with no block event (Z0b). Left for a later round (logs / crops regrow 0 meanwhile).
  ROLLBACK to 0.1.0: /zones restore all (or Server Setup -> Zones -> Restore all), wait until /zones status says nothing is waiting, then
  stop the server; regen.properties, regen/ and regions.good.properties may stay (0.1.0 ignores them).
'''

P = G.Patch(os.path.join(ROOT, "SkyyZones", "build_skyyzones_0.1.0.py"), os.path.join(ROOT, "SkyyZones", "build_skyyzones_0.2.0.py"))
assert P.has('VERSION = "0.1.0"') and P.has('guard = mk("ZGuard", T["EES"])'), "not the SkyyZones 0.1.0 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

# ---------------------------------------------------------------------------------------------------- header / version
P.rep('''"""SkyyZones 0.1.0 - build script (javassist via jpype). A NEW mod: protected worlds + regions, phases Z0 + Z1 of''',
      '''"""SkyyZones 0.2.0 - build script (derived from the hand-written 0.1.0 by tools/zones_0_2_0_patch.py - edit the patch, not this file).
''' + NOTE + '''  CHECKED: SkyyZones/test_skyyzones_0.2.0.py.

0.1.0 (the base, unchanged below unless named above) - a NEW mod: protected worlds + regions, phases Z0 + Z1 of''')
P.rep('''Run:   python SkyyZones/build_skyyzones_0.1.0.py      -> SkyyZones/SkyyZones-0.1.0.jar   (no --deploy: tools/deploy_set.py installs the set)
Check: python SkyyZones/test_skyyzones_0.1.0.py       (bare JVMs, -Xverify:all, every new code path executed, engine-access audit)''',
      '''Run:   python SkyyZones/build_skyyzones_0.2.0.py      -> SkyyZones/SkyyZones-0.2.0.jar   (no --deploy: tools/deploy_set.py installs the set)
Check: python SkyyZones/test_skyyzones_0.2.0.py       (bare JVMs, -Xverify:all, every new code path executed, engine-access audit)''')
P.rep('VERSION = "0.1.0"', 'VERSION = "0.2.0"')

# ---------------------------------------------------------------------------------------------------- tokens + Z2 desk probes
P.rep('''    "BSEL": "com.hypixel.hytale.server.core.prefab.selection.standard.BlockSelection",
}''', '''    "BSEL": "com.hypixel.hytale.server.core.prefab.selection.standard.BlockSelection",
    "BOPS": "com.hypixel.hytale.server.core.universe.world.chunk.BlockOperations",   # 0.2.0 block writes (placeholder / regrow)
}''')
P.rep('''print("Z0 desk probes: Z5 Z5b Z9 Z18 Z19 + cancelled-event skip + Z0b (%d event-less block writers) re-checked" % len(_noev))
''', '''print("Z0 desk probes: Z5 Z5b Z9 Z18 Z19 + cancelled-event skip + Z0b (%d event-less block writers) re-checked" % len(_noev))
# ---- 0.2.0 Z2 desk probes (the regrow flow rests on them)
for c, m in ((T["BOPS"], "setBlock"), (T["BSEC"], "getRotationIndex"), (T["BSEC"], "getFiller"), (T["WLD"], "execute"), (T["WLD"], "getPlayerRefs"),
             (T["PR"], "getTransform"), (T["CHS"], "getChunkSectionReferenceAtBlockAsync"), (T["UNI"], "get"), (T["UNI"], "getWorld"),
             (T["BTY"], "getAssetMap"), ("com.hypixel.hytale.assetstore.map.BlockTypeAssetMap", "getIndex"),
             ("com.hypixel.hytale.assetstore.map.BlockTypeAssetMap", "getAsset")):
    B.probe(pool, c, m)
if "(L%s;Lcom/hypixel/hytale/component/Ref;IIIIL%s;III)Z" % (T["CHS"].replace(".", "/"), T["BTY"].replace(".", "/")) not in _sig(T["BOPS"], "setBlock"):
    raise SystemExit("Z2 changed: BlockOperations.setBlock(ChunkStore, Ref, x, y, z, id, BlockType, rotation, filler, settings) is gone")
# Z1: World.execute only QUEUES the task (taskQueue.offer) - never runs it inline, so a pass queued from a BreakBlockEvent handler runs
# after performBlockBreak has removed the block
# (the bytecode of execute itself: Deque.offer is called, Runnable.run never)
if _first_call(T["WLD"], "execute", "offer") < 0 or _first_call(T["WLD"], "execute", "run") >= 0:
    raise SystemExit("Z1 changed: World.execute may run the task inline now - the placeholder step could run before the block is removed")
print("Z2 desk probes: Z1 (World.execute queues), BlockOperations.setBlock shape, rotation / filler readers, async section load re-checked")
''')

# ---------------------------------------------------------------------------------------------------- stone lists the cobbles (fixer)
P.rep('''TYPES = [("stone", "Rock_Stone,Rock_Shale,Rock_Slate,Rock_Basalt,Rock_Sandstone,Rock_Calcite,Rock_Chalk,Rock_Lime,Rock_Marble,Rock_Quartzite,Rock_Volcanic"),''',
      '''TYPES = [("stone", "Rock_Stone,Rock_Shale,Rock_Slate,Rock_Basalt,Rock_Sandstone,Rock_Calcite,Rock_Chalk,Rock_Lime,Rock_Marble,Rock_Quartzite,Rock_Volcanic,"
                   "Rock_*_Cobble,Rock_Stone_Mossy"),   # 0.2.0 fixer: spec 4.2 "Cobble" (mines built of cobble / mossy stone)''')

# ---------------------------------------------------------------------------------------------------- regen.properties defaults
P.rep('''REGIONS_HEAD = "\\n".join([''', '''# 0.2.0 regrowing blocks (spec 4.2 / Question 2 defaults, docs/answered/world.md 120): seconds + placeholder per resource type; 0 = no
# regrow (logs + crops: whole-tree / crop-stage regrow is Z3, a later round)
REGROW = [("stone", 3), ("copper", 4), ("iron", 5), ("gold", 6), ("silver", 6), ("thorium", 6), ("cobalt", 8), ("adamantite", 10),
          ("mithril", 12), ("onyxium", 15), ("gem", 30), ("logs", 0), ("crops", 0)]
assert sorted(k for k, _ in REGROW) == sorted(k for k, _ in TYPES), "a resource type without a regrow row (or the other way round)"
PLACEHOLDER = "Rock_Bedrock"
if PLACEHOLDER not in _items:
    raise SystemExit("the default placeholder %s is not a vanilla block id" % PLACEHOLDER)
# fixer: logs + crops stay 0 until Z3 (a ripe crop / a lone trunk every few seconds otherwise)
NO_Z3 = ("logs", "crops")
assert all(s == 0 for k, s in REGROW if k in NO_Z3)
# fixer: /zones audit fix needs a concrete id for a wildcard type (every ore): the vanilla id a pattern stands for - the plain-stone
# variant first (Ore_Copper* -> Ore_Copper_Stone), else the pattern's own stem (Ore_Prisma), else the first match by name
FALLBACK = {}
with zipfile.ZipFile(ASSETS_ZIP) as _az:
    _blockids = set()
    for _n in _az.namelist():
        if _n.startswith("Server/Item/Items/") and _n.endswith(".json") and (_n.rsplit("/", 1)[1][:-5].startswith(("Ore_", "Rock_"))):
            try:
                if "BlockType" in json.loads(_az.read(_n).decode("utf-8-sig")):
                    _blockids.add(_n.rsplit("/", 1)[1][:-5])
            except Exception:
                pass
for _tid, _pats in TYPES:
    if dict(REGROW).get(_tid, 0) <= 0:
        continue
    for _p in _pats.split(","):
        if "*" not in _p:
            continue
        _rx = re.compile("^" + re.escape(_p).replace(r"\\*", ".*") + "$")
        # only real BLOCKS (Ore_Copper is the ore item, not a block); uncracked first
        _m = sorted((i for i in _blockids if _rx.match(i)), key=lambda i: ("Cracked" in i, i))
        if not _m:
            continue
        _pick = ([i for i in _m if i.endswith("_Stone")] + [i for i in _m if i == _p.replace("*", "")] + _m)[0]
        FALLBACK[_p] = _pick
assert FALLBACK.get("Ore_Copper*") == "Ore_Copper_Stone" and FALLBACK.get("Ore_Iron*") == "Ore_Iron_Stone" and "Ore_Prisma*" not in FALLBACK, FALLBACK
print("audit fallback ids: %s" % ", ".join("%s -> %s" % kv for kv in sorted(FALLBACK.items())))
REGEN_TEXT = "\\n".join([
    "# SkyyZones regrowing blocks (research/cloud/Zone-Regen-Spec.md 4). Change them in game: SkyWynn Menu -> Server Setup -> Zones ->",
    "# Regrowing blocks, or edit here. A listed block mined in a SKYBLOCK region turns into its placeholder, then grows back.",
    "# regen.enabled off = every waiting block comes back at once and listed blocks break like vanilla (no regrow).",
    "regen.enabled=true",
    "# regen.speedMult = every regrow time x this (0.5 = twice as fast). regen.jitter = each time x (1 - jitter .. 1 + jitter).",
    "regen.speedMult=1",
    "regen.jitter=0.2",
    "# regen.offlineCounts = time while the server is off counts toward the timers.",
    "regen.offlineCounts=true",
    "# regen.defaultSec = the regrow time of a resource type that has no regrow line below.",
    "regen.defaultSec=5",
    "# regen.passBatch = most blocks put back in one pass (one world tick) of one world; the rest follow on the next tick.",
    "# regen.maxDepleted = most waiting blocks in one world (the oldest then comes back early).",
    "regen.passBatch=200",
    "regen.maxDepleted=20000",
    "# regrow.<type>=<seconds>,<placeholder block id>: how long a mined block of that resource type takes to come back and what stands",
    "# there meanwhile. 0 = no regrow (the block breaks like vanilla and stays gone).",
] + ["regrow.%s=%d,%s" % (k, s, PLACEHOLDER if s > 0 else "none") for k, s in REGROW] + [""])

REGIONS_HEAD = "\\n".join([''')

# ---------------------------------------------------------------------------------------------------- ZApi: the new engine stand-ins
P.rep('''            "public int give(@REF@ r, @ST@ st, String id);", "public String blockAt(@WLD@ w, int x, int y, int z);"):''',
      '''            "public int give(@REF@ r, @ST@ st, String id);", "public String blockAt(@WLD@ w, int x, int y, int z);",
            # 0.2.0 regrow: rotation + filler, a block write, a player in the spot, a chunk load request, the world by name, a queued task, a scan
            "public int[] stateAt(@WLD@ w, int x, int y, int z);", "public boolean put(@WLD@ w, int x, int y, int z, String id, int rot);",
            "public boolean occupied(@WLD@ w, int x, int y, int z);", "public void load(@WLD@ w, int x, int y, int z, Runnable after);",
            "public @WLD@ world(String name);", "public boolean exec(@WLD@ w, Runnable r);",
            "public java.util.List scan(@WLD@ w, int[] box, String[] ids, int[] stats);",
            # fixer 2: a delayed task (the next regrow pass of a backlog - never re-queued into the same world tick)
            "public void later(Runnable r, long ms);"):''')

# ---------------------------------------------------------------------------------------------------- ZCfg: regen settings + the world lock
P.rep('''          "public static final String DEFAULT_TEXT = %s;" % jl(CONFIG_TEXT), "public static final String TYPES_TEXT = %s;" % jl(TYPES_TEXT)):''',
      '''          "public static final String DEFAULT_TEXT = %s;" % jl(CONFIG_TEXT), "public static final String TYPES_TEXT = %s;" % jl(TYPES_TEXT),
          # 0.2.0 regrowing blocks (regen.properties) + the worlds a broken region line locks as FULL (fail closed)
          "public static volatile boolean REGEN_ON = true;", "public static volatile double JITTER = 0.2;", "public static volatile double SPEED = 1.0;",
          "public static volatile boolean OFFLINE = true;", "public static volatile int PASS = 200;", "public static volatile int MAXDEP = 20000;",
          "public static volatile int DEFSEC = 5;", "public static java.nio.file.Path RFILE;",
          "public static volatile java.util.HashMap REGROW = new java.util.HashMap();",
          "public static volatile java.util.HashSet LOCKW = new java.util.HashSet();",
          "public static final String REGEN_TEXT = %s;" % jl(REGEN_TEXT)):''')
P.rep('''  return WSET.contains(w.toLowerCase());
}""")''', '''  String lw = w.toLowerCase();
  return WSET.contains(lw) || LOCKW.contains(lw);
}""")''')

CFG_REGEN = r'''# ZCfg 0.2.0: the regrow settings (regen.properties; the kit binds the scalar rows to the fields, the regrow. table runs reloadRegen)
# =====================================================================================================================================
M(cfg, r"""
public static double dec(String v, double d, double lo, double hi) {
  double x = d;
  if (v != null) { try { x = Double.parseDouble(v.trim()); } catch (Throwable t) { x = d; } }
  if (Double.isNaN(x)) x = d;
  if (x < lo) x = lo;
  if (x > hi) x = hi;
  return x;
}""")
# null = fine, else why not: "<seconds 0-3600>[,<placeholder id or none>]" ("|" from the kit's columns counts as ",")
M(cfg, r"""
public static String regrowWhy(String v) {
  if (v == null) return "an empty line";
  String[] c = v.replace('|', ',').split(",", -1);
  if (c.length < 1 || c.length > 2) return "write <seconds>,<placeholder block id> (e.g. 4,Rock_Bedrock)";
  int s = -1;
  try { s = Integer.parseInt(c[0].trim()); } catch (Throwable t) { s = -1; }
  if (s < 0 || s > 3600) return "the seconds are a whole number from 0 to 3600 (0 = no regrow)";
  String ph = c.length > 1 ? c[1].trim() : "";
  if (ph.length() > 0 && !ph.equalsIgnoreCase("none") && !ph.matches("\\*?[A-Za-z0-9_]{1,80}")) return "'" + ph + "' is not a block id";
  return null;
}""")
M(cfg, r"""
public static String phOf(String v) {
  String[] c = v.replace('|', ',').split(",", -1);
  String ph = c.length > 1 ? c[1].trim() : "";
  if (ph.length() == 0 || ph.equalsIgnoreCase("none")) return "@PH@";
  return ph;
}""".replace("@PH@", PLACEHOLDER))
# fixer: the types whose regrow needs Z3 (whole trees / crop stages) - held at 0 until then
M(cfg, r"""
public static boolean noZ3(String type) {
  return @NOZ3@;
}""".replace("@NOZ3@", " || ".join('"%s".equals(type)' % t for t in NO_Z3)))
# type id -> Object[] { Integer seconds, String placeholder }; a bad line is skipped (warned once): its type then uses regen.defaultSec
M(cfg, r"""
public static java.util.HashMap parseRegrow(java.util.Properties p) {
  java.util.HashMap m = new java.util.HashMap();
  if (p == null) return m;
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith("regrow.")) continue;
    String id = k.substring(7).toLowerCase();
    String v = p.getProperty(k);
    String why = id.matches("[a-z0-9_]{1,32}") ? regrowWhy(v) : "not a type id (a-z 0-9 _)";
    if (why != null) { warnOnce("regrow:" + k + "=" + v, "regen.properties: '" + k + "=" + v + "' - " + why + " - skipped (that type uses regen.defaultSec + @PH@)"); continue; }
    int s = Integer.parseInt(v.replace('|', ',').split(",", -1)[0].trim());
    if (s > 0 && noZ3(id)) { warnOnce("z3:" + k + "=" + v, "regen.properties: '" + k + "=" + v + "' - " + id + " cannot regrow yet (whole trees / crop stages come later) - read as 0"); s = 0; }
    m.put(id, new Object[] { Integer.valueOf(s), phOf(v) });
  }
  return m;
}""".replace("@PH@", PLACEHOLDER))
M(cfg, r"""
public static String loadRegen(boolean first) {
  boolean wrote = first && writeIfMissing(RFILE, REGEN_TEXT);
  java.util.Properties p = read(RFILE);
  if (p == null) return "regen.properties could not be read - regrowing keeps its old settings";
  REGEN_ON = bool(p.getProperty("regen.enabled"), true);
  SPEED = dec(p.getProperty("regen.speedMult"), 1.0, 0.1, 10.0);
  JITTER = dec(p.getProperty("regen.jitter"), 0.2, 0.0, 0.5);
  OFFLINE = bool(p.getProperty("regen.offlineCounts"), true);
  DEFSEC = intOf(p.getProperty("regen.defaultSec"), 5, 1, 3600);
  PASS = intOf(p.getProperty("regen.passBatch"), 200, 10, 5000);
  MAXDEP = intOf(p.getProperty("regen.maxDepleted"), 20000, 100, 200000);
  java.util.HashMap m = parseRegrow(p);
  REGROW = m;
  return (wrote ? "default regen.properties written; " : "") + "regrowing " + (REGEN_ON ? "ON" : "OFF") + " (" + m.size() + " regrow rows)";
}""")
# the kit's reload routine of the regrow table (runs after the kit wrote regen.properties)
M(cfg, r"""
public static void reloadRegen() {
  info("regrow table re-read: " + loadRegen(false));
}""")
M(cfg, r"""
public static int regrowSec(String type) {
  Object o = type == null ? null : REGROW.get(type);
  if (o instanceof Object[]) return ((Integer) ((Object[]) o)[0]).intValue();
  return DEFSEC;
}""")
M(cfg, r"""
public static String placeholder(String type) {
  Object o = type == null ? null : REGROW.get(type);
  if (o instanceof Object[]) return (String) ((Object[]) o)[1];
  return "@PH@";
}""".replace("@PH@", PLACEHOLDER))
# (the kit's check of a regrow table line, ZCfg.checkRegrow, is defined after ZRules - it asks whether the placeholder is a listed block)
# =====================================================================================================================================
# ZRegion: one region (immutable once published: edits make a copy)
'''
P.rep("# ZRegion: one region (immutable once published: edits make a copy)\n", CFG_REGEN)

# ---------------------------------------------------------------------------------------------------- ZRules.resType
P.rep('''M(rules, r"""
public static String why(int code) {''', '''# 0.2.0: the resource type a SKYBLOCK break at x y z counts as (the same walk as decide(): the top region must be SKYBLOCK; the first listed
# type of the SKYBLOCK regions there, top first) - null = none (no regrow)
M(rules, r"""
public static String resType(@PKG@.ZIndex ix, String w, int x, int y, int z, String id) {
  if (ix == null) return null;
  java.util.ArrayList at = ix.at(w, x, y, z);
  if (at.isEmpty() || ((@PKG@.ZRegion) at.get(0)).mode != 1) return null;
  String b = bare(id);
  for (int i = 0; i < at.size(); i++) {
    @PKG@.ZRegion r = (@PKG@.ZRegion) at.get(i);
    if (r.mode != 1) continue;
    String t = listedType(r, b);
    if (t != null) return t;
  }
  return null;
}""")
# fixer: the resource type that lists this block id anywhere (null = none) - a placeholder must never be a mineable block
M(rules, r"""
public static String listedAny(String id) {
  if (id == null) return null;
  String b = bare(id);
  java.util.Iterator it = @PKG@.ZCfg.TYPES.keySet().iterator();
  while (it.hasNext()) {
    String t = (String) it.next();
    if (typeHas(t, b)) return t;
  }
  return null;
}""")
M(rules, r"""
public static String why(int code) {''')

# ---------------------------------------------------------------------------------------------------- ZSave: the last good copy
P.rep('''"public static volatile java.nio.file.Path LOGF;", "public static final int KEEP = 10;",''',
      '''"public static volatile java.nio.file.Path LOGF;", "public static final int KEEP = 10;", "public static volatile java.nio.file.Path GOOD;",''')
P.rep('''# the write itself: never a text older than the newest written one; the file on disk is copied to history/ first (skipped if equal)''',
      '''# 0.2.0 (the 0.1.0 critic's fail-open finding): regions.good.properties = the text of every successful write and every clean load - the
# exact last good copy of every region (history/ is one change behind); temp file + rename, skipped when equal
M(sav, r"""
public static synchronized boolean good(String text) {
  if (GOOD == null || text == null) return false;
  try {
    if (java.nio.file.Files.exists(GOOD, new java.nio.file.LinkOption[0]) && new String(java.nio.file.Files.readAllBytes(GOOD), "UTF-8").equals(text)) return true;
    java.nio.file.Files.createDirectories(GOOD.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = GOOD.resolveSibling(GOOD.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, text.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    try {
      java.nio.file.Files.move(tmp, GOOD, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    } catch (Throwable am) {
      java.nio.file.Files.move(tmp, GOOD, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    }
    return true;
  } catch (Throwable t) { @PKG@.ZCfg.warnOnce("good", "could not write regions.good.properties (the last good copy of the regions): " + t); return false; }
}""")
# the write itself: never a text older than the newest written one; the file on disk is copied to history/ first (skipped if equal)''')
P.rep('''    WRITTEN = seq;
    WRITES.incrementAndGet();
    return true;''', '''    WRITTEN = seq;
    WRITES.incrementAndGet();
    good(text);
    return true;''')

# ---------------------------------------------------------------------------------------------------- ZStore: good copy first, world lock
P.rep('''          "public static volatile long LAST_SEQ = 0L;", "public static final int MAX_REGIONS = 500;",''',
      '''          "public static volatile long LAST_SEQ = 0L;", "public static final int MAX_REGIONS = 500;",
          "public static java.util.HashSet LOCKNEW = new java.util.HashSet();",''')
P.rep('''public static @PKG@.ZRegion fromHistory(String id) {
  try {
    java.nio.file.Path h = @PKG@.ZSave.HIST;''', '''public static @PKG@.ZRegion fromHistory(String id) {
  try {
    java.nio.file.Path g = @PKG@.ZSave.GOOD;
    if (g != null && java.nio.file.Files.exists(g, new java.nio.file.LinkOption[0])) {
      java.util.Properties gp = @PKG@.ZCfg.read(g);
      if (gp != null && gp.getProperty("region." + id + ".world") != null) {
        String[] gw = new String[1];
        @PKG@.ZRegion gr = parseOne(gp, id, gw);
        if (gw[0] == null) return gr;
      }
    }
    java.nio.file.Path h = @PKG@.ZSave.HIST;''')
P.rep('''  if (h != null) { @PKG@.ZCfg.warn("regions.properties: region " + id + " has a bad " + why + " - it protects as its newest good copy in history/ until fixed"); return h; }''',
      '''  if (h != null) { @PKG@.ZCfg.warn("regions.properties: region " + id + " has a bad " + why + " - it protects as its last good copy (regions.good.properties / history/) until fixed"); return h; }''')
P.rep('''  @PKG@.ZCfg.warn("regions.properties: region " + id + " has a bad " + why + " and no readable world + boxes - it does NOT protect until fixed");
  return null;''', '''  if (parsed.world.matches("[A-Za-z0-9_.-]{1,64}")) {
    LOCKNEW.add(parsed.world.toLowerCase());
    @PKG@.ZCfg.warn("regions.properties: region " + id + " has a bad " + why + ", no readable box and no good copy - the WHOLE WORLD " + parsed.world + " is protected (FULL, nothing breaks or is placed) until the line is fixed + /zones reload");
    return null;
  }
  @PKG@.ZCfg.warn("regions.properties: region " + id + " has a bad " + why + " and no readable world - it does NOT protect until fixed");
  return null;''')
P.rep('''public static java.util.TreeMap fromHistoryAll(String[] name) {
  try {
    java.nio.file.Path h = @PKG@.ZSave.HIST;''', '''public static java.util.TreeMap fromHistoryAll(String[] name) {
  try {
    java.nio.file.Path g = @PKG@.ZSave.GOOD;
    if (g != null && java.nio.file.Files.exists(g, new java.nio.file.LinkOption[0])) {
      java.util.Properties gp = @PKG@.ZCfg.read(g);
      if (gp != null) {
        java.util.TreeMap gm = parseAll(gp, new String[1], new int[1], false);
        if (!gm.isEmpty()) { name[0] = g.getFileName().toString(); return gm; }
      }
    }
    java.nio.file.Path h = @PKG@.ZSave.HIST;''')
P.rep('''      if (!m.isEmpty()) { name[0] = (String) names.get(i); return m; }''', '''      if (!m.isEmpty()) { name[0] = "history/" + (String) names.get(i); return m; }''')
for _l in ('''        @PKG@.ZCfg.warn("regions.properties cannot be read - the " + h.size() + " regions of history/" + hn[0] + " protect meanwhile; region edits are blocked until /zones reload reads the file");''',
           '''        return "regions.properties UNREADABLE (" + h.size() + " regions from history/" + hn[0] + " protect)";''',
           '''        save("SkyyZones", "restored " + h.size() + " regions from history/" + hn[0] + " (regions.properties " + (exists ? "was blank" : "was missing") + ")");''',
           '''        @PKG@.ZCfg.warn("regions.properties " + (exists ? "was blank" : "was missing") + " - the " + h.size() + " regions of history/" + hn[0] + " are restored and written back (/zones reload clear removes every region)");''',
           '''        return REGIONS.size() + " regions in " + INDEX.byWorld.size() + " worlds (RESTORED from history/" + hn[0] + ")";'''):
    P.rep(_l, _l.replace('history/" + hn[0]', '" + hn[0]'))
P.rep('''  String[] bad = new String[1];
  int[] kept = new int[1];
  java.util.TreeMap out = parseAll(p, bad, kept, true);''', '''  String[] bad = new String[1];
  int[] kept = new int[1];
  LOCKNEW = new java.util.HashSet();
  java.util.TreeMap out = parseAll(p, bad, kept, true);''')
P.rep('''  REGIONS.clear();
  REGIONS.putAll(out);
  BAD = bad[0];
  publish();''', '''  REGIONS.clear();
  REGIONS.putAll(out);
  BAD = bad[0];
  publish();
  @PKG@.ZCfg.LOCKW = LOCKNEW;
  if (bad[0] == null && !REGIONS.isEmpty()) @PKG@.ZSave.good(text());''')
P.rep('''  String t = loadTypes(false);
  String r = @PKG@.ZStore.load(clear);
  return "Re-read: " + t + "; " + r + ".";''', '''  String t = loadTypes(false);
  String r = @PKG@.ZStore.load(clear);
  String g = loadRegen(false);
  return "Re-read: " + t + "; " + r + "; " + g + ".";''')

# ---------------------------------------------------------------------------------------------------- ZEng: block writes etc.
ENG = r'''# ZEng 0.2.0: the regrow engine calls (each with the harness stand-in first)
# =====================================================================================================================================
# the LOADED section holding x y z, or null (never loads one; the blockAt recipe)
M(eng, r"""
public static @BSEC@ section(@WLD@ w, int x, int y, int z) {
  if (w == null || y < 0 || y >= 320) return null;
  @CHS@ cs = w.getChunkStore();
  @REF@ c = cs.getChunkReference(@CHU@.indexChunkFromBlock(x, z));
  if (c == null || !c.isValid()) return null;
  @REF@ r = cs.getChunkSectionReferenceAtBlock(x, y, z);
  if (r == null || !r.isValid()) return null;
  Object s = cs.getStore().getComponent(r, @BSEC@.getComponentType());
  return s instanceof @BSEC@ ? (@BSEC@) s : null;
}""")
# { rotation index, filler } of the block at x y z; null = not loaded
M(eng, r"""
public static int[] stateAt(@WLD@ w, int x, int y, int z) {
  @PKG@.ZApi a = API;
  if (a != null) return a.stateAt(w, x, y, z);
  try {
    @BSEC@ s = section(w, x, y, z);
    if (s == null) return null;
    return new int[] { s.getRotationIndex(x, y, z), s.getFiller(x, y, z) };
  } catch (Throwable t) { fail("block state", t); return null; }
}""")
# write block id (with its rotation) at x y z in a LOADED chunk (BlockSetCommand's call: index, BlockType, rotation, filler 0, settings 0
# = the full update, as SkyyExploration's luggage); false = not loaded / unknown id / refused. Fires no PlaceBlockEvent (probe Z5).
M(eng, r"""
public static boolean put(@WLD@ w, int x, int y, int z, String id, int rot) {
  @PKG@.ZApi a = API;
  if (a != null) return a.put(w, x, y, z, id, rot);
  try {
    if (w == null || id == null || y < 0 || y >= 320) return false;
    @CHS@ cs = w.getChunkStore();
    @REF@ c = cs.getChunkReference(@CHU@.indexChunkFromBlock(x, z));
    if (c == null || !c.isValid()) return false;
    @REF@ r = cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (r == null || !r.isValid()) return false;
    int idx = @BTY@.getAssetMap().getIndex(id);
    if (idx == Integer.MIN_VALUE) { @PKG@.ZCfg.warnOnce("noblock:" + id, "the block id " + id + " is unknown to the game - it cannot be written (regrow / placeholder)"); return false; }
    Object t = @BTY@.getAssetMap().getAsset(idx);
    if (!(t instanceof @BTY@)) return false;
    return @BOPS@.setBlock(cs, r, x, y, z, idx, (@BTY@) t, rot, 0, 0);
  } catch (Throwable t) { fail("block write", t); return false; }
}""")
# a player whose body overlaps the block's space (feet y-1.8 .. y+1, 0.85 across): never write a solid block into a player (spec 4.3)
M(eng, r"""
public static boolean occupied(@WLD@ w, int x, int y, int z) {
  @PKG@.ZApi a = API;
  if (a != null) return a.occupied(w, x, y, z);
  try {
    if (w == null) return false;
    java.util.Collection c = w.getPlayerRefs();
    if (c == null) return false;
    java.util.Iterator it = c.iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @PR@)) continue;
      com.hypixel.hytale.math.vector.Transform t = ((@PR@) o).getTransform();
      if (t == null || t.getPosition() == null) continue;
      @V3D@ p = t.getPosition();
      double dx = p.x - ((double) x + 0.5);
      double dz = p.z - ((double) z + 0.5);
      double dy = p.y - (double) y;
      if (dx > -0.85 && dx < 0.85 && dz > -0.85 && dz < 0.85 && dy > -1.9 && dy < 1.0) return true;
    }
    return false;
  } catch (Throwable t) { fail("player-in-block check", t); return true; }
}""")
# ask for the section (loads the chunk), then run `after` on the world thread
M(eng, r"""
public static void load(@WLD@ w, int x, int y, int z, Runnable after) {
  @PKG@.ZApi a = API;
  if (a != null) { a.load(w, x, y, z, after); return; }
  try {
    if (w == null || y < 0 || y >= 320) return;
    java.util.concurrent.CompletableFuture f = w.getChunkStore().getChunkSectionReferenceAtBlockAsync(x, y, z);
    if (f != null && after != null) f.thenRunAsync(after, (java.util.concurrent.Executor) w);
  } catch (Throwable t) { fail("chunk load", t); }
}""")
# fixer 2: run r after ms on the server scheduler (World.consumeTaskQueue drains its queue until EMPTY - a task the pass queues again would
# run in the same tick, so a backlog pass is delayed here instead); a failure only leaves the rest to the 1 s regrow tick
M(eng, r"""
public static void later(Runnable r, long ms) {
  @PKG@.ZApi a = API;
  if (a != null) { a.later(r, ms); return; }
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(r, ms, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable t) { fail("delayed regrow pass", t); }
}""")
M(eng, r"""
public static @WLD@ world(String name) {
  @PKG@.ZApi a = API;
  if (a != null) return a.world(name);
  try { return name == null ? null : @UNI@.get().getWorld(name); } catch (Throwable t) { fail("world lookup", t); return null; }
}""")
# World.execute QUEUES the task (probe Z1); false = the world takes no tasks (shutting down)
M(eng, r"""
public static boolean exec(@WLD@ w, Runnable r) {
  @PKG@.ZApi a = API;
  if (a != null) return a.exec(w, r);
  try { if (w == null) return false; w.execute(r); return true; } catch (Throwable t) { return false; }
}""")
# the blocks of box (x0 y0 z0 x1 y1 z1) whose id is one of ids, in LOADED sections only: int[] { x, y, z, index in ids }; stats[0] = blocks
# read, stats[1] = sections not loaded; stops after cap blocks (audit)
M(eng, r"""
public static java.util.List scan(@WLD@ w, int[] box, String[] ids, int[] stats, long cap) {
  @PKG@.ZApi a = API;
  if (a != null) return a.scan(w, box, ids, stats);
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    int[] ix = new int[ids.length];
    for (int i = 0; i < ids.length; i++) ix[i] = @BTY@.getAssetMap().getIndex(ids[i]);
    int y0 = Math.max(box[1], 0);
    int y1 = Math.min(box[4], 319);
    for (int sx = box[0] >> 5; sx <= (box[3] >> 5); sx++)
      for (int sz = box[2] >> 5; sz <= (box[5] >> 5); sz++)
        for (int sy = y0 >> 5; sy <= (y1 >> 5); sy++) {
          if ((long) stats[0] >= cap) return out;
          @BSEC@ s = section(w, sx << 5, sy << 5, sz << 5);
          if (s == null) { stats[1] = stats[1] + 1; continue; }
          int ax = Math.max(box[0], sx << 5);
          int bx = Math.min(box[3], (sx << 5) + 31);
          int ay = Math.max(y0, sy << 5);
          int by = Math.min(y1, (sy << 5) + 31);
          int az = Math.max(box[2], sz << 5);
          int bz = Math.min(box[5], (sz << 5) + 31);
          for (int i = ax; i <= bx; i++)
            for (int k = az; k <= bz; k++)
              for (int j = ay; j <= by; j++) {
                int v = s.get(i, j, k);
                stats[0] = stats[0] + 1;
                for (int q = 0; q < ix.length; q++) if (v == ix[q]) { out.add(new int[] { i, j, k, q }); break; }
              }
        }
  } catch (Throwable t) { fail("audit scan", t); }
  return out;
}""")

# =====================================================================================================================================
# ZMsg: chat lines + the throttled refusal note
'''
P.rep("# ZMsg: chat lines + the throttled refusal note\n", ENG)

# ---------------------------------------------------------------------------------------------------- the regrow classes
REGEN = r'''# 0.2.0 REGROWING BLOCKS (spec 4.1-4.3, 9): ZDep = one waiting block, ZRw = one world's waiting blocks + its journal / snapshot,
# ZPass = the world-thread pass (placeholder, regrow, catch-up), ZRegen = the break hook + start / restore / status / audit, ZTicker = the
# 1 s scheduler tick (+ the 60 s snapshot)
# =====================================================================================================================================
dep = mk("ZDep")
for f in ("public int x;", "public int y;", "public int z;", "public long key;", "public String orig;", "public String type;", "public String ph;",
          "public int rot;", "public volatile long due;", "public volatile int state;", "public int tries;", "public volatile long next;",
          "public volatile boolean force;", "public volatile long asked;", "public static volatile long CLOCK = 0L;"):
    F(dep, f)
# CLOCK = the harness clock (0 in game = the wall clock)
M(dep, r"""
public static long now() {
  long c = CLOCK;
  return c != 0L ? c : System.currentTimeMillis();
}""")
M(dep, r"""
public static long key(int x, int y, int z) {
  return (((long) (x & 0x3FFFFFF)) << 38) | (((long) (y & 0xFFF)) << 26) | ((long) (z & 0x3FFFFFF));
}""")
C(dep, r"""
public ZDep(int x, int y, int z, String orig, String type, String ph, int rot, long due) {
  this.x = x; this.y = y; this.z = z; this.orig = orig; this.type = type; this.ph = ph; this.rot = rot; this.due = due;
  this.key = key(x, y, z); this.state = 0; this.tries = 0; this.next = 0L;
}""")
M(dep, r"""
public String line() {
  return "D " + this.x + " " + this.y + " " + this.z + " " + this.orig + " " + this.type + " " + this.due + " " + this.rot + " " + this.ph;
}""")
# fixer 2: V = a block that GREW BACK (time = when): kept 30 min in the snapshot, checked after the next start (a crash before its chunk
# was saved leaves the placeholder in the saved chunk with no D entry)
M(dep, r"""
public String vline() {
  return "V" + line().substring(1);
}""")
M(dep, r"""
public static boolean idOk(String id) {
  return id != null && id.matches("\\*?[A-Za-z0-9_.-]{1,120}");
}""")
# a journal / snapshot D line (9 words) -> an entry (state 1: its placeholder is assumed in place; the pass checks the world); null = bad
M(dep, r"""
public static @PKG@.ZDep parse(String[] a) {
  if (a == null || a.length != 9 || (!a[0].equals("D") && !a[0].equals("V"))) return null;
  try {
    int x = Integer.parseInt(a[1]);
    int y = Integer.parseInt(a[2]);
    int z = Integer.parseInt(a[3]);
    long due = Long.parseLong(a[6]);
    int rot = Integer.parseInt(a[7]);
    if (!idOk(a[4]) || !a[5].matches("[a-z0-9_]{1,32}") || !idOk(a[8]) || rot < 0 || rot > 255 || y < -64 || y > 511) return null;
    @PKG@.ZDep d = new @PKG@.ZDep(x, y, z, a[4], a[5], a[8], rot, due);
    d.state = 1;
    return d;
  } catch (Throwable t) { return null; }
}""")

rw = mk("ZRw")
for f in ("public String world;", "public java.util.concurrent.ConcurrentHashMap dep;",
          "public java.nio.file.Path jf;", "public java.nio.file.Path sf;", "public java.io.OutputStream out;", "public volatile long lines;",
          "public java.util.concurrent.atomic.AtomicLong queued;", "public volatile boolean hold;", "public volatile @PKG@.ZIndex ix;",
          "public java.util.concurrent.ConcurrentHashMap recent;", "public java.util.concurrent.ConcurrentHashMap check;",
          "public static final long KEEPV = 1800000L;",
          "public static final java.util.concurrent.atomic.AtomicLong JFAIL = new java.util.concurrent.atomic.AtomicLong();"):
    F(rw, f)
C(rw, r"""
public ZRw(String world, java.nio.file.Path dir) {
  this.world = world;
  this.dep = new java.util.concurrent.ConcurrentHashMap();
  this.queued = new java.util.concurrent.atomic.AtomicLong(0L);
  this.recent = new java.util.concurrent.ConcurrentHashMap();
  this.check = new java.util.concurrent.ConcurrentHashMap();
  this.jf = dir.resolve(world + ".journal");
  this.sf = dir.resolve(world + ".snap");
  this.lines = 0L;
}""")
# one journal line, written + flushed now (spec 4.1 step 2: the record before the block changes); false = not written (the caller refuses)
M(rw, r"""
public synchronized boolean append(String line) {
  try {
    if (this.out == null) {
      java.nio.file.Files.createDirectories(this.jf.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      this.out = java.nio.file.Files.newOutputStream(this.jf, new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND, java.nio.file.StandardOpenOption.WRITE });
    }
    this.out.write((line + "\n").getBytes("UTF-8"));
    this.out.flush();
    this.lines = this.lines + 1L;
    return true;
  } catch (Throwable t) {
    JFAIL.incrementAndGet();
    @PKG@.ZCfg.warnOnce("journal:" + this.world, "could not write the regrow journal " + this.jf + " (" + t + ") - gathering in regrowing areas of " + this.world + " is refused while it fails");
    try { if (this.out != null) this.out.close(); } catch (Throwable t2) { }
    this.out = null;
    return false;
  }
}""")
# an entry is finished: out of memory, then an R line (a missing R only means the block is checked again after a restart)
M(rw, r"""
public boolean drop(@PKG@.ZDep d) {
  if (d == null || !this.dep.remove(Long.valueOf(d.key), d)) return false;
  append("R " + d.x + " " + d.y + " " + d.z);
  return true;
}""")
# fixer 2: an entry GREW BACK (the original is in the world): out of memory, kept as recent (when = now) and journaled as a V line (critic:
# a crash before the chunk is saved again reloads the placeholder - the next start checks every recent spot, see ZPass)
M(rw, r"""
public boolean done(@PKG@.ZDep d, long now) {
  if (d == null || !this.dep.remove(Long.valueOf(d.key), d)) return false;
  d.due = now;
  this.recent.put(Long.valueOf(d.key), d);
  append(d.vline());
  return true;
}""")
# the snapshot (spec 5.3 / 9): every waiting entry -> <world>.snap.tmp -> atomic rename, then the journal is emptied (both under this lock,
# so no journal line is lost); nothing waiting = both files removed. force = even with no new journal line.
M(rw, r"""
public synchronized boolean snapshot(boolean force) {
  if (!force && this.lines == 0L) return true;
  if (this.hold) {
    @PKG@.ZCfg.warnOnce("hold:" + this.world, "regrow files of " + this.world + " could not be read at the start - they are NOT rewritten or compacted (no waiting block is lost); the journal keeps growing until a start reads them");
    return false;
  }
  try {
    if (this.out != null) { this.out.close(); this.out = null; }
    long now = @PKG@.ZDep.now();
    java.util.Iterator ri = this.recent.values().iterator();
    while (ri.hasNext()) { if (now - ((@PKG@.ZDep) ri.next()).due > KEEPV) ri.remove(); }
    if (this.dep.isEmpty() && this.recent.isEmpty() && this.check.isEmpty()) {
      java.nio.file.Files.deleteIfExists(this.sf);
      java.nio.file.Files.deleteIfExists(this.jf);
      this.lines = 0L;
      return true;
    }
    StringBuilder sb = new StringBuilder("# SkyyZones regrow snapshot of world " + this.world + ": D x y z original type regrowAtMs rotation placeholder (V = grown back at that time, checked after a start)\n");
    java.util.Iterator it = this.dep.values().iterator();
    while (it.hasNext()) sb.append(((@PKG@.ZDep) it.next()).line()).append('\n');
    it = this.check.values().iterator();
    while (it.hasNext()) sb.append(((@PKG@.ZDep) it.next()).vline()).append('\n');
    it = this.recent.values().iterator();
    while (it.hasNext()) sb.append(((@PKG@.ZDep) it.next()).vline()).append('\n');
    java.nio.file.Files.createDirectories(this.sf.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = this.sf.resolveSibling(this.sf.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, sb.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    try {
      java.nio.file.Files.move(tmp, this.sf, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    } catch (Throwable am) {
      java.nio.file.Files.move(tmp, this.sf, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    }
    java.nio.file.Files.deleteIfExists(this.jf);
    this.lines = 0L;
    return true;
  } catch (Throwable t) { @PKG@.ZCfg.warnOnce("snap:" + this.world, "could not write the regrow snapshot " + this.sf + " (the journal is kept): " + t); return false; }
}""")
M(rw, r"""
public synchronized void close() {
  try { if (this.out != null) this.out.close(); } catch (Throwable t) { }
  this.out = null;
}""")

pas = mk("ZPass", None, ("java.lang.Runnable",))
for f in ("public @PKG@.ZRw rw;", "public @WLD@ w;", "public boolean k;", "public static final int LOADS = 8;", "public static final long REASK = 30000L;",
          "public static final java.util.concurrent.atomic.AtomicLong ASKED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong RESTORED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong PLACED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong BLOCKED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong CHANGED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong CANCELLED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong UNLOADED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong WFAIL = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong VERIFIED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final long STALE = 5000L;", "public static final long NEXT = 50L;"):
    F(pas, f)
C(pas, "public ZPass(@PKG@.ZRw rw, @WLD@ w) { this.rw = rw; this.w = w; this.k = false; }")
# k = a chunk-load callback: it only queues a (merged) pass - never a full pass per loaded chunk (critic: N loads -> N passes)
C(pas, "public ZPass(@PKG@.ZRw rw, @WLD@ w, boolean k) { this.rw = rw; this.w = w; this.k = k; }")
# queue one pass for that world (at most one waits in its queue). fixer 2: queued = WHEN it was queued; a pass still not run after 5 s (a
# world stopped with it in its queue - ZRw outlives the World) no longer blocks every later kick of that world
M(pas, r"""
public static boolean kick(@WLD@ w, @PKG@.ZRw rw) {
  if (w == null || rw == null) return false;
  long now = @PKG@.ZDep.now();
  long q = rw.queued.get();
  if (q != 0L && now - q < STALE && now >= q) return false;
  if (!rw.queued.compareAndSet(q, now)) return false;
  if (@PKG@.ZEng.exec(w, new @PKG@.ZPass(rw, w))) return true;
  rw.queued.compareAndSet(now, 0L);
  return false;
}""")
# THE PASS (world thread). state 0 (just broken): still the original = the break was cancelled by another system -> dropped; else the
# placeholder. Due (or forced, or regen off): unloaded -> waits for the chunk (forced: asks for it); the original already -> dropped; changed
# by hand -> left, dropped; a player inside -> retry; else the original back. At most regen.passBatch writes; more -> another pass 50 ms
# later (fixer 2: never re-queued from here - the world drains its queue until empty, so that ran the whole backlog in ONE tick).
# Then (fixer 2) the CHECK list: spots that grew back shortly before the last stop - a loaded one still holding its placeholder (a crash
# before the chunk was saved) gets its original back; anything else is dropped from the list.
M(pas, r"""
public static int pass(@PKG@.ZRw rw, @WLD@ w) {
  long now = @PKG@.ZDep.now();
  boolean off = !@PKG@.ZCfg.REGEN_ON;
  int max = @PKG@.ZCfg.PASS;
  int writes = 0;
  boolean more = false;
  java.util.HashSet asked = null;
  int loads = 0;
  @PKG@.ZIndex ix = @PKG@.ZStore.INDEX;
  if (ix != rw.ix) {
    rw.ix = ix;
    java.util.Iterator ci = rw.dep.values().iterator();
    while (ci.hasNext()) {
      @PKG@.ZDep c = (@PKG@.ZDep) ci.next();
      String t = @PKG@.ZRules.resType(ix, rw.world, c.x, c.y, c.z, c.orig);
      if (!c.force && (t == null || !t.equals(c.type))) { c.force = true; c.next = 0L; }
    }
  }
  java.util.Iterator it = rw.dep.values().iterator();
  while (it.hasNext()) {
    @PKG@.ZDep d = (@PKG@.ZDep) it.next();
    if (writes >= max) { more = true; break; }
    boolean due = off || d.force || d.due <= now;
    if (d.state == 0) {
      String c0 = @PKG@.ZEng.blockAt(w, d.x, d.y, d.z);
      if (c0 == null) { if (!due) continue; }
      else if (c0.equals(d.orig)) { rw.drop(d); CANCELLED.incrementAndGet(); continue; }
      else {
        d.state = 1;
        if (!due) {
          if (c0.equals(d.ph)) continue;
          if (@PKG@.ZEng.put(w, d.x, d.y, d.z, d.ph, 0)) { PLACED.incrementAndGet(); writes++; }
          else @PKG@.ZCfg.warnOnce("ph:" + d.ph, "could not place the placeholder " + d.ph + " (type " + d.type + ") - the mined spot stays empty until it grows back");
          continue;
        }
      }
    }
    if (!due || d.next > now) continue;
    String cur = @PKG@.ZEng.blockAt(w, d.x, d.y, d.z);
    if (cur == null) {
      UNLOADED.incrementAndGet();
      if ((off || d.force) && (d.asked == 0L || now - d.asked >= REASK)) {
        Long ck = Long.valueOf((((long) (d.x >> 5)) << 32) | (((long) (d.z >> 5)) & 0xFFFFFFFFL));
        if (asked == null) asked = new java.util.HashSet();
        if (asked.contains(ck)) d.asked = now;
        else if (loads < LOADS) {
          asked.add(ck);
          loads++;
          d.asked = now;
          ASKED.incrementAndGet();
          @PKG@.ZEng.load(w, d.x, d.y, d.z, new @PKG@.ZPass(rw, w, true));
        }
      }
      continue;
    }
    if (cur.equals(d.orig)) { rw.drop(d); continue; }
    if (!cur.equals(d.ph) && !cur.equals("Empty")) {
      rw.drop(d);
      CHANGED.incrementAndGet();
      @PKG@.ZCfg.info("regrow: " + rw.world + " " + d.x + " " + d.y + " " + d.z + " is now " + cur + " (not the placeholder) - left as it is, " + d.orig + " not put back");
      continue;
    }
    if (@PKG@.ZEng.occupied(w, d.x, d.y, d.z)) {
      d.tries = d.tries + 1;
      d.next = now + (d.tries >= 12 ? 5000L : 1000L);
      BLOCKED.incrementAndGet();
      if (d.tries == 12) @PKG@.ZCfg.warnOnce("stuck:" + rw.world + ":" + d.key, "regrow: a player has stood in the block at " + rw.world + " " + d.x + " " + d.y + " " + d.z + " for 12 s - still waiting (tries every 5 s)");
      continue;
    }
    if (@PKG@.ZEng.put(w, d.x, d.y, d.z, d.orig, d.rot)) { rw.done(d, now); RESTORED.incrementAndGet(); writes++; }
    else { d.next = now + 5000L; WFAIL.incrementAndGet(); @PKG@.ZCfg.warnOnce("wfail:" + d.orig, "regrow: could not put " + d.orig + " back at " + rw.world + " " + d.x + " " + d.y + " " + d.z + " - trying again every 5 s"); }
  }
  if (!more && !rw.check.isEmpty()) {
    java.util.Iterator vi = rw.check.values().iterator();
    while (vi.hasNext()) {
      @PKG@.ZDep v = (@PKG@.ZDep) vi.next();
      if (writes >= max) { more = true; break; }
      Long vk = Long.valueOf(v.key);
      if (rw.dep.containsKey(vk)) { rw.check.remove(vk, v); continue; }
      String cv = @PKG@.ZEng.blockAt(w, v.x, v.y, v.z);
      if (cv == null) continue;
      if (!cv.equals(v.ph)) { rw.check.remove(vk, v); continue; }
      if (@PKG@.ZEng.occupied(w, v.x, v.y, v.z)) continue;
      if (@PKG@.ZEng.put(w, v.x, v.y, v.z, v.orig, v.rot)) {
        rw.check.remove(vk, v);
        v.due = now;
        rw.recent.put(vk, v);
        rw.append(v.vline());
        VERIFIED.incrementAndGet();
        writes++;
        @PKG@.ZCfg.info("regrow: " + rw.world + " " + v.x + " " + v.y + " " + v.z + " still held the placeholder " + v.ph + " after the restart (grew back just before an unclean stop) - " + v.orig + " put back");
      }
    }
  }
  if (more) @PKG@.ZEng.later(new @PKG@.ZPass(rw, w, true), NEXT);
  return writes;
}""")
M(pas, r"""
public void run() {
  if (this.k) { kick(this.w, this.rw); return; }
  this.rw.queued.set(0L);
  try { pass(this.rw, this.w); } catch (Throwable t) { @PKG@.ZCfg.warnOnce("pass", "regrow pass failed (logged once): " + t); }
}""")

rgn = mk("ZRegen")
for f in ("public static final java.util.concurrent.ConcurrentHashMap WORLDS = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile java.nio.file.Path DIR = null;", "public static final java.util.Random RND = new java.util.Random();",
          "public static final java.util.concurrent.atomic.AtomicLong BROKE = new java.util.concurrent.atomic.AtomicLong();",
          "public static final long AUDIT_CAP = 500000L;"):
    F(rgn, f)
M(rgn, r"""
public static @PKG@.ZRw rw(String w, boolean make) {
  if (w == null) return null;
  @PKG@.ZRw r = (@PKG@.ZRw) WORLDS.get(w);
  if (r != null || !make || DIR == null) return r;
  @PKG@.ZRw n = new @PKG@.ZRw(w, DIR);
  r = (@PKG@.ZRw) WORLDS.putIfAbsent(w, n);
  return r == null ? n : r;
}""")
M(rgn, r"""
public static @PKG@.ZDep at(String w, int x, int y, int z) {
  @PKG@.ZRw r = w == null ? null : (@PKG@.ZRw) WORLDS.get(w);
  return r == null ? null : (@PKG@.ZDep) r.dep.get(Long.valueOf(@PKG@.ZDep.key(x, y, z)));
}""")
M(rgn, r"""
public static boolean depleted(String w, int x, int y, int z) {
  @PKG@.ZRw r = w == null ? null : (@PKG@.ZRw) WORLDS.get(w);
  return r != null && !r.dep.isEmpty() && r.dep.containsKey(Long.valueOf(@PKG@.ZDep.key(x, y, z)));
}""")
# the wait of one break: regrow.<type> s x regen.speedMult x (1 +- regen.jitter), at least 0.5 s; -1 = this type does not regrow
M(rgn, r"""
public static long delay(String type) {
  int s = @PKG@.ZCfg.regrowSec(type);
  if (s <= 0) return -1L;
  double j = @PKG@.ZCfg.JITTER;
  double f = @PKG@.ZCfg.SPEED * (1.0 + j * (RND.nextDouble() * 2.0 - 1.0));
  long ms = Math.round(1000.0 * (double) s * f);
  return ms < 500L ? 500L : ms;
}""")
# regen.maxDepleted: the waiting block due first comes back at the next pass - FORCED, so an unloaded one is loaded + put back too (critic:
# else the map grows past the cap while its oldest entries sit in unloaded chunks)
M(rgn, r"""
public static void early(@PKG@.ZRw r) {
  @PKG@.ZDep best = null;
  java.util.Iterator it = r.dep.values().iterator();
  while (it.hasNext()) {
    @PKG@.ZDep d = (@PKG@.ZDep) it.next();
    if (d.due > 0L && !d.force && (best == null || d.due < best.due)) best = d;
  }
  if (best != null) { best.due = 0L; best.force = true; best.next = 0L; }
}""")
# THE BREAK HOOK (ZGuard, world thread, before the engine removes the block): 0 = registered (journal first, then the engine breaks it),
# 1 = no regrow here (vanilla break), 2 = already waiting (refuse: never mined twice for one regrow), 3 = the journal line could not be
# written (refuse - nothing may break without its record)
M(rgn, r"""
public static int broke(@WLD@ w, String wn, int x, int y, int z, String type) {
  if (!@PKG@.ZCfg.REGEN_ON || type == null || DIR == null) return 1;
  long ms = delay(type);
  if (ms < 0L) return 1;
  if (wn == null || !wn.matches("[A-Za-z0-9_.-]{1,64}")) { @PKG@.ZCfg.warnOnce("wname:" + wn, "regrow: world name '" + wn + "' cannot name a journal file - its blocks break like vanilla"); return 1; }
  String id = @PKG@.ZEng.blockAt(w, x, y, z);
  if (id == null || id.equals("Empty")) return 1;
  if (!@PKG@.ZDep.idOk(id)) { @PKG@.ZCfg.warnOnce("odd:" + id, "regrow: block id '" + id + "' cannot be journaled - it breaks like vanilla"); return 1; }
  int[] st = @PKG@.ZEng.stateAt(w, x, y, z);
  if (st != null && st[1] != 0) { @PKG@.ZCfg.warnOnce("filler:" + id, "regrow: " + id + " is part of a bigger block - it breaks like vanilla (no regrow)"); return 1; }
  String ph = @PKG@.ZCfg.placeholder(type);
  String pt = @PKG@.ZRules.listedAny(ph);
  if (pt != null) {
    @PKG@.ZCfg.warnOnce("phlisted:" + type + ":" + ph, "regrow." + type + ": the placeholder " + ph + " is itself a block of type " + pt + " (it could be mined at once) - @PH@ is used instead");
    ph = "@PH@";
    if (@PKG@.ZRules.listedAny(ph) != null) { @PKG@.ZCfg.warnOnce("phlisted:@PH@", "regrow: @PH@ is a listed block of a resource type - no placeholder is safe, listed blocks break like vanilla (no regrow)"); return 1; }
  }
  if (!@PKG@.ZDep.idOk(ph)) return 1;
  @PKG@.ZRw r = rw(wn, true);
  if (r == null) return 1;
  Long k = Long.valueOf(@PKG@.ZDep.key(x, y, z));
  if (r.dep.containsKey(k)) return 2;
  if (r.dep.size() >= @PKG@.ZCfg.MAXDEP) early(r);
  @PKG@.ZDep d = new @PKG@.ZDep(x, y, z, id, type, ph, st == null ? 0 : st[0], @PKG@.ZDep.now() + ms);
  if (r.dep.putIfAbsent(k, d) != null) return 2;
  if (!r.append(d.line())) { r.dep.remove(k, d); return 3; }
  BROKE.incrementAndGet();
  @PKG@.ZPass.kick(w, r);
  return 0;
}""".replace("@PH@", PLACEHOLDER))
# one snapshot / journal file into r (D adds or replaces, R removes); false = the file exists but could not be read (3 tries). Fixer: read
# leniently (a bad byte becomes U+FFFD and only that line is skipped as bad); a torn last line (no newline: a crash in the middle of a
# write) is skipped, never half-parsed ("Rock_Bedr"), warned with its text, and the file is kept as <file>.torn-<ms>. Fixer 2: V lines
# (grown back) go to the check list; a file with any other skipped line is kept as <file>.bad-<ms> before the start compacts it.
M(rgn, r"""
public static boolean readInto(@PKG@.ZRw r, java.nio.file.Path f, int[] bad) {
  if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return true;
  byte[] raw = null;
  Throwable last = null;
  for (int i = 0; i < 3 && raw == null; i++) {
    try { raw = java.nio.file.Files.readAllBytes(f); } catch (Throwable t) { last = t; try { Thread.sleep(100L); } catch (Throwable t2) { } }
  }
  if (raw == null) { @PKG@.ZCfg.warn("could not read " + f + " (3 tries): " + last + " - it is kept untouched (no snapshot rewrites it) until a start reads it; its waiting blocks stay placeholders meanwhile"); return false; }
  String text = new String(raw, java.nio.charset.StandardCharsets.UTF_8);
  java.util.List lines = new java.util.ArrayList(java.util.Arrays.asList(text.split("\n", -1)));
  String tail = (String) lines.remove(lines.size() - 1);
  if (tail.trim().length() > 0) {
    bad[0] = bad[0] + 1;
    java.nio.file.Path keep = f.resolveSibling(f.getFileName().toString() + ".torn-" + @PKG@.ZDep.now());
    try { java.nio.file.Files.copy(f, keep, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); } catch (Throwable t) { keep = null; }
    @PKG@.ZCfg.warn("regen/: the last line of " + f.getFileName() + " was cut off (a crash while writing) and is skipped: '" + tail.trim() + "'" + (keep != null ? " - the file is kept as " + keep.getFileName() : "") + "; /zones audit finds a placeholder it may have left");
  }
  int b0 = bad[0];
  for (int i = 0; i < lines.size(); i++) {
    String l = ((String) lines.get(i)).trim();
    if (l.length() == 0 || l.startsWith("#")) continue;
    String[] a = l.split("\\s+");
    if (a[0].equals("R") && a.length == 4) {
      try { r.dep.remove(Long.valueOf(@PKG@.ZDep.key(Integer.parseInt(a[1]), Integer.parseInt(a[2]), Integer.parseInt(a[3])))); } catch (Throwable t) { bad[0] = bad[0] + 1; }
      continue;
    }
    @PKG@.ZDep d = @PKG@.ZDep.parse(a);
    if (d == null) { bad[0] = bad[0] + 1; continue; }
    Long dk = Long.valueOf(d.key);
    if (a[0].equals("V")) { r.dep.remove(dk); r.check.put(dk, d); continue; }
    r.check.remove(dk);
    r.dep.put(dk, d);
  }
  if (bad[0] > b0) {
    java.nio.file.Path keep = f.resolveSibling(f.getFileName().toString() + ".bad-" + @PKG@.ZDep.now());
    try { java.nio.file.Files.copy(f, keep, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); } catch (Throwable t) { keep = null; }
    @PKG@.ZCfg.warn("regen/: " + (bad[0] - b0) + " unreadable lines in " + f.getFileName() + " skipped" + (keep != null ? " - the file is kept as " + keep.getFileName() + " (the start compacts the original)" : "") + "; /zones audit finds a placeholder they may have left");
  }
  return true;
}""")
M(rgn, r"""
public static synchronized void closeAll() {
  java.util.Iterator it = WORLDS.values().iterator();
  while (it.hasNext()) ((@PKG@.ZRw) it.next()).close();
}""")
# fixer: regen/alive = the time the server was last seen alive (written every 60 s while blocks wait + at shutdown) - regen.offlineCounts
# false measures the downtime from it (a crash after an idle hour no longer adds the hour to every timer)
M(rgn, r"""
public static void beat() {
  java.nio.file.Path d = DIR;
  if (d == null) return;
  boolean any = false;
  java.util.Iterator it = WORLDS.values().iterator();
  while (it.hasNext() && !any) any = !((@PKG@.ZRw) it.next()).dep.isEmpty();
  if (!any) return;
  try {
    java.nio.file.Files.createDirectories(d, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path f = d.resolve("alive");
    java.nio.file.Path tmp = d.resolve("alive.tmp");
    java.nio.file.Files.write(tmp, String.valueOf(@PKG@.ZDep.now()).getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { @PKG@.ZCfg.warnOnce("alive", "could not write regen/alive (the heartbeat): " + t); }
}""")
M(rgn, r"""
public static long lastBeat() {
  java.nio.file.Path d = DIR;
  if (d == null) return 0L;
  try {
    java.nio.file.Path f = d.resolve("alive");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return 0L;
    long v = Long.parseLong(new String(java.nio.file.Files.readAllBytes(f), "UTF-8").trim());
    return v > 0L ? v : 0L;
  } catch (Throwable t) { return 0L; }
}""")
# START (spec 9): every regen/<world>.snap + .journal replayed, then compacted into a fresh snapshot (not when a file could not be read);
# regen.offlineCounts false: the downtime (now - the newest file time) is added to every timer
M(rgn, r"""
public static synchronized String start(java.nio.file.Path dir) {
  closeAll();
  WORLDS.clear();
  DIR = dir;
  int n = 0;
  int[] bad = new int[1];
  try {
    if (dir == null || !java.nio.file.Files.isDirectory(dir, new java.nio.file.LinkOption[0])) return "no block waiting to grow back";
    long alive = lastBeat();
    java.util.TreeSet names = new java.util.TreeSet();
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(dir);
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext()) {
        String f = ((java.nio.file.Path) it.next()).getFileName().toString();
        if (f.endsWith(".snap")) names.add(f.substring(0, f.length() - 5));
        else if (f.endsWith(".journal")) names.add(f.substring(0, f.length() - 8));
      }
    } finally { ds.close(); }
    java.util.Iterator wi = names.iterator();
    while (wi.hasNext()) {
      String w = (String) wi.next();
      if (!w.matches("[A-Za-z0-9_.-]{1,64}")) { @PKG@.ZCfg.warn("regen/: '" + w + "' is not a world name - its files are left alone"); continue; }
      @PKG@.ZRw r = new @PKG@.ZRw(w, dir);
      boolean ok = readInto(r, r.sf, bad);
      ok = readInto(r, r.jf, bad) && ok;
      if (!@PKG@.ZCfg.OFFLINE && !r.dep.isEmpty()) {
        long last = 0L;
        try { if (java.nio.file.Files.exists(r.sf, new java.nio.file.LinkOption[0])) last = java.nio.file.Files.getLastModifiedTime(r.sf, new java.nio.file.LinkOption[0]).toMillis(); } catch (Throwable t) { }
        try { if (java.nio.file.Files.exists(r.jf, new java.nio.file.LinkOption[0])) last = Math.max(last, java.nio.file.Files.getLastModifiedTime(r.jf, new java.nio.file.LinkOption[0]).toMillis()); } catch (Throwable t) { }
        last = Math.max(last, alive);
        long down = last > 0L ? @PKG@.ZDep.now() - last : 0L;
        if (down > 0L) {
          java.util.Iterator di = r.dep.values().iterator();
          while (di.hasNext()) { @PKG@.ZDep d = (@PKG@.ZDep) di.next(); d.due = d.due + down; }
        }
      }
      r.hold = !ok;
      if (ok) r.snapshot(true);
      if (r.dep.isEmpty() && r.check.isEmpty() && ok) continue;
      WORLDS.put(w, r);
      n = n + r.dep.size();
    }
  } catch (Throwable t) { @PKG@.ZCfg.warn("could not read the regrow files in " + dir + ": " + t); }
  if (bad[0] > 0) @PKG@.ZCfg.warn("regen/: " + bad[0] + " unreadable journal / snapshot lines skipped");
  return (n == 0 ? "no block" : n + (n == 1 ? " block" : " blocks")) + " waiting to grow back" + (n == 0 ? "" : " in " + WORLDS.size() + (WORLDS.size() == 1 ? " world" : " worlds"))
    + (bad[0] > 0 ? " (" + bad[0] + " unreadable lines skipped)" : "");
}""")
M(rgn, r"""
public static void snapshotAll(boolean force) {
  java.util.Iterator it = WORLDS.values().iterator();
  while (it.hasNext()) ((@PKG@.ZRw) it.next()).snapshot(force);
}""")
M(rgn, r"""
public static void shutdown() {
  try { beat(); } catch (Throwable t) { }
  try { snapshotAll(true); } catch (Throwable t) { }
  closeAll();
}""")
# /zones restore <region|all> + the Server Setup action: every waiting block (in the region) due NOW, forced (unloaded chunks are asked for);
# { blocks, worlds not loaded, blocks in them }
M(rgn, r"""
public static int[] restore(@PKG@.ZRegion reg) {
  int n = 0;
  int wn = 0;
  int nb = 0;
  java.util.Iterator it = WORLDS.values().iterator();
  while (it.hasNext()) {
    @PKG@.ZRw r = (@PKG@.ZRw) it.next();
    if (reg != null && !reg.world.equals(r.world)) continue;
    int m = 0;
    java.util.Iterator di = r.dep.values().iterator();
    while (di.hasNext()) {
      @PKG@.ZDep d = (@PKG@.ZDep) di.next();
      if (reg != null && !reg.contains(d.x, d.y, d.z)) continue;
      d.force = true;
      d.asked = 0L;
      d.next = 0L;
      m++;
    }
    if (m == 0) continue;
    n = n + m;
    @WLD@ w = @PKG@.ZEng.world(r.world);
    if (w == null) { wn++; nb = nb + m; continue; }
    @PKG@.ZPass.kick(w, r);
  }
  return new int[] { n, wn, nb };
}""")
M(rgn, r"""
public static java.util.ArrayList status() {
  java.util.ArrayList out = new java.util.ArrayList();
  long now = @PKG@.ZDep.now();
  int total = 0;
  java.util.ArrayList per = new java.util.ArrayList();
  java.util.TreeSet names = new java.util.TreeSet(WORLDS.keySet());
  java.util.Iterator wi = names.iterator();
  while (wi.hasNext()) {
    @PKG@.ZRw r = (@PKG@.ZRw) WORLDS.get(wi.next());
    if (r != null && r.hold) per.add(" " + r.world + ": ITS REGROW FILES COULD NOT BE READ at the start - kept untouched (restart to read them again; /zones audit finds their placeholders)");
    if (r != null && !r.check.isEmpty()) per.add(" " + r.world + ": " + r.check.size() + " spots that grew back just before the last stop are checked when their chunk loads (a crash may have saved the placeholder)");
    if (r == null || r.dep.isEmpty()) continue;
    java.util.TreeMap types = new java.util.TreeMap();
    long next = Long.MAX_VALUE;
    int forced = 0;
    int stuck = 0;
    java.util.Iterator di = r.dep.values().iterator();
    while (di.hasNext()) {
      @PKG@.ZDep d = (@PKG@.ZDep) di.next();
      Integer c = (Integer) types.get(d.type);
      types.put(d.type, Integer.valueOf(c == null ? 1 : c.intValue() + 1));
      if (d.due < next) next = d.due;
      if (d.force) forced++;
      if (d.tries > 0) stuck++;
    }
    int n = r.dep.size();
    total = total + n;
    StringBuilder ts = new StringBuilder();
    java.util.Iterator ti = types.keySet().iterator();
    while (ti.hasNext()) { String t = (String) ti.next(); if (ts.length() > 0) ts.append(", "); ts.append(t).append(' ').append(types.get(t)); }
    per.add(" " + r.world + ": " + n + " waiting (" + ts + "); next back in " + Math.max(0L, (next - now + 999L) / 1000L) + " s"
      + (forced > 0 ? "; " + forced + " being put back now" : "") + (stuck > 0 ? "; " + stuck + " wait for a player to step out" : ""));
  }
  out.add("Regrowing blocks: " + (@PKG@.ZCfg.REGEN_ON ? "ON" : "OFF (every waiting block is being put back)") + " - " + total + " waiting"
    + "; since the start " + BROKE.get() + " mined, " + @PKG@.ZPass.RESTORED.get() + " grown back"
    + (@PKG@.ZPass.CHANGED.get() > 0L ? ", " + @PKG@.ZPass.CHANGED.get() + " changed by hand (left)" : "")
    + (@PKG@.ZPass.CANCELLED.get() > 0L ? ", " + @PKG@.ZPass.CANCELLED.get() + " breaks stopped by another mod" : "")
    + (@PKG@.ZPass.VERIFIED.get() > 0L ? ", " + @PKG@.ZPass.VERIFIED.get() + " placeholders left by an unclean stop put back" : ""));
  out.addAll(per);
  if (@PKG@.ZRw.JFAIL.get() > 0L) out.add(" JOURNAL WRITE ERRORS: " + @PKG@.ZRw.JFAIL.get() + " (those breaks were refused) - see the server log");
  if (@PKG@.ZPass.WFAIL.get() > 0L) out.add(" Block write errors: " + @PKG@.ZPass.WFAIL.get() + " (retried every 5 s) - see the server log");
  return out;
}""")
# fixer: the vanilla id a default wildcard pattern stands for (build-time table FALLBACK: Ore_Copper* -> Ore_Copper_Stone); null = none
M(rgn, r"""
public static String fallback(String pat) {
  if (pat == null) return null;
@FB@
  return null;
}""".replace("@FB@", "\n".join('  if (pat.equalsIgnoreCase("%s")) return "%s";' % kv for kv in sorted(FALLBACK.items()))))
# the first plain block id of a type (no * / +), else the first wildcard's vanilla id: what /zones audit fix puts back; null = none
M(rgn, r"""
public static String plain(String type) {
  Object o = @PKG@.ZCfg.TYPES.get(type);
  if (!(o instanceof String[])) return null;
  String[] a = (String[]) o;
  for (int i = 0; i < a.length; i++) if (a[i].indexOf('*') < 0 && !a[i].endsWith("+") && @PKG@.ZDep.idOk(a[i])) return a[i];
  for (int i = 0; i < a.length; i++) { String f = fallback(a[i]); if (f != null) return f; }
  return null;
}""")
# /zones audit <region> [fix] (spec 5.1 / 9 "lost write"): placeholder blocks of the region's regrowing types in its LOADED chunks that
# no waiting entry explains; fix = each back to the first plain block id of the first regrowing type with that placeholder
M(rgn, r"""
public static java.util.ArrayList audit(@WLD@ w, @PKG@.ZRegion reg, boolean fix) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.ArrayList phs = new java.util.ArrayList();
  for (int i = 0; reg.mode == 1 && i < reg.types.length; i++) {
    if (@PKG@.ZCfg.regrowSec(reg.types[i]) <= 0) continue;
    String ph = @PKG@.ZCfg.placeholder(reg.types[i]);
    if (!phs.contains(ph)) phs.add(ph);
  }
  if (phs.isEmpty()) { out.add("Region " + reg.id + " has no regrowing resource types - nothing to audit."); return out; }
  String[] ids = (String[]) phs.toArray(new String[phs.size()]);
  @PKG@.ZRw r = (@PKG@.ZRw) WORLDS.get(reg.world);
  int found = 0;
  int orphans = 0;
  int fixed = 0;
  int nofix = 0;
  long read = 0L;
  int unloaded = 0;
  java.util.ArrayList sample = new java.util.ArrayList();
  int[] b = reg.box;
  for (int i = 0; i + 5 < b.length; i = i + 6) {
    int[] stats = new int[2];
    java.util.List pos = @PKG@.ZEng.scan(w, new int[] { b[i], b[i + 1], b[i + 2], b[i + 3], b[i + 4], b[i + 5] }, ids, stats, AUDIT_CAP - read);
    read = read + (long) stats[0];
    unloaded = unloaded + stats[1];
    for (int j = 0; pos != null && j < pos.size(); j++) {
      int[] p = (int[]) pos.get(j);
      found++;
      if (r != null && r.dep.containsKey(Long.valueOf(@PKG@.ZDep.key(p[0], p[1], p[2])))) continue;
      orphans++;
      if (sample.size() < 5) sample.add(p[0] + " " + p[1] + " " + p[2]);
      if (!fix) continue;
      String back = null;
      for (int t = 0; t < reg.types.length; t++) {
        if (@PKG@.ZCfg.regrowSec(reg.types[t]) <= 0 || !ids[p[3]].equals(@PKG@.ZCfg.placeholder(reg.types[t]))) continue;
        String pb = plain(reg.types[t]);
        if (pb == null) continue;
        if (back == null || reg.types[t].equals("stone")) back = pb;
      }
      if (back != null && @PKG@.ZEng.put(w, p[0], p[1], p[2], back, 0)) fixed++; else nofix++;
    }
    if (read >= AUDIT_CAP) break;
  }
  out.add("Audit of " + reg.id + ": " + read + " blocks read" + (unloaded > 0 ? " (" + unloaded + " chunk sections not loaded - go closer and run it again)" : "")
    + (read >= AUDIT_CAP ? " - STOPPED at " + AUDIT_CAP + " blocks" : "") + "; " + found + " placeholder blocks, " + orphans + " with no timer.");
  if (!sample.isEmpty()) out.add(" e.g. at " + sample);
  if (fix) out.add(" Put back: " + fixed + (nofix > 0 ? "; " + nofix + " left (their type has no plain block id, or the write failed)" : "") + ".");
  else if (orphans > 0) out.add(" /zones audit " + reg.id + " fix turns them into their type's first block (bedrock you placed there on purpose would change too).");
  if (fix && orphans > 0) @PKG@.ZCfg.info("/zones audit " + reg.id + " fix: " + fixed + " placeholders put back, " + nofix + " left");
  return out;
}""")

tkr = mk("ZTicker", None, ("java.lang.Runnable",))
for f in ("public static volatile java.util.concurrent.ScheduledFuture FUT = null;", "public static long N = 0L;", "public static boolean FAILED_ONCE = false;"):
    F(tkr, f)
C(tkr, "public ZTicker() { }")
M(tkr, r"""
public void run() {
  try {
    N = N + 1L;
    java.util.Iterator it = @PKG@.ZRegen.WORLDS.values().iterator();
    while (it.hasNext()) {
      @PKG@.ZRw r = (@PKG@.ZRw) it.next();
      if (r.dep.isEmpty() && r.check.isEmpty()) continue;
      @WLD@ w = @PKG@.ZEng.world(r.world);
      if (w != null) @PKG@.ZPass.kick(w, r);
    }
    if (N % 60L == 0L) { @PKG@.ZRegen.snapshotAll(false); @PKG@.ZRegen.beat(); }
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ZCfg.warn("regrow tick failed (logged once): " + t); }
  }
}""")
M(tkr, r"""
public static void stop() {
  java.util.concurrent.ScheduledFuture f = FUT;
  FUT = null;
  if (f != null) { try { f.cancel(false); } catch (Throwable t) { } }
}""")
M(tkr, r"""
public static void start() {
  stop();
  FUT = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.ZTicker(), 1000L, 1000L, java.util.concurrent.TimeUnit.MILLISECONDS);
}""")
# the Server Setup action "Restore all" (the kit calls it with the admin's id + name)
M(cfg, r"""
public static Object[] restoreAction(java.util.UUID who, String name) {
  int[] r = @PKG@.ZRegen.restore(null);
  String m = r[0] == 0 ? "Nothing is waiting to grow back." : "Putting back " + r[0] + " waiting blocks now" + (r[1] > 0 ? " (" + r[2] + " in worlds that are not loaded come back when they load)" : "") + ". /zones status shows what is left.";
  info("restore all (Server Setup, " + name + "): " + r[0] + " blocks");
  return new Object[] { "ok", "", m };
}""")
# the kit's check of a regrow table line (regrow[<type>]); the placeholder must be a block the game knows (when the block map is loaded)
# and (fixer) never a listed block of any type (it could be mined at once); logs / crops stay 0 until Z3
M(cfg, r"""
public static String checkRegrow(String key, String value) {
  if (key == null || !key.startsWith("regrow[") || !key.endsWith("]")) return "Unknown table line.";
  String e = key.substring(7, key.length() - 1);
  if (!e.matches("[a-z0-9_]{1,32}")) return "A type id is 1-32 of a-z, 0-9 and _.";
  if (value == null) return null;
  String why = regrowWhy(value);
  if (why != null) return "Write <seconds>,<placeholder block>: " + why + ".";
  if (noZ3(e) && Integer.parseInt(value.replace('|', ',').split(",", -1)[0].trim()) > 0) return e + " cannot grow back yet (whole trees and crop stages come in a later version) - keep 0.";
  String ph = phOf(value);
  String lt = @PKG@.ZRules.listedAny(ph);
  if (lt != null) return "The placeholder " + ph + " is itself a block of type " + lt + " - players could mine it at once. Pick a block no type lists (e.g. @PH@).";
  try {
    Object m = @BTY@.getAssetMap();
    if (m != null && @BTY@.getAssetMap().getIndex(ph) == Integer.MIN_VALUE) return "No block '" + ph + "' in the game files.";
  } catch (Throwable t) { }
  return null;
}""".replace("@PH@", PLACEHOLDER))

# =====================================================================================================================================
# ZGuard: ONE registerSystem per class; the acting entity's event (Archetype.empty() like SkyyIslands' guards)
'''
P.rep("# ZGuard: ONE registerSystem per class; the acting entity's event (Archetype.empty() like SkyyIslands' guards)\n", REGEN)

# ---------------------------------------------------------------------------------------------------- ZGuard: the regrow hooks
P.rep('''M(guard, "public boolean wandable(@EV@ ev) { return false; }")''', '''M(guard, "public boolean wandable(@EV@ ev) { return false; }")
# 0.2.0: only the BreakBlockEvent guard starts a regrow (a dig / Primary use only cracks; the break event follows)
M(guard, "public boolean regen(@EV@ ev) { return false; }")
M(guard, r"""
public static int regrow(@WLD@ w, String wn, @PKG@.ZIndex ix, @V3I@ b, String id) {
  String t = @PKG@.ZRules.resType(ix, wn, b.x, b.y, b.z, id);
  if (t == null) return 1;
  return @PKG@.ZRegen.broke(w, wn, b.x, b.y, b.z, t);
}""")''')
P.rep('''    if (!@PKG@.ZCfg.ON) return;
    @PKG@.ZIndex ix = @PKG@.ZStore.INDEX;
    boolean pw = @PKG@.ZCfg.protectedWorld(wn);
    if (!pw && !ix.has(wn)) return;
    scoped = pw || ix.top(wn, b.x, b.y, b.z) != null;
    int act = action(ev, held);
    if (act == @PKG@.ZRules.OTHER) return;
    @REF@ r = chunk.getReferenceTo(idx);
    @PR@ pr = r == null ? null : (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) {
      if (!@PKG@.ZCfg.MOBS || (act != @PKG@.ZRules.BREAK && act != @PKG@.ZRules.PLACE)) return;
      if (@PKG@.ZRules.decide(ix, wn, pw, b.x, b.y, b.z, act, block(ev)) != @PKG@.ZRules.ALLOW) {
        if (ev instanceof @ICE@) ((@ICE@) ev).setCancelled(true);
        MOBS.incrementAndGet();
      }
      return;
    }
    if (@PKG@.ZBuild.bypass(pr)) { free = true; BYPASSED.incrementAndGet(); return; }
    int d = @PKG@.ZRules.decide(ix, wn, pw, b.x, b.y, b.z, act, block(ev));
    if (d == @PKG@.ZRules.ALLOW) { ALLOWED.incrementAndGet(); return; }''',
      '''    boolean dep = @PKG@.ZRegen.depleted(wn, b.x, b.y, b.z);
    if (!@PKG@.ZCfg.ON && !dep) return;
    @PKG@.ZIndex ix = @PKG@.ZStore.INDEX;
    boolean pw = @PKG@.ZCfg.protectedWorld(wn);
    if (!dep && !pw && !ix.has(wn)) return;
    scoped = dep || pw || ix.top(wn, b.x, b.y, b.z) != null;
    int act = action(ev, held);
    if (act == @PKG@.ZRules.OTHER) return;
    boolean hit = dep && (act == @PKG@.ZRules.BREAK || act == @PKG@.ZRules.PLACE);
    @REF@ r = chunk.getReferenceTo(idx);
    @PR@ pr = r == null ? null : (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) {
      if (hit) { if (ev instanceof @ICE@) ((@ICE@) ev).setCancelled(true); MOBS.incrementAndGet(); return; }
      if (!@PKG@.ZCfg.ON) return;
      if (!@PKG@.ZCfg.MOBS || (act != @PKG@.ZRules.BREAK && act != @PKG@.ZRules.PLACE)) return;
      if (@PKG@.ZRules.decide(ix, wn, pw, b.x, b.y, b.z, act, block(ev)) != @PKG@.ZRules.ALLOW || (regen(ev) && regrow(w, wn, ix, b, block(ev)) >= 2)) {
        if (ev instanceof @ICE@) ((@ICE@) ev).setCancelled(true);
        MOBS.incrementAndGet();
      }
      return;
    }
    if (@PKG@.ZBuild.bypass(pr)) { free = true; BYPASSED.incrementAndGet(); return; }
    if (hit) {
      if (ev instanceof @ICE@) ((@ICE@) ev).setCancelled(true);
      REFUSED.incrementAndGet();
      GROWING.incrementAndGet();
      @PKG@.ZMsg.refuse(pr, "Growing back - wait a moment.");
      return;
    }
    if (!@PKG@.ZCfg.ON) return;
    int d = @PKG@.ZRules.decide(ix, wn, pw, b.x, b.y, b.z, act, block(ev));
    if (d == @PKG@.ZRules.ALLOW) {
      int g = regen(ev) ? regrow(w, wn, ix, b, block(ev)) : 1;
      if (g >= 2) {
        if (ev instanceof @ICE@) ((@ICE@) ev).setCancelled(true);
        REFUSED.incrementAndGet();
        @PKG@.ZMsg.refuse(pr, g == 2 ? "Growing back - wait a moment." : "You can't gather here right now - the server could not save it (see the server log).");
        return;
      }
      ALLOWED.incrementAndGet();
      return;
    }''')
P.rep('''          "public static final java.util.concurrent.atomic.AtomicLong FAILS = new java.util.concurrent.atomic.AtomicLong();"):
    F(guard, f)''', '''          "public static final java.util.concurrent.atomic.AtomicLong FAILS = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong GROWING = new java.util.concurrent.atomic.AtomicLong();"):
    F(guard, f)''')
P.rep('''M(gP, "public @V3I@ target(@EV@ ev) { return ev instanceof @PLBE@ ? ((@PLBE@) ev).getTargetBlock() : null; }")''',
      '''M(gB, "public boolean regen(@EV@ ev) { return ev instanceof @BBE@; }")   # 0.2.0
M(gP, "public @V3I@ target(@EV@ ev) { return ev instanceof @PLBE@ ? ((@PLBE@) ev).getTargetBlock() : null; }")''')

# ---------------------------------------------------------------------------------------------------- bridge: a waiting spot = deny
# fixer 2: also while zones.on is off (the placeholder must never be mined - critic)
P.rep('''    if (!@PKG@.ZCfg.ON) return "allow";
    String act = a.length > 4''', '''    String act = a.length > 4''')
P.rep('''    String id = a.length > 5 && a[5] != null ? String.valueOf(a[5]) : "";
    int d = @PKG@.ZRules.decide(ix, w, @PKG@.ZCfg.protectedWorld(w), x, y, z, ac, id);''',
      '''    String id = a.length > 5 && a[5] != null ? String.valueOf(a[5]) : "";
    if ((ac == @PKG@.ZRules.BREAK || ac == @PKG@.ZRules.PLACE) && @PKG@.ZRegen.depleted(w, x, y, z)) return "deny";
    if (!@PKG@.ZCfg.ON) return "allow";
    int d = @PKG@.ZRules.decide(ix, w, @PKG@.ZCfg.protectedWorld(w), x, y, z, ac, id);''')

# ---------------------------------------------------------------------------------------------------- Server Setup rows
P.rep('''CATS = [("zones", "Protection"), ("regions", "Regions"), ("titles", "Area titles"), ("tools", "Builder tools"), ("types", "Resource types")]''',
      '''CATS = [("zones", "Protection"), ("regions", "Regions"), ("titles", "Area titles"), ("tools", "Builder tools"), ("types", "Resource types"),
        ("regen", "Regrowing blocks")]''')
P.rep('''     "reload:ZCfg.reloadTypes@types.properties:type.;check=ZCfg.checkType"),
]''', '''     "reload:ZCfg.reloadTypes@types.properties:type.;check=ZCfg.checkType"),
    # 0.2.0 regrowing blocks (regen.properties)
    ("regen.enabled", "Regrowing blocks", "regen", "bool", "true", "", "", "", "", "live,danger",
     "Mined listed blocks in SKYBLOCK areas become a placeholder, then grow back. Off: all come back now.",
     "field:ZCfg.REGEN_ON@regen.properties:regen.enabled"),
    ("regen.speedMult", "Regrow time multiplier", "regen", "dec", "1", "0.1", "10", "", "", "live",
     "Every regrow time x this (0.5 = twice as fast).", "field:ZCfg.SPEED@regen.properties:regen.speedMult"),
    ("regen.jitter", "Regrow time spread", "regen", "dec", "0.2", "0", "0.5", "", "", "live,adv",
     "Each time x (1 - this .. 1 + this), so a vein refills block by block.", "field:ZCfg.JITTER@regen.properties:regen.jitter"),
    ("regen.offlineCounts", "Server downtime counts", "regen", "bool", "true", "", "", "", "", "live,adv",
     "On: time while the server is off counts toward the timers (read at start).", "field:ZCfg.OFFLINE@regen.properties:regen.offlineCounts"),
    ("regen.defaultSec", "Regrow time without a row", "regen", "int", "5", "1", "3600", "", "s", "live",
     "A resource type with no row in the table below grows back after this.", "field:ZCfg.DEFSEC@regen.properties:regen.defaultSec"),
    ("regen.passBatch", "Blocks put back per pass", "regen", "int", "200", "10", "5000", "", "", "live,adv",
     "Per world, at most this many block writes in one world tick; the rest follow next tick (lag guard).", "field:ZCfg.PASS@regen.properties:regen.passBatch"),
    ("regen.maxDepleted", "Most waiting blocks per world", "regen", "int", "20000", "100", "200000", "", "", "live,adv",
     "Above this the oldest waiting block comes back early.", "field:ZCfg.MAXDEP@regen.properties:regen.maxDepleted"),
    ("regrow", "Regrow time + placeholder per type", "regen", "table", "", "0", "3600", "int|text;none;Seconds|Placeholder block", "", "live",
     "0 s = no regrow (logs + crops: 0 for now). Placeholder = what stands there; never a listed block.",
     "reload:ZCfg.reloadRegen@regen.properties:regrow.;check=ZCfg.checkRegrow"),
    ("regen.restoreAll", "Put every mined block back now", "regen", "action", "", "", "", "Restore all", "", "live,danger",
     "Run before rolling SkyyZones back. Loaded chunks at once, the rest load first.", "action:ZCfg.restoreAction"),
]''')
P.rep('''               FILES=["Skyy_SkyyZones/config.properties", "Skyy_SkyyZones/types.properties"],''',
      '''               FILES=["Skyy_SkyyZones/config.properties", "Skyy_SkyyZones/types.properties", "Skyy_SkyyZones/regen.properties"],''')
P.rep('''               RELOAD=None, KEEP=10, DEFAULTS={"config.properties": CONFIG_TEXT, "types.properties": TYPES_TEXT},''',
      '''               RELOAD=None, KEEP=10, DEFAULTS={"config.properties": CONFIG_TEXT, "types.properties": TYPES_TEXT, "regen.properties": REGEN_TEXT},''')

# ---------------------------------------------------------------------------------------------------- commands
P.rep('''  say(pr, "/zones info - what protects the block you look at   /zones list - the regions of this world");''',
      '''  say(pr, "/zones info - what protects the block you look at   /zones list - the regions of this world   /zones status - regrowing blocks");''')
P.rep('''  say(pr, "/zones reload (re-read the files)   /zones reload clear (accept a regions file with no region: removes every region)");''',
      '''  say(pr, "/zones reload (re-read the files)   /zones reload clear (accept a regions file with no region: removes every region)");
  say(pr, "/zones restore <region or all> - every mined block back now (run 'all' before rolling SkyyZones back)   /zones audit <region> [fix] - placeholders with no timer");''')
P.rep('''      + " | Chests: " + @PKG@.ZRules.verdict(@PKG@.ZRules.decide(ix, wn, pw, p[0], p[1], p[2], @PKG@.ZRules.CONTAINER, id)));
  }''', '''      + " | Chests: " + @PKG@.ZRules.verdict(@PKG@.ZRules.decide(ix, wn, pw, p[0], p[1], p[2], @PKG@.ZRules.CONTAINER, id)));
  }
  @PKG@.ZDep dd = @PKG@.ZRegen.at(wn, p[0], p[1], p[2]);
  if (dd != null) say(pr, "Mined: grows back as " + dd.orig + " in " + Math.max(0L, (dd.due - @PKG@.ZDep.now() + 999L) / 1000L) + " s (type " + dd.type + (dd.force ? ", being put back now" : "") + ").");''')
P.rep('''    say(pr, (i == 0 ? "Region here (wins): " : "Also here: ") + r.summary() + (lt != null ? " - this block is type " + lt : ""));''',
      '''    say(pr, (i == 0 ? "Region here (wins): " : "Also here: ") + r.summary() + (lt != null ? " - this block is type " + lt + grows(lt) : ""));''')
# fixer (critic: logs / crops in a SKYBLOCK region vanish for good with no word to the builder)
P.rep('''M(cmds, r"""
public static void info(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ w) {''', '''M(cmds, r"""
public static String grows(String type) {
  if (!@PKG@.ZCfg.REGEN_ON) return " (regrowing is off: once mined it stays gone)";
  int s = @PKG@.ZCfg.regrowSec(type);
  if (s <= 0) return " (does NOT grow back" + (@PKG@.ZCfg.noZ3(type) ? " yet - whole trees / crops come later" : "") + ": once mined it stays gone)";
  return " (grows back after about " + s + " s)";
}""")
M(cmds, r"""
public static void noRegrow(@PR@ pr, String id) {
  @PKG@.ZRegion r = @PKG@.ZStore.get(id);
  if (r == null || r.mode != 1) return;
  for (int i = 0; i < r.types.length; i++) {
    if (@PKG@.ZCfg.regrowSec(r.types[i]) <= 0) bad(pr, "Note: " + r.types[i] + grows(r.types[i]) + ".");
  }
}""")
M(cmds, r"""
public static void info(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ w) {''')
P.rep('''    if (a.length == 5 && m != null && !m.startsWith("!")) result(pr, @PKG@.ZStore.set(id, "types", a[4], who));''',
      '''    if (a.length == 5 && m != null && !m.startsWith("!")) { result(pr, @PKG@.ZStore.set(id, "types", a[4], who)); noRegrow(pr, id); }''')
P.rep('''    result(pr, @PKG@.ZStore.set(id, sub, a[3], who));
    return;''', '''    result(pr, @PKG@.ZStore.set(id, sub, a[3], who));
    if (sub.equals("types") || sub.equals("mode")) noRegrow(pr, id);
    return;''')
P.rep('''M(cmds, r"""
public static void run(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ w, String[] a) {''', '''# 0.2.0 regrowing blocks: status (builders), restore + audit (admins)
M(cmds, r"""
public static void status(@PR@ pr) {
  java.util.ArrayList l = @PKG@.ZRegen.status();
  for (int i = 0; i < l.size(); i++) say(pr, (String) l.get(i));
}""")
M(cmds, r"""
public static void restore(@PR@ pr, String id) {
  @PKG@.ZRegion reg = null;
  if (!id.equals("all")) {
    reg = @PKG@.ZStore.get(id);
    if (reg == null) { bad(pr, "No region " + id + " (/zones list) - or /zones restore all."); return; }
  }
  int[] r = @PKG@.ZRegen.restore(reg);
  @PKG@.ZCfg.info("/zones restore " + id + " by " + pr.getUsername() + ": " + r[0] + " blocks");
  if (r[0] == 0) { say(pr, "Nothing is waiting to grow back" + (reg == null ? "." : " in " + id + ".")); return; }
  ok(pr, "Putting back " + r[0] + " waiting " + (r[0] == 1 ? "block" : "blocks") + " now (loaded chunks at once, the others are loaded first). /zones status shows what is left.");
  if (r[1] > 0) bad(pr, r[2] + " of them are in " + r[1] + (r[1] == 1 ? " world" : " worlds") + " that are not loaded - they come back when the world loads.");
}""")
M(cmds, r"""
public static void audit(@WLD@ w, @PR@ pr, String id, boolean fix) {
  @PKG@.ZRegion reg = @PKG@.ZStore.get(id);
  if (reg == null || !reg.world.equals(w.getName())) { bad(pr, "No region " + id + " in this world (/zones list)."); return; }
  java.util.ArrayList l = @PKG@.ZRegen.audit(w, reg, fix);
  for (int i = 0; i < l.size(); i++) say(pr, (String) l.get(i));
}""")
M(cmds, r"""
public static void run(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ w, String[] a) {''')
P.rep('''    if (!c.equals("wand") && !c.equals("reload") && !c.equals("protect") && !c.equals("type") && !c.equals("region")) { help(pr); return; }''',
      '''    if (c.equals("status") && a.length == 1) { status(pr); return; }
    if (!c.equals("wand") && !c.equals("reload") && !c.equals("protect") && !c.equals("type") && !c.equals("region") && !c.equals("restore") && !c.equals("audit")) { help(pr); return; }''')
P.rep('''    if (c.equals("region") && a.length >= 3) { region(ref, st, pr, wn, a); return; }''',
      '''    if (c.equals("region") && a.length >= 3) { region(ref, st, pr, wn, a); return; }
    if (c.equals("restore") && a.length == 2) { restore(pr, a[1].toLowerCase()); return; }
    if (c.equals("audit") && (a.length == 2 || a.length == 3 && a[2].equalsIgnoreCase("fix"))) { audit(w, pr, a[1].toLowerCase(), a.length == 3); return; }''')
P.rep('''VARIANTS = [("ZCmd1", ["word"], "(builders) /zones info, list, show, build, help; (admins) wand, reload"),
            ("ZCmd2", ["word", "value"], "(builders) /zones show <region, off or seconds>, /zones build <on or off>; (admins) /zones protect <on or off>, /zones reload clear"),
            ("ZCmd3", ["word", "name", "value"], "(builders) /zones show <region> <seconds>; (admins) /zones region <delete or addbox> <name>, /zones type <type> <block ids, none or look>"),''',
      '''VARIANTS = [("ZCmd1", ["word"], "(builders) /zones info, list, show, build, status, help; (admins) wand, reload"),
            ("ZCmd2", ["word", "value"], "(builders) /zones show <region, off or seconds>, /zones build <on or off>; (admins) /zones protect <on or off>, /zones reload clear, /zones restore <region or all>, /zones audit <region>"),
            ("ZCmd3", ["word", "name", "value"], "(builders) /zones show <region> <seconds>; (admins) /zones region <delete or addbox> <name>, /zones type <type> <block ids, none or look>, /zones audit <region> fix"),''')
P.rep('''ARG_HELP = {"word": "info, list, show, build, help, wand, reload, protect, type or region",''',
      '''ARG_HELP = {"word": "info, list, show, build, status, help, wand, reload, protect, type, region, restore or audit",''')

# ---------------------------------------------------------------------------------------------------- the plugin
P.rep('''  @PKG@.ZSave.LOGF = dir.resolve("region-changes.log");
  return @PKG@.ZCfg.loadCfg(true) + "; " + @PKG@.ZCfg.loadTypes(true) + "; " + @PKG@.ZStore.start();''',
      '''  @PKG@.ZSave.LOGF = dir.resolve("region-changes.log");
  @PKG@.ZSave.GOOD = dir.resolve("regions.good.properties");
  @PKG@.ZCfg.RFILE = dir.resolve("regen.properties");
  return @PKG@.ZCfg.loadCfg(true) + "; " + @PKG@.ZCfg.loadTypes(true) + "; " + @PKG@.ZCfg.loadRegen(true) + "; " + @PKG@.ZStore.start() + "; " + @PKG@.ZRegen.start(dir.resolve("regen"));''')
P.rep('''    @PKG@.ZFn.publish();
    getLogger().at(java.util.logging.Level.INFO).log("[SkyyZones] @VERSION@ ready - protected worlds + regions (FULL / SKYBLOCK, Z1: no regrow yet); "''',
      '''    @PKG@.ZFn.publish();
    try { @PKG@.ZTicker.start(); } catch (Throwable t) { @PKG@.ZCfg.warn("the regrow timer did not start - mined blocks wait until it does (restart): " + t); }
    getLogger().at(java.util.logging.Level.INFO).log("[SkyyZones] @VERSION@ ready - protected worlds + regions (FULL / SKYBLOCK + regrowing blocks, Z2); "''')
P.rep('''  try { @PKG@.ZFn.unpublish(); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''', '''  try { @PKG@.ZFn.unpublish(); } catch (Throwable t) { }
  try { @PKG@.ZTicker.stop(); } catch (Throwable t) { }
  try { @PKG@.ZRegen.shutdown(); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''')
P.rep('''ALL = [api, cfg, reg, idx, rules, sav, sto, eng, msg, bld, sel, wnd, guard] + gcls + [shw, tick, fn, rkit, cmds] + vcls + [cmd, quit_, pl]''',
      '''ALL = [api, cfg, reg, idx, rules, sav, sto, eng, msg, bld, sel, wnd, dep, rw, pas, rgn, tkr, guard] + gcls + [shw, tick, fn, rkit, cmds] + vcls + [cmd, quit_, pl]''')
P.rep('''and SKYBLOCK areas (only the listed resource blocks break - regrowing comes in a later version); deny by default;''',
      '''and SKYBLOCK areas (only the listed resource blocks break; mined ones turn into a placeholder for a few seconds, then grow back); deny by default;''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
print("wrote SkyyZones/build_skyyzones_0.2.0.py (%d changes)" % len(P.changes))
