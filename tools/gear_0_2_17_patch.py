"""Derive SkyyGear/build_skyygear_0.2.17.py from the LIVE 0.2.16 (build_skyygear_0.2.16.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_16_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_17_patch.py      then      python SkyyGear/build_skyygear_0.2.17.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.17.py

0.2.17 = TOOL RARITY ON CRAFT (Skyy 2026-10-10, inventory screenshot of 13 identical crafted pickaxes: "pickaxes dont seem to get different
rarity's from crafting like weapons and armor... they should."; docs/answered/gear.md LOCKED 2026-10-10 tool rarity line, 2026-10-06 "Those
speed tiers only roll on weapons. Not tools"; numbers from research/cloud/Tool-Levels-Revision.md sections 5-7) + THE MACE LOAD WARNINGS.
  1. CRAFTED GATHERING TOOLS ROLL A RARITY (GearRoll.craftDoc): pickaxes, shovels, hatchets, hoes and sickles (GearTool's five families; every
     other Tool_* - hammers, watering cans, fishing rods - is not a SkyyGear gathering tool and stays as it was) roll from the SAME craft odds
     column + Smithing step-up as weapons / armor (odds.<rarity> craft weight, smith.perLevel / smith.cap, craft.maxRarity; the step-up ends at
     Fabled; Mythic stays boss-only; Untiered never - its odds are 0 and the cap stops it; a Set roll (weight 0 by default) becomes Normal on a
     tool). Server Setup -> Gear -> Tools -> "Crafted tools roll a rarity" (part.toolRarity, default on; off = crafted tools are Normal with no
     modifiers, the 0.2.16 behaviour). A rolled tool document carries "tr":1 (the frame / name colour of its rarity like gear); a tool document
     without it (every tool made before 0.2.17) keeps its own quality frame and works exactly as before - no retro roll.
  2. RARITY SCALES THE TOOL'S OWN LEVEL STATS: the level's power bonus (factor - 1) and the level Fortune x (1 + tool.rarityBoost[rarity] %),
     default "0 5 10 15 20 25" (Normal .. Mythic), only on a rolled tool ("tr"); caps unchanged (power x100, tool.fortune.cap 25).
  3. TOOL MODIFIERS (9 new stat rows, slot letter t = tool, LIVE): mpow Mining Power % (pickaxe), dpow Digging Power % (shovel), cpow Chopping
     Power % (hatchet) - max 30, weight 10; mfort Mining Fortune (pickaxe, shovel), ffort Foraging Fortune (hatchet), afort Farming Fortune (hoe,
     sickle) - max 10, weight 10; mwis / fwis / awis Mining / Foraging / Farming Wisdom % (more skill XP, SkyySkills' live xp.<skill> bonus) -
     max 10, weight 8. Each family rolls only its own keys (pickaxe 3, shovel 3, hatchet 3, hoe / sickle 2), never a combat stat and NEVER a
     weapon speed tier (GearSpeed has no tool family - asserted). Count per rarity = rarity.<id> modifiers (1 / 2 / 3 / 4 / 5 / 6) capped by the
     pool; each slot the pool cannot fill adds tool.spareSlotBoost 10 % to every roll (max tool.spareSlotMax 30 %, Revision 5). Roll strength =
     the rarity's low-high % x the item level factor, like gear (GearRoll.bounds). Applied in GearTool: Power x (1 + mod %) on the family's own
     blocks (pickaxe rock / ore, shovel soil, hatchet logs), Fortune + mod (then tool.fortune.cap), Wisdom = the "gear" skill:bonus source's
     xp.<skill> (tool part capped at tool.wisdom.cap 15 %, the worn mining armor's part keeps armor.wisdom.cap). Only while the tool is active
     (level met), like its level stats. NOT a modifier (left out, reported): tool SWING speed - SkyyTrees owns the swing tiers (its own nodes,
     re-applied every second) and reads no gear source yet; a swing roll would do nothing (LOCKED 2026-09-30 "never a stat that does nothing").
     Sickle Range stays out (no stage 0).
  4. REFORGE + LEVEL UP + IDENTIFY ON TOOLS: the Reforge page lists the gathering tools; a reforge re-rolls the tool modifiers for its rarity
     and level (rarity and level kept), costs cost.reforge like gear and pays xp.reforge Smithing XP (coins in, a few XP out - no loop: XP is
     never worth coins back); a tool made before 0.2.17 (plain Normal, or no document at all) gets its first rolls (and "tr") when reforged.
     Level up works on tools too. Identify accepts an unidentified tool document (none is made today).
  5. CRAFT SMITHING XP FOR TOOLS (replaces "tools pay on reforge"): xp.craft.<rarity> x the tier factor x tool.xpCraft % (default 100 = the
     same as a weapon of that metal: Iron Normal 250, Iron Rare 1000), once per crafted tool (bench or /craft), through skill:fn:addxp.
  6. THE 9 MACE LOAD WARNINGS 'Missing interaction *SkyyGear_Spd{F,S,X}_Mace_Weapon_Mace_Primary_Swing_{Left,Right,Up_Left}_Next': the
     mace tap chain that 0.2.13's named Charging children <file>_Hold0 start (Swing_X -> its Replace -> Swing_X_Selector -> the pad step)
     still carried its Next steps INLINE; the engine configures those named steps' packets (SimpleInteraction.configurePacket ->
     Interaction.getInteractionIdOrUnknown, which logs the WARN and loads a SendMessage placeholder) before the batch's inline children load.
     FIX (the 0.2.13 way): every inline Next / Failed step on that chain is now its own NAMED file <step>_Next (the very id the warning names,
     without the inline star) in the same batch - 18 files (Swing_X_Next + Swing_X_Selector_Next per swing and tier; a smoke test showed that
     naming only the first step moves the 9 lines one step down). Re-inlined, every speed file equals 0.2.16's; every string id resolves.
  7. INVESTIGATED, NOT CHANGED: the vanilla inventory Stats panel "Defense 0%" with SkyyGear armor on = 0.2.5's hidden armor box (GearABox
     empties each gear armor TYPE's damageResistance map, which is the same packet field the client's Character panel sums) - see the report.
SAVED DATA: rolled tools carry the gear document they had since 0.2 + "tr":1 + their modifiers; nothing else is stored.
CONFIG (PROJECT-RULES 4): ONE-TIME UPDATE migrate0217 = pure ADDITION (the 0.2.16 shape, no value rewritten, no change-log row): the block
(heading, marker, the 6 tool rarity rows with their help lines, the 9 stats.<tool key> rows with their name lines) at the END of the file, only
the keys the file lacks (kept + noted); verified History copy first, atomic write, ISO-8859-1 bytes, run-once marker, every other byte and
line ending kept.
ROLLBACK (for tools/deploy_set.py, reported, not edited here): 0.2.17 -> 0.2.16 is safe for items: rolled tools keep their documents; 0.2.16
shows their tool modifier lines as unknown keys (grey, no effect) and the tool keeps working at its level stats; the rarity frame and name
colour do NOT stay (0.2.16's GearView treats every tool as plain and puts its own quality back at the next stamp scan); going forward to
0.2.17 again restores them from the saved rarity.
FIX ROUND (critics, 2026-10-10): (a) Smithing XP loop: craft XP of a tool x its salvage share GearRoll.TX_* (built from Assets.zip: a tool
whose vanilla salvage gives back more than half its bars pays the net metal share - Tool_Sickle_Copper, 1 bar in / 1 ore back, pays 0);
(b) GearRoll.craftable takes a rolling tool even with part.levels off (the switch no longer silently needs Tool levels); (c) the Identify
refusal wording back to "weapons and armor" (the Identify list shows gear only); (d) the Reforge page subtitle names tools.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.16.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.17.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.16"' in s and s.startswith('"""SkyyGear 0.2.16 - build script'), "build_skyygear_0.2.16.py is not the live 0.2.16"
assert "toolRolls" not in s and "TR_MARK" not in s, "0.2.16 already has the 0.2.17 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.16 - build script (javassist via jpype). GENERATED by tools/gear_0_2_16_patch.py from the LIVE 0.2.15 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.16.py -> SkyyGear/SkyyGear-0.2.16.jar (never --deploy).

0.2.16 = ''', '''"""SkyyGear 0.2.17 - build script (javassist via jpype). GENERATED by tools/gear_0_2_17_patch.py from the LIVE 0.2.16 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.17.py -> SkyyGear/SkyyGear-0.2.17.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.17 = "):].strip() + '''

0.2.16 (the base, everything below is still true unless 0.2.17 above says otherwise):
0.2.16 = ''')
rep('VERSION = "0.2.16"', 'VERSION = "0.2.17"')

# ================================================================================================================ 1. the stat table: 9 tool rows
rep('''    ("xpb", "XP Bonus", "wa", "%", 5, 2, 0, ""),
]''', '''    ("xpb", "XP Bonus", "wa", "%", 5, 2, 0, ""),
    # 0.2.17 TOOL MODIFIERS (Skyy 2026-10-10 "pickaxes dont seem to get different rarity's from crafting like weapons and armor... they should.";
    # research/cloud/Tool-Levels-Revision.md 6): slot t = a gathering tool only (each key only on its families, TOOL_STAT_FAM); LIVE (GearTool)
    ("mpow", "Mining Power", "t", "%", 30, 10, 1, ""),
    ("dpow", "Digging Power", "t", "%", 30, 10, 1, ""),
    ("cpow", "Chopping Power", "t", "%", 30, 10, 1, ""),
    ("mfort", "Mining Fortune", "t", "", 10, 10, 1, ""),
    ("ffort", "Foraging Fortune", "t", "", 10, 10, 1, ""),
    ("afort", "Farming Fortune", "t", "", 10, 10, 1, ""),
    ("mwis", "Mining Wisdom", "t", "%", 10, 8, 1, ""),
    ("fwis", "Foraging Wisdom", "t", "%", 10, 8, 1, ""),
    ("awis", "Farming Wisdom", "t", "%", 10, 8, 1, ""),
]
# 0.2.17: the tool modifier keys + the GearTool families (1 pickaxe, 2 shovel, 3 hatchet, 4 hoe, 5 sickle) each may roll on
TOOL_KEYS = ["mpow", "dpow", "cpow", "mfort", "ffort", "afort", "mwis", "fwis", "awis"]
TOOL_STAT_FAM = {"mpow": (1,), "dpow": (2,), "cpow": (3,), "mfort": (1, 2), "ffort": (3,), "afort": (4, 5), "mwis": (1, 2), "fwis": (3,),
                 "awis": (4, 5)}
assert sorted(TOOL_STAT_FAM) == sorted(TOOL_KEYS)
for _f in (1, 2, 3, 4, 5):
    assert [_k for _k in TOOL_KEYS if _f in TOOL_STAT_FAM[_k]], "a tool family without a modifier"''')
rep('''assert S_KEYS == SPEC_KEYS + LATER_KEYS, "the stat table must match spec 4.2 (keys + display order) + the design-review rows + chg"''',
    '''assert S_KEYS == SPEC_KEYS + LATER_KEYS + TOOL_KEYS, "the stat table must match spec 4.2 (keys + display order) + the design-review rows + chg + 0.2.17 tool rows"''')
rep('''    assert re.match(r"^[a-z][a-zA-Z]*$", _s[0]) and re.match(r"^(?!.*(.).*\\1)[wsae]{1,4}$", _s[2]) and _s[3] in ("", "%"), _s''',
    '''    assert re.match(r"^[a-z][a-zA-Z]*$", _s[0]) and re.match(r"^(?!.*(.).*\\1)[wsaet]{1,4}$", _s[2]) and _s[3] in ("", "%"), _s
    assert ("t" in _s[2]) == (_s[0] in TOOL_KEYS) and (_s[2] == "t" or "t" not in _s[2]), "0.2.17: slot t = the tool rows only, alone: %s" % (_s,)''')
rep('''assert [s[0] for s in STATS if s[6] == 1] == SPEC_KEYS[:22], "live stats = spec 4.2 LIVE rows + chg (0.1.2)"''',
    '''assert [s[0] for s in STATS if s[6] == 1] == SPEC_KEYS[:22] + TOOL_KEYS, "live stats = spec 4.2 LIVE rows + chg (0.1.2) + the 0.2.17 tool rows"''')

# the fresh file: the tool rows sit in the 0.2.17 block at the end (migrate0217 adds exactly those lines to an older file), not in the stats block
rep('''    _where = {"w": "weapon", "s": "spell weapon", "a": "armor", "e": "Equipment"}
    for s in STATS:''', '''    _where = {"w": "weapon", "s": "spell weapon", "a": "armor", "e": "Equipment"}
    for s in [_s for _s in STATS if _s[0] not in TOOL_KEYS]:          # 0.2.17: the tool rows live in the 0.2.17 block''')

# ================================================================================================================ 2. Python defaults + config rows
rep('''TOOL_FCAP_DEF = 25.0          # tool Fortune cap (Revision 4 rule 3: tool.fortune.cap 25)''',
    '''TOOL_FCAP_DEF = 25.0          # tool Fortune cap (Revision 4 rule 3: tool.fortune.cap 25)
# 0.2.17 tool rarity: % more level power bonus / level Fortune per rarity Normal Unique Rare Legendary Fabled Mythic (PLACEHOLDER)
TOOL_RB_DEF = "0 5 10 15 20 25"
TOOL_SPARE_DEF, TOOL_SPAREMAX_DEF, TOOL_WCAP_DEF, TOOL_XPC_DEF = 10.0, 30.0, 15.0, 100''')
rep('''    ("tool.fortune.cap", "Tool Fortune cap", "tools", "dec", repr(TOOL_FCAP_DEF), "0", "1000", "", "", "live,danger",
     "Most Fortune one tool gives (100 = one sure extra drop)." + PH, "field:GearCfg.TOOL_FCAP"),''',
    '''    ("tool.fortune.cap", "Tool Fortune cap", "tools", "dec", repr(TOOL_FCAP_DEF), "0", "1000", "", "", "live,danger",
     "Most Fortune one tool gives (100 = one sure extra drop)." + PH, "field:GearCfg.TOOL_FCAP"),
    # 0.2.17 TOOL RARITY (Skyy 2026-10-10 "pickaxes dont seem to get different rarity's from crafting like weapons and armor... they should.")
    ("part.toolRarity", "Crafted tools roll a rarity", "tools", "bool", "true", "", "", "", "", "live,part,danger",
     "Crafted pickaxes, shovels, hatchets, hoes, sickles roll a rarity + tool modifiers. Off = Normal.", "field:GearCfg.TOOL_RAR"),
    ("tool.rarityBoost", "Tool level stats by rarity", "tools", "text", TOOL_RB_DEF, "3", "100", "", "", "live,danger",
     "% more level Power + Fortune: Normal Unique Rare Legendary Fabled Mythic.",
     "field:GearCfg.TOOL_RBT;check=GearCfg.checkBoost"),
    ("tool.spareSlotBoost", "Boost per empty modifier slot", "tools", "dec", repr(TOOL_SPARE_DEF), "0", "100", "", "%", "live,danger",
     "Each modifier slot a tool cannot fill: its rolls this % stronger." + PH, "field:GearCfg.TOOL_SPARE"),
    ("tool.spareSlotMax", "Most empty-slot boost", "tools", "dec", repr(TOOL_SPAREMAX_DEF), "0", "300", "", "%", "live,danger",
     "The empty-slot boost never goes above this." + PH, "field:GearCfg.TOOL_SPAREMAX"),
    ("tool.wisdom.cap", "Most Wisdom % from a tool", "tools", "dec", repr(TOOL_WCAP_DEF), "0", "100", "", "%", "live,danger",
     "A held tool's Wisdom (more skill XP) stops here.", "field:GearCfg.TOOL_WCAP"),
    ("tool.xpCraft", "Tool craft Smithing XP", "tools", "int", str(TOOL_XPC_DEF), "0", "1000", "", "%", "live,danger",
     "Crafted tools pay this % of the craft Smithing XP (xp.craft x tier)." + PH, "field:GearCfg.TOOL_XPC"),''')
rep('''     "Smithing XP per crafted weapon / armor piece by rarity, x the tier factor. Tools pay on reforge.",''',
    '''     "Smithing XP per crafted weapon, armor piece or tool by rarity, x the tier factor.",''')
rep('''           "part.utLines", "utfx", "utline.power", "gear.mythicItems", "market.gatheringSets", "market.gatheringPrefixes", "utdrop.mob", "utdrop.chest",
           "utdrop.luggage"}''', '''           "part.utLines", "utfx", "utline.power", "gear.mythicItems", "market.gatheringSets", "market.gatheringPrefixes", "utdrop.mob", "utdrop.chest",
           "utdrop.luggage",
           # 0.2.17: tool rarity (item rolls, gathering speed / Fortune / XP = economy) - confirm in Server Setup
           "part.toolRarity", "tool.rarityBoost", "tool.spareSlotBoost", "tool.spareSlotMax", "tool.wisdom.cap", "tool.xpCraft"}''')
rep('''              ("UT_LUG", "String", '"1 2 4 8"'), ("UT_ARMOR", "int", "50"), ("UT_LEAN", "int", "3")]''',
    '''              ("UT_LUG", "String", '"1 2 4 8"'), ("UT_ARMOR", "int", "50"), ("UT_LEAN", "int", "3"),
              # 0.2.17 tool rarity
              ("TOOL_RAR", "boolean", "true"), ("TOOL_RBT", "String", jstr(TOOL_RB_DEF)), ("TOOL_SPARE", "double", repr(TOOL_SPARE_DEF)),
              ("TOOL_SPAREMAX", "double", repr(TOOL_SPAREMAX_DEF)), ("TOOL_WCAP", "double", repr(TOOL_WCAP_DEF)), ("TOOL_XPC", "int", str(TOOL_XPC_DEF))]''')

# the fresh file's 0.2.17 block (= exactly what migrate0217 adds to an older file)
rep(r'''UB_LINES = [UB_HEAD, UB_MARK] + [_x for _c, _ls in UB_GROUPS for _x in [_c] + _ls]
assert all(all(32 <= ord(_c) < 127 for _c in _x) for _x in UB_LINES) and all("=" not in _x for _x in (UB_HEAD, UB_MARK))
assert len(set(UB_LINES)) == len(UB_LINES)''', r'''UB_LINES = [UB_HEAD, UB_MARK] + [_x for _c, _ls in UB_GROUPS for _x in [_c] + _ls]
assert all(all(32 <= ord(_c) < 127 for _c in _x) for _x in UB_LINES) and all("=" not in _x for _x in (UB_HEAD, UB_MARK))
assert len(set(UB_LINES)) == len(UB_LINES)


# 0.2.17: the tool rarity block at the very end of a fresh file (migrate0217 appends the missing keys of it, group by group, to an older one)
TR_MARK_ID = "SkyyGear 0.2.17 tool rarity"
TR_WHO = "SkyyGear 0.2.17"
TR_HEAD = "# ---- Tool rarity: crafted gathering tools roll a rarity and tool modifiers (SkyyGear 0.2.17) ----"
TR_MARK = ("# %s (Skyy 2026-10-10): crafted pickaxes, shovels, hatchets, hoes and sickles roll a rarity like weapons and armor, with tool "
           "modifiers only (never a weapon speed tier), and pay Smithing XP" % TR_MARK_ID)
_trr = dict((_r[0], _r) for _r in CFG_ROWS)
TR_SCAL = ["part.toolRarity", "tool.rarityBoost", "tool.spareSlotBoost", "tool.spareSlotMax", "tool.wisdom.cap", "tool.xpCraft"]
_TWHERE = {1: "pickaxe", 2: "shovel", 3: "hatchet", 4: "hoe", 5: "sickle"}
TR_GROUPS = [("# %s: %s" % (_trr[_k][1], _trr[_k][10]), ["%s=%s" % (_k, _trr[_k][4])]) for _k in TR_SCAL]
TR_GROUPS += [("# %s = %s (tool modifier: %s%s)" % (_s[0], _s[1], ", ".join(_TWHERE[_f] for _f in TOOL_STAT_FAM[_s[0]]), ", %" if _s[3] == "%" else ""),
               ["stats.%s=%d,%d" % (_s[0], _s[4], _s[5])]) for _s in STATS if _s[0] in TOOL_KEYS]
TR_LINES = [TR_HEAD, TR_MARK] + [_x for _c, _ls in TR_GROUPS for _x in [_c] + _ls]
assert all(all(32 <= ord(_c) < 127 for _c in _x) for _x in TR_LINES) and all("=" not in _x for _x in (TR_HEAD, TR_MARK))
assert len(set(TR_LINES)) == len(TR_LINES) and len(TR_GROUPS) == len(TR_SCAL) + len(TOOL_KEYS)''')
rep('''    L += [""] + UB_LINES       # 0.2.16: the Untiered batch block (migrate0216 adds the missing lines of it to an older file)
    return "\\n".join(L) + "\\n"''', '''    L += [""] + UB_LINES       # 0.2.16: the Untiered batch block (migrate0216 adds the missing lines of it to an older file)
    L += [""] + TR_LINES       # 0.2.17: the tool rarity block (migrate0217 adds the missing lines of it to an older file)
    return "\\n".join(L) + "\\n"''')
rep('''assert _DL[-len(GU_LINES) - len(GM_LINES) - len(UB_LINES) - 4:-len(GM_LINES) - len(UB_LINES) - 2] == [""] + GU_LINES + [""], _DL[-len(GU_LINES) - len(GM_LINES) - 3:]''',
    '''_NT = len(TR_LINES) + 1          # 0.2.17: the tool rarity block (+ its blank line) now ends the file
assert _DL[-len(GU_LINES) - len(GM_LINES) - len(UB_LINES) - 4 - _NT:-len(GM_LINES) - len(UB_LINES) - 2 - _NT] == [""] + GU_LINES + [""], _DL[-len(GU_LINES) - len(GM_LINES) - 3:]''')
rep('''assert _DL[-len(GM_LINES) - len(UB_LINES) - 2:-len(UB_LINES) - 1] == GM_LINES + [""] and all(_DL.count(_x) == 1 for _x in GM_LINES) and DEFAULT_TEXT.count(GM_MARK_ID) == 1''',
    '''assert _DL[-len(GM_LINES) - len(UB_LINES) - 2 - _NT:-len(UB_LINES) - 1 - _NT] == GM_LINES + [""] and all(_DL.count(_x) == 1 for _x in GM_LINES) and DEFAULT_TEXT.count(GM_MARK_ID) == 1''')
rep('''assert _DL[-len(UB_LINES) - 1:] == UB_LINES + [""] and all(_DL.count(_x) == 1 for _x in UB_LINES) and DEFAULT_TEXT.count(UB_MARK_ID) == 1''',
    '''assert _DL[-len(UB_LINES) - 1 - _NT:-_NT] == UB_LINES + [""] and all(_DL.count(_x) == 1 for _x in UB_LINES) and DEFAULT_TEXT.count(UB_MARK_ID) == 1
# 0.2.17: the tool rarity block once, at the very end, every line unique; the rows read back; the tool stats rows only there
assert _DL[-len(TR_LINES) - 1:] == TR_LINES + [""] and all(_DL.count(_x) == 1 for _x in TR_LINES) and DEFAULT_TEXT.count(TR_MARK_ID) == 1
for _k in TOOL_KEYS:
    assert _dp.get("stats." + _k) == "%d,%d" % (STATS[S_KEYS.index(_k)][4], STATS[S_KEYS.index(_k)][5]) and DEFAULT_TEXT.count("\\nstats.%s=" % _k) == 1, _k
assert _dp.get("tool.rarityBoost") == TOOL_RB_DEF and _dp.get("part.toolRarity") == "true" and _dp.get("tool.xpCraft") == str(TOOL_XPC_DEF)''')

# ================================================================================================================ 3. Java fields
rep('''F(gdf, "public static final String[] S_SUF = %s;" % jarr([s[7] for s in STATS]))''',
    '''F(gdf, "public static final String[] S_SUF = %s;" % jarr([s[7] for s in STATS]))
# 0.2.17: the GearTool families a tool modifier may roll on (bit 1 << fam), 0 = not a tool modifier; GearTool.fam's numbering
F(gdf, "public static final int[] S_TMASK = %s;" % jints([sum(1 << _f for _f in TOOL_STAT_FAM.get(s[0], ())) for s in STATS]))
F(gdf, "public static final String[] T_FAM = %s;" % jarr(TOOL_FAMS))''')
rep('''F(gcf, "public static final String[] UB_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in UB_GROUPS for _x in _ls]))''',
    '''F(gcf, "public static final String[] UB_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in UB_GROUPS for _x in _ls]))
# 0.2.17: the tool rarity block (migrate0217)
F(gcf, "public static final String TR_MARK = %s;" % jstr(TR_MARK))
F(gcf, "public static final String TR_MARK_ID = %s;" % jstr(TR_MARK_ID))
F(gcf, "public static final String TR_WHO = %s;" % jstr(TR_WHO))
F(gcf, "public static final String TR_HEAD = %s;" % jstr(TR_HEAD))
F(gcf, "public static final String[] TR_GC = %s;" % jarr([_c for _c, _ls in TR_GROUPS]))
F(gcf, "public static final int[] TR_GS = %s;" % jints([len(_ls) for _c, _ls in TR_GROUPS]))
F(gcf, "public static final String[] TR_GL = %s;" % jarr([_x for _c, _ls in TR_GROUPS for _x in _ls]))
F(gcf, "public static final String[] TR_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in TR_GROUPS for _x in _ls]))''')
rep('''F(gcf, "public static final String TOOL_HATCH_DEF = %s;" % jstr(TOOL_HATCH_DEF))   # 0.2.12 Chopping Power''',
    '''F(gcf, "public static final String TOOL_HATCH_DEF = %s;" % jstr(TOOL_HATCH_DEF))   # 0.2.12 Chopping Power
F(gcf, "public static final String TOOL_RB_DEF = %s;" % jstr(TOOL_RB_DEF))         # 0.2.17 tool level stats by rarity
F(gcf, "public static volatile String TOOL_RBSRC = null;")
F(gcf, "public static volatile double[] TOOL_RBV = null;")''')

# ================================================================================================================ 4. GearCfg: the boost row, the loader, the update
rep(r'''M(gcf, r"""
public static String checkCurve(String key, String value) {
  if (value == null) return null;
  if (curvePts(value) == null) return "Write level:factor points with rising levels 0-100 and factors above 0, e.g. 1:1.0,4:1.6,10:2.0,40:3.0,100:5.0 (straight lines between the points).";
  return null;
}""")''', r'''M(gcf, r"""
public static String checkCurve(String key, String value) {
  if (value == null) return null;
  if (curvePts(value) == null) return "Write level:factor points with rising levels 0-100 and factors above 0, e.g. 1:1.0,4:1.6,10:2.0,40:3.0,100:5.0 (straight lines between the points).";
  return null;
}""")
# 0.2.17 tool.rarityBoost: "0 5 10 15 20 25" -> six percents 0-500 (Normal .. Mythic; spaces or commas); null = not that
M(gcf, r"""
public static double[] boostOf(String s) {
  if (s == null) return null;
  String t = s.trim().replace(',', ' ');
  if (t.length() == 0) return null;
  String[] ps = t.split("\\s+");
  if (ps.length != 6) return null;
  double[] out = new double[6];
  for (int i = 0; i < 6; i++) {
    try { out[i] = Double.parseDouble(ps[i]); } catch (Throwable x) { return null; }
    if (Double.isNaN(out[i]) || out[i] < 0.0 || out[i] > 500.0) return null;
  }
  return out;
}""")
M(gcf, r"""
public static String checkBoost(String key, String value) {
  if (value == null) return null;
  if (boostOf(value) == null) return "Write 6 percents 0-500 for Normal Unique Rare Legendary Fabled Mythic, e.g. 0 5 10 15 20 25.";
  return null;
}""")
# the % a rolled tool of rarity r adds to its level power bonus + level Fortune (Set / Untiered 0); re-parsed when the row's text changes
M(gcf, r"""
public static double toolBoost(int r) {
  String s = TOOL_RBT;
  double[] v = TOOL_RBV;
  if (v == null || s != TOOL_RBSRC) {
    v = boostOf(s);
    if (v == null) v = boostOf(TOOL_RB_DEF);
    TOOL_RBV = v;
    TOOL_RBSRC = s;
  }
  if (v == null || r < 0 || r >= v.length) return 0.0;
  return v[r];
}""")''')
rep('''  UT_LEAN = (int) plong(p, "utbag.classLean", 3L, 1L, 10L);''', '''  UT_LEAN = (int) plong(p, "utbag.classLean", 3L, 1L, 10L);
  // 0.2.17 tool rarity (Server Setup -> Gear -> Tools); a hand-edited boost row the check would refuse falls back to its default with one WARN
  TOOL_RAR = pbool(p, "part.toolRarity", true);
  String trb = ptext(p, "tool.rarityBoost", TOOL_RB_DEF);
  if (boostOf(trb) == null) { @PKG@.Gear.warnOnce("trboost:" + trb, "config.properties: tool.rarityBoost=" + trb + " is not six percents 0-500 - the default " + TOOL_RB_DEF + " is used"); trb = TOOL_RB_DEF; }
  TOOL_RBT = trb.trim();
  TOOL_SPARE = pdec(p, "tool.spareSlotBoost", 10.0, 0.0, 100.0);
  TOOL_SPAREMAX = pdec(p, "tool.spareSlotMax", 30.0, 0.0, 300.0);
  TOOL_WCAP = pdec(p, "tool.wisdom.cap", 15.0, 0.0, 100.0);
  TOOL_XPC = (int) plong(p, "tool.xpCraft", 100L, 0L, 1000L);''')
rep(r'''# setup(), right after migrate0214 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes), one INFO''',
    r'''# ---- 0.2.17 ONE-TIME UPDATE migrate0217 (PROJECT-RULES section 4): a pure ADDITION, the 0.2.16 shape. null = the marker is already in a comment
# line (a fresh 0.2.17 file carries it); else { new text, String[] notes (keys already there - kept), "part.toolRarity, ..." (what was added) }
M(gcf, r"""
public static Object[] trUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(TR_MARK_ID) >= 0) return null;
  }
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    k = e + 1;
  }
  java.util.ArrayList notes = new java.util.ArrayList();
  StringBuilder added = new StringBuilder();
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add("");
  blk.add(TR_HEAD);
  blk.add(TR_MARK);
  int at = 0;
  for (int g = 0; g < TR_GC.length; g++) {
    boolean first = true;
    for (int j = 0; j < TR_GS[g]; j++) {
      int x = at + j;
      if (pp.getProperty(TR_GK[x]) != null) { notes.add(TR_GK[x] + " is already in the file - kept"); continue; }
      if (first) { blk.add(TR_GC[g]); first = false; }
      blk.add(TR_GL[x]);
      if (added.length() > 0) added.append(", ");
      added.append(TR_GK[x]);
    }
    at = at + TR_GS[g];
  }
  String crDef = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) out.add(raw[i]);
  chPut(out, chEnd(l, tail, raw), blk, crDef);
  StringBuilder sb = new StringBuilder(text.length() + 4096);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), (String[]) notes.toArray(new String[0]), added.toString() };
}""")
M(gcf, r"""
public static synchronized String migrate0217() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    String otext = new String(old, "ISO-8859-1");
    Object[] r = trUpdate(otext);
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), TR_WHO, "before the 0.2.17 tool rarity update");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated with the 0.2.17 tool rarity rows: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the rows still work at their defaults; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] notes = (String[]) r[1];
    String add = (String) r[2];
    int n = add.length() == 0 ? 0 : add.split(", ").length;
    String msg = "config.properties: the 0.2.17 tool rarity rows were added at the end (" + n + " lines: the switch, the rarity boost, the empty-slot boost, the Wisdom cap, the craft XP share, 9 tool modifier stats); no value changed; the old file is kept in config-history";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.2.17 tool rarity: added " + n + " keys" + (notes.length > 0 ? "; " + notes.length + " notes" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not add the 0.2.17 tool rarity rows to config.properties (the file is used as it is; every row works at its default): " + t);
    return "";
  }
}""")
# setup(), right after migrate0214 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes), one INFO''')
rep('''  @PKG@.GearCfg.migrate0216();
  @PKG@.GearCfg.load();''', '''  @PKG@.GearCfg.migrate0216();
  @PKG@.GearCfg.migrate0217();
  @PKG@.GearCfg.load();''')

# ================================================================================================================ 5. GearData: which tools roll
rep('''M(gdt, "public static boolean isTool(String id) { return id != null && id.startsWith(\\"Tool_\\") && !skyyItem(id); }")''',
    '''M(gdt, "public static boolean isTool(String id) { return id != null && id.startsWith(\\"Tool_\\") && !skyyItem(id); }")
# 0.2.17: GearTool.fam's numbering (1 pickaxe, 2 shovel, 3 hatchet, 4 hoe, 5 sickle; 0 = not a gathering tool - hammers, watering cans, rods ...)
M(gdt, r"""
public static int toolFam(String id) {
  if (id == null || !isTool(id)) return 0;
  for (int i = 0; i < @PKG@.GearDefs.T_FAM.length; i++) if (id.startsWith(@PKG@.GearDefs.T_FAM[i])) return i + 1;
  return 0;
}""")
# 0.2.17: a gathering tool that rolls a rarity + tool modifiers now (part.toolRarity + part.tools on; a tool made gear by gear.include rolls as gear)
M(gdt, "public static boolean toolRolls(String id) { return @PKG@.GearCfg.TOOL_RAR && @PKG@.GearCfg.PART_TOOLS && toolFam(id) > 0 && !isGear(id); }")
# 0.2.17: what the Reforge / Identify pages accept: gear + the gathering tools that roll
M(gdt, "public static boolean forgeable(String id) { return isGear(id) || toolRolls(id); }")''')
rep('''M(gdt, "public static boolean identified(@BD@ d) { return bool(d, \\"id\\", true); }")''',
    '''M(gdt, "public static boolean identified(@BD@ d) { return bool(d, \\"id\\", true); }")
# 0.2.17: a tool document rolled by 0.2.17+ (craft, reforge, identify): "tr":1 - it shows its rarity frame and uses its rarity boost + modifiers
M(gdt, "public static boolean toolRolled(@BD@ d) { return d != null && num(d, \\"tr\\", 0) == 1; }")''')

# ================================================================================================================ 6. GearRoll: pool, rolls, craft, XP
rep(r'''  if (slot == 4) return s.indexOf('e') >= 0;
  return false;
}""")''', r'''  if (slot == 4) return s.indexOf('e') >= 0;
  if (slot == 3) return s.indexOf('t') >= 0;       // 0.2.17: tool modifiers (pool() narrows them to the tool's family)
  return false;
}""")''')
rep(r'''    if (i == @PKG@.GearDefs.I_CHG && !@PKG@.GearChg.canRoll(id, slot)) continue;''',
    r'''    if (i == @PKG@.GearDefs.I_CHG && !@PKG@.GearChg.canRoll(id, slot)) continue;
    // 0.2.17: a tool modifier only on a rolling gathering tool of one of its families (no item known = none)
    if (slot == 3 && (!@PKG@.GearData.toolRolls(id) || (@PKG@.GearDefs.S_TMASK[i] & (1 << @PKG@.GearData.toolFam(id))) == 0)) continue;''')
rep(r'''# design review 5: Health Regen % only scales Raw Health Regen, so it is a candidate only after Raw Health Regen was picked''',
    r'''# 0.2.17 (Tool-Levels-Revision 5, spare-slot boost): bounds() x m (m = 1 + the boost); the same rounding, at least 1
M(grl, r"""
public static int[] boundsX(int i, int r, int lvl, double m) {
  if (!(m > 1.0)) return bounds(i, r, lvl);
  int rr = @PKG@.GearCfg.ri(r);
  double f = @PKG@.GearLevel.factor(lvl);
  double mx = (double) @PKG@.GearCfg.S_MAX[i] * m;
  long lo = Math.round(mx * (double) @PKG@.GearCfg.R_LO[rr] / 100.0 * f / 100.0);
  long hi = Math.round(mx * (double) @PKG@.GearCfg.R_HI[rr] / 100.0 * f / 100.0);
  if (lo < 1L) lo = 1L;
  if (hi < 1L) hi = 1L;
  if (hi < lo) hi = lo;
  return new int[] { (int) lo, (int) hi };
}""")
# 0.2.17: the spare-slot boost % of a tool roll: (the rarity's modifier count - the pool size) x tool.spareSlotBoost, at most tool.spareSlotMax
M(grl, r"""
public static double spare(int slot, int r, int poolSize) {
  if (slot != 3) return 0.0;
  int count = @PKG@.GearCfg.R_MODS[@PKG@.GearCfg.ri(r)];
  if (count <= poolSize) return 0.0;
  double b = (double) (count - poolSize) * @PKG@.GearCfg.TOOL_SPARE;
  if (b > @PKG@.GearCfg.TOOL_SPAREMAX) b = @PKG@.GearCfg.TOOL_SPAREMAX;
  return b < 0.0 ? 0.0 : b;
}""")
# design review 5: Health Regen % only scales Raw Health Regen, so it is a candidate only after Raw Health Regen was picked''')
rep(r'''  @BA@ out = new @BA@();
  int[] p = pool(slot, id);
  if (p.length == 0) return out;
  int count = @PKG@.GearCfg.R_MODS[@PKG@.GearCfg.ri(r)];
  if (count > p.length) count = p.length;''', r'''  @BA@ out = new @BA@();
  int[] p = pool(slot, id);
  if (p.length == 0) return out;
  int count = @PKG@.GearCfg.R_MODS[@PKG@.GearCfg.ri(r)];
  double boost = spare(slot, r, p.length);          // 0.2.17: a tool's empty modifier slots make its rolls stronger
  if (count > p.length) count = p.length;''')
rep(r'''    if (!pick[i]) continue;
    int[] b = bounds(i, r, lvl);
    out.add(@PKG@.GearData.mod(@PKG@.GearDefs.S_KEY[i], randInt(b[0], b[1])));''', r'''    if (!pick[i]) continue;
    int[] b = boost > 0.0 ? boundsX(i, r, lvl, 1.0 + boost / 100.0) : bounds(i, r, lvl);
    out.add(@PKG@.GearData.mod(@PKG@.GearDefs.S_KEY[i], randInt(b[0], b[1])));''')
rep(r'''  @BD@ d = @PKG@.GearData.base(@PKG@.GearData.kindFor(id), r, ident, src);
  if (lvl >= 0) d.put("lvl", new org.bson.BsonInt32(@PKG@.GearLevel.clamp(lvl)));''', r'''  // 0.2.17: a gathering tool is never Set / Mythic / Untiered (no set id, no boss tool, no Untiered tool)
  if (@PKG@.GearData.toolFam(id) > 0 && !@PKG@.GearData.isGear(id) && r > 4) r = 0;
  @BD@ d = @PKG@.GearData.base(@PKG@.GearData.kindFor(id), r, ident, src);
  if (@PKG@.GearData.toolRolls(id)) d.put("tr", new org.bson.BsonInt32(1));         // 0.2.17: a rolled tool (frame, boost, modifiers)
  if (lvl >= 0) d.put("lvl", new org.bson.BsonInt32(@PKG@.GearLevel.clamp(lvl)));''')
rep(r'''# a crafted document at level lvl (craftLevel; -1 = no stamp). Rarity from the craft odds + Smithing; a plain tool (not gear) stays Normal:
# it has no modifiers yet ("coming later" stats never roll, LOCKED 2026-09-30)
M(grl, r"""
public static @BD@ craftDoc(String id, java.util.UUID u, int lvl) {
  int r = (@PKG@.GearData.isTool(id) && !@PKG@.GearData.isGear(id)) ? 0 : craftRarity(u, null);
  return newDoc(id, r, true, "craft", lvl);
}""")''', r'''# a crafted document at level lvl (craftLevel; -1 = no stamp). Rarity from the craft odds + Smithing. 0.2.17 (Skyy 2026-10-10 "pickaxes dont
# seem to get different rarity's from crafting like weapons and armor... they should."): a gathering tool rolls too (the same odds column,
# Smithing step-up and craft.maxRarity; a Set roll becomes Normal) while part.toolRarity is on; any other tool (not gear) stays Normal
M(grl, r"""
public static @BD@ craftDoc(String id, java.util.UUID u, int lvl) {
  int r = 0;
  if (!@PKG@.GearData.isTool(id) || @PKG@.GearData.isGear(id)) r = craftRarity(u, null);
  else if (@PKG@.GearData.toolRolls(id)) {
    r = craftRarity(u, null);
    if (r > 4) r = 0;
  }
  return newDoc(id, r, true, "craft", lvl);
}""")''')
rep(r'''# Smithing XP one crafted item of rarity r pays: xp.craft[r] x the tier factor, whole XP (half up); 0 for anything that is not gear (tools)
M(grl, r"""
public static long craftXp(String id, int r) {
  if (id == null || !@PKG@.GearData.isGear(id)) return 0L;''', r'''# Smithing XP one crafted item of rarity r pays: xp.craft[r] x the tier factor, whole XP (half up); 0 for anything that is not gear. 0.2.17: a
# rolling gathering tool pays it too, x tool.xpCraft % (replaces "tools pay on reforge") x its salvage share (TX_*, below)
# 0.2.17 fix round (critic: Smithing XP loop): the gear ANTI-FARM bound (0.2.3: a Salvagebench lap gives back <= 0.5 ore per bar) must hold
# for the rolling tools too. Built here from Assets.zip (in memory, nothing committed): per tool of the five families with a recipe, the
# recipe's bars of its metal vs the ore / bars its vanilla salvage recipe gives back; back <= half = full pay, else pay = the net metal as a
# share of half the bars (Tool_Sickle_Copper: 1 bar in, 1 ore back = net 0 -> 0 XP; every other tool of the live set pays in full)
_TX = []
_TSAL = {}
for _n in sorted(AZ_NAMES):
    if _n.startswith("Server/Item/Recipes/") and _n.endswith(".json"):
        try:
            _rd = json.loads(AZ.read(_n).decode("utf-8-sig"))
        except Exception:
            continue
        _ins = [_x.get("ItemId") for _x in (_rd.get("Input") or []) if isinstance(_x, dict)]
        if len(_ins) == 1 and isinstance(_ins[0], str) and _ins[0].startswith("Tool_"):
            _TSAL.setdefault(_ins[0], []).append([_o for _o in (_rd.get("Output") or []) if isinstance(_o, dict)])
for _i in sorted(_AZ_JSON):
    _d = _AZ_JSON[_i]
    if not (isinstance(_d, dict) and isinstance(_d.get("Recipe"), dict) and any(_i.startswith(_p) for _p in TOOL_FAMS)):
        continue
    _mt = _i.rsplit("_", 1)[-1]
    _bars = sum(int(_x.get("Quantity", 1)) for _x in (_d["Recipe"].get("Input") or []) if isinstance(_x, dict) and _x.get("ItemId") == "Ingredient_Bar_" + _mt)
    if _bars <= 0:
        continue
    _back = max([0] + [sum(int(_o.get("Quantity", 1)) for _o in _os if _o.get("ItemId") in ("Ore_" + _mt, "Ingredient_Bar_" + _mt)) for _os in _TSAL.get(_i, [])])
    if _back * 2 > _bars:
        _TX.append((_i, max(0, int(100 * (_bars - _back) * 2 // _bars))))
assert ("Tool_Sickle_Copper", 0) in _TX and all(_p < 100 for _i, _p in _TX), _TX
TX_TABLE = list(_TX)              # the harness reads it (X3b)
F(grl, "public static final String[] TX_ID = %s;" % jarr([_i for _i, _p in _TX]))
F(grl, "public static final int[] TX_PCT = %s;" % jints([_p for _i, _p in _TX]))
M(grl, r"""
public static int toolXpPct(String id) {
  if (id == null) return 100;
  for (int i = 0; i < TX_ID.length; i++) if (TX_ID[i].equals(id)) return TX_PCT[i];
  return 100;
}""")
M(grl, r"""
public static long craftXp(String id, int r) {
  if (id == null) return 0L;
  boolean tool = !@PKG@.GearData.isGear(id);
  if (tool && !@PKG@.GearData.toolRolls(id)) return 0L;
  if (tool) {
    if (r > 4) r = 0;
    double tv = (double) @PKG@.GearCfg.xpCraft(r) * xpTier(xpStart(id)) * (double) @PKG@.GearCfg.TOOL_XPC / 100.0 * (double) toolXpPct(id) / 100.0;
    if (!(tv > 0.0) || Double.isInfinite(tv)) return 0L;
    return (long) Math.floor(tv + 0.5);
  }''')
rep(r'''    if (u == null || id == null || got == null || !@PKG@.GearData.isGear(id)) return res;''',
    r'''    if (u == null || id == null || got == null || !@PKG@.GearData.forgeable(id)) return res;          // 0.2.17: + rolling tools''')
rep(r'''  int r = @PKG@.GearData.rarity(d);
  d.put("mods", rollMods(id, @PKG@.GearData.slotOf(id), r, @PKG@.GearLevel.level(id, d)));
  String n = pickName(@PKG@.GearData.str(d, "rf", null));''', r'''  int r = @PKG@.GearData.rarity(d);
  d.put("mods", rollMods(id, @PKG@.GearData.slotOf(id), r, @PKG@.GearLevel.level(id, d)));
  if (@PKG@.GearData.toolRolls(id)) d.put("tr", new org.bson.BsonInt32(1));         // 0.2.17: an old tool gets its first rolls here
  String n = pickName(@PKG@.GearData.str(d, "rf", null));''')
rep(r'''  d.put("mods", rollMods(id, @PKG@.GearData.slotOf(id), r, @PKG@.GearLevel.level(id, d)));
  d.put("id", new org.bson.BsonBoolean(true));''', r'''  d.put("mods", rollMods(id, @PKG@.GearData.slotOf(id), r, @PKG@.GearLevel.level(id, d)));
  if (@PKG@.GearData.toolRolls(id)) d.put("tr", new org.bson.BsonInt32(1));         // 0.2.17
  d.put("id", new org.bson.BsonBoolean(true));''')

# ================================================================================================================ 7. GearTool: rarity boost + modifiers live
rep(r'''# double[] { fam, row, eff level, active 1/0, power factor, Fortune, need, tier } for a stack; null = not a gathering tool
M(gtool, r"""
public static double[] stats(java.util.UUID u, @IS@ s) {''', r'''# 0.2.17: the sum of one modifier key on a document
M(gtool, r"""
public static int modv(@BD@ d, String key) {
  @BA@ ms = @PKG@.GearData.mods(d);
  int s = 0;
  for (int i = 0; i < ms.size(); i++) {
    @BV@ m = ms.get(i);
    if (m == null || !m.isDocument()) continue;
    if (key.equals(@PKG@.GearData.str(m.asDocument(), "s", ""))) s = s + @PKG@.GearData.num(m.asDocument(), "v", 0);
  }
  return s;
}""")
M(gtool, r"""
public static String powKey(int f) { return f == 1 ? "mpow" : (f == 2 ? "dpow" : (f == 3 ? "cpow" : null)); }""")
M(gtool, r"""
public static String fortKey(int f) { return f == 1 || f == 2 ? "mfort" : (f == 3 ? "ffort" : "afort"); }""")
M(gtool, r"""
public static String wisKey(int f) { return f == 1 || f == 2 ? "mwis" : (f == 3 ? "fwis" : "awis"); }""")
# 0.2.17: { power factor, Fortune, Wisdom % } of a tool at level lv. A ROLLED tool (GearData.toolRolled: "tr") adds tool.rarityBoost[rarity] % to
# its level power bonus + level Fortune, then its own family's modifiers (power x (1 + %), Fortune +, Wisdom); Fortune capped at tool.fortune.cap,
# Wisdom at tool.wisdom.cap, power at x100. Any other tool document (made before 0.2.17) = exactly 0.2.16's level stats, no Wisdom.
M(gtool, r"""
public static double[] eff(int f, int lv, int t, @BD@ d) {
  double pw = power(f, lv, t);
  double fo = fortune(f, lv, t);
  if (!@PKG@.GearCfg.PART_TOOLS || f <= 0 || !@PKG@.GearData.toolRolled(d)) return new double[] { pw, fo, 0.0 };
  double rb = @PKG@.GearCfg.toolBoost(@PKG@.GearData.rarity(d)) / 100.0;
  if (pw > 1.0) pw = 1.0 + (pw - 1.0) * (1.0 + rb);
  String pk = powKey(f);
  if (pk != null) pw = pw * (1.0 + (double) modv(d, pk) / 100.0);
  if (Double.isNaN(pw) || pw < 1.0) pw = 1.0;
  if (pw > 100.0) pw = 100.0;
  fo = fo * (1.0 + rb) + (double) modv(d, fortKey(f));
  if (Double.isNaN(fo) || !(fo > 0.0)) fo = 0.0;
  if (fo > @PKG@.GearCfg.TOOL_FCAP) fo = @PKG@.GearCfg.TOOL_FCAP;
  fo = (double) Math.round(fo * 10.0) / 10.0;
  double wi = (double) modv(d, wisKey(f));
  if (Double.isNaN(wi) || !(wi > 0.0)) wi = 0.0;
  if (wi > @PKG@.GearCfg.TOOL_WCAP) wi = @PKG@.GearCfg.TOOL_WCAP;
  return new double[] { pw, fo, wi };
}""")
# double[] { fam, row, eff level, active 1/0, power factor, Fortune, need, tier, Wisdom % (0.2.17) } for a stack; null = not a gathering tool
M(gtool, r"""
public static double[] stats(java.util.UUID u, @IS@ s) {''')
rep(r'''  boolean on = g[2] != 0 && @PKG@.GearCfg.PART_TOOLS;
  double pw = on ? power(f, g[1], t) : 1.0;
  double fo = on ? fortune(f, g[1], t) : 0.0;
  return new double[] { (double) f, (double) row(f), (double) g[1], on ? 1.0 : 0.0, pw, fo, (double) g[0], (double) t };
}""")''', r'''  boolean on = g[2] != 0 && @PKG@.GearCfg.PART_TOOLS;
  double pw = 1.0;
  double fo = 0.0;
  double wi = 0.0;
  if (on) {
    double[] ef = eff(f, g[1], t, d);          // 0.2.17: rarity boost + the tool's modifiers
    pw = ef[0];
    fo = ef[1];
    wi = ef[2];
  }
  return new double[] { (double) f, (double) row(f), (double) g[1], on ? 1.0 : 0.0, pw, fo, (double) g[0], (double) t, wi };
}""")''')
rep(r'''  double tf = st != null && st[3] != 0.0 ? st[5] : 0.0;
  if (st == null || (!(tf > 0.0) && !(af > 0.0) && !(aw > 0.0))) post(u, -1, 0.0, null);
  else postX(u, (int) st[1], tf + af, ONLY[(int) st[0]], aw);
  return st;''', r'''  double tf = st != null && st[3] != 0.0 ? st[5] : 0.0;
  double tw = st != null && st[3] != 0.0 && st.length > 8 ? st[8] : 0.0;          // 0.2.17: the tool's own Wisdom (capped in eff)
  if (st == null || (!(tf > 0.0) && !(af > 0.0) && !(aw > 0.0) && !(tw > 0.0))) post(u, -1, 0.0, null);
  else postX(u, (int) st[1], tf + af, ONLY[(int) st[0]], aw + tw);
  return st;''')
rep(r'''  int lv = g[0];
  String sk = skill(f);
  if (f <= 3) {
    double pw = power(f, lv, t);
    String pct = (f == 3 ? "Chopping Power" : "Mining Power") + " +" + (int) Math.round((pw - 1.0) * 100.0) + "%";''', r'''  int lv = g[0];
  String sk = skill(f);
  double[] ef = eff(f, lv, t, d);          // 0.2.17: with the rarity boost + the tool's modifiers (a rolled tool)
  if (f <= 3) {
    double pw = ef[0];
    String pct = (f == 3 ? "Chopping Power" : (f == 2 ? "Digging Power" : "Mining Power")) + " +" + (int) Math.round((pw - 1.0) * 100.0) + "%";''')
rep(r'''  double fo = fortune(f, lv, t);
  String what = f == 3 ? "log" : (f == 2 ? "sand / gravel" : (f == 1 ? "rock / ore" : "crop"));
  txt.add(sk + " Fortune +" + @PKG@.Gear.fnum(fo) + " (" + @PKG@.Gear.fnum(fo) + "% extra " + what + " chance)");
  col.add(null);''', r'''  double fo = ef[1];
  String what = f == 3 ? "log" : (f == 2 ? "sand / gravel" : (f == 1 ? "rock / ore" : "crop"));
  txt.add(sk + " Fortune +" + @PKG@.Gear.fnum(fo) + " (" + @PKG@.Gear.fnum(fo) + "% extra " + what + " chance)");
  col.add(null);
  if (ef[2] > 0.0) { txt.add(sk + " Wisdom +" + @PKG@.Gear.fnum(ef[2]) + "% (more " + sk + " XP)"); col.add(null); }      // 0.2.17''')
rep(r'''  return "tool stats on (Mining / Chopping Power by tool level, Fortune up to " + @PKG@.Gear.fnum(@PKG@.GearCfg.TOOL_FCAP) + " through skill:bonus source gear; under-level tools work like plain tools)";''',
    r'''  return "tool stats on (Mining / Chopping Power by tool level, Fortune up to " + @PKG@.Gear.fnum(@PKG@.GearCfg.TOOL_FCAP) + " through skill:bonus source gear; under-level tools work like plain tools); crafted tool rarity " + (@PKG@.GearCfg.TOOL_RAR ? "on (boost " + @PKG@.GearCfg.TOOL_RBT + "%, tool modifiers, Wisdom up to " + @PKG@.Gear.fnum(@PKG@.GearCfg.TOOL_WCAP) + "%, craft XP " + @PKG@.GearCfg.TOOL_XPC + "%)" : "OFF (part.toolRarity)");''')

# ================================================================================================================ 8. GearView: frame, line colour, order
rep(r'''M(gvw, r"""
public static boolean dim(String key) {
  if (later(key)) return true;
  return "chg".equals(key) && !@PKG@.GearCfg.CHG_ON;
}""")''', r'''M(gvw, r"""
public static boolean dim(String key) {
  if (later(key)) return true;
  return "chg".equals(key) && !@PKG@.GearCfg.CHG_ON;
}""")
# 0.2.17: a modifier on a tool that is not a tool modifier (an old SkyyRolls tool's Damage / Strength) does nothing - grey, as before
M(gvw, r"""
public static boolean toolDead(String key) {
  int i = @PKG@.GearDefs.sIndex(key);
  return i < 0 || @PKG@.GearDefs.S_SLOT[i].indexOf('t') < 0;
}""")''')
rep(r'''    add(txt, col, modLine(k, v), (dim(k) || slot == 3) ? @PKG@.GearDefs.C_GRAY : null);''',
    r'''    add(txt, col, modLine(k, v), (dim(k) || (slot == 3 && toolDead(k))) ? @PKG@.GearDefs.C_GRAY : null);      // 0.2.17: tool modifiers are live''')
rep(r'''  statLines(id, d, txt, col);
  if (slot == 3) @PKG@.GearTool.lines(owner, id, d, txt, col);   // 0.2.12: tool power + Fortune by level''',
    r'''  if (slot == 3) @PKG@.GearTool.lines(owner, id, d, txt, col);   // 0.2.12: tool power + Fortune by level (0.2.17: above the tool modifiers)
  statLines(id, d, txt, col);''')
rep(r'''    boolean plainTool = @PKG@.GearData.isTool(id) && !@PKG@.GearData.isGear(id);''',
    r'''    boolean plainTool = @PKG@.GearData.isTool(id) && !@PKG@.GearData.isGear(id) && !@PKG@.GearData.toolRolled(doc);      // 0.2.17: a rolled tool shows its rarity''')

# ================================================================================================================ 9. Reforge + Identify accept the rolling tools
# fix round (b): a rolling tool is craftable (gets its rolled document) even with part.levels off - the craft then has no level stamp (-1), like gear
rep(r'''  if (@PKG@.GearData.isGear(id)) return true;
  return @PKG@.GearCfg.PART_LEVELS && @PKG@.GearData.isTool(id) && !"tool".equals(@PKG@.GearData.toolKind(id));''', r'''  if (@PKG@.GearData.isGear(id)) return true;
  if (@PKG@.GearData.toolRolls(id)) return true;          // 0.2.17 fix round: part.toolRarity does not depend on part.levels
  return @PKG@.GearCfg.PART_LEVELS && @PKG@.GearData.isTool(id) && !"tool".equals(@PKG@.GearData.toolKind(id));''')
# fix round (d): the Reforge page subtitle names tools
rep('''  b.set("#SkyyGSub.Text", "Pick a weapon or armor piece. Reforge re-rolls its modifiers, Level up raises it one level - both for coins.");''',
    '''  b.set("#SkyyGSub.Text", "Pick a weapon, armor piece or tool. Reforge re-rolls its modifiers, Level up raises it one level - both for coins.");''')
rep(r'''# why a stack cannot be reforged (null = it can); spec 5.4 "Which items"
M(gfg, r"""
public static String refuse(@IS@ it, @BD@ d) {
  if (it == null || it.isEmpty()) return "Pick a weapon or armor piece first.";
  String id = it.getItemId();
  if (@PKG@.GearData.isTool(id)) return "Tools get their own modifiers with gathering gear - they cannot be reforged yet.";
  if (!@PKG@.GearData.isGear(id)) return @PKG@.Gear.itemName(id) + " is not gear - only weapons and armor can be reforged.";''',
    r'''# 0.2.17: the document a reforge / level up / the page works on - the gear view, or for a rolling gathering tool WITHOUT any document (a
# tool from before 0.2) a fresh plain Normal one (it is written only when the reforge / level up succeeds; stampIfMissing gives it its level)
M(gfg, r"""
public static @BD@ docOf(String id, @BD@ md) {
  @BD@ d = @PKG@.GearData.effective(id, md);
  if (d == null && @PKG@.GearData.state(md) == 0 && @PKG@.GearData.toolRolls(id)) d = @PKG@.GearData.base(@PKG@.GearData.kindFor(id), 0, true, "tool");
  return d;
}""")
# why a stack cannot be reforged (null = it can); spec 5.4 "Which items"
M(gfg, r"""
public static String refuse(@IS@ it, @BD@ d) {
  if (it == null || it.isEmpty()) return "Pick a weapon, armor piece or tool first.";
  String id = it.getItemId();
  // 0.2.17: pickaxes, shovels, hatchets, hoes and sickles reforge like gear (tool modifiers); other tools never
  if (@PKG@.GearData.isTool(id) && !@PKG@.GearData.forgeable(id)) return @PKG@.GearData.toolFam(id) > 0 ? "Tool rarity is off on this server - tools cannot be reforged." : @PKG@.Gear.itemName(id) + " cannot be reforged - only pickaxes, shovels, hatchets, hoes and sickles.";
  if (!@PKG@.GearData.forgeable(id)) return @PKG@.Gear.itemName(id) + " is not gear - only weapons, armor and gathering tools can be reforged.";''')
rep(r'''      if (it == null || it.isEmpty() || !@PKG@.GearData.isGear(it.getItemId())) continue;
      out.add(new int[] { @PKG@.GearStamp.SCAN[k], i });''', r'''      if (it == null || it.isEmpty() || !@PKG@.GearData.forgeable(it.getItemId())) continue;          // 0.2.17: + gathering tools
      out.add(new int[] { @PKG@.GearStamp.SCAN[k], i });''')
rep(r'''  @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
  String why = refuse(it, d);
  if (why == null) why = @PKG@.GearStamp.stackWhy(it, give, "a reforge");''', r'''  @BD@ d = docOf(id, it.getMetadata());          // 0.2.17: a tool from before 0.2 gets a plain document to reforge
  String why = refuse(it, d);
  if (why == null) why = @PKG@.GearStamp.stackWhy(it, give, "a reforge");''')
rep(r'''  @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
  String why = refuse(it, d);
  if (why == null) why = @PKG@.GearStamp.stackWhy(it, give, "a level up");''', r'''  @BD@ d = docOf(id, it.getMetadata());          // 0.2.17
  String why = refuse(it, d);
  if (why == null) why = @PKG@.GearStamp.stackWhy(it, give, "a level up");''')
rep(r'''public boolean pick(@INV@ inv, int s, int slot) {
  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);
  if (it == null || it.isEmpty() || !@PKG@.GearData.isGear(it.getItemId())) return false;
  String ep = @PKG@.Gear.epoch(this.playerRef.getUuid());''', r'''public boolean pick(@INV@ inv, int s, int slot) {
  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);
  if (it == null || it.isEmpty() || !@PKG@.GearData.forgeable(it.getItemId())) return false;          // 0.2.17: + gathering tools
  String ep = @PKG@.Gear.epoch(this.playerRef.getUuid());''')
rep(r'''  String id = sel.getItemId();
  @BD@ d = @PKG@.GearData.effective(id, sel.getMetadata());
  int r = @PKG@.GearData.rarity(d);
  int lvl = @PKG@.GearLevel.level(id, d);
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelName''', r'''  String id = sel.getItemId();
  @BD@ d = @PKG@.GearForge.docOf(id, sel.getMetadata());          // 0.2.17
  int r = @PKG@.GearData.rarity(d);
  int lvl = @PKG@.GearLevel.level(id, d);
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelName''')
rep(r'''    String id = it.getItemId();
    @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
    int r = d == null ? 0 : @PKG@.GearData.rarity(d);
    int lvl = @PKG@.GearLevel.level(id, d);
    boolean on = rw[0] == this.selSec && rw[1] == this.selSlot;
    String rid = "#SkyyGRow" + i;''', r'''    String id = it.getItemId();
    @BD@ d = @PKG@.GearForge.docOf(id, it.getMetadata());          // 0.2.17: a tool from before 0.2 lists as Normal
    int r = d == null ? 0 : @PKG@.GearData.rarity(d);
    int lvl = @PKG@.GearLevel.level(id, d);
    boolean on = rw[0] == this.selSec && rw[1] == this.selSlot;
    String rid = "#SkyyGRow" + i;''')
rep(r'''    b.set("#SkyyGEmpty1.Text", "No weapons or armor on you.");''',r'''    b.set("#SkyyGEmpty1.Text", "No weapons, armor or tools on you.");''')
rep(r'''  if (!@PKG@.GearData.isGear(id)) return @PKG@.Gear.itemName(id) + " is not gear - only weapons and armor get identified.";''',
    r'''  if (!@PKG@.GearData.forgeable(id)) return @PKG@.Gear.itemName(id) + " is not gear - only weapons and armor get identified.";''')

# ================================================================================================================ 10. the mace _Next steps (named)
rep(r'''def speed_var_defaults(ints, vars_):''', r'''def speed_name_next(out_i, taken):
    """0.2.17: the chain a named Charging child <file>_Hold<key> starts (the mace's tap: Swing_Left -> its Replace -> Swing_Left_Selector -> the
    pad step) carried its Next / Failed steps INLINE; the engine configures those named steps' packets (SimpleInteraction.configurePacket ->
    Interaction.getInteractionIdOrUnknown: WARN 'Missing interaction *<step>_Next' + a SendMessage placeholder) before the batch's inline
    children load - 9 WARN lines at every start (smoke test 2026-10-10: naming only the first step moved the 9 lines one step down, to
    *<step>_Selector_Next). Every inline Next / Failed step on that chain (following string ids, Failed and Replace defaults; a Charging's own key
    map is 0.2.13's) becomes its own NAMED file <step>_Next / <step>_Failed (the id the warning names, without the inline star), in the same
    batch. Returns the new names."""
    made, seen, work = [], set(), []
    for k in sorted(out_i):
        if not k.rsplit("_", 1)[-1].startswith("Hold"):
            continue
        dv = out_i[k].get("DefaultValue") if isinstance(out_i[k], dict) else None
        work += [x for x in ((dv.get("Interactions") if isinstance(dv, dict) else None) or []) if isinstance(x, str)]
    while work:
        x = work.pop()
        if x in seen or x not in out_i or not isinstance(out_i[x], dict):
            continue
        seen.add(x)
        d = out_i[x]
        for key in ("Next", "Failed"):
            v = d.get(key)
            if isinstance(v, dict) and ("Type" in v or "Parent" in v) and d.get("Type") != "Charging":
                nm = "%s_%s" % (x, key)
                if nm in out_i or nm in taken: raise SystemExit("speed self-check: the named %s %s collides" % (key, nm))
                out_i[nm] = v
                d[key] = nm
                made.append(nm)
                work.append(nm)
            elif isinstance(v, str):
                work.append(v)
        dv = d.get("DefaultValue")
        if isinstance(dv, dict):
            work += [y for y in (dv.get("Interactions") or []) if isinstance(y, str)]
    return made


def speed_var_defaults(ints, vars_):''')
rep(r'''            speed_name_inline(oi, lambda y: G.resolved(y).get("Type"), set(cw.inter) | set(orr))      # 0.2.13 (2.)''',
    r'''            speed_name_inline(oi, lambda y: G.resolved(y).get("Type"), set(cw.inter) | set(orr))      # 0.2.13 (2.)
            SPEED_NEXT_NAMED.extend(speed_name_next(oi, set(cw.inter) | set(orr)))                   # 0.2.17 (the mace _Next)''')
rep(r'''def speed_build(cw, names, items, read_anim):''', r'''SPEED_NEXT_NAMED = []          # 0.2.17: the named <step>_Next files speed_name_next made (all tiers)


def speed_build(cw, names, items, read_anim):''')
rep(r'''assert len(_SPD_HOLD) == 18 and len([_h for _h in _SPD_HOLD if "_Mace_" in _h]) == 18, "0.2.13: the 18 named mace Charging children: %s" % _SPD_HOLD''',
    r'''assert len(_SPD_HOLD) == 18 and len([_h for _h in _SPD_HOLD if "_Mace_" in _h]) == 18, "0.2.13: the 18 named mace Charging children: %s" % _SPD_HOLD
# 0.2.17: exactly the 9 mace tap steps (3 swings x 3 tiers) had an inline Next under a named Charging child -> 9 named <step>_Next files; every
# tap step a Hold child points at now has a NAMED Next; every string id in the speed files resolves to a vanilla interaction or a speed file
assert sorted(SPEED_NEXT_NAMED) == sorted("SkyyGear_Spd%s_Mace_Weapon_Mace_Primary_Swing_%s%s_Next" % (_t, _w, _x) for _t in ("S", "F", "X")
                                          for _w in ("Left", "Right", "Up_Left") for _x in ("", "_Selector")), "0.2.17: the named mace Next steps: %s" % SPEED_NEXT_NAMED
_SPD_IDS = dict((os.path.basename(_k)[:-5], json.loads(_v)) for _k, _v in SPEED_FILES.items() if _k.startswith(SPEED_DIR_I))
for _h in _SPD_HOLD:
    for _x in (_SPD_IDS[_h].get("DefaultValue") or {}).get("Interactions") or []:
        assert not isinstance(_SPD_IDS.get(_x, {}).get("Next"), dict), "0.2.17: %s still has an inline Next" % _x
for _x in SPEED_NEXT_NAMED:
    assert _SPD_IDS[_x[:-5]]["Next"] == _x and _SPD_IDS[_x].get("Type") == ("Simple" if "_Selector_" in _x else "Replace"), _x
    assert not [_k for _k in ("Next", "Failed") if isinstance(_SPD_IDS[_x].get(_k), dict)], "0.2.17: %s still has an inline step" % _x
_SPD_REFS = []


def _spd_refs(x, top):
    for _kk in ("Next", "Failed"):
        _v = x.get(_kk)
        if isinstance(_v, str):
            _SPD_REFS.append(_v)
        elif isinstance(_v, dict) and x.get("Type") == "Charging":
            _SPD_REFS.extend(_c for _c in _v.values() if isinstance(_c, str))
    for _l in ((x.get("DefaultValue") or {}).get("Interactions") if isinstance(x.get("DefaultValue"), dict) else None, x.get("Interactions")):
        if isinstance(_l, list):
            _SPD_REFS.extend(_r for _r in _l if isinstance(_r, str))


_spd_walk([_v for _v in _SPD_IDS.values()], _spd_refs)
_SPD_MISS = sorted(set(_r for _r in _SPD_REFS if _r not in _SPD_IDS and _r not in CW.inter))
assert not _SPD_MISS, "0.2.17: speed ids that resolve to nothing: %s" % _SPD_MISS[:5]
print("0.2.17 speed: %d mace chain steps got a named Next (%s ...); %d string references in the speed files all resolve" % (len(SPEED_NEXT_NAMED), SPEED_NEXT_NAMED[0], len(_SPD_REFS)))''')

# ================================================================================================================ 11. manifest
rep(r'''gathering tools get Mining / Chopping Power (fewer hits) and Fortune (extra drops through SkyySkills) from their level, above your skill they work like plain tools;''',
    r'''gathering tools get Mining / Chopping Power (fewer hits) and Fortune (extra drops through SkyySkills) from their level, above your skill they work like plain tools; crafted pickaxes, shovels, hatchets, hoes and sickles roll a rarity like weapons and armor with tool modifiers (Power, Fortune, Wisdom - never a speed tier), reforge like gear and pay Smithing XP;''')

open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", DST)
