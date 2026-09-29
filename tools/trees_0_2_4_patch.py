"""Derive SkyyTrees/build_skyytrees_0.2.4.py from the EDITED SkyyTrees/build_skyytrees_0.2.3.py (Skyy edited that generated script
directly in commit ab75b6c - NEVER re-run tools/trees_0_2_3_patch.py, it would drop those edits). Same style as trees_0_2_3_patch.py:
rep(old, new) with asserted single anchors, newline-agnostic; 0.2.3 stays untouched and its CRLF line endings are kept. Edit THIS file,
not the generated script.

0.2.4 = Skyy's 2026-09-25 locks (OPEN-QUESTIONS.md, research/Tree-Fall-Spec.md, research/Double-Jump-Spec.md, research/Swing-Speed-Spec.md):
 - Tree Feller: same height; extra logs 1 / 2 / 4 / 5 / 6 / 10 at node levels 1-6 (a 6-level table feller.logs replaces base + per x level
   and "the whole layer at max"); cooldown 3 s (Skyy's edit kept). Foraging.FFeller max 5 -> 6; players keep their levels.
 - Double Jump -> Acrobatics tier III slot 7 (replaces Sprinter); Quick Dodge back in tier II slot 5. Player files migrate (v=2): Double
   Jump buyers keep their level in S7 and a Dust credit pays the higher tier III price of the levels they already bought; Sprinter is
   refunded (Tokens / Dust are computed from levels); one-time chat line.
 - Mining Speed +40% (per 0.016), Heavy Pick on rock + ore, Heavy Hatchet +100% (per 0.05): Skyy's edit, kept exactly.
 - HARD RULE: the hatchet swing-speed bonus only when the swing chops WOOD (generated copy of the vanilla swing with a BlockCondition at
   the block-break moment); mobs, air and other blocks keep the vanilla cadence.
 - Config kit KEEP 20 -> 10 (LOCKED 2026-09-25).
 - The edited 0.2.3 builds as-is (checked 2026-09-28 in tools/dev/scratch/r9-trees): no kit-limit fix needed.
Run:  python tools/trees_0_2_4_patch.py   then   python SkyyTrees/build_skyytrees_0.2.4.py   (NO --deploy: coordinated deploy)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.2.3.py")
dst = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.2.4.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2.3"
s = raw.decode("utf8").replace("\r\n", "\n")
REG0 = s.count("registerSystem(")
# the EDITED 0.2.3 (commit ab75b6c) is the source: its locked defaults must be there, or this is the wrong file
for _a in ('("MSpeed", "Mining Speed", "Tool_Pickaxe_Iron", "SWING", 25, 0.016, 0,', '"feller.cooldownSec=3", "feller.maxPerLayer=64",',
           '("FSpeed2", "Heavy Hatchet", "Tool_Hatchet_Mithril", "DMG", 20, 0.05, 0,', '  return "jump";\n}""")',
           'boolean rock = ore || "Rocks".equals(gt) || "VolcanicRocks".equals(gt) || (gt != null && gt.startsWith("Ore"));'):
    assert s.count(_a) == 1, "not the edited 0.2.3 (commit ab75b6c): missing %r" % _a


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    s = s.replace(old, new)


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


# ================================================================ header / version
rep('''"""SkyyTrees 0.2.3 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
DERIVED from build_skyytrees_0.2.2.py by tools/trees_0_2_3_patch.py - edit the patch, not this file (0.2.2 stays untouched; 0.2.2 was
derived from 0.2.1 by tools/trees_0_2_2_patch.py, 0.2.1 from 0.2 by tools/trees_0_2_1_patch.py, 0.2 from 0.1 by tools/trees_0_2_patch.py).
0.2.3 = research/Swing-Speed-Spec.md.''', r'''"""SkyyTrees 0.2.4 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
DERIVED from the EDITED build_skyytrees_0.2.3.py by tools/trees_0_2_4_patch.py - edit the patch, not this file. 0.2.3 was derived from
0.2.2 by tools/trees_0_2_3_patch.py and then edited by Skyy in commit ab75b6c (locked defaults) - never re-run that patch; 0.2.2 was
derived from 0.2.1 by tools/trees_0_2_2_patch.py, 0.2.1 from 0.2 by tools/trees_0_2_1_patch.py, 0.2 from 0.1 by tools/trees_0_2_patch.py.
0.2.4 = Skyy's 2026-09-25 locks (OPEN-QUESTIONS.md; research/Tree-Fall-Spec.md, Double-Jump-Spec.md, Swing-Speed-Spec.md "LOCKED" parts).
  The edited 0.2.3 builds as-is (checked 2026-09-28 in a scratch copy): no kit-limit or other fix was needed.
  TREE FELLER (same height as the cut, unchanged): extra logs by node level = the table feller.logs (default 1,2,4,5,6,10 at levels 1-6),
    replacing base + per x level and "every log of the layer at max". Foraging.FFeller max 5 -> 6 (this node only - every other
    capstone stays 5; level 5 -> 6 costs the template B x 5^3 = 18,750,000 Foraging Dust). A level above the table uses its last number;
    feller.maxPerLayer (64) is only a safety ceiling now. Cooldown default 3 s (Skyy's edit, kept: a file still on feller.cooldownSec=5
    keeps 5). Foraging.FFeller.per / base are no longer read (a new file has no such lines; the Server Setup node table asks first when
    one is edited). The /tree card says "Breaks N more logs beside it on the same level" at every level. Players keep their levels
    (plain numbers): a level-5 owner is no longer maxed (level 5 = 6 logs) and can buy level 6 (10 logs).
  DOUBLE JUMP: Acrobatics tier III slot 7 (Acrobatics 20, template B 500, 1 token), replacing Sprinter (RSpeed2). Quick Dodge (RDodge, the
    0.2 row: +1% dodge push per level, max 10, B 150) is back in tier II slot 5. Acrobatics totals at max: speed +15% (was +20%), dodge
    push +20% (skill:bonus dodge.acrobatics = Quick Dodge + Evasion again; Evasion "adds to Quick Dodge"), Windrunner "adds to Fleet
    Foot". skill:bonus doublejump.acrobatics is unchanged; the trigger (default jump) and the jump itself live in SkyySkills.
  PLAYER FILES (nobody loses a token or Dust): 0.2.4 writes v=2. A file without v=2 is the 0.2.1-0.2.3 layout and is migrated when it is
    read (TreeStore.readFile, world thread): Acrobatics.RDouble (or the 0.2 key Acrobatics.RDodge when there is no RDouble line - what
    0.2.3 showed as Double Jump) = Double Jump, now in S7, same level, same off flag ("RDodge" in Acrobatics.off counts as Double Jump);
    Acrobatics.RSpeed2 (Sprinter) is dropped - its token and all its Dust come back by themselves (Tokens and Dust are computed from
    levels, never stored); Quick Dodge starts at 0. The Double Jump levels already bought were paid at the tier II price (Quick Dodge's
    B, 150); their tier III price (B 500) is higher, so the difference sum(n = 1 .. level-1) (B_RDouble - B_RDodge) x n^3 is stored as
    Acrobatics.dustCredit and added to the Acrobatics Dust earned (TreeCalc.balance). So every balance stays what 0.2.3 showed, plus
    the Sprinter refund. A respec of Acrobatics clears the credit (it only covered spent Dust: a respec gives back exactly the Dust
    earned, the same as a respec in 0.2.3). A changed file is marked dirty and saved within 10 s (then v=2: migrated once); an
    unchanged old file stays as it is until its next save. One-time chat line (TreeMsg.note024, from TreeTick, per profile, skipped while
    profile:busy; pending state kept in the file as note.r024=<Double Jump level>,<Sprinter level>,<Tree Feller level> until shown):
    "[Trees] SkyyTrees update: Double Jump moved to Acrobatics tier III (where Sprinter was) - you keep level N and pay no extra Dust.
    Sprinter was removed - its token and all its Dust are back (it was level M). Quick Dodge is back in tier II. Tree Feller now breaks
    1, 2, 4, 5, 6 or 10 more logs at levels 1-6 (no longer the whole layer)." (only the parts that apply). NEVER downgrade to 0.2.3
    after 0.2.4 saved a file: 0.2.3 reads a v=2 Acrobatics.RDouble line as the tier II node again (at its old price) and ignores the
    credit and the Quick Dodge levels (those levels would simply be refunded, the credit lost).
  HATCHET SWING SPEED ONLY ON WOOD (HARD RULE, Swing-Speed-Spec lock + OPEN-QUESTIONS "Swing speed"): 0.2.3 shortened the cooldown at the
    START of every hatchet swing, so hits on mobs came faster too. 0.2.4 decides at the moment the swing breaks its block instead:
    - root Hatchet_Attack (still SkyyTrees' override) -> Skyy_Tree_Swing_Chop: players without a chop tier effect go straight to the
      vanilla Interaction Hatchet_Attack (100% vanilla); a tier player's swing first resets the cooldown to the vanilla 0.35 s
      (TriggerCooldown) and runs Skyy_Tree_Chop_Chain (a copy of the vanilla Chaining step) -> Skyy_Tree_Chop, a GENERATED copy of the
      vanilla Hatchet_Chop whose one block-break step (0.05 s delay -> "Block_Break") points at Skyy_Tree_Chop_Wood instead.
    - Skyy_Tree_Chop_Wood runs at T_HIT = 0.083 + 0.05 = 0.133 s into the swing: a BlockCondition (UseLatestTarget = the block the swing
      is hitting now, like vanilla BreakBlock; matchers = tags Type=Wood / Trunk / Branch / Tree and BranchType=Long / Short / Corner,
      the tags the engine builds from the item Tags, checked in bytecode: AssetExtraInfo$Data.putTags adds key, value and key=value).
      Wood -> the tier tree -> TriggerCooldown (tier period - T_HIT), so the next swing comes at the tier period (0.35 / (1 + k%), the
      same numbers as 0.2.3); anything else (no block = air or a mob only, stone, dirt, furniture) -> TriggerCooldown (0.35 - T_HIT) =
      exactly the vanilla cadence. Then the unchanged vanilla Block_Break. Instant steps, no extra time; the mob-hit branch (Selector
      -> Hatchet_Chop_Damage, the item's Replace vars) is untouched. TriggerCooldown restarts the named cooldown from that moment
      (CooldownHandler$Cooldown.setCooldownMax + deductCharge -> remainingCooldown = the new length, bytecode 2026-09-28), and a client
      swing that arrives while the server still counts down only waits in the packet queue (InteractionManager.syncStart returns false).
    - Build-time self-checks (the build stops when Hytale changes what this relies on): the vanilla Interaction Hatchet_Attack is exactly
      {Chaining, ChainingAllowance, Next [Hatchet_Chop]}; Hatchet_Chop is Simple -> Parallel with exactly one branch [Simple -> "Block_Break"]
      and names Block_Break once; the copy differs from vanilla only in that one Next; every tier leaf + T_HIT = the tier period; every
      natural Wood_*_Trunk / _Trunk_Full and Wood_*_Branch_* item matches (a tag, else an explicit Id matcher - today Wood_Apple_Branch_Long
      and Wood_Ice_Branch_Long, whose own Tags list only their Family); no new id collides with a vanilla one.
      The server jar still has BlockConditionInteraction$BlockIdMatcher.tag and SimpleBlockInteraction.useLatestTarget.
    - Residual (the closest the engine allows, documented): ONE swing that hits a mob AND whose block target is wood (a mob standing in
      front of a log within reach while the crosshair ray reaches the log) uses the chopping cadence - the hit-scan and the block break
      are two parallel branches of one vanilla swing and the entity branch cannot tell the block branch that it hit something. A swing
      that hits only mobs / air never does. Weapon axes (Weapon_Axe_* / Weapon_Battleaxe_*) use other roots and are untouched.
      The pickaxe keeps the 0.2.3 design (faster pickaxe hits on mobs stay accepted - LOCKED 2026-09-25).
  CONFIG (trees.properties, once, in TreeCfg.upgrade when the file has no feller.logs key; the 0.2.1 / 0.2.3 pattern: ISO-8859-1 text, exact
    key and value, one TreeCfg.writeAtomic, settings parsed from exactly the new content): the untouched old default lines
    Foraging.FFeller.max=5 -> 6 and Acrobatics.RDouble.B=150 -> 500 (custom values kept + a warning); the 0.2.4 block (comments +
    feller.logs=1,2,4,5,6,10) is appended; a file without Acrobatics.RDodge.* lines (written by 0.2.1-0.2.3) also gets the Quick Dodge
    lines. feller.cooldownSec, Mining.MSpeed.per, Foraging.FSpeed2.per are NOT touched (Skyy's rule: a file on the old value keeps it
    until edited). Server Setup: new row feller.logs "Tree Feller logs per level" (abilities, text, live, danger; check
    TreeKit.checkFellerLogs: 1-20 whole numbers 1-256, each at least the one before; asks first above the safety cap); feller.maxPerLayer
    is now "Tree Feller safety cap". config:def 25 -> 26 rows. Config history keeps 10 old versions per file (KEEP 20 -> 10).
  UNVERIFIED (needs Skyy's in-game test): the client runs the generated chop chain like the server (BlockCondition + TriggerCooldown
    are vanilla, client-known interaction types - the seed and fire-trap assets use them - but this combination is new); the wood tags
    reach the client's block data; no rubber-banding on the first fast swing; the exact cadence (the mid-swing restart runs on the
    server's tick, like vanilla's own cooldown); the mixed mob + log swing (residual above); the one-time chat line with a real player;
    the new rows on the SkyyMenu Server Setup page; the player-file migration on the live world (none of the live world's files has
    Double Jump / Sprinter / Tree Feller levels today - checked read-only 2026-09-28).
  CHECKED in a bare JVM (2026-09-28, scratch harness under tools/dev/scratch/r9-trees, deleted afterwards; 162 checks, 0 fails): all 33
    classes load under -Xverify:all; a fresh start writes exactly DEFAULTS (feller.logs, FFeller max 6 without per / base, Quick Dodge S5,
    Double Jump S7 B 500, no Sprinter) and a second load leaves it byte for byte; a copy of the LIVE world's trees.properties (a 0.2 file
    upgraded by 0.2.1 / 0.2.2) gets exactly 4 changed lines (the kept 0.2.3 MSpeed / FSpeed per migration + FFeller.max 6 + RDouble.B
    500), feller.cooldownSec=5 and FSpeed2.per=0.02 kept, feller.logs + swing.enabled appended, no second Quick Dodge block; a file the
    edited 0.2.3 wrote, a pure 0.2 file and custom max / B values upgrade as described (custom kept), a second load changes nothing;
    Feller values 0,1,2,4,5,6,10,10,10 for levels 0-8, the safety cap and a custom / broken table; dodge.acrobatics = Quick Dodge +
    Evasion, Acrobatics speed = Fleet Foot + Windrunner; player files read by 0.2.4 AND by the edited 0.2.3 build (same file, same fake
    skill levels): Double Jump 3 + Sprinter 4 -> Tokens +1 and Dust + Sprinter's 18,000 exactly, credit 3,150, off flags kept, Foraging
    unchanged, saved as v=2 without RSpeed2, re-read without a second migration, note taken once, respec clears the credit (Dust =
    earned); the 0.2 key RDodge and "RDodge" in off -> Double Jump (balance identical to 0.2.3); RDouble wins over RDodge; a file with
    nothing to migrate stays untouched; a v=2 file with Quick Dodge is read as is; Double Jump 10 + Sprinter 10 -> credit 708,750 and
    Sprinter's 1,012,500 Dust back; TreeKit checks (feller.logs refusals, ask above the cap, FFeller per / base / max asks, Sprinter
    lines ask); the kit: KEEP 10, defaults read back, feller.logs asks first (danger), a bad list is refused, a set is applied by the
    kit's reload and writes only its line, export all -> import preview = nothing to change; the jar's chop chain walked again for tiers
    0-40 (wood periods 0.3465 .. 0.28 (+25%) .. 0.25 (+40%), everything else 0.35, tier 0 = vanilla) and the pickaxe tree unchanged.
  TEST (in game): the build report's numbered steps - server log lines, Tree Feller 1/2/4/5/6/10 on a wide tree, the Acrobatics S5 / S7
    cards, Double Jump from S7, a hatchet on wood vs a mob vs stone, weapon axes and the pickaxe unchanged, the Server Setup rows, an
    old test file migrating once, respec.

=== SkyyTrees 0.2.3 notes (history; still true unless 0.2.4 above says otherwise) ===
0.2.3 = research/Swing-Speed-Spec.md.''')
rep('''Run:   python build_skyytrees_0.2.3.py            -> SkyyTrees/SkyyTrees-0.2.3.jar
       python build_skyytrees_0.2.3.py --deploy   -> also Mods/SkyyTrees.jar''', '''Run:   python build_skyytrees_0.2.4.py            -> SkyyTrees/SkyyTrees-0.2.4.jar
       python build_skyytrees_0.2.4.py --deploy   -> also Mods/SkyyTrees.jar''')
rep('VERSION = "0.2.3"', 'VERSION = "0.2.4"')

# ================================================================ nodes: Double Jump -> tier III slot 7, Quick Dodge back, Feller max 6
rep('''  ("RDouble", "Double Jump", DJ_ICON, "DJUMP", 10, 0.05, 0.5, "Jump once more in mid-air at %V of your jump height", ADJ, "", ""),
  ("RStamina2", "Marathon", "Food_Pie_Apple", "STA", 15, 0.2, 0, "+%V max Stamina - adds to Second Wind", ON, "", ""),
  ("RSpeed2", "Sprinter", "Armor_Leather_Light_Legs", "RSPD", 10, 0.005, 0, "+%V move speed - adds to Fleet Foot", AFLAT + " - always on", "", ""),''',
    '''  # 0.2.4 LOCKED Skyy 2026-09-25 (research/Double-Jump-Spec.md): Quick Dodge is back in tier II slot 5 (the 0.2 row, verbatim)
  ("RDodge", "Quick Dodge", "Ingredient_Feathers_Blue", "RDODGE", 10, 0.01, 0, "+%V dodge push", ADODGE, "", ""),
  ("RStamina2", "Marathon", "Food_Pie_Apple", "STA", 15, 0.2, 0, "+%V max Stamina - adds to Second Wind", ON, "", ""),
  # 0.2.4 LOCKED Skyy 2026-09-25: Double Jump in tier III slot 7 (Acrobatics 20), replacing Sprinter (RSpeed2); stamina stays 2 (SkyySkills)
  ("RDouble", "Double Jump", DJ_ICON, "DJUMP", 10, 0.05, 0.5, "Jump once more in mid-air at %V of your jump height", ADJ, "", ""),''')
rep('''  ("RDodge2", "Evasion", "Glider", "RDODGE", 10, 0.01, 0, "+%V dodge push", ADODGE, "", ""),''',
    '''  ("RDodge2", "Evasion", "Glider", "RDODGE", 10, 0.01, 0, "+%V dodge push - adds to Quick Dodge", ADODGE, "", ""),''')
rep('''"+%V move speed - adds to Sprinter", AFLAT + " - always on", "", ""),''', '''"+%V move speed - adds to Fleet Foot", AFLAT + " - always on", "", ""),''')
rep('''  ("FSpeed", "Chopping Speed", "Tool_Hatchet_Iron", "SWING", 25, 0.01, 0, "+%V hatchet swing speed", "Less wait between hatchet swings - more logs per second (any hatchet, also on mobs)", "", ""),''',
    '''  # 0.2.4: the HARD RULE is built - the shorter wait only applies when the swing chops wood (Skyy_Tree_Chop_Wood); mobs keep vanilla speed.
  ("FSpeed", "Chopping Speed", "Tool_Hatchet_Iron", "SWING", 25, 0.01, 0, "+%V hatchet swing speed on wood", "Less wait between hatchet swings on wood (logs, branches, wood blocks) - hits on mobs and other blocks keep the normal speed", "", ""),''')
rep('''  ("FFeller", "Tree Feller", "Tool_Hatchet_Adamantite", "FELLER", 5, 1.0, 0.0,''',
    '''  # 0.2.4 LOCKED Skyy 2026-09-25 (research/Tree-Fall-Spec.md): 6 levels = feller.logs 1, 2, 4, 5, 6, 10 (per / base are no longer read)
  ("FFeller", "Tree Feller", "Tool_Hatchet_Adamantite", "FELLER", 6, 1.0, 0.0,''')
rep('''        assert mx == SLOT_MAX[s], (tn, nid)''',
    '''        assert mx == SLOT_MAX[s] or (nid == "FFeller" and mx == 6), (tn, nid)   # 0.2.4: only Tree Feller has 6 levels''')
rep('''assert _tot(("RSpeed", "RSpeed2", "RSpeed3")) == 0.2 and''', '''assert _tot(("RSpeed", "RSpeed3")) == 0.15 and''')
rep('''assert _tot(("RDodge2",)) == 0.1 and''', '''assert _tot(("RDodge", "RDodge2")) == 0.2 and''')
rep('''# 0.2.1: Double Jump sits exactly where Quick Dodge sat (same index, same Token / Dust cost), 55% at level 1, 100% at level 10
_RD = [r for r in ROWS if r["id"] == "RDouble"]
assert len(_RD) == 1 and not [r for r in ROWS if r["id"] == "RDodge"]
_RD = _RD[0]
assert TREES[_RD["t"]] == "Acrobatics" and _RD["s"] == 5 and _RD["tier"] == 2 and _RD["max"] == 10 and _RD["B"] == 150 and _RD["tok"] == 1
assert abs(_RD["base"] + _RD["per"] * 1 - 0.55) < 1e-9 and abs(_RD["base"] + _RD["per"] * 10 - 1.0) < 1e-9 and T["I_RDOUBLE"] == "52"
_FF = [r for r in ROWS if r["id"] == "FFeller"][0]
assert _FF["per"] == 1.0 and _FF["base"] == 0.0 and _FF["max"] == 5 and TREES[_FF["t"]] == "Foraging" and _FF["s"] == 12''',
    '''# 0.2.4 LOCKED Skyy 2026-09-25: Double Jump in tier III slot 7 (where Sprinter was: B 500, 1 token), 55% at level 1, 100% at level 10;
# Quick Dodge back in tier II slot 5 (B 150, 1 token) - the player-file migration (TreeStore.readFile) relies on exactly these indexes
_RD = [r for r in ROWS if r["id"] == "RDouble"]
_RQ = [r for r in ROWS if r["id"] == "RDodge"]
assert len(_RD) == 1 and len(_RQ) == 1 and not [r for r in ROWS if r["id"] == "RSpeed2"]
_RD = _RD[0]
_RQ = _RQ[0]
assert TREES[_RD["t"]] == "Acrobatics" and _RD["s"] == 7 and _RD["tier"] == 3 and _RD["max"] == 10 and _RD["B"] == 500 and _RD["tok"] == 1
assert abs(_RD["base"] + _RD["per"] * 1 - 0.55) < 1e-9 and abs(_RD["base"] + _RD["per"] * 10 - 1.0) < 1e-9 and T["I_RDOUBLE"] == "54"
assert TREES[_RQ["t"]] == "Acrobatics" and _RQ["s"] == 5 and _RQ["tier"] == 2 and _RQ["max"] == 10 and _RQ["B"] == 150 and _RQ["tok"] == 1
assert T["I_RDODGE"] == "52" and _RQ["per"] == 0.01 and _RQ["icon"] == "Ingredient_Feathers_Blue"
_FF = [r for r in ROWS if r["id"] == "FFeller"][0]
assert _FF["max"] == 6 and TREES[_FF["t"]] == "Foraging" and _FF["s"] == 12 and _FF["B"] == 150000 and _FF["tok"] == 3
# 0.2.4 LOCKED Skyy 2026-09-25 (research/Tree-Fall-Spec.md): extra logs at Tree Feller levels 1-6. Skyy locked 1 (level 1), 6 (level 5) and
# 10 (level 6); levels 2-4 are the whole-log steps of 1 + (level - 1) x 1.25 rounded half up (2.25 -> 2, 3.5 -> 4, 4.75 -> 5)
FELLER_LOGS = [1, 2, 4, 5, 6, 10]
assert FELLER_LOGS[0] == 1 and FELLER_LOGS[4] == 6 and FELLER_LOGS[5] == 10 and len(FELLER_LOGS) == _FF["max"]
assert [int(1 + (lv - 1) * 1.25 + 0.5) for lv in (2, 3, 4)] == FELLER_LOGS[1:4]
FELLER_LOGS_CSV = ",".join(str(x) for x in FELLER_LOGS)
T["FELLER_DEF"] = "new int[] { " + ", ".join(str(x) for x in FELLER_LOGS) + " }"
T["FELLER_CSV"] = FELLER_LOGS_CSV''')

# ================================================================ default trees.properties + once-only blocks
rep('''      "# Tree Feller: breaks logs beside the cut on the SAME Y level only. Hytale itself fells the tree once its whole layer is cut.",
      "# LOCKED Skyy 2026-09-25 (research/Tree-Fall-Spec.md): extra logs by level = 1, 2, 4, 5, 6, 10.",
      "# Level 6 jumps to 10 so a very large tree is not broken as a whole layer (that could crash). Cooldown 3 s (was 5).",
      "# This build still uses base + per x level, and the max level breaks every log on that level up to feller.maxPerLayer.",
      "# The locked table replaces that formula in the next Trees build. A file still on feller.cooldownSec=5 keeps 5 until edited.",
      "feller.cooldownSec=3", "feller.maxPerLayer=64",''',
    '''      "# Tree Feller: breaks logs beside the cut on the SAME Y level only. Hytale itself fells the tree once its whole layer is cut.",
      "# LOCKED Skyy 2026-09-25 (research/Tree-Fall-Spec.md): feller.logs = extra logs at node level 1, 2, 3 ... = 1, 2, 4, 5, 6, 10.",
      "# Level 6 jumps to 10 so a very large tree is not broken as a whole layer (that could crash). A level above the list uses its",
      "# last number. Cooldown 3 s (was 5; a file still on feller.cooldownSec=5 keeps 5 until edited).",
      "# feller.maxPerLayer = safety cap: one Tree Feller never breaks more logs than this, whatever feller.logs says.",
      "feller.logs=" + FELLER_LOGS_CSV,
      "feller.cooldownSec=3", "feller.maxPerLayer=64",''')
rep('''      "swing.enabled=true",
      "# Aggregated 'Tree bonus: ...' chat line''', '''      "# 0.2.4: the hatchet (Chopping Speed) only swings faster when the swing chops wood - hits on mobs and other blocks keep vanilla speed.",
      "swing.enabled=true",
      "# Aggregated 'Tree bonus: ...' chat line''')
rep('''      "# ---- nodes: <Tree>.<Id>.max / per / B / tokens / enabled (Vein Burst + Tree Feller also base; lists: items / crops) ----",''',
    '''      "# ---- nodes: <Tree>.<Id>.max / per / B / tokens / enabled (Vein Burst + Double Jump also base; lists: items / crops) ----",''')
rep('''      "# (up to base + per x level), logs on the cut level for Tree Feller (this build: base + per x level; max level = the whole layer;",
      "# LOCKED 2026-09-25 table is 1, 2, 4, 5, 6, 10 extra logs - applied in the next Trees build),",
      "# a fraction of your own jump height for Double Jump (base + per x level); Master Chef: per = chance per level above 1."]''',
    '''      "# (up to base + per x level), a fraction of your own jump height for Double Jump (base + per x level); Master Chef: per = chance",
      "# per level above 1. Tree Feller has no per / base (0.2.4): its logs per level are feller.logs above."]''')
rep('''    out.append(k + "per=%s" % repr(float(r["per"])))
    if KINDS[r["kind"]] in ("VEIN", "FELLER", "DJUMP"): out.append(k + "base=%s" % repr(float(r["base"])))''',
    '''    if KINDS[r["kind"]] != "FELLER": out.append(k + "per=%s" % repr(float(r["per"])))   # 0.2.4: Tree Feller reads feller.logs
    if KINDS[r["kind"]] in ("VEIN", "DJUMP"): out.append(k + "base=%s" % repr(float(r["base"])))''')
rep('''ADD021DJ = ["# ---------- SkyyTrees 0.2.1 (added once to a 0.2 file): Double Jump replaced Quick Dodge in Acrobatics S5 ----------",
            "# The old Acrobatics.RDodge.* lines are no longer read (their numbers do not carry over to Double Jump) - you can delete them."]''',
    '''ADD021DJ = ["# ---------- SkyyTrees 0.2.1+ (added once to a 0.2 file): Double Jump - Acrobatics S7 (tier III, where Sprinter was) since 0.2.4 ----------",
            "# Quick Dodge (the Acrobatics.RDodge.* lines) is back in S5 since 0.2.4. The Acrobatics.RSpeed2.* lines (Sprinter) are no longer read."]''')
rep('''    "# levels 1-4 = 1-4 more logs (base + per x level), the max level = every log of that tree on that level, up to feller.maxPerLayer.",''',
    '''    "# how many logs: feller.logs (0.2.4 block below; since 0.2.4 the Foraging.FFeller.per / base lines are no longer read).",''')
rep('''assert "Acrobatics.RDodge." not in DEFAULTS and "Acrobatics.RDodge." not in ADD02 and "Acrobatics.RDodge2.max=10" in DEFAULTS''',
    '''assert "Acrobatics.RDodge.max=10" in DEFAULTS and "Acrobatics.RDodge.B=150" in ADD02 and "Acrobatics.RDodge2.max=10" in DEFAULTS
assert "Acrobatics.RSpeed2." not in DEFAULTS and "Acrobatics.RSpeed2." not in ADD02 and "Acrobatics.RDouble.B=500" in DEFAULTS
assert "# Acrobatics S7 Double Jump (tier III)" in DEFAULTS and "# Acrobatics S5 Quick Dodge (tier II)" in DEFAULTS''')
rep('''assert "Foraging.FFeller.per=1.0" in DEFAULTS and "Foraging.FFeller.base=0.0" in DEFAULTS and "feller.cooldownSec=3" in DEFAULTS''',
    '''assert "Foraging.FFeller.per" not in DEFAULTS and "Foraging.FFeller.base" not in DEFAULTS and "feller.cooldownSec=3" in DEFAULTS
assert "Foraging.FFeller.max=6" in DEFAULTS and DEFAULTS.count("feller.logs=" + FELLER_LOGS_CSV + "\\n") == 1''')
after('''assert "Mining.MHeavy.per=0.02" in DEFAULTS and "# Foraging S10 Heavy Hatchet (tier V)" in DEFAULTS and "Chopping Speed II" not in DEFAULTS''', '''
# 0.2.4: appended ONCE to any older file (no feller.logs key), right after the untouched old default lines Foraging.FFeller.max=5 /
# Acrobatics.RDouble.B=150 were rewritten in place to 6 / 500 (TreeCfg.migrate024). It only ADDS keys. A file without Acrobatics.RDodge.*
# lines (written by 0.2.1-0.2.3; a 0.2 file still has its own) also gets the Quick Dodge node lines (ADD024DODGE).
ADD024 = "\\n".join([
    "# ---------- SkyyTrees 0.2.4 (added once): Tree Feller table, Double Jump in tier III ----------",
    "# Tree Feller: feller.logs = extra logs at node level 1, 2, 3 ... (LOCKED Skyy 2026-09-25: 1, 2, 4, 5, 6, 10; a level above the",
    "# list uses its last number). Foraging.FFeller.per / base are no longer read. The old default Foraging.FFeller.max=5 was changed",
    "# to 6 (a custom max was kept). feller.maxPerLayer is only a safety cap now.",
    "feller.logs=" + FELLER_LOGS_CSV,
    "# Double Jump moved to Acrobatics S7 (tier III, where Sprinter was): the old default Acrobatics.RDouble.B=150 was changed to 500",
    "# (the tier III price; players keep their levels and pay no extra Dust). Quick Dodge is back in S5. The Acrobatics.RSpeed2.* lines",
    "# (Sprinter) are no longer read - you can delete them."]) + "\\n"
ADD024DODGE = "\\n".join([_l for _r in ROWS if _r["id"] == "RDodge" for _l in node_lines(_r)]) + "\\n"
assert all(ord(ch) < 128 for ch in ADD024 + ADD024DODGE)
assert not [l for l in ADD024.splitlines() if not l.startswith("#") and l != "feller.logs=" + FELLER_LOGS_CSV]
assert "Acrobatics.RDodge.max=10" in ADD024DODGE and "RDouble" not in ADD024DODGE and "Acrobatics.RDodge.per=0.01" in ADD024DODGE''')

# ================================================================ 0.2.4 HARD RULE: hatchet swing speed only when the swing chops wood
before('''assert len(SWING_FILES) == 2 * SWING_MAX + 4''', r'''    # ---- 0.2.4 HARD RULE (Skyy 2026-09-25, OPEN-QUESTIONS "Swing speed"): the hatchet bonus only when the swing chops WOOD ----
    # 0.2.3 shortened the cooldown at the START of every hatchet swing, so mob hits came faster too. 0.2.4 decides at the moment the swing
    # breaks its block: a GENERATED copy of the vanilla swing (Skyy_Tree_Chop = Hatchet_Chop with its one block-break step pointed at
    # Skyy_Tree_Chop_Wood) runs a BlockCondition on the block the swing hits (UseLatestTarget like vanilla BreakBlock; wood tags) at
    # T_HIT (0.083 + 0.05 = 0.133 s): wood -> TriggerCooldown (tier period - T_HIT), anything else (air / a mob only / stone / furniture)
    # -> TriggerCooldown (0.35 - T_HIT) = exactly the vanilla cadence; then the vanilla Block_Break. A tier player's swing first resets the
    # cooldown to the vanilla 0.35 (so nothing from a fast wood swing carries into the next swing); players without a chop tier take the
    # vanilla Interaction Hatchet_Attack untouched. Only our own JSON goes into the jar (generated from Assets.zip read in memory).
    import copy as _copy
    CHOP_IDS = [swing_id("Chop", k) for k in range(1, SWING_MAX + 1)]
    CHOP_NEW = ["Skyy_Tree_Chop_Chain", "Skyy_Tree_Chop", "Skyy_Tree_Chop_Wood"]
    _ha = _rd(_one(V_INT, "Hatchet_Attack", "interaction"))
    _hc = _rd(_one(V_INT, "Hatchet_Chop", "interaction"))
    _one(V_INT, "Block_Break", "interaction")
    if sorted(_ha) != ["ChainingAllowance", "Next", "Type"] or _ha["Type"] != "Chaining" or _ha["Next"] != ["Hatchet_Chop"]:
        raise SystemExit("chop self-check: vanilla Hatchet_Attack is no longer {Chaining, ChainingAllowance, Next [Hatchet_Chop]}: " + json.dumps(_ha))
    _nx = _hc.get("Next")
    if _hc.get("Type") != "Simple" or not isinstance(_nx, dict) or _nx.get("Type") != "Parallel" or not isinstance(_nx.get("Interactions"), list):
        raise SystemExit("chop self-check: vanilla Hatchet_Chop is no longer Simple -> Parallel: " + json.dumps(_hc)[:300])
    def _isblk(b):
        return (isinstance(b, dict) and isinstance(b.get("Interactions"), list) and len(b["Interactions"]) == 1
                and isinstance(b["Interactions"][0], dict) and b["Interactions"][0].get("Next") == "Block_Break")
    _blk = [b for b in _nx["Interactions"] if _isblk(b)]
    if len(_blk) != 1:
        raise SystemExit("chop self-check: Hatchet_Chop no longer has exactly one [Simple -> Block_Break] branch: " + json.dumps(_nx)[:400])
    _st = _blk[0]["Interactions"][0]
    if _st.get("Type") != "Simple" or set(_st) - set(["Type", "$Comment", "RunTime", "Next"]):
        raise SystemExit("chop self-check: the block-break step of Hatchet_Chop changed: " + json.dumps(_st))
    if json.dumps(_hc).count('"Block_Break"') != 1:
        raise SystemExit("chop self-check: Hatchet_Chop names Block_Break more than once - the wood check must sit in front of its only block break")
    T_HIT = round(float(_hc.get("RunTime", 0) or 0) + float(_st.get("RunTime", 0) or 0), 4)
    if not (0.0 < T_HIT <= min(SWING_CD) - 0.05):
        raise SystemExit("chop self-check: the block break now happens %.4f s into the swing - no room for the tier cooldowns" % T_HIT)
    CHOP_CD = [round(SWING_CD[k] - T_HIT, 4) for k in range(0, SWING_MAX + 1)]
    assert all(c >= 0.05 for c in CHOP_CD) and all(abs(T_HIT + CHOP_CD[k] - SWING_CD[k]) < 0.00011 for k in range(SWING_MAX + 1)), CHOP_CD
    assert all(T_HIT + c >= _dur("Hatchet_Chop") - 1e-9 for c in CHOP_CD)   # never a next swing while this one still runs
    # the tags AssetExtraInfo$Data.putTags builds from an item's "Tags": {"Type": ["Wood", "Trunk"], ...} (key, value and key=value)
    CHOP_TAGS = ["Type=Wood", "Type=Trunk", "Type=Branch", "Type=Tree", "BranchType=Long", "BranchType=Short", "BranchType=Corner"]
    # every natural trunk and branch must match: by a tag (its own "Tags", else the Parent's - whether the engine MERGES a child's Tags
    # with the Parent's is not verified, so the strict reading is used), else by an explicit Id matcher (e.g. Wood_Apple_Branch_Long and
    # Wood_Ice_Branch_Long list only their Family tag)
    def _tags(i, depth=0):
        if i not in V_ITEM or depth > 20: return {}
        _d = _rd(V_ITEM[i][0])
        if isinstance(_d.get("Tags"), dict): return _d["Tags"]
        return _tags(_d.get("Parent"), depth + 1) if _d.get("Parent") else {}
    def _hit(tg):
        return bool(set("%s=%s" % (kk, v) for kk, vv in tg.items() for v in (vv if isinstance(vv, list) else [])) & set(CHOP_TAGS))
    _trunks = sorted(i for i in V_ITEM if re.match(r"^Wood_[A-Za-z_]+_Trunk(_Full)?$", i))
    _branches = sorted(i for i in V_ITEM if re.match(r"^Wood_[A-Za-z_]+_Branch_(Long|Short|Corner)$", i))
    CHOP_IDS_EXTRA = [i for i in _trunks + _branches if not _hit(_tags(i))]
    if len(_trunks) < 60 or len(_branches) < 60 or len(CHOP_IDS_EXTRA) > 12:
        raise SystemExit("chop self-check: natural wood without a matcher tag (%d trunks, %d branches): %s" % (len(_trunks), len(_branches), CHOP_IDS_EXTRA))
    CHOP_COVER = (len(_trunks), len(_branches), len(CHOP_IDS_EXTRA))
    def _cd(c, nxt): return {"Type": "TriggerCooldown", "Cooldown": {"Id": "Hatchet_Attack", "Cooldown": c}, "Next": nxt}
    def _csplit(lo, hi):
        if lo == hi: return _cd(CHOP_CD[lo], "Block_Break")
        mid = (lo + hi + 1) // 2
        return {"Type": "EffectCondition", "Match": "None", "EntityEffectIds": CHOP_IDS[mid - 1:hi], "Next": _csplit(lo, mid - 1), "Failed": _csplit(mid, hi)}
    chop_start = {"Type": "EffectCondition", "Match": "None", "EntityEffectIds": list(CHOP_IDS), "Next": "Hatchet_Attack",
                  "Failed": _cd(SWING_BASE, "Skyy_Tree_Chop_Chain")}
    chop_chain = {"Type": "Chaining", "ChainingAllowance": _ha["ChainingAllowance"], "Next": ["Skyy_Tree_Chop"]}
    chop_swing = _copy.deepcopy(_hc)
    _cb = [b for b in chop_swing["Next"]["Interactions"] if _isblk(b)]
    assert len(_cb) == 1
    _cb[0]["Interactions"][0]["Next"] = "Skyy_Tree_Chop_Wood"
    chop_wood = {"Type": "BlockCondition", "UseLatestTarget": True, "Matchers": [{"Block": {"Tag": t}} for t in CHOP_TAGS] + [{"Block": {"Id": i}} for i in CHOP_IDS_EXTRA],
                 "Next": {"Type": "EffectCondition", "Match": "None", "EntityEffectIds": list(CHOP_IDS),
                          "Next": _cd(CHOP_CD[0], "Block_Break"), "Failed": _csplit(1, SWING_MAX)},
                 "Failed": _cd(CHOP_CD[0], "Block_Break")}
    # the copy differs from vanilla in exactly that one Next
    if json.dumps(chop_swing).replace('"Skyy_Tree_Chop_Wood"', '"Block_Break"') != json.dumps(_hc) or json.dumps(chop_swing).count("Skyy_Tree_Chop_Wood") != 1:
        raise SystemExit("chop self-check: the generated swing differs from vanilla Hatchet_Chop in more than its block-break Next")
    # walk every tier through the start node and the wood node (EffectCondition Match None fails when ANY listed effect is active)
    def _cwalk(node, have):
        while isinstance(node, dict) and node.get("Type") == "EffectCondition":
            node = node["Failed"] if any(e in have for e in node["EntityEffectIds"]) else node["Next"]
        return node
    for k in range(0, SWING_MAX + 1):
        _have = set([CHOP_IDS[k - 1]]) if k else set()
        _s0 = _cwalk(chop_start, _have)
        if k == 0:
            if _s0 != "Hatchet_Attack": raise SystemExit("chop self-check: tier 0 does not reach the vanilla Hatchet_Attack: %r" % (_s0,))
        elif not (isinstance(_s0, dict) and _s0["Type"] == "TriggerCooldown" and _s0["Cooldown"] == {"Id": "Hatchet_Attack", "Cooldown": SWING_BASE}
                  and _s0["Next"] == "Skyy_Tree_Chop_Chain"):
            raise SystemExit("chop self-check: tier %d start reaches %r" % (k, _s0))
        _w = _cwalk(chop_wood["Next"], _have)
        if not (isinstance(_w, dict) and _w["Type"] == "TriggerCooldown" and _w["Next"] == "Block_Break" and _w["Cooldown"]["Id"] == "Hatchet_Attack"
                and _w["Cooldown"]["Cooldown"] == CHOP_CD[k]):
            raise SystemExit("chop self-check: tier %d on wood reaches %r" % (k, _w))
    assert chop_wood["Failed"] == _cd(CHOP_CD[0], "Block_Break") and CHOP_CD[0] == round(SWING_BASE - T_HIT, 4)
    for _i in CHOP_NEW:
        if _i in V_INT or _i in V_ROOT or _i in V_EFF: raise SystemExit("chop self-check: vanilla already has an asset " + _i)
    SWING_FILES["Server/Item/Interactions/SkyyTrees/%s.json" % swing_tree_id("Chop")] = json.dumps(chop_start, indent=2)   # replaces the 0.2.3 tree
    SWING_FILES["Server/Item/Interactions/SkyyTrees/Skyy_Tree_Chop_Chain.json"] = json.dumps(chop_chain, indent=2)
    SWING_FILES["Server/Item/Interactions/SkyyTrees/Skyy_Tree_Chop.json"] = json.dumps(chop_swing, indent=2)
    SWING_FILES["Server/Item/Interactions/SkyyTrees/Skyy_Tree_Chop_Wood.json"] = json.dumps(chop_wood, indent=2)
''')
rep('''assert len(SWING_FILES) == 2 * SWING_MAX + 4''', '''assert len(SWING_FILES) == 2 * SWING_MAX + 4 + 3   # 0.2.4: + the chop chain, swing copy and wood check''')
after('''    raise SystemExit("swing self-check: InteractionTypeUtils.getDefaultCooldown no longer loads float 0.35 - every tier number would be wrong:\\n" + _gdc)''', '''
# 0.2.4 chop check: the engine still has what the generated chop chain uses (BlockCondition tag matchers, SimpleBlockInteraction
# UseLatestTarget - BlockConditionInteraction's codec builds on SimpleBlockInteraction.CODEC, bytecode 2026-09-28)
_CFGC = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.client."
for _c, _f in (("BlockConditionInteraction$BlockIdMatcher", "tag"), ("BlockConditionInteraction$BlockIdMatcher", "tagIndex"),
               ("BlockConditionInteraction", "matchers"), ("SimpleBlockInteraction", "useLatestTarget"), ("TriggerCooldownInteraction", "cooldown")):
    try: pool.get(_CFGC + _c).getDeclaredField(_f)
    except Exception: raise SystemExit("chop self-check: %s.%s is gone - the wood-only hatchet chain needs a look" % (_c, _f))
print("chop: hatchet bonus only on wood - block break at %.3f s, wood tiers %.4f..%.4f s after it, vanilla rest %.4f s, %d trunks + %d branches (%d by id)"
      % (T_HIT, CHOP_CD[SWING_MAX], CHOP_CD[1], CHOP_CD[0], CHOP_COVER[0], CHOP_COVER[1], CHOP_COVER[2]))''')

# ================================================================ TreeCfg: feller.logs, 0.2.4 migration
after('''F(cfg, "public static final String ADD023 = " + json.dumps(ADD023) + ";")''', '''
F(cfg, "public static final String ADD024 = " + json.dumps(ADD024) + ";")
F(cfg, "public static final String ADD024DODGE = " + json.dumps(ADD024DODGE) + ";")''')
rep('''"int FELLER_ALL = 64", "boolean FELLED_NODES = true",''', '''"int FELLER_ALL = 64", "int[] FELLER_LOGS = @FELLER_DEF@", "boolean FELLED_NODES = true",''')
before('''M(cfg, r"""
public static long rate(int t) {''', '''# 0.2.4 feller.logs: extra logs at Tree Feller level 1, 2, 3 ... (1-20 whole numbers 1-256, each at least the one before; else the default)
M(cfg, r"""
public static int[] logs(String v) {
  int[] def = @FELLER_DEF@;
  String[] xs = split(v);
  if (xs.length < 1 || xs.length > 20) { warn("feller.logs needs 1 to 20 whole numbers - using @FELLER_CSV@"); return def; }
  int[] r = new int[xs.length];
  try {
    for (int i = 0; i < xs.length; i++) {
      r[i] = Integer.parseInt(xs[i]);
      if (r[i] < 1 || r[i] > 256 || (i > 0 && r[i] < r[i - 1])) { warn("feller.logs must be whole numbers 1-256, each at least the one before - using @FELLER_CSV@"); return def; }
    }
  } catch (Throwable t) { warn("feller.logs is not a list of whole numbers - using @FELLER_CSV@"); return def; }
  return r;
}""")
# extra logs at Tree Feller level lv: the table entry (a level above the table uses its last number), capped at feller.maxPerLayer
M(cfg, r"""
public static int fellerLogs(int lv) {
  if (lv <= 0) return 0;
  int[] t = FELLER_LOGS;
  if (t == null || t.length == 0) return 0;
  int n = t[(lv > t.length ? t.length : lv) - 1];
  int cap = FELLER_ALL;
  return n > cap ? cap : n;
}""")
''')
rep('''  FELLER_ALL = (int) clampL(lng(p, "feller.maxPerLayer", 64L), 1L, 256L);''', '''  FELLER_ALL = (int) clampL(lng(p, "feller.maxPerLayer", 64L), 1L, 256L);
  FELLER_LOGS = logs(str(p, "feller.logs", "@FELLER_CSV@"));''')
before('''# ONE atomic write for everything an older trees.properties is missing''', '''# 0.2.4: the untouched old default lines Foraging.FFeller.max=5 -> 6 (Tree Feller levels 1-6) and Acrobatics.RDouble.B=150 -> 500 (Double
# Jump's new tier III slot) (n[0] = lines changed); custom values are kept (upgrade warns about them)
M(cfg, r"""
public static String migrate024(String text, int[] n) {
  String[] ls = text.split("\\n", -1);
  StringBuilder sb = new StringBuilder(text.length() + 16);
  for (int i = 0; i < ls.length; i++) {
    String ln = ls[i];
    String r = migrateLine(ln, "Foraging.FFeller.max", "5", "6");
    if (r == null) r = migrateLine(ln, "Acrobatics.RDouble.B", "150", "500");
    if (r != null) { ln = r; n[0] = n[0] + 1; }
    if (i > 0) sb.append('\\n');
    sb.append(ln);
  }
  return sb.toString();
}""")
''')
rep('''  boolean need023 = p.getProperty("swing.enabled") == null;
  if (!need02 && !needDj && !needFel && !need023) return p;''', '''  boolean need023 = p.getProperty("swing.enabled") == null;
  boolean need024 = p.getProperty("feller.logs") == null;
  boolean needDodge = need024 && !need02 && !hasPrefix(p, "Acrobatics.RDodge.");
  if (!need02 && !needDj && !needFel && !need023 && !need024) return p;''')
rep('''    if (need023) text = migrateSwing(text, n2);''', '''    if (need023) text = migrateSwing(text, n2);
    int[] n3 = new int[1];
    if (need024) text = migrate024(text, n3);''')
rep('''    if (need023) sb.append("\\n").append(ADD023);''', '''    if (need023) sb.append("\\n").append(ADD023);
    if (need024) sb.append("\\n").append(ADD024);
    if (needDodge) sb.append(ADD024DODGE);''')
rep('''      info("updated " + FILE + " for SkyyTrees 0.2.3:"''', '''      info("updated " + FILE + " for SkyyTrees 0.2.4:"''')
rep('''(need023 ? " swing speed (" + n2[0] + " old default Mining Speed / Chopping Speed line(s) changed to per=0.01, swing.enabled added)" : ""));''',
    '''(need023 ? " swing speed (" + n2[0] + " old default Mining Speed / Chopping Speed line(s) changed to per=0.01, swing.enabled added);" : "") + (need024 ? " Tree Feller table + Double Jump in tier III (" + n3[0] + " old default line(s) changed, feller.logs added" + (needDodge ? ", Quick Dodge lines added" : "") + ")" : ""));''')
rep('''      if ("0.02".equals(str(q, "Foraging.FSpeed.per", ""))) q.setProperty("Foraging.FSpeed.per", "0.01");
    }
  }''', '''      if ("0.02".equals(str(q, "Foraging.FSpeed.per", ""))) q.setProperty("Foraging.FSpeed.per", "0.01");
    }
    if (need024) {
      if ("5".equals(str(q, "Foraging.FFeller.max", ""))) q.setProperty("Foraging.FFeller.max", "6");
      if ("150".equals(str(q, "Acrobatics.RDouble.B", ""))) q.setProperty("Acrobatics.RDouble.B", "500");
    }
  }''')
rep('''  if (needFel) {
    String pe = str(q, "Foraging.FFeller.per", "1.0");
    String ba = str(q, "Foraging.FFeller.base", "0.0");
    if (!"1.0".equals(pe) || !"0.0".equals(ba)) warn("Tree Feller custom numbers kept (Foraging.FFeller.per=" + pe + ", base=" + ba + "): since 0.2.1 they count logs on the SAME level as the cut (default per=1.0 base=0.0 = 1, 2, 3, 4 logs; the max level breaks the whole layer)");
  }
  if (needDj && hasPrefix(q, "Acrobatics.RDodge.")) info("Acrobatics.RDodge.* lines in trees.properties are unused since 0.2.1 (Quick Dodge became Double Jump) - you can delete them");''',
    '''  // 0.2.4: Foraging.FFeller.per / base are no longer read (feller.logs), so the 0.2.1 "custom Feller numbers kept" warning is gone
  if (need024) {
    String fm = q.getProperty("Foraging.FFeller.max");
    if (fm != null && !"6".equals(fm.trim())) warn("Foraging.FFeller.max=" + fm.trim() + " kept - Tree Feller levels follow feller.logs since 0.2.4 (1, 2, 4, 5, 6, 10 at levels 1-6; a level above the list uses its last number)");
    String db = q.getProperty("Acrobatics.RDouble.B");
    if (db != null && !"500".equals(db.trim())) warn("Acrobatics.RDouble.B=" + db.trim() + " kept - Double Jump is Acrobatics tier III (S7) since 0.2.4, where the template price is 500");
    if (q.getProperty("Foraging.FFeller.per") != null || q.getProperty("Foraging.FFeller.base") != null) info("Foraging.FFeller.per / base are no longer read (Tree Feller uses feller.logs since 0.2.4) - you can delete them");
    if (hasPrefix(q, "Acrobatics.RSpeed2.")) info("Acrobatics.RSpeed2.* lines (Sprinter) are unused since 0.2.4 (Double Jump took its slot) - you can delete them");
  }''')
rep('''# ONE atomic write for everything an older trees.properties is missing: the 0.2 block (a 0.1 file; it already carries the Double Jump
# lines), the Double Jump block (a 0.2 file), the Tree Feller migration + block (any file without feller.maxPerLayer), the 0.2.3 swing
# migration + block (any file without swing.enabled - research/Swing-Speed-Spec.md 4.2).''',
    '''# ONE atomic write for everything an older trees.properties is missing: the 0.2 block (a 0.1 file; it already carries the Double Jump
# lines), the Double Jump block (a 0.2 file), the Tree Feller migration + block (any file without feller.maxPerLayer), the 0.2.3 swing
# migration + block (any file without swing.enabled - research/Swing-Speed-Spec.md 4.2), the 0.2.4 migration + block (any file without
# feller.logs; + the Quick Dodge lines when a 0.2.1-0.2.3 file has none).''')

# ================================================================ TreeData / TreeStore: player-file layout v=2 + migration
after('''F(dat, "public boolean noteSwing;")   # 0.2.3: the one-time swing-speed chat notice was shown for this profile (file key note.swing=1)''', '''
F(dat, "public long[] credit = new long[%d];" % len(TREES))   # 0.2.4: Dust credit per tree (file <Tree>.dustCredit; the Double Jump move)
F(dat, "public int[] note024 = new int[3];")   # 0.2.4: pending one-time chat line {Double Jump level, Sprinter level, Tree Feller level}
F(dat, "public boolean mig;")   # 0.2.4: read from the 0.2.1-0.2.3 layout and changed - save soon''')
rep('''    // 0.2.1: Acrobatics slot 5 was RDodge (Quick Dodge) in 0.2 - same slot = same Token and Dust cost; an RDouble line always wins
    if (p.getProperty("Acrobatics.RDouble") == null) {
      String ov = p.getProperty("Acrobatics.RDodge");
      if (ov != null) { try { int x = Integer.parseInt(ov.trim()); d.lv[@I_RDOUBLE@] = x < 0 ? 0 : (x > 1000 ? 1000 : x); } catch (Throwable t3) { } }
    }''', '''    // 0.2.4: v=2 = this layout. Without it the file is the 0.2.1-0.2.3 layout: Acrobatics S5 was Double Jump (key RDouble, or the 0.2
    // key RDodge when there is no RDouble line - the 0.2.1 alias) and S7 was Sprinter (RSpeed2). Double Jump keeps its level (now S7),
    // Sprinter is dropped (its token and Dust come back: both are computed from levels), Quick Dodge starts at 0.
    boolean old = !"2".equals(String.valueOf(p.getProperty("v")).trim());
    int spr = 0;
    if (old) {
      d.lv[@I_RDODGE@] = 0;
      if (p.getProperty("Acrobatics.RDouble") == null) {
        String ov = p.getProperty("Acrobatics.RDodge");
        if (ov != null) { try { int x = Integer.parseInt(ov.trim()); d.lv[@I_RDOUBLE@] = x < 0 ? 0 : (x > 1000 ? 1000 : x); } catch (Throwable t3) { } }
      }
      String sv = p.getProperty("Acrobatics.RSpeed2");
      if (sv != null) { try { int x = Integer.parseInt(sv.trim()); spr = x < 0 ? 0 : (x > 1000 ? 1000 : x); } catch (Throwable t4) { } }
    }''')
rep('''          if (i < 0 && "Acrobatics".equals(tn) && "RDodge".equalsIgnoreCase(xs[j].trim())) i = @I_RDOUBLE@;''',
    '''          if (old && "Acrobatics".equals(tn) && "RDodge".equalsIgnoreCase(xs[j].trim())) i = @I_RDOUBLE@;   // the 0.2.1 alias (old layout only)''')
rep('''    d.noteSwing = "1".equals(String.valueOf(p.getProperty("note.swing")).trim());''', '''    d.noteSwing = "1".equals(String.valueOf(p.getProperty("note.swing")).trim());
    for (int tc = 0; tc < @PKG@.TreeDefs.NT; tc++) {
      String cr = p.getProperty(@PKG@.TreeDefs.TREES[tc] + ".dustCredit");
      if (cr != null) { try { long x = Long.parseLong(cr.trim()); d.credit[tc] = x < 0L ? 0L : x; } catch (Throwable t5) { } }
    }
    String nt = p.getProperty("note.r024");
    if (nt != null) {
      String[] ns = nt.split(",");
      for (int j = 0; j < ns.length && j < 3; j++) { try { int x = Integer.parseInt(ns[j].trim()); d.note024[j] = x < 0 ? 0 : x; } catch (Throwable t6) { } }
    }
    // 0.2.4 migration of an old-layout file: the Double Jump levels already bought were paid at the tier II price (Quick Dodge's B, 150);
    // their tier III price (Double Jump's B, 500) is higher, so the difference becomes a Dust credit - no balance goes down. The one-time
    // chat line is kept pending in the file (note.r024) until TreeMsg.note024 shows it.
    if (old) {
      int dj = d.lv[@I_RDOUBLE@];
      int fel = d.lv[@I_FFELLER@];
      if (dj > 0 || spr > 0 || fel > 0) {
        long add = 0L;
        long db = @PKG@.TreeCfg.B[@I_RDOUBLE@] - @PKG@.TreeCfg.B[@I_RDODGE@];
        if (db > 0L) { for (int n = 1; n < dj; n++) { long nn = (long) n; add = add + db * nn * nn * nn; } }
        d.credit[@T_ACROBATICS@] = d.credit[@T_ACROBATICS@] + add;
        d.note024[0] = dj;
        d.note024[1] = spr;
        d.note024[2] = fel;
        d.mig = true;
      }
    }''')
before('''M(sto, r"""
public static synchronized @PKG@.TreeData install(''', '''# 0.2.4: true once after an old-layout file was migrated in readFile (the caller marks the file dirty)
M(sto, r"""
public static synchronized boolean takeMig(@PKG@.TreeData d) {
  if (d == null || !d.mig) return false;
  d.mig = false;
  return true;
}""")
''')
rep('''  if (d != null) return d;
  return install(k, u, readFile(k));''', '''  if (d != null) return d;
  @PKG@.TreeData r = install(k, u, readFile(k));
  if (takeMig(r)) DIRTY.put(k, Boolean.TRUE);   // 0.2.4: a migrated old-layout file is saved (as v=2) within 10 s
  return r;''')
rep('''  p.setProperty("v", "1");''', '''  p.setProperty("v", "2");   // 0.2.4 layout: Double Jump in Acrobatics S7, Quick Dodge in S5''')
rep('''  if (d.noteSwing) p.setProperty("note.swing", "1");''', '''  if (d.noteSwing) p.setProperty("note.swing", "1");
  if (d.note024[0] > 0 || d.note024[1] > 0 || d.note024[2] > 0) p.setProperty("note.r024", d.note024[0] + "," + d.note024[1] + "," + d.note024[2]);''')
rep('''    if (d.respecAt[t] > 0L) p.setProperty(tn + ".respecAt", String.valueOf(d.respecAt[t]));''', '''    if (d.respecAt[t] > 0L) p.setProperty(tn + ".respecAt", String.valueOf(d.respecAt[t]));
    if (d.credit[t] > 0L) p.setProperty(tn + ".dustCredit", String.valueOf(d.credit[t]));''')
rep('''  d.respecAt[t] = now;''', '''  d.respecAt[t] = now;
  d.credit[t] = 0L;   // 0.2.4: a respec gives back everything spent; the migration credit only stood for Dust already spent''')
after('''public static synchronized boolean setNote(@PKG@.TreeData d) {
  if (d.noteSwing) return false;
  d.noteSwing = true;
  return true;
}""")''', '''
# 0.2.4: the pending one-time chat line (null = none), cleared once taken (the caller marks the file dirty and sends it)
M(sto, r"""
public static synchronized int[] takeNote024(@PKG@.TreeData d) {
  if (d == null || (d.note024[0] <= 0 && d.note024[1] <= 0 && d.note024[2] <= 0)) return null;
  int[] r = new int[] { d.note024[0], d.note024[1], d.note024[2] };
  d.note024[0] = 0;
  d.note024[1] = 0;
  d.note024[2] = 0;
  return r;
}""")''')

# ================================================================ TreeCalc: the migration credit counts as Dust earned
rep('''  r[2] = dustEarned(t, xp(u, t, lvl));''', '''  r[2] = dustEarned(t, xp(u, t, lvl)) + (d == null ? 0L : d.credit[t]);   // 0.2.4: + the Double Jump move credit''')

# ================================================================ TreeFx: Feller table, dodge / speed totals
rep('''  if (k == @K_FELLER@ && eff >= @PKG@.TreeCfg.MAX[i]) return (double) @PKG@.TreeCfg.FELLER_ALL;
  if (k == @K_VEIN@ || k == @K_FELLER@ || k == @K_DJUMP@) return @PKG@.TreeCfg.BASE[i] + per * (double) eff;''',
    '''  if (k == @K_FELLER@) return (double) @PKG@.TreeCfg.fellerLogs(eff);   // 0.2.4: the feller.logs table (capped at feller.maxPerLayer)
  if (k == @K_VEIN@ || k == @K_DJUMP@) return @PKG@.TreeCfg.BASE[i] + per * (double) eff;''')
rep('''  putNZ(m, "dodge.acrobatics", v[@I_RDODGE2@]);''', '''  putNZ(m, "dodge.acrobatics", v[@I_RDODGE@] + v[@I_RDODGE2@]);   // 0.2.4: Quick Dodge is back''')
rep('''  float sp = (float) r6(v[@I_RSPEED@] + v[@I_RSPEED2@] + v[@I_RSPEED3@]);''', '''  float sp = (float) r6(v[@I_RSPEED@] + v[@I_RSPEED3@]);   // 0.2.4: Sprinter was removed (Double Jump took its slot)''')

# ================================================================ TreeMsg: the one-time 0.2.4 chat line
after('''public static void say(@PR@ pr, String text, String color) {
  try { pr.sendMessage(@MSG@.raw(text).color(color)); } catch (Throwable t) { }
}""")''', '''
# 0.2.4: "1, 2, 4, 5, 6 or 10" from the live table
M(msg, r"""
public static String logsText() {
  int[] t = @PKG@.TreeCfg.FELLER_LOGS;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < t.length; i++) {
    if (i > 0) sb.append(i == t.length - 1 ? " or " : ", ");
    sb.append(t[i]);
  }
  return sb.toString();
}""")
# 0.2.4: the one-time line after a player-file migration (TreeTick, world thread; per profile; skipped while profile:busy)
M(msg, r"""
public static void note024(@PR@ pr, java.util.UUID u) {
  if (@PKG@.TreeStore.busy(u)) return;
  String k = @PKG@.TreeStore.pkey(u);
  @PKG@.TreeData d = @PKG@.TreeStore.dataK(k, u);
  if (d == null || d.bad) return;
  int[] n = @PKG@.TreeStore.takeNote024(d);
  if (n == null) return;
  @PKG@.TreeStore.dirty(k);
  StringBuilder sb = new StringBuilder("[Trees] SkyyTrees update:");
  if (n[0] > 0) sb.append(" Double Jump moved to Acrobatics tier III (where Sprinter was) - you keep level ").append(n[0]).append(" and pay no extra Dust.");
  if (n[1] > 0) sb.append(" Sprinter was removed - its token and all its Dust are back (it was level ").append(n[1]).append(").");
  if (n[0] > 0 || n[1] > 0) sb.append(" Quick Dodge is back in tier II.");
  if (n[2] > 0) sb.append(" Tree Feller now breaks ").append(logsText()).append(" more logs at levels 1-").append(@PKG@.TreeCfg.FELLER_LOGS.length).append(" (no longer the whole layer).");
  pr.sendMessage(@MSG@.raw(sb.toString()).color("#9cd8ff"));
}""")''')
rep('''    @PKG@.TreeSwing.notice(pr, u);''', '''    @PKG@.TreeSwing.notice(pr, u);
    @PKG@.TreeMsg.note024(pr, u);''')

# ================================================================ TreeSwing texts (hatchet: wood only)
rep('''breaking power). Chopping Speed does the same for hatchets. Chopping Speed II is now Heavy Hatchet''',
    '''breaking power). Chopping Speed does the same for hatchets on wood. Chopping Speed II is now Heavy Hatchet''')
rep('''  @PKG@.TreeCfg.info("swing speed ready: " + (2 * MAXT) + " effects, pickaxe root = " + pr + ", hatchet root = " + hr + (@PKG@.TreeCfg.SWING_ON ? "" : " (swing.enabled=false - off)"));''',
    '''  @PKG@.TreeCfg.info("swing speed ready: " + (2 * MAXT) + " effects, pickaxe root = " + pr + ", hatchet root = " + hr + " (hatchet bonus only when the swing chops wood)" + (@PKG@.TreeCfg.SWING_ON ? "" : " (swing.enabled=false - off)"));''')
rep('''". Hatchet (Chopping Speed): " + tierText(tier(v[@I_FSPEED@])) + ".";''',
    '''". Hatchet (Chopping Speed): " + tierText(tier(v[@I_FSPEED@])) + " - only when the swing chops wood (logs, branches, wood blocks); mobs and other blocks keep 0.35 s.";''')

# ================================================================ TreePage: the Feller card follows the table (text only - no layout / style change)
rep('''    if (eff >= @PKG@.TreeCfg.MAX[i]) return "Breaks every log of that tree on the same level (up to " + @PKG@.TreeCfg.FELLER_ALL + ")";
''', '')

# ================================================================ Server Setup rows + checks
rep('''    ("feller.cooldownSec", "Tree Feller cooldown", "abilities", "int", "3", "0", "86400", "", "s", "live",''',
    '''    ("feller.logs", "Tree Feller logs per level", "abilities", "text", FELLER_LOGS_CSV, "", "120", "", "", "live,danger",
     "Extra logs at Tree Feller level 1, 2, 3...: whole numbers 1-256, each at least the one before.", "reload;check=TreeKit.checkFellerLogs"),
    ("feller.cooldownSec", "Tree Feller cooldown", "abilities", "int", "3", "0", "86400", "", "s", "live",''')
rep('''    ("feller.maxPerLayer", "Tree Feller max logs", "abilities", "int", "64", "1", "256", "", "", "live",
     "The max level breaks every log of the tree on the cut's level, up to this many.", "reload"),''',
    '''    ("feller.maxPerLayer", "Tree Feller safety cap", "abilities", "int", "64", "1", "256", "", "", "live",
     "One Tree Feller never breaks more logs than this, whatever the logs per level say.", "reload"),''')
rep('''assert len(_exact) == 18 and len(CFG_ROWS) == 19 + len(TREES)   # 0.2.3: + swing.enabled (config:def 25 rows)''',
    '''assert len(_exact) == 19 and len(CFG_ROWS) == 20 + len(TREES)   # 0.2.4: + feller.logs (config:def 26 rows)
assert all(len(_r[10]) <= 100 for _r in CFG_ROWS)''')
rep('''RELOAD="TreeKit.reload", KEEP=20,''', '''RELOAD="TreeKit.reload", KEEP=10,''')   # LOCKED 2026-09-25: 10 old file versions
after('''    if (i > 0 && v < prev) return "Tier " + @PKG@.TreeDefs.roman(i + 1) + " (" + v + ") must not be below tier " + @PKG@.TreeDefs.roman(i) + " (" + prev + ").";
    prev = v;
  }
  return null;
}""")''', '''
# 0.2.4 feller.logs: the loader's rules (1-20 whole numbers 1-256, each at least the one before); a number above the safety cap asks first
M(kitc, r"""
public static String checkFellerLogs(String key, String value) {
  if (value == null) return null;
  String[] xs = @PKG@.TreeCfg.split(value);
  if (xs.length < 1 || xs.length > 20) return "Needs 1 to 20 whole numbers, like @FELLER_CSV@ (extra logs at Tree Feller level 1, 2, 3 ...).";
  int prev = 0;
  for (int i = 0; i < xs.length; i++) {
    int v = -1;
    try { v = Integer.parseInt(xs[i]); } catch (Throwable t) { return xs[i] + " is not a whole number - use numbers like @FELLER_CSV@."; }
    if (v < 1 || v > 256) return "Each number must be 1 to 256 (level " + (i + 1) + " is " + v + ").";
    if (v < prev) return "Level " + (i + 1) + " (" + v + ") must not be below level " + i + " (" + prev + ").";
    prev = v;
  }
  int cap = @PKG@.TreeCfg.FELLER_ALL;
  if (prev > cap) return "?The biggest number (" + prev + ") is above the Tree Feller safety cap (" + cap + ") - those levels break " + cap + " logs. Save it anyway?";
  return null;
}""")''')
rep('''  boolean hasBase = kd == @K_VEIN@ || kd == @K_FELLER@ || kd == @K_DJUMP@;''', '''  boolean hasBase = kd == @K_VEIN@ || kd == @K_DJUMP@;
  if (kd == @K_FELLER@ && (f.equals("per") || f.equals("base"))) return "?Tree Feller has no " + f + " since 0.2.4 - its logs per level are the row Tree Feller logs per level (feller.logs). Save it anyway?";''')
rep('''  if (f.equals("max")) {
    String rm = wholeIn(value, 1L, 100L, nm);
    if (rm != null || kd != @K_SWING@) return rm;''', '''  if (f.equals("max")) {
    String rm = wholeIn(value, 1L, 100L, nm);
    if (rm == null && kd == @K_FELLER@) {
      int[] tl = @PKG@.TreeCfg.FELLER_LOGS;
      if (Long.parseLong(value.trim()) > (long) tl.length) return "?feller.logs has " + tl.length + " numbers - Tree Feller levels above " + tl.length + " break the same " + tl[tl.length - 1] + " logs. Save it anyway?";
      return null;
    }
    if (rm != null || kd != @K_SWING@) return rm;''')
rep('''    return "?Only Vein Burst, Tree Feller and Double Jump use base - " + e + " does nothing. Save it anyway?";''',
    '''    return "?Only Vein Burst and Double Jump use base - " + e + " does nothing. Save it anyway?";''')

# ================================================================ final checks + write
assert s.count("registerSystem(") == REG0, "0.2.4 adds no system (one registerSystem per class)"
assert "0.2.3 SkyyTrees" not in s and "KEEP=20" not in s and "I_RSPEED2" not in s
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.2.3
print("wrote", dst)
