"""Derive SkyyTrees/build_skyytrees_0.2.1.py from build_skyytrees_0.2.py (the trees_0_2_patch.py style: rep(old, new) with asserted single
anchors, newline-agnostic; 0.2 stays untouched and its CRLF/LF line endings are kept). Edit THIS file, not the generated script.
0.2.1 = the SkyyTrees parts of two specs (HANDOFF feedback round 2; SkyyTrees 0.2 is the LIVE jar since 2026-09-24 19:55):
 - research/Tree-Fall-Spec.md 3.3: TREE FELLER REWORK. Same-Y logs only (flatFlood: breadth-first over the 8 horizontal neighbours,
   the 4 sides before the 4 diagonals, so the nearest logs go first), levels 1/2/3/4 = 1/2/3/4 more logs, the max level = every log
   of that tree on that layer (feller.maxPerLayer, default 64). No vertical reach at all; feller.maxHeight is now only how far up /
   down the read-only leaves check looks. Default cooldown 5 s (was 30). One-time trees.properties migration: the unchanged 0.1/0.2
   default lines Foraging.FFeller.per=8.0 / base=8.0 / feller.cooldownSec=30 become 1.0 / 0.0 / 5 in place (custom values kept +
   a server-log warning), feller.maxPerLayer + felled.nodes are appended once.
   Felled-log node rolls: "trees" is registered in skill:on:felled (SkyySkills 0.4.2 calls it once per credited felled position):
   Sap Tapper, Replanter and Pocket Change roll on felled trunks; Spread / Vein Burst / Tree Feller never run from it.
 - research/Double-Jump-Spec.md 3.1: DOUBLE JUMP (RDouble, kind DJUMP) replaces Quick Dodge (RDodge) in Acrobatics tier II slot 5
   (same slot = same Token / Dust cost). skill:bonus:<uuid>["trees"] "doublejump.acrobatics" = base 0.5 + 0.05 x level (55% .. 100% of
   the player's jump height); dodge.acrobatics = Evasion only. Old player files: Acrobatics.RDodge=<n> loads as RDouble level n
   (only when there is no Acrobatics.RDouble line) and "RDodge" in Acrobatics.off turns RDouble off; the next save writes RDouble.
   Build asserts: RDodge + RDodge2 = 0.2 -> RDodge2 = 0.1; Evasion's text no longer says "adds to Quick Dodge". The card's %K =
   bridge skill:dj:key (SkyySkills 0.4.2) or "crouch".
Run:  python tools/trees_0_2_1_patch.py   then   python SkyyTrees/build_skyytrees_0.2.1.py   (NO --deploy: coordinated deploy)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.2.py")
dst = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.2.1.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2"
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


# ================================================================ header / version
rep('''"""SkyyTrees 0.2 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
DERIVED from build_skyytrees_0.1.py by tools/trees_0_2_patch.py - edit the patch, not this file (0.1 stays untouched).
''', '''"""SkyyTrees 0.2.1 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
DERIVED from build_skyytrees_0.2.py by tools/trees_0_2_1_patch.py - edit the patch, not this file (0.2 stays untouched; 0.2 was
derived from 0.1 by tools/trees_0_2_patch.py).
0.2.1 = HANDOFF feedback round 2, the SkyyTrees parts of research/Tree-Fall-Spec.md (3.3) and research/Double-Jump-Spec.md (3.1).
  TREE FELLER REWORK (Skyy 2026-09-24: "Hytale already fells a tree when its whole base is broken, so Tree Feller breaks extra logs
    HORIZONTALLY on the broken block's Y level ... No vertical reach"):
    - TreeAbil.flatFlood: breadth-first search on the cut's Y level only, over the 8 horizontal neighbours in the order (1,0) (-1,0)
      (0,1) (0,-1) then the 4 diagonals, so the logs nearest the cut go first (level 1 = the log right beside it); |dx|, |dz| <=
      ability.maxRadius; ids starting with the cut's Wood_<W>_Trunk family (Trunk and Trunk_Full); never a placed log (skill:fn:placed)
      or one an ability broke in the last 5 s; at most 4000 reads. NOTHING above or below the cut level is ever broken.
    - Level curve (Foraging.FFeller: per 1.0, base 0.0, max 5): levels 1, 2, 3, 4 = 1, 2, 3, 4 more logs; the MAX level = every log of
      that tree on that level, up to feller.maxPerLayer (default 64, clamp 1-256) = TreeCfg.FELLER_ALL (TreeFx.value returns it at
      max, so tree:fn:bonus answers it too). A 2x2 tree needs level 3, a 3x3 needs the max level. The page says "Breaks 1 more log
      beside it on the same level" ... "Breaks every log of that tree on the same level (up to 64)".
    - Natural-tree check unchanged in spirit: with feller.needLeaves the old 26-neighbour flood runs READ-ONLY (max 0) from the cut
      up to feller.maxHeight up / down and only reports whether a Plant_Leaves_ block touches that wood (a partial cut of a thick tree
      fells nothing, so the tree is still whole). An empty layer or no leaves = no break and no cooldown (Timber Spread may still roll).
    - Every Feller log still breaks through BlockHarvestUtils.performBlockBreak = a real BreakBlockEvent each (island protection,
      SkyySkills XP + double drops, Collections). Once the whole layer is gone the engine fells the tree; SkyySkills 0.4.2 pays those
      logs as felled (its LAYER list reuses the first watch), so no log is ever both Feller-broken and felled.
    - feller.cooldownSec default 5 (was 30); chat "Tree Feller! +3 logs on this level (ready again in 5 s)".
    - trees.properties migration, ONCE (a file without feller.maxPerLayer): the unchanged old default lines Foraging.FFeller.per=8.0,
      Foraging.FFeller.base=8.0 and feller.cooldownSec=30 are rewritten in place to 1.0 / 0.0 / 5 (exact key and value text, comments
      untouched, bytes read and written as ISO-8859-1 = the java.util.Properties file encoding, so nothing else in the file changes);
      then the 0.2.1 block (feller.maxPerLayer=64, felled.nodes=true, comments) is appended. Custom per / base values are KEPT and the
      server log warns that they now count logs on one level. The whole new content is written through TreeCfg.writeAtomic and the
      in-memory settings are parsed from exactly that content (a failed write still runs with the migrated values; the next load
      retries). A 0.1 file gets the 0.2 block (now with Double Jump) + the migration in the same single write.
  FELLED-LOG NODE ROLLS (Tree-Fall-Spec 3.3): TreeFelledFn is registered as "trees" in the bridge map skill:on:felled (putIfAbsent,
    re-checked every 5 s like skill:on:gather, removed in shutdown). SkyySkills 0.4.2 calls it on the world thread once per credited
    felled position: Object[]{PlayerRef, Integer row, BlockType, String world, Integer x, Integer y, Integer z, String pkey}. On a
    Foraging (row 1) _Trunk it rolls Sap Tapper, Replanter and Pocket Change exactly like TreeGather.run; NEVER Spread / Vein /
    Feller (no chains). Skipped while profile:busy:<uuid> is set, when pkey is not the player's active profile any more, or with
    felled.nodes=false. Without SkyySkills 0.4.2 the map is simply never called.
  DOUBLE JUMP (Double-Jump-Spec 3.1, Skyy 2026-09-24 "add a double jump node to the acrobatics tree"):
    - KINDS += DJUMP (22; every older kind number unchanged). Acrobatics S5 (tier II, Acrobatics 10) is now RDouble "Double Jump"
      (icon Plant_Fruit_Windwillow, max 10, base 0.5, per 0.05): value = base + per x level = 55% at level 1 .. 100% at level 10 of
      the player's own jump height. It replaces Quick Dodge (RDodge): same slot, so the same unlock token and the same Dust per level.
    - skill:bonus:<uuid>["trees"]: "doublejump.acrobatics" = that fraction (absent = no node / off); "dodge.acrobatics" = Evasion
      (RDodge2) only. SkyySkills 0.4.2 reads doublejump.acrobatics (crouch in mid-air, Stamina, landing reset - all SkyySkills side).
    - Card HOW "Press %K in mid-air ...": %K = bridge skill:dj:key (SkyySkills 0.4.2: "crouch" / "jump" / "jump or crouch"), else
      "crouch". Evasion's NOW text is "+%V dodge push" (Quick Dodge no longer exists).
    - OLD SAVES (0.2 is live, so Acrobatics.RDodge lines exist): TreeStore.readFile loads Acrobatics.RDodge=<n> as RDouble level n
      when the file has no Acrobatics.RDouble line (an RDouble line always wins), and "RDodge" in Acrobatics.off turns RDouble off.
      Tokens and Dust are computed from levels (never stored), so the balance is exactly what 0.2 showed. snap() writes current ids,
      so the next save has Acrobatics.RDouble=<n> and no RDodge line; an untouched file is aliased again on every load (harmless).
      Acrobatics.RDodge2 (Evasion) is a different id and is never aliased.
    - trees.properties: a file 0.2 wrote (0.2 keys, no Acrobatics.RDouble.* key) gets the RDouble node lines appended once, with a
      comment that the old Acrobatics.RDodge.* lines are unused (an admin's Quick Dodge numbers do NOT carry over; logged once).
  CHECKED at build time in a bare JVM (the session's scratch harness under tools/dev/scratch, deleted afterwards; see the build
    report): the trees.properties upgrade of a real 0.1 and a real 0.2 default file (read from those jars) and of a customised file,
    idempotence on a second load, the RDodge -> RDouble save alias (spec 3.1 point 6 cases a-d incl. the same Tokens / Dust as 0.2),
    the Feller values 1/2/3/4/64, Double Jump 0.55 / 1.0 and the bonus map.
  UNVERIFIED (needs Skyy's in-game test): flatFlood / the same-Y breaks in a real world (Tree-Fall-Spec T7), the felled rolls
    (needs SkyySkills 0.4.2, T3), the Double Jump itself (SkyySkills 0.4.2, Double-Jump-Spec section 5).
  REVIEW FIXES (same version, before any deploy):
    - Log family = the natural shapes only: TreeDefs.isLog(id, fam) = Wood_<W>_Trunk or Wood_<W>_Trunk_Full, plus their block
      states (a Stripped trunk "*Wood_Oak_Trunk_State_Stripped"). Trunk_Half, Trunk_Stairs and the *_Deco shapes never match any more
      (0.1 / 0.2 matched every id starting with Wood_<W>_Trunk). Assets.zip, checked 2026-09-24: none of the 1126 tree prefabs
      (Server/Prefabs/Trees) uses a Half / Stairs / Deco trunk, only Trunk + Trunk_Full, so natural trees lose nothing. Used by
      flatFlood, the read-only leaves check (TreeAbil.matches, prefix mode) and the cut itself (a Half / Stairs cut never fires Feller).
    - TreeGather.felled: never rolls on a position a SkyyTrees ability broke in the last 5 s (TreeAbil.recent; run() already rolled
      for it through its real BreakBlockEvent), whatever SkyySkills reports. Off the world thread (Store.isInThread false) it does
      nothing and warns once (SkyySkills 0.4.2 documents FellCredit.one on the world thread; the guard keeps inventory writes safe).
    - TreeDefs.valueText: explicit DJUMP case (percent), no behaviour change.
    - Detail panel: SkyyTrDetHow 52 -> 72 px high (the Tree Feller and Double Jump HOW texts are ~130 characters, the longest in 0.2
      was 100; 72 px holds 4 lines at FontSize 11 in the 310 px column). The panel column still has ~98 px spare below the buttons.
  SKYY SIGN-OFF NEEDED BEFORE DEPLOY (open in HANDOFF section 4 and the specs' section 6; this build uses the specs' recommendations):
    - Double-Jump-Spec 6.1: tier II slot 5 (built: replaces Quick Dodge) or tier III slot 7 (would replace Sprinter). The save alias is
      lossless - RDouble level n = the old RDodge level n in the SAME slot, so the same Token / Dust - and a tier-III rebuild can alias
      RDouble back to RDodge the same way. 6.2 / 6.3 (boots, numbers) are SkyySkills / trees.properties values.
    - Tree-Fall-Spec 6.3: Tree Feller curve 1 / 2 / 3 / 4 / whole layer and the 5 s cooldown. Plain trees.properties values
      (Foraging.FFeller.per / base, feller.cooldownSec, feller.maxPerLayer): retuning needs no new migration.

=== SkyyTrees 0.2 notes (history; still true unless 0.2.1 above says otherwise) ===
''')
rep('''Run:   python build_skyytrees_0.2.py            -> SkyyTrees/SkyyTrees-0.2.jar
       python build_skyytrees_0.2.py --deploy   -> also Mods/SkyyTrees.jar + enabled in the HUD mod world (only with Skyy's OK)''',
    '''Run:   python build_skyytrees_0.2.1.py            -> SkyyTrees/SkyyTrees-0.2.1.jar
       python build_skyytrees_0.2.1.py --deploy   -> also Mods/SkyyTrees.jar + enabled in the HUD mod world (only with Skyy's OK)''')
rep('VERSION = "0.2"', 'VERSION = "0.2.1"')

# ================================================================ kinds, texts, node rows
# ================================================================ review fix: log family = natural trunk shapes only (+ block states)
after('''# Wood_Oak_Trunk_Full -> "Wood_Oak_Trunk" (Tree Feller family)
M(defs, r"""
public static String logFamily(String id) {
  if (id == null) return null;
  int t = id.indexOf("_Trunk");
  return t > 0 ? id.substring(0, t + 6) : null;
}""")
''', '''# 0.2.1 review: a block of the Tree Feller family fam (logFamily) = ONLY the natural shapes Wood_<W>_Trunk / Wood_<W>_Trunk_Full, with
# or without a block state ("*Wood_Oak_Trunk_State_Stripped"); never Trunk_Half / Trunk_Stairs / *_Deco (crafted building shapes - no
# tree prefab in Assets.zip uses them: 1126 Server/Prefabs/Trees files hold only Trunk + Trunk_Full, checked 2026-09-24)
M(defs, r"""
public static boolean isLog(String id, String fam) {
  if (id == null || fam == null || id.length() == 0 || fam.length() == 0) return false;
  String b = id.startsWith("*") ? id.substring(1) : id;
  int s = b.indexOf("_State_");
  if (s > 0) b = b.substring(0, s);
  return b.equals(fam) || b.equals(fam + "_Full");
}""")
''')
rep('''public static boolean matches(String id, String match, boolean prefix) {
  if (id == null || id.length() == 0 || match == null) return false;
  return prefix ? id.startsWith(match) : id.equals(match);''', '''public static boolean matches(String id, String match, boolean prefix) {
  if (id == null || id.length() == 0 || match == null) return false;
  return prefix ? @PKG@.TreeDefs.isLog(id, match) : id.equals(match);''')
rep('''  String fam = @PKG@.TreeDefs.logFamily(id);
  if (fam == null) return false;''', '''  String fam = @PKG@.TreeDefs.logFamily(id);
  if (fam == null || !@PKG@.TreeDefs.isLog(id, fam)) return false;''')
rep('''  if (k == @K_VEIN@ || k == @K_FELLER@) return String.valueOf(Math.round(v));''', '''  if (k == @K_VEIN@ || k == @K_FELLER@) return String.valueOf(Math.round(v));
  if (k == @K_DJUMP@) return pct(v);''')
rep('''("ST", "getExternalData")''', '''("ST", "getExternalData"), ("ST", "isInThread")''')

rep('''assert KINDS.index("MASTER") == 14 and KINDS.index("SOON") == 21''',
    '''assert KINDS.index("MASTER") == 14 and KINDS.index("SOON") == 21
KINDS += ["DJUMP"]   # 0.2.1 Double Jump (research/Double-Jump-Spec.md 3.1; existing kind numbers unchanged)
assert KINDS.index("DJUMP") == 22''')
after('''SOONHOW = "Draft slot - nothing here yet and it cannot be unlocked"
''', '''# 0.2.1 Double Jump (research/Double-Jump-Spec.md 2.2): %K = the trigger key SkyySkills 0.4.2 publishes as skill:dj:key (else "crouch")
DJ_ICON = "Plant_Fruit_Windwillow" if "Plant_Fruit_Windwillow" in ITEM_IDS else must("Ingredient_Feathers_Light")
ADJ = "Press %K in mid-air - once per jump - resets when you land - costs Stamina - no Acrobatics XP - needs SkyySkills 0.4.2"
''')
# Tree Feller rework (Tree-Fall-Spec 3.3): per 1.0 / base 0.0 = 1, 2, 3, 4 logs, the max level = the whole layer (TreeFx.value)
rep('''  ("FFeller", "Tree Feller", "Tool_Hatchet_Adamantite", "FELLER", 5, 8.0, 8.0, "Fells up to %V connected logs of a natural tree", "On a log that pays Foraging XP - the tree must touch leaves - cooldown %C s", "", ""),''',
    '''  ("FFeller", "Tree Feller", "Tool_Hatchet_Adamantite", "FELLER", 5, 1.0, 0.0, "Breaks %V more logs beside it on the same level", "On a log that pays Foraging XP - same Y level only (Hytale fells the tree once that layer is cut) - natural trees - cooldown %C s", "", ""),''')
# Double Jump replaces Quick Dodge (Double-Jump-Spec 2.1 / 2.2): same slot 5 (tier II, max 10, B 150, 1 token)
rep('''  ("RDodge", "Quick Dodge", "Ingredient_Feathers_Blue", "RDODGE", 10, 0.01, 0, "+%V dodge push", ADODGE, "", ""),''',
    '''  ("RDouble", "Double Jump", DJ_ICON, "DJUMP", 10, 0.05, 0.5, "Jump once more in mid-air at %V of your jump height", ADJ, "", ""),''')
rep('''"+%V dodge push - adds to Quick Dodge", ADODGE''', '''"+%V dodge push", ADODGE''')
rep('''assert _tot(("RDodge", "RDodge2")) == 0.2 and''', '''assert _tot(("RDodge2",)) == 0.1 and''')
after('''assert _tot(("ELuck",)) == 0.1 and _tot(("EScav",)) == 0.15
''', '''# 0.2.1: Double Jump sits exactly where Quick Dodge sat (same index, same Token / Dust cost), 55% at level 1, 100% at level 10
_RD = [r for r in ROWS if r["id"] == "RDouble"]
assert len(_RD) == 1 and not [r for r in ROWS if r["id"] == "RDodge"]
_RD = _RD[0]
assert TREES[_RD["t"]] == "Acrobatics" and _RD["s"] == 5 and _RD["tier"] == 2 and _RD["max"] == 10 and _RD["B"] == 150 and _RD["tok"] == 1
assert abs(_RD["base"] + _RD["per"] * 1 - 0.55) < 1e-9 and abs(_RD["base"] + _RD["per"] * 10 - 1.0) < 1e-9 and T["I_RDOUBLE"] == "52"
_FF = [r for r in ROWS if r["id"] == "FFeller"][0]
assert _FF["per"] == 1.0 and _FF["base"] == 0.0 and _FF["max"] == 5 and TREES[_FF["t"]] == "Foraging" and _FF["s"] == 12
''')

# ================================================================ trees.properties defaults + the 0.2.1 blocks
rep('''      "feller.cooldownSec=30", "feller.needLeaves=true", "feller.maxHeight=32",
''', '''      "# Tree Feller (0.2.1): breaks logs beside the cut on the SAME Y level only - levels 1-4 = 1-4 logs, the max level = every log",
      "# of that tree on that level (up to feller.maxPerLayer). Hytale itself fells the tree once its whole layer is cut.",
      "feller.cooldownSec=5", "feller.maxPerLayer=64",
      "# Natural-tree check: the cut wood must touch leaves within feller.maxHeight blocks above or below the cut (nothing there is broken)",
      "feller.needLeaves=true", "feller.maxHeight=32",
      "# Felled trees (SkyySkills 0.4.2 pays every log that falls): those logs also roll Sap Tapper, Replanter and Pocket Change",
      "felled.nodes=true",
''')
rep('''      "# per = amount per node level: a fraction for % nodes (0.02 = 2%), a flat amount for Health / Stamina, blocks for Vein Burst",
      "# and Tree Feller (up to base + per x level); Master Chef: per = chance per level above 1."]''',
    '''      "# per = amount per node level: a fraction for % nodes (0.02 = 2%), a flat amount for Health / Stamina, blocks for Vein Burst",
      "# (up to base + per x level), logs on the cut level for Tree Feller (base + per x level; its max level = the whole layer),",
      "# a fraction of your own jump height for Double Jump (base + per x level); Master Chef: per = chance per level above 1."]''')
rep('''    if KINDS[r["kind"]] in ("VEIN", "FELLER"): out.append(k + "base=%s" % repr(float(r["base"])))''',
    '''    if KINDS[r["kind"]] in ("VEIN", "FELLER", "DJUMP"): out.append(k + "base=%s" % repr(float(r["base"])))''')
after('''assert "Acrobatics.RSpeed.max=25" in ADD02 and "Exploration.EHeart2.enabled=true" in ADD02 and "Mining." not in ADD02
''', '''# 0.2.1: appended ONCE to a file 0.2 wrote (it has the 0.2 keys but no Acrobatics.RDouble.* key): Double Jump replaced Quick Dodge
ADD021DJ = ["# ---------- SkyyTrees 0.2.1 (added once to a 0.2 file): Double Jump replaced Quick Dodge in Acrobatics S5 ----------",
            "# The old Acrobatics.RDodge.* lines are no longer read (their numbers do not carry over to Double Jump) - you can delete them."]
for r in ROWS:
    if r["id"] == "RDouble": ADD021DJ.extend(node_lines(r))
ADD021DJ = "\\n".join(ADD021DJ) + "\\n"
# 0.2.1: appended ONCE to any older file (no feller.maxPerLayer key), right after the old default Tree Feller lines were rewritten in
# place (TreeCfg.migrateFeller). It only ADDS keys: a second feller.cooldownSec / FFeller line here would override a custom value.
ADD021FEL = "\\n".join([
    "# ---------- SkyyTrees 0.2.1 (added once): Tree Feller rework ----------",
    "# Tree Feller now breaks logs beside the cut on the SAME Y level only (Hytale itself fells a tree once its whole layer is cut):",
    "# levels 1-4 = 1-4 more logs (base + per x level), the max level = every log of that tree on that level, up to feller.maxPerLayer.",
    "# The old default lines Foraging.FFeller.per=8.0 / Foraging.FFeller.base=8.0 / feller.cooldownSec=30 were changed to 1.0 / 0.0 / 5",
    "# (custom values were kept). feller.maxHeight now only sets how far above / below the cut the leaves check looks.",
    "feller.maxPerLayer=64",
    "# Felled trees (SkyySkills 0.4.2 pays every log that falls): those logs also roll Sap Tapper, Replanter and Pocket Change.",
    "felled.nodes=true"]) + "\\n"
for _b in (ADD021DJ, ADD021FEL): assert all(ord(ch) < 128 for ch in _b)
assert "Acrobatics.RDodge." not in DEFAULTS and "Acrobatics.RDodge." not in ADD02 and "Acrobatics.RDodge2.max=10" in DEFAULTS
assert "Acrobatics.RDouble.base=0.5" in DEFAULTS and "Acrobatics.RDouble.max=10" in ADD02 and "Acrobatics.RDouble.base=0.5" in ADD021DJ
assert "Foraging.FFeller.per=1.0" in DEFAULTS and "Foraging.FFeller.base=0.0" in DEFAULTS and "feller.cooldownSec=5" in DEFAULTS
assert "feller.maxPerLayer=64" in DEFAULTS and "felled.nodes=true" in DEFAULTS and "feller.cooldownSec=30" not in DEFAULTS
assert "feller.maxPerLayer=64" in ADD021FEL and "felled.nodes=true" in ADD021FEL
assert not [l for l in ADD021FEL.splitlines() if not l.startswith("#") and (l.startswith("feller.cooldownSec") or "FFeller" in l)]
assert "Acrobatics." not in ADD021FEL and "feller." not in ADD021DJ
''')

# ================================================================ TreeCfg: new settings + the one-time 0.2.1 upgrade of trees.properties
rep('''F(cfg, "public static final String ADD02 = " + json.dumps(ADD02) + ";")''',
    '''F(cfg, "public static final String ADD02 = " + json.dumps(ADD02) + ";")
F(cfg, "public static final String ADD021DJ = " + json.dumps(ADD021DJ) + ";")
F(cfg, "public static final String ADD021FEL = " + json.dumps(ADD021FEL) + ";")''')
rep('''             "int FELLER_H = 32", "long VEIN_CD_MS = 40000L", "long FELLER_CD_MS = 30000L", "boolean FELLER_LEAVES = true",''',
    '''             "int FELLER_H = 32", "long VEIN_CD_MS = 40000L", "long FELLER_CD_MS = 5000L", "boolean FELLER_LEAVES = true",
             "int FELLER_ALL = 64", "boolean FELLED_NODES = true",''')
rep('''  FELLER_CD_MS = clampL(lng(p, "feller.cooldownSec", 30L), 0L, 86400L) * 1000L;
  FELLER_LEAVES = bool(p, "feller.needLeaves", true);''', '''  FELLER_CD_MS = clampL(lng(p, "feller.cooldownSec", 5L), 0L, 86400L) * 1000L;
  FELLER_LEAVES = bool(p, "feller.needLeaves", true);
  FELLER_ALL = (int) clampL(lng(p, "feller.maxPerLayer", 64L), 1L, 256L);
  FELLED_NODES = bool(p, "felled.nodes", true);''')
before('''M(cfg, r"""
public static synchronized String load() {''', '''M(cfg, r"""
public static boolean hasPrefix(java.util.Properties p, String pre) {
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith(pre)) return true;
  }
  return false;
}""")
# one "key=value" line whose key AND value text equal (key, old) -> "key=neu" (its \\r kept); anything else (comments, other keys,
# custom values, other separators) -> null = untouched
M(cfg, r"""
public static String migrateLine(String ln, String key, String old, String neu) {
  String body = ln;
  String cr = "";
  if (body.endsWith("\\r")) { body = body.substring(0, body.length() - 1); cr = "\\r"; }
  String tb = body.trim();
  if (tb.length() == 0 || tb.charAt(0) == '#' || tb.charAt(0) == '!') return null;
  int eq = body.indexOf('=');
  if (eq <= 0) return null;
  if (!body.substring(0, eq).trim().equals(key)) return null;
  if (!body.substring(eq + 1).trim().equals(old)) return null;
  return key + "=" + neu + cr;
}""")
# 0.2.1 Tree Feller rework: the unchanged 0.1 / 0.2 default lines only (n[0] = lines changed)
M(cfg, r"""
public static String migrateFeller(String text, int[] n) {
  String[] ls = text.split("\\n", -1);
  StringBuilder sb = new StringBuilder(text.length() + 16);
  for (int i = 0; i < ls.length; i++) {
    String ln = ls[i];
    String r = migrateLine(ln, "Foraging.FFeller.per", "8.0", "1.0");
    if (r == null) r = migrateLine(ln, "Foraging.FFeller.base", "8.0", "0.0");
    if (r == null) r = migrateLine(ln, "feller.cooldownSec", "30", "5");
    if (r != null) { ln = r; n[0] = n[0] + 1; }
    if (i > 0) sb.append('\\n');
    sb.append(ln);
  }
  return sb.toString();
}""")
# ONE atomic write for everything an older trees.properties is missing: the 0.2 block (a 0.1 file; it already carries the Double Jump
# lines), the Double Jump block (a 0.2 file), the Tree Feller migration + block (any file without feller.maxPerLayer). The returned
# settings are parsed from exactly the new content (ISO-8859-1 = what Properties.load(InputStream) reads), so a failed write still runs
# with the migrated numbers and the next load simply tries again.
M(cfg, r"""
public static java.util.Properties upgrade(java.util.Properties p) {
  boolean need02 = !has02(p);
  boolean needDj = !need02 && !hasPrefix(p, "Acrobatics.RDouble.");
  boolean needFel = p.getProperty("feller.maxPerLayer") == null;
  if (!need02 && !needDj && !needFel) return p;
  java.util.Properties q = p;
  try {
    byte[] old = java.nio.file.Files.readAllBytes(FILE);
    String text = new String(old, "ISO-8859-1");
    int[] n = new int[1];
    if (needFel) text = migrateFeller(text, n);
    StringBuilder sb = new StringBuilder(text);
    if (need02) sb.append("\\n").append(ADD02);
    if (needDj) sb.append("\\n").append(ADD021DJ);
    if (needFel) sb.append("\\n").append(ADD021FEL);
    byte[] data = sb.toString().getBytes("ISO-8859-1");
    java.util.Properties np = new java.util.Properties();
    np.load(new java.io.ByteArrayInputStream(data));
    q = np;
    try {
      writeAtomic(data);
      info("updated " + FILE + " for SkyyTrees 0.2.1:" + (need02 ? " added the 0.2 lines (Acrobatics and Exploration trees, per-tree Dust rates);" : "") + (needDj ? " added the Double Jump lines;" : "") + (needFel ? " Tree Feller rework (" + n[0] + " old default line(s) changed, feller.maxPerLayer added)" : ""));
    } catch (Throwable t2) { warn("could not update trees.properties (the new values apply anyway, the next load tries again): " + t2); }
  } catch (Throwable t) {
    warn("could not read trees.properties for the 0.2.1 update (the Tree Feller defaults are migrated in memory only): " + t);
    q = new java.util.Properties();
    q.putAll(p);
    if (needFel) {
      if ("8.0".equals(str(q, "Foraging.FFeller.per", ""))) q.setProperty("Foraging.FFeller.per", "1.0");
      if ("8.0".equals(str(q, "Foraging.FFeller.base", ""))) q.setProperty("Foraging.FFeller.base", "0.0");
      if ("30".equals(str(q, "feller.cooldownSec", ""))) q.setProperty("feller.cooldownSec", "5");
    }
  }
  if (needFel) {
    String pe = str(q, "Foraging.FFeller.per", "1.0");
    String ba = str(q, "Foraging.FFeller.base", "0.0");
    if (!"1.0".equals(pe) || !"0.0".equals(ba)) warn("Tree Feller custom numbers kept (Foraging.FFeller.per=" + pe + ", base=" + ba + "): since 0.2.1 they count logs on the SAME level as the cut (default per=1.0 base=0.0 = 1, 2, 3, 4 logs; the max level breaks the whole layer)");
  }
  if (needDj && hasPrefix(q, "Acrobatics.RDodge.")) info("Acrobatics.RDodge.* lines in trees.properties are unused since 0.2.1 (Quick Dodge became Double Jump) - you can delete them");
  return q;
}""")
''')
rep('''  if (loaded && !has02(p)) {
    try {
      byte[] old = java.nio.file.Files.readAllBytes(FILE);
      byte[] add = ("\\n" + ADD02).getBytes("UTF-8");
      java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream(old.length + add.length);
      bo.write(old, 0, old.length);
      bo.write(add, 0, add.length);
      writeAtomic(bo.toByteArray());
      info("added the SkyyTrees 0.2 lines (Acrobatics and Exploration trees, per-tree Dust rates) to " + FILE);
    } catch (Throwable t2) { warn("could not add the 0.2 lines to trees.properties (their built-in defaults apply anyway): " + t2); }
  }
  apply(p);''', '''  if (loaded) p = upgrade(p);
  apply(p);''')

# ================================================================ TreeStore.readFile: Acrobatics.RDodge (0.2 Quick Dodge) -> RDouble
rep('''      try { int x = Integer.parseInt(v.trim()); d.lv[i] = x < 0 ? 0 : (x > 1000 ? 1000 : x); } catch (Throwable t) { }
    }
    for (int tt = 0; tt < @PKG@.TreeDefs.NT; tt++) {''', '''      try { int x = Integer.parseInt(v.trim()); d.lv[i] = x < 0 ? 0 : (x > 1000 ? 1000 : x); } catch (Throwable t) { }
    }
    // 0.2.1: Acrobatics slot 5 was RDodge (Quick Dodge) in 0.2 - same slot = same Token and Dust cost; an RDouble line always wins
    if (p.getProperty("Acrobatics.RDouble") == null) {
      String ov = p.getProperty("Acrobatics.RDodge");
      if (ov != null) { try { int x = Integer.parseInt(ov.trim()); d.lv[@I_RDOUBLE@] = x < 0 ? 0 : (x > 1000 ? 1000 : x); } catch (Throwable t3) { } }
    }
    for (int tt = 0; tt < @PKG@.TreeDefs.NT; tt++) {''')
rep('''          int i = @PKG@.TreeDefs.idx(tn + "." + xs[j].trim());
          if (i >= 0) d.off[i] = true;''', '''          int i = @PKG@.TreeDefs.idx(tn + "." + xs[j].trim());
          if (i < 0 && "Acrobatics".equals(tn) && "RDodge".equalsIgnoreCase(xs[j].trim())) i = @I_RDOUBLE@;
          if (i >= 0) d.off[i] = true;''')

# ================================================================ TreeFx: Feller max = the whole layer, Double Jump value, bonus keys
rep('''  if (k == @K_VEIN@ || k == @K_FELLER@) return @PKG@.TreeCfg.BASE[i] + per * (double) eff;''',
    '''  if (k == @K_FELLER@ && eff >= @PKG@.TreeCfg.MAX[i]) return (double) @PKG@.TreeCfg.FELLER_ALL;
  if (k == @K_VEIN@ || k == @K_FELLER@ || k == @K_DJUMP@) return @PKG@.TreeCfg.BASE[i] + per * (double) eff;''')
rep('''  putNZ(m, "dodge.acrobatics", v[@I_RDODGE@] + v[@I_RDODGE2@]);''',
    '''  putNZ(m, "dodge.acrobatics", v[@I_RDODGE2@]);
  putNZ(m, "doublejump.acrobatics", v[@I_RDOUBLE@]);''')
after('''M(fx, r"""
public static double r6(double x) {
  return Math.round(x * 1000000.0) / 1000000.0;
}""")''', '''
# 0.2.1 Double Jump card: the trigger key SkyySkills 0.4.2 publishes (skill:dj:key = "crouch" / "jump" / "jump or crouch"), else crouch
M(fx, r"""
public static String djKey() {
  try {
    Object o = @PKG@.TreeStore.bridge().get("skill:dj:key");
    if (o instanceof String && ((String) o).trim().length() > 0) return ((String) o).trim();
  } catch (Throwable t) { }
  return "crouch";
}""")''')

# ================================================================ TreeAbil: same-Y flood + the reworked Tree Feller
before('''M(abil, r"""
public static @V3I@ pickNeighbour(''', '''# 0.2.1 Tree Feller (Tree-Fall-Spec 3.3): breadth-first on the cut's Y level ONLY, over the 8 horizontal neighbours - the 4 sides
# before the 4 diagonals - so the logs nearest the cut come first. TreeDefs.isLog(id, fam) = Wood_<W>_Trunk / _Trunk_Full (+ states)
# only, not placed, not broken by an ability in the last 5 s, |dx|, |dz| <= rh, at most max positions and 4000 reads. Never another Y level.
M(abil, r"""
public static java.util.ArrayList flatFlood(@WLD@ w, String wn, int ox, int oy, int oz, String fam, int max, int rh, java.util.function.Function pf) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (max <= 0 || fam == null) return out;
  int[] ddx = new int[] { 1, -1, 0, 0, 1, 1, -1, -1 };
  int[] ddz = new int[] { 0, 0, 1, -1, 1, -1, 1, -1 };
  java.util.HashSet seen = new java.util.HashSet();
  java.util.ArrayDeque q = new java.util.ArrayDeque();
  seen.add(Long.valueOf(pos(ox, oy, oz)));
  q.add(new int[] { ox, oz });
  int reads = 0;
  while (!q.isEmpty() && reads < 4000 && out.size() < max) {
    int[] c = (int[]) q.poll();
    for (int n = 0; n < 8 && out.size() < max; n++) {
      int x = c[0] + ddx[n];
      int z = c[1] + ddz[n];
      if (Math.abs(x - ox) > rh || Math.abs(z - oz) > rh) continue;
      Long k = Long.valueOf(pos(x, oy, z));
      if (seen.contains(k)) continue;
      seen.add(k);
      reads++;
      String id = blockIdAt(w, x, oy, z);
      if (!@PKG@.TreeDefs.isLog(id, fam)) continue;
      if (recent(wn, x, oy, z) || placed(pf, wn, x, oy, z)) continue;
      q.add(new int[] { x, z });
      out.add(new @V3I@(x, oy, z));
    }
  }
  return out;
}""")
''')
rep('''  boolean[] leaves = new boolean[1];
  java.util.ArrayList l = flood(w, wn, x, y, z, fam, true, max, 256, @PKG@.TreeCfg.RADIUS, @PKG@.TreeCfg.FELLER_H, leaves, pf);
  if (l.isEmpty()) return false;
  if (@PKG@.TreeCfg.FELLER_LEAVES && !leaves[0]) return false;
  int n = breakList(pr, w, wn, l);
  if (n <= 0) return false;
  long cd = @PKG@.TreeCfg.FELLER_CD_MS;
  CD.put(u.toString() + "|feller", Long.valueOf(System.currentTimeMillis() + cd));
  @PKG@.TreeMsg.say(pr, "Tree Feller! +" + n + " logs (ready again in " + (cd / 1000L) + " s)", "#ffc300");''',
    '''  java.util.ArrayList l = flatFlood(w, wn, x, y, z, fam, max, @PKG@.TreeCfg.RADIUS, pf);
  if (l.isEmpty()) return false;
  if (@PKG@.TreeCfg.FELLER_LEAVES) {
    boolean[] leaves = new boolean[1];
    flood(w, wn, x, y, z, fam, true, 0, 256, @PKG@.TreeCfg.RADIUS, @PKG@.TreeCfg.FELLER_H, leaves, pf);
    if (!leaves[0]) return false;
  }
  int n = breakList(pr, w, wn, l);
  if (n <= 0) return false;
  long cd = @PKG@.TreeCfg.FELLER_CD_MS;
  CD.put(u.toString() + "|feller", Long.valueOf(System.currentTimeMillis() + cd));
  @PKG@.TreeMsg.say(pr, "Tree Feller! +" + n + (n == 1 ? " log" : " logs") + " on this level" + (cd > 0L ? " (ready again in " + (cd / 1000L) + " s)" : ""), "#ffc300");''')

# ================================================================ TreeGather: felled-log rolls + the skill:on:felled registration
rep('''F(gat, "public static Object INSTANCE;")''', '''F(gat, "public static Object INSTANCE;")
F(gat, "public static Object FELLED;")
F(gat, "public static boolean OFF_THREAD_TOLD = false;")''')
before('''# SkyySkills 0.4 calls this on the world thread: Object[]{PlayerRef, Integer row, BlockType, String world, Boolean harvest, x, y, z}''',
       '''# 0.2.1 (Tree-Fall-Spec 3.3): one log that FELL because this player cut the tree (SkyySkills 0.4.2 skill:on:felled, world thread).
# Foraging trunks roll Sap Tapper, Replanter and Pocket Change exactly like run(); abilities (Spread / Vein Burst / Tree Feller) never.
# Review guards: a position one of OUR abilities broke in the last 5 s (TreeAbil.mark) already rolled in run() through its real
# BreakBlockEvent, so it never rolls again here, whatever SkyySkills reports; off the world thread nothing happens (warned once).
M(gat, r"""
public static void felled(@PR@ pr, int row, @BTY@ bt, String wn, int x, int y, int z) {
  if (!@PKG@.TreeCfg.FELLED_NODES || row != 1 || bt == null || wn == null) return;
  if (@PKG@.TreeAbil.recent(wn, x, y, z)) return;
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return;
  if (!r.getStore().isInThread()) {
    if (!OFF_THREAD_TOLD) { OFF_THREAD_TOLD = true; @PKG@.TreeCfg.warn("skill:on:felled was called off the world thread - felled-log tree bonuses skipped (logged once)"); }
    return;
  }
  java.util.UUID u = pr.getUuid();
  if (@PKG@.TreeStore.busy(u)) return;
  String id = @PKG@.TreeDefs.bid(bt);
  if (id.indexOf("_Trunk") < 0) return;
  double[] v = @PKG@.TreeFx.get(u);
  if (v == null) v = @PKG@.TreeFx.compute(u);
  Object[] lists = @PKG@.TreeCfg.LIST;
  if (roll(v[@I_FSAP@])) giveItem(pr, wn, pick(lists[@I_FSAP@]));
  if (roll(v[@I_FSAPLING@])) giveItem(pr, wn, @PKG@.TreeDefs.saplingOf(id));
  if (roll(v[@I_FCOINS@])) coins(pr, 1);
}""")
''')
after('''M(gat, r"""
public static java.util.Map gatherMap() {
  java.util.Map b = @PKG@.TreeStore.bridge();
  Object o = b.get("skill:on:gather");
  if (o instanceof java.util.Map) return (java.util.Map) o;
  java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
  Object prev = b.putIfAbsent("skill:on:gather", n);
  if (prev instanceof java.util.Map) return (java.util.Map) prev;
  return n;
}""")''', '''
M(gat, r"""
public static java.util.Map felledMap() {
  java.util.Map b = @PKG@.TreeStore.bridge();
  Object o = b.get("skill:on:felled");
  if (o instanceof java.util.Map) return (java.util.Map) o;
  java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
  Object prev = b.putIfAbsent("skill:on:felled", n);
  if (prev instanceof java.util.Map) return (java.util.Map) prev;
  return n;
}""")''')
rep('''    if (INSTANCE == null) return;
    java.util.Map m = gatherMap();
    if (m.get("trees") != INSTANCE) m.put("trees", INSTANCE);
  } catch (Throwable t) { }''', '''    if (INSTANCE == null) return;
    java.util.Map m = gatherMap();
    if (m.get("trees") != INSTANCE) m.put("trees", INSTANCE);
  } catch (Throwable t) { }
  try {
    if (FELLED == null) return;
    java.util.Map f = felledMap();
    if (f.get("trees") != FELLED) f.put("trees", FELLED);
  } catch (Throwable t2) { }''')
rep('''    if (o instanceof java.util.Map && INSTANCE != null) ((java.util.Map) o).remove("trees", INSTANCE);
  } catch (Throwable t) { }''', '''    if (o instanceof java.util.Map && INSTANCE != null) ((java.util.Map) o).remove("trees", INSTANCE);
  } catch (Throwable t) { }
  try {
    Object f = @PKG@.TreeStore.bridge().get("skill:on:felled");
    if (f instanceof java.util.Map && FELLED != null) ((java.util.Map) f).remove("trees", FELLED);
  } catch (Throwable t2) { }''')

# ================================================================ TreeFelledFn: the skill:on:felled listener object
rep('''bfn = pool.makeClass(PKG + ".TreeBonusFn")''', '''bfn = pool.makeClass(PKG + ".TreeBonusFn")
ffn = pool.makeClass(PKG + ".TreeFelledFn")''')
before('''# ================= TreeDmgSys: breaking power (DMG) =================''', '''# 0.2.1: SkyySkills 0.4.2 calls this once per credited felled position, world thread:
# Object[]{PlayerRef, Integer row, BlockType, String world, Integer x, Integer y, Integer z, String pkey} (Tree-Fall-Spec 2.8)
ffn.addInterface(pool.get("java.util.function.Function"))
F(ffn, "public static boolean FAILED_ONCE = false;")
C(ffn, "public TreeFelledFn() { }")
M(ffn, r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 7 || !(a[0] instanceof @PR@) || !(a[1] instanceof Number)) return null;
    if (!(a[4] instanceof Number) || !(a[5] instanceof Number) || !(a[6] instanceof Number)) return null;
    @PR@ pr = (@PR@) a[0];
    if (a.length >= 8 && a[7] instanceof String && !((String) a[7]).equals(@PKG@.TreeStore.pkey(pr.getUuid()))) return null;
    @BTY@ bt = null;
    if (a[2] instanceof @BTY@) bt = (@BTY@) a[2];
    String wn = null;
    if (a[3] instanceof String) wn = (String) a[3];
    @PKG@.TreeGather.felled(pr, ((Number) a[1]).intValue(), bt, wn, ((Number) a[4]).intValue(), ((Number) a[5]).intValue(), ((Number) a[6]).intValue());
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TreeCfg.warn("felled-log tree bonus failed (logged once): " + t); }
  }
  return null;
}""")

''')
rep('''ALL = (defs, cfg, dat, sto, stk, calc, fx, msg, abil, gat, tfn, bfn, dmg, tick, svr, ops, page, vcmd, qcmd, rcmd, cmd, pl)''',
    '''ALL = (defs, cfg, dat, sto, stk, calc, fx, msg, abil, gat, tfn, bfn, ffn, dmg, tick, svr, ops, page, vcmd, qcmd, rcmd, cmd, pl)''')
rep('''  @PKG@.TreeGather.INSTANCE = new @PKG@.TreeGather();
  @PKG@.TreeGather.ensure();''', '''  @PKG@.TreeGather.INSTANCE = new @PKG@.TreeGather();
  @PKG@.TreeGather.FELLED = new @PKG@.TreeFelledFn();
  @PKG@.TreeGather.ensure();''')

# ================================================================ TreePage: Feller texts, %K on the Double Jump card
rep('''    return "+1 Grade on every dish and a " + @PKG@.TreeDefs.pct(@PKG@.TreeFx.value(i, eff)) + " chance of one more";
  }''', '''    return "+1 Grade on every dish and a " + @PKG@.TreeDefs.pct(@PKG@.TreeFx.value(i, eff)) + " chance of one more";
  }
  if (@PKG@.TreeDefs.KIND[i] == @K_FELLER@) {
    if (eff <= 0) return "nothing yet";
    if (eff >= @PKG@.TreeCfg.MAX[i]) return "Breaks every log of that tree on the same level (up to " + @PKG@.TreeCfg.FELLER_ALL + ")";
    long fn = Math.round(@PKG@.TreeFx.value(i, eff));
    return "Breaks " + fn + (fn == 1L ? " more log" : " more logs") + " beside it on the same level";
  }''')
rep('''  line(b, "SkyyTrDetHow", @PKG@.TreeDefs.HOW[i0].replace("%C", cd(i0)), "#8fa6ba", 11, false, 52);''',
    '''  line(b, "SkyyTrDetHow", @PKG@.TreeDefs.HOW[i0].replace("%C", cd(i0)).replace("%K", @PKG@.TreeFx.djKey()), "#8fa6ba", 11, false, 72);''')
# review: the detail column (330 wide, padding 10 -> 310 px text, 498 high, padding 8 -> 482 px) stacks 60 + 24 + 40 + 40 + 22 + 40 +
# HOW + 10 + 36 + 8 + 32; HOW 72 (4 lines at FontSize 11) -> 384 px, so it still fits with ~98 px to spare
assert 60 + 24 + 40 + 40 + 22 + 40 + 72 + 10 + 36 + 8 + 32 <= 498 - 16
for _l in ('"SkyyTrDetState", stateLine(d, i0, st0), fg0, 13, true, 24);', '"SkyyTrDetNow", nowLine(d, i0), "#dfe8f0", 12, false, 40);',
           '"SkyyTrDetNext", nextLine(d, i0), "#bfe8c8", 12, false, 40);', '"SkyyTrDetCost", costLine(d, i0), "#ffe08a", 12, false, 22);',
           '"SkyyTrDetNeed", needLine(d, i0, lvl, tokA, dustA), "#ffb080", 12, false, 40);', 'Group #SkyyTrDetTop { Anchor: (Height: 60)',
           'Group #SkyyTrDet { Anchor: (Width: 330, Height: 498); Background: #101d30; Padding: (Horizontal: 10, Vertical: 8)',
           'TextButton #SkyyTrBuy { Anchor: (Width: 306, Height: 36)', 'TextButton #SkyyTrToggle { Anchor: (Width: 306, Height: 32)'):
    assert s.count(_l) == 1, "detail panel layout changed: " + _l

# ================================================================ manifest text
rep('''move speed / jump / fall damage / dodge push and the chest luck SkyyExploration reads.''',
    '''move speed / jump / fall damage / dodge push / Double Jump and the chest luck SkyyExploration reads.''')

# ================================================================ sanity
assert 'VERSION = "0.2.1"' in s and "DERIVED from build_skyytrees_0.2.py by tools/trees_0_2_1_patch.py" in s
for bad in ('"RDodge", "Quick Dodge"', "v[@I_RDODGE@]", '_tot(("RDodge", "RDodge2"))', "adds to Quick Dodge", "Fells up to %V connected logs",
            '"FELLER", 5, 8.0, 8.0', '"feller.cooldownSec=30", "feller.needLeaves', '"feller.cooldownSec", 30L', "FELLER_CD_MS = 30000L",
            'logs (ready again in " + (cd / 1000L)', "if (loaded && !has02(p))", "flood(w, wn, x, y, z, fam, true, max, 256"):
    assert bad not in s, "0.2 leftover: " + bad
assert s.count("public static java.util.ArrayList flatFlood(") == 1 and s.count("flatFlood(w, wn, x, y, z, fam, max, @PKG@.TreeCfg.RADIUS, pf)") == 1
assert s.count("flood(w, wn, x, y, z, fam, true, 0, 256,") == 1   # the read-only leaves check
assert s.count('putNZ(m, "doublejump.acrobatics", v[@I_RDOUBLE@]);') == 1 and s.count('putNZ(m, "dodge.acrobatics", v[@I_RDODGE2@]);') == 1
assert s.count('"Acrobatics.RDodge"') == 1 and s.count('"RDodge".equalsIgnoreCase') == 1 and s.count("d.lv[@I_RDOUBLE@] =") == 1
assert s.count("if (loaded) p = upgrade(p);") == 1 and s.count("public static java.util.Properties upgrade(") == 1
# trees.properties is still only ever written through TreeCfg.writeAtomic (tmp + atomic move): the default file and the upgrade
assert s.count("writeAtomic(DEFAULTS.getBytes") == 1 and s.count("writeAtomic(data);") == 1 and s.count("writeAtomic(") == 3
assert s.count('b.get("skill:on:felled")') == 1 and s.count('putIfAbsent("skill:on:felled"') == 1 and s.count("new @PKG@.TreeFelledFn()") == 1
assert s.count('.replace("%K", @PKG@.TreeFx.djKey())') == 1 and s.count('"skill:dj:key"') == 1
# review fixes
assert s.count("public static boolean isLog(String id, String fam)") == 1 and s.count("@PKG@.TreeDefs.isLog(id, ") == 3
assert "id.startsWith(fam)" not in s and "prefix ? id.startsWith(match)" not in s
assert s.count("  if (@PKG@.TreeAbil.recent(wn, x, y, z)) return;\n  @REF@ r = pr.getReference();") == 1
assert s.count("if (!r.getStore().isInThread())") == 1 and s.count("if (k == @K_DJUMP@) return pct(v);") == 1
assert s.count('"#8fa6ba", 11, false, 72);') == 1 and '"#8fa6ba", 11, false, 52);' not in s
assert s.count("registerSystem(") == 2   # one registerSystem per class, unchanged: TreeDmgSys + TreeTick
assert s.count('setPermissionGroups(new String[] { "hytale:Adventurer" })') == 3 and s.count("setPermissionGroups(new String[0])") == 1
assert "--deploy" in s   # the script keeps its optional deploy switch; workflows never pass it
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.2
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
