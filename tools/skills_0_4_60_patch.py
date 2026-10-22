"""Derive SkyySkills/build_skyyskills_0.4.60.py from the GENERATED SkyySkills 0.4.59 (build_skyyskills_0.4.59.py = the tools/deploy_set.py SET
pin, made by tools/skills_0_4_59_patch.py). Every anchor is asserted once; at the end every change is undone on a copy and compared with
0.4.59 (tools/soundpass_gen.Patch). Line endings kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_60_patch.py   then   python SkyySkills/build_skyyskills_0.4.60.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.60.py
Deploys + rolls back TOGETHER with SkyyPets 0.4.9 + SkyyTrees 0.4.7 (Balance P8c, the Beastmastery skill).
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

BM_OLD_CATCH = "Mining,Foraging,Farming,Fishing,Alchemy,Smithing,Cooking,Acrobatics"   # 0.4.57 - 0.4.59 catchup.skills
BM_NEW_CATCH = BM_OLD_CATCH + ",Beastmastery"
BM_SKIP = ("skyygear_hp", "skyypet_health", "skyypet_mana")   # P5 cross-check (docs/log 2026-10-22): Health % / Mana % layers of other mods

NOTE = '''0.4.60 (2026-10-22) = BALANCE PASS P8c, the SkyySkills part (research/Balance-P8-Rebirth-Spec.md 4.4 + 5; FULL round with SkyyPets 0.4.9
  + SkyyTrees 0.4.7 - pin and roll back TOGETHER; new saved skill slot). Skyy (2026-10-21): "keep going down the list. dont stop until the
  entire list is done" + "just go with the recommended on all of them. i need to go to bed." (spec Q7 [yes]: "Beastmastery skill: levels
  from the XP your pets gain (1 Beastmastery XP per pet XP), resets on rebirth like the other skills, and its points open the Beastmastery
  tree"); docs/answered/skills.md:164 Beastmastery = a skill that "levels up from leveling pets".
  1. THE BEASTMASTERY SKILL = storage slot 20 (APPENDED after Battlemagic 19; saved key Beastmastery + Beastmastery.paid, written with every
     save from now on; a profile file without them loads 0 XP, level 0, nothing owed). It levels on the P3 general table (levels=, own list
     levels.skill.Beastmastery allowed), has the run cap (levels.runCap + 10 a rebirth, levels.capMax), RESETS ON REBIRTH like every slot but
     Exploration (x.Beastmastery in the participant's facts; a rebirth staged by 0.4.59 has no x.Beastmastery line -> left as it is), level-up
     lines + level coins, /skills top beastmastery, a /skills row after Exploration (13 rows, the list scrolls) with its Stats + Tree buttons
     (Tree while SkyyTrees' tree:names lists Beastmastery -> /tree beastmastery), and its Stats page (how-to, "1 tree point a level", the XP
     factor, catch-up / past-life lines).
  2. ITS XP = only skill:fn:addxp {UUID, "Beastmastery", n, "pets", key} from SkyyPets 0.4.9 (the pet XP the player's pets really gained,
     AFTER pet echo, so Beastmastery Echo speeds the skill) x beast.xpFactor (new Server Setup row Skills -> Levels "Beastmastery XP per pet
     XP", dec 0-10, default 1 - applied to the "pets" source only) x P3Xp.mult (xp.skillMult.Beastmastery, CATCH-UP - Beastmastery is in the
     catchup.skills default now - and the PAST-LIFE boost on replayed levels). NOT the server xp multiplier and NOT the skill:bonus sources
     (Void Insight / keep / Beastmastery Echo / tree XP): the pet XP it comes from already carries all of them (the SkyyPets 0.4.6 fix-round
     rule - never count Insight + keep twice); an admin who lists Beastmastery in bridge.bonus.addxpSkills turns the bonus on. Always grantable
     (like Fishing). No "+N Beastmastery XP" chat line per grant (pet XP comes in many small grants); level-up lines show. XP SkyySkills awards
     to Beastmastery is never reported to pets:fn:onxp (no pet XP loop; SkyyPets 0.4.9 ignores it too). Rebirth facts gain arm.beastmastery
     (facts only; SkyyRebirth reads its own arms - counting Beastmastery for Void Particles is a SkyyRebirth change, not in this round).
  3. ONE-TIME UPDATE BmMigP8c (PROJECT-RULES 4; PlMigP8's reviewed machinery, copied): ONCE on an existing xp.properties, setup() right after
     PlMigP8, BEFORE SkillCfg.load. catchup.skills whose LAST entry is a one-line entry holding exactly the 0.4.59 default -> + ",Beastmastery"
     (value text only); any other value kept (one INFO line); no line = nothing written (the new code default lists it). Then ONE block in the
     file's own line ending: the comment + beast.xpFactor=1 (if absent) + the run-once marker "Balance P8c Beastmastery (SkyySkills 0.4.60)".
     config-history copy first (verified), one config-changes.log row per change (Undo), a Properties check (only the planned keys differ),
     atomicWrite. A fresh file carries the marker. SAVED PLAYER DATA: not rewritten - Beastmastery starts at 0 XP for every existing profile.
  4. P5 CROSS-CHECK FIX (docs/log 2026-10-22): RbStat.skip (and so ClassStat.skip) also skips skyygear_hp, skyypet_health and skyypet_mana -
     gear / pet Health % and pet Mana % are percent layers, never part of the class / rebirth % base (the class Health % is taken on the flat
     max only).
  SAVED DATA: player files gain Beastmastery=<xp> / Beastmastery.paid=<level> on their next save. NEVER ROLL BACK below 0.4.60 once a
  Beastmastery line was saved (0.4.59's snap() drops the unknown key on its next save - the Beastmastery XP is lost; nothing else).
  ROLLBACK otherwise only TOGETHER with SkyyPets 0.4.8 + SkyyTrees 0.4.6; Undo the BmMigP8c rows in Server Setup -> Changes first.
'''

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.59.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.60.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.59"') and P.has("PlMigP8") and not P.has("BmMigP8c"), "not the generated SkyySkills 0.4.59 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

P.rep('''"""SkyySkills 0.4.59 - build script (derived from the generated 0.4.58 by tools/skills_0_4_59_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.60 - build script (derived from the generated 0.4.59 by tools/skills_0_4_60_patch.py - edit the patch, not this file;
''' + NOTE + '''0.4.59 was derived from the generated 0.4.58 by tools/skills_0_4_59_patch.py;
''')
P.rep('VERSION = "0.4.59"', 'VERSION = "0.4.60"')

# ================================================================================================================ 1. slot 20 Beastmastery
P.rep('''_SL = _SL + [("Combat." + CLASS_ROWS[7][0], CLASS_ROWS[7][1], CLASS_ROWS[7][2], CLASS_ROWS[7][3])]''',
      '''_SL = _SL + [("Combat." + CLASS_ROWS[7][0], CLASS_ROWS[7][1], CLASS_ROWS[7][2], CLASS_ROWS[7][3])]
# 0.4.60 (Balance P8c, research/Balance-P8-Rebirth-Spec.md 4.4): Beastmastery = storage slot 20 (APPENDED; saved key = its name)
BEAST60_ROWS = [("Beastmastery", "Beastmastery", "Ingredient_Hide_Medium", "#e0b070")]
for _c in BEAST60_ROWS: must(_c[2])
_SL = _SL + [tuple(_c) for _c in BEAST60_ROWS]''')
P.rep('''assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 20   # 0.4.37: + Fishing, Ranching, Orchard; 0.4.43: + Battlemagic''',
      '''assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 21   # 0.4.37: + Fishing, Ranching, Orchard; 0.4.43: + Battlemagic; 0.4.60: + Beastmastery''')
P.rep('''assert SLOT_NAMES[19:] == ["Combat.Spellblade"] and SLOT_LABELS[19:] == ["Battlemagic"]   # 0.4.43''',
      '''assert SLOT_NAMES[19:20] == ["Combat.Spellblade"] and SLOT_LABELS[19:20] == ["Battlemagic"]   # 0.4.43
assert SLOT_NAMES[20:] == ["Beastmastery"] == SLOT_LABELS[20:]   # 0.4.60''')
P.rep('''SKILL_ROW_SLOTS = [0, 1, 2, 16, 17, 18, 10, 11, 12, 4, 13, 3]   # 0.4.38: + Fishing, Ranching, Orchard after Farming (12 rows)''',
      '''SKILL_ROW_SLOTS = [0, 1, 2, 16, 17, 18, 10, 11, 12, 4, 13, 20, 3]   # 0.4.38: + Fishing, Ranching, Orchard after Farming (12 rows); 0.4.60: + Beastmastery after Exploration''')
P.rep('''for _nm37, _ix37 in (("FISHING", 16), ("RANCHING", 17), ("ORCHARD", 18)):
    assert SLOT_NAMES[_ix37] == _nm37.capitalize()
    defs.addField(CtField.make("public static final int %s = %d;" % (_nm37, _ix37), defs))''',
      '''for _nm37, _ix37 in (("FISHING", 16), ("RANCHING", 17), ("ORCHARD", 18)):
    assert SLOT_NAMES[_ix37] == _nm37.capitalize()
    defs.addField(CtField.make("public static final int %s = %d;" % (_nm37, _ix37), defs))
assert SLOT_NAMES[20] == "Beastmastery"
defs.addField(CtField.make("public static final int BEASTMASTERY = 20;", defs))   # 0.4.60 Balance P8c''')
P.rep('''UI_PAGE_COLORS = _B5C + CLASS_ROWS + EXTRA_ROWS + GATHER37_ROWS   # 0.4.37''', '''UI_PAGE_COLORS = _B5C + CLASS_ROWS + EXTRA_ROWS + GATHER37_ROWS + BEAST60_ROWS   # 0.4.60: + Beastmastery; 0.4.37''')
P.rep('''assert sorted(_B5C + [_x[3] for _x in CLASS_ROWS + EXTRA_ROWS + GATHER37_ROWS]) == sorted(SLOT_COLORS), "UI_PAGE_COLORS != SkillDefs.COLORS"''',
      '''assert sorted(_B5C + [_x[3] for _x in CLASS_ROWS + EXTRA_ROWS + GATHER37_ROWS + BEAST60_ROWS]) == sorted(SLOT_COLORS), "UI_PAGE_COLORS != SkillDefs.COLORS"''')

# the /skills page: 13 rows in the scrolling list (the pre-0.4.47 window budget numbers only bound the list's content now)
P.rep('''assert (SK_H, STATS_H, OV_H) == (973, 848, 689) and SK_LIST_H == 808 and SK_TOP_LIST_H == 781, (SK_H, STATS_H, OV_H, SK_LIST_H, SK_TOP_LIST_H)   # 0.4.38: 12 rows
assert SK_H <= SUI.MAX_PAGE_H, "the /skills page must fit a 1080 px screen (%d > %d)" % (SK_H, SUI.MAX_PAGE_H)''',
      '''assert (STATS_H, OV_H) == (848, 689) and SK_LIST_H == 808 + SK_ROW_H + SUI.ROW_GAP, (SK_H, STATS_H, OV_H, SK_LIST_H, SK_TOP_LIST_H)   # 0.4.38: 12 rows; 0.4.60: 13 rows
# 0.4.60: SK_H / SK_BODY_H are the pre-0.4.47 window budget (no page uses them since the kit 1.7 hub page: 1600 x 980, the list scrolls);
# SK_LIST_H stays the bound of the scroll list's content (SkyySkList) below''')
P.rep('''assert SUI.grow_pick(len(SK_ROW_SLOTS), SK_LIST_AVAIL, SK_ROW_HS) == 0, "0.4.47: the 12 skill rows keep their 62 / 82 px and scroll"''',
      '''assert SUI.grow_pick(len(SK_ROW_SLOTS), SK_LIST_AVAIL, SK_ROW_HS) == 0, "0.4.47: the 12 skill rows keep their 62 / 82 px and scroll (0.4.60: 13)"''')

# ================================================================================================================ 2. the XP path
# always grantable (SkyyPets 0.4.9)
P.rep('''  int[] g37 = new int[] {{ {PKG}.SkillDefs.FISHING, {PKG}.SkillDefs.RANCHING, {PKG}.SkillDefs.ORCHARD }};   // 0.4.37: always grantable (SkyyFishing catches; shards later)''',
      '''  int[] g37 = new int[] {{ {PKG}.SkillDefs.FISHING, {PKG}.SkillDefs.RANCHING, {PKG}.SkillDefs.ORCHARD, {PKG}.SkillDefs.BEASTMASTERY }};   // 0.4.37: always grantable (SkyyFishing catches; shards later); 0.4.60: + Beastmastery (SkyyPets 0.4.9)''')
# the factor on the "pets" source, before the multipliers
P.rep('''  if (base > {PKG}.BridgeCfg.PER_CALL) {{ warnLimited(u, "refused " + base + " XP from " + source + " (over bridge.maxXpPerCall " + {PKG}.BridgeCfg.PER_CALL + ")"); return -2L; }}''',
      '''  if (base > {PKG}.BridgeCfg.PER_CALL) {{ warnLimited(u, "refused " + base + " XP from " + source + " (over bridge.maxXpPerCall " + {PKG}.BridgeCfg.PER_CALL + ")"); return -2L; }}
  if (slot == {PKG}.SkillDefs.BEASTMASTERY && "pets".equals(source)) {{   // 0.4.60 Balance P8c: beast.xpFactor Beastmastery XP per pet XP
    base = {PKG}.P3Xp.beastBase(base);
    if (base <= 0L) return 0L;
  }}''')
# Beastmastery: no server multiplier / class factor (the pet XP carries them), P3Xp.mult (catch-up, past-life, skillMult), the bonus only if listed
P.rep('''  boolean canBoost = {PKG}.SkillDefs.boostable(slot);
  long amt = canBoost ? {PKG}.SkillCfg.scaled(base) : base;''', '''  boolean canBoost = {PKG}.SkillDefs.boostable(slot);
  if (slot == {PKG}.SkillDefs.BEASTMASTERY) {{   // 0.4.60 Balance P8c: the pet XP it comes from already carries the multiplier + every booster
    long ba = {PKG}.P3Xp.apply(u, slot, base, false);
    if (grant && {PKG}.SkillBonus.grantBonus(slot)) ba = {PKG}.SkillBonus.boost(u, slot, ba);
    return ba;
  }}
  long amt = canBoost ? {PKG}.SkillCfg.scaled(base) : base;''')
# no chat line per grant; no pet XP loop
P.rep('''    {PKG}.SkillXp.gain3(pr, this.slot, this.amt, this.slot != {PKG}.SkillDefs.EXPLORATION, false);''',
      '''    {PKG}.SkillXp.gain3(pr, this.slot, this.amt, this.slot != {PKG}.SkillDefs.EXPLORATION && this.slot != {PKG}.SkillDefs.BEASTMASTERY, false);   // 0.4.60: no "+N Beastmastery XP" line per pet grant''')
P.rep('''  if (u == null || amount <= 0L || skill < 0 || skill >= {PKG}.SkillDefs.N) return;''',
      '''  if (u == null || amount <= 0L || skill < 0 || skill >= {PKG}.SkillDefs.N) return;
  if (skill == {PKG}.SkillDefs.BEASTMASTERY) return;   // 0.4.60 Balance P8c: Beastmastery XP comes FROM pet XP - never fed back to pets''')
# P3Xp: catch-up default, the factor, beastBase; the rebirth bonus of Beastmastery only when an admin lists it
P.rep('''P3_CATCH = "%s"''' % BM_OLD_CATCH, '''BM_OLD_CATCH = "%s"   # 0.4.60: the 0.4.57 - 0.4.59 catchup.skills default (BmMigP8c rewrites exactly this)
P3_CATCH = BM_OLD_CATCH + ",Beastmastery"   # 0.4.60 Balance P8c (spec 4.4: Beastmastery is in catchup.skills)''' % BM_OLD_CATCH)
P.rep('''             "public static volatile double XP_MULT_MAX = 0.0;",   # 0.4.59 rebirth.xpMultMax (0 = off)''',
      '''             "public static volatile double XP_MULT_MAX = 0.0;",   # 0.4.59 rebirth.xpMultMax (0 = off)
             "public static volatile double BEAST_F = 1.0;",   # 0.4.60 beast.xpFactor (Beastmastery XP per pet XP)''')
P.rep('''  XP_MULT_MAX = clamp(@PKG@.SkillCfg.dbl(p, "rebirth.xpMultMax", 0.0), 0.0, 100.0, 0.0);   // 0.4.59 Balance P8: the fastest-rebirth ceiling (0 = off)''',
      '''  XP_MULT_MAX = clamp(@PKG@.SkillCfg.dbl(p, "rebirth.xpMultMax", 0.0), 0.0, 100.0, 0.0);   // 0.4.59 Balance P8: the fastest-rebirth ceiling (0 = off)
  BEAST_F = clamp(@PKG@.SkillCfg.dbl(p, "beast.xpFactor", 1.0), 0.0, 10.0, 1.0);   // 0.4.60 Balance P8c: Beastmastery XP per pet XP''')
P.rep('''p3x.addMethod(CtNewMethod.make(J14(r"""
public static double rbSrc(java.util.UUID u, int s) {
  if (u == null || s < 0 || s >= @PKG@.SkillDefs.N || !@PKG@.SkillDefs.boostable(s)) return 0.0;''', '''p3x.addMethod(CtNewMethod.make(J14(r"""
public static double rbSrc(java.util.UUID u, int s) {
  if (u == null || s < 0 || s >= @PKG@.SkillDefs.N || !@PKG@.SkillDefs.boostable(s)) return 0.0;
  if (s == @PKG@.SkillDefs.BEASTMASTERY && !@PKG@.SkillBonus.grantBonus(s)) return 0.0;   // 0.4.60: the pet XP carries the rebirth XP already''')
P.rep('''public static double bonusP8(java.util.UUID u, int slot) {
  if (slot < 0 || slot >= @PKG@.SkillDefs.N) return 0.0;
  if (!@PKG@.SkillDefs.boostable(slot)) return 0.0;''', '''public static double bonusP8(java.util.UUID u, int slot) {
  if (slot < 0 || slot >= @PKG@.SkillDefs.N) return 0.0;
  if (!@PKG@.SkillDefs.boostable(slot)) return 0.0;
  if (slot == @PKG@.SkillDefs.BEASTMASTERY && !@PKG@.SkillBonus.grantBonus(slot)) return 0.0;   // 0.4.60 Balance P8c: no booster twice (see BridgeXp.paidY)''')
P.rep('''p3x.addMethod(CtNewMethod.make(J14(r"""
public static long apply(java.util.UUID u, int s, long amt, boolean own) {
  if (amt <= 0L) return amt;
  return times(amt, mult(u, s, own));
}"""), p3x))''', '''p3x.addMethod(CtNewMethod.make(J14(r"""
public static long apply(java.util.UUID u, int s, long amt, boolean own) {
  if (amt <= 0L) return amt;
  return times(amt, mult(u, s, own));
}"""), p3x))
# 0.4.60 Balance P8c: SkyyPets' pet XP -> Beastmastery XP (x beast.xpFactor; the fraction paid by chance, as times() pays it)
p3x.addMethod(CtNewMethod.make(J14(r"""
public static long beastBase(long base) {
  if (base <= 0L) return 0L;
  double f = BEAST_F;
  if (!(f > 0.0)) return 0L;
  return times(base, f);
}"""), p3x))''')
# rebirth facts + the tree button
P.rep('''           'public static final String[] XARMS = new String[] { "ranching", "orchard", "acrobatics" };'):   # 0.4.57: + arm.acrobatics (SkyyRebirth FOR SKYYSKILLS 3)''',
      '''           'public static final String[] XARMS = new String[] { "ranching", "orchard", "acrobatics", "beastmastery" };'):   # 0.4.57: + arm.acrobatics (SkyyRebirth FOR SKYYSKILLS 3); 0.4.60: + arm.beastmastery (facts only)''')
P.rep('''  if (slot == {PKG}.SkillDefs.FISHING) return "fishing";
  if ({PKG}.SkillDefs.isClass(slot)) return "class";''', '''  if (slot == {PKG}.SkillDefs.FISHING) return "fishing";
  if (slot == {PKG}.SkillDefs.BEASTMASTERY) return "beastmastery";   // 0.4.60: SkyyTrees 0.4.0+ lists Beastmastery in tree:names
  if ({PKG}.SkillDefs.isClass(slot)) return "class";''')

# ================================================================================================================ 4. RbStat / ClassStat skip
P.rep('''  return s.equals(KH) || s.equals(KM) || s.equals(KS) || s.startsWith("skyyacc_") || s.equals("skyyskill_classhp");   // 0.4.58: + the class Health layer''',
      '''  return s.equals(KH) || s.equals(KM) || s.equals(KS) || s.startsWith("skyyacc_") || s.equals("skyyskill_classhp")   // 0.4.58: + the class Health layer
      || %s;   // 0.4.60 (P5 cross-check): SkyyGear's Health %%, SkyyPets' Health / Mana %% layers''' % " || ".join('s.equals("%s")' % k for k in BM_SKIP))

# ================================================================================================================ the Stats page + texts
P.rep('''  int row = {PKG}.SkillDefs.perkRow(s);
  if (row < 0) return out;
  int b = next ? lv + 1 : lv;''', '''  if (s == {PKG}.SkillDefs.BEASTMASTERY) {{   // 0.4.60 Balance P8c: no perks - its levels are the Beastmastery tree's points
    if (next) {{
      out.add("+1 Beastmastery tree point at level " + (lv + 1));
      if ({PKG}.SkillCfg.COINS_PER_LEVEL > 0L) out.add("+" + {PKG}.SkillDefs.fmt({PKG}.SkillStore.rbCoins({PKG}.SkillCfg.COINS_PER_LEVEL * (long) (lv + 1), {PKG}.SkillStore.rbN({PKG}.SkillStore.pkey(u)))) + " coins when you reach level " + (lv + 1));
      return out;
    }}
    out.add(lv + " Beastmastery tree point" + (lv == 1 ? "" : "s") + " - 1 a level (/tree beasts)");
    out.add("Beastmastery XP per pet XP: x" + {PKG}.DivCfg.num({PKG}.P3Xp.BEAST_F));
    return out;
  }}
  int row = {PKG}.SkillDefs.perkRow(s);
  if (row < 0) return out;
  int b = next ? lv + 1 : lv;''')
P.rep('''  if (s == {PKG}.SkillDefs.ORCHARD) return "Earn XP by harvesting fruit - apples and berry bushes - when they are ripe (break them or press F)";''',
      '''  if (s == {PKG}.SkillDefs.ORCHARD) return "Earn XP by harvesting fruit - apples and berry bushes - when they are ripe (break them or press F)";
  if (s == {PKG}.SkillDefs.BEASTMASTERY) return "Earn XP whenever your pets gain XP (SkyyPets) - each pet XP is Beastmastery XP. A pet at its max level gains none. Every level is a Beastmastery tree point";   // 0.4.60''')
P.rep('''use Mining, Foraging, Farming, Fishing, Ranching, Orchard, Acrobatics, Alchemy, Smithing, Cooking or Exploration (class skills''',
      '''use Mining, Foraging, Farming, Fishing, Ranching, Orchard, Acrobatics, Alchemy, Smithing, Cooking, Exploration or Beastmastery (class skills''')
P.rep('''Use mining, foraging, farming, fishing, ranching, orchard, alchemy, smithing, cooking, acrobatics, exploration, combat (your class skill)''',
      '''Use mining, foraging, farming, fishing, ranching, orchard, alchemy, smithing, cooking, acrobatics, exploration, beastmastery, combat (your class skill)''')
for _hd in ('''  super("top", "Top 10 players of a skill: /skills top mining");''',
            '''  super("stats", "Open the Stats page of a skill: /skills stats mining (or /skills stats overall)");''',
            '''  super("xp", "(admin) Give yourself skill XP for testing: /skills xp alchemy 3100000 (also 500k, 3.1m)");'''):
    P.rep(_hd + '''
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | fishing | ranching | orchard | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill)''',
          _hd + '''
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | fishing | ranching | orchard | alchemy | smithing | cooking | acrobatics | exploration | beastmastery | combat (your class skill)''')

# ================================================================================================================ the Server Setup row
P.rep('''     "Most past-life x Void XP (0 = off; tree XP never cut). 9.3 = runs stop shrinking at rebirth 10.", "reload"),''',
      '''     "Most past-life x Void XP (0 = off; tree XP never cut). 9.3 = runs stop shrinking at rebirth 10.", "reload"),
    # 0.4.60 (Balance P8c 5.2: "Beastmastery XP per pet XP (beast.xpFactor) dec 0-10, 1.0")
    ("beast.xpFactor", "Beastmastery XP per pet XP", "levels", "dec", "1", "0", "10", "", "x", "live",
     "Beastmastery XP for each pet XP your pets gain (SkyyPets). 0 = Beastmastery earns nothing.", "reload"),''')
P.rep('''assert len(CFG_ROWS) == 285 + len(P4_ROWS_POWER) + len(P4_ROWS_MANA) + len(P4_ROWS_MOVE) + 1, ("0.4.59: + rebirth.xpMultMax; 0.4.58:''',
      '''assert len(CFG_ROWS) == 285 + len(P4_ROWS_POWER) + len(P4_ROWS_MANA) + len(P4_ROWS_MOVE) + 2, ("0.4.60: + beast.xpFactor; 0.4.59: + rebirth.xpMultMax; 0.4.58:''')

# ================================================================================================================ 3. the fresh default file + BmMigP8c
BMDATA = r'''# ================= 0.4.60 BALANCE P8c - the BmMigP8c plan and the fresh default file (tools/skills_0_4_60_patch.py) =================
BM_KEYS = [("catchup.skills", BM_OLD_CATCH, P3_CATCH, "catchup.skills")]          # (key, 0.4.59 default, 0.4.60 default, change-log row)
BM_ADD = [("beast.xpFactor", "1", "beast.xpFactor")]
BM_MARK_ID = "Balance P8c Beastmastery (SkyySkills 0.4.60)"
BM_MARK = "# %s: the Beastmastery skill - its XP per pet XP and its catch-up" % BM_MARK_ID
BM_HEAD = ["", "# ---------- Balance P8c: the Beastmastery skill (SkyySkills 0.4.60) ----------",
           "# Comments must stay on their own lines. Beastmastery levels from the XP your pets gain (SkyyPets); catchup.skills (above) lists it.",
           "# beast.xpFactor = Beastmastery XP for each pet XP (1 = one for one; 0 = Beastmastery earns nothing)."]
for _t in BM_HEAD + [BM_MARK]:
    assert all(32 <= ord(_c) < 127 for _c in _t) and '"' not in _t and "\\" not in _t and (not _t or _t.startswith("# ")), _t
assert "=" not in BM_MARK and not any(_cre.match(r"#\s*[A-Za-z][A-Za-z0-9._-]*\s*[=:]\s*\S+\s*$", _ln) for _ln in BM_HEAD)
BM_BLOCK = "\n".join(BM_HEAD + ["%s=%s" % (_k, _v) for _k, _v, _r in BM_ADD] + [BM_MARK]) + "\n"
DEFAULTS_059 = DEFAULTS   # 0.4.60: the 0.4.59 default file (P3_CATCH already = the 0.4.60 list there: P3's own block carries it)
assert ("\n" + DEFAULTS_059).count("\ncatchup.skills=" + P3_CATCH + "\n") == 1 and ("\ncatchup.skills=" + BM_OLD_CATCH + "\n") not in DEFAULTS_059
DEFAULTS = DEFAULTS_059 + ("" if DEFAULTS_059.endswith("\n") else "\n") + BM_BLOCK
assert all(ord(ch) < 128 for ch in DEFAULTS) and len(DEFAULTS.encode("utf-8")) < 65000 and DEFAULTS.count(BM_MARK_ID) == 1, len(DEFAULTS)
print("0.4.60: P8c update plan %d key(s), %d line(s) appended; default file %d bytes" % (len(BM_KEYS), len(BM_ADD), len(DEFAULTS)))
'''
P.rep('''DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)''',
      BMDATA + '''DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\\n \\" \\\\ escapes)''')
P.rep('''assert DEFAULTS.count(P3_MARK_ID) == 1 and DEFAULTS.endswith(P8_BLOCK) and DEFAULTS.count(P8_MARK_ID) == 1 and _dp.get("rebirth.pastLifeXp") == P8_PAST and _dp.get("rebirth.xpMultMax") == "0"   # 0.4.59''',
      '''assert DEFAULTS_059.count(P3_MARK_ID) == 1 and DEFAULTS_059.endswith(P8_BLOCK) and DEFAULTS_059.count(P8_MARK_ID) == 1 and _dp.get("rebirth.pastLifeXp") == P8_PAST and _dp.get("rebirth.xpMultMax") == "0"   # 0.4.59 (0.4.60: the 0.4.59 file)
assert DEFAULTS.endswith(BM_BLOCK) and DEFAULTS.count(BM_MARK_ID) == 1 and _dp.get("catchup.skills") == P3_CATCH and _dp.get("beast.xpFactor") == "1"   # 0.4.60''')
P.rep('''plm8 = pool.makeClass(PKG + ".PlMigP8")        # 0.4.59: the one-time Balance P8 update (rebirth.pastLifeXp + rebirth.xpMultMax)''',
      '''plm8 = pool.makeClass(PKG + ".PlMigP8")        # 0.4.59: the one-time Balance P8 update (rebirth.pastLifeXp + rebirth.xpMultMax)
bm60 = pool.makeClass(PKG + ".BmMigP8c")        # 0.4.60: the one-time Balance P8c update (catchup.skills + beast.xpFactor)''')


def _plm(name):
    a = P.s.index('plm8.addMethod(CtNewMethod.make(J14(r"""\npublic static ' + name)
    b = P.s.index('"""), plm8))', a)
    return P.s[a + len('plm8.addMethod(CtNewMethod.make(J14(r"""'):b]


_IDX, _OLDH, _PLAN, _SAME, _RUN = (_plm("int idx("), _plm("boolean oldHit("), _plm("Object[] plan("), _plm("boolean sameAfter("),
                                   _plm("synchronized String run()"))
_PLAN = _PLAN.replace('''"the 0.4.59 default has no such line" : "the 0.4.59 (Balance P8) default is "''',
                      '''"the 0.4.60 default has no such line" : "the 0.4.60 (Balance P8c) default is "''')
assert "0.4.59" not in _PLAN and "P8)" not in _PLAN, _PLAN
for _a, _b in (("xp.properties NOT updated for 0.4.59 (Balance P8)", "xp.properties NOT updated for 0.4.60 (Balance P8c)"),
               ('"before the 0.4.59 Balance P8 update"', '"before the 0.4.60 Balance P8c update"'),
               ('"xp.properties updated for 0.4.59 (Balance P8: past-life XP list, fastest-rebirth ceiling row): "',
                '"xp.properties updated for 0.4.60 (Balance P8c: Beastmastery in catch-up, Beastmastery XP per pet XP row): "'),
               ('"could not update xp.properties for 0.4.59 (Balance P8; the file is used as it is): "',
                '"could not update xp.properties for 0.4.60 (Balance P8c; the file is used as it is): "')):
    assert _RUN.count(_a) >= 1, _a
    _RUN = _RUN.replace(_a, _b)
assert "0.4.59" not in _RUN and "P8)" not in _RUN and "Balance P8 " not in _RUN, _RUN
BMMIG = r'''# ---- BmMigP8c (0.4.60, PROJECT-RULES section 4; PlMigP8's reviewed machinery, copied): ONCE on an EXISTING xp.properties, setup() right after
# PlMigP8, BEFORE SkillCfg.load. catchup.skills whose LAST entry is a one-line entry holding exactly the 0.4.59 default (OLDS) -> NEWS (+
# Beastmastery); any other value kept (INFO); no line = nothing written. Then ONE block in the file's own line ending: HEAD + beast.xpFactor=1
# (if absent) + the marker. config-history copy first (verified), one config-changes.log row per change (Undo), Properties check, atomicWrite.
# A failure = WARN, file untouched, retried next start.
bm60.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(BM_MARK_ID), bm60))
bm60.addField(CtField.make("public static final String MARK = %s;" % json.dumps(BM_MARK), bm60))
bm60.addField(CtField.make("public static final String HEAD = %s;" % json.dumps("\n".join(BM_HEAD) + "\n"), bm60))
bm60.addField(CtField.make("public static final String[] KEYS = %s;" % jarr([_e[0] for _e in BM_KEYS]), bm60))
bm60.addField(CtField.make("public static final String[] OLDS = %s;" % jarr([_e[1] for _e in BM_KEYS]), bm60))
bm60.addField(CtField.make("public static final String[] NEWS = %s;" % jarr([_e[2] for _e in BM_KEYS]), bm60))
bm60.addField(CtField.make("public static final String[] ROWK = %s;" % jarr([_e[3] for _e in BM_KEYS]), bm60))
bm60.addField(CtField.make("public static final String[] ADDK = %s;" % jarr([_e[0] for _e in BM_ADD]), bm60))
bm60.addField(CtField.make("public static final String[] ADDV = %s;" % jarr([_e[1] for _e in BM_ADD]), bm60))
bm60.addField(CtField.make("public static final String[] ADDR = %s;" % jarr([_e[2] for _e in BM_ADD]), bm60))
bm60.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.60";', bm60))
bm60.addMethod(CtNewMethod.make(J14(r"""''' + _IDX + r'''"""), bm60))
bm60.addMethod(CtNewMethod.make(J14(r"""''' + _OLDH + r'''"""), bm60))
bm60.addMethod(CtNewMethod.make(J14(r"""''' + _PLAN + r'''"""), bm60))
bm60.addMethod(CtNewMethod.make(J14(r"""''' + _SAME + r'''"""), bm60))
bm60.addMethod(CtNewMethod.make(J14(r"""''' + _RUN + r'''"""), bm60))

'''
P.rep('''# ---- CurveP3Mig (0.4.57, spec 6.2, PROJECT-RULES section 4): ONCE, setup() right after Xp56Mig.run, BEFORE P3Mig (which only runs once this''',
      BMMIG + '''# ---- CurveP3Mig (0.4.57, spec 6.2, PROJECT-RULES section 4): ONCE, setup() right after Xp56Mig.run, BEFORE P3Mig (which only runs once this''')
P.rep('''  String rules = {PKG}.SkillCfg.load();
  {PKG}.LvFloor.start(base);''', '''  {PKG}.BmMigP8c.run();       // 0.4.60 Balance P8c: an untouched catchup.skills -> + Beastmastery + the Beastmastery XP row, once; History first
  String rules = {PKG}.SkillCfg.load();
  {PKG}.LvFloor.start(base);''')
P.rep("cst, p4m, plm8, lvf,", "cst, p4m, plm8, bm60, lvf,")

# ================================================================================================================ the ready line
P.rep('''+ "; /skills lists " + {PKG}.SkillDefs.ROW_SLOTS.length + " rows (Fishing, Ranching, Orchard included)"''',
      '''+ "; /skills lists " + {PKG}.SkillDefs.ROW_SLOTS.length + " rows (Fishing, Ranching, Orchard, Beastmastery included)" + "; Beastmastery from pet XP (skill:fn:addxp source pets, x" + {PKG}.DivCfg.num({PKG}.P3Xp.BEAST_F) + " per pet XP)"''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0
P.finish()
