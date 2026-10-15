"""Derive SkyyTrees/build_skyytrees_0.3.11.py from the LIVE generated SkyyTrees/build_skyytrees_0.3.10.py (the tools/deploy_set.py SET pin).
Run:  python tools/trees_0_3_11_patch.py   then   python SkyyTrees/build_skyytrees_0.3.11.py   (never --deploy: coordinated deploy)
      then python SkyyTrees/test_skyytrees_0.3.11.py --dir <tools/dev/scratch/<task>/...> (bare JVM)
EDITED-SCRIPTS RULE (commit ab75b6c): the lineage is Skyy's EDITED 0.2.3 -> trees_0_2_4_patch.py -> ... -> trees_0_3_10_patch.py -> the
generated 0.3.10 read here; tools/trees_0_2_3_patch.py and older are NEVER re-run. Edit THIS file, never the generated build script.

0.3.11 = REPLANT FELLED TREES (Skyy's fresh-profile test 2026-10-15, Hytale 0.7.2: "no saplings. i cant replant my trees. (there iss another mod
in my stuff that auto replants trees. maybe see if that works.)" - checked: Saplings From Trees is broken on 0.7 and Serilum's TreeHarvester in
the Mods folder crashes on 0.7, so we do it ourselves). SKYY'S PICK (popup 2026-10-15, docs/answered/gear.md: "Which starter quest/sapling
fixes? (... trees auto-replant on your island.)" -> "both for now. when protection works right, island only." = auto-replant AND a small
sapling-drop chance, EVERYWHERE for now; once SkyyZones protection works, both on player islands only - one Server Setup switch):
  - When a player fells a NATURAL tree, the matching vanilla sapling is planted on the stump spot a few seconds after the last log fell, and
    with trees.saplingDropPct (default 10 %) the player also gets one matching sapling (once per tree, storage > hotbar > backpack, dropped
    at the feet when full - the Replanter node's give). NO DUPLICATE TREE DETECTION: SkyySkills already tracks felled trees - its skill:on:felled bridge calls SkyyTrees'
    TreeFelledFn once per falling log (world thread; placed logs never fall, so only natural trees reach it); TreeReplant only collects those
    calls: one pending replant per player + world + tree (logs within 6 blocks of the first), its spot = the LOWEST felled log's column,
    the timer restarts with every new log of that tree (trees.replantDelaySec after the last one).
  - THE SPOT: one below the lowest felled log (= the cut base log, now air), going down at most 4 blocks through air to the first block:
    it must be soil (vanilla saplings need Support Down "Type=Soil": the Soil-tagged blocks of Assets.zip, built in) with air above - else
    nothing is planted (a mid-trunk cut leaves a log there = no sapling; a block someone put there = no sapling; an unloaded section = none).
    Placed with BlockOperations.setBlock (the engine's own /block set call, settings 0 = its block entity: the sapling's FarmingBlock grows
    it like a hand-planted one) on the WORLD THREAD (World.execute).
  - THE SAPLING: Wood_<W>_Trunk -> Plant_Sapling_<W> when the game has it, else the sapling whose grown tree (its last Farming stage prefab
    in Assets.zip) is made of that wood (Fir -> Plant_Sapling_Spruce); a wood with no sapling (Burnt ...) = nothing. Build-checked.
  - WHERE: trees.replantWhere = all (DEFAULT, Skyy "for now": every world where a natural tree can be felled - a protected world that
    refuses the break never fells a tree, and a cut that leaves the log = no spot) or island = own island only: SkyyIslands' island:role:fn
    (Object[]{UUID, world}) must say owner, admin, member (co-op) or trusted - a visitor, a banned player, a non-island world (the hub, zones,
    shard worlds - role null) or no SkyyIslands at all = never. The switch covers the replant AND the sapling drop.
  - NEEDS SkyySkills' felled-tree tracking: skill:on:felled only fires while SkyySkills "Felled logs roll tree nodes" (fell.nodes) is on
    and the log has an XP rule - said in the row's help.
  - SERVER SETUP -> Trees -> Abilities: "Replant felled trees" (trees.replant, default ON), "Replant delay" (trees.replantDelaySec, 1-60 s,
    default 5), "Replant + drops in" (trees.replantWhere, Everywhere / Own island only, default Everywhere) and "Sapling drop chance"
    (trees.saplingDropPct, 0-100 %, default 10) - live. A fresh trees.properties lists all four; an existing file has no line = the default
    (no migration, nothing written).
  - REVIEW FIX: a pending replant whose world hop never ran (the world closed in between) is dropped after its delay + 60 s, so the
    pending list (max 256) can never fill up and switch the replant off.
  - Build: Assets.zip is read from the CACHED copy (tools/serverjar.py); the optional pre-release icon cross-check runs only with
    SKYY_CHECK_PRE=1 (it opened an installed game file).
  ROLLBACK 0.3.11 -> 0.3.10: safe (the four lines are ignored; nothing else is written).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.3.10.py")
dst = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.3.11.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
CR, LF = chr(13), chr(10)
s = raw.decode("utf8").replace(CR + LF, LF)
assert 'VERSION = "0.3.10"' in s and "GENERATED by tools/trees_0_3_10_patch.py from the LIVE build_skyytrees_0.3.9.py" in s, \
    "build_skyytrees_0.3.10.py is not the live 0.3.10 of the edited lineage"
assert "TreeReplant" not in s, "0.3.10 already has the 0.3.11 parts"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
CHANGES = []
OLD = s


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.11 = REPLANT"):HEAD.index("  ROLLBACK 0.3.11")].rstrip()

# ================================================================================================================ header + version
rep('''"""SkyyTrees 0.3.10 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_3_10_patch.py from the LIVE build_skyytrees_0.3.9.py (the SET pin) - edit the patch, not this file. 0.3.9
was GENERATED''', '''"""SkyyTrees 0.3.11 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_3_11_patch.py from the LIVE build_skyytrees_0.3.10.py (the SET pin) - edit the patch, not this file. 0.3.10
was GENERATED by tools/trees_0_3_10_patch.py from the LIVE build_skyytrees_0.3.9.py. 0.3.9
was GENERATED''')
rep('''0.3.10 (2026-10-14; notes: tools/trees_0_3_10_patch.py) ''', '''0.3.11 (2026-10-15; notes: tools/trees_0_3_11_patch.py) ''' + NOTE[len("0.3.11 = "):].replace(LF, LF + "    ") + '''
  CHECKED: SkyyTrees/test_skyytrees_0.3.11.py (bare JVM: class compare vs 0.3.10, -Xverify:all, the replant path executed - grouping, the
    island role gate, the spot rules, the timer, the switch - every 0.3.10 section, the access audit, start twice).

=== SkyyTrees 0.3.10 notes (history; still true unless 0.3.11 above says otherwise) ===
0.3.10 (2026-10-14; notes: tools/trees_0_3_10_patch.py) ''', 1)
rep('''Run:   python build_skyytrees_0.3.10.py            -> SkyyTrees/SkyyTrees-0.3.10.jar
       python build_skyytrees_0.3.10.py --deploy   -> also''', '''Run:   python build_skyytrees_0.3.11.py            -> SkyyTrees/SkyyTrees-0.3.11.jar
       python build_skyytrees_0.3.11.py --deploy   -> also''')
rep('VERSION = "0.3.10"', 'VERSION = "0.3.11"')

# ================================================================================================================ Assets.zip: the cached copy
rep('''ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")''',
    '''sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import serverjar as _SJ                     # 0.3.11: the CACHED Assets.zip (tools/serverjar.py) - never the installed game file
ASSETS = _SJ.assets_zip()''')
rep('''if os.path.isfile(ASSETS_07):''', '''if os.environ.get("SKYY_CHECK_PRE") == "1" and os.path.isfile(ASSETS_07):     # 0.3.11: an installed game file - opt-in only''')

# ================================================================================================================ the replant tables (build time)
rep('''SAP_WOODS = [w for w in WOODS if "Plant_Sapling_" + w in ITEM_IDS]
''', '''SAP_WOODS = [w for w in WOODS if "Plant_Sapling_" + w in ITEM_IDS]
# 0.3.11 REPLANT: the wood family of a felled trunk -> the vanilla sapling that grows that tree (a sapling block with Farming stages). Name match
# first (Wood_Oak_Trunk -> Plant_Sapling_Oak), then the wood its grown tree is made of (its last stage prefab: Fir -> Plant_Sapling_Spruce).
# Valid ground = the blocks tagged Type=Soil (every vanilla sapling: Support Down TagId "Type=Soil").
import collections as _rcol
with zipfile.ZipFile(ASSETS) as z:
    _rn = z.namelist()
    _rsap = {}
    _rsoil = set()
    _rall = {}
    for _n in _rn:
        if not (_n.startswith("Server/Item/Items/") and _n.endswith(".json")):
            continue
        _b = os.path.basename(_n)[:-5]
        if not (_b.startswith("Plant_Sapling_") or _b.startswith("Soil_") or "Soil" in z.read(_n).decode("utf-8-sig", "replace")[:4000]):
            continue
        try:
            _j = json.loads(z.read(_n).decode("utf-8-sig"))
        except Exception:
            continue
        _bt = _j.get("BlockType") or {}
        if _b.startswith("Plant_Sapling_"):
            _rall[_b] = _j
        if _b.startswith("Plant_Sapling_") and "Farming" in _bt:
            _rsap[_b] = _bt
        if "Soil" in (((_j.get("Tags") or {}).get("Type")) or []) and _bt:
            _rsoil.add(_b)
    for _b in _rsap:          # every sapling needs soil below (its own Support, or its Parent's: most saplings inherit Plant_Sapling_Oak's)
        _c, _sp = _b, None
        while _c and _sp is None:
            _sp = (_rall.get(_c, {}).get("BlockType") or {}).get("Support")
            _c = _rall.get(_c, {}).get("Parent")
        assert _sp is not None and {"TagId": "Type=Soil"} in (_sp.get("Down") or []), "0.3.11: %s no longer needs soil below (%s)" % (_b, _sp)
    _rpref = [_n for _n in _rn if _n.startswith("Server/Prefabs/") and _n.endswith(".prefab.json")]
    REPL = dict((w, "Plant_Sapling_" + w) for w in WOODS if "Plant_Sapling_" + w in _rsap)
    for _sid in sorted(_rsap):
        _st = ((_rsap[_sid].get("Farming") or {}).get("Stages") or {}).get("Default") or []
        _ps = [p_["Path"] for s_ in _st for p_ in s_.get("Prefabs", [])]
        if not _ps:
            continue
        _c = [n_ for n_ in _rpref if n_.endswith("/" + _ps[-1])]
        if not _c:
            continue
        _fam = _rcol.Counter(re.findall(r'"Wood_([A-Za-z_]+?)_Trunk"', z.read(_c[0]).decode("utf-8-sig", "replace"))).most_common(1)
        if _fam and _fam[0][0] in WOODS and _fam[0][0] not in REPL:
            REPL[_fam[0][0]] = _sid
REPL_FAM = sorted(REPL)
REPL_SAP = [REPL[w] for w in REPL_FAM]
REPL_SOIL = sorted(_rsoil)
assert REPL.get("Oak") == "Plant_Sapling_Oak" and REPL.get("Birch") == "Plant_Sapling_Birch" and REPL.get("Fir") == "Plant_Sapling_Spruce", REPL
assert "Burnt" not in REPL and all(v in ITEM_IDS for v in REPL_SAP) and len(REPL_FAM) >= 25, REPL
assert "Soil_Grass" in REPL_SOIL and "Soil_Dirt" in REPL_SOIL and "Soil_Dirt_Tilled" in REPL_SOIL and "Rock_Stone" not in REPL_SOIL, REPL_SOIL[:20]
''')

# ================================================================================================================ the config (2 rows, default file)
rep('''DL.extend(["# Farming tree level = the average of Farming, Ranching and Orchard (SkyySkills skill:farmavg) - false = the Farming level (0.3.10)",
           "farming.average=true"])''', '''DL.extend(["# Farming tree level = the average of Farming, Ranching and Orchard (SkyySkills skill:farmavg) - false = the Farming level (0.3.10)",
           "farming.average=true"])
DL.extend(["# Replant (0.3.11): a felled natural tree gets its vanilla sapling on the stump, this many seconds after the last log (needs SkyySkills fell.nodes)",
           "trees.replant=true",
           "trees.replantDelaySec=5",
           "# Where the replant and the sapling drop work: all = everywhere (Skyy: for now), island = the player's own island only",
           "trees.replantWhere=all",
           "# Chance (percent, once per felled natural tree) to also get one matching sapling",
           "trees.saplingDropPct=10"])''')
rep('''             "boolean FARM_AVG = true", "boolean HAS310 = true",   # 0.3.10: farming.average; the file holds Spellblade class lines''',
    '''             "boolean FARM_AVG = true", "boolean HAS310 = true",   # 0.3.10: farming.average; the file holds Spellblade class lines
             "boolean REPLANT = true", "long REPLANT_MS = 5000L",   # 0.3.11: trees.replant, trees.replantDelaySec
             "boolean REPLANT_ISLAND = false", "int SAP_DROP_PCT = 10",   # 0.3.11: trees.replantWhere (island = true), trees.saplingDropPct''')
rep('''  FARM_AVG = bool(p, "farming.average", true);   // 0.3.10: the Farming tree's level = skill:farmavg (the three farming skills' average)''',
    '''  FARM_AVG = bool(p, "farming.average", true);   // 0.3.10: the Farming tree's level = skill:farmavg (the three farming skills' average)
  REPLANT = bool(p, "trees.replant", true);                                          // 0.3.11
  REPLANT_MS = clampL(lng(p, "trees.replantDelaySec", 5L), 1L, 60L) * 1000L;
  REPLANT_ISLAND = str(p, "trees.replantWhere", "all").equalsIgnoreCase("island");   // all (default) / island
  SAP_DROP_PCT = (int) clampL(lng(p, "trees.saplingDropPct", 10L), 0L, 100L);''')
RP_HELP = "ON: a felled natural tree gets its sapling on the stump. Needs SkyySkills felled-log tree nodes on."
RD_HELP = "Seconds after the last log of a felled tree falls before its sapling is planted."
RW_HELP = "Where replant + sapling drops work. Everywhere for now; own island once protection works (Skyy)."
SD_HELP = "Chance per felled natural tree to also get one matching sapling. 0 = off."
assert len(RP_HELP) <= 100 and len(RD_HELP) <= 100 and len(RW_HELP) <= 100 and len(SD_HELP) <= 100
rep('''    ("felled.nodes", "Felled logs roll bonuses", "abilities", "bool", "true", "", "", "", "", "live",
     "Logs of a felled tree roll Sap Tapper, Replanter and Pocket Change (SkyySkills 0.4.2).", "reload"),''',
    '''    ("felled.nodes", "Felled logs roll bonuses", "abilities", "bool", "true", "", "", "", "", "live",
     "Logs of a felled tree roll Sap Tapper, Replanter and Pocket Change (SkyySkills 0.4.2).", "reload"),
    # 0.3.11 (Skyy 2026-10-15 "no saplings. i cant replant my trees." + popup "both for now. when protection works right, island only.")
    ("trees.replant", "Replant felled trees", "abilities", "bool", "true", "", "", "", "", "live", "%s", "reload"),
    ("trees.replantDelaySec", "Replant delay", "abilities", "int", "5", "1", "60", "", "s", "live", "%s", "reload"),
    ("trees.replantWhere", "Replant + drops in", "abilities", "choice", "all", "", "", "all|Everywhere,island|Own island only", "", "live", "%s", "reload"),
    ("trees.saplingDropPct", "Sapling drop chance", "abilities", "int", "10", "0", "100", "", "%%", "live", "%s", "reload"),''' % (RP_HELP, RD_HELP, RW_HELP, SD_HELP))
rep('''assert len(_exact) == 20 + EXTRA_EXACT_ROWS and len(CFG_ROWS) == 21 + len(TREES) + EXTRA_EXACT_ROWS + EXTRA_TABLE_ROWS and len(CFG_ROWS) == 46   # 0.3.3: + Assassin, Monk; 0.3.10: + farming.average, nodes.Fishing, class.nodes.Spellblade
assert [r[0] for r in CFG_ROWS].count("class.enabled") == 1 and len(set(r[0] for r in CFG_ROWS)) == 46''',
    '''assert len(_exact) == 24 + EXTRA_EXACT_ROWS and len(CFG_ROWS) == 25 + len(TREES) + EXTRA_EXACT_ROWS + EXTRA_TABLE_ROWS and len(CFG_ROWS) == 50   # 0.3.3: + Assassin, Monk; 0.3.10: + farming.average, nodes.Fishing, class.nodes.Spellblade; 0.3.11: + trees.replant, trees.replantDelaySec, trees.replantWhere, trees.saplingDropPct
assert [r[0] for r in CFG_ROWS].count("class.enabled") == 1 and len(set(r[0] for r in CFG_ROWS)) == 50''')

# ================================================================================================================ engine names
rep('''    "BHU": "com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils",''',
    '''    "BHU": "com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils",
    "BOP": "com.hypixel.hytale.server.core.universe.world.chunk.BlockOperations",     # 0.3.11: the replant (/block set's call)''')
rep('''    B.probe(pool, T.get(c, c), m)
''', '''    B.probe(pool, T.get(c, c), m)
for c, m in (("BOP", "setBlock"), ("WLD", "execute")):      # 0.3.11: the replant
    B.probe(pool, T[c], m)
''')

# ================================================================================================================ the classes
rep('''ffn = pool.makeClass(PKG + ".TreeFelledFn")
''', '''ffn = pool.makeClass(PKG + ".TreeFelledFn")
rpt = pool.makeClass(PKG + ".TreeReplantTask")   # 0.3.11: one pending replant (a felled tree) - its timer (Runnable) and the world-thread plant
rpl = pool.makeClass(PKG + ".TreeReplant")       # 0.3.11: the replant rules (sapling, spot, own island) + the pending list
''')
rep('''ALL = (defs, cfg, dat, sto, stk, calc, cls, fx, swg, msg, abil, gat, tfn, afn, bfn, ffn, dmg,''',
    '''ALL = (defs, cfg, dat, sto, stk, calc, cls, fx, swg, msg, abil, gat, tfn, afn, bfn, ffn, rpt, rpl, dmg,''')

RP_JAVA = r'''
# ================= 0.3.11 REPLANT (Skyy 2026-10-15: "no saplings. i cant replant my trees."). SkyySkills' felled-tree tracking calls
# TreeFelledFn once per falling log of a NATURAL tree (world thread); TreeReplant only collects those calls into one pending replant per
# player + world + tree, and TreeReplantTask plants the sapling trees.replantDelaySec after the last log - on the world thread.
rpt.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public @WLD@ w;", "public String wn;", "public java.util.UUID u;", "public int x;", "public int y;", "public int z;",
           "public String sap;", "public volatile long last;", "public volatile int stage;", "public int logs;"):
    F(rpt, _f)
C(rpt, "public TreeReplantTask(@WLD@ w, String wn, java.util.UUID u, int x, int y, int z, String sap) { this.w = w; this.wn = wn; this.u = u; this.x = x; this.y = y; this.z = z; this.sap = sap; this.last = System.currentTimeMillis(); this.logs = 1; }")
# another log of this tree: the spot follows the LOWEST log; the timer restarts
M(rpt, r"""
public synchronized void add(int x, int y, int z) {
  if (y < this.y) { this.x = x; this.y = y; this.z = z; }
  this.logs = this.logs + 1;
  this.last = System.currentTimeMillis();
}""")
M(rpt, r"""
public synchronized boolean near(String wn, java.util.UUID u, int x, int z) {
  return this.stage == 0 && this.wn.equals(wn) && this.u.equals(u) && Math.abs(x - this.x) <= 6 && Math.abs(z - this.z) <= 6;
}""")
F(rpl, "public static final String[] FAM = %s;" % jstr(REPL_FAM))       # wood family (Wood_<W>_Trunk) ...
F(rpl, "public static final String[] SAP = %s;" % jstr(REPL_SAP))       # ... -> its vanilla sapling
F(rpl, "public static final String[] SOIL = %s;" % jstr(REPL_SOIL))     # sorted: blocks tagged Type=Soil (a sapling's Support Down)
F(rpl, "public static final java.util.ArrayList PEND = new java.util.ArrayList();")
F(rpl, "public static volatile java.util.Map TEST_BLOCKS = null;")     # harness only: "x|y|z" -> block id instead of a world (null in the game)
F(rpl, "public static volatile long PLANTED = 0L;")
F(rpl, "public static boolean FAILED_ONCE = false;")
M(rpl, r"""
public static String sapOf(String id) {
  if (id == null || !id.startsWith("Wood_")) return null;
  int b = id.indexOf("_Trunk");
  if (b <= 5) return null;
  String f = id.substring(5, b);
  for (int i = 0; i < FAM.length; i++) if (FAM[i].equals(f)) return SAP[i];
  return null;
}""")
M(rpl, r"""
public static boolean isSoil(String id) {
  return id != null && java.util.Arrays.binarySearch(SOIL, id) >= 0;
}""")
M(rpl, r"""
public static boolean isAir(String id) {
  return id != null && (id.length() == 0 || id.equals("Empty"));
}""")
M(rpl, r"""
public static synchronized @PKG@.TreeReplantTask find(String wn, java.util.UUID u, int x, int z) {
  for (int i = 0; i < PEND.size(); i++) {
    @PKG@.TreeReplantTask g = (@PKG@.TreeReplantTask) PEND.get(i);
    if (g.near(wn, u, x, z)) return g;
  }
  return null;
}""")
M(rpl, r"""
public static synchronized boolean keep(@PKG@.TreeReplantTask g) {
  long old = System.currentTimeMillis() - @PKG@.TreeCfg.REPLANT_MS - 60000L;   // REVIEW FIX: a replant whose world hop never ran (world closed)
  for (int i = PEND.size() - 1; i >= 0; i--) {
    @PKG@.TreeReplantTask o = (@PKG@.TreeReplantTask) PEND.get(i);
    if (o.last < old) PEND.remove(i);
  }
  if (PEND.size() >= 256) return false;
  PEND.add(g);
  return true;
}""")
M(rpl, r"""
public static synchronized void drop(@PKG@.TreeReplantTask g) {
  PEND.remove(g);
}""")
M(rpl, r"""
public static synchronized int pending() {
  return PEND.size();
}""")
M(rpl, r"""
public static void failed(Throwable t) {
  if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TreeCfg.warn("replant failed (logged once): " + t); }
}""")
# WHERE (trees.replantWhere): all = everywhere (Skyy "for now"); island = OWN ISLAND: SkyyIslands' island:role:fn says owner / admin /
# member (co-op) / trusted; visitor, banned, null (not an island world) or no SkyyIslands = never
M(rpl, r"""
public static boolean allowed(java.util.UUID u, String wn) {
  if (!@PKG@.TreeCfg.REPLANT_ISLAND) return true;
  try {
    Object f = @PKG@.TreeStore.bridge().get("island:role:fn");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, wn });
    if (!(r instanceof String)) return false;
    String s = (String) r;
    return s.equals("owner") || s.equals("admin") || s.equals("member") || s.equals("trusted");
  } catch (Throwable t) { return false; }
}""")
M(rpl, r"""
public static String blockAt(@WLD@ w, int x, int y, int z) {
  java.util.Map tb = TEST_BLOCKS;
  if (tb != null) { Object o = tb.get(x + "|" + y + "|" + z); return o == null ? "" : o.toString(); }
  if (w == null) return null;
  return @PKG@.TreeAbil.blockIdAt(w, x, y, z);
}""")
# BlockSetCommand's call: the asset index, the BlockType, rotation 0, filler 0, settings 0 (= heightmap, light, block entity: the sapling's
# FarmingBlock, physics); a section that is not loaded = nothing
M(rpl, r"""
public static boolean place(@WLD@ w, int x, int y, int z, String id) {
  java.util.Map tb = TEST_BLOCKS;
  if (tb != null) { tb.put(x + "|" + y + "|" + z, id); return true; }
  if (w == null || id == null) return false;
  @CHS@ cs = w.getChunkStore();
  if (cs == null) return false;
  @REF@ r = cs.getChunkSectionReferenceAtBlock(x, y, z);
  if (r == null || !r.isValid()) return false;
  int idx = @BTY@.getAssetMap().getIndex(id);
  @BTY@ t = (@BTY@) @BTY@.getAssetMap().getAsset(idx);
  if (t == null || !id.equals(@PKG@.TreeDefs.bid(t))) return false;
  return @BOP@.setBlock(cs, r, x, y, z, idx, t, 0, 0, 0);
}""")
# THE SPOT: one below the lowest felled log, down through air (at most 4 blocks) to the first block: soil with air above = plant there
M(rpl, r"""
public static boolean plant(@PKG@.TreeReplantTask g) {
  if (!@PKG@.TreeCfg.REPLANT || g == null) return false;
  for (int k = 0; k < 4; k++) {
    int y = g.y - 1 - k;
    String b = blockAt(g.w, g.x, y, g.z);
    if (b == null) return false;
    if (isAir(b)) continue;
    if (!isSoil(b)) return false;
    String up = blockAt(g.w, g.x, y + 1, g.z);
    if (!isAir(up)) return false;
    if (!place(g.w, g.x, y + 1, g.z, g.sap)) return false;
    PLANTED = PLANTED + 1L;
    @PKG@.TreeCfg.info("replanted " + g.sap + " at " + g.x + " " + (y + 1) + " " + g.z + " in " + g.wn + " (" + g.logs + " felled logs, " + g.u + ")");
    return true;
  }
  return false;
}""")
M(rpl, r"""
public static void plantNow(@PKG@.TreeReplantTask g) {
  drop(g);
  try { plant(g); } catch (Throwable t) { failed(t); }
}""")
M(rpl, r"""
public static void schedule(@PKG@.TreeReplantTask g, long ms) {
  java.util.concurrent.CompletableFuture.delayedExecutor(ms < 1L ? 1L : ms, java.util.concurrent.TimeUnit.MILLISECONDS).execute(g);
}""")
# one felled log (world name, player, block id, position): 0 = ignored, 1 = a new pending replant, 2 = added to this tree's one, 3 = a new
# pending replant AND its sapling drop won (once per tree: trees.saplingDropPct; the caller gives the sapling on the world thread)
M(rpl, r"""
public static int note2(@WLD@ w, String wn, java.util.UUID u, String id, int x, int y, int z) {
  if ((!@PKG@.TreeCfg.REPLANT && @PKG@.TreeCfg.SAP_DROP_PCT <= 0) || wn == null || u == null) return 0;
  String sap = sapOf(id);
  if (sap == null) return 0;
  @PKG@.TreeReplantTask g = find(wn, u, x, z);
  if (g != null) { g.add(x, y, z); return 2; }
  if (!allowed(u, wn)) return 0;
  g = new @PKG@.TreeReplantTask(w, wn, u, x, y, z, sap);
  if (!keep(g)) return 0;
  schedule(g, @PKG@.TreeCfg.REPLANT_MS);
  return @PKG@.TreeGather.roll((double) @PKG@.TreeCfg.SAP_DROP_PCT / 100.0) ? 3 : 1;
}""")
M(rpl, r"""
public static void note(@PR@ pr, @BTY@ bt, String wn, int x, int y, int z) {
  try {
    if ((!@PKG@.TreeCfg.REPLANT && @PKG@.TreeCfg.SAP_DROP_PCT <= 0) || pr == null || bt == null || wn == null) return;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid() || !r.getStore().isInThread()) return;
    @WLD@ w = @PKG@.TreeAbil.worldOf(pr, wn);
    if (w == null) return;
    String id = @PKG@.TreeDefs.bid(bt);
    int res = note2(w, wn, pr.getUuid(), id, x, y, z);
    if (res == 3 && !@PKG@.TreeStore.busy(pr.getUuid())) @PKG@.TreeGather.giveItem(pr, wn, sapOf(id));   // the sapling drop (world thread)
  } catch (Throwable t) { failed(t); }
}""")
# the timer (stage 0, any thread): not quiet yet -> wait the rest; quiet -> hop to the world thread (stage 1) and plant there
M(rpt, r"""
public void run() {
  try {
    if (this.stage == 0) {
      long wait = this.last + @PKG@.TreeCfg.REPLANT_MS - System.currentTimeMillis();
      if (wait > 20L) { @PKG@.TreeReplant.schedule(this, wait); return; }
      this.stage = 1;
      if (@PKG@.TreeReplant.TEST_BLOCKS != null || this.w == null) { @PKG@.TreeReplant.plantNow(this); return; }
      this.w.execute(this);
      return;
    }
    @PKG@.TreeReplant.plantNow(this);
  } catch (Throwable t) { @PKG@.TreeReplant.drop(this); @PKG@.TreeReplant.failed(t); }
}""")

'''
rep('''# 0.2.1: SkyySkills 0.4.2 calls this once per credited felled position, world thread:
''', RP_JAVA + '''# 0.2.1: SkyySkills 0.4.2 calls this once per credited felled position, world thread:
''')
rep('''    @PKG@.TreeGather.felled(pr, ((Number) a[1]).intValue(), bt, wn, ((Number) a[4]).intValue(), ((Number) a[5]).intValue(), ((Number) a[6]).intValue());''',
    '''    @PKG@.TreeReplant.note(pr, bt, wn, ((Number) a[4]).intValue(), ((Number) a[5]).intValue(), ((Number) a[6]).intValue());   // 0.3.11: the replant (own island)
    @PKG@.TreeGather.felled(pr, ((Number) a[1]).intValue(), bt, wn, ((Number) a[4]).intValue(), ((Number) a[5]).intValue(), ((Number) a[6]).intValue());''')

# ================================================================================================================ checks on the result
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "no system / command added"
_i = s.index
assert _i('rpt = pool.makeClass(PKG + ".TreeReplantTask")') < _i("public static String blockIdAt(@WLD@ w") < _i("public static boolean plant(@PKG@.TreeReplantTask g)") \
    < _i("public static int note2(") < _i("public static void note(@PR@ pr") < _i("public void run() {\n  try {\n    if (this.stage == 0)") < _i("public TreeFelledFn() { }")
assert _i("public static @WLD@ worldOf(@PR@ pr, String wn)") < _i("public static void note(@PR@ pr")
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.10 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8") if NL != LF else s.encode("utf8"))
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.10 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
