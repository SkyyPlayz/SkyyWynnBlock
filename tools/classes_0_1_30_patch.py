"""Derive SkyyClasses/build_skyyclasses_0.1.30.py from the GENERATED SkyyClasses 0.1.29 (build_skyyclasses_0.1.29.py = the
tools/deploy_set.py SET pin; the EDITED lineage: Skyy's hand-edited 0.1.6 (commit ab75b6c) -> classes_0_1_7_patch.py -> ... ->
classes_0_1_29_patch.py -> 0.1.29). Never re-run an older patch, never edit a generated script - edit this patch. Every anchor is asserted;
at the end every change is undone on a copy and compared with 0.1.29 (nothing else changed). Line endings kept.
Run:  python tools/classes_0_1_30_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.30.py   (never --deploy)
      then  python SkyyClasses/test_skyyclasses_0.1.30.py

0.1.30 (2026-10-16) = MODIFIERS OUT OF THE TREE + EVERY ABILITY SAYS WHAT IT DOES (round cls0130, with SkyyTrees 0.3.18). Skyy 2026-10-16
  (screenshot: Spellblade Lattice, Arcane Breach selected): "i dont see where it says what an ability does." + (screenshots: Spellblade
  Lattice page 1) "and for the tree, upgrades should work their way down the tree like we discussed, and have each ability show up in the
  tree where you would unlock it. ... (and the modifiers stay in the list on the right under the ability. because they DO NOT take normal
  ability points to get. they auto unlock as the ability levels up.)" Popups: "when do an ability's 2 modifier SLOTS open?" -> "Both open
  with the ability (Recommended)"; "AP already spent on modifier nodes in the tree - what happens to it?" -> "Refund it (Recommended)".
  (docs/answered/classes.md 2026-10-16; this replaces the 2026-10-15 "each modifier costs 1 AP in the tree" part of
  research/Ability-Tree-Redesign-Spec.md.)
    (1) MODIFIERS UNLOCK BY ABILITY LEVEL AGAIN, class trees or not: Abil.modOk = ability level >= its mods.unlock step (2 / 4 / 6 / 8 / 10
      by default; fix round: with abil.levels OFF every modifier is open). SkyyTrees 0.3.18 has no modifier nodes any more (tree:fn:modOwned answers null). The 2 modifier slots still come with the
      ability (owning its ability node with class trees on - unchanged since 0.1.26); rebirth slots 3 + 4 unchanged. The level-up line names
      the new modifier again ("New modifier: Radius+ - equip it in /tree class."). Every "buy it in your class tree (node A1.Power)" text is
      now "unlocks at <Ability> Lv N". class:fn:abilMods (modRows) answers the unlock level of every modifier (field 2) and, for a locked one,
      "unlocks at <Ability> Lv N" (field 9) + what it will do at Lv 1 (field 10, as before). tree:reads:SkyyClasses lists the ability nodes
      (Class.<Class>.A1 .. A4a / A4b) + the path nodes - no modifier nodes. The abil.treeGate / mods.unlock help says so.
    (2) WHAT EVERY ABILITY DOES (NEW class:fn:abilDoes: String ability id -> String[4] { name, what it does, the walking cost line, how it
      grows with its level } or null): one plain sentence per ability with its LIVE numbers (the Server Setup rows: AbilCfg / AbilNum
      fields - damage as "x one hit" of the weapon held, area / range in blocks, durations in s), the walking shape's Mana + Stamina +
      cooldown (AbilPage.costLine, the same line the Lattice shows), and the level gain ("Levels by use: +2 % damage a level ..."; the
      ability's own level steps - stun / root / Breach per level - are in its sentence). The table DOES below is written from the CODE
      (the cast functions of 0.1.29); its wording follows research/classes/<Class>.md. The build checks every field it names exists and
      that the default text fits SkyyTrees 0.3.18's boxes (the node detail: 5 lines of 13 px in 424 px with the growth; the Lattice tail: 4).
    (3) THE ONE-TIME SLOT CHECK (abiltree3; PROJECT-RULES 4 + PROFILES-CONTRACT: per profile file): the ACTIVE profile of an online player
      (not loading - profile:busy absent), once per server run per pkey, from the 2 s ClassTick: an equipped modifier (e.<Id> slots 1-2,
      e2.<Id> slots 3-4) whose ability level is below its mods.unlock step goes back to the list - FIRST a verified History copy of the
      untouched abilities/<pkey>.properties in history/abiltree3/ (AbilSave.histCopyIn, the 0.1.26 machinery with its folder as an
      argument), then ONE write (fix round: AbilStore.setIf - only onto the very lines it was worked out from; a loadout click in between
      = worked out again in 2 s) (the slot lines + the run-once marker abil.tree3=done), one line in abiltree3-changes.log (the Undo), one
      INFO line and ONE chat line to the player naming each modifier and the level it comes back at. Modifiers the level allows stay
      slotted. Nothing to drop = the run-once marker alone (fix round 2: History copy first + one log line; ability levels off or no
      file yet = nothing written, looked at again). A failed History copy = nothing changes (tried again
      in 2 s). Modifier use-levels (m.<Id>.<Mod>) and rebirth picks are never touched.
    No command, permission or Server Setup row added; no existing bridge key or argument changed (SkyyWardrobe's loadout fns, SkyyMenu's
    panel fields, SkyyHud's class:fn:abil are unchanged). ROLLBACK to 0.1.29: no crash - 0.1.29 reads the same files (abil.tree3 is an
    unknown key it keeps); with SkyyTrees 0.3.18 it would find no modifier nodes, so every modifier stays locked until SkyyTrees is rolled
    back too (0.3.17 + 0.1.29 together, with the History copies of both mods put back = the state before this round).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.29.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.30.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.29"' in s and s.startswith('"""SkyyClasses 0.1.29 - build script') and "abilDoes" not in s, "not the generated 0.1.29 script"
REG0 = s.count("registerCommand(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.30 (2026-10-16)"):].rstrip() + "\n"

# ================================================================================================ docstring + version
rep('''"""SkyyClasses 0.1.29 - build script (javassist via jpype). GENERATED by tools/classes_0_1_29_patch.py from the generated 0.1.28 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_28_patch.py -> 0.1.28) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.30 - build script (javassist via jpype). GENERATED by tools/classes_0_1_30_patch.py from the generated 0.1.29 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_29_patch.py -> 0.1.29) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''' + NOTE)
rep('VERSION = "0.1.29"', 'VERSION = "0.1.30"')

# ================================================================================================ (1) the help texts of the two rows
rep('''   "Class trees on: buy abilities and modifiers as nodes in /tree class. Off: class level only.")''',
    '''   "Class trees on: buy abilities in /tree class (modifiers: by ability level). Off: class level only.")''')
rep('''   "No class trees: ability level for each 1st-5th modifier. With trees, modifier nodes unlock them.")''',
    '''   "Ability level for each 1st-5th modifier (no Ability Points; ability levels off = all open).")''')

# ================================================================================================ (1) tree:reads - the ability nodes only
rep('''        out.append(LINE_ID[_a[3]])
        out += ["%s.%s" % (LINE_ID[_a[3]], _m) for _m in AB_MODS[_a[0]]]
    return out''', '''        out.append(LINE_ID[_a[3]])   # 0.1.30: no modifier nodes (modifiers unlock by ability level; SkyyTrees 0.3.18)
    return out''')
rep('''assert "Class.Mage.A1.Power" in TREE_READS and "Class.Mage.A4b.Pierce" in TREE_READS and "Class.Assassin.A4b" not in TREE_READS and "M1A" not in TREE_READS
''', '''assert "Class.Mage.A1" in TREE_READS and "Class.Mage.A4b" in TREE_READS and "Class.Assassin.A4b" not in TREE_READS and "M1A" not in TREE_READS
assert "Class.Mage.A1.Power" not in TREE_READS and ".Power" not in TREE_READS, "0.1.30: no modifier nodes"
# 0.1.30 (Skyy 2026-10-16 "i dont see where it says what an ability does."): WHAT EVERY ABILITY DOES - the walking shape, written from the
# cast code of 0.1.29 (wording: research/classes/<Class>.md). {FIELD} = the LIVE Server Setup number (AbilCfg / AbilNum), {FIELD*k} = it x k.
# "x one hit" = one hit of the weapon held (SkyyArmory's number; abil.hitFallback for weapons it does not know)
DOES = {
    "Meteor": "A meteor falls where you look (up to {M_RANGE} blocks) {M_DELAY} s later and hits every enemy within {M_RADIUS} blocks for {M_POWER}x one staff hit.",
    "ManaBarrier": "A {B_RADIUS}-block dome where you look (up to {B_RANGE} blocks) for {B_TIME} s: inside it every {B_RATIO} damage to you costs 1 Mana instead of Health (at most {B_MAX} % of your max Health). You need {B_KEEP} Mana left after the cost.",
    "FrostNova": "Freezes every enemy within {F_RADIUS} blocks for {F_FREEZE} s and hits them for {F_POWER}x one staff hit. A hit after {F_BREAK} s shatters the ice for {F_BREAK_P}x more; then they are slowed {F_CHILL} s.",
    "Starfall": "{T_STARS} stars fall over {T_TIME} s within {T_RADIUS} blocks of where you look (up to {T_RANGE} blocks); each star hits every enemy within {T_STAR_R} blocks for {T_POWER}x one staff hit.",
    "ArcaneBeam": "Channel a beam {R_RANGE} blocks along your look for {R_TIME} s: every enemy on it takes {R_RATE}x one staff hit a second, ramping up to {R_RAMP}x by the end.",
    "SacredHeal": "Heals you and every player within {S_RADIUS} blocks for {S_HEAL} % of their max Health (you {S_SELF} % more), then {S_HOT} % of that again over {S_HOT_TIME} s. Players outside your party get a smaller share.",
    "ShieldBubble": "A {U_RADIUS}-block bubble where you look (up to {U_RANGE} blocks) for {U_TIME} s: hits on you and your party inside hit the bubble first (it soaks {U_HP} % of your max Health). When it drops to 75, 50 and 25 % and when it breaks, everyone inside heals {U_PULSE} % of max Health.",
    "GuardianSpirit": "Passive, always on: a killing blow on you or a party member within {GS_RADIUS} blocks leaves them at {GS_HP} % Health instead, for {GS_MANA} Mana + {GS_STAM} Stamina. Per player the wait between saves starts at {GS_CD} s and doubles (reset after {GS_RESET} s without damage).",
    "Sanctuary": "A {Y_RADIUS}-block holy zone under you for {Y_TIME} s: you and your party inside heal {Y_HEAL} % of max Health a second and take {Y_CUT} % less damage.",
    "MartyrsGrace": "Heals the most hurt player within {G_RANGE} blocks for {G_FIRST} % of max Health, then jumps to the next most hurt, {G_DROP} % less each time, up to {G_TARGETS} players (your party first).",
    "FlowingForm": "An aura for up to {FF_TIME} s ({FF_DM} Mana + {FF_DS} Stamina a second): every hit you land is a combo stack (max {FF_MAX}, {FF_DECAY} s each, +{FF_MOVE} % move speed). Enemies within {FF_RADIUS} blocks are Awed: they take more damage the higher your combo. Awe lasts {FF_ALINGER} s after they leave.",
    "PalmStrike": "Strikes the enemy you look at (within {PS_REACH} blocks) for {PS_POWER}x one hit, stuns it {PS_STUN} s and pushes it {PS_PUSH} blocks back. Each level takes {PS_CD_LVL} s off the cooldown (down to {PS_CD_FLOOR} s).",
    "CycloneKick": "Kicks every enemy within {CK_RADIUS} blocks for {CK_POWER}x one hit and pushes them {CK_PUSH} blocks away.",
    "HundredFists": "Flowing Form's aura (drains {HF_DM} Mana + {HF_DS} Stamina a second) where every {HF_EVERY}th combo hit sends a shockwave: {HF_POWER}x one hit to every Awed enemy in the aura (at most once per {HF_GAP} s).",
    "StillWater": "A stance for {SW_TIME} s: projectiles from within {SW_FRONT} degrees of your look are deflected, and melee hits you block strike back for {SW_POWER}x one hit.",
    "CloakFirstStrike": "Cloaked for {CL_TIME} s - mobs within {CL_LOSE} blocks lose you (attacking ends it). Your next hit within {CL_WINDOW} s is a First Strike: +{CL_STRIKE} % damage.",
    "Toxin": "Throws a vial where you look (up to {TX_RANGE} blocks): a {TX_RADIUS}-block poison cloud for {TX_TIME} s. Enemies inside take {TX_POISON}x one hit a second and deal {TX_WEAKEN} % less.",
    "GodKiller": "Your next hit on a boss or mini-boss within {GK_WINDOW} s deals {GK_MULT}x damage ({GK_BACK}x from behind).",
    "VanishingAct": "You vanish in a {VA_RADIUS}-block smoke that stays {VA_TIME} s: cloaked {VA_CLOAK} s, enemies inside lose you after {VA_LOSE} s and move {VA_SLOW} % slower. Your next hit is a First Strike (+{CL_STRIKE} %).",
    "RallyingGuard": "You and your party within {RG_PARTY} blocks (other players within {RG_PLAYERS}) take {RG_CUT} % less damage for {RG_TIME} s (at most {RG_CUTCAP} %). Enemies within {RG_TAUNT} blocks turn on you for {RG_TAUNTTIME} s.",
    "ShieldShockwave": "A {SS_ANGLE*2}-degree cone {SS_RANGE} blocks in front of you: {SS_POWER}x one hit to every enemy in it and a {SS_STUN} s stun (+{SS_STUNLEVEL} s a level, at most +0.6 s).",
    "IronChain": "Hooks the enemy you look at (up to {IC_RANGE} blocks) and drags it to you: {IC_POWER}x one hit and a {IC_STUN} s stun (+0.02 s a level, at most +0.4 s).",
    "Challenge": "The enemy you look at (up to {CH_RANGE} blocks) must fight you for {CH_TIME} s: you take {CH_CUT} % less from it and {CH_REFLECT} % of its hits reflect back.",
    "GuardiansOath": "Links you to a party member (the one you look at within {GO_RANGE} blocks, else the most hurt) for {GO_TIME} s: {GO_SHARE} % of the damage they take comes to you, and you take {GO_CUT} % less.",
    "Enrage": "You and allies near you (party within {EN_PARTY} blocks, others within {EN_PLAYERS}) deal more damage: +{EN_START} % growing to +{EN_PEAK} % over {EN_GROW} s, held {EN_HOLD} s. You get {EN_SELFMULT}x that (at most +{EN_SELFCAP} %).",
    "Whirlwind": "Spin for {WW_TIME} s: every {WW_EVERY} s each enemy within {WW_RADIUS} blocks takes {WW_POWER}x one hit, and you heal {WW_HEAL} % of the damage.",
    "Earthsplitter": "A shockwave line {ES_LENGTH} blocks ahead ({ES_WIDTH} wide): {ES_POWER}x one hit and enemies knocked {ES_UP} blocks up. Stronger at low Health: + your missing Health % (at most +{ES_MISSINGCAP} %).",
    "BloodFrenzy": "A toggle (press again to stop): every swing costs {BF_HITMANA} Mana + {BF_HITSTAM} Stamina (+{BF_DRAINMANA} / {BF_DRAINSTAM} a second) and each hit adds a stack (max {BF_MAX}, each lasts {BF_DECAY} s): +{BF_DMG} % damage and +{BF_MOVE} % speed per stack. Allies near you get {BF_ALLY} % of it.",
    "WarlordsBanner": "Plants a war banner at your feet for {WB_TIME} s ({WB_RADIUS} blocks): +{WB_SELF} % damage and defence for you, +{WB_PARTY} % your party, +{WB_PLAYERS} % others. Kills inside keep it up longer (+{WB_KILLADD} s, mini-boss +{WB_MINIADD}, boss +{WB_BOSSADD}; at most {WB_CAP} s). It falls if you leave it.",
    "PinningShot": "An arrow along your look ({PN_RANGE} blocks, pierces {PN_PIERCE}): {PN_POWER}x one hit, roots {PN_ROOT} s (+0.02 s a level) and Marks them +{PN_MARK} % damage taken for {PN_MARKTIME} s (+1 % a level, at most {PN_MARKCAP} %).",
    "RapidFire": "Fires {RF_ARROWS} arrows over {RF_TIME} s along your look (up to {RF_RANGE} blocks), each {RF_POWER}x one hit.",
    "ExplosiveArrow": "Your next arrow hit within {EA_WINDOW} s explodes: {EA_MULT}x the hit to every enemy within {EA_RADIUS} blocks.",
    "ArrowRain": "Arrows rain on a {AR_RADIUS}-block circle where you look (up to {AR_RANGE} blocks) for {AR_TIME} s: {AR_POWER}x one hit in all, enemies {AR_SLOW} % slower; after {AR_ROOTAFTER} s inside they are rooted {AR_ROOT} s and Marked +{AR_MARK} %.",
    "HuntersNet": "A {HN_RADIUS}-block net where you look (up to {HN_RANGE} blocks): every enemy inside is rooted {HN_TIME} s, takes {HN_POWER}x one hit and is Marked +{HN_MARK} % for {HN_MARKTIME} s.",
    "ArcaneBreach": "A {AB_ANGLE*2}-degree arc {AB_RANGE} blocks in front: {AB_POWER}x one hit and Breach - they take {AB_BREACH} % more from everyone for {AB_TIME} s (+{AB_PERSTACK} % per Momentum, +{AB_PERLEVEL} % a level, at most {AB_CAP} %). +{AB_GAIN} Momentum.",
    "ElementalImbue": "For {EI_TIME} s your hits deal +{EI_PCT} % extra damage as your element and put its status on the enemy (Burn, Chill, Shock ... - pick the element under its row).",
    "Sunder": "A heavy strike on the enemy you look at (within {SU_RANGE} blocks): {SU_POWER}x one hit, and it deals {SU_WEAKEN} % less for {SU_TIME} s. +{SU_GAIN} Momentum.",
    "RiftCleave": "A {RC_ANGLE*2}-degree arc {RC_RANGE} blocks ahead ({RC_POWER}x one hit) tears a rift {RC_LENGTH} blocks long for {RC_TIME} s: enemies inside are Breached +{RC_BREACH} % and {RC_SLOW} % slower. +{RC_GAIN} Momentum.",
    "ShatteringArc": "Spends your Momentum (keeps {SA_KEEP}) on one {SA_ANGLE*2}-degree arc {SA_RANGE} blocks ahead: {SA_POWER}x one hit +{SA_PERSTACK}x per Momentum spent, and Breach +{SA_BREACH} % (+{SA_BREACHPERSTACK} % per Momentum, at most {SA_BREACHCAP} %) for {SA_TIME} s (+{SA_TIMEPERSTACK} s per Momentum).",
}
''')

# the Java of the table + its checks (after ABIL_LINES: every row list exists there)
rep('''] + ["%s=%s" % (_r[0], abil_text(_r[3])) for _r in ABIL_ROWS]
''', '''] + ["%s=%s" % (_r[0], abil_text(_r[3])) for _r in ABIL_ROWS]
# 0.1.30: the DOES table -> one Java expression per ability (live fields) + the same text with the defaults (the fit checks)
DOES_FIELDS = dict((_r[1], ("AbilCfg", _r[2], _r[3])) for _r in ABIL_ROWS)
DOES_FIELDS.update(dict((_r[1], ("AbilNum", _r[2], _r[3])) for _r in NUM_ROWS))
assert sorted(DOES) == sorted(a[0] for a in ABILS), "0.1.30: one DOES text per ability"
DOES_JAVA, DOES_DEF = {}, {}


def _does_num(x):
    r = round(float(x) * 100.0) / 100.0   # AbilDoes.n: 2 decimals (0.65 Mana a second, 0.25x one hit)
    return str(int(r)) if r == int(r) else ("%.2f" % r).rstrip("0")


for _aid, _tx in DOES.items():
    _parts = re.split(r"(\\{[A-Z0-9_]+(?:\\*[0-9.]+)?\\})", _tx)
    _js, _ds = [], []
    for _p in _parts:
        if not _p:
            continue
        _m = re.fullmatch(r"\\{([A-Z0-9_]+)(?:\\*([0-9.]+))?\\}", _p)
        if not _m:
            assert '"' not in _p and "\\\\" not in _p and "{" not in _p and "}" not in _p and all(32 <= ord(_c) < 127 for _c in _p), (_aid, _p)
            _js.append('"' + _p + '"')
            _ds.append(_p)
            continue
        _f, _k = _m.group(1), _m.group(2)
        assert _f in DOES_FIELDS, "0.1.30: DOES %s names an unknown field %s" % (_aid, _f)
        _h, _t, _dv = DOES_FIELDS[_f]
        assert _t in ("int", "dec"), (_aid, _f, _t)
        _js.append("@PKG@.AbilDoes.n((double) @PKG@.%s.%s%s)" % (_h, _f, (" * " + repr(float(_k))) if _k else ""))
        _ds.append(_does_num(float(_dv) * (float(_k) if _k else 1.0)))
    DOES_JAVA[_aid] = " + ".join(_js)
    DOES_DEF[_aid] = "".join(_ds)
# the default texts fit SkyyTrees 0.3.18's boxes (summary 13 px in its 424 px detail well): the node detail's "How it works" = what it
# does + the level line in 5 lines; the Lattice tail ("What it does") = the sentence in 4 lines
DOES_GROW_DEF = "Levels by use: +%s %% NOUN a level (half after Lv %d, a quarter after Lv %d; top Lv %d)." % (
    _does_num(_ROWV["abil.perLevel"]), _ROWV["abil.softLevel"], _ROWV["abil.halfLevel"], _ROWV["abil.maxLevel"])
for _aid, _tx in DOES_DEF.items():
    _g = DOES_GROW_DEF.replace("NOUN", AB_NOUN[_aid])
    assert SUI.text_lines(_tx + " " + _g, 424, 13) <= 5, "0.1.30: %s does not fit the node detail: %s" % (_aid, _tx)
    assert SUI.text_lines(_tx, 424, 13) <= 4, "0.1.30: %s does not fit the Lattice tail: %s" % (_aid, _tx)
print("0.1.30 DOES: %d abilities, longest %d characters (%s)" % (len(DOES_DEF), max(len(v) for v in DOES_DEF.values()), max(DOES_DEF, key=lambda a: len(DOES_DEF[a]))))
''')

# ================================================================================================ (1) modifiers: the ability level unlocks them
rep('''public static boolean modOk(String csv, int ai, int k, int lvl) {
  if (ai < 0 || k < 0 || k >= @PKG@.AbilModDefs.count(ai)) return false;
  if (@PKG@.AbilCfg.TREE_GATE && csv != null) return @PKG@.AbilModDefs.csvHas(csv, lineId(ai) + "." + @PKG@.AbilModDefs.MID[@PKG@.AbilModDefs.at(ai, k)]);   // 0.1.26: its MODIFIER node
  return lvl >= @PKG@.AbilModDefs.unlockAt(k);   // no class tree: the ability level unlocks it (mods.unlock, as before)
}''', '''public static boolean modOk(String csv, int ai, int k, int lvl) {
  if (ai < 0 || k < 0 || k >= @PKG@.AbilModDefs.count(ai)) return false;
  if (!@PKG@.AbilCfg.LEVELS) return true;   // fix round: ability levels off = no level to reach - every modifier is open
  return lvl >= @PKG@.AbilModDefs.unlockAt(k);   // 0.1.30 (Skyy 2026-10-16 "they auto unlock as the ability levels up"): the ability level (mods.unlock), class trees or not
}''')
rep('''      String nu = (@PKG@.AbilCfg.TREE_GATE && ucsv != null) ? "" : newMods(ai, l0, l1);   // 0.1.26: with a class tree the tree unlocks modifiers
      say(pr, @PKG@.AbilDefs.NAMES[ai] + " reached Lv " + l1 + "! " + gainText(ai, l1) + "." + (nu.length() > 0 ? " New modifier: " + nu + " - equip it in /tree class." : ""));   // 0.1.26: nu stays empty with a class tree''',
    '''      String nu = newMods(ai, l0, l1);   // 0.1.30: the ability level unlocks modifiers again (class trees too)
      say(pr, @PKG@.AbilDefs.NAMES[ai] + " reached Lv " + l1 + "! " + gainText(ai, l1) + "." + (nu.length() > 0 ? " New modifier: " + nu + " - equip it in /tree class." : ""));''')
rep('''    int at = tg ? 0 : @PKG@.AbilModDefs.unlockAt(j);   // 0.1.26: 0 = the tree unlocks it''',
    '''    int at = @PKG@.AbilModDefs.unlockAt(j);   // 0.1.30: the ability level unlocks it (tg kept for the head line only)''')
rep('''    String now = un ? modText(ai, mi, ml, cnt > 0 ? cnt : 1) : (tg ? "buy it in your class tree (node " + lineId(ai) + "." + @PKG@.AbilModDefs.MID[mi] + ")" : "unlocks at " + @PKG@.AbilDefs.NAMES[ai] + " Lv " + at);''',
    '''    String now = un ? modText(ai, mi, ml, cnt > 0 ? cnt : 1) : "unlocks at " + @PKG@.AbilDefs.NAMES[ai] + " Lv " + at;   // 0.1.30''')
rep('''    if (!modOk(csv, ai, pos, l)) {   // 0.1.26: the tree's modifier node (no tree: the ability level)
      if (@PKG@.AbilCfg.TREE_GATE && csv != null) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " is not unlocked - buy it in your class tree (node " + lineId(ai) + "." + @PKG@.AbilModDefs.MID[mi] + ").";
      return''', '''    if (!modOk(csv, ai, pos, l)) {   // 0.1.30: the ability level
      return''')
rep('''    return "-That modifier is still locked - " + (@PKG@.AbilCfg.TREE_GATE && csvR != null ? "buy it in your class tree (node " + lineId(ai) + "." + @PKG@.AbilModDefs.MID[mi] + ")." : "it unlocks at " + @PKG@.AbilDefs.NAMES[ai] + " Lv " + at + ".");''',
    '''    return "-That modifier is still locked - it unlocks at " + @PKG@.AbilDefs.NAMES[ai] + " Lv " + at + ".";   // 0.1.30''')
rep('''  if (!modOk(csv, ai, pos, l)) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " is not unlocked - buy it in your class tree (node " + lineId(ai) + "." + @PKG@.AbilModDefs.MID[mi] + ").";''',
    '''  if (!modOk(csv, ai, pos, l)) return "-" + @PKG@.AbilModDefs.MNAME[mi] + " unlocks at " + nm + " Lv " + @PKG@.AbilModDefs.unlockAt(pos) + " (Lv " + l + " now) - use " + nm + " to level it.";   // 0.1.30''')

# ================================================================================================ (2) + (3) AbilDoes + AbilMig3 (before ClassTick, which calls AbilMig3.tick)
rep('''# ================= ClassTick (0.1.3): profile epoch check every 2 s -> republish class:<uuid> (contract rule 3). No SkyyProfiles = no-op =================
''', '''# ================= 0.1.30 AbilDoes: what every ability does (class:fn:abilDoes; the DOES table, live numbers) =================
abdoes = pool.makeClass(PKG + ".AbilDoes")
M(abdoes, r"""
public static String n(double x) {
  if (x != x || Double.isInfinite(x)) return "0";
  long c = Math.round(x * 100.0);
  if (c % 100L == 0L) return String.valueOf(c / 100L);
  String s = String.valueOf((double) c / 100.0);
  return s;
}""")
_dj = ["public static String does(int ai) {", "  if (ai < 0 || ai >= @PKG@.AbilDefs.IDS.length) return \\"\\";", "  @PKG@.AbilNum.sync();",
       "  String id = @PKG@.AbilDefs.IDS[ai];"]
for _aid in [a[0] for a in ABILS]:
    _dj.append("  if (id.equals(%s)) return %s;" % (jstr(_aid), DOES_JAVA[_aid]))
_dj += ["  return \\"\\";", "}"]
M(abdoes, "\\n".join(_dj))
M(abdoes, r"""
public static String grow(int ai) {
  if (ai < 0 || ai >= @PKG@.AbilDefs.IDS.length) return "";
  if (!@PKG@.AbilCfg.LEVELS) return "Ability levels are off on this server.";
  return "Levels by use: +" + @PKG@.AbilMath.fmt(@PKG@.AbilCfg.PER_LEVEL) + " % " + @PKG@.AbilDefs.NOUN[ai] + " a level (half after Lv " + @PKG@.AbilCfg.SOFT_LVL
    + ", a quarter after Lv " + @PKG@.AbilCfg.HALF_LVL + "; top Lv " + @PKG@.AbilCfg.MAX_LVL + ").";
}""")
M(abdoes, r"""
public static String[] info(String id) {
  int ai = @PKG@.AbilDefs.find(id);
  if (ai < 0) return null;
  String c = "";
  try { c = @PKG@.AbilPage.costLine(ai, 0, true, @PKG@.AbilDefs.CLS[ai]); } catch (Throwable t) { c = ""; }
  return new String[] { @PKG@.AbilDefs.NAMES[ai], does(ai), c, grow(ai) };
}""")
abdfn = pool.makeClass(PKG + ".AbilDoesFn")
abdfn.addInterface(pool.get("java.util.function.Function"))
C(abdfn, "public AbilDoesFn() { }")
M(abdfn, r"""
public Object apply(Object o) {
  try {
    Object x = o instanceof Object[] && ((Object[]) o).length > 0 ? ((Object[]) o)[0] : o;
    if (x == null) return null;
    return @PKG@.AbilDoes.info(String.valueOf(x).trim());
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class:fn:abilDoes failed: " + t); return null; }
}""")
# ================= 0.1.30 AbilMig3: THE ONE-TIME SLOT CHECK (modifiers unlock by ability level again; PROJECT-RULES 4, PROFILES-CONTRACT) =================
abmig3 = pool.makeClass(PKG + ".AbilMig3")
F(abmig3, "public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();")   # pkey -> Boolean (looked at this run)
F(abmig3, "public static volatile long DROPPED = 0L;")
F(abmig3, "public static volatile long FILES = 0L;")
F(abmig3, "public static volatile String LAST = \\"\\";")
M(abmig3, r"""
public static String joinS(String a, String b) {
  String v = (a == null ? "" : a) + "," + (b == null ? "" : b);
  return ",".equals(v) ? null : v;
}""")
M(abmig3, r"""
public static void logLine(String k, String text) {
  try {
    java.nio.file.Path dir = @PKG@.AbilStore.DIR;
    if (dir == null) return;
    java.nio.file.Path f = dir.getParent().resolve("abiltree3-changes.log");
    String line = java.time.LocalDateTime.now().toString() + "\\t" + k + "\\tslots\\t" + text.replace('\\t', ' ').replace('\\n', ' ')
      + "\\tUndo: stop the server, copy history/abiltree3/" + k + ".properties over abilities/" + k + ".properties (the marker abil.tree3 goes with it)\\n";
    synchronized (@PKG@.AbilSave.HLOCK) {
      java.nio.file.Files.write(f, line.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
    }
  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("the slot check could not write abiltree3-changes.log: " + t); }
}""")
# one profile file: "" = nothing to do (or done before), null = not now (unreadable / History failed - tried again), else the chat text
M(abmig3, r"""
public static String check(String k) {
  if (k == null || @PKG@.AbilStore.DIR == null) return null;
  java.util.Properties p = @PKG@.AbilStore.load(k);
  if (@PKG@.AbilStore.FAILAT.get(k) != null) return null;
  if ("done".equals(String.valueOf(p.getProperty("abil.tree3")).trim())) return "";
  java.util.ArrayList ks = new java.util.ArrayList();
  java.util.ArrayList vs = new java.util.ArrayList();
  StringBuilder said = new StringBuilder();
  int n = 0;
  for (int ai = 0; ai < @PKG@.AbilDefs.IDS.length; ai++) {
    String id = @PKG@.AbilDefs.IDS[ai];
    String[] e = @PKG@.Abil.eqOf4(p, id);
    int l = @PKG@.Abil.alvlk(k, @PKG@.Abil.numOf(p, "u." + id));
    boolean ch = false;
    for (int j = 0; j < 4; j++) {
      if (e[j] == null || e[j].length() == 0) continue;
      int mi = @PKG@.AbilModDefs.find(e[j]);
      int pos = @PKG@.AbilModDefs.pos(ai, mi);
      if (mi < 0 || pos < 0) continue;
      int at = @PKG@.AbilModDefs.unlockAt(pos);
      if (@PKG@.Abil.modOk(null, ai, pos, l)) continue;   // fix round: the same rule as equipping (ability levels off = every modifier stays)
      e[j] = "";
      ch = true;
      n++;
      said.append(said.length() > 0 ? ", " : "").append(@PKG@.AbilModDefs.MNAME[mi]).append(" on ").append(@PKG@.AbilDefs.NAMES[ai]).append(" (Lv ").append(at).append(")");
    }
    if (ch) {
      ks.add("e." + id); vs.add(joinS(e[0], e[1]));
      ks.add("e2." + id); vs.add(joinS(e[2], e[3]));
    }
  }
  if (n == 0) {   // fix round 2 (critic: no run-once marker): nothing to drop = the marker alone (History copy first, one log line), never again
    if (!@PKG@.AbilCfg.LEVELS || p.isEmpty()) return "";   // ability levels off (every modifier open: looked at again once they are on) / no file yet
    if (!@PKG@.AbilSave.histCopyIn(k, "abiltree3")) return null;
    if (!@PKG@.AbilStore.setIf(k, p, new String[] { "abil.tree3" }, new String[] { "done" })) return null;
    @PKG@.AbilStore.saveSoon(k);
    logLine(k, "nothing to move back (the run-once marker only)");
    return "";
  }
  if (!@PKG@.AbilSave.histCopyIn(k, "abiltree3")) return null;   // a verified History copy first, or nothing changes
  ks.add("abil.tree3");
  vs.add("done");
  String[] ka = new String[ks.size()];
  String[] va = new String[vs.size()];
  for (int i = 0; i < ka.length; i++) { ka[i] = (String) ks.get(i); va[i] = (String) vs.get(i); }
  if (!@PKG@.AbilStore.setIf(k, p, ka, va)) return null;   // fix round: only onto the very lines it was worked out from (a loadout click meanwhile = again in 2 s)
  @PKG@.AbilStore.saveSoon(k);
  DROPPED = DROPPED + (long) n;
  FILES = FILES + 1L;
  LAST = k + ": " + said.toString();
  logLine(k, n + " modifier(s) back to the list: " + said.toString());
  @PKG@.ClassCfg.info("ability slot check (0.1.30) for " + k + ": " + n + " modifier(s) back to the list - " + said.toString() + " [abil.tree3=done; the old file: history/abiltree3/" + k + ".properties; abiltree3-changes.log]");
  return "Modifiers now unlock by themselves as each ability levels up (no Ability Points). Back in your list until the ability reaches that level: " + said.toString() + ".";   // fix round: the AP line is SkyyTrees' own
}""")
M(abmig3, r"""
public static int consider(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  if (u == null) return -1;
  String k = @PKG@.ClassCfg.pkey(u);
  if (k == null || SEEN.containsKey(k)) return -1;
  if (@PKG@.Kit.busy(u)) return -1;
  String r = check(k);
  if (r == null) return -1;
  SEEN.put(k, Boolean.TRUE);
  if (r.length() == 0) return 0;
  @PKG@.Abil.send(pr, r, "#ffc800");
  return 1;
}""")
M(abmig3, r"""
public static void tick() {
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ pr = (@PR@) it.next();
    if (pr == null || !pr.isValid()) continue;
    try { consider(pr); } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("the ability slot check failed: " + t); }
  }
}""")
# ================= ClassTick (0.1.3): profile epoch check every 2 s -> republish class:<uuid> (contract rule 3). No SkyyProfiles = no-op =================
''')
rep('''  try { @PKG@.Kit.topTick(); } catch (Throwable t4) { if (FAILS < 5) { FAILS++; @PKG@.ClassCfg.warn("class kit top-up tick failed: " + t4); } }   // 0.1.29
''', '''  try { @PKG@.Kit.topTick(); } catch (Throwable t4) { if (FAILS < 5) { FAILS++; @PKG@.ClassCfg.warn("class kit top-up tick failed: " + t4); } }   // 0.1.29
  try { @PKG@.AbilMig3.tick(); } catch (Throwable t5) { if (FAILS < 5) { FAILS++; @PKG@.ClassCfg.warn("ability slot check tick failed: " + t5); } }   // 0.1.30
''')
# the History copy with its folder as an argument (0.1.26's abiltree2 copy = histCopyIn(k, "abiltree2"), byte-for-byte the same steps)
rep('''public static boolean histCopy0(String k) {
  java.nio.file.Path DIR = @PKG@.AbilStore.DIR;
  if (DIR == null || k == null) return false;
  try {
    java.nio.file.LinkOption[] no = new java.nio.file.LinkOption[0];
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    java.nio.file.Path h = DIR.getParent().resolve("history").resolve("abiltree2").resolve(k + ".properties");''',
    '''public static boolean histCopy0(String k, String fold) {
  java.nio.file.Path DIR = @PKG@.AbilStore.DIR;
  if (DIR == null || k == null || fold == null) return false;
  try {
    java.nio.file.LinkOption[] no = new java.nio.file.LinkOption[0];
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    java.nio.file.Path h = DIR.getParent().resolve("history").resolve(fold).resolve(k + ".properties");   // 0.1.30: the folder is an argument''')
rep('''    if (hx && !java.nio.file.Files.isRegularFile(h, no)) { @PKG@.ClassCfg.warnLimited("the ability tree update cannot keep abilities/" + k + ".properties: history/abiltree2/" + k + ".properties is not a file (the update waits)"); return false; }''',
    '''    if (hx && !java.nio.file.Files.isRegularFile(h, no)) { @PKG@.ClassCfg.warnLimited("the ability tree update cannot keep abilities/" + k + ".properties: history/" + fold + "/" + k + ".properties is not a file (the update waits)"); return false; }''')
rep('''        @PKG@.ClassCfg.info("the ability tree update: an older History copy (from an earlier server run) is kept as history/abiltree2/" + String.valueOf(kept.getFileName()) + " - a fresh copy is made");''',
    '''        @PKG@.ClassCfg.info("the ability tree update: an older History copy (from an earlier server run) is kept as history/" + fold + "/" + String.valueOf(kept.getFileName()) + " - a fresh copy is made");''')
rep('''  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("the ability tree update could not copy abilities/" + k + ".properties into history/abiltree2 (the update waits): " + t); return false; }''',
    '''  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("the ability tree update could not copy abilities/" + k + ".properties into history/" + fold + " (the update waits): " + t); return false; }''')
rep('''public static boolean histCopy(String k) {
  boolean r = false;
  synchronized (HLOCK) { r = histCopy0(k); }
  return r;
}''', '''public static boolean histCopy(String k) {
  boolean r = false;
  synchronized (HLOCK) { r = histCopy0(k, "abiltree2"); }
  return r;
}""")
M(absave, r"""
public static boolean histCopyIn(String k, String fold) {
  boolean r = false;
  synchronized (HLOCK) { r = histCopy0(k, fold); }   // 0.1.30: history/abiltree3 for the slot check
  return r;
}''')

rep('''  DATA.put(k, p);
  return true;
}""")
M(abst, r"""
public static boolean granted(String k) {''', '''  DATA.put(k, p);
  return true;
}""")
M(abst, r"""
public static synchronized boolean setIf(String k, java.util.Properties expect, String[] keys, String[] vals) {
  if (k == null || expect == null || DATA.get(k) != expect) return false;   // fix round: changed since it was read (copy-on-write: a new object)
  return set(k, keys, vals);
}""")
M(abst, r"""
public static boolean granted(String k) {''')

# ================================================================================================ the bridge
rep('''  b.put("class:fn:migInfo", new @PKG@.AbilMigFn());         // 0.1.26: SkyyTrees 0.3.13's one-time ability tree update (the alt + the usable modifiers)
''', '''  b.put("class:fn:migInfo", new @PKG@.AbilMigFn());         // 0.1.26: SkyyTrees 0.3.13's one-time ability tree update (the alt + the usable modifiers)
  b.put("class:fn:abilDoes", new @PKG@.AbilDoesFn());       // 0.1.30: what an ability does - { name, does, cost, growth } (SkyyTrees 0.3.18's texts)
''')
rep('''  try { @PKG@.ClassCfg.bridge().remove("class:fn:migInfo"); } catch (Throwable t) { }       // 0.1.26
''', '''  try { @PKG@.ClassCfg.bridge().remove("class:fn:migInfo"); } catch (Throwable t) { }       // 0.1.26
  try { @PKG@.ClassCfg.bridge().remove("class:fn:abilDoes"); } catch (Throwable t) { }      // 0.1.30
''')
rep('''          abmi,                          # 0.1.26: + class:fn:migInfo
''', '''          abmi,                          # 0.1.26: + class:fn:migInfo
          abdoes, abdfn, abmig3,         # 0.1.30: + class:fn:abilDoes, the one-time slot check
''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert s.count("csvHas(csv, lineId(ai) + \".\"") == 0, "0.1.30: no modifier node is read any more"
assert s.count("buy it in your class tree (node \" + lineId(ai) + \".\"") == 0, "0.1.30: no modifier node text left"
assert s.count("@PKG@.AbilMig3.tick()") == 1 and s.count('b.put("class:fn:abilDoes"') == 1 and s.count('remove("class:fn:abilDoes")') == 1
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.1.29 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", dst, "(%d lines; 0.1.29 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
