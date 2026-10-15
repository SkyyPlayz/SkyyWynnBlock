"""Derive SkyyTrees/build_skyytrees_0.3.10.py from the LIVE generated SkyyTrees/build_skyytrees_0.3.9.py (the tools/deploy_set.py SET pin).
Run:  python tools/trees_0_3_10_patch.py   then   python SkyyTrees/build_skyytrees_0.3.10.py   (never --deploy: coordinated deploy)
      then python SkyyTrees/test_skyytrees_0.3.10.py --dir <tools/dev/scratch/<task>/...> (bare JVM)
EDITED-SCRIPTS RULE (commit ab75b6c): the lineage is Skyy's EDITED 0.2.3 -> trees_0_2_4_patch.py -> ... -> trees_0_3_9_patch.py -> the
generated 0.3.9 read here; tools/trees_0_2_3_patch.py and older are NEVER re-run. Edit THIS file, never the generated build script.

0.3.10 = THE SPELLBLADE TREE + THE REBIRTH MODIFIER SLOTS + THE FISHING TREE + THE FARMING AVERAGE (with SkyyClasses 0.1.25; Skyy 2026-10-14
~18:30 "do 1. 3. 6. 7. 8. and 9.": '1. ... then Spellblade', '7. Rebirth wrap-up: the extra modifier slot every 5th rebirth ...', '8.
Gathering leftovers: a SkyyTrees Fishing tree, and the Farming tree reading the Farming average ...'; "Basically we are making our own runes
and modifiers, then controlling them in the skill tree ...").
WHAT CHANGES:
  - THE SPELLBLADE CLASS TREE (research/classes/Spellblade.md "Class tree paths"; SkyyClasses 0.1.25 = the 8th class): the template page 1
    (stat spine - the melee spine: Health / Strength / Focus; A1-A4 = Arcane Breach / Elemental Imbue / Sunder / the Ability 1 alt Rift
    Cleave or Shattering Arc, M<n>A / M<n>B their modifier slots, free) + page 2: trunk T1 Long Arm, T2 Steady Guard, T3 Far Crescent (the
    great shield + traversals: SkyyArmory, coming), T4 Second Wind, T5 Keen Edge, T6 Tempo; paths Tempest (Twin Attunement, Burning Rift,
    Reaction - later, Crescent Storm - SkyyArmory, Tempest), Breaker (Deep Breach, Armour Split, Opening - later, Marked for Death, Breaker
    - later), Vanguard (Shield Rhythm / Wide Shadow / Carry Through - SkyyArmory, Momentum Push, Vanguard). The K nodes are bought once
    SkyyClasses 0.1.25 lists them (tree:reads:SkyyClasses). Class level gates: the template's (trunk 5 / 10 / 15 / 25 / 40 / 55, paths
    20 / 30 / 45 / 65 / 75) - kept from the built-in table while trees.properties has no Spellblade line (TreeCfg.HAS310: no file write).
  - THE ABILITY PANEL - REBIRTH SLOTS 3 + 4 (SkyyClasses 0.1.25 o[78 ..] + modRows head fields 11-15): the ability detail cycles every
    open slot with "Next slot" (it replaces "Tree node" while an ability has more than two slots); a closed slot 3 / 4 says the rebirth it
    opens at; the card's slot 2 text shows "+1" / "+2" when rebirth slots are open. THE IMBUE ELEMENT: the Elemental Imbue detail's 5th row
    = "Element: Fire" + Change (class:fn:abilDo attune; with Twin Attunement the selected slot 2 changes the second element).
  - THE FISHING TREE (research/Gathering-Shards-Spec.md 5.4 "own tree (SkyyTrees: Fortune, bite speed, double catch, treasure chance,
    sea-creature damage later)"; SkyySkills 0.4.37 has the Fishing skill): tree 8 on the 12-slot template, its own tab (row 2 beside
    Acrobatics / Exploration), Tokens from the Fishing level, Dust from Fishing XP. Nodes: Fishing Fortune, Quick Bite, Fishing Wisdom,
    Sea Legs (+max Health - applied HERE), Treasure Hunter, Strong Line, Bait Saver, Rare Catch, Steady Reel, Fortune II, Twin Catch, Sea
    Hunter. Every node but Sea Legs is APPLIED BY ANOTHER MOD and shows "Coming with SkyyFishing" / "Coming with SkyySkills" until that mod
    lists it (tree:reads:<mod>, the 0.3 reader contract) - never a node that does nothing. The reader keys: Fishing.<Id> through
    tree:fn:bonus (fractions, like every tree); Fishing Wisdom = skill:bonus xp.fishing. No trees.properties lines are written: a file
    without Fishing lines uses the built-in numbers (the default file of a NEW server has them).
  - THE FARMING TREE'S LEVEL = THE FARMING AVERAGE (spec 5.3 "the Farming tree (SkyyTrees reads the average as the tree's level)"; Skyy
    2026-10-11 "your farming level is the average of your 3 farming skills"): skill:farmavg:<uuid> (SkyySkills 0.4.37+) is the Farming tree's
    level for Tokens and tier gates; absent (an older SkyySkills, not published yet) = the Farming level as before. Server Setup -> Trees
    -> "Farming tree uses the average" (farming.average, default ON). Dust still comes from Farming XP. Nothing a player owns is taken away:
    bought nodes keep working; a balance the lower level makes negative only blocks new buys until the average catches up (the existing
    negative-balance rules: a respec is free).
  ROLLBACK 0.3.10 -> 0.3.9: safe - the Spellblade's class tree and the Fishing tree become unknown (0.3.9 drops their saved lines at the
  profile's next save: Fishing node levels and Spellblade picks are lost, nothing else); the Farming tree reads the Farming level again.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.3.9.py")
dst = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.3.10.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
CR, LF = chr(13), chr(10)
s = raw.decode("utf8").replace(CR + LF, LF)
assert 'VERSION = "0.3.9"' in s and "GENERATED by tools/trees_0_3_9_patch.py from the LIVE build_skyytrees_0.3.8.py" in s, \
    "build_skyytrees_0.3.9.py is not the live 0.3.9 of the edited lineage"
assert "Spellblade" not in s.split("CLASSES = [")[1][:400] and '"Fishing"' not in s.split("TREES = [")[1][:200], "0.3.9 already has the 0.3.10 parts"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
CHANGES = []


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.10 = THE SPELLBLADE"):HEAD.index("  ROLLBACK 0.3.10")].rstrip()

# ================================================================================================================ header + version
rep('''"""SkyyTrees 0.3.9 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_3_9_patch.py from the LIVE build_skyytrees_0.3.8.py (the SET pin) - edit the patch, not this file. 0.3.8
was GENERATED''', '''"""SkyyTrees 0.3.10 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_3_10_patch.py from the LIVE build_skyytrees_0.3.9.py (the SET pin) - edit the patch, not this file. 0.3.9
was GENERATED by tools/trees_0_3_9_patch.py from the LIVE build_skyytrees_0.3.8.py. 0.3.8
was GENERATED''')
rep('''0.3.9 (2026-10-14; notes: tools/trees_0_3_9_patch.py) ''', '''0.3.10 (2026-10-14; notes: tools/trees_0_3_10_patch.py) ''' + NOTE[len("0.3.10 = "):].replace(LF, LF + "    ") + '''
  CHECKED: SkyyTrees/test_skyytrees_0.3.10.py (bare JVM: class compare vs 0.3.9, -Xverify:all, the Spellblade tree + panel with the real
    SkyyClasses 0.1.25, the rebirth slots, the Fishing tree, the Farming average, every 0.3.9 section, the access audit, start twice).

=== SkyyTrees 0.3.9 notes (history; still true unless 0.3.10 above says otherwise) ===
0.3.9 (2026-10-14; notes: tools/trees_0_3_9_patch.py) ''', 1)
rep('''Run:   python build_skyytrees_0.3.9.py            -> SkyyTrees/SkyyTrees-0.3.9.jar
       python build_skyytrees_0.3.9.py --deploy   -> also''', '''Run:   python build_skyytrees_0.3.10.py            -> SkyyTrees/SkyyTrees-0.3.10.jar
       python build_skyytrees_0.3.10.py --deploy   -> also''')
rep('VERSION = "0.3.9"', 'VERSION = "0.3.10"')

# ================================================================================================================ THE FISHING TREE (tree 8)
rep('''TREES = ["Mining", "Foraging", "Farming", "Cooking", "Acrobatics", "Exploration", "Alchemy", "Smithing"]
TCOLOR = ["#8fc8ff", "#8fe08a", "#f0d060", "#ffb070", "#c8a0ff", "#e0a040", "#7fe0d0", "#c0c8d0"]''',
    '''TREES = ["Mining", "Foraging", "Farming", "Cooking", "Acrobatics", "Exploration", "Alchemy", "Smithing", "Fishing"]   # 0.3.10: + Fishing
TCOLOR = ["#8fc8ff", "#8fe08a", "#f0d060", "#ffb070", "#c8a0ff", "#e0a040", "#7fe0d0", "#c0c8d0", "#6fc0e8"]   # 0.3.10: SkyySkills' Fishing colour''')
rep('''assert TREES[:6] == TREES_025 and len(TREES) == len(TCOLOR) == 8 and TREES.index("Alchemy") == 6 and TREES.index("Smithing") == 7''',
    '''assert TREES[:6] == TREES_025 and len(TREES) == len(TCOLOR) == 9 and TREES.index("Alchemy") == 6 and TREES.index("Smithing") == 7
T10 = TREES.index("Fishing")      # 0.3.10: the Fishing tree (8) - after the two 0.3 trees; its default lines are its own block (no migration)
assert T10 == 8''')
rep('''for n, k in enumerate(KINDS): T["K_" + k] = str(n)''', '''_KINDS_03 = list(KINDS)
KINDS += ["FISH"]   # 0.3.10: a "read" kind like ALCH / SMITH - stored and shown here, applied by SkyyFishing through tree:fn:bonus
assert KINDS[:27] == _KINDS_03 and KINDS.index("FISH") == 27
for n, k in enumerate(KINDS): T["K_" + k] = str(n)''')
rep('''READER_MODS = ("SkyySkills", "SkyyGear", "SkyySacks")''', '''READER_MODS = ("SkyySkills", "SkyyGear", "SkyySacks", "SkyyFishing")   # 0.3.10: + SkyyFishing (the Fishing tree)''')
rep('''    "SHaggle": ("SkyyGear",), "SMaster": ("SkyyGear",),
}''', '''    "SHaggle": ("SkyyGear",), "SMaster": ("SkyyGear",),
    # 0.3.10: the Fishing tree - SkyyFishing applies the catch nodes, SkyySkills the XP (skill:bonus xp.fishing); Sea Legs is applied here
    "NFortune": ("SkyyFishing",), "NBite": ("SkyyFishing",), "NWisdom": ("SkyySkills",), "NTreasure": ("SkyyFishing",),
    "NLine": ("SkyyFishing",), "NBait": ("SkyyFishing",), "NRare": ("SkyyFishing",), "NReel": ("SkyyFishing",), "NFortune2": ("SkyyFishing",),
    "NDouble": ("SkyyFishing",), "NHunter": ("SkyyFishing",),
}
CATCH = "SkyyFishing rolls it on every catch"''')
rep(''' ],
}
ROWS = []''', ''' ],
 # 0.3.10 (research/Gathering-Shards-Spec.md 5.4): FISHING on the 12-slot template. Every node but Sea Legs waits for its reader (SkyyFishing /
 # SkyySkills: "Coming with ..." until that mod lists Fishing.<Id> in tree:reads:<mod>) - never a node that does nothing
 "Fishing": [
  ("NFortune", "Fishing Fortune", "Fish_Salmon_Item", "FISH", 25, 0.01, 0, "+%V double-catch chance", CATCH + " - one more fish of the same kind", "", ""),
  ("NBite", "Quick Bite", "Fish_Minnow_Item", "FISH", 20, 0.01, 0, "-%V wait for a bite", "SkyyFishing shortens the wait before a fish bites", "", ""),
  ("NWisdom", "Fishing Wisdom", "Fish_Frostgill_Item", "XP", 15, 0.01, 0, "+%V Fishing XP", "Every catch that pays Fishing XP pays more (SkyySkills, skill:bonus xp.fishing)", "", ""),
  ("NSea", "Sea Legs", "Fish_Crab_Item", "HP", 10, 1.0, 0, "+%V max Health", ON, "", ""),
  ("NTreasure", "Treasure Hunter", "Furniture_Ancient_Chest_Small", "FISH", 10, 0.005, 0, "+%V treasure chance", CATCH + " - a treasure instead of a fish", "", ""),
  ("NLine", "Strong Line", "Deco_Rope", "FISH", 15, 0.02, 0, "-%V reel and line wear", "SkyyFishing wears your rigged parts out slower", "", ""),
  ("NBait", "Bait Saver", "Fish_Bluegill_Item", "FISH", 10, 0.03, 0, "%V chance a bait is not used up", CATCH, "", ""),
  ("NRare", "Rare Catch", "Fish_Clownfish_Item", "FISH", 10, 0.01, 0, "+%V chance of a rarer fish", CATCH + " - the next rarity up", "", ""),
  ("NReel", "Steady Reel", "Fish_Pike_Item", "FISH", 10, 0.02, 0, "+%V reel strength", "SkyyFishing: big fish tire faster on your line", "", ""),
  ("NFortune2", "Fortune II", "Fish_Trout_Rainbow_Item", "FISH", 20, 0.01, 0, "+%V double-catch chance - adds to Fortune", "Stacks with Fishing Fortune (SkyyFishing)", "", ""),
  ("NDouble", "Twin Catch", "Fish_Tang_Blue_Item", "FISH", 10, 0.01, 0, "%V chance of two extra fish", CATCH + " - a roll of its own after Fortune", "", ""),
  ("NHunter", "Sea Hunter", "Fish_Shark_Hammerhead_Item", "FISH", 5, 0.05, 0, "+%V damage to sea creatures", "SkyyFishing's sea creatures (later) - comes with them", "", ""),
 ],
}
ROWS = []''')
rep('''assert len(ROWS) == 96 and len(set(r["id"] for r in ROWS)) == 96   # 0.3: + Alchemy (72-83) and Smithing (84-95)''',
    '''assert len(ROWS) == 108 and len(set(r["id"] for r in ROWS)) == 108   # 0.3: + Alchemy (72-83) and Smithing (84-95); 0.3.10: + Fishing (96-107)''')
rep('''assert [r["id"] for r in ROWS if r["t"] >= T03 and not r["readers"]] == ["PMana", "SHealth"]''',
    '''assert [r["id"] for r in ROWS if r["t"] >= T03 and not r["readers"]] == ["PMana", "SHealth", "NSea"]   # 0.3.10: + Sea Legs (applied here)
_N = [r for r in ROWS if r["t"] == T10]
assert [r["id"] for r in _N] == ["NFortune", "NBite", "NWisdom", "NSea", "NTreasure", "NLine", "NBait", "NRare", "NReel", "NFortune2", "NDouble", "NHunter"]
assert all(r["max"] == SLOT_MAX[r["s"] - 1] and r["lk"] == "" for r in _N) and [KINDS[r["kind"]] for r in _N].count("FISH") == 10
assert sum(sum(r["B"] * n ** 3 for n in range(1, r["max"])) for r in _N) == 37778125, "0.3.10: the template cost (37,778,125 Dust to max)"''')
# the default file: the 0.3 block holds only Alchemy + Smithing (TreeMig's block stays byte for byte); Fishing = its own block, no migration
rep('''DL.extend(DEF03_HEAD)
for r in ROWS:
    if r["t"] >= T03: DL.extend(node_lines(r))''', '''DL.extend(DEF03_HEAD)
for r in ROWS:
    if T03 <= r["t"] < T10: DL.extend(node_lines(r))
# 0.3.10: the Fishing tree's lines (a NEW server's file); an existing file is NOT rewritten - missing lines = these built-in numbers
DEF310_HEAD = ["# ---- Fishing tree (SkyyTrees 0.3.10; a file without these lines uses the same built-in numbers) ----",
               "# Every node but Sea Legs is applied by SkyyFishing or SkyySkills: it shows 'Coming with <mod>' until that mod says it applies it."]
DL.extend(DEF310_HEAD)
for r in ROWS:
    if r["t"] == T10: DL.extend(node_lines(r))
DL.extend(["# Farming tree level = the average of Farming, Ranching and Orchard (SkyySkills skill:farmavg) - false = the Farming level (0.3.10)",
           "farming.average=true"])''')
rep('''for r in ROWS:
    if r["t"] >= T03:
        for _l in node_lines(r): ADD03.append(("" if _l.startswith("#") else _l.split("=", 1)[0], _l))''',
    '''for r in ROWS:
    if T03 <= r["t"] < T10:   # 0.3.10: the 0.3 block stays Alchemy + Smithing only
        for _l in node_lines(r): ADD03.append(("" if _l.startswith("#") else _l.split("=", 1)[0], _l))''')
rep('''DL = ["# SkyyTrees %s - skill trees for Mining, Foraging, Farming, Cooking, Alchemy, Smithing, Acrobatics and Exploration.''',
    '''DL = ["# SkyyTrees %s - skill trees for Mining, Foraging, Farming, Cooking, Alchemy, Smithing, Acrobatics, Exploration and Fishing.''')
# the tab rows: Fishing beside Acrobatics + Exploration
rep('''               [TREES.index(_n) for _n in ("Acrobatics", "Exploration")]]''', '''               [TREES.index(_n) for _n in ("Acrobatics", "Exploration", "Fishing")]]   # 0.3.10: + Fishing''')
# Fishing Wisdom = skill:bonus xp.fishing (SkyySkills applies it for the skills in bridge.bonus.xpSkills)
rep('''  putNZ(m, "xp.smithing", v[@I_SWISDOM@]);''', '''  putNZ(m, "xp.smithing", v[@I_SWISDOM@]);
  putNZ(m, "xp.fishing", v[@I_NWISDOM@]);     // 0.3.10: the Fishing tree (SkyySkills lists Fishing.NWisdom when it applies it)''')

# ================================================================================================================ THE FARMING AVERAGE
rep('''             "int FELLER_ALL = 64", "int[] FELLER_LOGS = @FELLER_DEF@", "boolean FELLED_NODES = true", "boolean SWING_ON = true",''',
    '''             "int FELLER_ALL = 64", "int[] FELLER_LOGS = @FELLER_DEF@", "boolean FELLED_NODES = true", "boolean SWING_ON = true",
             "boolean FARM_AVG = true", "boolean HAS310 = true",   # 0.3.10: farming.average; the file holds Spellblade class lines''')
rep('''  SWING_ON = bool(p, "swing.enabled", true);''', '''  SWING_ON = bool(p, "swing.enabled", true);
  FARM_AVG = bool(p, "farming.average", true);   // 0.3.10: the Farming tree's level = skill:farmavg (the three farming skills' average)''')
rep('''    ("swing.enabled", "Faster tool swings", "abilities", "bool", "true", "", "", "", "", "live",
     "ON: Mining / Chopping Speed shorten the wait between pickaxe / hatchet swings. OFF: they do nothing.", "reload"),''',
    '''    ("swing.enabled", "Faster tool swings", "abilities", "bool", "true", "", "", "", "", "live",
     "ON: Mining / Chopping Speed shorten the wait between pickaxe / hatchet swings. OFF: they do nothing.", "reload"),
    # 0.3.10 (research/Gathering-Shards-Spec.md 5.3)
    ("farming.average", "Farming tree uses the average", "general", "bool", "true", "", "", "", "", "live",
     "ON: Farming tree level = average of Farming, Ranching, Orchard (SkyySkills). OFF: Farming level.", "reload"),''')
rep('''assert len(_exact) == 19 + EXTRA_EXACT_ROWS and len(CFG_ROWS) == 20 + len(TREES) + EXTRA_EXACT_ROWS + EXTRA_TABLE_ROWS and len(CFG_ROWS) == 43   # 0.3.3: + Assassin, Monk
assert [r[0] for r in CFG_ROWS].count("class.enabled") == 1 and len(set(r[0] for r in CFG_ROWS)) == 43''',
    '''assert len(_exact) == 20 + EXTRA_EXACT_ROWS and len(CFG_ROWS) == 21 + len(TREES) + EXTRA_EXACT_ROWS + EXTRA_TABLE_ROWS and len(CFG_ROWS) == 46   # 0.3.3: + Assassin, Monk; 0.3.10: + farming.average, nodes.Fishing, class.nodes.Spellblade
assert [r[0] for r in CFG_ROWS].count("class.enabled") == 1 and len(set(r[0] for r in CFG_ROWS)) == 46''')
rep('''# -1 = SkyySkills not loaded; else the active profile's level of that skill (0 for a skill SkyySkills does not know yet)
M(calc, r"""
public static int level(java.util.UUID u, int t) {
  java.util.function.Function f = fn("skill:fn:level");
  if (f == null) return -1;''', '''# -1 = SkyySkills not loaded; else the active profile's level of that skill (0 for a skill SkyySkills does not know yet)
# 0.3.10: the Farming tree's level = the Farming average (floor((Farming + Ranching + Orchard) / 3), SkyySkills 0.4.37+: skill:fn:level
# "farmingavg", the active profile) while farming.average is on and SkyySkills publishes skill:farmavg:<uuid>; absent = the Farming level as before
M(calc, r"""
public static int farmAvg(java.util.UUID u) {
  try {
    Object o = @PKG@.TreeStore.bridge().get("skill:farmavg:" + u.toString());
    if (!(o instanceof Number)) return -1;
    // fix round (critic): skill:farmavg:<uuid> only says SkyySkills knows the average - it can lag a profile switch by a tick, so the level
    // itself comes from skill:fn:level "farmingavg" (SkyySkills 0.4.37+: the ACTIVE profile, resolved on the call); the bridge number is the
    // fallback only when that call answers nothing
    java.util.function.Function f = fn("skill:fn:level");
    if (f != null) {
      Object r = f.apply(new Object[] { u, "farmingavg" });
      if (r instanceof Number) { int a = ((Number) r).intValue(); return a < 0 ? 0 : a; }
    }
    int l = ((Number) o).intValue();
    return l < 0 ? 0 : l;
  } catch (Throwable e) { }
  return -1;
}""")
M(calc, r"""
public static int level(java.util.UUID u, int t) {
  java.util.function.Function f = fn("skill:fn:level");
  if (f == null) return -1;
  if (t == @T_FARMING@ && @PKG@.TreeCfg.FARM_AVG && u != null) { int fa = farmAvg(u); if (fa >= 0) return fa; }''')
assert "# -1 = SkyySkills not loaded" in s

# ================================================================================================================ THE SPELLBLADE CLASS TREE
rep('''CLASSES = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk"]   # 0.3.3: + Assassin, Monk (SkyyClasses 0.1.14)
CSKILL = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity", "Assassination", "Zen"]   # 0.3.5: what players see (Monk = Zen, LOCKED 2026-10-08)''',
    '''CLASSES = ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Monk", "Spellblade"]   # 0.3.3: + Assassin, Monk (SkyyClasses 0.1.14); 0.3.10: + Spellblade (SkyyClasses 0.1.25)
CSKILL = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity", "Assassination", "Zen", "Battlemagic"]   # 0.3.5: what players see (Monk = Zen, LOCKED 2026-10-08)''')
rep('''CSKILL_KEY = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity", "Assassination", "Discipline"]''',
    '''CSKILL_KEY = ["Archery", "Swordsmanship", "Sorcery", "Fury", "Divinity", "Assassination", "Discipline", "Battlemagic"]''')
rep('''CMAGIC = [False, False, True, False, True, False, False]''', '''CMAGIC = [False, False, True, False, True, False, False, False]   # 0.3.10: the Spellblade takes the melee spine (Health / Strength / Focus)''')
# fix round (critic): the Spellblade's icon goes AFTER the Monk's Bo staff (CLASSES order) - never shift the Monk's icon
rep('''CICON = ["Weapon_Shortbow_Iron", "Weapon_Sword_Iron", "Weapon_Staff_Iron", "Weapon_Battleaxe_Iron", "Weapon_Wand_Wood", "Weapon_Daggers_Iron",
         "Weapon_Staff_Bo_Wood"]''',
    '''CICON = ["Weapon_Shortbow_Iron", "Weapon_Sword_Iron", "Weapon_Staff_Iron", "Weapon_Battleaxe_Iron", "Weapon_Wand_Wood", "Weapon_Daggers_Iron",
         "Weapon_Staff_Bo_Wood", "Weapon_Longsword_Iron"]
assert CICON[CLASSES.index("Monk")] == "Weapon_Staff_Bo_Wood" and CICON[CLASSES.index("Spellblade")] == "Weapon_Longsword_Iron", CICON''')
rep('''CCOLOR = ["#8fd67a", "#e0b060", "#7fb0e0", "#d9443f", "#f2e6a0", "#b58cff", "#f08a30"]   # 0.3.3: + Assassin, Monk (SkyySkills 0.4.21 rows)''',
    '''CCOLOR = ["#8fd67a", "#e0b060", "#7fb0e0", "#d9443f", "#f2e6a0", "#b58cff", "#f08a30", "#6fd0d8"]   # 0.3.3: + Assassin, Monk (SkyySkills 0.4.21 rows); 0.3.10: + Spellblade''')
rep('''assert len(CLASSES) == len(CSKILL) == len(CMAGIC) == len(CICON) == len(CCOLOR) == 7''', '''assert len(CLASSES) == len(CSKILL) == len(CMAGIC) == len(CICON) == len(CCOLOR) == 8''')
def _arm(x): return "Waits for the great shield / the Spellblade moves in SkyyArmory (not built) - it lists Class.Spellblade." + x + " then"
SB_PATHS = """
# 0.3.10 (research/classes/Spellblade.md "Class tree paths"; LOCKED popup batch 1: paths Tempest / Breaker / Vanguard). T4 / T5 use
# SkyyClasses' own Momentum numbers (Server Setup -> Classes -> Momentum numbers): amount 0 here, so no double source; T6 Tempo reads the Amount
CPATHS["Spellblade"] = (("Tempest", "Breaker", "Vanguard"), ("Weapon_Longsword_Flame", "Weapon_Longsword_Spectral", "Weapon_Shield_Iron"), [
   ("Long Arm", "A", 25, "Longsword arcs reach %A% of a block further", @T1@, "Weapon_Longsword_Iron"),
   ("Steady Guard", "A", 15, "Great shield guard costs %A% less Stamina", @T2@, "Weapon_Shield_Iron"),
   ("Far Crescent", "A", 15, "Crescent Rush and Bulwark Charge go %A% farther", @T3@, "Weapon_Longsword_Spectral"),
   ("Second Wind", "K", 0, "Once a minute, losing all your Momentum keeps a few stacks", None, "Potion_Health"),
   ("Keen Edge", "K", 0, "Your longsword and Zweihander hits deal more damage", None, "Weapon_Longsword_Iron"),
   ("Tempo", "K", 5, "All Spellblade ability cooldowns -%A%", None, "Deco_Scroll")], [
   ("Twin Attunement", "K", 0, "Imbue alternates two attuned elements - Imbue 2 s shorter", None, None),
   ("Burning Rift", "K", 0, "An imbued Breach or Rift arc leaves element patches - cost +3 Mana", None, None),
   ("Reaction", "L", 0, "Statuses of two elements react in a burst - element damage -10%", "Needs element reactions (none at launch) - a later build applies Class.Spellblade.PA3", None),
   ("Crescent Storm", "A", 0, "The crescent fires from 5 Momentum and splits in 3 - dash 1 block shorter", @PA4@, None),
   ("Tempest", "K", 0, "Unstoppable: every 5th hit rings your element - stacks decay faster", None, None)], [
   ("Deep Breach", "K", 0, "Breach on bosses +5 points - on other mobs -3", None, None),
   ("Armour Split", "K", 0, "Sunder also cuts defence 10% - cooldown +4 s", None, None),
   ("Opening", "L", 0, "A Sundered boss breaks out 1 s later - you take +10% from it", "Needs SkyyArmory's boss breakout window - a later build applies Class.Spellblade.PB3", None),
   ("Marked for Death", "K", 0, "Breached + Sundered targets take 10% more - Breach 1 s shorter", None, None),
   ("Breaker", "L", 0, "Sunder's first hit strips one boss buff or shield - cost +6 Mana", "Needs SkyyMobs' elite affixes - a later build applies Class.Spellblade.PB5", None)], [
   ("Shield Rhythm", "A", 0, "Great shield bashes give +2 Momentum - sword hits at most +1 a swing", @PC1@, None),
   ("Wide Shadow", "A", 0, "The guard shelters allies 4 blocks behind for 30% - you are slower", @PC2@, None),
   ("Momentum Push", "K", 0, "The Momentum push reaches farther - less attack speed per stack", None, None),
   ("Carry Through", "A", 0, "Bulwark Charge dumps the crowd in one Breached pile - 2 blocks shorter", @PC4@, None),
   ("Vanguard", "K", 0, "Unstoppable: you take less damage - max Momentum 18", None, None)])
"""
for _x in ("T1", "T2", "T3", "PA4", "PC1", "PC2", "PC4"): SB_PATHS = SB_PATHS.replace("@" + _x + "@", repr(_arm(_x)))
rep("CABIL = {   # 0.3.7: A1-A4 = ability lines 1-4", SB_PATHS.lstrip(LF) + "CABIL = {   # 0.3.7: A1-A4 = ability lines 1-4")
rep('''            ("Rain or Net", "Enables your Ability 1 alt: Arrow Rain or Hunter's Net", "Ability 1 Alt", "your Ability 1 alt")],
}''', '''            ("Rain or Net", "Enables your Ability 1 alt: Arrow Rain or Hunter's Net", "Ability 1 Alt", "your Ability 1 alt")],
 # 0.3.10 (SkyyClasses 0.1.25)
 "Spellblade": [("Arcane Breach", "Enables Arcane Breach (ability line 1)", "Arcane Breach", "Arcane Breach"),
                ("Elemental Imbue", "Enables Elemental Imbue (ability line 2)", "Imbue", "Elemental Imbue"),
                ("Sunder", "Enables Sunder (ability line 3)", "Sunder", "Sunder"),
                ("Rift or Shatter", "Enables your Ability 1 alt: Rift Cleave or Shattering Arc", "Ability 1 Alt", "your Ability 1 alt")],
}''')
rep('''assert [c["name"] for c in CN if CT_ID[c["n"]] == "X1"] == ["Edge", "Edge", "Wellspring", "Edge", "Wellspring", "Edge", "Edge"]''',
    '''assert [c["name"] for c in CN if CT_ID[c["n"]] == "X1"] == ["Edge", "Edge", "Wellspring", "Edge", "Wellspring", "Edge", "Edge", "Edge"]   # 0.3.10: + Spellblade''')
rep('''assert [c["name"] for c in CN if c["hid"]] == ["Switch"] * 6 and''', '''assert [c["name"] for c in CN if c["hid"]] == ["Switch"] * 7 and''')
# the class level gates of the Spellblade (a file without any class.nodes.Spellblade line keeps the built-in levels - no file write)
rep('''F(cls, "public static final boolean[] NEW33 = %s;" % jbool([("%s.%s" % (CLASSES[c["ci"]], CT_ID[c["n"]])) not in OLD32_PAIRS for c in CN]))   # 0.3.3 fix 2''',
    '''F(cls, "public static final boolean[] NEW33 = %s;" % jbool([("%s.%s" % (CLASSES[c["ci"]], CT_ID[c["n"]])) not in OLD32_PAIRS for c in CN]))   # 0.3.3 fix 2
F(cls, "public static final boolean[] NEW310 = %s;" % jbool([CLASSES[c["ci"]] == "Spellblade" for c in CN]))   # 0.3.10: the Spellblade pairs''')
rep('''  HAS33 = has33;
  C_ON = con; C_AMT = cam; C_AP = cap; C_MIN = cmn;''', '''  HAS33 = has33;
  // 0.3.10: the same rule for the Spellblade (SkyyClasses 0.1.25): no class.nodes.Spellblade line = its lines are not in this file (no
  // migration writes them) - a missing class.minLevel line of a Spellblade node keeps its built-in level instead of "no level needed"
  boolean has310 = false;
  for (int j = 0; j < cnn && !has310; j++) {
    if (!@PKG@.TreeClass.NEW310[j]) continue;
    if (p.getProperty("class.nodes." + @PKG@.TreeClass.CLASSES[j / @PKG@.TreeClass.NN] + "." + @PKG@.TreeClass.NID[j % @PKG@.TreeClass.NN]) != null) has310 = true;
  }
  if (!has310) {
    for (int j = 0; j < cnn; j++) {
      if (!@PKG@.TreeClass.NEW310[j]) continue;
      String mk3 = "class.minLevel." + @PKG@.TreeClass.CLASSES[j / @PKG@.TreeClass.NN] + "." + @PKG@.TreeClass.NID[j % @PKG@.TreeClass.NN];
      if (p.getProperty(mk3) == null) cmn[j] = @PKG@.TreeClass.CMIN[j];
    }
  }
  HAS310 = has310;
  C_ON = con; C_AMT = cam; C_AP = cap; C_MIN = cmn;''')

rep("assert NHID == 6 and NMIN == NC * 24 + 1, (NHID, NMIN)", "assert NHID == 7 and NMIN == NC * 24 + 1, (NHID, NMIN)   # 0.3.10: + the Spellblade's hidden Switch")

# ================================================================================================================ THE ABILITY PANEL: rebirth slots 3 + 4, the Imbue element
rep('''  int msl = this.mslot;
  if (msl < 0 || msl > 1) msl = 0;''', '''  int msl = this.mslot;
  if (msl < 0 || msl > 3) msl = 0;   // 0.3.10: slots 3 + 4 (rebirth)''')
rep('''    int aslots = 0;
    try { aslots = Integer.parseInt(ah[6]); } catch (Throwable x) { aslots = 0; }
    String e0 = ah[7];
    String e1 = ah[8];
    String cur = msl == 0 ? e0 : e1;
    boolean slotOpen = msl < aslots;''', '''    int aslots = 0;
    try { aslots = Integer.parseInt(ah[6]); } catch (Throwable x) { aslots = 0; }
    String e0 = ah[7];
    String e1 = ah[8];
    String e2 = ah.length > 12 ? ah[11] : "";   // 0.3.10: SkyyClasses 0.1.25's slots 3 + 4 (head fields 11 / 12)
    String e3 = ah.length > 12 ? ah[12] : "";
    int rbs = 0;
    try { if (ah.length > 13) rbs = Integer.parseInt(ah[13].trim()); } catch (Throwable x3) { rbs = 0; }
    String att = ah.length > 15 ? ah[15] : "";   // the Imbue attunement ("" = not Imbue)
    // fix round: a closed rebirth slot names the rebirth from the live rb.modSlotEvery / rb.modSlotMax (head fields 16 / 17; an older
    // SkyyClasses 0.1.25 build without them = the defaults 5 / 2) - the same rule as SkyyClasses' slotHint
    long rbEv = 5L;
    long rbMx = 2L;
    int tsl = 2;
    try { if (ah.length > 17) { rbEv = Long.parseLong(ah[16].trim()); rbMx = Long.parseLong(ah[17].trim()); } } catch (Throwable x4) { rbEv = 5L; rbMx = 2L; }
    try { if (ah.length > 14) tsl = Integer.parseInt(ah[14].trim()); } catch (Throwable x5) { tsl = 2; }
    if (rbMx > 2L) rbMx = 2L;
    int needRb = msl + 1 - tsl;   // rebirth slots this slot needs (slots fill tree first, then rebirth)
    String closedRb = (rbEv > 0L && needRb >= 1 && (long) needRb <= rbMx) ? "opens at rebirth " + ((long) needRb * rbEv) : (tsl < 2 ? "unlock the tree slots first" : "no more slots on this server");
    String cur = msl == 0 ? e0 : (msl == 1 ? e1 : (msl == 2 ? e2 : e3));
    boolean slotOpen = msl < aslots;''')
rep('''    b.set("#SkyyTrAdM.Text", rbp > 0 ? "Rebirth: " + rbp + " upgrade" + (rbp == 1 ? "" : "s") + " - press Max Up" : (slotOpen ? "Modifier slot " + (msl + 1) + (cur.length() > 0 ? " - now " + cur : " - empty") : "Modifier slot " + (msl + 1) + " - unlock M" + ((Integer) ap[ab0 + 5]).intValue() + (msl == 0 ? "A" : "B") + " in the tree"));''',
    '''    b.set("#SkyyTrAdM.Text", rbp > 0 ? "Rebirth: " + rbp + " upgrade" + (rbp == 1 ? "" : "s") + " - press Max Up" : (slotOpen ? "Modifier slot " + (msl + 1) + " of " + aslots + (cur.length() > 0 ? " - now " + cur : " - empty") : (msl >= 2 ? "Modifier slot " + (msl + 1) + " - " + closedRb : "Modifier slot " + (msl + 1) + " - unlock M" + ((Integer) ap[ab0 + 5]).intValue() + (msl == 0 ? "A" : "B") + " in the tree")));''')
rep('''      boolean un = "1".equals(f[3]);
      boolean inThis = f[0].equals(cur);
      boolean inOther = f[0].equals(msl == 0 ? e1 : e0);''', '''      boolean un = "1".equals(f[3]);
      boolean inThis = f[0].equals(cur);
      int inOthers = (msl != 0 && f[0].equals(e0) ? 1 : 0) + (msl != 1 && f[0].equals(e1) ? 1 : 0) + (msl != 2 && f[0].equals(e2) ? 1 : 0) + (msl != 3 && f[0].equals(e3) ? 1 : 0);   // 0.3.10: 4 slots
      boolean inOther = inOthers == 1;
      if (inOthers >= 2) inOther = true;''')
rep('''      int rs = (!slotOpen || !un) ? 0 : (inThis ? 1 : (inOther && "1".equals(f[11]) ? 2 : (inOther ? 3 : 4)));''',
    '''      int rs = (!slotOpen || !un) ? 0 : (inThis ? 1 : (inOther && inOthers == 1 && "1".equals(f[11]) ? 2 : (inOther ? 3 : 4)));''')
rep('''    b.set("#SkyyTrAdH.Text", "Modifiers unlock with the ability's own level and level up while equipped (each counted use). A stackable one can sit in both slots from its Lv 2 (double effect). Swap out of combat.");
    ev.addEventBinding(@BT@.Activating, "#SkyyTrAu", @EVD@.of("a", "trmu"));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrAv", @EVD@.of("a", "trtree"));''',
    '''    if (att.length() > 0 && amr.length - 1 < 5) {   // 0.3.10: Elemental Imbue - the 5th row = the element (attunement) + Change
      int k = 4;
      int rs = 6;
{{AROWATT}}
      boolean twin = att.indexOf('+') > 0;
      String a1 = twin ? att.substring(0, att.indexOf('+')) : att;
      String a2 = twin ? att.substring(att.indexOf('+') + 1) : "";
      b.set("#SkyyTrAt" + k + ".Text", "Element: " + a1 + (twin ? " + " + a2 + " (pick slot 2, then Change, for the second)" : "") + " - Imbue uses it; an Elemental sword uses its own. Change it out of combat.");
      ev.addEventBinding(@BT@.Activating, "#SkyyTrAq" + k, @EVD@.of("a", "trmat"));
    }
    b.set("#SkyyTrAdH.Text", "Modifiers unlock with the ability's own level and level up while equipped (each counted use). A stackable one can fill two slots from its Lv 2 (double effect). Swap out of combat." + (rbs > 0 ? " Rebirth: +" + rbs + " slot" + (rbs == 1 ? "" : "s") + "." : ""));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrAu", @EVD@.of("a", "trmu"));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrAv", @EVD@.of("a", aslots > 2 ? "trmnx" : "trtree"));   // 0.3.10: Next slot while it has 3 or 4''')
rep('''                SUI.button("SkyyTrAq" + k_, "Equip", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8})])]''',
    '''                SUI.button("SkyyTrAq" + k_, "Equip", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8})])]
    # 0.3.10: the Imbue element row (the 5th row, rs 6): the same row shape, its button says Change
    arow_att = [app("SkyyTrDet", SUI.group("SkyyTrAr" + k_, "Left", h=TRC_AD_ROW_H, anchor={"bottom": 4})),
                app("SkyyTrAr" + k_, SUI.label("SkyyTrAt" + k_, "", "rowSub", w=TRC_AD_TXT_W, h=TRC_AD_ROW_H, wrap=True)),
                app("SkyyTrAr" + k_, SUI.button("SkyyTrAq" + k_, "Change", "secondary", size="small", w=TRC_AD_BTN_W, anchor={"left": 8}))]''')
rep('''             app("SkyyTrAdB", SUI.button("SkyyTrAv", "Tree node", "secondary", w=TR_BUY_W, anchor={"left": 8}))]''',
    '''             app("SkyyTrAdB", SUI.choose(SUI.J("aslots > 2"), SUI.button("SkyyTrAv", "Next slot", "secondary", w=TR_BUY_W, anchor={"left": 8}),
                                         SUI.button("SkyyTrAv", "Tree node", "secondary", w=TR_BUY_W, anchor={"left": 8})))]   # 0.3.10''')
rep('''        "DETP": detp, "DET": "\\n".join(det), "BUY": "\\n".join(buy), "ADET": "\\n".join(adet), "AROW": "\\n".join(arow),''',
    '''        "DETP": detp, "DET": "\\n".join(det), "BUY": "\\n".join(buy), "ADET": "\\n".join(adet), "AROW": "\\n".join(arow), "AROWATT": "\\n".join(arow_att),''')
rep('''              "ADET": 4, "AROW": 6, "FOOT": 2, "RESPEC": 2}''', '''              "ADET": 4, "AROW": 6, "AROWATT": 6, "FOOT": 2, "RESPEC": 2}''')
# the card's slot 2 text: "+1" / "+2" when rebirth slots are open
rep('''public static String slotText(Object[] ap, int i, int j, int line) {
  int b0 = 12 + i * 16;
  int slots = ((Integer) ap[b0 + 14]).intValue();
  if (j >= slots) return "Tree: M" + line + (j == 0 ? "A" : "B");
  String m = String.valueOf(ap[b0 + 10 + j * 2]);
  if (m.length() == 0) return "Empty slot " + (j + 1);
  return m + " " + ((Integer) ap[b0 + 11 + j * 2]).intValue();
}''', '''public static String slotText(Object[] ap, int i, int j, int line) {
  int b0 = 12 + i * 16;
  int slots = ((Integer) ap[b0 + 14]).intValue();
  if (j >= slots) return "Tree: M" + line + (j == 0 ? "A" : "B");
  String m = String.valueOf(ap[b0 + 10 + j * 2]);
  String more = j == 1 && slots > 2 && ap.length >= 94 ? " +" + (slots - 2) : "";   // 0.3.10: the rebirth slots 3 + 4 (in the detail)
  if (m.length() == 0) return "Empty slot " + (j + 1) + more;
  return m + " " + ((Integer) ap[b0 + 11 + j * 2]).intValue() + more;
}''')
# the page events: Next slot, Change (the Imbue element)
rep('''      if (data.indexOf("trtree\\"") >= 0) { this.amode = false; this.msg = ""; rebuild(); return; }''',
    '''      if (data.indexOf("trtree\\"") >= 0) { this.amode = false; this.msg = ""; rebuild(); return; }
      if (data.indexOf("trmnx\\"") >= 0) { this.mslot = (this.mslot + 1) % 4; this.msg = ""; rebuild(); return; }   // 0.3.10: Next slot (1 - 4)
      if (data.indexOf("trmat\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "attune", this.aslot, this.mslot); rebuild(); return; }   // 0.3.10: the Imbue element''')
rep('''  if (act.equals("unequip")) return said(@PKG@.TreeClass.ado(u, "unequip", id, String.valueOf(this.mslot), csv));''',
    '''  if (act.equals("unequip")) return said(@PKG@.TreeClass.ado(u, "unequip", id, String.valueOf(this.mslot), csv));
  if (act.equals("attune")) return said(@PKG@.TreeClass.ado(u, "attune", "next", k == 1 ? "2" : "1", csv));   // 0.3.10: k = the selected slot (slot 2 = the second element)''')

# ================================================================================================================ fix round: Sea Legs in max Health
# fix round (critic HIGH): Sea Legs (NSea, +1 max Health a level) was in the effect vector but not in skyytree_health - the Health total is a
# helper now (healthOf, executed by the harness) and adds v[NSea]
rep('''# 0.3: + Forge Hardened in skyytree_health, the new skyytree_mana (Deep Reserves) - the same mod() call (SkyySkills' skyyskill_mana pattern)
M(fx, r"""''', '''# 0.3.10 fix round: the skyytree_health total (+ Sea Legs, the Fishing tree)
M(fx, r"""
public static double healthOf(java.util.UUID u, double[] v) {
  return v[@I_FVIGOR@] + v[@I_AHEARTY@] + v[@I_CFED@] + v[@I_EHEART@] + v[@I_EHEART2@] + v[@I_SHEALTH@] + v[@I_NSEA@] + extraStat(u, 0);
}""")
# 0.3: + Forge Hardened in skyytree_health, the new skyytree_mana (Deep Reserves) - the same mod() call (SkyySkills' skyyskill_mana pattern)
M(fx, r"""''')
rep('''    double hp = v[@I_FVIGOR@] + v[@I_AHEARTY@] + v[@I_CFED@] + v[@I_EHEART@] + v[@I_EHEART2@] + v[@I_SHEALTH@] + extraStat(u, 0);''',
    '''    double hp = healthOf(u, v);   // 0.3.10 fix round: + Sea Legs''')

# ================================================================================================================ done
assert s.count("registerSystem(") == REG0, "no new system"
assert s.count("registerCommand(") == CMD0, "no new command"
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote %s (%d changes, %d lines)" % (dst, len(CHANGES), s.count(LF)))
