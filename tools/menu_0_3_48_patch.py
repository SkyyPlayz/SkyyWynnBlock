"""Derive SkyyMenu/build_skyymenu_0.3.48.py from the LIVE SkyyMenu 0.3.47 (python tools/menu_0_3_48_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_47_patch.py -> 0.3.47 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.48. Every anchor is asserted once; at the end every change is undone on a copy and
compared with 0.3.47 (nothing else changed). Line endings kept. The harness SkyyMenu/test_skyymenu_0.3.48.py is its own file.

0.3.48 (2026-11-01) = RARITY + TOOLTIP PASS for the Pets tile (rarity-pass round rar_menu; LOOKS ONLY). Skyy 2026-10-24: "make that the global
  default. if it has a rarity, it gets color coded. if it has flavor text, the text is well laid out, well organized, clear, readable, and
  color coded." + 2026-10-18 "make all the flavor text use a slightly bigger font, and color code everything".
  1. RARITY ICON + FRAME: the Pets tile (the only rarity-bearing thing SkyyMenu draws) shows SkyyPets' hidden rarity portrait
     Skyy_PetIcon_<Kind>_<Rarity> (SkyyPets 0.4.18+, 48 kinds x 6 rarities since 0.4.19; referenced by id at run time only - no SkyyPets
     file shipped or overridden) with the quality frame ON (setSkipItemQualityBackground(false) for that one icon; every other tile keeps
     true). The client draws the frame AND colours the popup title from the item's Quality (research/Vanilla-UI-Style-Guide.md 15, the
     proven SkyyPets 0.4.18 way). Fallback = 0.3.47's icon (Skyy_Menu_Icon_Pet_<Art> / ICON_PETS, frame skipped) when: no pet, a kind
     not in PET_RKIND (the 48 SkyyPets 0.4.22 frame kinds), an unknown rarity word, or a SkyyPets older than 0.4.19 (gate: its bridge key
     pets:fn:giveSecretEgg, put since 0.4.19).
  2. POPUP TITLE: stays plain text ("Pets - <name> Lv N"). DECISION: <color> spans in ItemGridSlot.setName are NOT proven (only in the
     Description; nameplate markup showed raw in 2026-10-02's test), so the title takes its rarity colour from the framed item's Quality
     (as SkyyPets' own grid does) and the coloured name + gold Lv are in the tooltip body. MenuPage.names (the info line) stays plain.
  3. TOOLTIP SECTIONS (Style Guide 15 colours): soft white #d6e4ee description / dim grey #7f93a6 'PET SLOT' / 'SUMMON SLOT' headers, each
     followed on the same line by the rarity-coloured "<Rarity> <Kind>" (a renamed pet: rarity-coloured name + "(<Rarity> <Kind>)"), gold
     #e8c25a "Lv N" or dim 'empty'; soft white "Pets owned: " + gold number; dim profile + command lines; unreadable file = red #ff7a7a.
     At most 6 text lines (= 0.3.47's tallest: the summon slot is now always listed, 'empty' when free). Every line is clipped to
     StatsCalc.LINE_MAX on its PLAIN text before the spans go on. MenuPage.bodies (the info box when tooltips are off) = the plain text.
  4. FOOTER COLOURS: FOOT_COLOR #ffff55 -> #ffcc00 (Style Guide 15 actions = SkyyPets TIP_FOOT), DIM_COLOR #ff5555 -> #ff7a7a (costs /
     blocked) - every tile's 'Click to open!' / 'Not installed' footer.
  Lang keys / slot names touched: none (all strings are Java run-time text in MenuData / PetTile / MenuPage.put / MenuUtil; no lang file).
  SAVED DATA: none. No new class / command / system. ROLLBACK to 0.3.47: safe alone (the plain icon + text come back).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.47.py"), os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.48.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.3.47"\n') and P.has("tools/menu_0_3_47_patch.py") and not P.has("PET_RKIND"), "not the generated SkyyMenu 0.3.47 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# the 48 kinds SkyyPets 0.4.22 ships a rarity portrait for (Server/Item/Items/SkyyPets/PetFrames/Skyy_PetIcon_<Kind>_<Rarity>.json, 288 items;
# the harness checks this list against the SET jar)
PET_RKIND = ['Antelope', 'Bear', 'Bison', 'Boar', 'Bunny', 'Camel', 'Cat', 'Chicken', 'Corgi', 'CrystalGolem', 'Deer', 'Dog', 'DragonBlood',
             'DragonCrystal', 'DragonFire', 'DragonLight', 'DragonPlain', 'DragonSky', 'DragonStorm', 'DragonTundra', 'DragonVoid', 'Fox',
             'Frog', 'Gecko', 'Goat', 'Hawk', 'Horse', 'Meerkat', 'Molerat', 'Moose', 'Mosshorn', 'Mouflon', 'Mouse', 'Owl', 'Rabbit', 'Ram',
             'Rat', 'Skeleton', 'SkeletonKnight', 'Skrill', 'Squirrel', 'Turkey', 'Tusker', 'VoidCrawler', 'VoidEye', 'VoidLarva', 'Warthog',
             'Wolf']

P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.48: rarity + tooltip pass (Skyy 2026-10-24 global rule): the Pets tile wears SkyyPets' rarity portrait with the quality frame (popup
       title in the rarity colour), its tooltip is sectioned + colour coded (Style Guide 15), every footer yellow is #ffcc00 / red #ff7a7a
       (notes: tools/menu_0_3_48_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.48.py.
''')
P.rep('VERSION = "0.3.47"\n', 'VERSION = "0.3.48"\n')

# ---------- 4. the footer colours (Style Guide 15) + the tooltip colour tokens + the rarity colours / frame kinds
P.rep('''FOOT_COLOR  = "#ffff55"
DIM_COLOR   = "#ff5555"
''', '''FOOT_COLOR  = SUI.COLOR["warning"]            # 0.3.48 #ffcc00:: Style Guide 15 "actions" yellow (= SkyyPets TIP_FOOT; was #ffff55)
DIM_COLOR   = "#ff7a7a"                       # 0.3.48: Style Guide 15 "costs" red (was #ff5555)
# 0.3.48: the tooltip colour code (research/Vanilla-UI-Style-Guide.md 15) + the rarity colours = SkyyPets' RARITY_COLORS (the vanilla item
# quality colours + the Mythic colour), Common .. Mythic in PetTile.RARITY order
TIP_SOFT, TIP_DIM, TIP_GOLD, TIP_BAD = SUI.COLOR["rowName"], SUI.COLOR["rowSub"], "#e8c25a", DIM_COLOR
assert (FOOT_COLOR, TIP_SOFT, TIP_DIM) == ("#ffcc00", "#d6e4ee", "#7f93a6"), "0.3.48: the kit tokens = Style Guide 15"
RAR_COL = [SUI.QUALITY["Common"], SUI.QUALITY["Uncommon"], SUI.QUALITY["Rare"], SUI.QUALITY["Epic"], SUI.QUALITY["Legendary"], SUI.RARITY["Mythic"]]
PET_RKIND = %r
assert len(RAR_COL) == 6 and all(c.startswith("#") and len(c) == 7 for c in RAR_COL), "0.3.48: one rarity colour per rarity"
''' % (PET_RKIND,))
P.rep('''F(dat, "public static final String ICON_PETS = %s;" % jstr(ICON_PETS))
''', '''F(dat, "public static final String ICON_PETS = %s;" % jstr(ICON_PETS))
# 0.3.48: SkyyPets' rarity portrait kinds (Skyy_PetIcon_<Kind>_<Rarity>), the rarity colours, the tooltip colour tokens
assert set(PET_ART) <= set(PET_RKIND) and len(PET_RKIND) == len(set(PET_RKIND)) == 48, "0.3.48: every Menu pet art kind has a SkyyPets rarity portrait"
F(dat, "public static final String[] PET_RKIND = %s;" % jarr(PET_RKIND))
F(dat, "public static final String[] RAR_COL = %s;" % jarr(RAR_COL))
for _n, _v in (("TIP_SOFT", TIP_SOFT), ("TIP_DIM", TIP_DIM), ("TIP_GOLD", TIP_GOLD), ("TIP_BAD", TIP_BAD)):
    F(dat, "public static final String %s = %s;" % (_n, jstr(_v)))
''')
P.rep('''M(dat, r"""
public static int viewIndex(String v) {''', '''# 0.3.48: one colour span (USE_MARKUP off = the plain text) - the only proven Description markup
M(dat, r"""
public static String tc(String hex, String t) {
  if (!USE_MARKUP) return t;
  return "<color is=" + Q + hex + Q + ">" + t + "</color>";
}""")
M(dat, r"""
public static int viewIndex(String v) {''')

# ---------- MenuUtil.plain: a tooltip text without its colour spans (the info box under the grid is a Label - no markup)
P.rep('''# a name that may be pasted into a command line: letters, digits and _ only
''', '''# 0.3.48: the text without <color ...> / </color> tags (MenuPage.bodies feed the info box Label when tooltips are off)
M(utl, r"""
public static String plain(String s) {
  if (s == null || s.indexOf("color") < 0) return s;     // tags matched char by char (lint back-text: no quoted tag literal)
  StringBuilder b = new StringBuilder();
  int i = 0;
  while (i < s.length()) {
    if (s.charAt(i) == '<' && (s.startsWith("color", i + 1) || s.startsWith("/color>", i + 1))) {
      int e = s.indexOf('>', i);
      if (e < 0) { b.append(s.substring(i)); break; }
      i = e + 1;
      continue;
    }
    b.append(s.charAt(i));
    i++;
  }
  return b.toString();
}""")
# a name that may be pasted into a command line: letters, digits and _ only
''')

# ---------- 1. PetTile: the rarity portrait (+ the gate), 3. the sectioned tooltip
P.rep('''M(pet, r"""
public static String icon(String[] pi) {
  if (!has(pi)) return @PKG@.MenuData.ICON_PETS;
''', '''# 0.3.48: the rarity word's index (PetTile.RARITY: Common 0 .. Mythic 5), -1 = unknown
M(pet, r"""
public static int rarIdx(String r) {
  if (r == null) return -1;
  for (int i = 0; i < RARITY.length; i++) if (RARITY[i].equals(r)) return i;
  return -1;
}""")
# 0.3.48: SkyyPets ships the 48-kind rarity portraits (0.4.19+; its bridge function pets:fn:giveSecretEgg is put since 0.4.19)
M(pet, r"""
public static boolean frames() {
  try { return @PKG@.MenuUtil.bridge().get("pets:fn:giveSecretEgg") != null; }
  catch (Throwable t) { return false; }
}""")
# 0.3.48: the pet slot's rarity portrait Skyy_PetIcon_<Kind>_<Rarity> (SkyyPets' hidden icon item, by id only), or null = 0.3.47's icon
M(pet, r"""
public static String ricon(String[] pi) {
  if (!has(pi) || rarIdx(pi[4]) < 0 || !frames()) return null;
  for (int i = 0; i < @PKG@.MenuData.PET_RKIND.length; i++) if (@PKG@.MenuData.PET_RKIND[i].equals(pi[1])) return "Skyy_PetIcon_" + pi[1] + "_" + pi[4];
  return null;
}""")
# 0.3.48: an icon that wears the quality frame (MenuPage.put): exactly a rarity portrait id (the base Skyy_PetIcon_<Kind> has no Quality)
M(pet, r"""
public static boolean framed(String icon) {
  if (icon == null || !icon.startsWith("Skyy_PetIcon_")) return false;
  int u = icon.lastIndexOf('_');
  return u > 12 && rarIdx(icon.substring(u + 1)) >= 0;
}""")
M(pet, r"""
public static String icon(String[] pi) {
  if (!has(pi)) return @PKG@.MenuData.ICON_PETS;
  String rc = ricon(pi);                       // 0.3.48: the rarity portrait first
  if (rc != null) return rc;
''')
P.rep('''M(pet, r"""
public static String body(java.util.UUID u, String[] pi) {
  int max = @PKG@.StatsCalc.LINE_MAX;''', '''# 0.3.48: one slot line - dim header, then the rarity-coloured "<Rarity> <Kind>" (a renamed pet: its name + "(<Rarity> <Kind>)") and the gold
# level, or dim "empty". A renamed pet whose line would not fit loses the end of its NAME (the spans stay); only a line that still
# cannot fit (an unrenamed pet, or fewer than 4 name characters left) is drawn clipped in one colour.
M(pet, r"""
public static String slotLine(String[] pi, int at, String label, int max) {
  String h = @PKG@.MenuData.tc(@PKG@.MenuData.TIP_DIM, label + "  ");
  if (pi[at].length() == 0) return h + @PKG@.MenuData.tc(@PKG@.MenuData.TIP_DIM, "empty");
  int ri = rarIdx(pi[at + 3]);
  String rc = ri < 0 ? @PKG@.MenuData.TIP_SOFT : @PKG@.MenuData.RAR_COL[ri];
  String all = label + "  " + slotText(pi, at);
  String kd = display(pi[at]);
  String nm = pi[at + 1];
  boolean named = !nm.equals(kd);
  if (all.length() > max) {                    // fix: shorten only a renamed pet's name (spans kept); else one colour
    int keep = nm.length() - (all.length() - max);
    if (!named || keep < 4) return @PKG@.MenuData.tc(rc, @PKG@.MenuUtil.clip(all, max));
    nm = @PKG@.MenuUtil.clip(nm, keep);
  }
  String lv = @PKG@.MenuData.tc(@PKG@.MenuData.TIP_GOLD, "Lv " + pi[at + 2]);
  if (!named) return h + @PKG@.MenuData.tc(rc, pi[at + 3] + " " + kd) + " " + lv;
  return h + @PKG@.MenuData.tc(rc, nm) + @PKG@.MenuData.tc(@PKG@.MenuData.TIP_DIM, " (") + @PKG@.MenuData.tc(rc, pi[at + 3] + " " + kd)
       + @PKG@.MenuData.tc(@PKG@.MenuData.TIP_DIM, ")") + " " + lv;
}""")
M(pet, r"""
public static String body(java.util.UUID u, String[] pi) {
  int max = @PKG@.StatsCalc.LINE_MAX;''')
P.rep('''  StringBuilder sb = new StringBuilder();
  sb.append(@PKG@.MenuUtil.clip("Your pets on this profile" + (pn.length() > 0 ? " (" + pn + ")" : "") + ". Click to see them all.", max));
  if (pi == null || pi.length != 10 || "bad".equals(pi[0])) sb.append("\\nYour pet file could not be read. Ask an admin.");
  else {
    sb.append("\\n").append(@PKG@.MenuUtil.clip("Pet slot: " + slotText(pi, 1), max));
    if (pi[5].length() > 0) sb.append("\\n").append(@PKG@.MenuUtil.clip("Summon slot: " + slotText(pi, 5), max));
    sb.append("\\n").append(@PKG@.MenuUtil.clip("Pets owned: " + pi[9], max));
  }
  sb.append("\\nPets stay on this profile - every profile has its own.");
  sb.append("\\nCommand: /pets (or /pet)");
  return sb.toString();
}""")''', '''  StringBuilder sb = new StringBuilder();   // 0.3.48: Style Guide 15 colours, sections (MenuData.tooltip puts the blank line after line 1)
  sb.append(@PKG@.MenuData.tc(@PKG@.MenuData.TIP_SOFT, @PKG@.MenuUtil.clip("Your pets on this profile" + (pn.length() > 0 ? " (" + pn + ")" : "") + ". Click to see them all.", max)));
  if (pi == null || pi.length != 10 || "bad".equals(pi[0])) sb.append("\\n").append(@PKG@.MenuData.tc(@PKG@.MenuData.TIP_BAD, "Your pet file could not be read. Ask an admin."));
  else {
    sb.append("\\n").append(slotLine(pi, 1, "PET SLOT", max));
    sb.append("\\n").append(slotLine(pi, 5, "SUMMON SLOT", max));
    sb.append("\\n").append(@PKG@.MenuData.tc(@PKG@.MenuData.TIP_SOFT, "Pets owned: ")).append(@PKG@.MenuData.tc(@PKG@.MenuData.TIP_GOLD, @PKG@.MenuUtil.clip(pi[9], 9)));
  }
  sb.append("\\n").append(@PKG@.MenuData.tc(@PKG@.MenuData.TIP_DIM, "Pets stay on this profile - every profile has its own."));
  sb.append("\\n").append(@PKG@.MenuData.tc(@PKG@.MenuData.TIP_DIM, "Command: /pets (or /pet)"));
  return sb.toString();
}""")''')

# ---------- 1. MenuPage.put: the quality frame for a rarity portrait only; the info box keeps the plain text
P.rep('''    if (dim) gs.setItemIncompatible(true);
    gs.setSkipItemQualityBackground(true);
    slots.set(idx, gs);
    this.acts[idx] = act;
    this.names[idx] = name;
    this.bodies[idx] = body;''', '''    if (dim) gs.setItemIncompatible(true);
    gs.setSkipItemQualityBackground(!@PKG@.PetTile.framed(icon));   // 0.3.48: the rarity frame + popup title colour (Pets tile) only
    slots.set(idx, gs);
    this.acts[idx] = act;
    this.names[idx] = name;
    this.bodies[idx] = @PKG@.MenuUtil.plain(body);                   // 0.3.48: the info box is a Label (no colour spans)''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.48 adds no system / command"
_i = P.s.index
assert _i("public static String tc(String hex") < _i("public static int rarIdx(String r)") < _i("public static boolean frames()") \
    < _i("public static String ricon(") < _i("public static boolean framed(") < _i("public static String icon(String[] pi)") \
    < _i("public static String slotText(") < _i("public static String slotLine(") < _i("public static String body(java.util.UUID u")
assert _i("public static String plain(String s)") < _i("public void put(java.util.ArrayList slots, int idx")
assert _i("public static boolean framed(") < _i("public void put(java.util.ArrayList slots, int idx")
P.finish()
