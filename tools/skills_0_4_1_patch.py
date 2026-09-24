"""Derive SkyySkills/build_skyyskills_0.4.1.py from 0.4 (same style as skills_0_4_patch.py: rep(old, new) with asserted single anchors,
newline-agnostic; 0.4 stays untouched, the CRLF/LF line endings of 0.4 are preserved). Edit THIS file, not the generated script.
0.4.1 = research/Exploration-Build-Spec.md section 3 (SkyySkills part of the Exploration round; partners SkyyExploration 0.1 +
        SkyyTrees 0.2, each still loads alone):
 - 3.1 slot 13 Exploration (append-only), /skills row after Acrobatics, perk row 8, skill:<uuid> gains Exploration after Cooking.
 - 3.2 Exploration XP only through skill:fn:addxp, boosters bypassed IN CODE (SkillDefs.boostable): no xp multiplier, no tree bonus,
       forced out of the bonus lists, block rules naming it ignored; GRANT[Exploration] = exploration.enabled.
 - 3.3 +0.1 max Stamina per level (perk.exploration.staminaPerLevel) - every perk array (statics AND the PerkCfg.read() fallbacks)
       gets its 9th entry; the Exploration block of xp.properties is appended once (ExplCfg.ensureDefaults).
 - 3.4 Acro.boost adds the Acrobatics tree dodge (skill:bonus dodge.acrobatics, capped by acro.treeDodgeMax).
 - 3.5 UI: /skills 690 tall + "- explore" footer, Tree buttons through SkillBonus.treeAvailable (bridge tree:names of SkyyTrees 0.2),
       Stats page texts for Exploration and the Acrobatics "Skill tree:" line, skill args list exploration.
 Orchestrator-level call (the spec is silent): Exploration grants add no "+N Exploration XP" chat line of their own - SkyyExploration
 writes its own chest / zone / aggregated 30 s chunk lines (hidden by /explore quiet); level-up lines and coins still show.
Run:  python tools/skills_0_4_1_patch.py   then   python SkyySkills/build_skyyskills_0.4.1.py   (NO --deploy: coordinated deploy)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.1.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4"
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
rep('''"""SkyySkills 0.4 - build script (derived from 0.3.2 by tools/skills_0_4_patch.py - edit the patch, not this file;
0.3.2 was derived from 0.3.1 by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4 (research/Alchemy-Skill-Spec.md''', '''"""SkyySkills 0.4.1 - build script (derived from 0.4 by tools/skills_0_4_1_patch.py - edit the patch, not this file;
0.4 was derived from 0.3.2 by tools/skills_0_4_patch.py, 0.3.2 from 0.3.1 by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by
tools/skills_0_3_patch.py)
0.4.1 (research/Exploration-Build-Spec.md section 3 - the Exploration row; deploy with SkyyExploration 0.1 + SkyyTrees 0.2, each loads alone):
  SLOT 13 Exploration (N = 14, append-only: slots 0-12 unchanged; >= CLASS0 but not a class). /skills = 9 rows: Mining, Foraging,
  Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration, class skill (ROW_SLOTS); perk row 8 = exploration (PERK_SLOT; PerkCfg.KEYS
  has 9 entries and so does EVERY perk array - the HP / STA / MANA / DD / ONLY statics AND the dhp / dsta / dmana / ddd / donly fallbacks
  inside PerkCfg.read(), whose loop indexes them up to KEYS.length). skill:<uuid> = "...,Cooking:3,Exploration:12,<class skills>";
  skill:fn:level / skill:fn:xp answer "Exploration" through indexOf. Player files gain Exploration=<xp> / Exploration.paid=<level> (old
  files load 0). NEVER DOWNGRADE to 0.4 once Exploration XP exists: 0.4's snap() drops the unknown keys on its next save.
  XP: ONLY through skill:fn:addxp (skill "Exploration"; SkyyExploration sends Object[]{UUID, "Exploration", Long, "exploration", pkey}).
  NO BOOSTERS (Skyy Q3), enforced in code: SkillDefs.boostable(EXPLORATION) = false -> BridgeXp.offer pays the base XP (no xp multiplier)
  and never adds a skill-tree bonus, SkillBonus.xpBonus returns 0 for it; BridgeCfg.read sets GRANT[EXPLORATION] = exploration.enabled
  (grantable whatever an old 0.4 bridge.addxp.skills line says) and forces BONUS_XP / BONUS_ADDXP[EXPLORATION] = false (one WARN
  "Exploration never gets XP bonuses (Skyy) - ignored" when bridge.bonus.xpSkills / addxpSkills name it). A block. / prefix. / suffix.
  rule naming Exploration is ignored with a WARN. bridge.maxXpPerMinute still counts Exploration (a safety bound, not a booster). The
  admin /skills xp exploration <n> stays raw. Exploration grants post no "+N Exploration XP" line of their own (BridgeTask note = false
  for this slot): SkyyExploration writes its own chest / zone / aggregated chunk lines and /explore quiet hides them; level-up lines
  and the level coins show as for every skill.
  PERK: +0.1 max Stamina per level (perk.exploration.staminaPerLevel, summed into the skyyskill_stamina MAX modifier by the 1 s
  Perks.tick) + the generic coinsPerLevel x level. CONFIG: the Exploration block (exploration.enabled, perk.exploration.staminaPerLevel,
  acro.treeDodgeMax) is in a fresh xp.properties and appended ONCE to an existing file without exploration.enabled (ExplCfg.ensureDefaults,
  the AlchCfg pattern); /skills reload re-reads it; the code defaults are the same numbers.
  ACROBATICS TREE (SkyyTrees 0.2): Acro.boost pushes dodgeBonus(level) + Acro.treeDodge(u) = skill:bonus:<uuid> "dodge.acrobatics" summed
  over sources, clamped 0..acro.treeDodgeMax (0.25), only while acro.enabled and acro.dodgeBoost (a level-0 player with tree points
  still gets the tree part). Speed / jump / fall nodes need no Skills change: they arrive as the movement source "trees.acrobatics",
  which MoveSync and the stat:owner:fallDamage owner (SkyySkills) already sum.
  UI: /skills root Height 690 (8 x 58 + Acrobatics 72 + 4 px gaps), footer "- explore". Tree buttons (row "Tree", Stats "Skill tree")
  only when SkillBonus.treeAvailable(slot): SkyyTrees running (tree:fn:level) AND bridge tree:names (SkyyTrees 0.2, comma list of tree
  labels) lists the skill - or, without tree:names (SkyyTrees 0.1), Mining / Foraging / Farming / Cooking exactly as in 0.4;
  treeName(Acrobatics) = "acrobatics", treeName(Exploration) = "exploration". Stats page Exploration: how-to text (wrapped label), "+X max
  Stamina", the skill:stats:Exploration hook lines (SkyyExploration) or "Install SkyyExploration to earn Exploration XP", and "Exploration
  XP ignores the xp multiplier and every skill-tree or booster bonus"; Stats page Acrobatics: "Skill tree: +5% speed, +0.2 blocks jump,
  -5% fall damage, +10% dodge push" from move:<uuid>["trees.acrobatics"] + the tree dodge. /skills stats|top|xp help and the unknown-skill
  message list exploration (the 3+ letter prefix "exp" resolves).
  Known edge (0.4 bridge behaviour, unchanged): BridgeTask still drops a grant it accepted when the player is in creative (creativeXp=
  false) or the profile changed between offer and task; SkyyExploration never grants in creative with its defaults.
0.4 (research/Alchemy-Skill-Spec.md''')
rep('''Run:   python build_skyyskills_0.4.py            -> SkyySkills/SkyySkills-0.4.jar
       python build_skyyskills_0.4.py --deploy   -> also copies''', '''Run:   python build_skyyskills_0.4.1.py            -> SkyySkills/SkyySkills-0.4.1.jar
       python build_skyyskills_0.4.1.py --deploy   -> also copies''')
rep('VERSION = "0.4"', 'VERSION = "0.4.1"')

# ================================================================ xp.properties: the Exploration block (3.3)
after('''ALCH_LIT, SMITH_LIT, BRIDGE_LIT = json.dumps(ALCH_DEFAULTS), json.dumps(SMITH_DEFAULTS), json.dumps(BRIDGE_DEFAULTS)
''', r'''# 0.4.1: Exploration (research/Exploration-Build-Spec.md 3.3). Also appended once to an existing xp.properties that has no
# exploration.enabled key (ExplCfg.ensureDefaults); the code defaults (ExplCfg.ENABLED, PerkCfg STA[8], AcroCfg.TREE_DODGE_MAX) are the
# same numbers, so a file that lacks a key still gets them.
EXPL_STA_DEF, EXPL_DODGE_DEF = "0.1", "0.25"
EXPL_L = []
EXPL_L.append("# ---------- Exploration (SkyySkills 0.4.1) ----------")
EXPL_L.append("# Comments must stay on their own lines.")
EXPL_L.append("# Exploration XP only comes from other mods through skill:fn:addxp (SkyyExploration: loot chests, new chunks, zones).")
EXPL_L.append("# It never gets the xp multiplier or any skill-tree / booster bonus (Skyy). exploration.enabled=false refuses it.")
EXPL_L.append("exploration.enabled=true")
EXPL_L.append("perk.exploration.staminaPerLevel=" + EXPL_STA_DEF)
EXPL_L.append("# Acrobatics skill-tree dodge nodes (SkyyTrees 0.2, skill:bonus dodge.acrobatics) add at most this much dodge push.")
EXPL_L.append("acro.treeDodgeMax=" + EXPL_DODGE_DEF)
L.append("")
L.extend(EXPL_L)
EXPL_DEFAULTS = "\n".join(EXPL_L) + "\n"
assert all(ord(ch) < 128 for ch in EXPL_DEFAULTS)
EXPL_LIT = json.dumps(EXPL_DEFAULTS)
''')

# ================================================================ classes
after('''pfn  = pool.makeClass(PKG + ".SkillPlacedFn")
''', '''# 0.4.1
exc  = pool.makeClass(PKG + ".ExplCfg")
''')

# ================================================================ 3.1 slot 13 + rows
rep('''# 0.4: slots 10-12 (append-only; they are >= CLASS0 but NOT classes - class loops stop at CLASS_END = 10)
EXTRA_ROWS = [("Alchemy", "Alchemy", "Potion_Health", "#7fe0d0"), ("Smithing", "Smithing", "Ingredient_Bar_Iron", "#c0c8d0"),
              ("Cooking", "Cooking", "Food_Pie_Apple", "#ffb070")]''',
    '''# 0.4: slots 10-12, 0.4.1: slot 13 Exploration = slots 10-13 (append-only; they are >= CLASS0 but NOT classes - class loops stop at
# CLASS_END = 10)
EXTRA_ROWS = [("Alchemy", "Alchemy", "Potion_Health", "#7fe0d0"), ("Smithing", "Smithing", "Ingredient_Bar_Iron", "#c0c8d0"),
              ("Cooking", "Cooking", "Food_Pie_Apple", "#ffb070"), ("Exploration", "Exploration", "Tool_Map", "#e0a040")]''')
rep('''assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 13
assert SLOT_NAMES[10:] == ["Alchemy", "Smithing", "Cooking"] and SLOT_NAMES[5 + len(CLASS_ROWS) - 1] == "Combat.Mage"''',
    '''assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 14
assert SLOT_NAMES[10:] == ["Alchemy", "Smithing", "Cooking", "Exploration"] and SLOT_NAMES[5 + len(CLASS_ROWS) - 1] == "Combat.Mage"''')
after('''defs.addField(CtField.make("public static final int COOKING = 12;", defs))
''', '''defs.addField(CtField.make("public static final int EXPLORATION = 13;", defs))   # 0.4.1
''')
rep('''defs.addField(CtField.make("public static final int[] ROW_SLOTS = new int[] { 0, 1, 2, 10, 11, 12, 4, 3 };", defs))''',
    '''defs.addField(CtField.make("public static final int[] ROW_SLOTS = new int[] { 0, 1, 2, 10, 11, 12, 4, 13, 3 };", defs))   # 0.4.1: Exploration after Acrobatics''')
rep('''defs.addField(CtField.make("public static final int[] PERK_SLOT = new int[] { 0, 1, 2, 3, 4, 10, 11, 12 };", defs))''',
    '''defs.addField(CtField.make("public static final int[] PERK_SLOT = new int[] { 0, 1, 2, 3, 4, 10, 11, 12, 13 };", defs))''')
rep('''  if (s == COOKING) return 7;
  return -1;
}""", defs))
''', '''  if (s == COOKING) return 7;
  if (s == EXPLORATION) return 8;
  return -1;
}""", defs))
# 0.4.1 (Skyy Q3: no XP boosters for Exploration): false = the xp multiplier and every skill-tree / booster bonus are skipped for this
# slot, in code (BridgeXp.offer, SkillBonus.xpBonus), whatever xp.properties says
defs.addMethod(CtNewMethod.make("""
public static boolean boostable(int s) {
  return s != EXPLORATION;
}""", defs))
''')
rep('''  int[] order = new int[] {{ {PKG}.SkillDefs.MINING, {PKG}.SkillDefs.FORAGING, {PKG}.SkillDefs.FARMING, {PKG}.SkillDefs.ACROBATICS, {PKG}.SkillDefs.ALCHEMY, {PKG}.SkillDefs.SMITHING, {PKG}.SkillDefs.COOKING }};''',
    '''  int[] order = new int[] {{ {PKG}.SkillDefs.MINING, {PKG}.SkillDefs.FORAGING, {PKG}.SkillDefs.FARMING, {PKG}.SkillDefs.ACROBATICS, {PKG}.SkillDefs.ALCHEMY, {PKG}.SkillDefs.SMITHING, {PKG}.SkillDefs.COOKING, {PKG}.SkillDefs.EXPLORATION }};''')

# ================================================================ 3.2 block rules naming Exploration are ignored (with the reason)
after('''    return new long[] {{ (long) sk, x }};
  }} catch (Throwable t) {{ return null; }}
}}""", cfg))
''', r'''# 0.4.1: a block. / prefix. / suffix. rule naming Exploration ("Exploration:5") is ignored with a WARN - Exploration XP only comes from
# other mods through skill:fn:addxp (parseRule would call it a bad rule anyway; this names the reason and does not count it as bad)
cfg.addMethod(CtNewMethod.make(f"""
public static boolean explRule(String v) {{
  if (v == null) return false;
  String s = v.trim();
  int c = s.indexOf(':');
  if (c <= 0) return false;
  return {PKG}.SkillDefs.indexOf(s.substring(0, c)) == {PKG}.SkillDefs.EXPLORATION;
}}""", cfg))
''')
rep('''      long[] r = parseRule(v);
''', '''      if (explRule(v)) {{ warn("rule " + k + "=" + v + " ignored - Exploration XP only comes from other mods (skill:fn:addxp, SkyyExploration), never from blocks"); continue; }}
      long[] r = parseRule(v);
''')

# ================================================================ 3.3 the Exploration block: ExplCfg, load order, AcroCfg.treeDodgeMax
before('''# ================= BridgeCfg (0.4): bridge.* keys (skill:fn:addxp / skill:fn:craftxp) =================
''', r'''# ================= ExplCfg (0.4.1): the Exploration block of xp.properties (research/Exploration-Build-Spec.md 3.2 / 3.3) =================
# exploration.enabled=false refuses every Exploration grant (BridgeCfg.read sets GRANT[EXPLORATION] from it, so ExplCfg.read runs first).
# perk.exploration.staminaPerLevel is read by PerkCfg like every perk.* key, acro.treeDodgeMax by AcroCfg. Appended ONCE to an existing
# xp.properties that has no exploration.enabled key (the AlchCfg pattern; a restart finds the key and appends nothing).
exc.addField(CtField.make("public static final String DEFAULTS = " + EXPL_LIT + ";", exc))
exc.addField(CtField.make("public static volatile boolean ENABLED = true;", exc))
exc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ENABLED = {PKG}.SkillCfg.bool(p, "exploration.enabled", true);
}}""", exc))
exc.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  if (p.getProperty("exploration.enabled") != null) return;
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Exploration section (exploration.enabled, perk.exploration.staminaPerLevel, acro.treeDodgeMax - default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the Exploration section to xp.properties: " + t); }}
}}""", exc))

''')
after('''    {PKG}.BridgeCfg.ensureDefaults(p);
''', '''    {PKG}.ExplCfg.ensureDefaults(p);
''')
before('''    {PKG}.BridgeCfg.read(p);
''', '''    {PKG}.ExplCfg.read(p);
''')
rep('''", bridge skills " + {PKG}.BridgeCfg.GRANT_TEXT''',
    '''", exploration " + ({PKG}.ExplCfg.ENABLED ? "on (no boosters)" : "off") + ", bridge skills " + {PKG}.BridgeCfg.GRANT_TEXT''')
rep('''"double DODGE_PER_LVL = 0.004", "double DODGE_MAX = 0.5"):''',
    '''"double DODGE_PER_LVL = 0.004", "double DODGE_MAX = 0.5", "double TREE_DODGE_MAX = 0.25"):''')
after('''  DODGE_MAX = Math.min(2.0, nn({PKG}.SkillCfg.dbl(p, "acro.dodgeBoostMax", 0.5)));
''', '''  TREE_DODGE_MAX = Math.min(2.0, nn({PKG}.SkillCfg.dbl(p, "acro.treeDodgeMax", 0.25)));
''')

# ================================================================ 3.3 perk arrays: 9 entries everywhere (statics + read() fallbacks)
rep('''pcfg.addField(CtField.make('public static final String[] KEYS = new String[] { "mining", "foraging", "farming", "combat", "acrobatics", "alchemy", "smithing", "cooking" };', pcfg))''',
    '''pcfg.addField(CtField.make('public static final String[] KEYS = new String[] { "mining", "foraging", "farming", "combat", "acrobatics", "alchemy", "smithing", "cooking", "exploration" };', pcfg))''')
rep('''              "boolean WEAPON_ONLY = true", "double[] HP = new double[] { 0.0, 0.1, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0 }",
              "double[] STA = new double[] { 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }", "double[] MANA = new double[] { 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0 }",
              "double[] DD = new double[] { 0.005, 0.005, 0.005, 0.0, 0.0, 0.0, 0.0, 0.0 }", 'String[] ONLY = new String[] { "", "_Trunk", "", "", "", "", "", "" }'):''',
    '''              "boolean WEAPON_ONLY = true", "double[] HP = new double[] { 0.0, 0.1, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0 }",
              "double[] STA = new double[] { 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1 }", "double[] MANA = new double[] { 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0 }",
              "double[] DD = new double[] { 0.005, 0.005, 0.005, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }", 'String[] ONLY = new String[] { "", "_Trunk", "", "", "", "", "", "", "" }'):''')
rep('''  double[] dhp = new double[] {{ 0.0, 0.1, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0 }};
''', '''  double[] dhp = new double[] {{ 0.0, 0.1, 0.25, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0 }};
''')
rep('''  double[] dsta = new double[] {{ 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }};
''', '''  double[] dsta = new double[] {{ 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1 }};
''')
rep('''  double[] dmana = new double[] {{ 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0 }};
''', '''  double[] dmana = new double[] {{ 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0 }};
''')
rep('''  double[] ddd = new double[] {{ 0.005, 0.005, 0.005, 0.0, 0.0, 0.0, 0.0, 0.0 }};
''', '''  double[] ddd = new double[] {{ 0.005, 0.005, 0.005, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 }};
''')
rep('''  String[] donly = new String[] {{ "", "_Trunk", "", "", "", "", "", "" }};
''', '''  String[] donly = new String[] {{ "", "_Trunk", "", "", "", "", "", "", "" }};
''')

# ================================================================ 3.2 BridgeCfg: Exploration grant forced, never in the bonus lists
rep('''    if (hit < 0 || hit == {PKG}.SkillDefs.COMBAT) {{ {PKG}.SkillCfg.warn("bridge.addxp.skills: unknown or not grantable skill '" + t + "' - ignored"); continue; }}
    g[hit] = true;''', '''    if (hit < 0 || hit == {PKG}.SkillDefs.COMBAT) {{ {PKG}.SkillCfg.warn("bridge.addxp.skills: unknown or not grantable skill '" + t + "' - ignored"); continue; }}
    if (hit == {PKG}.SkillDefs.EXPLORATION) continue;
    g[hit] = true;''')
rep('''  GRANT = g;
  GRANT_TEXT = sb.toString();''', '''  g[{PKG}.SkillDefs.EXPLORATION] = {PKG}.ExplCfg.ENABLED;
  if ({PKG}.ExplCfg.ENABLED) {{
    if (sb.length() > 0) sb.append(',');
    sb.append({PKG}.SkillDefs.LABELS[{PKG}.SkillDefs.EXPLORATION]);
  }}
  GRANT = g;
  GRANT_TEXT = sb.toString();''')
before('''  boolean[] bx = new boolean[{PKG}.SkillDefs.N];
''', '''  boolean named = false;
''')
rep('''    if (bh < 0 || bh == {PKG}.SkillDefs.COMBAT) {{ {PKG}.SkillCfg.warn("bridge.bonus.xpSkills: unknown skill '" + bt + "' - ignored"); continue; }}
    bx[bh] = true;''', '''    if (bh < 0 || bh == {PKG}.SkillDefs.COMBAT) {{ {PKG}.SkillCfg.warn("bridge.bonus.xpSkills: unknown skill '" + bt + "' - ignored"); continue; }}
    if (bh == {PKG}.SkillDefs.EXPLORATION) {{ named = true; continue; }}
    bx[bh] = true;''')
before('''  BONUS_XP = bx;
''', '''  bx[{PKG}.SkillDefs.EXPLORATION] = false;
''')
after('''    if (gh < 0 || gh == {PKG}.SkillDefs.COMBAT) {{ {PKG}.SkillCfg.warn("bridge.bonus.addxpSkills: unknown skill '" + gt + "' - ignored"); continue; }}
''', '''    if (gh == {PKG}.SkillDefs.EXPLORATION) {{ named = true; continue; }}
''')
before('''  BONUS_ADDXP = gx;
''', '''  gx[{PKG}.SkillDefs.EXPLORATION] = false;
  if (named) {PKG}.SkillCfg.warn("bridge.bonus.xpSkills / bridge.bonus.addxpSkills: Exploration never gets XP bonuses (Skyy) - ignored");
''')

# ================================================================ 3.2 BridgeXp.offer: no multiplier, no tree bonus for a non-boostable slot
rep('''# Any thread; no I/O; never blocks.
bxp.addMethod(''', '''# Any thread; no I/O; never blocks. 0.4.1: a slot that is not SkillDefs.boostable (Exploration) is paid its base XP exactly - no xp
# multiplier, no tree bonus (still inside bridge.maxXpPerMinute).
bxp.addMethod(''')
rep('''  long amt = {PKG}.SkillCfg.scaled(base);
  if (!grant || {PKG}.SkillBonus.grantBonus(slot)) amt = {PKG}.SkillBonus.boost(u, slot, amt);''',
    '''  boolean canBoost = {PKG}.SkillDefs.boostable(slot);
  long amt = canBoost ? {PKG}.SkillCfg.scaled(base) : base;
  if (canBoost && (!grant || {PKG}.SkillBonus.grantBonus(slot))) amt = {PKG}.SkillBonus.boost(u, slot, amt);''')
rep('''    {PKG}.SkillXp.gain3(pr, this.slot, this.amt, true, false);
''', '''    {PKG}.SkillXp.gain3(pr, this.slot, this.amt, this.slot != {PKG}.SkillDefs.EXPLORATION, false);
''')
rep('''# ================= BridgeTask (0.4): cross-mod XP award on the player's world thread =================
''', '''# ================= BridgeTask (0.4): cross-mod XP award on the player's world thread =================
# 0.4.1: Exploration grants add no "+N Exploration XP" chat line (note = false): SkyyExploration writes its own chest / zone /
# aggregated chunk lines (hidden by /explore quiet); level-up lines and coins show as usual.
''')
rep('''  if (slot < 0 || slot >= {PKG}.SkillDefs.N) return 0.0;
  boolean[] on = {PKG}.BridgeCfg.BONUS_XP;''', '''  if (slot < 0 || slot >= {PKG}.SkillDefs.N) return 0.0;
  if (!{PKG}.SkillDefs.boostable(slot)) return 0.0;
  boolean[] on = {PKG}.BridgeCfg.BONUS_XP;''')

# ================================================================ 3.4 Acrobatics tree dodge
before('''# dodge boost: extra push along the client's horizontal velocity''', r'''# 0.4.1 (Exploration-Build-Spec 3.4): the Acrobatics skill tree's dodge nodes - SkyyTrees 0.2 posts skill:bonus:<uuid> "dodge.acrobatics"
# (a fraction, like dodgeBonus); summed over every source, clamped 0..acro.treeDodgeMax; only while acro.enabled and acro.dodgeBoost
acro.addMethod(CtNewMethod.make(f"""
public static double treeDodge(java.util.UUID u) {{
  if (u == null || !{PKG}.AcroCfg.ENABLED || !{PKG}.AcroCfg.DODGE_BOOST) return 0.0;
  double t = {PKG}.SkillBonus.sum(u, "dodge.acrobatics");
  if (Double.isNaN(t) || t <= 0.0) return 0.0;
  double mx = {PKG}.AcroCfg.TREE_DODGE_MAX;
  return t > mx ? mx : t;
}}""", acro))
''')
rep('''  double f = dodgeBonus({PKG}.SkillStore.level(u, {PKG}.SkillDefs.ACROBATICS));
  if (f <= 0.0) return;''', '''  double f = dodgeBonus({PKG}.SkillStore.level(u, {PKG}.SkillDefs.ACROBATICS)) + treeDodge(u);
  if (f <= 0.0) return;''')

# ================================================================ 3.5 tree buttons: treeName + treeAvailable
rep('''# /tree argument of a slot (SkyyTrees 0.1 trees: mining, foraging, farming, cooking); null = no tree for that skill''',
    '''# /tree argument of a slot (SkyyTrees 0.1 trees: mining, foraging, farming, cooking; SkyyTrees 0.2 adds acrobatics, exploration);
# null = no tree for that skill. Whether the RUNNING SkyyTrees has that tree = treeAvailable (0.4.1, below).''')
rep('''  if (slot == {PKG}.SkillDefs.COOKING) return "cooking";
  return null;
}}""", sbn))
''', r'''  if (slot == {PKG}.SkillDefs.COOKING) return "cooking";
  if (slot == {PKG}.SkillDefs.ACROBATICS) return "acrobatics";
  if (slot == {PKG}.SkillDefs.EXPLORATION) return "exploration";
  return null;
}}""", sbn))
# 0.4.1: a Tree button for this slot? SkyyTrees running (tree:fn:level) AND its bridge tree:names (SkyyTrees 0.2: comma list of tree
# labels) lists the slot; without tree:names (SkyyTrees 0.1) only its four trees - exactly the 0.4 buttons
sbn.addMethod(CtNewMethod.make(f"""
public static boolean treeAvailable(int slot) {{
  if (slot < 0 || slot >= {PKG}.SkillDefs.N || treeName(slot) == null || !treesOn()) return false;
  Object o = null;
  try {{ o = {PKG}.SkillStore.bridge().get("tree:names"); }} catch (Throwable t) {{ }}
  if (!(o instanceof String)) return slot == {PKG}.SkillDefs.MINING || slot == {PKG}.SkillDefs.FORAGING || slot == {PKG}.SkillDefs.FARMING || slot == {PKG}.SkillDefs.COOKING;
  String[] ps = ((String) o).split(",");
  for (int i = 0; i < ps.length; i++) {{
    String nm = ps[i].trim();
    if (nm.equalsIgnoreCase({PKG}.SkillDefs.LABELS[slot]) || nm.equalsIgnoreCase({PKG}.SkillDefs.NAMES[slot])) return true;
  }}
  return false;
}}""", sbn))
''')

# ================================================================ 3.5 /skills page
rep('''"Group #SkyySkills {{ Anchor: (Width: 640, Height: 624);''', '''"Group #SkyySkills {{ Anchor: (Width: 640, Height: 690);''')
rep('''        if ({PKG}.SkillBonus.treeName(sl) != null) {{''', '''        if ({PKG}.SkillBonus.treeAvailable(sl)) {{''')
rep('''Gather - brew - smelt - cook - fight with your class weapons - run jump fall dodge.  Stats shows every boost''',
    '''Gather - brew - smelt - cook - class weapons - run jump fall dodge - explore.  Stats shows every boost''')

# ================================================================ 3.5 Stats page
before('''# 0.4 trees bridge: "Skill tree: +X% double drops, +Y% XP" from skill:bonus:<uuid> (SkyyTrees); null when both are 0
''', r'''# 0.4.1 (Exploration-Build-Spec 3.5): the Acrobatics "Skill tree:" line - SkyyTrees 0.2 posts its speed / jump / fall nodes as the movement
# source move:<uuid>["trees.acrobatics"] (flat layer: speed = fraction of vanilla speed, jump = blocks, fallDamage = negative fraction) and
# its dodge nodes as skill:bonus dodge.acrobatics (Acro.treeDodge, clamped), plus the XP bonus if an admin lists Acrobatics; null = nothing
spg.addMethod(CtNewMethod.make(f"""
public static String acroTreeLine(java.util.UUID u) {{
  java.util.ArrayList parts = new java.util.ArrayList();
  try {{
    java.util.Map m = {PKG}.MoveSync.sources(u, false);
    Object o = null;
    if (m != null) o = m.get("trees.acrobatics");
    if (o instanceof java.util.Map) {{
      java.util.Map e = (java.util.Map) o;
      double sp = (double) {PKG}.MoveSync.num(e.get("speed"));
      double jp = (double) {PKG}.MoveSync.num(e.get("jump"));
      double fd = (double) {PKG}.MoveSync.num(e.get("fallDamage"));
      if (sp > 0.00001) parts.add("+" + pc(sp) + " speed");
      if (jp > 0.00001) parts.add("+" + num(jp) + " blocks jump");
      if (fd < -0.00001) parts.add("-" + pc(0.0 - fd) + " fall damage");
    }}
  }} catch (Throwable t) {{ }}
  double dg = {PKG}.Acro.treeDodge(u);
  if (dg > 0.00001) parts.add("+" + pc(dg) + " dodge push");
  double xb = {PKG}.SkillBonus.xpBonus(u, {PKG}.SkillDefs.ACROBATICS);
  if (xb > 0.00001) parts.add("+" + pc(xb) + " XP");
  if (parts.isEmpty()) return null;
  StringBuilder sb = new StringBuilder("Skill tree: ");
  for (int i = 0; i < parts.size(); i++) {{
    if (i > 0) sb.append(", ");
    sb.append((String) parts.get(i));
  }}
  return sb.toString();
}}""", spg))
''')
rep('''public static String treeLine(java.util.UUID u, int s) {{
  double dd = {PKG}.SkillBonus.dd(u, s);''', '''public static String treeLine(java.util.UUID u, int s) {{
  if (s == {PKG}.SkillDefs.ACROBATICS) return acroTreeLine(u);
  double dd = {PKG}.SkillBonus.dd(u, s);''')
after('''  int hooked = hook(u, s, lv, next, out);
''', '''  if (s == {PKG}.SkillDefs.EXPLORATION && !next) {{
    if (!{PKG}.ExplCfg.ENABLED) out.add("Exploration XP is turned off on this server (exploration.enabled=false)");
    else if (hooked < 0) out.add("Install SkyyExploration to earn Exploration XP");
    out.add("Exploration XP ignores the xp multiplier and every skill-tree or booster bonus");
  }}
''')
before('''  if (s == {PKG}.SkillDefs.COMBAT) return "Your combat skill is your class skill''',
       '''  if (s == {PKG}.SkillDefs.EXPLORATION) return "Earn XP by exploring - open loot chests for the first time - walk into new chunks (not while flying) - discover Hytale's zones. Once each per profile. XP boosters never apply";
''')
after('''  b.set("#" + id + ".Text", text);
}}""", spg))
''', r'''# 0.4.1: the same line with Wrap: true (the Exploration how-to text is longer than one line)
spg.addMethod(CtNewMethod.make(f"""
public static void wrapLine({UCB} b, String id, String text, String color, int size, int h) {{
  b.appendInline("#SkyySkStats", "Label #" + id + " {{ Anchor: (Height: " + h + "); Text: \\"\\"; Style: (FontSize: " + size + ", TextColor: " + color + ", VerticalAlignment: Center, Wrap: true); }}");
  b.set("#" + id + ".Text", text);
}}""", spg))
''')
rep('''  line(b, "SkyyStHow", how(s), "#8fa6ba", 10, false, 22);
''', '''  if (s == {PKG}.SkillDefs.EXPLORATION) wrapLine(b, "SkyyStHow", how(s), "#8fa6ba", 10, 30);
  else line(b, "SkyyStHow", how(s), "#8fa6ba", 10, false, 22);
''')
rep('''  String tree = {PKG}.SkillBonus.treesOn() ? {PKG}.SkillBonus.treeName(s) : null;''',
    '''  String tree = {PKG}.SkillBonus.treeAvailable(s) ? {PKG}.SkillBonus.treeName(s) : null;''')

# ================================================================ 3.5 skill args
rep('''"mining | foraging | farming | alchemy | smithing | cooking | acrobatics | combat (your class skill) | archery | swordsmanship | assassination | shaman | sorcery"''',
    '''"mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | assassination | shaman | sorcery"''', 2)
rep('''"mining | foraging | farming | alchemy | smithing | cooking | acrobatics | combat (your class skill) | archery | swordsmanship | sorcery"''',
    '''"mining | foraging | farming | alchemy | smithing | cooking | acrobatics | exploration | combat (your class skill) | archery | swordsmanship | sorcery"''')
rep('''Use mining, foraging, farming, alchemy, smithing, cooking, acrobatics, combat (your class skill)''',
    '''Use mining, foraging, farming, alchemy, smithing, cooking, acrobatics, exploration, combat (your class skill)''')

# ================================================================ plugin log line, class list, manifest
rep('''rows Alchemy (Alchemy Bench) / Smithing (Furnace) / Cooking (via SkyyCooking);''',
    '''rows Alchemy (Alchemy Bench) / Smithing (Furnace) / Cooking (via SkyyCooking) / Exploration (via SkyyExploration, no boosters);''')
rep('''afss, afn, cfn, xcmd, sbn, xfn, dfn, pfn):''', '''afss, afn, cfn, xcmd, sbn, xfn, dfn, pfn, exc):''')
rep('''Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics and your class combat skill (SkyyClasses) to level 100.''',
    '''Mining, Foraging, Farming, Alchemy, Smithing, Cooking, Acrobatics, Exploration and your class combat skill (SkyyClasses) to level 100.''')
rep('''cooking (SkyyCooking), kills with class weapons''', '''cooking (SkyyCooking), exploring (SkyyExploration - never boosted), kills with class weapons''')
rep('''Alchemy makes potion effects last longer and adds max Mana.''', '''Alchemy makes potion effects last longer and adds max Mana; Exploration adds max Stamina.''')

# ================================================================ sanity
assert 'VERSION = "0.4.1"' in s and "0.4.1 (research/Exploration-Build-Spec.md section 3" in s
assert "public static final int EXPLORATION = 13;" in s and "{ 0, 1, 2, 10, 11, 12, 4, 13, 3 }" in s and "{ 0, 1, 2, 3, 4, 10, 11, 12, 13 }" in s
assert s.count("{PKG}.SkillDefs.boostable(slot)") == 2 and "public static boolean boostable(int s)" in s
assert s.count("{PKG}.SkillBonus.treeAvailable(") == 2 and s.count("public static boolean treeAvailable(int slot)") == 1
assert "SkillBonus.treeName(sl) != null" not in s and "treesOn() ? {PKG}.SkillBonus.treeName(s)" not in s
assert s.count("{PKG}.ExplCfg.ensureDefaults(p);") == 1 and s.count("{PKG}.ExplCfg.read(p);") == 1
assert s.index("{PKG}.ExplCfg.read(p);") < s.index("{PKG}.BridgeCfg.read(p);"), "ExplCfg.read must run before BridgeCfg.read (GRANT)"
assert s.count("g[{PKG}.SkillDefs.EXPLORATION] = {PKG}.ExplCfg.ENABLED;") == 1
assert s.count('warn("bridge.bonus.xpSkills / bridge.bonus.addxpSkills: Exploration never gets XP bonuses (Skyy) - ignored")') == 1
assert s.count("+ treeDodge(u);") == 1 and s.count('"acro.treeDodgeMax", 0.25') == 1
assert s.count("return acroTreeLine(u);") == 1 and "Height: 624" not in s and s.count("Width: 640, Height: 690") == 1
assert "SkillDefs.ROWS" not in s
assert "--deploy" in s   # the script keeps its optional deploy switch; this workflow never passes it
# every PerkCfg array literal (static defaults AND the read() fallbacks) has one entry per KEYS entry (spec 3.3)
_keys = re.search(r"public static final String\[\] KEYS = new String\[\] \{ (.*?) \};", s).group(1)
NK = len(_keys.split(","))
assert NK == 9 and _keys.rstrip().endswith('"exploration"'), _keys
_pc = s[s.index("# ================= PerkCfg"):s.index("# ================= AlchCfg")]
_arrs = re.findall(r"new (?:double|String)\[\] \{\{? (.*?) \}\}?", _pc)
assert len(_arrs) == 11, "expected 1 KEYS + 5 static + 5 read() perk arrays, found %d" % len(_arrs)
for _a in _arrs:
    assert len(_a.split(",")) == NK, "perk array with %d entries (want %d): %s" % (len(_a.split(",")), NK, _a)
_rd = _pc[_pc.index("public static void read(java.util.Properties p) {{"):]
_rd = _rd[:_rd.index('}}""", pcfg))')]
assert len(re.findall(r"new (?:double|String)\[\] \{\{ ", _rd)) == 5, "PerkCfg.read() fallbacks"
assert not [a for a in re.findall(r"new (?:double|String)\[\] \{\{ (.*?) \}\}", _rd) if len(a.split(",")) == 8], "8-entry literal left in PerkCfg.read()"
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.4
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
