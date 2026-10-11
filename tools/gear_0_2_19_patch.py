"""Derive SkyyGear/build_skyygear_0.2.19.py from the LIVE 0.2.18 (build_skyygear_0.2.18.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_18_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_19_patch.py      then      python SkyyGear/build_skyygear_0.2.19.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.19.py

0.2.19 = TOOLTIP RESTYLE, look only (Skyy 2026-10-10: "is it posible for you to customize the item flavor text to make it look better?" + on the
mockups A Clean / B Wynncraft / C SkyBlock: "mix B and C i like the top part of wynncraft, but the Ability and part below that looks better on
skyblock."; docs/answered/ui.md LOCKED 2026-10-10 TOOLTIP STYLE line). No stat, roll, level or data change - only the item description text that
GearView writes (and the text of the mystery bags made from now on). Every tooltip SkyyGear renders, top to bottom (blank line between blocks):
  TOP (Wynncraft)
    name in the rarity colour (unchanged)
    grey "Fast Attack Speed" (weapons with a speed tier)
    base rows "Label value": "Damage 22-30", "Quick Shot 9 damage - 1 Mana - pierces 3 - 32 blocks", "Spell 43", "Health +16", "Resistance 7.9%
      (physical, projectile)", "Fire Resistance 10%", tool Power / Fortune / Wisdom rows (both sets on a multitool), mining-piece lines, grey notes
    rolled rows "+ Strength   +12" (green) / "- Walk Speed   -2%" (red); "coming later" / dead tool keys stay grey; Untiered fixed lines the same
      (their minus lines are the red downside); the Damage modifier is its own green row now (0.2.18 folded it into the damage line)
    the set block (green while complete / grey, a Mythic piece purple - unchanged)
    requirement rows: grey "Class Req: Warrior / Berserker" (weapons; from SkyyClasses' class:list + class:weapons:<Class>, longest matching
      prefix, no line without SkyyClasses or for a free weapon), "Lv. Min: 15 Swordsmanship" in the 0.2 gate colours (green met, red + "(you: M)"
      too low, grey not checked), "Gives no stats until ..." / "No bonus until ..." (red)
  BOTTOM (SkyBlock)
    Ability section: bold gold "Ability: <name>" + grey description + cost - "Charged Shot" (wand / staff: damage + "Mana Cost: N" + SkyyArmory's
      hold words), "Charged Attack" (a speed-tier melee weapon with a charged attack: its full-charge range), "Trade-off" (Untiered: the table's
      note, then each trick - upsides grey, downsides red); an unidentified item's gold "Identify: ..." line sits here
    the flavour slot: the item's own description (vanilla / pack lang) in italic grey - empty when the item has none (it was the grey block at
      the top of the description in 0.2.18)
    grey "Reforge: Sharp (2x)" (a reforged item), grey "This item can be reforged!" (identified, forgeable, not Untiered, not a Mining Set piece)
    bold rarity + type line in the rarity colour: "RARE SWORD", "LEGENDARY HELMET", "UNIQUE PICKAXE", "FABLED MULTITOOL" (0.2.18: "RARE WEAPON")
  Unidentified gear: grey "Unidentified - ...", red "Cannot be used until identified.", the requirement rows, gold Identify line, the bold
  rarity line. Mystery bags (GearUnid, new bags only - a bag's text is written once when it is made): the armor type, the grey / red lines,
  "Lv. Range: 5-9" (or "Lv. Min: 5"), the gold Identify line, bold "RARE SWORD".
MARKUP (VERIFIED in HytaleServer.jar): Message has color / bold / italic / monospace / underline (FormattedMessage carries Boolean bold, italic,
monospace); vanilla item descriptions use <b>, <i>, <color is=...> (server.lang) which the client turns into the same FormattedMessage fields.
UNVERIFIED in the client: that the item tooltip draws bold / italic for a structured Message (bold(true) / italic(true)) - worst case plain text.
No right alignment exists: the number follows the label ("Damage 22-30") and rolled rows use a 3-space gap ("+ Damage   +8%").
How the style travels: a line's colour string may start with "*" (bold) or "~" (italic) (GearView.bold / ital); GearView.seg reads it. Only the
tooltip lines carry it (never statLines, which the Reforge / Identify page columns read as a plain TextColor). The sig hashes every line + its
colour string, so each stack re-renders ONCE after the update (the document is untouched) and is stable after that.
Plain text (gear:fn:describe, /gear, the Reforge page) follows the same order without markup (blank lines and the flavour slot are dropped).
The level: the item level = its use requirement, shown once on "Lv. Min: N"; every number is the levelled one (the 0.2.1 rule: base rows show
the item's own levelled numbers, a Lv 1 kit item its vanilla ones) - the per-line "at Lv N" words are gone (Wynncraft short rows).
GearBase.shots answers one more element ([7] = SkyyArmory's quick words) so the quick row is rebuilt from numbers, not parsed.
ROLLBACK (for tools/deploy_set.py, reported, not edited here): 0.2.19 -> 0.2.18 is safe: no saved data changes; stacks re-render once to the
0.2.18 text; mystery bags made under 0.2.19 keep the new text (no bag is re-rendered by either version).
FIX ROUND (critics, 2026-10-10): (1) plain text (gear:fn:describe -> the SkyyAuctions item page, 12 lines; /gear) drops the owner hint "This
item can be reforged!" and folds the Ability section into one line, so a rolled Rare sword fits the Auctions page again; (2) GearCfg.cfgEpoch
adds classSig (a hash of SkyyClasses' class:list + class:weapons:*) so "Class Req" re-renders when SkyyClasses' data changes at runtime.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.18.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.19.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.18"' in s and s.startswith('"""SkyyGear 0.2.18 - build script'), "build_skyygear_0.2.18.py is not the live 0.2.18"
assert "public static String reqLine" not in s and "TOOLTIP RESTYLE" not in s, "0.2.18 already has the 0.2.19 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


def cut(start, end, new):
    """replace s[start anchor : end anchor) (the start anchor unique, the end anchor = the first one after it)"""
    global s
    assert s.count(start) == 1, "start anchor count %d: %s" % (s.count(start), start[:120])
    a = s.index(start)
    b = s.index(end, a + len(start))
    s = s[:a] + new + s[b:]


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.18 - build script (javassist via jpype). GENERATED by tools/gear_0_2_18_patch.py from the LIVE 0.2.17 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.18.py -> SkyyGear/SkyyGear-0.2.18.jar (never --deploy).

0.2.18 = ''', '''"""SkyyGear 0.2.19 - build script (javassist via jpype). GENERATED by tools/gear_0_2_19_patch.py from the LIVE 0.2.18 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.19.py -> SkyyGear/SkyyGear-0.2.19.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.19 = "):].strip() + '''

0.2.18 (the base, everything below is still true unless 0.2.19 above says otherwise):
0.2.18 = ''')
rep('VERSION = "0.2.18"', 'VERSION = "0.2.19"')

# ================================================================================================================ 1. GearBase.shots: + the quick words
rep('''# Long quick damage (-1 = none), Integer charged Mana, Integer quick Mana, String traversal line (0.2.4; null = none) }''',
    '''# Long quick damage (-1 = none), Integer charged Mana, Integer quick Mana, String traversal line (0.2.4; null = none), String quick words
# (0.2.19, SkyyArmory's [9]; "" = none) }''')
rep('''    return new Object[] { c, q, Long.valueOf(cv), Long.valueOf(qv), Integer.valueOf(cm), Integer.valueOf(qm), tw.length() > 0 ? tw : null };''',
    '''    return new Object[] { c, q, Long.valueOf(cv), Long.valueOf(qv), Integer.valueOf(cm), Integer.valueOf(qm), tw.length() > 0 ? tw : null, qw };''')

# ================================================================================================================ 2. GearView: style helpers
rep('''# weapon base damage from the engine's own damage data (SkyyRolls 0.1.4 rangeOf / damageText, ItemWeapon basic breakdown)''',
    r'''# ####################################################################################################################################
# 0.2.19 TOOLTIP STYLE (tools/gear_0_2_19_patch.py header): Wynncraft top + SkyBlock bottom. A line's colour string may carry a style mark:
# "*#hex" = bold, "~#hex" = italic (seg reads it; only tooltip lines carry it - statLines, which the pages read as a TextColor, never do).
# FLAVOR = the flavour-slot marker line (descMsg puts the item's own description there; plain drops it).
# ####################################################################################################################################
F(gvw, 'public static final String FLAVOR = String.valueOf((char) 1) + "flavor";')
F(gvw, 'public static final String GAP = "   ";')
F(gvw, 'public static final String REFORGE_HINT = "This item can be reforged!";')
M(gvw, 'public static String bold(String hex) { return "*" + (hex == null ? "" : hex); }')
M(gvw, 'public static String ital(String hex) { return "~" + (hex == null ? "" : hex); }')
M(gvw, r"""
public static @MSG@ seg(String t, String c) {
  if (c == null || c.length() == 0) return @MSG@.raw(t);
  boolean b = c.charAt(0) == '*';
  boolean it = c.charAt(0) == '~';
  String h = (b || it) ? c.substring(1) : c;
  @MSG@ m = h.length() > 0 ? @MSG@.raw(t).color(h) : @MSG@.raw(t);
  if (b) m = m.bold(true);
  if (it) m = m.italic(true);
  return m;
}""")
# a base row: "Damage 22-30" (Wynncraft: the number right after the label - the client has no right alignment)
M(gvw, 'public static String row(String label, String val) { return label + " " + val; }')
# a rolled row: "+ Strength   +12" / "- Walk Speed   -2%" (+ the stat's own note); unknown stat keys are kept and shown by name (rule 3)
M(gvw, r"""
public static String rollLine(String key, int v) {
  int i = @PKG@.GearDefs.sIndex(key);
  String lab = i < 0 ? key : @PKG@.GearDefs.S_LABEL[i];
  String val = i < 0 ? (v >= 0 ? "+" : "") + v : valText(key, v);
  return (v < 0 ? "- " : "+ ") + lab + GAP + val + (i < 0 ? "" : suffix(i));
}""")
# green up / red down; grey = coming later, Charged Attack Damage while charged.on is off, a dead key on a tool
M(gvw, r"""
public static String rollCol(String key, int v, boolean dead) {
  if (dead || dim(key)) return @PKG@.GearDefs.C_GRAY;
  return v < 0 ? @PKG@.GearDefs.C_BAD : @PKG@.GearDefs.C_OK;
}""")
# the type word of the rarity line ("RARE SWORD"): the id's family word (the mystery bag names: Shortbow = BOW, Bo = BO STAFF, armor by slot)
M(gvw, r"""
public static String typeWord(String id) {
  if (id == null) return "ITEM";
  if (@PKG@.GearData.isMulti(id)) return "MULTITOOL";
  int s = @PKG@.GearData.slotOf(id);
  if (s == 2) {
    if (id.endsWith("_Head")) return "HELMET";
    if (id.endsWith("_Chest")) return "CHESTPLATE";
    if (id.endsWith("_Hands")) return "GAUNTLETS";
    if (id.endsWith("_Legs")) return "LEGGINGS";
    return "ARMOR";
  }
  if (id.startsWith("Weapon_") || id.startsWith("Tool_")) {
    String[] p = id.split("_");
    if (p.length > 1 && p[1].length() > 0) {
      if (p[1].equals("Shortbow") || p[1].equals("Longbow")) return "BOW";
      if (p[1].equals("Bo")) return "BO STAFF";
      return p[1].toUpperCase();
    }
  }
  return slotWord(id);
}""")
# "Warrior / Berserker": the enabled classes (SkyyClasses class:list "Name:Skill,...") whose class:weapons:<Name> prefix matches the id - the
# longest matching prefix wins (class:weapons:free counts too: a free weapon = no line); null = no line (no SkyyClasses, nothing matches)
M(gvw, r"""
public static int prefixLen(Object w, String id) {
  if (!(w instanceof String) || id == null) return -1;
  String[] ps = ((String) w).split(",");
  int best = -1;
  for (int k = 0; k < ps.length; k++) {
    String p = ps[k].trim();
    if (p.length() > best && p.length() > 0 && id.startsWith(p)) best = p.length();
  }
  return best;
}""")
M(gvw, r"""
public static String classReq(String id) {
  try {
    Object list = @PKG@.Gear.bget("class:list");
    if (!(list instanceof String) || id == null) return null;
    String[] es = ((String) list).split(",");
    int best = prefixLen(@PKG@.Gear.bget("class:weapons:free"), id);
    boolean free = best > 0;
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < es.length; i++) {
      String e = es[i].trim();
      int c = e.indexOf(':');
      String nm = c >= 0 ? e.substring(0, c).trim() : e;
      if (nm.length() == 0) continue;
      int n = prefixLen(@PKG@.Gear.bget("class:weapons:" + nm), id);
      if (n <= 0 || n < best) continue;
      if (n > best) { sb.setLength(0); best = n; free = false; }
      if (sb.length() > 0) sb.append(" / ");
      sb.append(nm);
    }
    if (free || sb.length() == 0) return null;
    return sb.toString();
  } catch (Throwable t) { return null; }
}""")
# may this document be reforged (the "This item can be reforged!" line): GearForge.refuse + reforge's own refusals, read only
M(gvw, r"""
public static boolean canReforge(String id, @BD@ d) {
  if (id == null || d == null || !@PKG@.GearData.forgeable(id) || !@PKG@.GearData.identified(d)) return false;
  int r = @PKG@.GearData.rarity(d);
  if (r == @PKG@.GearDefs.R_UT) return false;
  if (r == @PKG@.GearDefs.R_SET && @PKG@.GearMine.isPiece(id)) return false;
  return true;
}""")
# the item has its own description (the flavour slot; moved up from below nameMsg in 0.2.19 - lines() calls it)
M(gvw, r"""
public static boolean hasDesc(String id) {
  try { @ITM@ it = @PKG@.Gear.item(id); return it != null && @PKG@.Gear.tr(it.getDescriptionTranslationKey()) != null; } catch (Throwable t) { return false; }
}""")
# a block of lines, a blank line before it when something is above (the tooltip's dividers)
M(gvw, r"""
public static void sect(java.util.ArrayList txt, java.util.ArrayList col, java.util.ArrayList t, java.util.ArrayList c) {
  if (t.isEmpty()) return;
  if (!txt.isEmpty()) { txt.add(""); col.add(null); }
  for (int i = 0; i < t.size(); i++) { txt.add(t.get(i)); col.add(c.get(i)); }
}""")
# weapon base damage from the engine's own damage data (SkyyRolls 0.1.4 rangeOf / damageText, ItemWeapon basic breakdown)''')

# ================================================================================================================ 3. armor rows: "Label value"
rep('''        if (add != 0.0) st.add(nm + ": " + @PKG@.Gear.fnum(add));
        if (mul != 0.0) st.add(nm + ": " + @PKG@.Gear.fnum(mul * 100.0) + "%");''',
    '''        if (add != 0.0) st.add(nm + " " + @PKG@.Gear.fnum(add));
        if (mul != 0.0) st.add(nm + " " + @PKG@.Gear.fnum(mul * 100.0) + "%");''', count=2)
rep('''        StringBuilder sb = new StringBuilder("Armor: ");''', '''        StringBuilder sb = new StringBuilder("Armor ");''')
rep('''        if (pc != 0.0) st.add(cause + " resistance: " + @PKG@.GearBase.pct(pc));
        if (fl != 0.0) st.add(cause + " resistance: " + @PKG@.Gear.fnum(fl));''',
    '''        if (pc != 0.0) st.add(cause + " Resistance " + @PKG@.GearBase.pct(pc));
        if (fl != 0.0) st.add(cause + " Resistance " + @PKG@.Gear.fnum(fl));''')
rep('''  int lv = @PKG@.GearLevel.level(id, d);
  out.add("Health at Lv " + lv + ": +" + @PKG@.GearBase.rint((double) tg[0]));
  out.add("Resistance at Lv " + lv + ": " + @PKG@.GearBase.pct((double) tg[1]) + " (physical, projectile)");''',
    '''  out.add("Health +" + @PKG@.GearBase.rint((double) tg[0]));          // 0.2.19: the level is on the Lv. Min row
  out.add("Resistance " + @PKG@.GearBase.pct((double) tg[1]) + " (physical, projectile)");''')

# ================================================================================================================ 4. the requirement row
rep('''M(gvw, r"""
public static void add(java.util.ArrayList txt, java.util.ArrayList col, String t, String c) {''',
    r'''# 0.2.19: the requirement row "Lv. Min: 15 Swordsmanship" - gateLine's states and colours exactly (gateLine keeps its text for the pages)
M(gvw, r"""
public static Object[] reqLine(java.util.UUID owner, String id, @BD@ d, int need) {
  String kind = @PKG@.GearData.kind(d);
  String gate = @PKG@.GearData.gate(d);
  String lv = "Lv. Min: " + need;
  boolean mine = @PKG@.GearMine.isPiece(id);
  if (mine) gate = "Mining";
  if (!mine && !@PKG@.GearDefs.enforcedKind(kind)) {
    if (gate.length() == 0) return new Object[] { "", null, Boolean.FALSE, "" };
    if (@PKG@.GearCfg.PART_TOOLS && @PKG@.GearTool.fam(id) > 0) {
      Object[] tc = @PKG@.GearGate.check(owner, id, d, need);
      String tl = (String) tc[1];
      String treq = lv + " " + (tl.length() > 0 ? tl : gate);
      int tst = ((Integer) tc[5]).intValue();
      if (tst != 0) return new Object[] { treq, @PKG@.GearDefs.C_GRAY, Boolean.FALSE, gate };
      if (((Boolean) tc[0]).booleanValue()) return new Object[] { treq, @PKG@.GearDefs.C_OK, Boolean.FALSE, gate };
      int th = ((Integer) tc[3]).intValue();
      return new Object[] { treq + " (you: " + (th < 0 ? 0 : th) + ")", @PKG@.GearDefs.C_BAD, Boolean.FALSE, gate };
    }
    return new Object[] { lv + " " + gate, @PKG@.GearDefs.C_GRAY, Boolean.FALSE, gate };
  }
  Object[] c = @PKG@.GearGate.check(owner, id, d, need);
  String label = (String) c[1];
  boolean ok = ((Boolean) c[0]).booleanValue();
  int have = ((Integer) c[3]).intValue();
  int st = ((Integer) c[5]).intValue();
  String req = label.length() > 0 ? lv + " " + label : lv;
  if (st == 4 || st == 5 || st == 3) return new Object[] { req, @PKG@.GearDefs.C_GRAY, Boolean.FALSE, label };
  if (st == 2) {
    if (ok) return new Object[] { lv, @PKG@.GearDefs.C_GRAY, Boolean.FALSE, "Level" };
    return new Object[] { lv + " (skills unavailable)", @PKG@.GearDefs.C_BAD, Boolean.TRUE, "Level" };
  }
  if (st == 1) {
    if (ok) return new Object[] { req, @PKG@.GearDefs.C_OK, Boolean.FALSE, label };
    return new Object[] { req + " (pick a class)", @PKG@.GearDefs.C_BAD, Boolean.TRUE, label };
  }
  if (ok) return new Object[] { req, @PKG@.GearDefs.C_OK, Boolean.FALSE, label };
  return new Object[] { req + " (you: " + (have < 0 ? 0 : have) + ")", @PKG@.GearDefs.C_BAD, Boolean.TRUE, label };
}""")
M(gvw, r"""
public static void add(java.util.ArrayList txt, java.util.ArrayList col, String t, String c) {''')

# ================================================================================================================ 5. the rows + statLines (+ utRows)
cut('''# base value lines + modifier lines of an identified document (the tooltip body, the Reforge page's line columns)''',
    '''# 0.2.2: GearView.hints (0.2.1's grey note''',
    r'''# 0.2.19: a speed-tier weapon's rows: { "Fast Attack Speed", "Damage 7-9" (the tap's own steps x the level multiplier x the tier's hit weight =
# the PER-HIT damage, 0.2.6), the full-charge range "18-26" (x the level multiplier only) or null }; null = no tier line (GearSpeed.tipLines'
# numbers exactly, new words)
M(gvw, r"""
public static String[] speedRows(String id, @BD@ d) {
  if (!@PKG@.GearSpeed.shows(id, d)) return null;
  int t = @PKG@.GearSpeed.tierOf(d);
  int f = @PKG@.GearSpeed.famOf(id);
  double w = @PKG@.GearSpeed.weight(f, t);
  String[] out = new String[] { @PKG@.GearSpeed.tierName(t) + " Attack Speed", null, null };
  try {
    boolean on = @PKG@.GearBase.on();
    double m = on ? @PKG@.GearBase.mult(id, d, false) : 1.0;
    float[] r = @PKG@.GearSpeed.tapRange(id, t);
    if (r != null) out[1] = row("Damage", @PKG@.GearBase.rangeText(new float[] { (float) ((double) r[0] * m * w), (float) ((double) r[1] * m * w) }));
    float[] c = @PKG@.GearSpeed.chargedRange(id);
    if (r != null && c != null) out[2] = @PKG@.GearBase.rangeText(new float[] { (float) ((double) c[0] * m), (float) ((double) c[1] * m) });
  } catch (Throwable x) { }
  return out;
}""")
# the wand / staff quick row: "Quick Shot 9 damage - 1 Mana - pierces 3 - 32 blocks" (SkyyArmory's numbers + words, GearBase.shots)
M(gvw, r"""
public static String quickRow(Object[] sh) {
  String qw = sh.length > 7 && sh[7] instanceof String ? (String) sh[7] : "";
  return "Quick Shot " + ((Long) sh[3]).longValue() + " damage - " + ((Integer) sh[5]).intValue() + " Mana" + (qw.length() > 0 ? " - " + qw : "");
}""")
# a weapon's head (speed), base rows and Ability rows. 0.2.2 rules kept: a SkyyArmory wand / staff shows its two shots and never the melee line
# (unless its tap is still a melee swing); without SkyyArmory 0.2.1's damage / spell rows. The Damage modifier is its own rolled row now.
M(gvw, r"""
public static void weaponRows(String id, @BD@ d, int slot, java.util.ArrayList ht, java.util.ArrayList hc, java.util.ArrayList bt, java.util.ArrayList bc, java.util.ArrayList at, java.util.ArrayList ac) {
  boolean on = @PKG@.GearBase.on();
  Object[] sh = @PKG@.GearBase.shots(id, d);
  String[] spd = null;
  if (sh == null && slot == 0) spd = speedRows(id, d);
  if (spd != null) {
    add(ht, hc, spd[0], @PKG@.GearDefs.C_GRAY);
    if (spd[1] != null) add(bt, bc, spd[1], null);
    if (spd[2] != null) {
      add(at, ac, "Ability: Charged Attack", bold(@PKG@.GearDefs.C_GOLD));
      add(at, ac, "Deals " + spd[2] + " damage at full charge.", @PKG@.GearDefs.C_GRAY);
    }
  }
  if ((sh == null || sh[1] == null) && (spd == null || spd[1] == null)) {
    float[] lr = null;
    if (on && !@PKG@.GearBase.asVanilla(id, d, false)) lr = @PKG@.GearBase.range(id, d);
    if (lr != null) add(bt, bc, row("Damage", @PKG@.GearBase.rangeText(lr)), null);
    else {
      String b = damageText(id);
      if (b != null) add(bt, bc, row("Damage", b), null);
    }
  }
  if (sh != null) {
    if (sh[1] != null) add(bt, bc, quickRow(sh), null);
    add(at, ac, "Ability: Charged Shot", bold(@PKG@.GearDefs.C_GOLD));
    add(at, ac, "Deals " + ((Long) sh[2]).longValue() + " damage.", @PKG@.GearDefs.C_GRAY);
    add(at, ac, "Mana Cost: " + ((Integer) sh[4]).intValue(), @PKG@.GearDefs.C_GRAY);
    if (sh.length > 6 && sh[6] != null) add(at, ac, (String) sh[6], @PKG@.GearDefs.C_GRAY);     // 0.2.4: the hold's traversal (SkyyArmory)
  } else if (slot == 1 && on) {
    float[] sr = @PKG@.GearBase.spellRange(id, d);
    if (sr != null) add(bt, bc, row("Spell", @PKG@.GearBase.rangeText(sr)), null);
  }
}""")
# the levelled armor rows ("Health +16", "Resistance 7.9% (physical, projectile)", the other vanilla rows) or 0.2's plain ones
M(gvw, r"""
public static void baseRows(String id, @BD@ d, int slot, java.util.ArrayList ht, java.util.ArrayList hc, java.util.ArrayList bt, java.util.ArrayList bc, java.util.ArrayList at, java.util.ArrayList ac) {
  if (slot == 0 || slot == 1) { weaponRows(id, d, slot, ht, hc, bt, bc, at, ac); return; }
  if (slot != 2) return;
  java.util.ArrayList al = new java.util.ArrayList();
  boolean lv = levelArmorLines(id, d, al);
  if (!lv) armorLines(id, al);
  for (int i = 0; i < al.size(); i++) add(bt, bc, (String) al.get(i), null);
}""")
# the rolled rows: every modifier of the document, in its order
M(gvw, r"""
public static void rolledRows(String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  int slot = @PKG@.GearData.slotOf(id);
  @BA@ ms = @PKG@.GearData.mods(d);
  for (int i = 0; i < ms.size(); i++) {
    @BV@ m = ms.get(i);
    if (m == null || !m.isDocument()) continue;
    String k = @PKG@.GearData.str(m.asDocument(), "s", "?");
    int v = @PKG@.GearData.num(m.asDocument(), "v", 0);
    add(txt, col, rollLine(k, v), rollCol(k, v, slot == 3 && toolDead(k)));      // 0.2.17: tool modifiers are live
  }
}""")
# base value rows + rolled rows of an identified document (the Reforge / Identify page columns: plain colours, no style marks, no blank lines)
M(gvw, r"""
public static void statLines(String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  java.util.ArrayList at = new java.util.ArrayList();
  java.util.ArrayList ac = new java.util.ArrayList();
  baseRows(id, d, @PKG@.GearData.slotOf(id), txt, col, txt, col, at, ac);
  rolledRows(id, d, txt, col);
}""")
# 0.2.16 -> 0.2.19: an Untiered item - its stat lines (body at its level + fixed) as rolled rows (a minus line = the red downside), and its
# Ability section "Trade-off": the table's note (grey), then each trick - an upside grey, a downside red
M(gvw, r"""
public static boolean trickBad(int k, double v) {
  if (k == @PKG@.GearUtFx.T_TAKEN) return v > 0.0;
  if (k == @PKG@.GearUtFx.T_RANGE) return true;
  return v < 0.0;
}""")
M(gvw, r"""
public static void utRows(String id, @BD@ d, java.util.ArrayList rt, java.util.ArrayList rc, java.util.ArrayList at, java.util.ArrayList ac) {
  int[] l = @PKG@.GearUtFx.lines(id, d);
  if (l == null) {
    if (@PKG@.GearData.rarity(d) == @PKG@.GearDefs.R_UT && !@PKG@.GearCfg.UT_ON) add(rt, rc, "(Untiered lines are off on this server)", @PKG@.GearDefs.C_GRAY);
  } else {
    for (int i = 0; i < l.length; i++) if (l[i] != 0) add(rt, rc, rollLine(@PKG@.GearDefs.S_KEY[i], l[i]), rollCol(@PKG@.GearDefs.S_KEY[i], l[i], false));
  }
  add(at, ac, "Ability: Trade-off", bold(@PKG@.GearDefs.C_GOLD));
  String un = @PKG@.GearUt.note(id);
  add(at, ac, un != null ? un : "Untiered - fixed stats.", @PKG@.GearDefs.C_GRAY);
  double[] tk = null;
  if (l != null) tk = @PKG@.GearUtFx.tricks(id, d);
  for (int k = 0; tk != null && k < tk.length; k++) {
    if (tk[k] == 0.0) continue;
    add(at, ac, @PKG@.GearUtFx.trickText(k, tk[k]), trickBad(k, tk[k]) ? @PKG@.GearDefs.C_BAD : @PKG@.GearDefs.C_GRAY);
  }
}""")
''')

# ================================================================================================================ 6. lines(): the new order
cut('''# every tooltip line below the name (spec 6.1 identified, 6.2 unidentified), for the owner (null = neutral text). 0.2 (spec 7): the''',
    '''M(gvw, r"""
public static String nameText(String id, @BD@ d) {''',
    r'''# 0.2.19 TOOLTIP STYLE: every line below the name (spec 6.1 identified, 6.2 unidentified) for the owner (null = neutral text), in blocks with a
# blank line between: head (speed) / base rows / rolled rows / set / requirements / Ability / flavour slot / reforge + the bold rarity line
M(gvw, r"""
public static void lines(String id, @BD@ d, java.util.UUID owner, java.util.ArrayList txt, java.util.ArrayList col) {
  int r = @PKG@.GearData.rarity(d);
  int need = @PKG@.GearLevel.level(id, d);
  int slot = @PKG@.GearData.slotOf(id);
  String hex = @PKG@.GearDefs.R_HEX[r];
  Object[] g = reqLine(owner, id, d, need);
  String gt = (String) g[0];
  java.util.ArrayList ht = new java.util.ArrayList();
  java.util.ArrayList hc = new java.util.ArrayList();
  java.util.ArrayList bt = new java.util.ArrayList();
  java.util.ArrayList bc = new java.util.ArrayList();
  java.util.ArrayList rt = new java.util.ArrayList();
  java.util.ArrayList rc = new java.util.ArrayList();
  java.util.ArrayList st = new java.util.ArrayList();
  java.util.ArrayList sc = new java.util.ArrayList();
  java.util.ArrayList qt = new java.util.ArrayList();
  java.util.ArrayList qc = new java.util.ArrayList();
  java.util.ArrayList at = new java.util.ArrayList();
  java.util.ArrayList ac = new java.util.ArrayList();
  java.util.ArrayList lt = new java.util.ArrayList();
  java.util.ArrayList lc = new java.util.ArrayList();
  java.util.ArrayList ft = new java.util.ArrayList();
  java.util.ArrayList fc = new java.util.ArrayList();
  String cr = (slot == 0 || slot == 1) && "class".equals(@PKG@.GearData.gate(d)) ? classReq(id) : null;
  if (cr != null) add(qt, qc, "Class Req: " + cr, @PKG@.GearDefs.C_GRAY);
  if (gt.length() > 0) add(qt, qc, gt, (String) g[1]);
  if (!@PKG@.GearData.identified(d)) {
    add(bt, bc, "Unidentified - its modifiers appear when you identify it.", @PKG@.GearDefs.C_GRAY);
    add(bt, bc, slot == 2 ? "Gives no stats until identified." : "Cannot be used until identified.", @PKG@.GearDefs.C_BAD);
    add(at, ac, "Identify: " + @PKG@.GearCfg.idWhere() + " - " + @PKG@.Gear.fmt(@PKG@.GearCfg.costIdentify(r, need)) + " coins", @PKG@.GearDefs.C_GOLD);
  } else {
    if (slot == 2 && ((Boolean) g[2]).booleanValue()) add(qt, qc, "Gives no stats until " + g[3] + " " + need, @PKG@.GearDefs.C_BAD);
    if (slot == 3) {
      // 0.2.12: tool power + Fortune by level - its rows into the base block, its red "No bonus until ..." under the requirement
      java.util.ArrayList tt = new java.util.ArrayList();
      java.util.ArrayList tc = new java.util.ArrayList();
      @PKG@.GearTool.lines(owner, id, d, tt, tc);
      for (int i = 0; i < tt.size(); i++) {
        String c = (String) tc.get(i);
        if (@PKG@.GearDefs.C_BAD.equals(c)) add(qt, qc, (String) tt.get(i), c);
        else add(bt, bc, (String) tt.get(i), c);
      }
    }
    baseRows(id, d, slot, ht, hc, bt, bc, at, ac);
    if (slot == 2) @PKG@.GearMine.lines(owner, id, d, bt, bc);   // 0.2.15: a metal piece's mining lines
    rolledRows(id, d, rt, rc);
    if (r == @PKG@.GearDefs.R_UT) utRows(id, d, rt, rc, at, ac);  // 0.2.16
    @PKG@.GearSet.tipLines(owner, id, d, r, st, sc);              // 0.2.14
    if (hasDesc(id)) add(lt, lc, FLAVOR, null);
    String rf = @PKG@.GearData.str(d, "rf", null);
    int rfn = @PKG@.GearData.num(d, "rfN", 0);
    if (rf != null && rf.length() > 0) add(ft, fc, "Reforge: " + rf + (rfn > 0 ? " (" + rfn + "x)" : ""), @PKG@.GearDefs.C_GRAY);
    if (canReforge(id, d)) add(ft, fc, REFORGE_HINT, @PKG@.GearDefs.C_GRAY);
  }
  add(ft, fc, @PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + typeWord(id), bold(hex));
  sect(txt, col, ht, hc);
  sect(txt, col, bt, bc);
  sect(txt, col, rt, rc);
  sect(txt, col, st, sc);
  sect(txt, col, qt, qc);
  sect(txt, col, at, ac);
  sect(txt, col, lt, lc);
  sect(txt, col, ft, fc);
}""")
''')

# ================================================================================================================ 7. descMsg: style marks + the flavour slot
cut('''M(gvw, r"""
public static @MSG@ descMsg(String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {''',
    '''# spec 6.3 sig:''',
    r'''# 0.2.19: the description = the lines with their style marks; the flavour slot gets the item's own description (italic grey) - 0.2.18 put
# it at the top
M(gvw, r"""
public static @MSG@ descMsg(String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  @MSG@ m = @MSG@.empty();
  for (int i = 0; i < txt.size(); i++) {
    if (i > 0) m.insert(@MSG@.raw("\n"));
    String t = (String) txt.get(i);
    if (t.length() == 0) continue;
    if (FLAVOR.equals(t)) {
      try { m.insert(@PKG@.Gear.item(id).getDescriptionTranslationMessage().color(@PKG@.GearDefs.C_GRAY).italic(true)); } catch (Throwable x) { }
      continue;
    }
    m.insert(seg(t, (String) col.get(i)));
  }
  return m;
}""")
''')

# ================================================================================================================ 8. plain(): drop the flavour marker
# FIX ROUND (critic: the SkyyAuctions item page shows at most 12 lines of gear:fn:describe): plain text also drops the owner hint "This item
# can be reforged!" and folds an Ability section into ONE line ("Ability: Charged Shot - Deals 97 damage - Mana Cost: 5"; a part's final "."
# dropped) - the rolled Rare sword is 11 lines again, so the Auctions page keeps the rarity line. The tooltip itself is unchanged.
rep('''  for (int i = 0; i < txt.size(); i++) { String t = (String) txt.get(i); if (t.length() > 0) out.add(t); }
  String[] a = new String[out.size()];''', '''  for (int i = 0; i < txt.size(); i++) {
    String t = (String) txt.get(i);
    if (t.length() == 0 || FLAVOR.equals(t) || REFORGE_HINT.equals(t)) continue;
    if (t.startsWith("Ability: ")) {
      StringBuilder sb = new StringBuilder(t);
      while (i + 1 < txt.size()) {
        String n = (String) txt.get(i + 1);
        if (n.length() == 0 || FLAVOR.equals(n)) break;
        i++;
        if (n.endsWith(".")) n = n.substring(0, n.length() - 1);
        sb.append(" - ").append(n);
      }
      t = sb.toString();
    }
    out.add(t);
  }
  String[] a = new String[out.size()];''')

# ================================================================================================================ 8c. Class Req follows SkyyClasses
# FIX ROUND (critic: "Class Req" was not re-rendered when SkyyClasses' class:list / class:weapons:* change at runtime): GearCfg.classSig = a
# hash of those bridge strings (refreshed at most once a second, like armorySig) is part of cfgEpoch -> GearTick marks every player dirty and
# the sig (which carries cfgEpoch) re-renders the stacks whose text changed. No SkyyClasses = a constant.
rep('''M(gcf, r"""
public static long cfgEpoch() {''', r'''F(gcf, "public static volatile long CSIG = 0L;")
F(gcf, "public static volatile long CSIG_AT = 0L;")
M(gcf, r"""
public static long classCompute() {
  Object l = @PKG@.Gear.bget("class:list");
  long h = ahash(l) * 31L + ahash(@PKG@.Gear.bget("class:weapons:free"));
  if (l instanceof String) {
    String[] es = ((String) l).split(",");
    for (int i = 0; i < es.length; i++) {
      String e = es[i].trim();
      int c = e.indexOf(':');
      String nm = c >= 0 ? e.substring(0, c).trim() : e;
      if (nm.length() == 0) continue;
      h = h * 31L + ahash(@PKG@.Gear.bget("class:weapons:" + nm));
    }
  }
  return h;
}""")
M(gcf, r"""
public static long classSig() {
  long now = System.currentTimeMillis();
  long at = CSIG_AT;
  if (at != 0L && now >= at && now - at < 1000L) return CSIG;
  long h = classCompute();
  CSIG = h;
  CSIG_AT = now;
  return h;
}""")
M(gcf, r"""
public static long cfgEpoch() {''')
rep('''  return EPOCH * 1000003L + k + ka + armorySig() * 1000033L;''',
    '''  return EPOCH * 1000003L + k + ka + armorySig() * 1000033L + classSig() * 1000037L;     // 0.2.19 fix round: + SkyyClasses' Class Req data''')

# ================================================================================================================ 8b. hasDesc moves up (lines() calls it now)
rep('''M(gvw, r"""
public static boolean hasDesc(String id) {
  try { @ITM@ it = @PKG@.Gear.item(id); return it != null && @PKG@.Gear.tr(it.getDescriptionTranslationKey()) != null; } catch (Throwable t) { return false; }
}""")
# 0.2.19: the description = ''', "# 0.2.19: the description = ")

# ================================================================================================================ 9. mystery bags (new bags)
cut('''M(gunid, r"""
public static @MSG@ descMsg(@BD@ d) {''',
    '''M(gunid, r"""
public static @IS@ view(@IS@ s, @BD@ d) {''',
    r'''# 0.2.19 TOOLTIP STYLE: the armor type, what is unknown (grey), the refusal (red), "Lv. Range: 5-9", the gold Identify line, bold "RARE SWORD"
M(gunid, r"""
public static @MSG@ descMsg(@BD@ d) {
  java.util.ArrayList txt = new java.util.ArrayList();
  java.util.ArrayList col = new java.util.ArrayList();
  int r = rar(d);
  int ty = type(d);
  int at = at(d);
  boolean arm = ty >= 0 && @PKG@.GearPool.T_ARM[ty];
  if (arm && at > 0 && @PKG@.GearCfg.SHOW_AT) { txt.add(@PKG@.GearPool.AT_NAME[at] + " armor"); col.add(@PKG@.GearDefs.C_LABEL); }
  if (r == @PKG@.GearDefs.R_UT) { txt.add("Unidentified - which Untiered " + typeName(ty).toLowerCase() + " it is and its exact level are decided when you identify it. Untiered gear has fixed stats and one trade-off."); col.add(@PKG@.GearDefs.C_GRAY); }
  else { txt.add("Unidentified - which " + typeName(ty).toLowerCase() + " it is, its exact level and its modifiers are decided when you identify it."); col.add(@PKG@.GearDefs.C_GRAY); }
  txt.add(arm ? "Cannot be worn until identified." : "Cannot be used until identified."); col.add(@PKG@.GearDefs.C_BAD);
  txt.add(""); col.add(null);
  int lo = lo(d);
  int hi = hi(d);
  txt.add(lo == hi ? "Lv. Min: " + lo : "Lv. Range: " + lo + "-" + hi); col.add(@PKG@.GearDefs.C_GRAY);
  txt.add(""); col.add(null);
  txt.add("Identify: " + (@PKG@.GearCfg.IDENTIFY_CMD ? "/identify" : "at an identifier") + " - " + @PKG@.Gear.fmt(cost(d)) + " coins"); col.add(@PKG@.GearDefs.C_GOLD);
  txt.add(""); col.add(null);
  txt.add(@PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + typeName(ty).toUpperCase()); col.add(@PKG@.GearView.bold(@PKG@.GearDefs.R_HEX[r]));
  @MSG@ m = @MSG@.empty();
  for (int i = 0; i < txt.size(); i++) {
    if (i > 0) m.insert(@MSG@.raw("\n"));
    String t = (String) txt.get(i);
    if (t.length() == 0) continue;
    m.insert(@PKG@.GearView.seg(t, (String) col.get(i)));
  }
  return m;
}""")
''')

# ================================================================================================================ 10. manifest
rep(r'''count as both tools, a bit slower and with less Fortune (Mining + Foraging gate);''',
    r'''count as both tools, a bit slower and with less Fortune (Mining + Foraging gate); tooltips in the SkyWynn style (Wynncraft-style stat, roll and requirement rows on top, a SkyBlock-style Ability section, reforge line and bold rarity line below);''')

open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", DST)
